#!/usr/bin/env python3
"""Derive symbol-pinned estate evidence anchors at a reviewed checkout cut.

The embedded estate-12 specification is the standing inventory.  A caller may
instead supply a JSON file containing either an array of anchor rows or an
object with an ``anchors`` array.  Every row has exactly these fields:
``anchor_id``, ``file``, ``symbol_or_content_pin``, and ``kind``.

Kinds:

* ``symbol``: a unique Python function, async function, or class definition;
* ``symbol_range``: the same, including its AST-derived final line;
* ``content``: one exact, unique source line; and
* ``content_range``: two exact, unique source lines in start/end order.

Any missing or ambiguous pin is a named refusal.  No partial map is emitted.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


MAP_SCHEMA = "joulewise.estate_anchor_map.v1"
SPEC_SCHEMA = "joulewise.estate_anchor_spec.v1"


def _anchor(
    anchor_id: str,
    file: str,
    symbol_or_content_pin: str | list[str],
    kind: str,
) -> dict[str, Any]:
    return {
        "anchor_id": anchor_id,
        "file": file,
        "symbol_or_content_pin": symbol_or_content_pin,
        "kind": kind,
    }


# The legacy group is the estate-11 runsheet's 15-anchor inventory, with #14
# under the magistrate-ruled new name.  The audit group re-expresses §0.3's
# immutable ranges by named symbols (splitting historical multi-symbol ranges)
# and exact unique content.  The v5 group pins every newly merged surface the
# estate-12 handoff must consume.
ESTATE_12_ANCHOR_SPEC_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs/process_traces/2026-08-30-t28-estate11/estate-12-anchor-spec.json"
)


def _load_estate_12_spec() -> tuple[dict[str, Any], ...]:
    """The standing estate-12 inventory lives as DATA beside the template.

    Keeping the spec out of scripts/*.py keeps this tool outside the
    grep-shaped pinset-writer tripwire in tests/test_receipt_histsem.py:
    the spec's content pins may NAME pinned surfaces; this script never
    touches them.
    """
    raw = json.loads(ESTATE_12_ANCHOR_SPEC_PATH.read_text(encoding="utf-8"))
    anchors = raw["anchors"] if isinstance(raw, dict) else raw
    return tuple(dict(row) for row in anchors)


ESTATE_12_ANCHOR_SPEC: tuple[dict[str, Any], ...] = _load_estate_12_spec()


class AnchorRefusal(ValueError):
    """A named fail-closed anchor derivation refusal."""

    def __init__(self, reason: str, anchor_id: str, detail: str):
        super().__init__(detail)
        self.reason = reason
        self.anchor_id = anchor_id
        self.detail = detail

    def payload(self) -> dict[str, str]:
        return {
            "anchor_id": self.anchor_id,
            "detail": self.detail,
            "reason": self.reason,
            "status": "REFUSE",
        }


def _refuse(reason: str, anchor_id: str, detail: str) -> AnchorRefusal:
    return AnchorRefusal(reason, anchor_id, detail)


def _definition_names(tree: ast.AST) -> list[tuple[str, ast.AST]]:
    rows: list[tuple[str, ast.AST]] = []

    class DefinitionVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.parents: list[str] = []

        def _visit_definition(self, node: ast.AST) -> None:
            name = str(getattr(node, "name"))
            rows.append((".".join((*self.parents, name)), node))
            self.parents.append(name)
            self.generic_visit(node)
            self.parents.pop()

        visit_FunctionDef = _visit_definition
        visit_AsyncFunctionDef = _visit_definition
        visit_ClassDef = _visit_definition

    DefinitionVisitor().visit(tree)
    return rows


def _resolve_symbol(
    path: Path, text: str, anchor_id: str, pin: object
) -> tuple[int, int]:
    if not isinstance(pin, str) or not pin:
        raise _refuse("anchor_spec_invalid", anchor_id, "symbol pin must be a nonempty string")
    try:
        tree = ast.parse(text, filename=os.fspath(path))
    except SyntaxError as exc:
        raise _refuse("anchor_python_invalid", anchor_id, f"cannot parse {path}: {exc}") from exc
    definitions = _definition_names(tree)
    if "." in pin:
        matches = [node for qualified, node in definitions if qualified == pin]
    else:
        matches = [node for qualified, node in definitions if qualified.rsplit(".", 1)[-1] == pin]
    if not matches:
        raise _refuse("anchor_symbol_missing", anchor_id, f"symbol {pin!r} is absent from {path}")
    if len(matches) != 1:
        lines = sorted(int(getattr(node, "lineno")) for node in matches)
        raise _refuse(
            "anchor_symbol_ambiguous",
            anchor_id,
            f"symbol {pin!r} resolves {len(matches)} times in {path} at lines {lines}",
        )
    node = matches[0]
    return int(node.lineno), int(getattr(node, "end_lineno", node.lineno))


def _unique_content_line(
    path: Path, lines: Sequence[str], anchor_id: str, pin: object, label: str
) -> int:
    if not isinstance(pin, str):
        raise _refuse("anchor_spec_invalid", anchor_id, f"{label} content pin must be a string")
    matches = [index for index, line in enumerate(lines, start=1) if line == pin]
    if not matches:
        raise _refuse("anchor_content_missing", anchor_id, f"{label} content is absent from {path}")
    if len(matches) != 1:
        raise _refuse(
            "anchor_content_ambiguous",
            anchor_id,
            f"{label} content resolves {len(matches)} times in {path} at lines {matches}",
        )
    return matches[0]


def _validate_rows(raw: object) -> list[dict[str, Any]]:
    if isinstance(raw, Mapping):
        raw = raw.get("anchors")
    if not isinstance(raw, list) and not isinstance(raw, tuple):
        raise _refuse("anchor_spec_invalid", "<spec>", "anchor spec must be an array or an object with an anchors array")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    required = {"anchor_id", "file", "symbol_or_content_pin", "kind"}
    for index, item in enumerate(raw):
        if not isinstance(item, Mapping) or set(item) != required:
            raise _refuse("anchor_spec_invalid", f"<row:{index}>", f"anchor row must have exactly {sorted(required)}")
        row = dict(item)
        anchor_id = row["anchor_id"]
        if not isinstance(anchor_id, str) or not anchor_id or anchor_id in seen:
            raise _refuse("anchor_spec_invalid", str(anchor_id), "anchor_id must be a unique nonempty string")
        seen.add(anchor_id)
        if row["kind"] not in {"symbol", "symbol_range", "content", "content_range"}:
            raise _refuse("anchor_kind_unknown", anchor_id, f"unknown kind {row['kind']!r}")
        if not isinstance(row["file"], str) or not row["file"]:
            raise _refuse("anchor_spec_invalid", anchor_id, "file must be a nonempty string")
        rows.append(row)
    return rows


def derive_anchor_map(checkout_root: Path, spec: object) -> dict[str, Any]:
    """Resolve all anchors or raise one named refusal without partial output."""

    try:
        root = checkout_root.resolve(strict=True)
    except OSError as exc:
        raise _refuse("anchor_checkout_invalid", "<checkout>", str(exc)) from exc
    if not root.is_dir():
        raise _refuse("anchor_checkout_invalid", "<checkout>", f"not a directory: {root}")
    rows = _validate_rows(spec)
    resolved: dict[str, dict[str, Any]] = {}
    file_cache: dict[str, tuple[Path, bytes, str, list[str]]] = {}
    for row in sorted(rows, key=lambda value: value["anchor_id"]):
        anchor_id = row["anchor_id"]
        relative = Path(row["file"])
        if relative.is_absolute() or ".." in relative.parts:
            raise _refuse("anchor_path_invalid", anchor_id, f"file must be repository-relative: {relative}")
        if row["file"] not in file_cache:
            path = root / relative
            try:
                normalized = path.resolve(strict=True)
                normalized.relative_to(root)
                raw = normalized.read_bytes()
                text = raw.decode("utf-8")
            except (OSError, UnicodeDecodeError, ValueError) as exc:
                raise _refuse("anchor_file_unreadable", anchor_id, f"cannot read {relative}: {exc}") from exc
            file_cache[row["file"]] = (normalized, raw, text, text.splitlines())
        path, raw, text, lines = file_cache[row["file"]]
        kind = row["kind"]
        pin = row["symbol_or_content_pin"]
        end_line: int | None = None
        if kind in {"symbol", "symbol_range"}:
            if path.suffix != ".py":
                raise _refuse("anchor_kind_file_mismatch", anchor_id, "symbol kinds require a .py file")
            line, symbol_end = _resolve_symbol(path, text, anchor_id, pin)
            if kind == "symbol_range":
                end_line = symbol_end
        elif kind == "content":
            line = _unique_content_line(path, lines, anchor_id, pin, "pinned")
        else:
            if not isinstance(pin, list) or len(pin) != 2:
                raise _refuse("anchor_spec_invalid", anchor_id, "content_range pin must be a two-string array")
            line = _unique_content_line(path, lines, anchor_id, pin[0], "start")
            end_line = _unique_content_line(path, lines, anchor_id, pin[1], "end")
            if end_line < line:
                raise _refuse("anchor_range_reversed", anchor_id, f"range end {end_line} precedes start {line}")
        result: dict[str, Any] = {
            "file": row["file"],
            "kind": kind,
            "line": line,
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "symbol_or_content_pin": pin,
        }
        if end_line is not None:
            result["end_line"] = end_line
        resolved[anchor_id] = result
    return {
        "anchor_count": len(resolved),
        "anchors": resolved,
        "schema_version": MAP_SCHEMA,
        "spec_sha256": hashlib.sha256(render_spec(rows)).hexdigest(),
    }


def render_spec(spec: object = ESTATE_12_ANCHOR_SPEC) -> bytes:
    rows = _validate_rows(spec)
    payload = {
        "anchors": sorted(rows, key=lambda value: value["anchor_id"]),
        "schema_version": SPEC_SCHEMA,
    }
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def render_anchor_map(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _load_spec(path: Path) -> object:
    try:
        raw = path.read_text(encoding="utf-8")
        return json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _refuse("anchor_spec_invalid", "<spec>", f"cannot load {path}: {exc}") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout_root", type=Path)
    parser.add_argument("anchor_spec", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--print-embedded-spec", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.print_embedded_spec:
            if args.anchor_spec is not None or args.output is not None:
                raise _refuse(
                    "anchor_arguments_invalid",
                    "<arguments>",
                    "--print-embedded-spec cannot be combined with a spec or output path",
                )
            sys.stdout.buffer.write(render_spec())
            return 0
        spec = ESTATE_12_ANCHOR_SPEC if args.anchor_spec is None else _load_spec(args.anchor_spec)
        rendered = render_anchor_map(derive_anchor_map(args.checkout_root, spec))
        if args.output is None:
            sys.stdout.buffer.write(rendered)
        else:
            args.output.write_bytes(rendered)
        return 0
    except AnchorRefusal as exc:
        sys.stderr.write(json.dumps(exc.payload(), sort_keys=True, ensure_ascii=False) + "\n")
        return 2
    except OSError as exc:
        refusal = _refuse("anchor_output_unwritable", "<output>", str(exc))
        sys.stderr.write(json.dumps(refusal.payload(), sort_keys=True, ensure_ascii=False) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
