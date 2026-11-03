"""Ordered process pool for independent whole-window member derivations (L9-SPEEDUP-R1 stage 4b).

Only the computation moves: a caller hands ``member_map`` one call per member of
a module-level pure function, in member order, and then consumes the outcomes in
that same order exactly where the serial loop called the function. Everything
the caller decides stays serial.

Active only in a process that entered ``analysis_run_caches(..., workers=N)`` with
N > 1 (the block-5 driver, and since L9-SPEEDUP-R2 a step-4 child with its share
of the workers); anywhere else ``member_map`` returns ``None`` and the caller
runs its unchanged serial loop.

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
* Stops (L9-SPEEDUP-R2). A caller whose serial loop can stop before its last
  member (an exception, a refusal) passes ``account=False`` and reports only the
  outcomes it consumed through ``account_outcomes``: a task the serial loop never
  reached ran only because of the pool, so its observations and its fits count
  no more than its value does.

Since L9-SPEEDUP-R2 a step-4 child (``b5_analysis.parallel.run_child``) is also
a run driver for this purpose: it enters the run caches with its share of the
workers, so its whole-window and strict-validation members use a nested pool.

D-188 SHIP: the verified derivation store (``joulewise.analysis_verified_store``).
Nothing below changes while the run has no store (``vdl_mode`` off): no task is
pre-filtered, nothing is shipped, nothing is merged.

* Pre-filter. Before dispatching, each call of a registered leaf (the leaf
  itself, or one of the two strict-validation wrappers in ``_WRAPPED_LEAVES``)
  is probed with the store's side-effect-free ``probe``. A hit is not
  dispatched: it becomes an outcome that carries the probed hit, and
  ``consume`` applies it at the member's own serial position (``hit.apply()``
  re-verifies the trees, extras and physics admission there and registers the
  entry's V2 rows through the consumer session's own checks; it never uses the
  worker 4-tuple path). If applying raises, the member is computed serially
  there. A hit that shadow mode samples is dispatched instead, with its entry,
  so the worker's store recomputes and compares it.
* Fills in workers. A worker task with a store context runs a registered leaf
  through ``store.call`` in a fresh store seeded with the entries it was
  shipped, and returns what it added (``MemberOutcome.vdl_new``).
* Merge. Defects, poisoned keys and restricted counters merge from every
  outcome, consumed or not (Sol #11: a shadow mismatch survives the worker's
  ``except BaseException`` and the caller's serial recomputation). Entries and
  the shipped memos merge only from consumed outcomes that are ok and
  firing-free, and never overwrite.
* Recorder. While a leaf fill is being recorded in this process
  (``fill_active()``), ``member_map`` stays serial: a pool worker's reads are
  invisible to the fill's read recorder, also when the pool already exists (no
  thread start marks the fill then).
"""
from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from pathlib import Path
import sys
import time
from typing import Any, Callable, Sequence


@dataclass(frozen=True)
class MemberTask:
    function: str
    args: tuple
    kwargs: dict
    session: bool
    physics: dict
    # D-188 SHIP: the run's verified-store context ({} when the run has no store):
    # mode, commit, the entries this task is shipped and the shipped memo tables.
    vdl: dict = field(default_factory=dict)
    # D-188 TIMERS: time this task in the worker (restricted tier only).
    timing: bool = False


@dataclass(frozen=True)
class MemberOutcome:
    ok: bool
    value: Any
    records: tuple
    firings: int | None
    physics: dict
    # D-188 SHIP: what the task added to its worker's store (entries, memos) and
    # its side channel (defects, poisoned keys, restricted counters).
    vdl_new: dict = field(default_factory=dict, compare=False)
    # D-188 TIMERS: the worker's task cost (wall_ns, cpu_ns, phases) or None.
    cost: dict | None = field(default=None, compare=False)
    # D-188 SHIP: a pre-filter hit (never pickled: synthesized in the caller) and
    # the wrapper's projection of the leaf value (None: the value itself).
    hit: Any = field(default=None, compare=False, repr=False)
    post: Any = field(default=None, compare=False, repr=False)


# The two run memos shipped to and merged back from worker tasks when the run
# has a verified store (content-keyed, deterministic, never a firing's value).
SHIPPED_MEMOS = ('environment_admission.window_thermal_pressure', 'cli.strict_clock_evidence')


def _floor_strict_leaf(path, strict):
    return (path,), {'strict': strict}


def _bracket_strict_leaf(path_text):
    return (Path(path_text),), {'strict': True, 'physics_cache': {}}


# Member functions that are thin wrappers of a registered leaf: (leaf id, leaf
# reference, wrapper arguments -> leaf arguments, leaf value -> wrapper value).
# floor_extraction._default_strict_validator(path, strict) is
# validate_bundle(path, strict=strict); bracket._strict_problems(path_text) is
# list(validate_bundle(Path(path_text), strict=True, physics_cache={})).
_WRAPPED_LEAVES = {
    'joulewise.floor_extraction:_default_strict_validator':
        ('L1_strict_validation', 'joulewise.cli:validate_bundle', _floor_strict_leaf, None),
    'joulewise.b5_analysis.bracket:_strict_problems':
        ('L1_strict_validation', 'joulewise.cli:validate_bundle', _bracket_strict_leaf, list),
}


_WORKER_PHYSICS: dict | None = None
_WORKER_MEMOS: dict | None = None


def _resolve(reference: str) -> Callable[..., Any]:
    module, _, name = reference.partition(':')
    target: Any = importlib.import_module(module)
    for part in name.split('.'):
        target = getattr(target, part)
    return target


def is_genuine(function: Any, reference: str) -> bool:
    """Whether ``function`` is the module-level function ``reference`` names.

    A worker resolves the function by reference, so a caller ships a member to
    the pool only when the function it would call serially is that function
    (never a test double or a wrapper installed in the caller's process).
    """
    module, _, name = reference.partition(':')
    return (getattr(function, '__module__', None) == module
            and getattr(function, '__qualname__', None) == name
            and _resolve(reference) is function)


def single_bound_per_calibration(bundles: Sequence[Any]) -> bool:
    """Whether no calibration artifact appears under two metadata bounds in ``bundles``.

    The reducer caches max(metadata ``b_fiducial_s``, fresh bound) under the
    calibration artifact's sha256 alone. A serial loop that shares one
    call-local cache (or one read session's cache) across its members can carry
    one member's metadata bound to another member with the same artifact; a pool
    task starts from a fresh local cache. When every artifact appears under one
    metadata bound, both give every member the same value; otherwise the caller
    stays serial (L9-SPEEDUP-R2; cf. R1 review F3). Scheduling only: a bundle
    whose metadata cannot be read here keeps the caller serial.
    """
    import json
    from pathlib import Path

    from joulewise.whole_window import _effective_bound_partition

    seen: dict[str, str | None] = {}
    for bundle in bundles:
        try:
            metadata = json.loads((Path(bundle) / 'metadata.json').read_bytes())
            calibration = metadata.get('instrument_calibration') if isinstance(metadata, dict) else None
            digest = calibration.get('artifact_sha256') if isinstance(calibration, dict) else None
        except (OSError, ValueError):
            return False
        if not isinstance(digest, str):
            continue
        partition = _effective_bound_partition(metadata)
        if seen.setdefault(digest, partition) != partition:
            return False
    return True


def pool_active() -> bool:
    """Whether ``member_map`` would use a pool here (for callers that schedule work)."""
    from joulewise import analysis_run_cache

    caches = analysis_run_cache.current()
    return caches is not None and caches.workers >= 2


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


# --------------------------------------------------------------- D-188 SHIP: store


def _store_module():
    """``joulewise.analysis_verified_store`` if this process imported it (else None)."""
    return sys.modules.get('joulewise.analysis_verified_store')


def vdl_store(caches=None):
    """The active run's verified store, or None (no run, or the run has none)."""
    if caches is None:
        from joulewise import analysis_run_cache
        caches = analysis_run_cache.current()
    return None if caches is None else getattr(caches, 'vdl', None)


def fill_active() -> bool:
    """Whether a leaf fill is being recorded in this process (a pool would escape it)."""
    module = _store_module()
    return module is not None and module.fill_active()


def _leaf_call(reference: str, args: tuple, kwargs: dict):
    """(leaf id, leaf function, leaf args, leaf kwargs, post) for a registered leaf call, or None."""
    module = _store_module()
    if module is None:
        return None
    wrapped = _WRAPPED_LEAVES.get(reference)
    try:
        if wrapped is not None:
            leaf_id, leaf_reference, adapt, post = wrapped
            leaf_args, leaf_kwargs = adapt(*args, **kwargs)
            return leaf_id, _resolve(leaf_reference), leaf_args, leaf_kwargs, post
        # The registry by id (the closed LEAVES plus test-only registrations).
        specs = getattr(module, '_LEAVES_BY_ID', None)
        for spec in (specs.values() if isinstance(specs, dict) else module.LEAVES):
            if reference in spec.qualnames:
                return spec.leaf_id, _resolve(reference), tuple(args), dict(kwargs), None
    except Exception:  # noqa: BLE001 - an unresolvable leaf is simply not a leaf call
        return None
    return None


def _shadow_sampled(store, hit) -> bool:
    """Whether ``store.call`` would shadow-recompute this hit (the same key-hash sample)."""
    mode = store.mode
    if mode.name != 'shadow':
        return False
    try:
        return int(hit.prepared.key[:8], 16) % 1000 < mode.permille
    except Exception:  # noqa: BLE001 - unknowable: treat as sampled (dispatch, never serve)
        return True


def shipped_memos(caches) -> dict:
    tables = getattr(caches, 'memos', None) or {}
    return {name: dict(tables[name]) for name in SHIPPED_MEMOS if tables.get(name)}


def vdl_context(caches, entries: dict | None = None) -> dict:
    """The store context a worker task is shipped ({} when the run has no store).

    ``entries`` is an ``export_entries`` payload (its defects are never shipped
    down: they stay with the process that recorded them).
    """
    store = vdl_store(caches)
    if store is None:
        return {}
    if entries is not None:
        entries = {**entries, 'defects': []}
    return {'mode': store.mode, 'commit': store.commit, 'entries': entries, 'memos': shipped_memos(caches)}


def seed_memos(memos: dict, context: dict) -> dict:
    """Add the context's shipped memo entries to ``memos`` (never overwrite); return the keys before."""
    for name, table in (context.get('memos') or {}).items():
        if name in SHIPPED_MEMOS and isinstance(table, dict):
            target = memos.setdefault(name, {})
            for key, value in table.items():
                target.setdefault(key, value)
    return {name: set(memos.get(name, {})) for name in SHIPPED_MEMOS}


def export_new(caches, context: dict, memos_before: dict) -> dict:
    """What this task added: store entries not shipped to it, new memo entries, side channel."""
    store = vdl_store(caches)
    if store is None:
        return {}
    shipped = set(((context.get('entries') or {}).get('entries') or {}))
    payload = store.export_entries(lambda key, _entry: key not in shipped)
    payload['counters'] = store.restricted_counters()
    tables = getattr(caches, 'memos', None) or {}
    payload['memos'] = {name: {key: value for key, value in tables.get(name, {}).items()
                               if key not in memos_before.get(name, ())}
                        for name in SHIPPED_MEMOS if tables.get(name)}
    return payload


def merge_side_channel(caches, payload: dict | None) -> None:
    """Defects, poisoned keys and restricted counters of any outcome (consumed or not)."""
    store = vdl_store(caches)
    if store is None or not payload:
        return
    store.merge_entries({'schema': payload.get('schema'), 'entries': {},
                         'poisoned': payload.get('poisoned', ()), 'defects': payload.get('defects', ())})
    counters = payload.get('counters')
    if not isinstance(counters, dict):
        return
    for name, count in counters.items():
        if not isinstance(name, str) or type(count) is not int or count <= 0:
            continue
        if name.startswith('defect:'):
            # A blind worker counted its defect instead of raising it: the run's
            # store counts it too and stops serving (lead ruling).
            for _ in range(count):
                store._defect(name[len('defect:'):])
            continue
        with store._lock:
            store._counters[name] = store._counters.get(name, 0) + count


def merge_consumed(caches, payload: dict | None) -> None:
    """Entries and shipped memos of a consumed, ok, firing-free outcome (never overwrite)."""
    store = vdl_store(caches)
    if store is None or not payload:
        return
    store.merge_entries({'schema': payload.get('schema'), 'entries': payload.get('entries') or {},
                         'poisoned': (), 'defects': ()})
    tables = getattr(caches, 'memos', None)
    if tables is None:
        return
    for name, table in (payload.get('memos') or {}).items():
        if name in SHIPPED_MEMOS and isinstance(table, dict):
            target = tables.setdefault(name, {})
            for key, value in table.items():
                target.setdefault(key, value)


def _count(store, name: str) -> None:
    try:
        store._count(name)
    except Exception:  # noqa: BLE001 - restricted counters never affect the run
        pass


def run_member(task: MemberTask) -> MemberOutcome:
    """Worker entry point: one member derivation under the run's caches and observer."""
    global _WORKER_PHYSICS, _WORKER_MEMOS
    from contextlib import nullcontext
    from joulewise.analysis_run_cache import analysis_run_caches
    from joulewise.authentication_io import V2AuthenticationReadSession
    from joulewise.b5_analysis import phase_timing
    from joulewise.b5_analysis.deadline_observer import observe_wall_deadline
    from joulewise.whole_window import shared_instrument_calibration_physics_cache

    if _WORKER_PHYSICS is None:
        _WORKER_PHYSICS, _WORKER_MEMOS = {}, {}
    _merge_physics(_WORKER_PHYSICS, task.physics)
    context = task.vdl or {}
    if context.get('mode') is not None:
        import joulewise.analysis_verified_store  # noqa: F401 - the store's leaf registry
    memos_before = seed_memos(_WORKER_MEMOS, context)
    session = V2AuthenticationReadSession() if task.session else None
    ok, value, vdl_new = True, None, {}
    with shared_instrument_calibration_physics_cache(_WORKER_PHYSICS), \
            analysis_run_caches(_WORKER_PHYSICS, memos=_WORKER_MEMOS, vdl_mode=context.get('mode'),
                                vdl_commit=context.get('commit'), vdl_entries=context.get('entries')) as caches, \
            observe_wall_deadline() as deadline, phase_timing.task_cost(task.timing) as cost:
        # The run memos never store a value computed while a deadline fired.
        caches.deadline = deadline
        try:
            with session if session is not None else nullcontext():
                leaf = _leaf_call(task.function, task.args, task.kwargs) if caches.vdl is not None else None
                if leaf is None:
                    value = _resolve(task.function)(*task.args, **task.kwargs)
                else:
                    # Through the store: a fill here is exported to the caller;
                    # a shipped entry is served (or shadow-recomputed) here.
                    leaf_id, fn, leaf_args, leaf_kwargs, post = leaf
                    value = caches.vdl.call(leaf_id, fn, *leaf_args, **leaf_kwargs)
                    if post is not None:
                        value = post(value)
        except BaseException:  # noqa: BLE001 - the caller recomputes serially
            ok, value = False, None
        firings = None if deadline is None else deadline.firings
        vdl_new = export_new(caches, context, memos_before)
    records = () if session is None else tuple(
        (record.normalized_path, record.sha256, record.grammar, record.read_count)
        for record in session.records.values())
    return MemberOutcome(ok, value if ok else None, records, firings, _snapshot(_WORKER_PHYSICS),
                         vdl_new=vdl_new, cost=cost)


def _pool(caches):
    if caches.pool is None:
        import concurrent.futures as cf
        import multiprocessing
        caches.pool = cf.ProcessPoolExecutor(max_workers=caches.workers,
                                             mp_context=multiprocessing.get_context('spawn'))
    return caches.pool


def _prefilter(store, reference: str, args, kwargs):
    """A probed hit for this call ('hit', hit, post), a shadow-sampled one ('shadow', hit), or None."""
    leaf = _leaf_call(reference, tuple(args), dict(kwargs))
    if leaf is None:
        return None
    leaf_id, fn, leaf_args, leaf_kwargs, post = leaf
    try:
        hit = store.probe(leaf_id, fn, *leaf_args, **leaf_kwargs)
    except Exception:  # noqa: BLE001 - probe is side-effect free; a failure is a miss
        return None
    if hit is None:
        return None
    if _shadow_sampled(store, hit):
        return ('shadow', hit)
    return ('hit', hit, post)


def member_map(function: Callable[..., Any], calls: Sequence[tuple[tuple, dict]],
               *, worker: Callable[[MemberTask], MemberOutcome] | None = None,
               account: bool = True) -> list[MemberOutcome] | None:
    """Outcomes of ``function(*args, **kwargs)`` per call, in call order; or None (run serially).

    With ``account=False`` nothing is reported to the run yet: the caller passes
    the outcomes it consumed to ``account_outcomes`` (always, also when its loop
    stops early or raises).
    """
    from joulewise import analysis_run_cache
    from joulewise.authentication_io import active_v2_authentication_session
    from joulewise.b5_analysis import phase_timing

    caches = analysis_run_cache.current()
    if caches is None or caches.workers < 2 or len(calls) < 2:
        return None
    reference = f'{function.__module__}:{function.__qualname__}'
    if '<' in reference or _resolve(reference) is not function:
        return None
    if fill_active():
        # D-188: a worker's reads would escape the enclosing fill's recorder.
        return None
    worker = run_member if worker is None else worker
    session = active_v2_authentication_session() is not None
    physics = _snapshot(caches.physics_store)
    store = vdl_store(caches)
    outcomes: list[MemberOutcome | None] = [None] * len(calls)
    contexts: dict[int, dict] = {}
    for index, (args, kwargs) in enumerate(calls):
        found = _prefilter(store, reference, args, kwargs) if store is not None else None
        if found is not None and found[0] == 'hit':
            _count(store, 'ship:prefilter_hit')
            outcomes[index] = MemberOutcome(True, None, (), 0, {}, hit=found[1], post=found[2])
            continue
        if found is not None:
            # Shadow-sampled: the worker recomputes it against the shipped entry.
            hit = found[1]
            entries = {'schema': getattr(_store_module(), 'SCHEMA', None), 'entries': {hit.key: hit.entry},
                       'poisoned': [], 'defects': []}
            contexts[index] = vdl_context(caches, entries)
        else:
            contexts[index] = vdl_context(caches)
    pending = [index for index in range(len(calls)) if outcomes[index] is None]
    timing = phase_timing.enabled()
    broken = False
    if pending:
        pool = _pool(caches)
        started = time.perf_counter_ns()
        futures = {index: pool.submit(worker, MemberTask(reference, tuple(calls[index][0]), dict(calls[index][1]),
                                                         session, physics, contexts[index], timing))
                   for index in pending}
        with phase_timing.pool_wait():
            for done, index in enumerate(pending):
                try:
                    outcomes[index] = futures[index].result()
                except Exception:  # noqa: BLE001 - a lost worker: recompute in the caller
                    broken = True
                    outcomes[index] = MemberOutcome(False, None, (), 0, {})
                phase_timing.pool_progress(done + 1, len(pending))
        phase_timing.pool_batch(reference, [outcomes[index].cost for index in pending],
                                time.perf_counter_ns() - started, caches.workers)
    if broken:
        caches.pool.shutdown(wait=True, cancel_futures=True)
        caches.pool = None
    if store is not None:
        for outcome in outcomes:
            merge_side_channel(caches, outcome.vdl_new)
    if account:
        account_outcomes(outcomes)
    return outcomes


def account_outcomes(outcomes: Sequence[MemberOutcome | None]) -> None:
    """Report consumed outcomes to the run: firings, unobservable workers, verified fits."""
    from joulewise import analysis_run_cache

    caches = analysis_run_cache.current()
    if caches is None:
        return
    for outcome in outcomes:
        if outcome is None:
            continue
        if outcome.firings is None:
            caches.worker_observer_unavailable = True
        elif outcome.firings:
            if caches.deadline is not None:
                caches.deadline.firings += outcome.firings
            else:
                caches.worker_observer_unavailable = True
        elif outcome.ok:
            if caches.physics_store is not None:
                _merge_physics(caches.physics_store, outcome.physics)
            # D-188: a consumed, firing-free outcome's store entries and memos.
            merge_consumed(caches, outcome.vdl_new)


def consume(outcome: MemberOutcome | None, compute: Callable[[], Any], *, account: bool = False) -> Any:
    """The member's value at its serial position: the worker's, or ``compute()`` serially.

    ``account=True`` (for outcomes of ``member_map(..., account=False)``) first
    reports this outcome to the run, as the serial loop's own observation of a
    member it reached.
    """
    if account:
        account_outcomes((outcome,))
    if outcome is None or not outcome.ok:
        return compute()
    if outcome.hit is not None:
        # D-188: a pre-filtered store hit, applied here (its rows registered
        # through the consumer session's own checks); any anomaly computes.
        from joulewise.b5_analysis import phase_timing
        try:
            with phase_timing.span('k.vdl.hit'):
                value = outcome.hit.apply()
        except Exception:  # noqa: BLE001 - the leaf runs at this position
            _count(outcome.hit.store, 'ship:prefilter_hit_discarded')
            return compute()
        return value if outcome.post is None else outcome.post(value)
    from joulewise.authentication_io import active_v2_authentication_session

    session = active_v2_authentication_session()
    if session is not None:
        with session._lock:
            for identity, digest, grammar, count in outcome.records:
                for _ in range(count):
                    session._register(identity, digest, grammar, f'member derivation input {identity}')
    return outcome.value
