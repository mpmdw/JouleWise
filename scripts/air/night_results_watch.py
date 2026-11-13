"""Air-only, structure-only results watcher. No work happens at import time.

Exit status: 0 quiet, 10 notice, 20 alarm, 2 usage/internal error.
Git never checks out a results branch. Only projected structural records reach
the temporary directory; existence markers (including slots) are empty files.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime as dt
import importlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from joulewise import window_state as ws

MAIN_REF = "refs/heads/main:refs/air-watch/main"
EXIT_CODES = {"quiet": 0, "notice": 10, "alarm": 20, "error": 2}
PREFIX = "refs/heads/night-results/"
ROOT = Path(__file__).resolve().parents[2]
PAYLOADS = ("r1_result.json", "align-r1/r1_result.json")
SLOTS = ("r1_slots.json", "align-r1/r1_slots.json")
# _artifact_list/_durable_record on main and _publish_terminal_result on W1.
# Neither writer publishes night_plan.json or the R1 payload/slots files.
PUBLISHED_PREFIX = "docs/process_traces/night-results/"
PUBLISHED_JSON = ("result.json", "refusal.json", "chain.started", "chain.exited",
                  "chain.unkilled", "hazard_result.json", "courier.json", "courier.delivery.json")
PUBLISHED_EXISTENCE = ("censuses.jsonl", "receipt.json", "clean_dwell.output.txt", "clean_dwell.json",
                       "start_conditions.json", "go_receipt.json", "go-census.json", "arm_decision.json",
                       "launch.pending", "launch.resolved", "network_time_off.json", "courier.sent",
                       "courier.filed", "courier.heartbeat")
MAX_RECORD = 4 * 1024 * 1024


class WatchError(Exception):
    """Diagnostic deliberately contains no subprocess or record text."""


def number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def plan_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value):
        raise ValueError("invalid plan id")
    if ".." in value or value.endswith((".", ".lock")):
        raise ValueError("invalid plan id")
    return value


def valid_ref(ref):
    return isinstance(ref, str) and ref.startswith(PREFIX) and plan_id(ref[len(PREFIX):])


def oid(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value) is not None


class Git:
    """Small injectable Git boundary. HTTPS/file only; SSH is disabled outright."""

    def __init__(self, repository, timeout=25):
        self.repository = Path(repository)
        self.timeout = timeout

    def _run(self, *args):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never",
                   GIT_ALLOW_PROTOCOL="file:https",
                   GIT_ASKPASS="/usr/bin/false", SSH_ASKPASS="/usr/bin/false",
                   GIT_SSH_COMMAND="/usr/bin/false")
        argv = ["git", "-C", str(self.repository), "-c", "gc.auto=0",
                "-c", "maintenance.auto=false", "-c", "credential.interactive=false",
                "-c", "protocol.allow=never", "-c", "protocol.https.allow=always",
                "-c", "protocol.file.allow=always", *args]
        try:
            proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL, env=env, start_new_session=True)
            try:
                output, _ = proc.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate(timeout=2)
                raise WatchError("GIT_TIMEOUT") from None
            if proc.returncode:
                raise WatchError("GIT_FAILED")
            return output
        except OSError:
            raise WatchError("GIT_UNAVAILABLE") from None

    def ls_remote(self, pattern):
        rows = {}
        try:
            for line in self._run("ls-remote", "--refs", "origin", pattern).decode("ascii").splitlines():
                sha, ref = line.split()
                if not oid(sha) or not valid_ref(ref) or ref in rows:
                    raise ValueError()
                rows[ref] = sha
        except (ValueError, UnicodeError):
            raise WatchError("GIT_INVALID_REFS") from None
        return rows

    def check_origin(self):
        """Fail before polling, without exposing the URL or invoking transport."""
        raw = self._run("remote", "get-url", "origin")
        try:
            url = raw.decode("utf-8").strip()
            parsed = urlsplit(url)
            allowed = ((parsed.scheme == "https" and url.startswith("https://") and bool(parsed.netloc))
                       or (parsed.scheme == "file" and url.startswith("file://"))
                       or (not parsed.scheme and not re.match(r"[^/]*:", url)))
            if not url or any(ord(c) < 32 for c in url) or not allowed:
                raise ValueError()
        except (UnicodeError, ValueError):
            raise WatchError("ORIGIN_PROTOCOL_NOT_ALLOWED") from None

    def fetch(self, ref):
        if not valid_ref(ref):
            raise WatchError("GIT_INVALID_REF")
        self._run("fetch", "--no-tags", "--no-write-fetch-head", "origin", ref)

    def list_tree(self, ref):
        if not oid(ref):
            raise WatchError("GIT_INVALID_OID")
        # Ignore symlinks/submodules, even when they have an allowed filename.
        paths = set()
        for row in self._run("ls-tree", "-rz", "--full-tree", ref).split(b"\0"):
            if row:
                header, path = row.split(b"\t", 1)
                if header.startswith((b"100644 blob ", b"100755 blob ")):
                    paths.add(os.fsdecode(path))
        return paths

    def fetch_main(self):
        """Refresh a private ref only; never touches the working tree or branches."""
        self._run("fetch", "--no-tags", "--no-write-fetch-head", "origin", "+" + MAIN_REF)

    def current_from_main(self):
        return self._run("cat-file", "blob", MAIN_REF.split(":", 1)[1] + ":docs/process/CURRENT.json")

    def show(self, ref, path):
        if not oid(ref):
            raise WatchError("GIT_INVALID_OID")
        return self._run("show", f"{ref}:{path}")


def optional_exit_module():
    if not (ROOT / "joulewise/exit_contract.py").is_file():
        return None
    try:
        return importlib.import_module("joulewise.exit_contract")
    except ImportError:
        return None


def declared_contract(plan, module):
    """Adapt plan words, never the exit tool's own outcome vocabulary (N-1)."""
    if "exit_contract" not in plan:
        return None
    raw = plan["exit_contract"]
    if not isinstance(raw, dict):
        raise WatchError("INVALID_EXIT_CONTRACT")
    # The shadow reader's plan vocabulary is also a safe fallback when the
    # optional exit tool has not landed. Never ignore a declared refusal.
    allowed = set(module.PLAN_WORDS) & ws.EXIT_WORDS if module is not None else ws.EXIT_WORDS
    result = {}
    for key, word in raw.items():
        if not isinstance(key, str) or not re.fullmatch(r"0|[1-9][0-9]*", key):
            raise WatchError("INVALID_EXIT_CONTRACT")
        if not isinstance(word, str) or word not in allowed:
            raise WatchError("INVALID_EXIT_CONTRACT")
        result[int(key)] = word
    return result


def parse_object(raw):
    def unique(pairs):
        doc = {}
        for key, value in pairs:
            if key in doc:
                raise ValueError()
            doc[key] = value
        return doc

    def invalid(_):
        raise ValueError()

    try:
        if len(raw) > MAX_RECORD:
            raise ValueError()
        doc = json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)
        if not isinstance(doc, dict):
            raise ValueError()
        return doc
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        raise WatchError("INVALID_RECORD") from None


def project(doc):
    """Keep only window_state inputs. Invalid values become a fixed sentinel.

    Keeping the key with a sentinel preserves fail-closed validation. Counts
    replace arbitrary reason strings. Slots and all other existence-only files
    are never read. Nested measurements, identifiers and paths are discarded.
    """
    validators = {
        "verdict": lambda v: isinstance(v, str) and v in ws.VERDICTS,
        "chain_exit_code": lambda v: v is None or type(v) is int,
        "exit_code": lambda v: v is None or type(v) is int,
        "fault": lambda v: type(v) is bool,
        "measurement_outcome": lambda v: v is None or isinstance(v, str) and v in ws.MEASUREMENT_OUTCOMES,
        "chain_outcome": lambda v: isinstance(v, str) and v in ws.RECORDED_OUTCOMES,
        "status": lambda v: isinstance(v, str) and v in ws.PAYLOAD_STATUSES,
        "ended_epoch_s": number, "t0_epoch_s": number,
        "window_max_s": lambda v: number(v) and v > 0,
        "courier_mode": lambda v: isinstance(v, str) and v in {"file-only", "mail", "git-push"},
        "sent": lambda v: type(v) is bool,
        "transport": lambda v: isinstance(v, str) and v in {"git-push", "mail", "file"},
        "commit": oid,
        "result_sha256": lambda v: isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) is not None,
        "ref": lambda v: isinstance(v, str) and v.startswith(PREFIX) and len(v) > len(PREFIX),
    }
    out = {key: value if validators[key](value) else []
           for key, value in doc.items() if key in validators}
    # Delivery proofs need only valid shape, never actual identifiers.
    for key in ("message_id", "mail_message_id"):
        if key in doc:
            v = doc[key]
            out[key] = "recorded" if isinstance(v, str) and v.strip() else []
    for key, replacement in (("commit", "a" * 40), ("result_sha256", "a" * 64),
                             ("ref", PREFIX + "recorded")):
        if key in out and out[key] != []:
            out[key] = replacement
    for key in ("fault_reasons", "reasons"):
        if key in doc:
            v = doc[key]
            out[key] = (["recorded_fault"] * len(v) if isinstance(v, list)
                        and all(isinstance(r, str) and r for r in v) else False)
    for key in ("chain", "faults"):
        if key in doc:
            out[key] = project(doc[key]) if isinstance(doc[key], dict) else False
    return out


def layout(paths, plan):
    """Use a single coherent layout; never mix two directories' records."""
    published = PUBLISHED_PREFIX + plan + "/"
    if any(published + name in paths for name in (*PUBLISHED_JSON, *PUBLISHED_EXISTENCE)):
        return published
    prefixes = (plan + "/", "night/", "")
    for prefix in prefixes:
        if prefix + "result.json" in paths:
            return prefix
    for prefix in prefixes:
        if any(prefix + name in paths for name in (*ws.JSON_MARKERS, *ws.EXISTENCE_MARKERS, *PAYLOADS, *SLOTS)):
            return prefix
    return ""


@dataclass(frozen=True)
class Summary:
    outcome: str = "UNKNOWN"
    state: str = "UNKNOWN"
    invariants: tuple[str, ...] = ()
    verdict: str | None = None
    chain_exit_code: int | None = None
    fault: bool | None = None
    fault_reason_count: int = 0
    result_exists: bool = False

    def fields(self):
        return (f"outcome={self.outcome} state={self.state} "
                f"invariants={','.join(self.invariants) or '-'} verdict={self.verdict or 'UNKNOWN'} "
                f"chain_exit_code={'absent' if self.chain_exit_code is None else self.chain_exit_code} "
                # A record generation without the field prints "absent", never "False".
                f"fault={'absent' if self.fault is None else str(self.fault).lower()} "
                f"fault_reason_count={self.fault_reason_count}")


def inspect_ref(git, ref, sha, now, exit_module=None):
    git.fetch(ref)
    paths = git.list_tree(sha)
    plan = plan_id(ref[len(PREFIX):])
    prefix = layout(paths, plan)
    published = prefix == PUBLISHED_PREFIX + plan + "/"
    json_names = PUBLISHED_JSON if published else (*ws.JSON_MARKERS, *PAYLOADS)
    existence_names = PUBLISHED_EXISTENCE if published else (*ws.EXISTENCE_MARKERS, *SLOTS)
    raw_plan = {}
    # Plans can carry outcome-bearing extra fields too; never write them raw.
    # A published branch never gets a plan from another directory in its tree.
    plan_path = None if published else next(
        (p for p in (plan + "/night_plan.json", "night_plan.json") if p in paths), None)
    if plan_path:
        raw_plan = parse_object(git.show(sha, plan_path))
    contract = declared_contract(raw_plan, exit_module)
    with tempfile.TemporaryDirectory(prefix="jw-air-watch-") as directory:
        root = Path(directory)
        night = root / "night"
        night.mkdir()
        if plan_path:
            (root / "night_plan.json").write_text(json.dumps(project(raw_plan)), encoding="utf-8")
        for name in (*json_names, *existence_names):
            if prefix + name not in paths:
                continue
            destination = night / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            if name in existence_names:
                destination.touch()
            else:
                # A malformed record is still present; let the owning reader
                # classify it as UNKNOWN, without retaining any of its bytes.
                try:
                    doc = project(parse_object(git.show(sha, prefix + name)))
                except WatchError as error:
                    if str(error) != "INVALID_RECORD":
                        raise
                    destination.write_text("null", encoding="utf-8")
                else:
                    destination.write_text(json.dumps(doc), encoding="utf-8")
        observation = ws.observe_night_dir(root)  # plist facts intentionally unknown
        state = ws.derive_window_state(observation, now)
        outcome = ws.window_outcome(night, exit_contract=contract)
        # The night-only API cannot see plan delivery waivers/timing. Use the
        # full observation for invariants and plan errors, then recompute the
        # recorded-outcome check against the contract-aware outcome.
        word = ws.WindowOutcome.UNKNOWN if observation.errors else outcome.outcome
        invariants = set(state.violated_invariants) - {"RECORDED_OUTCOME_DISAGREES"}
        mismatch = ws.invariant_recorded_outcome(observation, word)
        if mismatch:
            invariants.add(mismatch)
        return Summary(word.value, state.state.value, tuple(sorted(invariants)),
                       observation.verdict, observation.chain_exit_code, observation.fault,
                       len(observation.fault_reasons), "result.json" in observation.markers)


@dataclass(frozen=True)
class Event:
    level: str
    code: str
    subject: str
    fields: str = ""
    identity: str = ""

    def line(self, now):
        stamp = dt.datetime.fromtimestamp(now, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return f"{stamp} {self.level} {self.code} {self.subject}" + (" " + self.fields if self.fields else "")


def result_events(ref, sha, summary):
    events = [Event("INFO", "RESULT", ref, summary.fields(), sha)]
    if summary.outcome not in {"MEASURED_OK", "MEASURED_WITH_FLAGS"}:
        events.append(Event("ALARM", "RESULT_NOT_MEASURED", ref, summary.fields(), sha))
    elif summary.outcome == "MEASURED_WITH_FLAGS":
        events.append(Event("NOTICE", "RESULT_WITH_FLAGS", ref, summary.fields(), sha))
    events.extend(Event("ALARM", "INVARIANT_VIOLATED:" + code, ref, summary.fields(), sha)
                  for code in summary.invariants)
    return events


def context_events(refs, results, current, now, min_expected_s, grace):
    """Pure optional timing checks. Unknown observables never mean success."""
    events = []
    armed = current.get("armed") or {}
    plan = armed.get("plan_id")
    if plan:
        plan_id(plan)
        ref = PREFIX + plan
        t0 = armed.get("t0_epoch_s", armed.get("t0"))
        latest = armed.get("latest_end_epoch_s", armed.get("latest_end"))
        if ref in refs and number(t0) and now < t0 + min_expected_s:
            events.append(Event("ALARM", "RESULT_EARLY", plan, identity=str(t0)))
        if ref not in refs and number(latest) and now > latest + grace:
            events.append(Event("ALARM", "ARMED_NO_RESULT_PAST_LATEST_END", plan, identity=str(latest)))
    wait = current.get("wait") or {}
    deadline = wait.get("deadline_epoch_s")
    if number(deadline) and now > deadline:
        observable = wait.get("observable")
        target = wait.get("plan_id", plan)
        if isinstance(observable, dict):
            target = observable.get("plan_id", target)
            observable = observable.get("kind")
        if target:
            plan_id(target)
        ref = PREFIX + target if target else None
        seen = (ref in refs if observable == "results_branch_exists" else
                results.get(ref, False) if observable == "result_json_exists" else None)
        if observable not in {"results_branch_exists", "result_json_exists"} or not target:
            # Only bounded identifier text is permitted in an unchecked code.
            word = observable if isinstance(observable, str) and re.fullmatch(r"[a-z_]{1,64}", observable) else "UNKNOWN"
            code = "DEADLINE_PASSED_UNCHECKED:" + word
        elif seen:
            return events
        else:
            code = "DEADLINE_PASSED"
        events.append(Event("ALARM", code, target or "-", identity=str(deadline)))
    return events


def empty_state():
    return {"version": 1, "initialized": False, "refs": {}, "active": [], "raised": [],
            "last_success": None, "started": None, "failures": 0, "read_failures": {}}


def load_state(path):
    if not path.exists():
        return empty_state()
    state = parse_object(path.read_bytes())
    # Round-1 state has no per-ref counter. Its baselines remain intact.
    state.setdefault("read_failures", {})
    try:
        if (state["version"] != 1 or type(state["initialized"]) is not bool
                or not isinstance(state["refs"], dict)
                or not all(valid_ref(r) and oid(s) for r, s in state["refs"].items())
                or not isinstance(state["active"], list)
                or not all(valid_ref(r) for r in state["active"])
                or not isinstance(state["raised"], list)
                or not all(isinstance(s, str) for s in state["raised"])
                or type(state["failures"]) is not int or state["failures"] < 0
                or not isinstance(state["read_failures"], dict)
                or not all(valid_ref(r) and isinstance(v, dict) and oid(v.get("sha"))
                           and type(v.get("count")) is int and v["count"] > 0
                           for r, v in state["read_failures"].items())
                or any(state[k] is not None and not number(state[k]) for k in ("last_success", "started"))):
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise WatchError("INVALID_STATE") from None
    return state


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False, encoding="utf-8") as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class Watcher:
    def __init__(self, git, state, *, include_plans=(), silence_s=600, failure_limit=3,
                 min_expected_s=0, grace=300, exit_module=None):
        self.git, self.state = git, state
        self.included = {PREFIX + plan_id(p) for p in include_plans}
        self.silence_s, self.failure_limit = silence_s, failure_limit
        self.min_expected_s, self.grace, self.exit_module = min_expected_s, grace, exit_module

    def poll(self, now, current=None):
        state = self.state
        if state["started"] is None:
            state["started"] = now
        events = []
        try:
            refs = self.git.ls_remote(PREFIX + "*")
            if not all(valid_ref(r) and oid(s) for r, s in refs.items()):
                raise WatchError("GIT_INVALID_REFS")
        except (WatchError, ValueError):
            state["failures"] += 1
            events.append(Event("INFO", "LS_REMOTE_FAILED", "-"))
            last = state["last_success"] if state["last_success"] is not None else state["started"]
            if state["failures"] >= self.failure_limit or now - last >= self.silence_s:
                events.append(Event("ALARM", "SILENCE", "-", identity=str(last)))
            # No absence claims from a failed remote snapshot.
            return self._new(events)
        state["last_success"], state["failures"] = now, 0
        first = not state["initialized"]
        results = {}
        active = set(state["active"])
        armed = (current or {}).get("armed") or {}
        target = armed.get("plan_id")
        included = self.included | ({PREFIX + plan_id(target)} if target is not None else set())
        for ref, sha in sorted(refs.items()):
            changed = state["refs"].get(ref) != sha
            eligible = ref in active or ref in included or changed and not first
            # A first snapshot establishes an unread baseline for unnamed refs.
            if not eligible:
                state["refs"][ref] = sha
                continue
            try:
                summary = inspect_ref(self.git, ref, sha, now, self.exit_module)
            except WatchError:
                previous = state["read_failures"].get(ref, {})
                count = previous.get("count", 0) + 1 if previous.get("sha") == sha else 1
                state["read_failures"][ref] = {"sha": sha, "count": count}
                events.append(Event("ALARM", "REF_READ_FAILED", ref, identity=sha))
                if count >= self.failure_limit:
                    events.append(Event("ALARM", "REF_READ_FAILING", ref, f"count={count}", sha))
                # Retain the old SHA: retries, including after restart, are mandatory.
                continue
            state["read_failures"].pop(ref, None)
            results[ref] = summary.result_exists
            active.add(ref)
            events.extend(result_events(ref, sha, summary))
            state["refs"][ref] = sha
        state["initialized"] = True
        state["active"] = sorted(active & refs.keys())
        # Drop deleted refs so their later reappearance is observable.
        state["refs"] = {r: s for r, s in state["refs"].items() if r in refs}
        state["read_failures"] = {r: v for r, v in state["read_failures"].items() if r in refs}
        events.extend(context_events(refs, results, current or {}, now, self.min_expected_s, self.grace))
        return self._new(events)

    def _new(self, events):
        raised = set(self.state["raised"])
        output = []
        for event in events:
            key = "|".join((event.level, event.code, event.subject, event.identity))
            if event.code == "LS_REMOTE_FAILED" or key not in raised:
                output.append(event)
                raised.add(key)
        self.state["raised"] = sorted(raised)
        return output


def event_exit(events):
    levels = {event.level for event in events}
    return EXIT_CODES["alarm"] if "ALARM" in levels else EXIT_CODES["notice"] if "NOTICE" in levels else EXIT_CODES["quiet"]


def read_current(path):
    # gen_current is intentionally not imported; CURRENT is an optional data API.
    if not path.is_file():
        return {}
    return parse_current(path.read_bytes())


def fresh_current(git, path):
    """CURRENT from origin/main via a private ref; else the local file. Returns (doc, stale)."""
    try:
        git.fetch_main()
        raw = git.current_from_main()
    except WatchError:
        return read_current(path), True
    return parse_current(raw), False


def parse_current(raw):
    doc = parse_object(raw)
    if any(doc.get(k) is not None and not isinstance(doc[k], dict) for k in ("armed", "wait")):
        raise WatchError("INVALID_CURRENT")
    armed, wait = doc.get("armed") or {}, doc.get("wait") or {}
    for key in ("t0", "t0_epoch_s", "latest_end", "latest_end_epoch_s"):
        if armed.get(key) is not None and not number(armed[key]):
            raise WatchError("INVALID_CURRENT")
    if wait and not number(wait.get("deadline_epoch_s")):
        raise WatchError("INVALID_CURRENT")
    return doc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--once", action="store_true")
    modes.add_argument("--loop", action="store_true")
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--state", type=Path, default=Path.home() / "Library/Application Support/JouleWise/air-watch/state.json")
    parser.add_argument("--current", type=Path, default=ROOT / "docs/process/CURRENT.json")
    parser.add_argument("--plan-id", type=plan_id)
    parser.add_argument("--include-plan", type=plan_id, action="append", default=[])
    for name, default in (("t0", None), ("latest-end", None),
                          ("min-expected-s", 0), ("grace", 300), ("silence-minutes", 10),
                          ("interval", 120), ("hours", 26), ("git-timeout", 25)):
        parser.add_argument("--" + name, type=float, default=default)
    parser.add_argument("--failure-limit", type=int, default=3)
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument("--current-from-origin", action="store_true",
                        help="fetch origin main into refs/air-watch/main and read CURRENT there; "
                             "fall back to --current with INFO CURRENT_STALE")
    parser.add_argument("--notify-cmd", nargs=argparse.REMAINDER, help="last option; argv, with event line appended")
    try:
        args = parser.parse_args(argv)
        if (any(v is not None and (not number(v) or v < 0) for v in
                (args.t0, args.latest_end, args.min_expected_s, args.grace))
                or any(not number(v) or v <= 0 for v in
                       (args.silence_minutes, args.interval, args.hours, args.git_timeout))
                or args.failure_limit < 2
                or (args.t0 is not None or args.latest_end is not None) and not args.plan_id
                or args.notify_cmd == []):
            parser.error("invalid timing, failure limit, plan or notification arguments")
        state = load_state(args.state)
        git = Git(args.repo, args.git_timeout)
        git.check_origin()
        watcher = Watcher(git, state, include_plans=args.include_plan,
                          silence_s=args.silence_minutes * 60, failure_limit=args.failure_limit,
                          min_expected_s=args.min_expected_s, grace=args.grace,
                          exit_module=optional_exit_module())
        stop = time.monotonic() + args.hours * 3600
        status = EXIT_CODES["quiet"]
        stale = False
        while True:
            if args.current_from_origin:
                current, now_stale = fresh_current(git, args.current)
                if now_stale and not stale:
                    print(Event("INFO", "CURRENT_STALE", "-").line(time.time()), flush=True)
                stale = now_stale
            else:
                current = read_current(args.current)
            if args.plan_id:
                current = dict(current, armed={"plan_id": args.plan_id,
                                              "t0_epoch_s": args.t0, "latest_end_epoch_s": args.latest_end})
            now = time.time()
            events = watcher.poll(now, current)
            for event in events:
                line = event.line(now)
                print(line, flush=True)
                if args.notify_cmd:
                    subprocess.run([*args.notify_cmd, line], stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   timeout=10, check=True)
            # Persist only after delivery. A crash may repeat a line; it must
            # never permanently suppress an alarm that was not delivered.
            save_state(args.state, state)
            status = max(status, event_exit(events))
            if args.once or event_exit(events) == EXIT_CODES["alarm"] and not args.keep_going:
                return status
            remaining = stop - time.monotonic()
            if remaining <= 0:
                return status
            time.sleep(min(args.interval, remaining))
    except SystemExit as error:
        return int(error.code)
    except WatchError as error:
        code = "ORIGIN_PROTOCOL_NOT_ALLOWED" if str(error) == "ORIGIN_PROTOCOL_NOT_ALLOWED" else "WATCH_ERROR"
        print(Event("INFO", code, "-").line(time.time()), flush=True)
        return EXIT_CODES["error"]
    except (OSError, ValueError, TypeError, AttributeError, subprocess.SubprocessError):
        print(Event("INFO", "WATCH_ERROR", "-").line(time.time()), flush=True)
        return EXIT_CODES["error"]


if __name__ == "__main__":
    raise SystemExit(main())
