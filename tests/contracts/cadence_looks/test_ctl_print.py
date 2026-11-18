"""Run the unchanged freeze against the controls builder under test discovery."""

from copy import deepcopy
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import controls_print as controls

from . import synthetic_acceptance as vectors
from .ctl_print_adapter import check_fixture


class TestFrozenControlsPrint(vectors.Contract):
    def setUp(self):
        super().setUp()
        validator = patch.object(vectors, "VALIDATE", check_fixture)
        validator.start()
        self.addCleanup(validator.stop)


class TestControlsPrintProjection(unittest.TestCase):
    def test_pair_depth_from_fresh_calls(self):
        def episode(kind, counts):
            return controls.Episode(kind, (), controls.Delivery(counts, 0, 0, 0, 120),
                                    (2000,) * len(counts), 106, "a" * 64)

        self.assertEqual(controls.compare_pair(episode("split", (342, 341, 341)),
                                               episode("plain", (1024,))), (2342, 3024))

    def test_zero_pin_refuses_even_if_committed(self):
        committed, candidate = vectors.example()
        committed["plan"]["code_sha"] = candidate["plan"]["code_sha"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "binding"):
            check_fixture(committed, candidate)

    def test_public_projection_is_unchanged_by_private_values(self):
        committed, candidate = vectors.example()
        public = committed["public"]
        expected = (b'{"commit":"' + b"b" * 40 + b'","look_id":"lm-ctl-01","manifest_sha256":"'
                    + public["manifest_sha256"].encode() + b'","n_legs":12,"stage1_sha256":"'
                    + public["stage1_sha256"].encode() + b'"}')
        self.assertEqual(controls.encode_public_projection(candidate["public"], public), expected)

        variant = deepcopy(candidate)
        variant["private"]["phases"]["dc_in"][-1] = 98
        variant["private"]["qualifier"] = "no"
        check_fixture(committed, variant)
        self.assertEqual(controls.encode_public_projection(variant["public"], public), expected)

    def test_public_projection_refuses_a_word_even_if_committed(self):
        committed, candidate = vectors.example()
        committed["public"]["qualifier"] = candidate["public"]["qualifier"] = "yes"
        with self.assertRaisesRegex(ValueError, "public disclosure"):
            check_fixture(committed, candidate)
