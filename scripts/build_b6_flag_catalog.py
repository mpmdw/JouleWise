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
    "calibration.capture_battery_unmeasured": "Doctrine 2: the measured capture battery span remains excluding.",
    "clock.systematic": "HV-16: majority count of labels discloses.",
    **{f"code.{suffix}": "HV-23/CA-46: unreviewed number-bearing changes decide the number."
       for suffix in ("executed_differs_from_sealed", "identity_unmeasured")},
    **{f"pack.{suffix}": "HV-23: per-run configuration identity is recorded in the export."
       for suffix in ("identity_mismatch", "identity_unmeasured")},
    "lineage.plan_tree_digest_differs": "HV-23: per-run configuration identity is recorded in the export.",
    **{f"model.{suffix}": "HV-21: direct files and stack comparisons decide the computation."
       for suffix in ("identity_unmeasured", "identity_unpinned")},
    "records.malformed_flag_exclusion_possible": "HV-22: record grammar discloses.",
    "whole_window.verdict_absent": "HV-20: harvest's own member flags decide the members.",
    "whole_window.member_failures_unreadable": "HV-20: harvest's own member flags decide the members.",
    "neg8.screen_failed": "HV-18/design 13.7: survivor screen decides the registered drift screen.",
    "neg8.bound_not_derived": "HV-18/design 13.7: clean corpus and surviving counts decide the bound.",
    "roster.duplicate_run_id": "CA-13: duplicated positions have no unit.",
    "instrument.precal_screen_failed": "CA-16: alignment above reference discloses and is carried.",
    "records.malformed_flag_member_exclusion_possible": "HV-22: record grammar discloses.",
    "member.cooldown_evidence_unverified": "HV-5: measured idle admission decides.",
    "instrument.binary_identity_unmeasured": "X: an unmeasured identity discloses.",
}


def _entry(family: str, klass: str, effect: str, note: str) -> dict:
    return {"family": family, "klass": klass, "effect": effect, "blinding": "STRUCTURE", "note": note}


NEW_CODES = {
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
           "acceptance_preflight_unverified": "CA-15/S-068: preflight record shape discloses in HAZARD mode.",
           "capture_list_write_failed": "CA-38: list write failure discloses; capture stays.",
           "capture_list_line_unreadable": "CA-38: malformed list line is skipped and disclosed.",
           "capture_bytes_changed": "HV-6: historical capture changed bytes disclose.",
       }.items()},
    "calibration.operative_bound_above_stop": _entry("CALIBRATION", "PHYSICS", "EXCLUDE_WINDOW", "T1: measured operative timing bound is above the registered physical stop line."),
    "calibration.bracket_incomplete": _entry("CALIBRATION", "NUMBER", "EXCLUDE_WINDOW", "No two refitted captures: operative timing bound is undefined."),
    "neg8.survivor_screen_failed": _entry("NEG8", "NUMBER", "EXCLUDE_WINDOW", "Registered endpoint drift screen fails on the surviving references."),
    "neg8.survivor_screen_undefined": _entry("NEG8", "NUMBER", "EXCLUDE_WINDOW", "No defined corpus bound or insufficient endpoints: drift allowance is undefined."),
    "neg8.survivor_screen_passed": _entry("NEG8", "NUMBER", "DISCLOSE", "Survivor screen passed; counts only outside withheld."),
    "model.files_differ_from_registered": _entry("MODEL_IDENTITY", "PHYSICS", "EXCLUDE_WINDOW", "Design 13.9: measured model bytes are another experiment."),
    "model.stack_differs_from_registered": _entry("MODEL_IDENTITY", "NUMBER", "EXCLUDE_WINDOW", "HV-21: runtime, kernel packages, tokenizer or quantization changes the executed computation."),
    "model.identity_unrecorded": _entry("MODEL_IDENTITY", "REPRESENTATION", "DISCLOSE", "HV-21: precheck directly measures the files; a missing run identity discloses."),
    "code.changed_since_registration": _entry("CODE_IDENTITY", "REPRESENTATION", "DISCLOSE", "HV-23/CA-46: changed committed paths are recorded."),
    "code.executed_head_unrecorded": _entry("CODE_IDENTITY", "REPRESENTATION", "DISCLOSE", "HV-23: unrecorded executing commit discloses."),
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
