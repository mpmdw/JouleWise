"""B0 oracle/corpus checks and the intentionally red current-head parity gate.

Full corpus: python3 -B tests/parity/b0_runner.py --candidate .
Focused unittest: python3 -B -m unittest tests.test_b0_idle_parity
Set B0_PARITY_CANDIDATE to another archive/tree to test a future cure without
editing expectations. No production assertion is fitted to bee658c5.
"""
import gzip
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from tests.parity.b0_corpus import AXES, DEFAULTS, OPERATIONS, corpus, jobs, named_cases
from tests.parity.b0_runner import differences, safe_scratch, shrink_changes, parity_failed

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests/parity/b0_runner.py"


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = corpus()

    def test_every_single_and_every_pair_without_other_faults(self):
        actual = {tuple(sorted(c["changes"].items())) for c in self.cases}
        for axis, values in AXES.items():
            for value in values[1:]:
                self.assertIn(((axis, value),), actual)
        for a, b in combinations(AXES, 2):
            for av, bv in product(AXES[a][1:], AXES[b][1:]):
                self.assertIn(tuple(sorted(((a, av), (b, bv)))), actual)

    def test_exhaustive_cleanup_cross(self):
        cross = [c for c in self.cases if c["id"].startswith("cross.")]
        self.assertEqual(len(cross), 5 * len(AXES["receipt_encoding"]) * len(AXES["c5"]) * len(AXES["outcome"]))
        self.assertEqual(len({c["id"] for c in cross}), len(cross))
        for c in cross:
            self.assertEqual(c["operations"], ["driver.cleanup", "driver.courier_cleanup"])

    def test_deterministic_generation_and_projection(self):
        self.assertEqual(self.cases, corpus())
        selected = list(jobs())
        self.assertEqual(selected, list(jobs()))
        self.assertEqual({j["operation"] for j in selected}, set(OPERATIONS))
        for j in selected:
            self.assertTrue(set(j["changes"]).issubset(OPERATIONS[j["operation"]]))
            self.assertTrue(all(v != DEFAULTS[a] for a, v in j["changes"].items()))

    def test_named_witnesses_are_retained_on_every_surface(self):
        names = {c["id"] for c in named_cases()}
        selected = {(j["id"], j["operation"]) for j in jobs()}
        for name in names:
            for operation in OPERATIONS:
                self.assertIn((name, operation), selected)
        for prefix in ("29a.F1", "29a.F2", "29b.B1", "29b.B2", "29b.N1", "47b.C1", "47b.C2", "47b.C3", "47b.C5", "47b.C6", "72b.F1", "72b.F2", "72b.F3", "72b.F4"):
            self.assertTrue(any(n.startswith(prefix) for n in names), prefix)

    def test_exact_comparator_kills_observable_mutations(self):
        baseline = {"return": None, "exception": {"class": "Refused", "message": "old", "refusal_code": "x"},
            "stdout": "line\n", "stderr": "", "files": {"a": {"after": {"bytes_base64": "YQ==", "mode": 420}}},
            "calls": [{"call": "first", "args": [1]}, {"call": "second", "args": [2]}]}
        for key, value in (
            ("return", {}), ("exception", {"class": "TypeError", "message": "old", "refusal_code": "x"}),
            ("exception", {"class": "Refused", "message": "changed", "refusal_code": "x"}),
            ("exception", {"class": "Refused", "message": "old", "refusal_code": "y"}),
            ("stdout", "line"), ("stderr", "error"), ("files", {}),
            ("files", {"a": {"after": {"bytes_base64": "Yg==", "mode": 420}}}),
            ("files", {"a": {"after": {"bytes_base64": "YQ==", "mode": 493}}}),
            ("calls", list(reversed(baseline["calls"]))),
        ):
            with self.subTest(key=key, value=value):
                self.assertTrue(list(differences(baseline, dict(baseline, **{key: value}))))
        self.assertFalse(list(differences(baseline, baseline)))

    def test_scratch_fence(self):
        self.assertEqual(safe_scratch("/tmp/278ebc9e/b0par-test").name, "b0par-test")
        for path in ("/tmp/other", "/Users/edr/night-custody", "/tmp/278ebc9e/b0par-test/child", "/tmp/278ebc9e/other"):
            with self.assertRaises(ValueError): safe_scratch(path)

    def test_shrinking_preserves_the_interaction(self):
        minimal, history = shrink_changes({"wrapper": "bad", "encoding": "bom", "irrelevant": "x"},
            lambda c: c.get("wrapper") == "bad" and c.get("encoding") == "bom")
        self.assertEqual(minimal, {"wrapper": "bad", "encoding": "bom"})
        self.assertTrue(any(row["removed"] == "irrelevant" and row["still_fails"] for row in history))

    def test_private_api_availability_cannot_make_parity_impossible(self):
        self.assertFalse(parity_failed({"mismatches": 2, "new_private_api": 2}))
        self.assertTrue(parity_failed({"mismatches": 3, "new_private_api": 2}))
        self.assertTrue(parity_failed({"mismatches": 2, "new_private_api": 2,
                                       "authority_failures": ["72b.F4.bare_idle"]}))


class DifferentialTests(unittest.TestCase):
    def run_harness(self, output, *args):
        completed = subprocess.run([sys.executable, "-B", str(RUNNER), "--output", output, *args],
            cwd=ROOT, text=True, capture_output=True, timeout=600)
        self.assertIn(completed.returncode, (0, 1), completed.stdout + completed.stderr)
        # A crashed evaluator must never reuse a previous run's summary and
        # masquerade as a successful compatibility check.
        self.assertTrue(completed.stdout.rstrip().endswith(("PARITY PASS", "PARITY FAIL")),
                        completed.stdout + completed.stderr)
        return completed, json.loads((Path(output) / "summary.json").read_bytes())

    def test_oracle_self_parity_and_nonvacuous_valid_seeds(self):
        output = "/tmp/278ebc9e/b0par-unit-self"
        completed, summary = self.run_harness(output, "--self", "--case", "idle.valid")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(summary["mismatches"], 0)
        with gzip.open(Path(output) / "base.jsonl.gz", "rt") as f:
            rows = {r["operation"]: r for r in map(json.loads, f)}
        for operation, row in rows.items():
            self.assertIsNone(row["exception"], operation)
        self.assertEqual(rows["generator.render_only"]["return"], 0)
        self.assertEqual(rows["driver.probe_dispatch"]["return"], 0)
        self.assertTrue(rows["zero_capture_facts"]["return"]["facts"]["fields"]["scan_complete"])
        self.assertTrue(rows["driver.cleanup"]["files"])
        self.assertTrue(any(c["call"] == "write_refusal" for c in rows["driver.cleanup"]["calls"]))
        for operation in ("gate.C5", "gate.C3"):
            self.assertIsNone(rows[operation]["return"]["receipt"])

    def test_idle_parity_against_candidate(self):
        output = "/tmp/278ebc9e/b0par-unit-candidate"
        completed, summary = self.run_harness(output, "--candidate", os.environ.get("B0_PARITY_CANDIDATE", str(ROOT)), "--case", "72b.")
        # New-private-API observations are kept in reports but are not a public
        # compatibility assertion. All shared-surface diffs, including calls,
        # fail this gate. Expected red until the independent fix seat acts.
        public = summary["mismatches"] - summary["new_private_api"]
        self.assertEqual(public, 0, completed.stdout + "\nExact differences: " + output + "/inventory.md")
        self.assertFalse(summary["authority_failures"], completed.stdout)


if __name__ == "__main__":
    unittest.main()
