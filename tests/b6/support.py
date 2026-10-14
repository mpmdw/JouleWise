"""Synthetic session inputs and injected hardware seams; no measurement roots."""
import copy
import json
import os
import subprocess
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from joulewise.b5 import plan
from joulewise.b6 import precheck
from joulewise.hazards import arm, battery, clock, contention, instrument, thermal
from joulewise.hazards.base import Context
from tests.hazards.fakes import (FakeClocks, FakeSmc, FakeProcessTable, Runner, FrequencyReader,
                                 BOOT_UUID, completed, battery_bytes, update_time)

ROOT = Path(__file__).resolve().parents[2]
PACKS = {'alpha': 'd117_floor_qwen3-1p7b_v5', 'beta': 'd117_floor_qwen3-8b_v5',
         'gamma': 'd117_contrast_qwen3-1p7b_vs_qwen3-8b_v5'}


def tree(pack):
    return json.loads((ROOT / 'configs/campaigns' / PACKS[pack] / 'plan_tree.json').read_text())


def fp(pack=PACKS['alpha']):
    return {'code_commit': 'a' * 40, 'code_dirty': False, 'os_build': 'TEST',
            'model_hashes': {'synthetic-model': 'b' * 64},
            'runtime_versions': {'python': '3.13.1', 'packages': {'mlx': 'test'}},
            'boot_session_uuid': BOOT_UUID, 'meter_device': {'serial': 'test', 'bcdDevice': '1'},
            'powermetrics_version': 'c' * 64, 'pack': {'pack_id': pack, 'tree_id': 'd' * 40}}


class DeskCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ['TMPDIR'], prefix='b6-desk-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.processes = []

    def tearDown(self):
        # Only children this test registered may be signalled. Normally the
        # cadence adapter has already waited for them before returning.
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate(timeout=1)


def synthetic_checkout(root):
    measurement = root / 'measurement'
    registration = measurement / precheck.REGISTRATION_RELATIVE
    registration.mkdir(parents=True)
    pack = PACKS['alpha']
    pack_root = measurement / 'configs/campaigns' / pack
    pack_root.mkdir()
    t = tree('alpha')
    (pack_root / 'plan_tree.json').write_text(json.dumps(t))
    model = measurement / 'model.safetensors'
    model.write_bytes(b'synthetic weights')
    from joulewise.provenance import model_artifact_identity
    digest = model_artifact_identity(str(model))['sha256']
    pins = {'units': {'test': {'model_source': str(model), 'model_artifact_sha256': digest}},
            'runtime_versions': {'python': '3.13.1', 'packages': {'mlx': 'test'}}}
    (registration / 'identity_pins.json').write_text(json.dumps(pins))
    for dispatch in plan.resolve_stage_dispatches(t, ROOT):
        directory = measurement / dispatch.config_dir
        directory.mkdir(parents=True, exist_ok=True)
        manifest = json.loads((ROOT / dispatch.config_dir / 'order_manifest.json').read_text())
        (directory / 'order_manifest.json').write_text(json.dumps(manifest))
        for entry in manifest['executed_order']:
            (directory / entry['config']).write_text(json.dumps({'model': {'source': str(model)}}))
    ledger = measurement / plan.DEFAULT_LEDGER_RELATIVE
    ledger.parent.mkdir()
    ledger.write_text('')
    state = root / 'state'
    state.mkdir()
    return measurement, state, model


def fake_environment(measurement, *, busy=False, battery_name='float-20261005-desk.ioreg',
                     current_ma=0, thermal_level=0, idle_s=900, assertion=True, final_agent=False,
                     initial_agent=False, cadence_ms=100, free_gib=70):
    raw = battery_bytes(battery_name)
    clocks = FakeClocks(wall_s=update_time(raw) + 10, drift_word=2 * clock.FREQUENCY_SCALE)
    smc = FakeSmc(clocks, current=lambda _t: current_ma)
    table = FakeProcessTable(clocks, driver_pid=os.getpid())
    if busy:
        table.processes[350].cpu_per_s = 0.1
    calls = {'census': 0}

    def census(argv):
        calls['census'] += 1
        hit = initial_agent if calls['census'] == 1 else final_agent
        return completed(argv, b'987654 claude\n' if hit else b'', returncode=0 if hit else 1)

    def capture(argv):
        report = {'schema': instrument.CHILD_SCHEMA, 'returncode': 0, 'frames': 300,
                  'count_expected': 300, 'elapsed_s': 1, 'group_gone': True,
                  'intervals_ns': [int(cadence_ms * 10**6)] * 300}
        return completed(argv, json.dumps(report).encode())

    handlers = {
        battery.IOREG_BATTERY_ARGV: lambda argv: completed(argv, raw),
        thermal.NOTIFYUTIL_ARGV: lambda argv: completed(argv, f'{thermal.NOTIFY_KEY} {thermal_level}\n'.encode()),
        arm.AGENT_CENSUS_ARGV: census,
        precheck.HID_ARGV: lambda argv: completed(argv, f'"HIDIdleTime" = {idle_s * 10**9}\n'.encode()),
        precheck.ASSERTIONS_ARGV: lambda argv: completed(argv, b'PreventSystemSleep 1\n' if assertion else b'PreventSystemSleep 0\n'),
        precheck.POWER_CUSTOM_ARGV: lambda argv: completed(argv, b'Battery Power:\n sleep 1\n'),
        precheck.ANALYSIS_ARGV: lambda argv: completed(argv, b'123 1 0.0 mediaanalysisd\n'),
        contention.PS_ARGV: table.ps,
        '/usr/bin/sntp': lambda argv: completed(argv, b'offset +0.001\n'),
        str(measurement / '.venv/bin/python'): lambda argv: completed(argv, json.dumps(
            {'python': '3.13.1', 'packages': {'mlx': 'test'}}).encode()),
        # No real cadence child in orchestration tests.
        __import__('sys').executable: capture,
    }
    runner = Runner(handlers, real_python=False)
    ctx = Context(run=runner, clocks=clocks)
    seams = precheck.Seams(smc_read=smc, frequency_reader=FrequencyReader(clocks),
                          boot_reader=lambda ctx: BOOT_UUID, host_reader=table.host_cpu,
                          orphan_collect=lambda: [], process_uid=lambda pid: os.getuid(),
                          kill=lambda pid, sig: (_ for _ in ()).throw(AssertionError('unexpected kill')),
                          stat=lambda path: SimpleNamespace(st_dev=1),
                          statvfs=lambda path: SimpleNamespace(f_bavail=free_gib * 1024**3, f_frsize=1,
                                                             f_blocks=100 * 1024**3),
                          fingerprint_collect=lambda *args, **kwargs: fp(),
                          lstat=lambda path: SimpleNamespace(st_flags=0))
    return ctx, seams, table
