#!/usr/bin/env python3
"""Prepare an unissued continuation, or authenticate one through its byte pin.

A continuation lets an unchanged acceptance judge another identity epoch (the
machine's six-field identity). A judged epoch is an identity that acceptance
may evaluate. Acknowledged rows are exactly the equivalence night's finalized
attempts; these bypass only the range-expansion trigger. Systematic failures
remain triggers and prevent candidate preparation. The level screen caps
each retained capture's bound. The bracket screen caps their range, maximum
minus minimum. Both come from the prior
acceptance's ratified operatives: no threshold is fitted to this night.
"""

from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal, DecimalException
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import calibration_bracketing as acceptance_module  # noqa: E402
from joulewise.calibration_epoch_continuation import (  # noqa: E402
    CONTINUATION_SCHEMA, DECLARED_SLOT_COUNT, TERMINAL_STATES,
    ContinuationRefusal, _decimal, _json_object, acceptance_judged_epochs,
    authenticate_epoch_continuation, continuation_rule, equivalence_statistics,
)
from joulewise.calibration_ledger import (  # noqa: E402
    DEFAULT_HEAD_PIN_PATH, SESSION_KIND_DERIVATION,
    content_id_from_artifact_hashes, load_calibration_ledger_snapshot,
)
from scripts.issue_calibration_acceptance_generation import (  # noqa: E402
    PrepareRefusal, _read_member_evidence, anchor_v3_replay_outcome,
)

VERDICT_EXITS = {"pass": 0, "fail": 4, "inconclusive": 5}


def _refuse(condition: bool, field: str) -> None:
    if condition:
        raise ContinuationRefusal(field)


def _load_snapshot(args: argparse.Namespace):
    return load_calibration_ledger_snapshot(
        args.ledger, args.head_pin, require_committed_pin=True,
        verify_custody=False, mode="read_replay", repo_root=Path(args.repo_root),
    )


def _refuse_out_path(out: Path, force: bool) -> None:
    parts = out.resolve().parts
    _refuse(any(a == "configs" and b == "calibration" for a, b in zip(parts, parts[1:])),
            "out_under_configs_calibration")
    _refuse(out.exists() and not force, "out_exists_use_force")


def derive_record(args: argparse.Namespace) -> tuple[dict[str, Any], Mapping[str, Any], Any]:
    """Re-read every finalized slot's primary bytes, then apply the fixed rule."""

    artifact = acceptance_module.load_calibration_acceptance_bound(Path(args.acceptance))
    _refuse(artifact is None or artifact.get("artifact_role") != "issued", "acceptance_unauthenticated")
    rule = continuation_rule(artifact)
    snapshot = _load_snapshot(args)
    session = snapshot.bracket_session_by_id.get(args.session_id)
    _refuse(session is None, "session_absent")
    _refuse(session.session_kind != SESSION_KIND_DERIVATION, "session_not_derivation")
    _refuse(session.state not in TERMINAL_STATES, "session_not_terminal")
    _refuse(len(session.declared_slots) != DECLARED_SLOT_COUNT, "session_requires_12_declared_slots")
    _refuse(bool(snapshot.refusal_reasons), "ledger: " + ", ".join(snapshot.refusal_reasons))
    for name, observation in session.finalized_slots.items():
        _refuse(observation.classification_disposition == "systematic-invalid",
                f"night_contains_systematic_failure: slots.{name}; continuation would be stale on arrival; "
                "the desk reports the failure to Ed under D-102's systematic-failure trigger")
    continued_epoch: dict[str, Any] | None = None
    slots: list[dict[str, Any]] = []
    retained: list[str] = []
    acknowledged: list[str] = []
    for name in session.declared_slots:
        observation = session.finalized_slots.get(name)
        if observation is None:
            slots.append({
                "slot": name, "attempt_id": None, "content_id": None,
                "manifest_sha256": None, "instrument_evidence_sha256": None,
                "disposition": "window_exhausted" if session.abort_reason == "window_exhausted" else "no_row",
                "anchor_v3_resolved": False, "anchor_v3_detail": None,
                "b_fiducial_s": None,
            })
            continue
        _refuse(snapshot.observation_by_attempt.get(observation.attempt_id) != observation,
                f"slots.{name}.observation_missing")
        evidence, _manifest = _read_member_evidence(observation)
        content_id = content_id_from_artifact_hashes(observation.artifact_sha256)
        _refuse(content_id is None or content_id != observation.content_id, f"slots.{name}.content_id")
        resolved, detail = anchor_v3_replay_outcome(evidence)
        lexeme = evidence.get("b_fiducial_s")
        _refuse(lexeme != observation.exact_bound_lexeme_s, f"slots.{name}.b_fiducial_s")
        _refuse(lexeme is not None and not isinstance(lexeme, str), f"slots.{name}.b_fiducial_s")
        if lexeme is not None:
            _decimal(lexeme, f"slots.{name}.b_fiducial_s")
        disposition = observation.classification_disposition
        _refuse(disposition not in {"valid", "ordinary-invalid", "systematic-invalid"}, f"slots.{name}.disposition")
        slots.append({
            "slot": name, "attempt_id": observation.attempt_id,
            "content_id": content_id,
            "manifest_sha256": observation.artifact_sha256["manifest.json"],
            "instrument_evidence_sha256": observation.artifact_sha256["instrument_evidence.json"],
            "disposition": disposition,
            "anchor_v3_resolved": resolved, "anchor_v3_detail": detail,
            "b_fiducial_s": lexeme,
        })
        acknowledged.append(observation.attempt_id)
        if disposition == "valid" and resolved:
            _refuse(not isinstance(lexeme, str), f"slots.{name}.b_fiducial_s")
            epoch = dict(observation.identity_epoch)
            if continued_epoch is None:
                continued_epoch = epoch
            _refuse(epoch != continued_epoch, f"slots.{name}.identity_epoch_not_unanimous")
            _refuse(epoch == artifact["identity_epoch"], "continued_identity_epoch_unchanged")
            retained.append(lexeme)
    statistics = equivalence_statistics(retained, rule)
    record = {
        "schema_version": CONTINUATION_SCHEMA,
        "decision_ids": ["D-102"],
        "acceptance_id": artifact["acceptance_id"],
        "acceptance_file_sha256": acceptance_module._acceptance_artifact_sha256(artifact),
        "acceptance_derivation_sha256": artifact["derivation_sha256"],
        "continued_identity_epoch": continued_epoch,
        "ruling": {"channel": "directive issue 316", "d102_addendum_date": args.d102_addendum_date, "authority": "owner"},
        "rule": rule,
        "evidence": {
            "ledger": {"ledger_schema": snapshot.ledger_schema,
                       "head_sequence": snapshot.head_sequence, "head_digest": snapshot.head_digest},
            "session_id": session.session_id, "session_kind": session.session_kind,
            "session_state": session.state, "declared_slots": list(session.declared_slots),
            "slots": slots, "acknowledged_attempt_ids": acknowledged,
            **{key: item for key, item in statistics.items() if key != "verdict"},
        },
        "verdict": statistics["verdict"],
    }
    return record, artifact, session


def _s9_projection(record: Mapping[str, Any], artifact: Mapping[str, Any], session: Any) -> dict[str, Any]:
    """Rebuild the science fields of the S9 v1 witness without importing it."""

    evidence = record["evidence"]
    rule = record["rule"]
    outcomes = []
    retained = []
    for slot in evidence["slots"]:
        keep = slot["disposition"] == "valid" and slot["anchor_v3_resolved"]
        outcome, detail = "valid_resolved", None
        if slot["content_id"] is None:
            outcome = "unused" if slot["disposition"] == "window_exhausted" else "no_row"
            detail = "window_exhausted" if outcome == "unused" else None
        elif slot["disposition"] != "valid":
            outcome, detail = "disposition", slot["disposition"]
        elif not slot["anchor_v3_resolved"]:
            outcome, detail = "valid_unresolved", slot["anchor_v3_detail"] or "unknown"
        outcomes.append({"slot": slot["slot"], "attempt_id": slot["attempt_id"],
                         "b_fiducial_s": slot["b_fiducial_s"] if keep else None,
                         "retained": keep, "outcome": outcome, "detail": detail})
        if keep:
            retained.append({key: slot[key] for key in ("slot", "attempt_id", "b_fiducial_s")})
    stats = artifact["decimal_derivation"]["source_statistics"]
    operatives = artifact["decimal_derivation"]["ratified_operatives"]
    expected: dict[str, Any] = {
        "schema_version": "joulewise.epoch_equivalence_check.v1",
        "reference_envelope": {
            "acceptance_id": artifact["acceptance_id"],
            "corpus_n": artifact["derivation_corpus"]["n"],
            "raw_corpus_maximum_s": stats["maximum_s"], "raw_corpus_range_s": stats["range_s"],
            "level_screen_s": rule["level_screen_s"], "bracket_screen_s": rule["operative_bracket_screen_s"],
            "maximum_budgetable_drift_s": operatives["maximum_budgetable_drift_s"],
        },
        "session": {"session_id": session.session_id, "session_kind": session.session_kind,
                    "state": session.state, "abort_reason": session.abort_reason,
                    "declared_slots": list(session.declared_slots)},
        "slot_outcomes": outcomes, "retained": retained, "m": evidence["m"],
        "verdict": record["verdict"].upper(),
    }
    if record["verdict"] == "inconclusive":
        expected.update({key: None for key in ("maximum_s", "minimum_s", "range_s", "maximum_slot", "minimum_slot",
                                              "level_screen_comparison", "bracket_screen_comparison")})
    else:
        low, high, spread = (evidence[key] for key in ("retained_min_s", "retained_max_s", "retained_range_s"))
        low_slot = next(row["slot"] for row in retained if Decimal(row["b_fiducial_s"]) == Decimal(low))
        high_slot = next(row["slot"] for row in retained if Decimal(row["b_fiducial_s"]) == Decimal(high))
        expected.update({"minimum_s": low, "maximum_s": high, "range_s": spread,
                         "minimum_slot": low_slot, "maximum_slot": high_slot,
                         "level_screen_comparison": {
                             "left": high, "left_source": f"retained maximum ({high_slot})", "operator": "<=",
                             "right": rule["level_screen_s"], "right_source": "operative preflight_level_screen_s",
                             "holds": Decimal(high) <= Decimal(rule["level_screen_s"]),
                         },
                         "bracket_screen_comparison": {
                             "left": spread, "left_source": "retained range (max - min)", "operator": "<=",
                             "right": rule["operative_bracket_screen_s"], "right_source": "operative bracket_screen_s",
                             "holds": Decimal(spread) <= Decimal(rule["operative_bracket_screen_s"]),
                         }})
    return expected


def _crosscheck(expected: Any, actual: Any, field: str = "equivalence_record") -> None:
    if isinstance(expected, dict):
        _refuse(not isinstance(actual, dict), field)
        provenance = {
            "equivalence_record": {"verdict_reason", "tool_sha256", "repo_head", "emitted_at"},
            "equivalence_record.reference_envelope": {"acceptance_path"},
        }.get(field, set())
        unknown = set(actual) - set(expected) - provenance
        _refuse(bool(unknown), f"{field}.{sorted(unknown)[0]}" if unknown else field)
        for key, value in expected.items():
            _refuse(key not in actual, f"{field}.{key}")
            _crosscheck(value, actual[key], f"{field}.{key}")
    elif isinstance(expected, list):
        _refuse(not isinstance(actual, list) or len(actual) != len(expected), field)
        for index, (left, right) in enumerate(zip(expected, actual)):
            _crosscheck(left, right, f"{field}[{index}]")
    else:
        _refuse(type(expected) is not type(actual) or expected != actual, field)


def prepare_candidate(args: argparse.Namespace) -> int:
    _refuse_out_path(args.out, args.force)
    input_paths = [args.ledger, args.head_pin, args.acceptance, args.equivalence_record]
    _refuse(any(path is not None and args.out.resolve() == Path(path).resolve()
                for path in input_paths), "out_overwrites_input")
    _refuse(date.fromisoformat(args.d102_addendum_date).isoformat() != args.d102_addendum_date,
            "d102_addendum_date")
    record, artifact, session = derive_record(args)
    _refuse(any(args.out.resolve() == (Path(row.custody_locator) / name).resolve()
                for row in session.finalized_slots.values()
                for name in row.artifact_sha256), "out_overwrites_primary_evidence")
    if args.equivalence_record is not None:
        witness = _json_object(args.equivalence_record.read_bytes())
        expected = _s9_projection(record, artifact, session)
        # Recognized science extensions are checked, never silently ignored.
        # Unknown fields refuse so a future witness format cannot smuggle in a
        # conflicting statistic that this version does not know how to replay.
        for key in ("acceptance_id", "acceptance_file_sha256", "acceptance_derivation_sha256",
                    "continued_identity_epoch", "rule", "evidence"):
            if key in witness:
                expected[key] = record[key]
        if "ledger" in witness:
            expected["ledger"] = record["evidence"]["ledger"]
        if "rc" in witness:
            expected["rc"] = VERDICT_EXITS[record["verdict"]]
        _crosscheck(expected, witness)
    rc = VERDICT_EXITS[record["verdict"]]
    if rc:
        print(json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False))
        return rc
    # An opaque content identity is deterministic and does not choose an
    # issuance filename or new acceptance generation for the lead.
    record["continuation_id"] = "epoch-continuation-" + acceptance_module._canonical_sha256(record)
    record["candidate_not_issued"] = True
    record["derivation_sha256"] = acceptance_module._canonical_sha256(record)
    raw = (json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("wb" if args.force else "xb") as destination:
        destination.write(raw)
    print(raw.decode("utf-8"), end="")
    return 0


def check(args: argparse.Namespace) -> int:
    value = _json_object(args.candidate.read_bytes())
    _refuse("candidate_not_issued" in value, "candidate_not_issued")
    entry = acceptance_module.ISSUED_ACCEPTANCE_REGISTRY.get(value.get("acceptance_id"))
    _refuse(entry is None, "acceptance_unregistered")
    artifact = acceptance_module.load_calibration_acceptance_bound(entry["path"])
    _refuse(artifact is None, "acceptance_unauthenticated")
    snapshot = _load_snapshot(args) if args.ledger is not None else None
    continuation = authenticate_epoch_continuation(args.candidate, artifact, snapshot)
    loaded = []
    refusals = []
    epochs = acceptance_judged_epochs(
        artifact, snapshot, continuation_details=loaded, refusal_details=refusals,
    )
    _refuse(not any(item.continuation_id == continuation.continuation_id
                    and item.file_sha256 == continuation.file_sha256 for item in loaded),
            "continuation_registry_path_unavailable_or_invalid")
    print(json.dumps({
        **continuation.evaluation_record(),
        "judged_epochs": [dict(epoch) for epoch in epochs],
        "continuation_refusals": refusals,
    }, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare-candidate", description=__doc__, help="re-derive a PASS night and write an unissued continuation")
    prepare.add_argument("--session-id", required=True, help="terminal derivation session containing the acknowledged rows")
    prepare.add_argument("--ledger", type=Path, required=True, help="immutable calibration observation ledger")
    prepare.add_argument("--head-pin", type=Path, required=True, help="committed digest and sequence of the ledger head")
    prepare.add_argument("--acceptance", type=Path, required=True, help="byte-pinned issued acceptance supplying both screens")
    prepare.add_argument("--repo-root", type=Path, required=True, help="repository authenticating the committed head pin")
    prepare.add_argument("--d102-addendum-date", required=True, help="owner ruling date, YYYY-MM-DD; preparation does not issue the addendum")
    prepare.add_argument("--out", type=Path, required=True, help="candidate output outside every configs/calibration directory")
    prepare.add_argument("--force", action="store_true", help="allow replacement of the explicitly named output")
    prepare.add_argument("--equivalence-record", type=Path, help="optional S9 v1 witness; disagreements name the science field and refuse")
    verify = sub.add_parser("check", description=__doc__, help="require issued, registry-pinned bytes and print judged epochs")
    verify.add_argument("--candidate", type=Path, required=True, help="file to check; marked candidates refuse until separately issued and registered")
    verify.add_argument("--ledger", type=Path, help="also verify the terminal session and acknowledged attempts")
    verify.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH, help="committed ledger head pin, used with --ledger")
    verify.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="repository authenticating the committed head pin")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return prepare_candidate(args) if args.command == "prepare-candidate" else check(args)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, PrepareRefusal,
            DecimalException, OverflowError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
