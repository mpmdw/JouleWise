"""Tests for the round-7 DX artifact fence.

The always-on tests read every digest, field path, rendering rule, and expected
value from the registry parser exported by the fence; this file intentionally
contains no pinned digest.  Figure 4 stores coordinates to 0.01 px, so the
fence's 0.0008 ms y tolerance is the upward-rounded half-unit inversion
``0.005 px * 50 ms / 326 px``; its x tolerance is derived the same way.

The replay test is corpus-gated, like the Section 2 fence test.  A skip is not a
pass: the CLI test separately proves that an absent corpus exits 3 and names
the missing path.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FENCE_PATH = ROOT / "scripts" / "check_paper_round7_artifacts.py"
REGISTRY_PATH = Path(
    os.environ.get("R7F_REGISTRY", ROOT / "docs" / "paper" / "results-fill-registry.md")
)
SKELETON_PATH = ROOT / "docs" / "paper" / "draft-v2-skeleton.md"
CORPUS_ROOT = Path("/Users/edr/code/JouleWise")

FENCE_SPEC = importlib.util.spec_from_file_location("check_paper_round7_artifacts", FENCE_PATH)
assert FENCE_SPEC is not None and FENCE_SPEC.loader is not None
FENCE = importlib.util.module_from_spec(FENCE_SPEC)
sys.modules[FENCE_SPEC.name] = FENCE
FENCE_SPEC.loader.exec_module(FENCE)

CORPUS_PRESENT = all(
    path.exists()
    for path in (
        CORPUS_ROOT
        / "runs_window_a_20260722"
        / "instrument_validation"
        / "20260722T145535-e941c821"
        / "instrument_evidence.json",
        CORPUS_ROOT
        / "runs_window_a_20260722"
        / "instrument_validation"
        / "20260722T145535-e941c821"
        / "raw"
        / "powermetrics.plist",
        CORPUS_ROOT / "runs" / "instrument_validation",
    )
)


class RegistryAndDigestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REGISTRY_PATH.read_text(encoding="utf-8")
        cls.spec = FENCE.parse_registry_text(cls.text)
        cls.artifacts, json_checks = FENCE.load_json_artifacts(ROOT, cls.spec)
        if not all(check.match for check in json_checks):
            raise AssertionError(json_checks)

    def test_registry_has_the_closed_dx_row_set(self) -> None:
        self.assertEqual(tuple(self.spec.rows), FENCE.EXPECTED_DX_IDS)
        self.assertEqual(len(self.spec.rows), 19)

    def test_registry_pinned_files_match(self) -> None:
        comparisons = FENCE.check_file_pins(ROOT, self.spec)
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_every_supplier_field_resolves(self) -> None:
        comparisons = FENCE.check_supplier_fields(self.spec, self.artifacts)
        self.assertGreater(len(comparisons), len(self.spec.rows))
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_every_registry_marker_renders_from_its_supplier(self) -> None:
        comparisons = FENCE.check_rendered_rows(self.spec, self.artifacts)
        self.assertEqual(len(comparisons), len(self.spec.rows))
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_artifact_gates_are_true(self) -> None:
        comparisons = FENCE.check_gates(self.artifacts)
        self.assertEqual(len(comparisons), 3)
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_all_118_figure_marks_invert_to_xd(self) -> None:
        comparisons = FENCE.check_figure(ROOT, self.spec, self.artifacts)
        marks = [row for row in comparisons if re.fullmatch(r"figure (?:onset|offset) mark [0-9]+", row.label)]
        self.assertEqual(len(marks), 118)
        self.assertTrue(all(row.match for row in comparisons), comparisons)

    def test_current_skeleton_has_no_malformed_dx_literal(self) -> None:
        comparisons = FENCE.check_skeleton_literals(
            SKELETON_PATH.read_text(encoding="utf-8"), self.spec
        )
        self.assertTrue(all(row.match for row in comparisons), comparisons)


class RefusalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REGISTRY_PATH.read_text(encoding="utf-8")
        cls.spec = FENCE.parse_registry_text(cls.text)
        cls.artifacts, _ = FENCE.load_json_artifacts(ROOT, cls.spec)

    def test_malformed_dx_row_is_refused(self) -> None:
        original = next(line for line in self.text.splitlines() if line.startswith("| DX-010 "))
        mutated = original.replace("| MEASURED |", "| UNKNOWN |")
        self.assertNotEqual(mutated, original)
        with self.assertRaises(FENCE.RegistryError):
            FENCE.parse_registry_text(self.text.replace(original, mutated, 1))

    def test_altered_registered_digest_is_refused(self) -> None:
        digest = self.spec.sources["XD"].sha256
        replacement = ("0" if digest[0] != "0" else "1") + digest[1:]
        mutated_text = self.text.replace(digest, replacement)
        mutated_spec = FENCE.parse_registry_text(mutated_text)
        comparisons = FENCE.check_file_pins(ROOT, mutated_spec)
        self.assertTrue(any(not row.match and row.label == "digest XD" for row in comparisons))

    def test_altered_json_field_is_refused(self) -> None:
        artifacts = copy.deepcopy(self.artifacts)
        artifacts["XD"]["summary"]["onset_best_fit_lag"]["median_ms"] = 13.1
        comparisons = FENCE.check_rendered_rows(self.spec, artifacts)
        self.assertTrue(any(not row.match and row.label == "row DX-010" for row in comparisons))

    def test_altered_registry_value_is_refused(self) -> None:
        original = next(line for line in self.text.splitlines() if line.startswith("| DX-010 "))
        mutated = original.replace("| +13.0 ms |", "| +13.1 ms |")
        self.assertNotEqual(mutated, original)
        spec = FENCE.parse_registry_text(self.text.replace(original, mutated, 1))
        comparisons = FENCE.check_rendered_rows(spec, self.artifacts)
        self.assertTrue(any(not row.match and row.label == "row DX-010" for row in comparisons))

    def test_altered_successor_literal_is_refused(self) -> None:
        comparisons = FENCE.check_skeleton_literals("[FILL:DX-010] +13.1 ms\n", self.spec)
        self.assertEqual(len(comparisons), 1)
        self.assertFalse(comparisons[0].match)

    def test_exact_successor_literal_is_accepted(self) -> None:
        comparisons = FENCE.check_skeleton_literals("[FILL:DX-010] +13.0 ms\n", self.spec)
        self.assertEqual(len(comparisons), 1)
        self.assertTrue(comparisons[0].match)

    def test_missing_json_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for code, pin in self.spec.sources.items():
                if code == "XD":
                    continue
                target = root / pin.path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / pin.path, target)
            comparisons = FENCE.check_file_pins(root, self.spec)
            self.assertTrue(any(not row.match and row.label == "digest XD" for row in comparisons))
            artifacts, json_checks = FENCE.load_json_artifacts(root, self.spec)
            self.assertNotIn("XD", artifacts)
            self.assertTrue(any(not row.match and row.label == "JSON XD" for row in json_checks))


class InvocationTests(unittest.TestCase):
    def test_literals_only_cli_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(FENCE_PATH), "--literals-only"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertRegex(completed.stdout.splitlines()[-1], r"^R7F COMPARED [0-9]+ / MISMATCHES 0$")

    def test_absent_corpus_exits_three_and_names_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing_root = Path(directory) / "no-such-corpus"
            completed = subprocess.run(
                [sys.executable, str(FENCE_PATH), "--corpus-root", str(missing_root)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 3, completed.stdout + completed.stderr)
        self.assertIn(str(missing_root), completed.stdout)
        self.assertRegex(completed.stdout.splitlines()[-1], r"^R7F COMPARED [0-9]+ / MISMATCHES 0$")


@unittest.skipUnless(
    CORPUS_PRESENT,
    "retained XD/AQ corpora are not present; run the default R7F CLI where both corpora live",
)
class ReplayAgainstRetainedCorporaTests(unittest.TestCase):
    def test_both_producers_are_byte_identical(self) -> None:
        spec = FENCE.parse_registry(REGISTRY_PATH)
        comparisons = FENCE.replay_half(ROOT, CORPUS_ROOT, spec)
        self.assertEqual([row.label for row in comparisons], [
            "replay XD bytes",
            "replay F4 bytes",
            "replay AQ bytes",
        ])
        self.assertTrue(all(row.match for row in comparisons), comparisons)


if __name__ == "__main__":
    unittest.main()
