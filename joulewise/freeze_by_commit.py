"""Git-only block identities (F1/F2); no measurement inputs are opened here.

Authority: docs/process/freeze_by_commit.md and RUN_STATE item 146.
Registrations, rather than movable refs or main's bytes, own commit/tree IDs.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = "configs/analysis/b5/freeze_commits.json"
REGISTRATION_COMMIT_ENV = "JOULEWISE_B5_FREEZE_REGISTRATION_COMMIT"
_SHA1 = re.compile(r"[0-9a-f]{40}")
_SHA256 = re.compile(r"[0-9a-f]{64}")


class FreezeIdentityError(ValueError):
    """Missing history, an altered tag, or an unruled analysis checkout."""


def _git(repository: Path, *args: str, data: bytes | None = None) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(repository), *args], input=data,
            check=True, capture_output=True, timeout=30,
        ).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise FreezeIdentityError("freeze_git_object_unavailable") from exc


def _commit(value: str) -> str:
    if not isinstance(value, str) or _SHA1.fullmatch(value) is None:
        raise FreezeIdentityError("freeze_commit_invalid")
    return value


def _path(value: str) -> str:
    if (not isinstance(value, str) or not value or value.startswith("/")
            or any(part in ("", ".", "..", "restricted") for part in value.split("/"))
            or "\n" in value or "\0" in value or "\\" in value):
        raise FreezeIdentityError("freeze_path_invalid")
    return str(PurePosixPath(value))


def blob(repository: Path, commit: str, path: str) -> bytes:
    return _git(repository, "cat-file", "blob", f"{_commit(commit)}:{_path(path)}")


def blob_digests(repository: Path, commit: str, paths) -> dict[str, str]:
    """Batch-read only explicitly named Git blobs, never worktree/data paths."""
    commit = _commit(commit)
    paths = [_path(path) for path in paths]
    raw = _git(repository, "cat-file", "--batch",
               data="".join(f"{commit}:{path}\n" for path in paths).encode())
    result, offset = {}, 0
    for path in paths:
        end = raw.index(b"\n", offset)
        header = raw[offset:end].split()
        if len(header) != 3 or header[1] != b"blob":
            raise FreezeIdentityError("freeze_blob_unavailable")
        size = int(header[2])
        result[path] = hashlib.sha256(raw[end + 1:end + 1 + size]).hexdigest()
        offset = end + size + 2
    return result


def load_registration(repository: Path = ROOT) -> dict:
    """Load local metadata, or an explicitly pinned later registration commit.

    A commit cannot contain its own ID/tree in a ledger. A ruled block
    checkout therefore names the reviewed *later* registration commit in
    JOULEWISE_B5_FREEZE_REGISTRATION_COMMIT. Read that exact Git blob; never
    infer authority from the current tip of a branch or from remote state.
    """
    try:
        authority = os.environ.get(REGISTRATION_COMMIT_ENV)
        raw = (blob(repository, authority, REGISTRATION) if authority is not None
               else (repository / REGISTRATION).read_bytes())
        value = json.loads(raw)
        if (value["schema"] != "joulewise.block_freeze.v1"
                or value["active_analysis"] not in value["tags"]):
            raise ValueError()
        return value
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise FreezeIdentityError("freeze_registration_invalid") from exc


def verify_tag(repository: Path, tag: str, record: dict) -> str:
    """Require an annotated tag, its recorded object, peeled commit AND tree."""
    if not isinstance(tag, str) or re.fullmatch(r"b[0-9]+/(collection|analysis(?:-r[0-9]+)?)", tag) is None:
        raise FreezeIdentityError("freeze_tag_invalid")
    commit, tree = _commit(record["commit"]), _commit(record["tree"])
    ref = "refs/tags/" + tag
    if (_git(repository, "cat-file", "-t", ref).strip() != b"tag"
            or _git(repository, "rev-parse", ref).decode().strip() != _commit(record["tag_object"])
            or _git(repository, "rev-parse", ref + "^{commit}").decode().strip() != commit
            or _git(repository, "rev-parse", commit + "^{tree}").decode().strip() != tree):
        raise FreezeIdentityError("freeze_tag_identity_mismatch")
    return commit


def require_analysis_head(repository: Path, head: str, *, registration: dict | None = None) -> None:
    """F2: exact release commit, or a descendant with every new commit ruled.

    The caller owns the clean-checkout gate. No remote or branch-containment
    predicate is used. Merged side branches are included in the ruling census.
    """
    head = _commit(head)
    value = load_registration(repository) if registration is None else registration
    tag = value["active_analysis"]
    base = verify_tag(repository, tag, value["tags"][tag])
    if head == base:
        return
    _git(repository, "merge-base", "--is-ancestor", base, head)
    new_commits = _git(repository, "rev-list", f"{base}..{head}").decode().splitlines()
    ruled = value["ruled_descendants"]
    for commit in new_commits:
        record = ruled.get(commit)
        if not isinstance(record, dict):
            raise FreezeIdentityError("analysis_descendant_unruled")
        tree = _git(repository, "rev-parse", commit + "^{tree}").decode().strip()
        ruling = record.get("ruling", "")
        digest = record.get("ruling_sha256", "")
        if (tree != _commit(record.get("tree"))
                or not isinstance(ruling, str) or not ruling.startswith("docs/")
                or not isinstance(digest, str) or _SHA256.fullmatch(digest) is None
                or hashlib.sha256(blob(repository, commit, ruling)).hexdigest() != digest):
            raise FreezeIdentityError("analysis_descendant_ruling_invalid")


def require_commit_scoped_calibration() -> None:
    """Unissued F4 seam; the D-138 transaction must implement and enable it.

    Legacy acceptance and its live-byte staleness invariant remain in force.
    No caller can mistake a pinned historical digest for scientific acceptance.
    """
    raise FreezeIdentityError("calibration_commit_scope_reissue_pending")
