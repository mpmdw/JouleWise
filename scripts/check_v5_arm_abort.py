#!/usr/bin/env python3
"""Observe a fresh a1 ARM PASS/GO, then its same-boot expiry without launching.

Two phases are essential: an expired receipt's early refusal cannot establish
that its original PASS/GO was authentic. ``observe`` runs the full live verifier;
``finish`` reauthenticates those bytes and observes the canonical expiry refusal.
This tool never invokes the launcher, driver, sampler or an OFF setter.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness
from joulewise import arm_readiness_evidence_t0 as author
from joulewise import battery_float, network_time_off
from joulewise.night_gate import NightPlan, _authenticate_pack_records
from scripts.write_v5_qualification_plan import (
    ARM_ONLY_SCHEMA, create_record, exact, locator, no_fill, number,
    read_locator, read_object, require, safe_path,
)

START_SCHEMA = "joulewise.v5_arm_abort_observation.v1"
CONTROL_SCHEMA = "joulewise.v5_arm_abort_control.v1"
ABSENCE_KEYS = {"consumption_absent", "launch_pending_absent", "chain_started_absent", "bundles_absent", "sampler_artifacts_absent"}


def context_at(path):
    path = safe_path(path)
    context = read_object(path)
    no_fill(context)
    require(context.get("schema_version") == ARM_ONLY_SCHEMA
            and context.get("occurrence") in {"a1", "a2"}
            and context.get("mode") == "ARM_ONLY_NO_LAUNCH", "a1_context")
    plan = NightPlan.from_mapping(context["plan_binding"])
    require(path.parent == Path(plan.custody_root), "context_custody")
    require(plan.pack_night == context["pack_night"], "context_pack_binding")
    prepared = _authenticate_pack_records(plan)
    require(prepared["authorization_record"]["purpose"] == "G2B_SHAKEDOWN"
            and prepared["authorization_record"]["claim_eligible"] is False
            and prepared["authorization_record"]["permitted_blocks"] == 1, "a1_authority")
    return context, plan, prepared


def absence(plan, context):
    roots = [safe_path(plan.custody_root)]
    # All possible collection roots come from the authenticated ARM context.
    for name in ("claim_runs_root", "bound_runs_root", "quarantine_root"):
        roots.append(safe_path(context[name]))
    forbidden = {"launch.pending", "chain.started", "metadata.json", "powermetrics.raw.txt"}
    for root in roots:
        for path in root.rglob("*"):
            require(not path.is_symlink(), "absence.symlink")
            require(not (path.name in forbidden or path.name.endswith(".consumed.json")
                         or path.name == "arm_readiness.consumptions" and any(path.iterdir())), "launch_or_bundle_present")
    for name in ("claim_runs_root", "bound_runs_root"):
        # Empty runs roots preclude unknown bundle layouts, sampler transcripts
        # and pending reservations as well as the canonical bundle sentinels.
        require(not any(safe_path(context[name]).iterdir()), "runs_not_empty")
    return {"consumption_absent": True, "launch_pending_absent": True,
            "chain_started_absent": True, "bundles_absent": True,
            "sampler_artifacts_absent": True}


def t0_sources(plan, arm, at):
    pack_custody = Path(plan.custody_root) / plan.pack_night["pack_id"]
    evidence = []
    deadlines = []
    q110 = None
    arm_refs = {r["path"]: r for r in arm["evidence"] if r["namespace"] == "WINDOW_CUSTODY"}
    for row in author._EXPECTED_ROWS:
        path = safe_path(pack_custody / author._EVIDENCE_DIRECTORY / author._receipt_name(row))
        reference = locator(path)
        relative = path.relative_to(pack_custody).as_posix()
        require(relative in arm_refs and arm_refs[relative]["sha256"] == reference["sha256"], "t0_arm_binding")
        receipt = readiness.validate_evidence_receipt(read_object(path))
        require(receipt["kind"] == author._ROW_KIND[row] and receipt["status"] == "PASS"
                and receipt["boot_session_id"] == arm["boot_session_id"]
                and receipt["pack_sha256"] == plan.pack_night["pack_sha256"]
                and receipt["head_commit"] == plan.repo_head
                and at <= receipt["valid_until_monotonic_ns"], "t0_receipt")
        origin = receipt["valid_until_monotonic_ns"] - author._validity_horizon_ns(receipt["kind"])
        require(0 <= origin <= at, "t0_origin")
        evidence.append(reference)
        sidecar = path.with_name(path.name + ".sha256")
        require(sidecar.read_bytes() == readiness.gnu_sidecar(reference["sha256"], path.name), "t0_sidecar")
        evidence.append(locator(sidecar))
        deadlines.append({"receipt": reference, "kind": receipt["kind"],
                          "validity_origin_monotonic_ns": origin,
                          "valid_until_monotonic_ns": receipt["valid_until_monotonic_ns"]})
        for fact in receipt["facts"]:
            source_path = safe_path(pack_custody / fact["source_path"])
            require(pack_custody in source_path.parents, "t0_source_custody")
            source_ref = {"path": str(source_path), "sha256": fact["source_sha256"]}
            _, source_raw = read_locator(source_ref)
            evidence.append(source_ref)
            source = readiness.parse_json_bytes(source_raw)
            # The live verifier has already replayed the source. Retain its
            # underlying artifact hashes because expiry refusal precedes replay.
            for item in source.get("primary_artifacts", []):
                ref = {"path": str(safe_path(Path(plan.measurement_root) / item["path"])), "sha256": item["sha256"]}
                read_locator(ref)
                evidence.append(ref)
            for item in source.get("input_artifacts", []):
                read_locator(item)
                evidence.append(item)
            if fact["fact_id"] == "clock.correct_and_prior_state.v1":
                require(fact["source_kind"] == "PROBE", "clock_not_probe")
                q110 = {"clock_receipt": reference,
                        "r1_batch_finished_monotonic_ns": fact["value"]["r1_batch_finished_monotonic_ns"],
                        "validity_origin_monotonic_ns": origin,
                        "elapsed_ns": origin - fact["value"]["r1_batch_finished_monotonic_ns"]}
    captures = []
    for name in author._CAPTURE_FILES.values():
        path = pack_custody / author._INPUT_DIRECTORY / name
        evidence.append(locator(path))
        captures.append(read_object(path))
    first_boundary = min(capture["started_monotonic_ns"] for capture in captures)
    require(0 <= first_boundary <= at, "t0_first_boundary")
    require(q110 is not None and q110["elapsed_ns"] >= 0, "q110_clock_source")
    # Q110 is evidence for later adjudication, not a new 600-second arm gate.
    q110["below_registered_600s"] = q110["elapsed_ns"] < 600_000_000_000
    return evidence, deadlines, q110, first_boundary


def battery_sources(value, plan):
    exact(value, {"arm", "publication", "t0"}, "battery_sites")
    native_phases = {"arm": {"arm", "arm_check"},
                     "publication": {"publication", "publish_install", "validate_install"},
                     "t0": {"t0", "t0_power_row"}}
    refs = []
    for phase, item in value.items():
        exact(item, {"record", "raw"}, "battery_source")
        _, raw_record = read_locator(item["record"])
        record = readiness.parse_json_bytes(raw_record)
        _, raw = read_locator(item["raw"])
        require(record["schema"] == battery_float.SCHEMA and record["plan_id"] == plan.plan_id
                and record["phase"] in native_phases[phase]
                and record["raw_stdout_sha256"] == readiness.sha256_bytes(raw)
                and record["argv"] == list(battery_float.IOREG_BATTERY_ARGV)
                and record["exit_code"] == 0 and not record["probe_error"]
                and not record["timed_out"], "battery_record")
        parsed = battery_float.parse(raw, record["wall_time_s"])
        require(all(record.get(k) == v for k, v in parsed.items()), "battery_replay")
        battery_float.require_pass(record)
        refs.extend([item["record"], item["raw"]])
    return refs


def observe(context_path, arm_path, evidence_path, *, now_ns=None, now_epoch=None, boot=None):
    now_ns = time.monotonic_ns if now_ns is None else now_ns
    now_epoch = time.time if now_epoch is None else now_epoch
    boot = readiness._current_boot_session_id if boot is None else boot
    context, plan, prepared = context_at(context_path)
    arm_context = context["arm_context"]
    absence(plan, arm_context)
    arm_path = safe_path(arm_path)
    require(arm_path.parent == Path(plan.custody_root) / plan.pack_night["pack_id"] / "arm_readiness.receipts", "arm_namespace")
    arm, _, digest = readiness._read_arm_with_sidecar(arm_path)
    namespace = readiness.scan_receipt_namespace(arm_path.parent, "arm")
    require(len(namespace) == 1 and namespace[0]["path"] == arm_path, "a1_fresh_arm_namespace")
    require(arm["arm_context"] == context["arm_context"]
            and arm["pack"]["pack_id"] == plan.pack_night["pack_id"]
            and arm["pack"]["plan_id"] == plan.plan_id
            and arm["pack"]["pack_sha256"] == plan.pack_night["pack_sha256"]
            and arm["pack"]["pack_root"] == plan.pack_night["pack_root"]
            and arm["reviewed_main"]["head_commit"] == plan.repo_head
            and arm["boot_session_id"] == boot()
            and arm["status"] == "PASS" and arm["arm_disposition"] == "GO", "arm_bindings")
    confirmation = prepared["confirmation_record"]
    verification = readiness.verify_arm_receipt(plan.pack_night["pack_root"], arm_path,
        step6_confirmation_table=confirmation["table_path"], expected_confirmation_digest=confirmation["table_sha256"])
    require(verification["receipt_sha256"] == digest, "arm_verification_digest")
    at, epoch = now_ns(), now_epoch()
    require(at <= arm["valid_until_monotonic_ns"], "arm_already_expired")
    sources, horizons, q110, first_boundary = t0_sources(plan, arm, at)
    evidence_path = safe_path(evidence_path)
    evidence = read_object(evidence_path)
    exact(evidence, {"network_time_off", "battery", "expiry_check_deadline_epoch_s", "s1_t0_not_before_epoch_s"}, "evidence")
    sources.extend(battery_sources(evidence["battery"], plan))
    off_path, _ = read_locator(evidence["network_time_off"])
    off = network_time_off.read_receipt(off_path, plan_id=plan.plan_id, window_id=arm["pack"]["window_id"])
    require(off["boot_id"] == arm["boot_session_id"], "off_boot")
    # OFF is written inside R0. E-9 readiness is the first governed settled
    # ledger use; using R0's start would always produce a negative interval.
    readiness_capture = read_object(Path(plan.custody_root) / plan.pack_night["pack_id"]
                                   / author._INPUT_DIRECTORY / "ledger-readiness.json")
    settled_at = readiness_capture["started_monotonic_ns"]
    require(type(settled_at) is int and first_boundary <= settled_at <= at
            and readiness_capture["boot_session_id"] == arm["boot_session_id"], "off_settle_boundary")
    require(network_time_off.seconds_since_receipt(off, {"epoch_s": epoch - (at - settled_at) / 1e9,
            "monotonic_s": settled_at / 1e9, "boot_id": arm["boot_session_id"]}) >= 600, "off_settle")
    expiry_epoch = epoch + (arm["valid_until_monotonic_ns"] + 1 - at) / 1e9
    deadline = evidence["expiry_check_deadline_epoch_s"]
    require(expiry_epoch < deadline <= evidence["s1_t0_not_before_epoch_s"], "expiry_deadline")
    number(deadline, "expiry_deadline")
    record = {"schema_version": START_SCHEMA, "context": locator(context_path),
              "arm_receipt": locator(arm_path), "arm_sidecar": locator(arm_path.with_name(arm_path.name + ".sha256")),
              "evidence_input": locator(evidence_path), "boot_session_id": arm["boot_session_id"],
              "observed_monotonic_ns": at, "observed_epoch_s": epoch,
              "first_t0_boundary_monotonic_ns": first_boundary,
              "arm_verification": {"status": "PASS", "arm_disposition": "GO", "receipt_sha256": digest},
              "valid_until_monotonic_ns": arm["valid_until_monotonic_ns"],
              "earliest_expired_check_monotonic_ns": arm["valid_until_monotonic_ns"] + 1,
              "expiry_check_deadline_epoch_s": deadline,
              "s1_t0_not_before_epoch_s": evidence["s1_t0_not_before_epoch_s"],
              "sources": [*sources, evidence["network_time_off"]], "receipt_horizons": horizons,
              "q110": q110, "absence": absence(plan, arm_context)}
    create_record(Path(plan.custody_root) / "arm-abort-observation.json", record)
    return record


def finish(context_path, *, wait=False, now_ns=None, now_epoch=None, boot=None, sleep=None):
    now_ns = time.monotonic_ns if now_ns is None else now_ns
    now_epoch = time.time if now_epoch is None else now_epoch
    boot = readiness._current_boot_session_id if boot is None else boot
    sleep = time.sleep if sleep is None else sleep
    context, plan, prepared = context_at(context_path)
    arm_context = context["arm_context"]
    start_path = safe_path(Path(plan.custody_root) / "arm-abort-observation.json")
    start = read_object(start_path)
    require(start["schema_version"] == START_SCHEMA and start["context"] == locator(context_path), "observation_binding")
    require(start["boot_session_id"] == boot(), "boot_changed")
    for ref in [start["arm_receipt"], start["arm_sidecar"], start["evidence_input"], *start["sources"]]:
        read_locator(ref)
    arm_path = Path(start["arm_receipt"]["path"])
    namespace = readiness.scan_receipt_namespace(arm_path.parent, "arm")
    require(len(namespace) == 1 and namespace[0]["path"] == arm_path, "a1_fresh_arm_namespace")
    arm, _, digest = readiness._read_arm_with_sidecar(arm_path)
    require(arm["boot_session_id"] == start["boot_session_id"]
            and arm["valid_until_monotonic_ns"] == start["valid_until_monotonic_ns"]
            and start["arm_verification"] == {"status": "PASS", "arm_disposition": "GO", "receipt_sha256": digest}, "observation_arm")
    target = arm["valid_until_monotonic_ns"] + 1
    while now_ns() < target:
        absence(plan, arm_context)
        require(now_epoch() < start["expiry_check_deadline_epoch_s"], "expiry_check_late")
        require(wait, "not_yet_expired")
        sleep(min(30, (target - now_ns()) / 1e9))
    require(boot() == start["boot_session_id"], "boot_changed")
    confirmation = prepared["confirmation_record"]
    try:
        readiness.verify_arm_receipt(plan.pack_night["pack_root"], arm_path,
            step6_confirmation_table=confirmation["table_path"], expected_confirmation_digest=confirmation["table_sha256"])
    except readiness.ArmReadinessError as error:
        require(error.reason_code == "readiness_record_expired", "wrong_expiry_refusal")
    else:
        raise ValueError("expired_arm_accepted")
    at, epoch = now_ns(), now_epoch()
    require(target <= at and epoch < start["expiry_check_deadline_epoch_s"]
            and epoch < start["s1_t0_not_before_epoch_s"], "expiry_or_s1_order")
    record = {"schema_version": CONTROL_SCHEMA, "occurrence": context["occurrence"], "verdict": "PASS",
              "context": locator(context_path), "observation": locator(start_path),
              "arm_receipt": start["arm_receipt"], "boot_session_id": start["boot_session_id"],
              "valid_until_monotonic_ns": arm["valid_until_monotonic_ns"],
              "checked_monotonic_ns": at, "checked_epoch_s": epoch,
              "refusal_reason_code": "readiness_record_expired", "absence": absence(plan, arm_context),
              "ordering": {"s1_t0_not_before_epoch_s": start["s1_t0_not_before_epoch_s"], "expired_before_s1_t0": True},
              "receipt_horizons": start["receipt_horizons"], "q110": start["q110"],
              "sources": start["sources"]}
    create_record(Path(plan.custody_root) / "arm-abort-control.json", record)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    arm = commands.add_parser("arm")
    arm.add_argument("--context", type=Path, required=True)
    first = commands.add_parser("observe")
    first.add_argument("--context", type=Path, required=True)
    first.add_argument("--arm-receipt", type=Path, required=True)
    first.add_argument("--evidence", type=Path, required=True)
    last = commands.add_parser("finish")
    last.add_argument("--context", type=Path, required=True)
    last.add_argument("--wait", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "arm":
            from scripts.run_night import arm_only
            result = arm_only(args.context)
        else:
            result = (observe(args.context, args.arm_receipt, args.evidence) if args.command == "observe"
                      else finish(args.context, wait=args.wait))
    except (OSError, ValueError, KeyError, TypeError):
        output, code = {"status": "REFUSED", "reason_code": "arm_abort_control_invalid"}, 2
    else:
        output, code = {"status": "PASS", "schema_version": result["schema_version"],
                        "occurrence": context_at(args.context)[0]["occurrence"]}, 0
    sys.stdout.buffer.write(readiness.render_json(output))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
