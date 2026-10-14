"""Structure-only outbox with injected transports and owner-NO parsing."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

VERDICTS = {"COLLECTED", "NO_COLLECTION", "NULL", "HARVEST_FAULT"}
STATES = {"NEXT", "PRECHECK", "WAIT_PHYSICS", "SMOKE_RUN", "SMOKE_DESK", "ARM_WAIT", "SESSION_RUN",
          "SESSION_DESK", "ROTATE", "HOLD_LOOP", "DONE"}
ANALYSIS_WORDS = ("resolved", "unresolved", "positive", "negative", "direction", "replicated", "not_replicated",
                  "higher", "lower", "above_floor", "below_floor", "equivalent", "different", "dbar",
                  "direction_supported", "not_estimable", "not_resolvable", "not_distinguished", "inconclusive")
SCREEN = re.compile(r"\d(?:\.\d+)?\s*(?:mJ|kJ|J|W|joules?|watts?)\b|\b(?:" +
                    "|".join(ANALYSIS_WORDS) + r")\b", re.I)
TOKEN = re.compile(r"[a-zA-Z0-9_.:/+-]+\Z")
FIELDS = {"packs", "pack_id", "session_id", "round", "t0_not_before", "smoke", "predicted_flags", "thin_margin",
          "previous", "verdict", "counting", "flags", "minutes", "chain", "harvest", "desk", "state", "cause",
          "counts", "planned", "present", "succeeded", "time", "count", "short", "hazard", "reason"}


def body(fields, catalog):
    blocked = False

    def clean(value, key=None):
        nonlocal blocked
        if isinstance(value, dict):
            # Per-pack and per-module maps permit identifiers, but recurse only
            # into explicitly structured maps; unknown lane fields vanish.
            return {k: clean(v, k) for k, v in value.items()
                    if k in FIELDS or (key in {"counting", "counts", "short"} and TOKEN.fullmatch(k))}
        if isinstance(value, (list, tuple)):
            return [clean(x, key) for x in value]
        if type(value) in (int, float, bool) or value is None:
            return value
        if isinstance(value, str):
            if SCREEN.search(value):
                blocked = True
            if value in catalog.codes:
                if catalog.entry(value).get("blinding") != "STRUCTURE":
                    blocked = True
                    return None
            elif key in {"flags", "predicted_flags"}:
                return None
            if not TOKEN.fullmatch(value) or "@" in value:
                blocked = True
                return None
            if key == "verdict" and value not in VERDICTS:
                blocked = True
            if key == "state" and value not in STATES:
                blocked = True
            return value
        return None

    filtered = clean(fields)
    result = json.dumps(filtered, indent=2)
    blocked = blocked or bool(SCREEN.search(result))
    state = fields.get("state", "HOLD_LOOP")
    if state not in STATES:
        state = "HOLD_LOOP"
    return (f"state changed to {state}; details withheld", True) if blocked else (result, False)


def owner_no(comments, owner_login, notice_created):
    stamp = datetime.fromisoformat(notice_created.replace("Z", "+00:00"))
    for comment in comments:
        try:
            created = datetime.fromisoformat(comment["created_at"].replace("Z", "+00:00"))
            if comment["user"]["login"] == owner_login and comment["body"].strip() == "NO" and created > stamp:
                return True
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    return False


class GitHubTransport:
    def __init__(self, repo, run):
        if "@" in repo:
            raise ValueError("repository must be owner/name")
        self.repo, self.run = repo, run

    def api(self, endpoint, *args):
        result = self.run(["gh", "api", f"repos/{self.repo}/{endpoint}", *args])
        if result.returncode:
            raise RuntimeError("github_delivery_failed")
        return json.loads(result.stdout or "null")

    def send(self, entry):
        if entry["kind"] == "arm_notice":
            issue = self.api("issues", "--method", "POST", "-f", "title=Block 6 arm notice", "-f",
                             "body=" + entry["body"], "-f", "labels[]=directive-notice")
            return {"issue_number": issue["number"], "created_at": issue["created_at"]}
        issues = self.api("issues?state=open&labels=b6-loop-status")
        if issues:
            issue = issues[0]
        else:
            issue = self.api("issues", "--method", "POST", "-f", "title=Block 6 loop status", "-f",
                             "body=Structure-only loop updates", "-f", "labels[]=b6-loop-status")
        self.api(f"issues/{issue['number']}/comments", "--method", "POST", "-f", "body=" + entry["body"])
        return {"issue_number": issue["number"]}

    def has_no(self, receipt, owner_login):
        if not receipt or "created_at" not in receipt:
            return False
        # paginate emits one JSON array per page; --slurp turns them into one list.
        pages = self.api(f"issues/{receipt['issue_number']}/comments", "--paginate", "--slurp")
        comments = [c for page in pages for c in page] if pages and isinstance(pages[0], list) else pages
        return owner_no(comments or [], owner_login, receipt["created_at"])

    def close(self, receipt):
        if receipt:
            self.api(f"issues/{receipt['issue_number']}", "--method", "PATCH", "-f", "state=closed")


class SMTPTransport:
    """Optional: caller supplies sender and recipient at runtime, never argv."""
    def __init__(self, run, send):
        self.run, self.sender = run, send

    def send(self, entry):
        item = self.run(["security", "find-generic-password", "-s", "joulewise-b6-smtp", "-w"])
        if item.returncode or not item.stdout.strip():
            raise RuntimeError("smtp_not_configured")
        self.sender(item.stdout.strip(), entry["body"])
        return {}


class Mailer:
    def __init__(self, loop_root, catalog, *, clock, transport=None, smtp=None):
        self.root = Path(loop_root)
        self.outbox = self.root / "outbox"
        self.catalog, self.clock, self.transport, self.smtp = catalog, clock, transport, smtp

    def enqueue(self, kind, identity, cause, fields):
        key = hashlib.sha256(json.dumps([kind, identity, cause]).encode()).hexdigest()[:24]
        self.outbox.mkdir(parents=True, exist_ok=True)
        path = self.outbox / (key + ".json")
        if not path.exists():
            text, blocked = body(fields, self.catalog)
            self._write(path, {"key": key, "kind": kind, "body": text, "blocked": blocked,
                               "delivered": False, "tries": 0, "retry_at": self.clock(), "receipt": None})
        return key

    def _write(self, path, entry):
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(entry, indent=2) + "\n")
        temp.replace(path)

    def entry(self, key):
        return json.loads((self.outbox / (key + ".json")).read_text())

    def has_no(self, key, owner_login):
        entry = self.entry(key)
        if self.transport is None:
            return False
        try:
            return self.transport.has_no(entry["receipt"], owner_login)
        except Exception:
            entry["no_probe_failed"] = True
            self._write(self.outbox / (key + ".json"), entry)
            return False

    def close_notice(self, key):
        entry = self.entry(key)
        entry["close_pending"] = not entry["delivered"] or entry["receipt"] is not None
        self._write(self.outbox / (key + ".json"), entry)

    def flush(self, *, state=None, deferred_overrun=False):
        overrun_hold = state == "HOLD_LOOP" and deferred_overrun
        if ((self.root / "collection.active").exists() and not overrun_hold) or state in {"SMOKE_RUN", "SESSION_RUN"}:
            return
        for path in sorted(self.outbox.glob("*.json")):
            entry = json.loads(path.read_text())
            if entry["delivered"] and not entry.get("close_pending"):
                continue
            now = self.clock()
            if now < entry["retry_at"]:
                continue
            try:
                if entry["delivered"]:
                    self.transport.close(entry["receipt"])
                    entry["close_pending"] = False
                else:
                    if self.transport is None:
                        raise RuntimeError("transport_missing")
                    entry["receipt"] = self.transport.send(entry)
                    entry["delivered"] = True
                entry["error"] = None
            except Exception:
                # Never copy transport exception text: it can contain credentials.
                if not entry["delivered"] and self.smtp is not None:
                    try:
                        self.smtp.send(entry)
                        entry["delivered"] = True
                    except Exception:
                        pass
                entry["tries"] += 1
                entry["error"] = "delivery_failed"
                entry["retry_at"] = now + (300, 900, 3600)[min(entry["tries"]-1, 2)]
            self._write(path, entry)
