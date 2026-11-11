#!/usr/bin/env python3
"""Generate the shadow CURRENT.json declaration from RUN_STATE pointer blocks.

No Git, clock, custody, process or network observations. Only exact, unindented
pointer fences outside other fenced examples are declarations.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "joulewise.current_pointer.v1"
OBSERVABLES = frozenset({
    "result_json_exists", "results_branch_exists", "watchdog_status_state",
    "pr_merged", "ruling_recorded", "none",
})
KEYS = frozenset({"owner", "armed", "host", "t0", "latest_end", "wait", "deadline",
                  "on_early_or_refused", "next_observable"})
ARM_KEYS = frozenset({"armed", "host", "t0", "latest_end"})
MIN_EPOCH = 1767225600  # 2026-01-01T00:00:00+00:00
MAX_EPOCH = 1893456000  # 2030-01-01T00:00:00+00:00
HEADING = re.compile(r"^([1-9][0-9]*)([a-z]?)\.[ \t]+\*\*\S")
DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
ISO_TIME = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)


class PointerError(ValueError):
    """Invalid declaration, with a named reason and a RUN_STATE line number."""


def _fail(line: int, code: str, detail: str) -> None:
    raise PointerError(f"RUN_STATE line {line}: {code}: {detail}")


def _epoch(value: str, key: str, line: int) -> int | float:
    if ISO_TIME.fullmatch(value) is None:
        _fail(line, "INVALID_TIME", f"{key} must be ISO 8601 with a UTC offset")
    try:
        epoch = datetime.fromisoformat(value).timestamp()
    except ValueError:
        _fail(line, "INVALID_TIME", f"{key} has an invalid date, time or offset")
    if not MIN_EPOCH <= epoch <= MAX_EPOCH:
        _fail(line, "IMPLAUSIBLE_TIME", f"{key} must be within 2026-01-01..2030-01-01 UTC")
    return int(epoch) if epoch.is_integer() else epoch


def _pointer(values: dict[str, str], lines: dict[str, int], start: int,
             item: str, heading: str) -> dict:
    for key in ("owner", "wait", "next_observable"):
        if key not in values:
            _fail(start, "MISSING_KEY", f"required key {key}")
    observable = values["wait"]
    if observable not in OBSERVABLES:
        _fail(lines["wait"], "INVALID_WAIT", f"{observable!r}; expected "
              + ", ".join(sorted(OBSERVABLES)) + "; chain_exited cannot represent a pre-chain refusal")
    present = ARM_KEYS & values.keys()
    if present and present != ARM_KEYS:
        _fail(start, "PARTIAL_ARM", "armed, host, t0 and latest_end must appear together")
    for key in ("deadline", "on_early_or_refused"):
        if observable != "none" and key not in values:
            _fail(start, "MISSING_KEY", f"{key} required when wait is not none")
    epochs = {key: _epoch(values[key], key, lines[key])
              for key in ("t0", "latest_end", "deadline") if key in values}
    armed = None
    if present:
        if epochs["t0"] >= epochs["latest_end"]:
            _fail(lines["latest_end"], "ARM_ORDER", "t0 must be strictly earlier than latest_end")
        if "deadline" not in epochs:
            _fail(start, "MISSING_KEY", "deadline required when armed, including wait none")
        if epochs["deadline"] < epochs["latest_end"]:
            _fail(lines["deadline"], "DEADLINE_ORDER", "deadline must be at least latest_end")
        armed = {"plan_id": values["armed"], "host": values["host"],
                 "t0_epoch_s": epochs["t0"], "latest_end_epoch_s": epochs["latest_end"]}
    date = DATE.search(heading)
    return {"schema": SCHEMA, "source_item": item,
            "source_item_heading_date": date[0] if date else None,
            "owner": values["owner"], "armed": armed,
            "wait": {"observable": observable, "deadline_epoch_s": epochs.get("deadline"),
                     "on_early_or_refused": values.get("on_early_or_refused")},
            "next_observable": values["next_observable"]}


def _entries(body: list[tuple[int, str]]) -> tuple[dict[str, str], dict[str, int]]:
    values, lines = {}, {}
    for number, line in body:
        key, colon, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not colon:
            _fail(number, "INVALID_ENTRY", "expected key: value")
        if key not in KEYS:
            _fail(number, "UNKNOWN_KEY", f"unknown key {key!r}")
        if key in values:
            _fail(number, "DUPLICATE_KEY", f"duplicate key {key!r}")
        if not value:
            _fail(number, "EMPTY_VALUE", f"empty value for {key}")
        if not value.isprintable():
            _fail(number, "INVALID_VALUE", f"{key} must be single-line printable text")
        values[key], lines[key] = value, number
    return values, lines


def render(run_state_text: str) -> bytes:
    """Validate every block, then render the highest numbered block's declaration.

    Other fenced code suppresses recognition of headings and pointer fences.
    Quoted and indented pointer fences are examples, never declarations.
    """
    candidates = []
    item = heading = None
    eligible = seen = False
    other_fence = None
    body = None
    start = 0
    for number, line in enumerate(run_state_text.splitlines(), 1):
        if body is not None:
            if line == "```":
                values, lines = _entries(body)
                candidates.append(((int(item[:-1]), item[-1]) if item[-1].isalpha()
                                   else (int(item), ""),
                                   _pointer(values, lines, start, item, heading)))
                body = None
            elif line == "```pointer":
                _fail(number, "SECOND_POINTER", "second pointer block in one item")
            else:
                body.append((number, line))
            continue
        if other_fence is not None:
            if re.fullmatch(r"[ \t]*" + re.escape(other_fence[0])
                            + "{" + str(len(other_fence)) + r",}[ \t]*", line):
                other_fence = None
            continue
        if match := HEADING.match(line):
            item, heading = match[1] + match[2], line
            eligible, seen = True, False
        elif line == "```pointer":
            if seen:
                _fail(number, "SECOND_POINTER", "second pointer block in one item")
            if item is None or not eligible:
                _fail(number, "MISPLACED_POINTER", "pointer fence must directly follow a numbered item heading (blank lines allowed)")
            start, body = number, []
            eligible, seen = False, True
        elif match := FENCE.fullmatch(line):
            other_fence = match[1]
            eligible = False
        elif line.strip():
            eligible = False
    if body is not None:
        _fail(start, "UNTERMINATED_POINTER", "pointer fence has no exact closing fence")
    pointer = (max(candidates, key=lambda candidate: candidate[0])[1] if candidates else
               {"schema": SCHEMA, "source_item": None, "source_item_heading_date": None,
                "owner": None, "armed": None, "wait": None, "next_observable": None})
    return (json.dumps(pointer, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def generate(run_state_path: str | Path, out_path: str | Path) -> None:
    """Render first, then atomically replace the output in its own directory."""
    data = render(Path(run_state_path).read_text(encoding="utf-8"))
    out_path = Path(out_path)
    fd, temporary = tempfile.mkstemp(dir=out_path.parent, prefix=".gen_current.")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        os.replace(temporary, out_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _keys(value: object, expected: set[str], name: str) -> None:
    if not isinstance(value, dict) or value.keys() != expected:
        raise ValueError(f"{name} must be an object with exactly {sorted(expected)}")


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip() or not value.isprintable():
        raise ValueError(f"{name} must be nonempty single-line text")


def _number(value: object, name: str) -> None:
    if type(value) not in (int, float) or not MIN_EPOCH <= value <= MAX_EPOCH:
        raise ValueError(f"{name} must be epoch seconds within 2026-01-01..2030-01-01 UTC")


def validate(pointer: object) -> None:
    """Validate the generated schema; malformed output is invalid, not drift."""
    _keys(pointer, {"schema", "source_item", "source_item_heading_date", "owner",
                    "armed", "wait", "next_observable"}, "pointer")
    if pointer["schema"] != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    if pointer["source_item"] is None:
        if any(pointer[key] is not None for key in pointer if key != "schema"):
            raise ValueError("no-pointer document must have all declaration fields null")
        return
    if not isinstance(pointer["source_item"], str) or re.fullmatch(r"[1-9][0-9]*[a-z]?", pointer["source_item"]) is None:
        raise ValueError("source_item must be a numbered item string")
    date = pointer["source_item_heading_date"]
    if date is not None and (not isinstance(date, str) or DATE.fullmatch(date) is None):
        raise ValueError("source_item_heading_date must be YYYY-MM-DD or null")
    for key in ("owner", "next_observable"):
        _text(pointer[key], key)
    armed, wait = pointer["armed"], pointer["wait"]
    _keys(wait, {"observable", "deadline_epoch_s", "on_early_or_refused"}, "wait")
    if not isinstance(wait["observable"], str) or wait["observable"] not in OBSERVABLES:
        raise ValueError("wait.observable is not in the closed vocabulary")
    if wait["deadline_epoch_s"] is not None:
        _number(wait["deadline_epoch_s"], "wait.deadline_epoch_s")
    if wait["on_early_or_refused"] is not None:
        _text(wait["on_early_or_refused"], "wait.on_early_or_refused")
    if wait["observable"] != "none" and any(wait[key] is None for key in ("deadline_epoch_s", "on_early_or_refused")):
        raise ValueError("wait requires deadline and refusal branch unless none")
    if armed is not None:
        _keys(armed, {"plan_id", "host", "t0_epoch_s", "latest_end_epoch_s"}, "armed")
        for key in ("plan_id", "host"):
            _text(armed[key], "armed." + key)
        for key in ("t0_epoch_s", "latest_end_epoch_s"):
            _number(armed[key], "armed." + key)
        if armed["t0_epoch_s"] >= armed["latest_end_epoch_s"]:
            raise ValueError("armed requires t0 < latest_end")
        if wait["deadline_epoch_s"] is None or wait["deadline_epoch_s"] < armed["latest_end_epoch_s"]:
            raise ValueError("armed requires deadline >= latest_end")


def check(run_state_path: str | Path, out_path: str | Path) -> int:
    """Return 0 for byte agreement, 1 for drift, 2 for invalid/unreadable input."""
    try:
        expected = render(Path(run_state_path).read_text(encoding="utf-8"))
        actual = Path(out_path).read_bytes()
        # Parsing distinguishes an invalid file from valid JSON with byte drift.
        validate(json.loads(actual.decode("utf-8"), object_pairs_hook=_object))
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        print(f"gen_current: {error}", file=sys.stderr)
        return 2
    if actual != expected:
        print(f"DRIFT: {out_path} differs; run python3 scripts/gen_state.py", file=sys.stderr)
        return 1
    return 0


def check_default() -> int:
    return check(ROOT / "RUN_STATE.md", ROOT / "docs/process/CURRENT.json")


def generate_default() -> int:
    return main([])


def show(pointer: dict) -> str:
    armed, wait = pointer["armed"], pointer["wait"]
    arm_text = (f"{armed['plan_id']}@{armed['host']} t0={armed['t0_epoch_s']} end={armed['latest_end_epoch_s']}"
                if armed else "none")
    wait_text = (f"{wait['observable']} deadline={wait['deadline_epoch_s']} on_early_or_refused={wait['on_early_or_refused']}"
                 if wait else "none")
    return (f"item={pointer['source_item']} date={pointer['source_item_heading_date']} "
            f"owner={pointer['owner']} armed={arm_text} wait={wait_text} next={pointer['next_observable']}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--show", action="store_true")
    parser.add_argument("--run-state", type=Path, default=ROOT / "RUN_STATE.md")
    parser.add_argument("--out", type=Path, default=ROOT / "docs/process/CURRENT.json")
    args = parser.parse_args(argv)
    if args.check or args.show:
        code = check(args.run_state, args.out)
        if code or args.check:
            return code
        print(show(json.loads(args.out.read_text(encoding="utf-8"))))
        return 0
    try:
        generate(args.run_state, args.out)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"gen_current: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
