#!/usr/bin/env python3
"""MBP span watcher in GitHub Actions (RL-173 C; RL-149 §2.8 line 7). Standard library, git and the REST API.

Each campaign span declares itself and its close on a durable, create-only ref, so the watcher does not
depend on a shadow pointer and an obligation cannot be erased by a later commit:

    # on the MBP, before the launch (the arm does not proceed if this push fails):
    python3 scripts/mbp_watch.py arm --plan PLAN --t0 EPOCH --deadline EPOCH [--remote URL]
    # on the MBP, in the span's Check (after the receipt):
    python3 scripts/mbp_watch.py close --plan PLAN --status CLOSED_OK|STOPPED|REFUSED|FAULT|STRANDED|CLOSE_UNPROVEN \\
        --close-epoch EPOCH [--remote URL]
    # in Actions, every 10 minutes:
    python3 scripts/mbp_watch.py watch --repo OWNER/REPO --owner LOGIN [--grace-s 1200] [--run-url URL]
    # each arm (C.4):
    python3 scripts/mbp_watch.py read --repo OWNER/REPO --after-epoch EPOCH [--max-age-s 7200]

``arm`` pushes a parentless commit to ``refs/heads/span-watch/<plan>`` holding ``arm.json`` (plan, t0, the
runner's deadline). ``close`` adds ``close.json`` (plan, status, close time) as a fast-forward child. Both
carry operational fields only. ``watch`` reads every ``span-watch/*`` ref live (``git ls-remote`` and one
fetch), and the ``desk-bundles/*`` and ``cadence-desk-final/*`` refs of the PR #800 controller and the desk:

- ``SPAN_SILENT``: an armed span with no close record and no bound bundle after its deadline + grace (C.1);
- ``SPAN_STOP``: a close record or bound bundle status other than ``CLOSED_OK``;
- ``DESK_HOLD``: a verdict that holds the next arm;
- ``RESULT_UNREADABLE``: an arm, close, transition or verdict record that is malformed or not bound to the
  arm (a bundle whose ``t0_epoch`` is outside [arm t0 - 900 s, arm deadline]).

Each event opens one ``mbp-alarm`` issue, assigned to the repository owner with a mention (C.3), keyed by
code, span, detail and the ref's commit, so a new commit is a new episode and an old one is never re-filed.
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
PLAN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
LOGIN_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
SHA_RE = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
ARMS = "refs/heads/span-watch/"
BUNDLE = "refs/heads/desk-bundles/"
VERDICT = "refs/heads/cadence-desk-final/"
ARM_SCHEMA = "joulewise.mbp_watch_arm.v1"
CLOSE_SCHEMA = "joulewise.mbp_watch_close.v1"
TRANSITION_SCHEMA = "joulewise.cadence_controller_transition.v1"
CLOSE_STATUSES = ("CLOSED_OK", "STOPPED", "REFUSED", "FAULT", "STRANDED", "CLOSE_UNPROVEN")
TRANSITION_STATUSES = ("CLOSED_OK", "STOPPED", "REFUSED", "STRANDED", "CLOSE_UNPROVEN")
# cadence_desk_format.md section 3, "Codes" (PR #800/#799). Anything else prints as UNKNOWN_HOLD.
HOLD_CODES = ("DESK_DENIED_CONTENT", "DESK_UNAUTHENTICATED", "DESK_IDENTITY", "DESK_ROSTER", "DESK_NO_LEG_ROWS",
              "DESK_DUPLICATE", "DESK_ATTEMPTS", "DESK_SCHEMA", "DESK_FEED_PROOF", "DESK_REFUSAL", "DESK_ERROR",
              "REFUSAL", "INSTRUMENT_FAULT", "CONTAMINATED_REDOS", "LEG_OVERTIME", "HAND_TABLE_DISAGREES",
              "HAND_TABLE_INVALID")
EVENT_CODES = ("SPAN_SILENT", "SPAN_STOP", "DESK_HOLD", "RESULT_UNREADABLE")
DETAILS = set(CLOSE_STATUSES) | set(HOLD_CODES) | {
    "NO_RESULTS_REF", "UNKNOWN_HOLD", "MULTIPLE", "UNNAMED", "ARM_RECORD", "CLOSE_RECORD", "TRANSITION",
    "TRANSITION_MISBOUND", "DESK_VERDICT"}


def epoch_ok(value):
    return number(value) and MIN_EPOCH <= value <= MAX_EPOCH


def attempt_of(plan):
    match = ATTEMPT_RE.fullmatch(plan)
    return int(match.group(1)) if match else None
CLOCK_SLACK_S = 300
PROTECTED = ("span-watch", "desk-bundles")  # each needs a ruleset blocking deletion and non-fast-forward
REQUIRED_RULES = {"deletion", "non_fast_forward"}
ATTEMPT_RE = re.compile(r".*-a([1-9][0-9]{0,3})")
MIN_EPOCH, MAX_EPOCH = 1_767_225_600, 1_893_456_000  # 2026-01-01 .. 2030-01-01 UTC
EXIT = {"ok": 0, "usage": 2, "stale": 20, "open_alarm": 21, "failed_run": 22}
MAX_RECORD = 1 << 20
MAX_ISSUE_PAGES = 100
IDENT = {"GIT_AUTHOR_NAME": "JouleWise mbp-watch", "GIT_AUTHOR_EMAIL": "mbp-watch@example.invalid",
         "GIT_COMMITTER_NAME": "JouleWise mbp-watch", "GIT_COMMITTER_EMAIL": "mbp-watch@example.invalid"}


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
        out = self.run("ls-remote", "--refs", self.remote, ARMS + "*", BUNDLE + "*", VERDICT + "*")
        for line in out.decode("ascii", "replace").splitlines():
            sha, _, ref = line.partition("\t")
            if not SHA_RE.fullmatch(sha) or not ref.startswith((ARMS, BUNDLE, VERDICT)):
                raise WatchError("GIT_INVALID_REFS")
            rows[ref] = sha
        return rows

    def fetch(self, shas):
        """One round trip for every tip the watch reads (GitHub serves advertised tips by id)."""
        if shas:
            self.run("fetch", "--quiet", "--no-tags", "--depth=1", self.remote, *sorted(set(shas)))

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


# --- the MBP side: arm and close records -----------------------------------------------------------

def _remote_url(repository, remote):
    if remote:
        return remote
    try:
        return subprocess.run(["git", "-C", str(repository), "remote", "get-url", "origin"], capture_output=True,
                              check=True, timeout=30).stdout.decode().strip()
    except (OSError, subprocess.SubprocessError):
        raise WatchError("NO_REMOTE") from None


def _publish(remote, plan, files, child=False, timeout=60):
    """Push a commit holding ``files`` to span-watch/<plan>: parentless (create-only) or a child of the tip."""
    ref = ARMS + plan
    with tempfile.TemporaryDirectory(prefix="mbp-watch-") as tmp:
        repo = Path(tmp) / "r.git"
        try:
            subprocess.run(["git", "init", "--bare", "-q", str(repo)], check=True, capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            raise WatchError("GIT_UNAVAILABLE") from None
        git = Git(repo, remote=remote, timeout=timeout)
        parents = []
        if child:
            git.run("fetch", "--quiet", "--no-tags", "--depth=1", remote, ref)
            parent = git.run("rev-parse", "FETCH_HEAD").decode().strip()
            existing = git.blob(parent, "arm.json")
            if existing is None or git.blob(parent, "close.json") is not None:
                raise WatchError("NOT_ARMED_OR_ALREADY_CLOSED")
            arm_times = _arm_times(_json(existing), plan)
            close_doc = _json(files.get("close.json"))
            if arm_times is None or close_doc is None or close_doc["close_epoch_s"] < arm_times[0]:
                raise WatchError("CLOSE_BEFORE_ARM")
            files = {"arm.json": existing, **files}
            parents = ["-p", parent]
        entries = b""
        for name in sorted(files):
            blob = git.run("hash-object", "-w", "--stdin", input=files[name]).decode().strip()
            entries += f"100644 blob {blob}\t{name}\n".encode()
        tree = git.run("mktree", input=entries).decode().strip()
        commit = git.run("commit-tree", tree, *parents, input=f"span-watch {plan}\n".encode(), env=IDENT)
        commit = commit.decode().strip()
        # No force: a second arm for the same plan, or a close on a moved tip, is rejected by the remote.
        git.run("push", "--quiet", remote, f"{commit}:{ref}")
        return commit


def arm(args):
    """Create-only. Re-publishing byte-identical content is an idempotent no-op; any other arm of the plan id
    is refused by the remote (no force), and the ruleset forbids deleting or rewriting the ref."""
    if not plan_ok(args.plan) or attempt_of(args.plan) is None \
            or not (epoch_ok(args.t0) and epoch_ok(args.deadline) and args.t0 < args.deadline):
        raise WatchError("BAD_ARM")
    record = {"schema": ARM_SCHEMA, "plan_id": args.plan, "attempt": attempt_of(args.plan), "t0_epoch_s": args.t0,
              "deadline_epoch_s": args.deadline}
    commit = _publish(_remote_url(args.repo_dir, args.remote), args.plan, {"arm.json": canonical(record)})
    print(f"MBP_WATCH_ARM plan={args.plan} t0={iso(args.t0)} deadline={iso(args.deadline)} commit={commit}")
    return EXIT["ok"]


def close(args, now=None):
    now = time.time() if now is None else now
    if not plan_ok(args.plan) or args.status not in CLOSE_STATUSES or not epoch_ok(args.close_epoch) \
            or args.close_epoch > now + CLOCK_SLACK_S:
        raise WatchError("BAD_CLOSE")
    record = {"schema": CLOSE_SCHEMA, "plan_id": args.plan, "status": args.status, "close_epoch_s": args.close_epoch}
    commit = _publish(_remote_url(args.repo_dir, args.remote), args.plan, {"close.json": canonical(record)},
                      child=True)
    print(f"MBP_WATCH_CLOSE plan={args.plan} status={args.status} commit={commit}")
    return EXIT["ok"]


# --- the watch -----------------------------------------------------------------------------------

def _json(raw):
    try:
        doc = json.loads(raw) if raw is not None else None
    except ValueError:
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


def read_arm(git, plan, sha):
    """(t0, deadline, attempt, sha256 of the arm record) or None. The digest names the silence episode:
    it does not change when a close record is appended to the ref."""
    raw = git.blob(sha, "arm.json")
    times = _arm_times(_json(raw), plan)
    return (*times, hashlib.sha256(raw).hexdigest()) if times else None


def read_close(git, plan, sha, t0, now):
    """('absent', None), ('invalid', None) or (status word, close epoch)."""
    raw = git.blob(sha, "close.json")
    if raw is None:
        return "absent", None
    doc = _json(raw)
    if not doc or doc.get("schema") != CLOSE_SCHEMA or doc.get("plan_id") != plan \
            or doc.get("status") not in CLOSE_STATUSES or not epoch_ok(doc.get("close_epoch_s")) \
            or doc["close_epoch_s"] < t0 or doc["close_epoch_s"] > now + CLOCK_SLACK_S:
        return "invalid", None
    return doc["status"], doc["close_epoch_s"]


def read_transition(git, plan, sha, arm_times, now):
    """('invalid' | 'misbound' | status word, receipt epoch or None).

    Bound to the arm: the same attempt, launched no earlier than the arm (less clock slack) and by its
    deadline, with a receipt after both the launch and the arm and not in the future.
    """
    doc = _json(git.blob(sha, "transition.json"))
    if not doc or doc.get("schema") != TRANSITION_SCHEMA or doc.get("plan_id") != plan \
            or doc.get("status") not in TRANSITION_STATUSES or type(doc.get("attempt")) is not int \
            or doc["attempt"] != attempt_of(plan) or not epoch_ok(doc.get("t0_epoch")) \
            or not epoch_ok(doc.get("receipt_epoch")) or doc["receipt_epoch"] < doc["t0_epoch"] \
            or doc["receipt_epoch"] > now + CLOCK_SLACK_S:
        return "invalid", None
    if arm_times and not (arm_times[0] - CLOCK_SLACK_S <= doc["t0_epoch"] <= arm_times[1]
                          and doc["receipt_epoch"] >= arm_times[0]):
        return "misbound", None
    return doc["status"], doc["receipt_epoch"]


def read_verdict(git, plan, sha):
    """'invalid', None (no hold), or a closed-vocabulary hold word."""
    doc = _json(git.blob(sha, "desk_verdict.json"))
    if not doc or doc.get("plan_id") != plan or type(doc.get("next_arm_hold")) is not bool:
        return "invalid"
    if not doc["next_arm_hold"]:
        return None
    codes = {h.get("code") for h in doc.get("holds") or [] if isinstance(h, dict)}
    named = {c if c in HOLD_CODES else "UNKNOWN_HOLD" for c in codes if isinstance(c, str)}
    return named.pop() if len(named) == 1 else ("MULTIPLE" if named else "UNNAMED")


def event(code, detail, plan, ref, sha, **times):
    return {"code": code, "detail": detail, "plan": plan, "ref": ref, "sha": sha, "times": times}


def events(git, now, grace_s):
    """Every alarm the current refs imply. No age limit: an obligation lasts as long as its ref."""
    by_plan = {}
    for ref, sha in git.refs().items():
        prefix = next(p for p in (ARMS, BUNDLE, VERDICT) if ref.startswith(p))
        plan = ref[len(prefix):]
        if plan_ok(plan):
            by_plan.setdefault(plan, {})[prefix] = (ref, sha)
    git.fetch([sha for entries in by_plan.values() for _, sha in entries.values()])
    found = []
    for plan, entries in sorted(by_plan.items()):
        arm_times, resolved_at = None, []
        if ARMS in entries:
            ref, sha = entries[ARMS]
            arm_times = read_arm(git, plan, sha)
            if arm_times is None:
                found.append(event("RESULT_UNREADABLE", "ARM_RECORD", plan, ref, sha, observed=now))
            else:
                status, when = read_close(git, plan, sha, arm_times[0], now)
                if status == "invalid":
                    found.append(event("RESULT_UNREADABLE", "CLOSE_RECORD", plan, ref, sha, observed=now))
                elif status != "absent":
                    resolved_at.append(when)
                    if status != "CLOSED_OK":
                        found.append(event("SPAN_STOP", status, plan, ref, sha, t0=arm_times[0], observed=now))
        if BUNDLE in entries:
            ref, sha = entries[BUNDLE]
            status, when = read_transition(git, plan, sha, arm_times, now)
            if status in ("invalid", "misbound"):
                detail = "TRANSITION" if status == "invalid" else "TRANSITION_MISBOUND"
                found.append(event("RESULT_UNREADABLE", detail, plan, ref, sha, observed=now))
            else:
                resolved_at.append(when)
                if status != "CLOSED_OK":
                    found.append(event("SPAN_STOP", status, plan, ref, sha, observed=now))
        if arm_times:
            limit = arm_times[1] + grace_s
            first = min(resolved_at) if resolved_at else None
            # Silence now, or a silence that ended between two polls (the result came after the limit).
            if (first is None and now > limit) or (first is not None and first > limit):
                ref, _ = entries[ARMS]
                found.append(event("SPAN_SILENT", "NO_RESULTS_REF", plan, ref, arm_times[3], t0=arm_times[0],
                                   deadline=arm_times[1], grace_s=grace_s, observed=now))
        if VERDICT in entries:
            ref, sha = entries[VERDICT]
            hold = read_verdict(git, plan, sha)
            if hold == "invalid":
                found.append(event("RESULT_UNREADABLE", "DESK_VERDICT", plan, ref, sha, observed=now))
            elif hold:
                found.append(event("DESK_HOLD", hold, plan, ref, sha, observed=now))
    return found


def key(event_):
    return f"{event_['code']}:{event_['plan']}:{event_['detail']}:{event_['sha']}"


def title(event_):
    return f"{LABEL} {event_['code']} {event_['plan']} {event_['detail']} {event_['sha'][:12]}"


def body(event_, owner, run_url):
    """Only closed-vocabulary words, a pattern-checked span id, a ref, a sha, numbers and the run link."""
    if event_["code"] not in EVENT_CODES or event_["detail"] not in DETAILS or not plan_ok(event_["plan"]) \
            or not SHA_RE.fullmatch(event_["sha"] or "") \
            or not re.fullmatch(r"refs/heads/(span-watch|desk-bundles|cadence-desk-final)/" + re.escape(event_["plan"]),
                                event_["ref"] or ""):
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
        rows = api.call("GET", "/issues", {"labels": LABEL, "state": "all", "per_page": 100, "page": page})
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
    """span-watch/* and desk-bundles/* must be protected against deletion and rewrite (C.1 obligations)."""
    for prefix in PROTECTED:
        rules = api.call("GET", f"/rules/branches/{prefix}/rules-probe")
        if not isinstance(rules, list) or not all(isinstance(rule, dict) for rule in rules):
            raise WatchError("API_SHAPE_RULES")
        if not REQUIRED_RULES <= {rule.get("type") for rule in rules}:
            raise WatchError(f"RULESET_MISSING_{prefix.upper().replace('-', '_')}")


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


def read(args, api=None, now=None):
    """The latest completed run is the most recently started execution (a re-run attempt counts with its
    own start), ties broken by ``run_number`` and ``run_attempt``. A start up to 300 s in the future is
    clock skew; more is an error. Every returned run must be well formed: a malformed answer is an error.
    """
    now = time.time() if now is None else now
    api = api or Api(args.repo, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    answer = api.call("GET", f"/actions/workflows/{WORKFLOW}/runs",
                      {"branch": "main", "status": "completed", "per_page": 20})
    if not isinstance(answer, dict) or not isinstance(answer.get("workflow_runs"), list):
        raise WatchError("API_SHAPE_RUNS")
    runs = answer["workflow_runs"]
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
    """Notify once per open ``mbp-alarm`` issue number. Lines carry the number, code and span only."""
    rows = api.call("GET", "/issues", {"labels": LABEL, "state": "open", "per_page": 100})
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise WatchError("API_SHAPE_ISSUES")
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
        line = f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} ALARM MBP_ALARM {code} {plan} issue={number_}"
        notify(line)
        lines.append(line)
        seen.add(number_)
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
    for p in (a, c):
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
    commands = {"arm": arm, "close": close, "watch": watch, "read": read}
    try:
        return commands[args.command](args)
    except WatchError as error:
        print(f"MBP_WATCH_ERROR {error}", file=sys.stderr)
        return EXIT["usage"]


if __name__ == "__main__":
    sys.exit(main())
