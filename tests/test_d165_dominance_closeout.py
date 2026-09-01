"""D-165 dominance close-out core and artifact-contract tests."""

from __future__ import annotations

import copy
import functools
import hashlib
import inspect
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from configs.campaigns.d117_contrast_v5 import generate_configs as generator
from joulewise.analysis_manifest_v3 import (
    finalize_prospective_analysis_manifest_v3,
)
from joulewise import dominance_closeout as core
from joulewise.detection_floor import (
    _common_mode_block_half_width as detection_floor_block_half_width,
)
from joulewise.floor_extraction import (
    _CommonModeBlockInputs,
    _common_mode_block_half_width,
)
from scripts.build_d165_dominance_closeout import (
    build_d165_dominance_closeout,
)
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
from tests.test_d117_contrast_v5_pack import (
    PINNED_DOMINANCE_CRITERION_BYTES,
    frozen_json_bytes,
)


ROOT = Path(__file__).resolve().parents[1]
REAL_BLOCK_FIXTURE = ROOT / "tests/fixtures/fcm_r4_real_blocks/measured_pair.json"
CELL_IDS = (
    "cell-decode-a",
    "cell-decode-b",
    "cell-prefill_p256-a",
    "cell-prefill_p256-b",
)


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


def floor_artifact() -> dict:
    return {
        "schema_version": core.FLOOR_ARTIFACT_SCHEMA_VERSION,
        "artifact_id": "d165-test-floor",
        "cells": [
            {
                "cell_id": cell_id,
                "absolute": {
                    "max_abs_residual_j": 1.0,
                    "prediction_component_j": 0.5,
                    "corner_widened_unguarded_floor_j": 2.0,
                },
                "comparative": {
                    "max_abs_delta_j": 1.0,
                    "prediction_component_j": 0.75,
                    "corner_widened_unguarded_floor_j": 2.5,
                },
            }
            for cell_id in CELL_IDS
        ],
    }


@functools.cache
def _production_finalized_manifest() -> dict:
    """Run the production finalizer once and retain its real wire shape."""

    with tempfile.TemporaryDirectory() as temporary:
        fixture = install_synthetic_finalization_fixture(Path(temporary))
        return finalize_prospective_analysis_manifest_v3(
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


def finalized_manifest() -> dict:
    return copy.deepcopy(_production_finalized_manifest())


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


def _attach_replay_sidecar(
    manifest: dict, floor: dict, sidecar: dict
) -> tuple[bytes, bytes, bytes]:
    floor_bytes = _file_json_bytes(floor)
    sidecar_bytes = _file_json_bytes(sidecar)
    evidence = manifest["evidence"]
    evidence["aggregate_floor_artifact"]["sha256"] = hashlib.sha256(
        floor_bytes
    ).hexdigest()
    # injected pending D165-SIDECAR-EMIT-01
    evidence["dominance_replay_sidecar"] = {
        "path": "dominance_replay_sidecar.json",
        "sha256": hashlib.sha256(sidecar_bytes).hexdigest(),
        "schema_version": sidecar["schema_version"],
        "sidecar_id": sidecar["sidecar_id"],
    }
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
) -> tuple[list[dict], dict, float, dict]:
    fixture = json.loads(REAL_BLOCK_FIXTURE.read_text(encoding="utf-8"))
    bound = float(fixture["operative_bound_s"])
    bracket = authenticated_bracket(bound)
    source_block_ids = []
    block_deltas_j = []
    block_inputs = []
    for source in fixture["blocks"]:
        source_block_ids.append(source["block_id"])
        block_deltas_j.append(source["delta_j"])
        block_inputs.append(
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
        selected_deltas = block_deltas_j
        selected_inputs = block_inputs
    else:
        selected_ids = block_ids
        selected_deltas = [
            block_deltas_j[index % len(block_deltas_j)]
            for index in range(len(selected_ids))
        ]
        selected_inputs = [
            block_inputs[index % len(block_inputs)]
            for index in range(len(selected_ids))
        ]
    blocks = core.d165_replay_blocks_from_mint_inputs(
        selected_ids, selected_deltas, selected_inputs
    )
    raw_blocks = [core._raw_replay_block(block) for block in blocks]
    result = core.replay_common_mode_dominance(
        raw_blocks,
        calibration_bracket=bracket,
        shared_edge_bound_s=bound,
    )
    return blocks, bracket, bound, result


def replay_sidecar(floor: dict, manifest: dict | None = None) -> dict:
    manifest = finalized_manifest() if manifest is None else manifest
    block_ids_by_cell: dict[str, list[str]] = {}
    for contrast in manifest["contrasts"]:
        for cell_key in ("cell_a_id", "cell_b_id"):
            block_ids_by_cell[contrast[cell_key]] = contrast["block_ids"]
    cells = []
    for floor_cell in floor["cells"]:
        blocks, bracket, bound, result = fixture_replay_inputs(
            block_ids_by_cell[floor_cell["cell_id"]]
        )
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
                "comparative": {
                    "independent": independent_from_component(
                        floor_cell["comparative"], "max_abs_delta_j"
                    ),
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
                },
            }
        )
    return {
        "schema_version": core.REPLAY_SCHEMA_VERSION,
        "sidecar_id": "d165-test-replay",
        "cells": cells,
    }


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
        sidecar = replay_sidecar(floor, manifest)
        manifest_bytes, floor_bytes, sidecar_bytes = _attach_replay_sidecar(
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
        mapping = dict(zip(CELL_IDS, forged_ids, strict=True))
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
            f"{CELL_IDS[0]!r} for component 'absolute'",
            errors,
        )
        self.assertIsNone(closeout["branch"])
        self.assertFalse(closeout["dominance_sentence_licensed"])
        self.assertFalse(closeout["subtitle_licensed"])

    def test_ratio_equal_to_two_passes(self) -> None:
        closeout, manifest, floor, sidecar = self.build()
        record = closeout["independent_ratios"][0]
        self.assertEqual(record["ratio"], 2.0)
        self.assertTrue(record["passes"])
        self.assertEqual(closeout["branch"], "A")
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
        manifest_bytes, floor_bytes, sidecar_bytes = _attach_replay_sidecar(
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

    def test_build_catches_unhashable_source_membership_as_named_neither(self) -> None:
        _, manifest, floor, sidecar = self.build()
        malformed_manifest_bytes = mutate_then_encode(
            _file_json_bytes(manifest),
            lambda value: value["contrasts"][0]["block_ids"].__setitem__(0, []),
        )
        floor_bytes = _file_json_bytes(floor)
        sidecar_bytes = _file_json_bytes(sidecar)
        closeout = build_d165_dominance_closeout(
            malformed_manifest_bytes, floor_bytes, sidecar_bytes
        )
        self.assertEqual(
            closeout["refusal_reason"], core.CLOSEOUT_INPUT_MALFORMED_SOURCE
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
        manifest_bytes = _file_json_bytes(manifest)
        floor_bytes = _file_json_bytes(floor)
        sidecar_bytes = _file_json_bytes(sidecar)
        for missing_key in ("path", "sha256", "schema_version", "sidecar_id"):
            with self.subTest(missing_key=missing_key):
                partial_manifest_bytes = mutate_then_encode(
                    manifest_bytes,
                    lambda value, key=missing_key: value["evidence"][
                        "dominance_replay_sidecar"
                    ].pop(key),
                )
                closeout = build_d165_dominance_closeout(
                    partial_manifest_bytes, floor_bytes, sidecar_bytes
                )
                self.assertEqual(
                    closeout["refusal_reason"], "manifest_lacks_replay_sidecar"
                )
                self.assertIsNone(closeout["branch"])

    def test_sidecar_attachment_schema_mismatch_has_identity_reason(self) -> None:
        _, manifest, floor, sidecar = self.build()
        manifest_bytes = mutate_then_encode(
            _file_json_bytes(manifest),
            lambda value: value["evidence"]["dominance_replay_sidecar"].update(
                {"schema_version": "forged-schema"}
            ),
        )
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
        cases.append(
            (
                "cell census",
                duplicate_cell,
                "sidecar.cells[1].cell_id: duplicate 'cell-decode-a'",
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
        cases.append(
            (
                "block census",
                duplicate_block,
                "sidecar.cells[0].comparative.common_mode_replay.inputs."
                "blocks[1].block_id: duplicate 'd117-decode-contrast-b01'",
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
        license_record["dominance_sentence_licensed"] = False
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

    def test_builder_guard_matrix_refuses_named_invalid_sources(self) -> None:
        manifest = finalized_manifest()
        floor = floor_artifact()
        sidecar = replay_sidecar(floor, manifest)
        cases = []

        short_floor = copy.deepcopy(floor)
        short_floor["cells"].pop()
        cases.append(
            (
                "floor census",
                manifest,
                short_floor,
                sidecar,
                "floor_artifact.cells: D-165 requires exactly four cells",
            )
        )
        missing_component = copy.deepcopy(floor)
        del missing_component["cells"][0]["absolute"]
        cases.append(
            (
                "component census",
                manifest,
                missing_component,
                sidecar,
                ".absolute: missing component",
            )
        )
        invalid_corner = copy.deepcopy(floor)
        invalid_corner["cells"][0]["absolute"][
            "corner_widened_unguarded_floor_j"
        ] = "forged"
        cases.append(
            (
                "corner operand",
                manifest,
                invalid_corner,
                sidecar,
                "corner_widened_unguarded_floor_j: invalid",
            )
        )
        wrong_manifest_schema = copy.deepcopy(manifest)
        wrong_manifest_schema["schema_version"] = "forged-schema"
        cases.append(
            (
                "manifest schema",
                wrong_manifest_schema,
                floor,
                sidecar,
                "manifest_id: source schema mismatch",
            )
        )

        for guard, manifest_value, floor_value, sidecar_value, expected in cases:
            with self.subTest(guard=guard):
                manifest_for_case = copy.deepcopy(manifest_value)
                sidecar_for_case = copy.deepcopy(sidecar_value)
                manifest_bytes, floor_bytes, sidecar_bytes = (
                    _attach_replay_sidecar(
                        manifest_for_case, floor_value, sidecar_for_case
                    )
                )
                with self.assertRaisesRegex(ValueError, expected):
                    build_d165_dominance_closeout(
                        manifest_bytes,
                        floor_bytes,
                        sidecar_bytes,
                    )

        attachment_cases: list[
            tuple[str, bytes, bytes, bytes, str]
        ] = []

        attached_manifest = copy.deepcopy(manifest)
        attached_manifest_bytes, floor_bytes, sidecar_bytes = (
            _attach_replay_sidecar(attached_manifest, floor, sidecar)
        )
        absent_manifest_bytes = mutate_then_encode(
            attached_manifest_bytes,
            lambda value: value["evidence"].pop("dominance_replay_sidecar"),
        )
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
            _attach_replay_sidecar(digest_manifest, floor, sidecar)
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

        campaign_manifest = copy.deepcopy(manifest)
        campaign_sidecar = copy.deepcopy(sidecar)
        contrasts = campaign_manifest["contrasts"]
        for target, other in (
            (contrasts[0], contrasts[1]),
            (contrasts[1], contrasts[0]),
        ):
            for cell_id in (target["cell_a_id"], target["cell_b_id"]):
                cell = next(
                    row
                    for row in campaign_sidecar["cells"]
                    if row["cell_id"] == cell_id
                )
                blocks = cell["comparative"]["common_mode_replay"]["inputs"][
                    "blocks"
                ]
                for block, block_id in zip(
                    blocks, other["block_ids"], strict=True
                ):
                    block["block_id"] = block_id
        campaign_manifest_bytes, campaign_floor_bytes, campaign_sidecar_bytes = (
            _attach_replay_sidecar(campaign_manifest, floor, campaign_sidecar)
        )
        attachment_cases.append(
            (
                "manifest block membership",
                campaign_manifest_bytes,
                campaign_floor_bytes,
                campaign_sidecar_bytes,
                "manifest_block_membership_mismatch",
            )
        )

        identity_manifest = copy.deepcopy(manifest)
        identity_manifest_bytes, identity_floor_bytes, identity_sidecar_bytes = (
            _attach_replay_sidecar(identity_manifest, floor, sidecar)
        )
        identity_manifest_bytes = mutate_then_encode(
            identity_manifest_bytes,
            lambda value: value["evidence"]["dominance_replay_sidecar"].update(
                {"sidecar_id": "other-sidecar"}
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

    def test_branch_a_and_branch_b_fixtures(self) -> None:
        branch_a, manifest_a, floor_a, sidecar_a = self.build()
        self.assertEqual(branch_a["branch"], "A")
        self.assertTrue(branch_a["dominance_sentence_licensed"])
        self.assertTrue(branch_a["subtitle_licensed"])
        self.assert_valid_closeout(branch_a, manifest_a, floor_a, sidecar_a)

        floor_b = floor_artifact()
        floor_b["cells"][0]["absolute"][
            "corner_widened_unguarded_floor_j"
        ] = 1.5
        branch_b, manifest_b, floor_b, sidecar_b = self.build(floor_b)
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
            )
        with self.assertRaisesRegex(
            ValueError, core.CLOSEOUT_INPUT_MALFORMED_ADAPTER
        ):
            core.d165_replay_blocks_from_mint_inputs(
                [[]], [blocks[0]["delta_j"]], [object()]
            )


if __name__ == "__main__":
    unittest.main()
