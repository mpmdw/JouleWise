"""Lane L9-ENV-3: analysis-only clamp of inverted corner windows.

Ed's 2026-10-30 ruling: ``joulewise/reduce.py`` stays byte-identical to
origin/main; the clamp of L9-ENV-2 (an inverted shifted corner window becomes
zero-length and contributes 0 J) applies only to whole_window's operative
re-derivation.  The oracle is L9-ENV-2's patched function (e1b3a0510), vendored
in ``tests/oracle_l9_env_2_reduce_clamp.py``; substituting it into origin/main's
reduce.py must rebuild exactly the e1b3a0510 file bytes.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import joulewise.reduce as reduce_module
import joulewise.whole_window as whole_window
from joulewise.bundle_read import TracePoint, Window
from joulewise.calibration_bracketing import (
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    ESTIMATOR_CODE_PATHS,
    _current_estimator_code_sha256,
)
from joulewise.whole_window import (
    AuthenticatedConsumptionSession,
    _clamp_inverted_operative_envelopes,
    _clamped_corner_composed_anchor_shift_envelope,
    _rederive_operative_summary,
)

ROOT = Path(__file__).resolve().parents[1]
ORACLE_PATH = ROOT / "tests/oracle_l9_env_2_reduce_clamp.py"
FUNCTION = "_corner_composed_anchor_shift_envelope"
# origin/main 7ebb7db (the ruling's base): reduce.py and the other three
# calibration ESTIMATOR_CODE_PATHS, which the live acceptance pins.
ORIGIN_MAIN_SHA256 = {
    "joulewise/powermetrics_fiducial.py": (
        "bcdfeec06a03525cc6f6c700f2e2e6d10341af1323e4f9355b68ee47eb5bd30c"
    ),
    "joulewise/uncertainty_evidence.py": (
        "b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8"
    ),
    "joulewise/adapters/powermetrics.py": (
        "70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4"
    ),
    "joulewise/reduce.py": (
        "7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc"
    ),
}
FROZEN_FILES_TEST_SHA256 = (
    "523f4ee386efc143fee98843104f60b2a9137d58083c17bcb0d5e7b325a4e19d"
)
PREFILL = "/phase_energy_j/prefill"
UNRECORDED = "anchor_energy_envelope_unrecorded"
EXCEEDS = "anchor_energy_envelope_exceeds_quarter_metric"


def _function_segment(source: str) -> str:
    tree = ast.parse(source)
    node = next(
        item for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name == FUNCTION
    )
    lines = source.splitlines(keepends=True)
    return "".join(lines[node.lineno - 1:node.end_lineno])


def vendored_segment() -> str:
    from tests import oracle_l9_env_2_reduce_clamp as oracle

    segment = _function_segment(ORACLE_PATH.read_text(encoding="utf-8"))
    if hashlib.sha256(segment.encode("utf-8")).hexdigest() != oracle.FUNCTION_SOURCE_SHA256:
        raise AssertionError("vendored oracle function bytes changed")
    return segment


def oracle_reduce_source() -> bytes:
    """origin/main's reduce.py with the vendored function: e1b3a0510's bytes."""

    current = (ROOT / "joulewise/reduce.py").read_text(encoding="utf-8")
    original = _function_segment(current)
    if current.count(original) != 1:
        raise AssertionError("origin/main function not found exactly once")
    return current.replace(original, vendored_segment()).encode("utf-8")


def _load_shadow(name: str, source: bytes):
    spec = importlib.util.spec_from_loader(name, loader=None)
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(ROOT / "joulewise/reduce.py")
    sys.modules[name] = module
    exec(compile(source, f"{name} (shadow of joulewise/reduce.py)", "exec"), module.__dict__)
    return module


_ORACLE = None
_PRISTINE = None


def oracle_module():
    """L9-ENV-2's patched reducer as a separate test-only module."""

    global _ORACLE
    if _ORACLE is None:
        from tests import oracle_l9_env_2_reduce_clamp as oracle

        source = oracle_reduce_source()
        if hashlib.sha256(source).hexdigest() != oracle.SOURCE_FILE_SHA256:
            raise AssertionError("oracle source is not e1b3a0510's reduce.py")
        _ORACLE = _load_shadow("tests._oracle_reduce_e1b3a0510", source)
    return _ORACLE


def pristine_module():
    """A fresh execution of origin/main's reduce.py bytes (no whole_window)."""

    global _PRISTINE
    if _PRISTINE is None:
        source = (ROOT / "joulewise/reduce.py").read_bytes()
        if hashlib.sha256(source).hexdigest() != ORIGIN_MAIN_SHA256["joulewise/reduce.py"]:
            raise AssertionError("reduce.py is not origin/main's bytes")
        _PRISTINE = _load_shadow("tests._pristine_reduce_origin_main", source)
    return _PRISTINE


def interval_curve(rows):
    return [
        TracePoint(t=(start + end) / 2.0, power_w=power, support_start_s=start, support_end_s=end)
        for start, end, power in rows
    ]


def point_curve(rows):
    return [TracePoint(t=(start + end) / 2.0, power_w=power) for start, end, power in rows]


def stepped_rows(origin_s: float, count: int, width_s: float, seed: int):
    rows = []
    value = seed
    for index in range(count):
        value = (value * 1103515245 + 12345) % (2**31)
        power = 5.0 + (value % 9000) / 100.0
        rows.append((origin_s + index * width_s, origin_s + (index + 1) * width_s, power))
    return rows


class OracleProvenanceTests(unittest.TestCase):
    def test_vendored_function_rebuilds_e1b3a0510_reduce_bytes(self) -> None:
        from tests import oracle_l9_env_2_reduce_clamp as oracle

        self.assertEqual(hashlib.sha256(oracle_reduce_source()).hexdigest(), oracle.SOURCE_FILE_SHA256)

    def test_vendored_function_matches_git_object_when_available(self) -> None:
        from tests import oracle_l9_env_2_reduce_clamp as oracle

        result = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{oracle.SOURCE_COMMIT}:{oracle.SOURCE_PATH}"],
            capture_output=True,
        )
        if result.returncode != 0:
            self.skipTest("e1b3a0510 not in this clone")
        self.assertEqual(hashlib.sha256(result.stdout).hexdigest(), oracle.SOURCE_FILE_SHA256)
        self.assertEqual(_function_segment(result.stdout.decode("utf-8")), vendored_segment())


class AnalysisClampFunctionTests(unittest.TestCase):
    """A1/A2 at function level: analysis clamp == oracle, bit for bit."""

    def _check(self, contributions, bundle_s, fiducial_s, span_s):
        analysis = _clamped_corner_composed_anchor_shift_envelope(
            contributions, bundle_s, fiducial_s, span_s)
        oracle = oracle_module()._corner_composed_anchor_shift_envelope(
            contributions, bundle_s, fiducial_s, span_s)
        origin = reduce_module._corner_composed_anchor_shift_envelope(
            contributions, bundle_s, fiducial_s, span_s)
        self.assertEqual(analysis, oracle)
        if origin is not None:
            # Non-inverting: bit-identical to origin/main reduce as well.
            self.assertEqual(analysis, origin)
        return analysis, origin

    def test_l9_env_2_inverted_cases(self) -> None:
        power_w, fiducial_s = 10.0, 0.1
        curve = interval_curve([(-1.0, 2.0, power_w)])
        for duration_s in (0.19, 0.1, 1e-6):
            with self.subTest(duration=duration_s):
                env, origin = self._check([(curve, [Window(0.5, 0.5 + duration_s)])], 0.0, fiducial_s, 0.0)
                self.assertIsNone(origin)
                self.assertEqual(env["lower_j"], 0.0)
                self.assertAlmostEqual(env["point_j"], power_w * duration_s, places=12)
                self.assertAlmostEqual(env["upper_j"], power_w * (duration_s + 2 * fiducial_s), places=12)

    def test_l9_env_2_corner_fixtures(self) -> None:
        fixtures = [
            ([(0.0, 0.5, 0.0), (0.5, 1.0, 100.0), (1.0, 1.5, 0.0)], [Window(0.5, 1.25)], 0.00005, 0.0, 0.0),
            ([(-1.0, 2.0, 10.0)], [Window(0.2, 0.8)], 0.0, 0.1, 0.0),
            ([(-1.0, 2.0, 10.0)], [Window(0.2, 0.8)], 0.0, 0.1, 0.05),
            ([(-1.0, 6.0, 10.0)], [Window(0.5, 4.35743)], 0.0, 0.01282, 0.0),
        ]
        for rows, windows, bundle_s, fiducial_s, span_s in fixtures:
            env, origin = self._check([(interval_curve(rows), windows)], bundle_s, fiducial_s, span_s)
            self.assertIsNotNone(origin)

    def test_soundness_grid(self) -> None:
        curve = interval_curve(stepped_rows(-1.0, 80, 0.025, 3))
        fiducial_s, span_s, bundle_s = 0.06, 0.004, 0.01
        edge_s = fiducial_s + span_s
        window = Window(0.3, 0.3 + 2 * edge_s * 0.8)
        env, origin = self._check([(curve, [window])], bundle_s, fiducial_s, span_s)
        self.assertIsNone(origin)
        grid = [edge_s * (k / 10.0) for k in range(-10, 11)]
        for eps_on in grid:
            for eps_off in grid:
                start, end = window.start_s + eps_on, window.end_s + eps_off
                if end < start:
                    continue
                for k in range(-4, 5):
                    energy = reduce_module._shift_energy_j(
                        [(curve, [Window(start, end)])], bundle_s * k / 4.0)
                    self.assertGreaterEqual(energy, env["lower_j"] - 1e-9)
                    self.assertLessEqual(energy, env["upper_j"] + 1e-9)

    def test_sweep_bit_identical_to_oracle(self) -> None:
        inverted = defined = 0
        for origin_s in (0.0, 1_784_491_122.85):
            for seed in (1, 7, 42):
                rows = stepped_rows(origin_s - 1.0, 60, 0.05, seed)
                for make in (interval_curve, point_curve):
                    curve = make(rows)
                    for fiducial_s, span_s, bundle_s in (
                        (0.0, 0.0, 0.0),
                        (0.02142716616057592, 8.106231689453125e-06, 0.0566),
                        (0.0665, 1e-05, 0.03),
                    ):
                        edge_s = fiducial_s + span_s
                        for factor in (0.0, 0.1, 0.5, 0.99, 1.0 - 1e-9, 1.0, 1.0 + 1e-9, 1.01, 1.5, 3.0, 10.0):
                            duration_s = 2.0 * edge_s * factor if edge_s else 0.13 * factor
                            start_s = origin_s + 0.4
                            short = Window(start_s, start_s + duration_s)
                            long = Window(start_s + 0.9, start_s + 1.4)
                            for windows in ([short], [short, long], [long, short]):
                                contributions = [(curve, windows)]
                                for extra in ((), ((make(stepped_rows(origin_s - 1.0, 60, 0.05, seed + 1)),
                                                    [Window(start_s + 0.2, start_s + 0.2 + duration_s)]),)):
                                    with self.subTest(origin=origin_s, seed=seed, factor=factor,
                                                      fiducial=fiducial_s, windows=len(windows),
                                                      contributions=1 + len(extra)):
                                        env, origin = self._check(
                                            contributions + list(extra), bundle_s, fiducial_s, span_s)
                                        if env is not None and origin is None:
                                            inverted += 1
                                        elif env is not None:
                                            defined += 1
        self.assertGreater(inverted, 200)
        self.assertGreater(defined, 300)

    def test_other_none_guards_are_unchanged(self) -> None:
        curve = interval_curve([(-1.0, 2.0, 10.0)])
        cases = [
            ([(curve, [Window(0.5, 0.6)])], None, 0.1, 0.0),
            ([(curve, [Window(0.5, 0.6)])], 0.0, None, 0.0),
            ([(curve, [Window(0.5, 0.6)])], 0.0, math.nan, 0.0),
            ([(curve, [Window(0.5, 0.6)])], math.inf, 0.1, 0.0),
            ([(curve, [Window(0.5, 0.6)])], -1.0, 0.1, 0.0),
            ([(curve, [Window(0.5, 0.6)])], 0.0, -0.1, 0.0),
            ([(curve, [Window(0.5, 0.6)])], 0.0, 0.1, -1.0),
            ([(curve, [Window(0.5, 0.6)])], 0.0, 0.1, math.nan),
            ([], 0.0, 0.1, 0.0),
            ([(curve, [])], 0.0, 0.1, 0.0),
            ([([], [Window(0.5, 0.6)])], 0.0, 0.1, 0.0),
            ([(interval_curve([(-1.0, 2.0, -1.0)]), [Window(0.5, 0.6)])], 0.0, 0.1, 0.0),
            # inverted window, but no overlap / trace support for the bound
            ([(curve, [Window(0.5, 0.6)])], 5.0, 0.1, 0.0),
            ([(interval_curve([(0.0, 0.1, 10.0)]), [Window(5.0, 5.1)])], 0.0, 0.1, 0.0),
        ]
        for args in cases:
            with self.subTest(args=args[1:]):
                self.assertIsNone(_clamped_corner_composed_anchor_shift_envelope(*args))
                self.assertIsNone(oracle_module()._corner_composed_anchor_shift_envelope(*args))
                self.assertIsNone(reduce_module._corner_composed_anchor_shift_envelope(*args))


def _bundle_fixture(test: unittest.TestCase, root: Path):
    from tests.test_whole_window_selection import (
        MaxBracketConsumptionTests,
        _install_synthetic_calibration_defaults,
    )

    _install_synthetic_calibration_defaults(test)
    root.mkdir(parents=True, exist_ok=True)
    bundle, minted, minted_bound, _operative = MaxBracketConsumptionTests._build_v052_bundle(root)
    return bundle, minted, minted_bound


def _phase_durations(summary: dict) -> dict[str, float]:
    return {
        phase: record["windows"][0]["window_duration_s"]
        for phase, record in summary["window_evidence_precheck"]["phase"].items()
    }


class PermanentWideningCaseTests(unittest.TestCase):
    """A3: operative bound dominates the minted bound; short prefill.

    The member is the repository's synthetic-session shape carrying the REAL
    minted summary; the session's re-derivation runs on the REAL bundle (the
    retained 0.4 s request fails metric-scale and member-era checks at a 66 ms
    bound for reasons the ruling does not touch, as in L9-ENV-2 E3).  Global
    precheck classification is asserted equal across origin/main and the
    analysis clamp before it is neutralised.
    """

    _cache: dict[str, float] = {}

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name)
        class_scope = SimpleNamespace(addCleanup=cls.addClassCleanup)
        cls.bundle, cls.minted, cls.minted_bound = _bundle_fixture(class_scope, cls.root / "fixture")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _bounds(self) -> tuple[float, float]:
        span_s = self.minted["energy_anchor_shift_envelopes"][PREFILL][
            "wall_minus_monotonic_independent_edge_span_s"]
        duration_s = _phase_durations(self.minted)["prefill"]
        self.assertLess(2.0 * (self.minted_bound + span_s), duration_s)
        return duration_s / 2.0 - span_s + 0.002, duration_s / 2.0 - span_s - 0.002

    def _rederive(self, bound_s: float) -> tuple[dict, dict, dict]:
        kwargs = dict(authenticated_fiducial_bound_s=bound_s,
                      _instrument_calibration_physics_cache=self._cache)
        old = reduce_module._rederive_summary_for_authenticated_fiducial_bound(self.bundle, **kwargs)
        new = _rederive_operative_summary(self.bundle, **kwargs)
        oracle = oracle_module()._rederive_summary_for_authenticated_fiducial_bound(self.bundle, **kwargs)
        for summary in (old, new, oracle):
            self.assertEqual(summary["status"], "succeeded")
        self.assertEqual(whole_window._classify_precheck_refusals(old)[0],
                         whole_window._classify_precheck_refusals(new)[0])
        return old, new, oracle

    def _session(self, name: str, minted: dict, operative_bound: float, rederive):
        from joulewise.uncertainty_evidence import CLOCK_METHOD_V3
        from tests.test_whole_window_selection import MaxBracketConsumptionTests

        root = self.root / name
        member = root / "member"
        member.mkdir(parents=True, exist_ok=True)
        (member / "summary_metrics.json").write_text(json.dumps(minted) + "\n", encoding="utf-8")
        (member / "metadata.json").write_text(json.dumps({
            "instrument_calibration": {"verified_effective_b_fiducial_s": self.minted_bound},
            "uncertainty_evidence": {"clock_anchor": {"method": CLOCK_METHOD_V3}},
        }) + "\n", encoding="utf-8")
        session = AuthenticatedConsumptionSession(root, {"member"})
        bundle = self.bundle

        def on_real_bundle(_path, **kwargs):
            return rederive(bundle, **kwargs)

        with (
            patch("joulewise.whole_window.calibration_bracket_for_bundles",
                  return_value=(MaxBracketConsumptionTests._bracket(operative_bound), ())),
            patch("joulewise.whole_window._current_strict_summary", return_value=True),
            patch("joulewise.whole_window._verify_instrument_calibration",
                  return_value=(self.minted_bound, None)),
            patch("joulewise.whole_window._classify_precheck_refusals", return_value=(set(), {})),
            patch("joulewise.whole_window._rederive_operative_summary",
                  side_effect=on_real_bundle) as call,
        ):
            session._prepare(bundle_paths={"member": member},
                             policy=SimpleNamespace(calibration_bracketing=object()))
        self.assertEqual(call.call_args.kwargs["authenticated_fiducial_bound_s"], operative_bound)
        return session

    def test_short_prefill_under_dominating_bound(self) -> None:
        just_under, _over = self._bounds()
        old, new, oracle = self._rederive(just_under)
        minted_prefill = self.minted["energy_anchor_shift_envelopes"][PREFILL]

        # A2 at summary level: the whole operative summary equals what
        # e1b3a0510's patched reducer re-derives, key order included.
        self.assertEqual(new, oracle)
        self.assertEqual(json.dumps(new), json.dumps(oracle))

        # Counterfactual at origin/main: prefill dropped, session refuses.
        self.assertNotIn(PREFILL, old["energy_anchor_shift_envelopes"])
        refused = self._session("old", self.minted, just_under,
                                reduce_module._rederive_summary_for_authenticated_fiducial_bound)
        self.assertFalse(refused.ready)
        self.assertEqual(refused.refusal_reasons, (UNRECORDED,))

        prefill = new["energy_anchor_shift_envelopes"][PREFILL]
        self.assertEqual(prefill["point_j"], minted_prefill["point_j"])
        self.assertEqual(prefill["lower_j"], 0.0)
        self.assertLessEqual(prefill["lower_j"], minted_prefill["lower_j"])
        self.assertGreaterEqual(prefill["upper_j"], minted_prefill["upper_j"])
        self.assertAlmostEqual(prefill["anchor_bound_s"] - minted_prefill["anchor_bound_s"],
                               just_under - self.minted_bound, places=12)
        for pointer, envelope in old["energy_anchor_shift_envelopes"].items():
            self.assertEqual(new["energy_anchor_shift_envelopes"][pointer], envelope)
        self.assertEqual(
            set(old["window_evidence_precheck"]["phase"]["prefill"]["reasons"])
            - set(new["window_evidence_precheck"]["phase"]["prefill"]["reasons"]),
            {UNRECORDED})

        session = self._session("new", self.minted, just_under, _rederive_operative_summary)
        self.assertTrue(session.ready, session.refusal_reasons)
        operative = session.provenance_for("member")["operative_envelopes"][PREFILL]
        self.assertEqual(operative["lower_j"], 0.0)
        self.assertEqual(operative["point_j"], minted_prefill["point_j"])

    def test_prefill_just_over_twice_edge_bound_is_unchanged(self) -> None:
        _under, just_over = self._bounds()
        old, new, oracle = self._rederive(just_over)
        self.assertEqual(new["energy_anchor_shift_envelopes"][PREFILL],
                         old["energy_anchor_shift_envelopes"][PREFILL])
        self.assertEqual(new, oracle)
        for name, rederive in (
            ("over-old", reduce_module._rederive_summary_for_authenticated_fiducial_bound),
            ("over-new", _rederive_operative_summary),
        ):
            with self.subTest(case=name):
                session = self._session(name, self.minted, just_over, rederive)
                self.assertTrue(session.ready, session.refusal_reasons)

    def test_bounds_sweep_equals_oracle(self) -> None:
        just_under, just_over = self._bounds()
        for bound_s in (self.minted_bound * 1.5, just_over, just_over + 0.0019, just_under - 0.0019,
                        just_under, just_under * 1.5):
            with self.subTest(bound=bound_s):
                _old, new, oracle = self._rederive(bound_s)
                self.assertEqual(json.dumps(new), json.dumps(oracle))

    def test_genuinely_missing_operative_envelope_still_refuses(self) -> None:
        just_under, _over = self._bounds()
        _old, new, _oracle = self._rederive(just_under)
        for pointer in (PREFILL, "/gross_energy_j"):
            with self.subTest(pointer=pointer):
                summary = json.loads(json.dumps(new))
                summary["energy_anchor_shift_envelopes"].pop(pointer)
                session = self._session("missing" + pointer.replace("/", "_"), self.minted, just_under,
                                        lambda _path, **_kwargs: summary)
                self.assertFalse(session.ready)
                self.assertEqual(session.refusal_reasons, ('anchor_energy_envelope_unrecorded',))

    def test_clamp_fails_closed_without_exact_reconstruction(self) -> None:
        just_under, _over = self._bounds()
        kwargs = dict(authenticated_fiducial_bound_s=just_under,
                      instrument_calibration_physics_cache=self._cache)
        old, _new, _oracle = self._rederive(just_under)
        # A recorded envelope the reconstruction cannot reproduce: no clamp.
        tampered = json.loads(json.dumps(old))
        tampered["energy_anchor_shift_envelopes"]["/phase_energy_j/decode"]["upper_j"] += 1e-9
        self.assertIs(_clamp_inverted_operative_envelopes(self.bundle, tampered, **kwargs), tampered)
        # The gross family is never clamped on the analysis side.
        no_gross = json.loads(json.dumps(old))
        no_gross["energy_anchor_shift_envelopes"].pop("/gross_energy_j")
        clamped = _clamp_inverted_operative_envelopes(self.bundle, no_gross, **kwargs)
        self.assertNotIn("/gross_energy_j", clamped["energy_anchor_shift_envelopes"])
        self.assertIn(PREFILL, clamped["energy_anchor_shift_envelopes"])
        # Unreadable path: unchanged summary (origin/main behaviour).
        self.assertIs(_clamp_inverted_operative_envelopes(self.root / "absent", old, **kwargs), old)


class FreezeProofTests(unittest.TestCase):
    """A4: reduce.py and every estimator path are origin/main's bytes."""

    def test_estimator_code_paths_are_origin_main_bytes(self) -> None:
        self.assertEqual(set(ESTIMATOR_CODE_PATHS), set(ORIGIN_MAIN_SHA256))
        for relative in ESTIMATOR_CODE_PATHS:
            with self.subTest(path=relative):
                self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                                 ORIGIN_MAIN_SHA256[relative])
        self.assertEqual(_current_estimator_code_sha256(), ORIGIN_MAIN_SHA256)

    def test_live_acceptance_estimator_pin_is_current(self) -> None:
        acceptance = json.loads(Path(DEFAULT_ACCEPTANCE_BOUND_PATH).read_bytes())
        self.assertEqual(acceptance["prospective_rederivation"]["estimator_code_sha256"],
                         _current_estimator_code_sha256())

    def test_frozen_files_test_is_unchanged(self) -> None:
        self.assertEqual(
            hashlib.sha256((ROOT / "tests/b5_analysis/test_frozen_files.py").read_bytes()).hexdigest(),
            FROZEN_FILES_TEST_SHA256)

    def test_reduce_is_not_patched_at_runtime(self) -> None:
        for name in ("_corner_composed_anchor_shift_envelope", "_anchor_shift_envelope",
                     "_rederive_summary_for_authenticated_fiducial_bound", "reduce_bundle"):
            function = getattr(reduce_module, name)
            self.assertEqual(function.__module__, "joulewise.reduce")
            self.assertEqual(Path(function.__code__.co_filename).resolve(),
                             (ROOT / "joulewise/reduce.py").resolve())
        self.assertNotIn("whole_window", json.dumps(sorted(vars(reduce_module))))

    def test_collection_mint_is_origin_main_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle, minted, _bound = _bundle_fixture(self, Path(tmp))
            cache: dict[str, float] = {}
            current = reduce_module.reduce_bundle(
                bundle, _instrument_calibration_physics_cache=cache).to_dict()
            pristine = pristine_module().reduce_bundle(
                bundle, _instrument_calibration_physics_cache=cache).to_dict()
            stored = json.loads((bundle / "summary_metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(json.dumps(current), json.dumps(pristine))
        self.assertEqual(current, minted)
        self.assertEqual(stored, minted)
        # The mint still omits inverting phases (reduce's own semantics).
        self.assertNotIn("/phase_energy_j/tokenize", current["energy_anchor_shift_envelopes"])
        self.assertIn(UNRECORDED, current["window_evidence_precheck"]["phase"]["tokenize"]["reasons"])


if __name__ == "__main__":
    unittest.main()
