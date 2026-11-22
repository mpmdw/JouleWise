"""RL-187 print calculations over authenticated, in-memory records."""

from collections import defaultdict
from dataclasses import dataclass, replace
from math import ceil, fsum, isfinite, sqrt
from statistics import median

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


def _finite(value):
    return type(value) in (float, int) and isfinite(value)


def _nonnegative_int(value):
    return type(value) is int and value >= 0


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
        rows = record["steps"]
        if tuple(row["kind"] for row in rows) != (*SCRIPT_STEPS[kind], "recovery"):
            raise ViewError("script_order")
        for row in rows:
            step = Step(row["kind"], row["started_ns"], row["ended_ns"], row["complete"])
            if (not _nonnegative_int(step.start_ns) or not _nonnegative_int(step.end_ns)
                    or step.end_ns < step.start_ns or type(step.complete) is not bool):
                raise ViewError("step_bounds")
            if step.kind in ("hidden", "turn"):
                step = replace(step, first_ns=row["first_token_ns"], requested_tokens=row["requested_tokens"],
                               delivered_tokens=row["actual_tokens"], context_tokens=row["context_tokens"])
                if (not all(map(_nonnegative_int, (step.requested_tokens, step.delivered_tokens,
                                                    step.context_tokens)))
                        or not 0 <= step.delivered_tokens <= step.requested_tokens
                        or (step.first_ns is not None and (not _nonnegative_int(step.first_ns)
                            or not step.start_ns <= step.first_ns <= step.end_ns))):
                    raise ViewError("call_counts_or_bounds")
            else:
                seconds = row["requested_s"]
                if (not _finite(seconds) or seconds <= 0
                        or (step.kind == "cpu" and (type(seconds) is not int or seconds not in (10, 30, 90)))):
                    raise ViewError("interval_dose")
                step = replace(step, requested_s=seconds)
            yield step
    except (ManifestError, TypeError, KeyError) as error:
        raise ViewError("script_record_shape") from error


def physical_call_view(leg: LegInput):
    """Replace just the logged turn. Keep the original episode and trace bounds."""
    episode = leg.episode
    if (episode is None or len(episode.turns) != 1 or episode.turns[0].logged is not True
            or episode.turns[0].tool_calls):
        raise ViewError("logged_envelope")
    steps = tuple(_read_steps(leg.work_bytes, leg.work_sha256, leg.leg_id, leg.kind))
    gates = (interval["end_ns"] for interval in episode.hardware.get("thermal", {}).get("intervals", ())
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
    other = [segment for segment in segments if segment.kind == "gap"
             or (segment.kind == "decode" and segment.turn in missing)]
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
    for segment in other:
        cursor = segment.start_ns
        for name, start, end in explicit:
            start, end = max(start, segment.start_ns), min(end, segment.end_ns)
            if end <= start:
                continue
            if cursor < start:
                parts["remainder"].append((cursor, start))
            parts[name].append((start, end))
            cursor = end
        if cursor < segment.end_ns:
            parts["remainder"].append((cursor, segment.end_ns))
    for name in {name for name, _, _ in explicit}:
        if sum(end - start for start, end in parts[name]) != sum(
            end - start for key, start, end in explicit if key == name
        ):
            raise ViewError("other_partition")
    return parts


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
    offset = mapping.offset_ns if mapping is not None else 0
    return any(b - a > limit and a < end - offset and b > start - offset
               for a, b in zip(trace.t_ns, trace.t_ns[1:]))


def _energy(kernel, trace, mapping, start, end):
    estimate = kernel.trace_energy(trace, start, end, mapping=mapping)
    if "trace.partial_coverage" in estimate.flags or not _finite(estimate.joules):
        return None
    return estimate.joules


def _baseline(kernel, trace, mapping, recovery, gap_limit):
    end = recovery.end_ns
    start = end - 40 * NS
    if not recovery.complete or start < recovery.start_ns:
        return None, "recovery_incomplete", None, "recovery_incomplete"
    if _has_gap(trace, mapping, start, end, gap_limit):
        return None, "gap_over_u1", None, "gap_over_u1"
    energy = _energy(kernel, trace, mapping, start, end)
    if energy is None:
        return None, "trace_or_clock_unavailable", None, "trace_or_clock_unavailable"
    previous = start - 40 * NS
    if previous < recovery.start_ns:
        return energy / 40, None, None, "recovery_incomplete"
    if _has_gap(trace, mapping, previous, start, gap_limit):
        return energy / 40, None, None, "gap_over_u1"
    prior = _energy(kernel, trace, mapping, previous, start)
    if prior is None:
        return energy / 40, None, None, "trace_or_clock_unavailable"
    return energy / 40, None, prior - energy, None


def _above(joules, seconds, baseline):
    return None if joules is None or baseline is None else joules - seconds * baseline


def _channel_values(kernel, view, episode, name, attrs, parts, gap_limit):
    channel = TRACE_CHANNELS[name]
    trace, mapping = kernel.phases.selected_trace(episode, channel)
    if trace is None:
        return {"reason": "trace_or_clock_unavailable", "baseline_w": None,
                "baseline_reason": "trace_or_clock_unavailable"}
    if name == "dc_in" and _has_gap(trace, mapping, episode.start_ns, episode.end_ns, gap_limit):
        baseline, reason, _, _ = _baseline(kernel, trace, mapping, view.steps[-1], gap_limit)
        return {"reason": "gap_over_u1", "baseline_w": baseline, "baseline_reason": reason}
    table = kernel.phases.phase_table(episode, channel, attrs)
    baseline, reason, drift, drift_reason = _baseline(kernel, trace, mapping, view.steps[-1], gap_limit)
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


def dose_fit(points_by_leg):
    """Fit whole hidden-call energy with an intercept and leave-one-out extrema."""
    points = tuple(points_by_leg.values())
    if len(points) < 4 or len({tokens for tokens, _ in points}) != 3:
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


def print_controls(positions, *, kernel, gap_limits_ns, pooled, instrument_manifest_sha256):
    """Produce the private calculations for all twelve bound positions."""
    positions = tuple(positions)
    if tuple(leg.leg_id for leg in positions) != PILOT + REMAINDER:
        raise ValueError("roster")
    if any(type(leg.kind) is not str or leg.kind not in SCRIPT_STEPS for leg in positions):
        raise ValueError("script_kind")
    if not _hex_pin(instrument_manifest_sha256, 64):
        raise ValueError("instrument_pin")
    rows, controls = [], []
    fit_points = {name: {} for name in CHANNELS}
    for leg in positions:
        row = {"leg_id": leg.leg_id, "kind": leg.kind}
        rows.append(row)
        if leg.episode is None or not leg.g0_released:
            row["disposition"] = "not_dispatched" if not leg.g0_released else "episode_missing"
            continue
        try:
            view = physical_call_view(leg)
            episode = kernel.phases.with_package(view.episode)
            attrs = {name: kernel.attribute_episode(episode, source=source, channel=channel)
                     for name, (source, channel) in TRACE_CHANNELS.items()}
            parts = _other_parts(view, attrs["gpu_rail"].segments)
        except ViewError as error:
            row.update(disposition="not_evaluable", reason=str(error))
            continue
        controls.append(kernel.phases.ControlLeg(episode, view.cpu_dose))
        visible = tuple(step for step in view.steps if step.kind == "turn")
        envelope = {"prompt_tokens": sum(step.context_tokens for step in visible),
                    "decode_tokens": sum(step.delivered_tokens for step in visible)}
        row.update(disposition="admitted" if leg.admitted and not view.short else "unadmitted",
                   delivery="short" if view.short else "as_requested", calls=_project_steps(view.steps),
                   envelope=envelope, channels={})
        for name in CHANNELS:
            channel = _channel_values(kernel, view, episode, name, attrs[name], parts, gap_limits_ns[name])
            row["channels"][name] = channel
            if "absolute" not in channel:
                continue
            def units(joules, duration, reason=channel["baseline_reason"]):
                return floor_units(joules, duration, name, pooled, instrument_manifest_sha256,
                                   baseline_reason=reason)

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
                if leg.admitted and not view.short and hidden["call_j"] is not None:
                    fit_points[name][leg.leg_id] = (hidden["delivered_tokens"], hidden["call_j"])
    alignment = kernel.phases.qualify_ctl01(controls if any(leg.episode is not None for leg in positions) else None)
    qualifier = {field: alignment[field] for field in ("qualified", "all_legs_close", "cpu_burn_order")
                 if field in alignment}
    return {"legs": rows, "timing_edge_j": kernel.phases.TIMING_EDGE_J, "aligned_power": qualifier,
            "dose_response": {name: dose_fit(points) for name, points in fit_points.items()}}
