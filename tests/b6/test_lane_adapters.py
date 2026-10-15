"""Adapter seams and path budgets, with no live tools or measurement roots."""
from dataclasses import replace
import json
from pathlib import Path
import plistlib
import shutil
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from joulewise.b6 import compose, plan_inputs, session_paths
from joulewise.b6.queue import Selection
from joulewise.b6.analysis_lane import AnalysisLane, HarvestLane
from joulewise.b6.lanes import Waker
from joulewise.b6.precheck_lane import PrecheckLane, probe_runner
from tests.b6.support import DeskCase, ROOT, PACKS, synthetic_checkout, fake_environment
from tests.test_b6_registration import registrations


class AdapterTests(DeskCase):
    def setUp(self):
        super().setUp()
        self.measurement, self.loop = self.root / 'measurement', self.root / 'loop'
        for relative in ('configs/b6/flag_catalog_b6.json',
                         *(f'configs/b6/packs/{pack}/registration.json' for pack in PACKS)):
            target = self.measurement / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def test_session_paths_never_overlap_checkout_and_have_one_copy_per_device(self):
        paths = session_paths.for_session(self.measurement, self.loop, 'r1-alpha')
        self.assertEqual(paths.custody, self.root / 'sessions/r1-alpha/custody')
        self.assertEqual(paths.terminal, paths.custody / 'night/result.json')
        paths = replace(paths, backup_bound=self.root / 'second-volume')
        second = paths.backup_bound
        second.mkdir()
        def stat(path):
            path = Path(path)
            if not path.exists():
                raise FileNotFoundError(path)
            return SimpleNamespace(st_dev=2 if path == second else 1)
        targets = session_paths.disk_targets(paths, stat=stat)
        self.assertEqual(sum(row['copies'] for row in targets), 2)
        for path in ('claude-session', 'codex-session', '../escape'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                session_paths.for_session(self.measurement, self.loop, path)
        with self.assertRaises(ValueError):
            session_paths.for_session(self.measurement, self.loop, 's', roots={'archive': self.measurement / 'archive'})

    def test_p1_campaign_names_fresh_outputs_mapping_and_all_destinations(self):
        calls = []
        def check(campaign, measurement, state_root, **kwargs):
            calls.append((campaign, kwargs))
            self.assertNotIn('reap', kwargs)  # production reaps registered orphans (design 3.3)
            self.assertEqual(kwargs['registration_dir'], self.measurement / 'configs/b6/registration')
            self.assertEqual(sum(row['copies'] for row in kwargs['disk_targets']), 1)
            return {'fingerprint': {'campaign': campaign}, 'predicted_flags': [{'code': 'meter.absent'}],
                    'margin': {'status': 'thin'},
                    'would_refuse': [{'hazard': 'disk', 'code': 'disk.low'}],
                    'certain_exclusion': {'source': 'model_hash', 'reasons': ['model.hash_mismatch: test']}}
        layout = SimpleNamespace(session_id='s', packs=('alpha', 'beta'))
        lane = PrecheckLane(self.measurement, self.loop, Mock(side_effect=AssertionError('real process')),
                            check=check)
        result = lane.run(layout, str(self.root / 'unused-plan.json'))
        lane.run(layout, str(self.root / 'unused-plan.json'))
        self.assertEqual([c[0] for c in calls[:2]], [PACKS['alpha'], PACKS['beta']])
        self.assertEqual(len({c[1]['out'] for c in calls}), 4)
        self.assertEqual(result.predicted_flags, ('meter.absent',))
        self.assertTrue(result.thin_margin)
        self.assertEqual(result.remedies, ('disk',))
        self.assertEqual([(x.code, x.pack_id) for x in result.certain_exclusion],
                         [('model.files_differ_from_registered', p) for p in ('alpha', 'beta')])
        self.assertEqual(set(result.fingerprint['packs']), {'alpha', 'beta'})
        self.assertFalse(lane.remedy('sampler'))
        self.assertFalse(lane.remedy('instrument'))

    def test_probe_runner_preserves_bytes_and_process_failures(self):
        run = Mock(return_value=SimpleNamespace(returncode=0, stdout='text', stderr=b'error'))
        result = probe_runner(run)(('git', '--version'), 1)
        self.assertEqual((result.stdout, result.stderr), (b'text', b'error'))
        run.side_effect = OSError('synthetic failure')
        self.assertIsNotNone(probe_runner(run)(('git',), 1).error)

    def test_p1_runs_the_real_precheck_with_fake_probes_and_no_signals(self):
        case = self.root / 'real-check'
        case.mkdir()
        measurement, _, _ = synthetic_checkout(case)
        for relative in ('configs/b6/flag_catalog_b6.json', 'configs/b6/packs/alpha/registration.json'):
            target = measurement / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        ctx, seams, _ = fake_environment(measurement)
        lane = PrecheckLane(measurement, case / 'loop', Mock(side_effect=AssertionError('real tool')),
                            context_factory=lambda out: ctx, seams=seams)
        result = lane.run(SimpleNamespace(session_id='s', packs=('alpha',)), str(case / 'plan.json'))
        self.assertEqual(result.would_refuse, ())
        self.assertEqual(result.certain_exclusion, ())
        self.assertIn('precheck.acceptance_unavailable', result.predicted_flags)
        record = json.loads(next((case / 'loop/staging/s/precheck').rglob('precheck.json')).read_text())
        # The production pre-check reaps registered orphans (design 3.3); the
        # fake census has none, and the fake kill would fail the test if called.
        self.assertEqual(record['readings']['orphans_killed'], {'rows': [], 'error': None})

    def test_resolver_binds_every_real_adapter(self):
        from joulewise.b6.lanes import resolve, LaneMissing
        lanes = resolve(self.measurement, self.loop, run=Mock())
        self.assertIsInstance(lanes.precheck, PrecheckLane)
        self.assertIsInstance(lanes.analysis, AnalysisLane)
        from joulewise.b6.driver_lane import DriverLane
        from joulewise.b6.desk_lane import DeskLane
        self.assertIsInstance(lanes.driver, DriverLane)
        self.assertIsInstance(lanes.desk, DeskLane)

    def test_round_runner_rejects_absolute_host_tools_before_spawning(self):
        from tests.b6.round_support import Round
        from unittest.mock import patch
        fixture = object.__new__(Round)
        fixture.calls = []
        fixture.launchctl = self.root / 'fake/launchctl'
        for tool in ('ioreg', 'pmset', 'sntp', 'launchctl', 'powermetrics'):
            with self.subTest(tool=tool), patch('subprocess.run', side_effect=AssertionError('spawn reached')) as spawn:
                with self.assertRaisesRegex(AssertionError, 'unexpected round subprocess'):
                    fixture.run(['/usr/bin/' + tool])
                spawn.assert_not_called()

    def test_preparation_inputs_share_the_sealed_thresholds_and_registered_sizing(self):
        for relative in ('configs/campaigns/v5_claim_25g83/registration_block5.md',
                         'configs/b6/registration/sizing_b5.json'):
            target = self.measurement / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        paths = session_paths.for_session(self.measurement, self.loop, 'r1-alpha')
        identities = {name: {'path': str(self.root / name), 'sha256': 'a' * 64}
                      for name in ('identity-epoch.json', 't1-bindings.json')}
        inputs = plan_inputs.build(self.measurement, self.measurement / 'configs/b6/registration',
            PACKS['alpha'], 'r1-alpha', identities, custody_root=paths.custody, runs_parent=paths.runs_parent,
            claim_backup=paths.backup_claim, bound_backup=paths.backup_bound, head='a' * 40)
        self.assertNotIn('t0_epoch_s', inputs)
        self.assertEqual(inputs['thresholds']['contention']['clean_s'], 180)
        self.assertEqual(inputs['programmed_span_s']['source']['path'], 'configs/b6/registration/sizing_b5.json')

    def test_capabilities_are_conservative_and_precision_is_unknown(self):
        caps = HarvestLane().capabilities()
        self.assertFalse(caps.pack_scoped_flags)
        self.assertTrue(caps.hidden_offsets)
        self.assertFalse(caps.block_id_strata)
        self.assertIsNone(AnalysisLane().precision_reached('alpha', object(), ['s']))

    def test_fixed_compose_and_machine_smoke_read_one_keep_map(self):
        regs = registrations()
        for pack, campaign in PACKS.items():
            layout = compose.layout(Selection((pack,), 1), regs, ROOT)
            self.assertEqual(layout.campaign_id, campaign)
            self.assertEqual(compose.smoke_keep(layout), compose.registered_smoke_keep(campaign))

    def test_waker_binds_record_path_without_starting_a_job(self):
        run = Mock(return_value=SimpleNamespace(returncode=0))
        waker = Waker(self.loop, wake_argv=['/synthetic/wake', str(self.loop), '{wake_record}'], run=run)
        waker.wake('reason', {})
        plist = plistlib.loads(next((self.loop / 'wake').glob('*.plist')).read_bytes())
        self.assertEqual(plist['ProgramArguments'][-1], str(self.loop / 'wake/000001.json'))
        self.assertEqual(run.call_count, 1)

    def test_wake_placeholder_refuses_before_any_activation(self):
        script = self.root / 'wake-repo/scripts/b6_wake.zsh'
        script.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / 'scripts/b6_wake.zsh', script)
        brief = script.parent.parent / 'docs/process/b6_wake_brief.md'
        brief.parent.mkdir(parents=True)
        brief.write_text('B6_WAKE_BRIEF_PLACEHOLDER\n')
        result = subprocess.run(['/bin/zsh', str(script),
                                 str(self.loop), str(self.root / 'wake.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 3)
        self.assertIn('placeholder', result.stderr)

    def test_program_courier_records_arguments_and_stdin_locally(self):
        custody = self.root / 'session/custody'
        prompt = f'Custody root: {custody}; plan: synthetic.\n'
        result = subprocess.run(['/bin/sh', str(ROOT / 'scripts/b6_courier.sh'), '-p', prompt],
                                input=b'synthetic stdin', capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(next((custody.parent / 'courier-program').glob('*.json')).read_text())
        self.assertFalse(record['mail_sent'])
        self.assertEqual(record['argv'], ['-p', prompt])
        self.assertEqual((custody.parent / 'courier-program' / record['stdin']).read_bytes(), b'synthetic stdin')
        self.assertTrue((custody / 'night/courier.sent').exists())

class DriverStatusTests(DeskCase):
    def setUp(self):
        super().setUp()
        from joulewise.b6.driver_lane import DriverLane, metadata_path, write
        from joulewise.b6.lanes import Prepared
        self.prepared = Prepared('test-session', str(self.root / 'session/custody/night_plan.json'),
                                 str(self.root / 'session/custody/night/result.json'), 18000)
        self.meta = metadata_path(self.prepared)
        self.metadata = {'prepared': vars(self.prepared), 'paths': {'measurement': str(self.root / 'measurement'),
            'staging': str(self.root / 'staging'), 'custody': str(self.root / 'session/custody')},
            'inputs': {}, 'smoke': None}
        write(self.meta, self.metadata)
        self.calls = []
        def run(argv, **kwargs):
            self.calls.append(argv)
            if argv[0] == '/synthetic/launchctl':
                label = argv[-1].rsplit('/', 1)[-1]
                import os
                return SimpleNamespace(returncode=113, stdout='', stderr=
                    f'Could not find service "{label}" in domain for user gui: {os.getuid()}')
            return SimpleNamespace(returncode=0, stdout='', stderr='')
        self.driver = DriverLane(self.root / 'measurement', self.root / 'loop', run,
                                 launchctl_bin='/synthetic/launchctl')

    def test_terminal_uninstalls_once_and_uses_program_courier(self):
        from joulewise.b6.driver_lane import write
        from joulewise.b6.lanes import Done, Running
        night = Path(self.prepared.terminal_path).parent
        write(night / 'result.json', {'verdict': 'GO', 'chain_exit_code': 0})
        for _ in range(2):
            self.assertEqual(self.driver.status(Running(str(self.meta))), Done())
        installs = [argv for argv in self.calls if '--uninstall' in argv]
        self.assertEqual(len(installs), 1)
        self.assertIn('--courier-bin', installs[0])
        self.assertIn('--launchctl-bin', installs[0])

    def test_refusal_is_physics_only_and_lost_job_is_done(self):
        from joulewise.b6.driver_lane import write
        from joulewise.b6.lanes import Done, Refused, Running
        night = Path(self.prepared.terminal_path).parent
        write(night / 'result.json', {'verdict': 'REFUSED', 'aborted_reason': 'night_refused_hazard'})
        write(night / 'hazard_result.json', {'arm': {'go': False, 'verdicts': {'thermal': 'REFUSE'}}})
        handle = Running(str(self.meta))
        self.assertEqual(self.driver.status(handle), Refused(('thermal',)))
        write(night / 'hazard_result.json', {'arm': {'go': False, 'verdicts': {'thermal': 'UNMEASURED'}}})
        self.assertEqual(self.driver.status(handle), Done(1, None))
        Path(self.prepared.terminal_path).unlink()
        self.assertEqual(self.driver.status(handle), Done(1, None))

    def test_existing_plan_is_a_no_second_install_key(self):
        from joulewise.b6.driver_lane import write
        from joulewise.b6.lanes import Running
        path = Path(self.prepared.plan_path)
        path.parent.mkdir()
        write(path, {'t0_epoch_s': 1800000480})
        write(self.meta, {**self.metadata, 'install_rc': 0})
        for _ in range(2):
            self.assertEqual(self.driver.launch(self.prepared), Running(str(self.meta)))
        self.assertEqual(self.calls, [])

    def test_plan_without_a_completed_install_installs_once_or_stops_after_t0(self):
        # A crash between the plan write and the install, or a failed install,
        # must not be read as a launched session (which status would then
        # report as lost and the desk as a structural crash).
        from joulewise.b6.driver_lane import read, write
        from joulewise.b6.lanes import Running
        path = Path(self.prepared.plan_path)
        path.parent.mkdir()
        write(path, {'t0_epoch_s': 1800000480})
        Path(self.metadata['paths']['staging']).mkdir()
        self.driver.clock = lambda: 1800000480 - 301
        self.assertEqual(self.driver.launch(self.prepared), Running(str(self.meta)))
        self.assertEqual(len([argv for argv in self.calls if argv[0].endswith('install_night_agent.sh')]), 1)
        self.assertEqual(read(self.meta)['install_rc'], 0)
        self.driver.launch(self.prepared)
        self.assertEqual(len([argv for argv in self.calls if argv[0].endswith('install_night_agent.sh')]), 1)
        write(self.meta, self.metadata)
        self.driver.clock = lambda: 1800000480 - 299
        with self.assertRaisesRegex(RuntimeError, 'never installed'):
            self.driver.launch(self.prepared)

    def test_t0_is_bound_at_launch_with_installer_margin(self):
        from joulewise.b6.driver_lane import read, write
        from joulewise.b6.lanes import Running
        from unittest.mock import patch
        self.metadata['inputs'] = {'measurement_root': str(self.root / 'measurement')}
        write(self.meta, self.metadata)
        self.driver.clock = lambda: 1800000001
        self.driver.config = {'launch_lead_s': 420}
        def writer(inputs, **kwargs):
            self.assertEqual(inputs['t0_epoch_s'], 1800000480)
            self.assertEqual(inputs['measurement_head'], 'a' * 40)
            return {'window_max_s': self.prepared.max_s, 'runs_roots': {'claim': '/synthetic/runs'}}
        Path(self.metadata['paths']['staging']).mkdir()
        with patch('joulewise.b6.driver_lane.smoke_module._git', return_value='a' * 40), \
             patch('joulewise.b6.driver_lane.plan.write_window_plan', side_effect=writer):
            self.assertIsInstance(self.driver.launch(self.prepared), Running)
        self.assertEqual(read(self.meta)['inputs']['t0_epoch_s'], 1800000480)
        self.assertTrue(read(self.meta)['install_attempted'])


class ReviewRegressionTests(DeskCase):
    """Defects the executing review reproduced (stage 2, DISPOSITIONS-adapters.md)."""

    def driver(self, name, stdout):
        from joulewise.b6.driver_lane import DriverLane, metadata_path, write
        from joulewise.b6.lanes import Prepared
        root = self.root / name
        prepared = Prepared(name, str(root / 'session/custody/night_plan.json'),
                            str(root / 'session/custody/night/result.json'), 18000)
        write(metadata_path(prepared), {'prepared': vars(prepared), 'inputs': {}, 'smoke': None,
              'paths': {'measurement': str(root / 'm'), 'staging': str(root / 'staging'),
                        'custody': str(root / 'session/custody')}})
        run = lambda argv, **kwargs: SimpleNamespace(returncode=0, stdout=stdout, stderr='')
        return prepared, DriverLane(root / 'm', root / 'loop', run, launchctl_bin='/synthetic/launchctl',
                                    group_alive=lambda pgid: False)

    def test_arm_census_and_blocking_unmeasured_instrument_are_physics_refusals(self):
        from joulewise.b6.driver_lane import metadata_path, write
        from joulewise.b6.lanes import Done, Refused, Running
        passing = dict.fromkeys(('clock', 'battery', 'thermal', 'contention', 'disk', 'instrument'), 'PASS')
        for name, arm, expected in (
                ('census', {'go': False, 'verdicts': passing,
                            'reasons': ['agent census exit 0; agent process present: 1 x']}, 'agent'),
                ('instrument', {'go': False, 'verdicts': {**passing, 'instrument': 'UNMEASURED'}}, 'instrument')):
            prepared, driver = self.driver(name, '')
            night = Path(prepared.terminal_path).parent
            write(night / 'result.json', {'verdict': 'REFUSED', 'aborted_reason': 'night_refused_hazard'})
            write(night / 'hazard_result.json', {'verdict': 'REFUSED', 'stage_reached': 'arm', 'arm': arm})
            self.assertEqual(driver.status(Running(str(metadata_path(prepared)))), Refused((expected,)))
            write(night / 'chain.started', {'pgid': 999999})
            self.assertEqual(driver.status(Running(str(metadata_path(prepared)))), Refused((expected,)))
            (night / 'chain-stages.jsonl').write_text('{"stage_id":"reservation","kind":"bracket_reservation","rc":0}\n')
            write(night / 'result.json', {'verdict': 'ABORTED', 'aborted_reason': 'night_aborted_agent_present',
                                         'chain_exit_code': -15})
            self.assertEqual(driver.status(Running(str(metadata_path(prepared)))), Done(-15, 'agent'))

    def test_loaded_calendar_job_whose_run_ended_without_terminal_is_lost(self):
        from joulewise.b6.driver_lane import metadata_path, read
        from joulewise.b6.lanes import Done, Running
        prepared, driver = self.driver('ended', 'state = not running\nruns = 1\nlast exit code = 1\n')
        handle = Running(str(metadata_path(prepared)))
        self.assertEqual(driver.status(handle), Done(1, None))
        self.assertTrue(read(metadata_path(prepared))['lost'])
        prepared, driver = self.driver('waiting', 'state = not running\nruns = 0\n')
        self.assertEqual(driver.status(Running(str(metadata_path(prepared)))), Running(str(metadata_path(prepared))))
        prepared, driver = self.driver('orphaned', 'state = not running\nruns = 1\n')
        driver.group_alive = lambda pgid: True
        self.assertIsInstance(driver.status(Running(str(metadata_path(prepared)))), Running)

    def test_k1_holds_on_acceptance_structure_filters_codes_and_faults_unexpected_exits(self):
        from dataclasses import asdict
        from unittest.mock import patch
        from joulewise.b6.desk_lane import DeskLane
        from joulewise.b6.driver_lane import metadata_path, write
        from joulewise.b6.lanes import Done, Prepared
        from joulewise.b6 import queue
        from joulewise.flags.catalog import load_catalog
        root = self.root / 'desk'
        measurement = root / 'measurement'
        for relative in ('configs/b6/flag_catalog_b6.json', 'configs/b6/packs/alpha/registration.json'):
            (measurement / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, measurement / relative)
        prepared = Prepared('desk', str(root / 'custody/night_plan.json'), str(root / 'custody/night/result.json'), 1)
        paths = {key: root / key for key in ('archive', 'export', 'staging', 'custody')}
        paths['measurement'] = measurement
        paths['staging'].mkdir(parents=True)
        write(metadata_path(prepared), {'prepared': asdict(prepared), 'packs': ['alpha'], 'runs_roots': [],
              'paths': {k: str(v) for k, v in paths.items()}, 'inputs': {'bracket_session_id': 'b'}})
        catalog = load_catalog(ROOT / 'configs/b6/flag_catalog_b6.json')
        restricted = next(code for code in catalog.codes if catalog.entry(code)['blinding'] == 'RESTRICTED')
        archive, custody = paths['archive'], paths['custody']
        write(archive / 'harvest.json', {'verdict': 'COLLECTED'})
        write(archive / 'derived/yield.json', {'per_roster_stage': []})
        write(archive / 'derived/roster.json', {'members': []})
        write(archive / 'derived/exclusions.json', {'members_excluded': []})
        # A restricted code recorded with the default STRUCTURE blinding.
        (archive / 'derived/flags.jsonl').write_text(json.dumps(
            {'code': restricted, 'blinding': 'STRUCTURE', 'scope': {'level': 'window'}}) + '\n')
        write(archive / 'derived/b6-acceptance.json', {'structural_failures': ['structure.missing_stage_bundles'],
                                                       'flag_counts': {restricted: 1}})
        write(custody / 'night/result.json', {'verdict': 'GO', 'chain_exit_code': 0})
        write(custody / 'night/chain.exited', {'exit_code': 0})
        (custody / 'night/chain-stages.jsonl').write_text('')
        for rc, ok in ((0, False), (1, None)):
            desk = DeskLane(measurement, root / 'loop', lambda *a, **k: SimpleNamespace(returncode=rc, stdout='', stderr=''))
            with patch.object(desk, '_advance', return_value=[]), \
                 patch('joulewise.b6.desk_lane.desk_compress.compress', return_value=(4, {})):
                line = desk.session_desk(prepared, Done())
            self.assertNotIn(restricted, line.window_flags)
            if rc == 0:
                self.assertFalse(line.structure_ok)
                self.assertIn('structure.missing_stage_bundles', line.structure_defects)
            else:
                self.assertEqual(line.harvest_rc, 3)
                self.assertEqual(queue.outcome(registrations()['alpha'], line, catalog)['status'], 'pending_harvest')
