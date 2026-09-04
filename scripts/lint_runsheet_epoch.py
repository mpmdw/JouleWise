#!/usr/bin/env python3
"""Check declared runsheet dependencies against named Git revisions.

The checker is deliberately read-only.  Its JSON contract identifies the
runsheet revision, the head whose source a step executes, and an explicit set
of obligations.  It never edits either the runsheet or the checkout.

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
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


CONTRACT_SCHEMA = "joulewise.runsheet_epoch_lint"
RESULT_SCHEMA = "joulewise.runsheet_epoch_lint.result"
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
    if not isinstance(revision, str) or not revision:
        raise ContractError(f"{label} must be a nonempty Git revision")
    return _git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}").strip()


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

        def _visit(self, node: ast.AST) -> None:
            name = str(getattr(node, "name"))
            qualified = ".".join((*self.parents, name))
            definitions.setdefault(qualified, []).append(node)
            definitions.setdefault(name, []).append(node)
            self.parents.append(name)
            self.generic_visit(node)
            self.parents.pop()

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
        source = cache.setdefault(path, _git_text(repo, head, path))
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


def _check_cli(runsheet: str, check: Mapping[str, Any]) -> list[dict[str, str]]:
    try:
        blocks = _zsh_blocks(runsheet)
    except ContractError as exc:
        return [_finding(check, "runsheet_invalid", str(exc))]
    anchor = check.get("block_anchor")
    if not isinstance(anchor, str) or not anchor:
        return [_finding(check, "check_invalid", "block_anchor must be a nonempty string")]
    matches = [block for block in blocks if anchor in block]
    if len(matches) != 1:
        return [
            _finding(
                check,
                "command_block_not_unique",
                f"block anchor {anchor!r} occurs in {len(matches)} zsh blocks",
            )
        ]
    command = check.get("command")
    invocations = [
        logical
        for logical in _logical_commands(matches[0])
        if isinstance(command, str) and command and command in logical
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
        if re.search(
            rf"(?<![A-Za-z0-9_-]){re.escape(flag)}(?![A-Za-z0-9_-])",
            invocation,
        )
        is None
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
        source = cache.setdefault(path, _git_text(repo, head, path))
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
    actual_start = int(getattr(start, "lineno"))
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


def _validate_contract(raw: object) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ContractError("contract must be a JSON object")
    contract = dict(raw)
    required = {"schema", "runsheet", "runsheet_revision", "executing_head", "checks"}
    if set(contract) != required:
        raise ContractError(f"contract must have exactly {sorted(required)}")
    if contract["schema"] != CONTRACT_SCHEMA:
        raise ContractError(f"unsupported schema {contract['schema']!r}")
    if not isinstance(contract["checks"], list) or not contract["checks"]:
        raise ContractError("checks must be a nonempty array")
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
    for index, check in enumerate(contract["checks"]):
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
        if set(check) != allowed_fields and not (
            required_fields <= set(check) <= allowed_fields
        ):
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
                not isinstance(flags, list)
                or not flags
                or not all(
                    isinstance(flag, str) and flag.startswith("--") for flag in flags
                )
            ):
                raise ContractError(
                    f"check {check_id} required_flags must be a nonempty option-name array"
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
    return contract


def lint_contract(repo: Path, raw: object) -> dict[str, Any]:
    contract = _validate_contract(raw)
    runsheet_revision = _resolve_commit(
        repo, contract["runsheet_revision"], "runsheet_revision"
    )
    executing_head = _resolve_commit(repo, contract["executing_head"], "executing_head")
    runsheet = _git_text(repo, runsheet_revision, contract["runsheet"])
    findings: list[dict[str, str]] = []
    source_cache: dict[str, str] = {}
    for check in contract["checks"]:
        kind = check["kind"]
        if kind == "symbol_existence":
            findings.extend(_check_symbol(repo, executing_head, runsheet, check, source_cache))
        elif kind == "contract_required_cli_inputs":
            findings.extend(_check_cli(runsheet, check))
        else:
            findings.extend(
                _check_coordinates(repo, executing_head, runsheet, check, source_cache)
            )
    return {
        "check_count": len(contract["checks"]),
        "executing_head": executing_head,
        "finding_count": len(findings),
        "findings": findings,
        "runsheet": contract["runsheet"],
        "runsheet_revision": runsheet_revision,
        "schema": RESULT_SCHEMA,
        "status": "PASS" if not findings else "REFUSE",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        raw = json.loads(args.contract.read_text(encoding="utf-8"))
        result = lint_contract(args.repository, raw)
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
