"""The span queue (``docs/process/cadence/QUEUE.json``) and the chaining state machine.

The queue is declarative and append-only in practice: the lead writes it (a
state-only commit on ``main``); nobody writes span state into it. A span's state
is *derived* from evidence (results refs, arm and close records, the probe, the
clock), so every reader computes the same answer and re-running a decision is
idempotent. ``next_action`` is the whole chaining rule:

* a queue halt, an open ``cadence-stop`` issue or a directive veto  -> ``halt``;
* walk spans in ``seq`` order, skipping CLOSED_OK spans;
* the first span that is bad-terminal (refused, fault, stranded, stopped,
  checklist failed, withdrawn)                                         -> ``halt``;
* a span whose results landed but has no after-session record            -> ``close``;
* a span armed or running                                                -> ``wait``;
* a queued span                                                          -> ``arm``;
* no span left                                                           -> ``drained``.

The magistrate's one after-session activation therefore runs ``close`` for the
span that just exited and then, on the same evidence plus its own close record,
``arm`` for the next one. A refusal or fault never chains.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re

SCHEMA = "joulewise.cadence_queue.v1"
QUEUE_PATH = "docs/process/cadence/QUEUE.json"
QUEUE_ID_RE = re.compile(r"cq-[a-z0-9][a-z0-9-]{2,40}")
SPAN_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,40}")
PLAN_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
HEX64 = re.compile(r"[0-9a-f]{64}")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
OWNER_LOGIN = "mpmdw"
VETO_RE = re.compile(r"^\s*(?:VETO|NO|STOP|HALT)\b", re.I)

# Span states.
QUEUED, ARMED, RUNNING, EXITED = "QUEUED", "ARMED", "RUNNING", "EXITED"
CLOSED_OK, STOPPED = "CLOSED_OK", "STOPPED"
REFUSED, FAULT, STRANDED = "REFUSED", "FAULT", "STRANDED"
CHECKLIST_FAILED, WITHDRAWN = "CHECKLIST_FAILED", "WITHDRAWN"
BAD_TERMINAL = frozenset({STOPPED, REFUSED, FAULT, STRANDED, CHECKLIST_FAILED, WITHDRAWN})

# Legal transitions (documentation and a guard for recorders).
TRANSITIONS = {
    QUEUED: {ARMED, CHECKLIST_FAILED, WITHDRAWN},
    ARMED: {RUNNING, EXITED, REFUSED, FAULT, STRANDED, WITHDRAWN},
    RUNNING: {EXITED, REFUSED, FAULT, STRANDED},
    EXITED: {CLOSED_OK, STOPPED},
    CLOSED_OK: set(), STOPPED: set(), REFUSED: set(), FAULT: set(), STRANDED: set(),
    CHECKLIST_FAILED: set(), WITHDRAWN: set(),
}

SPAN_KEYS = {"seq", "span_id", "block_id", "kit", "legs", "attempt", "not_before", "rerun_of"}
TOP_KEYS = {"schema", "queue_id", "expires_at", "halt", "standing_notice", "spans"}


class QueueError(ValueError):
    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems) if self.problems else "invalid queue")


def parse_time(text):
    """Epoch seconds for an ISO 8601 time with an explicit offset, else None."""
    if not isinstance(text, str):
        return None
    try:
        moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return None if moment.tzinfo is None else moment.timestamp()


def plan_id(span):
    return f"cq-{span['span_id']}-a{span['attempt']}"


def legal(a, b):
    return b in TRANSITIONS.get(a, set())


def validate_queue(doc, kits=None):
    """Validate a queue document. ``kits`` maps kit path -> (kit, sha256) to check legs and pins."""
    problems = []
    if not isinstance(doc, dict):
        raise QueueError(["queue: expected an object"])
    for k in sorted(set(doc) - TOP_KEYS):
        problems.append(f"queue: unknown key {k!r}")
    for k in sorted(TOP_KEYS - set(doc)):
        problems.append(f"queue: missing key {k!r}")
    if doc.get("schema") != SCHEMA:
        problems.append(f"schema: must be {SCHEMA}")
    if not (isinstance(doc.get("queue_id"), str) and QUEUE_ID_RE.fullmatch(doc["queue_id"])):
        problems.append("queue_id: cq-<lowercase id>")
    if parse_time(doc.get("expires_at")) is None:
        problems.append("expires_at: ISO 8601 with an explicit offset (a queue is finite)")
    halt = doc.get("halt")
    if halt is not None and not (isinstance(halt, dict) and set(halt) == {"reason", "by", "at"}
                                 and all(isinstance(v, str) and v.strip() for v in halt.values())):
        problems.append("halt: null or {reason, by, at}")
    notice = doc.get("standing_notice")
    if notice is not None and not (isinstance(notice, dict) and set(notice) == {"issue"}
                                   and type(notice["issue"]) is int and notice["issue"] > 0):
        problems.append("standing_notice: null or {issue: <directive-notice issue number>}")
    spans = doc.get("spans")
    if not isinstance(spans, list):
        problems.append("spans: list")
        spans = []
    seqs, ids, plans = [], set(), set()
    used_legs = {}
    for i, span in enumerate(spans):
        where = f"spans[{i}]"
        if not isinstance(span, dict):
            problems.append(f"{where}: object")
            continue
        for k in sorted(set(span) - SPAN_KEYS):
            problems.append(f"{where}: unknown key {k!r}")
        for k in sorted(SPAN_KEYS - {"rerun_of"} - set(span)):
            problems.append(f"{where}: missing key {k!r}")
        if type(span.get("seq")) is not int or span["seq"] < 1:
            problems.append(f"{where}.seq: positive integer")
        else:
            seqs.append(span["seq"])
        sid = span.get("span_id")
        if not (isinstance(sid, str) and SPAN_ID_RE.fullmatch(sid)) or sid in ids:
            problems.append(f"{where}.span_id: unique lowercase id")
        ids.add(sid)
        if not (isinstance(span.get("block_id"), str) and SPAN_ID_RE.fullmatch(span["block_id"])):
            problems.append(f"{where}.block_id: lowercase id")
        if type(span.get("attempt")) is not int or not 1 <= span["attempt"] <= 9:
            problems.append(f"{where}.attempt: 1..9")
        if not (isinstance(span.get("not_before"), str) and DATE_RE.fullmatch(span["not_before"])):
            problems.append(f"{where}.not_before: YYYY-MM-DD (local date of the earliest t0)")
        kit = span.get("kit")
        if not (isinstance(kit, dict) and set(kit) == {"path", "sha256"} and isinstance(kit.get("path"), str)
                and isinstance(kit.get("sha256"), str) and HEX64.fullmatch(kit["sha256"])):
            problems.append(f"{where}.kit: {{path, sha256}}")
            kit = None
        legs = span.get("legs")
        if not (isinstance(legs, list) and legs and all(isinstance(x, str) for x in legs)) or len(set(legs or [])) != len(legs or []):
            problems.append(f"{where}.legs: non-empty list of distinct leg ids")
            legs = []
        rerun = span.get("rerun_of")
        if rerun is not None and rerun not in ids - {sid}:
            problems.append(f"{where}.rerun_of: an earlier span_id")
        if isinstance(sid, str) and type(span.get("attempt")) is int:
            pid = plan_id(span)
            if not PLAN_ID_RE.fullmatch(pid) or pid in plans:
                problems.append(f"{where}: plan id {pid} invalid or duplicate")
            plans.add(pid)
        if kits is not None and kit is not None:
            entry = kits.get(kit["path"])
            if entry is None:
                problems.append(f"{where}.kit: {kit['path']} not supplied")
            else:
                k, sha = entry
                if sha != kit["sha256"]:
                    problems.append(f"{where}.kit.sha256: pinned {kit['sha256'][:12]}, file is {sha[:12]}")
                order = [leg["leg_id"] for leg in k["legs"]]
                pos = [order.index(x) if x in order else -1 for x in legs]
                if -1 in pos:
                    problems.append(f"{where}.legs: not in the kit: {[x for x, p in zip(legs, pos) if p < 0][:5]}")
                elif pos != sorted(pos):
                    problems.append(f"{where}.legs: not in the kit's seeded order")
                if len(legs) > k["span_template"]["legs_per_span"]:
                    problems.append(f"{where}.legs: {len(legs)} > span_template.legs_per_span")
                for x in legs:
                    prior = used_legs.get((kit["path"], x))
                    if prior is not None and rerun is None:
                        problems.append(f"{where}.legs: {x} already in span {prior} (a re-run names rerun_of)")
                    used_legs.setdefault((kit["path"], x), sid)
    if seqs != sorted(seqs) or len(set(seqs)) != len(seqs):
        problems.append("spans: seq must be strictly increasing in file order")
    if problems:
        raise QueueError(problems)
    return doc


def load_queue(path, kits_root=None):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    kits = None
    if kits_root is not None:
        from joulewise.cadence import kit as kitmod
        kits = {}
        for span in doc.get("spans", []):
            p = span.get("kit", {}).get("path")
            if isinstance(p, str) and p not in kits and (Path(kits_root) / p).is_file():
                kits[p] = kitmod.load_kit(Path(kits_root) / p)
    return validate_queue(doc, kits)


def result_ok(summary):
    """A results-ref summary that lets a span be closed normally (not a refusal or fault)."""
    if not isinstance(summary, dict):
        return False
    outcome = summary.get("outcome")
    return (summary.get("chain_exit_code") == 0 and summary.get("fault") is not True
            and summary.get("chain_outcome") in (None, "COMPLETE")
            and outcome in (None, "MEASURED_OK", "MEASURED_WITH_FLAGS"))


def span_state(span, evidence, now=None):
    """Derive one span's state. ``evidence`` keys (all optional):
    results {plan_id: summary}, armed [plan_id], started [plan_id], closed {plan_id: {stops: [...]}},
    withdrawn [plan_id], checklist_failed [plan_id], deadlines {plan_id: epoch},
    desk_final [plan_id] (read by next_action's k+2 rule)."""
    pid = plan_id(span)
    ev = evidence or {}
    if pid in ev.get("withdrawn", ()):
        return WITHDRAWN
    if pid in ev.get("checklist_failed", ()):
        return CHECKLIST_FAILED
    results = ev.get("results", {})
    if pid in results:
        summary = results[pid]
        if isinstance(summary, dict) and summary.get("fault") is True:
            return FAULT
        if not result_ok(summary):
            return REFUSED
        closed = ev.get("closed", {}).get(pid)
        if closed is None:
            return EXITED
        return STOPPED if closed.get("stops") else CLOSED_OK
    armed = pid in ev.get("armed", ()) or pid in ev.get("started", ())
    if armed:
        deadline = ev.get("deadlines", {}).get(pid)
        if now is not None and isinstance(deadline, (int, float)) and now > deadline:
            return STRANDED
        return RUNNING if pid in ev.get("started", ()) else ARMED
    return QUEUED


@dataclass
class Decision:
    action: str               # halt | close | wait | arm | drained
    span: dict | None = None
    reasons: list = field(default_factory=list)
    states: dict = field(default_factory=dict)

    def as_dict(self):
        return {"action": self.action, "span_id": self.span and self.span["span_id"],
                "plan_id": self.span and plan_id(self.span), "reasons": self.reasons, "states": self.states}


def next_action(queue, evidence=None, halts=(), now=None):
    states = {s["span_id"]: span_state(s, evidence, now) for s in queue["spans"]}
    reasons = []
    expires = parse_time(queue.get("expires_at"))
    if now is not None and expires is not None and now > expires:
        reasons.append(f"queue expired at {queue['expires_at']}")
    if queue.get("halt"):
        reasons.append(f"queue halt by {queue['halt']['by']}: {queue['halt']['reason']}")
    span_vetoes = set()
    for h in halts:
        if h.get("scope") == "queue":
            reasons.append(f"halt: {h.get('source')} #{h.get('issue')}")
        else:
            span_vetoes.add(h.get("scope"))
    if reasons:
        return Decision("halt", None, reasons, states)
    for span in queue["spans"]:
        st = states[span["span_id"]]
        if st == CLOSED_OK:
            continue
        if st in BAD_TERMINAL:
            return Decision("halt", span, [f"span {span['span_id']} is {st}"], states)
        if st == EXITED:
            return Decision("close", span, ["results landed; after-session record due"], states)
        if st in (ARMED, RUNNING):
            return Decision("wait", span, [f"span {span['span_id']} is {st}"], states)
        if span["span_id"] in span_vetoes:
            return Decision("halt", span, [f"span {span['span_id']} vetoed"], states)
        # k+2 rule (harvest-off contract): span k's full desk is final before span k+2 arms.
        index = queue["spans"].index(span)
        if index >= 2:
            older = queue["spans"][index - 2]
            if plan_id(older) not in (evidence or {}).get("desk_final", ()):
                return Decision("wait", span, [f"WAIT_AIR: desk of {older['span_id']} not final (k+2 rule)"], states)
        return Decision("arm", span, ["next queued span"], states)
    return Decision("drained", None, ["every span closed"], states)


def halts_from_issues(issues, queue, owner=OWNER_LOGIN):
    """Open owner-authored issues that halt the queue or veto a span.

    * label ``cadence-stop`` (the Air desk's named-stop page): halts the queue;
    * label ``directive`` whose title or first body line starts with VETO/NO/STOP/HALT
      and names the queue id, a span id, or the words "cadence"/"queue"/"all":
      halts the queue, or vetoes the named span(s) only.
    Comments are never read. Issues by anyone else are ignored."""
    out = []
    span_ids = {s["span_id"] for s in queue["spans"]}
    for issue in issues or ():
        author = (issue.get("author") or {}).get("login")
        if author != owner or str(issue.get("state", "OPEN")).upper() != "OPEN":
            continue
        labels = {(l.get("name") if isinstance(l, dict) else l) for l in issue.get("labels", [])}
        number = issue.get("number")
        if "cadence-stop" in labels:
            out.append({"scope": "queue", "source": "cadence-stop", "issue": number})
            continue
        if "directive" not in labels:
            continue
        title = issue.get("title") or ""
        first = (issue.get("body") or "").strip().splitlines()[:1]
        text = " ".join([title, *first])
        if not (VETO_RE.match(title) or (first and VETO_RE.match(first[0]))):
            continue
        named = {s for s in span_ids if re.search(rf"\b{re.escape(s)}\b", text)}
        if queue["queue_id"] in text or re.search(r"\b(cadence|queue|all)\b", text, re.I) and not named:
            out.append({"scope": "queue", "source": "directive-veto", "issue": number})
        else:
            out.extend({"scope": s, "source": "directive-veto", "issue": number} for s in sorted(named))
    return out
