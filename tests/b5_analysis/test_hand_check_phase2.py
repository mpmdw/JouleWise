"""Synthetic checks for the RL-38 reader; never opens study custody."""
import hashlib
import importlib.util
import csv
from contextlib import redirect_stdout
from decimal import localcontext
import io
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).absolute().parents[2] / 'docs/analysis/b5/hand_check_phase2.py'
spec = importlib.util.spec_from_file_location('phase2_reader', SCRIPT)
reader_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader_module)


class AccessBoundaryTests(unittest.TestCase):
    def test_other_root_is_rejected_before_stat(self):
        with patch.object(Path, 'lstat', side_effect=AssertionError('filesystem touched')):
            with self.assertRaisesRegex(ValueError, 'outside unseal'):
                reader_module.CustodyReader.checked_path(Path('/unapproved'), 'file.json')

    def test_absolute_and_parent_paths_are_rejected_before_stat(self):
        for relative in ('/outside.json', '../outside.json', 'sub/../../outside.json'):
            with self.subTest(relative=relative):
                with patch.object(Path, 'lstat', side_effect=AssertionError('filesystem touched')):
                    with self.assertRaisesRegex(ValueError, 'outside unseal'):
                        reader_module.CustodyReader.checked_path(reader_module.ROOT_A, relative)

    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'link').symlink_to(root/'absent-target')
            with patch.object(reader_module, 'ROOT_A', root):
                with self.assertRaisesRegex(ValueError, 'symlink refused'):
                    reader_module.CustodyReader.checked_path(root, 'link')

    def test_wrong_hash_refuses_before_json_parse(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'bad.json').write_bytes(b'not JSON')
            source = {'TEST': (root, 'bad.json', '0'*64)}
            with patch.object(reader_module, 'ROOT_A', root), patch.object(reader_module, 'SOURCES', source):
                with patch.object(reader_module.json, 'loads', side_effect=AssertionError('parsed unverified bytes')):
                    with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                        reader_module.CustodyReader().read('TEST')

    def test_changed_file_refuses_end_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = b'{"count": 2}'
            p = root/'sample.json'
            p.write_bytes(payload)
            source = {'TEST': (root, p.name, hashlib.sha256(payload).hexdigest())}
            with patch.object(reader_module, 'ROOT_A', root), patch.object(reader_module, 'SOURCES', source):
                reader = reader_module.CustodyReader()
                self.assertEqual(reader.read('TEST'), {'count': 2})
                p.write_bytes(b'{"count": 3}')
                with self.assertRaisesRegex(ValueError, 'changed during read'):
                    reader.finish()

    def test_projection_prefix_needs_content_name_and_full_record_pin(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = b'{}'
            digest = hashlib.sha256(payload).hexdigest()
            p = root/(digest+'-projection.json')
            p.write_bytes(payload)
            source = {'TEST': (root, p.name, digest[:12])}
            with patch.object(reader_module, 'ROOT_A', root), patch.object(reader_module, 'SOURCES', source):
                reader = reader_module.CustodyReader()
                with self.assertRaisesRegex(ValueError, 'read REC first'):
                    reader.read('TEST')
                reader.projection_pins.add(digest)
                self.assertEqual(reader.read('TEST'), {})
                self.assertEqual(reader.finish()['TEST']['sha256_after'], digest)


class IndependentArithmeticTests(unittest.TestCase):
    def test_student_tail_has_closed_form_witnesses(self):
        self.assertAlmostEqual(reader_module.student_tail(1, 1), .5, places=14)
        self.assertAlmostEqual(reader_module.student_tail(1, 2), 1-1/math.sqrt(3), places=14)
        self.assertAlmostEqual(reader_module.t975(5), 2.570581835636314, places=12)

    def test_fixed_stratum_weights_survive_unequal_unit_counts(self):
        result = reader_module.stratified([0, 2, 4], [9, 11])
        self.assertAlmostEqual(result['mean'], 8.4)
        self.assertNotAlmostEqual(result['mean'], (0+2+4+9+11)/5)
        self.assertEqual((result['n_r'], result['n_b'], result['df']), (3, 2, 1))

    def test_quad_orientation(self):
        members = [{'E_j': {'decode': x}} for x in (2, 10, 14, 6)]
        self.assertEqual(reader_module.quad_difference(members, 'decode'), 8)

    def test_common_sign_is_distinct_from_independent_corners(self):
        values = [0]*5
        shared = reader_module.widened_floor(values, [0]*5, False, common=[1]*5)
        independent = reader_module.widened_floor(values, [1]*5, False)
        self.assertEqual(shared, 1)
        self.assertGreater(independent, shared)

    def test_absolute_floor_recenters_comparative_does_not(self):
        self.assertEqual(reader_module.point_floor([10]*5, True), 0)
        self.assertEqual(reader_module.point_floor([10]*5, False), 10)

    def test_printed_precision_does_not_accept_a_real_disagreement(self):
        self.assertEqual(reader_module.printed_compare('1.23', 1.234)[2], 'within-rounding')
        self.assertEqual(reader_module.printed_compare('1.23', 1.236)[2], 'MISMATCH')
        self.assertEqual(reader_module.printed_compare('36%', .3606)[0], '36%')
        self.assertEqual(reader_module.printed_compare('78,389', 78389)[2], 'exact')


class PrintAuthorityTests(unittest.TestCase):
    def test_residual_precision_cannot_recover_full_input(self):
        cases = {'0.006543219876543': '0.0065', '-0.000076543219876': '-0.000077',
                 '0.00999': '0.010', '1.99999999999999999e-24': '2.0e-24',
                 '-0.000000': '0', '-1 distinct cause': '-1 distinct cause', '': ''}
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(reader_module.difference_text(value), expected)
        self.assertEqual(reader_module.printed_compare('36%', .36064268123456)[1], '0.064')
        # Classification happens before rounding the difference.
        self.assertEqual(reader_module.printed_compare('1.23', 1.23501)[2], 'MISMATCH')
        with self.assertRaisesRegex(ValueError, 'non-finite'):
            reader_module.difference_text('Infinity')

    def test_source_residual_in_note_is_also_rounded(self):
        rows = [{'difference': '0.00025888888888888',
                 'note': 'SOURCED: example; source difference=-0.000987654321; HAND: synthetic'}]
        reader_module.round_differences(rows)
        self.assertEqual(rows[0]['difference'], '0.00026')
        self.assertIn('source difference=-0.00099;', rows[0]['note'])

    def test_normalized_paths_collapse_lists_and_contrasts(self):
        contrast = {'floor': {'point_floor_diagnostics': {'value': 1, 'valid': True},
                              'resolutions': [{'point_floor_diagnostics': {'value': 2}}]},
                    'claim_evaluation': {'floor_limit': {'entries': [{'bound': 2}, {'bound': 3}],
                                                       'status': 'synthetic'}}}
        self.assertEqual(reader_module.dle5_leaf_counts([contrast, contrast]), (5, 12))

    def test_repository_mode_never_constructs_custody_reader(self):
        with patch.object(reader_module.CustodyReader, '__init__', side_effect=AssertionError('custody reader constructed')):
            with patch('sys.argv', [str(SCRIPT), '--repo-only']), redirect_stdout(io.StringIO()) as output:
                reader_module.main()
        self.assertIn('"byte_identical": true', output.getvalue())

    def test_opus_repository_mode_never_computes_from_custody(self):
        opus_path = SCRIPT.with_name('opus_coldreview_check.py')
        spec = importlib.util.spec_from_file_location('opus_reader', opus_path)
        opus = importlib.util.module_from_spec(spec)
        with localcontext():
            spec.loader.exec_module(opus)
            with patch.object(opus, 'compute', side_effect=AssertionError('custody compute called')):
                with patch.object(opus, 'load', side_effect=AssertionError('custody load called')):
                    with patch('sys.argv', [str(opus_path), '--repo-only']), redirect_stdout(io.StringIO()) as output:
                        opus.main()
        self.assertIn('"rounded_hand_table_byte_identical": true', output.getvalue())

    def test_rulings_are_idempotent_and_count_drift_stops(self):
        with SCRIPT.with_name('rederivation.tsv').open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        original = reader_module.table_text(rows)
        reader_module.apply_print_rulings(rows)
        self.assertEqual(reader_module.table_text(rows), original)
        rows[0]['match'] = 'MISMATCH'
        with self.assertRaisesRegex(ValueError, 'STOP: RL-42 counts differ'):
            reader_module.apply_print_rulings(rows)


if __name__ == '__main__':
    unittest.main()
