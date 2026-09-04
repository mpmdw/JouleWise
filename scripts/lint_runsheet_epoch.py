#!/usr/bin/env python3
"""Check declared runsheet dependencies against named Git revisions.

The checker is deliberately read-only.  Ratification contracts take their
obligations from a ``# joulewise-epoch-lint:`` JSON declaration at the start
of every executable zsh block and require the runsheet to invoke this checker
once.  Historical replay contracts keep their explicitly labelled sidecar
checks.  Both modes name exact commit ids; a ratification contract may also
authenticate exact post-image bytes over its named executing base.  The
checker never edits either the runsheet or the checkout.

Three obligation kinds are supported:

* ``symbol_existence`` resolves a Python definition through the abstract
  syntax tree (AST), rather than accepting a matching string in a comment;
* ``contract_required_cli_inputs`` confines a command check to one fenced zsh
  block and requires every declared option in that same block; and
* ``file_line_coordinates`` compares a cited start/end pair with the AST
  boundaries of the declared Python definitions at the executing head.

Exit status is zero for a clean contract, one when any declared obligation
finds drift, and two when the contract or named Git objects cannot be read.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


CONTRACT_SCHEMA = "joulewise.runsheet_epoch_lint"
RESULT_SCHEMA = "joulewise.runsheet_epoch_lint.result"
OVERLAY_SCHEMA = "joulewise.runsheet_epoch_lint.patch_overlay"
DECLARATION_PREFIX = "# joulewise-epoch-lint: "
MODES = {"historical_replay", "ratification"}
KINDS = {
    "symbol_existence",
    "contract_required_cli_inputs",
    "file_line_coordinates",
}


class ContractError(ValueError):
    """A fail-closed error in the lint contract or named Git inputs."""


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise ContractError(detail)
    return result.stdout


def _resolve_commit(repo: Path, revision: object, label: str) -> str:
    if not isinstance(revision, str) or re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        raise ContractError(f"{label} must be a full lowercase 40-hex commit id")
    resolved = _git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}").strip()
    if resolved != revision:
        raise ContractError(f"{label} does not name that exact commit")
    return resolved


def _git_text(repo: Path, revision: str, path: object) -> str:
    if (
        not isinstance(path, str)
        or not path
        or Path(path).is_absolute()
        or ".." in Path(path).parts
    ):
        raise ContractError(f"source path must be repository-relative: {path!r}")
    return _git(repo, "show", f"{revision}:{path}")


def _definitions(text: str, path: str) -> dict[str, list[ast.AST]]:
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        raise ContractError(f"cannot parse {path}: {exc}") from exc
    definitions: dict[str, list[ast.AST]] = {}

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.parents: list[str] = []
            self.constant_scopes: list[bool] = [True]

        def _record(self, name: str, node: ast.AST) -> None:
            qualified = ".".join((*self.parents, name))
            definitions.setdefault(qualified, []).append(node)
            definitions.setdefault(name, []).append(node)

        def _visit(self, node: ast.AST) -> None:
            name = str(getattr(node, "name"))
            self._record(name, node)
            self.parents.append(name)
            self.constant_scopes.append(isinstance(node, ast.ClassDef))
            self.generic_visit(node)
            self.constant_scopes.pop()
            self.parents.pop()

        def visit_Assign(self, node: ast.Assign) -> None:
            if self.constant_scopes[-1]:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self._record(target.id, node)
            self.generic_visit(node)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            if self.constant_scopes[-1] and isinstance(node.target, ast.Name):
                self._record(node.target.id, node)
            self.generic_visit(node)

        visit_FunctionDef = _visit
        visit_AsyncFunctionDef = _visit
        visit_ClassDef = _visit

    Visitor().visit(tree)
    return definitions


def _resolve_definition(
    source: str, path: str, symbol: object
) -> tuple[ast.AST | None, str | None]:
    if not isinstance(symbol, str) or not symbol:
        return None, "symbol must be a nonempty string"
    try:
        matches = _definitions(source, path).get(symbol, [])
    except ContractError as exc:
        return None, str(exc)
    if not matches:
        return None, f"symbol {symbol!r} is absent from {path}"
    unique = {id(node): node for node in matches}
    if len(unique) != 1:
        lines = sorted(int(getattr(node, "lineno")) for node in unique.values())
        return None, f"symbol {symbol!r} is ambiguous in {path} at lines {lines}"
    return next(iter(unique.values())), None


def _zsh_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] | None = None
    for line in text.splitlines():
        if current is None:
            if line == "```zsh":
                current = []
            continue
        if line == "```":
            blocks.append("\n".join(current))
            current = None
        else:
            current.append(line)
    if current is not None:
        raise ContractError("runsheet has an unterminated column-zero zsh block")
    return blocks


def _occurrences(text: str, needle: object) -> int:
    return text.count(needle) if isinstance(needle, str) and needle else 0


def _expected_occurrences(check: Mapping[str, Any]) -> int:
    return int(check.get("reference_occurrences", 1))


def _finding(check: Mapping[str, Any], reason: str, detail: str) -> dict[str, str]:
    return {
        "check_id": str(check.get("id", "<missing>")),
        "detail": detail,
        "kind": str(check.get("kind", "<missing>")),
        "reason": reason,
    }


def _check_symbol(
    repo: Path,
    head: str,
    runsheet: str,
    check: Mapping[str, Any],
    cache: dict[str, str],
) -> list[dict[str, str]]:
    reference = check.get("reference")
    count = _occurrences(runsheet, reference)
    expected = _expected_occurrences(check)
    findings: list[dict[str, str]] = []
    if count != expected:
        findings.append(
            _finding(
                check,
                "runsheet_reference_count_mismatch",
                f"reference occurs {count} times; contract declares {expected}",
            )
        )
    path = check.get("source_path")
    if not isinstance(path, str):
        return findings + [_finding(check, "check_invalid", "source_path must be a string")]
    try:
        if path not in cache:
            cache[path] = _git_text(repo, head, path)
        source = cache[path]
    except ContractError as exc:
        return findings + [_finding(check, "source_unreadable", str(exc))]
    _node, error = _resolve_definition(source, path, check.get("symbol"))
    if error:
        findings.append(_finding(check, "symbol_missing_or_ambiguous", error))
    return findings


def _logical_commands(block: str) -> list[str]:
    commands: list[str] = []
    continued: list[str] = []
    for raw_line in block.splitlines():
        stripped = raw_line.strip()
        if not continued and (not stripped or stripped.startswith("#")):
            continue
        carries = raw_line.rstrip().endswith("\\")
        part = raw_line.rstrip()
        if carries:
            part = part[:-1]
        continued.append(part.strip())
        if not carries:
            commands.append(" ".join(continued))
            continued = []
    if continued:
        commands.append(" ".join(continued))
    return commands


def _command_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command, comments=True, posix=True)
    except ValueError as exc:
        raise ContractError(f"cannot parse zsh command: {exc}") from exc


def _try_command_tokens(command: str) -> list[str] | None:
    try:
        return _command_tokens(command)
    except ContractError:
        return None


def _starts_with(tokens: Sequence[str], prefix: Sequence[str]) -> bool:
    return list(tokens[: len(prefix)]) == list(prefix)


def _is_python_command(token: str) -> bool:
    name = Path(token).name
    return token == "$PY" or name == "python" or name.startswith("python3")


def _is_ratification_invocation(tokens: Sequence[str], contract_path: str) -> bool:
    command = tokens[2:] if len(tokens) >= 2 and tokens[0] == "capture" else tokens
    if len(command) < 3:
        return False
    return (
        _is_python_command(command[0])
        and Path(command[1]).name == "lint_runsheet_epoch.py"
        and command[2] == contract_path
    )


def _check_cli(runsheet: str, check: Mapping[str, Any]) -> list[dict[str, str]]:
    try:
        blocks = _zsh_blocks(runsheet)
    except ContractError as exc:
        return [_finding(check, "runsheet_invalid", str(exc))]
    anchor = check.get("block_anchor")
    if not isinstance(anchor, str) or not anchor:
        return [_finding(check, "check_invalid", "block_anchor must be a nonempty string")]
    anchor_tokens = _command_tokens(anchor)
    matches = [
        block
        for block in blocks
        if any(
            tokens is not None and _starts_with(tokens, anchor_tokens)
            for logical in _logical_commands(block)
            for tokens in [_try_command_tokens(logical)]
        )
    ]
    if len(matches) != 1:
        return [
            _finding(
                check,
                "command_block_not_unique",
                f"block anchor {anchor!r} occurs in {len(matches)} zsh blocks",
            )
        ]
    command = check.get("command")
    command_tokens = _command_tokens(str(command)) if isinstance(command, str) else []
    invocations = [
        tokens
        for logical in _logical_commands(matches[0])
        for tokens in [_try_command_tokens(logical)]
        if tokens is not None
        and command_tokens
        and _starts_with(tokens, anchor_tokens)
        and _starts_with(tokens[len(anchor_tokens) :], command_tokens)
    ]
    if len(invocations) != 1:
        return [
            _finding(
                check,
                "command_not_unique",
                f"command {command!r} occurs in {len(invocations)} logical commands in the anchored block",
            )
        ]
    invocation = invocations[0]
    flags = check.get("required_flags")
    missing = [
        flag
        for flag in flags
        if not any(token == flag or token.startswith(f"{flag}=") for token in invocation)
    ]
    if missing:
        return [
            _finding(
                check,
                "contract_required_cli_input_missing",
                f"anchored command block omits {missing}",
            )
        ]
    return []


def _check_coordinates(
    repo: Path,
    head: str,
    runsheet: str,
    check: Mapping[str, Any],
    cache: dict[str, str],
) -> list[dict[str, str]]:
    reference = check.get("reference")
    count = _occurrences(runsheet, reference)
    expected = _expected_occurrences(check)
    findings: list[dict[str, str]] = []
    if count != expected:
        findings.append(
            _finding(
                check,
                "runsheet_reference_count_mismatch",
                f"reference occurs {count} times; contract declares {expected}",
            )
        )
    path = check.get("source_path")
    if not isinstance(path, str):
        return findings + [_finding(check, "check_invalid", "source_path must be a string")]
    try:
        if path not in cache:
            cache[path] = _git_text(repo, head, path)
        source = cache[path]
    except ContractError as exc:
        return findings + [_finding(check, "source_unreadable", str(exc))]
    start, start_error = _resolve_definition(source, path, check.get("start_symbol"))
    end, end_error = _resolve_definition(source, path, check.get("end_symbol"))
    if start_error or end_error:
        return findings + [
            _finding(
                check,
                "coordinate_symbol_missing_or_ambiguous",
                "; ".join(value for value in (start_error, end_error) if value),
            )
        ]
    cited_start = check.get("cited_start")
    cited_end = check.get("cited_end")
    decorators = getattr(start, "decorator_list", [])
    actual_start = min(
        [int(getattr(start, "lineno")), *[int(item.lineno) for item in decorators]]
    )
    actual_end = int(getattr(end, "end_lineno", getattr(end, "lineno")))
    if (cited_start, cited_end) != (actual_start, actual_end):
        findings.append(
            _finding(
                check,
                "file_line_coordinates_stale",
                f"cites {path}:{cited_start}-{cited_end}; definitions span {actual_start}-{actual_end}",
            )
        )
    return findings


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _valid_source_path(path: object) -> bool:
    return (
        isinstance(path, str)
        and bool(path)
        and not Path(path).is_absolute()
        and ".." not in Path(path).parts
    )


def _patch_overlay(
    repo: Path,
    raw: object,
    executing_head: str,
    root: Path,
) -> dict[str, str]:
    if not isinstance(raw, Mapping):
        raise ContractError("patch_overlay must be an object")
    overlay = dict(raw)
    if set(overlay) != {"schema", "base_revision", "files", "sha256"}:
        raise ContractError("patch_overlay has unexpected or missing fields")
    if overlay["schema"] != OVERLAY_SCHEMA:
        raise ContractError("patch_overlay schema mismatch")
    base = _resolve_commit(repo, overlay["base_revision"], "patch_overlay.base_revision")
    if base != executing_head:
        raise ContractError("patch_overlay base_revision must equal executing_head")
    files = overlay["files"]
    if not isinstance(files, list) or not files:
        raise ContractError("patch_overlay files must be a nonempty array")
    authenticated = {key: overlay[key] for key in ("schema", "base_revision", "files")}
    if overlay["sha256"] != _sha256(_canonical_json(authenticated)):
        raise ContractError("patch_overlay manifest digest mismatch")
    if root.exists():
        raise ContractError(f"patch overlay root is occupied: {root}")
    root.mkdir(parents=False)
    sources: dict[str, str] = {}
    previous = ""
    for index, item in enumerate(files):
        if not isinstance(item, Mapping) or set(item) != {
            "path",
            "base_sha256",
            "result_sha256",
            "content",
        }:
            raise ContractError(f"patch_overlay file {index} is malformed")
        path = item["path"]
        if not _valid_source_path(path):
            raise ContractError(f"patch_overlay file {index} path is invalid")
        assert isinstance(path, str)
        if path <= previous or path in sources:
            raise ContractError("patch_overlay file paths must be unique and sorted")
        previous = path
        content = item["content"]
        if not isinstance(content, str):
            raise ContractError(f"patch_overlay content for {path} must be UTF-8 text")
        base_raw = _git(repo, "show", f"{base}:{path}").encode("utf-8")
        if item["base_sha256"] != _sha256(base_raw):
            raise ContractError(f"patch_overlay base digest mismatch for {path}")
        result_raw = content.encode("utf-8")
        if item["result_sha256"] != _sha256(result_raw):
            raise ContractError(f"patch_overlay result digest mismatch for {path}")
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(result_raw)
        sources[path] = destination.read_text(encoding="utf-8")
    return sources


def _validate_checks(raw: object) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise ContractError("checks must be a nonempty array")
    checks = [dict(check) if isinstance(check, Mapping) else check for check in raw]
    seen: set[str] = set()
    fields = {
        "symbol_existence": {
            "required": {"id", "kind", "reference", "source_path", "symbol"},
            "optional": {"reference_occurrences"},
        },
        "contract_required_cli_inputs": {
            "required": {"id", "kind", "block_anchor", "command", "required_flags"},
            "optional": set(),
        },
        "file_line_coordinates": {
            "required": {
                "id",
                "kind",
                "reference",
                "source_path",
                "start_symbol",
                "end_symbol",
                "cited_start",
                "cited_end",
            },
            "optional": {"reference_occurrences"},
        },
    }
    for index, check in enumerate(checks):
        if not isinstance(check, Mapping):
            raise ContractError(f"check {index} must be an object")
        check_id = check.get("id")
        if not isinstance(check_id, str) or not check_id or check_id in seen:
            raise ContractError(f"check {index} id must be unique and nonempty")
        seen.add(check_id)
        kind = check.get("kind")
        if kind not in KINDS:
            raise ContractError(f"check {check_id} has unknown kind {kind!r}")
        expected_fields = fields[str(kind)]
        required_fields = expected_fields["required"]
        allowed_fields = required_fields | expected_fields["optional"]
        if not required_fields <= set(check) <= allowed_fields:
            raise ContractError(
                f"check {check_id} must contain {sorted(required_fields)}"
                f" with optional {sorted(expected_fields['optional'])}"
            )
        occurrences = check.get("reference_occurrences", 1)
        if (
            isinstance(occurrences, bool)
            or not isinstance(occurrences, int)
            or occurrences < 1
        ):
            raise ContractError(
                f"check {check_id} reference_occurrences must be a positive integer"
            )
        if kind == "contract_required_cli_inputs":
            flags = check.get("required_flags")
            if (
                not isinstance(check.get("block_anchor"), str)
                or not check["block_anchor"]
                or not isinstance(check.get("command"), str)
                or not check["command"]
                or not isinstance(flags, list)
                or not flags
                or not all(
                    isinstance(flag, str) and flag.startswith("--") for flag in flags
                )
            ):
                raise ContractError(
                    f"check {check_id} command fields and required_flags are invalid"
                )
        if kind == "file_line_coordinates":
            coordinates = (check.get("cited_start"), check.get("cited_end"))
            if any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in coordinates
            ):
                raise ContractError(
                    f"check {check_id} cited coordinates must be integers"
                )
    return checks  # type: ignore[return-value]


def _inline_checks(
    runsheet: str, contract_path: str
) -> tuple[list[dict[str, Any]], str]:
    blocks = _zsh_blocks(runsheet)
    if not blocks:
        raise ContractError("ratification runsheet has no executable zsh blocks")
    checks: list[dict[str, Any]] = []
    ratification_count = 0
    for index, block in enumerate(blocks, start=1):
        lines = [line for line in block.splitlines() if line.strip()]
        if not lines or not lines[0].startswith(DECLARATION_PREFIX):
            raise ContractError(f"executable zsh block {index} has no inline declaration")
        try:
            declaration = json.loads(lines[0][len(DECLARATION_PREFIX) :])
        except json.JSONDecodeError as exc:
            raise ContractError(f"inline declaration {index} is invalid JSON: {exc}") from exc
        if not isinstance(declaration, Mapping) or set(declaration) != {"checks"}:
            raise ContractError(f"inline declaration {index} must contain only checks")
        declared = declaration["checks"]
        if not isinstance(declared, list):
            raise ContractError(f"inline declaration {index} checks must be an array")
        checks.extend(declared)
        for logical in _logical_commands(block):
            tokens = _try_command_tokens(logical)
            if tokens is None:
                continue
            if _is_ratification_invocation(tokens, contract_path):
                ratification_count += 1
    if ratification_count != 1:
        raise ContractError(
            "runsheet must invoke its exact epoch-lint contract once; "
            f"found {ratification_count} invocations"
        )
    check_text = "\n".join(
        line
        for line in runsheet.splitlines()
        if not line.startswith(DECLARATION_PREFIX)
    )
    return _validate_checks(checks), check_text


def _validate_contract(raw: object) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ContractError("contract must be a JSON object")
    contract = dict(raw)
    base_fields = {"schema", "mode", "runsheet", "runsheet_revision", "executing_head"}
    mode = contract.get("mode")
    if mode not in MODES:
        raise ContractError(f"mode must be one of {sorted(MODES)}")
    mode_fields = {"checks"} if mode == "historical_replay" else {"contract_path"}
    allowed = base_fields | mode_fields | {"patch_overlay"}
    required = base_fields | mode_fields
    if not required <= set(contract) <= allowed:
        raise ContractError(
            f"{mode} contract must contain {sorted(required)} with optional patch_overlay"
        )
    if contract["schema"] != CONTRACT_SCHEMA:
        raise ContractError(f"unsupported schema {contract['schema']!r}")
    if mode == "historical_replay":
        contract["checks"] = _validate_checks(contract["checks"])
    else:
        path = contract["contract_path"]
        if not _valid_source_path(path):
            raise ContractError("contract_path must be repository-relative")
    return contract


def lint_contract(
    repo: Path,
    raw: object,
    *,
    overlay_root: Path | None = None,
) -> dict[str, Any]:
    contract = _validate_contract(raw)
    runsheet_revision = _resolve_commit(
        repo, contract["runsheet_revision"], "runsheet_revision"
    )
    executing_head = _resolve_commit(repo, contract["executing_head"], "executing_head")
    runsheet = _git_text(repo, runsheet_revision, contract["runsheet"])
    if contract["mode"] == "historical_replay":
        checks = contract["checks"]
        check_text = runsheet
    else:
        checks, check_text = _inline_checks(runsheet, contract["contract_path"])
    findings: list[dict[str, str]] = []
    source_cache: dict[str, str] = {}
    temporary: tempfile.TemporaryDirectory[str] | None = None
    overlay_file_count = 0
    try:
        if "patch_overlay" in contract:
            if overlay_root is None:
                temporary = tempfile.TemporaryDirectory(prefix="epoch-lint-")
                overlay_root = Path(temporary.name) / "overlay"
            overlay_sources = _patch_overlay(
                repo, contract["patch_overlay"], executing_head, overlay_root
            )
            overlay_file_count = len(overlay_sources)
            source_cache.update(overlay_sources)
        for check in checks:
            kind = check["kind"]
            if kind == "symbol_existence":
                findings.extend(
                    _check_symbol(repo, executing_head, check_text, check, source_cache)
                )
            elif kind == "contract_required_cli_inputs":
                findings.extend(_check_cli(check_text, check))
            else:
                findings.extend(
                    _check_coordinates(
                        repo, executing_head, check_text, check, source_cache
                    )
                )
        return {
            "check_count": len(checks),
            "executing_head": executing_head,
            "finding_count": len(findings),
            "findings": findings,
            "mode": contract["mode"],
            "overlay_file_count": overlay_file_count,
            "runsheet": contract["runsheet"],
            "runsheet_revision": runsheet_revision,
            "schema": RESULT_SCHEMA,
            "status": "PASS" if not findings else "REFUSE",
        }
    finally:
        if temporary is not None:
            temporary.cleanup()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--overlay-root", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        raw = json.loads(args.contract.read_text(encoding="utf-8"))
        result = lint_contract(args.repository, raw, overlay_root=args.overlay_root)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ContractError) as exc:
        error = {
            "detail": str(exc),
            "reason": "epoch_lint_input_invalid",
            "status": "ERROR",
        }
        sys.stderr.write(json.dumps(error, sort_keys=True, ensure_ascii=False) + "\n")
        return 2
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
