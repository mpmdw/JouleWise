#!/usr/bin/env python3
"""Validate the MBP schedule and recommend one action from structural facts.

Ledger decision observations have a decision key. Producers record actual host
events with an event key (LAUNCH, CLOSE, COPY_VERIFIED, REFUSAL, STOP, GATE, READY).
Only those events are used as launch and close history.

Only sequenced ledger events can open or close an attempt.
The independently committed head is read from <ledger>.head.json. Its digest
is SHA-256 over compact canonical JSON rows, each followed by one newline.
Decision observations go to a separate report ledger.
CONFIG binds the active queue commit and queue and register digests. READY
records carry the registered expected_ready_by value, including an explicit
null for no commitment. LAUNCH t0 matches the native receipt's exact start.

Probe sources that need no native command (for example meter readiness, the
High Power marker and queue commit) can be supplied via --host-facts. Probe
outputs null when a source is unavailable. Production close and host-fact
producers are separate from this scheduler.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, time as local_time, timedelta
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import time
from zoneinfo import ZoneInfo


PROCESS = Path(__file__).resolve().parents[1] / "docs/process"
DEFAULT_QUEUE = PROCESS / "mbp/QUEUE.json"
DEFAULT_RULES = PROCESS / "RULES.json"
SCHEMA = "joulewise.mbp_queue.v1"
ZONE = "America/Los_Angeles"
KINDS = ("v4_session", "counted", "product_filler", "diagnostic_filler", "maintenance")
FILLERS = {"product_filler", "diagnostic_filler"}
COUNTED_KINDS = {"counted", "v4_session"}
CLASSES = {"PHYSICS", "VALIDITY", "SAFETY"}
HOST_TESTS = ("host_power", "host_disk", "host_meter", "host_clean", "host_quiet",
              "owner_stop", "copy_debt")
ENTRY_TESTS = ("pin", "window", "dependency", "fits", "launcher_admits", "not_refused",
               "session_route", "batch_clear", "desk_gate", "contaminated_redos",
               "new_pin_smoke", "f0_retirement", "ready_outside_block", "hygiene")
DECISIONS = {"LAUNCH", "WAIT", "HALT", "CLOSE_OWED", "QUEUE_EMPTY"}
PLACEHOLDERS = re.compile(r"\{([a-zA-Z_][a-zA-Z_0-9]*)\}")
ARGV_FIELDS = {"deadline_epoch", "out", "magistrate_pid"}


def as_json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, allow_nan=False)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def bad_constant(value):
    raise ValueError(f"invalid JSON number {value}")


def parse_json(source):
    return json.loads(source, object_pairs_hook=unique_object, parse_constant=bad_constant)


def integer(value):
    return type(value) is int and value >= 0


def positive_integer(value):
    return integer(value) and value > 0


def number(value):
    return integer(value) or (type(value) is float and math.isfinite(value) and value >= 0)


def epoch(value):
    return number(value) and value < 253370764800


def string(value):
    return isinstance(value, str) and bool(value.strip()) and value.isprintable()


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value) is not None


def one_of(*values):
    return lambda value: isinstance(value, str) and value in values


def nullable(check):
    return lambda value: value is None or check(value)


def array(check):
    return lambda value: isinstance(value, list) and all(check(item) for item in value)


def hexadecimal(size):
    pattern = re.compile(fr"[0-9a-fA-F]{{{size}}}")
    return lambda value: isinstance(value, str) and pattern.fullmatch(value) is not None


def boolean(value):
    return type(value) is bool


def calendar_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d\d-\d\d", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def clock_time(value):
    return isinstance(value, str) and re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d", value) is not None


def argument_vector(value):
    return (
        isinstance(value, list) and bool(value) and string(value[0])
        and all(isinstance(arg, str) and "\0" not in arg
                and set(PLACEHOLDERS.findall(arg)) <= ARGV_FIELDS for arg in value)
    )


PIN = hexadecimal(40)
KIT = nullable(hexadecimal(64))
REVIEW = lambda value: calendar_date(value) or (
    isinstance(value, str) and value.startswith("end:") and string(value[4:])
)
RULE_NAME = lambda value: (
    string(value) and (value in HOST_TESTS + ENTRY_TESTS + ("filler_ladder",)
                       or value.startswith("pipeline:") and string(value[9:]))
)
IS_OBJECT = lambda value: isinstance(value, dict)


class Errors:
    def __init__(self):
        self.items = []

    def add(self, path, code, detail):
        self.items.append(f"{path}: {code}: {detail}")

    def read_json(self, path):
        try:
            return parse_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, RecursionError) as err:
            self.add(path, "READ_JSON", str(err))
            return None

    def fields(self, path, where, row, required, optional=None, codes=None):
        if not isinstance(row, dict):
            self.add(path, "BAD_VALUE", f"{where} must be an object")
            return False
        count = len(self.items)
        optional = optional or {}
        codes = codes or {}
        for key in sorted(row.keys() - required.keys() - optional.keys()):
            self.add(path, "UNKNOWN_KEY", f"{where}.{key}")
        for key in sorted(required.keys() - row.keys()):
            self.add(path, "MISSING_KEY", f"{where}.{key}")
        for key, check in (required | optional).items():
            if key in row and not check(row[key]):
                self.add(path, codes.get(key, "BAD_VALUE"), f"{where}.{key}")
        return count == len(self.items)

    def finish(self):
        if not self.items:
            return 0
        for error in self.items:
            print(error.replace("\n", "\\n").replace("\r", "\\r"), file=sys.stderr)
        return 2


RULE_FIELDS = {
    "id": identifier, "class": one_of(*CLASSES), "protects": string, "test": RULE_NAME,
    "scope": string, "source": string, "owner": one_of("lead", "research_lead"),
    "added": calendar_date, "review_by": REVIEW, "status": one_of("LIVE", "FLAG", "RETIRED"),
}
RULE_PARAMS = {
    "host_disk": ({"floor_gib": number}, {}),
    "host_quiet": ({"patterns": array(string), "recheck_s": integer}, {}),
    "owner_stop": ({}, {"maintenance_marker": string, "recheck_s": integer}),
    "copy_debt": ({"wait_s": integer}, {"page_age_s": integer}),
    "launcher_admits": ({}, {"output_root": nullable(string)}),
    "batch_clear": ({"offset_s": integer, "period_s": lambda value: integer(value) and value > 0,
                     "settle_s": integer}, {}),
    "f0_retirement": ({"gate": identifier}, {}),
    "filler_ladder": ({"stability_prefix": identifier, "instrument_prefix": identifier,
                       "high_power_prefix": identifier, "high_power_look_gate": identifier}, {}),
    "hygiene": ({"start_gate": identifier, "end_gate": identifier}, {}),
}
ENTRY_FIELDS = {
    "id": identifier, "kind": one_of(*KINDS), "launcher": string, "worktree": string,
    "argv": argument_vector, "pin": PIN, "kit_sha256": KIT, "expected_s": positive_integer,
    "worst_case_s": positive_integer, "requires": array(identifier), "params": IS_OBJECT,
    "repeat": boolean, "product": string,
}
ENTRY_OPTIONAL = {
    "block": identifier, "expected_ready_by": epoch, "plan_argv": argument_vector,
    "done": boolean, "close_gap_s": integer,
}
ENTRY_PARAMS = {
    "window": IS_OBJECT, "date_caps": array(IS_OBJECT), "not_on_dates_of": array(identifier),
    "batch_clear": boolean, "soak_end_s": integer, "group": identifier, "legs": positive_integer,
    "after": array(identifier), "gates": array(identifier),
    "groups": array(identifier), "qualification": boolean, "floating_battery": boolean,
    "dry_run_required": boolean, "campaign": identifier, "launch_window_local":
        lambda value: array(clock_time)(value) and len(value) == 2,
    "kill_margin_s": integer, "pilot": boolean, "hygiene_change": boolean,
}


def validate_rules(path, data, errors):
    rules = {}
    if not isinstance(data, list):
        if data is not None:
            errors.add(path, "BAD_VALUE", "rules must be an array")
        return rules
    for index, row in enumerate(data):
        where = f"rules[{index}]"
        if not errors.fields(path, where, row, RULE_FIELDS, {"params": IS_OBJECT},
                             {"class": "BAD_CLASS", "test": "BAD_TEST"}):
            continue
        if row["id"] in rules:
            errors.add(path, "DUPLICATE_ID", row["id"])
        rules[row["id"]] = row
        required, optional = RULE_PARAMS.get(row["test"], ({}, {}))
        params = row.get("params", {})
        if not row["test"].startswith("pipeline:"):
            errors.fields(path, f"{where}.params", params, required, optional)
        if row["test"] == "host_quiet":
            patterns = params.get("patterns", [])
            if array(string)(patterns):
                for pattern in patterns:
                    try:
                        re.compile(pattern)
                    except re.error as err:
                        errors.add(path, "BAD_PATTERN", f"{where}.params.patterns: {err}")
    return rules


def pair(row):
    return row["pin"].lower(), (row["kit_sha256"] or "").lower()


def validate_queue(path, data, rules, errors, check_references):
    if data is None:
        return
    queue_fields = {"schema": one_of(SCHEMA), "timezone": one_of(ZONE),
                    "admitted": array(IS_OBJECT), "entries": array(IS_OBJECT)}
    errors.fields(path, "queue", data, queue_fields)
    if not isinstance(data, dict):
        return
    admitted = set()
    admission = data.get("admitted")
    for index, row in enumerate(admission if isinstance(admission, list) else []):
        if errors.fields(path, f"admitted[{index}]", row, {"pin": PIN, "kit_sha256": KIT}):
            key = pair(row)
            if key in admitted:
                errors.add(path, "DUPLICATE_ADMISSION", f"admitted[{index}]")
            admitted.add(key)
    ids = set()
    standing = False
    entries = data.get("entries")
    entries = entries if isinstance(entries, list) else []
    for index, entry in enumerate(entries):
        where = f"entries[{index}]"
        errors.fields(path, where, entry, ENTRY_FIELDS, ENTRY_OPTIONAL)
        if not isinstance(entry, dict):
            continue
        entry_id = entry.get("id")
        if identifier(entry_id):
            if entry_id in ids:
                errors.add(path, "DUPLICATE_ID", entry_id)
            ids.add(entry_id)
        if PIN(entry.get("pin")) and "kit_sha256" in entry and KIT(entry["kit_sha256"]):
            if pair(entry) not in admitted:
                errors.add(path, "PIN_NOT_ADMITTED", f"{entry_id}: pin and kit hash")
        worst, expected = entry.get("worst_case_s"), entry.get("expected_s")
        if integer(worst) and integer(expected) and worst < expected:
            errors.add(path, "BAD_DURATION", f"{entry_id}: worst_case_s < expected_s")
        plan = entry.get("plan_argv")
        if argument_vector(plan):
            if plan == entry.get("argv") or any(PLACEHOLDERS.search(arg) for arg in plan):
                errors.add(path, "BAD_PLAN_ARGV",
                           f"{entry_id}: a dry run needs its own concrete command")
        refs = entry.get("requires")
        params = entry.get("params")
        if check_references and array(identifier)(refs):
            for ref in refs:
                if ref not in rules or rules[ref]["status"] == "RETIRED":
                    errors.add(path, "BAD_RULE_REFERENCE", f"{entry_id}: {ref}")
            restricted = {rules[ref]["test"] for ref in refs if ref in rules}
            if (entry.get("repeat") is True and entry.get("done") is not True
                    and one_of(*FILLERS)(entry.get("kind"))
                    and not entry.get("block") and not (isinstance(params, dict) and
                         (params.get("after") or params.get("gates")))
                    and not restricted.intersection({"window", "dependency", "session_route"})):
                standing = True
        if isinstance(params, dict):
            validate_entry_params(path, where, params, errors)
            if entry.get("kind") == "counted":
                if params.get("date_caps") and not (params.get("groups") or identifier(params.get("group"))):
                    errors.add(path, "MISSING_COUNT_METADATA",
                               f"{where}.params.group is required for a counted date cap")
                if (params.get("date_caps") or params.get("groups") or params.get("group")) and "legs" not in params:
                    errors.add(path, "MISSING_COUNT_METADATA",
                               f"{where}.params.legs is required for grouped counted work")
    if check_references and not standing:
        errors.add(path, "NO_STANDING_FILLER", "no unfinished repeating filler free of window, dependency and session_route")


def validate_entry_params(path, where, params, errors):
    where = f"{where}.params"

    errors.fields(path, where, params, {}, ENTRY_PARAMS)
    if params.get("groups") and array(identifier)(params["groups"]):
        if len(set(params["groups"])) != len(params["groups"]):
            errors.add(path, "BAD_GROUPS", f"{where}.groups must be unique")
        if params.get("group") and params["group"] not in params["groups"]:
            errors.add(path, "BAD_GROUPS", f"{where}.group conflicts with groups")
    if "window" in params and errors.fields(path, f"{where}.window", params["window"], {}, {
        "earliest_epoch": nullable(epoch), "latest_epoch": nullable(epoch),
    }):
        earliest = params["window"].get("earliest_epoch")
        latest = params["window"].get("latest_epoch")
        if earliest is not None and latest is not None and earliest > latest:
            errors.add(path, "BAD_WINDOW", f"{where}.window earliest_epoch > latest_epoch")
    caps = params.get("date_caps")
    if isinstance(caps, list):
        for index, cap in enumerate(caps):
            errors.fields(path, f"{where}.date_caps[{index}]", cap, {"group": identifier, "max": integer})


MAINTENANCE_PATH = "/Users/Shared/JouleWise/MAINTENANCE"
RESTORE_READBACKS = ("power_mode", "network_time_off", "frequency_word_zero", "no_monitor",
                     "no_high_power_marker", "feeds_stopped", "process_group_gone")
CONTAMINATED = "CONTAMINATED_REDOS"
KIT_STOPS = {"LEG_OVERTIME", "NON_CLEAN_CLOSE", "LAUNCHER_REFUSED", "DESK_FAILURE", "CONSUMER_GATE"}
COPY_EVENTS = {"COPY_STARTED", "COPY_VERIFIED", "UPLOAD_STOPPED"}
MIRRORS = {
    "launches": {"LAUNCH"}, "closes": {"CLOSE"}, "receipts": {"RECEIPT"},
    "restore_proofs": {"RESTORE"}, "stops": {"STOP"}, "gates": {"GATE"},
    "ready": {"READY"}, "refusals": {"REFUSAL"}, "copy_events": COPY_EVENTS,
    "config_events": {"CONFIG"},
}
HEAD_FIELDS = {"ledger_id": identifier, "last_seq": positive_integer, "digest": hexadecimal(64)}
REVISION_FIELDS = {"queue_commit": identifier, "queue_digest": hexadecimal(64),
                   "rules_digest": hexadecimal(64)}
BOUND = {"open_seq": positive_integer, "span_id": identifier,
         "entry_id": identifier, "kit_sha256": KIT}
KINDS_CHECK = one_of(*KINDS)
REGISTRATION = {"kind": KINDS_CHECK, "groups": array(identifier),
                "legs": integer, "block": nullable(identifier)}
EVENT_FIELDS = {
    "LAUNCH": {**REGISTRATION, "span_id": identifier, "entry_id": identifier, "pin": PIN,
               "kit_sha256": KIT, "t0_epoch": epoch, "boot_id": identifier,
               "queue_commit": identifier, "registration": IS_OBJECT, "campaign": identifier},
    "CLOSE": {**BOUND, "ended_epoch": epoch, "clean": boolean, "load_redos": integer,
              "load_flag": boolean},
    "RECEIPT": {**BOUND, "receipt_id": identifier, "receipt": IS_OBJECT},
    "RESTORE": {**BOUND, "readbacks": IS_OBJECT},
    "STOP": {**BOUND, "code": one_of(CONTAMINATED, *KIT_STOPS), "epoch": epoch},
    "GATE": {"id": identifier, "passed": boolean},
    "READY": {"entry_id": identifier, "effective": boolean, "route_clear": boolean,
              "expected_ready_by": nullable(epoch)},
    "CONFIG": REVISION_FIELDS,
    "REFUSAL": {"entry_id": identifier, "kit_sha256": KIT, "block": nullable(identifier),
                "queue_commit": identifier, "epoch": epoch, "reason": string},
    **{event: BOUND for event in COPY_EVENTS},
}
EVENT_OPTIONAL = {"LAUNCH": {"soak_end_epoch": epoch, "predicted_batch_epoch": epoch}}
HOST_FIELDS = {
    "now_epoch": epoch, "clock_verified": boolean, "boot_epoch": epoch,
    "power": IS_OBJECT, "disk_free_gib": number, "fence_clear": boolean,
    "runner_group_clear": boolean, "high_power_marker": boolean, "foreign_processes": array(IS_OBJECT),
    "process_census_verified": boolean, "upload_stopped": boolean, "owner_stop": boolean,
    "owner_veto": boolean, "maintenance_active": boolean, "maintenance_marker": string,
    **REVISION_FIELDS,
    "ledger_head": IS_OBJECT, "plans": IS_OBJECT,
}
HOST_OPTIONAL = {
    "labels_loaded": array(string), "meter_ready": boolean, "collector_ready": boolean,
    "receipt_attestations": array(IS_OBJECT), "errors": IS_OBJECT, "uncopied": array(IS_OBJECT),
    **{key: array(IS_OBJECT) for key in MIRRORS},
}


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def ledger_digest(rows):
    return hashlib.sha256("".join(canonical(row) + "\n" for row in rows).encode()).hexdigest()


class Halt(Exception):
    def __init__(self, rule, detail):
        self.decision = {"decision": "HALT", "rule": rule, "detail": detail}
        super().__init__(detail)


def require(condition, rule, detail):
    if not condition:
        raise Halt(rule, detail)


def fields(value, required, rule, name, optional=None):
    problems = Errors()
    problems.fields(name, name, value, required, optional)
    if problems.items:
        raise Halt(rule, problems.items[0].split(": ", 2)[-1])


def same(left, right):
    return canonical(left) == canonical(right)


def head_valid(head):
    fields(head, HEAD_FIELDS, "LEDGER_HEAD_INVALID", "ledger head")


def read_head(path):
    try:
        head = parse_json(path.read_text(encoding="utf-8"))
        head_valid(head)
        return head
    except (OSError, ValueError, RecursionError, Halt) as err:
        raise Halt("LEDGER_HEAD_INVALID", f"committed head is unreadable or invalid: {path.name}") from err


def default_head_path(ledger):
    return ledger.with_name(ledger.name + ".head.json")


def read_events(path):
    if path is None:
        raise Halt("LEDGER_MISSING", "no committed event ledger was supplied")
    try:
        with path.open(encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH)
            rows = []
            for index, line in enumerate(stream, 1):
                require(line.endswith("\n"), "LEDGER_INVALID", f"row {index} is incomplete")
                try:
                    rows.append(parse_json(line))
                except (ValueError, RecursionError) as err:
                    raise Halt("LEDGER_INVALID", f"row {index} has invalid JSON") from err
            return rows
    except (OSError, UnicodeError) as err:
        raise Halt("LEDGER_MISSING", "event ledger is unreadable") from err


@dataclass
class Attempt:
    launch: dict
    close: dict | None = None
    receipt: dict | None = None
    restore: dict | None = None
    copy: dict[str, int] = field(default_factory=dict)

    @property
    def span(self):
        return self.launch["span_id"]

    def prove_close(self):
        require(self.receipt is not None, "RECEIPT_MISSING", f"{self.span} has no own receipt")
        require(self.restore is not None, "RESTORE_UNPROVEN", f"{self.span} has no restore readbacks")
        for check in RESTORE_READBACKS:
            require(self.restore[check] is True, "RESTORE_UNPROVEN", f"{self.span} failed {check}")
        start, end = self.launch["t0_epoch"], self.close["ended_epoch"]
        received_start = self.receipt["started"]["epoch_s"]
        received_end = self.receipt["ended"]["epoch_s"]
        require(start == received_start and received_start <= received_end <= end,
                "CLOCK_ROLLBACK", f"{self.span} receipt and close timestamps are inconsistent")
        require(not self.close["clean"] or self.receipt["rc"] == 0,
                "RECEIPT_CONFLICT", f"{self.span} clean close disagrees with its receipt")

    def clean_load(self):
        return (self.close is not None and self.close["clean"] is True
                and self.close["load_redos"] == 0 and self.close["load_flag"] is False)

    def copy_verified(self):
        return self.copy.get("COPY_VERIFIED", 0) > self.copy.get("COPY_STARTED", 0)

    def upload_active(self):
        return self.copy.get("COPY_STARTED", 0) > max(
            self.copy.get("COPY_VERIFIED", 0), self.copy.get("UPLOAD_STOPPED", 0))


class History:
    """Fold one already committed event stream in its physical order."""

    def __init__(self, rows, head):
        require(isinstance(rows, list) and rows, "LEDGER_MISSING", "event ledger is missing or empty")
        head_valid(head)
        require(head["last_seq"] == len(rows), "LEDGER_HEAD_MISMATCH",
                "row count disagrees with the independently committed head")
        for index, row in enumerate(rows, 1):
            require(isinstance(row, dict) and positive_integer(row.get("seq")) and row["seq"] == index,
                    "LEDGER_SEQUENCE", f"expected sequence {index} at row {index}")
        require(ledger_digest(rows) == head["digest"], "LEDGER_HEAD_MISMATCH",
                "ordered rows disagree with the independently committed digest")
        self.rows = rows
        self.attempts = {}
        self.spans = set()
        self.receipt_ids = set()
        self.latest = None
        self.stops = []
        self.refusals = []
        self.gates = {}
        self.passed_gates = set()
        self.ready = {}
        self.revision = None
        for row in rows:
            self.fold(row)

    def fold(self, row):
        seq, event = row["seq"], row.get("event")
        label = f"ledger event {seq}"
        require(isinstance(event, str) and event in EVENT_FIELDS, "LEDGER_INVALID", f"{label} has no known event")
        fields(row, {**EVENT_FIELDS[event], "seq": positive_integer, "event": string, "legs": integer},
               "LEDGER_INVALID", label, EVENT_OPTIONAL.get(event))
        require(event in {"LAUNCH", "CLOSE"} or row["legs"] == 0,
                "LEDGER_LEGS", f"{label} must carry zero legs")
        if event == "LAUNCH":
            if self.latest is not None:
                require(self.latest.close is not None, "LEDGER_OVERLAP",
                        f"{row['span_id']} opened before {self.latest.span} closed")
                self.latest.prove_close()
            fields(row["registration"], REGISTRATION, "LEDGER_REGISTRATION", f"{label}.registration")
            require(all(same(row[key], row["registration"][key]) for key in REGISTRATION),
                    "LEDGER_REGISTRATION", f"{label} disagrees with its kit registration")
            require(len(set(row["groups"])) == len(row["groups"]), "LEDGER_REGISTRATION",
                    f"{label} has duplicate group membership")
            require(row["kind"] != "counted" or positive_integer(row["legs"]),
                    "LEDGER_LEGS", f"{label} counted launch needs positive legs")
            if row["kind"] == "counted":
                require(valid_counted_groups(row["groups"], row["entry_id"]), "LEDGER_REGISTRATION",
                        f"{label} lacks explicit registered memberships")
            require(row["span_id"] not in self.spans, "LEDGER_DUPLICATE", f"reused attempt {row['span_id']}")
            self.spans.add(row["span_id"])
            self.latest = self.attempts[seq] = Attempt(row)
        elif event == "GATE":
            self.gates[row["id"]] = row["passed"]
            if row["passed"]:
                self.passed_gates.add(row["id"])
        elif event == "READY":
            self.ready[row["entry_id"]] = row
        elif event == "CONFIG":
            self.revision = {key: row[key] for key in REVISION_FIELDS}
        elif event == "REFUSAL":
            self.refusals.append(row)
        else:
            attempt = self.attempts.get(row["open_seq"])
            require(attempt is not None, "LEDGER_ORPHAN", f"{label} names missing attempt {row['span_id']}")
            require(all(same(row[key], attempt.launch[key]) for key in ("span_id", "entry_id", "kit_sha256")),
                    "LEDGER_ATTEMPT_CONFLICT", f"{label} does not bind to attempt {attempt.span}")
            if event == "STOP":
                self.stops.append((row, attempt))
            elif event in COPY_EVENTS:
                require(attempt.close is not None, "LEDGER_ORPHAN", f"{label} precedes the close of {attempt.span}")
                if event == "COPY_STARTED":
                    require(not attempt.upload_active(), "COPY_OVERLAP",
                            f"{label} restarts an active copy for {attempt.span}")
                else:
                    require(attempt.copy.get(event, 0) <= attempt.copy.get("COPY_STARTED", 0),
                            "LEDGER_DUPLICATE", f"{label} repeats {event} for the same copy of {attempt.span}")
                attempt.copy[event] = seq
            elif event == "CLOSE":
                require(attempt.close is None, "LEDGER_DUPLICATE", f"duplicate close for {attempt.span}")
                require(row["legs"] == attempt.launch["legs"], "LEDGER_LEGS",
                        f"{label} changes the charged legs for {attempt.span}")
                attempt.close = row
            elif event == "RESTORE":
                require(attempt.restore is None, "LEDGER_DUPLICATE", f"duplicate restore for {attempt.span}")
                fields(row["readbacks"], dict.fromkeys(RESTORE_READBACKS, boolean),
                       "RESTORE_INVALID", f"{attempt.span}.restore")
                attempt.restore = row["readbacks"]
            else:
                self.add_receipt(row, attempt)

    def add_receipt(self, row, attempt):
        require(attempt.receipt is None and row["receipt_id"] not in self.receipt_ids,
                "LEDGER_DUPLICATE", f"duplicate or reused receipt for {attempt.span}")
        receipt = row["receipt"]
        fields(receipt, {"entry_id": identifier, "span_id": identifier, "kit_sha256": KIT,
                         "mock": boolean, "rc": lambda value: type(value) is int,
                         "started": IS_OBJECT, "ended": IS_OBJECT}, "RECEIPT_INVALID", attempt.span,
               {"error": nullable(string), "roster": nullable(array(identifier)),
                "span_result": IS_OBJECT})
        for name in ("started", "ended"):
            fields(receipt[name], {"epoch_s": epoch}, "RECEIPT_INVALID", f"{attempt.span}.{name}")
        if "span_result" in receipt:
            span = receipt["span_result"]
            fields(span, {}, "RECEIPT_INVALID", f"{attempt.span}.span_result",
                   {**dict.fromkeys(("outcome", "chain_outcome", "fault"), nullable(string)),
                    "steps": nullable(array(IS_OBJECT))})
            for step in span.get("steps") or ():
                fields(step, {"name": string, "rc": lambda value: type(value) is int},
                       "RECEIPT_INVALID", f"{attempt.span}.steps")
        require(receipt["mock"] is False and all(
            same(receipt[key], attempt.launch[key]) for key in ("span_id", "entry_id", "kit_sha256")
        ), "RECEIPT_CONFLICT", f"{attempt.span} has a mock or wrong-attempt receipt")
        self.receipt_ids.add(row["receipt_id"])
        attempt.receipt = receipt

    def verify_mirrors(self, facts):
        for field, events in MIRRORS.items():
            if field not in facts:
                continue
            projection = [row for row in self.rows if row["event"] in events]
            supplied = facts[field]
            if same(projection, supplied):
                continue
            if isinstance(supplied, list):
                difference = next((row for i, row in enumerate(projection)
                                   if i >= len(supplied) or not same(row, supplied[i])), None)
                if difference is None and len(supplied) > len(projection):
                    difference = supplied[len(projection)]
            else:
                difference = projection[0] if projection else None
            point = (difference.get("span_id") or f"event {difference.get('seq')}"
                     if isinstance(difference, dict) else "projection")
            raise Halt("LEDGER_FACT_CONFLICT", f"{field} disagrees at {point}")
        if "uncopied" in facts:
            debts = self.copy_debts()
            require(same(debts, facts["uncopied"]), "LEDGER_FACT_CONFLICT",
                    f"uncopied disagrees at {debts[0]['span_id'] if debts else 'copy projection'}")
        if "receipt_attestations" in facts:
            attested = facts["receipt_attestations"]
            require(isinstance(attested, list), "LEDGER_FACT_CONFLICT", "receipt_attestations is not a list")
            seen = set()
            for attestation in attested:
                span = attestation.get("span_id") if isinstance(attestation, dict) else None
                attempt = next((run for run in self.attempts.values() if run.span == span), None)
                require(attempt is not None and attempt.receipt is not None and span not in seen and
                        same(project_receipt(attempt.receipt), attestation), "LEDGER_FACT_CONFLICT",
                        f"receipt_attestations disagrees at {span or 'unknown attempt'}")
                seen.add(span)

    def verify_revision(self, observed):
        require(self.revision is not None, "CONFIG_REVISION", "ledger has no committed CONFIG event")
        for key in REVISION_FIELDS:
            require(observed.get(key) == self.revision[key], "CONFIG_REVISION",
                    f"{key} disagrees with the committed CONFIG event")

    def copy_debts(self):
        return [{"span_id": run.span, "entry_id": run.launch["entry_id"], "kind": run.launch["kind"],
                 "ended_epoch": run.close["ended_epoch"]}
                for run in self.attempts.values() if run.close is not None and not run.copy_verified()]

    def contaminated(self):
        return any(row["code"] == CONTAMINATED and not any(
            later.launch["seq"] > attempt.launch["seq"] and later.clean_load()
            and later.close["seq"] > row["seq"] for later in self.attempts.values()
        ) for row, attempt in self.stops)

    def batch_triggered(self, campaign):
        affected = set()
        for stop, attempt in self.stops:
            row = attempt.launch
            if stop["code"] != CONTAMINATED or row["kind"] != "counted" or row["campaign"] != campaign:
                continue
            require(attempt.close is not None and all(
                key in row for key in ("soak_end_epoch", "predicted_batch_epoch")
            ), "BATCH_HISTORY_UNKNOWN", f"{attempt.span} lacks batch timing evidence")
            if row["soak_end_epoch"] <= row["predicted_batch_epoch"] <= attempt.close["ended_epoch"]:
                affected.add(attempt.span)
        return len(affected) >= 2


@dataclass(frozen=True)
class Eligibility:
    rule: str
    detail: str
    until: int | float | None = None


def wait(rule, detail, until):
    return {"decision": "WAIT", "rule": rule, "class": "VALIDITY", "detail": detail,
            "until_epoch": until}
def local_candidates(day, hour, zone):
    naive = datetime.combine(day, hour)
    result = set()
    forward = []
    for fold in (0, 1):
        stamp = naive.replace(tzinfo=zone, fold=fold).timestamp()
        actual = datetime.fromtimestamp(stamp, zone).replace(tzinfo=None)
        if actual == naive:
            result.add(stamp)
        elif actual > naive:
            forward.append(stamp)
    # A spring-forward gap has no such wall time. Use its first valid instant.
    if not result and forward:
        high = int(min(forward))
        low = high - 86400
        while high - low > 1:
            middle = (low + high) // 2
            if datetime.fromtimestamp(middle, zone).replace(tzinfo=None) < naive:
                low = middle
            else:
                high = middle
        result.add(high)
    return sorted(result)


def status_at(rule, day):
    review = rule["review_by"]
    if rule["status"] == "LIVE" and calendar_date(review) and review < day.isoformat():
        return ("FLAG", False) if rule["owner"] == "lead" else ("LIVE", True)
    return rule["status"], False


def entry_groups(entry):
    params = entry["params"]
    group = params.get("group")
    return set(params.get("groups", [group] if group else []))


def qualification(entry):
    params = entry["params"]
    return (params.get("qualification", False) or params.get("batch_clear", False)
            or entry["id"].startswith("qual-") or "qualification" in entry_groups(entry))


def valid_counted_groups(groups, name):
    development = name.startswith("dev-") or any(group.startswith("dev-") for group in groups)
    return (bool(groups) and (not development or "dev-total" in groups)
            and (not name.startswith("qual-") or "qualification" in groups))


def render_argv(entry, now, caller_pid, output_root):
    argv = entry["argv"]
    require(all("<lead fills at merge>" not in arg for arg in [*argv, entry["worktree"]]),
            "LAUNCHER_UNKNOWN", f"{entry['id']} has a launcher placeholder")
    values = {}
    for name in {name for arg in argv for name in PLACEHOLDERS.findall(arg)}:
        if name == "deadline_epoch":
            margin = entry["params"].get("kill_margin_s")
            require(integer(margin) and epoch(now + entry["worst_case_s"] + margin),
                    "DEADLINE_UNKNOWN", f"{entry['id']} has no valid params.kill_margin_s or deadline")
            values[name] = str(math.ceil(now + entry["worst_case_s"] + margin))
        elif name == "out":
            require(string(output_root), "LAUNCHER_UNKNOWN", f"{entry['id']} has no output root")
            values[name] = str(Path(output_root) / f"{entry['id']}-{now}")
        else:
            require(positive_integer(caller_pid), "LAUNCHER_UNKNOWN", f"{entry['id']} needs --caller-pid")
            values[name] = str(caller_pid)
    return [PLACEHOLDERS.sub(lambda match: values[match[1]], arg) for arg in argv]


def plan_signature(entry, facts, now, argv):
    return digest([entry, facts["ledger_head"], facts["queue_commit"], facts["queue_digest"],
                   facts["rules_digest"], facts["now_epoch"], now, argv])


def validate_observation(facts):
    require(isinstance(facts, dict), "FACT_INVALID", "host facts are missing or invalid")
    for key, check in HOST_FIELDS.items():
        rule = ("OWNER_FACT" if key in {"owner_stop", "owner_veto", "maintenance_active", "maintenance_marker"}
                else "FACT_INVALID")
        require(check(facts.get(key)), rule, f"{key} is missing, null or invalid")
    for key in facts:
        require(key in HOST_FIELDS or key in HOST_OPTIONAL, "FACT_INVALID", f"unknown fact {key}")
        if key in HOST_OPTIONAL and key not in MIRRORS:
            require(HOST_OPTIONAL[key](facts[key]), "FACT_INVALID", f"{key} is null or invalid")
    fields(facts["power"], {"ac": boolean, "charging": boolean}, "HOST_POWER", "power")
    if facts.get("errors"):
        raise Halt("PROBE_FAILED", f"failed observation: {sorted(facts['errors'])[0]}")
    for index, row in enumerate(facts["foreign_processes"]):
        fields(row, {"pid": positive_integer, "name": string}, "HOST_CENSUS",
               f"foreign_processes[{index}]")


class Scheduler:
    """Evaluate host, registration and priority against a single folded history."""

    def __init__(self, queue, rules, facts, history, now, caller_pid):
        self.entries = queue["entries"]
        self.by_id = {entry["id"]: entry for entry in self.entries}
        self.admitted = {pair(row) for row in queue["admitted"]}
        self.rules = rules
        self.facts = facts
        self.history = history
        self.now = now
        self.caller_pid = caller_pid
        self.zone = ZoneInfo(queue["timezone"])
        self.today = self.local(now).date()
        self.by_test = {}
        for rule in rules.values():
            status, _ = status_at(rule, self.today)
            if status == "LIVE":
                self.by_test.setdefault(rule["test"], []).append(rule)
        self.blocks = {}
        self.completed = {}
        for attempt in history.attempts.values():
            if attempt.close is not None and attempt.close["clean"] is True:
                self.completed[(attempt.launch["entry_id"], attempt.launch["kit_sha256"])] = attempt
        for entry in self.entries:
            if entry.get("block"):
                self.blocks.setdefault(entry["block"], []).append(entry)
        self.active = {block for block, entries in self.blocks.items()
                       if all(e["kind"] == "counted" for e in entries)
                       and self.completed.get(self.key(entries[0])) is not None
                       and any(not self.done(e) for e in entries[1:])}
        self.commands = {}
        self.batch_rule = self.require_rule("batch_clear") if any(
            entry["kind"] == "counted" for entry in self.entries) else None

    def local(self, when):
        return datetime.fromtimestamp(when, self.zone)

    def require_rule(self, test):
        rows = self.by_test.get(test, ())
        require(len(rows) == 1, "RULE_REQUIRED", f"{test} needs one live register row")
        return rows[0]

    def key(self, entry):
        return entry["id"], entry["kit_sha256"]

    def done(self, entry):
        return entry.get("done", False) or not entry["repeat"] and self.key(entry) in self.completed

    def host(self):
        facts, latest = self.facts, self.history.latest
        power = self.require_rule("host_power")
        disk = self.require_rule("host_disk")
        self.require_rule("host_clean")
        self.require_rule("host_meter")
        quiet = self.require_rule("host_quiet")
        owner = self.require_rule("owner_stop")
        copy = self.require_rule("copy_debt")
        require(facts["power"]["ac"] is True, power["id"], "power.ac is false")
        require(facts["disk_free_gib"] >= disk["params"]["floor_gib"], disk["id"], "disk is below the registered floor")
        require(owner.get("params", {}).get("maintenance_marker") == MAINTENANCE_PATH
                and facts["maintenance_marker"] == MAINTENANCE_PATH, "OWNER_FACT",
                "maintenance observation is not bound to the registered path")
        require(not facts["owner_stop"] and not facts["owner_veto"], owner["id"], "owner stop or veto is active")
        if facts["maintenance_active"]:
            return wait(owner["id"], "owner maintenance marker is active",
                        self.now + owner.get("params", {}).get("recheck_s", 60))
        require(facts["high_power_marker"] is False, "host-clean", "unowned High Power marker")
        require(facts["fence_clear"] is True and facts["runner_group_clear"] is True,
                quiet["id"], "fence or runner group is active")
        require(facts["process_census_verified"] is True, "HOST_CENSUS", "process census is unverified")
        if facts["foreign_processes"]:
            return wait(quiet["id"], "foreign processes are present", self.now + quiet["params"]["recheck_s"])
        until = latest.close["ended_epoch"] + copy["params"]["wait_s"]
        if not latest.copy_verified() and self.now < until:
            return wait(copy["id"], "latest copy is awaiting verification", until)
        require(facts["upload_stopped"] is True, "UPLOAD_ACTIVE", "upload stop before soak is unproven")
        for attempt in self.history.attempts.values():
            require(not attempt.upload_active(), "UPLOAD_ACTIVE",
                    f"{attempt.span} has no upload stop after its latest copy start")
        return None

    def check_clock(self):
        require(self.facts["clock_verified"] is True and self.facts["boot_epoch"] <= self.now,
                "CLOCK_UNVERIFIED", "observation clock or boot epoch is unverified")
        require(self.now >= self.facts["now_epoch"], "CLOCK_ROLLBACK", "requested t0 precedes the probe observation")
        previous = None
        for attempt in self.history.attempts.values():
            start, end = attempt.launch["t0_epoch"], attempt.close["ended_epoch"]
            require(start <= end <= self.now and (previous is None or start >= previous),
                    "CLOCK_ROLLBACK", f"{attempt.span} has an uncertain t0 or close time")
            previous = end

    def registered_history(self):
        """Check new events against the current revision when that registration is available."""
        for attempt in self.history.attempts.values():
            row = attempt.launch
            entry = self.by_id.get(row["entry_id"])
            if entry is None or row["queue_commit"] != self.history.revision["queue_commit"]:
                continue
            params = entry["params"]
            require(pair(row) == pair(entry) and row["kind"] == entry["kind"]
                    and row["block"] == entry.get("block") and set(row["groups"]) == entry_groups(entry)
                    and ("campaign" not in params or row["campaign"] == params["campaign"])
                    and (entry["kind"] != "counted" and "legs" not in params or row["legs"] == params.get("legs")),
                    "LEDGER_REGISTRATION", f"{attempt.span} disagrees with its current kit registration")

    def static_blocks(self, entry):
        def affects(row):
            return row["queue_commit"] == self.history.revision["queue_commit"] and (
                (row["entry_id"], row["kit_sha256"]) == self.key(entry)
                or row["block"] is not None and row["block"] == entry.get("block")
                or row["kit_sha256"] is not None and row["kit_sha256"] == entry["kit_sha256"]
            )

        if any(affects(row) for row in self.history.refusals):
            return Eligibility("not-refused", "a refusal holds the current kit or block")
        for stop, attempt in self.history.stops:
            if stop["code"] in KIT_STOPS and affects(attempt.launch):
                return Eligibility(stop["code"], "the named stop holds this kit or block")
        for attempt in self.history.attempts.values():
            if attempt.close is not None and not attempt.close["clean"] and affects(attempt.launch):
                return Eligibility("NON_CLEAN_CLOSE", f"{attempt.span} holds this kit or block")
        if entry["id"] == "f0-part-c" or any(self.rules[rule]["test"] == "f0_retirement"
                                           for rule in entry["requires"]):
            gate = self.require_rule("f0_retirement")["params"]["gate"]
            require(gate in self.history.gates, "GATE_UNKNOWN", f"{entry['id']} requires gate {gate}")
            if gate in self.history.passed_gates:
                return Eligibility("f0-retirement", "R1 post-close Check retires F0")
        return None

    def period_window(self, entry, day):
        params = entry["params"]
        window = params.get("window")
        require(isinstance(window, dict) and epoch(window.get("latest_epoch")), "DATE_DEADLINE_UNKNOWN",
                f"{entry['id']} has no registered latest t0")
        latest = self.local(window["latest_epoch"])
        earliest = self.local(window["earliest_epoch"]) if window.get("earliest_epoch") is not None else None
        days = max(0, (day - latest.date()).days)
        if days == 0:
            return window.get("earliest_epoch"), window["latest_epoch"]
        start = None if earliest is None else local_candidates(
            earliest.date() + timedelta(days=days), earliest.time(), self.zone)[0]
        finish = local_candidates(latest.date() + timedelta(days=days), latest.time(), self.zone)[-1]
        return start, finish

    def remaining(self, entry):
        if not entry.get("block"):
            return [entry]
        block = self.blocks[entry["block"]]
        return [member for member in block[block.index(entry):] if not self.done(member)]

    def cutoff(self, entry, day):
        latest_start = math.inf
        for member in reversed(self.remaining(entry)):
            require(member["kind"] == "counted", "BLOCK_INVALID",
                    f"{entry.get('block', entry['id'])} mixes counted and other work")
            opening, latest = self.period_window(member, day)
            if self.local(latest).date() != day:
                return None
            latest_start = min(latest, latest_start - member["worst_case_s"])
            if opening is not None and opening > latest_start:
                return None
        return latest_start

    def date_limit(self, entry, day):
        params = entry["params"]
        used = Counter()
        proposed = Counter()
        qual_blocks = set()
        for attempt in self.history.attempts.values():
            row = attempt.launch
            if row["kind"] != "counted" or self.local(row["t0_epoch"]).date() != day:
                continue
            for group in row["groups"]:
                used[group] += row["legs"]
            if "qualification" in row["groups"]:
                qual_blocks.add(row["block"] or row["entry_id"])
        caps = {"dev-mixed": 12, "dev-total": 24}
        excludes = set(params.get("not_on_dates_of", []))
        for member in self.remaining(entry):
            members = entry_groups(member)
            legs = member["params"].get("legs")
            require(positive_integer(legs) and valid_counted_groups(members, member["id"])
                    and (not qualification(member) or "qualification" in members),
                    "DATE_LEGS_UNKNOWN", f"{member['id']} needs positive legs and all registered groups")
            for group in members:
                proposed[group] += legs
            for cap in member["params"].get("date_caps", []):
                group = cap["group"]
                caps[group] = min(caps.get(group, cap["max"]), cap["max"])
            excludes.update(member["params"].get("not_on_dates_of", []))
        if "qualification" in proposed:
            excludes.add("dev-total")
        if "dev-total" in proposed:
            excludes.add("qualification")
        if "qualification" in proposed and "dev-total" in proposed:
            return "block members have disjoint registered groups"
        if any(used[group] for group in excludes):
            return "registered groups are disjoint on this date"
        if "qualification" in proposed and qual_blocks - {entry.get("block") or entry["id"]}:
            return "another qualification block used this date"
        if any(used[group] + proposed[group] > cap for group, cap in caps.items()):
            return "registered counted date cap would be exceeded"
        return None

    def dated_slot(self, entry):
        # Completed members retain their actual date in the ledger. Search
        # only for the remaining starts, on the first lawful date from today.
        day = max(self.local(self.period_window(member, self.today)[1]).date()
                  for member in self.remaining(entry))
        while True:
            opening, latest = self.period_window(entry, day)
            day = self.local(latest).date()
            cutoff = self.cutoff(entry, day)
            start_of_day = local_candidates(day, local_time.min, self.zone)[0]
            start = max(start_of_day, opening if opening is not None else start_of_day)
            unavailable = self.date_limit(entry, day)
            if cutoff is not None and not unavailable and start <= cutoff and self.now <= cutoff:
                return start, cutoff, None
            if cutoff is None or start > cutoff or (
                unavailable and not any(
                    run.launch["kind"] == "counted" and self.local(run.launch["t0_epoch"]).date() == day
                    for run in self.history.attempts.values()
                )
            ):
                return None, None, Eligibility("registered-window", unavailable or "block cannot fit its date")
            day += timedelta(days=1)

    def batch(self, entry, when):
        params = entry["params"]
        if entry["kind"] != "counted":
            return None
        require(identifier(params.get("campaign")), "BATCH_HISTORY_UNKNOWN",
                f"{entry['id']} lacks its registered campaign")
        if not (qualification(entry) or self.history.batch_triggered(params["campaign"])):
            return None
        require(integer(params.get("soak_end_s")) and params["soak_end_s"] <= entry["expected_s"],
                "BATCH_TIMING_UNKNOWN", f"{entry['id']} has no valid soak end")
        batch_params = self.batch_rule["params"]
        boot_batch = self.facts["boot_epoch"] + batch_params["offset_s"]
        period = batch_params["period_s"]
        predicted = boot_batch + max(0, math.ceil((when - boot_batch) / period)) * period
        if when + params["soak_end_s"] <= predicted <= when + entry["expected_s"]:
            return Eligibility(self.batch_rule["id"], "predicted batch overlaps measured interval",
                               predicted + batch_params["settle_s"])
        previous = predicted - period
        if previous >= boot_batch and previous <= when < previous + batch_params["settle_s"]:
            return Eligibility(self.batch_rule["id"], "predicted batch clearance has not elapsed",
                               previous + batch_params["settle_s"])
        return None

    def local_launcher(self, entry):
        window = entry["params"].get("launch_window_local")
        if window is None or entry["id"].startswith("hp-02"):
            return None
        start, end = map(local_time.fromisoformat, window)
        clock = self.local(self.now).time()
        inside = start <= clock <= end if start <= end else clock >= start or clock <= end
        if inside:
            return None
        for day in (self.today, self.today + timedelta(days=1)):
            for stamp in local_candidates(day, start, self.zone):
                if stamp > self.now:
                    return Eligibility("launcher-admits", "frozen launcher window is closed", stamp)
        return Eligibility("launcher-admits", "frozen launcher window is closed")

    def check_plans(self):
        plans = self.facts["plans"]
        output_root = self.require_rule("launcher_admits").get("params", {}).get("output_root")
        expected = {entry["id"]: entry for entry in self.entries if "plan_argv" in entry and not self.done(entry)}
        require(set(plans) == set(expected), "PLAN_UNKNOWN",
                "dry-run observations must cover exactly the pending entries with plan argv")
        for name, entry in expected.items():
            record = plans[name]
            fields(record, {"rc": lambda value: type(value) is int, "signature": hexadecimal(64)},
                   "PLAN_UNKNOWN", f"plans.{name}")
            argv = render_argv(entry, self.now, self.caller_pid, output_root)
            require(record["signature"] == plan_signature(entry, self.facts, self.now, argv),
                    "PLAN_CONFLICT", f"{name} dry run is not bound to this head, observation, t0 and argv")
            self.commands[name] = argv

    def ready_state(self, entry):
        name = entry["id"]
        state = self.history.ready.get(name)
        require(state is not None, "READY_UNKNOWN", f"{name} has no READY transition")
        require(entry.get("expected_ready_by") == state["expected_ready_by"],
                "READY_DEADLINE_CONFLICT", f"{name} queue deadline disagrees with the committed READY transition")
        return state

    def checks(self, entry):
        """Return a known ineligibility. Unknown evidence raises Halt."""
        params, kind = entry["params"], entry["kind"]
        require(pair(entry) in self.admitted, "pin-admitted", f"{entry['id']} pin and kit are not admitted")
        held = self.static_blocks(entry)
        if held is not None:
            return held, None, False
        if kind in COUNTED_KINDS and self.history.contaminated():
            return Eligibility("contaminated-redos", "no later clean span clears the stop"), None, False
        if entry.get("block"):
            members = self.blocks[entry["block"]]
            if any(self.key(member) not in self.completed for member in members[:members.index(entry)]):
                return self.pending(entry, "block-dependency", "a preceding span is not closed clean")
        if kind == "v4_session" and self.active:
            if any(any(qualification(member) for member in self.blocks[block]) for block in self.active):
                return Eligibility("ready-outside-block", "qualification block is in progress"), None, False
        for parent in params.get("after", []):
            if parent not in self.by_id:
                require(any(key[0] == parent for key in self.completed), "DEPENDENCY_UNKNOWN",
                        f"{entry['id']} names unknown predecessor {parent}")
            elif self.key(self.by_id[parent]) not in self.completed:
                return self.pending(entry, "block-dependency", f"{parent} has not closed clean")
        gates = set(params.get("gates", []))
        if kind == "counted" and qualification(entry):
            gates.add("freeze-2")
        for gate in sorted(gates):
            require(gate in self.history.gates, "GATE_UNKNOWN", f"{entry['id']} requires gate {gate}")
            if not self.history.gates[gate]:
                return self.pending(entry, "block-dependency", f"gate {gate} is closed")
        if kind in COUNTED_KINDS and not params.get("pilot"):
            if not any(run.launch["pin"] == entry["pin"] and run.clean_load()
                       for run in self.history.attempts.values()):
                return Eligibility("new-pin-smoke", "a clean native smoke on this pin is owed"), None, False
        if params.get("floating_battery") and self.facts["power"]["charging"]:
            return Eligibility("host-power", "kit requires a floating battery"), None, False
        if kind == "maintenance" and params.get("hygiene_change"):
            hygiene = self.require_rule("hygiene")["params"]
            require(hygiene["start_gate"] in self.history.gates, "GATE_UNKNOWN", "hygiene start gate is unknown")
            if self.history.gates[hygiene["start_gate"]] and not self.history.gates.get(hygiene["end_gate"], False):
                return Eligibility("qualification-hygiene", "qualification hygiene settings are frozen"), None, False
        require(not params.get("dry_run_required") or "plan_argv" in entry, "PLAN_UNKNOWN",
                f"{entry['id']} requires a dry run")
        if "plan_argv" in entry and self.facts["plans"][entry["id"]]["rc"] != 0:
            return Eligibility("launcher-admits", "pinned launcher dry run refused"), None, False

        ready = True
        if kind in COUNTED_KINDS:
            state = self.ready_state(entry)
            ready = state["effective"]
            if kind == "v4_session" and ready:
                require(state["route_clear"], "SESSION_ROUTE", f"{entry['id']} notice and veto route is unproven")
        cutoff = None
        if kind == "counted":
            start, cutoff, failure = self.dated_slot(entry)
            if failure is not None:
                return failure, None, False
            if self.now < start:
                return Eligibility("registered-window", "counted date has not opened", start), cutoff, True
            blocked = self.batch(entry, self.now)
            if blocked is not None:
                return blocked, cutoff, True
        if not ready:
            return Eligibility("session-route" if kind == "v4_session" else "READY_PENDING",
                               "work has not reached READY"), cutoff, True
        failure = self.local_launcher(entry)
        return failure, cutoff, failure is not None

    def pending(self, entry, rule, detail):
        cutoff = self.dated_slot(entry)[1] if entry["kind"] == "counted" else None
        return Eligibility(rule, detail), cutoff, entry["kind"] in COUNTED_KINDS

    def filler_rank(self, entry):
        if entry["kind"] == "diagnostic_filler":
            return 5, ""
        ladder = self.require_rule("filler_ladder")["params"]
        name = entry["id"]
        if name.startswith(ladder["stability_prefix"]):
            already = any(run.launch["entry_id"].startswith(ladder["stability_prefix"])
                          and self.local(run.launch["t0_epoch"]).date() == self.today
                          for run in self.history.attempts.values())
            return (4 if already else 0), ""
        if name.startswith(ladder["instrument_prefix"]):
            return 1, name
        if name.startswith(ladder["high_power_prefix"]):
            return 2, ""
        return 3, ""

    def precedence(self, entry, cutoff):
        return (0 if entry.get("block") in self.active else 1, KINDS.index(entry["kind"]),
                cutoff if cutoff is not None else math.inf,
                self.filler_rank(entry) if entry["kind"] in FILLERS else (0, ""))

    def ranking(self, report):
        checks = []
        for entry in self.entries:
            if self.done(entry):
                report["entries"].append({"id": entry["id"], "kind": entry["kind"], "status": "DONE"})
                continue
            failure, cutoff, pending = self.checks(entry)
            checks.append((entry, failure, cutoff, pending))
        checks.sort(key=lambda item: self.precedence(item[0], item[2]))
        future = [item for item in checks if item[3]]
        eligible, waits = [], []
        for entry, failure, cutoff, _ in checks:
            kind = entry["kind"]
            if failure is None and kind in FILLERS | {"maintenance"}:
                end = self.now + entry["worst_case_s"]
                for other, _, deadline, _ in future:
                    if other["kind"] not in COUNTED_KINDS:
                        continue
                    ready_by = self.ready_state(other)["expected_ready_by"]
                    if kind in FILLERS and ready_by is not None and ready_by <= end:
                        failure = Eligibility("READY_FIT", f"{entry['id']} occupies {other['id']}'s READY deadline")
                        break
                    if deadline is not None and end > deadline:
                        failure = Eligibility("counted-fits", f"{entry['id']} overran {other['id']}'s latest start")
                        break
            row = {"id": entry["id"], "kind": kind, "status": failure.rule if failure else "ELIGIBLE"}
            if failure is not None:
                row.update(rule=failure.rule, detail=failure.detail)
                if failure.until is not None:
                    waits.append(failure)
            else:
                eligible.append(entry)
            report["entries"].append(row)
        if eligible:
            return eligible[0], None
        blocked = next((row for row in report["entries"] if row["status"] == "READY_FIT"), None)
        if blocked is not None:
            return None, {"decision": "HALT", "rule": blocked["rule"], "detail": blocked["detail"]}
        if waits:
            earliest = min(waits, key=lambda item: item.until)
            return None, wait(earliest.rule, earliest.detail, earliest.until)
        return None, {"decision": "QUEUE_EMPTY", "detail": "all unfinished entries are held"}

    def measured(self, entry):
        if entry["kind"] != "maintenance":
            rule = self.require_rule("host_meter")
            require(self.facts.get("meter_ready") is True and self.facts.get("collector_ready") is True,
                    rule["id"], "meter_ready or collector_ready is missing or false")


def checked_config(queue, raw_rules):
    errors = Errors()
    rules = validate_rules("rules", raw_rules, errors)
    validate_queue("queue", queue, rules, errors, True)
    require(not errors.items, "CONFIG_INVALID", errors.items[0] if errors.items else "")
    return rules


def authorize_next(queue, raw_rules, facts, rows, head, *, now=None, caller_pid=None, recheck_head):
    """Construct the only launch decision, after verifying all inputs and rechecking the head."""
    report = {"entries": [], "host": [], "overdue": [], "advisories": []}
    try:
        require(isinstance(rows, list) and rows, "LEDGER_MISSING", "event ledger is missing or empty")
        head_valid(head)
        require(isinstance(facts, dict), "FACT_INVALID", "host facts are missing or invalid")
        require(same(facts.get("ledger_head"), head), "LEDGER_FACT_CONFLICT",
                "ledger_head does not match the independently committed head")
        require(facts.get("queue_digest") == digest(queue) and facts.get("rules_digest") == digest(raw_rules),
                "CONFIG_REVISION", "queue or rule register differs from the probed revision")
        require(isinstance(queue, dict) and isinstance(raw_rules, list), "CONFIG_INVALID", "queue or rules is missing")
        history = History(rows, head)
        history.verify_mirrors(facts)
        validate_observation(facts)
        history.verify_revision(facts)
        rules = checked_config(queue, raw_rules)
        when = facts["now_epoch"] if now is None else now
        require(epoch(when) and when >= facts["now_epoch"], "CLOCK_ROLLBACK", "requested t0 precedes the probe observation")
        require(history.latest is not None, "PREDECESSOR_MISSING", "no attempt opened in the committed ledger")
        if history.latest.close is None:
            decision = {"decision": "CLOSE_OWED", "entry": history.latest.span}
        else:
            history.latest.prove_close()
            scheduler = Scheduler(queue, rules, facts, history, when, caller_pid)
            scheduler.check_clock()
            scheduler.registered_history()
            report["overdue"] = [{"rule": rule["id"], "review_by": rule["review_by"]}
                                 for rule in rules.values() if status_at(rule, scheduler.today)[1]]
            page_age = scheduler.require_rule("copy_debt")["params"].get("page_age_s")
            if page_age is not None:
                report["advisories"] = [f"copy-debt: {debt['span_id']} remains uncopied"
                                        for debt in history.copy_debts()
                                        if when - debt["ended_epoch"] >= page_age]
            decision = scheduler.host()
            if decision is None:
                scheduler.check_plans()
                entry, decision = scheduler.ranking(report)
                if entry is not None:
                    scheduler.measured(entry)
                    argv = scheduler.commands.get(entry["id"])
                    if argv is None:
                        argv = render_argv(entry, when, caller_pid, scheduler.require_rule(
                            "launcher_admits").get("params", {}).get("output_root"))
                    require(same(recheck_head(), head), "LEDGER_HEAD_CHANGED",
                            "committed head changed during authorization")
                    report["decision"] = {
                        "decision": "LAUNCH", "entry": entry["id"], "worktree": entry["worktree"],
                        "argv": argv, "reasons": [f"committed sequence {head['last_seq']}",
                                                  f"proven predecessor {history.latest.span}"],
                    }
                    return report
        require(same(recheck_head(), head), "LEDGER_HEAD_CHANGED", "committed head changed during authorization")
        report["decision"] = decision
    except Halt as err:
        report["decision"] = err.decision
    except (ValueError, OverflowError, RecursionError) as err:
        report["decision"] = Halt("INPUT_DOMAIN", str(err)).decision
    return report


def explain(report):
    for row in report["entries"]:
        print(f"{row['id']} {row['kind']} {row['status']}" + (f" {row['detail']}" if "detail" in row else ""))
    for row in report["overdue"]:
        print(f"OVERDUE {row['rule']} {row['review_by']}")
    for note in report["advisories"]:
        print(note)
    print(as_json(report["decision"]))


def ledger_rows(path, errors):
    try:
        with path.open(encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH)
            for index, line in enumerate(stream, 1):
                try:
                    row = parse_json(line)
                    if not isinstance(row, dict):
                        raise ValueError("expected a JSON object")
                except (ValueError, RecursionError) as err:
                    errors.add(path, "BAD_LEDGER_ROW", f"line {index}: {err}")
                    continue
                yield index, row
    except (OSError, ValueError) as err:
        errors.add(path, "READ_LEDGER", str(err))
def append_decision(path, decision, now):
    line = (as_json({**decision, "now_epoch": now}) + "\n").encode()
    with path.open("a+b") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        if stream.tell():
            stream.seek(-1, os.SEEK_END)
            if stream.read(1) != b"\n":
                raise ValueError("previous ledger row has no terminal newline")
        stream.write(line)
        stream.flush()


def report_ledger(path, since, errors):
    records = []
    for index, row in ledger_rows(path, errors):
        if "decision" not in row and "event" in row:
            continue
        if (not isinstance(row.get("decision"), str) or row["decision"] not in DECISIONS
                or not epoch(row.get("now_epoch"))):
            errors.add(path, "BAD_LEDGER_ROW", f"line {index}: invalid decision or now_epoch")
            continue
        if row["decision"] in ("WAIT", "HALT") and not identifier(row.get("rule")):
            errors.add(path, "BAD_LEDGER_ROW", f"line {index}: invalid rule for {row['decision']}")
            continue
        if records and row["now_epoch"] < records[-1]["now_epoch"]:
            errors.add(path, "LEDGER_ORDER", f"line {index}: decision timestamps went backwards")
        records.append(row)
    if errors.items:
        return
    decisions, rules = Counter(), Counter()
    for previous, current in zip(records, records[1:]):
        duration = current["now_epoch"] - max(since, previous["now_epoch"])
        if duration > 0:
            decisions[previous["decision"]] += duration
            if previous["decision"] in ("WAIT", "HALT"):
                rules[previous["rule"]] += duration
    for heading, totals in (("Hours by decision", decisions), ("Hours by rule (WAIT and HALT)", rules)):
        print(heading)
        for key, seconds in sorted(totals.items()):
            print(f"{key} {seconds / 3600:.6f}")


def parse_power(output):
    source = re.search(r"Now drawing from '(AC|Battery) Power'", output)
    charge = re.search(r";\s*(not charging|charging|charged|discharging)\b", output)
    if source is None:
        raise ValueError("battery summary did not identify a power source")
    if charge is None:
        raise ValueError("battery summary did not identify a charging state")
    return {"ac": source[1] == "AC", "charging": charge[1] == "charging"}


def parse_disk(output):
    for line in output.splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 6 and fields[-1] == "/" and fields[3].isdigit():
            return int(fields[3])
    raise ValueError("df output did not identify available GiB on /")


def parse_labels(output):
    lines = output.strip().splitlines()
    if not lines or lines[0].split() != ["PID", "Status", "Label"]:
        raise ValueError("loaded job list did not identify its columns")
    labels = []
    for line in lines[1:]:
        fields = line.split(maxsplit=2)
        if len(fields) != 3 or not string(fields[2]):
            raise ValueError("loaded job list has an unreadable label")
        labels.append(fields[2])
    return sorted(labels)


def parse_processes(output):
    lines = output.strip().splitlines()
    if not lines or lines[0].split() not in (["PID", "PPID", "COMM"], ["PID", "PPID", "COMMAND"]):
        raise ValueError("ps output did not identify its columns")
    processes = {}
    for line in lines[1:]:
        fields = line.split(maxsplit=2)
        if len(fields) != 3 or not fields[0].isdigit() or not fields[1].isdigit():
            raise ValueError("ps output has an unreadable process")
        processes[int(fields[0])] = (int(fields[1]), fields[2])
    return processes


def process_tree(processes, root):
    descendants = {root}
    frontier = [root]
    children = {}
    for pid, (parent, _) in processes.items():
        children.setdefault(parent, []).append(pid)
    while frontier:
        for child in children.get(frontier.pop(), ()):
            if child not in descendants:
                descendants.add(child)
                frontier.append(child)
    return descendants


def parse_boot(output):
    match = re.search(r"\bsec\s*=\s*(\d+)", output)
    if match is None:
        raise ValueError("sysctl output did not identify the boot epoch")
    return int(match[1])


def project_receipt(receipt):
    def take(row, key, check):
        value = row.get(key)
        return value if check(value) else None

    def obj(row, key):
        value = row.get(key)
        return value if isinstance(value, dict) else {}

    def integer_rc(value):
        return type(value) is int

    span = obj(receipt, "span_result")
    steps = span.get("steps")
    if steps is None:
        steps = receipt.get("steps")
    result = {
        "entry_id": take(receipt, "entry_id", identifier),
        "kit_sha256": take(receipt, "kit_sha256", KIT),
        "rc": take(receipt, "rc", integer_rc),
        "error": take(receipt, "error", string),
        "mock": take(receipt, "mock", boolean),
        "roster": take(receipt, "roster", array(identifier)),
        "started": {"epoch_s": take(obj(receipt, "started"), "epoch_s", epoch)},
        "ended": {"epoch_s": take(obj(receipt, "ended"), "epoch_s", epoch)},
        "span_result": {
            "outcome": take(span, "outcome", string),
            "chain_outcome": take(span, "chain_outcome", string),
            "fault": take(span, "fault", string),
            "steps": [{"name": take(step, "name", string), "rc": take(step, "rc", integer_rc)}
                      for step in steps if isinstance(step, dict)] if isinstance(steps, list) else None,
        },
    }
    if "span_id" in receipt:
        result["span_id"] = take(receipt, "span_id", identifier)
    return result


def read_regular_json(path, *, dir_fd=None):
    # O_NOFOLLOW closes the gap between enumerating a file and opening it.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dir_fd)
    with os.fdopen(fd, encoding="utf-8") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("expected a regular JSON file")
        data = parse_json(stream.read())
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")
    return data


def receipt_files(root, depth=1, *, dir_fd=None):
    # Walk by descriptor so renaming a parent or substituting a symlink cannot
    # redirect an open outside the explicitly supplied roots.
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dir_fd)
    try:
        with os.scandir(fd) as files:
            for entry in sorted(files, key=lambda row: row.name):
                if entry.name == "runner_receipt.json" and entry.is_file(follow_symlinks=False):
                    yield fd, entry.name
                elif depth < 4 and entry.is_dir(follow_symlinks=False):
                    yield from receipt_files(entry.name, depth + 1, dir_fd=fd)
    finally:
        os.close(fd)


def probe_command(command, parse, fact, errors):
    # Every probe command is a fixed, whitespace-separated native getter.
    argv = command.split()
    try:
        child = subprocess.run(argv, capture_output=True, text=True, check=False,
                               timeout=15, env={**os.environ, "LC_ALL": "C"})
        if child.returncode:
            raise ValueError(f"{Path(argv[0]).name} exited {child.returncode}")
        return parse(child.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired) as err:
        errors[fact] = str(err)
        return None


def probe_plans(queue, rules, facts, history, args, errors):
    plans = {}
    if (history is None or history.latest is None or history.latest.close is None
            or facts["fence_clear"] is not True or facts["runner_group_clear"] is not True
            or facts["process_census_verified"] is not True or facts["foreign_processes"]):
        errors["plans"] = "dry run requires a committed close and a clear runner census"
        return plans
    try:
        history.latest.prove_close()
    except Halt as err:
        errors["plans"] = err.decision["detail"]
        return plans
    output_root = next((row.get("params", {}).get("output_root") for row in rules.values()
                        if row["test"] == "launcher_admits" and row["status"] == "LIVE"), None)
    completed = {(run.launch["entry_id"], run.launch["kit_sha256"]) for run in history.attempts.values()
                 if run.close is not None and run.close["clean"]}
    now = facts["now_epoch"]
    for entry in queue["entries"]:
        name = entry["id"]
        if ("plan_argv" not in entry or entry.get("done")
                or not entry["repeat"] and (name, entry["kit_sha256"]) in completed):
            continue
        try:
            argv = render_argv(entry, now, args.caller_pid, output_root)
            signature = plan_signature(entry, facts, now, argv)
            child = subprocess.run(entry["plan_argv"], cwd=entry["worktree"], check=False,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            plans[name] = {"signature": signature, "rc": child.returncode}
        except (Halt, OSError, ValueError, subprocess.TimeoutExpired) as err:
            errors[f"plans.{name}"] = f"dry run failed: {type(err).__name__}"
    return plans


def probe_maintenance(args, errors):
    active = False
    paths = {Path(MAINTENANCE_PATH): None}
    if args.maintenance_marker is not None:
        paths[args.maintenance_marker] = None
    for path in paths:
        try:
            path.lstat()
            active = True
        except FileNotFoundError:
            continue
        except OSError:
            errors["maintenance_active"] = "a maintenance marker could not be checked"
    return None if not active and "maintenance_active" in errors else active


def probe(args, queue, raw_rules, rules, supplied):
    failures = {}
    power = probe_command("/usr/bin/pmset -g batt", parse_power, "power", failures)
    disk = probe_command("/bin/df -g /", parse_disk, "disk_free_gib", failures)
    labels = probe_command("/bin/launchctl list", parse_labels, "labels_loaded", failures)
    processes = probe_command("/bin/ps -axo pid,ppid,comm", parse_processes, "foreign_processes", failures)
    boot = probe_command("/usr/sbin/sysctl -n kern.boottime", parse_boot, "boot_epoch", failures)
    now = time.time()
    quiet = [row for row in rules.values() if row["test"] == "host_quiet" and row["status"] == "LIVE"]
    foreign = None
    if processes is not None and len(quiet) == 1:
        patterns = [re.compile(pattern) for pattern in quiet[0]["params"]["patterns"]]
        root = args.caller_pid or os.getppid()
        if root in processes:
            excluded = process_tree(processes, root)
            foreign = [{"pid": pid, "name": name} for pid, (_, name) in sorted(processes.items())
                       if pid not in excluded and any(pattern.search(name) for pattern in patterns)]
        else:
            failures["foreign_processes"] = "caller pid is absent from the process census"

    fence_clear = supplied.get("fence_clear")
    if args.custody is not None:
        try:
            read_regular_json(args.custody / "desk_fence.json")
            fence_clear = False
        except FileNotFoundError:
            fence_clear = True if args.custody.is_dir() else None
        except (OSError, ValueError, RecursionError):
            fence_clear = None
            failures["fence_clear"] = "fence state could not be read"
    receipts = []
    for root in args.receipt_root:
        try:
            for directory, name in receipt_files(root):
                try:
                    receipts.append(project_receipt(read_regular_json(name, dir_fd=directory)))
                except (OSError, ValueError, RecursionError):
                    failures["receipt_attestations"] = "a receipt could not be projected"
        except (OSError, ValueError):
            failures["receipt_attestations"] = "receipt root could not be read"
    history, head = None, None
    revisions = {"queue_digest": digest(queue), "rules_digest": digest(raw_rules)}
    if args.ledger is not None:
        try:
            head_path = args.ledger_head or default_head_path(args.ledger)
            head = read_head(head_path)
            history = History(read_events(args.ledger), head)
            require(history.revision is not None, "CONFIG_REVISION", "ledger has no committed CONFIG event")
            queue_commit = history.revision["queue_commit"]
            history.verify_revision({"queue_commit": queue_commit, **revisions})
            require(all(observed is None or observed == queue_commit
                        for observed in (args.queue_commit, supplied.get("queue_commit"))),
                    "CONFIG_REVISION", "supplied queue commit disagrees with the committed CONFIG event")
            require(same(read_head(head_path), head), "LEDGER_HEAD_CHANGED", "head changed during probe")
        except Halt as err:
            failures["ledger_head"] = err.decision["detail"]
            history, head = None, None
    facts = {key: supplied.get(key) for key in HOST_FIELDS}
    facts.update(now_epoch=now, boot_epoch=boot, power=power, disk_free_gib=disk,
                 foreign_processes=foreign, process_census_verified=foreign is not None,
                 fence_clear=fence_clear, ledger_head=head, **revisions,
                 queue_commit=history.revision["queue_commit"] if history is not None else None,
                 maintenance_marker=MAINTENANCE_PATH,
                 maintenance_active=probe_maintenance(args, failures), plans={})
    for key in ("meter_ready", "collector_ready"):
        if key in supplied:
            facts[key] = supplied[key]
    if labels is not None:
        facts["labels_loaded"] = labels
    if args.receipt_root:
        facts["receipt_attestations"] = receipts
    if args.run_plans:
        facts["plans"] = probe_plans(queue, rules, facts, history, args, failures)
    facts["errors"] = failures
    return facts, failures
def write_facts(path, facts):
    # Readers see either the previous complete probe or this complete probe.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(as_json(facts) + "\n")
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def parse_since(value):
    when = datetime.fromisoformat(value)
    if when.tzinfo is None:
        raise ValueError("ISO8601 needs a UTC offset")
    return when.timestamp()


def parse_epoch(value):
    try:
        when = float(value)
    except ValueError as err:
        raise argparse.ArgumentTypeError("expected an epoch") from err
    if not epoch(when):
        raise argparse.ArgumentTypeError("epoch is outside the supported range")
    return int(when) if when.is_integer() else when


def positive_pid(value):
    if not value.isdecimal() or not int(value) > 0:
        raise argparse.ArgumentTypeError("expected a positive pid")
    return int(value)


def create_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "explain", "next", "probe"):
        command = commands.add_parser(name)
        command.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
        command.add_argument("--rules", type=Path, default=DEFAULT_RULES)
        if name != "validate":
            command.add_argument("--ledger", type=Path, help="committed structural event ledger")
            command.add_argument("--ledger-head", type=Path, help="writer's independent committed head (default: LEDGER.head.json)")
        if name in ("explain", "next"):
            command.add_argument("--facts", type=Path)
            command.add_argument("--now")
        if name == "explain":
            command.add_argument("--json", action="store_true")
        elif name == "next":
            command.add_argument("--record", type=Path, help="append to a separate decision observation ledger")
        elif name == "probe":
            command.add_argument("--out", type=Path, required=True)
            command.add_argument("--custody", type=Path, help="directory containing desk_fence.json")
            command.add_argument("--receipt-root", type=Path, action="append", default=[])
            command.add_argument("--host-facts", type=Path, help="current external structural host observations")
            command.add_argument("--queue-commit", type=str)
            command.add_argument("--maintenance-marker", type=Path, help="additional stop marker to check")
            command.add_argument("--run-plans", action="store_true")
        if name in ("next", "explain", "probe"):
            command.add_argument("--self-pid", "--caller-pid", type=positive_pid, dest="caller_pid")
    command = commands.add_parser("report")
    command.add_argument("--ledger", type=Path, required=True)
    command.add_argument("--since", required=True)
    return parser


def control_inputs(args):
    require(args.ledger is not None, "LEDGER_MISSING", "no committed event ledger was supplied")
    head_path = args.ledger_head or default_head_path(args.ledger)
    require(head_path.resolve() != args.ledger.resolve(), "LEDGER_HEAD_INVALID",
            "event ledger and committed head need separate files")
    head = read_head(head_path)
    rows = read_events(args.ledger)
    require(args.facts is not None, "FACT_INVALID", "no facts snapshot was supplied")
    errors = Errors()
    queue = errors.read_json(args.queue)
    rules = errors.read_json(args.rules)
    facts = errors.read_json(args.facts)
    require(not errors.items, "FACT_INVALID", errors.items[0] if errors.items else "")
    return queue, rules, facts, rows, head, head_path


def separate_output(out, inputs):
    for path in inputs:
        if path is None:
            continue
        if path.resolve() == out.resolve() or path.exists() and out.exists() and path.samefile(out):
            return False
    return True


def scheduling_command(args):
    facts = None
    try:
        if args.now is not None:
            try:
                args.now = parse_epoch(args.now)
            except argparse.ArgumentTypeError as err:
                raise Halt("CLOCK_INVALID", str(err)) from err
        queue, rules, facts, rows, head, head_path = control_inputs(args)
        if args.command == "next" and args.record is not None:
            require(separate_output(args.record, (args.ledger, head_path, args.queue, args.rules, args.facts)),
                    "RECORD_PATH", "decision record must be separate from scheduler inputs")
        report = authorize_next(queue, rules, facts, rows, head, now=args.now, caller_pid=args.caller_pid,
                                recheck_head=lambda: read_head(head_path))
    except Halt as err:
        report = {"entries": [], "host": [], "overdue": [], "advisories": [], "decision": err.decision}
    if args.command == "explain":
        if args.json:
            print(as_json(report))
        else:
            explain(report)
        return 0
    decision = report["decision"]
    if args.record is not None and decision.get("rule") != "RECORD_PATH" and isinstance(facts, dict):
        now = args.now if args.now is not None else facts.get("now_epoch")
        if epoch(now):
            try:
                append_decision(args.record, decision, now)
            except (OSError, ValueError):
                decision = Halt("RECORD_WRITE", "decision observation could not be appended").decision
    print(as_json(decision))
    return 0


def main(argv=None):
    args = create_parser().parse_args(argv)
    if args.command in ("next", "explain"):
        return scheduling_command(args)
    errors = Errors()
    if args.command == "report":
        try:
            since = parse_since(args.since)
        except (ValueError, OverflowError) as err:
            errors.add(args.ledger, "BAD_SINCE", str(err))
        else:
            report_ledger(args.ledger, since, errors)
        return errors.finish()
    raw_rules = errors.read_json(args.rules)
    queue = errors.read_json(args.queue)
    if not isinstance(raw_rules, list) and not errors.items:
        errors.add(args.rules, "BAD_VALUE", "rules must be an array")
    if queue is None and not errors.items:
        errors.add(args.queue, "BAD_VALUE", "queue must be an object")
    rules = validate_rules(args.rules, raw_rules, errors)
    validate_queue(args.queue, queue, rules, errors, isinstance(raw_rules, list))
    if args.command == "validate" or errors.items:
        return errors.finish()
    supplied = errors.read_json(args.host_facts) if args.host_facts else {}
    if not isinstance(supplied, dict):
        errors.add(args.host_facts, "BAD_VALUE", "host facts must be an object")
    head_path = args.ledger_head or (default_head_path(args.ledger) if args.ledger is not None else None)
    if not separate_output(args.out, (args.ledger, head_path, args.queue, args.rules, args.host_facts)):
        errors.add(args.out, "WRITE_FACTS", "probe output must be separate from its inputs")
    if errors.items:
        return errors.finish()
    facts, failures = probe(args, queue, raw_rules, rules, supplied)
    try:
        write_facts(args.out, facts)
    except (OSError, ValueError) as err:
        errors.add(args.out, "WRITE_FACTS", str(err))
        return errors.finish()
    return 3 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
