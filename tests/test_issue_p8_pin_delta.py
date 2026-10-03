"""P8 transaction integrity and sampler-free preflight regressions."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise import calibration_bracketing as bracket
from joulewise.calibration_exits import RefusalCode
from joulewise.calibration_ledger import CalibrationLedgerSnapshot, LEDGER_SCHEMA
from scripts import issue_p8_pin_delta as issuer
from scripts import validate_powermetrics_fiducial as writer
from scripts.reissue_calibration_acceptance import build_member_delta_report


class P8PinDeltaTests(unittest.TestCase):
    def test_recorded_script_reproduces_issued_bytes_and_preserves_science(self):
        with redirect_stdout(io.StringIO()):
            new, delta, _ = issuer.build_p8()
        old = bracket.load_calibration_acceptance_bound(bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)
        payload = issuer.encode_pin_delta(bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH.read_bytes(), old, new)
        self.assertEqual(payload, issuer.P8_PATH.read_bytes())
        self.assertEqual(delta['verdict'], 'PROCEED')
        self.assertEqual(delta['changed_pin_count'], 1)
        for key in ('derivation_corpus', 'decimal_derivation', 'ledger_cutoff',
                    'identity_epoch', 'prior_observation_set', 'issuance'):
            self.assertEqual(new[key], old[key])
        for key, value in old['derivation_notes'].items():
            if key not in ('generation', 'predecessor', 'reissue_delta'):
                self.assertEqual(new['derivation_notes'][key], value)
        self.assertTrue(bracket._valid_acceptance_bound(new))
        # P8 by name: the D-138 Revision 6 transaction moved the live default
        # to the 25G83 n24 generation; P8 stays registered and loadable.
        self.assertEqual(bracket.load_calibration_acceptance_bound(issuer.P8_PATH), new)

    def test_member_value_change_cannot_pass_delta_or_production_validator(self):
        with redirect_stdout(io.StringIO()):
            new, _, _ = issuer.build_p8()
        old = bracket.load_calibration_acceptance_bound(bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)
        copy = deepcopy(old)
        copy['derivation_corpus']['members'][0]['b_fiducial_s'] = '0.030067931757111658'
        issuer.digest(copy)
        self.assertEqual(build_member_delta_report(old, copy)['verdict'], 'STOP')
        new['derivation_corpus']['members'][0]['b_fiducial_s'] = '0.030067931757111658'
        issuer.digest(new)
        self.assertFalse(bracket._valid_acceptance_bound(new))

    def test_changed_frozen_pin_requires_a_new_transaction(self):
        with patch.object(bracket, '_current_estimator_code_sha256', return_value={}):
            with self.assertRaisesRegex(ValueError, 'freeze/cap'):
                issuer.build_p8()

    def test_default_derivation_basis_follows_the_live_default_explicit_p8_valid_r7_stale(self):
        # Since the D-138 Revision 6 transaction the default basis is the
        # live 25G83 n24 generation; P8 named explicitly is still a valid basis.
        screen, basis = writer._derivation_only_screen_basis()
        self.assertEqual(basis['acceptance_id'], bracket.EPOCH_25G83_R2_ACCEPTANCE_ID)
        self.assertEqual(str(screen), '0.036462861644980')
        screen, basis = writer._derivation_only_screen_basis(acceptance_path=issuer.P8_PATH)
        self.assertEqual(basis['acceptance_id'], issuer.P8_ID)
        self.assertEqual(str(screen), '0.032898493715362')
        with self.assertRaises(writer._AcceptancePreflightError) as raised:
            writer._derivation_only_screen_basis(acceptance_path=bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)
        self.assertEqual(raised.exception.reason, 'acceptance_artifact_stale')

    def test_derivation_only_cli_dry_preflight_uses_default_and_refuses_r7(self):
        # Stop at the standalone-session guard, after basis authentication;
        # test mode fixes identity, and no sampler or capture is entered.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            epoch = dict(bracket.load_calibration_acceptance_bound()['identity_epoch'], os_build='25G83')
            identity = root / 'identity.json'
            identity.write_text(json.dumps(epoch))
            args = ['--allow-live', '--derivation-only', '--sampler-direct-for-test',
                    '--power-policy', epoch['power_policy'], '--identity-epoch-json-for-test',
                    str(identity), '--output-root', str(root / 'unused')]
            # Synthetic disk-custody snapshot; the basis and CLI logic remain
            # production code. This establishes no live ledger/hardware claim.
            snapshot = CalibrationLedgerSnapshot(LEDGER_SCHEMA, root / 'ledger',
                0, '0' * 64, (), (), ())
            original_popen = writer.subprocess.Popen
            def git_only_popen(argv, *a, **kw):
                if not isinstance(argv, list) or argv[0] != 'git':
                    raise AssertionError(f'non-Git process entered: {argv}')
                return original_popen(argv, *a, **kw)
            for acceptance, expected in ((issuer.P8_PATH, RefusalCode.DERIVATION_ONLY_SESSION_KIND_REQUIRED.value),
                                         (bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH, RefusalCode.FROZEN_PROTOCOL_INVALID.value)):
                with self.subTest(acceptance=acceptance.name):
                    stderr = io.StringIO()
                    with patch.object(writer, 'DEFAULT_ACCEPTANCE_BOUND_PATH', acceptance), \
                            patch.object(writer, 'load_calibration_ledger_snapshot', return_value=snapshot), \
                            patch.object(writer.subprocess, 'Popen', side_effect=git_only_popen), \
                            redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                        code = writer.main(args)
                    self.assertEqual(code, 2)
                    refusal = json.loads(stderr.getvalue().splitlines()[-1])
                    self.assertEqual(refusal['code'], expected)
                    if acceptance == bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH:
                        self.assertEqual(refusal['context']['reason'], 'acceptance_artifact_stale')
                    self.assertFalse((root / 'unused').exists())


if __name__ == '__main__':
    unittest.main()
