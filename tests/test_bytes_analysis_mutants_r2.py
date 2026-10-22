"""Independent synthetic oracles for the second BYTES survivor batch."""
from __future__ import annotations

import itertools
import json
import math
import unittest
from pathlib import Path

from joulewise import bytes_analysis as ba
from joulewise.external import km003c_parse as kp


def _models():
    path = Path(__file__).parent / "fixtures/bytes/campaign_design.json"
    # A public config_key per model keeps this manifest valid on the BY-REV
    # lane, whose validate_manifest requires one; this head ignores it.
    return [{**model, "config_key": model.get("config_key") or f"synthetic|{model['model']}|512"}
            for model in json.loads(path.read_text())["models"]]


def _line_points():
    # Four non-tier registered models can remain after other cells are refused.
    # Constant resident rate refuses the extended design; k=1, df=2 makes
    # the statistical interval independently soluble without ba's quantile.
    models = [m for m in _models() if not m["tier"]]
    return [dict(model=m["model"], BW=x, resident=1, time=1, tier=False,
                 boundary="DC input", power=y, duration_s=duration,
                 meter_offset_bound_w=bound, meter_offset_sensitivity_w=sensitivity)
            for m, x, y, duration, bound, sensitivity in zip(
                models, (1, 2, 3, 4), (6, 6, 8, 12), (2, 4, 2, 4),
                (.25, .5, .75, 1), (2, -8, 6, -16))]


def _epsilon():
    result = ba.h2(_line_points(), {}, boundary="DC input")
    return next(row for row in result["primary_intervals"] if row["term"] == "epsilon")


def _meter_stream():
    # Exact device/host mapping at 10 Hz; powers jump at 4 s and 6 s.
    watts = [20] * 40 + [10] * 20 + [30] * 41
    samples = kp.Samples([i * 100 for i in range(101)], [1] * 101,
                         watts, [0] * 51 + [1] * 50, 0, 100)
    batches = [{"tx": 5_000_000_000, "rx": 5_000_000_000, "n": 51},
               {"tx": 10_000_000_000, "rx": 10_000_000_000, "n": 50}]
    fit = kp.clock_fit(samples, batches)
    fit.stats.update(excess_latency_ms_min=-7, excess_latency_ms_max=3)
    return kp.Stream({"start_raw_ns": 0, "start_mono_ns": 0},
                     {"end_raw_ns": 10_000_000_000, "end_mono_ns": 10_000_000_000},
                     batches, [], samples, fit,
                     [fit.host_ns(d) for d in samples.dev_ms], watts, [], [])


def _passes():
    common = dict(model="Qwen3-4B-4bit", boundary="DC input", basis="gross primary",
                  selection="primary", bytes=1, resident=2, role="fit", moe=False,
                  tier=True, status="computed", h_j=1, B_j=.5,
                  meter_phase_edge_mean_j=2, meter_attribution_floor_j=2,
                  attribution_floor_j=2, mean_j=100, meter_offset_sensitivity_w=10)
    return [dict(common, pass_id=1, duration_s=2, meter_offset_bound_j=2),
            dict(common, pass_id=2, duration_s=4, meter_offset_bound_j=6)]


class BytesOffsetMutationTests(unittest.TestCase):
    def assert_quantity(self, actual, expected):
        # bar: 1e-6 relative, or 1e-6 absolute at zero (COMMON fallback;
        # these synthetic quantities have no printed half-width).
        self.assertAlmostEqual(actual, expected,
                               delta=abs(expected) * 1e-6 if expected else 1e-6)

    def test_offset_bound_keeps_registered_stratum_weights(self):
        """Unequal kept strata retain .2/.8 meter-bound weights. Kills A0a9cde7a8e."""
        models = _models()
        manifest = dict(synthetic=True, models=models, sessions=[
            dict(session_id="synthetic-p1", pass_id=1, test7_passed=True)])
        ba.validate_manifest(manifest)
        reference = dict(energy_j=100, duration_s=10, families={
            family: {"allowance_j": 1} for family in ("gross", "idle_subtracted")})
        records = []
        for i in range(50):
            repeat = i < 10
            records.append(dict(
                model=models[0]["model"], pass_id=1, session_id="synthetic-p1",
                run_id=str(i), stratum="repeat" if repeat else "quad",
                unit_id=str(i if repeat else (i - 10) // 4),
                status="succeeded", excluded=i < 5, flags=[], duration_s=2,
                rails_j=20, rails_secondary_j=18, rails_anchor_j=.125,
                rails_interpolation_j=0, operative={"status": "synthetic"},
                meter=dict(gross_j=40, secondary_j=36, phase_edge_j=2,
                           offset_bound_j=.2 if repeat else 1.2,
                           offset_sensitivity_w=10),
                neg8_inputs=dict(test7_passed=True, boundaries={
                    boundary: reference for boundary in ("DC input", "rest")})))
        cells = ba.reduce_models(records, manifest, boundaries=("DC input", "rest"))
        self.assertEqual({(c["n_r"], c["n_b"]) for c in cells}, {(5, 10)})
        for point in ba.combine_passes(cells):
            with self.subTest(boundary=point["boundary"], basis=point["basis"]):
                # Five repeat bounds average .2 J; ten quad means average 1.2 J.
                # Registered support = .2*.2 + .8*1.2 = 1 J for either boundary.
                self.assert_quantity(point["meter_offset_bound_j"], 1)
        # Plain member mean = (5*.2 + 40*1.2)/45 = 49/45 J:
        # gap 4/45 J / bar 1e-6 J > 88,000 bars.

    def test_pass_offset_bound_is_the_arithmetic_mean(self):
        """Two pass supports average without taking their minimum. Kills Ab131190591."""
        point = ba.combine_passes(_passes()[::-1])[0]
        # (2 J + 6 J)/2 = 4 J; integer/dyadic arithmetic is exact in binary64.
        self.assertEqual(point["meter_offset_bound_j"], 4)
        # Mutant gives 2 J: exact-value difference 2 J, bar=0.

    def test_power_support_is_the_ratio_of_pass_means(self):
        """Mean joule support is divided by mean duration.

        Kills N7fb83e8a45, N9f8754fabe, Nf4337f66b3.
        """
        point = ba.combine_passes(_passes())[0]
        # Mean support (2+6)/2=4 J; mean duration (2+4)/2=3 s.
        # 4 J / 3 s = 4/3 W, rather than mean(2/2, 6/4)=1.25 W.
        self.assert_quantity(point["meter_offset_bound_w"], 4/3)
        # Mutants give 3, 4, 12 W; minimum gap 5/3 W:
        # (5/3)/(4/3*1e-6) = 1,250,000 bars.

    def test_named_coefficient_support_uses_slope_response_weights(self):
        """Named epsilon carries its own response-box support.

        Kills A43c663184b, A6f129d8feb through the public H2 result.
        """
        # For x=1..4, Sxx=5 and slope response weights are [-.3,-.1,.1,.3].
        # A response box [.25,.5,.75,1] W permits maximal slope movement
        # .075+.05+.075+.3 = .5 J/GB (all four signs can attain the support).
        self.assert_quantity(_epsilon()["coefficient_C"], .5)
        # Intercept support is 1 W: using its numeric value for the slope
        # instead produces 1 J/GB (gap .5 = 1,000,000 bars).
        # Replacing multiplication by addition gives .8+2.5=3.3 J/GB
        # (gap 2.8 = 5,600,000 bars of .5e-6 J/GB).

    def test_named_hc3_offset_endpoints_belong_to_epsilon(self):
        """Named epsilon widens its own HC3 interval. Kills A425e4cc5d5."""
        row = _epsilon()
        # y=3+2*x+[1,-1,-1,1]; leverages [.7,.3,.3,.7] give
        # slope HC3 variance 2*(.3/.3)^2+2*(.1/.7)^2=100/49.
        # df=2: F(t)=.5+t/(2*sqrt(t*t+2)); F(t)=.975 => t²=722/39.
        # Widen the slope, 2 +/- t*(10/7), by support .5 J/GB.
        half = math.sqrt(722/39) * 10/7
        self.assert_quantity(row["offset_intervals"][0], 1.5 - half)
        self.assert_quantity(row["offset_intervals"][1], 2.5 + half)
        # Intercept is 3, support 1, HC3 SE sqrt(125/9+25/49).
        # Binding its interval instead shifts either endpoint >9 J/GB;
        # each asserted endpoint's bar <9e-6 J/GB: >1,000,000 bars.

    def test_named_ols_offset_endpoints_belong_to_epsilon(self):
        """Named epsilon widens its own labelled OLS interval. Kills A3f168e754d."""
        row = _epsilon()
        # SSE=4, df=2 => MSE=2; slope OLS variance=MSE/Sxx=2/5.
        # Same independent df=2 critical value and .5 J/GB response support.
        half = math.sqrt(722/39) * math.sqrt(2/5)
        self.assert_quantity(row["offset_ols_intervals"][0], 1.5 - half)
        self.assert_quantity(row["offset_ols_intervals"][1], 2.5 + half)
        # Intercept OLS SE=sqrt(3), estimate=3, support=1.
        # Wrong-index endpoints shift >4 J/GB; bars <6e-6 J/GB:
        # >660,000 bars.

    def test_named_sensitivity_normalizes_duration_and_milliseconds(self):
        """Epsilon sensitivity divides each edge difference by its own time and 1000.

        Kills N66dcefba03, Nf1dec3fc9c, Nbd525b83a6, Abfaff8e135.
        """
        # Differences [2,-8,6,-16] W over [2,4,2,4] s give [1,-2,3,-4] W/s.
        # Their centered x cross-product is -5, and Sxx=5: slope=-1 per s,
        # hence -.001 J/GB per ms. The intercept is +2 per s, not the slope.
        self.assert_quantity(_epsilon()["d_beta_d_delta_per_ms"], -.001)
        # Multiply time => -.016; omit time => -.004; multiply 1000 => -1000;
        # wrong index => +.002. Minimum gap .003 / bar 1e-9 = 3,000,000 bars.

    def test_positive_resident_effect_is_not_labelled_adds_nothing(self):
        """A strictly positive offset rho rejects adds-nothing. Kills A6b8b4d4bc5."""
        models = _models()
        models = [m for m in models if m["tier"]] + [m for m in models if not m["tier"]][:2]
        points = [dict(model=m["model"], tier=m["tier"], BW=2+a,
                       resident=2+b, time=1, boundary="DC input", duration_s=2,
                       power=3 + 2*(2+a) + 4*(2+b) + c/8,
                       meter_offset_bound_w=.125, meter_offset_sensitivity_w=0)
                  for m, (a, b, c) in zip(models, itertools.product((-1, 1), repeat=3))]
        result = ba.h2(points, {}, boundary="DC input")
        # Cube signs are orthogonal: y=3+2*BW+4*resident+c/8 gives rho=4.
        # Rho weights b/8 give response support 8*(1/8)*.125=.125 J/GB.
        # Small orthogonal noise leaves its widened interval well above zero.
        rho = next(r for r in result["primary_intervals"] if r["term"] == "rho")
        self.assert_quantity(rho["estimate"], 4)
        self.assertGreater(rho["offset_intervals"][0], 3)
        self.assertIs(result["resident_adds_nothing_offset"], False)
        # Mutant returns True: exact Boolean difference, bar=0.

    def test_meter_sensitivity_uses_samples_strictly_before_both_edges(self):
        """Coherent displacement subtracts the two immediately preceding powers.

        Kills N68fb78c3a3, N2c5c3172fc, N42a7cdbfed, N34bd2a0bff, Aa5a0256147.
        """
        result = ba.meter_decode(_meter_stream(), [4_000_000_000, 6_000_000_000],
                                 [1_000_000_000, 3_000_000_000])
        # At aligned edges the preceding samples are t=3.9 s (20 W) and
        # t=5.9 s (10 W). Derivative of energy with displacement: 20-10=10 W.
        # Powers and integer subtraction are exact in binary64.
        self.assertEqual(result["offset_sensitivity_w"], 10)
        # Fixed index 0/1 => 0 W; right-hand sample => -20 W; sum => 30 W.
        # Minimum difference 10 W under exact comparison, bar=0.

    def test_meter_offset_bound_covers_the_larger_edge(self):
        """A coherent offset support uses the larger edge power. Kills A4b8b9b81b8."""
        result = ba.meter_decode(_meter_stream(), [4_000_000_000, 6_000_000_000],
                                 [1_000_000_000, 3_000_000_000])
        # Edge-adjacent maxima are 20 W and 30 W. Worst residual is 7 ms;
        # one 100 ms sample plus residual permits .107 s displacement.
        # A coherent shift swaps one slice: 30 W * .107 s = 3.21 J.
        self.assert_quantity(result["offset_bound_j"], 3.21)
        # Mutant uses 20 W => 2.14 J, gap 1.07 / bar 3.21e-6 J:
        # >333,000 bars.

    def test_ols_return_widens_both_statistical_endpoints(self):
        """OLS itself expands its HC3/OLS endpoints outwards.

        Kills Ac2c4c25bf7, A7b840b5bc6. H2 overwrites these endpoints before
        serialization, so call OLS directly: its return contract is also used
        for response fits and sensitivity fits at separate H2 call sites.
        """
        fit = ba.ols([[1], [2], [3], [4]], [6, 6, 8, 12], family_size=1,
                     response_bounds=[.25, .5, .75, 1])
        # Independent slope=2 and support=.5 as above. Residuals [1,-1,-1,1]
        # give HC3 SE=10/7 and OLS SE=sqrt(2/5); the df=2 .975 quantile
        # solves F(t)=.5+t/(2*sqrt(t*t+2))=.975, so t²=722/39.
        for field, se in (("offset_intervals", 10/7),
                          ("offset_ols_intervals", math.sqrt(2/5))):
            with self.subTest(field=field):
                half = math.sqrt(722/39) * se
                self.assert_quantity(fit[field][1][0], 1.5 - half)
                self.assert_quantity(fit[field][1][1], 2.5 + half)
        # Either sign mutation moves the corresponding endpoint by 2*C=1
        # J/GB; largest endpoint bar <9e-6 J/GB: >110,000 bars.
