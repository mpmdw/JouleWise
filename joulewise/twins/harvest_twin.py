"""Independent arithmetic oracle for B5/B6 harvests, not a custody validator.

Written from B5-REG §§0.4, 0.10–0.12 and B6-REPL §§1.7–1.8 before
opening the harvest implementation or its tests. Inputs are already decoded,
time-aligned evidence. No production reducer/harvest/statistics kernel is used.
Where the registrations are silent (refusal edges of the timing envelope, the
support-overlap tolerance), it follows production's reducer and reader; those
post-freeze choices are listed in PR #554.
This module never reads a session directory or decides whether it is unblinded.
The caller must authenticate and classify evidence before supplying it.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import math
from statistics import fmean, stdev
from typing import Iterable, Mapping, Sequence


# B5-REG §0.12 / B6-REPL §1.8: t(.975, n-1), rounded to three places.
# The supported corpus sizes are 6–12 (B5 requires at least ten).
_T975 = {5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
         10: 2.228, 11: 2.201}


def _finite(value: float, name: str, *, nonnegative: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    value = float(value)
    if not math.isfinite(value) or (nonnegative and value < 0):
        raise ValueError(f"invalid {name}")
    return value


@dataclass(frozen=True)
class PowerInterval:
    start_s: float
    end_s: float
    power_w: float

    def __post_init__(self) -> None:
        for name in ("start_s", "end_s", "power_w"):
            object.__setattr__(self, name, _finite(getattr(self, name), name,
                                                nonnegative=name == "power_w"))
        if self.end_s <= self.start_s:
            raise ValueError("power interval must have positive duration")


def _trace(records: Iterable[PowerInterval]) -> tuple[PowerInterval, ...]:
    result = tuple(records)
    if not result:
        raise ValueError("empty power trace")
    # Match bundle_read's interval-support representation tolerance (1 us).
    # At 45 W, the top of the request power range, 1 us * 45 W = 4.5e-5 J,
    # below 1e-4 of the approximately 1 J attribution limit; both supports count.
    if any(a.start_s > b.start_s or b.start_s < a.end_s - 1e-6
           for a, b in zip(result, result[1:])):
        raise ValueError("power intervals overlap or are out of order")
    return result


def _integral(records: Sequence[PowerInterval], start: float, end: float) -> float:
    return math.fsum(row.power_w * max(0.0, min(end, row.end_s)
                                      - max(start, row.start_s)) for row in records)


def overlap_energy(records: Iterable[PowerInterval], start_s: float,
                   end_s: float) -> float:
    """B5-REG §0.4: clip each interval to the requested phase; sum W × s."""
    rows = _trace(records)
    start = _finite(start_s, "start_s")
    end = _finite(end_s, "end_s")
    if end < start:
        raise ValueError("reversed phase")
    return _integral(rows, start, end)


@dataclass(frozen=True)
class TimingEnvelope:
    point_j: float
    minimum_j: float
    maximum_j: float
    max_abs_delta_j: float


def anchor_envelope(records: Iterable[PowerInterval], start_s: float,
                    end_s: float, operative_fiducial_s: float,
                    wall_minus_monotonic_span_s: float,
                    effective_clock_bound_s: float) -> TimingEnvelope:
    """Exact four edge corners × every common-shift breakpoint (REG §0.10).

    Within each corner E is piecewise linear in the common shift. Thus its
    extrema occur at ±m or when either displaced edge meets any record edge.
    Refuse a reversed displaced corner or trace support that does not cover
    every corner under every common shift: unmeasured power is not zero.
    Equality at a zero-length corner or at a support edge is allowed.
    """
    rows = _trace(records)
    start = _finite(start_s, "start_s")
    end = _finite(end_s, "end_s")
    if end < start:
        raise ValueError("reversed phase")
    # Work in elapsed coordinates before applying small shifts. At 2026
    # epochs, adding a millisecond shift first discards about 1e-7 seconds.
    origin = rows[0].start_s
    rows = tuple(PowerInterval(r.start_s - origin, r.end_s - origin, r.power_w)
                 for r in rows)
    start, end = start - origin, end - origin
    g = math.fsum((_finite(operative_fiducial_s, "fiducial", nonnegative=True),
                   _finite(wall_minus_monotonic_span_s, "span", nonnegative=True)))
    m = _finite(effective_clock_bound_s, "clock bound", nonnegative=True)
    trace_start = min(row.start_s for row in rows)
    trace_end = max(row.end_s for row in rows)
    point = _integral(rows, start, end)
    extrema = [point]
    boundaries = {edge for row in rows for edge in (row.start_s, row.end_s)}
    for e_on, e_off in product((-g, g), repeat=2):
        left, right = start + e_on, end + e_off
        if right < left:
            raise ValueError("reversed displaced corner")
        # Production's strict comparisons, in elapsed coordinates: all
        # supports together must cover [start - g - m, end + g + m].
        if trace_start + m > left or trace_end - m < right:
            raise ValueError("trace does not cover displaced phase and common shift")
        shifts = {-m, m}
        shifts.update(edge - displaced for edge in boundaries
                      for displaced in (left, right)
                      if -m <= edge - displaced <= m)
        extrema.extend(_integral(rows, left + d, right + d) for d in shifts)
    lower, upper = min(extrema), max(extrema)
    return TimingEnvelope(point, lower, upper, max(point - lower, upper - point))


@dataclass(frozen=True)
class CalibrationBracket:
    observed_drift_s: float
    drift_allowance_s: float
    operative_fiducial_s: float


def calibration_bracket(opening_s: float, closing_s: float,
                        bracket_screen_s: float, *,
                        maximum_allowance_s: float | None = None) -> CalibrationBracket:
    """B5-REG §0.11; B6-REPL §§1.7, 3.3. Acceptance supplies the screen.

    A supplied maximum enforces B5's ceiling on max(observed drift, screen).
    With None this is arithmetic only: block 6's drift budget only flags
    (calibration.drift_above_budget), so it must not refuse that arithmetic.
    """
    pre, post, screen = (_finite(v, name, nonnegative=True) for v, name in (
        (opening_s, "opening"), (closing_s, "closing"), (bracket_screen_s, "screen")))
    drift = abs(post - pre)
    allowance = max(drift, screen)
    if maximum_allowance_s is not None:
        maximum = _finite(maximum_allowance_s, "maximum allowance", nonnegative=True)
        if allowance > maximum:
            raise ValueError("calibration drift allowance exceeds maximum")
    return CalibrationBracket(drift, allowance, max(pre, post) + allowance)


@dataclass(frozen=True)
class MemberArithmetic:
    gross_energy_j: float
    idle_subtracted_energy_j: float
    phase_energy_j: Mapping[str, float]
    phase_envelopes: Mapping[str, TimingEnvelope]
    phase_bounds_j: Mapping[str, Mapping[str, float]]


def member_arithmetic(records: Iterable[PowerInterval], request: tuple[float, float],
                      phases: Mapping[str, tuple[float, float]], *, idle_power_w: float,
                      operative_fiducial_s: float, wall_minus_monotonic_span_s: float,
                      effective_clock_bound_s: float,
                      whole_window_drift_allowance_j: float) -> MemberArithmetic:
    """Gross/idle-subtracted request, gross phases, and the three bound kinds.

    B5-REG §0.10 and B5-PLAN §4.4: interval-support interpolation is explicitly
    zero; every member gets HALF the reference-derived gross drift allowance.
    """
    rows = _trace(records)
    start, end = (_finite(v, "request edge") for v in request)
    idle = _finite(idle_power_w, "idle power", nonnegative=True)
    drift = _finite(whole_window_drift_allowance_j, "drift allowance", nonnegative=True)
    gross = overlap_energy(rows, start, end)
    energies, envelopes, bounds = {}, {}, {}
    for name, (on, off) in phases.items():
        if not start <= on <= off <= end:
            raise ValueError("phase outside request")
        env = anchor_envelope(rows, on, off, operative_fiducial_s,
                              wall_minus_monotonic_span_s, effective_clock_bound_s)
        energies[name] = env.point_j
        envelopes[name] = env
        bounds[name] = {"E_clock_anchor_shift_bound_j": env.max_abs_delta_j,
                        "E_interpolation_joint_edge_bound_j": 0.0,
                        "E_whole_window_drift_allowance_j": drift / 2}
    return MemberArithmetic(gross, gross - idle * (end - start), energies,
                            envelopes, bounds)


@dataclass(frozen=True)
class ReferenceEnergy:
    gross_j: float
    idle_subtracted_j: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "gross_j", _finite(self.gross_j, "gross", nonnegative=True))
        # Idle subtraction may legitimately make a diagnostic energy negative.
        object.__setattr__(self, "idle_subtracted_j", _finite(self.idle_subtracted_j, "idle-subtracted"))


@dataclass(frozen=True)
class DriftFamily:
    corpus_n: int
    start_n: int
    end_n: int
    start_mean_j: float
    end_mean_j: float
    difference_j: float
    envelope_j: float
    repeatability_j: float
    bound_j: float
    spread_j: float
    allowance_j: float
    passed: bool


def endpoint_bound(corpus: Sequence[float], start_n: int,
                    end_n: int) -> tuple[float, float, float]:
    """REG §0.12: return envelope, repeatability, and their maximum."""
    values = sorted(_finite(v, "corpus energy") for v in corpus)
    if len(values) - 1 not in _T975:
        raise ValueError("registered corpus size must be 6–12")
    if any(type(n) is not int or not 1 <= n <= 3 for n in (start_n, end_n)):
        raise ValueError("endpoint count must be 1–3")
    upper = lambda n: fmean(values[-n:])
    lower = lambda n: fmean(values[:n])
    envelope = max(upper(start_n) - lower(end_n), upper(end_n) - lower(start_n))
    repeatability = _T975[len(values) - 1] * stdev(values) * math.sqrt(1 / start_n + 1 / end_n)
    return envelope, repeatability, max(envelope, repeatability)


def _drift_family(corpus: Sequence[float], start: Sequence[float],
                  end: Sequence[float], midpoint: float | None) -> DriftFamily:
    envelope, repeatability, bound = endpoint_bound(corpus, len(start), len(end))
    a, b = fmean(start), fmean(end)
    trajectory = [a, b] if midpoint is None else [a, midpoint, b]
    difference = abs(b - a)
    spread = max(trajectory) - min(trajectory)
    return DriftFamily(len(corpus), len(start), len(end), a, b, difference,
                       envelope, repeatability, bound, spread, max(spread, bound),
                       difference <= bound)


@dataclass(frozen=True)
class SessionDrift:
    gross: DriftFamily
    idle_subtracted: DriftFamily
    passed: bool
    member_drift_allowance_j: float


def session_drift(corpus: Sequence[ReferenceEnergy | None],
                   start: Sequence[ReferenceEnergy | None],
                   end: Sequence[ReferenceEnergy | None],
                   midpoint: ReferenceEnergy | None, *, block: int = 5) -> SessionDrift:
    """First twelve clean corpus runs, survivors only, both energy families.

    None denotes a reference already classified lost by the evidence reader.
    B5 needs ten clean corpus runs; B6 needs six. Both need 2–3 survivors at
    each endpoint. Lost midpoint falls back to the endpoint difference.
    Diagnostic interior references are intentionally absent from this API.
    """
    if block not in (5, 6):
        raise ValueError("block must be 5 or 6")
    if len(start) > 3 or len(end) > 3:
        raise ValueError("endpoint roster exceeds three slots")
    clean = [row for row in corpus if row is not None][:12]
    left = [row for row in start if row is not None]
    right = [row for row in end if row is not None]
    if len(clean) < (10 if block == 5 else 6) or min(len(left), len(right)) < 2:
        raise ValueError("insufficient surviving references")
    families = [_drift_family([getattr(r, field) for r in clean],
                              [getattr(r, field) for r in left],
                              [getattr(r, field) for r in right],
                              None if midpoint is None else getattr(midpoint, field))
                for field in ("gross_j", "idle_subtracted_j")]
    gross, net = families
    return SessionDrift(gross, net, gross.passed and net.passed, gross.allowance_j / 2)
