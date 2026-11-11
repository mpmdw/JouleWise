"""Committed owner permission to read outcomes; never read the named custody paths.

This is an opt-in accident guard (RL-53 W-8), not an authentication boundary.
Patterns use fnmatch semantics: '*' can match '/'. Matching is lexical only.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


SCHEMA = "joulewise.unseal_record.v1"
FIELDS = frozenset({
    "schema", "given_by", "given_at", "words", "block", "verdict_sha256",
    "verdict_path", "paths_opened", "stays_sealed", "seats_may_read",
    "recorded_by", "recorded_at",
})
_BLOCK = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
_DIGEST = re.compile(r"[A-Fa-f0-9]{64}")
_TIME = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?"
    r"(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)"
)


class UnsealRecordError(ValueError):
    """Invalid record, with a structure-only .code (no owner words or paths)."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class UnsealRefused(ValueError):
    """Reading is not authorized, with a structure-only .code."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _text(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        value.encode("utf-8")
    except UnicodeError:
        return False
    return True


def _path(value: object) -> str:
    """Normalize separators and dot segments, without filesystem operations."""
    if not _text(value) or any(ord(c) < 32 for c in value):
        raise UnsealRecordError("path_invalid")
    value = value.replace("\\", "/")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise UnsealRecordError("path_invalid")
    parts = value.split("/")
    if ".." in parts:
        raise UnsealRecordError("path_invalid")
    normalized = "/".join(p for p in parts if p not in ("", "."))
    if not normalized or re.match(r"^[A-Za-z]:", normalized):
        raise UnsealRecordError("path_invalid")
    return normalized


def validate(mapping: Mapping) -> None:
    """Validate exactly v1's fields. Preserve the owner's words verbatim."""
    if not isinstance(mapping, Mapping):
        raise UnsealRecordError("not_mapping")
    if set(mapping) - FIELDS:
        raise UnsealRecordError("unknown_key")
    if FIELDS - set(mapping):
        raise UnsealRecordError("missing_field")
    if mapping["schema"] != SCHEMA:
        raise UnsealRecordError("schema_invalid")
    for field in ("given_by", "words", "recorded_by"):
        if not _text(mapping[field]):
            raise UnsealRecordError(field + "_invalid")
    for field in ("given_at", "recorded_at"):
        value = mapping[field]
        if not isinstance(value, str) or not _TIME.fullmatch(value):
            raise UnsealRecordError(field + "_invalid")
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise UnsealRecordError(field + "_invalid") from None
    if not isinstance(mapping["block"], str) or not _BLOCK.fullmatch(mapping["block"]):
        raise UnsealRecordError("block_invalid")
    if not isinstance(mapping["verdict_sha256"], str) or not _DIGEST.fullmatch(mapping["verdict_sha256"]):
        raise UnsealRecordError("verdict_sha256_invalid")
    _path(mapping["verdict_path"])
    for field in ("paths_opened", "stays_sealed", "seats_may_read"):
        values = mapping[field]
        if not isinstance(values, list) or (field != "stays_sealed" and not values):
            raise UnsealRecordError(field + "_invalid")
        for value in values:
            if field == "seats_may_read":
                if not _text(value):
                    raise UnsealRecordError(field + "_invalid")
            else:
                _path(value)


def _pairs(items: list[tuple]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise UnsealRecordError("duplicate_key")
        result[key] = value
    return result


def load(path: str | os.PathLike) -> dict:
    """Read only the record file. Never dereference any field in it."""
    try:
        with open(path, "rb") as stream:
            mapping = json.loads(stream.read(), object_pairs_hook=_pairs)
    except (OSError, ValueError, UnicodeError) as exc:
        if isinstance(exc, UnsealRecordError):
            raise
        raise UnsealRecordError("record_unreadable") from None
    validate(mapping)
    return mapping


def canonical_bytes(mapping: Mapping) -> bytes:
    """UTF-8 JSON, sorted keys, compact separators, no trailing newline."""
    validate(mapping)
    return json.dumps(dict(mapping), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def record_sha256(mapping: Mapping) -> str:
    return hashlib.sha256(canonical_bytes(mapping)).hexdigest()


def _git(directory: Path, *args: str) -> bytes:
    # Local objects only. Do not consult the operator's global Git configuration,
    # inherit repository overrides, invoke hooks/fsmonitor, or lazy-fetch blobs.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(directory), *args],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise UnsealRefused("commit_unverifiable") from None
    if result.returncode:
        raise UnsealRefused("commit_unverifiable")
    return result.stdout


def _committed(path: Path, raw: bytes) -> None:
    try:
        directory = path.parent.resolve()
        root = Path(os.fsdecode(_git(directory, "rev-parse", "--show-toplevel").rstrip(b"\n"))).resolve()
        relative = (directory / path.name).relative_to(root).as_posix()
        head = _git(directory, "rev-parse", "--verify", "HEAD^{commit}").strip().decode("ascii")
    except (OSError, RuntimeError, ValueError) as exc:
        if isinstance(exc, UnsealRefused):
            raise
        raise UnsealRefused("commit_unverifiable") from None
    entry = _git(root, "ls-tree", "-z", head, "--", relative)
    if not entry:
        raise UnsealRefused("record_not_committed")
    try:
        header, name = entry.rstrip(b"\0").split(b"\t", 1)
        mode, kind, oid = header.split()
        blob = oid.decode("ascii")
    except ValueError:
        raise UnsealRefused("commit_unverifiable") from None
    if mode not in (b"100644", b"100755") or kind != b"blob" or os.fsdecode(name) != relative:
        raise UnsealRefused("record_not_committed")
    if _git(directory, "cat-file", "blob", blob) != raw:
        raise UnsealRefused("record_not_committed")


def require_unseal(records_dir: str | os.PathLike, *, block: str,
                   verdict_sha256: str, path: str | None = None) -> dict:
    """Find one valid, HEAD-committed permission bound to this exact verdict.

    Edited/untracked matching records refuse. Multiple matching records refuse
    as ambiguous; a fresh verdict needs a fresh record. No verdict or outcome
    path from a record is opened, resolved, globbed, or statted.
    """
    if not isinstance(block, str) or not _BLOCK.fullmatch(block):
        raise UnsealRefused("block_invalid")
    if not isinstance(verdict_sha256, str) or not _DIGEST.fullmatch(verdict_sha256):
        raise UnsealRefused("verdict_sha256_invalid")
    try:
        requested = None if path is None else _path(path)
    except UnsealRecordError:
        raise UnsealRefused("path_invalid") from None
    directory = Path(records_dir)
    try:
        files = sorted(p for p in directory.iterdir() if p.suffix == ".json")
    except FileNotFoundError:
        raise UnsealRefused("no_record") from None
    except OSError:
        raise UnsealRefused("records_unreadable") from None
    if not files:
        raise UnsealRefused("no_record")
    matching_block, matches = False, []
    for file in files:
        try:
            if file.is_symlink():
                raise UnsealRecordError("record_symlink")
            with open(file, "rb") as stream:
                raw = stream.read()
            record = json.loads(raw, object_pairs_hook=_pairs)
            validate(record)
            prefix = record["block"] + "-"
            stamp = file.stem.removeprefix(prefix)
            if not file.stem.startswith(prefix) or not re.fullmatch(r"[0-9]{8}", stamp):
                raise UnsealRecordError("filename_invalid")
            date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))
        except (OSError, ValueError, UnicodeError):
            raise UnsealRefused("record_invalid") from None
        if record["block"] == block:
            matching_block = True
            if record["verdict_sha256"].lower() == verdict_sha256.lower():
                _committed(file, raw)
                matches.append(record)
    if not matching_block:
        raise UnsealRefused("block_mismatch")
    if not matches:
        raise UnsealRefused("digest_mismatch")
    if len(matches) != 1:
        raise UnsealRefused("ambiguous_record")
    record = matches[0]
    if requested is not None:
        if any(fnmatch.fnmatchcase(requested, _path(p)) for p in record["stays_sealed"]):
            raise UnsealRefused("stays_sealed")
        if not any(fnmatch.fnmatchcase(requested, _path(p)) for p in record["paths_opened"]):
            raise UnsealRefused("path_not_opened")
    return record
