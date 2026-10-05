"""Real v2 mint -> claim loader regressions for producer plan ownership."""

import copy
import json

from joulewise.detection_floor import complete_bundle_sha256
from tests.fixtures.analysis_v2.binding import (
    load, load_single_producer_v1, MintedAnalysisV2TestCase, single_producer_v1,
)
from tests.fixtures.analysis_v2.binding import write_json


class AnalysisEngineV2BindingTests(MintedAnalysisV2TestCase):
    def test_fixture_minted_v2_aggregate_binds_both_producers(self):
        fixture = self.fixture
        binding = load(fixture).floor_binding
        assert binding.global_problems == ()
        assert binding.bound_cell_ids == frozenset(cell["cell_id"] for cell in fixture.artifact["cells"])
        assert not any("calibration_plan_identity_mismatch" in problem
                       for problems in binding.problems_by_cell.values() for problem in problems)


    def test_other_producer_plan_tag_is_refused(self):
        fixture = self.fixture
        cell = fixture.artifact["cells"][0]
        bundle_id = cell["absolute"]["bundle_observations"][0]["bundle_id"]
        root_id = cell["provenance"]["absolute"]["evidence_root_id"]
        path = fixture.evidence_roots[root_id] / bundle_id / "config.json"
        original = path.read_bytes()
        metadata_path = path.parent / "metadata.json"
        original_metadata = metadata_path.read_bytes()
        original_floor = fixture.floor_path.read_bytes()
        config = json.loads(original)
        other_sha = fixture.artifact["provenance"]["producer_calibration_plans"][1]["sha256"]
        config["run_metadata"]["tags"] = [
            f"calibration-plan-sha256={other_sha}" if tag.startswith("calibration-plan-sha256=") else tag
            for tag in config["run_metadata"]["tags"]
        ]
        try:
            config_sha = write_json(path, config)
            metadata = json.loads(original_metadata)
            metadata["config_sha256"] = config_sha
            write_json(metadata_path, metadata)
            # Keep all byte pins consistent so the only refusal is plan ownership.
            artifact = copy.deepcopy(fixture.artifact)
            bundle_sha = complete_bundle_sha256(path.parent)
            for target in artifact["cells"][:2]:
                row = target["absolute"]["bundle_observations"][0]
                assert row["bundle_id"] == bundle_id
                row.update(config_sha256=config_sha, bundle_sha256=bundle_sha)
                target["provenance"]["absolute"]["bundle_sha256s"][0] = bundle_sha
            write_json(fixture.floor_path, artifact)
            binding = load(fixture).floor_binding
            assert cell["cell_id"] not in binding.bound_cell_ids
            assert binding.problems_by_cell[cell["cell_id"]] == (f"calibration_plan_identity_mismatch: {bundle_id}",)
            assert fixture.artifact["cells"][2]["cell_id"] in binding.bound_cell_ids
        finally:
            path.write_bytes(original)
            metadata_path.write_bytes(original_metadata)
            fixture.floor_path.write_bytes(original_floor)


    def test_each_producer_plan_file_is_hash_checked(self):
        for index in (0, 1):
            with self.subTest(producer=index):
                self._check_producer_plan_hash(index)

    def _check_producer_plan_hash(self, index):
        fixture = self.fixture
        path = fixture.plan_paths[index]
        original = path.read_bytes()
        try:
            path.write_bytes(original + b" ")
            binding = load(fixture).floor_binding
            assert "calibration_plan_bytes_hash_mismatch" in binding.global_problems
            assert not binding.bound_cell_ids
        finally:
            path.write_bytes(original)


    def test_aggregate_canonical_producer_set_is_rechecked(self):
        fixture = self.fixture
        original = fixture.pinset_path.read_bytes()
        pinset = copy.deepcopy(fixture.pinset)
        pinset["producer_plans"][1]["plan"]["declared_sha256"] = "f" * 64
        try:
            write_json(fixture.pinset_path, pinset)
            binding = load(fixture).floor_binding
            assert any(p.startswith("calibration_producer_set_hash_mismatch:") for p in binding.global_problems)
            assert not binding.bound_cell_ids
        finally:
            fixture.pinset_path.write_bytes(original)


    def test_block_must_name_its_cell_producer_plan(self):
        fixture = self.fixture
        original = fixture.floor_path.read_bytes()
        artifact = copy.deepcopy(fixture.artifact)
        block = artifact["cells"][0]["comparative"]["blocks"][0]
        block["calibration_plan_sha256"] = artifact["provenance"]["producer_calibration_plans"][1]["sha256"]
        try:
            write_json(fixture.floor_path, artifact)
            binding = load(fixture).floor_binding
            assert binding.problems_by_cell[artifact["cells"][0]["cell_id"]] == (
                f"calibration_plan_identity_mismatch: {block['block_id']}",)
            assert artifact["cells"][0]["cell_id"] not in binding.bound_cell_ids
            assert artifact["cells"][2]["cell_id"] in binding.bound_cell_ids
        finally:
            fixture.floor_path.write_bytes(original)


    def test_real_v1_mint_preserves_single_plan_and_staged_order_behavior(self):
        with single_producer_v1(self.fixture) as single:
            binding = load_single_producer_v1(self.fixture, single).floor_binding
            assert binding.global_problems == ()
            assert binding.bound_cell_ids == frozenset({single.cell_id})
            assert "producer_calibration_plans" not in single.artifact["provenance"]


class AnalysisEngineLegacyBindingTests(MintedAnalysisV2TestCase):
    folded_artifact = True

    def test_real_folded_v1_mint_binds_stack_and_plan(self):
        with single_producer_v1(self.fixture) as single:
            member = single.source.cells["decode"].absolute.members[0]
            model = member.metadata["workload_provenance"]["model"]["artifact_identity"]
            assert model["kind"] == "file_set"
            assert "sha256" not in model
            cell = single.artifact["cells"][0]
            assert cell["source_regime"]["stack_identity"]["model_artifact_sha256"] == model["folded_sha256"]
            binding = load_single_producer_v1(self.fixture, single).floor_binding
            assert binding.global_problems == ()
            assert binding.bound_cell_ids == frozenset({single.cell_id})
            assert binding.cell_stack_identity_sha256[single.cell_id] == cell["source_regime"]["stack_identity_sha256"]

    def test_real_folded_v1_plan_authentication_stays_in_campaign_seam(self):
        from joulewise.analysis_engine.inputs import _campaign_order_binding_problems

        fixture = self.fixture
        with single_producer_v1(fixture) as single:
            path = fixture.plan_paths[0]
            original = path.read_bytes()
            try:
                path.write_bytes(original + b" ")
                problems = _campaign_order_binding_problems(
                    single.artifact, single.floor_path,
                    {single.producer["evidence_root_id"]: single.source.evidence_root}, {})
                assert problems == ("calibration_plan_bytes_hash_mismatch",)
            finally:
                path.write_bytes(original)

    def test_real_folded_v1_loader_preserves_all_plan_failure_diagnostics(self):
        fixture = self.fixture
        with single_producer_v1(fixture) as single:
            path = fixture.plan_paths[0]
            original = path.read_bytes()
            for raw, secondary in (
                (b"{", "calibration_plan_bytes_invalid"),
                (b"{}", "calibration_plan_declared_provenance_mismatch"),
            ):
                with self.subTest(secondary=secondary):
                    try:
                        path.write_bytes(raw)
                        binding = load_single_producer_v1(fixture, single).floor_binding
                        assert binding.global_problems == (
                            "calibration_plan_bytes_hash_mismatch", secondary)
                        assert not binding.bound_cell_ids
                        assert not any("calibration_plan_identity_mismatch" in p
                                       for p in binding.problems_by_cell[single.cell_id])
                    finally:
                        path.write_bytes(original)
