#!/usr/bin/env python3
"""MBP span watcher in GitHub Actions (RL-173 C; RL-149 §2.8 line 7). Standard library, git and the REST API.

Each campaign span declares itself and its close in one append-only log branch, so the watcher does not
depend on a shadow pointer and an obligation can be neither deleted nor quietly rewritten:

    # the lead, once (then protect the branch with the ruleset in docs/ops/MBP-WATCH.md):
    python3 scripts/mbp_watch.py init-log [--remote URL]
    # on the MBP, before the launch (the arm does not proceed if this push fails):
    python3 scripts/mbp_watch.py arm --plan PLAN --t0 EPOCH --deadline EPOCH [--remote URL]
    # on the MBP, in the span's Check (after the receipt):
    python3 scripts/mbp_watch.py close --plan PLAN --status CLOSED_OK|STOPPED|REFUSED|FAULT|STRANDED|CLOSE_UNPROVEN \\
        --close-epoch EPOCH [--remote URL]
    # in Actions, every 10 minutes:
    python3 scripts/mbp_watch.py watch --repo OWNER/REPO --owner LOGIN [--grace-s 1200] [--run-url URL]
    # each arm (C.4):
    python3 scripts/mbp_watch.py read --repo OWNER/REPO --after-epoch EPOCH [--max-age-s 7200]

``refs/heads/span-watch/log`` holds one commit per record, each adding ``arms/<plan>.json`` (plan, attempt,
t0, the runner's deadline) or ``closes/<plan>.json`` (plan, status, close time); operational fields only.
``watch`` re-reads the whole log every run (a commit that changes or removes a file is ``LOG_REWRITTEN``):

- ``SPAN_SILENT``: an arm with no close visible by its deadline + grace (C.1), judged by the later of the
  close's own time and the time of the commit that carries it;
- ``SPAN_STOP``: a close status other than ``CLOSED_OK``;
- ``RESULT_UNREADABLE``: a malformed or rewritten record, or a close without an arm.

The results ref is the log: a controller that pushes desk bundles (PR #800) also pushes ``close``. Desk
holds are the controller's own arm gate (line 9), not this watcher's.

Each event opens one ``mbp-alarm`` issue, assigned to the repository owner with a mention (C.3), keyed by
code, span, detail and the record's commit, so a new record is a new episode and an old one is never
re-filed.
Every word in an issue comes from a closed vocabulary in this file, never from a record (C.2). A failed
listing, fetch, issue read, or an issue creation that GitHub does not confirm, fails the run.

``read`` (C.4): the workflow's latest completed run on ``main`` succeeded, started after ``--after-epoch``
(the previous span's close) and within ``--max-age-s``, and no ``mbp-alarm`` issue is open. Any malformed
API answer is an error, never a pass. Exit codes: 0 ok, 2 usage or API error, 20 no qualifying run,
21 an alarm is open, 22 the latest run did not succeed.
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
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

WORKFLOW = "mbp-watch.yml"
LABEL = "mbp-alarm"
BOT = "github-actions[bot]"  # the workflow's GITHUB_TOKEN files every alarm as this user
PLAN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
LOGIN_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
SHA_RE = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
ARMS = "refs/heads/span-watch/"
ARM_SCHEMA = "joulewise.mbp_watch_arm.v1"
CLOSE_SCHEMA = "joulewise.mbp_watch_close.v1"
CLOSE_STATUSES = ("CLOSED_OK", "STOPPED", "REFUSED", "FAULT", "STRANDED", "CLOSE_UNPROVEN")
EVENT_CODES = ("SPAN_SILENT", "SPAN_STOP", "RESULT_UNREADABLE")
DETAILS = set(CLOSE_STATUSES) | {"NO_RESULTS_REF", "ARM_RECORD", "CLOSE_RECORD", "LOG_REWRITTEN"}
CLOCK_SLACK_S = 300
PROTECTED = ("span-watch/log",)  # the exact branch must carry rules blocking deletion and non-fast-forward
REQUIRED_RULES = {"deletion", "non_fast_forward"}
ATTEMPT_RE = re.compile(r".*-a([1-9][0-9]{0,3})")
MIN_EPOCH, MAX_EPOCH = 1_767_225_600, 1_893_456_000  # 2026-01-01 .. 2030-01-01 UTC
EXIT = {"ok": 0, "usage": 2, "stale": 20, "open_alarm": 21, "failed_run": 22}
MAX_RECORD = 1 << 20
MAX_ISSUE_PAGES = 100
IDENT = {"GIT_AUTHOR_NAME": "JouleWise mbp-watch", "GIT_AUTHOR_EMAIL": "mbp-watch@example.invalid",
         "GIT_COMMITTER_NAME": "JouleWise mbp-watch", "GIT_COMMITTER_EMAIL": "mbp-watch@example.invalid"}


def epoch_ok(value):
    return number(value) and MIN_EPOCH <= value <= MAX_EPOCH


def attempt_of(plan):
    match = ATTEMPT_RE.fullmatch(plan)
    return int(match.group(1)) if match else None


class WatchError(Exception):
    """A read or write the watcher depends on failed: the run fails, so the arm's read refuses."""


def plan_ok(value):
    return isinstance(value, str) and PLAN_RE.fullmatch(value) is not None and ".." not in value \
        and not value.endswith((".", ".lock"))


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def iso(epoch):
    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical(doc):
    return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode() + b"\n"


# --- transport -----------------------------------------------------------------------------------

class Git:
    """Remote refs and blobs. Never checks out a ref."""

    def __init__(self, repository=".", remote="origin", timeout=60):
        self.repository, self.remote, self.timeout = str(repository), remote, timeout

    def run(self, *args, input=None, env=None):
        full_env = dict(os.environ, GIT_TERMINAL_PROMPT="0", **(env or {}))
        try:
            proc = subprocess.run(["git", "-C", self.repository, "-c", "gc.auto=0", "-c", "maintenance.auto=false",
                                   *args], capture_output=True, timeout=self.timeout, env=full_env, input=input)
        except (OSError, subprocess.TimeoutExpired):
            raise WatchError("GIT_UNAVAILABLE") from None
        if proc.returncode:
            raise WatchError("GIT_FAILED")
        return proc.stdout

    def refs(self):
        rows = {}
        out = self.run("ls-remote", "--refs", self.remote, ARMS + "*")
        for line in out.decode("ascii", "replace").splitlines():
            sha, _, ref = line.partition("\t")
            if not SHA_RE.fullmatch(sha) or not ref.startswith(ARMS):
                raise WatchError("GIT_INVALID_REFS")
            rows[ref] = sha
        return rows



    def blob(self, sha, path):
        """The blob's bytes, or None when the tree has no such regular file. A git failure raises."""
        listing = self.run("ls-tree", "-z", sha, "--", path)
        if not listing:
            return None
        header = listing.split(b"\t", 1)[0].split()
        if len(header) != 3 or header[1] != b"blob" or header[0] not in (b"100644", b"100755"):
            return None
        data = self.run("cat-file", "blob", header[2].decode("ascii"))
        return data if len(data) <= MAX_RECORD else None


class Api:
    """GitHub REST with an optional token. ``opener`` is injectable for tests."""

    def __init__(self, repo, token=None, base="https://api.github.com", opener=None, timeout=30):
        if not REPO_RE.fullmatch(repo or ""):
            raise WatchError("BAD_REPO")
        self.repo, self.token, self.base, self.timeout = repo, token, base, timeout
        self.opener = opener or urllib.request.urlopen

    def call(self, method, path, params=None, body=None, allow_422=False):
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
            if allow_422 and error.code == 422:
                return None
            raise WatchError(f"API_HTTP_{error.code}") from None
        except (urllib.error.URLError, OSError):
            raise WatchError("API_UNAVAILABLE") from None
        try:
            return json.loads(raw) if raw else None
        except ValueError:
            raise WatchError("API_UNPARSEABLE") from None


# --- the MBP side: the append-only span log ----------------------------------------------------------
#
# One branch, refs/heads/span-watch/log, protected by a ruleset (no deletion, no non-fast-forward). Each
# arm and each close is one commit that ADDS one file: arms/<plan>.json or closes/<plan>.json. The watch
# re-reads the whole history every run and alarms on any commit that modifies or deletes a file, so an
# obligation can neither be deleted nor quietly rewritten, and the close's publication time is the
# commit's own time.

LOG_REF = "refs/heads/span-watch/log"
LOG_BRANCH = "span-watch/log"
LOG_ROOT_FILE = "README"
LOG_PATH_RE = re.compile(r"(arms|closes)/([A-Za-z0-9][A-Za-z0-9_.-]{0,127})\.json")


def _remote_url(repository, remote):
    if remote:
        return remote
    try:
        return subprocess.run(["git", "-C", str(repository), "remote", "get-url", "origin"], capture_output=True,
                              check=True, timeout=30).stdout.decode().strip()
    except (OSError, subprocess.SubprocessError):
        raise WatchError("NO_REMOTE") from None


def _scratch_repo(tmp, remote, timeout=60):
    repo = Path(tmp) / "r.git"
    try:
        subprocess.run(["git", "init", "--bare", "-q", str(repo)], check=True, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        raise WatchError("GIT_UNAVAILABLE") from None
    return Git(repo, remote=remote, timeout=timeout)


def _append(remote, path, data, check=None, tries=3):
    """Add one new file to the log as one fast-forward commit. Identical bytes already there: no-op."""
    for _ in range(tries):
        with tempfile.TemporaryDirectory(prefix="mbp-watch-") as tmp:
            git = _scratch_repo(tmp, remote)
            git.run("fetch", "--quiet", "--no-tags", "--depth=1", remote, LOG_REF)
            parent = git.run("rev-parse", "FETCH_HEAD").decode().strip()
            existing = git.blob(parent, path)
            if existing is not None:
                if existing == data:
                    return parent  # the same record is already published (a retry after a lost acknowledgement)
                raise WatchError("RECORD_EXISTS")
            if check:
                check(git, parent)
            git.run("read-tree", parent)
            blob = git.run("hash-object", "-w", "--stdin", input=data).decode().strip()
            git.run("update-index", "--add", "--cacheinfo", "100644", blob, path)
            tree = git.run("write-tree").decode().strip()
            commit = git.run("commit-tree", tree, "-p", parent, input=f"span-watch {path}\n".encode(),
                             env=IDENT).decode().strip()
            try:
                git.run("push", "--quiet", remote, f"{commit}:{LOG_REF}")  # never forced
                return commit
            except WatchError:
                continue  # another record landed first: re-read and try again
    raise WatchError("LOG_PUSH_FAILED")


def init_log(args):
    """The lead, once: create the log's root commit (refused if the log exists)."""
    remote = _remote_url(args.repo_dir, args.remote)
    with tempfile.TemporaryDirectory(prefix="mbp-watch-") as tmp:
        git = _scratch_repo(tmp, remote)
        blob = git.run("hash-object", "-w", "--stdin",
                       input=b"Append-only span log for scripts/mbp_watch.py (RL-173 C). Do not edit.\n").decode().strip()
        tree = git.run("mktree", input=f"100644 blob {blob}\t{LOG_ROOT_FILE}\n".encode()).decode().strip()
        commit = git.run("commit-tree", tree, input=b"span-watch log\n", env=IDENT).decode().strip()
        git.run("push", "--quiet", remote, f"{commit}:{LOG_REF}")
    print(f"MBP_WATCH_INIT_LOG commit={commit}")
    return EXIT["ok"]


def arm(args):
    """Before the launch. The plan id must end -a<N>; a different arm for the same plan id is refused."""
    if not plan_ok(args.plan) or attempt_of(args.plan) is None \
            or not (epoch_ok(args.t0) and epoch_ok(args.deadline) and args.t0 < args.deadline):
        raise WatchError("BAD_ARM")
    record = {"schema": ARM_SCHEMA, "plan_id": args.plan, "attempt": attempt_of(args.plan), "t0_epoch_s": args.t0,
              "deadline_epoch_s": args.deadline}
    commit = _append(_remote_url(args.repo_dir, args.remote), f"arms/{args.plan}.json", canonical(record))
    print(f"MBP_WATCH_ARM plan={args.plan} t0={iso(args.t0)} deadline={iso(args.deadline)} commit={commit}")
    return EXIT["ok"]


def close(args, now=None):
    """In the Check. Refused without an arm, before the arm's t0, more than 300 s ahead, or twice."""
    now = time.time() if now is None else now
    if not plan_ok(args.plan) or args.status not in CLOSE_STATUSES or not epoch_ok(args.close_epoch) \
            or args.close_epoch > now + CLOCK_SLACK_S:
        raise WatchError("BAD_CLOSE")
    record = {"schema": CLOSE_SCHEMA, "plan_id": args.plan, "status": args.status, "close_epoch_s": args.close_epoch}

    def chronology(git, parent):
        times = _arm_times(_json(git.blob(parent, f"arms/{args.plan}.json")), args.plan)
        if times is None:
            raise WatchError("NOT_ARMED")
        if args.close_epoch < times[0]:
            raise WatchError("CLOSE_BEFORE_ARM")

    commit = _append(_remote_url(args.repo_dir, args.remote), f"closes/{args.plan}.json", canonical(record),
                     check=chronology)
    print(f"MBP_WATCH_CLOSE plan={args.plan} status={args.status} commit={commit}")
    return EXIT["ok"]


# --- the watch -----------------------------------------------------------------------------------

def _json(raw):
    try:
        doc = json.loads(raw) if raw is not None else None
    except (ValueError, RecursionError):
        return None
    return doc if isinstance(doc, dict) else None


def _arm_times(doc, plan):
    """(t0, deadline, attempt) of a valid arm record, else None."""
    if not doc or doc.get("schema") != ARM_SCHEMA or doc.get("plan_id") != plan \
            or doc.get("attempt") != attempt_of(plan) or attempt_of(plan) is None:
        return None
    t0, deadline = doc.get("t0_epoch_s"), doc.get("deadline_epoch_s")
    if not (epoch_ok(t0) and epoch_ok(deadline) and t0 < deadline):
        return None
    return float(t0), float(deadline), doc["attempt"]


def read_log(git):
    """Walk the whole log. Returns (records, problems, tip): records maps (kind, plan) to
    (bytes, commit, commit time); problems lists (detail, commit) for any commit that is not one addition."""
    tip = git.refs().get(LOG_REF)
    if tip is None:
        raise WatchError("LOG_MISSING")
    git.run("fetch", "--quiet", "--no-tags", git.remote, f"+{LOG_REF}:refs/mbp-watch/log")
    commits = git.run("rev-list", "--reverse", "--parents", "--format=%ct", tip).decode().split("\n")
    records, problems = {}, []
    rows = [line for line in commits if line and not line.startswith("commit ")]
    heads = [line.split()[1:] for line in commits if line.startswith("commit ")]
    for (sha, *parents), stamp in zip(heads, rows):
        when = float(stamp)
        if not parents:
            names = git.run("ls-tree", "--name-only", sha).decode().split()
            if names != [LOG_ROOT_FILE]:
                problems.append(("LOG_REWRITTEN", sha))
            continue
        if len(parents) != 1:
            problems.append(("LOG_REWRITTEN", sha))
            continue
        changes = git.run("diff-tree", "--no-commit-id", "-r", "--name-status", "--no-renames", parents[0], sha)
        changes = [line.split("\t") for line in changes.decode().splitlines() if line]
        match = LOG_PATH_RE.fullmatch(changes[0][1]) if len(changes) == 1 and len(changes[0]) == 2 else None
        if not match or changes[0][0] != "A":
            problems.append(("LOG_REWRITTEN", sha))
            continue
        kind = "arm" if match.group(1) == "arms" else "close"
        records[(kind, match.group(2))] = (git.blob(sha, changes[0][1]), sha, when)
    return records, problems, tip


def read_close(raw, plan, t0, now):
    """'invalid' or (status word, close epoch)."""
    doc = _json(raw)
    if not doc or doc.get("schema") != CLOSE_SCHEMA or doc.get("plan_id") != plan \
            or doc.get("status") not in CLOSE_STATUSES or not epoch_ok(doc.get("close_epoch_s")) \
            or doc["close_epoch_s"] < t0 or doc["close_epoch_s"] > now + CLOCK_SLACK_S:
        return "invalid"
    return doc["status"], doc["close_epoch_s"]


def event(code, detail, plan, ref, sha, **times):
    return {"code": code, "detail": detail, "plan": plan, "ref": ref, "sha": sha, "times": times}


def events(git, now, grace_s):
    """Every alarm the log implies. The log is append-only and protected, so no obligation, close or stop
    in it can disappear: there is no age limit and nothing else to retain."""
    records, problems, _ = read_log(git)
    found = [event("RESULT_UNREADABLE", detail, "span-watch-log", LOG_REF, sha, observed=now)
             for detail, sha in problems]
    for plan in sorted({plan for _, plan in records}):
        if ("arm", plan) not in records:
            raw, sha, _ = records[("close", plan)]
            found.append(event("RESULT_UNREADABLE", "CLOSE_RECORD", plan, LOG_REF, sha, observed=now))
            continue
        raw, arm_sha, _ = records[("arm", plan)]
        arm_times = _arm_times(_json(raw), plan)
        if arm_times is None:
            found.append(event("RESULT_UNREADABLE", "ARM_RECORD", plan, LOG_REF, arm_sha, observed=now))
            continue
        visible = None
        if ("close", plan) in records:
            raw, sha, published = records[("close", plan)]
            closed = read_close(raw, plan, arm_times[0], now)
            if closed == "invalid":
                found.append(event("RESULT_UNREADABLE", "CLOSE_RECORD", plan, LOG_REF, sha, observed=now))
            else:
                visible = max(closed[1], published)  # finished, and committed for publication, no earlier
                if closed[0] != "CLOSED_OK":
                    found.append(event("SPAN_STOP", closed[0], plan, LOG_REF, sha, t0=arm_times[0], observed=now))
        limit = arm_times[1] + grace_s
        # Silence now, or a silence that ended between two polls (the close became visible after the limit).
        if (visible is None and now > limit) or (visible is not None and visible > limit):
            found.append(event("SPAN_SILENT", "NO_RESULTS_REF", plan, LOG_REF, arm_sha, t0=arm_times[0],
                               deadline=arm_times[1], grace_s=grace_s, observed=now))
    return found


def key(event_):
    return f"{event_['code']}:{event_['plan']}:{event_['detail']}:{event_['sha']}"


def title(event_):
    return f"{LABEL} {event_['code']} {event_['plan']} {event_['detail']} {event_['sha'][:12]}"


def body(event_, owner, run_url):
    """Only closed-vocabulary words, a pattern-checked span id, a ref, a sha, numbers and the run link."""
    if event_["code"] not in EVENT_CODES or event_["detail"] not in DETAILS or not plan_ok(event_["plan"]) \
            or not SHA_RE.fullmatch(event_["sha"] or "") \
            or event_["ref"] != LOG_REF:
        raise WatchError("UNSAFE_FIELD")
    lines = [f"@{owner} MBP span alarm (RL-173 C). Operational codes only.", "",
             f"- span: `{event_['plan']}`", f"- code: `{event_['code']}`", f"- detail: `{event_['detail']}`",
             f"- ref: `{event_['ref']}`, record `{event_['sha'][:12]}`"]
    for name, value in sorted(event_["times"].items()):
        if name not in ("t0", "deadline", "grace_s", "observed") or not number(value):
            raise WatchError("UNSAFE_FIELD")
        lines.append(f"- {name}: {int(value)} s" if name == "grace_s" else f"- {name}: {iso(value)} ({int(value)})")
    if run_url:
        if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/actions/runs/[0-9]+", run_url):
            raise WatchError("UNSAFE_FIELD")
        lines.append(f"- watcher run: {run_url}")
    lines += ["", "Closing this issue is the lead's acknowledgement that the event is handled; the arm's read "
              "(`scripts/mbp_watch.py read`) refuses while any `mbp-alarm` issue is open.", "",
              f"<!-- mbp-watch-key: {key(event_)} -->"]
    return "\n".join(lines) + "\n"


KEY_RE = re.compile(r"<!-- mbp-watch-key: ([A-Za-z0-9_.:-]+) -->")


def existing_keys(api):
    """Every filed event key -> its issue (open or closed)."""
    keys = {}
    for page in range(1, MAX_ISSUE_PAGES + 1):
        # By creator, not by label: an issue GitHub created without the label is still found and repaired.
        rows = api.call("GET", "/issues", {"creator": BOT, "state": "all", "per_page": 100, "page": page})
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise WatchError("API_SHAPE_ISSUES")
        for row in rows:
            match = KEY_RE.search(row.get("body") or "")
            if match:
                keys.setdefault(match.group(1), row)
        if len(rows) < 100:
            return keys
    raise WatchError("ISSUE_LIST_TOO_LONG")


def delivered(issue, owner):
    labels = [row.get("name") for row in issue.get("labels") or [] if isinstance(row, dict)]
    assignees = [row.get("login") for row in issue.get("assignees") or [] if isinstance(row, dict)]
    return type(issue.get("number")) is int and LABEL in labels and owner in assignees


def check_rulesets(api):
    """The span log branch itself must carry active rules blocking deletion and non-fast-forward updates.
    The query names the real branch, so the answer covers exactly the ref the obligations live on."""
    for branch in PROTECTED:
        rules = api.call("GET", f"/rules/branches/{branch}")
        if not isinstance(rules, list) or not all(isinstance(rule, dict) for rule in rules):
            raise WatchError("API_SHAPE_RULES")
        if not REQUIRED_RULES <= {rule.get("type") for rule in rules}:
            raise WatchError("RULESET_MISSING_SPAN_LOG")


def ensure_label(api):
    api.call("POST", "/labels", body={"name": LABEL, "color": "b60205",
                                      "description": "MBP span watcher alarm (RL-173 C)"}, allow_422=True)
    label = api.call("GET", f"/labels/{LABEL}")
    if not isinstance(label, dict) or label.get("name") != LABEL:
        raise WatchError("LABEL_MISSING")


def deliver(api, found, owner, run_url, dry_run=False):
    if not LOGIN_RE.fullmatch(owner or ""):
        raise WatchError("BAD_OWNER")
    if not found:
        return []
    seen = existing_keys(api)
    opened = []
    for event_ in found:
        issue = seen.get(key(event_))
        if issue is not None:
            # Filed before. An open issue whose delivery was never confirmed is repaired and re-checked.
            if issue.get("state") == "open" and not delivered(issue, owner) and not dry_run:
                ensure_label(api)
                fixed = api.call("PATCH", f"/issues/{issue['number']}", body={"labels": [LABEL],
                                                                            "assignees": [owner]})
                if not isinstance(fixed, dict) or not delivered(fixed, owner):
                    raise WatchError("DELIVERY_UNVERIFIED")
            continue
        text = body(event_, owner, run_url)
        if not dry_run:
            ensure_label(api)
            made = api.call("POST", "/issues", body={"title": title(event_), "body": text, "labels": [LABEL],
                                                     "assignees": [owner]})
            if not isinstance(made, dict) or not delivered(made, owner):
                raise WatchError("DELIVERY_UNVERIFIED")
            seen[key(event_)] = made
        opened.append(title(event_))
    return opened


def watch(args, git=None, api=None, now=None):
    now = time.time() if now is None else now
    git = git or Git()
    api = api or Api(args.repo, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    check_rulesets(api)
    found = events(git, now, args.grace_s)
    opened = deliver(api, found, args.owner, args.run_url, args.dry_run)
    print(f"MBP_WATCH observed={iso(now)} events={len(found)} opened={len(opened)}")
    for name in opened:
        print(f"OPENED {name}")
    return EXIT["ok"]


# --- the arm's read (C.4) --------------------------------------------------------------------------

def parse_time(value):
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp()
    except (TypeError, ValueError):
        return None


RUN_WINDOW_S = 86400
MAX_RUN_PAGES = 10


def read(args, api=None, now=None):
    """Every completed run on ``main`` created since a day before the later of ``--after-epoch`` and now minus
    ``--max-age-s`` is enumerated (all pages,
    checked against ``total_count``); the latest is the most recently started execution among them (a re-run
    attempt counts with its own start; ties by ``run_number`` then ``run_attempt``). A re-run of a run created
    earlier than that window is outside the rule. A start up to 300 s in the future is clock skew; more is an
    error. Every run must be well formed: a malformed answer is an error, never a pass.
    """
    now = time.time() if now is None else now
    api = api or Api(args.repo, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    floor = max(args.after_epoch, now - args.max_age_s) if args.max_age_s is not None else args.after_epoch
    since = dt.datetime.fromtimestamp(floor - RUN_WINDOW_S, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    runs = []
    for page in range(1, MAX_RUN_PAGES + 1):
        answer = api.call("GET", f"/actions/workflows/{WORKFLOW}/runs",
                          {"branch": "main", "status": "completed", "created": f">={since}", "per_page": 100,
                           "page": page})
        if not isinstance(answer, dict) or not isinstance(answer.get("workflow_runs"), list) \
                or type(answer.get("total_count")) is not int:
            raise WatchError("API_SHAPE_RUNS")
        runs += answer["workflow_runs"]
        if len(answer["workflow_runs"]) < 100 or len(runs) >= answer["total_count"]:
            break
    else:
        raise WatchError("TOO_MANY_RUNS")
    if len(runs) != answer["total_count"]:
        raise WatchError("API_SHAPE_RUNS")
    for run in runs:
        if not isinstance(run, dict) or type(run.get("run_number")) is not int or type(run.get("id")) is not int \
                or parse_time(run.get("run_started_at")) is None or run.get("status") != "completed" \
                or not isinstance(run.get("conclusion"), str) or type(run.get("run_attempt")) is not int \
                or run["run_attempt"] < 1:
            raise WatchError("API_SHAPE_RUNS")
    if not runs:
        print("MBP_WATCH_READ STALE no completed run")
        return EXIT["stale"]
    latest = max(runs, key=lambda run: (parse_time(run["run_started_at"]), run["run_number"], run["run_attempt"]))
    started = parse_time(latest["run_started_at"])
    if started > now + CLOCK_SLACK_S:
        raise WatchError("RUN_IN_FUTURE")
    if latest["conclusion"] != "success":
        conclusion = latest["conclusion"] if re.fullmatch(r"[a-z_]{1,20}", latest["conclusion"]) else "other"
        print(f"MBP_WATCH_READ FAILED_RUN run={latest['id']} conclusion={conclusion}")
        return EXIT["failed_run"]
    if started <= args.after_epoch or (args.max_age_s is not None and now - started > args.max_age_s):
        print(f"MBP_WATCH_READ STALE run={latest['id']} started={iso(started)} after={iso(args.after_epoch)}")
        return EXIT["stale"]
    alarms = api.call("GET", "/issues", {"labels": LABEL, "state": "open", "per_page": 100})
    if not isinstance(alarms, list) or not all(isinstance(row, dict) for row in alarms):
        raise WatchError("API_SHAPE_ISSUES")
    if alarms:
        first = alarms[0].get("number")
        print(f"MBP_WATCH_READ OPEN_ALARM count={len(alarms)} first=#{first if type(first) is int else '?'}")
        return EXIT["open_alarm"]
    print(f"MBP_WATCH_READ OK run={latest['id']} started={iso(started)} after={iso(args.after_epoch)} open_alarms=0")
    return EXIT["ok"]


# --- the lead's notification on the Air (C.3) -------------------------------------------------------

DEFAULT_POLL_STATE = Path.home() / "Library/Application Support/JouleWise/air-watch/mbp-alarm-state.json"


def alarm_poll(state_path, notify, api):
    """Notify once per open ``mbp-alarm`` issue number (all pages). ``notify`` must return True for the
    issue to be acknowledged; any other result is retried on the next poll."""
    rows = []
    for page in range(1, MAX_ISSUE_PAGES + 1):
        batch = api.call("GET", "/issues", {"labels": LABEL, "state": "open", "per_page": 100, "page": page})
        if not isinstance(batch, list) or not all(isinstance(row, dict) for row in batch):
            raise WatchError("API_SHAPE_ISSUES")
        rows += batch
        if len(batch) < 100:
            break
    else:
        raise WatchError("ISSUE_LIST_TOO_LONG")
    try:
        seen = set(json.loads(Path(state_path).read_text()).get("notified", []))
    except (OSError, ValueError, AttributeError):
        seen = set()
    lines = []
    for row in rows:
        number_ = row.get("number")
        if type(number_) is not int or number_ in seen:
            continue
        match = KEY_RE.search(row.get("body") or "")
        parts = match.group(1).split(":") if match else []
        code = parts[0] if parts and parts[0] in EVENT_CODES else "UNKNOWN"
        plan = parts[1] if len(parts) > 1 and plan_ok(parts[1]) else "unknown"
        # The notifier shows level, code and one subject token: the subject carries span, issue and code.
        line = (f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} ALARM MBP_ALARM "
                f"issue-{number_}/{code}/{plan}")  # the notifier keeps 80 characters: identity first
        if notify(line) is True:  # only a confirmed notification is acknowledged; a failure is retried
            seen.add(number_)
        lines.append(line)
    Path(state_path).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(state_path) + ".tmp")
    tmp.write_text(json.dumps({"notified": sorted(seen)}))
    os.replace(tmp, state_path)
    return lines


def _finite(minimum):
    def parse(text):
        try:
            value = float(text)
        except ValueError:
            raise argparse.ArgumentTypeError("not a number") from None
        if not math.isfinite(value) or value < minimum:
            raise argparse.ArgumentTypeError(f"must be finite and at least {minimum}")
        return value
    return parse


def parser():
    top = argparse.ArgumentParser(prog="mbp_watch.py")
    sub = top.add_subparsers(dest="command", required=True)
    a = sub.add_parser("arm")
    a.add_argument("--plan", required=True)
    a.add_argument("--t0", type=_finite(MIN_EPOCH), required=True)
    a.add_argument("--deadline", type=_finite(MIN_EPOCH), required=True, help="the runner's deadline (epoch)")
    c = sub.add_parser("close")
    c.add_argument("--plan", required=True)
    c.add_argument("--status", required=True, choices=CLOSE_STATUSES)
    c.add_argument("--close-epoch", type=_finite(MIN_EPOCH), required=True)
    i = sub.add_parser("init-log")
    for p in (a, c, i):
        p.add_argument("--remote", help="push URL (default: origin of --repo-dir)")
        p.add_argument("--repo-dir", default=".")
    w = sub.add_parser("watch")
    w.add_argument("--repo", required=True)
    w.add_argument("--owner", required=True)
    w.add_argument("--grace-s", type=_finite(0), default=1200.0)
    w.add_argument("--run-url")
    w.add_argument("--dry-run", action="store_true")
    r = sub.add_parser("read")
    r.add_argument("--repo", required=True)
    r.add_argument("--after-epoch", type=_finite(MIN_EPOCH), required=True)
    r.add_argument("--max-age-s", type=_finite(1), default=7200.0)
    return top


def main(argv=None):
    args = parser().parse_args(argv)
    commands = {"init-log": init_log, "arm": arm, "close": close, "watch": watch, "read": read}
    try:
        return commands[args.command](args)
    except WatchError as error:
        print(f"MBP_WATCH_ERROR {error}", file=sys.stderr)
        return EXIT["usage"]


if __name__ == "__main__":
    sys.exit(main())
