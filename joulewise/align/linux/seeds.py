"""The unchanged ALIGN pilot-4 seed law (apple/sampling.py, 9c40e4e5d).

llama.cpp's portable wire seed is uint32. Keep both canonical uint64 seeds and
the explicit low-32-bit projection in per-turn provenance. Different engines
are not promised identical samples, even when the logical seeds match.
"""
import hashlib
import json


def leading_seed(value):
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def episode_seed(model_id, thinking, task_pair, seed_index):
    return leading_seed(["align-p4-v1", model_id, thinking, task_pair, seed_index])


def turn_seed(seed, turn_index):
    return leading_seed(["align-p4-turn-v1", seed, turn_index])
