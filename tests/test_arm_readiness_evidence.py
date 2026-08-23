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
            "successor_pack_ids": {
                "ALPHA": "d117_floor_qwen25_1p5b_v2",
                "BETA": "d117_floor_qwen25_7b_v2",
                "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v2",
            },
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


def resolved_r1_row_registry() -> dict:
    registry = json.loads(
        (ROOT / readiness.ROW_REGISTRY_RELATIVE_PATH).read_text(encoding="utf-8")
    )
    registry["schema_version"] = readiness.R1_ROW_REGISTRY_SCHEMA
    registry["registry_id"] = "test-r1-row-registry-v2"
    # The registry-LOAD closure check admits only refusal codes the production
    # vocabulary registers, so this synthetic registry carries the real
    # vocabulary rather than lifecycle_registry()'s test_r1_* placeholders.
    production_vocabulary = copy.deepcopy(
        registry["freeze_evidence_lifecycle"]["refusal_vocabulary"]
    )
    policies = []
    for kind, freshness_class in sorted(
        readiness.R1_EVIDENCE_FRESHNESS_CLASSES.items()
    ):
        if kind == "ARM_CAPABILITY":
            continue
        policies.append(
            {
                "kind": kind,
                "freshness_class": freshness_class,
                "freshness_policy_id": f"test.{freshness_class.lower()}.v1",
                "horizon_ns": (
                    None if freshness_class == "RE_DERIVABLE" else 1_200_000_000_000
                ),
                "environment_comparison": (
                    "test-only"
                    if freshness_class == "EXECUTION_BOUND"
                    else "NOT_APPLICABLE"
                ),
            }
        )
    policy_by_kind = {
        item["kind"]: item["freshness_policy_id"] for item in policies
    }
    registry["freeze_evidence_lifecycle"] = lifecycle_registry(
        policies=tuple(policies)
    )
    registry["freeze_evidence_lifecycle"]["row_policies"] = [
        {
            "row_id": row["row_id"],
            "freshness_policy_id": policy_by_kind[
                row["required_evidence_kinds"][0]
            ],
        }
        for row in registry["rows"]
    ]
    registry["freeze_evidence_lifecycle"]["refusal_vocabulary"] = production_vocabulary
    return registry


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
            set(readiness.R1_EVIDENCE_FRESHNESS_CLASSES) - {"ARM_CAPABILITY"},
            set(readiness._EVIDENCE_SOURCE_KINDS),
        )
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

        clock_override = lifecycle_registry(
            policies=(
                {
                    "kind": "CLOCK_PROBE",
                    "freshness_class": "EXECUTION_BOUND",
                    "freshness_policy_id": "test.clock.wrong.v1",
                    "horizon_ns": 1,
                    "environment_comparison": "ED_RESERVED:comparison",
                },
            )
        )
        with self.assertRaises(readiness.ArmReadinessError) as clock_mismatch:
            readiness.validate_r1_lifecycle_registry(clock_override)
        self.assertEqual(
            clock_mismatch.exception.reason_code, "readiness_row_registry_mismatch"
        )
        self.assertIn("CLASS_MISMATCH", str(clock_mismatch.exception))

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
        non_slot_whitespace_a = (
            b'{"arm_attachments":{"arm_readiness":{"freeze_receipt":null}},"x":1}'
        )
        non_slot_whitespace_b = (
            b'{"arm_attachments": {"arm_readiness":{"freeze_receipt":null}},"x":1}'
        )
        self.assertNotEqual(
            readiness.normalize_plan_tree_for_freeze_evidence(non_slot_whitespace_a),
            readiness.normalize_plan_tree_for_freeze_evidence(non_slot_whitespace_b),
        )
        self.assertEqual(
            readiness.normalize_plan_tree_for_freeze_evidence(
                non_slot_whitespace_a
            ),
            non_slot_whitespace_a,
        )
        slot_start, slot_end = readiness._json_member_value_span(
            after.decode("utf-8"),
            ("arm_attachments", "arm_readiness", "freeze_receipt"),
        )
        normalized_after = readiness.normalize_plan_tree_for_freeze_evidence(after)
        self.assertEqual(normalized_after[slot_start : slot_start + 4], b"null")
        self.assertEqual(
            hashlib.sha256(
                after[:slot_start] + after[slot_end:]
            ).hexdigest(),
            hashlib.sha256(
                normalized_after[:slot_start] + normalized_after[slot_start + 4 :]
            ).hexdigest(),
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

    def test_reserved_and_unimplemented_environment_policies_refuse_authoring(self) -> None:
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

    def test_contradictory_resolved_policy_fields_refuse(self) -> None:
        contradictory = lifecycle_registry()
        contradictory["evidence_policies"][0]["horizon_ns"] = 123
        contradictory["evidence_policies"][0]["environment_comparison"] = (
            "contradictory-but-resolved"
        )
        with self.assertRaises(readiness.ArmReadinessError) as caught:
            readiness.validate_r1_lifecycle_registry(contradictory)
        self.assertEqual(
            caught.exception.reason_code, "readiness_row_registry_mismatch"
        )
        self.assertIn("UNKNOWN_POLICY", str(caught.exception))

    def test_successor_profile_ids_install_from_registry_roles(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        lifecycle = lifecycle_registry()
        row_registry = {
            "schema_version": readiness.R1_ROW_REGISTRY_SCHEMA,
            "freeze_evidence_lifecycle": lifecycle,
        }
        expected = {
            "d117_floor_qwen25_1p5b_v2": "ALPHA",
            "d117_floor_qwen25_7b_v2": "BETA",
            "d117_contrast_qwen25_1p5b_vs_7b_v2": "GAMMA",
        }
        for pack_id, profile in expected.items():
            pack = root / pack_id
            pack.mkdir()
            self.assertEqual(readiness._plan_profile(pack, row_registry), profile)

        not_installed = root / "d117_floor_qwen25_1p5b_v3"
        not_installed.mkdir()
        with self.assertRaises(readiness.ArmReadinessError) as refused:
            readiness._plan_profile(not_installed, row_registry)
        self.assertEqual(
            refused.exception.reason_code, "readiness_row_registry_mismatch"
        )
        lifecycle["successor_policy"]["successor_pack_ids"]["ALPHA"] = (
            not_installed.name
        )
        self.assertEqual(
            readiness._plan_profile(not_installed, row_registry), "ALPHA"
        )

        repository = root / "registry-copy"
        registry_path = repository / readiness.ROW_REGISTRY_RELATIVE_PATH
        registry_path.parent.mkdir(parents=True)
        installed_registry = resolved_r1_row_registry()
        registry_path.write_bytes(readiness.render_json(installed_registry))
        installed_pack = (
            repository
            / "configs/campaigns"
            / "d117_floor_qwen25_1p5b_v2"
        )
        installed_pack.mkdir(parents=True)
        (installed_pack / "copy-marker.txt").write_text("temporary registry copy\n")
        git(repository, "init", "-q")
        git(repository, "config", "user.email", "test@example.invalid")
        git(repository, "config", "user.name", "R1 Test")
        git(repository, "add", ".")
        git(repository, "commit", "-qm", "install successor registry")
        loaded, _raw, reference = readiness._registry_reference(installed_pack)
        self.assertEqual(reference["plan_profile"], "ALPHA")
        rows, kinds = evidence._required_generic_rows(installed_pack, {})
        self.assertTrue(rows)
        self.assertTrue(kinds)
        self.assertEqual(loaded["schema_version"], readiness.R1_ROW_REGISTRY_SCHEMA)
        installed_lifecycle = readiness.validate_r1_lifecycle_registry(
            loaded["freeze_evidence_lifecycle"]
        )
        self.assertTrue(
            all(
                policy["horizon_ns"] == 1_200_000_000_000
                for policy in installed_lifecycle["evidence_policies"]
                if policy["freshness_class"] != "RE_DERIVABLE"
            )
        )
        self.assertEqual(
            set(evidence._r1_policies_for_kinds(installed_lifecycle, ["DOCTRINE_PIN"])),
            {"DOCTRINE_PIN"},
        )

        missing_horizon = copy.deepcopy(installed_lifecycle)
        next(
            policy
            for policy in missing_horizon["evidence_policies"]
            if policy["freshness_class"] == "TIME_BOUND"
        )["horizon_ns"] = None
        with self.assertRaises(readiness.ArmReadinessError) as horizon_refused:
            readiness.validate_r1_lifecycle_registry(missing_horizon)
        self.assertEqual(
            horizon_refused.exception.reason_code, "readiness_row_registry_mismatch"
        )

        removed_id = copy.deepcopy(installed_lifecycle)
        removed_id["successor_policy"]["successor_pack_ids"].pop("ALPHA")
        with self.assertRaises(readiness.ArmReadinessError) as id_refused:
            readiness._plan_profile(
                installed_pack,
                {
                    "schema_version": readiness.R1_ROW_REGISTRY_SCHEMA,
                    "freeze_evidence_lifecycle": removed_id,
                },
            )
        self.assertEqual(
            id_refused.exception.reason_code, "readiness_row_registry_mismatch"
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

    def test_r1_lifecycle_grandfathers_a_historical_v1_pack_and_profile(self) -> None:
        """Reconstructed from a dissolved premise (was: ``..._is_dormant_...``).

        The old premise was DORMANCY: while two registries existed, a
        historical v1 pack loaded the v1 registry, whose schema is not R1, so
        ``_r1_lifecycle_registry_for_pack`` returned None and the lifecycle
        simply did not exist for that pack.  The ruled repoint leaves ONE
        registry coordinate (MAGISTRATE-RULING.md:124-131), and that helper
        returns None only for a non-R1 schema -- so dormancy is now
        structurally unreachable, not merely unobserved.

        The safety property it protected survives in a different mechanism: a
        v1-era pack is not silently swept into R1 semantics, it is governed by
        an EXPLICIT grandfathering refusal.  That is what is asserted here.
        """

        pack = ROOT / "configs/campaigns/d117_floor_qwen25_1p5b_v1"
        registry, registry_raw, reference = readiness._registry_reference(pack)
        before_digest = hashlib.sha256(registry_raw).hexdigest()
        self.assertEqual(registry["schema_version"], readiness.R1_ROW_REGISTRY_SCHEMA)
        lifecycle = evidence._r1_lifecycle_registry_for_pack(pack)
        self.assertIsNotNone(lifecycle)
        roles = {
            item["role"]: item["code"] for item in lifecycle["refusal_vocabulary"]
        }
        self.assertEqual(
            roles["V1_GRANDFATHERING"], "readiness_r1_v1_grandfathering"
        )
        self.assertEqual(readiness._plan_profile(pack, registry), "ALPHA")
        self.assertEqual(
            hashlib.sha256(
                (ROOT / readiness.ROW_REGISTRY_RELATIVE_PATH).read_bytes()
            ).hexdigest(),
            before_digest,
        )
        self.assertEqual(reference["plan_profile"], "ALPHA")

    def test_deriver_read_routing_guard_detects_direct_helper_and_alias_reads(self) -> None:
        self.assertEqual(evidence._unrouted_deriver_reads(), ())
        source = Path(evidence.__file__).read_text(encoding="utf-8")
        source += (
            "\ndef _derive_direct_read_probe(context):\n"
            "    return (context.pack_root / 'probe').read_bytes()\n"
        )
        findings = evidence._unrouted_deriver_reads(source)
        self.assertTrue(any(item.endswith(":read_bytes") for item in findings))
        helper_source = (
            "def _unrecorded_helper(context):\n"
            "    return context.pack_root.joinpath('probe').read_bytes()\n\n"
            "def _derive_probe(context):\n"
            "    return _unrecorded_helper(context)\n"
        )
        helper_findings = evidence._unrouted_deriver_reads(helper_source)
        self.assertTrue(
            any(
                item.startswith("_unrecorded_helper:")
                and item.endswith(":read_bytes")
                for item in helper_findings
            )
        )
        alias_sources = {
            "builtins_import": (
                "def _unrecorded_helper(path):\n"
                "    reader = __import__('builtins').open\n"
                "    return reader(path, 'rb').read()\n\n"
                "def _derive_probe(context):\n"
                "    return _unrecorded_helper(context.pack_root / 'probe')\n"
            ),
            "importlib": (
                "import importlib\n\n"
                "def _unrecorded_helper(path):\n"
                "    reader = importlib.import_module('builtins').open\n"
                "    return reader(path, 'rb').read()\n\n"
                "def _derive_probe(context):\n"
                "    return _unrecorded_helper(context.pack_root / 'probe')\n"
            ),
            "os_attribute": (
                "import os\n\n"
                "def _unrecorded_helper(path):\n"
                "    reader = os.open\n"
                "    return reader(path, os.O_RDONLY)\n\n"
                "def _derive_probe(context):\n"
                "    helper = _unrecorded_helper\n"
                "    return helper(context.pack_root / 'probe')\n"
            ),
            "imported_alias": (
                "from os import open as raw_open\n\n"
                "def _derive_probe(context):\n"
                "    return raw_open(context.pack_root / 'probe', 0)\n"
            ),
        }
        for label, alias_source in alias_sources.items():
            with self.subTest(label=label):
                alias_findings = evidence._unrouted_deriver_reads(alias_source)
                self.assertTrue(
                    any(
                        item.endswith(":reader") or item.endswith(":raw_open")
                        for item in alias_findings
                    ),
                    alias_findings,
                )


if __name__ == "__main__":
    unittest.main()
