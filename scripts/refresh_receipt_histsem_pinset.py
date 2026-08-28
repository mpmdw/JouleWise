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

# The CLI-owned set deliberately excludes this script.  Including a tool that
# rewrites its own authenticator makes an honest one-change review cycle
# impossible: before commit the dirty-tool guard must refuse, and after the
# sidecar write the dirty-sidecar guard must refuse until a second commit.  The
# script's own committed sidecar is instead pinned by the family-marker test
# with the same public renderer below.
CUSTODY_TOOL_SIDECARS = (
    "build_family_marker.py",
    "verify_family_marker.py",
    "build_v4_histsem_pinset.py",
    "verify_receipt_histsem.py",
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
    parser.add_argument("--refresh-tool-sidecars", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--print-pinset-sha256", action="store_true")
    parser.add_argument("--write-test-pin", type=Path, default=None)
    return parser


def _refusal(reason_code: str, detail: str) -> readiness.HistoricalSemanticsError:
    return readiness.HistoricalSemanticsError(reason_code, detail)


def _resolve_from(repository: Path, supplied: Path) -> Path:
    candidate = supplied if supplied.is_absolute() else repository / supplied
    try:
        return candidate.resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise _refusal(
            "histsem_pinset_invalid", f"path cannot be normalized: {supplied}: {exc}"
        ) from exc


def _enumerated_pinset_paths(repository: Path) -> tuple[Path, ...]:
    return tuple(
        _resolve_from(repository, relative)
        for relative in readiness.RECEIPT_HISTSEM_PINSET_RELATIVE_PATH
    )


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


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
        "--ignored=matching",
        "--",
        pack_path,
    )
    if dirty:
        detail = dirty.decode("utf-8", errors="replace").strip()
        raise _refusal(
            "histsem_binding_mismatch",
            f"pack {pack_path!r} has worktree bytes that are not the HEAD blob: {detail}",
        )


def _tool_paths(name: str) -> tuple[str, str]:
    tool_path = f"scripts/{name}"
    return tool_path, f"{tool_path}.sha256"


def _require_clean_tool_sidecar(repository: Path, name: str) -> None:
    tool_path, sidecar_path = _tool_paths(name)
    dirty = _git(
        repository,
        "status",
        "--porcelain",
        "--",
        tool_path,
        sidecar_path,
    )
    if dirty:
        detail = dirty.decode("utf-8", errors="replace").strip()
        raise _refusal(
            "histsem_binding_mismatch",
            f"custody tool {name!r} or its sidecar is not the HEAD blob: {detail}",
        )


def _require_current_head_reviewable(repository: Path) -> None:
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
    _require_current_head_reviewable(repository)


def render_tool_sidecar(tool_bytes: bytes, name: str) -> bytes:
    """Render the one governed GNU sidecar format for a custody tool."""

    return readiness.gnu_sidecar(readiness.sha256_bytes(tool_bytes), name)


def _sidecar_diff(relative_path: str, old: bytes, new: bytes) -> str:
    before = old.decode("utf-8").splitlines(keepends=True)
    after = new.decode("utf-8").splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            before,
            after,
            fromfile=f"{relative_path}@old",
            tofile=f"{relative_path}@new",
        )
    )


def _head_blob(repository: Path, relative_path: str) -> bytes:
    code, raw, stderr = readiness._histsem_git(
        repository,
        "show",
        f"HEAD:{relative_path}",
    )
    if code != 0:
        detail = stderr.decode("utf-8", errors="replace").strip()
        raise _refusal(
            "histsem_history_unavailable",
            f"cannot read committed custody tool {relative_path!r}"
            f"{': ' + detail if detail else ''}",
        )
    return raw


def _prepare_tool_sidecars(
    repository: Path,
) -> list[tuple[str, Path, bytes, bytes, str]]:
    for name in CUSTODY_TOOL_SIDECARS:
        _require_clean_tool_sidecar(repository, name)
    _require_current_head_reviewable(repository)

    prepared: list[tuple[str, Path, bytes, bytes, str]] = []
    for name in CUSTODY_TOOL_SIDECARS:
        tool_relative, sidecar_relative = _tool_paths(name)
        tool_raw = _head_blob(repository, tool_relative)
        sidecar_path = repository / sidecar_relative
        try:
            old = sidecar_path.read_bytes()
        except OSError as exc:
            raise _refusal(
                "histsem_history_unavailable",
                f"cannot read custody-tool sidecar {sidecar_relative!r}: {exc}",
            ) from exc
        new = render_tool_sidecar(tool_raw, name)
        prepared.append(
            (
                name,
                sidecar_path,
                old,
                new,
                _sidecar_diff(sidecar_relative, old, new) if old != new else "",
            )
        )
    return prepared


def _write_tool_sidecars(
    prepared: list[tuple[str, Path, bytes, bytes, str]],
) -> tuple[list[str], list[str]]:
    written: list[tuple[Path, bytes]] = []
    try:
        for _name, path, old, new, _diff in prepared:
            if old != new:
                written.append((path, old))
                path.write_bytes(new)
                if path.read_bytes() != new:
                    raise OSError(f"written sidecar bytes differ from candidate: {path}")
    except BaseException:
        for path, old in reversed(written):
            path.write_bytes(old)
        raise
    return (
        [diff for _name, _path, _old, _new, diff in prepared if diff],
        [name for name, _path, old, new, _diff in prepared if old == new],
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


def _verify_whole_candidate(
    repository: Path,
    rows: tuple[Mapping[str, Any], ...],
) -> None:
    for row in rows:
        pack_id = str(row["pack_id"])
        pack_path = str(row["pack_path"])
        try:
            pack_root = _resolve_from(repository, Path(pack_path)).resolve(strict=True)
            pack_root.relative_to(repository)
        except (OSError, RuntimeError, ValueError) as exc:
            raise _refusal(
                "histsem_pinset_invalid",
                f"whole-candidate pack path is invalid for {pack_id!r}: {pack_path!r}",
            ) from exc
        try:
            _verify_candidate(repository, pack_root, rows)
        except readiness.HistoricalSemanticsError as exc:
            raise _refusal(
                exc.reason_code,
                f"whole-candidate verification refused for {pack_id}: {exc}",
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


def _refresh_write_backups(
    repository: Path,
    args: argparse.Namespace,
) -> list[tuple[Path, bool, bytes]]:
    pinset_path = _resolve_from(repository, args.pinset)
    output_path = pinset_path if args.output is None else _resolve_from(repository, args.output)
    paths = [output_path]
    if args.write_test_pin is not None:
        paths.append(_resolve_from(repository, args.write_test_pin))
    backups: list[tuple[Path, bool, bytes]] = []
    for path in dict.fromkeys(paths):
        existed = path.exists()
        backups.append((path, existed, path.read_bytes() if existed else b""))
    return backups


def _restore_backups(backups: list[tuple[Path, bool, bytes]]) -> None:
    for path, existed, raw in reversed(backups):
        _restore(path, existed, raw)


def _require_sidecar_write_separation(
    repository: Path,
    args: argparse.Namespace,
) -> None:
    pinset_path = _resolve_from(repository, args.pinset)
    output_path = (
        pinset_path if args.output is None else _resolve_from(repository, args.output)
    )
    test_pin_path = (
        None
        if args.write_test_pin is None
        else _resolve_from(repository, args.write_test_pin)
    )
    targets = [("pinset output", output_path)]
    if test_pin_path is not None:
        targets.append(("test pin", test_pin_path))
        if test_pin_path == output_path:
            raise _refusal(
                "histsem_pinset_invalid", "test pin file and pinset output must differ"
            )

    enumerated = _enumerated_pinset_paths(repository)
    if args.output is None and pinset_path not in enumerated:
        raise _refusal(
            "histsem_pinset_invalid",
            "in-place refresh requires an enumerated pinset member; use --output for a preview",
        )

    governed_paths = {
        _resolve_from(repository, Path(relative))
        for name in CUSTODY_TOOL_SIDECARS
        for relative in _tool_paths(name)
    }
    collisions = sorted(str(path) for _label, path in targets if path in governed_paths)
    if collisions:
        raise _refusal(
            "histsem_pinset_invalid",
            "pinset outputs must not target governed custody tools or sidecars: "
            + ", ".join(collisions),
        )

    scripts_root = _resolve_from(repository, Path("scripts"))
    script_targets = sorted(
        f"{label}: {path}" for label, path in targets if _is_within(path, scripts_root)
    )
    if script_targets:
        raise _refusal(
            "histsem_pinset_invalid",
            "pinset outputs must not target paths under repository scripts: "
            + ", ".join(script_targets),
        )

    other_members = sorted(
        f"{label}: {path}"
        for label, path in targets
        if path in enumerated and path != pinset_path
    )
    if other_members:
        raise _refusal(
            "histsem_pinset_invalid",
            "pinset outputs must not target an enumerated member other than --pinset: "
            + ", ".join(other_members),
        )

    if (
        args.output is not None
        and output_path not in enumerated
        and _is_within(output_path, repository)
    ):
        raise _refusal(
            "histsem_pinset_invalid",
            "a non-enumerated --output is a preview and must be outside the repository root",
        )


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
    _verify_whole_candidate(repository, candidate_rows)

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
    preview = output_path not in _enumerated_pinset_paths(repository)
    try:
        if changed:
            wrote_output = True
            output_path.write_bytes(candidate_raw)
            written_value, written_raw = _load_pinset(output_path)
            if written_raw != candidate_raw:
                raise _refusal("histsem_pinset_invalid", "written pinset bytes differ from candidate")
            written_rows = readiness._validate_histsem_pinset(written_value)
        if test_pin_path is not None and test_replacement != test_original:
            wrote_test = True
            test_pin_path.write_bytes(test_replacement)
        if changed and preview:
            for pack_id in requested:
                _verify_candidate(repository, pack_roots[pack_id], written_rows)
        elif changed:
            try:
                readiness.verify_all_receipt_histsem(
                    repository,
                    require_published=False,
                )
            except readiness.HistoricalSemanticsError as exc:
                raise _refusal(
                    exc.reason_code,
                    f"post-write whole-pinset verification refused: {exc}",
                ) from exc
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
    raw = b""
    diffs: list[str] = []
    current: list[str] = []
    sidecar_diffs: list[str] = []
    sidecar_current: list[str] = []
    try:
        repository = args.repository_root.resolve(strict=True)
        _require_sidecar_write_separation(repository, args)
        prepared = (
            _prepare_tool_sidecars(repository)
            if args.refresh_tool_sidecars
            else []
        )
        run_pinset_refresh = bool(
            args.refresh_row
            or args.print_pinset_sha256
            or args.write_test_pin is not None
            or args.output is not None
            or not args.refresh_tool_sidecars
        )
        backups = (
            _refresh_write_backups(repository, args)
            if args.refresh_tool_sidecars and run_pinset_refresh
            else []
        )
        try:
            if run_pinset_refresh:
                raw, diffs, current = refresh(args)
            if args.refresh_tool_sidecars:
                sidecar_diffs, sidecar_current = _write_tool_sidecars(prepared)
        except BaseException:
            _restore_backups(backups)
            raise
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
    if args.output is not None:
        output_path = _resolve_from(repository, args.output)
        if output_path not in _enumerated_pinset_paths(repository):
            sys.stdout.write(
                f"preview: {output_path} is not an enumerated pinset member and cannot be "
                "loaded by scripts/verify_receipt_histsem.py\n"
            )
    for pack_id in current:
        sys.stdout.write(f"row {pack_id} is already current\n")
    for diff in sidecar_diffs:
        sys.stdout.write(diff)
    for name in sidecar_current:
        sys.stdout.write(f"sidecar {name} is already current\n")
    if args.print_pinset_sha256:
        digest = readiness.sha256_bytes(raw)
        sys.stdout.write(f"pinset sha256: {digest}\n")
        sys.stdout.write(f'PINSET_SHA256 = "{digest}"\n')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
