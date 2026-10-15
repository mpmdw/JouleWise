"""Real user-owned fixture processes with root ownership/signal seams only."""
import gzip
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.quiet_kit.paths import read_json
from joulewise.quiet_kit.processes import Processes, TeardownBlocked, TERM_GRACE_S, group_members, shutdown_kind
from joulewise.quiet_kit.runner import Runner, Control
from joulewise.quiet_kit.schedule import PLANS
from .collector_fakes import CollectorHardware
from .fakes import FakeHardware

REPO = Path(__file__).resolve().parents[2]


class RelayFixture:
    """The OS processes are ordinary users; only the UID/signal seams fake root."""
    def __init__(self, directory, *, stubborn=False):
        self.directory, self.stubborn = directory, stubborn
        self.time = 0.
        self.group_signals, self.pid_signals, self.children = [], [], []
        self.real_kill = os.kill
        self.manager = Processes(REPO, identity_reader=lambda pid: {'pid': pid},
            member_reader=self.members, now=lambda: self.time, sleep=self.sleep)
        self.original_spawn = self.manager.spawn
        self.leader = None
        self.child_pid = None

    def sleep(self, seconds):
        self.time += seconds
        time.sleep(.01)  # Allow the actual signal handlers to run, without a 60 s test.

    def spawn(self, argv=None, directory=None):
        argv = [sys.executable, '-m', 'tests.quiet_kit.fake_sudo', '--directory', str(self.directory)]
        if self.stubborn:
            argv += ['--ignore-term']
        self.leader = self.original_spawn(argv, directory or self.directory, shutdown='sampler')
        self.children.append(self.leader)
        until = time.monotonic()+10
        while not (self.directory/'fake-sudo-ready.json').exists():
            if self.leader.poll() is not None or time.monotonic() >= until:
                raise AssertionError('fake sudo did not start')
            time.sleep(.005)
        self.child_pid = read_json(self.directory/'fake-sudo-ready.json')['child_pid']
        return self.leader

    def alive(self, pid):
        if self.leader and pid == self.leader.pid:
            return self.leader.poll() is None
        try:
            self.real_kill(pid, 0)
            return True
        except ProcessLookupError:
            return False

    def members(self, pgid):
        return [{'pid': pid, 'uid': 0 if pid == self.child_pid else os.getuid(),
                 'argv': 'fake root sampler' if pid == self.child_pid else 'fake sudo', 'pgid': pgid}
                for pid in (self.leader.pid, self.child_pid) if self.alive(pid)]

    def census(self, pgid, **kwargs):
        rows = self.members(pgid)
        return not rows, [f"{r['pid']} {r['argv']}" for r in rows]

    def killpg(self, pgid, sig):
        self.group_signals.append((pgid, sig))
        if any(r['uid'] == 0 for r in self.members(pgid)):
            raise PermissionError('fixture root member cannot be signalled by the kit')
        # Once the child is reaped, all remaining members are ours.
        for row in self.members(pgid):
            self.real_kill(row['pid'], sig)

    def kill(self, pid, sig):
        self.pid_signals.append((pid, sig))
        if pid == self.child_pid:
            raise PermissionError('fixture root child cannot be signalled by the kit')
        self.real_kill(pid, sig)

    def cleanup(self):
        # Test owner can signal both ordinary-user fixtures. Reap the child
        # through its leader first, so neither a live fixture nor zombie leaks.
        if not self.child_pid and (self.directory/'fake-sudo-child.json').exists():
            self.child_pid = read_json(self.directory/'fake-sudo-child.json')['pid']
        if self.child_pid and self.alive(self.child_pid):
            self.real_kill(self.child_pid, signal.SIGKILL)
        for p in self.children:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.real_kill(p.pid, signal.SIGKILL)
                p.wait(timeout=5)
        if self.child_pid:
            assert not self.alive(self.child_pid), 'fake root child leaked'


class TeardownTests(unittest.TestCase):
    def fixture(self, root, **kw):
        fake = RelayFixture(root, **kw)
        self.addCleanup(fake.cleanup)
        return fake

    def signals(self, fake):
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(patch('os.killpg', side_effect=fake.killpg))
        stack.enter_context(patch('os.kill', side_effect=fake.kill))
        stack.enter_context(patch('joulewise.hazards.instrument.group_absent', side_effect=fake.census))
        stack.enter_context(patch('joulewise.hazards.contention.take_snapshot',
                                  return_value=SimpleNamespace(rows={}, error='desk seam')))
        return stack

    def test_permission_denied_group_uses_sudo_TERM_relay_never_INT(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-relay-') as tmp:
            fake = self.fixture(Path(tmp))
            p = fake.spawn()
            fake.real_kill(p.pid, signal.SIGINT)
            time.sleep(.02)
            self.assertTrue(fake.alive(p.pid))
            self.assertTrue(fake.alive(fake.child_pid))
            with self.signals(fake):
                rows = fake.manager.stop(p)
            self.assertTrue(all(r['gone'] for r in rows))
            self.assertFalse(fake.alive(p.pid))
            self.assertFalse(fake.alive(fake.child_pid))
            self.assertEqual({sig for _, sig in fake.group_signals+fake.pid_signals}, {signal.SIGTERM})
            signals = [json.loads(line)['signal'] for line in (Path(tmp)/'fake-signals.jsonl').read_text().splitlines()]
            self.assertTrue(signals)
            self.assertEqual(set(signals), {signal.SIGTERM})

    def test_unresponsive_root_never_KILLs_relay_and_records_orphan(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-relay-') as tmp:
            fake = self.fixture(Path(tmp), stubborn=True)
            p = fake.spawn()
            with self.signals(fake), self.assertRaises(TeardownBlocked) as caught:
                fake.manager.stop(p)
            self.assertTrue(fake.alive(p.pid))
            self.assertTrue(fake.alive(fake.child_pid))
            self.assertGreaterEqual(fake.time, 10)
            self.assertGreaterEqual(len(fake.pid_signals), 2)
            self.assertNotIn(signal.SIGKILL, [sig for _, sig in fake.group_signals+fake.pid_signals])
            action = next(a for a in caught.exception.actions if a['director_action'] == 'root_sampler_orphan')
            self.assertEqual((action['pid'], action['group'], action['argv']),
                             (fake.child_pid, p.pid, 'fake root sampler'))
            journal = [json.loads(line) for line in (Path(tmp)/'children.jsonl').read_text().splitlines()]
            self.assertFalse(journal[-1]['groups'][0]['gone'])
            self.assertIn(action, journal[-1]['groups'][0]['director_actions'])

    def test_role_graces_and_unknown_UID_never_authorize_KILL(self):
        for role, grace in TERM_GRACE_S.items():
            for unknown in (False, True):
                with self.subTest(role=role, unknown=unknown), tempfile.TemporaryDirectory(prefix='quiet-kit-grace-') as tmp:
                    clock, killed, signals = [0.], [False], []
                    p = SimpleNamespace(pid=42420, returncode=None, quiet_kit_shutdown=role,
                                        wait=lambda timeout: None)
                    manager = Processes(Path(tmp), now=lambda: clock[0],
                        sleep=lambda seconds: clock.__setitem__(0, clock[0]+seconds),
                        member_reader=lambda pgid: None if unknown else
                            [{'pid': p.pid, 'uid': os.getuid(), 'argv': 'fixture', 'pgid': pgid}])
                    manager.processes[p.pid] = (p, 'test', Path(tmp))
                    def killpg(pgid, sig):
                        signals.append((clock[0], sig))
                        if sig == signal.SIGKILL: killed[0] = True
                    with (patch('os.getpgid', return_value=p.pid), patch('os.getpgrp', return_value=1),
                          patch('os.killpg', side_effect=killpg), patch('os.kill') as leader,
                          patch('joulewise.hazards.contention.take_snapshot', return_value=SimpleNamespace(error='desk')),
                          patch('joulewise.hazards.instrument.group_absent', side_effect=lambda *a, **kw: (killed[0], []))):
                        if unknown:
                            with self.assertRaises(TeardownBlocked): manager.stop(p)
                        else:
                            manager.stop(p)
                    self.assertGreaterEqual(clock[0], grace)
                    self.assertEqual(signals[0], (0., signal.SIGTERM))
                    self.assertEqual(leader.call_args.args, (p.pid, signal.SIGTERM))
                    self.assertEqual(killed[0], not unknown)
                    if not unknown: self.assertGreaterEqual(signals[-1][0], grace)

    def test_clock_advance_between_wait_condition_and_sleep_is_clamped(self):
        hw = FakeHardware()
        runner = Runner(REPO, REPO/'.scratch-qk/unused', '/fake/model-python', hw.seams())
        readings = iter([0., 0., 1., 2.])
        runner.seams.now = lambda: next(readings, 2.)
        sleeps = []
        runner.seams.sleep = lambda seconds: sleeps.append(seconds)
        control = Control.__new__(Control)
        control.runner = runner
        control.check = lambda **kw: None
        control.wait(.5)
        self.assertEqual(sleeps, [0.])

    def test_fixture_signature_is_specific_to_this_subprocess(self):
        from scripts.fixture_orphan_census import load_signatures
        patterns = dict(load_signatures())
        pattern = patterns['quiet-kit-fake-sudo']
        self.assertIsNotNone(pattern.search('/opt/homebrew/bin/python3.13 -m tests.quiet_kit.fake_sudo --child --directory /tmp/qk'))
        self.assertIsNone(pattern.search('/usr/bin/sudo -n /usr/bin/powermetrics'))
        self.assertIsNone(pattern.search('python -m joulewise.quiet_kit.capture'))

    def test_UID_census_parses_commands_and_fails_closed(self):
        completed = SimpleNamespace(returncode=0, stdout=' 41 501 /usr/bin/sudo -n sampler\n 42 0 /usr/bin/powermetrics -i 100\n')
        with patch('joulewise.quiet_kit.processes.subprocess.run', return_value=completed) as run:
            rows = group_members(41)
        self.assertEqual(run.call_args.args[0], ['/bin/ps','-o','pid=,uid=,command=','-g','41'])
        self.assertEqual(rows[1], {'pid':42,'uid':0,'argv':'/usr/bin/powermetrics -i 100','pgid':41})
        for reply in [SimpleNamespace(returncode=2,stdout=''), SimpleNamespace(returncode=0,stdout='unparseable')]:
            with patch('joulewise.quiet_kit.processes.subprocess.run',return_value=reply):
                self.assertIsNone(group_members(41))

    def test_production_argv_assign_the_required_graces(self):
        from joulewise.hazards.instrument import child_argv
        self.assertEqual(shutdown_kind(child_argv(Path('/fake/out'), executable='/usr/bin/powermetrics',
                                                 privilege_prefix=('sudo','-n'))), 'capture')
        for argv, expected in [
            (['/usr/bin/sudo','-n','/usr/bin/powermetrics','-i','100'], 'sampler'),
            (['/fake/python','-m','joulewise','run','config.json'], 'model'),
            (['/usr/sbin/taskpolicy','-c','utility','/fake/python','-m','joulewise.quiet_kit.capture'], 'capture'),
            (['/fake/python','-m','joulewise.hazards.instrument','--child'], 'capture')]:
            self.assertEqual(shutdown_kind(argv), expected)

    def test_finished_capture_root_group_is_detected_from_child_journal(self):
        from joulewise.quiet_kit.paths import append
        from joulewise.quiet_kit.processes import CHILD_SCHEMA, check_capture_teardown, require_group_absent
        with tempfile.TemporaryDirectory(prefix='quiet-kit-capture-leftover-') as tmp:
            root = Path(tmp)
            append(root/'raw/children.jsonl', {'schema':CHILD_SCHEMA,'event':'spawn','pid':41,'pgid':41})
            # The exited capture's parent group is absent; its separately
            # sessioned sampler is still alive and cannot be waited away.
            member = {'pid':42,'uid':0,'argv':'fixture root sampler','pgid':41}
            with (patch('joulewise.hazards.instrument.group_absent',return_value=(False,['42 fixture sampler'])),
                  patch('joulewise.quiet_kit.processes.require_group_absent',
                        side_effect=lambda pgid: require_group_absent(pgid, member_reader=lambda group:[member])),
                  patch('os.killpg',side_effect=AssertionError('a journal is not signal authority')),
                  self.assertRaises(TeardownBlocked) as caught):
                check_capture_teardown(root)
            self.assertEqual(caught.exception.actions[0]['director_action'],'root_sampler_orphan')

    def test_root_in_preflight_is_not_converted_to_a_waiting_probe(self):
        action = {'director_action':'root_sampler_orphan','pid':42,'uid':0,'argv':'fixture','pgid':41,'group':41}
        groups = [{'pgid':41,'gone':False,'director_actions':[action]}]
        hw = FakeHardware()
        probe = hw.probe
        def root_probe(name, *args):
            if name == 'instrument': raise TeardownBlocked(groups)
            return probe(name, *args)
        seams = hw.seams()
        seams.probe = root_probe
        with tempfile.TemporaryDirectory(prefix='quiet-kit-preflight-root-') as tmp:
            root = Path(tmp)
            (root/'WAKE_CMD').write_text('wake-preflight')
            runner = Runner(REPO, root, '/fake/model-python', seams, plans=PLANS[:2], scale=.001, emit=lambda _:None)
            self.assertEqual(runner.run(),0)
            self.assertFalse(hw.collected)
            self.assertEqual(hw.wakes,['wake-preflight'])
            self.assertEqual(read_json(root/'DONE')['director_actions'],[action])

    def test_plumbing_root_leftover_prints_action_and_reaps_no_relay(self):
        self.segment_failure(stubborn=True)

    def test_exception_mid_segment_reaps_the_real_fake_sampler_group(self):
        self.segment_failure(stubborn=False)

    def segment_failure(self, *, stubborn):
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
        from joulewise.clock import ClockStamp
        from joulewise.quiet_kit.collectors import Sampler, collect
        fixture = REPO/'tests/fixtures/controller_g2b/block3-pre'
        raw = gzip.decompress((fixture/'raw/powermetrics.plist.gz').read_bytes())
        evidence = json.loads(gzip.decompress((fixture/'instrument_evidence.json.gz').read_bytes()))
        stamps = {k: ClockStamp(**v) for k, v in evidence['clock_anchor']['clock_stamps'].items()}
        with tempfile.TemporaryDirectory(prefix='quiet-kit-segment-failure-') as tmp:
            root = Path(tmp)
            fake = self.fixture(root, stubborn=stubborn)
            hw = CollectorHardware()
            hw.processes = fake.manager
            def spawn(argv, directory):
                Path(argv[argv.index('-o')+1]).write_bytes(raw)
                return fake.spawn(argv, directory)
            fake.manager.spawn = spawn
            hw.sampler = lambda directory, control: Sampler(hw, directory, control)
            def failing_collect(plan, attempt, scale, control, kind):
                def fail(seconds, **kw):
                    raise ValueError('injected exception in first segment')
                control.wait = fail
                return collect(hw, plan, attempt, scale, control, kind)
            seams = hw.seams()
            seams.collect = failing_collect
            messages = []
            runner = Runner(REPO, root/'archive', '/fake/model-python', seams, emit=messages.append)
            fake_clock = SimpleNamespace(stamp=__import__('unittest').mock.Mock(side_effect=[stamps[k] for k in
                ('pre_spawn', 'sampling_started', 'sampling_stopped', 'post_parse')]))
            def ready(adapter, *_):
                adapter._first_parse_stamp = stamps['first_parse']
                return SimpleNamespace(ok=True)
            with (self.signals(fake), patch('joulewise.clock.SystemClock', return_value=fake_clock),
                  patch('joulewise.quiet_kit.collectors.snapshot', return_value={}),
                  patch.object(PowermetricsTelemetryAdapter, '_wait_until_ready', ready),
                  patch.object(PowermetricsTelemetryAdapter, '_wait_for_native_rollover', return_value=SimpleNamespace(ok=True))):
                self.assertEqual(runner.plumbing('m5-gpu-rail'), 1)
            attempt = next((root/'archive/_plumbing').glob('*/attempts/1/attempt.json'))
            if stubborn:
                self.assertTrue(fake.alive(fake.leader.pid))
                self.assertTrue(fake.alive(fake.child_pid))
                self.assertEqual(read_json(attempt)['reason'],'root_sampler_orphan')
                self.assertTrue(any('DIRECTOR ACTION REQUIRED: root_sampler_orphan' in line for line in messages))
                self.assertNotIn(signal.SIGKILL,[sig for _,sig in fake.group_signals+fake.pid_signals])
                self.assertFalse(list((root/'archive').glob('**/STATUS.json')))
            else:
                self.assertFalse(fake.alive(fake.leader.pid))
                self.assertFalse(fake.alive(fake.child_pid))
                self.assertIn('injected exception in first segment', read_json(attempt)['reason'])
                self.assertFalse(fake.manager.processes)

    def test_root_leftover_ends_job_with_done_status_journal_and_wake(self):
        hw = FakeHardware()
        action = {'director_action': 'root_sampler_orphan', 'pid': 42, 'uid': 0,
                  'argv': 'fixture root sampler', 'pgid': 41, 'group': 41}
        groups = [{'pgid': 41, 'gone': False, 'director_actions': [action]}]
        with tempfile.TemporaryDirectory(prefix='quiet-kit-root-done-') as tmp:
            root = Path(tmp)
            (root/'WAKE_CMD').write_text('wake-for-root-orphan')
            def collect(*args):
                hw.collected.append(args[0].test_id)
                raise TeardownBlocked(groups)
            seams = hw.seams()
            seams.collect = collect
            messages = []
            runner = Runner(REPO, root, '/fake/model-python', seams, plans=PLANS[:2], scale=.001, emit=messages.append)
            self.assertEqual(runner.run(), 0)
            self.assertEqual(hw.collected, [PLANS[0].test_id])
            self.assertEqual(hw.wakes, ['wake-for-root-orphan'])
            self.assertEqual(read_json(root/'DONE')['director_actions'], [action])
            self.assertEqual(read_json(root/'STATUS.json')['director_actions'], [action])
            self.assertEqual(read_json(root/'STATUS.json')['director_action'], 'root_sampler_orphan')
            self.assertEqual(read_json(root/PLANS[0].test_id/'attempts/1/attempt.json')['director_actions'], [action])
            journal = [json.loads(line) for line in (root/'journal.jsonl').read_text().splitlines()]
            self.assertTrue(any(action in row.get('director_actions', []) for row in journal))
            self.assertTrue(all(r['last_reason'] == 'root_sampler_orphan' for r in read_json(root/'DONE')['incomplete_tests']))
            self.assertTrue(any('DIRECTOR ACTION REQUIRED: root_sampler_orphan' in line for line in messages))
