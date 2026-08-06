"""Exact process-identity primitives for the JouleWise quiet guard.

The quiet guard never identifies a process by a name pattern.  A durable
identity binds the PID to its observed start time, executable, argument-vector
digest, and complete observed ancestry.  Callers must re-observe an identity
immediately before acting on it; a PID whose identity changed is a reused PID,
not the process named by the registry.

On Darwin the production observer obtains the sub-second process start time
from ``KERN_PROC_PID`` and the real argument vector from ``KERN_PROCARGS2``.
``/bin/ps`` is used only to obtain parent linkage and enumerate census PIDs;
display-oriented ``comm`` and ``command`` fields never define identity.  Every
row and every ancestry link is re-observed after the walk.  A disappearance,
exec, PID reuse, or reparenting at any point makes the complete observation
torn and therefore unusable.  Tests and recovery logic use injected sources
and readers and never inspect the real process table.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import ctypes
import ctypes.util
import errno
import hashlib
import struct
import subprocess
import sys
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence


PROCESS_IDENTITY_SCHEMA = "joulewise.quiet_guard.process_identity/v1"
ARGV_DIGEST_PREFIX = "sha256:"
CENSUS_SNAPSHOT_ATTEMPTS = 2


class ProcessIdentityError(ValueError):
    """A process observation or durable identity is malformed."""


class ProcessObservationError(ProcessIdentityError):
    """A listed or previously observed process cannot be observed reliably."""

    def __init__(self, detail: str, *, error_number: int | None = None) -> None:
        super().__init__(detail)
        self.error_number = error_number


def argv_digest(argv: Sequence[str] | bytes) -> str:
    """Return an unambiguous SHA-256 digest for an argv observation.

    A true vector is encoded as length-prefixed UTF-8 fields, so argument
    boundaries cannot collide.  A platform observation available only as raw
    bytes is tagged separately and hashed byte-for-byte.
    """

    digest = hashlib.sha256()
    if isinstance(argv, bytes):
        digest.update(b"raw-command\0")
        digest.update(argv)
    else:
        digest.update(b"argv-vector\0")
        for argument in argv:
            if type(argument) is not str:
                raise ProcessIdentityError("argv entries must be plain strings")
            encoded = argument.encode("utf-8", "surrogateescape")
            digest.update(len(encoded).to_bytes(8, "big"))
            digest.update(encoded)
    return ARGV_DIGEST_PREFIX + digest.hexdigest()


def _plain_nonempty(value: Any, field: str) -> str:
    if type(value) is not str or not value:
        raise ProcessIdentityError(f"{field} must be a non-empty string")
    return value


def _positive_pid(value: Any, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise ProcessIdentityError(f"{field} must be a positive integer")
    return value


def _digest(value: Any) -> str:
    value = _plain_nonempty(value, "argv_digest")
    if not value.startswith(ARGV_DIGEST_PREFIX) or len(value) != 71:
        raise ProcessIdentityError("argv_digest must be sha256:<64 lowercase hex>")
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise ProcessIdentityError("argv_digest contains non-hex characters") from exc
    if value[7:] != value[7:].lower():
        raise ProcessIdentityError("argv_digest must use lowercase hex")
    return value


@dataclass(frozen=True)
class AncestorIdentity:
    """One exact ancestor link, nearest parent first."""

    pid: int
    start_time: str
    executable: str
    argv_digest: str

    def __post_init__(self) -> None:
        _positive_pid(self.pid, "ancestor.pid")
        _plain_nonempty(self.start_time, "ancestor.start_time")
        _plain_nonempty(self.executable, "ancestor.executable")
        _digest(self.argv_digest)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "pid": self.pid,
            "start_time": self.start_time,
            "executable": self.executable,
            "argv_digest": self.argv_digest,
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "AncestorIdentity":
        if not isinstance(value, Mapping) or set(value) != {
            "pid",
            "start_time",
            "executable",
            "argv_digest",
        }:
            raise ProcessIdentityError("ancestor identity fields are invalid")
        return cls(
            pid=_positive_pid(value["pid"], "ancestor.pid"),
            start_time=_plain_nonempty(value["start_time"], "ancestor.start_time"),
            executable=_plain_nonempty(value["executable"], "ancestor.executable"),
            argv_digest=_digest(value["argv_digest"]),
        )


@dataclass(frozen=True)
class ProcessIdentity:
    """The complete exact identity used for registry and action checks."""

    pid: int
    start_time: str
    executable: str
    argv_digest: str
    ancestry: tuple[AncestorIdentity, ...] = ()

    def __post_init__(self) -> None:
        _positive_pid(self.pid, "pid")
        _plain_nonempty(self.start_time, "start_time")
        _plain_nonempty(self.executable, "executable")
        _digest(self.argv_digest)
        if not isinstance(self.ancestry, tuple) or not all(
            isinstance(item, AncestorIdentity) for item in self.ancestry
        ):
            raise ProcessIdentityError("ancestry must be an ancestor tuple")
        seen = {self.pid}
        for ancestor in self.ancestry:
            if ancestor.pid in seen:
                raise ProcessIdentityError("ancestry contains a PID cycle")
            seen.add(ancestor.pid)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": PROCESS_IDENTITY_SCHEMA,
            "pid": self.pid,
            "start_time": self.start_time,
            "executable": self.executable,
            "argv_digest": self.argv_digest,
            "ancestry": [item.to_mapping() for item in self.ancestry],
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "ProcessIdentity":
        if not isinstance(value, Mapping) or set(value) != {
            "schema",
            "pid",
            "start_time",
            "executable",
            "argv_digest",
            "ancestry",
        }:
            raise ProcessIdentityError("process identity fields are invalid")
        if value["schema"] != PROCESS_IDENTITY_SCHEMA:
            raise ProcessIdentityError("process identity schema mismatch")
        ancestry = value["ancestry"]
        if not isinstance(ancestry, list):
            raise ProcessIdentityError("process ancestry must be a list")
        return cls(
            pid=_positive_pid(value["pid"], "pid"),
            start_time=_plain_nonempty(value["start_time"], "start_time"),
            executable=_plain_nonempty(value["executable"], "executable"),
            argv_digest=_digest(value["argv_digest"]),
            ancestry=tuple(AncestorIdentity.from_mapping(item) for item in ancestry),
        )


def validate_identity_mapping(value: Any) -> ProcessIdentity:
    """Validate and normalize a durable identity mapping."""

    return ProcessIdentity.from_mapping(value)


class ProcessSource(Protocol):
    """Injectable boundary for exact observation and independent census."""

    def observe(self, pid: int) -> ProcessIdentity | None:
        """Return an identity or ``None`` only for a positively absent PID.

        Observation failures and torn reads raise ``ProcessObservationError``;
        callers must never reinterpret them as absence.
        """

        ...

    def census(self) -> tuple[ProcessIdentity, ...]:
        ...


class Revalidation(str, Enum):
    MATCH = "match"
    ABSENT = "absent"
    PID_REUSED = "pid_reused"
    UNOBSERVABLE = "unobservable"


def revalidate_identity(
    expected: ProcessIdentity,
    source: ProcessSource,
) -> tuple[Revalidation, ProcessIdentity | None]:
    """Re-observe ``expected.pid`` and classify the exact identity."""

    try:
        observed = source.observe(expected.pid)
    except ProcessObservationError:
        return Revalidation.UNOBSERVABLE, None
    if observed is None:
        return Revalidation.ABSENT, None
    if observed == expected:
        return Revalidation.MATCH, observed
    return Revalidation.PID_REUSED, observed


def independent_census(
    source: ProcessSource,
    predicate: Callable[[ProcessIdentity], bool],
) -> tuple[ProcessIdentity, ...]:
    """Return an independently observed, deterministically ordered family."""

    return tuple(sorted((row for row in source.census() if predicate(row)), key=lambda row: row.pid))


def descends_from(identity: ProcessIdentity, ancestor: ProcessIdentity) -> bool:
    """Return whether ``identity`` contains the exact ancestor identity."""

    target = AncestorIdentity(
        pid=ancestor.pid,
        start_time=ancestor.start_time,
        executable=ancestor.executable,
        argv_digest=ancestor.argv_digest,
    )
    return target in identity.ancestry


class SnapshotProcessSource:
    """Deterministic source used by tests and recovery simulations."""

    def __init__(self, identities: Iterable[ProcessIdentity] = ()) -> None:
        self._identities = {identity.pid: identity for identity in identities}

    def observe(self, pid: int) -> ProcessIdentity | None:
        return self._identities.get(pid)

    def census(self) -> tuple[ProcessIdentity, ...]:
        return tuple(self._identities[pid] for pid in sorted(self._identities))


@dataclass(frozen=True)
class DarwinProcessRecord:
    """One kernel-backed row, including linkage used for race checks."""

    pid: int
    ppid: int
    start_time: str
    executable: str
    argv: tuple[str, ...]


class DarwinProcessReader(Protocol):
    """Injectable single-row Darwin observer used beneath ProcessSource."""

    def read(self, pid: int) -> DarwinProcessRecord | None:
        ...


class _Timeval(ctypes.Structure):
    _fields_ = (("tv_sec", ctypes.c_long), ("tv_usec", ctypes.c_int))


class SysctlDarwinProcessReader:
    """Read exact Darwin process material using fixed kernel interfaces.

    ``extern_proc.p_starttime`` is the first member of ``kinfo_proc`` on
    Darwin, so decoding the leading ``struct timeval`` avoids mirroring the
    private pointer-heavy remainder of that ABI.  The value is accepted only
    when two complete observations agree.
    """

    CTL_KERN = 1
    KERN_ARGMAX = 8
    KERN_PROC = 14
    KERN_PROC_PID = 1
    KERN_PROCARGS2 = 49

    def __init__(
        self,
        runner: Callable[..., subprocess.CompletedProcess[bytes]] | None = None,
        *,
        platform_name: str | None = None,
        libc: Any | None = None,
    ) -> None:
        self._runner = runner or subprocess.run
        self._platform_name = platform_name or sys.platform
        self._libc = libc

    def _system_library(self) -> Any | None:
        if self._platform_name != "darwin":
            return None
        if self._libc is None:
            library = ctypes.util.find_library("System")
            if not library:
                return None
            self._libc = ctypes.CDLL(library, use_errno=True)
            self._libc.sysctl.argtypes = (
                ctypes.POINTER(ctypes.c_int),
                ctypes.c_uint,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_size_t),
                ctypes.c_void_p,
                ctypes.c_size_t,
            )
            self._libc.sysctl.restype = ctypes.c_int
        return self._libc

    def _sysctl(self, mib: Sequence[int], capacity: int | None = None) -> bytes:
        libc = self._system_library()
        if libc is None:
            raise ProcessObservationError("Darwin system library is unavailable")
        names = (ctypes.c_int * len(mib))(*mib)
        if capacity is None:
            size = ctypes.c_size_t(0)
            if libc.sysctl(names, len(mib), None, ctypes.byref(size), None, 0) != 0:
                raise ProcessObservationError(
                    "Darwin sysctl size query failed",
                    error_number=ctypes.get_errno(),
                )
            capacity = size.value
        if capacity < 0:
            raise ProcessObservationError("Darwin sysctl returned a negative capacity")
        if capacity == 0:
            return b""
        buffer = ctypes.create_string_buffer(capacity)
        size = ctypes.c_size_t(capacity)
        if libc.sysctl(names, len(mib), buffer, ctypes.byref(size), None, 0) != 0:
            raise ProcessObservationError(
                "Darwin sysctl payload query failed",
                error_number=ctypes.get_errno(),
            )
        return bytes(buffer.raw[: size.value])

    def _argmax(self) -> int:
        payload = self._sysctl((self.CTL_KERN, self.KERN_ARGMAX))
        if len(payload) < ctypes.sizeof(ctypes.c_int):
            raise ProcessObservationError("KERN_ARGMAX payload is malformed")
        value = struct.unpack_from("=i", payload)[0]
        if not 0 < value <= 16 * 1024 * 1024:
            raise ProcessObservationError("KERN_ARGMAX value is invalid")
        return value

    def _start_time(self, pid: int) -> str | None:
        try:
            payload = self._sysctl(
                (self.CTL_KERN, self.KERN_PROC, self.KERN_PROC_PID, pid)
            )
        except ProcessObservationError as exc:
            if exc.error_number == errno.ESRCH:
                return None
            raise
        if not payload:
            return None
        if len(payload) < ctypes.sizeof(_Timeval):
            raise ProcessObservationError("KERN_PROC_PID payload is malformed")
        value = _Timeval.from_buffer_copy(payload)
        if value.tv_sec <= 0 or not 0 <= value.tv_usec < 1_000_000:
            raise ProcessObservationError("KERN_PROC_PID start time is invalid")
        return f"{value.tv_sec}.{value.tv_usec:06d}"

    def _procargs(self, pid: int) -> tuple[str, tuple[str, ...]] | None:
        capacity = self._argmax()
        payload = self._sysctl((self.CTL_KERN, self.KERN_PROCARGS2, pid), capacity)
        if len(payload) < ctypes.sizeof(ctypes.c_int):
            raise ProcessObservationError("KERN_PROCARGS2 payload is malformed")
        argc = struct.unpack_from("=i", payload)[0]
        if argc <= 0 or argc > 1_000_000:
            raise ProcessObservationError("KERN_PROCARGS2 argc is invalid")
        cursor = ctypes.sizeof(ctypes.c_int)
        executable_end = payload.find(b"\0", cursor)
        if executable_end <= cursor:
            raise ProcessObservationError("KERN_PROCARGS2 executable is missing")
        executable = payload[cursor:executable_end].decode("utf-8", "surrogateescape")
        cursor = executable_end + 1
        while cursor < len(payload) and payload[cursor] == 0:
            cursor += 1
        arguments: list[str] = []
        for _ in range(argc):
            end = payload.find(b"\0", cursor)
            if end < cursor:
                raise ProcessObservationError("KERN_PROCARGS2 argv is truncated")
            arguments.append(payload[cursor:end].decode("utf-8", "surrogateescape"))
            cursor = end + 1
        if not arguments:
            raise ProcessObservationError("KERN_PROCARGS2 argv is empty")
        return executable, tuple(arguments)

    def _parent(self, pid: int) -> int | None:
        result = self._runner(
            ("/bin/ps", "-p", str(pid), "-o", "pid=,ppid="),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise ProcessObservationError("parent linkage query failed")
        parts = bytes(result.stdout).split()
        if len(parts) != 2:
            raise ProcessObservationError("parent linkage payload is malformed")
        try:
            observed_pid, ppid = (int(part) for part in parts)
        except ValueError:
            raise ProcessObservationError("parent linkage is not numeric")
        if observed_pid != pid or ppid < 0:
            raise ProcessObservationError("parent linkage does not match the requested PID")
        return ppid

    def _read_once(self, pid: int) -> DarwinProcessRecord | None:
        start_time = self._start_time(pid)
        if start_time is None:
            return None
        procargs = self._procargs(pid)
        ppid = self._parent(pid)
        executable, argv = procargs
        return DarwinProcessRecord(pid, ppid, start_time, executable, argv)

    def read(self, pid: int) -> DarwinProcessRecord | None:
        if type(pid) is not int or pid <= 0:
            raise ProcessObservationError("PID must be a positive integer")
        if self._platform_name != "darwin":
            raise ProcessObservationError("Darwin process observation is unavailable")
        first = self._read_once(pid)
        if first is None:
            return None
        second = self._read_once(pid)
        if second is None or first != second:
            raise ProcessObservationError("process changed during kernel observation")
        return first


class PsProcessSource:
    """Fail-closed Darwin source with an ancestry-spanning race check."""

    def __init__(
        self,
        runner: Callable[..., subprocess.CompletedProcess[bytes]] | None = None,
        *,
        reader: DarwinProcessReader | None = None,
    ) -> None:
        self._runner = runner or subprocess.run
        self._reader = reader or SysctlDarwinProcessReader(self._runner)

    def _run(self, arguments: Sequence[str]) -> bytes:
        result = self._runner(
            list(arguments),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            return b""
        return bytes(result.stdout)

    @staticmethod
    def _ancestor(row: DarwinProcessRecord) -> AncestorIdentity:
        return AncestorIdentity(row.pid, row.start_time, row.executable, argv_digest(row.argv))

    def observe(self, pid: int) -> ProcessIdentity | None:
        if type(pid) is not int or pid <= 0:
            return None
        row = self._reader.read(pid)
        if row is None:
            return None
        observed_rows = [row]
        ancestry: list[AncestorIdentity] = []
        seen = {pid}
        parent_pid = row.ppid
        while parent_pid > 0:
            if parent_pid in seen:
                raise ProcessObservationError("process ancestry contains a cycle")
            seen.add(parent_pid)
            parent = self._reader.read(parent_pid)
            if parent is None:
                raise ProcessObservationError("ancestor disappeared during observation")
            observed_rows.append(parent)
            ancestry.append(self._ancestor(parent))
            parent_pid = parent.ppid
        # The observation is useful only if the child and every ancestry link
        # still have precisely the same start, argv, executable, and parent.
        for original in observed_rows:
            if self._reader.read(original.pid) != original:
                raise ProcessObservationError("process ancestry changed during observation")
        return ProcessIdentity(
            pid=row.pid,
            start_time=row.start_time,
            executable=row.executable,
            argv_digest=argv_digest(row.argv),
            ancestry=tuple(ancestry),
        )

    def census(self) -> tuple[ProcessIdentity, ...]:
        for attempt in range(CENSUS_SNAPSHOT_ATTEMPTS):
            raw = self._run(("/bin/ps", "-axo", "pid="))
            if not raw:
                raise ProcessIdentityError("Darwin process census is unavailable")
            pids: list[int] = []
            for token in raw.split():
                try:
                    pids.append(int(token))
                except ValueError as exc:
                    raise ProcessObservationError(
                        "Darwin process census listed a non-PID"
                    ) from exc
            identities: list[ProcessIdentity] = []
            try:
                for pid in pids:
                    identity = self.observe(pid)
                    if identity is not None:
                        identities.append(identity)
            except ProcessObservationError:
                if attempt + 1 == CENSUS_SNAPSHOT_ATTEMPTS:
                    raise
                continue
            return tuple(sorted(identities, key=lambda identity: identity.pid))
        raise AssertionError("bounded census attempts exhausted without a result")
