"""Offline derivation of the production bracket-session receipt cadence.

Campaign generators use this module to replay the authenticated production
ledger writer rather than copying receipt counts or event sequences into pack
source.  The replay deliberately retains only cadence and row shape; receipt
digests and absolute ledger positions exist only when a real window is armed.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any, Callable

import joulewise.calibration_ledger as calibration_ledger


ORACLE_SCHEMA = "joulewise.bracket_session_receipt_oracle.v1"


def _sha256(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _write_head_pin(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _model_vector(fields: tuple[str, ...]) -> dict[str, Any]:
    vector: dict[str, Any] = {field: f"receipt-oracle-{field}" for field in fields}
    if "sampling_interval_ms" in vector:
        vector["sampling_interval_ms"] = 100
    return vector


def _operation_functions() -> tuple[Callable[..., Any], ...]:
    return (
        calibration_ledger.append_bracket_session_receipt,
        calibration_ledger.claim_bracket_session_slot,
        calibration_ledger.finalize_bracket_session_slot,
    )


_OPERATION_FUNCTION_NAMES = tuple(
    operation.__name__ for operation in _operation_functions()
)


def _physical_shape(receipt: Any) -> dict[str, Any]:
    target = receipt.get("target_core", {})
    return {
        "relative_sequence": receipt["sequence"],
        "schema_version": receipt["schema_version"],
        "event": receipt["event"],
        "target_schema_version": receipt.get("target_schema_version"),
        "target_event": receipt.get("target_event"),
        "slot": receipt.get("slot", target.get("slot")),
    }


def derive_bracket_session_receipt_oracle() -> dict[str, Any]:
    """Replay one finalized pre/post bracket session through production code.

    The result is safe to embed in a prospective campaign pack: it records the
    deterministic physical cadence and shape, while keeping all arm-dependent
    receipt bytes and the absolute terminal sequence empty.
    """

    with tempfile.TemporaryDirectory(prefix="joulewise-receipt-oracle-") as raw_root:
        root = Path(raw_root)
        ledger_path = root / "calibration_observation_ledger.jsonl"
        head_pin_path = root / "calibration_ledger_head.json"
        initial_pin = {
            "sequence": 0,
            "head_digest": calibration_ledger.GENESIS_DIGEST,
            "ledger_schema": calibration_ledger.LEDGER_SCHEMA,
        }
        _write_head_pin(head_pin_path, initial_pin)

        session_id = "receipt-oracle-session"
        runs_root = root / "runs"
        identity_epoch = _model_vector(calibration_ledger.IDENTITY_EPOCH_FIELDS)
        t1_bindings = _model_vector(calibration_ledger.T1_FIELDS)
        slots = {
            slot: {
                "attempt_id": f"receipt-oracle-{slot}",
                "custody_locator": str(
                    runs_root / "instrument_validation" / f"receipt-oracle-{slot}"
                ),
                "identity_epoch": identity_epoch,
                "t1_bindings": t1_bindings,
            }
            for slot in calibration_ledger.BRACKET_SESSION_SLOTS
        }

        calibration_ledger.append_bracket_session_receipt(
            ledger_path,
            session_id=session_id,
            window_id="receipt-oracle-window",
            plan_id="receipt-oracle-plan",
            plan_sha256=_sha256("receipt-oracle-plan"),
            evidence_root_id="receipt-oracle-evidence",
            runs_root=runs_root,
            slots=slots,
            head_pin_path=head_pin_path,
            require_committed_pin=False,
            repo_root=root,
        )
        for slot in calibration_ledger.BRACKET_SESSION_SLOTS:
            attempt_id = slots[slot]["attempt_id"]
            calibration_ledger.claim_bracket_session_slot(
                ledger_path,
                session_id=session_id,
                slot=slot,
                attempt_id=attempt_id,
            )
            calibration_ledger.finalize_bracket_session_slot(
                ledger_path,
                session_id=session_id,
                slot=slot,
                disposition="valid",
                custody_locator=slots[slot]["custody_locator"],
                artifact_sha256={
                    artifact: _sha256(f"{slot}:{artifact}")
                    for artifact in calibration_ledger.GOVERNED_ARTIFACTS
                },
                identity_epoch=identity_epoch,
                t1_bindings=t1_bindings,
                capture_wall_time_s="1.0",
                exact_bound_lexeme_s="0.01",
            )

        terminal_pin = calibration_ledger.terminal_head_pin_for_session(
            ledger_path,
            session_id=session_id,
        )
        _write_head_pin(head_pin_path, terminal_pin)
        snapshot = calibration_ledger.load_calibration_ledger_snapshot(
            ledger_path,
            head_pin_path,
            require_committed_pin=False,
            verify_custody=False,
            repo_root=root,
        )
        if snapshot.refusal_reasons:
            joined = ", ".join(snapshot.refusal_reasons)
            raise RuntimeError(f"production receipt replay refused: {joined}")
        session = next(
            (item for item in snapshot.bracket_sessions if item.session_id == session_id),
            None,
        )
        if session is None or session.state != "finalized":
            raise RuntimeError("production receipt replay did not finalize its session")

        physical_shape = [_physical_shape(receipt) for receipt in snapshot.receipts]
        logical_operation_count = sum(
            receipt["schema_version"] != calibration_ledger.CONTROL_SCHEMA
            for receipt in snapshot.receipts
        )
        terminal_delta = terminal_pin["sequence"] - initial_pin["sequence"]
        return {
            "schema_version": ORACLE_SCHEMA,
            "status": "derived_from_production_model",
            "source": {
                "module": calibration_ledger.__name__,
                "operation_functions": list(_OPERATION_FUNCTION_NAMES),
                "append_policy_revision": calibration_ledger.APPEND_POLICY_REVISION,
                "claim_policy_revision": calibration_ledger.CLAIM_POLICY_REVISION,
            },
            "session_terminal_state": session.state,
            "logical_operation_count": logical_operation_count,
            "receipt_count": len(snapshot.receipts),
            "physical_receipt_shape": physical_shape,
            "terminal_sequence": None,
            "terminal_sequence_rule": {
                "base": "authenticated_arm_head_sequence",
                "delta": terminal_delta,
                "applicability": "clean_path_no_recovery_control_rows",
                "recovery_note": (
                    "Authenticated recovery control rows (for example an "
                    "abandon-tail repair between an intent and its "
                    "reconstructed target) may lawfully extend the terminal "
                    "sequence beyond base+delta. Arm-time verification must "
                    "validate the business-receipt cadence separately from "
                    "authenticated control rows rather than requiring "
                    "base+delta exactly."
                ),
            },
            "arm_time_receipts": [],
        }


__all__ = ["ORACLE_SCHEMA", "derive_bracket_session_receipt_oracle"]
