"""Structure-only watchdog status over the terminal courier's Git-push route.

No checkout, plan, transcript or outcome is copied. Mutable files and temporary
Git objects live under watchdog storage; origin is read from the code clone.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
import re
import signal
import socket
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path


SCHEMA = "joulewise.watchdog_status.v1"
KEEPALIVE_S = 3600
# Start early enough for a 300 s launchd tick plus the shared transport budget.
KEEPALIVE_DUE_S = KEEPALIVE_S - 300 - 2 * 25
MIN_PUSH_INTERVAL_S = 60
TRANSPORT_BUDGET_S = 25
AIR_STALE_S = KEEPALIVE_S + 15 * 60
GIT = "/usr/bin/git"


def status_ref(host):
    if not isinstance(host, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", host):
        raise ValueError("invalid watchdog status host")
    if ".." in host or host.endswith((".", ".lock")):
        raise ValueError("invalid watchdog status host")
    return "refs/heads/watchdog-status/" + host


class GitTransport:
    """One shared deadline; launchd never waits for a terminal/auth prompt."""

    def __init__(self, repository):
        self.repository = Path(repository)
        self.deadline = time.monotonic() + TRANSPORT_BUDGET_S
        self.env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never",
                        GIT_ASKPASS="/usr/bin/false", SSH_ASKPASS="/usr/bin/false",
                        GIT_SSH_COMMAND="/usr/bin/ssh -oBatchMode=yes -oConnectTimeout=5")
        # An inherited index/worktree override must never touch the code clone.
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                     "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            self.env.pop(name, None)

    def run(self, args, *, input=None, allowed=(0,)):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("status transport deadline")
        process = subprocess.Popen([GIT, *args], stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   start_new_session=True, env=self.env)
        try:
            stdout, stderr = process.communicate(input=input, timeout=remaining)
        except subprocess.TimeoutExpired as exc:
            # Git may have SSH/credential children holding its output pipes.
            # Kill only this transport's new process group, then bound reaping.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate(timeout=2)
            raise TimeoutError("status transport deadline") from exc
        result = subprocess.CompletedProcess([GIT, *args], process.returncode, stdout, stderr)
        if result.returncode not in allowed:
            # No remote URL, credential or custody detail in the diagnostic.
            raise RuntimeError(f"status git operation rc={result.returncode}")
        return result

    def origin(self):
        return self.run(["-C", str(self.repository), "remote", "get-url", "origin"]).stdout.strip()

    def publish(self, directory, ref, latest, transitions):
        origin = self.origin()
        with tempfile.TemporaryDirectory(prefix="status-push-", dir=directory) as tmp:
            bare = str(Path(tmp) / "repo.git")
            self.run(["init", "--bare", "-q", bare])
            git = ["--git-dir=" + bare, "-c", "user.name=JouleWise watchdog",
                   "-c", "user.email=joulewise-watchdog@example.invalid"]
            remote = self.run([*git, "ls-remote", "--exit-code", origin, ref], allowed=(0, 2))
            parents = []
            if remote.returncode == 0:
                self.run([*git, "fetch", "--depth=1", "--no-tags", origin, ref])
                parent = self.run([*git, "rev-parse", "FETCH_HEAD"]).stdout.strip()
                parents = ["-p", parent]
            # The empty index makes each commit an exact, small snapshot.
            for name, data in (("status.json", json.dumps(latest, sort_keys=True) + "\n"),
                               ("transitions.jsonl", "".join(json.dumps(row, sort_keys=True) + "\n"
                                                            for row in transitions))):
                blob = self.run([*git, "hash-object", "-w", "--stdin"], input=data).stdout.strip()
                self.run([*git, "update-index", "--add", "--cacheinfo", "100644", blob, name])
            tree = self.run([*git, "write-tree"]).stdout.strip()
            commit = self.run([*git, "commit-tree", tree, *parents], input="watchdog status\n").stdout.strip()
            # No force: a competing host writer or rejected push stays a failure.
            self.run([*git, "push", origin, commit + ":" + ref])
            return commit

    def read(self, ref):
        origin = self.origin()
        with tempfile.TemporaryDirectory(prefix="status-poll-") as tmp:
            self.run(["init", "--bare", "-q", tmp])
            git = ["--git-dir=" + tmp]
            self.run([*git, "fetch", "--depth=1", "--no-tags", origin, ref])
            return json.loads(self.run([*git, "show", "FETCH_HEAD:status.json"]).stdout)

    def poll(self, ref, cursor=None):
        origin = self.origin()
        with tempfile.TemporaryDirectory(prefix="status-poll-") as tmp:
            self.run(["init", "--bare", "-q", tmp])
            git = ["--git-dir=" + tmp]
            # Only this tiny status history, never main or custody refs.
            self.run([*git, "fetch", "--no-tags", origin, ref])
            head = self.run([*git, "rev-parse", "FETCH_HEAD"]).stdout.strip()
            revisions = ["FETCH_HEAD"]
            if cursor is not None:
                if not isinstance(cursor, str) or not re.fullmatch(r"[0-9a-f]{40,64}", cursor):
                    raise ValueError("invalid Air cursor")
                self.run([*git, "merge-base", "--is-ancestor", cursor, "FETCH_HEAD"])
                revisions.append("^" + cursor)
            commits = self.run([*git, "rev-list", "--reverse", *revisions]).stdout.splitlines()
            events = []
            for commit in commits:
                lines = self.run([*git, "show", commit + ":transitions.jsonl"]).stdout.splitlines()
                events.extend(json.loads(line) for line in lines)
            record = json.loads(self.run([*git, "show", head + ":status.json"]).stdout)
            return record, events, head


class StatusExporter:
    def __init__(self, storage, repository, *, host=None, wall=time.time, transport=GitTransport):
        self.storage = storage
        self.repository = repository
        self.host = host or os.environ.get("MAGISTRATE_WATCHDOG_STATUS_HOST") or socket.gethostname()
        self.ref = status_ref(self.host)
        self.wall = wall
        self.transport = transport
        self.thread = None
        self.thread_lock = threading.Lock()

    def _read(self, name, default=None):
        try:
            value = json.loads(self.storage.read_text(self.storage.root / name))
            return value if isinstance(value, dict) else default
        except (OSError, ValueError):
            return default

    def record(self, state):
        now = self.wall()
        heartbeat = state.get("magistrate_heartbeat") or {}
        heartbeat_age = heartbeat.get("age_s")
        if heartbeat_age is not None:
            heartbeat_age = max(0, heartbeat_age + now - heartbeat.get("observed_epoch_s", now))
        hold = state.get("unsafe_hold") or {}
        word = str(state.get("state", "BOOT"))
        return {"schema": SCHEMA, "host": self.host, "state": word,
                "hold_reason": hold.get("category", word) if word.startswith("HOLD_") or word == "STRANDED" else None,
                "transition_seq": state.get("transition_seq", 0),
                "transition_epoch_s": state.get("transition_epoch_s", now),
                "recorded_epoch_s": now,
                "dwell_s": max(0, now - hold.get("since_epoch_s", state.get("transition_epoch_s", now))),
                "last_heartbeat_age_s": heartbeat_age,
                "heartbeat_stale": bool(heartbeat.get("stale", False)),
                "last_activation_id": state.get("activation_id")}

    def checkpoint(self, state, *, transition=False):
        if self.storage.dry_run:
            return
        record = self.record(state)
        previous = self._read("status.json", {})
        self.storage.atomic_json(self.storage.root / "status.json", record)
        if transition or previous.get("heartbeat_stale") != record["heartbeat_stale"]:
            # Durable outbox preserves every transition across offline periods,
            # rate limiting, crashes, restarts and supervisor replacement.
            name = f"{time.time_ns()}-{uuid.uuid4().hex}.json"
            self.storage.atomic_json(self.storage.root / "status-outbox" / name, record)

    def launch_hold(self):
        receipt = self._read("status-delivery.json", {})
        attempt = self._read("status-attempt.json", {})
        if attempt.get("error"):
            return "status_export: " + str(attempt["error"])
        attempted = attempt.get("attempt_epoch_s", 0)
        if not isinstance(attempted, (int, float)) or not math.isfinite(attempted):
            return "status_export: invalid delivery attempt timestamp"
        if attempt.get("pending") and self.wall() - attempted > TRANSPORT_BUDGET_S + 5:
            return "status_export: delivery worker did not finish within budget"
        delivered = receipt.get("delivered_epoch_s")
        if (receipt.get("ref") != self.ref or not isinstance(delivered, (int, float))
                or isinstance(delivered, bool) or not math.isfinite(delivered)
                or not 0 <= self.wall() - delivered < KEEPALIVE_S):
            return "status_export: acknowledged status absent or stale"
        return None

    def flush(self):
        if self.storage.dry_run:
            return
        root = self.storage.root
        self.storage.mkdir(root)
        descriptor = os.open(self.storage._write_path(root / "status-export.lock"), os.O_CREAT | os.O_RDWR, 0o600)
        try:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return
            now = self.wall()
            attempt = self._read("status-attempt.json", {})
            receipt = self._read("status-delivery.json", {})
            attempted = attempt.get("attempt_epoch_s")
            # A backward wall step never licenses extra attempts. Stay quiet
            # until the persisted attempt is at least a minute in the past.
            if isinstance(attempted, (int, float)) and now - attempted < MIN_PUSH_INTERVAL_S:
                return
            paths = sorted((root / "status-outbox").glob("*.json"))
            delivered = receipt.get("delivered_epoch_s")
            if not paths and receipt.get("ref") == self.ref and isinstance(delivered, (int, float)) and 0 <= now - delivered < KEEPALIVE_DUE_S:
                return
            # A fresh acknowledged receipt still permits admission while its
            # next update is in flight. A previous failure stays latched until
            # success; starting a retry cannot clear it.
            self.storage.atomic_json(root / "status-attempt.json", {
                "attempt_epoch_s": now, "error": attempt.get("error"), "pending": True})
            try:
                latest = self._read("status.json")
                if latest is None:
                    raise ValueError("no local status checkpoint")
                rows = [json.loads(self.storage.read_text(path)) for path in paths]
                commit = self.transport(self.repository).publish(root, self.ref, latest, rows)
                self.storage.atomic_json(root / "status-delivery.json", {
                    "ref": self.ref, "commit": commit, "delivered_epoch_s": self.wall()})
                for path in paths:
                    self.storage.unlink(path)
                self.storage.atomic_json(root / "status-attempt.json", {"attempt_epoch_s": now, "error": None})
            except Exception as exc:
                self.storage.atomic_json(root / "status-attempt.json", {
                    "attempt_epoch_s": now, "error": f"delivery failed: {type(exc).__name__}"})
        finally:
            os.close(descriptor)

    def flush_background(self):
        # No transport or wait on the resident's REQUEST/TERM/KILL path.
        with self.thread_lock:
            if self.thread is None or not self.thread.is_alive():
                self.thread = threading.Thread(target=self.flush, name="watchdog-status-push", daemon=True)
                self.thread.start()

    def finish(self):
        if self.thread is not None:
            self.thread.join(TRANSPORT_BUDGET_S + 1)
        self.flush()


def alarm_reasons(record, host, now):
    """Air-side decision: missing/malformed/stale observations always alarm."""
    try:
        if record["schema"] != SCHEMA or record["host"] != host:
            raise ValueError("identity")
        age = now - record["recorded_epoch_s"]
        if not math.isfinite(age) or age < -5:
            raise ValueError("timestamp")
        word = record["state"]
        healthy = {"ACTIVE", "IDLE", "FENCED", "LAUNCHING", "BACKOFF", "BACKOFF_USAGE",
                   "STOPPED", "STOP_REQUESTED", "STANDDOWN_REQUEST", "STANDDOWN_TERM", "STANDDOWN_KILL"}
        if word not in healthy and not word.startswith("HOLD_") and word not in {"STRANDED", "CLOCK_UNCERTAIN", "NETWORK_UNCERTAIN"}:
            raise ValueError("unknown state")
        if not isinstance(record["heartbeat_stale"], bool):
            raise ValueError("heartbeat status")
        reasons = [word] if word.startswith("HOLD_") or word in {"STRANDED", "CLOCK_UNCERTAIN", "NETWORK_UNCERTAIN"} else []
        if age >= AIR_STALE_S:
            reasons.append("watchdog_status_stale")
        if record["heartbeat_stale"]:
            reasons.append("magistrate_heartbeat_stale")
        return reasons
    except (KeyError, TypeError, ValueError, AttributeError):
        return ["watchdog_status_invalid"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("poll",))
    parser.add_argument("--repository", type=Path, required=True, help="Air code clone whose origin holds status")
    parser.add_argument("--host", required=True)
    parser.add_argument("--cursor-file", type=Path, required=True, help="Air-owned persistent cursor and unacknowledged alarms")
    parser.add_argument("--ack", action="store_true", help="acknowledge previously delivered alarms before this poll")
    args = parser.parse_args(argv)
    try:
        previous = {}
        if args.cursor_file.exists():
            previous = json.loads(args.cursor_file.read_text())
            if previous.get("host") != args.host or not isinstance(previous.get("pending_reasons"), list):
                raise ValueError("Air cursor identity or shape")
        record, events, head = GitTransport(args.repository).poll(status_ref(args.host), previous.get("commit"))
        reasons = alarm_reasons(record, args.host, time.time())
        if "watchdog_status_invalid" in reasons:
            raise ValueError("invalid current status")
        pending = [] if args.ack else previous.get("pending_reasons", [])
        for event in events:
            # Historical transitions are faults when observed, not stale
            # snapshots. Keep them latched even if the latest state recovered.
            observed = alarm_reasons(event, args.host, event.get("recorded_epoch_s"))
            pending.extend("transition:" + reason for reason in observed)
        pending = sorted(set(pending))
        args.cursor_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.cursor_file.with_name("." + args.cursor_file.name + "." + uuid.uuid4().hex)
        descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            with os.fdopen(descriptor, "w") as handle:
                json.dump({"host": args.host, "commit": head, "pending_reasons": pending}, handle, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, args.cursor_file)
            directory = os.open(args.cursor_file.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            temporary.unlink(missing_ok=True)
        reasons = sorted(set(reasons + pending))
    except Exception as exc:
        record, reasons = None, ["watchdog_status_unavailable:" + type(exc).__name__]
    print(json.dumps({"alarm": bool(reasons), "reasons": reasons, "status": record}, sort_keys=True))
    return 3 if reasons else 0


if __name__ == "__main__":
    raise SystemExit(main())
