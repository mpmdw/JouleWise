#!/usr/bin/env python3
"""MBP span watcher in GitHub Actions (RL-173 C; RL-149 §2.8 line 7). Standard library, git and the REST API.

    python3 scripts/mbp_watch.py watch --repo OWNER/REPO --owner LOGIN [--current docs/process/CURRENT.json]
        [--grace-s 1200] [--lookback-s 172800] [--plan-prefix cq-] [--run-url URL] [--dry-run]
    python3 scripts/mbp_watch.py read --repo OWNER/REPO --after-epoch EPOCH [--max-age-s S]

``watch`` runs every 10 minutes in ``.github/workflows/mbp-watch.yml``. It opens one ``mbp-alarm`` issue,
assigned to the repository owner and mentioning them, for each new event:

- ``SPAN_SILENT``: CURRENT.json's armed span has no results ref by its deadline plus the grace (C.1). The
  deadline is ``wait.deadline_epoch_s`` when set, else ``armed.latest_end_epoch_s``.
- ``SPAN_STOP``: a span's results ref records a stop: ``desk-bundles/<plan>``'s ``transition.json`` status
  other than ``CLOSED_OK``, or a ``night-results/<plan>`` result that is not a clean completion.
- ``DESK_HOLD``: ``cadence-desk-final/<plan>``'s verdict holds the next arm.
- ``RESULT_UNREADABLE`` / ``CURRENT_INVALID``: a record it must read is missing or malformed (fail loud).

The issue carries operational codes only (C.2; the repository is public): span id, code, times, ref and
short sha, the run link. Every value is checked against a fixed pattern before it is written. A failure to
read git or the API fails the run, so the arm's read (below) refuses.

``read`` is the arm's check (C.4): the workflow's latest completed run on ``main`` must have succeeded and
have started after ``--after-epoch`` (the previous span's close), and no ``mbp-alarm`` issue may be open.
It needs no token for this public repository (``GH_TOKEN`` is used when set). Exit codes: 0 ok, 2 usage or
API error, 20 no qualifying run (stale), 21 an alarm is open, 22 the latest run did not succeed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

WORKFLOW = "mbp-watch.yml"
LABEL = "mbp-alarm"
PLAN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
CODE_RE = re.compile(r"[A-Z][A-Z0-9_]{0,63}")
LOGIN_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
SHA_RE = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
BUNDLE = "refs/heads/desk-bundles/"
NIGHT = "refs/heads/night-results/"
VERDICT = "refs/heads/cadence-desk-final/"
RESULT_PREFIXES = (BUNDLE, NIGHT)
TRANSITION_STATUSES = {"CLOSED_OK", "STOPPED", "REFUSED", "STRANDED", "CLOSE_UNPROVEN"}
EXIT = {"ok": 0, "usage": 2, "stale": 20, "open_alarm": 21, "failed_run": 22}
MAX_RECORD = 1 << 20


class WatchError(Exception):
    """A read the watcher depends on failed: the run fails, so the arm's read refuses."""


def plan_ok(value):
    return isinstance(value, str) and PLAN_RE.fullmatch(value) is not None and ".." not in value


def code_ok(value):
    return isinstance(value, str) and CODE_RE.fullmatch(value) is not None


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def iso(epoch):
    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- transport -----------------------------------------------------------------------------------

class Git:
    """Read-only remote refs and blobs. Never checks out a results ref."""

    def __init__(self, repository=".", remote="origin", timeout=60):
        self.repository, self.remote, self.timeout = str(repository), remote, timeout

    def _run(self, *args):
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        try:
            proc = subprocess.run(["git", "-C", self.repository, "-c", "gc.auto=0", "-c", "maintenance.auto=false",
                                   *args], capture_output=True, timeout=self.timeout, env=env)
        except (OSError, subprocess.TimeoutExpired):
            raise WatchError("GIT_UNAVAILABLE") from None
        if proc.returncode:
            raise WatchError("GIT_FAILED")
        return proc.stdout

    def refs(self):
        rows = {}
        out = self._run("ls-remote", "--refs", self.remote, BUNDLE + "*", NIGHT + "*", VERDICT + "*")
        for line in out.decode("ascii", "replace").splitlines():
            sha, _, ref = line.partition("\t")
            if SHA_RE.fullmatch(sha) and ref.startswith((BUNDLE, NIGHT, VERDICT)):
                rows[ref] = sha
        return rows

    def fetch(self, shas):
        """One round trip for every tip the watch reads (GitHub serves reachable commits by id)."""
        if shas:
            self._run("fetch", "--quiet", "--no-tags", "--depth=1", self.remote, *sorted(set(shas)))

    def commit_time(self, sha):
        return int(self._run("show", "-s", "--format=%ct", sha).strip() or 0)

    def blob(self, sha, path):
        try:
            data = self._run("show", f"{sha}:{path}")
        except WatchError:
            return None
        return data if len(data) <= MAX_RECORD else None


class Api:
    """GitHub REST with an optional token. ``opener`` is injectable for tests."""

    def __init__(self, repo, token=None, base="https://api.github.com", opener=None, timeout=30):
        if not REPO_RE.fullmatch(repo or ""):
            raise WatchError("BAD_REPO")
        self.repo, self.token, self.base, self.timeout = repo, token, base, timeout
        self.opener = opener or urllib.request.urlopen

    def call(self, method, path, params=None, body=None):
        url = f"{self.base}/repos/{self.repo}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
                   "User-Agent": "joulewise-mbp-watch"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with self.opener(request, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as error:
            if method == "POST" and path == "/labels" and error.code == 422:
                return None  # the label already exists
            raise WatchError(f"API_HTTP_{error.code}") from None
        except (urllib.error.URLError, OSError):
            raise WatchError("API_UNAVAILABLE") from None
        try:
            return json.loads(raw) if raw else None
        except ValueError:
            raise WatchError("API_UNPARSEABLE") from None


# --- the watch -----------------------------------------------------------------------------------

def read_current(path):
    """Return (armed plan, t0, deadline) or None; raise ValueError on a malformed pointer."""
    doc = json.loads(Path(path).read_text())
    if not isinstance(doc, dict) or doc.get("schema") != "joulewise.current_pointer.v1":
        raise ValueError("schema")
    armed = doc.get("armed")
    if armed is None:
        return None
    if not isinstance(armed, dict) or not plan_ok(armed.get("plan_id")):
        raise ValueError("armed")
    t0, latest_end = armed.get("t0_epoch_s"), armed.get("latest_end_epoch_s")
    wait = doc.get("wait") or {}
    deadline = wait.get("deadline_epoch_s") if isinstance(wait, dict) else None
    if deadline is None:
        deadline = latest_end
    if not (number(t0) and number(deadline) and t0 < deadline):
        raise ValueError("times")
    return armed["plan_id"], float(t0), float(deadline)


def bundle_event(git, plan, sha):
    raw = git.blob(sha, "transition.json")
    try:
        doc = json.loads(raw) if raw is not None else None
    except ValueError:
        doc = None
    if not isinstance(doc, dict) or doc.get("plan_id") != plan or doc.get("status") not in TRANSITION_STATUSES:
        return ("RESULT_UNREADABLE", "TRANSITION")
    if doc["status"] != "CLOSED_OK":
        return ("SPAN_STOP", doc["status"])
    return None


def night_event(git, plan, sha):
    raw = git.blob(sha, f"docs/process_traces/night-results/{plan}/result.json")
    try:
        doc = json.loads(raw) if raw is not None else None
    except ValueError:
        doc = None
    if not isinstance(doc, dict):
        return ("RESULT_UNREADABLE", "RESULT_JSON")
    exit_code, fault, outcome = doc.get("chain_exit_code"), doc.get("fault"), doc.get("chain_outcome")
    if fault is True:
        return ("SPAN_STOP", "FAULT")
    if type(exit_code) is int and exit_code != 0:
        return ("SPAN_STOP", f"CHAIN_EXIT_{exit_code}" if 0 < exit_code < 1000 else "CHAIN_EXIT")
    if outcome != "COMPLETE":
        word = outcome if code_ok(outcome) else "UNKNOWN"
        return ("SPAN_STOP", f"OUTCOME_{word}"[:64])
    if exit_code != 0 or fault is not False:
        return ("RESULT_UNREADABLE", "RESULT_FIELDS")
    return None


def verdict_event(git, plan, sha):
    raw = git.blob(sha, "desk_verdict.json")
    try:
        doc = json.loads(raw) if raw is not None else None
    except ValueError:
        doc = None
    if not isinstance(doc, dict) or doc.get("plan_id") != plan or type(doc.get("next_arm_hold")) is not bool:
        return ("RESULT_UNREADABLE", "DESK_VERDICT")
    if doc["next_arm_hold"]:
        codes = sorted({h.get("code") for h in doc.get("holds") or [] if isinstance(h, dict) and code_ok(h.get("code"))})
        return ("DESK_HOLD", codes[0] if len(codes) == 1 else ("MULTIPLE" if codes else "UNNAMED"))
    return None


def events(git, current, now, grace_s, lookback_s, plan_prefix):
    """Each event: dict(code, detail, plan, ref, sha, times). Pure over ``git`` and ``current``."""
    found = []
    refs = git.refs()
    by_plan = {}
    for ref, sha in refs.items():
        prefix = next(p for p in (BUNDLE, NIGHT, VERDICT) if ref.startswith(p))
        plan = ref[len(prefix):]
        if plan_ok(plan):
            by_plan.setdefault(plan, {})[prefix] = (ref, sha)
    armed_plan = current[0] if current else None
    if current:
        plan, t0, deadline = current
        if not any(prefix in by_plan.get(plan, {}) for prefix in RESULT_PREFIXES) and now > deadline + grace_s:
            found.append({"code": "SPAN_SILENT", "detail": "NO_RESULTS_REF", "plan": plan, "ref": None, "sha": None,
                          "times": {"t0": t0, "deadline": deadline, "grace_s": grace_s, "observed": now}})
    watched = {plan: entries for plan, entries in by_plan.items()
               if plan == armed_plan or plan.startswith(plan_prefix)}
    git.fetch([sha for entries in watched.values() for _, sha in entries.values()])
    for plan, entries in sorted(watched.items()):
        for prefix, reader in ((BUNDLE, bundle_event), (NIGHT, night_event), (VERDICT, verdict_event)):
            if prefix not in entries:
                continue
            ref, sha = entries[prefix]
            committed = git.commit_time(sha)
            if plan != armed_plan and now - committed > lookback_s:
                continue
            event = reader(git, plan, sha)
            if event:
                found.append({"code": event[0], "detail": event[1], "plan": plan, "ref": ref, "sha": sha,
                              "times": {"ref_committed": committed, "observed": now}})
    return found


def title(event):
    parts = [LABEL, event["code"], event["plan"], event["detail"]]
    if event["sha"]:
        parts.append(event["sha"][:12])
    return " ".join(parts)


def body(event, owner, run_url):
    for key in ("code", "detail"):
        if not code_ok(event[key]):
            raise WatchError("UNSAFE_FIELD")
    if not plan_ok(event["plan"]) or (event["sha"] and not SHA_RE.fullmatch(event["sha"])):
        raise WatchError("UNSAFE_FIELD")
    lines = [f"@{owner} MBP span alarm (RL-173 C). Operational codes only.", "",
             f"- span: `{event['plan']}`", f"- code: `{event['code']}`", f"- detail: `{event['detail']}`"]
    if event["ref"]:
        if not re.fullmatch(r"refs/heads/[A-Za-z0-9_./-]+|docs/process/CURRENT\.json", event["ref"]):
            raise WatchError("UNSAFE_FIELD")
        lines.append(f"- ref: `{event['ref']}` at `{event['sha'][:12]}`")
    for key, value in sorted(event["times"].items()):
        if not number(value):
            raise WatchError("UNSAFE_FIELD")
        lines.append(f"- {key}: {int(value)} s" if key == "grace_s" else f"- {key}: {iso(value)} ({int(value)})")
    if run_url:
        if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/actions/runs/[0-9]+", run_url):
            raise WatchError("UNSAFE_FIELD")
        lines.append(f"- watcher run: {run_url}")
    lines += ["", "Close this issue once the stop is handled; the arm's read (`scripts/mbp_watch.py read`) "
              "refuses while any `mbp-alarm` issue is open."]
    return "\n".join(lines) + "\n"


def existing_titles(api):
    titles, page = set(), 1
    while True:
        rows = api.call("GET", "/issues", {"labels": LABEL, "state": "all", "per_page": 100, "page": page}) or []
        titles.update(row.get("title") for row in rows if isinstance(row, dict))
        if len(rows) < 100 or page >= 20:
            return titles
        page += 1


def deliver(api, found, owner, run_url, dry_run=False):
    if not LOGIN_RE.fullmatch(owner or ""):
        raise WatchError("BAD_OWNER")
    if not found:
        return []
    seen = existing_titles(api)
    opened = []
    for event in found:
        name = title(event)
        if name in seen:
            continue
        text = body(event, owner, run_url)
        if not dry_run:
            api.call("POST", "/labels", body={"name": LABEL, "color": "b60205",
                                               "description": "MBP span watcher alarm (RL-173 C)"})
            api.call("POST", "/issues", body={"title": name, "body": text, "labels": [LABEL], "assignees": [owner]})
        seen.add(name)
        opened.append(name)
    return opened


def watch(args, git=None, api=None, now=None):
    now = time.time() if now is None else now
    git = git or Git()
    api = api or Api(args.repo, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    found = []
    try:
        current = read_current(args.current)
    except (OSError, ValueError, TypeError):
        current = None
        try:
            digest = hashlib.sha256(Path(args.current).read_bytes()).hexdigest()
        except OSError:
            digest = None
        found.append({"code": "CURRENT_INVALID", "detail": "POINTER", "plan": "current-pointer",
                      "ref": "docs/process/CURRENT.json" if digest else None, "sha": digest, "times": {"observed": now}})
    found += events(git, current, now, args.grace_s, args.lookback_s, args.plan_prefix)
    opened = deliver(api, found, args.owner, args.run_url, args.dry_run)
    armed = f"armed={current[0]} deadline={iso(current[2])}" if current else "armed=none"
    print(f"MBP_WATCH {armed} events={len(found)} opened={len(opened)}")
    for name in opened:
        print(f"OPENED {name}")
    return EXIT["ok"]


# --- the arm's read (C.4) --------------------------------------------------------------------------

def parse_time(value):
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()
    except (TypeError, ValueError):
        return None


def read(args, api=None, now=None):
    now = time.time() if now is None else now
    api = api or Api(args.repo, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    runs = (api.call("GET", f"/actions/workflows/{WORKFLOW}/runs",
                     {"branch": "main", "status": "completed", "per_page": 10}) or {}).get("workflow_runs") or []
    runs = [run for run in runs if isinstance(run, dict) and parse_time(run.get("run_started_at")) is not None]
    if not runs:
        print("MBP_WATCH_READ STALE no completed run")
        return EXIT["stale"]
    latest = max(runs, key=lambda run: parse_time(run["run_started_at"]))
    started = parse_time(latest["run_started_at"])
    run_id = latest.get("id")
    if latest.get("conclusion") != "success":
        print(f"MBP_WATCH_READ FAILED_RUN run={run_id} conclusion={latest.get('conclusion')}")
        return EXIT["failed_run"]
    if started <= args.after_epoch or (args.max_age_s is not None and now - started > args.max_age_s):
        print(f"MBP_WATCH_READ STALE run={run_id} started={iso(started)} after={iso(args.after_epoch)}")
        return EXIT["stale"]
    alarms = api.call("GET", "/issues", {"labels": LABEL, "state": "open", "per_page": 100}) or []
    alarms = [row for row in alarms if isinstance(row, dict) and "pull_request" not in row]
    if alarms:
        print(f"MBP_WATCH_READ OPEN_ALARM count={len(alarms)} first=#{alarms[0].get('number')}")
        return EXIT["open_alarm"]
    print(f"MBP_WATCH_READ OK run={run_id} started={iso(started)} after={iso(args.after_epoch)} open_alarms=0")
    return EXIT["ok"]


def parser():
    top = argparse.ArgumentParser(prog="mbp_watch.py")
    sub = top.add_subparsers(dest="command", required=True)
    w = sub.add_parser("watch")
    w.add_argument("--repo", required=True)
    w.add_argument("--owner", required=True)
    w.add_argument("--current", default="docs/process/CURRENT.json")
    w.add_argument("--grace-s", type=float, default=1200.0)
    w.add_argument("--lookback-s", type=float, default=172800.0)
    w.add_argument("--plan-prefix", default="cq-")
    w.add_argument("--run-url")
    w.add_argument("--dry-run", action="store_true")
    r = sub.add_parser("read")
    r.add_argument("--repo", required=True)
    r.add_argument("--after-epoch", type=float, required=True)
    r.add_argument("--max-age-s", type=float, help="optional: also refuse a run older than this")
    return top


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return watch(args) if args.command == "watch" else read(args)
    except WatchError as error:
        print(f"MBP_WATCH_ERROR {error}", file=sys.stderr)
        return EXIT["usage"]


if __name__ == "__main__":
    sys.exit(main())
