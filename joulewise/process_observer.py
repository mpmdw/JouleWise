"""Spawn/wait observation and bounded process journals for live drivers."""
from __future__ import annotations
import json
import stat
import uuid
import os
import subprocess
import time
import queue
import threading
from contextvars import ContextVar
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping, Sequence


_PROCESS_JOURNAL = ContextVar("rehearsal_process_journal", default=None)


PROCESS_EVENT_SCHEMA = "joulewise.t0_rehearsal_process_event.v1"


def append_observation(path: Path, value: Mapping[str, Any]) -> None:
    from joulewise.calibration_ledger import canonical_json_bytes
    payload = canonical_json_bytes(value) + b"\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    try:
        if os.write(descriptor, payload) != len(payload):
            raise OSError("short observation write")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class _ProcessJournal:
    """A capped queue keeps custody I/O off the process supervision seams."""
    def __init__(self, path, *, observe_only=False):
        self.path = Path(path)
        self.observe_only = observe_only
        self.journal_id = str(uuid.uuid4())
        self.pending = queue.Queue(maxsize=1024)
        self.count = 0
        self.error = None
        self.writer = threading.Thread(target=self._write, daemon=True,
                                       name="rehearsal-process-journal")
        self.writer.start()

    def _write(self):
        try:
            while True:
                value = self.pending.get()
                if value is None:
                    append_observation(self.path, {
                        "schema_version": PROCESS_EVENT_SCHEMA, "event": "seal",
                        "journal_id": self.journal_id, "record_count": self.count})
                    return
                append_observation(self.path, value)
                self.count += 1
        except Exception as exc:
            self.error = str(exc)

    def emit(self, value):
        value = dict(value, journal_id=self.journal_id)
        try:
            self.pending.put_nowait(value)
        except queue.Full:
            # Retain control of the child even if its observation was lost.
            # This context can never seal successfully after overflow.
            self.error = "process observation queue overflow"

    def close(self):
        try:
            self.pending.put_nowait(None)
        except queue.Full:
            self.error = "process observation queue overflow"
        self.writer.join(timeout=2)
        if self.writer.is_alive() or self.error is not None:
            if not self.observe_only:
                raise ValueError("process observation journal incomplete: " + (self.error or "drain timed out"))
            # Missing seal is itself fail-closed evidence even if this write fails.
            try:
                append_observation(self.path.with_name("producer-faults.jsonl"), {
                    "schema_version": "joulewise.v5_qualification_producer_fault.v1",
                    "producer": "process_journal", "status": "REFUSED"})
            except Exception:
                pass


@contextmanager
def process_journal(path: Path, *, observe_only=False):
    journal = _ProcessJournal(path, observe_only=observe_only)
    token = _PROCESS_JOURNAL.set(journal)
    try:
        yield journal
    finally:
        _PROCESS_JOURNAL.reset(token)
        journal.close()


class ObservedProcess(subprocess.Popen):
    """Popen with retained DEVNULL descriptor custody and observed reaping.

    fd0 is identified from the actual descriptor supplied to Popen, rather
    than inferred later from argv. A non-DEVNULL launch is retained as such.
    """
    def __init__(self, args, **kwargs):
        self._journal = _PROCESS_JOURNAL.get()
        self._exit_recorded = False
        self._timed_out = False
        self._command = list(args) if not isinstance(args, str) else [args]
        self._spawned_ns = time.monotonic_ns()
        self._fd0 = "unobserved"
        descriptor = None
        if self._journal is not None and kwargs.get("stdin") == subprocess.DEVNULL:
            try:
                descriptor = os.open(os.devnull, os.O_RDONLY)
                actual, expected = os.fstat(descriptor), os.stat(os.devnull)
                if (stat.S_ISCHR(actual.st_mode) and
                        (actual.st_dev, actual.st_ino, actual.st_rdev) ==
                        (expected.st_dev, expected.st_ino, expected.st_rdev)):
                    self._fd0 = "/dev/null"
                kwargs["stdin"] = descriptor
            except BaseException:
                if not self._journal.observe_only:
                    raise
                self._journal.error = "fd0 observation fault"
        try:
            super().__init__(args, **kwargs)
        finally:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except BaseException:
                    if not self._journal.observe_only:
                        raise
                    self._journal.error = "fd0 observation close fault"
        self._event("spawn", None)

    def _event(self, event, exit_code):
        if self._journal is not None:
            try:
                value = {
                    "schema_version": PROCESS_EVENT_SCHEMA, "event": event,
                    "pid": self.pid, "argv": self._command,
                    "stdin_fd0_target": self._fd0, "exit_code": exit_code,
                    "timed_out": self._timed_out,
                    "monotonic_ns": time.monotonic_ns(),
                    "spawned_monotonic_ns": self._spawned_ns,
                }
                self._journal.emit(value)
            except BaseException:
                if not self._journal.observe_only:
                    raise
                self._journal.error = "process event producer fault"

    def communicate(self, *args, **kwargs):
        stdout, stderr = super().communicate(*args, **kwargs)
        self.observe_output(stdout)
        return stdout, stderr

    def observe_output(self, stdout):
        if self._journal is not None and self._command[:1] == ["/usr/bin/pgrep"]:
            try:
                self._journal.emit({"schema_version": PROCESS_EVENT_SCHEMA,
                    "event": "output", "pid": self.pid, "argv": self._command,
                    "spawned_monotonic_ns": self._spawned_ns,
                    "stdout": stdout.decode("utf-8", errors="replace") if isinstance(stdout, bytes) else stdout})
            except BaseException:
                if not self._journal.observe_only:
                    raise
                self._journal.error = "process output producer fault"

    def _observe_exit(self, code):
        if code is not None and not self._exit_recorded:
            self._event("exit", code)
            self._exit_recorded = True
        return code

    def wait(self, *args, **kwargs):
        return self._observe_exit(super().wait(*args, **kwargs))

    def poll(self):
        return self._observe_exit(super().poll())


def observed_process_type():
    return subprocess.Popen if _PROCESS_JOURNAL.get() is None else ObservedProcess


def observed_popen(args, **kwargs):
    if _PROCESS_JOURNAL.get() is None:
        return subprocess.Popen(args, **kwargs)
    kwargs.setdefault("stdin", subprocess.DEVNULL)
    return ObservedProcess(args, **kwargs)


def observed_run(args, **kwargs):
    """subprocess.run semantics with the same spawn/reap journal seam."""
    if _PROCESS_JOURNAL.get() is None:
        return subprocess.run(args, **kwargs)
    input = kwargs.pop("input", None)
    capture_output = kwargs.pop("capture_output", False)
    timeout = kwargs.pop("timeout", None)
    check = kwargs.pop("check", False)
    if input is not None:
        if "stdin" in kwargs:
            raise ValueError("stdin and input arguments may not both be used")
        kwargs["stdin"] = subprocess.PIPE
    if capture_output:
        if "stdout" in kwargs or "stderr" in kwargs:
            raise ValueError("stdout/stderr with capture_output")
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if input is None:
        kwargs.setdefault("stdin", subprocess.DEVNULL)
    with ObservedProcess(args, **kwargs) as process:
        process._timed_out = False
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            process._timed_out = True
            process.kill()
            process.communicate()
            raise
        code = process.wait()
        if check and code:
            raise subprocess.CalledProcessError(code, args, output=stdout, stderr=stderr)
        return subprocess.CompletedProcess(args, code, stdout, stderr)
