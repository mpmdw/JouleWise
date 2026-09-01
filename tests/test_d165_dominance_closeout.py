"""D-165 dominance close-out core and artifact-contract tests."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from configs.campaigns.d117_contrast_v5 import generate_configs as generator
from joulewise import dominance_closeout as core
from joulewise.detection_floor import (
    _common_mode_block_half_width as detection_floor_block_half_width,
)
from joulewise.floor_extraction import _common_mode_block_half_width
from scripts.build_d165_dominance_closeout import (
    build_d165_dominance_closeout,
)
from tests.test_d117_contrast_v5_pack import (
    PINNED_DOMINANCE_CRITERION_BYTES,
    frozen_json_bytes,
)


ROOT = Path(__file__).resolve().parents[1]
REAL_BLOCK_FIXTURE = ROOT / "tests/fixtures/fcm_r4_real_blocks/measured_pair.json"
CELL_IDS = (
    "qwen3-1p7b-prefill",
    "qwen3-1p7b-decode",
    "qwen3-8b-prefill",
    "qwen3-8b-decode",
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


def finalized_manifest() -> dict:
    return {
        "schema_version": core.FINALIZED_MANIFEST_SCHEMA_VERSION,
        "manifest_id": "d165-test-finalized-manifest",
        "freeze_status": "finalized",
    }


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


def fixture_replay_inputs() -> tuple[list[dict], dict, float, dict]:
    fixture = json.loads(REAL_BLOCK_FIXTURE.read_text(encoding="utf-8"))
    bound = float(fixture["operative_bound_s"])
    bracket = authenticated_bracket(bound)
    blocks = []
    for source in fixture["blocks"]:
        block = {
            "block_id": source["block_id"],
            "delta_j": source["delta_j"],
            "onset_sweep_j": copy.deepcopy(source["onset_sweep_j"]),
            "offset_sweep_j": copy.deepcopy(source["offset_sweep_j"]),
            "zero_point_contrast_j": source["zero_point_contrast_j"],
            "bundle_residual_half_widths_j": copy.deepcopy(
                source["bundle_residual_half_widths_j"]
            ),
            "member_window_bounds_s": copy.deepcopy(
                source["member_window_bounds_s"]
            ),
            "member_envelope_integral_sum_j": source[
                "member_envelope_integral_sum_j"
            ],
        }
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
        blocks.append(block)
    raw_blocks = [core._raw_replay_block(block) for block in blocks]
    result = core.replay_common_mode_dominance(
        raw_blocks,
        calibration_bracket=bracket,
        shared_edge_bound_s=bound,
    )
    return blocks, bracket, bound, result


def replay_sidecar(floor: dict) -> dict:
    blocks, bracket, bound, result = fixture_replay_inputs()
    cells = []
    for floor_cell in floor["cells"]:
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

    def build(self, floor: dict | None = None) -> tuple[dict, dict, dict, dict]:
        floor = floor_artifact() if floor is None else floor
        manifest = finalized_manifest()
        sidecar = replay_sidecar(floor)
        closeout = build_d165_dominance_closeout(manifest, floor, sidecar)
        return closeout, manifest, floor, sidecar

    def assert_valid_closeout(
        self, closeout: dict, manifest: dict, floor: dict, sidecar: dict
    ) -> None:
        self.assertEqual(
            core.validate_d165_closeout(
                closeout,
                finalized_manifest=manifest,
                floor_artifact=floor,
                replay_sidecar=sidecar,
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
                    finalized_manifest=manifest,
                    floor_artifact=floor,
                    replay_sidecar=sidecar,
                )
            )
        )

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
        closeout = build_d165_dominance_closeout(manifest, floor, sidecar)
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
        mutated_floor = copy.deepcopy(floor)
        mutated_floor["cells"][0]["absolute"][
            "corner_widened_unguarded_floor_j"
        ] = 2.1
        errors = core.validate_d165_closeout(
            closeout,
            finalized_manifest=manifest,
            floor_artifact=mutated_floor,
            replay_sidecar=sidecar,
        )
        self.assertTrue(any("source-hash mismatch" in error for error in errors))

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
                (root / name).write_text(json.dumps(value), encoding="utf-8")
            output = root / "closeout.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/build_d165_dominance_closeout.py"),
                    str(root / "manifest.json"),
                    str(root / "floor.json"),
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


if __name__ == "__main__":
    unittest.main()
