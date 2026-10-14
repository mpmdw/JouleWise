"""Regressions for production defects the S10 chain fixture found in the floor mint."""
from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tests import test_mint_floor_artifact_generalized as g

generalized = g.generalized


def _lineage_bearing_artifacts(lineage_for_index):
    """Build the synthetic v2 aggregate with each producer's components on a lineage.

    Returns the artifact, its components and the pinset value whose component
    pins are the components' own digests (as the pinset emitter writes them).
    """
    pinset, inputs, snapshot = g.synthetic_v2_fixture()
    for producer_index, producer in enumerate(pinset["producer_plans"]):
        lineage = lineage_for_index(producer_index)
        plan_id = producer["plan"]["plan_id"]
        report = copy.deepcopy(inputs[plan_id].cells["decode"].absolute.report)
        report["launch_lineage"] = copy.deepcopy(lineage)
        for report_cell in report["cells"]:
            for member_row in report_cell["members"]:
                member_row["launch_lineage"] = copy.deepcopy(lineage)
        g._reattach_producer_report(pinset, inputs, producer_index, report)
        producer_input = inputs[plan_id]
        inputs[plan_id] = replace(producer_input, cells={
            role: replace(cell,
                          absolute=replace(cell.absolute, launch_lineage=copy.deepcopy(lineage)),
                          comparative=replace(cell.comparative, launch_lineage=copy.deepcopy(lineage)))
            for role, cell in producer_input.cells.items()})
    g._repair_v2_pinset_self_hashes(pinset)
    # The window authentication (stubbed exactly as the existing lineage test
    # stubs it) returns the lineage of the producer whose runs root it opens.
    by_root = {Path(inputs[producer["plan"]["plan_id"]].evidence_root): lineage_for_index(producer_index)
               for producer_index, producer in enumerate(pinset["producer_plans"])}

    def authenticate(runs_root, _member_ids, **_kwargs):
        return copy.deepcopy(by_root[Path(runs_root)])

    with tempfile.TemporaryDirectory() as tmp:
        path, digest = g.write_pinset(Path(tmp), pinset)
        loaded = generalized.load_pinset(path, digest)
        with mock.patch.object(generalized.mint_estimator, "authenticate_window_launch_lineage",
                               side_effect=authenticate):
            artifact, components = generalized._build_v2_artifacts(
                pinset=loaded, pinset_path=path, pinset_sha256=digest, producer_inputs=inputs,
                calibration_ledger_snapshot=snapshot, project_commit="0" * 40, project_tree_state="clean")
    for producer, entry, component in zip(pinset["producer_plans"], pinset["aggregate"]["component_artifacts"],
                                          components, strict=True):
        producer["component_artifact"]["sha256"] = generalized._artifact_sha256(component)
        entry["sha256"] = producer["component_artifact"]["sha256"]
    g._repair_v2_pinset_self_hashes(pinset)
    return artifact, components, pinset


class PostBindComponentLineageTests(unittest.TestCase):
    """The post-bind check rebuilds each component from the aggregate; it must carry the lineage."""

    def test_single_lineage_components_pass_post_bind_component_hash_check(self):
        lineage = g.launch_lineage()
        artifact, components, pinset = _lineage_bearing_artifacts(lambda _index: lineage)
        self.assertEqual(artifact["provenance"]["launch_lineage"], lineage)
        self.assertTrue(all(c["provenance"]["launch_lineage"] == lineage for c in components))
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = g.write_pinset(Path(tmp), pinset)
            errors = generalized._validate_v2_artifact_binding(artifact, generalized.load_pinset(path, digest))
        self.assertFalse([e for e in errors if "component artifact hash mismatch" in e], errors)

    def test_component_hash_still_binds_every_other_byte(self):
        lineage = g.launch_lineage()
        artifact, _components, pinset = _lineage_bearing_artifacts(lambda _index: lineage)
        tampered = copy.deepcopy(artifact)
        tampered["provenance"]["launch_lineage"] = {**tampered["provenance"]["launch_lineage"],
                                                    "schema_version": "tampered"}
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = g.write_pinset(Path(tmp), pinset)
            errors = generalized._validate_v2_artifact_binding(tampered, generalized.load_pinset(path, digest))
        self.assertTrue([e for e in errors if "component artifact hash mismatch" in e], errors)


def _window_lineage(index):
    lineage = g.launch_lineage()
    lineage["window_id"] = f"window-{index + 1}"
    lineage["plan_id"] = f"plan-{index + 1}"
    return lineage


class QLineageConditionalSeamTests(unittest.TestCase):
    """Q-LINEAGE is open: the unchanged rule refuses two windows; the fixture seam's option is pinned here."""

    def test_two_window_lineages_refuse_under_the_unchanged_rule(self):
        with self.assertRaisesRegex(generalized.MintError,
                                    "launch_lineage_conflict: aggregate components does not carry one"):
            _lineage_bearing_artifacts(_window_lineage)

    def test_conditional_seam_omits_the_aggregate_carrier_and_rebinds_each_producer(self):
        from tests.b5_analysis.fixtures_s10 import conditional_aggregate_lineage_seam
        with conditional_aggregate_lineage_seam():
            artifact, components, pinset = _lineage_bearing_artifacts(_window_lineage)
            self.assertNotIn("launch_lineage", artifact["provenance"])
            self.assertEqual([c["provenance"]["launch_lineage"]["window_id"] for c in components],
                             ["window-1", "window-2"])
            with tempfile.TemporaryDirectory() as tmp:
                path, digest = g.write_pinset(Path(tmp), pinset)
                errors = generalized._validate_v2_artifact_binding(artifact,
                                                                   generalized.load_pinset(path, digest))
        self.assertFalse([e for e in errors if "component artifact hash mismatch" in e], errors)
        # Within one producer the cells must still share one lineage.
        with conditional_aggregate_lineage_seam(), self.assertRaisesRegex(generalized.MintError, "producer"):
            generalized._common_minted_artifact_launch_lineage(
                [{"provenance": {"launch_lineage": _window_lineage(0)}},
                 {"provenance": {"launch_lineage": _window_lineage(1)}}], label="producer 'p' cells")


if __name__ == "__main__":
    unittest.main()
