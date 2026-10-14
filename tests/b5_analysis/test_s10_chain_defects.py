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


class SingleCountStatementTests(unittest.TestCase):
    """The v2 writer's convenience statement for a floor with no attribution-limited cell."""

    def write(self, artifact, root):
        paths = {name: Path(root) / name for name in ("floor.json", "single-count.md", "replay.json")}
        generalized._write_v2_artifact_outputs(
            output_core=generalized._fresh_original_core(), artifact=artifact, sidecar={"replay": True},
            floor_path=paths["floor.json"], statement_path=paths["single-count.md"],
            d165_replay_out=paths["replay.json"])
        return paths

    def test_floor_without_attribution_limited_cell_writes_the_not_applicable_statement(self):
        artifact = {"cells": [{"cell_id": "c1", "absolute": {}, "comparative": {}}], "transport_groups": []}
        with tempfile.TemporaryDirectory() as root:
            paths = self.write(artifact, root)
            self.assertEqual(paths["single-count.md"].read_text(),
                             generalized.V2_SINGLE_COUNT_NOT_APPLICABLE_STATEMENT)
            self.assertTrue(paths["floor.json"].is_file() and paths["replay.json"].is_file())

    def test_non_canonical_discipline_still_refuses(self):
        artifact = {"cells": [{"cell_id": "c1", "single_count_discipline": {"rule_id": "tampered"}}],
                    "transport_groups": []}
        with tempfile.TemporaryDirectory() as root, self.assertRaisesRegex(Exception, "single-count discipline is not canonical"):
            self.write(artifact, root)


class ClaimGateFloorSpecReaderTests(unittest.TestCase):
    """block5_claim_gate_inputs reads each floor pack's sealed spec only for its planned units."""

    SPEC = g.ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json" \
        if hasattr(g, "ROOT") else Path(__file__).resolve().parents[2] / \
        "configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json"

    def test_sealed_floor_spec_declares_registration_and_is_read_as_governed(self):
        from joulewise.analysis_engine import inputs
        import inspect
        raw = self.SPEC.read_bytes()
        with self.assertRaisesRegex(inputs.AnalysisInputError, "forbidden key 'estimator_registration'"):
            inputs._strict_json_admission_bytes(raw, "floor spec")
        spec = inputs._strict_json_admission_bytes(raw, "floor spec", governed_extraction_spec=True)
        self.assertTrue(any("estimator_registration" in cell for cell in spec["cells"]))
        source = inspect.getsource(inputs.block5_claim_gate_inputs)
        self.assertIn('"floor spec",\n', source)
        self.assertIn("governed_extraction_spec=True", source)

    def test_other_inputs_still_refuse_registration_vocabulary(self):
        from joulewise.analysis_engine import inputs
        with self.assertRaisesRegex(inputs.AnalysisInputError, "forbidden key"):
            inputs._strict_json_admission_bytes(b'{"contrasts":[{"estimator_registration":{}}]}', "analysis manifest")


class ClaimSideIndexedRunsRootTests(unittest.TestCase):
    """analyze-claims authenticates the block-5 runs root by the window index, as finalization does."""

    def setUp(self):
        import json
        from joulewise.analysis_engine import inputs
        self.inputs = inputs
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name).resolve()
        self.custody, self.runs, self.other = root / "custody", root / "gamma-runs", root / "other-runs"
        for path in (self.custody, self.runs, self.other):
            path.mkdir()
        (self.custody / "bracket.json").write_text(json.dumps({"runs_root": str(self.runs)}))
        self.manifest = {"schema_version": inputs.ANALYSIS_MANIFEST_FINALIZED_V3_SCHEMA,
                         "evidence": {"bracket_binding": {"path": "bracket.json"}}}
        self.path = self.custody / "am.finalized.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_without_the_index_a_root_outside_custody_still_refuses(self):
        with self.assertRaisesRegex(self.inputs.AnalysisInputError, "escapes custody"):
            self.inputs._finalized_runs_root(self.manifest, self.path, self.runs)

    def test_indexed_root_outside_custody_is_admitted(self):
        self.assertEqual(self.inputs._finalized_runs_root(self.manifest, self.path, self.runs,
                                                          indexed_runs_root=self.runs), self.runs)

    def test_another_root_than_the_indexed_one_refuses(self):
        for supplied, indexed in ((self.other, self.runs), (self.runs, self.other)):
            with self.subTest(supplied=supplied.name, indexed=indexed.name), \
                 self.assertRaisesRegex(self.inputs.AnalysisInputError, "runs_root_not_the_indexed_window"):
                self.inputs._finalized_runs_root(self.manifest, self.path, supplied, indexed_runs_root=indexed)


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
