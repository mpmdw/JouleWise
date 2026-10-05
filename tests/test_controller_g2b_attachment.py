"""REAL block-3 calibration bytes; synthetic launch/ledger and mock workload.

The launch-chain and session-status authenticators, manifest hashes, battery
reader and stored-physics replay all execute. The reused launch fixture stubs
ARM/T-0 issuance, pack inspection and boot identity; this is desk evidence,
not a live G2-b validation. Captures are decompressed only into test scratch.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from joulewise import adapters, arm_readiness, battery_float, calibration_ledger as ledger, controller
from joulewise.calibration_bracketing import REVISION_FIVE_EPOCH
from joulewise.clock import FakeClock
from joulewise.schemas import BenchmarkConfig, CampaignPolicy, RunStatus
from tests import test_arm_readiness as launch_fixture

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/controller_g2b/block3-pre'


class G2bAttachmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.launch = launch_fixture.LaunchConsumptionV2Tests()
        self.addCleanup(self.launch.doCleanups)
        self.launch._set_up_fixture(self.root)
        self.runs = Path(self.launch.arm['arm_context']['claim_runs_root'])
        self.bound_runs = Path(self.launch.arm['arm_context']['bound_runs_root'])
        self.evidence = json.loads(gzip.decompress((FIXTURE / 'instrument_evidence.json.gz').read_bytes()))
        self.session_id = self.evidence['battery_float']['pre']['session_id']
        self.attempt_id = self.evidence['validation_id']
        self.capture = self.runs / 'instrument_validation' / self.attempt_id
        provenance = json.loads((FIXTURE / 'provenance.json').read_bytes())
        for name, descriptor in provenance['files'].items():
            raw = gzip.decompress((FIXTURE / (name + '.gz')).read_bytes())
            self.assertEqual(hashlib.sha256(raw).hexdigest(), descriptor['sha256'])
            target = self.capture / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        self.config = BenchmarkConfig.from_mapping(json.loads((ROOT / 'configs/examples/mock_local.json').read_bytes()))
        config_value = self.config.to_dict()
        config_value['run_id'] = 'g2b-fixture-member'
        config_value['run_metadata']['tags'].append('launch_lineage_required')
        self.config = BenchmarkConfig.from_mapping(config_value)
        self.config_path = self.launch.pack / 'member.json'
        self.config_path.write_text(json.dumps(self.config.to_dict()) + '\n')
        # Both controls are sealed pack bytes: only the ordinary member and
        # the untagged member are registered in the authenticated inventory.
        self.unregistered_path = self.launch.pack / 'unregistered.json'
        self.unregistered_path.write_bytes(self.config_path.read_bytes())
        plain_config = replace(self.config, run_id='plain-registered-member',
            run_metadata=replace(self.config.run_metadata, tags=()))
        self.plain_config_path = self.launch.pack / 'plain.json'
        self.plain_config_path.write_text(json.dumps(plain_config.to_dict()) + '\n')
        self.plan_path = self.launch.pack / 'calibration_plan.json'
        self.plan_path.write_text(json.dumps({'plan_id': self.launch.arm['pack']['plan_id']}) + '\n')
        self.plan_sha = hashlib.sha256(self.plan_path.read_bytes()).hexdigest()
        tree = {'plan': {'path': 'calibration_plan.json', 'plan_id': self.launch.arm['pack']['plan_id'],
                         'actual_sha256': self.plan_sha},
                'arm_attachments': {'identity_pin_projection': {'identity_units': [{
                    'config_inventory': [
                        {'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                        for path in (self.config_path, self.plain_config_path)]}]}}}
        tree_raw = arm_readiness.render_json(tree)
        (self.launch.pack / 'plan_tree.json').write_bytes(tree_raw)
        (self.launch.pack / 'plan_tree.sha256').write_bytes(arm_readiness.gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), 'plan_tree.json'))
        self.ledger = self.root / 'runs/calibration_observation_ledger.jsonl'
        self.pin = self.root / 'configs/calibration/calibration_ledger_head.json'
        self.pin.parent.mkdir(parents=True)
        self.pin.write_text(json.dumps({'sequence': 0, 'head_digest': ledger.GENESIS_DIGEST, 'ledger_schema': ledger.LEDGER_SCHEMA}) + '\n')
        for args in (('add', self.launch.pack.name, 'configs'),
                     ('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false', 'commit', '-qm', 'synthetic G2-b reservation inputs')):
            subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)
        self.launch.arm['pack']['pack_sha256'] = arm_readiness.committed_pack_tree_sha256(self.launch.pack)
        self.launch.arm['arm_context']['bracket_session_id'] = self.session_id
        self.launch.arm['arm_context']['pre_attempt_id'] = self.attempt_id
        self.launch._install_attested_launch_recipe()
        self.launch._settle()
        # Match only the synthetic reviewed-head boundary used by this existing
        # launch fixture. Neither lineage nor session authentication is mocked.
        self.head_patch = patch.object(arm_readiness, '_git_text', return_value=self.launch.arm['reviewed_main']['head_commit'])
        self.head_patch.start()
        self.addCleanup(self.head_patch.stop)
        self.open_session()
        self.env_patch = patch.dict(os.environ, {}, clear=True)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def open_session(self, *, finalize=True, session_id=None, kind=ledger.SESSION_KIND_BRACKET):
        sid = session_id or self.session_id
        ledger.append_bracket_session_receipt(self.ledger, head_pin_path=self.pin, repo_root=self.root,
            session_id=sid, window_id=self.launch.arm['pack']['window_id'], plan_id=self.launch.arm['pack']['plan_id'],
            plan_sha256=self.plan_sha, evidence_root_id='synthetic-g2b-evidence', runs_root=self.runs,
            session_kind=kind, declared_slots=('pre', 'post') if kind == ledger.SESSION_KIND_DERIVATION else None,
            slots={slot: {'attempt_id': self.attempt_id if slot == 'pre' else 'fixture-post',
                'custody_locator': str(self.capture if slot == 'pre' else self.runs / 'instrument_validation/fixture-post'),
                'identity_epoch': REVISION_FIVE_EPOCH, 't1_bindings': self.evidence['bindings']}
                for slot in ('pre', 'post')})
        if finalize:
            ledger.claim_bracket_session_slot(self.ledger, session_id=sid, slot='pre', attempt_id=self.attempt_id)
            ledger.finalize_bracket_session_slot(self.ledger, session_id=sid, slot='pre', disposition='valid',
                custody_locator=str(self.capture), artifact_sha256=ledger.artifact_hashes(self.capture),
                identity_epoch=REVISION_FIVE_EPOCH, t1_bindings=self.evidence['bindings'],
                capture_wall_time_s=str(self.evidence['capture_wall_time_s']), exact_bound_lexeme_s=str(self.evidence['b_fiducial_s']))

    def run_member(self, *, root=None, capture=None):
        digest = self.evidence['bindings']['powermetrics_sha256']
        class MockWorkloadRegistry:
            def resolve_runtime(inner, config, clock):
                return adapters.resolve_runtime(config, clock)
            def resolve_transport(inner, config):
                return adapters.resolve_transport(config)
            def resolve_telemetry(inner, config, clock):
                telemetry, failure = adapters.resolve_telemetry(config, clock)
                telemetry.device_metadata = lambda config, context=None: {'rail_manifest': ['mock'], 'powermetrics': {'executable_sha256': digest}}
                return telemetry, failure
        policy = CampaignPolicy.from_mapping(json.loads((ROOT / 'configs/campaign_policies/quiet_mac_exploratory.json').read_bytes()))
        # The workload/sampler are mock: this desk test exercises attachment
        # authentication, without pretending to observe a live display gate.
        policy = replace(policy, idle_admission=replace(policy.idle_admission, enabled=False))
        with patch.object(sys, 'argv', ['joulewise', 'run', str(self.config_path)]):
            return controller.run_benchmark(self.config, root or self.runs, FakeClock(start=1700000000),
                registry=MockWorkloadRegistry(), environment_snapshot=None, campaign_policy=policy,
                campaign_environment_preflight={'snapshot': {'power_source': 'AC Power',
                    'power': {'external_connected': True}, 'low_power_mode': False}},
                instrument_calibration_dir=capture or self.capture, instrument_power_policy='ac_high_power')

    def test_real_revision_five_capture_runs_and_remains_independently_readable(self):
        path, summary = self.run_member()
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        bundle_metadata = json.loads((path / 'metadata.json').read_bytes())
        metadata = bundle_metadata['instrument_calibration']
        self.assertEqual(bundle_metadata['extra']['launch_lineage']['bracket_session_id'], self.session_id)
        self.assertEqual(bundle_metadata['extra']['launch_lineage_locator_sha256'],
            metadata['g2b_pre_slot']['launch_lineage_locator_sha256'])
        self.assertEqual(metadata['g2b_pre_slot']['session_id'], self.session_id)
        self.assertEqual(metadata['g2b_pre_slot']['plan_sha256'], self.plan_sha)
        self.assertNotIn('g2a_pre_bracket', metadata)
        for file in self.capture.rglob('*'):
            if file.is_file():
                self.assertEqual((path / 'instrument_calibration' / file.relative_to(self.capture)).read_bytes(), file.read_bytes())
        self.assertEqual(battery_float.authenticate_capture(path / 'instrument_calibration').status, 'pass')
        self.assertGreater(metadata['verified_effective_b_fiducial_s'], 0)

    def test_bound_root_uses_same_authenticated_claim_pre_slot(self):
        path, summary = self.run_member(root=self.bound_runs)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertEqual(json.loads((path / 'metadata.json').read_bytes())['instrument_calibration']['g2b_pre_slot']['session_id'], self.session_id)

    def test_foreign_session_refused_before_bundle_creation(self):
        self.ledger.unlink()
        self.open_session(session_id='foreign-session')
        with self.assertRaises(ledger.CalibrationLedgerError):
            self.run_member()
        self.assertFalse((self.runs / self.config.run_id).exists())

    def test_unfinalized_pre_refused(self):
        self.ledger.unlink()
        self.open_session(finalize=False)
        with self.assertRaisesRegex(ValueError, 'finalized pre slot'):
            self.run_member()

    def test_post_directory_refused_even_with_identical_real_bytes(self):
        post = self.runs / 'instrument_validation/fixture-post'
        shutil.copytree(self.capture, post)
        with self.assertRaisesRegex(ValueError, 'finalized pre slot'):
            self.run_member(capture=post)

    def test_finalized_post_slot_refused(self):
        # Synthetic post identity on copied REAL pre physics. This is only a
        # forbidden-slot control; it is never presented as a live post capture.
        post = self.runs / 'instrument_validation/fixture-post'
        shutil.copytree(self.capture, post)
        evidence = json.loads((post / 'instrument_evidence.json').read_bytes())
        evidence['validation_id'] = 'fixture-post'
        for record in evidence['battery_float'].values():
            record.update(slot='post', attempt_id='fixture-post')
        (post / 'instrument_evidence.json').write_text(json.dumps(evidence) + '\n')
        manifest = json.loads((post / 'manifest.json').read_bytes())
        manifest['validation_id'] = 'fixture-post'
        manifest['artifacts']['instrument_evidence.json'] = hashlib.sha256((post / 'instrument_evidence.json').read_bytes()).hexdigest()
        (post / 'manifest.json').write_text(json.dumps(manifest) + '\n')
        ledger.claim_bracket_session_slot(self.ledger, session_id=self.session_id, slot='post', attempt_id='fixture-post')
        ledger.finalize_bracket_session_slot(self.ledger, session_id=self.session_id, slot='post', disposition='valid',
            custody_locator=str(post), artifact_sha256=ledger.artifact_hashes(post),
            identity_epoch=REVISION_FIVE_EPOCH, t1_bindings=evidence['bindings'],
            capture_wall_time_s=str(evidence['capture_wall_time_s']), exact_bound_lexeme_s=str(evidence['b_fiducial_s']))
        with self.assertRaisesRegex(ValueError, 'finalized pre slot'):
            self.run_member(capture=post)

    def test_no_lineage_retains_revision_five_refusal(self):
        (self.runs / arm_readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME).unlink()
        with self.assertRaisesRegex(ValueError, 'revision_five'):
            self.run_member()

    def test_plain_unregistered_member_retains_revision_five_refusal(self):
        self.config = replace(self.config, run_id='plain-unregistered-review-member',
            run_metadata=replace(self.config.run_metadata, tags=()))
        with self.assertRaisesRegex(ValueError, 'revision_five'):
            self.run_member()
        self.assertFalse((self.runs / self.config.run_id).exists())

    def test_tagged_unregistered_member_retains_revision_five_refusal(self):
        self.config_path = self.unregistered_path
        with self.assertRaisesRegex(ValueError, 'revision_five'):
            self.run_member()
        self.assertFalse((self.runs / self.config.run_id).exists())

    def test_authenticated_untagged_member_retains_revision_five_refusal(self):
        self.config_path = self.plain_config_path
        self.config = BenchmarkConfig.from_mapping(json.loads(self.config_path.read_bytes()))
        context = arm_readiness.authenticate_campaign_launch_lineage(
            self.runs, config_paths=(self.config_path,))
        self.assertIn(self.config_path.name, context['config_inventory'])
        with self.assertRaisesRegex(ValueError, 'revision_five'):
            self.run_member()
        self.assertFalse((self.runs / self.config.run_id).exists())

    def test_running_config_must_match_authenticated_source(self):
        self.config = replace(self.config, run_id='changed-running-member')
        with self.assertRaisesRegex(ValueError, 'revision_five'):
            self.run_member()
        self.assertFalse((self.runs / self.config.run_id).exists())

    def test_reserved_directory_symlink_is_refused(self):
        relocated = self.capture.with_name('relocated')
        self.capture.rename(relocated)
        self.capture.symlink_to(relocated, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'finalized pre slot'):
            self.run_member()

    def test_corrupt_lineage_has_no_g2a_fallback(self):
        (self.runs / arm_readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME).write_bytes(b'{}\n')
        with patch.dict(os.environ, {'JOULEWISE_G2A_PRE_BRACKET_PLAN': 'unused'}):
            with self.assertRaises(arm_readiness.LaunchLineageError):
                self.run_member()

    def test_byte_identical_foreign_custody_refused(self):
        other = self.runs / 'instrument_validation/foreign-copy'
        shutil.copytree(self.capture, other)
        with self.assertRaisesRegex(ValueError, 'finalized pre slot'):
            self.run_member(capture=other)

    def test_derivation_session_cannot_use_lineage_route(self):
        self.ledger.unlink()
        self.open_session(kind=ledger.SESSION_KIND_DERIVATION)
        with self.assertRaisesRegex(ValueError, 'finalized pre slot'):
            self.run_member()


if __name__ == '__main__':
    unittest.main()
