"""RL-187 print calculations over authenticated, in-memory records."""

from bisect import bisect_left, bisect_right
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, replace
from math import ceil, fsum, isfinite, sqrt
from statistics import median
from sys import float_info
from types import MappingProxyType

from .controls_print import (
    CHANNELS, PILOT, REMAINDER, SCRIPT_STEPS, ControlsRefusal, _hex_pin, validate_script_pin,
)
from .qualification_manifest import _decode, ManifestError


NS = 1_000_000_000
FLOOR_WINDOWS = (10, 40, 128)
BASELINE_REASONS = frozenset({"trace_or_clock_unavailable", "recovery_incomplete", "gap_over_u1"})
TRACE_CHANNELS = {
    "gpu_rail": ("powermetrics", "gpu_power"),
    "cpu_rail": ("powermetrics", "cpu_power"),
    "rail_sum": ("powermetrics", "package"),
    "dc_in": ("wall_meter", "dc_in"),
}


class ViewError(ValueError):
    """The physical-call view failed a named RL-187 check."""


class LegRecordError(Exception):
    """A frozen numerical operation refused an authenticated leg record."""


VALUE_DEPENDENT_REASONS = frozenset({"nonfinite_sample", "nonfinite_estimate"})


class ValueReadError(ValueError):
    """A measured sample or calculation is unusable."""

    def __init__(self, reason):
        if reason not in VALUE_DEPENDENT_REASONS:
            raise ValueError("unknown measurement failure")
        super().__init__(reason)


def _record_call(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except ViewError:
        raise
    except ValueError as error:
        # RecordError is also a ValueError. The callers are the ruled sites.
        raise LegRecordError() from error


@dataclass(frozen=True)
class Step:
    kind: str
    start_ns: int
    end_ns: int
    complete: bool
    first_ns: int | None = None
    requested_tokens: int | None = None
    delivered_tokens: int | None = None
    context_tokens: int | None = None
    requested_s: float | None = None


@dataclass(frozen=True)
class PhysicalView:
    episode: object
    steps: tuple[Step, ...]

    @property
    def short(self):
        return any(step.delivered_tokens < step.requested_tokens for step in self.steps
                   if step.kind in ("hidden", "turn"))

    @property
    def cpu_dose(self):
        return next((step.requested_s for step in self.steps if step.kind == "cpu" and step.complete), None)


@dataclass(frozen=True)
class LegInput:
    leg_id: str
    kind: str
    admitted: bool
    g0_released: bool
    episode: object | None = None
    work_bytes: bytes | None = None
    work_sha256: str | None = None


@dataclass(frozen=True)
class TraceTiming:
    t_ns: tuple[int, ...]
    nominal_interval_ns: int


@dataclass(frozen=True)
class ChannelTiming:
    reason: str | None
    baseline_reason: str | None
    drift_reason: str | None

    @property
    def fit_supported(self):
        return self.reason is None and self.baseline_reason is None


@dataclass(frozen=True)
class LegAdmission:
    disposition: str
    reason: str | None = None
    view: PhysicalView | None = None
    parts: Mapping | None = None
    channels: Mapping | None = None
    rail_gaps: tuple[tuple[str, str], ...] = ()

    @property
    def admitted(self):
        return self.disposition == "admitted"


@dataclass(frozen=True)
class NativeLegInput(LegInput):
    admission: LegAdmission | None = None


def _finite(value):
    if type(value) is int:
        return -float_info.max <= value <= float_info.max
    return type(value) is float and isfinite(value)


def _nonnegative_int(value):
    return type(value) is int and value >= 0


def _step(row, *, interrupted=False):
    kind = row["kind"]
    call = kind in ("hidden", "turn")
    start = row.get("started_ns") if interrupted and call else row["started_ns"]
    end = row.get("ended_ns") if interrupted else row["ended_ns"]
    if (any(not _nonnegative_int(row[key]) for key in ("started_ns", "ended_ns") if key in row)
            or (end is not None and (start is None or end < start))
            or type(row["complete"]) is not bool):
        raise ViewError("step_bounds")
    if call:
        first = row.get("first_token_ns") if interrupted else row["first_token_ns"]
        context = row.get("context_tokens") if interrupted else row["context_tokens"]
        requested, delivered = row["requested_tokens"], row["actual_tokens"]
        counts = [requested]
        if not interrupted or "context_tokens" in row:
            counts.append(context)
        if not interrupted or delivered is not None:
            counts.append(delivered)
        if (not all(_nonnegative_int(value) and _finite(value) for value in counts)
                or (delivered is not None and delivered > requested)
                or (first is not None and (not _nonnegative_int(first) or start is None
                    or end is None or not start <= first <= end))):
            raise ViewError("call_counts_or_bounds")
        if interrupted:
            return None
        return Step(kind, start, end, row["complete"], first_ns=first, requested_tokens=requested,
                    delivered_tokens=delivered, context_tokens=context)
    seconds = row["requested_s"]
    if (not _finite(seconds) or seconds <= 0
            or (kind == "cpu" and (type(seconds) is not int or seconds not in (10, 30, 90)))):
        raise ViewError("interval_dose")
    return None if interrupted else Step(kind, start, end, row["complete"], requested_s=seconds)


def script_steps(record, kind, *, allow_interrupted=False):
    """Validate the closed step sequence and the wire shape of each reached step."""
    try:
        rows = record["steps"]
        names = tuple(row["kind"] for row in rows)
        expected = (*SCRIPT_STEPS[kind], "recovery")
        if names != (expected[:len(rows)] if allow_interrupted else expected):
            raise ViewError("script_order")
        steps = []
        for index, row in enumerate(rows):
            # The native writer can leave only its last, failed call or
            # interval unfinished. A finished call always has actual tokens.
            interrupted = (allow_interrupted and index == len(rows) - 1 and row["complete"] is False
                           and (row["kind"] not in ("hidden", "turn") or row["actual_tokens"] is None))
            steps.append(_step(row, interrupted=interrupted))
        visible = [row for row in rows if row["kind"] == "turn"]
        prompt_total = sum(row.get("context_tokens", 0) for row in visible)
        decode_total = sum(row["actual_tokens"] or 0 for row in visible)
        # Both totals can become denominators in the frozen phase calculation.
        if not (_finite(prompt_total) and _finite(decode_total)):
            raise ViewError("aggregate_token_counts")
        return tuple(steps)
    except (TypeError, KeyError) as error:
        raise ViewError("script_record_shape") from error


def _read_steps(payload, digest, leg_id, kind):
    if payload is None:
        raise ViewError("script_record_missing")
    try:
        validate_script_pin(payload, digest)
    except ControlsRefusal as error:
        raise ViewError("script_digest") from error
    try:
        record = _decode(payload)
        if (record["schema"] != "joulewise.cadence_script_work.v1" or record["leg_id"] != leg_id
                or record["script"]["kind"] != kind):
            raise ViewError("script_identity")
        return script_steps(record, kind)
    except (ManifestError, TypeError, KeyError) as error:
        raise ViewError("script_record_shape") from error


def thermal_intervals(hardware):
    """Validate the interval structure shared by the blind and value readers."""
    thermal = hardware.get("thermal", {})
    if not isinstance(thermal, Mapping):
        raise ViewError("thermal_interval_shape")
    intervals = thermal.get("intervals", ())
    if not isinstance(intervals, (list, tuple)):
        raise ViewError("thermal_interval_shape")
    previous = None
    for row in intervals:
        if not isinstance(row, Mapping) or row.get("kind") not in ("G0", "G1", "H"):
            raise ViewError("thermal_interval_shape")
        start, end = row.get("start_ns"), row.get("end_ns")
        if (type(start) is not int or type(end) is not int or start > end
                or (previous is not None and start < previous)
                or (row["kind"] == "H" and not _nonnegative_int(row.get("turn")))):
            raise ViewError("thermal_interval_shape")
        previous = end
    return intervals


def physical_call_view(leg: LegInput, *, projected_work=None):
    """Replace just the logged turn. Keep the original episode and trace bounds."""
    episode = leg.episode
    if (episode is None or len(episode.turns) != 1 or episode.turns[0].logged is not True
            or episode.turns[0].tool_calls):
        raise ViewError("logged_envelope")
    steps = (_read_steps(leg.work_bytes, leg.work_sha256, leg.leg_id, leg.kind) if projected_work is None
             else script_steps(projected_work, leg.kind))
    gates = (interval["end_ns"] for interval in thermal_intervals(episode.hardware)
             if interval["kind"] == "G0")
    previous = max(episode.start_ns, max(gates, default=episode.start_ns))
    for step in steps:
        if step.start_ns < previous or step.end_ns > episode.end_ns:
            raise ViewError("step_order_or_episode_bounds")
        previous = step.end_ns

    envelope = episode.turns[0]
    visible = tuple(step for step in steps if step.kind == "turn")
    if (not all(map(_nonnegative_int, (envelope.prefill_tokens, envelope.context_tokens,
                                      envelope.decode_tokens, envelope.hidden_tokens)))
            or envelope.hidden_tokens != 0
            or sum(step.context_tokens for step in visible) != envelope.prefill_tokens + envelope.context_tokens
            or sum(step.delivered_tokens for step in visible) != envelope.decode_tokens):
        raise ViewError("envelope_counts")
    if (visible[0].start_ns, visible[0].first_ns) != (envelope.start_ns, envelope.first_token_ns):
        raise ViewError("envelope_stamps")

    turns = tuple(replace(envelope, index=index, start_ns=step.start_ns, end_ns=step.end_ns,
                          first_token_ns=step.first_ns, context_tokens=0, prefill_tokens=step.context_tokens,
                          decode_tokens=step.delivered_tokens, hidden_tokens=0)
                  for index, step in enumerate(visible))
    return PhysicalView(replace(episode, turns=turns), steps)


def _project_steps(steps):
    rows = []
    for step in steps:
        row = {"kind": step.kind, "duration_s": (step.end_ns - step.start_ns) / NS}
        if step.kind in ("turn", "hidden"):
            row.update(requested_tokens=step.requested_tokens, delivered_tokens=step.delivered_tokens,
                       context_tokens=step.context_tokens)
        else:
            row["requested_s"] = step.requested_s
        rows.append(row)
    return rows


def _other_parts(view, segments):
    """Intersect named work with frozen other segments, retaining the remainder."""
    missing = {turn.index for turn in view.episode.turns if turn.first_token_ns is None}
    other = [(start, end) for turn, kind, start, end in segments
             if kind == "gap" or (kind == "decode" and turn in missing)]
    explicit = []
    for step in view.steps:
        if step.kind == "hidden":
            if step.first_ns is None:
                explicit.append(("hidden", step.start_ns, step.end_ns))
            else:
                explicit.extend((("hidden_prefill", step.start_ns, step.first_ns),
                                 ("hidden_decode", step.first_ns, step.end_ns)))
        elif step.kind != "turn":
            explicit.append((step.kind, step.start_ns, step.end_ns))

    parts = defaultdict(list)
    for segment_start, segment_end in other:
        cursor = segment_start
        for name, start, end in explicit:
            start, end = max(start, segment_start), min(end, segment_end)
            if end <= start:
                continue
            if cursor < start:
                parts["remainder"].append((cursor, start))
            parts[name].append((start, end))
            cursor = end
        if cursor < segment_end:
            parts["remainder"].append((cursor, segment_end))
    for name in {name for name, _, _ in explicit}:
        if sum(end - start for start, end in parts[name]) != sum(
            end - start for key, start, end in explicit if key == name
        ):
            raise ViewError("other_partition")
    return parts


def _physical_partition(episode, work, kind):
    from joulewise.align.attribution import _segments

    if any(interval["kind"] == "G0" and interval["end_ns"] > episode.start_ns
           for interval in thermal_intervals(episode.hardware)):
        raise LegRecordError()
    leg = LegInput(work["leg_id"], kind, False, True, episode)
    view = physical_call_view(leg, projected_work=work)
    segments = _record_call(_segments, view.episode, [])
    return view, _other_parts(view, segments), segments


def prepare_admission(position, episode, work, issued, traces):
    """Determine native participation using the bound kit and blind records."""
    if not position["g0_released"]:
        return LegAdmission("not_dispatched")
    if not position["script_complete"]:
        return LegAdmission("not_evaluable", "script_incomplete")
    if not position["admitted"]:
        return LegAdmission("not_evaluable", "runner_unadmitted")
    try:
        view, parts, segments = _physical_partition(episode, work, issued["kind"])
    except ViewError as error:
        return LegAdmission("not_evaluable", str(error))
    except LegRecordError:
        return LegAdmission("not_evaluable", "leg_record_invalid")
    if any(not step.complete for step in view.steps):
        return LegAdmission("not_evaluable", "script_incomplete")
    turns = iter(issued["turn_tokens"])
    for step in view.steps:
        if step.kind in ("turn", "hidden"):
            tokens = next(turns) if step.kind == "turn" else issued["hidden_tokens"]
            if step.delivered_tokens != tokens:
                return LegAdmission("not_evaluable", "token_delivery")
        elif step.kind in ("gap", "recovery"):
            seconds = issued[f"{step.kind}_s"]
            # Compare the exact monotonic nanoseconds against the binary64
            # issued duration without rounding the measured interval.
            numerator, denominator = seconds.as_integer_ratio()
            if (step.end_ns - step.start_ns) * denominator < numerator * NS:
                reason = "gap_incomplete" if step.kind == "gap" else "recovery_incomplete"
                return LegAdmission("not_evaluable", reason)
    channels = {name: _channel_timing(view, name, *traces[name]) for name in CHANNELS}
    rail_gaps = _blind_rail_gaps(parts, segments, traces)
    return LegAdmission("admitted", view=view,
                        parts=MappingProxyType({name: tuple(ranges) for name, ranges in parts.items()}),
                        channels=MappingProxyType(channels), rail_gaps=rail_gaps)


def blind_view_refusal(episode, work, kind):
    """Report the physical-view portion of the blind verdict."""
    try:
        _physical_partition(episode, work, kind)
    except ViewError as error:
        return str(error)
    except LegRecordError:
        return "leg_record_invalid"
    return None


@dataclass(frozen=True)
class PhaseKernel:
    phases: object
    attribute_episode: object
    trace_energy: object

    @classmethod
    def frozen(cls):
        from joulewise.align.apple import rl176_phases
        from joulewise.align.attribution import attribute_episode, trace_energy

        return cls(rl176_phases, attribute_episode, trace_energy)


def _has_gap(trace, mapping, start, end, limit):
    times = trace.t_ns
    offset = mapping.offset_ns if mapping is not None else 0
    lo = max(0, bisect_right(times, start - offset) - 1)
    hi = min(bisect_left(times, end - offset), len(times) - 1)
    return any(times[index + 1] - times[index] > limit for index in range(lo, hi))


def _blind_rail_gaps(parts, segments, traces):
    measured = {name: list(ranges) for name, ranges in parts.items()}
    for _, kind, start, end in segments:
        if kind in ("prefill", "decode", "tool"):
            measured.setdefault(kind, []).append((start, end))
    marks = []
    # The native component traces share one verified grid and mapping.
    for name in ("cpu_rail", "gpu_rail", "rail_sum"):
        trace, mapping = traces[name]
        limit = registered_u1_ns(trace, name)
        marks.extend((name, part) for part, ranges in sorted(measured.items())
                     if any(end > start and _has_gap(trace, mapping, start, end, limit) for start, end in ranges))
    return tuple(marks)


def registered_u1_ns(trace, channel):
    """Apply the registered U1 rule to the authenticated trace cadence."""
    if channel == "dc_in":
        return 2 * NS
    period = trace.nominal_interval_ns
    if type(period) is not int or period <= 0:
        raise ValueError("controls_cadence")
    return max(NS, 5 * period)


def _channel_timing(view, name, trace, mapping, gap_limit=None):
    """Select timestamp support for the two recovery windows and the fit."""
    unavailable = "trace_or_clock_unavailable"
    if trace is None or len(trace.t_ns) < 2:
        return ChannelTiming(unavailable, unavailable, unavailable)
    limit = registered_u1_ns(trace, name) if gap_limit is None else gap_limit
    episode = view.episode
    reason = ("gap_over_u1" if name == "dc_in"
              and _has_gap(trace, mapping, episode.start_ns, episode.end_ns, limit) else None)
    recovery = view.steps[-1]
    end = recovery.end_ns
    start = end - 40 * NS
    if not recovery.complete or start < recovery.start_ns:
        return ChannelTiming(reason, "recovery_incomplete", "recovery_incomplete")
    if _has_gap(trace, mapping, start, end, limit):
        return ChannelTiming(reason, "gap_over_u1", "gap_over_u1")
    previous = start - 40 * NS
    drift_reason = ("recovery_incomplete" if previous < recovery.start_ns else
                    "gap_over_u1" if _has_gap(trace, mapping, previous, start, limit) else None)
    return ChannelTiming(reason, None, drift_reason)


def _energy(kernel, trace, mapping, start, end):
    estimate = kernel.trace_energy(trace, start, end, mapping=mapping)
    if "trace.partial_coverage" in estimate.flags or not _finite(estimate.joules):
        return None
    return estimate.joules


def _baseline(kernel, trace, mapping, recovery, coverage):
    end = recovery.end_ns
    start = end - 40 * NS
    if coverage.baseline_reason is not None:
        return None, coverage.baseline_reason, None, coverage.drift_reason
    energy = _energy(kernel, trace, mapping, start, end)
    if energy is None:
        return None, "trace_or_clock_unavailable", None, "trace_or_clock_unavailable"
    previous = start - 40 * NS
    if coverage.drift_reason is not None:
        return energy / 40, None, None, coverage.drift_reason
    prior = _energy(kernel, trace, mapping, previous, start)
    if prior is None:
        return energy / 40, None, None, "trace_or_clock_unavailable"
    return energy / 40, None, prior - energy, None


def _above(joules, seconds, baseline):
    return None if joules is None or baseline is None else joules - seconds * baseline


def _channel_values(kernel, view, episode, name, attrs, parts, coverage):
    channel = TRACE_CHANNELS[name]
    trace, mapping = kernel.phases.selected_trace(episode, channel)
    if coverage.reason == "trace_or_clock_unavailable":
        return {"reason": coverage.reason, "baseline_w": None, "baseline_reason": coverage.baseline_reason}
    if coverage.reason is not None:
        baseline, reason, _, _ = _baseline(kernel, trace, mapping, view.steps[-1], coverage)
        return {"reason": coverage.reason, "baseline_w": baseline, "baseline_reason": reason}
    table = _record_call(kernel.phases.phase_table, episode, channel, attrs)
    baseline, reason, drift, drift_reason = _baseline(kernel, trace, mapping, view.steps[-1], coverage)
    above = {key: _above(phase["joules"], phase["seconds"], baseline)
             for key, phase in table["phases"].items()}
    detailed = {}
    for key, ranges in parts.items():
        seconds = sum(end - start for start, end in ranges) / NS
        values = [_energy(kernel, trace, mapping, start, end) for start, end in ranges]
        absolute = fsum(values) if all(value is not None for value in values) else None
        detailed[key] = {"seconds": seconds, "joules": absolute,
                         "above_baseline_j": _above(absolute, seconds, baseline)}

    result = {"absolute": table, "baseline_w": baseline, "baseline_reason": reason,
              "baseline_drift_j": drift, "baseline_drift_reason": drift_reason,
              "above_baseline_j": above, "other": detailed}
    hidden = next((step for step in view.steps if step.kind == "hidden"), None)
    if hidden is not None:
        whole = _energy(kernel, trace, mapping, hidden.start_ns, hidden.end_ns)
        decode = detailed.get("hidden_decode", {}).get("above_baseline_j")
        divisor = hidden.delivered_tokens
        divisor_reason = None
        if not divisor:
            divisor_reason = "zero_tokens"
        elif hidden.first_ns is None:
            divisor_reason = "missing_first_token"
        elif decode is None:
            divisor_reason = reason or "trace_coverage"
        result["hidden"] = {
            "delivered_tokens": divisor, "seconds": (hidden.end_ns - hidden.start_ns) / NS,
            "call_j": _above(whole, (hidden.end_ns - hidden.start_ns) / NS, baseline),
            "prefill_j": detailed.get("hidden_prefill", {}).get("above_baseline_j"),
            "decode_j": decode, "j_per_token": decode / divisor if divisor and decode is not None else None,
            "j_per_token_reason": divisor_reason,
            "tail_cut": name == "dc_in",
        }
    return result


def _ols(points):
    mean_tokens = fsum(tokens for tokens, _ in points) / len(points)
    mean_j = fsum(joules for _, joules in points) / len(points)
    slope = (fsum((tokens - mean_tokens) * (joules - mean_j) for tokens, joules in points)
             / fsum((tokens - mean_tokens) ** 2 for tokens, _ in points))
    return slope, mean_j - slope * mean_tokens


def has_dose_quorum(doses):
    doses = tuple(doses)
    return len(doses) >= 4 and len(set(doses)) == 3


def dose_fit(points_by_leg):
    """Fit whole hidden-call energy with an intercept and leave-one-out extrema."""
    points = tuple(points_by_leg.values())
    if not has_dose_quorum(tokens for tokens, _ in points):
        return {"slope": None, "intercept": None, "range": None, "reason": "insufficient_legs",
                "legs": tuple(points_by_leg)}
    slope, intercept = _ols(points)
    refits = [_ols(points[:index] + points[index + 1:])[0] for index in range(len(points))]
    return {"slope": slope, "intercept": intercept, "range": (min(refits), max(refits)),
            "reason": None, "legs": tuple(points_by_leg)}


@dataclass(frozen=True)
class HoldWindow:
    member: tuple[str, str, str]  # kit, kit digest, leg
    channel: str
    window_s: int
    retained: int
    sd_w: float | None
    reason: str | None = None


class HoldPool(dict):
    """Pooled windows with the reason vocabulary from the verified input schema."""

    def __init__(self, *args, reason_enum=()):
        super().__init__(*args)
        self.reason_enum = frozenset(reason_enum)
        if any(type(reason) is not str or not reason or reason == "missing_floor" for reason in self.reason_enum):
            raise ValueError("floor_reason")


def _is_hold_null_reason(reason, reason_enum):
    return type(reason) is str and reason in reason_enum


def validate_instrument_pins(manifest_bytes, hold_bytes, edges_bytes, *, manifest_sha256,
                             hold_sha256, edges_sha256):
    """Check the three committed source byte strings before using a projection."""
    for payload, expected in ((manifest_bytes, manifest_sha256), (hold_bytes, hold_sha256),
                              (edges_bytes, edges_sha256)):
        try:
            validate_script_pin(payload, expected)
        except ControlsRefusal as error:
            raise ValueError("instrument_pin") from error


def pool_hold_windows(rows, qualified_members, *, reason_enum=()):
    """Pool the per-leg hold variances over the committed instrument roster."""
    reason_enum = frozenset(reason_enum)
    seen, weights, variance, nulls = set(), defaultdict(int), defaultdict(list), defaultdict(set)
    for row in rows:
        if row.member not in qualified_members:
            raise ValueError("instrument_member")
        key = (row.channel, row.window_s)
        if (row.channel not in ("gpu_rail", "rail_sum", "dc_in") or row.window_s not in FLOOR_WINDOWS
                or (row.member, key) in seen or not _nonnegative_int(row.retained)):
            raise ValueError("instrument_window")
        if row.reason is not None and not _is_hold_null_reason(row.reason, reason_enum):
            raise ValueError("floor_reason")
        seen.add((row.member, key))
        if row.sd_w is None:
            if row.reason is not None:
                nulls[key].add(row.reason)
            continue
        if not _finite(row.sd_w) or row.sd_w < 0 or row.retained < 2:
            raise ValueError("instrument_variance")
        weight = row.retained - 1
        weights[key] += weight
        variance[key].append(weight * row.sd_w ** 2)
    windows = ((channel, window) for channel in ("gpu_rail", "rail_sum", "dc_in")
               for window in FLOOR_WINDOWS)
    return HoldPool({key: (sqrt(fsum(variance[key]) / weights[key]), ()) if weights[key]
                     else (None, tuple(sorted(nulls[key]))) for key in windows}, reason_enum=reason_enum)


def floor_units(joules, duration_s, channel, pooled, manifest_sha256, *, baseline_reason=None):
    """Describe a phased energy value against its own duration's pooled floor."""
    if channel == "cpu_rail":
        return {"joules": joules, "duration_s": duration_s, "floor_j": None,
                "window_s": None, "units": None, "reason": "no_matched_floor"}
    if not _hex_pin(manifest_sha256, 64):
        raise ValueError("instrument_pin")
    window = max((width for width in FLOOR_WINDOWS if width <= duration_s), default=10)
    sd, reasons = pooled[(channel, window)]
    reason_enum = pooled.reason_enum if type(pooled) is HoldPool else ()
    if type(reasons) is not tuple or any(not _is_hold_null_reason(reason, reason_enum) for reason in reasons):
        raise ValueError("floor_reason")
    if sd is not None and (not _finite(sd) or sd < 0):
        raise ValueError("instrument_variance")
    floor = None if sd is None else sd * duration_s
    if baseline_reason is not None and baseline_reason not in BASELINE_REASONS:
        raise ValueError("baseline_reason")
    reason = (reasons[0] if reasons and floor is None else baseline_reason) if joules is None or not floor else None
    return {"joules": joules, "duration_s": duration_s, "floor_j": floor, "window_s": window,
            "units": joules / floor if floor and joules is not None else None,
            "under_shortest_window": duration_s < 10, "instrument_manifest_sha256": manifest_sha256,
            "reason": reason}


@dataclass(frozen=True)
class ReadParameters:
    hidden_tokens: tuple[int, int, int]
    recovery_s: float
    gap_s: int
    prefill_tokens: int


def read_parameters(*, gpu_token_floors, dc_token_floors, return_bounds,
                    decode_end_lags, qualified_prefills):
    """Calculate the counterfactual RL-187 §3.7 settings for the read.

    Return values use the reported upper bound for ``under`` and None for
    ``never returned``. Decode-end lags use None for ``over 1 s``.
    RL-197 fixes the actual issued-kit settings independently of this read.
    """
    gpu, dc = tuple(gpu_token_floors), tuple(dc_token_floors)
    prefills = sorted(set(qualified_prefills), key=lambda size: abs(size - 2000))
    withheld = withheld_reason(gpu, dc, prefills)
    if withheld:
        raise ValueError({"no_dc_in_floor": "missing_token_floor", "no_prefill_size": "prefill_requires_ruling",
                          "dose_under_floor_at_k2": "dose_requires_ruling"}[withheld])
    threshold = min(median(gpu), median(dc)) if gpu else 0
    dose = next((candidate for candidate in (128, 256, 512) if candidate >= threshold), None)
    bounds, lags = tuple(return_bounds), tuple(decode_end_lags)
    if any(value is not None and (not _finite(value) or value < 0) for value in (*bounds, *lags)):
        raise ValueError("missing_instrument_timing")
    never_returned = not bounds or None in bounds
    returned = max(bounds) if not never_returned else None
    recovery = 600 if never_returned else min(600, max(120, 5 * returned))
    if not lags or None in lags:
        gap = 60 if never_returned else min(60, max(10, ceil(returned)))
    else:
        gap = max(10, ceil(5 * max(lags)))
    if len(prefills) > 1 and abs(prefills[0] - 2000) == abs(prefills[1] - 2000):
        raise ValueError("prefill_requires_ruling")
    return ReadParameters((dose, 2 * dose, 4 * dose), recovery, gap, prefills[0])


def withheld_reason(gpu_token_floors, dc_token_floors, qualified_prefills):
    """Evaluate RL-197's ordered reservation reasons on qualified observations."""
    if any(not _finite(value) or value < 0 for value in (*gpu_token_floors, *dc_token_floors)):
        raise ValueError("instrument_floor_observation")
    if any(not _nonnegative_int(value) or not value for value in qualified_prefills):
        raise ValueError("instrument_prefill_observation")
    if not dc_token_floors:
        return "no_dc_in_floor"
    if not qualified_prefills:
        return "no_prefill_size"
    if gpu_token_floors and min(median(gpu_token_floors), median(dc_token_floors)) > 512:
        return "dose_under_floor_at_k2"
    return None


def _rail_gap_marks(kernel, episode, attribution, parts, leg_id, gap_limits_ns):
    measured = {name: list(ranges) for name, ranges in parts.items()}
    for segment in attribution.segments:
        if segment.kind in ("prefill", "decode", "tool"):
            measured.setdefault(segment.kind, []).append((segment.start_ns, segment.end_ns))
    marks = []
    for name in ("cpu_rail", "gpu_rail", "rail_sum"):
        components = (TRACE_CHANNELS[name],) if name != "rail_sum" else (
            TRACE_CHANNELS["cpu_rail"], TRACE_CHANNELS["gpu_rail"], ("powermetrics", "ane_power"),
        )
        affected = set()
        for component in components:
            trace, mapping = kernel.phases.selected_trace(episode, component)
            if trace is None:
                continue
            limit = gap_limits_ns[name] if gap_limits_ns is not None else None
            if limit is None:
                limit = _record_call(registered_u1_ns, trace, name)
            affected.update(part for part, ranges in measured.items()
                            if any(end > start and _has_gap(trace, mapping, start, end, limit)
                                   for start, end in ranges))
        marks.extend({"leg_id": leg_id, "channel": name, "part": part} for part in sorted(affected))
    return marks


def _format_leg(row, view, channels, pooled, instrument_manifest_sha256, *, short=False):
    visible = tuple(step for step in view.steps if step.kind == "turn")
    envelope = {"prompt_tokens": sum(step.context_tokens for step in visible),
                "decode_tokens": sum(step.delivered_tokens for step in visible)}
    row.update(delivery="short" if short else "as_requested", calls=_project_steps(view.steps),
               envelope=envelope, channels=channels)
    for name, channel in channels.items():
        if "absolute" not in channel:
            continue

        def units(joules, duration, reason=channel["baseline_reason"]):
            return floor_units(joules, duration, name, pooled, instrument_manifest_sha256, baseline_reason=reason)

        channel["phase_floors"] = {
            phase: units(joules, channel["absolute"]["phases"][phase]["seconds"])
            for phase, joules in channel["above_baseline_j"].items()
        }
        channel["baseline_drift_floor"] = units(channel["baseline_drift_j"], 40,
                                                 channel["baseline_drift_reason"])
        for part in channel["other"].values():
            part["floor"] = units(part["above_baseline_j"], part["seconds"])
        hidden = channel.get("hidden")
        if hidden is not None:
            hidden["floor"] = units(hidden["call_j"], hidden["seconds"])


def _print_result(kernel, rows, controls, marks, fit_points, ran):
    alignment = kernel.phases.qualify_ctl01(controls if ran else None)
    qualifier = {field: alignment[field] for field in ("qualified", "all_legs_close", "cpu_burn_order")
                 if field in alignment}
    result = {"legs": rows, "timing_edge_j": kernel.phases.TIMING_EDGE_J, "aligned_power": qualifier,
              "dose_response": {name: dose_fit(points) for name, points in fit_points.items()}}
    if marks:
        result["rail_gap_marks"] = marks
    return result


def _measured_fit_point(hidden):
    if not _finite(hidden["call_j"]):
        raise ValueReadError("nonfinite_estimate")
    return hidden["delivered_tokens"], hidden["call_j"]


def print_admitted_controls(positions, *, kernel, pooled, instrument_manifest_sha256):
    """Calculate native results with the scientific participation set already fixed."""
    rows, controls, marks = [], [], []
    fit_points = {name: {} for name in CHANNELS}
    for leg in positions:
        admission = leg.admission
        row = {"leg_id": leg.leg_id, "kind": leg.kind, "disposition": admission.disposition}
        rows.append(row)
        if admission.reason is not None:
            row["reason"] = admission.reason
        if admission.admitted:
            view = admission.view
            episode = kernel.phases.with_package(replace(leg.episode, turns=view.episode.turns))
            parts = admission.parts
            channels = {name: _channel_values(kernel, view, episode, name, None, parts,
                                              admission.channels[name]) for name in CHANNELS}
            marks.extend({"leg_id": leg.leg_id, "channel": name, "part": part}
                         for name, part in admission.rail_gaps)
            controls.append(kernel.phases.ControlLeg(episode, view.cpu_dose))
            _format_leg(row, view, channels, pooled, instrument_manifest_sha256)
            if leg.kind == "hidden":
                for name, coverage in admission.channels.items():
                    if coverage.fit_supported:
                        try:
                            fit_points[name][leg.leg_id] = _measured_fit_point(channels[name]["hidden"])
                        except ValueReadError:
                            continue
    return _print_result(kernel, rows, controls, marks, fit_points, any(leg.g0_released for leg in positions))


def print_controls(positions, *, kernel, pooled, instrument_manifest_sha256, gap_limits_ns=None):
    """Calculate from legacy frozen record fixtures."""
    positions = tuple(positions)
    if tuple(leg.leg_id for leg in positions) != PILOT + REMAINDER:
        raise ValueError("roster")
    if any(type(leg.kind) is not str or leg.kind not in SCRIPT_STEPS for leg in positions):
        raise ValueError("script_kind")
    if not _hex_pin(instrument_manifest_sha256, 64):
        raise ValueError("instrument_pin")
    rows, controls, marks = [], [], []
    fit_points = {name: {} for name in CHANNELS}
    for leg in positions:
        row = {"leg_id": leg.leg_id, "kind": leg.kind}
        rows.append(row)
        if leg.episode is None or not leg.g0_released:
            row["disposition"] = "not_dispatched" if not leg.g0_released else "episode_missing"
            continue
        try:
            view = physical_call_view(leg)
            episode = _record_call(kernel.phases.with_package, view.episode)
            attrs = {name: _record_call(kernel.attribute_episode, episode, source=source, channel=channel)
                     for name, (source, channel) in TRACE_CHANNELS.items()}
            segments = ((s.turn if s.kind == "decode" else None, s.kind, s.start_ns, s.end_ns)
                        for s in attrs["gpu_rail"].segments)
            parts = _record_call(_other_parts, view, segments)
            channels = {}
            for name in CHANNELS:
                trace, mapping = kernel.phases.selected_trace(episode, TRACE_CHANNELS[name])
                limit = None if gap_limits_ns is None else gap_limits_ns[name]
                coverage = _record_call(_channel_timing, view, name, trace, mapping, limit)
                channels[name] = _channel_values(kernel, view, episode, name, attrs[name], parts, coverage)
            leg_marks = _rail_gap_marks(kernel, episode, attrs["gpu_rail"], parts,
                                        leg.leg_id, gap_limits_ns)
        except ViewError as error:
            row.update(disposition="not_evaluable", reason=str(error))
            continue
        except LegRecordError:
            row.update(disposition="not_evaluable", reason="leg_record_invalid")
            continue
        marks.extend(leg_marks)
        controls.append(kernel.phases.ControlLeg(episode, view.cpu_dose))
        short = view.short
        admitted = leg.admitted and not short
        row["disposition"] = "admitted" if admitted else "unadmitted"
        _format_leg(row, view, channels, pooled, instrument_manifest_sha256, short=short)
        for name, channel in channels.items():
            hidden = channel.get("hidden")
            if admitted and hidden is not None and hidden["call_j"] is not None:
                fit_points[name][leg.leg_id] = (hidden["delivered_tokens"], hidden["call_j"])
    return _print_result(kernel, rows, controls, marks, fit_points, any(leg.episode is not None for leg in positions))
