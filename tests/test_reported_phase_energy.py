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
BUILDER = ROOT / "scripts/build_reported_phase_energy.py"


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _report_id(report: dict) -> str:
    preimage = copy.deepcopy(report)
    preimage["artifact_id"] = ""
    return "dfer-" + core.canonical_json_sha256(preimage)


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


def _reseal_report(source: dict) -> None:
    report = source["extraction_report"]["document"]
    report["artifact_id"] = _report_id(report)
    _reseal_wrapper(source, "extraction_report")


def _registered_cell(cell_id: str, metric: str, member_ids: list[str]) -> dict:
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
            {
                "ordinal": ordinal,
                "bundle_id": bundle_id,
                "config_sha256": _digest(f"config:{bundle_id}"),
            }
            for ordinal, bundle_id in enumerate(member_ids, start=1)
        ],
        "missing_or_invalid_member": "refuse_reported_mean",
        "numeric_value": None,
    }


def _reported_cell(
    registered: dict,
    *,
    base_j: float,
    prompt_tokens: int,
    token_source: str,
) -> dict:
    decode = registered["metric"] == "phase_energy_j.decode"
    members = []
    for registered_member in registered["members"]:
        ordinal = registered_member["ordinal"]
        bundle_id = registered_member["bundle_id"]
        point = base_j + ordinal / 10
        output_tokens = 512
        members.append(
            {
                "ordinal": ordinal,
                "bundle_id": bundle_id,
                "config_sha256": registered_member["config_sha256"],
                "bundle_sha256": _digest(f"bundle:{bundle_id}"),
                "summary_sha256": _digest(
                    f"summary:{registered['cell_id']}:{bundle_id}"
                ),
                "metadata_sha256": _digest(f"metadata:{bundle_id}"),
                "whole_window_evaluation_basis_sha256": _digest(
                    f"basis:{bundle_id}"
                ),
                "outcome": "admitted",
                "reasons": [],
                "point_j": point,
                "energy_anchor_shift_envelope": {
                    "point_j": point,
                    "lower_j": point - 1.0,
                    "upper_j": point + 2.0,
                },
                "observed_token_denominator": {
                    "kind": (
                        core.OUTPUT_DENOMINATOR_KIND
                        if decode
                        else core.PROMPT_DENOMINATOR_KIND
                    ),
                    "count": output_tokens if decode else prompt_tokens,
                    "token_count_source": token_source,
                    "observed_total_token_count": prompt_tokens + output_tokens,
                    "observed_output_token_count": output_tokens,
                    "prompt_realized_token_count": prompt_tokens,
                    "tokenize_prompt_token_count": prompt_tokens,
                    "prefill_prompt_token_count": prompt_tokens,
                },
            }
        )
    return {
        "cell_id": registered["cell_id"],
        "metric": registered["metric"],
        "outcome": "issued",
        "expected_n": 50,
        "observed_n": 50,
        "admitted_n": 50,
        "interval_policy": {
            "composition_rule": core.DEFAULT_COMPOSITION_RULE,
            "t95_critical_value": None,
            "window_allowance_j": None,
        },
        "members": members,
    }


def _source_from_blueprint(row: dict, selected_prefill_tokens: int) -> dict:
    role = row["campaign_role"]
    model = row["model_id"]
    base_ids = [f"fixture-{role}-base-{index:02d}" for index in range(1, 51)]
    selected_ids = [
        f"fixture-{role}-prefill-p{selected_prefill_tokens}-{index:02d}"
        for index in range(1, 51)
    ]
    registered = [
        _registered_cell(
            f"d117-reported-mean-ph-decode-{model}",
            "phase_energy_j.decode",
            base_ids,
        ),
        _registered_cell(
            f"d117-reported-mean-ph-prefill-p42-{model}",
            "phase_energy_j.prefill",
            base_ids,
        ),
        _registered_cell(
            f"d117-reported-mean-ph-prefill-p{selected_prefill_tokens}-{model}",
            "phase_energy_j.prefill",
            selected_ids,
        ),
    ]
    floor_cells = [{"cell_id": f"synthetic-floor-{role}", "fixture_only": True}]
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
    report_cells = [
        _reported_cell(
            registered[0],
            base_j=row["decode_point_base_j"],
            prompt_tokens=88,
            token_source=row["token_count_source"],
        ),
        _reported_cell(
            registered[1],
            base_j=row["p42_point_base_j"],
            prompt_tokens=42,
            token_source=row["token_count_source"],
        ),
        _reported_cell(
            registered[2],
            base_j=row["selected_prefill_point_base_j"],
            prompt_tokens=selected_prefill_tokens,
            token_source=row["token_count_source"],
        ),
    ]
    report = {
        "schema_version": core.EXTRACTION_REPORT_SCHEMA_VERSION,
        "artifact_id": "",
        "campaign_role": role,
        "outcome": "issued",
        "consumption_semantics_id": "d123_fixture_issued_fields.v1",
        "reported_energy_cells": report_cells,
    }
    report["artifact_id"] = _report_id(report)
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
        "schema_version": core.SOURCE_SCHEMA_VERSION,
        "campaign_role": role,
        "source_commit": row["source_commit_fill"] * 40,
        "extraction_spec": _wrap(f"{role}/extraction-spec.json", spec),
        "extraction_report": _wrap(f"{role}/extraction-report.json", report),
        "g2a_selection": _wrap(f"{role}/g2a-selection.json", g2a),
        "prompt_pin": _wrap(f"{role}/prompt-pin.json", prompt_pin),
    }


def _source_bytes(source: dict) -> bytes:
    return core.canonical_json_bytes(source)


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

    def test_d123_reported_phase_energy_contract_table(self) -> None:
        blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
        self.assertEqual(blueprint["fixture_kind"], "synthetic_non_measurement")
        self.assertEqual(blueprint["members_per_cell"], 50)
        sources = [
            _source_from_blueprint(row, blueprint["selected_prefill_tokens"])
            for row in blueprint["packs"]
        ]

        floor_before = FLOOR_COPY.read_bytes()
        floor_digest_before = hashlib.sha256(floor_before).hexdigest()
        self.assertEqual(floor_before, PREEXISTING_FLOOR.read_bytes())
        artifacts = [
            core.build_reported_phase_energy(_source_bytes(source))
            for source in sources
        ]
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
        observed = core.reported_phase_energy_token_values(artifacts)
        self.assertEqual(set(observed), set(expected))
        for token, rendered in expected.items():
            with self.subTest(token=token):
                self.assertEqual(observed[token], rendered)

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

        t95_source = copy.deepcopy(sources[0])
        for cell in t95_source["extraction_report"]["document"][
            "reported_energy_cells"
        ]:
            cell["interval_policy"] = {
                "composition_rule": core.T95_WINDOW_COMPOSITION_RULE,
                "t95_critical_value": 2.0,
                "window_allowance_j": 0.25,
            }
        _reseal_report(t95_source)
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

        artifact_failure = copy.deepcopy(sources[0])
        artifact_failure["extraction_spec"]["file_sha256"] = "0" * 64
        with self.assertRaises(core.StopFill):
            core.build_reported_phase_energy(_source_bytes(artifact_failure))

        outcome_failure = copy.deepcopy(sources[0])
        outcome_failure["extraction_report"]["document"]["outcome"] = "refused"
        _reseal_report(outcome_failure)
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
                "outcome", "excluded"
            ),
            "cell_outcome": lambda source, member: source["extraction_report"][
                "document"
            ]["reported_energy_cells"][0].__setitem__("outcome", "refused"),
            "cell_expected_census": lambda source, member: source[
                "extraction_report"
            ]["document"]["reported_energy_cells"][0].__setitem__("expected_n", 49),
            "cell_observed_census": lambda source, member: source[
                "extraction_report"
            ]["document"]["reported_energy_cells"][0].__setitem__("observed_n", 49),
            "cell_admitted_census": lambda source, member: source[
                "extraction_report"
            ]["document"]["reported_energy_cells"][0].__setitem__("admitted_n", 49),
            "energy_endpoint": lambda source, member: member[
                "energy_anchor_shift_envelope"
            ].__setitem__("lower_j", member["point_j"] + 1),
        }
        for label, mutate in cell_cases.items():
            attacked = copy.deepcopy(sources[0])
            member = attacked["extraction_report"]["document"][
                "reported_energy_cells"
            ][0]["members"][0]
            mutate(attacked, member)
            _reseal_report(attacked)
            artifact = core.build_reported_phase_energy(_source_bytes(attacked))
            values = core.reported_phase_energy_token_values([artifact, artifacts[1]])
            with self.subTest(mutation=label, refusal="cell"):
                self.assertTrue(
                    all(
                        values[token] == core.STOP_FILL
                        for token in expected
                        if token.startswith("[E_1p7B_decode")
                        or token == "[N_bundles_1p7B_decode]"
                    )
                )
                self.assertEqual(
                    values[
                        "[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request]"
                    ],
                    expected[
                        "[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request]"
                    ],
                )

        token_cases = {
            "denominator_source": lambda denominator: denominator.__setitem__(
                "token_count_source", "config_fallback"
            ),
            "prompt_four_surface": lambda denominator: denominator.__setitem__(
                "tokenize_prompt_token_count",
                denominator["tokenize_prompt_token_count"] + 1,
            ),
            "mixed_runtime_sources": lambda denominator: denominator.__setitem__(
                "token_count_source", "server_usage"
            ),
        }
        for label, mutate in token_cases.items():
            attacked = copy.deepcopy(sources[0])
            denominator = attacked["extraction_report"]["document"][
                "reported_energy_cells"
            ][2]["members"][0]["observed_token_denominator"]
            mutate(denominator)
            _reseal_report(attacked)
            artifact = core.build_reported_phase_energy(_source_bytes(attacked))
            values = core.reported_phase_energy_token_values([artifact, artifacts[1]])
            with self.subTest(mutation=label, refusal="per-token"):
                self.assertEqual(
                    values[
                        "[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_token]"
                    ],
                    core.STOP_FILL,
                )
                self.assertEqual(
                    values[
                        "[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request]"
                    ],
                    expected[
                        "[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request]"
                    ],
                )
                self.assertEqual(
                    values["[N_bundles_1p7B_prefill_p[PREFILL_LENGTH]]"], "50"
                )

        join_failure = copy.deepcopy(sources[0])
        join_failure["prompt_pin"]["document"]["prefill_length"] = 1024
        _reseal_wrapper(join_failure, "prompt_pin")
        with self.assertRaises(core.StopFill):
            core.build_reported_phase_energy(_source_bytes(join_failure))

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
            elif path[-1] == "status":
                replacement = "unknown"
            elif path[-1] == "admitted":
                replacement = not current
            else:
                replacement = current - 1
            _set_path(attacked, path, replacement)
            projected = core.reported_phase_energy_token_values(
                [attacked, artifacts[1]]
            )
            with self.subTest(mutation_path=path):
                self.assertTrue(
                    all(projected[token] == core.STOP_FILL for token in alpha_tokens)
                )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / "alpha-source.json"
            output_path = root / "alpha-artifact.json"
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
