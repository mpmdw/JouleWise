from __future__ import annotations

import hashlib
import unittest

from joulewise import analysis_manifest_v3, identity_pins
from joulewise.analysis_engine import artifact
from joulewise.authentication_io import canonical_json_bytes


FIXTURE_CORPUS = {
    "empty_object": (
        {},
        b"{}",
        "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
    ),
    "key_order": (
        {"z": 1, "a": 2},
        b'{"a":2,"z":1}',
        "c2985c5ba6f7d2a55e768f92490ca09388e95bc4cccb9fdf11b15f4d42f93e73",
    ),
    "nested_unicode": (
        {
            "unicode": "caf\N{LATIN SMALL LETTER E WITH ACUTE} \N{HOT BEVERAGE}",
            "nested": {
                "\N{GREEK SMALL LETTER BETA}": [True, None, "line\nbreak"]
            },
        },
        (
            '{"nested":{"\N{GREEK SMALL LETTER BETA}":[true,null,"line\\nbreak"]},'
            '"unicode":"caf\N{LATIN SMALL LETTER E WITH ACUTE} \N{HOT BEVERAGE}"}'
        ).encode("utf-8"),
        "e31f8df95c5415b98c966100471b346b6aac0c115083ef52ff25452267f16f89",
    ),
    "finite_numbers": (
        {"negative": -7, "fraction": 1.25, "zero": 0},
        b'{"fraction":1.25,"negative":-7,"zero":0}',
        "1178b0ad096dc037f4ea7f075a5f9da1db032b002ec5ad7c6d1901787c03c8ab",
    ),
}


class CanonicalJsonBytesTests(unittest.TestCase):
    def test_claim_path_names_are_one_object(self) -> None:
        self.assertIs(identity_pins.canonical_json_bytes, canonical_json_bytes)
        self.assertIs(analysis_manifest_v3.canonical_json_bytes, canonical_json_bytes)
        self.assertIs(artifact.canonical_json_bytes, canonical_json_bytes)

    def test_fixture_bytes_and_pre_move_hashes_are_unchanged(self) -> None:
        for name, (value, expected_bytes, expected_sha256) in FIXTURE_CORPUS.items():
            with self.subTest(name=name):
                actual = canonical_json_bytes(value)
                self.assertEqual(actual, expected_bytes)
                self.assertEqual(hashlib.sha256(actual).hexdigest(), expected_sha256)


if __name__ == "__main__":
    unittest.main()
