"""Lane L9-ENV-2: inverted corner windows clamp to zero length.

Ed's 2026-10-30 ruling: in ``_corner_composed_anchor_shift_envelope`` a
window shorter than ``2 * edge_bound_s`` inverts at the (+edge, -edge) corner;
it now becomes a zero-length window (0 J) instead of dropping the envelope.
The pre-ruling function is rebuilt from the current source by reversing only
that hunk and authenticated against the sealed pre-ruling digest, so every
comparison here is against the exact origin/main bytes.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import joulewise.reduce as reduce_module
from joulewise.bundle_read import TracePoint, Window
from joulewise.reduce import (
    _corner_composed_anchor_shift_envelope,
    _rederive_summary_for_authenticated_fiducial_bound,
)
from joulewise.whole_window import AuthenticatedConsumptionSession

ROOT = Path(__file__).resolve().parents[1]
PRE_RULING_SHA256 = (
    "7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc"
)
PRE_RULING_HUNK = """                if any(window.end_s < window.start_s for window in shifted_windows):
                    return None
                corner_contributions.append((curve, shifted_windows))
"""
RULING_HUNK = """                # Ed's 2026-10-30 ruling (lane L9-ENV-2): a window shorter
                # than 2*edge_bound inverts at the (+edge, -edge) corner.
                # The admissible set then contains an empty interval, so
                # with nonnegative power the true minimum contribution is
                # 0 J: clamp to a zero-length window at the shifted midpoint
                # (inside the original window) instead of dropping the
                # envelope.  Non-inverted windows are untouched.
                shifted_windows = [
                    Window(
                        start_s=(window.start_s + window.end_s) / 2.0,
                        end_s=(window.start_s + window.end_s) / 2.0,
                    )
                    if window.end_s < window.start_s
                    else window
                    for window in shifted_windows
                ]
                corner_contributions.append((curve, shifted_windows))
"""
PREFILL = "/phase_energy_j/prefill"
UNRECORDED = "anchor_energy_envelope_unrecorded"


def pre_ruling_source() -> bytes:
    current = (ROOT / "joulewise/reduce.py").read_text(encoding="utf-8")
    if current.count(RULING_HUNK) != 1:
        raise AssertionError("ruling hunk not found exactly once")
    return current.replace(RULING_HUNK, PRE_RULING_HUNK).encode("utf-8")


_PRE_RULING_MODULE = None


def pre_ruling_module():
    """origin/main's reduce.py, executed as a separate module."""

    global _PRE_RULING_MODULE
    if _PRE_RULING_MODULE is None:
        source = pre_ruling_source()
        if hashlib.sha256(source).hexdigest() != PRE_RULING_SHA256:
            raise AssertionError("reversed source is not the sealed bytes")
        name = "joulewise._reduce_pre_ruling_l9_env_2"
        spec = importlib.util.spec_from_loader(name, loader=None)
        module = importlib.util.module_from_spec(spec)
        module.__file__ = str(ROOT / "joulewise/reduce.py")
        sys.modules[name] = module
        exec(compile(source, "pre-ruling joulewise/reduce.py", "exec"), module.__dict__)
        _PRE_RULING_MODULE = module
    return _PRE_RULING_MODULE


def interval_curve(rows):
    return [
        TracePoint(t=(start + end) / 2.0, power_w=power, support_start_s=start, support_end_s=end)
        for start, end, power in rows
    ]


def point_curve(rows):
    return [TracePoint(t=t, power_w=power) for t, power in rows]


def stepped_rows(origin_s: float, count: int, width_s: float, seed: int):
    rows = []
    value = seed
    for index in range(count):
        value = (value * 1103515245 + 12345) % (2**31)
        power = 5.0 + (value % 9000) / 100.0
        rows.append((origin_s + index * width_s, origin_s + (index + 1) * width_s, power))
    return rows


class ClampEnvelopeTests(unittest.TestCase):
    def test_reversed_source_is_the_sealed_pre_ruling_bytes(self) -> None:
        self.assertEqual(hashlib.sha256(pre_ruling_source()).hexdigest(), PRE_RULING_SHA256)

    def test_non_inverted_windows_are_bit_identical_to_origin_main(self) -> None:
        # E2: every window with duration >= 2*edge_bound takes the unchanged
        # code path, so the envelope dict is equal float for float.
        old = pre_ruling_module()._corner_composed_anchor_shift_envelope
        cases = 0
        for origin_s in (0.0, 1_784_491_122.85):
            for seed in (1, 7, 42):
                rows = stepped_rows(origin_s - 1.0, 60, 0.05, seed)
                for make in (interval_curve, lambda r: point_curve(
                        [(start, power) for start, _end, power in r])):
                    curve = make(rows)
                    for fiducial_s, span_s, bundle_s in (
                        (0.0, 0.0, 0.0),
                        (0.02142716616057592, 8.106231689453125e-06, 0.0566),
                        (0.0665, 1e-05, 0.03),
                    ):
                        edge_s = fiducial_s + span_s
                        for factor in (1.0, 1.0 + 1e-9, 1.01, 1.5, 3.0, 10.0):
                            duration_s = max(2.0 * edge_s * factor, 0.0)
                            if duration_s == 0.0:
                                duration_s = 0.13 * factor
                            start_s = origin_s + 0.4
                            window = Window(start_s, start_s + duration_s)
                            # Inversion is decided in the function's
                            # anchor-relative coordinates; rounding can invert
                            # a nominal 2*edge_bound window, so skip those.
                            relative = curve[0].t
                            if (window.end_s - relative) - edge_s < (window.start_s - relative) + edge_s:
                                continue
                            for windows in ([window], [window, Window(start_s + 0.9, start_s + 1.4)]):
                                contributions = [(curve, windows)]
                                with self.subTest(origin=origin_s, seed=seed, factor=factor,
                                                  fiducial=fiducial_s, windows=len(windows)):
                                    self.assertEqual(
                                        _corner_composed_anchor_shift_envelope(
                                            contributions, bundle_s, fiducial_s, span_s),
                                        old(contributions, bundle_s, fiducial_s, span_s),
                                    )
                                    cases += 1
        self.assertGreater(cases, 300)

    def test_existing_reduce_corner_fixtures_are_bit_identical(self) -> None:
        # E2 over the committed corner fixtures of tests/test_reduce.py.
        old = pre_ruling_module()._corner_composed_anchor_shift_envelope
        fixtures = [
            ([(0.0, 0.5, 0.0), (0.5, 1.0, 100.0), (1.0, 1.5, 0.0)], [Window(0.5, 1.25)], 0.00005, 0.0, 0.0),
            ([(-1.0, 2.0, 10.0)], [Window(0.2, 0.8)], 0.0, 0.1, 0.0),
            ([(-1.0, 2.0, 10.0)], [Window(0.2, 0.8)], 0.0, 0.1, 0.05),
            ([(-1.0, 6.0, 10.0)], [Window(0.5, 4.35743)], 0.0, 0.01282, 0.0),
        ]
        for rows, windows, bundle_s, fiducial_s, span_s in fixtures:
            contributions = [(interval_curve(rows), windows)]
            new = _corner_composed_anchor_shift_envelope(contributions, bundle_s, fiducial_s, span_s)
            self.assertIsNotNone(new)
            self.assertEqual(new, old(contributions, bundle_s, fiducial_s, span_s))

    def test_inverted_corner_clamps_to_zero_energy(self) -> None:
        # E1 on a flat trace: lower = 0 J (empty interval admissible), point
        # unchanged, upper unaffected by the clamp; origin/main drops it.
        power_w, fiducial_s, span_s = 10.0, 0.1, 0.0
        curve = interval_curve([(-1.0, 2.0, power_w)])
        for duration_s in (0.19, 0.1, 1e-6):
            contributions = [(curve, [Window(0.5, 0.5 + duration_s)])]
            with self.subTest(duration=duration_s):
                self.assertIsNone(pre_ruling_module()._corner_composed_anchor_shift_envelope(
                    contributions, 0.0, fiducial_s, span_s))
                env = _corner_composed_anchor_shift_envelope(contributions, 0.0, fiducial_s, span_s)
                self.assertIsNotNone(env)
                self.assertEqual(env["lower_j"], 0.0)
                self.assertAlmostEqual(env["point_j"], power_w * duration_s, places=12)
                self.assertAlmostEqual(env["upper_j"], power_w * (duration_s + 2 * fiducial_s), places=12)
                self.assertLessEqual(env["lower_j"], env["point_j"])

    def test_clamped_bound_contains_every_admissible_window_energy(self) -> None:
        # Soundness: brute-force every admissible (eps_on, eps_off) on a grid
        # (non-inverted windows only, as physics requires) plus the common
        # shift; the clamped envelope contains them all.
        rows = stepped_rows(-1.0, 80, 0.025, 3)
        curve = interval_curve(rows)
        fiducial_s, span_s, bundle_s = 0.06, 0.004, 0.01
        edge_s = fiducial_s + span_s
        window = Window(0.3, 0.3 + 2 * edge_s * 0.8)
        env = _corner_composed_anchor_shift_envelope([(curve, [window])], bundle_s, fiducial_s, span_s)
        self.assertIsNotNone(env)
        grid = [edge_s * (k / 10.0) for k in range(-10, 11)]
        shifts = [bundle_s * (k / 4.0) for k in range(-4, 5)]
        for eps_on in grid:
            for eps_off in grid:
                start, end = window.start_s + eps_on, window.end_s + eps_off
                if end < start:
                    continue
                for delta in shifts:
                    energy = reduce_module._shift_energy_j([(curve, [Window(start, end)])], delta)
                    self.assertGreaterEqual(energy, env["lower_j"] - 1e-9)
                    self.assertLessEqual(energy, env["upper_j"] + 1e-9)

    def test_other_none_guards_are_unchanged(self) -> None:
        old = pre_ruling_module()._corner_composed_anchor_shift_envelope
        curve = interval_curve([(-1.0, 2.0, 10.0)])
        cases = [
            ([(curve, [Window(0.5, 0.6)])], None, 0.1, 0.0),
            ([(curve, [Window(0.5, 0.6)])], 0.0, math.nan, 0.0),
            ([(curve, [Window(0.5, 0.6)])], -1.0, 0.1, 0.0),
            ([(curve, [Window(0.5, 0.6)])], 0.0, 0.1, -1.0),
            ([], 0.0, 0.1, 0.0),
            ([(curve, [])], 0.0, 0.1, 0.0),
            ([([], [Window(0.5, 0.6)])], 0.0, 0.1, 0.0),
            ([(interval_curve([(-1.0, 2.0, -1.0)]), [Window(0.5, 0.6)])], 0.0, 0.1, 0.0),
            # trace support too short for the bundle bound
            ([(curve, [Window(0.5, 0.6)])], 5.0, 0.1, 0.0),
        ]
        for args in cases:
            with self.subTest(args=args[1:]):
                self.assertIsNone(_corner_composed_anchor_shift_envelope(*args))
                self.assertIsNone(old(*args))


def _bundle_fixture(test: unittest.TestCase, root: Path):
    from tests.test_whole_window_selection import (
        MaxBracketConsumptionTests,
        _install_synthetic_calibration_defaults,
    )

    _install_synthetic_calibration_defaults(test)
    root.mkdir(parents=True, exist_ok=True)
    bundle, minted, minted_bound, _operative = MaxBracketConsumptionTests._build_v052_bundle(root)
    return MaxBracketConsumptionTests, bundle, minted, minted_bound


def _origin_main_mint(bundle: Path, cache: dict) -> dict:
    # What the block-5 nights stored: minted by the pre-ruling reducer.
    return pre_ruling_module().reduce_bundle(
        bundle, reducer_version="0.5.2", _instrument_calibration_physics_cache=cache).to_dict()


def _phase_durations(summary: dict) -> dict[str, float]:
    return {
        phase: record["windows"][0]["window_duration_s"]
        for phase, record in summary["window_evidence_precheck"]["phase"].items()
    }


class PermanentWideningCaseTests(unittest.TestCase):
    """E3: operative bound dominates the minted bound; short prefill.

    The step under test is whole_window's minted-vs-operative envelope
    coverage.  The retained powermetrics fixture (0.4 s request) fails
    metric-scale prechecks and member-era capture checks at a 66 ms bound
    for reasons the ruling does not touch, so the session member is the
    existing synthetic-session shape (tests/test_whole_window_selection.py)
    carrying the REAL minted summary, and the re-derivation returns the REAL
    origin/main or post-ruling operative summary.  The global precheck
    classification of both operative summaries is asserted equal before it
    is neutralised, so neutralising it cannot hide an effect of the clamp.
    """

    _cache: dict[str, float] = {}

    def _bounds(self, minted: dict, minted_bound: float) -> tuple[float, float]:
        span_s = minted["energy_anchor_shift_envelopes"][PREFILL][
            "wall_minus_monotonic_independent_edge_span_s"]
        duration_s = _phase_durations(minted)["prefill"]
        # the minted edge bound is far below half the prefill duration
        self.assertLess(2.0 * (minted_bound + span_s), duration_s)
        just_under = duration_s / 2.0 - span_s + 0.002  # duration < 2*edge_bound
        just_over = duration_s / 2.0 - span_s - 0.002   # duration > 2*edge_bound
        return just_under, just_over

    def _rederive_both(self, bundle: Path, bound_s: float) -> tuple[dict, dict]:
        old = pre_ruling_module()._rederive_summary_for_authenticated_fiducial_bound(
            bundle, authenticated_fiducial_bound_s=bound_s,
            _instrument_calibration_physics_cache=self._cache)
        new = _rederive_summary_for_authenticated_fiducial_bound(
            bundle, authenticated_fiducial_bound_s=bound_s,
            _instrument_calibration_physics_cache=self._cache)
        self.assertEqual(old["status"], "succeeded")
        self.assertEqual(new["status"], "succeeded")
        from joulewise.whole_window import _classify_precheck_refusals

        self.assertEqual(_classify_precheck_refusals(old)[0], _classify_precheck_refusals(new)[0])
        return old, new

    def _session(self, root: Path, minted: dict, minted_bound: float, operative_bound: float,
                 operative: dict):
        from tests.test_whole_window_selection import MaxBracketConsumptionTests
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3

        member = root / "member"
        member.mkdir(parents=True, exist_ok=True)
        (member / "summary_metrics.json").write_text(json.dumps(minted) + "\n", encoding="utf-8")
        (member / "metadata.json").write_text(json.dumps({
            "instrument_calibration": {"verified_effective_b_fiducial_s": minted_bound},
            "uncertainty_evidence": {"clock_anchor": {"method": CLOCK_METHOD_V3}},
        }) + "\n", encoding="utf-8")
        session = AuthenticatedConsumptionSession(root, {"member"})
        with (
            patch("joulewise.whole_window.calibration_bracket_for_bundles",
                  return_value=(MaxBracketConsumptionTests._bracket(operative_bound), ())),
            patch("joulewise.whole_window._current_strict_summary", return_value=True),
            patch("joulewise.whole_window._verify_instrument_calibration",
                  return_value=(minted_bound, None)),
            patch("joulewise.whole_window._classify_precheck_refusals",
                  return_value=(set(), {})),
            patch("joulewise.whole_window._rederive_summary_for_authenticated_fiducial_bound",
                  return_value=operative) as rederive,
        ):
            session._prepare(bundle_paths={"member": member},
                             policy=SimpleNamespace(calibration_bracketing=object()))
        self.assertEqual(rederive.call_args.kwargs["authenticated_fiducial_bound_s"], operative_bound)
        return session

    def test_short_prefill_under_dominating_bound(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _helper, bundle, minted, minted_bound = _bundle_fixture(self, root / "fixture")
            just_under, _over = self._bounds(minted, minted_bound)
            old_summary, new_summary = self._rederive_both(bundle, just_under)
            minted_prefill = minted["energy_anchor_shift_envelopes"][PREFILL]

            old_mint = _origin_main_mint(bundle, self._cache)
            # Counterfactual at origin/main: the prefill envelope is dropped
            # and the session refuses globally.
            self.assertNotIn(PREFILL, old_summary["energy_anchor_shift_envelopes"])
            old_session = self._session(root / "old", old_mint, minted_bound, just_under, old_summary)
            self.assertFalse(old_session.ready)
            self.assertEqual(old_session.refusal_reasons, (UNRECORDED,))

            # After the ruling: the envelope exists, covers the minted one,
            # keeps the point estimate, and the session is ready.
            prefill = new_summary["energy_anchor_shift_envelopes"][PREFILL]
            self.assertEqual(prefill["point_j"], minted_prefill["point_j"])
            self.assertEqual(prefill["lower_j"], 0.0)
            self.assertLessEqual(prefill["lower_j"], minted_prefill["lower_j"])
            self.assertGreaterEqual(prefill["upper_j"], minted_prefill["upper_j"])
            self.assertAlmostEqual(prefill["anchor_bound_s"] - minted_prefill["anchor_bound_s"],
                                   just_under - minted_bound, places=12)
            # every pointer origin/main produced is exactly origin/main's value
            for pointer, envelope in old_summary["energy_anchor_shift_envelopes"].items():
                self.assertEqual(new_summary["energy_anchor_shift_envelopes"][pointer], envelope)
            # Block-5 shape (summaries minted at origin/main, re-derived after
            # the ruling) and future-night shape (both after the ruling).
            for name, mint in (("block5", old_mint), ("new", minted)):
                with self.subTest(mint=name):
                    session = self._session(root / name, mint, minted_bound, just_under, new_summary)
                    self.assertTrue(session.ready, session.refusal_reasons)
                    self.assertEqual(
                        session.provenance_for("member")["operative_envelopes"][PREFILL]["lower_j"], 0.0)

    def test_prefill_just_over_twice_edge_bound_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _helper, bundle, minted, minted_bound = _bundle_fixture(self, root / "fixture")
            _under, just_over = self._bounds(minted, minted_bound)
            old_summary, new_summary = self._rederive_both(bundle, just_over)
            self.assertIn(PREFILL, old_summary["energy_anchor_shift_envelopes"])
            self.assertEqual(new_summary["energy_anchor_shift_envelopes"][PREFILL],
                             old_summary["energy_anchor_shift_envelopes"][PREFILL])
            old_mint = _origin_main_mint(bundle, self._cache)
            for name, mint, summary in (("old", old_mint, old_summary), ("block5", old_mint, new_summary),
                                        ("new", minted, new_summary)):
                with self.subTest(case=name):
                    session = self._session(root / name, mint, minted_bound, just_over, summary)
                    self.assertTrue(session.ready, session.refusal_reasons)

    def test_genuinely_missing_operative_envelope_still_refuses(self) -> None:
        # Counterfactual: a pointer absent for a reason other than inversion
        # still fails coverage with anchor_energy_envelope_unrecorded.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _helper, bundle, minted, minted_bound = _bundle_fixture(self, root / "fixture")
            just_under, _over = self._bounds(minted, minted_bound)
            _old, new_summary = self._rederive_both(bundle, just_under)
            for pointer in (PREFILL, "/gross_energy_j"):
                with self.subTest(pointer=pointer):
                    summary = json.loads(json.dumps(new_summary))
                    summary["energy_anchor_shift_envelopes"].pop(pointer)
                    session = self._session(root / pointer.replace("/", "_"), minted,
                                            minted_bound, just_under, summary)
                    self.assertFalse(session.ready)
                    self.assertEqual(session.refusal_reasons, (UNRECORDED,))

    def test_mint_differs_from_origin_main_only_on_inverting_phases(self) -> None:
        # E2 on a full reduce_bundle mint: every envelope origin/main records
        # is bit-identical; the only differences are newly defined envelopes
        # (lower_j == 0) for phases shorter than 2*edge_bound, and their
        # metric-local precheck reason moving from *_unrecorded to the
        # quarter-metric test the envelope now feeds.
        with tempfile.TemporaryDirectory() as tmp:
            _helper, bundle, minted, minted_bound = _bundle_fixture(self, Path(tmp))
            old = _origin_main_mint(bundle, self._cache)
        edge_s = minted_bound + minted["energy_anchor_shift_envelopes"][PREFILL][
            "wall_minus_monotonic_independent_edge_span_s"]
        inverting = {phase for phase, duration in _phase_durations(minted).items()
                     if duration < 2.0 * edge_s}
        self.assertEqual(inverting, {"generation_setup", "tokenize"})
        old_env, new_env = old["energy_anchor_shift_envelopes"], minted["energy_anchor_shift_envelopes"]
        for pointer, envelope in old_env.items():
            self.assertEqual(new_env[pointer], envelope)
        self.assertEqual(set(new_env) - set(old_env),
                         {"/phase_energy_j/" + phase for phase in inverting})
        for phase in inverting:
            self.assertEqual(new_env["/phase_energy_j/" + phase]["lower_j"], 0.0)
            for record in (old["window_evidence_precheck"]["phase"][phase],
                           minted["window_evidence_precheck"]["phase"][phase]):
                self.assertFalse(record["eligible"])
            old_reasons = set(old["window_evidence_precheck"]["phase"][phase]["reasons"])
            new_reasons = set(minted["window_evidence_precheck"]["phase"][phase]["reasons"])
            self.assertEqual(old_reasons - new_reasons, {UNRECORDED})
            self.assertLessEqual(new_reasons - old_reasons, {"anchor_energy_envelope_exceeds_quarter_metric"})
        trimmed_old, trimmed_new = json.loads(json.dumps(old)), json.loads(json.dumps(minted))
        for summary in (trimmed_old, trimmed_new):
            for phase in inverting:
                summary["energy_anchor_shift_envelopes"].pop("/phase_energy_j/" + phase, None)
                summary["window_evidence_precheck"]["phase"].pop(phase)
        self.assertEqual(json.dumps(trimmed_new, sort_keys=True), json.dumps(trimmed_old, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
