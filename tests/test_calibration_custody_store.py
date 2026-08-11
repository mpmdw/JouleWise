"""Content-addressed calibration-custody store contract tests."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.calibration_ledger import (
    CUSTODY_STORE_MANIFEST_NAME,
    CUSTODY_STORE_MANIFEST_SCHEMA,
    GENESIS_DIGEST,
    GOVERNED_ARTIFACTS,
    LEDGER_SCHEMA,
    append_pending_receipt,
    artifact_hashes,
    calibration_custody_store_manifest_bytes,
    finalize_attempt_receipt,
    head_pin_for_receipt,
    load_calibration_ledger_snapshot,
)
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from scripts import mint_floor_artifact as mint_core


class CalibrationCustodyStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.ledger = self.root / "ledger.jsonl"
        self.head = self.root / "head.json"
        self._write_head(
            {
                "sequence": 0,
                "head_digest": GENESIS_DIGEST,
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        self.identity_epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        self.t1_bindings = {
            field: f"value-{field}" for field in V2_BINDING_FIELDS
        }
        self.t1_bindings.update(self.identity_epoch)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_head(self, value: dict) -> None:
        self.head.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def _custody(self, attempt_id: str, *, token: str | None = None) -> Path:
        token = token or attempt_id
        custody = self.root / "legacy" / attempt_id
        (custody / "raw").mkdir(parents=True)
        payloads = {
            "raw/powermetrics.plist": f"raw-{token}\n".encode(),
            "events.jsonl": (json.dumps({"token": token}) + "\n").encode(),
            "power_trace.csv": f"timestamp_s,power_w\n1,{token}\n".encode(),
            "instrument_evidence.json": (
                json.dumps({"attempt": token}, sort_keys=True) + "\n"
            ).encode(),
            "manifest.json": (
                json.dumps({"attempt": token}, sort_keys=True) + "\n"
            ).encode(),
        }
        for relative, raw in payloads.items():
            path = custody / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.assertEqual(set(artifact_hashes(custody)), set(GOVERNED_ARTIFACTS))
        return custody

    def _append_final(
        self,
        attempt_id: str,
        custody: Path,
        *,
        hashes: dict[str, str] | None = None,
        disposition: str = "valid",
    ) -> None:
        append_pending_receipt(
            self.ledger,
            attempt_id=attempt_id,
            custody_locator=str(custody),
            identity_epoch=self.identity_epoch,
            t1_bindings=self.t1_bindings,
            head_pin_path=self.head,
            require_committed_pin=False,
        )
        receipt = finalize_attempt_receipt(
            self.ledger,
            attempt_id=attempt_id,
            disposition=disposition,
            custody_locator=str(custody),
            artifact_sha256=(hashes if hashes is not None else artifact_hashes(custody)),
            identity_epoch=self.identity_epoch,
            t1_bindings=self.t1_bindings,
            capture_wall_time_s="99.0",
            exact_bound_lexeme_s="0.025",
        )
        self._write_head(head_pin_for_receipt(receipt))

    def _load(self, *, store: Path | None = None):
        return load_calibration_ledger_snapshot(
            self.ledger,
            self.head,
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
            require_committed_pin=False,
            repo_root=self.root,
            calibration_custody_store=store,
        )

    def _make_store(self, snapshot, custody_by_attempt: dict[str, Path]) -> Path:
        store = self.root / f"store-{len(list(self.root.glob('store-*')))}"
        store.mkdir()
        for observation in snapshot.observations:
            assert observation.content_id is not None
            shutil.copytree(
                custody_by_attempt[observation.attempt_id],
                store / observation.content_id,
            )
        (store / CUSTODY_STORE_MANIFEST_NAME).write_bytes(
            calibration_custody_store_manifest_bytes(snapshot)
        )
        return store

    def test_absent_mode_preserves_exact_legacy_locator_behavior(self) -> None:
        custody = self._custody("attempt-a")
        self._append_final("attempt-a", custody)
        implicit = self._load()
        explicit = self._load(store=None)
        self.assertEqual(implicit, explicit)
        self.assertEqual(implicit.refusal_reasons, ())
        self.assertEqual(implicit.observations[0].custody_locator, str(custody))
        self.assertIsNone(implicit.custody_store_manifest_schema)
        self.assertIsNone(implicit.custody_store_manifest_sha256)

    def test_store_loads_only_manifest_and_exact_ledger_projection(self) -> None:
        custody = self._custody("attempt-a")
        self._append_final("attempt-a", custody)
        legacy = self._load()
        store = self._make_store(legacy, {"attempt-a": custody})
        extra = store / ("f" * 64) / "never-read.bin"
        extra.parent.mkdir()
        extra.write_bytes(b"unreferenced")

        with V2AuthenticationReadSession() as session:
            snapshot = self._load(store=store)
            registered_store_paths = {
                identity
                for identity in session.records
                if identity == str(store.resolve())
                or store.resolve() in Path(identity).parents
            }
        self.assertEqual(snapshot.refusal_reasons, ())
        self.assertEqual(
            snapshot.custody_store_manifest_schema,
            CUSTODY_STORE_MANIFEST_SCHEMA,
        )
        self.assertEqual(
            snapshot.custody_store_manifest_sha256,
            hashlib.sha256(
                (store / CUSTODY_STORE_MANIFEST_NAME).read_bytes()
            ).hexdigest(),
        )
        content_id = snapshot.observations[0].content_id
        expected = {
            str((store / CUSTODY_STORE_MANIFEST_NAME).resolve()),
            *(str((store / content_id / relative).resolve()) for relative in GOVERNED_ARTIFACTS),
        }
        self.assertEqual(registered_store_paths, expected)
        self.assertNotIn(str(extra.resolve()), session.records)

    def test_store_refuses_missing_symlink_nonregular_and_hash_mismatch(self) -> None:
        custody = self._custody("attempt-a")
        self._append_final("attempt-a", custody)
        legacy = self._load()
        baseline = self._make_store(legacy, {"attempt-a": custody})
        content_id = legacy.observations[0].content_id
        assert content_id is not None

        cases = ("missing_dir", "missing_file", "symlink", "nonregular", "hash")
        for case in cases:
            with self.subTest(case=case):
                store = self.root / f"attack-{case}"
                shutil.copytree(baseline, store)
                target = store / content_id / "power_trace.csv"
                if case == "missing_dir":
                    shutil.rmtree(store / content_id)
                elif case == "missing_file":
                    target.unlink()
                elif case == "symlink":
                    target.unlink()
                    target.symlink_to(custody / "power_trace.csv")
                elif case == "nonregular":
                    target.unlink()
                    target.mkdir()
                else:
                    target.write_bytes(b"tampered")
                snapshot = self._load(store=store)
                self.assertEqual(
                    snapshot.refusal_reasons,
                    ("calibration_ledger_custody_invalid",),
                )

    def test_store_never_falls_back_to_valid_legacy_locator(self) -> None:
        custody = self._custody("attempt-a")
        self._append_final("attempt-a", custody)
        legacy = self._load()
        self.assertTrue(legacy.valid)
        store = self._make_store(legacy, {"attempt-a": custody})
        shutil.rmtree(store / legacy.observations[0].content_id)
        relocated = self._load(store=store)
        self.assertEqual(
            relocated.refusal_reasons,
            ("calibration_ledger_custody_invalid",),
        )

    def test_store_refuses_null_and_duplicate_content_identity(self) -> None:
        null_custody = self._custody("null-content")
        incomplete_hashes = artifact_hashes(null_custody)
        del incomplete_hashes["instrument_evidence.json"]
        self._append_final(
            "null-content",
            null_custody,
            hashes=incomplete_hashes,
            disposition="abandoned",
        )
        null_store = self.root / "null-store"
        null_store.mkdir()
        null_snapshot = self._load(store=null_store)
        self.assertEqual(
            null_snapshot.refusal_reasons,
            ("calibration_ledger_custody_invalid",),
        )

        # Start a second isolated ledger whose two attempts have identical
        # governed bytes and therefore the same content identity.
        self.ledger.unlink()
        self._write_head(
            {
                "sequence": 0,
                "head_digest": GENESIS_DIGEST,
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        first = self._custody("duplicate-a", token="same")
        second = self._custody("duplicate-b", token="same")
        self._append_final("duplicate-a", first)
        self._append_final("duplicate-b", second)
        duplicate_store = self.root / "duplicate-store"
        duplicate_store.mkdir()
        duplicate_snapshot = self._load(store=duplicate_store)
        self.assertEqual(
            duplicate_snapshot.refusal_reasons,
            ("calibration_ledger_custody_invalid",),
        )

    def test_manifest_is_canonical_strict_and_exactly_ledger_derived(self) -> None:
        custody = self._custody("attempt-a")
        self._append_final("attempt-a", custody)
        legacy = self._load()
        baseline = self._make_store(legacy, {"attempt-a": custody})
        manifest_path = baseline / CUSTODY_STORE_MANIFEST_NAME

        value = json.loads(manifest_path.read_bytes())
        value["ledger"]["head_digest"] = "0" * 64
        manifest_path.write_text(json.dumps(value) + "\n", encoding="utf-8")
        self.assertEqual(
            self._load(store=baseline).refusal_reasons,
            ("calibration_ledger_custody_invalid",),
        )

        manifest_path.write_bytes(calibration_custody_store_manifest_bytes(legacy))
        raw = manifest_path.read_bytes()
        duplicate = raw.replace(
            b'{"contents":',
            b'{"schema_version":"duplicate","contents":',
            1,
        )
        manifest_path.write_bytes(duplicate)
        self.assertEqual(
            self._load(store=baseline).refusal_reasons,
            ("calibration_ledger_custody_invalid",),
        )

    def test_post_bind_provenance_must_equal_authenticated_snapshot(self) -> None:
        custody = self._custody("attempt-a")
        self._append_final("attempt-a", custody)
        legacy = self._load()
        store = self._make_store(legacy, {"attempt-a": custody})
        snapshot = self._load(store=store)
        provenance = {
            "schema_version": CUSTODY_STORE_MANIFEST_SCHEMA,
            "manifest_sha256": snapshot.custody_store_manifest_sha256,
        }
        artifact = {"provenance": {"calibration_custody_store": provenance}}
        mint_core._validate_custody_store_provenance(artifact, snapshot)
        with self.assertRaisesRegex(
            mint_core.MintError,
            "differs from the authenticated calibration ledger snapshot",
        ):
            mint_core._validate_custody_store_provenance(
                {
                    "provenance": {
                        "calibration_custody_store": {
                            **provenance,
                            "manifest_sha256": "0" * 64,
                        }
                    }
                },
                snapshot,
            )
        mint_core._validate_custody_store_provenance(
            {"provenance": {}}, legacy
        )
        with self.assertRaises(mint_core.MintError):
            mint_core._validate_custody_store_provenance(artifact, legacy)


if __name__ == "__main__":
    unittest.main()
