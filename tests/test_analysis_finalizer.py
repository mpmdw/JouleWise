from __future__ import annotations

import copy
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from joulewise.analysis_manifest_v3 import (
    AnalysisManifestFinalizationError,
    FINALIZED_BASENAME_SUFFIX,
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
    finalize_bracket_session_slot,
    load_calibration_ledger_snapshot,
    terminal_head_pin_for_session,
)
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from joulewise.schemas import BenchmarkConfig
from tests.test_analysis_manifest_v3 import install_synthetic_prospective_fixture
from joulewise.detection_floor import (
    build_floor_artifact,
    build_transport_group,
    validate_floor_artifact,
)
from tests.test_detection_floor import condition_family, make_artifact, make_cell
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
        },
        "adapters": {
            "runtime": {
                "name": "mlx",
                "prepare_metadata": {
                    "adapter": "mlx_runtime",
                    "version": None,
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
    _write_json(binding_path, binding)
    return ledger, binding_path


def install_synthetic_finalization_fixture(
    root: Path, *, shared_family: bool = False
) -> dict:
    root = Path(root)
    prospective_path, plan_tree_path, prospective = (
        install_synthetic_prospective_fixture(
            root, shared_family=shared_family
        )
    )
    runs_root = root / "runs"
    runs_root.mkdir()
    occurrences = []
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
                "a" if member["arm"] == "A" else "b"
            )
            metadata_raw = (
                json.dumps(
                    _metadata_for_config(config, model_token),
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
                    },
                    sort_keys=True,
                )
                + "\n"
            ).encode()
            (bundle / "summary_metrics.json").write_bytes(summary_raw)
            occurrences.append(
                {
                    "bundle_id": member["run_id"],
                    "bundle_path": member["run_id"],
                    "config_sha256": hashlib.sha256(config_raw).hexdigest(),
                    "metadata_sha256": hashlib.sha256(metadata_raw).hexdigest(),
                    "summary_sha256": hashlib.sha256(summary_raw).hexdigest(),
                }
            )
    occurrences.sort(key=lambda row: row["bundle_id"])
    basis_body = {
        "schema_version": "joulewise.idle_admission_evaluation_basis.v1",
        "policy_sha256": "c" * 64,
        "member_occurrences": occurrences,
        "calibration_bracket_set": [],
        "consumption_semantics_id": "d078_minted_envelopes_v1",
    }
    basis = {
        **basis_body,
        "sha256": hashlib.sha256(
            json.dumps(
                basis_body,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
    }
    verdict = {
        "schema_version": "joulewise.idle_admission_whole_window_verdict.v1",
        "record_type": "idle_admission_whole_window_verdict",
        "status": "passed",
        "claim_licensing": True,
        "bundle_ids": sorted(row["bundle_id"] for row in occurrences),
        "evaluation_basis": basis,
        "decision_envelope_outcomes": {
            "decode": "supported",
            "prefill_p256": "refused_below_floor",
        },
    }
    verdict_path = root / "whole_window_verdict.json"
    _write_json(verdict_path, verdict)
    ledger_path, bracket_path = _install_calibration_session(
        root, prospective=prospective, runs_root=runs_root
    )
    cells = []
    groups = []
    for contrast_index, contrast in enumerate(prospective["contrasts"]):
        group_id = f"synthetic-exact-group-{contrast_index}"
        group_cells = []
        condition_ids = [
            contrast["condition_a_id"],
            contrast["condition_b_id"],
        ]
        for condition_index, condition_id in enumerate(condition_ids):
            cell = make_cell(
                cell_id=f"synthetic-floor-{contrast_index}-{condition_index}",
                condition=condition_id,
                metric=contrast["metric"],
            )
            cell["key"]["window_class"] = "phase"
            cell["transport_group_id"] = group_id
            cells.append(cell)
            group_cells.append(cell)
        groups.append(
            build_transport_group(
                transport_group_id=group_id,
                backend="powermetrics",
                metric=contrast["metric"],
                window_class="phase",
                stack_identity=group_cells[0]["source_regime"]["stack_identity"],
                source_cells=group_cells,
                allowed_consumer_condition_families=[
                    condition_family(condition_id)
                    for condition_id in condition_ids
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
            second = finalize_prospective_analysis_manifest_v3(
                fixture["prospective_path"], **kwargs
            )
            self.assertEqual(first, second)
            self.assertEqual(
                [row["measurement_arm"] for row in first["contrasts"]],
                ["decode", "prefill_p256"],
            )
            self.assertEqual(
                first["lineage"]["prospective_semantics_sha256"],
                first["lineage"]["finalized_semantics_sha256"],
            )
            path = (
                fixture["root"]
                / f"{fixture['prospective']['manifest_id']}{FINALIZED_BASENAME_SUFFIX}"
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


if __name__ == "__main__":
    unittest.main()
