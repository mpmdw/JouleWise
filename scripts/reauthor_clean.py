#!/usr/bin/env python3
"""Fail-closed cleanup for the three no-clobber T-0 re-author namespaces.

The protocol deliberately proves logical namespace deletion only.  It does not
claim secure erase, APFS block reclamation, or exclusion of a hostile same-UID
process.
"""

from __future__ import annotations

import argparse
import ctypes
import errno
import fcntl
import hashlib
import json
import os
import re
import secrets
import stat
import subprocess
import sys
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Iterable, Iterator, Mapping, Sequence


STATE_SCHEMA = "joulewise.reauthor_clean_state.v3"
RECEIPT_SCHEMA = "joulewise.reauthor_clean_receipt.v3"
PROTOCOL = "manifested_quarantine_fd_unlink.v1"
CANONICALIZATION_ALGORITHM = "rfc8785-profile.sorted-utf8-json.v1"
INVENTORY_ALGORITHM = "joulewise.reauthor_clean_fd_payload_sha256.v1"
PAYLOAD_ALGORITHM = "joulewise.reauthor_clean_logical_payload.v1"
EVENT_CHAIN_ALGORITHM = "joulewise.reauthor_clean_event_chain_sha256.v1"
OPERATION_DIRECTORY = "reauthor-clean.operations"
QUARANTINE_DIRECTORY = ".reauthor_clean.quarantine"
EXPECTED_NAMESPACES = frozenset(
    {
        "arm_readiness.t0.sources",
        "arm_readiness.evidence",
        "arm_readiness.t0.inputs",
    }
)
UF_IMMUTABLE = getattr(stat, "UF_IMMUTABLE", 0x00000002)
O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
ZERO_EVENT_HASH = "0" * 64

REAUTHOR_CLEAN_REASON_CODES = frozenset(
    {
        "reauthor_clean_usage_invalid",
        "reauthor_clean_pack_root_invalid",
        "reauthor_clean_pack_identity_invalid",
        "reauthor_clean_frozen_pack",
        "reauthor_clean_namespace_set_invalid",
        "reauthor_clean_namespace_shape_invalid",
        "reauthor_clean_namespace_missing",
        "reauthor_clean_namespace_inventory_invalid",
        "reauthor_clean_operation_log_invalid",  # retained legacy name
        "reauthor_clean_quarantine_unreceipted",  # retained legacy name
        "reauthor_clean_removal_incomplete",  # retained legacy name
        "reauthor_clean_quarantine_invalid",
        "reauthor_clean_output_collision",
        "reauthor_clean_io_error",
        "reauthor_clean_internal_error",
        "reauthor_clean_platform_capability_missing",
        "reauthor_clean_operation_lock_busy",
        "reauthor_clean_state_manifest_invalid",
        "reauthor_clean_state_ambiguous",
        "reauthor_clean_state_binding_mismatch",
        "reauthor_clean_event_chain_invalid",
        "reauthor_clean_state_inventory_mismatch",
        "reauthor_clean_concurrent_mutation",
        "reauthor_clean_hardlink_unsupported",
        "reauthor_clean_entry_type_unsupported",
        "reauthor_clean_extended_attribute_unreadable",
        "reauthor_clean_destroyed_unverified",
        "reauthor_clean_destroyed_mismatch",
        "reauthor_clean_legacy_state_unbound",
    }
)


class ReauthorCleanError(ValueError):
    """One named, fail-closed refusal, optionally carrying incident custody."""

    def __init__(
        self,
        reason_code: str,
        detail: str,
        *,
        outcome: Mapping[str, object] | None = None,
    ) -> None:
        if reason_code not in REAUTHOR_CLEAN_REASON_CODES:
            raise AssertionError(f"unregistered re-author-clean reason: {reason_code}")
        super().__init__(detail)
        self.reason_code = reason_code
        self.outcome = dict(outcome or {})


def _refuse(
    reason_code: str,
    detail: str,
    *,
    outcome: Mapping[str, object] | None = None,
) -> ReauthorCleanError:
    return ReauthorCleanError(reason_code, detail, outcome=outcome)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _render_json(value: object) -> bytes:
    return _canonical_json(value) + b"\n"


def _utc_now() -> datetime:
    return datetime.now(UTC)


# Tests replace this hook to simulate process death at exact durability steps.
_FAULT_INJECTOR: Callable[[str], None] | None = None


def _fault(point: str) -> None:
    if _FAULT_INJECTOR is not None:
        _FAULT_INJECTOR(point)


def _run_git(repository: Path, *args: str) -> bytes:
    try:
        completed = subprocess.run(
            ("git", "-C", str(repository), *args),
            check=False,
            capture_output=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _refuse(
            "reauthor_clean_pack_root_invalid", f"cannot execute Git proof: {exc}"
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise _refuse("reauthor_clean_pack_root_invalid", f"Git proof failed: {detail}")
    return completed.stdout


def _committed_paths(repository: Path, relative: str) -> set[str]:
    raw = _run_git(repository, "ls-tree", "-r", "--name-only", "HEAD", "--", relative)
    try:
        return set(raw.decode("utf-8", errors="strict").splitlines())
    except UnicodeDecodeError as exc:
        raise _refuse(
            "reauthor_clean_pack_identity_invalid", "Git returned a non-UTF-8 path"
        ) from exc


def _canonical_without_symlink_ancestry(path: Path, reason_code: str) -> Path:
    lexical = Path(os.path.abspath(os.path.normpath(os.fspath(path))))
    resolved = Path(os.path.realpath(lexical))
    if lexical != resolved:
        raise _refuse(reason_code, f"path traverses a symlinked ancestor: {path}")
    return lexical


def _authenticate_pack(pack_root: Path) -> dict[str, object]:
    if not pack_root.is_absolute():
        raise _refuse("reauthor_clean_pack_root_invalid", "pack root must be absolute")
    root = _canonical_without_symlink_ancestry(
        pack_root, "reauthor_clean_pack_root_invalid"
    )
    if root.is_symlink() or not root.is_dir():
        raise _refuse(
            "reauthor_clean_pack_root_invalid",
            "pack root must be an existing non-symlink directory",
        )
    try:
        repository_raw = _run_git(root, "rev-parse", "--show-toplevel").rstrip(b"\n")
        repository = Path(repository_raw.decode("utf-8", errors="strict")).resolve(
            strict=True
        )
        relative = root.relative_to(repository)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise _refuse(
            "reauthor_clean_pack_root_invalid",
            "pack root is not below a UTF-8 Git worktree",
        ) from exc
    if relative.parts != ("configs", "campaigns", root.name):
        raise _refuse(
            "reauthor_clean_pack_root_invalid",
            "pack root must be exactly configs/campaigns/<PACK_ID>",
        )
    relative_text = relative.as_posix()
    if _run_git(repository, "cat-file", "-t", f"HEAD:{relative_text}").strip() != b"tree":
        raise _refuse(
            "reauthor_clean_pack_root_invalid", "pack root is not a committed Git tree"
        )

    plan_path = root / "plan_tree.json"
    sidecar_path = root / "plan_tree.sha256"
    if (
        plan_path.is_symlink()
        or sidecar_path.is_symlink()
        or not plan_path.is_file()
        or not sidecar_path.is_file()
    ):
        raise _refuse(
            "reauthor_clean_pack_identity_invalid",
            "pack lacks regular plan_tree.json and plan_tree.sha256 files",
        )
    try:
        plan_raw = plan_path.read_bytes()
        sidecar_raw = sidecar_path.read_bytes()
        committed_plan = _run_git(repository, "show", f"HEAD:{relative_text}/plan_tree.json")
    except OSError as exc:
        raise _refuse(
            "reauthor_clean_pack_identity_invalid", f"cannot read pack identity: {exc}"
        ) from exc
    if plan_raw != committed_plan:
        raise _refuse(
            "reauthor_clean_pack_identity_invalid",
            "working plan_tree.json differs from committed pack bytes",
        )
    if sidecar_raw != f"{_sha256(plan_raw)}  plan_tree.json\n".encode("ascii"):
        raise _refuse(
            "reauthor_clean_pack_identity_invalid",
            "plan-tree sidecar does not authenticate exact bytes",
        )
    try:
        tree = json.loads(plan_raw)
    except (UnicodeDecodeError, ValueError) as exc:
        raise _refuse(
            "reauthor_clean_pack_identity_invalid", "plan_tree.json is invalid JSON"
        ) from exc
    plan = tree.get("plan") if isinstance(tree, dict) else None
    window = tree.get("window_identity") if isinstance(tree, dict) else None
    if not isinstance(plan, dict) or not isinstance(window, dict):
        raise _refuse(
            "reauthor_clean_pack_identity_invalid", "plan tree omits plan/window identity"
        )
    plan_id = plan.get("plan_id")
    window_id = window.get("window_id")
    if not isinstance(plan_id, str) or not plan_id or not isinstance(window_id, str) or not window_id:
        raise _refuse(
            "reauthor_clean_pack_identity_invalid",
            "plan/window identity must contain nonempty strings",
        )
    generation_match = re.search(r"_v([1-9][0-9]*)$", root.name)
    if generation_match is None:
        raise _refuse(
            "reauthor_clean_pack_identity_invalid",
            "PACK_ID must end in an explicit _v<generation>",
        )
    generation = int(generation_match.group(1))
    freeze_relative = f"{relative_text}/arm_readiness.freeze.receipts/freeze-{generation:04d}.json"
    if freeze_relative in _committed_paths(repository, freeze_relative):
        raise _refuse(
            "reauthor_clean_frozen_pack",
            f"current generation has committed freeze receipt freeze-{generation:04d}.json",
        )
    if freeze_relative + ".sha256" in _committed_paths(repository, freeze_relative + ".sha256"):
        raise _refuse(
            "reauthor_clean_pack_identity_invalid",
            "current generation has a committed orphan freeze sidecar",
        )
    return {
        "pack_id": root.name,
        "generation": generation,
        "canonical_pack_path": str(root),
        "plan_id": plan_id,
        "window_id": window_id,
        "plan_tree_sha256": _sha256(plan_raw),
        "pack_tree_git_oid": _run_git(
            repository, "rev-parse", f"HEAD:{relative_text}"
        ).decode("ascii").strip(),
        "informational_prepare_head": _run_git(repository, "rev-parse", "HEAD")
        .decode("ascii")
        .strip(),
    }


def _prepare_namespace_request(
    pack_identity: Mapping[str, object], namespaces: Sequence[Path]
) -> tuple[Path, dict[str, Path]]:
    if len(namespaces) != len(EXPECTED_NAMESPACES):
        raise _refuse(
            "reauthor_clean_namespace_set_invalid",
            "namespace list must contain the complete three-name T-0 set",
        )
    if any(not path.is_absolute() for path in namespaces):
        raise _refuse(
            "reauthor_clean_namespace_shape_invalid", "every namespace path must be absolute"
        )
    names = [path.name for path in namespaces]
    if len(set(names)) != len(names) or set(names) != EXPECTED_NAMESPACES:
        raise _refuse(
            "reauthor_clean_namespace_set_invalid",
            f"namespace names must be exactly {sorted(EXPECTED_NAMESPACES)!r}",
        )
    parents: set[Path] = set()
    targets: dict[str, Path] = {}
    for supplied in namespaces:
        canonical = _canonical_without_symlink_ancestry(
            supplied, "reauthor_clean_namespace_shape_invalid"
        )
        parent = canonical.parent
        if not parent.is_dir() or parent.is_symlink():
            raise _refuse(
                "reauthor_clean_namespace_missing",
                f"namespace parent is not an existing real directory: {parent}",
            )
        parents.add(parent)
        targets[canonical.name] = canonical
    if len(parents) != 1:
        raise _refuse(
            "reauthor_clean_namespace_shape_invalid",
            "all namespaces must share one custody pack root",
        )
    custody = next(iter(parents))
    if custody.name != pack_identity["pack_id"]:
        raise _refuse(
            "reauthor_clean_namespace_shape_invalid",
            "custody pack root name does not match authenticated PACK_ID",
        )
    return custody, targets


def _anchor(metadata: os.stat_result) -> dict[str, int | None]:
    return {
        "st_dev": metadata.st_dev,
        "st_ino": metadata.st_ino,
        "st_gen": getattr(metadata, "st_gen", None),
    }


def _anchor_matches(metadata: os.stat_result, anchor: Mapping[str, object]) -> bool:
    return _anchor(metadata) == dict(anchor)


def _lstat_path(path: Path) -> os.stat_result:
    return os.stat(path, follow_symlinks=False)


def _validate_namespace_shapes(targets: Mapping[str, Path]) -> None:
    devices: set[int] = set()
    for name in sorted(EXPECTED_NAMESPACES):
        target = targets[name]
        try:
            metadata = _lstat_path(target)
        except FileNotFoundError as exc:
            raise _refuse(
                "reauthor_clean_namespace_missing", f"namespace does not exist: {target}"
            ) from exc
        if not stat.S_ISDIR(metadata.st_mode):
            raise _refuse(
                "reauthor_clean_namespace_shape_invalid",
                f"namespace is not a real directory: {target}",
            )
        devices.add(metadata.st_dev)
        devices.add(_lstat_path(target.parent).st_dev)
    if len(devices) != 1:
        raise _refuse(
            "reauthor_clean_namespace_shape_invalid",
            "namespace quarantine requires same-device atomic rename; EXDEV is refused",
        )


def _ensure_real_directory(path: Path, parent: Path, reason: str) -> None:
    if path.exists() or path.is_symlink():
        try:
            metadata = _lstat_path(path)
        except OSError as exc:
            raise _refuse(reason, f"cannot inspect directory {path}: {exc}") from exc
        if not stat.S_ISDIR(metadata.st_mode):
            raise _refuse(reason, f"path is not a real directory: {path}")
        return
    try:
        path.mkdir(mode=0o700)
        _fsync_directory(parent)
    except OSError as exc:
        raise _refuse("reauthor_clean_io_error", f"cannot create directory {path}: {exc}") from exc


def _fsync_directory(path_or_fd: Path | int) -> None:
    descriptor: int | None = None
    try:
        if isinstance(path_or_fd, int):
            os.fsync(path_or_fd)
        else:
            descriptor = os.open(path_or_fd, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW)
            os.fsync(descriptor)
    except OSError as exc:
        raise _refuse("reauthor_clean_io_error", f"cannot fsync directory: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _load_libc_fchflags() -> object:
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        function = libc.fchflags
        function.argtypes = (ctypes.c_int, ctypes.c_uint)
        function.restype = ctypes.c_int
        return function
    except (AttributeError, OSError) as exc:
        raise _refuse(
            "reauthor_clean_platform_capability_missing",
            f"libc fchflags is unavailable: {exc}",
        ) from exc


def _fchflags(descriptor: int, flags: int) -> None:
    function = _load_libc_fchflags()
    ctypes.set_errno(0)
    if function(descriptor, flags) != 0:  # type: ignore[operator]
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def _descriptor_flags(descriptor: int) -> int:
    metadata = os.fstat(descriptor)
    if not hasattr(metadata, "st_flags"):
        raise _refuse(
            "reauthor_clean_platform_capability_missing",
            "descriptor stat does not expose st_flags",
        )
    return int(metadata.st_flags)  # type: ignore[attr-defined]


def _set_flags_verified(descriptor: int, flags: int) -> None:
    try:
        _fchflags(descriptor, flags)
    except ReauthorCleanError:
        raise
    except OSError as exc:
        raise _refuse(
            "reauthor_clean_platform_capability_missing",
            f"descriptor fchflags({flags:#x}) failed: {exc}",
        ) from exc
    observed = _descriptor_flags(descriptor)
    if observed != flags:
        raise _refuse(
            "reauthor_clean_platform_capability_missing",
            f"fchflags verification mismatch: requested {flags:#x}, observed {observed:#x}",
        )


def _capability_sentinel(operation_root: Path, state_id: str) -> None:
    """Prove set/clear/post-unlink-set/st_flags/cleanup before any rename."""

    root_fd: int | None = None
    file_fd: int | None = None
    name = f".fchflags-sentinel-{state_id}"
    try:
        root_fd = os.open(operation_root, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW)
        file_fd = os.open(
            name, os.O_RDWR | os.O_CREAT | os.O_EXCL | O_NOFOLLOW, 0o600, dir_fd=root_fd
        )
        os.write(file_fd, b"disposable fchflags capability sentinel\n")
        os.fsync(file_fd)
        _set_flags_verified(file_fd, UF_IMMUTABLE)
        _set_flags_verified(file_fd, 0)
        os.unlink(name, dir_fd=root_fd)
        _set_flags_verified(file_fd, UF_IMMUTABLE)
        if os.fstat(file_fd).st_nlink != 0:
            raise _refuse(
                "reauthor_clean_platform_capability_missing",
                "post-unlink sentinel retained a namespace link",
            )
        _set_flags_verified(file_fd, 0)
        os.fsync(root_fd)
    except ReauthorCleanError:
        raise
    except FileExistsError as exc:
        raise _refuse(
            "reauthor_clean_platform_capability_missing",
            f"capability sentinel collision: {name}",
        ) from exc
    except OSError as exc:
        # Best-effort cleanup is attempted below, but no fallback is allowed.
        raise _refuse(
            "reauthor_clean_platform_capability_missing",
            f"post-unlink fchflags capability sentinel failed: {exc}",
        ) from exc
    finally:
        if file_fd is not None:
            try:
                _fchflags(file_fd, 0)
            except Exception:
                pass
            os.close(file_fd)
        if root_fd is not None:
            try:
                os.unlink(name, dir_fd=root_fd)
            except FileNotFoundError:
                pass
            except OSError:
                pass
            os.close(root_fd)


@contextmanager
def _operation_lock(operation_root: Path) -> Iterator[None]:
    path = operation_root / ".lock"
    descriptor: int | None = None
    try:
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise _refuse(
                "reauthor_clean_operation_lock_busy",
                "another re-author cleanup holds the custody operation lock",
            ) from exc
        yield
    finally:
        if descriptor is not None:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            finally:
                os.close(descriptor)


def _publish_no_clobber(
    path: Path,
    raw: bytes,
    *,
    immutable: bool = True,
    fault_prefix: str = "artifact",
) -> str:
    descriptor: int | None = None
    try:
        _fault(f"before_{fault_prefix}_create")
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | O_NOFOLLOW, 0o600)
        view = memoryview(raw)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
        os.fsync(descriptor)
        _fault(f"after_{fault_prefix}_file_fsync")
        if immutable:
            _set_flags_verified(descriptor, UF_IMMUTABLE)
            os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        _fault(f"before_{fault_prefix}_directory_fsync")
        _fsync_directory(path.parent)
        _fault(f"after_{fault_prefix}_directory_fsync")
        return _sha256(raw)
    except FileExistsError as exc:
        raise _refuse(
            "reauthor_clean_output_collision", f"no-clobber artifact already exists: {path}"
        ) from exc
    except ReauthorCleanError:
        raise
    except OSError as exc:
        raise _refuse("reauthor_clean_io_error", f"cannot publish {path}: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _read_canonical_object(path: Path, reason: str) -> tuple[dict[str, object], bytes]:
    try:
        metadata = _lstat_path(path)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError("artifact is not a singly linked regular file")
        flags = getattr(metadata, "st_flags", None)
        if flags not in (0, UF_IMMUTABLE):
            raise ValueError(f"authority artifact has unexpected flags {flags!r}")
        if flags == 0:
            descriptor = os.open(path, os.O_RDONLY | O_NOFOLLOW)
            try:
                _set_flags_verified(descriptor, UF_IMMUTABLE)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            _fsync_directory(path.parent)
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise _refuse(reason, f"cannot read canonical artifact {path}: {exc}") from exc
    if not isinstance(value, dict) or raw != _render_json(value):
        raise _refuse(reason, f"artifact is not canonical JSON: {path}")
    return value, raw


def _manifest_identity_core(manifest: Mapping[str, object]) -> dict[str, object]:
    keys = (
        "schema_version",
        "protocol",
        "nonce",
        "algorithms",
        "pack_identity",
        "custody",
        "request",
        "sources",
    )
    return {key: manifest[key] for key in keys}


def _derive_state_id(identity_core: Mapping[str, object]) -> str:
    return _sha256(STATE_SCHEMA.encode("ascii") + b"\0" + _canonical_json(identity_core))


def _request_record(targets: Mapping[str, Path]) -> list[dict[str, str]]:
    return [{"name": name, "canonical_path": str(targets[name])} for name in sorted(targets)]


def _request_digest(targets: Mapping[str, Path]) -> str:
    return _sha256(_canonical_json(_request_record(targets)))


def _build_manifest(
    pack_identity: Mapping[str, object],
    custody: Path,
    operation_root: Path,
    targets: Mapping[str, Path],
) -> dict[str, object]:
    nonce = secrets.token_bytes(32).hex()
    sources = []
    for name in sorted(targets):
        source = targets[name]
        metadata = _lstat_path(source)
        sources.append(
            {
                "name": name,
                "canonical_path": str(source),
                "parent_anchor": _anchor(_lstat_path(source.parent)),
                "root_anchor": _anchor(metadata),
            }
        )
    identity_core: dict[str, object] = {
        "schema_version": STATE_SCHEMA,
        "protocol": PROTOCOL,
        "nonce": nonce,
        "algorithms": {
            "canonicalization": CANONICALIZATION_ALGORITHM,
            "inventory": INVENTORY_ALGORITHM,
            "payload": PAYLOAD_ALGORITHM,
            "event_chain": EVENT_CHAIN_ALGORITHM,
            "digest": "sha256",
        },
        "pack_identity": dict(pack_identity),
        "custody": {
            "canonical_root_path": str(custody),
            "root_anchor": _anchor(_lstat_path(custody)),
            "canonical_operation_root_path": str(operation_root),
            "operation_root_anchor": _anchor(_lstat_path(operation_root)),
        },
        "request": {
            "exact_sorted_three_names": sorted(EXPECTED_NAMESPACES),
            "entries": _request_record(targets),
            "request_sha256": _request_digest(targets),
        },
        "sources": sources,
    }
    state_id = _derive_state_id(identity_core)
    manifest = dict(identity_core)
    manifest.update(
        {
            "state_id": state_id,
            "expected_quarantine_path": str(
                custody / QUARANTINE_DIRECTORY / state_id
            ),
            "informational_created_at_utc": _utc_now()
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z"),
        }
    )
    return manifest


def _manifest_path(operation_root: Path, state_id: str) -> Path:
    return operation_root / f"state-{state_id}.manifest.json"


def _inventory_path(operation_root: Path, state_id: str) -> Path:
    return operation_root / f"state-{state_id}.inventory.json"


def _receipt_path(operation_root: Path, state_id: str) -> Path:
    return operation_root / f"state-{state_id}.receipt.json"


def _events_path(operation_root: Path, state_id: str) -> Path:
    return operation_root / f"state-{state_id}.events"


def _validate_manifest_file(path: Path) -> tuple[dict[str, object], bytes]:
    manifest, raw = _read_canonical_object(path, "reauthor_clean_state_manifest_invalid")
    try:
        state_id = manifest["state_id"]
        expected_name = f"state-{state_id}.manifest.json"
        derived = _derive_state_id(_manifest_identity_core(manifest))
    except (KeyError, TypeError, ValueError) as exc:
        raise _refuse(
            "reauthor_clean_state_manifest_invalid", f"manifest fields are invalid: {exc}"
        ) from exc
    if (
        manifest.get("schema_version") != STATE_SCHEMA
        or manifest.get("protocol") != PROTOCOL
        or not isinstance(manifest.get("nonce"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", str(manifest.get("nonce")))
        or not isinstance(state_id, str)
        or not re.fullmatch(r"[0-9a-f]{64}", state_id)
        or path.name != expected_name
        or state_id != derived
    ):
        raise _refuse(
            "reauthor_clean_state_manifest_invalid",
            "manifest filename, embedded state ID, schema, nonce, or derivation disagrees",
        )
    return manifest, raw


def _manifest_matches_request(
    manifest: Mapping[str, object],
    pack_identity: Mapping[str, object],
    custody: Path,
    operation_root: Path,
    targets: Mapping[str, Path],
) -> bool:
    recorded_pack = manifest.get("pack_identity")
    if not isinstance(recorded_pack, dict):
        return False
    stable_pack = dict(pack_identity)
    # HEAD is informational; an unrelated movement with the same pack tree is allowed.
    stable_pack["informational_prepare_head"] = recorded_pack.get(
        "informational_prepare_head"
    )
    return (
        recorded_pack == stable_pack
        and manifest.get("request")
        == {
            "exact_sorted_three_names": sorted(EXPECTED_NAMESPACES),
            "entries": _request_record(targets),
            "request_sha256": _request_digest(targets),
        }
        and isinstance(manifest.get("custody"), dict)
        and manifest["custody"].get("canonical_root_path") == str(custody)  # type: ignore[index]
        and manifest["custody"].get("canonical_operation_root_path")  # type: ignore[index]
        == str(operation_root)
    )


def _verify_manifest_binding(
    manifest: Mapping[str, object],
    pack_identity: Mapping[str, object],
    custody: Path,
    operation_root: Path,
    targets: Mapping[str, Path],
) -> None:
    if not _manifest_matches_request(manifest, pack_identity, custody, operation_root, targets):
        raise _refuse(
            "reauthor_clean_state_binding_mismatch",
            "state manifest is foreign, stale, or bound to a different pack/request",
        )
    recorded = manifest["custody"]
    if not _anchor_matches(_lstat_path(custody), recorded["root_anchor"]):  # type: ignore[index]
        raise _refuse(
            "reauthor_clean_state_binding_mismatch", "custody root inode anchor changed"
        )
    if not _anchor_matches(_lstat_path(operation_root), recorded["operation_root_anchor"]):  # type: ignore[index]
        raise _refuse(
            "reauthor_clean_state_binding_mismatch", "operation root inode anchor changed"
        )
    for source in manifest["sources"]:  # type: ignore[index]
        path = Path(source["canonical_path"])
        if not _anchor_matches(_lstat_path(path.parent), source["parent_anchor"]):
            raise _refuse(
                "reauthor_clean_state_binding_mismatch",
                f"source parent inode anchor changed: {path.parent}",
            )


def _event_path(events_root: Path, sequence: int) -> Path:
    return events_root / f"{sequence:08d}.event.json"


def _load_events(events_root: Path, state_id: str) -> list[dict[str, object]]:
    if not events_root.exists():
        return []
    try:
        root_meta = _lstat_path(events_root)
        if not stat.S_ISDIR(root_meta.st_mode):
            raise ValueError("event root is not a directory")
        entries = sorted(events_root.iterdir(), key=lambda item: item.name)
    except (OSError, ValueError) as exc:
        raise _refuse(
            "reauthor_clean_event_chain_invalid", f"cannot inspect event chain: {exc}"
        ) from exc
    events: list[dict[str, object]] = []
    previous = ZERO_EVENT_HASH
    for sequence, path in enumerate(entries, start=1):
        if path.name != f"{sequence:08d}.event.json":
            raise _refuse(
                "reauthor_clean_event_chain_invalid",
                "event filenames are torn, reordered, duplicated, or noncontiguous",
            )
        event, raw = _read_canonical_object(path, "reauthor_clean_event_chain_invalid")
        if (
            event.get("schema_version") != "joulewise.reauthor_clean_event.v1"
            or event.get("state_id") != state_id
            or event.get("sequence") != sequence
            or event.get("prev_event_sha256") != previous
            or not isinstance(event.get("event_type"), str)
            or not isinstance(event.get("data"), dict)
        ):
            raise _refuse(
                "reauthor_clean_event_chain_invalid", f"invalid event link at {path.name}"
            )
        event["event_sha256"] = _sha256(raw)
        events.append(event)
        previous = event["event_sha256"]  # type: ignore[assignment]
    return events


def _publish_event(
    events_root: Path,
    state_id: str,
    event_type: str,
    data: Mapping[str, object],
) -> dict[str, object]:
    events = _load_events(events_root, state_id)
    sequence = len(events) + 1
    event = {
        "schema_version": "joulewise.reauthor_clean_event.v1",
        "state_id": state_id,
        "sequence": sequence,
        "prev_event_sha256": events[-1]["event_sha256"] if events else ZERO_EVENT_HASH,
        "event_type": event_type,
        "data": dict(data),
    }
    raw = _render_json(event)
    digest = _publish_no_clobber(
        _event_path(events_root, sequence),
        raw,
        fault_prefix=f"event_{event_type.lower()}",
    )
    event["event_sha256"] = digest
    return event


def _event_for(
    events: Sequence[Mapping[str, object]], event_type: str, path: str | None = None
) -> Mapping[str, object] | None:
    found = []
    for event in events:
        if event.get("event_type") != event_type:
            continue
        data = event.get("data")
        if path is not None and (not isinstance(data, dict) or data.get("path") != path):
            continue
        found.append(event)
    if len(found) > 1:
        raise _refuse(
            "reauthor_clean_event_chain_invalid",
            f"duplicate {event_type} event for {path or 'state'}",
        )
    return found[0] if found else None


def _open_directory(path: Path) -> int:
    try:
        return os.open(path, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW)
    except OSError as exc:
        raise _refuse("reauthor_clean_io_error", f"cannot open directory {path}: {exc}") from exc


def _source_records(manifest: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    return {item["name"]: item for item in manifest["sources"]}  # type: ignore[index]


def _create_quarantine(custody: Path, manifest: Mapping[str, object]) -> Path:
    root = custody / QUARANTINE_DIRECTORY
    _ensure_real_directory(root, custody, "reauthor_clean_quarantine_invalid")
    active = Path(str(manifest["expected_quarantine_path"]))
    if active.exists() or active.is_symlink():
        return active
    try:
        active.mkdir(mode=0o700)
        _fsync_directory(root)
    except OSError as exc:
        raise _refuse("reauthor_clean_io_error", f"cannot create quarantine: {exc}") from exc
    return active


def _prepared_event(
    manifest: Mapping[str, object], operation_root: Path, active: Path
) -> None:
    state_id = str(manifest["state_id"])
    events_root = _events_path(operation_root, state_id)
    events = _load_events(events_root, state_id)
    existing = _event_for(events, "PREPARED")
    anchor = _anchor(_lstat_path(active))
    if existing is not None:
        if existing["data"].get("quarantine_anchor") != anchor:  # type: ignore[index]
            raise _refuse(
                "reauthor_clean_state_binding_mismatch", "quarantine inode anchor changed"
            )
        return
    _capability_sentinel(operation_root, state_id)
    _publish_event(events_root, state_id, "PREPARED", {"quarantine_anchor": anchor})


def _quarantine_sources(
    manifest: Mapping[str, object],
    custody: Path,
    operation_root: Path,
    active: Path,
) -> None:
    state_id = str(manifest["state_id"])
    events_root = _events_path(operation_root, state_id)
    records = _source_records(manifest)
    prepared = _event_for(_load_events(events_root, state_id), "PREPARED")
    if prepared is None or prepared["data"].get("quarantine_anchor") != _anchor(_lstat_path(active)):  # type: ignore[index]
        raise _refuse(
            "reauthor_clean_state_binding_mismatch", "quarantine PREPARED anchor is missing"
        )
    for name in sorted(EXPECTED_NAMESPACES):
        source = Path(records[name]["canonical_path"])
        destination = active / name
        source_exists = source.exists() or source.is_symlink()
        destination_exists = destination.exists() or destination.is_symlink()
        events = _load_events(events_root, state_id)
        root_verified = _event_for(events, "DELETE_VERIFIED", name) is not None
        if source_exists and destination_exists:
            raise _refuse(
                "reauthor_clean_state_binding_mismatch",
                f"source was recreated while quarantined: {name}",
            )
        if not source_exists and not destination_exists:
            if root_verified:
                continue
            raise _refuse(
                "reauthor_clean_state_binding_mismatch",
                f"source exists in neither allowed split-rename location: {name}",
            )
        candidate = destination if destination_exists else source
        metadata = _lstat_path(candidate)
        if not stat.S_ISDIR(metadata.st_mode) or not _anchor_matches(metadata, records[name]["root_anchor"]):
            raise _refuse(
                "reauthor_clean_state_binding_mismatch",
                f"source inode anchor/shape changed: {name}",
            )
        if source_exists:
            _fault(f"before_rename_{name}")
            source_parent_fd: int | None = None
            destination_parent_fd: int | None = None
            try:
                source_parent_fd = os.open(
                    custody, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW
                )
                destination_parent_fd = os.open(
                    active, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW
                )
                os.rename(
                    source.name,
                    destination.name,
                    src_dir_fd=source_parent_fd,
                    dst_dir_fd=destination_parent_fd,
                )
            except OSError as exc:
                if exc.errno == errno.EXDEV:
                    raise _refuse(
                        "reauthor_clean_namespace_shape_invalid",
                        "same-device quarantine rename returned EXDEV",
                    ) from exc
                raise _refuse(
                    "reauthor_clean_io_error", f"cannot quarantine {source}: {exc}"
                ) from exc
            finally:
                if source_parent_fd is not None:
                    os.close(source_parent_fd)
                if destination_parent_fd is not None:
                    os.close(destination_parent_fd)
            _fault(f"after_rename_{name}")
            _fault(f"before_source_parent_fsync_{name}")
            _fsync_directory(custody)
            _fault(f"after_source_parent_fsync_{name}")
            _fault(f"before_quarantine_parent_fsync_{name}")
            _fsync_directory(active)
            _fault(f"after_quarantine_parent_fsync_{name}")
        events = _load_events(events_root, state_id)
        event = _event_for(events, "RENAME_VERIFIED", name)
        data = {
            "path": name,
            "source_path": str(source),
            "quarantine_path": str(destination),
            "inode_anchor": dict(records[name]["root_anchor"]),
        }
        if event is None:
            _publish_event(events_root, state_id, "RENAME_VERIFIED", data)
        elif event["data"] != data:
            raise _refuse(
                "reauthor_clean_event_chain_invalid", f"rename event mismatch: {name}"
            )


def _xattrs(descriptor: int) -> list[dict[str, str]]:
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        flistxattr = libc.flistxattr
        fgetxattr = libc.fgetxattr
        flistxattr.argtypes = (
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_int,
        )
        flistxattr.restype = ctypes.c_ssize_t
        fgetxattr.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.c_int,
        )
        fgetxattr.restype = ctypes.c_ssize_t
        size = flistxattr(descriptor, None, 0, 0)
        if size < 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))
        if size:
            name_buffer = ctypes.create_string_buffer(size)
            observed = flistxattr(descriptor, name_buffer, size, 0)
            if observed != size:
                error = ctypes.get_errno()
                raise OSError(error or errno.EIO, "unstable extended-attribute list")
            name_bytes = name_buffer.raw[:size].split(b"\0")
            names = [raw.decode("utf-8", errors="strict") for raw in name_bytes if raw]
        else:
            names = []
        result = []
        for name in sorted(names):
            name.encode("utf-8", errors="strict")
            encoded = name.encode("utf-8")
            value_size = fgetxattr(descriptor, encoded, None, 0, 0, 0)
            if value_size < 0:
                error = ctypes.get_errno()
                raise OSError(error, os.strerror(error))
            value_buffer = ctypes.create_string_buffer(value_size or 1)
            observed = fgetxattr(
                descriptor, encoded, value_buffer, value_size, 0, 0
            )
            if observed != value_size:
                error = ctypes.get_errno()
                raise OSError(error or errno.EIO, "unstable extended attribute")
            result.append(
                {"name": name, "value_hex": value_buffer.raw[:value_size].hex()}
            )
        return result
    except (AttributeError, OSError, UnicodeError) as exc:
        raise _refuse(
            "reauthor_clean_extended_attribute_unreadable",
            f"cannot read complete extended attributes/resource fork: {exc}",
        ) from exc


def _stable_metadata(metadata: os.stat_result) -> tuple[object, ...]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        getattr(metadata, "st_gen", None),
        metadata.st_mode,
        metadata.st_uid,
        metadata.st_gid,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
        getattr(metadata, "st_flags", None),
        metadata.st_nlink,
    )


def _hash_fd(descriptor: int) -> tuple[str, int]:
    digest = hashlib.sha256()
    offset = 0
    while True:
        block = os.pread(descriptor, 1024 * 1024, offset)
        if not block:
            break
        digest.update(block)
        offset += len(block)
    return digest.hexdigest(), offset


def _payload_record(
    descriptor: int,
    relative: str,
    kind: str,
    *,
    children: Sequence[str] = (),
) -> dict[str, object]:
    relative.encode("utf-8", errors="strict")
    before = os.fstat(descriptor)
    flags = _descriptor_flags(descriptor)
    common: dict[str, object] = {
        "path": relative,
        "type": kind,
        "mode": stat.S_IMODE(before.st_mode),
        "uid": before.st_uid,
        "gid": before.st_gid,
        "flags": flags,
        "xattrs": _xattrs(descriptor),
    }
    if kind == "file":
        content_sha, size = _hash_fd(descriptor)
        common.update({"size": size, "content_sha256": content_sha})
    else:
        common["children"] = list(children)
    after = os.fstat(descriptor)
    if _stable_metadata(before) != _stable_metadata(after):
        raise _refuse(
            "reauthor_clean_concurrent_mutation", f"unstable double-stat/hash: {relative}"
        )
    return common


def _open_child(parent_fd: int, name: str, is_directory: bool) -> int:
    flags = os.O_RDONLY | O_NOFOLLOW | (O_DIRECTORY if is_directory else 0)
    try:
        return os.open(name, flags, dir_fd=parent_fd)
    except OSError as exc:
        raise _refuse(
            "reauthor_clean_concurrent_mutation", f"cannot descriptor-open {name}: {exc}"
        ) from exc


def _scan_tree(
    directory_fd: int,
    prefix: str,
    visitor: Callable[[int, str, str, list[str], os.stat_result], None],
) -> None:
    try:
        names = sorted(os.listdir(directory_fd))
    except OSError as exc:
        raise _refuse(
            "reauthor_clean_namespace_inventory_invalid", f"cannot list frozen tree: {exc}"
        ) from exc
    for name in names:
        try:
            name.encode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise _refuse(
                "reauthor_clean_entry_type_unsupported", "non-UTF-8 namespace name"
            ) from exc
        relative = f"{prefix}/{name}" if prefix else name
        metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISLNK(metadata.st_mode) or not (
            stat.S_ISDIR(metadata.st_mode) or stat.S_ISREG(metadata.st_mode)
        ):
            raise _refuse(
                "reauthor_clean_entry_type_unsupported",
                f"symlink or special entry is unsupported: {relative}",
            )
        if stat.S_ISREG(metadata.st_mode) and metadata.st_nlink != 1:
            raise _refuse(
                "reauthor_clean_hardlink_unsupported", f"hard-linked file: {relative}"
            )
        child_fd = _open_child(directory_fd, name, stat.S_ISDIR(metadata.st_mode))
        try:
            child_names: list[str] = []
            if stat.S_ISDIR(metadata.st_mode):
                child_names = sorted(os.listdir(child_fd))
                _scan_tree(child_fd, relative, visitor)
            visitor(
                child_fd,
                relative,
                "directory" if stat.S_ISDIR(metadata.st_mode) else "file",
                child_names,
                metadata,
            )
        finally:
            os.close(child_fd)


def _preflight_flags_and_freeze(active: Path, operation_root: Path, state_id: str) -> None:
    events_root = _events_path(operation_root, state_id)
    events = _load_events(events_root, state_id)
    freeze_intent = _event_for(events, "FREEZE_INTENT")
    root_fd = _open_directory(active)
    try:
        if freeze_intent is None:
            def check(fd: int, relative: str, _kind: str, _children: list[str], _meta: os.stat_result) -> None:
                if _descriptor_flags(fd) != 0:
                    raise _refuse(
                        "reauthor_clean_namespace_inventory_invalid",
                        f"pre-existing conflicting flags on {relative}",
                    )

            _scan_tree(root_fd, "", check)
            if _descriptor_flags(root_fd) != 0:
                raise _refuse(
                    "reauthor_clean_namespace_inventory_invalid",
                    "pre-existing conflicting flags on quarantine root",
                )
            _publish_event(events_root, state_id, "FREEZE_INTENT", {})

        def freeze(fd: int, relative: str, _kind: str, _children: list[str], _meta: os.stat_result) -> None:
            flags = _descriptor_flags(fd)
            if flags not in (0, UF_IMMUTABLE):
                raise _refuse(
                    "reauthor_clean_namespace_inventory_invalid",
                    f"unexpected flag while freezing {relative}: {flags:#x}",
                )
            _set_flags_verified(fd, UF_IMMUTABLE)

        _scan_tree(root_fd, "", freeze)
        root_flags = _descriptor_flags(root_fd)
        if root_flags not in (0, UF_IMMUTABLE):
            raise _refuse(
                "reauthor_clean_namespace_inventory_invalid", "unexpected quarantine-root flags"
            )
        _set_flags_verified(root_fd, UF_IMMUTABLE)
        os.fsync(root_fd)
        _fault("after_freeze_before_inventory")
    finally:
        os.close(root_fd)


def _inventory_tree(active: Path, manifest: Mapping[str, object]) -> dict[str, object]:
    objects: list[dict[str, object]] = []
    root_fd = _open_directory(active)
    try:
        def collect(fd: int, relative: str, kind: str, children: list[str], metadata: os.stat_result) -> None:
            if _descriptor_flags(fd) != UF_IMMUTABLE:
                raise _refuse(
                    "reauthor_clean_state_inventory_mismatch",
                    f"immutability wall is absent: {relative}",
                )
            payload = _payload_record(fd, relative, kind, children=children)
            deletion_payload = dict(payload)
            if kind == "directory":
                deletion_payload["children"] = []
            objects.append(
                {
                    "path": relative,
                    "type": kind,
                    "inode_anchor": _anchor(metadata),
                    "inventory_payload": payload,
                    "inventory_payload_sha256": _sha256(_canonical_json(payload)),
                    "authorized_deletion_payload_sha256": _sha256(
                        _canonical_json(deletion_payload)
                    ),
                }
            )

        _scan_tree(root_fd, "", collect)
    finally:
        os.close(root_fd)
    objects.sort(key=lambda item: str(item["path"]))
    return {
        "schema_version": "joulewise.reauthor_clean_inventory.v3",
        "state_id": manifest["state_id"],
        "inventory_algorithm": INVENTORY_ALGORITHM,
        "payload_algorithm": PAYLOAD_ALGORITHM,
        "object_count": len(objects),
        "objects": objects,
    }


def _authorize_inventory(
    active: Path, manifest: Mapping[str, object], operation_root: Path
) -> tuple[dict[str, object], bytes]:
    state_id = str(manifest["state_id"])
    path = _inventory_path(operation_root, state_id)
    events_root = _events_path(operation_root, state_id)
    events = _load_events(events_root, state_id)
    authorization = _event_for(events, "DELETE_AUTHORIZED")
    if path.exists():
        inventory, raw = _read_canonical_object(
            path, "reauthor_clean_state_inventory_mismatch"
        )
        recomputed = _inventory_tree(active, manifest)
        if inventory != recomputed:
            raise _refuse(
                "reauthor_clean_state_inventory_mismatch",
                "frozen inventory differs before deletion authorization",
            )
    else:
        inventory = _inventory_tree(active, manifest)
        raw = _render_json(inventory)
        _publish_no_clobber(path, raw, fault_prefix="inventory")
    expected_data = {
        "inventory_path": str(path),
        "inventory_sha256": _sha256(raw),
        "object_count": inventory["object_count"],
    }
    if authorization is None:
        _publish_event(events_root, state_id, "DELETE_AUTHORIZED", expected_data)
    elif authorization["data"] != expected_data:
        raise _refuse(
            "reauthor_clean_event_chain_invalid", "authorization event does not bind inventory"
        )
    return inventory, raw


def _load_authorized_inventory(
    active: Path, manifest: Mapping[str, object], operation_root: Path
) -> tuple[dict[str, object], bytes]:
    state_id = str(manifest["state_id"])
    path = _inventory_path(operation_root, state_id)
    inventory, raw = _read_canonical_object(path, "reauthor_clean_state_inventory_mismatch")
    events = _load_events(_events_path(operation_root, state_id), state_id)
    authorization = _event_for(events, "DELETE_AUTHORIZED")
    if authorization is None or authorization["data"] != {
        "inventory_path": str(path),
        "inventory_sha256": _sha256(raw),
        "object_count": inventory.get("object_count"),
    }:
        raise _refuse(
            "reauthor_clean_event_chain_invalid", "inventory lacks exact authorization event"
        )
    objects = _object_map(inventory)
    for event in events:
        if event.get("event_type") == "DELETE_MISMATCH":
            relative = event["data"].get("path")  # type: ignore[index]
            if not isinstance(relative, str) or relative not in objects:
                raise _refuse(
                    "reauthor_clean_event_chain_invalid",
                    "mismatch event names an unknown inventory object",
                )
            raise _destroyed_mismatch_error(
                manifest, operation_root, inventory, events, relative
            )
    active_fd = _open_directory(active)
    try:
        for event in events:
            if event.get("event_type") != "DELETE_INTENT":
                continue
            relative = event["data"].get("path")  # type: ignore[index]
            if not isinstance(relative, str) or relative not in objects:
                raise _refuse(
                    "reauthor_clean_event_chain_invalid",
                    "delete intent names an unknown inventory object",
                )
            if _event_for(events, "DELETE_VERIFIED", relative) is None and _event_for(
                events, "DELETE_MISMATCH", relative
            ) is None:
                current = _path_stat(active_fd, relative)
                if current is None:
                    raise _destroyed_unverified_error(
                        active,
                        inventory,
                        events,
                        relative,
                        operation_root=operation_root,
                        manifest=manifest,
                    )
                item = objects[relative]
                if not _anchor_matches(current, item["inode_anchor"]):
                    raise _refuse(
                        "reauthor_clean_concurrent_mutation",
                        f"intent target inode changed while thawed: {relative}",
                    )
                parent_relative, name = _parent_and_name(relative)
                parent_fd = (
                    os.dup(active_fd)
                    if not parent_relative
                    else _open_relative(active_fd, parent_relative, True)
                )
                object_fd = _open_child(
                    parent_fd, name, item["type"] == "directory"
                )
                try:
                    if _descriptor_flags(object_fd) not in (0, UF_IMMUTABLE):
                        raise _refuse(
                            "reauthor_clean_concurrent_mutation",
                            f"intent target gained unexpected flags: {relative}",
                        )
                    if _descriptor_flags(parent_fd) not in (0, UF_IMMUTABLE):
                        raise _refuse(
                            "reauthor_clean_concurrent_mutation",
                            f"intent parent gained unexpected flags: {relative}",
                        )
                    _set_flags_verified(object_fd, UF_IMMUTABLE)
                    _set_flags_verified(parent_fd, UF_IMMUTABLE)
                    os.fsync(parent_fd)
                finally:
                    os.close(object_fd)
                    os.close(parent_fd)
    finally:
        os.close(active_fd)
    _verify_remaining_projection(
        active, inventory, events, manifest=manifest, operation_root=operation_root
    )
    return inventory, raw


def _object_map(inventory: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    objects = inventory.get("objects")
    if not isinstance(objects, list) or inventory.get("object_count") != len(objects):
        raise _refuse(
            "reauthor_clean_state_inventory_mismatch", "inventory object list/count is invalid"
        )
    result: dict[str, Mapping[str, object]] = {}
    for item in objects:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or item["path"] in result:
            raise _refuse(
                "reauthor_clean_state_inventory_mismatch", "inventory paths collide"
            )
        result[item["path"]] = item
    return result


def _verified_paths(events: Sequence[Mapping[str, object]]) -> set[str]:
    paths: set[str] = set()
    for event in events:
        if event.get("event_type") == "DELETE_VERIFIED":
            path = event["data"].get("path")  # type: ignore[index]
            if not isinstance(path, str) or path in paths:
                raise _refuse(
                    "reauthor_clean_event_chain_invalid", "duplicate/invalid verified path"
                )
            paths.add(path)
    return paths


def _path_stat(active_fd: int, relative: str) -> os.stat_result | None:
    try:
        return os.stat(relative, dir_fd=active_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None


def _open_relative(active_fd: int, relative: str, is_directory: bool) -> int:
    flags = os.O_RDONLY | O_NOFOLLOW | (O_DIRECTORY if is_directory else 0)
    try:
        return os.open(relative, flags, dir_fd=active_fd)
    except OSError as exc:
        raise _refuse(
            "reauthor_clean_state_inventory_mismatch",
            f"cannot open remaining object {relative}: {exc}",
        ) from exc


def _verify_remaining_projection(
    active: Path,
    inventory: Mapping[str, object],
    events: Sequence[Mapping[str, object]],
    *,
    manifest: Mapping[str, object],
    operation_root: Path,
) -> None:
    objects = _object_map(inventory)
    verified = _verified_paths(events)
    if not verified.issubset(objects):
        raise _refuse(
            "reauthor_clean_event_chain_invalid", "verified event names an unknown object"
        )
    active_fd = _open_directory(active)
    try:
        for relative, item in objects.items():
            metadata = _path_stat(active_fd, relative)
            if relative in verified:
                if metadata is not None:
                    raise _refuse(
                        "reauthor_clean_state_inventory_mismatch",
                        f"verified object reappeared: {relative}",
                    )
                continue
            if metadata is None or not _anchor_matches(metadata, item["inode_anchor"]):
                intent = _event_for(events, "DELETE_INTENT", relative)
                if intent is not None:
                    raise _destroyed_unverified_error(
                        active,
                        inventory,
                        events,
                        relative,
                        operation_root=operation_root,
                        manifest=manifest,
                    )
                raise _refuse(
                    "reauthor_clean_state_inventory_mismatch",
                    f"unattributed missing/replaced remaining object: {relative}",
                )
            kind = item["type"]
            if kind == "file" and (not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1):
                raise _refuse(
                    "reauthor_clean_state_inventory_mismatch", f"remaining file shape changed: {relative}"
                )
            if kind == "directory" and not stat.S_ISDIR(metadata.st_mode):
                raise _refuse(
                    "reauthor_clean_state_inventory_mismatch", f"remaining directory shape changed: {relative}"
                )
            fd = _open_relative(active_fd, relative, kind == "directory")
            try:
                expected = dict(item["inventory_payload"])
                if kind == "directory":
                    direct_verified = {
                        path.rsplit("/", 1)[-1]
                        for path in verified
                        if path.rpartition("/")[0] == relative
                    }
                    expected["children"] = [
                        child for child in expected["children"] if child not in direct_verified
                    ]
                    observed_children = sorted(os.listdir(fd))
                else:
                    observed_children = []
                observed = _payload_record(fd, relative, str(kind), children=observed_children)
                if observed != expected:
                    raise _refuse(
                        "reauthor_clean_state_inventory_mismatch",
                        f"remaining frozen projection differs: {relative}",
                    )
            finally:
                os.close(fd)
    finally:
        os.close(active_fd)


def _parent_and_name(relative: str) -> tuple[str, str]:
    parent, _, name = relative.rpartition("/")
    return parent, name


def _delete_order(objects: Mapping[str, Mapping[str, object]]) -> list[str]:
    return sorted(objects, key=lambda path: (-path.count("/"), 0 if objects[path]["type"] == "file" else 1, path))


def _parent_expected_children(
    inventory: Mapping[str, object], events: Sequence[Mapping[str, object]], parent: str
) -> list[str]:
    objects = _object_map(inventory)
    verified = _verified_paths(events)
    parent_item = objects.get(parent)
    if parent_item is None:
        # The active quarantine root is outside the authorized object inventory.
        roots = sorted(path for path in objects if "/" not in path and path not in verified)
        return roots
    children = list(parent_item["inventory_payload"]["children"])  # type: ignore[index]
    return [
        name
        for name in children
        if f"{parent}/{name}" not in verified
    ]


def _delete_one(
    active: Path,
    manifest: Mapping[str, object],
    operation_root: Path,
    inventory: Mapping[str, object],
    relative: str,
) -> None:
    state_id = str(manifest["state_id"])
    events_root = _events_path(operation_root, state_id)
    events = _load_events(events_root, state_id)
    item = _object_map(inventory)[relative]
    if _event_for(events, "DELETE_VERIFIED", relative) is not None:
        return
    mismatch = _event_for(events, "DELETE_MISMATCH", relative)
    if mismatch is not None:
        raise _destroyed_mismatch_error(manifest, operation_root, inventory, events, relative)
    parent_relative, name = _parent_and_name(relative)
    active_fd = _open_directory(active)
    parent_fd: int | None = None
    object_fd: int | None = None
    try:
        parent_fd = os.dup(active_fd) if not parent_relative else _open_relative(active_fd, parent_relative, True)
        current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if not _anchor_matches(current, item["inode_anchor"]):
            raise _refuse(
                "reauthor_clean_concurrent_mutation", f"target replacement before open: {relative}"
            )
        is_directory = item["type"] == "directory"
        object_fd = _open_child(parent_fd, name, is_directory)
        if not _anchor_matches(os.fstat(object_fd), item["inode_anchor"]):
            raise _refuse(
                "reauthor_clean_concurrent_mutation", f"target inode changed at open: {relative}"
            )
        children = sorted(os.listdir(object_fd)) if is_directory else []
        payload = _payload_record(object_fd, relative, str(item["type"]), children=children)
        expected_payload = dict(item["inventory_payload"])
        if is_directory:
            expected_payload["children"] = []
        if payload != expected_payload:
            raise _refuse(
                "reauthor_clean_concurrent_mutation", f"payload changed before unlink: {relative}"
            )
        expected_parent_before = _parent_expected_children(inventory, events, parent_relative)
        if sorted(os.listdir(parent_fd)) != expected_parent_before:
            raise _refuse(
                "reauthor_clean_concurrent_mutation", f"parent child-set changed: {relative}"
            )
        intent = _event_for(events, "DELETE_INTENT", relative)
        intent_data = {
            "path": relative,
            "inode_anchor": dict(item["inode_anchor"]),
            "authorized_payload_sha256": item["authorized_deletion_payload_sha256"],
        }
        if intent is None:
            intent = _publish_event(events_root, state_id, "DELETE_INTENT", intent_data)
        elif intent["data"] != intent_data:
            raise _refuse(
                "reauthor_clean_event_chain_invalid", f"delete intent mismatch: {relative}"
            )
        _fault(f"after_intent_before_thaw:{relative}")
        _set_flags_verified(object_fd, 0)
        parent_flags = _descriptor_flags(parent_fd)
        if parent_flags == UF_IMMUTABLE:
            _set_flags_verified(parent_fd, 0)
        elif parent_relative and parent_flags != 0:
            raise _refuse(
                "reauthor_clean_concurrent_mutation", f"parent flags changed: {relative}"
            )
        _fault(f"after_thaw_before_unlink:{relative}")
        latest = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if not _anchor_matches(latest, item["inode_anchor"]):
            raise _refuse(
                "reauthor_clean_concurrent_mutation", f"target replacement before unlink: {relative}"
            )
        _fault(f"before_unlink:{relative}")
        if is_directory:
            os.rmdir(name, dir_fd=parent_fd)
        else:
            os.unlink(name, dir_fd=parent_fd)
        _fault(f"after_unlink_before_parent_freeze:{relative}")
        _set_flags_verified(parent_fd, UF_IMMUTABLE)
        _fault(f"before_delete_parent_fsync:{relative}")
        os.fsync(parent_fd)
        _fault(f"after_delete_parent_fsync:{relative}")
        events_after_unlink = _load_events(events_root, state_id)
        expected_parent_after = _parent_expected_children(
            inventory, events_after_unlink, parent_relative
        )
        # Current object has no verified event yet, so subtract it explicitly.
        expected_parent_after = [child for child in expected_parent_after if child != name]
        if sorted(os.listdir(parent_fd)) != expected_parent_after:
            events = _load_events(events_root, state_id)
            raise _destroyed_unverified_error(
                active,
                inventory,
                events,
                relative,
                operation_root=operation_root,
                manifest=manifest,
            )
        if is_directory:
            final_hash = str(item["authorized_deletion_payload_sha256"])
        else:
            _fault(f"after_unlink_before_postunlink_freeze:{relative}")
            _set_flags_verified(object_fd, UF_IMMUTABLE)
            if os.fstat(object_fd).st_nlink != 0:
                raise _refuse(
                    "reauthor_clean_destroyed_mismatch",
                    f"unlinked file still has namespace links: {relative}",
                )
            final_payload = _payload_record(object_fd, relative, "file")
            final_hash = _sha256(_canonical_json(final_payload))
        verified_data = {
            "path": relative,
            "inode_anchor": dict(item["inode_anchor"]),
            "authorized_payload_sha256": item["authorized_deletion_payload_sha256"],
            "final_held_fd_payload_sha256": final_hash,
            "intent_event_sha256": intent["event_sha256"],
        }
        if final_hash != item["authorized_deletion_payload_sha256"]:
            mismatch_event = _publish_event(
                events_root,
                state_id,
                "DELETE_MISMATCH",
                verified_data,
            )
            events = _load_events(events_root, state_id)
            raise _destroyed_mismatch_error(
                manifest, operation_root, inventory, events, relative
            )
        _fault(f"after_postunlink_hash_before_event:{relative}")
        _publish_event(events_root, state_id, "DELETE_VERIFIED", verified_data)
    except FileNotFoundError:
        events = _load_events(events_root, state_id)
        if _event_for(events, "DELETE_INTENT", relative) is not None:
            raise _destroyed_unverified_error(
                active, inventory, events, relative, operation_root=operation_root, manifest=manifest
            )
        raise _refuse(
            "reauthor_clean_state_inventory_mismatch", f"object vanished without intent: {relative}"
        )
    except ReauthorCleanError:
        raise
    except OSError as exc:
        raise _refuse(
            "reauthor_clean_io_error", f"descriptor deletion failed for {relative}: {exc}"
        ) from exc
    finally:
        if object_fd is not None:
            os.close(object_fd)
        if parent_fd is not None:
            os.close(parent_fd)
        os.close(active_fd)


def _remaining_verified(
    active: Path, inventory: Mapping[str, object], events: Sequence[Mapping[str, object]]
) -> list[dict[str, object]]:
    objects = _object_map(inventory)
    removed = _verified_paths(events)
    for event in events:
        if event.get("event_type") not in {"DELETE_INTENT", "DELETE_MISMATCH"}:
            continue
        relative = event["data"].get("path")  # type: ignore[index]
        if isinstance(relative, str) and not (active / relative).exists():
            removed.add(relative)
    result: list[dict[str, object]] = []
    try:
        active_fd = _open_directory(active)
        try:
            for relative, item in sorted(objects.items()):
                metadata = _path_stat(active_fd, relative)
                if relative in removed:
                    if metadata is not None:
                        return []
                    continue
                if metadata is None or not _anchor_matches(
                    metadata, item["inode_anchor"]
                ):
                    return []
                kind = str(item["type"])
                fd = _open_relative(active_fd, relative, kind == "directory")
                try:
                    expected = dict(item["inventory_payload"])
                    children: list[str] = []
                    if kind == "directory":
                        expected["children"] = [
                            child
                            for child in expected["children"]
                            if f"{relative}/{child}" not in removed
                        ]
                        children = sorted(os.listdir(fd))
                    observed = _payload_record(
                        fd, relative, kind, children=children
                    )
                    if observed != expected:
                        return []
                finally:
                    os.close(fd)
                result.append(
                    {
                        "path": relative,
                        "inode_anchor": item["inode_anchor"],
                        "authorized_payload_sha256": item[
                            "authorized_deletion_payload_sha256"
                        ],
                    }
                )
        finally:
            os.close(active_fd)
    except (OSError, ReauthorCleanError):
        return []
    return result


def _refreeze_incident_parent(active: Path, relative: str) -> None:
    parent_relative, _name = _parent_and_name(relative)
    active_fd = _open_directory(active)
    parent_fd: int | None = None
    try:
        parent_fd = (
            os.dup(active_fd)
            if not parent_relative
            else _open_relative(active_fd, parent_relative, True)
        )
        flags = _descriptor_flags(parent_fd)
        if flags == 0:
            _set_flags_verified(parent_fd, UF_IMMUTABLE)
            os.fsync(parent_fd)
        elif flags != UF_IMMUTABLE:
            raise _refuse(
                "reauthor_clean_concurrent_mutation",
                f"incident parent has unexpected flags: {parent_relative or '.'}",
            )
    finally:
        if parent_fd is not None:
            os.close(parent_fd)
        os.close(active_fd)


def _receipt_document(
    manifest: Mapping[str, object],
    operation_root: Path,
    inventory: Mapping[str, object],
    events: Sequence[Mapping[str, object]],
    *,
    status: str,
    destroyed_unverified: Sequence[Mapping[str, object]] = (),
    destroyed_mismatch: Sequence[Mapping[str, object]] = (),
    observed_missing_unattributed: Sequence[str] = (),
    reason_codes: Sequence[str] = (),
) -> dict[str, object]:
    verified_events = [event for event in events if event["event_type"] == "DELETE_VERIFIED"]
    destroyed_verified = []
    for event in verified_events:
        data = event["data"]
        destroyed_verified.append(
            {
                "path": data["path"],
                "inode_anchor": data["inode_anchor"],
                "authorized_payload_sha256": data["authorized_payload_sha256"],
                "final_held_fd_payload_sha256": data["final_held_fd_payload_sha256"],
                "verification_event_sha256": event["event_sha256"],
            }
        )
    inventory_raw = _render_json(inventory)
    state_id = str(manifest["state_id"])
    manifest_raw = _render_json(manifest)
    active = Path(str(manifest["expected_quarantine_path"]))
    return {
        "schema_version": RECEIPT_SCHEMA,
        "receipt_kind": "reauthor_clean_deletion_custody",
        "status": status,
        "completion": "COMPLETE" if status == "COMPLETE_VERIFIED" else "INCOMPLETE",
        "deletion_semantics": "logical_namespace_unlink_not_secure_erase",
        "claim": "VERIFIED LOGICAL NAMESPACE DELETION",
        "truth_boundary": "not secure erase and not hostile-process exclusion",
        "state_manifest": {
            "path": str(_manifest_path(operation_root, state_id)),
            "sha256": _sha256(manifest_raw),
            "state_id": state_id,
        },
        "pack_identity": manifest["pack_identity"],
        "request_sha256": manifest["request"]["request_sha256"],  # type: ignore[index]
        "inventory": {
            "path": str(_inventory_path(operation_root, state_id)),
            "sha256": _sha256(inventory_raw),
            "object_count": inventory["object_count"],
        },
        "event_count": len(events),
        "event_chain_head_sha256": events[-1]["event_sha256"] if events else ZERO_EVENT_HASH,
        "destroyed_verified": sorted(destroyed_verified, key=lambda item: item["path"]),
        "destroyed_unverified": list(destroyed_unverified),
        "destroyed_mismatch": list(destroyed_mismatch),
        "remaining_verified": _remaining_verified(active, inventory, events)
        if active.exists()
        else [],
        "observed_missing_unattributed": list(observed_missing_unattributed),
        "reason_codes": list(reason_codes),
    }


def _publish_or_verify_receipt(
    manifest: Mapping[str, object], operation_root: Path, document: Mapping[str, object]
) -> tuple[Path, bytes]:
    path = _receipt_path(operation_root, str(manifest["state_id"]))
    expected = _render_json(document)
    if path.exists() or path.is_symlink():
        _existing, raw = _read_canonical_object(path, "reauthor_clean_event_chain_invalid")
        if raw != expected:
            raise _refuse(
                "reauthor_clean_event_chain_invalid", "terminal receipt replay is nondeterministic"
            )
        return path, raw
    _publish_no_clobber(path, expected, fault_prefix="terminal_receipt")
    return path, expected


def _destroyed_unverified_error(
    active: Path,
    inventory: Mapping[str, object],
    events: Sequence[Mapping[str, object]],
    relative: str,
    *,
    operation_root: Path,
    manifest: Mapping[str, object] | None = None,
) -> ReauthorCleanError:
    if manifest is None:
        state_id = str(inventory["state_id"])
        manifest, _raw = _validate_manifest_file(_manifest_path(operation_root, state_id))
    item = _object_map(inventory)[relative]
    intent = _event_for(events, "DELETE_INTENT", relative)
    try:
        _refreeze_incident_parent(active, relative)
    except ReauthorCleanError:
        # The incident is already terminal.  Failed remainder re-freeze is
        # represented by an empty remaining_verified projection, never by a
        # false success or by deleting more custody.
        pass
    destroyed = [
        {
            "path": relative,
            "scope": "object",
            "intent_event_sha256": intent["event_sha256"] if intent else None,
            "authorized_payload_sha256": item["authorized_deletion_payload_sha256"],
            "diagnosis": "unlink observed without durable DELETE_VERIFIED event",
        }
    ]
    document = _receipt_document(
        manifest,
        operation_root,
        inventory,
        events,
        status="INCOMPLETE_DESTROYED_UNVERIFIED",
        destroyed_unverified=destroyed,
        reason_codes=["reauthor_clean_destroyed_unverified"],
    )
    receipt_path, raw = _publish_or_verify_receipt(manifest, operation_root, document)
    return _refuse(
        "reauthor_clean_destroyed_unverified",
        "object was destroyed after intent without a durable verification event; deletion is permanently incomplete",
        outcome={
            "status": "REFUSE",
            "completion": "INCOMPLETE_DESTROYED_UNVERIFIED",
            "receipt_path": str(receipt_path),
            "receipt_sha256": _sha256(raw),
        },
    )


def _destroyed_mismatch_error(
    manifest: Mapping[str, object],
    operation_root: Path,
    inventory: Mapping[str, object],
    events: Sequence[Mapping[str, object]],
    relative: str,
) -> ReauthorCleanError:
    event = _event_for(events, "DELETE_MISMATCH", relative)
    if event is None:
        raise _refuse(
            "reauthor_clean_event_chain_invalid", "destroyed mismatch lacks durable event"
        )
    data = event["data"]
    mismatch = [
        {
            "path": relative,
            "authorized_payload_sha256": data["authorized_payload_sha256"],
            "observed_final_sha256": data["final_held_fd_payload_sha256"],
            "event_sha256": event["event_sha256"],
        }
    ]
    document = _receipt_document(
        manifest,
        operation_root,
        inventory,
        events,
        status="INCOMPLETE_DESTROYED_MISMATCH",
        destroyed_mismatch=mismatch,
        reason_codes=["reauthor_clean_destroyed_mismatch"],
    )
    receipt_path, raw = _publish_or_verify_receipt(manifest, operation_root, document)
    return _refuse(
        "reauthor_clean_destroyed_mismatch",
        "post-unlink held-descriptor payload differs from authorization",
        outcome={
            "status": "REFUSE",
            "completion": "INCOMPLETE_DESTROYED_MISMATCH",
            "receipt_path": str(receipt_path),
            "receipt_sha256": _sha256(raw),
        },
    )


def _finalize_complete(
    active: Path,
    manifest: Mapping[str, object],
    operation_root: Path,
    inventory: Mapping[str, object],
) -> Mapping[str, object]:
    state_id = str(manifest["state_id"])
    events_root = _events_path(operation_root, state_id)
    events = _load_events(events_root, state_id)
    objects = _object_map(inventory)
    if _verified_paths(events) != set(objects):
        raise _refuse(
            "reauthor_clean_state_inventory_mismatch", "not every inventory object is verified"
        )
    if any(event["event_type"] == "DELETE_MISMATCH" for event in events):
        raise _refuse(
            "reauthor_clean_destroyed_mismatch", "mismatch incident forbids success"
        )
    for entry in manifest["request"]["entries"]:  # type: ignore[index]
        if Path(entry["canonical_path"]).exists() or Path(entry["canonical_path"]).is_symlink():
            raise _refuse(
                "reauthor_clean_state_inventory_mismatch",
                "targeted logical namespace reappeared before completion",
            )
    document = _receipt_document(
        manifest,
        operation_root,
        inventory,
        events,
        status="COMPLETE_VERIFIED",
    )
    receipt_path, raw = _publish_or_verify_receipt(manifest, operation_root, document)
    # Housekeeping is deliberately outside the completion predicate.
    try:
        if active.exists() and not os.listdir(active):
            active_fd = _open_directory(active)
            try:
                _set_flags_verified(active_fd, 0)
            finally:
                os.close(active_fd)
            parent_fd = _open_directory(active.parent)
            try:
                os.rmdir(active.name, dir_fd=parent_fd)
                os.fsync(parent_fd)
            finally:
                os.close(parent_fd)
    except (OSError, ReauthorCleanError):
        pass
    return {
        "status": "PASS",
        "completion": "COMPLETE",
        "receipt_path": str(receipt_path),
        "receipt_sha256": _sha256(raw),
        "deletion_claim": "VERIFIED LOGICAL NAMESPACE DELETION",
    }


def _verify_terminal(
    manifest: Mapping[str, object], operation_root: Path, targets: Mapping[str, Path]
) -> Mapping[str, object] | None:
    path = _receipt_path(operation_root, str(manifest["state_id"]))
    if not path.exists():
        return None
    receipt, raw = _read_canonical_object(path, "reauthor_clean_event_chain_invalid")
    status = receipt.get("status")
    if status not in {
        "COMPLETE_VERIFIED",
        "INCOMPLETE_DESTROYED_UNVERIFIED",
        "INCOMPLETE_DESTROYED_MISMATCH",
    }:
        raise _refuse(
            "reauthor_clean_event_chain_invalid", "terminal receipt has invalid status"
        )
    inventory, _inventory_raw = _read_canonical_object(
        _inventory_path(operation_root, str(manifest["state_id"])),
        "reauthor_clean_state_inventory_mismatch",
    )
    events = _load_events(
        _events_path(operation_root, str(manifest["state_id"])),
        str(manifest["state_id"]),
    )
    expected = _receipt_document(
        manifest,
        operation_root,
        inventory,
        events,
        status=str(status),
        destroyed_unverified=receipt.get("destroyed_unverified", []),
        destroyed_mismatch=receipt.get("destroyed_mismatch", []),
        observed_missing_unattributed=receipt.get("observed_missing_unattributed", []),
        reason_codes=receipt.get("reason_codes", []),
    )
    if raw != _render_json(expected):
        raise _refuse(
            "reauthor_clean_event_chain_invalid", "terminal receipt bytes do not replay"
        )
    if status == "COMPLETE_VERIFIED":
        if any(path.exists() or path.is_symlink() for path in targets.values()):
            raise _refuse(
                "reauthor_clean_state_inventory_mismatch", "completed target reappeared"
            )
        if _verified_paths(events) != set(_object_map(inventory)):
            raise _refuse(
                "reauthor_clean_event_chain_invalid", "complete receipt lacks full event proof"
            )
        return {
            "status": "PASS",
            "completion": "ALREADY_COMPLETE",
            "receipt_path": str(path),
            "receipt_sha256": _sha256(raw),
            "deletion_claim": "VERIFIED LOGICAL NAMESPACE DELETION",
        }
    reason = (
        "reauthor_clean_destroyed_unverified"
        if status == "INCOMPLETE_DESTROYED_UNVERIFIED"
        else "reauthor_clean_destroyed_mismatch"
    )
    raise _refuse(
        reason,
        "terminal incomplete deletion custody cannot be upgraded by retry",
        outcome={
            "status": "REFUSE",
            "completion": status,
            "receipt_path": str(path),
            "receipt_sha256": _sha256(raw),
        },
    )


def _legacy_guard(
    custody: Path, operation_root: Path, targets: Mapping[str, Path]
) -> None:
    quarantine = custody / QUARANTINE_DIRECTORY
    legacy = []
    if quarantine.exists() and quarantine.is_dir():
        legacy = [
            entry
            for entry in quarantine.iterdir()
            if re.fullmatch(r"[0-9]{8}T[0-9]{12}Z", entry.name)
        ]
    legacy_receipts = list(operation_root.glob("reauthor-clean-*.receipt.json"))
    if legacy:
        active = legacy[0]
        present = {
            name: (active / name).exists() or (active / name).is_symlink()
            for name in EXPECTED_NAMESPACES
        }
        if not all(present.values()):
            legacy_raw = b""
            if legacy_receipts:
                try:
                    legacy_raw = legacy_receipts[-1].read_bytes()
                except OSError:
                    legacy_raw = b""
            identity = {
                "legacy_quarantine": str(active),
                "request": _request_record(targets),
                "legacy_receipt_sha256": _sha256(legacy_raw) if legacy_raw else None,
            }
            incident_id = _sha256(
                b"joulewise.reauthor_clean_legacy_incident.v1\0"
                + _canonical_json(identity)
            )
            document = {
                "schema_version": RECEIPT_SCHEMA,
                "receipt_kind": "reauthor_clean_deletion_custody",
                "status": "INCOMPLETE_DESTROYED_UNVERIFIED",
                "completion": "INCOMPLETE",
                "deletion_semantics": "logical_namespace_unlink_not_secure_erase",
                "claim": "NO VERIFIED DELETION CLAIM",
                "truth_boundary": "not secure erase and not hostile-process exclusion",
                "state_manifest": None,
                "legacy_identity": identity,
                "destroyed_verified": [],
                "destroyed_unverified": [
                    {
                        "path": str(active),
                        "scope": "subtree_delta_unknown",
                        "intent_event_sha256": None,
                        "authorized_payload_sha256": None,
                        "diagnosis": "legacy v2 partial rmtree has no per-object event proof",
                    }
                ],
                "destroyed_mismatch": [],
                "remaining_verified": sorted(
                    name for name, exists in present.items() if exists
                ),
                "observed_missing_unattributed": sorted(
                    name for name, exists in present.items() if not exists
                ),
                "reason_codes": [
                    "reauthor_clean_legacy_state_unbound",
                    "reauthor_clean_destroyed_unverified",
                ],
            }
            receipt_path = operation_root / f"legacy-{incident_id}.receipt.json"
            raw = _render_json(document)
            if receipt_path.exists():
                _existing, observed = _read_canonical_object(
                    receipt_path, "reauthor_clean_event_chain_invalid"
                )
                if observed != raw:
                    raise _refuse(
                        "reauthor_clean_event_chain_invalid",
                        "legacy incident receipt replay differs",
                    )
            else:
                _publish_no_clobber(
                    receipt_path, raw, fault_prefix="legacy_incident_receipt"
                )
            raise _refuse(
                "reauthor_clean_destroyed_unverified",
                "legacy partial rmtree is permanently destroyed-unverified",
                outcome={
                    "status": "REFUSE",
                    "completion": "INCOMPLETE_DESTROYED_UNVERIFIED",
                    "receipt_path": str(receipt_path),
                    "receipt_sha256": _sha256(raw),
                },
            )
    if legacy or legacy_receipts:
        raise _refuse(
            "reauthor_clean_legacy_state_unbound",
            "legacy v2 cleanup state is not bound to v3 inode/event proof; partial rmtree state must be preserved as destroyed-unverified incident custody",
        )


def _select_manifest(
    operation_root: Path,
    pack_identity: Mapping[str, object],
    custody: Path,
    targets: Mapping[str, Path],
) -> dict[str, object] | None:
    candidates = []
    foreign_nonterminal = []
    for path in sorted(operation_root.glob("state-*.manifest.json")):
        manifest, _raw = _validate_manifest_file(path)
        terminal = _receipt_path(operation_root, str(manifest["state_id"])).exists()
        semantic_match = _manifest_matches_request(
            manifest, pack_identity, custody, operation_root, targets
        )
        anchors_match = False
        if semantic_match:
            try:
                recorded_custody = manifest["custody"]
                anchors_match = _anchor_matches(
                    _lstat_path(custody), recorded_custody["root_anchor"]
                ) and _anchor_matches(
                    _lstat_path(operation_root),
                    recorded_custody["operation_root_anchor"],
                )
                for source in manifest["sources"]:
                    source_path = Path(source["canonical_path"])
                    quarantine_path = Path(
                        str(manifest["expected_quarantine_path"])
                    ) / str(source["name"])
                    locations = [
                        candidate
                        for candidate in (source_path, quarantine_path)
                        if candidate.exists() or candidate.is_symlink()
                    ]
                    if locations and not any(
                        _anchor_matches(_lstat_path(candidate), source["root_anchor"])
                        for candidate in locations
                    ):
                        anchors_match = False
                    if not _anchor_matches(
                        _lstat_path(source_path.parent), source["parent_anchor"]
                    ):
                        anchors_match = False
            except (KeyError, OSError, TypeError):
                anchors_match = False
        if semantic_match and (anchors_match or terminal):
            candidates.append(manifest)
        elif not terminal:
            foreign_nonterminal.append(path)
    if foreign_nonterminal:
        raise _refuse(
            "reauthor_clean_state_binding_mismatch",
            f"foreign/stale nonterminal state present: {foreign_nonterminal[0]}",
        )
    nonterminal = [
        item
        for item in candidates
        if not _receipt_path(operation_root, str(item["state_id"])).exists()
    ]
    if len(nonterminal) > 1:
        raise _refuse(
            "reauthor_clean_state_ambiguous", "multiple matching nonterminal states"
        )
    if nonterminal:
        return nonterminal[0]
    completed = [
        item
        for item in candidates
        if _receipt_path(operation_root, str(item["state_id"])).exists()
    ]
    if len(completed) > 1:
        # Deterministic idempotence is unambiguous only when exactly one receipt binds.
        raise _refuse(
            "reauthor_clean_state_ambiguous", "multiple terminal states match this request"
        )
    return completed[0] if completed else None


def clean(
    pack_root: Path | str,
    namespaces: Iterable[Path | str],
    *,
    resume_removal: bool = False,
) -> Mapping[str, object]:
    """Execute or resume manifested quarantine FD-unlink v3."""

    pack_identity = _authenticate_pack(Path(pack_root))
    namespace_paths = tuple(Path(item) for item in namespaces)
    custody, targets = _prepare_namespace_request(pack_identity, namespace_paths)
    operation_root = custody / OPERATION_DIRECTORY
    _ensure_real_directory(
        operation_root, custody, "reauthor_clean_operation_log_invalid"
    )
    with _operation_lock(operation_root):
        _legacy_guard(custody, operation_root, targets)
        manifest = _select_manifest(operation_root, pack_identity, custody, targets)
        if manifest is not None:
            # Binding is verified BEFORE any terminal replay: a custody root
            # replaced at the same path (old operation tree moved in) must
            # refuse, never return ALREADY_COMPLETE (round-3 delta F1). Every
            # anchor the verifier checks survives completion — custody root,
            # operation root, and source PARENTS — so the complete case
            # verifies cleanly.
            _verify_manifest_binding(manifest, pack_identity, custody, operation_root, targets)
            terminal = _verify_terminal(manifest, operation_root, targets)
            if terminal is not None:
                return terminal
            if not resume_removal:
                raise _refuse(
                    "reauthor_clean_removal_incomplete",
                    "a manifested nonterminal cleanup exists; inspect it and use --resume-removal",
                )
        else:
            _validate_namespace_shapes(targets)
            manifest = _build_manifest(pack_identity, custody, operation_root, targets)
            raw = _render_json(manifest)
            _publish_no_clobber(
                _manifest_path(operation_root, str(manifest["state_id"])),
                raw,
                fault_prefix="manifest",
            )

        state_id = str(manifest["state_id"])
        events_root = _events_path(operation_root, state_id)
        _ensure_real_directory(
            events_root, operation_root, "reauthor_clean_event_chain_invalid"
        )
        active = _create_quarantine(custody, manifest)
        _prepared_event(manifest, operation_root, active)
        _quarantine_sources(manifest, custody, operation_root, active)
        events = _load_events(events_root, state_id)
        authorization = _event_for(events, "DELETE_AUTHORIZED")
        if authorization is None:
            _preflight_flags_and_freeze(active, operation_root, state_id)
            inventory, _raw = _authorize_inventory(active, manifest, operation_root)
        else:
            inventory, _raw = _load_authorized_inventory(active, manifest, operation_root)
        events = _load_events(events_root, state_id)
        for relative in _delete_order(_object_map(inventory)):
            if _event_for(events, "DELETE_VERIFIED", relative) is None:
                _delete_one(active, manifest, operation_root, inventory, relative)
                events = _load_events(events_root, state_id)
        return _finalize_complete(active, manifest, operation_root, inventory)


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _refuse("reauthor_clean_usage_invalid", message)


def _parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument(
        "--namespace",
        type=Path,
        action="append",
        required=True,
        help="absolute T-0 namespace path; repeat for the complete three-name set",
    )
    parser.add_argument(
        "--resume-removal",
        action="store_true",
        help="resume one manifested v3 cleanup after full binding verification",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        outcome = clean(args.pack_root, args.namespace, resume_removal=args.resume_removal)
    except ReauthorCleanError as exc:
        payload = {
            "status": "REFUSE",
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
        }
        payload.update(exc.outcome)
        sys.stdout.buffer.write(_render_json(payload))
        return 2
    except Exception as exc:  # pragma: no cover - last-resort fail-closed boundary
        sys.stdout.buffer.write(
            _render_json(
                {
                    "status": "REFUSE",
                    "reason_codes": ["reauthor_clean_internal_error"],
                    "detail": f"unexpected internal error: {exc}",
                }
            )
        )
        return 2
    sys.stdout.buffer.write(_render_json(outcome))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
