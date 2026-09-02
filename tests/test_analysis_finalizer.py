from __future__ import annotations

import copy
import hashlib
import io
import json
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from joulewise.analysis_manifest_v3 import (
    AnalysisManifestFinalizationError,
    FINALIZED_BASENAME_SUFFIX,
    analysis_semantics_sha256_v1,
    calculate_manifest_id,
    finalize_prospective_analysis_manifest_v3,
    frozen_family_block_strata,
    validate_finalized_analysis_manifest_v3,
)
from joulewise.calibration_bracketing import build_calibration_bracket_binding
from joulewise.calibration_ledger import (
    GENESIS_DIGEST,
    IDENTITY_EPOCH_FIELDS,
    LEDGER_SCHEMA,
    artifact_hashes,
    append_bracket_session_receipt,
    canonical_json_bytes,
    finalize_bracket_session_slot,
    load_calibration_ledger_snapshot,
    terminal_head_pin_for_session,
)
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from joulewise.schemas import BenchmarkConfig
from joulewise.identity_pins import build_stack_identity
from tests.test_analysis_manifest_v3 import install_synthetic_prospective_fixture
from joulewise.detection_floor import (
    build_floor_artifact,
    build_transport_group,
    validate_floor_artifact,
)
from joulewise.idle_admission import ADAPTER_CONTINUITY_SCHEMA
from joulewise.whole_window import build_neg8_drift_bound_artifact, canonical_sha256
from tests.test_detection_floor import make_artifact, make_cell, make_regime
from tests.test_run_campaign import read_all_jsonl, run_campaign_module
from scripts.finalize_analysis_manifest import main as finalize_main


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _metadata_for_config(config: dict, model_token: str) -> dict:
    return {
        "workload_provenance": {
            "model": {
                "artifact_identity": {
                    "status": "ok",
                    "kind": "file_set",
                    "algorithm": "sha256",
                    "folded_sha256": model_token * 64,
                }
            },
            "tokenizer": {
                "backend": "mlx",
                "identifier": config["model"]["source"],
                "revision": config["model"]["revision"],
                "class": "TokenizerWrapper",
                "vocab_size": 151643,
            },
            "sampler": {
                "api": "mlx.sample",
                "kind": "deterministic_greedy",
                "pinned": True,
            },
            "output_policy": {
                "name": "fixed_token_count",
                "requested_tokens": config["workload_profile"]["output_tokens"],
                "stop_condition": "requested_tokens",
            },
        },
        "adapters": {
            "runtime": {
                "name": "mlx",
                "prepare_metadata": {
                    "adapter": "mlx_runtime",
                    "version": "synthetic-mlx-1",
                    "kernel_library": "synthetic-kernel-1",
                    "batching_concurrency_policy": "single-request sequential",
                },
            },
            "telemetry": {"name": "powermetrics"},
        },
        "device": {
            "device": "macbook_m3_max",
            "telemetry": "powermetrics",
            "rail_manifest": ["cpu_power", "gpu_power", "ane_power"],
            "boundary": "Apple SoC CPU + GPU + ANE package power",
        },
        "machine": "synthetic-mac",
        "platform": {"build_version": "25F84"},
        "environment": {
            "build_version": "25F84",
            "power_source": "AC Power",
            "power": {
                "adapter_watts": 100.0,
                "adapter_description": "Synthetic 100W Adapter",
            },
        },
        "instrument_calibration": {"artifact_sha256": "9" * 64},
        "model": config["model"],
        "quantization": config["quantization"],
    }


def _install_calibration_session(
    root: Path, *, prospective: dict, runs_root: Path
) -> tuple[Path, Path]:
    ledger = root / "calibration_ledger.jsonl"
    head_pin = root / "calibration_ledger_head.json"
    _write_json(
        head_pin,
        {
            "sequence": 0,
            "head_digest": GENESIS_DIGEST,
            "ledger_schema": LEDGER_SCHEMA,
        },
    )
    epoch = {
        field: value
        for field, value in zip(
            IDENTITY_EPOCH_FIELDS,
            ("25F84", "Mac15,9", "ac_high_power", 100, "estimator-v1", "pulse-v3"),
            strict=True,
        )
    }
    t1 = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
    t1.update(epoch)
    slots = {}
    for slot in ("pre", "post"):
        custody = runs_root / "instrument_validation" / f"synthetic-session-{slot}"
        (custody / "raw").mkdir(parents=True)
        (custody / "raw" / "powermetrics.plist").write_bytes(
            f"raw-{slot}".encode()
        )
        (custody / "events.jsonl").write_text('{"timestamp_s":99.0}\n')
        _write_json(custody / "instrument_evidence.json", {"slot": slot})
        _write_json(custody / "manifest.json", {"slot": slot})
        slots[slot] = {
            "attempt_id": f"synthetic-session-{slot}",
            "custody_locator": str(custody),
            "identity_epoch": epoch,
            "t1_bindings": t1,
        }
    append_bracket_session_receipt(
        ledger,
        session_id="synthetic-session",
        window_id="synthetic-window",
        plan_id=prospective["plan"]["plan_id"],
        plan_sha256=prospective["plan"]["sha256"],
        evidence_root_id=prospective["evidence_root_id"],
        runs_root=runs_root,
        slots=slots,
        head_pin_path=head_pin,
        require_committed_pin=False,
    )
    for slot in ("pre", "post"):
        custody = Path(slots[slot]["custody_locator"])
        finalize_bracket_session_slot(
            ledger,
            session_id="synthetic-session",
            slot=slot,
            disposition="valid",
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=epoch,
            t1_bindings=t1,
            capture_wall_time_s="99.0" if slot == "pre" else "111.0",
            exact_bound_lexeme_s="0.025",
        )
    terminal = terminal_head_pin_for_session(
        ledger, session_id="synthetic-session"
    )
    _write_json(head_pin, terminal)
    snapshot = load_calibration_ledger_snapshot(
        ledger,
        head_pin,
        require_committed_pin=False,
        verify_custody=False,
    )
    binding = build_calibration_bracket_binding(
        snapshot,
        session_id="synthetic-session",
        window_id="synthetic-window",
        plan_id=prospective["plan"]["plan_id"],
        plan_sha256=prospective["plan"]["sha256"],
        evidence_root_id=prospective["evidence_root_id"],
        runs_root=runs_root,
    )
    binding_path = root / "bracket_binding.json"
    binding_path.write_bytes(canonical_json_bytes(binding) + b"\n")
    return ledger, binding_path


def install_synthetic_finalization_fixture(
    root: Path,
    *,
    shared_family: bool = False,
    transport_mode: str = "exact_stack_only",
    runtime_backend: str = "mlx",
    telemetry_backend: str = "powermetrics",
    shared_governed_stack: bool = False,
    floor_cells_by_slot: dict[tuple[str, str], dict] | None = None,
    dominance_criterion: dict | None = None,
) -> dict:
    root = Path(root)
    prospective_path, plan_tree_path, prospective = (
        install_synthetic_prospective_fixture(
            root,
            shared_family=shared_family,
            transport_mode=transport_mode,
            runtime_backend=runtime_backend,
            telemetry_backend=telemetry_backend,
            floor_cells_by_slot=floor_cells_by_slot,
            dominance_criterion=dominance_criterion,
        )
    )
    runs_root = root / "runs"
    runs_root.mkdir()
    bundle_paths: dict[str, Path] = {}
    for contrast in prospective["contrasts"]:
        for member in contrast["members"]:
            bundle = runs_root / member["run_id"]
            bundle.mkdir()
            source_config = prospective_path.parent / member["config"]
            config = json.loads(source_config.read_bytes())
            config_raw = (
                json.dumps(
                    BenchmarkConfig.from_mapping(config).to_dict(),
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            ).encode()
            config = json.loads(config_raw)
            (bundle / "config.json").write_bytes(config_raw)
            model_token = (
                "c"
                if shared_governed_stack
                else "a" if member["arm"] == "A" else "b"
            )
            metadata = _metadata_for_config(config, model_token)
            if shared_governed_stack:
                metadata["workload_provenance"]["tokenizer"].update(
                    {
                        "identifier": "synthetic-shared-tokenizer",
                        "revision": "shared",
                    }
                )
                metadata["workload_provenance"]["output_policy"][
                    "requested_tokens"
                ] = 512
            if runtime_backend != "mlx" or telemetry_backend != "powermetrics":
                metadata["adapters"]["runtime"]["name"] = runtime_backend
                metadata["adapters"]["telemetry"]["name"] = telemetry_backend
                metadata["device"]["telemetry"] = telemetry_backend
                metadata["device"]["rail_manifest"] = [telemetry_backend]
                metadata["connection"] = {
                    "transport": config["hardware_target"]["transport"]
                }
            metadata["config_sha256"] = hashlib.sha256(config_raw).hexdigest()
            metadata_raw = (
                json.dumps(
                    metadata,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            ).encode()
            (bundle / "metadata.json").write_bytes(metadata_raw)
            summary_raw = (
                json.dumps(
                    {
                        "status": "succeeded",
                        "synthetic_effect_value_j": (
                            -1000.0 if contrast["measurement_arm"] == "prefill_p256" else 1000.0
                        ),
                        "measurement_quality": {
                            "telemetry_source": telemetry_backend,
                        },
                    },
                    sort_keys=True,
                )
                + "\n"
            ).encode()
            (bundle / "summary_metrics.json").write_bytes(summary_raw)
            bundle_paths[member["run_id"]] = bundle

    bundle_ids = sorted(bundle_paths)
    reference_ids = (bundle_ids[0], bundle_ids[-1])
    for bundle_id, gross, idle in (
        (reference_ids[0], 8.0, 7.0),
        (reference_ids[1], 8.001, 7.001),
    ):
        summary_path = bundle_paths[bundle_id] / "summary_metrics.json"
        summary = json.loads(summary_path.read_text())
        summary.update(
            gross_energy_j=gross,
            idle_subtracted_energy_j=idle,
            energy_anchor_shift_envelopes={
                "/gross_energy_j": {
                    "point_j": gross,
                    "lower_j": gross - 0.001,
                    "upper_j": gross + 0.001,
                }
            },
        )
        _write_json(summary_path, summary)

    policy_path = (
        Path(__file__).resolve().parents[1]
        / "configs"
        / "campaign_policies"
        / "quiet_mac_p2_production.json"
    )
    policy_sha = hashlib.sha256(policy_path.read_bytes()).hexdigest()
    campaign_manifest = {
        "schema_version": "joulewise.campaign_provenance.v1",
        "analysis_manifest_id": prospective["manifest_id"],
        "campaign_policy": {"sha256": policy_sha},
        "members": [
            {
                "config": f"{bundle_id}.json",
                "run_id": bundle_id,
                "execution": "invoked",
                "bundle_ids": [bundle_id],
                "role": (
                    run_campaign_module.NEG8_REFERENCE_ROLE
                    if bundle_id in reference_ids
                    else None
                ),
                "sentinel_position": (
                    "start"
                    if bundle_id == reference_ids[0]
                    else "end"
                    if bundle_id == reference_ids[1]
                    else None
                ),
                "scientific_config_sha256": "8" * 64,
                "canonical_neg8_workload": bundle_id in reference_ids,
            }
            for bundle_id in bundle_ids
        ],
    }
    _write_json(
        runs_root / "campaign_manifests" / "synthetic.json",
        campaign_manifest,
    )
    freshness = {
        "os_build": "25F84",
        "power_supply_identity_sha256": canonical_sha256(
            {
                "power_source": "AC Power",
                "adapter_watts": 100.0,
                "adapter_description": "Synthetic 100W Adapter",
            }
        ),
        "calibration_identity_sha256": "9" * 64,
    }
    drift = build_neg8_drift_bound_artifact(
        corpus_id="synthetic-neg8-reference-corpus",
        condition_id="synthetic-neg8",
        manifest_sha256="7" * 64,
        scientific_config_sha256="8" * 64,
        members=[
            {
                "bundle_id": f"synthetic-neg8-reference-{index}",
                "point_gross_j": 8.0 + index / 1000.0,
                "point_idle_subtracted_j": 7.0 + index / 1000.0,
                "bundle_evidence_sha256": f"{index:x}" * 64,
            }
            for index in range(1, 11)
        ],
        derivation_timestamp_s=time.time(),
        freshness_bindings=freshness,
    )
    drift_path = root / "neg8_drift_bound.json"
    _write_json(drift_path, drift)
    writer_args = run_campaign_module.parse_args(
        [
            "--whole-window-verdict",
            "--runs-dir",
            str(runs_root),
            "--campaign-policy",
            str(policy_path),
            "--neg8-drift-bound",
            str(drift_path),
        ]
    )
    writer_stdout = io.StringIO()
    with (
        mock.patch.object(run_campaign_module, "validate_bundle", return_value=[]),
        mock.patch.object(
            run_campaign_module, "_final_idle_admission_attempt", return_value=1
        ),
        mock.patch.object(
            run_campaign_module, "_load_idle_rich_telemetry", return_value=[]
        ),
        mock.patch.object(
            run_campaign_module, "post_run_environment_refusals", return_value=()
        ),
        mock.patch.object(
            run_campaign_module,
            "evaluate_cpu_idle_admission",
            return_value={"decision": "admitted", "conditions": []},
        ),
        mock.patch.object(
            run_campaign_module, "_adapter_observations_for", return_value=[]
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
                    "schema_version": "joulewise.instrument_calibration_bracket.v1",
                    "status": "passed",
                    "b_fiducial_s": 0.025,
                },
                (),
            ),
        ),
        redirect_stdout(writer_stdout),
    ):
        if run_campaign_module.run_whole_window_verdict(writer_args) != 0:
            rows = read_all_jsonl(runs_root / "campaign_log.jsonl")
            raise AssertionError(
                "production whole-window writer refused fixture: "
                f"{writer_stdout.getvalue()} {rows[-1] if rows else None}"
            )
    verdict = read_all_jsonl(runs_root / "campaign_log.jsonl")[-1]
    verdict_path = root / "whole_window_verdict.json"
    _write_json(verdict_path, verdict)
    ledger_path, bracket_path = _install_calibration_session(
        root, prospective=prospective, runs_root=runs_root
    )
    cells = []
    groups = []
    for contrast_index, contrast in enumerate(prospective["contrasts"]):
        condition_ids = [
            contrast["condition_a_id"],
            contrast["condition_b_id"],
        ]
        for condition_index, condition_id in enumerate(condition_ids):
            arm = "A" if condition_index == 0 else "B"
            representative = next(
                member
                for member in contrast["members"]
                if member["arm"] == arm
            )
            bundle = bundle_paths[representative["run_id"]]
            stack = build_stack_identity(
                json.loads((bundle / "config.json").read_text()),
                json.loads((bundle / "metadata.json").read_text()),
            )
            if stack is None:
                raise AssertionError("synthetic fixture lacks a stack identity")
            condition_row = next(
                row
                for row in prospective["condition_families"]
                if row["condition_family_id"] == condition_id
            )
            condition_definition = json.loads(
                (prospective_path.parent / condition_row["path"]).read_text()
            )
            group_id = (
                f"synthetic-floor-group-{contrast['measurement_arm']}-{arm.lower()}"
            )
            cell = make_cell(
                cell_id=f"synthetic-floor-{contrast_index}-{condition_index}",
                condition=condition_id,
                metric=contrast["metric"],
                regime=make_regime(stack_identity=stack),
            )
            cell["key"]["backend"] = telemetry_backend
            cell["key"]["window_class"] = "phase"
            cell["key"]["condition_family_definition"] = condition_definition
            cell["key"]["condition_family_sha256"] = condition_row[
                "canonical_domain_sha256"
            ]
            cell["transport_group_id"] = group_id
            cells.append(cell)
            groups.append(
                build_transport_group(
                    transport_group_id=group_id,
                    backend=telemetry_backend,
                    metric=contrast["metric"],
                    window_class="phase",
                    stack_identity=stack,
                    source_cells=[cell],
                    allowed_consumer_condition_families=[
                        {
                            "condition_family_id": condition_id,
                            "condition_family_definition": condition_definition,
                            "condition_family_sha256": condition_row[
                                "canonical_domain_sha256"
                            ],
                        }
                    ],
                )
            )
    base_floor = make_artifact()
    floor = build_floor_artifact(
        artifact_id="synthetic-exact-aggregate-floor",
        calibration_scope="smoke",
        source_class="synthetic",
        provenance=base_floor["provenance"],
        cells=cells,
        transport_groups=groups,
    )
    floor_errors = validate_floor_artifact(floor)
    if floor_errors:
        raise AssertionError(floor_errors)
    floor_path = root / "aggregate_floor.json"
    _write_json(floor_path, floor)
    return {
        "root": root,
        "prospective_path": prospective_path,
        "plan_tree_path": plan_tree_path,
        "prospective": prospective,
        "runs_root": runs_root,
        "verdict_path": verdict_path,
        "ledger_path": ledger_path,
        "bracket_path": bracket_path,
        "floor_path": floor_path,
    }


class AnalysisFinalizerTests(unittest.TestCase):
    def test_legacy_finalization_is_byte_unchanged_without_floor_identity_fields(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            manifest = finalize_prospective_analysis_manifest_v3(
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
        legacy_projection = copy.deepcopy(manifest)
        for arm in legacy_projection["arms"]:
            arm.pop("floor_cell_id", None)
            arm.pop("floor_stack_identity", None)
        self.assertEqual(
            manifest["manifest_id"], calculate_manifest_id(legacy_projection)
        )
        for arm in manifest["arms"]:
            self.assertNotIn("floor_cell_id", arm)
            self.assertNotIn("floor_stack_identity", arm)

    def test_cli_maps_fuzz_shaped_prospective_value_to_closed_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prospective_path, plan_tree_path, prospective = (
                install_synthetic_prospective_fixture(root)
            )
            prospective["families"][0]["contrast_ids"] = [{}]
            _write_json(prospective_path, prospective)
            runs = root / "runs"
            runs.mkdir()
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = finalize_main(
                    [
                        "--prospective-manifest",
                        str(prospective_path),
                        "--plan-tree",
                        str(plan_tree_path),
                        "--custody-root",
                        str(root),
                        "--runs-root",
                        str(runs),
                        "--whole-window-verdict",
                        str(prospective_path),
                        "--bracket-binding",
                        str(prospective_path),
                        "--calibration-ledger",
                        str(prospective_path),
                        "--aggregate-floor-artifact",
                        str(prospective_path),
                        "--output-dir",
                        str(root),
                    ]
                )
            self.assertEqual(code, 2)
            refusal = json.loads(stdout.getvalue())
            self.assertEqual(refusal["status"], "REFUSE")
            self.assertEqual(
                refusal["reason"],
                "analysis_finalization_prospective_invalid",
            )

    def test_cli_emits_machine_readable_finalized_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = finalize_main(
                    [
                        "--prospective-manifest",
                        str(fixture["prospective_path"]),
                        "--plan-tree",
                        str(fixture["plan_tree_path"]),
                        "--custody-root",
                        str(fixture["root"]),
                        "--runs-root",
                        str(fixture["runs_root"]),
                        "--whole-window-verdict",
                        str(fixture["verdict_path"]),
                        "--bracket-binding",
                        str(fixture["bracket_path"]),
                        "--calibration-ledger",
                        str(fixture["ledger_path"]),
                        "--aggregate-floor-artifact",
                        str(fixture["floor_path"]),
                        "--output-dir",
                        str(fixture["root"]),
                    ]
                )
            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["status"], "FINALIZED")
            self.assertTrue(Path(result["output"]).is_file())

    def test_finalizes_both_contrasts_idempotently_without_outcome_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            kwargs = {
                "plan_tree_path": fixture["plan_tree_path"],
                "custody_root": fixture["root"],
                "runs_root": fixture["runs_root"],
                "whole_window_verdict_path": fixture["verdict_path"],
                "bracket_binding_path": fixture["bracket_path"],
                "calibration_ledger_path": fixture["ledger_path"],
                "aggregate_floor_artifact_path": fixture["floor_path"],
                "output_dir": fixture["root"],
            }
            first = finalize_prospective_analysis_manifest_v3(
                fixture["prospective_path"], **kwargs
            )
            path = (
                fixture["root"]
                / f"{fixture['prospective']['manifest_id']}{FINALIZED_BASENAME_SUFFIX}"
            )
            first_bytes = path.read_bytes()
            second = finalize_prospective_analysis_manifest_v3(
                fixture["prospective_path"], **kwargs
            )
            self.assertEqual(first, second)
            self.assertEqual(path.read_bytes(), first_bytes)
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                hashlib.sha256(first_bytes).hexdigest(),
            )
            self.assertEqual(
                [row["measurement_arm"] for row in first["contrasts"]],
                ["decode", "prefill_p256"],
            )
            self.assertEqual(
                first["lineage"]["prospective_semantics_sha256"],
                first["lineage"]["finalized_semantics_sha256"],
            )
            self.assertEqual(
                validate_finalized_analysis_manifest_v3(
                    first, manifest_path=path, custody_root=fixture["root"]
                ),
                (),
            )

    def test_shared_family_freezes_cross_arm_strata_and_missing_stratum_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(
                Path(tmp), shared_family=True
            )
            manifest = finalize_prospective_analysis_manifest_v3(
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
            family_id = manifest["families"][0]["family_instance_id"]
            strata = frozen_family_block_strata(manifest, family_id)
            self.assertEqual([number for number, _ in strata], list(range(1, 11)))
            self.assertTrue(
                all(
                    len(set(block_ids.values())) == 2
                    for _, block_ids in strata
                )
            )

            attacked = copy.deepcopy(manifest)
            attacked["blocks"] = attacked["blocks"][:-1]
            attacked["manifest_id"] = calculate_manifest_id(attacked)
            path = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            reason_codes = {
                item.reason_code
                for item in validate_finalized_analysis_manifest_v3(
                    attacked,
                    manifest_path=path,
                    custody_root=fixture["root"],
                )
            }
            self.assertIn(
                "analysis_manifest_family_semantics_mismatch", reason_codes
            )

    def test_failed_whole_window_verdict_refuses_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            verdict = json.loads(fixture["verdict_path"].read_text())
            verdict["status"] = "failed"
            _write_json(fixture["verdict_path"], verdict)
            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_verdict_not_passed",
            ):
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
            output = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            self.assertFalse(output.exists())

    def test_reformatted_bracket_binding_bytes_refuse_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            bracket = json.loads(fixture["bracket_path"].read_bytes())
            fixture["bracket_path"].write_bytes(
                (json.dumps(bracket, indent=2, sort_keys=True) + "\n").encode(
                    "utf-8"
                )
            )

            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_bracket_binding_mismatch",
            ) as raised:
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
            self.assertEqual(
                raised.exception.reason_code,
                "analysis_finalization_bracket_binding_mismatch",
            )
            self.assertIn("bracket binding bytes", raised.exception.detail)
            output = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            self.assertFalse(output.exists())

    def test_missing_attachment_and_conflicting_namespace_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            fixture["floor_path"].unlink()
            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_attachment_missing",
            ):
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

        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            output_path = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            output_path.write_text("occupied\n")
            occupied_bytes = output_path.read_bytes()
            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_output_conflict",
            ):
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
            self.assertEqual(output_path.read_bytes(), occupied_bytes)

    def test_finalized_semantic_mutation_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            manifest = finalize_prospective_analysis_manifest_v3(
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
            attacked = copy.deepcopy(manifest)
            attacked["contrasts"][0]["sidedness"] = "greater"
            attacked["lineage"]["finalized_semantics_sha256"] = (
                analysis_semantics_sha256_v1(attacked)
            )
            attacked["manifest_id"] = calculate_manifest_id(attacked)
            path = fixture["root"] / (
                fixture["prospective"]["manifest_id"]
                + FINALIZED_BASENAME_SUFFIX
            )
            reason_codes = {
                item.reason_code
                for item in validate_finalized_analysis_manifest_v3(
                    attacked,
                    manifest_path=path,
                    custody_root=fixture["root"],
                )
            }
            self.assertIn("analysis_manifest_family_semantics_mismatch", reason_codes)

    def test_self_authored_verdict_and_stripped_bracket_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            production = json.loads(fixture["verdict_path"].read_text())
            forged = {
                "schema_version": production["schema_version"],
                "record_type": production["record_type"],
                "status": "passed",
                "claim_licensing": True,
                "bundle_ids": production["bundle_ids"],
                "evaluation_basis": production["evaluation_basis"],
            }
            _write_json(fixture["verdict_path"], forged)
            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_attachment_invalid",
            ):
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

        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            bracket = json.loads(fixture["bracket_path"].read_text())
            bracket["endpoints"]["pre"]["receipt_digest"] = "0" * 64
            bracket["binding_digest"] = hashlib.sha256(
                json.dumps(
                    {
                        key: value
                        for key, value in bracket.items()
                        if key != "binding_digest"
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()
            _write_json(fixture["bracket_path"], bracket)
            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_bracket_binding_mismatch",
            ):
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

    def test_attachment_symlinks_and_nonregular_paths_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            alias = fixture["root"] / "verdict-alias.json"
            alias.symlink_to(fixture["verdict_path"].name)
            common = {
                "plan_tree_path": fixture["plan_tree_path"],
                "custody_root": fixture["root"],
                "runs_root": fixture["runs_root"],
                "bracket_binding_path": fixture["bracket_path"],
                "calibration_ledger_path": fixture["ledger_path"],
                "aggregate_floor_artifact_path": fixture["floor_path"],
                "output_dir": fixture["root"],
            }
            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_attachment_invalid",
            ):
                finalize_prospective_analysis_manifest_v3(
                    fixture["prospective_path"],
                    whole_window_verdict_path=alias,
                    **common,
                )
            directory = fixture["root"] / "not-a-file"
            directory.mkdir()
            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_attachment_invalid",
            ):
                finalize_prospective_analysis_manifest_v3(
                    fixture["prospective_path"],
                    whole_window_verdict_path=directory,
                    **common,
                )

            runs_alias = fixture["root"] / "runs-alias"
            runs_alias.symlink_to(
                fixture["runs_root"].relative_to(fixture["root"]),
                target_is_directory=True,
            )
            bracket = json.loads(fixture["bracket_path"].read_text())
            bracket["runs_root"] = str(runs_alias)
            bracket["binding_digest"] = hashlib.sha256(
                json.dumps(
                    {
                        key: value
                        for key, value in bracket.items()
                        if key != "binding_digest"
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()
            _write_json(fixture["bracket_path"], bracket)
            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_bracket_binding_mismatch",
            ):
                finalize_prospective_analysis_manifest_v3(
                    fixture["prospective_path"],
                    whole_window_verdict_path=fixture["verdict_path"],
                    **common,
                )

    def test_realized_floor_selector_mismatch_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(Path(tmp))
            floor = json.loads(fixture["floor_path"].read_text())
            for cell in floor["cells"]:
                cell["key"]["backend"] = "mock"
            for group in floor["transport_groups"]:
                group["backend"] = "mock"
            self.assertEqual(validate_floor_artifact(floor), [])
            _write_json(fixture["floor_path"], floor)
            with self.assertRaisesRegex(
                AnalysisManifestFinalizationError,
                "analysis_finalization_floor_dependency_unsatisfied",
            ):
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


if __name__ == "__main__":
    unittest.main()
