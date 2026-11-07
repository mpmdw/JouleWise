"""Keep the operator handoff explicit about its evidence and native limits."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class DocumentationTest(unittest.TestCase):
    def test_d1_d6_runbook_has_smc_first_and_adaptive_idle(self):
        book = (ROOT / 'docs/align/r0_desk_runbook.md').read_text()
        for term in ('smc,host,disk,load', 'idle_max_seconds', 'ten consecutive',
                     '3,300 s', '2,700', 'per-phase coverage', 'baseline flags'):
            self.assertIn(term, book)
        sensors = (ROOT / 'docs/align/smc_temperature.md').read_text()
        for term in ('D1–D6', 'OLS residuals', '0.15', '500 ms', 'diagnostic only', '125 °C', 'Erratum 1'):
            self.assertIn(term, sensors)

    def test_report_distinguishes_original_counts_and_unverified_ci(self):
        report = (ROOT / "docs/run_reports/2026-11-05-align-r0-desk.md").read_text()
        for term in ("31 new R0 tests", "9 pre-existing endpoint tests", "CI was not green",
                     "b6.test_cold_pass_fixes", "tests.align.test_r0_mlx_native"):
            self.assertTrue(term in report, f"handoff must retain: {term}")

    def test_runbook_explains_empty_metadata_and_robust_memory_evidence(self):
        book = (ROOT / "docs/align/r0_desk_runbook.md").read_text()
        for term in ("metadata_absent_single_stream", "median", "synchronize", "KV", "--gpu-step"):
            self.assertTrue(term in book, f"operator guidance must explain: {term}")

    def test_runbook_separates_r0_disk_report_from_w1_storage_gate(self):
        book = (ROOT / "docs/align/r0_desk_runbook.md").read_text()
        for term in ("report-only", "66 decimal GB", "w1_disk_gate", "chat_template_kwargs",
                     "58525031a", "inside the same hub root", "selections and sensor locations remain PROVISIONAL"):
            self.assertIn(term, book)


if __name__ == "__main__":
    unittest.main()
