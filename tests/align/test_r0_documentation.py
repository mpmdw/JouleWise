"""Keep the operator handoff explicit about its evidence and native limits."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class DocumentationTest(unittest.TestCase):
    def test_report_distinguishes_original_counts_and_unverified_ci(self):
        report = (ROOT / "docs/run_reports/2026-11-05-align-r0-desk.md").read_text()
        for term in ("31 new R0 tests", "9 pre-existing endpoint tests", "CI was not green",
                     "b6.test_cold_pass_fixes", "tests.align.test_r0_mlx_native"):
            self.assertTrue(term in report, f"handoff must retain: {term}")

    def test_runbook_explains_empty_metadata_and_robust_memory_evidence(self):
        book = (ROOT / "docs/align/r0_desk_runbook.md").read_text()
        for term in ("metadata_absent_single_stream", "median", "synchronize", "KV", "--gpu-step"):
            self.assertTrue(term in book, f"operator guidance must explain: {term}")


if __name__ == "__main__":
    unittest.main()
