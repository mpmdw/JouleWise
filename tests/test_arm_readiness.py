from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
from tests.test_arm_readiness_schemas import (
    TEST_BOOT_SESSION_ID,
    probe_clock_value,
    sample_arm,
    sample_evidence,
)


class ClockProbePredicateLivenessTests(unittest.TestCase):
    @staticmethod
    def _predicate_passes(age_ns: int) -> bool:
        value = probe_clock_value()
        receipt = sample_evidence()
        receipt.update(
            {
                "evidence_id": "test-clock-attestation",
                "kind": "CLOCK_ATTESTATION",
                "valid_until_monotonic_ns": (
                    value["r1_batch_finished_monotonic_ns"]
                    + 21_600_000_000_000
                    + age_ns
                ),
            }
        )
        receipt["facts"] = [
            {
                "fact_id": "clock.correct_and_prior_state.v1",
                "value_type": "OBJECT",
                "value": value,
                "source_kind": "PROBE",
                "source_path": "source.json",
                "source_sha256": "0" * 64,
            }
        ]
        live_clock_anchor = {
            "boot_session_id": receipt["boot_session_id"],
            "realtime_ns": value["anchor_realtime_ns"],
            "monotonic_raw_ns": value["anchor_monotonic_raw_ns"],
            "read_skew_ns": value["anchor_read_skew_ns"],
        }
        return readiness._predicate_passes(
            receipt,
            "clock.correct_and_prior_state.v1",
            live_clock_anchor=live_clock_anchor,
        )

    def test_t0_liveness_bound_refuses_at_600s_plus_1ns(self) -> None:
        self.assertFalse(self._predicate_passes(600_000_000_001))

    def test_t0_liveness_bound_passes_at_600s_minus_1ns(self) -> None:
        self.assertTrue(self._predicate_passes(599_999_999_999))

    def test_t0_liveness_bound_passes_at_exactly_600s(self) -> None:
        self.assertTrue(self._predicate_passes(600_000_000_000))

    def test_t0_liveness_bound_refuses_negative(self) -> None:
        self.assertFalse(self._predicate_passes(-1))


class LaunchConsumptionV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.pack = root / "pack-v2"
        self.pack.mkdir()
        self.custody = root / "arm-custody"
        self.arm = sample_arm(root / "context")
        self.arm["boot_session_id"] = TEST_BOOT_SESSION_ID
        self.arm["pack"]["pack_root"] = str(self.pack)
        pack_record_patch = mock.patch.object(
            readiness, "_pack_record", return_value=self.arm["pack"]
        )
        pack_record_patch.start()
        self.addCleanup(pack_record_patch.stop)
        for name in (
            "claim_runs_root",
            "bound_runs_root",
            "custody_root",
            "quarantine_root",
            "claim_backup_destination",
            "bound_backup_destination",
        ):
            Path(self.arm["arm_context"][name]).mkdir(parents=True)
        Path(self.arm["arm_context"]["waiver_path"]).write_bytes(
            readiness.render_json([])
        )
        namespace = self.custody / self.pack.name / "arm_readiness.receipts"
        namespace.mkdir(parents=True)
        self.arm_path = namespace / "arm-0001.json"
        arm_raw = readiness.render_json(self.arm)
        self.arm_path.write_bytes(arm_raw)
        self.arm_path.with_name(f"{self.arm_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(arm_raw).hexdigest(), self.arm_path.name
            )
        )
        self.window_root = self.custody / "window-plan"
        self.window_root.mkdir()
        (self.window_root / "window.env").write_text(
            f"PACK_ROOT={self.pack}\n"
        )
        self.chain_path = self.window_root / "window-chain.zsh"
        self.chain_path.write_text(
            f"#!/bin/zsh\n# PACK_ROOT={self.pack}\nexit 0\n"
        )
        self.exec_argv = [
            "/usr/bin/caffeinate",
            "-is",
            "/bin/zsh",
            str(self.chain_path),
            str(self.window_root),
        ]
        self.manifest_path = (
            self.custody
            / self.pack.name
            / "arm_readiness.t0.inputs"
            / "launch-manifest.json"
        )
        self.manifest_path.parent.mkdir(parents=True)
        self.manifest_path.write_bytes(
            readiness.render_json(
                {
                    "schema_version": readiness.LAUNCH_MANIFEST_SCHEMA,
                    "boot_session_id": TEST_BOOT_SESSION_ID,
                    "window_plan_root": str(self.window_root),
                    "prewindow_command": ["/bin/true"],
                    "launch_command": self.exec_argv,
                }
            )
        )
        self._install_attested_launch_recipe()

    def _rewrite_arm(self) -> None:
        raw = readiness.render_json(self.arm)
        self.arm_path.write_bytes(raw)
        self.arm_path.with_name(f"{self.arm_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(raw).hexdigest(), self.arm_path.name
            )
        )

    @staticmethod
    def _artifact(path: Path) -> dict[str, str]:
        return {
            "path": str(path.resolve()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    def _install_attested_launch_recipe(self) -> None:
        custody_pack_root = self.custody / self.pack.name
        source_relative = (
            "arm_readiness.t0.sources/t0-single-launch-capability.json"
        )
        source_path = custody_pack_root / source_relative
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source = {
            "schema_version": "joulewise.arm_readiness_t0_evidence_source.v1",
            "row_id": "t0.single_launch_capability",
            "kind": "LAUNCH_RECIPE",
            "head_commit": self.arm["reviewed_main"]["head_commit"],
            "head_tree_oid": self.arm["reviewed_main"]["head_tree_oid"],
            "pack_sha256": self.arm["pack"]["pack_sha256"],
            "boot_session_id": self.arm["boot_session_id"],
            "primary_artifacts": [],
            "input_artifacts": sorted(
                (
                    self._artifact(self.manifest_path),
                    self._artifact(self.window_root / "window.env"),
                    self._artifact(self.chain_path),
                ),
                key=lambda item: item["path"],
            ),
            "probes": [],
            "facts": [
                {
                    "fact_id": "t0.single_launch_capability.v1",
                    "value": {
                        "atomic_single_use_capability_available": True,
                        "attempt_ids_unused": True,
                        "exact_launch_command_frozen": True,
                        "session_id_unused": True,
                    },
                }
            ],
            "derivation": {"launch_command": self.exec_argv},
        }
        source_raw = readiness.render_json(source)
        source_path.write_bytes(source_raw)
        evidence_id = "evidence-t0-t0-single-launch-capability"
        evidence_name = f"{evidence_id}.json"
        evidence_path = custody_pack_root / "arm_readiness.evidence" / evidence_name
        evidence_path.parent.mkdir(exist_ok=True)
        evidence = {
            "schema_version": readiness.EVIDENCE_RECEIPT_SCHEMA,
            "evidence_id": evidence_id,
            "kind": "LAUNCH_RECIPE",
            "status": "PASS",
            "issued_at_utc": "2026-08-11T00:00:00Z",
            "boot_session_id": self.arm["boot_session_id"],
            "valid_until_monotonic_ns": 10**30,
            "pack_sha256": self.arm["pack"]["pack_sha256"],
            "head_commit": self.arm["reviewed_main"]["head_commit"],
            "facts": [
                {
                    "fact_id": "t0.single_launch_capability.v1",
                    "value_type": "OBJECT",
                    "value": copy.deepcopy(source["facts"][0]["value"]),
                    "source_kind": "PROBE",
                    "source_path": source_relative,
                    "source_sha256": hashlib.sha256(source_raw).hexdigest(),
                }
            ],
            "checks": [{"check_id": "derive-t0-launch", "status": "PASS"}],
            "reason_codes": [],
            "assurance": copy.deepcopy(readiness.ASSURANCE),
        }
        evidence_raw = readiness.render_json(evidence)
        evidence_path.write_bytes(evidence_raw)
        evidence_digest = hashlib.sha256(evidence_raw).hexdigest()
        evidence_path.with_name(f"{evidence_name}.sha256").write_bytes(
            readiness.gnu_sidecar(evidence_digest, evidence_name)
        )
        self.arm["evidence"] = [
            {
                "evidence_id": evidence_id,
                "receipt_kind": "LAUNCH_RECIPE",
                "namespace": "WINDOW_CUSTODY",
                "path": f"arm_readiness.evidence/{evidence_name}",
                "sha256": evidence_digest,
                "schema_version": readiness.EVIDENCE_RECEIPT_SCHEMA,
                "status": "PASS",
            }
        ]
        self._rewrite_arm()

    def _launch_recipe_artifact_paths(self) -> dict[str, Path]:
        item = self.arm["evidence"][0]
        receipt = self.custody / self.pack.name / str(item["path"])
        return {
            "receipt": receipt,
            "sidecar": receipt.with_name(f"{receipt.name}.sha256"),
            "source": (
                self.custody
                / self.pack.name
                / "arm_readiness.t0.sources/t0-single-launch-capability.json"
            ),
            "manifest": self.manifest_path,
            "environment": self.window_root / "window.env",
            "chain": self.chain_path,
        }

    def _verify_with_launch_recipe_replay(
        self, consumption_path: Path
    ) -> dict[str, object]:
        def replay_semantics(
            root: Path,
            custody_pack_root: Path,
            arm: object,
            *,
            launch_binding_cache: dict[Path, bytes] | None = None,
            # Mirrors the production signature, which now threads Ed's step-6
            # confirmation custody through verification.  A double that does
            # not accept what its caller passes is not a double: it raises
            # TypeError from inside the mock, and the test then fails for a
            # reason unrelated to what it asserts.  Named explicitly rather
            # than swallowed by **kwargs, so the NEXT signature change fails
            # loudly here instead of drifting silently.
            step6_confirmation_table: Path | str | None = None,
            expected_confirmation_digest: str | None = None,
        ) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
            self.assertIsNotNone(launch_binding_cache)
            self.assertIsInstance(arm, dict)
            item = arm["evidence"][0]
            items, receipts, refusals = readiness._discover_evidence(
                root,
                custody_pack_root,
                pack_sha256=arm["pack"]["pack_sha256"],
                head_commit=arm["reviewed_main"]["head_commit"],
                boot_session_id=arm["boot_session_id"],
                now_monotonic_ns=None,
                include_pack=False,
                launch_binding_cache=launch_binding_cache,
            )
            self.assertEqual(items, [item])
            self.assertEqual(set(receipts), {item["evidence_id"]})
            self.assertEqual(refusals, [])
            return arm["rows"], arm["refusals"]

        with mock.patch.object(
            readiness,
            "_derive_arm_semantics_for_verification",
            side_effect=replay_semantics,
        ), mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            return readiness.verify_consumed_launch(
                self.pack,
                consumption_path,
                launch_manifest=self.manifest_path,
                expected_exec_argv=self.exec_argv,
            )

    def _consumer_inputs(self, token: bytes = b"t" * 32) -> dict[str, object]:
        arm_raw = self.arm_path.read_bytes()
        manifest_raw = self.manifest_path.read_bytes()
        manifest = readiness.parse_json_bytes(
            manifest_raw, require_canonical=True
        )
        window_root = Path(str(manifest["window_plan_root"]))
        chain_path = window_root / "window-chain.zsh"
        return {
            "pack_root": self.pack,
            "arm_receipt": self.arm_path,
            "authenticated_arm_receipt": copy.deepcopy(self.arm),
            "arm_receipt_sha256": hashlib.sha256(arm_raw).hexdigest(),
            "window_custody_root": self.custody,
            "launch_manifest": self.manifest_path,
            "authenticated_launch_manifest": manifest,
            "launch_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "window_plan_root": window_root,
            "window_environment_sha256": hashlib.sha256(
                (window_root / "window.env").read_bytes()
            ).hexdigest(),
            "window_chain_sha256": hashlib.sha256(
                chain_path.read_bytes()
            ).hexdigest(),
            "exec_argv": list(manifest["launch_command"]),
            "handoff_token_sha256": hashlib.sha256(token).hexdigest(),
        }

    def _invoke_consumer(self, inputs: dict[str, object]) -> dict[str, object]:
        arm_digest = hashlib.sha256(self.arm_path.read_bytes()).hexdigest()
        with mock.patch.object(
            readiness,
            "_verify_arm_receipt",
            return_value={
                "status": "PASS",
                "arm_disposition": "GO",
                "receipt_path": str(self.arm_path.resolve()),
                "receipt_sha256": arm_digest,
                "pack_sha256": self.arm["pack"]["pack_sha256"],
            },
        ), mock.patch.object(
            readiness, "reviewed_main", return_value=self.arm["reviewed_main"]
        ), mock.patch.object(
            readiness, "_root_policy_refusals", return_value=([], set())
        ):
            return readiness._consume_launch_capability(**inputs)

    def _consume(
        self, token: bytes = b"t" * 32, **overrides: object
    ) -> dict[str, object]:
        inputs = self._consumer_inputs(token)
        inputs.update(overrides)
        return self._invoke_consumer(inputs)

    def _settle(self, token: bytes = b"l" * 32) -> tuple[Path, dict[str, object]]:
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            settled = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
        return consumption_path, settled

    def _authenticate_campaign(
        self, runs_root: Path, *, config_paths: tuple[Path, ...] = ()
    ) -> dict[str, object]:
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ), mock.patch.object(
            readiness,
            "_git_text",
            return_value=self.arm["reviewed_main"]["head_commit"],
        ), mock.patch.object(
            readiness,
            "_authenticated_pack_config_inventory",
            return_value={
                path.resolve().relative_to(self.pack.resolve()).as_posix():
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in config_paths
                if path.resolve().is_relative_to(self.pack.resolve())
            },
        ):
            return readiness.authenticate_campaign_launch_lineage(
                runs_root, config_paths=config_paths
            )

    def test_v2_claim_is_fsynced_and_replays_from_consumption(self) -> None:
        with mock.patch.object(
            readiness, "_fsync_directory", wraps=readiness._fsync_directory
        ) as fsync_directory:
            result = self._consume()
        self.assertEqual(fsync_directory.call_count, 3)
        consumption_path = Path(str(result["consumption_path"]))
        consumption = readiness.validate_consumption_receipt(
            readiness.parse_json_bytes(
                consumption_path.read_bytes(), require_canonical=True
            )
        )
        self.assertEqual(
            consumption["schema_version"], readiness.CONSUMPTION_RECEIPT_SCHEMA
        )
        self.assertEqual(consumption["exec_argv"], self.exec_argv)
        self.assertEqual(
            consumption["arm_context_sha256"],
            hashlib.sha256(
                readiness.render_json(self.arm["arm_context"])
            ).hexdigest(),
        )
        with mock.patch.object(
            readiness, "_pack_record", return_value=self.arm["pack"]
        ), mock.patch.object(
            readiness,
            "_derive_arm_semantics_for_verification",
            return_value=(self.arm["rows"], self.arm["refusals"]),
        ), mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            verified = readiness.verify_consumed_launch(
                self.pack,
                consumption_path,
                launch_manifest=self.manifest_path,
                expected_exec_argv=self.exec_argv,
            )
        self.assertEqual(verified["status"], "PASS")
        self.assertEqual(verified["consumption_sha256"], result["consumption_sha256"])

    def test_start_settle_completion_form_one_authenticated_lineage(self) -> None:
        token = b"h" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
            completed = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "completion"
            )
        lineage = readiness.authenticate_launch_lineage(
            completed["launch_lineage"], require_completion=True
        )
        self.assertEqual(lineage["consumption_sha256"], result["consumption_sha256"])
        self.assertIsNotNone(lineage["completion_sha256"])

    def test_settle_publishes_both_canonical_no_clobber_locators(self) -> None:
        with mock.patch.object(
            readiness, "_fsync_directory", wraps=readiness._fsync_directory
        ) as fsync_directory:
            _consumption_path, settled = self._settle()
        for role in ("claim_runs_root", "bound_runs_root"):
            root = Path(self.arm["arm_context"][role])
            locator_path = root / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
            raw = locator_path.read_bytes()
            locator = readiness.parse_json_bytes(raw, require_canonical=True)
            self.assertEqual(
                set(locator), readiness.LAUNCH_LINEAGE_LOCATOR_KEYS
            )
            self.assertEqual(
                locator["schema_version"],
                readiness.LAUNCH_LINEAGE_LOCATOR_SCHEMA,
            )
            self.assertEqual(locator["root_role"], role)
            self.assertEqual(locator["root_path"], str(root.resolve()))
            self.assertEqual(locator["launch_lineage"], settled["launch_lineage"])
            self.assertIsNone(locator["launch_lineage"]["completion"])
            self.assertEqual(
                locator_path.with_name(f"{locator_path.name}.sha256").read_bytes(),
                readiness.gnu_sidecar(
                    hashlib.sha256(raw).hexdigest(), locator_path.name
                ),
            )
            self.assertEqual(
                sum(
                    Path(call.args[0]).resolve() == root.resolve()
                    for call in fsync_directory.call_args_list
                ),
                2,
            )
        authenticated = self._authenticate_campaign(
            Path(self.arm["arm_context"]["claim_runs_root"])
        )
        self.assertEqual(
            readiness.render_json(authenticated["launch_lineage"]),
            readiness.render_json(settled["launch_lineage"]),
        )
        selected_locator = (
            Path(self.arm["arm_context"]["claim_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        self.assertEqual(
            authenticated["locator_sha256"],
            hashlib.sha256(selected_locator.read_bytes()).hexdigest(),
        )

    def test_lineage_replay_derives_pack_root_and_rejects_caller_mismatch(self) -> None:
        _consumption_path, settled = self._settle()
        replay = readiness.authenticate_launch_lineage(
            settled["launch_lineage"], require_completion=False
        )
        self.assertEqual(replay["pack_root"], str(self.pack.resolve()))
        other = Path(self.temporary.name) / "other-pack"
        other.mkdir()
        with self.assertRaises(readiness.LaunchLineageError) as caught:
            readiness.authenticate_launch_lineage(
                settled["launch_lineage"],
                require_completion=False,
                expected_pack_root=other,
            )
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_partial_locator_publication_burns_and_cannot_be_repaired(self) -> None:
        token = b"p" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        bound_locator = (
            Path(self.arm["arm_context"]["bound_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        real_write = readiness._exclusive_write

        def fail_bound_primary(path: Path, raw: bytes) -> None:
            if path.resolve(strict=False) == bound_locator.resolve(strict=False):
                raise readiness.ArmReadinessError(
                    "readiness_io_error", "injected bound-locator crash"
                )
            real_write(path, raw)

        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            with mock.patch.object(
                readiness, "_exclusive_write", side_effect=fail_bound_primary
            ):
                with self.assertRaises(readiness.LaunchLineageError) as caught:
                    readiness.record_launch_lifecycle_event(
                        self.pack, consumption_path, "settle"
                    )
            self.assertEqual(
                caught.exception.reason_code, "launch_consumption_invalid"
            )
            claim_locator = (
                Path(self.arm["arm_context"]["claim_runs_root"])
                / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
            )
            self.assertTrue(claim_locator.is_file())
            self.assertTrue(
                claim_locator.with_name(f"{claim_locator.name}.sha256").is_file()
            )
            self.assertFalse(bound_locator.exists())
            with self.assertRaises(readiness.LaunchLineageError) as replay:
                readiness.record_launch_lifecycle_event(
                    self.pack, consumption_path, "settle"
                )
        self.assertEqual(
            replay.exception.reason_code, "launch_consumption_invalid"
        )

    def test_precreated_locator_burns_settle_without_publishing_sibling(self) -> None:
        token = b"o" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        claim_locator = (
            Path(self.arm["arm_context"]["claim_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        claim_locator.write_text("precreated\n")
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            with self.assertRaises(readiness.LaunchLineageError) as caught:
                readiness.record_launch_lifecycle_event(
                    self.pack, consumption_path, "settle"
                )
        self.assertEqual(caught.exception.reason_code, "launch_consumption_invalid")
        bound_locator = (
            Path(self.arm["arm_context"]["bound_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        self.assertFalse(bound_locator.exists())
        claim_locator.unlink()
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            with self.assertRaises(readiness.LaunchLineageError) as replay:
                readiness.record_launch_lifecycle_event(
                    self.pack, consumption_path, "settle"
                )
        self.assertEqual(
            replay.exception.reason_code, "launch_consumption_invalid"
        )
        self.assertFalse(bound_locator.exists())

    def test_locator_missing_corrupt_root_swap_and_mixed_are_discriminated(self) -> None:
        self._settle()
        claim = (
            Path(self.arm["arm_context"]["claim_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        bound = (
            Path(self.arm["arm_context"]["bound_runs_root"])
            / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
        )
        paths = (
            claim,
            claim.with_name(f"{claim.name}.sha256"),
            bound,
            bound.with_name(f"{bound.name}.sha256"),
        )
        original = {path: path.read_bytes() for path in paths}

        claim.with_name(f"{claim.name}.sha256").unlink()
        with self.assertRaises(readiness.LaunchLineageError) as missing:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(missing.exception.reason_code, "launch_consumption_missing")
        for path, raw in original.items():
            path.write_bytes(raw)

        claim.write_bytes(original[claim] + b" ")
        with self.assertRaises(readiness.LaunchLineageError) as corrupt_primary:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(
            corrupt_primary.exception.reason_code, "launch_consumption_invalid"
        )
        for path, raw in original.items():
            path.write_bytes(raw)

        claim.with_name(f"{claim.name}.sha256").write_text("corrupt\n")
        with self.assertRaises(readiness.LaunchLineageError) as corrupt_sidecar:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(
            corrupt_sidecar.exception.reason_code, "launch_consumption_invalid"
        )
        for path, raw in original.items():
            path.write_bytes(raw)

        claim.write_bytes(original[bound])
        claim.with_name(f"{claim.name}.sha256").write_bytes(
            original[bound.with_name(f"{bound.name}.sha256")]
        )
        bound.write_bytes(original[claim])
        bound.with_name(f"{bound.name}.sha256").write_bytes(
            original[claim.with_name(f"{claim.name}.sha256")]
        )
        with self.assertRaises(readiness.LaunchLineageError) as swapped:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(swapped.exception.reason_code, "launch_binding_mismatch")
        for path, raw in original.items():
            path.write_bytes(raw)

        second = LaunchConsumptionV2Tests(
            methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
        )
        second.setUp()
        try:
            second._settle()
            second_bound_path = (
                Path(second.arm["arm_context"]["bound_runs_root"])
                / readiness.LAUNCH_LINEAGE_LOCATOR_BASENAME
            )
            second_locator = readiness.parse_json_bytes(
                second_bound_path.read_bytes(), require_canonical=True
            )
        finally:
            second.doCleanups()
        mixed = json.loads(original[bound])
        mixed["launch_lineage"] = second_locator["launch_lineage"]
        mixed_raw = readiness.render_json(mixed)
        bound.write_bytes(mixed_raw)
        bound.with_name(f"{bound.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(mixed_raw).hexdigest(), bound.name
            )
        )
        with self.assertRaises(readiness.LaunchLineageError) as conflict:
            self._authenticate_campaign(claim.parent)
        self.assertEqual(conflict.exception.reason_code, "launch_lineage_conflict")

    def test_public_consumption_name_is_absent(self) -> None:
        self.assertNotIn("consume_launch_capability", readiness.__all__)
        with self.assertRaises(AttributeError):
            getattr(readiness, "consume_launch_capability")
        with self.assertRaises(ImportError):
            exec(
                "from joulewise.arm_readiness import consume_launch_capability",
                {},
            )

    def test_private_complete_context_consumes_once_at_atomic_primary(self) -> None:
        self._consume()
        with mock.patch.object(
            readiness, "_exclusive_write", wraps=readiness._exclusive_write
        ) as exclusive_write:
            with self.assertRaises(readiness.ArmReadinessError) as replay:
                self._consume()
        self.assertEqual(
            replay.exception.reason_code, "readiness_record_consumed"
        )
        exclusive_write.assert_called_once()

    def _author_complete_launch_context(self, name: str) -> None:
        window_root = self.custody / name
        window_root.mkdir()
        (window_root / "window.env").write_text(
            f"PACK_ROOT=/tmp/{name}\nBRACKET_SESSION_ID={name}\n"
        )
        chain_path = window_root / "window-chain.zsh"
        chain_path.write_text(f"#!/bin/zsh\n# {name}\nexit 0\n")
        argv = [
            "/usr/bin/caffeinate",
            "-is",
            "/bin/zsh",
            str(chain_path),
            str(window_root),
        ]
        self.manifest_path.write_bytes(
            readiness.render_json(
                {
                    "schema_version": readiness.LAUNCH_MANIFEST_SCHEMA,
                    "boot_session_id": TEST_BOOT_SESSION_ID,
                    "window_plan_root": str(window_root),
                    "prewindow_command": ["/bin/true"],
                    "launch_command": argv,
                }
            )
        )

    def _install_foreign_pack_session_context(self) -> None:
        beta = LaunchConsumptionV2Tests(
            methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
        )
        beta.setUp()
        try:
            beta_manifest = readiness.parse_json_bytes(
                beta.manifest_path.read_bytes(), require_canonical=True
            )
            self.assertEqual(
                beta_manifest["boot_session_id"], self.arm["boot_session_id"]
            )
            beta_window = Path(str(beta_manifest["window_plan_root"]))
            staged_window = self.custody / "beta-pack-session"
            staged_window.mkdir()
            (staged_window / "window.env").write_bytes(
                (beta_window / "window.env").read_bytes()
            )
            staged_chain = staged_window / "window-chain.zsh"
            staged_chain.write_bytes(
                (beta_window / "window-chain.zsh").read_bytes()
            )
            beta_manifest["window_plan_root"] = str(staged_window)
            beta_manifest["launch_command"] = [
                "/usr/bin/caffeinate",
                "-is",
                "/bin/zsh",
                str(staged_chain),
                str(staged_window),
            ]
            self.manifest_path.write_bytes(readiness.render_json(beta_manifest))
        finally:
            beta.doCleanups()

    def _caller_attested_references(self) -> dict[str, dict[str, str]]:
        inputs = self._consumer_inputs()
        window_root = Path(str(inputs["window_plan_root"]))
        return {
            "launch_manifest": self._artifact(self.manifest_path),
            "window_environment": self._artifact(window_root / "window.env"),
            "window_chain": self._artifact(window_root / "window-chain.zsh"),
        }

    def _assert_current_context_binding_refusal(self) -> None:
        consumption_dir = (
            self.custody / self.pack.name / "arm_readiness.consumptions"
        )
        with self.assertRaises(readiness.LaunchLineageError) as caught:
            self._consume()
        self.assertEqual(
            caught.exception.reason_code, "launch_binding_mismatch"
        )
        self.assertFalse(consumption_dir.exists())

    def test_foreign_pack_session_refuses_without_burning_honest_arm(self) -> None:
        honest_manifest = self.manifest_path.read_bytes()
        self._install_foreign_pack_session_context()
        self._assert_current_context_binding_refusal()
        self.manifest_path.write_bytes(honest_manifest)
        self.assertEqual(self._consume()["status"], "CONSUMED")

    def test_self_authored_context_refuses_without_burning_honest_arm(self) -> None:
        honest_manifest = self.manifest_path.read_bytes()
        self._author_complete_launch_context("self-authored-session")
        self._assert_current_context_binding_refusal()
        self.manifest_path.write_bytes(honest_manifest)
        self.assertEqual(self._consume()["status"], "CONSUMED")

    def test_omitted_digest_and_path_inputs_are_registered_usage_refusals(
        self,
    ) -> None:
        consumption_dir = (
            self.custody / self.pack.name / "arm_readiness.consumptions"
        )
        for omitted in ("launch_manifest_sha256", "launch_manifest"):
            with self.subTest(omitted=omitted):
                inputs = self._consumer_inputs()
                del inputs[omitted]
                with self.assertRaises(readiness.ArmReadinessError) as caught:
                    self._invoke_consumer(inputs)
                self.assertEqual(
                    caught.exception.reason_code, "readiness_usage_invalid"
                )
                self.assertFalse(consumption_dir.exists())

    def test_foreign_consumption_record_refuses_on_replay(self) -> None:
        self._author_complete_launch_context("foreign-replay-session")
        with mock.patch.object(
            readiness,
            "_attested_launch_artifact_references",
            return_value=self._caller_attested_references(),
            create=True,
        ):
            result = self._consume()
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness, "_pack_record", return_value=self.arm["pack"]
        ), mock.patch.object(
            readiness,
            "_derive_arm_semantics_for_verification",
            return_value=(self.arm["rows"], self.arm["refusals"]),
        ), mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            with self.assertRaises(readiness.LaunchLineageError) as caught:
                readiness.verify_consumed_launch(self.pack, consumption_path)
        self.assertEqual(
            caught.exception.reason_code, "launch_binding_mismatch"
        )

    def test_attested_identity_lookup_is_load_bearing_for_foreign_attacks(
        self,
    ) -> None:
        for attack in ("foreign-pack-session", "self-authored"):
            fixture = LaunchConsumptionV2Tests(
                methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
            )
            fixture.setUp()
            try:
                if attack == "foreign-pack-session":
                    fixture._install_foreign_pack_session_context()
                else:
                    fixture._author_complete_launch_context(
                        "self-authored-session"
                    )
                with mock.patch.object(
                    readiness,
                    "_attested_launch_artifact_references",
                    return_value=fixture._caller_attested_references(),
                    create=True,
                ):
                    with self.assertRaises(AssertionError):
                        fixture._assert_current_context_binding_refusal()
            finally:
                fixture.doCleanups()

    def test_byte_identical_manifest_at_noncanonical_path_refuses_no_burn(
        self,
    ) -> None:
        substitute = Path(self.temporary.name) / "manifest-copy.json"
        substitute.write_bytes(self.manifest_path.read_bytes())
        consumption_dir = (
            self.custody / self.pack.name / "arm_readiness.consumptions"
        )
        with self.assertRaises(readiness.LaunchLineageError) as caught:
            self._consume(launch_manifest=substitute)
        self.assertEqual(
            caught.exception.reason_code, "launch_binding_mismatch"
        )
        self.assertFalse(consumption_dir.exists())
        self.assertEqual(self._consume()["status"], "CONSUMED")

    def test_launch_recipe_anchor_requires_exactly_one_satisfying_receipt(
        self,
    ) -> None:
        for mode in ("zero", "multiple"):
            fixture = LaunchConsumptionV2Tests(
                methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
            )
            fixture.setUp()
            try:
                if mode == "zero":
                    fixture.arm["evidence"] = []
                else:
                    original_item = fixture.arm["evidence"][0]
                    original_path = (
                        fixture.custody
                        / fixture.pack.name
                        / str(original_item["path"])
                    )
                    duplicate = readiness.parse_json_bytes(
                        original_path.read_bytes(), require_canonical=True
                    )
                    duplicate["evidence_id"] = "evidence-t0-launch-duplicate"
                    duplicate_name = "evidence-t0-launch-duplicate.json"
                    duplicate_path = original_path.with_name(duplicate_name)
                    duplicate_raw = readiness.render_json(duplicate)
                    duplicate_path.write_bytes(duplicate_raw)
                    duplicate_digest = hashlib.sha256(duplicate_raw).hexdigest()
                    duplicate_path.with_name(
                        f"{duplicate_name}.sha256"
                    ).write_bytes(
                        readiness.gnu_sidecar(duplicate_digest, duplicate_name)
                    )
                    duplicate_item = copy.deepcopy(original_item)
                    duplicate_item.update(
                        {
                            "evidence_id": duplicate["evidence_id"],
                            "path": f"arm_readiness.evidence/{duplicate_name}",
                            "sha256": duplicate_digest,
                        }
                    )
                    fixture.arm["evidence"].append(duplicate_item)
                    fixture.arm["evidence"].sort(
                        key=lambda item: item["evidence_id"]
                    )
                fixture._rewrite_arm()
                with self.subTest(mode=mode):
                    fixture._assert_current_context_binding_refusal()
            finally:
                fixture.doCleanups()

    def test_launch_recipe_reconciliation_reads_each_artifact_once(self) -> None:
        targets = {
            path.resolve(): name
            for name, path in self._launch_recipe_artifact_paths().items()
        }
        read_counts = {name: 0 for name in targets.values()}
        real_open = Path.open

        def tracking_open(path: Path, *args: object, **kwargs: object):
            resolved = path.resolve(strict=False)
            if resolved in targets:
                read_counts[targets[resolved]] += 1
            return real_open(path, *args, **kwargs)

        inputs = self._consumer_inputs()
        with mock.patch.object(Path, "open", new=tracking_open):
            result = self._invoke_consumer(inputs)
        self.assertEqual(result["status"], "CONSUMED")
        self.assertEqual(
            read_counts,
            {
                "receipt": 1,
                "sidecar": 1,
                "source": 1,
                "manifest": 1,
                "environment": 1,
                "chain": 1,
            },
        )

    def test_verify_consumed_launch_reads_each_artifact_once(self) -> None:
        result = self._consume()
        consumption_path = Path(str(result["consumption_path"]))
        targets = {
            path.resolve(): name
            for name, path in self._launch_recipe_artifact_paths().items()
        }
        read_counts = {name: 0 for name in targets.values()}
        real_open = Path.open

        def tracking_open(path: Path, *args: object, **kwargs: object):
            resolved = path.resolve(strict=False)
            if resolved in targets:
                read_counts[targets[resolved]] += 1
            return real_open(path, *args, **kwargs)

        with mock.patch.object(Path, "open", new=tracking_open):
            verified = self._verify_with_launch_recipe_replay(consumption_path)
        self.assertEqual(verified["status"], "PASS")
        self.assertEqual(
            read_counts,
            {
                "receipt": 1,
                "sidecar": 1,
                "source": 1,
                "manifest": 1,
                "environment": 1,
                "chain": 1,
            },
        )

    def test_verify_consumed_launch_refuses_each_oversized_artifact(self) -> None:
        cases = {
            "receipt": readiness._LAUNCH_BINDING_RECEIPT_MAX_BYTES,
            "sidecar": readiness._LAUNCH_BINDING_SIDECAR_MAX_BYTES,
            "source": readiness._LAUNCH_BINDING_SOURCE_MAX_BYTES,
            "manifest": readiness._LAUNCH_BINDING_MANIFEST_MAX_BYTES,
            "environment": readiness._LAUNCH_BINDING_ENVIRONMENT_MAX_BYTES,
            "chain": readiness._LAUNCH_BINDING_CHAIN_MAX_BYTES,
        }
        for name, cap in cases.items():
            fixture = LaunchConsumptionV2Tests(
                methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
            )
            fixture.setUp()
            try:
                result = fixture._consume()
                consumption_path = Path(str(result["consumption_path"]))
                target = fixture._launch_recipe_artifact_paths()[name]
                with target.open("r+b") as handle:
                    handle.truncate(cap + 1)
                content_reads = 0
                real_open = Path.open

                class CountingHandle:
                    def __init__(self, handle: object) -> None:
                        self.handle = handle

                    def __enter__(self) -> "CountingHandle":
                        return self

                    def __exit__(self, *args: object) -> None:
                        self.handle.close()

                    def fileno(self) -> int:
                        return self.handle.fileno()

                    def read(self, size: int = -1) -> bytes:
                        nonlocal content_reads
                        content_reads += 1
                        return self.handle.read(size)

                def tracking_open(path: Path, *args: object, **kwargs: object):
                    handle = real_open(path, *args, **kwargs)
                    if path.resolve(strict=False) == target.resolve(strict=False):
                        return CountingHandle(handle)
                    return handle

                with self.subTest(artifact=name), mock.patch.object(
                    Path, "open", new=tracking_open
                ):
                    with self.assertRaises(readiness.LaunchLineageError) as caught:
                        fixture._verify_with_launch_recipe_replay(consumption_path)
                self.assertEqual(
                    caught.exception.reason_code, "launch_binding_mismatch"
                )
                self.assertIn(
                    caught.exception.reason_code,
                    readiness.LAUNCH_LINEAGE_REASON_CODES,
                )
                self.assertEqual(content_reads, 0)
            finally:
                fixture.doCleanups()

    def test_exactly_capped_chain_authenticates_at_consume_and_verify(self) -> None:
        self.chain_path.write_bytes(
            b"#" * readiness._LAUNCH_BINDING_CHAIN_MAX_BYTES
        )
        self._install_attested_launch_recipe()
        result = self._consume()
        self.assertEqual(result["status"], "CONSUMED")
        verified = self._verify_with_launch_recipe_replay(
            Path(str(result["consumption_path"]))
        )
        self.assertEqual(verified["status"], "PASS")

    def test_launch_recipe_oversize_refuses_before_content_read(self) -> None:
        cases = {
            "receipt": readiness._LAUNCH_BINDING_RECEIPT_MAX_BYTES,
            "sidecar": readiness._LAUNCH_BINDING_SIDECAR_MAX_BYTES,
            "source": readiness._LAUNCH_BINDING_SOURCE_MAX_BYTES,
        }
        for name, cap in cases.items():
            fixture = LaunchConsumptionV2Tests(
                methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
            )
            fixture.setUp()
            try:
                target = fixture._launch_recipe_artifact_paths()[name]
                with target.open("r+b") as handle:
                    handle.truncate(cap + 1)
                inputs = fixture._consumer_inputs()
                content_reads = 0
                real_open = Path.open

                class CountingHandle:
                    def __init__(self, handle: object) -> None:
                        self.handle = handle

                    def __enter__(self) -> "CountingHandle":
                        return self

                    def __exit__(self, *args: object) -> None:
                        self.handle.close()

                    def fileno(self) -> int:
                        return self.handle.fileno()

                    def read(self, size: int = -1) -> bytes:
                        nonlocal content_reads
                        content_reads += 1
                        return self.handle.read(size)

                def tracking_open(path: Path, *args: object, **kwargs: object):
                    handle = real_open(path, *args, **kwargs)
                    if path.resolve(strict=False) == target.resolve(strict=False):
                        return CountingHandle(handle)
                    return handle

                with self.subTest(artifact=name), mock.patch.object(
                    Path, "open", new=tracking_open
                ):
                    with self.assertRaises(readiness.LaunchLineageError) as caught:
                        fixture._invoke_consumer(inputs)
                self.assertEqual(
                    caught.exception.reason_code, "launch_binding_mismatch"
                )
                self.assertEqual(content_reads, 0)
            finally:
                fixture.doCleanups()

    def test_launch_recipe_memory_error_is_normalized(self) -> None:
        inputs = self._consumer_inputs()
        with mock.patch.object(
            readiness,
            "_read_launch_binding_artifact",
            side_effect=MemoryError("injected allocation refusal"),
        ):
            with self.assertRaises(readiness.LaunchLineageError) as caught:
                self._invoke_consumer(inputs)
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_private_consumer_requires_complete_matching_context_before_write(
        self,
    ) -> None:
        other_window_root = Path(self.temporary.name) / "other-window"
        other_window_root.mkdir()
        cases = {
            "missing_arm": {"authenticated_arm_receipt": None},
            "missing_manifest": {"authenticated_launch_manifest": None},
            "missing_window_root": {"window_plan_root": None},
            "arm_digest": {"arm_receipt_sha256": "0" * 64},
            "manifest_digest": {"launch_manifest_sha256": "0" * 64},
            "window_root": {"window_plan_root": other_window_root},
            "environment_digest": {"window_environment_sha256": "0" * 64},
            "chain_digest": {"window_chain_sha256": "0" * 64},
            "exec_argv": {"exec_argv": ["/bin/false"]},
        }
        consumption_dir = (
            self.custody / self.pack.name / "arm_readiness.consumptions"
        )
        for name, overrides in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(
                    (readiness.ArmReadinessError, readiness.LaunchLineageError)
                ) as caught:
                    self._consume(**overrides)
                self.assertIn(
                    caught.exception.reason_code,
                    readiness.READINESS_REASON_CODES
                    | readiness.LAUNCH_LINEAGE_REASON_CODES,
                )
                self.assertFalse(consumption_dir.exists())

        with self.assertRaises(TypeError):
            readiness._consume_launch_capability(
                self.pack,
                self.arm_path,
                self.custody,
            )
        self.assertFalse(consumption_dir.exists())

    def test_campaign_config_membership_and_completion_absence_are_enforced(self) -> None:
        consumption_path, _settled = self._settle()
        config_path = self.pack / "member.json"
        config_path.write_text('{"run_id":"member"}\n')
        authenticated = self._authenticate_campaign(
            Path(self.arm["arm_context"]["claim_runs_root"]),
            config_paths=(config_path,),
        )
        self.assertEqual(authenticated["pack_root"], str(self.pack.resolve()))
        copied = Path(self.temporary.name) / "copied-member.json"
        copied.write_bytes(config_path.read_bytes())
        with self.assertRaises(readiness.LaunchLineageError) as outside:
            self._authenticate_campaign(
                Path(self.arm["arm_context"]["claim_runs_root"]),
                config_paths=(copied,),
            )
        self.assertEqual(outside.exception.reason_code, "launch_binding_mismatch")
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "completion"
            )
        with self.assertRaises(readiness.LaunchLineageError) as completed:
            self._authenticate_campaign(
                Path(self.arm["arm_context"]["claim_runs_root"]),
                config_paths=(config_path,),
            )
        self.assertEqual(completed.exception.reason_code, "launch_binding_mismatch")

    def test_writer_auth_does_not_reapply_short_arm_expiration(self) -> None:
        self.arm["valid_until_monotonic_ns"] = 200
        arm_raw = readiness.render_json(self.arm)
        self.arm_path.write_bytes(arm_raw)
        self.arm_path.with_name(f"{self.arm_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(arm_raw).hexdigest(), self.arm_path.name
            )
        )
        token = b"e" * 32
        with mock.patch.object(readiness.time, "monotonic_ns", return_value=100):
            result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ), mock.patch.object(
            readiness.time, "monotonic_ns", side_effect=(110, 120)
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
        with mock.patch.object(readiness.time, "monotonic_ns", return_value=10_000):
            authenticated = self._authenticate_campaign(
                Path(self.arm["arm_context"]["claim_runs_root"])
            )
        self.assertEqual(authenticated["authentication"]["consumption_sha256"], result["consumption_sha256"])

    def test_missing_consumption_sidecar_is_machine_refusal(self) -> None:
        result = self._consume()
        consumption_path = Path(str(result["consumption_path"]))
        consumption_path.with_name(f"{consumption_path.name}.sha256").unlink()
        with self.assertRaises(readiness.LaunchLineageError) as caught:
            readiness.authenticate_launch_lineage(
                {
                    "schema_version": readiness.LAUNCH_LINEAGE_SCHEMA,
                    "collection_boot_session_id": TEST_BOOT_SESSION_ID,
                    "pack_id": self.arm["pack"]["pack_id"],
                    "plan_id": self.arm["pack"]["plan_id"],
                    "window_id": self.arm["pack"]["window_id"],
                    "bracket_session_id": self.arm["arm_context"]["bracket_session_id"],
                    "consumption": {
                        "path": str(consumption_path),
                        "sha256": str(result["consumption_sha256"]),
                    },
                    "start": None,
                    "settle": None,
                    "completion": None,
                },
                require_completion=False,
            )
        self.assertEqual(caught.exception.reason_code, "launch_consumption_missing")

    def test_primary_remains_burned_when_post_claim_directory_fsync_fails(self) -> None:
        failure = arm_readiness_error = readiness.ArmReadinessError(
            "readiness_io_error", "injected post-claim fsync failure"
        )
        with mock.patch.object(
            readiness,
            "_fsync_directory",
            side_effect=[None, failure],
        ):
            with self.assertRaises(readiness.ArmReadinessError) as caught:
                self._consume()
        self.assertIs(caught.exception, arm_readiness_error)
        consumption_path = (
            self.custody
            / self.pack.name
            / "arm_readiness.consumptions"
            / "arm-0001.consumed.json"
        )
        self.assertTrue(consumption_path.is_file())
        self.assertFalse(
            consumption_path.with_name(f"{consumption_path.name}.sha256").exists()
        )
        with self.assertRaises(readiness.ArmReadinessError) as replay:
            self._consume()
        self.assertEqual(replay.exception.reason_code, "readiness_record_consumed")

    def test_primary_remains_burned_when_sidecar_publication_fails(self) -> None:
        real_write = readiness._exclusive_write
        calls = 0

        def injected(path: Path, raw: bytes) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise readiness.ArmReadinessError(
                    "readiness_io_error", "injected sidecar failure"
                )
            real_write(path, raw)

        with mock.patch.object(readiness, "_exclusive_write", side_effect=injected):
            with self.assertRaises(readiness.ArmReadinessError):
                self._consume()
        consumption_path = (
            self.custody
            / self.pack.name
            / "arm_readiness.consumptions"
            / "arm-0001.consumed.json"
        )
        self.assertTrue(consumption_path.is_file())
        with self.assertRaises(readiness.ArmReadinessError) as replay:
            self._consume()
        self.assertEqual(replay.exception.reason_code, "readiness_record_consumed")

    def test_completed_sidecar_remains_burned_when_final_fsync_fails(self) -> None:
        failure = readiness.ArmReadinessError(
            "readiness_io_error", "injected final directory fsync failure"
        )
        with mock.patch.object(
            readiness,
            "_fsync_directory",
            side_effect=[None, None, failure],
        ):
            with self.assertRaises(readiness.ArmReadinessError) as caught:
                self._consume()
        self.assertIs(caught.exception, failure)
        consumption_path = (
            self.custody
            / self.pack.name
            / "arm_readiness.consumptions"
            / "arm-0001.consumed.json"
        )
        self.assertTrue(consumption_path.is_file())
        self.assertTrue(
            consumption_path.with_name(f"{consumption_path.name}.sha256").is_file()
        )
        with self.assertRaises(readiness.ArmReadinessError) as replay:
            self._consume()
        self.assertEqual(replay.exception.reason_code, "readiness_record_consumed")

    def test_chain_death_after_start_is_lifecycle_incomplete(self) -> None:
        token = b"d" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            started = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
        with self.assertRaises(readiness.LaunchLineageError) as incomplete:
            readiness.authenticate_launch_lineage(
                started["launch_lineage"], require_completion=False
            )
        self.assertEqual(
            incomplete.exception.reason_code, "launch_lifecycle_incomplete"
        )

    def test_missing_completion_and_identity_mismatch_are_discriminated(self) -> None:
        token = b"q" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            settled = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
        with self.assertRaises(readiness.LaunchLineageError) as incomplete:
            readiness.authenticate_launch_lineage(
                settled["launch_lineage"], require_completion=True
            )
        self.assertEqual(
            incomplete.exception.reason_code, "launch_lifecycle_incomplete"
        )
        mismatched = dict(settled["launch_lineage"])
        mismatched["pack_id"] = "another-pack"
        with self.assertRaises(readiness.LaunchLineageError) as mismatch:
            readiness.authenticate_launch_lineage(
                mismatched, require_completion=False
            )
        self.assertEqual(mismatch.exception.reason_code, "launch_binding_mismatch")

    def test_later_arm_successor_does_not_destroy_historical_lineage(self) -> None:
        token = b"s" * 32
        result = self._consume(token)
        consumption_path = Path(str(result["consumption_path"]))
        with mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "start", handoff_token=token
            )
            readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "settle"
            )
            completed = readiness.record_launch_lifecycle_event(
                self.pack, consumption_path, "completion"
            )

        original_raw = self.arm_path.read_bytes()
        successor = copy.deepcopy(self.arm)
        successor["receipt_id"] = "arm-0002"
        successor["supersedes"] = {
            "receipt_id": self.arm["receipt_id"],
            "receipt_path": f"arm_readiness.receipts/{self.arm_path.name}",
            "receipt_sha256": hashlib.sha256(original_raw).hexdigest(),
            "pack_id": self.arm["pack"]["pack_id"],
            "pack_sha256": self.arm["pack"]["pack_sha256"],
        }
        successor_path = self.arm_path.with_name("arm-0002.json")
        successor_raw = readiness.render_json(successor)
        successor_path.write_bytes(successor_raw)
        successor_path.with_name(f"{successor_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(successor_raw).hexdigest(), successor_path.name
            )
        )

        historical = readiness.authenticate_launch_lineage(
            completed["launch_lineage"], require_completion=True
        )
        self.assertEqual(
            historical["consumption_sha256"], result["consumption_sha256"]
        )
        with mock.patch.object(
            readiness, "_pack_record", return_value=self.arm["pack"]
        ), mock.patch.object(
            readiness,
            "_derive_arm_semantics_for_verification",
            return_value=(self.arm["rows"], self.arm["refusals"]),
        ), mock.patch.object(
            readiness,
            "_current_boot_session_id",
            return_value=TEST_BOOT_SESSION_ID,
        ):
            with self.assertRaises(readiness.LaunchLineageError) as launch_entry:
                readiness.verify_consumed_launch(self.pack, consumption_path)
        self.assertEqual(
            launch_entry.exception.reason_code, "launch_binding_mismatch"
        )


class ArmPackReplayComparisonTests(unittest.TestCase):
    def _assert_verify_side_pack_refusal(
        self,
        pack: Path,
        custody_pack_root: Path,
        receipt: dict,
        expected_detail: str,
    ) -> None:
        with self.assertRaises(readiness.ArmReadinessError) as caught:
            readiness._derive_arm_semantics_for_verification(
                pack,
                custody_pack_root,
                receipt,
            )
        self.assertEqual(
            caught.exception.reason_code,
            "readiness_pack_digest_mismatch",
        )
        self.assertEqual(str(caught.exception), expected_detail)

    def _consumption_for_arm(self, arm_path: Path) -> tuple[dict, Path]:
        raw = arm_path.read_bytes()
        return (
            {
                "arm_receipt": {
                    "receipt_id": arm_path.stem,
                    "path": f"arm_readiness.receipts/{arm_path.name}",
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            },
            arm_path.parent.parent
            / "arm_readiness.consumptions"
            / f"{arm_path.stem}.consumed.json",
        )

    def _relocated_fixture(
        self, *, different_repository_relative_path: bool
    ) -> tuple[Path, Path, dict, Path]:
        from tests.test_arm_readiness_lifecycle import git, make_go_fixture

        temporary, repository, pack, _custody, arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        relocated_repository = Path(temporary.name) / "relocated-repository"
        git(
            Path(temporary.name),
            "clone",
            "-q",
            "--no-local",
            str(repository),
            str(relocated_repository),
        )
        git(relocated_repository, "config", "user.email", "tests@joulewise.invalid")
        git(relocated_repository, "config", "user.name", "JouleWise tests")
        git(relocated_repository, "config", "gc.auto", "0")
        git(relocated_repository, "config", "maintenance.auto", "false")
        relocated_pack = relocated_repository / pack.relative_to(repository)
        if different_repository_relative_path:
            destination = relocated_repository / "relocated" / pack.name
            destination.parent.mkdir()
            git(
                relocated_repository,
                "mv",
                relocated_pack.relative_to(relocated_repository).as_posix(),
                destination.relative_to(relocated_repository).as_posix(),
            )
            git(relocated_repository, "commit", "-qm", "relocate pack within repo")
            relocated_pack = destination

        # The arm carries the original canonical spelling. Replacing that pack
        # directory with a symlink makes strict=True resolve to the relocated
        # bytes, which is the one reachable location-only route to the fieldwise
        # comparison after the caller-expected-root check.
        shutil.rmtree(pack)
        pack.symlink_to(relocated_pack, target_is_directory=True)
        consumption, consumption_path = self._consumption_for_arm(arm_path)
        return pack, relocated_pack, consumption, consumption_path

    def test_successor_replay_accepts_same_repository_relative_relocation(
        self,
    ) -> None:
        recorded_path, relocated_pack, consumption, consumption_path = (
            self._relocated_fixture(different_repository_relative_path=False)
        )

        try:
            _arm, _arm_path, resolved_root, authenticated_pack = (
                readiness._replay_consumed_arm(
                    relocated_pack,
                    consumption,
                    consumption_path,
                    require_current_boot=False,
                    require_unexpired=False,
                    replay_arm_semantics=False,
                )
            )
        except readiness.LaunchLineageError as exc:
            self.fail(
                "same repository-relative relocation refused: "
                f"{exc.reason_code}: {exc}"
            )

        self.assertNotEqual(str(recorded_path), str(resolved_root))
        self.assertEqual(resolved_root, relocated_pack.resolve())
        self.assertEqual(
            authenticated_pack["pack_root"], str(relocated_pack.resolve())
        )

    def test_successor_replay_names_repository_relative_location_difference(
        self,
    ) -> None:
        _recorded_path, relocated_pack, consumption, consumption_path = (
            self._relocated_fixture(different_repository_relative_path=True)
        )

        with self.assertRaises(readiness.LaunchLineageError) as caught:
            readiness._replay_consumed_arm(
                relocated_pack,
                consumption,
                consumption_path,
                require_current_boot=False,
                require_unexpired=False,
                replay_arm_semantics=False,
            )

        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")
        self.assertEqual(
            str(caught.exception),
            "consumed arm pack repository-relative location differs from the authenticated pack location",
        )

    def test_replay_content_difference_keeps_authenticated_bytes_detail(self) -> None:
        from tests.test_arm_readiness_lifecycle import make_go_fixture

        temporary, _repository, pack, _custody, arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        arm = json.loads(arm_path.read_text())
        arm["pack"]["plan_id"] = "different-plan"
        raw = readiness.render_json(arm)
        arm_path.write_bytes(raw)
        arm_path.with_name(f"{arm_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(hashlib.sha256(raw).hexdigest(), arm_path.name)
        )
        consumption, consumption_path = self._consumption_for_arm(arm_path)

        with self.assertRaises(readiness.LaunchLineageError) as caught:
            readiness._replay_consumed_arm(
                pack,
                consumption,
                consumption_path,
                require_current_boot=False,
                require_unexpired=False,
                replay_arm_semantics=False,
            )

        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")
        self.assertEqual(
            str(caught.exception),
            "consumed arm pack record differs from authenticated pack bytes",
        )

    def test_verify_side_pack_comparison_names_content_or_keyset_difference(
        self,
    ) -> None:
        from tests.test_arm_readiness_lifecycle import make_go_fixture

        temporary, _repository, pack, custody, arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        expected_detail = (
            "arm receipt pack binding differs from committed pack bytes"
        )
        for mutation in ("content", "keyset"):
            with self.subTest(mutation=mutation):
                receipt = json.loads(arm_path.read_text())
                if mutation == "content":
                    receipt["pack"]["plan_id"] = "different-plan"
                else:
                    receipt["pack"].pop("plan_id")
                self._assert_verify_side_pack_refusal(
                    pack,
                    custody / pack.name,
                    receipt,
                    expected_detail,
                )

    def test_verify_side_pack_comparison_names_successor_relative_location_difference(
        self,
    ) -> None:
        from tests.test_arm_readiness_lifecycle import make_go_fixture

        temporary, _repository, pack, custody, arm_path = make_go_fixture()
        self.addCleanup(temporary.cleanup)
        receipt = json.loads(arm_path.read_text())
        receipt["pack"]["pack_root"] = (
            f"/historical/checkout/relocated/{pack.name}"
        )

        self._assert_verify_side_pack_refusal(
            pack,
            custody / pack.name,
            receipt,
            "arm receipt repository-relative pack location differs",
        )

    def test_verify_side_pack_comparison_names_legacy_location_binding(
        self,
    ) -> None:
        from tests.test_arm_readiness_lifecycle import make_go_fixture

        temporary, _repository, pack, custody, arm_path = make_go_fixture(
            "d117_floor_qwen25_1p5b_v3"
        )
        self.addCleanup(temporary.cleanup)
        receipt = json.loads(arm_path.read_text())
        receipt["pack"]["pack_root"] = (
            f"/historical/checkout/configs/campaigns/{pack.name}"
        )

        self._assert_verify_side_pack_refusal(
            pack,
            custody / pack.name,
            receipt,
            "arm receipt archival location differs; replay below the registry's family-publication generation threshold is location-bound (see the 2026-08-20 ruling)",
        )


class LaunchPackConfigInventoryTests(unittest.TestCase):
    def test_real_pack_inventory_authenticates_exact_member_bytes(self) -> None:
        pack = (
            Path(__file__).resolve().parents[1]
            / "configs/campaigns/d117_floor_qwen25_1p5b_v1"
        )
        inventory = readiness._authenticated_pack_config_inventory(pack)
        relative = "01_phase_decode_absolute/d117f15-df-ph-decode-abs-r01.json"
        self.assertEqual(
            inventory[relative],
            hashlib.sha256((pack / relative).read_bytes()).hexdigest(),
        )


class R1ArmLifecycleGateTests(unittest.TestCase):
    def _discover_one_r1_receipt(
        self, kind: str, freshness_class: str, *, status: str, deadline: int
    ) -> tuple[list[dict], dict[str, dict], list[dict]]:
        from tests.test_arm_readiness_evidence import lifecycle_registry

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        pack = root / "pack"
        pack.mkdir()
        custody_pack = root / "custody" / pack.name
        evidence_dir = custody_pack / "arm_readiness.evidence"
        evidence_dir.mkdir(parents=True)
        source_raw = b"production-boundary-source\n"
        (custody_pack / "source.json").write_bytes(source_raw)
        receipt = sample_evidence()
        receipt.update(
            {
                "evidence_id": f"test-{kind.lower()}",
                "kind": kind,
                "status": status,
                "boot_session_id": TEST_BOOT_SESSION_ID,
                "valid_until_monotonic_ns": deadline,
                "reason_codes": (
                    [] if status == "PASS" else ["readiness_dependency_refused"]
                ),
            }
        )
        receipt["facts"][0].update(
            {
                "fact_id": "test.production-boundary.v1",
                "source_kind": "PROBE",
                "source_path": "source.json",
                "source_sha256": hashlib.sha256(source_raw).hexdigest(),
            }
        )
        raw = readiness.render_json(receipt)
        receipt_path = evidence_dir / "evidence-test.json"
        receipt_path.write_bytes(raw)
        receipt_path.with_name(f"{receipt_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(hashlib.sha256(raw).hexdigest(), receipt_path.name)
        )
        registry = lifecycle_registry(
            policies=(
                {
                    "kind": kind,
                    "freshness_class": freshness_class,
                    "freshness_policy_id": f"test.{kind.lower()}.v1",
                    "horizon_ns": 1_000,
                    "environment_comparison": "NOT_APPLICABLE",
                },
            )
        )
        return readiness._discover_evidence(
            pack,
            custody_pack,
            pack_sha256=None,
            head_commit=None,
            boot_session_id=TEST_BOOT_SESSION_ID,
            now_monotonic_ns=100,
            lifecycle_registry=registry,
        )

    def test_production_discovery_enforces_time_and_session_lifecycles(self) -> None:
        _items, _receipts, time_refusals = self._discover_one_r1_receipt(
            "CLOCK_PROBE", "TIME_BOUND", status="PASS", deadline=99
        )
        self.assertEqual(
            [item["code"] for item in time_refusals], ["readiness_record_expired"]
        )
        _items, _receipts, session_refusals = self._discover_one_r1_receipt(
            "LEDGER_RESERVATION",
            "SESSION_STATE_BOUND",
            status="REFUSE",
            deadline=200,
        )
        self.assertEqual(
            [item["code"] for item in session_refusals],
            ["readiness_dependency_refused"],
        )

    def test_code_class_dispatcher_applies_each_ruled_lifecycle(self) -> None:
        now = 100
        timed = {
            "boot_session_id": TEST_BOOT_SESSION_ID,
            "valid_until_monotonic_ns": 200,
        }
        readiness.validate_r1_class_lifecycle(
            {},
            "DOCTRINE_PIN",
            current_boot_session_id=TEST_BOOT_SESSION_ID,
            now_monotonic_ns=now,
        )
        for kind in ("PACK_AUTHENTICATION", "CLOCK_PROBE"):
            with self.subTest(kind=kind):
                readiness.validate_r1_class_lifecycle(
                    timed,
                    kind,
                    current_boot_session_id=TEST_BOOT_SESSION_ID,
                    now_monotonic_ns=now,
                )
        readiness.validate_r1_class_lifecycle(
            timed,
            "LEDGER_RESERVATION",
            current_boot_session_id=TEST_BOOT_SESSION_ID,
            now_monotonic_ns=now,
            semantic_state_valid=True,
        )
        readiness.validate_r1_class_lifecycle(
            timed,
            "ARM_CAPABILITY",
            current_boot_session_id=TEST_BOOT_SESSION_ID,
            now_monotonic_ns=now,
            semantic_state_valid=True,
            capability_consumed=False,
        )
        with self.assertRaises(readiness.ArmReadinessError) as expired:
            readiness.validate_r1_class_lifecycle(
                timed | {"valid_until_monotonic_ns": 99},
                "CLOCK_PROBE",
                current_boot_session_id=TEST_BOOT_SESSION_ID,
                now_monotonic_ns=now,
            )
        self.assertEqual(expired.exception.reason_code, "readiness_record_expired")
        with self.assertRaises(readiness.ArmReadinessError) as state:
            readiness.validate_r1_class_lifecycle(
                timed,
                "LEDGER_RESERVATION",
                current_boot_session_id=TEST_BOOT_SESSION_ID,
                now_monotonic_ns=now,
                semantic_state_valid=False,
            )
        self.assertEqual(state.exception.reason_code, "readiness_dependency_refused")
        with self.assertRaises(readiness.ArmReadinessError) as consumed:
            readiness.validate_r1_class_lifecycle(
                timed,
                "ARM_CAPABILITY",
                current_boot_session_id=TEST_BOOT_SESSION_ID,
                now_monotonic_ns=now,
                semantic_state_valid=True,
                capability_consumed=True,
            )
        self.assertEqual(consumed.exception.reason_code, "readiness_record_consumed")

    def test_temporal_budget_evaluates_only_the_time_bound_t0_set(self) -> None:
        from tests.test_arm_readiness_evidence import lifecycle_registry

        policies = tuple(
            {
                "kind": kind,
                "freshness_class": freshness_class,
                "freshness_policy_id": f"test.{kind.lower()}.v1",
                "horizon_ns": (None if freshness_class == "RE_DERIVABLE" else 1_000),
                "environment_comparison": (
                    "NOT_APPLICABLE"
                    if freshness_class != "EXECUTION_BOUND"
                    else "test-only"
                ),
            }
            for kind, freshness_class in (
                ("DOCTRINE_PIN", "RE_DERIVABLE"),
                ("CLOCK_PROBE", "TIME_BOUND"),
                ("LEDGER_RESERVATION", "SESSION_STATE_BOUND"),
            )
        )
        registry = lifecycle_registry(policies=policies)
        now = 1_000
        receipts = [
            {"kind": "CLOCK_PROBE", "evidence_id": "clock", "valid_until_monotonic_ns": now + 70_000_000_000},
            {"kind": "LEDGER_RESERVATION", "evidence_id": "ledger", "valid_until_monotonic_ns": now + 1},
            {"kind": "PACK_AUTHENTICATION", "evidence_id": "pack", "valid_until_monotonic_ns": now + 1},
        ]
        self.assertEqual(
            readiness.validate_r1_temporal_budget(
                receipts, registry, now_monotonic_ns=now
            ),
            now + 70_000_000_000,
        )
        receipts[0]["valid_until_monotonic_ns"] = now + 59_000_000_000
        with self.assertRaises(readiness.EvidenceLifecycleError) as caught:
            readiness.validate_r1_temporal_budget(
                receipts, registry, now_monotonic_ns=now
            )
        self.assertEqual(caught.exception.role, "TEMPORAL_BUDGET")

        wrong_class = lifecycle_registry(
            policies=(
                {
                    "kind": "CLOCK_PROBE",
                    "freshness_class": "EXECUTION_BOUND",
                    "freshness_policy_id": "test.clock.override.v1",
                    "horizon_ns": 1_000,
                    "environment_comparison": "ED_RESERVED:comparison",
                },
            )
        )
        with self.assertRaises(readiness.ArmReadinessError) as override:
            readiness.validate_r1_temporal_budget(
                receipts, wrong_class, now_monotonic_ns=now
            )
        self.assertEqual(
            override.exception.reason_code, "readiness_row_registry_mismatch"
        )
        self.assertIn("CLASS_MISMATCH", str(override.exception))

    def test_terminal_review_tree_binding_is_unconditional(self) -> None:
        source = {
            "schema_version": readiness._T0_EVIDENCE_SOURCE_SCHEMA,
            "head_tree_oid": "a" * 40,
        }
        readiness.validate_terminal_review_head_tree(source, "a" * 40)
        with self.assertRaises(readiness.ArmReadinessError) as caught:
            readiness.validate_terminal_review_head_tree(source, "b" * 40)
        self.assertEqual(
            caught.exception.reason_code, "readiness_terminal_review_missing"
        )


if __name__ == "__main__":
    unittest.main()
