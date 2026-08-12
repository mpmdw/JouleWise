from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
from joulewise.arm_readiness import (
    ASSURANCE,
    EVIDENCE_RECEIPT_SCHEMA,
    _latest_dry_run,
    _pack_record,
    generate_dry_run_receipt,
    gnu_sidecar,
    render_json,
    reviewed_main,
    validate_freeze_receipt,
    validate_dry_run_receipt,
)
from tests.test_arm_readiness_lifecycle import PACK_NAME, git, make_go_fixture
from tests.test_arm_readiness_schemas import (
    TEST_BOOT_SESSION_ID,
    predicate_content,
    predicate_source_kind,
    sample_dry_run,
)


def install_passing_freeze(repo: Path, pack: Path) -> None:
    tree_path = pack / "plan_tree.json"
    tree = json.loads(tree_path.read_text())
    registry, _registry_raw, registry_reference = readiness._registry_reference(pack)
    profile = registry_reference["plan_profile"]
    definitions = readiness._profile_rows(registry, profile, phase="freeze")
    by_kind: dict[str, list[dict]] = {}
    for row in definitions:
        if row["row_id"] == "desk.identity_pin_projection":
            continue
        for kind in row["required_evidence_kinds"]:
            by_kind.setdefault(kind, []).append(row)
    evidence_directory = pack / "arm_readiness.evidence"
    source_directory = pack / "arm_readiness.sources"
    evidence_directory.mkdir()
    source_directory.mkdir()
    for index, (kind, rows) in enumerate(sorted(by_kind.items()), start=1):
        facts = []
        for row in rows:
            source_relative = f"arm_readiness.sources/{row['row_id']}.json"
            content = predicate_content(row["predicate_id"])
            source_raw = render_json(
                {"predicate_id": row["predicate_id"], "value": content}
            )
            (pack / source_relative).write_bytes(source_raw)
            facts.append(
                {
                    "fact_id": row["predicate_id"],
                    "value_type": "OBJECT",
                    "value": content,
                    "source_kind": predicate_source_kind(kind),
                    "source_path": source_relative,
                    "source_sha256": hashlib.sha256(source_raw).hexdigest(),
                }
            )
        evidence = {
            "schema_version": EVIDENCE_RECEIPT_SCHEMA,
            "evidence_id": f"freeze-evidence-{index:03d}",
            "kind": kind,
            "status": "PASS",
            "issued_at_utc": "2026-08-11T00:00:00Z",
            "boot_session_id": TEST_BOOT_SESSION_ID,
            "valid_until_monotonic_ns": 10**30,
            "pack_sha256": "0" * 64,
            "head_commit": "a" * 40,
            "facts": facts,
            "checks": [],
            "reason_codes": [],
            "assurance": copy.deepcopy(ASSURANCE),
        }
        raw = render_json(evidence)
        path = evidence_directory / f"evidence-{index:03d}.json"
        path.write_bytes(raw)
        path.with_name(f"{path.name}.sha256").write_bytes(
            gnu_sidecar(hashlib.sha256(raw).hexdigest(), path.name)
        )
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "freeze evidence")

    evidence_items, evidence_receipts, evidence_refusals = readiness._discover_evidence(
        pack,
        pack,
        pack_sha256=None,
        head_commit=None,
        boot_session_id=TEST_BOOT_SESSION_ID,
        now_monotonic_ns=None,
    )
    self_identity_item, self_identity_receipt, identity_reasons = (
        readiness._load_frozen_identity_evidence(pack, tree)
    )
    if self_identity_item is not None and self_identity_receipt is not None:
        evidence_items.append(self_identity_item)
        evidence_items.sort(key=lambda item: item["evidence_id"])
        evidence_receipts[self_identity_item["evidence_id"]] = self_identity_receipt
    rows, row_refusals = readiness._evaluate_rows(
        definitions,
        evidence_receipts,
        clock_route="MANUAL",
        successor_acceptance=False,
        forced_reason_codes={"desk.identity_pin_projection": identity_reasons},
    )
    refusals = evidence_refusals + row_refusals
    if refusals:
        raise AssertionError(refusals)
    receipt = {
        "schema_version": readiness.FREEZE_RECEIPT_SCHEMA,
        "receipt_kind": "freeze",
        "receipt_id": "freeze-0001",
        "status": "PASS",
        "arm_disposition": "NOT_APPLICABLE",
        "issued_at_utc": "2026-08-11T00:00:00Z",
        "pack_identity": readiness._pack_identity(pack, tree),
        "row_registry": registry_reference,
        "evidence": evidence_items,
        "rows": rows,
        "refusals": [],
        "supersedes": None,
        "assurance": copy.deepcopy(ASSURANCE),
    }
    validate_freeze_receipt(receipt)
    raw = render_json(receipt)
    digest = hashlib.sha256(raw).hexdigest()
    namespace = pack / "arm_readiness.freeze.receipts"
    namespace.mkdir()
    (namespace / "freeze-0001.json").write_bytes(raw)
    (namespace / "freeze-0001.json.sha256").write_bytes(
        gnu_sidecar(digest, "freeze-0001.json")
    )
    tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] = {
        "path": "arm_readiness.freeze.receipts/freeze-0001.json",
        "sha256": digest,
    }
    tree_raw = render_json(tree)
    tree_path.write_bytes(tree_raw)
    (pack / "plan_tree.sha256").write_bytes(
        gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
    )
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "passing freeze")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")


class ArmReadinessDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = mock.patch.object(
            readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_dry_run_schema_can_never_authorize(self) -> None:
        receipt = sample_dry_run()
        validate_dry_run_receipt(receipt)
        self.assertEqual(receipt["arm_disposition"], "NOT_APPLICABLE")
        receipt["arm_disposition"] = "GO"
        with self.assertRaises(ValueError):
            validate_dry_run_receipt(receipt)

    def test_real_under_lease_rehearsal_uses_reservation_and_both_writer_slots(self) -> None:
        temporary, repo, pack, custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        install_passing_freeze(repo, pack)
        synthetic = Path(temporary.name) / "synthetic"
        before = {
            path.relative_to(pack).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in pack.rglob("*")
            if path.is_file()
        }
        result = generate_dry_run_receipt(
            pack,
            custody,
            "rehearsal-1",
            synthetic,
        )
        after = {
            path.relative_to(pack).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in pack.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)
        receipt = json.loads(Path(result["receipt_path"]).read_text())
        checks = {check["check_id"]: check for check in receipt["checks"]}
        self.assertEqual(checks["real_reservation_cli_execute"]["status"], "PASS", receipt)
        self.assertEqual(checks["real_writer_entry_pre"]["status"], "PASS", receipt)
        self.assertEqual(checks["real_writer_entry_post"]["status"], "PASS", receipt)
        self.assertEqual(checks["same_head_pack_binding"]["status"], "PASS", receipt)
        self.assertEqual(receipt["arm_disposition"], "NOT_APPLICABLE")
        self.assertEqual(result["status"], "PASS")
        ledger_rows = [
            json.loads(line)
            for line in (synthetic / "calibration_observation_ledger.jsonl")
            .read_text()
            .splitlines()
        ]
        core_rows = [row for row in ledger_rows if row["event"] != "append-intent"]
        self.assertEqual(
            [(row["event"], row.get("slot"), row.get("attempt_id")) for row in core_rows],
            [
                ("bracket-session-open", None, None),
                ("bracket-session-slot-claim", "pre", "dry-rehearsal-1-pre"),
                ("bracket-session-slot-finalization", "pre", "dry-rehearsal-1-pre"),
                ("bracket-session-slot-claim", "post", "dry-rehearsal-1-post"),
                ("bracket-session-slot-finalization", "post", "dry-rehearsal-1-post"),
            ],
        )

    def test_dry_run_becomes_stale_after_later_head_even_when_pack_bytes_do_not_change(self) -> None:
        temporary, repo, pack, custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        install_passing_freeze(repo, pack)
        result = generate_dry_run_receipt(
            pack,
            custody,
            "rehearsal-stale",
            Path(temporary.name) / "synthetic-stale",
        )
        self.assertEqual(result["status"], "PASS")
        (repo / "outside-pack.txt").write_text("later head\n")
        git(repo, "add", "outside-pack.txt")
        git(repo, "commit", "-qm", "later head")
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        receipt, code = _latest_dry_run(
            custody / PACK_NAME,
            _pack_record(pack),
            reviewed_main(pack),
        )
        self.assertIsNotNone(receipt)
        self.assertEqual(code, "readiness_dry_run_stale")

    def test_dry_run_refuses_a_dirty_or_nonreviewed_checkout(self) -> None:
        temporary, repo, pack, custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        install_passing_freeze(repo, pack)
        (repo / "untracked-review-change.txt").write_text("dirty\n")
        result = generate_dry_run_receipt(
            pack,
            custody,
            "rehearsal-dirty",
            Path(temporary.name) / "synthetic-dirty",
        )
        self.assertEqual(result["status"], "REFUSE")
        self.assertIn("readiness_git_tree_dirty", result["reason_codes"])
        receipt = json.loads(Path(result["receipt_path"]).read_text())
        binding = next(
            check
            for check in receipt["checks"]
            if check["check_id"] == "same_head_pack_binding"
        )
        self.assertEqual(binding["status"], "REFUSE")

    def test_dry_run_rehearsal_root_and_id_are_single_use(self) -> None:
        temporary, repo, pack, custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        install_passing_freeze(repo, pack)
        synthetic = Path(temporary.name) / "synthetic-single-use"
        result = generate_dry_run_receipt(
            pack,
            custody,
            "rehearsal-single-use",
            synthetic,
        )
        self.assertEqual(result["status"], "PASS")
        with self.assertRaisesRegex(readiness.ArmReadinessError, "already used"):
            generate_dry_run_receipt(
                pack,
                custody,
                "rehearsal-single-use",
                Path(temporary.name) / "other-synthetic-root",
            )
        with self.assertRaisesRegex(readiness.ArmReadinessError, "already exists"):
            generate_dry_run_receipt(
                pack,
                custody,
                "second-rehearsal",
                synthetic,
            )


if __name__ == "__main__":
    unittest.main()
