"""D-180 clause 2 and D-182 desk policy; no I/O or measurement authority.

Python 3.9 and stdlib only. The foreground caller supplies the live driver's
resolved schedule and the gate's age limit; this module must not import either
runtime (the driver requires Python 3.11). See ``retry_allowed`` for inputs.
"""

import hashlib
import json
import math
import re
from dataclasses import dataclass
from typing import Mapping


RETRY_INTERVAL_S = 60
# NIGHT_HANDBACK / runbook 1.4: accepted notice before publication, no minimum
# interval beyond ordering. R1 repeats that lead on EVERY attempt.
NOTICE_LEAD_S = 0
UNCERTAIN_STATES = ("CLOCK_UNCERTAIN", "NETWORK_UNCERTAIN")
ZERO_CAPTURE_MACHINE_REFUSALS = frozenset({
    "night_refused_not_quiet", "night_refused_bind_expired",
    "night_refused_agent_present", "night_refused_hid_idle",
    "night_refused_boot_clock",
})
RETRY_CAUSES = {
    "arm_idle_interactive": "Only an otherwise idle interactive agent session blocked the arm-time census. Its complete descendant process tree must establish no test, measurement or capture work; unknown activity is not idle. Repeat the unchanged census after the session closes; never signal a foreign process. A173 alone owns any future stub exemption.",
    "arm_notice_mismatch": "The notice fingerprint or reviewed head differs from the approved candidate. Recheck preserved candidate bytes and all fixed inputs, then send a new notice. Changed science, custody or unexplained candidate bytes are evidence drift, not a notice-only fault.",
    "arm_watchdog_uncertain": f"A watchdog tick (one supervisor evaluation) returned {UNCERTAIN_STATES[0]} (wall and elapsed clocks disagree) or {UNCERTAIN_STATES[1]} (the remote stop check is inconclusive). Let the watchdog clear its hold: two sane clock samples, or a successful network positive control with the stop reference absent. Never clear its state by hand.",
    "arm_transport": "A named mail/API/network/process-transport operation failed before publication, or installation transport failed with positive noncommit and completed cleanup evidence. A bare nonzero exit or lost response is insufficient. Restore transport and obtain accepted notice delivery; after publication require uninstall exit 0, preserved matching bytes and completed unpublication. Committed, retained, unknown or failed-restoration outcomes stop.",
}

# Explicit assignments are intentional: registry additions must force review.
COLD_GATE_CODES = {
    "night_refused_agent_present": "Production census refusal, including a receipt at t0; never an idle arm event. Zero-capture successor route per D-182.",
    "night_refused_not_quiet": "One-shot load refusal for v2, a terminal power/thermal predicate failure, or one named non-observer process at or above 0.5 busy cores over a single 30 s observation at t0 or at the arm check (registration v3; cold gate QPE01-DAEMON-CONTAMINATION-01 ruling 10 Q2, 2026-09-23). Also: more than two launchd spawns of corecaptured (the Wi-Fi log-capture helper) in the last 10 min at t0, detection only, or new spawns persisting 180 s after the arm check's one licensed Wi-Fi cycle (cold ruling 16 Q2, 2026-09-23). The detail names the process, its pid and its share, and the receipt's C3 row carries top_consumers_at_decision. For v4, load is diagnostic and the CPU cutoff is a sealed plan parameter with a named ruling. Zero-capture successor route per D-182.",
    "night_refused_bind_expired": "Bind window expired with every sample recorded. Load is diagnostic; the CPU cutoff is a sealed plan parameter. Zero-capture successor route per D-182.",
    "night_refused_hid_idle": "Screensaver-configuration guard failed; this is not a live inactivity measurement. Zero-capture successor route per D-182.",
    "night_refused_boot_clock": "Measurement boot/clock guard failed; not a watchdog uncertainty tick. Zero-capture successor route per D-182.",
    "night_refused_registration": "The registration digest is not in the ruled table, or its bound chain-source digest differs from the measured source.",
    "night_window_expired": "Measurement window expired.",
    "night_plan_stale": "Plan age, pinned head, or a clean measurement clone failed; not a stale notice.",
    "measurement_root_outside_custody": "A plan authored at/after 1790340000 whose resolved measurement_root is not strictly inside /Users/edr/night-custody/measurement (acceptance ruling v2.1 R16). Re-author the plan; never a retry cause.",
    "night_plan_malformed": "Plan structure or fields failed their contract.",
    "night_chain_digest_mismatch": "Executable chain bytes differ from their fixed fingerprint.",
    "launch_go_receipt_missing": "Required measurement-pack launch authorization is absent.",
    "launch_go_receipt_invalid": "Required measurement-pack launch authorization is invalid.",
    "night_refused_class_unbuilt": "This gate cannot execute the requested plan class.",
    "night_receipt_class_invalid": "Receipt class/condition contract is invalid.",
    "night_probe_error": "An observation failed; missing evidence grants no permission.",
    "night_aborted_agent_present": "An agent appeared while the chain ran.",
    "night_chain_already_started": "The once-only chain-start record exists.",
    "night_chain_alive": "The existing chain has not been proved ended.",
    "night_chain_launch_failed": "Launch failed after the once-only start claim; not pre-arm transport.",
    "night_courier_running": "The result-delivery process is still running.",
    "night_courier_unavailable": "The driver's delivery executable is unavailable; not a failed notice send.",
    "night_plan_overruns_deadman": "Completion/dead-man schedule was refused; retained even if normally unreachable.",
    "night_record_exists": "A write-once night record proves invocation already occurred.",
    "night_calibration_refused": "The chain's calibration ledger refused (custody timeout, strict pre-reserve, or invalid custody); the document names the exact code; never an auto-retry cause.",
    "night_window_exceeded": "The chain ran past the exclusive window end and was terminated by the driver; reservation or capture intent may have been written and the session may need desk recovery; never an auto-retry cause.",
    "non_observer_process_busy": "Two CONSECUTIVE envelopes were excluded because one non-observer process held at least 30 busy-core-seconds inside each (registration v3's per-envelope integral; cold gate QPE01-DAEMON-CONTAMINATION-01 ruling 10 Q2, 2026-09-23). The chain ends about 31 minutes after t0 with a typed refusal naming the process, its pid and its core-seconds. This is a machine-state abort AFTER capture, so D-182's zero-capture route does not apply by itself; Ed's 2026-09-23 addendum to D-182 licenses ONE new-plan successor when fewer than minimum_retained envelopes were captured (installed by lane QPE01-ABORT-SUCCESSOR-01; until that lane lands the chain ends with no successor); the captured envelopes stay in the archive. One such envelope followed by a clean one never aborts; never an auto-retry cause.",
}
INSTALLER_REFUSALS = {
    "install_span_closed": "The selected transaction ended; never switch spans mid-install or bypass the plan cutoff.",
    "install_outside_span": "Wait for an allowed span before the cutoff; scheduling wait is not a fifth retry cause.",
    "plan_t0_in_the_past": "Author a future plan through ordinary planning.",
    "night_agent_already_loaded": "A loaded or UNKNOWN job blocks admission; follow harvest/uninstall and human resolution.",
    "plan_outside_custody_root": "Wrong published location; the existing installation rule still applies.",
    "night_plan_malformed": "Invalid plan fields; not a notice-only fault.",
    "plan_schedule_unrepresentable": "The schedule cannot be represented; no new duration ceiling is implied.",
    "install_spans_unresolvable_on_day": "Local-date spans fail resolution; never repair or drop them silently.",
    "plan_t0_not_minute_aligned": "t0 must name a whole minute.",
    "plan_t0_ambiguous_local_time": "t0's local minute occurs twice; choose an unambiguous minute.",
    "retained prior plist: <path>; re-run --uninstall": "A saved previous job file remains; follow the existing human-resolution/uninstall path.",
    "unsupported plist destination: <path>": "The job-file destination is not a regular file; resolve it under the existing path.",
    "--render-only directory must differ from launch_dir": "Use a separate directory for rendered job files.",
}
OTHER_REFUSALS = {
    "HOLD_CENSUS": "A supervisor census hold alone does not establish the narrowly evidenced idle arm cause.",
    "slot_refused": "A measurement slot refused; cure the finding before any further night.",
}
DISPOSITIONS = {
    **dict.fromkeys(RETRY_CAUSES, "retry"),
    **dict.fromkeys(COLD_GATE_CODES, "cold_gate"),
    **dict.fromkeys(INSTALLER_REFUSALS, "cold_gate"),
    **dict.fromkeys(OTHER_REFUSALS, "cold_gate"),
}


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


def classify_abort(cause):
    """Classify exact arm-event IDs; unknown, mixed and malformed causes stop."""
    return DISPOSITIONS.get(cause, "cold_gate") if isinstance(cause, str) else "cold_gate"


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("expected a finite epoch/duration")
    return value


def retry_allowed(now_epoch_s, plan, attempts, notice) -> Decision:
    """Check supplied evidence, without observing or mutating the machine.

    plan: mapping with ``plan_bytes`` (reread candidate), ``saved_plan_bytes``
    (pre-notice snapshot), ``reviewed_head``, ``install_close_epoch_s`` from
    run_night.install_close_epoch, and ``plan_max_age_s`` from night_gate.

    attempts: chronological prior abort mappings: attempt (1-based),
    attempt_epoch_s, abort_epoch_s, cause, receipt_class, plan_sha256,
    message_id (empty if no send), outcome (not_published/restored_unpublished).
    The latter outcome certifies noncommit, uninstall 0, byte comparison and
    unpublication. A lost install response cannot establish that outcome.

    notice: accepted, message_id, thread_id, sent_epoch_s, attempt, plan_id,
    receipt_class, measurement_head, plan_sha256; plus freshly observed
    prerequisites_clear and veto_clear (literal bools), latest_no_epoch_s
    (None only if no observed standing NO), latest_abort_epoch_s (None for initial),
    and blocking_causes (all known concurrent refusal codes, empty to proceed).
    prerequisites_clear covers census, watchdog, science, custody, no invocation
    and the authorized observable stop/directive channels. veto_clear covers
    directive issues, standdown.request/STOP, and any NO relayed into a readable
    channel. An unreadable notice thread is recorded as a limitation in the
    attempt directory, not a stop. Every observed NO is preserved and stops.
    Caller retains the underlying observations; neither boolean requires
    reading an inaccessible notice thread.

    Empty history validates an initial arm without a retry delay. R2 successor
    activations use ordinary fresh-plan arming, not adoption of old bytes.
    Missing/malformed inputs fail closed. Denial is routing, not a new remedy.
    """
    try:
        now = _number(now_epoch_s)
        raw = plan["plan_bytes"]
        if not isinstance(raw, bytes) or raw != plan["saved_plan_bytes"]:
            return Decision(False, "candidate_changed")
        candidate = json.loads(raw)
        digest = hashlib.sha256(raw).hexdigest()
        head = plan["reviewed_head"]
        if not isinstance(head, str) or re.fullmatch(r"[0-9a-f]{40}", head) is None:
            return Decision(False, "invalid_head")
        if candidate["repo_head"] != head or candidate["measurement_head"] != head:
            return Decision(False, "candidate_head_mismatch")
        if not isinstance(attempts, (list, tuple)) or not isinstance(notice, Mapping):
            return Decision(False, "malformed_evidence")
        blockers = notice["blocking_causes"]
        if not isinstance(blockers, (list, tuple)) or blockers:
            return Decision(False, "cold_gate_evidence")
        if notice["latest_no_epoch_s"] is not None:
            _number(notice["latest_no_epoch_s"])
            return Decision(False, "owner_no")
        if notice["veto_clear"] is not True or notice["prerequisites_clear"] is not True:
            return Decision(False, "prerequisites_not_clear")
        if (type(notice["attempt"]) is not int or notice["attempt"] != len(attempts) + 1
                or notice["accepted"] is not True
                or any(not isinstance(notice[key], str) or not notice[key].strip()
                       for key in ("message_id", "thread_id"))):
            return Decision(False, "notice_not_current")
        previous_abort = None
        for ordinal, prior in enumerate(attempts, 1):
            started = _number(prior["attempt_epoch_s"])
            aborted = _number(prior["abort_epoch_s"])
            if (type(prior["attempt"]) is not int or prior["attempt"] != ordinal
                    or started > aborted or aborted > now
                    or (previous_abort is not None and started < previous_abort)):
                return Decision(False, "invalid_history")
            if (classify_abort(prior["cause"]) != "retry"
                    or prior["outcome"] not in ("not_published", "restored_unpublished")):
                return Decision(False, "cold_gate_history")
            if (prior["receipt_class"] != candidate["receipt_class"]
                    or prior["plan_sha256"] != digest):
                return Decision(False, "candidate_changed")
            if prior["message_id"] == notice["message_id"]:
                return Decision(False, "notice_reused")
            previous_abort = aborted
        if notice["latest_abort_epoch_s"] != previous_abort:
            return Decision(False, "notice_abort_mismatch")
        if attempts and now - attempts[-1]["attempt_epoch_s"] < RETRY_INTERVAL_S:
            return Decision(False, "retry_spacing")
        authored = _number(candidate["authored_epoch_s"])
        t0 = _number(candidate["t0_epoch_s"])
        max_age = _number(plan["plan_max_age_s"])
        if max_age <= 0 or not 0 <= now - authored <= max_age or not 0 <= t0 - authored <= max_age:
            return Decision(False, "plan_age")
        if now >= _number(plan["install_close_epoch_s"]):
            return Decision(False, "install_closed")
        if (notice["plan_sha256"] != digest or notice["measurement_head"] != head
                or any(notice[key] != candidate[key] for key in ("plan_id", "receipt_class"))):
            return Decision(False, "notice_binding_mismatch")
        sent = _number(notice["sent_epoch_s"])
        if sent + NOTICE_LEAD_S > now or (previous_abort is not None and sent < previous_abort):
            return Decision(False, "notice_timing")
        return Decision(True, "allowed")
    except (KeyError, TypeError, ValueError, OverflowError):
        return Decision(False, "malformed_evidence")


def terminal_zero_capture_refusal(result, receipt) -> Decision:
    """Read the shared terminal result and receipt fence before delivery checks.

    Live gate receipts do not yet have the harvested C5 zero_capture_evidence
    block. A bare C5 row is neither evidence nor a veto; the watchdog must
    establish absence from custody. A positive capture claim in any measured
    row still vetoes release.
    """
    try:
        reason = result["aborted_reason"]
        if (result["verdict"] != "REFUSED" or receipt["verdict"] != "REFUSED"
                or reason not in ZERO_CAPTURE_MACHINE_REFUSALS
                or receipt["refusal"]["reason"] != reason):
            return Decision(False, "not_zero_capture_machine_refusal")
        plan_id = result["plan_id"]
        if not isinstance(plan_id, str) or not plan_id or receipt["plan_id"] != plan_id:
            return Decision(False, "handoff_plan_mismatch")
        if result["chain_exit_code"] is not None or result["chain_sha256"] is not None:
            return Decision(False, "chain_may_have_started")
        rows = receipt["conditions"]
        if not isinstance(rows, list):
            return Decision(False, "missing_zero_capture_evidence")
        for row in rows:
            measured = row["measured"]
            if not isinstance(measured, dict):
                return Decision(False, "missing_zero_capture_evidence")
            for evidence in (measured, measured.get("zero_capture_evidence", {})):
                if not isinstance(evidence, dict):
                    return Decision(False, "missing_zero_capture_evidence")
                if (("chain_started_absent" in evidence
                     and evidence["chain_started_absent"] is not True)
                        or ("reservation_absent" in evidence
                            and evidence["reservation_absent"] is not True)
                        or evidence.get("session_id") is not None
                        or ("capture_writer_ran" in evidence
                            and evidence["capture_writer_ran"] is not False)
                        or ("instrument_validation_empty" in evidence
                            and evidence["instrument_validation_empty"] is not True)
                        or evidence.get("captured_envelopes", 0) != 0):
                    return Decision(False, "start_reservation_or_capture_not_absent")
        return Decision(True, "terminal_zero_capture_refusal")
    except (KeyError, TypeError, ValueError):
        return Decision(False, "missing_zero_capture_evidence")


def successor_license(result, receipt, facts, delivery, claims, now_epoch_s) -> Decision:
    """Pure D-182 door 1 plus the shared one-use, delivery and spacing tail.

    Door 2 for a captured ``non_observer_process_busy`` abort belongs to A270.
    ``claims`` binds the candidate identity and the durable prior claim.
    """
    terminal = terminal_zero_capture_refusal(result, receipt)
    if not terminal.allowed:
        return terminal
    if facts is None or not getattr(facts, "clean", False):
        return Decision(False, "start_reservation_or_capture_not_absent")
    try:
        # Release keeps the receipt's veto-only role (cold ruling, A234 round
        # 2). The successor route additionally needs the receipt shape the
        # driver writes (run_night.py ~1869, C1-C5): exactly one C5 row, the
        # no-retry-bound row D-182 names. An empty conditions list is
        # malformed and licenses no successor.
        if sum(1 for row in receipt["conditions"] if row["condition_id"] == "C5") != 1:
            return Decision(False, "malformed_successor_evidence")
        if (facts.chain_started or facts.reservation_markers_found
                or facts.capture_entries_found or facts.envelopes_captured):
            return Decision(False, "start_reservation_or_capture_not_absent")
        plan_id = result["plan_id"]
        if delivery["plan_id"] != plan_id:
            return Decision(False, "handoff_plan_mismatch")
        if (delivery["courier.sent"] is not True
                or not isinstance(delivery["message_id"], str)
                or not delivery["message_id"]):
            return Decision(False, "delivery_incomplete")
        candidate_id = claims["candidate_plan_id"]
        candidate_sha = claims["candidate_sha256"]
        predecessor_sha = claims["predecessor_sha256"]
        if (not isinstance(candidate_id, str) or not candidate_id
                or not isinstance(candidate_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", candidate_sha)
                or not isinstance(predecessor_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", predecessor_sha)):
            return Decision(False, "malformed_successor_evidence")
        if candidate_id == plan_id or candidate_sha == predecessor_sha:
            return Decision(False, "predecessor_rearm")
        if claims["predecessor_is_successor"] is True:
            return Decision(False, "successor_already_used")
        existing = claims["existing_claim"]
        if existing is not None and (existing.get("successor_plan_id") != candidate_id
                                     or existing.get("successor_sha256") != candidate_sha):
            return Decision(False, "successor_already_used")
        if _number(now_epoch_s) - _number(result["ended_epoch_s"]) < RETRY_INTERVAL_S:
            return Decision(False, "successor_spacing")
        return Decision(True, "new_plan_only")
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        return Decision(False, "malformed_successor_evidence")


def zero_capture_successor_allowed(result, receipt, delivery, facts=None, claims=None,
                                   now_epoch_s=None) -> Decision:
    """Compatibility entry point; missing disk facts never grant a licence."""
    return successor_license(result, receipt, facts, delivery, claims,
                             now_epoch_s)


def successor_arm_allowed(now_epoch_s, plan, notice, result, receipt, delivery,
                          facts=None, claims=None) -> Decision:
    """Desk adapter for retry-format plan/notice evidence; no production caller."""
    eligible = successor_license(result, receipt, facts, delivery, claims, now_epoch_s)
    if not eligible.allowed:
        return eligible
    try:
        terminal = _number(result["ended_epoch_s"])
        if (_number(notice["sent_epoch_s"]) < terminal
                or notice["message_id"] == delivery["message_id"]):
            return Decision(False, "notice_not_fresh")
        return retry_allowed(now_epoch_s, plan, [], notice)
    except (KeyError, TypeError, ValueError, OverflowError):
        return Decision(False, "malformed_successor_evidence")


def render_policy() -> str:
    """Return the entire marked Markdown block, including its final newline."""
    lines = ["<!-- BEGIN ARM-RETRY-POLICY v1 -->", "",
             "D-180 clause 2; A172 rulings R1–R3 and fix-round-1 R1–R4 (2026-09-15). "
             "Exact arm-event IDs are labels for recorded observations, not receipt codes.", "",
             "| Retry cause | Meaning and required clearance |", "|---|---|"]
    lines.extend("| `{}` | {} |".format(k, v) for k, v in RETRY_CAUSES.items())
    for title, rows in (("Gate and driver refusals", COLD_GATE_CODES),
                        ("Installer §1.3 refusals", INSTALLER_REFUSALS),
                        ("Other explicit refusals", OTHER_REFUSALS)):
        lines.extend(["", "**{} — cold-gate path.**".format(title), "",
                      "| Exact cause | Why A172 grants no retry exception |", "|---|---|"])
        lines.extend("| `{}` | {} |".format(k, v) for k, v in rows.items())
    lines.extend(["",
        "Unknown or mixed causes and every capture, clock, custody, ledger or pre-registration guard stay on the cold-gate path; receipt refusals remain ineligible for same-plan retries. Known concurrent refusal evidence overrides an eligible arm cause. These dispositions preserve existing harvest, delivery and human-resolution remedies; they do not call a review into a live chain.", "",
        "R1's operative time bounds are `now < install_close_epoch(plan)` and plan age within `PLAN_MAX_AGE_S` (including the existing authored-to-t0 check), with at least {} seconds between arm attempts. D-180's same-or-next-listed-span ceiling is subsumed by `install_close_epoch(plan)` and `PLAN_MAX_AGE_S`, because with whole-day install spans it could otherwise bind 15 minutes before install close. There is no attempt-count cap, separate notice-age limit, new window cadence or delay after a successful harvest.".format(RETRY_INTERVAL_S), "",
        "D-182: binding observations inside the window are not retries. A zero-capture machine-state refusal may license ONE new-plan successor after courier delivery. A successor is a fresh plan with its own id and SHA-256 digest. The evidence-night successor check reads the predecessor (the refused plan), the shared disk facts (chain start, reservation markers, capture entries and envelope index), and the courier.sent delivery marker with message id. run_night.py creates chain.started before starting the chain (lines 536 and 3170); a calibration ledger session is appended only inside that chain, so absent chain.started also proves no ledger session. A bare C5 receipt row supplies none of these disk facts. The successor route also requires the driver's receipt shape with exactly one C5 row; early release keeps the receipt's veto-only role. The check requires the watchdog's early-release latch, at least 60 s since result.ended_epoch_s, and an unspent successor claim; a claim is the create-once file under night-custody/successor-claims that binds the predecessor to the successor id and digest. Real publish-install creates that claim immediately before publication; a rehearsal does not. The real launchctl must be spelled launchctl; any other spelling that resolves to it is refused, never treated as a rehearsal. A predecessor whose plan id cannot name a claim file fails the successor check. The claim binds only until the predecessor's completion time. Re-preparing with changed bytes after failed publication gives up the successor for the rest of that span. Removing released predecessor custody during its span is an operator action that forfeits the successor bound. The candidate still needs a fresh accepted notice, its own future install close, and no observed NO on any notice thread. Never re-arm the predecessor or treat this as a same-candidate retry. Direct install_night_agent.sh performs no successor check; a follow-up lane owns that route.", "",
        "Every actual attempt sends a newly accepted notice and repeats the existing notice-to-publication lead: accepted email before publication, with no additional minimum interval. A notice is stale if its SHA-256 fingerprint (digest of the exact plan bytes) or reviewed head differs, a newer abort or NO exists, or it belongs to an earlier attempt. A new thread never clears an earlier NO. Waiting observations send no repeated email. Preserve each attempt in `$STAGE/arm-attempts/NNNNNN/` (a positive ordinal padded to at least six digits, without a count limit), created exclusively; never overwrite prior notice, candidate or failure evidence.", "",
        "`prerequisites_clear` covers census, watchdog, science, custody, no invocation and authorized observable stop/directive checks; `veto_clear` covers directive issues (`gh issue list --label directive`), `standdown.request`/STOP and any NO relayed into a readable channel. Record an unreadable notice thread as a limitation in the attempt directory; it is not a stop and neither clearance boolean requires reading it. Preserve every observed NO; each stops publication.", "",
        "<!-- END ARM-RETRY-POLICY v1 -->", ""])
    return "\n".join(lines)
