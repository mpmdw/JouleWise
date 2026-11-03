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
* Named memos of pure, deterministic derivations (see ``memo``). The V2
  strict-grammar success set (D-188 L7) is ``memo(GRAMMAR_VERDICT_MEMO)``.
* D-188 VDL-CORE: the run's verified derivation store
  (``joulewise.analysis_verified_store``), created only here and only when the
  activation names a VDL mode other than ``off``; and a slot for the phase
  timers (``timing``, set by their owner).
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import itertools
from typing import Any, Iterator

_ACTIVE: "_RunCaches | None" = None
_SERIALS = itertools.count(1)
GRAMMAR_VERDICT_MEMO = "authentication_io.grammar_ok"


class _RunCaches:
    def __init__(self, physics_store: dict | None, memos: dict | None = None, workers: int = 1):
        self.physics_store = physics_store
        self.memos: dict[str, dict[Any, Any]] = {} if memos is None else memos
        self.hits: dict[str, int] = {}
        self.misses: dict[str, int] = {}
        # Member-level worker pool (joulewise.analysis_member_pool): only the
        # driver process of a run with workers > 1 has one; the run's deadline
        # observer receives worker firings.
        self.workers = workers
        self.deadline: Any = None
        self.worker_observer_unavailable = False
        self.pool: Any = None
        # D-188: a process-unique activation serial (verification scopes that
        # outlive an activation are discarded), the verified derivation store
        # (None unless this activation enabled it) and the phase-timer slot.
        self.serial = next(_SERIALS)
        self.vdl: Any = None
        self.timing: Any = None


@contextmanager
def analysis_run_caches(
    physics_store: dict | None = None, *, memos: dict | None = None, workers: int = 1,
    vdl_mode: Any = None, vdl_commit: str | None = None, vdl_entries: Any = None,
) -> Iterator[_RunCaches]:
    """Activate the run caches in this process for the duration of the block.

    ``memos`` lets a long-lived worker process keep its memo tables across the
    tasks it runs for one analysis run. ``workers`` > 1 lets whole-window
    member work use a spawned pool (created on first use, shut down here).
    ``vdl_mode`` (an ``analysis_verified_store.Mode``; ``None`` or ``off``: no
    store) creates the run's verified derivation store, seeded from
    ``vdl_entries`` (an ``export_entries`` payload) when given.
    """

    global _ACTIVE
    if physics_store is not None and not isinstance(physics_store, dict):
        raise TypeError("run physics store must be a dict")
    if memos is not None and not isinstance(memos, dict):
        raise TypeError("run memos must be a dict")
    if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1:
        raise TypeError("run workers must be a positive int")
    store = None
    if vdl_mode is not None:
        from joulewise.analysis_verified_store import Mode, VerifiedStore  # noqa: PLC0415

        if not isinstance(vdl_mode, Mode):
            raise TypeError("run vdl_mode must be an analysis_verified_store.Mode")
        if vdl_mode.active:
            store = VerifiedStore(vdl_mode, commit=vdl_commit)
            if vdl_entries is not None:
                store.merge_entries(vdl_entries)
    previous = _ACTIVE
    caches = _RunCaches(physics_store, memos, workers)
    caches.vdl = store
    _ACTIVE = caches
    try:
        yield caches
    finally:
        _ACTIVE = previous
        if caches.pool is not None:
            caches.pool.shutdown(wait=True, cancel_futures=True)
            caches.pool = None


def current() -> "_RunCaches | None":
    return _ACTIVE


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


def run_reduce_physics_kwargs(bundle_path: Any) -> dict[str, Any]:
    """``reduce_bundle`` keyword arguments sharing the run's physics store, or {}.

    Outside an analysis run (no run store and no shared store in the calling
    context) this is ``{}`` and performs no read. Inside one, the partition is
    chosen from the bundle's metadata exactly as validate-bundle chooses it
    (``cli._strict_problems``: ``BundleReader.raw_metadata()``, the same
    authenticated json read the reducer itself performs).
    """

    from pathlib import Path  # noqa: PLC0415

    from joulewise.bundle_read import BundleReader  # noqa: PLC0415
    from joulewise.whole_window import shared_physics_cache  # noqa: PLC0415

    if run_physics_store() is None and shared_physics_cache() is None:
        return {}
    cache = physics_cache_for_call(None, BundleReader(Path(bundle_path)).raw_metadata())
    return {} if cache is None else {"_instrument_calibration_physics_cache": cache}


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


_CANONICAL_KEY_DOMAIN = b"joulewise.analysis_run_cache.canonical_key.v2\0"


def _frame(tag: bytes, payload: bytes) -> bytes:
    return tag + str(len(payload)).encode("ascii") + b":" + payload


def _qualified(kind: type) -> bytes:
    return f"{kind.__module__}.{kind.__qualname__}".encode("utf-8", "surrogatepass")


def _canonical_bytes(item: Any) -> bytes:
    """An injective, type-tagged, length-framed encoding of a JSON-shaped value.

    Every value is framed as tag + payload length + payload, so no encoded value
    is a prefix of another and no two values of different types share bytes: a
    float and the mapping {"float": its hex} differ (D-188 SHIP-FIX, finding A),
    as do a list and a tuple, and a subclass and its base. The approach is the
    verified store's (analysis_verified_store.canonical_bytes), restricted to the
    JSON-shaped values a run memo keys on.
    """

    if item is None:
        return b"N"
    if item is True:
        return b"T"
    if item is False:
        return b"F"
    kind = type(item)
    if kind is int:
        return _frame(b"i", str(item).encode("ascii"))
    if kind is float:
        return _frame(b"f", item.hex().encode("ascii"))
    if kind is str:
        return _frame(b"s", item.encode("utf-8", "surrogatepass"))
    if isinstance(item, (int, float, str)) and not isinstance(item, bool):
        # A subclass (an IntEnum, a str enum): its type is part of the key.
        base = int if isinstance(item, int) else float if isinstance(item, float) else str
        return _frame(b"x", _qualified(kind) + b"\0" + _canonical_bytes(base(item)))
    if isinstance(item, (list, tuple)):
        return _frame(b"l", _qualified(kind) + b"\0"
                      + b"".join(_frame(b"m", _canonical_bytes(element)) for element in item))
    if isinstance(item, dict):
        if not all(isinstance(key, str) for key in item):
            raise TypeError("non-string key")
        pairs = sorted((_canonical_bytes(key), _canonical_bytes(element)) for key, element in item.items())
        return _frame(b"d", _qualified(kind) + b"\0"
                      + b"".join(_frame(b"k", key) + _frame(b"v", element) for key, element in pairs))
    raise TypeError(f"uncanonical {kind.__name__}")


def canonical_key(value: Any) -> str:
    """A digest of a JSON-shaped value under an injective, type-tagged encoding.

    Floats keep their exact bits (``float.hex``); a float never shares a key with
    any other value, in particular not with the mapping ``{"float": x.hex()}``
    (D-188 SHIP-FIX, finding A). Raises TypeError for a value with no exact
    canonical form, and the caller then does not use the memo for that call.
    """

    return hashlib.sha256(_CANONICAL_KEY_DOMAIN + _canonical_bytes(value)).hexdigest()
