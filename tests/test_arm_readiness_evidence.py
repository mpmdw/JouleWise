from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import joulewise.arm_readiness as readiness
import joulewise.arm_readiness_evidence as evidence
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID, sample_evidence


ROOT = Path(__file__).resolve().parents[1]


def git(repository: Path, *args: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(repository), *args),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def lifecycle_registry(
    *,
    allowlist: tuple[str, ...] = (),
    policies: tuple[dict, ...] | None = None,
) -> dict:
    if policies is None:
        policies = (
            {
                "kind": "DOCTRINE_PIN",
                "freshness_class": "RE_DERIVABLE",
                "freshness_policy_id": "test.doctrine.rederive.v1",
                "horizon_ns": None,
                "environment_comparison": "NOT_APPLICABLE",
            },
        )
    policy_ids = [item["freshness_policy_id"] for item in policies]
    return {
        "schema_version": readiness.R1_LIFECYCLE_REGISTRY_SCHEMA,
        "registry_id": "test-r1-lifecycle-v1",
        "irrelevant_path_allowlist": sorted(allowlist),
        "evidence_policies": sorted(
            (copy.deepcopy(item) for item in policies), key=lambda item: item["kind"]
        ),
        "row_policies": [
            {
                "row_id": f"test.row.{index:02d}",
                "freshness_policy_id": policy_id,
            }
            for index, policy_id in enumerate(policy_ids)
        ],
        "arm_policy": {
            "capability_horizon_ns": 300_000_000_000,
            "arm_to_consume_budget_ns": 60_000_000_000,
        },
        "successor_policy": {
            "successor_pack_ids": ["test-alpha-v2", "test-beta-v2", "test-gamma-v2"],
            "cross_chain_numbering": "test.freeze-0002.v1",
            "freeze_receipt_v2_predecessor_bindings": [
                "evidence_set_root",
                "freeze_receipt",
                "identity_receipt",
                "pack_digest",
                "pack_id",
            ],
            "family_publication_marker_schema": "test.family-marker.v1",
        },
        "refusal_vocabulary": [
            {
                "role": role,
                "code": f"test_r1_{role.lower()}",
                "type": "POLICY",
            }
            for role in sorted(readiness.R1_REFUSAL_ROLES)
        ],
    }


def plan_tree(*, frozen: bool, marker: str = "stable") -> bytes:
    return readiness.render_json(
        {
            "arm_attachments": {
                "arm_readiness": {
                    "contract_id": "D-134",
                    "freeze_receipt": (
                        {
                            "path": "arm_readiness.freeze.receipts/freeze-0002.json",
                            "sha256": "a" * 64,
                        }
                        if frozen
                        else None
                    ),
                    "marker": marker,
                }
            }
        }
    )


def content_source_and_receipt(
    repository: Path, derivation_commit: str, dependency: str = "dependency.txt"
) -> tuple[dict, dict]:
    dependency_raw = (repository / dependency).read_bytes()
    source = {
        "schema_version": evidence._R1_SOURCE_SCHEMA,
        "kind": "DOCTRINE_PIN",
        "head_commit": derivation_commit,
        "derivation_commit": derivation_commit,
        "pack_sha256": "b" * 64,
        "freshness_class": "RE_DERIVABLE",
        "freshness_policy_id": "test.doctrine.rederive.v1",
        "environment_fingerprint": None,
        "primary_artifacts": [
            {
                "path": dependency,
                "sha256": hashlib.sha256(dependency_raw).hexdigest(),
            }
        ],
        "checks": [],
        "facts": [{"fact_id": "test.fact", "value": {"passes": True}}],
        "derivation": {"test": True},
    }
    source_digest = hashlib.sha256(readiness.render_json(source)).hexdigest()
    receipt = {
        "schema_version": readiness.CONTENT_EVIDENCE_RECEIPT_SCHEMA,
        "evidence_id": "freeze-doctrine-pin-v1",
        "kind": "DOCTRINE_PIN",
        "status": "PASS",
        "issued_at_utc": "2026-08-17T00:00:00Z",
        "freshness_class": "RE_DERIVABLE",
        "freshness_policy_id": "test.doctrine.rederive.v1",
        "pack_sha256": "b" * 64,
        "derivation_commit": derivation_commit,
        "dependency_manifest_sha256": source_digest,
        "facts": [
            {
                "fact_id": "test.fact",
                "value_type": "OBJECT",
                "value": {"passes": True},
                "source_kind": "PACK",
                "source_path": "arm_readiness.sources/doctrine-pin.json",
                "source_sha256": source_digest,
            }
        ],
        "checks": [],
        "reason_codes": [],
        "assurance": copy.deepcopy(readiness.ASSURANCE),
    }
    readiness.validate_evidence_receipt(receipt)
    return source, receipt


class R1EvidenceLifecycleTests(unittest.TestCase):
    def make_repository(self) -> tuple[tempfile.TemporaryDirectory, Path, str]:
        temporary = tempfile.TemporaryDirectory()
        repository = Path(temporary.name)
        git(repository, "init", "-q")
        git(repository, "config", "user.email", "test@example.invalid")
        git(repository, "config", "user.name", "R1 Test")
        (repository / "dependency.txt").write_text("stable\n")
        (repository / "notes.txt").write_text("first\n")
        (repository / "pack").mkdir()
        (repository / "pack/plan_tree.json").write_bytes(plan_tree(frozen=False))
        git(repository, "add", ".")
        git(repository, "commit", "-qm", "derivation")
        return temporary, repository, git(repository, "rev-parse", "HEAD")

    def test_taxonomy_is_code_constant_and_registry_mismatch_refuses(self) -> None:
        self.assertEqual(
            {
                kind
                for kind, freshness_class in evidence._DERIVER_FRESHNESS_CLASSES.items()
                if freshness_class == "RE_DERIVABLE"
            },
            {"DOCTRINE_PIN", "PACK_FAMILY"},
        )
        self.assertEqual(
            set(evidence._DERIVER_FRESHNESS_CLASSES), set(evidence._DERIVERS)
        )
        mismatch = lifecycle_registry(
            policies=(
                {
                    "kind": "DOCTRINE_PIN",
                    "freshness_class": "EXECUTION_BOUND",
                    "freshness_policy_id": "test.doctrine.wrong.v1",
                    "horizon_ns": 1,
                    "environment_comparison": "test-only",
                },
            )
        )
        with self.assertRaises(evidence.EvidenceAuthoringError) as caught:
            evidence._r1_policies_for_kinds(mismatch, ["DOCTRINE_PIN"])
        self.assertEqual(caught.exception.reason_code, "test_r1_class_mismatch")

    def test_content_schema_has_no_boot_or_deadline_keys(self) -> None:
        temporary, repository, head = self.make_repository()
        self.addCleanup(temporary.cleanup)
        _source, receipt = content_source_and_receipt(repository, head)
        self.assertNotIn("boot_session_id", receipt)
        self.assertNotIn("valid_until_monotonic_ns", receipt)
        for key, value in (
            ("boot_session_id", TEST_BOOT_SESSION_ID),
            ("valid_until_monotonic_ns", 10**30),
        ):
            mutated = copy.deepcopy(receipt)
            mutated[key] = value
            with self.subTest(key=key), self.assertRaises(
                readiness.ArmReadinessError
            ) as caught:
                readiness.validate_evidence_receipt(mutated)
            self.assertEqual(caught.exception.reason_code, "readiness_unknown_key")

    def test_changed_set_primary_gate_and_manifest_conjunct_discriminate(self) -> None:
        temporary, repository, derivation = self.make_repository()
        self.addCleanup(temporary.cleanup)
        source, receipt = content_source_and_receipt(repository, derivation)
        (repository / "notes.txt").write_text("second\n")
        git(repository, "add", "notes.txt")
        git(repository, "commit", "-qm", "irrelevant")
        head = git(repository, "rev-parse", "HEAD")

        changed = readiness.validate_r1_evidence_lifecycle(
            repository,
            receipt,
            source,
            lifecycle_registry(allowlist=("notes.txt",)),
            current_head=head,
            expected_freshness_class="RE_DERIVABLE",
            plan_tree_path="pack/plan_tree.json",
        )
        self.assertEqual(changed, ("notes.txt",))
        with self.assertRaises(readiness.EvidenceLifecycleError) as relevant:
            readiness.validate_r1_evidence_lifecycle(
                repository,
                receipt,
                source,
                lifecycle_registry(),
                current_head=head,
                expected_freshness_class="RE_DERIVABLE",
                plan_tree_path="pack/plan_tree.json",
            )
        self.assertEqual(relevant.exception.role, "DEPENDENCY_CHANGED_SET")

        (repository / "dependency.txt").write_text("changed\n")
        git(repository, "add", "dependency.txt")
        git(repository, "commit", "-qm", "dependency change")
        changed_head = git(repository, "rev-parse", "HEAD")
        with self.assertRaises(readiness.EvidenceLifecycleError) as manifest:
            readiness.validate_r1_evidence_lifecycle(
                repository,
                receipt,
                source,
                lifecycle_registry(
                    allowlist=("dependency.txt", "notes.txt")
                ),
                current_head=changed_head,
                expected_freshness_class="RE_DERIVABLE",
                plan_tree_path="pack/plan_tree.json",
            )
        self.assertEqual(manifest.exception.role, "DEPENDENCY_MANIFEST")

    def test_plan_tree_normalization_subtracts_only_freeze_slot(self) -> None:
        before = plan_tree(frozen=False)
        after = plan_tree(frozen=True)
        self.assertEqual(
            readiness.normalize_plan_tree_for_freeze_evidence(before),
            readiness.normalize_plan_tree_for_freeze_evidence(after),
        )
        changed_elsewhere = plan_tree(frozen=True, marker="changed")
        self.assertNotEqual(
            readiness.normalize_plan_tree_for_freeze_evidence(before),
            readiness.normalize_plan_tree_for_freeze_evidence(changed_elsewhere),
        )
        injected = json.loads(after)
        injected["arm_attachments"]["arm_readiness"]["freeze_receipt"][
            "extra"
        ] = True
        with self.assertRaises(readiness.ArmReadinessError):
            readiness.normalize_plan_tree_for_freeze_evidence(
                readiness.render_json(injected)
            )

        temporary, repository, derivation = self.make_repository()
        self.addCleanup(temporary.cleanup)
        source, receipt = content_source_and_receipt(
            repository, derivation, dependency="pack/plan_tree.json"
        )
        (repository / "pack/plan_tree.json").write_bytes(plan_tree(frozen=True))
        git(repository, "add", "pack/plan_tree.json")
        git(repository, "commit", "-qm", "fill freeze slot")
        frozen_head = git(repository, "rev-parse", "HEAD")
        readiness.validate_r1_evidence_lifecycle(
            repository,
            receipt,
            source,
            lifecycle_registry(allowlist=("pack/plan_tree.json",)),
            current_head=frozen_head,
            expected_freshness_class="RE_DERIVABLE",
            plan_tree_path="pack/plan_tree.json",
        )
        (repository / "pack/plan_tree.json").write_bytes(
            plan_tree(frozen=True, marker="one-byte-elsewhere")
        )
        git(repository, "add", "pack/plan_tree.json")
        git(repository, "commit", "-qm", "change other plan field")
        with self.assertRaises(readiness.EvidenceLifecycleError) as changed:
            readiness.validate_r1_evidence_lifecycle(
                repository,
                receipt,
                source,
                lifecycle_registry(allowlist=("pack/plan_tree.json",)),
                current_head=git(repository, "rev-parse", "HEAD"),
                expected_freshness_class="RE_DERIVABLE",
                plan_tree_path="pack/plan_tree.json",
            )
        self.assertEqual(changed.exception.role, "DEPENDENCY_MANIFEST")

    def test_allowlist_tampering_refuses_before_policy_use(self) -> None:
        raw = readiness.render_json(lifecycle_registry(allowlist=("notes.txt",)))
        digest = hashlib.sha256(raw).hexdigest()
        readiness.authenticate_r1_lifecycle_registry(raw, digest)
        tampered = raw.replace(b"notes.txt", b"other.txt")
        with self.assertRaises(readiness.ArmReadinessError) as caught:
            readiness.authenticate_r1_lifecycle_registry(tampered, digest)
        self.assertEqual(caught.exception.reason_code, "readiness_row_registry_mismatch")

    def test_reserved_registry_and_environment_semantics_refuse_issuance(self) -> None:
        self.assertEqual(
            evidence._ENVIRONMENT_FINGERPRINT_KINDS,
            {
                "MINT_TRUST",
                "MULTICELL_MINT",
                "PACK_AUTHENTICATION",
                "REASON_CODE_COVERAGE",
                "RECOVERY_LEDGER_TEST",
                "THREE_WINDOW_REGRESSION",
            },
        )
        readiness.validate_r1_lifecycle_registry(
            readiness.R1_LIFECYCLE_REGISTRY_PLACEHOLDER,
            require_resolved=False,
        )
        with self.assertRaises(readiness.ArmReadinessError):
            readiness.validate_r1_lifecycle_registry(
                readiness.R1_LIFECYCLE_REGISTRY_PLACEHOLDER
            )
        execution = lifecycle_registry(
            policies=(
                {
                    "kind": "PACK_AUTHENTICATION",
                    "freshness_class": "EXECUTION_BOUND",
                    "freshness_policy_id": "test.execution.pending.v1",
                    "horizon_ns": 100,
                    "environment_comparison": "ED_RESERVED:comparison",
                },
            )
        )
        with self.assertRaises(readiness.ArmReadinessError):
            readiness.validate_r1_lifecycle_registry(execution)
        execution["evidence_policies"][0]["environment_comparison"] = "test-only"
        readiness.validate_r1_lifecycle_registry(execution)
        with self.assertRaises(evidence.EvidenceAuthoringError) as caught:
            evidence._r1_policies_for_kinds(
                execution, ["PACK_AUTHENTICATION"]
            )
        self.assertEqual(
            caught.exception.reason_code,
            "test_r1_unknown_policy",
        )

    def test_v1_receipt_is_never_grandfathered_and_fixture_bytes_are_neutral(self) -> None:
        pack_names = (
            "d117_floor_qwen25_1p5b_v1",
            "d117_floor_qwen25_7b_v1",
            "d117_contrast_qwen25_1p5b_vs_7b_v1",
        )
        paths = sorted(
            path
            for pack_name in pack_names
            for path in (ROOT / "configs/campaigns" / pack_name).glob(
                "arm_readiness.evidence/evidence-*.json*"
            )
        )
        before_all = {path: path.read_bytes() for path in paths}
        receipt_path = (
            ROOT
            / "configs/campaigns/d117_floor_qwen25_1p5b_v1"
            / "arm_readiness.evidence/evidence-doctrine-pin.json"
        )
        before = before_all[receipt_path]
        legacy = readiness.validate_evidence_receipt(
            readiness.parse_json_bytes(before, require_canonical=True)
        )
        with self.assertRaises(readiness.EvidenceLifecycleError) as caught:
            readiness.validate_r1_evidence_lifecycle(
                ROOT,
                legacy,
                {},
                lifecycle_registry(),
                current_head=git(ROOT, "rev-parse", "HEAD"),
                expected_freshness_class="RE_DERIVABLE",
                plan_tree_path=(
                    "configs/campaigns/d117_floor_qwen25_1p5b_v1/plan_tree.json"
                ),
            )
        self.assertEqual(caught.exception.role, "V1_GRANDFATHERING")
        self.assertEqual(caught.exception.reason_code, "test_r1_v1_grandfathering")
        self.assertEqual({path: path.read_bytes() for path in paths}, before_all)

    def test_deriver_read_routing_guard_detects_a_direct_read_mutation(self) -> None:
        self.assertEqual(evidence._unrouted_deriver_reads(), ())
        source = Path(evidence.__file__).read_text(encoding="utf-8")
        source += (
            "\ndef _derive_direct_read_probe(context):\n"
            "    return (context.pack_root / 'probe').read_bytes()\n"
        )
        findings = evidence._unrouted_deriver_reads(source)
        self.assertTrue(any(item.endswith(":read_bytes") for item in findings))


if __name__ == "__main__":
    unittest.main()
