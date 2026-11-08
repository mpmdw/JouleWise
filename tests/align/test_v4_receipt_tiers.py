"""MED-1: strict tier = re-register on change; amendment tier = lead-signed amendment row.

Synthetic temporary Git repositories only.
"""
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.align.apple import v4_registration as registration
from tests.align import test_r11_delta_sol1 as delta

SIGNATURE = 'lead: synthetic-amendment 2026-11-08'
AMENDABLE = 'joulewise/kv_size.py'          # delta3: nothing is amendable in the real registration; the mechanism is exercised
                                            # by patching one analysis-only path into the allowlist
STRICT_EXAMPLES = ('docs/align/pilot_protocol_v4.md', 'scripts/align_v4_kit.py', 'joulewise/align/apple/endpoint.py',
                   'joulewise/align/apple/prompt_cache.py', 'scripts/run_night.py', 'scripts/launch_window.py',
                   'scripts/km003c_monitor.py', 'joulewise/external/km003c_usb.py', 'scripts/hazard_monitor.py',
                   'scripts/bytes_h_session.py', 'scripts/run_campaign.py', 'joulewise/adapters/mlx_runtime.py',
                   'scripts/night_chains/align_r1_rehearsal.zsh', 'joulewise/align/apple/v4_topup.py',
                   # strict by default (delta2): shared B5/B6 code and the calibration spine are strict too
                   'joulewise/b6/idle_wait.py', 'joulewise/b5/driver.py', 'joulewise/b6/courier.py',
                   'scripts/reserve_calibration_window_bracket.py', 'scripts/validate_powermetrics_fiducial.py',
                   'scripts/b5_window_calibration_verdict.py', 'scripts/align_r1_runtime.py',
                   'configs/align/v4/r1_runtime.json', 'joulewise/__main__.py')


def amendment(candidate, path, new_text, *, reason='infrastructure fix', signature=SIGNATURE, old=None):
    old = old or candidate.receipt['artifacts'][path]
    candidate.write(path, new_text)
    candidate.commit(f'Synthetic change to {path}')
    return {'path': path, 'old_sha256': old, 'new_sha256': candidate.digest(path),
            'reason': reason, 'lead_signature': signature}


class TierClassificationTests(unittest.TestCase):
    def test_every_bound_path_is_strict_and_the_allowlist_is_empty(self):
        # delta3 S1 F01 / S2 H1: every bound path is statically reachable (a module body runs on
        # import), so none is "absent from both the static closure and the dynamic trace".
        self.assertEqual(registration.AMENDMENT_ALLOWLIST, ())
        for path in STRICT_EXAMPLES + (AMENDABLE,):
            with self.subTest(path=path):
                self.assertIn(path, registration.ARTIFACTS)
                self.assertTrue(registration.is_strict(path))
        self.assertTrue(all(registration.is_strict(p) for p in registration.ARTIFACTS))
        self.assertFalse([p for p in registration.STRICT_SCRIPTS if p not in registration.ARTIFACTS])
        self.assertTrue(all(registration.is_strict(p) for p in registration.STRICT_SCRIPTS))

    def test_a_listed_path_would_be_the_only_amendable_one(self):
        with mock.patch.object(registration, 'AMENDMENT_ALLOWLIST', (AMENDABLE,)):
            self.assertFalse(registration.is_strict(AMENDABLE))
            amendable = [p for p in registration.ARTIFACTS if not registration.is_strict(p)]
            self.assertEqual(amendable, [AMENDABLE])


class ReceiptTierTests(unittest.TestCase):
    def setUp(self):
        # exercise the amendment mechanism on one synthetic allowlist entry
        patcher = mock.patch.object(registration, 'AMENDMENT_ALLOWLIST', (AMENDABLE,))
        patcher.start()
        self.addCleanup(patcher.stop)

    def candidate(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        return delta.TemporaryCandidate(Path(self._tmp.name))

    def test_strict_tier_change_needs_a_new_receipt_even_with_an_amendment_row(self):
        for path in ('joulewise/align/apple/endpoint.py', 'scripts/launch_window.py', 'docs/align/pilot_protocol_v4.md',
                     'joulewise/b6/idle_wait.py', 'scripts/b5_window_calibration_verdict.py'):
            with self.subTest(path=path):
                candidate = self.candidate()
                row = amendment(candidate, path, 'changed strict-tier bytes\n')
                with self.assertRaisesRegex(ValueError, 'digest drift.*strict tier'):
                    registration.validate_receipt(candidate.receipt, candidate.root)
                candidate.receipt['amendments'] = [row]
                with self.assertRaisesRegex(ValueError, 'strict-tier path'):
                    registration.validate_receipt(candidate.receipt, candidate.root)

    def test_amendment_tier_change_is_refused_without_a_row_and_admitted_with_a_signed_one(self):
        candidate = self.candidate()
        row = amendment(candidate, AMENDABLE, 'fixed infrastructure code\n')
        with self.assertRaisesRegex(ValueError, f'digest drift: {AMENDABLE}.*amendment tier'):
            registration.validate_receipt(candidate.receipt, candidate.root)
        candidate.receipt['amendments'] = [row]
        registration.validate_receipt(candidate.receipt, candidate.root)

    def test_amendment_rows_are_checked(self):
        candidate = self.candidate()
        row = amendment(candidate, AMENDABLE, 'fixed infrastructure code\n')
        bad_rows = {
            'wrong new sha': {**row, 'new_sha256': 'e' * 64},
            'wrong old sha': {**row, 'old_sha256': 'e' * 64},
            'no reason': {**row, 'reason': ' '},
            'unsigned': {**row, 'lead_signature': 'PENDING_LEAD_SIGNATURE'},
            'extra field': {**row, 'note': 'x'},
            'missing field': {k: v for k, v in row.items() if k != 'reason'},
            'bad digest': {**row, 'new_sha256': 'nothex'},
            'unbound path': {**row, 'path': 'joulewise/not_bound.py'},
        }
        for name, bad in bad_rows.items():
            with self.subTest(name=name):
                candidate.receipt['amendments'] = [bad]
                with self.assertRaises(ValueError):
                    registration.validate_receipt(candidate.receipt, candidate.root)
        candidate.receipt['amendments'] = 'not a list'
        with self.assertRaises(ValueError):
            registration.validate_receipt(candidate.receipt, candidate.root)

    def test_amendments_chain_and_a_later_unamended_edit_is_still_refused(self):
        candidate = self.candidate()
        first = amendment(candidate, AMENDABLE, 'first fix\n')
        second = amendment(candidate, AMENDABLE, 'second fix\n', old=first['new_sha256'])
        candidate.receipt['amendments'] = [first, second]
        registration.validate_receipt(candidate.receipt, candidate.root)
        broken = {**second, 'old_sha256': 'a' * 64}
        candidate.receipt['amendments'] = [first, broken]
        with self.assertRaisesRegex(ValueError, 'chain broken'):
            registration.validate_receipt(candidate.receipt, candidate.root)
        candidate.receipt['amendments'] = [first]                    # the working bytes moved past it
        with self.assertRaisesRegex(ValueError, 'digest drift'):
            registration.validate_receipt(candidate.receipt, candidate.root)

    def test_the_committed_pin_is_not_amendable(self):
        # An amendment never rewrites what the gates reviewed: the receipt's own digest must
        # still match the pinned commit.
        candidate = self.candidate()
        candidate.receipt['artifacts'][AMENDABLE] = 'c' * 64
        with self.assertRaisesRegex(ValueError, 'digest drift'):
            registration.validate_receipt(candidate.receipt, candidate.root)

    def test_artifact_set_digest_moves_with_any_bound_byte(self):
        candidate = self.candidate()
        before = registration.artifact_set_digest(candidate.root)
        self.assertEqual(before, registration.artifact_set_digest(candidate.root))
        candidate.write(AMENDABLE, 'edited\n')
        self.assertNotEqual(before, registration.artifact_set_digest(candidate.root))


if __name__ == '__main__':
    unittest.main()
