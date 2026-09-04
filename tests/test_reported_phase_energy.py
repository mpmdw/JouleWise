"""Table-driven R1 acceptance for the D-123 reported-energy supplier."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise import reported_phase_energy as core


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests/fixtures/reported_phase_energy"
BLUEPRINT = FIXTURE_ROOT / "two_pack_source.json"
FLOOR_COPY = FIXTURE_ROOT / "preexisting_floor_output.json"
PREEXISTING_FLOOR = (
    ROOT / "tests/fixtures/results_prose_render/synthetic_alpha_floor.json"
)
PRODUCTION_EXTRACTION_REPORT = (
    ROOT / "tests/fixtures/d117_postcollection_trust/extraction_report.json"
)
REGISTRY = ROOT / "docs/paper/results-fill-registry.md"
BUILDER = ROOT / "scripts/build_reported_phase_energy.py"


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _wrap(path: str, document: dict) -> dict:
    return {
        "path": path,
        "file_sha256": core.canonical_json_sha256(document),
        "document": document,
    }


def _reseal_wrapper(source: dict, key: str) -> None:
    source[key]["file_sha256"] = core.canonical_json_sha256(
        source[key]["document"]
    )


def _reseal_source(source: dict) -> None:
    source["source_id"] = ""
    source["source_id"] = "rpes-" + core.canonical_json_sha256(source)


def _reseal_artifact(artifact: dict) -> None:
    artifact["artifact_id"] = ""
    artifact["artifact_id"] = "rpe-" + core.canonical_json_sha256(artifact)


def _registered_cell(
    cell_id: str,
    metric: str,
    members: list[dict[str, str]],
    *,
    composition_rule: str = core.DEFAULT_COMPOSITION_RULE,
) -> dict:
    return {
        "cell_id": cell_id,
        "metric": metric,
        "window_class": "phase",
        "target_precheck_path": [
            "phase",
            "prefill" if metric.endswith("prefill") else "decode",
        ],
        "measurand": "gross_phase_energy_j",
        "reducer": core.MEMBER_REDUCER,
        "expected_n": 50,
        "members": [
            {"ordinal": ordinal, **member}
            for ordinal, member in enumerate(members, start=1)
        ],
        "interval_policy": {
            "composition_rule": composition_rule,
            "t95_critical_value": (
                None if composition_rule == core.DEFAULT_COMPOSITION_RULE else 2.0
            ),
            "window_allowance_j": (
                None if composition_rule == core.DEFAULT_COMPOSITION_RULE else 0.25
            ),
        },
        "missing_or_invalid_member": "refuse_reported_mean",
        "numeric_value": None,
    }


def _write_member_bundle(
    runs_root: Path,
    *,
    bundle_id: str,
    decode_j: float,
    prefill_j: float,
    prompt_tokens: int,
    token_source: str,
) -> dict[str, str]:
    bundle = runs_root / bundle_id
    bundle.mkdir(parents=True)
    output_tokens = 512
    config = {
        "schema_version": "0.1",
        "run_id": bundle_id,
        "model": {
            "name": "mock-model",
            "family": "mock",
            "source": None,
            "revision": None,
            "weight_format": "mock",
            "context_window": 8192,
        },
        "quantization": {
            "name": "none",
            "bits": None,
            "group_size": None,
        },
        "hardware_target": {
            "id": "synthetic_mac",
            "device_kind": "test",
            "host": None,
            "runtime_backend": "mock",
            "telemetry_backend": "powermetrics",
            "transport": "local",
            "notes": None,
        },
        "workload_profile": {
            "name": "reported_energy_fixture",
            "prompt_text": None,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "repetitions": 1,
            "warmup_runs": 1,
            "dataset_ref": None,
        },
        "sampling": {
            "power_hz": 20.0,
            "idle_seconds": 1.0,
            "warmup_seconds": 0.0,
        },
        "interconnect": {
            "name": "local",
            "link_speed_mbps": None,
            "notes": None,
        },
        "run_metadata": {
            "project": "capstone-joulewise",
            "operator": "test",
            "ambient_temp_c": None,
            "notes": None,
            "tags": ["synthetic_non_measurement"],
        },
    }
    config_bytes = core.canonical_json_bytes(config)
    (bundle / "config.json").write_bytes(config_bytes)
    metadata = {
        "run_id": bundle_id,
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "workload_observed": {
            "token_count": prompt_tokens + output_tokens,
            "output_token_count": output_tokens,
            "token_count_source": token_source,
        },
        "workload_provenance": {
            "prompt": {"realized_token_count": prompt_tokens}
        },
    }
    metadata_bytes = core.canonical_json_bytes(metadata)
    (bundle / "metadata.json").write_bytes(metadata_bytes)

    def envelope(point: float) -> dict:
        return {
            "method": "common_trace_shift_plus_independent_edge_corners_v3",
            "anchor_bound_s": 0.01,
            "point_j": point,
            "lower_j": point - 1.0,
            "upper_j": point + 2.0,
            "max_abs_delta_j": 2.0,
        }

    summary = {
        "status": "succeeded",
        "phase_energy_j": {"decode": decode_j, "prefill": prefill_j},
        "energy_anchor_shift_envelopes": {
            "/phase_energy_j/decode": envelope(decode_j),
            "/phase_energy_j/prefill": envelope(prefill_j),
        },
        "measurement_quality": {"token_counts_source": token_source},
    }
    summary_bytes = core.canonical_json_bytes(summary)
    (bundle / "summary_metrics.json").write_bytes(summary_bytes)
    events = [
        {
            "timestamp_s": 0.0,
            "event_type": "phase_end",
            "phase": "tokenize",
            "message": "",
            "metadata": {"prompt_tokens": prompt_tokens},
        },
        {
            "timestamp_s": 0.1,
            "event_type": "phase_start",
            "phase": "prefill",
            "message": "",
            "metadata": {"prompt_tokens": prompt_tokens},
        },
    ]
    (bundle / "events.jsonl").write_bytes(
        b"".join(core.canonical_json_bytes(row) + b"\n" for row in events)
    )
    return {
        "bundle_id": bundle_id,
        "bundle_path": bundle_id,
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "metadata_sha256": hashlib.sha256(metadata_bytes).hexdigest(),
        "summary_sha256": hashlib.sha256(summary_bytes).hexdigest(),
    }


def _source_material_from_blueprint(
    row: dict,
    selected_prefill_tokens: int,
    runs_root: Path,
    *,
    composition_rule: str = core.DEFAULT_COMPOSITION_RULE,
    mixed_sources: bool = False,
) -> dict:
    role = row["campaign_role"]
    model = row["model_id"]
    base_ids = [f"fixture-{role}-base-{index:02d}" for index in range(1, 51)]
    selected_ids = [
        f"fixture-{role}-prefill-p{selected_prefill_tokens}-{index:02d}"
        for index in range(1, 51)
    ]
    occurrences: list[dict[str, str]] = []
    base_members: list[dict[str, str]] = []
    selected_members: list[dict[str, str]] = []
    for ordinal, bundle_id in enumerate(base_ids, start=1):
        occurrence = _write_member_bundle(
            runs_root,
            bundle_id=bundle_id,
            decode_j=row["decode_point_base_j"] + ordinal / 10,
            prefill_j=row["p42_point_base_j"] + ordinal / 10,
            prompt_tokens=42,
            token_source=(
                "server_usage" if mixed_sources and ordinal == 1
                else row["token_count_source"]
            ),
        )
        occurrences.append(occurrence)
        base_members.append(
            {
                "bundle_id": bundle_id,
                "config_sha256": occurrence["config_sha256"],
            }
        )
    for ordinal, bundle_id in enumerate(selected_ids, start=1):
        occurrence = _write_member_bundle(
            runs_root,
            bundle_id=bundle_id,
            decode_j=row["decode_point_base_j"] + ordinal / 10,
            prefill_j=row["selected_prefill_point_base_j"] + ordinal / 10,
            prompt_tokens=selected_prefill_tokens,
            token_source=(
                "server_usage" if mixed_sources and ordinal == 1
                else row["token_count_source"]
            ),
        )
        occurrences.append(occurrence)
        selected_members.append(
            {
                "bundle_id": bundle_id,
                "config_sha256": occurrence["config_sha256"],
            }
        )
    registered = [
        _registered_cell(
            f"d117-reported-mean-ph-decode-{model}",
            "phase_energy_j.decode",
            base_members,
            composition_rule=composition_rule,
        ),
        _registered_cell(
            f"d117-reported-mean-ph-prefill-p42-{model}",
            "phase_energy_j.prefill",
            base_members,
            composition_rule=composition_rule,
        ),
        _registered_cell(
            f"d117-reported-mean-ph-prefill-p{selected_prefill_tokens}-{model}",
            "phase_energy_j.prefill",
            selected_members,
            composition_rule=composition_rule,
        ),
    ]
    floor_cells = [
        {
            "cell_id": f"synthetic-floor-{role}",
            "kind": "absolute",
            "metric": "gross_energy_j",
            "window_class": "request",
            "members": [
                {"slot": base_ids[0], "bundle_id": base_ids[0]}
            ],
        }
    ]
    spec = {
        "schema_version": core.EXTRACTION_SPEC_SCHEMA_VERSION,
        "cells": floor_cells,
        "reported_energy_cells": registered,
        "reported_energy_registration": {
            "authority": "D-123",
            "procedure_only": True,
            "postcollection_numeric_values": (
                "structurally_absent_until_governed_reduction"
            ),
            "floor_projection_sha256": core.canonical_json_sha256(floor_cells),
            "no_semantics_change_rule": "fixture-only disjoint projection",
        },
    }
    extraction_report = json.loads(
        PRODUCTION_EXTRACTION_REPORT.read_text(encoding="utf-8")
    )
    extraction_report["runs_root"] = str(runs_root.resolve())
    basis_payload = {
        "schema_version": "joulewise.idle_admission_evaluation_basis.v1",
        "policy_sha256": _digest(f"policy:{role}"),
        "member_occurrences": sorted(
            occurrences, key=lambda item: (item["bundle_id"], item["bundle_path"])
        ),
        "calibration_bracket_set": None,
        "consumption_semantics_id": extraction_report["consumption_semantics_id"],
    }
    basis = {
        **basis_payload,
        "sha256": core.canonical_json_sha256(basis_payload),
    }
    for allowance in extraction_report["whole_window_drift_allowances"].values():
        allowance["whole_window_evaluation_basis_sha256"] = basis["sha256"]
    for cell in extraction_report["cells"]:
        allowance = cell.get("whole_window_drift_allowance")
        if isinstance(allowance, dict):
            allowance["whole_window_evaluation_basis_sha256"] = basis["sha256"]
        floor = cell.get("floor")
        if isinstance(floor, dict):
            provenance = floor.get("whole_window_drift_allowance_provenance")
            if isinstance(provenance, dict):
                provenance["whole_window_evaluation_basis_sha256"] = basis["sha256"]
    g2a = {
        "schema_version": core.G2A_SCHEMA_VERSION,
        "collection_prefill_tokens": selected_prefill_tokens,
        "fixture_only": True,
    }
    prompt_pin = {
        "schema_version": core.PROMPT_PIN_SCHEMA_VERSION,
        "prefill_length": selected_prefill_tokens,
        "prompt_tokens": selected_prefill_tokens,
        "g2a_record_sha256": core.canonical_json_sha256(g2a),
        "fixture_only": True,
    }
    return {
        "schema_version": core.SOURCE_MATERIAL_SCHEMA_VERSION,
        "campaign_role": role,
        "source_commit": row["source_commit_fill"] * 40,
        "extraction_spec": _wrap(f"{role}/extraction-spec.json", spec),
        "extraction_report": _wrap(
            f"{role}/extraction-report.json", extraction_report
        ),
        "whole_window_evaluation_basis": _wrap(
            f"{role}/whole-window-evaluation-basis.json", basis
        ),
        "g2a_selection": _wrap(f"{role}/g2a-selection.json", g2a),
        "prompt_pin": _wrap(f"{role}/prompt-pin.json", prompt_pin),
    }


def _source_bytes(source: dict) -> bytes:
    return core.canonical_json_bytes(source)


def _issued_projection(
    artifacts: list[dict], sources: list[dict]
) -> tuple[bytes, str]:
    issuance = core.build_reported_phase_energy_issuance(
        artifacts,
        {source["campaign_role"]: _source_bytes(source) for source in sources},
    )
    raw = core.canonical_json_bytes(issuance)
    return raw, hashlib.sha256(raw).hexdigest()


def _paths_with_keys(value: object, keys: set[str], path: tuple = ()) -> list[tuple]:
    result = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            if key in keys or key.endswith("_sha256"):
                result.append(child_path)
            result.extend(_paths_with_keys(child, keys, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.extend(_paths_with_keys(child, keys, (*path, index)))
    return result


def _set_path(value: object, path: tuple, replacement: object) -> None:
    target = value
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement


class ReportedPhaseEnergyContractTests(unittest.TestCase):
    maxDiff = None

    def test_fixed_authenticated_parents_determine_one_reported_energy_projection(
        self,
    ) -> None:
        blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            materials = [
                _source_material_from_blueprint(
                    row,
                    blueprint["selected_prefill_tokens"],
                    root / row["campaign_role"],
                )
                for row in blueprint["packs"]
            ]
            self.assertTrue(
                all("reported_energy_projection" not in row for row in materials)
            )
            caller_projection = copy.deepcopy(materials[0])
            caller_projection["reported_energy_projection"] = _wrap(
                "caller/projection.json",
                {"schema_version": core.PROJECTION_SCHEMA_VERSION},
            )
            with self.assertRaisesRegex(
                core.StopFill, "^source_material_closed_keys_mismatch$"
            ):
                core.build_reported_phase_energy_source(
                    _source_bytes(caller_projection)
                )
            projections = [
                core.build_reported_phase_energy_projection(_source_bytes(material))
                for material in materials
            ]
            sources = [
                core.build_reported_phase_energy_source(_source_bytes(material))
                for material in materials
            ]
            artifacts = [
                core.build_reported_phase_energy(_source_bytes(source))
                for source in sources
            ]
            issuance_bytes, _ = _issued_projection(artifacts, sources)
            self.assertEqual(
                projections[0]["reported_energy_cells"][0]["per_token"][
                    "value_j_per_token"
                ],
                102.55 / 512,
            )

            self.assertEqual(
                core.canonical_json_bytes(
                    core.build_reported_phase_energy_projection(
                        _source_bytes(materials[0])
                    )
                ),
                core.canonical_json_bytes(projections[0]),
            )

            attacked_source = copy.deepcopy(sources[0])
            attacked_projection = attacked_source[
                "reported_energy_projection"
            ]["document"]
            cell = attacked_projection["reported_energy_cells"][0]
            member = cell["members"][0]
            member["energy_j"] += 100.0
            member["energy_interval_j"]["lower_j"] += 100.0
            member["energy_interval_j"]["upper_j"] += 100.0
            points = [row["energy_j"] for row in cell["members"]]
            lowers = [
                row["energy_interval_j"]["lower_j"] for row in cell["members"]
            ]
            uppers = [
                row["energy_interval_j"]["upper_j"] for row in cell["members"]
            ]
            cell["mean_j_per_request"] = math.fsum(points) / 50
            cell["interval"]["lower_j"] = math.fsum(lowers) / 50
            cell["interval"]["upper_j"] = math.fsum(uppers) / 50
            cell["per_token"]["numerator_energy_j"] = math.fsum(points)
            cell["per_token"]["value_j_per_token"] = (
                math.fsum(points) / cell["per_token"]["observed_token_count"]
            )
            _reseal_wrapper(attacked_source, "reported_energy_projection")
            _reseal_source(attacked_source)
            attacked_source_bytes = _source_bytes(attacked_source)

            attacked_artifact = copy.deepcopy(artifacts[0])
            attacked_artifact["cells"] = copy.deepcopy(
                attacked_projection["reported_energy_cells"]
            )
            attacked_artifact["inputs"]["reported_energy_projection"][
                "file_sha256"
            ] = attacked_source["reported_energy_projection"]["file_sha256"]
            attacked_artifact["inputs"]["source"]["source_id"] = (
                attacked_source["source_id"]
            )
            attacked_artifact["inputs"]["source"]["file_sha256"] = (
                hashlib.sha256(attacked_source_bytes).hexdigest()
            )
            _reseal_artifact(attacked_artifact)
            self.assertEqual(core.validate_reported_phase_energy(attacked_artifact), [])

            attacked_issuance = json.loads(issuance_bytes)
            alpha = next(
                row
                for row in attacked_issuance["artifacts"]
                if row["campaign_role"] == "alpha"
            )
            alpha["artifact_id"] = attacked_artifact["artifact_id"]
            alpha["source_id"] = attacked_source["source_id"]
            attacked_issuance_bytes = core.canonical_json_bytes(attacked_issuance)
            self.assertEqual(
                core.validate_reported_phase_energy_issuance(attacked_issuance), []
            )
            self.assertRegex(
                hashlib.sha256(attacked_issuance_bytes).hexdigest(), r"^[0-9a-f]{64}$"
            )

            self.assertEqual(
                core.validate_reported_energy_projection_derivation(
                    attacked_source
                ),
                "reported_energy_projection_derivation_mismatch",
            )
            with self.assertRaisesRegex(
                core.StopFill,
                "^reported_energy_projection_derivation_mismatch$",
            ):
                core.build_reported_phase_energy_issuance(
                    [attacked_artifact, artifacts[1]],
                    {
                        "alpha": attacked_source_bytes,
                        "beta": _source_bytes(sources[1]),
                    },
                )

    def test_d123_reported_phase_energy_contract_table(self) -> None:
        blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        self.assertEqual(blueprint["fixture_kind"], "synthetic_non_measurement")
        self.assertEqual(blueprint["members_per_cell"], 50)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        parent_root = Path(temporary.name) / "parents"
        materials = [
            _source_material_from_blueprint(
                row,
                blueprint["selected_prefill_tokens"],
                parent_root / row["campaign_role"],
                mixed_sources=row["campaign_role"] == "alpha",
            )
            for row in blueprint["packs"]
        ]
        self.assertTrue(
            all("reported_energy_projection" not in material for material in materials)
        )
        sources = [
            core.build_reported_phase_energy_source(_source_bytes(material))
            for material in materials
        ]
        for source in sources:
            self.assertEqual(core.validate_reported_phase_energy_source(source), [])

        floor_before = FLOOR_COPY.read_bytes()
        floor_digest_before = hashlib.sha256(floor_before).hexdigest()
        self.assertEqual(floor_before, PREEXISTING_FLOOR.read_bytes())
        artifacts = [
            core.build_reported_phase_energy(_source_bytes(source))
            for source in sources
        ]
        issuance_bytes, issuance_sha256 = _issued_projection(artifacts, sources)
        self.assertEqual(
            hashlib.sha256(FLOOR_COPY.read_bytes()).hexdigest(),
            floor_digest_before,
        )
        self.assertNotEqual(artifacts[0]["artifact_id"], artifacts[1]["artifact_id"])
        for artifact, role in zip(artifacts, ("alpha", "beta")):
            with self.subTest(role=role, check="content-addressed-default"):
                self.assertEqual(artifact["campaign_role"], role)
                self.assertEqual(core.validate_reported_phase_energy(artifact), [])
                self.assertRegex(artifact["artifact_id"], r"^rpe-[0-9a-f]{64}$")
                self.assertTrue(
                    all(
                        cell["interval"]["composition_rule"]
                        == core.DEFAULT_COMPOSITION_RULE
                        for cell in artifact["cells"]
                    )
                )

        expected = {
            "[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request]": "202.55",
            "[E_1p7B_prefill_p[PREFILL_LENGTH]_lower_J]": "201.55",
            "[E_1p7B_prefill_p[PREFILL_LENGTH]_upper_J]": "204.55",
            "[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_token]": "0.39560546875",
            "[N_bundles_1p7B_prefill_p[PREFILL_LENGTH]]": "50",
            "[E_1p7B_decode_J_per_request]": "102.55",
            "[E_1p7B_decode_lower_J]": "101.55",
            "[E_1p7B_decode_upper_J]": "104.55",
            "[E_1p7B_decode_J_per_token]": "0.20029296875",
            "[N_bundles_1p7B_decode]": "50",
            "[E_8B_prefill_p[PREFILL_LENGTH]_J_per_request]": "502.55",
            "[E_8B_prefill_p[PREFILL_LENGTH]_lower_J]": "501.55",
            "[E_8B_prefill_p[PREFILL_LENGTH]_upper_J]": "504.55",
            "[E_8B_prefill_p[PREFILL_LENGTH]_J_per_token]": "0.98154296875",
            "[N_bundles_8B_prefill_p[PREFILL_LENGTH]]": "50",
            "[E_8B_decode_J_per_request]": "402.55",
            "[E_8B_decode_lower_J]": "401.55",
            "[E_8B_decode_upper_J]": "404.55",
            "[E_8B_decode_J_per_token]": "0.78623046875",
            "[N_bundles_8B_decode]": "50",
        }
        observed = core.reported_phase_energy_token_values(
            artifacts,
            issuance_manifest_bytes=issuance_bytes,
            expected_issuance_sha256=issuance_sha256,
        )
        self.assertEqual(set(observed), set(expected))
        for token, rendered in expected.items():
            with self.subTest(token=token):
                self.assertEqual(observed[token], rendered)
        for untrusted in (
            core.reported_phase_energy_token_values(artifacts),
            core.reported_phase_energy_token_values(
                artifacts,
                issuance_manifest_bytes=issuance_bytes,
                expected_issuance_sha256="0" * 64,
            ),
        ):
            self.assertTrue(
                all(value == core.STOP_FILL for value in untrusted.values())
            )

        for artifact in artifacts:
            for cell in artifact["cells"]:
                with self.subTest(role=artifact["campaign_role"], cell=cell["cell_id"]):
                    points = [member["energy_j"] for member in cell["members"]]
                    counts = [
                        member["observed_token_denominator"]["count"]
                        for member in cell["members"]
                    ]
                    self.assertEqual(
                        cell["per_token"]["value_j_per_token"],
                        math.fsum(points) / sum(counts),
                    )
                    self.assertEqual(cell["per_token"]["numerator_energy_j"], math.fsum(points))

        t95_material = _source_material_from_blueprint(
            blueprint["packs"][0],
            blueprint["selected_prefill_tokens"],
            parent_root / "t95-alpha",
            composition_rule=core.T95_WINDOW_COMPOSITION_RULE,
        )
        t95_source = core.build_reported_phase_energy_source(
            _source_bytes(t95_material)
        )
        t95_artifact = core.build_reported_phase_energy(_source_bytes(t95_source))
        for cell in t95_artifact["cells"]:
            with self.subTest(cell=cell["cell_id"], check="t95-window-rule"):
                interval = cell["interval"]
                self.assertEqual(
                    interval["composition_rule"], core.T95_WINDOW_COMPOSITION_RULE
                )
                self.assertEqual(
                    interval["repeatability_half_width_j"],
                    2.0
                    * statistics_stdev(
                        [member["energy_j"] for member in cell["members"]]
                    )
                    / math.sqrt(50),
                )
                self.assertEqual(core.validate_reported_phase_energy(t95_artifact), [])
        self.assertTrue(
            all(
                value == core.STOP_FILL
                for token, value in core.reported_phase_energy_token_values(
                    [t95_artifact, artifacts[1]],
                    issuance_manifest_bytes=issuance_bytes,
                    expected_issuance_sha256=issuance_sha256,
                ).items()
                if "1p7B" in token
            )
        )
        forged_t95_issuance = json.loads(issuance_bytes)
        alpha_binding = next(
            row
            for row in forged_t95_issuance["artifacts"]
            if row["campaign_role"] == "alpha"
        )
        alpha_binding["artifact_id"] = t95_artifact["artifact_id"]
        alpha_binding["source_id"] = t95_source["source_id"]
        forged_t95_bytes = core.canonical_json_bytes(forged_t95_issuance)
        forged_t95_values = core.reported_phase_energy_token_values(
            [t95_artifact, artifacts[1]],
            issuance_manifest_bytes=forged_t95_bytes,
            expected_issuance_sha256=hashlib.sha256(forged_t95_bytes).hexdigest(),
        )
        self.assertTrue(
            all(
                forged_t95_values[token] == core.STOP_FILL
                for token in expected
                if "1p7B" in token
            )
        )
        self.assertTrue(
            all(
                forged_t95_values[token] == expected[token]
                for token in expected
                if "8B" in token
            )
        )
        with self.assertRaisesRegex(
            core.StopFill, "issuance_composition_rule_not_current"
        ):
            core.build_reported_phase_energy_issuance(
                [t95_artifact, artifacts[1]],
                {"alpha": _source_bytes(t95_source), "beta": _source_bytes(sources[1])},
            )

        artifact_failure = copy.deepcopy(sources[0])
        artifact_failure["extraction_spec"]["file_sha256"] = "0" * 64
        _reseal_source(artifact_failure)
        with self.assertRaises(core.StopFill):
            core.build_reported_phase_energy(_source_bytes(artifact_failure))

        outcome_failure = copy.deepcopy(sources[0])
        outcome_failure["extraction_report"]["document"][
            "all_cells_extractable"
        ] = False
        _reseal_wrapper(outcome_failure, "extraction_report")
        _reseal_source(outcome_failure)
        with self.assertRaises(core.StopFill):
            core.build_reported_phase_energy(_source_bytes(outcome_failure))

        cell_cases = {
            "member_identity": lambda source, member: member.__setitem__(
                "bundle_id", "different-issued-bundle"
            ),
            "member_digest": lambda source, member: member.__setitem__(
                "config_sha256", "0" * 64
            ),
            "member_outcome": lambda source, member: member.__setitem__(
                "admitted", False
            ),
            "cell_outcome": lambda source, member: source[
                "reported_energy_projection"
            ][
                "document"
            ]["reported_energy_cells"][0].__setitem__("status", "refused"),
            "cell_expected_census": lambda source, member: source[
                "reported_energy_projection"
            ]["document"]["reported_energy_cells"][0].__setitem__(
                "registered_member_count", 49
            ),
            "cell_observed_census": lambda source, member: source[
                "reported_energy_projection"
            ]["document"]["reported_energy_cells"][0].__setitem__(
                "admitted_independent_bundle_count", 49
            ),
            "cell_admitted_census": lambda source, member: source[
                "reported_energy_projection"
            ]["document"]["reported_energy_cells"][0].__setitem__(
                "registered_member_count", 48
            ),
            "energy_endpoint": lambda source, member: member[
                "energy_interval_j"
            ].__setitem__("lower_j", member["energy_j"] + 1),
        }
        for label, mutate in cell_cases.items():
            attacked = copy.deepcopy(sources[0])
            member = attacked["reported_energy_projection"]["document"][
                "reported_energy_cells"
            ][0]["members"][0]
            mutate(attacked, member)
            _reseal_wrapper(attacked, "reported_energy_projection")
            _reseal_source(attacked)
            with self.subTest(mutation=label, refusal="derivation"):
                self.assertEqual(
                    core.validate_reported_energy_projection_derivation(attacked),
                    "reported_energy_projection_derivation_mismatch",
                )
                with self.assertRaisesRegex(
                    core.StopFill,
                    "^reported_energy_projection_derivation_mismatch$",
                ):
                    core.build_reported_phase_energy(_source_bytes(attacked))

        selected_cell = next(
            cell
            for cell in artifacts[0]["cells"]
            if f"prefill-p{blueprint['selected_prefill_tokens']}" in cell["cell_id"]
        )
        self.assertEqual(
            selected_cell["per_token"]["token_count_sources"],
            ["runtime_observed", "server_usage"],
        )
        invalid_denominator_row = copy.deepcopy(blueprint["packs"][0])
        invalid_denominator_row["token_count_source"] = "config_fallback"
        invalid_denominator_material = _source_material_from_blueprint(
            invalid_denominator_row,
            blueprint["selected_prefill_tokens"],
            parent_root / "invalid-denominator-alpha",
        )
        invalid_denominator_source = core.build_reported_phase_energy_source(
            _source_bytes(invalid_denominator_material)
        )
        invalid_denominator_artifact = core.build_reported_phase_energy(
            _source_bytes(invalid_denominator_source)
        )
        refused_token_cell = next(
            cell
            for cell in invalid_denominator_artifact["cells"]
            if f"prefill-p{blueprint['selected_prefill_tokens']}" in cell["cell_id"]
        )
        self.assertEqual(refused_token_cell["status"], "issued")
        self.assertIsNone(refused_token_cell["per_token"])
        self.assertEqual(
            refused_token_cell["refusal_reasons"],
            ["runtime_token_denominator_invalid"],
        )

        join_failure = copy.deepcopy(sources[0])
        join_failure["prompt_pin"]["document"]["prefill_length"] = 1024
        _reseal_wrapper(join_failure, "prompt_pin")
        _reseal_source(join_failure)
        with self.assertRaises(core.StopFill):
            core.build_reported_phase_energy(_source_bytes(join_failure))

        incompatible_report = copy.deepcopy(materials[0])
        incompatible_report["extraction_report"] = _wrap(
            "alpha/extraction-report.json",
            {
                "schema_version": core.EXTRACTION_REPORT_SCHEMA_VERSION,
                "artifact_id": "dfer-" + "0" * 64,
                "campaign_role": "alpha",
                "outcome": "issued",
                "consumption_semantics_id": "invented_fixture_wire.v1",
            },
        )
        with self.assertRaisesRegex(
            core.StopFill, "extraction_report_contract_invalid"
        ):
            core.build_reported_phase_energy_source(
                _source_bytes(incompatible_report)
            )

        missing_custody_source = copy.deepcopy(sources[0])
        missing_member = missing_custody_source["reported_energy_projection"][
            "document"
        ]["reported_energy_cells"][0]["members"][0]
        for key in (
            "bundle_sha256",
            "summary_sha256",
            "metadata_sha256",
            "whole_window_evaluation_basis_sha256",
        ):
            del missing_member[key]
        _reseal_wrapper(missing_custody_source, "reported_energy_projection")
        _reseal_source(missing_custody_source)
        self.assertEqual(
            core.validate_reported_energy_projection_derivation(
                missing_custody_source
            ),
            "reported_energy_projection_derivation_mismatch",
        )
        with self.assertRaisesRegex(
            core.StopFill, "^reported_energy_projection_derivation_mismatch$"
        ):
            core.build_reported_phase_energy(_source_bytes(missing_custody_source))

        alternate_row = copy.deepcopy(blueprint["packs"][0])
        alternate_row["decode_point_base_j"] += 10.0
        alternate_material = _source_material_from_blueprint(
            alternate_row,
            blueprint["selected_prefill_tokens"],
            parent_root / "alternate-alpha",
        )
        alternate_source = core.build_reported_phase_energy_source(
            _source_bytes(alternate_material)
        )
        alternate_artifact = core.build_reported_phase_energy(
            _source_bytes(alternate_source)
        )
        for ordered in (
            [artifacts[0], alternate_artifact, artifacts[1]],
            [alternate_artifact, artifacts[0], artifacts[1]],
        ):
            duplicate_values = core.reported_phase_energy_token_values(
                ordered,
                issuance_manifest_bytes=issuance_bytes,
                expected_issuance_sha256=issuance_sha256,
            )
            self.assertTrue(
                all(
                    duplicate_values[token] == core.STOP_FILL
                    for token in expected
                    if "1p7B" in token
                )
            )
            self.assertTrue(
                all(
                    duplicate_values[token] == expected[token]
                    for token in expected
                    if "8B" in token
                )
            )

        resealed_attack = copy.deepcopy(artifacts[0])
        resealed_attack["cells"][0]["members"][0]["energy_j"] += 100.0
        resealed_attack["cells"][0]["members"][0]["energy_interval_j"][
            "lower_j"
        ] += 100.0
        resealed_attack["cells"][0]["members"][0]["energy_interval_j"][
            "upper_j"
        ] += 100.0
        points = [member["energy_j"] for member in resealed_attack["cells"][0]["members"]]
        lowers = [
            member["energy_interval_j"]["lower_j"]
            for member in resealed_attack["cells"][0]["members"]
        ]
        uppers = [
            member["energy_interval_j"]["upper_j"]
            for member in resealed_attack["cells"][0]["members"]
        ]
        cell = resealed_attack["cells"][0]
        cell["mean_j_per_request"] = math.fsum(points) / 50
        cell["interval"]["lower_j"] = math.fsum(lowers) / 50
        cell["interval"]["upper_j"] = math.fsum(uppers) / 50
        cell["per_token"]["numerator_energy_j"] = math.fsum(points)
        cell["per_token"]["value_j_per_token"] = (
            math.fsum(points) / cell["per_token"]["observed_token_count"]
        )
        _reseal_artifact(resealed_attack)
        self.assertEqual(core.validate_reported_phase_energy(resealed_attack), [])
        resealed_values = core.reported_phase_energy_token_values(
            [resealed_attack, artifacts[1]],
            issuance_manifest_bytes=issuance_bytes,
            expected_issuance_sha256=issuance_sha256,
        )
        self.assertTrue(
            all(
                resealed_values[token] == core.STOP_FILL
                for token in expected
                if "1p7B" in token
            )
        )

        mutation_paths = _paths_with_keys(
            artifacts[0],
            {
                "artifact_id",
                "source_commit",
                "status",
                "registered_member_count",
                "admitted_independent_bundle_count",
                "admitted",
                "ordinal",
                "count",
                "observed_token_count",
                "observed_total_token_count",
                "observed_output_token_count",
                "prompt_realized_token_count",
                "tokenize_prompt_token_count",
                "prefill_prompt_token_count",
                "mean_j_per_request",
                "lower_j",
                "upper_j",
                "value_j_per_token",
                "numerator_energy_j",
                "energy_j",
                "token_count_sources",
            },
        )
        self.assertGreater(len(mutation_paths), 500)
        alpha_tokens = [token for token in expected if "1p7B" in token]
        for path in mutation_paths:
            attacked = copy.deepcopy(artifacts[0])
            current = attacked
            for part in path:
                current = current[part]
            if path[-1] == "artifact_id":
                replacement = "rpe-" + "0" * 64
            elif path[-1] == "source_commit":
                replacement = "0" * 40
            elif path[-1].endswith("_sha256"):
                replacement = "0" * 64
            elif path[-1] == "token_count_sources":
                replacement = ["config_fallback"]
            elif path[-1] == "status":
                replacement = "unknown"
            elif path[-1] == "admitted":
                replacement = not current
            else:
                replacement = current + 1
            _set_path(attacked, path, replacement)
            if path[-1] != "artifact_id":
                _reseal_artifact(attacked)
            projected = core.reported_phase_energy_token_values(
                [attacked, artifacts[1]],
                issuance_manifest_bytes=issuance_bytes,
                expected_issuance_sha256=issuance_sha256,
            )
            with self.subTest(mutation_path=path):
                self.assertTrue(
                    all(projected[token] == core.STOP_FILL for token in alpha_tokens)
                )

        registry = REGISTRY.read_text(encoding="utf-8")
        for token in expected:
            row = next(
                line for line in registry.splitlines() if f"`{token}`" in line
            )
            with self.subTest(token=token, check="registry-sync"):
                self.assertIn("joulewise.reported_phase_energy.v1", row)
                self.assertIn(core.DEFAULT_COMPOSITION_RULE, row)
                self.assertIn("STOP_FILL on", row)
                self.assertIn("VALUE_UNISSUED", row)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / "alpha-source.json"
            material_path = root / "alpha-source-material.json"
            output_path = root / "alpha-artifact.json"
            material_path.write_bytes(_source_bytes(materials[0]))
            produced_source_path = root / "alpha-source-produced.json"
            produced = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    str(material_path),
                    "--produce-source",
                    "--output",
                    str(produced_source_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(produced.returncode, 0, produced.stderr)
            self.assertEqual(
                json.loads(produced_source_path.read_text(encoding="utf-8")),
                sources[0],
            )
            source_path.write_bytes(_source_bytes(sources[0]))
            result = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    str(source_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")), artifacts[0]
            )
            repeated = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    str(source_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(repeated.returncode, 2)
            self.assertIn("output_exists", repeated.stderr)

        self.assertEqual(FLOOR_COPY.read_bytes(), floor_before)


def statistics_stdev(values: list[float]) -> float:
    # Local import keeps the one acceptance method's relation readable.
    import statistics

    return statistics.stdev(values)


if __name__ == "__main__":
    unittest.main()
