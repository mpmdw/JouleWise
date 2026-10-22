"""Small synthetic oracles for surviving BYTES arithmetic mutations."""
from __future__ import annotations

import csv
import itertools
import math
import tempfile
import unittest
from pathlib import Path

from joulewise import bytes_analysis as ba


def _manifest():
    return {
        "synthetic": True,
        "models": [{
            "model": "fabricated", "cell_ids": ["cell"], "role": "heldout",
            "moe": False, "tier": False, "W_bytes": 1_000_000_000,
            "KV_bytes": 0, "R_bytes": 2_000_000_000,
        }],
        "sessions": [{
            "session_id": "synthetic-p1", "pass_id": 1, "test7_passed": True,
        }],
    }


def _module():
    reference = {
        "test7_passed": True,
        "boundaries": {"rails": {"energy_j": 100, "duration_s": 10,
            "families": {family: {"allowance_j": 1}
                         for family in ("gross", "idle_subtracted")}}},
    }
    return [{
        "model": "fabricated", "pass_id": 1, "session_id": "synthetic-p1",
        "run_id": str(i), "stratum": "repeat" if i < 10 else "quad",
        "unit_id": str(i if i < 10 else (i - 10) // 4),
        "status": "succeeded", "excluded": False, "flags": [], "meter": None,
        "duration_s": 2, "rails_j": 20, "rails_secondary_j": 18,
        "rails_anchor_j": .125, "rails_interpolation_j": .25,
        "operative": {"status": "synthetic"}, "neg8_inputs": reference,
    } for i in range(50)]


def _passes():
    common = {
        "model": "fabricated", "boundary": "rails", "basis": "gross primary",
        "selection": "primary", "bytes": .5, "resident": 2,
        "role": "heldout", "moe": False, "tier": False, "status": "computed",
        "h_j": 1, "B_j": .5, "meter_phase_edge_mean_j": 0,
        "duration_s": 2, "meter_attribution_floor_j": None,
    }
    return [dict(common, pass_id=i, mean_j=mean, attribution_floor_j=floor,
                 without_assisted={"mean_j": mean - 10, "h_j": 1,
                                   "B_j": .5, "below_minimum": False})
            for i, mean, floor in ((1, 100, 1), (2, 120, 4))]


def _cube():
    # Independent signs make the noise orthogonal to the two regressors.
    return [{
        "model": f"cube-{i}", "boundary": "rails", "tier": i < 6,
        "BW": 2 + a, "resident": 2 + b, "time": 1,
        "power": 3 + 2 * (2 + a) + c,
    } for i, (a, b, c) in enumerate(itertools.product((-1, 1), repeat=3))]


class BytesArithmeticMutationTests(unittest.TestCase):
    def assert_quantity(self, actual, expected):
        # bar: 1e-6 relative, or 1e-6 absolute at zero (COMMON fallback;
        # these synthetic JSON outputs have no printed half-width).
        self.assertAlmostEqual(
            actual, expected, delta=abs(expected) * 1e-6 if expected else 1e-6)

    def test_named_primary_coefficients(self):
        """Named epsilon is the slope, not the intercept. Kills M7ca4b6ba13."""
        result = ba.h2(_cube(), {})
        # P = 3 + 2*BW + c; c sums to zero against 1, BW and resident.
        expected = {"epsilon": 2, "extended_epsilon": 2, "rho": 0,
                    "tier_epsilon": 2, "tier_rho": 0}
        coefficients = [r for r in result["primary_intervals"]
                        if not r["term"].startswith("tier_deviation:")]
        self.assertEqual({r["term"] for r in coefficients}, set(expected))
        self.assert_quantity(result["two_term"]["coefficients"][0], 3)
        for row in coefficients:
            with self.subTest(term=row["term"]):
                self.assert_quantity(row["estimate"], expected[row["term"]])
        # Mutation binds epsilon to 3 instead of 2: 1 / 2e-6 = 500,000 bars.

    def test_primary_interval_endpoints(self):
        """H2 endpoints use family-adjusted t and independent SEs. Kills M5bfe141b2f."""
        # Residuals [1,-1,-1,1] are orthogonal to 1 and x=[1,2,3,4].
        # The constant resident regressor refuses the extended fit; the tier
        # is empty, so epsilon is the only primary interval (family=1, df=2).
        points = [dict(model=str(x), BW=x, resident=1, time=1, tier=False,
                       boundary="rails", power=y)
                  for x, y in zip((1, 2, 3, 4), (6, 6, 8, 12))]
        result = ba.h2(points, {})
        self.assertEqual(result["k"], 1)
        # Sxx=5, SSE=4, MSE=2. Leverages [.7,.3,.3,.7] give
        # HC3 slope variance 2*(.3/.3)^2+2*(.1/.7)^2=100/49.
        # OLS slope variance=MSE/Sxx=2/5.
        hc3, ols = 10/7, math.sqrt(2/5)
        # For t with df=2, F(t)=1/2+t/(2*sqrt(t*t+2)).
        # Setting F=.975 gives t*t=722/39, independently of ba's quantile.
        critical = math.sqrt(722/39)
        row = result["primary_intervals"][0]
        self.assert_quantity(row["HC3_se"], hc3)
        self.assert_quantity(row["OLS_se"], ols)
        self.assert_quantity(row["lower"], 2 - critical * hc3)
        self.assert_quantity(row["upper"], 2 + critical * hc3)
        lo, hi = result["two_term"]["ols_intervals"][1]
        self.assert_quantity(lo, 2 - critical * ols)
        self.assert_quantity(hi, 2 + critical * ols)
        # Mutant shifts HC3 lower endpoint >4.7 J/GB; bar <4.2e-6 J/GB:
        # >1,100,000 bars.

    def test_leave_one_out_predictions_use_the_other_nine_points(self):
        """Every LOO fold uses all nine other rows. Kills M9320cf871e."""
        points = [{
            "model": str(x), "BW": x, "resident": 1 + x % 3, "time": 1,
            "power": 3 + 2*x + (10 if x == 1 else 0),
            "tier": x <= 6, "boundary": "rails",
        } for x in range(1, 11)]
        rows = ba.h2(points, {})["loo_description"]
        self.assertEqual(len(rows), 10)
        self.assertEqual([row["status"] for row in rows], ["computed"] * 10)
        # Full-data sufficient statistics by hand: n=10, sum x=55,
        # sum x^2=385, sum y=150, sum xy=945. Remove one observation
        # and solve the 2x2 normal equations (independent of centered OLS).
        for point, row in zip(points, rows):
            x, y = point["BW"], point["power"]
            sx, sy, sxx, sxy = 55-x, 150-y, 385-x*x, 945-x*y
            determinant = 9*sxx - sx*sx
            expected = ((sy*sxx - sx*sxy) + x*(9*sxy - sx*sy)) / determinant
            self.assert_quantity(row["predicted_w"], expected)
        # The mutant refuses four folds: exact status/count difference, bar=0.

    def test_deviation_uses_the_full_covariance(self):
        """Prediction spread includes off-diagonal covariance. Kills Mc44c81c98c."""
        # Cube fit centered at (2,2): covariance=(8/25)I. Translating
        # its intercept yields this non-diagonal covariance in native units.
        fit = {"coefficients": [3, 2, 0], "mse": 8/5, "critical": 2,
               "covariance": [[72/25, -16/25, -16/25],
                              [-16/25, 8/25, 0], [-16/25, 0, 8/25]]}
        result = ba.deviation(fit, [4, 4], 13)
        # Query centered at (2,2): parameter variance=(8/25)*(1+4+4)
        # =72/25; add residual 8/5 =>112/25 before taking sqrt.
        self.assert_quantity(result["prediction_half_w"], 2 * math.sqrt(112/25))
        # Mutant uses only 128/25, giving a half-width shift >0.95 W:
        # >220,000 bars of 4.24e-6 W.

    def test_pass_difference_is_signed_in_pass_order(self):
        """Pass difference is pass 2 minus pass 1. Kills M7a54107169."""
        for means, expected in (((100, 120), 20), ((120, 100), -20)):
            rows = _passes()
            for row, mean in zip(rows, means):
                row["mean_j"] = mean
            # Reverse delivery order: the pass identities still define the sign.
            actual = ba.combine_passes(rows[::-1])[0]["pass_difference_j"]
            self.assertEqual(actual, expected)
        # Integer subtraction is exact in binary64; mutant shift >=200 J, bar=0.

    def test_combined_attribution_floor_is_worst_pass(self):
        """Combined rails floor is the largest pass floor. Kills M381d9ca0e1, Me32213db94."""
        for floors in ((1, 4), (4, 1)):
            rows = _passes()
            for row, floor in zip(rows, floors):
                row["attribution_floor_j"] = floor
            self.assertEqual(ba.combine_passes(rows)[0]["attribution_floor_j"], 4)
        # Copied integer floors are exact; either operand collapse loses 3 J, bar=0.

    def test_combined_meter_floor_is_worst_pass(self):
        """Combined meter floor is the largest pass floor. Kills M96abad714d, Mf9872383d4."""
        for floors in ((2, 5), (5, 2)):
            rows = _passes()
            for row, floor in zip(rows, floors):
                row.update(boundary="DC input", meter_attribution_floor_j=floor,
                           meter_offset_bound_j=0, meter_offset_sensitivity_w=0)
            self.assertEqual(ba.combine_passes(rows)[0]["meter_attribution_floor_j"], 5)
        # Copied integer floors are exact; either operand collapse loses 3 J, bar=0.

    def test_pass_attribution_floor_is_worst_member(self):
        """A pass retains its largest kept member anchor. Kills M2b0d65cb43."""
        records = _module()
        records[-1]["rails_anchor_j"] = .75
        cell = ba.reduce_models(records, _manifest(), boundaries=("rails",))[0]
        self.assertEqual(cell["attribution_floor_j"], .75)
        # Dyadic anchors are copied/added to zero exactly; mutant loses .625 J, bar=0.

    def test_blinded_secondary_subtracts_each_runs_own_idle_energy(self):
        """Blinded secondary subtracts own idle watts times duration.

        Kills M50017a0b7b, M3fcc328578, Md003ace2ad, M47d491a92f, Maa40c1f7ea.
        """
        fields = [
            "run_id", "role", "cell_ids", "strata", "unit_ids", "config_key",
            "status", "excluded", "exclusion_codes", "flag_codes", "emitted_tokens",
            "dur_decode_s", "phase_decode_j", "idle_power_w", "gross_energy_j",
            "idle_subtracted_energy_j", "bound_E_clock_anchor_shift_bound_j",
            "bound_E_interpolation_joint_edge_bound_j",
        ]
        rows = []
        for i in range(50):
            repeat = i < 10
            unit = i if repeat else (i - 10) // 4
            # Five repeats and one complete quad are excluded. The remaining
            # strata have unequal sizes, forcing registered .2/.8 weights.
            excluded = (repeat and unit < 5) or (not repeat and unit == 0)
            rows.append(dict.fromkeys(fields, ""))
            rows[-1].update(
                run_id=str(i), role="floor", cell_ids="cell",
                strata="repeat" if repeat else "quad", unit_ids=str(unit),
                status="succeeded", excluded=str(excluded).lower(),
                exclusion_codes="member.cooldown_cap_hit" if excluded else "",
                emitted_tokens=512, dur_decode_s=2 if repeat else 4,
                phase_decode_j=20 if repeat else 30, idle_power_w=1 if repeat else 2,
                bound_E_clock_anchor_shift_bound_j=.125,
                bound_E_interpolation_joint_edge_bound_j=0)
        for role, count in (("corpus", 6), ("start", 2), ("end", 2)):
            for i in range(count):
                row = dict.fromkeys(fields, "")
                row.update(run_id=f"{role}-{i}", role=role, config_key="neg8_reference",
                           status="succeeded", excluded="false", dur_decode_s=10,
                           gross_energy_j=100, idle_subtracted_energy_j=90)
                rows.append(row)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            with (source / "synthetic-p1.runs.csv").open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            records = ba.load_records(source, _manifest(), stage="blinded")
            cells = ba.reduce_models(records, _manifest(), boundaries=("rails",))
            point = next(p for p in ba.combine_passes(cells)
                         if p["basis"] == "idle-subtracted secondary")
        # Repeat E_idle=1W*2s=2J, net=18J. Quad E_idle=2W*4s=8J, net=22J.
        # Registered weights: .2*18 + .8*22 = 21.2 J, not a member average.
        self.assert_quantity(point["mean_j"], 21.2)
        # Mutant means: 6.8, 34.8, 28, 27.5, 26.2 J. Smallest gap=5 J,
        # over 235,000 bars (bar=21.2e-6 J).

    def test_without_assisted_lower_endpoint(self):
        """Diagnostic lower bound includes mean, h and B with minus signs.

        Kills Mf7ce56a8c4, M0421a346f4, M1e2d8592af, M8649a2af33,
        M2764469c3f, M2b4a97c71e, Ma6293ad65e.
        """
        diagnostic = ba.combine_passes(_passes())[0]["without_assisted"]
        # Mean of 90/110 is 100; subtract h=1 and B=.5. Dyadic arithmetic
        # is exact in binary64. Mutants lose the value or shift >=.5 J, bar=0.
        self.assertEqual(diagnostic["lower_j"], 98.5)

    def test_without_assisted_upper_endpoint(self):
        """Diagnostic upper bound includes mean, h and B with plus signs.

        Kills M124a7259b5, M34764e0ab8, Mf37183b001, M8a8751d3ff,
        M03c1d567e8, M4d52f54e3a, Mb59420ce4e.
        """
        diagnostic = ba.combine_passes(_passes())[0]["without_assisted"]
        # 100 + 1 + .5 = 101.5 J, exactly in binary64; missing value or
        # smallest mutant shift .5 J is visible under exact comparison, bar=0.
        self.assertEqual(diagnostic["upper_j"], 101.5)

    def test_without_assisted_energy_per_output_token(self):
        """Diagnostic energy per output token divides by 512. Kills M941bc63cc8."""
        diagnostic = ba.combine_passes(_passes())[0]["without_assisted"]
        # 100/512=.1953125 is exact in binary64. Multiplication instead
        # gives 51,200, an exact-value difference of 51,199.8046875, bar=0.
        self.assertEqual(diagnostic["printed_j_per_output_token"], .1953125)

    def test_without_assisted_sums_all_bounds_with_undefined_variance(self):
        """One-unit diagnostic retains all three bounds despite null h.

        Kills M8508398ca4, M576d952762, M7f7466a914.
        """
        records = _module()
        for row in records:
            if row["unit_id"] != "0":
                row["flags"] = ["battery.assist"]
        diagnostic = ba.reduce_models(
            records, _manifest(), boundaries=("rails",))[0]["without_assisted"]
        self.assertEqual((diagnostic["n_r"], diagnostic["n_b"]), (1, 1))
        self.assertIsNone(diagnostic["h_j"])
        # Each retained member: anchor .125 J, interpolation .25 J,
        # drift .5*allowance(1 J)*scale(1)=.5 J. Sum = .875 J.
        self.assert_quantity(diagnostic["B_j"], .875)
        # Operand collapses give .125/.25/.5 J: gap >=.375 J,
        # >428,000 bars of .875e-6 J.
