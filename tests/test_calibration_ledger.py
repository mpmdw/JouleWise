"""Defect-shaped D-109 calibration-ledger regressions."""

from __future__ import annotations

from dataclasses import replace
import json
import hashlib
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import joulewise.calibration_ledger as calibration_ledger
from joulewise.calibration_ledger import (
    DEFAULT_HEAD_PIN_PATH,
    GENESIS_DIGEST,
    GOVERNED_ARTIFACTS,
    HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA,
    HISTORICAL_IMPORT_FINALIZATION_EVENT,
    HISTORICAL_IMPORT_RESERVATION_EVENT,
    HISTORICAL_IMPORT_TABLE_SCHEMA,
    LEDGER_SCHEMA,
    CalibrationLedgerError,
    append_pending_receipt,
    artifact_hashes,
    bootstrap_historical_import,
    canonical_json_bytes,
    canonical_sha256,
    content_id_from_artifact_hashes,
    custody_manifest_bytes,
    finalize_attempt_receipt,
    generate_historical_custody_manifest,
    head_pin_for_receipt,
    load_calibration_ledger_snapshot,
    prepare_historical_import,
)
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS


class CalibrationLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "ledger.jsonl"
        self.pin = self.root / "head.json"
        self._write_pin(
            {
                "sequence": 0,
                "head_digest": GENESIS_DIGEST,
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        self.epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        self.t1 = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        self.t1.update(self.epoch)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_pin(self, value: dict) -> None:
        self.pin.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def _custody(self, attempt_id: str) -> Path:
        path = self.root / "another-root" / "instrument_validation" / attempt_id
        (path / "raw").mkdir(parents=True)
        (path / "raw" / "powermetrics.plist").write_bytes(b"raw-" + attempt_id.encode())
        (path / "events.jsonl").write_text(
            '{"timestamp_s": 99.0}\n', encoding="utf-8"
        )
        (path / "instrument_evidence.json").write_text(
            json.dumps({"b_fiducial_s": 0.025, "attempt": attempt_id}) + "\n",
            encoding="utf-8",
        )
        (path / "manifest.json").write_text(
            json.dumps({"attempt": attempt_id}) + "\n", encoding="utf-8"
        )
        return path

    def _reserve(self, attempt_id: str, custody: Path):
        return append_pending_receipt(
            self.ledger,
            attempt_id=attempt_id,
            custody_locator=str(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            head_pin_path=self.pin,
            require_committed_pin=False,
        )

    def _finalize(self, attempt_id: str, custody: Path, disposition: str = "valid"):
        return finalize_attempt_receipt(
            self.ledger,
            attempt_id=attempt_id,
            disposition=disposition,
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="99.0",
            exact_bound_lexeme_s="0.025",
        )

    def _snapshot(self, *, verify_custody: bool = True):
        return load_calibration_ledger_snapshot(
            self.ledger,
            self.pin,
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
            require_committed_pin=False,
            verify_custody=verify_custody,
        )

    def _historical_custody(
        self,
        checkout: Path,
        run_name: str,
        attempt_id: str,
        token: str,
    ) -> Path:
        custody = checkout / run_name / "instrument_validation" / attempt_id
        (custody / "raw").mkdir(parents=True)
        payloads = {
            "raw/powermetrics.plist": f"raw-{token}\n".encode(),
            "events.jsonl": (
                json.dumps({"event_type": "capture", "token": token}) + "\n"
            ).encode(),
            "power_trace.csv": f"timestamp_s,gpu_w\n1,{token}\n".encode(),
        }
        for relative, raw in payloads.items():
            (custody / relative).write_bytes(raw)
        bound = f"0.0{int(token) + 1}"
        evidence = {
            "artifact_sha256": {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in payloads.items()
            },
            "b_fiducial_s": float(bound),
            "bindings": dict(self.t1),
            "capture_wall_time_s": 1000.0 + int(token),
            # Deliberately non-authoritative and contrary to some ruled rows.
            "status": "valid" if int(token) % 2 else "invalid",
            "validation_id": attempt_id,
        }
        evidence_raw = (
            json.dumps(evidence, indent=2, sort_keys=True) + "\n"
        ).encode()
        (custody / "instrument_evidence.json").write_bytes(evidence_raw)
        manifest_artifacts = {
            **evidence["artifact_sha256"],
            "instrument_evidence.json": hashlib.sha256(evidence_raw).hexdigest(),
        }
        manifest = {
            "artifacts": manifest_artifacts,
            "schema_version": "joulewise.instrument_validation_manifest.v1",
            "validation_id": attempt_id,
        }
        (custody / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return custody

    def _historical_fixture(self):
        checkout = self.root / "checkout"
        specifications = (
            ("20260101T000001-aaaaaaaa", "1", "valid"),
            ("20260101T000002-bbbbbbbb", "2", "systematic-invalid"),
            ("20260101T000003-cccccccc", "3", "ordinary-invalid"),
        )
        custodies = [
            self._historical_custody(
                checkout, "runs_fixture", attempt_id, token
            )
            for attempt_id, token, disposition in specifications
        ]
        members = []
        for custody, (attempt_id, token, disposition) in zip(
            custodies, specifications
        ):
            del token
            hashes = artifact_hashes(custody)
            self.assertEqual(set(hashes), set(GOVERNED_ARTIFACTS))
            members.append(
                {
                    "attempt_id": attempt_id,
                    "content_id": content_id_from_artifact_hashes(hashes),
                    "artifact_sha256": hashes,
                    "disposition": disposition,
                }
            )
        table = {
            "schema_version": HISTORICAL_IMPORT_TABLE_SCHEMA,
            "ledger_schema": LEDGER_SCHEMA,
            "identity_epoch": dict(self.epoch),
            "members": members,
        }
        return checkout, checkout / "runs_fixture", custodies, table

    def _historical_import_args(self, table: dict, custodies: list[Path]) -> dict:
        table_raw = (json.dumps(table, indent=2, sort_keys=True) + "\n").encode()
        manifest = {
            "schema_version": HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA,
            "ledger_schema": LEDGER_SCHEMA,
            "members": {
                member["content_id"]: str(custody.resolve())
                for member, custody in zip(table["members"], custodies)
            },
        }
        manifest_raw = custody_manifest_bytes(manifest)
        return {
            "disposition_table_raw": table_raw,
            "expected_disposition_table_sha256": hashlib.sha256(
                table_raw
            ).hexdigest(),
            "custody_manifest_raw": manifest_raw,
            "expected_custody_manifest_sha256": hashlib.sha256(
                manifest_raw
            ).hexdigest(),
        }

    def test_crash_between_reservation_and_finalization_refuses(self) -> None:
        custody = self.root / "never-created"
        pending = self._reserve("crash-attempt", custody)
        self._write_pin(head_pin_for_receipt(pending))
        snapshot = self._snapshot()
        self.assertIn("calibration_ledger_pending", snapshot.refusal_reasons)
        self.assertFalse(custody.exists())

    def test_reservation_requires_complete_epoch_and_full_t1(self) -> None:
        with self.assertRaisesRegex(
            CalibrationLedgerError, "malformed receipt"
        ):
            append_pending_receipt(
                self.ledger,
                attempt_id="partial-reservation",
                custody_locator=str(self.root / "partial"),
                identity_epoch={"power_policy": "ac_high_power"},
                t1_bindings={"power_policy": "ac_high_power"},
                head_pin_path=self.pin,
                require_committed_pin=False,
            )

    def test_production_writer_reserves_before_capture_state_or_sampler(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "validate_powermetrics_fiducial.py"
        ).read_text(encoding="utf-8")
        reservation = source.index("\n    append_pending_receipt(")
        directory_creation = source.index('(out_dir / "raw").mkdir')
        sampler_launch = source.index("process = subprocess.Popen(")
        uncaught_finalizer = source.index("atexit.register(finalize_abandoned)")

        self.assertLess(reservation, directory_creation)
        self.assertLess(reservation, sampler_launch)
        self.assertLess(uncaught_finalizer, directory_creation)

    def test_proper_prefix_of_pinned_head_refuses_as_rollback(self) -> None:
        custody = self._custody("rollback")
        self._reserve("rollback", custody)
        final = self._finalize("rollback", custody)
        self._write_pin(head_pin_for_receipt(final))
        lines = self.ledger.read_bytes().splitlines(keepends=True)
        self.ledger.write_bytes(lines[0])
        snapshot = self._snapshot(verify_custody=False)
        self.assertIn("calibration_ledger_rollback", snapshot.refusal_reasons)

    def test_unpinned_physical_extension_refuses_stale_head(self) -> None:
        custody = self._custody("uncommitted")
        self._reserve("uncommitted", custody)
        snapshot = self._snapshot(verify_custody=False)
        self.assertIn("calibration_ledger_head_mismatch", snapshot.refusal_reasons)

    def test_true_sibling_fork_refuses_on_predecessor_conflict(self) -> None:
        custody = self._custody("fork")
        first = self._reserve("fork", custody)
        final = self._finalize("fork", custody)
        sibling = {
            **dict(first),
            "sequence": 3,
            "predecessor_digest": first["receipt_digest"],
            "attempt_id": "fork-sibling",
            "custody_locator": str(self.root / "fork-sibling"),
        }
        sibling["receipt_digest"] = canonical_sha256(
            {key: value for key, value in sibling.items() if key != "receipt_digest"}
        )
        with self.ledger.open("ab") as handle:
            handle.write(canonical_json_bytes(sibling) + b"\n")
        self._write_pin(head_pin_for_receipt(sibling))
        snapshot = self._snapshot(verify_custody=False)
        self.assertIn("calibration_ledger_chain_conflict", snapshot.refusal_reasons)
        self.assertNotIn(
            "calibration_ledger_attempt_conflict", snapshot.refusal_reasons
        )
        self.assertNotIn("calibration_ledger_head_mismatch", snapshot.refusal_reasons)
        self.assertEqual(sibling["receipt_digest"], snapshot.head_digest)
        self.assertNotEqual(final["receipt_digest"], sibling["receipt_digest"])

    def test_content_bearing_abandoned_receipt_is_unresolved_evidence(self) -> None:
        custody = self._custody("abandoned-content")
        self._reserve("abandoned-content", custody)
        final = self._finalize(
            "abandoned-content", custody, disposition="abandoned"
        )
        self._write_pin(head_pin_for_receipt(final))
        snapshot = self._snapshot()
        observation = snapshot.observation_by_attempt["abandoned-content"]
        self.assertIsNotNone(observation.content_id)
        self.assertEqual(observation.disposition, "abandoned")
        self.assertEqual(observation.classification_disposition, "unresolved")

    def test_finalization_is_single_transition(self) -> None:
        custody = self._custody("single")
        self._reserve("single", custody)
        self._finalize("single", custody)
        with self.assertRaisesRegex(CalibrationLedgerError, "uniquely pending"):
            self._finalize("single", custody)

    def test_missing_or_changed_custody_bytes_refuse(self) -> None:
        custody = self._custody("custody")
        self._reserve("custody", custody)
        final = self._finalize("custody", custody)
        self._write_pin(head_pin_for_receipt(final))
        (custody / "instrument_evidence.json").write_text("changed\n")
        snapshot = self._snapshot()
        self.assertEqual(
            snapshot.refusal_reasons,
            ("calibration_ledger_custody_invalid",),
        )

    def test_baseline_must_be_exact_member_of_current_chain(self) -> None:
        snapshot = load_calibration_ledger_snapshot(
            self.ledger,
            self.pin,
            baseline_sequence=1,
            baseline_digest="f" * 64,
            require_committed_pin=False,
        )
        self.assertIn("calibration_ledger_baseline_missing", snapshot.refusal_reasons)

    def test_historical_import_cli_dry_run_is_byte_stable_and_writes_nothing(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        table_path = self.root / "dispositions.json"
        table_path.write_text(
            json.dumps(table, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        manifest_path = self.root / "custody-manifest.json"
        manifest_path.write_bytes(import_args["custody_manifest_raw"])
        dry_ledger = self.root / "dry-run-ledger.jsonl"
        script = Path(__file__).resolve().parents[1] / "scripts" / (
            "calibration_ledger_bootstrap.py"
        )
        command = [
            sys.executable,
            str(script),
            "--disposition-table",
            str(table_path),
            "--expected-table-sha256",
            import_args["expected_disposition_table_sha256"],
            "--custody-manifest",
            str(manifest_path),
            "--expected-custody-manifest-sha256",
            import_args["expected_custody_manifest_sha256"],
            "--checkout-root",
            str(checkout),
            "--ledger",
            str(dry_ledger),
            "--head-pin",
            str(DEFAULT_HEAD_PIN_PATH),
            str(root),
        ]
        first = subprocess.run(command, check=True, capture_output=True)
        second = subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, b"")
        self.assertFalse(dry_ledger.exists())
        rows = [json.loads(line) for line in first.stdout.splitlines()]
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[-1]["record"], "bootstrap-summary")
        self.assertFalse(rows[-1]["executed"])
        self.assertEqual(rows[-1]["final_sequence"], 6)
        self.assertEqual(
            rows[-1]["disposition_table_sha256"],
            import_args["expected_disposition_table_sha256"],
        )
        self.assertEqual(
            rows[-1]["custody_manifest_sha256"],
            import_args["expected_custody_manifest_sha256"],
        )
        wrong_digest = list(command)
        digest_index = wrong_digest.index("--expected-table-sha256") + 1
        wrong_digest[digest_index] = "0" * 64
        refused = subprocess.run(wrong_digest, check=False, capture_output=True)
        self.assertEqual(refused.returncode, 2)
        self.assertIn(b"disposition table sha256 mismatch", refused.stderr)
        emitted = subprocess.run(
            [
                sys.executable,
                str(script),
                "--disposition-table",
                str(table_path),
                "--expected-table-sha256",
                import_args["expected_disposition_table_sha256"],
                "--checkout-root",
                str(checkout),
                "--emit-custody-manifest",
                str(root),
            ],
            check=True,
            capture_output=True,
        )
        self.assertEqual(emitted.stdout, import_args["custody_manifest_raw"])
        self.assertIn(
            import_args["expected_custody_manifest_sha256"].encode(),
            emitted.stderr,
        )
        self.assertFalse(dry_ledger.exists())

    def test_historical_import_refuses_nonimportable_disposition(self) -> None:
        _checkout, _root, custodies, table = self._historical_fixture()
        table["members"][0]["disposition"] = "abandoned"
        import_args = self._historical_import_args(table, custodies)
        with self.assertRaisesRegex(CalibrationLedgerError, "member is malformed"):
            prepare_historical_import(**import_args)

    def test_historical_import_refuses_symlinked_pinned_custody(self) -> None:
        _checkout, _root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        linked = self.root / "symlinked-custody"
        linked.symlink_to(custodies[0], target_is_directory=True)
        manifest = json.loads(import_args["custody_manifest_raw"])
        manifest["members"][table["members"][0]["content_id"]] = str(linked)
        manifest_raw = custody_manifest_bytes(manifest)
        import_args["custody_manifest_raw"] = manifest_raw
        import_args["expected_custody_manifest_sha256"] = hashlib.sha256(
            manifest_raw
        ).hexdigest()
        with self.assertRaisesRegex(CalibrationLedgerError, "through a symlink"):
            prepare_historical_import(**import_args)

    def test_historical_import_refuses_nonempty_ledger_and_nongenesis_pin(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        self.ledger.write_bytes(b"not-empty\n")
        with self.assertRaisesRegex(CalibrationLedgerError, "empty ledger"):
            bootstrap_historical_import(
                self.ledger,
                head_pin_path=self.pin,
                roots=[root],
                checkout_root=checkout,
                **import_args,
                require_committed_pin=False,
            )

        self.ledger.write_bytes(b"")
        self._write_pin(
            {
                "sequence": 1,
                "head_digest": "f" * 64,
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        with self.assertRaisesRegex(CalibrationLedgerError, "genesis head pin"):
            bootstrap_historical_import(
                self.ledger,
                head_pin_path=self.pin,
                roots=[root],
                checkout_root=checkout,
                **import_args,
                require_committed_pin=False,
            )

    def test_historical_import_io_failure_rolls_back_partial_append(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)

        def partial_write_then_fail(handle, payload):
            handle.write(payload[: len(payload) // 2])
            handle.flush()
            raise OSError("injected mid-import failure")

        with mock.patch.object(
            calibration_ledger,
            "_write_bootstrap_payload",
            side_effect=partial_write_then_fail,
        ):
            with self.assertRaisesRegex(CalibrationLedgerError, "failed atomically"):
                bootstrap_historical_import(
                    self.ledger,
                    head_pin_path=self.pin,
                    roots=[root],
                    checkout_root=checkout,
                    **import_args,
                    execute=True,
                    require_committed_pin=False,
                )
        self.assertTrue(self.ledger.exists())
        self.assertEqual(self.ledger.read_bytes(), b"")
        self.assertEqual(json.loads(self.pin.read_text())["sequence"], 0)

    def test_historical_import_fsync_failure_keeps_visible_ledger_empty(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        with mock.patch.object(
            calibration_ledger.os,
            "fsync",
            side_effect=OSError("injected fsync"),
        ):
            with self.assertRaisesRegex(CalibrationLedgerError, "failed atomically"):
                bootstrap_historical_import(
                    self.ledger,
                    head_pin_path=self.pin,
                    roots=[root],
                    checkout_root=checkout,
                    **import_args,
                    execute=True,
                    require_committed_pin=False,
                )
        self.assertEqual(self.ledger.read_bytes(), b"")

    def test_sigkill_mid_import_leaves_retryable_genesis(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        code = f"""
import os, signal
from pathlib import Path
import joulewise.calibration_ledger as module
def die_mid_write(handle, payload):
    handle.write(payload[:len(payload) // 2])
    handle.flush()
    os.fsync(handle.fileno())
    os.kill(os.getpid(), signal.SIGKILL)
module._write_bootstrap_payload = die_mid_write
module.bootstrap_historical_import(
    Path({str(self.ledger)!r}),
    head_pin_path=Path({str(self.pin)!r}),
    roots=[Path({str(root)!r})],
    checkout_root=Path({str(checkout)!r}),
    disposition_table_raw={import_args['disposition_table_raw']!r},
    expected_disposition_table_sha256={import_args['expected_disposition_table_sha256']!r},
    custody_manifest_raw={import_args['custody_manifest_raw']!r},
    expected_custody_manifest_sha256={import_args['expected_custody_manifest_sha256']!r},
    execute=True,
    require_committed_pin=False,
)
"""
        killed = subprocess.run([sys.executable, "-c", code], check=False)
        self.assertEqual(killed.returncode, -signal.SIGKILL)
        self.assertEqual(self.ledger.read_bytes(), b"")
        plan = bootstrap_historical_import(
            self.ledger,
            head_pin_path=self.pin,
            roots=[root],
            checkout_root=checkout,
            **import_args,
            execute=True,
            require_committed_pin=False,
        )
        self.assertEqual(self.ledger.read_bytes(), plan.ledger_bytes)

    def test_execute_reauthenticates_all_artifacts_after_lock(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        original_gate = calibration_ledger._require_genesis_bootstrap_state
        calls = 0

        def mutate_after_locked_gate(*args, **kwargs):
            nonlocal calls
            calls += 1
            original_gate(*args, **kwargs)
            if calls == 2:
                with (custodies[0] / "events.jsonl").open("ab") as handle:
                    handle.write(b"drift-after-prepare\n")

        with mock.patch.object(
            calibration_ledger,
            "_require_genesis_bootstrap_state",
            side_effect=mutate_after_locked_gate,
        ):
            with self.assertRaisesRegex(
                CalibrationLedgerError, "reauthentication failed"
            ):
                bootstrap_historical_import(
                    self.ledger,
                    head_pin_path=self.pin,
                    roots=[root],
                    checkout_root=checkout,
                    **import_args,
                    execute=True,
                    require_committed_pin=False,
                )
        self.assertEqual(self.ledger.read_bytes(), b"")

    def test_historical_import_marker_is_not_a_post_cutoff_live_observation(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        plan = bootstrap_historical_import(
            self.ledger,
            head_pin_path=self.pin,
            roots=[root],
            checkout_root=checkout,
            **import_args,
            execute=True,
            require_committed_pin=False,
        )
        self._write_pin(dict(plan.head_pin))
        snapshot = load_calibration_ledger_snapshot(
            self.ledger,
            self.pin,
            require_committed_pin=False,
            repo_root=checkout,
        )
        self.assertTrue(snapshot.valid)
        self.assertEqual(len(snapshot.observations), 3)
        self.assertTrue(all(row.is_historical_import for row in snapshot.observations))
        self.assertEqual(snapshot.post_cutoff_live_observations(0), ())
        self.assertEqual(
            {receipt["event"] for receipt in snapshot.receipts},
            {
                HISTORICAL_IMPORT_RESERVATION_EVENT,
                HISTORICAL_IMPORT_FINALIZATION_EVENT,
            },
        )

    def test_live_capture_finalization_cannot_carry_import_marker(self) -> None:
        custody = self._custody("live-marker-boundary")
        self._reserve("live-marker-boundary", custody)
        final = self._finalize("live-marker-boundary", custody)
        self._write_pin(head_pin_for_receipt(final))
        snapshot = self._snapshot()
        self.assertTrue(snapshot.valid)
        self.assertEqual(len(snapshot.observations), 1)
        self.assertFalse(snapshot.observations[0].is_historical_import)
        self.assertEqual(
            {receipt["event"] for receipt in snapshot.receipts},
            {"reservation", "finalization"},
        )

    def test_historical_import_manifest_pins_head_and_subset_roots_refuse(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        source = custodies[0]
        duplicate = (
            checkout
            / "a_duplicate"
            / "instrument_validation"
            / source.name
        )
        duplicate.parent.mkdir(parents=True)
        shutil.copytree(source, duplicate)
        table_raw = (json.dumps(table, indent=2, sort_keys=True) + "\n").encode()
        table_sha = hashlib.sha256(table_raw).hexdigest()
        manifest = generate_historical_custody_manifest(
            roots=[root, checkout / "a_duplicate"],
            checkout_root=checkout,
            disposition_table_raw=table_raw,
            expected_disposition_table_sha256=table_sha,
        )
        manifest_raw = custody_manifest_bytes(manifest)
        import_args = {
            "disposition_table_raw": table_raw,
            "expected_disposition_table_sha256": table_sha,
            "custody_manifest_raw": manifest_raw,
            "expected_custody_manifest_sha256": hashlib.sha256(
                manifest_raw
            ).hexdigest(),
        }
        plan = prepare_historical_import(
            roots=[root, checkout / "a_duplicate"],
            checkout_root=checkout,
            **import_args,
        )
        imported = next(
            row
            for row in plan.receipts
            if row["attempt_id"] == source.name
            and row["event"] == HISTORICAL_IMPORT_FINALIZATION_EVENT
        )
        self.assertEqual(
            imported["custody_locator"],
            str(duplicate.resolve()),
        )
        with self.assertRaisesRegex(
            CalibrationLedgerError, "absent from root discovery"
        ):
            prepare_historical_import(
                roots=[root],
                checkout_root=checkout,
                **import_args,
            )
        manifest_only = prepare_historical_import(**import_args)
        self.assertEqual(manifest_only.head_digest, plan.head_digest)

    def test_historical_import_refuses_tampered_evidence_bytes(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        with (custodies[1] / "events.jsonl").open("ab") as handle:
            handle.write(b"tampered\n")
        with self.assertRaisesRegex(CalibrationLedgerError, "hash mismatch"):
            prepare_historical_import(
                roots=[root],
                checkout_root=checkout,
                **import_args,
            )

    def test_three_member_historical_import_has_hand_computed_head(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        inspect_candidate = calibration_ledger._inspect_historical_candidate

        def stable_vector_candidate(*args, **kwargs):
            content_id, candidate, error = inspect_candidate(*args, **kwargs)
            if candidate is not None:
                candidate = replace(
                    candidate,
                    custody_locator=(
                        "/fixture-checkout/"
                        f"{Path(candidate.custody_locator).relative_to(checkout.resolve())}"
                    ),
                )
            return content_id, candidate, error

        # Normalize only the machine-specific absolute custody prefix so this
        # remains a literal cross-checkout wire vector. File authentication,
        # ordering, receipt construction, and chaining all remain production.
        with mock.patch.object(
            calibration_ledger,
            "_inspect_historical_candidate",
            side_effect=stable_vector_candidate,
        ):
            plan = prepare_historical_import(
                **import_args,
            )
        self.assertEqual(plan.final_sequence, 6)
        self.assertEqual(
            plan.head_digest,
            "01027fdfa3b2991693ffb25e4165573c0521e2ebe7b41b7ecd69abb9a7197f28",
        )


if __name__ == "__main__":
    unittest.main()
