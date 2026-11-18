#!/usr/bin/env python3
"""Validate the MBP schedule and recommend one action from structural facts.

Ledger decision observations have a decision key. Producers record actual host
events with an event key (LAUNCH, CLOSE, COPY_VERIFIED, REFUSAL, STOP, GATE, READY).
Only those events are used as launch and close history.

LAUNCH, CLOSE, COPY_VERIFIED and the receipt share a span_id for each attempt.
Legacy inputs use entry_id, kit_sha256 and t0_epoch. Order launches by sequence
or by boot_id, boot_order and monotonic_ns, with append order as the legacy
fallback. A CLOSE adds kind, ended_epoch, clean and the RESTORE_READBACKS.
A GATE carries its id. REFUSAL, STOP and READY use the respective facts fields.
When a facts snapshot and a ledger are both supplied, the ledger must retain
every launch and close observation in the snapshot.

Probe sources that need no native command (for example meter readiness, the
High Power marker and queue commit) can be supplied via --host-facts. Probe
outputs null when a source is unavailable. Production close and host-fact
producers are separate from this scheduler.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
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
    "argv": argument_vector, "pin": PIN, "kit_sha256": KIT, "expected_s": integer,
    "worst_case_s": integer, "requires": array(identifier), "params": IS_OBJECT,
    "repeat": boolean, "product": string,
}
ENTRY_OPTIONAL = {
    "block": identifier, "expected_ready_by": epoch, "plan_argv": argument_vector,
    "done": boolean, "close_gap_s": integer,
}
ENTRY_PARAMS = {
    "window": IS_OBJECT, "date_caps": array(IS_OBJECT), "not_on_dates_of": array(identifier),
    "batch_clear": boolean, "soak_end_s": integer, "group": identifier, "legs": positive_integer,
    "after": array(identifier), "gates": array(identifier), "launch_window_local":
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
                    and not restricted.intersection({"window", "dependency", "session_route"})):
                standing = True
            if (entry.get("kind") == "counted" and isinstance(params, dict)
                    and any(params.get(key) for key in ("window", "date_caps", "not_on_dates_of"))
                    and not any(ref in rules and rules[ref]["test"] == "window"
                                and rules[ref]["status"] == "LIVE" for ref in refs)):
                errors.add(path, "UNBOUND_DATE_RULE", f"{entry_id}: configured dates require a LIVE window rule")
        if isinstance(params, dict):
            validate_entry_params(path, where, params, errors)
            if entry.get("kind") == "counted":
                if params.get("date_caps") and not identifier(params.get("group")):
                    errors.add(path, "MISSING_COUNT_METADATA",
                               f"{where}.params.group is required for a counted date cap")
                if (params.get("date_caps") or params.get("group")) and "legs" not in params:
                    errors.add(path, "MISSING_COUNT_METADATA",
                               f"{where}.params.legs is required for grouped counted work")
    if check_references and not standing:
        errors.add(path, "NO_STANDING_FILLER", "no unfinished repeating filler free of window, dependency and session_route")


def validate_entry_params(path, where, params, errors):
    where = f"{where}.params"
    errors.fields(path, where, params, {}, ENTRY_PARAMS)
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


FACT_TYPES = {
    "now_epoch": epoch, "boot_epoch": epoch, "power": IS_OBJECT, "disk_free_gib": number,
    "meter_ready": boolean, "fence": IS_OBJECT, "labels_loaded": array(string),
    "foreign_processes": array(IS_OBJECT), "high_power_marker": boolean, "owner_stop": boolean,
    "maintenance_active": boolean,
    "launches": array(IS_OBJECT), "closes": array(IS_OBJECT), "refusals": array(IS_OBJECT),
    "gates": array(identifier), "ready": array(IS_OBJECT), "queue_commit": string,
    "uncopied": array(IS_OBJECT), "stops": array(IS_OBJECT), "plans": IS_OBJECT,
    "errors": IS_OBJECT, "receipts": array(nullable(IS_OBJECT)),
}
CLOSE_FIELDS = {"entry_id": identifier, "kind": nullable(one_of(*KINDS)),
                "ended_epoch": nullable(epoch), "clean": nullable(boolean),
                "restore_proven": nullable(boolean), "t0_epoch": nullable(epoch)}
ATTEMPT_FIELDS = {"span_id": identifier, "sequence": integer, "boot_id": identifier,
                  "boot_order": integer, "monotonic_ns": integer, "ledger_index": integer}
CLOSE_OPTIONAL = {**ATTEMPT_FIELDS, "kit_sha256": KIT, "pin": PIN, "mock": nullable(boolean),
                  "copy_verified": nullable(boolean), "fault": nullable(string),
                  "load_redos": nullable(integer), "load_flag": nullable(boolean), "stranded": boolean,
                  "group": nullable(identifier), "legs": integer}
RESTORE_READBACKS = ("power_mode", "network_time_off", "frequency_word_zero", "no_monitor",
                     "no_high_power_marker", "feeds_stopped", "process_group_gone")
LAUNCH_FIELDS = {"entry_id": identifier, "t0_epoch": nullable(epoch)}
LAUNCH_OPTIONAL = {**ATTEMPT_FIELDS, "kit_sha256": KIT, "kind": one_of(*KINDS),
                   "group": nullable(identifier), "legs": integer}
FACT_ROWS = {
    "launches": (LAUNCH_FIELDS, LAUNCH_OPTIONAL),
    "closes": (CLOSE_FIELDS, CLOSE_OPTIONAL),
    "foreign_processes": ({"pid": integer, "name": string}, {}),
    "ready": ({"entry_id": identifier, "effective": nullable(boolean)}, {}),
    "refusals": ({"entry_id": identifier, "queue_commit": string, "epoch": epoch, "reason": string},
                 {"kit_sha256": KIT, "block": identifier}),
    "uncopied": ({"entry_id": identifier, "kind": nullable(one_of(*KINDS)),
                  "ended_epoch": nullable(epoch)}, {"kit_sha256": KIT}),
    "stops": ({"code": identifier, "epoch": epoch},
              {"entry_id": identifier, "queue_commit": string, "kit_sha256": KIT, "block": identifier}),
}


def validate_facts(path, data, errors, now=None):
    if data is None:
        return
    if not isinstance(data, dict):
        errors.add(path, "BAD_VALUE", "facts must be an object")
        return
    for key, check in FACT_TYPES.items():
        if key in data and not nullable(check)(data[key]):
            errors.add(path, "BAD_VALUE", f"facts.{key}")
    if now is None and not epoch(data.get("now_epoch")):
        errors.add(path, "MISSING_CLOCK", "now_epoch or --now is required")
    if isinstance(data.get("power"), dict):
        errors.fields(path, "facts.power", data["power"], {},
                      {"ac": nullable(boolean), "charging": nullable(boolean)})
    if isinstance(data.get("fence"), dict):
        errors.fields(path, "facts.fence", data["fence"], {}, {
            "purpose": nullable(string), "pid": nullable(integer), "deadline": nullable(epoch),
            "pid_alive": nullable(boolean),
        })
    for key, (required, optional) in FACT_ROWS.items():
        if isinstance(data.get(key), list):
            for index, row in enumerate(data[key]):
                errors.fields(path, f"facts.{key}[{index}]", row, required, optional)
    if isinstance(data.get("receipts"), list):
        for index, receipt in enumerate(data["receipts"]):
            if receipt is not None and project_receipt(receipt) != receipt:
                errors.add(path, "BAD_RECEIPT_PROJECTION", f"facts.receipts[{index}]")


def status_at(rule, day):
    review = rule["review_by"]
    status = rule["status"]
    if status == "LIVE" and calendar_date(review) and review < day.isoformat():
        if rule["owner"] == "lead":
            return "FLAG", False
        return "LIVE", True
    return status, False


@dataclass(frozen=True)
class Check:
    detail: str = "holds"
    holds: bool = True
    until: int | float | None = None


def fails(detail, until=None):
    return Check(detail, False, until)


def missing(name):
    return fails(f"{name} is null or missing")


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


def identity(record):
    when = ("span", record["span_id"]) if "span_id" in record else ("t0", record["t0_epoch"])
    return record["entry_id"], record.get("kit_sha256"), when


def attempt_name(attempt):
    return attempt.get("span_id", attempt["entry_id"])


def latest_attempt(attempts):
    if not attempts:
        return None, None
    if any("sequence" in row for row in attempts):
        if any("sequence" not in row for row in attempts):
            return None, "launch sequence is incomplete"
        newest = max(attempts, key=lambda row: row["sequence"])
        if sum(row["sequence"] == newest["sequence"] for row in attempts) != 1:
            return None, "latest launch sequence is ambiguous"
        return newest, None
    if all("boot_order" in row for row in attempts):
        order = max(row["boot_order"] for row in attempts)
        in_boot = [row for row in attempts if row["boot_order"] == order]
        latest_boots = {row["boot_id"] for row in in_boot if "boot_id" in row}
        if len(latest_boots) > 1:
            return None, "latest boot order is ambiguous"
    elif all("boot_id" in row for row in attempts):
        newest_boot = next(reversed(dict.fromkeys(row["boot_id"] for row in attempts)))
        in_boot = [row for row in attempts if row.get("boot_id") == newest_boot]
    else:
        # A missing boot stamp says nothing about which boot contained the
        # attempt. Keep every attempt in the append-ordered history.
        return attempts[-1], None
    if all("monotonic_ns" in row for row in in_boot):
        newest = max(in_boot, key=lambda row: row["monotonic_ns"])
        if sum(row["monotonic_ns"] == newest["monotonic_ns"] for row in in_boot) != 1:
            return None, "latest monotonic launch stamp is ambiguous"
        return newest, None
    return in_boot[-1], None


class AttemptHistory:
    def __init__(self, facts):
        self.launches = facts.get("launches")
        self.closes = facts.get("closes")
        self.latest, self.order_error = latest_attempt(self.launches)
        self.receipts = {}
        for receipt in facts.get("receipts") or []:
            if receipt is not None and receipt["mock"] is False and receipt["entry_id"] is not None:
                start = receipt["started"]["epoch_s"]
                finish = receipt["ended"]["epoch_s"]
                if start is not None and finish is not None and start <= finish:
                    key = identity({**receipt, "t0_epoch": start})
                    self.receipts.setdefault(key, set()).add(finish)

        self.closes_by_launch = {}
        self.unpaired_closes = []
        by_identity = {}
        for index, launch in enumerate(self.launches or []):
            by_identity.setdefault(identity(launch), []).append((index, launch))
        self.reused_ids = {key for key, attempts in by_identity.items() if len(attempts) > 1}
        for close in self.closes or []:
            matching = [index for index, launch in by_identity.get(identity(close), ())
                        if self.close_follows(launch, close)]
            if len(matching) == 1:
                self.closes_by_launch.setdefault(matching[0], []).append(close)
            elif not by_identity.get(identity(close)):
                self.unpaired_closes.append(close)

        if self.latest is not None:
            index = next(index for index, launch in enumerate(self.launches) if launch is self.latest)
            self.latest_close = next(iter(self.closes_by_launch.get(index, ())), None)
        else:
            self.latest_close = None

    @staticmethod
    def close_follows(launch, close):
        if "ledger_index" in launch and "ledger_index" in close:
            if close["ledger_index"] <= launch["ledger_index"]:
                return False
        return all(key not in launch or key not in close or launch[key] == close[key]
                   for key in ("sequence", "boot_id", "boot_order", "monotonic_ns", "t0_epoch"))

    def receipt_matches(self, close):
        key = identity(close)
        finishes = self.receipts.get(key, ())
        return (key not in self.reused_ids and close["t0_epoch"] is not None
                and close["ended_epoch"] is not None and len(finishes) == 1
                and close["t0_epoch"] <= next(iter(finishes)) <= close["ended_epoch"])

    def runs(self):
        for index, launch in enumerate(self.launches or []):
            yield launch, self.closes_by_launch.get(index, ())
        for close in self.unpaired_closes:
            yield close, ()


def kit_matches(record, entry):
    return (record.get("entry_id") == entry["id"]
            and record.get("kit_sha256") == entry["kit_sha256"])


def plan_signature(entry, queue_commit):
    data = [entry["plan_argv"], entry["worktree"], entry["pin"], entry["kit_sha256"], queue_commit]
    return hashlib.sha256(as_json(data).encode()).hexdigest()


class Scheduler:
    def __init__(self, queue, rules, facts, now, caller_pid=None):
        self.entries = queue["entries"]
        self.by_id = {entry["id"]: entry for entry in self.entries}
        self.admitted = {pair(row) for row in queue["admitted"]}
        self.rules = rules
        self.facts = facts
        self.now = now
        self.zone = ZoneInfo(queue["timezone"])
        self.today = self.local(now).date()
        self.caller_pid = caller_pid
        self.closes = facts.get("closes")
        self.history = AttemptHistory(facts)
        self.bound_closes = [
            rows[0] for rows in self.history.closes_by_launch.values()
            if self.history.receipt_matches(rows[0])
        ]
        self.newest = self.history.latest_close
        self.launches = facts.get("launches")
        self.rule_status = {key: status_at(rule, self.today) for key, rule in rules.items()}
        self.blocks = {}
        for entry in self.entries:
            if "block" in entry:
                self.blocks.setdefault(entry["block"], []).append(entry)
        self.active_blocks = {name for name, entries in self.blocks.items()
                              if all(entry["kind"] == "counted" for entry in entries)
                              and self.closed_clean(entries[0]) and any(not self.done(e) for e in entries[1:])}
        self.batches = next((rule["params"] for rule in rules.values()
                             if rule["test"] == "batch_clear" and rule["status"] != "RETIRED"), None)
        self.ladder = next((rule["params"] for rule in rules.values()
                            if rule["test"] == "filler_ladder" and self.live(rule)), None)
        self.output_root = next((rule.get("params", {}).get("output_root") for rule in rules.values()
                                 if rule["test"] == "launcher_admits" and rule["status"] != "RETIRED"), None)
        self.cutoffs = {}

    def local(self, when):
        return datetime.fromtimestamp(when, self.zone)

    def live(self, rule):
        return self.rule_status.get(rule["id"], ("LIVE", False))[0] == "LIVE"

    def closed_clean(self, entry):
        return any(kit_matches(close, entry) and close["clean"] is True
                   for close in self.bound_closes)

    def done(self, entry):
        return entry.get("done", False) or not entry["repeat"] and self.closed_clean(entry)

    def latest_launch_owed(self):
        if self.history.latest is not None and self.newest is None and self.closes is not None:
            return attempt_name(self.history.latest)
        return None

    def host_check(self, rule):
        facts = self.facts
        test = rule["test"]
        params = rule.get("params", {})
        fence = facts.get("fence")
        if test == "host_power":
            ac = (facts.get("power") or {}).get("ac")
            return missing("power.ac") if ac is None else Check("AC power required", ac)
        if test == "host_disk":
            disk = facts.get("disk_free_gib")
            floor = params["floor_gib"]
            return missing("disk_free_gib") if disk is None else Check(f"disk floor: {floor} GiB", disk >= floor)
        if test == "host_meter":
            ready = facts.get("meter_ready")
            return missing("meter_ready") if ready is None else Check("meter or collector unavailable", ready)
        if test == "host_clean":
            errors = facts.get("errors") or {}
            if "attempt_history" in errors:
                return fails(errors["attempt_history"] if string(errors["attempt_history"])
                             else "launch and close evidence conflict")
            if self.closes is None:
                return missing("closes")
            if self.history.order_error:
                return fails(self.history.order_error)
            if self.closes and self.history.latest is None:
                return missing("launch attempt history for the recorded close")
            if self.newest is not None:
                span = attempt_name(self.history.latest or self.newest)
                ended = self.newest["ended_epoch"]
                if ended is None:
                    return missing(f"{span} close.ended_epoch")
                if self.newest["restore_proven"] is not False and not self.history.receipt_matches(self.newest):
                    return fails(f"{span} has no matching close receipt")
                if self.newest["restore_proven"] is not True:
                    if self.newest["restore_proven"] is None:
                        return missing(f"{span} close.restore_proven")
                    return fails(f"{span} close has unproven restoration")
                if ended > self.now:
                    return fails(f"{span} close ends after the requested start")
            marker = facts.get("high_power_marker")
            if marker is None:
                return missing("high_power_marker")
            if marker and (fence is None or fence.get("pid_alive") is not True):
                return fails("High Power marker has no live fence")
        if test == "host_quiet":
            if "fence" not in facts or "fence" in (facts.get("errors") or {}):
                return missing("fence")
            if fence is not None:
                alive, deadline = fence.get("pid_alive"), fence.get("deadline")
                if alive is None:
                    return missing("fence.pid_alive")
                if alive is True:
                    if deadline is None:
                        return missing("fence.deadline")
                    if deadline <= self.now:
                        return fails("fence deadline passed with its process still alive")
                    return fails("fence process is alive", deadline)
            if self.launches is None:
                return missing("launches")
            owed = self.latest_launch_owed()
            if owed is not None:
                return fails(f"{owed} has no matching close")
            foreign = facts.get("foreign_processes")
            if foreign is None:
                return missing("foreign_processes")
            if foreign:
                return fails("foreign processes are present", self.now + params["recheck_s"])
        if test == "owner_stop":
            stop = facts.get("owner_stop")
            maintenance = facts.get("maintenance_active")
            if stop is True or maintenance is True:
                retry = params.get("recheck_s")
                return fails("owner maintenance or stop is active", self.now + retry if retry else None)
            if stop is None:
                return missing("owner_stop")
            if maintenance is None and (params.get("maintenance_marker") or "maintenance_active" in facts):
                return missing("maintenance_active")
        if test == "copy_debt" and self.newest is not None:
            ended = self.newest["ended_epoch"]
            if ended is None:
                return missing("newest close.ended_epoch")
            until = ended + params["wait_s"]
            if self.now < until and self.newest.get("copy_verified") is not True:
                uncopied = facts.get("uncopied")
                if uncopied is None or any(
                    item["entry_id"] == self.newest["entry_id"] and item["ended_epoch"] == ended
                    and item.get("kit_sha256") == self.newest.get("kit_sha256") for item in uncopied
                ):
                    return fails("newest close has no verified copy yet", until)
        return Check()

    def shift_window(self, entry, days):
        window = entry["params"].get("window", {})
        shifted = []
        for key in ("earliest_epoch", "latest_epoch"):
            when = window.get(key)
            if when is not None and days:
                local = self.local(when)
                candidates = local_candidates(local.date() + timedelta(days=days), local.time(), self.zone)
                when = candidates[min(local.fold, len(candidates) - 1)]
            shifted.append(when)
        return shifted

    def remaining(self, entry):
        if "block" not in entry:
            return [entry]
        members = self.blocks[entry["block"]]
        index = members.index(entry)
        return [member for member in members[index:] if not self.done(member)]

    def raw_cutoff(self, entry, days):
        deadlines = []
        elapsed = 0
        for member in self.remaining(entry):
            _, latest = self.shift_window(member, days)
            if latest is not None:
                deadlines.append(latest - elapsed)
            elapsed += member["worst_case_s"]
        return min(deadlines, default=None)

    def date_shift(self, entry, when):
        cutoff = self.raw_cutoff(entry, 0)
        if cutoff is None:
            return 0
        _, latest = self.shift_window(entry, 0)
        anchor = latest if latest is not None else max(
            latest for member in self.remaining(entry)
            if (latest := self.shift_window(member, 0)[1]) is not None)
        return max(0, (self.local(when).date() - self.local(anchor).date()).days)

    def history_for_date(self, day):
        if self.launches is None or self.closes is None:
            return None
        launched = set()
        counts = Counter()
        unknown = set()
        for row, closes in self.history.runs():
            entry = self.by_id.get(row["entry_id"])
            if entry is not None and not kit_matches(row, entry):
                entry = None
            params = entry["params"] if entry is not None else {}
            t0 = row["t0_epoch"]
            if t0 is not None and self.local(t0).date() != day:
                continue
            if t0 is not None:
                launched.add(row["entry_id"])
            facts = (row, *closes)
            kinds = {record["kind"] for record in facts if record.get("kind") is not None}
            if not kinds and entry is not None:
                kinds.add(entry["kind"])
            if kinds and "counted" not in kinds:
                continue
            groups = {record["group"] for record in facts if record.get("group") is not None}
            legs = {record["legs"] for record in facts if "legs" in record}
            group = next(iter(groups), params.get("group")) if len(groups) <= 1 else None
            count = next(iter(legs), params.get("legs")) if len(legs) <= 1 else None
            if kinds != {"counted"} or t0 is None or group is None or not positive_integer(count):
                unknown.add(group)
            else:
                counts[group] += count
        return counts, launched, unknown

    def date_caps(self, entry, day):
        params = entry["params"]
        caps, excludes = params.get("date_caps", []), params.get("not_on_dates_of", [])
        if not caps and not excludes:
            return Check()
        history = self.history_for_date(day)
        if history is None:
            return missing("launches or closes date history")
        counts, _, unknown = history
        relevant_groups = {cap["group"] for cap in caps} | set(excludes)
        if None in unknown or unknown.intersection(relevant_groups):
            return missing("counted date history (kind, t0, group or legs)")
        for cap in caps:
            group = cap["group"]
            added = params["legs"] if params.get("group") == group else 0
            if counts[group] + added > cap["max"]:
                if added > cap["max"]:
                    return fails(f"{group} entry legs exceed its date cap")
                return fails(f"{group} date cap {cap['max']} would be exceeded",
                             local_candidates(day + timedelta(days=1), local_time.min, self.zone)[0])
        for group in excludes:
            if counts[group]:
                return fails(f"{group} already launched on the local date",
                             local_candidates(day + timedelta(days=1), local_time.min, self.zone)[0])
        return Check()

    def window(self, entry, when):
        if entry["kind"] != "counted":
            return Check("date rules apply to named counted entries")
        params = entry["params"]
        shifted = self.date_shift(entry, when)
        earliest, _ = self.shift_window(entry, shifted)
        cutoff = self.raw_cutoff(entry, shifted)
        # Move a missed date, including one on which the remaining block cannot fit.
        if cutoff is not None and when > cutoff:
            shifted += 1
            earliest, _ = self.shift_window(entry, shifted)
            if earliest is None:
                earliest = local_candidates(self.local(when).date() + timedelta(days=1),
                                            local_time.min, self.zone)[0]
            cutoff = self.raw_cutoff(entry, shifted)
        if cutoff is not None and earliest is not None and earliest > cutoff:
            return fails("the block cannot fit on its registered date")
        if earliest is not None and when < earliest:
            return fails("registered window has not opened", earliest)
        check = self.date_caps(entry, self.local(when).date())
        if not check.holds:
            return check
        if params.get("batch_clear"):
            return self.batch(entry, when, self.batches)
        return Check()

    def batch(self, entry, when, params):
        if entry["kind"] != "counted":
            return Check("batch clearance applies to named qualification entries")
        boot = self.facts.get("boot_epoch")
        if boot is None:
            return missing("boot_epoch")
        if params is None:
            return missing("qualification batch rule parameters")
        soak_end = entry["params"].get("soak_end_s")
        if soak_end is None:
            return missing("params.soak_end_s")
        batch = boot + params["offset_s"]
        period = params["period_s"]
        batch += max(0, math.ceil((when - batch) / period)) * period
        if when + soak_end <= batch <= when + entry["expected_s"]:
            return fails("predicted OS batch overlaps the span after soak", batch + params["settle_s"])
        previous = batch if batch == when else batch - period
        if previous >= boot + params["offset_s"] and previous <= when < previous + params["settle_s"]:
            return fails("predicted OS batch clearance has not elapsed", previous + params["settle_s"])
        return Check()

    def is_stability(self, entry):
        return self.ladder is not None and entry["id"].startswith(self.ladder["stability_prefix"])

    def filler_rank(self, entry, when):
        if self.ladder is not None and entry["kind"] == "product_filler":
            if self.is_stability(entry):
                history = self.history_for_date(self.local(when).date())
                if history is not None:
                    _, launched, _ = history
                    if not any(entry_id.startswith(self.ladder["stability_prefix"]) for entry_id in launched):
                        return (0, "")
                return (4, "")
            if entry["id"].startswith(self.ladder["instrument_prefix"]):
                return (1, entry["id"])
            if entry["id"].startswith(self.ladder["high_power_prefix"]):
                return (2, "")
        return (3 if entry["kind"] == "product_filler" else 5, "")

    def priority(self, entry, when, cutoff=None):
        active = 0 if entry.get("block") in self.active_blocks else 1
        kind = KINDS.index(entry["kind"])
        if entry["kind"] == "counted":
            return active, kind, cutoff if cutoff is not None else float("inf"), ""
        if entry["kind"] in FILLERS:
            rank, name = self.filler_rank(entry, when)
            return active, kind, rank, name
        return active, kind, 0, ""

    def predecessor(self, entry):
        if "block" not in entry:
            return Check()
        members = self.blocks[entry["block"]]
        if all(self.closed_clean(member) for member in members[:members.index(entry)]):
            return Check()
        return fails("the preceding span in the block has no clean close")

    def scoped_fault(self, entry, codes):
        rows = self.facts.get("stops")
        if rows is None:
            return missing("stops")
        commit = self.facts.get("queue_commit")
        for row in rows:
            if row["code"] not in codes:
                continue
            scoped = (
                row.get("block") is not None and row.get("block") == entry.get("block")
                or kit_matches(row, entry)
                or row.get("kit_sha256") is not None and row["kit_sha256"] == entry["kit_sha256"]
            )
            if scoped and (row.get("queue_commit") is None or row["queue_commit"] == commit):
                return fails(f"{row['code']} holds this kit or block")
        return Check()

    def launcher(self, entry, when):
        params = entry["params"]
        window = params.get("launch_window_local")
        high_power = self.ladder is not None and entry["id"].startswith(self.ladder["high_power_prefix"])
        if window and not high_power:
            start, end = map(local_time.fromisoformat, window)
            local = self.local(when)
            clock = local.time()
            inside = start <= clock <= end if start <= end else clock >= start or clock <= end
            if not inside:
                today = local.date()
                for day in (today, today + timedelta(days=1)):
                    for stamp in local_candidates(day, start, self.zone):
                        if stamp > when:
                            return fails("outside frozen local launch window", stamp)
        if "plan_argv" in entry:
            if "plans" not in self.facts:
                return Check("SKIPPED: probe did not run plans")
            plans = self.facts["plans"]
            evidence = plans.get(entry["id"]) if isinstance(plans, dict) else None
            if not isinstance(evidence, dict) or evidence.get("signature") != plan_signature(
                    entry, self.facts.get("queue_commit")):
                return missing(f"plans.{entry['id']} (current probe)")
            if evidence.get("rc") != 0 or not integer(evidence.get("rc")):
                return fails(f"probe dry run did not admit {entry['id']}")
        return Check()

    def render_argv(self, entry):
        argv = entry["argv"]
        fields = {name for arg in argv for name in PLACEHOLDERS.findall(arg)}
        if not fields:
            return argv, Check()
        values = {}
        if "deadline_epoch" in fields:
            margin = entry["params"].get("kill_margin_s")
            if margin is None:
                return None, missing("params.kill_margin_s")
            values["deadline_epoch"] = str(math.ceil(self.now + entry["worst_case_s"] + margin))
        if "out" in fields:
            if self.output_root is None:
                return None, missing("launcher-admits.params.output_root")
            values["out"] = str(Path(self.output_root) / f"{entry['id']}-{self.now}")
        if "magistrate_pid" in fields:
            if self.caller_pid is None:
                return None, missing("--caller-pid")
            values["magistrate_pid"] = str(self.caller_pid)
        return [PLACEHOLDERS.sub(lambda match: values[match[1]], arg) for arg in argv], Check()

    def check(self, rule, entry, when):
        test = rule["test"]
        params = entry["params"]
        facts = self.facts
        kind = entry["kind"]
        if test == "pin":
            return Check("pin and kit hash must be admitted", pair(entry) in self.admitted)
        if test == "window":
            return self.window(entry, when)
        if test == "dependency":
            if params.get("after") and self.closes is None:
                return missing("closes")
            for predecessor in params.get("after", []):
                row = self.by_id.get(predecessor)
                clean = self.closed_clean(row) if row is not None else any(
                    c["entry_id"] == predecessor and c["clean"] is True for c in self.bound_closes)
                if not clean:
                    return fails(f"{predecessor} has no clean close")
            if params.get("gates") and facts.get("gates") is None:
                return missing("gates")
            for gate in params.get("gates", []):
                if gate not in facts["gates"]:
                    return fails(f"gate {gate} is not recorded")
        if test == "fits":
            limit = when + entry["worst_case_s"]
            entry_priority = self.priority(entry, when, self.cutoffs.get(entry["id"]))
            for other in self.entries:
                cutoff = self.cutoffs.get(other["id"])
                if cutoff is not None and limit > cutoff and self.priority(other, when, cutoff) < entry_priority:
                    return fails(f"would pass latest feasible start of {other['id']} ({cutoff:g})")
        if test == "launcher_admits":
            check = self.launcher(entry, when)
            if check.holds:
                _, argv_check = self.render_argv(entry)
                if not argv_check.holds:
                    return argv_check
            return check
        if test == "not_refused":
            if facts.get("refusals") is None or facts.get("queue_commit") is None:
                return missing("refusals or queue_commit")
            for refusal in facts["refusals"]:
                if refusal["queue_commit"] != facts["queue_commit"]:
                    continue
                if (refusal["entry_id"] == entry["id"] and
                    ("kit_sha256" not in refusal or kit_matches(refusal, entry))
                    or refusal.get("block") is not None and refusal["block"] == entry.get("block")
                    or refusal.get("kit_sha256") is not None and refusal["kit_sha256"] == entry["kit_sha256"]):
                    return fails("refused at current queue_commit")
            return self.scoped_fault(entry, {"LEG_OVERTIME", "NON_CLEAN_CLOSE", "LAUNCHER_REFUSED"})
        if test == "session_route":
            if kind != "v4_session":
                return Check()
            if facts.get("ready") is None:
                return missing("ready")
            return Check("no effective READY record", any(
                row["entry_id"] == entry["id"] and row["effective"] is True for row in facts["ready"]))
        if test == "batch_clear":
            return self.batch(entry, when, rule["params"])
        if test == "desk_gate":
            return self.scoped_fault(entry, {"DESK_FAILURE", "CONSUMER_GATE"})
        if test == "contaminated_redos" and kind in COUNTED_KINDS:
            if self.closes is None or facts.get("stops") is None:
                return missing("closes or stops")
            events = [row["epoch"] for row in facts["stops"] if row["code"] == "CONTAMINATED_REDOS"]
            events += [row["ended_epoch"] for row in self.bound_closes
                       if row.get("fault") == "CONTAMINATED_REDOS" and row["ended_epoch"] is not None]
            if events and not any(row["ended_epoch"] is not None and row["ended_epoch"] > max(events)
                                  and row["clean"] is True and row.get("load_redos") == 0
                                  and row.get("load_flag") is False for row in self.bound_closes):
                return fails("CONTAMINATED_REDOS awaits a clean span with no load redo or flag")
        if test == "new_pin_smoke" and kind in COUNTED_KINDS and not params.get("pilot"):
            if self.closes is None:
                return missing("closes")
            if not any(row["clean"] is True and row.get("mock") is False
                       and (row.get("pin") or self.by_id.get(row["entry_id"], {}).get("pin")) == entry["pin"]
                       for row in self.bound_closes):
                return fails("no clean native smoke on this pin")
        if test == "f0_retirement" and entry["id"] == "f0-part-c":
            if facts.get("gates") is None:
                return missing("gates")
            if rule["params"]["gate"] in facts["gates"]:
                return fails("R1 post-close Check retires standing F0")
        if test == "ready_outside_block" and kind == "v4_session" and self.active_blocks:
            return fails("a counted block is in progress")
        if test == "hygiene" and kind == "maintenance" and params.get("hygiene_change"):
            gates = facts.get("gates")
            if gates is None:
                return missing("gates")
            rp = rule["params"]
            if rp["start_gate"] in gates and rp["end_gate"] not in gates:
                return fails("qualification hygiene settings are frozen")
        return Check()

    def entry_rules(self, entry):
        rule_ids = set(entry["requires"])
        # Faults apply by scope even when a newly queued entry lacks a redundant reference.
        by_scope = {"not_refused", "desk_gate", "contaminated_redos", "f0_retirement",
                    "hygiene", "fits"}
        if entry["kind"] == "v4_session":
            by_scope.add("session_route")
            if any(any(member["id"].startswith("qual-") or member["params"].get("batch_clear")
                       or any(self.rules[ref]["test"] == "batch_clear" for ref in member["requires"])
                       for member in self.blocks[block]) for block in self.active_blocks):
                by_scope.add("ready_outside_block")
        rule_ids.update(rule["id"] for rule in self.rules.values() if rule["test"] in by_scope)
        return [rule for test in ENTRY_TESTS for rule in self.rules.values()
                if rule["id"] in rule_ids and rule["test"] == test]

    def checks(self, entry, when, omit_fits=False):
        predecessor = self.predecessor(entry)
        if not predecessor.holds:
            rule = self.rules.get("block-dependency")
            if rule is not None and rule["status"] != "RETIRED":
                yield rule, predecessor
        for rule in self.entry_rules(entry):
            status, _ = self.rule_status[rule["id"]]
            if status != "RETIRED" and not (omit_fits and rule["test"] == "fits"):
                yield rule, self.check(rule, entry, when)
        if not omit_fits:
            _, argv_check = self.render_argv(entry)
            if not argv_check.holds and not any(rule["test"] == "launcher_admits" and self.live(rule)
                                                for rule in self.entry_rules(entry)):
                # Missing substitution inputs prevent rendering even if the queue omits the rule.
                yield {"id": "launcher-admits", "class": "PHYSICS"}, argv_check

    def first_failure(self, checks):
        return next(((rule, check) for rule, check in checks
                     if self.rule_status.get(rule["id"], ("LIVE", False))[0] == "LIVE"
                     and not check.holds), None)

    def earliest_entry(self, entry, when, omit_fits):
        """Follow known recheck times until all predicates can hold together."""
        anchors = [self.now]
        if self.batches is not None and self.facts.get("boot_epoch") is not None:
            anchors.append(self.facts["boot_epoch"] + self.batches["offset_s"])
        for member in self.remaining(entry):
            anchors.extend(stamp for stamp in self.shift_window(member, 0) if stamp is not None)
        for launch, _ in self.history.runs():
            if launch["t0_epoch"] is not None:
                anchors.append(launch["t0_epoch"])
        last_anchor = max(anchors)
        seen = set()
        while True:
            checks = list(self.checks(entry, when, omit_fits))
            failures = [(rule, check) for rule, check in checks
                        if self.live(rule) and not check.holds]
            if not failures:
                return when
            if any(check.until is None for _, check in failures):
                return None
            later = max(check.until for _, check in failures)
            if later <= when or not epoch(later):
                return None
            if when > last_anchor and self.local(when).date() > self.local(last_anchor).date():
                # Once dated input events are past, only recurring local clocks
                # and the boot-relative batch phase can change the outcome.
                local = self.local(when)
                phase = when % self.batches["period_s"] if self.batches else 0
                state = (local.month, local.day, local.weekday(), local.time(), local.utcoffset(), phase,
                         tuple((rule["id"], check.until - when) for rule, check in failures))
                if state in seen:
                    return None
                seen.add(state)
            when = later

    def prepare_cutoffs(self, entries):
        for entry in entries:
            if entry["kind"] != "counted" or not any(rule["test"] == "window" and self.live(rule)
                       for rule in self.entry_rules(entry)):
                continue
            if self.raw_cutoff(entry, 0) is None:
                continue
            when = self.earliest_entry(entry, self.now, omit_fits=True)
            if when is not None:
                self.cutoffs[entry["id"]] = self.raw_cutoff(entry, self.date_shift(entry, when))

    def check_row(self, rule, check):
        status, overdue = self.rule_status.get(rule["id"], ("LIVE", False))
        return {"rule": rule["id"], "class": rule["class"], "status": status,
                "overdue": overdue, "holds": check.holds, "detail": check.detail,
                **({"until_epoch": check.until} if check.until is not None else {})}

    def host_decision(self, rule, check):
        owed = self.latest_launch_owed()
        if rule["test"] == "host_quiet" and owed is not None and check.detail == f"{owed} has no matching close":
            return {"decision": "CLOSE_OWED", "entry": owed}
        if check.until is not None:
            return self.wait(rule, check, check.until)
        return {"decision": "HALT", "rule": rule["id"], "detail": check.detail}

    @staticmethod
    def wait(rule, check, until):
        return {"decision": "WAIT", "until_epoch": until, "rule": rule["id"],
                "class": rule["class"], "detail": check.detail}

    def evaluate(self):
        host_checks = [(rule, self.host_check(rule)) for test in HOST_TESTS for rule in self.rules.values()
                       if rule["test"] == test and rule["status"] != "RETIRED"]
        pending = [entry for entry in self.entries if not self.done(entry)]
        self.prepare_cutoffs(pending)
        pending.sort(key=lambda entry: self.priority(entry, self.now, self.cutoffs.get(entry["id"])))
        rows = {}
        eligible = []
        waits = []
        for entry in pending:
            checks = list(self.checks(entry, self.now))
            failure = self.first_failure(checks)
            row = {"id": entry["id"], "kind": entry["kind"], "status": "ELIGIBLE",
                   "checks": [self.check_row(rule, check) for rule, check in checks]}
            if failure:
                rule, check = failure
                row.update(status=rule["id"], rule=rule["id"], **{"class": rule["class"]}, detail=check.detail)
                if check.until is not None:
                    when = self.earliest_entry(entry, self.now, omit_fits=False)
                    if when is not None:
                        waits.append((when, rule, check))
            else:
                eligible.append(entry)
            rows[entry["id"]] = row

        host_failure = self.first_failure(host_checks)
        if host_failure and host_failure[0]["test"] == "host_meter" and any(
                entry["kind"] == "maintenance" for entry in eligible):
            eligible = [entry for entry in eligible if entry["kind"] == "maintenance"]
            host_failure = self.first_failure((rule, check) for rule, check in host_checks
                                              if rule["test"] != "host_meter")
        if host_failure:
            decision = self.host_decision(*host_failure)
        elif eligible:
            best = self.choose(eligible, pending)
            argv, check = self.render_argv(best)
            if check.holds:
                decision = {"decision": "LAUNCH", "entry": best["id"], "worktree": best["worktree"],
                            "argv": argv, "reasons": [
                                f"{check['rule']}: {check['detail']}" for check in rows[best["id"]]["checks"]
                                if check["status"] == "LIVE" and check["holds"]
                            ]}
            else:
                decision = {"decision": "QUEUE_EMPTY", "detail": check.detail}
        elif waits:
            when, rule, check = min(waits, key=lambda row: row[0])
            decision = self.wait(rule, check, when)
        else:
            detail = next((row["detail"] for row in rows.values() if "detail" in row), "no unfinished entries")
            decision = {"decision": "QUEUE_EMPTY", "detail": detail}

        reports = []
        for entry in self.entries:
            reports.append(rows.get(entry["id"], {"id": entry["id"], "kind": entry["kind"],
                                                 "status": "DONE", "checks": []}))
        overdue = [{"rule": key, "review_by": self.rules[key]["review_by"]}
                   for key, (_, flagged) in self.rule_status.items() if flagged]
        advisories = []
        for rule in self.rules.values():
            if rule["test"] == "copy_debt" and self.live(rule):
                age = rule["params"].get("page_age_s")
                for debt in self.facts.get("uncopied") or []:
                    if age is not None and debt["ended_epoch"] is not None and self.now - debt["ended_epoch"] >= age:
                        advisories.append(f"{rule['id']}: {debt['entry_id']} still has copy debt")
        return {"entries": reports, "host": [self.check_row(rule, check) for rule, check in host_checks],
                "overdue": overdue, "advisories": advisories, "decision": decision}

    def choose(self, eligible, pending):
        first = eligible[0]
        if first["kind"] not in FILLERS or first.get("block") in self.active_blocks:
            return first
        ready_by = min((entry["expected_ready_by"] for entry in pending
                        if entry["kind"] in COUNTED_KINDS and entry.get("expected_ready_by", 0) > self.now),
                       default=None)
        if ready_by is None:
            return first
        top_rank = self.filler_rank(first, self.now)[0]
        if top_rank == 0:
            return first
        fillers = [entry for entry in eligible if entry["kind"] in FILLERS]
        fit = [entry for entry in fillers if self.now + entry["expected_s"] <= ready_by]
        if fit:
            return max(fit, key=lambda entry: entry["expected_s"])
        return min(fillers, key=lambda entry: entry["expected_s"])


def explain(report):
    for row in report["entries"]:
        print(f"{row['id']} {row['kind']} {row['status']}", end="")
        if "rule" in row:
            print(f" {row['class']} {row['detail']}", end="")
        print()
        for check in row["checks"]:
            if check["status"] == "FLAG" or check["detail"].startswith("SKIPPED"):
                print(f"  {check['status']} {check['rule']} {check['class']} {check['detail']}")
    for check in report["host"]:
        verdict = "PASS" if check["holds"] else "FAIL"
        print(f"HOST {check['rule']} {check['class']} {check['status']} {verdict} {check['detail']}")
    for row in report["overdue"]:
        print(f"OVERDUE {row['rule']} {row['review_by']}")
    for advisory in report["advisories"]:
        print(advisory)
    print(as_json(report["decision"]))


def ledger_rows(path, errors):
    try:
        with path.open(encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH)
            for index, line in enumerate(stream, 1):
                try:
                    data = parse_json(line)
                    if not isinstance(data, dict):
                        raise ValueError("expected a JSON object")
                except (ValueError, RecursionError) as err:
                    errors.add(path, "BAD_LEDGER_ROW", f"line {index}: {err}")
                    continue
                yield index, data
    except (OSError, ValueError) as err:
        errors.add(path, "READ_LEDGER", str(err))


def missing_observation(observed, ledger):
    """Find the first snapshot observation absent from the ordered ledger."""
    events = iter(ledger)
    for observation in observed or ():
        # Copy verification can have been appended separately since the snapshot.
        known = {key: value for key, value in observation.items()
                 if value is not None and (key != "copy_verified" or value is True)}
        if not any(identity(row) == identity(observation)
                   and all(row.get(key) == value for key, value in known.items())
                   for row in events):
            return observation
    return None


def overlay_ledger(facts, path, errors):
    launches = []
    closes = []
    verified = set()
    refusals = []
    stops = []
    gates = []
    ready = {}
    for index, row in ledger_rows(path, errors):
        where = f"line {index}"
        event = row.get("event")
        payload = {key: value for key, value in row.items() if key not in {"event", "now_epoch"}}
        if event in ("LAUNCH", "CLOSE", "COPY_VERIFIED"):
            required, optional = (CLOSE_FIELDS, CLOSE_OPTIONAL) if event == "CLOSE" else (
                LAUNCH_FIELDS, LAUNCH_OPTIONAL)
            required = {**required, "kit_sha256": KIT}
            if event == "CLOSE":
                required = {key: check for key, check in required.items() if key != "restore_proven"}
                optional = {**optional, "restore_readbacks": IS_OBJECT,
                            "restore_proven": nullable(boolean)}
            if errors.fields(path, where, payload, required, optional):
                payload["ledger_index"] = index
                if event == "LAUNCH":
                    launches.append(payload)
                elif event == "CLOSE":
                    readbacks = payload.pop("restore_readbacks", {})
                    if readbacks:
                        errors.fields(path, f"{where}.restore_readbacks", readbacks, {},
                                      {key: nullable(boolean) for key in RESTORE_READBACKS})
                    evidence = [readbacks.get(key) for key in RESTORE_READBACKS]
                    proof = (False if any(v is False for v in evidence)
                             else True if all(v is True for v in evidence) else None)
                    # An explicit failure binds even when other readbacks are present.
                    payload["restore_proven"] = False if payload.get("restore_proven") is False else proof
                    if payload.get("stranded"):
                        payload["clean"] = False
                    closes.append(payload)
                else:
                    verified.add(identity(payload))
        elif event == "GATE":
            if errors.fields(path, where, payload, {"id": identifier}):
                gates.append(payload["id"])
        elif event in ("REFUSAL", "STOP", "READY"):
            key = {"REFUSAL": "refusals", "STOP": "stops", "READY": "ready"}[event]
            if errors.fields(path, where, payload, *FACT_ROWS[key]):
                if event == "REFUSAL":
                    refusals.append(payload)
                elif event == "STOP":
                    stops.append(payload)
                else:
                    ready[payload["entry_id"]] = payload
        elif event is not None:
            errors.add(path, "BAD_LEDGER_EVENT", f"{where}: unrecognized event")
        elif not (isinstance(row.get("decision"), str) and row["decision"] in DECISIONS):
            errors.add(path, "BAD_LEDGER_ROW", f"{where}: expected event or decision")
    for close in closes:
        if identity(close) in verified:
            close["copy_verified"] = True
    uncopied = [
        {key: close[key] for key in ("entry_id", "kind", "ended_epoch", "kit_sha256") if key in close}
        for close in closes if close.get("copy_verified") is not True
    ]
    closes.reverse()
    observations = dict(facts.get("errors") or {})
    for key, parsed in (("launches", launches), ("closes", closes)):
        omitted = missing_observation(facts.get(key), parsed)
        if omitted is not None:
            label = "launch" if key == "launches" else "close"
            observations["attempt_history"] = (
                f"supplied ledger omits or contradicts the observed {label} for {attempt_name(omitted)}")
            facts["errors"] = observations
            return
    observations.pop("attempt_history", None)
    if observations or "errors" in facts:
        facts["errors"] = observations
    facts.update(launches=launches, closes=closes, uncopied=uncopied, refusals=refusals,
                 gates=gates, ready=list(ready.values()), stops=stops)


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


def run_plans(queue, facts, errors):
    plans = {}
    for entry in queue["entries"]:
        if "plan_argv" not in entry or entry.get("done"):
            continue
        signature = plan_signature(entry, facts.get("queue_commit"))
        rc = None
        try:
            child = subprocess.run(entry["plan_argv"], cwd=entry["worktree"], check=False,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            rc = child.returncode
            if rc:
                errors[f"plans.{entry['id']}"] = f"dry run exited {rc}"
        except (OSError, ValueError, subprocess.TimeoutExpired) as err:
            errors[f"plans.{entry['id']}"] = f"dry run failed: {type(err).__name__}"
        plans[entry["id"]] = {"signature": signature, "rc": rc}
    return plans


def maintenance_active(args, rules, errors):
    paths = []
    for row in rules.values():
        marker = row.get("params", {}).get("maintenance_marker")
        if row["test"] == "owner_stop" and row["status"] != "RETIRED" and marker:
            paths.append(Path(marker))
    if args.maintenance_marker is not None:
        paths.append(args.maintenance_marker)
    active = False
    for path in dict.fromkeys(paths):
        try:
            path.lstat()
            active = True
        except FileNotFoundError:
            continue
        except OSError as err:
            errors["maintenance_active"] = str(err)
    if not active and "maintenance_active" in errors:
        return None
    return active


def probe(args, queue, rules, supplied):
    failures = {}
    supplied_errors = supplied.get("errors") or {}
    if "attempt_history" in supplied_errors:
        failures["attempt_history"] = supplied_errors["attempt_history"]
    power = probe_command("/usr/bin/pmset -g batt", parse_power, "power", failures)
    disk = probe_command("/bin/df -g /", parse_disk, "disk_free_gib", failures)
    labels = probe_command("/bin/launchctl list", parse_labels, "labels_loaded", failures)
    processes = probe_command("/bin/ps -axo pid,ppid,comm", parse_processes,
                              "foreign_processes", failures)
    boot = probe_command("/usr/sbin/sysctl -n kern.boottime", parse_boot, "boot_epoch", failures)
    now = time.time()
    quiet_rules = [row for row in rules.values() if row["test"] == "host_quiet" and row["status"] != "RETIRED"]
    foreign = None
    if processes is not None:
        patterns = [re.compile(pattern) for row in quiet_rules for pattern in row["params"]["patterns"]]
        root = args.caller_pid or os.getppid()
        if root not in processes:
            failures["foreign_processes"] = "caller pid is absent from the process census"
        else:
            excluded = process_tree(processes, root)
            foreign = [{"pid": pid, "name": name} for pid, (_, name) in sorted(processes.items())
                       if pid not in excluded and any(pattern.search(name) for pattern in patterns)]
    fence = None
    if args.custody is not None:
        try:
            raw_fence = read_regular_json(args.custody / "desk_fence.json")
            pid = raw_fence.get("pid")
            fence = {"purpose": raw_fence.get("purpose") if string(raw_fence.get("purpose")) else None,
                     "pid": pid if integer(pid) and pid else None,
                     "deadline": raw_fence.get("deadline") if epoch(raw_fence.get("deadline")) else None,
                     "pid_alive": pid in processes if processes is not None and integer(pid) and pid else None}
        except FileNotFoundError:
            if not args.custody.is_dir():
                failures["fence"] = "fence directory unavailable"
        except (OSError, ValueError, RecursionError) as err:
            failures["fence"] = str(err)
    else:
        if "fence" in supplied_errors:
            failures["fence"] = "the supplied fence fact is unreadable"
        elif "fence" in supplied:
            fence = supplied["fence"]
        else:
            failures["fence"] = "fence fact not supplied"
    maintenance = maintenance_active(args, rules, failures)
    receipts = []
    for root in args.receipt_root:
        try:
            for directory, name in receipt_files(root):
                try:
                    receipts.append(project_receipt(read_regular_json(name, dir_fd=directory)))
                except (OSError, ValueError, RecursionError) as err:
                    failures[f"receipts.{len(receipts)}"] = f"receipt unreadable: {type(err).__name__}"
                    receipts.append(None)
        except (OSError, ValueError) as err:
            failures[f"receipt_root.{root.name}"] = str(err)
    facts = dict.fromkeys(FACT_TYPES)
    facts.update({key: supplied[key] for key in FACT_TYPES if key in supplied})
    facts.update(now_epoch=now, boot_epoch=boot, power=power, disk_free_gib=disk, labels_loaded=labels,
                 foreign_processes=foreign, fence=fence,
                 receipts=receipts if args.receipt_root else None, maintenance_active=maintenance,
                 errors=failures)
    if facts["closes"]:
        history = AttemptHistory(facts)
        for close in facts["closes"]:
            if not history.receipt_matches(close):
                close["clean"] = None
                if close["restore_proven"] is True:
                    close["restore_proven"] = None
    if args.queue_commit is not None:
        facts["queue_commit"] = args.queue_commit
    if args.run_plans:
        facts["plans"] = run_plans(queue, facts, failures)
    else:
        facts.pop("plans", None)
    # Missing optional sources stay null. Command/file failures are reported separately.
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
        if name in ("explain", "next"):
            command.add_argument("--facts", required=True, type=Path)
            command.add_argument("--now", type=parse_epoch)
            command.add_argument("--caller-pid", type=positive_pid)
            command.add_argument("--ledger", type=Path, help="append-only structural launch and close events")
        if name == "explain":
            command.add_argument("--json", action="store_true")
        elif name == "next":
            command.add_argument("--record", type=Path, help="append a decision observation to this ledger")
        elif name == "probe":
            command.add_argument("--out", type=Path, required=True)
            command.add_argument("--custody", type=Path, help="directory containing desk_fence.json")
            command.add_argument("--receipt-root", type=Path, action="append", default=[])
            command.add_argument("--self-pid", "--caller-pid", type=positive_pid, dest="caller_pid")
            command.add_argument("--host-facts", type=Path, help="additional structural facts from the caller")
            command.add_argument("--ledger", type=Path, help="append-only structural launch and close events")
            command.add_argument("--queue-commit")
            command.add_argument("--maintenance-marker", type=Path, help="additional stop marker to check")
            command.add_argument("--run-plans", action="store_true")
    command = commands.add_parser("report")
    command.add_argument("--ledger", type=Path, required=True)
    command.add_argument("--since", required=True)
    return parser


def main(argv=None):
    args = create_parser().parse_args(argv)
    errors = Errors()
    if args.command == "report":
        try:
            since = parse_since(args.since)
        except (ValueError, OverflowError) as err:
            errors.add(args.ledger, "BAD_SINCE", str(err))
        else:
            report_ledger(args.ledger, since, errors)
        return errors.finish()
    source = errors.read_json(args.rules)
    if source is None and not errors.items:
        errors.add(args.rules, "BAD_VALUE", "rules must be an array")
    rules = validate_rules(args.rules, source, errors)
    reference_rules = rules if not isinstance(source, list) else {
        row["id"]: row for row in source if isinstance(row, dict)
        and identifier(row.get("id")) and RULE_NAME(row.get("test"))
        and one_of("LIVE", "FLAG", "RETIRED")(row.get("status"))
    }
    queue = errors.read_json(args.queue)
    if queue is None and not any(error.startswith(f"{args.queue}:") for error in errors.items):
        errors.add(args.queue, "BAD_VALUE", "queue must be an object")
    validate_queue(args.queue, queue, reference_rules, errors, isinstance(source, list))
    if args.command == "validate":
        return errors.finish()
    if args.command == "probe":
        supplied = {}
        if args.host_facts is not None:
            supplied = errors.read_json(args.host_facts)
            if supplied is None and not any(error.startswith(f"{args.host_facts}:") for error in errors.items):
                errors.add(args.host_facts, "BAD_VALUE", "facts must be an object")
            validate_facts(args.host_facts, supplied, errors, 0)
        if args.ledger is not None and isinstance(supplied, dict):
            overlay_ledger(supplied, args.ledger, errors)
        if args.queue_commit is not None and not string(args.queue_commit):
            errors.add(args.out, "BAD_VALUE", "--queue-commit must be a nonempty string")
        if errors.items:
            return errors.finish()
        facts, failures = probe(args, queue, rules, supplied)
        try:
            write_facts(args.out, facts)
        except (OSError, ValueError) as err:
            errors.add(args.out, "WRITE_FACTS", str(err))
            return errors.finish()
        # An omitted fence source stays unknown without making a host command fail.
        return 3 if any(key != "fence" or args.custody is not None for key in failures) else 0
    facts = errors.read_json(args.facts)
    if facts is None and not any(error.startswith(f"{args.facts}:") for error in errors.items):
        errors.add(args.facts, "BAD_VALUE", "facts must be an object")
    validate_facts(args.facts, facts, errors, args.now)
    if args.ledger is not None and isinstance(facts, dict):
        overlay_ledger(facts, args.ledger, errors)
    if errors.items:
        return errors.finish()
    now = args.now if args.now is not None else facts["now_epoch"]
    results = Scheduler(queue, rules, facts, now, args.caller_pid).evaluate()
    if args.command == "explain":
        if args.json:
            print(as_json(results))
        else:
            explain(results)
    else:
        decision = results["decision"]
        if args.record is not None:
            try:
                append_decision(args.record, decision, now)
            except (OSError, ValueError) as err:
                errors.add(args.record, "APPEND_LEDGER", str(err))
                return errors.finish()
        print(as_json(decision))
    return 0


if __name__ == "__main__":
    sys.exit(main())
