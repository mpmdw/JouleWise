from __future__ import annotations
from tests import evidence_factory
from tests import receipt_factory

import copy
import hashlib
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import joulewise.receipt_readers as readiness
import joulewise.evidence_replay as evidence_author
from joulewise.receipt_readers import ASSURANCE, _latest_dry_run, _pack_record, committed_pack_tree_sha256, gnu_sidecar, render_json, reviewed_main, validate_freeze_receipt, validate_dry_run_receipt; from tests.receipt_factory import generate_dry_run_receipt
from tests.test_arm_readiness_lifecycle import (
    PACK_NAME,
    git,
    make_go_fixture,
    predecessor_pack_root,
)
from tests.test_arm_readiness_schemas import (
    TEST_BOOT_SESSION_ID,
    predicate_content,
    sample_dry_run,
)


def install_passing_freeze(
    repo: Path, pack: Path, *, mint_receipt: bool = True
) -> None:
    repo = repo.resolve(strict=True)
    pack = pack.resolve(strict=True)
    tree_path = pack / "plan_tree.json"
    tree = json.loads(tree_path.read_text())

    # The two RE_DERIVABLE evidence classes are replayed from committed
    # dependencies at freeze and again at arm.  Give the synthetic repository
    # the same dependency surface as production so the fixture exercises that
    # authentication instead of bypassing it with hand-written facts.
    for relative in (
        "joulewise/arm_readiness_evidence.py",
        "scripts/author_arm_readiness_evidence.py",
        "docs/phase_2/window_runbook.md",
        "docs/decision_log.md",
    ):
        source = Path(__file__).resolve().parents[1] / relative
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        body = _historical_fixture_source(relative)
        target.write_bytes(body)
    for family_pack in evidence_author._PACKS_BY_PROFILE.values():
        relative = f"configs/campaigns/{family_pack}/plan_tree.json"
        source = Path(__file__).resolve().parents[1] / relative
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    tree["arm_attachments"]["launch"] = {
        "schema_version": "joulewise.fixture_launch.v1"
    }
    existing_stages = tree.get("stage_graph")
    tree["stage_graph"] = (
        list(existing_stages) if isinstance(existing_stages, list) else []
    ) + [
        {
            "stage_id": "fixture-verdict",
            "kind": "whole_window_verdict",
            "launch": {"commands": []},
        },
        {
            "stage_id": "fixture-backup",
            "kind": "backup",
            "launch": {
                "commands": [
                    {"command_kind": "backup", "command_id": "backup.claim"},
                    {"command_kind": "backup", "command_id": "backup.bound"},
                ]
            },
        },
    ]
    tree["closeout_attachments"] = {
        "backup_requirements": {"required_successful_backups": 2}
    }
    tree_raw = render_json(tree)
    tree_path.write_bytes(tree_raw)
    (pack / "plan_tree.sha256").write_bytes(
        gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
    )
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "R1 fixture authoring dependencies")

    registry, _registry_raw, registry_reference = readiness._registry_reference(pack)
    lifecycle = registry["freeze_evidence_lifecycle"]
    profile = registry_reference["plan_profile"]
    definitions = readiness._profile_rows(registry, profile, phase="freeze")
    applicable_definitions = [
        row
        for row in definitions
        if readiness.applicability_for_row(
            row,
            clock_route="MANUAL",
            successor_acceptance=not readiness._issued_d079(tree),
        )
        == "REQUIRED"
    ]
    by_kind: dict[str, list[dict]] = {}
    for row in applicable_definitions:
        if row["row_id"] == "desk.identity_pin_projection":
            continue
        for kind in row["required_evidence_kinds"]:
            by_kind.setdefault(kind, []).append(row)
    evidence_directory = pack / "arm_readiness.evidence"
    source_directory = pack / "arm_readiness.sources"
    derivation_commit = reviewed_main(pack)["head_commit"]
    pack_sha = committed_pack_tree_sha256(pack)
    evidence_directory.mkdir()
    source_directory.mkdir()
    context = evidence_author._DerivationContext(
        pack_root=pack,
        repository=repo,
        tree=tree,
        pack_sha256=pack_sha,
        head_commit=derivation_commit,
    )
    policies = {
        item["kind"]: item for item in lifecycle["evidence_policies"]
    }
    plan_relative = (pack / "calibration_plan.json").relative_to(repo).as_posix()
    plan_artifact = {
        "path": plan_relative,
        "sha256": hashlib.sha256((pack / "calibration_plan.json").read_bytes()).hexdigest(),
    }
    # Freeze replay uses the host clock, so evidence must age from authoring,
    # not from boot. Sample once for every caller, including real-clock CLI tests.
    authored_at_monotonic_ns = time.monotonic_ns()
    for kind, rows in sorted(by_kind.items()):
        facts = {}
        for row in rows:
            content = predicate_content(row["predicate_id"])
            facts[row["predicate_id"]] = content
        derived = (
            evidence_author._DERIVERS[kind](context)
            if kind in {"DOCTRINE_PIN", "PACK_FAMILY"}
            else evidence_author._DerivedKind(
                kind,
                facts,
                (plan_artifact,),
                (),
                {"fixture": "registry-shaped synthetic evidence"},
            )
        )
        policy = policies[kind]
        environment = (
            {"schema_version": "joulewise.fixture_environment.v1"}
            if policy["freshness_class"] == "EXECUTION_BOUND"
            else None
        )
        source_raw = evidence_author._r1_fact_source(
            context, derived, policy, environment
        )
        source_path = pack / evidence_author._source_path(kind)
        source_path.write_bytes(source_raw)
        evidence = evidence_author._assemble_r1_receipt(
            context,
            derived,
            source_raw,
            policy,
            issued_at_utc="2026-08-11T00:00:00Z",
            boot_session_id=TEST_BOOT_SESSION_ID,
            now_monotonic_ns=authored_at_monotonic_ns,
            environment_fingerprint=environment,
        )
        raw = render_json(evidence)
        path = evidence_directory / evidence_author._receipt_name(kind)
        path.write_bytes(raw)
        path.with_name(f"{path.name}.sha256").write_bytes(
            gnu_sidecar(hashlib.sha256(raw).hexdigest(), path.name)
        )
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "freeze evidence")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    if not mint_receipt:
        return

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
    predecessor = predecessor_pack_root(repo, pack.name)
    predecessor_tree = json.loads((predecessor / "plan_tree.json").read_text())
    predecessor_reference = predecessor_tree["arm_attachments"]["arm_readiness"][
        "freeze_receipt"
    ]
    predecessor_receipt = json.loads(
        (predecessor / predecessor_reference["path"]).read_text()
    )
    freeze_number = (
        readiness._freeze_receipt_ordinal(
            predecessor_receipt["receipt_id"], "fixture predecessor receipt_id"
        )
        + 1
    )
    freeze_id = f"freeze-{freeze_number:04d}"
    freeze_name = f"{freeze_id}.json"
    receipt = {
        "schema_version": readiness.FREEZE_RECEIPT_SCHEMA,
        "receipt_kind": "freeze",
        "receipt_id": freeze_id,
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
    (namespace / freeze_name).write_bytes(raw)
    (namespace / f"{freeze_name}.sha256").write_bytes(
        gnu_sidecar(digest, freeze_name)
    )
    tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] = {
        "path": f"arm_readiness.freeze.receipts/{freeze_name}",
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


class FreezeFixtureClockOriginTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary, repo, self.pack, _custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        registry, _raw, _reference = readiness._registry_reference(self.pack)
        self.lifecycle = registry["freeze_evidence_lifecycle"]
        # ONE home for the horizon: the registry's evidence policy for the
        # kind this test authenticates (a retuned registry retunes the test).
        self.horizon_ns = next(
            policy["horizon_ns"]
            for policy in self.lifecycle["evidence_policies"]
            if policy["kind"] == "ACCEPTANCE_OWNER"
        )
        # Reproduce a host awake longer than the evidence horizon (by 1/14).
        self.origin = 1 + self.horizon_ns + self.horizon_ns // 14
        with mock.patch.object(time, "monotonic_ns", return_value=self.origin):
            install_passing_freeze(repo, self.pack, mint_receipt=False)
        path = self.pack / "arm_readiness.evidence/evidence-acceptance-owner.json"
        raw = path.read_bytes()
        self.receipt = json.loads(raw)
        self.item = {
            "evidence_id": self.receipt["evidence_id"],
            "receipt_kind": self.receipt["kind"],
            "namespace": "PACK",
            "path": path.relative_to(self.pack).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "schema_version": self.receipt["schema_version"],
            "status": self.receipt["status"],
        }

    def test_fresh_evidence_authenticates_after_seven_days_host_uptime(self) -> None:
        with mock.patch.object(
            time, "monotonic_ns", return_value=self.origin + 1_000_000_000
        ):
            authenticated = readiness._authenticate_generic_evidence_item(
                self.item,
                self.pack,
                self.pack,
                expected_boot_session_id=TEST_BOOT_SESSION_ID,
                lifecycle_registry=self.lifecycle,
            )
        self.assertEqual(authenticated["status"], "PASS")
        self.assertEqual(authenticated, self.receipt)

    def test_evidence_still_expires_eight_days_after_authoring(self) -> None:
        with mock.patch.object(
            time, "monotonic_ns", return_value=self.origin + self.horizon_ns + 1_000_000_000
        ):
            with self.assertRaises(readiness.ArmReadinessError) as caught:
                readiness._authenticate_generic_evidence_item(
                    self.item,
                    self.pack,
                    self.pack,
                    expected_boot_session_id=TEST_BOOT_SESSION_ID,
                    lifecycle_registry=self.lifecycle,
                )
        self.assertEqual(caught.exception.reason_code, "readiness_record_expired")
        self.assertIn("evidence item expired", str(caught.exception))


class ArmReadinessDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = mock.patch.object(
            readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        )
        patcher.start()
        self.addCleanup(patcher.stop)












if __name__ == "__main__":
    unittest.main()


def _historical_fixture_source(relative):
    root = Path(__file__).resolve().parents[1]
    source = root / relative
    if source.is_file():
        return source.read_bytes()
    if not str(relative).endswith((".py", ".sh")):
        raise FileNotFoundError(source)
    return subprocess.check_output(["git", "-C", str(root), "show", "92026c184:" + str(relative)])
