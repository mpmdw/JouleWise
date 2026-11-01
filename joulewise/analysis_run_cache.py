"""Run-scoped, content-addressed caches for one block-5 analysis run (L9-SPEEDUP-R1).

Nothing here is active outside ``analysis_run_caches()``; the block-5 driver
enters it once per run (and each of its spawned worker processes enters its
own). Every cached value is a deterministic function of inputs bound by
content digest (bytes) plus the scalar arguments of the call; nothing is keyed
by a path or an mtime, and the caller still performs every authenticated read
before it consults a cache. A raised exception is never cached.

Two kinds of state live here:

* The run's instrument-calibration physics store (``whole_window``'s J2
  partitioned store). The driver shares it through ``whole_window``'s context
  variable; this module also makes it visible to strict-validation and
  ``reduce`` sites that run inside a fresh ``contextvars.Context()`` (the
  paper-custody indexed replays), which otherwise drop it. The reducer reads a
  physics entry only after its own artifact, plist and events hash checks, and
  stores only a verified fit (a wall-deadline firing yields no fit and is never
  stored).
* Named memos of pure, deterministic derivations (see ``memo``).
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
from typing import Any, Iterator

_ACTIVE: "_RunCaches | None" = None


class _RunCaches:
    def __init__(self, physics_store: dict | None, memos: dict | None = None):
        self.physics_store = physics_store
        self.memos: dict[str, dict[Any, Any]] = {} if memos is None else memos
        self.hits: dict[str, int] = {}
        self.misses: dict[str, int] = {}


@contextmanager
def analysis_run_caches(
    physics_store: dict | None = None, *, memos: dict | None = None
) -> Iterator[_RunCaches]:
    """Activate the run caches in this process for the duration of the block.

    ``memos`` lets a long-lived worker process keep its memo tables across the
    tasks it runs for one analysis run.
    """

    global _ACTIVE
    if physics_store is not None and not isinstance(physics_store, dict):
        raise TypeError("run physics store must be a dict")
    if memos is not None and not isinstance(memos, dict):
        raise TypeError("run memos must be a dict")
    previous = _ACTIVE
    caches = _RunCaches(physics_store, memos)
    _ACTIVE = caches
    try:
        yield caches
    finally:
        _ACTIVE = previous


def active() -> bool:
    return _ACTIVE is not None


def run_physics_store() -> dict | None:
    """The run's partitioned physics store, or ``None`` outside a run."""

    return None if _ACTIVE is None else _ACTIVE.physics_store


def physics_cache_for_call(local: dict | None, metadata: Any) -> dict | None:
    """``whole_window.physics_cache_for`` that also sees the run store in a fresh context.

    Outside a run this is exactly ``physics_cache_for(local, metadata)``. Inside
    one, when the calling context carries no shared store (an isolated replay
    context), the run's store is used for this call's view.
    """

    from joulewise.whole_window import (  # noqa: PLC0415
        physics_cache_for,
        shared_instrument_calibration_physics_cache,
        shared_physics_cache,
    )

    store = run_physics_store()
    if store is not None and shared_physics_cache() is None:
        with shared_instrument_calibration_physics_cache(store):
            return physics_cache_for(local, metadata)
    return physics_cache_for(local, metadata)


def memo(name: str) -> dict | None:
    """The named memo of the active run, or ``None`` outside a run."""

    if _ACTIVE is None:
        return None
    return _ACTIVE.memos.setdefault(name, {})


def note(name: str, hit: bool) -> None:
    if _ACTIVE is None:
        return
    table = _ACTIVE.hits if hit else _ACTIVE.misses
    table[name] = table.get(name, 0) + 1


def stats() -> dict[str, dict[str, int]]:
    if _ACTIVE is None:
        return {}
    return {"hits": dict(_ACTIVE.hits), "misses": dict(_ACTIVE.misses)}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_key(value: Any) -> str:
    """A digest of a JSON-shaped value; floats keep their exact repr.

    Raises TypeError/ValueError for a value with no exact canonical form, and
    the caller then does not use the memo for that call.
    """

    def exact(item: Any) -> Any:
        if isinstance(item, bool) or item is None or isinstance(item, (int, str)):
            return item
        if isinstance(item, float):
            return {"float": item.hex()}
        if isinstance(item, (list, tuple)):
            return [exact(element) for element in item]
        if isinstance(item, dict):
            if not all(isinstance(key, str) for key in item):
                raise TypeError("non-string key")
            return {key: exact(element) for key, element in item.items()}
        raise TypeError(f"uncanonical {type(item).__name__}")

    raw = json.dumps(exact(value), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
