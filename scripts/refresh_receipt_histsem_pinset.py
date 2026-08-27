#!/usr/bin/env python3
"""Refresh reviewed current-coordinate fields in a receipt-histsem pinset."""

from __future__ import annotations

import argparse
import copy
import difflib
import re
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402


_IMMUTABLE_FIELDS = frozenset(
    {
        "freeze_receipt",
        "head_commit",
        "historical_pack_sha256",
        "pack_id",
        "pack_path",
        "plan_sha256",
        "plan_tree_sha256",
        "published_anchor",
        "receipt_count",
        "receipts",
    }
)
_TEST_PIN = re.compile(
    rb'(?m)^(PINSET_SHA256 = ")[0-9a-f]{64}("\r?)$'
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument(
        "--pinset",
        type=Path,
        default=readiness.RECEIPT_HISTSEM_PINSET_RELATIVE_PATH[0],
    )
    parser.add_argument("--refresh-row", action="append", default=[], metavar="PACK_ID")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--print-pinset-sha256", action="store_true")
    parser.add_argument("--write-test-pin", type=Path, default=None)
    return parser


def _refusal(reason_code: str, detail: str) -> readiness.HistoricalSemanticsError:
    return readiness.HistoricalSemanticsError(reason_code, detail)


def _resolve_from(repository: Path, supplied: Path) -> Path:
    return supplied.resolve(strict=False) if supplied.is_absolute() else repository / supplied


def _load_pinset(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise _refusal("histsem_pinset_absent", f"receipt-histsem pinset is absent: {path}") from exc
    except OSError as exc:
        raise _refusal("histsem_pinset_invalid", f"receipt-histsem pinset is unreadable: {exc}") from exc
    try:
        value = readiness.parse_json_bytes(raw, require_canonical=True)
        readiness._validate_histsem_pinset(value)
    except readiness.ArmReadinessError as exc:
        raise _refusal("histsem_pinset_invalid", f"receipt-histsem pinset is not canonical: {exc}") from exc
    if not isinstance(value, dict):  # defensive; the validator requires an object
        raise _refusal("histsem_pinset_invalid", "receipt-histsem pinset must be an object")
    return value, raw


def _git(repository: Path, *args: str) -> bytes:
    code, stdout, stderr = readiness._histsem_git(repository, *args)
    if code != 0:
        detail = stderr.decode("utf-8", errors="replace").strip()
        raise _refusal(
            "histsem_git_unavailable",
            f"local Git query refused{': ' + detail if detail else ''}",
        )
    return stdout


def _require_clean_pack(repository: Path, pack_path: str) -> None:
    dirty = _git(
        repository,
        "status",
        "--porcelain",
        "--untracked-files=all",
        "--",
        pack_path,
    )
    if dirty:
        detail = dirty.decode("utf-8", errors="replace").strip()
        raise _refusal(
            "histsem_binding_mismatch",
            f"pack {pack_path!r} has worktree bytes that are not the HEAD blob: {detail}",
        )


def _require_reviewable_heads(repository: Path, head_commit: str) -> None:
    code, _stdout, _stderr = readiness._histsem_git(
        repository,
        "merge-base",
        "--is-ancestor",
        head_commit,
        "origin/main",
    )
    if code != 0:
        raise _refusal(
            "histsem_commit_unpublished",
            f"historical receipt commit {head_commit} is not an ancestor of origin/main",
        )
    remote_refs = _git(
        repository,
        "for-each-ref",
        "--format=%(refname)",
        "--contains",
        "HEAD",
        "refs/remotes",
    )
    if not remote_refs.strip():
        raise _refusal(
            "histsem_commit_unpublished",
            "current HEAD is not reachable from a remote-tracking ref",
        )


def _immutable_field_for(detail: str) -> str:
    lowered = detail.lower()
    if "plan tree" in lowered or "plan-tree" in lowered or "plan_tree" in lowered:
        return "plan_tree_sha256"
    if "plan/pack" in lowered or "plan identity" in lowered or "plan bytes" in lowered:
        return "plan_sha256"
    if "predecessor" in lowered or "freeze" in lowered:
        return "freeze_receipt"
    if "receipt" in lowered or "fact source" in lowered:
        return "receipts"
    if "historical" in lowered:
        return "historical_pack_sha256/head_commit"
    return ", ".join(sorted(_IMMUTABLE_FIELDS))


def _verify_candidate(
    repository: Path,
    pack_root: Path,
    rows: tuple[Mapping[str, Any], ...],
) -> None:
    try:
        readiness.verify_receipt_histsem_pack(
            pack_root,
            require_published=False,
            _pinset_rows=rows,
        )
    except readiness.HistoricalSemanticsError as exc:
        field = _immutable_field_for(str(exc))
        raise _refusal(
            exc.reason_code,
            f"immutable field {field} refuses refresh: {exc}",
        ) from exc


def _derive_row(
    repository: Path,
    row: Mapping[str, Any],
) -> tuple[dict[str, Any], Path]:
    pack_id = str(row["pack_id"])
    pack_path = str(row["pack_path"])
    pack_root = (repository / pack_path).resolve(strict=True)
    try:
        pack_root.relative_to(repository)
    except ValueError as exc:
        raise _refusal("histsem_pinset_invalid", f"pack path escapes repository: {pack_path!r}") from exc
    _require_clean_pack(repository, pack_path)
    head_commit = str(row["head_commit"])
    _require_reviewable_heads(repository, head_commit)

    historical_digest, historical_paths = readiness._historical_pack_tree(
        repository,
        pack_path,
        head_commit,
    )
    if historical_digest != row["historical_pack_sha256"]:
        raise _refusal(
            "histsem_historical_digest_mismatch",
            f"immutable field historical_pack_sha256 differs for row {pack_id}",
        )
    if readiness._histsem_tree_has_authoring_custody(historical_paths):
        raise _refusal(
            "histsem_historical_tree_not_pre_authoring",
            f"immutable field head_commit for row {pack_id} is not pre-authoring",
        )

    refreshed = copy.deepcopy(dict(row))
    refreshed["current_pack_sha256"] = readiness.committed_pack_tree_sha256(pack_root)
    refreshed["post_authoring_delta"] = readiness._histsem_delta(
        repository,
        pack_path,
        head_commit,
    )
    for field in _IMMUTABLE_FIELDS:
        if refreshed[field] != row[field]:
            raise AssertionError(f"refresh changed immutable field {field}")
    return refreshed, pack_root


def _row_diff(pinset: Path, pack_id: str, old: Mapping[str, Any], new: Mapping[str, Any]) -> str:
    before = readiness.render_json(old).decode("utf-8").splitlines(keepends=True)
    after = readiness.render_json(new).decode("utf-8").splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            before,
            after,
            fromfile=f"{pinset}#{pack_id}@old",
            tofile=f"{pinset}#{pack_id}@new",
        )
    )


def _test_pin_bytes(path: Path, digest: str) -> tuple[bytes, bytes]:
    try:
        original = path.read_bytes()
    except OSError as exc:
        raise _refusal("histsem_pinset_invalid", f"test pin file is unreadable: {exc}") from exc
    matches = list(_TEST_PIN.finditer(original))
    if len(matches) != 1:
        raise _refusal(
            "histsem_pinset_invalid",
            f"test pin file must contain exactly one PINSET_SHA256 literal; found {len(matches)}",
        )
    replacement = matches[0].group(1) + digest.encode("ascii") + matches[0].group(2)
    return original, original[: matches[0].start()] + replacement + original[matches[0].end() :]


def _restore(path: Path, existed: bool, raw: bytes) -> None:
    if existed:
        path.write_bytes(raw)
    elif path.exists():
        path.unlink()


def refresh(args: argparse.Namespace) -> tuple[bytes, list[str], list[str]]:
    repository = args.repository_root.resolve(strict=True)
    pinset_path = _resolve_from(repository, args.pinset)
    output_path = pinset_path if args.output is None else _resolve_from(repository, args.output)
    test_pin_path = (
        None if args.write_test_pin is None else _resolve_from(repository, args.write_test_pin)
    )
    if not args.refresh_row:
        if not args.print_pinset_sha256 or args.write_test_pin is not None:
            raise _refusal(
                "histsem_pinset_absent",
                "at least one --refresh-row is required unless only the pinset digest is printed",
            )
        _value, raw = _load_pinset(pinset_path)
        return raw, [], []
    if test_pin_path is not None and test_pin_path == output_path:
        raise _refusal("histsem_pinset_invalid", "test pin file and pinset output must differ")

    value, original_pinset = _load_pinset(pinset_path)
    requested = list(dict.fromkeys(args.refresh_row))
    rows_by_id: dict[str, list[int]] = {}
    for index, row in enumerate(value["packs"]):
        rows_by_id.setdefault(str(row["pack_id"]), []).append(index)
    for pack_id in requested:
        matches = rows_by_id.get(pack_id, [])
        if not matches:
            raise _refusal("histsem_pinset_absent", f"pinset has no row for pack_id {pack_id!r}")
        if len(matches) != 1:
            raise _refusal("histsem_pinset_invalid", f"pinset has ambiguous pack_id {pack_id!r}")

    candidate = copy.deepcopy(value)
    pack_roots: dict[str, Path] = {}
    diffs: list[str] = []
    current: list[str] = []
    for pack_id in requested:
        index = rows_by_id[pack_id][0]
        old_row = candidate["packs"][index]
        new_row, pack_root = _derive_row(repository, old_row)
        candidate["packs"][index] = new_row
        pack_roots[pack_id] = pack_root
        if old_row == new_row:
            current.append(pack_id)
        else:
            diffs.append(_row_diff(pinset_path, pack_id, old_row, new_row))

    candidate_raw = readiness.render_json(candidate)
    candidate_rows = readiness._validate_histsem_pinset(
        readiness.parse_json_bytes(candidate_raw, require_canonical=True)
    )
    for pack_id in requested:
        _verify_candidate(repository, pack_roots[pack_id], candidate_rows)

    changed = candidate_raw != original_pinset
    output_existed = output_path.exists()
    output_original = output_path.read_bytes() if output_existed else b""
    test_original = b""
    test_replacement = b""
    test_existed = False
    digest = readiness.sha256_bytes(candidate_raw)
    if test_pin_path is not None:
        test_existed = test_pin_path.exists()
        test_original, test_replacement = _test_pin_bytes(test_pin_path, digest)

    wrote_output = False
    wrote_test = False
    try:
        if changed:
            wrote_output = True
            output_path.write_bytes(candidate_raw)
            written_value, written_raw = _load_pinset(output_path)
            if written_raw != candidate_raw:
                raise _refusal("histsem_pinset_invalid", "written pinset bytes differ from candidate")
            written_rows = readiness._validate_histsem_pinset(written_value)
            for pack_id in requested:
                _verify_candidate(repository, pack_roots[pack_id], written_rows)
        if test_pin_path is not None and test_replacement != test_original:
            wrote_test = True
            test_pin_path.write_bytes(test_replacement)
    except BaseException:
        if wrote_test and test_pin_path is not None:
            _restore(test_pin_path, test_existed, test_original)
        if wrote_output:
            _restore(output_path, output_existed, output_original)
        raise
    return candidate_raw, diffs, current


def _emit_refusal(exc: readiness.HistoricalSemanticsError) -> int:
    payload = {
        "schema_version": "joulewise.receipt_histsem_verification.v1",
        "status": "REFUSE",
        "reason_codes": [exc.reason_code],
        "detail": str(exc),
    }
    sys.stdout.write(readiness.render_json(payload).decode("utf-8"))
    return 2


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        raw, diffs, current = refresh(args)
    except readiness.HistoricalSemanticsError as exc:
        return _emit_refusal(exc)
    except readiness.ArmReadinessError as exc:
        return _emit_refusal(
            _refusal("histsem_pinset_invalid", f"receipt-histsem refresh refused: {exc}")
        )
    except OSError as exc:
        return _emit_refusal(
            _refusal("histsem_pinset_invalid", f"receipt-histsem refresh I/O refused: {exc}")
        )

    for diff in diffs:
        sys.stdout.write(diff)
    for pack_id in current:
        sys.stdout.write(f"row {pack_id} is already current\n")
    if args.print_pinset_sha256:
        digest = readiness.sha256_bytes(raw)
        sys.stdout.write(f"pinset sha256: {digest}\n")
        sys.stdout.write(f'PINSET_SHA256 = "{digest}"\n')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
