"""Acceptance coverage for the D-165 OB-01 / OR-01 renderer."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from joulewise import dominance_closeout as core
from joulewise.results_fill_outcome import STOP_FILL, render_outcome_fills
from tests import test_d165_dominance_closeout as d165_fixtures


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "results_fill_outcome"


def _file_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _built_sources(
    builder: str,
) -> tuple[dict | None, bytes | None, bytes | None, bytes | None]:
    case = d165_fixtures.D165DominanceCloseoutTests()
    if builder == "none":
        return None, None, None, None
    if builder == "branch_a":
        floor = d165_fixtures.floor_artifact()
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
        closeout, manifest, floor, sidecar = case.build(floor)
    elif builder == "branch_b":
        floor = d165_fixtures.floor_artifact()
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
        manifest = d165_fixtures.finalized_manifest()
        sidecar = d165_fixtures.replay_sidecar(
            floor, residual_width_scale=10.0
        )
        manifest_bytes, floor_bytes, sidecar_bytes = (
            d165_fixtures._reseal_test_sources(manifest, floor, sidecar)
        )
        closeout = d165_fixtures.build_d165_dominance_closeout(
            manifest_bytes, floor_bytes, sidecar_bytes
        )
        return closeout, manifest_bytes, floor_bytes, sidecar_bytes
    elif builder == "closeout_refusal":
        floor = d165_fixtures.floor_artifact()
        floor["cells"][0]["absolute"]["max_abs_residual_j"] = 0.0
        floor["cells"][0]["absolute"]["prediction_component_j"] = 0.0
        closeout, manifest, floor, sidecar = case.build(floor)
    else:
        raise AssertionError(f"unknown fixture builder: {builder}")
    return (
        closeout,
        _file_json_bytes(manifest),
        _file_json_bytes(floor),
        _file_json_bytes(sidecar),
    )


def _render(fixture: dict) -> dict[str, str]:
    closeout, manifest, floor, sidecar = _built_sources(fixture["builder"])
    return render_outcome_fills(
        closeout,
        finalized_manifest_bytes=manifest,
        floor_artifact_bytes=floor,
        replay_sidecar_bytes=sidecar,
        before_comparison_stops=fixture["before_comparison_stops"],
        precedence=fixture["precedence"],
    )


class ResultsFillOutcomeTests(unittest.TestCase):
    maxDiff = None

    def test_registered_outcome_renderings_and_fail_closed_guards(self) -> None:
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
        fixtures = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in fixture_paths
        }
        for name, fixture in fixtures.items():
            with self.subTest(fixture=name):
                rendered = _render(fixture)
                self.assertEqual(rendered, fixture["expected"])
                self.assertFalse(
                    any(
                        marker in value
                        for value in rendered.values()
                        for marker in ("[VALUE]", "[FILL:", "[PENDING]")
                    )
                )

        stopped = {"OB-01": STOP_FILL, "OR-01": STOP_FILL}

        closeout, manifest, floor, sidecar = _built_sources("branch_a")
        assert closeout is not None
        incomplete = copy.deepcopy(closeout)
        incomplete["independent_ratios"].pop()
        self.assertEqual(
            render_outcome_fills(
                incomplete,
                finalized_manifest_bytes=manifest,
                floor_artifact_bytes=floor,
                replay_sidecar_bytes=sidecar,
            ),
            stopped,
            "deleting one A-fixture census entry must flip the entire result",
        )

        assert floor is not None
        self.assertEqual(
            render_outcome_fills(
                closeout,
                finalized_manifest_bytes=manifest,
                floor_artifact_bytes=floor + b" ",
                replay_sidecar_bytes=sidecar,
            ),
            stopped,
            "a close-out whose source bytes do not authenticate must stop",
        )

        before = fixtures["before_comparison_refusal"]
        unauthenticated_before = copy.deepcopy(before)
        unauthenticated_before["before_comparison_stops"][0][
            "authenticated"
        ] = False
        self.assertEqual(_render(unauthenticated_before), stopped)

        conflicting = copy.deepcopy(before)
        conflicting["builder"] = "closeout_refusal"
        self.assertEqual(_render(conflicting), stopped)

        missing_precedence = copy.deepcopy(before)
        missing_precedence["precedence"] = None
        self.assertEqual(_render(missing_precedence), stopped)


if __name__ == "__main__":
    unittest.main()
