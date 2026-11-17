#!/usr/bin/env python3
"""Validate typed RUN_STATE items and display their recorded or derived status."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import time

if __package__:
    from .gen_current import FENCE, HEADING, MAX_EPOCH, MIN_EPOCH, ROOT, _epoch
else:
    from gen_current import FENCE, HEADING, MAX_EPOCH, MIN_EPOCH, ROOT, _epoch


SCHEMA = "joulewise.run_state_item.v1"
OWNERS = ("lead", "magistrate", "research_lead", "ed")
INITIAL = ("DRAFT", "ISSUED", "CLOSED")
SETTABLE = ("ISSUED", "ARMED", "CLOSED", "VOID", "EXPIRED")
LEGAL = {"DRAFT": {"ISSUED", "VOID", "EXPIRED", "SUPERSEDED"},
         "ISSUED": {"ARMED", "CLOSED", "VOID", "EXPIRED", "SUPERSEDED"},
         "ARMED": {"CLOSED", "ISSUED"},
         "CLOSED": {"SUPERSEDED"},
         "VOID": set(), "EXPIRED": set(), "SUPERSEDED": set()}
OPEN = ("DRAFT", "ISSUED", "ARMED")
TOP_MARKER_PREFIX = "<!-- RUN_STATE TYPED ITEMS:"
LEGACY_MARKER_PREFIX = "<!-- RUN_STATE LEGACY ITEMS"
LEGACY_MARKER_RE = re.compile(r"^<!-- RUN_STATE LEGACY ITEMS below: prose, not typed; cutover ([1-9][0-9]*) -->$")
REFERENCE = re.compile(r"[1-9][0-9]*[a-z]?")
HEADER_KEYS = {"schema", "number", "owner", "status", "issued_epoch_s",
               "expires_epoch_s", "supersedes", "sets"}
SET_KEYS = {"item", "status", "at_epoch_s"}


@dataclass(frozen=True)
class ItemError:
    line: int
    code: str
    detail: str

    def __str__(self) -> str:
        return f"RUN_STATE line {self.line}: {self.code}: {self.detail}"


@dataclass(frozen=True)
class Item:
    number: int
    line: int
    heading: str
    header: dict


@dataclass(frozen=True)
class Parsed:
    cutover: int | None
    top_line: int | None
    items: tuple[Item, ...]
    legacy_numbers: frozenset[str]
    errors: tuple[ItemError, ...]


@dataclass(frozen=True)
class _Line:
    number: int
    text: str
    kind: str
    content: tuple[str, ...] = ()


def canonical(header: dict) -> str:
    return json.dumps(header, sort_keys=True, ensure_ascii=False, separators=(", ", ": "), allow_nan=False)


def _scan(text: str):
    """Yield only fence openers and lines outside fences, with one-based locations."""
    lines = text.split("\n")
    fence = None
    index = 0
    while index < len(lines):
        line = lines[index].removesuffix("\r")
        index += 1
        if fence is not None:
            if fence.fullmatch(line):
                fence = None
            continue
        kind = "blank" if not line.strip() else "prose"
        if line.startswith(TOP_MARKER_PREFIX):
            kind = "top"
        elif line.startswith(LEGACY_MARKER_PREFIX):
            kind = "legacy"
        elif HEADING.match(line):
            kind = "heading"
        elif line in ("```item", "```pointer"):
            kind = line[3:]
            end = index
            while end < len(lines) and lines[end].removesuffix("\r") != "```":
                if kind == "item" and (lines[end].startswith((TOP_MARKER_PREFIX, LEGACY_MARKER_PREFIX, "```item"))
                                       or HEADING.match(lines[end])):
                    break
                end += 1
            if end < len(lines) and lines[end].removesuffix("\r") == "```":
                yield _Line(index, line, kind,
                            tuple(row.removesuffix("\r") for row in lines[index:end]))
                index = end + 1
                continue
            yield _Line(index, line, "unterminated_" + kind)
            index = end
            continue
        elif match := FENCE.fullmatch(line):
            fence = re.compile(r"[ \t]*" + re.escape(match[1][0]) + "{" + str(len(match[1])) + r",}[ \t]*")
        yield _Line(index, line, kind)


def heading_lines(text: str):
    """Yield (line, numeric part, suffix) for headings outside fenced examples."""
    for line in _scan(text):
        if line.kind == "heading":
            match = HEADING.match(line.text)
            yield line.number, int(match[1]), match[2]


def _markers(lines: list[_Line], errors: list[ItemError]) -> tuple[int | None, int | None, int | None]:
    tops = [line for line in lines if line.kind == "top"]
    legacies = [line for line in lines if line.kind == "legacy"]
    if not tops and not legacies:
        return None, None, None
    for markers, name in ((tops, "top"), (legacies, "legacy")):
        if not markers:
            other = (tops or legacies)[0]
            errors.append(ItemError(other.number, "MARKER", f"missing {name} marker"))
        for duplicate in markers[1:]:
            errors.append(ItemError(duplicate.number, "MARKER", f"duplicate {name} marker"))
    cutover = None
    for marker in legacies:
        match = LEGACY_MARKER_RE.fullmatch(marker.text)
        if match:
            if cutover is None:
                cutover = int(match[1])
        else:
            errors.append(ItemError(marker.number, "MARKER", "invalid legacy cutover marker"))
    top = tops[0].number if tops else None
    legacy = legacies[0].number if legacies else None
    if top is not None and legacy is not None and top >= legacy:
        errors.append(ItemError(legacy, "MARKER", "legacy marker must follow the top marker"))
    return cutover, top, legacy


def _json_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _bad_constant(value: str):
    raise ValueError(f"non-finite number {value}")


def _header(line: _Line, errors: list[ItemError]) -> dict | None:
    if len(line.content) != 1:
        errors.append(ItemError(line.number, "BAD_JSON", "item block must contain one JSON line"))
        return None
    raw = line.content[0]
    try:
        header = json.loads(raw, object_pairs_hook=_json_object, parse_constant=_bad_constant)
        normalized = canonical(header)
    except (ValueError, RecursionError) as error:
        errors.append(ItemError(line.number, "BAD_JSON", str(error)))
        return None
    if normalized != raw:
        errors.append(ItemError(line.number, "NONCANONICAL", "item JSON must use canonical formatting"))
    if not isinstance(header, dict):
        errors.append(ItemError(line.number, "SCHEMA", "item header must be an object"))
        return None
    return header


def parse(text: str) -> Parsed:
    lines = list(_scan(text))
    errors = []
    cutover, top, legacy = _markers(lines, errors)
    items = []
    legacy_lines = {}
    heading = None
    eligible = seen = pointer_seen = False
    first_line = None
    item_headings = set()

    for line in lines:
        if top is None or legacy is None or not top < line.number < legacy:
            if line.kind == "heading":
                match = HEADING.match(line.text)
                legacy_lines.setdefault(match[1] + match[2], line.number)
            elif line.kind in ("item", "unterminated_item"):
                errors.append(ItemError(line.number, "ITEM_BEFORE_CUTOVER", "item block outside the typed region"))
            continue
        if line.kind == "blank":
            continue
        if first_line is None:
            first_line = line.number
        if line.kind == "heading":
            heading, eligible, seen, pointer_seen = line, True, False, False
        elif line.kind == "pointer" and eligible and not pointer_seen:
            pointer_seen = True
        elif line.kind in ("item", "unterminated_item"):
            if heading is not None:
                item_headings.add(heading.number)
            if seen:
                errors.append(ItemError(line.number, "SECOND_ITEM_BLOCK", "second item block for one heading"))
            elif not eligible or line.kind == "unterminated_item":
                errors.append(ItemError(line.number, "MISPLACED_ITEM_BLOCK",
                                        "expected one complete item block directly after its heading or pointer"))
            else:
                match = HEADING.match(heading.text)
                number = int(match[1])
                if match[2]:
                    errors.append(ItemError(heading.number, "LETTER_SUFFIX", "typed item number has a letter suffix"))
                header = _header(line, errors)
                if header is not None:
                    items.append(Item(number, heading.number, heading.text, header))
            eligible, seen = False, True
        else:
            eligible = False

    if cutover is not None and top is not None and legacy is not None and top < legacy:
        if legacy_lines and cutover <= max(int(key.rstrip("abcdefghijklmnopqrstuvwxyz")) for key in legacy_lines):
            errors.append(ItemError(legacy, "MARKER", "cutover must exceed the maximum legacy heading"))
        if first_line is not None and first_line not in item_headings:
            errors.append(ItemError(first_line, "ORDER", "first typed item must directly follow the top marker"))
        for line in lines:
            if top < line.number < legacy and line.kind == "heading" and line.number not in item_headings:
                if int(HEADING.match(line.text)[1]) >= cutover:
                    errors.append(ItemError(line.number, "UNTYPED_ITEM", "heading has no item block"))

    previous = None
    seen_numbers = {}
    for item in items:
        earlier = seen_numbers.get(item.number, legacy_lines.get(str(item.number)))
        if earlier is not None:
            errors.append(ItemError(item.line, "DUPLICATE_NUMBER",
                                    f"item {item.number} appears on lines {earlier} and {item.line}"))
        if (previous is not None and previous.number < item.number) or (cutover is not None and item.number < cutover):
            errors.append(ItemError(item.line, "ORDER", "typed items must descend and be at or above the cutover"))
        seen_numbers.setdefault(item.number, item.line)
        previous = item
    return Parsed(cutover, top, tuple(items), frozenset(legacy_lines), tuple(errors))


def valid_epoch(value: object) -> bool:
    return type(value) is int and MIN_EPOCH <= value <= MAX_EPOCH


def _positive(value: object) -> bool:
    return type(value) is int and value > 0


def header_errors(header: dict, line: int, number: int) -> list[ItemError]:
    """Validate the header itself before consulting other items."""
    errors = []

    def fail(code: str, detail: str):
        errors.append(ItemError(line, code, detail))

    if header.keys() != HEADER_KEYS:
        fail("SCHEMA", f"item header requires exactly {', '.join(sorted(HEADER_KEYS))}")
        return errors
    if header["schema"] != SCHEMA or header["owner"] not in OWNERS or header["status"] not in INITIAL:
        fail("SCHEMA", "invalid schema, owner or initial status")
    if not _positive(header["number"]):
        fail("SCHEMA", "number must be a positive integer")
    elif header["number"] != number:
        fail("NUMBER_MISMATCH", f"heading {number} differs from header {header['number']}")
    issued, expiry = header["issued_epoch_s"], header["expires_epoch_s"]
    if not valid_epoch(issued):
        fail("BAD_TIME", "issued_epoch_s must be integer seconds within 2026-01-01..2030-01-01 UTC")
    if expiry is not None:
        if header["status"] == "CLOSED":
            fail("SCHEMA", "CLOSED items require a null expiry")
        if not valid_epoch(expiry):
            fail("BAD_TIME", "expires_epoch_s must be null or integer seconds within the epoch bounds")
        elif valid_epoch(issued) and expiry <= issued:
            fail("EXPIRY_ORDER", "expires_epoch_s must exceed issued_epoch_s")

    refs = header["supersedes"]
    if (not isinstance(refs, list) or
            any(not isinstance(ref, str) or not REFERENCE.fullmatch(ref) for ref in refs)
            or len(set(refs)) != len(refs)):
        fail("SCHEMA", "supersedes must contain unique item number strings")
    changes = header["sets"]
    if not isinstance(changes, list):
        fail("SCHEMA", "sets must be an array")
        return errors
    for index, change in enumerate(changes):
        if (not isinstance(change, dict) or change.keys() != SET_KEYS
                or not _positive(change["item"]) or change["status"] not in SETTABLE):
            fail("SCHEMA", f"sets[{index}] requires a positive item number, settable status and at_epoch_s")
        elif not valid_epoch(change["at_epoch_s"]):
            fail("BAD_TIME", f"sets[{index}].at_epoch_s must be integer seconds within the epoch bounds")
    return errors


def _replay(parsed: Parsed, items: list[Item], errors: list[ItemError]):
    targets = {str(item.number): item for item in items}
    known_headings = {str(item.number) for item in parsed.items}
    states, changed_at, superseded_by = {}, {}, {}
    for item in sorted(items, key=lambda item: item.number):
        number, header = item.number, item.header
        issued = header["issued_epoch_s"]
        states[number], changed_at[number] = header["status"], issued
        transitions = [(ref, "SUPERSEDED", issued) for ref in header["supersedes"]]
        transitions.extend((str(change["item"]), change["status"], change["at_epoch_s"])
                           for change in header["sets"])
        for ref, status, at in transitions:
            target = targets.get(ref)
            if ref not in known_headings and ref not in parsed.legacy_numbers:
                code, detail = "DANGLING_REF", "no matching heading"
            elif int(ref.rstrip("abcdefghijklmnopqrstuvwxyz")) >= number:
                code, detail = "FORWARD_REF", f"target must precede item {number}"
            elif target is None:
                if ref not in parsed.legacy_numbers or status == "SUPERSEDED":
                    continue
                code, detail = "LEGACY_TARGET", "sets can only change typed items"
            else:
                current = states[target.number]
                expiry = target.header["expires_epoch_s"]
                if status not in LEGAL[current]:
                    code, detail = "ILLEGAL_TRANSITION", f"{current} → {status}"
                elif not changed_at[target.number] <= at <= issued:
                    code, detail = "TIME_ORDER", "change time precedes issuance or the last change, or exceeds setter issuance"
                elif status == "ARMED" and expiry is not None and at >= expiry:
                    code, detail = "ARM_AFTER_EXPIRY", "arming time meets or exceeds expiry"
                elif status == "EXPIRED" and (expiry is None or at < expiry):
                    code, detail = "EARLY_EXPIRY", "expiry is absent or has not been reached"
                else:
                    states[target.number], changed_at[target.number] = status, at
                    if status == "SUPERSEDED":
                        superseded_by[target.number] = number
                    continue
            errors.append(ItemError(item.line, code, f"item {ref}: {detail}"))
    return states, superseded_by


def validate(parsed: Parsed) -> list[ItemError]:
    errors = list(parsed.errors)
    valid = []
    for item in parsed.items:
        item_errors = header_errors(item.header, item.line, item.number)
        errors.extend(item_errors)
        if not item_errors:
            valid.append(item)
    _replay(parsed, valid, errors)
    return sorted(errors, key=lambda error: error.line)


def replay(parsed: Parsed) -> dict[int, str]:
    """Replay a validated document in ascending item number."""
    return _replay(parsed, list(parsed.items), [])[0]


def _derive(parsed: Parsed, states: dict[int, str], as_of_epoch_s: int) -> dict[int, str]:
    result = states.copy()
    for item in parsed.items:
        expiry = item.header["expires_epoch_s"]
        if result[item.number] in ("DRAFT", "ISSUED") and expiry is not None and as_of_epoch_s >= expiry:
            result[item.number] = "EXPIRED"
    return result


def derive(parsed: Parsed, as_of_epoch_s: int) -> dict[int, str]:
    return _derive(parsed, replay(parsed), as_of_epoch_s)


def open_items(parsed: Parsed) -> list[dict]:
    states = replay(parsed)
    return [{"item": item.number, "status": states[item.number], "owner": item.header["owner"],
             "expires_epoch_s": item.header["expires_epoch_s"]}
            for item in parsed.items if states[item.number] in OPEN]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "status"):
        sub = commands.add_parser(command)
        sub.add_argument("--run-state", type=Path, default=ROOT / "RUN_STATE.md")
    clock = sub.add_mutually_exclusive_group()
    clock.add_argument("--as-of")
    clock.add_argument("--as-of-epoch", type=int)
    args = parser.parse_args(argv)
    try:
        parsed = parse(args.run_state.read_text(encoding="utf-8"))
        errors = validate(parsed)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 2
        if args.command == "status":
            as_of = args.as_of_epoch
            if args.as_of is not None:
                as_of = _epoch(args.as_of, "--as-of", 1)
            if as_of is None:
                as_of = int(time.time())
            states, superseded_by = _replay(parsed, list(parsed.items), [])
            shown = _derive(parsed, states, as_of)
            for item in parsed.items:
                expiry = item.header["expires_epoch_s"]
                suffix = f" superseded_by={superseded_by[item.number]}" if item.number in superseded_by else ""
                print(f"{item.number} {shown[item.number]} owner={item.header['owner']} "
                      f"expires={expiry if expiry is not None else 'none'}{suffix}")
    except (OSError, ValueError) as error:
        print(f"run_state_items: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
