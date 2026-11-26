"""Read-only measurement-owner census and acquisition-owned campaign registry.

This is a snapshot guard, not capture/publication mutual exclusion. Hand-run
chains have coverage only during registered campaigns; direct collectors and
old checkouts may be uninstrumented. A dead owner can leave surviving children.
Use driver-managed chains and sequential publication/launch, with the same
JOULEWISE_CUSTODY_PARENT in measurement and publication environments.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import errno
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import sys
from typing import Callable

CUSTODY_PARENT_ENV = "JOULEWISE_CUSTODY_PARENT"
ADDITIONAL_PARENTS_ENV = "JOULEWISE_ADDITIONAL_CUSTODY_PARENTS"
IDENTITY_PROBE_ENV = "JOULEWISE_IDENTITY_PROBE"
REGISTRY_SCHEMA = "joulewise.active_campaign.v1"
_START = re.compile(r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4}")


@dataclass(frozen=True)
class Identity:
    state: str  # LIVE, DEAD, UNKNOWN
    start_time: str | None = None


def _start_token(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split())
    return normalized if _START.fullmatch(normalized) else None


def observe_identity(pid: int) -> Identity:
    """Observe only this PID's lstart and state, never command text.

    The optional probe executable receives the same arguments as ps; it is a
    single pathname, not shell text. Exit 1 with empty output denotes no PID.
    All other failures are UNKNOWN. Tokens match the watchdog's whitespace
    normalization, under the C locale and UTC (lstart has one-second precision).
    """
    if type(pid) is not int or pid <= 0:
        return Identity("UNKNOWN")
    try:
        result = subprocess.run(
            [os.environ.get(IDENTITY_PROBE_ENV, "/bin/ps"),
             "-p", str(pid), "-o", "lstart=", "-o", "stat="],
            capture_output=True, text=True, timeout=2,
            env={**os.environ, "LC_ALL": "C", "LANG": "C", "TZ": "UTC"},
        )
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return Identity("UNKNOWN")
    if result.returncode == 1 and not result.stdout.strip() and not result.stderr.strip():
        return Identity("DEAD")
    parts = result.stdout.split()
    if result.returncode != 0 or result.stderr.strip() or len(parts) != 6:
        return Identity("UNKNOWN")
    token = _start_token(" ".join(parts[:5]))
    if token is None or not re.fullmatch(r"[A-Za-z+<Ns0-9-]+", parts[5]):
        return Identity("UNKNOWN")
    return Identity("DEAD") if parts[5].startswith("Z") else Identity("LIVE", token)


def custody_parent() -> Path:
    return census_fs(Path(os.environ.get(CUSTODY_PARENT_ENV, "~/night-custody")), "expanduser")


@dataclass(frozen=True)
class RegistryEntry:
    path: Path
    st_dev: int
    st_ino: int
    payload: bytes


def remove_campaign(entry: RegistryEntry | None) -> None:
    """Release only the unchanged inode and bytes published by this acquisition."""
    if entry is None:
        return
    try:
        with entry.path.open("rb") as handle:
            current = os.fstat(handle.fileno())
            if ((current.st_dev, current.st_ino) != (entry.st_dev, entry.st_ino)
                    or handle.read() != entry.payload):
                return
        current = entry.path.stat()
        if (current.st_dev, current.st_ino) == (entry.st_dev, entry.st_ino):
            entry.path.unlink()
    except FileNotFoundError:
        pass


def publish_campaign(runs_root: Path, nonce: str, *, pid: int | None = None,
                     start_time: str | None = None,
                     parent: Path | None = None,
                     observer: Callable[[int], Identity] | None = None) -> RegistryEntry:
    """Publish before child dispatch.

    An unavailable start identity (the ps probe returned UNKNOWN) is published
    as ``"start_time": null``; it no longer raises (Opus triple audit F4a: the
    raise made run_campaign return 2 and lost the stage to a failed probe).
    The caller flags it (``campaign.runner_record_flagged``), and the census
    judges such an entry by the process state and the entry's own write time
    (:func:`_inspect_identity`).
    """
    pid = os.getpid() if pid is None else pid
    if start_time is None:
        identity = (observer or observe_identity)(pid)
        start_time = identity.start_time if identity.state == "LIVE" else None
    registry = (custody_parent() if parent is None else parent) / "active-campaigns"
    registry.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps({"schema": REGISTRY_SCHEMA, "pid": pid,
                          "start_time": _start_token(start_time),
                          "runs_root": str(runs_root.resolve()), "nonce": nonce},
                         sort_keys=True) + "\n").encode()
    path = registry / f"{pid}-{secrets.token_hex(24)}.json"
    with path.open("xb") as handle:
        st = os.fstat(handle.fileno())
        entry = RegistryEntry(path, st.st_dev, st.st_ino, payload)
        try:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            # The descriptor still owns this unique file, including partial writes.
            current = path.stat()
            if (current.st_dev, current.st_ino) == (st.st_dev, st.st_ino):
                path.unlink()
            raise
    return entry


@dataclass
class Census:
    refusals: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    resolved_parents: list[str] = field(default_factory=list)

    @property
    def clear(self) -> bool:
        return not self.refusals


class Refused(RuntimeError):
    """An invalid census or an indeterminate filesystem observation."""

    def __init__(self, path_or_reason: Path | str, error_number: int | None = None,
                 *, operation: str | None = None):
        self.path = path_or_reason if isinstance(path_or_reason, Path) else None
        self.errno = error_number
        self.operation = operation
        reason = (f"census indeterminate: {self.path} (errno {error_number})"
                  if self.path is not None else str(path_or_reason))
        super().__init__(reason)


def census_fs(path: Path, operation: str, *, dir_fd: int | None = None):
    """Perform one census filesystem operation, including iterator consumption."""
    target = path if dir_fd is None else path.name

    @contextmanager
    def observation():
        try:
            yield
        except OSError as exc:
            number = exc.errno
            if number is None and isinstance(exc, FileNotFoundError):
                number = errno.ENOENT
            failed_path = Path(os.fsdecode(exc.filename)) if exc.filename else path
            raise Refused(failed_path if failed_path.is_absolute() else path,
                          number, operation=operation) from exc

    @contextmanager
    def directory():
        with observation():
            fd = os.open(target, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dir_fd)
            try:
                yield fd
            finally:
                os.close(fd)

    def open_marker(name, flags):
        return os.open(name, flags | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dir_fd)

    if operation == "directory":
        return directory()
    with observation():
        match operation:
            case "list":
                if dir_fd is None:
                    return list(path.iterdir())
                with os.scandir(dir_fd) as entries:
                    return [path / entry.name for entry in entries]
            case "stat":
                if dir_fd is None:
                    return path.stat()
                info = os.stat(target, dir_fd=dir_fd, follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    raise OSError(errno.ELOOP, "census entry is a symlink", target)
                return info
            case "lstat":
                return path.lstat() if dir_fd is None else os.lstat(target, dir_fd=dir_fd)
            case "read":
                if dir_fd is None:
                    return path.read_text(encoding="utf-8")
                with open(target, encoding="utf-8", opener=open_marker) as handle:
                    return handle.read()
            case "resolve":
                return Path(os.path.realpath(path, strict=True))
            case "expanduser":
                return path.expanduser()
            case "home":
                return Path.home()
            case _:
                raise ValueError(f"unsupported census filesystem operation: {operation}")


def _read_marker(path: Path, *, dir_fd: int | None = None) -> dict:
    value = json.loads(census_fs(path, "read", dir_fd=dir_fd))
    if not isinstance(value, dict):
        raise ValueError(f"not an object: {path}")
    return value


def _exists(path: Path) -> bool:
    try:
        census_fs(path, "stat")
        return True
    except Refused as exc:
        if exc.errno != errno.ENOENT:
            raise
        return False


def _is_symlink(path: Path, *, dir_fd: int | None = None) -> bool:
    try:
        return stat.S_ISLNK(census_fs(path, "lstat", dir_fd=dir_fd).st_mode)
    except Refused as exc:
        if dir_fd is not None or exc.errno != errno.ENOENT:
            raise
        return False


def census_entries(path: Path, *, dir_fd: int | None = None) -> dict[str, Path]:
    """Index one complete listing by folded name while preserving its spelling."""
    names = {}
    for entry in census_fs(path, "list", dir_fd=dir_fd):
        key = entry.name.casefold()
        if key in names:
            raise Refused(f"case-folded name collision at {path}: {names[key].name!r} and {entry.name!r}")
        names[key] = entry
    return names


def _valid_exit(record: dict) -> bool:
    return ("exit_code" in record
            and (type(record["exit_code"]) is int or record["exit_code"] is None)
            and type(record.get("epoch_s")) in (int, float)
            and type(record.get("monotonic_ns")) is int)


def _started_after_written(start: str, path: Path, *, dir_fd: int | None = None) -> bool:
    """True when the ``lstart`` token (UTC, 1 s precision) is more than 1 s after ``path``'s mtime."""
    import calendar
    import time

    try:
        started = calendar.timegm(time.strptime(start, "%a %b %d %H:%M:%S %Y"))
    except (ValueError, OverflowError):
        return False
    written = census_fs(path, "stat", dir_fd=dir_fd).st_mtime
    return started > written + 1


def _inspect_identity(record: dict, path: Path, result: Census,
                      observer: Callable[[int], Identity], *, dir_fd: int | None = None) -> None:
    pid = record.get("pid")
    if type(pid) is not int or pid <= 0:
        raise ValueError(f"invalid PID: {path}")
    identity = observer(pid)
    if identity.state == "DEAD":
        result.warnings.append(f"stale dead owner: {path}")
        return
    token = _start_token(record.get("start_time"))
    observed = _start_token(identity.start_time)
    if identity.state == "LIVE" and token is None and observed is not None \
            and _started_after_written(observed, path, dir_fd=dir_fd):
        # An entry published without a start time (publish_campaign, probe
        # UNKNOWN): a live process that started after the entry was written
        # cannot be its writer, so the pid was reused.
        result.warnings.append(f"stale reused PID (entry has no start time): {path}")
        return
    if identity.state != "LIVE" or token is None or observed is None:
        raise ValueError(f"identity unavailable or legacy live PID: {path}")
    if token != observed:
        result.warnings.append(f"stale reused PID: {path}")
        return
    result.refusals.append(f"live measurement owner: {path}")


def _pending_present(path: Path) -> bool:
    # A dangling link is unreadable custody, not an absent launcher record.
    return _exists(path) or _is_symlink(path)


def _marker(path: Path, names: dict[str, Path] | None, *, include_dangling=False) -> Path | None:
    if names is not None:
        return names.get(path.name.casefold())
    present = _pending_present(path) if include_dangling else _exists(path)
    return path if present else None


def pending_launch_closed(night: Path, *, names: dict[str, Path] | None = None,
                          dir_fd: int | None = None) -> bool:
    """Read durable closure before probing a historical, reusable group number."""
    for name in ("chain.exited", "launch.resolved"):
        path = _marker(night / name, names, include_dangling=True)
        if path is None:
            continue
        if _is_symlink(path, dir_fd=dir_fd):
            raise ValueError(f"launcher closure is a symlink: {path}")
        record = _read_marker(path, dir_fd=dir_fd)
        if name == "chain.exited":
            valid = _valid_exit(record)
        else:
            valid = (record.get("schema") == "joulewise.launch_resolved.v1"
                     and record.get("basis") == "group_absent"
                     and type(record.get("pgid")) is int and record["pgid"] > 1
                     and type(record.get("epoch_s")) in (int, float)
                     and type(record.get("monotonic_ns")) is int)
        if not valid:
            raise ValueError(f"invalid launcher closure: {path}")
        return True
    return False


def _pending_group_gone(pgid: int, marker: Path) -> bool:
    """Check whether a process group exists without sending it a signal."""
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True
    except OSError as exc:
        raise Refused(f"pending process group indeterminate: {marker}: {exc}") from exc
    return False


def _inspect_pending(path: Path, result: Census,
                     observer: Callable[[int], Identity], *, names: dict[str, Path] | None = None,
                     dir_fd: int | None = None) -> None:
    path = _marker(path, names, include_dangling=True)
    if path is None:
        return
    if pending_launch_closed(path.parent, names=names, dir_fd=dir_fd):
        return
    if _is_symlink(path, dir_fd=dir_fd):
        raise ValueError(f"pending launcher identity is a symlink: {path}")
    record = _read_marker(path, dir_fd=dir_fd)
    pid, pgid = record.get("pid"), record.get("pgid")
    if type(pid) is not int or pid <= 1 or type(pgid) is not int or pgid <= 1:
        raise ValueError(f"invalid pending launcher identity: {path}")
    identity = observer(pid)
    token, observed = _start_token(record.get("start_time")), _start_token(identity.start_time)
    if identity.state == "LIVE" and token is not None and observed is not None and token != observed:
        result.warnings.append(f"stale reused PID: {path}")
        return
    if _pending_group_gone(pgid, path):
        result.warnings.append(f"stale dead pending process group: {path}")
        return
    # A dead leader cannot disprove surviving members of an unresolved group.
    refusal_count = len(result.refusals)
    _inspect_identity(record, path, result, lambda pid: identity, dir_fd=dir_fd)
    if len(result.refusals) == refusal_count:
        result.refusals.append(f"live measurement owner process group: {path}")


def _inspect_started_chain(night: Path, result: Census,
                           observer: Callable[[int], Identity], *, names: dict[str, Path] | None = None,
                           dir_fd: int | None = None) -> None:
    started = _marker(night / "chain.started", names)
    if started is None:
        return
    exited = _marker(night / "chain.exited", names)
    if exited is None:
        record = _read_marker(started, dir_fd=dir_fd)
        # Reconcile an exit published while reading the start marker.
        current = census_entries(night, dir_fd=dir_fd) if names is not None else None
        exited = _marker(night / "chain.exited", current)
    if exited is not None:
        if not _valid_exit(_read_marker(exited, dir_fd=dir_fd)):
            raise ValueError(f"invalid exit marker: {exited}")
        return
    if _start_token(record.get("start_time")) is None:
        raise ValueError(f"chain start identity unavailable: {started}")
    _inspect_identity(record, started, result, observer, dir_fd=dir_fd)


def _inspect_chain(night: Path, result: Census, observer: Callable[[int], Identity],
                   *, dir_fd: int | None = None) -> None:
    names = census_entries(night, dir_fd=dir_fd) if dir_fd is not None else None
    pending = Census()
    _inspect_pending(night / "launch.pending", pending, observer, names=names, dir_fd=dir_fd)
    _inspect_started_chain(night, pending, observer, names=names, dir_fd=dir_fd)
    # Commit diagnostics only after both reads, so reconciliation cannot duplicate them.
    result.refusals.extend(pending.refusals)
    result.warnings.extend(pending.warnings)


def _inspect_campaign(path: Path, result: Census, observer: Callable[[int], Identity],
                      *, dir_fd: int | None = None) -> None:
    record = _read_marker(path, dir_fd=dir_fd)
    if (record.get("schema") != REGISTRY_SCHEMA
            or not isinstance(record.get("nonce"), str) or not record["nonce"]
            or not isinstance(record.get("runs_root"), str)
            or not Path(record["runs_root"]).is_absolute()):
        raise ValueError(f"invalid registry marker: {path}")
    # The entry itself governs; a missing referenced campaign.lock does not clear it.
    _inspect_identity(record, path, result, observer, dir_fd=dir_fd)


def _reconciled(action: Callable[[], None], present: Callable[[], bool]) -> None:
    try:
        action()
    except Refused as exc:
        if exc.errno != errno.ENOENT or exc.operation == "stat":
            raise
        # Exactly one reread/reconciliation; repeated disappearance is uncertain.
        if present():
            action()


def _inspect_resolved_root(parent: Path, result: Census, observer: Callable[[int], Identity]) -> None:
    with census_fs(parent, "directory") as root_fd:
        for key, child in census_entries(parent, dir_fd=root_fd).items():
            if key == "active-campaigns":
                with census_fs(child, "directory", dir_fd=root_fd) as registry_fd:
                    for entry in census_entries(child, dir_fd=registry_fd).values():
                        _inspect_campaign(entry, result, observer, dir_fd=registry_fd)
            elif stat.S_ISDIR(census_fs(child, "stat", dir_fd=root_fd).st_mode):
                with census_fs(child, "directory", dir_fd=root_fd) as plan_fd:
                    night = census_entries(child, dir_fd=plan_fd).get("night")
                    if night is not None:
                        with census_fs(night, "directory", dir_fd=plan_fd) as night_fd:
                            _inspect_chain(night, result, observer, dir_fd=night_fd)


def census(*, parents: list[Path] | None = None,
           observer: Callable[[int], Identity] | None = None, strict: bool = False) -> Census:
    """Inspect plan and registry entries, with complete enumeration for strict callers."""
    result = Census()
    observer = observer or observe_identity
    try:
        if parents is None:
            extra = json.loads(os.environ.get(ADDITIONAL_PARENTS_ENV, "[]"))
            if not isinstance(extra, list) or any(not isinstance(p, str) or not p for p in extra):
                raise ValueError("additional custody parents must be a JSON array of paths")
            parents = [custody_parent(), *(census_fs(Path(p), "expanduser") for p in extra)]
        resolved = set()
        for parent in dict.fromkeys(parents):
            if strict:
                if not parent.is_absolute() or {part.casefold() for part in parent.parts} & {"..", "restricted"}:
                    raise Refused(f"invalid custody parent: {parent}")
                parent = census_fs(parent, "resolve")
                if any(part.casefold() == "restricted" for part in parent.parts):
                    raise Refused(f"invalid resolved custody parent: {parent}")
                if parent not in resolved:
                    resolved.add(parent)
                    _inspect_resolved_root(parent, result, observer)
                    result.resolved_parents.append(str(parent))
                continue
            try:
                children = census_fs(parent, "list")
            except Refused as exc:
                if exc.errno != errno.ENOENT:
                    raise
                continue
            for child in children:
                if child.name == "active-campaigns":
                    def inspect_registry() -> None:
                        pending = Census()
                        for path in census_fs(child, "list"):
                            _reconciled(lambda: _inspect_campaign(path, pending, observer),
                                        lambda: _exists(path))
                        result.refusals.extend(pending.refusals)
                        result.warnings.extend(pending.warnings)
                    _reconciled(inspect_registry, lambda: _exists(child))
                else:
                    try:
                        is_dir = stat.S_ISDIR(census_fs(child, "stat").st_mode)
                    except Refused as exc:
                        if exc.errno != errno.ENOENT:
                            raise
                        continue
                    if is_dir:
                        night = child / "night"
                        _reconciled(lambda: _inspect_chain(night, result, observer),
                                    lambda: (_exists(night / "chain.started")
                                             or _pending_present(night / "launch.pending")))
    except Refused as exc:
        if strict:
            raise
        result.refusals.append(f"census indeterminate: {exc}")
    except (ValueError, TypeError, UnicodeError, RuntimeError) as exc:
        result.refusals.append(f"census indeterminate: {exc}")
    return result


def main() -> int:
    result = census()
    for warning in result.warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    for refusal in result.refusals:
        print(f"REFUSING: {refusal}", file=sys.stderr)
    return 0 if result.clear else 1


if __name__ == "__main__":
    sys.exit(main())
