"""Boundary observations only. Ledger construction belongs to the offline reader.

Writers receive an already-open journal's append callback. They never open a
file, flush, fsync, launch a process or start a thread. The owner retains its
existing durability boundaries. Missing ends (including process death) stay
missing; an emission error is reported on stderr, never an admission decision.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import os
import subprocess
import sys
import threading
import time

SCHEMA = "joulewise.timing_boundary.v1"
_current = ContextVar("timing_receipt_writer", default=None)
_parent = ContextVar("timing_receipt_parent", default=None)


def paired_stamp():
    before = time.monotonic_ns()
    epoch = time.time_ns()
    after = time.monotonic_ns()
    return dict(epoch_ns=epoch, monotonic_before_ns=before, monotonic_after_ns=after)


def clock_stamp(clock):
    """Use the controller's injected clock, including the synthetic clock seam."""
    stamp = clock.stamp()
    return dict(epoch_ns=round(stamp.epoch_s * 1e9),
                monotonic_before_ns=round(stamp.monotonic_before_s * 1e9),
                monotonic_after_ns=round(stamp.monotonic_after_s * 1e9))


class Writer:
    def __init__(self, append, *, producer, plan_id=None, member=None, attempt=None,
                 boot_session_id=None, stamp=paired_stamp, clock_domain="host-monotonic",
                 wall_resolution_s=None, monotonic_resolution_s=None):
        self.append, self.stamp = append, stamp
        self._lock = threading.RLock()
        self.sequence = 0
        self.identity = dict(producer=producer, plan_id=plan_id, member=member, attempt=attempt,
                             boot_session_id=boot_session_id, clock_domain=clock_domain,
                             producer_id=f"{producer}:{os.getpid()}:{stamp()['monotonic_before_ns']}",
                             wall_resolution_s=(time.get_clock_info("time").resolution
                                                if wall_resolution_s is None else wall_resolution_s),
                             monotonic_resolution_s=(time.get_clock_info("monotonic").resolution
                                                     if monotonic_resolution_s is None else monotonic_resolution_s))
        self.failed = False

    def emit(self, event, span_id, phase, activity, *, parent_span_id=None, status=None,
             rc=None, requested_s=None, stamp=None, stage=None):
        with self._lock:
            try:
                return self._emit(event, span_id, phase, activity, parent_span_id=parent_span_id,
                                  status=status, rc=rc, requested_s=requested_s, stamp=stamp, stage=stage)
            except Exception as error:  # includes failed clock reads/encoding
                self.failed = True
                sys.stderr.write(f"timing receipt missing: {type(error).__name__}: {error}\n")
                return None

    def _emit(self, event, span_id, phase, activity, *, parent_span_id=None, status=None,
              rc=None, requested_s=None, stamp=None, stage=None):
        self.sequence += 1
        row = dict(schema=SCHEMA, kind="timing_boundary", **self.identity, sequence=self.sequence, event=event,
                   span_id=span_id, parent_span_id=parent_span_id, phase=phase,
                   activity=activity, stage=stage, **(stamp or self.stamp()))
        if event == "end":
            row.update(status=status, rc=rc)
        if requested_s is not None:
            row["requested_s"] = requested_s
        self.append(row)
        return row


@contextmanager
def bind(writer, *, parent_span_id=None):
    token = _current.set(writer)
    parent = _parent.set(parent_span_id)
    try:
        yield writer
    finally:
        _parent.reset(parent)
        _current.reset(token)


def worker_target(operation):
    """Carry only receipt identity into an owner's already-existing worker.

    Copying the caller's entire context could enable unrelated observation
    writers in the child and change capture artifacts beyond these markers.
    """
    writer, parent = _current.get(), _parent.get()
    @wraps(operation)
    def run():
        with bind(writer, parent_span_id=parent):
            return operation()
    return run


class Span:
    def __init__(self):
        self.status, self.rc = "complete", None


@contextmanager
def span(phase, activity, *, requested_s=None, stage=None):
    writer = _current.get()
    result = Span()
    if writer is None:
        yield result
        return
    parent = _parent.get()
    with writer._lock:
        identity = f"{writer.identity['producer_id']}:{writer.sequence + 1}"
        writer.emit("start", identity, phase, activity, parent_span_id=parent,
                    requested_s=requested_s, stage=stage)
    token = _parent.set(identity)
    try:
        yield result
    except BaseException as error:
        result.status = ("interrupted" if isinstance(error, (KeyboardInterrupt, SystemExit)) else
                         "timeout" if isinstance(error, (TimeoutError, subprocess.TimeoutExpired)) else
                         "refused" if type(error).__name__.endswith(("Refusal", "Refused")) else "error")
        result.rc = getattr(error, "returncode", None)
        raise
    finally:
        _parent.reset(token)
        writer.emit("end", identity, phase, activity, parent_span_id=parent,
                    status=result.status, rc=result.rc, stage=stage)


def timed(phase, activity, *, outcome=None):
    """Bracket an existing operation; optional receipt scope is owned by its caller."""
    def decorate(operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            with span(phase, activity) as receipt:
                result = operation(*args, **kwargs)
                if getattr(result, "go", None) is False or (
                        isinstance(result, dict) and result.get("go") is False):
                    receipt.status = "refused"
                if type(result) is int:
                    receipt.rc = result
                if outcome is not None:
                    receipt.status = outcome(result)
                return result
        return wrapped
    return decorate


def bound(writer_for):
    """Bind a pre-opened owner's writer without changing its operation's result."""
    def decorate(operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            with bind(writer_for(*args, **kwargs)):
                return operation(*args, **kwargs)
        return wrapped
    return decorate


def project(rows):
    """OFFLINE ONLY: project completed pairs to the dc684b308 reader's --span shape.

    Accept plain journal rows or events.jsonl's metadata envelope. Return timed
    documents and explicit diagnostics. Open/broken pairs never invent elapsed
    time. Wall/monotonic disagreement is left for the pinned reader to report.
    """
    opened, documents, warnings, seen = {}, [], [], set()
    phases = {"arm", "dwell", "idle", "scaffold", "decode", "gates", "holds",
              "references", "finalize", "offload"}
    identity_keys = ("producer_id", "plan_id", "member", "attempt", "boot_session_id", "clock_domain",
                     "phase", "activity", "parent_span_id", "stage")
    for row in rows:
        if not isinstance(row, dict):
            warnings.append("malformed journal row")
            continue
        row = row.get("metadata", row)
        if not isinstance(row, dict):
            warnings.append("malformed boundary envelope")
            continue
        if row.get("schema") != SCHEMA:
            continue
        key = (row.get("producer_id"), row.get("span_id"))
        locator = f"{key[0]}/{key[1]}"
        valid = (all(type(row.get(k)) is int for k in
                     ("epoch_ns", "monotonic_before_ns", "monotonic_after_ns", "sequence"))
                 and row["monotonic_before_ns"] <= row["monotonic_after_ns"]
                 and row.get("phase") in phases and all(isinstance(v, str) and v for v in key))
        if not valid:
            warnings.append(locator + ": malformed boundary")
            continue
        if row.get("event") == "start":
            if key in seen:
                warnings.append(locator + ": duplicate start")
                opened.pop(key, None)
                continue
            seen.add(key)
            opened[key] = row
        elif row.get("event") == "end":
            start = opened.pop(key, None)
            if start is None:
                warnings.append(locator + ": end without start")
                continue
            if (any(start.get(k) != row.get(k) for k in identity_keys)
                    or row["sequence"] <= start["sequence"]
                    or row["monotonic_before_ns"] < start["monotonic_before_ns"]
                    or row["epoch_ns"] < start["epoch_ns"]
                    or row.get("status") not in ("complete", "refused", "timeout", "interrupted", "error")):
                warnings.append(locator + ": mismatched/reversed pair")
                continue
            documents.append(dict(phase=row["phase"], activity=row["activity"],
                                  started_ns=start["epoch_ns"], ended_ns=row["epoch_ns"],
                                  started_monotonic_ns=start["monotonic_before_ns"],
                                  ended_monotonic_ns=row["monotonic_before_ns"],
                                  start_boundary=start, end_boundary=row))
        else:
            warnings.append(locator + ": unknown event")
    warnings.extend(f"{key}: open span (end unavailable)" for key in opened)
    documents.sort(key=lambda row: (row["started_ns"], row["ended_ns"]))
    return documents, warnings


def reader_projection(documents):
    """OFFLINE ONLY: refine parent envelopes before passing --span to the reader.

    Its generic --span records have equal priority. Partition at *observed*
    boundaries here so nested arm/dwell or publication/push envelopes never
    double count or create equal-priority conflicts. Unrelated overlapping
    operations remain explicitly unattributed; they are not ordered by guess.
    """
    by_id = {d['start_boundary']['span_id']: d for d in documents}
    points = sorted({d[k] for d in documents for k in ('started_ns', 'ended_ns')})
    result, warnings = [], []

    def descends(child, ancestor):
        parent = child['start_boundary']['parent_span_id']
        seen = set()
        while parent is not None and parent not in seen:
            if parent == ancestor['start_boundary']['span_id']:
                return True
            seen.add(parent)
            parent = by_id.get(parent, {}).get('start_boundary', {}).get('parent_span_id')
        return False

    for a, b in zip(points, points[1:]):
        active = [d for d in documents if d['started_ns'] <= a and d['ended_ns'] >= b]
        if not active:
            continue
        leaves = [d for d in active if not any(descends(other, d) for other in active if other is not d)]
        if len(leaves) != 1:
            warnings.append(f"unrelated overlapping spans: {a}..{b}")
            result.append(dict(phase='unattributed', started_ns=a, ended_ns=b))
            continue
        owner = leaves[0]
        # Endpoints come from emitted boundaries, with their original clock
        # brackets retained. Do not fabricate a monotonic stamp for a wall cut.
        result.append(dict(phase=owner['phase'], activity=owner['activity'],
                           started_ns=a, ended_ns=b,
                           source_span_id=owner['start_boundary']['span_id']))
    return result, warnings
