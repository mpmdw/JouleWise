"""Adversarial review witnesses for f6251227a; all roots/data are synthetic.

Expected failures assert the intended contract, NOT successful qualification.
Remove each decorator when its finding is fixed; unexpected success requests
that review. No native smoke, model, sensor, launchd, or production path runs.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise.align import w1_prequal as wp, w1_smoke as smoke
from tests.align import test_w1_smoke as fixtures
from tests.align.test_w1_prequal import RebuildingArm

ROOT = Path(__file__).resolve().parents[2]


class TemporaryContext(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='w1review-projection-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ctx = wp.Context(self.root, self.root / 'work', 'w1', commit='a' * 40)
        self.ctx.work.mkdir()

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value))
        return name


class ProjectionWitnesses(TemporaryContext):
    def deadline(self, kind='w1'):
        return {'window_max_s': 1, 'programmed_span_s': 43200,
                'smoke_deadline_projection': {
                    'kind': kind, 'bracket_s': 0, 'close_s': 0, 'harvest_s': 0,
                    'segments': [{'bound_s': 1, 'attempts': 1, 'batch_encounters': 0}]}}

    @unittest.expectedFailure
    def test_S1_deadline_cannot_understate_the_installed_span(self):
        self.ctx.deadline_projection = self.write('deadline.json', self.deadline())
        self.assertEqual(wp.check_deadline(self.ctx)['status'], wp.FAIL)

    @unittest.expectedFailure
    def test_S1_d_projection_cannot_qualify_the_w1_gate(self):
        self.ctx.deadline_projection = self.write('deadline.json', self.deadline('d'))
        self.assertEqual(wp.check_deadline(self.ctx)['status'], wp.FAIL)

    @unittest.expectedFailure
    def test_S2_series_projection_must_describe_its_hashed_source(self):
        windows = ([{'window': 'W1', 'role': 'w1'}]
                   + [{'window': f'C{i}', 'role': 'calibration',
                       'benign_per_pair': {'spam': 7, 'bank': 7}} for i in range(1, 9)]
                   + [{'window': 'T1', 'role': 'test'}])
        bad = copy.deepcopy(windows)
        bad[1]['benign_per_pair'] = {'spam': 1, 'bank': 1}
        source = self.write('source.json', {'windows': bad})
        projection = {'schema': wp.SERIES_SCHEMA, 'windows': windows,
                      'source': {'path': source, 'sha256': hashlib.sha256(
                          (self.root / source).read_bytes()).hexdigest()}}
        self.ctx.series_projection = self.write('series.json', projection)
        self.assertEqual(wp.check_series_manifest(self.ctx)['status'], wp.FAIL)

    def test_controls_reject_short_budget_and_wrong_source_hash(self):
        value = self.deadline()
        value['smoke_deadline_projection']['segments'][0]['bound_s'] = 2
        with self.assertRaisesRegex(ValueError, 'corrected requirement'):
            wp.validate_deadline(value)
        self.write('source.json', {})
        self.ctx.series_projection = self.write('series.json', {
            'source': {'path': 'source.json', 'sha256': '0' * 64}})
        self.assertEqual(wp.check_series_manifest(self.ctx)['status'], wp.FAIL)


class PacketWitnesses(TemporaryContext):
    def setUp(self):
        super().setUp()
        self.env = mock.patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.root / 'host')})
        self.env.start()
        self.addCleanup(self.env.stop)

    @unittest.expectedFailure
    def test_S3_mandatory_expiry_is_distinguished_from_unrelated_late_refusal(self):
        class NoPacketExpiry(RebuildingArm):
            def __init__(self):
                super().__init__(expiry=False)
                self.first_now = None

            def rebuild(self, root):
                rebuilt = super().rebuild(root)
                rebuilt.pop('expires_at_epoch_s')
                return rebuilt

            def __call__(self, *args, now, **kw):
                self.first_now = self.first_now or now()
                row = super().__call__(*args, now=now, **kw)
                if now() > self.first_now + 86400:
                    row.update(admitted=False, reasons=['unrelated host/record freshness refusal'])
                return row

        from scripts import align_v4_session as session
        with mock.patch.object(session, 'arm_checks', NoPacketExpiry()):
            row = wp.check_packet_rebuild(self.ctx)
        self.assertEqual(row['status'], wp.FAIL, row)

    @unittest.expectedFailure
    def test_S3_tamper_probe_needs_an_admitted_control_of_its_own(self):
        class RejectEverything(RebuildingArm):
            def __call__(self, *args, **kw):
                row = super().__call__(*args, **kw)
                row.update(admitted=False, reasons=['unrelated refusal for every arm'])
                return row

        from scripts import align_v4_session as session
        with mock.patch.object(session, 'arm_checks', RejectEverything()):
            row = wp.check_packet_tamper(self.ctx)
        self.assertEqual(row['status'], wp.FAIL, row)


class ReceiptWitnesses(TemporaryContext):
    @unittest.expectedFailure
    def test_S10_executed_scripts_must_be_covered_as_well_as_python_package_modules(self):
        from joulewise.align.apple import v4_registration as reg
        repo = self.root / 'repo'
        repo.mkdir()
        self.ctx.repo = repo
        bound = ('docs/align/v4/PREQUAL.md', 'joulewise/example.py')
        for relative in (*bound, 'scripts/unbound.py'):
            path = repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# synthetic\n')
        env = {**os.environ, 'GIT_AUTHOR_NAME': 'Review witness', 'GIT_AUTHOR_EMAIL': 'review@invalid',
               'GIT_COMMITTER_NAME': 'Review witness', 'GIT_COMMITTER_EMAIL': 'review@invalid'}
        for args in (('init', '-q'), ('add', '.'), ('commit', '-q', '-m', 'synthetic receipt fixture')):
            subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
                            '-C', str(repo), *args], check=True, capture_output=True, env=env, timeout=30)
        self.ctx.commit = wp.git(repo, 'rev-parse', 'HEAD')
        # Provisioned-registration acceptance is independent of the closure test.
        # The exact/drift receipt validator self-tests still execute unmodified.
        with mock.patch.object(reg, 'ARTIFACTS', bound), \
                mock.patch.object(reg, 'require_registration', return_value={'commit': self.ctx.commit}), \
                mock.patch.object(wp, 'executed_closure', return_value={'scripts/unbound.py'}):
            row = wp.check_receipt(self.ctx)
        self.assertEqual(row['status'], wp.FAIL, row)


class NativeRunnerWitnesses(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='w1review-native-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.production = self.root / 'production'
        config_path = self.production / smoke.CONFIG
        config_path.parent.mkdir(parents=True)
        self.config = smoke.load_config(ROOT)
        self.config['production_roots'] = []
        config_path.write_text(json.dumps(self.config))
        self.env = mock.patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.root / 'host')})
        self.env.start()
        self.addCleanup(self.env.stop)
        (self.root / 'host').mkdir()
        self.clock = fixtures.Clock()
        self.mbp = fixtures.FakeMBP(self, self.clock)
        self.prequal = self.root / 'prequal.json'
        self.prequal.write_text(json.dumps({'status': 'PASS', 'commit': 'a' * 40,
                                            'next': 'w1', 'checkout_dirty': False}))

    def runner(self, **kw):
        options = dict(packet=wp.triage_packet(), battery_log=self.root / 'battery.jsonl',
                       obc_off_attested_by='synthetic', w1_disk_config=self.root / 'disk.json',
                       prequal_report=self.prequal, run=self.mbp,
                       popen=mock.Mock(return_value=fixtures.FakeProcess()),
                       sleep=self.clock.sleep, clock=self.clock,
                       prepare=fixtures.fake_prepare, isolate_fn=fixtures.fake_isolate,
                       config=self.config)
        options.update(kw)
        return smoke.SmokeRunner(self.production, options.pop('smoke_dir', self.root / 'smoke'), **options)

    def main_installs(self):
        return [c for c in self.mbp.calls if 'install' in c and '--session-root' in c
                and Path(c[c.index('--session-root') + 1]).name == 'main']

    @unittest.expectedFailure
    def test_S4_production_smoke_dir_refused_before_creating_or_cloning(self):
        isolate = mock.Mock(side_effect=fixtures.fake_isolate)
        runner = self.runner(smoke_dir=self.production / 'smoke', isolate_fn=isolate)
        self.assertEqual(runner.run(), 2)
        self.assertFalse((self.production / 'smoke').exists())
        isolate.assert_not_called()

    @unittest.expectedFailure
    def test_S4_relative_write_paths_are_not_silently_ignored(self):
        roots = smoke.production_roots(self.production, self.config)
        self.assertTrue(smoke.isolation_violations(self.root / 'smoke',
            {'inputs': {'custody_root': '../production/custody'}}, roots))

    @unittest.expectedFailure
    def test_S4_configured_root_alias_protects_the_real_directory(self):
        real = self.root / 'real-custody'
        real.mkdir()
        alias = self.root / 'custody-alias'
        alias.symlink_to(real, target_is_directory=True)
        roots = smoke.production_roots(self.production, {'production_roots': [str(alias)]})
        self.assertTrue(smoke.isolation_violations(self.root / 'smoke',
            {'inputs': {'custody_root': str(real / 'window')}}, roots))

    @unittest.expectedFailure
    def test_S5_fault_isolation_failure_aborts_before_the_main_arm(self):
        real = smoke.fault_session

        def escape(*args, **kw):
            session = real(*args, **kw)
            if args[1] == 'arm-control':
                path = session / 'session.json'
                state = json.loads(path.read_bytes())
                state['inputs']['custody_root'] = str(self.production / 'custody')
                path.write_text(json.dumps(state))
            return session

        with mock.patch.object(smoke, 'fault_session', escape):
            self.runner().run()
        self.assertEqual(self.main_installs(), [])

    @unittest.expectedFailure
    def test_S5_fault_plan_is_scanned_before_its_install_attempt(self):
        real = smoke.fault_session

        def escape(*args, **kw):
            session = real(*args, **kw)
            state = json.loads((session / 'session.json').read_bytes())
            plan_path = Path(state['plan_path'])
            plan = json.loads(plan_path.read_bytes())
            plan['claim_runs_root'] = str(self.production / 'runs/escape')
            plan_path.write_text(json.dumps(plan))
            state['plan_sha256'] = hashlib.sha256(plan_path.read_bytes()).hexdigest()
            (session / 'session.json').write_text(json.dumps(state))
            return session

        with mock.patch.object(smoke, 'fault_session', escape):
            self.runner().run()
        self.assertFalse(any('install' in c and '--session-root' in c
                             and 'faults' in Path(c[c.index('--session-root') + 1]).parts
                             for c in self.mbp.calls))

    @unittest.expectedFailure
    def test_S6_a_published_but_unloaded_real_plan_blocks_smoke(self):
        home = self.root / 'home'
        plist = home / 'Library/LaunchAgents/com.joulewise.night.plist'
        plist.parent.mkdir(parents=True)
        import plistlib
        plist.write_bytes(plistlib.dumps({'ProgramArguments': [
            '/synthetic/run_night.py', '--plan', str(self.production / 'plan.json')]}))
        runner = self.runner()
        runner.dir.mkdir()
        with mock.patch.object(Path, 'home', return_value=home):
            admitted, _ = runner.guards()
        self.assertFalse(admitted)

    @unittest.expectedFailure
    def test_S7_exhausted_wall_budget_prevents_main_install(self):
        runner = self.runner()
        real = runner.arm_fault

        def slow(*args):
            result = real(*args)
            self.clock.sleep(400)
            return result

        runner.arm_fault = slow
        runner.run()
        self.assertEqual(self.main_installs(), [])

    @unittest.expectedFailure
    def test_S7_failed_detach_prevents_the_main_arm(self):
        self.mbp.still_mounted = True
        self.runner().run()
        self.assertEqual(self.main_installs(), [])

    @unittest.expectedFailure
    def test_S7_terminal_timeout_tears_down_the_smoke_job_it_installed(self):
        class NeverCloses(fixtures.FakeMBP):
            def build_window(mbp, state):
                super().build_window(state)
                (Path(state['inputs']['custody_root']) / 'night/result.json').unlink()
                mbp.job_loaded = True

        self.mbp = NeverCloses(self, self.clock)
        self.runner().run()
        self.assertTrue(any('bootout' in c or '--uninstall' in c for c in self.mbp.calls))

    def test_control_loaded_job_prevents_any_arm(self):
        self.mbp.job_loaded = True
        self.assertEqual(self.runner().run(), 2)
        self.assertEqual(self.main_installs(), [])

    @unittest.expectedFailure
    def test_S8_timeout_kills_descendants_even_if_parent_exits_on_term(self):
        process = mock.Mock(pid=123456)
        process.communicate.side_effect = [subprocess.TimeoutExpired('synthetic', 1), ('', '')]
        with mock.patch.object(subprocess, 'Popen', return_value=process), \
                mock.patch.object(os, 'killpg') as killpg:
            smoke.bounded_run(['synthetic'], timeout=1)
        self.assertIn(mock.call(process.pid, signal.SIGKILL), killpg.call_args_list)


class MeasurementViewWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='w1review-view-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        cls.production = cls.root / 'stand-in-production'
        subprocess.run(['git', 'clone', '--quiet', '--shared', str(ROOT), str(cls.production)],
                       check=True, capture_output=True, timeout=120)

    def view(self):
        from scripts import align_v4_kit as kit, bytes_h_session as h
        session = Path(tempfile.mkdtemp(prefix='session-', dir=self.root))
        return h.measurement_view(self.production, session, kit=kit.KIT, pack_id=kit.PACK_ID)

    @unittest.expectedFailure
    def test_S9_view_receipt_locator_is_acceptable_to_production_validator(self):
        from joulewise.align.apple import v4_registration as reg
        view, _ = self.view()
        # Check the exact path resolver, before receipt contents/readiness matter.
        reg._local(view, reg.REGISTRATION + 'registration_receipt.json')

    def test_control_reduced_view_preserves_the_production_kit_byte_check(self):
        from scripts import align_v4_kit as kit
        view, pack = self.view()
        smoke.reduce_view(view, pack, smoke.load_config(ROOT)['keep'])
        # Only pending registration is bypassed. Real generated bytes are compared.
        with mock.patch.object(kit, 'require_w1_ready'):
            kit.generate(view, check=True, source_root=self.production)

    @unittest.expectedFailure
    def test_S4_reduction_does_not_write_through_a_planted_manifest_symlink(self):
        view, pack = self.view()
        tree = json.loads((pack / 'plan_tree.json').read_bytes())
        stage = next(s for s in tree['stage_graph'] if s['stage_id'] == 'align-v4-reference-start')
        manifest = view / stage['input']['path']
        victim = self.production / 'synthetic-escape-manifest.json'
        victim.write_bytes(manifest.read_bytes())
        before = victim.read_bytes()
        manifest.unlink()
        manifest.symlink_to(victim)
        smoke.reduce_view(view, pack, smoke.load_config(ROOT)['keep'])
        self.assertEqual(victim.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
