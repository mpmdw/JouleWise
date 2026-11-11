#!/usr/bin/env python3
"""Validate the shadow head pointer; bump changes only its number and timestamp.

No custody, process, network, or Git observations are made. RUN_STATE is used
only for numbered headings. Observable names are declarations, not probes.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shlex
import sys


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "joulewise.current_pointer.v1"
OBSERVABLES = frozenset({
    "result_json_exists", "results_branch_exists", "watchdog_status_state",
    "pr_merged", "none",
})
MIN_EPOCH = 1767225600  # 2026-01-01T00:00:00+00:00 (exclusive)
MAX_EPOCH = 1893456000  # 2030-01-01T00:00:00+00:00 (exclusive)
HEADING = re.compile(r"^([1-9][0-9]*)([a-z]?)\.[ \t]+\*\*\S")
ISO_TIME = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)


def top_item(run_state: Path) -> tuple[int, str]:
    """Select numerically, including letter suffixes; never interpret prose."""
    with run_state.open(encoding="utf-8") as stream:
        items = ((int(m[1]), m[2]) for line in stream if (m := HEADING.match(line)))
        try:
            return max(items)
        except ValueError:
            raise ValueError("RUN_STATE has no numbered item headings") from None


def _object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ValueError(f"non-JSON constant: {value}")


def _keys(value: object, required: set[str], name: str,
          optional: frozenset[str] = frozenset()) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing or unknown:
        raise ValueError(f"{name}: missing keys {sorted(missing)}; unknown keys {sorted(unknown)}")


def _text(value: object, name: str) -> None:
    if (not isinstance(value, str) or not value.strip()
            or any(not char.isprintable() for char in value)):
        raise ValueError(f"{name} must be nonempty single-line text")


def _epoch(value: object, name: str) -> None:
    if type(value) is not int or not MIN_EPOCH < value < MAX_EPOCH:
        raise ValueError(f"{name} must be integer epoch seconds after 2026-01-01 and before 2030")


def validate(pointer: object) -> None:
    _keys(pointer, {"schema", "run_state_top_item", "updated", "owner", "armed",
                    "wait", "next_observable"}, "pointer",
          frozenset({"run_state_top_item_suffix"}))
    if pointer["schema"] != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    number = pointer["run_state_top_item"]
    if type(number) is not int or number < 1:
        raise ValueError("run_state_top_item must be a positive integer")
    if "run_state_top_item_suffix" in pointer:
        suffix = pointer["run_state_top_item_suffix"]
        if not isinstance(suffix, str) or re.fullmatch("[a-z]", suffix) is None:
            raise ValueError("run_state_top_item_suffix must be one lowercase letter")
    updated = pointer["updated"]
    if not isinstance(updated, str) or ISO_TIME.fullmatch(updated) is None:
        raise ValueError("updated must be an ISO timestamp with an offset")
    # fromisoformat also rejects invalid dates, times and UTC offsets.
    datetime.fromisoformat(updated)
    _text(pointer["owner"], "owner")
    _text(pointer["next_observable"], "next_observable")
    if len(pointer["next_observable"]) > 240:
        raise ValueError("next_observable must be at most 240 characters")
    armed, wait = pointer["armed"], pointer["wait"]
    if armed is not None:
        _keys(armed, {"plan_id", "t0_epoch_s", "latest_end_epoch_s", "host"}, "armed")
        for name in ("plan_id", "host"):
            _text(armed[name], "armed." + name)
        for name in ("t0_epoch_s", "latest_end_epoch_s"):
            _epoch(armed[name], "armed." + name)
        if armed["latest_end_epoch_s"] < armed["t0_epoch_s"]:
            raise ValueError("armed.latest_end_epoch_s must be >= t0_epoch_s")
        if wait is None:
            raise ValueError("armed requires wait with a deadline")
    if wait is not None:
        _keys(wait, {"observable", "deadline_epoch_s", "on_early_or_refused"}, "wait")
        observable = wait["observable"]
        if not isinstance(observable, str) or observable not in OBSERVABLES:
            raise ValueError("wait.observable must be one of " + ", ".join(sorted(OBSERVABLES))
                             + "; use result_json_exists instead of chain_exited")
        _epoch(wait["deadline_epoch_s"], "wait.deadline_epoch_s")
        _text(wait["on_early_or_refused"], "wait.on_early_or_refused")
        if armed is not None:
            if observable == "none":
                raise ValueError("armed requires a checkable wait, not none")
            if wait["deadline_epoch_s"] < armed["latest_end_epoch_s"]:
                raise ValueError("wait.deadline_epoch_s must be >= armed.latest_end_epoch_s")


def load(pointer_path: Path) -> tuple[str, dict]:
    source = pointer_path.read_bytes().decode("utf-8")
    pointer = json.loads(source, object_pairs_hook=_object, parse_constant=_constant)
    validate(pointer)
    return source, pointer


def check(pointer_path: Path, run_state: Path) -> dict:
    _, pointer = load(pointer_path)
    number, suffix = top_item(run_state)
    if pointer["run_state_top_item"] != number:
        raise ValueError(f"run_state_top_item is {pointer['run_state_top_item']}; RUN_STATE highest item is {number}{suffix}")
    if ("run_state_top_item_suffix" in pointer
            and pointer["run_state_top_item_suffix"] != suffix):
        raise ValueError(f"run_state_top_item_suffix differs from RUN_STATE item {number}{suffix}; correct or remove the optional suffix manually")
    return pointer


def _value_spans(source: str) -> dict[str, tuple[int, int]]:
    """Find top-level JSON value tokens without changing formatting or escapes."""
    decoder = json.JSONDecoder()

    def skip(index: int) -> int:
        while source[index] in " \t\r\n":
            index += 1
        return index

    index = skip(skip(0) + 1)  # validated nonempty object
    spans = {}
    while True:
        key, end = decoder.raw_decode(source, index)
        start = skip(skip(end) + 1)  # colon
        _, end = decoder.raw_decode(source, start)
        spans[key] = (start, end)
        index = skip(end)
        if source[index] == "}":
            return spans
        index = skip(index + 1)  # comma


def bump(pointer_path: Path, run_state: Path, *, updated: str | None = None) -> None:
    source, pointer = load(pointer_path)
    number, suffix = top_item(run_state)
    if ("run_state_top_item_suffix" in pointer
            and pointer["run_state_top_item_suffix"] != suffix):
        raise ValueError("bump preserves the optional suffix; correct or remove run_state_top_item_suffix manually")
    updated = updated if updated is not None else datetime.now(timezone.utc).isoformat(timespec="seconds")
    candidate = {**pointer, "run_state_top_item": number, "updated": updated}
    validate(candidate)
    spans = _value_spans(source)
    replacements = [(spans[key], json.dumps(candidate[key]))
                    for key in ("run_state_top_item", "updated")]
    for (start, end), value in sorted(replacements, reverse=True):
        source = source[:start] + value + source[end:]
    pointer_path.write_bytes(source.encode("utf-8"))


def show(pointer: dict) -> str:
    item = str(pointer["run_state_top_item"]) + pointer.get("run_state_top_item_suffix", "")
    armed, wait = pointer["armed"], pointer["wait"]
    arm_text = (f"{armed['plan_id']}@{armed['host']} t0={armed['t0_epoch_s']} end={armed['latest_end_epoch_s']}"
                if armed is not None else "none")
    wait_text = (f"{wait['observable']} deadline={wait['deadline_epoch_s']}"
                 if wait is not None else "none")
    return f"item={item} owner={pointer['owner']} armed={arm_text} wait={wait_text} next={pointer['next_observable']}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "bump", "show"):
        child = commands.add_parser(command)
        child.add_argument("--pointer", type=Path, default=ROOT / "docs/process/CURRENT.json")
        child.add_argument("--run-state", type=Path, default=ROOT / "RUN_STATE.md")
    args = parser.parse_args(argv)
    try:
        if args.command == "bump":
            bump(args.pointer, args.run_state)
        pointer = check(args.pointer, args.run_state)
        if args.command == "show":
            print(show(pointer))
        else:
            print(f"CURRENT {args.command}: item {pointer['run_state_top_item']}")
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        command = shlex.join([sys.executable, "-B", str(Path(__file__).resolve()), "bump",
                              "--pointer", str(args.pointer), "--run-state", str(args.run_state)])
        print(f"CURRENT check failed: {error}\nBump command: {command}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
