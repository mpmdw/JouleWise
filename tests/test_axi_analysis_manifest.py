from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.analysis_engine.registry import (
    AnalysisManifestError,
    canonical_json_bytes,
    calculate_manifest_id,
    normalize_technical_invalid_reason,
    normalized_json_bytes,
    pairing_projection_sha256,
    registry_semantic_sha256,
    render_dispatch_receipt,
    render_strict_validation_evidence,
    sha256_bytes,
    validate_analysis_manifest_v2,
    validate_analysis_registry_v2,
    validate_attempt_ledger,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "axi_ap_spec"
GOLDEN = ROOT / "tests" / "goldens"
AXI_VALID_BUNDLE = ROOT / "tests" / "fixtures" / "axi_valid_burst"
ROSTER_SHA = "502b0c4577aee495623a33332a26be956b8b3d01d1cb3d0d225382f6bc2130f9"
AP2_REGISTRY_SHA = "9defb37454aec95ff8a40df60f50edcca8e45d17d03f35364f07571d31475b01"
AP2_ONE_MODEL_MANIFEST_SHA = "623f82c9a7aa317195ab2120e63ca0249b57cab093d586447cc259bbf1814216"


def load_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def evidence_for(name: str) -> tuple[dict, dict, bytes, dict[str, bytes], bytes]:
    registry_name = "ap_spec_draft_front.v2.json" if name == "draft" else "ap_spec_native_mtp_front.v2.json"
    registry = load_json(ROOT / "configs" / "analysis_registry" / registry_name)
    manifest_path = FIXTURE / f"{name}_analysis_manifest.json"
    manifest = load_json(manifest_path)
    configs = {entry["config"]: (ROOT / entry["config"]).read_bytes() for entry in manifest["entries"]}
    return registry, manifest, manifest_path.read_bytes(), configs, (ROOT / manifest["request_roster"]["path"]).read_bytes()


def reidentify(manifest: dict, registry: dict) -> None:
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    registry["planned_manifest_id"] = manifest["manifest_id"]
    registry["planned_manifest_sha256"] = sha256_bytes(normalized_json_bytes(manifest))


class AxiAnalysisRegistryTests(unittest.TestCase):


    def test_ap2_registry_and_generated_manifest_bytes_are_unchanged(self) -> None:
        registry_path = ROOT / "configs" / "analysis_registry" / "slice_2m_ap2.v1.json"
        self.assertEqual(hashlib.sha256(registry_path.read_bytes()).hexdigest(), AP2_REGISTRY_SHA)
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "generate_matrix.py"),
                    "--base",
                    str(ROOT / "configs" / "examples" / "mac_mlx_local.json"),
                    "--model-tag",
                    "qwen25-1p5b",
                    "--out-dir",
                    tmp,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            generated = Path(tmp, "analysis_manifest.json").read_bytes()
            self.assertEqual(hashlib.sha256(generated).hexdigest(), AP2_ONE_MODEL_MANIFEST_SHA)


class AxiAttemptLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        _, self.manifest, _, _, _ = evidence_for("draft")
        self.bundle_temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.bundle_temp.cleanup)
        self.bundle_store_ordinal = 0

    def finalized_bundles(self, *rows: dict) -> dict[tuple[str, int, str], Path]:
        root = Path(self.bundle_temp.name) / f"store-{self.bundle_store_ordinal}"
        self.bundle_store_ordinal += 1
        result: dict[tuple[str, int, str], Path] = {}
        for row in rows:
            run_id = row["run_id"]
            if run_id is None:
                continue
            key = (row["entry_id"], row["attempt_ordinal"], run_id)
            path = root / row["entry_id"] / f"a{row['attempt_ordinal']}" / run_id
            shutil.copytree(AXI_VALID_BUNDLE, path)
            metadata = load_json(path / "metadata.json")
            metadata["run_id"] = run_id
            (path / "metadata.json").write_bytes(normalized_json_bytes(metadata))
            result[key] = path
        return result

    def receipt(self, *, entry_index: int, attempt: int, run_id: str | None, failed: bool = False) -> dict:
        entry = self.manifest["entries"][entry_index]
        return {
            "schema_version": "joulewise.dispatch_receipt.v1",
            "manifest_id": self.manifest["manifest_id"],
            "entry_id": entry["entry_id"],
            "pair_id": entry["pair_id"],
            "arm": entry["arm"],
            "attempt_ordinal": attempt,
            "dispatch_started": True,
            "transport_status": "failed" if failed else "ok",
            "process_exit_code": 1 if failed else 0,
            "admitted_request_count": 0 if failed else 1,
            "finalized_run_id": run_id,
        }

    @staticmethod
    def row(receipt: dict, *, reason: str | None, reason_hash: str | None, eligible: bool) -> tuple[dict, str, bytes]:
        receipt_bytes = render_dispatch_receipt(receipt)
        receipt_hash = sha256_bytes(receipt_bytes)
        return (
            {
                "schema_version": "joulewise.attempt_ledger.v1",
                "manifest_id": receipt["manifest_id"],
                "entry_id": receipt["entry_id"],
                "pair_id": receipt["pair_id"],
                "arm": receipt["arm"],
                "attempt_ordinal": receipt["attempt_ordinal"],
                "run_id": receipt["finalized_run_id"],
                "dispatch_receipt_sha256": receipt_hash,
                "technical_invalid_reason_code": reason,
                "reason_evidence_sha256": receipt_hash if reason == "dispatch_failed_before_bundle_creation" else reason_hash,
                "eligible_for_analysis": eligible,
            },
            receipt_hash,
            receipt_bytes,
        )

    def test_hand_authored_dispatch_and_strict_evidence_byte_goldens(self) -> None:
        receipt_path = GOLDEN / "axi_dispatch_receipt_failed.json"
        evidence_path = GOLDEN / "axi_strict_validation_evidence.json"
        self.assertEqual(render_dispatch_receipt(load_json(receipt_path)), receipt_path.read_bytes())
        self.assertEqual(render_strict_validation_evidence(load_json(evidence_path)), evidence_path.read_bytes())
        self.assertEqual(sha256_bytes(receipt_path.read_bytes()), "ea63fa60996164cb7673af918760f40f86884b6d92c16c88374b0f806131060c")
        self.assertEqual(sha256_bytes(evidence_path.read_bytes()), "152f4756d8a814f882e37af421c6f916ca13fde7e3726afd1790a1e10e219117")

    def test_strict_evidence_reasons_use_closed_axi_validator_enum(self) -> None:
        evidence = load_json(GOLDEN / "axi_strict_validation_evidence.json")
        evidence["validator_reason_codes"] = ["favorable_energy_outcome"]
        with self.assertRaisesRegex(ValueError, "AXI_VALIDATOR_REASON_CODES"):
            render_strict_validation_evidence(evidence)

    def test_dispatch_failure_then_first_eligible_is_selected(self) -> None:
        failed = self.receipt(entry_index=0, attempt=0, run_id=None, failed=True)
        eligible = self.receipt(entry_index=0, attempt=1, run_id="run-first", failed=False)
        row0, hash0, bytes0 = self.row(failed, reason="dispatch_failed_before_bundle_creation", reason_hash=None, eligible=False)
        row1, hash1, bytes1 = self.row(eligible, reason=None, reason_hash=None, eligible=True)
        selected = validate_attempt_ledger(
            [row0, row1],
            self.manifest,
            receipts={hash0: bytes0, hash1: bytes1},
            finalized_bundles=self.finalized_bundles(row0, row1),
        )
        self.assertEqual(selected[row1["entry_id"]], row1)

    def test_closed_reason_normalization_counts_unknown_as_eligible(self) -> None:
        self.assertIsNone(normalize_technical_invalid_reason("output_divergent"))
        self.assertIsNone(normalize_technical_invalid_reason("future_reason"))
        self.assertEqual(normalize_technical_invalid_reason("strict_bundle_invalid"), "strict_bundle_invalid")
        receipt = self.receipt(entry_index=0, attempt=0, run_id="run-eligible", failed=False)
        row, digest, raw = self.row(receipt, reason=None, reason_hash=None, eligible=True)
        selected = validate_attempt_ledger(
            [row],
            self.manifest,
            receipts={digest: raw},
            finalized_bundles=self.finalized_bundles(row),
        )
        self.assertEqual(selected[row["entry_id"]], row)

    def test_reason_predicate_mismatch_refuses_with_exact_code(self) -> None:
        receipt = self.receipt(entry_index=0, attempt=0, run_id="run-created", failed=False)
        row, digest, raw = self.row(receipt, reason="dispatch_failed_before_bundle_creation", reason_hash=None, eligible=False)
        with self.assertRaises(AnalysisManifestError) as raised:
            validate_attempt_ledger(
                [row],
                self.manifest,
                receipts={digest: raw},
                finalized_bundles=self.finalized_bundles(row),
            )
        self.assertEqual(raised.exception.code, "analysis_attempt_reason_predicate_mismatch")

    def test_unledgered_dispatch_receipt_refuses_as_attempt_gap(self) -> None:
        receipt = self.receipt(entry_index=0, attempt=0, run_id="run-eligible")
        row, digest, raw = self.row(receipt, reason=None, reason_hash=None, eligible=True)
        extra = self.receipt(entry_index=1, attempt=0, run_id="unledgered-run")
        extra_raw = render_dispatch_receipt(extra)
        extra_digest = sha256_bytes(extra_raw)
        with self.assertRaises(AnalysisManifestError) as raised:
            validate_attempt_ledger(
                [row],
                self.manifest,
                receipts={digest: raw, extra_digest: extra_raw},
                finalized_bundles=self.finalized_bundles(row),
            )
        self.assertEqual(raised.exception.code, "analysis_attempt_ledger_gap")

    def test_gap_misorder_and_later_eligible_topup_refuse(self) -> None:
        receipt0 = self.receipt(entry_index=0, attempt=0, run_id="run-0")
        receipt2 = self.receipt(entry_index=0, attempt=2, run_id="run-2")
        row0, hash0, bytes0 = self.row(receipt0, reason=None, reason_hash=None, eligible=True)
        row2, hash2, bytes2 = self.row(receipt2, reason=None, reason_hash=None, eligible=True)
        with self.assertRaises(AnalysisManifestError) as gap:
            validate_attempt_ledger(
                [row0, row2],
                self.manifest,
                receipts={hash0: bytes0, hash2: bytes2},
                finalized_bundles=self.finalized_bundles(row0, row2),
            )
        self.assertEqual(gap.exception.code, "analysis_attempt_ledger_gap")

        receipt1 = self.receipt(entry_index=0, attempt=1, run_id="run-1")
        row1, hash1, bytes1 = self.row(receipt1, reason=None, reason_hash=None, eligible=True)
        with self.assertRaises(AnalysisManifestError) as topup:
            validate_attempt_ledger(
                [row0, row1], self.manifest,
                receipts={hash0: bytes0, hash1: bytes1},
                finalized_bundles=self.finalized_bundles(row0, row1),
            )
        self.assertEqual(topup.exception.code, "outcome_dependent_topup_forbidden")

    def test_duplicate_and_reversed_attempt_rows_refuse(self) -> None:
        failed = self.receipt(
            entry_index=0, attempt=0, run_id=None, failed=True
        )
        eligible = self.receipt(
            entry_index=0, attempt=1, run_id="run-first", failed=False
        )
        row0, hash0, bytes0 = self.row(
            failed,
            reason="dispatch_failed_before_bundle_creation",
            reason_hash=None,
            eligible=False,
        )
        row1, hash1, bytes1 = self.row(
            eligible, reason=None, reason_hash=None, eligible=True
        )
        receipts = {hash0: bytes0, hash1: bytes1}
        finalized = self.finalized_bundles(row0, row1)
        for label, rows in (
            ("duplicate", [row0, row0, row1]),
            ("reversed", [row1, row0]),
        ):
            with self.subTest(label=label), self.assertRaises(
                AnalysisManifestError
            ):
                validate_attempt_ledger(
                    rows,
                    self.manifest,
                    receipts=receipts,
                    finalized_bundles=finalized,
                )

    def test_any_attempt_after_first_eligible_refuses_even_if_later_invalid(self) -> None:
        eligible = self.receipt(entry_index=0, attempt=0, run_id="run-first")
        failed = self.receipt(
            entry_index=0, attempt=1, run_id=None, failed=True
        )
        row0, hash0, bytes0 = self.row(
            eligible, reason=None, reason_hash=None, eligible=True
        )
        row1, hash1, bytes1 = self.row(
            failed,
            reason="dispatch_failed_before_bundle_creation",
            reason_hash=None,
            eligible=False,
        )
        with self.assertRaises(AnalysisManifestError) as raised:
            validate_attempt_ledger(
                [row0, row1],
                self.manifest,
                receipts={hash0: bytes0, hash1: bytes1},
                finalized_bundles=self.finalized_bundles(row0, row1),
            )
        self.assertEqual(
            raised.exception.code, "outcome_dependent_topup_forbidden"
        )

    def test_eligible_attempt_requires_finalized_run_linkage(self) -> None:
        receipt = self.receipt(
            entry_index=0, attempt=0, run_id=None, failed=False
        )
        row, digest, raw = self.row(
            receipt, reason=None, reason_hash=None, eligible=True
        )
        with self.assertRaises(AnalysisManifestError) as raised:
            validate_attempt_ledger(
                [row],
                self.manifest,
                receipts={digest: raw},
                finalized_bundles={},
            )
        self.assertEqual(raised.exception.code, "analysis_attempt_ledger_gap")
        self.assertIn("finalized run linkage", raised.exception.detail)

    def test_eligible_receipt_naming_nonexistent_bundle_store_run_refuses(self) -> None:
        receipt = self.receipt(
            entry_index=0, attempt=0, run_id="run-not-in-bundle-store"
        )
        row, digest, raw = self.row(
            receipt, reason=None, reason_hash=None, eligible=True
        )
        with self.assertRaises(AnalysisManifestError) as raised:
            validate_attempt_ledger(
                [row],
                self.manifest,
                receipts={digest: raw},
                finalized_bundles={},
            )
        self.assertEqual(raised.exception.code, "analysis_attempt_ledger_gap")
        self.assertIn("finalized run coverage", raised.exception.detail)

    def test_eligible_bundle_store_run_must_be_strict_valid(self) -> None:
        receipt = self.receipt(
            entry_index=0, attempt=0, run_id="run-structurally-invalid"
        )
        row, digest, raw = self.row(
            receipt, reason=None, reason_hash=None, eligible=True
        )
        bundles = self.finalized_bundles(row)
        bundle_path = next(iter(bundles.values()))
        (bundle_path / "events.jsonl").unlink()
        with self.assertRaises(AnalysisManifestError) as raised:
            validate_attempt_ledger(
                [row],
                self.manifest,
                receipts={digest: raw},
                finalized_bundles=bundles,
            )
        self.assertEqual(raised.exception.code, "analysis_attempt_ledger_gap")
        self.assertIn("not strict-valid", raised.exception.detail)


if __name__ == "__main__":
    unittest.main()
