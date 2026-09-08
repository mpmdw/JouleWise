"""Read-only measurement-owner census and acquisition-owned campaign registry.

This is a snapshot guard, not capture/publication mutual exclusion. Hand-run
chains have coverage only during registered campaigns; direct collectors and
old checkouts may be uninstrumented. A dead owner can leave surviving children.
Use driver-managed chains and sequential publication/launch, with the same
JOULEWISE_CUSTODY_PARENT in measurement and publication environments.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import secrets
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
    normalization, under the C locale (lstart has one-second precision).
    """
    if type(pid) is not int or pid <= 0:
        return Identity("UNKNOWN")
    try:
        result = subprocess.run(
            [os.environ.get(IDENTITY_PROBE_ENV, "/bin/ps"),
             "-p", str(pid), "-o", "lstart=", "-o", "stat="],
            capture_output=True, text=True, timeout=2,
            env={**os.environ, "LC_ALL": "C", "LANG": "C"},
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
    return Path(os.environ.get(CUSTODY_PARENT_ENV, "~/night-custody")).expanduser()


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
    """Publish before child dispatch; failure prevents measurement acquisition."""
    pid = os.getpid() if pid is None else pid
    if start_time is None:
        identity = (observer or observe_identity)(pid)
        start_time = identity.start_time if identity.state == "LIVE" else None
    if type(pid) is not int or pid <= 0 or _start_token(start_time) is None or not nonce:
        raise RuntimeError("campaign start identity unavailable")
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

    @property
    def clear(self) -> bool:
        return not self.refusals


def _read_marker(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"not an object: {path}")
    return value


def _exists(path: Path) -> bool:
    try:
        path.stat()
        return True
    except FileNotFoundError:
        return False


def _valid_exit(record: dict) -> bool:
    return ("exit_code" in record
            and (type(record["exit_code"]) is int or record["exit_code"] is None)
            and type(record.get("epoch_s")) in (int, float)
            and type(record.get("monotonic_ns")) is int)


def _inspect_identity(record: dict, path: Path, result: Census,
                      observer: Callable[[int], Identity]) -> None:
    pid = record.get("pid")
    if type(pid) is not int or pid <= 0:
        raise ValueError(f"invalid PID: {path}")
    identity = observer(pid)
    if identity.state == "DEAD":
        result.warnings.append(f"stale dead owner: {path}")
        return
    token = _start_token(record.get("start_time"))
    observed = _start_token(identity.start_time)
    if identity.state != "LIVE" or token is None or observed is None:
        raise ValueError(f"identity unavailable or legacy live PID: {path}")
    if token != observed:
        result.warnings.append(f"stale reused PID: {path}")
        return
    result.refusals.append(f"live measurement owner: {path}")


def _inspect_chain(night: Path, result: Census, observer: Callable[[int], Identity]) -> None:
    started, exited = night / "chain.started", night / "chain.exited"
    if not _exists(started):
        return
    if _exists(exited):
        if not _valid_exit(_read_marker(exited)):
            raise ValueError(f"invalid exit marker: {exited}")
        return
    record = _read_marker(started)
    # Reconcile an exit published while reading the start marker.
    if _exists(exited):
        if not _valid_exit(_read_marker(exited)):
            raise ValueError(f"invalid exit marker: {exited}")
        return
    if _start_token(record.get("start_time")) is None:
        raise ValueError(f"chain start identity unavailable: {started}")
    _inspect_identity(record, started, result, observer)


def _inspect_campaign(path: Path, result: Census, observer: Callable[[int], Identity]) -> None:
    record = _read_marker(path)
    if (record.get("schema") != REGISTRY_SCHEMA
            or not isinstance(record.get("nonce"), str) or not record["nonce"]
            or not isinstance(record.get("runs_root"), str)
            or not Path(record["runs_root"]).is_absolute()):
        raise ValueError(f"invalid registry marker: {path}")
    # The entry itself governs; a missing referenced campaign.lock does not clear it.
    _inspect_identity(record, path, result, observer)


def _reconciled(action: Callable[[], None], present: Callable[[], bool]) -> None:
    try:
        action()
    except FileNotFoundError:
        # Exactly one reread/reconciliation; repeated disappearance is uncertain.
        if present():
            action()


def census(*, parents: list[Path] | None = None,
           observer: Callable[[int], Identity] | None = None) -> Census:
    """Inspect direct plan directories and registry entries without custody writes."""
    result = Census()
    observer = observer or observe_identity
    try:
        if parents is None:
            extra = json.loads(os.environ.get(ADDITIONAL_PARENTS_ENV, "[]"))
            if not isinstance(extra, list) or any(not isinstance(p, str) or not p for p in extra):
                raise ValueError("additional custody parents must be a JSON array of paths")
            parents = [custody_parent(), *(Path(p).expanduser() for p in extra)]
        for parent in dict.fromkeys(parents):
            # Missing parent is empty; ENOTDIR and permission errors are not.
            try:
                children = list(parent.iterdir())
            except FileNotFoundError:
                continue
            for child in children:
                if child.name == "active-campaigns":
                    def inspect_registry() -> None:
                        pending = Census()
                        for path in list(child.iterdir()):
                            _reconciled(lambda: _inspect_campaign(path, pending, observer),
                                        lambda: _exists(path))
                        result.refusals.extend(pending.refusals)
                        result.warnings.extend(pending.warnings)
                    _reconciled(inspect_registry, lambda: _exists(child))
                else:
                    # stat errors must propagate instead of Path.is_dir swallowing them.
                    import stat
                    try:
                        is_dir = stat.S_ISDIR(child.stat().st_mode)
                    except FileNotFoundError:
                        continue
                    if is_dir:
                        _reconciled(lambda: _inspect_chain(child / "night", result, observer),
                                    lambda: _exists(child / "night" / "chain.started"))
    except (OSError, ValueError, TypeError, UnicodeError, RuntimeError) as exc:
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
