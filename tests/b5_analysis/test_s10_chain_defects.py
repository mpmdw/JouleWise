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


class OrderManifestBesidePlanCopyTests(unittest.TestCase):
    """C9: the claim gate's floor binder resolves each producer plan copy's order
    manifest beside it (multi-producer branch); the indexed emitter wrote only the
    plan copies, so every floor cell refused component_evidence_root_disagreement
    (producer order manifest path_resolution_refused) and no contrast floor resolved."""

    def test_emitter_writes_each_order_manifest_where_the_binder_resolves_it(self):
        import json
        from scripts import emit_floor_mint_pinset as emit
        from joulewise.analysis_engine import inputs as ai
        with tempfile.TemporaryDirectory(prefix="s10-order-") as tmp:
            out = Path(tmp) / "mint"
            out.mkdir()
            plans = {p: json.dumps({"order_manifest": "order_manifest.json", "pack": p}).encode() for p in ("alpha", "beta")}
            orders = {p: json.dumps({"executed_order": [{"run_id": p + "-r01"}]}).encode() for p in plans}
            emit._write_block5_outputs(out, {"pins": "synthetic"}, {"inputs": "synthetic"}, plans, orders)
            for pack in plans:
                resolved = ai._lexical_child_path(out / pack, json.loads(plans[pack])["order_manifest"],
                                                  label="producer order manifest", require_directory=False)
                self.assertEqual(resolved.read_bytes(), orders[pack])

    def test_order_manifests_must_cover_both_plans(self):
        from scripts import emit_floor_mint_pinset as emit, mint_floor_artifact_generalized as mint
        with tempfile.TemporaryDirectory(prefix="s10-order-") as tmp:
            with self.assertRaises(mint.MintError):
                emit._write_block5_outputs(Path(tmp), {}, {}, {"alpha": b"{}", "beta": b"{}"}, {"alpha": b"{}"})
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_indexed_emitter_hands_the_order_manifests_to_the_writer(self):
        import inspect
        from scripts import emit_floor_mint_pinset as emit
        source = inspect.getsource(emit.emit_indexed_pinset)
        self.assertIn("_write_block5_outputs(out_dir, value, manifest, plans, orders)", source)


class ClaimCustodyManifestRootTests(unittest.TestCase):
    """Joined run, step 9b: the claim-evidence custody gate validated the finalized
    manifest with the custody's runs root as its custody root, while the driver
    finalizes into its own subdirectory (restricted/finalized), so every attachment
    path missed; the refusals were records, not codes, and surfaced as
    paper_custody_not_issuable."""

    def gate(self, refusals):
        import json
        from joulewise import paper_custody as c
        from joulewise import analysis_manifest_v3 as v3
        from joulewise.authentication_io import V2AuthenticationReadSession
        seen = {}
        with tempfile.TemporaryDirectory(prefix="s10-claim-custody-") as tmp:
            runs = Path(tmp) / "restricted"
            (runs / "finalized").mkdir(parents=True)
            binding = c._BoundFile("runs_root", Path("finalized/am-x.finalized.json"), "0" * 64,
                                   c.InputRole.FINALIZED_MANIFEST, "generated")
            raws = {c.InputRole.FINALIZED_MANIFEST: b"{}", c.InputRole.CLAIM_VERDICTS: json.dumps({"inputs": {}}).encode(),
                    c.InputRole.FLOOR_ARTIFACT: b"{}", c.InputRole.CLAIM_SIDE_BOUND: b"{}"}
            ctx = c._GateContext("claim_evidence", "production.claim_evidence.gamma.v5", "production", "claim-evidence.v1",
                                 ("ctr",), Path(tmp) / "repository", runs, "a" * 40, (binding,), (), raws,
                                 V2AuthenticationReadSession())

            def validate(manifest, **kwargs):
                seen.update(kwargs)
                return refusals

            from joulewise.analysis_engine import artifact, claim_side_bound
            with mock.patch.object(v3, "validate_finalized_analysis_manifest_v3", validate), \
                 mock.patch.object(artifact, "validate_claim_verdicts", return_value=()), \
                 mock.patch.object(claim_side_bound, "validate_claim_side_bound", return_value=()):
                replay = c._claim_issuance_gate(ctx)
            return replay, seen, runs

    def test_manifest_is_validated_in_its_own_custody_root(self):
        replay, seen, runs = self.gate(())
        self.assertEqual(seen["custody_root"], runs / "finalized")
        self.assertEqual(seen["manifest_path"], runs / "finalized" / "am-x.finalized.json")

    def test_block5_verdict_replay_authenticates_the_floor_with_its_sibling_pinset(self):
        # Joined run, step 9b, next refusal: validate_claim_verdicts authenticated the
        # embedded block-5 floor against the registered pinsets only.
        import json
        from joulewise import paper_custody as c
        from joulewise import analysis_manifest_v3 as v3
        from joulewise.analysis_engine import artifact, claim_side_bound, inputs
        from joulewise.authentication_io import V2AuthenticationReadSession
        seen = {}
        with tempfile.TemporaryDirectory(prefix="s10-claim-pinset-") as tmp:
            runs = Path(tmp) / "restricted"
            (runs / "mint").mkdir(parents=True)
            manifest = c._BoundFile("runs_root", Path("finalized/am-x.finalized.json"), "0" * 64,
                                    c.InputRole.FINALIZED_MANIFEST, "generated")
            floor = c._BoundFile("runs_root", Path("mint/d-aggregate-floor.json"), "0" * 64,
                                 c.InputRole.FLOOR_ARTIFACT, "generated")
            raws = {c.InputRole.FINALIZED_MANIFEST: b"{}", c.InputRole.CLAIM_VERDICTS: json.dumps({"inputs": {}}).encode(),
                    c.InputRole.FLOOR_ARTIFACT: b"{}", c.InputRole.CLAIM_SIDE_BOUND: b"{}",
                    c.InputRole.CLAIM_REPLAY_REQUEST: b"{}"}
            ctx = c._GateContext("claim_evidence", "production.claim_evidence.gamma.v5", "production", "claim-evidence.v1",
                                 ("ctr",), Path(tmp) / "repository", runs, "a" * 40, (manifest, floor), (), raws,
                                 V2AuthenticationReadSession())
            sibling = runs / "mint" / "floor-mint-pinset.json"

            def verdicts(value, **kwargs):
                seen.update(kwargs)
                return []

            with mock.patch.object(v3, "validate_finalized_analysis_manifest_v3", return_value=()), \
                 mock.patch.object(inputs, "sibling_floor_pinset", side_effect=lambda path: (seen.setdefault("floor", path), sibling)[1]), \
                 mock.patch.object(artifact, "validate_claim_verdicts", verdicts), \
                 mock.patch.object(claim_side_bound, "validate_claim_side_bound", return_value=()):
                c._claim_issuance_gate(ctx)
        self.assertEqual(seen["floor"], runs / "mint" / "d-aggregate-floor.json")
        self.assertEqual(seen["floor_pinset_path"], sibling)

    def test_block5_manifest_replay_runs_outside_the_custody_read_session(self):
        # Joined run, step 9b, next refusal (paper_custody_binding_mismatch): the
        # window-index replay of the finalized manifest read about 3,000 archive and
        # bundle files inside the custody session, outside the census. Like the claim
        # replay, it now runs in a fresh context; the owner's own reads stay bound.
        import json
        from joulewise import paper_custody as c, authentication_io as aio
        from joulewise import analysis_manifest_v3 as v3
        from joulewise.analysis_engine import artifact, claim_side_bound, inputs
        observed = []
        with tempfile.TemporaryDirectory(prefix="s10-claim-session-") as tmp:
            runs = Path(tmp) / "restricted"
            manifest = c._BoundFile("runs_root", Path("finalized/am-x.finalized.json"), "0" * 64,
                                    c.InputRole.FINALIZED_MANIFEST, "generated")
            floor = c._BoundFile("runs_root", Path("mint/d-aggregate-floor.json"), "0" * 64,
                                 c.InputRole.FLOOR_ARTIFACT, "generated")
            raws = {c.InputRole.FINALIZED_MANIFEST: b"{}", c.InputRole.CLAIM_VERDICTS: json.dumps({"inputs": {}}).encode(),
                    c.InputRole.FLOOR_ARTIFACT: b"{}", c.InputRole.CLAIM_SIDE_BOUND: b"{}",
                    c.InputRole.CLAIM_REPLAY_REQUEST: b"{}"}
            session = aio.V2AuthenticationReadSession()
            ctx = c._GateContext("claim_evidence", "production.claim_evidence.gamma.v5", "production", "claim-evidence.v1",
                                 ("ctr",), Path(tmp) / "repository", runs, "a" * 40, (manifest, floor), (), raws, session)

            def validate(value, **kwargs):
                observed.append(aio._ACTIVE_SESSION.get())
                return ()

            with mock.patch.object(v3, "validate_finalized_analysis_manifest_v3", validate), \
                 mock.patch.object(inputs, "sibling_floor_pinset", return_value=runs / "mint" / "floor-mint-pinset.json"), \
                 mock.patch.object(artifact, "validate_claim_verdicts", return_value=[]), \
                 mock.patch.object(claim_side_bound, "validate_claim_side_bound", return_value=()), session:
                self.assertIs(aio._ACTIVE_SESSION.get(), session)
                c._claim_issuance_gate(ctx)
        self.assertEqual(observed, [None])

    def test_claim_replay_loads_the_block5_floor_with_its_sibling_pinset(self):
        # Joined run, step 9b, next refusal (claim_verdicts_replay_refused): the replay
        # read the floor's evidence roots through the registered pinsets only.
        import hashlib
        from types import SimpleNamespace
        from joulewise import paper_custody as c
        from joulewise.analysis_engine import inputs
        from joulewise.b5_analysis import windows, archive
        from joulewise.authentication_io import V2AuthenticationReadSession
        calls = []
        with tempfile.TemporaryDirectory(prefix="s10-claim-replay-") as tmp:
            runs = Path(tmp) / "restricted"
            manifest = c._BoundFile("runs_root", Path("finalized/am-x.finalized.json"), "0" * 64,
                                    c.InputRole.FINALIZED_MANIFEST, "generated")
            floor = c._BoundFile("runs_root", Path("mint/d-aggregate-floor.json"), "0" * 64,
                                 c.InputRole.FLOOR_ARTIFACT, "generated")
            raws = {c.InputRole.FINALIZED_MANIFEST: b"{}", c.InputRole.CLAIM_VERDICTS: b"{}", c.InputRole.FLOOR_ARTIFACT: b"{}"}
            ctx = c._GateContext("claim_evidence", "production.claim_evidence.gamma.v5", "production", "claim-evidence.v1",
                                 ("ctr",), Path(tmp) / "repository", runs, "a" * 40, (manifest, floor), (), raws,
                                 V2AuthenticationReadSession())
            digest = hashlib.sha256(b"{}").hexdigest()
            request = {"claim_verdicts_sha256": digest, "analysis_manifest_sha256": digest, "floor_artifact_sha256": digest,
                       "window_index_sha256": hashlib.sha256(b"index").hexdigest(), "evidence_roots": {"root-a": "alpha"}}

            def load(path, *, require_sibling_pinset=False):
                calls.append((Path(path), require_sibling_pinset))
                return SimpleNamespace(file_sha256=digest, root_ids={"root-other"})

            with mock.patch.object(c, "_check_claim_replay_request"), \
                 mock.patch.object(c, "_tracked_window_index", return_value=Path(tmp) / "index.json"), \
                 mock.patch.object(c, "_git_blob", return_value=b"index"), \
                 mock.patch.object(windows, "load_window_index", return_value=SimpleNamespace(entries=())), \
                 mock.patch.object(archive, "open_attempt_record"), \
                 mock.patch.object(windows, "select_analysed_attempts", return_value={}), \
                 mock.patch.object(inputs, "load_floor_artifact", side_effect=load), \
                 self.assertRaises(c._ClaimReplayRefused):
                c._replay_claim_verdicts(ctx, request)
        self.assertEqual(calls, [(runs / "mint" / "d-aggregate-floor.json", True)])

    def test_manifest_refusals_become_reason_codes(self):
        from joulewise.analysis_manifest_v3 import ManifestRefusal
        replay, _seen, _runs = self.gate((ManifestRefusal("analysis_manifest_lineage_mismatch", "synthetic"),))
        self.assertFalse(replay.authentic)
        self.assertIn("analysis_manifest_lineage_mismatch", replay.validator_codes)
        self.assertTrue(all(type(code) is str for code in replay.validator_codes))


class PaperSourcesBlockFiveFloorTests(unittest.TestCase):
    """Joined run, step 6: the close-out's paper-source replay authenticated the block-5
    aggregate floor against the registered pinsets only, which name no block-5 floor, and
    refused d165_closeout_driver_paper_sources_invalid (d165_paper_floor_artifact_invalid)."""

    def check(self, *, floor_bytes=None, window_index=True):
        import hashlib
        import json
        from types import SimpleNamespace
        from joulewise import dominance_closeout as dc
        with tempfile.TemporaryDirectory(prefix="s10-paper-floor-") as tmp:
            root = Path(tmp)
            floor = root / "mint" / "x-aggregate-floor.json"
            floor.parent.mkdir()
            floor.write_bytes(b'{"floor": "synthetic"}\n')
            manifest = {"evidence": {"aggregate_floor_artifact": {"path": "mint/x-aggregate-floor.json"}}}
            seen = []

            def load(path, *, require_sibling_pinset=False):
                seen.append(("sibling", Path(path), require_sibling_pinset))
                return SimpleNamespace(file_sha256=hashlib.sha256(floor.read_bytes()).hexdigest())

            def registered_only(raw):
                seen.append(("registered",))
                raise dc.AnalysisInputError("invalid floor artifact: artifact.pinset: no pinset matches artifact family identity")

            with mock.patch.object(dc, "load_floor_artifact", load), \
                 mock.patch.object(dc, "authenticate_floor_artifact_bytes", registered_only), \
                 mock.patch.object(dc, "validate_finalized_analysis_manifest_v3", return_value=()), \
                 mock.patch.object(dc, "validate_d165_replay_sidecar", return_value=()), \
                 mock.patch.object(dc, "validate_d165_closeout", return_value=()):
                codes = dc.validate_d165_paper_sources(
                    closeout={}, finalized_manifest_bytes=json.dumps(manifest).encode(),
                    finalized_manifest_path=root / "am.finalized.json", custody_root=root,
                    floor_artifact_bytes=floor.read_bytes() if floor_bytes is None else floor_bytes,
                    replay_sidecar_bytes=b"{}", window_index=root / "index.json" if window_index else None)
            return codes, seen, floor

    def test_block5_floor_authenticates_against_its_sibling_pinset(self):
        codes, seen, floor = self.check()
        self.assertEqual(codes, ())
        self.assertEqual(seen, [("sibling", floor, True)])

    def test_block5_other_bytes_than_the_attachment_refuse(self):
        codes, _seen, _floor = self.check(floor_bytes=b'{"floor": "other"}\n')
        self.assertIn("d165_paper_floor_artifact_invalid", codes)

    def test_without_a_window_index_the_registered_pinset_path_is_unchanged(self):
        codes, seen, _floor = self.check(window_index=False)
        self.assertEqual(seen, [("registered",)])
        self.assertIn("d165_paper_floor_artifact_invalid", codes)


if __name__ == "__main__":
    unittest.main()
