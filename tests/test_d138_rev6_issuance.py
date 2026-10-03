"""D-138 issued-byte authentication and desk identity counterfactuals.

Reads the retained ledger chain without replaying custody or taking a capture;
these checks establish default selection/freshness, not live hardware validation.
"""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise import calibration_bracketing as bracket
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
from joulewise.schemas import CalibrationBracketingPolicy
from scripts import issue_calibration_acceptance_generation as issuer


class D138RevisionSixIssuanceTests(unittest.TestCase):
    def setUp(self):
        self.path = bracket.EPOCH_25G83_R2_ACCEPTANCE_BOUND_PATH
        self.raw = self.path.read_bytes()
        self.issued = json.loads(self.raw)

    def assert_default_restored(self):
        loaded = bracket.load_calibration_acceptance_bound()
        self.assertEqual(loaded, self.issued)
        self.assertTrue(bracket._valid_acceptance_bound(loaded))
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(),
                         bracket.EPOCH_25G83_R2_ACCEPTANCE_BOUND_SHA256)

    def test_default_loads_issued_rev6_and_literal_generation_matches(self):
        self.assertEqual(bracket.ACTIVE_ACCEPTANCE_ID, 'd079_calibration_acceptance_v2_n24_25g83_r2')
        self.assertEqual(bracket.DEFAULT_ACCEPTANCE_BOUND_PATH, self.path)
        self.assert_default_restored()
        self.assertEqual(bracket._D102_GENERATION_DERIVATIONS[bracket.ACTIVE_ACCEPTANCE_ID],
            issuer.generation_row_for_registry(self.issued['registered_generation_row']))
        print('W4 DEFAULT=PASS issued_rev6=True valid=True generation_row_equal=True')

    def test_25g83_fresh_25f84_stale_and_explicit_p8_valid(self):
        cutoff = self.issued['ledger_cutoff']
        packet = Path(__file__).resolve().parents[1] / 'docs/process_traces/rev6-derivation-block1/packet/3-chain-logs-and-harvest'
        snapshot = load_calibration_ledger_snapshot(
            packet / 'calibration_observation_ledger.jsonl', packet / 'calibration_ledger_head.json',
            require_committed_pin=False, baseline_sequence=cutoff['sequence'], baseline_digest=cutoff['head_digest'],
            verify_custody=False,
        )
        self.assertEqual(snapshot.refusal_reasons, ())
        for build, expected in (('25G83', 'fresh'), ('25F84', 'stale')):
            identity = {**self.issued['identity_epoch'], 'os_build': build}
            result, reasons = bracket.evaluate_calibration_bracket(
                [], window_start_s=100.0, window_end_s=110.0, bindings=identity,
                policy=CalibrationBracketingPolicy(require_bracket=True, calibration_bracket_max_drift_s=0.02), ledger_snapshot=snapshot,
            )
            self.assertEqual(result['acceptance']['artifact']['acceptance_id'], bracket.ACTIVE_ACCEPTANCE_ID)
            self.assertEqual(result['acceptance']['freshness']['status'], expected)
            if expected == 'fresh':
                self.assertEqual(result['acceptance']['freshness']['stale_fields'], [])
                self.assertNotIn('calibration_acceptance_bound_stale', reasons)
            else:
                self.assertEqual(result['acceptance']['freshness']['stale_fields'], ['os_build'])
                self.assertIn('calibration_acceptance_bound_stale', reasons)
        p8 = bracket.load_calibration_acceptance_bound(bracket.ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH)
        self.assertIsNotNone(p8)
        self.assertEqual(p8['identity_epoch']['os_build'], '25F84')
        self.assertTrue(bracket._valid_acceptance_bound(p8))
        self.assertEqual(hashlib.sha256(bracket.ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH.read_bytes()).hexdigest(),
                         bracket.ANCHOR_V3_R8_ACCEPTANCE_BOUND_SHA256)
        print('W4 IDENTITY=PASS 25G83=fresh 25F84=stale explicit_P8=valid')

    def test_missing_generation_row_red_then_restored(self):
        retained = {key: row for key, row in bracket._D102_GENERATION_DERIVATIONS.items()
                    if key != bracket.ACTIVE_ACCEPTANCE_ID}
        with patch.object(bracket, '_D102_GENERATION_DERIVATIONS', retained):
            self.assertIsNone(bracket.load_calibration_acceptance_bound())
            self.assertFalse(bracket._valid_acceptance_bound(self.issued))
        self.assert_default_restored()
        print('W4 RED missing_generation_row: default_refused=True; RESTORED=PASS')

    def test_corrupt_one_byte_red_then_restored(self):
        # Change exactly the final newline to a space: JSON still parses, so
        # this refusal must come from the byte pin rather than the JSON parser.
        corrupted = self.raw[:-1] + b' '
        self.assertEqual(sum(a != b for a, b in zip(corrupted, self.raw)), 1)
        self.assertEqual(json.loads(corrupted), self.issued)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'corrupt.json'
            path.write_bytes(corrupted)
            self.assertIsNone(bracket.load_calibration_acceptance_bound(path))
        self.assert_default_restored()
        print('W4 RED corrupt_one_byte: copy_refused=True; RESTORED=PASS')

    def test_member_lexeme_resealed_both_digests_red_then_restored(self):
        altered = copy.deepcopy(self.issued)
        member = altered['derivation_corpus']['members'][0]
        before = member['b_fiducial_s']
        member['b_fiducial_s'] = '0.1' + before[2:]
        altered['derivation_input_sha256'] = issuer.derivation_input_sha256(altered)
        altered['derivation_sha256'] = issuer.derivation_sha256(altered)
        self.assertNotEqual(altered['derivation_input_sha256'], self.issued['derivation_input_sha256'])
        self.assertNotEqual(altered['derivation_sha256'], self.issued['derivation_sha256'])
        self.assertEqual(altered['derivation_input_sha256'], issuer.derivation_input_sha256(altered))
        self.assertEqual(altered['derivation_sha256'], issuer.derivation_sha256(altered))
        self.assertFalse(bracket._valid_acceptance_bound(altered))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'resealed.json'
            path.write_text(json.dumps(altered, indent=2) + '\n')
            self.assertIsNone(bracket.load_calibration_acceptance_bound(path))
        self.assert_default_restored()
        print('W4 RED member_lexeme_both_seals: structural_and_copy_refused=True; RESTORED=PASS')


if __name__ == '__main__':
    unittest.main()
