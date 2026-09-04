from __future__ import annotations

import copy
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as arm_readiness
import joulewise.calibration_ledger as calibration_ledger
from joulewise import reduce as reduce_module
from joulewise.analysis_engine.inputs import (
    BundleEvidence,
    _enforce_registered_realized_identity,
)
from joulewise.bundle_read import BundleReader
from joulewise.calibration_exits import RefusalCode
from tests.test_analysis_inputs import _metadata_for, _scalar_config


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class SilentRefusalCounterfactualTests(unittest.TestCase):
    def test_empty_committed_pack_refuses_with_specific_code(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            pack = repository / "pack"
            pack.mkdir(parents=True)
            (repository / "tracked.txt").write_text("outside pack\n", encoding="utf-8")
            subprocess.run(("git", "init", "-q"), cwd=repository, check=True)
            subprocess.run(
                ("git", "config", "user.email", "tests@joulewise.invalid"),
                cwd=repository,
                check=True,
            )
            subprocess.run(
                ("git", "config", "user.name", "JouleWise tests"),
                cwd=repository,
                check=True,
            )
            subprocess.run(("git", "add", "."), cwd=repository, check=True)
            subprocess.run(
                ("git", "commit", "-qm", "fixture"), cwd=repository, check=True
            )

            with self.assertRaises(arm_readiness.ArmReadinessError) as caught:
                arm_readiness.committed_pack_tree_sha256(pack)

        self.assertEqual(
            caught.exception.reason_code, "readiness_pack_not_committed"
        )

    def test_changed_bound_launch_bytes_refuse_with_specific_code(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact = Path(temporary) / "window-chain.zsh"
            artifact.write_bytes(b"original\n")
            reference = {
                "path": str(artifact),
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            }
            artifact.write_bytes(b"changed\n")

            with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                arm_readiness._read_exact_launch_reference(
                    reference,
                    max_bytes=1024,
                    label="test launch artifact",
                )

        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_realized_identity_disagreement_refuses_with_specific_code(self) -> None:
        config = _scalar_config()
        metadata = _metadata_for(config, requested_tokens=512)
        changed_config = copy.deepcopy(config)
        changed_config["model"]["revision"] = "different-revision"
        changed_metadata = _metadata_for(changed_config, requested_tokens=512)

        def evidence(entry_id: str, raw_config: dict, raw_metadata: dict) -> BundleEvidence:
            return BundleEvidence(
                entry={"entry_id": entry_id},
                bundle_id=entry_id,
                relative_path=entry_id,
                path=Path(entry_id),
                summary={"status": "succeeded"},
                metadata=raw_metadata,
                raw_config=raw_config,
                strict_problems=(),
                base_reason_codes=(),
                config_sha256="a" * 64,
                expected_config_sha256="a" * 64,
                summary_sha256="b" * 64,
                replacement_classification="registered",
                inclusion_status="included",
            )

        evidence_by_entry = {
            "entry-a": evidence("entry-a", config, metadata),
            "entry-b": evidence("entry-b", changed_config, changed_metadata),
        }
        manifest = {
            "schema_version": "joulewise.analysis_manifest.v2",
            "entries": [
                {"entry_id": "entry-a", "model_tag": "model-a"},
                {"entry_id": "entry-b", "model_tag": "model-a"},
            ],
        }

        _enforce_registered_realized_identity(manifest, evidence_by_entry)

        for row in evidence_by_entry.values():
            self.assertEqual(row.base_reason_codes, ("config_hash_mismatch",))
            self.assertEqual(row.inclusion_status, "excluded")

    def test_physical_ledger_rollback_keeps_specific_code_at_readiness_sites(
        self,
    ) -> None:
        snapshot = calibration_ledger.CalibrationLedgerSnapshot(
            ledger_schema=calibration_ledger.LEDGER_SCHEMA,
            ledger_path=Path("ledger.jsonl"),
            head_sequence=0,
            head_digest=calibration_ledger.GENESIS_DIGEST,
            receipts=(),
            observations=(),
            refusal_reasons=(RefusalCode.LEDGER_HEAD_MISMATCH.value,),
            committed_head_sequence=1,
            committed_head_digest="a" * 64,
        )
        inspection = calibration_ledger.CalibrationLedgerInspection(
            state="clean",
            ledger_id="ledger-fixture",
            head_sequence=0,
            head_digest=calibration_ledger.GENESIS_DIGEST,
            valid_end_offset=0,
            residue_start_offset=0,
            residue_length=0,
            residue_sha256=hashlib.sha256(b"").hexdigest(),
            active_operation_id=None,
            active_operation_key=None,
            target_core_sha256=None,
        )
        with mock.patch.object(
            calibration_ledger,
            "load_calibration_ledger_snapshot",
            return_value=snapshot,
        ), mock.patch.object(
            calibration_ledger,
            "inspect_calibration_ledger",
            return_value=inspection,
        ), mock.patch.object(
            calibration_ledger,
            "writer_lease_is_live",
            return_value=False,
        ):
            for phase in ("pre-slot", "terminal"):
                with self.subTest(phase=phase):
                    readiness = calibration_ledger.calibration_readiness(
                        Path("ledger.jsonl"),
                        Path("head.json"),
                        phase=phase,
                        require_committed_pin=False,
                    )
                    self.assertEqual(
                        readiness.refusal_code, RefusalCode.LEDGER_ROLLBACK
                    )

    def test_unregistered_anchor_reconstruction_refuses_before_fallback(self) -> None:
        fixture = REPOSITORY_ROOT / "tests" / "fixtures" / "d078_r01"
        reader = BundleReader(fixture)
        metadata = copy.deepcopy(reader.metadata())
        metadata["uncertainty_evidence"]["clock_anchor"]["method"] = (
            "powermetrics_not_a_registered_anchor_method_v9"
        )

        context = reduce_module._derive_anchor_context(
            reader, metadata, reducer_version="0.5.2"
        )

        self.assertTrue(context.unresolved)
        self.assertEqual(context.detail, "anchor_method_unregistered")
        self.assertIsNone(context.curve)


if __name__ == "__main__":
    unittest.main()
