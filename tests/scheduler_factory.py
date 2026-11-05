"""Synthetic scheduler receipts for format-reader tests only."""
from __future__ import annotations
import json, os, time, uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from joulewise import scheduler_receipts as _readers
from joulewise import receipt_readers as arm_readiness
from joulewise.receipt_readers import _fsync_directory
globals().update({k: v for k, v in vars(_readers).items() if not k.startswith("__")})





def _create_boot_pin(
    path: Path, *, family_id: str, boot_session_id: str
) -> tuple[Mapping[str, Any], str]:
    pin = {
        "schema_version": CAMPAIGN_BOOT_PIN_SCHEMA,
        "family_id": family_id,
        "boot_session_id": boot_session_id,
        "created_at_utc": _utc_now(),
    }
    raw = render_json(pin)
    digest = arm_readiness.sha256_bytes(raw)
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except FileExistsError as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict",
            "campaign boot pin create lost the single-writer race",
        ) from exc
    except OSError as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict", f"cannot create campaign boot pin: {exc}"
        ) from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict", f"cannot persist campaign boot pin: {exc}"
        ) from exc
    try:
        _fsync_directory(path.parent)
        sidecar_path = path.with_name(CAMPAIGN_BOOT_PIN_SIDECAR_NAME)
        descriptor = os.open(
            sidecar_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(arm_readiness.gnu_sidecar(digest, path.name))
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_directory(path.parent)
    except Exception as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_conflict",
            f"cannot persist campaign boot pin authentication sidecar: {exc}",
            pin_sha256=digest,
        ) from exc
    return pin, digest


def _load_or_create_boot_pin(
    campaign_root: Path, *, family_id: str, live_boot_session_id: str
) -> tuple[Mapping[str, Any], str, tuple[str, ...]]:
    pin_path = campaign_root / CAMPAIGN_BOOT_PIN_NAME
    if os.path.lexists(pin_path):
        pin, digest = _read_boot_pin(pin_path)
        return pin, digest, ()
    try:
        custody_entries = sorted(path.name for path in campaign_root.iterdir())
    except OSError as exc:
        raise SchedulerGateError(
            "scheduler_boot_pin_underivable",
            f"cannot inspect campaign custody root before first pin: {exc}",
        ) from exc
    # A missing pin refuses when the root carries SCHEDULER CUSTODY
    # HISTORY (an orphan sidecar, or any emitted gate receipt): history
    # without a pin means the pin was lost, and re-pinning would
    # silently re-anchor the campaign span to a new boot (lens B-1a).
    # Entries foreign to this module (staging files, dotfiles, empty
    # dirs) do not brick first-pin creation (lens ND-1); they are
    # returned so the caller records them in the G5 observations.
    scheduler_history = sorted(
        name
        for name in custody_entries
        if name == CAMPAIGN_BOOT_PIN_SIDECAR_NAME
        or name.startswith(SCHEDULER_GATE_RECEIPT_FILE_PREFIX)
    )
    if scheduler_history:
        raise SchedulerGateError(
            "scheduler_boot_pin_underivable",
            "campaign boot pin is missing from a custody root that carries "
            f"scheduler history (entries={scheduler_history})",
        )
    foreign_entries = tuple(
        name for name in custody_entries if name not in scheduler_history
    )
    pin, digest = _create_boot_pin(
        pin_path,
        family_id=family_id,
        boot_session_id=live_boot_session_id,
    )
    return pin, digest, foreign_entries


def _live_boot_session_id() -> str:
    try:
        return arm_readiness._current_boot_session_id()
    except arm_readiness.ArmReadinessError as exc:
        raise SchedulerGateError("scheduler_boot_pin_underivable", str(exc)) from exc


def _evaluate_g5(
    *,
    campaign_root: Path,
    family_id: str,
    receipt_boot_session_ids: Mapping[str, str],
) -> tuple[dict[str, Any], str]:
    observations: dict[str, Any] = {
        "pin_path": str((campaign_root / CAMPAIGN_BOOT_PIN_NAME).resolve()),
        "family_id": family_id,
        "live_boot_session_id": "unavailable",
        "pinned_boot_session_id": "unavailable",
        "pin_sha256": None,
        "receipt_boot_session_ids": dict(receipt_boot_session_ids),
    }
    try:
        if not campaign_root.is_dir():
            raise SchedulerGateError(
                "scheduler_boot_pin_conflict", "campaign custody root must already exist"
            )
        _require_nonempty_string(family_id, "family_id")
        if not receipt_boot_session_ids:
            raise SchedulerGateError(
                "scheduler_boot_pin_underivable", "no receipt boot_session_id values were supplied"
            )
        for receipt_id, boot_session_id in receipt_boot_session_ids.items():
            _require_nonempty_string(receipt_id, "receipt id")
            _require_nonempty_string(boot_session_id, f"{receipt_id}.boot_session_id")

        live = _live_boot_session_id()
        observations["live_boot_session_id"] = live
        pin, pin_sha256, foreign_entries = _load_or_create_boot_pin(
            campaign_root, family_id=family_id, live_boot_session_id=live
        )
        observations["pin_sha256"] = pin_sha256
        if foreign_entries:
            observations["pin_creation_ignored_entries"] = list(foreign_entries)
        pinned = str(pin["boot_session_id"])
        observations["pinned_boot_session_id"] = pinned
        observations["pin_created_at_utc"] = pin["created_at_utc"]
        if pin["family_id"] != family_id:
            raise SchedulerGateError(
                "scheduler_boot_pin_conflict", "campaign boot pin belongs to a different family"
            )
        mismatched_receipts = sorted(
            receipt_id
            for receipt_id, boot_session_id in receipt_boot_session_ids.items()
            if boot_session_id != pinned
        )
        observations["mismatched_receipts"] = mismatched_receipts
        if live != pinned or mismatched_receipts:
            raise SchedulerGateError(
                "scheduler_boot_pin_mismatch",
                "live, span-pinned, and receipt boot_session_id values are not identical",
            )
        return _gate_result("G5", "PASS", observations=observations), live
    except SchedulerGateError as exc:
        if exc.pin_sha256 is not None:
            observations["pin_sha256"] = exc.pin_sha256
        code = exc.code
        if code not in G5_REASON_CODES:
            code = "scheduler_boot_pin_underivable"
        return (
            _gate_result(
                "G5",
                "REFUSE",
                observations=observations,
                refusals=[_gate_refusal(code, gate_id="G5", detail=str(exc))],
            ),
            str(observations["live_boot_session_id"]),
        )


def _g4_failed_conjunct(reviewed: Mapping[str, Any]) -> str:
    if reviewed.get("clean") is not True:
        return "dirty"
    head = reviewed.get("head_commit")
    local_main = reviewed.get("local_main_commit")
    origin_main = reviewed.get("origin_main_commit")
    if "unavailable" in {head, local_main, origin_main}:
        return "unavailable"
    if head != local_main:
        return "head_ne_local_main"
    if head != origin_main:
        return "head_ne_origin_main"
    # A malformed or stale proof that claims non-exact despite equal raw values
    # is still underivable and therefore follows the availability refusal limb.
    return "unavailable"


def _evaluate_g4(pack_root: Path) -> tuple[dict[str, Any], Mapping[str, Any]]:
    try:
        reviewed = arm_readiness.reviewed_main(pack_root)
    except Exception:
        reviewed = {
            "head_commit": "unavailable",
            "head_tree_oid": "unavailable",
            "local_main_commit": "unavailable",
            "origin_main_commit": "unavailable",
            "clean": True,
            "exact_match": False,
        }
    observations = dict(reviewed)
    observations["freeze_interlock"] = "V-3(c)_local_main_and_origin_main"
    if reviewed.get("exact_match") is True:
        observations["failed_conjunct"] = None
        return _gate_result("G4", "PASS", observations=observations), reviewed

    failed_conjunct = _g4_failed_conjunct(reviewed)
    observations["failed_conjunct"] = failed_conjunct
    code = (
        "readiness_git_tree_dirty"
        if failed_conjunct == "dirty"
        else "readiness_reviewed_main_mismatch"
    )
    detail = f"reviewed_main exact_match is not true ({failed_conjunct})"
    return (
        _gate_result(
            "G4",
            "REFUSE",
            observations=observations,
            refusals=[_gate_refusal(code, gate_id="G4", detail=detail)],
        ),
        reviewed,
    )








def evaluate_scheduler_gates(
    *,
    pack_root: Path | str,
    campaign_root: Path | str,
    family_id: str,
    window_class: str,
    receipt_boot_session_ids: Mapping[str, str],
    now_monotonic_ns: int | None = None,
    family_publication_marker: Path | str | None = None,
    step6_confirmation_table: Path | str | None = None,
    expected_confirmation_digest: str | None = None,
) -> dict[str, Any]:
    """Evaluate every scheduler gate and return a strict staged receipt.

    G5 always executes first.  A G5 refusal makes only the monotonic-clock
    gates G1/G2 ``NOT_EVALUATED``; G4 still executes, and all other staged
    gates remain visibly ``NOT_IMPLEMENTED``.
    """

    pack_path = Path(pack_root)
    campaign_path = Path(campaign_root)
    if window_class not in WINDOW_CLASSES:
        raise SchedulerGateError("scheduler_environment_error", "window_class is invalid")
    now_ns = time.monotonic_ns() if now_monotonic_ns is None else now_monotonic_ns
    if not isinstance(now_ns, int) or isinstance(now_ns, bool) or now_ns < 0:
        raise SchedulerGateError(
            "scheduler_environment_error", "now_monotonic_ns must be a non-negative integer"
        )

    # Required evaluation order: G5 completes before any other gate is called.
    g5, live_boot_session_id = _evaluate_g5(
        campaign_root=campaign_path,
        family_id=family_id,
        receipt_boot_session_ids=receipt_boot_session_ids,
    )
    g1 = _not_implemented("G1") if g5["verdict"] == "PASS" else _not_evaluated("G1")
    g2 = _not_implemented("G2") if g5["verdict"] == "PASS" else _not_evaluated("G2")
    g3 = _not_implemented("G3")
    g4, reviewed = _evaluate_g4(pack_path)
    g6 = _not_implemented("G6")
    try:
        repository = arm_readiness._repo_for_pack(pack_path)
    except arm_readiness.ArmReadinessError:
        repository = pack_path
    publication_root = campaign_path / "family_publication"
    marker_path = (
        Path(family_publication_marker)
        if family_publication_marker is not None
        else publication_root / arm_readiness.FAMILY_PUBLICATION_MARKER_NAME
    )
    confirmation_path = (
        Path(step6_confirmation_table)
        if step6_confirmation_table is not None
        else publication_root / arm_readiness.STEP6_CONFIRMATION_TABLE_NAME
    )
    g7, family_publication = _evaluate_g7(
        repository=repository,
        pack_root=pack_path,
        campaign_root=campaign_path,
        family_id=family_id,
        marker_path=marker_path,
        confirmation_path=confirmation_path,
        expected_confirmation_digest=expected_confirmation_digest,
    )

    # Pack authentication is not a scheduler gate and cannot be represented as
    # a successful placeholder.  All seven gate evaluations above still run;
    # then the owning arm-readiness loader fails closed if the pack is invalid.
    pack = arm_readiness._pack_record(pack_path)

    gates = [g5, g1, g2, g3, g4, g6, g7]
    receipt = {
        "schema_version": SCHEDULER_GATE_RECEIPT_SCHEMA,
        "receipt_kind": "window_scheduler_gate",
        "receipt_id": str(uuid.uuid4()),
        "issued_at_utc": _utc_now(),
        "now_monotonic_ns": now_ns,
        "boot_session_id": live_boot_session_id,
        "campaign_boot_pin_sha256": g5["observations"]["pin_sha256"],
        "window_class": window_class,
        "pack": dict(pack),
        "reviewed_main": dict(reviewed),
        "gates": gates,
        "verdict": (
            "GO"
            if all(gate["verdict"] in {"PASS", "RECORD_ONLY"} for gate in gates)
            else "NO-GO"
        ),
        # G3 owns claim admission and is not implemented in this stage.
        "claim_admissible": False,
        "assurance": dict(arm_readiness.ASSURANCE),
        "family_publication": family_publication,
    }
    validate_scheduler_gate_receipt(receipt)
    return receipt
