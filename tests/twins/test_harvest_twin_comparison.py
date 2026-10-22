"""Post-freeze comparisons; synthetic inputs only, no archived evidence reads."""

import random
import unittest

from joulewise import reduce as production
from joulewise import whole_window as ww
from joulewise.bundle_read import TracePoint, Window
from joulewise.idle_admission import Neg8BracketPolicy
from joulewise.twins.harvest_twin import (
    PowerInterval, ReferenceEnergy, anchor_envelope, endpoint_bound, session_drift,
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
        # These machine-readable columns have no printed precision: COMMON's
        # fallback relative 1e-6. Identically zero arithmetic stays zero.
        self.assertAlmostEqual(a, b, delta=1e-6 * max(abs(a), abs(b)))

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
