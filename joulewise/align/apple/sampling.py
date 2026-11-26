"""Pilot-4 opt-in sampling and common-random-number seed law (no MLX import)."""
import hashlib
import json
import math

SEED_LAW = "align-p4-v1"
TURN_SEED_LAW = "align-p4-turn-v1"
SEED_BITS = 64  # Installed nanobind seed accepts uint64; 2**64 is rejected.


def leading_seed(value):
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:SEED_BITS // 8], "big")


def episode_seed(model_id, thinking, task_pair, seed_index):
    return leading_seed([SEED_LAW, model_id, thinking, task_pair, seed_index])


def turn_seed(seed, turn_index):
    return leading_seed([TURN_SEED_LAW, seed, turn_index])


def seed_inputs(config, thinking):
    # The campaign's model_id is explicit in its existing identity tag. For a
    # standalone caller the pinned model name is its model identifier.
    tags = config.run_metadata.tags
    model_id = next((t.split("=", 1)[1] for t in tags if t.startswith("align-model=")), config.model.name)
    return model_id, "thinking_on" if thinking is True else "thinking_off" if thinking is False else "template_default"


def validate_policy(policy):
    if not isinstance(policy, dict) or set(policy) != {"temperature", "top_p", "top_k", "min_p"}:
        raise ValueError("sampler requires temperature, top_p, top_k and min_p")
    if any(type(policy[k]) not in (int, float) or not math.isfinite(policy[k]) for k in ("temperature", "top_p", "min_p")):
        raise ValueError("sampler parameters must be finite numbers")
    if policy["temperature"] <= 0 or not 0 <= policy["top_p"] <= 1 or not 0 <= policy["min_p"] <= 1:
        raise ValueError("invalid categorical sampler parameters")
    if type(policy["top_k"]) is not int or policy["top_k"] < 0:
        raise ValueError("top_k must be a nonnegative integer")
    return dict(policy)
