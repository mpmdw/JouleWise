"""Ordered, bounded pack computations with the member pool's authentication rules.

Only consumed outcomes replay reads, deadlines, poison and store entries. Failed
computations run again at their serial position, so the original code owns the
exception and its partial census. Callers own isolated staging and publication.
"""
from __future__ import annotations

from contextlib import nullcontext, redirect_stderr, redirect_stdout
from dataclasses import dataclass
import io
import multiprocessing
import pickle
from types import MappingProxyType

from joulewise import analysis_member_pool as members, analysis_run_cache as arc
from joulewise.authentication_io import V2AuthenticationReadSession, active_v2_authentication_session
from . import phase_timing
from .deadline_observer import observe_wall_deadline
from .parallel import _merge, _program, _snapshot, member_worker_shares


def _mapping(value):
    return MappingProxyType(value)


def dumps(value):
    """Private process transport; preserve frozen mappings without global reducers."""
    buffer = io.BytesIO()
    class TransportPickler(pickle.Pickler):
        def persistent_id(self, item):
            from .windows import _SELECTION_TOKEN
            return 'selected-window' if item is _SELECTION_TOKEN else None

    pickler = TransportPickler(buffer, protocol=pickle.HIGHEST_PROTOCOL)
    pickler.dispatch_table = {MappingProxyType: lambda value: (_mapping, (dict(value),))}
    pickler.dump(value)
    return buffer.getvalue()


def loads(payload):
    """Restore in-process capabilities and object-identity roster bindings."""
    from .archive import ArchiveHandle
    from .windows import _SELECTION_TOKEN

    class TransportUnpickler(pickle.Unpickler):
        def persistent_load(self, identity):
            if identity != 'selected-window':
                raise pickle.UnpicklingError('unknown pack transport identity')
            return _SELECTION_TOKEN

    reader = TransportUnpickler(io.BytesIO(payload))
    value = reader.load()
    for item in reader.memo.copy().values():
        if isinstance(item, ArchiveHandle) and '_rebuilt_roster_bindings' in item.__dict__:
            item._rebuilt_roster_bindings = {id(roster): roster
                                           for roster in item._rebuilt_roster_bindings.values()}
    return value


@dataclass(frozen=True)
class PackTask:
    function: str
    payload: bytes
    workers: int
    session: bool
    physics: dict
    vdl: dict
    timing: bool


def run_pack(task):
    from joulewise.whole_window import shared_instrument_calibration_physics_cache

    physics, memos = _snapshot(task.physics), {}
    before = members.seed_memos(memos, task.vdl)
    session = V2AuthenticationReadSession() if task.session else None
    out, err = io.StringIO(), io.StringIO()
    ok, value = False, None
    with shared_instrument_calibration_physics_cache(physics), arc.analysis_run_caches(
            physics, memos=memos, workers=task.workers,
            vdl_mode=task.vdl.get('mode'), vdl_commit=task.vdl.get('commit'),
            vdl_entries=task.vdl.get('entries')) as caches, observe_wall_deadline() as deadline, \
            phase_timing.task_cost(task.timing) as cost:
        caches.deadline = deadline
        try:
            from joulewise.analysis_verified_store import enter_program_scope
            with session if session is not None else nullcontext(), \
                    enter_program_scope(), redirect_stdout(out), redirect_stderr(err):
                args, kwargs = loads(task.payload)
                value = dumps((_program(task.function)(*args, **kwargs), out.getvalue(), err.getvalue()))
                ok = True
        except BaseException:  # The serial call decides the failure, including its partial reads.
            value = None
        firings = None if deadline is None or caches.worker_observer_unavailable else deadline.firings
        delta = members.export_new(caches, task.vdl, before)
    records = () if session is None else tuple(
        (r.normalized_path, r.sha256, r.grammar, r.read_count) for r in session.records.values())
    return members.MemberOutcome(ok, value, records, firings, physics, vdl_new=delta, cost=cost)


def pack_map(function, calls):
    """Compute ahead; never account an unconsumed pack. None keeps the serial path."""
    from concurrent.futures import ProcessPoolExecutor

    caches = arc.current()
    if caches is None or caches.workers < 2 or len(calls) < 2 or members.fill_active():
        return None
    reference = function.__module__ + ':' + function.__qualname__
    if '<' in reference or _program(reference) is not function:
        return None
    context = members.vdl_context(caches)
    if context and context.get('entries') is None:
        context = members.vdl_context(caches, caches.vdl.export_entries())
    shares = member_worker_shares(caches.workers, len(calls))
    tasks = [PackTask(reference, dumps(call), share, active_v2_authentication_session() is not None,
                      _snapshot(caches.physics_store or {}), context, phase_timing.enabled())
             for call, share in zip(calls, shares)]
    with ProcessPoolExecutor(max_workers=min(caches.workers, len(tasks)),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        futures = [pool.submit(run_pack, task) for task in tasks]
        outcomes = []
        for future in futures:
            try:
                outcome = future.result()
            except Exception:
                outcome = members.MemberOutcome(False, None, (), 0, {})
            members.merge_side_channel(caches, outcome.vdl_new)
            outcomes.append(outcome)
    return outcomes


def consume(outcome, compute):
    """Use a successful worker result, or execute the original call serially."""
    import sys

    if outcome is None or not outcome.ok:
        return members.consume(outcome, compute, account=True)
    value, out, err = loads(members.consume(outcome, lambda: None, account=True))
    sys.stdout.write(out)
    sys.stderr.write(err)
    return value


def bracket_pack(archive, repo_root):
    from .bracket import evaluate_window_bracket

    result = evaluate_window_bracket(archive, repo_root=repo_root)
    return result, archive.census()


def merge_census(archive, rows):
    from .windows import AnalysisRefusal

    for row in rows:
        if row.path in archive._census and archive._census[row.path] != row:
            raise AnalysisRefusal('archive_input_changed')
        archive._census[row.path] = row
