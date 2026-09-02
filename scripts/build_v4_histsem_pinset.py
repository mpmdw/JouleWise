#!/usr/bin/env python3
"""Build the versioned `_v5` receipt-histsem pinset from local Git objects."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402


class BuildError(ValueError):
    """The local-object construction contract refused."""


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--base-pinset", type=Path, required=True)
    parser.add_argument("--historical-head", required=True)
    parser.add_argument("--current-head", required=True)
    parser.add_argument("--pack-root", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def _git(repository: Path, *args: str) -> bytes:
    try:
        completed = subprocess.run(
            ("git", "-C", str(repository), *args),
            check=False,
            capture_output=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise BuildError(f"local Git query failed: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise BuildError(f"local Git query refused: {detail}")
    return completed.stdout


def _show(repository: Path, head: str, relative: str) -> bytes:
    return _git(repository, "show", f"{head}:{relative}")


def _canonical(raw: bytes, where: str) -> Mapping[str, Any]:
    try:
        value = readiness.parse_json_bytes(raw, require_canonical=True)
    except readiness.ArmReadinessError as exc:
        raise BuildError(f"{where} is not canonical JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise BuildError(f"{where} must be an object")
    return value


def _relative_pack(repository: Path, supplied: Path) -> tuple[Path, str]:
    candidate = supplied if supplied.is_absolute() else repository / supplied
    root = candidate.resolve(strict=True)
    try:
        relative = root.relative_to(repository).as_posix()
    except ValueError as exc:
        raise BuildError("pack root escapes the repository") from exc
    if PurePosixPath(relative).name != root.name:
        raise BuildError("pack path is anomalous")
    return root, relative


def _delta(repository: Path, historical_head: str, current_head: str, pack_path: str) -> dict[str, list[str]]:
    raw = _git(
        repository,
        "diff",
        "--name-status",
        "--no-renames",
        historical_head,
        current_head,
        "--",
        pack_path,
    )
    result = {"added": [], "deleted": [], "modified": []}
    names = {"A": "added", "D": "deleted", "M": "modified"}
    prefix = f"{pack_path}/"
    try:
        lines = raw.decode("utf-8", errors="strict").splitlines()
    except UnicodeDecodeError as exc:
        raise BuildError("post-authoring delta is not UTF-8") from exc
    for line in lines:
        try:
            status, path = line.split("\t", 1)
        except ValueError as exc:
            raise BuildError("post-authoring delta is malformed") from exc
        if status not in names or not path.startswith(prefix):
            raise BuildError("post-authoring delta is anomalous")
        result[names[status]].append(path[len(prefix) :])
    for values in result.values():
        values.sort()
    if result["deleted"]:
        raise BuildError("post-authoring delta deletes pack bytes")
    if not set(result["modified"]) <= readiness._HISTSEM_ALLOWED_MODIFICATIONS:
        raise BuildError("post-authoring delta modifies bytes outside the closed envelope")
    if any(
        not PurePosixPath(path).parts
        or PurePosixPath(path).parts[0] not in readiness._HISTSEM_CUSTODY_DIRECTORIES
        for path in result["added"]
    ):
        raise BuildError("post-authoring delta adds bytes outside custody")
    return result


def _row(
    repository: Path,
    root: Path,
    relative: str,
    historical_head: str,
    current_head: str,
) -> dict[str, Any]:
    historical_digest, historical_paths = readiness._historical_pack_tree(
        repository, relative, historical_head
    )
    current_digest, _current_paths = readiness._historical_pack_tree(
        repository, relative, current_head
    )
    if current_digest != readiness.committed_pack_tree_sha256(root):
        raise BuildError("HEAD differential self-test failed")
    # The pre-authoring test asks only whether EVIDENCE AUTHORING had already
    # happened at the historical coordinate, so it consults the authoring
    # subset, not the full custody frozenset.  U11 projection receipts are
    # committed per pack BEFORE authoring under the ruled _v5 order (runsheet
    # §3.2), so their presence here is correct.  `_delta` above keeps the full
    # frozenset: a projection receipt is still an admissible post-authoring
    # addition.  See `_HISTSEM_AUTHORING_CUSTODY_DIRECTORIES`.
    if readiness._histsem_tree_has_authoring_custody(historical_paths):
        raise BuildError("historical coordinate is not pre-authoring")

    plan_tree_raw = _show(repository, current_head, f"{relative}/plan_tree.json")
    plan_tree = _canonical(plan_tree_raw, f"{relative}/plan_tree.json")
    attachment = plan_tree.get("arm_attachments", {}).get("arm_readiness")
    if not isinstance(attachment, Mapping) or not isinstance(
        attachment.get("freeze_receipt"), Mapping
    ):
        raise BuildError("plan tree has no pinned freeze receipt")
    freeze_reference = dict(attachment["freeze_receipt"])
    expected_freeze_path = "arm_readiness.freeze.receipts/freeze-0004.json"
    if freeze_reference.get("path") != expected_freeze_path:
        raise BuildError("the _v5 pinset requires freeze-0004 exactly")
    freeze_raw = _show(repository, current_head, f"{relative}/{expected_freeze_path}")
    if readiness.sha256_bytes(freeze_raw) != freeze_reference.get("sha256"):
        raise BuildError("freeze receipt differs from the plan-tree binding")
    freeze_sidecar = _show(
        repository, current_head, f"{relative}/{expected_freeze_path}.sha256"
    )
    if freeze_sidecar != readiness.gnu_sidecar(
        readiness.sha256_bytes(freeze_raw), "freeze-0004.json"
    ):
        raise BuildError("freeze receipt sidecar differs")
    try:
        freeze = readiness.validate_freeze_receipt(
            readiness.parse_json_bytes(freeze_raw, require_canonical=True)
        )
    except readiness.ArmReadinessError as exc:
        raise BuildError(f"freeze receipt is invalid: {exc}") from exc
    if (
        freeze["schema_version"] != readiness.FREEZE_RECEIPT_V2_SCHEMA
        or freeze["receipt_id"] != "freeze-0004"
        or freeze["status"] != "PASS"
        or freeze.get("predecessor") is None
    ):
        raise BuildError("freeze receipt is not the required PASS v2 successor")

    plan_path = str(freeze["pack_identity"]["plan_path"])
    plan_raw = _show(repository, current_head, f"{relative}/{plan_path}")
    plan_sha256 = readiness.sha256_bytes(plan_raw)
    if plan_sha256 != freeze["pack_identity"]["plan_sha256"]:
        raise BuildError("frozen plan digest differs from freeze identity")

    receipts = sorted(
        (
            dict(item)
            for item in freeze["evidence"]
            if item["namespace"] == "PACK"
            and item["schema_version"] in readiness.GENERIC_EVIDENCE_RECEIPT_SCHEMAS
        ),
        key=lambda item: str(item["evidence_id"]),
    )
    if len(receipts) != 11:
        raise BuildError("freeze-0004 must bind exactly eleven generic PACK receipts")
    for item in receipts:
        receipt_path = str(item["path"])
        raw = _show(repository, current_head, f"{relative}/{receipt_path}")
        sidecar = _show(repository, current_head, f"{relative}/{receipt_path}.sha256")
        if (
            readiness.sha256_bytes(raw) != item["sha256"]
            or sidecar
            != readiness.gnu_sidecar(str(item["sha256"]), Path(receipt_path).name)
        ):
            raise BuildError(f"generic receipt binding differs: {receipt_path}")
        receipt = readiness.validate_evidence_receipt(
            readiness.parse_json_bytes(raw, require_canonical=True)
        )
        receipt_head = receipt.get("derivation_commit", receipt.get("head_commit"))
        if (
            receipt_head != historical_head
            or receipt["pack_sha256"] != historical_digest
            or any(
                not isinstance(fact.get("source_sha256"), str)
                or re.fullmatch(r"[0-9a-f]{64}", fact["source_sha256"]) is None
                for fact in receipt["facts"]
            )
        ):
            raise BuildError(f"generic receipt historical coordinate differs: {receipt_path}")

    return {
        "current_pack_sha256": current_digest,
        "freeze_receipt": freeze_reference,
        "head_commit": historical_head,
        "historical_pack_sha256": historical_digest,
        "pack_id": root.name,
        "pack_path": relative,
        "plan_sha256": plan_sha256,
        "plan_tree_sha256": readiness.sha256_bytes(plan_tree_raw),
        "post_authoring_delta": _delta(
            repository, historical_head, current_head, relative
        ),
        "published_anchor": "D-151:joulewise.d117_step6_confirmation_table.v1#successor_pinset",
        "receipt_count": len(receipts),
        "receipts": receipts,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    repository = args.repository.resolve(strict=True)
    base_path = args.base_pinset.resolve(strict=True)
    output = args.output.resolve(strict=False)
    for head in (args.historical_head, args.current_head):
        if re.fullmatch(r"[0-9a-f]{40}", head) is None:
            raise BuildError("both heads must be full lowercase Git OIDs")
        _git(repository, "cat-file", "-e", f"{head}^{{commit}}")
    if _git(repository, "rev-parse", "HEAD").decode().strip() != args.current_head:
        raise BuildError("current-head must equal the checked-out HEAD")
    if _git(
        repository,
        "merge-base",
        "--is-ancestor",
        args.historical_head,
        args.current_head,
    ) is None:
        raise AssertionError("unreachable")
    base = dict(_canonical(base_path.read_bytes(), "base pinset"))
    readiness._validate_histsem_pinset(base)
    registry, _raw = readiness.load_registry(repository)
    expected_ids = set(
        registry["freeze_evidence_lifecycle"]["successor_policy"][
            "successor_pack_ids"
        ].values()
    )
    if len(args.pack_root) != 3:
        raise BuildError("exactly three _v5 pack roots are required")
    normalized = [_relative_pack(repository, item) for item in args.pack_root]
    if {root.name for root, _relative in normalized} != expected_ids:
        raise BuildError("pack roots do not equal the registry successor roster")
    if len({relative for _root, relative in normalized}) != 3:
        raise BuildError("pack roots must be unique")
    rows = [
        _row(
            repository,
            root,
            relative,
            args.historical_head,
            args.current_head,
        )
        for root, relative in sorted(normalized, key=lambda item: item[1])
    ]
    # Chain composition (D-151 condition 6 / runsheet §3.7): the successor is
    # MEMBER 2 of the code-enumerated chain and carries ONLY the three _v5
    # rows. The v1 rows stay in the immutable member-1 artifact; copying them
    # here would make the chain union refuse on duplicate identities. The
    # base is still validated above and used for collision screening.
    base_identities = {
        (str(row["pack_id"]), str(row["pack_path"])) for row in base["packs"]
    }
    for row in rows:
        identity = (str(row["pack_id"]), str(row["pack_path"]))
        if identity in base_identities:
            raise BuildError(
                f"successor row collides with a base pinset identity: {identity!r}"
            )
    value = dict(base)
    value["packs"] = rows
    readiness._validate_histsem_pinset(value)
    raw = readiness.render_json(value)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        output,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o644,
    )
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    readiness._fsync_directory(output.parent)
    return {
        "schema_version": "joulewise.receipt_histsem_pinset_build.v1",
        "status": "PASS",
        "output": str(output),
        "sha256": readiness.sha256_bytes(raw),
        "base_pack_count": len(base["packs"]),
        "successor_pack_count": len(rows),
        "pack_count": len(value["packs"]),
        "receipt_count": sum(int(item["receipt_count"]) for item in value["packs"]),
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = build(args)
    except (
        BuildError,
        OSError,
        readiness.ArmReadinessError,
        readiness.HistoricalSemanticsError,
    ) as exc:
        result = {
            "schema_version": "joulewise.receipt_histsem_pinset_build.v1",
            "status": "REFUSE",
            "reason_codes": ["histsem_pinset_invalid"],
            "detail": str(exc),
        }
        sys.stdout.buffer.write(readiness.render_json(result))
        return 2
    sys.stdout.buffer.write(readiness.render_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
