"""Post-hoc log tampering that preserves every measured turn, call and trace.

The records contract has no scratchpad count separate from hidden_tokens.
The runner stores tokenizer counts in hardware["runner"]["scratchpad_tokens"];
external producers may supply that same adapter metadata. Missing counts are
flagged, never estimated from text or subtracted from measured decode work.
"""

from __future__ import annotations

import math
import random
from dataclasses import replace
from typing import Callable, Iterable

from joulewise.align.records import Episode, ToolCall


def _flag(ep: Episode, *flags: str) -> Episode:
    return replace(ep, flags=tuple(dict.fromkeys((*ep.flags, *flags))))


def delete_turns(ep: Episode, indices: Iterable[int]) -> Episode:
    """Mark the selected zero-based turn indices unlogged; keep their work."""
    selected = set(indices)
    valid = {t.index for t in ep.turns}
    result = replace(ep, turns=tuple(
        replace(t, logged=False) if t.index in selected else t for t in ep.turns))
    result = _flag(result, "tamper.delete_turns")
    if selected - valid:
        result = _flag(result, "tamper.delete_turns.index_out_of_range")
    return result


def drop_tool_calls(ep: Episode, predicate: Callable[[ToolCall], bool]) -> Episode:
    """Mark matching calls unlogged without deleting timing or byte counts."""
    turns = []
    failed = False
    for turn in ep.turns:
        calls = []
        for call in turn.tool_calls:
            try:
                drop = predicate(call)
            except Exception:
                failed = True
                drop = False
            calls.append(replace(call, logged=False) if drop else call)
        turns.append(replace(turn, tool_calls=tuple(calls)))
    result = _flag(replace(ep, turns=tuple(turns)), "tamper.drop_tool_calls")
    return _flag(result, "tamper.drop_tool_calls.predicate_error") if failed else result


def _hide_indices(ep: Episode, indices: set[int]) -> Episode:
    hardware = dict(ep.hardware)
    metadata = dict(hardware.get("runner", {}))
    counts = metadata.get("scratchpad_tokens", {})
    counted = set(metadata.get("scratchpad_counted_hidden", []))
    turns = []
    flags = ["tamper.hide_scratchpad"]
    for turn in ep.turns:
        if turn.index not in indices:
            turns.append(turn)
            continue
        count = counts.get(str(turn.index))
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            flags.append("tamper.hide_scratchpad.count_unavailable")
            turns.append(turn)
            continue
        hidden = turn.hidden_tokens
        if turn.index not in counted:
            hidden += count
            if hidden > turn.decode_tokens:
                flags.append("tamper.hide_scratchpad.count_exceeds_decode")
                hidden = turn.decode_tokens
            counted.add(turn.index)
        turns.append(replace(turn, hidden_tokens=hidden))
    if not any(before.hidden_tokens != after.hidden_tokens
               for before, after in zip(ep.turns, turns)):
        flags.append("tamper.hide_scratchpad.noop")
    metadata["scratchpad_counted_hidden"] = sorted(counted)
    hardware["runner"] = metadata
    return _flag(replace(ep, turns=tuple(turns), hardware=hardware), *flags)


def hide_scratchpad(ep: Episode) -> Episode:
    """Move known scratchpad work into hidden_tokens once, preserving decode."""
    return _hide_indices(ep, {t.index for t in ep.turns})


def random_tamper(ep: Episode, rng: random.Random, kind: str, fraction: float) -> Episode:
    """Select round(fraction * eligible items) with the supplied RNG.

    fraction is an evaluation-set design parameter, not a measured threshold.
    Invalid fractions/kinds produce an unchanged record with diagnostic flags.
    """
    if not math.isfinite(fraction) or not 0.0 <= fraction <= 1.0:
        return _flag(ep, "tamper.random_tamper.invalid_fraction")
    if kind == "delete_turns":
        choices = [t.index for t in ep.turns if t.logged]
        selected = rng.sample(choices, round(len(choices) * fraction))
        result = delete_turns(ep, selected)
    elif kind == "drop_tool_calls":
        choices = [(t.index, i) for t in ep.turns for i, c in enumerate(t.tool_calls)
                   if t.logged and c.logged]
        selected = set(rng.sample(choices, round(len(choices) * fraction)))
        result = replace(ep, turns=tuple(replace(t, tool_calls=tuple(
            replace(c, logged=False) if (t.index, i) in selected else c
            for i, c in enumerate(t.tool_calls))) for t in ep.turns))
        result = _flag(result, "tamper.drop_tool_calls")
    elif kind == "hide_scratchpad":
        choices = [t.index for t in ep.turns if t.logged]
        selected = set(rng.sample(choices, round(len(choices) * fraction)))
        result = _hide_indices(ep, selected)
    else:
        return _flag(ep, "tamper.random_tamper.unknown_kind")
    return _flag(result, "tamper.random_tamper")


__all__ = ["delete_turns", "drop_tool_calls", "hide_scratchpad", "random_tamper"]
