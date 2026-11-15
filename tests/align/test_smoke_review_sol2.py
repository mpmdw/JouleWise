"""Review witnesses for f6251227a, synthetic paths/hosts only.

These assert the required properties and deliberately FAIL on the reviewed
candidate. They are executable repair acceptance criteria, not native evidence.
Run this module alone; no models, network, real host commands or study data.
"""
from __future__ import annotations

from tests.git_fixture import init_git_fixture
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise.align import w1_prequal as wp, w1_smoke as smoke
from tests.align.test_w1_prequal import RebuildingArm
from tests.align.test_w1_smoke import (
    Clock, FakeMBP, FakeProcess, KEPT, fake_isolate, fake_prepare,
)

ROOT = Path(__file__).resolve().parents[2]


class ReviewFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='smoke-review-sol2-')
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name)
        host = self.tmp / 'host'
        host.mkdir()
        patch = mock.patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(host)})
        patch.start()
        self.addCleanup(patch.stop)
        self.clock = Clock()
        self.production = self.tmp / 'synthetic-production'
        self.production.mkdir()
        self.config = smoke.load_config(ROOT)
        # Do not even resolve the real configured production-root strings.
        self.config['production_roots'] = [str(self.tmp / 'synthetic-custody')]
        config_path = self.production / smoke.CONFIG
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps(self.config))
        self.prequal = self.tmp / 'prequal.json'
        self.prequal.write_text(json.dumps({
            'status': 'PASS', 'commit': 'a' * 40, 'next': 'w1', 'checkout_dirty': False,
        }))

    def runner(self, mbp, *, directory=None, **kwargs):
        return smoke.SmokeRunner(
            self.production, directory or self.tmp / 'smoke', packet=wp.triage_packet(),
            battery_log=self.tmp / 'battery.jsonl', obc_off_attested_by='synthetic',
            w1_disk_config=self.tmp / 'disk.json', prequal_report=self.prequal,
            python=sys.executable, config=copy.deepcopy(self.config), run=mbp,
            popen=kwargs.pop('popen', mock.Mock(return_value=FakeProcess())),
            clock=self.clock, sleep=self.clock.sleep, isolate_fn=fake_isolate,
            prepare=fake_prepare, **kwargs,
        )

    def projection(self, name, value):
        path = self.production / name
        path.write_text(json.dumps(value))
        return name

    def ctx(self, **kwargs):
        work = self.tmp / 'work'
        work.mkdir(exist_ok=True)
        return wp.Context(self.production, work, commit='a' * 40, **kwargs)


class IsolationWitnesses(ReviewFixture):
    def test_protected_smoke_directory_is_rejected_before_first_write(self):
        protected = self.production / 'runs/smoke-escape'
        mbp = FakeMBP(self, self.clock)
        runner = self.runner(mbp, directory=protected)
        self.assertEqual(runner.run(), 2)
        self.assertFalse(protected.exists(), 'protected root was written before isolation rejection')

    def test_fault_plan_escape_is_checked_before_install(self):
        mbp = FakeMBP(self, self.clock)
        runner = self.runner(mbp)
        runner.dir.mkdir()
        runner.started = self.clock()
        runner.clone = runner.dir / 'measurement'
        main = runner.dir / 'main'
        fake_prepare(runner.clone, main, self.config['keep'])
        original = smoke.fault_session

        def escaped_plan(*args, **kwargs):
            session = original(*args, **kwargs)
            state = json.loads((session / 'session.json').read_text())
            path = Path(state['plan_path'])
            plan = json.loads(path.read_text())
            plan['claim_runs_root'] = str(self.production / 'runs/escaped')
            path.write_text(json.dumps(plan))
            state['plan_sha256'] = smoke.sha256(path)
            (session / 'session.json').write_text(json.dumps(state))
            # Prove the plan-aware checker catches this exact fixture.
            self.assertTrue(smoke.isolation_violations(runner.dir, state, runner.roots, plan=plan))
            return session

        with mock.patch.object(smoke, 'fault_session', escaped_plan):
            with self.assertRaisesRegex(RuntimeError, 'isolat'):
                runner.arm_fault(smoke.ARM_FAULTS[0], main)

    def test_fault_state_escape_aborts_entire_smoke(self):
        mbp = FakeMBP(self, self.clock)
        runner = self.runner(mbp)
        original = smoke.fault_session

        def escaped_state(*args, **kwargs):
            session = original(*args, **kwargs)
            if args[1] == 'arm-control':
                path = session / 'session.json'
                state = json.loads(path.read_text())
                state['inputs']['custody_root'] = str(self.production / 'runs/escaped')
                path.write_text(json.dumps(state))
            return session

        with mock.patch.object(smoke, 'fault_session', escaped_state):
            runner.run()
        self.assertIsNone(mbp.main_state, 'main arm ran after a caught fault-isolation exception')

    def test_symlink_escape_is_detected_control(self):
        directory = self.tmp / 'smoke'
        directory.mkdir()
        (directory / 'escape').symlink_to(self.production)
        self.assertTrue(smoke.isolation_violations(directory, {}, [str(self.production)]))

    def test_readonly_import_exception_cannot_exempt_plan_write_paths(self):
        directory = self.tmp / 'smoke'
        directory.mkdir()
        packages = self.production / '.venv/lib/synthetic/site-packages'
        packages.mkdir(parents=True)
        plan = {'custody_root': str(packages / 'escaped-custody')}
        violations = smoke.isolation_violations(
            directory, {'inputs': {'custody_root': str(directory / 'custody')}},
            [str(self.production)], plan=plan, readonly=[str(packages)],
        )
        self.assertTrue(violations, 'a read-only import allowlist authorized a production custody write')


class NativeSafetyWitnesses(ReviewFixture):
    def test_failed_disk_teardown_prevents_main_arm(self):
        mbp = FakeMBP(self, self.clock, still_mounted=True)
        self.runner(mbp).run()
        self.assertIsNone(mbp.main_state, 'main arm ran with injected disk image still mounted')

    def test_exhausted_global_budget_prevents_main_arm(self):
        mbp = FakeMBP(self, self.clock)
        runner = self.runner(mbp)
        original = runner.arm_fault

        def consume_budget(fault, session):
            outcome = original(fault, session)
            if fault['id'] == 'arm-control':
                self.clock.now += self.config['budget_s'] + 1
            return outcome

        runner.arm_fault = consume_budget
        runner.run()
        self.assertIsNone(mbp.main_state, 'smoke installed after its global deadline')

    def test_timeout_kills_descendants_even_if_group_leader_exits_on_term(self):
        process = mock.Mock(pid=123456)
        # A child ignores TERM, closes inherited pipes, and outlives its parent.
        process.communicate.side_effect = [subprocess.TimeoutExpired(['synthetic'], 1), ('', '')]
        with mock.patch.object(smoke.subprocess, 'Popen', return_value=process), \
                mock.patch.object(smoke.os, 'killpg') as killpg:
            result = smoke.bounded_run(['synthetic'], timeout=1)
        self.assertEqual(result.returncode, 124)
        self.assertIn(mock.call(process.pid, signal.SIGKILL), killpg.call_args_list)

    def test_contender_is_reaped_after_forced_kill(self):
        contender = mock.Mock(pid=123456)
        contender.wait.side_effect = [subprocess.TimeoutExpired(['yes'], 10), 0]
        mbp = FakeMBP(self, self.clock)
        runner = self.runner(mbp, popen=mock.Mock(return_value=contender))
        runner.dir.mkdir()
        runner.started = self.clock()
        state = fake_prepare(runner.dir / 'measurement', runner.dir / 'main', self.config['keep'])
        for rows in KEPT.values():
            for run_id in rows:
                (Path(state['inputs']['runs_parent']) / 'claim' / run_id).mkdir(parents=True)
        runner.in_window_faults(state, self.clock() + 2700)
        contender.kill.assert_called_once()
        self.assertGreaterEqual(contender.wait.call_count, 2, 'SIGKILL was sent but the child was not reaped')


class ProjectionWitnesses(ReviewFixture):
    def test_deadline_requires_binding_to_actual_installed_schedule(self):
        # An invented zero-work schedule can pass regardless of the actual plan.
        projection = {'window_max_s': 0, 'smoke_deadline_projection': {
            'kind': 'w1', 'segments': [{'bound_s': 0, 'attempts': 1, 'batch_encounters': 0}],
            'bracket_s': 0, 'close_s': 0, 'harvest_s': 0,
        }}
        name = self.projection('deadline.json', projection)
        row = wp.probe('deadline', self.ctx(deadline_projection=name))
        self.assertEqual(row['status'], wp.FAIL, row)

    def test_d_projection_cannot_size_next_w1_or_bypass_r1_floor(self):
        projection = {'window_max_s': 0, 'smoke_deadline_projection': {
            'kind': 'd', 'segments': [{'bound_s': 0, 'attempts': 1, 'batch_encounters': 0}],
            'bracket_s': 0, 'close_s': 0, 'harvest_s': 0,
        }}
        name = self.projection('d.json', projection)
        statuses = {next_window: wp.probe('deadline', self.ctx(
            next_window=next_window, deadline_projection=name))['status'] for next_window in ('w1', 'r1')}
        self.assertEqual(statuses, {'w1': wp.FAIL, 'r1': wp.FAIL})

    def test_series_projection_must_match_hashed_source_roster(self):
        windows = ([{'window': 'W1', 'role': 'w1'}]
                   + [{'window': f'C{i}', 'role': 'calibration', 'benign_per_pair': {'spam': 7, 'bank': 7}}
                      for i in range(1, 9)] + [{'window': 'T1', 'role': 'test'}])
        source = self.projection('source.json', {'windows': [windows[0], windows[-1]]})
        projection = {'schema': wp.SERIES_SCHEMA, 'windows': windows, 'source': {
            'path': source, 'sha256': hashlib.sha256((self.production / source).read_bytes()).hexdigest(),
        }}
        name = self.projection('series.json', projection)
        row = wp.probe('series-manifest', self.ctx(series_projection=name))
        self.assertEqual(row['status'], wp.FAIL, row)


class PacketWitnesses(ReviewFixture):
    def test_both_packet_probes_reject_an_arm_lenient_on_nested_status(self):
        from scripts import align_v4_session

        class LenientStatusArm(RebuildingArm):
            def rebuild(self, root):
                packet = super().rebuild(root)
                packet['checks']['full_desk_gate'] = {'status': 'pass', 'basis': 'desk'}
                return packet

            def __call__(self, root, plan, *, next_arm_triage=None, **kwargs):
                packet = json.loads(Path(next_arm_triage).read_text())
                entry = (packet.get('checks') or {}).get('full_desk_gate')
                if isinstance(entry, dict) and 'status' in entry:
                    packet['checks']['full_desk_gate']['status'] = 'pass'
                # This arm silently repairs a failed status before comparison.
                path = Path(next_arm_triage).with_suffix('.lenient.json')
                path.write_text(json.dumps(packet))
                return super().__call__(root, plan, next_arm_triage=path, **kwargs)

        arm = LenientStatusArm()
        ctx = self.ctx()
        with mock.patch.object(align_v4_session, 'arm_checks', arm):
            rebuild = wp.probe('packet-rebuild', ctx)
            tamper = wp.probe('packet-tamper', ctx)
            root = next(ctx.work.glob('rebuild-*'))
            edited = arm.rebuild(root)
            edited['checks']['full_desk_gate']['status'] = 'fail'
            direct = wp._arm_file(ctx, root, edited, now=time.time())
        self.assertTrue(direct['admitted'], 'the stand-in must reproduce the nested-status escape')
        self.assertEqual(rebuild['status'], wp.PASS, rebuild)
        self.assertEqual(tamper['status'], wp.FAIL, tamper)


class ReceiptWitnesses(ReviewFixture):
    def test_receipt_coverage_includes_imported_scripts(self):
        from joulewise.align.apple import v4_registration as reg
        repository = self.tmp / 'receipt-repository'
        repository.mkdir()
        bound = ('docs/align/v4/PREQUAL.md', 'scripts/align_v4_kit.py')
        for name in (*bound, 'scripts/new_unbound_helper.py'):
            path = repository / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# synthetic\n')
        env = {**os.environ, 'GIT_AUTHOR_NAME': 'review', 'GIT_AUTHOR_EMAIL': 'review@invalid',
               'GIT_COMMITTER_NAME': 'review', 'GIT_COMMITTER_EMAIL': 'review@invalid'}

        def git(*args):
            return subprocess.run(['git', '-C', str(repository), *args], env=env,
                                  capture_output=True, text=True, check=True, timeout=30).stdout.strip()

        init_git_fixture(repository, '-q')
        git('config', 'commit.gpgsign', 'false')
        git('config', 'core.hooksPath', '/dev/null')
        git('add', '.')
        git('commit', '-qm', 'synthetic receipt')
        ctx = self.ctx()
        ctx.repo, ctx.commit = repository, git('rev-parse', 'HEAD')
        # Keep the real validator self-tests; stub only the ready registration.
        with mock.patch.object(reg, 'ARTIFACTS', bound), \
                mock.patch.object(wp, 'executed_closure', return_value={'scripts/new_unbound_helper.py'}), \
                mock.patch.object(reg, 'require_registration', return_value={'commit': ctx.commit}):
            row = wp.probe('receipt', ctx)
        self.assertEqual(row['status'], wp.FAIL, row)


if __name__ == '__main__':
    unittest.main()
