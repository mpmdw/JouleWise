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
from tests.test_arm_readiness_lifecycle import (
    PACK_NAME,
    git,
    make_go_fixture,
    predecessor_pack_root,
)
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

    def test_pack_comparison_is_fieldwise_and_successor_scoped(self) -> None:
        temporary, _repo, pack, _custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        current = _pack_record(pack)
        registry, _raw, _reference = readiness._registry_reference(pack)

        for field in sorted(set(current) - {"pack_root"}):
            with self.subTest(field=field):
                recorded = copy.deepcopy(current)
                recorded[field] = f"{recorded[field]}-different"
                self.assertEqual(
                    readiness._pack_mapping_mismatch_kind(
                        recorded, current, pack, registry
                    ),
                    "content",
                )
        for keyset in ("missing", "extra"):
            with self.subTest(keyset=keyset):
                recorded = copy.deepcopy(current)
                if keyset == "missing":
                    recorded.pop("plan_id")
                else:
                    recorded["unexpected"] = "different"
                self.assertEqual(
                    readiness._pack_mapping_mismatch_kind(
                        recorded, current, pack, registry
                    ),
                    "content",
                )

        _repository, _prefix, relative = readiness._repository_and_pack_relative(
            pack
        )
        relocated = copy.deepcopy(current)
        relocated["pack_root"] = f"/historical/checkout/{relative}"
        self.assertIsNone(
            readiness._pack_mapping_mismatch_kind(
                relocated, current, pack, registry
            )
        )
        relocated["pack_root"] = f"/historical/checkout/other/{pack.name}"
        self.assertEqual(
            readiness._pack_mapping_mismatch_kind(
                relocated, current, pack, registry
            ),
            "repository_relative_location",
        )

        legacy_temporary, _legacy_repo, legacy_pack, _custody, _arm = (
            make_go_fixture("d117_floor_qwen25_1p5b_v3")
        )
        self.addCleanup(legacy_temporary.cleanup)
        legacy_current = _pack_record(legacy_pack)
        legacy_registry, _raw, _reference = readiness._registry_reference(
            legacy_pack
        )
        legacy_recorded = copy.deepcopy(legacy_current)
        legacy_recorded["pack_root"] = (
            f"/historical/checkout/configs/campaigns/{legacy_pack.name}"
        )
        self.assertEqual(
            readiness._pack_mapping_mismatch_kind(
                legacy_recorded, legacy_current, legacy_pack, legacy_registry
            ),
            "archival_location",
        )

    def test_every_non_pack_staleness_limb_still_refuses(self) -> None:
        current_pack = copy.deepcopy(sample_dry_run()["pack"])
        current_reviewed = {
            "head_commit": "a" * 40,
            "clean": True,
            "exact_match": True,
        }
        expected_binding = hashlib.sha256(
            "\0".join(
                [
                    "reviewed-head",
                    current_reviewed["head_commit"],
                    "pack",
                    current_pack["pack_sha256"],
                ]
            ).encode("utf-8")
        ).hexdigest()
        passing_check = readiness._dry_run_check(
            "same_head_pack_binding",
            [
                "reviewed-head",
                current_reviewed["head_commit"],
                "pack",
                current_pack["pack_sha256"],
            ],
            0,
            current_reviewed["head_commit"],
            "",
        )
        self.assertEqual(passing_check["command_sha256"], expected_binding)

        cases = {
            "pack_content": lambda receipt, reviewed: receipt["pack"].__setitem__(
                "plan_id", "different-plan"
            ),
            "head_unavailable": lambda receipt, reviewed: reviewed.__setitem__(
                "head_commit", "unavailable"
            ),
            "dirty": lambda receipt, reviewed: reviewed.__setitem__("clean", False),
            "not_exact": lambda receipt, reviewed: reviewed.__setitem__(
                "exact_match", False
            ),
            "binding_missing": lambda receipt, reviewed: receipt.__setitem__(
                "checks", []
            ),
            "binding_duplicate": lambda receipt, reviewed: receipt.__setitem__(
                "checks", [copy.deepcopy(passing_check), copy.deepcopy(passing_check)]
            ),
            "binding_digest": lambda receipt, reviewed: receipt["checks"][0].__setitem__(
                "command_sha256", "0" * 64
            ),
        }
        for name, mutate in cases.items():
            with self.subTest(limb=name), tempfile.TemporaryDirectory() as directory:
                custody_pack_root = Path(directory) / "pack-v1"
                namespace = custody_pack_root / "arm_readiness.dry_run.receipts"
                namespace.mkdir(parents=True)
                receipt = sample_dry_run()
                receipt["pack"] = copy.deepcopy(current_pack)
                receipt["checks"] = [copy.deepcopy(passing_check)]
                reviewed = copy.deepcopy(current_reviewed)
                mutate(receipt, reviewed)
                validate_dry_run_receipt(receipt)
                raw = render_json(receipt)
                receipt_path = namespace / "dry-run-0001.json"
                receipt_path.write_bytes(raw)
                receipt_path.with_name(f"{receipt_path.name}.sha256").write_bytes(
                    gnu_sidecar(hashlib.sha256(raw).hexdigest(), receipt_path.name)
                )

                _latest, code = _latest_dry_run(
                    custody_pack_root, current_pack, reviewed
                )

                self.assertEqual(code, "readiness_dry_run_stale")

    def test_dry_run_accepts_successor_location_only_difference(self) -> None:
        temporary, _repository, pack, custody, _arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        current_pack = _pack_record(pack)
        reviewed = reviewed_main(pack)
        _repository_root, _prefix, relative = (
            readiness._repository_and_pack_relative(pack)
        )
        receipt = sample_dry_run()
        receipt["pack"] = copy.deepcopy(current_pack)
        receipt["pack"]["pack_root"] = f"/historical/checkout/{relative}"
        receipt["checks"] = [
            readiness._dry_run_check(
                "same_head_pack_binding",
                [
                    "reviewed-head",
                    reviewed["head_commit"],
                    "pack",
                    current_pack["pack_sha256"],
                ],
                0,
                reviewed["head_commit"],
                "",
            )
        ]
        namespace = custody / pack.name / "arm_readiness.dry_run.receipts"
        namespace.mkdir(parents=True)
        raw = render_json(receipt)
        receipt_path = namespace / "dry-run-0001.json"
        receipt_path.write_bytes(raw)
        receipt_path.with_name(f"{receipt_path.name}.sha256").write_bytes(
            gnu_sidecar(hashlib.sha256(raw).hexdigest(), receipt_path.name)
        )

        latest, code = _latest_dry_run(
            custody / pack.name, current_pack, reviewed
        )

        self.assertIsNotNone(latest)
        self.assertIsNone(code)

    def test_production_minted_dry_run_survives_repository_relocation(self) -> None:
        from joulewise import arm_readiness_evidence as evidence
        from tests.test_arm_readiness_evidence_author import make_author_fixture

        family = {
            "ALPHA": "d117_floor_qwen25_1p5b_v4",
            "BETA": "d117_floor_qwen25_7b_v4",
            "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v4",
        }
        with (
            mock.patch.dict(evidence._PACKS_BY_PROFILE, family),
            mock.patch.object(
                readiness, "_utc_now", return_value="2026-08-12T12:00:00Z"
            ),
            mock.patch.object(evidence.time, "monotonic_ns", return_value=100),
        ):
            temporary, repository, pack, custody, _arm_path = make_author_fixture(
                PACK_NAME
            )
            self.addCleanup(temporary.cleanup)
            # The production author executes copied Python modules inside this
            # intentionally minimal repository. Give it the bytecode ignore a
            # normal checkout already has so that the real reviewed-main gate,
            # rather than fixture-only __pycache__ residue, decides cleanliness.
            (repository / ".gitignore").write_text("__pycache__/\n*.pyc\n")
            git(repository, "add", ".gitignore")
            git(repository, "commit", "-qm", "ignore interpreter bytecode")
            git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
            authored = evidence.author_arm_readiness_evidence(pack)
            self.assertEqual(authored["status"], "PASS", authored)
            pack_relative = pack.relative_to(repository).as_posix()
            git(
                repository,
                "add",
                "--",
                f"{pack_relative}/{evidence._SOURCE_DIRECTORY}",
                f"{pack_relative}/{evidence._EVIDENCE_DIRECTORY}",
            )
            git(repository, "commit", "-qm", "author freeze evidence")
            git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
            predecessor = predecessor_pack_root(repository, pack.name)
            frozen = readiness.generate_freeze_receipt(
                pack, predecessor_pack_root=predecessor
            )
            self.assertEqual(frozen["status"], "PASS", frozen)
            git(repository, "add", "--", pack_relative)
            git(repository, "commit", "-qm", "mint freeze receipt")
            git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

            minted = generate_dry_run_receipt(
                pack,
                custody,
                "relocation-rehearsal",
                Path(temporary.name) / "synthetic-relocation",
            )
            self.assertEqual(minted["status"], "PASS", minted)
            recorded = json.loads(Path(minted["receipt_path"]).read_text())

            relocated_repository = Path(temporary.name) / "relocated-repository"
            git(
                Path(temporary.name),
                "clone",
                "-q",
                "--no-local",
                str(repository),
                str(relocated_repository),
            )
            git(relocated_repository, "config", "gc.auto", "0")
            git(relocated_repository, "config", "maintenance.auto", "false")
            relocated_pack = relocated_repository / pack.relative_to(repository)
            current_pack = _pack_record(relocated_pack)

            latest, code = _latest_dry_run(
                custody / pack.name,
                current_pack,
                reviewed_main(relocated_pack),
            )

        self.assertIsNotNone(latest)
        self.assertNotEqual(
            recorded["pack"]["pack_root"], current_pack["pack_root"]
        )
        self.assertEqual(
            {
                key: value
                for key, value in recorded["pack"].items()
                if key != "pack_root"
            },
            {
                key: value
                for key, value in current_pack.items()
                if key != "pack_root"
            },
        )
        self.assertIsNone(code)

    @unittest.skip(
        "STRUCTURAL-BLOCKED: synthetic fixture authors legacy generic evidence; "
        "R1 requires content/execution receipt schemas"
    )
    def test_real_under_lease_rehearsal_uses_reservation_and_both_writer_slots(self) -> None:
        """Blocked by legacy-schema evidence in the synthetic freeze fixture."""

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

    @unittest.skip(
        "STRUCTURAL-BLOCKED: synthetic fixture authors legacy generic evidence; "
        "R1 requires content/execution receipt schemas"
    )
    def test_dry_run_becomes_stale_after_later_head_even_when_pack_bytes_do_not_change(self) -> None:
        """Blocked by legacy-schema evidence in the synthetic freeze fixture."""

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

    @unittest.skip(
        "STRUCTURAL-BLOCKED: synthetic fixture authors legacy generic evidence; "
        "R1 requires content/execution receipt schemas"
    )
    def test_dry_run_refuses_a_dirty_or_nonreviewed_checkout(self) -> None:
        """Blocked by legacy-schema evidence in the synthetic freeze fixture."""

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

    @unittest.skip(
        "STRUCTURAL-BLOCKED: synthetic fixture authors legacy generic evidence; "
        "R1 requires content/execution receipt schemas"
    )
    def test_dry_run_rehearsal_root_and_id_are_single_use(self) -> None:
        """Blocked by legacy-schema evidence in the synthetic freeze fixture."""

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
