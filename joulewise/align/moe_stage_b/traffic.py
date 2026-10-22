"""Translate layer-qualified MoE routes into incremental memory traffic.

This is a decode-first model of one named memory path, not a total inference
energy model. Link bandwidth and incremental joules per byte must be supplied
with provenance; nominal bus specifications are not measured coefficients.
"""

from __future__ import annotations

import math
import bisect
from collections import OrderedDict
from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from joulewise.align.records import Episode, RouterLog

NS_PER_SECOND = 1_000_000_000
ExpertKey = tuple[int, int]


@dataclass(frozen=True)
class OffloadConfig:
    """Pinned experts are outside the dynamic cache budget.

    A shared byte budget spans the listed layers. SLRU has a protected half,
    as in the pinned llama.cpp cache; mixed expert sizes are a generalization.
    'none' streams every nonresident request. The path can be PCIe, DRAM, etc.;
    it must match what the selected sensor actually measures.
    """

    expert_bytes: Mapping[int, int]
    resident: frozenset[ExpertKey]
    cache_capacity_bytes: int
    cache_policy: str  # "none" | "lru" | "slru"
    bandwidth_bytes_s: float
    joules_per_byte: float
    path: str
    bandwidth_source: str
    energy_source: str
    prefill_mode: str = "bypass"  # "bypass" (no cache update) | "serial"
    prefill_batch_tokens: int = 1  # Explicit backend microbatch size; never inferred.
    flags: tuple[str, ...] = ()  # Unavailable configuration inputs remain explicit.
    decode_miss_stalls: bool = False
    running_power_w: float = 0.0  # Sensor-visible platform power during a blocking upload.


@dataclass(frozen=True)
class TokenWindow:
    token_index: int
    start_ns: int
    end_ns: int


@dataclass(frozen=True)
class TimingResult:
    windows: tuple[TokenWindow, ...]
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class TransferPulse:
    token_index: int
    start_ns: int
    end_ns: int
    bytes_moved: int
    energy_j: float


@dataclass(frozen=True)
class TokenTraffic:
    token_index: int
    phase: str
    selected: int
    resident_hits: int
    cache_hits: int
    batch_reuse: int
    misses: int
    bytes_moved: int
    energy_j: float
    transfer_time_s: float
    stall_energy_j: float = 0.0

    @property
    def incremental_energy_j(self) -> float:
        """Memory traffic plus running power during added decode time."""
        return self.energy_j + self.stall_energy_j


@dataclass(frozen=True)
class TrafficResult:
    tokens: tuple[TokenTraffic, ...]
    pulses: tuple[TransferPulse, ...]
    flags: tuple[str, ...] = ()

    @property
    def total_bytes(self) -> int:
        return sum(token.bytes_moved for token in self.tokens)

    @property
    def total_energy_j(self) -> float:
        return math.fsum(token.energy_j for token in self.tokens)


@dataclass(frozen=True)
class ExpertSize:
    bytes_per_expert: int | None
    flags: tuple[str, ...] = ()


def expert_size_from_config(
    config: Mapping[str, Any], *, block_elements: int, block_bytes: int,
) -> ExpertSize:
    """Size the three gated-FFN matrices using stored quantization blocks.

    HF Qwen MoE uses moe_intermediate_size; OLMoE uses intermediate_size.
    GGML quantizes rows, so gate/up and down must each have aligned row
    lengths. This excludes shared experts, biases, scales and other tensors.
    Pass measured GGUF per-expert tensor strides to OffloadConfig when those
    exist; a parameter count alone does not specify a quantized tensor size.
    """
    hidden = config.get("hidden_size")
    intermediate = config.get("moe_intermediate_size", config.get("intermediate_size"))
    dimensions = (hidden, intermediate, block_elements, block_bytes)
    if any(not isinstance(v, int) or isinstance(v, bool) or v <= 0 for v in dimensions):
        return ExpertSize(None, ("invalid_expert_dimensions",))
    if hidden % block_elements or intermediate % block_elements:
        return ExpertSize(None, ("quantized_rows_not_block_aligned",))
    # gate and up: intermediate rows of hidden; down: hidden rows of intermediate.
    size = (2 * intermediate * (hidden // block_elements)
            + hidden * (intermediate // block_elements)) * block_bytes
    return ExpertSize(size)


def episode_token_windows(episode: Episode, *, prefill_batch_tokens: int = 1) -> TimingResult:
    """Uniform within-phase timing adapter, never a claim of observed token times.

    RouterLog cannot store token times or turn boundaries. Counts and phase order
    must match all turns, including unlogged work, before this adapter assigns
    windows. Actual token timing should be supplied directly to model_traffic.
    """
    router = episode.router_log
    flags = ["uniform_within_phase_token_timing"]
    if (not isinstance(prefill_batch_tokens, int) or isinstance(prefill_batch_tokens, bool)
            or prefill_batch_tokens <= 0):
        return TimingResult((), ("invalid_prefill_batch_size",))
    if prefill_batch_tokens > 1:
        flags.append("prefill_batch_timing_assumption")
    if router is None:
        return TimingResult((), ("missing_router_log",))
    expected = tuple(phase for turn in episode.turns
                     for phase, count in (("prefill", turn.prefill_tokens),
                                          ("decode", turn.decode_tokens))
                     for _ in range(count))
    if router.phase != expected:
        return TimingResult((), ("router_turn_phase_mismatch",))
    windows: list[TokenWindow] = []
    for turn in episode.turns:
        boundary = turn.first_token_ns
        if boundary is None:
            flags.append("missing_first_token_time")
            # No basis for separating prefill and decode: keep the missing data explicit.
            return TimingResult((), tuple(dict.fromkeys(flags)))
        for start, end, count, batch_size in (
                (turn.start_ns, boundary, turn.prefill_tokens, prefill_batch_tokens),
                (boundary, turn.end_ns, turn.decode_tokens, 1)):
            if count and end <= start:
                return TimingResult((), tuple(dict.fromkeys(flags + ["zero_phase_duration"])))
            for j in range(count):
                left = (j//batch_size)*batch_size
                right = min(count, left+batch_size)
                windows.append(TokenWindow(len(windows), start + (end-start)*left//count,
                                           start + (end-start)*right//count))
        if any(call.start_ns < turn.end_ns and call.end_ns > boundary
               for call in turn.tool_calls):
            flags.append("tool_overlaps_decode_window")
    return TimingResult(tuple(windows), tuple(dict.fromkeys(flags)))


class _Cache:
    """Request-atomic LRU/SLRU; selected experts cannot evict one another."""

    def __init__(self, config: OffloadConfig) -> None:
        self.config = config
        self.probation: OrderedDict[ExpertKey, int] = OrderedDict()
        self.protected: OrderedDict[ExpertKey, int] = OrderedDict()
        self.used_bytes = 0
        self.protected_bytes = 0

    def request(self, keys: Sequence[ExpertKey]) -> tuple[int, int, bool]:
        cap = self.config.cache_capacity_bytes
        sizes = self.config.expert_bytes
        if self.config.cache_policy == "none" or cap == 0:
            return 0, len(keys), False
        if sum(sizes[layer] for layer, _ in keys) > cap:
            # The real cache bypasses requests that cannot retain their selected set.
            return 0, len(keys), True
        hits = 0
        for key in keys:
            if key in self.protected:
                self.protected.move_to_end(key)
                hits += 1
            elif key in self.probation:
                value = self.probation.pop(key)
                target = self.protected if self.config.cache_policy == "slru" else self.probation
                target[key] = value
                if self.config.cache_policy == "slru":
                    self.protected_bytes += value
                hits += 1
            if self.config.cache_policy == "slru":
                # SLRU's protected segment owns half of the dynamic budget.
                while self.protected_bytes > cap // 2 and self.protected:
                    old, value = self.protected.popitem(last=False)
                    self.protected_bytes -= value
                    self.probation[old] = value
        selected = set(keys)
        for key in sorted(keys):
            if key in self.probation or key in self.protected:
                continue
            size = sizes[key[0]]
            while self.used_bytes + size > cap:
                for segment in (self.probation, self.protected):
                    victim = next((old for old in segment if old not in selected), None)
                    if victim is not None:
                        removed = segment.pop(victim)
                        self.used_bytes -= removed
                        if segment is self.protected:
                            self.protected_bytes -= removed
                        break
                else:
                    # Request-size check above guarantees a victim exists.
                    raise AssertionError("cache accounting invariant")
            self.probation[key] = size
            self.used_bytes += size
        return hits, len(keys)-hits, False


def model_traffic(
    router: RouterLog, config: OffloadConfig, *,
    windows: Sequence[TokenWindow] | None = None,
) -> TrafficResult:
    """Compute bytes, energy, duration and serialized transfer pulses.

    No timestamps means a serial transfer-only clock starting at zero. Explicit
    windows anchor transfers to token starts. Transfers that cannot fit are
    queued and flagged, not silently clipped or discarded. Prefill defaults to
    bypassing cache updates because shared records do not describe its batches.
    """
    flags: list[str] = list(config.flags)
    if config.cache_policy not in ("none", "lru", "slru"):
        flags.append("invalid_cache_policy")
    if config.prefill_mode not in ("serial", "bypass"):
        flags.append("invalid_prefill_mode")
    if (not isinstance(config.prefill_batch_tokens, int)
            or isinstance(config.prefill_batch_tokens, bool) or config.prefill_batch_tokens <= 0):
        flags.append("invalid_prefill_batch_size")
    if (not isinstance(config.cache_capacity_bytes, int)
            or isinstance(config.cache_capacity_bytes, bool) or config.cache_capacity_bytes < 0):
        flags.append("invalid_cache_capacity")
    if not math.isfinite(config.bandwidth_bytes_s) or config.bandwidth_bytes_s <= 0:
        flags.append("invalid_bandwidth")
    if not math.isfinite(config.joules_per_byte) or config.joules_per_byte < 0:
        flags.append("invalid_energy_coefficient")
    if (not isinstance(config.decode_miss_stalls, bool)
            or not math.isfinite(config.running_power_w) or config.running_power_w < 0):
        flags.append("invalid_stall_parameters")
    if len(set(router.layers)) != len(router.layers):
        flags.append("duplicate_layer_ids")
    if any(not isinstance(config.expert_bytes.get(layer), int)
           or config.expert_bytes[layer] <= 0 for layer in router.layers):
        flags.append("missing_or_invalid_expert_size")
    if any(layer not in router.layers or not 0 <= expert < router.num_experts
           for layer, expert in config.resident):
        flags.append("invalid_resident_expert")
    if not config.path or not config.bandwidth_source or not config.energy_source:
        flags.append("missing_parameter_provenance")
    if any(phase not in ("prefill", "decode") for phase in router.phase):
        flags.append("unknown_router_phase")
    if windows is not None:
        if (len(windows) != len(router.phase)
                or any(w.token_index != i or not isinstance(w.start_ns, int)
                       or not isinstance(w.end_ns, int)
                       or isinstance(w.start_ns, bool) or isinstance(w.end_ns, bool)
                       or w.end_ns <= w.start_ns for i, w in enumerate(windows))
                or any(b.start_ns < a.start_ns for a, b in zip(windows, windows[1:]))):
            flags.append("invalid_token_windows")
    if flags:
        return TrafficResult((), (), tuple(flags))
    if "prefill" in router.phase:
        flags.append("prefill_batch_boundaries_unavailable")
        flags.append("prefill_cache_bypassed" if config.prefill_mode == "bypass"
                     else "serial_prefill_assumption")
        if config.prefill_mode == "bypass" and config.prefill_batch_tokens > 1:
            flags.append("prefill_batch_union_profile_assumption")
        if config.prefill_mode == "bypass":
            flags.append("prefill_readonly_cache_reuse_unmodelled")
    if windows is None:
        flags.append("transfer_only_time_axis")
    flags.append("serialized_token_start_transfer_profile")
    cache = _Cache(config)
    tokens: list[TokenTraffic] = []
    pulses: list[TransferPulse] = []
    available_ns = windows[0].start_ns if windows else 0
    prefill_offset = 0
    prefill_seen: set[ExpertKey] = set()
    batch_start = batch_end = 0
    for i, (phase, row) in enumerate(zip(router.phase, router.experts)):
        if phase == "prefill" and config.prefill_mode == "bypass":
            if prefill_offset % config.prefill_batch_tokens == 0:
                prefill_seen.clear()
                batch_start = i
                batch_end = i
                while (batch_end+1 < len(router.phase)
                       and batch_end-i+1 < config.prefill_batch_tokens
                       and router.phase[batch_end+1] == "prefill"):
                    batch_end += 1
            prefill_offset += 1
        else:
            prefill_offset = 0
            batch_start = batch_end = i
        selected = resident_hits = hits = batch_reuse = misses = moved = 0
        for layer, ids in zip(router.layers, row):
            unique_ids = tuple(dict.fromkeys(ids))
            if len(unique_ids) != len(ids):
                flags.append("duplicate_expert_ids")
            selected += len(unique_ids)
            keys = [(layer, e) for e in unique_ids if (layer, e) not in config.resident]
            resident_hits += len(unique_ids)-len(keys)
            if phase == "prefill" and config.prefill_mode == "bypass":
                fresh = [key for key in keys if key not in prefill_seen]
                batch_reuse += len(keys)-len(fresh)
                prefill_seen.update(keys)
                n_hit, n_miss, bypass = 0, len(fresh), False
            else:
                n_hit, n_miss, bypass = cache.request(keys)
            if bypass:
                flags.append("request_exceeds_cache_capacity")
            hits += n_hit
            misses += n_miss
            moved += n_miss * config.expert_bytes[layer]
        energy = moved * config.joules_per_byte
        duration_s = moved / config.bandwidth_bytes_s
        tokens.append(TokenTraffic(i, phase, selected, resident_hits, hits, batch_reuse,
                                   misses, moved, energy, duration_s,
                                   (math.ceil(duration_s*NS_PER_SECOND)/NS_PER_SECOND
                                    * config.running_power_w
                                    if phase == "decode" and config.decode_miss_stalls else 0.0)))
        if moved:
            start = max(available_ns, windows[batch_start].start_ns if windows is not None else 0)
            # Round upward to integer ns so the profile never exceeds configured bandwidth.
            end = start + math.ceil(duration_s * NS_PER_SECOND)
            pulses.append(TransferPulse(i, start, end, moved, energy))
            available_ns = end
            if windows is not None and end > windows[batch_end].end_ns:
                flags.append("transfer_exceeds_token_window")
    return TrafficResult(tuple(tokens), tuple(pulses), tuple(dict.fromkeys(flags)))



@dataclass(frozen=True)
class StallTiming:
    """A synthetic compute-only schedule retimed for blocking decode uploads."""

    episode: Episode
    windows: tuple[TokenWindow, ...]
    reference_decode_duration_ns: int
    flags: tuple[str, ...] = ()


def apply_decode_stalls(
    episode: Episode, config: OffloadConfig, *, windows: Sequence[TokenWindow],
) -> StallTiming:
    """Extend a compute-only schedule; never apply to measured token timestamps.

    Uploads precede dependent expert work in the pinned llama.cpp CUDA stream.
    Each decode miss adds ceil(bytes/bandwidth * 1e9) ns, and later turns/tools
    move by the accumulated delay. Prefill timing remains a separate assumption.
    The returned windows are passed unchanged to traffic, sensor and features.
    """
    router = episode.router_log
    nominal = tuple(windows)
    if router is None or len(nominal) != len(router.phase):
        return StallTiming(episode, nominal, 0, ("missing_stall_token_timing",))
    reference_ns = sum(w.end_ns-w.start_ns for w, phase in zip(nominal, router.phase)
                       if phase == "decode")
    if not config.decode_miss_stalls:
        return StallTiming(episode, nominal, reference_ns)
    # Counts and cache misses are independent of timestamps. Production traffic
    # is rerun on the resulting actual windows; this pass only sizes delays.
    counts = model_traffic(router, config)
    if len(counts.tokens) != len(nominal):
        return StallTiming(episode, nominal, reference_ns, counts.flags)
    delays = [(w.end_ns, math.ceil(t.transfer_time_s*NS_PER_SECOND))
              for w, t in zip(nominal, counts.tokens) if t.phase == "decode"]
    ends = [end for end, _ in delays]
    cumulative = [0]
    for _, delay in delays:
        cumulative.append(cumulative[-1]+delay)

    def shifted(time_ns: int) -> int:
        return time_ns+cumulative[bisect.bisect_right(ends, time_ns)]

    actual = tuple(TokenWindow(w.token_index, shifted(w.start_ns), shifted(w.end_ns))
                   for w in nominal)
    turns = tuple(replace(
        turn, start_ns=shifted(turn.start_ns), end_ns=shifted(turn.end_ns),
        first_token_ns=(shifted(turn.first_token_ns)
                        if turn.first_token_ns is not None else None),
        tool_calls=tuple(replace(call, start_ns=shifted(call.start_ns),
                                 end_ns=shifted(call.end_ns)) for call in turn.tool_calls))
                  for turn in episode.turns)
    flags = ("blocking_decode_upload_stalls", "constant_running_power_during_stall",
             "compute_only_schedule_retimed")
    result = replace(episode, end_ns=shifted(episode.end_ns), turns=turns,
                     flags=tuple(dict.fromkeys((*episode.flags, *flags))))
    return StallTiming(result, actual, reference_ns, flags)


def decode_reuse(router: RouterLog) -> float | None:
    """Mean adjacent decode-token expert overlap, normalized by top-k.

    Prefill resets adjacency. Turn boundaries are not in RouterLog, so callers
    must interpret this as log adjacency, not an observed within-turn statistic.
    """
    overlaps: list[float] = []
    previous = None
    for phase, row in zip(router.phase, router.experts):
        if phase != "decode":
            previous = None
            continue
        if previous is not None and router.layers and router.top_k:
            overlaps.append(sum(len(set(a) & set(b)) for a, b in zip(previous, row))
                            / (len(router.layers)*router.top_k))
        previous = row
    return math.fsum(overlaps)/len(overlaps) if overlaps else None
