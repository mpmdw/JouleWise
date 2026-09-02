"""Strict-bundle and CLI integration fixtures for P2-037."""

from __future__ import annotations

import ast
import base64
import copy
import io
import hashlib
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import floor_mint_estimator
import joulewise.controller as controller_module
from joulewise.analysis_engine import AnalysisInputError, analyze_claims
from joulewise.analysis_engine.artifact import render_claim_verdicts
from joulewise.analysis_engine.artifact import (
    calculate_claim_verdicts_id,
    validate_claim_verdicts,
)
from joulewise.analysis_manifest import calculate_manifest_id
from joulewise.analysis_manifest_v3 import (
    ARM_FREEZE,
    FINALIZED_BASENAME_SUFFIX,
    FINALIZED_INTERNAL_ERROR_CODE,
    FINALIZED_MALFORMED_VALUE_CODE,
    FINALIZED_REFUSAL_CODES,
    TRANSPORT_RULING_PENDING_REFUSAL,
    finalize_prospective_analysis_manifest_v3,
    normalized_realized_stack_identity,
)
from joulewise.arm_readiness import LaunchLineageError
from joulewise.analysis_engine.estimators import StochasticVarianceTerm
from joulewise.analysis_engine.multiplicity import holm_adjust
from joulewise.analysis_engine.inputs import (
    BundleEvidence,
    CONSUMPTION_PROVENANCE_PRECHECK_KEY,
    FloorEvidenceBinding,
    FloorRequest,
    FloorResolution,
    LoadedAnalysisInputs,
    MOCK_TELEMETRY_CLAIM_REFUSAL,
    _campaign_cooldown_evidence,
    bind_floor_artifact_evidence,
    campaign_cooldown_evidence,
    declared_evidence_roots,
    floor_binding_reason_codes,
    floor_request_for_evidence,
    floor_stack_identity,
    load_analysis_inputs,
    load_manifest,
    realized_scientific_identity,
    window_evidence_precheck,
)
from joulewise.idle_admission import ADAPTER_CONTINUITY_SCHEMA, NEG8_BRACKET_SCHEMA
from joulewise.schemas import BenchmarkConfig
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
)
from joulewise.whole_window import (
    AuthenticatedConsumptionSession,
    CustodyTelemetryIdentity,
    IDLE_ADMISSION_CORE_SCHEMA,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    OCCURRENCE_SUPERSESSION_SCHEMA,
    REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
    WHOLE_WINDOW_SCHEMA,
    build_row_provenance,
    source_manifest_descriptors,
    supersession_entry_sha256,
    validate_occurrence_supersession_entry,
    whole_window_refusal_reasons,
)
from joulewise.cli import main, validate_bundle
from joulewise.detection_floor import (
    ATTRIBUTION_FLOOR_SOURCE,
    ATTRIBUTION_LIMIT_CLASS,
    abba_delta,
    absolute_false_effect_floor,
    attribution_single_count_discipline,
    build_absolute_record,
    build_comparative_record,
    build_floor_artifact,
    build_floor_cell,
    build_transport_group,
    canonical_domain_sha256,
    comparative_false_effect_floor,
    complete_bundle_sha256,
    STACK_IDENTITY_DOMAIN,
    validate_floor_artifact,
)
from scripts.generate_matrix import main as generate_matrix
from tests.test_detection_floor import (
    condition_family,
    make_artifact,
    make_cell,
    make_regime,
    whole_window_allowance,
)
from tests.test_run_campaign import (
    d100_real_salvage_leaf_patches,
    install_real_salvage_window,
    read_all_jsonl,
    run_campaign_module,
)
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
SIDECARS = {"order_manifest.json", "analysis_manifest.json"}
CLEAN_SOURCE_STATE = {
    "git_commit": "1" * 40,
    "tracked": "clean",
    "staged": "clean",
    "untracked": "clean",
    "diff_sha256": "2" * 64,
}
# No strict-valid powermetrics fixture exists in-repo. The positive companions
# therefore stipulate production telemetry identity while exercising the real
# strict-valid mock bundles and the real analyze_claims wiring.
PRODUCTION_TELEMETRY_IDENTITY = CustodyTelemetryIdentity(
    custody_bound_config=True,
    config_backend_class="powermetrics",
    metadata_backend_class="powermetrics",
    summary_backend_class="powermetrics",
    triangle_agrees=True,
)


def fixture_calibration_ledger_snapshot() -> CalibrationLedgerSnapshot:
    return CalibrationLedgerSnapshot(
        ledger_schema=LEDGER_SCHEMA,
        ledger_path=Path("fixture-ledger.jsonl"),
        head_sequence=0,
        head_digest=GENESIS_DIGEST,
        receipts=(),
        observations=(),
        refusal_reasons=(),
    )


def prepared_minted_consumption_session(
    runs_root: Path,
    referenced_bundle_ids: set[str],
    **kwargs: object,
) -> AuthenticatedConsumptionSession:
    declared_semantics = kwargs.get("consumption_semantics_id")
    if isinstance(declared_semantics, str):
        return AuthenticatedConsumptionSession(
            runs_root,
            referenced_bundle_ids,
            evaluation_basis_sha256=kwargs.get("evaluation_basis_sha256"),
            consumption_semantics_id=declared_semantics,
            calibration_ledger_snapshot=kwargs.get(
                "calibration_ledger_snapshot"
            ),
        )
    session = AuthenticatedConsumptionSession(
        runs_root,
        referenced_bundle_ids,
        evaluation_basis_sha256=kwargs.get("evaluation_basis_sha256"),
        consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,
        calibration_ledger_snapshot=fixture_calibration_ledger_snapshot(),
    )
    session._prepare(
        bundle_paths={
            bundle_id: Path(runs_root) / bundle_id
            for bundle_id in referenced_bundle_ids
        },
        policy=SimpleNamespace(calibration_bracketing=object()),
    )
    return session


def install_explicit_mock_sampler(bundle: Path) -> None:
    metadata_path = bundle / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["workload_provenance"]["sampler"] = {
        "api": "mock_runtime.generate",
        "kind": "deterministic_mock",
        "pinned": True,
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def install_passing_analysis_whole_window(
    runs_root: Path,
    bundle_ids: list[str],
    *,
    source_name: str,
    schema_version: str = "joulewise.campaign_provenance.v1",
) -> None:
    """Install one provenance-bound passing verdict for a synthetic corpus."""

    bundle_ids = sorted(bundle_ids)
    reference_ids = [
        f"{source_name}-neg8-reference-start",
        f"{source_name}-neg8-reference-end",
    ]
    for bundle_id in reference_ids:
        bundle = runs_root / bundle_id
        bundle.mkdir(parents=True, exist_ok=True)
        summary = {
            "gross_energy_j": 1.0,
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": {
                    "point_j": 1.0,
                    "lower_j": 0.99,
                    "upper_j": 1.01,
                }
            },
        }
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
    covered_ids = sorted([*bundle_ids, *reference_ids])
    # Anchor to the repo-registered production policy: re-derivation resolves
    # tolerances from tracked policy files only (fail-closed on unknown shas).
    registered_policy_path = (
        ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json"
    )
    policy_sha = hashlib.sha256(registered_policy_path.read_bytes()).hexdigest()
    registered_bracket = json.loads(registered_policy_path.read_text())[
        "idle_admission_extension"
    ]["neg8_bracket"]
    campaign_dir = runs_root / "campaign_manifests"
    campaign_dir.mkdir(parents=True, exist_ok=True)
    source_path = campaign_dir / f"{source_name}.json"
    source_manifest = {
        "schema_version": schema_version,
        "session_id": source_name,
        "analysis_manifest_id": None,
        "campaign_policy": {"sha256": policy_sha},
        "members": [
            {
                "execution": "invoked",
                "run_id": reference_ids[0],
                "bundle_ids": [reference_ids[0]],
                "role": "neg8_daily_reference_start",
                "sentinel_position": "start",
            },
            {
                "execution": "invoked",
                "run_id": f"{source_name}-campaign-members",
                "bundle_ids": bundle_ids,
            },
            {
                "execution": "invoked",
                "run_id": reference_ids[1],
                "bundle_ids": [reference_ids[1]],
                "role": "neg8_daily_reference_end",
                "sentinel_position": "end",
            },
        ],
    }
    source_path.write_text(
        json.dumps(
            source_manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    descriptors = source_manifest_descriptors(runs_root, [source_path])
    row = {
        "schema_version": WHOLE_WINDOW_SCHEMA,
        "record_type": "idle_admission_whole_window_verdict",
        "status": "passed",
        "campaign_policy": {"sha256": policy_sha},
        "bundle_ids": covered_ids,
        "idle_admission_core": {
            "schema_version": IDLE_ADMISSION_CORE_SCHEMA,
            "policy_sha256": policy_sha,
            "members": [
                {
                    "bundle_id": bundle_id,
                    "cpu_admission": {"decision": "admitted"},
                }
                for bundle_id in covered_ids
            ],
            "adapter_wattage_continuity": {
                "schema_version": ADAPTER_CONTINUITY_SCHEMA,
                "decision": "stable",
            },
            "neg8_bracket": {
                "schema_version": NEG8_BRACKET_SCHEMA,
                "decision": "passed",
                "policy": dict(registered_bracket),
            },
            "conditions": [],
        },
    }
    row["row_provenance"] = build_row_provenance(
        policy_sha256=policy_sha,
        bundle_ids=covered_ids,
        source_manifests=descriptors,
    )
    log_rows = []
    if schema_version == "joulewise.campaign_provenance.v2":
        from joulewise.campaign_provenance import campaign_provenance_attestation

        log_rows.append(
            campaign_provenance_attestation(
                manifest_path=source_path,
                raw_manifest_bytes=source_path.read_bytes(),
                manifest=source_manifest,
                timestamp="2026-08-01T12:00:00Z",
            )
        )
    log_rows.append(row)
    (runs_root / "campaign_log.jsonl").write_text(
        "".join(json.dumps(value) + "\n" for value in log_rows)
    )


def install_two_row_supersession_counterfactual(
    runs_root: Path,
    bundle_ids: list[str],
) -> list[dict]:
    """Append two identical writer-shaped rows for each named bundle.

    Each row has the same 11 keys as the production recorder emits, but its
    values are synthetic.  The source manifests intentionally omit
    ``campaign_policy`` because this helper installs the legacy/hand-edited
    consumer counterfactual after finalization rather than exercising the
    guarded recorder.  That omission does not weaken the reader case: every
    installed row passes the production supersession validator before the
    exact out-of-band duplicate bytes are appended.
    """

    root = Path(runs_root).resolve()
    campaign_dir = root / "campaign_manifests"
    campaign_dir.mkdir(parents=True, exist_ok=True)
    policy_path = (
        ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json"
    )
    policy_sha256 = hashlib.sha256(policy_path.read_bytes()).hexdigest()
    rows = []
    for bundle_ordinal, bundle_id in enumerate(bundle_ids):
        canonical = root / bundle_id
        if not canonical.is_dir():
            raise AssertionError("counterfactual bundle must be canonical")
        occurrences = []
        for suffix in ("a", "b"):
            manifest_path = campaign_dir / (
                f"supersession-counterfactual-{bundle_ordinal}-{suffix}.json"
            )
            manifest = {
                "schema_version": "joulewise.campaign_provenance.v1",
                "analysis_manifest_id": None,
                "session_id": (
                    f"supersession-counterfactual-{bundle_ordinal}-{suffix}"
                ),
                "members": [
                    {
                        "config": f"{bundle_id}.json",
                        "execution": "invoked",
                        "run_id": bundle_id,
                        "bundle_ids": [bundle_id],
                    }
                ],
            }
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            occurrences.append(
                {
                    "bundle_id": bundle_id,
                    "source_manifest": {
                        "path": manifest_path.relative_to(root).as_posix(),
                        "sha256": hashlib.sha256(
                            manifest_path.read_bytes()
                        ).hexdigest(),
                    },
                    "member_index": 0,
                    "bundle_index": 0,
                }
            )

        quarantine = root.parent / f"supersession-quarantine-{bundle_id}"
        quarantine.mkdir()
        custody = {}
        for name, field in (
            ("config.json", "config_sha256"),
            ("metadata.json", "metadata_sha256"),
            ("summary_metrics.json", "summary_sha256"),
        ):
            raw = (canonical / name).read_bytes()
            (quarantine / name).write_bytes(raw)
            custody[field] = hashlib.sha256(raw).hexdigest()
        row = {
            "schema_version": OCCURRENCE_SUPERSESSION_SCHEMA,
            "record_type": "campaign_occurrence_supersession",
            "timestamp": f"2026-09-01T12:00:0{bundle_ordinal}Z",
            "runs_root": str(root),
            "campaign_policy_sha256": policy_sha256,
            "bundle_id": bundle_id,
            "selected_occurrence": occurrences[1],
            "superseded_occurrences": [occurrences[0]],
            "quarantine": {"path": str(quarantine.resolve()), **custody},
            "reason": "counterfactual duplicate supersession disposition",
        }
        row["entry_sha256"] = supersession_entry_sha256(row)
        if not validate_occurrence_supersession_entry(row, root):
            raise AssertionError("counterfactual supersession row must validate")
        encoded = (json.dumps(row, sort_keys=True) + "\n").encode("utf-8")
        with (root / "campaign_log.jsonl").open("ab") as handle:
            handle.write(encoded)
            handle.write(encoded)
        rows.append(row)
    return rows


def _real_mlx_identity_inputs(arm_id: str) -> tuple[dict, dict]:
    """Adapt a real MLX metadata boundary to either frozen v3 arm."""

    fixture = ROOT / "tests" / "fixtures" / "d078_r01"
    raw_config = json.loads(
        (fixture / "config.json").read_text(encoding="utf-8")
    )
    metadata = json.loads(
        (fixture / "metadata.json").read_text(encoding="utf-8")
    )
    expected = ARM_FREEZE[arm_id]["realized_stack_identity"]
    expected_artifact = expected["model_artifact"]
    artifact = metadata["workload_provenance"]["model"]["artifact_identity"]
    artifact.pop("sha256", None)
    artifact.update(
        status="ok",
        kind=expected_artifact["kind"],
        algorithm=expected_artifact["algorithm"],
        folded_sha256=expected_artifact["folded_sha256"],
    )
    metadata["workload_provenance"]["tokenizer"] = copy.deepcopy(
        expected["tokenizer"]
    )
    metadata["adapters"]["runtime"]["name"] = expected["runtime"]["name"]
    metadata["adapters"]["runtime"]["prepare_metadata"].update(
        adapter=expected["runtime"]["adapter"],
        version=expected["runtime"]["version"],
    )
    metadata["adapters"]["telemetry"]["name"] = expected["telemetry"]["name"]
    metadata["device"] = copy.deepcopy(expected["device_boundary"])
    metadata["model"] = copy.deepcopy(expected["model"])
    metadata["quantization"] = copy.deepcopy(expected["quantization"])
    raw_config["model"] = copy.deepcopy(expected["model"])
    raw_config["quantization"] = copy.deepcopy(expected["quantization"])
    return raw_config, metadata


def _v3_fixture_artifact(*, diverged: bool = False) -> dict:
    manifest_path = (
        ROOT
        / "configs"
        / "campaigns"
        / "splitwise_decode_v1"
        / "analysis_manifest_v3.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evidence_by_entry = {}
    for entry in manifest["entries"]:
        block_number = entry["block_number"]
        value = (
            10.0 + block_number
            if entry["arm_id"] == "A"
            else 20.0 + block_number
        )
        raw_config, metadata = _real_mlx_identity_inputs(entry["arm_id"])
        evidence_by_entry[entry["entry_id"]] = BundleEvidence(
            entry=entry,
            bundle_id=entry["run_id"],
            relative_path=entry["run_id"],
            path=Path("runs") / entry["run_id"],
            summary={
                "status": "succeeded",
                "test_value": value,
                "measurement_quality": {
                    "cooldown_cap_hit": False,
                    "idle_window_suspect": False,
                },
            },
            metadata=metadata,
            raw_config=raw_config,
            strict_problems=(),
            base_reason_codes=(
                ("whole_window_verdict_conflict",) if diverged else ()
            ),
            config_sha256=entry["config_sha256"],
            expected_config_sha256=entry["config_sha256"],
            summary_sha256="a" * 64,
            replacement_classification="registered",
            inclusion_status="excluded" if diverged else "included",
        )
    floor_artifact = make_artifact()
    floor_artifact["artifact_id"] = "df-v3-test"
    self_errors = validate_floor_artifact(floor_artifact)
    if self_errors:
        raise AssertionError(self_errors)
    floor_bytes = (json.dumps(floor_artifact, indent=2) + "\n").encode("utf-8")
    floor_sha256 = hashlib.sha256(floor_bytes).hexdigest()
    loaded_inputs = LoadedAnalysisInputs(
        manifest=manifest,
        manifest_sha256="b" * 64,
        floor_artifact=floor_artifact,
        floor_sha256=floor_sha256,
        floor_artifact_bytes=floor_bytes,
        registered=evidence_by_entry,
        effective=evidence_by_entry,
        extra_audits=(),
        valid_replacements=(),
        unregistered_matching=(),
        top_up_entry_ids=frozenset(),
        supersession_audit=(
            {
                "scope": "analysis_corpus",
                "evidence_root_id": None,
                "authenticated_basis": {
                    "kind": "whole_window_evaluation_basis_sha256",
                    "sha256": "d" * 64,
                },
                "raw_count": 2 if diverged else 1,
                "validated_count": 1,
                "status": "refused" if diverged else "clean",
            },
            {
                "scope": "floor_evidence",
                "evidence_root_id": "a10",
                "authenticated_basis": {
                    "kind": "floor_component_campaign_log_sha256",
                    "sha256s": ["e" * 64],
                },
                "raw_count": 0,
                "validated_count": 0,
                "status": "clean",
            },
            {
                "scope": "floor_evidence",
                "evidence_root_id": "window_c",
                "authenticated_basis": {
                    "kind": "floor_component_campaign_log_sha256",
                    "sha256s": ["f" * 64],
                },
                "raw_count": 0,
                "validated_count": 0,
                "status": "clean",
            },
        ),
        supersession_diverged=diverged,
    )
    floor_resolutions = (
        FloorResolution(
            status="exact",
            artifact_id="df-v3-test",
            artifact_sha256=floor_sha256,
            source_cell_ids=("floor-a",),
            transport_group_id=None,
            transport_rule_id=None,
            floor_abs_j=0.8,
            floor_cmp_j=1.0,
            floor_gate_j=1.0,
            reason_codes=(),
        ),
        FloorResolution(
            status="exact",
            artifact_id="df-v3-test",
            artifact_sha256=floor_sha256,
            source_cell_ids=("floor-b",),
            transport_group_id=None,
            transport_rule_id=None,
            floor_abs_j=0.9,
            floor_cmp_j=1.2,
            floor_gate_j=1.2,
            reason_codes=(),
        ),
    )
    patches = (
        mock.patch(
            "joulewise.analysis_engine.metric_value",
            side_effect=lambda summary, metric: summary["test_value"],
        ),
        mock.patch(
            "joulewise.analysis_engine.window_evidence_precheck",
            return_value={"reasons": ()},
        ),
        mock.patch(
            "joulewise.analysis_engine.governed_stochastic_variance",
            return_value=([{"name": "idle", "variance": 0.0}], ()),
        ),
        mock.patch(
            "joulewise.analysis_engine.deterministic_bounds",
            return_value=(
                {
                    "E_interpolation_joint_edge_bound_j": 0.05,
                    "E_clock_anchor_shift_bound_j": 0.10,
                },
                (),
            ),
        ),
        mock.patch(
            "joulewise.analysis_engine._resolve_contrast_floor",
            return_value=list(floor_resolutions),
        ),
        mock.patch(
            "joulewise.analysis_engine.load_analysis_inputs",
            return_value=loaded_inputs,
        ),
    )
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        return analyze_claims(
            manifest_path,
            Path("runs"),
            Path("floor.json"),
            strict_validator=lambda path, strict=True: [],
        )


def _v3_supersession_finding_artifact() -> dict:
    artifact = _v3_fixture_artifact(diverged=True)
    audit = artifact["supersession_audit"][0]
    audit["validated_count"] = audit["raw_count"]
    audit["findings"] = [
        {
            "reason_code": (
                REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS
            ),
            "bundle_ids": ["bundle-a", "bundle-z"],
        }
    ]
    artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
    return artifact


class AnalysisIntegrationTests(unittest.TestCase):
    def setUp(self):
        source_patch = mock.patch(
            "joulewise.bundle._capture_source_state",
            return_value=dict(CLEAN_SOURCE_STATE),
        )
        source_patch.start()
        self.addCleanup(source_patch.stop)
        session_patch = mock.patch(
            "joulewise.analysis_engine.inputs.AuthenticatedConsumptionSession",
            side_effect=prepared_minted_consumption_session,
        )
        session_patch.start()
        self.addCleanup(session_patch.stop)

    def test_production_two_row_audit_persists_and_stripped_finding_refuses(self):
        """Insert two bundle ids in reverse lexical order, then call production.

        ``load_analysis_inputs`` must call ``supersession_visibility_scan`` and
        emit the ids sorted; the artifact must persist that exact finding.  The
        counterfactual input then strips findings from the produced audit row.
        """

        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            finalized = finalize_prospective_analysis_manifest_v3(
                fixture["prospective_path"],
                plan_tree_path=fixture["plan_tree_path"],
                custody_root=fixture["root"],
                runs_root=fixture["runs_root"],
                whole_window_verdict_path=fixture["verdict_path"],
                bracket_binding_path=fixture["bracket_path"],
                calibration_ledger_path=fixture["ledger_path"],
                aggregate_floor_artifact_path=fixture["floor_path"],
                output_dir=fixture["root"],
            )
            finalized_path = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            bundle_ids = [
                finalized["entries"][-1]["run_id"],
                finalized["entries"][0]["run_id"],
            ]
            self.assertNotEqual(bundle_ids, sorted(bundle_ids))
            install_two_row_supersession_counterfactual(
                fixture["runs_root"],
                bundle_ids,
            )

            loaded = load_analysis_inputs(
                finalized_path,
                fixture["runs_root"],
                fixture["floor_path"],
                strict_validator=lambda path, strict=True: [],
            )
            analysis_audit = next(
                row
                for row in loaded.supersession_audit
                if row["scope"] == "analysis_corpus"
            )
            self.assertEqual(analysis_audit["raw_count"], 4)
            self.assertEqual(analysis_audit["validated_count"], 4)
            self.assertEqual(analysis_audit["status"], "refused")
            self.assertEqual(
                analysis_audit["findings"],
                [
                    {
                        "reason_code": (
                            REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS
                        ),
                        "bundle_ids": sorted(bundle_ids),
                    }
                ],
            )

            artifact = analyze_claims(
                finalized_path,
                fixture["runs_root"],
                fixture["floor_path"],
                strict_validator=lambda path, strict=True: [],
            )
            artifact_bytes = render_claim_verdicts(artifact)
            persisted = json.loads(artifact_bytes)
            persisted_audit = next(
                row
                for row in persisted["supersession_audit"]
                if row["scope"] == "analysis_corpus"
            )
            self.assertEqual(persisted_audit, dict(analysis_audit))
            self.assertEqual(
                persisted_audit["findings"],
                [
                    {
                        "reason_code": (
                            REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS
                        ),
                        "bundle_ids": sorted(bundle_ids),
                    }
                ],
            )
            expected_audit_bytes = "\n".join(
                "    " + line
                for line in json.dumps(
                    dict(analysis_audit), indent=2, ensure_ascii=False
                ).splitlines()
            ).encode("utf-8")
            self.assertIn(expected_audit_bytes, artifact_bytes)
            self.assertEqual(
                validate_claim_verdicts(
                    persisted,
                    frozen_manifest=finalized,
                ),
                [],
            )

            stripped = copy.deepcopy(persisted)
            stripped_audit = next(
                row
                for row in stripped["supersession_audit"]
                if row["scope"] == "analysis_corpus"
            )
            del stripped_audit["findings"]
            stripped["claim_verdicts_id"] = calculate_claim_verdicts_id(
                stripped
            )
            stripped_persisted = json.loads(render_claim_verdicts(stripped))
            errors = validate_claim_verdicts(
                stripped_persisted,
                frozen_manifest=finalized,
            )
            self.assertTrue(
                any(
                    "authenticated equal counts cannot be refused" in error
                    for error in errors
                ),
                errors,
            )

    def test_finalized_gamma_runs_real_engine_then_isolates_math_layers(self):
        """Real synthetic end-to-end pass followed by isolated math seams."""

        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(
                Path(tmp), shared_family=True
            )
            finalized = finalize_prospective_analysis_manifest_v3(
                fixture["prospective_path"],
                plan_tree_path=fixture["plan_tree_path"],
                custody_root=fixture["root"],
                runs_root=fixture["runs_root"],
                whole_window_verdict_path=fixture["verdict_path"],
                bracket_binding_path=fixture["bracket_path"],
                calibration_ledger_path=fixture["ledger_path"],
                aggregate_floor_artifact_path=fixture["floor_path"],
                output_dir=fixture["root"],
            )
            finalized_path = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            loaded_manifest, manifest_sha = load_manifest(finalized_path)
            self.assertEqual(loaded_manifest, finalized)
            real_inputs = load_analysis_inputs(
                finalized_path,
                fixture["runs_root"],
                fixture["floor_path"],
                strict_validator=lambda path, strict=True: [],
            )
            self.assertEqual(len(real_inputs.registered), 80)
            self.assertEqual(
                {
                    evidence.relative_path
                    for evidence in real_inputs.registered.values()
                },
                {entry["bundle_path"] for entry in finalized["entries"]},
            )
            end_to_end_artifact = analyze_claims(
                finalized_path,
                fixture["runs_root"],
                fixture["floor_path"],
                strict_validator=lambda path, strict=True: [],
            )
            self.assertEqual(
                [row["contrast_id"] for row in end_to_end_artifact["contrasts"]],
                [row["contrast_id"] for row in finalized["contrasts"]],
            )
            self.assertEqual(
                end_to_end_artifact["inputs"]["analysis_manifest"]["file_sha256"],
                manifest_sha,
            )

            with self.assertRaisesRegex(
                AnalysisInputError,
                "analysis_manifest_prospective_not_consumable",
            ):
                analyze_claims(
                    fixture["prospective_path"],
                    fixture["runs_root"],
                    fixture["floor_path"],
                    strict_validator=lambda path, strict=True: [],
                )

            evidence_by_entry = {}
            for entry in finalized["entries"]:
                bundle = fixture["runs_root"] / entry["bundle_path"]
                raw_config = json.loads((bundle / "config.json").read_text())
                metadata = json.loads((bundle / "metadata.json").read_text())
                summary = {
                    "status": "succeeded",
                    "test_value": (
                        20.0 + entry["block_number"]
                        if entry["arm_id"].endswith(":B")
                        else 10.0 + entry["block_number"]
                    ),
                    "measurement_quality": {
                        "cooldown_cap_hit": False,
                        "idle_window_suspect": False,
                    },
                }
                evidence_by_entry[entry["entry_id"]] = BundleEvidence(
                    entry=entry,
                    bundle_id=entry["run_id"],
                    relative_path=entry["bundle_path"],
                    path=bundle,
                    summary=summary,
                    metadata=metadata,
                    raw_config=raw_config,
                    strict_problems=(),
                    base_reason_codes=(),
                    config_sha256=entry["config_sha256"],
                    expected_config_sha256=entry["config_sha256"],
                    summary_sha256=hashlib.sha256(
                        json.dumps(summary, sort_keys=True).encode()
                    ).hexdigest(),
                    replacement_classification="registered",
                    inclusion_status="included",
                )
            floor_artifact = make_artifact()
            floor_artifact["artifact_id"] = "synthetic-finalized-edge-floor"
            floor_bytes = (json.dumps(floor_artifact, indent=2) + "\n").encode()
            floor_sha = hashlib.sha256(floor_bytes).hexdigest()
            loaded_inputs = LoadedAnalysisInputs(
                manifest=finalized,
                manifest_sha256=manifest_sha,
                floor_artifact=floor_artifact,
                floor_sha256=floor_sha,
                floor_artifact_bytes=floor_bytes,
                registered=evidence_by_entry,
                effective=evidence_by_entry,
                extra_audits=(),
                valid_replacements=(),
                unregistered_matching=(),
                top_up_entry_ids=frozenset(),
                supersession_audit=(
                    {
                        "scope": "analysis_corpus",
                        "evidence_root_id": None,
                        "authenticated_basis": {
                            "kind": "whole_window_evaluation_basis_sha256",
                            "sha256": finalized["evidence"][
                                "whole_window_verdict"
                            ]["evaluation_basis_sha256"],
                        },
                        "raw_count": 1,
                        "validated_count": 1,
                        "status": "clean",
                    },
                    {
                        "scope": "floor_evidence",
                        "evidence_root_id": "a10",
                        "authenticated_basis": {
                            "kind": "floor_component_campaign_log_sha256",
                            "sha256s": ["e" * 64],
                        },
                        "raw_count": 0,
                        "validated_count": 0,
                        "status": "clean",
                    },
                    {
                        "scope": "floor_evidence",
                        "evidence_root_id": "window_c",
                        "authenticated_basis": {
                            "kind": "floor_component_campaign_log_sha256",
                            "sha256s": ["f" * 64],
                        },
                        "raw_count": 0,
                        "validated_count": 0,
                        "status": "clean",
                    },
                ),
            )
            floor_resolutions = [
                FloorResolution(
                    status="exact",
                    artifact_id=floor_artifact["artifact_id"],
                    artifact_sha256=floor_sha,
                    source_cell_ids=(condition_id,),
                    transport_group_id=None,
                    transport_rule_id=None,
                    floor_abs_j=0.5,
                    floor_cmp_j=1.0,
                    floor_gate_j=1.0,
                    reason_codes=(),
                )
                for condition_id in (
                    finalized["contrasts"][0]["condition_a_id"],
                    finalized["contrasts"][0]["condition_b_id"],
                )
            ]
            with (
                mock.patch(
                    "joulewise.analysis_engine.metric_value",
                    side_effect=lambda summary, metric: summary["test_value"],
                ),
                mock.patch(
                    "joulewise.analysis_engine.window_evidence_precheck",
                    return_value={"reasons": ()},
                ),
                mock.patch(
                    "joulewise.analysis_engine.governed_stochastic_variance",
                    return_value=([{"name": "idle", "variance": 0.0}], ()),
                ),
                mock.patch(
                    "joulewise.analysis_engine.deterministic_bounds",
                    return_value=(
                        {
                            "E_interpolation_joint_edge_bound_j": 0.05,
                            "E_clock_anchor_shift_bound_j": 0.10,
                        },
                        (),
                    ),
                ),
                mock.patch(
                    "joulewise.analysis_engine._resolve_contrast_floor",
                    return_value=floor_resolutions,
                ),
                mock.patch(
                    "joulewise.analysis_engine.load_analysis_inputs",
                    return_value=loaded_inputs,
                ),
            ):
                artifact = analyze_claims(
                    finalized_path,
                    fixture["runs_root"],
                    fixture["floor_path"],
                    strict_validator=lambda path, strict=True: [],
                )

        self.assertEqual(
            [row["contrast_id"] for row in artifact["contrasts"]],
            [row["contrast_id"] for row in finalized["contrasts"]],
        )
        self.assertEqual(len(artifact["contrasts"]), 2)
        self.assertEqual(len(artifact["families"]), 1)
        self.assertEqual(artifact["families"][0]["m"], 2)
        self.assertEqual(
            validate_claim_verdicts(
                artifact,
                frozen_manifest=finalized,
            ),
            [],
        )
        self.assertTrue(
            all(row["loo"]["status"] == "complete" for row in artifact["contrasts"])
        )
        first_omissions = [
            row["omitted_block_id"] for row in artifact["contrasts"][0]["loo"]["rows"]
        ]
        second_omissions = [
            row["omitted_block_id"] for row in artifact["contrasts"][1]["loo"]["rows"]
        ]
        self.assertEqual(len(first_omissions), 10)
        self.assertTrue(
            all(left != right for left, right in zip(first_omissions, second_omissions))
        )
        for omission_index in range(10):
            raw = {
                contrast["contrast_id"]: contrast["loo"]["rows"][omission_index][
                    "raw_p"
                ]
                for contrast in artifact["contrasts"]
            }
            adjusted = holm_adjust(raw, m=2)
            for contrast in artifact["contrasts"]:
                self.assertEqual(
                    contrast["loo"]["rows"][omission_index]["adjusted_p"],
                    adjusted[contrast["contrast_id"]],
                )

        family_drift = copy.deepcopy(artifact)
        family_drift["families"][0]["alpha"] = 0.01
        family_drift["claim_verdicts_id"] = calculate_claim_verdicts_id(
            family_drift
        )
        self.assertTrue(
            any(
                "frozen analysis-manifest family semantics" in error
                for error in validate_claim_verdicts(
                    family_drift,
                    frozen_manifest=finalized,
                )
            )
        )

    def test_governed_transport_finalizes_then_refuses_with_pending_ruling_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(
                Path(tmp),
                transport_mode="governed_transport",
            )
            finalized = finalize_prospective_analysis_manifest_v3(
                fixture["prospective_path"],
                plan_tree_path=fixture["plan_tree_path"],
                custody_root=fixture["root"],
                runs_root=fixture["runs_root"],
                whole_window_verdict_path=fixture["verdict_path"],
                bracket_binding_path=fixture["bracket_path"],
                calibration_ledger_path=fixture["ledger_path"],
                aggregate_floor_artifact_path=fixture["floor_path"],
                output_dir=fixture["root"],
            )
            finalized_path = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            self.assertTrue(
                all(
                    contrast["floor_dependency"]["transport"]["mode"]
                    == "governed_transport"
                    for contrast in finalized["contrasts"]
                )
            )
            with self.assertRaisesRegex(
                AnalysisInputError,
                TRANSPORT_RULING_PENDING_REFUSAL,
            ):
                analyze_claims(
                    finalized_path,
                    fixture["runs_root"],
                    fixture["floor_path"],
                    strict_validator=lambda path, strict=True: [],
                )

    def test_finalized_load_boundary_maps_wrong_typed_sites_to_closed_vocabulary(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            finalized = finalize_prospective_analysis_manifest_v3(
                fixture["prospective_path"],
                plan_tree_path=fixture["plan_tree_path"],
                custody_root=fixture["root"],
                runs_root=fixture["runs_root"],
                whole_window_verdict_path=fixture["verdict_path"],
                bracket_binding_path=fixture["bracket_path"],
                calibration_ledger_path=fixture["ledger_path"],
                aggregate_floor_artifact_path=fixture["floor_path"],
                output_dir=fixture["root"],
            )
            finalized_path = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            cases = {
                "lineage": {**finalized, "lineage": 7},
                "condition_families": {
                    **finalized,
                    "condition_families": 7,
                },
                "design": {**finalized, "design": 7},
                "replacement_policy": {
                    **finalized,
                    "replacement_policy": 7,
                },
                "arms": {**finalized, "arms": 7},
                "entries": {**finalized, "entries": 7},
                "blocks": {**finalized, "blocks": 7},
                "families": {**finalized, "families": 7},
                "contrasts": {**finalized, "contrasts": 7},
                "nested_multiplicity": {
                    **finalized,
                    "families": [
                        {**finalized["families"][0], "multiplicity": None},
                        *finalized["families"][1:],
                    ],
                },
                "nested_evidence": {
                    **finalized,
                    "evidence": {
                        **finalized["evidence"],
                        "bracket_binding": False,
                    },
                },
                "finalization_contract": {
                    **finalized,
                    "finalization_contract": 7,
                },
                "evidence": {**finalized, "evidence": 7},
            }
            for label, candidate in cases.items():
                with self.subTest(label=label):
                    finalized_path.write_text(
                        json.dumps(candidate, indent=2, sort_keys=True) + "\n"
                    )
                    with self.assertRaises(AnalysisInputError) as raised:
                        load_manifest(finalized_path)
                    self.assertIn(
                        FINALIZED_MALFORMED_VALUE_CODE,
                        str(raised.exception),
                    )
                    self.assertIn("manifest.", str(raised.exception))
                    self.assertIsNotNone(raised.exception.__cause__)
                    self.assertIsInstance(
                        raised.exception.__cause__.__cause__, TypeError
                    )

    def test_finalized_load_boundary_classifies_internal_helper_failures(self):
        self.assertNotEqual(
            FINALIZED_MALFORMED_VALUE_CODE,
            FINALIZED_INTERNAL_ERROR_CODE,
        )
        self.assertIn(FINALIZED_MALFORMED_VALUE_CODE, FINALIZED_REFUSAL_CODES)
        self.assertIn(FINALIZED_INTERNAL_ERROR_CODE, FINALIZED_REFUSAL_CODES)
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            finalize_prospective_analysis_manifest_v3(
                fixture["prospective_path"],
                plan_tree_path=fixture["plan_tree_path"],
                custody_root=fixture["root"],
                runs_root=fixture["runs_root"],
                whole_window_verdict_path=fixture["verdict_path"],
                bracket_binding_path=fixture["bracket_path"],
                calibration_ledger_path=fixture["ledger_path"],
                aggregate_floor_artifact_path=fixture["floor_path"],
                output_dir=fixture["root"],
            )
            finalized_path = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            for exception_type in (RuntimeError, TypeError):
                injected = exception_type("injected validator defect")
                with self.subTest(exception_type=exception_type.__name__), mock.patch(
                    "joulewise.analysis_manifest_v3."
                    "analysis_semantics_sha256_v1",
                    side_effect=injected,
                ):
                    with self.assertRaises(AnalysisInputError) as raised:
                        load_manifest(finalized_path)
                    self.assertIn(
                        FINALIZED_INTERNAL_ERROR_CODE,
                        str(raised.exception),
                    )
                    self.assertNotIn(
                        FINALIZED_MALFORMED_VALUE_CODE,
                        str(raised.exception),
                    )
                    self.assertIn(exception_type.__name__, str(raised.exception))
                    self.assertIs(raised.exception.__cause__, injected)

    def test_authenticated_nested_bundle_conflicts_with_run_id_rejoin(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            runs = fixture["runs_root"]
            campaign_manifest_path = (
                runs / "campaign_manifests" / "synthetic.json"
            )
            campaign_manifest = json.loads(
                campaign_manifest_path.read_text()
            )
            selected_ids = sorted(
                member["bundle_ids"][0]
                for member in campaign_manifest["members"]
            )
            target_id = selected_ids[2]
            nested = runs / "nested" / target_id
            nested.parent.mkdir()
            shutil.move(str(runs / target_id), nested)

            ledger_path = runs / "selection" / "attempt_ledger.jsonl"
            ledger_path.parent.mkdir()
            ledger_path.write_text('{"authenticated":"fixture"}\n')
            selection = {
                "schema_version": "joulewise.attempt_ledger_selection.v1",
                "attempt_ledger_path": ledger_path.relative_to(runs).as_posix(),
                "attempt_ledger_sha256": hashlib.sha256(
                    ledger_path.read_bytes()
                ).hexdigest(),
                "selected_bundle_ids": selected_ids,
                "selected_membership_sha256": hashlib.sha256(
                    json.dumps(
                        selected_ids,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode()
                ).hexdigest(),
                "selected_bundles": [
                    {
                        "bundle_id": bundle_id,
                        "path": (
                            nested.relative_to(runs).as_posix()
                            if bundle_id == target_id
                            else bundle_id
                        ),
                    }
                    for bundle_id in selected_ids
                ],
                "quarantined_attempts": [],
            }
            selection_manifest = {
                "schema_version": "joulewise.campaign_provenance.v1",
                "analysis_manifest_id": fixture["prospective"]["manifest_id"],
                "campaign_policy": campaign_manifest["campaign_policy"],
                "attempt_ledger_selection": selection,
                "members": [],
            }
            (runs / "campaign_manifests" / "selection.json").write_text(
                json.dumps(selection_manifest, indent=2, sort_keys=True) + "\n"
            )
            (runs / "campaign_log.jsonl").write_text("")
            policy_path = (
                ROOT
                / "configs"
                / "campaign_policies"
                / "quiet_mac_p2_production.json"
            )
            writer_args = run_campaign_module.parse_args(
                [
                    "--whole-window-verdict",
                    "--runs-dir",
                    str(runs),
                    "--campaign-policy",
                    str(policy_path),
                    "--neg8-drift-bound",
                    str(fixture["root"] / "neg8_drift_bound.json"),
                ]
            )
            with (
                mock.patch.object(
                    run_campaign_module,
                    "validated_attempt_selection",
                    return_value=set(selected_ids),
                ),
                mock.patch.object(
                    run_campaign_module, "validate_bundle", return_value=[]
                ),
                mock.patch.object(
                    run_campaign_module,
                    "_final_idle_admission_attempt",
                    return_value=1,
                ),
                mock.patch.object(
                    run_campaign_module,
                    "_load_idle_rich_telemetry",
                    return_value=[],
                ),
                mock.patch.object(
                    run_campaign_module,
                    "post_run_environment_refusals",
                    return_value=(),
                ),
                mock.patch.object(
                    run_campaign_module,
                    "evaluate_cpu_idle_admission",
                    return_value={"decision": "admitted", "conditions": []},
                ),
                mock.patch.object(
                    run_campaign_module,
                    "_adapter_observations_for",
                    return_value=[],
                ),
                mock.patch.object(
                    run_campaign_module,
                    "evaluate_adapter_wattage_continuity",
                    return_value={
                        "schema_version": ADAPTER_CONTINUITY_SCHEMA,
                        "decision": "stable",
                        "conditions": [],
                    },
                ),
                mock.patch.object(
                    run_campaign_module,
                    "_neg8_reference_scientific_config_sha256",
                    return_value="8" * 64,
                ),
                mock.patch.object(
                    run_campaign_module,
                    "calibration_bracket_for_bundles",
                    return_value=(
                        {
                            "schema_version": (
                                "joulewise.instrument_calibration_bracket.v1"
                            ),
                            "status": "passed",
                            "b_fiducial_s": 0.025,
                        },
                        (),
                    ),
                ),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(
                    run_campaign_module.run_whole_window_verdict(writer_args),
                    0,
                )
            verdict = read_all_jsonl(runs / "campaign_log.jsonl")[-1]
            occurrence = next(
                row
                for row in verdict["evaluation_basis"]["member_occurrences"]
                if row["bundle_id"] == target_id
            )
            self.assertEqual(
                occurrence["bundle_path"], f"nested/{target_id}"
            )
            fixture["verdict_path"].write_text(
                json.dumps(verdict, indent=2, sort_keys=True) + "\n"
            )
            with mock.patch(
                "joulewise.whole_window.validated_attempt_selection",
                return_value=set(selected_ids),
            ), mock.patch(
                "joulewise.whole_window.whole_window_refusal_reasons",
                return_value=(),
            ):
                finalized = finalize_prospective_analysis_manifest_v3(
                    fixture["prospective_path"],
                    plan_tree_path=fixture["plan_tree_path"],
                    custody_root=fixture["root"],
                    runs_root=runs,
                    whole_window_verdict_path=fixture["verdict_path"],
                    bracket_binding_path=fixture["bracket_path"],
                    calibration_ledger_path=fixture["ledger_path"],
                    aggregate_floor_artifact_path=fixture["floor_path"],
                    output_dir=fixture["root"],
                )
            finalized_path = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            finalized_entry = next(
                entry
                for entry in finalized["entries"]
                if entry["run_id"] == target_id
            )
            self.assertEqual(
                finalized_entry["bundle_path"], f"nested/{target_id}"
            )

            shutil.copytree(nested, runs / target_id)
            with (
                mock.patch(
                    "joulewise.whole_window.validated_attempt_selection",
                    return_value=set(selected_ids),
                ),
                mock.patch(
                    "joulewise.whole_window.whole_window_refusal_reasons",
                    return_value=(),
                ),
                self.assertRaisesRegex(
                    AnalysisInputError,
                    "analysis_manifest_bundle_path_divergence",
                ),
            ):
                load_analysis_inputs(
                    finalized_path,
                    runs,
                    fixture["floor_path"],
                    strict_validator=lambda path, strict=True: [],
                )

    def test_consumer_rejects_symlink_and_nonregular_manifest_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.json"
            target.write_text("{}\n")
            alias = root / "alias.json"
            alias.symlink_to(target.name)
            with self.assertRaisesRegex(
                AnalysisInputError,
                "path_resolution_refused",
            ):
                load_manifest(alias)
            directory = root / "manifest-directory"
            directory.mkdir()
            with self.assertRaisesRegex(
                AnalysisInputError,
                "path_resolution_refused",
            ):
                load_manifest(directory)

    def _salvage_floor_dispatch_fixture(self, root: Path) -> tuple[dict, dict[str, Path]]:
        artifact = make_artifact()
        record = artifact["cells"][0]["absolute"]
        record["consumption_semantics_id"] = (
            SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
        )
        record["whole_window_evaluation_basis_sha256"] = "b" * 64
        record["whole_window_drift_allowance"][
            "whole_window_evaluation_basis_sha256"
        ] = "b" * 64
        self.assertEqual(validate_floor_artifact(artifact), [])
        roots = {"a10": root / "a10", "window_c": root / "window-c"}
        for value in roots.values():
            value.mkdir()
        return artifact, roots

    def test_b4_salvage_floor_binder_refuses_without_explicit_dispatch_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact, roots = self._salvage_floor_dispatch_fixture(root)
            binding = bind_floor_artifact_evidence(
                artifact,
                root / "floor.json",
                roots,
                strict_validator=lambda _path, _strict: (),
            )
        self.assertIn("salvage_floor_dispatch_required", binding.global_problems)
        self.assertFalse(binding.bound_cell_ids)

    def test_b4_salvage_floor_binder_rejects_mismatched_dispatch_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact, roots = self._salvage_floor_dispatch_fixture(root)
            binding = bind_floor_artifact_evidence(
                artifact,
                root / "floor.json",
                roots,
                strict_validator=lambda _path, _strict: (),
                consumption_semantics_id=(
                    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
                ),
                evaluation_basis_sha256="c" * 64,
            )
        self.assertIn("salvage_floor_dispatch_mismatch", binding.global_problems)
        self.assertFalse(binding.bound_cell_ids)

    def test_b4_salvage_floor_binder_accepts_correct_pair_after_real_row_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = make_artifact()
            record = artifact["cells"][0]["absolute"]
            record["consumption_semantics_id"] = (
                SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
            )
            ordinary_ids = tuple(
                row["bundle_id"] for row in record["bundle_observations"]
            )
            roots = {"a10": root / "a10", "window_c": root / "window-c"}
            roots["window_c"].mkdir()
            args, _failed, _bundle_ids = install_real_salvage_window(
                roots["a10"], ordinary_bundle_ids=ordinary_ids
            )
            with d100_real_salvage_leaf_patches(), redirect_stdout(io.StringIO()):
                self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 0)
                row = read_all_jsonl(roots["a10"] / "campaign_log.jsonl")[-1]
                basis_sha256 = row["evaluation_basis"]["sha256"]
                record["whole_window_evaluation_basis_sha256"] = basis_sha256
                record["whole_window_drift_allowance"][
                    "whole_window_evaluation_basis_sha256"
                ] = basis_sha256
                self.assertEqual(validate_floor_artifact(artifact), [])
                binding = bind_floor_artifact_evidence(
                    artifact,
                    root / "floor.json",
                    roots,
                    strict_validator=lambda _path, _strict: (),
                    consumption_semantics_id=(
                        SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
                    ),
                    evaluation_basis_sha256=basis_sha256,
                )
        self.assertNotIn("salvage_floor_dispatch_required", binding.global_problems)
        self.assertNotIn("salvage_floor_dispatch_mismatch", binding.global_problems)
        self.assertFalse(
            any(
                problem.startswith("salvage_floor_verdict_revalidation_failed")
                for problem in binding.global_problems
            )
        )

    def test_holm_m1_is_identity_and_keeps_the_registered_denominator(self):
        self.assertEqual(holm_adjust({"only-contrast": 0.04}, m=1), {"only-contrast": 0.04})
        self.assertEqual(holm_adjust({"only-contrast": None}, m=1), {"only-contrast": None})
        with self.assertRaises(ValueError):
            holm_adjust({"only-contrast": 0.04}, m=2)

    def test_v3_abba_engine_and_d093_refusal_precedence(self):
        clean = _v3_fixture_artifact()
        refused = _v3_fixture_artifact(diverged=True)

        self.assertEqual(validate_claim_verdicts(clean), [])
        manifest = json.loads(
            (
                ROOT
                / "configs"
                / "campaigns"
                / "splitwise_decode_v1"
                / "analysis_manifest_v3.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            validate_claim_verdicts(clean, frozen_manifest=manifest), []
        )
        self.assertEqual(
            clean["claim_verdicts_id"],
            "cv-97532d73a9889e34caab780a64435cda3c9d11ea7e708b1234d4c5ad68ce07e0",
        )
        self.assertEqual(
            hashlib.sha256(render_claim_verdicts(clean)).hexdigest(),
            "5e8e93e8f3106ec7637baebb0b43ee87f1fda2ba74ed61d1b931893d51a73fe7",
        )
        arm_by_entry = {
            entry["entry_id"]: entry["arm_id"] for entry in manifest["entries"]
        }
        for audit in clean["bundle_audit"]:
            arm_id = arm_by_entry[audit["entry_id"]]
            self.assertIsNotNone(audit["scientific_identity"])
            self.assertEqual(
                normalized_realized_stack_identity(audit["scientific_identity"]),
                normalized_realized_stack_identity(
                    ARM_FREEZE[arm_id]["realized_stack_identity"]
                ),
            )
        contrast = clean["contrasts"][0]
        self.assertEqual(contrast["estimator"]["name"], "abba_block_arm_mean_difference_t_v1")
        self.assertEqual(contrast["estimator"]["estimate"], 10.0)
        self.assertAlmostEqual(contrast["deterministic_bounds"]["total"], 0.3)
        self.assertEqual(contrast["floor"]["active_floor_j"], 1.2)
        self.assertEqual(contrast["floor"]["aggregation"], "max_never_sum")
        self.assertEqual(len(contrast["bundle_blocks"]["included_bundle_ids"]), 40)
        self.assertTrue(
            all(
                set(block["position_bundle_ids"]) == {"A1", "B1", "B2", "A2"}
                for block in contrast["bundle_blocks"]["blocks"]
            )
        )

        self.assertEqual(validate_claim_verdicts(refused), [])
        refused_contrast = refused["contrasts"][0]
        self.assertEqual(refused["supersession_audit"][0]["status"], "refused")
        self.assertEqual(refused_contrast["estimator"]["n"], 0)
        self.assertEqual(refused_contrast["bundle_blocks"]["included_bundle_ids"], [])
        self.assertIn(
            "whole_window_verdict_conflict",
            refused_contrast["claim_evaluation"]["reason_codes"],
        )

    def test_supersession_audit_valid_finding_validates_after_persistence(self):
        artifact = _v3_supersession_finding_artifact()
        persisted = json.loads(render_claim_verdicts(artifact))
        self.assertEqual(validate_claim_verdicts(persisted), [])

    def test_supersession_audit_finding_unknown_key_refuses(self):
        artifact = _v3_supersession_finding_artifact()
        artifact["supersession_audit"][0]["findings"][0]["detail"] = "extra"
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        errors = validate_claim_verdicts(artifact)
        self.assertTrue(
            any("unrecognized key(s): detail" in error for error in errors),
            errors,
        )

    def test_supersession_audit_finding_unknown_reason_refuses(self):
        artifact = _v3_supersession_finding_artifact()
        artifact["supersession_audit"][0]["findings"][0][
            "reason_code"
        ] = "unruled_reason"
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        errors = validate_claim_verdicts(artifact)
        self.assertTrue(
            any("findings[0].reason_code: invalid" in error for error in errors),
            errors,
        )

    def test_supersession_audit_finding_empty_bundle_ids_refuses(self):
        artifact = _v3_supersession_finding_artifact()
        artifact["supersession_audit"][0]["findings"][0]["bundle_ids"] = []
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        errors = validate_claim_verdicts(artifact)
        self.assertTrue(
            any(
                "bundle_ids: must be a nonempty array of nonempty strings"
                in error
                for error in errors
            ),
            errors,
        )

    def test_supersession_audit_finding_duplicate_bundle_ids_refuses(self):
        artifact = _v3_supersession_finding_artifact()
        artifact["supersession_audit"][0]["findings"][0]["bundle_ids"] = [
            "bundle-a",
            "bundle-a",
        ]
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        errors = validate_claim_verdicts(artifact)
        self.assertTrue(
            any(
                "bundle_ids: must be sorted and duplicate-free" in error
                for error in errors
            ),
            errors,
        )

    def test_supersession_audit_finding_unsorted_bundle_ids_refuses(self):
        artifact = _v3_supersession_finding_artifact()
        artifact["supersession_audit"][0]["findings"][0]["bundle_ids"] = [
            "bundle-z",
            "bundle-a",
        ]
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        errors = validate_claim_verdicts(artifact)
        self.assertTrue(
            any(
                "bundle_ids: must be sorted and duplicate-free" in error
                for error in errors
            ),
            errors,
        )

    def test_supersession_audit_clean_row_with_findings_refuses(self):
        artifact = _v3_fixture_artifact()
        artifact["supersession_audit"][0]["findings"] = [
            {
                "reason_code": (
                    REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS
                ),
                "bundle_ids": ["bundle-a"],
            }
        ]
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        errors = validate_claim_verdicts(artifact)
        self.assertTrue(
            any(
                "findings: only a refused row may carry findings" in error
                for error in errors
            ),
            errors,
        )

    def test_supersession_audit_equal_authenticated_refusal_without_findings_refuses(
        self,
    ):
        artifact = _v3_fixture_artifact(diverged=True)
        audit = artifact["supersession_audit"][0]
        audit["validated_count"] = audit["raw_count"]
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        errors = validate_claim_verdicts(artifact)
        self.assertTrue(
            any(
                "authenticated equal counts cannot be refused" in error
                for error in errors
            ),
            errors,
        )

    def test_v3_requires_scan_row_for_every_declared_floor_root(self):
        artifact = _v3_fixture_artifact()
        stripped = copy.deepcopy(artifact)
        stripped["supersession_audit"] = [
            row
            for row in stripped["supersession_audit"]
            if row["scope"] != "floor_evidence"
        ]
        stripped["claim_verdicts_id"] = calculate_claim_verdicts_id(stripped)

        errors = validate_claim_verdicts(stripped)

        self.assertTrue(
            any(
                "missing floor-evidence scan row(s): a10, window_c" in error
                for error in errors
            ),
            errors,
        )

    def test_v3_zero_root_coordinated_attack_refuses(self):
        attacked = copy.deepcopy(_v3_fixture_artifact())
        attacked["inputs"]["floor_artifact"]["evidence_root_ids"] = []
        attacked["supersession_audit"] = [
            row
            for row in attacked["supersession_audit"]
            if row["scope"] == "analysis_corpus"
        ]
        attacked["claim_verdicts_id"] = calculate_claim_verdicts_id(attacked)

        errors = validate_claim_verdicts(attacked)

        self.assertTrue(
            any("unrecognized key(s): evidence_root_ids" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any(
                "missing floor-evidence scan row(s): a10, window_c" in error
                for error in errors
            ),
            errors,
        )

    def test_v3_missing_real_root_decoy_attack_refuses(self):
        attacked = copy.deepcopy(_v3_fixture_artifact())
        attacked["inputs"]["floor_artifact"]["evidence_root_ids"] = ["decoy"]
        attacked["supersession_audit"] = [
            row
            for row in attacked["supersession_audit"]
            if row["scope"] == "analysis_corpus"
        ]
        attacked["supersession_audit"].append(
            {
                "scope": "floor_evidence",
                "evidence_root_id": "decoy",
                "authenticated_basis": {
                    "kind": "floor_component_campaign_log_sha256",
                    "sha256s": ["e" * 64],
                },
                "raw_count": 0,
                "validated_count": 0,
                "status": "clean",
            }
        )
        attacked["claim_verdicts_id"] = calculate_claim_verdicts_id(attacked)

        errors = validate_claim_verdicts(attacked)

        self.assertTrue(
            any("unrecognized key(s): evidence_root_ids" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any(
                "missing floor-evidence scan row(s): a10, window_c" in error
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any("unexpected floor-evidence scan row(s): decoy" in error for error in errors),
            errors,
        )

    def test_v3_embedded_floor_bytes_are_hash_and_schema_bound(self):
        artifact = _v3_fixture_artifact()

        hash_mismatch = copy.deepcopy(artifact)
        hash_mismatch["inputs"]["floor_artifact"]["embedded_bytes_base64"] = (
            base64.b64encode(b"{}").decode("ascii")
        )
        hash_mismatch["claim_verdicts_id"] = calculate_claim_verdicts_id(
            hash_mismatch
        )
        hash_errors = validate_claim_verdicts(hash_mismatch)
        self.assertTrue(
            any("sha256 does not match bound file_sha256" in error for error in hash_errors),
            hash_errors,
        )

        invalid_floor = copy.deepcopy(hash_mismatch)
        invalid_floor["inputs"]["floor_artifact"]["file_sha256"] = hashlib.sha256(
            b"{}"
        ).hexdigest()
        invalid_floor["claim_verdicts_id"] = calculate_claim_verdicts_id(
            invalid_floor
        )
        schema_errors = validate_claim_verdicts(invalid_floor)
        self.assertTrue(
            any("invalid floor artifact" in error for error in schema_errors),
            schema_errors,
        )

    def test_supersession_authenticated_basis_kind_is_scope_bound(self):
        artifact = _v3_fixture_artifact()
        floor_misbound = copy.deepcopy(artifact)
        floor_row = next(
            row
            for row in floor_misbound["supersession_audit"]
            if row["scope"] == "floor_evidence"
        )
        floor_row["authenticated_basis"] = {
            "kind": "analysis_manifest_file_sha256",
            "sha256": "f" * 64,
        }
        floor_misbound["claim_verdicts_id"] = calculate_claim_verdicts_id(
            floor_misbound
        )
        self.assertTrue(
            any(
                "authenticated_basis: invalid or unauthenticated" in error
                for error in validate_claim_verdicts(floor_misbound)
            )
        )

        corpus_misbound = copy.deepcopy(artifact)
        corpus_row = next(
            row
            for row in corpus_misbound["supersession_audit"]
            if row["scope"] == "analysis_corpus"
        )
        corpus_row["authenticated_basis"] = {
            "kind": "floor_component_campaign_log_sha256",
            "sha256s": ["f" * 64],
        }
        corpus_misbound["claim_verdicts_id"] = calculate_claim_verdicts_id(
            corpus_misbound
        )
        self.assertTrue(
            any(
                "authenticated_basis: invalid or unauthenticated" in error
                for error in validate_claim_verdicts(corpus_misbound)
            )
        )

    def test_v3_excluded_position_diagnostic_names_physical_abba_slot(self):
        artifact = _v3_fixture_artifact()
        first_block = artifact["contrasts"][0]["bundle_blocks"]["blocks"][0]
        a1_bundle_id = first_block["position_bundle_ids"]["A1"]
        audit = next(
            row for row in artifact["bundle_audit"] if row["bundle_id"] == a1_bundle_id
        )
        audit["inclusion_status"] = "excluded"
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)

        errors = validate_claim_verdicts(artifact)

        self.assertTrue(
            any(
                ".position_bundle_ids.A1: included block requires included audit evidence"
                in error
                for error in errors
            ),
            errors,
        )
        self.assertFalse(
            any(
                ".bundle_b_id: included block requires included audit evidence" in error
                for error in errors
            ),
            errors,
        )

    @classmethod
    def setUpClass(cls):
        cls._temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls._temporary.name)
        cls.config_dir = cls.root / "configs"
        cls.runs_root = cls.root / "runs"
        cls.floor_path = cls.root / "floor.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = generate_matrix(
                [
                    "--base",
                    str(BASE_CONFIG),
                    "--model-tag",
                    "mock-model",
                    "--out-dir",
                    str(cls.config_dir),
                ]
            )
        if code != 0:
            raise AssertionError(f"matrix generation failed: {code}")
        with mock.patch(
            "joulewise.bundle._capture_source_state",
            return_value=dict(CLEAN_SOURCE_STATE),
        ):
            for config in sorted(cls.config_dir.glob("*.json")):
                if config.name in SIDECARS:
                    continue
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    code = main(["run", str(config), "--runs-dir", str(cls.runs_root)])
                if code != 0:
                    raise AssertionError(f"mock run failed for {config.name}: {code}")
                run_id = json.loads(config.read_text(encoding="utf-8"))["run_id"]
                install_explicit_mock_sampler(cls.runs_root / run_id)
        cls.floor_path.write_text(
            json.dumps(make_artifact(), indent=2) + "\n", encoding="utf-8"
        )
        cls.manifest_path = cls.config_dir / "analysis_manifest.json"
        manifest = json.loads(cls.manifest_path.read_text())
        bundle_ids = sorted(entry["run_id"] for entry in manifest["entries"])
        install_passing_analysis_whole_window(
            cls.runs_root,
            bundle_ids,
            source_name="analysis-whole-window-source",
        )

    @classmethod
    def tearDownClass(cls):
        cls._temporary.cleanup()

    @staticmethod
    def _canonical_model_bytes(model: dict) -> bytes:
        return json.dumps(
            model,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def test_real_controller_unpinned_model_is_included_by_loader(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = manifest["entries"][0]

        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
            loaded = load_analysis_inputs(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
            )

        evidence = loaded.registered[target["entry_id"]]
        self.assertEqual(
            set(evidence.raw_config["model"]),
            {
                "name",
                "family",
                "source",
                "revision",
                "weight_format",
                "context_window",
            },
        )
        self.assertEqual(evidence.inclusion_status, "included")
        self.assertNotIn("config_hash_mismatch", evidence.base_reason_codes)

    def test_real_controller_pinned_model_matches_canonical_bytes_and_is_included(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
            base["model"].update(
                tokenizer_json_sha256="a" * 64,
                chat_template_sha256="b" * 64,
            )
            base_path = root / "pinned-base.json"
            base_path.write_text(
                json.dumps(base, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            config_dir = root / "configs"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = generate_matrix(
                    [
                        "--base",
                        str(base_path),
                        "--model-tag",
                        "mock-model",
                        "--out-dir",
                        str(config_dir),
                    ]
                )
            self.assertEqual(code, 0)

            runs_root = root / "runs"
            for config_path in sorted(config_dir.glob("*.json")):
                if config_path.name in SIDECARS:
                    continue
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    code = main(
                        ["run", str(config_path), "--runs-dir", str(runs_root)]
                    )
                self.assertEqual(code, 0, config_path.name)
                run_id = json.loads(config_path.read_text(encoding="utf-8"))[
                    "run_id"
                ]
                install_explicit_mock_sampler(runs_root / run_id)

            manifest_path = config_dir / "analysis_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            bundle_ids = sorted(entry["run_id"] for entry in manifest["entries"])
            install_passing_analysis_whole_window(
                runs_root,
                bundle_ids,
                source_name="pinned-controller-loader-source",
            )
            with mock.patch(
                "joulewise.analysis_engine.inputs.custody_telemetry_identity",
                return_value=PRODUCTION_TELEMETRY_IDENTITY,
            ):
                loaded = load_analysis_inputs(
                    manifest_path,
                    runs_root,
                    self.floor_path,
                    strict_validator=validate_bundle,
                )

            target = manifest["entries"][0]
            evidence = loaded.registered[target["entry_id"]]
            config_model = evidence.raw_config["model"]
            metadata_model = evidence.metadata["model"]
            self.assertEqual(
                self._canonical_model_bytes(metadata_model),
                self._canonical_model_bytes(config_model),
            )
            self.assertEqual(config_model["tokenizer_json_sha256"], "a" * 64)
            self.assertEqual(config_model["chat_template_sha256"], "b" * 64)
            self.assertEqual(evidence.inclusion_status, "included")
            self.assertNotIn("config_hash_mismatch", evidence.base_reason_codes)

    def test_old_asdict_model_emission_is_rejected_at_controller_loader_seam(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_root = root / "runs"
            shutil.copytree(self.config_dir, config_dir)
            shutil.copytree(self.runs_root, runs_root)
            manifest_path = config_dir / "analysis_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            target = manifest["entries"][0]
            shutil.rmtree(runs_root / target["run_id"])

            canonical_to_dict = BenchmarkConfig.to_dict
            canonical_write_metadata = controller_module._Execution._write_metadata

            def old_asdict_write_metadata(execution):
                def metadata_only_asdict(config):
                    data = canonical_to_dict(config)
                    data["model"] = asdict(config.model)
                    return data

                with mock.patch.object(
                    BenchmarkConfig,
                    "to_dict",
                    metadata_only_asdict,
                ):
                    return canonical_write_metadata(execution)

            with mock.patch.object(
                controller_module._Execution,
                "_write_metadata",
                old_asdict_write_metadata,
            ):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    code = main(
                        [
                            "run",
                            str(config_dir / target["config"]),
                            "--runs-dir",
                            str(runs_root),
                        ]
                    )
            self.assertEqual(code, 0)
            install_explicit_mock_sampler(runs_root / target["run_id"])

            with mock.patch(
                "joulewise.analysis_engine.inputs.custody_telemetry_identity",
                return_value=PRODUCTION_TELEMETRY_IDENTITY,
            ):
                loaded = load_analysis_inputs(
                    manifest_path,
                    runs_root,
                    self.floor_path,
                    strict_validator=validate_bundle,
                )

            evidence = loaded.registered[target["entry_id"]]
            self.assertNotIn("tokenizer_json_sha256", evidence.raw_config["model"])
            self.assertNotIn("chat_template_sha256", evidence.raw_config["model"])
            self.assertIsNone(evidence.metadata["model"]["tokenizer_json_sha256"])
            self.assertIsNone(evidence.metadata["model"]["chat_template_sha256"])
            self.assertEqual(evidence.inclusion_status, "excluded")
            self.assertIn("config_hash_mismatch", evidence.base_reason_codes)

    def test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact(self):
        first = analyze_claims(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        second = analyze_claims(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertEqual(first, second)
        self.assertEqual(render_claim_verdicts(first), render_claim_verdicts(second))
        self.assertEqual(len(first["bundle_audit"]), 30)
        self.assertTrue(all(row["strict_status"] == "valid" for row in first["bundle_audit"]))
        self.assertTrue(
            all(
                row["inclusion_status"] == "excluded"
                and MOCK_TELEMETRY_CLAIM_REFUSAL in row["base_reason_codes"]
                for row in first["bundle_audit"]
            )
        )
        self.assertEqual(len(first["families"]), 4)
        self.assertEqual(len(first["contrasts"]), 24)
        for contrast in first["contrasts"]:
            with self.subTest(contrast=contrast["contrast_id"]):
                evaluation = contrast["claim_evaluation"]
                self.assertEqual(evaluation["outcome"], "not_estimable")
                self.assertFalse(evaluation["claim_ready_for_l2_l3"])
                self.assertIn(
                    MOCK_TELEMETRY_CLAIM_REFUSAL,
                    evaluation["reason_codes"],
                )
                # Reducer 0.4.2 supplies the governed precheck, so its
                # absence reason must NOT appear; the remaining fail-closed
                # reasons keep the mock campaign terminally ineligible.
                self.assertNotIn(
                    "window_evidence_precheck_missing", evaluation["reason_codes"]
                )

                self.assertIn(
                    "campaign_cooldown_evidence_missing", evaluation["reason_codes"]
                )
                self.assertIn("floor_transport_inapplicable", evaluation["reason_codes"])
                self.assertNotIn("loo_magnitude_influential", evaluation["reason_codes"])
                self.assertEqual(contrast["estimator"]["n"], 0)
                self.assertIsNone(contrast["estimator"]["df"])
                self.assertEqual(
                    contrast["loo"],
                    {"status": "not_run", "rows": []},
                )
                self.assertNotIn("floor_limit_class", contrast["floor"])
                self.assertNotIn("floor_limit", evaluation)
                self.assertTrue(
                    all(
                        "floor_limit_class" not in resolution
                        for resolution in contrast["floor"]["resolutions"]
                    )
                )
        self.assertEqual(validate_claim_verdicts(first), [])

    def test_v1_claim_consumption_records_and_requires_d093_counts(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["schema_version"],
            "joulewise.analysis_manifest.v1",
        )
        artifact = analyze_claims(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertEqual(validate_claim_verdicts(artifact), [])
        self.assertTrue(artifact["supersession_audit"])
        for row in artifact["supersession_audit"]:
            self.assertIsInstance(row["raw_count"], int)
            self.assertIsInstance(row["validated_count"], int)
            self.assertEqual(row["raw_count"], row["validated_count"])

        omitted = copy.deepcopy(artifact)
        del omitted["supersession_audit"]
        omitted["claim_verdicts_id"] = calculate_claim_verdicts_id(omitted)
        errors = validate_claim_verdicts(omitted)
        self.assertTrue(
            any(
                "every claim consumption requires the pre-estimation D-093 scan record"
                in error
                for error in errors
            ),
            errors,
        )

    def test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity(
        self,
    ):
        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
            first = analyze_claims(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
            )
            second = analyze_claims(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
            )
        self.assertEqual(first, second)
        self.assertEqual(render_claim_verdicts(first), render_claim_verdicts(second))
        self.assertEqual(len(first["bundle_audit"]), 30)
        self.assertTrue(
            all(row["strict_status"] == "valid" for row in first["bundle_audit"])
        )
        self.assertEqual(len(first["families"]), 4)
        self.assertEqual(len(first["contrasts"]), 24)
        for contrast in first["contrasts"]:
            with self.subTest(contrast=contrast["contrast_id"]):
                evaluation = contrast["claim_evaluation"]
                self.assertEqual(evaluation["outcome"], "not_resolvable")
                self.assertFalse(evaluation["claim_ready_for_l2_l3"])
                self.assertNotIn(
                    "window_evidence_precheck_missing", evaluation["reason_codes"]
                )
                self.assertIn(
                    "campaign_cooldown_evidence_missing", evaluation["reason_codes"]
                )
                self.assertIn(
                    "floor_transport_inapplicable", evaluation["reason_codes"]
                )
                self.assertNotIn(
                    "loo_magnitude_influential", evaluation["reason_codes"]
                )
                self.assertEqual(contrast["estimator"]["n"], 5)
                self.assertEqual(contrast["estimator"]["df"], 4)
                self.assertEqual(len(contrast["loo"]["rows"]), 5)
                self.assertTrue(
                    all(
                        "estimate_magnitude" not in row["influence_triggers"]
                        for row in contrast["loo"]["rows"]
                    )
                )
        by_id = {
            contrast["contrast_id"]: contrast for contrast in first["contrasts"]
        }
        for family in first["families"]:
            for omission_index in range(5):
                raw = {
                    contrast_id: by_id[contrast_id]["loo"]["rows"][
                        omission_index
                    ]["raw_p"]
                    for contrast_id in family["contrast_ids"]
                }
                adjusted = holm_adjust(raw, m=family["m"])
                for contrast_id in family["contrast_ids"]:
                    self.assertEqual(
                        by_id[contrast_id]["loo"]["rows"][omission_index][
                            "adjusted_p"
                        ],
                        adjusted[contrast_id],
                    )
        omitted_loo = json.loads(json.dumps(first))
        omitted_loo["contrasts"][0]["loo"] = {"status": "not_run", "rows": []}
        omitted_loo["claim_verdicts_id"] = calculate_claim_verdicts_id(
            omitted_loo
        )
        self.assertTrue(validate_claim_verdicts(omitted_loo))

    def test_attribution_limited_floor_is_claim_bearing_in_final_artifact(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = manifest["contrasts"][0]
        selector = target["floor_selector"]
        condition_ids = selector["condition_family_ids"]
        cells = [
            make_cell(
                cell_id=f"attribution-{condition_id}",
                condition=condition_id,
                energies=[0.0] * 5,
                deltas=[0.0] * 5,
                absolute_half_widths=[0.5] * 5,
                comparative_half_widths=[0.5] * 5,
            )
            for condition_id in condition_ids
        ]
        for cell in cells:
            cell["key"].update(
                backend="powermetrics",
                metric=selector["metric"],
                window_class=selector["window_class"],
            )
            cell["transport_group_id"] = "tg-analysis-attribution"
        group = build_transport_group(
            transport_group_id="tg-analysis-attribution",
            backend="powermetrics",
            metric=selector["metric"],
            window_class=selector["window_class"],
            stack_identity=cells[0]["source_regime"]["stack_identity"],
            source_cells=cells,
            allowed_consumer_condition_families=[
                {
                    key: cell["key"][key]
                    for key in (
                        "condition_family_id",
                        "condition_family_definition",
                        "condition_family_sha256",
                    )
                }
                for cell in cells
            ],
        )
        floor_artifact = build_floor_artifact(
            artifact_id="analysis-attribution-floor",
            calibration_scope="window_a",
            source_class="synthetic",
            provenance=make_artifact()["provenance"],
            cells=cells,
            transport_groups=[group],
            idle_drift_guard={
                "calibration_status": "calibrated",
                "method": "p2_015_prediction_guard_v1",
                "guard_w": 0.25,
                "n_bundles": 2,
                "bundle_sha256": ["1" * 64, "2" * 64],
                "cell_id": cells[0]["cell_id"],
                "artifact_sha256": "3" * 64,
            },
        )
        self.assertEqual(validate_floor_artifact(floor_artifact), [])
        cells_by_condition = {
            cell["key"]["condition_family_id"]: cell for cell in cells
        }

        def labelled_floor_request(
            contrast, condition_id, rows, artifact
        ):
            del rows, artifact
            if contrast["contrast_id"] != target["contrast_id"]:
                return None
            cell = cells_by_condition[condition_id]
            return FloorRequest(
                backend=cell["key"]["backend"],
                metric=cell["key"]["metric"],
                window_class=cell["key"]["window_class"],
                condition_family_id=condition_id,
                condition_family_sha256=cell["key"][
                    "condition_family_sha256"
                ],
                stack_identity_sha256=cell["source_regime"][
                    "stack_identity_sha256"
                ],
                consumer_stress={},
            )

        with tempfile.TemporaryDirectory() as tmp:
            floor_path = Path(tmp) / "attribution-floor.json"
            floor_path.write_text(
                json.dumps(floor_artifact, indent=2) + "\n",
                encoding="utf-8",
            )
            artifact = analyze_claims(
                self.manifest_path,
                self.runs_root,
                floor_path,
                strict_validator=validate_bundle,
                _floor_request_factory=labelled_floor_request,
            )

        observed = next(
            contrast
            for contrast in artifact["contrasts"]
            if contrast["contrast_id"] == target["contrast_id"]
        )
        floor = observed["floor"]
        self.assertEqual(floor["status"], "resolved")
        self.assertEqual(
            floor["floor_limit_class"],
            ATTRIBUTION_LIMIT_CLASS,
        )
        self.assertEqual(floor["floor_source"], ATTRIBUTION_FLOOR_SOURCE)
        self.assertEqual(
            floor["single_count_discipline"],
            attribution_single_count_discipline(),
        )
        self.assertEqual(
            set(floor["point_floor_diagnostics"]),
            {cell["cell_id"] for cell in cells},
        )
        for resolution, cell in zip(
            floor["resolutions"], cells, strict=True
        ):
            self.assertEqual(resolution["status"], "exact")
            self.assertEqual(
                resolution["floor_gate_j"],
                cell["floor_gate_j"],
            )
            self.assertEqual(
                resolution["floor_limit_class"],
                ATTRIBUTION_LIMIT_CLASS,
            )
        expected_floor = max(cell["floor_gate_j"] for cell in cells)
        self.assertEqual(floor["active_floor_j"], expected_floor)
        evaluation = observed["claim_evaluation"]
        self.assertNotIn(
            "floor_transport_inapplicable",
            evaluation["reason_codes"],
        )
        self.assertEqual(
            evaluation["floor_limit"],
            {
                "floor_limit_class": ATTRIBUTION_LIMIT_CLASS,
                "floor_source": ATTRIBUTION_FLOOR_SOURCE,
                "published_floor_j": expected_floor,
                "point_floor_diagnostics": floor[
                    "point_floor_diagnostics"
                ],
                "single_count_discipline": (
                    attribution_single_count_discipline()
                ),
            },
        )
        self.assertEqual(validate_claim_verdicts(artifact), [])
        missing_single_count = json.loads(json.dumps(artifact))
        del missing_single_count["contrasts"][
            artifact["contrasts"].index(observed)
        ]["claim_evaluation"]["floor_limit"]["single_count_discipline"]
        missing_single_count["claim_verdicts_id"] = (
            calculate_claim_verdicts_id(missing_single_count)
        )
        self.assertTrue(
            any(
                "single_count_discipline" in error
                for error in validate_claim_verdicts(missing_single_count)
            )
        )

    def test_analysis_loader_refuses_when_whole_window_verdict_is_missing(self):
        # F5 defect shape: P2-037 formerly loaded cleanup/cooldown/bundles/floor
        # while routing entirely around the campaign-wide causal verdict.
        with tempfile.TemporaryDirectory() as tmp:
            copied_runs = Path(tmp) / "runs-without-whole-window"
            shutil.copytree(self.runs_root, copied_runs)
            (copied_runs / "campaign_log.jsonl").unlink()
            loaded = load_analysis_inputs(
                self.manifest_path,
                copied_runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
            self.assertTrue(loaded.registered)
            for evidence in loaded.registered.values():
                self.assertFalse(evidence.included)
                self.assertIn(
                    "whole_window_neg8_verdict_missing", evidence.base_reason_codes
                )

    def test_authenticated_v2_whole_window_source_reaches_claim_consumption(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        bundle_ids = sorted(entry["run_id"] for entry in manifest["entries"])
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "v2-runs"
            shutil.copytree(self.runs_root, runs)
            install_passing_analysis_whole_window(
                runs,
                bundle_ids,
                source_name="analysis-whole-window-source",
                schema_version="joulewise.campaign_provenance.v2",
            )

            self.assertEqual(
                whole_window_refusal_reasons(
                    runs,
                    set(bundle_ids),
                    consumption_session=prepared_minted_consumption_session(
                        runs,
                        set(bundle_ids),
                    ),
                ),
                (),
            )
            artifact = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )

        self.assertTrue(artifact["bundle_audit"])
        self.assertTrue(
            all(
                "whole_window_verdict_provenance_invalid"
                not in row["base_reason_codes"]
                for row in artifact["bundle_audit"]
            )
        )

    def test_unattested_and_relabelled_v2_whole_window_sources_refuse(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        bundle_ids = sorted(entry["run_id"] for entry in manifest["entries"])
        for case in ("unattested", "relabelled"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                runs = Path(tmp) / f"{case}-runs"
                shutil.copytree(self.runs_root, runs)
                install_passing_analysis_whole_window(
                    runs,
                    bundle_ids,
                    source_name="analysis-whole-window-source",
                    schema_version=(
                        "joulewise.campaign_provenance.v2"
                        if case == "unattested"
                        else "joulewise.campaign_provenance.v1"
                    ),
                )
                log_path = runs / "campaign_log.jsonl"
                log_rows = [
                    json.loads(line)
                    for line in log_path.read_text(encoding="utf-8").splitlines()
                ]
                verdict = next(
                    row
                    for row in log_rows
                    if row.get("record_type")
                    == "idle_admission_whole_window_verdict"
                )
                if case == "unattested":
                    log_rows = [verdict]
                else:
                    source_path = (
                        runs
                        / "campaign_manifests"
                        / "analysis-whole-window-source.json"
                    )
                    raw = source_path.read_bytes()
                    v1 = b'"schema_version": "joulewise.campaign_provenance.v1"'
                    v2 = b'"schema_version": "joulewise.campaign_provenance.v2"'
                    self.assertEqual(raw.count(v1), 1)
                    source_path.write_bytes(raw.replace(v1, v2, 1))
                    verdict["row_provenance"]["source_campaign_manifests"][0][
                        "sha256"
                    ] = hashlib.sha256(source_path.read_bytes()).hexdigest()
                    log_rows = [verdict]
                log_path.write_text(
                    "".join(json.dumps(row) + "\n" for row in log_rows),
                    encoding="utf-8",
                )

                reasons = whole_window_refusal_reasons(runs, set(bundle_ids))

                self.assertIn(
                    "whole_window_verdict_provenance_invalid",
                    reasons,
                )

    def test_analysis_loader_consumes_session_operated_envelopes(self):
        """Claim inputs use the authenticated widened view, not stored bounds."""

        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target_id = manifest["entries"][0]["run_id"]
        summary_path = self.runs_root / target_id / "summary_metrics.json"
        stored_bytes = summary_path.read_bytes()
        widened_by_bundle: dict[str, Mapping[str, object]] = {}

        class FakeConsumptionSession:
            def __init__(self, runs_root, bundle_ids):
                self.runs_root = Path(runs_root)
                self.bundle_ids = frozenset(bundle_ids)
                self.ready = True
                self.refusal_reasons = ()

            def summary_for(self, bundle_id):
                summary = json.loads(
                    (self.runs_root / bundle_id / "summary_metrics.json").read_text(
                        encoding="utf-8"
                    )
                )
                point = float(summary["gross_energy_j"])
                summary["energy_anchor_shift_envelopes"] = {
                    "/gross_energy_j": {
                        "method": "authenticated_anchor_shift_extrema_v1",
                        "anchor_bound_s": 0.03,
                        "point_j": point,
                        "lower_j": point - 0.25,
                        "upper_j": point + 0.25,
                        "max_abs_delta_j": 0.25,
                    }
                }
                widened_by_bundle[bundle_id] = summary
                return summary

            def provenance_for(self, bundle_id):
                envelope = widened_by_bundle[bundle_id][
                    "energy_anchor_shift_envelopes"
                ]["/gross_energy_j"]
                return {
                    "consumption_semantics_id": (
                        "d078_authenticated_max_bracket_rederivation_v1"
                    ),
                    "minted_bound_dominated": True,
                    "minted_fiducial_bound_s": 0.01,
                    "operative_fiducial_bound_s": 0.03,
                    "calibration_bracket": {
                        "pre": {
                            "bundle_id": "pre",
                            "manifest_sha256": "1" * 64,
                            "calibration_evidence_sha256": "2" * 64,
                        },
                        "post": {
                            "bundle_id": "post",
                            "manifest_sha256": "3" * 64,
                            "calibration_evidence_sha256": "4" * 64,
                        },
                    },
                    "operative_envelopes": {
                        "/gross_energy_j": {
                            **envelope,
                            "half_width_j": 0.25,
                        }
                    },
                }

        with (
            mock.patch(
                "joulewise.analysis_engine.inputs.AuthenticatedConsumptionSession",
                FakeConsumptionSession,
            ),
            mock.patch(
                "joulewise.analysis_engine.inputs.whole_window_refusal_reasons",
                return_value=(),
            ),
            mock.patch(
                "joulewise.analysis_engine.inputs.whole_window_drift_allowances",
                return_value=mock.Mock(status="legacy", allowances={}),
            ),
        ):
            loaded = load_analysis_inputs(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
            )

        target = next(
            evidence
            for evidence in loaded.effective.values()
            if evidence.bundle_id == target_id
        )
        self.assertIs(target.summary, widened_by_bundle[target_id])
        self.assertEqual(
            target.summary["energy_anchor_shift_envelopes"][
                "/gross_energy_j"
            ]["anchor_bound_s"],
            0.03,
        )
        self.assertIn(
            CONSUMPTION_PROVENANCE_PRECHECK_KEY,
            target.audit_row()["window_prechecks"],
        )
        self.assertEqual(summary_path.read_bytes(), stored_bytes)

    def test_production_request_factory_reaches_predeclared_transport(self):
        loaded = load_analysis_inputs(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        contrast = loaded.manifest["contrasts"][0]
        condition_id = contrast["condition_a_id"]
        evidence = [
            row
            for row in loaded.effective.values()
            if row.entry.get("condition_id") == condition_id
        ]
        self.assertTrue(evidence)
        stack = floor_stack_identity(evidence[0].raw_config, evidence[0].metadata)
        self.assertIsNotNone(stack)
        source = make_cell(cell_id="transport-source", condition="calibration-only")
        source["key"].update(
            backend="mock",
            metric=contrast["floor_selector"]["metric"],
            window_class=contrast["floor_selector"]["window_class"],
        )
        source["source_regime"]["stack_identity"] = stack
        source["source_regime"]["stack_identity_sha256"] = canonical_domain_sha256(
            STACK_IDENTITY_DOMAIN, stack
        )
        source["transport_group_id"] = "tg-production-transport"
        group = build_transport_group(
            transport_group_id="tg-production-transport",
            backend="mock",
            metric=contrast["floor_selector"]["metric"],
            window_class=contrast["floor_selector"]["window_class"],
            stack_identity=stack,
            source_cells=[source],
            allowed_consumer_condition_families=[condition_family(condition_id)],
        )
        artifact = build_floor_artifact(
            artifact_id="production-transport",
            calibration_scope="window_a",
            source_class="synthetic",
            provenance=make_artifact()["provenance"],
            cells=[source],
            transport_groups=[group],
        )
        binding = FloorEvidenceBinding(
            bound_cell_ids=frozenset({source["cell_id"]}),
            cell_scientific_identity_sha256={},
            cell_stack_identity_sha256={
                source["cell_id"]: source["source_regime"]["stack_identity_sha256"]
            },
            bound_bundle_sha256s=frozenset(),
            problems_by_cell={source["cell_id"]: ()},
            global_problems=(),
        )
        request = floor_request_for_evidence(
            artifact,
            binding,
            contrast,
            condition_id,
            evidence,
        )
        self.assertIsNotNone(request)
        self.assertEqual(request.condition_family_id, condition_id)
        self.assertEqual(request.stack_identity_sha256, group["stack_identity_sha256"])

    def test_named_strata_manifest_preserves_terminal_mock_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "configs"
            shutil.copytree(self.config_dir, config_dir)
            manifest_path = config_dir / "analysis_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            block_ids = manifest["contrasts"][0]["block_ids"]
            manifest["design"]["randomization"] = {
                "scheme": "stratified_paired_label_swap",
                "exchangeability": "within_named_strata",
                "named_strata": [
                    {"stratum_id": "early", "block_ids": block_ids[:3]},
                    {"stratum_id": "late", "block_ids": block_ids[3:]},
                ],
            }
            manifest["manifest_id"] = calculate_manifest_id(manifest)
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            loaded = load_analysis_inputs(
                manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
            )

        self.assertEqual(
            loaded.manifest["design"]["randomization"]["scheme"],
            "stratified_paired_label_swap",
        )
        self.assertTrue(loaded.registered)
        self.assertTrue(
            all(
                not evidence.included
                and MOCK_TELEMETRY_CLAIM_REFUSAL
                in evidence.base_reason_codes
                for evidence in loaded.registered.values()
            )
        )

    def test_named_strata_manifest_preserves_terminal_mock_refusal_with_production_telemetry_identity(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "configs"
            shutil.copytree(self.config_dir, config_dir)
            manifest_path = config_dir / "analysis_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            block_ids = manifest["contrasts"][0]["block_ids"]
            manifest["design"]["randomization"] = {
                "scheme": "stratified_paired_label_swap",
                "exchangeability": "within_named_strata",
                "named_strata": [
                    {"stratum_id": "early", "block_ids": block_ids[:3]},
                    {"stratum_id": "late", "block_ids": block_ids[3:]},
                ],
            }
            manifest["manifest_id"] = calculate_manifest_id(manifest)
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with mock.patch(
                "joulewise.analysis_engine.inputs.custody_telemetry_identity",
                return_value=PRODUCTION_TELEMETRY_IDENTITY,
            ):
                artifact = analyze_claims(
                    manifest_path,
                    self.runs_root,
                    self.floor_path,
                    strict_validator=validate_bundle,
                )
        self.assertTrue(
            all(
                contrast["loo"]["status"] == "complete"
                for contrast in artifact["contrasts"]
            )
        )
        self.assertTrue(
            all(
                len(contrast["loo"]["rows"]) == 5
                for contrast in artifact["contrasts"]
            )
        )

    def test_hash_bound_campaign_cooldown_is_rechecked_per_member(self):
        runs = self.root / "cooldown-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        bundle_ids = [entry["run_id"] for entry in manifest["entries"]]
        campaign_dir = runs / "campaign_manifests"
        raw_dir = campaign_dir / "raw"
        raw_dir.mkdir(parents=True)
        trace = (
            b'{"idle_power_w":5.0,"release":true,'
            b'"release_criteria_met_late":false,"timestamp_s":1.0}\n'
        )
        trace_path = raw_dir / "cooldown.jsonl"
        trace_path.write_bytes(trace)
        descriptor = {
            "path": "raw/cooldown.jsonl",
            "sha256": hashlib.sha256(trace).hexdigest(),
            "records": 1,
        }
        session_id = "campaign-fixture"
        members = []
        for index, bundle_id in enumerate(bundle_ids):
            cooldown = (
                {
                    "result": "first_run_exempt",
                    "session_id": session_id,
                    "following_run_id": bundle_id,
                }
                if index == 0
                else {
                    "result": "recovered",
                    "session_id": session_id,
                    "following_run_id": bundle_id,
                    "raw_artifact": descriptor,
                }
            )
            members.append(
                {
                    "run_id": bundle_id,
                    "bundle_ids": [bundle_id],
                    "execution": "invoked",
                    "preceding_campaign_cooldown": cooldown,
                }
            )
        (campaign_dir / "campaign-fixture.json").write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.campaign_provenance.v1",
                    "session_id": session_id,
                    "analysis_manifest_id": manifest["manifest_id"],
                    "first_physical_run_id": bundle_ids[0],
                    "members": members,
                    "cooldown_gates": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertTrue(
            all(row["campaign_cooldown"]["verified"] for row in artifact["bundle_audit"])
        )
        self.assertTrue(
            all(
                "campaign_cooldown_evidence_missing"
                not in contrast["claim_evaluation"]["reason_codes"]
                for contrast in artifact["contrasts"]
            )
        )

        trace_path.write_bytes(trace + b'{"tampered":true}\n')
        refuted = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertTrue(
            any(
                "campaign_cooldown_evidence_missing"
                in contrast["claim_evaluation"]["reason_codes"]
                for contrast in refuted["contrasts"]
            )
        )

    def test_physical_repetition_rows_supply_each_canonical_cooldown(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "runs"
            campaign_dir = runs / "campaign_manifests"
            raw_dir = campaign_dir / "raw"
            raw_dir.mkdir(parents=True)
            trace = (
                b'{"release":true,"release_criteria_met_late":false,'
                b'"rolling_mean_power_w":5.0,"timestamp_s":10.0}\n'
            )
            trace_path = raw_dir / "config-r2.jsonl"
            trace_path.write_bytes(trace)
            descriptor = {
                "path": "raw/config-r2.jsonl",
                "sha256": hashlib.sha256(trace).hexdigest(),
                "records": 1,
            }
            session_id = "physical-repetition-campaign"
            first_run_id = "config__r1"
            second_run_id = "config__r2"
            first_cooldown = {
                "result": "first_run_exempt",
                "session_id": session_id,
                "following_run_id": first_run_id,
            }
            second_cooldown = {
                "result": "recovered",
                "session_id": session_id,
                "following_run_id": second_run_id,
                "raw_artifact": descriptor,
            }
            (campaign_dir / "physical.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.campaign_provenance.v1",
                        "session_id": session_id,
                        "analysis_manifest_id": "physical-manifest",
                        "first_physical_run_id": first_run_id,
                        "members": [
                            {
                                "run_id": "config",
                                "bundle_ids": [first_run_id, second_run_id],
                                "execution": "invoked",
                                # Compatibility summary must not fan out over
                                # the physical rows below.
                                "preceding_campaign_cooldown": first_cooldown,
                                "physical_members": [
                                    {
                                        "bundle_id": first_run_id,
                                        "preceding_campaign_cooldown": first_cooldown,
                                    },
                                    {
                                        "bundle_id": second_run_id,
                                        "preceding_campaign_cooldown": second_cooldown,
                                    },
                                ],
                            }
                        ],
                        "cooldown_gates": [second_cooldown],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )

            cooldowns = _campaign_cooldown_evidence(
                runs, "physical-manifest"
            )

            self.assertEqual(cooldowns[first_run_id]["result"], "first_run_exempt")
            self.assertTrue(cooldowns[first_run_id]["verified"])
            self.assertEqual(cooldowns[second_run_id]["result"], "recovered")
            self.assertTrue(cooldowns[second_run_id]["verified"])
            self.assertEqual(cooldowns[second_run_id]["raw_artifact"], descriptor)
            for bundle_id in (first_run_id, second_run_id):
                evidence = BundleEvidence(
                    entry={},
                    bundle_id=bundle_id,
                    relative_path=bundle_id,
                    path=runs / bundle_id,
                    summary={
                        "window_evidence_precheck": {
                            "gross_request": {"eligible": True, "reasons": []}
                        },
                        "measurement_quality": {"cooldown_cap_hit": False},
                    },
                    metadata={},
                    raw_config={},
                    strict_problems=(),
                    base_reason_codes=(),
                    config_sha256=None,
                    summary_sha256=None,
                    replacement_classification="registered",
                    inclusion_status="included",
                    campaign_cooldown=cooldowns[bundle_id],
                )
                precheck = window_evidence_precheck(
                    evidence,
                    {"name": "gross_energy_j", "metric_tag": "gross_request"},
                )
                self.assertNotIn(
                    "campaign_cooldown_evidence_missing", precheck["reasons"]
                )

    def test_real_cap_hit_campaign_records_defeat_summary_only_reading(self):
        """Audit P0.4: the four real cap-hit members carry
        ``measurement_quality.cooldown_cap_hit=null`` in their summaries, so
        summary-only extraction would treat them as clean n.  The verified
        campaign-log join must mark each one ``cooldown_cap_hit``."""

        from tests.test_floor_extraction import (
            AUDIT_CAP_HIT_TABLE,
            install_real_cap_hit_manifest,
        )

        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp)
            for bundle_id in AUDIT_CAP_HIT_TABLE:
                install_real_cap_hit_manifest(runs, bundle_id)
            cooldowns = campaign_cooldown_evidence(runs)
            for bundle_id in AUDIT_CAP_HIT_TABLE:
                evidence = BundleEvidence(
                    entry={},
                    bundle_id=bundle_id,
                    relative_path=bundle_id,
                    path=runs / bundle_id,
                    summary={
                        "window_evidence_precheck": {
                            "gross_request": {"eligible": True, "reasons": []}
                        },
                        # The stored summary fact for all four members.
                        "measurement_quality": {"cooldown_cap_hit": None},
                    },
                    metadata={},
                    raw_config={},
                    strict_problems=(),
                    base_reason_codes=(),
                    config_sha256=None,
                    summary_sha256=None,
                    replacement_classification="registered",
                    inclusion_status="included",
                    campaign_cooldown=cooldowns[bundle_id],
                )
                precheck = window_evidence_precheck(
                    evidence,
                    {"name": "gross_energy_j", "metric_tag": "gross_request"},
                )
                self.assertFalse(precheck["eligible"])
                self.assertIn("cooldown_cap_hit", precheck["reasons"])
                self.assertNotIn(
                    "campaign_cooldown_evidence_missing", precheck["reasons"]
                )

    def test_artifact_is_path_relocation_deterministic(self):
        expected = analyze_claims(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        relocated = self.root / "relocated"
        relocated_configs = relocated / "configs"
        relocated_runs = relocated / "runs"
        relocated_floor = relocated / "floor.json"
        shutil.copytree(self.config_dir, relocated_configs)
        shutil.copytree(self.runs_root, relocated_runs)
        shutil.copy2(self.floor_path, relocated_floor)
        observed = analyze_claims(
            relocated_configs / "analysis_manifest.json",
            relocated_runs,
            relocated_floor,
            strict_validator=validate_bundle,
        )
        self.assertEqual(observed, expected)
        self.assertEqual(render_claim_verdicts(observed), render_claim_verdicts(expected))

    def test_unrelated_invalid_utf8_config_is_ignored_by_closed_set_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "runs"
            shutil.copytree(self.runs_root, runs)
            before = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
            unrelated = runs / "unrelated-invalid-utf8"
            unrelated.mkdir()
            (unrelated / "config.json").write_bytes(b"\xff\xfe")
            after = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
            self.assertEqual(after, before)
            self.assertEqual(render_claim_verdicts(after), render_claim_verdicts(before))
            self.assertEqual(len(after["bundle_audit"]), 30)

    def test_private_stochastic_seam_changes_recorded_policy_identity(self):
        def unavailable_floor(contrast, condition_id, rows, floor_artifact):
            del contrast, condition_id, rows, floor_artifact
            return None

        def governed_pair_terms(evidence_a, evidence_b, metric):
            del evidence_a, evidence_b, metric
            return (
                (
                    StochasticVarianceTerm(
                        "fixture_governed_j2",
                        variance_a=0.25,
                        variance_b=0.25,
                        correlation_scope="independent_run",
                    ),
                ),
                (),
            )

        artifact = analyze_claims(
            self.manifest_path,
            self.runs_root,
            self.floor_path,
            strict_validator=validate_bundle,
            _floor_request_factory=unavailable_floor,
            _pair_stochastic_factory=governed_pair_terms,
        )
        self.assertIn(
            "private_test_seam:",
            artifact["engine"]["policy_identity"]["floor_resolution"],
        )
        self.assertIn(
            "private_test_seam:",
            artifact["engine"]["policy_identity"]["stochastic_variance"],
        )
        contrast = artifact["contrasts"][0]
        self.assertEqual(contrast["estimator"]["n"], 0)
        self.assertIsNone(contrast["estimator"]["SE_metrology"])
        self.assertEqual(
            contrast["claim_evaluation"]["outcome"],
            "not_estimable",
        )
        self.assertIn(
            MOCK_TELEMETRY_CLAIM_REFUSAL,
            contrast["claim_evaluation"]["reason_codes"],
        )

    def test_private_stochastic_seam_changes_recorded_policy_identity_with_production_telemetry_identity(
        self,
    ):
        def unavailable_floor(contrast, condition_id, rows, floor_artifact):
            del contrast, condition_id, rows, floor_artifact
            return None

        def governed_pair_terms(evidence_a, evidence_b, metric):
            del evidence_a, evidence_b, metric
            return (
                (
                    StochasticVarianceTerm(
                        "fixture_governed_j2",
                        variance_a=0.25,
                        variance_b=0.25,
                        correlation_scope="independent_run",
                    ),
                ),
                (),
            )

        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
            artifact = analyze_claims(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
                _floor_request_factory=unavailable_floor,
                _pair_stochastic_factory=governed_pair_terms,
            )
        self.assertIn(
            "private_test_seam:",
            artifact["engine"]["policy_identity"]["floor_resolution"],
        )
        self.assertIn(
            "private_test_seam:",
            artifact["engine"]["policy_identity"]["stochastic_variance"],
        )
        estimator = artifact["contrasts"][0]["estimator"]
        self.assertGreater(estimator["SE_metrology"], 0.0)
        self.assertGreater(estimator["SE_total"], estimator["SE_repeat"])
        repeat_width = (
            estimator["repeat_point_CI95"]["upper"]
            - estimator["repeat_point_CI95"]["lower"]
        )
        metrology_width = (
            estimator["metrology_aware_CI95"]["upper"]
            - estimator["metrology_aware_CI95"]["lower"]
        )
        self.assertGreater(metrology_width, repeat_width)

    def _exercise_cli_distinct_calibration_binding(
        self,
        *,
        production_identity: bool,
    ):
        scenario_suffix = "-production" if production_identity else ""
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        condition_ids = sorted(
            {
                entry["condition_id"]
                for entry in manifest["entries"]
                if entry["role"] == "condition"
            }
        )
        analysis_root = self.root / (
            f"independent-analysis-corpus{scenario_suffix}"
        )
        shutil.copytree(self.runs_root, analysis_root)
        evidence_roots = {
            "a10": self.root / f"independent-a10-evidence{scenario_suffix}",
            "window_c": (
                self.root / f"independent-window-c-evidence{scenario_suffix}"
            ),
        }
        for evidence_root in evidence_roots.values():
            evidence_root.mkdir()
        floor_dir = self.root / f"independent-floor{scenario_suffix}"
        floor_dir.mkdir(exist_ok=True)
        calibration_plan_path = floor_dir / "calibration_plan.json"
        calibration_plan_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.detection_floor_calibration_plan.v1",
                    "plan_id": "floor-exact-cli-plan",
                    "calibration_scope": "window_a",
                    "condition_family_ids": condition_ids,
                    "comparative_member_labels": ["A", "B", "B", "A"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        calibration_plan_sha256 = hashlib.sha256(
            calibration_plan_path.read_bytes()
        ).hexdigest()
        pinset_directory = floor_dir / "floor_mint_pinsets"
        pinset_directory.mkdir()
        pinset = json.loads(
            (
                ROOT / "scripts" / "floor_mint_pinsets" / "mint1.json"
            ).read_text(encoding="utf-8")
        )
        pinset["plan"]["plan_id"] = "floor-exact-cli-plan"
        pinset["plan"]["sha256"] = calibration_plan_sha256
        (pinset_directory / "floor_exact_cli.json").write_text(
            json.dumps(pinset, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        pinset_patch = mock.patch(
            "joulewise.detection_floor._FLOOR_MINT_PINSET_DIRECTORY",
            pinset_directory,
        )
        pinset_patch.start()
        self.addCleanup(pinset_patch.stop)
        cells = []
        groups = []
        order_rows = {"a10": [], "window_c": []}
        campaign_rows = {"a10": [], "window_c": []}
        calibration_roots_by_id = {}
        all_bound_hashes = []
        for condition_id in condition_ids:
            entries = sorted(
                (
                    entry
                    for entry in manifest["entries"]
                    if entry["condition_id"] == condition_id
                ),
                key=lambda entry: entry["planned_rep_index"],
            )
            source_config = json.loads(
                (self.config_dir / entries[0]["config"]).read_text(encoding="utf-8")
            )
            calibration_ids = []
            with mock.patch(
                "joulewise.bundle._capture_source_state",
                return_value=dict(CLEAN_SOURCE_STATE),
            ):
                for index in range(25):
                    run_id = f"cal-{condition_id}-{index:02d}"
                    root_id = "a10" if index < 5 else "window_c"
                    evidence_root = evidence_roots[root_id]
                    calibration_roots_by_id[run_id] = evidence_root
                    calibration_config = json.loads(json.dumps(source_config))
                    calibration_config["run_id"] = run_id
                    tags = calibration_config["run_metadata"]["tags"]
                    tags.append(
                        f"calibration-plan-sha256={calibration_plan_sha256}"
                    )
                    if index >= 5:
                        block_index = (index - 5) // 4
                        sequence_index = (index - 5) % 4
                        labels = ("A", "B", "B", "A")
                        tags.extend(
                            (
                                f"calibration-abba-block-id=floor-{condition_id}-b{block_index}",
                                f"calibration-abba-label={labels[sequence_index]}",
                                f"calibration-abba-sequence-index={sequence_index + 1}",
                            )
                        )
                    config_path = floor_dir / f"{run_id}.json"
                    config_path.write_text(
                        json.dumps(calibration_config, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        code = main(
                            [
                                "run",
                                str(config_path),
                                "--runs-dir",
                                str(evidence_root),
                            ]
                        )
                    self.assertEqual(code, 0)
                    install_explicit_mock_sampler(evidence_root / run_id)
                    calibration_ids.append(run_id)
                    order_rows[root_id].append(
                        {
                            "index": len(order_rows[root_id]) + 1,
                            "config": config_path.name,
                            "run_id": run_id,
                        }
                    )
                    campaign_rows[root_id].append(
                        {
                            "run_index": len(campaign_rows[root_id]) + 1,
                            "run_id": run_id,
                        }
                    )

            def calibration_record(run_id):
                bundle = calibration_roots_by_id[run_id] / run_id
                summary = json.loads((bundle / "summary_metrics.json").read_text(encoding="utf-8"))
                bundle_hash = complete_bundle_sha256(bundle)
                all_bound_hashes.append(bundle_hash)
                return {
                    "bundle_id": run_id,
                    "bundle_sha256": bundle_hash,
                    "config_sha256": hashlib.sha256((bundle / "config.json").read_bytes()).hexdigest(),
                    "metric_value_j": summary["gross_energy_j"],
                }

            observations = [calibration_record(run_id) for run_id in calibration_ids[:5]]
            drift_allowance = whole_window_allowance(
                value=5e-324,
                observed=0.0,
                derived=5e-324,
            )
            absolute = build_absolute_record(
                absolute_false_effect_floor(
                    [row["metric_value_j"] for row in observations],
                    admissible_half_widths_j=[0.0] * len(observations),
                ),
                observations,
                consumption_semantics_id="d078_minted_envelopes_v1",
                whole_window_drift_allowance=drift_allowance,
            )
            blocks = []
            for block_index in range(5):
                ids = calibration_ids[5 + block_index * 4 : 9 + block_index * 4]
                member_records = [calibration_record(run_id) for run_id in ids]
                positioned = [
                    {"position": position, **record}
                    for position, record in zip(
                        ("A1", "B1", "B2", "A2"), member_records, strict=True
                    )
                ]
                delta = abba_delta(
                    positioned[0]["metric_value_j"],
                    positioned[1]["metric_value_j"],
                    positioned[2]["metric_value_j"],
                    positioned[3]["metric_value_j"],
                )
                blocks.append(
                    {
                        "block_id": f"floor-{condition_id}-b{block_index}",
                        "executed_labels": ["A", "B", "B", "A"],
                        "members": positioned,
                        "delta_j": delta,
                    }
                )
            comparative = build_comparative_record(
                comparative_false_effect_floor(
                    [block["delta_j"] for block in blocks],
                    admissible_half_widths_j=[0.0] * len(blocks),
                ),
                blocks,
                consumption_semantics_id="d078_minted_envelopes_v1",
                whole_window_drift_allowance=drift_allowance,
            )
            first_bundle = calibration_roots_by_id[
                calibration_ids[0]
            ] / calibration_ids[0]
            stack = floor_stack_identity(
                json.loads((first_bundle / "config.json").read_text(encoding="utf-8")),
                json.loads((first_bundle / "metadata.json").read_text(encoding="utf-8")),
            )
            self.assertIsNotNone(stack)
            component_regime = make_regime(stack_identity=stack)
            cell = build_floor_cell(
                cell_id=f"floor-{condition_id}",
                key={
                    "backend": "mock",
                    "metric": "gross_energy_j",
                    "window_class": "request",
                    **condition_family(condition_id),
                },
                eligibility={
                    "use_role": "primary_claim_gate",
                    "minimum_claim_n": 5,
                    "status": "claim_ready",
                    "claim_usable": True,
                    "reason_codes": [],
                },
                absolute=absolute,
                comparative=comparative,
                transport_group_id=f"tg-{condition_id}",
                provenance={
                    "absolute": {
                        "calibration_cell_id": f"floor-{condition_id}-abs",
                        "evidence_root_id": "a10",
                        "order_manifest": {
                            "manifest_id": "floor-exact-a10-order",
                            "sha256": "0" * 64,
                        },
                        "campaign_log": {"sha256": "0" * 64},
                        "extraction_report": {"sha256": "0" * 64},
                        "extraction_spec": {"sha256": "0" * 64},
                        "bundle_ids": [
                            observation["bundle_id"]
                            for observation in observations
                        ],
                        "bundle_sha256s": [
                            observation["bundle_sha256"]
                            for observation in observations
                        ],
                        "source_regime": component_regime,
                    },
                    "comparative": {
                        "calibration_cell_id": f"floor-{condition_id}-cmp",
                        "evidence_root_id": "window_c",
                        "order_manifest": {
                            "manifest_id": "floor-exact-window-c-order",
                            "sha256": "0" * 64,
                        },
                        "campaign_log": {"sha256": "0" * 64},
                        "extraction_report": {"sha256": "0" * 64},
                        "extraction_spec": {"sha256": "0" * 64},
                        "bundle_ids": [
                            member["bundle_id"]
                            for block in blocks
                            for member in block["members"]
                        ],
                        "bundle_sha256s": [
                            member["bundle_sha256"]
                            for block in blocks
                            for member in block["members"]
                        ],
                        "source_regime": component_regime,
                    },
                },
            )
            cells.append(cell)
            groups.append(
                build_transport_group(
                    transport_group_id=f"tg-{condition_id}",
                    backend="mock",
                    metric="gross_energy_j",
                    window_class="request",
                    stack_identity=stack,
                    source_cells=[cell],
                    allowed_consumer_condition_families=[
                        {
                            key: cell["key"][key]
                            for key in (
                                "condition_family_id",
                                "condition_family_definition",
                                "condition_family_sha256",
                            )
                        }
                    ],
                )
            )
        root_descriptor_hashes = {}
        for root_id, evidence_root in evidence_roots.items():
            order_path = evidence_root / "order_manifest.json"
            order_path.write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.order_manifest.v1",
                        "manifest_id": f"floor-exact-{root_id.replace('_', '-')}-order",
                        "executed_order": order_rows[root_id],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            campaign_path = evidence_root / "campaign_log.jsonl"
            campaign_path.write_text(
                "".join(
                    json.dumps(row, sort_keys=True) + "\n"
                    for row in campaign_rows[root_id]
                ),
                encoding="utf-8",
            )
            root_descriptor_hashes[root_id] = {
                "order_manifest": hashlib.sha256(
                    order_path.read_bytes()
                ).hexdigest(),
                "campaign_log": hashlib.sha256(
                    campaign_path.read_bytes()
                ).hexdigest(),
            }
        extraction_spec_path = floor_dir / "extraction_spec.json"
        extraction_spec_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.floor_extraction_spec.fixture.v1",
                    "condition_family_ids": condition_ids,
                    "absolute_n": 5,
                    "comparative_n_blocks": 5,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        extraction_report_path = floor_dir / "extraction_report.json"
        extraction_report_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.floor_extraction_report.fixture.v1",
                    "cell_ids": [cell["cell_id"] for cell in cells],
                    "bundle_ids": [
                        bundle_id
                        for cell in cells
                        for component in ("absolute", "comparative")
                        for bundle_id in cell["provenance"][component]["bundle_ids"]
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        common_descriptor_hashes = {
            "extraction_report": hashlib.sha256(
                extraction_report_path.read_bytes()
            ).hexdigest(),
            "extraction_spec": hashlib.sha256(
                extraction_spec_path.read_bytes()
            ).hexdigest(),
        }
        for cell in cells:
            for component in ("absolute", "comparative"):
                component_provenance = cell["provenance"][component]
                root_id = component_provenance["evidence_root_id"]
                descriptor_hashes = {
                    **root_descriptor_hashes[root_id],
                    **common_descriptor_hashes,
                }
                for descriptor_name, descriptor_sha256 in descriptor_hashes.items():
                    component_provenance[descriptor_name][
                        "sha256"
                    ] = descriptor_sha256
        provenance = make_artifact()["provenance"]
        provenance["calibration_plan"] = {
            "plan_id": "floor-exact-cli-plan",
            "declared_calibration_scope": "window_a",
            "relative_path": "calibration_plan.json",
            "sha256": calibration_plan_sha256,
        }
        exact_floor = build_floor_artifact(
            artifact_id="floor-exact-cli",
            calibration_scope="window_a",
            source_class="synthetic",
            provenance=provenance,
            cells=cells,
            transport_groups=groups,
            idle_drift_guard={
                "calibration_status": "calibrated",
                "method": "p2_015_prediction_guard_v1",
                "guard_w": 0.25,
                "n_bundles": 2,
                "bundle_sha256": all_bound_hashes[:2],
                "cell_id": cells[0]["cell_id"],
                "artifact_sha256": "3" * 64,
            },
        )
        self.assertEqual(validate_floor_artifact(exact_floor), [])
        floor_path = floor_dir / "floor-exact-cli.json"
        floor_path.write_text(json.dumps(exact_floor, indent=2) + "\n", encoding="utf-8")
        bare_root_binding = bind_floor_artifact_evidence(
            exact_floor,
            floor_path,
            analysis_root,
            strict_validator=validate_bundle,
        )
        self.assertIn(
            "evidence_root_mapping_required",
            bare_root_binding.global_problems,
        )
        self.assertIn(
            "evidence_root_mapping_required",
            floor_binding_reason_codes(bare_root_binding),
        )
        self.assertFalse(bare_root_binding.bound_cell_ids)
        bare_loaded = load_analysis_inputs(
            self.manifest_path,
            analysis_root,
            floor_path,
            strict_validator=validate_bundle,
        )
        self.assertIn(
            "evidence_root_mapping_required",
            floor_binding_reason_codes(bare_loaded.floor_binding),
        )

        missing_root_binding = bind_floor_artifact_evidence(
            exact_floor,
            floor_path,
            {"a10": evidence_roots["a10"]},
            strict_validator=validate_bundle,
        )
        self.assertIn(
            "missing_evidence_root_mapping: 'window_c'",
            missing_root_binding.global_problems,
        )
        self.assertFalse(missing_root_binding.bound_cell_ids)

        surplus_root_binding = bind_floor_artifact_evidence(
            exact_floor,
            floor_path,
            {**evidence_roots, "unexpected": analysis_root},
            strict_validator=validate_bundle,
        )
        self.assertFalse(
            any(
                problem.startswith("unknown_evidence_root_mapping:")
                for problem in surplus_root_binding.global_problems
            ),
            surplus_root_binding.global_problems,
        )
        self.assertNotIn(
            "unknown_evidence_root_mapping",
            floor_binding_reason_codes(surplus_root_binding),
        )
        self.assertEqual(
            surplus_root_binding.bound_cell_ids,
            (
                frozenset(
                    cell["cell_id"] for cell in exact_floor["cells"]
                )
                if production_identity
                else frozenset()
            ),
        )

        wrong_root = floor_dir / "wrong-evidence-root"
        wrong_root.mkdir()
        wrong_root_binding = bind_floor_artifact_evidence(
            exact_floor,
            floor_path,
            {
                "a10": wrong_root,
                "window_c": evidence_roots["window_c"],
            },
            strict_validator=validate_bundle,
        )
        self.assertTrue(
            any(
                problem.startswith("component_evidence_root_disagreement:")
                for problem in wrong_root_binding.global_problems
            )
        )
        self.assertFalse(wrong_root_binding.bound_cell_ids)

        leaked_path_artifact = json.loads(json.dumps(exact_floor))
        leaked_path_artifact["provenance"]["calibration_plan"][
            "relative_path"
        ] = str(calibration_plan_path.resolve())
        leaked_path_binding = bind_floor_artifact_evidence(
            leaked_path_artifact,
            floor_path,
            evidence_roots,
            strict_validator=validate_bundle,
        )
        self.assertTrue(
            any(
                problem.startswith("artifact_absolute_path_leakage:")
                for problem in leaked_path_binding.global_problems
            )
        )
        self.assertFalse(leaked_path_binding.bound_cell_ids)

        loaded = load_analysis_inputs(
            self.manifest_path,
            analysis_root,
            floor_path,
            strict_validator=validate_bundle,
            evidence_roots=evidence_roots,
        )
        self.assertFalse(
            {
                "evidence_root_mapping_required",
                "missing_evidence_root_mapping",
                "unknown_evidence_root_mapping",
            }
            & set(floor_binding_reason_codes(loaded.floor_binding))
        )
        if production_identity:
            self.assertFalse(loaded.floor_binding.global_problems)
            self.assertEqual(
                loaded.floor_binding.bound_cell_ids,
                frozenset(cell["cell_id"] for cell in exact_floor["cells"]),
            )
        self.assertEqual(len(loaded.registered), 30)
        self.assertFalse(
            any(
                evidence.bundle_id.startswith("cal-")
                for evidence in (
                    *loaded.registered.values(),
                    *loaded.extra_audits,
                )
            )
        )
        missing_loaded = load_analysis_inputs(
            self.manifest_path,
            analysis_root,
            floor_path,
            strict_validator=validate_bundle,
            evidence_roots={"a10": evidence_roots["a10"]},
        )
        self.assertIn(
            "missing_evidence_root_mapping: 'window_c'",
            missing_loaded.floor_binding.global_problems,
        )

        output = self.root / f"exact-cli-claim-verdicts{scenario_suffix}.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as stderr:
            code = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(analysis_root),
                    "--evidence-root",
                    f"a10={evidence_roots['a10']}",
                    "--evidence-root",
                    f"window_c={evidence_roots['window_c']}",
                    "--floor-artifact",
                    str(floor_path),
                    "--output",
                    str(output),
                ]
            )
        self.assertEqual(code, 0, stderr.getvalue())
        artifact = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(len(artifact["bundle_audit"]), 30)
        self.assertFalse(
            any(
                row["bundle_id"].startswith("cal-")
                for row in artifact["bundle_audit"]
            )
        )
        gross = [
            contrast
            for contrast in artifact["contrasts"]
            if contrast["metric"]["name"] == "gross_energy_j"
        ]
        self.assertTrue(gross)
        if production_identity:
            self.assertTrue(
                all(
                    contrast["floor"]["status"] == "resolved"
                    for contrast in gross
                ),
            )
            self.assertTrue(
                all(
                    resolution["status"] == "exact"
                    for contrast in gross
                    for resolution in contrast["floor"]["resolutions"]
                )
            )
            self.assertTrue(
                all(
                    contrast["loo"]["status"] == "complete"
                    for contrast in gross
                )
            )
            self.assertTrue(
                all(len(contrast["loo"]["rows"]) == 5 for contrast in gross)
            )
        else:
            self.assertTrue(
                all(
                    contrast["floor"]["status"] == "refused"
                    and all(
                        "artifact_schema_invalid" in resolution["reason_codes"]
                        for resolution in contrast["floor"]["resolutions"]
                    )
                    for contrast in gross
                )
            )
            self.assertTrue(
                all(
                    contrast["loo"] == {"status": "not_run", "rows": []}
                    and MOCK_TELEMETRY_CLAIM_REFUSAL
                    in contrast["claim_evaluation"]["reason_codes"]
                    for contrast in gross
                )
            )

        def refresh_first_cell(candidate):
            changed_cell = candidate["cells"][0]
            changed_blocks = changed_cell["comparative"]["blocks"]
            for changed_block in changed_blocks:
                members = changed_block["members"]
                changed_block["delta_j"] = abba_delta(
                    members[0]["metric_value_j"],
                    members[1]["metric_value_j"],
                    members[2]["metric_value_j"],
                    members[3]["metric_value_j"],
                )
            changed_cell["comparative"] = build_comparative_record(
                comparative_false_effect_floor(
                    [block["delta_j"] for block in changed_blocks],
                    admissible_half_widths_j=[0.0] * len(changed_blocks),
                ),
                changed_blocks,
                consumption_semantics_id=changed_cell["comparative"][
                    "consumption_semantics_id"
                ],
                whole_window_drift_allowance=changed_cell["comparative"][
                    "whole_window_drift_allowance"
                ],
            )
            comparative_provenance = changed_cell["provenance"]["comparative"]
            comparative_provenance["bundle_ids"] = [
                member["bundle_id"]
                for block in changed_blocks
                for member in block["members"]
            ]
            comparative_provenance["bundle_sha256s"] = [
                member["bundle_sha256"]
                for block in changed_blocks
                for member in block["members"]
            ]
            changed_cell["floor_cmp_j"] = changed_cell["comparative"][
                "drift_widened_guarded_floor_j"
            ]
            changed_cell["floor_gate_j"] = max(
                changed_cell["floor_abs_j"], changed_cell["floor_cmp_j"]
            )
            candidate["transport_groups"][0] = build_transport_group(
                transport_group_id=changed_cell["transport_group_id"],
                backend="mock",
                metric="gross_energy_j",
                window_class="request",
                stack_identity=changed_cell["source_regime"]["stack_identity"],
                source_cells=[changed_cell],
                allowed_consumer_condition_families=[
                    {
                        key: changed_cell["key"][key]
                        for key in (
                            "condition_family_id",
                            "condition_family_definition",
                            "condition_family_sha256",
                        )
                    }
                ],
            )

        def binding_for(candidate, name):
            candidate_path = floor_dir / name
            candidate_path.write_text(
                json.dumps(candidate, indent=2) + "\n", encoding="utf-8"
            )
            return load_analysis_inputs(
                self.manifest_path,
                analysis_root,
                candidate_path,
                strict_validator=validate_bundle,
                evidence_roots=evidence_roots,
            ).floor_binding

        relabeled = json.loads(json.dumps(exact_floor))
        relabeled_members = relabeled["cells"][0]["comparative"]["blocks"][0]["members"]
        payload_keys = (
            "bundle_id",
            "bundle_sha256",
            "config_sha256",
            "metric_value_j",
        )
        for key in payload_keys:
            relabeled_members[0][key], relabeled_members[1][key] = (
                relabeled_members[1][key],
                relabeled_members[0][key],
            )
        refresh_first_cell(relabeled)
        relabeled_binding = binding_for(relabeled, "floor-relabeled-abba.json")
        self.assertTrue(
            any(
                "calibration_abba_label_mismatch" in problem
                for problem in relabeled_binding.problems_by_cell[relabeled["cells"][0]["cell_id"]]
            )
        )
        self.assertNotIn(
            relabeled["cells"][0]["cell_id"], relabeled_binding.bound_cell_ids
        )
        self.assertIn(
            "calibration_abba_label_mismatch",
            floor_binding_reason_codes(relabeled_binding),
        )
        relabeled_result = analyze_claims(
            self.manifest_path,
            analysis_root,
            floor_dir / "floor-relabeled-abba.json",
            strict_validator=validate_bundle,
            evidence_roots=evidence_roots,
        )
        self.assertTrue(
            any(
                "calibration_abba_label_mismatch" in resolution["reason_codes"]
                for contrast in relabeled_result["contrasts"]
                for resolution in contrast["floor"]["resolutions"]
            )
        )

        reordered = json.loads(json.dumps(exact_floor))
        reordered_members = reordered["cells"][0]["comparative"]["blocks"][0]["members"]
        for key in payload_keys:
            reordered_members[1][key], reordered_members[2][key] = (
                reordered_members[2][key],
                reordered_members[1][key],
            )
        refresh_first_cell(reordered)
        reordered_binding = binding_for(reordered, "floor-reordered-members.json")
        self.assertTrue(
            any(
                "calibration_abba_member_order_mismatch" in problem
                for problem in reordered_binding.problems_by_cell[reordered["cells"][0]["cell_id"]]
            )
        )
        self.assertNotIn(
            reordered["cells"][0]["cell_id"], reordered_binding.bound_cell_ids
        )
        self.assertIn(
            "calibration_abba_member_order_mismatch",
            floor_binding_reason_codes(reordered_binding),
        )

        plan_bytes = calibration_plan_path.read_bytes()
        try:
            calibration_plan_path.write_bytes(plan_bytes + b" ")
            plan_binding = binding_for(exact_floor, "floor-tampered-plan.json")
        finally:
            calibration_plan_path.write_bytes(plan_bytes)
        self.assertIn(
            "calibration_plan_bytes_hash_mismatch", plan_binding.global_problems
        )
        self.assertFalse(plan_binding.bound_cell_ids)
        self.assertIn(
            "calibration_plan_bytes_hash_mismatch",
            floor_binding_reason_codes(plan_binding),
        )

        guard_tampered = json.loads(json.dumps(exact_floor))
        guard_tampered["idle_drift_guard"]["bundle_sha256"] = all_bound_hashes[25:27]
        guard_binding = binding_for(guard_tampered, "floor-tampered-guard.json")
        self.assertIn(
            "idle_drift_guard_provenance_mismatch", guard_binding.global_problems
        )
        self.assertFalse(guard_binding.bound_cell_ids)
        self.assertIn(
            "idle_drift_guard_provenance_mismatch",
            floor_binding_reason_codes(guard_binding),
        )

        fabricated = json.loads(json.dumps(exact_floor))
        fabricated_cell = fabricated["cells"][0]
        fake_observations = fabricated_cell["absolute"]["bundle_observations"]
        for observation in fake_observations:
            observation["metric_value_j"] += 1.0
        fabricated_cell["absolute"] = build_absolute_record(
            absolute_false_effect_floor(
                [observation["metric_value_j"] for observation in fake_observations],
                admissible_half_widths_j=[0.0] * len(fake_observations),
            ),
            fake_observations,
            consumption_semantics_id=fabricated_cell["absolute"][
                "consumption_semantics_id"
            ],
            whole_window_drift_allowance=fabricated_cell["absolute"][
                "whole_window_drift_allowance"
            ],
        )
        fabricated_cell["floor_abs_j"] = fabricated_cell["absolute"][
            "drift_widened_guarded_floor_j"
        ]
        fabricated_cell["floor_gate_j"] = max(
            fabricated_cell["floor_abs_j"], fabricated_cell["floor_cmp_j"]
        )
        fabricated["transport_groups"][0] = build_transport_group(
            transport_group_id=fabricated_cell["transport_group_id"],
            backend="mock",
            metric="gross_energy_j",
            window_class="request",
            stack_identity=fabricated_cell["source_regime"]["stack_identity"],
            source_cells=[fabricated_cell],
            allowed_consumer_condition_families=[
                {
                    key: fabricated_cell["key"][key]
                    for key in (
                        "condition_family_id",
                        "condition_family_definition",
                        "condition_family_sha256",
                    )
                }
            ],
        )
        fabricated_path = floor_dir / "floor-fabricated-metrics.json"
        fabricated_path.write_text(
            json.dumps(fabricated, indent=2) + "\n", encoding="utf-8"
        )
        fabricated_output = self.root / (
            f"fabricated-floor-claim-verdicts{scenario_suffix}.json"
        )
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as stderr:
            code = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(analysis_root),
                    "--evidence-root",
                    f"a10={evidence_roots['a10']}",
                    "--evidence-root",
                    f"window_c={evidence_roots['window_c']}",
                    "--floor-artifact",
                    str(fabricated_path),
                    "--output",
                    str(fabricated_output),
                ]
            )
        self.assertEqual(code, 0, stderr.getvalue())
        refused = json.loads(fabricated_output.read_text(encoding="utf-8"))
        affected_condition = fabricated_cell["key"]["condition_family_id"]
        affected = [
            resolution
            for contrast in refused["contrasts"]
            for resolution in contrast["floor"]["resolutions"]
            if resolution["source_cell_ids"] == []
            or affected_condition
            in {
                contrast["conditions"]["condition_a_id"],
                contrast["conditions"]["condition_b_id"],
            }
        ]
        self.assertTrue(affected)
        self.assertTrue(
            any(
                row["status"] == "refused"
                and "artifact_schema_invalid" in row["reason_codes"]
                for row in affected
            )
        )

    def test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal(self):
        self._exercise_cli_distinct_calibration_binding(
            production_identity=False,
        )

    def test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal_with_production_telemetry_identity(
        self,
    ):
        with (
            mock.patch(
                "joulewise.analysis_engine.inputs.custody_telemetry_identity",
                return_value=PRODUCTION_TELEMETRY_IDENTITY,
            ),
            mock.patch(
                "joulewise.analysis_engine.inputs.anchor_fallback_member_unusable",
                return_value=False,
            ),
        ):
            self._exercise_cli_distinct_calibration_binding(
                production_identity=True,
            )

    def test_cli_evidence_root_parser_rejects_malformed_and_duplicate_ids(self):
        base = [
            "analyze-claims",
            "--analysis-manifest",
            str(self.manifest_path),
            "--runs-root",
            str(self.runs_root),
            "--floor-artifact",
            str(self.floor_path),
            "--output",
            str(self.root / "parser-must-not-run.json"),
        ]
        cases = (
            (["--evidence-root", "a10"], "expected ID=PATH"),
            (["--evidence-root", f"={self.runs_root}"], "ID must be nonempty"),
            (["--evidence-root", "a10="], "PATH must be nonempty"),
            (
                [
                    "--evidence-root",
                    f"a10={self.runs_root}",
                    "--evidence-root",
                    f"a10={self.runs_root}",
                ],
                "duplicate evidence-root ID",
            ),
        )
        for evidence_args, expected in cases:
            with self.subTest(evidence_args=evidence_args):
                stderr = io.StringIO()
                with (
                    redirect_stderr(stderr),
                    self.assertRaises(SystemExit) as raised,
                ):
                    main([*base, *evidence_args])
                self.assertEqual(raised.exception.code, 2)
                self.assertIn(expected, stderr.getvalue())

    def test_claim_output_cannot_be_written_under_floor_evidence_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_root = Path(tmp)
            with self.assertRaisesRegex(
                AnalysisInputError,
                "output must be outside floor evidence roots",
            ):
                analyze_claims(
                    self.manifest_path,
                    self.runs_root,
                    self.floor_path,
                    strict_validator=validate_bundle,
                    evidence_roots={"a10": evidence_root},
                    output_path=evidence_root / "claim-verdicts.json",
                )

    def test_declared_evidence_roots_filters_valid_artifacts_and_fails_closed_on_read(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            supplied = {
                "a10": root / "a10",
                "window_c": root / "window-c",
                "unexpected": root / "unexpected",
            }
            self.assertEqual(
                declared_evidence_roots(self.floor_path, supplied),
                {
                    "a10": supplied["a10"],
                    "window_c": supplied["window_c"],
                },
            )
            self.assertIsNone(declared_evidence_roots(self.floor_path, None))

            missing = root / "missing.json"
            self.assertIs(declared_evidence_roots(missing, supplied), supplied)

            with mock.patch.object(
                Path,
                "read_bytes",
                side_effect=PermissionError("fixture unreadable"),
            ):
                self.assertIs(
                    declared_evidence_roots(self.floor_path, supplied),
                    supplied,
                )

            invalid_utf8 = root / "invalid-utf8.json"
            invalid_utf8.write_bytes(b"\xff")
            self.assertIs(
                declared_evidence_roots(invalid_utf8, supplied),
                supplied,
            )

            invalid_json = root / "invalid-json.json"
            invalid_json.write_text("{\n", encoding="utf-8")
            self.assertIs(
                declared_evidence_roots(invalid_json, supplied),
                supplied,
            )

            unusable = root / "unusable.json"
            unusable.write_text("[]\n", encoding="utf-8")
            self.assertIs(
                declared_evidence_roots(unusable, supplied),
                supplied,
            )

    def test_claim_output_separation_preserves_declared_root_and_ignores_surplus_symlink(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            declared_roots = {
                "a10": root / "a10",
                "window_c": root / "window-c",
            }
            for declared_root in declared_roots.values():
                declared_root.mkdir()

            exact_output = root / "exact-claim-verdicts.json"
            analyze_claims(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
                evidence_roots=declared_roots,
                output_path=exact_output,
            )
            self.assertTrue(exact_output.is_file())

            declared_target = root / "declared-target"
            declared_target.mkdir()
            declared_symlink = root / "declared-symlink"
            declared_symlink.symlink_to(declared_target, target_is_directory=True)
            with self.assertRaisesRegex(
                AnalysisInputError,
                "path_resolution_refused: symlink input",
            ):
                analyze_claims(
                    self.manifest_path,
                    self.runs_root,
                    self.floor_path,
                    strict_validator=validate_bundle,
                    evidence_roots={
                        **declared_roots,
                        "a10": declared_symlink,
                    },
                    output_path=root / "declared-symlink-must-not-write.json",
                )

            surplus_target = root / "surplus-target"
            surplus_target.mkdir()
            surplus_symlink = root / "surplus-symlink"
            surplus_symlink.symlink_to(surplus_target, target_is_directory=True)
            surplus_output = root / "surplus-symlink-claim-verdicts.json"
            analyze_claims(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
                evidence_roots={
                    **declared_roots,
                    "unexpected": surplus_symlink,
                },
                output_path=surplus_output,
            )
            self.assertTrue(surplus_output.is_file())

    def test_cli_output_separation_preserves_exact_and_absent_mapping_and_ignores_surplus_containment(
        self,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            declared_roots = {
                "a10": root / "a10",
                "window_c": root / "window-c",
            }
            for declared_root in declared_roots.values():
                declared_root.mkdir()
            evidence_args = [
                "--evidence-root",
                f"a10={declared_roots['a10']}",
                "--evidence-root",
                f"window_c={declared_roots['window_c']}",
            ]
            base = [
                "analyze-claims",
                "--analysis-manifest",
                str(self.manifest_path),
                "--runs-root",
                str(self.runs_root),
                "--floor-artifact",
                str(self.floor_path),
            ]

            exact_output = root / "exact-cli-claim-verdicts.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                exact_code = main(
                    [*base, *evidence_args, "--output", str(exact_output)]
                )
            self.assertEqual(exact_code, 0)
            self.assertTrue(exact_output.is_file())

            absent_output = root / "absent-cli-claim-verdicts.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                absent_code = main([*base, "--output", str(absent_output)])
            self.assertEqual(absent_code, 0)
            self.assertTrue(absent_output.is_file())

            declared_output = declared_roots["a10"] / "must-not-write.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                declared_code = main(
                    [*base, *evidence_args, "--output", str(declared_output)]
                )
            self.assertEqual(declared_code, 2)
            self.assertFalse(declared_output.exists())

            absent_refused_output = self.runs_root / "must-not-write-without-roots.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                absent_refused_code = main(
                    [*base, "--output", str(absent_refused_output)]
                )
            self.assertEqual(absent_refused_code, 2)
            self.assertFalse(absent_refused_output.exists())

            surplus_root = root / "surplus"
            surplus_root.mkdir()
            surplus_output = surplus_root / "claim-verdicts.json"
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                surplus_code = main(
                    [
                        *base,
                        *evidence_args,
                        "--evidence-root",
                        f"unexpected={surplus_root}",
                        "--output",
                        str(surplus_output),
                    ]
                )
            self.assertEqual(surplus_code, 0)
            self.assertTrue(surplus_output.is_file())

    def test_cli_writes_artifact_and_invalid_input_writes_nothing(self):
        output = self.root / "cli-claim-verdicts.json"
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(self.runs_root),
                    "--floor-artifact",
                    str(self.floor_path),
                    "--output",
                    str(output),
                ]
            )
        self.assertEqual(code, 0, stderr.getvalue())
        self.assertTrue(output.is_file())
        self.assertIn("claim-verdicts:", stdout.getvalue())
        invalid_floor = self.root / "invalid-floor.json"
        invalid_floor.write_text("{}\n", encoding="utf-8")
        refused_output = self.root / "must-not-exist.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            refused = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(self.runs_root),
                    "--floor-artifact",
                    str(invalid_floor),
                    "--output",
                    str(refused_output),
                ]
            )
        self.assertEqual(refused, 2)
        self.assertFalse(refused_output.exists())

    def test_cli_refuses_output_aliases_and_paths_inside_immutable_inputs(self):
        floor_before = self.floor_path.read_bytes()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            aliases_floor = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(self.runs_root),
                    "--floor-artifact",
                    str(self.floor_path),
                    "--output",
                    str(self.floor_path),
                ]
            )
        self.assertEqual(aliases_floor, 2)
        self.assertEqual(self.floor_path.read_bytes(), floor_before)

        inside_runs = self.runs_root / "must-not-write-claim-verdicts.json"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            inside = main(
                [
                    "analyze-claims",
                    "--analysis-manifest",
                    str(self.manifest_path),
                    "--runs-root",
                    str(self.runs_root),
                    "--floor-artifact",
                    str(self.floor_path),
                    "--output",
                    str(inside_runs),
                ]
            )
        self.assertEqual(inside, 2)
        self.assertFalse(inside_runs.exists())

    def test_legacy_flag_refuses_any_nonexact_six_bundle_manifest_set(self):
        with self.assertRaisesRegex(
            AnalysisInputError,
            "exactly the frozen six-bundle allowlist",
        ):
            analyze_claims(
                self.manifest_path,
                self.runs_root,
                self.floor_path,
                strict_validator=validate_bundle,
                legacy_l1_mechanics=True,
                legacy_allowlist=frozenset(),
            )

    def test_valid_replacement_fills_original_slot_without_sixth_block(self):
        runs = self.root / "replacement-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        shutil.rmtree(runs / target["run_id"])
        replacement = json.loads(
            (self.config_dir / target["config"]).read_text(encoding="utf-8")
        )
        replacement["run_id"] = target["run_id"] + "-replacement"
        replacement["run_metadata"]["tags"].extend(
            [
                f"analysis-replacement-of={target['entry_id']}",
                "analysis-replacement-reason=bundle_incomplete",
            ]
        )
        config_path = self.root / "replacement-config.json"
        config_path.write_text(json.dumps(replacement, indent=2) + "\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["run", str(config_path), "--runs-dir", str(runs)]), 0)
        install_passing_analysis_whole_window(
            runs,
            [
                replacement["run_id"]
                if entry["entry_id"] == target["entry_id"]
                else entry["run_id"]
                for entry in manifest["entries"]
            ],
            source_name="replacement-whole-window-source",
        )
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertEqual(artifact["sampling_audit"]["valid_replacements"], [])
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(
            len(artifact["sampling_audit"]["demoted_contrast_ids"]),
            12,
        )
        replacement_audit = next(
            row
            for row in artifact["bundle_audit"]
            if row["bundle_id"] == replacement["run_id"]
        )
        self.assertEqual(
            replacement_audit["replacement_classification"],
            "replacement_candidate",
        )
        self.assertEqual(replacement_audit["inclusion_status"], "excluded")
        self.assertIn(
            MOCK_TELEMETRY_CLAIM_REFUSAL,
            replacement_audit["base_reason_codes"],
        )
        affected = [
            contrast
            for contrast in artifact["contrasts"]
            if target["cell_id"]
            in {
                contrast["conditions"]["cell_a_id"],
                contrast["conditions"]["cell_b_id"],
            }
        ]
        self.assertTrue(affected)
        self.assertTrue(all(contrast["estimator"]["n"] == 0 for contrast in affected))
        self.assertTrue(
            all(
                MOCK_TELEMETRY_CLAIM_REFUSAL
                in contrast["claim_evaluation"]["reason_codes"]
                for contrast in affected
            )
        )

    def test_valid_replacement_fills_original_slot_without_sixth_block_with_production_telemetry_identity(
        self,
    ):
        runs = self.root / "replacement-production-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        shutil.rmtree(runs / target["run_id"])
        replacement = json.loads(
            (self.config_dir / target["config"]).read_text(encoding="utf-8")
        )
        replacement["run_id"] = target["run_id"] + "-production-replacement"
        replacement["run_metadata"]["tags"].extend(
            [
                f"analysis-replacement-of={target['entry_id']}",
                "analysis-replacement-reason=bundle_incomplete",
            ]
        )
        config_path = self.root / "replacement-production-config.json"
        config_path.write_text(
            json.dumps(replacement, indent=2) + "\n", encoding="utf-8"
        )
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(
                main(["run", str(config_path), "--runs-dir", str(runs)]),
                0,
            )
        install_passing_analysis_whole_window(
            runs,
            [
                replacement["run_id"]
                if entry["entry_id"] == target["entry_id"]
                else entry["run_id"]
                for entry in manifest["entries"]
            ],
            source_name="replacement-production-whole-window-source",
        )
        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
            artifact = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
        self.assertEqual(
            len(artifact["sampling_audit"]["valid_replacements"]),
            1,
        )
        self.assertFalse(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(
            artifact["sampling_audit"]["demoted_contrast_ids"],
            [],
        )
        affected = [
            contrast
            for contrast in artifact["contrasts"]
            if target["cell_id"]
            in {
                contrast["conditions"]["cell_a_id"],
                contrast["conditions"]["cell_b_id"],
            }
        ]
        self.assertTrue(affected)
        self.assertTrue(
            all(contrast["estimator"]["n"] == 5 for contrast in affected)
        )

    def test_replacement_with_changed_rep_tag_is_topup_not_slot_fill(self):
        runs = self.root / "wrong-rep-replacement-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        shutil.rmtree(runs / target["run_id"])
        replacement = json.loads(
            (self.config_dir / target["config"]).read_text(encoding="utf-8")
        )
        replacement["run_id"] = target["run_id"] + "-wrong-rep-replacement"
        replacement["run_metadata"]["tags"] = [
            "rep6" if tag == "rep1" else tag
            for tag in replacement["run_metadata"]["tags"]
        ]
        replacement["run_metadata"]["tags"].extend(
            [
                f"analysis-replacement-of={target['entry_id']}",
                "analysis-replacement-reason=bundle_incomplete",
            ]
        )
        config_path = self.root / "wrong-rep-replacement-config.json"
        config_path.write_text(
            json.dumps(replacement, indent=2) + "\n", encoding="utf-8"
        )
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["run", str(config_path), "--runs-dir", str(runs)]), 0)

        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertEqual(artifact["sampling_audit"]["valid_replacements"], [])
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        extra = next(
            row
            for row in artifact["bundle_audit"]
            if row["bundle_id"] == replacement["run_id"]
        )
        self.assertIn("config_hash_mismatch", extra["base_reason_codes"])

    def test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples(self):
        runs = self.root / "incomplete-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        shutil.rmtree(runs / target["run_id"])
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        affected = [
            contrast
            for contrast in artifact["contrasts"]
            if target["cell_id"]
            in {
                contrast["conditions"]["cell_a_id"],
                contrast["conditions"]["cell_b_id"],
            }
        ]
        self.assertEqual(len(affected), 12)
        for contrast in affected:
            with self.subTest(contrast=contrast["contrast_id"]):
                self.assertEqual(contrast["estimator"]["n"], 0)
                self.assertIsNone(contrast["estimator"]["df"])
                missing = next(
                    row
                    for row in contrast["bundle_blocks"]["blocks"]
                    if row["block_id"] == target["block_id"]
                )
                self.assertFalse(missing["included"])
                self.assertIn("bundle_missing", missing["reason_codes"])
                self.assertIn(
                    "fixed_n_plan_incomplete",
                    contrast["claim_evaluation"]["reason_codes"],
                )
                self.assertIn(
                    MOCK_TELEMETRY_CLAIM_REFUSAL,
                    contrast["claim_evaluation"]["reason_codes"],
                )
                self.assertEqual(
                    contrast["claim_evaluation"]["outcome"],
                    "not_estimable",
                )

    def test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity(
        self,
    ):
        runs = self.root / "incomplete-production-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        prepared_session = prepared_minted_consumption_session(
            runs,
            {entry["run_id"] for entry in manifest["entries"]},
        )
        shutil.rmtree(runs / target["run_id"])
        with (
            mock.patch(
                "joulewise.analysis_engine.inputs.custody_telemetry_identity",
                return_value=PRODUCTION_TELEMETRY_IDENTITY,
            ),
            mock.patch(
                "joulewise.analysis_engine.inputs.AuthenticatedConsumptionSession",
                return_value=prepared_session,
            ),
        ):
            artifact = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
        affected = [
            contrast
            for contrast in artifact["contrasts"]
            if target["cell_id"]
            in {
                contrast["conditions"]["cell_a_id"],
                contrast["conditions"]["cell_b_id"],
            }
        ]
        self.assertEqual(len(affected), 12)
        for contrast in affected:
            with self.subTest(contrast=contrast["contrast_id"]):
                self.assertEqual(contrast["estimator"]["n"], 4)
                self.assertEqual(contrast["estimator"]["df"], 3)
                missing = next(
                    row
                    for row in contrast["bundle_blocks"]["blocks"]
                    if row["block_id"] == target["block_id"]
                )
                self.assertFalse(missing["included"])
                self.assertIn("bundle_missing", missing["reason_codes"])
                self.assertIn(
                    "fixed_n_plan_incomplete",
                    contrast["claim_evaluation"]["reason_codes"],
                )
                self.assertEqual(
                    contrast["claim_evaluation"]["outcome"],
                    "not_resolvable",
                )

    def test_bundle_config_byte_mutation_is_excluded_even_when_identity_and_metadata_hash_match(self):
        runs = self.root / "config-byte-mutation-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        bundle = runs / target["run_id"]
        config_path = bundle / "config.json"
        config_path.write_bytes(config_path.read_bytes() + b" ")
        config_hash = hashlib.sha256(config_path.read_bytes()).hexdigest()
        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["config_sha256"] = config_hash
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        audit = next(
            row
            for row in artifact["bundle_audit"]
            if row["entry_id"] == target["entry_id"]
        )
        self.assertEqual(audit["inclusion_status"], "excluded")
        self.assertIn("config_hash_mismatch", audit["base_reason_codes"])
        self.assertNotEqual(
            audit["config_sha256"], audit["expected_config_sha256"]
        )

    def test_registered_bundle_symlink_escape_is_rejected(self):
        runs = self.root / "symlink-escape-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(entry for entry in manifest["entries"] if entry["role"] == "condition")
        outside = self.root / "outside-registered-bundle"
        shutil.copytree(runs / target["run_id"], outside)
        shutil.rmtree(runs / target["run_id"])
        (runs / target["run_id"]).symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(AnalysisInputError, "must not be a symlink"):
            analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )

    def test_public_engine_rejects_false_precheck_without_governed_reason(self):
        runs = self.root / "false-precheck-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition" and entry["planned_rep_index"] == 1
        )
        summary_path = runs / target["run_id"] / "summary_metrics.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["window_evidence_precheck"] = {
            "gross_request": {"eligible": False, "reasons": []}
        }
        summary_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        audit = next(
            row
            for row in artifact["bundle_audit"]
            if row["entry_id"] == target["entry_id"]
        )
        gross = audit["window_prechecks"]["gross_request"]
        self.assertFalse(gross["eligible"])
        self.assertIn("window_evidence_precheck_missing", gross["reasons"])

    def test_cleanup_suspect_is_excluded_even_with_stale_broad_runner_waiver(self):
        from joulewise import reduce as reduce_module

        runs = self.root / "cleanup-suspect-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition" and entry["planned_rep_index"] == 1
        )
        bundle = runs / target["run_id"]
        events_path = bundle / "events.jsonl"
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        cleanup = next(
            event
            for event in events
            if event["event_type"] == "stage_completed" and event["phase"] == "cleanup"
        )
        cleanup["metadata"]["cleanup_ok"] = False
        events_path.write_text(
            "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
            encoding="utf-8",
        )
        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata.setdefault("extra", {})["node_cleanup"] = [
            {"path": "/remote/tmp/joulewise-task", "removed": False}
        ]
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        summary = reduce_module.reduce_bundle(bundle)
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.assertEqual(validate_bundle(bundle, strict=True), [])

        unwaived = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        unwaived_audit = next(
            row for row in unwaived["bundle_audit"] if row["entry_id"] == target["entry_id"]
        )
        unwaived_inputs = load_analysis_inputs(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        unwaived_evidence = unwaived_inputs.registered[target["entry_id"]]
        self.assertEqual(
            unwaived_evidence.claim_evidence_flags,
            ("runtime_cleanup_ok", "remote_cleanup_failed"),
        )
        self.assertIsNone(unwaived_evidence.waiver)
        self.assertEqual(unwaived_audit["inclusion_status"], "excluded")
        self.assertIn("required_error_term_unknown", unwaived_audit["base_reason_codes"])
        affected = [
            contrast
            for contrast in unwaived["contrasts"]
            if target["cell_id"]
            in {
                contrast["conditions"]["cell_a_id"],
                contrast["conditions"]["cell_b_id"],
            }
        ]
        self.assertTrue(affected)
        self.assertTrue(
            all(
                "required_error_term_unknown"
                in contrast["claim_evaluation"]["reason_codes"]
                for contrast in affected
            )
        )

        campaign_dir = runs / "campaign_manifests"
        campaign_dir.mkdir(parents=True, exist_ok=True)
        waiver = {
            "target_kind": "bundle_id",
            "target": target["run_id"],
            "reason": "cleanup residue reviewed and bounded",
            "approver": "campaign-owner",
            "timestamp": "2026-07-11T00:00:00Z",
            "scope": "any",
        }
        (campaign_dir / "cleanup-waiver.json").write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.campaign_provenance.v1",
                    "session_id": "cleanup-waiver-fixture",
                    "created_at": "2026-07-11T00:00:00Z",
                    "config_dir": str(self.config_dir),
                    "analysis_manifest_id": manifest["manifest_id"],
                    "first_physical_run_id": None,
                    "members": [
                        {
                            "config": target["config"],
                            "run_id": target["run_id"],
                            "bundle_ids": [target["run_id"]],
                            "execution": "existing",
                            "preceding_campaign_cooldown": None,
                            "claim_evidence": [
                                {
                                    "bundle_id": target["run_id"],
                                    "claim_evidence_flags": [
                                        "runtime_cleanup_ok",
                                    ],
                                    "waiver": waiver,
                                }
                            ],
                        }
                    ],
                    "cooldown_gates": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        waived = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        waived_audit = next(
            row for row in waived["bundle_audit"] if row["entry_id"] == target["entry_id"]
        )
        waived_inputs = load_analysis_inputs(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        waived_evidence = waived_inputs.registered[target["entry_id"]]
        self.assertEqual(waived_audit["inclusion_status"], "excluded")
        self.assertIn("required_error_term_unknown", waived_audit["base_reason_codes"])
        self.assertIsNone(waived_evidence.waiver)

    def test_malformed_campaign_claim_evidence_refuses_with_analysis_input_error(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = manifest["entries"][0]
        malformed_values = (
            ("claim_evidence_flags", [["runtime_cleanup_ok"]]),
            ("bundle_id", [target["run_id"]]),
        )
        for field, value in malformed_values:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                runs = Path(tmp) / "runs"
                shutil.copytree(self.runs_root, runs)
                campaign_dir = runs / "campaign_manifests"
                campaign_dir.mkdir(parents=True, exist_ok=True)
                evidence = {
                    "bundle_id": target["run_id"],
                    "claim_evidence_flags": ["runtime_cleanup_ok"],
                    "waiver": None,
                }
                evidence[field] = value
                (campaign_dir / "malformed.json").write_text(
                    json.dumps(
                        {
                            "schema_version": "joulewise.campaign_provenance.v1",
                            "analysis_manifest_id": manifest["manifest_id"],
                            "members": [
                                {
                                    "config": target["config"],
                                    "run_id": target["run_id"],
                                    "bundle_ids": [target["run_id"]],
                                    "execution": "invoked",
                                    "claim_evidence": [evidence],
                                }
                            ],
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )

                with self.assertRaisesRegex(
                    AnalysisInputError, "malformed campaign claim evidence"
                ):
                    load_analysis_inputs(
                        self.manifest_path,
                        runs,
                        self.floor_path,
                        strict_validator=validate_bundle,
                    )

    def test_realized_model_artifact_identity_disagreement_fails_cohort_closed(self):
        runs = self.root / "identity-mismatch-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition" and entry["planned_rep_index"] == 1
        )
        metadata_path = runs / target["run_id"] / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["workload_provenance"]["model"]["artifact_identity"]["sha256"] = (
            "0" * 64
        )
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        audit = next(
            row
            for row in artifact["bundle_audit"]
            if row["entry_id"] == target["entry_id"]
        )
        self.assertEqual(audit["strict_status"], "valid")
        self.assertEqual(audit["inclusion_status"], "excluded")
        self.assertIn("config_hash_mismatch", audit["base_reason_codes"])

    def test_realized_identity_accepts_directory_shaped_model_artifact(self):
        fixture = Path("tests/fixtures/d078_r01")
        raw_config = json.loads(
            (fixture / "config.json").read_text(encoding="utf-8")
        )
        metadata = json.loads(
            (fixture / "metadata.json").read_text(encoding="utf-8")
        )
        artifact = metadata["workload_provenance"]["model"][
            "artifact_identity"
        ]
        self.assertEqual(artifact["kind"], "file_set")
        self.assertNotIn("sha256", artifact)

        identity = realized_scientific_identity(raw_config, metadata)

        self.assertIsNotNone(identity)
        self.assertEqual(
            identity["model_artifact"]["sha256"],
            artifact["folded_sha256"],
        )

    def test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis(self):
        runs = self.root / "topup-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        topup = json.loads((self.config_dir / target["config"]).read_text(encoding="utf-8"))
        topup["run_id"] = target["run_id"] + "-topup"
        topup["run_metadata"]["tags"] = [
            "rep6" if tag == "rep1" else tag
            for tag in topup["run_metadata"]["tags"]
        ]
        config_path = self.root / "topup-config.json"
        config_path.write_text(json.dumps(topup, indent=2) + "\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["run", str(config_path), "--runs-dir", str(runs)]), 0)
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(len(artifact["sampling_audit"]["demoted_contrast_ids"]), 12)
        demoted = [
            contrast
            for contrast in artifact["contrasts"]
            if contrast["sampling"]["confirmatory_status"] == "demoted_exploratory"
        ]
        self.assertEqual(len(demoted), 12)
        for contrast in demoted:
            self.assertEqual(contrast["estimator"]["n"], 0)
            self.assertIn(
                "outcome_dependent_top_up",
                contrast["claim_evaluation"]["reason_codes"],
            )
            self.assertIn(
                MOCK_TELEMETRY_CLAIM_REFUSAL,
                contrast["claim_evaluation"]["reason_codes"],
            )
            self.assertEqual(
                contrast["claim_evaluation"]["outcome"],
                "not_estimable",
            )
            self.assertFalse(contrast["claim_evaluation"]["claim_ready_for_l2_l3"])

        laundered = json.loads(json.dumps(artifact))
        laundered["sampling_audit"].update(
            unregistered_matching_bundles=[],
            top_up_detected=False,
            demoted_contrast_ids=[],
        )
        for contrast in laundered["contrasts"]:
            contrast["sampling"]["confirmatory_status"] = "confirmatory"
            evaluation = contrast["claim_evaluation"]
            evaluation["reason_codes"] = [
                reason
                for reason in evaluation["reason_codes"]
                if reason != "outcome_dependent_top_up"
            ]
        laundered["claim_verdicts_id"] = calculate_claim_verdicts_id(laundered)
        errors = validate_claim_verdicts(laundered)
        self.assertTrue(
            any("must exactly enumerate top-up audits" in error for error in errors),
            errors,
        )

    def test_unregistered_matching_topup_demotes_but_preserves_fixed_n_analysis_with_production_telemetry_identity(
        self,
    ):
        runs = self.root / "topup-production-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "condition"
            and entry["planned_rep_index"] == 1
            and entry["condition_id"] == "cond-2m-short_short"
        )
        topup = json.loads(
            (self.config_dir / target["config"]).read_text(encoding="utf-8")
        )
        topup["run_id"] = target["run_id"] + "-production-topup"
        topup["run_metadata"]["tags"] = [
            "rep6" if tag == "rep1" else tag
            for tag in topup["run_metadata"]["tags"]
        ]
        config_path = self.root / "topup-production-config.json"
        config_path.write_text(
            json.dumps(topup, indent=2) + "\n", encoding="utf-8"
        )
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(
                main(["run", str(config_path), "--runs-dir", str(runs)]),
                0,
            )
        with mock.patch(
            "joulewise.analysis_engine.inputs.custody_telemetry_identity",
            return_value=PRODUCTION_TELEMETRY_IDENTITY,
        ):
            artifact = analyze_claims(
                self.manifest_path,
                runs,
                self.floor_path,
                strict_validator=validate_bundle,
            )
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(
            len(artifact["sampling_audit"]["demoted_contrast_ids"]),
            12,
        )
        demoted = [
            contrast
            for contrast in artifact["contrasts"]
            if contrast["sampling"]["confirmatory_status"]
            == "demoted_exploratory"
        ]
        self.assertEqual(len(demoted), 12)
        for contrast in demoted:
            self.assertEqual(contrast["estimator"]["n"], 5)
            self.assertIn(
                "outcome_dependent_top_up",
                contrast["claim_evaluation"]["reason_codes"],
            )
            self.assertFalse(
                contrast["claim_evaluation"]["claim_ready_for_l2_l3"]
            )

    def test_unregistered_matching_sentinel_topup_demotes_linked_contrasts(self):
        runs = self.root / "sentinel-topup-runs"
        shutil.copytree(self.runs_root, runs)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        target = next(
            entry
            for entry in manifest["entries"]
            if entry["role"] == "drift_sentinel_start"
            and entry["planned_rep_index"] == 1
        )
        topup = json.loads((self.config_dir / target["config"]).read_text(encoding="utf-8"))
        topup["run_id"] = target["run_id"] + "-topup"
        topup["run_metadata"]["tags"] = [
            "rep6" if tag == "rep1" else tag
            for tag in topup["run_metadata"]["tags"]
        ]
        config_path = self.root / "sentinel-topup-config.json"
        config_path.write_text(json.dumps(topup, indent=2) + "\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["run", str(config_path), "--runs-dir", str(runs)]), 0)
        artifact = analyze_claims(
            self.manifest_path,
            runs,
            self.floor_path,
            strict_validator=validate_bundle,
        )
        self.assertTrue(artifact["sampling_audit"]["top_up_detected"])
        self.assertEqual(len(artifact["sampling_audit"]["demoted_contrast_ids"]), 24)
        self.assertTrue(
            all(
                contrast["sampling"]["confirmatory_status"]
                == "demoted_exploratory"
                for contrast in artifact["contrasts"]
            )
        )


if __name__ == "__main__":
    unittest.main()


class SupersessionAwareCooldownJoinTests(unittest.TestCase):
    """Declaration-first cooldown-join and supersession regressions."""

    @staticmethod
    def _manifest(
        tmp: Path,
        name: str,
        session: str,
        bundle_id: str,
        *,
        analysis_manifest_id: str | None = None,
        cooldown: object | None = None,
        execution: str = "invoked",
        outcome: str | None = None,
        schema_version: str = "joulewise.campaign_provenance.v1",
    ) -> Path:
        campaign_dir = tmp / "campaign_manifests"
        campaign_dir.mkdir(parents=True, exist_ok=True)
        if cooldown is None:
            cooldown = {
                "result": "first_run_exempt",
                "session_id": session,
                "following_run_id": bundle_id,
            }
        manifest = {
            "schema_version": schema_version,
            "analysis_manifest_id": analysis_manifest_id,
            "session_id": session,
            "first_physical_run_id": bundle_id,
            "members": [
                {
                    "config": f"{bundle_id}.json",
                    "execution": execution,
                    "run_id": bundle_id,
                    "bundle_ids": [bundle_id],
                    "preceding_campaign_cooldown": (
                        cooldown if execution == "invoked" else None
                    ),
                }
            ],
        }
        if outcome is not None:
            manifest["members"][0]["outcome"] = outcome
        path = campaign_dir / name
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    @staticmethod
    def _attest(root: Path, manifest_path: Path, **changes: object) -> dict:
        from joulewise.campaign_provenance import campaign_provenance_attestation

        raw = manifest_path.read_bytes()
        manifest = json.loads(raw.decode("utf-8"))
        row = campaign_provenance_attestation(
            manifest_path=manifest_path,
            raw_manifest_bytes=raw,
            manifest=manifest,
            timestamp="2026-08-01T12:00:00Z",
        )
        row.update(changes)
        log_path = root / "campaign_log.jsonl"
        prior = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        log_path.write_text(
            prior + json.dumps(row, sort_keys=True) + "\n", encoding="utf-8"
        )
        return row

    def _install_legacy_existing_binding(
        self,
        root: Path,
        manifest_name: str,
        *,
        outcome: str = "usable",
    ) -> dict:
        manifest_path = root / "campaign_manifests" / manifest_name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        member = manifest["members"][0]
        status = {
            "usable": "skipped",
            "failed": "failed",
            "incomplete": "incomplete_existing",
            "waived": "waived",
        }[outcome]
        classification = (
            outcome if outcome in {"usable", "failed", "waived"} else "usable"
        )
        member_rows = []
        for bundle_id in member["bundle_ids"]:
            row = {
                "bundle_id": bundle_id,
                "status": "succeeded" if classification == "usable" else "failed",
                "strict_valid": classification == "usable",
                "collection_integrity_flags": (
                    [] if classification == "usable" else ["fixture_failure"]
                ),
                "collection_classification": classification,
            }
            if classification == "waived":
                row["waiver"] = {"scope": "fixture_failure"}
            member_rows.append(row)
        log_row = {
            "status": status,
            "run_id": member["run_id"],
            "config": str(root / "configs" / member["config"]),
            "campaign_provenance_manifest": str(manifest_path.resolve()),
            "members": member_rows,
        }
        log_path = root / "campaign_log.jsonl"
        prior = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        log_path.write_text(
            prior + json.dumps(log_row, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return log_row

    def _install_real_supersession(
        self,
        root: Path,
        bundle_id: str,
        *,
        selected_manifest: str | tuple[str, int],
        superseded_manifests: list[str | tuple[str, int]],
    ) -> dict:
        from joulewise.whole_window import (
            OCCURRENCE_SUPERSESSION_SCHEMA,
            supersession_entry_sha256,
        )

        canonical = root / bundle_id
        canonical.mkdir()
        quarantine = Path(tempfile.mkdtemp(prefix="d5j-quarantine-"))
        self.addCleanup(shutil.rmtree, quarantine, ignore_errors=True)
        custody_hashes = {}
        for name, payload in (
            ("config.json", {"run_id": bundle_id}),
            ("metadata.json", {"status": "failed"}),
            ("summary_metrics.json", {"status": "failed"}),
        ):
            raw = (json.dumps(payload, sort_keys=True) + "\n").encode()
            (canonical / name).write_bytes(raw)
            (quarantine / name).write_bytes(raw)
            custody_hashes[name] = hashlib.sha256(raw).hexdigest()

        def occurrence(manifest_ref: str | tuple[str, int]) -> dict:
            manifest_name, bundle_index = (
                (manifest_ref, 0)
                if isinstance(manifest_ref, str)
                else manifest_ref
            )
            path = root / "campaign_manifests" / manifest_name
            return {
                "bundle_id": bundle_id,
                "source_manifest": {
                    "path": f"campaign_manifests/{manifest_name}",
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                },
                "member_index": 0,
                "bundle_index": bundle_index,
            }

        entry = {
            "schema_version": OCCURRENCE_SUPERSESSION_SCHEMA,
            "record_type": "campaign_occurrence_supersession",
            "runs_root": str(root.resolve()),
            "bundle_id": bundle_id,
            "reason": "failed occurrence quarantined before retry",
            "selected_occurrence": occurrence(selected_manifest),
            "superseded_occurrences": [
                occurrence(name) for name in superseded_manifests
            ],
            "quarantine": {
                "path": str(quarantine.resolve()),
                "config_sha256": custody_hashes["config.json"],
                "metadata_sha256": custody_hashes["metadata.json"],
                "summary_sha256": custody_hashes["summary_metrics.json"],
            },
        }
        entry["entry_sha256"] = supersession_entry_sha256(entry)
        log_path = root / "campaign_log.jsonl"
        prior = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        log_path.write_text(
            prior + json.dumps(entry, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return entry

    def _duplicated_root(self) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="fix9-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self._manifest(tmp, "campaign-a.json", "session-a", "dup-bundle")
        self._manifest(tmp, "campaign-b.json", "session-b", "dup-bundle")
        return tmp

    def _physical_manifest_root(self, members: list[dict]) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="fix10-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        campaign_dir = tmp / "campaign_manifests"
        campaign_dir.mkdir(parents=True)
        manifest = {
            "schema_version": "joulewise.campaign_provenance.v1",
            "analysis_manifest_id": None,
            "session_id": "physical-session",
            "first_physical_run_id": "dup-bundle",
            "members": members,
        }
        (campaign_dir / "physical.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        return tmp

    @staticmethod
    def _physical_member(
        bundle_ids: list[str], physical_members: list[dict]
    ) -> dict:
        return {
            "execution": "invoked",
            "run_id": "dup-bundle",
            "bundle_ids": bundle_ids,
            "physical_members": physical_members,
        }

    @staticmethod
    def _first_exempt_cooldown() -> dict:
        return {
            "result": "first_run_exempt",
            "session_id": "physical-session",
            "following_run_id": "dup-bundle",
        }

    def test_duplicate_without_supersession_still_refuses(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        resolved = _campaign_cooldown_evidence(self._duplicated_root(), None)
        row = resolved["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_authenticated_v2_invoked_then_existing_accepts_every_outcome(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        for outcome in ("usable", "failed", "incomplete", "waived"):
            with self.subTest(outcome=outcome):
                root = Path(tempfile.mkdtemp(prefix=f"gauntlet-v2-i-e-{outcome}-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                invoked = self._manifest(
                    root,
                    "00-invoked.json",
                    "invoked-session",
                    "bundle",
                    schema_version="joulewise.campaign_provenance.v2",
                )
                existing = self._manifest(
                    root,
                    "01-existing.json",
                    "existing-session",
                    "bundle",
                    execution="existing",
                    outcome=outcome,
                    schema_version="joulewise.campaign_provenance.v2",
                )
                self._attest(root, invoked)
                self._attest(root, existing)

                row = _campaign_cooldown_evidence(root, None)["bundle"]
                self.assertTrue(row["verified"])
                self.assertEqual(row["manifest"], "campaign_manifests/00-invoked.json")

    def test_v1_existing_outcome_cannot_bypass_missing_log_binding(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-b1-v1-outcome-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(root, "00-invoked.json", "invoked-session", "bundle")
        self._manifest(
            root,
            "01-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="usable",
        )

        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_real_v1_relabel_without_writer_attestation_refuses_globally(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-b1-relabel-probe-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        fixture = (
            ROOT
            / "tests"
            / "fixtures"
            / "cooldown_join"
            / "real_7b_v1_existing_manifest.json"
        )
        existing_path = root / "campaign_manifests" / "real.json"
        existing_path.parent.mkdir(parents=True)
        shutil.copyfile(fixture, existing_path)

        fixture_raw = existing_path.read_bytes()
        v1 = b'"schema_version": "joulewise.campaign_provenance.v1"'
        v2 = b'"schema_version": "joulewise.campaign_provenance.v2"'
        execution = b'      "execution": "existing",\n'
        outcome = b'      "outcome": "usable",\n'
        self.assertEqual(fixture_raw.count(v1), 1)
        self.assertEqual(fixture_raw.count(execution), 1)
        relabelled_raw = fixture_raw.replace(v1, v2, 1).replace(
            execution,
            execution + outcome,
            1,
        )
        self.assertEqual(
            relabelled_raw.replace(v2, v1, 1).replace(outcome, b"", 1),
            fixture_raw,
        )
        existing_path.write_bytes(relabelled_raw)

        # This proves only absence of writer-minted external evidence.  The
        # attestation is anti-malformation, not a secret-key tamper signature.
        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

        self._attest(root, existing_path)
        joined = _campaign_cooldown_evidence(root, None)
        self.assertEqual(
            joined,
            {
                "neg8-window-midpoint": {
                    "result": "unknown",
                    "verified": False,
                    "session_id": None,
                    "manifest": None,
                    "raw_artifact": None,
                }
            },
        )

    def test_authenticated_bare_v2_existing_reaches_join_refusal(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-v2-e-only-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        manifest = self._manifest(
            root,
            "00-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="usable",
            schema_version="joulewise.campaign_provenance.v2",
        )
        self._attest(root, manifest)

        row = _campaign_cooldown_evidence(root, None)["bundle"]
        self.assertFalse(row["verified"])
        self.assertEqual(row["result"], "unknown")

    def test_v2_attestation_matrix_fails_closed_except_exact_current_binding(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        for case in (
            "valid",
            "missing",
            "mismatched",
            "malformed",
            "stale_only",
            "stale_plus_current",
            "duplicate_current",
        ):
            with self.subTest(case=case):
                root = Path(tempfile.mkdtemp(prefix=f"gauntlet-attest-{case}-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                manifest = self._manifest(
                    root,
                    "current.json",
                    "current-session",
                    "bundle",
                    schema_version="joulewise.campaign_provenance.v2",
                )
                if case == "valid":
                    self._attest(root, manifest)
                elif case == "mismatched":
                    self._attest(
                        root,
                        manifest,
                        campaign_provenance_session_id="other-session",
                    )
                elif case == "malformed":
                    self._attest(
                        root,
                        manifest,
                        campaign_provenance_manifest="current.json",
                    )
                elif case in {"stale_only", "stale_plus_current"}:
                    self._attest(
                        root,
                        manifest,
                        campaign_provenance_manifest_sha256="0" * 64,
                    )
                    if case == "stale_plus_current":
                        self._attest(root, manifest)
                elif case == "duplicate_current":
                    self._attest(root, manifest)
                    self._attest(root, manifest)

                joined = _campaign_cooldown_evidence(root, None)
                if case in {"valid", "stale_plus_current"}:
                    self.assertTrue(joined["bundle"]["verified"])
                else:
                    self.assertEqual(joined, {})

    def test_attestation_reader_path_classification_table(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        malformed = (
            "current.json",
            "./campaign_manifests/current.json",
            "campaign_manifests//current.json",
            "/campaign_manifests/current.json",
            "campaign_manifests\\current.json",
            "campaign_manifests/./current.json",
            "campaign_manifests/nested/current.json",
            "campaign_manifests/",
            "campaign_manifests/.json",
            "campaign_manifests/current.JSON",
        )
        stale = (
            "campaign_manifests/nul\x00name.json",
            "campaign_manifests/line\nbreak.json",
            "campaign_manifests/unicodé.json",
            "campaign_manifests/.leading-dot.json",
            "campaign_manifests/back\\slash.json",
            "campaign_manifests/ordinary-missing.json",
        )
        for classification, variants in (("malformed", malformed), ("stale", stale)):
            for variant in variants:
                with self.subTest(classification=classification, variant=variant):
                    root = Path(
                        tempfile.mkdtemp(prefix="gauntlet-attest-path-")
                    )
                    self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                    manifest = self._manifest(
                        root,
                        "current.json",
                        "current-session",
                        "bundle",
                        schema_version="joulewise.campaign_provenance.v2",
                    )
                    self._attest(root, manifest)
                    self.assertTrue(
                        _campaign_cooldown_evidence(root, None)["bundle"][
                            "verified"
                        ]
                    )
                    self._attest(
                        root,
                        manifest,
                        campaign_provenance_manifest=variant,
                    )

                    joined = _campaign_cooldown_evidence(root, None)
                    if classification == "malformed":
                        self.assertEqual(joined, {})
                    else:
                        self.assertTrue(joined["bundle"]["verified"])

        with self.subTest(classification="positive-control"):
            root = Path(tempfile.mkdtemp(prefix="gauntlet-attest-path-"))
            self.addCleanup(shutil.rmtree, root, ignore_errors=True)
            manifest = self._manifest(
                root,
                "current.json",
                "current-session",
                "bundle",
                schema_version="joulewise.campaign_provenance.v2",
            )
            self._attest(root, manifest)
            self.assertTrue(
                _campaign_cooldown_evidence(root, None)["bundle"]["verified"]
            )

    def test_v2_outcome_presence_and_closed_enum_are_global_catalog_gates(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        cases = (
            ("existing", None),
            ("existing", "unknown"),
            ("invoked", "usable"),
            ("blocked_before_invoke", "failed"),
        )
        for execution, outcome in cases:
            with self.subTest(execution=execution, outcome=outcome):
                root = Path(tempfile.mkdtemp(prefix="gauntlet-v2-outcome-wire-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                invalid = self._manifest(
                    root,
                    "invalid.json",
                    "invalid-session",
                    "bundle",
                    execution=execution,
                    outcome=outcome,
                    schema_version="joulewise.campaign_provenance.v2",
                )
                self._attest(root, invalid)
                self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_authenticated_v2_failed_existing_then_retry_refuses_without_repair(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-v2-e-i-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        manifests = [self._manifest(
            root,
            "00-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="failed",
            schema_version="joulewise.campaign_provenance.v2",
        )]
        manifests.append(self._manifest(
            root,
            "01-existing.json",
            "second-existing-session",
            "bundle",
            execution="existing",
            outcome="failed",
            schema_version="joulewise.campaign_provenance.v2",
        ))
        manifests.append(self._manifest(
            root,
            "02-invoked.json",
            "invoked-session",
            "bundle",
            schema_version="joulewise.campaign_provenance.v2",
        ))
        for manifest in manifests:
            self._attest(root, manifest)

        row = _campaign_cooldown_evidence(root, None)["bundle"]
        self.assertFalse(row["verified"])

    def test_authenticated_v2_failed_existing_retry_accepts_exact_repair(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import (
            validate_occurrence_supersession_entry,
            validated_supersession_entries,
        )

        root = Path(tempfile.mkdtemp(prefix="gauntlet-v2-e-i-repair-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        manifests = [self._manifest(
            root,
            "00-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="failed",
            schema_version="joulewise.campaign_provenance.v2",
        )]
        manifests.append(self._manifest(
            root,
            "01-existing.json",
            "second-existing-session",
            "bundle",
            execution="existing",
            outcome="failed",
            schema_version="joulewise.campaign_provenance.v2",
        ))
        manifests.append(self._manifest(
            root,
            "02-invoked.json",
            "invoked-session",
            "bundle",
            schema_version="joulewise.campaign_provenance.v2",
        ))
        for manifest in manifests:
            self._attest(root, manifest)
        entry = self._install_real_supersession(
            root,
            "bundle",
            selected_manifest="02-invoked.json",
            superseded_manifests=["00-existing.json"],
        )

        self.assertTrue(validate_occurrence_supersession_entry(entry, root))
        self.assertEqual(validated_supersession_entries(root), [entry])
        row = _campaign_cooldown_evidence(root, None)["bundle"]
        self.assertTrue(row["verified"])
        self.assertEqual(row["manifest"], "campaign_manifests/02-invoked.json")

    def test_legacy_existing_aliases_bind_every_closed_log_outcome(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        for outcome in ("usable", "failed", "incomplete", "waived"):
            with self.subTest(outcome=outcome):
                root = Path(tempfile.mkdtemp(prefix=f"gauntlet-v1-{outcome}-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                self._manifest(
                    root, "00-invoked.json", "invoked-session", "bundle"
                )
                self._manifest(
                    root,
                    "01-existing.json",
                    "existing-session",
                    "bundle",
                    execution="existing",
                )
                self._install_legacy_existing_binding(
                    root, "01-existing.json", outcome=outcome
                )

                row = _campaign_cooldown_evidence(root, None)["bundle"]

                self.assertEqual(row["result"], "first_run_exempt")
                self.assertTrue(row["verified"])
                self.assertEqual(
                    row["manifest"], "campaign_manifests/00-invoked.json"
                )

    def test_one_legacy_log_row_cannot_authenticate_two_existing_members(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-b2-log-reuse-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        manifest_path = self._manifest(
            root, "physical.json", "physical-session", "bundle"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        existing = {
            **manifest["members"][0],
            "execution": "existing",
            "preceding_campaign_cooldown": None,
        }
        manifest["members"].extend([existing, dict(existing)])
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self._install_legacy_existing_binding(root, "physical.json")

        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_legacy_existing_binding_failures_refuse_join_globally(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        for case in (
            "missing",
            "inconsistent",
            "conflicting",
            "ambiguous",
            "unparseable",
        ):
            with self.subTest(case=case):
                root = Path(tempfile.mkdtemp(prefix=f"gauntlet-v1-{case}-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                self._manifest(
                    root,
                    "00-existing.json",
                    "existing-session",
                    "bundle",
                    execution="existing",
                )
                self._manifest(root, "01-invoked.json", "invoked-session", "bundle")
                if case != "missing":
                    row = self._install_legacy_existing_binding(
                        root, "00-existing.json"
                    )
                    log_path = root / "campaign_log.jsonl"
                    if case in {"inconsistent", "conflicting"}:
                        original = json.loads(json.dumps(row))
                        row["members"][0]["bundle_id"] = "other-bundle"
                        log_path.write_text(
                            (
                                json.dumps(original, sort_keys=True) + "\n"
                                if case == "conflicting"
                                else ""
                            )
                            + json.dumps(row, sort_keys=True)
                            + "\n",
                            encoding="utf-8",
                        )
                    elif case == "ambiguous":
                        log_path.write_text(
                            log_path.read_text(encoding="utf-8")
                            + json.dumps(row, sort_keys=True)
                            + "\n",
                            encoding="utf-8",
                        )
                    elif case == "unparseable":
                        log_path.write_text(
                            log_path.read_text(encoding="utf-8") + "{not-json\n",
                            encoding="utf-8",
                        )

                self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_unknown_prospective_existing_outcome_refuses_join_globally(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-v2-unknown-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        invalid = self._manifest(
            root,
            "00-existing.json",
            "existing-session",
            "bundle",
            execution="existing",
            outcome="surprising",
            schema_version="joulewise.campaign_provenance.v2",
        )
        invoked = self._manifest(
            root,
            "01-invoked.json",
            "invoked-session",
            "bundle",
            schema_version="joulewise.campaign_provenance.v2",
        )
        self._attest(root, invalid)
        self._attest(root, invoked)

        # D-097: a v2 existing outcome outside the closed enum refuses globally.
        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_result_map_keyset_unions_candidates_and_declared_ids(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        declared_only = "declared-with-zero-emissions"
        root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle", declared_only],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        }
                    ],
                )
            ]
        )

        joined = _campaign_cooldown_evidence(root, None)

        candidate_ids = {"dup-bundle"}
        declared_ids = {"dup-bundle", declared_only}
        self.assertEqual(set(joined), candidate_ids | declared_ids)

    def test_unresolved_declared_id_has_exact_refusal_payload(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = self._physical_manifest_root(
            [self._physical_member(["dup-bundle"], [])]
        )

        self.assertEqual(
            _campaign_cooldown_evidence(root, None),
            {
                "dup-bundle": {
                    "result": "unknown",
                    "verified": False,
                    "session_id": None,
                    "manifest": None,
                    "raw_artifact": None,
                }
            },
        )

    def test_repeated_declared_bundle_with_malformed_physical_row_refuses(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle", "dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        },
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": "malformed",
                        },
                    ],
                )
            ]
        )

        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_b1_partial_supersession_cannot_launder_malformed_declaration(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import (
            validate_occurrence_supersession_entry,
            validated_supersession_entries,
        )

        root = Path(tempfile.mkdtemp(prefix="d5j-b1-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(root, "campaign-a.json", "session-a", "dup-bundle")
        self._manifest(root, "campaign-b.json", "session-b", "dup-bundle")
        self._manifest(
            root,
            "campaign-c.json",
            "session-c",
            "dup-bundle",
            cooldown="malformed",
        )
        entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest="campaign-b.json",
            superseded_manifests=["campaign-a.json"],
        )

        self.assertTrue(validate_occurrence_supersession_entry(entry, root))
        self.assertEqual(validated_supersession_entries(root), [entry])
        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_other_catalog_declaration_does_not_create_duplicate(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="d5j-b2-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "selected.json",
            "selected-session",
            "dup-bundle",
            analysis_manifest_id="selected",
        )
        self._manifest(
            root,
            "filtered-sibling.json",
            "filtered-session",
            "dup-bundle",
            analysis_manifest_id="other",
        )

        row = _campaign_cooldown_evidence(root, "selected")["dup-bundle"]
        self.assertEqual(row["result"], "first_run_exempt")
        self.assertTrue(row["verified"])
        self.assertEqual(row["manifest"], "campaign_manifests/selected.json")

    def test_campaign_provenance_aggregation_call_site_fence(self):
        production_paths = list((ROOT / "joulewise").rglob("*.py")) + list(
            (ROOT / "scripts").glob("*.py")
        )
        catalog_calls: dict[str, int] = {}
        dereference_calls: dict[str, int] = {}
        catalog_importers: set[str] = set()
        dereference_importers: set[str] = set()
        for path in production_paths:
            relative = path.relative_to(ROOT).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == "load_authenticated_campaign_catalog":
                        catalog_calls[relative] = catalog_calls.get(relative, 0) + 1
                    if node.func.id == "load_authenticated_campaign_manifest":
                        dereference_calls[relative] = (
                            dereference_calls.get(relative, 0) + 1
                        )
                if isinstance(node, ast.ImportFrom) and node.module == (
                    "joulewise.campaign_provenance"
                ):
                    imported = {alias.name for alias in node.names}
                    if "load_authenticated_campaign_catalog" in imported:
                        catalog_importers.add(relative)
                    if "load_authenticated_campaign_manifest" in imported:
                        dereference_importers.add(relative)

        self.assertEqual(
            catalog_calls,
            {
                "joulewise/analysis_engine/inputs.py": 2,
                "scripts/run_campaign.py": 4,
            },
        )
        self.assertEqual(sum(catalog_calls.values()), 6)
        self.assertEqual(catalog_importers, set(catalog_calls))
        self.assertEqual(
            dereference_calls,
            {"joulewise/whole_window.py": 1},
        )
        self.assertEqual(
            dereference_importers,
            {"joulewise/whole_window.py"},
        )

    def test_b2_wrong_schema_duplicate_or_unreadable_catalog_refuses_join(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        for label, sibling in (
            ("unreadable", b"{ this is not json"),
            (
                "wrong-schema",
                json.dumps(
                    {
                        "schema_version": "joulewise.campaign_provenance.v999",
                        "analysis_manifest_id": "selected",
                        "members": [
                            {
                                "execution": "invoked",
                                "run_id": "solo-bundle",
                                "bundle_ids": ["solo-bundle"],
                                "preceding_campaign_cooldown": "malformed",
                            }
                        ],
                    }
                ).encode(),
            ),
        ):
            with self.subTest(label=label):
                root = Path(tempfile.mkdtemp(prefix=f"d5j-catalog-{label}-"))
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                self._manifest(
                    root,
                    "selected.json",
                    "selected-session",
                    "solo-bundle",
                    analysis_manifest_id="selected",
                )
                (root / "campaign_manifests" / "sibling.json").write_bytes(sibling)
                self.assertEqual(
                    _campaign_cooldown_evidence(root, "selected"),
                    {},
                )

    def test_nonselected_manifest_with_nonobject_member_refuses_catalog(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-b3-catalog-member-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "selected.json",
            "selected-session",
            "bundle",
            analysis_manifest_id="selected",
        )
        sibling = {
            "schema_version": "joulewise.campaign_provenance.v1",
            "analysis_manifest_id": "other",
            "members": [None],
        }
        (root / "campaign_manifests" / "sibling.json").write_text(
            json.dumps(sibling), encoding="utf-8"
        )

        self.assertEqual(_campaign_cooldown_evidence(root, "selected"), {})

    def test_cross_member_duplicate_with_malformed_physical_row_refuses(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        }
                    ],
                ),
                self._physical_member(
                    ["dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": "malformed",
                        }
                    ],
                ),
            ]
        )

        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_repeated_declarations_use_true_positions_for_supersession(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import validated_supersession_entries

        root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle", "dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        },
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        },
                    ],
                )
            ]
        )
        entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest=("physical.json", 0),
            superseded_manifests=[("physical.json", 1)],
        )

        self.assertEqual(validated_supersession_entries(root), [entry])
        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "first_run_exempt")
        self.assertTrue(row["verified"])
        self.assertEqual(row["manifest"], "campaign_manifests/physical.json")

    def test_single_declared_occurrence_keeps_physical_and_legacy_resolution(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        physical_root = self._physical_manifest_root(
            [
                self._physical_member(
                    ["dup-bundle"],
                    [
                        {
                            "bundle_id": "dup-bundle",
                            "preceding_campaign_cooldown": (
                                self._first_exempt_cooldown()
                            ),
                        }
                    ],
                )
            ]
        )
        physical = _campaign_cooldown_evidence(physical_root, None)["dup-bundle"]
        self.assertEqual(physical["result"], "first_run_exempt")
        self.assertTrue(physical["verified"])
        self.assertEqual(physical["manifest"], "campaign_manifests/physical.json")

        legacy_root = Path(tempfile.mkdtemp(prefix="fix10-legacy-"))
        self.addCleanup(shutil.rmtree, legacy_root, ignore_errors=True)
        self._manifest(
            legacy_root, "legacy.json", "legacy-session", "single-bundle"
        )
        legacy = _campaign_cooldown_evidence(legacy_root, None)["single-bundle"]
        self.assertEqual(legacy["result"], "first_run_exempt")
        self.assertTrue(legacy["verified"])
        self.assertEqual(legacy["manifest"], "campaign_manifests/legacy.json")

    def test_valid_supersession_resolves_selected_occurrence(self):
        from joulewise.analysis_engine import inputs as inputs_module

        entry = {
            "record_type": "campaign_occurrence_supersession",
            "bundle_id": "dup-bundle",
            "selected_occurrence": {
                "source_manifest": {"path": "campaign_manifests/campaign-b.json"},
                "member_index": 0,
                "bundle_index": 0,
            },
            "superseded_occurrences": [
                {
                    "source_manifest": {
                        "path": "campaign_manifests/campaign-a.json"
                    },
                    "member_index": 0,
                    "bundle_index": 0,
                }
            ],
        }
        with unittest.mock.patch.object(
            inputs_module,
            "supersession_entry_validation_results",
            return_value=([entry], [True]),
        ):
            resolved = inputs_module._campaign_cooldown_evidence(
                self._duplicated_root(), None
            )
        row = resolved["dup-bundle"]
        self.assertEqual(row["manifest"], "campaign_manifests/campaign-b.json")
        self.assertEqual(row["session_id"], "session-b")

    def test_validated_log_supersession_selects_governing_cooldown_row(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import (
            validate_occurrence_supersession_entry,
            validated_supersession_entries,
        )

        root = self._duplicated_root()
        bundle_id = "dup-bundle"
        entry = self._install_real_supersession(
            root,
            bundle_id,
            selected_manifest="campaign-b.json",
            superseded_manifests=["campaign-a.json"],
        )
        self.assertTrue(validate_occurrence_supersession_entry(entry, root))
        self.assertEqual(validated_supersession_entries(root), [entry])

        row = _campaign_cooldown_evidence(root, None)[bundle_id]
        self.assertEqual(row["manifest"], "campaign_manifests/campaign-b.json")
        self.assertEqual(row["session_id"], "session-b")
        self.assertTrue(row["verified"])

    def test_v4_valid_exact_plus_corrupted_same_bundle_clone_refuses(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import (
            supersession_entry_validation_results,
            validated_supersession_entries,
        )

        root = self._duplicated_root()
        entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest="campaign-b.json",
            superseded_manifests=["campaign-a.json"],
        )
        corrupted_clone = dict(entry)
        corrupted_clone["entry_sha256"] = "0" * 64
        with (root / "campaign_log.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(corrupted_clone, sort_keys=True) + "\n")

        raw = supersession_entry_validation_results(root)
        self.assertIsNotNone(raw)
        assert raw is not None
        self.assertEqual(raw[0], [entry, corrupted_clone])
        self.assertEqual(raw[1], [True, False])
        self.assertEqual(validated_supersession_entries(root), [entry])
        row = _campaign_cooldown_evidence(root, None)["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def test_d093_visibility_scan_records_divergence_before_consumption(self):
        from joulewise.analysis_engine.inputs import supersession_visibility_scan

        root = self._duplicated_root()
        entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest="campaign-b.json",
            superseded_manifests=["campaign-a.json"],
        )
        corrupted_clone = dict(entry)
        corrupted_clone["entry_sha256"] = "0" * 64
        with (root / "campaign_log.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(corrupted_clone, sort_keys=True) + "\n")

        audit = supersession_visibility_scan(
            root,
            scope="analysis_corpus",
            evidence_root_id=None,
            authenticated_basis={
                "kind": "whole_window_evaluation_basis_sha256",
                "sha256": "a" * 64,
            },
        )
        self.assertEqual(audit["raw_count"], 2)
        self.assertEqual(audit["validated_count"], 1)
        self.assertEqual(audit["status"], "refused")
        self.assertNotIn("path", audit["authenticated_basis"])

    def test_d093_two_row_scan_persists_as_valid_claim_artifact(self):
        from joulewise.analysis_engine.inputs import supersession_visibility_scan

        root = self._duplicated_root()
        self._manifest(root, "campaign-z-a.json", "session-z-a", "z-bundle")
        self._manifest(root, "campaign-z-b.json", "session-z-b", "z-bundle")

        z_entry = self._install_real_supersession(
            root,
            "z-bundle",
            selected_manifest="campaign-z-b.json",
            superseded_manifests=["campaign-z-a.json"],
        )
        with (root / "campaign_log.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(z_entry, sort_keys=True) + "\n")

        a_entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest="campaign-b.json",
            superseded_manifests=["campaign-a.json"],
        )
        with (root / "campaign_log.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(a_entry, sort_keys=True) + "\n")

        audit = supersession_visibility_scan(
            root,
            scope="analysis_corpus",
            evidence_root_id=None,
            authenticated_basis={
                "kind": "whole_window_evaluation_basis_sha256",
                "sha256": "a" * 64,
            },
        )
        self.assertEqual(audit["raw_count"], 4)
        self.assertEqual(audit["validated_count"], 4)
        self.assertEqual(
            audit["findings"],
            [
                {
                    "reason_code": (
                        REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_MULTIPLE_ROWS
                    ),
                    "bundle_ids": ["dup-bundle", "z-bundle"],
                }
            ],
        )

        artifact = _v3_fixture_artifact(diverged=True)
        artifact["supersession_audit"][0] = audit
        artifact["claim_verdicts_id"] = calculate_claim_verdicts_id(artifact)
        persisted = json.loads(render_claim_verdicts(artifact))
        self.assertEqual(validate_claim_verdicts(persisted), [])

    def test_invalid_json_supersession_reader_input_refuses_join_globally(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence

        root = Path(tempfile.mkdtemp(prefix="gauntlet-sup-json-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(root, "campaign.json", "session", "bundle")
        (root / "campaign_log.jsonl").write_text(
            "{unidentifiable-json\n", encoding="utf-8"
        )

        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_unidentifiable_supersession_record_refuses_join_globally(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import OCCURRENCE_SUPERSESSION_SCHEMA

        root = Path(tempfile.mkdtemp(prefix="gauntlet-sup-unidentifiable-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(root, "campaign.json", "session", "bundle")
        (root / "campaign_log.jsonl").write_text(
            json.dumps(
                {
                    "schema_version": OCCURRENCE_SUPERSESSION_SCHEMA,
                    "record_type": "campaign_occurrence_supersession",
                    "reason": "bundle identity was lost",
                }
            )
            + "\n",
            encoding="utf-8",
        )

        self.assertEqual(_campaign_cooldown_evidence(root, None), {})

    def test_exact_supersession_cannot_license_emission_subset(self):
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import validated_supersession_entries

        root = Path(tempfile.mkdtemp(prefix="d5j-struck-cell-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self._manifest(
            root,
            "selected.json",
            "selected-session",
            "dup-bundle",
            analysis_manifest_id="selected",
        )
        self._manifest(
            root,
            "filtered.json",
            "filtered-session",
            "dup-bundle",
            analysis_manifest_id="selected",
            cooldown="malformed",
        )
        entry = self._install_real_supersession(
            root,
            "dup-bundle",
            selected_manifest="selected.json",
            superseded_manifests=["filtered.json"],
        )

        self.assertEqual(validated_supersession_entries(root), [entry])
        row = _campaign_cooldown_evidence(root, "selected")["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])
        self.assertIsNone(row["manifest"])

    def _assert_7b_corpus_shape_resolves(self) -> None:
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import validated_supersession_entries

        root = Path(tempfile.mkdtemp(prefix="d5j-real-shape-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        bundle_ids = [f"member-{index:02d}" for index in range(57)]
        genuine_indices = (44, 45)
        original_names: dict[str, str] = {}
        for index, bundle_id in enumerate(bundle_ids):
            name = f"campaign-{index:02d}-0-invoked.json"
            original_names[bundle_id] = name
            self._manifest(
                root,
                name,
                f"session-{index:02d}",
                bundle_id,
            )
            aliases = 1 if index < 24 else 2 if index < 44 else 0
            for alias_index in range(aliases):
                alias_name = (
                    f"campaign-{index:02d}-{alias_index + 1}-existing.json"
                )
                self._manifest(
                    root,
                    alias_name,
                    f"existing-{index:02d}-{alias_index}",
                    bundle_id,
                    execution="existing",
                )
                self._install_legacy_existing_binding(root, alias_name)

        duplicate_ids = tuple(bundle_ids[index] for index in genuine_indices)
        for retry_index, (member_index, bundle_id) in enumerate(
            zip(genuine_indices, duplicate_ids, strict=True)
        ):
            retry_name = f"campaign-{member_index:02d}-1-invoked.json"
            self._manifest(
                root,
                retry_name,
                f"retry-session-{retry_index}",
                bundle_id,
            )
            if retry_index == 1:
                alias_name = f"campaign-{member_index:02d}-2-existing.json"
                self._manifest(
                    root,
                    alias_name,
                    "retry-existing-session",
                    bundle_id,
                    execution="existing",
                )
                self._install_legacy_existing_binding(root, alias_name)
            self._install_real_supersession(
                root,
                bundle_id,
                selected_manifest=retry_name,
                superseded_manifests=[original_names[bundle_id]],
            )

        self.assertEqual(len(validated_supersession_entries(root)), 2)
        joined = _campaign_cooldown_evidence(root, None)
        self.assertEqual(len(joined), 57)
        self.assertTrue(all(row["verified"] for row in joined.values()))
        for index, bundle_id in enumerate(duplicate_ids):
            self.assertEqual(
                joined[bundle_id]["session_id"], f"retry-session-{index}"
            )

    def _assert_contrast_corpus_shape_resolves(self) -> None:
        from joulewise.analysis_engine.inputs import _campaign_cooldown_evidence
        from joulewise.whole_window import validated_supersession_entries

        root = Path(tempfile.mkdtemp(prefix="d5j-contrast-shape-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        bundle_ids = [f"member-{index:02d}" for index in range(47)]
        target = bundle_ids[23]
        for index, bundle_id in enumerate(bundle_ids):
            self._manifest(
                root,
                f"campaign-{index:02d}-0-invoked.json",
                f"session-{index:02d}",
                bundle_id,
            )
        retries = []
        for retry_index in (1, 2):
            name = f"campaign-23-{retry_index}-invoked.json"
            retries.append(name)
            self._manifest(
                root,
                name,
                f"retry-session-{retry_index}",
                target,
            )
        self._install_real_supersession(
            root,
            target,
            selected_manifest=retries[-1],
            superseded_manifests=["campaign-23-0-invoked.json", retries[0]],
        )

        self.assertEqual(len(validated_supersession_entries(root)), 1)
        joined = _campaign_cooldown_evidence(root, None)
        self.assertEqual(len(joined), 47)
        self.assertTrue(all(row["verified"] for row in joined.values()))
        self.assertEqual(joined[target]["session_id"], "retry-session-2")

    def test_57_member_fixture_preserves_44_aliases_and_two_supersessions(self):
        self._assert_7b_corpus_shape_resolves()

    def test_47_member_fixture_preserves_one_consumed_supersession(self):
        self._assert_contrast_corpus_shape_resolves()

    def test_supersession_naming_mismatched_occurrences_refuses(self):
        from joulewise.analysis_engine import inputs as inputs_module

        entry = {
            "bundle_id": "dup-bundle",
            "selected_occurrence": {
                "source_manifest": {"path": "campaign_manifests/campaign-b.json"},
                "member_index": 0,
                "bundle_index": 0,
            },
            "superseded_occurrences": [
                {
                    "source_manifest": {
                        "path": "campaign_manifests/campaign-OTHER.json"
                    },
                    "member_index": 3,
                    "bundle_index": 0,
                }
            ],
        }
        with unittest.mock.patch.object(
            inputs_module,
            "supersession_entry_validation_results",
            return_value=([entry], [True]),
        ):
            resolved = inputs_module._campaign_cooldown_evidence(
                self._duplicated_root(), None
            )
        row = resolved["dup-bundle"]
        self.assertEqual(row["result"], "unknown")
        self.assertFalse(row["verified"])

    def test_matcher_partial_extra_and_repeated_identities_refuse(self):
        from joulewise.whole_window import (
            supersession_selected_occurrence_identity as match,
        )

        a = ("campaign_manifests/a.json", 0, 0)
        b = ("campaign_manifests/b.json", 0, 0)
        c = ("campaign_manifests/c.json", 0, 0)
        entry = {
            "bundle_id": "x",
            "selected_occurrence": {
                "source_manifest": {"path": b[0]},
                "member_index": 0,
                "bundle_index": 0,
            },
            "superseded_occurrences": [
                {
                    "source_manifest": {"path": a[0]},
                    "member_index": 0,
                    "bundle_index": 0,
                }
            ],
        }
        self.assertEqual(match([entry], "x", [a, b]), b)
        self.assertIsNone(match([entry], "x", [a, b, c]))
        self.assertIsNone(match([entry], "x", [a]))
        self.assertIsNone(match([entry], "x", [a, a]))
        self.assertIsNone(match([entry], "wrong-id", [a, b]))
        self.assertIsNone(match([entry, dict(entry)], "x", [a, b]))

class CooldownResultKeysetUnitTests(unittest.TestCase):
    """Direct structural lock for the C1 keyset union (audit finding F1).

    The public join cannot currently produce an emission-only id (emissions
    are sourced from declared invoked positions), so this exercises the
    helper directly: the defensive leg must surface an undeclared emission
    id rather than dropping it.
    """

    def test_emission_only_id_is_included_after_declared_ids(self):
        from joulewise.analysis_engine.inputs import _cooldown_result_bundle_ids

        declared = {"decl-a": [("m", 0, 0)], "decl-b": [("m", 1, 0)]}
        emissions = {"decl-b": [(("m", 1, 0), {})], "emit-only": [(("m", 2, 0), {})]}
        self.assertEqual(
            _cooldown_result_bundle_ids(declared, emissions),
            ["decl-a", "decl-b", "emit-only"],
        )

    def test_no_emission_only_ids_yields_declared_order(self):
        from joulewise.analysis_engine.inputs import _cooldown_result_bundle_ids

        declared = {"decl-a": [("m", 0, 0)]}
        self.assertEqual(
            _cooldown_result_bundle_ids(declared, {"decl-a": [(("m", 0, 0), {})]}),
            ["decl-a"],
        )


class MintLaunchLineageAuthenticationTests(unittest.TestCase):
    @staticmethod
    def _lineage(*, plan_id: str = "plan-1") -> dict:
        return {
            "schema_version": "joulewise.launch_lineage.v1",
            "collection_boot_session_id": (
                "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
            ),
            "pack_id": "pack-1",
            "plan_id": plan_id,
            "window_id": "window-1",
            "bracket_session_id": "bracket-1",
            "consumption": {"path": "/consume.json", "sha256": "a" * 64},
            "start": {"path": "/start.json", "sha256": "b" * 64},
            "settle": {"path": "/settle.json", "sha256": "c" * 64},
            "completion": None,
        }

    @staticmethod
    def _component(report: dict) -> SimpleNamespace:
        return SimpleNamespace(
            spec={
                "cells": [
                    {
                        "cell_id": "absolute",
                        "members": [{"bundle_id": "member"}],
                    }
                ]
            },
            members=(SimpleNamespace(bundle_id="member"),),
            report=report,
            whole_window_evaluation_basis_sha256="d" * 64,
        )

    @staticmethod
    def _write_bundle(root: Path, *, marker: bool) -> None:
        bundle = root / "member"
        bundle.mkdir()
        (bundle / "config.json").write_text(
            json.dumps(
                {
                    "run_metadata": {
                        "tags": (
                            ["launch_lineage_required"] if marker else []
                        )
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (bundle / "metadata.json").write_text("{}\n", encoding="utf-8")

    def test_copied_lineage_without_source_receipts_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_bundle(root, marker=True)
            component = self._component({"launch_lineage": self._lineage()})

            with self.assertRaisesRegex(
                ValueError,
                "launch_consumption_missing",
            ):
                floor_mint_estimator._authenticate_mint_launch_lineage(
                    component,
                    runs_root=root,
                )

    def test_legacy_sources_are_dormant_but_cannot_claim_copied_lineage(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_bundle(root, marker=False)
            self.assertIsNone(
                floor_mint_estimator._authenticate_mint_launch_lineage(
                    self._component({}),
                    runs_root=root,
                )
            )
            with self.assertRaisesRegex(
                ValueError,
                "launch_consumption_missing",
            ):
                floor_mint_estimator._authenticate_mint_launch_lineage(
                    self._component({"launch_lineage": self._lineage()}),
                    runs_root=root,
                )

    def test_mint_compares_full_copied_lineage_after_direct_authentication(
        self,
    ) -> None:
        authenticated = self._lineage()
        copied = self._lineage(plan_id="plan-2")
        component = self._component({"launch_lineage": copied})
        with mock.patch.object(
            floor_mint_estimator,
            "authenticate_window_launch_lineage",
            return_value=authenticated,
        ) as reopened:
            with self.assertRaisesRegex(
                ValueError,
                "launch_lineage_conflict",
            ):
                floor_mint_estimator._authenticate_mint_launch_lineage(
                    component,
                    runs_root=Path("/authenticated-root"),
                )

        reopened.assert_called_once_with(
            Path("/authenticated-root"),
            {"member"},
            evaluation_basis_sha256="d" * 64,
        )

    def test_mint_completion_absence_keeps_registered_refusal(self) -> None:
        component = self._component({"launch_lineage": self._lineage()})
        with mock.patch.object(
            floor_mint_estimator,
            "authenticate_window_launch_lineage",
            side_effect=LaunchLineageError(
                "launch_lifecycle_incomplete",
                "completion absent",
            ),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "launch_lifecycle_incomplete",
            ):
                floor_mint_estimator._authenticate_mint_launch_lineage(
                    component,
                    runs_root=Path("/authenticated-root"),
                )
