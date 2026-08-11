"""FCM-01 round-4 ACCEPTANCE ORACLE (authored by the cold gate's oracle author).

The implementer of round 4 MAY NOT EDIT THIS FILE. It is the acceptance bar,
authored before implementation under the gate's oracle-authorship separation.

It asserts the registered semantics of `r4_oracle_spec.md`:

  * the zero-shift contrast `z` is an EXPLICIT registered input, present in
    both sweeps by exact equality, never recovered by tolerance matching;
  * the width is composed as EXCURSIONS about `z`, with `|z - d|` added
    outward exactly once, and the `64u*S_env` enclosure UNCHANGED;
  * a mismatch beyond `isclose(z, d, rel_tol=1e-9, abs_tol=1e-12)` REFUSES
    with the typed gross-divergence reason;
  * BOTH semantic bars hold independently, in exact rational arithmetic;
  * the emitted width does not overstate beyond the declared budget;
  * the candidate-(3) trap formula (shipped arithmetic + |z-d|) FAILS,
    committed as a named negative regression.

DECLARED SIGNATURE the implementer conforms to (see r4_oracle_spec.md Sec 6):

    two_shared_edge_common_mode_floor(
        block_deltas_j, *,
        onset_sweeps_j, offset_sweeps_j,
        zero_point_contrasts_j,               # NEW, REQUIRED
        bundle_residual_half_widths_j,
        member_window_bounds_s=None,
        member_envelope_integral_sums_j=None,
        calibration_bracket, shared_edge_bound_s,
    ) -> FloorEstimate

If the magistrate renames the new keyword, change ZERO_POINT_KWARG below and
nothing else.
"""

from __future__ import annotations

import math
import random
import unittest
from fractions import Fraction

from joulewise import detection_floor
from joulewise.detection_floor import CommonModeEstimatorRefusal
from joulewise.floor_extraction import CELL_REFUSAL_CODES

# --------------------------------------------------------------------------
# Declared contract constants
# --------------------------------------------------------------------------
ZERO_POINT_KWARG = "zero_point_contrasts_j"
GROSS_DIVERGENCE_REASON = "common_mode_zero_point_divergence_out_of_domain"
PRECONDITION_REASON = "common_mode_precondition_failed"

REL_TOL = 1e-9
ABS_TOL = 1e-12
PAD_COEFFICIENT = 64.0
U = 2.0 ** -53                      # ulp(1.0) / 2
OUTWARD_STEPS = 4

# Runtime-bounded case counts (measured: see the module docstring of the
# authoring report; the whole module runs well under 60 s on CPython 3.13).
RANDOM_CASES = 25000
RANDOM_SEED = 0xFC0142

F = Fraction.from_float


# --------------------------------------------------------------------------
# Exact-arithmetic bars (the oracle proper -- no float shortcuts)
# --------------------------------------------------------------------------
def _exc_bounds_exact(onset, offset, zero):
    """Exact signed excursion envelope about the sweep zero point."""
    z = F(zero)
    lo = (F(min(onset)) - z) + (F(min(offset)) - z)
    hi = (F(max(onset)) - z) + (F(max(offset)) - z)
    return lo, hi


def bar_about_zero_exact(onset, offset, zero):
    """BAR 1 -- the excursion composition the estimator claims to compute."""
    lo, hi = _exc_bounds_exact(onset, offset, zero)
    return max(abs(lo), abs(hi))


def bar_about_delta_exact(onset, offset, zero, delta):
    """BAR 2 -- what the consumer needs: a half-width about `delta` covering
    every admissible value ``v = z + exc``.  Exact, and independent of BAR 1."""
    lo, hi = _exc_bounds_exact(onset, offset, zero)
    m = F(zero) - F(delta)
    return max(abs(lo + m), abs(hi + m))


def s_env_floored(envelope_sum, delta, zero, onset, offset):
    """The declared scale reference (spec Sec 2.1)."""
    return max(
        float(envelope_sum),
        1.0,
        abs(delta),
        abs(zero),
        *(abs(v) for v in onset),
        *(abs(v) for v in offset),
    )


def pad_for(envelope_sum, delta, zero, onset, offset):
    """The declared enclosure (spec Sec 2.2) -- UNCHANGED from round 3."""
    return PAD_COEFFICIENT * U * s_env_floored(
        envelope_sum, delta, zero, onset, offset
    )


def _outward(value, direction):
    for _ in range(OUTWARD_STEPS):
        value = math.nextafter(value, direction)
    return value


def trap_candidate3_width(delta, onset, offset, zero, envelope_sum):
    """The REFUTED candidate-(3) formula: round-3 arithmetic (centred on
    `delta`) plus `|delta - zero|` added once.  Committed so that no future
    round re-derives it.  It is unsound because the mismatch enters the
    composition twice but is compensated once."""
    pad = pad_for(envelope_sum, delta, zero, onset, offset)
    lower = _outward(
        math.fsum((min(onset), min(offset), -delta, -pad)), -math.inf
    )
    upper = _outward(
        math.fsum((max(onset), max(offset), -delta, pad)), math.inf
    )
    shared = _outward(max(delta - lower, upper - delta), math.inf)
    return _outward(math.fsum((shared, abs(delta - zero))), math.inf)


# --------------------------------------------------------------------------
# Harness
# --------------------------------------------------------------------------
def bracket(bound_s):
    """A minimally authentic D-102 bracket with the allowance embedded once."""
    return {
        "status": "passed",
        "endpoint_max_b_fiducial_s": 0.0,
        "calibration_drift_allowance_s": bound_s,
        "b_fiducial_s": bound_s,
        "acceptance": {
            "allowance": {
                "rule": "max(observed_drift_s,bracket_screen_s)",
                "value_s": repr(bound_s),
                "embedding_count": 1,
                "embedded_in": "b_fiducial_s",
            }
        },
    }


def safe_windows(n_blocks, bound_s):
    """Member windows comfortably inside the strict-noncollapse domain."""
    span = max(1.0, 8.0 * bound_s)
    return [[(0.0, span)] * 4 for _ in range(n_blocks)]


def emit(
    deltas,
    onsets,
    offsets,
    zeros,
    envelopes,
    bound_s,
    residuals=None,
):
    """Invoke the registered estimator under its declared signature."""
    n = len(deltas)
    if residuals is None:
        residuals = [[0.0, 0.0, 0.0, 0.0] for _ in range(n)]
    kwargs = {
        "onset_sweeps_j": onsets,
        "offset_sweeps_j": offsets,
        "bundle_residual_half_widths_j": residuals,
        "member_window_bounds_s": safe_windows(n, bound_s),
        "member_envelope_integral_sums_j": envelopes,
        "calibration_bracket": bracket(bound_s),
        "shared_edge_bound_s": bound_s,
        ZERO_POINT_KWARG: zeros,
    }
    return detection_floor.two_shared_edge_common_mode_floor(deltas, **kwargs)


def emit_one(delta, onset, offset, zero, envelope_sum, bound_s, residual=None):
    """Two identical blocks (the estimator needs n>=2); return block 0's width."""
    residuals = None if residual is None else [list(residual), list(residual)]
    estimate = emit(
        [delta, delta],
        [list(onset), list(onset)],
        [list(offset), list(offset)],
        [zero, zero],
        [envelope_sum, envelope_sum],
        bound_s,
        residuals=residuals,
    )
    return estimate.admissible_half_widths_j[0]


def sweeps_containing(zero, downward, upward):
    """Build sweeps whose zero-shift entry is EXACTLY `zero`."""
    onset = sorted({zero, zero - downward, zero + upward})
    offset = sorted({zero, zero - downward * 0.5, zero + upward * 0.5})
    return onset, offset


def just_beyond_tolerance(delta, sign):
    """Smallest representable mismatch that `isclose` rejects."""
    z = delta + sign * max(REL_TOL * abs(delta), ABS_TOL)
    guard = 0
    while math.isclose(z, delta, rel_tol=REL_TOL, abs_tol=ABS_TOL):
        z = math.nextafter(z, sign * math.inf)
        guard += 1
        if guard > 4096:
            raise AssertionError("could not step beyond the admission band")
    return z


# --------------------------------------------------------------------------
# The oracle
# --------------------------------------------------------------------------
class R4RegisteredSemanticsOracle(unittest.TestCase):
    """Acceptance bar for the round-4 excursion-composition repair."""

    BOUND_S = 0.1

    # -- Sec 3.1 ---------------------------------------------------------
    def test_zero_point_is_explicit_and_checked_by_exact_presence(self):
        """`z` must be present in BOTH sweeps by exact equality.

        A zero point that is merely *close* to a sweep entry must refuse:
        the whole defect class of round 3 was recovering this structural
        fact by tolerance.
        """
        delta = 0.25
        zero = delta
        onset, offset = sweeps_containing(zero, 0.4, 0.1)
        # sanity: the honest construction is admitted
        self.assertGreater(
            emit_one(delta, onset, offset, zero, 100.0, self.BOUND_S), 0.0
        )

        for label, mangled_on, mangled_off in (
            (
                "onset lacks the zero point",
                [math.nextafter(v, math.inf) if v == zero else v for v in onset],
                offset,
            ),
            (
                "offset lacks the zero point",
                onset,
                [math.nextafter(v, math.inf) if v == zero else v for v in offset],
            ),
        ):
            with self.subTest(label):
                with self.assertRaises(CommonModeEstimatorRefusal) as caught:
                    emit_one(
                        delta, mangled_on, mangled_off, zero, 100.0, self.BOUND_S
                    )
                self.assertEqual(caught.exception.reason, PRECONDITION_REASON)

    # -- Sec 3.2 ---------------------------------------------------------
    def test_gross_divergence_beyond_tolerance_refuses_with_typed_reason(self):
        """Just beyond the admission band, the estimator must REFUSE."""
        self.assertIn(
            GROSS_DIVERGENCE_REASON, detection_floor.COMMON_MODE_REFUSAL_CODES
        )
        for delta in (0.2, -0.2, 1.0, 137.5, 1e-6):
            for sign in (+1.0, -1.0):
                with self.subTest(delta=delta, sign=sign):
                    zero = just_beyond_tolerance(delta, sign)
                    onset, offset = sweeps_containing(
                        zero, 0.4 * max(abs(delta), 1.0), 0.1 * max(abs(delta), 1.0)
                    )
                    with self.assertRaises(CommonModeEstimatorRefusal) as caught:
                        emit_one(delta, onset, offset, zero, 1000.0, self.BOUND_S)
                    self.assertEqual(
                        caught.exception.reason, GROSS_DIVERGENCE_REASON
                    )

    def test_gross_divergence_reason_is_in_the_cell_refusal_registry(self):
        """D-078: every estimator refusal must be a registered cell reason."""
        self.assertIn(GROSS_DIVERGENCE_REASON, CELL_REFUSAL_CODES)

    # -- Sec 2, both bars, over the dictated mismatch grid ----------------
    def test_mismatch_grid_admits_and_satisfies_both_bars(self):
        """`delta` perturbed INDEPENDENTLY of the sweeps' zero point.

        Mismatches span 0, +/-abs_tol, and +/-{0.25, 0.9, 1-ulp} x rel_tol x
        |delta|, both signs. Every one is inside the admission band, so every
        one must be ADMITTED and satisfy BOTH exact bars.
        """
        fractions_of_rel = (0.25, 0.9, 1.0 - 2.0 ** -52)
        for delta in (0.2, -0.2, 1.0, -137.5, 1e-6, 5e4):
            budget = REL_TOL * abs(delta)
            offsets = [0.0, ABS_TOL, -ABS_TOL]
            offsets += [s * f * budget for f in fractions_of_rel for s in (1, -1)]
            for mismatch in offsets:
                zero = delta + mismatch
                if not math.isclose(zero, delta, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                    continue  # abs_tol step can exceed the band for tiny delta
                scale = max(abs(delta), 1.0)
                onset, offset = sweeps_containing(zero, 0.4 * scale, 0.11 * scale)
                envelope = 200.0 * scale
                with self.subTest(delta=delta, mismatch=mismatch):
                    width = emit_one(
                        delta, onset, offset, zero, envelope, self.BOUND_S
                    )
                    self._assert_both_bars(
                        width, delta, onset, offset, zero, envelope
                    )

    # -- Sec 2, overstatement cap ----------------------------------------
    def test_overstatement_is_capped_by_the_declared_budget(self):
        """The enclosure must be conservative, not unboundedly generous.

        emitted - BAR1 <= pad + |z - d| + the outward-step slack.
        """
        for delta in (0.2, -1.0, 137.5):
            zero = delta + 0.5 * REL_TOL * abs(delta)
            scale = max(abs(delta), 1.0)
            onset, offset = sweeps_containing(zero, 0.4 * scale, 0.11 * scale)
            envelope = 200.0 * scale
            with self.subTest(delta=delta):
                width = emit_one(
                    delta, onset, offset, zero, envelope, self.BOUND_S
                )
                exact = bar_about_zero_exact(onset, offset, zero)
                pad = pad_for(envelope, delta, zero, onset, offset)
                slack = 8 * OUTWARD_STEPS * math.ulp(max(1.0, width))
                cap = F(pad) + (F(zero) - F(delta) if zero >= delta
                                else F(delta) - F(zero)) + F(slack)
                self.assertLessEqual(
                    F(width) - exact,
                    cap,
                    f"overstatement {float(F(width) - exact)} exceeds cap "
                    f"{float(cap)}",
                )

    # -- Sec 2.5 ---------------------------------------------------------
    def test_bundle_residuals_are_added_not_swallowed(self):
        """`local = fsum(r)/2` must still compose onto the shared width."""
        delta = 0.2
        zero = delta
        onset, offset = sweeps_containing(zero, 0.4, 0.11)
        bare = emit_one(delta, onset, offset, zero, 200.0, self.BOUND_S)
        residual = (0.05, 0.07, 0.0, 0.11)
        loaded = emit_one(
            delta, onset, offset, zero, 200.0, self.BOUND_S, residual=residual
        )
        self.assertGreaterEqual(
            F(loaded), F(bare) + F(math.fsum(residual) / 2.0) - F(
                8 * OUTWARD_STEPS * math.ulp(max(1.0, loaded))
            ),
        )

    # -- the round-3 counterexample --------------------------------------
    def test_fcm_r3_01_counterexample_is_covered(self):
        """The exact FCM-R3-01 case must now be covered on both bars.

        Executed at df42bcd: emitted 0.09999999950000743 against a required
        0.10000000050000024 -- an exact-arithmetic understatement of
        9.999928e-10 J at an input every coded precondition admitted.
        """
        delta = 1.0
        zero = 1.0000000005000003
        onset = [0.9, zero, 1.01]
        offset = [zero, zero]
        envelope = 1.0
        self.assertTrue(
            math.isclose(zero, delta, rel_tol=REL_TOL, abs_tol=ABS_TOL),
            "the counterexample must sit INSIDE the admission band",
        )
        width = emit_one(delta, onset, offset, zero, envelope, self.BOUND_S)
        self._assert_both_bars(width, delta, onset, offset, zero, envelope)

    # -- NEGATIVE regression: the refuted candidate (3) -------------------
    def test_candidate3_trap_formula_is_refuted_and_stays_refuted(self):
        """Committed so no future round re-derives the intuitive repair.

        Candidate (3) -- round-3 arithmetic centred on `delta`, plus
        `|delta - zero|` added once -- FAILS BAR 1 on the FCM-R3-01 case,
        because the mismatch enters the composition twice and is compensated
        once. It passes BAR 2, which is exactly why BOTH bars are asserted
        independently.
        """
        delta = 1.0
        zero = 1.0000000005000003
        onset = [0.9, zero, 1.01]
        offset = [zero, zero]
        envelope = 1.0

        trap = trap_candidate3_width(delta, onset, offset, zero, envelope)
        bar1 = bar_about_zero_exact(onset, offset, zero)
        bar2 = bar_about_delta_exact(onset, offset, zero, delta)

        # the numbers from the refuter's report, pinned
        self.assertAlmostEqual(trap, 0.10000000000000775, places=17)
        self.assertAlmostEqual(float(bar1), 0.10000000050000024, places=17)

        self.assertLess(
            F(trap), bar1, "the trap formula must FAIL the about-zero bar"
        )
        self.assertGreaterEqual(
            F(trap), bar2, "the trap formula passes the about-delta bar alone"
        )

        # and the registered implementation must NOT be the trap
        width = emit_one(delta, onset, offset, zero, envelope, self.BOUND_S)
        self.assertGreaterEqual(F(width), bar1)

    # -- distilled randomized generator ----------------------------------
    def test_randomized_adversarial_magnitudes_satisfy_both_bars(self):
        """Fixed-seed distillation of the refuter's 300k-draw sweep.

        Adversarial magnitudes 1e-2..1e5, near-total cancellation, and
        mismatches drawn across the whole admission band in both signs.
        """
        rng = random.Random(RANDOM_SEED)
        checked = 0
        for _ in range(RANDOM_CASES):
            magnitude = rng.choice((1e-2, 1.0, 1e2, 1e4, 1e5))
            # near-total cancellation: delta tiny against member magnitudes
            delta = magnitude * rng.choice((1e-9, 1e-6, 1e-3, 1.0)) * rng.choice(
                (1.0, -1.0)
            )
            if delta == 0.0:
                continue
            band = max(REL_TOL * abs(delta), ABS_TOL)
            mismatch = rng.uniform(-1.0, 1.0) * band * rng.choice(
                (0.0, 0.25, 0.5, 0.9, 1.0 - 2.0 ** -52)
            )
            zero = delta + mismatch
            if not math.isclose(zero, delta, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                continue
            span = abs(zero) * rng.uniform(1e-9, 0.5) + magnitude * 1e-12
            onset = sorted({zero} | {
                zero + span * rng.uniform(-1.0, 1.0)
                for _ in range(rng.randrange(1, 5))
            })
            offset = sorted({zero} | {
                zero + span * rng.uniform(-1.0, 1.0)
                for _ in range(rng.randrange(1, 5))
            })
            envelope = magnitude * rng.uniform(1.0, 200.0)
            width = emit_one(delta, onset, offset, zero, envelope, self.BOUND_S)
            self._assert_both_bars(
                width, delta, onset, offset, zero, envelope, quiet=True
            )
            checked += 1
        self.assertGreater(checked, RANDOM_CASES // 2, "generator degenerated")

    # -- shared assertion -------------------------------------------------
    def _assert_both_bars(
        self, width, delta, onset, offset, zero, envelope, quiet=False
    ):
        """BOTH registered bars, asserted INDEPENDENTLY in exact arithmetic."""
        bar1 = bar_about_zero_exact(onset, offset, zero)
        bar2 = bar_about_delta_exact(onset, offset, zero, delta)
        context = "" if quiet else (
            f"\n  delta={delta!r}\n  zero={zero!r}\n  onset={onset!r}"
            f"\n  offset={offset!r}\n  envelope={envelope!r}"
        )
        self.assertGreaterEqual(
            F(width),
            bar1,
            f"BAR 1 (excursion composition about z) understated by "
            f"{float(bar1 - F(width))} J{context}",
        )
        self.assertGreaterEqual(
            F(width),
            bar2,
            f"BAR 2 (delta-centred requirement) understated by "
            f"{float(bar2 - F(width))} J{context}",
        )


if __name__ == "__main__":
    unittest.main()
