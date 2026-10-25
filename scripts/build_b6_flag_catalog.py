#!/usr/bin/env python3
"""Reproduce block six's catalog from the untouched sealed block-five table."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.flags.catalog import catalog_from_bytes

SOURCE = ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json"
TARGET = ROOT / "configs/b6/flag_catalog_b6.json"
RECLASSIFY = {
    **{f"calibration.{suffix}": "CA-15/CA-16/CA-38/CA-40: own-capture calibration decides the bound."
       for suffix in ("acceptance_mismatch", "binding_failed", "bracket_acceptance_failed", "capture_invalid",
                      "ledger_snapshot_refused", "no_bracket", "session_not_bound")},
    "calibration.historical_custody_mismatch": "HV-6/CA-48: other captures do not decide this session's number.",
    "clock.systematic": "HV-16: majority count of labels discloses.",
    **{f"code.{suffix}": "HV-23/CA-46: unreviewed number-bearing changes decide the number."
       for suffix in ("executed_differs_from_sealed", "identity_unmeasured")},
    **{f"pack.{suffix}": "HV-23: per-run configuration identity is recorded in the export."
       for suffix in ("identity_mismatch", "identity_unmeasured")},
    "lineage.plan_tree_digest_differs": "HV-23: per-run configuration identity is recorded in the export.",
    **{f"model.{suffix}": "HV-21: direct files and stack comparisons decide the computation."
       for suffix in ("identity_unmeasured", "identity_unpinned", "identity_mismatch", "identity_inconsistent_in_window")},
    "records.malformed_flag_exclusion_possible": "HV-22: record grammar discloses.",
    "whole_window.verdict_absent": "HV-20: harvest's own member flags decide the members.",
    "whole_window.member_failures_unreadable": "HV-20: harvest's own member flags decide the members.",
    "neg8.screen_failed": "HV-18/design 13.7: survivor screen decides the registered drift screen.",
    "neg8.bound_not_derived": "HV-18/design 13.7: clean corpus and surviving counts decide the bound.",
    "roster.duplicate_run_id": "CA-13: duplicated positions have no unit.",
    "instrument.precal_screen_failed": "CA-16: alignment above reference discloses and is carried.",
    "records.malformed_flag_member_exclusion_possible": "HV-22: record grammar discloses.",
    "member.cooldown_evidence_unverified": "HV-5: measured idle admission decides.",
    "member.cooldown_cap_hit": "Registration 8.3: the 300 s cap sets wait time; the next run's idle admission decides.",
    "contention.request_overlap": "Registration 8.5: per-process 0.05 CPU-s/s discloses; exclusion needs M4's w times max(0, C - k*c_q) >= F_min/4.",
    "instrument.binary_identity_unmeasured": "X: an unmeasured identity discloses.",
}


def _entry(family: str, klass: str, effect: str, note: str) -> dict:
    return {"family": family, "klass": klass, "effect": effect, "blinding": "STRUCTURE", "note": note}


NEW_CODES = {
    "clock.step_unmeasured": _entry("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "FIX-416-G: two remaining dwell anchors determine the rate but cannot measure a step after fitting; disclose without refusing on count. Rate, skew and boot-session checks act at N=2; N<2 remains UNMEASURED. At every N>=3 the step bar is corrected for exact fit absorption from the RAW positions."),
    "bytes.reference_request_unavailable": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "BYTES section 6: the read reference bundle cannot define a whole request; print the dropped reference and reason in NEG-8 inputs."),
    'bytes.meter_decode_unavailable': _entry('RECORDS', 'REPRESENTATION', 'DISCLOSE', 'BYTES section 6: the decode meter value is unavailable; disclose the affected DC-input and rest cells.'),
    'bytes.meter_gap': _entry('RECORDS', 'REPRESENTATION', 'DISCLOSE', 'FIX-416 disposition: a dropped device sample in a decode or reference span leaves that run without a DC-input value; rails selection is unchanged.'),
    'catalog.digest_mismatch': _entry('RECORDS', 'REPRESENTATION', 'DISCLOSE', 'FIX-416: the running flag catalog digest differs from the pack registration; record both digests.'),
    "records.claim_usable_counting_disagreement": _entry("RECORDS", "REPRESENTATION", "DISCLOSE",
        "Audit F11: harvest usability and block-six acceptance counting disagree; acceptance counting governs; disclose only."),
    "bytes.decode_battery_assist": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "BAT-2 sections 3-4: a negative battery current received in [decode_start + tau, decode_end + tau) marks decode assistance; only the labelled description omits its whole unit; the harvest's battery.assist is counted only."),
    "bytes.withheld_missing": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "B6 Q1: an expected withheld export file is missing; disclose the pass and sidecar row counts, retain any surviving pass under Addendum 7 D9."),
    "bytes.module_changed_after_commitment": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "B6 Q2: the analysis module evaluating the held-out stage differs from the module that wrote the stage-1 commitment; the second commitment prints beside the registered result as the post-agreement fix."),
    "bytes.commitment_not_rebuilt": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "B6 Q2: under a module changed after the stage-1 commitment, the committed content does not rebuild; the committed content is evaluated as committed and the differing fields are listed."),
    "records.window_plan_unreadable": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "Registration 8.4: missing records never refuse a capture; its level screen is diagnostic."),
    "records.resume_finalize_failed": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "Desk refit failed twice; the named slot is retained in the aborted bracket and collection continues."),
    "agents.hid_recent": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "HID inactivity has no energy derivation; idle admission measures the hazard."),
    "clock.rate_above_budget": _entry("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Registration 8.6: above the old h-inclusive budget, below the 5 ms / T_stream_max - 0.25 ppm hold."),
    "clock.rate_hold": _entry("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Lead ruling 2026-10-16: the registered rate hold wakes the orchestrator without a redraw attempt or timed retry."),
    "power.pstar_unsized": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "No registered T_phase for this pack/phase: no P* exclusion. Once sized, P* = F_min/(4*T_phase); never use a science duration or another pack's size."),
    "instrument.single_interval_above_screen": _entry("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "A single interval above twice the 100 ms sampling period discloses; median <= 150 ms remains the refusal."),
    "meter.unexplained_idle_step": _entry("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Registration 8.5 D24: print the meter cross-check; power outside the measured rails excludes nothing."),
    **{f"calibration.{suffix}": _entry("CALIBRATION", "NUMBER" if suffix in {
           "alignment_above_reference", "drift_above_budget", "capture_outside_acceptance_range",
           "other_session_systematic", "other_session_range_expansion", "corpus_doubling_reached",
       } else "REPRESENTATION", "DISCLOSE", note)
       for suffix, note in {
           "alignment_above_reference": "T1/CA-16: capture is carried into the operative bound.",
           "drift_above_budget": "T2: measured drift is carried into the operative bound.",
           "capture_outside_acceptance_range": "CA-40: own-capture range expansion is carried.",
           "estimator_code_changed": "CA-40: recorded protocol/estimator digests differ.",
           "other_session_systematic": "CA-40/Erratum 3: another session cannot remove this session.",
           "other_session_range_expansion": "CA-40/Erratum 3: another session's range expansion discloses.",
           "corpus_doubling_reached": "CA-40/Erratum 3: valid capture count reaches twice the corpus.",
           "stop_line_unregistered": "T1: null stop line has no refusal.",
           "stop_line_unsized": "Lead ruling 2026-10-16: no registered per-pack T10 stop; carry the bound and let the run's own phase checks decide.",
           "acceptance_preflight_unverified": "CA-15/S-068: preflight record shape discloses in HAZARD mode.",
           "capture_list_write_failed": "CA-38: list write failure discloses; capture stays.",
           "capture_list_line_unreadable": "CA-38: malformed list line is skipped and disclosed.",
       }.items()},
    "calibration.operative_bound_above_stop": _entry("CALIBRATION", "PHYSICS", "EXCLUDE_WINDOW", "T1: measured operative timing bound is above the registered physical stop line."),
    "calibration.bracket_incomplete": _entry("CALIBRATION", "NUMBER", "EXCLUDE_WINDOW", "No two refitted captures: operative timing bound is undefined."),
    "neg8.survivor_screen_failed": _entry("NEG8", "NUMBER", "EXCLUDE_WINDOW", "Registered endpoint drift screen fails on the surviving references."),
    "neg8.survivor_screen_undefined": _entry("NEG8", "NUMBER", "EXCLUDE_WINDOW", "No defined corpus bound or insufficient endpoints: drift allowance is undefined."),
    "neg8.survivor_screen_passed": _entry("NEG8", "NUMBER", "DISCLOSE", "Survivor screen passed; counts only outside withheld."),
    **{f"neg8.{role}_energy_unreadable": _entry("NEG8", "REPRESENTATION", "DISCLOSE", "Design 13.7: unreadable energy drops this member; screen uses survivors.")
       for role in ("reference", "corpus")},
    "model.files_differ_from_registered": _entry("MODEL_IDENTITY", "PHYSICS", "EXCLUDE_WINDOW", "Design 13.9: measured model bytes are another experiment."),
    "model.stack_differs_from_registered": _entry("MODEL_IDENTITY", "NUMBER", "EXCLUDE_WINDOW", "HV-21: runtime, kernel packages, tokenizer or quantization changes the executed computation."),
    "model.identity_unrecorded": _entry("MODEL_IDENTITY", "REPRESENTATION", "DISCLOSE", "HV-21: precheck directly measures the files; a missing run identity discloses."),
    "model.source_unpinned": _entry("MODEL_IDENTITY", "REPRESENTATION", "DISCLOSE", "HV-21: an observed source without a pin discloses; no measured byte difference."),
    "code.changed_since_registration": _entry("CODE_IDENTITY", "REPRESENTATION", "DISCLOSE", "HV-23/CA-46: changed committed and tracked-edit paths are recorded."),
    "code.executed_head_unrecorded": _entry("CODE_IDENTITY", "REPRESENTATION", "DISCLOSE", "HV-23: unrecorded executing commit discloses."),
    "code.tracked_edits_unrecorded": _entry("CODE_IDENTITY", "REPRESENTATION", "DISCLOSE", "HV-23/CA-46: absent executed porcelain discloses."),
    "code.number_bearing_unreviewed": _entry("CODE_IDENTITY", "NUMBER", "EXCLUDE_WINDOW", "HV-23/CA-46: unreviewed acquisition or reduction changes can move a printed number."),
    "registration.default_used": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "Missing optional registration keys use the specified defaults."),
    "catalog.code_unclassified": _entry("RECORDS", "REPRESENTATION", "DISCLOSE", "HV-8: code missing from block-six catalog is recorded for classification."),
    "plan.spare_retry_present": _entry("ROSTER", "REPRESENTATION", "DISCLOSE", "Design 13.7: block-six plan should omit reference spares."),
    **{f"structure.{suffix}": _entry("RECORDS", "NUMBER", "EXCLUDE_WINDOW", "Design 13.1: " + note)
       for suffix, note in {"chain_crashed": "collection terminated structurally.",
                            "missing_stage_bundles": "an expected stage has no bundles although later stages ran.",
                            "no_capture_records": "a whole record class is missing.",
                            "no_roster": "no planned members were recorded."}.items()},
    "agent.unit_overlap": _entry("PHYSICS_IN_SPAN", "PHYSICS", "EXCLUDE_MEMBER", "CA-7/design 13.6: agent work overlaps this unit; collection-lane placeholder."),
    "sleep.in_run": _entry("PHYSICS_IN_SPAN", "PHYSICS", "EXCLUDE_MEMBER", "S1: sleep breaks the run's record sequence; collection-lane placeholder."),
    "idle.wait_cap_skip": _entry("MEMBER_VALIDITY", "PHYSICS", "EXCLUDE_MEMBER", "Q2: measured idle admission never passed within the cap; collection-lane placeholder."),
    "member.duration_outlier": _entry("DIAGNOSTIC", "REPRESENTATION", "DISCLOSE", "Design 13: duration is a per-run flag; collection-lane placeholder."),
    "clock.time_server_offset": _entry("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "C1: query-only diagnostic; collection-lane placeholder."),
}
# Stage-1 integration (2026-10-14): the codes the block-6 driver lane actually
# writes (joulewise/b6/{agent_pause,idle_wait,sleep_guard}.py, the controller
# and the driver), with the family, class and effect of its proposal in
# joulewise.flags.catalog.DRAFT_CODES. The effects follow the design texts:
# agent overlap excludes the overlapping unit (design 13 item 6), a sleep inside
# a run excludes that run (design 3.4, council S1), a run skipped at the idle
# wait cap or the session wait budget is a skip with a flag (design 6.2), and
# everything else discloses (idle.waited until test M2 says otherwise). A pack
# registration may still set other effects through its flag_effects.
COLLECTION_CODES = {
    code: _entry(family, klass, effect, note) for code, (family, klass, effect, note) in {
        "agent.presence": ("PHYSICS_IN_SPAN", "PHYSICS", "EXCLUDE_MEMBER",
                           "Design 13.6: an agent was present; the presence interval excludes overlapping members."),
        "agent.presence_overlap": ("PHYSICS_IN_SPAN", "PHYSICS", "EXCLUDE_MEMBER",
                                   "Design 13.6: agent presence overlaps this member; its whole unit is excluded."),
        "agent.capture_overlap": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE",
                                  "Agent presence overlapped a calibration capture; disclosed."),
        "agent.pause_marker_stale": ("RECORDS", "REPRESENTATION", "DISCLOSE",
                                     "A pause marker from an earlier process was found; disclosed."),
        "sleep.in_run": ("PHYSICS_IN_SPAN", "PHYSICS", "EXCLUDE_MEMBER",
                         "Council S1: the sleep-counting minus sleep-blind offset grew by more than 1 ms inside the run."),
        "sleep.between_runs": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Council S1: sleep between runs; disclosed."),
        "sleep.in_chain": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Council S1: sleep outside any run; disclosed."),
        "sleep.reading_unmeasured": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Council S1: a per-run sleep reading failed; disclosed."),
        "sleep.assertion_lost": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Design 6.3: the driver's no-sleep hold exited and was restarted."),
        "sleep.assertion_unverified": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Design 6.3: the driver's no-sleep hold could not be verified."),
        "idle.waited": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Design 6.2: the idle baseline slid before admission; test M2 decides any other effect."),
        "idle.wait_cap_skip": ("MEMBER_VALIDITY", "PHYSICS", "EXCLUDE_MEMBER",
                               "Design 6.2: no quiet idle span within the 1,500 s cap; the run was skipped."),
        "idle.wait_budget_skip": ("MEMBER_VALIDITY", "PHYSICS", "EXCLUDE_MEMBER",
                                  "Design 6.2: the session wait budget was spent; the run was skipped."),
        "idle.wait_budget_exhausted": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "Design 6.2: the session wait budget was spent."),
        "idle.wait_budget_unreadable": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE", "The session wait ledger could not be read; disclosed."),
        "idle.wait_ledger_unwritable": ("RECORDS", "REPRESENTATION", "DISCLOSE", "The session wait ledger could not be written; disclosed."),
        "idle.busy_fraction_exceeded": ("DIAGNOSTIC", "PHYSICS", "DISCLOSE",
                                        "Driver H1: the busy fraction alone is disclosed; power and GPU still decide admission."),
    }.items()
}
NEW_CODES.update(COLLECTION_CODES)
# The unattended loop's own session-record codes (loop lane F5 and F6, deferred
# to the merge). Records about records: they disclose and never remove data.
LOOP_CODES = {
    "precheck.certain_exclusion": _entry(
        "RECORDS", "NUMBER", "EXCLUDE_WINDOW",
        "Design 3.3: the registered acceptance excludes the nominal synthetic session; hold before collecting."),
    "precheck.acceptance_unavailable": _entry(
        "RECORDS", "REPRESENTATION", "DISCLOSE",
        "Stage-2 issue 2: missing or malformed acceptance values flag collection; counting remains pending."),
    "registration.after_first_session": _entry(
        "RECORDS", "REPRESENTATION", "DISCLOSE",
        "Design 16 item 2: the pack registration's commit is later than this session's start."),
    "notice.undelivered": _entry(
        "RECORDS", "REPRESENTATION", "DISCLOSE",
        "Design 6.4 / pruning 7a decision 7: the arm notice was not delivered; the session still armed."),
    "notice.no_unreadable": _entry(
        "RECORDS", "REPRESENTATION", "DISCLOSE",
        "Loop F6: the owner's NO reply or the remote STOP could not be read at arm; the session still armed."),
}
NEW_CODES.update(LOOP_CODES)


def build() -> bytes:
    document = json.loads(SOURCE.read_bytes())
    for code, note in RECLASSIFY.items():
        document["codes"][code].update(effect="DISCLOSE", note=note)
    document["codes"].update(NEW_CODES)
    document["rules"]["cell_unit_minimum"] = 5
    raw = (json.dumps(document, sort_keys=True, indent=2) + "\n").encode()
    catalog_from_bytes(raw)
    return raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    raw = build()
    if args.write:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(raw)
        return 0
    if not TARGET.is_file() or TARGET.read_bytes() != raw:
        print("block-six flag catalog needs regeneration", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
