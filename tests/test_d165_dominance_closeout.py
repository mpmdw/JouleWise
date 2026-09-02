"""D-165 dominance close-out core and artifact-contract tests."""

from __future__ import annotations

import ast
import copy
import functools
import hashlib
import io
import inspect
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import CodeType, SimpleNamespace
from unittest import mock

from configs.campaigns.d117_contrast_v5 import generate_configs as generator
from joulewise.analysis_manifest_v3 import (
    AnalysisManifestFinalizationError,
    calculate_manifest_id,
    finalize_prospective_analysis_manifest_v3,
)
from joulewise import detection_floor as detection_floor_module
from joulewise import dominance_closeout as core
from joulewise.detection_floor import (
    _common_mode_block_half_width as detection_floor_block_half_width,
)
from joulewise.floor_extraction import (
    _CommonModeBlockInputs,
    _common_mode_block_half_width,
)
from scripts import build_d165_dominance_closeout as cli_module
from scripts import mint_floor_artifact_generalized as generalized_mint
from scripts.build_d165_dominance_closeout import (
    build_d165_dominance_closeout,
)
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
from tests.test_d117_contrast_v5_pack import (
    PINNED_DOMINANCE_CRITERION_BYTES,
    frozen_json_bytes,
)
from tests.test_mint_floor_artifact_generalized import (
    _mixed_common_mode_seams,
    freeze_mixed_estimator_v2_pinset,
)
from joulewise.identity_pins import build_stack_identity, stack_identity_sha256


ROOT = Path(__file__).resolve().parents[1]
REAL_BLOCK_FIXTURE = ROOT / "tests/fixtures/fcm_r4_real_blocks/measured_pair.json"
def authenticated_bracket(operative_bound_s: float) -> dict:
    allowance_s = 0.010818
    return {
        "status": "passed",
        "endpoint_max_b_fiducial_s": operative_bound_s - allowance_s,
        "calibration_drift_allowance_s": allowance_s,
        "b_fiducial_s": operative_bound_s,
        "acceptance": {
            "allowance": {
                "rule": "max(observed_drift_s,bracket_screen_s)",
                "value_s": str(allowance_s),
                "embedding_count": 1,
                "embedded_in": "b_fiducial_s",
            }
        },
    }


def _file_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def mutate_then_encode(source_bytes: bytes, mutator) -> bytes:
    """Decode, mutate, and canonical-file encode one JSON source."""

    value = json.loads(source_bytes.decode("utf-8"))
    mutator(value)
    return _file_json_bytes(value)


def _reseal_test_sources(
    manifest: dict, floor: dict, sidecar: dict
) -> tuple[bytes, bytes, bytes]:
    """Reseal explicitly mutated test sources derived from a real finalization."""

    floor_bytes = _file_json_bytes(floor)
    sidecar_bytes = _file_json_bytes(sidecar)
    evidence = manifest["evidence"]
    evidence["aggregate_floor_artifact"]["sha256"] = hashlib.sha256(
        floor_bytes
    ).hexdigest()
    evidence["dominance_replay_sidecar"]["sha256"] = hashlib.sha256(
        sidecar_bytes
    ).hexdigest()
    evidence["dominance_replay_sidecar"]["schema_version"] = sidecar[
        "schema_version"
    ]
    evidence["dominance_replay_sidecar"]["sidecar_id"] = sidecar["sidecar_id"]
    manifest["manifest_id"] = calculate_manifest_id(manifest)
    return _file_json_bytes(manifest), floor_bytes, sidecar_bytes


def independent_from_component(component: dict, parent_key: str) -> dict:
    point = core._point_unguarded_floor_from_component(
        component, parent_key=parent_key
    )
    return core._build_independent_record(
        point_unguarded_floor_j=point,
        corner_widened_unguarded_floor_j=component[
            "corner_widened_unguarded_floor_j"
        ],
    )


def fixture_replay_inputs(
    block_ids: list[str] | None = None,
    block_deltas_j: list[float] | None = None,
    block_members: list[dict[str, str]] | None = None,
    residual_width_scale: float = 1.0,
) -> tuple[list[dict], dict, float, dict]:
    fixture = json.loads(REAL_BLOCK_FIXTURE.read_text(encoding="utf-8"))
    bound = float(fixture["operative_bound_s"])
    bracket = authenticated_bracket(bound)
    source_block_ids = []
    source_block_deltas_j = []
    source_block_members = []
    source_block_inputs = []
    for source in fixture["blocks"]:
        source_block_ids.append(source["block_id"])
        source_block_deltas_j.append(source["delta_j"])
        source_block_members.append(
            {row["position"]: row["bundle_id"] for row in source["members"]}
        )
        source_block_inputs.append(
            _CommonModeBlockInputs(
                onset_values_j=tuple(source["onset_sweep_j"]),
                offset_values_j=tuple(source["offset_sweep_j"]),
                zero_point_contrast_j=source["zero_point_contrast_j"],
                bundle_residual_half_widths_j=tuple(
                    source["bundle_residual_half_widths_j"]
                ),
                member_window_bounds_s=tuple(
                    tuple(window) for window in source["member_window_bounds_s"]
                ),
                member_envelope_integral_sum_j=source[
                    "member_envelope_integral_sum_j"
                ],
            )
        )
    if block_ids is None:
        selected_ids = source_block_ids
        selected_deltas = source_block_deltas_j
        selected_members = source_block_members
    else:
        selected_ids = block_ids
        selected_deltas = block_deltas_j or [
            source_block_deltas_j[index % len(source_block_deltas_j)]
            for index in range(len(selected_ids))
        ]
        selected_members = block_members or [
            source_block_members[index % len(source_block_members)]
            for index in range(len(selected_ids))
        ]
    selected_inputs = []
    for index, delta_j in enumerate(selected_deltas):
        source = source_block_inputs[index % len(source_block_inputs)]
        shift = delta_j - source.zero_point_contrast_j
        selected_inputs.append(
            _CommonModeBlockInputs(
                onset_values_j=tuple(value + shift for value in source.onset_values_j),
                offset_values_j=tuple(value + shift for value in source.offset_values_j),
                zero_point_contrast_j=delta_j,
                bundle_residual_half_widths_j=tuple(
                    value * residual_width_scale
                    for value in source.bundle_residual_half_widths_j
                ),
                member_window_bounds_s=source.member_window_bounds_s,
                member_envelope_integral_sum_j=source.member_envelope_integral_sum_j,
            )
        )
    blocks = core.d165_replay_blocks_from_mint_inputs(
        selected_ids, selected_deltas, selected_inputs, selected_members
    )
    raw_blocks = [core._raw_replay_block(block) for block in blocks]
    result = core.replay_common_mode_dominance(
        raw_blocks,
        calibration_bracket=bracket,
        shared_edge_bound_s=bound,
    )
    return blocks, bracket, bound, result


def replay_sidecar(
    floor: dict,
    *,
    default_cell_ids: frozenset[str] = frozenset(),
    residual_width_scale: float = 20.0,
) -> dict:
    cells = []
    for floor_cell in floor["cells"]:
        comparative = {
            "independent": independent_from_component(
                floor_cell["comparative"], "max_abs_delta_j"
            ),
            "estimator": "default",
        }
        if floor_cell["cell_id"] not in default_cell_ids:
            floor_blocks = floor_cell["comparative"]["blocks"]
            block_ids = [block["block_id"] for block in floor_blocks]
            block_deltas = [block["delta_j"] for block in floor_blocks]
            block_members = [
                {row["position"]: row["bundle_id"] for row in block["members"]}
                for block in floor_blocks
            ]
            blocks, bracket, bound, result = fixture_replay_inputs(
                block_ids,
                block_deltas,
                block_members,
                residual_width_scale,
            )
            comparative = {
                "independent": comparative["independent"],
                "estimator": "common_mode",
                "common_mode_replay": {
                    "inputs": {
                        "calibration_bracket": copy.deepcopy(bracket),
                        "calibration_bracket_sha256": (
                            core.canonical_json_sha256(bracket)
                        ),
                        "shared_edge_bound_s": bound,
                        "blocks": copy.deepcopy(blocks),
                    },
                    "result": copy.deepcopy(result),
                },
            }
        cells.append(
            {
                "cell_id": floor_cell["cell_id"],
                "absolute": {
                    "independent": independent_from_component(
                        floor_cell["absolute"], "max_abs_residual_j"
                    ),
                    "common_mode": {
                        "status": "not_applicable",
                        "reason": core.ABSOLUTE_COMMON_MODE_REASON,
                    },
                },
                "comparative": comparative,
            }
        )
    return {
        "schema_version": core.REPLAY_SCHEMA_VERSION,
        "sidecar_id": "d165-test-replay",
        "cells": cells,
    }


def builder_recomputations(
    floor: dict,
    sidecar: dict,
    *,
    default_cell_ids: frozenset[str] = frozenset(),
) -> dict[str, SimpleNamespace]:
    sidecar_cells = {cell["cell_id"]: cell for cell in sidecar["cells"]}
    result: dict[str, SimpleNamespace] = {}
    for floor_cell in floor["cells"]:
        cell_id = floor_cell["cell_id"]
        replay = sidecar_cells[cell_id]["comparative"].get(
            "common_mode_replay"
        )
        if cell_id in default_cell_ids:
            result[cell_id] = SimpleNamespace(
                estimator_path="default",
                comparative_blocks=tuple(
                    copy.deepcopy(floor_cell["comparative"]["blocks"])
                ),
            )
            continue
        inputs = tuple(
            _CommonModeBlockInputs(
                onset_values_j=tuple(block["onset_sweep_j"]),
                offset_values_j=tuple(block["offset_sweep_j"]),
                zero_point_contrast_j=block["zero_point_contrast_j"],
                bundle_residual_half_widths_j=tuple(
                    block["bundle_residual_half_widths_j"]
                ),
                member_window_bounds_s=tuple(
                    tuple(window) for window in block["member_window_bounds_s"]
                ),
                member_envelope_integral_sum_j=(
                    block["member_envelope_integral_sum_j"]
                ),
            )
            for block in replay["inputs"]["blocks"]
        )
        result[cell_id] = SimpleNamespace(
            estimator_path="common_mode",
            comparative_blocks=tuple(
                copy.deepcopy(floor_cell["comparative"]["blocks"])
            ),
            block_inputs=inputs,
            calibration_bracket=copy.deepcopy(
                replay["inputs"]["calibration_bracket"]
            ),
            shared_edge_bound_s=replay["inputs"]["shared_edge_bound_s"],
        )
    return result


def _recompute_sidecar_cell_result(sidecar: dict, cell_index: int = 0) -> None:
    replay = sidecar["cells"][cell_index]["comparative"]["common_mode_replay"]
    inputs = replay["inputs"]
    replay["result"] = core.replay_common_mode_dominance(
        [core._raw_replay_block(block) for block in inputs["blocks"]],
        calibration_bracket=inputs["calibration_bracket"],
        shared_edge_bound_s=inputs["shared_edge_bound_s"],
    )


@functools.cache
def _production_sources() -> tuple[dict, dict, dict]:
    """Finalize a dominance-enabled fixture with a real sealed sidecar."""

    with tempfile.TemporaryDirectory() as temporary:
        fixture = install_synthetic_finalization_fixture(
            Path(temporary),
            dominance_criterion=generator.dominance_criterion_registration(),
        )
        floor = json.loads(fixture["floor_path"].read_bytes())
        sidecar = replay_sidecar(floor)
        sidecar_path = fixture["root"] / "dominance_replay_sidecar.json"
        sidecar_path.write_bytes(_file_json_bytes(sidecar))
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
            dominance_replay_sidecar_path=sidecar_path,
        )
        return manifest, floor, sidecar


def finalized_manifest() -> dict:
    return copy.deepcopy(_production_sources()[0])


def floor_artifact() -> dict:
    return copy.deepcopy(_production_sources()[1])



def _compiled_string_constants(code: CodeType):
    """Yield string constants recursively from one compiled module."""

    for constant in code.co_consts:
        if isinstance(constant, str):
            yield constant
        elif isinstance(constant, CodeType):
            yield from _compiled_string_constants(constant)


class D165DominanceCloseoutTests(unittest.TestCase):
    maxDiff = None

    @staticmethod
    def set_neither_branch(closeout: dict, reason: str) -> None:
        closeout.update(
            {
                "all_independent_pass": None,
                "all_required_common_mode_pass": None,
                "branch": None,
                "dominance_sentence_licensed": False,
                "subtitle_licensed": False,
                "refusal_reason": reason,
            }
        )

    def build(self, floor: dict | None = None) -> tuple[dict, dict, dict, dict]:
        floor = floor_artifact() if floor is None else floor
        manifest = finalized_manifest()
        sidecar = replay_sidecar(floor)
        manifest_bytes, floor_bytes, sidecar_bytes = _reseal_test_sources(
            manifest, floor, sidecar
        )
        closeout = build_d165_dominance_closeout(
            manifest_bytes,
            floor_bytes,
            sidecar_bytes,
        )
        return closeout, manifest, floor, sidecar

    def assert_valid_closeout(
        self, closeout: dict, manifest: dict, floor: dict, sidecar: dict
    ) -> None:
        self.assertEqual(
            core.validate_d165_closeout(
                closeout,
                finalized_manifest_bytes=_file_json_bytes(manifest),
                floor_artifact_bytes=_file_json_bytes(floor),
                replay_sidecar_bytes=_file_json_bytes(sidecar),
            ),
            [],
        )

    def test_census_is_eight_ordinary_plus_four_comparative_common_mode(self) -> None:
        closeout, manifest, floor, sidecar = self.build()
        self.assertEqual(len(closeout["independent_ratios"]), 8)
        self.assertEqual(len(closeout["comparative_common_mode_ratios"]), 4)
        self.assertEqual(
            {record["component"] for record in closeout["independent_ratios"]},
            {"absolute", "comparative"},
        )
        self.assert_valid_closeout(closeout, manifest, floor, sidecar)

        malformed = copy.deepcopy(closeout)
        malformed["independent_ratios"].pop()
        self.assertTrue(
            any(
                "exactly eight" in error
                for error in core.validate_d165_closeout(
                    malformed,
                    finalized_manifest_bytes=_file_json_bytes(manifest),
                    floor_artifact_bytes=_file_json_bytes(floor),
                    replay_sidecar_bytes=_file_json_bytes(sidecar),
                )
            )
        )

    def test_terra_relabel_all_cells_to_forged_ids_refuses_neither_branch(self) -> None:
        closeout, manifest, floor, sidecar = self.build()
        forged_ids = ("forged-a", "forged-b", "forged-c", "forged-d")
        cell_ids = tuple(cell["cell_id"] for cell in floor["cells"])
        mapping = dict(zip(cell_ids, forged_ids, strict=True))
        for record in closeout["independent_ratios"]:
            record["cell_id"] = mapping[record["cell_id"]]
        for record in closeout["comparative_common_mode_ratios"]:
            record["cell_id"] = mapping[record["cell_id"]]
        reason = (
            "closeout.independent_ratios.cell_id: unknown 'forged-a' "
            "for component 'absolute'"
        )
        self.set_neither_branch(closeout, reason)

        errors = core.validate_d165_closeout(
            closeout,
            finalized_manifest_bytes=_file_json_bytes(manifest),
            floor_artifact_bytes=_file_json_bytes(floor),
            replay_sidecar_bytes=_file_json_bytes(sidecar),
        )
        self.assertIn(reason, errors)
        self.assertIsNone(closeout["branch"])
        self.assertFalse(closeout["dominance_sentence_licensed"])
        self.assertFalse(closeout["subtitle_licensed"])

    def test_luna_replace_first_cell_id_with_forged_cell_refuses(self) -> None:
        closeout, manifest, floor, sidecar = self.build()
        cell_ids = tuple(cell["cell_id"] for cell in floor["cells"])
        closeout["independent_ratios"][0]["cell_id"] = "forged-cell"
        reason = (
            "closeout.independent_ratios.cell_id: unknown 'forged-cell' "
            "for component 'absolute'"
        )
        self.set_neither_branch(closeout, reason)

        errors = core.validate_d165_closeout(
            closeout,
            finalized_manifest_bytes=_file_json_bytes(manifest),
            floor_artifact_bytes=_file_json_bytes(floor),
            replay_sidecar_bytes=_file_json_bytes(sidecar),
        )
        self.assertIn(reason, errors)
        self.assertIn(
            "closeout.independent_ratios.cell_id: missing "
            f"{cell_ids[0]!r} for component 'absolute'",
            errors,
        )
        self.assertIsNone(closeout["branch"])
        self.assertFalse(closeout["dominance_sentence_licensed"])
        self.assertFalse(closeout["subtitle_licensed"])

    def test_ratio_equal_to_two_passes(self) -> None:
        floor = floor_artifact()
        component = floor["cells"][0]["absolute"]
        point = core._point_unguarded_floor_from_component(
            component, parent_key="max_abs_residual_j"
        )
        component["corner_widened_unguarded_floor_j"] = 2.0 * point
        closeout, manifest, floor, sidecar = self.build(floor)
        record = closeout["independent_ratios"][0]
        self.assertEqual(record["ratio"], 2.0)
        self.assertTrue(record["passes"])
        self.assert_valid_closeout(closeout, manifest, floor, sidecar)

    def test_zero_denominator_refuses_with_named_reason(self) -> None:
        floor = floor_artifact()
        floor["cells"][0]["absolute"]["max_abs_residual_j"] = 0.0
        floor["cells"][0]["absolute"]["prediction_component_j"] = 0.0
        closeout, manifest, floor, sidecar = self.build(floor)
        record = closeout["independent_ratios"][0]
        self.assertEqual(record["status"], "refused")
        self.assertEqual(
            record["refusal_reason"], core.DOMINANCE_ZERO_DENOMINATOR_REASON
        )
        self.assertIsNone(closeout["branch"])
        self.assertEqual(
            closeout["refusal_reason"], core.DOMINANCE_ZERO_DENOMINATOR_REASON
        )
        self.assert_valid_closeout(closeout, manifest, floor, sidecar)

    def test_missing_sidecar_cell_stops_with_neither_branch(self) -> None:
        floor = floor_artifact()
        manifest = finalized_manifest()
        sidecar = replay_sidecar(floor)
        missing_id = sidecar["cells"].pop()["cell_id"]
        manifest_bytes, floor_bytes, sidecar_bytes = _reseal_test_sources(
            manifest, floor, sidecar
        )
        closeout = build_d165_dominance_closeout(
            manifest_bytes,
            floor_bytes,
            sidecar_bytes,
        )
        self.assertIsNone(closeout["branch"])
        self.assertFalse(closeout["dominance_sentence_licensed"])
        missing = [
            record
            for record in closeout["comparative_common_mode_ratios"]
            if record["cell_id"] == missing_id
        ]
        self.assertEqual(missing[0]["status"], "refused")
        self.assertIn("cell census", closeout["refusal_reason"])
        self.assert_valid_closeout(closeout, manifest, floor, sidecar)

    def test_source_hash_mutation_refuses_validation(self) -> None:
        closeout, manifest, floor, sidecar = self.build()
        manifest_bytes = _file_json_bytes(manifest)
        floor_bytes = _file_json_bytes(floor)
        sidecar_bytes = _file_json_bytes(sidecar)

        def mutate_floor(value: dict) -> None:
            value["cells"][0]["absolute"][
                "corner_widened_unguarded_floor_j"
            ] = 2.1

        mutated_floor_bytes = mutate_then_encode(floor_bytes, mutate_floor)
        errors = core.validate_d165_closeout(
            closeout,
            finalized_manifest_bytes=manifest_bytes,
            floor_artifact_bytes=mutated_floor_bytes,
            replay_sidecar_bytes=sidecar_bytes,
        )
        self.assertIn(core.FLOOR_ARTIFACT_SOURCE_HASH_MISMATCH, errors)

        edited_manifest_bytes = mutate_then_encode(
            manifest_bytes,
            lambda value: value["evidence"]["dominance_replay_sidecar"].update(
                {"path": "moved-sidecar.json"}
            ),
        )
        errors = core.validate_d165_closeout(
            closeout,
            finalized_manifest_bytes=edited_manifest_bytes,
            floor_artifact_bytes=floor_bytes,
            replay_sidecar_bytes=sidecar_bytes,
        )
        self.assertIn(
            "closeout.finalized_manifest_sha256: source-byte-hash mismatch", errors
        )

    def test_floor_bytes_must_match_the_artifact_digest_sealed_by_manifest(self) -> None:
        _, manifest, floor, sidecar = self.build()
        manifest_bytes = _file_json_bytes(manifest)
        floor_bytes = _file_json_bytes(floor)
        sidecar_bytes = _file_json_bytes(sidecar)
        reminted_floor_bytes = mutate_then_encode(
            floor_bytes,
            lambda value: value["cells"][0]["absolute"].update(
                {"corner_widened_unguarded_floor_j": 2.1}
            ),
        )
        closeout = build_d165_dominance_closeout(
            manifest_bytes, reminted_floor_bytes, sidecar_bytes
        )
        self.assertEqual(
            closeout["refusal_reason"],
            core.FLOOR_ARTIFACT_SOURCE_HASH_MISMATCH,
        )
        self.assertIsNone(closeout["branch"])
        self.assertFalse(closeout["dominance_sentence_licensed"])
        self.assertFalse(closeout["subtitle_licensed"])
        self.assertEqual(
            core.validate_d165_closeout(
                closeout,
                finalized_manifest_bytes=manifest_bytes,
                floor_artifact_bytes=reminted_floor_bytes,
                replay_sidecar_bytes=sidecar_bytes,
            ),
            [],
        )

    def test_worked_sidecar_digest_matches_contract_literal(self) -> None:
        sidecar_bytes = _file_json_bytes(replay_sidecar(floor_artifact()))
        self.assertEqual(
            hashlib.sha256(sidecar_bytes).hexdigest(),
            "69ac25694cb5d8f8cf7645c844b2eab3c769ba82748802a3291fcae950440735",
        )

    def test_stage2_builder_uses_floor_identity_and_default_shape(self) -> None:
        floor = floor_artifact()
        default_id = floor["cells"][0]["cell_id"]
        source_sidecar = replay_sidecar(
            floor, default_cell_ids=frozenset({default_id})
        )
        built = core.build_d165_replay_sidecar(
            floor,
            builder_recomputations(
                floor,
                source_sidecar,
                default_cell_ids=frozenset({default_id}),
            ),
        )
        self.assertEqual(
            built["sidecar_id"], f"{floor['artifact_id']}::d165-replay"
        )
        self.assertNotIn("lineage", built)
        default_comparative = built["cells"][0]["comparative"]
        self.assertEqual(set(default_comparative), {"independent", "estimator"})
        self.assertEqual(default_comparative["estimator"], "default")
        self.assertNotIn("common_mode_replay", default_comparative)
        malformed_floor = copy.deepcopy(floor)
        del malformed_floor["artifact_id"]
        with self.assertRaisesRegex(ValueError, r"^closeout_input_malformed$"):
            core.build_d165_replay_sidecar(
                malformed_floor,
                builder_recomputations(
                    floor,
                    source_sidecar,
                    default_cell_ids=frozenset({default_id}),
                ),
            )

    def test_stage2_sidecar_ownership_ast_census(self) -> None:
        reference_sites = {
            ROOT / "joulewise" / "dominance_closeout.py": "owner",
            ROOT / "joulewise" / "floor_mint_estimator.py": "adapter-consumer",
            ROOT / "scripts" / "mint_floor_artifact_generalized.py": "mint-consumer",
            ROOT / "joulewise" / "analysis_manifest_v3.py": "manifest-consumer",
        }
        owner = ROOT / "joulewise" / "dominance_closeout.py"
        production = sorted(
            set((ROOT / "joulewise").rglob("*.py"))
            | set((ROOT / "scripts").rglob("*.py"))
        )
        schema_literal = "joulewise.d165_dominance_replay.v1"
        record_literal_paths: list[Path] = []
        owner_code = compile(owner.read_text(encoding="utf-8"), str(owner), "exec")
        self.assertIn(schema_literal, set(_compiled_string_constants(owner_code)))
        for path in production:
            if path == owner:
                continue
            code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
            self.assertNotIn(
                schema_literal,
                set(_compiled_string_constants(code)),
                str(path.relative_to(ROOT)),
            )

        reference_paths: dict[str, set[Path]] = {
            "d165_replay_blocks_from_mint_inputs": set(),
            "build_d165_replay_sidecar": set(),
        }
        for path in production:
            tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    keys = {
                        key.value
                        for key in node.keys
                        if isinstance(key, ast.Constant) and isinstance(key.value, str)
                    }
                    if {
                        "block_id",
                        "members",
                        "delta_j",
                        "onset_sweep_j",
                        "offset_sweep_j",
                        "zero_point_contrast_j",
                        "bundle_residual_half_widths_j",
                        "member_window_bounds_s",
                        "member_envelope_integral_sum_j",
                    } <= keys:
                        record_literal_paths.append(path)
                if path not in reference_sites:
                    continue
                if isinstance(node, ast.Name) and node.id in reference_paths:
                    reference_paths[node.id].add(path)
                if isinstance(node, ast.Attribute) and node.attr in reference_paths:
                    reference_paths[node.attr].add(path)
        self.assertEqual(
            record_literal_paths, [owner]
        )
        for name, paths in reference_paths.items():
            self.assertTrue(paths <= {
                ROOT / "joulewise" / "dominance_closeout.py",
                ROOT / "joulewise" / "floor_mint_estimator.py",
                ROOT / "scripts" / "mint_floor_artifact_generalized.py",
            }, name)
        self.assertIn(
            ROOT / "scripts" / "mint_floor_artifact_generalized.py",
            reference_paths["build_d165_replay_sidecar"],
        )

    def test_dominance_finalization_requires_sidecar(self) -> None:
        """A criterion-enabled prospective pack cannot finalize without it."""

        with tempfile.TemporaryDirectory() as temporary:
            fixture = install_synthetic_finalization_fixture(
                Path(temporary),
                dominance_criterion=generator.dominance_criterion_registration(),
            )
            with self.assertRaises(AnalysisManifestFinalizationError) as raised:
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
            "analysis_finalization_attachment_missing",
        )

    def test_builder_floor_cells_not_list_raises_input_malformed(self) -> None:
        """build_d165_dominance_closeout stops on a non-list floor census."""

        _, manifest, floor, sidecar = self.build()
        floor["cells"] = {"not": "a list"}
        manifest_bytes, floor_bytes, sidecar_bytes = _reseal_test_sources(
            manifest, floor, sidecar
        )
        with self.assertRaisesRegex(ValueError, r"^closeout_input_malformed$"):
            build_d165_dominance_closeout(
                manifest_bytes,
                floor_bytes,
                sidecar_bytes,
            )

    def test_builder_manifest_id_precedes_malformed_floor_stop(self) -> None:
        """build_d165_dominance_closeout surfaces its first source precondition."""

        _, manifest, floor, sidecar = self.build()
        floor["cells"] = {"not": "a list"}
        _, floor_bytes, sidecar_bytes = _reseal_test_sources(
            manifest, floor, sidecar
        )
        manifest["manifest_id"] = "forged-manifest-id"
        with self.assertRaises(ValueError) as raised:
            build_d165_dominance_closeout(
                _file_json_bytes(manifest),
                floor_bytes,
                sidecar_bytes,
            )
        self.assertEqual(str(raised.exception), "finalized_manifest_id_mismatch")

    def test_builder_arms_not_list_returns_named_refusal_artifact(self) -> None:
        """build_d165_dominance_closeout can truthfully build this refusal."""

        _, manifest, floor, sidecar = self.build()
        manifest["arms"] = {"not": "an arm array"}
        manifest["manifest_id"] = calculate_manifest_id(manifest)
        closeout = build_d165_dominance_closeout(
            _file_json_bytes(manifest),
            _file_json_bytes(floor),
            _file_json_bytes(sidecar),
        )
        self.assertEqual(closeout["refusal_reason"], "closeout_input_malformed")
        self.assertIsNone(closeout["branch"])

    def test_forged_sidecar_bytes_cannot_pair_with_closeout_built_from_other_bytes(
        self,
    ) -> None:
        closeout, manifest, floor, sidecar = self.build()
        manifest_bytes = _file_json_bytes(manifest)
        floor_bytes = _file_json_bytes(floor)
        sidecar_bytes = _file_json_bytes(sidecar)

        def forge_self_consistent_pair(value: dict) -> None:
            replay = value["cells"][0]["comparative"]["common_mode_replay"]
            block = replay["inputs"]["blocks"][0]
            block["delta_j"] *= 0.9
            for field in (
                "onset_sweep_j",
                "offset_sweep_j",
                "bundle_residual_half_widths_j",
            ):
                block[field] = [operand * 0.9 for operand in block[field]]
            block["zero_point_contrast_j"] *= 0.9
            block["member_envelope_integral_sum_j"] *= 0.9
            block["derived_split"] = core.split_common_mode_block_width(
                delta_j=block["delta_j"],
                onset_sweep_j=block["onset_sweep_j"],
                offset_sweep_j=block["offset_sweep_j"],
                zero_point_contrast_j=block["zero_point_contrast_j"],
                bundle_residual_half_widths_j=block[
                    "bundle_residual_half_widths_j"
                ],
                member_envelope_integral_sum_j=block[
                    "member_envelope_integral_sum_j"
                ],
            )
            inputs = replay["inputs"]
            replay["result"] = core.replay_common_mode_dominance(
                [core._raw_replay_block(item) for item in inputs["blocks"]],
                calibration_bracket=inputs["calibration_bracket"],
                shared_edge_bound_s=inputs["shared_edge_bound_s"],
            )

        forged_sidecar_bytes = mutate_then_encode(
            sidecar_bytes, forge_self_consistent_pair
        )
        self.assertEqual(
            core.validate_d165_replay_sidecar(
                json.loads(forged_sidecar_bytes.decode("utf-8"))
            ),
            [],
        )
        self.assertEqual(
            core.validate_d165_closeout(
                closeout,
                finalized_manifest_bytes=manifest_bytes,
                floor_artifact_bytes=floor_bytes,
                replay_sidecar_bytes=sidecar_bytes,
            ),
            [],
        )
        errors = core.validate_d165_closeout(
            closeout,
            finalized_manifest_bytes=manifest_bytes,
            floor_artifact_bytes=floor_bytes,
            replay_sidecar_bytes=forged_sidecar_bytes,
        )
        self.assertIn(
            "closeout.replay_sidecar_sha256: source-byte-hash mismatch", errors
        )

    def test_public_closeout_apis_expose_only_source_byte_channels(self) -> None:
        forbidden = {"finalized_manifest", "floor_artifact", "replay_sidecar"}
        for function in (
            build_d165_dominance_closeout,
            core.validate_d165_closeout,
        ):
            with self.subTest(function=function.__name__):
                parameters = inspect.signature(function).parameters
                self.assertTrue(
                    {
                        "finalized_manifest_bytes",
                        "floor_artifact_bytes",
                        "replay_sidecar_bytes",
                    }
                    <= set(parameters)
                )
                self.assertTrue(forbidden.isdisjoint(parameters))

    def test_manifest_id_tamper_refuses_before_closeout_licensing(self) -> None:
        _, manifest, floor, sidecar = self.build()
        malformed_manifest_bytes = mutate_then_encode(
            _file_json_bytes(manifest),
            lambda value: value["arms"][0].update({"model_tag": "tampered"}),
        )
        floor_bytes = _file_json_bytes(floor)
        sidecar_bytes = _file_json_bytes(sidecar)
        closeout = build_d165_dominance_closeout(
            malformed_manifest_bytes, floor_bytes, sidecar_bytes
        )
        self.assertEqual(
            closeout["refusal_reason"], "finalized_manifest_id_mismatch"
        )
        self.assertIsNone(closeout["branch"])
        self.assertFalse(closeout["dominance_sentence_licensed"])
        self.assertFalse(closeout["subtitle_licensed"])
        self.assertEqual(
            core.validate_d165_closeout(
                closeout,
                finalized_manifest_bytes=malformed_manifest_bytes,
                floor_artifact_bytes=floor_bytes,
                replay_sidecar_bytes=sidecar_bytes,
            ),
            [],
        )

    def test_source_preconditions_authenticate_manifest_before_other_fields(
        self,
    ) -> None:
        """_source_precondition_errors authenticates manifest_id before fields."""

        _, manifest, floor, sidecar = self.build()
        floor_bytes = _file_json_bytes(floor)
        sidecar_bytes = _file_json_bytes(sidecar)
        for field, value in (
            ("schema_version", "bogus.v0"),
            ("freeze_status", "draft"),
        ):
            with self.subTest(field=field):
                mutated_manifest = copy.deepcopy(manifest)
                mutated_manifest[field] = value
                mutated_manifest["manifest_id"] = "forged-manifest-id"
                errors = core._source_precondition_errors(
                    mutated_manifest,
                    floor,
                    sidecar,
                    floor_artifact_bytes=floor_bytes,
                    replay_sidecar_bytes=sidecar_bytes,
                )
                self.assertEqual(errors[0], "finalized_manifest_id_mismatch")

    def test_validate_catches_unhashable_closeout_census_as_named_neither(self) -> None:
        closeout, manifest, floor, sidecar = self.build()
        closeout["independent_ratios"][0]["component"] = []
        self.set_neither_branch(closeout, core.CLOSEOUT_INPUT_MALFORMED_RECORDS)
        self.assertEqual(
            closeout["refusal_reason"], core.CLOSEOUT_INPUT_MALFORMED_RECORDS
        )
        self.assertEqual(
            core.validate_d165_closeout(
                closeout,
                finalized_manifest_bytes=_file_json_bytes(manifest),
                floor_artifact_bytes=_file_json_bytes(floor),
                replay_sidecar_bytes=_file_json_bytes(sidecar),
            ),
            [],
        )

    def test_replay_sidecar_source_byte_hash_guard_is_isolated(self) -> None:
        closeout, manifest, floor, sidecar = self.build()
        closeout["replay_sidecar_sha256"] = "0" * 64
        errors = core.validate_d165_closeout(
            closeout,
            finalized_manifest_bytes=_file_json_bytes(manifest),
            floor_artifact_bytes=_file_json_bytes(floor),
            replay_sidecar_bytes=_file_json_bytes(sidecar),
        )
        self.assertIn(
            "closeout.replay_sidecar_sha256: source-byte-hash mismatch", errors
        )

    def test_each_partial_replay_attachment_refuses_as_manifest_lacks_sidecar(
        self,
    ) -> None:
        _, manifest, floor, sidecar = self.build()
        floor_bytes = _file_json_bytes(floor)
        sidecar_bytes = _file_json_bytes(sidecar)
        for missing_key in ("path", "sha256", "schema_version", "sidecar_id"):
            with self.subTest(missing_key=missing_key):
                partial = copy.deepcopy(manifest)
                partial["evidence"]["dominance_replay_sidecar"].pop(missing_key)
                partial["manifest_id"] = calculate_manifest_id(partial)
                partial_manifest_bytes = _file_json_bytes(partial)
                closeout = build_d165_dominance_closeout(
                    partial_manifest_bytes, floor_bytes, sidecar_bytes
                )
                self.assertEqual(
                    closeout["refusal_reason"], "manifest_lacks_replay_sidecar"
                )
                self.assertIsNone(closeout["branch"])

    def test_sidecar_attachment_schema_mismatch_has_identity_reason(self) -> None:
        _, manifest, floor, sidecar = self.build()
        manifest["evidence"]["dominance_replay_sidecar"][
            "schema_version"
        ] = "forged-schema"
        manifest["manifest_id"] = calculate_manifest_id(manifest)
        manifest_bytes = _file_json_bytes(manifest)
        closeout = build_d165_dominance_closeout(
            manifest_bytes, _file_json_bytes(floor), _file_json_bytes(sidecar)
        )
        self.assertEqual(
            closeout["refusal_reason"], "replay_sidecar_identity_mismatch"
        )
        self.assertIsNone(closeout["branch"])

    def test_validators_reject_missing_extra_and_nonfinite_fields(self) -> None:
        floor = floor_artifact()
        sidecar = replay_sidecar(floor)
        extra = copy.deepcopy(sidecar)
        extra["unexpected"] = True
        self.assertTrue(
            any("extra keys" in error for error in core.validate_d165_replay_sidecar(extra))
        )

        missing = copy.deepcopy(sidecar)
        del missing["cells"][0]["absolute"]["independent"]["ratio_id"]
        self.assertTrue(
            any(
                "missing keys" in error
                for error in core.validate_d165_replay_sidecar(missing)
            )
        )

        nonfinite = copy.deepcopy(sidecar)
        nonfinite["cells"][0]["comparative"]["common_mode_replay"]["result"][
            "ratio"
        ] = float("nan")
        self.assertTrue(
            any(
                "finite" in error
                for error in core.validate_d165_replay_sidecar(nonfinite)
            )
        )

    def test_default_estimator_cannot_carry_common_mode_replay(self) -> None:
        sidecar = replay_sidecar(floor_artifact())
        sidecar["cells"][0]["comparative"]["estimator"] = "default"
        self.assertEqual(
            core.validate_d165_replay_sidecar(sidecar),
            [
                "sidecar.cells[0].comparative.estimator: must be 'common_mode' "
                "when common_mode_replay is present"
            ],
        )

    def test_replay_sidecar_guard_matrix_trips_one_named_guard_per_case(self) -> None:
        base = replay_sidecar(floor_artifact())
        cases: list[tuple[str, dict, str]] = []

        schema = copy.deepcopy(base)
        schema["schema_version"] = "forged-schema"
        cases.append(
            (
                "schema authentication",
                schema,
                "sidecar.schema_version: must be " f"{core.REPLAY_SCHEMA_VERSION!r}",
            )
        )
        identity = copy.deepcopy(base)
        identity["sidecar_id"] = ""
        cases.append(
            (
                "identity authentication",
                identity,
                "sidecar.sidecar_id: must be a nonempty string",
            )
        )
        duplicate_cell = copy.deepcopy(base)
        duplicate_cell["cells"][1]["cell_id"] = duplicate_cell["cells"][0][
            "cell_id"
        ]
        duplicate_cell_id = duplicate_cell["cells"][0]["cell_id"]
        cases.append(
            (
                "cell census",
                duplicate_cell,
                f"sidecar.cells[1].cell_id: duplicate {duplicate_cell_id!r}",
            )
        )
        absolute_common = copy.deepcopy(base)
        absolute_common["cells"][0]["absolute"]["common_mode"][
            "status"
        ] = "complete"
        cases.append(
            (
                "absolute cancellation license",
                absolute_common,
                "sidecar.cells[0].absolute.common_mode: must be the registered "
                "not_applicable record",
            )
        )
        bracket_digest = copy.deepcopy(base)
        bracket_digest["cells"][0]["comparative"]["common_mode_replay"][
            "inputs"
        ]["calibration_bracket_sha256"] = "0" * 64
        cases.append(
            (
                "bracket authentication",
                bracket_digest,
                "sidecar.cells[0].comparative.common_mode_replay.inputs."
                "calibration_bracket_sha256: source-hash mismatch",
            )
        )
        bound = copy.deepcopy(base)
        bound["cells"][0]["comparative"]["common_mode_replay"]["inputs"][
            "shared_edge_bound_s"
        ] *= 0.5
        cases.append(
            (
                "operative bound authentication",
                bound,
                "sidecar.cells[0].comparative.common_mode_replay.inputs: "
                "unauthenticated or invalid replay "
                "(common_mode_replay_authenticated_operative_bound_invalid)",
            )
        )
        too_many = copy.deepcopy(base)
        source_block = too_many["cells"][0]["comparative"][
            "common_mode_replay"
        ]["inputs"]["blocks"][0]
        too_many["cells"][0]["comparative"]["common_mode_replay"]["inputs"][
            "blocks"
        ] = [
            {**copy.deepcopy(source_block), "block_id": f"block-{index}"}
            for index in range(17)
        ]
        cases.append(
            (
                "exact corner cap",
                too_many,
                "sidecar.cells[0].comparative.common_mode_replay.inputs.blocks: "
                "count must be 1..16",
            )
        )
        duplicate_block = copy.deepcopy(base)
        blocks = duplicate_block["cells"][0]["comparative"][
            "common_mode_replay"
        ]["inputs"]["blocks"]
        blocks[1]["block_id"] = blocks[0]["block_id"]
        duplicate_block_id = blocks[0]["block_id"]
        cases.append(
            (
                "block census",
                duplicate_block,
                "sidecar.cells[0].comparative.common_mode_replay.inputs."
                f"blocks[1].block_id: duplicate {duplicate_block_id!r}",
            )
        )
        split = copy.deepcopy(base)
        split["cells"][0]["comparative"]["common_mode_replay"]["inputs"][
            "blocks"
        ][0]["derived_split"]["shared_width_j"] += 1.0
        cases.append(
            (
                "split arithmetic",
                split,
                "sidecar.cells[0].comparative.common_mode_replay.inputs."
                "blocks[0].derived_split: does not match "
                "split_common_mode_block_width",
            )
        )
        independent = copy.deepcopy(base)
        independent["cells"][0]["absolute"]["independent"]["ratio"] += 1.0
        cases.append(
            (
                "ordinary arithmetic",
                independent,
                "sidecar.cells[0].absolute.independent: does not match "
                "dominance_ratio",
            )
        )
        result = copy.deepcopy(base)
        result["cells"][0]["comparative"]["common_mode_replay"]["result"][
            "ratio"
        ] += 1.0
        cases.append(
            (
                "replay arithmetic",
                result,
                "sidecar.cells[0].comparative.common_mode_replay.result: "
                "does not match replay_common_mode_dominance",
            )
        )

        for guard, artifact, expected in cases:
            with self.subTest(guard=guard):
                self.assertEqual(core.validate_d165_replay_sidecar(artifact), [expected])

    def test_closeout_guard_matrix_trips_one_named_guard_per_case(self) -> None:
        closeout, manifest, floor, sidecar = self.build()
        cases: list[tuple[str, dict, str]] = []

        schema = copy.deepcopy(closeout)
        schema["schema_version"] = "forged-schema"
        schema_reason = (
            "closeout.schema_version: must be " f"{core.CLOSEOUT_SCHEMA_VERSION!r}"
        )
        self.set_neither_branch(schema, schema_reason)
        cases.append(("schema authentication", schema, schema_reason))

        source_hash = copy.deepcopy(closeout)
        source_hash["sources"]["floor_artifact"][
            "canonical_json_sha256"
        ] = "0" * 64
        source_hash_reason = "closeout.sources.floor_artifact: source-hash mismatch"
        self.set_neither_branch(source_hash, source_hash_reason)
        cases.append(("source authentication", source_hash, source_hash_reason))

        operand = copy.deepcopy(closeout)
        ordinary = operand["independent_ratios"][0]
        ordinary.update(
            core._build_independent_record(
                point_unguarded_floor_j=ordinary["point_unguarded_floor_j"],
                corner_widened_unguarded_floor_j=(
                    ordinary["corner_widened_unguarded_floor_j"] + 1.0
                ),
            )
        )
        operand_reason = (
            "closeout.independent_ratios["
            f"{(ordinary['cell_id'], ordinary['component'])!r}]: "
            "source operand mismatch"
        )
        self.set_neither_branch(operand, operand_reason)
        cases.append(("source operand arithmetic", operand, operand_reason))

        common_result = copy.deepcopy(closeout)
        common = common_result["comparative_common_mode_ratios"][0]
        common_corner = common["common_mode_corner_widened_unguarded_floor_j"] + 1.0
        common["common_mode_corner_widened_unguarded_floor_j"] = common_corner
        common.update(
            core.dominance_ratio(
                corner_widened_unguarded_floor_j=common_corner,
                point_unguarded_floor_j=common["point_unguarded_floor_j"],
            )
        )
        common_reason = (
            "closeout.comparative_common_mode_ratios"
            f"[{common['cell_id']!r}]: source result mismatch"
        )
        self.set_neither_branch(common_result, common_reason)
        cases.append(("source result arithmetic", common_result, common_reason))

        license_record = copy.deepcopy(closeout)
        license_record["dominance_sentence_licensed"] = not closeout[
            "dominance_sentence_licensed"
        ]
        license_reason = (
            "closeout.dominance_sentence_licensed: does not match branch rule"
        )
        cases.append(("branch license", license_record, license_reason))

        for guard, artifact, expected in cases:
            with self.subTest(guard=guard):
                self.assertEqual(
                    core.validate_d165_closeout(
                        artifact,
                        finalized_manifest_bytes=_file_json_bytes(manifest),
                        floor_artifact_bytes=_file_json_bytes(floor),
                        replay_sidecar_bytes=_file_json_bytes(sidecar),
                    ),
                    [expected],
                )

    def test_builder_structural_floor_guard_matrix_is_input_malformed(self) -> None:
        """build_d165_dominance_closeout stops on short or duplicate floors."""

        manifest = finalized_manifest()
        floor = floor_artifact()
        sidecar = replay_sidecar(floor)
        short_floor = copy.deepcopy(floor)
        short_floor["cells"].pop()
        duplicate_floor = copy.deepcopy(floor)
        duplicate_floor["cells"][1]["cell_id"] = duplicate_floor["cells"][0][
            "cell_id"
        ]
        for guard, floor_value in (
            ("three cells", short_floor),
            ("duplicate cell_id", duplicate_floor),
        ):
            with self.subTest(guard=guard):
                manifest_bytes, floor_bytes, sidecar_bytes = _reseal_test_sources(
                    copy.deepcopy(manifest), floor_value, copy.deepcopy(sidecar)
                )
                with self.assertRaisesRegex(
                    ValueError, r"^closeout_input_malformed$"
                ):
                    build_d165_dominance_closeout(
                        manifest_bytes,
                        floor_bytes,
                        sidecar_bytes,
                    )

    def test_builder_component_guards_use_first_source_precondition(self) -> None:
        """build_d165_dominance_closeout follows _source_precondition_errors."""

        manifest = finalized_manifest()
        floor = floor_artifact()
        sidecar = replay_sidecar(floor)
        missing_component = copy.deepcopy(floor)
        del missing_component["cells"][0]["absolute"]
        invalid_corner = copy.deepcopy(floor)
        invalid_corner["cells"][0]["absolute"][
            "corner_widened_unguarded_floor_j"
        ] = "forged"
        for guard, floor_value in (
            ("missing component", missing_component),
            ("invalid corner", invalid_corner),
        ):
            with self.subTest(guard=guard):
                manifest_for_case = copy.deepcopy(manifest)
                sidecar_for_case = copy.deepcopy(sidecar)
                manifest_bytes, floor_bytes, sidecar_bytes = _reseal_test_sources(
                    manifest_for_case, floor_value, sidecar_for_case
                )
                expected = core._source_precondition_errors(
                    manifest_for_case,
                    floor_value,
                    sidecar_for_case,
                    floor_artifact_bytes=floor_bytes,
                    replay_sidecar_bytes=sidecar_bytes,
                )[0]
                self.assertIn("cannot align with floor artifact", expected)
                with self.assertRaises(ValueError) as raised:
                    build_d165_dominance_closeout(
                        manifest_bytes,
                        floor_bytes,
                        sidecar_bytes,
                    )
                self.assertEqual(str(raised.exception), expected)

    def test_builder_schema_guards_use_named_source_precondition(self) -> None:
        """build_d165_dominance_closeout routes _source_reference failures."""

        manifest = finalized_manifest()
        floor = floor_artifact()
        sidecar = replay_sidecar(floor)
        wrong_manifest_schema = copy.deepcopy(manifest)
        wrong_manifest_schema["schema_version"] = "forged-schema"
        wrong_floor_schema = copy.deepcopy(floor)
        wrong_floor_schema["schema_version"] = "forged-schema"
        cases = (
            (
                "manifest schema",
                wrong_manifest_schema,
                floor,
                "finalized_manifest: schema is not finalized v3",
            ),
            (
                "floor schema",
                manifest,
                wrong_floor_schema,
                "floor_artifact: schema is not detection_floor_artifact.v2",
            ),
        )
        for guard, manifest_value, floor_value, expected in cases:
            with self.subTest(guard=guard):
                manifest_for_case = copy.deepcopy(manifest_value)
                sidecar_for_case = copy.deepcopy(sidecar)
                manifest_bytes, floor_bytes, sidecar_bytes = (
                    _reseal_test_sources(
                        manifest_for_case, floor_value, sidecar_for_case
                    )
                )
                with self.assertRaises(ValueError) as raised:
                    build_d165_dominance_closeout(
                        manifest_bytes,
                        floor_bytes,
                        sidecar_bytes,
                    )
                self.assertEqual(str(raised.exception), expected)

        attachment_cases: list[
            tuple[str, bytes, bytes, bytes, str]
        ] = []

        attached_manifest = copy.deepcopy(manifest)
        attached_manifest_bytes, floor_bytes, sidecar_bytes = (
            _reseal_test_sources(attached_manifest, floor, sidecar)
        )
        absent_manifest = json.loads(attached_manifest_bytes)
        absent_manifest["evidence"].pop("dominance_replay_sidecar")
        absent_manifest["manifest_id"] = calculate_manifest_id(absent_manifest)
        absent_manifest_bytes = _file_json_bytes(absent_manifest)
        attachment_cases.append(
            (
                "manifest attachment",
                absent_manifest_bytes,
                floor_bytes,
                sidecar_bytes,
                "manifest_lacks_replay_sidecar",
            )
        )

        digest_manifest = copy.deepcopy(manifest)
        digest_manifest_bytes, digest_floor_bytes, original_sidecar_bytes = (
            _reseal_test_sources(digest_manifest, floor, sidecar)
        )
        forged_sidecar = copy.deepcopy(sidecar)
        forged_sidecar["cells"][0]["absolute"]["independent"].update(
            core._build_independent_record(
                point_unguarded_floor_j=2.0,
                corner_widened_unguarded_floor_j=4.0,
            )
        )
        attachment_cases.append(
            (
                "sidecar digest",
                digest_manifest_bytes,
                digest_floor_bytes,
                _file_json_bytes(forged_sidecar),
                "replay_sidecar_digest_mismatch",
            )
        )
        self.assertNotEqual(
            _file_json_bytes(forged_sidecar), original_sidecar_bytes
        )

        identity_manifest = copy.deepcopy(manifest)
        identity_manifest_bytes, identity_floor_bytes, identity_sidecar_bytes = (
            _reseal_test_sources(identity_manifest, floor, sidecar)
        )
        identity_manifest_bytes = mutate_then_encode(
            identity_manifest_bytes,
            lambda value: (
                value["evidence"]["dominance_replay_sidecar"].update(
                    {"sidecar_id": "other-sidecar"}
                ),
                value.update({"manifest_id": calculate_manifest_id(value)}),
            ),
        )
        attachment_cases.append(
            (
                "sidecar identity",
                identity_manifest_bytes,
                identity_floor_bytes,
                identity_sidecar_bytes,
                "replay_sidecar_identity_mismatch",
            )
        )

        for (
            guard,
            manifest_bytes,
            floor_bytes,
            sidecar_bytes,
            expected,
        ) in attachment_cases:
            with self.subTest(guard=guard):
                closeout = build_d165_dominance_closeout(
                    manifest_bytes,
                    floor_bytes,
                    sidecar_bytes,
                )
                self.assertIsNone(closeout["branch"])
                self.assertFalse(closeout["dominance_sentence_licensed"])
                self.assertFalse(closeout["subtitle_licensed"])
                self.assertEqual(closeout["refusal_reason"], expected)
                self.assertEqual(
                    core.validate_d165_closeout(
                        closeout,
                        finalized_manifest_bytes=manifest_bytes,
                        floor_artifact_bytes=floor_bytes,
                        replay_sidecar_bytes=sidecar_bytes,
                    ),
                    [],
                )

    def test_floor_member_census_refuses_each_position_delta_and_count_mutation(
        self,
    ) -> None:
        manifest = finalized_manifest()
        floor = floor_artifact()
        sidecar = replay_sidecar(floor)

        def wrong_member(mutated_floor: dict, mutated_sidecar: dict) -> None:
            block = mutated_sidecar["cells"][0]["comparative"][
                "common_mode_replay"
            ]["inputs"]["blocks"][0]
            block["members"]["A1"] = "wrong-bundle"

        def swap_positions(mutated_floor: dict, mutated_sidecar: dict) -> None:
            members = mutated_sidecar["cells"][0]["comparative"][
                "common_mode_replay"
            ]["inputs"]["blocks"][0]["members"]
            members["A1"], members["B1"] = members["B1"], members["A1"]

        def delta_mismatch(mutated_floor: dict, mutated_sidecar: dict) -> None:
            replay = mutated_sidecar["cells"][0]["comparative"][
                "common_mode_replay"
            ]
            block = replay["inputs"]["blocks"][0]
            shift = 1e-6
            block["delta_j"] += shift
            block["zero_point_contrast_j"] += shift
            block["onset_sweep_j"] = [
                value + shift for value in block["onset_sweep_j"]
            ]
            block["offset_sweep_j"] = [
                value + shift for value in block["offset_sweep_j"]
            ]
            block["derived_split"] = core.split_common_mode_block_width(
                delta_j=block["delta_j"],
                onset_sweep_j=block["onset_sweep_j"],
                offset_sweep_j=block["offset_sweep_j"],
                zero_point_contrast_j=block["zero_point_contrast_j"],
                bundle_residual_half_widths_j=block[
                    "bundle_residual_half_widths_j"
                ],
                member_envelope_integral_sum_j=block[
                    "member_envelope_integral_sum_j"
                ],
            )
            _recompute_sidecar_cell_result(mutated_sidecar)

        def missing_block(mutated_floor: dict, mutated_sidecar: dict) -> None:
            mutated_sidecar["cells"][0]["comparative"]["common_mode_replay"][
                "inputs"
            ]["blocks"].pop()
            _recompute_sidecar_cell_result(mutated_sidecar)

        def extra_block(mutated_floor: dict, mutated_sidecar: dict) -> None:
            blocks = mutated_sidecar["cells"][0]["comparative"][
                "common_mode_replay"
            ]["inputs"]["blocks"]
            extra = copy.deepcopy(blocks[-1])
            extra["block_id"] = "extra-extraction-block"
            extra["members"] = {
                position: f"extra-{position}" for position in core._ABBA_POSITIONS
            }
            blocks.append(extra)
            _recompute_sidecar_cell_result(mutated_sidecar)

        def duplicate_floor_id(mutated_floor: dict, mutated_sidecar: dict) -> None:
            blocks = mutated_floor["cells"][0]["comparative"]["blocks"]
            blocks[1]["block_id"] = blocks[0]["block_id"]

        cases = (
            ("wrong positioned member", wrong_member),
            ("A1/B1 swap", swap_positions),
            ("delta_j beyond _close", delta_mismatch),
            ("missing block", missing_block),
            ("extra block", extra_block),
            ("duplicated floor block id", duplicate_floor_id),
        )
        for label, mutate in cases:
            with self.subTest(label=label):
                mutated_floor = copy.deepcopy(floor)
                mutated_sidecar = copy.deepcopy(sidecar)
                mutate(mutated_floor, mutated_sidecar)
                manifest_bytes, floor_bytes, sidecar_bytes = _reseal_test_sources(
                    copy.deepcopy(manifest), mutated_floor, mutated_sidecar
                )
                closeout = build_d165_dominance_closeout(
                    manifest_bytes, floor_bytes, sidecar_bytes
                )
                self.assertEqual(
                    closeout["refusal_reason"], "floor_member_census_mismatch"
                )
                self.assertIsNone(closeout["branch"])

    def test_floor_member_census_direct_call_rejects_malformed_floor(self) -> None:
        """_floor_member_census_error guards malformed floor cells directly."""

        floor = floor_artifact()
        sidecar = replay_sidecar(floor)
        floor["cells"] = {"not": "a list"}
        self.assertEqual(
            core._floor_member_census_error(floor, sidecar),
            "closeout_input_malformed",
        )

    def test_floor_cell_unresolved_does_not_fall_back_to_another_floor_cell(
        self,
    ) -> None:
        _, manifest, floor, sidecar = self.build()
        manifest["arms"][0]["floor_cell_id"] = None
        manifest["manifest_id"] = calculate_manifest_id(manifest)
        closeout = build_d165_dominance_closeout(
            _file_json_bytes(manifest),
            _file_json_bytes(floor),
            _file_json_bytes(sidecar),
        )
        self.assertEqual(closeout["refusal_reason"], "floor_cell_unresolved")
        self.assertIsNone(closeout["branch"])

    def test_resolved_default_cell_refuses_cell_not_common_mode(self) -> None:
        _, manifest, floor, sidecar = self.build()
        target_id = manifest["arms"][0]["floor_cell_id"]
        target = next(
            cell for cell in sidecar["cells"] if cell["cell_id"] == target_id
        )
        target["comparative"] = {
            "independent": target["comparative"]["independent"],
            "estimator": "default",
        }
        manifest_bytes, floor_bytes, sidecar_bytes = _reseal_test_sources(
            manifest, floor, sidecar
        )
        closeout = build_d165_dominance_closeout(
            manifest_bytes, floor_bytes, sidecar_bytes
        )
        self.assertEqual(closeout["refusal_reason"], "cell_not_common_mode")
        self.assertIsNone(closeout["branch"])

    def test_floor_stack_identity_recomputes_to_finalizer_expected_stack_sha(
        self,
    ) -> None:
        _, manifest, floor, sidecar = self.build()
        floor_by_id = {cell["cell_id"]: cell for cell in floor["cells"]}
        for arm in manifest["arms"]:
            expected_stack_sha = stack_identity_sha256(
                arm["floor_stack_identity"]
            )
            self.assertEqual(
                expected_stack_sha,
                floor_by_id[arm["floor_cell_id"]]["source_regime"][
                    "stack_identity_sha256"
                ],
            )

        mutated = copy.deepcopy(manifest)
        mutated["arms"][0]["floor_stack_identity"]["kernel_library"] = (
            "mutated-kernel"
        )
        mutated["manifest_id"] = calculate_manifest_id(mutated)
        closeout = build_d165_dominance_closeout(
            _file_json_bytes(mutated),
            _file_json_bytes(floor),
            _file_json_bytes(sidecar),
        )
        self.assertEqual(closeout["refusal_reason"], "floor_cell_unresolved")

    def test_seven_field_realized_identity_cannot_substitute_for_floor_stack(
        self,
    ) -> None:
        _, manifest, floor, sidecar = self.build()
        manifest["arms"][0]["floor_stack_identity"] = copy.deepcopy(
            manifest["arms"][0]["realized_stack_identity"]
        )
        manifest["manifest_id"] = calculate_manifest_id(manifest)
        closeout = build_d165_dominance_closeout(
            _file_json_bytes(manifest),
            _file_json_bytes(floor),
            _file_json_bytes(sidecar),
        )
        self.assertEqual(closeout["refusal_reason"], "floor_cell_unresolved")

    def test_minted_mixed_floor_finalizes_and_refuses_default_contrast_cell(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seed = install_synthetic_finalization_fixture(
                root / "seed", shared_governed_stack=True
            )
            seed_bundle = next(
                path
                for path in seed["runs_root"].iterdir()
                if (path / "config.json").is_file()
            )
            governed_stack = build_stack_identity(
                json.loads((seed_bundle / "config.json").read_bytes()),
                json.loads((seed_bundle / "metadata.json").read_bytes()),
            )
            self.assertIsNotNone(governed_stack)

            mint_root = root / "mint"
            mint_root.mkdir()
            pinset_path, pinset_sha, inputs, snapshot = (
                freeze_mixed_estimator_v2_pinset(
                    mint_root,
                    source_stack_identity=dict(governed_stack),
                )
            )
            with _mixed_common_mode_seams(inputs):
                floor = generalized_mint.mint_multi_cell_authenticated_artifact(
                    pinset_path=pinset_path,
                    pinset_sha256=pinset_sha,
                    producer_inputs=inputs,
                    calibration_ledger_snapshot=snapshot,
                    project_commit="0" * 40,
                    project_tree_state="clean",
                )
            floor_by_id = {cell["cell_id"]: cell for cell in floor["cells"]}
            cells_by_slot = {
                ("decode", "A"): floor_by_id["cell-0-decode"],
                ("decode", "B"): floor_by_id["cell-1-decode"],
                ("prefill_p256", "A"): floor_by_id["cell-0-prefill"],
                ("prefill_p256", "B"): floor_by_id["cell-1-prefill"],
            }
            fixture = install_synthetic_finalization_fixture(
                root / "final",
                shared_governed_stack=True,
                floor_cells_by_slot=cells_by_slot,
                dominance_criterion=generator.dominance_criterion_registration(),
            )
            fixture["floor_path"].write_bytes(_file_json_bytes(floor))
            default_ids = frozenset(floor_by_id)
            sidecar = replay_sidecar(floor, default_cell_ids=default_ids)
            sidecar_path = fixture["root"] / "dominance_replay_sidecar.json"
            sidecar_path.write_bytes(_file_json_bytes(sidecar))
            pinset_projection, pinset_error = (
                detection_floor_module._read_floor_mint_pinset(
                    pinset_path, expected_sha256=pinset_sha
                )
            )
            self.assertIsNone(pinset_error)
            with mock.patch.object(
                detection_floor_module,
                "_repository_floor_mint_pinsets",
                return_value=([pinset_projection], None),
            ):
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
                    dominance_replay_sidecar_path=sidecar_path,
                )
            closeout = build_d165_dominance_closeout(
                _file_json_bytes(manifest),
                _file_json_bytes(floor),
                _file_json_bytes(sidecar),
            )
        self.assertEqual(
            {arm["floor_cell_id"] for arm in manifest["arms"]}, set(floor_by_id)
        )
        self.assertEqual(closeout["refusal_reason"], "cell_not_common_mode")
        self.assertIsNone(closeout["branch"])

    def test_branch_a_and_branch_b_fixtures(self) -> None:
        floor_a = floor_artifact()
        for cell in floor_a["cells"]:
            for component_name, parent_key in (
                ("absolute", "max_abs_residual_j"),
                ("comparative", "max_abs_delta_j"),
            ):
                component = cell[component_name]
                point = core._point_unguarded_floor_from_component(
                    component, parent_key=parent_key
                )
                component["corner_widened_unguarded_floor_j"] = 2.0 * point
        branch_a, manifest_a, floor_a, sidecar_a = self.build(floor_a)
        self.assertEqual(branch_a["branch"], "A")
        self.assertTrue(branch_a["dominance_sentence_licensed"])
        self.assertTrue(branch_a["subtitle_licensed"])
        self.assert_valid_closeout(branch_a, manifest_a, floor_a, sidecar_a)

        branch_b, manifest_b, floor_b, sidecar_b = self.build()
        self.assertEqual(branch_b["branch"], "B")
        self.assertFalse(branch_b["all_independent_pass"])
        self.assertFalse(branch_b["dominance_sentence_licensed"])
        self.assertFalse(branch_b["subtitle_licensed"])
        self.assert_valid_closeout(branch_b, manifest_b, floor_b, sidecar_b)

    def test_generator_imports_shared_core_and_registration_bytes_are_unchanged(self) -> None:
        self.assertIs(generator.dominance_ratio, core.dominance_ratio)
        self.assertIs(
            generator.split_common_mode_block_width,
            core.split_common_mode_block_width,
        )
        self.assertIs(
            generator.replay_common_mode_dominance,
            core.replay_common_mode_dominance,
        )
        self.assertEqual(
            frozen_json_bytes(generator.dominance_criterion_registration()),
            PINNED_DOMINANCE_CRITERION_BYTES,
        )
        self.assertEqual(
            hashlib.sha256(PINNED_DOMINANCE_CRITERION_BYTES).hexdigest(),
            "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b",
        )

    def test_contract_runnable_command_names_exactly_the_parser_flags(self) -> None:
        # Extract the flags from the contract's fenced command rather than
        # re-typing them, so a parser rename without a contract edit fails here.
        contract = (ROOT / "docs/contracts/d165_dominance_closeout.md").read_text(
            encoding="utf-8"
        )
        commands = [
            line
            for line in contract.splitlines()
            if line.startswith("python3 scripts/build_d165_dominance_closeout.py")
        ]
        self.assertEqual(len(commands), 1, commands)
        documented = re.findall(r"--[a-z-]+", commands[0])
        parser = cli_module._parser()
        parsed = [
            action.option_strings[0]
            for action in parser._actions
            if action.option_strings and action.option_strings[0] != "-h"
        ]
        self.assertEqual(documented, parsed)
        required = {a.option_strings[0] for a in parser._actions if a.required}
        for flag in documented:
            bracketed = f"[{flag}" in commands[0]
            self.assertEqual(bracketed, flag not in required, flag)

    def test_cli_writes_the_same_valid_closeout_as_the_python_builder(self) -> None:
        expected, manifest, floor, sidecar = self.build()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sources = {
                "manifest.json": manifest,
                "floor.json": floor,
                "sidecar.json": sidecar,
            }
            for name, value in sources.items():
                (root / name).write_bytes(_file_json_bytes(value))
            output = root / "closeout.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/build_d165_dominance_closeout.py"),
                    "--finalized-manifest",
                    str(root / "manifest.json"),
                    "--floor-artifact",
                    str(root / "floor.json"),
                    "--replay-sidecar",
                    str(root / "sidecar.json"),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), expected)

    def test_cli_malformed_floor_writes_no_partial_output(self) -> None:
        """cli_module.main reports the builder stop and creates no output."""

        _, manifest, floor, sidecar = self.build()
        floor["cells"] = {"not": "a list"}
        manifest_bytes, floor_bytes, sidecar_bytes = _reseal_test_sources(
            manifest, floor, sidecar
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = root / "manifest.json"
            floor_path = root / "floor.json"
            sidecar_path = root / "sidecar.json"
            manifest_path.write_bytes(manifest_bytes)
            floor_path.write_bytes(floor_bytes)
            sidecar_path.write_bytes(sidecar_bytes)
            output = root / "closeout.json"
            stderr = io.StringIO()
            with mock.patch.object(sys, "stderr", stderr):
                result = cli_module.main(
                    [
                        "--finalized-manifest",
                        str(manifest_path),
                        "--floor-artifact",
                        str(floor_path),
                        "--replay-sidecar",
                        str(sidecar_path),
                        "--output",
                        str(output),
                    ]
                )
            self.assertEqual(result, 2)
            self.assertEqual(
                stderr.getvalue(),
                "d165_dominance_closeout_refused: closeout_input_malformed\n",
            )
            self.assertFalse(output.exists())

    def test_cli_refuses_to_overwrite_an_existing_output(self) -> None:
        _, manifest, floor, sidecar = self.build()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, value in {
                "manifest.json": manifest,
                "floor.json": floor,
                "sidecar.json": sidecar,
            }.items():
                (root / name).write_bytes(_file_json_bytes(value))
            output = root / "closeout.json"
            original = b"pre-existing output\n"
            output.write_bytes(original)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/build_d165_dominance_closeout.py"),
                    "--finalized-manifest",
                    str(root / "manifest.json"),
                    "--floor-artifact",
                    str(root / "floor.json"),
                    "--replay-sidecar",
                    str(root / "sidecar.json"),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("output_already_exists", completed.stderr)
            self.assertEqual(output.read_bytes(), original)

    def test_extraction_total_stays_bit_identical_after_split_exposure(self) -> None:
        blocks, _, _, _ = fixture_replay_inputs()
        for block in blocks:
            arguments = (
                block["delta_j"],
                block["onset_sweep_j"],
                block["offset_sweep_j"],
                block["zero_point_contrast_j"],
                block["member_envelope_integral_sum_j"],
                block["bundle_residual_half_widths_j"],
            )
            self.assertEqual(
                _common_mode_block_half_width(*arguments),
                detection_floor_block_half_width(*arguments),
            )

    def test_measured_pair_reshaped_as_one_cell_sidecar_round_trips(self) -> None:
        """The fixture's two blocks become one sidecar comparative cell.

        Reshaping removes fixture-only member/corpus diagnostics, retains the
        seven registered raw block inputs plus block_id, adds each derived
        shared/local split, embeds and hashes an authenticated bracket, and
        adds synthetic independent records because the fixture has only the
        comparative common-mode inputs.
        """

        floor = floor_artifact()
        sidecar = replay_sidecar(floor)
        sidecar["sidecar_id"] = "measured-pair-one-cell-replay"
        sidecar["cells"] = sidecar["cells"][:1]
        self.assertEqual(core.validate_d165_replay_sidecar(sidecar), [])

        unauthenticated = copy.deepcopy(sidecar)
        unauthenticated["cells"][0]["comparative"]["common_mode_replay"][
            "inputs"
        ]["shared_edge_bound_s"] *= 0.5
        errors = core.validate_d165_replay_sidecar(unauthenticated)
        self.assertTrue(any("unauthenticated" in error for error in errors))

    def test_mint_adapter_rejects_misaligned_inputs_with_named_reason(self) -> None:
        blocks, _, _, _ = fixture_replay_inputs()
        with self.assertRaisesRegex(ValueError, "d165_mint_adapter_input_invalid"):
            core.d165_replay_blocks_from_mint_inputs(
                [block["block_id"] for block in blocks],
                [block["delta_j"] for block in blocks[:-1]],
                [object() for _ in blocks],
                [block["members"] for block in blocks],
            )
        with self.assertRaisesRegex(
            ValueError, core.CLOSEOUT_INPUT_MALFORMED_ADAPTER
        ):
            core.d165_replay_blocks_from_mint_inputs(
                [[]],
                [blocks[0]["delta_j"]],
                [object()],
                [blocks[0]["members"]],
            )

    def test_mint_adapter_copies_exact_positioned_members_only(self) -> None:
        blocks, _, _, _ = fixture_replay_inputs()
        self.assertEqual(set(blocks[0]["members"]), set(core._ABBA_POSITIONS))
        self.assertNotIn("members", core._raw_replay_block(blocks[0]))
        invalid_members = copy.deepcopy(blocks[0]["members"])
        invalid_members.pop("A1")
        with self.assertRaisesRegex(ValueError, "d165_mint_adapter_input_invalid"):
            core.d165_replay_blocks_from_mint_inputs(
                [blocks[0]["block_id"]],
                [blocks[0]["delta_j"]],
                [object()],
                [invalid_members],
            )


if __name__ == "__main__":
    unittest.main()
