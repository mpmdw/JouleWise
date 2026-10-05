#!/usr/bin/env python3
"""Restore only a NULL attempt's exact native T-0 reservation unit.

The retained append-intent and its one bracket-session-open row are replayed
with the native ledger grammar, then saved create-once before restoring seed.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness, calibration_ledger as ledger, night_gate
from joulewise import v5_qualification as q
from joulewise.authentication_io import read_authentication_input
from scripts.capture_t0_step import COMMAND_CAPTURE_SCHEMA

SCHEMA = "joulewise.v5_null_reservation_restore.v1"


def regular_bytes(path, grammar):
    path = Path(path)
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise q.HarvestRefusal("null_restore_input_not_regular")
    return read_authentication_input(path, grammar=grammar, label="block-4 NULL reservation restore")


def validate_tail(seed, attempted, pin, reservation):
    """Use the existing ledger parser and shape; never redefine ledger rows."""
    pin_head = ledger._head_pin(pin)
    receipts, reasons = ledger._parse_ledger(seed)
    seed_head = (len(receipts), receipts[-1]["receipt_digest"] if receipts else ledger.GENESIS_DIGEST)
    if reasons or pin_head is None or pin_head != seed_head:
        raise q.HarvestRefusal("null_restore_seed_not_pinned_head")
    if not attempted.startswith(seed):
        raise q.HarvestRefusal("null_restore_seed_not_exact_prefix")
    tail = attempted[len(seed):]
    lines = tail.splitlines(keepends=True)
    if len(lines) != 2 or any(not line.endswith(b"\n") for line in lines):
        raise q.HarvestRefusal("null_restore_tail_not_one_reservation_unit")
    intent, row = (readiness.parse_json_bytes(line) for line in lines)
    if (not isinstance(row, dict) or row != reservation
            or row.get("event") != ledger.BRACKET_SESSION_OPEN_EVENT
            or not ledger._valid_session_receipt_shape(row)
            or row.get("sequence") != seed_head[0] + 2
            or intent.get("event") != ledger.APPEND_INTENT_EVENT
            or intent.get("sequence") != seed_head[0] + 1
            or intent.get("predecessor_digest") != seed_head[1]
            or row.get("predecessor_digest") != intent.get("receipt_digest")
            or intent.get("target_core") != ledger._target_core(row)
            or any(intent["target_core"].get(key) != row.get(key) for key in ("session_id", "plan_id"))):
        raise q.HarvestRefusal("null_restore_tail_not_attempt_reservation")
    complete, reasons = ledger._parse_ledger(attempted)
    if reasons or len(complete) != len(receipts) + 2:
        raise q.HarvestRefusal("null_restore_ledger_chain_invalid")
    return row


def require_null(harvest, plan, plan_digest):
    if (harvest.get("schema") != q.ATTEMPT_HARVEST_SCHEMA
            or harvest.get("verdict") != "NULL"
            or harvest.get("plan_id") != plan.plan_id or harvest.get("plan_sha256") != plan_digest):
        raise q.HarvestRefusal("null_restore_requires_attempt_null_harvest")
    started = Path(plan.custody_root) / "night/chain.started"
    if started.exists() or started.is_symlink():
        raise q.HarvestRefusal("null_restore_chain_started")


def flag(argv, name):
    if not isinstance(argv, list) or argv.count(name) != 1:
        raise q.HarvestRefusal("null_restore_reservation_argv_invalid")
    index = argv.index(name)
    if index + 1 >= len(argv):
        raise q.HarvestRefusal("null_restore_reservation_argv_invalid")
    return argv[index + 1]


def reservation_binding(plan, capture, row):
    """Bind the dropped row to the actual T-0 command and frozen ARM identity."""
    if (capture.get("schema_version") != COMMAND_CAPTURE_SCHEMA
            or capture.get("step_id") != "ledger-reservation" or capture.get("exit_code") != 0):
        raise q.HarvestRefusal("null_restore_reservation_capture_invalid")
    argv = capture.get("argv")
    expected_script = str(Path(plan.measurement_root) / "scripts/reserve_calibration_window_bracket.py")
    if (not isinstance(argv, list) or len(argv) < 2 or argv[1] != expected_script
            or "--execute" not in argv):
        raise q.HarvestRefusal("null_restore_reservation_argv_invalid")
    result = readiness.parse_json_bytes(capture.get("stdout", "").encode())
    if result.get("status") != "reserved" or result.get("receipt") != row:
        raise q.HarvestRefusal("null_restore_reservation_receipt_mismatch")
    pack = Path(plan.pack_night["pack_root"])
    frozen = q.read(pack / "calibration_plan.json")
    record = q.read(Path(plan.custody_root) / "qualification-plan-record.json")
    context = q.read(q.authenticated_reference(record["arm_context"]))
    for name, value in {"session-id": context["bracket_session_id"],
                        "plan-id": frozen["plan_id"], "plan-sha256": q.sha(pack / "calibration_plan.json"),
                        "runs-root": context["claim_runs_root"],
                        "pre-attempt-id": context["pre_attempt_id"],
                        "post-attempt-id": context["post_attempt_id"]}.items():
        if flag(argv, "--" + name) != value:
            raise q.HarvestRefusal("null_restore_reservation_identity_mismatch")
    for name in ("session_id", "window_id", "plan_id", "plan_sha256", "evidence_root_id", "runs_root"):
        if row[name] != flag(argv, "--" + name.replace("_", "-")):
            raise q.HarvestRefusal("null_restore_reservation_identity_mismatch")
    return Path(flag(argv, "--ledger")), Path(flag(argv, "--head-pin"))


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


def verify_restore(reference, previous_harvest, *, restored_ledger=None):
    """Replay saved attempted bytes and bind the next attempt to its NULL prior."""
    record = q.read(q.authenticated_reference(reference))
    expected = {"schema", "plan_id", "plan", "harvest", "seed", "reservation", "attempt_ledger",
                "restored_ledger", "head_pin", "head_pin_copy", "dropped_receipt_sha256"}
    if set(record) != expected or record["schema"] != SCHEMA or record["harvest"] != previous_harvest:
        raise q.HarvestRefusal("null_restore_record_identity_mismatch")
    plan_path = q.authenticated_reference(record["plan"])
    plan = night_gate.NightPlan.from_mapping(q.read(plan_path))
    harvest_path = q.authenticated_reference(record["harvest"])
    harvest = q.counted_attempt(q.read(harvest_path), harvest_path)
    require_null(harvest, plan, record["plan"]["sha256"])
    if record["plan_id"] != plan.plan_id or Path(reference["path"]) != Path(plan.custody_root) / "null-reservation-restore.json":
        raise q.HarvestRefusal("null_restore_record_identity_mismatch")
    if (Path(record["attempt_ledger"]["path"]) != Path(plan.custody_root) / "null-reservation-ledger.jsonl"
            or Path(record["reservation"]["path"]) != Path(plan.custody_root) / plan.pack_night["pack_id"] /
               "arm_readiness.t0.inputs/ledger-reservation.json"):
        raise q.HarvestRefusal("null_restore_custody_path_mismatch")
    seed = regular_bytes(q.authenticated_reference(record["seed"]), "jsonl")
    attempted = regular_bytes(q.authenticated_reference(record["attempt_ledger"]), "jsonl")
    capture = q.read(q.authenticated_reference(record["reservation"]))
    row = readiness.parse_json_bytes(capture["stdout"].encode())["receipt"]
    live, pin = reservation_binding(plan, capture, row)
    # The live pin may advance after this restore. Authenticate its retained
    # bytes against the path/digest recorded while the native lease was held.
    pin_path = q.authenticated_reference(record["head_pin_copy"])
    if (pin_path != Path(plan.custody_root) / "null-reservation-head-pin.json"
            or record["head_pin"] != {"path": str(pin), "sha256": record["head_pin_copy"]["sha256"]}
            or record["restored_ledger"] != {"path": str(live), "sha256": record["seed"]["sha256"]}):
        raise q.HarvestRefusal("null_restore_ledger_binding_mismatch")
    validate_tail(seed, attempted, q.read(pin_path), row)
    if row["receipt_digest"] != record["dropped_receipt_sha256"]:
        raise q.HarvestRefusal("null_restore_dropped_row_mismatch")
    # Writer verification checks the live seed. A later harvester replays the
    # retained pre-reservation seed, since its own reservation extended live.
    if restored_ledger is not None:
        path = q.authenticated_reference(restored_ledger)
        if restored_ledger["sha256"] != record["seed"]["sha256"] or regular_bytes(path, "jsonl") != seed:
            raise q.HarvestRefusal("null_restore_next_seed_mismatch")
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("plan", "harvest", "seed"):
        parser.add_argument("--" + name, type=Path, required=True)
        parser.add_argument("--" + name + "-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        restore(*({"path": str(getattr(args, name).absolute()), "sha256": getattr(args, name + "_sha256")}
                  for name in ("plan", "harvest", "seed")), output=args.output.absolute())
    except (OSError, ValueError, KeyError, TypeError):
        print("status=REFUSED")
        return 2
    print("status=RESTORED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
