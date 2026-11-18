"""RL-176 B.1 descriptive prints on already loaded episode records."""

from bisect import bisect_left, bisect_right
from collections import defaultdict
from dataclasses import dataclass, replace
import math
from statistics import fmean

from joulewise.adapters.powermetrics import RAIL_MANIFEST
from joulewise.align.attribution import attribute_episode
from joulewise.align.records import ClockMapping, Episode, PowerTrace

NS = 1_000_000_000
GPU = ("powermetrics", "gpu_power")
CPU = ("powermetrics", "cpu_power")
PACKAGE = ("powermetrics", "package")
DC = ("wall_meter", "dc_in")
RAILS = {"gpu": GPU, "cpu": CPU, "package": PACKAGE}
PHASES = ("prefill", "decode", "tool", "other")
TIMING_EDGE_J = 1.0
CTL_DOSES = (10, 30, 90)
CTL_LEG_COUNT = 12


@dataclass(frozen=True)
class ControlLeg:
    episode: Episode
    cpu_burn_s: int | None = None


def selected_trace(episode: Episode, channel: tuple[str, str]) -> tuple[
    PowerTrace | None, ClockMapping | None
]:
    matches = [t for t in episode.power_traces if (t.source, t.channel) == channel]
    if len(matches) != 1 or len(matches[0].t_ns) < 2 or matches[0].unit != "W":
        return None, None
    trace = matches[0]
    if trace.clock_domain == episode.clock_domain:
        return trace, None
    matches = [m for m in episode.clock_mappings
               if (m.trace_domain, m.episode_domain) == (trace.clock_domain, episode.clock_domain)]
    return (trace, matches[0]) if len(matches) == 1 else (None, None)


def with_package(episode):
    """Recover the adapter's package rail sum on its shared native support."""
    if any((t.source, t.channel) == PACKAGE for t in episode.power_traces):
        return episode
    traces = [selected_trace(episode, ("powermetrics", name))[0] for name in RAIL_MANIFEST]
    if any(t is None for t in traces):
        return episode
    base = traces[0]
    if any((t.t_ns, t.clock_domain, t.nominal_interval_ns, t.averaging_window_ns, t.duty_fraction)
           != (base.t_ns, base.clock_domain, base.nominal_interval_ns, base.averaging_window_ns,
               base.duty_fraction) for t in traces[1:]):
        return episode
    package = replace(base, channel=PACKAGE[1], values=tuple(map(math.fsum, zip(
        *(t.values for t in traces)))))
    return replace(episode, power_traces=(*episode.power_traces, package))


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def segment_joules(segments):
    values = [s.energy.joules for s in segments]
    return math.fsum(values) if all(map(finite, values)) else None


def phase_table(episode, channel, attribution=None):
    """Tile ungated time, checking closure against independently integrated total."""
    if channel == PACKAGE:
        episode = with_package(episode)
    trace, _ = selected_trace(episode, channel)
    if trace is None:
        return {"closes": False, "reason": "trace_or_clock_unavailable"}
    source, name = channel
    if attribution is None:
        attribution = attribute_episode(episode, source=source, channel=name)
    buckets = {key: [] for key in PHASES}
    excluded = []
    missing_first_token = {t.index for t in episode.turns if t.first_token_ns is None}
    for segment in attribution.segments:
        if segment.kind in ("gate", "hold"):
            excluded.append(segment)
        else:
            phase = segment.kind
            if phase == "gap" or (phase == "decode" and segment.turn in missing_first_token):
                phase = "other"
            buckets[phase].append(segment)

    phases = {}
    for name, segments in buckets.items():
        seconds = sum(s.end_ns - s.start_ns for s in segments) / NS
        joules = segment_joules(segments)
        phases[name] = {
            "seconds": seconds, "joules": joules,
            "mean_watts": joules / seconds if joules is not None and seconds else None,
        }
    missing_logged_decode = any(t.logged and t.decode_tokens and t.index in missing_first_token
                                for t in episode.turns)
    totals = episode.totals(logged_only=True)
    for phase in ("prefill", "decode"):
        joules = phases[phase]["joules"]
        tokens = totals[f"{phase}_tokens"]
        phases[phase]["joules_per_token"] = (
            joules / tokens if joules is not None and tokens and not missing_first_token else None
        )
    total_j = attribution.total.joules
    excluded_j = segment_joules(excluded)
    ungated = total_j - excluded_j if finite(total_j) and excluded_j is not None else None
    phase_j = [row["joules"] for row in phases.values()]
    summed = math.fsum(phase_j) if all(map(finite, phase_j)) else None
    error = abs(summed - ungated) if summed is not None and ungated is not None else None
    relative = error / abs(ungated) if ungated and error is not None else None
    return {"phases": phases, "ungated_j": ungated, "phase_sum_j": summed,
            "absolute_error_j": error, "relative_error": relative,
            "closes": error is not None and error <= 0.01 * abs(ungated)
            and all(finite(segment.energy.half_width_j)
                    and "trace.partial_coverage" not in segment.energy.flags
                    for segment in attribution.segments if segment.kind not in ("gate", "hold")),
            "missing_first_token_turns": sorted(missing_first_token),
            "missing_logged_decode_boundary": missing_logged_decode}


def phase_metrics(table):
    phases = table.get("phases")
    if phases is None or not table["closes"] or table["missing_first_token_turns"]:
        return {}
    tool = phases["tool"]["joules"]
    other = phases["other"]["joules"]
    return {
        "decode_energy": phases["decode"]["joules"],
        "prefill_energy": phases["prefill"]["joules"],
        "tool_plus_other_energy": tool + other if tool is not None and other is not None else None,
        "mean_decode_watts": phases["decode"]["mean_watts"],
        "joules_per_decode_token": phases["decode"]["joules_per_token"],
    }


def _event_times(episode, native_ns):
    events = defaultdict(list)
    short, calls = 0, 0
    for turn in episode.turns:
        events["turn_start"].append(turn.start_ns)
        events["turn_end"].append(turn.end_ns)
        if turn.first_token_ns is not None:
            events["first_token"].append(turn.first_token_ns)
        for call in turn.tool_calls:
            calls += 1
            if call.end_ns - call.start_ns < 2 * native_ns:
                short += 1
            else:
                events["tool_start"].append(call.start_ns)
                events["tool_end"].append(call.end_ns)
    return events, short, calls


def _member_profile(episode, trace, mapping):
    period = trace.nominal_interval_ns
    events, short, calls = _event_times(episode, period)
    offset = mapping.offset_ns if mapping is not None else 0
    output = {}
    for event, stamps in events.items():
        across_events = defaultdict(list)
        for stamp in stamps:
            center = stamp - offset
            lo = bisect_left(trace.t_ns, center - 5 * NS)
            hi = bisect_right(trace.t_ns, center + 10 * NS)
            per_event = defaultdict(list)
            for pos in range(lo, hi):
                delta = trace.t_ns[pos] - center
                bin_ns = ((2 * delta + period) // (2 * period)) * period
                if -5 * NS <= bin_ns <= 10 * NS and finite(trace.values[pos]):
                    per_event[bin_ns].append(trace.values[pos])
            for bin_ns, values in per_event.items():
                across_events[bin_ns].append(fmean(values))
        output[event] = {tick: fmean(values) for tick, values in across_events.items()}
    return output, short, calls


def event_profiles(window_episodes, *, include_dc=True):
    """Average native samples by event, then member, window and across windows."""
    by_window = defaultdict(list)
    grid_members = defaultdict(set)
    short_calls = defaultdict(lambda: [0, 0])
    for window, episode in window_episodes:
        episode = with_package(episode)
        channels = {**RAILS, "dc_in": DC} if include_dc and episode.condition == "benign" else RAILS
        for rail, channel in channels.items():
            trace, mapping = selected_trace(episode, channel)
            if trace is None or trace.nominal_interval_ns <= 0:
                continue
            period = trace.nominal_interval_ns
            member, short, calls = _member_profile(episode, trace, mapping)
            short_calls[rail][0] += short
            short_calls[rail][1] += calls
            if any(member.values()):
                grid_members[(rail, period)].add((window, episode.episode_id))
            for event, bins in member.items():
                for tick, watts in bins.items():
                    by_window[(rail, period, event, tick, window)].append(watts)
    across_windows = defaultdict(list)
    for (rail, period, event, tick, _), values in by_window.items():
        across_windows[(rail, period, event, tick)].append(fmean(values))
    profiles = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for (rail, period, event, tick), values in sorted(across_windows.items()):
        profiles[rail][str(period)][event].append({
            "relative_ns": tick, "mean_watts": fmean(values),
            "window_range_watts": [min(values), max(values)], "windows": len(values),
        })
    grid_counts = defaultdict(dict)
    for (rail, period), members in sorted(grid_members.items()):
        grid_counts[rail][str(period)] = {
            "members": len(members), "windows": len({window for window, _ in members}),
        }
    return {
        "timing_edge_j": TIMING_EDGE_J,
        "profile_counts": dict(grid_counts),
        "window_ns": [-5 * NS, 10 * NS],
        "profiles": {rail: {period: dict(events) for period, events in grids.items()}
                     for rail, grids in profiles.items()},
        "short_tool_calls": {
            rail: {"short": short, "total": total, "share": short / total if total else None}
            for rail, (short, total) in short_calls.items()
        },
    }


def qualify_ctl01(legs):
    """Run the same phase code on the complete conditionless control block."""
    if legs is None:
        return {"qualified": "not_run", "legs": []}
    legs = tuple(legs)
    rows, burns = [], defaultdict(list)
    for leg in legs:
        phases = {rail: phase_table(leg.episode, channel) for rail, channel in RAILS.items()}
        cpu_other = phases["cpu"].get("phases", {}).get("other", {}).get("joules")
        if leg.cpu_burn_s is not None:
            burns[leg.cpu_burn_s].append(cpu_other)
        rows.append({"episode_id": leg.episode.episode_id, "cpu_burn_s": leg.cpu_burn_s,
                     "closed": all(row["closes"] for row in phases.values()), "rails": phases})
    doses_complete = set(burns) == set(CTL_DOSES) and all(
        len(values) == 1 and finite(values[0]) for values in burns.values()
    )
    order_ok = doses_complete and burns[10][0] < burns[30][0] < burns[90][0]
    all_closed = (len(rows) == len({row["episode_id"] for row in rows}) == CTL_LEG_COUNT
                  and all(row["closed"] for row in rows))
    return {"qualified": "yes" if all_closed and order_ok else "no",
            "legs": rows, "all_legs_close": all_closed, "cpu_burn_order": order_ok,
            "event_profiles": event_profiles(
                (("ctl-01", leg.episode) for leg in legs), include_dc=False)}
