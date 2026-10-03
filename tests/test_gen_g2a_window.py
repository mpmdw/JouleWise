"""Desk-only G2-a authoring and safe reservation inspection regressions."""
from __future__ import annotations
from contextlib import redirect_stdout
from dataclasses import replace
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock
from joulewise import night_agent_install as install, night_gate
from joulewise.night_plan_writer import write_night_plan
from scripts import gen_g2_phase_d as generator, run_night
from tests import battery_float_fixture

ROOT = Path(__file__).resolve().parents[1]
HEAD = 'a' * 40


def tree(root):
    return {p.relative_to(root).as_posix(): (p.lstat().st_mode, p.lstat().st_mtime_ns,
             os.readlink(p) if p.is_symlink() else p.read_bytes() if p.is_file() else None)
            for p in [root, *sorted(root.rglob('*'))]}


class G2aFixture:
    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.measurement, self.g2a, self.night = (self.base / name for name in ('measurement', 'g2a', 'night'))
        self.measurement.mkdir()
        self.python = self.measurement / '.venv/bin/python'
        self.python.parent.mkdir(parents=True)
        self.python.symlink_to(sys.executable)
        self.bin = self.base / 'bin'
        self.bin.mkdir()
        (self.bin / 'git').write_text('#!/bin/sh\nprintf "%s\\n" ' + HEAD + '\n')
        (self.bin / 'claude').write_text('#!/bin/sh\nexit 0\n')
        for p in self.bin.iterdir():
            p.chmod(0o755)
        self.g2a.mkdir()
        wp = self.g2a / 'window-plan'
        wp.mkdir()
        self.plan_id = 'g2a-fixture-20261003'
        (wp / 'calibration_plan.json').write_text(json.dumps({'plan_id': 'plan-' + self.plan_id + '-g2a-probe-v1'}) + '\n')
        for name in ('identity-epoch.json', 't1-bindings.json'):
            (wp / name).write_text('{}\n')
        for name in install.PROBE_CODE_PATHS:
            p = self.measurement / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((ROOT / name).read_bytes())
        self.reservation = self.measurement / 'scripts/reserve_calibration_window_bracket.py'
        self.reservation.write_text('from pathlib import Path\nimport sys\n'
            'assert "--verify-only" in sys.argv and "--execute" not in sys.argv\n'
            'Path(__file__).with_suffix(".CALLED").touch()\nprint("{}")\n')
        for name, value in (('runs/calibration_observation_ledger.jsonl', {'receipt_digest': 'b'*64}),
                            ('configs/calibration/calibration_ledger_head.json', {'head_digest': 'b'*64})):
            path = self.measurement / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value) + '\n')
        reg = self.measurement / night_gate.D166_REGISTRATION_PATH
        reg.parent.mkdir(parents=True)
        reg.write_bytes((ROOT / night_gate.D166_REGISTRATION_PATH).read_bytes())
        policy = self.measurement / 'configs/campaign_policies/quiet_mac_p2_production.json'
        policy.parent.mkdir(parents=True, exist_ok=True)
        policy.write_bytes((ROOT / 'configs/campaign_policies/quiet_mac_p2_production.json').read_bytes())
        self.chain = self.night / 'chain.zsh'
        generator.emit_g2a_night_chain(self.chain, '20261003', measurement_root=self.measurement,
                                      g2a_root=self.g2a, night_root=self.night, plan_id=self.plan_id)
        self.plan_path = self.night / 'night_plan.json'
        t0 = (int(time.time()) // 60 + 120) * 60
        real_head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
                                   text=True, check=True).stdout.strip()
        self.plan = night_gate.NightPlan(plan_id=self.plan_id, receipt_class='DIAGNOSTIC_NO_PACK',
            t0_epoch_s=t0, window_max_s=generator.NIGHT_PROGRAMMED_SPAN_S+900, authored_epoch_s=time.time(),
            repo_head=real_head, measurement_root=str(self.measurement), measurement_head=HEAD,
            chain_path=str(self.chain), chain_sha256_path=str(self.chain)+'.sha256', custody_root=str(self.night),
            registration_path=night_gate.D166_REGISTRATION_PATH)
        write_night_plan(self.plan_path, self.plan)

    def environment(self):
        return mock.patch.dict(os.environ, {'PATH': str(self.bin)+os.pathsep+os.environ['PATH']})

    def close(self):
        self.temporary.cleanup()


class G2aInspectionTests(unittest.TestCase):
    def setUp(self):
        self.f = G2aFixture()
        self.addCleanup(self.f.close)

    def run_chain(self, **flags):
        with self.f.environment():
            env = run_night._chain_environment(self.f.plan, self.f.night/'night')
            env.update(flags)
            return subprocess.run(['/bin/zsh', str(self.f.chain)], env=env, capture_output=True, check=False)

    def test_argv_only_precedes_all_mutation_and_describes_actual_reservation(self):
        before = tree(self.f.base)
        result = self.run_chain(NIGHT_VERIFY_ONLY='1', NIGHT_RESERVATION_ARGV_ONLY='1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(tree(self.f.base), before)
        self.assertTrue(result.stdout.endswith(b'\0'))
        argv = result.stdout.decode().split('\0')[:-1]
        self.assertEqual(argv[:2], [str(self.f.python), str(self.f.reservation)])
        self.assertEqual(argv[-1], '--verify-only')
        self.assertNotIn('--execute', argv)
        for flag, value in (('--session-id', self.f.plan_id+'-calibration'),
                            ('--plan-id', 'plan-'+self.f.plan_id+'-g2a-probe-v1'),
                            ('--plan-sha256', hashlib.sha256((self.f.g2a/'window-plan/calibration_plan.json').read_bytes()).hexdigest()),
                            ('--runs-root', str(self.f.g2a/'runs'))):
            self.assertEqual(argv[argv.index(flag)+1], value)

    def test_verify_only_invokes_reservation_without_input_checks_or_capture(self):
        result = self.run_chain(NIGHT_VERIFY_ONLY='1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.f.reservation.with_suffix('.CALLED').exists())
        self.assertFalse((self.f.g2a/'runs').exists())

    def test_plan_id_exports_are_shell_quoted_in_inspection(self):
        plan_id = "g2a desk;$(touch injected-marker)"
        generator.emit_g2a_night_chain(self.f.chain, '20261003', measurement_root=self.f.measurement,
            g2a_root=self.f.g2a, night_root=self.f.night, plan_id=plan_id)
        before = tree(self.f.base)
        result = self.run_chain(NIGHT_RESERVATION_ARGV_ONLY='1', NIGHT_VERIFY_ONLY='1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(tree(self.f.base), before)
        argv = result.stdout.decode().split('\0')[:-1]
        self.assertEqual(argv[argv.index('--session-id')+1], plan_id+'-calibration')
        self.assertFalse(self.f.reservation.with_suffix('.CALLED').exists())
        self.assertFalse((self.f.g2a/'runs').exists())

    def test_probe_bindings_accept_g2a_without_derivation_wrapper(self):
        with self.f.environment():
            binding = install.probe_bindings(self.f.plan, self.f.plan_path, sys.executable)
        self.assertEqual(binding['chain_source_sha256'], binding['chain_sha256'])
        self.assertFalse(self.f.reservation.with_suffix('.CALLED').exists())
        self.assertFalse((self.f.measurement/'scripts/night_chains/calibration_derivation_only.zsh').exists())

    def test_derivation_wrapper_without_source_still_refuses(self):
        self.f.chain.write_text(self.f.chain.read_text().replace('export NIGHT_CHAIN_INTERFACE=g2a-reservation-v1\n', ''))
        with self.assertRaises((ValueError, OSError)):
            install.reservation_inspection_source(self.f.plan)

    def test_typed_calibration_refusal_path_is_night_custody(self):
        text = self.f.chain.read_text()
        self.assertEqual(night_gate.chain_literal(text, 'JOULEWISE_CALIBRATION_REFUSAL_PATH'),
                         str(self.f.night/'night/calibration-refusal.json'))
        self.assertEqual(night_gate.chain_literal(text, 'NIGHT_PROGRAMMED_SPAN_S'), '17248')

    def test_installer_render_only_succeeds_without_running_reservation(self):
        real_run = subprocess.run
        def run(argv, *a, **kw):
            if argv[0] == '/usr/bin/git':
                head = self.f.plan.repo_head if str(argv[2]) == str(ROOT) else HEAD
                return subprocess.CompletedProcess(argv, 0, head+'\n', '')
            return real_run(argv, *a, **kw)
        with self.f.environment(), mock.patch.object(install.subprocess, 'run', side_effect=run), \
                mock.patch.object(install, 'BATTERY_PROBE_RUNNER', battery_float_fixture.runner()), \
                mock.patch.object(run_night, 'install_spans_for_day', return_value=[(0, time.time()+10000)]), \
                redirect_stdout(io.StringIO()):
            result = install.main(['--plan', str(self.f.plan_path), '--python', sys.executable,
                                   '--render-only', str(self.f.base/'rendered')])
        self.assertEqual(result, 0)
        self.assertFalse(self.f.reservation.with_suffix('.CALLED').exists())
        self.assertTrue(list((self.f.base/'rendered').glob('*.plist')))


class G2aAuthoringTests(unittest.TestCase):
    def test_programmed_span_uses_code_for_both_models_without_local_model_files(self):
        from scripts import generate_g2a_probe_inputs as producer
        with mock.patch.object(producer, '_validate_panel', side_effect=AssertionError('local model files')), \
                mock.patch.object(producer, '_load_runtime_tokenizer', side_effect=AssertionError('tokenizer load')):
            self.assertEqual(generator.programmed_span_s(), 17248)

    def args(self, base):
        return SimpleNamespace(new_g2a_window=base/'night/night_plan.json', night_root=base/'night',
            g2a_root=base/'g2a', plan_id='d117-g2a-20261003',
            measurement_root=Path('/Users/edr/night-custody/measurement/JouleWise-measurement-g2a-20261003'),
            measurement_head=HEAD, t0_epoch_s=6000, window_max_s=18148)

    def test_one_command_authors_v2_plan_chain_sidecar_and_schedule(self):
        with tempfile.TemporaryDirectory() as temporary:
            args = self.args(Path(temporary))
            with redirect_stdout(io.StringIO()) as output:
                plan = generator.author_g2a_window(args, now=lambda: 3000)
            value = json.loads(args.new_g2a_window.read_bytes())
            self.assertEqual(value['schema'], 'joulewise.night_plan.v2')
            self.assertEqual(value['schema_version'], 2)
            self.assertEqual(value['receipt_class'], 'DIAGNOSTIC_NO_PACK')
            self.assertEqual(value['registration_path'], night_gate.D166_REGISTRATION_PATH)
            schedule = json.loads(output.getvalue().splitlines()[0])
            self.assertEqual(schedule['latest_chain_start_epoch_s'], 6900)
            self.assertEqual(schedule['harvest_open_epoch_s'], 24448)
            self.assertEqual(schedule['stand_down_epoch_s'], 5520)
            expected = run_night.schedule(plan)
            self.assertEqual({key: schedule[key] for key in expected}, json.loads(json.dumps(expected)))
            self.assertEqual(subprocess.run(['/bin/zsh', '-n', plan.chain_path]).returncode, 0)

    def test_plan_may_be_staged_outside_the_night_root_for_later_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            args = self.args(base)
            (base/'stage').mkdir()
            args.new_g2a_window = base/'stage/night_plan.json'
            with redirect_stdout(io.StringIO()):
                plan = generator.author_g2a_window(args, now=lambda: 3000)
            self.assertTrue((base/'stage/night_plan.json').is_file())
            self.assertFalse((base/'night/night_plan.json').exists())
            self.assertEqual(Path(plan.custody_root), (base/'night').resolve())
            self.assertEqual(Path(plan.chain_path), (base/'night/chain.zsh').resolve())
            args.new_g2a_window = base/'stage/other.json'
            with self.assertRaises(ValueError), redirect_stdout(io.StringIO()):
                generator.author_g2a_window(args, now=lambda: 3000)

    def test_authoring_fences_refuse_before_publication(self):
        cases = [('plan_id', 'night-CODEX'), ('plan_id', 'night-claude'), ('plan_id', 'night-T3'),
                 ('g2a_root', Path('/tmp/ClAuDe-probe')), ('night_root', Path('/tmp/t3')),
                 ('measurement_root', Path('/tmp/measurement')), ('measurement_root', Path('/Users/edr/night-custody/measurement')),
                 ('t0_epoch_s', 6001), ('t0_epoch_s', 5340), ('window_max_s', 18147),
                 ('measurement_head', 'bad')]
        for field, bad in cases:
            with self.subTest(field=field, value=bad), tempfile.TemporaryDirectory() as temporary:
                base = Path(temporary)
                args = self.args(base)
                setattr(args, field, bad)
                with self.assertRaises(ValueError), redirect_stdout(io.StringIO()):
                    generator.author_g2a_window(args, now=lambda: 3000)
                self.assertEqual(list(base.iterdir()), [])
