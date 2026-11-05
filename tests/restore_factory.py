"""Construct synthetic historical restore records; never a production command."""
from __future__ import annotations
import os
from pathlib import Path
from joulewise import receipt_readers as readiness, calibration_ledger as ledger, night_gate
from joulewise import qualification_readers as q
from joulewise.qualification_readers import regular_bytes, validate_tail, require_null, reservation_binding
SCHEMA = q.NULL_RESTORE_SCHEMA

def restore(plan_reference, harvest_reference, seed_reference, *, output):
    plan_path = q.authenticated_reference(plan_reference)
    plan = q.load_plan(plan_path, "G2B_SHAKEDOWN")
    harvest_path = q.authenticated_reference(harvest_reference)
    harvest = q.read(harvest_path)
    require_null(q.counted_attempt(harvest, harvest_path), plan, plan_reference["sha256"])
    if harvest_path != Path(plan.block_archive_root) / "attempts" / plan.plan_id / "harvest.json":
        raise q.HarvestRefusal("null_restore_harvest_not_counted_attempt")
    q.authenticate_attempt_record(harvest, Path(plan.block_archive_root))
    q.attempt_history(harvest, plan.block_archive_root, current_harvest=harvest_path)
    custody = Path(plan.custody_root)
    if Path(output) != custody / "null-reservation-restore.json":
        raise q.HarvestRefusal("null_restore_output_not_attempt_custody")
    capture_path = custody / plan.pack_night["pack_id"] / "arm_readiness.t0.inputs/ledger-reservation.json"
    capture = q.read(capture_path)
    result = readiness.parse_json_bytes(capture.get("stdout", "").encode())
    row = result.get("receipt")
    live, pin_path = reservation_binding(plan, capture, row)
    seed_path = q.authenticated_reference(seed_reference)
    seed = regular_bytes(seed_path, "jsonl")
    # Permanent native writer lease serializes the restore with every append.
    with ledger.CalibrationWriterLease(live):
        attempted, pin_raw = regular_bytes(live, "jsonl"), regular_bytes(pin_path, "json")
        validate_tail(seed, attempted, readiness.parse_json_bytes(pin_raw), row)
        require_null(q.counted_attempt(harvest, harvest_path), plan, plan_reference["sha256"])
        # Preserve attempted bytes before any mutation. Each output is create-once.
        saved = custody / "null-reservation-ledger.jsonl"
        saved_pin = custody / "null-reservation-head-pin.json"
        if any(path.exists() or path.is_symlink() for path in (Path(output), saved, saved_pin)):
            raise q.HarvestRefusal("null_restore_custody_exists")
        for path, raw in ((saved, attempted), (saved_pin, pin_raw)):
            with path.open("xb") as stream:
                os.chmod(path, 0o600)
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
        ledger._fsync_parent_directory(custody)
        pin_ref = q.reference(pin_path)
        # Recheck byte identity under the lease immediately before truncation.
        if regular_bytes(live, "jsonl") != attempted or regular_bytes(pin_path, "json") != pin_raw:
            raise q.HarvestRefusal("null_restore_source_changed")
        descriptor = os.open(live, os.O_WRONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(seed)
            stream.truncate(len(seed))
            stream.flush()
            os.fsync(stream.fileno())
        if regular_bytes(live, "jsonl") != seed or regular_bytes(pin_path, "json") != pin_raw:
            raise q.HarvestRefusal("null_restore_verification_failed")
        record = {"schema": SCHEMA, "plan_id": plan.plan_id, "plan": plan_reference,
                  "harvest": harvest_reference, "seed": seed_reference,
                  "reservation": q.reference(capture_path), "attempt_ledger": q.reference(saved),
                  "restored_ledger": q.reference(live), "head_pin": pin_ref,
                  "head_pin_copy": q.reference(saved_pin),
                  "dropped_receipt_sha256": row["receipt_digest"]}
        with Path(output).open("xb") as stream:
            os.chmod(output, 0o600)
            stream.write(readiness.render_json(record))
            stream.flush()
            os.fsync(stream.fileno())
        ledger._fsync_parent_directory(custody)
    return q.reference(output)
