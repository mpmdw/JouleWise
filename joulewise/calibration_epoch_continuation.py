"""Authenticated additional identity epochs judged by an unchanged acceptance.

The candidate issuer owns primary-evidence replay. This reader authenticates
issued bytes and, when given a snapshot, checks every finalized session row.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, DecimalException, InvalidOperation, localcontext
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from joulewise.authentication_io import read_authentication_input
from joulewise import calibration_bracketing as acceptance_module
from joulewise.calibration_bracketing import EPOCH_CONTINUATION_REGISTRY
from joulewise.calibration_ledger import (
    IDENTITY_EPOCH_FIELDS, LEDGER_SCHEMA, SESSION_KIND_DERIVATION,
    CalibrationLedgerSnapshot, content_id_from_artifact_hashes,
)

CONTINUATION_SCHEMA = "joulewise.calibration_epoch_continuation.v1"
CONTINUATION_INVALID = "calibration_epoch_continuation_invalid"
MINIMUM_RETAINED = 6
DECLARED_SLOT_COUNT = 12
RULE_SOURCE = "ratified_operatives of the acceptance"
TERMINAL_STATES = frozenset({"finalized", "aborted"})
SLOT_KEYS = frozenset({
    "slot", "attempt_id", "content_id", "manifest_sha256",
    "instrument_evidence_sha256", "disposition", "anchor_v3_resolved",
    "anchor_v3_detail", "b_fiducial_s",
})


class ContinuationRefusal(ValueError):
    """A named detail beneath calibration_epoch_continuation_invalid."""


def _require(condition: bool, field: str) -> None:
    if not condition:
        raise ContinuationRefusal(field)


def _decimal(value: Any, field: str) -> Decimal:
    _require(isinstance(value, str) and bool(value), field)
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ContinuationRefusal(field) from exc
    _require(number.is_finite() and number >= 0, field)
    return number


def continuation_rule(acceptance: Mapping[str, Any]) -> dict[str, Any]:
    """Read both comparators from the registry and cross-check the artifact."""

    registered = acceptance_module.acceptance_generation_operatives(
        acceptance["acceptance_id"], acceptance=acceptance,
    )
    _require(registered is not None, "acceptance_operatives_unregistered")
    supplied = acceptance["decimal_derivation"]["ratified_operatives"]
    for field in ("preflight_level_screen_s", "bracket_screen_s"):
        _require(supplied.get(field) == registered[field], f"ratified_operatives.{field}")
    return {
        "level_screen_s": registered["preflight_level_screen_s"],
        "operative_bracket_screen_s": registered["bracket_screen_s"],
        "m_minimum": MINIMUM_RETAINED,
        "source": RULE_SOURCE,
    }


def envelope_holds_over_all_valid(
    lexemes_all_valid: Sequence[str], rule: Mapping[str, Any],
) -> bool:
    """Check both screens independently of file-asserted anchor resolution.

    This has no minimum count: retention alone determines m and whether the
    equivalence statistics are inconclusive. An empty valid set is vacuous.
    """

    values = [_decimal(value, "b_fiducial_s") for value in lexemes_all_valid]
    level = _decimal(rule["level_screen_s"], "rule.level_screen_s")
    bracket = _decimal(rule["operative_bracket_screen_s"], "rule.operative_bracket_screen_s")
    with localcontext() as context:
        context.prec = 80 + sum(
            len(v.as_tuple().digits) + abs(v.as_tuple().exponent)
            for v in [*values, level, bracket]
        )
        return all(value <= level for value in values) and (
            not values or max(values) - min(values) <= bracket
        )


def equivalence_statistics(
    lexemes: Sequence[str], rule: Mapping[str, Any],
) -> dict[str, Any]:
    """Reconstruct the fixed-rule verdict in exact decimal arithmetic."""

    values = [_decimal(value, "b_fiducial_s") for value in lexemes]
    level = _decimal(rule["level_screen_s"], "rule.level_screen_s")
    bracket = _decimal(rule["operative_bracket_screen_s"], "rule.operative_bracket_screen_s")
    # Enough precision for subtraction of every represented decimal place,
    # including a very small positive quantum at a comparator boundary.
    with localcontext() as context:
        operands = [*values, level, bracket]
        context.prec = 80 + sum(
            len(v.as_tuple().digits) + abs(v.as_tuple().exponent)
            for v in operands
        )
        low = min(values) if values else None
        high = max(values) if values else None
        spread = high - low if values else None
        verdict = "inconclusive"
        if len(values) >= MINIMUM_RETAINED:
            verdict = "pass" if all(value <= level for value in values) and spread <= bracket else "fail"
    return {
        "m": len(values),
        "retained_min_s": str(low) if low is not None else None,
        "retained_max_s": str(high) if high is not None else None,
        "retained_range_s": str(spread) if spread is not None else None,
        "verdict": verdict,
    }


def _json_object(raw: bytes) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in items:
            _require(key not in value, f"duplicate_key.{key}")
            value[key] = item
        return value

    def nonfinite(value: str) -> None:
        raise ContinuationRefusal(f"nonfinite_json.{value}")

    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    _require(isinstance(value, dict), "continuation_not_object")
    return value


@dataclass(frozen=True)
class Continuation:
    continuation_id: str
    file_sha256: str
    continued_identity_epoch: Mapping[str, Any]
    session_id: str
    acknowledged_attempt_ids: tuple[str, ...]
    m: int
    verdict: str
    ledger_cross_check: str

    def evaluation_record(self) -> dict[str, Any]:
        return {
            "continuation_id": self.continuation_id,
            "continuation_file_sha256": self.file_sha256,
            "session_id": self.session_id,
            "m": self.m,
            "verdict": self.verdict,
            "ledger_cross_check": self.ledger_cross_check,
        }


def authenticate_epoch_continuation(
    path: Path,
    acceptance_artifact: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot | None,
    *,
    registry: Mapping[str, Mapping[str, Any]] = EPOCH_CONTINUATION_REGISTRY,
) -> Continuation:
    """Authenticate one path; the CLI uses exactly this production reader."""

    raw = read_authentication_input(path, grammar="json", label="epoch continuation")
    value = _json_object(raw)
    _require("candidate_not_issued" not in value, "candidate_not_issued")
    continuation_id = value.get("continuation_id")
    _require(isinstance(continuation_id, str) and bool(continuation_id), "continuation_id")
    registered = registry.get(continuation_id)
    _require(registered is not None, "continuation_unregistered")
    file_sha = hashlib.sha256(raw).hexdigest()
    _require(file_sha == registered.get("file_sha256"), "continuation_file_sha256")
    artifact = acceptance_module._authenticated_explicit_acceptance_bound(acceptance_artifact)
    _require(artifact is not None and artifact.get("artifact_role") == "issued", "acceptance_unauthenticated")
    _require(value.get("schema_version") == CONTINUATION_SCHEMA, "schema_version")
    _require(value.get("decision_ids") == ["D-102"], "decision_ids")
    for field, expected in (
        ("acceptance_id", artifact["acceptance_id"]),
        ("acceptance_file_sha256", acceptance_module._acceptance_artifact_sha256(artifact)),
        ("acceptance_derivation_sha256", artifact["derivation_sha256"]),
    ):
        _require(value.get(field) == expected, field)
    _require(value.get("verdict") == "pass", "verdict")
    core = {key: item for key, item in value.items() if key != "derivation_sha256"}
    _require(value.get("derivation_sha256") == acceptance_module._canonical_sha256(core), "derivation_sha256")
    epoch = value.get("continued_identity_epoch")
    _require(isinstance(epoch, dict) and set(epoch) == set(IDENTITY_EPOCH_FIELDS), "continued_identity_epoch")
    for field, item in epoch.items():
        _require(type(item) is type(artifact["identity_epoch"][field]) and item not in (None, ""), f"continued_identity_epoch.{field}")
    _require(epoch != artifact["identity_epoch"], "continued_identity_epoch_unchanged")
    ruling = value["ruling"]
    _require(ruling["channel"] == "directive issue 316" and ruling["authority"] == "owner", "ruling")
    _require(date.fromisoformat(ruling["d102_addendum_date"]).isoformat() == ruling["d102_addendum_date"], "ruling.d102_addendum_date")
    rule = continuation_rule(artifact)
    _require(value["rule"] == rule, "rule")
    evidence = value["evidence"]
    _require(isinstance(evidence["session_id"], str) and bool(evidence["session_id"]), "evidence.session_id")
    ledger = evidence["ledger"]
    _require(ledger["ledger_schema"] == LEDGER_SCHEMA and type(ledger["head_sequence"]) is int
             and ledger["head_sequence"] > 0 and acceptance_module._valid_sha256(ledger["head_digest"]), "evidence.ledger")
    _require(evidence["session_kind"] == SESSION_KIND_DERIVATION, "evidence.session_kind")
    _require(evidence["session_state"] in TERMINAL_STATES, "evidence.session_state")
    declared = evidence["declared_slots"]
    _require(isinstance(declared, list) and len(declared) == DECLARED_SLOT_COUNT
             and all(isinstance(slot, str) and slot for slot in declared)
             and len(set(declared)) == DECLARED_SLOT_COUNT, "evidence.declared_slots")
    slots = evidence["slots"]
    _require(isinstance(slots, list), "evidence.slots")
    for slot in slots:
        _require(isinstance(slot, dict) and set(slot) == SLOT_KEYS, "slots.keys")
    _require([slot["slot"] for slot in slots] == declared, "evidence.slots")
    acknowledged = evidence["acknowledged_attempt_ids"]
    finalized = [slot for slot in slots if slot["content_id"] is not None]
    _require(isinstance(acknowledged, list) and all(isinstance(a, str) and a for a in acknowledged)
             and len(set(acknowledged)) == len(acknowledged)
             and acknowledged == [slot["attempt_id"] for slot in finalized], "evidence.acknowledged_attempt_ids")
    lexemes: list[str] = []
    lexemes_all_valid: list[str] = []
    for slot in slots:
        _require(type(slot["anchor_v3_resolved"]) is bool, "slots.anchor_v3_resolved")
        _require(slot["anchor_v3_detail"] is None or isinstance(slot["anchor_v3_detail"], str), "slots.anchor_v3_detail")
        _require(not slot["anchor_v3_resolved"] or slot["anchor_v3_detail"] is None, "slots.anchor_v3_detail")
        _require(slot["disposition"] != "valid" or slot["anchor_v3_resolved"]
                 or bool(slot["anchor_v3_detail"]), "slots.anchor_v3_detail_required")
        if slot["content_id"] is None:
            _require(evidence["session_state"] == "aborted" and slot["disposition"] in {"window_exhausted", "no_row"}
                     and slot["attempt_id"] is None
                     and slot["manifest_sha256"] is None and slot["instrument_evidence_sha256"] is None
                     and slot["b_fiducial_s"] is None and slot["anchor_v3_resolved"] is False,
                     "slots.unfinalized")
            continue
        hashes = {"manifest.json": slot["manifest_sha256"], "instrument_evidence.json": slot["instrument_evidence_sha256"]}
        _require(content_id_from_artifact_hashes(hashes) == slot["content_id"], "slots.content_id")
        _require(slot["disposition"] in {"valid", "ordinary-invalid", "systematic-invalid"}, "slots.disposition")
        if slot["b_fiducial_s"] is not None:
            _decimal(slot["b_fiducial_s"], "slots.b_fiducial_s")
        if slot["disposition"] == "valid":
            _decimal(slot["b_fiducial_s"], "slots.b_fiducial_s")
            lexemes_all_valid.append(slot["b_fiducial_s"])
            if slot["anchor_v3_resolved"]:
                lexemes.append(slot["b_fiducial_s"])
    _require(envelope_holds_over_all_valid(lexemes_all_valid, rule),
             "unresolved_valid_row_exceeds_envelope")
    statistics = equivalence_statistics(lexemes, rule)
    for field, expected in statistics.items():
        actual = value["verdict"] if field == "verdict" else evidence[field]
        _require(type(actual) is type(expected) and actual == expected, f"evidence.{field}")

    cross_check = "skipped_no_ledger_snapshot"
    if ledger_snapshot is not None:
        _require(not ledger_snapshot.refusal_reasons, "ledger_snapshot_invalid")
        session = ledger_snapshot.bracket_session_by_id.get(evidence["session_id"])
        _require(session is not None, "session_absent")
        _require(session.state in TERMINAL_STATES and session.state == evidence["session_state"], "session_not_terminal_or_state_mismatch")
        _require(session.session_kind == SESSION_KIND_DERIVATION, "session_not_derivation")
        _require(list(session.declared_slots) == declared, "session_declared_slots")
        _require(ledger_snapshot.ledger_schema == ledger["ledger_schema"]
                 and ledger_snapshot.head_sequence >= ledger["head_sequence"], "ledger_head_precedes_continuation")
        file_finalized = {(slot["slot"], slot["attempt_id"]) for slot in finalized}
        ledger_finalized = {(name, row.attempt_id) for name, row in session.finalized_slots.items()}
        # Check absence before equality so a finalized row relabelled as an
        # unused opportunity is reported explicitly, even if the subset passes.
        _require(all(slot["slot"] not in session.finalized_slots
                     for slot in slots if slot["content_id"] is None), "hidden_finalized_row")
        _require(file_finalized == ledger_finalized, "ledger_finalized_slots_mismatch")
        _require(all((row.bracket_slot, row.attempt_id) in file_finalized
                     for row in ledger_snapshot.observations
                     if row.bracket_session_id == session.session_id), "hidden_finalized_row")
        for slot in finalized:
            row = session.finalized_slots.get(slot["slot"])
            _require(row is not None and row.attempt_id == slot["attempt_id"], "acknowledged_attempt_missing")
            _require(ledger_snapshot.observation_by_attempt.get(row.attempt_id) == row
                     and row.bracket_session_id == session.session_id, "acknowledged_attempt_missing")
            _require(row.content_id == slot["content_id"], "acknowledged_content_id")
            _require(row.classification_disposition == slot["disposition"]
                     and row.exact_bound_lexeme_s == slot["b_fiducial_s"], "acknowledged_row_disagrees")
            if slot["disposition"] == "valid" and slot["anchor_v3_resolved"]:
                _require(dict(row.identity_epoch) == epoch, "acknowledged_identity_epoch")
        cross_check = "verified_terminal_derivation_session"
    return Continuation(
        continuation_id, file_sha, MappingProxyType(epoch), evidence["session_id"],
        tuple(acknowledged), evidence["m"], "pass", cross_check,
    )


def load_epoch_continuations(
    acceptance_artifact: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot | None,
    *,
    registry: Mapping[str, Mapping[str, Any]] = EPOCH_CONTINUATION_REGISTRY,
    refusal_details: list[dict[str, str]] | None = None,
) -> tuple[Continuation, ...]:
    """Return valid issued continuations; optionally collect every refusal.

    Without a snapshot only the session cross-check is skipped. Each returned
    continuation explicitly records that degradation in ``ledger_cross_check``.
    """

    accepted: list[Continuation] = []
    for continuation_id, entry in registry.items():
        try:
            continuation = authenticate_epoch_continuation(
                Path(entry["path"]), acceptance_artifact, ledger_snapshot, registry=registry,
            )
            _require(continuation.continuation_id == continuation_id, "registry_continuation_id")
            accepted.append(continuation)
        except (OSError, ValueError, KeyError, TypeError, AttributeError, DecimalException, OverflowError) as exc:
            if refusal_details is not None:
                refusal_details.append({"reason": CONTINUATION_INVALID,
                                        "continuation_id": continuation_id, "detail": str(exc)})
    return tuple(accepted)


def acceptance_judged_epochs(
    acceptance_artifact: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    *,
    registry: Mapping[str, Mapping[str, Any]] = EPOCH_CONTINUATION_REGISTRY,
    refusal_details: list[dict[str, str]] | None = None,
    continuation_details: list[Continuation] | None = None,
) -> tuple[Mapping[str, Any], ...]:
    """The original epoch followed by authenticated continued epochs."""

    continuations = load_epoch_continuations(
        acceptance_artifact, ledger_snapshot, registry=registry, refusal_details=refusal_details,
    )
    if continuation_details is not None:
        continuation_details.extend(continuations)
    return (MappingProxyType(dict(acceptance_artifact["identity_epoch"])),
            *(c.continued_identity_epoch for c in continuations))
