"""MED-4: the desk prints per-member DC residuals for BENIGN members only; sabotage rows are sealed."""
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import km003c as meter
from scripts import align_v4_kit as kit
from scripts import align_v4_session as session

SECRET = 987654.321       # a sabotage member's DC value; must never be printed or recorded


def row(residual, energy):
    return {**meter._empty(), 'status': 'available', 'dc_in_energy_j': energy, 'dc_in_delta_j': energy / 2,
            'dc_in_residual_j': residual, 'residual_status': 'scored', 'score': residual, 'flags': [],
            'turn_rows': [{'residual_j': residual}]}


class SealTests(unittest.TestCase):
    def report(self):
        return {'schema': 'x', 'label': meter.LABEL, 'print_only': True, 'detail': None,
                'members': {'benign-1': row(4.5, 100.0), 'sab-1': row(SECRET, SECRET), 'odd-1': row(SECRET, SECRET)}}

    def plan(self):
        return [{'run_id': 'benign-1', 'condition': 'benign'}, {'run_id': 'sab-1', 'condition': 'sabotage'},
                {'run_id': 'odd-1'}]

    def test_benign_rows_pass_through_and_everything_else_is_hash_only(self):
        sealed = meter.seal_non_benign(self.report(), self.plan())
        self.assertEqual(sealed['members']['benign-1']['dc_in_residual_j'], 4.5)
        for rid in ('sab-1', 'odd-1'):             # a missing condition is sealed too (fail closed)
            self.assertTrue(sealed['members'][rid]['sealed'])
            self.assertEqual(len(sealed['members'][rid]['sealed_hmac_sha256']), 64)
        text = json.dumps(sealed)
        self.assertNotIn(str(SECRET), text)
        self.assertNotIn('dc_in_residual_j', json.dumps(sealed['members']['sab-1']))
        # auditable: the hash changes with the hidden value, so the sealed row can be checked later
        other = self.report()
        other['members']['sab-1'] = row(SECRET+1, SECRET)
        self.assertNotEqual(meter.seal_non_benign(other, self.plan())['members']['sab-1']['sealed_hmac_sha256'],
                            sealed['members']['sab-1']['sealed_hmac_sha256'])

    def test_desk_prints_benign_dc_values_and_no_sabotage_dc_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reg = root / 'kit/registration'
            reg.mkdir(parents=True)
            members = [{'run_id': 'benign-1', 'condition': 'benign', 'ordinal': 5, 'ac_powermode': 0, 'role': 'D'},
                       {'run_id': 'sab-1', 'condition': 'sabotage', 'ordinal': 11, 'ac_powermode': 0, 'role': 'D'}]
            (reg.parent / 'collection_plan.json').write_text(json.dumps({'members': members}))
            state = {'measurement_root': str(root), 'registration_dir': str(reg), 'inputs': {'custody_root': str(root)}}
            report = {'schema': 'x', 'label': meter.LABEL, 'print_only': True, 'detail': None,
                      'members': {'benign-1': row(4.5, 100.0), 'sab-1': row(SECRET, SECRET)}}
            out = io.StringIO()
            with patch.object(session, 'bundle_ac_powermode', return_value=0), \
                    patch.object(meter, 'session_report', return_value=report), redirect_stdout(out):
                checks, desk = session.powermode_desk_check(state=state, members=[], runs_root=root, kit_path=kit.KIT)
            printed = out.getvalue()
            self.assertIn('benign-1', printed)
            self.assertIn('4.5', printed)
            self.assertIn('sab-1', printed)
            self.assertIn('sealed_hmac_sha256', printed)
            self.assertNotIn(str(SECRET), printed)
            self.assertNotIn(str(SECRET), json.dumps(desk, default=str))
            self.assertTrue(desk['km003c']['members']['sab-1']['sealed'])
            self.assertFalse(any('km003c' in k or 'meter' in k for k in checks))


if __name__ == '__main__':
    unittest.main()
