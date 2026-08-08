"""Defect-shaped D-109 calibration-ledger regressions."""

from __future__ import annotations

from dataclasses import replace
import io
import inspect
import json
import hashlib
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

from joulewise.calibration_exits import RefusalCode

import joulewise.calibration_ledger as calibration_ledger
from scripts import calibration_ledger_bootstrap as bootstrap_cli
from scripts import reserve_calibration_window_bracket as bracket_session_cli
from scripts import recover_calibration_ledger as recovery_cli
from tests.test_calibration_bracketing import (
    _unissued_acceptance_fixture,
    _unissued_acceptance_fixture_bytes,
)
from joulewise.calibration_bracketing import (
    _canonical_sha256 as acceptance_canonical_sha256,
    _valid_acceptance_bound,
    evaluate_calibration_bracket,
    load_calibration_acceptance_bound,
)
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    GOVERNED_ARTIFACTS,
    BRACKET_SESSION_ABORT_EVENT,
    BRACKET_SESSION_FINALIZATION_EVENT,
    HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA,
    HISTORICAL_IMPORT_FINALIZATION_EVENT,
    HISTORICAL_IMPORT_RESERVATION_EVENT,
    HISTORICAL_IMPORT_TABLE_SCHEMA,
    LEDGER_SCHEMA,
    CalibrationLedgerError,
    abort_bracket_session,
    append_bracket_session_receipt,
    HistoricalImportDurabilityUncertain,
    append_pending_receipt,
    artifact_hashes,
    bootstrap_historical_import,
    canonical_json_bytes,
    canonical_sha256,
    content_id_from_artifact_hashes,
    custody_manifest_bytes,
    finalize_attempt_receipt,
    finalize_bracket_session_slot,
    generate_historical_custody_manifest,
    head_pin_for_receipt,
    load_calibration_ledger_snapshot,
    prepare_historical_import,
    terminal_head_pin_for_session,
)
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from joulewise.schemas import CalibrationBracketingPolicy


_REAL_D079_TABLE = Path("/private/tmp/d079-ledger-dispositions.json")
_REAL_D079_CUSTODY_MANIFEST = Path(
    "/private/tmp/d079-custody-manifest.lead.json"
)
_REAL_D079_TABLE_SHA256 = (
    "5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a"
)
_REAL_D079_CUSTODY_MANIFEST_SHA256 = (
    "99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078"
)
_ISSUED_D079_DERIVATION_SHA256 = (
    "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02"
)
_ISSUED_D079_FILE_SHA256 = (
    "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
)


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

    def _isolated_cli_checkout(self) -> tuple[Path, Path]:
        """Copy the CLI into a tiny repo with a committed genesis head pin."""

        source_root = Path(__file__).resolve().parents[1]
        repo = self.root / "cli-repo"
        shutil.copytree(source_root / "joulewise", repo / "joulewise")
        (repo / "scripts").mkdir()
        shutil.copy2(
            source_root / "scripts" / "calibration_ledger_bootstrap.py",
            repo / "scripts" / "calibration_ledger_bootstrap.py",
        )
        pin = repo / "configs" / "calibration" / "calibration_ledger_head.json"
        pin.parent.mkdir(parents=True)
        pin.write_text(
            json.dumps(
                {
                    "sequence": 0,
                    "head_digest": GENESIS_DIGEST,
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "tests@joulewise.invalid"],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "JouleWise tests"],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "add", pin.relative_to(repo).as_posix()],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-qm", "pin synthetic genesis head"],
            cwd=repo,
            check=True,
        )
        return repo / "scripts" / "calibration_ledger_bootstrap.py", pin

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

    def _open_bracket_session(self, session_id: str = "session-alpha"):
        return append_bracket_session_receipt(
            self.ledger,
            session_id=session_id,
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root=self.root / "another-root",
            slots={
                "pre": {
                    "attempt_id": f"{session_id}-pre",
                    "custody_locator": str(
                        self.root
                        / "another-root"
                        / "instrument_validation"
                        / f"{session_id}-pre"
                    ),
                    "identity_epoch": self.epoch,
                    "t1_bindings": self.t1,
                },
                "post": {
                    "attempt_id": f"{session_id}-post",
                    "custody_locator": str(
                        self.root
                        / "another-root"
                        / "instrument_validation"
                        / f"{session_id}-post"
                    ),
                    "identity_epoch": self.epoch,
                    "t1_bindings": self.t1,
                },
            },
            head_pin_path=self.pin,
            require_committed_pin=False,
        )

    def _finalize_bracket_slot(self, session_id: str, slot: str):
        attempt_id = f"{session_id}-{slot}"
        custody = (
            self.root / "another-root" / "instrument_validation" / attempt_id
        )
        if not custody.exists():
            custody = self._custody(attempt_id)
        return finalize_bracket_session_slot(
            self.ledger,
            session_id=session_id,
            slot=slot,
            disposition="valid",
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="99.0" if slot == "pre" else "111.0",
            exact_bound_lexeme_s="0.025",
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

    def test_unresolved_session_intent_refuses_terminal_read_then_repairs_append_only(
        self,
    ) -> None:
        self._open_bracket_session()
        custody = self._custody("session-alpha-pre")

        def stop_after_intent(stage):
            if stage == "intent":
                raise OSError("simulated process death after intent fsync")

        with mock.patch.object(
            calibration_ledger,
            "_after_ledger_fsync",
            side_effect=stop_after_intent,
        ):
            with self.assertRaisesRegex(OSError, "simulated process death"):
                finalize_bracket_session_slot(
                    self.ledger,
                    session_id="session-alpha",
                    slot="pre",
                    disposition="systematic-invalid",
                    custody_locator=str(custody),
                    artifact_sha256=artifact_hashes(custody),
                    identity_epoch=self.epoch,
                    t1_bindings=self.t1,
                    capture_wall_time_s="99.0",
                    exact_bound_lexeme_s="0.035435840879704805",
                )

        torn_bytes = self.ledger.read_bytes()
        with self.assertRaisesRegex(
            CalibrationLedgerError, "calibration_ledger_recovery_required"
        ):
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )

        calibration_ledger.repair_calibration_ledger(self.ledger)

        abort_bracket_session(
            self.ledger,
            session_id="session-alpha",
            reason="recover_torn_systematic_pre",
        )
        self.assertTrue(self.ledger.read_bytes().startswith(torn_bytes))
        self._write_pin(
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )
        )
        recovered = self._snapshot()
        self.assertEqual(recovered.refusal_reasons, ())
        self.assertEqual(recovered.bracket_sessions[0].state, "aborted")
        self.assertEqual(
            recovered.observations[0].disposition,
            "systematic-invalid",
        )

    def test_recovery_and_completed_operation_retry_are_idempotent(self) -> None:
        custody, _physical = self._persist_reservation_intent("idempotent")
        first = calibration_ledger.repair_calibration_ledger(self.ledger)
        bytes_after_first = self.ledger.read_bytes()
        second = calibration_ledger.repair_calibration_ledger(self.ledger)
        self.assertEqual(second, first)
        self.assertEqual(self.ledger.read_bytes(), bytes_after_first)
        repeated = self._reserve("idempotent", custody)
        self.assertEqual(repeated["attempt_id"], "idempotent")
        self.assertEqual(self.ledger.read_bytes(), bytes_after_first)

    def test_same_operation_key_with_different_target_fails_closed(self) -> None:
        custody = self.root / "conflict"
        self._reserve("conflict", custody)
        with self.assertRaisesRegex(
            CalibrationLedgerError, RefusalCode.LEDGER_OPERATION_CONFLICT.value
        ):
            append_pending_receipt(
                self.ledger,
                attempt_id="conflict",
                custody_locator=str(self.root / "different"),
                identity_epoch=self.epoch,
                t1_bindings=self.t1,
                head_pin_path=self.pin,
                require_committed_pin=False,
            )

    def test_terminal_session_pin_refuses_complete_unresolved_intent(self) -> None:
        self._open_bracket_session()
        self._finalize_bracket_slot("session-alpha", "pre")
        custody = self._custody("session-alpha-post")

        def stop_after_intent(stage):
            if stage == "intent":
                raise OSError("post intent durable")

        with mock.patch.object(
            calibration_ledger, "_after_ledger_fsync", side_effect=stop_after_intent
        ):
            with self.assertRaisesRegex(OSError, "post intent"):
                finalize_bracket_session_slot(
                    self.ledger,
                    session_id="session-alpha",
                    slot="post",
                    disposition="valid",
                    custody_locator=str(custody),
                    artifact_sha256=artifact_hashes(custody),
                    identity_epoch=self.epoch,
                    t1_bindings=self.t1,
                    capture_wall_time_s="111.0",
                    exact_bound_lexeme_s="0.025",
                )
        with self.assertRaisesRegex(
            CalibrationLedgerError, "calibration_ledger_recovery_required"
        ):
            terminal_head_pin_for_session(self.ledger, session_id="session-alpha")

    def test_terminal_session_pin_classifies_nonadmitted_residue(self) -> None:
        self._open_bracket_session()
        self.ledger.write_bytes(self.ledger.read_bytes() + b"malformed-residue")
        with self.assertRaisesRegex(
            CalibrationLedgerError, "calibration_ledger_recovery_required"
        ):
            terminal_head_pin_for_session(self.ledger, session_id="session-alpha")

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

    def test_production_writer_reserves_or_validates_before_capture_state_or_sampler(
        self,
    ) -> None:
        from scripts import validate_powermetrics_fiducial as writer

        custody = self.root / "behavioral-order" / "instrument_validation" / "attempt"
        lifecycle = writer._CaptureLedgerLifecycle(
            ledger_path=self.ledger,
            head_pin_path=self.pin,
            attempt_id="behavioral-order-attempt",
            custody_locator=str(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            require_committed_pin=False,
        )
        real_append = writer.append_pending_receipt
        observed_before_capture_state: list[bool] = []

        def observe_reservation(*args, **kwargs):
            observed_before_capture_state.append(not custody.exists())
            return real_append(*args, **kwargs)

        with mock.patch.object(
            writer,
            "append_pending_receipt",
            side_effect=observe_reservation,
        ):
            lifecycle.begin()
        self.assertEqual(observed_before_capture_state, [True])
        self.assertFalse(custody.exists())
        first = json.loads(self.ledger.read_text().splitlines()[1])
        self.assertEqual(first["event"], "reservation")
        self.assertEqual(first["disposition"], "pending")

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
        self.assertIn("calibration_ledger_head_mismatch", snapshot.refusal_reasons)
        self.assertEqual(final["receipt_digest"], snapshot.head_digest)
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
        first = self._finalize("single", custody)
        retry = self._finalize("single", custody)
        self.assertEqual(retry, first)

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

    def test_bracket_session_happy_path_reserves_two_slots_under_one_pin(self) -> None:
        capability = self._open_bracket_session()
        self.assertEqual(capability["sequence"], 2)
        self.assertEqual(tuple(capability["slots"]), ("pre", "post"))
        self.assertEqual(
            {slot["expected_time_role"] for slot in capability["slots"].values()},
            {"pre", "post"},
        )

        pre = self._finalize_bracket_slot("session-alpha", "pre")
        self.assertEqual(pre["sequence"], 4)
        self.assertEqual(pre["event"], BRACKET_SESSION_FINALIZATION_EVENT)
        post = self._finalize_bracket_slot("session-alpha", "post")
        self.assertEqual(post["sequence"], 6)

        pin = terminal_head_pin_for_session(
            self.ledger, session_id="session-alpha"
        )
        self.assertEqual(pin["sequence"], post["sequence"])
        self.assertEqual(pin["head_digest"], post["receipt_digest"])
        self._write_pin(pin)
        snapshot = self._snapshot()
        self.assertEqual(snapshot.refusal_reasons, ())
        self.assertEqual(snapshot.head_sequence, 6)
        self.assertEqual(
            [observation.bracket_slot for observation in snapshot.observations],
            ["pre", "post"],
        )
        session = snapshot.bracket_session_by_id["session-alpha"]
        self.assertEqual(session.state, "finalized")
        self.assertEqual(set(session.finalized_slots), {"pre", "post"})

    def test_bracket_session_refuses_reordered_duplicate_and_conflicting_slots(
        self,
    ) -> None:
        self._open_bracket_session()
        post_custody = self._custody("session-alpha-post")
        with self.assertRaisesRegex(CalibrationLedgerError, "expected pre"):
            finalize_bracket_session_slot(
                self.ledger,
                session_id="session-alpha",
                slot="post",
                disposition="valid",
                custody_locator=str(post_custody),
                artifact_sha256=artifact_hashes(post_custody),
                identity_epoch=self.epoch,
                t1_bindings=self.t1,
                capture_wall_time_s="111.0",
                exact_bound_lexeme_s="0.025",
            )
        self._finalize_bracket_slot("session-alpha", "pre")
        repeated = self._finalize_bracket_slot("session-alpha", "pre")
        self.assertEqual(repeated["slot"], "pre")

        conflicting_t1 = dict(self.t1)
        conflicting_t1["power_policy"] = "battery"
        with self.assertRaisesRegex(CalibrationLedgerError, "reserved session binding"):
            finalize_bracket_session_slot(
                self.ledger,
                session_id="session-alpha",
                slot="post",
                disposition="valid",
                custody_locator=str(post_custody),
                artifact_sha256=artifact_hashes(post_custody),
                identity_epoch=self.epoch,
                t1_bindings=conflicting_t1,
                capture_wall_time_s="111.0",
                exact_bound_lexeme_s="0.025",
            )

    def test_generic_head_pin_refuses_session_open_and_pre_receipts(self) -> None:
        capability = self._open_bracket_session()
        with self.assertRaisesRegex(
            CalibrationLedgerError, "terminal_head_pin_for_session"
        ):
            head_pin_for_receipt(capability)
        pre = self._finalize_bracket_slot("session-alpha", "pre")
        with self.assertRaisesRegex(
            CalibrationLedgerError, "terminal_head_pin_for_session"
        ):
            head_pin_for_receipt(pre)

    def test_aborted_systematic_pre_remains_in_r2_universe_and_fires_trigger(
        self,
    ) -> None:
        self._open_bracket_session()
        custody = self._custody("session-alpha-pre")
        finalize_bracket_session_slot(
            self.ledger,
            session_id="session-alpha",
            slot="pre",
            disposition="systematic-invalid",
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="99.0",
            exact_bound_lexeme_s="0.035435840879704805",
        )
        abort_bracket_session(
            self.ledger,
            session_id="session-alpha",
            reason="pre_capture_systematic-invalid",
        )
        self._write_pin(
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )
        )
        snapshot = self._snapshot()
        self.assertEqual(len(snapshot.observations), 1)
        self.assertEqual(snapshot.observations[0].disposition, "systematic-invalid")
        self.assertEqual(snapshot.bracket_sessions[0].state, "aborted")

        with mock.patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            result, reasons = evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.t1,
                policy=CalibrationBracketingPolicy(
                    require_bracket=True,
                    calibration_bracket_max_drift_s=0.010,
                ),
                ledger_snapshot=snapshot,
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertIn(
            "new_systematic_failure_challenges_preflight_screen",
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
        )
    def test_open_session_refuses_until_governed_abort_and_never_deletes_partial(
        self,
    ) -> None:
        self._open_bracket_session()
        pre = self._finalize_bracket_slot("session-alpha", "pre")
        open_snapshot = self._snapshot()
        self.assertIn(
            "calibration_ledger_bracket_session_open",
            open_snapshot.refusal_reasons,
        )
        self.assertEqual(
            [observation.bracket_slot for observation in open_snapshot.observations],
            [],
        )

        closure = abort_bracket_session(
            self.ledger,
            session_id="session-alpha",
            reason="science_member_failed_before_post",
        )
        self.assertEqual(closure["event"], BRACKET_SESSION_ABORT_EVENT)
        self.assertEqual(closure["finalized_slots"], ("pre",))
        self.assertEqual(closure["unused_slots"], ("post",))
        self._write_pin(
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )
        )
        snapshot = self._snapshot()
        self.assertEqual(snapshot.refusal_reasons, ())
        self.assertEqual(
            [observation.bracket_slot for observation in snapshot.observations],
            ["pre"],
        )
        self.assertEqual(
            snapshot.observations[0].observation_kind,
            "bracket-session-aborted",
        )
        session = snapshot.bracket_session_by_id["session-alpha"]
        self.assertEqual(session.state, "aborted")
        self.assertEqual(session.finalized_slots["pre"].receipt_digest, pre["receipt_digest"])
        with self.assertRaisesRegex(
            CalibrationLedgerError, RefusalCode.LEDGER_OPERATION_CONFLICT.value
        ):
            abort_bracket_session(
                self.ledger,
                session_id="session-alpha",
                reason="duplicate closure",
            )

    def test_bracket_session_open_requires_exact_committed_physical_head(self) -> None:
        self._open_bracket_session()
        with self.assertRaisesRegex(
            CalibrationLedgerError, "physical ledger head differs from the committed pin"
        ):
            self._open_bracket_session("session-beta")

    def test_bracket_reservation_cli_is_explicit_and_machine_readable(self) -> None:
        epoch_path = self.root / "epoch.json"
        t1_path = self.root / "t1.json"
        epoch_path.write_text(json.dumps(self.epoch), encoding="utf-8")
        t1_path.write_text(json.dumps(self.t1), encoding="utf-8")
        argv = [
            "--ledger",
            str(self.ledger),
            "--head-pin",
            str(self.pin),
            "--session-id",
            "session-cli",
            "--window-id",
            "window-cli",
            "--plan-id",
            "plan-cli",
            "--plan-sha256",
            "b" * 64,
            "--evidence-root-id",
            "evidence-cli",
            "--runs-root",
            str(self.root / "cli-runs"),
            "--pre-attempt-id",
            "session-cli-pre",
            "--post-attempt-id",
            "session-cli-post",
            "--pre-custody-locator",
            str(self.root / "cli-runs" / "instrument_validation" / "session-cli-pre"),
            "--post-custody-locator",
            str(self.root / "cli-runs" / "instrument_validation" / "session-cli-post"),
            "--identity-epoch-json",
            str(epoch_path),
            "--t1-bindings-json",
            str(t1_path),
            "--allow-uncommitted-pin-for-test",
        ]
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(bracket_session_cli.main(argv), 0)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "validated_not_reserved")
        self.assertFalse(self.ledger.exists())

        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(bracket_session_cli.main([*argv, "--execute"]), 0)
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["status"], "reserved")
        self.assertEqual(output["receipt"]["event"], "bracket-session-open")
        self.assertEqual(output["terminal_head_pin"], None)
        self.assertTrue(self.ledger.is_file())

    def test_bracket_reservation_cli_dry_run_and_execute_share_malformed_input_refusal(
        self,
    ) -> None:
        epoch_path = self.root / "bad-cli-epoch.json"
        t1_path = self.root / "bad-cli-t1.json"
        epoch_path.write_text(json.dumps(self.epoch), encoding="utf-8")
        t1_path.write_text(json.dumps(self.t1), encoding="utf-8")
        runs_root = self.root / "bad-cli-runs"
        argv = [
            "--ledger", str(self.ledger),
            "--head-pin", str(self.pin),
            "--session-id", "session-bad-cli",
            "--window-id", "",
            "--plan-id", "plan-bad-cli",
            "--plan-sha256", "b" * 64,
            "--evidence-root-id", "evidence-bad-cli",
            "--runs-root", str(runs_root),
            "--pre-attempt-id", "session-bad-cli-pre",
            "--post-attempt-id", "session-bad-cli-post",
            "--pre-custody-locator",
            str(runs_root / "instrument_validation" / "session-bad-cli-pre"),
            "--post-custody-locator",
            str(runs_root / "instrument_validation" / "session-bad-cli-post"),
            "--identity-epoch-json", str(epoch_path),
            "--t1-bindings-json", str(t1_path),
            "--allow-uncommitted-pin-for-test",
        ]
        for execute in (False, True):
            with self.subTest(execute=execute), mock.patch(
                "sys.stderr", new_callable=io.StringIO
            ) as stderr:
                self.assertEqual(
                    bracket_session_cli.main(
                        [*argv, "--execute"] if execute else argv
                    ),
                    2,
                )
                self.assertIn("malformed", stderr.getvalue())
        self.assertFalse(self.ledger.exists())

    def test_terminal_session_head_refuses_rollback_and_nonterminal_extension(self) -> None:
        self._open_bracket_session()
        self._finalize_bracket_slot("session-alpha", "pre")
        post = self._finalize_bracket_slot("session-alpha", "post")
        lines = self.ledger.read_bytes().splitlines(keepends=True)
        self.ledger.write_bytes(b"".join(lines[:-1]))
        with self.assertRaisesRegex(
            CalibrationLedgerError, RefusalCode.LEDGER_RECOVERY_REQUIRED.value
        ):
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )
        self.ledger.write_bytes(b"".join(lines))
        self._write_pin(
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )
        )
        ordinary_custody = self._custody("later-ordinary")
        pending = append_pending_receipt(
            self.ledger,
            attempt_id="later-ordinary",
            custody_locator=str(ordinary_custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            head_pin_path=self.pin,
            require_committed_pin=False,
        )
        self.assertEqual(pending["sequence"], 8)
        with self.assertRaisesRegex(CalibrationLedgerError, "pending"):
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )

    def test_phase_readiness_requires_under_lease_gate_and_disposes_custody(self) -> None:
        pre_reserve = calibration_ledger.calibration_readiness(
            self.ledger,
            self.pin,
            phase="pre-reserve",
            require_committed_pin=False,
        )
        self.assertEqual(pre_reserve.status, "ready")
        self.assertFalse(pre_reserve.as_dict()["authorizes_arm"])

        self._open_bracket_session()
        warning = calibration_ledger.calibration_readiness(
            self.ledger,
            self.pin,
            phase="pre-slot",
            session_id="session-alpha",
            slot="pre",
            attempt_id="session-alpha-pre",
            require_committed_pin=False,
        )
        self.assertEqual(warning.status, "ready")
        self.assertEqual(warning.claim_state, "absent")
        self.assertFalse(warning.as_dict()["authorizes_arm"])

        with calibration_ledger.CalibrationWriterLease(self.ledger):
            enforcing = calibration_ledger.calibration_readiness(
                self.ledger,
                self.pin,
                phase="pre-slot",
                session_id="session-alpha",
                slot="pre",
                attempt_id="session-alpha-pre",
                enforcing_under_lease=True,
                require_committed_pin=False,
            )
            self.assertTrue(enforcing.as_dict()["authorizes_arm"])
            calibration_ledger.claim_bracket_session_slot(
                self.ledger,
                session_id="session-alpha",
                slot="pre",
                attempt_id="session-alpha-pre",
            )
            idempotent = calibration_ledger.calibration_readiness(
                self.ledger,
                self.pin,
                phase="pre-slot",
                session_id="session-alpha",
                slot="pre",
                attempt_id="session-alpha-pre",
                enforcing_under_lease=True,
                require_committed_pin=False,
            )
            self.assertEqual(idempotent.claim_state, "exact_completed")
            self.assertTrue(idempotent.as_dict()["authorizes_arm"])

        custody = (
            self.root
            / "another-root"
            / "instrument_validation"
            / "session-alpha-pre"
        )
        custody.mkdir(parents=True)
        with calibration_ledger.CalibrationWriterLease(self.ledger):
            partial = calibration_ledger.calibration_readiness(
                self.ledger,
                self.pin,
                phase="pre-slot",
                session_id="session-alpha",
                slot="pre",
                attempt_id="session-alpha-pre",
                enforcing_under_lease=True,
                require_committed_pin=False,
            )
        self.assertEqual(partial.refusal_code, RefusalCode.CUSTODY_PARTIAL)

        custody.rmdir()
        legacy = self.ledger.with_name(f"{self.ledger.name}.append-journal")
        legacy.write_bytes(b"")
        with calibration_ledger.CalibrationWriterLease(self.ledger):
            journal_blocked = calibration_ledger.calibration_readiness(
                self.ledger,
                self.pin,
                phase="pre-slot",
                session_id="session-alpha",
                slot="pre",
                attempt_id="session-alpha-pre",
                enforcing_under_lease=True,
                require_committed_pin=False,
            )
        self.assertEqual(journal_blocked.status, "blocked")
        self.assertIsNotNone(
            calibration_ledger.inspect_calibration_ledger(
                self.ledger
            ).legacy_journal_path
        )

    def test_enforcing_post_readiness_refuses_deleted_finalized_pre_custody(self) -> None:
        self._open_bracket_session()
        calibration_ledger.claim_bracket_session_slot(
            self.ledger,
            session_id="session-alpha",
            slot="pre",
            attempt_id="session-alpha-pre",
        )
        self._finalize_bracket_slot("session-alpha", "pre")
        pre_custody = (
            self.root
            / "another-root"
            / "instrument_validation"
            / "session-alpha-pre"
        )
        (pre_custody / "manifest.json").unlink()

        with calibration_ledger.CalibrationWriterLease(self.ledger):
            readiness = calibration_ledger.calibration_readiness(
                self.ledger,
                self.pin,
                phase="pre-slot",
                session_id="session-alpha",
                slot="post",
                attempt_id="session-alpha-post",
                enforcing_under_lease=True,
                require_committed_pin=False,
            )
        self.assertEqual(
            readiness.refusal_code, RefusalCode.LEDGER_CUSTODY_INVALID
        )
        self.assertFalse(readiness.as_dict()["authorizes_arm"])
        self.assertIsNone(readiness.as_dict()["terminal_result"])

    def test_sessionless_pin_advancement_refuses_pending_business_head(self) -> None:
        self._reserve("pending-business-head", self.root / "pending-custody")
        inspection = calibration_ledger.inspect_calibration_ledger(self.ledger)
        with self.assertRaises(CalibrationLedgerError) as raised:
            calibration_ledger.advance_calibration_head_pin(
                self.ledger,
                self.pin,
                session_id=None,
                expected_sequence=inspection.head_sequence,
                expected_digest=inspection.head_digest,
                operator_identity="desk-operator",
                attestation_reason="must reject an ordinary pending head",
                execute=False,
                require_committed_pin=False,
            )
        self.assertEqual(raised.exception.code, RefusalCode.PIN_ADVANCEMENT_UNSAFE)

    def test_guarded_terminal_pin_advancement_reaches_terminal_readiness(self) -> None:
        self._open_bracket_session()
        abort_bracket_session(
            self.ledger,
            session_id="session-alpha",
            reason="guarded-pin-test",
        )
        before = calibration_ledger.calibration_readiness(
            self.ledger,
            self.pin,
            phase="terminal",
            session_id="session-alpha",
            require_committed_pin=False,
        )
        self.assertEqual(before.status, "ready")
        self.assertTrue(before.needs_pin_commit)
        assert before.head_pin_candidate is not None
        candidate = dict(before.head_pin_candidate)
        dry_run = calibration_ledger.advance_calibration_head_pin(
            self.ledger,
            self.pin,
            session_id="session-alpha",
            expected_sequence=candidate["sequence"],
            expected_digest=candidate["head_digest"],
            operator_identity="desk-operator",
            attestation_reason="reviewed exact terminal candidate",
            execute=False,
            require_committed_pin=False,
        )
        self.assertFalse(dry_run["executed"])
        calibration_ledger.advance_calibration_head_pin(
            self.ledger,
            self.pin,
            session_id="session-alpha",
            expected_sequence=candidate["sequence"],
            expected_digest=candidate["head_digest"],
            operator_identity="desk-operator",
            attestation_reason="reviewed exact terminal candidate",
            execute=True,
            require_committed_pin=False,
        )
        after = calibration_ledger.calibration_readiness(
            self.ledger,
            self.pin,
            phase="terminal",
            session_id="session-alpha",
            require_committed_pin=False,
        )
        self.assertEqual(after.status, "ready")
        self.assertEqual(after.pin_relation, calibration_ledger.PinRelation.EXACT)
        self.assertFalse(after.needs_pin_commit)

    def test_session_snapshot_loader_refuses_rollback_against_committed_terminal_pin(
        self,
    ) -> None:
        self._open_bracket_session()
        self._finalize_bracket_slot("session-alpha", "pre")
        self._finalize_bracket_slot("session-alpha", "post")
        self._write_pin(
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )
        )
        self.assertEqual(self._snapshot().refusal_reasons, ())
        lines = self.ledger.read_bytes().splitlines(keepends=True)
        self.ledger.write_bytes(b"".join(lines[:-1]))

        rolled_back = self._snapshot(verify_custody=False)
        self.assertIn("calibration_ledger_rollback", rolled_back.refusal_reasons)
        self.assertIn(
            "calibration_ledger_bracket_session_open",
            rolled_back.refusal_reasons,
        )

    def test_conflicting_session_identity_and_session_fork_refuse(self) -> None:
        self._open_bracket_session()
        self._finalize_bracket_slot("session-alpha", "pre")
        post = self._finalize_bracket_slot("session-alpha", "post")
        clean_lines = self.ledger.read_bytes().splitlines(keepends=True)

        conflicting = json.loads(clean_lines[-1])
        conflicting["window_id"] = "window-substituted"
        conflicting["receipt_digest"] = canonical_sha256(
            {
                key: value
                for key, value in conflicting.items()
                if key != "receipt_digest"
            }
        )
        self.ledger.write_bytes(
            b"".join(clean_lines[:-1]) + canonical_json_bytes(conflicting) + b"\n"
        )
        with self.assertRaisesRegex(
            CalibrationLedgerError, "terminal_head_pin_for_session"
        ):
            head_pin_for_receipt(conflicting)
        self._write_pin(
            {
                "sequence": conflicting["sequence"],
                "head_digest": conflicting["receipt_digest"],
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        conflict_snapshot = self._snapshot(verify_custody=False)
        self.assertIn(
            "calibration_ledger_operation_conflict",
            conflict_snapshot.refusal_reasons,
        )

        forked = json.loads(clean_lines[-1])
        forked["predecessor_digest"] = json.loads(clean_lines[0])[
            "receipt_digest"
        ]
        forked["receipt_digest"] = canonical_sha256(
            {
                key: value
                for key, value in forked.items()
                if key != "receipt_digest"
            }
        )
        self.ledger.write_bytes(
            b"".join(clean_lines[:-1]) + canonical_json_bytes(forked) + b"\n"
        )
        self._write_pin(
            {
                "sequence": forked["sequence"],
                "head_digest": forked["receipt_digest"],
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        fork_snapshot = self._snapshot(verify_custody=False)
        self.assertIn(
            "calibration_ledger_chain_conflict", fork_snapshot.refusal_reasons
        )
        self.assertEqual(post["slot"], "post")

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
        script, head_pin = self._isolated_cli_checkout()
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
            str(head_pin),
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
        self.assertEqual(rows[-1]["outcome"], "planned")
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

    @unittest.skipUnless(
        _REAL_D079_TABLE.is_file() and _REAL_D079_CUSTODY_MANIFEST.is_file(),
        "lead-reviewed D-079 import inputs are unavailable",
    )
    def test_d079_issued_artifact_mode_is_deterministic_and_write_explicit(
        self,
    ) -> None:
        script, head_pin = self._isolated_cli_checkout()
        dry_ledger = self.root / "issued-mode-ledger.jsonl"
        emitted_path = self.root / "issued-acceptance.json"
        source_path = self.root / "unissued-acceptance.json"
        source_raw = _unissued_acceptance_fixture_bytes()
        source_path.write_bytes(source_raw)
        command = [
            sys.executable,
            str(script),
            "--disposition-table",
            str(_REAL_D079_TABLE),
            "--expected-table-sha256",
            _REAL_D079_TABLE_SHA256,
            "--custody-manifest",
            str(_REAL_D079_CUSTODY_MANIFEST),
            "--expected-custody-manifest-sha256",
            _REAL_D079_CUSTODY_MANIFEST_SHA256,
            "--checkout-root",
            "/Users/edr",
            "--ledger",
            str(dry_ledger),
            "--head-pin",
            str(head_pin),
            "--acceptance-artifact",
            str(source_path),
            "--prepare-issued-artifact",
        ]
        first = subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(first.stderr, b"")
        self.assertFalse(dry_ledger.exists())
        self.assertFalse(emitted_path.exists())
        rows = [json.loads(line) for line in first.stdout.splitlines()]
        issued = next(
            row for row in rows if row["record"] == "issued-acceptance-artifact"
        )
        summary = rows[-1]
        self.assertEqual(summary["record"], "bootstrap-summary")
        self.assertEqual(summary["final_sequence"], 76)
        self.assertEqual(
            summary["head_digest"],
            "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",
        )
        self.assertEqual(
            issued["derivation_sha256"], _ISSUED_D079_DERIVATION_SHA256
        )
        self.assertEqual(issued["artifact_file_sha256"], _ISSUED_D079_FILE_SHA256)
        self.assertEqual(
            len(issued["artifact"]["prior_observation_set"]["observations"]),
            38,
        )
        self.assertEqual(issued["artifact"]["derivation_corpus"]["n"], 19)

        plan = prepare_historical_import(
            checkout_root=Path("/Users/edr"),
            disposition_table_raw=_REAL_D079_TABLE.read_bytes(),
            expected_disposition_table_sha256=_REAL_D079_TABLE_SHA256,
            custody_manifest_raw=_REAL_D079_CUSTODY_MANIFEST.read_bytes(),
            expected_custody_manifest_sha256=(
                _REAL_D079_CUSTODY_MANIFEST_SHA256
            ),
        )
        issued_receipts, issued_reasons = calibration_ledger._parse_ledger(
            plan.ledger_bytes
        )
        self.assertEqual(issued_reasons, set())
        self.assertEqual(len(issued_receipts), 76)
        self.assertEqual(
            next(reversed(issued_receipts))["receipt_digest"], plan.head_digest
        )
        source = _unissued_acceptance_fixture()
        reversed_source = dict(reversed(tuple(source.items())))
        canonical_artifact = bootstrap_cli._issued_acceptance_artifact(
            plan, source, source_artifact_raw=source_raw
        )
        reordered_artifact = bootstrap_cli._issued_acceptance_artifact(
            plan, reversed_source, source_artifact_raw=source_raw
        )
        canonical_bytes = bootstrap_cli._issued_artifact_bytes(
            canonical_artifact
        )
        reordered_bytes = bootstrap_cli._issued_artifact_bytes(
            reordered_artifact
        )
        self.assertEqual(canonical_bytes, reordered_bytes)
        self.assertEqual(
            hashlib.sha256(reordered_bytes).hexdigest(),
            _ISSUED_D079_FILE_SHA256,
        )

        class BinaryOutput:
            def __init__(self) -> None:
                self.buffer = io.BytesIO()

        success_stdout = BinaryOutput()
        with mock.patch.object(
            bootstrap_cli,
            "_issued_artifact_bytes",
            wraps=bootstrap_cli._issued_artifact_bytes,
        ) as serialize:
            prepared = bootstrap_cli._prepare_issued_acceptance_artifact(
                plan, source, source_artifact_raw=source_raw
            )
            with mock.patch.object(bootstrap_cli.sys, "stdout", success_stdout):
                bootstrap_cli._emit(
                    plan,
                    executed=True,
                    outcome="committed",
                    prepared_issued_artifact=prepared,
                )
        self.assertEqual(serialize.call_count, 1)
        success_rows = [
            json.loads(line)
            for line in success_stdout.buffer.getvalue().splitlines()
        ]
        self.assertEqual(
            success_rows[-2]["artifact_file_sha256"],
            _ISSUED_D079_FILE_SHA256,
        )
        self.assertEqual(
            success_rows[-1]["issued_artifact_file_sha256"],
            _ISSUED_D079_FILE_SHA256,
        )

        emit_command = [
            argument
            for argument in command
            if argument != "--prepare-issued-artifact"
        ]
        emit_command.extend(["--emit-issued-artifact", str(emitted_path)])
        emitted = subprocess.run(emit_command, check=True, capture_output=True)
        self.assertFalse(dry_ledger.exists())
        self.assertTrue(emitted_path.is_file())
        self.assertEqual(
            hashlib.sha256(emitted_path.read_bytes()).hexdigest(),
            _ISSUED_D079_FILE_SHA256,
        )
        emitted_rows = [json.loads(line) for line in emitted.stdout.splitlines()]
        self.assertEqual(
            emitted_rows[-1]["issued_artifact_derivation_sha256"],
            _ISSUED_D079_DERIVATION_SHA256,
        )

    def test_issued_artifact_rejects_self_consistent_unpinned_template(
        self,
    ) -> None:
        source = load_calibration_acceptance_bound()
        self.assertIsNotNone(source)
        tampered = json.loads(json.dumps(source))
        tampered["issuance"]["reason"] = "self-consistent but unauthenticated"
        tampered["derivation_sha256"] = acceptance_canonical_sha256(
            {
                key: value
                for key, value in tampered.items()
                if key != "derivation_sha256"
            }
        )
        self.assertTrue(_valid_acceptance_bound(tampered))

        with self.assertRaisesRegex(ValueError, "role-indexed byte pin"):
            bootstrap_cli._issued_acceptance_artifact(object(), tampered)

    def test_execute_invalid_artifact_source_refuses_without_ledger_write(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        table_path = self.root / "invalid-source-dispositions.json"
        table_path.write_bytes(import_args["disposition_table_raw"])
        manifest_path = self.root / "invalid-source-custody.json"
        manifest_path.write_bytes(import_args["custody_manifest_raw"])
        source = load_calibration_acceptance_bound()
        self.assertIsNotNone(source)
        tampered = json.loads(json.dumps(source))
        tampered["issuance"]["reason"] = "invalid source must precede commit"
        tampered["derivation_sha256"] = acceptance_canonical_sha256(
            {
                key: value
                for key, value in tampered.items()
                if key != "derivation_sha256"
            }
        )
        self.assertTrue(_valid_acceptance_bound(tampered))
        source_path = self.root / "invalid-source.json"
        source_path.write_text(json.dumps(tampered), encoding="utf-8")
        ledger = self.root / "must-remain-absent.jsonl"
        script = Path(__file__).resolve().parents[1] / "scripts" / (
            "calibration_ledger_bootstrap.py"
        )

        refused = subprocess.run(
            [
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
                str(ledger),
                "--head-pin",
                str(self.pin),
                "--acceptance-artifact",
                str(source_path),
                "--prepare-issued-artifact",
                "--execute",
                str(root),
            ],
            check=False,
            capture_output=True,
        )

        self.assertEqual(refused.returncode, 2)
        self.assertIn(b"role-indexed byte pin", refused.stderr)
        self.assertFalse(ledger.exists())

    def test_issued_artifact_mid_write_failure_preserves_destination(self) -> None:
        payload = b'{"artifact":"complete"}\n'

        def partial_write_then_fail(handle, raw):
            handle.write(raw[: len(raw) // 2])
            handle.flush()
            raise OSError("injected issued-artifact mid-write failure")

        for name, prior in (("existing", b"prior-anchor\n"), ("absent", None)):
            with self.subTest(destination=name):
                destination = self.root / f"{name}-issued.json"
                if prior is not None:
                    destination.write_bytes(prior)
                with mock.patch.object(
                    bootstrap_cli,
                    "_write_issued_artifact_payload",
                    side_effect=partial_write_then_fail,
                ):
                    with self.assertRaisesRegex(OSError, "mid-write"):
                        bootstrap_cli._atomic_emit_issued_artifact(
                            destination, payload
                        )
                if prior is None:
                    self.assertFalse(destination.exists())
                else:
                    self.assertEqual(destination.read_bytes(), prior)

    def test_historical_input_digest_pair_changes_committed_chain(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        original = prepare_historical_import(
            roots=[root], checkout_root=checkout, **import_args
        )

        compact_table_raw = canonical_json_bytes(table)
        self.assertEqual(json.loads(compact_table_raw), json.loads(
            import_args["disposition_table_raw"]
        ))
        self.assertNotEqual(
            hashlib.sha256(compact_table_raw).hexdigest(),
            import_args["expected_disposition_table_sha256"],
        )
        table_reformatted = prepare_historical_import(
            roots=[root],
            checkout_root=checkout,
            **{
                **import_args,
                "disposition_table_raw": compact_table_raw,
                "expected_disposition_table_sha256": hashlib.sha256(
                    compact_table_raw
                ).hexdigest(),
            },
        )

        compact_manifest_raw = canonical_json_bytes(
            json.loads(import_args["custody_manifest_raw"])
        )
        self.assertNotEqual(
            hashlib.sha256(compact_manifest_raw).hexdigest(),
            import_args["expected_custody_manifest_sha256"],
        )
        manifest_reformatted = prepare_historical_import(
            roots=[root],
            checkout_root=checkout,
            **{
                **import_args,
                "custody_manifest_raw": compact_manifest_raw,
                "expected_custody_manifest_sha256": hashlib.sha256(
                    compact_manifest_raw
                ).hexdigest(),
            },
        )

        self.assertNotEqual(original.ledger_bytes, table_reformatted.ledger_bytes)
        self.assertNotEqual(original.head_digest, table_reformatted.head_digest)
        self.assertNotEqual(original.ledger_bytes, manifest_reformatted.ledger_bytes)
        self.assertNotEqual(original.head_digest, manifest_reformatted.head_digest)
        import_receipts = (
            receipt
            for receipt in original.receipts
            if "historical_import_input_sha256" in receipt
        )
        for receipt in import_receipts:
            self.assertEqual(
                dict(receipt["historical_import_input_sha256"]),
                {
                    "disposition_table": import_args[
                        "expected_disposition_table_sha256"
                    ],
                    "custody_manifest": import_args[
                        "expected_custody_manifest_sha256"
                    ],
                },
            )

    def test_reformatted_table_cannot_confirm_or_execute_existing_chain(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        original = prepare_historical_import(
            roots=[root], checkout_root=checkout, **import_args
        )
        self.ledger.write_bytes(original.ledger_bytes)
        compact_table_raw = canonical_json_bytes(table)
        reformatted_args = {
            **import_args,
            "disposition_table_raw": compact_table_raw,
            "expected_disposition_table_sha256": hashlib.sha256(
                compact_table_raw
            ).hexdigest(),
        }
        reformatted = prepare_historical_import(
            roots=[root], checkout_root=checkout, **reformatted_args
        )

        with self.assertRaisesRegex(CalibrationLedgerError, "empty ledger"):
            calibration_ledger._require_genesis_bootstrap_state(
                self.ledger,
                self.pin,
                require_committed_pin=False,
                repo_root=checkout,
                expected_payload=reformatted.ledger_bytes,
            )
        with self.assertRaisesRegex(CalibrationLedgerError, "empty ledger"):
            bootstrap_historical_import(
                self.ledger,
                head_pin_path=self.pin,
                roots=[root],
                checkout_root=checkout,
                **reformatted_args,
                execute=True,
                require_committed_pin=False,
            )
        self.assertEqual(self.ledger.read_bytes(), original.ledger_bytes)

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

    def test_post_replace_dir_fsync_fault_is_committed_and_retry_confirms(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        real_fsync = calibration_ledger.os.fsync
        fsync_calls = 0

        def fail_both_directory_fsyncs(descriptor):
            nonlocal fsync_calls
            fsync_calls += 1
            if fsync_calls >= 2:
                raise OSError("injected post-replace directory fsync")
            return real_fsync(descriptor)

        with mock.patch.object(
            calibration_ledger.os,
            "fsync",
            side_effect=fail_both_directory_fsyncs,
        ):
            with self.assertRaises(HistoricalImportDurabilityUncertain) as raised:
                bootstrap_historical_import(
                    self.ledger,
                    head_pin_path=self.pin,
                    roots=[root],
                    checkout_root=checkout,
                    **import_args,
                    execute=True,
                    require_committed_pin=False,
                )
        plan = raised.exception.plan
        self.assertEqual(
            raised.exception.outcome, "committed_durability_uncertain"
        )
        self.assertEqual(fsync_calls, 3)
        self.assertEqual(self.ledger.read_bytes(), plan.ledger_bytes)

        with mock.patch.object(calibration_ledger.os, "replace") as replace_mock:
            confirmed = bootstrap_historical_import(
                self.ledger,
                head_pin_path=self.pin,
                roots=[root],
                checkout_root=checkout,
                **import_args,
                execute=True,
                require_committed_pin=False,
            )
        replace_mock.assert_not_called()
        self.assertEqual(confirmed.head_digest, plan.head_digest)
        self.assertEqual(self.ledger.read_bytes(), plan.ledger_bytes)

        self._write_pin(dict(plan.head_pin))
        with self.assertRaisesRegex(CalibrationLedgerError, "genesis head pin"):
            bootstrap_historical_import(
                self.ledger,
                head_pin_path=self.pin,
                roots=[root],
                checkout_root=checkout,
                **import_args,
                execute=True,
                require_committed_pin=False,
            )

    def test_durability_uncertain_cli_emits_full_summary_and_distinct_exit(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        plan = prepare_historical_import(
            roots=[root], checkout_root=checkout, **import_args
        )
        table_path = self.root / "uncertain-dispositions.json"
        table_path.write_bytes(import_args["disposition_table_raw"])
        manifest_path = self.root / "uncertain-custody-manifest.json"
        manifest_path.write_bytes(import_args["custody_manifest_raw"])

        class BinaryOutput:
            def __init__(self) -> None:
                self.buffer = io.BytesIO()

        stdout = BinaryOutput()
        stderr = io.StringIO()
        emitted_path = self.root / "uncertain-issued.json"
        issued_artifact = {"derivation_sha256": "d" * 64}
        issued_raw = bootstrap_cli._issued_artifact_bytes(issued_artifact)
        issued_file_sha256 = hashlib.sha256(issued_raw).hexdigest()
        issued_record = {
            "schema_version": bootstrap_cli.ISSUED_ARTIFACT_OUTPUT_SCHEMA,
            "record": "issued-acceptance-artifact",
            "artifact": issued_artifact,
            "derivation_sha256": issued_artifact["derivation_sha256"],
            "artifact_file_sha256": issued_file_sha256,
            "artifact_file_content": issued_raw.decode("utf-8"),
        }
        prepared_issued_artifact = (
            bootstrap_cli.PreparedIssuedAcceptanceArtifact(
                artifact_file_bytes=issued_raw,
                artifact_file_sha256=issued_file_sha256,
                derivation_sha256=issued_artifact["derivation_sha256"],
                output_record_bytes=canonical_json_bytes(issued_record) + b"\n",
                summary_fields=(
                    (
                        "issued_artifact_derivation_sha256",
                        issued_artifact["derivation_sha256"],
                    ),
                    ("issued_artifact_file_sha256", issued_file_sha256),
                ),
            )
        )
        argv = [
            "calibration_ledger_bootstrap.py",
            "--disposition-table",
            str(table_path),
            "--expected-table-sha256",
            import_args["expected_disposition_table_sha256"],
            "--custody-manifest",
            str(manifest_path),
            "--expected-custody-manifest-sha256",
            import_args["expected_custody_manifest_sha256"],
            "--ledger",
            str(self.ledger),
            "--head-pin",
            str(self.pin),
            "--emit-issued-artifact",
            str(emitted_path),
            "--execute",
            str(root),
        ]
        with (
            mock.patch.object(bootstrap_cli.sys, "argv", argv),
            mock.patch.object(bootstrap_cli.sys, "stdout", stdout),
            mock.patch.object(bootstrap_cli.sys, "stderr", stderr),
            mock.patch.object(
                bootstrap_cli,
                "prepare_historical_import",
                return_value=plan,
            ),
            mock.patch.object(
                bootstrap_cli,
                "_prepare_issued_acceptance_artifact",
                return_value=prepared_issued_artifact,
            ),
            mock.patch.object(
                bootstrap_cli,
                "bootstrap_historical_import",
                side_effect=HistoricalImportDurabilityUncertain(plan),
            ),
            mock.patch.object(
                bootstrap_cli,
                "_issued_artifact_bytes",
                side_effect=ValueError(
                    "injected post-commit artifact serialization"
                ),
            ) as serialize,
        ):
            exit_code = bootstrap_cli.main()
        serialize.assert_not_called()
        self.assertEqual(exit_code, bootstrap_cli.DURABILITY_UNCERTAIN_EXIT)
        self.assertNotEqual(exit_code, 2)
        rows = [json.loads(line) for line in stdout.buffer.getvalue().splitlines()]
        self.assertEqual(len(rows), len(plan.receipts) + 2)
        self.assertEqual(rows[-2]["record"], "issued-acceptance-artifact")
        self.assertEqual(rows[-1]["record"], "bootstrap-summary")
        self.assertTrue(rows[-1]["executed"])
        self.assertEqual(
            rows[-1]["outcome"], "committed_durability_uncertain"
        )
        self.assertEqual(rows[-1]["head_digest"], plan.head_digest)
        self.assertEqual(
            rows[-1]["disposition_table_sha256"],
            plan.disposition_table_sha256,
        )
        self.assertEqual(
            rows[-1]["custody_manifest_sha256"],
            plan.custody_manifest_sha256,
        )
        self.assertEqual(
            rows[-1]["issued_artifact_file_sha256"], issued_file_sha256
        )
        self.assertEqual(emitted_path.read_bytes(), issued_raw)
        self.assertIn("rerun the identical --execute invocation", stderr.getvalue())

    def test_tampered_nonempty_ledger_never_enters_confirm_path(self) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        plan = prepare_historical_import(
            roots=[root], checkout_root=checkout, **import_args
        )
        self.ledger.write_bytes(plan.ledger_bytes + b"tampered\n")
        with mock.patch.object(calibration_ledger, "_fsync_parent_directory") as sync:
            with self.assertRaisesRegex(CalibrationLedgerError, "empty ledger"):
                bootstrap_historical_import(
                    self.ledger,
                    head_pin_path=self.pin,
                    roots=[root],
                    checkout_root=checkout,
                    **import_args,
                    execute=True,
                    require_committed_pin=False,
                )
        sync.assert_not_called()
        self.assertEqual(self.ledger.read_bytes(), plan.ledger_bytes + b"tampered\n")

    def test_stable_lock_serializes_replace_against_waiting_old_writer(
        self,
    ) -> None:
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        self.ledger.write_bytes(b"")
        lock_path = calibration_ledger._ledger_lock_path(self.ledger)
        bootstrap_locked = threading.Event()
        allow_replace = threading.Event()
        writer_waiting = threading.Event()
        real_reauthenticate = calibration_ledger._reauthenticate_historical_import_plan
        real_flock = calibration_ledger.fcntl.flock
        bootstrap_results = []
        bootstrap_errors = []
        writer_results = []
        writer_errors = []

        def pause_with_bootstrap_lock(plan):
            bootstrap_locked.set()
            if not allow_replace.wait(timeout=5):
                raise RuntimeError("test timed out before replace release")
            real_reauthenticate(plan)

        def observe_writer_lock(descriptor, operation):
            if threading.current_thread().name == "stale-ledger-writer":
                writer_waiting.set()
            return real_flock(descriptor, operation)

        def run_bootstrap():
            try:
                bootstrap_results.append(
                    bootstrap_historical_import(
                        self.ledger,
                        head_pin_path=self.pin,
                        roots=[root],
                        checkout_root=checkout,
                        **import_args,
                        execute=True,
                        require_committed_pin=False,
                    )
                )
            except Exception as exc:  # pragma: no cover - asserted below
                bootstrap_errors.append(exc)

        def run_writer():
            try:
                writer_results.append(self._reserve("stale-writer", self.root / "x"))
            except Exception as exc:
                writer_errors.append(exc)

        with (
            mock.patch.object(
                calibration_ledger,
                "_reauthenticate_historical_import_plan",
                side_effect=pause_with_bootstrap_lock,
            ),
            mock.patch.object(
                calibration_ledger.fcntl,
                "flock",
                side_effect=observe_writer_lock,
            ),
        ):
            bootstrap_thread = threading.Thread(target=run_bootstrap)
            bootstrap_thread.start()
            self.assertTrue(bootstrap_locked.wait(timeout=5))
            lock_inode_before = lock_path.stat().st_ino
            writer_thread = threading.Thread(
                target=run_writer, name="stale-ledger-writer"
            )
            writer_thread.start()
            self.assertTrue(writer_waiting.wait(timeout=5))
            allow_replace.set()
            bootstrap_thread.join(timeout=5)
            writer_thread.join(timeout=5)
        self.assertFalse(bootstrap_thread.is_alive())
        self.assertFalse(writer_thread.is_alive())
        self.assertEqual(bootstrap_errors, [])
        self.assertEqual(len(bootstrap_results), 1)
        self.assertEqual(writer_results, [])
        self.assertEqual(len(writer_errors), 1)
        self.assertIn("head differs", str(writer_errors[0]))
        self.assertEqual(
            self.ledger.read_bytes(), bootstrap_results[0].ledger_bytes
        )
        self.assertTrue(lock_path.exists())
        self.assertEqual(lock_path.stat().st_ino, lock_inode_before)

    def test_hostile_lock_identity_refuses_and_ordinary_lockfile_proceeds(
        self,
    ) -> None:
        self.ledger.write_bytes(b"")
        lock_path = calibration_ledger._ledger_lock_path(self.ledger)

        lock_path.symlink_to(self.ledger)
        with self.assertRaisesRegex(CalibrationLedgerError, "opened safely"):
            self._reserve("symlink-lock", self.root / "symlink-lock-custody")
        lock_path.unlink()

        os_link = getattr(calibration_ledger.os, "link")
        os_link(self.ledger, lock_path)
        checkout, root, custodies, table = self._historical_fixture()
        import_args = self._historical_import_args(table, custodies)
        with self.assertRaisesRegex(CalibrationLedgerError, "dedicated regular"):
            bootstrap_historical_import(
                self.ledger,
                head_pin_path=self.pin,
                roots=[root],
                checkout_root=checkout,
                **import_args,
                execute=True,
                require_committed_pin=False,
            )
        lock_path.unlink()

        receipt = self._reserve("ordinary-lock", self.root / "ordinary-custody")
        lock_status = lock_path.stat()
        ledger_status = self.ledger.stat()
        self.assertEqual(receipt["event"], "reservation")
        self.assertTrue(stat.S_ISREG(lock_status.st_mode))
        self.assertEqual(lock_status.st_nlink, 1)
        self.assertNotEqual(
            (lock_status.st_dev, lock_status.st_ino),
            (ledger_status.st_dev, ledger_status.st_ino),
        )

    def test_symlink_alias_cannot_acquire_a_second_writer_lease(self) -> None:
        self.ledger.write_bytes(b"")
        alias = self.root / "ledger-alias.jsonl"
        alias.symlink_to(self.ledger)
        self.assertEqual(
            calibration_ledger._ledger_lock_path(self.ledger),
            calibration_ledger._ledger_lock_path(alias),
        )
        holder_code = "\n".join(
            (
                "import time",
                "from pathlib import Path",
                "from joulewise.calibration_ledger import CalibrationWriterLease",
                f"with CalibrationWriterLease(Path({str(self.ledger)!r})):",
                "    print('LEASED', flush=True)",
                "    time.sleep(60)",
            )
        )
        holder = subprocess.Popen(
            [sys.executable, "-c", holder_code],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            assert holder.stdout is not None
            self.assertEqual(holder.stdout.readline().strip(), "LEASED")
            with self.assertRaises(CalibrationLedgerError) as raised:
                calibration_ledger.CalibrationWriterLease(alias).acquire()
            self.assertEqual(
                raised.exception.code, RefusalCode.LIVE_WRITER_CONTENTION
            )
        finally:
            if holder.poll() is None:
                holder.kill()
            holder.communicate(timeout=10)

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
            {"append-intent", "reservation", "finalization"},
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

        manifest = json.loads(import_args["custody_manifest_raw"])
        manifest["members"] = {
            content_id: (
                "/fixture-checkout/"
                f"{Path(locator).relative_to(checkout.resolve())}"
            )
            for content_id, locator in manifest["members"].items()
        }
        manifest_raw = custody_manifest_bytes(manifest)
        import_args["custody_manifest_raw"] = manifest_raw
        import_args["expected_custody_manifest_sha256"] = hashlib.sha256(
            manifest_raw
        ).hexdigest()

        def stable_vector_candidate(locator, *args, **kwargs):
            actual = checkout.resolve() / Path(locator).relative_to(
                "/fixture-checkout"
            )
            content_id, candidate, error = inspect_candidate(
                actual, *args, **kwargs
            )
            if candidate is not None:
                candidate = replace(
                    candidate,
                    custody_locator=str(locator),
                )
            return content_id, candidate, error

        # Normalize the machine-specific absolute custody prefix in both the
        # manifest digest and receipt bytes so this remains a literal
        # cross-checkout wire vector. File authentication, input-digest
        # binding, ordering, receipt construction, and chaining remain live.
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
            "ac4426e4bbc961256116221f1fad7b9580968f072209bda14e875df897ea19e0",
        )

    def _persist_reservation_intent(self, attempt_id: str = "operation-a"):
        custody = self.root / attempt_id
        target = calibration_ledger._new_receipt(
            sequence=1,
            predecessor_digest=GENESIS_DIGEST,
            event="reservation",
            attempt_id=attempt_id,
            content_id=None,
            artifacts={},
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=str(custody),
        )
        target_core = calibration_ledger._target_core(target)
        intent = calibration_ledger._new_append_intent(
            receipts=[],
            byte_offset=0,
            target_core=target_core,
            operation_key=calibration_ledger._operation_key_for_core(target_core),
        )
        self.ledger.write_bytes(canonical_json_bytes(intent) + b"\n")
        physical = calibration_ledger._scan_physical_ledger(
            self.ledger.read_bytes()
        )
        self.assertIsNotNone(physical.active_intent)
        return custody, physical

    def test_closure_regression_same_head_foreign_prefix_never_admitted(self) -> None:
        _custody, physical = self._persist_reservation_intent()
        intent_raw = self.ledger.read_bytes()
        intent = physical.active_intent
        assert intent is not None
        target_a = calibration_ledger._intent_target_receipt(
            intent,
            sequence=len(physical.receipts) + 1,
            predecessor_digest=next(reversed(physical.receipts))["receipt_digest"],
        )
        bytes_a = canonical_json_bytes(target_a) + b"\n"
        target_b = calibration_ledger._new_receipt(
            sequence=target_a["sequence"],
            predecessor_digest=target_a["predecessor_digest"],
            event="reservation",
            attempt_id="operation-b",
            content_id=None,
            artifacts={},
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=str(self.root / "operation-b"),
        )
        bytes_b = canonical_json_bytes(target_b) + b"\n"
        shared = 0
        for left, right in zip(bytes_a, bytes_b):
            if left != right:
                break
            shared += 1
        self.assertGreater(shared, 0)
        variants = {
            "zero": b"",
            "one-shared": bytes_b[:1],
            "several-shared": bytes_b[: min(shared, 17)],
            "len-minus-one": bytes_a[:-1],
            "foreign-fragment": bytes_b[: min(len(bytes_b), shared + 1)],
            "foreign-complete": bytes_b,
        }
        for name, injected in variants.items():
            with self.subTest(name=name):
                self.ledger.write_bytes(intent_raw + injected)
                before = self.ledger.read_bytes()
                with mock.patch.object(
                    calibration_ledger,
                    "_legacy_journal_metadata",
                    side_effect=AssertionError("sidecar must not be read"),
                ):
                    result = calibration_ledger.repair_calibration_ledger(
                        self.ledger
                    )
                after = self.ledger.read_bytes()
                self.assertEqual(result.state, "clean")
                self.assertTrue(after.startswith(before))
                parsed = calibration_ledger._scan_physical_ledger(after)
                business = [
                    row
                    for row in parsed.receipts
                    if row.get("schema_version")
                    != calibration_ledger.CONTROL_SCHEMA
                ]
                self.assertEqual(
                    [row.get("attempt_id") for row in business],
                    ["operation-a"],
                )
                abandonments = [
                    row
                    for row in parsed.receipts
                    if row.get("event") == calibration_ledger.ABANDONMENT_EVENT
                ]
                mismatches = not bytes_a.startswith(injected)
                self.assertEqual(bool(abandonments), mismatches)
                if mismatches:
                    abandonment = abandonments[-1]
                    self.assertEqual(abandonment["residue_length"], len(injected))
                    self.assertEqual(
                        abandonment["residue_sha256"],
                        hashlib.sha256(injected).hexdigest(),
                    )
                    self.assertLess(
                        abandonment["sequence"], business[-1]["sequence"]
                    )

    def test_bare_business_pair_after_protocol_activation_is_named_refusal(
        self,
    ) -> None:
        governed_custody = self._custody("governed-operation")
        self._reserve("governed-operation", governed_custody)
        self._finalize("governed-operation", governed_custody)
        physical = calibration_ledger._scan_physical_ledger(
            self.ledger.read_bytes()
        )
        self._write_pin(
            {
                "sequence": len(physical.receipts),
                "head_digest": next(reversed(physical.receipts))["receipt_digest"],
                "ledger_schema": LEDGER_SCHEMA,
            }
        )

        foreign_custody = self._custody("foreign-bare-operation")
        reservation = calibration_ledger._new_receipt(
            sequence=len(physical.receipts) + 1,
            predecessor_digest=next(reversed(physical.receipts))["receipt_digest"],
            event="reservation",
            attempt_id="foreign-bare-operation",
            content_id=None,
            artifacts={},
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s=None,
            exact_bound_lexeme_s=None,
            disposition="pending",
            custody_locator=str(foreign_custody),
        )
        hashes = artifact_hashes(foreign_custody)
        finalization = calibration_ledger._new_receipt(
            sequence=reservation["sequence"] + 1,
            predecessor_digest=reservation["receipt_digest"],
            event="finalization",
            attempt_id="foreign-bare-operation",
            content_id=content_id_from_artifact_hashes(hashes),
            artifacts=hashes,
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="100.0",
            exact_bound_lexeme_s="0.025",
            disposition="valid",
            custody_locator=str(foreign_custody),
        )
        with self.ledger.open("ab") as handle:
            handle.write(canonical_json_bytes(reservation) + b"\n")
            handle.write(canonical_json_bytes(finalization) + b"\n")

        snapshot = self._snapshot(verify_custody=False)
        self.assertIn(
            "calibration_ledger_ungoverned_business",
            snapshot.refusal_reasons,
        )
        self.assertNotIn(
            "foreign-bare-operation", snapshot.observation_by_attempt
        )

    def test_operator_abandons_junk_and_orphaned_finalization_as_one_residue(
        self,
    ) -> None:
        custody = self._custody("orphaned-finalization")
        reservation = self._reserve("orphaned-finalization", custody)
        physical = calibration_ledger._scan_physical_ledger(
            self.ledger.read_bytes()
        )
        self._write_pin(
            {
                "sequence": len(physical.receipts),
                "head_digest": next(reversed(physical.receipts))["receipt_digest"],
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        hashes = artifact_hashes(custody)
        orphan = calibration_ledger._new_receipt(
            sequence=len(physical.receipts) + 1,
            predecessor_digest=next(reversed(physical.receipts))["receipt_digest"],
            event="finalization",
            attempt_id=reservation["attempt_id"],
            content_id=content_id_from_artifact_hashes(hashes),
            artifacts=hashes,
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="100.0",
            exact_bound_lexeme_s="0.025",
            disposition="valid",
            custody_locator=str(custody),
        )
        residue = b"junk\n" + canonical_json_bytes(orphan) + b"\n"
        with self.ledger.open("ab") as handle:
            handle.write(residue)

        with self.assertRaisesRegex(
            CalibrationLedgerError, "operator-attested abandon-tail"
        ):
            calibration_ledger.repair_calibration_ledger(self.ledger)
        result = calibration_ledger.abandon_calibration_ledger_tail(
            self.ledger,
            operator_identity="night-operator",
            attestation_reason="junk broke the chain before the orphaned receipt",
            head_pin_path=self.pin,
            require_committed_pin=False,
        )
        self.assertEqual(result.state, "clean")
        final = calibration_ledger._scan_physical_ledger(
            self.ledger.read_bytes()
        )
        abandonment = next(reversed(final.receipts))
        self.assertEqual(abandonment["residue_length"], len(residue))
        self.assertEqual(
            abandonment["residue_sha256"], hashlib.sha256(residue).hexdigest()
        )
        self.assertFalse(
            any(
                row.get("event") == "finalization"
                and row.get("attempt_id") == "orphaned-finalization"
                for row in final.receipts
            )
        )

    def test_operator_abandonment_refuses_same_sequence_sibling_of_pin(
        self,
    ) -> None:
        def reservation(attempt_id: str) -> dict:
            return calibration_ledger._new_receipt(
                sequence=1,
                predecessor_digest=GENESIS_DIGEST,
                event="reservation",
                attempt_id=attempt_id,
                content_id=None,
                artifacts={},
                identity_epoch=self.epoch,
                t1_bindings=self.t1,
                capture_wall_time_s=None,
                exact_bound_lexeme_s=None,
                disposition="pending",
                custody_locator=str(self.root / attempt_id),
            )

        pinned = reservation("pinned-head")
        sibling = reservation("same-sequence-sibling")
        self.assertNotEqual(pinned["receipt_digest"], sibling["receipt_digest"])
        self._write_pin(
            {
                "sequence": pinned["sequence"],
                "head_digest": pinned["receipt_digest"],
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        original = canonical_json_bytes(sibling) + b"\nterminal-residue"
        self.ledger.write_bytes(original)
        with self.assertRaisesRegex(
            CalibrationLedgerError, "committed head digest"
        ):
            calibration_ledger.abandon_calibration_ledger_tail(
                self.ledger,
                operator_identity="night-operator",
                attestation_reason="must authenticate the pinned digest",
                head_pin_path=self.pin,
                require_committed_pin=False,
            )
        self.assertEqual(self.ledger.read_bytes(), original)

    def test_terminal_pin_includes_authenticated_trailing_abandonment(self) -> None:
        self._open_bracket_session()
        self._finalize_bracket_slot("session-alpha", "pre")
        self._finalize_bracket_slot("session-alpha", "post")
        self._write_pin(
            terminal_head_pin_for_session(
                self.ledger, session_id="session-alpha"
            )
        )
        with self.ledger.open("ab") as handle:
            handle.write(b"post-terminal-residue")
        result = calibration_ledger.abandon_calibration_ledger_tail(
            self.ledger,
            operator_identity="night-operator",
            attestation_reason="authenticate residue after terminal post",
            head_pin_path=self.pin,
            require_committed_pin=False,
        )
        self.assertEqual(result.state, "clean")
        physical = calibration_ledger._scan_physical_ledger(
            self.ledger.read_bytes()
        )
        abandonment = next(reversed(physical.receipts))
        self.assertEqual(abandonment["event"], calibration_ledger.ABANDONMENT_EVENT)
        pin = terminal_head_pin_for_session(
            self.ledger, session_id="session-alpha"
        )
        self.assertEqual(pin["sequence"], abandonment["sequence"])
        self.assertEqual(pin["head_digest"], abandonment["receipt_digest"])

    def test_intent_commitment_mutation_and_operator_crossing_fail_closed(self) -> None:
        _custody, physical = self._persist_reservation_intent()
        intent = dict(physical.active_intent or {})
        target_core = dict(intent["target_core"])
        target_core["custody_locator"] = str(self.root / "substituted-custody")
        self.assertEqual(
            calibration_ledger._operation_key_for_core(target_core),
            intent["operation_key"],
        )
        intent["target_core"] = target_core
        intent["receipt_digest"] = calibration_ledger._receipt_digest(intent)
        self.ledger.write_bytes(canonical_json_bytes(intent) + b"\n")

        def assert_content_binding_refuses() -> None:
            inspected = calibration_ledger.inspect_calibration_ledger(self.ledger)
            self.assertEqual(inspected.state, "residue")
            self.assertEqual(inspected.head_sequence, 0)

        assert_content_binding_refuses()
        validator_source = inspect.getsource(
            calibration_ledger._valid_control_receipt_shape
        )
        binding_check = (
            '            and canonical_sha256(target_core) '
            '== receipt["target_core_sha256"]\n'
        )
        self.assertEqual(validator_source.count(binding_check), 1)
        mutant_source = validator_source.replace(binding_check, "")
        mutant_namespace = dict(calibration_ledger.__dict__)
        exec(compile(mutant_source, "<content-binding-mutant>", "exec"), mutant_namespace)
        mutant_validator = mutant_namespace["_valid_control_receipt_shape"]
        with mock.patch.object(
            calibration_ledger,
            "_valid_control_receipt_shape",
            mutant_validator,
        ):
            with self.assertRaises(AssertionError):
                assert_content_binding_refuses()
            mutant_inspection = calibration_ledger.inspect_calibration_ledger(
                self.ledger
            )
            self.assertEqual(mutant_inspection.state, "intent")
            self.assertEqual(mutant_inspection.head_sequence, 1)

        self.ledger.write_bytes(
            canonical_json_bytes(physical.active_intent) + b"\n"
        )
        with self.assertRaisesRegex(CalibrationLedgerError, "irrevocable"):
            calibration_ledger.abandon_calibration_ledger_tail(
                self.ledger,
                operator_identity="night-operator",
                attestation_reason="must not cross the durable intent",
                head_pin_path=self.pin,
                require_committed_pin=False,
            )

    def test_sigkill_at_all_six_append_points_converges_without_deletion(
        self,
    ) -> None:
        cases = (
            "during-intent",
            "after-intent-fsync",
            "during-target",
            "after-target-fsync",
            "during-abandonment",
            "after-abandonment-fsync",
        )
        repo_root = Path(__file__).resolve().parents[1]
        for case in cases:
            with self.subTest(case=case):
                self.ledger.unlink(missing_ok=True)
                abandonment_case = "abandonment" in case
                attempt_id = (
                    "abandon-crash" if abandonment_case else "crash-boundary"
                )
                if abandonment_case:
                    self._persist_reservation_intent(attempt_id)
                    with self.ledger.open("ab") as handle:
                        handle.write(b"foreign-tail")
                action = (
                    f"ledger.repair_calibration_ledger(Path({str(self.ledger)!r}))"
                    if abandonment_case
                    else f"""
ledger.append_pending_receipt(
    Path({str(self.ledger)!r}),
    attempt_id={attempt_id!r},
    custody_locator={str(self.root / 'crash')!r},
    identity_epoch={self.epoch!r},
    t1_bindings={self.t1!r},
    head_pin_path=Path({str(self.pin)!r}),
    require_committed_pin=False,
)
"""
                )
                child_code = f"""
import os
from pathlib import Path
import signal
import joulewise.calibration_ledger as ledger

case = {case!r}
write_calls = [0]
real_write = ledger._write_ledger_append_payload

def crash_write(handle, payload):
    write_calls[0] += 1
    crash_call = 1 if case in {{'during-intent', 'during-abandonment'}} else 2
    if case.startswith('during-') and write_calls[0] == crash_call:
        handle.write(payload[:max(1, len(payload) // 3)])
        handle.flush()
        os.fsync(handle.fileno())
        os.kill(os.getpid(), signal.SIGKILL)
    return real_write(handle, payload)

def crash_after(stage):
    expected = {{
        'after-intent-fsync': 'intent',
        'after-target-fsync': 'target',
        'after-abandonment-fsync': 'abandonment',
    }}.get(case)
    if stage == expected:
        os.kill(os.getpid(), signal.SIGKILL)

ledger._write_ledger_append_payload = crash_write
ledger._after_ledger_fsync = crash_after
{action}
raise SystemExit('crash hook was not reached')
"""
                killed = subprocess.run(
                    [sys.executable, "-c", child_code],
                    cwd=repo_root,
                    check=False,
                )
                self.assertEqual(killed.returncode, -signal.SIGKILL)

                before = self.ledger.read_bytes()
                calibration_ledger.repair_calibration_ledger(self.ledger)
                after = self.ledger.read_bytes()
                self.assertTrue(after.startswith(before))
                final = calibration_ledger._scan_physical_ledger(after)
                self.assertFalse(final.reasons)
                self.assertIsNone(final.active_intent)
                business = [
                    row
                    for row in final.receipts
                    if row.get("schema_version")
                    != calibration_ledger.CONTROL_SCHEMA
                ]
                if case == "during-intent":
                    self.assertEqual(business, [])
                    self.assertTrue(
                        any(
                            row.get("event")
                            == calibration_ledger.ABANDONMENT_EVENT
                            for row in final.receipts
                        )
                    )
                else:
                    self.assertEqual([row["attempt_id"] for row in business], [attempt_id])
                    retry_custody = (
                        self.root / attempt_id
                        if abandonment_case
                        else self.root / "crash"
                    )
                    retry = self._reserve(attempt_id, retry_custody)
                    self.assertEqual(retry, business[-1])

    def test_legacy_journal_is_hashed_archived_and_never_replayed(self) -> None:
        legacy = calibration_ledger._legacy_append_journal_path(self.ledger)
        legacy_payload = b'{"payload":"foreign-operation"}\n'
        legacy.write_bytes(legacy_payload)
        result = calibration_ledger.repair_calibration_ledger(self.ledger)
        self.assertEqual(result.state, "clean")
        self.assertFalse(legacy.exists())
        archives = list(self.root.glob("ledger.jsonl.append-journal.archived-*"))
        self.assertEqual(len(archives), 1)
        self.assertEqual(archives[0].read_bytes(), legacy_payload)
        parsed = calibration_ledger._scan_physical_ledger(
            self.ledger.read_bytes()
        )
        abandonment = next(reversed(parsed.receipts))
        self.assertEqual(abandonment["event"], calibration_ledger.ABANDONMENT_EVENT)
        self.assertEqual(
            abandonment["legacy_journal"]["sha256"],
            hashlib.sha256(legacy_payload).hexdigest(),
        )
        self.assertFalse(
            any(row.get("attempt_id") == "foreign-operation" for row in parsed.receipts)
        )

    def test_issued_shape_76_receipt_prefix_authenticates_without_controls(self) -> None:
        receipts: list[dict] = []
        predecessor = GENESIS_DIGEST
        for index in range(38):
            attempt_id = f"issued-prefix-{index:02d}"
            reservation = calibration_ledger._new_receipt(
                sequence=len(receipts) + 1,
                predecessor_digest=predecessor,
                event=HISTORICAL_IMPORT_RESERVATION_EVENT,
                attempt_id=attempt_id,
                content_id=None,
                artifacts={},
                identity_epoch=self.epoch,
                t1_bindings=self.t1,
                capture_wall_time_s=None,
                exact_bound_lexeme_s=None,
                disposition="pending",
                custody_locator=f"/issued/{attempt_id}",
                historical_import_input_sha256={
                    "disposition_table": "d" * 64,
                    "custody_manifest": "c" * 64,
                },
            )
            receipts.append(reservation)
            predecessor = reservation["receipt_digest"]
            artifacts = {
                "instrument_evidence.json": f"{index + 1:064x}",
                "manifest.json": f"{index + 101:064x}",
            }
            final = calibration_ledger._new_receipt(
                sequence=len(receipts) + 1,
                predecessor_digest=predecessor,
                event=HISTORICAL_IMPORT_FINALIZATION_EVENT,
                attempt_id=attempt_id,
                content_id=content_id_from_artifact_hashes(artifacts),
                artifacts=artifacts,
                identity_epoch=self.epoch,
                t1_bindings=self.t1,
                capture_wall_time_s="99.0",
                exact_bound_lexeme_s="0.025",
                disposition="valid",
                custody_locator=f"/issued/{attempt_id}",
            )
            receipts.append(final)
            predecessor = final["receipt_digest"]
        raw = b"".join(canonical_json_bytes(row) + b"\n" for row in receipts)
        parsed, reasons = calibration_ledger._parse_ledger(raw)
        self.assertEqual(reasons, set())
        self.assertEqual(len(parsed), 76)
        self.assertFalse(
            any(row.get("schema_version") == calibration_ledger.CONTROL_SCHEMA for row in parsed)
        )

    def test_recovery_cli_has_no_payload_source_and_governs_operator_tail(self) -> None:
        parser = recovery_cli.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["repair", "--payload", "foreign.json"])
        with self.assertRaises(SystemExit):
            parser.parse_args(["--allow-uncommitted-head-pin", "inspect"])
        self.ledger.write_bytes(b"complete-but-malformed\n")
        with (
            mock.patch("sys.stdout", new_callable=io.StringIO) as output,
            mock.patch.object(
                calibration_ledger,
                "_committed_pin_bytes",
                return_value=self.pin.read_bytes(),
            ),
        ):
            code = recovery_cli.main(
                [
                    "--ledger",
                    str(self.ledger),
                    "--head-pin",
                    str(self.pin),
                    "abandon-tail",
                    "--operator-identity",
                    "night-operator",
                    "--attestation-reason",
                    "inspected malformed terminal bytes at 02:00",
                ]
            )
        self.assertEqual(code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["inspection"]["state"], "clean")
        parsed = calibration_ledger._scan_physical_ledger(
            self.ledger.read_bytes()
        )
        terminal_receipt = next(reversed(parsed.receipts))
        self.assertEqual(terminal_receipt["actor_type"], "operator")
        self.assertEqual(terminal_receipt["residue_start_offset"], 0)


if __name__ == "__main__":
    unittest.main()
