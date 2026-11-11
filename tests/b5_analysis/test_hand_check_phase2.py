"""Synthetic checks for the RL-38 reader; never opens study custody."""
import hashlib
import importlib.util
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


if __name__ == '__main__':
    unittest.main()
