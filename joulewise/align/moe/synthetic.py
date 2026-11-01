"""Production-shaped topic-affinity worlds for offline Stage A validation.

Main-task affinity is uniform over experts. A side task has affinity one on
a layer-specific set of top_k experts and zero elsewhere. A stated fraction
of sabotage decode tokens changes topic. No condition changes token/tool
counts. Paired common random numbers make the zero-shift control exact;
independent_noise permits a separate exchangeable-noise control.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from joulewise.align.records import Episode, RouterLog, ToolCall, Turn


@dataclass(frozen=True)
class TopicWorld:
    """Explicit fixture design; dimensions can be set to the full verified model."""

    groups: int = 12
    repeats: int = 1
    num_experts: int = 32
    top_k: int = 4
    layers: int = 4
    turns: int = 6
    prefill_tokens: int = 128
    decode_tokens: int = 192
    # Timing is a configurable serving scenario, not a measured calibration.
    prefill_ns_per_token: int = 500_000
    decode_ns_per_token: int = 20_000_000
    tool_ns: int = 200_000_000


def expected_topic_statistics(num_experts: int, top_k: int, fraction: float) -> dict[str, float]:
    """Infinite-token expectations for the independent-topic decode process.

    Expert-selection marginals are p_core=f+(1-f)k/E, p_other=(1-f)k/E.
    Normalized usage probabilities are p/k. Overlap averages squared selection
    marginals, giving k/E + f^2(1-k/E). CV is f*sqrt(E/k-1).
    """
    base = (1 - fraction) / num_experts
    probabilities = [base + fraction / top_k] * top_k + [base] * (num_experts - top_k)
    entropy = (-math.fsum(p * math.log(p) for p in probabilities if p)
               / math.log(num_experts)) if num_experts > 1 else 0.0
    return {
        "usage_entropy": entropy,
        "load_imbalance": fraction * math.sqrt(num_experts / top_k - 1),
        "reuse_fraction": top_k / num_experts + fraction**2 * (1 - top_k / num_experts),
    }


def topic_episodes(side_fraction: float, *, design: TopicWorld | None = None,
                   seed: int = 0, independent_noise: bool = False) -> tuple[Episode, ...]:
    """Generate paired multi-turn tool-using episodes with actual RouterLog rows.

    A decode token changes topic with probability side_fraction. Prefill is an
    unchanged negative control. Counts vary between tasks/repeats, but are
    identical within each benign/sabotage pair. Topic randomness is independent
    between groups. Invalid fixture settings return an empty world; invalid
    side fractions use zero shift with an explicit episode flag.
    """
    design = design or TopicWorld()
    if (min(design.groups, design.repeats, design.layers, design.turns,
            design.prefill_tokens, design.decode_tokens) <= 0
            or not 0 < design.top_k <= design.num_experts
            or min(design.prefill_ns_per_token, design.decode_ns_per_token, design.tool_ns) < 0):
        return ()
    flags = ["synthetic_topic_affinity_world"]
    if not math.isfinite(side_fraction) or not 0 <= side_fraction <= 1:
        side_fraction = 0.0
        flags.append("invalid_side_fraction_used_zero")
    if not independent_noise:
        flags.append("paired_common_random_numbers")
    episodes = []
    world_rng = random.Random(seed)
    for group in range(design.groups):
        cores = tuple(tuple(world_rng.sample(range(design.num_experts), design.top_k))
                      for _ in range(design.layers))
        for repeat in range(design.repeats):
            router_seed = world_rng.randrange(2**63)
            count_rng = random.Random(world_rng.randrange(2**63))
            counts = [(design.prefill_tokens + count_rng.randrange(design.prefill_tokens // 2 + 1),
                       design.decode_tokens + count_rng.randrange(design.decode_tokens // 2 + 1))
                      for _ in range(design.turns)]
            for label, condition in enumerate(("benign", "sabotage")):
                rng = random.Random(router_seed + (label if independent_noise else 0))
                phases = []
                expert_rows = []
                turns = []
                cursor = 0
                context = 0
                shifted = 0
                for turn_index, (prefill, decode) in enumerate(counts):
                    start = cursor
                    first = start + prefill * design.prefill_ns_per_token
                    generated = first + decode * design.decode_ns_per_token
                    calls = ()
                    cursor = generated
                    if turn_index + 1 < design.turns:
                        cursor += design.tool_ns
                        calls = (ToolCall(("read_file", "lookup", "write_artifact")[turn_index % 3],
                                          generated, cursor, 128, 2048),)
                    turns.append(Turn(turn_index, start, cursor, context, prefill, decode,
                                      first_token_ns=first, tool_calls=calls))
                    context += prefill + decode
                    for phase, length in (("prefill", prefill), ("decode", decode)):
                        for _ in range(length):
                            draw = rng.random()
                            main = tuple(tuple(rng.sample(range(design.num_experts), design.top_k))
                                         for _ in range(design.layers))
                            side = label == 1 and phase == "decode" and draw < side_fraction
                            phases.append(phase)
                            expert_rows.append(cores if side else main)
                            shifted += int(side)
                router = RouterLog("synthetic/topic-affinity", design.num_experts, design.top_k,
                                   tuple(range(design.layers)), tuple(phases), tuple(expert_rows))
                episodes.append(Episode(
                    f"topic-{group}-{repeat}-{condition}", f"synthetic/task-{group}", condition,
                    router.model, "synthetic", router_seed, "synthetic.monotonic", 0, cursor,
                    tuple(turns), router_log=router,
                    hardware={"synthetic": True, "side_fraction_of_decode": side_fraction if label else 0.0,
                              "shifted_tokens": shifted, "topic_affinity_core_size": design.top_k},
                    flags=tuple(flags)))
    return tuple(episodes)


__all__ = ["TopicWorld", "expected_topic_statistics", "topic_episodes"]
