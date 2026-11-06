import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import qwen4exp_align_feasibility as feasibility


class AlignFeasibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.policy = {
            "schema": "align-v4-feasibility/v1",
            "limits": {"episode_time_limit_s": 1000, "deadman_limit_s": 800},
            "efforts": {
                "low": {"initial_prompt_tokens": 4000, "turns": [
                    {"reasoning_tokens": 100, "answer_tokens": 100},
                    {"reasoning_tokens": 12000, "answer_tokens": 1000},
                    {"reasoning_tokens": 23000, "answer_tokens": 700}]},
                "medium": {"initial_prompt_tokens": 4000, "turns": [
                    {"reasoning_tokens": 28000, "answer_tokens": 0}]},
                "xhigh": {"initial_prompt_tokens": 4000, "turns": [
                    {"reasoning_tokens": 35000, "answer_tokens": 0}]},
            },
            "window": {"length_s": 3600, "episode_count": 5},
        }
        self.budget = self.root / "budget.json"
        self.budget.write_text(json.dumps(self.policy))

    def performance(self, name, multiplier=1, profile="maxfit", decode_by_context=None):
        rows = [{"reasoning_effort": e, "context": c,
                 "prefill_tps": 100 * multiplier,
                 "decode_tps": (decode_by_context or {}).get(c, 100) * multiplier}
                for e in self.policy["efforts"] for c in feasibility.CONTEXT_RUNGS]
        path = self.root / name
        # Shape of qwen4exp_mbp_live.supervise(): worker rows nest under "results".
        path.write_text(json.dumps({"schema": "qwen4exp-mbp-live/v1", "command": "performance",
                                    "profile": profile, "verdict": "completed",
                                    "results": {"verdict": "completed", "medians": rows}}))
        return path

    def test_prompt_growth_uses_4k_16k_and_late_40960_medians(self):
        rates = feasibility.load_performance([self.performance("p.json")])
        result = feasibility.calculate(self.policy, rates)
        low = result["rows"][0]
        # Prefills: 4000 + 4200 + 17200. Decodes: 200 + 13000 + 23700.
        self.assertAlmostEqual(low["episode_wall_seconds"], 623)
        self.assertEqual(low["episodes_per_window"], 5)
        self.assertEqual(low["verdict"], "MARGINAL")

    def test_verdict_boundaries_and_plan_fields_come_from_fixture(self):
        rows = feasibility.calculate(self.policy, feasibility.load_performance([self.performance("p.json")]))["rows"]
        self.assertEqual([r["verdict"] for r in rows], ["MARGINAL", "FEASIBLE", "FEASIBLE"])
        slow = feasibility.calculate(self.policy, feasibility.load_performance([self.performance("slow.json", .1)]))
        self.assertTrue(all(r["verdict"] == "INFEASIBLE" for r in slow["rows"]))

    def test_second_performance_file_supplies_preferred_medians(self):
        rates = feasibility.load_performance([self.performance("512.json"), self.performance("2048.json", 2)])
        self.assertEqual(rates[("low", 4096)]["prefill_tps"], 200)

    def test_cli_labels_estimate_and_never_imports_mlx(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(feasibility.main(["--performance", str(self.performance("p.json")),
                                               "--budget", str(self.budget)]), 0)
        self.assertIn("PLANNING ESTIMATE — NOT ENERGY EVIDENCE", out.getvalue())
        self.assertIn("5 episodes in 3600 s", out.getvalue())

    def test_parses_literal_policy_from_align_python_without_importing_it(self):
        source = self.root / "align_v4_feasibility.py"
        source.write_text("raise RuntimeError('must not import')\nALIGN_V4_FEASIBILITY = " + repr(self.policy))
        loaded, identity = feasibility.load_budget_source(source)
        self.assertEqual(loaded, self.policy)
        self.assertEqual(identity, str(source))

    def test_reads_medians_where_the_supervisor_writes_them(self):
        path = self.performance("p.json")
        report = json.loads(path.read_text())
        report["medians"] = report.pop("results")["medians"]  # pre-fix fixture shape
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "not completed|no median"):
            feasibility.load_performance([path])

    def test_decode_that_outgrows_the_measured_context_is_refused(self):
        bad = json.loads(json.dumps(self.policy))
        bad["efforts"]["xhigh"]["turns"] = [{"reasoning_tokens": 37000, "answer_tokens": 0}]  # 41,000
        with self.assertRaisesRegex(ValueError, "exceeds measured"):
            feasibility.calculate(bad, feasibility.load_performance([self.performance("p.json")]))

    def test_decode_is_charged_at_the_context_it_reaches(self):
        rates = feasibility.load_performance([self.performance(
            "p.json", decode_by_context={4096: 100, 16384: 50, 40960: 10})])
        medium = feasibility.calculate(self.policy, rates)["rows"][1]
        # 4,000 + 28,000 reaches the 40,960 rung: 28,000 / 10 tok/s.
        self.assertAlmostEqual(medium["decode_seconds"], 2800)

    def test_window_that_cannot_hold_its_planned_episodes_is_infeasible(self):
        policy = json.loads(json.dumps(self.policy))
        policy["window"]["episode_count"] = 12  # medium fits 11 x 320 s in 3600 s
        rows = feasibility.calculate(policy, feasibility.load_performance([self.performance("p.json")]))["rows"]
        self.assertEqual(rows[1]["episodes_per_window"], 11)
        self.assertEqual(rows[1]["verdict"], "INFEASIBLE")

    def test_refuses_mixed_artifact_profiles(self):
        with self.assertRaisesRegex(ValueError, "mix artifact profiles"):
            feasibility.load_performance([self.performance("a.json"), self.performance("b.json", profile="maxfit5")])

    def test_refuses_unmeasured_context_and_incomplete_report(self):
        bad = json.loads(json.dumps(self.policy))
        bad["efforts"]["low"]["initial_prompt_tokens"] = 50000
        with self.assertRaisesRegex(ValueError, "exceeds measured"):
            feasibility.calculate(bad, feasibility.load_performance([self.performance("p.json")]))
        path = self.performance("incomplete.json")
        report = json.loads(path.read_text())
        report["verdict"] = "incomplete"
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "not completed"):
            feasibility.load_performance([path])


if __name__ == "__main__":
    unittest.main()
