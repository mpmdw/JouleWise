"""Defect-shaped whole-window selection-consumption regressions."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import joulewise.whole_window as whole_window_module

from joulewise.whole_window import (
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
    AuthenticatedConsumptionSession,
    CONDITION_NEG8_DRIFT_BOUND_STALE,
    CONDITION_NEG8_DRIFT_BOUND_UNDERIVED,
    CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED,
    CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED,
    CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED,
    NEG8_POINT_DRIFT_ESTIMAND,
    NEG8_POINT_DRIFT_CONDITION_CODES,
    _current_core_rederivation_reasons,
    _current_strict_summary,
    _consumption_provenance_valid,
    _derived_neg8_decision,
    _validate_row,
    build_evaluation_basis,
    build_neg8_drift_bound_artifact,
    canonical_sha256,
    custody_telemetry_identity,
    mint_neg8_drift_bound_artifact,
    validated_attempt_selection,
    whole_window_drift_allowances,
    whole_window_refusal_reasons,
)
from joulewise.analysis_engine.claims import REDUCER_REASON_CODES
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    append_pending_receipt,
    artifact_hashes as calibration_artifact_hashes,
    finalize_attempt_receipt,
    head_pin_for_receipt,
    load_calibration_ledger_snapshot,
)
from joulewise.floor_extraction import (
    ANCHOR_FALLBACK_MEMBER_REFUSAL,
    CELL_REFUSAL_CODES,
)
from joulewise.analysis_engine.registry import (
    normalized_json_bytes,
    render_dispatch_receipt,
    sha256_bytes,
)
from joulewise.schemas import CalibrationBracketingPolicy
from tests.test_axi_analysis_manifest import AXI_VALID_BUNDLE, evidence_for
from tests.test_run_campaign import (
    d100_real_salvage_leaf_patches,
    install_real_salvage_window,
    read_all_jsonl,
    run_campaign_module,
)


class WholeWindowSelectionTests(unittest.TestCase):
    @staticmethod
    def _bounded_clause(decision_log: str, marker: str) -> str:
        _, clause = decision_log.split(marker, 1)
        boundaries = [
            index
            for boundary in ("\n### ", "\n   **Clause-")
            if (index := clause.find(boundary)) >= 0
        ]
        return clause[: min(boundaries)] if boundaries else clause

    def test_screen_budget_refusals_are_bidirectionally_registered(self):
        decision_log = Path("docs/decision_log.md").read_text(encoding="utf-8")
        addendum_2_marker = (
            "**Clause-10 addendum 2 — screen+budget wave registry"
        )
        addendum_3_marker = "**Clause-10 addendum 3 — terminal mock bar"
        self.assertIn(addendum_2_marker, decision_log)
        self.assertIn(addendum_3_marker, decision_log)
        addendum_2 = self._bounded_clause(decision_log, addendum_2_marker)
        addendum_3 = self._bounded_clause(decision_log, addendum_3_marker)
        addendum_2_codes = {
            CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED,
            CONDITION_NEG8_DRIFT_BOUND_STALE,
            CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED,
            ANCHOR_FALLBACK_MEMBER_REFUSAL,
            "whole_window_drift_allowance_unrecorded",
        }
        addendum_3_codes = {"mock_telemetry_claim_ineligible"}
        for reason in addendum_2_codes:
            with self.subTest(reason=reason):
                self.assertIn(f"`{reason}`", addendum_2)
        for reason in addendum_3_codes:
            with self.subTest(reason=reason):
                self.assertIn(f"`{reason}`", addendum_3)

        code_vocabularies = {
            CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED: (
                NEG8_POINT_DRIFT_CONDITION_CODES,
            ),
            CONDITION_NEG8_DRIFT_BOUND_STALE: (
                NEG8_POINT_DRIFT_CONDITION_CODES,
            ),
            CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED: (
                NEG8_POINT_DRIFT_CONDITION_CODES,
            ),
            ANCHOR_FALLBACK_MEMBER_REFUSAL: (CELL_REFUSAL_CODES,),
            "whole_window_drift_allowance_unrecorded": (
                CELL_REFUSAL_CODES,
                REDUCER_REASON_CODES,
            ),
            "mock_telemetry_claim_ineligible": (
                CELL_REFUSAL_CODES,
                REDUCER_REASON_CODES,
            ),
        }
        self.assertEqual(
            set(code_vocabularies),
            addendum_2_codes | addendum_3_codes,
        )
        for reason, vocabularies in code_vocabularies.items():
            for vocabulary in vocabularies:
                with self.subTest(reason=reason, vocabulary=type(vocabulary).__name__):
                    self.assertIn(reason, vocabulary)

        # Existing gross-family spellings remain code-side registered even
        # though they predate this addendum's five new registrations.
        self.assertIn(
            CONDITION_NEG8_DRIFT_BOUND_UNDERIVED,
            NEG8_POINT_DRIFT_CONDITION_CODES,
        )
        self.assertIn(
            CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED,
            NEG8_POINT_DRIFT_CONDITION_CODES,
        )

    def test_governed_tagged_mock_source_uses_mock_backend_class(self):
        fixture = Path("tests/fixtures/axi_valid_burst")
        identity = custody_telemetry_identity(fixture)
        self.assertTrue(identity.custody_bound_config)
        self.assertTrue(identity.mock_config)
        self.assertTrue(identity.triangle_agrees)

    def test_label_disagreement_is_not_a_current_strict_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "label-disagreement"
            shutil.copytree(Path("tests/fixtures/d078_r01"), bundle)
            summary_path = bundle / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["measurement_quality"]["telemetry_source"] = "mock"
            summary_path.write_text(
                json.dumps(summary, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            self.assertFalse(_current_strict_summary(summary, bundle))

    @staticmethod
    def _custody_triangle_disagreement(root: Path, bundle_id: str) -> Path:
        bundle = root / bundle_id
        shutil.copytree(Path("tests/fixtures/d078_r01"), bundle)
        summary_path = bundle / "summary_metrics.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["measurement_quality"]["telemetry_source"] = "mock"
        summary_path.write_text(
            json.dumps(summary, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return bundle

    def test_custody_triangle_disagreement_refuses_current_core(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = self._custody_triangle_disagreement(root, "member")
            with patch(
                "joulewise.whole_window._manifest_bundle_paths",
                return_value={"member": bundle},
            ):
                reasons = _current_core_rederivation_reasons(
                    core={},
                    bundle_ids=["member"],
                    manifests=[],
                    runs_root=root,
                    policy_sha256="a" * 64,
                )
        self.assertEqual(reasons, {"bundle_strict_invalid"})

    def test_custody_triangle_disagreement_survives_mixed_current_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid = self._custody_triangle_disagreement(root, "invalid")
            current = root / "current"
            shutil.copytree(Path("tests/fixtures/d078_r01"), current)
            current_summary_path = current / "summary_metrics.json"
            current_summary = json.loads(
                current_summary_path.read_text(encoding="utf-8")
            )
            current_summary["summary_provenance"]["reducer_version"] = "0.5.2"
            current_summary_path.write_text(
                json.dumps(current_summary, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with patch(
                "joulewise.whole_window._manifest_bundle_paths",
                return_value={"invalid": invalid, "current": current},
            ):
                reasons = _current_core_rederivation_reasons(
                    core={},
                    bundle_ids=["invalid", "current"],
                    manifests=[],
                    runs_root=root,
                    policy_sha256="a" * 64,
                )
        self.assertIn("bundle_strict_invalid", reasons)
        self.assertIn("whole_window_verdict_provenance_invalid", reasons)

    def test_config_absent_frozen_member_keeps_empty_current_refusal_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "legacy"
            bundle.mkdir()
            (bundle / "summary_metrics.json").write_text(
                json.dumps(
                    {
                        "summary_provenance": {"reducer_version": "0.4.2"},
                        "measurement_quality": {
                            "telemetry_source": "powermetrics"
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with patch(
                "joulewise.whole_window._manifest_bundle_paths",
                return_value={"legacy": bundle},
            ):
                reasons = _current_core_rederivation_reasons(
                    core={},
                    bundle_ids=["legacy"],
                    manifests=[],
                    runs_root=root,
                    policy_sha256="a" * 64,
                )
        self.assertEqual(reasons, set())

    def test_current_neg8_sentinel_custody_disagreement_is_strict_invalid(self):
        policy = {
            "require_bracket": True,
            "max_abs_delta_j": 0.05,
            "max_rel_delta": 0.25,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._custody_triangle_disagreement(root, "neg8-s")
            manifest = {
                "members": [
                    {
                        "execution": "invoked",
                        "bundle_ids": ["neg8-s"],
                        "role": "neg8_daily_reference_start",
                        "sentinel_position": "start",
                    }
                ]
            }
            decision, problem = _derived_neg8_decision(
                [manifest],
                root,
                policy,
                current=True,
            )
        self.assertIsNone(decision)
        self.assertEqual(problem, "bundle_strict_invalid")


    def test_neg8_drift_mint_names_custody_triangle_disagreement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = self._custody_triangle_disagreement(root, "member")
            manifest_path = root / "corpus.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.neg8_reference_corpus.v1",
                        "corpus_id": "custody-disagreement",
                        "freeze_status": "settled_reference",
                        "condition_id": "df-rq-mid",
                        "members": [
                            {
                                "bundle_id": f"member-{index}",
                                "bundle_path": bundle.name,
                            }
                            for index in range(10)
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "custody telemetry triangle disagrees",
            ):
                mint_neg8_drift_bound_artifact(root, manifest_path)

    def test_basis_row_cannot_downgrade_by_stripping_point_drift_shape(self):
        policy_sha256 = "a" * 64
        policy = {
            "require_bracket": True,
            "max_abs_delta_j": 0.05,
            "max_rel_delta": 0.25,
        }
        family_record = {
            "drift_allowance_j": 0.4,
            "trajectory_excursion_max_j": 0.3,
            "derived_repeatability_bound_j": 0.4,
            "provenance": {"bound_derivation_sha256": "b" * 64},
        }
        derived = {
            "decision": "passed",
            "claim_families": {
                "gross_energy": dict(family_record),
                "idle_subtracted_energy": dict(family_record),
            },
            "bound_freshness": {"decision": "fresh"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "campaign.json"
            manifest = {
                "schema_version": "joulewise.campaign_provenance.v1",
                "campaign_policy": {"sha256": policy_sha256},
                "members": [],
            }
            raw = json.dumps(manifest).encode()
            manifest_path.write_bytes(raw)
            basis = {
                "sha256": "c" * 64,
                "member_occurrences": [
                    {"bundle_id": "A", "bundle_path": "A"},
                    {"bundle_id": "B", "bundle_path": "B"},
                ],
            }
            bracket = {
                "schema_version": "joulewise.neg8_bracket_check.v1",
                "decision": "passed",
                "policy": policy,
                "estimand": NEG8_POINT_DRIFT_ESTIMAND,
                "claim_families": derived["claim_families"],
                "drift_bound_artifact": None,
                "bound_freshness": derived["bound_freshness"],
            }
            row = {
                "schema_version": (
                    "joulewise.idle_admission_whole_window_verdict.v1"
                ),
                "status": "passed",
                "bundle_ids": ["A", "B"],
                "campaign_policy": {"sha256": policy_sha256},
                "evaluation_basis": basis,
                "row_provenance": {
                    "schema_version": (
                        "joulewise.idle_admission_whole_window_provenance.v1"
                    ),
                    "policy_sha256": policy_sha256,
                    "membership_sha256": canonical_sha256(["A", "B"]),
                    "source_campaign_manifests": [
                        {
                            "path": "campaign.json",
                            "sha256": hashlib.sha256(raw).hexdigest(),
                        }
                    ],
                },
                "idle_admission_core": {
                    "schema_version": (
                        "joulewise.idle_admission_core_verdict.v1"
                    ),
                    "policy_sha256": policy_sha256,
                    "neg8_bracket": bracket,
                    "adapter_wattage_continuity": {
                        "schema_version": (
                            "joulewise.adapter_wattage_continuity.v1"
                        ),
                        "decision": "stable",
                    },
                    "members": [
                        {
                            "bundle_id": bundle_id,
                            "cpu_admission": {"decision": "admitted"},
                        }
                        for bundle_id in ("A", "B")
                    ],
                },
            }
            with (
                patch(
                    "joulewise.whole_window._validated_evaluation_basis",
                    return_value=basis,
                ),
                patch(
                    "joulewise.whole_window._basis_source_manifests",
                    return_value=[manifest],
                ),
                patch(
                    "joulewise.whole_window._current_core_rederivation_reasons",
                    return_value=set(),
                ),
                patch(
                    "joulewise.whole_window._registered_bracket_policy",
                    return_value=policy,
                ),
                patch(
                    "joulewise.whole_window._derived_neg8_decision",
                    return_value=(derived, None),
                ) as derive,
            ):
                baseline_ok, baseline_reasons = _validate_row(
                    row, root, {"A", "B"}
                )
                self.assertTrue(baseline_ok, baseline_reasons)
                self.assertTrue(derive.call_args.kwargs["point_drift"])
                for field in (
                    "estimand",
                    "claim_families",
                    "drift_bound_artifact",
                    "bound_freshness",
                ):
                    stripped = json.loads(json.dumps(row))
                    del stripped["idle_admission_core"]["neg8_bracket"][field]
                    with self.subTest(field=field):
                        ok, reasons = _validate_row(
                            stripped, root, {"A", "B"}
                        )
                        self.assertFalse(ok)
                        self.assertIn(
                            "whole_window_verdict_provenance_invalid",
                            reasons,
                        )

    def test_basis_passing_row_without_allowances_is_discriminated_absent(self):
        row = {
            "record_type": "idle_admission_whole_window_verdict",
            "bundle_ids": ["A", "B"],
            "evaluation_basis": {
                "sha256": "c" * 64,
                "member_occurrences": [
                    {"bundle_id": "A"},
                    {"bundle_id": "B"},
                ],
            },
            "idle_admission_core": {
                "neg8_bracket": {
                    "claim_families": {
                        "gross_energy": {},
                        "idle_subtracted_energy": {},
                    }
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "campaign_log.jsonl").write_text(
                json.dumps(row) + "\n", encoding="utf-8"
            )
            with (
                patch(
                    "joulewise.whole_window.whole_window_refusal_reasons",
                    return_value=(),
                ),
                patch(
                    "joulewise.whole_window._validate_row",
                    return_value=(True, ()),
                ),
            ):
                result = whole_window_drift_allowances(
                    root, {"A", "B"}
                )
        self.assertEqual(result.status, "absent")
        self.assertEqual(result.allowances, {})

    def test_unrelated_basis_row_does_not_hide_basisless_frozen_replay(
        self,
    ) -> None:
        """Basis detection follows the same requested-ID scope as selection."""

        rows = [
            {
                "record_type": "idle_admission_whole_window_verdict",
                "bundle_ids": ["A"],
            },
            {
                "record_type": "idle_admission_whole_window_verdict",
                "bundle_ids": ["B"],
                "evaluation_basis": {
                    "sha256": "b" * 64,
                    "member_occurrences": [{"bundle_id": "B"}],
                },
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "campaign_log.jsonl").write_text(
                "".join(json.dumps(value) + "\n" for value in rows),
                encoding="utf-8",
            )
            with (
                patch(
                    "joulewise.whole_window.whole_window_refusal_reasons",
                    return_value=(),
                ),
                patch(
                    "joulewise.whole_window._validate_row",
                    return_value=(True, ()),
                ),
            ):
                result = whole_window_drift_allowances(root, {"A"})

        self.assertEqual(result.status, "legacy")
        self.assertEqual(result.allowances, {})

    def _real_fixture(self, root: Path):
        _registry, manifest, _raw, _configs, _roster = evidence_for("draft")
        entry = manifest["entries"][0]
        evidence = root / "axi_attempt_evidence" / manifest["manifest_id"]
        receipts_dir = evidence / "dispatch_receipts"
        receipts_dir.mkdir(parents=True)

        def receipt(attempt: int, run_id: str | None, *, failed: bool) -> dict:
            return {
                "schema_version": "joulewise.dispatch_receipt.v1",
                "manifest_id": manifest["manifest_id"],
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

        def row(receipt_value: dict, *, failed: bool) -> dict:
            raw = render_dispatch_receipt(receipt_value)
            digest = sha256_bytes(raw)
            (receipts_dir / f"{digest}.json").write_bytes(raw)
            return {
                "schema_version": "joulewise.attempt_ledger.v1",
                "manifest_id": manifest["manifest_id"],
                "entry_id": entry["entry_id"],
                "pair_id": entry["pair_id"],
                "arm": entry["arm"],
                "attempt_ordinal": receipt_value["attempt_ordinal"],
                "run_id": receipt_value["finalized_run_id"],
                "dispatch_receipt_sha256": digest,
                "technical_invalid_reason_code": (
                    "dispatch_failed_before_bundle_creation" if failed else None
                ),
                "reason_evidence_sha256": digest if failed else None,
                "eligible_for_analysis": not failed,
            }

        failed_row = row(receipt(0, None, failed=True), failed=True)
        eligible_row = row(receipt(1, "run-first", failed=False), failed=False)
        bundle = (
            root
            / "axi_attempt_bundles"
            / manifest["manifest_id"]
            / entry["entry_id"]
            / "a1"
            / "run-first"
        )
        shutil.copytree(AXI_VALID_BUNDLE, bundle)
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        metadata["run_id"] = "run-first"
        (bundle / "metadata.json").write_bytes(normalized_json_bytes(metadata))
        manifest_path = evidence / "analysis_manifest.json"
        manifest_path.write_bytes(normalized_json_bytes(manifest))
        ledger_path = evidence / "attempt_ledger.jsonl"

        def write_rows(rows: list[dict]) -> bytes:
            raw = "".join(
                json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
                for value in rows
            ).encode()
            ledger_path.write_bytes(raw)
            return raw

        ledger_raw = write_rows([failed_row, eligible_row])
        selection = {
            "attempt_ledger_path": ledger_path.relative_to(root).as_posix(),
            "attempt_ledger_sha256": hashlib.sha256(ledger_raw).hexdigest(),
            "analysis_manifest_path": manifest_path.relative_to(root).as_posix(),
            "analysis_manifest_sha256": hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest(),
            "selected_bundles": [
                {
                    "bundle_id": f"{entry['entry_id']}__a1__run-first",
                    "path": bundle.relative_to(root).as_posix(),
                    "entry_id": entry["entry_id"],
                    "attempt_ordinal": 1,
                    "run_id": "run-first",
                }
            ],
            "quarantined_attempts": [
                {
                    "entry_id": entry["entry_id"],
                    "attempt_ordinal": 0,
                    "run_id": None,
                    "properly_quarantined": True,
                    "recovery_continuity_verified": True,
                }
            ],
        }
        return selection, failed_row, eligible_row, write_rows, row, receipt

    def _fixture(self, root: Path, *, quarantined_run: str | None = None):
        evidence = root / "axi_attempt_evidence" / "m"
        evidence.mkdir(parents=True)
        row = {
            "entry_id": "e",
            "attempt_ordinal": 0,
            "run_id": "run",
            "eligible_for_analysis": True,
        }
        ledger_raw = (json.dumps(row) + "\n").encode()
        manifest_raw = json.dumps({"manifest_id": "m"}).encode()
        (evidence / "attempt_ledger.jsonl").write_bytes(ledger_raw)
        (evidence / "analysis_manifest.json").write_bytes(manifest_raw)
        selection = {
            "attempt_ledger_path": "axi_attempt_evidence/m/attempt_ledger.jsonl",
            "attempt_ledger_sha256": hashlib.sha256(ledger_raw).hexdigest(),
            "analysis_manifest_path": "axi_attempt_evidence/m/analysis_manifest.json",
            "analysis_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "selected_bundles": [
                {
                    "bundle_id": "e__a0__run",
                    "path": "axi_attempt_bundles/m/e/a0/run",
                    "entry_id": "e",
                    "attempt_ordinal": 0,
                    "run_id": "run",
                }
            ],
            "quarantined_attempts": (
                []
                if quarantined_run is None
                else [
                    {
                        "entry_id": "e",
                        "attempt_ordinal": 0,
                        "run_id": quarantined_run,
                        "properly_quarantined": True,
                        "recovery_continuity_verified": True,
                    }
                ]
            ),
        }
        return selection, row

    def test_authoritative_selection_descriptor_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection, row = self._fixture(Path(tmp))
            with patch(
                "joulewise.whole_window.validate_attempt_ledger",
                return_value={"e": row},
            ):
                self.assertEqual(
                    validated_attempt_selection(selection, Path(tmp)),
                    {"e__a0__run"},
                )

    def test_selected_and_quarantined_membership_must_be_disjoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection, row = self._fixture(Path(tmp), quarantined_run="run")
            with patch(
                "joulewise.whole_window.validate_attempt_ledger",
                return_value={"e": row},
            ):
                self.assertIsNone(validated_attempt_selection(selection, Path(tmp)))

    def test_every_rejected_attempt_must_be_listed_as_quarantined(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selection, row = self._fixture(root)
            row["eligible_for_analysis"] = False
            ledger = root / selection["attempt_ledger_path"]
            ledger_raw = (json.dumps(row) + "\n").encode()
            ledger.write_bytes(ledger_raw)
            selection["attempt_ledger_sha256"] = hashlib.sha256(
                ledger_raw
            ).hexdigest()
            selection["selected_bundles"] = []
            with patch(
                "joulewise.whole_window.validate_attempt_ledger",
                return_value={"e": None},
            ):
                self.assertIsNone(validated_attempt_selection(selection, root))

    def test_selected_descriptor_must_match_authoritative_first_eligible_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            selection, row = self._fixture(Path(tmp))
            later = {**row, "attempt_ordinal": 1, "run_id": "later"}
            with patch(
                "joulewise.whole_window.validate_attempt_ledger",
                return_value={"e": later},
            ):
                self.assertIsNone(validated_attempt_selection(selection, Path(tmp)))

    def test_real_validator_rejects_truncated_duplicate_and_reordered_ledgers(self) -> None:
        mutations = {
            "truncated": lambda failed, eligible: [failed],
            "duplicate": lambda failed, eligible: [failed, failed, eligible],
            "reordered": lambda failed, eligible: [eligible, failed],
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                selection, failed, eligible, write_rows, _row, _receipt = (
                    self._real_fixture(root)
                )
                ledger_raw = write_rows(mutate(failed, eligible))
                selection["attempt_ledger_sha256"] = hashlib.sha256(
                    ledger_raw
                ).hexdigest()
                self.assertIsNone(validated_attempt_selection(selection, root))

    def test_real_validator_accepts_complete_first_eligible_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selection, *_rest = self._real_fixture(root)
            self.assertEqual(
                validated_attempt_selection(selection, root),
                {"draft-off-000__a1__run-first"},
            )

    def test_real_validator_rejects_selection_of_later_eligible_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selection, failed, eligible, write_rows, make_row, make_receipt = (
                self._real_fixture(root)
            )
            later = make_row(
                make_receipt(2, "run-later", failed=False), failed=False
            )
            first_bundle = root / selection["selected_bundles"][0]["path"]
            later_bundle = first_bundle.parents[1] / "a2" / "run-later"
            shutil.copytree(first_bundle, later_bundle)
            metadata = json.loads((later_bundle / "metadata.json").read_bytes())
            metadata["run_id"] = "run-later"
            (later_bundle / "metadata.json").write_bytes(
                normalized_json_bytes(metadata)
            )
            ledger_raw = write_rows([failed, eligible, later])
            selection["attempt_ledger_sha256"] = hashlib.sha256(
                ledger_raw
            ).hexdigest()
            selection["selected_bundles"][0].update(
                bundle_id="draft-off-000__a2__run-later",
                path=later_bundle.relative_to(root).as_posix(),
                attempt_ordinal=2,
                run_id="run-later",
            )
            self.assertIsNone(validated_attempt_selection(selection, root))

    def test_frozen_neg8_derivation_keeps_committed_direct_resolution(self) -> None:
        # Delta-review P1 regression: selection-custody path resolution is a
        # CURRENT-strict improvement. A frozen row whose NEG-8 references are
        # reachable only through selection custody must keep the committed
        # runs_root/<bundle_id> resolution — the references stay unreadable
        # (None), the derived decision stays 'failed', and a stored 'passed'
        # stays in conflict. current=True may resolve them; current=False
        # must not.
        import tempfile
        from joulewise.whole_window import _derived_neg8_decision

        policy = {
            "require_bracket": True,
            "max_abs_delta_j": 0.05,
            "max_rel_delta": 0.25,
        }
        summary = {
            "gross_energy_j": 5.0,
            "idle_subtracted_energy_j": 4.5,
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": {"point_j": 5.0, "lower_j": 4.9, "upper_j": 5.1}
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for position, bundle_id in (("start", "neg8-s"), ("end", "neg8-e")):
                hidden = root / "axi_attempt_bundles" / "a1" / bundle_id
                hidden.mkdir(parents=True)
                (hidden / "summary_metrics.json").write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n"
                )
                (hidden / "metadata.json").write_text(
                    json.dumps(
                        {
                            "campaign_environment_preflight": {
                                "snapshot": {"build_version": "25F84"}
                            },
                            "environment": {
                                "power_source": "AC Power",
                                "power": {
                                    "adapter_watts": 140,
                                    "adapter_description": "test supply",
                                },
                            },
                            "instrument_calibration": {
                                "artifact_sha256": "c" * 64
                            },
                        }
                    )
                    + "\n"
                )
            manifest = {
                "attempt_ledger_selection": {
                    "selected_bundles": [
                        {
                            "bundle_id": bundle_id,
                            "path": f"axi_attempt_bundles/a1/{bundle_id}",
                        }
                        for bundle_id in ("neg8-s", "neg8-e")
                    ]
                },
                "members": [
                    {
                        "execution": "invoked",
                        "bundle_ids": ["neg8-s"],
                        "role": "neg8_daily_reference_start",
                        "sentinel_position": "start",
                    },
                    {
                        "execution": "invoked",
                        "bundle_ids": ["neg8-e"],
                        "role": "neg8_daily_reference_end",
                        "sentinel_position": "end",
                    },
                ],
            }
            frozen_decision, frozen_problem = _derived_neg8_decision(
                [manifest], root, policy, current=False
            )
            drift_bound = build_neg8_drift_bound_artifact(
                corpus_id="settled-neg8-selection-test",
                condition_id="df-rq-mid",
                manifest_sha256="a" * 64,
                scientific_config_sha256="b" * 64,
                members=[
                    {
                        "bundle_id": f"reference-{index:02d}",
                        "point_gross_j": 5.0 + index * 0.001,
                        "point_idle_subtracted_j": 4.5 + index * 0.001,
                        "bundle_evidence_sha256": hashlib.sha256(
                            f"reference-{index:02d}".encode()
                        ).hexdigest(),
                    }
                    for index in range(10)
                ],
                derivation_timestamp_s=1_000_000.0,
                freshness_bindings={
                    "os_build": "25F84",
                    "power_supply_identity_sha256": canonical_sha256(
                        {
                            "power_source": "AC Power",
                            "adapter_watts": 140.0,
                            "adapter_description": "test supply",
                        }
                    ),
                    "calibration_identity_sha256": "c" * 64,
                },
            )
            amended_decision, amended_problem = _derived_neg8_decision(
                [manifest],
                root,
                policy,
                current=True,
                point_drift=True,
                drift_bound_artifact=drift_bound,
                freshness_evaluated_at_s=1_000_001.0,
            )
        self.assertIsNone(frozen_problem)
        self.assertEqual(frozen_decision, "failed")
        self.assertIsNone(amended_problem)
        self.assertEqual(amended_decision, "passed")

    def test_partial_and_full_basis_verdicts_coexist_without_latest_wins(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            partial = {
                "record_type": "idle_admission_whole_window_verdict",
                "bundle_ids": ["A"],
                "evaluation_basis": {
                    "sha256": "partial-basis",
                    "member_occurrences": [{"bundle_id": "A"}],
                },
            }
            full = {
                "record_type": "idle_admission_whole_window_verdict",
                "bundle_ids": ["A", "B"],
                "evaluation_basis": {
                    "sha256": "full-basis",
                    "member_occurrences": [
                        {"bundle_id": "A"},
                        {"bundle_id": "B"},
                    ],
                },
            }
            (root / "campaign_log.jsonl").write_text(
                json.dumps(partial) + "\n" + json.dumps(full) + "\n"
            )
            with patch(
                "joulewise.whole_window._validate_row",
                return_value=(True, ()),
            ) as validate:
                self.assertEqual(
                    whole_window_refusal_reasons(root, {"A", "B"}), ()
                )
            self.assertEqual(validate.call_count, 1)
            self.assertEqual(validate.call_args.args[0], full)

    def test_explicit_claim_basis_selects_only_its_matching_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [
                {
                    "record_type": "idle_admission_whole_window_verdict",
                    "bundle_ids": ["A", "B"],
                    "evaluation_basis": {
                        "sha256": basis,
                        "member_occurrences": [
                            {"bundle_id": "A"},
                            {"bundle_id": "B"},
                        ],
                    },
                }
                for basis in ("older-basis", "claim-basis")
            ]
            (root / "campaign_log.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows)
            )
            with patch(
                "joulewise.whole_window._validate_row",
                return_value=(True, ()),
            ) as validate:
                self.assertEqual(
                    whole_window_refusal_reasons(
                        root,
                        {"A", "B"},
                        evaluation_basis_sha256="claim-basis",
                    ),
                    (),
                )
            self.assertEqual(validate.call_count, 1)
            self.assertEqual(
                validate.call_args.args[0]["evaluation_basis"]["sha256"],
                "claim-basis",
            )

    def test_consumption_semantics_dispatch_is_not_latest_wins(self) -> None:
        """A later mint-time row cannot displace explicit widened semantics."""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            widened = {
                "record_type": "idle_admission_whole_window_verdict",
                "bundle_ids": ["A", "B"],
                "evaluation_basis": {
                    "sha256": "shared-basis",
                    "consumption_semantics_id": (
                        MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
                    ),
                    "member_occurrences": [
                        {"bundle_id": "A"},
                        {"bundle_id": "B"},
                    ],
                },
            }
            mint_time = {
                "record_type": "idle_admission_whole_window_verdict",
                "bundle_ids": ["A", "B"],
                "evaluation_basis": {
                    "sha256": "shared-basis",
                    "consumption_semantics_id": (
                        MINTED_CONSUMPTION_SEMANTICS_ID
                    ),
                    "member_occurrences": [
                        {"bundle_id": "A"},
                        {"bundle_id": "B"},
                    ],
                },
            }
            # Put the mint-time row last: file order must not affect dispatch.
            (root / "campaign_log.jsonl").write_text(
                json.dumps(widened) + "\n" + json.dumps(mint_time) + "\n",
                encoding="utf-8",
            )
            with patch(
                "joulewise.whole_window._validate_row",
                return_value=(True, ()),
            ) as validate:
                self.assertEqual(
                    whole_window_refusal_reasons(root, {"A", "B"}),
                    (),
                )
        self.assertEqual(validate.call_count, 1)
        self.assertEqual(
            validate.call_args.args[0]["evaluation_basis"][
                "consumption_semantics_id"
            ],
            MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        )


class MaxBracketConsumptionTests(unittest.TestCase):
    def test_minted_semantics_loads_and_refuses_pending_ledger_snapshot(self) -> None:
        snapshot = CalibrationLedgerSnapshot(
            ledger_schema=LEDGER_SCHEMA,
            ledger_path=Path("fixture-ledger.jsonl"),
            head_sequence=1,
            head_digest="a" * 64,
            receipts=(),
            observations=(),
            refusal_reasons=("calibration_ledger_pending",),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "member"
            bundle.mkdir()
            (bundle / "summary_metrics.json").write_text("{}\n", encoding="utf-8")
            with patch(
                "joulewise.whole_window.load_calibration_ledger_snapshot",
                return_value=snapshot,
            ) as load_snapshot:
                session = AuthenticatedConsumptionSession(
                    root,
                    {"member"},
                    consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
                )
                session._prepare(
                    bundle_paths={"member": bundle},
                    policy=SimpleNamespace(calibration_bracketing=object()),
                )
        load_snapshot.assert_called_once()
        self.assertIs(session.calibration_ledger_snapshot, snapshot)
        self.assertFalse(session.ready)
        self.assertEqual(session.refusal_reasons, ("calibration_ledger_pending",))

    def test_minted_secondary_verifier_refuses_missing_session(self) -> None:
        with patch(
            "joulewise.whole_window._validate_row_uncached",
            return_value=(True, ()),
        ) as validate_uncached:
            valid, reasons = _validate_row(
                {"consumption_semantics_id": MINTED_CONSUMPTION_SEMANTICS_ID},
                Path("/runs-root"),
                {"member"},
            )
        self.assertFalse(valid)
        self.assertEqual(reasons, ("whole_window_verdict_provenance_invalid",))
        validate_uncached.assert_not_called()

    def test_supplied_ledger_snapshot_object_is_reused_without_reload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pin = root / "head.json"
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
            snapshot = load_calibration_ledger_snapshot(
                root / "absent-ledger.jsonl",
                pin,
                baseline_sequence=0,
                baseline_digest=GENESIS_DIGEST,
                require_committed_pin=False,
            )
            first = AuthenticatedConsumptionSession(
                root,
                {"a"},
                calibration_ledger_snapshot=snapshot,
            )
            secondary = AuthenticatedConsumptionSession(
                root,
                {"b"},
                calibration_ledger_snapshot=snapshot,
            )
            self.assertIs(first.calibration_ledger_snapshot, snapshot)
            self.assertIs(secondary.calibration_ledger_snapshot, snapshot)

    """Defect-shaped CAL-REBRACKET-01 reducer/session regressions."""

    EXPECTED_MINTED_ANCHOR_BOUND_S = 0.07799298220062004
    EXPECTED_OPERATIVE_ANCHOR_BOUND_S = 0.07899298220062004
    _physics_cache: dict[str, float] = {}

    @classmethod
    def _build_v052_bundle(
        cls,
        fixture_root: Path,
        *,
        protocol_id: str | None = None,
    ) -> tuple[Path, dict, float, float]:
        """Construct an independent real reducer fixture for one defect shape."""

        from joulewise.reduce import reduce_bundle
        from tests.test_reduce import D078R01RegressionTests

        helper = D078R01RegressionTests()
        evidence = helper._valid_instrument_evidence(
            **({"protocol_id": protocol_id} if protocol_id is not None else {})
        )
        minted_fiducial_bound_s = float(evidence["b_fiducial_s"])
        operative_fiducial_bound_s = minted_fiducial_bound_s + 0.001

        v052_root = fixture_root / "v052"
        v052_root.mkdir()
        bundle = helper._bundle_with_calibration(
            v052_root,
            evidence=evidence,
        )
        cls._install_suite_shape(bundle)
        minted = reduce_bundle(
            bundle,
            reducer_version="0.5.2",
            _instrument_calibration_physics_cache=cls._physics_cache,
        ).to_dict()
        (bundle / "summary_metrics.json").write_text(
            json.dumps(minted, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["instrument_calibration"][
            "verified_effective_b_fiducial_s"
        ] = minted_fiducial_bound_s
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return (
            bundle,
            minted,
            minted_fiducial_bound_s,
            operative_fiducial_bound_s,
        )

    @staticmethod
    def _install_suite_shape(bundle: Path) -> None:
        """Add one real item/block/level window to the powermetrics fixture."""

        shutil.copyfile(
            Path("configs/suite_manifests/mock_suite_manifest.json"),
            bundle / "suite_manifest.json",
        )
        events_path = bundle / "events.jsonl"
        events = [
            json.loads(line)
            for line in events_path.read_text(encoding="utf-8").splitlines()
        ]
        start_s = next(
            float(row["timestamp_s"])
            for row in events
            if row.get("event_type") == "phase_start"
            and row.get("phase") == "prefill"
        )
        end_s = next(
            float(row["timestamp_s"])
            for row in events
            if row.get("event_type") == "phase_end"
            and row.get("phase") == "decode"
        )
        starts = [
            ("suite_start", {}),
            ("block_start", {"block_id": "block_a"}),
            ("level_start", {"level_id": "level_1"}),
            (
                "item_start",
                {"item_id": "mock_item_001", "item_index": 0},
            ),
        ]
        ends = [
            (
                "item_end",
                {
                    "item_id": "mock_item_001",
                    "item_index": 0,
                    "status": "succeeded",
                },
            ),
            ("level_end", {"level_id": "level_1"}),
            ("block_end", {"block_id": "block_a"}),
            ("suite_end", {}),
        ]

        def marker(event_type: str, metadata: dict, timestamp_s: float) -> dict:
            return {
                "event_type": event_type,
                "message": "",
                "metadata": metadata,
                "phase": "suite",
                "timestamp_s": timestamp_s,
            }

        shaped: list[dict] = []
        for row in events:
            if (
                row.get("event_type") == "phase_start"
                and row.get("phase") == "prefill"
            ):
                shaped.extend(
                    marker(event_type, metadata, start_s)
                    for event_type, metadata in starts
                )
            shaped.append(row)
            if (
                row.get("event_type") == "phase_end"
                and row.get("phase") == "decode"
            ):
                shaped.extend(
                    marker(event_type, metadata, end_s)
                    for event_type, metadata in ends
                )
        events_path.write_text(
            "".join(
                json.dumps(row, sort_keys=True) + "\n" for row in shaped
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _write_real_v3_candidate(
        runs_root: Path,
        name: str,
        *,
        first_endpoint_s: float,
        stored_bound_s: float,
    ) -> Path:
        """Install one primary-byte-authenticated protocol-v3 candidate."""

        from joulewise.powermetrics_fiducial import PROTOCOL_ID
        from tests.test_reduce import self_consistent_calibration

        evidence, raw, events = self_consistent_calibration(
            first_endpoint_s=first_endpoint_s,
            protocol_id=PROTOCOL_ID,
        )
        evidence["validation_id"] = name
        evidence["b_fiducial_s"] = stored_bound_s
        evidence["artifact_sha256"] = {
            "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
            "events.jsonl": hashlib.sha256(events).hexdigest(),
        }
        directory = runs_root / "instrument_validation" / name
        (directory / "raw").mkdir(parents=True)
        (directory / "raw" / "powermetrics.plist").write_bytes(raw)
        (directory / "events.jsonl").write_bytes(events)
        evidence_raw = (
            json.dumps(evidence, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        (directory / "instrument_evidence.json").write_bytes(evidence_raw)
        manifest = {
            "schema_version": "joulewise.instrument_validation_manifest.v1",
            "validation_id": name,
            "protocol_id": evidence["protocol_id"],
            "pulse_count": evidence["pulse_count"],
            "artifacts": {
                "events.jsonl": hashlib.sha256(events).hexdigest(),
                "instrument_evidence.json": hashlib.sha256(
                    evidence_raw
                ).hexdigest(),
                "raw/powermetrics.plist": hashlib.sha256(raw).hexdigest(),
            },
        }
        (directory / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return directory

    @staticmethod
    def _install_axi_shape(
        destination: Path,
        *,
        calibrated_source: Path,
    ) -> Path:
        """Bind the committed AXI event-v2 fixture to real powermetrics bytes."""

        shutil.copytree(Path("tests/fixtures/axi_valid_burst"), destination)
        shutil.copytree(
            calibrated_source / "calibration",
            destination / "calibration",
        )
        shutil.copytree(
            calibrated_source / "raw",
            destination / "raw",
            dirs_exist_ok=True,
        )
        shutil.copyfile(
            calibrated_source / "power_trace.csv",
            destination / "power_trace.csv",
        )

        config_path = destination / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["hardware_target"]["id"] = "macbook_m3_max"
        config["hardware_target"]["telemetry_backend"] = "powermetrics"
        config["sampling"]["power_hz"] = 10.0
        config_raw = (
            json.dumps(config, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        config_path.write_bytes(config_raw)

        source_metadata = json.loads(
            (calibrated_source / "metadata.json").read_text(encoding="utf-8")
        )
        axi_metadata = json.loads(
            (destination / "metadata.json").read_text(encoding="utf-8")
        )
        for key in ("batch", "event_semantics_version", "runtime", "speculation"):
            source_metadata[key] = axi_metadata[key]
        source_metadata["runtime"]["primary_source_identity"] = "powermetrics"
        source_metadata["config_sha256"] = hashlib.sha256(
            config_raw
        ).hexdigest()
        source_metadata["run_id"] = config["run_id"]
        (destination / "metadata.json").write_text(
            json.dumps(source_metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        start_s = 1784491122.85
        scale = 0.4 / 2.2
        events_path = destination / "events.jsonl"
        events = [
            json.loads(line)
            for line in events_path.read_text(encoding="utf-8").splitlines()
        ]
        for row in events:
            row["timestamp_s"] = start_s + float(row["timestamp_s"]) * scale
            metadata = row.get("metadata")
            if not isinstance(metadata, dict):
                continue
            admitted_at_s = metadata.get("admitted_at_s")
            if isinstance(admitted_at_s, int | float) and not isinstance(
                admitted_at_s, bool
            ):
                metadata["admitted_at_s"] = (
                    start_s + float(admitted_at_s) * scale
                )
            if "source_identity" in metadata:
                metadata["source_identity"] = "powermetrics"
        events.insert(
            0,
            {
                "event_type": "run_started",
                "message": "run started",
                "metadata": {},
                "phase": "run",
                "timestamp_s": start_s - 0.1,
            },
        )
        events_path.write_text(
            "".join(
                json.dumps(row, sort_keys=True) + "\n" for row in events
            ),
            encoding="utf-8",
        )

        token_path = destination / "outputs" / "request_tokens.jsonl"
        tokens = [
            json.loads(line)
            for line in token_path.read_text(encoding="utf-8").splitlines()
        ]
        for row in tokens:
            row["timestamp_s"] = (
                start_s + float(row["timestamp_s"]) * scale
            )
        token_path.write_text(
            "".join(
                json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
                for row in tokens
            ),
            encoding="utf-8",
        )
        (destination / "summary_metrics.json").unlink()
        return destination

    @staticmethod
    def _half_width(envelope: dict) -> float:
        return max(
            float(envelope["point_j"]) - float(envelope["lower_j"]),
            float(envelope["upper_j"]) - float(envelope["point_j"]),
            float(envelope["max_abs_delta_j"]),
        )

    @staticmethod
    def _bracket(bound_s: float) -> dict:
        return {
            "schema_version": "joulewise.instrument_calibration_bracket.v1",
            "status": "passed",
            "b_fiducial_s": bound_s,
            "pre": {
                "manifest_sha256": "a" * 64,
                "evidence_sha256": "b" * 64,
                "b_fiducial_s": bound_s - 0.001,
            },
            "post": {
                "manifest_sha256": "c" * 64,
                "evidence_sha256": "d" * 64,
                "b_fiducial_s": bound_s,
            },
        }

    @staticmethod
    def _d079_bracket() -> dict:
        return {
            "schema_version": "joulewise.instrument_calibration_bracket.v1",
            "status": "passed",
            "endpoint_max_b_fiducial_s": 0.031,
            "calibration_drift_allowance_s": 0.011,
            "b_fiducial_s": 0.042,
            "pre": {
                "manifest_sha256": "a" * 64,
                "evidence_sha256": "b" * 64,
                "b_fiducial_s": 0.020,
            },
            "post": {
                "manifest_sha256": "c" * 64,
                "evidence_sha256": "d" * 64,
                "b_fiducial_s": 0.031,
            },
            "acceptance": {
                "schema_version": "joulewise.calibration_acceptance_evaluation.v2",
                "allowance": {
                    "value_s": "0.011",
                    "embedding_count": 1,
                    "embedded_in": "b_fiducial_s",
                },
            },
        }

    @staticmethod
    def _summary(point: float, bound_s: float, half_width: float) -> dict:
        def envelope(value: float) -> dict:
            return {
                "method": (
                    "common_trace_shift_plus_independent_edge_corners_v3"
                ),
                "anchor_bound_s": bound_s,
                "point_j": value,
                "lower_j": value - half_width,
                "upper_j": value + half_width,
                "max_abs_delta_j": half_width,
            }

        return {
            "status": "succeeded",
            "summary_provenance": {"reducer_version": "0.5.2"},
            "measurement_quality": {"telemetry_source": "powermetrics"},
            "gross_energy_j": point,
            "phase_energy_j": {"prefill": point / 2.0},
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": envelope(point),
                "/phase_energy_j/prefill": envelope(point / 2.0),
            },
            "window_evidence_precheck": {
                "gross_request": {"eligible": True, "reasons": []},
                "phase": {
                    "prefill": {"eligible": True, "reasons": []}
                },
            },
        }

    def _consumption_provenance_fixture(
        self,
        root: Path,
        *,
        occurrence_ids: tuple[str, ...] = ("member",),
        referenced_ids: set[str] | None = None,
        evaluation_basis_sha256: str | None = None,
    ) -> tuple[dict, list[dict], AuthenticatedConsumptionSession]:
        session = AuthenticatedConsumptionSession(
            root,
            referenced_ids if referenced_ids is not None else set(occurrence_ids),
            evaluation_basis_sha256=evaluation_basis_sha256,
        )
        session._prepared = True
        session.calibration_bracket = self._bracket(0.03)
        session.operative_fiducial_bound_s = 0.03
        provenance: dict[str, dict] = {}
        occurrences: list[dict] = []
        for index, bundle_id in enumerate(occurrence_ids):
            bundle = root / bundle_id
            bundle.mkdir()
            summary = self._summary(40.0 + index, 0.02, 0.1)
            (bundle / "summary_metrics.json").write_text(
                json.dumps(summary) + "\n",
                encoding="utf-8",
            )
            complete = {
                pointer: {
                    **envelope,
                    "anchor_bound_s": 0.03,
                    "lower_j": float(envelope["point_j"]) - 0.2,
                    "upper_j": float(envelope["point_j"]) + 0.2,
                    "max_abs_delta_j": 0.2,
                    "half_width_j": 0.2,
                }
                for pointer, envelope in summary[
                    "energy_anchor_shift_envelopes"
                ].items()
            }
            record = {
                "consumption_semantics_id": (
                    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
                ),
                "minted_bound_dominated": True,
                "minted_fiducial_bound_s": 0.02,
                "operative_fiducial_bound_s": 0.03,
                "calibration_bracket": {
                    "pre": dict(session.calibration_bracket["pre"]),
                    "post": dict(session.calibration_bracket["post"]),
                },
                "operative_envelopes": complete,
            }
            session._provenance[bundle_id] = record
            provenance[bundle_id] = json.loads(json.dumps(record))
            occurrences.append(
                {"bundle_id": bundle_id, "bundle_path": bundle_id}
            )
        basis = {
            "consumption_semantics_id": (
                MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
            ),
            "calibration_bracket_set": {
                "pre": dict(session.calibration_bracket["pre"]),
                "post": dict(session.calibration_bracket["post"]),
            },
            "consumption_provenance": provenance,
        }
        return basis, occurrences, session

    def test_persisted_operative_bound_must_equal_authenticated_bracket_max(
        self,
    ) -> None:
        for persisted_bound in (0.029, 0.031):
            with self.subTest(
                persisted_bound=persisted_bound
            ), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                basis, occurrences, session = (
                    self._consumption_provenance_fixture(root)
                )
                record = basis["consumption_provenance"]["member"]
                record["operative_fiducial_bound_s"] = persisted_bound
                record["minted_bound_dominated"] = True
                self.assertFalse(
                    _consumption_provenance_valid(
                        basis,
                        occurrences,
                        runs_root=root,
                        consumption_session=session,
                    )
                )

    def test_persisted_pointer_subset_cannot_discharge_gov_02(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            basis, occurrences, session = (
                self._consumption_provenance_fixture(root)
            )
            del basis["consumption_provenance"]["member"][
                "operative_envelopes"
            ]["/phase_energy_j/prefill"]
            self.assertFalse(
                _consumption_provenance_valid(
                    basis,
                    occurrences,
                    runs_root=root,
                    consumption_session=session,
                )
            )

    def test_persisted_record_must_equal_session_discharge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            basis, occurrences, session = (
                self._consumption_provenance_fixture(root)
            )
            basis["consumption_provenance"]["member"][
                "minted_fiducial_bound_s"
            ] = 0.019
            self.assertFalse(
                _consumption_provenance_valid(
                    basis,
                    occurrences,
                    runs_root=root,
                    consumption_session=session,
                )
            )

    def test_authenticated_session_provenance_is_accepted_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            basis, occurrences, session = (
                self._consumption_provenance_fixture(root)
            )
            self.assertTrue(
                _consumption_provenance_valid(
                    basis,
                    occurrences,
                    runs_root=root,
                    consumption_session=session,
                )
            )

    def test_explicit_sha_selection_accepts_superset_basis_provenance(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            basis, occurrences, session = self._consumption_provenance_fixture(
                root,
                occurrence_ids=("member", "extra"),
                referenced_ids={"member"},
                evaluation_basis_sha256="e" * 64,
            )
            self.assertTrue(
                _consumption_provenance_valid(
                    basis,
                    occurrences,
                    runs_root=root,
                    consumption_session=session,
                )
            )

    def test_set_equality_selection_rejects_superset_basis_provenance(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            basis, occurrences, session = self._consumption_provenance_fixture(
                root,
                occurrence_ids=("member", "extra"),
                referenced_ids={"member"},
            )
            self.assertFalse(
                _consumption_provenance_valid(
                    basis,
                    occurrences,
                    runs_root=root,
                    consumption_session=session,
                )
            )

    def test_explicit_sha_selection_rejects_genuinely_mismatched_set(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            basis, occurrences, session = self._consumption_provenance_fixture(
                root,
                occurrence_ids=("member", "extra"),
                referenced_ids={"member", "missing"},
                evaluation_basis_sha256="e" * 64,
            )
            self.assertFalse(
                _consumption_provenance_valid(
                    basis,
                    occurrences,
                    runs_root=root,
                    consumption_session=session,
                )
            )

    def test_rederivation_is_identity_at_the_minted_bound(self) -> None:
        from joulewise.reduce import (
            _rederive_summary_for_authenticated_fiducial_bound,
        )

        with tempfile.TemporaryDirectory() as tmp:
            bundle, minted, minted_bound, _operative_bound = (
                self._build_v052_bundle(Path(tmp))
            )
            identity = _rederive_summary_for_authenticated_fiducial_bound(
                bundle,
                authenticated_fiducial_bound_s=minted_bound,
                _instrument_calibration_physics_cache=self._physics_cache,
            )
        minted_envelopes = minted["energy_anchor_shift_envelopes"]
        self.assertEqual(
            identity["energy_anchor_shift_envelopes"],
            minted_envelopes,
        )

    def test_rederivation_covers_every_named_metric_family(self) -> None:
        from joulewise.reduce import (
            _rederive_summary_for_authenticated_fiducial_bound,
        )

        with tempfile.TemporaryDirectory() as tmp:
            bundle, _minted, _minted_bound, operative_bound = (
                self._build_v052_bundle(Path(tmp))
            )
            widened = _rederive_summary_for_authenticated_fiducial_bound(
                bundle,
                authenticated_fiducial_bound_s=operative_bound,
                _instrument_calibration_physics_cache=self._physics_cache,
            )
        widened_envelopes = widened["energy_anchor_shift_envelopes"]
        expected_pointers = {
            "/gross_energy_j",
            "/idle_subtracted_energy_j",
            "/energy_request_j",
            "/energy_token_j",
            "/energy_output_token_j",
            "/phase_energy_j/prefill",
            "/phase_energy_j/decode",
            "/suite_item_energy_j/0:mock_item_001",
            "/suite_block_energy_j/block_a",
            "/suite_level_energy_j/block_a~1level_1",
        }
        self.assertEqual(
            set(widened_envelopes),
            expected_pointers,
        )

    def test_dominated_member_strictly_widens_every_named_metric_family(
        self,
    ) -> None:
        from joulewise.reduce import (
            _rederive_summary_for_authenticated_fiducial_bound,
        )

        with tempfile.TemporaryDirectory() as tmp:
            bundle, minted, _minted_bound, operative_bound = (
                self._build_v052_bundle(Path(tmp))
            )
            widened = _rederive_summary_for_authenticated_fiducial_bound(
                bundle,
                authenticated_fiducial_bound_s=operative_bound,
                _instrument_calibration_physics_cache=self._physics_cache,
            )
        minted_envelopes = minted["energy_anchor_shift_envelopes"]
        widened_envelopes = widened["energy_anchor_shift_envelopes"]
        self.assertEqual(set(widened_envelopes), set(minted_envelopes))
        for pointer, minted_envelope in minted_envelopes.items():
            with self.subTest(pointer=pointer):
                wider = widened_envelopes[pointer]
                self.assertEqual(
                    wider["point_j"], minted_envelope["point_j"]
                )
                self.assertLessEqual(
                    wider["lower_j"], minted_envelope["lower_j"]
                )
                self.assertGreaterEqual(
                    wider["upper_j"], minted_envelope["upper_j"]
                )
                self.assertGreater(
                    self._half_width(wider),
                    self._half_width(minted_envelope),
                )

    def test_rederivation_records_the_expected_operative_anchor_bound(
        self,
    ) -> None:
        from joulewise.reduce import (
            _rederive_summary_for_authenticated_fiducial_bound,
        )

        with tempfile.TemporaryDirectory() as tmp:
            bundle, minted, _minted_bound, operative_bound = (
                self._build_v052_bundle(Path(tmp))
            )
            widened = _rederive_summary_for_authenticated_fiducial_bound(
                bundle,
                authenticated_fiducial_bound_s=operative_bound,
                _instrument_calibration_physics_cache=self._physics_cache,
            )
        self.assertAlmostEqual(
            minted["energy_anchor_shift_envelopes"][
                "/gross_energy_j"
            ]["anchor_bound_s"],
            self.EXPECTED_MINTED_ANCHOR_BOUND_S,
            places=12,
        )
        for pointer, envelope in widened["energy_anchor_shift_envelopes"].items():
            with self.subTest(pointer=pointer):
                self.assertAlmostEqual(
                    envelope["anchor_bound_s"],
                    self.EXPECTED_OPERATIVE_ANCHOR_BOUND_S,
                    places=12,
                )

    def test_reducer_0_6_2_uses_the_same_authenticated_override_path(
        self,
    ) -> None:
        from joulewise.reduce import (
            _rederive_summary_for_authenticated_fiducial_bound,
            reduce_bundle,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_bundle, _source_minted, _minted_bound, operative_bound = (
                self._build_v052_bundle(root)
            )
            axi_bundle = self._install_axi_shape(
                root / "axi-v062",
                calibrated_source=source_bundle,
            )
            axi_minted = reduce_bundle(
                axi_bundle,
                reducer_version="0.6.2",
                _instrument_calibration_physics_cache=self._physics_cache,
            ).to_dict()
            (axi_bundle / "summary_metrics.json").write_text(
                json.dumps(axi_minted, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            axi_widened = (
                _rederive_summary_for_authenticated_fiducial_bound(
                    axi_bundle,
                    authenticated_fiducial_bound_s=operative_bound,
                    _instrument_calibration_physics_cache=self._physics_cache,
                )
            )
        self.assertEqual(
            axi_minted["summary_provenance"]["reducer_version"],
            "0.6.2",
        )
        expected_pointers = {
            "/gross_energy_j",
            "/idle_subtracted_energy_j",
            "/phase_energy_j/prefill",
            "/phase_energy_j/decode",
        }
        self.assertEqual(
            set(axi_widened["energy_anchor_shift_envelopes"]),
            expected_pointers,
        )
        for pointer in expected_pointers:
            with self.subTest(pointer=pointer):
                minted = axi_minted["energy_anchor_shift_envelopes"][pointer]
                widened = axi_widened["energy_anchor_shift_envelopes"][pointer]
                self.assertEqual(widened["point_j"], minted["point_j"])
                self.assertLessEqual(widened["lower_j"], minted["lower_j"])
                self.assertGreaterEqual(widened["upper_j"], minted["upper_j"])
                self.assertGreater(
                    self._half_width(widened),
                    self._half_width(minted),
                )
                self.assertAlmostEqual(
                    widened["anchor_bound_s"],
                    self.EXPECTED_OPERATIVE_ANCHOR_BOUND_S,
                    places=12,
                )

    def test_rederivation_refuses_when_the_trace_tail_is_too_short(
        self,
    ) -> None:
        from joulewise.reduce import (
            _rederive_summary_for_authenticated_fiducial_bound,
        )

        with tempfile.TemporaryDirectory() as tmp:
            bundle, _minted, minted_bound, _operative_bound = (
                self._build_v052_bundle(Path(tmp))
            )
            short_tail = (
                _rederive_summary_for_authenticated_fiducial_bound(
                    bundle,
                    authenticated_fiducial_bound_s=minted_bound + 2.0,
                    _instrument_calibration_physics_cache=self._physics_cache,
                )
            )
        self.assertIn(
            "post_window_trace_tail_shorter_than_anchor_bound",
            short_tail["window_evidence_precheck"]["gross_request"][
                "reasons"
            ],
        )
        self.assertNotIn("energy_anchor_shift_envelopes", short_tail)

    def test_session_caches_complete_widened_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "member"
            bundle.mkdir()
            minted = self._summary(40.0, 0.02, 0.1)
            widened = self._summary(40.0, 0.03, 0.2)
            # A metric-local refusal that already existed at mint time is not
            # a widening failure. The affected metric remains barred for its
            # own consumer, while complete whole-window rebracketing proceeds.
            for summary in (minted, widened):
                summary["window_evidence_precheck"]["phase"]["setup"] = {
                    "eligible": False,
                    "reasons": ["clock_bound_exceeds_quarter_window"],
                }
            (bundle / "summary_metrics.json").write_text(
                json.dumps(minted) + "\n", encoding="utf-8"
            )
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "instrument_calibration": {
                            "verified_effective_b_fiducial_s": 0.02
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            session = AuthenticatedConsumptionSession(root, {"member"})
            with (
                patch(
                    "joulewise.whole_window.calibration_bracket_for_bundles",
                    return_value=(self._bracket(0.03), ()),
                ),
                patch(
                    "joulewise.whole_window._current_strict_summary",
                    return_value=True,
                ),
                patch(
                    "joulewise.whole_window._verify_instrument_calibration",
                    return_value=(0.02, None),
                ) as verify,
                patch(
                    "joulewise.whole_window."
                    "_rederive_summary_for_authenticated_fiducial_bound",
                    return_value=widened,
                ) as rederive,
            ):
                session._prepare(
                    bundle_paths={"member": bundle},
                    policy=SimpleNamespace(calibration_bracketing=object()),
                )
                session._prepare(
                    bundle_paths={"member": bundle},
                    policy=SimpleNamespace(calibration_bracketing=object()),
                )

        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertEqual(rederive.call_count, 1)
        self.assertIs(
            verify.call_args.kwargs["physics_cache"],
            rederive.call_args.kwargs[
                "_instrument_calibration_physics_cache"
            ],
        )
        self.assertIs(session.summary_for("member"), widened)
        provenance = session.provenance_for("member")
        self.assertTrue(provenance["minted_bound_dominated"])
        self.assertEqual(
            set(provenance["operative_envelopes"]),
            {"/gross_energy_j", "/phase_energy_j/prefill"},
        )
        for envelope in provenance["operative_envelopes"].values():
                self.assertAlmostEqual(envelope["half_width_j"], 0.2)
        self.assertEqual(
            provenance["calibration_bracket"]["post"][
                "evidence_sha256"
            ],
            "d" * 64,
        )

    def test_d079_allowance_drives_reduction_and_evaluation_basis_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "member"
            bundle.mkdir()
            minted = self._summary(40.0, 0.02, 0.1)
            widened = self._summary(40.0, 0.042, 0.3)
            (bundle / "summary_metrics.json").write_text(
                json.dumps(minted) + "\n", encoding="utf-8"
            )
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "instrument_calibration": {
                            "verified_effective_b_fiducial_s": 0.02
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            bracket = self._d079_bracket()
            session = AuthenticatedConsumptionSession(root, {"member"})
            with (
                patch(
                    "joulewise.whole_window.calibration_bracket_for_bundles",
                    return_value=(bracket, ()),
                ),
                patch(
                    "joulewise.whole_window._current_strict_summary",
                    return_value=True,
                ),
                patch(
                    "joulewise.whole_window._verify_instrument_calibration",
                    return_value=(0.02, None),
                ),
                patch(
                    "joulewise.whole_window."
                    "_rederive_summary_for_authenticated_fiducial_bound",
                    return_value=widened,
                ) as rederive,
            ):
                session._prepare(
                    bundle_paths={"member": bundle},
                    policy=SimpleNamespace(calibration_bracketing=object()),
                )

            self.assertTrue(session.ready, session.refusal_reasons)
            self.assertEqual(
                rederive.call_args.kwargs[
                    "authenticated_fiducial_bound_s"
                ],
                0.042,
            )
            provenance = session.provenance_by_bundle()
            self.assertEqual(
                provenance["member"]["calibration_bracket"][
                    "calibration_drift_allowance_s"
                ],
                0.011,
            )
            basis = build_evaluation_basis(
                policy_sha256="e" * 64,
                member_occurrences=[
                    {"bundle_id": "member", "bundle_path": "member"}
                ],
                calibration_bracket=bracket,
                consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
                consumption_provenance=provenance,
            )
            self.assertEqual(
                basis["calibration_bracket_set"][
                    "calibration_drift_allowance_s"
                ],
                0.011,
            )
            self.assertEqual(
                basis["calibration_bracket_set"][
                    "operative_b_fiducial_s"
                ],
                0.042,
            )

    def test_legacy_bracket_basis_hash_is_byte_identical(self) -> None:
        bracket = {
            "pre": {
                "manifest_sha256": "a" * 64,
                "evidence_sha256": "b" * 64,
                "b_fiducial_s": 0.02,
            },
            "post": {
                "manifest_sha256": "c" * 64,
                "evidence_sha256": "d" * 64,
                "b_fiducial_s": 0.021,
            },
            "b_fiducial_s": 0.021,
            "status": "passed",
        }
        basis = build_evaluation_basis(
            policy_sha256="e" * 64,
            member_occurrences=[{"bundle_id": "m", "bundle_path": "m"}],
            calibration_bracket=bracket,
        )
        self.assertEqual(
            basis["sha256"],
            "e1e93a54eb17a7d9eeb3766659d879dc388c4bbe4a90694c668b12860b4ee959",
        )
        self.assertEqual(
            set(basis["calibration_bracket_set"]), {"pre", "post"}
        )

    def test_d079_real_selector_to_real_reducer_embeds_allowance_once(self) -> None:
        from joulewise.bundle_read import BundleReader
        from joulewise.powermetrics_fiducial import PROTOCOL_ID
        from joulewise.reduce import reduce_bundle

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle, minted, minted_bound, _old_operative = (
                self._build_v052_bundle(root, protocol_id=PROTOCOL_ID)
            )
            window = BundleReader(bundle).measured_window()
            self.assertIsNotNone(window)
            # This retained powermetrics fixture predates current environment-
            # admission custody. Neutralize only that unrelated gate while the
            # selector, candidate authentication, calibration verification, and
            # complete reducer/re-reducer remain production implementations.
            with (
                patch(
                    "joulewise.reduce.current_environment_refusals",
                    return_value=(),
                ),
                patch(
                    "joulewise.reduce.environment_admission_refusals",
                    return_value=(),
                ),
            ):
                minted = reduce_bundle(
                    bundle,
                    reducer_version="0.5.2",
                    _instrument_calibration_physics_cache=self._physics_cache,
                ).to_dict()
                (bundle / "summary_metrics.json").write_text(
                    json.dumps(minted, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                pre_candidate = self._write_real_v3_candidate(
                    root,
                    "real-pre",
                    first_endpoint_s=window.start_s - 400.0,
                    stored_bound_s=0.024,
                )
                post_candidate = self._write_real_v3_candidate(
                    root,
                    "real-post",
                    first_endpoint_s=window.end_s + 5.0,
                    stored_bound_s=0.025,
                )
                ledger_path = root / "calibration_ledger.jsonl"
                head_pin_path = root / "calibration_head.json"
                head_pin_path.write_text(
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
                for candidate_path in (pre_candidate, post_candidate):
                    evidence = json.loads(
                        (candidate_path / "instrument_evidence.json").read_text(
                            encoding="utf-8"
                        ),
                        parse_float=str,
                    )
                    bindings = evidence["bindings"]
                    epoch = {
                        field: bindings[field]
                        for field in (
                            "os_build",
                            "hardware_model",
                            "power_policy",
                            "sampling_interval_ms",
                            "estimator_revision",
                            "pulse_protocol_id",
                        )
                    }
                    append_pending_receipt(
                        ledger_path,
                        attempt_id=candidate_path.name,
                        custody_locator=str(candidate_path),
                        identity_epoch=epoch,
                        t1_bindings=bindings,
                        head_pin_path=head_pin_path,
                        require_committed_pin=False,
                    )
                    final = finalize_attempt_receipt(
                        ledger_path,
                        attempt_id=candidate_path.name,
                        disposition="valid",
                        custody_locator=str(candidate_path),
                        artifact_sha256=calibration_artifact_hashes(
                            candidate_path
                        ),
                        identity_epoch=epoch,
                        t1_bindings=bindings,
                        capture_wall_time_s=str(
                            evidence["capture_wall_time_s"]
                        ),
                        exact_bound_lexeme_s=str(evidence["b_fiducial_s"]),
                    )
                    head_pin_path.write_text(
                        json.dumps(head_pin_for_receipt(final)) + "\n",
                        encoding="utf-8",
                    )
                calibration_snapshot = load_calibration_ledger_snapshot(
                    ledger_path,
                    head_pin_path,
                    baseline_sequence=0,
                    baseline_digest=GENESIS_DIGEST,
                    require_committed_pin=False,
                )
                session = AuthenticatedConsumptionSession(
                    root,
                    {bundle.name},
                    calibration_ledger_snapshot=calibration_snapshot,
                    _allow_unissued_calibration_fixture=True,
                )
                session._prepare(
                    bundle_paths={bundle.name: bundle},
                    policy=SimpleNamespace(
                        calibration_bracketing=CalibrationBracketingPolicy(
                            require_bracket=True,
                            calibration_bracket_max_drift_s=0.010,
                        )
                    ),
                )

            self.assertTrue(session.ready, session.refusal_reasons)
            bracket = session.calibration_bracket
            self.assertEqual(bracket["status"], "passed")
            self.assertEqual(
                bracket["pre"]["b_fiducial_decimal_s"], "0.024"
            )
            self.assertEqual(
                bracket["post"]["b_fiducial_decimal_s"], "0.025"
            )
            self.assertEqual(
                bracket["acceptance"]["allowance"]["value_s"],
                "0.010818",
            )
            self.assertEqual(
                bracket["acceptance"]["allowance"]["embedding_count"],
                1,
            )
            self.assertAlmostEqual(bracket["b_fiducial_s"], 0.035818)
            provenance = session.provenance_for(bundle.name)
            self.assertAlmostEqual(
                provenance["operative_fiducial_bound_s"],
                bracket["b_fiducial_s"],
            )
            operative = session.summary_for(bundle.name)
            pointer = "/gross_energy_j"
            minted_anchor = minted["energy_anchor_shift_envelopes"][pointer][
                "anchor_bound_s"
            ]
            operative_anchor = operative["energy_anchor_shift_envelopes"][
                pointer
            ]["anchor_bound_s"]
            self.assertAlmostEqual(
                operative_anchor - minted_anchor,
                bracket["b_fiducial_s"] - minted_bound,
                places=12,
            )

    def test_session_retains_widening_introduced_metric_local_refusal(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "member"
            bundle.mkdir()
            minted = self._summary(40.0, 0.02, 0.1)
            widened = self._summary(40.0, 0.03, 0.2)
            for summary, bound_s, half_width in (
                (minted, 0.02, 0.1),
                (widened, 0.03, 0.2),
            ):
                summary["phase_energy_j"]["decode"] = 10.0
                summary["energy_anchor_shift_envelopes"][
                    "/phase_energy_j/decode"
                ] = {
                    "method": (
                        "common_trace_shift_plus_independent_edge_corners_v3"
                    ),
                    "anchor_bound_s": bound_s,
                    "point_j": 10.0,
                    "lower_j": 10.0 - half_width,
                    "upper_j": 10.0 + half_width,
                    "max_abs_delta_j": half_width,
                }
                summary["window_evidence_precheck"]["phase"]["decode"] = {
                    "eligible": True,
                    "reasons": [],
                }
            widened["window_evidence_precheck"]["phase"]["prefill"] = {
                "eligible": False,
                "reasons": ["clock_bound_exceeds_quarter_window"],
                "windows": [
                    {
                        "eligible": False,
                        "reasons": [
                            "clock_bound_exceeds_quarter_window"
                        ],
                    }
                ],
            }
            (bundle / "summary_metrics.json").write_text(
                json.dumps(minted) + "\n", encoding="utf-8"
            )
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "instrument_calibration": {
                            "verified_effective_b_fiducial_s": 0.02
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            session = AuthenticatedConsumptionSession(root, {"member"})
            with (
                patch(
                    "joulewise.whole_window.calibration_bracket_for_bundles",
                    return_value=(self._bracket(0.03), ()),
                ),
                patch(
                    "joulewise.whole_window._current_strict_summary",
                    return_value=True,
                ),
                patch(
                    "joulewise.whole_window._verify_instrument_calibration",
                    return_value=(0.02, None),
                ),
                patch(
                    "joulewise.whole_window."
                    "_rederive_summary_for_authenticated_fiducial_bound",
                    return_value=widened,
                ),
            ):
                session._prepare(
                    bundle_paths={"member": bundle},
                    policy=SimpleNamespace(calibration_bracketing=object()),
                )

        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertEqual(session.refusal_reasons, ())
        self.assertEqual(
            session.path_refusal_reasons,
            {
                "member": {
                    ("phase", "prefill"): (
                        "clock_bound_exceeds_quarter_window",
                    )
                }
            },
        )
        self.assertIs(session.summary_for("member"), widened)
        self.assertIsNotNone(session.provenance_for("member"))

    def test_session_skips_rederivation_for_undominated_member(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "member"
            bundle.mkdir()
            minted = self._summary(40.0, 0.03, 0.2)
            (bundle / "summary_metrics.json").write_text(
                json.dumps(minted) + "\n", encoding="utf-8"
            )
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "instrument_calibration": {
                            "verified_effective_b_fiducial_s": 0.03
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            session = AuthenticatedConsumptionSession(root, {"member"})
            with (
                patch(
                    "joulewise.whole_window.calibration_bracket_for_bundles",
                    return_value=(self._bracket(0.03), ()),
                ),
                patch(
                    "joulewise.whole_window._current_strict_summary",
                    return_value=True,
                ),
                patch(
                    "joulewise.whole_window._verify_instrument_calibration",
                    return_value=(0.03, None),
                ),
                patch(
                    "joulewise.whole_window."
                    "_rederive_summary_for_authenticated_fiducial_bound",
                ) as rederive,
            ):
                session._prepare(
                    bundle_paths={"member": bundle},
                    policy=SimpleNamespace(calibration_bracketing=object()),
                )

        self.assertTrue(session.ready, session.refusal_reasons)
        self.assertEqual(session.summary_for("member"), minted)
        self.assertFalse(
            session.provenance_for("member")["minted_bound_dominated"]
        )
        rederive.assert_not_called()

    def test_session_authentication_cache_is_scoped_and_fail_closed(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = AuthenticatedConsumptionSession(root, {"member"})
            session._prepared = True
            row = {"record_type": "test", "value": 1}
            with patch(
                "joulewise.whole_window._validate_row_uncached",
                return_value=(True, ()),
            ) as authenticate:
                first = _validate_row(
                    row,
                    root,
                    {"member"},
                    consumption_session=session,
                )
                second = _validate_row(
                    json.loads(json.dumps(row)),
                    root,
                    {"member"},
                    consumption_session=session,
                )
                self.assertEqual(authenticate.call_count, 1)

                other_root = root / "other-root"
                other_root.mkdir()
                _validate_row(
                    row,
                    other_root,
                    {"member"},
                    consumption_session=session,
                )
                _validate_row(
                    row,
                    root,
                    {"other-member"},
                    consumption_session=session,
                )
                self.assertEqual(authenticate.call_count, 3)

                # The selected basis is part of cache identity even within
                # one session object.
                session.evaluation_basis_sha256 = "a" * 64
                basis_first = _validate_row(
                    row,
                    root,
                    {"member"},
                    consumption_session=session,
                )
                basis_second = _validate_row(
                    row,
                    root,
                    {"member"},
                    consumption_session=session,
                )
                self.assertEqual(authenticate.call_count, 4)

                failure_row = {"record_type": "test", "value": "failure"}
                authenticate.return_value = (False, ("refused",))
                failure_first = _validate_row(
                    failure_row,
                    root,
                    {"member"},
                    consumption_session=session,
                )
                failure_second = _validate_row(
                    failure_row,
                    root,
                    {"member"},
                    consumption_session=session,
                )
                self.assertEqual(authenticate.call_count, 6)

                # Losing readiness invalidates prior successes rather than
                # leaving them available if mutable session state recovers.
                authenticate.return_value = (True, ())
                session.refusal_reasons = ("instrument_calibration_invalid",)
                _validate_row(
                    row,
                    root,
                    {"member"},
                    consumption_session=session,
                )
                self.assertEqual(session._row_validation_results, {})
                session.refusal_reasons = ()
                recovered = _validate_row(
                    row,
                    root,
                    {"member"},
                    consumption_session=session,
                )
                cached_recovered = _validate_row(
                    row,
                    root,
                    {"member"},
                    consumption_session=session,
                )

        self.assertEqual(first, (True, ()))
        self.assertEqual(second, first)
        self.assertEqual(basis_first, (True, ()))
        self.assertEqual(basis_second, basis_first)
        self.assertEqual(failure_first, (False, ("refused",)))
        self.assertEqual(failure_second, failure_first)
        self.assertEqual(recovered, (True, ()))
        self.assertEqual(cached_recovered, recovered)
        self.assertEqual(authenticate.call_count, 8)

    def test_provenance_scalar_disagreement_blocks_before_rederivation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "member"
            bundle.mkdir()
            minted = self._summary(40.0, 0.02, 0.1)
            (bundle / "summary_metrics.json").write_text(
                json.dumps(minted) + "\n", encoding="utf-8"
            )
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "instrument_calibration": {
                            "verified_effective_b_fiducial_s": 0.01
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            session = AuthenticatedConsumptionSession(root, {"member"})
            with (
                patch(
                    "joulewise.whole_window.calibration_bracket_for_bundles",
                    return_value=(self._bracket(0.03), ()),
                ),
                patch(
                    "joulewise.whole_window._current_strict_summary",
                    return_value=True,
                ),
                patch(
                    "joulewise.whole_window._verify_instrument_calibration",
                    return_value=(0.02, None),
                ),
                patch(
                    "joulewise.whole_window."
                    "_rederive_summary_for_authenticated_fiducial_bound",
                ) as rederive,
            ):
                session._prepare(
                    bundle_paths={"member": bundle},
                    policy=SimpleNamespace(calibration_bracketing=object()),
                )

        self.assertEqual(
            session.refusal_reasons,
            ("whole_window_verdict_provenance_invalid",),
        )
        self.assertIsNone(session.summary_for("member"))
        rederive.assert_not_called()

    def test_session_propagates_short_tail_leaf_without_minted_fallback(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "member"
            bundle.mkdir()
            minted = self._summary(40.0, 0.02, 0.1)
            failed = {
                **minted,
                "energy_anchor_shift_envelopes": None,
                "window_evidence_precheck": {
                    "gross_request": {
                        "eligible": False,
                        "reasons": [
                            "post_window_trace_tail_shorter_than_anchor_bound"
                        ],
                    }
                },
            }
            (bundle / "summary_metrics.json").write_text(
                json.dumps(minted) + "\n", encoding="utf-8"
            )
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "instrument_calibration": {
                            "verified_effective_b_fiducial_s": 0.02
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            session = AuthenticatedConsumptionSession(root, {"member"})
            with (
                patch(
                    "joulewise.whole_window.calibration_bracket_for_bundles",
                    return_value=(self._bracket(0.03), ()),
                ),
                patch(
                    "joulewise.whole_window._current_strict_summary",
                    return_value=True,
                ),
                patch(
                    "joulewise.whole_window._verify_instrument_calibration",
                    return_value=(0.02, None),
                ),
                patch(
                    "joulewise.whole_window."
                    "_rederive_summary_for_authenticated_fiducial_bound",
                    return_value=failed,
                ),
            ):
                session._prepare(
                    bundle_paths={"member": bundle},
                    policy=SimpleNamespace(calibration_bracketing=object()),
                )

        self.assertEqual(
            session.refusal_reasons,
            ("post_window_trace_tail_shorter_than_anchor_bound",),
        )
        self.assertIsNone(session.summary_for("member"))
        self.assertIsNone(session.provenance_for("member"))


class SalvageSemanticsDispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def row(self, semantics: str, *, basis: str = "b" * 64) -> dict:
        return {
            "record_type": "idle_admission_whole_window_verdict",
            "bundle_ids": ["survivor"],
            "evaluation_basis": {
                "sha256": basis,
                "consumption_semantics_id": semantics,
                "member_occurrences": [{"bundle_id": "survivor"}],
            },
        }

    def write_rows(self, *rows: dict) -> None:
        (self.root / "campaign_log.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows),
            encoding="utf-8",
        )

    def test_b5_salvage_binding_cannot_substitute_same_policy_window(self) -> None:
        descriptor_x = {
            "path": "campaign_manifests/window-x.json",
            "sha256": "1" * 64,
            "size": 101,
        }
        descriptor_y = {
            "path": "campaign_manifests/window-y.json",
            "sha256": "2" * 64,
            "size": 202,
        }
        binding_x = {"source_campaign_manifests": [descriptor_x]}
        manifest_y = {
            "members": [
                {
                    "execution": "invoked",
                    "bundle_ids": ["survivor-y", "dangler-y"],
                }
            ]
        }
        self.assertFalse(
            whole_window_module._salvage_binding_matches_verified_manifest_set(
                binding_x,
                [descriptor_y],
                [manifest_y],
                self.root,
                "dangler-y",
            )
        )
        binding_y = {"source_campaign_manifests": [descriptor_y]}
        self.assertTrue(
            whole_window_module._salvage_binding_matches_verified_manifest_set(
                binding_y,
                [descriptor_y],
                [manifest_y],
                self.root,
                "dangler-y",
            )
        )
        self.assertFalse(
            whole_window_module._salvage_binding_matches_verified_manifest_set(
                binding_y,
                [descriptor_y, descriptor_x],
                [manifest_y, manifest_y],
                self.root,
                "dangler-y",
            )
        )

    def test_no_argument_consumers_exclude_salvage_rows(self) -> None:
        args, _failed, bundle_ids = install_real_salvage_window(self.root)
        with d100_real_salvage_leaf_patches(), redirect_stdout(io.StringIO()):
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 0)
            reasons = whole_window_refusal_reasons(self.root, set(bundle_ids))
            self.assertIn("whole_window_neg8_verdict_missing", reasons)
            self.assertEqual(
                whole_window_refusal_reasons(
                    self.root,
                    set(bundle_ids),
                    consumption_semantics_id=(
                        SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
                    ),
                ),
                ("whole_window_verdict_provenance_invalid",),
            )

    def test_explicit_salvage_dispatch_selects_only_salvage(self) -> None:
        args, _failed, bundle_ids = install_real_salvage_window(self.root)
        with d100_real_salvage_leaf_patches(), redirect_stdout(io.StringIO()):
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 0)
            row = read_all_jsonl(self.root / "campaign_log.jsonl")[-1]
            basis_sha256 = row["evaluation_basis"]["sha256"]
            session = AuthenticatedConsumptionSession(
                self.root,
                set(bundle_ids),
                evaluation_basis_sha256=basis_sha256,
                consumption_semantics_id=(
                    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
                ),
            )
            session._prepare(
                bundle_paths={bundle_id: self.root / bundle_id for bundle_id in bundle_ids},
                policy=run_campaign_module.load_campaign_policy(
                    args.campaign_policy
                ).policy,
            )
            self.assertTrue(session.ready)
            self.assertEqual(
                whole_window_refusal_reasons(
                    self.root,
                    set(bundle_ids),
                    evaluation_basis_sha256=basis_sha256,
                    consumption_session=session,
                    consumption_semantics_id=SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
                ),
                (),
            )
            for semantics in (
                MINTED_CONSUMPTION_SEMANTICS_ID,
                MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
            ):
                with self.subTest(semantics=semantics):
                    self.assertIn(
                        "whole_window_neg8_verdict_missing",
                        whole_window_refusal_reasons(
                            self.root,
                            set(bundle_ids),
                            evaluation_basis_sha256=basis_sha256,
                            consumption_semantics_id=semantics,
                        ),
                    )

    def test_multiple_salvage_rows_for_one_basis_conflict_even_if_identical(self) -> None:
        args, _failed, bundle_ids = install_real_salvage_window(self.root)
        with d100_real_salvage_leaf_patches(), redirect_stdout(io.StringIO()):
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 0)
            log_path = self.root / "campaign_log.jsonl"
            row = read_all_jsonl(log_path)[-1]
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
            reasons = whole_window_refusal_reasons(
                self.root,
                set(bundle_ids),
                evaluation_basis_sha256=row["evaluation_basis"]["sha256"],
                consumption_semantics_id=SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
            )
        self.assertEqual(reasons, ("whole_window_verdict_conflict",))

    def test_b5_real_row_rejects_same_policy_binding_substitution(self) -> None:
        root_x = self.root / "window-x"
        root_y = self.root / "window-y"
        args_x, _failed_x, bundle_ids_x = install_real_salvage_window(
            root_x, session_id="window-x"
        )
        args_y, _failed_y, bundle_ids_y = install_real_salvage_window(
            root_y, session_id="window-y"
        )
        self.assertEqual(bundle_ids_x, bundle_ids_y)
        with d100_real_salvage_leaf_patches(), redirect_stdout(io.StringIO()):
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args_x), 0)
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args_y), 0)
            row_x = read_all_jsonl(root_x / "campaign_log.jsonl")[-1]
            rows_y = read_all_jsonl(root_y / "campaign_log.jsonl")
            forged = json.loads(json.dumps(rows_y[-1]))
            forged["salvage_dangler_exclusion"] = row_x[
                "salvage_dangler_exclusion"
            ]
            forged["window_membership"] = row_x["window_membership"]
            forged["evaluation_basis"]["salvage_dangler_exclusion"] = row_x[
                "salvage_dangler_exclusion"
            ]
            basis_core = {
                key: value
                for key, value in forged["evaluation_basis"].items()
                if key != "sha256"
            }
            forged["evaluation_basis"]["sha256"] = canonical_sha256(basis_core)
            rows_y[-1] = forged
            (root_y / "campaign_log.jsonl").write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows_y),
                encoding="utf-8",
            )
            session = AuthenticatedConsumptionSession(
                root_y,
                set(bundle_ids_y),
                evaluation_basis_sha256=forged["evaluation_basis"]["sha256"],
                consumption_semantics_id=(
                    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
                ),
            )
            session._prepare(
                bundle_paths={bundle_id: root_y / bundle_id for bundle_id in bundle_ids_y},
                policy=run_campaign_module.load_campaign_policy(
                    args_y.campaign_policy
                ).policy,
            )
            reasons = whole_window_refusal_reasons(
                root_y,
                set(bundle_ids_y),
                evaluation_basis_sha256=forged["evaluation_basis"]["sha256"],
                consumption_session=session,
                consumption_semantics_id=(
                    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
                ),
            )
        self.assertIn("whole_window_verdict_provenance_invalid", reasons)

    def test_salvage_basis_is_compound_max_plus_exact_exclusion(self) -> None:
        occurrence = {
            "bundle_id": "survivor",
            "bundle_path": "survivor",
            "config_sha256": "1" * 64,
            "metadata_sha256": "2" * 64,
            "summary_sha256": "3" * 64,
        }
        provenance = {
            "survivor": {
                "consumption_semantics_id": MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
            }
        }
        exclusion = {"schema_version": "joulewise.salvage_dangler_exclusion.v1"}
        with patch(
            "joulewise.whole_window.validate_salvage_exclusion_payload",
            return_value=True,
        ):
            basis = build_evaluation_basis(
                policy_sha256="a" * 64,
                member_occurrences=[occurrence],
                calibration_bracket=None,
                consumption_semantics_id=SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
                consumption_provenance=provenance,
                salvage_dangler_exclusion=exclusion,
            )
        self.assertEqual(
            basis["consumption_semantics_id"],
            SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
        )
        self.assertEqual(basis["salvage_dangler_exclusion"], exclusion)
        self.assertEqual(basis["consumption_provenance"], provenance)


if __name__ == "__main__":
    unittest.main()
