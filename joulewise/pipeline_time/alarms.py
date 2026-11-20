"""Alarm deduplication and delivery channels for the pipeline watcher.

Channels need no Gmail and no agent: a macOS notification, an append to
`alarms.jsonl` (which the lead's session watches), and a GitHub issue labelled
`pipeline-alarm`. Mail is an optional argv channel, off by default.

Dedupe rules, per alarm key:
- A key raises once when it first appears. While it stays active, the local
  channels repeat at most every `repeat_s[severity]` (alarm 1 h, warn 6 h) and
  the issue channel at most every `issue_repeat_s` (6 h). An alarm with
  `repeat=False` (a finished overrun) is sent once and never again.
- A key that disappears is resolved: one `resolved` line, and its issue is
  closed with a comment. A key that returns within its repeat interval is
  marked active again without a new post.
- Only `alarm` severity uses the issue channel; `warn` stays local.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ISSUE_LABEL = "pipeline-alarm"
KEY_MARKER = "pipeline-alarm-key:"
REPEAT_S = {"alarm": 3600, "warn": 6 * 3600}
ISSUE_REPEAT_S = 6 * 3600
KEEP_RESOLVED_S = 7 * 86400
TITLE = "JouleWise pipeline"


@dataclass
class Alarm:
    key: str
    code: str
    severity: str  # "alarm" or "warn"
    summary: str
    detail: str = ""
    repeat: bool = True
    profile_pid: int | None = None
    stage: str | None = None
    public: str = ""  # L3: the only alarm text an issue may carry (no argv, cwd, paths, host, user)

    def line(self) -> str:
        return f"{self.severity.upper()} {self.code} {self.summary}"


@dataclass
class Action:
    alarm: Alarm | None
    kind: str  # "raise", "repeat", "resolve", "quiet"
    key: str
    issue: bool = False
    record: dict = field(default_factory=dict)


def load_state(path: Path) -> dict:
    try:
        state = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {"alarms": {}}
    if not isinstance(state, dict) or not isinstance(state.get("alarms"), dict):
        return {"alarms": {}}
    return state


def save_state(path: Path, state: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".state-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(state, handle, sort_keys=True, indent=1)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def plan(alarms: list[Alarm], state: dict, now: float, repeat_s=None, issue_repeat_s=ISSUE_REPEAT_S,
         hold: tuple = ()) -> list[Action]:
    """Decide what to send this poll and update `state` in place (the caller saves it).

    Keys starting with a `hold` prefix belong to a source that was blind this poll; an
    active one stays active and is not resolved (no false "resolved" or issue close).
    """
    repeat_s = dict(REPEAT_S, **(repeat_s or {}))
    records = state.setdefault("alarms", {})
    actions: list[Action] = []
    seen = set()
    for alarm in alarms:
        if alarm.key in seen:
            continue
        seen.add(alarm.key)
        rec = records.get(alarm.key)
        wants_issue = alarm.severity == "alarm"
        if rec is None:
            rec = records[alarm.key] = {"code": alarm.code, "severity": alarm.severity, "first_s": now,
                                        "last_sent_s": now, "last_issue_s": now if wants_issue else None,
                                        "issue": None, "active": True, "once": not alarm.repeat}
            actions.append(Action(alarm, "raise", alarm.key, issue=wants_issue, record=rec))
            continue
        was_active = rec.get("active", False)
        rec["active"] = True
        rec.pop("resolved_s", None)
        rec["severity"] = alarm.severity
        if rec.get("once") or not alarm.repeat:
            rec["once"] = True
            actions.append(Action(alarm, "quiet", alarm.key, record=rec))
            continue
        local_due = now - float(rec.get("last_sent_s") or 0) >= repeat_s.get(alarm.severity, REPEAT_S["alarm"])
        last_issue = rec.get("last_issue_s")
        issue_due = wants_issue and (last_issue is None or now - float(last_issue) >= issue_repeat_s)
        if not local_due and not issue_due:
            actions.append(Action(alarm, "quiet", alarm.key, record=rec))
            continue
        kind = "raise" if not was_active else "repeat"
        if local_due:
            rec["last_sent_s"] = now
        if issue_due:
            rec["last_issue_s"] = now
        actions.append(Action(alarm, kind if local_due else "quiet", alarm.key, issue=issue_due, record=rec))
    for key, rec in list(records.items()):
        if key in seen:
            continue
        if rec.get("active") and hold and key.startswith(tuple(hold)):
            continue
        if rec.get("active"):
            rec["active"] = False
            rec["resolved_s"] = now
            actions.append(Action(None, "resolve", key, issue=bool(rec.get("issue")), record=rec))
        elif now - float(rec.get("resolved_s") or now) > KEEP_RESOLVED_S:
            del records[key]
    return actions


def default_runner(argv, timeout=60, input_text=None):
    try:
        done = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, input=input_text)
        return done.returncode, done.stdout, done.stderr
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, "", str(exc)


def applescript_quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def notify(alarm_line: str, runner=default_runner, osascript="/usr/bin/osascript") -> bool:
    text = alarm_line.replace("\n", " ")[:220]
    script = f"display notification {applescript_quote(text)} with title {applescript_quote(TITLE)}"
    rc, _out, _err = runner([osascript, "-e", script], timeout=15)
    return rc == 0


def append_jsonl(path: Path, record: dict) -> bool:
    try:
        path = Path(path)
        if not path.parent.is_dir():
            if not path.parent.parent.is_dir():
                return False
            path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        return True
    except OSError:
        return False


PRIVATE_PATH_RE = re.compile(r"(?:/Users|/Volumes|/private|/home|/var/folders|/tmp|/opt)/\S*|~/\S*")


def _local_names() -> list[str]:
    names = []
    try:
        import getpass
        names.append(getpass.getuser())
    except Exception:  # noqa: BLE001
        pass
    try:
        import socket
        host = socket.gethostname()
        names += [host, host.split(".")[0]]
    except OSError:
        pass
    return [n for n in names if n and len(n) >= 3]


def scrub(text: str, names=None) -> str:
    """Defence in depth for public text: drop absolute paths, the host name and the user name."""
    text = PRIVATE_PATH_RE.sub("<local path>", text)
    for name in sorted(set(_local_names() if names is None else names), key=len, reverse=True):
        text = re.sub(re.escape(name), "<local>", text, flags=re.I)
    return text


def public_text(alarm: Alarm) -> str:
    """The detector's public line, scrubbed; never the summary or detail."""
    return scrub(alarm.public or f"{alarm.code} for key {alarm.key}")


class IssueChannel:
    """GitHub issues through `gh`. One open issue per key, found again by a body marker."""

    def __init__(self, repo: str, runner=default_runner, gh="gh"):
        self.repo = repo
        self.runner = runner
        self.gh = gh
        self._open = None

    def open_issues(self) -> dict:
        if self._open is None:
            rc, out, _ = self.runner([self.gh, "issue", "list", "--repo", self.repo, "--label", ISSUE_LABEL,
                                      "--state", "open", "--limit", "100", "--json", "number,body"], timeout=60)
            found = {}
            if rc == 0:
                try:
                    for row in json.loads(out or "[]"):
                        match = re.search(re.escape(KEY_MARKER) + r"\s*(\S+)", row.get("body") or "")
                        if match:
                            found[match.group(1)] = int(row["number"])
                except (ValueError, TypeError, KeyError):
                    found = {}
            self._open = found
        return self._open

    def body(self, alarm: Alarm, now: float) -> str:
        """L3: the repository is public. The issue carries the code, key, stage and the detector's
        public line (budget and elapsed time) only; argv, cwd, detail and host stay local."""
        stamp = time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(now))
        stage = f", stage `{alarm.stage}`" if alarm.stage else ""
        return (f"**{alarm.code}** ({alarm.severity}{stage}) at {stamp}\n\n{public_text(alarm)}\n\n"
                f"Alarm key `{alarm.key}`. Full detail is in the Air's local `ledger/alarms.jsonl`"
                + (" and the named profile" if "profile " in (alarm.public or "") else "") + ".\n\n"
                "Raised by the non-agent Air pipeline watcher (RL-127 terms 6-8, "
                "`scripts/pipeline_watch.py`). It posts at most once per alarm key per 6 h "
                "and closes this issue when the condition clears.\n\n"
                + f"<!-- {KEY_MARKER} {alarm.key} -->\n")

    def raise_or_comment(self, alarm: Alarm, record: dict, now: float) -> bool:
        number = record.get("issue") or self.open_issues().get(alarm.key)
        if number:
            rc, _, _ = self.runner([self.gh, "issue", "comment", str(number), "--repo", self.repo,
                                    "--body", "Still active.\n\n" + self.body(alarm, now)], timeout=60)
            if rc == 0:
                record["issue"] = int(number)
                return True
            record["issue"] = None
        title = f"[pipeline-alarm] {alarm.code}: {public_text(alarm)}"[:200]
        rc, out, _ = self.runner([self.gh, "issue", "create", "--repo", self.repo, "--label", ISSUE_LABEL,
                                  "--title", title, "--body", self.body(alarm, now)], timeout=60)
        if rc != 0:
            return False
        match = re.search(r"/issues/(\d+)", out or "")
        record["issue"] = int(match.group(1)) if match else None
        return True

    def resolve(self, key: str, record: dict, now: float) -> bool:
        number = record.get("issue")
        if not number:
            return True
        stamp = time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(now))
        rc, _, _ = self.runner([self.gh, "issue", "close", str(number), "--repo", self.repo,
                                "--comment", f"Resolved at {stamp}: the watcher no longer sees `{key}`."],
                               timeout=60)
        if rc == 0:
            record["issue"] = None
        return rc == 0


def deliver(actions: list[Action], now: float, jsonl_path: Path | None, channels: dict,
            issues: IssueChannel | None = None, runner=default_runner, host: str = "") -> list[str]:
    """Send each action through the enabled channels; return one log line per delivery."""
    log = []
    for action in actions:
        if action.kind == "quiet" and not action.issue:
            continue
        alarm = action.alarm
        rec = action.record
        if action.kind in ("raise", "repeat", "resolve") and jsonl_path and channels.get("jsonl", True):
            entry = {"ts": round(now, 3), "event": action.kind, "key": action.key, "host": host,
                     "code": alarm.code if alarm else rec.get("code"),
                     "severity": alarm.severity if alarm else rec.get("severity")}
            if alarm:
                entry.update({"summary": alarm.summary, "detail": alarm.detail})
                if rec.get("profile"):
                    entry["profile"] = rec["profile"]
            ok = append_jsonl(jsonl_path, entry)
            log.append(f"jsonl {'ok' if ok else 'failed'} {action.kind} {action.key}")
        notify_this = channels.get("notification", True) and (
            action.kind in ("raise", "repeat") or (action.kind == "resolve" and rec.get("severity") == "alarm"))
        if notify_this:
            line = alarm.line() if alarm else f"RESOLVED {rec.get('code')} {action.key}"
            ok = notify(line, runner=runner)
            log.append(f"notify {'ok' if ok else 'failed'} {action.kind} {action.key}")
        if action.issue and issues is not None and channels.get("issue", True):
            if action.kind == "resolve":
                ok = issues.resolve(action.key, rec, now)
            else:
                ok = issues.raise_or_comment(alarm, rec, now)
            log.append(f"issue {'ok' if ok else 'failed'} {action.kind} {action.key} #{rec.get('issue')}")
        mail_cmd = channels.get("mail_cmd")
        if mail_cmd and action.kind in ("raise", "repeat") and alarm and alarm.severity == "alarm":
            rc, _, _ = runner(list(mail_cmd) + [alarm.line()], timeout=30, input_text=alarm.detail)
            log.append(f"mail {'ok' if rc == 0 else 'failed'} {action.kind} {action.key}")
    return log


def alarm_dict(alarm: Alarm) -> dict:
    return asdict(alarm)
