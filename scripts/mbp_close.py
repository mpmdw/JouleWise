#!/usr/bin/env python3
"""Close a finished MBP attempt from structural evidence and manage its copy child.

The launch producer retains desk_fence.json through close and tick, with pid,
pgid, and the scheduler attempt key: entry_id, kit_sha256, t0_epoch and span_id
when present. A standalone close also binds its canonical OUT to fence.out.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import ctypes
from datetime import datetime
import fcntl
import json
import math
import os
from pathlib import Path
import re
import select
import shlex
import stat
import subprocess
import sys
import tempfile
import time
import uuid

if __package__:
    from . import mbp_sched as sched
else:
    import mbp_sched as sched


SCHEMA = "joulewise.mbp_close.v1"
RECEIPT = "runner_receipt.json"
HIGH_POWER_MARKER = Path("/Users/Shared/JouleWise/host-power/high-power.marker")
MAINTENANCE_PROCESSES = (
    "dasd", "XProtect", "XProtectPluginService", "mds", "mdworker", "backupd",
    "softwareupdated", "mobileassetd", "bird", "cloudd", "fileproviderd",
)
CLOSE_ERRORS = (OSError, ValueError, RecursionError)
TIMEOUT = 15
COPY_POLL_S = 0.25
COPY_STOP_S = 60


class Refused(ValueError):
    pass


def read_optional(path):
    try:
        return sched.read_regular_json(path)
    except FileNotFoundError:
        return None


def obj(value):
    return value if isinstance(value, dict) else {}


def field(row, key, check):
    value = row.get(key)
    return value if check(value) else None


def text(value):
    return isinstance(value, str) and (value == "" or value.isprintable())


def positive_pid(value):
    return type(value) is int and value > 1


def type_int(value):
    return type(value) is int


def string_array(value):
    return isinstance(value, list) and all(text(item) for item in value)


def project_receipt(raw):
    kit = obj(raw.get("kit"))
    span = obj(raw.get("span_result"))
    steps = raw.get("steps", span.get("steps"))
    feeds = raw.get("feeds")
    receipt = {
        "entry_id": field(raw, "entry_id", sched.identifier),
        "kit_sha256": field(raw, "kit_sha256", sched.hexadecimal(64)) or
        field(kit, "sha256", sched.hexadecimal(64)),
        "campaign_id": field(raw, "campaign_id", sched.identifier) or
        field(kit, "campaign_id", sched.identifier),
        "frozen_commit": field(raw, "frozen_commit", sched.hexadecimal(40)) or
        field(kit, "frozen_commit", sched.hexadecimal(40)),
        "runner_kind": field(raw, "runner_kind", sched.identifier),
        "rc": field(raw, "rc", type_int),
        "error": field(raw, "error", text),
        "mock": field(raw, "mock", sched.boolean),
        "roster": field(raw, "roster", sched.array(sched.identifier)),
        "legs_planned": field(raw, "legs_planned", sched.integer),
        "legs_finished": field(raw, "legs_finished", sched.integer),
        "started": {"epoch_s": field(obj(raw.get("started")), "epoch_s", sched.epoch)},
        "ended": {"epoch_s": field(obj(raw.get("ended")), "epoch_s", sched.epoch)},
        "span_result": {key: field(span, key, check) for key, check in (
            ("outcome", sched.identifier), ("chain_outcome", sched.identifier),
            ("fault", lambda value: isinstance(value, bool) or sched.identifier(value)),
        )},
        "batch_windows": field(raw, "batch_windows", string_array),
        "steps": [
            {"name": field(obj(step), "name", sched.identifier), "rc": field(obj(step), "rc", type_int)}
            for step in steps
        ] if isinstance(steps, list) else None,
        "feeds": {
            name: {"stop": {"proven_stopped": field(obj(obj(feed).get("stop")),
                                                   "proven_stopped", sched.boolean)}}
            for name, feed in feeds.items() if sched.identifier(name)
        } if isinstance(feeds, dict) and all(sched.identifier(name) for name in feeds) else None,
    }
    if "span_id" in raw:
        receipt["span_id"] = field(raw, "span_id", sched.identifier)
    return receipt


LEG_FIELDS = {
    "leg_id": sched.identifier, "attempts": sched.integer, "admitted": sched.boolean,
    "leg_status": sched.identifier, "g0_role": sched.identifier, "g0_outcome": sched.identifier,
    "g0_s": sched.number, "wall_s": sched.number, "budget_s": sched.number,
    "contaminated_redos": sched.integer, "os_level_max": sched.integer, "pm_nominal": sched.boolean,
    "prefill_tokens": sched.integer, "decode_tokens": sched.integer,
}


def project_leg(raw):
    reference = raw.get("span_reference")
    leg = {key: field(raw, key, check) for key, check in LEG_FIELDS.items()}
    leg["span_reference"] = {
        key: field(reference, key, check) for key, check in (
            ("leg_id", sched.identifier), ("attempt", sched.integer),
            ("redone", sched.boolean), ("excluded", sched.boolean),
        )
    } if isinstance(reference, dict) else None
    return leg


@contextmanager
def directory(path, *, dir_fd=None):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dir_fd)
    try:
        yield fd
    finally:
        os.close(fd)


def leg_table(out):
    legs = []
    try:
        with directory(out) as root, directory("desk-bundle", dir_fd=root) as bundle, directory(
            "legs", dir_fd=bundle
        ) as parent, os.scandir(parent) as entries:
            for item in sorted(entries, key=lambda row: row.name):
                if not item.is_dir(follow_symlinks=False) or not sched.identifier(item.name):
                    continue
                with directory(item.name, dir_fd=parent) as leg:
                    try:
                        raw = sched.read_regular_json("leg_summary.json", dir_fd=leg)
                    except FileNotFoundError:
                        continue
                    legs.append(project_leg(raw))
    except FileNotFoundError:
        pass
    return legs


def consumer_rows(legs):
    return [
        {"leg_id": row["leg_id"], "released": row["g0_outcome"] == "released",
         "span_reference": row["span_reference"]}
        for row in legs if row["g0_role"] == "consume"
    ]


def probe(argv, parse, *, timeout=TIMEOUT, no_match=False):
    try:
        command = subprocess.run(argv, capture_output=True, text=True, timeout=timeout,
                                 env={**os.environ, "LC_ALL": "C"})
        if no_match and command.returncode == 1 and not command.stdout and not command.stderr:
            return []
        return parse(command.stdout) if command.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def power_mode(output):
    modes = re.findall(r"^\s*powermode\s+(\d+)\s*$", output, flags=re.MULTILINE)
    return int(modes[0]) if len(modes) == 1 else None


def network_time(output):
    match = re.fullmatch(r"Network Time: (On|Off)", output.strip())
    return match[1] if match else None


def pids(output):
    values = [int(line) for line in output.splitlines()]
    return values if all(positive_pid(pid) for pid in values) else None


def groups(output):
    live = {}
    for line in output.splitlines():
        pid, pgid, state = line.split()
        if not state.startswith("Z"):
            live[int(pid)] = int(pgid)
    if not live:
        raise ValueError("process census is empty")
    return live


def require_idle_group(custody, attempt=None, *, name=None, out=None):
    """Use the attempt's retained fence and a census of live PID/PGID pairs."""
    try:
        fence = read_optional(custody / "desk_fence.json")
    except CLOSE_ERRORS as exc:
        raise Refused("desk fence is unreadable") from exc
    if attempt is None and name is None:
        if fence is None:
            return None
        raise Refused("retained desk fence has no launch history")
    if fence is None or not positive_pid(fence.get("pid")) or not positive_pid(fence.get("pgid")):
        raise Refused("retained desk fence has no authoritative PGID")
    key = attempt_key(fence)
    if key is None or (attempt is not None and key != attempt_key(attempt)):
        raise Refused("retained desk fence does not identify the attempt")
    if name is not None and (name not in (fence["entry_id"], fence.get("span_id")) or fence.get("out") != str(out)):
        raise Refused("standalone close does not match the retained fence's entry and OUT")
    live = probe(["/bin/ps", "-axo", "pid=,pgid=,stat="], groups)
    if live is None:
        raise Refused("process group census unavailable")
    if fence["pid"] in live or fence["pgid"] in live.values():
        raise Refused("desk fence owner or process group is alive")
    return fence


def marker_present(path):
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return None


class DarwinTimex(ctypes.Structure):
    # Darwin sys/timex.h. A zero modes word makes ntp_adjtime read-only.
    _fields_ = [
        ("modes", ctypes.c_uint), ("offset", ctypes.c_long), ("freq", ctypes.c_long),
        ("maxerror", ctypes.c_long), ("esterror", ctypes.c_long), ("status", ctypes.c_int),
        ("constant", ctypes.c_long), ("precision", ctypes.c_long), ("tolerance", ctypes.c_long),
        ("ppsfreq", ctypes.c_long), ("jitter", ctypes.c_long), ("shift", ctypes.c_int),
        ("stabil", ctypes.c_long), ("jitcnt", ctypes.c_long), ("calcnt", ctypes.c_long),
        ("errcnt", ctypes.c_long), ("stbcnt", ctypes.c_long),
    ]


def frequency_word():
    if sys.platform != "darwin" or ctypes.sizeof(ctypes.c_long) != 8:
        return None
    try:
        query = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True).ntp_adjtime
        query.argtypes = [ctypes.POINTER(DarwinTimex)]
        query.restype = ctypes.c_int
        value = DarwinTimex()
        status = query(ctypes.byref(value))
    except (OSError, AttributeError):
        return None
    return value.freq if 0 <= status <= 5 else None


def readback(receipt, marker, custody, attempt, pgid):
    errors = {}
    mode = sched.probe_command("/usr/bin/pmset -g", power_mode, "power_mode", errors)
    battery = sched.probe_command("/usr/bin/pmset -g batt", sched.parse_power, "power", errors)
    ntp = sched.probe_command("/usr/sbin/systemsetup -getusingnetworktime", network_time,
                              "network_time", errors)
    labels = sched.probe_command("/bin/launchctl list", sched.parse_labels, "labels_loaded", errors)
    if labels is not None:
        labels = [name for name in labels if name.startswith("com.joulewise.")]
    present = marker_present(marker)
    monitors = {
        "km003c_monitor.py": probe(["/usr/bin/pgrep", "-f", r"(^|[ /])km003c_monitor\.py( |$)"],
                                  pids, no_match=True),
        "hazard_monitor.py": probe(["/usr/bin/pgrep", "-f", r"(^|[ /])hazard_monitor\.py( |$)"],
                                  pids, no_match=True),
        "powermetrics": probe(["/usr/bin/pgrep", "-u", "0", "-x", "powermetrics"], pids, no_match=True),
    }
    frequency = frequency_word()
    host = {"power_mode": mode, "power": battery, "network_time": ntp, "labels_loaded": labels,
            "high_power_marker": present, "monitors": monitors, "frequency_word": frequency}
    feed_rows = obj(receipt).get("feeds")
    feeds = None if feed_rows is None else all(
        feed["stop"]["proven_stopped"] is True for feed in feed_rows.values()
    )
    steps = obj(receipt).get("steps")
    restore_steps = None if steps is None else (
        any(step["name"] == "restore" for step in steps)
        and all(step["name"] is not None and (step["rc"] == 0 or not (
            step["name"] == "restore" or step["name"].startswith(("stop-", "close-"))
        )) for step in steps)
    )
    current_fence = require_idle_group(custody, attempt)
    if current_fence["pgid"] != pgid:
        raise Refused("retained PGID changed during close")
    checks = {
        "power_mode": None if mode is None else mode == 0,
        "network_time_off": None if ntp is None else ntp == "Off",
        "frequency_word_zero": None if frequency is None else frequency == 0,
        "no_monitor": None if any(value is None for value in monitors.values()) else not any(monitors.values()),
        "no_high_power_marker": None if present is None else not present,
        "feeds_stopped": feeds,
        "process_group_gone": True,
    }
    native_ok = battery is not None and labels is not None and all(
        value is True for key, value in checks.items() if key != "feeds_stopped"
    )
    return host, checks, restore_steps, native_ok


def local_time(value):
    return datetime.fromtimestamp(value).astimezone().isoformat(timespec="milliseconds") if value is not None else "unknown"


def create_once(path, content):
    """Publish complete bytes without replacing a preexisting record."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False,
                                         mode="w", encoding="utf-8") as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError:
            return False
        with directory(path.parent) as parent:
            os.fsync(parent)
        return True
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def json_line(value):
    return sched.as_json(value) + "\n"


@contextmanager
def lock(path):
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("expected a regular lock file")
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield fd
    finally:
        os.close(fd)


def maintenance_table(path, started, ended):
    if started is None or ended is None or ended < started:
        return {"status": "unobserved"}
    predicate = " OR ".join(f'process == "{name}"' for name in MAINTENANCE_PROCESSES)
    bounds = [datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
              for value in (math.floor(started), math.ceil(ended))]
    if not path.is_file():
        output = probe(["/usr/bin/log", "show", "--start", bounds[0], "--end", bounds[1],
                        "--predicate", predicate], str, timeout=300)
        if output is None:
            return {"status": "unobserved"}
        create_once(path, output)
    # On retry after a crash before link, use the same immutable log.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, encoding="utf-8") as stream:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("maintenance log must be a regular file")
        output = stream.read()
    bins = {}
    pattern = re.compile(
        r"^(\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d(?:\.\d+)?(?:[+-]\d{4})?)\s+"
        r"(?:\S+\s+){5}([\w]+)(?:\[[\d]+\])?:"
    )
    for line in output.splitlines():
        match = pattern.match(line)
        if match and match[2] in MAINTENANCE_PROCESSES:
            stamp = datetime.fromisoformat(match[1]).timestamp()
            if started <= stamp <= ended:
                index = int((stamp - started) // 600)
                bins.setdefault(str(index), dict.fromkeys(MAINTENANCE_PROCESSES, 0))[match[2]] += 1
    return {"status": "observed", "bins": bins}


def verdict(receipt, legs, consumers):
    overtime = sum(row["wall_s"] is not None and row["budget_s"] is not None
                   and row["wall_s"] > 1.5 * row["budget_s"] for row in legs)
    redos = sum(row["contaminated_redos"] or 0 for row in legs)
    if receipt is None:
        return ["STRANDED"], overtime, redos
    span = receipt["span_result"]
    roster = receipt["roster"]
    feeds = receipt["feeds"]
    problems = {
        "RUNNER_RC": receipt["rc"] != 0,
        "RUNNER_ERROR": bool(receipt["error"]),
        "MOCK": receipt["mock"] is True,
        "ROSTER_INCOMPLETE": roster is None or not (
            receipt["legs_finished"] == receipt["legs_planned"] == len(roster)
        ),
        "SPAN_OUTCOME": span["outcome"] != "MEASURED_OK",
        "CHAIN_OUTCOME": span["chain_outcome"] != "COMPLETE",
        "SPAN_FAULT": span["fault"] is not False,
        "FEEDS_NOT_STOPPED": feeds is None or any(
            feed["stop"]["proven_stopped"] is not True for feed in feeds.values()
        ),
        "LEG_OVERTIME": overtime >= 2,
        "CONTAMINATED_REDOS": redos >= 3,
        "CONSUMER_NOT_RELEASED": any(not row["released"] for row in consumers),
    }
    return [code for code, present in problems.items() if present], overtime, redos


def attempt_name(row):
    return row.get("span_id", row["entry_id"])


def attempt_key(row):
    started = row.get("t0_epoch")
    if not sched.identifier(row.get("entry_id")) or not sched.epoch(started):
        return None
    if "span_id" in row:
        if not sched.identifier(row["span_id"]) or not sched.KIT(row.get("kit_sha256")):
            return None
    elif not sched.hexadecimal(64)(row.get("kit_sha256")):
        return None
    return row["entry_id"], row.get("span_id"), row.get("kit_sha256"), started


def receipt_key(receipt):
    return attempt_key({**receipt, "t0_epoch": receipt["started"]["epoch_s"]})


def matching_receipt(receipt, launch):
    if receipt is None or receipt["mock"] is not False:
        return False
    key = receipt_key(receipt)
    ended = receipt["ended"]["epoch_s"]
    return key is not None and key == attempt_key(launch) and ended is not None and ended >= key[-1]


def scoped_stops(problems, entry, kit, block, queue_commit, when):
    scope = {"entry_id": entry}
    for key, value in (("kit_sha256", kit), ("block", block), ("queue_commit", queue_commit)):
        if value is not None:
            scope[key] = value
    stops = []
    if "CONTAMINATED_REDOS" in problems:
        stops.append({"code": "CONTAMINATED_REDOS", "epoch": when})
    for code, holds in (("LEG_OVERTIME", "LEG_OVERTIME" in problems),
                        ("NON_CLEAN_CLOSE", bool(problems)),
                        ("CONSUMER_GATE", "CONSUMER_NOT_RELEASED" in problems)):
        if holds:
            stops.append({"code": code, "epoch": when, **scope})
    return stops


def summary(record):
    consumers = []
    for row in record["consumers"]:
        reference = row["span_reference"]
        source = "unknown"
        if reference:
            source = f"{reference['leg_id']} attempt {reference['attempt']}"
            if reference["redone"]:
                source += " redone"
            if reference["excluded"]:
                source += " excluded"
        consumers.append(f"{row['leg_id']} {'released' if row['released'] else 'unreleased'} ({source})")
    problems = ", ".join(record["problems"]) or "none"
    copy = record["copy"]
    span = f" (span {record['span_id']})" if "span_id" in record else ""
    return "\n".join([
        f"Entry {record['entry_id']}{span}",
        f"Started {local_time(record['t0_epoch'])}",
        f"Ended {local_time(record['ended_epoch'])}",
        f"Legs run {record['legs']}",
        f"Legs admitted {record['legs_admitted']}",
        f"Contaminated redos {record['load_redos']}",
        "Consumers " + ("; ".join(consumers) or "none"),
        f"Restore proven {'yes' if record['restore_proven'] else 'no'}",
        f"Clean {'yes' if record['clean'] else 'no'}",
        f"Problems {problems}",
        f"Copy {copy['status']}" + (f" (pid {copy['pid']})" if copy["pid"] is not None else ""),
    ]) + "\n"


def post_argv(entry, body):
    return [sys.executable, str(Path(__file__).with_name("run_state_add.py")), "add",
            "--heading", f"MBP close {entry}", "--body", str(body), "--status", "CLOSED",
            "--owner", "magistrate"]


def managed_directory(path, out=None):
    if out is not None and path.resolve().is_relative_to(out):
        raise ValueError("close records and copy controls must be outside OUT")
    if path.is_symlink():
        raise ValueError("managed directory must not be a symlink")
    path.mkdir(exist_ok=True)
    return path


def make_close(args, *, launch=None, receipt=None, snapshot=None):
    out = args.out.resolve(strict=True)
    custody = args.custody.resolve(strict=True)
    if custody.is_relative_to(out):
        raise ValueError("custody must be outside OUT")
    if launch is None:
        fence = require_idle_group(custody, name=args.entry, out=out)
    else:
        fence = require_idle_group(custody, launch)
    pgid = fence["pgid"]
    if receipt is None:
        with directory(out) as parent:
            try:
                receipt = project_receipt(sched.read_regular_json(RECEIPT, dir_fd=parent))
            except FileNotFoundError:
                pass
    if launch is not None and not matching_receipt(receipt, launch):
        raise Refused(f"{args.entry}: newest attempt has no matching receipt")
    if receipt is not None and receipt_key(receipt) != attempt_key(fence):
        raise Refused(f"{args.entry}: receipt does not identify the retained attempt")
    entry_id = fence["entry_id"]
    span_id = fence.get("span_id")
    if args.entry not in (entry_id, span_id):
        raise Refused(f"{args.entry}: receipt names a different entry or span")

    attempt_name = span_id or entry_id
    parent = managed_directory(managed_directory(custody / "closes", out) / attempt_name, out)
    target = parent / "close.json"
    with lock(parent / ".lock"):
        existing = read_optional(target)
        if existing is not None:
            if existing.get("schema") != SCHEMA or existing.get("entry_id") != entry_id:
                raise Refused(f"{args.entry}: close.json is not an MBP close record for this entry")
            if attempt_key(existing) != attempt_key(fence) or existing.get("pgid") != pgid:
                raise Refused(f"{args.entry}: close.json has a different attempt or PGID")
            if not (parent / "summary.txt").is_file():
                create_once(parent / "summary.txt", summary(existing))
            return existing, False, 0

        started = fence["t0_epoch"]
        ended = obj(receipt).get("ended", {}).get("epoch_s")
        kit = fence.get("kit_sha256")
        attempt = {
            "entry_id": entry_id, "kit_sha256": kit, "t0_epoch": started,
            **({"open_seq": launch["seq"]} if launch is not None else {}),
            **({"span_id": span_id} if span_id is not None else {}),
        }
        host, readbacks, steps_ok, native_ok = readback(receipt, args.high_power_marker, custody, attempt, pgid)
        proven = (native_ok and steps_ok is True and readbacks["feeds_stopped"] is True
                  and matching_receipt(receipt, attempt))
        legs = leg_table(out) if receipt is not None else []
        consumers = consumer_rows(legs)
        maintenance = maintenance_table(parent / "maintenance-log.txt", started, ended)
        problems, overtime, redos = verdict(receipt, legs, consumers)
        clean = not problems
        stops = scoped_stops(problems, entry_id, kit, obj(launch).get("block"), obj(launch).get("queue_commit"),
                             ended if ended is not None else time.time())
        if require_idle_group(custody, attempt)["pgid"] != pgid:
            raise Refused("retained PGID changed during close")
        record = {
            "schema": SCHEMA, **attempt, "kind": obj(launch).get("kind"),
            "ended_epoch": ended, "out": str(out), "pgid": pgid,
            "pin": obj(receipt).get("frozen_commit"), "mock": obj(receipt).get("mock"),
            "receipt": receipt, "stranded": receipt is None, "host": host,
            "restore_readbacks": readbacks, "restore_steps_passed": steps_ok, "restore_proven": proven,
            "leg_table": legs, "legs": len(legs), "legs_admitted": sum(row["admitted"] is True for row in legs),
            "overtime_legs": overtime, "load_redos": redos,
            "load_flag": bool(redos) if legs and all(row["contaminated_redos"] is not None for row in legs) else None,
            "consumers": consumers, "maintenance": maintenance, "clean": clean,
            "problems": problems + (["RESTORE_UNPROVEN"] if receipt is not None and not proven else []),
            "stops": stops, "copy": {"pid": None, "status": "not started"},
        }
        if not args.no_copy and args.copy_config is not None:
            config = copy_config(args.copy_config, out, attempt_name, custody)
            copy = record["copy"]
            copy["config"] = config
            if snapshot is not None:
                head, history = snapshot
                pending = stage_observations(history, launch, close_events(record, launch))
                attempt["copy_start_seq"] = head["last_seq"] + len(pending) + 1
            try:
                copy["pid"] = start_copy(custody, out, attempt_name, config, attempt)
                copy["status"] = "started"
                if "copy_start_seq" in attempt:
                    copy["start_seq"] = attempt["copy_start_seq"]
            except (OSError, ValueError, subprocess.SubprocessError):
                copy["status"] = "start failed"
        body = parent / "summary.txt"
        create_once(target, json_line(record))
        create_once(body, summary(record))
        status = 0 if proven or (receipt is None and native_ok) else 5
        return record, True, status


def copy_config(path, out, entry, custody):
    if path.resolve().is_relative_to(out):
        raise ValueError("copy config must be outside OUT")
    raw = sched.read_regular_json(path)
    argv = raw.get("argv")
    if not (isinstance(argv, list) and argv and sched.string(argv[0])
            and all(isinstance(arg, str) and "\0" not in arg for arg in argv)
            and sched.string(raw.get("pidfile"))):
        raise ValueError("copy config requires argv and a pidfile")
    values = {"{out}": str(out), "{entry}": entry}

    def replace(value):
        return re.sub(r"\{(?:out|entry)\}", lambda match: values[match[0]], value)

    pidfile = Path(replace(raw["pidfile"]))
    if not pidfile.is_absolute():
        pidfile = path.absolute().parent / pidfile
    pidfile = pidfile.resolve()
    reserved = [custody / name for name in ("closes", "copy-control", "mbp_ledger.jsonl",
                                           "desk_fence.json", ".tick.lock")]
    if any(pidfile.is_relative_to(path) for path in [out, *reserved]):
        raise ValueError("copy pidfile must be outside OUT and the close control paths")
    return {"argv": [replace(value) for value in raw["argv"]], "pidfile": str(pidfile)}


def active_copy(custody):
    control = custody / "copy-control"
    if control.is_symlink():
        raise ValueError("copy control must not be a symlink")
    active = read_optional(control / "active.json")
    if active is None:
        return None
    job = active.get("job")
    if not sched.hexadecimal(32)(job):
        raise ValueError("invalid copy job")
    state = control / job
    try:
        with (state / "lease").open("rb") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return {**active, **(read_optional(state / "ready.json") or {})}
    except FileNotFoundError:
        pass
    return None


def copy_starting(custody):
    try:
        with (custody / "copy-control" / "start.lock").open("rb") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
    except FileNotFoundError:
        return False
    except BlockingIOError:
        return True
    return False


def start_copy(custody, out, entry, config, attempt=None):
    control = managed_directory(custody / "copy-control", out)
    with lock(control / "start.lock"):
        active = active_copy(custody)
        if active is not None:
            if (active["entry_id"] == entry and active["out"] == str(out)
                    and active.get("attempt") == attempt and active.get("pid")):
                return active["pid"]
            raise ValueError("another copy is active")
        job = uuid.uuid4().hex
        state = managed_directory(control / job, out)
        create_once(state / "config.json", json_line(config))
        sched.write_facts(control / "active.json", {
            "job": job, "entry_id": entry, "out": str(out), "attempt": attempt,
        })
        child = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "_copy-worker", str(state)],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        with child.stdout:
            if not select.select([child.stdout], [], [], TIMEOUT)[0]:
                create_once(state / "stop", "")
                raise ValueError("copy supervisor did not respond")
            pid = child.stdout.readline().strip()
        if not pid.isdigit() or not positive_pid(int(pid)):
            raise ValueError("copy supervisor did not start a child")
        return int(pid)


def copy_stop_requested(state):
    return (state / "stop").is_file()


def run_copy_child(state, argv, ready, finished=None):
    # The supervisor owns the Popen handle. A stale pidfile cannot signal a
    # reused PID because the parent does not reap this child before TERM.
    if copy_stop_requested(state):
        return
    child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        ready(child.pid)
    except BaseException:
        child.terminate()
        child.wait()
        raise
    sent = False
    while child.poll() is None:
        if not sent and copy_stop_requested(state):
            child.terminate()
            sent = True
        time.sleep(COPY_POLL_S)
    if finished is not None:
        finished(child.pid)


def copy_worker(state):
    with lock(state / "lease"):
        config = sched.read_regular_json(state / "config.json")
        pidfile = Path(config["pidfile"])
        if pidfile.exists() or pidfile.is_symlink():
            return 2
        published = None

        def ready(pid):
            nonlocal published
            if not create_once(pidfile, f"{pid}\n"):
                raise ValueError("copy pidfile already exists")
            published = pidfile.lstat()
            create_once(state / "ready.json", json_line({"pid": pid}))
            print(pid, flush=True)

        def finished(pid):
            # The child has been reaped. Its isolated group remains observable
            # if a descendant survives the original process.
            live = probe(["/bin/ps", "-axo", "pid=,pgid=,stat="], groups)
            if live is not None and pid not in live.values():
                create_once(state / "done.json", json_line({"pgid": pid}))

        try:
            run_copy_child(state, config["argv"], ready, finished)
        finally:
            if published is not None:
                try:
                    if os.path.samestat(published, pidfile.lstat()):
                        pidfile.unlink()
                except FileNotFoundError:
                    pass
    return 0


def request_copy_stop(custody, active, timeout):
    create_once(custody / "copy-control" / active["job"] / "stop", "")
    deadline = time.monotonic() + timeout
    while (remaining := deadline - time.monotonic()) > 0:
        current = active_copy(custody)
        if current is None or current["job"] != active["job"]:
            return True
        time.sleep(min(COPY_POLL_S, remaining))
    return False


def read_head(path):
    try:
        head = sched.read_regular_json(path)
        sched.head_valid(head)
        return head
    except (*CLOSE_ERRORS, sched.Halt) as exc:
        raise sched.Halt("LEDGER_HEAD_INVALID", "committed head is unreadable or invalid") from exc


def read_rows(stream):
    rows = []
    for line in stream:
        sched.require(line.endswith("\n"), "LEDGER_INVALID", "event ledger has an incomplete row")
        rows.append(sched.parse_json(line))
    return rows


def read_snapshot(ledger, *, optional=False, nonblocking=False):
    head_path = sched.default_head_path(ledger)
    if ledger.is_symlink() or not sched.separate_output(head_path, (ledger,)):
        raise sched.Halt("LEDGER_INVALID", "event ledger and committed head must be separate files")
    if optional and not ledger.exists() and not head_path.exists() and not head_path.is_symlink():
        return None
    head = read_head(head_path)
    fd = os.open(ledger, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, encoding="utf-8", newline="") as stream:
        sched.require(stat.S_ISREG(os.fstat(fd).st_mode), "LEDGER_INVALID", "event ledger is not regular")
        fcntl.flock(fd, fcntl.LOCK_SH | (fcntl.LOCK_NB if nonblocking else 0))
        return head, sched.History(read_rows(stream), head)


def record_matches(record, launch, receipt):
    return (record.get("schema") == SCHEMA and attempt_key(record) == attempt_key(launch)
            and record.get("open_seq") == launch["seq"] and record.get("receipt") == receipt
            and record.get("ended_epoch") == receipt["ended"]["epoch_s"])


def receipt_locations(root, depth=1, *, dir_fd=None, name=None):
    with directory(root if name is None else name, dir_fd=dir_fd) as parent:
        try:
            data = sched.read_regular_json(RECEIPT, dir_fd=parent)
        except FileNotFoundError:
            pass
        else:
            yield root, project_receipt(data)
        if depth >= 4:
            return
        with os.scandir(parent) as entries:
            children = sorted(item.name for item in entries if item.is_dir(follow_symlinks=False))
        for child in children:
            yield from receipt_locations(root / child, depth + 1, dir_fd=parent, name=child)


def receipts_in(roots):
    locations = {}
    for root in roots:
        for location, receipt in receipt_locations(root.absolute()):
            locations[location.resolve()] = receipt
    return locations


def bound(launch):
    return {"open_seq": launch["seq"], **{key: launch[key] for key in ("span_id", "entry_id", "kit_sha256")}}


def close_events(record, launch):
    events = [
        {"event": "RECEIPT", "receipt_id": launch["span_id"],
         "receipt": sched.project_receipt(record["receipt"])},
        {"event": "CLOSE", "legs": launch["legs"], "ended_epoch": record["ended_epoch"],
         "clean": record["clean"], "load_redos": record["load_redos"], "load_flag": record["load_flag"] is not False},
    ]
    checks = record["restore_readbacks"]
    if all(type(value) is bool for value in checks.values()) and (
        record["restore_proven"] or any(value is False for value in checks.values())
    ):
        events.insert(1, {"event": "RESTORE", "readbacks": checks})
    events.extend({"event": "STOP", "code": stop["code"], "epoch": stop["epoch"]}
                  for stop in record["stops"])
    if "start_seq" in record["copy"]:
        events.append({"event": "COPY_STARTED", "copy_start_seq": record["copy"]["start_seq"]})
    return events


OBSERVED = {"RECEIPT", "RESTORE", "CLOSE", "STOP", "COPY_STARTED", "UPLOAD_STOPPED"}


def stage_observations(history, launch, observed):
    run = history.attempts.get(launch["seq"])
    sched.require(run is not None and sched.same(run.launch, launch), "LEDGER_ATTEMPT_CONFLICT",
                  f"{launch['span_id']} launch changed before event publication")
    binding = bound(launch)
    staged = []
    for observation in observed:
        event = observation["event"]
        sched.require(event in OBSERVED and not (binding.keys() | {"seq"}) & observation.keys(),
                      "EVENT_AUTHORITY", "producer supplied a foreign field or event")
        payload = {"legs": 0, **{k: v for k, v in observation.items() if k != "copy_start_seq"}, **binding}
        rows = history.rows + staged
        same_run = [row for row in rows if row.get("open_seq") == launch["seq"]]
        matches = [row for row in same_run if row["event"] == event]
        start_seq = observation.get("copy_start_seq")
        next_seq = len(rows) + 1
        if event == "COPY_STARTED":
            sched.require(sched.positive_integer(start_seq) and start_seq <= next_seq, "COPY_SEQUENCE",
                          f"{launch['span_id']} copy start has no reserved sequence")
            matches = [rows[start_seq - 1]] if start_seq < next_seq else []
        elif event == "UPLOAD_STOPPED":
            latest_start = max((row["seq"] for row in same_run if row["event"] == "COPY_STARTED"), default=None)
            sched.require(latest_start is not None and start_seq == latest_start, "COPY_SEQUENCE",
                          f"{launch['span_id']} stop does not observe the latest copy start")
            matches = [row for row in matches if row["seq"] > start_seq]
        elif event == "STOP":
            matches = [row for row in matches if row["code"] == payload["code"]]
        if matches:
            sched.require(all(sched.same({k: v for k, v in row.items() if k != "seq"}, payload)
                              for row in matches), "CLOSE_CONFLICT",
                          f"{launch['span_id']} has conflicting {event} evidence")
        else:
            staged.append({**payload, "seq": next_seq})
    return staged


def publish_head(path, head):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False,
                                         mode="w", encoding="utf-8") as stream:
            temporary = Path(stream.name)
            stream.write(sched.canonical(head) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        with directory(path.parent) as parent:
            os.fsync(parent)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def append_observed(ledger, expected_head, launch, observed):
    """Append only to an existing, independently committed stream."""
    head_path = sched.default_head_path(ledger)
    sched.require(sched.separate_output(head_path, (ledger,)), "LEDGER_HEAD_INVALID",
                  "event ledger and committed head need separate files")
    fd = os.open(ledger, os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "r+", encoding="utf-8", newline="") as stream:
        sched.require(stat.S_ISREG(os.fstat(fd).st_mode), "LEDGER_INVALID", "event ledger is not regular")
        fcntl.flock(fd, fcntl.LOCK_EX)
        head = read_head(head_path)
        sched.require(sched.same(head, expected_head), "LEDGER_HEAD_CHANGED",
                      "committed head changed before event publication")
        rows = read_rows(stream)
        history = sched.History(rows, head)
        staged = stage_observations(history, launch, observed)
        if not staged:
            return head
        new_rows = rows + staged
        new_head = {**head, "last_seq": len(new_rows), "digest": sched.ledger_digest(new_rows)}
        sched.History(new_rows, new_head)
        stream.write("".join(sched.canonical(row) + "\n" for row in staged))
        stream.flush()
        os.fsync(fd)
        publish_head(head_path, new_head)
        return new_head


def observed_copy_stop(custody, ledger, snapshot):
    if snapshot is None or active_copy(custody) is not None:
        return snapshot
    control = custody / "copy-control"
    job = read_optional(control / "active.json")
    if job is None or not sched.hexadecimal(32)(job.get("job")):
        return snapshot
    state = control / job["job"]
    done, ready = read_optional(state / "done.json"), read_optional(state / "ready.json")
    pgid = obj(done).get("pgid")
    if not positive_pid(pgid) or obj(ready).get("pid") != pgid:
        return snapshot
    head, history = snapshot
    attempt = obj(job.get("attempt"))
    run = history.attempts.get(attempt.get("open_seq"))
    if run is None or attempt_key(attempt) != attempt_key(run.launch):
        return snapshot
    start_seq = attempt.get("copy_start_seq")
    latest_start = run.copy.get("COPY_STARTED")
    live = probe(["/bin/ps", "-axo", "pid=,pgid=,stat="], groups)
    if latest_start is None or start_seq != latest_start or live is None or pgid in live.values():
        return snapshot
    new_head = append_observed(ledger, head, run.launch, [{"event": "UPLOAD_STOPPED", "copy_start_seq": start_seq}])
    return read_snapshot(ledger) if new_head != head else snapshot


def newest_uncopied(custody, history=None):
    if history is not None:
        for run in reversed(history.attempts.values()):
            if run.close is not None and not run.copy_verified():
                record = read_optional(custody / "closes" / run.span / "close.json")
                if record and record.get("open_seq") == run.launch["seq"] and attempt_key(record) == attempt_key(run.launch):
                    return record, run
                return None, None
        return None, None
    candidates = [record for path in (custody / "closes").glob("*/close.json")
                  if not path.parent.is_symlink() and (record := read_optional(path))
                  and record.get("schema") == SCHEMA and "open_seq" not in record]
    if len(candidates) > 1:
        raise ValueError("multiple uncopied closes lack launch order")
    return next(iter(candidates), None), None


def copy_resume(custody, deadline):
    if deadline is not None and time.time() >= deadline:
        return 0
    ledger = custody / "mbp_ledger.jsonl"
    snapshot = observed_copy_stop(custody, ledger, read_snapshot(ledger, optional=True))
    history = snapshot[1] if snapshot is not None else None
    record, run = newest_uncopied(custody, history)
    if record is None or "config" not in record["copy"]:
        return 0
    out = Path(record["out"])
    name = attempt_name(record)
    attempt = {key: record[key] for key in ("entry_id", "kit_sha256", "t0_epoch", "span_id") if key in record}
    if run is None:
        require_idle_group(custody, record, name=name, out=out)
    else:
        require_idle_group(custody, history.latest.launch)
        sched.require(not any(attempt.upload_active() for attempt in history.attempts.values()),
                      "UPLOAD_ACTIVE", "existing copy must stop before resuming")
        attempt.update(open_seq=run.launch["seq"], copy_start_seq=snapshot[0]["last_seq"] + 1)
    pid = start_copy(custody, out, name, record["copy"]["config"], attempt)
    if run is not None:
        append_observed(ledger, snapshot[0], run.launch, [
            {"event": "COPY_STARTED", "copy_start_seq": attempt["copy_start_seq"]},
        ])
    print(f"Copy started (pid {pid})")
    return 0


def copy_limits(rules, override):
    params = next((rule["params"] for rule in rules
                   if rule["test"] == "copy_debt" and rule["status"] == "LIVE"), {})
    registered = params.get("wait_s", 600)
    return (min(registered, override) if override is not None else registered, params.get("page_age_s", 7200))


def wait_for_copy(custody, ledger, active, launch, deadline_epoch):
    deadline = time.monotonic() + max(0, deadline_epoch - time.time())
    while time.monotonic() < deadline:
        try:
            _, history = read_snapshot(ledger, nonblocking=True)
        except BlockingIOError:
            pass
        else:
            sched.require(history.latest.launch == launch, "LEDGER_HEAD_CHANGED", "attempt changed during copy wait")
            if history.latest.copy_verified():
                break
        current = active_copy(custody)
        if current is None or current["job"] != active["job"]:
            return
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(COPY_POLL_S, remaining))
    request_copy_stop(custody, active, 0)


def add_close_options(parser):
    parser.add_argument("--custody", type=Path, required=True)
    parser.add_argument("--copy-config", type=Path)
    parser.add_argument("--no-copy", action="store_true")
    parser.add_argument("--high-power-marker", type=Path, default=HIGH_POWER_MARKER)


def copy_wait_seconds(value):
    try:
        seconds = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected seconds") from exc
    if not math.isfinite(seconds) or seconds < 0:
        raise argparse.ArgumentTypeError("expected finite nonnegative seconds")
    return seconds


def add_tick_parser(commands, queue, rules):
    tick = commands.add_parser("tick", help="close the latest finished attempt and print the next decision")
    add_close_options(tick)
    tick.add_argument("--receipt-root", type=Path, required=True, action="append")
    tick.add_argument("--queue", type=Path, default=queue)
    tick.add_argument("--rules", type=Path, default=rules)
    tick.add_argument("--caller-pid", "--self-pid", type=sched.positive_pid)
    tick.add_argument("--host-facts", type=Path)
    tick.add_argument("--queue-commit")
    tick.add_argument("--maintenance-marker", type=Path)
    tick.add_argument("--run-plans", action="store_true")
    tick.add_argument("--copy-wait-s", type=copy_wait_seconds)
    tick.add_argument("--record", type=Path, help="separate decision log (default: CUSTODY/mbp_decisions.jsonl)")
    tick.set_defaults(tick_action=run_tick_command)


def probe_for_tick(args, queue, rules, ledger, launch):
    supplied = sched.read_regular_json(args.host_facts) if args.host_facts is not None else {}
    # The retained fence is evidence for this attempt. Observe it by PGID
    # rather than asking the general probe to treat file presence as live.
    require_idle_group(args.custody, launch)
    supplied.update(fence_clear=True, runner_group_clear=True,
                    high_power_marker=marker_present(args.high_power_marker))
    if copy_starting(args.custody) or active_copy(args.custody) is not None:
        supplied["upload_stopped"] = False
    options = argparse.Namespace(**{
        **vars(args), "custody": None, "receipt_root": [], "ledger": ledger,
        "ledger_head": sched.default_head_path(ledger),
    })
    return sched.probe(options, queue, rules, sched.checked_config(queue, rules), supplied)[0]


def maintenance_wait(rules, now):
    rule = next((rule for rule in rules if rule["test"] == "owner_stop" and rule["status"] == "LIVE"), {})
    return {"decision": "WAIT", "reason": "MAINTENANCE", "rule": rule.get("id", "owner-stop"),
            "class": "SAFETY", "until_epoch": now + rule.get("params", {}).get("recheck_s", 60),
            "detail": "owner maintenance marker is present"}


def halt(rule, detail, launch=None):
    decision = {"decision": "HALT", "rule": rule, "detail": detail}
    if launch is not None:
        decision["entry"] = launch["span_id"]
    return decision


def finish_attempt(args, ledger, snapshot):
    head, history = snapshot
    launch = history.latest.launch
    retained = require_idle_group(args.custody, launch)
    pgid = retained["pgid"]
    locations = receipts_in(args.receipt_root)
    matches = [(out, receipt) for out, receipt in locations.items() if matching_receipt(receipt, launch)]
    sched.require(len(matches) == 1, "RECEIPT_MISSING",
                  f"{launch['span_id']} has no unique matching runner receipt")
    out, receipt = matches[0]
    args.out, args.entry = out, launch["span_id"]
    target = args.custody / "closes" / args.entry / "close.json"
    if history.latest.close is None:
        record, _, _ = make_close(args, launch=launch, receipt=receipt, snapshot=snapshot)
    else:
        record = read_optional(target)
    if record is not None:
        sched.require(record_matches(record, launch, receipt) and record.get("pgid") == pgid,
                      "CLOSE_CONFLICT", f"{launch['span_id']} conflicts with its immutable close")
        new_head = append_observed(ledger, head, launch, close_events(record, launch))
        if new_head != head:
            head, history = read_snapshot(ledger)
    sched.require(history.latest.launch == launch, "LEDGER_HEAD_CHANGED", "attempt changed during close")
    if history.latest.receipt is not None:
        native = sched.project_receipt(receipt)
        # A previously committed receipt may omit optional fields. Every
        # attested field must agree with the fresh native receipt.
        sched.require(all(sched.same(native.get(key), value) for key, value in history.latest.receipt.items()),
                      "RECEIPT_CONFLICT", f"{launch['span_id']} native and committed receipts disagree")
    return head, history


def page_debt(history, now, age):
    pages = {}
    for row in history.copy_debts():
        hours = (now - row["ended_epoch"]) / 3600
        if now - row["ended_epoch"] >= age:
            pages[row["entry_id"]] = max(pages.get(row["entry_id"], 0), hours)
    for entry, hours in sorted(pages.items()):
        print(f"PAGE uncopied {entry} {hours:.2f}")


def run_tick_command(args):
    try:
        args.custody = args.custody.resolve(strict=True)
        ledger = args.custody / "mbp_ledger.jsonl"
        head_path = sched.default_head_path(ledger)
        decision_log = args.record or args.custody / "mbp_decisions.jsonl"
        protected = (ledger, head_path, args.rules, args.queue, args.host_facts,
                     args.custody / "desk_fence.json", args.custody / ".tick.lock")
        roots = [root.resolve() for root in args.receipt_root]
        if (any(args.custody.is_relative_to(root) or decision_log.resolve().is_relative_to(root) for root in roots)
                or not sched.separate_output(decision_log, protected)):
            print(sched.as_json(halt("RECORD_PATH", "decision record must be separate from tick inputs and OUT")))
            return 0
        with lock(args.custody / ".tick.lock"):
            return run_tick(args, ledger, decision_log)
    except CLOSE_ERRORS as exc:
        print(sched.as_json(halt("TICK_INPUT", str(exc))))
        return 2


def run_tick(args, ledger, decision_log):
    now = time.time()
    launch = None
    head_path = sched.default_head_path(ledger)
    try:
        queue = sched.read_regular_json(args.queue)
        with args.rules.open(encoding="utf-8") as stream:
            rules = sched.parse_json(stream.read())
        sched.checked_config(queue, rules)
        snapshot = read_snapshot(ledger)
        _, history = snapshot
        sched.require(history.latest is not None, "PREDECESSOR_MISSING", "no attempt opened in committed ledger")
        launch = history.latest.launch
        snapshot = finish_attempt(args, ledger, snapshot)
        head, history = observed_copy_stop(args.custody, ledger, snapshot)
        sched.require(history.latest.launch == launch, "LEDGER_HEAD_CHANGED", "attempt changed during tick")
        facts = probe_for_tick(args, queue, rules, ledger, launch)
        if facts["maintenance_active"] is not True:
            # Preserve the attempt-specific proof refusal even when a requested
            # dry run also fails because the preceding close is unproven.
            history.latest.prove_close()
        wait, page_age = copy_limits(rules, args.copy_wait_s)
        active = active_copy(args.custody)
        if active is not None and facts["maintenance_active"] is not True and history.latest.close is not None:
            wait_for_copy(args.custody, ledger, active, launch, history.latest.close["ended_epoch"] + wait)
            head, history = observed_copy_stop(args.custody, ledger, read_snapshot(ledger))
            sched.require(history.latest.launch == launch, "LEDGER_HEAD_CHANGED", "attempt changed during tick")
            facts = probe_for_tick(args, queue, rules, ledger, launch)

        def recheck_head():
            require_idle_group(args.custody, launch)
            if copy_starting(args.custody) or active_copy(args.custody) is not None:
                raise sched.Halt("UPLOAD_ACTIVE", "an upload is still active")
            return read_head(head_path)

        now = facts["now_epoch"]
        if facts["maintenance_active"] is True:
            decision = maintenance_wait(rules, now)
        else:
            decision = sched.authorize_next(
                queue, rules, facts, history.rows, head, now=now, caller_pid=args.caller_pid, recheck_head=recheck_head,
            )["decision"]
            if decision["decision"] == "HALT":
                decision.setdefault("entry", launch["span_id"])
        page_debt(history, now, page_age)
    except sched.Halt as exc:
        decision = dict(exc.decision)
        if launch is not None:
            decision.setdefault("entry", launch["span_id"])
    except (Refused, *CLOSE_ERRORS) as exc:
        decision = halt("CLOSE_UNPROVEN", str(exc), launch)
    # Check again so a path changed during the copy wait cannot alias evidence.
    if not sched.separate_output(decision_log, (ledger, head_path)):
        decision = halt("RECORD_PATH", "decision record aliases committed history")
    else:
        try:
            sched.append_decision(decision_log, decision, now)
        except (OSError, ValueError):
            decision = halt("RECORD_WRITE", "decision observation could not be appended")
    print(sched.as_json(decision))
    return 0


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    close = commands.add_parser("close")
    add_close_options(close)
    close.add_argument("--out", type=Path, required=True)
    close.add_argument("--entry", required=True)
    close.add_argument("--post", action="store_true")
    resume = commands.add_parser("copy-resume")
    resume.add_argument("--custody", type=Path, required=True)
    resume.add_argument("--deadline-epoch", type=sched.parse_epoch)
    stop = commands.add_parser("copy-stop")
    stop.add_argument("--custody", type=Path, required=True)
    return root


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 2 and argv[0] == "_copy-worker":
        return copy_worker(Path(argv[1]))
    args = parser().parse_args(argv)
    try:
        if args.command == "close":
            if not sched.identifier(args.entry) or args.entry in {".", ".."}:
                raise ValueError("invalid entry identifier")
            ledger = args.custody / "mbp_ledger.jsonl"
            snapshot = read_snapshot(ledger, optional=True)
            launch = snapshot[1].latest.launch if snapshot is not None and snapshot[1].latest is not None else None
            if snapshot is not None and launch is None:
                raise Refused("committed ledger has no launch")
            record, created, status = make_close(args, launch=launch, snapshot=snapshot)
            if launch is not None:
                append_observed(ledger, snapshot[0], launch, close_events(record, launch))
            name = attempt_name(record)
            body = args.custody.resolve() / "closes" / name / "summary.txt"
            command = post_argv(name, body)
            print(summary(record), end="")
            if args.post and created:
                posted = subprocess.run(command, capture_output=True, text=True, check=False)
                print("RUN_STATE posted" if posted.returncode == 0 else shlex.join(command))
                return status or posted.returncode
            print(shlex.join(command))
            return status
        if args.command == "copy-resume":
            return copy_resume(args.custody, args.deadline_epoch)
        active = active_copy(args.custody)
        if active is not None and not request_copy_stop(args.custody, active, COPY_STOP_S):
            print("copy-stop: child did not exit within 60 seconds", file=sys.stderr)
            return 2
        ledger = args.custody / "mbp_ledger.jsonl"
        observed_copy_stop(args.custody, ledger, read_snapshot(ledger, optional=True))
        return 0
    except sched.Halt as exc:
        print(f"{args.command}: {exc.decision['detail']}", file=sys.stderr)
        return 4
    except Refused as exc:
        print(f"{args.command}: {exc}", file=sys.stderr)
        return 4
    except (OSError, ValueError, RecursionError, subprocess.SubprocessError) as exc:
        print(f"{args.command}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
