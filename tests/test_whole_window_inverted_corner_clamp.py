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
import contextlib
import dataclasses
import hashlib
import importlib.util
import json
import math
import random
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


_SEAT_BASE = None
SEAT_BASE_COMMIT = "3e4d359c2"


def seat_base_whole_window():
    """L9-ENV-3's whole_window.py (3e4d359c2), for L9-ENV-4 counterfactuals."""

    global _SEAT_BASE
    if _SEAT_BASE is None:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{SEAT_BASE_COMMIT}:joulewise/whole_window.py"],
            capture_output=True,
        )
        if result.returncode != 0:
            raise unittest.SkipTest(f"{SEAT_BASE_COMMIT} not in this clone")
        _SEAT_BASE = _load_shadow("tests._whole_window_3e4d359c2", result.stdout)
    return _SEAT_BASE


_SHADOW_WHOLE_WINDOW: dict[str, object] = {}
# L9-ENV-4's head, for L9-ENV-5 counterfactuals (O-F3, O-F5).
ENV4_COMMIT = "0a799146c"
# The ruling's base; origin/main's whole_window.py is byte-identical to it
# (checked at 4c26b2e2c), so this is "origin/main behaviour" for O-F1.
ORIGIN_MAIN_COMMIT = "7ebb7db2a"


def whole_window_at(commit: str):
    """``joulewise/whole_window.py`` at ``commit``, as a separate module."""

    if commit not in _SHADOW_WHOLE_WINDOW:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{commit}:joulewise/whole_window.py"],
            capture_output=True,
        )
        if result.returncode != 0:
            raise unittest.SkipTest(f"{commit} not in this clone")
        _SHADOW_WHOLE_WINDOW[commit] = _load_shadow(f"tests._whole_window_{commit}", result.stdout)
    return _SHADOW_WHOLE_WINDOW[commit]


def _gate_for(summary: dict, pointer: str) -> dict:
    for group_key, prefix in whole_window._CLAMP_GROUP_PREFIXES:
        if pointer.startswith(prefix):
            for member, gate in summary["window_evidence_precheck"][group_key].items():
                if prefix + reduce_module._json_pointer_token(str(member)) == pointer:
                    return gate
    raise KeyError(pointer)


def assert_gates_self_consistent(test: unittest.TestCase, summary: dict) -> None:
    """L9-ENV-4 F1: no member gate is ineligible without a reason."""

    def walk(gate, where):
        if isinstance(gate, dict):
            if "eligible" in gate and "reasons" in gate and gate["eligible"] is False:
                test.assertTrue(gate["reasons"], f"{where}: eligible False with no reason")
            for key, value in gate.items():
                walk(value, f"{where}/{key}")
        elif isinstance(gate, list):
            for index, value in enumerate(gate):
                walk(value, f"{where}/{index}")

    walk(summary.get("window_evidence_precheck"), "window_evidence_precheck")


def expected_from_oracle(old: dict, oracle: dict) -> tuple[dict, list[str]]:
    """The analysis summary L9-ENV-4 expects, derived from e1b3a0510's.

    Equal to the oracle except for a clamped pointer whose envelope passes the
    envelope gate (no gate reasons): the oracle records it and leaves the gate
    eligible, the analysis path does not add it (the member keeps reduce's
    ``unrecorded`` refusal).  Returns the excluded pointers too.
    """

    old_env = old.get("energy_anchor_shift_envelopes") or {}
    group_prefixes = tuple(prefix for _key, prefix in whole_window._CLAMP_GROUP_PREFIXES)
    if not any(pointer.startswith(group_prefixes) for pointer in old_env):
        # L9-ENV-5 (O-F3): no recorded member envelope proves the mirror, so
        # the analysis path clamps nothing (the oracle still would).
        return old, []
    oracle_env = oracle.get("energy_anchor_shift_envelopes") or {}
    joint_j = (oracle.get("energy_bound_terms_j") or {}).get("E_interpolation_joint_edge_bound_j")
    excluded = [
        pointer for pointer, envelope in oracle_env.items()
        if pointer not in old_env
        and not reduce_module._anchor_envelope_gate_reasons(envelope, joint_j)
    ]
    if not excluded:
        return oracle, []
    if set(oracle_env) - set(excluded) == set(old_env):
        return old, excluded
    expected = json.loads(json.dumps(oracle))
    for pointer in excluded:
        expected["energy_anchor_shift_envelopes"].pop(pointer)
        _gate_for(expected, pointer).clear()
        _gate_for(expected, pointer).update(json.loads(json.dumps(_gate_for(old, pointer))))
    return expected, excluded


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

    def test_reviewer_mini_sweep_with_mixed_sign_trace(self) -> None:
        """Reviewer K1 (mutant M02 / L9-ENV-4 M04): one -1 W sample in an
        otherwise positive trace must refuse exactly as the oracle does."""

        rng = random.Random(7)
        refused_mixed = 0
        for epoch_s in (0.0, 1793232000.123456):
            for interval in (True, False):
                dt_s = 0.05
                curve = [
                    TracePoint(t=epoch_s + i * dt_s + (dt_s / 2 if interval else 0.0),
                               power_w=rng.uniform(1, 9),
                               support_start_s=(epoch_s + i * dt_s) if interval else None,
                               support_end_s=(epoch_s + (i + 1) * dt_s) if interval else None)
                    for i in range(300)
                ]
                mixed = list(curve)
                mixed[10] = dataclasses.replace(mixed[10], power_w=-1.0)
                for edge_s in (0.03, 0.0656):
                    for length_s in (0.0, 0.01, 2 * edge_s - 1e-9, 2 * edge_s, 2 * edge_s + 1e-9, 0.5, 3.0):
                        start_s = epoch_s + 5.0
                        shapes = (
                            ("single", [(curve, [Window(start_s, start_s + length_s)])]),
                            ("short+long", [(curve, [Window(start_s, start_s + length_s),
                                                     Window(start_s + 1, start_s + 3)])]),
                            ("two-source", [(curve, [Window(start_s, start_s + length_s)]),
                                            (curve, [Window(start_s + 4, start_s + 4.2)])]),
                            ("mixed-sign", [(mixed, [Window(start_s, start_s + length_s)])]),
                            ("near-end", [(curve, [Window(epoch_s + 14.99, epoch_s + 14.99 + length_s)])]),
                        )
                        for shape, contributions in shapes:
                            for span_s in (0.0, 0.0012):
                                analysis = _clamped_corner_composed_anchor_shift_envelope(
                                    contributions, 0.0005, edge_s, span_s)
                                oracle = oracle_module()._corner_composed_anchor_shift_envelope(
                                    contributions, 0.0005, edge_s, span_s)
                                self.assertEqual(
                                    json.dumps(analysis), json.dumps(oracle),
                                    (epoch_s, interval, edge_s, length_s, shape, span_s))
                                if shape == "mixed-sign":
                                    self.assertIsNone(analysis)
                                    refused_mixed += 1
        self.assertEqual(refused_mixed, 2 * 2 * 2 * 7 * 2)
        # Without the -1 W sample the same short window clamps (the guard,
        # not some other check, refuses the mixed-sign trace).
        start_s = 5.0
        positive = [TracePoint(t=i * 0.05 + 0.025, power_w=5.0, support_start_s=i * 0.05,
                               support_end_s=(i + 1) * 0.05) for i in range(300)]
        negative = list(positive)
        negative[10] = dataclasses.replace(negative[10], power_w=-1.0)
        window = [Window(start_s, start_s + 0.01)]
        self.assertIsNotNone(_clamped_corner_composed_anchor_shift_envelope([(positive, window)], 0.0005, 0.03, 0.0))
        self.assertIsNone(_clamped_corner_composed_anchor_shift_envelope([(negative, window)], 0.0005, 0.03, 0.0))

    @staticmethod
    def _ulp_case(seed: int):
        """Random clamped shape (found by search) where the clamp position
        changes the result in the last bits through the breakpoint set."""

        rng = random.Random(seed)
        interval = rng.random() < 0.5
        dt_s = rng.choice([0.05, 0.1, 0.0731])
        curve = [
            TracePoint(t=i * dt_s + (dt_s / 2 if interval else 0.0), power_w=round(rng.uniform(0, 12), 3),
                       support_start_s=i * dt_s if interval else None,
                       support_end_s=(i + 1) * dt_s if interval else None)
            for i in range(40)
        ]
        edge_s = round(rng.uniform(0.02, 0.2), 4)
        windows = []
        for _ in range(rng.randint(2, 3)):
            start_s = round(rng.uniform(0.5, 40 * dt_s - 1.0), 4)
            length_s = round(rng.choice([rng.uniform(0, 2 * edge_s), rng.uniform(0, 1.0)]), 4)
            windows.append(Window(start_s, start_s + length_s))
        return [(curve, windows)], rng.choice([0.0, 0.0005, 0.01]), edge_s, 0.0

    def test_clamp_position_is_the_midpoint_to_the_last_bit(self) -> None:
        """L9-ENV-4 survivors M01/M02 (clamp to the shifted start or end).

        In exact arithmetic any point of the inverted corner window gives the
        same envelope (a zero-length window contributes 0 J and adds no kink);
        in floating point the extra breakpoints differ, and on these searched
        cases only the midpoint reproduces e1b3a0510 bit for bit.
        """

        for seed in (1618, 1760, 2352, 2353):
            with self.subTest(seed=seed):
                args = self._ulp_case(seed)
                analysis = _clamped_corner_composed_anchor_shift_envelope(*args)
                self.assertIsNone(reduce_module._corner_composed_anchor_shift_envelope(*args))
                self.assertIsNotNone(analysis)
                self.assertEqual(json.dumps(analysis),
                                 json.dumps(oracle_module()._corner_composed_anchor_shift_envelope(*args)))

    def test_input_window_inverted_at_zero_shift_is_refused(self) -> None:
        """L9-ENV-5 O-F5: outside the ruling, so None as at origin/main."""

        curve = interval_curve([(-1.0, 10.0, 10.0)])
        cases = (
            [(curve, [Window(5.1, 5.0)])],
            [(curve, [Window(0.5, 0.6), Window(0.81, 0.8)])],
            [(curve, [Window(0.5, 0.6)]), (curve, [Window(2.0, 2.0 - 1e-9)])],
        )
        env4 = whole_window_at(ENV4_COMMIT)
        for contributions in cases:
            with self.subTest(windows=[[(w.start_s, w.end_s) for w in ws] for _c, ws in contributions]):
                self.assertIsNone(_clamped_corner_composed_anchor_shift_envelope(contributions, 0.0, 0.1, 0.0))
                self.assertIsNone(reduce_module._corner_composed_anchor_shift_envelope(contributions, 0.0, 0.1, 0.0))
                # Counterfactual: e1b3a0510 and L9-ENV-4 define an envelope.
                self.assertIsNotNone(
                    oracle_module()._corner_composed_anchor_shift_envelope(contributions, 0.0, 0.1, 0.0))
                self.assertIsNotNone(
                    env4._clamped_corner_composed_anchor_shift_envelope(contributions, 0.0, 0.1, 0.0))
        # A zero-length input window is not inverted and still clamps.
        self.assertIsNotNone(_clamped_corner_composed_anchor_shift_envelope(
            [(curve, [Window(5.0, 5.0)])], 0.0, 0.1, 0.0))

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


def run_session(test: unittest.TestCase, root: Path, *, bundle: Path, minted: dict, minted_bound: float,
                operative_bound: float, rederive, analysis_clamp: bool | None = None,
                module=whole_window):
    """Prepare a one-member max-bracket session whose re-derivation runs on ``bundle``.

    ``analysis_clamp=None`` constructs the session without the keyword (the
    default; also how ``module`` = origin/main's whole_window.py is built).
    The re-derivation the session must reach is replaced by ``rederive`` on
    the real bundle; without the flag, reaching the clamp fails the test.
    """

    from joulewise.uncertainty_evidence import CLOCK_METHOD_V3
    from tests.test_whole_window_selection import MaxBracketConsumptionTests

    member = root / "member"
    member.mkdir(parents=True, exist_ok=True)
    (member / "summary_metrics.json").write_text(json.dumps(minted) + "\n", encoding="utf-8")
    (member / "metadata.json").write_text(json.dumps({
        "instrument_calibration": {"verified_effective_b_fiducial_s": minted_bound},
        "uncertainty_evidence": {"clock_anchor": {"method": CLOCK_METHOD_V3}},
    }) + "\n", encoding="utf-8")

    def on_real_bundle(_path, **kwargs):
        return rederive(bundle, **kwargs)

    def unexpected(*_args, **_kwargs):
        raise AssertionError("the session reached the wrong re-derivation")

    reached = (
        "_rederive_operative_summary" if analysis_clamp
        else "_rederive_summary_for_authenticated_fiducial_bound"
    )
    # The clamp must stay unreached by a default session (origin/main has no
    # such function; ``create`` lets the guard stand there too).
    guard = (contextlib.nullcontext() if analysis_clamp else
             patch.object(module, "_rederive_operative_summary", side_effect=unexpected, create=True))
    # A shadow module (origin/main's file) sees the same synthetic calibration
    # defaults that _install_synthetic_calibration_defaults put on whole_window.
    defaults = contextlib.ExitStack()
    if module is not whole_window:
        for name in ("load_calibration_acceptance_bound", "load_calibration_ledger_snapshot"):
            defaults.enter_context(patch.object(module, name, getattr(whole_window, name)))
    with (
        defaults,
        guard,
        patch.object(module, "calibration_bracket_for_bundles",
                     return_value=(MaxBracketConsumptionTests._bracket(operative_bound), ())),
        patch.object(module, "_current_strict_summary", return_value=True),
        patch.object(module, "_verify_instrument_calibration", return_value=(minted_bound, None)),
        patch.object(module, "_classify_precheck_refusals", return_value=(set(), {})),
        patch.object(module, reached, side_effect=on_real_bundle) as call,
    ):
        session = module.AuthenticatedConsumptionSession(
            root, {"member"}, **({} if analysis_clamp is None else {"analysis_clamp": analysis_clamp}))
        session._prepare(bundle_paths={"member": member},
                         policy=SimpleNamespace(calibration_bracketing=object()))
    test.assertEqual(call.call_args.kwargs["authenticated_fiducial_bound_s"], operative_bound)
    return session


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
        assert_gates_self_consistent(self, new)
        self.assertEqual(whole_window._classify_precheck_refusals(old)[0],
                         whole_window._classify_precheck_refusals(new)[0])
        return old, new, oracle

    def _session(self, name: str, minted: dict, operative_bound: float, rederive, **kwargs):
        return run_session(self, self.root / name, bundle=self.bundle, minted=minted,
                           minted_bound=self.minted_bound, operative_bound=operative_bound,
                           rederive=rederive, **kwargs)

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

        session = self._session("new", self.minted, just_under, _rederive_operative_summary,
                                analysis_clamp=True)
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
        for name, rederive, flag in (
            ("over-old", reduce_module._rederive_summary_for_authenticated_fiducial_bound, None),
            ("over-new", _rederive_operative_summary, True),
        ):
            with self.subTest(case=name):
                session = self._session(name, self.minted, just_over, rederive, analysis_clamp=flag)
                self.assertTrue(session.ready, session.refusal_reasons)

    def test_bounds_sweep_equals_oracle(self) -> None:
        just_under, just_over = self._bounds()
        critical_s = (just_under + just_over) / 2.0
        for bound_s in (self.minted_bound * 1.5, just_over, just_over + 0.0019, just_under - 0.0019,
                        just_under, just_under * 1.5, critical_s * 3.0):
            with self.subTest(bound=bound_s):
                old, new, oracle = self._rederive(bound_s)
                expected, excluded = expected_from_oracle(old, oracle)
                # No envelope on this fixture passes after clamping (single
                # windows): the analysis path equals the oracle here.
                self.assertEqual(excluded, [])
                self.assertEqual(json.dumps(new), json.dumps(expected))

    def test_no_reproduced_member_envelope_is_not_clamped(self) -> None:
        """L9-ENV-5 O-F3: with no recorded member envelope reproduced, no clamp.

        At 3x the critical bound every member inverts and reduce records no
        envelope map, so nothing proves the mirror on this bundle.
        """

        just_under, just_over = self._bounds()
        bound_s = (just_under + just_over) / 2.0 * 3.0
        kwargs = dict(authenticated_fiducial_bound_s=bound_s,
                      instrument_calibration_physics_cache=self._cache)
        old, new, oracle = self._rederive(bound_s)
        self.assertNotIn("energy_anchor_shift_envelopes", old)
        self.assertEqual(json.dumps(new), json.dumps(old))
        self.assertIs(_clamp_inverted_operative_envelopes(self.bundle, old, **kwargs), old)
        self.assertIn("/phase_energy_j/decode", oracle["energy_anchor_shift_envelopes"])
        # Counterfactual at L9-ENV-4: decode was clamped from an unproven mirror.
        env4 = whole_window_at(ENV4_COMMIT)._clamp_inverted_operative_envelopes(self.bundle, old, **kwargs)
        self.assertEqual(list(env4["energy_anchor_shift_envelopes"]), ["/phase_energy_j/decode"])
        # An empty recorded map is the same case.
        empty = json.loads(json.dumps(old))
        empty["energy_anchor_shift_envelopes"] = {}
        self.assertIs(_clamp_inverted_operative_envelopes(self.bundle, empty, **kwargs), empty)

    def _with_long_prefill(self, module, bound_s: float):
        """Mirror whose prefill row is the reviewer's [short, long] phase.

        Flat 10 W; windows [0.005 s, 8 s] at the operative bound: the short
        interval inverts, so reduce omits the envelope, and the clamped
        envelope passes the quarter-metric gate (lower_j > 0).
        """

        curve = interval_curve([(-5.0 + i * 0.05, -5.0 + (i + 1) * 0.05, 10.0) for i in range(400)])
        long_prefill = [(curve, [Window(0.5, 0.505), Window(3.0, 11.0)])]
        real = module._group_envelope_contributions

        def rows(reader, version, anchor_curve):
            return [(pointer, long_prefill if pointer == PREFILL else contributions)
                    for pointer, contributions in real(reader, version, anchor_curve)]

        return patch.object(module, "_group_envelope_contributions", side_effect=rows), long_prefill

    def test_passing_clamped_envelope_is_not_added(self) -> None:
        """L9-ENV-4 F1: a clamped envelope never makes a member eligible."""

        just_under, _over = self._bounds()
        old, _new, _oracle = self._rederive(just_under)
        # A long multi-interval member whose other checks pass: only reduce's
        # envelope stamp refuses it.
        bare = json.loads(json.dumps(old))
        gate = _gate_for(bare, PREFILL)
        gate["reasons"] = [UNRECORDED]
        for inner in gate.get("windows", []):
            inner["reasons"] = [UNRECORDED]
        kwargs = dict(authenticated_fiducial_bound_s=just_under,
                      instrument_calibration_physics_cache=self._cache)

        patcher, long_prefill = self._with_long_prefill(whole_window, just_under)
        with patcher:
            new = _clamp_inverted_operative_envelopes(self.bundle, bare, **kwargs)
        envelopes = new["energy_anchor_shift_envelopes"]
        self.assertNotIn(PREFILL, envelopes)
        self.assertEqual(_gate_for(new, PREFILL), _gate_for(bare, PREFILL))
        self.assertEqual(_gate_for(new, PREFILL)["reasons"], [UNRECORDED])
        # The other short phases still clamp (their envelopes refuse).
        for pointer in ("/phase_energy_j/tokenize", "/phase_energy_j/generation_setup"):
            self.assertIn(pointer, envelopes)
            self.assertIn(EXCEEDS, _gate_for(new, pointer)["reasons"])
        assert_gates_self_consistent(self, new)
        self.assertIn(("phase", "prefill"), whole_window._classify_precheck_refusals(new)[1])

        # The oracle (e1b3a0510) defines a passing envelope here; that is the
        # one deliberate difference from it.
        anchor = reduce_module._derive_anchor_context(
            reduce_module.BundleReader(self.bundle), reduce_module.BundleReader(self.bundle).metadata(),
            strict_calibration=True, reducer_version=reduce_module.REDUCER_VERSION,
            authenticated_fiducial_bound_override_s=just_under,
            instrument_calibration_physics_cache=self._cache)
        bounds = (anchor.bundle_bound_s, anchor.fiducial_bound_s or 0.0, anchor.edge_span_s)
        self.assertIsNone(reduce_module._corner_composed_anchor_shift_envelope(long_prefill, *bounds))
        oracle_env = oracle_module()._corner_composed_anchor_shift_envelope(long_prefill, *bounds)
        self.assertGreater(oracle_env["lower_j"], 0.0)
        joint_j = bare["energy_bound_terms_j"]["E_interpolation_joint_edge_bound_j"]
        self.assertEqual(reduce_module._anchor_envelope_gate_reasons(oracle_env, joint_j), [])
        self.assertEqual(_clamped_corner_composed_anchor_shift_envelope(long_prefill, *bounds), oracle_env)

        # Counterfactual at 3e4d359c2: the envelope is added and the gate is
        # left {"eligible": false, "reasons": []} (self-inconsistent).
        base_module = seat_base_whole_window()
        patcher, _ = self._with_long_prefill(base_module, just_under)
        with patcher:
            base = base_module._clamp_inverted_operative_envelopes(self.bundle, bare, **kwargs)
        self.assertEqual(base["energy_anchor_shift_envelopes"][PREFILL], oracle_env)
        base_gate = _gate_for(base, PREFILL)
        self.assertEqual((base_gate["eligible"], base_gate["reasons"]), (False, []))
        self.assertNotIn(("phase", "prefill"), whole_window._classify_precheck_refusals(base)[1])

        # The joint interpolation bound counts (reviewer mutant M16): with it
        # large enough the same envelope refuses, so it is added and restamped.
        wide_joint = json.loads(json.dumps(bare))
        wide_joint["energy_bound_terms_j"]["E_interpolation_joint_edge_bound_j"] = 1e6
        patcher, _ = self._with_long_prefill(whole_window, just_under)
        with patcher:
            added = _clamp_inverted_operative_envelopes(self.bundle, wide_joint, **kwargs)
        self.assertEqual(added["energy_anchor_shift_envelopes"][PREFILL], oracle_env)
        self.assertEqual(_gate_for(added, PREFILL)["reasons"], [EXCEEDS])
        assert_gates_self_consistent(self, added)

    def test_genuinely_missing_operative_envelope_still_refuses(self) -> None:
        just_under, _over = self._bounds()
        _old, new, _oracle = self._rederive(just_under)
        for pointer in (PREFILL, "/gross_energy_j"):
            with self.subTest(pointer=pointer):
                summary = json.loads(json.dumps(new))
                summary["energy_anchor_shift_envelopes"].pop(pointer)
                session = self._session("missing" + pointer.replace("/", "_"), self.minted, just_under,
                                        lambda _path, **_kwargs: summary, analysis_clamp=True)
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
        # _restamp_clamped_gate fail-closed branches (reviewer mutants M09,
        # M15): an eligible gate, an inner window without the stamp, a gate
        # without the stamp.
        eligible = json.loads(json.dumps(old))
        _gate_for(eligible, PREFILL)["eligible"] = True
        self.assertIs(_clamp_inverted_operative_envelopes(self.bundle, eligible, **kwargs), eligible)
        inner = json.loads(json.dumps(old))
        self.assertTrue(_gate_for(inner, PREFILL)["windows"])
        _gate_for(inner, PREFILL)["windows"][0]["reasons"] = []
        self.assertIs(_clamp_inverted_operative_envelopes(self.bundle, inner, **kwargs), inner)
        unstamped = json.loads(json.dumps(old))
        _gate_for(unstamped, PREFILL)["reasons"].remove(UNRECORDED)
        self.assertIs(_clamp_inverted_operative_envelopes(self.bundle, unstamped, **kwargs), unstamped)
        # A recorded group pointer the mirror does not know (mutant M18).
        foreign = json.loads(json.dumps(old))
        envelopes = foreign["energy_anchor_shift_envelopes"]
        envelopes["/phase_energy_j/ghost"] = envelopes["/phase_energy_j/decode"]
        self.assertIs(_clamp_inverted_operative_envelopes(self.bundle, foreign, **kwargs), foreign)
        # Positive control: the same summary unmodified does clamp prefill.
        self.assertIn(PREFILL, _clamp_inverted_operative_envelopes(
            self.bundle, old, **kwargs)["energy_anchor_shift_envelopes"])


    def test_tail_refusal_context_adds_envelopes_without_restamping(self) -> None:
        """Reviewer K4 / mutant M12: reduce stamps no envelope gate reasons on
        ``post_window_trace_tail_shorter_than_anchor_bound``, so neither may the clamp."""

        just_under, _over = self._bounds()
        kwargs = dict(authenticated_fiducial_bound_s=just_under,
                      instrument_calibration_physics_cache=self._cache)
        old, new, _oracle = self._rederive(just_under)
        real = whole_window._derive_anchor_context

        def tail(*args, **kw):
            return dataclasses.replace(
                real(*args, **kw), detail="post_window_trace_tail_shorter_than_anchor_bound")

        with patch.object(whole_window, "_derive_anchor_context", side_effect=tail):
            out = _clamp_inverted_operative_envelopes(self.bundle, old, **kwargs)
        self.assertIsNot(out, old)
        self.assertEqual(out["energy_anchor_shift_envelopes"], new["energy_anchor_shift_envelopes"])
        self.assertIn(PREFILL, out["energy_anchor_shift_envelopes"])
        self.assertEqual(out["window_evidence_precheck"], old["window_evidence_precheck"])
        self.assertNotEqual(new["window_evidence_precheck"], old["window_evidence_precheck"])

    def test_unknown_recorded_member_pointer_fails_closed(self) -> None:
        """Reviewer K4 / mutant M14: an unknown recorded /phase_energy_j/* pointer."""

        for bound_s in (self.minted_bound * 1.5, *self._bounds()):
            with self.subTest(bound=bound_s):
                kwargs = dict(authenticated_fiducial_bound_s=bound_s,
                              instrument_calibration_physics_cache=self._cache)
                old, _new, _oracle = self._rederive(bound_s)
                tampered = json.loads(json.dumps(old))
                envelopes = tampered["energy_anchor_shift_envelopes"]
                envelopes["/phase_energy_j/zz_unknown"] = dict(envelopes["/gross_energy_j"])
                self.assertIs(_clamp_inverted_operative_envelopes(self.bundle, tampered, **kwargs), tampered)


class RestampGateTests(unittest.TestCase):
    """Reviewer K2 (mutants M06/M11): ``_restamp_clamped_gate`` invariants."""

    def test_restamp_replaces_only_the_unrecorded_stamp(self) -> None:
        gate = {"eligible": False, "reasons": [UNRECORDED, "negative_power_sample"],
                "windows": [{"eligible": False, "reasons": [UNRECORDED, "negative_power_sample"]}]}
        self.assertTrue(whole_window._restamp_clamped_gate(gate, [EXCEEDS]))
        expected = [EXCEEDS, "negative_power_sample"]
        self.assertEqual(gate, {"eligible": False, "reasons": expected,
                                "windows": [{"eligible": False, "reasons": expected}]})

    def test_restamp_refuses_gate_without_the_stamp(self) -> None:
        gate = {"eligible": False, "reasons": ["clock_bound_exceeds_quarter_window"]}
        self.assertFalse(whole_window._restamp_clamped_gate(gate, [EXCEEDS]))
        self.assertEqual(gate, {"eligible": False, "reasons": ["clock_bound_exceeds_quarter_window"]})

    def test_restamp_refuses_an_eligible_gate(self) -> None:
        gate = {"eligible": True, "reasons": [UNRECORDED]}
        self.assertFalse(whole_window._restamp_clamped_gate(gate, [EXCEEDS]))
        self.assertEqual(gate, {"eligible": True, "reasons": [UNRECORDED]})

    def test_restamp_never_loosens_eligibility(self) -> None:
        gate = {"eligible": False, "reasons": [UNRECORDED]}
        whole_window._restamp_clamped_gate(gate, [])
        self.assertIs(gate["eligible"], False)
        gate = {"eligible": False, "reasons": [UNRECORDED]}
        self.assertTrue(whole_window._restamp_clamped_gate(gate, [EXCEEDS]))
        self.assertEqual(gate, {"eligible": False, "reasons": [EXCEEDS]})


class AxiV062ClampTests(unittest.TestCase):
    """L9-ENV-4 F5: the 0.6.2 mirror on the real AXI event-v2 fixture.

    ``_install_axi_shape`` binds the committed AXI fixture to the same real
    powermetrics bytes; the per-source request-phase unions and the shifted
    source curves are what reviewer mutants M11/M17 break.
    """

    _cache: dict[str, float] = {}

    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_whole_window_selection import MaxBracketConsumptionTests

        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name)
        class_scope = SimpleNamespace(addCleanup=cls.addClassCleanup)
        source, cls.minted52, cls.minted_bound = _bundle_fixture(class_scope, cls.root / "fixture")
        cls.bundle = MaxBracketConsumptionTests._install_axi_shape(
            cls.root / "axi-v062", calibrated_source=source)
        cls.minted = reduce_module.reduce_bundle(
            cls.bundle, reducer_version=reduce_module.AXI_REDUCER_VERSION,
            _instrument_calibration_physics_cache=cls._cache).to_dict()
        (cls.bundle / "summary_metrics.json").write_text(
            json.dumps(cls.minted, sort_keys=True) + "\n", encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _critical(self) -> float:
        span_s = self.minted["energy_anchor_shift_envelopes"][PREFILL][
            "wall_minus_monotonic_independent_edge_span_s"]
        return _phase_durations(self.minted)["prefill"] / 2.0 - span_s

    def _rederive(self, bound_s: float) -> tuple[dict, dict, dict]:
        kwargs = dict(authenticated_fiducial_bound_s=bound_s,
                      _instrument_calibration_physics_cache=self._cache)
        old = reduce_module._rederive_summary_for_authenticated_fiducial_bound(self.bundle, **kwargs)
        new = _rederive_operative_summary(self.bundle, **kwargs)
        oracle = oracle_module()._rederive_summary_for_authenticated_fiducial_bound(self.bundle, **kwargs)
        for summary in (old, new, oracle):
            self.assertEqual(summary["status"], "succeeded")
            self.assertEqual(summary["summary_provenance"]["reducer_version"],
                             reduce_module.AXI_REDUCER_VERSION)
        assert_gates_self_consistent(self, new)
        self.assertEqual(whole_window._classify_precheck_refusals(old)[0],
                         whole_window._classify_precheck_refusals(new)[0])
        return old, new, oracle

    def test_mirror_reproduces_every_recorded_envelope(self) -> None:
        bound_s = self._critical() + 0.002
        old, _new, _oracle = self._rederive(bound_s)
        reader = reduce_module.BundleReader(self.bundle)
        anchor = reduce_module._derive_anchor_context(
            reader, reader.metadata(), strict_calibration=True,
            reducer_version=reduce_module.AXI_REDUCER_VERSION,
            authenticated_fiducial_bound_override_s=bound_s,
            instrument_calibration_physics_cache=self._cache)
        self.assertNotEqual(anchor.curve[0].t, reader.summed_curve()[0].t)
        rows = whole_window._group_envelope_contributions(
            reader, reduce_module.AXI_REDUCER_VERSION, anchor.curve)
        bounds = (anchor.bundle_bound_s, anchor.fiducial_bound_s or 0.0, anchor.edge_span_s)
        recorded = old["energy_anchor_shift_envelopes"]
        self.assertEqual([pointer for pointer, _rows in rows], ["/phase_energy_j/decode", PREFILL])
        self.assertIn("/phase_energy_j/decode", recorded)
        self.assertNotIn(PREFILL, recorded)
        for pointer, contributions in rows:
            with self.subTest(pointer=pointer):
                envelope = reduce_module._corner_composed_anchor_shift_envelope(contributions, *bounds)
                self.assertEqual(json.dumps(envelope), json.dumps(recorded.get(pointer)))

    def test_mirror_groups_per_source_with_shifted_source_curves(self) -> None:
        """Two sources, overlapping requests, nonzero anchor shift (M11/M17)."""

        raw = interval_curve(stepped_rows(1_784_491_122.0, 80, 0.05, 5))
        sources = {
            "src-b": interval_curve(stepped_rows(1_784_491_122.0, 80, 0.05, 9)),
            "src-a": interval_curve(stepped_rows(1_784_491_122.0, 80, 0.05, 11)),
        }
        base_s = 1_784_491_122.5
        request_windows = {
            ("src-b", "request-000", "prefill", 0): Window(base_s, base_s + 0.2),
            ("src-b", "request-001", "prefill", 0): Window(base_s + 0.1, base_s + 0.4),
            ("src-a", "request-000", "prefill", 0): Window(base_s + 1.0, base_s + 1.1),
            ("src-a", "request-000", "decode", 1): Window(base_s + 1.1, base_s + 2.0),
        }
        reader = SimpleNamespace(
            summed_curve=lambda: raw,
            request_phase_windows=lambda: dict(request_windows),
            source_curve=lambda source: sources[source],
        )
        shift_s = 0.0123
        rows = whole_window._group_envelope_contributions(
            reader, reduce_module.AXI_REDUCER_VERSION, reduce_module._shift_curve(raw, shift_s))

        def shifted(source):
            return reduce_module._shift_curve(sources[source], raw[0].t + shift_s - raw[0].t)

        expected = [
            ("/phase_energy_j/decode", [(shifted("src-a"), [Window(base_s + 1.1, base_s + 2.0)])]),
            (PREFILL, [
                (shifted("src-a"), [Window(base_s + 1.0, base_s + 1.1)]),
                (shifted("src-b"), [Window(base_s, base_s + 0.4)]),
            ]),
        ]
        self.assertEqual(rows, expected)
        self.assertNotEqual(shifted("src-a"), reduce_module._shift_curve(raw, shift_s))

    def test_fake_reader_differential_against_reduce_v060_grouping(self) -> None:
        """Reviewer K3 (mutants M09/M11/M17): two sources, three requests each,
        a negative-offset tokenize phase, and a nonzero anchor shift; the rows
        are rebuilt independently from ``reduce._reduce_v060``'s grouping."""

        rng = random.Random(3)
        raw = {
            source: [TracePoint(t=100.0 + i * 0.05, power_w=rng.uniform(1, 9),
                                support_start_s=100.0 + i * 0.05, support_end_s=100.05 + i * 0.05)
                     for i in range(400)]
            for source in ("meter-b", "meter-a")
        }
        request_windows = {}
        for source in ("meter-a", "meter-b"):
            for request_id in ("r2", "r1", "r3"):
                for phase, (offset_s, duration_s) in {
                    "prefill": (0.0, 0.1), "decode": (0.12, 1.0), "tokenize": (-0.01, 0.0005),
                }.items():
                    base_s = 105.0 + int(request_id[1]) * 0.6 + (0.3 if source == "meter-b" else 0.0)
                    request_windows[(source, request_id, phase, 0)] = Window(
                        base_s + offset_s, base_s + offset_s + duration_s)
        reader = SimpleNamespace(
            summed_curve=lambda: raw["meter-a"],
            source_curve=lambda source: raw[source],
            request_phase_windows=lambda: dict(request_windows),
        )
        shift_s = 0.0123
        anchor = reduce_module._shift_curve(reader.summed_curve(), shift_s)
        rows = whole_window._group_envelope_contributions(
            reader, reduce_module.AXI_REDUCER_VERSION, anchor)
        grouped: dict[str, dict[str, list[Window]]] = {}
        for (source, _request, phase, _ordinal), window in request_windows.items():
            grouped.setdefault(phase, {}).setdefault(source, []).append(window)
        expected = [
            ("/phase_energy_j/" + phase, [
                (reduce_module._shift_curve(raw[source], shift_s),
                 reduce_module._union_windows(grouped[phase][source]))
                for source in sorted(grouped[phase])
            ])
            for phase in sorted(grouped)
        ]
        self.assertEqual(rows, expected)
        # The shift is applied in the anchor's direction (M09/M11 flip it).
        self.assertEqual(rows[0][1][0][0][0].t, raw["meter-a"][0].t + shift_s)

    def test_short_prefill_clamps_and_bounds_sweep_equals_oracle(self) -> None:
        critical_s = self._critical()
        clamped_at = []
        for bound_s in (self.minted_bound, critical_s - 0.002, critical_s + 0.002,
                        critical_s * 1.5, critical_s * 3.0):
            with self.subTest(bound=bound_s):
                old, new, oracle = self._rederive(bound_s)
                expected, excluded = expected_from_oracle(old, oracle)
                self.assertEqual(excluded, [])
                self.assertEqual(json.dumps(new), json.dumps(expected))
                added = set(new.get("energy_anchor_shift_envelopes") or {}) - set(
                    old.get("energy_anchor_shift_envelopes") or {})
                for pointer in added:
                    old_gate, new_gate = _gate_for(old, pointer), _gate_for(new, pointer)
                    self.assertEqual(set(old_gate["reasons"]) - set(new_gate["reasons"]), {UNRECORDED})
                    self.assertEqual(set(new_gate["reasons"]) - set(old_gate["reasons"]), {EXCEEDS})
                    self.assertIs(new_gate["eligible"], False)
                if PREFILL in added:
                    clamped_at.append(bound_s)
                    self.assertEqual(new["energy_anchor_shift_envelopes"][PREFILL]["lower_j"], 0.0)
                if bound_s == critical_s * 3.0:
                    # L9-ENV-5 O-F3: decode inverts too, nothing is recorded,
                    # so the 0.6.2 mirror is unproven and nothing is clamped.
                    self.assertEqual(json.dumps(new), json.dumps(old))
                    self.assertIn(PREFILL, oracle["energy_anchor_shift_envelopes"])
        self.assertEqual(clamped_at, [critical_s + 0.002, critical_s * 1.5])


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
