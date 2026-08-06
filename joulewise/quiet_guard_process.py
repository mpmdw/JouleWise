"""Snapshot-bound process identity primitives for the JouleWise quiet guard.

Recovery uses one accepted Darwin ``KERN_PROC_ALL`` payload as its presence
and topology authority.  Exact ``KERN_PROC_PID``/``KERN_PROCARGS2`` reads are
then limited to custody roots, candidate descendants, and the ancestry links
needed to construct their complete identities.  No accepted table is replaced
inside an invocation: disappearance, PID reuse, exec, reparenting, or any
observation failure after acceptance is a refusal.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import ctypes
import ctypes.util
import errno
import hashlib
import struct
import sys
from typing import Any, Iterable, Mapping, Protocol, Sequence


PROCESS_IDENTITY_SCHEMA = "joulewise.quiet_guard.process_identity/v1"
ARGV_DIGEST_PREFIX = "sha256:"
KERNEL_TABLE_ACQUISITION_ATTEMPTS = 3

# 64-bit Darwin SDK ABI (MacOSX.sdk sys/proc.h + sys/sysctl.h).  Tests build
# byte-accurate kinfo_proc rows at these offsets so decoder drift fails closed.
KINFO_PROC_SIZE = 648
KINFO_PROC_START_OFFSET = 0
KINFO_PROC_PID_OFFSET = 40
KINFO_PROC_PPID_OFFSET = 560


class ProcessIdentityError(ValueError):
    """A process observation or durable identity is malformed."""


class ProcessObservationError(ProcessIdentityError):
    """A snapshot row cannot be observed reliably."""

    def __init__(self, detail: str, *, error_number: int | None = None) -> None:
        super().__init__(detail)
        self.error_number = error_number


def argv_digest(argv: Sequence[str] | bytes) -> str:
    """Return an unambiguous SHA-256 digest for an argv observation."""

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
    """The complete exact identity used for registry and custody checks."""

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
    return ProcessIdentity.from_mapping(value)


@dataclass(frozen=True)
class KernelProcessRecord:
    """One row from the accepted process-table presence/topology snapshot."""

    pid: int
    ppid: int
    start_time: str

    def __post_init__(self) -> None:
        if type(self.pid) is not int or self.pid < 0:
            raise ProcessObservationError(
                "kernel row pid must be a nonnegative integer"
            )
        if type(self.ppid) is not int or self.ppid < 0:
            raise ProcessObservationError("kernel row parent PID is invalid")
        _plain_nonempty(self.start_time, "kernel row start_time")


@dataclass(frozen=True)
class KernelProcessTable:
    """Validated immutable KERN_PROC_ALL payload interpretation."""

    rows: tuple[KernelProcessRecord, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.rows, tuple) or not all(
            isinstance(row, KernelProcessRecord) for row in self.rows
        ):
            raise ProcessObservationError("kernel process table rows are invalid")
        by_pid = {row.pid: row for row in self.rows}
        if len(by_pid) != len(self.rows):
            raise ProcessObservationError("kernel process table contains duplicate PIDs")
        for row in self.rows:
            if row.ppid and row.ppid not in by_pid:
                raise ProcessObservationError(
                    f"kernel process table parent {row.ppid} is missing"
                )
        for origin in by_pid:
            seen: set[int] = set()
            pid = origin
            while pid:
                if pid in seen:
                    raise ProcessObservationError("kernel process table contains a cycle")
                seen.add(pid)
                pid = by_pid[pid].ppid

    @property
    def by_pid(self) -> dict[int, KernelProcessRecord]:
        return {row.pid: row for row in self.rows}

    def descendants(self, root_pid: int) -> frozenset[int]:
        if type(root_pid) is not int or root_pid <= 0:
            raise ProcessObservationError(
                "kernel process table traversal root must be a positive PID"
            )
        children: dict[int, list[int]] = {}
        for row in self.rows:
            children.setdefault(row.ppid, []).append(row.pid)
        descendants: set[int] = set()
        pending = list(children.get(root_pid, ()))
        while pending:
            pid = pending.pop()
            if pid in descendants:
                raise ProcessObservationError("kernel process table traversal cycled")
            descendants.add(pid)
            pending.extend(children.get(pid, ()))
        return frozenset(descendants)


def custody_candidate_pids(
    snapshot: KernelProcessTable,
    roots: Iterable[ProcessIdentity],
) -> tuple[frozenset[int], frozenset[int]]:
    """Return snapshot-matching root PIDs and all of their descendants."""

    by_pid = snapshot.by_pid
    active_roots = {
        root.pid
        for root in roots
        if root.pid in by_pid and by_pid[root.pid].start_time == root.start_time
    }
    descendants: set[int] = set()
    for pid in active_roots:
        descendants.update(snapshot.descendants(pid))
    return frozenset(active_roots), frozenset(descendants)


class ProcessSource(Protocol):
    """Boundary for one inventory plus snapshot-bound exact observations."""

    def inventory(self) -> KernelProcessTable:
        ...

    def observe(
        self, pid: int, snapshot: KernelProcessTable
    ) -> ProcessIdentity | None:
        """Return ``None`` only when a requested row is positively absent."""

        ...


class Revalidation(str, Enum):
    MATCH = "match"
    ABSENT = "absent"
    PID_REUSED = "pid_reused"
    UNOBSERVABLE = "unobservable"


def revalidate_identity(
    expected: ProcessIdentity,
    source: ProcessSource,
    snapshot: KernelProcessTable,
) -> tuple[Revalidation, ProcessIdentity | None]:
    """Classify an expected identity against one accepted snapshot."""

    row = snapshot.by_pid.get(expected.pid)
    if row is None:
        return Revalidation.ABSENT, None
    try:
        observed = source.observe(expected.pid, snapshot)
    except ProcessObservationError:
        return Revalidation.UNOBSERVABLE, None
    if observed is None:
        return Revalidation.UNOBSERVABLE, None
    if observed == expected:
        return Revalidation.MATCH, observed
    return Revalidation.PID_REUSED, observed


class SnapshotProcessSource:
    """Deterministic one-snapshot source for tests and recovery simulations."""

    def __init__(
        self,
        identities: Iterable[ProcessIdentity] = (),
        *,
        inventory_rows: Iterable[KernelProcessRecord] | None = None,
        unobservable_pids: Iterable[int] = (),
    ) -> None:
        identities = tuple(identities)
        self._identities = {identity.pid: identity for identity in identities}
        if inventory_rows is None:
            derived: dict[int, KernelProcessRecord] = {}
            for identity in identities:
                chain = (
                    (identity.pid, identity.start_time),
                    *((ancestor.pid, ancestor.start_time) for ancestor in identity.ancestry),
                )
                for index, (pid, start_time) in enumerate(chain):
                    ppid = chain[index + 1][0] if index + 1 < len(chain) else 0
                    row = KernelProcessRecord(pid, ppid, start_time)
                    if pid in derived and derived[pid] != row:
                        raise ProcessObservationError(
                            "snapshot identities disagree on kernel topology"
                        )
                    derived[pid] = row
            inventory_rows = tuple(derived[pid] for pid in sorted(derived))
        self._snapshot = KernelProcessTable(tuple(inventory_rows))
        self._unobservable_pids = frozenset(unobservable_pids)
        self.inventory_calls = 0
        self.observed_pids: list[int] = []

    def inventory(self) -> KernelProcessTable:
        self.inventory_calls += 1
        return self._snapshot

    def observe(
        self, pid: int, snapshot: KernelProcessTable
    ) -> ProcessIdentity | None:
        self.observed_pids.append(pid)
        if pid in self._unobservable_pids:
            raise ProcessObservationError(f"cannot observe snapshot PID {pid}")
        if snapshot is not self._snapshot:
            raise ProcessObservationError("exact observation used a foreign snapshot")
        identity = self._identities.get(pid)
        if identity is None:
            return None
        row = snapshot.by_pid.get(pid)
        if row is None:
            raise ProcessObservationError("identity is absent from the accepted snapshot")
        expected_ppid = identity.ancestry[0].pid if identity.ancestry else 0
        if identity.start_time != row.start_time or expected_ppid != row.ppid:
            raise ProcessObservationError("identity changed after snapshot acceptance")
        return identity


@dataclass(frozen=True)
class DarwinProcessRecord:
    """One exact candidate row bound to the accepted kernel table."""

    pid: int
    ppid: int
    start_time: str
    executable: str
    argv: tuple[str, ...]


class DarwinProcessReader(Protocol):
    def inventory(self) -> KernelProcessTable:
        ...

    def read_exact(self, expected: KernelProcessRecord) -> DarwinProcessRecord | None:
        ...


class _Timeval(ctypes.Structure):
    _fields_ = (("tv_sec", ctypes.c_long), ("tv_usec", ctypes.c_int))


class SysctlDarwinProcessReader:
    """Decode Darwin KERN_PROC_ALL and exact candidate sysctl material."""

    CTL_KERN = 1
    KERN_ARGMAX = 8
    KERN_PROC = 14
    KERN_PROC_ALL = 0
    KERN_PROC_PID = 1
    KERN_PROCARGS2 = 49

    def __init__(
        self,
        *,
        platform_name: str | None = None,
        libc: Any | None = None,
    ) -> None:
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

    def _sysctl_size(self, mib: Sequence[int]) -> int:
        libc = self._system_library()
        if libc is None:
            raise ProcessObservationError("Darwin system library is unavailable")
        names = (ctypes.c_int * len(mib))(*mib)
        for _ in range(KERNEL_TABLE_ACQUISITION_ATTEMPTS):
            size = ctypes.c_size_t(0)
            if libc.sysctl(names, len(mib), None, ctypes.byref(size), None, 0) == 0:
                return size.value
            error_number = ctypes.get_errno()
            if error_number != errno.EINTR:
                raise ProcessObservationError(
                    "Darwin sysctl size query failed", error_number=error_number
                )
        raise ProcessObservationError(
            "Darwin sysctl size query was repeatedly interrupted",
            error_number=errno.EINTR,
        )

    def _sysctl_capacity(self, mib: Sequence[int], capacity: int) -> bytes:
        libc = self._system_library()
        if libc is None:
            raise ProcessObservationError("Darwin system library is unavailable")
        if type(capacity) is not int or capacity <= 0 or capacity > 64 * 1024 * 1024:
            raise ProcessObservationError("Darwin sysctl capacity is invalid")
        names = (ctypes.c_int * len(mib))(*mib)
        for _ in range(KERNEL_TABLE_ACQUISITION_ATTEMPTS):
            buffer = ctypes.create_string_buffer(capacity)
            size = ctypes.c_size_t(capacity)
            if libc.sysctl(names, len(mib), buffer, ctypes.byref(size), None, 0) == 0:
                if size.value > capacity:
                    raise ProcessObservationError("Darwin sysctl exceeded its capacity")
                return bytes(buffer.raw[: size.value])
            error_number = ctypes.get_errno()
            if error_number != errno.EINTR:
                raise ProcessObservationError(
                    "Darwin sysctl payload query failed", error_number=error_number
                )
        raise ProcessObservationError(
            "Darwin sysctl payload query was repeatedly interrupted",
            error_number=errno.EINTR,
        )

    def _sysctl(self, mib: Sequence[int], capacity: int | None = None) -> bytes:
        if capacity is None:
            capacity = self._sysctl_size(mib)
        if capacity == 0:
            return b""
        return self._sysctl_capacity(mib, capacity)

    @staticmethod
    def _decode_row(payload: bytes, offset: int = 0) -> KernelProcessRecord:
        if ctypes.sizeof(ctypes.c_long) != 8 or ctypes.sizeof(ctypes.c_void_p) != 8:
            raise ProcessObservationError("unsupported Darwin kinfo_proc ABI")
        if offset < 0 or len(payload) - offset < KINFO_PROC_SIZE:
            raise ProcessObservationError("KERN_PROC payload row is truncated")
        timeval = _Timeval.from_buffer_copy(
            payload[offset + KINFO_PROC_START_OFFSET : offset + KINFO_PROC_PID_OFFSET]
        )
        pid = struct.unpack_from("=i", payload, offset + KINFO_PROC_PID_OFFSET)[0]
        ppid = struct.unpack_from("=i", payload, offset + KINFO_PROC_PPID_OFFSET)[0]
        if timeval.tv_sec <= 0 or not 0 <= timeval.tv_usec < 1_000_000:
            raise ProcessObservationError("KERN_PROC start time is invalid")
        return KernelProcessRecord(pid, ppid, f"{timeval.tv_sec}.{timeval.tv_usec:06d}")

    @classmethod
    def decode_kernel_table(cls, payload: bytes) -> KernelProcessTable:
        if not payload or len(payload) % KINFO_PROC_SIZE:
            raise ProcessObservationError("KERN_PROC_ALL payload size is malformed")
        rows = tuple(
            cls._decode_row(payload, offset)
            for offset in range(0, len(payload), KINFO_PROC_SIZE)
        )
        return KernelProcessTable(rows)

    def inventory(self) -> KernelProcessTable:
        mib = (self.CTL_KERN, self.KERN_PROC, self.KERN_PROC_ALL, 0)
        for _ in range(KERNEL_TABLE_ACQUISITION_ATTEMPTS):
            size = self._sysctl_size(mib)
            capacity = size + max(KINFO_PROC_SIZE * 4, size // 8)
            try:
                payload = self._sysctl_capacity(mib, capacity)
            except ProcessObservationError as exc:
                if exc.error_number == errno.ENOMEM:
                    continue
                raise
            return self.decode_kernel_table(payload)
        raise ProcessObservationError(
            "KERN_PROC_ALL repeatedly outgrew its acquisition buffer",
            error_number=errno.ENOMEM,
        )

    def _argmax(self) -> int:
        payload = self._sysctl((self.CTL_KERN, self.KERN_ARGMAX))
        if len(payload) < ctypes.sizeof(ctypes.c_int):
            raise ProcessObservationError("KERN_ARGMAX payload is malformed")
        value = struct.unpack_from("=i", payload)[0]
        if not 0 < value <= 16 * 1024 * 1024:
            raise ProcessObservationError("KERN_ARGMAX value is invalid")
        return value

    def _process_row(self, pid: int) -> KernelProcessRecord | None:
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
        if len(payload) != KINFO_PROC_SIZE:
            raise ProcessObservationError("KERN_PROC_PID payload size is malformed")
        row = self._decode_row(payload)
        if row.pid != pid:
            raise ProcessObservationError("KERN_PROC_PID returned a different PID")
        return row

    def _procargs(self, pid: int) -> tuple[str, tuple[str, ...]] | None:
        try:
            capacity = self._argmax()
            payload = self._sysctl((self.CTL_KERN, self.KERN_PROCARGS2, pid), capacity)
        except ProcessObservationError as exc:
            if exc.error_number == errno.ESRCH:
                return None
            raise
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

    def read_exact(self, expected: KernelProcessRecord) -> DarwinProcessRecord | None:
        if self._platform_name != "darwin":
            raise ProcessObservationError("Darwin process observation is unavailable")
        before = self._process_row(expected.pid)
        if before is None:
            return None
        if before != expected:
            raise ProcessObservationError("candidate changed after table acceptance")
        first_args = self._procargs(expected.pid)
        middle = self._process_row(expected.pid)
        second_args = self._procargs(expected.pid)
        after = self._process_row(expected.pid)
        if (
            first_args is None
            or second_args is None
            or middle != expected
            or after != expected
            or first_args != second_args
        ):
            raise ProcessObservationError("candidate changed during exact observation")
        executable, argv = first_args
        return DarwinProcessRecord(
            expected.pid, expected.ppid, expected.start_time, executable, argv
        )


class DarwinProcessSource:
    """Production source: one kernel table plus targeted exact observations."""

    def __init__(self, *, reader: DarwinProcessReader | None = None) -> None:
        self._reader = reader or SysctlDarwinProcessReader()

    def inventory(self) -> KernelProcessTable:
        return self._reader.inventory()

    def observe(
        self, pid: int, snapshot: KernelProcessTable
    ) -> ProcessIdentity | None:
        if type(pid) is not int or pid <= 0:
            raise ProcessObservationError("PID must be a positive integer")
        by_pid = snapshot.by_pid
        target = by_pid.get(pid)
        if target is None:
            return None
        exact: dict[int, DarwinProcessRecord] = {}
        lineage: list[DarwinProcessRecord] = []
        row = target
        while True:
            observed = exact.get(row.pid)
            if observed is None:
                observed = self._reader.read_exact(row)
                if observed is None:
                    return None
                exact[row.pid] = observed
            lineage.append(observed)
            if row.ppid == 0:
                break
            row = by_pid[row.ppid]
        # A complete identity is accepted only if the child and every ancestry
        # link still have the same snapshot-bound row and true argv after the
        # whole walk.  This is an exact-observation race check, not a semantic
        # process-table re-snapshot.
        for original in lineage:
            repeated = self._reader.read_exact(by_pid[original.pid])
            if repeated is None or repeated != original:
                raise ProcessObservationError(
                    "candidate ancestry changed during exact observation"
                )
        child, *parents = lineage
        return ProcessIdentity(
            pid=child.pid,
            start_time=child.start_time,
            executable=child.executable,
            argv_digest=argv_digest(child.argv),
            ancestry=tuple(
                AncestorIdentity(
                    parent.pid,
                    parent.start_time,
                    parent.executable,
                    argv_digest(parent.argv),
                )
                for parent in parents
            ),
        )
