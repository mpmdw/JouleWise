"""Acceptance coverage for the D-165 OB-01 / OR-01 renderer."""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import inspect
import json
import re
import unittest
from pathlib import Path

from joulewise import dominance_closeout as core
from joulewise import results_fill_outcome as renderer
from joulewise.analysis_manifest_v3 import calculate_manifest_id
from joulewise.identity_pins import stack_identity_sha256
from tests import test_d165_dominance_closeout as d165_fixtures


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "results_fill_outcome"
REGISTRY = ROOT / "docs" / "paper" / "results-fill-registry.md"
FILL_KEYS = ("OB-01", "OR-01")
QWEN3 = {
    "A": {
        "family": "qwen3",
        "model_tag": "qwen3-1p7b",
        "name": "Qwen3-1.7B-4bit",
        "public_name": "Qwen3-1.7B",
        "revision": "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
    },
    "B": {
        "family": "qwen3",
        "model_tag": "qwen3-8b",
        "name": "Qwen3-8B-4bit",
        "public_name": "Qwen3-8B",
        "revision": "545dc4251c05440727734bcd94334791f6ab0192",
    },
}


def _file_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _switch_sources_to_qwen3(manifest: dict, floor: dict) -> None:
    """Retarget fresh D-165 builder copies to the ruled synthetic `_v5` pair."""

    floor_by_id = {cell["cell_id"]: cell for cell in floor["cells"]}
    for arm in manifest["arms"]:
        identity = QWEN3[arm["arm_id"].rsplit(":", 1)[1]]
        arm["model_tag"] = identity["model_tag"]
        realized = arm["realized_stack_identity"]
        realized["model"].update(
            {
                "context_window": 40960,
                "family": identity["family"],
                "name": identity["name"],
                "revision": identity["revision"],
                "source": f"/Users/edr/jw_models/mlx-community/{identity['name']}",
            }
        )
        realized["tokenizer"].update(
            {
                "identifier": (
                    f"/Users/edr/jw_models/mlx-community/{identity['name']}"
                ),
                "revision": identity["revision"],
                "vocab_size": 151936,
            }
        )
        floor_stack = arm["floor_stack_identity"]
        floor_stack["tokenizer_identity"].update(
            {
                "identifier": identity["name"],
                "revision": identity["revision"],
                "vocab_size": 151936,
            }
        )
        floor_cell = floor_by_id[arm["floor_cell_id"]]
        floor_cell["source_regime"]["stack_identity"] = copy.deepcopy(floor_stack)
        floor_cell["source_regime"]["stack_identity_sha256"] = (
            stack_identity_sha256(floor_stack)
        )


def _built_sources(
    builder: str, *, v5_identity: bool = True
) -> tuple[dict | None, bytes, bytes, bytes]:
    floor = d165_fixtures.floor_artifact()
    manifest = d165_fixtures.finalized_manifest()
    if v5_identity:
        _switch_sources_to_qwen3(manifest, floor)

    if builder == "branch_a":
        for cell in floor["cells"]:
            for component_name, parent_key in (
                ("absolute", "max_abs_residual_j"),
                ("comparative", "max_abs_delta_j"),
            ):
                component = cell[component_name]
                point = core._point_unguarded_floor_from_component(
                    component, parent_key=parent_key
                )
                component["corner_widened_unguarded_floor_j"] = 2.0 * point
    elif builder == "branch_b":
        first = True
        for cell in floor["cells"]:
            for component_name, parent_key in (
                ("absolute", "max_abs_residual_j"),
                ("comparative", "max_abs_delta_j"),
            ):
                if first:
                    first = False
                    continue
                component = cell[component_name]
                point = core._point_unguarded_floor_from_component(
                    component, parent_key=parent_key
                )
                component["corner_widened_unguarded_floor_j"] = 2.0 * point
    elif builder == "closeout_refusal":
        floor["cells"][0]["absolute"]["max_abs_residual_j"] = 0.0
        floor["cells"][0]["absolute"]["prediction_component_j"] = 0.0
    elif builder not in {"none", "source_refusal", "census_refusal"}:
        raise AssertionError(f"unknown fixture builder: {builder}")

    sidecar = d165_fixtures.replay_sidecar(
        floor, residual_width_scale=10.0 if builder == "branch_b" else 20.0
    )
    if builder == "census_refusal":
        sidecar["cells"].pop()
    manifest_bytes, floor_bytes, sidecar_bytes = (
        d165_fixtures._reseal_test_sources(manifest, floor, sidecar)
    )
    if builder == "none":
        return None, manifest_bytes, floor_bytes, sidecar_bytes
    if builder == "source_refusal":
        changed_floor = json.loads(floor_bytes.decode("utf-8"))
        changed_floor["cells"][0]["absolute"][
            "corner_widened_unguarded_floor_j"
        ] = 2.1
        floor_bytes = _file_json_bytes(changed_floor)
    closeout = d165_fixtures.build_d165_dominance_closeout(
        manifest_bytes, floor_bytes, sidecar_bytes
    )
    return closeout, manifest_bytes, floor_bytes, sidecar_bytes


def _validation_result(
    validator: str,
    source_bytes: bytes,
    manifest_bytes: bytes,
    *,
    result: tuple | None = None,
):
    if result is None:
        source = json.loads(source_bytes)
        result = (
            (source["reason"],)
            if validator == "whole_window_refusal_reasons"
            else ()
        )
    result_type = getattr(renderer, "BeforeComparisonValidationResult", None)
    if result_type is None:
        return {
            "validator": validator,
            "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "finalized_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "result": result,
        }
    return result_type(
        validator=validator,
        source_sha256=hashlib.sha256(source_bytes).hexdigest(),
        finalized_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        result=result,
    )


def _before_inputs(
    fixture: dict, manifest_bytes: bytes
) -> tuple[list[bytes], list[object]]:
    sources: list[bytes] = []
    results: list[object] = []
    for item in fixture["before_comparison_sources"]:
        source_bytes = _file_json_bytes(item["source"])
        sources.append(source_bytes)
        results.append(
            _validation_result(item["validator"], source_bytes, manifest_bytes)
        )
    return sources, results


def _render(fixture: dict, *, v5_identity: bool = True) -> dict[str, str]:
    closeout, manifest, floor, sidecar = _built_sources(
        fixture["builder"], v5_identity=v5_identity
    )
    sources, results = _before_inputs(fixture, manifest)
    before_kwargs = (
        {
            "before_comparison_source_bytes": sources,
            "before_comparison_validator_results": results,
        }
        if sources
        else {}
    )
    return renderer.render_outcome_fills(
        closeout,
        finalized_manifest_bytes=manifest,
        floor_artifact_bytes=floor,
        replay_sidecar_bytes=sidecar,
        **before_kwargs,
    )


def _registry_oracle(name: str) -> str:
    registry = REGISTRY.read_text(encoding="utf-8")
    match = re.search(
        rf"Acceptance oracle `{re.escape(name)}`: `([^`\r\n]+)`", registry
    )
    if match is None:
        raise AssertionError(f"registry acceptance oracle missing: {name}")
    return match.group(1)


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


class ResultsFillOutcomeTests(unittest.TestCase):
    maxDiff = None

    def test_b1_registered_bytes_are_the_independent_acceptance_oracle(self) -> None:
        fixture_paths = sorted(FIXTURES.glob("*.json"))
        self.assertEqual(
            [path.name for path in fixture_paths],
            [
                "before_comparison_absent_verdict.json",
                "before_comparison_refusal.json",
                "branch_a.json",
                "branch_b.json",
                "closeout_refusal.json",
            ],
        )
        for path in fixture_paths:
            fixture = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(fixture=path.stem):
                for fill_key, oracle_name in fixture["registry_oracles"].items():
                    self.assertEqual(fixture["expected"][fill_key], _registry_oracle(oracle_name))
                rendered = _render(fixture)
                self.assertEqual(
                    {key: rendered[key] for key in FILL_KEYS}, fixture["expected"]
                )
                self.assertFalse(
                    any(
                        marker in value
                        for value in rendered.values()
                        for marker in ("[VALUE]", "[FILL:", "[PENDING]")
                    )
                )

    def test_f1_before_comparison_requires_digest_bound_source_bytes_and_result(
        self,
    ) -> None:
        fixture = _fixture("before_comparison_refusal")
        closeout, manifest, floor, sidecar = _built_sources("none")
        sources, results = _before_inputs(fixture, manifest)
        self.assertEqual(_render(fixture)["OR-01"], fixture["expected"]["OR-01"])

        changed_model = json.loads(sources[0])
        changed_model["model"] = "Qwen3-8B"
        changed_model_bytes = _file_json_bytes(changed_model)
        self.assertEqual(
            renderer.render_outcome_fills(
                closeout,
                finalized_manifest_bytes=manifest,
                floor_artifact_bytes=floor,
                replay_sidecar_bytes=sidecar,
                before_comparison_source_bytes=[changed_model_bytes],
                before_comparison_validator_results=results,
            ),
            {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL},
            "changed source bytes must fail against the owning result's digest",
        )
        changed_reason = json.loads(sources[0])
        changed_reason["reason"] = "fabricated"
        changed_reason_bytes = _file_json_bytes(changed_reason)
        rebound_digest_only = dataclasses.replace(
            results[0],
            source_sha256=hashlib.sha256(changed_reason_bytes).hexdigest(),
        )
        self.assertEqual(
            renderer.render_outcome_fills(
                closeout,
                finalized_manifest_bytes=manifest,
                floor_artifact_bytes=floor,
                replay_sidecar_bytes=sidecar,
                before_comparison_source_bytes=[changed_reason_bytes],
                before_comparison_validator_results=[rebound_digest_only],
            ),
            {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL},
            "a caller-rehashed reason must still match the owning validator result",
        )
        invalid_result = _validation_result(
            "whole_window_refusal_reasons",
            sources[0],
            manifest,
            result=("whole_window_verdict_provenance_invalid",),
        )
        self.assertEqual(
            renderer.render_outcome_fills(
                None,
                finalized_manifest_bytes=manifest,
                before_comparison_source_bytes=sources,
                before_comparison_validator_results=[invalid_result],
            ),
            {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL},
        )
        wrong_validator = _validation_result(
            "validate_claim_verdicts", sources[0], manifest
        )
        self.assertEqual(
            renderer.render_outcome_fills(
                None,
                finalized_manifest_bytes=manifest,
                before_comparison_source_bytes=sources,
                before_comparison_validator_results=[wrong_validator],
            ),
            {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL},
        )
        self.assertEqual(
            renderer.render_outcome_fills(
                None,
                finalized_manifest_bytes=manifest,
                before_comparison_source_bytes=sources,
                before_comparison_validator_results=[
                    {
                        "validator": "whole_window_refusal_reasons",
                        "source_sha256": hashlib.sha256(sources[0]).hexdigest(),
                        "finalized_manifest_sha256": hashlib.sha256(manifest).hexdigest(),
                        "result": ("synthetic_window_excluded",),
                    }
                ],
            ),
            {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL},
            "a caller-authored validation dictionary is not an authority result",
        )

    def test_f2_registered_stage_order_has_no_precedence_channel(self) -> None:
        parameters = inspect.signature(renderer.render_outcome_fills).parameters
        self.assertNotIn("precedence", parameters)
        self.assertNotIn("before_comparison_stops", parameters)

        close_fixture = _fixture("closeout_refusal")
        self.assertEqual(_render(close_fixture)["OR-01"], close_fixture["expected"]["OR-01"])

        before_fixture = _fixture("before_comparison_refusal")
        closeout, manifest, floor, sidecar = _built_sources("closeout_refusal")
        sources, results = _before_inputs(before_fixture, manifest)
        rendered = renderer.render_outcome_fills(
            closeout,
            finalized_manifest_bytes=manifest,
            floor_artifact_bytes=floor,
            replay_sidecar_bytes=sidecar,
            before_comparison_source_bytes=sources,
            before_comparison_validator_results=results,
        )
        self.assertEqual(rendered["OR-01"], before_fixture["expected"]["OR-01"])
        self.assertEqual(
            rendered["_secondary_closeout_reason"],
            "dominance_ratio_zero_denominator",
        )

    def test_f3_top_level_closeout_reason_renders_without_matching_ratio(self) -> None:
        cases = {
            "source_refusal": (
                "floor_artifact_source_hash_mismatch",
                "closeout_source",
            ),
            "census_refusal": (
                "replay_sidecar.cells: cell census does not match floor artifact",
                "closeout_census",
            ),
        }
        for builder, (reason, oracle) in cases.items():
            with self.subTest(builder=builder):
                closeout, manifest, floor, sidecar = _built_sources(builder)
                self.assertEqual(closeout["refusal_reason"], reason)
                statuses = [
                    record["status"]
                    for key in (
                        "independent_ratios",
                        "comparative_common_mode_ratios",
                    )
                    for record in closeout[key]
                ]
                self.assertEqual(
                    all(status == "complete" for status in statuses),
                    builder == "source_refusal",
                )
                rendered = renderer.render_outcome_fills(
                    closeout,
                    finalized_manifest_bytes=manifest,
                    floor_artifact_bytes=floor,
                    replay_sidecar_bytes=sidecar,
                )
                self.assertEqual(rendered["OR-01"], _registry_oracle(oracle))

    def test_f4_v5_identity_gate_precedes_every_fill(self) -> None:
        fixture = _fixture("branch_b")
        rendered = _render(fixture, v5_identity=False)
        self.assertEqual(
            {key: rendered[key] for key in FILL_KEYS},
            {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL},
        )
        self.assertEqual(rendered["_stop_reason"], "identity_not_v5")

        _, manifest, _, _ = _built_sources("branch_a")
        identities = {
            (
                arm["realized_stack_identity"]["model"]["name"],
                arm["realized_stack_identity"]["model"]["revision"],
            )
            for arm in json.loads(manifest)["arms"]
        }
        self.assertEqual(
            identities,
            {(value["name"], value["revision"]) for value in QWEN3.values()},
        )

        closeout, manifest, floor, sidecar = _built_sources("branch_b")
        wrong_revision_manifest = json.loads(manifest)
        wrong_revision_manifest["arms"][0]["realized_stack_identity"]["model"][
            "revision"
        ] = "0" * 40
        wrong_revision_manifest["manifest_id"] = calculate_manifest_id(
            wrong_revision_manifest
        )
        wrong_manifest_bytes = _file_json_bytes(wrong_revision_manifest)
        wrong_closeout = d165_fixtures.build_d165_dominance_closeout(
            wrong_manifest_bytes, floor, sidecar
        )
        self.assertEqual(
            core.validate_d165_closeout(
                wrong_closeout,
                finalized_manifest_bytes=wrong_manifest_bytes,
                floor_artifact_bytes=floor,
                replay_sidecar_bytes=sidecar,
            ),
            [],
        )
        wrong_revision_rendered = renderer.render_outcome_fills(
            wrong_closeout,
            finalized_manifest_bytes=wrong_manifest_bytes,
            floor_artifact_bytes=floor,
            replay_sidecar_bytes=sidecar,
        )
        self.assertEqual(wrong_revision_rendered["_stop_reason"], "identity_not_v5")

    def test_existing_fail_closed_guards_remain_biting(self) -> None:
        stopped = {"OB-01": renderer.STOP_FILL, "OR-01": renderer.STOP_FILL}
        closeout, manifest, floor, sidecar = _built_sources("branch_a")
        incomplete = copy.deepcopy(closeout)
        incomplete["independent_ratios"].pop()
        self.assertEqual(
            renderer.render_outcome_fills(
                incomplete,
                finalized_manifest_bytes=manifest,
                floor_artifact_bytes=floor,
                replay_sidecar_bytes=sidecar,
            ),
            stopped,
            "deleting one A-fixture census entry must flip the entire result",
        )
        self.assertEqual(
            renderer.render_outcome_fills(
                closeout,
                finalized_manifest_bytes=manifest,
                floor_artifact_bytes=floor + b" ",
                replay_sidecar_bytes=sidecar,
            ),
            stopped,
            "a close-out whose source bytes do not authenticate must stop",
        )


if __name__ == "__main__":
    unittest.main()
