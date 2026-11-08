"""Delta witnesses at ed65d9094: synthetic paths/hosts, no measurements.

Assertions describe the required safety property. Surviving findings deliberately
fail without skip/expectedFailure decorators. Process-group native controls live
in tests.align.test_w1_smoke.BoundedRunTests (run that module separately).
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.align import w1_prequal as wp, w1_smoke as smoke
from tests.align import test_w1_smoke as fixtures

ROOT = Path(__file__).resolve().parents[2]


class DeltaFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='smoke-delta-sol1-')
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name).resolve()
        self.home = self.tmp / 'account-home'
        (self.home / 'Library/LaunchAgents').mkdir(parents=True)
        patch = mock.patch.object(Path, 'home', return_value=self.home)
        patch.start()
        self.addCleanup(patch.stop)
        host = self.tmp / 'host'
        host.mkdir()
        patch = mock.patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(host)})
        patch.start()
        self.addCleanup(patch.stop)
        self.production = self.tmp / 'synthetic-production'
        self.production.mkdir()
        self.config = smoke.load_config(ROOT)
        # Never resolve the real home roots named in the checked-in config.
        self.config['production_roots'] = [str(self.tmp / 'synthetic-custody')]
        config = self.production / smoke.CONFIG
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps(self.config))
        self.clock = fixtures.Clock()
        self.mbp = fixtures.FakeMBP(self, self.clock)
        self.prequal = self.tmp / 'prequal.json'
        self.prequal.write_text(json.dumps({'status': 'PASS', 'commit': 'a' * 40,
                                            'next': 'w1', 'checkout_dirty': False}))

    def runner(self, **changes):
        options = dict(packet={}, battery_log=self.tmp / 'battery', obc_off_attested_by='synthetic',
                       w1_disk_config=self.tmp / 'disk', prequal_report=self.prequal,
                       python='/synthetic/python', config=self.config, run=self.mbp,
                       popen=mock.Mock(return_value=fixtures.FakeProcess()), clock=self.clock,
                       sleep=self.clock.sleep, prepare=fixtures.fake_prepare, isolate_fn=fixtures.fake_isolate)
        options.update(changes)
        return smoke.SmokeRunner(self.production, options.pop('smoke_dir', self.tmp / 'smoke'), **options)

    def context(self):
        work = self.tmp / 'work'
        work.mkdir(exist_ok=True)
        return wp.Context(self.production, work, 'w1', commit='a' * 40)


class IsolationDelta(DeltaFixture):
    def test_literal_resolved_relative_private_and_tmpdir_controls(self):
        isolated = self.tmp / 'smoke'
        isolated.mkdir()
        production = self.tmp / 'custody-target'
        production.mkdir()
        alias = self.tmp / 'custody-alias'
        alias.symlink_to(production, target_is_directory=True)
        roots = smoke.production_roots(self.production, {'production_roots': [str(alias)]})
        for path in (str(alias / 'out'), str(production / 'out'), '../custody-target/out'):
            with self.subTest(path=path):
                self.assertTrue(smoke.isolation_violations(isolated, {}, roots,
                                    plan={'nested': {'claim_runs_root': path}}))
        # /tmp <-> /private/tmp folding is lexical, with a unique synthetic root.
        lexical = str(production).removeprefix('/private')
        self.assertIsNotNone(smoke._inside(Path(lexical) / 'out', roots))
        self.assertTrue(smoke.isolation_violations(isolated, {}, roots,
                            env={'TMPDIR': str(production)}))
        self.assertFalse(smoke.isolation_violations(isolated,
                            {'custody_root': str(isolated / 'custody')}, roots,
                            env={'TMPDIR': str(isolated / 'tmp')}))

    def test_D1_detached_cli_checks_destination_before_parent_write(self):
        from scripts import align_v4_w1_smoke as cli
        directory = self.production / 'new-parent/smoke'
        argv = ['run', '--measurement-root', str(self.production), '--smoke-dir', str(directory),
                '--prequal-report', str(self.prequal), '--next-arm-triage', str(self.tmp / 'packet'),
                '--w1-disk-config', str(self.tmp / 'disk'), '--obc-off-attested-by', 'synthetic',
                '--battery-log', str(self.tmp / 'battery'), '--detach']
        self.assertTrue(smoke.destination_violations(directory, [str(self.production)]))
        # No process is launched. The actual CLI still creates the forbidden parent.
        with mock.patch.object(smoke, 'detach', return_value=123), contextlib.redirect_stdout(io.StringIO()):
            try:
                cli.main(argv)
            except SystemExit:
                pass
        self.assertFalse(directory.parent.exists(), 'detach wrote inside the protected checkout before validation')

    def test_published_unloaded_night_and_deadman_each_block(self):
        runner = self.runner()
        runner.dir.mkdir()
        for label in (smoke.NIGHT_LABEL, smoke.NIGHT_LABEL + '.deadman'):
            with self.subTest(label=label):
                plist = self.home / f'Library/LaunchAgents/{label}.plist'
                plist.write_text('synthetic installed but unloaded plan')
                try:
                    self.assertFalse(runner.guards()[0])
                finally:
                    plist.unlink()

    def test_D2_reducer_does_not_follow_manifest_swapped_after_check(self):
        from scripts import align_v4_kit as kit, bytes_h_session as h
        isolated = self.tmp / 'smoke'
        session = isolated / 'main'
        session.mkdir(parents=True)
        # The real view/reducer uses code/config bytes only; no source runs/ is read.
        with contextlib.redirect_stdout(io.StringIO()):
            view, pack = h.measurement_view(ROOT, session, kit=kit.KIT, pack_id=kit.PACK_ID)
        tree = json.loads((pack / 'plan_tree.json').read_bytes())
        stage = next(row for row in tree['stage_graph'] if row['stage_id'] == 'align-v4-reference-start')
        manifest = view / stage['input']['path']
        victim = self.production / 'victim-manifest.json'
        victim.write_bytes(manifest.read_bytes())
        before = victim.read_bytes()
        read_bytes = Path.read_bytes
        swapped = []

        def swap_after_read(path):
            raw = read_bytes(path)
            if path == manifest and not swapped:
                # writable(path) has already returned. Only a disposable file is swapped.
                path.unlink()
                path.symlink_to(victim)
                swapped.append(True)
            return raw

        with mock.patch.object(Path, 'read_bytes', swap_after_read):
            try:
                smoke.reduce_view(view, pack, self.config['keep'])
            except smoke.IsolationAbort:
                pass
        self.assertTrue(swapped, 'the witness must reach the check/use boundary')
        self.assertEqual(victim.read_bytes(), before, 'the reducer followed the replacement symlink and wrote production')

    def test_D7_other_launch_write_bindings_cannot_use_the_readonly_exception(self):
        isolated = self.tmp / 'smoke'
        isolated.mkdir()
        sites = self.production / 'synthetic-site-packages'
        sites.mkdir()
        roots = [str(self.production)]
        for key in ('operator_log_root', 'pre_calibration_dir', 'post_calibration_dir'):
            with self.subTest(key=key):
                self.assertTrue(smoke.isolation_violations(isolated, {}, roots,
                    plan={'hazard_window': {'bindings': {key: str(sites / 'write-target')}}},
                    readonly=[str(sites)]), f'{key} is a launch WRITE binding, not a read-only import')


class NativeDelta(DeltaFixture):
    def test_budget_exhaustion_and_failed_detach_stop_main_arm(self):
        for cause in ('budget', 'detach'):
            with self.subTest(cause=cause):
                self.mbp = fixtures.FakeMBP(self, self.clock, still_mounted=(cause == 'detach'))
                runner = self.runner(smoke_dir=self.tmp / cause)
                original = runner.arm_fault

                def slow(*args):
                    result = original(*args)
                    self.clock.sleep(400)
                    return result

                if cause == 'budget':
                    runner.arm_fault = slow
                self.assertNotEqual(runner.run(), 0)
                self.assertIsNone(self.mbp.main_state)
                self.clock = fixtures.Clock()

    def test_D3_isolation_preparation_share_the_hard_deadline(self):
        called = []

        def isolate_slow(*args, **kw):
            self.clock.sleep(self.config['budget_s'] + 1)
            return fixtures.fake_isolate(*args, **kw)

        def prepare(*args, **kw):
            called.append(self.clock())
            return fixtures.fake_prepare(*args, **kw)

        runner = self.runner(isolate_fn=isolate_slow, prepare=prepare)
        self.assertNotEqual(runner.run(), 0)
        self.assertIsNone(self.mbp.main_state)
        self.assertEqual(called, [], 'prepare still writes after the global deadline expired during isolation')

    def test_D4_install_timeout_still_cleans_up_a_job_published_before_return(self):
        class InstalledThenTimedOut(fixtures.FakeMBP):
            def install(host, argv):
                result = super().install(argv)
                if host.main_state is not None:
                    host.job_loaded = True
                    # bounded_run reports an unproven group after the installer published.
                    result.group_survived = True
                return result

        self.mbp = InstalledThenTimedOut(self, self.clock)
        runner = self.runner()
        self.assertNotEqual(runner.run(), 0)
        self.assertIsNotNone(self.mbp.main_state, 'the synthetic installer must have published the smoke job')
        self.assertFalse(self.mbp.job_loaded, 'ownership was recorded too late; finally left the installed job loaded')

    def test_terminal_timeout_cleans_up_an_already_recorded_owned_job(self):
        class NeverCloses(fixtures.FakeMBP):
            def build_window(host, state):
                super().build_window(state)
                (Path(state['inputs']['custody_root']) / 'night/result.json').unlink()
                host.job_loaded = True

        self.mbp = NeverCloses(self, self.clock)
        runner = self.runner()
        runner.run()
        self.assertIsNone(runner.installed)
        self.assertFalse(self.mbp.job_loaded)
        self.assertTrue(any('--uninstall' in argv for argv in self.mbp.calls))


class ProjectionDelta(DeltaFixture):
    def test_D5_deadline_refuses_forged_plan_with_only_matching_labels(self):
        from joulewise import night_gate
        from joulewise.b6 import plan_inputs
        plan = {'schema': night_gate.HAZARD_PLAN_SCHEMA, 'receipt_class': night_gate.HAZARD_PACK,
                'plan_id': 'align-v4-forged-plan-copy', 'pack': {'programmed_span_s': 1},
                'window_max_s': plan_inputs.window_max_s({'programmed_span_s': {'seconds': 1}})}
        # Not even a structurally valid installed plan; no source identity or schedule.
        with self.assertRaises((ValueError, TypeError)):
            night_gate.NightPlan.from_mapping(plan)
        path = self.production / 'night_plan.json'
        path.write_text(json.dumps(plan))
        ctx = self.context()
        ctx.deadline_projection = path.name
        row = wp.probe('deadline', ctx)
        self.assertEqual(row['status'], wp.FAIL, row)

    def test_series_roster_order_and_counts_are_bound_to_source(self):
        ctx = self.context()
        windows = ([{'window': 'W1', 'role': 'w1'}]
                   + [{'window': f'C{i}', 'role': 'calibration', 'benign_per_pair': {'spam': 7, 'bank': 7}}
                      for i in range(1, 9)] + [{'window': 'T1', 'role': 'test'}])
        source = self.production / 'series-source.json'
        source.write_text(json.dumps({'windows': windows}))
        value = {'schema': wp.SERIES_SCHEMA, 'windows': copy.deepcopy(windows),
                 'source': {'path': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}}
        projection = self.production / 'series.json'
        ctx.series_projection = projection.name
        projection.write_text(json.dumps(value))
        self.assertEqual(wp.probe('series-manifest', ctx)['status'], wp.PASS)
        for change in ('order', 'count', 'omit'):
            with self.subTest(change=change):
                edited = copy.deepcopy(value)
                if change == 'order':
                    edited['windows'][1:3] = reversed(edited['windows'][1:3])
                elif change == 'count':
                    edited['windows'][1]['benign_per_pair']['spam'] = 1
                else:
                    edited['windows'].pop(3)
                projection.write_text(json.dumps(edited))
                self.assertEqual(wp.probe('series-manifest', ctx)['status'], wp.FAIL)


class PacketDelta(DeltaFixture):
    def packet_probe(self, mode):
        """The production tamper probe against a bounded, deterministic rebuilding arm."""
        ctx = self.context()
        valid = {'schema': 'synthetic.packet', 'valid_until_epoch_s': self.clock() + 600,
                 'checks': {'full_desk_gate': {'status': 'pass', 'basis': 'synthetic'}},
                 'window_chain': [{'window': 'C3#1', 'commit': 'a' * 40, 'sha256': 'b' * 64},
                                  {'window': 'C3#2', 'commit': 'c' * 40, 'sha256': 'd' * 64}],
                 'calibration_windows': [{'window': 'C3#1', 'captured_members': 0},
                                         {'window': 'C3#2', 'captured_members': 22}]}

        def arm(_ctx, _root, packet, **_kw):
            edited = copy.deepcopy(packet)
            if mode == 'status':
                entry = (edited.get('checks') or {}).get('full_desk_gate')
                if isinstance(entry, dict) and 'status' in entry:
                    entry['status'] = 'pass'
            chain = edited.get('window_chain')
            if isinstance(chain, list) and len(chain) == 2 and isinstance(chain[0], dict):
                if mode == 'element':
                    chain[0] = copy.deepcopy(valid['window_chain'][0])
                if mode == 'chain-sha':
                    chain[0]['sha256'] = valid['window_chain'][0]['sha256']
            strip = lambda p: {k: v for k, v in p.items() if k not in wp.PACKET_IGNORED}
            same = strip(edited) == strip(valid)
            return {'admitted': same, 'reasons': [] if same else [
                'next_arm_triage: packet does not match its committed sources'],
                'next_arm_triage': {'rebuilt_packet': valid}}

        seed = arm(ctx, self.production, valid)
        with mock.patch.object(wp, '_rebuild', return_value=(self.production, None, self.clock(), valid, seed, valid)), \
                mock.patch.object(wp, '_arm_file', arm):
            row = wp.check_packet_tamper(ctx)
        return row, valid, arm

    def test_nested_failed_status_and_ignored_chain_element_are_caught(self):
        for mode in ('status', 'element'):
            with self.subTest(mode=mode):
                row, _valid, _arm = self.packet_probe(mode)
                self.assertEqual(row['status'], wp.FAIL, row)

    def test_D6_packet_probe_catches_an_arm_ignoring_one_chain_hash(self):
        row, valid, arm = self.packet_probe('chain-sha')
        edited = copy.deepcopy(valid)
        edited['window_chain'][0]['sha256'] = 'e' * 64
        self.assertTrue(arm(None, None, edited)['admitted'], 'stand-in must accept the unverified chain digest')
        self.assertEqual(row['status'], wp.FAIL, row)

    def test_strict_packet_control_passes(self):
        row, _valid, _arm = self.packet_probe('strict')
        self.assertEqual(row['status'], wp.PASS, row)


class ReceiptDelta(unittest.TestCase):
    def test_current_first_party_closure_includes_scripts_and_is_receipt_covered(self):
        from joulewise.align.apple import v4_registration as reg
        closure = wp.executed_closure(ROOT)
        self.assertIn('scripts/align_v4_session.py', closure)
        self.assertIn('joulewise/b5/driver.py', closure)
        self.assertEqual(set(closure) - set(reg.ARTIFACTS), set())


if __name__ == '__main__':
    unittest.main()
