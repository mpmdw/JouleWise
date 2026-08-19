"""Synthetic D-117 three-window live-ledger integration regression."""

from __future__ import annotations

import copy
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import joulewise.calibration_ledger as calibration_ledger_module
from joulewise.calibration_bracketing import (
    CalibrationCandidate,
    _canonical_sha256 as bracketing_canonical_sha256,
    _valid_acceptance_bound,
    build_calibration_bracket_binding,
    calibration_bracket_for_bundles,
    discover_calibration_candidates,
    evaluate_calibration_bracket,
    load_calibration_acceptance_bound,
    validate_calibration_bracket_binding,
)
from joulewise.calibration_ledger import (
    APPEND_INTENT_EVENT,
    APPEND_RECORDS_PER_OPERATION,
    BRACKET_SESSION_FINALIZATION_EVENT,
    BRACKET_SESSION_OPEN_EVENT,
    BRACKET_SESSION_SLOT_CLAIM_EVENT,
    BRACKET_SESSION_SLOTS,
    CONTROL_SCHEMA,
    GOVERNED_ARTIFACTS,
    HISTORICAL_IMPORT_FINALIZATION_EVENT,
    HISTORICAL_IMPORT_RESERVATION_EVENT,
    LEDGER_SCHEMA,
    RECEIPT_SCHEMA,
    abort_bracket_session,
    append_bracket_session_receipt,
    canonical_json_bytes,
    canonical_sha256,
    claim_bracket_session_slot,
    content_id_from_artifact_hashes,
    finalize_bracket_session_slot,
    load_calibration_ledger_snapshot,
    terminal_head_pin_for_session,
)
from joulewise.powermetrics_fiducial import (
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
)
from joulewise.schemas import CalibrationBracketingPolicy
from scripts import validate_powermetrics_fiducial as production_writer
from tests.receipt_corpus import ReceiptCorpus


_FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "calibration_live_three_window"
    / "scenario.json"
)
_USE_WINDOW_BINDING = object()
_USE_WINDOW_RUNS_ROOT = object()
_ISSUANCE_BASE_SEQUENCE = 76
_LIVE_SESSION_COUNT = 3
_OPERATIONS_PER_SESSION = 1 + 2 * len(BRACKET_SESSION_SLOTS)
_PHYSICAL_RECORDS_PER_SESSION = (
    _OPERATIONS_PER_SESSION * APPEND_RECORDS_PER_OPERATION
)
_EXPECTED_TERMINAL_SEQUENCE = (
    _ISSUANCE_BASE_SEQUENCE
    + _LIVE_SESSION_COUNT * _PHYSICAL_RECORDS_PER_SESSION
)


def _hash(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _content_hashes(label: str) -> dict[str, str]:
    return {
        "manifest.json": _hash(f"{label}:manifest"),
        "instrument_evidence.json": _hash(f"{label}:evidence"),
    }


def _receipt(core: dict) -> dict:
    value = copy.deepcopy(core)
    value.pop("receipt_digest", None)
    value["receipt_digest"] = canonical_sha256(value)
    return value


def _ledger_bytes(receipts: ReceiptCorpus) -> bytes:
    return b"".join(canonical_json_bytes(row) + b"\n" for row in receipts)


def _pin_for(receipt: dict) -> dict:
    return {
        "sequence": receipt["sequence"],
        "head_digest": receipt["receipt_digest"],
        "ledger_schema": LEDGER_SCHEMA,
    }


def _pin_bytes(pin: dict) -> bytes:
    return (json.dumps(pin, sort_keys=True) + "\n").encode("utf-8")


def _write_synthetic_custody(custody: Path, label: str) -> None:
    for relative in GOVERNED_ARTIFACTS:
        path = custody / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"{label}:{relative}".encode("utf-8"))


class CalibrationLiveThreeWindowTests(unittest.TestCase):
    """Exercise one issuance-equivalent prefix and its three live sessions."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = json.loads(_FIXTURE.read_text(encoding="utf-8"))
        cls.epoch = dict(cls.scenario["identity_epoch"])
        cls.t1 = dict(cls.scenario["t1_bindings"])

        cls._class_tmp = tempfile.TemporaryDirectory()
        root = Path(cls._class_tmp.name)
        runtime_windows = []
        for source in cls.scenario["windows"]:
            window = copy.deepcopy(source)
            window["runs_root"] = str(root / "night-roots" / window["name"])
            runtime_windows.append(window)
        cls.windows = {
            row["name"]: row for row in runtime_windows
        }
        cls.policy = CalibrationBracketingPolicy(
            require_bracket=True,
            calibration_bracket_max_drift_s=0.010,
        )

        source = load_calibration_acceptance_bound()
        if source is None:
            raise AssertionError("checked-in issued acceptance artifact is unavailable")
        source_path = Path(
            "configs/calibration/calibration_acceptance_d079_v2.json"
        )
        if hashlib.sha256(source_path.read_bytes()).hexdigest() != cls.scenario[
            "source_acceptance_sha256"
        ]:
            raise AssertionError("fixture source acceptance pin drifted")

        base_receipts, acceptance = cls._build_issuance_equivalent_base(source)
        cls.base_receipts = base_receipts
        cls.acceptance = acceptance
        cls.base_sequence = len(base_receipts)
        cls.base_digest = base_receipts.one(sequence=cls.base_sequence)[
            "receipt_digest"
        ]

        ledger = root / "runs" / "ledger.jsonl"
        pin = root / "configs" / "calibration" / "head.json"
        ledger.parent.mkdir(parents=True)
        pin.parent.mkdir(parents=True)
        ledger.write_bytes(_ledger_bytes(base_receipts))
        pin.write_bytes(
            _pin_bytes(_pin_for(base_receipts.one(sequence=cls.base_sequence)))
        )

        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "tests@joulewise.invalid"],
            cwd=root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "JouleWise tests"],
            cwd=root,
            check=True,
        )
        subprocess.run(
            ["git", "add", pin.relative_to(root).as_posix()],
            cwd=root,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-qm", "pin issuance-equivalent head"],
            cwd=root,
            check=True,
        )

        bindings: dict[str, dict] = {}
        closeouts: dict[str, dict] = {}
        for window in runtime_windows:
            attempts = {
                slot: f"d117-{window['name']}-{slot}" for slot in ("pre", "post")
            }
            slots = {
                slot: {
                    "attempt_id": attempts[slot],
                    "custody_locator": (
                        f"{window['runs_root']}/instrument_validation/"
                        f"{attempts[slot]}"
                    ),
                    "identity_epoch": cls.epoch,
                    "t1_bindings": cls.t1,
                }
                for slot in ("pre", "post")
            }
            append_bracket_session_receipt(
                ledger,
                session_id=window["session_id"],
                window_id=window["window_id"],
                plan_id=window["plan_id"],
                plan_sha256=window["plan_sha256"],
                evidence_root_id=window["evidence_root_id"],
                runs_root=window["runs_root"],
                slots=slots,
                head_pin_path=pin,
                require_committed_pin=True,
                repo_root=root,
            )
            for slot in ("pre", "post"):
                lifecycle = production_writer._CaptureLedgerLifecycle(
                    ledger_path=ledger,
                    head_pin_path=pin,
                    attempt_id=attempts[slot],
                    custody_locator=slots[slot]["custody_locator"],
                    identity_epoch=cls.epoch,
                    t1_bindings=cls.t1,
                    session_id=window["session_id"],
                    slot=slot,
                    require_committed_pin=False,
                )
                # The synthetic issuance prefix has hash-only import custody.
                # Keep that fixture boundary while exercising the production
                # writer's reservation validation, exclusive claim, and
                # finalization path for every live endpoint.
                def load_without_import_custody(*args, **kwargs):
                    kwargs["verify_custody"] = False
                    return load_calibration_ledger_snapshot(*args, **kwargs)

                with patch.object(
                    production_writer,
                    "load_calibration_ledger_snapshot",
                    side_effect=load_without_import_custody,
                ), patch.object(
                    calibration_ledger_module,
                    "load_calibration_ledger_snapshot",
                    side_effect=load_without_import_custody,
                ):
                    lifecycle.begin()
                _write_synthetic_custody(
                    Path(slots[slot]["custody_locator"]), attempts[slot]
                )
                lifecycle.capture_wall_time_s = str(
                    window[f"{slot}_capture_s"]
                )
                lifecycle.exact_bound_lexeme_s = window[f"{slot}_bound_s"]
                _receipt_value, terminal_pin = lifecycle.finalize("valid")
                if slot == "pre":
                    if terminal_pin is not None:
                        raise AssertionError("pre finalization emitted a terminal pin")
                elif terminal_pin is None:
                    raise AssertionError("post finalization omitted its terminal pin")
            pin_value = terminal_pin
            pin.write_bytes(_pin_bytes(pin_value))
            subprocess.run(
                ["git", "add", pin.relative_to(root).as_posix()],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-qm", f"pin {window['name']} closeout"],
                cwd=root,
                check=True,
            )
            closeout_snapshot = load_calibration_ledger_snapshot(
                ledger,
                pin,
                baseline_sequence=cls.base_sequence,
                baseline_digest=cls.base_digest,
                require_committed_pin=True,
                verify_custody=False,
                repo_root=root,
            )
            bindings[window["name"]] = build_calibration_bracket_binding(
                closeout_snapshot,
                session_id=window["session_id"],
                window_id=window["window_id"],
                plan_id=window["plan_id"],
                plan_sha256=window["plan_sha256"],
                evidence_root_id=window["evidence_root_id"],
                runs_root=window["runs_root"],
            )
            closeouts[window["name"]] = {
                "snapshot": closeout_snapshot,
                "ledger_bytes": ledger.read_bytes(),
                "pin_bytes": pin.read_bytes(),
                "pin_commit": subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip(),
            }

        cls.bindings = bindings
        cls.closeouts = closeouts
        cls.final_ledger_bytes = ledger.read_bytes()
        cls.final_pin_bytes = pin.read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._class_tmp.cleanup()

    @classmethod
    def _build_issuance_equivalent_base(
        cls, source: dict
    ) -> tuple[ReceiptCorpus, dict]:
        artifact = copy.deepcopy(source)
        artifact["identity_epoch"] = dict(cls.epoch)
        artifact["prior_observation_set"]["epoch_catalog"] = {
            "d079_epoch": dict(cls.epoch)
        }

        observations: list[dict] = []
        receipt_members: list[dict] = []
        for member in artifact["derivation_corpus"]["members"]:
            hashes = {
                "manifest.json": member["manifest_sha256"],
                "instrument_evidence.json": member[
                    "instrument_evidence_sha256"
                ],
            }
            content_id = content_id_from_artifact_hashes(hashes)
            if content_id is None:
                raise AssertionError("derivation member lacks a content identity")
            receipt_members.append(
                {
                    "attempt_id": member["member_id"],
                    "content_id": content_id,
                    "artifact_sha256": hashes,
                    "disposition": "valid",
                    "bound_s": member["b_fiducial_s"],
                }
            )

        additions = cls.scenario["issuance_equivalent_base"][
            "synthetic_additions_to_derivation_corpus"
        ]
        for disposition, count in additions.items():
            for index in range(count):
                attempt_id = f"synthetic-import-{disposition}-{index:02d}"
                hashes = _content_hashes(attempt_id)
                content_id = content_id_from_artifact_hashes(hashes)
                if content_id is None:
                    raise AssertionError("synthetic import lacks a content identity")
                receipt_members.append(
                    {
                        "attempt_id": attempt_id,
                        "content_id": content_id,
                        "artifact_sha256": hashes,
                        "disposition": disposition,
                        "bound_s": (
                            "0.040000"
                            if disposition == "systematic-invalid"
                            else "0.026000"
                        ),
                    }
                )

        receipts: list[dict] = []
        predecessor = "0" * 64
        import_inputs = {
            "disposition_table": _hash("synthetic-d117-disposition-table"),
            "custody_manifest": _hash("synthetic-d117-custody-manifest"),
        }
        for index, member in enumerate(
            sorted(receipt_members, key=lambda row: row["attempt_id"]), start=1
        ):
            custody = f"/synthetic/d117/import/{member['attempt_id']}"
            reservation = _receipt(
                {
                    "schema_version": RECEIPT_SCHEMA,
                    "ledger_schema": LEDGER_SCHEMA,
                    "sequence": len(receipts) + 1,
                    "predecessor_digest": predecessor,
                    "event": HISTORICAL_IMPORT_RESERVATION_EVENT,
                    "attempt_id": member["attempt_id"],
                    "content_id": None,
                    "artifact_sha256": {},
                    "identity_epoch": dict(cls.epoch),
                    "t1_bindings": dict(cls.t1),
                    "capture_wall_time_s": None,
                    "exact_bound_lexeme_s": None,
                    "disposition": "pending",
                    "custody_locator": custody,
                    "historical_import_input_sha256": import_inputs,
                }
            )
            receipts.append(reservation)
            predecessor = reservation["receipt_digest"]
            finalization = _receipt(
                {
                    "schema_version": RECEIPT_SCHEMA,
                    "ledger_schema": LEDGER_SCHEMA,
                    "sequence": len(receipts) + 1,
                    "predecessor_digest": predecessor,
                    "event": HISTORICAL_IMPORT_FINALIZATION_EVENT,
                    "attempt_id": member["attempt_id"],
                    "content_id": member["content_id"],
                    "artifact_sha256": member["artifact_sha256"],
                    "identity_epoch": dict(cls.epoch),
                    "t1_bindings": dict(cls.t1),
                    "capture_wall_time_s": str(float(index)),
                    "exact_bound_lexeme_s": member["bound_s"],
                    "disposition": member["disposition"],
                    "custody_locator": custody,
                }
            )
            receipts.append(finalization)
            predecessor = finalization["receipt_digest"]
            observations.append(
                {
                    "content_id": member["content_id"],
                    "epoch_id": "d079_epoch",
                    "disposition": member["disposition"],
                    "attempt_id": member["attempt_id"],
                }
            )

        cutoff = {
            "sequence": len(receipts),
            "head_digest": next(reversed(receipts))["receipt_digest"],
            "ledger_schema": LEDGER_SCHEMA,
        }
        artifact["ledger_cutoff"] = {
            **cutoff,
            "role": "issued_acceptance_baseline",
        }
        artifact["prior_observation_set"]["cutoff"] = cutoff
        artifact["prior_observation_set"]["observations"] = observations
        counts = {
            disposition: sum(
                row["disposition"] == disposition for row in observations
            )
            for disposition in ("ordinary-invalid", "systematic-invalid", "valid")
        }
        artifact["backfill_candidate"]["candidate_inventory"] = counts
        artifact["derivation_sha256"] = bracketing_canonical_sha256(
            {
                key: value
                for key, value in artifact.items()
                if key != "derivation_sha256"
            }
        )
        if not _valid_acceptance_bound(artifact):
            raise AssertionError("synthetic issued acceptance artifact is invalid")
        return ReceiptCorpus(receipts), artifact

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "ledger.jsonl"
        self.pin = self.root / "head.json"
        self.ledger.write_bytes(self.final_ledger_bytes)
        self.pin.write_bytes(self.final_pin_bytes)
        self.receipts = ReceiptCorpus(
            json.loads(line) for line in self.final_ledger_bytes.splitlines()
        )
        self.snapshot = self._load_snapshot()
        self.candidates = self._discover(self.snapshot)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _load_snapshot(
        self,
        *,
        ledger: Path | None = None,
        pin: Path | None = None,
        require_committed_pin: bool = False,
        repo_root: Path | None = None,
    ):
        return load_calibration_ledger_snapshot(
            ledger or self.ledger,
            pin or self.pin,
            baseline_sequence=self.base_sequence,
            baseline_digest=self.base_digest,
            require_committed_pin=require_committed_pin,
            verify_custody=False,
            repo_root=repo_root or self.root,
        )

    @staticmethod
    def _candidate(observation) -> CalibrationCandidate:
        return CalibrationCandidate(
            relative_path=observation.custody_locator,
            manifest_sha256=observation.artifact_sha256["manifest.json"],
            evidence_sha256=observation.artifact_sha256[
                "instrument_evidence.json"
            ],
            protocol_id=observation.t1_bindings["pulse_protocol_id"],
            capture_wall_time_s=float(observation.capture_wall_time_s),
            b_fiducial_s=observation.exact_bound_lexeme_s,
            bindings=dict(observation.t1_bindings),
            attempt_id=observation.attempt_id,
            content_id=observation.content_id,
            ledger_receipt_digest=observation.receipt_digest,
            bracket_session_id=observation.bracket_session_id,
            bracket_slot=observation.bracket_slot,
            bracket_window_id=observation.bracket_window_id,
            bracket_plan_id=observation.bracket_plan_id,
            bracket_plan_sha256=observation.bracket_plan_sha256,
            bracket_evidence_root_id=observation.bracket_evidence_root_id,
            bracket_runs_root=observation.bracket_runs_root,
        )

    def _discover(self, snapshot):
        with patch(
            "joulewise.calibration_bracketing._candidate_from_observation",
            side_effect=self._candidate,
        ):
            return discover_calibration_candidates(snapshot)

    def _evaluate(
        self,
        window_name: str,
        *,
        snapshot=None,
        candidates=None,
        binding=_USE_WINDOW_BINDING,
        bindings=None,
        bracket_runs_root=_USE_WINDOW_RUNS_ROOT,
    ):
        window = self.windows[window_name]
        selected_binding = (
            self.bindings[window_name]
            if binding is _USE_WINDOW_BINDING
            else binding
        )
        selected_runs_root = (
            window["runs_root"]
            if bracket_runs_root is _USE_WINDOW_RUNS_ROOT
            else bracket_runs_root
        )
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=self.acceptance,
        ):
            return evaluate_calibration_bracket(
                self.candidates if candidates is None else candidates,
                window_start_s=window["window_start_s"],
                window_end_s=window["window_end_s"],
                bindings=self.t1 if bindings is None else bindings,
                policy=self.policy,
                ledger_snapshot=self.snapshot if snapshot is None else snapshot,
                bracket_binding=selected_binding,
                bracket_window_id=window["window_id"],
                bracket_plan_id=window["plan_id"],
                bracket_plan_sha256=window["plan_sha256"],
                bracket_evidence_root_id=window["evidence_root_id"],
                bracket_runs_root=selected_runs_root,
            )

    def _variant_snapshot(self, receipts: ReceiptCorpus, pin: dict | None = None):
        self.ledger.write_bytes(_ledger_bytes(receipts))
        if pin is None:
            pin = _pin_for(receipts.one(sequence=len(receipts)))
        self.pin.write_bytes(_pin_bytes(pin))
        return self._load_snapshot()

    @classmethod
    def _rechain(cls, receipts: ReceiptCorpus) -> ReceiptCorpus:
        sources = copy.deepcopy(receipts)
        result: list[dict] = []
        predecessor = "0" * 64
        byte_offset = 0
        lineage_anchor = sources.one(sequence=1) if len(sources) else None
        ledger_id = canonical_sha256(
            {
                "ledger_schema": LEDGER_SCHEMA,
                "lineage_anchor_sequence": 1 if sources else 0,
                "lineage_anchor_digest": (
                    lineage_anchor["receipt_digest"]
                    if lineage_anchor is not None
                    else "0" * 64
                ),
            }
        )
        pending_intent: dict | None = None

        def append_rechained(source: dict, target: dict | None = None) -> None:
            nonlocal predecessor, byte_offset
            sequence = len(result) + 1
            row = copy.deepcopy(source)
            row["sequence"] = sequence
            row["predecessor_digest"] = predecessor
            if (
                row.get("schema_version") == CONTROL_SCHEMA
                and row.get("event") == APPEND_INTENT_EVENT
            ):
                if target is None or target.get("schema_version") == CONTROL_SCHEMA:
                    raise AssertionError("fixture intent lacks its semantic target")
                target_core = cls._target_core(target)
                operation_key = cls._operation_key(target_core)
                base_head = {
                    "sequence": sequence - 1,
                    "digest": predecessor,
                    "byte_offset": byte_offset,
                }
                target_core_sha256 = canonical_sha256(target_core)
                row.update(
                    {
                        "ledger_id": ledger_id,
                        "base_head": base_head,
                        "operation_key": operation_key,
                        "target_schema_version": target_core["schema_version"],
                        "target_event": target_core["event"],
                        "target_core": target_core,
                        "target_core_sha256": target_core_sha256,
                        "operation_id": canonical_sha256(
                            {
                                "ledger_id": ledger_id,
                                "base_head": base_head,
                                "operation_key": operation_key,
                                "target_core_sha256": target_core_sha256,
                            }
                        ),
                    }
                )
            row = _receipt(row)
            result.append(row)
            predecessor = row["receipt_digest"]
            byte_offset += len(canonical_json_bytes(row)) + 1

        for source in sources:
            if pending_intent is not None:
                append_rechained(pending_intent, source)
                append_rechained(source)
                pending_intent = None
            elif (
                source.get("schema_version") == CONTROL_SCHEMA
                and source.get("event") == APPEND_INTENT_EVENT
            ):
                pending_intent = copy.deepcopy(source)
            else:
                append_rechained(source)
        if pending_intent is not None:
            raise AssertionError("fixture intent lacks its semantic target")
        return ReceiptCorpus(result)

    @staticmethod
    def _rehash_binding(binding: dict) -> dict:
        value = copy.deepcopy(binding)
        value["binding_digest"] = bracketing_canonical_sha256(
            {
                key: item
                for key, item in value.items()
                if key != "binding_digest"
            }
        )
        return value

    def _receipt_selector(
        self, session_id: str, event: str, slot: str | None = None
    ):
        return lambda row: (
            row.get("session_id") == session_id
            and row.get("event") == event
            and (slot is None or row.get("slot") == slot)
        )

    def _intent_selector(
        self, session_id: str, event: str, slot: str | None = None
    ):
        return lambda row: (
            row.get("schema_version") == CONTROL_SCHEMA
            and row.get("event") == APPEND_INTENT_EVENT
            and row.get("target_core", {}).get("session_id") == session_id
            and row.get("target_core", {}).get("event") == event
            and (
                slot is None
                or row.get("target_core", {}).get("slot") == slot
            )
        )

    def _operation_selector(
        self, session_id: str, event: str, slot: str | None = None
    ):
        receipt = self._receipt_selector(session_id, event, slot)
        intent = self._intent_selector(session_id, event, slot)
        return lambda row: receipt(row) or intent(row)

    @staticmethod
    def _changed(row: dict, change) -> dict:
        value = copy.deepcopy(row)
        change(value)
        return value

    @staticmethod
    def _target_core(row: dict) -> dict:
        return {
            key: copy.deepcopy(value)
            for key, value in row.items()
            if key not in {"sequence", "predecessor_digest", "receipt_digest"}
        }

    @staticmethod
    def _operation_key(target_core: dict) -> dict:
        return {
            "event": target_core["event"],
            "session_id": target_core.get("session_id"),
            "slot": target_core.get("slot"),
            "attempt_id": target_core.get("attempt_id"),
        }

    def test_issuance_equivalent_base_has_76_receipts_and_26_2_10_dispositions(
        self,
    ) -> None:
        expected = self.scenario["issuance_equivalent_base"]
        prefix = ReceiptCorpus(self.snapshot.receipts).filter(
            lambda row: row["sequence"] <= self.base_sequence
        )
        imported = [
            row
            for row in self.snapshot.observations
            if row.sequence <= self.base_sequence
        ]
        counts = {
            disposition: sum(row.disposition == disposition for row in imported)
            for disposition in ("valid", "systematic-invalid", "ordinary-invalid")
        }
        self.assertEqual(self.base_sequence, _ISSUANCE_BASE_SEQUENCE)
        self.assertEqual(len(prefix), expected["receipt_count"])
        self.assertEqual(len(imported), expected["observation_count"])
        self.assertEqual(counts, expected["disposition_counts"])
        self.assertTrue(all(row.is_historical_import for row in imported))

    def test_exactly_six_live_candidates_and_zero_imported_candidates(self) -> None:
        with patch(
            "joulewise.calibration_bracketing._candidate_from_observation",
            side_effect=self._candidate,
        ) as authenticate:
            candidates = discover_calibration_candidates(self.snapshot)
        authenticated_attempts = {
            call.args[0].attempt_id for call in authenticate.call_args_list
        }
        imported_attempts = {
            row.attempt_id
            for row in self.snapshot.observations
            if row.is_historical_import
        }
        expected = self.scenario["expected_live_extension"]
        self.assertEqual(len(candidates), expected["candidate_count"])
        self.assertEqual(authenticated_attempts & imported_attempts, set())
        self.assertTrue(all(candidate.bracket_session_id for candidate in candidates))

    def test_bundle_path_uses_ledger_discovery_as_candidate_authority(self) -> None:
        window = self.windows["gamma"]
        reader = SimpleNamespace(
            measured_window=lambda: SimpleNamespace(
                start_s=window["window_start_s"],
                end_s=window["window_end_s"],
            ),
            metadata=lambda: {
                "instrument_calibration": {"bindings": dict(self.t1)}
            },
        )
        with (
            patch(
                "joulewise.calibration_bracketing.BundleReader",
                return_value=reader,
            ),
            patch(
                "joulewise.calibration_bracketing._candidate_from_observation",
                side_effect=self._candidate,
            ),
            patch(
                "joulewise.calibration_bracketing.discover_calibration_candidates",
                wraps=discover_calibration_candidates,
            ) as discover,
            patch(
                "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
                return_value=self.acceptance,
            ),
        ):
            result, reasons = calibration_bracket_for_bundles(
                Path(window["runs_root"]),
                [Path(window["runs_root"]) / "science-member"],
                self.policy,
                ledger_snapshot=self.snapshot,
                bracket_binding=self.bindings["gamma"],
                bracket_window_id=window["window_id"],
                bracket_plan_id=window["plan_id"],
                bracket_plan_sha256=window["plan_sha256"],
                bracket_evidence_root_id=window["evidence_root_id"],
            )
        discover.assert_called_once_with(self.snapshot)
        self.assertEqual(reasons, ())
        self.assertEqual(result["status"], "passed")
        self.assertEqual(
            [result[slot]["attempt_id"] for slot in ("pre", "post")],
            ["d117-gamma-pre", "d117-gamma-post"],
        )

    def test_alpha_beta_gamma_each_bind_only_their_own_pre_post_pair(self) -> None:
        for name, window in self.windows.items():
            with self.subTest(window=name):
                resolved = validate_calibration_bracket_binding(
                    self.bindings[name],
                    self.snapshot,
                    window_id=window["window_id"],
                    plan_id=window["plan_id"],
                    plan_sha256=window["plan_sha256"],
                    evidence_root_id=window["evidence_root_id"],
                    runs_root=window["runs_root"],
                )
                self.assertIsNotNone(resolved)
                result, reasons = self._evaluate(name)
                self.assertEqual(reasons, ())
                self.assertEqual(result["status"], "passed")
                self.assertEqual(
                    [result[slot]["attempt_id"] for slot in ("pre", "post")],
                    [f"d117-{name}-pre", f"d117-{name}-post"],
                )

    def test_all_six_are_same_epoch_causal_fresh_protocol_and_t1_eligible(
        self,
    ) -> None:
        observations = {
            row.attempt_id: row
            for row in self.snapshot.observations
            if not row.is_historical_import
        }
        self.assertEqual(len(observations), 6)
        for name, window in self.windows.items():
            pre = observations[f"d117-{name}-pre"]
            post = observations[f"d117-{name}-post"]
            with self.subTest(window=name):
                self.assertEqual(dict(pre.identity_epoch), self.epoch)
                self.assertEqual(dict(post.identity_epoch), self.epoch)
                self.assertEqual(dict(pre.t1_bindings), self.t1)
                self.assertEqual(dict(post.t1_bindings), self.t1)
                self.assertEqual(pre.t1_bindings["pulse_protocol_id"], PROTOCOL_ID)
                self.assertEqual(post.t1_bindings["pulse_protocol_id"], PROTOCOL_ID)
                self.assertLessEqual(float(pre.capture_wall_time_s), window["window_start_s"])
                self.assertGreaterEqual(float(post.capture_wall_time_s), window["window_end_s"])
                self.assertLessEqual(
                    window["window_end_s"] - float(pre.capture_wall_time_s),
                    MAX_AGE_S,
                )
                self.assertLessEqual(
                    float(post.capture_wall_time_s) - window["window_start_s"],
                    MAX_AGE_S,
                )

    def test_no_neighboring_endpoint_can_substitute_for_a_bound_endpoint(self) -> None:
        names = list(self.windows)
        for index, name in enumerate(names):
            neighbor = names[(index + 1) % len(names)]
            tampered = copy.deepcopy(self.bindings[name])
            tampered["endpoints"]["post"] = copy.deepcopy(
                self.bindings[neighbor]["endpoints"]["post"]
            )
            tampered = self._rehash_binding(tampered)
            with self.subTest(window=name, neighbor=neighbor):
                _result, reasons = self._evaluate(name, binding=tampered)
                self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))

    def test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding(
        self,
    ) -> None:
        beta = self.windows["beta"]
        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
        foreign_pre = by_attempt["d117-alpha-pre"]
        foreign_post = by_attempt["d117-gamma-post"]
        self.assertNotEqual(foreign_pre.bracket_runs_root, beta["runs_root"])
        self.assertNotEqual(foreign_post.bracket_runs_root, beta["runs_root"])
        self.assertLessEqual(foreign_pre.capture_wall_time_s, beta["window_start_s"])
        self.assertGreaterEqual(foreign_post.capture_wall_time_s, beta["window_end_s"])

        _result, reasons = self._evaluate("beta", binding=None)
        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))

        _result, reasons = self._evaluate(
            "beta",
            binding=self.bindings["beta"],
            bracket_runs_root=foreign_pre.bracket_runs_root,
        )
        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))

        result, reasons = self._evaluate("beta", binding=self.bindings["beta"])
        self.assertEqual(reasons, ())
        self.assertEqual(
            [result[slot]["attempt_id"] for slot in ("pre", "post")],
            ["d117-beta-pre", "d117-beta-post"],
        )
        self.assertNotIn(
            foreign_pre.attempt_id,
            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
        )
        self.assertNotIn(
            foreign_post.attempt_id,
            {result["pre"]["attempt_id"], result["post"]["attempt_id"]},
        )

    def test_each_night_issues_its_verdict_at_a_committed_closeout(self) -> None:
        expected = self.scenario["expected_live_extension"]
        pin_commits = []
        pin_digests = []
        for index, vector in enumerate(expected["cross_window_openness"], start=1):
            name = vector["closeout"]
            snapshot = self.closeouts[name]["snapshot"]
            pin_value = json.loads(self.closeouts[name]["pin_bytes"])
            candidates = self._discover(snapshot)
            candidate_window_ids = {
                candidate.bracket_window_id for candidate in candidates
            }
            expected_window_ids = {
                self.windows[window_name]["window_id"]
                for window_name in vector["candidate_windows"]
            }
            with self.subTest(closeout=name):
                self.assertEqual(snapshot.refusal_reasons, ())
                self.assertEqual(len(snapshot.bracket_sessions), index)
                self.assertEqual(
                    len(
                        [
                            observation
                            for observation in snapshot.observations
                            if not observation.is_historical_import
                        ]
                    ),
                    index * 2,
                )
                self.assertEqual(
                    snapshot.head_sequence,
                    self.base_sequence + index * _PHYSICAL_RECORDS_PER_SESSION,
                )
                self.assertEqual(pin_value["sequence"], snapshot.head_sequence)
                self.assertEqual(pin_value["head_digest"], snapshot.head_digest)
                self.assertEqual(candidate_window_ids, expected_window_ids)
                result, reasons = self._evaluate(
                    name,
                    snapshot=snapshot,
                    candidates=candidates,
                    binding=self.bindings[name],
                )
                self.assertEqual(reasons, ())
                self.assertEqual(result["status"], "passed")
                self.assertEqual(
                    result["acceptance"]["ledger_snapshot"]["sequence"],
                    snapshot.head_sequence,
                )
            pin_commits.append(self.closeouts[name]["pin_commit"])
            pin_digests.append(pin_value["head_digest"])
        self.assertEqual(len(set(pin_commits)), _LIVE_SESSION_COUNT)
        self.assertEqual(len(set(pin_digests)), _LIVE_SESSION_COUNT)

    def test_final_closeout_replays_all_verdicts_with_complete_universe(self) -> None:
        snapshots = []
        for name in self.windows:
            result, reasons = self._evaluate(name, candidates=self.candidates)
            self.assertEqual(reasons, ())
            snapshots.append(result["acceptance"]["ledger_snapshot"])
        self.assertEqual(snapshots, [snapshots[0]] * 3)
        self.assertEqual(snapshots[0]["sequence"], _EXPECTED_TERMINAL_SEQUENCE)
        for name in self.windows:
            _result, reasons = self._evaluate(
                name, candidates=self.candidates[:-1]
            )
            self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))

    def test_production_writer_receipts_end_at_derived_terminal_sequence(self) -> None:
        live = ReceiptCorpus(self.snapshot.receipts).filter(
            lambda row: row["sequence"] > self.base_sequence
        )
        expected = self.scenario["expected_live_extension"]
        receipt_model = expected["receipt_model_supersession"]["landed"]
        self.assertEqual(self.snapshot.head_sequence, _EXPECTED_TERMINAL_SEQUENCE)
        self.assertEqual(
            len(live),
            expected["session_count"] * _PHYSICAL_RECORDS_PER_SESSION,
        )
        # The fixture predates the intent protocol and names its semantic
        # operation count ``receipts_per_session``. Keep that historical
        # oracle distinct from the physical append cadence.
        self.assertEqual(
            receipt_model["receipts_per_session"],
            _OPERATIONS_PER_SESSION,
        )
        self.assertEqual(len(receipt_model["events"]), _OPERATIONS_PER_SESSION)
        self.assertEqual(_OPERATIONS_PER_SESSION, 5)
        self.assertEqual(APPEND_RECORDS_PER_OPERATION, 2)
        self.assertEqual(_PHYSICAL_RECORDS_PER_SESSION, 10)
        for window in self.windows.values():
            rows = ReceiptCorpus(
                row
                for row in live
                if row.get("session_id") == window["session_id"]
                or row.get("schema_version") == CONTROL_SCHEMA
                and row.get("event") == APPEND_INTENT_EVENT
                and row.get("target_core", {}).get("session_id")
                == window["session_id"]
            )
            business_rows = ReceiptCorpus(
                row for row in rows if row.get("schema_version") != CONTROL_SCHEMA
            )
            intent_rows = ReceiptCorpus(
                row
                for row in rows
                if row.get("schema_version") == CONTROL_SCHEMA
                and row.get("event") == APPEND_INTENT_EVENT
            )
            self.assertEqual(len(rows), _PHYSICAL_RECORDS_PER_SESSION)
            self.assertEqual(
                len(intent_rows),
                len(business_rows) * (APPEND_RECORDS_PER_OPERATION - 1),
            )
            self.assertEqual(
                [row["event"] for row in business_rows],
                [
                    BRACKET_SESSION_OPEN_EVENT,
                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
                    BRACKET_SESSION_FINALIZATION_EVENT,
                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
                    BRACKET_SESSION_FINALIZATION_EVENT,
                ],
            )
            self.assertEqual(
                {row["session_id"] for row in business_rows},
                {window["session_id"]},
            )
            self.assertEqual(
                [
                    row["slot"]
                    for row in business_rows
                    if row.get("event") != BRACKET_SESSION_OPEN_EVENT
                ],
                ["pre", "pre", "post", "post"],
            )
            self.assertEqual(
                [row["target_event"] for row in intent_rows],
                [row["event"] for row in business_rows],
            )
        live_observations = [
            observation
            for observation in self.snapshot.observations
            if not observation.is_historical_import
        ]
        self.assertEqual(
            len(self.snapshot.bracket_sessions), expected["session_count"]
        )
        self.assertEqual(
            {session.state for session in self.snapshot.bracket_sessions},
            {"finalized"},
        )
        self.assertEqual(
            len(live_observations), expected["live_observation_count"]
        )
        self.assertTrue(
            all(
                observation.observation_kind == "bracket-session-finalized"
                and observation.disposition == "valid"
                for observation in live_observations
            )
        )

    def test_d110_allowance_selects_both_max_operands_across_windows(self) -> None:
        expected = self.scenario["expected_live_extension"]
        by_attempt = {candidate.attempt_id: candidate for candidate in self.candidates}
        for vector in expected["allowance_branch_vectors"]:
            name = vector["window"]
            overridden = dict(by_attempt)
            for slot in ("pre", "post"):
                attempt_id = f"d117-{name}-{slot}"
                overridden[attempt_id] = replace(
                    overridden[attempt_id],
                    b_fiducial_s=vector[f"{slot}_bound_s"],
                )
            candidates = tuple(
                overridden[candidate.attempt_id] for candidate in self.candidates
            )
            with self.subTest(window=name, branch=vector["branch"]):
                observed = Decimal(vector["observed_drift_s"])
                screen = Decimal(expected["never_zero_allowance_s"])
                if vector["branch"] == "bracket_screen_s":
                    self.assertLess(observed, screen)
                else:
                    self.assertEqual(vector["branch"], "observed_drift_s")
                    self.assertGreater(observed, screen)
                result, reasons = self._evaluate(name, candidates=candidates)
                self.assertEqual(reasons, ())
                allowance = result["acceptance"]["allowance"]
                self.assertEqual(allowance["rule"], expected["allowance_rule"])
                self.assertEqual(
                    result["acceptance"]["drift"]["observed_s"],
                    vector["observed_drift_s"],
                )
                self.assertEqual(
                    allowance["value_s"], vector["selected_allowance_s"]
                )
                self.assertEqual(allowance["embedding_count"], 1)

    def test_no_failure_campaign_has_32_valid_observations_two_short_of_trigger(
        self,
    ) -> None:
        expected = self.scenario["expected_live_extension"][
            "valid_observation_count"
        ]
        issuance_valid = {
            observation.content_id
            for observation in self.snapshot.observations
            if observation.is_historical_import
            and observation.disposition == "valid"
            and dict(observation.identity_epoch) == self.epoch
        }
        valid_same_epoch = {
            observation.content_id
            for observation in self.snapshot.observations
            if observation.disposition == "valid"
            and dict(observation.identity_epoch) == self.epoch
        }
        self.assertEqual(len(issuance_valid), expected["issuance"])
        self.assertEqual(
            len(valid_same_epoch), expected["after_three_live_windows"]
        )
        self.assertEqual(
            expected["corpus_doubling_trigger"] - len(valid_same_epoch),
            expected["shortfall"],
        )
        for name in self.windows:
            result, reasons = self._evaluate(name)
            self.assertEqual(reasons, ())
            self.assertNotIn(
                "corpus_doubles_from_17_to_34",
                result["acceptance"]["prospective_rederivation"][
                    "observed_triggers"
                ],
            )

    def test_refuses_import_marker_removal_import_leakage_or_discovery_regression(
        self,
    ) -> None:
        marker_removed = self.receipts.replace(
            lambda row: row.get("sequence") == 2,
            lambda row: _receipt(
                self._changed(
                    row,
                    lambda value: value.__setitem__("event", "finalization"),
                )
            ),
        )
        snapshot = self._variant_snapshot(marker_removed)
        self.assertIn("calibration_ledger_attempt_conflict", snapshot.refusal_reasons)

        first_import = next(
            row
            for row in self.snapshot.observations
            if row.is_historical_import and row.disposition == "valid"
        )
        leaked = replace(first_import, observation_kind="live-capture")
        leaked_snapshot = replace(
            self.snapshot,
            observations=tuple(
                leaked if row.attempt_id == leaked.attempt_id else row
                for row in self.snapshot.observations
            ),
        )
        leaked_candidates = self._discover(leaked_snapshot)
        _result, reasons = self._evaluate(
            "alpha", snapshot=leaked_snapshot, candidates=leaked_candidates
        )
        self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))

        imported_candidate = self._candidate(first_import)
        _result, reasons = self._evaluate(
            "alpha", candidates=(*self.candidates, imported_candidate)
        )
        self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))

    def test_refuses_missing_duplicate_reordered_or_conflicting_session_receipts(
        self,
    ) -> None:
        alpha_session = self.windows["alpha"]["session_id"]
        post_claim = self._operation_selector(
            alpha_session, BRACKET_SESSION_SLOT_CLAIM_EVENT, "post"
        )
        post_final = self._operation_selector(
            alpha_session, BRACKET_SESSION_FINALIZATION_EVENT, "post"
        )
        session_open = self._receipt_selector(
            alpha_session, BRACKET_SESSION_OPEN_EVENT
        )
        variants: dict[str, ReceiptCorpus] = {}
        variants["missing"] = self._rechain(self.receipts.without(post_final))
        duplicated_operation = copy.deepcopy(self.receipts.filter(post_final))
        variants["duplicate"] = self._rechain(
            self.receipts.insert_after(
                self._receipt_selector(
                    alpha_session,
                    BRACKET_SESSION_FINALIZATION_EVENT,
                    "post",
                ),
                duplicated_operation,
            )
        )
        reordered_rows = ReceiptCorpus(
            (
                *copy.deepcopy(self.receipts.filter(post_final)),
                *copy.deepcopy(self.receipts.filter(post_claim)),
            )
        )
        reordered = self.receipts.replace_group(
            lambda row: post_claim(row) or post_final(row),
            reordered_rows,
        )
        variants["reordered"] = self._rechain(reordered)
        conflicting = self.receipts.replace(
            session_open,
            lambda row: self._changed(
                row,
                lambda value: value.__setitem__(
                    "window_id", "conflicting-alpha-window"
                ),
            ),
        )
        variants["conflicting"] = self._rechain(conflicting)

        for name, receipts in variants.items():
            with self.subTest(vector=name):
                snapshot = self._variant_snapshot(receipts)
                self.assertTrue(
                    {
                        "calibration_ledger_chain_conflict",
                        "calibration_ledger_bracket_session_conflict",
                        "calibration_ledger_bracket_session_open",
                        "calibration_ledger_operation_conflict",
                    }
                    & set(snapshot.refusal_reasons)
                )

    def test_refuses_open_or_abandoned_session_without_governed_closure(self) -> None:
        gamma_session = self.windows["gamma"]["session_id"]
        post_final = self._operation_selector(
            gamma_session, BRACKET_SESSION_FINALIZATION_EVENT, "post"
        )
        open_snapshot = self._variant_snapshot(
            copy.deepcopy(
                self.receipts.before(
                    self._intent_selector(
                        gamma_session,
                        BRACKET_SESSION_FINALIZATION_EVENT,
                        "post",
                    )
                )
            )
        )
        self.assertIn(
            "calibration_ledger_bracket_session_open",
            open_snapshot.refusal_reasons,
        )

        post_claim = self._operation_selector(
            gamma_session, BRACKET_SESSION_SLOT_CLAIM_EVENT, "post"
        )
        abandoned = copy.deepcopy(
            self.receipts.before(
                self._intent_selector(
                    gamma_session,
                    BRACKET_SESSION_SLOT_CLAIM_EVENT,
                    "post",
                )
            )
        )
        pre_final = self._receipt_selector(
            gamma_session, BRACKET_SESSION_FINALIZATION_EVENT, "pre"
        )
        abandoned = abandoned.replace(
            pre_final,
            lambda row: self._changed(
                row,
                lambda value: value.__setitem__("disposition", "abandoned"),
            ),
        )
        abandoned = self._rechain(abandoned)
        abandoned_snapshot = self._variant_snapshot(abandoned)
        self.assertIn(
            "calibration_ledger_bracket_session_open",
            abandoned_snapshot.refusal_reasons,
        )

    def test_refuses_head_pin_mismatch_rollback_fork_or_uncommitted_terminal_head(
        self,
    ) -> None:
        mismatch_pin = {
            "sequence": _EXPECTED_TERMINAL_SEQUENCE,
            "head_digest": "f" * 64,
            "ledger_schema": LEDGER_SCHEMA,
        }
        mismatch = self._variant_snapshot(self.receipts, mismatch_pin)
        self.assertIn("calibration_ledger_head_mismatch", mismatch.refusal_reasons)

        gamma_session = self.windows["gamma"]["session_id"]
        post_final = self._operation_selector(
            gamma_session, BRACKET_SESSION_FINALIZATION_EVENT, "post"
        )
        rollback = self._variant_snapshot(
            copy.deepcopy(
                self.receipts.before(
                    self._intent_selector(
                        gamma_session,
                        BRACKET_SESSION_FINALIZATION_EVENT,
                        "post",
                    )
                )
            ),
            json.loads(self.final_pin_bytes),
        )
        self.assertIn("calibration_ledger_rollback", rollback.refusal_reasons)

        fork_selector = self._receipt_selector(
            self.windows["gamma"]["session_id"],
            BRACKET_SESSION_SLOT_CLAIM_EVENT,
            "pre",
        )
        forked = self.receipts.replace(
            fork_selector,
            lambda row: _receipt(
                self._changed(
                    row,
                    lambda value: value.__setitem__(
                        "predecessor_digest", "e" * 64
                    ),
                )
            ),
        )
        fork = self._variant_snapshot(forked)
        self.assertIn("calibration_ledger_chain_conflict", fork.refusal_reasons)

        repo = self.root / "synthetic-repo"
        ledger = repo / "runs" / "ledger.jsonl"
        pin = repo / "configs" / "calibration" / "head.json"
        ledger.parent.mkdir(parents=True)
        pin.parent.mkdir(parents=True)
        ledger.write_bytes(self.final_ledger_bytes)
        pin.write_bytes(self.final_pin_bytes)
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
            ["git", "commit", "-qm", "pin synthetic terminal head"],
            cwd=repo,
            check=True,
        )
        pin.write_text(
            json.dumps(json.loads(self.final_pin_bytes), indent=2) + "\n",
            encoding="utf-8",
        )
        uncommitted = self._load_snapshot(
            ledger=ledger,
            pin=pin,
            require_committed_pin=True,
            repo_root=repo,
        )
        self.assertIn(
            "calibration_ledger_head_uncommitted", uncommitted.refusal_reasons
        )

    def test_refuses_omitted_added_duplicated_off_ledger_or_substituted_observations(
        self,
    ) -> None:
        imported = next(
            row
            for row in self.snapshot.observations
            if row.is_historical_import and row.disposition == "valid"
        )
        fake = replace(
            self.candidates[0],
            attempt_id="synthetic-off-ledger",
            content_id=_hash("synthetic-off-ledger-content"),
            ledger_receipt_digest=_hash("synthetic-off-ledger-receipt"),
        )
        variants = {
            "omitted": self.candidates[:-1],
            "added": (*self.candidates, fake),
            "duplicated": (*self.candidates, self.candidates[0]),
            "off-ledger": (*self.candidates, self._candidate(imported)),
            "content-substituted": (
                replace(self.candidates[0], content_id=_hash("substituted-content")),
                *self.candidates[1:],
            ),
        }
        for name, candidates in variants.items():
            with self.subTest(vector=name):
                _result, reasons = self._evaluate("alpha", candidates=candidates)
                self.assertEqual(
                    reasons, ("calibration_ledger_off_ledger_artifact",)
                )

    def test_refuses_missing_tampered_swapped_or_cross_window_bracket_binding(
        self,
    ) -> None:
        _result, reasons = self._evaluate("alpha", binding=None)
        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))

        tampered = copy.deepcopy(self.bindings["alpha"])
        tampered["window_id"] = "tampered-without-digest-update"
        _result, reasons = self._evaluate("alpha", binding=tampered)
        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))

        swapped = copy.deepcopy(self.bindings["alpha"])
        swapped["endpoints"]["pre"], swapped["endpoints"]["post"] = (
            swapped["endpoints"]["post"],
            swapped["endpoints"]["pre"],
        )
        swapped = self._rehash_binding(swapped)
        _result, reasons = self._evaluate("alpha", binding=swapped)
        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))

        _result, reasons = self._evaluate(
            "alpha", binding=self.bindings["beta"]
        )
        self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))

    def test_refuses_noncausal_stale_t1_protocol_or_epoch_mismatched_endpoint(
        self,
    ) -> None:
        gamma = self.windows["gamma"]
        selectors = {
            "open": self._receipt_selector(
                gamma["session_id"],
                BRACKET_SESSION_OPEN_EVENT,
            ),
            "pre": self._receipt_selector(
                gamma["session_id"],
                BRACKET_SESSION_FINALIZATION_EVENT,
                "pre",
            ),
            "post": self._receipt_selector(
                gamma["session_id"],
                BRACKET_SESSION_FINALIZATION_EVENT,
                "post",
            ),
        }

        variants: dict[str, tuple[ReceiptCorpus, tuple[str, ...]]] = {}
        noncausal = self.receipts.replace(
            selectors["pre"],
            lambda row: self._changed(
                row,
                lambda value: value.__setitem__(
                    "capture_wall_time_s",
                    str(gamma["window_start_s"] + 1.0),
                ),
            ),
        )
        variants["noncausal"] = (
            self._rechain(noncausal),
            ("calibration_bracket_binding_invalid",),
        )

        stale = self.receipts.replace(
            selectors["post"],
            lambda row: self._changed(
                row,
                lambda value: value.__setitem__(
                    "capture_wall_time_s",
                    str(gamma["window_start_s"] + MAX_AGE_S + 1.0),
                ),
            ),
        )
        variants["stale"] = (
            self._rechain(stale),
            ("instrument_calibration_stale",),
        )

        def wrong_open_t1(value: dict) -> None:
            value["slots"]["pre"]["t1_bindings"]["mlx_version"] = "wrong-mlx"

        def wrong_final_t1(value: dict) -> None:
            value["t1_bindings"]["mlx_version"] = "wrong-mlx"

        wrong_t1 = self.receipts.replace(
            selectors["open"],
            lambda row: self._changed(row, wrong_open_t1),
        ).replace(
            selectors["pre"],
            lambda row: self._changed(row, wrong_final_t1),
        )
        variants["t1"] = (
            self._rechain(wrong_t1),
            ("calibration_bracket_binding_invalid",),
        )

        def wrong_open_protocol(value: dict) -> None:
            slot = value["slots"]["pre"]
            slot["t1_bindings"]["pulse_protocol_id"] = PROTOCOL_V2_ID
            slot["identity_epoch"]["pulse_protocol_id"] = PROTOCOL_V2_ID

        def wrong_final_protocol(value: dict) -> None:
            value["t1_bindings"]["pulse_protocol_id"] = PROTOCOL_V2_ID
            value["identity_epoch"]["pulse_protocol_id"] = PROTOCOL_V2_ID

        wrong_protocol = self.receipts.replace(
            selectors["open"],
            lambda row: self._changed(row, wrong_open_protocol),
        ).replace(
            selectors["pre"],
            lambda row: self._changed(row, wrong_final_protocol),
        )
        variants["protocol"] = (
            self._rechain(wrong_protocol),
            ("calibration_bracket_binding_invalid",),
        )

        def wrong_open_epoch(value: dict) -> None:
            slot = value["slots"]["pre"]
            slot["t1_bindings"]["os_build"] = "wrong-os-build"
            slot["identity_epoch"]["os_build"] = "wrong-os-build"

        def wrong_final_epoch(value: dict) -> None:
            value["t1_bindings"]["os_build"] = "wrong-os-build"
            value["identity_epoch"]["os_build"] = "wrong-os-build"

        wrong_epoch = self.receipts.replace(
            selectors["open"],
            lambda row: self._changed(row, wrong_open_epoch),
        ).replace(
            selectors["pre"],
            lambda row: self._changed(row, wrong_final_epoch),
        )
        variants["epoch"] = (
            self._rechain(wrong_epoch),
            ("calibration_bracket_binding_invalid",),
        )

        for name, (receipts, expected_reasons) in variants.items():
            with self.subTest(vector=name):
                snapshot = self._variant_snapshot(receipts)
                binding = build_calibration_bracket_binding(
                    snapshot,
                    session_id=gamma["session_id"],
                    window_id=gamma["window_id"],
                    plan_id=gamma["plan_id"],
                    plan_sha256=gamma["plan_sha256"],
                    evidence_root_id=gamma["evidence_root_id"],
                    runs_root=gamma["runs_root"],
                )
                _result, reasons = self._evaluate(
                    "gamma",
                    snapshot=snapshot,
                    candidates=self._discover(snapshot),
                    binding=binding,
                )
                self.assertEqual(reasons, expected_reasons)

    def test_refuses_systematic_classification(self) -> None:
        window = {
            "session_id": "session-d117-systematic",
            "window_id": "plan-d117-systematic-refusal",
            "plan_id": "plan-d117-systematic-refusal",
            "plan_sha256": "d" * 64,
            "evidence_root_id": "evidence-d117-systematic-refusal",
            "runs_root": "/synthetic/d117/systematic-refusal",
        }
        attempts = {
            slot: f"d117-systematic-{slot}" for slot in ("pre", "post")
        }
        slots = {
            slot: {
                "attempt_id": attempts[slot],
                "custody_locator": (
                    f"{window['runs_root']}/instrument_validation/{attempts[slot]}"
                ),
                "identity_epoch": self.epoch,
                "t1_bindings": self.t1,
            }
            for slot in ("pre", "post")
        }
        append_bracket_session_receipt(
            self.ledger,
            **window,
            slots=slots,
            head_pin_path=self.pin,
            require_committed_pin=False,
        )
        claim_bracket_session_slot(
            self.ledger,
            session_id=window["session_id"],
            slot="pre",
            attempt_id=attempts["pre"],
        )
        finalize_bracket_session_slot(
            self.ledger,
            session_id=window["session_id"],
            slot="pre",
            disposition="systematic-invalid",
            custody_locator=slots["pre"]["custody_locator"],
            artifact_sha256=_content_hashes(attempts["pre"]),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="170.0",
            exact_bound_lexeme_s="0.040000",
        )
        abort_bracket_session(
            self.ledger,
            session_id=window["session_id"],
            reason="synthetic systematic preflight refusal",
        )
        self.pin.write_bytes(
            _pin_bytes(
                terminal_head_pin_for_session(
                    self.ledger, session_id=window["session_id"]
                )
            )
        )
        snapshot = self._load_snapshot()
        candidates = self._discover(snapshot)
        result, reasons = self._evaluate(
            "alpha", snapshot=snapshot, candidates=candidates
        )
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertIn(
            "new_systematic_failure_challenges_preflight_screen",
            result["acceptance"]["prospective_rederivation"][
                "observed_triggers"
            ],
        )

    @unittest.skip("U2 successor engine pending")
    def test_range_expanding_live_observation_requires_successor(self) -> None:
        vector = self.scenario["staged_successor_vectors"][
            "range_expanding_live_observation"
        ]
        self.assertEqual(
            vector["expected_trigger"],
            "new_valid_same_identity_capture_expands_observed_range",
        )

    @unittest.skip("U2 successor engine pending")
    def test_d102_observation_count_boundary_requires_successor(self) -> None:
        vector = self.scenario["staged_successor_vectors"][
            "d102_count_boundary"
        ]
        self.assertEqual(vector["expected_total_valid_same_epoch"], 34)
        self.assertEqual(
            vector["expected_trigger"], "corpus_doubles_from_17_to_34"
        )

    @unittest.skip("U2 successor engine pending")
    def test_successor_prior_set_refuses_omitted_or_changed_authenticated_prefix(
        self,
    ) -> None:
        vector = self.scenario["staged_successor_vectors"][
            "successor_prior_set_integrity"
        ]
        self.assertEqual(
            vector["mutations"],
            [
                "omit_authenticated_prefix_member",
                "change_authenticated_prefix_member",
            ],
        )


if __name__ == "__main__":
    unittest.main()
