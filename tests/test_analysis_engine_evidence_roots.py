"""Each floor producer uses its own runs root and pinned pack order bytes."""

from tests.fixtures.analysis_v2.binding import ROOT_IDS, load, MintedAnalysisV2TestCase


class AnalysisEngineEvidenceRootsTests(MintedAnalysisV2TestCase):
    def test_pack_order_manifest_binds_without_runs_root_copy(self):
        for root_id in ROOT_IDS:
            with self.subTest(evidence_root_id=root_id):
                self._check_pack_order_manifest(root_id)

    def _check_pack_order_manifest(self, root_id):
        fixture = self.fixture
        assert not (fixture.evidence_roots[root_id] / "order_manifest.json").exists()
        binding = load(fixture).floor_binding
        for cell in fixture.artifact["cells"]:
            if cell["provenance"]["absolute"]["evidence_root_id"] == root_id:
                assert cell["cell_id"] in binding.bound_cell_ids, binding.problems_by_cell[cell["cell_id"]]


    def test_pinned_pack_order_sha_checked_even_with_valid_runs_root_copy(self):
        for index in (0, 1):
            with self.subTest(producer=index):
                self._check_pinned_order_sha(index)

    def _check_pinned_order_sha(self, index):
        fixture = self.fixture
        path = fixture.order_paths[index]
        original = path.read_bytes()
        staged = fixture.evidence_roots[ROOT_IDS[index]] / "order_manifest.json"
        try:
            staged.write_bytes(original)
            path.write_bytes(original + b" ")
            binding = load(fixture).floor_binding
            assert not binding.bound_cell_ids
            assert any("order_manifest sha256 mismatch" in p for p in binding.global_problems)
        finally:
            path.write_bytes(original)
            staged.unlink()


    def test_contrast_root_does_not_supply_floor_producer_mapping(self):
        fixture = self.fixture
        from joulewise.analysis_engine.inputs import load_analysis_inputs

        binding = load_analysis_inputs(
            fixture.manifest_path, fixture.analysis_root, fixture.floor_path,
            strict_validator=fixture.strict_validator,
            evidence_roots={"evidence-d117-contrast-qwen3-1p7b-vs-qwen3-8b-v5": fixture.analysis_root},
            calibration_ledger_snapshot=fixture.snapshot,
        ).floor_binding
        assert not binding.bound_cell_ids
        for root_id in ROOT_IDS:
            assert f"missing_evidence_root_mapping: {root_id!r}" in binding.global_problems
