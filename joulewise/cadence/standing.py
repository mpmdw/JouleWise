"""The standing queue's law (RL-172 section (g), with (a), (c) and (f); RL-149 section 2.8). Pure functions.

The controller (``scripts/cadence_controller.py``) gathers every input fresh at each arm (git, the
owner's issues, the host) and hands it here. Nothing in this module opens a file, reads a clock, runs a
command or touches the network: each function takes what it judges and returns named reasons. A
missing, stale or contradictory input is itself a named reason, never a pass.

Reason categories (``REASONS``):

* ``halt``: nothing arms; the controller pages the magistrate and waits for an acknowledgement.
* ``wait``: this candidate cannot arm yet; ``eta`` says when it could (None: not known). Every wait is
  bounded: the controller pages ``WAIT_STALL`` when one outlasts its bound (``stall_bound``).
* ``retry``: a transient read failed (network); treated as a wait, never as a pass.
* ``cede``: a READY v4 session holds everything; the controller pages, goes silent, and never launches it.
* ``page``: an empty queue or a due F0; the magistrate's standing item decides.

The desk contract is ``FORMAT.md`` (desk builder, PR #799): the controller reads the desk's
``joulewise.cadence_desk_verdict.v1`` records by its §4, and derives the hand gates the desk prints
(``desk_final.CONSUMER_GATES`` and the class A rule) itself at the close, because the next span may arm
before any verdict exists.

This module adds no rule. Each check cites the ruling it enforces; where a ruling leaves a choice the
docstring says which way it is taken (always the stricter one).
"""
from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from datetime import date, datetime, time as dtime, timedelta
import hashlib
import json
import re
from zoneinfo import ZoneInfo

from joulewise.cadence import desk_final, kit as kitmod, queue as q

STANDING_SCHEMA = "joulewise.cadence_standing.v1"
SESSION_READY_SCHEMA = "joulewise.cadence_session_ready.v1"
SESSION_DONE_SCHEMA = "joulewise.cadence_session_done.v1"
WATCHER_STAMP_SCHEMA = "joulewise.cadence_watcher_stamp.v1"
TRANSITION_SCHEMA = "joulewise.cadence_controller_transition.v1"
VERDICT_SCHEMA = desk_final.VERDICT_SCHEMA
ZONE = ZoneInfo(kitmod.LOCAL_ZONE_NAME)

QUEUE_TTL_S = 7 * 86400            # RL-149 section 2.8 line 3; RL-172 (g) 3: from the queue file's FIRST commit
WATCHER_TTL_S = 24 * 3600          # RL-149 section 2.8 line 7
CLOCK_SKEW_S = 300                 # a commit or stamp further ahead of the host clock is a contradiction
DEV_MIXED_MAX = 12                 # RL-172 (a) 1
DEV_MAX = 24                       # RL-172 (a) 2
GAP_AFTER_CAMPAIGN_S = 300         # RL-171 section 6.1, confirmed RL-172 section 0
GAP_AFTER_OTHER_S = 1200           # after F0, F2 or any non-campaign close (RL-172 section 0)
F0_SPACING_S = 4 * 3600            # RL-165 section 3 line 5
F0_MAX_PER_DATE = 3
FALLBACK_HORIZON_S = 2.5 * 3600    # RL-165 section 3 line 3: no staged item can hold within 2 h 30 min
STALL_S = 2.5 * 3600               # the default bound on any wait
STALL_SHORT_S = 30 * 60            # waits the host or the lead clears in minutes, or never by themselves
SHORT_STALL_CODES = frozenset({"AGENT_PRESENT", "PLAN_REFUSED_AT_T0", "JOURNAL_COPY", "SPAN_LIVE", "CLOSING",
                               "ISSUES_UNREADABLE", "FETCH_FAILED", "NIGHT_UNKNOWN", "LEASE_EXPIRED"})
STALL_LONG_S = 36 * 3600           # a loaded night agent is a v4 window (28 to 33 h); it pages only past that
LONG_STALL_CODES = frozenset({"NIGHT_AGENT"})
MIDNIGHT_MARGIN_S = 120            # a dated arm is refused this close to the end of its date (F19)

PHASES = {"cl-dev-": "development", "cl-qual-": "qualification", "cl-hp-": "extension", "hp-": "extension",
          "cl-f2-": "filler", "f2-": "filler"}
SESSION_KINDS = ("r1-slot", "w1", "c", "t")
FALLBACK_KINDS = ("F0", "F2")      # RL-172 (g) 9: nothing else
QUEUE_ROLES = ("standing", "smoke")
BATCH_RULES = ("none", "rl172")
RESOLUTIONS = ("cleared", "rerun", "withdrawn")
GATE_DECISIONS = ("release", "hold")
CLASS_A = "class-a"
HHMM = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d-(?:[01]\d|2[0-3]):[0-5]\d")
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
VETO_WORD = re.compile(r"^\s*(?:VETO|NO|STOP|HALT)\b", re.I)

# code -> (category, plain text). Every reason the controller can give is here.
REASONS = {
    # halts: missing, stale or contradictory inputs, and the ruling's hard lines
    "STANDING_MISSING": ("halt", "the standing index is not on the audit branch"),
    "STANDING_INVALID": ("halt", "the standing index does not validate"),
    "AUDIT_REWRITTEN": ("halt", "the audit branch no longer descends from the tip the controller last read"),
    "QUEUE_MISSING": ("halt", "a listed queue is not on the audit branch"),
    "QUEUE_INVALID": ("halt", "a queue does not validate (validate-queue)"),
    "QUEUE_NOT_APPEND_ONLY": ("halt", "a queue's history is not append-only (RL-149 section 2.8 line 3)"),
    "QUEUE_REWRITTEN": ("halt", "a queue no longer extends the version the controller last read or armed from"),
    "QUEUE_EXPIRED": ("halt", "a queue with spans to run is past seven days from its first commit or its expires_at"),
    "QUEUE_COMMIT_IN_FUTURE": ("halt", "a queue's commit time is ahead of the host clock"),
    "QUEUE_HALT": ("halt", "a queue carries a lead halt"),
    "QUEUE_NO_NOTICE": ("halt", "a queue with spans to run names no standing notice issue (RL-149 section 2.8)"),
    "QUEUE_DUPLICATE": ("halt", "a plan id, or a kit leg without rerun_of, is queued twice across queues"),
    "KIT_UNKNOWN": ("halt", "a queued kit sha is not in the standing index"),
    "KIT_UNREADABLE": ("halt", "a queued kit could not be read or does not hash to its pin"),
    "KIT_EVIDENCE_MISSING": ("halt", "a kit has no line 1 or line 2 record (RL-149 section 2.8)"),
    "KIT_UNCLASSIFIED": ("halt", "a kit's campaign id names no phase the controller knows"),
    "KIT_ROLE_MISMATCH": ("halt", "a filler kit in a counted queue, or a counted kit in a fallback queue"),
    "DATE_MISSED": ("halt", "a counted span's t0-date is past its not_before: the lead re-dates it (RL-172 (a) 5)"),
    "DATE_DEV_MIXED_CAP": ("halt", "the t0-date would hold more than 12 mixed-size development legs (RL-172 (a) 1)"),
    "DATE_DEV_CAP": ("halt", "the t0-date would hold more than 24 development legs (RL-172 (a) 2)"),
    "DATE_QUAL_DEV_OVERLAP": ("halt", "qualification and development t0-dates would meet (RL-172 (a) 3)"),
    "DATE_QUAL_SINGLE": ("halt", "the qualification blocks would all fall on one date (RL-172 (a) 3)"),
    "SMOKE_QUEUE_NOT_PILOT_ONLY": ("halt", "a pilot is not alone in a smoke queue (RL-172 (g) 4)"),
    "SMOKE_REMAINDER_STAGED": ("halt", "a kit's remainder is queued before its pilot's class A gate released (RL-172 (g) 4)"),
    "PILOT_MISSING": ("halt", "a span of a kit arms before any pilot of that kit closed clean"),
    "PRIOR_GATES_UNKNOWN": ("halt", "a prior span's kit is not readable, so its hand gates cannot be derived"),
    "PRIOR_CONTRADICTS": ("halt", "a prior span's roster or kit disagrees with its queue entry or its receipt"),
    "GATE_RECORD_PREMATURE": ("halt", "a gate release was committed before the span it releases closed"),
    "GATE_DISAGREEMENT": ("halt", "the desk's verdict names a hand gate the controller did not derive, or the reverse"),
    "VETO_OPEN": ("halt", "an open owner directive starts STOP, NO, HALT or VETO (line 6)"),
    "CADENCE_STOP_OPEN": ("halt", "an open cadence-stop issue (line 6)"),
    "WATCHER_STAMP_MISSING": ("halt", "no results-watcher stamp on the audit branch (line 7)"),
    "WATCHER_STALE": ("halt", "the results-watcher stamp is older than 24 h (line 7)"),
    "WATCHER_STAMP_INVALID": ("halt", "the watcher stamp is malformed, names another watcher, or is ahead of its commit"),
    "SPAN_BAD_TERMINAL": ("halt", "a span closed refused, stopped, faulted, stranded or unproven, with no disposition"),
    "FOREIGN_CLOSE_UNPROVEN": ("halt", "another run's fence went away; its restore is unproven until note-run records it"),
    "ARM_INDETERMINATE": ("halt", "an arm intent has no launch result and no live span (restart after a crash)"),
    "DESK_HOLD": ("halt", "a desk verdict holds the next arm (a named stop) until the lead clears it"),
    "DESK_VERDICT_INVALID": ("halt", "a desk verdict is unsigned, malformed, misnamed or contradicts the armed entry"),
    "SESSION_INVALID": ("halt", "a v4 session READY record is malformed or names an unknown session"),
    "FALLBACK_INVALID": ("halt", "a fallback entry is not F0 or F2 on its standing rules (RL-172 (g) 9)"),
    "HOST_PROOF_FAILED": ("halt", "the arm's host readback or process-group absence failed (RL-172 (g) 5)"),
    "CLOSE_UNPROVEN": ("halt", "the close proof failed: restore, readback or process absence (RL-172 (g) 5)"),
    "RECEIPT_NOT_CLEAN": ("halt", "the span's receipt is a refusal or an error (a receipt all the same)"),
    "RECEIPT_MISSING": ("halt", "the span exited with no receipt"),
    "UNKNOWN_CAMPAIGN_RECEIPT": ("halt", "a campaign receipt on the host is in no ledger (Mythos F18)"),
    "CENSUS_FAILED": ("halt", "the host receipt census failed or found nothing"),
    "ROSTER_MISMATCH": ("halt", "the desk inputs do not match the queue entry (RL-172 (c) 1 to 3)"),
    "NO_LEG_ROWS": ("halt", "the span has no leg rows: a stop (RL-172 (c) 3; Sol probe)"),
    "NAMED_STOP": ("halt", "a named stop fired on the span's operational summary"),
    "LAUNCH_REFUSED": ("halt", "the launcher refused or did not hand the fence to its LaunchAgent"),
    "BUNDLE_REFUSED": ("halt", "the packer refused the span's files: nothing is published"),
    "BUNDLE_UNAUTHENTICATED": ("halt", "the close bundle could not be signed and pushed"),
    "SIGNING_UNAVAILABLE": ("halt", "the controller cannot sign: the span would run and not publish (Mythos F11)"),
    "CLOCK_SKEW": ("halt", "the host clock disagrees with the server's by more than 120 s"),
    "PREPARE_FAILED": ("halt", "the measurement checkout, kit copy, validate-kit or plan failed"),
    "STRANDED_ALARM": ("halt", "the live span is past its deadline; nothing is closed while its fence and PID live"),
    "CONFIG_INVALID": ("halt", "the controller's config does not validate"),
    "STATE_CORRUPT": ("halt", "a controller record does not parse, or a tick raised"),
    # waits
    "NOT_BEFORE": ("wait", "today is before the span's not_before (RL-172 (g) 1)"),
    "K2_DESK_DEBT": ("wait", "span k's desk is not final before span k+2, in machine order (line 9)"),
    "GAP": ("wait", "the floor after the last close has not run (300 s campaign, 1,200 s otherwise)"),
    "HAND_GATE": ("wait", "a hand gate holds this span until the lead's record (class A, L002, L005, or named)"),
    "JOURNAL_COPY": ("wait", "the newest campaign close's journal copy marker is not written (item 331's copy gate)"),
    "FREEZE2": ("wait", "qualification arms only after freeze 2 is committed (RL-149 section 2.8)"),
    "AGENT_PRESENT": ("wait", "an agent process is alive on the host"),
    "NIGHT_AGENT": ("wait", "a night agent (a v4 window) is loaded: the controller stays silent"),
    "PLAN_REFUSED_AT_T0": ("wait", "the pinned plan refuses this t0"),
    "NIGHT_UNKNOWN": ("wait", "the night-agent read failed: no network until it reads clean"),
    "LEASE_EXPIRED": ("wait", "the authority read is older than the arm lease: re-read before arming"),
    "SPAN_LIVE": ("wait", "a span or another run holds the host"),
    "CLOSING": ("wait", "the span's fence is gone; its receipt or process absence is not yet proven"),
    "MIDNIGHT": ("wait", "a dated span is not armed within 120 s of the end of its date"),
    "FALLBACK_SPACING": ("wait", "F0 spacing: 4 h between t0s and at most three a date"),
    "FALLBACK_DAY_COST": ("wait", "a filler here would cost a counted span its date (RL-165 section 3 line 7)"),
    # transient
    "FETCH_FAILED": ("retry", "the audit branch could not be fetched"),
    "ISSUES_UNREADABLE": ("retry", "the owner's open issues could not be read; no veto is assumed absent"),
    # cede and pages
    "V4_SESSION_READY": ("cede", "a v4 session is READY: it takes the next clean close (RL-172 (f))"),
    "QUEUE_EMPTY": ("page", "nothing is queued, waiting or due"),
    "FALLBACK_F0_DUE": ("page", "no counted span can hold within 2 h 30 min; F0 is due on its standing item"),
    "WAIT_STALL": ("page", "a wait has outlasted its bound"),
}


class StandingError(ValueError):
    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems) if self.problems else "invalid")


def reason(code, detail="", *, eta=None, span=None):
    if code not in REASONS:
        raise KeyError(code)
    return {"code": code, "category": REASONS[code][0], "detail": detail or REASONS[code][1],
            "eta": eta, "span": span}


def category(reasons):
    """The strongest category among ``reasons``: halt > cede > page > retry > wait."""
    order = ("halt", "cede", "page", "retry", "wait")
    cats = {r["category"] for r in reasons}
    return next((c for c in order if c in cats), None)


def stall_bound(codes):
    """How long a wait with these codes may last before it pages (Mythos F7: every wait is bounded)."""
    if set(codes) and set(codes) <= LONG_STALL_CODES:
        return STALL_LONG_S
    return STALL_SHORT_S if set(codes) & SHORT_STALL_CODES else STALL_S


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# --------------------------------------------------------------------------
# Dates (RL-172 (a): a day is the local date of a span's t0)
# --------------------------------------------------------------------------
def local_date(epoch):
    return datetime.fromtimestamp(epoch, ZONE).date().isoformat()


def date_start(text):
    return datetime.combine(date.fromisoformat(text), dtime(0, 0), ZONE).timestamp()


def date_end(text):
    """The first instant of the next local date (DST-safe)."""
    return datetime.combine(date.fromisoformat(text) + timedelta(days=1), dtime(0, 0), ZONE).timestamp()


def parse_time(text):
    return q.parse_time(text)


# --------------------------------------------------------------------------
# Kits: which law applies to a span is derived from its kit, never declared
# --------------------------------------------------------------------------
def kit_class(kit):
    """``{phase, mixed, k2, dated}`` from the kit itself. ``k2``: a campaign span for line 9 (RL-165
    section 6: development, qualification and hp-01; Part C, sessions and fillers are not). ``dated``:
    in RL-172 (a)'s date counts (hp-01, F0, F2 and v4 sessions are outside, (a) 4)."""
    cid = kit.get("campaign_id", "")
    phase = next((p for prefix, p in PHASES.items() if cid.startswith(prefix)), None)
    if phase is None:
        raise StandingError([f"KIT_UNCLASSIFIED: campaign id {cid!r}"])
    defaults = kit.get("leg_defaults") or {}
    sizes = {leg.get("prefill_tokens", defaults.get("prefill_tokens")) for leg in kit.get("legs", [])}
    sizes.discard(None)
    return {"phase": phase, "mixed": len(sizes) > 1, "k2": phase in ("development", "qualification", "extension"),
            "dated": phase in ("development", "qualification")}


def derived_gates(kit, roster):
    """The hand gates RL-172 (c) keeps, derived in code from the kit, the campaign and the roster (never from
    lead data; Sol 6, Mythos F2). The same rules as the desk's ``hand_gates``:

    * ``class-a``: the roster holds the kit's first leg (a kit's first span is its class A smoke);
    * ``L002`` / ``L005``: ``desk_final.CONSUMER_GATES`` for this campaign, when that leg is in the roster and
      is span-shaped in the kit.

    Each gate holds every later span of the same campaign until the lead's release record for the span that
    raised it."""
    gates = []
    legs = kit.get("legs") or []
    if legs and legs[0]["leg_id"] in roster:
        gates.append(CLASS_A)
    by_id = {leg["leg_id"]: leg for leg in legs}
    gates += [leg_id for _name, leg_id, _ruling, _rule in
              desk_final.consumer_gates(kit.get("campaign_id"), by_id, list(roster))]
    return gates


DESK_GATE_NAMES = {CLASS_A: "class A smoke hand-read",
                   **{leg: name for (_c, leg), (name, _r, _w) in desk_final.CONSUMER_GATES.items()}}


# --------------------------------------------------------------------------
# The standing index (lead data on the audit branch)
# --------------------------------------------------------------------------
STANDING_KEYS = {"schema", "standing_id", "queues", "kits", "hand_gates", "gate_records", "prior_spans", "withdrawn",
                 "dispositions", "sessions", "fallback", "freeze2"}
KIT_ENTRY_KEYS = {"source", "line1", "line2", "batch_window"}
PRIOR_KEYS = {"plan_id", "campaign_id", "block_id", "kit_sha256", "roster", "legs", "mixed", "t0", "closed",
              "desk_final"}


def _text(v):
    return isinstance(v, str) and v.strip() != ""


def validate_standing(doc):
    """The standing index. Closed schema; every problem is named."""
    p = []
    if not isinstance(doc, dict):
        raise StandingError(["standing: an object"])
    for k in sorted(set(doc) ^ STANDING_KEYS):
        p.append(f"standing: {'unknown' if k in doc else 'missing'} key {k!r}")
    if doc.get("schema") != STANDING_SCHEMA:
        p.append(f"schema: {STANDING_SCHEMA}")
    if not (_text(doc.get("standing_id")) and re.fullmatch(r"cs-[a-z0-9-]{3,40}", doc["standing_id"])):
        p.append("standing_id: cs-<lowercase id>")

    def queue_entries(entries, where):
        out = []
        if not isinstance(entries, list):
            p.append(f"{where}: a list")
            return out
        for i, entry in enumerate(entries):
            if not (isinstance(entry, dict) and set(entry) == {"path", "role"} and _text(entry["path"])
                    and entry["role"] in QUEUE_ROLES):
                p.append(f"{where}[{i}]: {{path, role in {QUEUE_ROLES}}}")
                continue
            out.append(entry["path"])
        return out

    paths = queue_entries(doc.get("queues"), "queues")
    if len(paths) != len(set(paths)):
        p.append("queues: a path listed twice")
    kits = doc.get("kits")
    if not isinstance(kits, dict):
        p.append("kits: an object keyed by kit sha256")
        kits = {}
    for sha, e in kits.items():
        where = f"kits[{sha[:12]}]"
        if not HEX64.fullmatch(sha):
            p.append(f"{where}: key is a sha256")
        if not (isinstance(e, dict) and set(e) == KIT_ENTRY_KEYS):
            p.append(f"{where}: keys {sorted(KIT_ENTRY_KEYS)} (hand gates are derived, never declared)")
            continue
        src = e["source"]
        if not (isinstance(src, dict) and set(src) == {"commit", "path"} and isinstance(src["commit"], str)
                and HEX40.fullmatch(src["commit"]) and _text(src["path"])):
            p.append(f"{where}.source: {{commit: 40 hex, path}}")
        for line in ("line1", "line2"):
            if not _text(e[line]):
                p.append(f"KIT_EVIDENCE_MISSING: {where}.{line} is empty")
        bw = e["batch_window"]
        if not (bw in BATCH_RULES or (isinstance(bw, str) and HHMM.fullmatch(bw))):
            p.append(f"{where}.batch_window: one of {BATCH_RULES} or HH:MM-HH:MM")
    gates = doc.get("hand_gates")
    if not isinstance(gates, list):
        p.append("hand_gates: a list (extra named gates; the mandatory ones are derived)")
        gates = []
    for i, g in enumerate(gates):
        if not (isinstance(g, dict) and set(g) == {"id", "holds", "passed", "record"} and _text(g["id"])
                and isinstance(g["holds"], list) and g["holds"] and all(_text(x) for x in g["holds"])
                and type(g["passed"]) is bool and isinstance(g["record"], str)
                and (not g["passed"] or g["record"].strip())):
            p.append(f"hand_gates[{i}]: {{id, holds: [span_id], passed, record}}")
    records = doc.get("gate_records")
    if not (isinstance(records, list) and all(
            isinstance(r, dict) and set(r) == {"plan_id", "gate", "decision", "record"} and _text(r["plan_id"])
            and _text(r["gate"]) and r["decision"] in GATE_DECISIONS and _text(r["record"]) for r in records)):
        p.append(f"gate_records: a list of {{plan_id, gate, decision in {GATE_DECISIONS}, record}}")
    prior = doc.get("prior_spans")
    if not isinstance(prior, list):
        p.append("prior_spans: a list")
        prior = []
    seen = set()
    for i, s in enumerate(prior):
        if not (isinstance(s, dict) and set(s) == PRIOR_KEYS):
            p.append(f"prior_spans[{i}]: keys {sorted(PRIOR_KEYS)}")
            continue
        roster = s["roster"]
        if not (isinstance(roster, list) and roster and all(_text(x) for x in roster) and len(set(roster)) == len(roster)
                and isinstance(s["kit_sha256"], str) and HEX64.fullmatch(s["kit_sha256"])
                and s["kit_sha256"] in kits):
            p.append(f"prior_spans[{i}]: kit_sha256 (a kit of the index) and roster (its legs): the hand gates of a "
                     "hand-armed span are derived like any other (Mythos N2)")
        if not (_text(s["plan_id"]) and _text(s["campaign_id"]) and _text(s["block_id"])
                and type(s["legs"]) is int and 0 <= s["legs"] <= len(roster or []) and type(s["mixed"]) is bool
                and parse_time(s["t0"]) is not None and parse_time(s["closed"]) is not None
                and parse_time(s["closed"]) >= parse_time(s["t0"])
                and (s["desk_final"] is None or _text(s["desk_final"]))):
            p.append(f"prior_spans[{i}]: plan_id, campaign_id, block_id, legs run (0 to the roster's length), mixed, "
                     "t0 <= closed (ISO with offset), desk_final null or evidence")
        if s.get("plan_id") in seen:
            p.append(f"prior_spans[{i}]: {s.get('plan_id')} twice")
        seen.add(s.get("plan_id"))
        try:
            kit_class({"campaign_id": s.get("campaign_id", "")})
        except StandingError as error:
            p.extend(f"prior_spans[{i}]: {x}" for x in error.problems)
    wd = doc.get("withdrawn")
    if not (isinstance(wd, list) and all(_text(x) for x in wd)):
        p.append("withdrawn: a list of plan ids")
    disp = doc.get("dispositions")
    if not (isinstance(disp, list) and all(isinstance(d, dict) and set(d) == {"plan_id", "resolution", "record"}
                                           and _text(d["plan_id"]) and d["resolution"] in RESOLUTIONS
                                           and _text(d["record"]) for d in disp)):
        p.append(f"dispositions: a list of {{plan_id, resolution in {RESOLUTIONS}, record}}")
    sessions = doc.get("sessions")
    if not isinstance(sessions, list):
        p.append("sessions: a list")
        sessions = []
    for i, s in enumerate(sessions):
        if not (isinstance(s, dict) and set(s) == {"session_id", "kind", "route"} and _text(s["session_id"])
                and s["kind"] in SESSION_KINDS and _text(s["route"])):
            p.append(f"sessions[{i}]: {{session_id, kind in {SESSION_KINDS}, route}}")
    fb = doc.get("fallback")
    if not isinstance(fb, list):
        p.append("fallback: a list")
        fb = []
    f2 = []
    for i, f in enumerate(fb):
        kind = f.get("kind") if isinstance(f, dict) else None
        if kind == "F2" and set(f) == {"kind", "queues"}:
            got = queue_entries(f["queues"], f"fallback[{i}].queues")
            ok = bool(got) and len(got) == len(f["queues"])
            f2 += got
        elif kind == "F0":
            ok = (set(f) == {"kind", "standing_item", "worst_case_s"} and _text(f["standing_item"])
                  and type(f["worst_case_s"]) is int and f["worst_case_s"] > 0)
        else:
            ok = False
        if not ok:
            p.append(f"FALLBACK_INVALID: fallback[{i}] is {{kind: F2, queues}} or {{kind: F0, standing_item, "
                     "worst_case_s}} and nothing else (RL-172 (g) 9)")
    if set(f2) & set(paths):
        p.append("fallback: an F2 queue is also a counted queue")
    if doc.get("freeze2") is not None and not _text(doc.get("freeze2")):
        p.append("freeze2: null or the commit record of freeze 2")
    if p:
        raise StandingError(p)
    return doc


# --------------------------------------------------------------------------
# Queues: expiry from the first authenticated commit, append-only history, cross-queue identity
# --------------------------------------------------------------------------
def queue_expiry(doc, first_commit_epoch):
    """RL-172 (g) 3 and RL-149 section 2.8 line 3, read strictly (Mythos F13): seven days from the FIRST
    authenticated commit of the queue file on the audit branch, or the file's ``expires_at`` if sooner. An
    append never renews the authority."""
    return min(first_commit_epoch + QUEUE_TTL_S, parse_time(doc["expires_at"]))


def append_only_problems(versions):
    """``versions``: the queue documents in commit order, oldest first. Each must keep every earlier span
    byte-for-byte, in order, and keep the queue id (RL-149 section 2.8 line 3)."""
    problems = []
    for older, newer in zip(versions, versions[1:]):
        if not (isinstance(older, dict) and isinstance(newer, dict)):
            problems.append("a historical version does not parse")
            continue
        if older.get("queue_id") != newer.get("queue_id"):
            problems.append(f"queue_id changed {older.get('queue_id')} -> {newer.get('queue_id')}")
        old, new = older.get("spans") or [], newer.get("spans") or []
        if new[:len(old)] != old:
            problems.append(f"spans of {older.get('queue_id')} were edited or removed, not appended")
    return problems


def cross_queue_reasons(views, disposed=frozenset()):
    """Mythos F12: a plan id in two queues, or one kit leg queued twice without ``rerun_of``, is a
    contradiction, whatever the queues' order. A span the lead disposed of as ``rerun`` or ``withdrawn``
    frees its legs: its re-run may be queued anywhere (Mythos N3)."""
    out, plans, legs = [], {}, {}
    for v in views:
        for s in (v.get("doc") or {}).get("spans", []):
            pid = q.plan_id(s)
            if pid in disposed:
                continue
            if pid in plans and plans[pid] != v["path"]:
                out.append(reason("QUEUE_DUPLICATE", f"{pid} in {plans[pid]} and {v['path']}"))
            plans.setdefault(pid, v["path"])
            for leg in s.get("legs", []):
                key = (s["kit"]["sha256"], leg)
                if key in legs and legs[key][0] != v["path"] and s.get("rerun_of") is None:
                    out.append(reason("QUEUE_DUPLICATE", f"{leg} of kit {key[0][:12]} in {legs[key][0]} "
                                                         f"({legs[key][1]}) and {v['path']} ({s['span_id']})"))
                legs.setdefault(key, (v["path"], s["span_id"]))
    return out


def queue_reasons(view, now, has_pending):
    """Every listed queue's own integrity, read before any candidate is chosen (Sol 5): a missing, invalid,
    rewritten or halted queue halts the controller whatever its priority."""
    out = list(view["reasons"])
    doc = view["doc"]
    if doc is None:
        return out
    if doc.get("halt"):
        out.append(reason("QUEUE_HALT", f"{doc['queue_id']}: {doc['halt'].get('reason')}"))
    if any(e is not None and e > now + CLOCK_SKEW_S for e in (view["commit_epoch"], view.get("first_commit_epoch"))):
        out.append(reason("QUEUE_COMMIT_IN_FUTURE", doc["queue_id"]))      # first or last commit (Mythos N8)
    if has_pending:
        if view["first_commit_epoch"] is None or now > queue_expiry(doc, view["first_commit_epoch"]):
            when = (datetime.fromtimestamp(queue_expiry(doc, view["first_commit_epoch"]), ZONE).isoformat()
                    if view["first_commit_epoch"] is not None else "unknown")
            out.append(reason("QUEUE_EXPIRED", f"{doc['queue_id']} expired at {when}"))
        if not (isinstance(doc.get("standing_notice"), dict) and type(doc["standing_notice"].get("issue")) is int):
            out.append(reason("QUEUE_NO_NOTICE", doc["queue_id"]))
    return out


# --------------------------------------------------------------------------
# Evidence: vetoes, the watcher stamp, desk verdicts, sessions
# --------------------------------------------------------------------------
def veto_reasons(issues, owner):
    """RL-149 section 2.8 line 6, read strictly: any open issue by the owner labelled ``cadence-stop``, or
    labelled ``directive`` whose title or first body line starts STOP/NO/HALT/VETO, halts every arm,
    whatever it names (a span-scoped veto also halts: the magistrate reads it). Comments are never read.
    ``issues`` None means the read failed: that is a retry, never "no veto"."""
    if issues is None:
        return [reason("ISSUES_UNREADABLE")]
    out = []
    for issue in issues:
        if (issue.get("author") or {}).get("login") != owner or str(issue.get("state", "OPEN")).upper() != "OPEN":
            continue
        labels = {(x.get("name") if isinstance(x, dict) else x) for x in issue.get("labels") or []}
        if "cadence-stop" in labels:
            out.append(reason("CADENCE_STOP_OPEN", f"#{issue.get('number')}: {issue.get('title', '')[:80]}"))
            continue
        if "directive" not in labels:
            continue
        first = (issue.get("body") or "").strip().splitlines()[:1]
        if VETO_WORD.match(issue.get("title") or "") or (first and VETO_WORD.match(first[0])):
            out.append(reason("VETO_OPEN", f"#{issue.get('number')}: {issue.get('title', '')[:80]}"))
    return out


def watcher_reasons(stamp, commit_epoch, now, watcher_name):
    """RL-149 section 2.8 line 7: the results-ref watcher was live within 24 h, by the lead's stamp. The
    stamp is a committed file on the audit branch; it must name the configured watcher, and its time may not
    be after its own commit. It is re-read at every arm (never cached) and its commit is bound into the arm
    record; whether one sub-24 h observation may serve several arms is the reading RL-149 line 7 gives
    ("live within the last 24 h"), and is put to the research lead (Sol 12)."""
    if stamp is None or commit_epoch is None:
        return [reason("WATCHER_STAMP_MISSING")]
    if not (isinstance(stamp, dict) and stamp.get("schema") == WATCHER_STAMP_SCHEMA
            and stamp.get("watcher") == watcher_name and parse_time(stamp.get("observed_live_at")) is not None
            and _text(stamp.get("by"))):
        return [reason("WATCHER_STAMP_INVALID", f"schema, watcher {watcher_name!r}, observed_live_at, by")]
    seen = parse_time(stamp["observed_live_at"])
    if seen > commit_epoch + CLOCK_SKEW_S or commit_epoch > now + CLOCK_SKEW_S:
        return [reason("WATCHER_STAMP_INVALID", "observed after its commit, or committed in the future")]
    if now - seen > WATCHER_TTL_S:
        return [reason("WATCHER_STALE", f"observed {stamp['observed_live_at']}, {(now - seen) / 3600:.1f} h ago")]
    return []


def watcher_lease(stamp):
    """The last instant the stamp still serves an arm."""
    return parse_time(stamp["observed_live_at"]) + WATCHER_TTL_S


def verdict_state(entry, *, run, accept_mock):
    """One controller span's desk verdict by FORMAT.md section 4. ``entry`` is what the controller read from the
    span's signed verdict ref: ``{"doc": verdict}`` (``desk_transport.read_verdict`` verified the signature by
    ``cadence-desk``, the subject, the trailers, ``verify_verdict`` and the plan id), ``{"error": text}`` when that
    reader refused, or None when there is no ref yet. ``run`` is the controller's own record of the span (its
    armed identities and the anchor it published). Returns ``(state, halts, kit_holds)``."""
    if entry is None:
        return "pending", [], []
    pid = run.plan_id
    if entry.get("error"):
        return "pending", [reason("DESK_VERDICT_INVALID", f"{pid}: {entry['error']}"[:300])], []
    doc = entry["doc"]
    armed = run.extra.get("armed") or {}
    ident = {k: armed.get(k) for k in ("plan_id", "queue_id", "span_id", "attempt")}
    if ident["plan_id"] != pid or any(doc.get(k) != v for k, v in ident.items()):
        return "pending", [reason("DESK_VERDICT_INVALID", f"{pid}: the verdict names another span")], []
    if (doc.get("identities") or {}).get("manifest_sha256") != run.bundle_sha256:
        # A verdict on another bundle is not this span's: never final, and a contradiction worth a page.
        return "pending", [reason("DESK_VERDICT_INVALID", f"{pid}: anchor {str((doc.get('identities') or {}).get('manifest_sha256'))[:12]} "
                                                          f"is not the published {str(run.bundle_sha256)[:12]}")], []
    # ``accept_mock`` is the synthetic switch (the production config refuses accept_mock_verdicts); the desk's own
    # counts_as_final keeps every other clause.
    final = desk_final.counts_as_final(doc, manifest_sha256=run.bundle_sha256, allow_mock=accept_mock is True,
                                       **{k: v for k, v in ident.items()})
    # The replay check needs the campaign's signed history (Mythos N11, Sol R8): a verdict built on a typed or
    # omitted history never counts.
    final = final and doc.get("history_source") == "signed-records"
    halts = []
    if doc.get("next_arm_hold") is True:
        codes = sorted({str(h.get("code")) for h in doc.get("holds") or [] if h.get("scope") == "queue"})
        halts.append(reason("DESK_HOLD", f"{pid}: {', '.join(codes)}", span=pid))
    kit_holds = sorted({h.get("gate") for h in doc.get("holds") or []
                        if str(h.get("scope", "")).startswith("kit:") and h.get("gate")})
    return ("final" if final else "pending"), halts, kit_holds


def session_reasons(standing, ready_records, done_ids):
    """RL-172 (f): a READY record from the lead holds everything of lower priority. It names a session of
    the standing index, whose own route the magistrate runs. The controller never launches it."""
    known = {s["session_id"]: s for s in standing["sessions"]}
    out = []
    for rec in ready_records:
        if not (isinstance(rec, dict) and rec.get("schema") == SESSION_READY_SCHEMA
                and rec.get("session_id") in known and _text(rec.get("by"))
                and parse_time(rec.get("ready_at")) is not None):
            out.append(reason("SESSION_INVALID", str(rec.get("session_id") if isinstance(rec, dict) else rec)))
            continue
        if rec["session_id"] in done_ids:
            continue
        s = known[rec["session_id"]]
        out.append(reason("V4_SESSION_READY", f"{s['session_id']} ({s['kind']}): route {s['route']}"))
    return out


# --------------------------------------------------------------------------
# The ledger: every span in machine order, across queues
# --------------------------------------------------------------------------
@dataclass
class Run:
    plan_id: str
    kind: str              # campaign | f2 | F0 | v4 | other
    phase: str | None
    block_id: str | None
    legs: int              # legs run (finished) for a closed controller span; planned while live
    mixed: bool
    t0: float              # the runner's own start for a closed controller span
    closed: float | None
    status: str            # LIVE | CLOSED_OK | STOPPED | REFUSED | ...
    source: str            # prior | controller | external
    campaign: str | None = None
    desk: str = "pending"  # final | pending
    bundle_sha256: str | None = None
    gates: list = field(default_factory=list)
    resolution: str | None = None
    extra: dict = field(default_factory=dict)


BAD = ("STOPPED", "REFUSED", "FAULT", "STRANDED", "CLOSE_UNPROVEN", "LAUNCH_REFUSED", "INDETERMINATE",
       "RECEIPT_MISSING")


def build_runs(standing, controller_records, external_runs, kits=None):
    """Every run in machine order. A prior (hand-armed) span's gates are derived from its kit and roster like a
    controller span's (Mythos N2); ``kits`` maps sha256 -> kit, and a prior span whose kit is not in it carries
    ``gates_unknown``."""
    disp = {d["plan_id"]: d["resolution"] for d in standing["dispositions"]}
    runs = []
    for s in standing["prior_spans"]:
        cls = kit_class({"campaign_id": s["campaign_id"]})
        kit = (kits or {}).get(s["kit_sha256"])
        gates = derived_gates(kit, s["roster"]) if kit is not None else []
        runs.append(Run(s["plan_id"], "campaign" if cls["k2"] else "f2", cls["phase"], s["block_id"], s["legs"],
                        s["mixed"], parse_time(s["t0"]), parse_time(s["closed"]), "CLOSED_OK", "prior",
                        campaign=s["campaign_id"], desk="final" if s["desk_final"] else "pending", gates=gates,
                        resolution=disp.get(s["plan_id"]),
                        extra={"kit_sha256": s["kit_sha256"], "roster": list(s["roster"]),
                               "gates_unknown": kits is not None and kit is None}))
    for r in controller_records:
        closed = r.get("closed_epoch")
        if closed is not None and r.get("legs_finished") is not None:
            legs_run = r["legs_finished"]
        elif r["status"] in BAD:
            legs_run = 0           # never ran, or no close: nothing to count on the date (Mythos N16)
        else:
            legs_run = len(r["legs"])
        runs.append(Run(r["plan_id"], r["kind"], r["phase"], r["block_id"], legs_run,
                        r["mixed"], r.get("runner_t0") or r["t0_epoch"], closed, r["status"], "controller",
                        campaign=r.get("campaign_id"), bundle_sha256=r.get("bundle_sha256"),
                        gates=list(r.get("gates") or []), resolution=disp.get(r["plan_id"]),
                        extra={"kit_sha256": r.get("kit_sha256"), "armed": r.get("armed") or {},
                               "roster": r["legs"]}))
    for e in external_runs:
        runs.append(Run(e["run_id"], e["kind"], None, None, 0, False, e["t0_epoch"], e.get("closed_epoch"),
                        "CLOSED_OK" if e.get("restore") == "proven" else "CLOSE_UNPROVEN", "external",
                        resolution=disp.get(e["run_id"])))
    runs.sort(key=lambda r: (r.t0, r.plan_id))
    return runs


def apply_verdicts(runs, verdicts, *, accept_mock):
    """Mark controller spans desk-final from the Air's verdicts (FORMAT.md section 4). Returns halts: a named-stop
    hold not cleared by the lead, an invalid verdict, and a verdict whose hand gates disagree with the gates the
    controller derived."""
    halts = []
    for run in runs:
        if run.source != "controller" or run.kind not in ("campaign", "f2"):
            continue
        state, hs, kit_holds = verdict_state(verdicts.get(run.plan_id), run=run, accept_mock=accept_mock)
        run.desk = state
        if run.resolution in RESOLUTIONS:   # cleared lifts the hold; rerun and withdrawn also take it out (N3)
            hs = [h for h in hs if h["code"] != "DESK_HOLD"]
        halts += hs
        if verdicts.get(run.plan_id) is not None and not hs:
            mine = sorted(DESK_GATE_NAMES[g] for g in run.gates)
            if sorted(kit_holds) != mine:
                halts.append(reason("GATE_DISAGREEMENT", f"{run.plan_id}: desk {kit_holds}, controller {mine}",
                                    span=run.plan_id))
    return halts


def k2_reasons(runs, span_id=None):
    """Line 9 in machine order across every queue (RL-165 section 6; RL-172 (g) 2): the new span is campaign
    span n; every campaign span up to n-2 must be desk-final. Stricter than "span n-2 only". A span the lead
    resolved as ``rerun`` or ``withdrawn`` (FORMAT.md section 4 item 4) leaves the count."""
    campaign = [r for r in runs if r.kind == "campaign" and r.resolution not in ("rerun", "withdrawn")]
    n = len(campaign) + 1
    owed = [r.plan_id for r in campaign[:max(0, n - 2)] if r.desk != "final"]
    if owed:
        return [reason("K2_DESK_DEBT", f"campaign span {n}: desk not final for {', '.join(owed)}", span=span_id)]
    return []


def last_close(runs):
    closed = [r for r in runs if r.closed is not None]
    return max(closed, key=lambda r: r.closed) if closed else None


def gap_reasons(runs, now, census_epoch=None, span_id=None):
    """The floor after the latest close of anything on the host: 300 s after a campaign span, 1,200 s after
    F0, F2 or any other close. A controller span's close is the end of its own close work (Mythos F25), so the
    floor counts after the bundle push, not after the receipt."""
    last = last_close(runs)
    ends = []
    if last is not None:
        ends.append(last.closed + (GAP_AFTER_CAMPAIGN_S if last.kind == "campaign" else GAP_AFTER_OTHER_S))
    if census_epoch is not None and (last is None or census_epoch > last.closed + 1):
        ends.append(census_epoch + GAP_AFTER_OTHER_S)
    until = max(ends) if ends else None
    if until is not None and now < until:
        return [reason("GAP", f"{until - now:.0f} s to go", eta=until, span=span_id)]
    return []


def date_reasons(span, cls, t0, runs, queued, standing):
    """RL-172 (a), enforced at the arm. ``queued``: (span, cls) of every unrun counted span in every queue,
    for the qualification/development date separation. A closed span counts the legs it ran (Mythos F8)."""
    sid = span["span_id"]
    day = local_date(t0)
    out = []
    if day < span["not_before"]:
        return [reason("NOT_BEFORE", f"{sid}: not before {span['not_before']}", eta=date_start(span["not_before"]),
                       span=sid)]
    if not cls["dated"]:
        return []
    if day > span["not_before"]:
        out.append(reason("DATE_MISSED", f"{sid}: t0-date {day} is after its date {span['not_before']}", span=sid))
    if t0 > date_end(day) - MIDNIGHT_MARGIN_S:
        out.append(reason("MIDNIGHT", f"{sid}: within {MIDNIGHT_MARGIN_S} s of the end of {day}",
                          eta=date_end(day), span=sid))
    same = [r for r in runs if r.kind == "campaign" and local_date(r.t0) == day
            and r.resolution != "withdrawn"]
    if cls["phase"] == "development":
        dev = sum(r.legs for r in same if r.phase == "development") + len(span["legs"])
        mixed = sum(r.legs for r in same if r.phase == "development" and r.mixed) + (
            len(span["legs"]) if cls["mixed"] else 0)
        if mixed > DEV_MIXED_MAX:
            out.append(reason("DATE_DEV_MIXED_CAP", f"{day}: {mixed} mixed-size development legs", span=sid))
        if dev > DEV_MAX:
            out.append(reason("DATE_DEV_CAP", f"{day}: {dev} development legs", span=sid))
        if any(r.phase == "qualification" for r in same):
            out.append(reason("DATE_QUAL_DEV_OVERLAP", f"{day} holds qualification", span=sid))
    if cls["phase"] == "qualification":
        if standing.get("freeze2") is None:
            return [reason("FREEZE2", sid, span=sid)]
        if any(r.phase == "development" for r in same) or any(
                c["phase"] == "development" and s["not_before"] == day for s, c in queued):
            out.append(reason("DATE_QUAL_DEV_OVERLAP", f"{day} holds or is planned for development", span=sid))
        blocks = {r.block_id for r in runs if r.phase == "qualification"} | {
            s["block_id"] for s, c in queued if c["phase"] == "qualification"} | {span["block_id"]}
        on_day = {r.block_id for r in same if r.phase == "qualification"} | {span["block_id"]}
        if len(blocks) >= 2 and on_day >= blocks:
            out.append(reason("DATE_QUAL_SINGLE", f"every qualification block would be on {day}", span=sid))
    return out


def _disposed(standing, kinds=("rerun", "withdrawn")):
    return {d["plan_id"] for d in standing["dispositions"] if d["resolution"] in kinds}


def pilot_reasons(span, kit, queue_role, view, runs, all_views, standing):
    """RL-172 (g) 4 with the gates derived. A span holding the kit's first leg is that kit's pilot: it must be
    alone in a smoke queue (spans the lead disposed of as ``rerun`` or ``withdrawn`` do not count, so a refused
    pilot's re-run is appended to the same smoke queue; Mythos N3), and no other span of the campaign may be queued
    anywhere until a pilot closed clean and its class A gate was released. Any other span needs such a released
    pilot: a controller span, or a prior (hand-armed) span whose gates are derived the same way (Mythos N2)."""
    sid, campaign = span["span_id"], kit["campaign_id"]
    out = []
    disposed = _disposed(standing)
    first = (kit.get("legs") or [{}])[0].get("leg_id")
    released = {(r["plan_id"], r["gate"]) for r in standing["gate_records"] if r["decision"] == "release"}
    pilots = [r for r in runs if r.campaign == campaign and CLASS_A in r.gates and r.plan_id not in disposed]
    released_pilot = any(r.status == "CLOSED_OK" and (r.plan_id, CLASS_A) in released for r in pilots)
    live_spans = [s for s in view["doc"]["spans"] if q.plan_id(s) not in disposed]
    if first in span["legs"]:
        if queue_role != "smoke" or len(live_spans) != 1:
            out.append(reason("SMOKE_QUEUE_NOT_PILOT_ONLY", f"{sid} holds {first}: a {queue_role} queue of "
                                                            f"{len(live_spans)} live span(s)", span=sid))
        others = [s["span_id"] for v in all_views for s in (v.get("doc") or {}).get("spans", [])
                  if s is not span and s["kit"]["sha256"] == span["kit"]["sha256"]
                  and q.plan_id(s) not in v["closed_ids"] and q.plan_id(s) not in v["withdrawn_ids"]
                  and q.plan_id(s) not in disposed]
        if others and not released_pilot:
            out.append(reason("SMOKE_REMAINDER_STAGED", f"{others[:4]} queued with pilot {sid}", span=sid))
    elif not any(r.status == "CLOSED_OK" for r in pilots):
        out.append(reason("PILOT_MISSING", f"{sid}: no pilot of {campaign} closed clean", span=sid))
    return out


def gate_reasons(span, campaign, runs, standing, record_epochs=None):
    """Every derived gate raised by an earlier span of this campaign, a controller span or a prior (hand-armed)
    one (Mythos N2), holds this span until the lead's release record for that span and gate (FORMAT.md section 4
    item 2; Sol 6). A ``hold`` record keeps it held. A release committed before the span it releases closed is a
    contradiction (Mythos N14): ``record_epochs`` maps (plan_id, gate) to the record's first commit time. The lead's
    extra named gates (``hand_gates``) hold the spans they name."""
    sid = span["span_id"]
    decisions = {(r["plan_id"], r["gate"]): r["decision"] for r in standing["gate_records"]}
    disposed = _disposed(standing)
    out = []
    for run in runs:
        if run.source not in ("controller", "prior") or run.campaign != campaign or run.plan_id in disposed:
            continue
        if run.extra.get("gates_unknown"):
            out.append(reason("PRIOR_GATES_UNKNOWN", f"{run.plan_id}: kit {str(run.extra.get('kit_sha256'))[:12]} "
                                                     "not readable", span=sid))
            continue
        for gate in run.gates:
            if decisions.get((run.plan_id, gate)) != "release":
                out.append(reason("HAND_GATE", f"{gate} of {run.plan_id} holds {campaign}", span=sid))
                continue
            if record_epochs is not None:
                epoch = record_epochs.get((run.plan_id, gate))
                if epoch is None or run.closed is None or epoch < run.closed:
                    out.append(reason("GATE_RECORD_PREMATURE", f"{gate} of {run.plan_id}: released at "
                                                               f"{epoch}, closed at {run.closed}", span=sid))
    for gate in standing["hand_gates"]:
        if sid in gate["holds"] and not gate["passed"]:
            out.append(reason("HAND_GATE", f"{gate['id']} holds {sid}", span=sid))
    return out


def prior_reasons(standing, views, receipts):
    """A prior span's declared roster and kit must equal its queue entry, when a listed queue holds it, and its
    receipt on the host, when the census finds one (``receipts``: plan_id -> {roster, kit_sha256}). Gates derived
    from a wrong roster would be wrong gates (Mythos N2)."""
    out = []
    entries = {q.plan_id(s): s for v in views for s in (v.get("doc") or {}).get("spans", [])}
    for p in standing["prior_spans"]:
        pid = p["plan_id"]
        entry, receipt = entries.get(pid), (receipts or {}).get(pid)
        if entry is not None and (entry["legs"] != p["roster"] or entry["kit"]["sha256"] != p["kit_sha256"]):
            out.append(reason("PRIOR_CONTRADICTS", f"{pid}: the queue entry says {entry['legs']} on "
                                                   f"{entry['kit']['sha256'][:12]}"))
        if receipt is not None and (receipt.get("roster") != p["roster"]
                                    or receipt.get("kit_sha256") != p["kit_sha256"]):
            out.append(reason("PRIOR_CONTRADICTS", f"{pid}: its receipt says {receipt.get('roster')} on "
                                                   f"{str(receipt.get('kit_sha256'))[:12]}"))
    return out


# --------------------------------------------------------------------------
# The desk-final inputs on the MBP side (RL-172 (c) 1 to 4), on the packed bundle's bytes
# --------------------------------------------------------------------------
def desk_input_reasons(*, span, kit_sha, kit, receipt, summaries, plan):
    """The roster, identity and completeness checks a desk-final needs, done at the close on the MBP from the
    packed bundle (the same bytes that are pushed). ``summaries``: leg_id -> leg_summary dict (bundle order);
    ``plan``: the runner's span_plan.json (or None). Zero leg rows is a stop."""
    sid, roster = span["span_id"], list(span["legs"])
    out = []

    def bad(detail):
        out.append(reason("ROSTER_MISMATCH", f"{sid}: {detail}", span=sid))

    if not summaries:
        out.append(reason("NO_LEG_ROWS", f"{sid}: 0 leg rows of {len(roster)}", span=sid))
    if receipt.get("roster") != roster:
        bad(f"receipt roster {receipt.get('roster')} != queue {roster}")
    if (receipt.get("kit") or {}).get("sha256") != kit_sha:
        bad("receipt kit sha is not the queue's pin")
    if (receipt.get("kit") or {}).get("frozen_commit") != kit["frozen"]["commit"]:
        bad("receipt frozen commit is not the kit's")
    if receipt.get("legs_planned") != len(roster):
        bad(f"legs_planned {receipt.get('legs_planned')} != {len(roster)}")
    rows = [leg.get("leg_id") for leg in receipt.get("legs") or []]
    if len(rows) != len(set(rows)):
        bad(f"duplicate leg rows in the receipt {rows}")
    if rows != roster[:len(rows)]:
        bad(f"receipt legs {rows} are not the roster's order")
    if plan is not None and [leg.get("leg_id") for leg in plan.get("legs", [])] != roster:
        bad("span_plan legs are not the roster")
    if plan is None and summaries:
        bad("span_plan.json missing")
    if list(summaries) != rows[:len(summaries)]:
        bad(f"bundle legs {list(summaries)} are not the receipt's {rows}")
    for leg_row in receipt.get("legs") or []:
        lid = leg_row.get("leg_id")
        summary = summaries.get(lid)
        if summary is None:
            if receipt.get("rc") == 0:
                bad(f"{lid}: no leg_summary in the bundle")
            continue
        if summary.get("leg_id") != lid:
            bad(f"{lid}: summary names {summary.get('leg_id')}")
        if summary.get("attempts") != len(leg_row.get("attempts") or []):
            bad(f"{lid}: attempts {summary.get('attempts')} != receipt {len(leg_row.get('attempts') or [])}")
        ref = summary.get("span_reference")
        if isinstance(ref, dict):   # kit v1.1 consumer: the reference is the first leg's accepted attempt
            first = (receipt.get("legs") or [{}])[0]
            if ref.get("leg_id") != first.get("leg_id") or ref.get("attempt") != len(first.get("attempts") or []):
                bad(f"{lid}: span reference {ref.get('leg_id')} a{ref.get('attempt')} is not the first leg's "
                    f"accepted attempt")
    return out


def receipt_command_reasons(receipt, expected_windows):
    """The close's command result: the runner's own restore and feed stops, read from its receipt."""
    out = []
    result = receipt.get("span_result") or {}
    clean = (receipt.get("rc") == 0 and result.get("chain_exit_code") == 0 and result.get("chain_outcome") == "COMPLETE"
             and result.get("fault") is False and result.get("outcome") == "MEASURED_OK"
             and receipt.get("legs_finished") == receipt.get("legs_planned") and not receipt.get("error"))
    if not clean:
        out.append(reason("RECEIPT_NOT_CLEAN", f"rc {receipt.get('rc')}, {result.get('verdict')}, "
                                               f"{receipt.get('error', '')}"[:200]))
    steps = {s.get("name"): s for s in receipt.get("steps") or []}
    close = [n for n in steps if n == "restore" or n.startswith(("stop-", "close-"))]
    if "restore" not in steps or any(steps[n].get("rc") != 0 for n in close):
        out.append(reason("CLOSE_UNPROVEN", "the receipt's restore or a feed stop is missing or failed: "
                                            + ", ".join(f"{n}={steps[n].get('rc')}" for n in close)))
    feeds = receipt.get("feeds") or {}
    if not feeds:
        out.append(reason("CLOSE_UNPROVEN", "the receipt names no feed"))
    for name, feed in feeds.items():
        if not (feed.get("stop") or {}).get("proven_stopped"):
            out.append(reason("CLOSE_UNPROVEN", f"feed {name} not proven stopped"))
    out += soak_attempt_reasons(receipt, clean)
    if receipt.get("batch_windows") != expected_windows:
        out.append(reason("ROSTER_MISMATCH", f"batch_windows {receipt.get('batch_windows')} != {expected_windows}"))
    return out


SOAK_RETRIES = 1   # RL-171 at the qualification pin: one retry of a soak refused for settle or quiet


def soak_attempt_reasons(receipt, clean):
    """The receipt's ``soak_attempts`` (RL-171, pin e1b85a59c on). A retried soak is normal, not a stop:
    every attempt but the last was refused (exit 5, renamed ``soak.rejected<N>``), there are at most
    ``SOAK_RETRIES`` + 1, and a clean span's last soak was accepted. A receipt from a pin before RL-171
    has no such field; it is accepted only with exactly one ``soak`` step (rc 0 when clean) and no
    ``soak.a<N>`` step."""
    steps = receipt.get("steps") or []
    names = [s.get("name") for s in steps]
    retries = [n for n in names if isinstance(n, str) and re.fullmatch(r"soak\.a\d+", n)]
    attempts = receipt.get("soak_attempts")
    if attempts is None:
        soak = [s for s in steps if s.get("name") == "soak"]
        if retries or len(soak) > 1 or (clean and (len(soak) != 1 or soak[0].get("rc") != 0)):
            return [reason("ROSTER_MISMATCH", f"no soak_attempts but soak steps {len(soak)} + {retries}")]
        return []
    if not isinstance(attempts, list) or (clean and not attempts) or len(attempts) > SOAK_RETRIES + 1:
        return [reason("ROSTER_MISMATCH", f"soak_attempts {attempts!r:.120}: 1 to {SOAK_RETRIES + 1} expected")]
    out = []
    if any(not isinstance(a, dict) or a.get("attempt") != i + 1 for i, a in enumerate(attempts)):
        out.append(reason("ROSTER_MISMATCH", "soak_attempts are not numbered 1..n"))
    elif any(not a.get("refused") for a in attempts[:-1]):
        out.append(reason("ROSTER_MISMATCH", "a soak was retried after an attempt that was not refused"))
    elif clean and attempts[-1].get("refused"):
        out.append(reason("ROSTER_MISMATCH", "a clean receipt whose last soak was refused"))
    elif len(retries) != len(attempts) - 1:
        out.append(reason("ROSTER_MISMATCH", f"{len(attempts)} soak attempts but retry steps {retries}"))
    return out


# --------------------------------------------------------------------------
# Host proofs (typed; the controller fills them, this judges them)
# --------------------------------------------------------------------------
PROOF_LINES = {
    # name -> which proof needs it
    "powermode": ("arm", "close"), "ac_power": ("arm", "close"), "network_time": ("arm", "close"),
    "kernel_frequency": ("arm", "close"), "high_power_marker": ("arm", "close"), "launchd_labels": ("arm", "close"),
    "sudo_kill": ("arm",), "measurement_mode": ("arm", "close"),
    "monitors": ("arm", "close"), "root_powermetrics": ("arm", "close"), "span_processes": ("arm", "close"),
    "launch_fence": ("arm", "close"), "agents": ("arm",), "signing": ("arm",), "verdict_signers": ("arm",),
}


def proof_reasons(proof, kind):
    """``proof``: {line: {ok: bool|None, detail, agent_only?: bool}}. A missing line or ``ok`` None (not
    observed) fails: missing evidence never passes. Agents present at the arm is a wait, not a halt;
    a measurement_mode verify whose only failures are the agent line is the same wait. The signing line
    is its own halt (Mythos F11)."""
    code = "HOST_PROOF_FAILED" if kind == "arm" else "CLOSE_UNPROVEN"
    out, waits = [], []
    for line, kinds in PROOF_LINES.items():
        if kind not in kinds:
            continue
        row = proof.get(line)
        if row is None or row.get("ok") is None:
            out.append(reason("SIGNING_UNAVAILABLE" if line in ("signing", "verdict_signers") else code,
                              f"{line}: not observed"))
        elif row["ok"] is False:
            if kind == "arm" and (line == "agents" or (line == "measurement_mode" and row.get("agent_only"))):
                waits.append(reason("AGENT_PRESENT", f"{line}: {row.get('detail', '')}"[:200]))
            elif line in ("signing", "verdict_signers"):
                out.append(reason("SIGNING_UNAVAILABLE", str(row.get("detail", ""))[:200]))
            else:
                out.append(reason(code, f"{line}: {row.get('detail', '')}"[:200]))
    return out + waits


# --------------------------------------------------------------------------
# The host's newest close and the journal-copy gate (item 331's copy_gate; Sol 11, Mythos F18)
# --------------------------------------------------------------------------
CAMPAIGN_RECEIPT = re.compile(r"/(?P<campaign>cl-[a-z0-9-]+)/(?P<plan>cq-[a-z0-9-]+-a[0-9]+)-[0-9]{8}T[0-9]{6}Z/"
                              r"runner_receipt\.json$")


def census_reasons(census, runs, output_root, copy_markers):
    """``census``: {"newest": (epoch, path), "campaign": [paths under the output root]} or an error string.

    * Every campaign receipt under the output root belongs to a span the ledger knows (prior or controller);
      an unknown one is a halt (Mythos F18: a hand-armed span missing from ``prior_spans``).
    * The copy gate, bound to the ONE newest close: if the newest receipt is a campaign span's, its journal
      copy marker (``<plan_id>.ok``, written by the lead after a hash-verified copy) must exist and be
      non-empty before another arm. After a non-campaign close the Check covers the copy."""
    if isinstance(census, str) or census is None:
        return [reason("CENSUS_FAILED", str(census))]
    out = []
    known = {r.plan_id for r in runs if r.source in ("prior", "controller")}
    for path in census["campaign"]:
        m = CAMPAIGN_RECEIPT.search(path)
        if m is None or m.group("plan") not in known:
            out.append(reason("UNKNOWN_CAMPAIGN_RECEIPT", path))
    _epoch, newest = census["newest"]
    m = CAMPAIGN_RECEIPT.search(newest) if newest.startswith(output_root.rstrip("/") + "/") else None
    if m is not None:
        plan_id = m.group("plan")
        if not copy_markers.get(plan_id):
            out.append(reason("JOURNAL_COPY", f"no journal-copy marker for {plan_id}, the newest close ({newest})"))
    return out


# --------------------------------------------------------------------------
# Selection: what the controller does next, from one fresh snapshot
# --------------------------------------------------------------------------
@dataclass
class Decision:
    action: str                       # arm | arm-fallback | wait | halt | cede | page
    reasons: list
    candidate: dict | None = None     # {queue_path, span, kit_sha, cls, role}
    gates: dict = field(default_factory=dict)   # span_id -> [reason codes] (the critical-path ledger)

    def as_dict(self):
        c = self.candidate
        return {"action": self.action, "reasons": self.reasons, "gates": self.gates,
                "candidate": None if c is None else {"queue_path": c["queue_path"], "span_id": c["span"]["span_id"],
                                                    "plan_id": q.plan_id(c["span"]), "kit_sha256": c["kit_sha"],
                                                    "class": c["cls"], "role": c["role"]}}


def _pending(view):
    doc = view.get("doc") or {"spans": []}
    return [s for s in doc["spans"] if q.plan_id(s) not in view["closed_ids"]
            and q.plan_id(s) not in view["withdrawn_ids"]]


def select(snap):
    """``snap`` keys:

    now, standing, input_reasons (list, from reading), queues and fallback_queues: [{path, role, fallback, doc,
    commit_epoch, first_commit_epoch, kits: {sha: kit}, reasons, closed_ids, withdrawn_ids}], runs
    (``build_runs`` with verdicts applied), desk_halts, vetoes, watcher, sessions, census_reasons, census_epoch,
    fallback, plan_worst: callable(candidate) -> seconds or None.
    """
    now, standing = snap["now"], snap["standing"]
    gates = {}
    globals_ = (list(snap["input_reasons"]) + list(snap["desk_halts"]) + list(snap["vetoes"]) + list(snap["watcher"])
                + list(snap.get("census_reasons", [])))
    if standing is None:      # the index could not be read: never a pass
        rs = globals_ or [reason("STANDING_MISSING")]
        return Decision("halt" if category(rs) == "halt" else "wait", rs, gates=gates)
    disposed = {d["plan_id"] for d in standing["dispositions"]}
    bad = [r for r in snap["runs"] if r.status in BAD and r.plan_id not in disposed]
    globals_ += [reason("FOREIGN_CLOSE_UNPROVEN" if r.source == "external" else "SPAN_BAD_TERMINAL",
                        f"{r.plan_id} is {r.status}", span=r.plan_id) for r in bad]
    live = [r for r in snap["runs"] if r.status == "LIVE"]
    if live:
        globals_.append(reason("SPAN_LIVE", ", ".join(r.plan_id for r in live)))
    views = list(snap["queues"]) + list(snap["fallback_queues"])
    for view in views:   # Sol 5: every listed queue's integrity first, whatever its priority
        globals_ += queue_reasons(view, now, bool(_pending(view)))
    globals_ += cross_queue_reasons(views, _disposed(standing))
    globals_ += prior_reasons(standing, views, snap.get("receipts"))
    heads = [_pending(v)[0]["span_id"] for v in views if v.get("doc") and _pending(v)]

    def held(action, rs):
        # Sol R6: a global reason is a prerequisite of every pending head span; the per-span ledger records it.
        for sid in heads:
            gates[sid] = [r["code"] for r in rs]
        return Decision(action, rs, gates=gates)

    if category(globals_) == "halt":
        return held("halt", [r for r in globals_ if r["category"] == "halt"])
    if snap["sessions"]:
        cat = category(snap["sessions"])
        return held("halt" if cat == "halt" else "cede", snap["sessions"])
    if category(globals_) in ("retry", "wait"):
        return held("wait", globals_)

    counted = _heads(snap["queues"], snap, views)
    queued = [(c["span"], c["cls"]) for c in counted if c["cls"]] + [
        (s, c) for c2 in counted for s, c in c2.get("later", [])]
    found_halt, waits = [], []
    for cand in counted:
        sid = cand["span"]["span_id"]
        rs = list(cand["static"])
        if cand["cls"] is not None:
            rs += date_reasons(cand["span"], cand["cls"], now, snap["runs"], queued, standing)
            rs += k2_reasons(snap["runs"], sid) if cand["cls"]["k2"] else []
        rs += gap_reasons(snap["runs"], now, snap.get("census_epoch"), sid)
        gates[sid] = [r["code"] for r in rs]
        cand["reasons"] = rs
        cat = category(rs)
        if cat == "halt":
            found_halt += [r for r in rs if r["category"] == "halt"]
        elif cat is not None:
            waits += rs
    if found_halt:   # a halt anywhere outranks an armable candidate elsewhere
        return Decision("halt", found_halt, gates=gates)
    armable = next((c for c in counted if category(c["reasons"]) is None), None)
    if armable is not None:
        return Decision("arm", [], candidate=armable, gates=gates)

    fallback = fallback_select(snap, counted, gates, views)
    if fallback is not None:
        return fallback
    if not counted:
        return Decision("page", [reason("QUEUE_EMPTY")], gates=gates)
    return Decision("wait", waits, gates=gates)


def _heads(queues, snap, all_views):
    """Each queue's next span (seq order, skipping spans the ledger has or the lead withdrew), with the
    static gates that need no clock: kit evidence and class, pilot and hand gates."""
    out = []
    standing = snap["standing"]
    for view in queues:
        pending = _pending(view)
        if not pending:
            continue
        span = pending[0]
        sha = span["kit"]["sha256"]
        static = []
        entry = standing["kits"].get(sha)
        kit = view["kits"].get(sha)
        cls = None
        if entry is None:
            static.append(reason("KIT_UNKNOWN", sha[:12]))
        elif kit is None:
            static.append(reason("KIT_UNREADABLE", sha[:12]))
        else:
            try:
                cls = kit_class(kit)
            except StandingError as error:
                static.append(reason("KIT_UNCLASSIFIED", "; ".join(error.problems)))
        if cls is not None:
            if (cls["phase"] == "filler") != view["fallback"]:
                static.append(reason("KIT_ROLE_MISMATCH", f"{span['span_id']} ({cls['phase']}) in a "
                                                          f"{'fallback' if view['fallback'] else 'counted'} queue"))
            static += pilot_reasons(span, kit, view["role"], view, snap["runs"], all_views, standing)
            static += gate_reasons(span, kit["campaign_id"], snap["runs"], standing, snap.get("record_epochs"))
        later = []
        for s in pending[1:]:
            k = view["kits"].get(s["kit"]["sha256"])
            if k is not None:
                with contextlib.suppress(StandingError):
                    later.append((s, kit_class(k)))
        out.append({"queue_path": view["path"], "role": view["role"], "span": span, "kit_sha": sha, "cls": cls,
                    "static": static, "later": later, "fallback": view["fallback"]})
    return out


def fallback_select(snap, counted, gates, all_views):
    """RL-172 (g) 9: F2 (a cadence-legs span the controller arms) or F0 (paged to the magistrate's standing
    item), and only when no counted span can arm within 2 h 30 min (RL-165 section 3 line 3) and the filler
    cannot cost a counted span due today its date (line 7)."""
    now = snap["now"]
    if not snap["fallback"]:
        return None
    for cand in counted:
        rs = cand.get("reasons") or []
        etas = [r["eta"] for r in rs if r["category"] in ("wait", "retry")]
        unknown = any(e is None for e in etas)
        eta = max((e for e in etas if e is not None), default=now)
        if (not unknown and eta <= now + FALLBACK_HORIZON_S) or any(r["code"] == "AGENT_PRESENT" for r in rs):
            return None
    today = local_date(now)
    due_today = [c for c in counted if c["cls"] and c["cls"]["dated"] and c["span"]["not_before"] == today]

    def costs_day(worst):
        return bool(due_today) and now + worst + GAP_AFTER_OTHER_S > date_end(today)

    for entry in snap["fallback"]:
        if entry["kind"] == "F2":
            paths = [x["path"] for x in entry["queues"]]
            for cand in _heads([v for v in snap["fallback_queues"] if v["path"] in paths], snap, all_views):
                sid = cand["span"]["span_id"]
                rs = list(cand["static"])
                if cand["cls"] is not None:
                    rs += date_reasons(cand["span"], cand["cls"], now, snap["runs"], [], snap["standing"])
                rs += gap_reasons(snap["runs"], now, snap.get("census_epoch"), sid)
                worst = snap["plan_worst"](cand) if category(rs) is None else None
                if category(rs) is None and worst is None:
                    rs.append(reason("PLAN_REFUSED_AT_T0", sid, span=sid))
                if worst is not None and costs_day(worst):
                    rs.append(reason("FALLBACK_DAY_COST", sid, span=sid))
                gates[sid] = [r["code"] for r in rs]
                if category(rs) is None:
                    return Decision("arm-fallback", [], candidate=cand, gates=gates)
                if category(rs) == "halt":
                    return Decision("halt", [r for r in rs if r["category"] == "halt"], gates=gates)
        elif entry["kind"] == "F0":
            f0 = [r for r in snap["runs"] if r.kind == "F0"]
            rs = []
            if f0 and now < max(r.t0 for r in f0) + F0_SPACING_S:
                rs.append(reason("FALLBACK_SPACING", "4 h since the last F0", eta=max(r.t0 for r in f0) + F0_SPACING_S))
            if sum(1 for r in f0 if local_date(r.t0) == today) >= F0_MAX_PER_DATE:
                rs.append(reason("FALLBACK_SPACING", f"three F0 on {today}", eta=date_end(today)))
            if costs_day(entry["worst_case_s"]):
                rs.append(reason("FALLBACK_DAY_COST", "F0"))
            rs += gap_reasons(snap["runs"], now, snap.get("census_epoch"))
            gates["F0"] = [r["code"] for r in rs]
            if category(rs) is None:
                return Decision("page", [reason("FALLBACK_F0_DUE", f"{entry['standing_item']}")], gates=gates)
    return None
