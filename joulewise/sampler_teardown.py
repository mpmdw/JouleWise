"""Parent-owned sampler process adoption, teardown, and custody evidence.

The telemetry adapter remains responsible for deciding *when* its sampler is
ready to stop.  The controller wraps the adapter's existing ``Popen`` call so
this module can adopt the returned child immediately, then a transparent
proxy routes the adapter's existing stop calls through the custodian.

D-139 A1 registered limitation (F1): parent-side adoption has an unavoidable
startup race.  A child forked before ``setpgid(child, child)`` remains in the
controller's process group, while a descendant can later escape with
``setsid``.  The bounded group census and report-only wide argv census are the
detection net.  The wide census never grants signaling authority.
"""

from __future__ import annotations

import errno
import ctypes
import ctypes.util
import os
import signal
import struct
import subprocess
import sys
import time
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from typing import Any


PROCESS_TERM_GRACE_S = 10.0
PROCESS_CENSUS_TIMEOUT_S = 1.0
PROCESS_CENSUS_POLL_S = 0.05


def _argv(value: object) -> list[str]:
    if isinstance(value, str | bytes | os.PathLike):
        return [os.fsdecode(value)]
    if isinstance(value, Sequence):
        return [os.fsdecode(item) for item in value]
    return [str(value)]


class _CustodiedProcess:
    """Transparent ``Popen`` proxy that preserves the adapter lifecycle."""

    def __init__(self, process: Any, custodian: SamplerTeardown) -> None:
        self._process = process
        self._custodian = custodian

    def __getattr__(self, name: str) -> Any:
        return getattr(self._process, name)

    def __enter__(self) -> _CustodiedProcess:
        self._process.__enter__()
        return self

    def __exit__(self, *args: Any) -> Any:
        return self._process.__exit__(*args)

    def poll(self) -> int | None:
        return self._process.poll()

    def terminate(self) -> None:
        self._custodian.teardown(self._process)

    def kill(self) -> None:
        # The adapter may call kill after its own communicate timeout.  A
        # completed custody teardown already killed/reaped as needed; an
        # incomplete one gets one fail-closed emergency attempt.
        if self._custodian.report is None:
            self._custodian.teardown(self._process)
        elif getattr(self._process, "returncode", None) is None:
            self._custodian.emergency_kill(self._process)

    def communicate(self, *args: Any, **kwargs: Any) -> Any:
        return self._process.communicate(*args, **kwargs)

    def wait(self, *args: Any, **kwargs: Any) -> Any:
        return self._process.wait(*args, **kwargs)


class SamplerTeardown:
    """Own one sampler child's process-group custody and final report."""

    def __init__(
        self,
        *,
        termination_grace_s: float = PROCESS_TERM_GRACE_S,
        census_timeout_s: float = PROCESS_CENSUS_TIMEOUT_S,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.termination_grace_s = termination_grace_s
        self.census_timeout_s = census_timeout_s
        self._monotonic = monotonic
        self._sleep = sleep
        self._process: Any | None = None
        self._spawn_argv: list[str] = []
        self._sampler_argv: list[str] = []
        self._direct_child_pid: int | None = None
        self._process_group_id: int | None = None
        self._isolation_mode = "not_spawned"
        self._adoption_errors: list[str] = []
        self._adoption_exception_class: str | None = None
        self.report: dict[str, Any] | None = None

    @property
    def spawned(self) -> bool:
        return self._process is not None

    @contextmanager
    def intercept_popen(self) -> Iterator[None]:
        """Adopt the first ``Popen`` made by the wrapped adapter start call.

        The wrapper restores the original constructor *before* it spawns, so
        helper subprocesses and teardown censuses cannot be captured.  This is
        intentionally a single-operator, single-sampler seam under D-139 A1.
        """

        original_popen = subprocess.Popen
        captured = False

        def parent_popen(*args: Any, **kwargs: Any) -> _CustodiedProcess:
            nonlocal captured
            command = args[0] if args else kwargs.get("args", [])
            command_argv = _argv(command)
            capture_this = not captured and self._is_sampler_spawn(command_argv)
            if capture_this:
                captured = True
                if subprocess.Popen is parent_popen:
                    subprocess.Popen = original_popen
            process = original_popen(*args, **kwargs)
            if capture_this and self._process is None:
                # Synthetic pipelines commonly return a Popen-shaped object
                # with no OS pid.  Such an object was never available for
                # process custody, even when its argv resembles powermetrics.
                if getattr(process, "pid", None) is None:
                    return process
                self._adopt(process, command_argv)
                return _CustodiedProcess(process, self)
            return process

        subprocess.Popen = parent_popen
        try:
            yield
        finally:
            if subprocess.Popen is parent_popen:
                subprocess.Popen = original_popen

    @staticmethod
    def _is_sampler_spawn(command: list[str]) -> bool:
        """Distinguish the continuous sampler from bounded capability probes."""

        sampler_command = SamplerTeardown._sampler_command(command)
        return "-o" in sampler_command and "-n" not in sampler_command

    def _adopt(self, process: Any, command: list[str]) -> None:
        self._process = process
        self._spawn_argv = list(command)
        self._sampler_argv = self._sampler_command(command)
        self._direct_child_pid = int(process.pid)
        try:
            os.setpgid(self._direct_child_pid, self._direct_child_pid)
        except OSError as exc:
            self._isolation_mode = "none_direct_child"
            self._process_group_id = None
            self._adoption_errors.append(
                f"setpgid({self._direct_child_pid}, {self._direct_child_pid}) "
                f"failed: {type(exc).__name__}: {exc}"
            )
            if exc.errno not in {errno.EACCES, errno.EPERM, errno.ESRCH}:
                # The process still receives direct-child cleanup, but custody
                # cannot be certified clean after an unexpected adoption error.
                self._adoption_errors.append("unexpected_adoption_error")
                self._adoption_exception_class = type(exc).__name__
        else:
            self._isolation_mode = "isolated_group"
            self._process_group_id = self._direct_child_pid

    def teardown(self, process: Any | None = None) -> dict[str, Any]:
        if self.report is not None:
            return self.report
        selected = process if process is not None else self._process
        report = self._new_report()
        if selected is None:
            report["status"] = "not_engaged"
            self.report = report
            return report
        try:
            self._signal_term(selected, report)
            if self._target_live(selected):
                report["kill_escalated"] = True
                self._signal_kill(selected, report)
            # F4: every permitted signal is issued above while the leader is
            # un-reaped.  Reaping is deliberately the final mutating action.
            self._reap_leader(selected, report)
            group_survivors = self._bounded_group_census()
            escaped = self._wide_argv_census(
                self._sampler_argv,
                process_group_id=self._process_group_id,
            )
            report["group_survivors"] = group_survivors
            report["escaped_candidates"] = escaped
            report["census_completed"] = True
            report["survivors_detected"] = bool(group_survivors or escaped)
            report["status"] = (
                "contaminated" if report["survivors_detected"] else "clean"
            )
            if "unexpected_adoption_error" in self._adoption_errors:
                report["status"] = "contamination_unknown"
        except BaseException as exc:  # F2: custody is fail-closed on every exception.
            report["status"] = "contamination_unknown"
            report["exception_class"] = type(exc).__name__
            report["errors"].append(f"{type(exc).__name__}: {exc}")
            self._emergency_cleanup(selected, report)
            self.report = report
            if not isinstance(exc, Exception):
                raise
        self.report = report
        return report

    @staticmethod
    def _sampler_command(command: list[str]) -> list[str]:
        """Remove the supported sudo launcher prefix for exact argv census."""

        if command and os.path.basename(command[0]) == "sudo":
            cursor = 1
            while cursor < len(command) and command[cursor].startswith("-"):
                cursor += 1
            return command[cursor:]
        return list(command)

    def emergency_kill(self, process: Any) -> None:
        report = self.report if self.report is not None else self._new_report()
        self._emergency_cleanup(process, report)
        report["status"] = "contamination_unknown"
        self.report = report

    def _new_report(self) -> dict[str, Any]:
        return {
            "status": "contamination_unknown",
            "spawn_observed": self.spawned,
            "isolation_mode": self._isolation_mode,
            "direct_child_pid": self._direct_child_pid,
            "process_group_id": self._process_group_id,
            "spawn_argv": list(self._spawn_argv),
            "sampler_argv": list(self._sampler_argv),
            "termination_signal": "SIGTERM",
            "termination_grace_s": self.termination_grace_s,
            "kill_escalated": False,
            "census_method": "bounded_process_group_plus_report_only_exact_argv",
            "census_timeout_s": self.census_timeout_s,
            "census_completed": False,
            "survivors_detected": False,
            "group_survivors": [],
            "escaped_candidates": [],
            "signal_attempts": [],
            "leader_reaped": getattr(self._process, "returncode", None) is not None,
            "exception_class": self._adoption_exception_class,
            "errors": list(self._adoption_errors),
        }

    @staticmethod
    def _leader_unreaped(process: Any) -> bool:
        return getattr(process, "returncode", None) is None

    def _record_signal(
        self, report: dict[str, Any], sig: signal.Signals, target: str, outcome: str
    ) -> None:
        report["signal_attempts"].append(
            {"signal": sig.name, "target": target, "outcome": outcome}
        )

    def _signal_term(self, process: Any, report: dict[str, Any]) -> None:
        if self._process_group_id is not None:
            if not self._leader_unreaped(process):
                self._record_signal(
                    report, signal.SIGTERM, "process_group", "refused_leader_reaped"
                )
                report["leader_reaped"] = True
                raise RuntimeError("group signal refused after sampler leader was reaped")
            try:
                os.killpg(self._process_group_id, signal.SIGTERM)
            except ProcessLookupError:
                outcome = "target_absent"
            else:
                outcome = "sent"
            self._record_signal(report, signal.SIGTERM, "process_group", outcome)
        else:
            if not self._leader_unreaped(process):
                self._record_signal(
                    report, signal.SIGTERM, "direct_child", "refused_leader_reaped"
                )
                report["leader_reaped"] = True
                return
            process.terminate()
            self._record_signal(report, signal.SIGTERM, "direct_child", "sent")
        deadline = self._monotonic() + self.termination_grace_s
        while self._target_live(process) and self._monotonic() < deadline:
            self._sleep(min(PROCESS_CENSUS_POLL_S, max(0.0, deadline - self._monotonic())))

    def _signal_kill(self, process: Any, report: dict[str, Any]) -> None:
        if self._process_group_id is not None:
            if not self._leader_unreaped(process):
                self._record_signal(
                    report, signal.SIGKILL, "process_group", "refused_leader_reaped"
                )
                report["leader_reaped"] = True
                raise RuntimeError("group SIGKILL refused after sampler leader was reaped")
            try:
                os.killpg(self._process_group_id, signal.SIGKILL)
            except ProcessLookupError:
                outcome = "target_absent"
            else:
                outcome = "sent"
            self._record_signal(report, signal.SIGKILL, "process_group", outcome)
        else:
            if not self._leader_unreaped(process):
                self._record_signal(
                    report, signal.SIGKILL, "direct_child", "refused_leader_reaped"
                )
                report["leader_reaped"] = True
                return
            process.kill()
            self._record_signal(report, signal.SIGKILL, "direct_child", "sent")

    def _target_live(self, process: Any) -> bool:
        if self._process_group_id is not None:
            return bool(self._process_group_members(self._process_group_id))
        if getattr(process, "returncode", None) is not None:
            return False
        if all(
            hasattr(os, name)
            for name in ("waitid", "P_PID", "WEXITED", "WNOHANG", "WNOWAIT")
        ):
            try:
                exited = os.waitid(  # type: ignore[attr-defined]
                    os.P_PID,
                    int(process.pid),
                    os.WEXITED | os.WNOHANG | os.WNOWAIT,
                )
            except ChildProcessError:
                return False
            return exited is None
        try:
            os.kill(int(process.pid), 0)
        except ProcessLookupError:
            return False
        return True

    def _reap_leader(self, process: Any, report: dict[str, Any]) -> None:
        if not self._leader_unreaped(process):
            report["leader_reaped"] = True
            return
        try:
            process.wait(timeout=max(0.1, self.census_timeout_s))
        except subprocess.TimeoutExpired:
            report["errors"].append("sampler leader did not reap within census timeout")
        report["leader_reaped"] = getattr(process, "returncode", None) is not None
        if not report["leader_reaped"]:
            raise RuntimeError("sampler leader remained un-reaped after teardown")

    def _bounded_group_census(self) -> list[dict[str, Any]]:
        if self._process_group_id is None:
            return []
        deadline = self._monotonic() + self.census_timeout_s
        while True:
            members = self._process_group_members(self._process_group_id)
            if not members or self._monotonic() >= deadline:
                return members
            self._sleep(min(PROCESS_CENSUS_POLL_S, max(0.0, deadline - self._monotonic())))

    @classmethod
    def _process_group_members(cls, process_group_id: int) -> list[dict[str, Any]]:
        return [
            {"pid": row["pid"], "state": row["state"]}
            for row in cls._process_table(include_argv=False)
            if row["pgid"] == process_group_id and not row["state"].startswith("Z")
        ]

    @classmethod
    def _wide_argv_census(
        cls, sampler_argv: list[str], *, process_group_id: int | None
    ) -> list[dict[str, Any]]:
        if not sampler_argv:
            return []
        candidates: list[dict[str, Any]] = []
        for row in cls._process_table(include_argv=True):
            if row["state"].startswith("Z") or row["argv"] != sampler_argv:
                continue
            if process_group_id is not None and row["pgid"] == process_group_id:
                continue
            candidates.append({"pid": row["pid"], "argv": list(row["argv"])})
        return candidates

    @classmethod
    def _process_table(cls, *, include_argv: bool) -> list[dict[str, Any]]:
        if sys.platform == "darwin":
            return cls._darwin_process_table(include_argv=include_argv)
        return cls._procfs_process_table(include_argv=include_argv)

    @staticmethod
    def _procfs_process_table(*, include_argv: bool) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        proc = os.path.join(os.sep, "proc")
        for name in os.listdir(proc):
            if not name.isdigit():
                continue
            try:
                with open(
                    os.path.join(proc, name, "stat"), encoding="utf-8"
                ) as handle:
                    stat_raw = handle.read()
                after_name = stat_raw[stat_raw.rfind(")") + 2 :].split()
                argv: list[str] = []
                if include_argv:
                    with open(os.path.join(proc, name, "cmdline"), "rb") as handle:
                        argv = [
                            os.fsdecode(part)
                            for part in handle.read().split(b"\0")
                            if part
                        ]
                rows.append(
                    {
                        "pid": int(name),
                        "pgid": int(after_name[2]),
                        "state": after_name[0],
                        "argv": argv,
                    }
                )
            except (FileNotFoundError, PermissionError, ProcessLookupError, ValueError):
                continue
        return rows

    @classmethod
    def _darwin_process_table(cls, *, include_argv: bool) -> list[dict[str, Any]]:
        class ProcBsdInfo(ctypes.Structure):
            _fields_ = [
                ("flags", ctypes.c_uint32),
                ("status", ctypes.c_uint32),
                ("xstatus", ctypes.c_uint32),
                ("pid", ctypes.c_uint32),
                ("ppid", ctypes.c_uint32),
                ("uid", ctypes.c_uint32),
                ("gid", ctypes.c_uint32),
                ("ruid", ctypes.c_uint32),
                ("rgid", ctypes.c_uint32),
                ("svuid", ctypes.c_uint32),
                ("svgid", ctypes.c_uint32),
                ("rfu_1", ctypes.c_uint32),
                ("comm", ctypes.c_char * 16),
                ("name", ctypes.c_char * 32),
                ("nfiles", ctypes.c_uint32),
                ("pgid", ctypes.c_uint32),
                ("pjobc", ctypes.c_uint32),
                ("e_tdev", ctypes.c_uint32),
                ("e_tpgid", ctypes.c_uint32),
                ("nice", ctypes.c_int32),
                ("start_tvsec", ctypes.c_uint64),
                ("start_tvusec", ctypes.c_uint64),
            ]

        library_name = ctypes.util.find_library("proc")
        if library_name is None:
            raise OSError("Darwin libproc is unavailable")
        library = ctypes.CDLL(library_name, use_errno=True)
        library.proc_listpids.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_int,
        ]
        library.proc_listpids.restype = ctypes.c_int
        library.proc_pidinfo.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint64,
            ctypes.c_void_p,
            ctypes.c_int,
        ]
        library.proc_pidinfo.restype = ctypes.c_int
        byte_count = library.proc_listpids(1, 0, None, 0)
        if byte_count <= 0:
            raise OSError(ctypes.get_errno(), "proc_listpids size query failed")
        pids = (ctypes.c_int * (byte_count // ctypes.sizeof(ctypes.c_int)))()
        filled = library.proc_listpids(1, 0, pids, ctypes.sizeof(pids))
        rows: list[dict[str, Any]] = []
        for pid in pids[: max(0, filled // ctypes.sizeof(ctypes.c_int))]:
            if pid <= 0:
                continue
            info = ProcBsdInfo()
            observed = library.proc_pidinfo(
                pid, 3, 0, ctypes.byref(info), ctypes.sizeof(info)
            )
            if observed != ctypes.sizeof(info):
                continue
            rows.append(
                {
                    "pid": int(info.pid),
                    "pgid": int(info.pgid),
                    "state": "Z" if info.status == 5 else str(info.status),
                    "argv": cls._darwin_argv(pid) if include_argv else [],
                }
            )
        return rows

    @staticmethod
    def _darwin_argv(pid: int) -> list[str]:
        library_name = ctypes.util.find_library("c")
        if library_name is None:
            return []
        library = ctypes.CDLL(library_name, use_errno=True)
        mib = (ctypes.c_int * 3)(1, 49, pid)  # CTL_KERN, KERN_PROCARGS2, pid
        size = ctypes.c_size_t(0)
        if library.sysctl(mib, 3, None, ctypes.byref(size), None, 0) != 0:
            return []
        buffer = ctypes.create_string_buffer(size.value)
        if library.sysctl(mib, 3, buffer, ctypes.byref(size), None, 0) != 0:
            return []
        raw = buffer.raw[: size.value]
        if len(raw) < struct.calcsize("i"):
            return []
        argc = struct.unpack_from("i", raw)[0]
        cursor = struct.calcsize("i")
        executable_end = raw.find(b"\0", cursor)
        if executable_end < 0:
            return []
        cursor = executable_end
        while cursor < len(raw) and raw[cursor] == 0:
            cursor += 1
        argv: list[str] = []
        for _ in range(max(0, argc)):
            end = raw.find(b"\0", cursor)
            if end < 0:
                break
            argv.append(os.fsdecode(raw[cursor:end]))
            cursor = end + 1
        return argv

    def _emergency_cleanup(self, process: Any, report: dict[str, Any]) -> None:
        if not self._leader_unreaped(process):
            report["leader_reaped"] = True
            return
        try:
            if self._process_group_id is not None:
                os.killpg(self._process_group_id, signal.SIGKILL)
                self._record_signal(
                    report, signal.SIGKILL, "process_group", "emergency_sent"
                )
            else:
                process.kill()
                self._record_signal(
                    report, signal.SIGKILL, "direct_child", "emergency_sent"
                )
            process.wait(timeout=max(0.1, self.census_timeout_s))
        except BaseException as cleanup_exc:
            report["errors"].append(
                f"emergency cleanup failed: {type(cleanup_exc).__name__}: {cleanup_exc}"
            )
        report["leader_reaped"] = getattr(process, "returncode", None) is not None
