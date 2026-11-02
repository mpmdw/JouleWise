"""Ordered process pool for independent whole-window member derivations (L9-SPEEDUP-R1 stage 4b).

Only the computation moves: a caller hands ``member_map`` one call per member of
a module-level pure function, in member order, and then consumes the outcomes in
that same order exactly where the serial loop called the function. Everything
the caller decides stays serial.

Active only in the driver process of a block-5 analysis run with workers > 1
(``analysis_run_caches(..., workers=N)``); anywhere else ``member_map`` returns
``None`` and the caller runs its unchanged serial loop.

Authentication equivalence:

* Read census. If the caller runs inside a ``V2AuthenticationReadSession``, each
  task runs inside its own fresh session in the worker and returns its records
  (normalized identity, sha256, grammar, read count, in first-read order).
  Consuming an outcome registers those records into the caller's session, in
  member order, read-count times, through the session's own first-digest and
  grammar enforcement: the session ends with the same records, in the same
  order, as the serial loop leaves, and a byte that changed since the session's
  first read of a file is refused exactly as a serial read would refuse it.
* Exceptions. A task that raised (any exception) is recomputed in the caller,
  serially, at its own position: the serial code path decides every failure.
* Calibration cache. Every task is shipped the run's physics store; each worker
  keeps its own; fits merge back only from tasks whose deadline did not fire.
* Wall deadline. Each task runs under the same ``detect_pulses`` observer the
  driver uses; firings are added to the run's observer (the step then fails
  closed as ``calibration_wall_deadline_fired``); a worker that cannot observe
  marks the run so the driver refuses the step as
  ``calibration_deadline_observer_unavailable``.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib
from typing import Any, Callable, Sequence


@dataclass(frozen=True)
class MemberTask:
    function: str
    args: tuple
    kwargs: dict
    session: bool
    physics: dict


@dataclass(frozen=True)
class MemberOutcome:
    ok: bool
    value: Any
    records: tuple
    firings: int | None
    physics: dict


_WORKER_PHYSICS: dict | None = None
_WORKER_MEMOS: dict | None = None


def _resolve(reference: str) -> Callable[..., Any]:
    module, _, name = reference.partition(':')
    target: Any = importlib.import_module(module)
    for part in name.split('.'):
        target = getattr(target, part)
    return target


def _merge_physics(store: dict, entries: dict) -> None:
    for partition, values in entries.items():
        if not isinstance(partition, str) or not isinstance(values, dict):
            continue
        target = store.setdefault(partition, {})
        for key, value in values.items():
            if isinstance(key, str) and isinstance(value, float) and key not in target:
                target[key] = value


def _snapshot(store: dict | None) -> dict:
    return {} if store is None else {p: dict(v) for p, v in store.items()}


def run_member(task: MemberTask) -> MemberOutcome:
    """Worker entry point: one member derivation under the run's caches and observer."""
    global _WORKER_PHYSICS, _WORKER_MEMOS
    from contextlib import nullcontext
    from joulewise.analysis_run_cache import analysis_run_caches
    from joulewise.authentication_io import V2AuthenticationReadSession
    from joulewise.b5_analysis.deadline_observer import observe_wall_deadline
    from joulewise.whole_window import shared_instrument_calibration_physics_cache

    if _WORKER_PHYSICS is None:
        _WORKER_PHYSICS, _WORKER_MEMOS = {}, {}
    _merge_physics(_WORKER_PHYSICS, task.physics)
    session = V2AuthenticationReadSession() if task.session else None
    ok, value = True, None
    with shared_instrument_calibration_physics_cache(_WORKER_PHYSICS), \
            analysis_run_caches(_WORKER_PHYSICS, memos=_WORKER_MEMOS), observe_wall_deadline() as deadline:
        try:
            with session if session is not None else nullcontext():
                value = _resolve(task.function)(*task.args, **task.kwargs)
        except BaseException:  # noqa: BLE001 - the caller recomputes serially
            ok, value = False, None
        firings = None if deadline is None else deadline.firings
    records = () if session is None else tuple(
        (record.normalized_path, record.sha256, record.grammar, record.read_count)
        for record in session.records.values())
    return MemberOutcome(ok, value if ok else None, records, firings, _snapshot(_WORKER_PHYSICS))


def _pool(caches):
    if caches.pool is None:
        import concurrent.futures as cf
        import multiprocessing
        caches.pool = cf.ProcessPoolExecutor(max_workers=caches.workers,
                                             mp_context=multiprocessing.get_context('spawn'))
    return caches.pool


def member_map(function: Callable[..., Any], calls: Sequence[tuple[tuple, dict]],
               *, worker: Callable[[MemberTask], MemberOutcome] | None = None) -> list[MemberOutcome] | None:
    """Outcomes of ``function(*args, **kwargs)`` per call, in call order; or None (run serially)."""
    from joulewise import analysis_run_cache
    from joulewise.authentication_io import active_v2_authentication_session

    caches = analysis_run_cache.current()
    if caches is None or caches.workers < 2 or len(calls) < 2:
        return None
    reference = f'{function.__module__}:{function.__qualname__}'
    if '<' in reference or _resolve(reference) is not function:
        return None
    worker = run_member if worker is None else worker
    session = active_v2_authentication_session() is not None
    physics = _snapshot(caches.physics_store)
    pool = _pool(caches)
    futures = [pool.submit(worker, MemberTask(reference, tuple(args), dict(kwargs), session, physics))
               for args, kwargs in calls]
    outcomes = []
    broken = False
    for future in futures:
        try:
            outcomes.append(future.result())
        except Exception:  # noqa: BLE001 - a lost worker: recompute in the caller
            broken = True
            outcomes.append(MemberOutcome(False, None, (), 0, {}))
    if broken:
        caches.pool.shutdown(wait=True, cancel_futures=True)
        caches.pool = None
    for outcome in outcomes:
        if outcome.firings is None:
            caches.worker_observer_unavailable = True
        elif outcome.firings:
            if caches.deadline is not None:
                caches.deadline.firings += outcome.firings
            else:
                caches.worker_observer_unavailable = True
        elif outcome.ok and caches.physics_store is not None:
            _merge_physics(caches.physics_store, outcome.physics)
    return outcomes


def consume(outcome: MemberOutcome | None, compute: Callable[[], Any]) -> Any:
    """The member's value at its serial position: the worker's, or ``compute()`` serially."""
    if outcome is None or not outcome.ok:
        return compute()
    from joulewise.authentication_io import active_v2_authentication_session

    session = active_v2_authentication_session()
    if session is not None:
        with session._lock:
            for identity, digest, grammar, count in outcome.records:
                for _ in range(count):
                    session._register(identity, digest, grammar, f'member derivation input {identity}')
    return outcome.value
