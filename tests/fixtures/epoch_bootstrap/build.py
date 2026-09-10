"""Build a disposable derivation-session ledger the S4 issuer can read."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_ledger import (
    BRACKET_SESSION_SLOTS,
    LEDGER_SCHEMA,
    SESSION_KIND_DERIVATION,
    append_bracket_session_receipt,
    artifact_hashes,
    claim_bracket_session_slot,
    derivation_session_slots,
    finalize_bracket_session_slot,
    load_calibration_ledger_snapshot,
)
from joulewise.uncertainty_evidence import CLOCK_ANCHOR_UNRESOLVED, CLOCK_METHOD_V3
from tests.git_fixture import init_git_fixture

# The successor epoch under test: 25G83, the build that invalidated the r6
# acceptance.  Only `os_build` differs from r6's epoch, which is exactly the
# real bootstrap's shape.
TARGET_EPOCH = {
    "os_build": "25G83",
    "hardware_model": "Mac15,9",
    "power_policy": "ac_high_power",
    "sampling_interval_ms": 100,
    "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
    "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
}
T1_BINDINGS = {
    "os_build": "25G83",
    "hardware_model": "Mac15,9",
    "powermetrics_sha256": "b7" + "6" * 62,
    "mlx_version": "0.31.2",
    "protocol_sha256": "9e" + "a" * 62,
    "anchor_method_version": "powermetrics_native_second_rate_aware_set_membership_v1",
    "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
    "power_policy": "ac_high_power",
    "sampling_interval_ms": 100,
    "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
}
SESSION_ID = "derivation-night-1"


@dataclass(frozen=True)
class Slot:
    """One declared slot's outcome, decided by the fixture, not by a value."""

    b_fiducial_s: str
    disposition: str = "valid"
    # None = the anchor-v3 replay resolved.  A string is the recorded refusal
    # detail, e.g. the registered `affine_clock_fit_empty` exclusion class.
    unresolved_detail: str | None = None
    # When set, the PRIMARY bytes carry this lexeme while the ledger row keeps
    # `b_fiducial_s`: the disagreement the issuer must refuse on.
    evidence_lexeme: str | None = None
    # The method the recorded clock anchor claims.  Anything other than the
    # anchor-v3 method is not an anchor-v3 replay at all.
    anchor_method: str = CLOCK_METHOD_V3


def _write_bundle(custody: Path, attempt_id: str, slot: Slot) -> None:
    (custody / "raw").mkdir(parents=True)
    (custody / "raw" / "powermetrics.plist").write_bytes(b"raw-" + attempt_id.encode())
    (custody / "events.jsonl").write_text('{"timestamp_s": 99.0}\n', encoding="utf-8")
    if slot.unresolved_detail is None:
        anchor = {
            "method": slot.anchor_method,
            "status": "resolved",
            "admissible_lower_epoch_s": 1.0,
            "admissible_upper_epoch_s": 2.0,
        }
        resolved = True
    else:
        anchor = {
            "method": slot.anchor_method,
            "status": "unknown",
            "reason": CLOCK_ANCHOR_UNRESOLVED,
            "detail": slot.unresolved_detail,
        }
        resolved = False
    # Written as raw text so the b_fiducial_s LEXEME is exactly the fixture's,
    # not a float round trip: the issuer reads it back with parse_float=str.
    (custody / "instrument_evidence.json").write_text(
        "{"
        f'"schema_version": "joulewise.instrument_evidence.v1", '
        f'"validation_id": "{attempt_id}", '
        f'"b_fiducial_s": {slot.evidence_lexeme or slot.b_fiducial_s}, '
        f'"clock_anchor_resolved": {"true" if resolved else "false"}, '
        f'"clock_anchor": {json.dumps(anchor)}'
        "}\n",
        encoding="utf-8",
    )
    (custody / "manifest.json").write_text(
        json.dumps({"attempt": attempt_id}) + "\n", encoding="utf-8"
    )


def build_derivation_ledger(
    root: Path,
    slots: Sequence[Slot],
    *,
    session_id: str = SESSION_ID,
    session_kind: str = SESSION_KIND_DERIVATION,
    second_session: tuple[str, Sequence[Slot]] | None = None,
) -> dict[str, Path]:
    """Create a Git-committed ledger holding one or two closed sessions.

    ``second_session`` writes a further derivation session into the SAME ledger
    without naming it in the registration, which is the addendum A-7
    counterfactual: valid, target-epoch rows that belong to no registered
    session.
    """

    root.mkdir(parents=True, exist_ok=True)
    init_git_fixture(root, "-q")
    runs = root / "runs"
    runs.mkdir()
    ledger = runs / "calibration_observation_ledger.jsonl"
    pin = runs / "calibration_ledger_head_pin.json"
    pin.write_text(
        json.dumps(
            {"sequence": 0, "head_digest": "0" * 64, "ledger_schema": LEDGER_SCHEMA},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _commit(root, "genesis pin")
    # A bracket-kind session's slot list is fixed at ("pre", "post"); only a
    # derivation session declares an arbitrary ordered list.
    _write_session(ledger, runs, pin, session_id, slots, session_kind)
    if second_session is not None:
        _write_session(
            ledger, runs, pin, second_session[0], second_session[1],
            SESSION_KIND_DERIVATION,
        )
    snapshot = load_calibration_ledger_snapshot(
        ledger, pin, require_committed_pin=False, verify_custody=False,
        mode="read_replay", repo_root=root,
    )
    pin.write_text(
        json.dumps(
            {
                "sequence": snapshot.head_sequence,
                "head_digest": snapshot.head_digest,
                "ledger_schema": LEDGER_SCHEMA,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _commit(root, "terminal pin")
    return {"root": root, "ledger": ledger, "pin": pin, "runs": runs}


def _write_session(
    ledger: Path,
    runs: Path,
    pin: Path,
    session_id: str,
    slots: Sequence[Slot],
    session_kind: str,
) -> None:
    # A session opens only at head-equals-pin, so a fixture writing a SECOND
    # session advances the working pin to the physical head first, exactly as
    # the desk does between two derivation nights.
    snapshot = load_calibration_ledger_snapshot(
        ledger, pin, require_committed_pin=False, verify_custody=False,
        mode="read_replay", repo_root=ledger.parent.parent,
    )
    pin.write_text(
        json.dumps(
            {
                "sequence": snapshot.head_sequence,
                "head_digest": snapshot.head_digest,
                "ledger_schema": LEDGER_SCHEMA,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    declared = (
        derivation_session_slots(len(slots))
        if session_kind == SESSION_KIND_DERIVATION
        else BRACKET_SESSION_SLOTS
    )
    append_bracket_session_receipt(
        ledger,
        session_id=session_id,
        window_id="window-derivation",
        plan_id="plan-derivation",
        plan_sha256="ab" * 32,
        evidence_root_id="evidence-derivation",
        runs_root=runs,
        slots={
            name: {
                "attempt_id": f"{session_id}-{name}",
                "custody_locator": str(runs / "instrument_validation" / f"{session_id}-{name}"),
                "identity_epoch": TARGET_EPOCH,
                "t1_bindings": T1_BINDINGS,
            }
            for name in declared
        },
        session_kind=session_kind,
        declared_slots=declared,
        head_pin_path=pin,
        require_committed_pin=False,
    )
    for name, slot in zip(declared, slots, strict=True):
        attempt_id = f"{session_id}-{name}"
        custody = runs / "instrument_validation" / attempt_id
        _write_bundle(custody, attempt_id, slot)
        claim_bracket_session_slot(
            ledger, session_id=session_id, slot=name, attempt_id=attempt_id
        )
        finalize_bracket_session_slot(
            ledger,
            session_id=session_id,
            slot=name,
            disposition=slot.disposition,
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=TARGET_EPOCH,
            t1_bindings=T1_BINDINGS,
            capture_wall_time_s="99.0",
            exact_bound_lexeme_s=slot.b_fiducial_s,
        )


def tamper_member_bundle(fixture: dict[str, Path], attempt_id: str, name: str) -> None:
    """Rewrite one member's primary bytes AFTER finalization, and re-commit.

    The ledger row's `artifact_sha256` was written at finalization, so this is
    the post-finalization edit the custody-hash clause exists to catch.
    """

    target = fixture["runs"] / "instrument_validation" / attempt_id / name
    target.write_text(target.read_text(encoding="utf-8").replace("}", ', "tampered": 1}', 1),
                      encoding="utf-8")
    _commit(fixture["root"], "tamper")


def _commit(root: Path, message: str) -> None:
    subprocess.run(("git", "-C", str(root), "add", "-A"), check=True, capture_output=True)
    subprocess.run(
        (
            "git", "-C", str(root),
            "-c", "user.email=fixture@example.invalid",
            "-c", "user.name=fixture",
            "commit", "-q", "-m", message,
        ),
        check=True,
        capture_output=True,
    )
