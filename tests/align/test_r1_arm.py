"""Real R1 arm route, with synthetic hardware/process command boundaries only."""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timezone
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import plistlib
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from joulewise.align import r1_arm as arm
from joulewise.align.apple import powermode
from joulewise.b5 import driver as hazard
from joulewise import night_agent_install, night_gate
from joulewise.hazards.clock import measured_rate_bound
from scripts import magistrate_watchdog as watchdog, run_night
from tests import process_reaper
from tests.test_b5_driver import FakeArm, fake_dc_meter_argv, fake_monitor_argv

ROOT = Path(__file__).resolve().parents[2]


def executable(path, source):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#!' + sys.executable + '\n' + source)
    path.chmod(0o755)


class ArmTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def prepare(self, measurement=ROOT, *, live_t0=False):
        now = time.time()
        t0 = math.ceil((now + arm.ARM_NOTICE_S) / 60) * 60
        if live_t0:
            t0 = int(now // 60) * 60
            now = t0 - arm.ARM_NOTICE_S
        record = arm.prepare(measurement, self.root / 'custody', t0, now=now)
        self.custody = self.root / 'custody'
        self.plan_path = Path(record['plan'])
        self.plan = night_gate.NightPlan.from_mapping(json.loads(self.plan_path.read_text()))
        return record

    def test_plan_pins_single_chain_and_derives_the_long_deadline(self):
        record = self.prepare()
        sizing = record['derivation']
        self.assertEqual(record['window_max_s'], sizing['window_max_s'])
        self.assertEqual(sizing['base_terms_s']['display_dwell_s'], arm.DISPLAY_DWELL_S)
        # The repository root has no prepare packet: recorded, flagged, not refused here.
        self.assertEqual(record['prepare_packet']['sha256'], None)
        self.assertTrue(any(f.startswith('r1.prepare_packet_absent_at_arm') for f in record['flags']))
        mapping = json.loads(self.plan_path.read_text())
        # RL-72 E2 sizing on the plan itself (W1 PREQUAL's installed-R1-plan check, w1_prequal.py:1396-1404).
        self.assertEqual(mapping['hazard_window']['programmed_span_s'], 108768)
        self.assertEqual(mapping['window_max_s'], 126480)
        # Admission at Automatic is the default (night_gate: absent means 0); the R1 driver owns
        # every A-B-A/series power transition. The key is omitted so main's watchdog can read the plan.
        self.assertNotIn('ac_powermode', mapping)
        self.assertIsNone(self.plan.ac_powermode)
        self.assertEqual(self.plan.receipt_class, 'HAZARD_PACK')
        self.assertTrue(self.plan.plan_id.startswith('align-r1-'))
        self.assertEqual(self.plan.hazard_window['member_count'], 0)
        self.assertEqual(self.plan.hazard_window['T_stream_max_s'], 5764)
        clock = self.plan.hazard_window['thresholds']['clock']
        self.assertEqual(clock['h_ms'], 0)  # existing ALIGN pilot/S-7 hold
        self.assertTrue(measured_rate_bound(Fraction(0), clock)['passes'])
        # (1 + .25) ppm * 5,764 s = 7.205 ms, above the existing 5 ms hold.
        self.assertFalse(measured_rate_bound(Fraction(1), clock)['passes'])
        self.assertIn('align_r1_rehearsal.zsh', Path(self.plan.chain_path).read_text())
        self.assertNotIn('run_campaign', Path(self.plan.chain_path).read_text())
        self.assertGreater(run_night.deadman_epoch(self.plan), self.plan.t0_epoch_s + 86400)
        with self.assertRaises(FileExistsError):
            arm.prepare(ROOT, self.custody, int(self.plan.t0_epoch_s))

    def test_follow_up_sizing_is_rl72_e2_for_every_t0(self):
        # RL-72 E2: programmed span 108,768 s (the driver's own two whole-unit redos, two batch
        # encounters and 9,000 s in-driver overhead), window_max_s 126,480 s.
        from scripts import align_r1_rehearsal as r1
        from joulewise.b6 import plan_inputs
        driver = r1.night_worst_case_s(['--config', str(ROOT / 'configs/align/v4/r1_runtime.json')])
        self.assertEqual(driver['programmed_span_s'], 108768)
        cases = [((2026, 11, 12), 19, 26), ((2026, 11, 8), 13, 30), ((2026, 11, 8), 8, 0),
                 ((2026, 10, 31), 5, 0), ((2026, 3, 7), 6, 0)]
        for date, hour, minute in cases:
            with self.subTest(date=date, hour=hour):
                t0 = int(datetime(*date, hour, minute, tzinfo=arm.BATCH_ZONE).timestamp())
                sizing = arm.size_window(t0)
                self.assertEqual(sizing['programmed_span_s'], 108768)
                self.assertEqual(sizing['writer_window_max_s'],
                                 plan_inputs.window_max_s({'programmed_span_s': {'seconds': 108768}}))
                self.assertEqual(sizing['window_max_s'], 126480)
                # No batch allowance is added on top: the span already holds two encounters.
                self.assertLessEqual(sizing['batch_window_crossings'], 2)
                for epoch in sizing['batch_crossings_epoch_s']:
                    local = datetime.fromtimestamp(epoch, arm.BATCH_ZONE)
                    self.assertEqual((local.hour, local.minute), (11, 45))
                    self.assertTrue(t0 <= epoch < t0 + sizing['window_max_s'])
                cli = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/arm_align_r1.py'),
                                      'size', '--t0', str(t0)], capture_output=True, text=True, check=True)
                self.assertEqual(json.loads(cli.stdout), sizing)

    def test_window_covers_wrapper_prefix_driver_work_deadline_and_close(self):
        # The wrapper's display dwell and D-109 bookends run outside the driver (r1_arm.wrapper_bytes);
        # the driver's own calibration brackets are inside its span (align_r1_rehearsal.phase_bound).
        sizing = arm.size_window(int(datetime(2026, 11, 12, 19, 26, tzinfo=arm.BATCH_ZONE).timestamp()))
        terms = sizing['base_terms_s']
        self.assertEqual(terms, {'r1_driver_span_s': 108768, 'hazard_arm_s': arm.b5_plan.T0_STAGE_CAP_S,
                                 'display_dwell_s': 300, 'bookends_s': 2 * 1800, 'close_s': 2 * 600,
                                 'harvest_s': 600})
        self.assertEqual(sizing['base_s'], sum(terms.values()))
        # Latest driver end: arm cap + dwell + pre bookend (+ its budget grace) + the driver's whole span
        # (its work deadline is chain start + span - 900, then its 900 s close reserve).
        latest_driver_end = (arm.b5_plan.T0_STAGE_CAP_S + 300 + 1800 + arm.chain.BUDGET_GRACE_S + 108768)
        self.assertEqual(sizing['latest_driver_end_offset_s'], latest_driver_end)
        self.assertLessEqual(latest_driver_end + 1800 + arm.chain.BUDGET_GRACE_S + 600, sizing['window_max_s'])
        self.assertLessEqual(sizing['base_s'], sizing['window_max_s'])

    def test_sizing_refuses_a_driver_span_other_than_rl72_e2(self):
        with self.assertRaisesRegex(ValueError, 'RL-72 E2'):
            arm.size_window(int(time.time()) + 3600, span_s=100627)

    def test_prepare_requires_fifteen_minute_notice_without_writing_custody(self):
        t0 = math.ceil(time.time() / 60) * 60
        with self.assertRaisesRegex(ValueError, '15 minutes'):
            arm.prepare(ROOT, self.root / 'custody', t0, now=t0 - arm.ARM_NOTICE_S + 1)
        self.assertFalse((self.root / 'custody').exists())

    def test_display_dwell_records_failure_without_veto_and_waits_full_dwell(self):
        for outcome in (0, 7, OSError('synthetic missing pmset')):
            with self.subTest(outcome=str(outcome)):
                custody = self.root / str(outcome)
                (custody / 'night').mkdir(parents=True)
                clock = [0]  # virtual elapsed seconds; no wall-clock sleep or host command
                def run(argv, **kwargs):
                    self.assertEqual(argv, ['/usr/bin/pmset', 'displaysleepnow'])
                    if isinstance(outcome, OSError):
                        raise outcome
                    return subprocess.CompletedProcess(argv, outcome)
                def sleep(seconds):
                    self.assertEqual(seconds, arm.DISPLAY_DWELL_S)
                    clock[0] += seconds
                self.assertEqual(arm.display_dwell(custody, run=run, sleep=sleep, now=lambda: clock[0]), 0)
                records = [json.loads(line) for line in (custody / 'night/r1_wrapper.jsonl').read_text().splitlines()]
                self.assertEqual([row['event'] for row in records], ['displaysleepnow', 'dwell_start', 'dwell_end'])
                self.assertEqual(records[0]['flag'], None if outcome == 0 else 'r1.display_sleep_failed')
                self.assertEqual(records[2]['epoch_s'] - records[1]['epoch_s'], arm.DISPLAY_DWELL_S)

    def test_mutated_chain_exits_65_before_any_wrapper_work(self):
        measurement, _, fakebin = self.synthetic_measurement(False)
        self.prepare(measurement)
        source = measurement / arm.CHAIN_SOURCE
        pinned = arm.digest(source)
        wrapper = Path(self.plan.chain_path).read_text()
        self.assertIn(pinned, wrapper)
        raw = bytearray(source.read_bytes())
        raw[-1] ^= 1  # exactly one byte differs after generation
        source.write_bytes(raw)
        night = self.custody / 'night'
        night.mkdir()
        # If the digest gate is bypassed, the first helper/chain command
        # hits this executable sentinel; no real pmset or sudo can execute.
        called = self.root / 'unexpected-work'
        sentinel = self.root / 'sentinel'
        executable(sentinel, f'from pathlib import Path\nPath({str(called)!r}).touch()\nraise SystemExit(99)\n')
        env = dict(os.environ, NIGHT_DIR=str(night), MEASUREMENT_ROOT=str(measurement), PY=str(sentinel),
                   PATH=str(fakebin) + ':' + os.environ['PATH'],
                   EVIDENCE_CHAIN_SOURCE_SHA256=arm.digest(source))  # mutable env cannot replace the literal
        result = subprocess.run(['/bin/zsh', '-f', self.plan.chain_path], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 65, result.stderr)
        self.assertFalse(called.exists())
        self.assertFalse((night / 'align-r1').exists())
        self.assertFalse((night / 'r1_wrapper.jsonl').exists())
        self.assertFalse((self.custody / 'bookends').exists())

    def test_shared_plists_fence_watchdog_through_a_second_day(self):
        self.prepare()
        schedule = run_night.schedule(self.plan)
        prepared = night_agent_install.Prepared(
            self.plan, self.plan_path, ROOT, sys.executable,
            (ROOT / 'configs/launchd/com.joulewise.night.plist.template').read_text(),
            str(ROOT / 'scripts/b6_courier.sh'), '/usr/bin:/bin', schedule, run_night.install_spans_for_day)
        agents = self.root / 'LaunchAgents'
        agents.mkdir()
        for label, payload in prepared.render(night_agent_install.LABELS):
            document = plistlib.loads(payload)
            self.assertNotIn('KeepAlive', document)
            self.assertEqual(document['ProgramArguments'][document['ProgramArguments'].index('--plan') + 1], str(self.plan_path))
            (agents / (label + '.plist')).write_bytes(payload)
        storage = watchdog.Storage(self.root)
        plans = watchdog._installed_agent_plans(datetime.now(timezone.utc), storage, launch_agents_dir=agents)
        self.assertEqual([p.plan_id for p in plans], [self.plan.plan_id])
        self.assertTrue(watchdog.plan_span_active(plans[0], self.plan.t0_epoch_s + 86400, storage))
        # The daily dead-man calendar can fire a day early on a >24 h plan;
        # the real dead-man must stand down before even resolving a courier.
        with patch.object(run_night.time, 'time', return_value=run_night.deadman_epoch(self.plan) - 86400), \
                patch.object(run_night, '_resolve_courier_bin') as courier:
            self.assertEqual(run_night.dead_man(self.plan_path), 0)
        courier.assert_not_called()
        self.assertNotIn('--uninstall', arm.installer_argv(self.custody))
        self.assertIn('--uninstall', arm.installer_argv(self.custody, uninstall=True))
        self.assertIn('--render-only', arm.installer_argv(self.custody, render_only=self.root / 'rendered'))

    def synthetic_measurement(self, interrupt):
        measurement = self.root / 'measurement'
        scripts = measurement / 'scripts'
        scripts.mkdir(parents=True)
        (measurement / '.git').symlink_to(ROOT / '.git')
        (measurement / 'configs').symlink_to(ROOT / 'configs', target_is_directory=True)
        (measurement / 'joulewise').symlink_to(ROOT / 'joulewise', target_is_directory=True)
        (scripts / 'night_chains').mkdir()
        shutil.copy2(ROOT / 'scripts/night_chains/align_r1_rehearsal.zsh', scripts / 'night_chains/align_r1_rehearsal.zsh')
        # Keep the real CLI/wrapper helper and record-writing path; replace
        # only its host command and 300 s wall-clock wait in the child process.
        scripts.joinpath('arm_align_r1.py').write_text(f'''
import sys, subprocess
sys.path.insert(0, {str(ROOT)!r})
from scripts.arm_align_r1 import main
from joulewise.align import r1_arm
real_dwell = r1_arm.display_dwell
clock = [0]
def fake_sleep(seconds):
    assert seconds == r1_arm.DISPLAY_DWELL_S
    clock[0] += seconds
def fake_pmset(argv, **kwargs):
    assert argv == ['/usr/bin/pmset', 'displaysleepnow']
    return subprocess.CompletedProcess(argv, 7)
r1_arm.display_dwell = lambda custody: real_dwell(custody, run=fake_pmset, sleep=fake_sleep, now=lambda: clock[0])
raise SystemExit(main())
''')
        (measurement / '.align-r1-prepare.json').write_text('{"synthetic": true}\n')
        (measurement / '.venv/bin').mkdir(parents=True)
        (measurement / '.venv/bin/python').symlink_to(sys.executable)
        self.mode = self.root / 'mode'
        self.mode.write_text('0')
        self.ready = self.root / 'interrupt-ready'
        # Only host command boundaries are replaced. The shim imports and
        # executes the real driver's main(), signals, guard and final writes.
        prefix = f'import sys\nsys.path.insert(0, {str(ROOT)!r})\n'
        scripts.joinpath('align_r1_rehearsal.py').write_text(prefix + f'''
import json, os, subprocess
from pathlib import Path
from scripts import align_r1_rehearsal as r1
from tests.align.test_r1_rehearsal import FakeWorld
world = FakeWorld()
real_run = r1._run
def run(argv):
    argv = tuple(str(a) for a in argv)
    if argv[0] in ('sudo', '/usr/bin/pmset', '/sbin/mount', '/usr/sbin/diskutil'):
        world.mode = int(Path({str(self.mode)!r}).read_text())
        result = world(argv)
        Path({str(self.mode)!r}).write_text(str(world.mode))
        return result
    return real_run(argv)
r1._run = run
# This synthetic runtime starts no descendants. The sandbox denies ps;
# supply that fixture process table explicitly rather than misreading it.
r1._process_table = lambda: {{}}
# The follow-up chain requires $MEASUREMENT_ROOT/.align-r1-prepare.json (D-2). Its
# real weight/stack preflights are native; the driver's packet check is replaced
# by a record of the file the chain passed, which must be the fixed path.
def require_prepare_packet(path, root=None):
    assert Path(path) == Path(os.environ['MEASUREMENT_ROOT']) / '.align-r1-prepare.json', path
    return {{'path': str(path), 'sha256': 'synthetic', 'synthetic': True}}
r1.require_prepare_packet = require_prepare_packet
r1.wait_outside_os_batch = lambda _: 0
raise SystemExit(r1.main())
''')
        runtime = self.root / 'runtime'
        executable(runtime, prefix + f'''
import json, os, time
from pathlib import Path
from tests.align.test_r1_rehearsal import FakeWorld
kind = sys.argv[sys.argv.index('--r1-kind') + 1]
if {interrupt!r} and kind == 'high-power-aba-b':
    Path({str(self.ready)!r}).write_text('ready')
    time.sleep(120)
world = FakeWorld()
world.mode = int(Path({str(self.mode)!r}).read_text())
result = world(sys.argv)
out = Path(sys.argv[sys.argv.index('--output') + 1])
(out / 'environment.json').write_text(json.dumps({{k: os.environ[k] for k in ('NIGHT_DIR', 'MEASUREMENT_ROOT')}}))
print(result.stdout)
raise SystemExit(result.returncode)
''')
        # zsh's sudo call is intercepted through PATH; the driver shim above
        # intercepts absolute pmset and the driver-managed sudo invocations.
        fakebin = self.root / 'bin'
        executable(fakebin / 'sudo', f'''
import sys
from pathlib import Path
if '-l' in sys.argv:
    print('/usr/bin/pmset -c powermode 0\\n/usr/bin/pmset -c powermode 2')
else:
    assert sys.argv[1:] == ['-n', '/usr/bin/pmset', '-c', 'powermode', '0'], sys.argv
    Path({str(self.mode)!r}).write_text('0')
''')
        # Calibration capture is an other-lane/hardware seam. Make it fail
        # deliberately, proving a records fault cannot veto R1.
        scripts.joinpath('validate_powermetrics_fiducial.py').write_text('''
import json, os
from pathlib import Path
records = [json.loads(line) for line in (Path(os.environ['NIGHT_DIR']) / 'r1_wrapper.jsonl').read_text().splitlines()]
assert records[-1]['event'] == 'dwell_end'
raise SystemExit(7)
''')
        return measurement, runtime, fakebin

    def exercise(self, interrupt=False):
        measurement, runtime, fakebin = self.synthetic_measurement(interrupt)
        self.prepare(measurement, live_t0=True)
        night = self.custody / 'night'
        self.addCleanup(process_reaper.reap, str(self.root), night=night, started_monotonic=time.monotonic())
        def probe(argv):
            if tuple(argv) == night_gate.AGENT_CENSUS_ARGV:
                return night_gate.ProbeResult(tuple(argv), 1, '', '', time.monotonic_ns())
            if tuple(argv) == ('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '0'):
                self.mode.write_text('0')  # run_night's close restore (host-level, R6-7)
                return night_gate.ProbeResult(tuple(argv), 0, '', '', time.monotonic_ns())
            if tuple(argv) == run_night.NETWORK_TIME_QUERY_ARGV:
                return night_gate.ProbeResult(tuple(argv), 0, 'Network Time: Off\n', '', time.monotonic_ns())
            self.assertEqual(tuple(argv), powermode.QUERY)
            return night_gate.ProbeResult(tuple(argv), 0, 'AC Power:\n powermode ' + self.mode.read_text() + '\n', '', time.monotonic_ns())
        probes = night_gate.Probes(run=probe, now_epoch_s=time.time, monotonic_ns=time.monotonic_ns,
                                  read_text=lambda p: Path(p).read_text(),
                                  checkout_head=lambda: self.plan.repo_head, measurement_head=lambda _: self.plan.measurement_head)
        production = hazard.production_seams(ROOT)
        # Use real lineage publication/config inventory; fake only hardware,
        # collectors and the reporting transport, like tests/test_b5_driver.
        seams = hazard.Seams(
            arm=FakeArm(), publish_lineage=production.publish_lineage,
            verify_lineage=lambda _: {role: {'valid': True} for role in ('claim', 'bound')},
            monitor_argv=lambda request: fake_monitor_argv(request.custody_root),
            meter_argv=fake_dc_meter_argv,  # every measurement requires DC-in (presign hazard driver)
            meter_probe=lambda root: {'live': True, 'synthetic': True},
            collectors_argv=lambda _: [sys.executable, '-c', 'print("synthetic collectors")'],
            g10_argv=production.g10_argv, disk_free_bytes=lambda _: 10**13,
            boot_session_uuid=lambda: 'SYNTHETIC-BOOT',
            run_command=lambda argv, timeout: hazard.CommandResult(tuple(argv), 0, '', '', False, None,
                                                                  hazard.stamp(), hazard.stamp()))
        stopped = threading.Event()
        signal_sent = threading.Event()
        lock_blocked = []
        children = []
        real_popen = subprocess.Popen
        def popen(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            if kwargs.get('start_new_session'):
                children.append(process)
            return process
        def synthetic_group_census(pgid, timeout_s=1):
            # Fixture process table: each launcher waits for its own child;
            # monitors and meter have no children. All handles are reaped.
            live = [p for p in children if p.pid == pgid and p.poll() is None]
            return not live, [str(p.pid) for p in live]
        def reap_children():
            for child in children:
                if child.poll() is None:
                    child.kill()
                child.wait(timeout=run_night.PROBE_TIMEOUT_S)
        self.addCleanup(reap_children)
        seams.popen = popen
        def signal_when_high():
            while not stopped.wait(0.01):
                if self.ready.exists():
                    contender = powermode.HostLock(role='synthetic competing admission')
                    lock_blocked.append(not contender.acquire())
                    contender.release()
                    signal_sent.set()
                    os.kill(os.getpid(), signal.SIGTERM)
                    return
        if interrupt:
            sender = threading.Thread(target=signal_when_high, daemon=True)
            sender.start()
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {
                'JOULEWISE_HOST_STATE_DIR': str(self.root / 'host'), 'HOME': str(self.root / 'home'),
                'ALIGN_R1_RUNTIME': str(runtime), 'PATH': str(fakebin) + ':' + os.environ['PATH']}))
            stack.enter_context(patch.object(run_night, 'make_probes', return_value=probes))
            stack.enter_context(patch.object(subprocess, 'Popen', side_effect=popen))
            stack.enter_context(patch.object(run_night, '_group_census', side_effect=synthetic_group_census))
            stack.enter_context(patch.object(run_night, '_hazard_seams', return_value=seams))
            stack.enter_context(patch.object(run_night, '_durable_record', return_value=None))
            stack.enter_context(patch.object(run_night, '_resolve_courier_bin', return_value=(Path('/usr/bin/true'), None, None)))
            stack.enter_context(patch.object(run_night, 'run_courier', return_value={'attempted': 1, 'sent': True,
                                                                                'heartbeat_seen': True, 'last_error': None}))
            try:
                code = run_night.run_night(self.plan_path)
            except KeyboardInterrupt:
                self.assertTrue(interrupt)
                code = 130
            finally:
                stopped.set()
                if interrupt:
                    sender.join(timeout=run_night.PROBE_TIMEOUT_S)
            lock = powermode.HostLock(role='test post-close proof')
            self.assertTrue(lock.acquire())
            lock.release()
        result_path = night / 'align-r1/r1_result.json'
        if not result_path.exists():
            self.fail('missing R1 result: ' + json.dumps({str(p.relative_to(self.custody)): p.read_text(errors='replace')[-6000:]
                      for p in self.custody.rglob('*') if p.is_file() and p.suffix in ('.log', '.json', '.stderr')}, default=str))
        result = json.loads(result_path.read_text())
        display = [json.loads(line) for line in (night / 'r1_wrapper.jsonl').read_text().splitlines()]
        self.assertEqual([row['event'] for row in display], ['displaysleepnow', 'dwell_start', 'dwell_end'])
        self.assertEqual(display[0]['flag'], 'r1.display_sleep_failed')
        self.assertEqual(display[-1]['epoch_s'] - display[-2]['epoch_s'], arm.DISPLAY_DWELL_S)
        self.assertEqual(self.mode.read_text(), '0')
        self.assertFalse((self.root / 'host/high-power.marker').exists())
        self.assertFalse((measurement / '.align-r1-high-power').exists())
        self.assertTrue((night / 'chain.exited').is_file())
        environment = json.loads((night / 'align-r1/idle_soak/environment.json').read_text())
        self.assertEqual(environment, {'NIGHT_DIR': str(night), 'MEASUREMENT_ROOT': str(measurement)})
        if interrupt:
            self.assertTrue(signal_sent.is_set())
            self.assertEqual(lock_blocked, [True])
            self.assertEqual(result['status'], 'aborted')
            self.assertTrue(result['child_terminations'])
            self.assertTrue(all(row['proven'] for row in result['child_terminations']))
            self.assertIn(code, (130, run_night.EXIT_ABORTED))
        else:
            self.assertEqual(code, 0)
            self.assertEqual(result['status'], 'complete')
            armed = json.loads((self.custody / 'arm.json').read_text())
            self.assertEqual(armed['prepare_packet'], {
                'path': str(measurement / '.align-r1-prepare.json'),
                'sha256': arm.digest(measurement / '.align-r1-prepare.json')})
            # D-2/D-7: the chain hands the driver the fixed packet under the plan's measurement root.
            self.assertEqual(result['prepare_packet']['path'], str(measurement / '.align-r1-prepare.json'))
            self.assertTrue((night / 'align-r1/r1_slots.json').is_file())
            self.assertEqual(json.loads((self.custody / 'bookends/pre.json').read_text())['flag'], 'r1.bookend_failed')
            self.assertEqual(json.loads((self.custody / 'bookends/pre.json').read_text())['exit_code'], 7)
            self.assertEqual(json.loads((self.custody / 'bookends/post.json').read_text())['flag'], 'r1.bookend_failed')
            self.assertTrue((night / 'meter_supervision.jsonl').is_file())
        print('R1_SYNTHETIC ' + json.dumps({'interrupt': interrupt, 'exit': code, 'r1_status': result['status'],
                                          'environment': environment, 'power_mode': 0,
                                          'host_lock_reacquired': True,
                                          'lock_blocked_during_high_power': lock_blocked}, sort_keys=True))

    def test_production_route_completes_with_synthetic_runtime(self):
        self.exercise()

    def test_mid_high_power_interrupt_restores_and_releases_host_lock(self):
        self.exercise(interrupt=True)


if __name__ == '__main__':
    unittest.main()
