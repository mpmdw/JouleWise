"""Canonical ALIGN episode stop classification.

The classifier is deliberately independent of adapters and diagnostics so the
runtime artifact and later desk summaries cannot disagree about concurrent
causes.  Flags retain every cause; this module only selects the primary one.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

FAULT_PREFIXES = ("runner.error", "episode_error:", "endpoint_error:")


def has_fault(flags: Iterable[str]) -> bool:
    """Return whether any retained flag represents a runner/episode fault."""
    return any(flag.startswith(FAULT_PREFIXES) for flag in flags)


def primary_stop(
    flags: Sequence[str], *, thermal_intervals: Iterable[Mapping[str, object]] = (),
    default: str = "episode_returned",
) -> str:
    """Select one stop while preserving all concurrent causes in ``flags``.

    Governed deadman aborts outrank faults.  Runtime faults then outrank
    malformed tool calls, thermal censoring, decode-budget, and ordinary stops.
    Unobserved G1/H intervals are valid flagged episodes, not incomplete ones.
    """
    deadman = next((f for f in flags if f.startswith("episode.deadman:")), None)
    if deadman:
        return "episode.deadman"
    if has_fault(flags):
        return "runner.error"
    if any(f.startswith("episode.malformed_tool_call:") for f in flags):
        return "episode.malformed_tool_call"
    thermal = next((f for f in flags if f.startswith(("thermal.gate_timeout:", "thermal.hold_timeout:"))), None)
    if thermal or any(
        row.get("kind") != "G0" and row.get("outcome") in ("timeout", "deadman")
        for row in thermal_intervals
    ):
        return "thermal.incomplete"
    ordered = (
        ("episode.decode_budget:", "episode.decode_budget"),
        ("episode.end_task:", "episode.end_task"),
        ("episode.time_guard:", "episode.time_guard"),
        ("episode.context_limit:", "episode.context_limit"),
        ("turn_token_budget_reached:", "turn_token_budget_reached"),
    )
    for prefix, stop in ordered:
        if any(flag.startswith(prefix) for flag in flags):
            return stop
    if "turn_budget_reached" in flags:
        return "turn_budget_reached"
    return default
