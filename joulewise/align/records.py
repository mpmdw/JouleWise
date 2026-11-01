"""Shared records for the alignment research pipeline (docs/align/PIPELINE.md).

Every lane of the pipeline reads and writes these records and nothing else
crosses a lane boundary. The module is stdlib-only, like the core package.

Clock rule: every timestamp is an integer nanosecond count in a named clock
domain. Records written on one host use that host's monotonic clock and name
it in ``clock_domain``; a power trace sampled on another host (or by a meter)
names its own domain, and the episode carries the offset estimate that maps
one onto the other (``ClockMapping``). No record stores wall-clock floats.

Serialisation: ``to_json``/``from_json`` round-trip exactly (integers stay
integers, floats are written with ``repr``). ``SCHEMA`` names the version; a
reader refuses a record whose schema it does not know.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, get_args, get_type_hints

SCHEMA = "joulewise.align.records.v1"

Condition = Literal["benign", "sabotage"]
PowerSource = Literal["nvml_power", "nvml_energy", "nvidia_smi", "ina3221", "powermetrics", "wall_meter", "mock"]
Visibility = Literal["full", "no_scratchpad", "actions_only", "tampered"]


class RecordError(ValueError):
    """A record is malformed; the message names the field."""


@dataclass(frozen=True)
class ToolCall:
    """One tool invocation inside a turn, as the agent loop observed it."""

    name: str
    start_ns: int
    end_ns: int
    args_bytes: int
    result_bytes: int
    logged: bool = True  # False when a tamper simulation removed it from the visible log

    def __post_init__(self) -> None:
        _check_interval("ToolCall", self.start_ns, self.end_ns)
        _check_nonneg("ToolCall", args_bytes=self.args_bytes, result_bytes=self.result_bytes)


@dataclass(frozen=True)
class Turn:
    """One model call: a prefill of ``prefill_tokens`` then ``decode_tokens`` generated.

    ``hidden_tokens`` counts generated tokens the monitor never sees (a hidden
    scratchpad or a reasoning block stripped before logging); they are part of
    ``decode_tokens``. ``context_tokens`` is the KV length before this turn's
    prefill (the cached prefix), so the prefill attends over
    ``context_tokens + prefill_tokens`` positions.
    """

    index: int
    start_ns: int
    end_ns: int
    context_tokens: int
    prefill_tokens: int
    decode_tokens: int
    hidden_tokens: int = 0
    first_token_ns: int | None = None  # end of prefill, when the server reports it
    tool_calls: tuple[ToolCall, ...] = ()
    logged: bool = True

    def __post_init__(self) -> None:
        _check_interval("Turn", self.start_ns, self.end_ns)
        _check_nonneg("Turn", index=self.index, context_tokens=self.context_tokens,
                      prefill_tokens=self.prefill_tokens, decode_tokens=self.decode_tokens,
                      hidden_tokens=self.hidden_tokens)
        if self.hidden_tokens > self.decode_tokens:
            raise RecordError("Turn.hidden_tokens exceeds decode_tokens")
        if self.first_token_ns is not None and not self.start_ns <= self.first_token_ns <= self.end_ns:
            raise RecordError("Turn.first_token_ns outside the turn")


@dataclass(frozen=True)
class MonitorVerdict:
    """A monitor's suspicion score for one episode under one visibility."""

    monitor_model: str
    visibility: Visibility
    suspicion: float  # 0..100, SHADE-Arena convention
    prompt_sha256: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.suspicion <= 100.0:
            raise RecordError("MonitorVerdict.suspicion outside 0..100")


@dataclass(frozen=True)
class ClockMapping:
    """Maps a power-trace clock domain onto the episode's domain: t_episode = t_trace + offset_ns.

    ``uncertainty_ns`` is the half-width of the offset estimate (from the
    method named in ``method``, e.g. a round-trip bracket); attribution code
    widens every interval by it.
    """

    trace_domain: str
    episode_domain: str
    offset_ns: int
    uncertainty_ns: int
    method: str


@dataclass(frozen=True)
class PowerTrace:
    """Samples from one sensor channel.

    For ``*_power``-style sources each sample is (t_ns, watts): the sensor's
    reading at t_ns, averaged over ``averaging_window_ns`` ending at t_ns when
    the sensor documents one (NVML power on A100/H100 averages a 25 ms slice of
    every 100 ms; ``duty_fraction`` records that). For ``nvml_energy`` each
    sample is (t_ns, cumulative_joules) from the energy counter.
    """

    source: PowerSource
    channel: str  # e.g. "gpu0", "VDD_IN", "package"
    clock_domain: str
    t_ns: tuple[int, ...]
    values: tuple[float, ...]
    unit: Literal["W", "J_cumulative"]
    nominal_interval_ns: int
    averaging_window_ns: int | None = None
    duty_fraction: float | None = None
    resolution: float | None = None  # sensor quantum in ``unit`` (W or J)
    notes: str = ""

    def __post_init__(self) -> None:
        if len(self.t_ns) != len(self.values):
            raise RecordError("PowerTrace t_ns and values differ in length")
        if any(b <= a for a, b in zip(self.t_ns, self.t_ns[1:])):
            raise RecordError("PowerTrace.t_ns not strictly increasing")
        if (self.source == "nvml_energy") != (self.unit == "J_cumulative"):
            raise RecordError("PowerTrace unit does not match source")
        if self.duty_fraction is not None and not 0.0 < self.duty_fraction <= 1.0:
            raise RecordError("PowerTrace.duty_fraction outside (0, 1]")


@dataclass(frozen=True)
class RouterLog:
    """MoE routing decisions for one episode (Stage A).

    ``experts[k]`` lists, for decode/prefill token k in generation order, the
    top-k expert ids chosen at each MoE layer: experts[k][layer] is a tuple of
    ids. ``phase[k]`` is "prefill" or "decode".
    """

    model: str
    num_experts: int
    top_k: int
    layers: tuple[int, ...]
    phase: tuple[Literal["prefill", "decode"], ...]
    experts: tuple[tuple[tuple[int, ...], ...], ...]

    def __post_init__(self) -> None:
        if len(self.phase) != len(self.experts):
            raise RecordError("RouterLog.phase and experts differ in length")
        for row in self.experts:
            if len(row) != len(self.layers):
                raise RecordError("RouterLog row does not cover every layer")
            for ids in row:
                if len(ids) != self.top_k or any(not 0 <= e < self.num_experts for e in ids):
                    raise RecordError("RouterLog expert ids malformed")


@dataclass(frozen=True)
class Episode:
    """One agent run of one task pair under one condition, with everything measured beside it."""

    episode_id: str
    task_pair: str  # e.g. "shade/bank_transfer"
    condition: Condition
    agent_model: str
    endpoint: str  # backend kind and identity, never a credential
    seed: int
    clock_domain: str
    start_ns: int
    end_ns: int
    turns: tuple[Turn, ...]
    main_task_score: float | None = None
    side_task_success: bool | None = None
    monitor_verdicts: tuple[MonitorVerdict, ...] = ()
    power_traces: tuple[PowerTrace, ...] = ()
    clock_mappings: tuple[ClockMapping, ...] = ()
    router_log: RouterLog | None = None
    hardware: Mapping[str, Any] = field(default_factory=dict)
    flags: tuple[str, ...] = ()  # recorded conditions, never refusals
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise RecordError(f"unknown schema {self.schema!r}")
        _check_interval("Episode", self.start_ns, self.end_ns)
        if [t.index for t in self.turns] != list(range(len(self.turns))):
            raise RecordError("Episode turns not indexed 0..n-1 in order")
        for turn in self.turns:
            if turn.start_ns < self.start_ns or turn.end_ns > self.end_ns:
                raise RecordError(f"Turn {turn.index} outside the episode")
        domains = {self.clock_domain} | {m.trace_domain for m in self.clock_mappings}
        for trace in self.power_traces:
            if trace.clock_domain not in domains:
                raise RecordError(f"PowerTrace domain {trace.clock_domain!r} has no ClockMapping")

    # Convenience views used by several lanes; each is a plain sum over logged fields.
    def logged_turns(self) -> tuple[Turn, ...]:
        return tuple(t for t in self.turns if t.logged)

    def totals(self, *, logged_only: bool = False) -> dict[str, int]:
        turns = self.logged_turns() if logged_only else self.turns
        calls = [c for t in turns for c in t.tool_calls if c.logged or not logged_only]
        return {
            "turns": len(turns),
            "prefill_tokens": sum(t.prefill_tokens for t in turns),
            "decode_tokens": sum(t.decode_tokens for t in turns),
            "hidden_tokens": sum(t.hidden_tokens for t in turns),
            "tool_calls": len(calls),
            "duration_ns": self.end_ns - self.start_ns,
        }


# ---------------------------------------------------------------- serialisation

def to_jsonable(record: Any) -> Any:
    if is_dataclass(record):
        return {f.name: to_jsonable(getattr(record, f.name)) for f in fields(record)}
    if isinstance(record, (list, tuple)):
        return [to_jsonable(x) for x in record]
    if isinstance(record, Mapping):
        return {str(k): to_jsonable(v) for k, v in record.items()}
    return record


def to_json(record: Any) -> str:
    return json.dumps(to_jsonable(record), sort_keys=True, separators=(",", ":"), allow_nan=False)


def from_json(cls: type, text: str | bytes) -> Any:
    return _build(cls, json.loads(text))


def write_episodes(path: Path, episodes: Iterable[Episode]) -> int:
    """Write one episode per line (JSONL); returns the count."""
    count = 0
    with Path(path).open("w", encoding="utf-8") as handle:
        for episode in episodes:
            handle.write(to_json(episode) + "\n")
            count += 1
    return count


def read_episodes(path: Path) -> list[Episode]:
    with Path(path).open(encoding="utf-8") as handle:
        return [from_json(Episode, line) for line in handle if line.strip()]


def _build(tp: Any, value: Any) -> Any:
    origin = getattr(tp, "__origin__", None)
    args = get_args(tp)
    if value is None:
        return None
    if is_dataclass(tp):
        if not isinstance(value, Mapping):
            raise RecordError(f"{tp.__name__} expects an object")
        hints = get_type_hints(tp)
        known = {f.name for f in fields(tp)}
        unknown = set(value) - known
        if unknown:
            raise RecordError(f"{tp.__name__} unknown fields {sorted(unknown)}")
        return tp(**{k: _build(hints[k], v) for k, v in value.items()})
    if origin is tuple:
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_build(args[0], v) for v in value)
        return tuple(_build(a, v) for a, v in zip(args, value))
    if origin is Literal:
        if value not in args:
            raise RecordError(f"{value!r} not one of {args}")
        return value
    if args and type(None) in args:  # Optional[X] / X | None
        inner = [a for a in args if a is not type(None)]
        return _build(inner[0], value) if len(inner) == 1 else value
    if tp is float and isinstance(value, int) and not isinstance(value, bool):
        return float(value)
    if origin in (Mapping, dict) or tp in (Mapping, dict):
        return dict(value)
    return value


def _check_interval(name: str, start: int, end: int) -> None:
    if not isinstance(start, int) or not isinstance(end, int) or isinstance(start, bool):
        raise RecordError(f"{name} times must be integer nanoseconds")
    if end < start:
        raise RecordError(f"{name} ends before it starts")


def _check_nonneg(name: str, **values: int) -> None:
    for key, value in values.items():
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise RecordError(f"{name}.{key} must be a non-negative integer")


__all__ = [
    "SCHEMA", "RecordError", "ToolCall", "Turn", "MonitorVerdict", "ClockMapping", "PowerTrace",
    "RouterLog", "Episode", "to_json", "to_jsonable", "from_json", "write_episodes", "read_episodes",
]
