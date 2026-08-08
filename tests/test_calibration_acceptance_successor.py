from __future__ import annotations

import ast
import fcntl
import hashlib
import io
import json
import os
import stat
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import joulewise.calibration_bracketing as bracketing
import joulewise.calibration_acceptance_attestation as attestation
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    RECEIPT_SCHEMA,
    CalibrationBracketSession,
    CalibrationLedgerSnapshot,
    LedgerObservation,
    bootstrap_historical_import,
    canonical_sha256,
    content_id_from_artifact_hashes,
    load_calibration_ledger_snapshot,
)
from scripts import build_calibration_acceptance_successor as successor


REPO_ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE_PATH = (
    REPO_ROOT / "configs" / "calibration" / "calibration_acceptance_d079_v2.json"
)
REGISTRY_PATH = bracketing.DEFAULT_ACCEPTANCE_REGISTRY_PATH
PARENT_HEAD = "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"
REAL_D079_TABLE = REPO_ROOT / (
    "docs/process_traces/2026-08-06-d079-issuance-coldgate/"
    "ISSUANCE-disposition-table.json"
)
REAL_D079_CUSTODY_MANIFEST = REPO_ROOT / (
    "docs/process_traces/2026-08-06-d079-issuance-coldgate/"
    "ISSUANCE-custody-manifest.json"
)
REAL_D079_TABLE_SHA256 = (
    "5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a"
)
REAL_D079_CUSTODY_MANIFEST_SHA256 = (
    "99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078"
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _receipt(**fields: object) -> dict:
    value = dict(fields)
    value["receipt_digest"] = canonical_sha256(value)
    return value


def _real_import_plan(ledger: Path, pin: Path):
    pin.parent.mkdir(parents=True, exist_ok=True)
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
    return bootstrap_historical_import(
        ledger,
        head_pin_path=pin,
        checkout_root=Path("/Users/edr"),
        disposition_table_raw=REAL_D079_TABLE.read_bytes(),
        expected_disposition_table_sha256=REAL_D079_TABLE_SHA256,
        custody_manifest_raw=REAL_D079_CUSTODY_MANIFEST.read_bytes(),
        expected_custody_manifest_sha256=REAL_D079_CUSTODY_MANIFEST_SHA256,
        execute=False,
        require_committed_pin=False,
        repo_root=ledger.parents[1],
    )


def _parent_artifact() -> dict:
    return json.loads(ACCEPTANCE_PATH.read_bytes())


def _parent_observations() -> list[LedgerObservation]:
    artifact = _parent_artifact()
    disposition_table = json.loads(REAL_D079_TABLE.read_bytes())
    source_by_attempt = {
        member["attempt_id"]: member for member in disposition_table["members"]
    }
    custody_by_content = json.loads(REAL_D079_CUSTODY_MANIFEST.read_bytes())[
        "members"
    ]
    corpus_by_attempt = {
        member["member_id"]: member
        for member in artifact["derivation_corpus"]["members"]
    }
    systematic_bounds = {
        "20260726T000039-491995f3": "0.035435840879704805",
        "20260801T064830-c76f5d1c": "0.0350400833260715",
    }
    observations: list[LedgerObservation] = []
    for index, row in enumerate(
        artifact["prior_observation_set"]["observations"], start=1
    ):
        member = corpus_by_attempt.get(row["attempt_id"])
        source = source_by_attempt[row["attempt_id"]]
        manifest_sha = source["artifact_sha256"]["manifest.json"]
        evidence_sha = source["artifact_sha256"]["instrument_evidence.json"]
        bound = (
            member["b_fiducial_s"]
            if member is not None
            else systematic_bounds.get(row["attempt_id"], "0.027000000000000001")
        )
        sequence = index * 2
        observations.append(
            LedgerObservation(
                sequence=sequence,
                receipt_digest=(PARENT_HEAD if sequence == 76 else _digest(f"r-{sequence}")),
                attempt_id=row["attempt_id"],
                content_id=row["content_id"],
                artifact_sha256={
                    "manifest.json": manifest_sha,
                    "instrument_evidence.json": evidence_sha,
                },
                identity_epoch=dict(artifact["identity_epoch"]),
                t1_bindings={},
                capture_wall_time_s=str(sequence),
                exact_bound_lexeme_s=bound,
                disposition=row["disposition"],
                custody_locator=custody_by_content[row["content_id"]],
                observation_kind="historical-import",
            )
        )
    return observations


def _new_observation(
    index: int,
    *,
    bound: str = "0.0200000000000000001",
    disposition: str = "valid",
    content_id: str | None = None,
    epoch: dict | None = None,
    artifacts: dict | None = None,
) -> LedgerObservation:
    attempt_id = f"live-{index:02d}"
    artifact_hashes = artifacts or {
        "manifest.json": _digest(f"live-manifest-{index}"),
        "instrument_evidence.json": _digest(f"live-evidence-{index}"),
    }
    return LedgerObservation(
        sequence=77 + index,
        receipt_digest=_digest(f"live-receipt-{index}"),
        attempt_id=attempt_id,
        content_id=(
            content_id
            if content_id is not None
            else content_id_from_artifact_hashes(artifact_hashes)
        ),
        artifact_sha256=artifact_hashes,
        identity_epoch=epoch or dict(_parent_artifact()["identity_epoch"]),
        t1_bindings={},
        capture_wall_time_s=str(1000 + index),
        exact_bound_lexeme_s=bound,
        disposition=disposition,
        custody_locator=f"/authenticated/live/{attempt_id}",
        observation_kind="live-capture",
    )


def _snapshot(
    extras: tuple[LedgerObservation, ...] = (),
    *,
    reasons: tuple[str, ...] = (),
) -> CalibrationLedgerSnapshot:
    receipts = [
        {
            "sequence": index,
            "event": (
                "historical-import-v1-finalization"
                if index == 76
                else "historical-import-v1-reservation"
            ),
            "receipt_digest": PARENT_HEAD if index == 76 else _digest(f"r-{index}"),
        }
        for index in range(1, 77)
    ]
    observations = _parent_observations()
    for extra in sorted(extras, key=lambda item: item.sequence):
        while len(receipts) < extra.sequence - 1:
            sequence = len(receipts) + 1
            receipts.append(
                {
                    "sequence": sequence,
                    "event": "reservation",
                    "receipt_digest": _digest(f"padding-{sequence}"),
                }
            )
        receipt = {
            "sequence": extra.sequence,
            "event": "finalization",
            "receipt_digest": extra.receipt_digest,
        }
        if extra.disposition == "abandoned":
            receipt.update(
                {
                    "attempt_id": extra.attempt_id,
                    "disposition": extra.disposition,
                    "content_id": extra.content_id,
                    "artifact_sha256": dict(extra.artifact_sha256),
                    "exact_bound_lexeme_s": extra.exact_bound_lexeme_s,
                }
            )
        receipts.append(receipt)
        observations.append(extra)
    head_digest = receipts[-1]["receipt_digest"]
    return CalibrationLedgerSnapshot(
        ledger_schema=LEDGER_SCHEMA,
        ledger_path=Path("/authenticated/ledger.jsonl"),
        head_sequence=len(receipts),
        head_digest=head_digest,
        receipts=tuple(receipts),
        observations=tuple(observations),
        refusal_reasons=reasons,
        baseline_sequence=76,
        baseline_digest=PARENT_HEAD,
        committed_head_sequence=len(receipts),
        committed_head_digest=head_digest,
    )


def _probe(snapshot: CalibrationLedgerSnapshot) -> dict:
    return bracketing.probe_calibration_acceptance_trigger(
        snapshot,
        observed_identity_epoch=_parent_artifact()["identity_epoch"],
        require_committed_registry=False,
        verify_custody=False,
    )


def _init_publication_repo(root: Path) -> tuple[Path, Path]:
    config = root / "configs/calibration"
    config.mkdir(parents=True)
    (config / ACCEPTANCE_PATH.name).write_bytes(ACCEPTANCE_PATH.read_bytes())
    registry = config / REGISTRY_PATH.name
    registry.write_bytes(REGISTRY_PATH.read_bytes())
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.invalid"],
        cwd=root,
        check=True,
    )
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "anchor"], cwd=root, check=True)
    return registry, config


def _open_pre_snapshot() -> CalibrationLedgerSnapshot:
    base = _snapshot()
    pre = _new_observation(2, bound="0.02")
    pre = replace(
        pre,
        sequence=79,
        bracket_session_id="session-1",
        bracket_slot="pre",
        bracket_window_id="window-1",
        bracket_plan_id="plan-1",
        bracket_plan_sha256="1" * 64,
        bracket_evidence_root_id="evidence-1",
        bracket_runs_root="/runs/window-1",
        observation_kind="bracket-session-finalized",
    )
    open_digest = _digest("session-open")
    claim_digest = _digest("session-pre-claim")
    receipts = (
        *base.receipts,
        {
            "sequence": 77,
            "event": "bracket-session-open",
            "session_id": "session-1",
            "predecessor_digest": PARENT_HEAD,
            "receipt_digest": open_digest,
        },
        {
            "sequence": 78,
            "event": "bracket-session-slot-claim",
            "session_id": "session-1",
            "receipt_digest": claim_digest,
        },
        {
            "sequence": 79,
            "event": "bracket-session-slot-finalization",
            "session_id": "session-1",
            "receipt_digest": pre.receipt_digest,
        },
    )
    session = CalibrationBracketSession(
        session_id="session-1",
        window_id="window-1",
        plan_id="plan-1",
        plan_sha256="1" * 64,
        evidence_root_id="evidence-1",
        runs_root="/runs/window-1",
        capability_receipt_digest=open_digest,
        capability_sequence=77,
        slot_attempt_ids={"pre": pre.attempt_id, "post": "post-attempt"},
        state="open",
        finalized_slots={"pre": pre},
    )
    return replace(
        base,
        head_sequence=79,
        head_digest=pre.receipt_digest,
        receipts=receipts,
        refusal_reasons=(
            "calibration_ledger_bracket_session_open",
            "calibration_ledger_head_mismatch",
        ),
        bracket_sessions=(session,),
        committed_head_sequence=76,
        committed_head_digest=PARENT_HEAD,
    )


class AcceptanceAttestationEnrollmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        abandoned = replace(
            _new_observation(0, disposition="abandoned"),
            content_id=None,
            artifact_sha256={},
            exact_bound_lexeme_s=None,
        )
        cls.snapshot = _snapshot(
            (abandoned, _new_observation(1, bound="0.02"))
        )
        cls.build = successor.build_calibration_acceptance_successor(
            cls.snapshot,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )

    def test_schema_leaf_exact_set_equals_declared_enrollment(self) -> None:
        successor_leaves = attestation.schema_leaf_patterns(
            attestation.SUCCESSOR_WIRE_SCHEMA
        )
        registry_leaves = attestation.schema_leaf_patterns(
            attestation.REGISTRY_WIRE_SCHEMA
        )
        self.assertEqual(
            successor_leaves | registry_leaves,
            set(attestation.ACCEPTANCE_ATTESTATION_FIELDS),
        )
        self.assertEqual(
            attestation.wire_leaf_patterns(
                self.build.artifact, attestation.SUCCESSOR_WIRE_SCHEMA
            ),
            successor_leaves,
        )
        self.assertEqual(
            attestation.wire_leaf_patterns(
                self.build.registry, attestation.REGISTRY_WIRE_SCHEMA
            ),
            registry_leaves,
        )

    def test_enrollment_pairing_and_annotation_contract(self) -> None:
        fields = attestation.ACCEPTANCE_ATTESTATION_FIELDS
        self.assertEqual(len(fields), len(set(fields)))
        annotations = {
            pattern
            for pattern, spec in fields.items()
            if spec.classification
            == attestation.NON_AUTHORITATIVE_ANNOTATION
        }
        self.assertEqual(
            annotations,
            {
                "issuance.reason",
                "prior_observation_set.observations[*].disposing_decision_id",
            },
        )
        for pattern, spec in fields.items():
            with self.subTest(pattern=pattern):
                if spec.classification == attestation.VERIFIED:
                    self.assertTrue(callable(spec.verifier))
                    self.assertTrue(callable(spec.forge_mutator))
                    self.assertIsNotNone(spec.stable_failure_code)
                    self.assertIsNone(spec.consumer_policy)
                else:
                    self.assertIsNone(spec.verifier)
                    self.assertIsNone(spec.forge_mutator)
                    self.assertIsNotNone(spec.consumer_policy)

    def test_maximal_fixture_visits_every_concrete_leaf_once(self) -> None:
        artifact_result = attestation.acceptance_attestation_pass(
            self.build.artifact,
            schema=attestation.SUCCESSOR_WIRE_SCHEMA,
            layer=attestation.S,
            require_all_patterns_visited=True,
        )
        registry_result = attestation.acceptance_attestation_pass(
            self.build.registry,
            schema=attestation.REGISTRY_WIRE_SCHEMA,
            layer=attestation.R,
            require_all_patterns_visited=True,
        )
        for result in (artifact_result, registry_result):
            self.assertEqual(result.violations, ())
            self.assertEqual(
                len(result.visited_concrete_leaves),
                len(set(result.visited_concrete_leaves)),
            )

    def test_unenrolled_new_leaf_fails_closed(self) -> None:
        changed = json.loads(json.dumps(self.build.artifact))
        changed["future_authority_leaf"] = "unenrolled"
        result = attestation.acceptance_attestation_pass(
            changed,
            schema=attestation.SUCCESSOR_WIRE_SCHEMA,
            layer=attestation.S,
        )
        self.assertIn("acceptance_attestation_unenrolled_field", result.violations)

    def test_verified_view_and_static_consumers_exclude_annotations(self) -> None:
        verified, violations = bracketing._verified_acceptance_after_ledger_residue(
            self.build.artifact,
            self.snapshot,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            verify_custody=False,
            require_terminal_cutoff=True,
        )
        self.assertEqual(violations, ())
        self.assertIsInstance(verified, attestation.VerifiedAcceptance)
        decision = verified.as_dict()
        self.assertNotIn("reason", decision["issuance"])
        self.assertTrue(
            all(
                "disposing_decision_id" not in row
                for row in decision["prior_observation_set"]["observations"]
            )
        )
        tree = ast.parse((REPO_ROOT / "joulewise/calibration_bracketing.py").read_text())
        decision_functions = {
            "evaluate_calibration_bracket",
            "probe_calibration_acceptance_trigger",
        }
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in decision_functions:
                string_constants = {
                    child.value
                    for child in ast.walk(node)
                    if isinstance(child, ast.Constant)
                    and isinstance(child.value, str)
                }
                self.assertNotIn("disposing_decision_id", string_constants)
                self.assertNotIn(
                    "issuance",
                    {
                        child.id
                        for child in ast.walk(node)
                        if isinstance(child, ast.Name)
                    },
                )


class RegistryTrustAnchorTests(unittest.TestCase):
    def test_current_registry_authenticates_exact_issued_state(self) -> None:
        registry = bracketing.load_calibration_acceptance_registry(
            require_committed=False
        )
        self.assertIsNotNone(registry)
        active = bracketing._active_registry_entry(registry)
        self.assertEqual(active["acceptance_id"], "d079_calibration_acceptance_v2_n19")
        self.assertEqual(
            active["artifact_sha256"],
            "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
        )
        artifact = bracketing.load_calibration_acceptance_bound()
        counts = {
            disposition: sum(
                row["disposition"] == disposition
                for row in artifact["prior_observation_set"]["observations"]
            )
            for disposition in ("valid", "systematic-invalid", "ordinary-invalid")
        }
        self.assertEqual(counts, {"valid": 30, "systematic-invalid": 2, "ordinary-invalid": 6})
        self.assertEqual(active["ledger_cutoff"]["sequence"], 76)


class AcceptanceAttestationForgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        abandoned = replace(
            _new_observation(0, disposition="abandoned"),
            content_id=None,
            artifact_sha256={},
            exact_bound_lexeme_s=None,
        )
        cls.snapshot = _snapshot(
            (abandoned, _new_observation(1, bound="0.02"))
        )
        cls.build = successor.build_calibration_acceptance_successor(
            cls.snapshot,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )

    def test_every_successor_verified_field_has_discriminating_forgery(self) -> None:
        specs = [
            (pattern, spec)
            for pattern, spec in attestation.ACCEPTANCE_ATTESTATION_FIELDS.items()
            if spec.classification == attestation.VERIFIED
            and not pattern.startswith("registry.")
        ]
        self.assertEqual(len(specs), 118)
        authentic_parent = _parent_artifact()
        authentic_parent_copy = json.loads(json.dumps(authentic_parent))
        parent_sha = self.build.registry["entries"][0]["artifact_sha256"]
        for pattern, spec in specs:
            with self.subTest(pattern=pattern):
                forged = json.loads(json.dumps(self.build.artifact))
                spec.forge_mutator(forged)
                if pattern != "derivation_sha256":
                    forged["derivation_sha256"] = bracketing._canonical_sha256(
                        {
                            key: value
                            for key, value in forged.items()
                            if key != "derivation_sha256"
                        }
                    )
                standalone: list[str] = []
                bracketing._valid_acceptance_bound(
                    forged,
                    parent=authentic_parent,
                    parent_artifact_sha256=parent_sha,
                    violations=standalone,
                )
                _view, ledger_reasons = (
                    bracketing._verified_acceptance_after_ledger_residue(
                        forged,
                        self.snapshot,
                        observed_identity_epoch=authentic_parent[
                            "identity_epoch"
                        ],
                        verify_custody=False,
                        require_terminal_cutoff=True,
                    )
                )
                self.assertIn(
                    spec.stable_failure_code,
                    set(standalone) | set(ledger_reasons),
                )
                self.assertEqual(authentic_parent, authentic_parent_copy)

    def test_every_registry_verified_field_refuses_in_committed_temp_repo(self) -> None:
        specs = [
            (pattern, spec)
            for pattern, spec in attestation.ACCEPTANCE_ATTESTATION_FIELDS.items()
            if pattern.startswith("registry.")
        ]
        self.assertEqual(len(specs), 15)
        for pattern, spec in specs:
            with self.subTest(pattern=pattern), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                forged = json.loads(json.dumps(self.build.registry))
                spec.forge_mutator(forged)
                for entry in self.build.registry["entries"]:
                    destination = root / entry["artifact_path"]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(
                        self.build.artifact_bytes
                        if entry["acceptance_id"]
                        == self.build.artifact["acceptance_id"]
                        else (REPO_ROOT / entry["artifact_path"]).read_bytes()
                    )
                registry_path = (
                    root
                    / "configs/calibration/calibration_acceptance_registry.json"
                )
                registry_path.write_bytes(successor._pretty_json_bytes(forged))
                subprocess.run(["git", "init", "-q"], cwd=root, check=True)
                subprocess.run(
                    ["git", "config", "user.name", "attestation-test"],
                    cwd=root,
                    check=True,
                )
                subprocess.run(
                    ["git", "config", "user.email", "test@example.invalid"],
                    cwd=root,
                    check=True,
                )
                subprocess.run(["git", "add", "."], cwd=root, check=True)
                subprocess.run(
                    ["git", "commit", "-qm", "forged authority"],
                    cwd=root,
                    check=True,
                )
                with self.assertRaises(
                    bracketing.CalibrationAcceptanceRegistryRefusal
                ) as raised:
                    bracketing.load_calibration_acceptance_registry(
                        registry_path,
                        repo_root=root,
                        require_committed=True,
                    )
                self.assertIn(
                    spec.stable_failure_code,
                    raised.exception.violations,
                )

    def test_forged_range_only_trigger_refuses_standalone_and_registry(self) -> None:
        forged = json.loads(json.dumps(self.build.artifact))
        self.assertEqual(
            forged["lineage"]["trigger_judgment"]["triggers"],
            ["new_valid_same_identity_capture_expands_observed_range"],
        )
        forged["lineage"]["trigger_judgment"]["triggers"] = [
            "content_distinct_valid_same_epoch_count_boundary"
        ]
        forged["derivation_sha256"] = bracketing._canonical_sha256(
            {
                key: value
                for key, value in forged.items()
                if key != "derivation_sha256"
            }
        )
        forged_bytes = successor._pretty_json_bytes(forged)
        registry = json.loads(json.dumps(self.build.registry))
        active = next(entry for entry in registry["entries"] if entry["active"])
        active["artifact_sha256"] = hashlib.sha256(forged_bytes).hexdigest()
        active["derivation_sha256"] = forged["derivation_sha256"]
        standalone: list[str] = []
        self.assertFalse(
            bracketing._valid_acceptance_bound(
                forged,
                parent=_parent_artifact(),
                parent_artifact_sha256=registry["entries"][0][
                    "artifact_sha256"
                ],
                violations=standalone,
            )
        )
        self.assertIn("trigger_judgment_mismatch", standalone)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for entry in registry["entries"]:
                destination = root / entry["artifact_path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(
                    forged_bytes
                    if entry["acceptance_id"] == forged["acceptance_id"]
                    else (REPO_ROOT / entry["artifact_path"]).read_bytes()
                )
            registry_path = (
                root / "configs/calibration/calibration_acceptance_registry.json"
            )
            registry_path.write_bytes(successor._pretty_json_bytes(registry))
            with self.assertRaises(
                bracketing.CalibrationAcceptanceRegistryRefusal
            ) as raised:
                bracketing.load_calibration_acceptance_registry(
                    registry_path,
                    repo_root=root,
                    require_committed=False,
                )
        self.assertEqual(
            raised.exception.reason,
            "acceptance_registry_trigger_judgment_mismatch",
        )

    def test_registry_rejects_multiple_active_without_a_cycle(self) -> None:
        registry = json.loads(REGISTRY_PATH.read_bytes())
        parent = registry["entries"][0]
        child = {
            **json.loads(json.dumps(parent)),
            "acceptance_id": "child",
            "artifact_path": "configs/calibration/child.json",
            "artifact_schema": bracketing.ACCEPTANCE_SUCCESSOR_SCHEMA,
            "generation": 2,
            "parent_acceptance_id": parent["acceptance_id"],
            "parent_artifact_sha256": parent["artifact_sha256"],
            "count_boundary_rule": bracketing.SUCCESSOR_COUNT_BOUNDARY_RULE,
            "ledger_cutoff": {
                **parent["ledger_cutoff"],
                "sequence": parent["ledger_cutoff"]["sequence"] + 1,
                "head_digest": "1" * 64,
            },
        }
        registry["entries"].append(child)
        violations: list[str] = []
        self.assertFalse(
            bracketing._valid_registry(registry, violations=violations)
        )
        self.assertIn("registry_active_cardinality_invalid", violations)
        self.assertIn("registry_active_leaf_invalid", violations)

    def test_registry_rejects_self_cycle_without_multiple_active_entries(self) -> None:
        registry = json.loads(REGISTRY_PATH.read_bytes())
        parent = registry["entries"][0]
        child = {
            **json.loads(json.dumps(parent)),
            "acceptance_id": "self-cycle",
            "artifact_path": "configs/calibration/self-cycle.json",
            "artifact_schema": bracketing.ACCEPTANCE_SUCCESSOR_SCHEMA,
            "generation": 2,
            "active": True,
            "parent_acceptance_id": "self-cycle",
            "parent_artifact_sha256": parent["artifact_sha256"],
            "count_boundary_rule": bracketing.SUCCESSOR_COUNT_BOUNDARY_RULE,
            "ledger_cutoff": {
                **parent["ledger_cutoff"],
                "sequence": parent["ledger_cutoff"]["sequence"] + 1,
                "head_digest": "2" * 64,
            },
        }
        parent["active"] = False
        registry["entries"].append(child)
        self.assertFalse(bracketing._valid_registry(registry))

    def test_registry_rejects_traversal_absolute_and_duplicate_paths(self) -> None:
        registry = json.loads(REGISTRY_PATH.read_bytes())
        for path in ("../escape.json", "/tmp/escape.json", "configs/calibration/../x.json"):
            with self.subTest(path=path):
                changed = json.loads(json.dumps(registry))
                changed["entries"][0]["artifact_path"] = path
                self.assertFalse(bracketing._valid_registry(changed))
        parent = registry["entries"][0]
        child = {
            **json.loads(json.dumps(parent)),
            "acceptance_id": "duplicate-path-child",
            "artifact_schema": bracketing.ACCEPTANCE_SUCCESSOR_SCHEMA,
            "generation": 2,
            "active": True,
            "parent_acceptance_id": parent["acceptance_id"],
            "parent_artifact_sha256": parent["artifact_sha256"],
            "count_boundary_rule": bracketing.SUCCESSOR_COUNT_BOUNDARY_RULE,
            "ledger_cutoff": {
                **parent["ledger_cutoff"],
                "sequence": parent["ledger_cutoff"]["sequence"] + 1,
                "head_digest": "3" * 64,
            },
        }
        parent["active"] = False
        registry["entries"].append(child)
        self.assertEqual(
            registry["entries"][0]["artifact_path"],
            registry["entries"][1]["artifact_path"],
        )
        self.assertFalse(bracketing._valid_registry(registry))

    def test_registry_requires_committed_bytes_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact_path = root / "configs/calibration/calibration_acceptance_d079_v2.json"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_bytes(ACCEPTANCE_PATH.read_bytes())
            registry_path = artifact_path.parent / "calibration_acceptance_registry.json"
            registry_path.write_bytes(REGISTRY_PATH.read_bytes())
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "anchor"], cwd=root, check=True)
            self.assertIsNotNone(
                bracketing.load_calibration_acceptance_registry(
                    registry_path, repo_root=root, require_committed=True
                )
            )
            registry_path.write_bytes(registry_path.read_bytes() + b" ")
            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceRegistryRefusal,
                "acceptance_registry_missing_commit",
            ):
                bracketing.load_calibration_acceptance_registry(
                    registry_path, repo_root=root, require_committed=True
                )

    def test_current_selection_is_plain_committed_registry_load(self) -> None:
        sentinel = {"registry": "committed"}
        with patch.object(
            bracketing,
            "load_calibration_acceptance_registry",
            return_value=sentinel,
        ) as loader:
            self.assertIs(
                bracketing._load_registry_for_current_active_selection(),
                sentinel,
            )
        loader.assert_called_once_with(require_committed=True)

    def test_registry_rejects_symlink_artifact_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "configs/calibration"
            config.mkdir(parents=True)
            target = root / "target.json"
            target.write_bytes(ACCEPTANCE_PATH.read_bytes())
            (config / "calibration_acceptance_d079_v2.json").symlink_to(target)
            registry_path = config / "calibration_acceptance_registry.json"
            registry_path.write_bytes(REGISTRY_PATH.read_bytes())
            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceRegistryRefusal,
                "acceptance_registry_artifact_path_substituted",
            ):
                bracketing.load_calibration_acceptance_registry(
                    registry_path, repo_root=root, require_committed=False
                )


class TriggerProbeTests(unittest.TestCase):
    def test_pre_probe_accepts_only_governed_open_u1_extension_shape(self) -> None:
        result = _probe(_open_pre_snapshot())
        self.assertEqual(result["outcome"], "successor_required")
        malformed = replace(
            _open_pre_snapshot(),
            refusal_reasons=("calibration_ledger_head_mismatch",),
        )
        self.assertEqual(
            _probe(malformed)["outcome"], "authentication_or_epoch_refusal"
        )

    def test_range_expansion_below_and_above_require_successor(self) -> None:
        for index, bound in enumerate(
            ("0.0200000000000000001", "0.033558756679899995")
        ):
            with self.subTest(bound=bound):
                result = _probe(_snapshot((_new_observation(index, bound=bound),)))
                self.assertEqual(result["outcome"], "successor_required")
                self.assertEqual(
                    result["observed_triggers"],
                    ["new_valid_same_identity_capture_expands_observed_range"],
                )

    def test_in_range_observation_does_not_trigger_before_boundary(self) -> None:
        result = _probe(_snapshot((_new_observation(0, bound="0.0271"),)))
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
        self.assertEqual(result["observed_triggers"], [])

    def test_counts_37_and_38_are_distinct(self) -> None:
        seven = tuple(_new_observation(index, bound="0.0271") for index in range(7))
        eight = tuple(_new_observation(index, bound="0.0271") for index in range(8))
        self.assertEqual(_probe(_snapshot(seven))["outcome"], "accepted_under_active_artifact")
        result = _probe(_snapshot(eight))
        self.assertEqual(result["outcome"], "successor_required")
        self.assertEqual(
            result["observed_triggers"],
            ["content_distinct_valid_same_epoch_count_boundary"],
        )

    def test_range_and_count_triggers_are_both_recorded_canonically(self) -> None:
        extras = (
            _new_observation(0, bound="0.02"),
            *tuple(
                _new_observation(index, bound="0.0271")
                for index in range(1, 8)
            ),
        )
        result = _probe(_snapshot(extras))
        self.assertEqual(result["outcome"], "successor_required")
        self.assertEqual(
            result["observed_triggers"],
            [
                "new_valid_same_identity_capture_expands_observed_range",
                "content_distinct_valid_same_epoch_count_boundary",
            ],
        )

    def test_systematic_classification_and_above_screen_both_refuse(self) -> None:
        cases = (
            _new_observation(0, disposition="systematic-invalid", bound="0.02"),
            _new_observation(0, disposition="valid", bound="0.04"),
        )
        for observation in cases:
            with self.subTest(disposition=observation.disposition, bound=observation.exact_bound_lexeme_s):
                result = _probe(_snapshot((observation,)))
                self.assertEqual(result["outcome"], "systematic_refusal")
                self.assertEqual(
                    result["refusal_reasons"],
                    [bracketing.SUCCESSOR_SYSTEMATIC_POLICY],
                )

    def test_ordinary_invalid_is_recorded_but_does_not_trigger(self) -> None:
        result = _probe(
            _snapshot((_new_observation(0, disposition="ordinary-invalid", bound="0.04"),))
        )
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
        self.assertEqual(len(result["new_content_ids"]), 1)

    def test_authenticated_terminal_no_content_is_excluded_without_refusal(self) -> None:
        observation = replace(
            _new_observation(0, disposition="abandoned"),
            content_id=None,
            artifact_sha256={},
            exact_bound_lexeme_s=None,
        )
        result = _probe(_snapshot((observation,)))
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
        self.assertEqual(result["new_content_ids"], [])
        self.assertEqual(result["refusal_reasons"], [])

    def test_terminal_no_content_receipt_variation_has_named_refusal(self) -> None:
        observation = replace(
            _new_observation(0, disposition="abandoned"),
            content_id=None,
            artifact_sha256={},
            exact_bound_lexeme_s=None,
        )
        snapshot = _snapshot((observation,))
        malformed_receipt = dict(snapshot.receipts[-1])
        malformed_receipt.pop("attempt_id")
        result = _probe(
            replace(snapshot, receipts=(*snapshot.receipts[:-1], malformed_receipt))
        )
        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
        self.assertEqual(
            result["refusal_reasons"],
            ["successor_terminal_no_content_receipt_malformed"],
        )

    def test_same_content_alias_does_not_increment_count(self) -> None:
        original = _parent_observations()[0]
        alias = replace(
            original,
            sequence=77,
            receipt_digest=_digest("alias-receipt"),
            attempt_id="live-alias",
            observation_kind="live-capture",
        )
        result = _probe(_snapshot((alias,)))
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
        self.assertEqual(result["new_content_ids"], [])

    def test_same_content_conflicting_disposition_epoch_bound_or_hash_refuses(self) -> None:
        base = _new_observation(0, bound="0.0271")
        changed_epoch = dict(base.identity_epoch)
        changed_epoch["os_build"] = "different"
        variants = (
            replace(base, sequence=78, attempt_id="alias", receipt_digest=_digest("a"), disposition="ordinary-invalid"),
            replace(base, sequence=78, attempt_id="alias", receipt_digest=_digest("b"), identity_epoch=changed_epoch),
            replace(base, sequence=78, attempt_id="alias", receipt_digest=_digest("c"), exact_bound_lexeme_s="0.0272"),
            replace(base, sequence=78, attempt_id="alias", receipt_digest=_digest("d"), artifact_sha256={"manifest.json": "1" * 64, "instrument_evidence.json": "2" * 64}),
        )
        for variant in variants:
            with self.subTest(receipt=variant.receipt_digest):
                result = _probe(_snapshot((base, variant)))
                self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
                self.assertIn("conflicting_content_classification_or_bytes", result["refusal_reasons"])

    def test_other_epoch_valid_is_excluded_without_self_fit(self) -> None:
        epoch = dict(_parent_artifact()["identity_epoch"])
        epoch["os_build"] = "25F85"
        result = _probe(_snapshot((_new_observation(0, epoch=epoch, bound="0.01"),)))
        self.assertEqual(result["outcome"], "accepted_under_active_artifact")

    def test_observed_epoch_and_estimator_bytes_refuse_before_science(self) -> None:
        epoch = dict(_parent_artifact()["identity_epoch"])
        epoch["hardware_model"] = "Other"
        result = bracketing.probe_calibration_acceptance_trigger(
            _snapshot(),
            observed_identity_epoch=epoch,
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
        with patch.object(bracketing, "_current_estimator_code_sha256", return_value={"x": "0" * 64}):
            result = _probe(_snapshot())
        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
        self.assertEqual(result["observed_triggers"], ["protocol_or_estimator_byte_change"])

    def test_probe_does_not_consult_writer_copied_scalar(self) -> None:
        import scripts.validate_powermetrics_fiducial as writer

        snapshot = _snapshot((_new_observation(0, bound="0.034"),))
        expected = _probe(snapshot)
        with patch.object(writer, "PREFLIGHT_SYSTEMATIC_SCREEN_S", Decimal("999")):
            actual = _probe(snapshot)
        self.assertEqual(actual, expected)

    def test_prefix_omission_and_physical_pin_mismatch_refuse(self) -> None:
        omitted = replace(_snapshot(), observations=tuple(_parent_observations()[1:]))
        self.assertEqual(_probe(omitted)["outcome"], "authentication_or_epoch_refusal")
        mismatched = replace(
            _snapshot(),
            refusal_reasons=("calibration_ledger_head_mismatch",),
        )
        self.assertEqual(_probe(mismatched)["outcome"], "authentication_or_epoch_refusal")

    def test_missing_custody_refuses_when_reauthentication_enabled(self) -> None:
        result = bracketing.probe_calibration_acceptance_trigger(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=True,
        )
        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
        self.assertIn("new_observation_custody_or_physics_invalid", result["refusal_reasons"])


class DecimalDerivationTests(unittest.TestCase):
    def test_n19_issued_pin_and_successor_kernel_split_are_exact(self) -> None:
        artifact = _parent_artifact()
        issued_stats = artifact["decimal_derivation"]["source_statistics"]
        issued_operatives = artifact["decimal_derivation"]["ratified_operatives"]
        self.assertEqual(
            issued_stats["prediction_95_two_draw_s"],
            "0.008826584887500717",
        )
        self.assertEqual(
            issued_stats["prediction_99_two_draw_s"],
            "0.012093166090593858",
        )
        self.assertEqual(issued_operatives["bracket_screen_s"], "0.010818")
        self.assertEqual(
            issued_operatives["maximum_budgetable_drift_s"],
            "0.012093166090593858",
        )
        self.assertEqual(
            issued_operatives["max_budgetable_excess_s"],
            "0.001275166090593858",
        )
        content_by_attempt = {
            row["attempt_id"]: row["content_id"]
            for row in artifact["prior_observation_set"]["observations"]
        }
        members = sorted(
            (
                {
                    "content_id": content_by_attempt[member["member_id"]],
                    "b_fiducial_s": member["b_fiducial_s"],
                }
                for member in artifact["derivation_corpus"]["members"]
            ),
            key=lambda member: member["content_id"],
        )
        derived = bracketing.derive_successor_decimal_derivation(members)
        stats = derived["source_statistics"]
        operatives = derived["ratified_operatives"]
        self.assertEqual(stats["prediction_95_two_draw_s"], "0.008826584887500731")
        self.assertEqual(stats["prediction_99_two_draw_s"], "0.012093166090698986")
        self.assertEqual(operatives["bracket_screen_s"], "0.010818")
        self.assertEqual(operatives["preflight_level_screen_s"], "0.033558756679900")
        self.assertEqual(
            operatives["maximum_budgetable_drift_s"],
            "0.012093166090698986",
        )
        self.assertEqual(
            operatives["max_budgetable_excess_s"],
            "0.001275166090698986",
        )
        self.assertFalse(
            derived["quantile_method"]["d102_df18_compatibility_pin"]
        )

    def test_preflight_screen_equals_half_even_quantized_observed_maximum(self) -> None:
        members = [
            {
                "content_id": f"{index:064x}",
                "b_fiducial_s": (
                    "0.0000000000000000"
                    if index <= 9
                    else "0.0000000000000005"
                ),
            }
            for index in range(1, 20)
        ]
        derived = bracketing.derive_successor_decimal_derivation(members)
        self.assertEqual(
            derived["ratified_operatives"]["bracket_screen_s"],
            "0.010818",
        )
        self.assertEqual(
            derived["rounding"]["preflight_level_screen"]["source_rule"],
            bracketing.SUCCESSOR_PREFLIGHT_SCREEN_RULE,
        )
        self.assertGreater(
            Decimal(derived["source_statistics"]["prediction_95_two_draw_s"]),
            Decimal(derived["source_statistics"]["maximum_s"]),
        )
        self.assertEqual(
            derived["ratified_operatives"]["preflight_level_screen_s"],
            "0.000000000000000",
        )

    def test_negative_nonfinite_and_binary_float_inputs_refuse(self) -> None:
        for invalid in ("-0.1", "NaN", "Infinity", 0.1):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    bracketing.derive_successor_decimal_derivation(
                        [
                            {"content_id": "1" * 64, "b_fiducial_s": invalid},
                            {"content_id": "2" * 64, "b_fiducial_s": "0.2"},
                        ]
                    )

    def test_quantile_algorithm_and_d102_pin_are_stable(self) -> None:
        self.assertEqual(
            bracketing.SUCCESSOR_QUANTILE_METHOD,
            "decimal_incomplete_beta_bisection_v1",
        )
        self.assertEqual(
            bracketing.decimal_student_t_quantile("0.995", 18),
            Decimal(
                "2.8784404727135853941939366597008136821841052811738896572381901955286218320347263"
            ),
        )
        bypassed = bracketing.decimal_student_t_quantile(
            "0.995", 18, use_compatibility_pin=False
        )
        self.assertLess(
            abs(
                bypassed
                - Decimal(
                    "2.8784404727386081178058787265646316079030323608869115266837277466388674896049174"
                )
            ),
            Decimal("1e-60"),
        )

    def test_nonpinned_df37_matches_checked_in_independent_reference(self) -> None:
        self.assertLess(
            abs(
                bracketing.decimal_student_t_quantile(
                    "0.995", 37, use_compatibility_pin=False
                )
                - Decimal(
                    "2.71540872154998830130830201963737496013944012008966094097330087289823817193540197518371053830804074116858911770212594477"
                )
            ),
            Decimal("1e-60"),
        )

    def test_quantile_continued_fraction_nonconvergence_is_governed(self) -> None:
        with patch.object(
            bracketing, "SUCCESSOR_CONTINUED_FRACTION_MAX_ITERATIONS", 0
        ):
            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceNumericalRefusal,
                "successor_quantile_continued_fraction_nonconvergence",
            ):
                bracketing.decimal_student_t_quantile(
                    "0.995", 17, use_compatibility_pin=False
                )

    def test_ratified_minimum_refuses_derivation_basis_below_19(self) -> None:
        with self.assertRaisesRegex(
            ValueError, "successor_derivation_basis_below_minimum_19"
        ):
            bracketing.derive_successor_decimal_derivation(
                [
                    {"content_id": "1" * 64, "b_fiducial_s": "0"},
                    {"content_id": "2" * 64, "b_fiducial_s": "0.1"},
                ]
            )

    def test_current_n30_worked_candidates_remain_below_inherited_envelope(self) -> None:
        with bracketing.localcontext() as context:
            context.prec = 100
            root_two = Decimal(2).sqrt()
            sample_sd = Decimal("0.011489826907224958") / (
                bracketing.decimal_student_t_quantile(
                    "0.995", 29, use_compatibility_pin=False
                )
                * root_two
            )
            high = (
                Decimal(2)
                * sample_sd
                * (Decimal(29) / Decimal(30)).sqrt()
            )
        members = [
            {
                "content_id": f"{index:064x}",
                "b_fiducial_s": str(Decimal(0) if index <= 15 else high),
            }
            for index in range(1, 31)
        ]
        derived = bracketing.derive_successor_decimal_derivation(members)
        self.assertEqual(
            derived["source_statistics"]["prediction_95_two_draw_s"],
            "0.008525415306447831",
        )
        self.assertEqual(
            derived["source_statistics"]["prediction_99_two_draw_s"],
            "0.011489826907224958",
        )
        self.assertEqual(
            derived["ratified_operatives"]["bracket_screen_s"],
            "0.010818",
        )
        self.assertEqual(
            derived["ratified_operatives"]["maximum_budgetable_drift_s"],
            "0.012093166090593858",
        )

    def test_degraded_n30_worked_arithmetic_grows_both_envelopes(self) -> None:
        with bracketing.localcontext() as context:
            context.prec = bracketing.SUCCESSOR_DECIMAL_PRECISION
            half_span = Decimal("0.004") * (Decimal(29) / Decimal(30)).sqrt()
            high = Decimal(2) * half_span
        members = [
            {
                "content_id": f"{index:064x}",
                "b_fiducial_s": str(Decimal(0) if index <= 15 else high),
            }
            for index in range(1, 31)
        ]
        derived = bracketing.derive_successor_decimal_derivation(members)
        self.assertEqual(
            derived["source_statistics"]["sample_sd_s"],
            "0.004000000000000000",
        )
        self.assertEqual(
            derived["source_statistics"]["prediction_95_two_draw_s"],
            "0.011569565992286168",
        )
        self.assertEqual(
            derived["source_statistics"]["prediction_99_two_draw_s"],
            "0.015592473312419959",
        )
        self.assertEqual(
            derived["ratified_operatives"]["bracket_screen_s"],
            "0.011569565992286168",
        )
        self.assertEqual(
            derived["ratified_operatives"]["maximum_budgetable_drift_s"],
            "0.015592473312419959",
        )

    def test_zero_variance_inherits_strictly_ordered_parent_envelope(self) -> None:
        members = [
            {"content_id": f"{index:064x}", "b_fiducial_s": "0.025"}
            for index in range(1, 20)
        ]
        operatives = bracketing.derive_successor_decimal_derivation(members)[
            "ratified_operatives"
        ]
        self.assertEqual(operatives["bracket_screen_s"], "0.010818")
        self.assertEqual(
            operatives["maximum_budgetable_drift_s"],
            "0.012093166090593858",
        )
        self.assertEqual(
            operatives["max_budgetable_excess_s"],
            "0.001275166090593858",
        )

    def test_screen_ceiling_crossing_refuses_instead_of_clamping_cap(self) -> None:
        members = [
            {
                "content_id": f"{index:064x}",
                "b_fiducial_s": "0" if index <= 9 else "1",
            }
            for index in range(1, 20)
        ]
        with patch.object(
            bracketing,
            "decimal_student_t_quantile",
            return_value=Decimal("3"),
        ):
            with self.assertRaisesRegex(
                ValueError, "^successor_screen_exceeds_budget_ceiling$"
            ):
                bracketing.derive_successor_decimal_derivation(members)

    def test_screen_strictly_above_ceiling_refuses_without_clamping(self) -> None:
        members = [
            {
                "content_id": f"{index:064x}",
                "b_fiducial_s": "0" if index <= 9 else "1",
            }
            for index in range(1, 20)
        ]

        def reversed_quantiles(probability: str, *_args, **_kwargs) -> Decimal:
            return Decimal("4" if probability == "0.975" else "3")

        with patch.object(
            bracketing,
            "decimal_student_t_quantile",
            side_effect=reversed_quantiles,
        ):
            with self.assertRaisesRegex(
                ValueError, "^successor_screen_exceeds_budget_ceiling$"
            ):
                bracketing.derive_successor_decimal_derivation(members)


class SuccessorBuilderTests(unittest.TestCase):
    def test_actual_30_trigger_inventory_retains_n19_basis_and_excludes_window_b(self) -> None:
        parent = _parent_artifact()
        grouped_result = bracketing._group_probe_observations(
            bracketing._probe_observation_universe(_snapshot())
        )
        self.assertIsNotNone(grouped_result)
        grouped, _noncontent = grouped_result
        basis_ids = successor._successor_derivation_basis_ids(
            parent,
            grouped,
            parent_new_ids=set(),
            active_epoch=parent["identity_epoch"],
        )
        trigger_ids = {
            content_id
            for content_id, aliases in grouped.items()
            if aliases[0].classification_disposition == "valid"
            and dict(aliases[0].identity_epoch) == parent["identity_epoch"]
        }
        window_b_attempts = {
            "20260726T031222-e0ce33f5",
            "20260801T014059-8c3bfe9e",
        }
        content_by_attempt = {
            row["attempt_id"]: row["content_id"]
            for row in parent["prior_observation_set"]["observations"]
        }
        self.assertEqual(len(trigger_ids), 30)
        self.assertEqual(len(basis_ids), 19)
        expected_basis_ids = {
            content_by_attempt[member["member_id"]]
            for member in parent["derivation_corpus"]["members"]
        }
        self.assertEqual(basis_ids, expected_basis_ids)
        self.assertTrue(
            {content_by_attempt[attempt] for attempt in window_b_attempts}
            .isdisjoint(basis_ids)
        )

    def test_first_range_successor_keeps_full_inventory_but_derives_n20(self) -> None:
        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
        build = successor.build_calibration_acceptance_successor(
            snapshot,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(build.artifact["derivation_corpus"]["n"], 20)
        count_trigger = build.artifact["prospective_rederivation"]["count_trigger"]
        self.assertEqual(count_trigger["source_trigger_count"], 31)
        self.assertEqual(count_trigger["next_boundary"], 38)
        self.assertEqual(
            count_trigger["universe_rule"],
            bracketing.SUCCESSOR_TRIGGER_UNIVERSE_RULE,
        )
        self.assertEqual(
            build.artifact["derivation_corpus"]["selection"],
            bracketing.SUCCESSOR_DERIVATION_BASIS_RULE,
        )
        self.assertEqual(
            len(build.artifact["prior_observation_set"]["observations"]),
            39,
        )
        self.assertTrue(
            all(
                "disposing_decision_id" in row
                and row["disposing_decision_id"] is None
                for row in build.artifact["prior_observation_set"]["observations"]
            )
        )
        self.assertEqual(
            build.artifact["decision_ids"],
            ["D-102", "D-109", "D-117", "D-125", "D-126"],
        )
        self.assertNotIn("COLD-GATE-U2-PENDING", build.artifact["decision_ids"])
        self.assertTrue(
            bracketing._valid_acceptance_bound(
                build.artifact,
                parent=_parent_artifact(),
                parent_artifact_sha256=build.registry["entries"][0][
                    "artifact_sha256"
                ],
            )
        )
        self.assertEqual(build.successor_probe["outcome"], "accepted_under_active_artifact")
        self.assertEqual(build.successor_probe["refusal_reasons"], [])
        self.assertNotIn("parent_judgment_policy", build.successor_probe)
        self.assertEqual(build.artifact["lineage"]["parent_acceptance_id"], "d079_calibration_acceptance_v2_n19")
        self.assertIn(
            _new_observation(0).content_id,
            build.artifact["lineage"]["trigger_judgment"]["new_content_ids"],
        )

    def test_absorbed_basis_additions_must_equal_parent_judgment(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0, bound="0.02"),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        tampered = json.loads(json.dumps(build.artifact))
        tampered["lineage"]["trigger_judgment"]["new_content_ids"] = []
        tampered["derivation_sha256"] = bracketing._canonical_sha256(
            {
                key: value
                for key, value in tampered.items()
                if key != "derivation_sha256"
            }
        )
        tampered_bytes = successor._pretty_json_bytes(tampered)
        registry = json.loads(json.dumps(build.registry))
        active = next(entry for entry in registry["entries"] if entry["active"])
        active["artifact_sha256"] = hashlib.sha256(tampered_bytes).hexdigest()
        active["derivation_sha256"] = tampered["derivation_sha256"]
        self.assertFalse(
            bracketing._valid_acceptance_bound(
                tampered,
                parent=_parent_artifact(),
                parent_artifact_sha256=build.registry["entries"][0][
                    "artifact_sha256"
                ],
            )
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for entry in registry["entries"]:
                destination = root / entry["artifact_path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(
                    tampered_bytes
                    if entry["acceptance_id"] == tampered["acceptance_id"]
                    else (REPO_ROOT / entry["artifact_path"]).read_bytes()
                )
            registry_path = (
                root / "configs/calibration/calibration_acceptance_registry.json"
            )
            registry_path.write_bytes(successor._pretty_json_bytes(registry))
            with patch.object(bracketing, "_valid_acceptance_bound", return_value=True):
                with self.assertRaisesRegex(
                    bracketing.CalibrationAcceptanceRegistryRefusal,
                    "acceptance_registry_derivation_basis_invalid",
                ):
                    bracketing.load_calibration_acceptance_registry(
                        registry_path, repo_root=root, require_committed=False
                    )

    def test_generation_two_artifact_records_boundary_38(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0, bound="0.02"),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(build.artifact["lineage"]["generation"], 2)
        self.assertEqual(bracketing._artifact_count_boundary(build.artifact), 38)

    def test_trigger_count_is_not_derived_from_a_fixed_nonbasis_gap(self) -> None:
        parent = _parent_artifact()
        parent_basis = {
            member["member_id"] for member in parent["derivation_corpus"]["members"]
        }
        demoted = next(
            row
            for row in parent["prior_observation_set"]["observations"]
            if row["disposition"] == "valid" and row["attempt_id"] not in parent_basis
        )
        demoted["disposition"] = "ordinary-invalid"
        parent["backfill_candidate"]["candidate_inventory"]["valid"] -= 1
        parent["backfill_candidate"]["candidate_inventory"][
            "ordinary-invalid"
        ] += 1
        parent["derivation_sha256"] = bracketing._canonical_sha256(
            {
                key: value
                for key, value in parent.items()
                if key != "derivation_sha256"
            }
        )
        parent_bytes = successor._pretty_json_bytes(parent)
        registry = json.loads(REGISTRY_PATH.read_bytes())
        registry["entries"][0]["artifact_sha256"] = hashlib.sha256(
            parent_bytes
        ).hexdigest()
        registry["entries"][0]["derivation_sha256"] = parent["derivation_sha256"]
        observations = [
            replace(observation, disposition="ordinary-invalid")
            if observation.attempt_id == demoted["attempt_id"]
            else observation
            for observation in _parent_observations()
        ]
        base = _snapshot((_new_observation(0, bound="0.02"),))
        snapshot = replace(
            base,
            observations=tuple(observations) + (base.observations[-1],),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent_path = root / registry["entries"][0]["artifact_path"]
            parent_path.parent.mkdir(parents=True)
            parent_path.write_bytes(parent_bytes)
            registry_path = parent_path.parent / REGISTRY_PATH.name
            registry_path.write_bytes(successor._pretty_json_bytes(registry))
            build = successor.build_calibration_acceptance_successor(
                snapshot,
                observed_identity_epoch=parent["identity_epoch"],
                registry_path=registry_path,
                repo_root=root,
                require_committed_registry=False,
                verify_custody=False,
            )
        trigger_count = build.artifact["prospective_rederivation"]["count_trigger"][
            "source_trigger_count"
        ]
        derivation_count = build.artifact["derivation_corpus"]["n"]
        self.assertEqual(trigger_count - derivation_count, 10)

    def test_builder_uses_loaded_real_reservation_finalization_cadence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "runs/calibration_observation_ledger.jsonl"
            pin = root / "configs/calibration/calibration_ledger_head.json"
            plan = _real_import_plan(ledger, pin)
            epoch = dict(_parent_artifact()["identity_epoch"])
            t1 = dict(plan.receipts[-1]["t1_bindings"])
            reservation_sequence = plan.final_sequence + 1
            finalization_sequence = reservation_sequence + 1
            artifacts = {
                "manifest.json": _digest("real-cadence-manifest"),
                "instrument_evidence.json": _digest("real-cadence-evidence"),
            }
            reservation = _receipt(
                schema_version=RECEIPT_SCHEMA,
                ledger_schema=LEDGER_SCHEMA,
                sequence=reservation_sequence,
                predecessor_digest=plan.head_digest,
                event="reservation",
                attempt_id="real-cadence-live",
                content_id=None,
                artifact_sha256={},
                identity_epoch=epoch,
                t1_bindings=t1,
                capture_wall_time_s=None,
                exact_bound_lexeme_s=None,
                disposition="pending",
                custody_locator="/authenticated/real-cadence-live",
            )
            finalization = _receipt(
                schema_version=RECEIPT_SCHEMA,
                ledger_schema=LEDGER_SCHEMA,
                sequence=finalization_sequence,
                predecessor_digest=reservation["receipt_digest"],
                event="finalization",
                attempt_id="real-cadence-live",
                content_id=content_id_from_artifact_hashes(artifacts),
                artifact_sha256=artifacts,
                identity_epoch=epoch,
                t1_bindings=t1,
                capture_wall_time_s="1000",
                exact_bound_lexeme_s="0.0200000000000000001",
                disposition="valid",
                custody_locator="/authenticated/real-cadence-live",
            )
            ledger.parent.mkdir(parents=True)
            encoded = lambda row: (
                json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            ).encode("utf-8")
            ledger.write_bytes(
                plan.ledger_bytes + encoded(reservation) + encoded(finalization)
            )
            pin.write_bytes(
                successor._pretty_json_bytes(
                    {
                        "sequence": finalization_sequence,
                        "head_digest": finalization["receipt_digest"],
                        "ledger_schema": LEDGER_SCHEMA,
                    }
                )
            )
            snapshot = load_calibration_ledger_snapshot(
                ledger,
                pin,
                baseline_sequence=76,
                baseline_digest=plan.head_digest,
                require_committed_pin=False,
                verify_custody=False,
                repo_root=root,
            )
            self.assertEqual(snapshot.refusal_reasons, ())
            build = successor.build_calibration_acceptance_successor(
                snapshot,
                observed_identity_epoch=epoch,
                require_committed_registry=False,
                verify_custody=False,
            )
        self.assertEqual(
            build.artifact["ledger_cutoff"]["sequence"], finalization_sequence
        )
        self.assertEqual(build.head_pin["sequence"], finalization_sequence)
        self.assertIn(
            f"_s{finalization_sequence}_", f"_{build.artifact['acceptance_id']}_"
        )
        new_content_id = content_id_from_artifact_hashes(artifacts)
        member = next(
            row
            for row in build.artifact["derivation_corpus"]["members"]
            if row["content_id"] == new_content_id
        )
        self.assertEqual(member["finalization_sequence"], finalization_sequence)

    def test_repeated_and_shuffled_builds_are_byte_identical(self) -> None:
        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
        first = successor.build_calibration_acceptance_successor(
            snapshot,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        shuffled = replace(snapshot, observations=tuple(reversed(snapshot.observations)))
        second = successor.build_calibration_acceptance_successor(
            shuffled,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(first.artifact_bytes, second.artifact_bytes)
        self.assertEqual(first.registry_bytes, second.registry_bytes)
        self.assertEqual(first.head_pin, second.head_pin)

    def test_38_trigger_progression_derives_n27_and_advances_to_76(self) -> None:
        extras = tuple(_new_observation(index, bound="0.0271") for index in range(8))
        build = successor.build_calibration_acceptance_successor(
            _snapshot(extras),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(build.artifact["derivation_corpus"]["n"], 27)
        count_trigger = build.artifact["prospective_rederivation"]["count_trigger"]
        self.assertEqual(count_trigger["source_trigger_count"], 38)
        self.assertEqual(count_trigger["next_boundary"], 76)

    def test_supported_successor_boundary_rules_all_have_recompute_branches(self) -> None:
        successor_rules = (
            bracketing._SUPPORTED_COUNT_BOUNDARY_RULES
            - {bracketing.GENESIS_COUNT_BOUNDARY_RULE}
        )
        self.assertTrue(successor_rules)
        for rule in successor_rules:
            with self.subTest(rule=rule):
                self.assertEqual(
                    bracketing._next_count_boundary(
                        parent_boundary=38,
                        trigger_count=38,
                        rule=rule,
                    ),
                    76,
                )

    def test_ancestor_boundary_rule_is_validated_from_its_entry(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0, bound="0.02"),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for entry in build.registry["entries"]:
                destination = root / entry["artifact_path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(
                    build.artifact_bytes
                    if entry["acceptance_id"] == build.artifact["acceptance_id"]
                    else (REPO_ROOT / entry["artifact_path"]).read_bytes()
                )
            registry = root / "configs/calibration/calibration_acceptance_registry.json"
            registry.write_bytes(build.registry_bytes)
            with patch.object(
                bracketing,
                "SUCCESSOR_COUNT_BOUNDARY_RULE",
                "future_rule_not_applied_to_ancestors",
            ):
                loaded = bracketing.load_calibration_acceptance_registry(
                    registry, repo_root=root, require_committed=False
                )
            self.assertEqual(
                loaded["entries"][0]["count_boundary_rule"],
                bracketing.GENESIS_COUNT_BOUNDARY_RULE,
            )

    def test_systematic_and_unresolved_never_build(self) -> None:
        cases = (
            _snapshot((_new_observation(0, disposition="systematic-invalid"),)),
            _snapshot((replace(_new_observation(0, disposition="abandoned"), content_id=None, artifact_sha256={}, exact_bound_lexeme_s=None),)),
        )
        for snapshot in cases:
            with self.subTest(head=snapshot.head_digest):
                with self.assertRaisesRegex(ValueError, "does not require a successor"):
                    successor.build_calibration_acceptance_successor(
                        snapshot,
                        observed_identity_epoch=_parent_artifact()["identity_epoch"],
                        require_committed_registry=False,
                        verify_custody=False,
                    )

    def test_no_content_closure_does_not_brick_range_successor(self) -> None:
        abandoned = replace(
            _new_observation(0, disposition="abandoned"),
            content_id=None,
            artifact_sha256={},
            exact_bound_lexeme_s=None,
        )
        build = successor.build_calibration_acceptance_successor(
            _snapshot((abandoned, _new_observation(1, bound="0.02"))),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(
            build.artifact["prior_observation_set"]["noncontent_attempts"],
            [
                {
                    "attempt_id": abandoned.attempt_id,
                    "closure_sequence": abandoned.sequence,
                    "receipt_digest": abandoned.receipt_digest,
                    "disposition": "abandoned",
                    "custody_locator": abandoned.custody_locator,
                }
            ],
        )
        self.assertEqual(
            build.successor_probe["outcome"], "accepted_under_active_artifact"
        )

    def test_real_successor_probe_rejection_blocks_build(self) -> None:
        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
        parent_probe = _probe(snapshot)
        rejected = {
            "outcome": "authentication_or_epoch_refusal",
            "refusal_reasons": ["synthetic_real_probe_rejection"],
        }
        with patch.object(
            successor,
            "probe_calibration_acceptance_trigger",
            side_effect=(parent_probe, rejected),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "successor_real_probe_refused:authentication_or_epoch_refusal",
            ):
                successor.build_calibration_acceptance_successor(
                    snapshot,
                    observed_identity_epoch=_parent_artifact()["identity_epoch"],
                    require_committed_registry=False,
                    verify_custody=False,
                )

    def test_nonterminal_or_uncommitted_head_refuses(self) -> None:
        snapshot = _snapshot((_new_observation(0),))
        for changed in (
            replace(snapshot, committed_head_digest="0" * 64),
            replace(snapshot, refusal_reasons=("calibration_ledger_pending",)),
            replace(snapshot, receipts=(*snapshot.receipts[:-1], {**snapshot.receipts[-1], "event": "reservation"})),
        ):
            with self.subTest(changed=changed.refusal_reasons):
                with self.assertRaisesRegex(ValueError, "committed terminal"):
                    successor.build_calibration_acceptance_successor(
                        changed,
                        observed_identity_epoch=_parent_artifact()["identity_epoch"],
                        require_committed_registry=False,
                        verify_custody=False,
                    )

    def test_failed_publication_precondition_mutates_neither_destination(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry, _ = _init_publication_repo(root)
            artifact = root / build.artifact_path
            artifact.write_text("occupied", encoding="utf-8")
            before = registry.read_bytes()
            with self.assertRaises(ValueError):
                successor.publish_successor(
                    build,
                    artifact_destination=artifact,
                    registry_destination=registry,
                    expected_registry_bytes=before,
                    repo_root=root,
                )
            self.assertEqual(artifact.read_text(encoding="utf-8"), "occupied")
            self.assertEqual(registry.read_bytes(), before)

    def test_faults_before_ref_advance_restore_prior_authority(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        original_replace = os.replace
        original_run = subprocess.run
        cases = (
            "after_artifact_replace",
            "after_registry_replace",
            "before_commit_tree",
            "after_commit_tree",
            "before_update_ref",
        )
        for fault in cases:
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                registry, _ = _init_publication_repo(root)
                artifact = root / build.artifact_path
                old_registry_bytes = registry.read_bytes()
                old_head = original_run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                replace_count = 0

                def injected_replace(source, destination):
                    nonlocal replace_count
                    original_replace(source, destination)
                    replace_count += 1
                    if (
                        fault == "after_artifact_replace"
                        and Path(destination).resolve(strict=False)
                        == artifact.resolve(strict=False)
                    ) or (
                        fault == "after_registry_replace"
                        and Path(destination).resolve(strict=False)
                        == registry.resolve(strict=False)
                    ):
                        raise OSError(fault)

                def injected_run(command, *args, **kwargs):
                    operation = command[1] if len(command) > 1 else ""
                    if fault == "before_commit_tree" and operation == "commit-tree":
                        raise subprocess.CalledProcessError(1, command)
                    if fault == "before_update_ref" and operation == "update-ref":
                        raise subprocess.CalledProcessError(1, command)
                    completed = original_run(command, *args, **kwargs)
                    if fault == "after_commit_tree" and operation == "commit-tree":
                        raise subprocess.CalledProcessError(1, command)
                    return completed

                with patch.object(successor.os, "replace", side_effect=injected_replace), patch.object(
                    successor.subprocess, "run", side_effect=injected_run
                ):
                    with self.assertRaises((OSError, ValueError)):
                        successor.publish_successor(
                            build,
                            artifact_destination=artifact,
                            registry_destination=registry,
                            expected_registry_bytes=old_registry_bytes,
                            repo_root=root,
                        )
                self.assertGreaterEqual(replace_count, 1)
                self.assertEqual(registry.read_bytes(), old_registry_bytes)
                self.assertFalse(artifact.exists())
                self.assertEqual(
                    original_run(
                        ["git", "rev-parse", "HEAD"],
                        cwd=root,
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.strip(),
                    old_head,
                )
                loaded = bracketing.load_calibration_acceptance_registry(
                    registry, repo_root=root, require_committed=True
                )
                self.assertEqual(
                    bracketing._active_registry_entry(loaded)["acceptance_id"],
                    "d079_calibration_acceptance_v2_n19",
                )

    def test_failed_publication_preserves_identical_prepublished_artifact(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        original_replace = os.replace
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry, _ = _init_publication_repo(root)
            artifact = root / build.artifact_path
            artifact.write_bytes(build.artifact_bytes)
            old_registry_bytes = registry.read_bytes()

            def fail_after_registry(source, destination):
                original_replace(source, destination)
                if Path(destination).resolve(strict=False) == registry.resolve(
                    strict=False
                ):
                    raise OSError("after_registry_replace")

            with patch.object(
                successor.os, "replace", side_effect=fail_after_registry
            ):
                with self.assertRaises(OSError):
                    successor.publish_successor(
                        build,
                        artifact_destination=artifact,
                        registry_destination=registry,
                        expected_registry_bytes=old_registry_bytes,
                        repo_root=root,
                    )
            self.assertEqual(registry.read_bytes(), old_registry_bytes)
            self.assertEqual(artifact.read_bytes(), build.artifact_bytes)
            loaded = bracketing.load_calibration_acceptance_registry(
                registry, repo_root=root, require_committed=True
            )
            self.assertEqual(
                bracketing._active_registry_entry(loaded)["acceptance_id"],
                "d079_calibration_acceptance_v2_n19",
            )

    def test_publication_fsyncs_both_stage_files_and_both_directory_mutations(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        original_fsync = os.fsync
        original_replace = os.replace
        sync_kinds: list[str] = []
        events: list[tuple[str, str, str | None]] = []

        def observed_fsync(descriptor: int) -> None:
            mode = os.fstat(descriptor).st_mode
            kind = "directory" if stat.S_ISDIR(mode) else "file"
            sync_kinds.append(kind)
            try:
                descriptor_path = (
                    fcntl.fcntl(
                        descriptor, fcntl.F_GETPATH, b"\0" * 1024
                    )
                    .split(b"\0", 1)[0]
                    .decode("utf-8")
                )
            except OSError:
                descriptor_path = None
            events.append(("fsync", kind, descriptor_path))
            original_fsync(descriptor)

        def observed_replace(source: Path, destination: Path) -> None:
            events.append(("replace", str(Path(source)), str(Path(destination))))
            original_replace(source, destination)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry, _ = _init_publication_repo(root)
            artifact = root / build.artifact_path
            with patch.object(
                successor.os, "fsync", side_effect=observed_fsync
            ), patch.object(successor.os, "replace", side_effect=observed_replace):
                successor.publish_successor(
                    build,
                    artifact_destination=artifact,
                    registry_destination=registry,
                    expected_registry_bytes=registry.read_bytes(),
                    repo_root=root,
                )
        self.assertEqual(sync_kinds.count("file"), 2)
        self.assertEqual(sync_kinds.count("directory"), 2)
        replace_events = [
            (index, source, destination)
            for index, (kind, source, destination) in enumerate(events)
            if kind == "replace"
        ]
        self.assertEqual(len(replace_events), 2)
        for replace_index, source, destination in replace_events:
            staged_syncs = [
                index
                for index, event in enumerate(events)
                if event == ("fsync", "file", source)
            ]
            destination_dir_syncs = [
                index
                for index, event in enumerate(events)
                if event
                == ("fsync", "directory", str(Path(destination).parent))
            ]
            self.assertTrue(staged_syncs)
            self.assertTrue(destination_dir_syncs)
            self.assertLess(max(staged_syncs), replace_index)
            self.assertLess(
                replace_index,
                min(index for index in destination_dir_syncs if index > replace_index),
            )

    def test_post_update_ref_verification_failure_keeps_successor_authoritative(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry, _ = _init_publication_repo(root)
            artifact = root / build.artifact_path
            old_head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            with patch.object(
                successor,
                "load_calibration_acceptance_registry",
                side_effect=ValueError("verification fault"),
            ):
                with self.assertRaises(successor.SuccessorDurabilityUncertain):
                    successor.publish_successor(
                        build,
                        artifact_destination=artifact,
                        registry_destination=registry,
                        expected_registry_bytes=registry.read_bytes(),
                        repo_root=root,
                    )
            new_head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertNotEqual(new_head, old_head)
            self.assertEqual(registry.read_bytes(), build.registry_bytes)
            self.assertEqual(artifact.read_bytes(), build.artifact_bytes)
            loaded = bracketing.load_calibration_acceptance_registry(
                registry, repo_root=root, require_committed=True
            )
            self.assertEqual(
                bracketing._active_registry_entry(loaded)["acceptance_id"],
                build.artifact["acceptance_id"],
            )

    def test_cli_returns_3_for_post_commit_durability_uncertainty(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.json"
            observed = root / "observed.json"
            registry.write_bytes(REGISTRY_PATH.read_bytes())
            observed.write_text(
                json.dumps(_parent_artifact()["identity_epoch"]), encoding="utf-8"
            )
            args = SimpleNamespace(
                ledger=root / "ledger.jsonl",
                head_pin=root / "pin.json",
                registry=registry,
                repo_root=root,
                observed_identity=observed,
                issue=True,
                artifact_out=root / build.artifact_path,
                registry_out=registry,
            )
            parser = SimpleNamespace(parse_args=lambda _argv: args)
            stderr = io.StringIO()
            with patch.object(successor, "_parser", return_value=parser), patch.object(
                successor, "load_calibration_acceptance_registry", return_value=build.registry
            ), patch.object(
                successor,
                "_load_parent_artifact",
                return_value=(build.registry["entries"][0], _parent_artifact()),
            ), patch.object(
                successor, "load_calibration_ledger_snapshot", return_value=_snapshot()
            ), patch.object(
                successor, "build_calibration_acceptance_successor", return_value=build
            ), patch.object(
                successor,
                "publish_successor",
                side_effect=successor.SuccessorDurabilityUncertain("post-commit"),
            ), redirect_stderr(stderr):
                self.assertEqual(successor.main([]), 3)
            self.assertIn("committed_durability_uncertain", stderr.getvalue())

    def test_publication_co_lands_both_paths_and_verifies_committed_mode(self) -> None:
        build = successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        for prepublish_artifact in (False, True):
            with self.subTest(prepublish_artifact=prepublish_artifact):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    registry, _ = _init_publication_repo(root)
                    artifact = root / build.artifact_path
                    if prepublish_artifact:
                        artifact.write_bytes(build.artifact_bytes)
                    before = registry.read_bytes()
                    verification = successor.publish_successor(
                        build,
                        artifact_destination=artifact,
                        registry_destination=registry,
                        expected_registry_bytes=before,
                        repo_root=root,
                    )
                    self.assertEqual(artifact.read_bytes(), build.artifact_bytes)
                    self.assertEqual(registry.read_bytes(), build.registry_bytes)
                    self.assertTrue(verification["committed_mode_verified"])
                    committed_paths = subprocess.run(
                        [
                            "git",
                            "diff-tree",
                            "--no-commit-id",
                            "--name-only",
                            "-r",
                            "HEAD",
                        ],
                        cwd=root,
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.splitlines()
                    self.assertEqual(
                        set(committed_paths),
                        {
                            build.artifact_path,
                            "configs/calibration/calibration_acceptance_registry.json",
                        },
                    )
                    loaded = bracketing.load_calibration_acceptance_registry(
                        registry, repo_root=root, require_committed=True
                    )
                    self.assertIsNotNone(loaded)
                    self.assertEqual(
                        bracketing._active_registry_entry(loaded)["acceptance_id"],
                        build.artifact["acceptance_id"],
                    )

    def test_uncommitted_registry_replacement_names_missing_commit_everywhere(self) -> None:
        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
        build = successor.build_calibration_acceptance_successor(
            snapshot,
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry, _ = _init_publication_repo(root)
            artifact = root / build.artifact_path
            artifact.write_bytes(build.artifact_bytes)
            registry.write_bytes(build.registry_bytes)

            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceRegistryRefusal,
                "acceptance_registry_missing_commit",
            ):
                bracketing.load_calibration_acceptance_registry(
                    registry, repo_root=root, require_committed=True
                )
            probe = bracketing.probe_calibration_acceptance_trigger(
                snapshot,
                observed_identity_epoch=_parent_artifact()["identity_epoch"],
                registry_path=registry,
                repo_root=root,
                require_committed_registry=True,
                verify_custody=False,
            )
            self.assertEqual(
                probe["refusal_reasons"], ["acceptance_registry_missing_commit"]
            )
            with self.assertRaisesRegex(
                bracketing.CalibrationAcceptanceRegistryRefusal,
                "acceptance_registry_missing_commit",
            ):
                successor.build_calibration_acceptance_successor(
                    snapshot,
                    observed_identity_epoch=_parent_artifact()["identity_epoch"],
                    registry_path=registry,
                    repo_root=root,
                    require_committed_registry=True,
                    verify_custody=False,
                )

    def test_dry_run_build_writes_nothing(self) -> None:
        before = {path: path.read_bytes() for path in (ACCEPTANCE_PATH, REGISTRY_PATH)}
        successor.build_calibration_acceptance_successor(
            _snapshot((_new_observation(0),)),
            observed_identity_epoch=_parent_artifact()["identity_epoch"],
            require_committed_registry=False,
            verify_custody=False,
        )
        self.assertEqual(before, {path: path.read_bytes() for path in before})


if __name__ == "__main__":
    unittest.main()
