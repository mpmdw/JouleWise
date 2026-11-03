"""Deterministic process-parallel dispatch of independent child programs (L9-SPEEDUP-R1).

Only the child program's execution moves to a spawned worker. Everything that
decides the record stays serial in the driver process, in the serial order:
re-authentication of earlier outputs, registration, refusal classification and
the stop at the first refusal. Each task carries the log counter it would have
had serially, so restricted logs keep their names. When a serial run would
have stopped at task k, the driver removes every later task's files and resets
the counter, leaving custody as the serial run would have.

Member pools (L9-SPEEDUP-R2): each child enters the run caches with its share
of the workers (``member_worker_shares``: at least 1, the serial path), so a
child with several workers (step 4's two packs) runs its whole-window
re-derivations and strict validations in a nested ordered member pool
(``joulewise.analysis_member_pool``). Its pool reports firings to the child's
observer; a member worker that could not observe makes the child report
``firings=None``, which fails the step closed in the driver. D-188: with no
more tasks than workers, the leftover workers go to the last task (step 4 at
7 workers: alpha 3, beta 4); with more tasks than workers (steps 1 and 2)
every child keeps exactly 1 (Sol #1: never 0).

Verified store (D-188 SHIP). When the run has a store, each task is shipped a
store context (``ChildTask.vdl``: mode, commit, the entries the driver selected
for it, the shipped memos); the child creates its own store from it, enters a
verification scope per program (``StepRunner.run``) and returns what it added
(``ChildResult.vdl_new``). Defects, poisoned keys and restricted counters merge
into the driver's store here, from every result (consumed or not); entries
merge only in the driver after its serial stop (``dry_run._account_deadlines``),
from the consumed, firing-free prefix.

Physics: the driver's run store is shipped to every task (seeded first with one
task per distinct calibration so workers rarely fit), and each worker keeps its
own store and memos for the step. A worker reports its wall-deadline firings
(counted by the same sys.monitoring observer the driver uses); the driver adds
them to its own observer, so a firing in a worker fails the step closed as
``calibration_wall_deadline_fired``. A worker with no observer fails the step as
``calibration_deadline_observer_unavailable``. Entries a worker fitted are merged
into the driver's store only from tasks whose deadline did not fire.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import importlib
import json
import os
from pathlib import Path
import time
from typing import Any, Callable, Sequence

WORKERS_ENV = 'JOULEWISE_B5_ANALYSIS_WORKERS'
DEFAULT_MAX_WORKERS = 8


def default_workers() -> int:
    """min(8, cpu_count - 2), at least 1."""
    return max(1, min(DEFAULT_MAX_WORKERS, (os.cpu_count() or 1) - 2))


def resolve_workers(requested: int | None = None) -> int:
    """An explicit count, else JOULEWISE_B5_ANALYSIS_WORKERS, else the default.

    An explicit count must be a positive int (ValueError otherwise). An
    environment value that is not a positive integer is ignored.
    """
    if requested is not None:
        if isinstance(requested, bool) or not isinstance(requested, int) or requested < 1:
            raise ValueError('workers must be a positive integer')
        return requested
    value = os.environ.get(WORKERS_ENV)
    if value is not None:
        try:
            parsed = int(value.strip())
        except ValueError:
            parsed = 0
        if parsed >= 1:
            return parsed
    return default_workers()


@dataclass(frozen=True)
class ChildTask:
    restricted: str
    counter: int
    step: str
    window: str | None
    program: str
    argv: tuple[str, ...]
    physics: dict
    # L9-SPEEDUP-R2: the child's own member-pool workers (1 is the serial path).
    member_workers: int = 1
    # D-188 SHIP: the store context ({} when the run has no store).
    vdl: dict = field(default_factory=dict)
    # D-188 TIMERS: run a sinkless child timer and return its table.
    timing: bool = False


@dataclass(frozen=True)
class ChildResult:
    exit_status: int
    stdout_path: str
    stderr_path: str
    exception: bool
    firings: int | None
    physics: dict
    # D-188 SHIP: entries, memos and side channel the child added.
    vdl_new: dict = field(default_factory=dict, compare=False)
    # D-188 TIMERS: the child timer's table (restricted tier) or None.
    timing: dict | None = field(default=None, compare=False)
    # D-188 SHIP (Sol #12): the class of an exception that escaped the program.
    exception_class: str | None = field(default=None, compare=False)


# One store and one set of memos per worker process for the step's pool.
_WORKER_PHYSICS: dict | None = None
_WORKER_MEMOS: dict | None = None


def _program(reference: str) -> Callable[[list[str]], Any]:
    module, _, name = reference.partition(':')
    return getattr(importlib.import_module(module), name)


def _merge(store: dict, entries: dict) -> None:
    """Add verified entries absent from ``store``; never overwrite one."""
    for partition, values in entries.items():
        if not isinstance(partition, str) or not isinstance(values, dict):
            continue
        target = store.setdefault(partition, {})
        for key, value in values.items():
            if isinstance(key, str) and isinstance(value, float) and key not in target:
                target[key] = value


def _snapshot(store: dict) -> dict:
    return {partition: dict(values) for partition, values in store.items()}


def run_child(task: ChildTask) -> ChildResult:
    """Worker entry point: the real program under the run's caches and observer."""
    global _WORKER_PHYSICS, _WORKER_MEMOS
    from joulewise.analysis_member_pool import export_new, seed_memos
    from joulewise.analysis_run_cache import analysis_run_caches
    from joulewise.whole_window import shared_instrument_calibration_physics_cache
    from . import phase_timing
    from .deadline_observer import observe_wall_deadline
    from .dry_run import StepRunner

    if _WORKER_PHYSICS is None:
        _WORKER_PHYSICS, _WORKER_MEMOS = {}, {}
    _merge(_WORKER_PHYSICS, task.physics)
    context = task.vdl or {}
    memos_before = seed_memos(_WORKER_MEMOS, context)
    runner = StepRunner(Path(task.restricted))
    runner._counter = task.counter - 1
    main = _program(task.program)
    with shared_instrument_calibration_physics_cache(_WORKER_PHYSICS), \
            analysis_run_caches(_WORKER_PHYSICS, memos=_WORKER_MEMOS, workers=task.member_workers,
                                vdl_mode=context.get('mode'), vdl_commit=context.get('commit'),
                                vdl_entries=context.get('entries')) as caches, \
            observe_wall_deadline() as deadline:
        # As in the driver: the child's member pool reports its workers' firings
        # to this observer, and a member worker that could not observe makes the
        # child unobservable (the driver then refuses the step).
        caches.deadline = deadline
        with phase_timing.child_session(task.timing):
            result = runner.run(main, list(task.argv), step=task.step, window=task.window)
        firings = None if deadline is None or caches.worker_observer_unavailable else deadline.firings
        vdl_new = export_new(caches, context, memos_before)
    return ChildResult(result.exit_status, str(result.stdout_path), str(result.stderr_path),
                       result.exception, firings, _snapshot(_WORKER_PHYSICS), vdl_new=vdl_new,
                       timing=phase_timing.child_table() if task.timing else None,
                       exception_class=getattr(result, 'exception_class', None))


def _calibration_key(argv: Sequence[str]) -> tuple[str, str] | None:
    """(metadata bound partition, calibration artifact sha256) of a bundle argument.

    Scheduling only: which task to run first so its fit seeds the others. It
    authenticates nothing; a wrong or unreadable value only costs a refit.
    """
    from joulewise.whole_window import _effective_bound_partition
    for argument in argv:
        path = Path(argument)
        if not (path / 'metadata.json').is_file():
            continue
        try:
            metadata = json.loads((path / 'metadata.json').read_bytes())
            calibration = metadata.get('instrument_calibration')
            digest = calibration.get('artifact_sha256') if isinstance(calibration, dict) else None
            partition = _effective_bound_partition(metadata)
        except (OSError, ValueError, AttributeError):
            return None
        if isinstance(digest, str) and partition is not None:
            return partition, digest
        return None
    return None


class WorkerDeadlineState:
    """Deadline observations reported by workers, for the driver."""

    def __init__(self):
        self.firings = 0
        self.unavailable = False


def member_worker_shares(workers: int, count: int) -> list[int]:
    """Each of ``count`` children's member-pool workers (D-188, Sol #1).

    With more children than workers every child gets 1 (the serial path; a
    child is never given 0, which the run caches reject). Otherwise each gets
    ``workers // count`` and the last one also the remainder.
    """
    if count < 1:
        return []
    if workers < count:
        return [1] * count
    share = workers // count
    return [share] * (count - 1) + [workers - (count - 1) * share]


def dispatch(tasks: Sequence[tuple[str, Sequence[str], str, str | None]], *, restricted: Path, first_counter: int,
             workers: int, physics_store: dict, worker: Callable[[ChildTask], ChildResult] | None = None,
             vdl: Sequence[dict] | None = None, timing: bool = False,
             ) -> tuple[list[ChildResult], WorkerDeadlineState]:
    """Run (program, argv, step, window) tasks in a spawned pool; results in task order.

    ``first_counter`` is the log counter of the first task; task i gets
    first_counter + i. Seed tasks (the first task of each calibration whose fit
    the store lacks) run first; every later task is shipped the merged store.
    An exception in a worker propagates after the pool is shut down.
    ``vdl`` gives task i its store context (``analysis_member_pool.vdl_context``);
    ``timing`` runs a child timer in each task and merges its table here.
    """
    import concurrent.futures as cf
    import multiprocessing
    from joulewise import analysis_run_cache
    from joulewise.analysis_member_pool import fill_active, merge_side_channel
    from . import phase_timing

    # Resolved at call time: a test substitutes a module-level wrapper of run_child.
    worker = run_child if worker is None else worker
    state = WorkerDeadlineState()
    if not tasks:
        return [], state
    if fill_active():
        # D-188: a child's reads are invisible to an enclosing fill's recorder.
        from joulewise.analysis_verified_store import note_unstorable
        note_unstorable('child_pool')
    caches = analysis_run_cache.current()
    specs = [(program, tuple(str(a) for a in argv), step, window) for program, argv, step, window in tasks]
    seeds, seen = [], set()
    for index, (_, argv, _, _) in enumerate(specs):
        key = _calibration_key(argv)
        if key is None or key in seen or key[1] in physics_store.get(key[0], {}):
            continue
        seen.add(key)
        seeds.append(index)
    results: list[ChildResult | None] = [None] * len(specs)

    # L9-SPEEDUP-R2: each child gets its share of the workers for its own
    # member pool (steps 1 and 2 have more tasks than workers: 1, serial).
    shares = member_worker_shares(workers, len(specs))
    contexts = list(vdl) if vdl is not None else [{}] * len(specs)

    def make(index):
        program, argv, step, window = specs[index]
        return ChildTask(str(restricted), first_counter + index, step, window, program, argv,
                         _snapshot(physics_store), shares[index], contexts[index] or {}, bool(timing))

    def collect(index, result):
        results[index] = result
        if result.firings is None:
            state.unavailable = True
        elif result.firings:
            state.firings += result.firings
        else:
            _merge(physics_store, result.physics)
        # D-188: a child's defects and counters count whether or not the driver
        # consumes it; its poison and entries merge only for a consumed child,
        # after the serial stop (dry_run._account_deadlines; SHIP-FIX finding B).
        merge_side_channel(caches, result.vdl_new)
        phase_timing.merge_child(result.timing)

    context = multiprocessing.get_context('spawn')
    size = max(1, min(workers, len(specs)))
    pool = cf.ProcessPoolExecutor(max_workers=size, mp_context=context)
    started = time.perf_counter_ns()
    try:
        with phase_timing.dispatch_wait():
            futures = {index: pool.submit(worker, make(index)) for index in seeds}
            for index in seeds:
                collect(index, futures[index].result())
            rest = [index for index in range(len(specs)) if index not in futures]
            futures = {index: pool.submit(worker, make(index)) for index in rest}
            for done, index in enumerate(rest):
                collect(index, futures[index].result())
                phase_timing.pool_progress(len(seeds) + done + 1, len(specs))
    except BaseException:
        pool.shutdown(wait=True, cancel_futures=True)
        raise
    pool.shutdown(wait=True)
    if timing:
        phase_timing.pool_batch('dispatch', [{'wall_ns': r.timing.get('wall_ns', 0), 'cpu_ns': r.timing.get('cpu_ns', 0)}
                                             for r in results if isinstance(r.timing, dict)],
                                time.perf_counter_ns() - started, size)
    return [result for result in results], state


def discard_after(results: Sequence[ChildResult], stop: int, outputs: Sequence[Path | None] = (),
                  created_dirs: Sequence[Path] = ()) -> None:
    """Remove the files of tasks after ``stop`` (a serial run never started them).

    ``created_dirs`` are output directories the driver created ahead of the
    pool; any of them left empty is removed too, in reverse creation order.
    """
    for index in range(stop + 1, len(results)):
        for path in (results[index].stdout_path, results[index].stderr_path):
            Path(path).unlink(missing_ok=True)
        if index < len(outputs) and outputs[index] is not None:
            Path(outputs[index]).unlink(missing_ok=True)
    for directory in reversed(list(created_dirs)):
        try:
            Path(directory).rmdir()
        except OSError:
            pass
