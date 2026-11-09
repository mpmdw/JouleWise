"""Independence and determinism: stdlib-only, never joulewise, pinned program digest, structure-only
stdout, canonical output, and parallel (and cached) runs byte-identical to the serial run."""
import ast
import hashlib
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

from .support import SCRIPT, SMALL, rc, run_cli, synth

# Pinned program digest. A change to the program changes this pin in the same commit, so a reviewer
# sees every program change; the recompute JSON records program_sha256 for the comparator.
PROGRAM_SHA256 = "99dee73a8b3f789797ee55a65504377a3dd378deb7086ba546cddf9ec7a88c20"


class IndependenceTests(unittest.TestCase):
    def imports(self):
        tree = ast.parse(SCRIPT.read_text())
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(node.level, 0)
                names.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and getattr(node.func, "id", None) == "__import__":
                self.fail("dynamic import")
            elif isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "import_module":
                self.fail("importlib import")
        return names

    def test_never_imports_joulewise_and_only_stdlib(self):
        names = self.imports()
        self.assertNotIn("joulewise", names)
        self.assertEqual(sorted(n for n in names if n not in sys.stdlib_module_names), [])
        # No path into the joulewise package either (no sys.path games, no file reads of it).
        self.assertIsNone(re.search(r"joulewise/|sys\.path", SCRIPT.read_text()))

    def test_program_digest_is_pinned(self):
        self.assertEqual(hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), PROGRAM_SHA256)


class DeterminismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name) / "s"
        synth.write_series(cls.root, windows=["C1", "C2", "T1"], w1=True, **SMALL)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_to(self, name, *extra):
        out = Path(self.tmp.name) / name
        code, stdout, stderr = run_cli("--root", self.root, "--out", out, *extra)
        self.assertEqual((code, stderr), (0, ""))
        return out.read_bytes(), stdout

    def test_parallel_and_cached_runs_are_byte_identical_to_serial(self):
        serial, stdout = self.run_to("serial.json", "--workers", 1)
        parallel, _ = self.run_to("parallel.json", "--workers", 4)
        cache = Path(self.tmp.name) / "cache"
        miss, _ = self.run_to("miss.json", "--workers", 3, "--reduce-cache", cache)
        hit, _ = self.run_to("hit.json", "--workers", 2, "--reduce-cache", cache)
        self.assertEqual(serial, parallel)
        self.assertEqual(serial, miss)
        self.assertEqual(serial, hit)
        doc = json.loads(serial)
        self.assertEqual(rc.canonical(doc) + b"\n", serial)   # canonical, strict JSON
        self.assertEqual(doc["program_sha256"], hashlib.sha256(SCRIPT.read_bytes()).hexdigest())
        # stdout carries counts and status words only: no decimal number, no member id.
        self.assertIsNone(re.search(r"\d\.\d|[eE][-+]?\d", stdout))
        self.assertNotIn("align-v4", stdout)

    def test_reduction_digests_bind_the_raw_bytes(self):
        data, _ = self.run_to("r.json", "--workers", 1)
        doc = json.loads(data)
        rid = "align-v4-c1-e06"
        raw = self.root / "windows/C1/members" / rid / "raw/powermetrics.plist"
        red = doc["reduction"][rid]
        self.assertEqual(red["raw_sha256"], synth.sha256_file(raw))
        self.assertEqual(red["raw_bytes"], raw.stat().st_size)
        reduced = rc.reduce_stream(raw)
        self.assertEqual(red["columns"], rc.column_stats(reduced["columns"]))
        self.assertEqual(doc["inputs"]["windows"]["C1"]["members"][rid]["raw_sha256"], red["raw_sha256"])


if __name__ == "__main__":
    unittest.main()
