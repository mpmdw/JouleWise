"""Block-4 consumer regressions; archived/synthetic bytes, no live Mac claims."""
from dataclasses import replace
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, battery_float, v5_qualification as q
from scripts import assemble_v5_battery_boundaries as assembler, harvest_v5_g2b_window as harvest
from scripts import run_campaign, run_night


class ConsumerTests(unittest.TestCase):
    def test_selected_ledger_reaches_both_snapshot_arguments(self):
        snapshot = SimpleNamespace(valid=False)
        with mock.patch.object(run_campaign, 'load_calibration_ledger_snapshot', return_value=snapshot) as load, \
             mock.patch.dict(os.environ, {'CALIBRATION_LEDGER': '/chosen/ledger', 'LEDGER_HEAD_PIN': '/chosen/pin'}):
            self.assertIs(run_campaign._load_calibration_snapshot_for_evaluation(), snapshot)
            self.assertEqual(load.call_args.kwargs['ledger_path'], Path('/chosen/ledger'))
            self.assertEqual(load.call_args.kwargs['head_pin_path'], Path('/chosen/pin'))
            args = run_campaign.parse_args(['--whole-window-verdict', '--calibration-ledger', '/explicit/ledger', '--head-pin', '/explicit/pin'])
            run_campaign._load_calibration_snapshot_for_evaluation(ledger_path=args.calibration_ledger, head_pin_path=args.head_pin)
            self.assertEqual(load.call_args.kwargs['ledger_path'], Path('/explicit/ledger'))
            self.assertEqual(load.call_args.kwargs['head_pin_path'], Path('/explicit/pin'))

    def test_chain_exports_native_selected_ledger_and_shared_off_path(self):
        from joulewise.arm_readiness_evidence_t0 import WINDOW_ENV_KEYS
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            chain = root / 'chain.zsh'
            chain.write_text('export V5_QUALIFICATION_OCCURRENCE=s1\n')
            values = {key: '/fixture/' + key for key in WINDOW_ENV_KEYS}
            (root / 'window.env').write_text(''.join(f'{key}={value}\n' for key, value in sorted(values.items())))
            plan = SimpleNamespace(plan_id='occurrence', measurement_root='/fixture/code', measurement_head='a'*40,
                custody_root=str(root), chain_path=str(chain), receipt_class='TRANSACTION_PACK', pack_night={'pack_id':'gamma'})
            with mock.patch.dict(os.environ, {}, clear=True):
                env = run_night._chain_environment(plan, root / 'night')
            self.assertEqual(env['CALIBRATION_LEDGER'], values['CALIBRATION_LEDGER'])
            self.assertEqual(env['LEDGER_HEAD_PIN'], values['LEDGER_HEAD_PIN'])
            self.assertEqual(env['JOULEWISE_NETWORK_TIME_OFF_RECEIPT'], str(q.off_receipt_path(plan)))

    def test_terminal_boundary_requires_exact_chain_path_and_unique_census(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            plan = SimpleNamespace(custody_root=str(root))
            expected = root / 'night/transcript/post-bracket-terminal-boundary.json'
            q.write(expected, {'fixture': 'STOP'})
            q.write(root / 'qualification-plan-record.json', {'terminal_boundary_path': str(expected)})
            q.require_terminal_boundary(plan, expected)
            wrong = root / 'elsewhere/post-bracket-terminal-boundary.json'
            q.write(wrong, {'fixture': 'STOP'})
            with self.assertRaisesRegex(q.HarvestRefusal, 'path_mismatch'):
                q.require_terminal_boundary(plan, wrong)
            with self.assertRaisesRegex(q.HarvestRefusal, 'census_invalid'):
                q.require_terminal_boundary(plan, expected)


class ArchivedBatteryTests(unittest.TestCase):
    source = Path(__file__).parent / 'fixtures/v5_qualification_harvest/block3_battery'

    def test_real_block3_glob_skips_attached_copy_and_replays_capture_pairs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / 'custody'
            shutil.copytree(self.source, root)
            # Avoid the repository-wide runs/ ignore rule in the stored fixture.
            (root / 'capture-tree').rename(root / 'runs')
            for relative, digest in q.read(root / 'SOURCE.json')['files'].items():
                self.assertEqual(q.sha(root / relative), digest)
            bound = root.parent / 'bound'; bound.mkdir()
            bundle = root / 'runs/g2a-small-p0512-r01'
            self.assertEqual(battery_float.authenticate_bundle(bundle).status, 'battery_float_evidence_missing')
            with self.assertRaises(battery_float.CustodyFailure):
                battery_float.authenticate_capture(bundle / 'instrument_calibration')
            passed, captures = harvest.battery_attempts(root, bound)
            self.assertFalse(passed)  # Block 3 predates bundle pair production.
            self.assertEqual(len(captures), 3)
            self.assertTrue(all('instrument_calibration' not in path.parts for _, path in captures))
            for _, path in captures:
                if path.parent.name == 'instrument_validation':
                    self.assertEqual(battery_float.authenticate_capture(path).status, 'pass')

    def test_real_t0_capture_retains_exact_observation_and_raw_digest(self):
        capture = self.source / 't0-receipt.json'
        observed, raw = q.captured_battery_observation(capture)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            locator = assembler.retain_t0_capture(capture, observed['plan_id'], root)
            self.assertEqual(Path(locator['raw']['path']).read_bytes(), raw)
            self.assertEqual(q.sha(Path(locator['raw']['path'])), observed['raw_stdout_sha256'])
            self.assertEqual(q.read(locator['record']['path'])['source_capture'], q.reference(capture.absolute()))
            with self.assertRaisesRegex(q.HarvestRefusal, 'identity_mismatch'):
                assembler.retain_t0_capture(capture, 'wrong-occurrence', root)

    def test_assembler_authenticates_native_phase_plan_and_raw_bytes(self):
        capture = next((self.source / 'capture-tree/instrument_validation').iterdir())
        original = q.read(capture / 'instrument_evidence.json')['battery_float']['pre']
        raw = (capture / 'raw/battery_float.pre.ioreg').read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            observations = {}
            for role, phase in q.BATTERY_BOUNDARY_PHASES.items():
                # Only probe transport/identity are a fixture. The captured
                # block-3 bytes, parser and all authenticators are real.
                record, observed = battery_float.observe(phase=phase, plan_id='occurrence',
                    wall_time_s=original['wall_time_s'], runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw, b''))
                observations[role] = q.persist_battery_observation(root, role, record, observed)
            output = root / 'boundaries.json'
            locator = assembler.assemble('occurrence', observations, output)
            self.assertTrue(q.battery_boundaries(output, locator['sha256'], 'occurrence'))
            from scripts.check_v5_arm_abort import battery_sources
            self.assertEqual(len(battery_sources(observations, SimpleNamespace(plan_id='occurrence'))), 6)
            with self.assertRaisesRegex(q.HarvestRefusal, 'identity_mismatch'):
                assembler.assemble('foreign', observations, root / 'foreign.json')
            path = Path(observations['t0']['record']['path'])
            record = q.read(path); record['phase'] = 'publish_install'
            path.write_bytes(readiness.render_json(record))
            observations['t0']['record'] = q.reference(path)
            with self.assertRaisesRegex(q.HarvestRefusal, 'identity_mismatch'):
                assembler.assemble('occurrence', observations, root / 'wrong-role.json')


class G10CustodyTests(unittest.TestCase):
    def test_real_g10_verifier_replays_retained_tree_and_refuses_support_mutation(self):
        from tests.test_t0_anchor_positive_control import PositiveControlTests
        from tests.test_t0_rehearsal import FixtureBuilder, fixture_bundle
        from joulewise import t0_rehearsal as t0
        control = PositiveControlTests(); control.setUp(); self.addCleanup(control.doCleanups)
        self.assertEqual(control.run_control()['status'], 'DISCHARGED')
        head = subprocess.check_output(['git', '-C', str(control.repository), 'rev-parse', 'HEAD'], text=True).strip()
        root = FixtureBuilder(Path(control.temporary.name).resolve() / 'qualification').build()
        plan = root / 'qualification-plan.json'; q.write(plan, {'measurement_root':str(control.repository)})
        observation = root / 'a1-observation.json'; q.write(observation, {'first_t0_boundary_monotonic_ns':10**30})
        first = root / 'a1-control.json'; q.write(first, {'observation':q.reference(observation), 'boot_session_id':control.stamp()['boot_id']})
        q.write(root / 'qualification-plan-record.json', {'head':head, 'plan':q.reference(plan), 'prerequisites':{
            'a1_control':q.reference(first), 'g10_control':q.reference(control.control / 'positive-control.json'),
            'g10_artifacts':[q.reference(control.control / 'custody-manifest.json')]}})
        shutil.copytree(control.control, root / 'records/g10-custody' / control.control.name)
        shutil.copyfile(control.control / 'positive-control.json', root / 'records/positive-control.json')
        self.assertEqual(q.g10_sources(root), {'g10-custody':control.control})
        bundle = fixture_bundle(root)
        bundle = replace(bundle, manifest=replace(bundle.manifest, value={'schema_version':'joulewise.v5_s1_qualification_bundle.v1'}))
        self.assertEqual(t0.evaluate_g10(bundle).status, t0.GateStatus.PASS)
        path = control.control / 'before.json'; path.write_bytes(path.read_bytes() + b' ')
        result = t0.evaluate_g10(bundle)
        self.assertEqual(result.status, t0.GateStatus.FAIL)
        self.assertIn('g10_custody_hash_or_census', result.message)


if __name__ == '__main__':
    unittest.main()
