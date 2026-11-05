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
REGISTRATION_REF = "refs/remotes/origin/main"
REGISTRATION_COMMIT_ENV = "JOULEWISE_B5_FREEZE_REGISTRATION_COMMIT"
_SHA1 = re.compile(r"[0-9a-f]{40}")


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
    """Read only origin/main's reviewed Git blob (F3; freeze_p1_rebind.md).

    Runtime authority overrides and descendant ledgers are retired. A ruled
    fix requires a new registered analysis-r<k> tag, through ordinary review.
    """
    if REGISTRATION_COMMIT_ENV in os.environ:
        raise FreezeIdentityError("freeze_registration_override_removed")
    try:
        main = _git(repository, "rev-parse", "--verify",
                    REGISTRATION_REF + "^{commit}").decode().strip()
    except FreezeIdentityError as exc:
        raise FreezeIdentityError("freeze_registration_origin_main_missing") from exc
    try:
        raw = blob(repository, main, REGISTRATION)
        value = json.loads(raw)
        if (not isinstance(value, dict)
                or value["schema"] != "joulewise.block_freeze.v1"
                or not isinstance(value["tags"], dict)
                or not isinstance(value["active_analysis"], str)
                or value["active_analysis"] not in value["tags"]
                or value.get("ruled_descendants")):
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


def require_analysis_head(repository: Path, head: str) -> None:
    """F2/F3: require an analysis tag registered in origin/main.

    The caller owns the clean-checkout gate. Descendants (including merges)
    require a new reviewed registration and analysis-r<k> tag before use.
    """
    head = _commit(head)
    value = load_registration(repository)
    for tag, record in value["tags"].items():
        if (re.fullmatch(r"b5/analysis(?:-r[0-9]+)?", tag)
                and isinstance(record, dict) and record.get("commit") == head):
            verify_tag(repository, tag, record)
            return
    raise FreezeIdentityError("analysis_descendant_unruled")


def require_commit_scoped_calibration() -> None:
    """Unissued F4 seam; the D-138 transaction must implement and enable it.

    Legacy acceptance and its live-byte staleness invariant remain in force.
    No caller can mistake a pinned historical digest for scientific acceptance.
    """
    raise FreezeIdentityError("calibration_commit_scope_reissue_pending")
