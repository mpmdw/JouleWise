"""The DIFFICULTY v2 registration (section 10, appendix A) pins file bytes; a merge must not move them."""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "docs/registrations/difficulty_pack_v2.md"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


class RegisteredHashTests(unittest.TestCase):
    def test_section_10_files_match_registration(self):
        text = REGISTRATION.read_text(encoding="utf-8")
        rows = re.findall(r"^\| `([^`]+)`[^|]*\| `([0-9a-f]{64})` \|$", text, re.M)
        self.assertEqual(len(rows), 12)
        for path, expected in rows:
            with self.subTest(path=path):
                self.assertEqual(sha256((ROOT / path).read_bytes()), expected)

    def test_appendix_a_configuration_hash(self):
        text = REGISTRATION.read_text(encoding="utf-8")
        block = text.split("\n```json\n", 1)[1].split("\n```", 1)[0] + "\n"
        self.assertEqual(sha256(block.encode("utf-8")),
                         "274994de6494074e3c716a981c5638ebed874aea84a4b61aa3d7c22b8dd7d9dd")


if __name__ == "__main__":
    unittest.main()
