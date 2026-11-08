"""Shared serialization and optional-dependency helpers; no I/O on import."""

from functools import lru_cache
import hashlib
import json
from typing import Any


@lru_cache(maxsize=1)
def require_numpy():
    """Import the optional desk extra only when a numerical operation needs it."""
    try:
        import numpy
    except ImportError as exc:
        raise RuntimeError("interp-energy numerical tools require optional NumPy") from exc
    return numpy


def canonical_sha256(value: Any) -> str:
    """SHA-256 of UTF-8 sorted-key compact JSON, without a trailing newline."""
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()
