"""Real w1 pre-capture schema, synthetic physics and an actual governed ledger."""
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock

from joulewise import calibration_ledger as ledger, controller
from joulewise.calibration_bracketing import REVISION_FIVE_EPOCH
from joulewise.clock import FakeClock
from joulewise.powermetrics_fiducial import PROTOCOL_ID, PROTOCOL_V3_SHA256
from joulewise.schemas import BenchmarkConfig, CampaignPolicy
from tests.git_fixture import init_git_fixture
from tests.test_reduce import self_consistent_calibration

ROOT = Path(__file__).resolve().parents[1]


class G2aCalibrationAttachmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.runs = self.root / 'g2a/runs'
        self.capture = self.runs / 'instrument_validation/fixture-pre'
        (self.capture / 'raw').mkdir(parents=True)
        # The shape was copied from w1's real archived pre capture, with all
        # scalar values replaced and repeated lists reduced to one template.
        evidence = json.loads((ROOT / 'tests/fixtures/g2a/pre-bracket-instrument-evidence-shape.json').read_bytes())
        physics, raw, events = self_consistent_calibration(protocol_id=PROTOCOL_ID)
        evidence.update(physics)
        self.bindings = dict(REVISION_FIVE_EPOCH, powermetrics_sha256='a' * 64,
            anchor_method_version=evidence['anchor_method_version'], mlx_version='0.31.2',
            protocol_sha256=PROTOCOL_V3_SHA256)
        evidence.update(validation_id='fixture-pre', bindings=self.bindings, status='valid')
        self.evidence = evidence
        for name, value in (('raw/powermetrics.plist', raw), ('events.jsonl', events),
                            ('power_trace.csv', b'fixture trace\n')):
            (self.capture / name).write_bytes(value)
        (self.capture / 'instrument_evidence.json').write_text(json.dumps(evidence) + '\n')
        self.hashes = {name: hashlib.sha256((self.capture / name).read_bytes()).hexdigest()
                      for name in ('raw/powermetrics.plist', 'events.jsonl', 'power_trace.csv', 'instrument_evidence.json')}
        (self.capture / 'manifest.json').write_text(json.dumps({
            'schema_version': 'joulewise.instrument_validation_manifest.v1', 'artifacts': self.hashes}) + '\n')
        self.hashes['manifest.json'] = hashlib.sha256((self.capture / 'manifest.json').read_bytes()).hexdigest()
        self.config = BenchmarkConfig.from_mapping(json.loads((ROOT / 'configs/examples/mock_local.json').read_bytes()))
        self.config_root = self.root / 'configs'
        self.config_root.mkdir()
        self.config_path = self.config_root / 'member.json'
        self.config_path.write_text(json.dumps(self.config.to_dict()) + '\n')
        self.ledger = self.root / 'ledger.jsonl'
        self.pin = self.root / 'pin.json'
        self.pin.write_text(json.dumps({'sequence': 0, 'head_digest': ledger.GENESIS_DIGEST,
                                       'ledger_schema': ledger.LEDGER_SCHEMA}) + '\n')
        init_git_fixture(self.root, '-q')
        subprocess.run(['git', 'add', 'pin.json'], cwd=self.root, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '-qm', 'fixture committed seed'], cwd=self.root, check=True, capture_output=True)
        self.plan_path = self.root / 'g2a/window-plan/calibration_plan.json'
        self.plan_path.parent.mkdir(parents=True)
        self.plan = {'schema_version': 'joulewise.g2a_probe_plan.v1', 'plan_id': 'fixture-plan',
            'session_id': 'fixture-session', 'window_id': 'fixture-window', 'evidence_root_id': 'fixture-evidence',
            'status': {'diagnostic': True, 'claim_eligible': False}, 'config_root': str(self.config_root),
            'calibration_ledger': {'path': str(self.ledger), 'head_sequence': 0, 'head_digest': ledger.GENESIS_DIGEST},
            'ledger_head_pin': {'path': str(self.pin)}, 'stages': [{'members': [{
                'run_id': self.config.run_id, 'config_path': 'member.json',
                'config_sha256': hashlib.sha256(self.config_path.read_bytes()).hexdigest()}]}]}
        self.plan_path.write_text(json.dumps(self.plan) + '\n')
        self.open_session()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(os.environ, {
            'JOULEWISE_G2A_PRE_BRACKET_PLAN': str(self.plan_path), 'JOULEWISE_NIGHT_PLAN_ID': 'fixture-window'}))
        real_load = ledger.load_calibration_ledger_snapshot
        def fixture_load(*args, **kwargs):
            kwargs['repo_root'] = self.root
            return real_load(*args, **kwargs)
        self.stack.enter_context(patch.object(ledger, 'load_calibration_ledger_snapshot', side_effect=fixture_load))

    def open_session(self, kind=ledger.SESSION_KIND_BRACKET):
        ledger.append_bracket_session_receipt(self.ledger, head_pin_path=self.pin, repo_root=self.root,
            session_id='fixture-session', window_id='fixture-window', plan_id='fixture-plan',
            plan_sha256=hashlib.sha256(self.plan_path.read_bytes()).hexdigest(),
            evidence_root_id='fixture-evidence', runs_root=self.runs, session_kind=kind,
            declared_slots=('pre', 'post') if kind == ledger.SESSION_KIND_DERIVATION else None,
            slots={slot: {'attempt_id': f'fixture-{slot}',
                'custody_locator': str(self.runs / 'instrument_validation' / f'fixture-{slot}'),
                'identity_epoch': REVISION_FIVE_EPOCH, 't1_bindings': self.bindings}
                for slot in ('pre', 'post')})
        ledger.claim_bracket_session_slot(self.ledger, session_id='fixture-session',
            slot='pre', attempt_id='fixture-pre')
        ledger.finalize_bracket_session_slot(self.ledger, session_id='fixture-session', slot='pre',
            disposition='valid', custody_locator=str(self.capture), artifact_sha256=self.hashes,
            identity_epoch=REVISION_FIVE_EPOCH, t1_bindings=self.bindings,
            capture_wall_time_s=str(self.evidence['capture_wall_time_s']),
            exact_bound_lexeme_s=str(self.evidence['b_fiducial_s']))

    def run_member(self):
        telemetry = Mock()
        telemetry.device_metadata.return_value = {'powermetrics': {'executable_sha256': 'a' * 64}}
        registry = Mock()
        registry.resolve_telemetry.return_value = (telemetry, None)
        bundle = self.runs / str(self.config.run_id)
        bundle.mkdir()
        with patch.object(controller.RunBundleWriter, 'create', return_value=SimpleNamespace(path=bundle)), \
                patch.object(controller, '_Execution') as execution:
            controller.run_benchmark(self.config, self.runs, FakeClock(), registry=registry,
                campaign_policy=CampaignPolicy.from_mapping(json.loads((ROOT / 'configs/campaign_policies/quiet_mac_p2_production.json').read_bytes())),
                campaign_environment_preflight={'snapshot': {'power_source': 'AC Power',
                    'power': {'external_connected': True}, 'low_power_mode': False}},
                instrument_calibration_dir=self.capture, instrument_power_policy='ac_high_power')
            metadata = execution.call_args.args[12]
        return bundle, metadata

    def test_registered_member_accepts_real_pre_capture_shape_through_explicit_chain_path(self):
        bundle, metadata = self.run_member()
        self.assertEqual(metadata['bindings']['os_build'], '25G83')
        self.assertEqual(metadata['g2a_pre_bracket']['session_id'], 'fixture-session')
        self.assertGreater(metadata['verified_effective_b_fiducial_s'], 0)
        attached = json.loads((bundle / 'instrument_calibration/instrument_evidence.json').read_bytes())
        self.assertIn('battery_float', attached)
        self.assertEqual(attached['pulse_count'], 59)

    def test_legacy_reader_still_refuses_real_pre_capture_shape_even_with_chain_environment(self):
        with self.assertRaisesRegex(ValueError, 'revision_five'):
            controller._load_instrument_calibration_attachment(self.capture, power_policy='ac_high_power',
                runtime_powermetrics_sha256='a' * 64, runtime_power_policy='ac_high_power')

    def test_derivation_session_cannot_use_explicit_diagnostic_path(self):
        # Build a valid governed derivation session with pre/post declared slots;
        # same epoch and evidence cannot elevate it to an ordinary endpoint.
        self.ledger.unlink()
        self.open_session(ledger.SESSION_KIND_DERIVATION)
        with self.assertRaisesRegex(ValueError, 'ordinary bracket session'):
            self.run_member()

    def test_wrong_member_config_cannot_use_explicit_diagnostic_path(self):
        self.config_path.write_text('{}\n')
        with self.assertRaisesRegex(ValueError, 'config mismatch'):
            self.run_member()

    def test_uncommitted_pin_cannot_use_explicit_diagnostic_path(self):
        self.pin.write_bytes(self.pin.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'ordinary bracket session'):
            self.run_member()
