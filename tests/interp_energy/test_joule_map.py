"""Synthetic energy recovery, drift, uncertainty and refusal tests; no captures."""

from dataclasses import asdict, replace
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from joulewise.interp_energy.joule_map import (
    Episode, analyze_map, desk_plan, interleaved_plan, synthetic_demo,
)

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/interp_energy/joule_map.py"


def exact_rows(n=8, *, cost=.02, perturbation=.007, drift=.00001):
    rows, _ = synthetic_demo(n, seed=12)
    rows = [r for r in rows if r.component_id == "layer0.attention"]
    return [replace(r, energy_j=100 * (.1 + drift * r.midpoint_s
                   + (perturbation if r.arm != "full" else 0)
                   - (cost if r.arm == "removed" else 0)) + r.idle_w * r.duration_s) for r in rows]


def component(result, name="layer0.attention"):
    return result["maps"][0]["components"][name]


class MapTests(unittest.TestCase):
    def test_plan_is_reproducible_balanced_and_randomized(self):
        a = interleaved_plan(["attention", "mlp", "head"], 8, seed=2)
        self.assertEqual(a, interleaved_plan(["attention", "mlp", "head"], 8, seed=2))
        self.assertNotEqual(a, interleaved_plan(["attention", "mlp", "head"], 8, seed=3))
        for start in range(0, len(a), 6):
            arms = [r["arm"] for r in a[start:start + 6]]
            self.assertEqual(arms, arms[::-1])
            self.assertEqual(set(arms[:3]), {"full", "clamped", "removed"})
        with self.assertRaises(ValueError):
            interleaved_plan(["head", "head"], 1)

    def test_removes_linear_drift_at_actual_times_and_corrects_control_shift(self):
        rows = exact_rows()
        # Input order has no effect; unequal durations imply unequal time weights.
        a = analyze_map(rows, bootstrap_replicates=399)
        self.assertEqual(a, analyze_map(rows[::-1], bootstrap_replicates=399))
        terms = component(a)
        self.assertAlmostEqual(terms["above_idle.corrected_saving"]["j_per_token"], .02)
        self.assertAlmostEqual(terms["above_idle.raw_saving"]["j_per_token"], .013)
        self.assertAlmostEqual(terms["above_idle.control_shift"]["j_per_token"], -.007)
        # A 2 s speedup at 3 W is .06 J/token of idle time, not target work.
        self.assertAlmostEqual(terms["gross.corrected_saving"]["j_per_token"], .08)
        for basis in ("gross", "above_idle"):
            self.assertAlmostEqual(terms[basis + ".raw_saving"]["j_per_token"]
                                   - terms[basis + ".control_shift"]["j_per_token"],
                                   terms[basis + ".corrected_saving"]["j_per_token"])

    def test_null_and_negative_costs_are_not_clipped(self):
        for cost in (0, -.005):
            terms = component(analyze_map(exact_rows(cost=cost), bootstrap_replicates=399))
            self.assertAlmostEqual(terms["above_idle.corrected_saving"]["j_per_token"], cost)

    def test_systematic_bound_does_not_average_down(self):
        bounds = []
        for n in (4, 16):
            terms = component(analyze_map(exact_rows(n), bootstrap_replicates=399))
            value = terms["above_idle.corrected_saving"]
            bounds.append(value["systematic_bound_j_per_token"])
            self.assertAlmostEqual(value["sensitivity_interval"][0], value["ci"][0] - bounds[-1])
        self.assertAlmostEqual(bounds[0], bounds[1])
        self.assertAlmostEqual(bounds[0], (.02 + .001 * 10 + .02 + .001 * 8) / 100)

    def test_correlated_additivity_audit_uses_matched_units(self):
        rows, audits = synthetic_demo(12, seed=2)
        costs = {"layer0.attention": .02, "layer0.mlp": .04, "layer0.joint": .055}
        rows = [r for r in rows if r.component_id in costs]
        # Strong common unit noise cancels in the paired audit (1 + 1 - 2).
        noise = {u: random.Random(i).gauss(0, .01) for i, u in enumerate(sorted({r.unit_id for r in rows}))}
        exact = []
        for r in rows:
            cost = costs[r.component_id] + noise[r.unit_id] * (2 if r.component_id.endswith("joint") else 1)
            net = .1 + (.01 if r.arm != "full" else 0) - (cost if r.arm == "removed" else 0)
            exact.append(replace(r, energy_j=100 * net + r.idle_w * r.duration_s))
        result = analyze_map(exact, bootstrap_replicates=399, bootstrap_block_units=2, additivity=audits)
        audit = result["maps"][0]["additivity"]["nonadditivity"]["above_idle.corrected_saving"]
        self.assertAlmostEqual(audit["j_per_token"], .005)
        self.assertLess(audit["ci"][1] - audit["ci"][0], 1e-12)
        self.assertFalse(audit["within_budget"])

    def test_context_and_boundary_strata_stay_separate(self):
        a = exact_rows()
        b = [replace(r, stratum_id="long", context_tokens=4096, boundary="gpu") for r in a]
        result = analyze_map(a + b, bootstrap_replicates=399)
        self.assertEqual(len(result["maps"]), 2)
        self.assertEqual({m["identity"]["context_tokens"] for m in result["maps"]}, {3, 4096})

    def test_refuses_mixed_work_missing_units_bad_tapes_and_bad_time(self):
        rows = exact_rows()
        for field, value in (("output_tokens", 99), ("context_tokens", 4),
                             ("prompt_sha256", "f" * 64), ("token_sequence_sha256", "f" * 64),
                             ("model_weights_sha256", "f" * 64), ("replay_policy_sha256", "f" * 64),
                             ("replacement_sha256", "f" * 64), ("source_kind", "unvalidated-native"),
                             ("arm", "removed"), ("midpoint_s", rows[1].midpoint_s)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                analyze_map([replace(rows[0], **{field: value})] + rows[1:], bootstrap_replicates=399)
        with self.assertRaises(ValueError):
            analyze_map(rows[1:], bootstrap_replicates=399)
        with self.assertRaises(ValueError):
            analyze_map(rows + [rows[0]], bootstrap_replicates=399)
        multiple, _ = synthetic_demo(8)
        with self.assertRaisesRegex(ValueError, "roster"):
            analyze_map([r for r in multiple if not (r.component_id.endswith("joint") and r.unit_id == "u0000")])

    def test_nonfinite_values_and_invalid_inference_parameters_fail(self):
        row = exact_rows()[0]
        for name, value in (("idle_w", float("nan")), ("energy_j", float("inf")),
                            ("output_tokens", True), ("energy_bound_j", -.1),
                            ("duration_s", 0), ("model_weights_sha256", "path")):
            with self.subTest(field=name), self.assertRaises(ValueError):
                replace(row, **{name: value})
        for kwargs in ({"confidence": 1}, {"confidence": .9999},
                       {"bootstrap_block_units": 3}, {"bootstrap_replicates": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                analyze_map(exact_rows(), **kwargs)

    def test_signed_rest_boundary_and_audit_refusals(self):
        rows = [replace(r, energy_j=-r.energy_j, idle_w=-r.idle_w, boundary="dc_minus_rails") for r in exact_rows()]
        self.assertLess(component(analyze_map(rows))["gross.corrected_saving"]["j_per_token"], 0)
        self.assertAlmostEqual(component(analyze_map(rows))["above_idle.corrected_saving"]["j_per_token"], -.02)
        for audit in ({"name": "x"}, {"name": "x", "parts": ["layer0.attention"],
                                     "joint": "layer0.attention", "budget_j_per_token": .1}):
            with self.assertRaises(ValueError):
                analyze_map(rows, additivity=[audit])

    def test_seeded_independent_unit_bootstrap_coverage(self):
        # Broad Monte Carlo tolerance, not a universal hardware coverage claim.
        covered = 0
        for trial in range(80):
            rng = random.Random(100 + trial)
            offsets = {f"u{i:04d}": rng.gauss(0, .004) for i in range(24)}
            rows = [replace(r, energy_j=r.energy_j - (100 * offsets[r.unit_id] if r.arm == "removed" else 0))
                    for r in exact_rows(24)]
            ci = component(analyze_map(rows, bootstrap_replicates=399, seed=trial))["above_idle.corrected_saving"]["ci"]
            covered += ci[0] <= .02 <= ci[1]
        self.assertGreaterEqual(covered, 68)  # >=85%; ~four binomial SEs below .95
        self.assertLessEqual(covered, 80)


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", "-S", str(CLI), *args], cwd=ROOT,
                              capture_output=True, text=True)

    def test_plan_and_demo_without_any_optional_dependencies(self):
        plan = self.run_cli("--plan-only")
        self.assertEqual(plan.returncode, 0, plan.stderr)
        self.assertEqual(json.loads(plan.stdout)["example"]["member_only_hours"], 48)
        demo = self.run_cli("--demo", "--bootstrap-replicates", "399")
        self.assertEqual(demo.returncode, 0, demo.stderr)
        self.assertEqual(json.loads(demo.stdout)["status"], "PROVISIONAL_DESK_ANALYSIS")
        self.assertEqual(desk_plan()["power"]["budget_units"], 12)

    def test_named_input_roundtrip_and_json_refusals(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.json"
            path.write_text(json.dumps({"episodes": [asdict(r) for r in exact_rows()], "additivity": []}))
            result = self.run_cli("--input", str(path), "--bootstrap-replicates", "399")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertAlmostEqual(component(json.loads(result.stdout))["above_idle.corrected_saving"]["j_per_token"], .02)
            for bad in ('{"episodes":[],"episodes":[],"additivity":[]}',
                        '{"episodes":NaN,"additivity":[]}', '{"episodes":[],"additivity":[],"path":"opaque"}'):
                path.write_text(bad)
                self.assertNotEqual(self.run_cli("--input", str(path)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
