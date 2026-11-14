"""RL-145 addendum row 8: the two gate files are byte-identical to the executed commit a6a09e6d7.

Any byte change to either file fails the suite. Repository files only.
"""
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PINNED = {
    'joulewise/align/apple/thermal_gates.py': 'c72937bd8bf7b5553c1ffd70e76018ffbf25f32578533c8749aa88419837918d',
    'joulewise/align/apple/thermal.py': 'b9b46f9ede50b265c245dcc05d3503139632ae129e313675622fa1dce25d39d7',
}


class GateFileHashTests(unittest.TestCase):
    def test_gate_files_are_byte_identical_to_the_executed_commit(self):
        for path, digest in PINNED.items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)


if __name__ == '__main__':
    unittest.main()
