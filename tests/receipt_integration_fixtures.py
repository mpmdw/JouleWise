"""Synthetic evidence fixture construction shared by stored receipt tests."""
from __future__ import annotations
import copy, hashlib, json, subprocess, tempfile, shutil, time
from pathlib import Path
from unittest import mock
from joulewise import receipt_readers as readiness
from joulewise.receipt_readers import *
from joulewise.identity_pins import IdentityPinProjectionError
from tests.fixtures.arm_clock import coherent_clock_anchor
from tests.receipt_factory import generate_arm_receipt, generate_dry_run_receipt, generate_freeze_receipt
from tests.test_arm_readiness_schemas import *
def write_receipt(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = render_json(value)
    path.write_bytes(raw)
    (path.parent / f"{path.name}.sha256").write_bytes(
        gnu_sidecar(hashlib.sha256(raw).hexdigest(), path.name)
    )


def install_passing_dry_run(pack: Path, custody: Path) -> None:
    pack_record = readiness._pack_record(pack)
    reviewed = reviewed_main(pack)
    receipt = sample_dry_run(custody)
    receipt["pack"] = pack_record
    command = [
        "reviewed-head",
        reviewed["head_commit"],
        "pack",
        pack_record["pack_sha256"],
    ]
    receipt["checks"] = [
        readiness._dry_run_check(check_id, command, 0, reviewed["head_commit"], "")
        for check_id in (
            "real_reservation_cli_execute",
            "real_writer_entry_post",
            "real_writer_entry_pre",
            "same_head_pack_binding",
        )
    ]
    write_receipt(
        custody / pack.name / "arm_readiness.dry_run.receipts/dry-run-0001.json",
        receipt,
    )


def install_passing_evidence(pack: Path, custody: Path) -> None:
    registry, _raw = load_registry(pack.parents[2])
    lifecycle_policies = {
        item["kind"]: item
        for item in registry["freeze_evidence_lifecycle"]["evidence_policies"]
    }
    pack_sha = committed_pack_tree_sha256(pack)
    head = reviewed_main(pack)["head_commit"]
    # Derive the bound plan SHA with the same production helper the row
    # evaluator uses, so a divergence fails the test rather than hiding.
    _tree, _tree_raw = readiness._plan_tree(pack)
    bound_plan_sha = readiness._pack_identity(pack, _tree)["plan_sha256"]
    rows_by_kind: dict[str, list[dict]] = {}
    for row in registry["rows"]:
        if row["evaluation_phase"] != "ARM_ONLY" or row["row_id"] in {
            "desk.identity_pin_projection",
            "desk.under_lease_rehearsal",
        }:
            continue
        for kind in row["required_evidence_kinds"]:
            rows_by_kind.setdefault(kind, []).append(row)
    directory = custody / pack.name / "arm_readiness.evidence"
    source_directory = custody / pack.name / "sources"
    source_directory.mkdir(parents=True, exist_ok=True)
    authored_now = time.monotonic_ns()
    clock_anchor = coherent_clock_anchor()
    for index, (kind, rows) in enumerate(sorted(rows_by_kind.items()), start=1):
        horizon = lifecycle_policies[kind]["horizon_ns"]
        if not isinstance(horizon, int):
            raise AssertionError(f"ARM-only fixture kind lacks a horizon: {kind}")
        receipt = {
            "schema_version": EVIDENCE_RECEIPT_SCHEMA,
            "evidence_id": f"evidence-{index:03d}",
            "kind": kind,
            "status": "PASS",
            "issued_at_utc": "2026-08-11T00:00:00Z",
            "boot_session_id": TEST_BOOT_SESSION_ID,
            "valid_until_monotonic_ns": authored_now + horizon,
            "pack_sha256": pack_sha,
            "head_commit": head,
            "facts": [],
            "checks": [],
            "reason_codes": [],
            "assurance": copy.deepcopy(ASSURANCE),
        }
        for row in rows:
            source_relative = f"sources/{row['row_id']}.json"
            content = predicate_content(
                row["predicate_id"], plan_sha256=bound_plan_sha
            )
            if row["predicate_id"] == "clock.correct_and_prior_state.v1":
                content.update(
                    {
                        "r0_anchor_realtime_ns": clock_anchor.realtime_ns
                        - 600_000_000_000,
                        "r0_anchor_monotonic_raw_ns": clock_anchor.monotonic_raw_ns
                        - 600_000_000_000,
                        "anchor_realtime_ns": clock_anchor.realtime_ns,
                        "anchor_monotonic_raw_ns": clock_anchor.monotonic_raw_ns,
                        "anchor_read_skew_ns": clock_anchor.read_skew_ns,
                        "r1_batch_started_monotonic_raw_ns": (
                            clock_anchor.monotonic_raw_ns - 1_000
                        ),
                        "r1_batch_finished_monotonic_raw_ns": (
                            clock_anchor.monotonic_raw_ns
                        ),
                        "r1_batch_finished_monotonic_ns": authored_now,
                    }
                )
            source_raw = render_json(
                {"predicate_id": row["predicate_id"], "value": content}
            )
            (custody / pack.name / source_relative).write_bytes(source_raw)
            receipt["facts"].append(
                {
                    "fact_id": row["predicate_id"],
                    "value_type": "OBJECT",
                    "value": content,
                    "source_kind": predicate_source_kind(kind),
                    "source_path": source_relative,
                    "source_sha256": hashlib.sha256(source_raw).hexdigest(),
                }
            )
        write_receipt(directory / f"evidence-{index:03d}.json", receipt)


def clear_initial_arm(custody: Path, pack_name: str) -> None:
    namespace = custody / pack_name / "arm_readiness.receipts"
    if namespace.exists():
        shutil.rmtree(namespace)


def synthetic_identity_verifier(
    pack_root: Path | str,
    window_custody_root: Path | str,
    bracket_session_id: str,
) -> dict:
    pack = Path(pack_root)
    custody = Path(window_custody_root)
    tree = json.loads((pack / "plan_tree.json").read_text())
    unit_ids = tuple(
        unit["identity_unit_id"]
        for unit in tree["arm_attachments"]["identity_pin_projection"]["identity_units"]
    )
    receipt = sample_identity_receipt(
        kind="arm_reverification",
        pack_id=pack.name,
        identity_unit_ids=unit_ids,
    )
    receipt["pack"]["reviewed_git_commit"] = reviewed_main(pack)["head_commit"]
    path = (
        custody
        / pack.name
        / "receipts"
        / bracket_session_id
        / "identity-pin-arm-verify.json"
    )
    if path.exists():
        raise IdentityPinProjectionError(
            "readiness_identity_receipt_namespace_anomalous",
            "synthetic U11 receipt already exists",
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = render_json(receipt)
    path.write_bytes(raw)
    path.with_suffix(".sha256").write_bytes(
        gnu_sidecar(hashlib.sha256(raw).hexdigest(), path.name)
    )
    return {
        "status": "PASS",
        "reason_codes": [],
        "receipt_path": str(path),
        "receipt_sha256": hashlib.sha256(raw).hexdigest(),
        "identity_units": [unit["model_runtime_config"] for unit in receipt["identity_units"]],
    }
