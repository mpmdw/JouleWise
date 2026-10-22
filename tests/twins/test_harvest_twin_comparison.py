"""Post-freeze comparisons; synthetic inputs only, no archived evidence reads."""

import random
import unittest
from decimal import Decimal
from pathlib import Path

from joulewise import calibration_bracketing as calibration
from joulewise import reduce as production
from joulewise import whole_window as ww
from joulewise.bundle_read import TracePoint, Window
from joulewise.idle_admission import Neg8BracketPolicy
from joulewise.twins.harvest_twin import (
    PowerInterval, ReferenceEnergy, SessionDrift, anchor_envelope, calibration_bracket,
    endpoint_bound, member_arithmetic, overlap_energy, session_drift,
)


BINDINGS = {"os_build": "synthetic", "power_supply_identity_sha256": "a" * 64,
            "calibration_identity_sha256": "b" * 64}


def production_drift(corpus, start, end, midpoint):
    artifact = ww.build_neg8_drift_bound_artifact(
        corpus_id="twin-synthetic", condition_id="synthetic", manifest_sha256="c" * 64,
        scientific_config_sha256="d" * 64,
        members=[{"bundle_id": f"r{i}", "point_gross_j": r.gross_j,
                  "point_idle_subtracted_j": r.idle_subtracted_j,
                  "bundle_evidence_sha256": "e" * 64} for i, r in enumerate(corpus)],
        derivation_timestamp_s=1000, freshness_bindings=BINDINGS)
    gross = lambda rs: [{"point_j": r.gross_j, "lower_j": r.gross_j - .01,
                          "upper_j": r.gross_j + .01} for r in rs]
    net = lambda rs: [r.idle_subtracted_j for r in rs]
    middle = [] if midpoint is None else [midpoint]
    return ww.evaluate_neg8_point_drift(
        gross(start), gross(end), Neg8BracketPolicy(True, 0, 0), artifact,
        start_idle_subtracted_j=net(start), end_idle_subtracted_j=net(end),
        midpoint_gross_j=gross(middle) or None,
        midpoint_idle_subtracted_j=net(middle) or None,
        bound_freshness_observation={"evaluated_at_s": 2000, "binding_status": "resolved",
                                     "bindings": BINDINGS},
        lost_references=[] if midpoint is not None and len(start) == len(end) == 3 else [
            {"bundle_id": "lost", "position": "midpoint", "reason": "member.timeout"}])


class ProductionComparison(unittest.TestCase):
    def near(self, a, b):
        # Joule columns have no printed half-width: DIFFICULTY revision 2.3
        # prescribes 1e-6 relative OR absolute in the column's unit (J).
        self.assertAlmostEqual(a, b, delta=max(1e-6, 1e-6 * max(abs(a), abs(b))))

    def near_seconds(self, a, b):
        # 54.531 ms prints in 1 us units: half-unit = 0.5 us; 1% = 5e-9 s.
        # 1e6 * ulp(0.068 s) ~= 1.4e-11 s < 1e-9 s < 5e-9 s.
        self.assertAlmostEqual(a, b, delta=1e-9)

    def test_b6_registered_minimum_disagrees_with_production(self):
        self.assertEqual(
            ww.NEG8_DRIFT_MINIMUM_N, 10,
            "A change means the B6-REPL 1.8 open item (registered 6, production 10) "
            "was acted on; update this test and PR #554's open-item list.")
        for n in range(6, 11):
            corpus = [ReferenceEnergy(37 + i * i / 100, 32 + i * i / 100)
                      for i in range(n)]
            for left in (2, 3):
                for right in (2, 3):
                    with self.subTest(n=n, start_n=left, end_n=right):
                        start = [ReferenceEnergy(37 + i / 100, 32 + i / 100)
                                 for i in range(left)]
                        end = [ReferenceEnergy(37.1 + i / 100, 32.1 + i / 100)
                               for i in range(right)]
                        middle = ReferenceEnergy(37.05, 32.05)
                        twin = session_drift(corpus, start, end, middle, block=6)
                        self.assertIsInstance(twin, SessionDrift)
                        if n < 10:
                            # The helper calls the real artifact builder first.
                            with self.assertRaisesRegex(ValueError, "n >= 10"):
                                production_drift(corpus, start, end, middle)
                            continue
                        main = production_drift(corpus, start, end, middle)
                        self.assertEqual(twin.passed, main["decision"] == "passed")
                        self.near(twin.member_drift_allowance_j,
                                  main["claim_families"][ww.NEG8_CLAIM_FAMILY_GROSS]
                                  ["drift_allowance_j"] / 2)
                        for name, family in ((ww.NEG8_CLAIM_FAMILY_GROSS, twin.gross),
                                             (ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED,
                                              twin.idle_subtracted)):
                            fresh = main["claim_families"][name]
                            for value, key in ((family.bound_j, "derived_repeatability_bound_j"),
                                               (family.difference_j, "point_delta_j"),
                                               (family.spread_j, "trajectory_excursion_max_j"),
                                               (family.allowance_j, "drift_allowance_j")):
                                self.near(value, fresh[key])
                            self.assertEqual(family.passed, fresh["screen_passed"])

    def test_anchor_refusal_agreement_reviewer_b3_b4(self):
        # Exact reviewer shapes: 131 ms interval supports, without edge nudges.
        edges = [k * .131 for k in range(200)]
        rows = [PowerInterval(a, b, 20 + i % 7)
                for i, (a, b) in enumerate(zip(edges, edges[1:]))]
        curve = [TracePoint(r.end_s, r.power_w, r.start_s, r.end_s) for r in rows]
        # g=45.7+0.3=46 ms, so 2g=92 ms and g+m=46+2=48 ms.
        # Refusals use strict reversal/coverage comparisons, with no edge bar.
        cases = [("B3", length, 10.0, 10.0 + length, length == .080)
                 for length in (.080, .092, .0921, .140)]
        cases += [("B4", margin, 20.0, edges[-1] - margin, margin < .048)
                  for margin in (.200, .048, .047, .020, 0.0)]
        for case, size, on, off, refuses in cases:
            with self.subTest(case=case, size_s=size):
                main = production._corner_composed_anchor_shift_envelope(
                    [(curve, [Window(on, off)])], .002, .0457, .0003)
                if refuses:
                    self.assertIsNone(main)
                    with self.assertRaises(ValueError):
                        anchor_envelope(rows, on, off, .0457, .0003, .002)
                else:
                    self.assertIsNotNone(main)
                    twin = anchor_envelope(rows, on, off, .0457, .0003, .002)
                    for value, key in ((twin.point_j, "point_j"),
                                       (twin.minimum_j, "lower_j"),
                                       (twin.maximum_j, "upper_j"),
                                       (twin.max_abs_delta_j, "max_abs_delta_j")):
                        self.near(value, main[key])

    def test_calibration_bracket_against_issued_b5_projection(self):
        # B5-REG 0.11's issued acceptance: derived from pre-block-5 captures and
        # quoted in the registration, so not blinded.
        root = Path(__file__).resolve().parents[2]
        acceptance = calibration.load_calibration_acceptance_bound(
            root / "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json")
        self.assertIsNotNone(acceptance)
        operatives = acceptance["decimal_derivation"]["ratified_operatives"]
        screen = Decimal(operatives["bracket_screen_s"])
        maximum = Decimal(operatives["maximum_budgetable_drift_s"])
        # Screen = the 24-capture range; ceiling = within-test two-draw Q99
        # (B5-REG 0.11). The screen is below the ceiling, so production's drift
        # check and the twin's registered allowance check are equivalent here.
        self.assertLess(screen, maximum)
        # Both drift directions, equal captures, below-screen and above-screen
        # brackets, all below the registered ceiling; includes B6-REPL 1.7.
        for pre_s, post_s in (("0.040", "0.030"), ("0.030", "0.030"),
                              ("0.031", "0.035"), ("0.030", "0.045"),
                              ("0.045", "0.030")):
            with self.subTest(pre_s=pre_s, post_s=post_s):
                main = calibration.issued_calibration_allowance_projection(
                    acceptance, pre_exact_bound_lexeme_s=pre_s,
                    post_exact_bound_lexeme_s=post_s)
                self.assertIsNotNone(main)
                twin = calibration_bracket(float(pre_s), float(post_s), float(screen),
                                           maximum_allowance_s=float(maximum))
                allowance = Decimal(main["applied_allowance_s"])
                operative = max(Decimal(pre_s), Decimal(post_s)) + allowance
                self.near_seconds(twin.observed_drift_s, float(main["observed_drift_s"]))
                self.near_seconds(twin.drift_allowance_s, float(allowance))
                self.near_seconds(twin.operative_fiducial_s, float(operative))
        self.assertIsNone(calibration.issued_calibration_allowance_projection(
            acceptance, pre_exact_bound_lexeme_s="0.030", post_exact_bound_lexeme_s="0.047"))
        with self.assertRaisesRegex(ValueError, "allowance exceeds maximum"):
            calibration_bracket(.030, .047, float(screen), maximum_allowance_s=float(maximum))

    def test_member_arithmetic_production_shaped_synthetic_members(self):
        rng = random.Random(5540)
        # Twelve members, six per origin: the sweep's physical ranges with two
        # phases each, bounded to keep tests/twins well below its ~30 s budget.
        for epoch in (0.0, 1790000000.0):
            for member in range(6):
                with self.subTest(epoch=epoch, member=member):
                    rows, cursor = [], epoch
                    # ~80 s idle/warm-up plus a request, 130.2-132.1 ms cadence.
                    for _ in range(900):
                        following = cursor + rng.uniform(.1302, .1321)
                        power = rng.uniform(2, 6) if cursor - epoch <= 80 else rng.uniform(15, 45)
                        rows.append(PowerInterval(cursor, following, power))
                        cursor = following
                    on = epoch + 82.0 + rng.uniform(0, .13)
                    prefill_end = on + rng.uniform(.15, .9)
                    off = prefill_end + rng.uniform(11, 23)
                    b_op, span, m = rng.uniform(.030, .068), rng.uniform(0, .001), rng.uniform(0, .005)
                    idle_w = rng.uniform(2, 6)
                    phases = {"prefill": (on, prefill_end), "decode": (prefill_end, off)}
                    twin = member_arithmetic(
                        rows, (on, off), phases, idle_power_w=idle_w,
                        operative_fiducial_s=b_op, wall_minus_monotonic_span_s=span,
                        effective_clock_bound_s=m, whole_window_drift_allowance_j=.6)
                    curve = [TracePoint(r.end_s, r.power_w, r.start_s, r.end_s) for r in rows]
                    gross = production._integrate(curve, on, off)
                    self.near(twin.gross_energy_j, gross)
                    # reduce.py:2958-2962 has no standalone net-energy function.
                    net = gross - idle_w * Window(on, off).duration_s
                    self.near(twin.idle_subtracted_energy_j, net)
                    for name, (phase_on, phase_off) in phases.items():
                        main = production._corner_composed_anchor_shift_envelope(
                            [(curve, [Window(phase_on, phase_off)])], m, b_op, span)
                        self.assertIsNotNone(main)
                        self.near(twin.phase_energy_j[name],
                                  production._integrate(curve, phase_on, phase_off))
                        self.near(twin.phase_bounds_j[name]["E_clock_anchor_shift_bound_j"],
                                  main["max_abs_delta_j"])

    def test_overlap_within_reader_tolerance_matches_production(self):
        # 1 ns is inside bundle_read's 1 us representation tolerance. Both
        # supports contribute: 5 W * (1 s + 1.000000001 s) = 10.000000005 J.
        rows = [PowerInterval(0, 1, 5), PowerInterval(1 - 1e-9, 2, 5)]
        curve = [TracePoint(r.end_s, r.power_w, r.start_s, r.end_s) for r in rows]
        self.near(overlap_energy(rows, 0, 2), 10.000000005)
        self.near(overlap_energy(rows, 0, 2), production._integrate(curve, 0, 2))

    def test_production_shaped_synthetic_sessions(self):
        rng = random.Random(20261022)
        for session in range(2):
            corpus = [ReferenceEnergy(37 + rng.uniform(-.5, .5),
                                      32 + rng.uniform(-.5, .5)) for _ in range(12)]
            start = [ReferenceEnergy(37 + rng.uniform(-.1, .1),
                                     32 + rng.uniform(-.1, .1)) for _ in range(3)]
            end = [ReferenceEnergy(37 + rng.uniform(-.1, .1),
                                   32 + rng.uniform(-.1, .1)) for _ in range(3 - session)]
            middle = ReferenceEnergy(37.5, 32.4) if session == 0 else None
            twin = session_drift(corpus, start, end, middle)
            main = production_drift(corpus, start, end, middle)
            self.assertEqual(twin.passed, main["decision"] == "passed")
            for family, result in ((ww.NEG8_CLAIM_FAMILY_GROSS, twin.gross),
                                   (ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED, twin.idle_subtracted)):
                fresh = main["claim_families"][family]
                self.near(result.bound_j, fresh["derived_repeatability_bound_j"])
                self.near(result.difference_j, fresh["point_delta_j"])
                self.near(result.allowance_j, fresh["drift_allowance_j"])
                self.assertEqual(result.passed, fresh["screen_passed"])
            # 100 science requests: ten repeats and ten four-member quads
            # for each of the two target phases, as in an ALPHA/BETA session.
            for member in range(100):
                epoch = 1790000000.0 if session else 0.0
                rows, cursor = [], epoch
                for _ in range(700):
                    following = cursor + rng.uniform(.1302, .1321)
                    rows.append(PowerInterval(cursor, following, rng.uniform(0, 45)))
                    cursor = following
                curve = [TracePoint(r.end_s, r.power_w, r.start_s, r.end_s) for r in rows]
                on, off = (78.017, 79.051) if member < 50 else (78.017, 88.051)
                on, off = epoch + on, epoch + off
                twin_env = anchor_envelope(rows, on, off, .0457, .0003, .002)
                main_env = production._corner_composed_anchor_shift_envelope(
                    [(curve, [Window(on, off)])], .002, .0457, .0003)
                for a, key in ((twin_env.point_j, "point_j"),
                               (twin_env.minimum_j, "lower_j"),
                               (twin_env.maximum_j, "upper_j"),
                               (twin_env.max_abs_delta_j, "max_abs_delta_j")):
                    self.near(a, main_env[key])

    def test_endpoint_bound_all_registered_sizes_and_survivor_counts(self):
        for n in range(6, 13):
            points = [37 + i * i / 100 for i in range(n)]
            for left in (2, 3):
                for right in (2, 3):
                    twin = endpoint_bound(points, left, right)
                    main = ww.neg8_count_adjusted_bound(points, left, right)
                    for a, key in zip(twin, ("envelope_j", "prediction_j", "bound_j")):
                        self.near(a, main[key])


if __name__ == "__main__":
    unittest.main()
