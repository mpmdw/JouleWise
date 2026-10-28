"""Runtime inventories bind each execution path to its own cell pin."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from joulewise import detection_floor
from scripts import emit_floor_mint_pinset as emitter
from scripts import mint_floor_artifact_generalized as mint
from tests.test_emit_floor_mint_pinset import contracts_from_pins
from tests.test_mint_floor_artifact_generalized import (
    _repair_v2_pinset_self_hashes, freeze_synthetic_v2_pinset,
)


def set_digest(values):
    return hashlib.sha256(json.dumps(sorted(set(values)), separators=(",", ":")).encode()).hexdigest()


class RuntimeIdentityCellTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        path, _, self.inputs, self.snapshot = freeze_synthetic_v2_pinset(self.root)
        self.legacy = json.loads(path.read_text())

    def per_cell(self, *, two_runtimes=True):
        pins = copy.deepcopy(self.legacy)
        inputs = dict(self.inputs)
        for producer in pins["producer_plans"]:
            plan_id = producer["plan"]["plan_id"]
            source = inputs[plan_id]
            cells = dict(source.cells)
            for cell in producer["cells"]:
                role = cell["role"]
                if two_runtimes and role == "prefill":
                    components = {}
                    for kind in ("absolute", "comparative"):
                        component = getattr(cells[role], kind)
                        regime = copy.deepcopy(component.source_regime)
                        regime["stack_identity"]["sampler_output_policy"] = {
                            "sampler": "synthetic", "output_policy": {"stop_condition": "requested_tokens_emitted"}}
                        components[kind] = replace(component, source_regime=regime)
                    cells[role] = replace(cells[role], **components)
                component = cells[role].absolute
                cell["scientific_config_identity_sha256"] = component.scientific_config_identity_sha256
                cell["runtime_identity_sha256"] = mint.derive_model_runtime_config(
                    component.source_regime["stack_identity"], component.scientific_config_identity_sha256
                )["runtime_identity_sha256"]
            producer["model_runtime_config"]["config_set_sha256"] = set_digest(
                [c["scientific_config_identity_sha256"] for c in producer["cells"]])
            producer["model_runtime_config"]["runtime_identity_sha256"] = set_digest(
                [c["runtime_identity_sha256"] for c in producer["cells"]])
            inputs[plan_id] = replace(source, cells=cells)
        _repair_v2_pinset_self_hashes(pins)
        return pins, inputs

    def test_R1_two_runtime_cells_pass_inventory(self):
        pins, inputs = self.per_cell()
        mint._parse_v2_pinset(pins)
        self.assertIsNotNone(detection_floor._project_floor_mint_pinset_v2(pins))
        for producer in pins["producer_plans"]:
            self.assertNotEqual(*[c["runtime_identity_sha256"] for c in producer["cells"]])
            mint._v2_gate_producer_inventory(producer, inputs[producer["plan"]["plan_id"]])

    def test_R2_wrong_cell_pin_refuses_inventory(self):
        pins, inputs = self.per_cell()
        producer = pins["producer_plans"][0]
        producer["cells"][1]["runtime_identity_sha256"] = producer["cells"][0]["runtime_identity_sha256"]
        producer["model_runtime_config"]["runtime_identity_sha256"] = set_digest(
            [c["runtime_identity_sha256"] for c in producer["cells"]])
        with self.assertRaisesRegex(mint.MintError, "runtime identity inventory mismatch"):
            mint._v2_gate_producer_inventory(producer, inputs[producer["plan"]["plan_id"]])

    def test_R3_wrong_producer_set_refuses(self):
        pins, inputs = self.per_cell()
        producer = pins["producer_plans"][0]
        producer["model_runtime_config"]["runtime_identity_sha256"] = "0" * 64
        with self.assertRaisesRegex(mint.MintError, "runtime.*set"):
            mint._v2_gate_producer_inventory(producer, inputs[producer["plan"]["plan_id"]])

    def test_R4_partial_and_invalid_runtime_keys_refuse_shape(self):
        pins, _ = self.per_cell()
        for attack in ("missing", "no_config", "uppercase", "null"):
            with self.subTest(attack=attack):
                candidate = copy.deepcopy(pins)
                cell = candidate["producer_plans"][0]["cells"][1]
                if attack == "missing":
                    del cell["runtime_identity_sha256"]
                elif attack == "no_config":
                    del cell["scientific_config_identity_sha256"]
                else:
                    cell["runtime_identity_sha256"] = "A" * 64 if attack == "uppercase" else None
                _repair_v2_pinset_self_hashes(candidate)
                with self.assertRaises(mint.MintError):
                    mint._parse_v2_pinset(candidate)
                self.assertIsNone(detection_floor._project_floor_mint_pinset_v2(candidate))
                try:
                    import jsonschema
                except ImportError:
                    continue
                schema = json.loads((emitter.REPO_ROOT / "scripts/floor_mint_pinsets/schema_v2.json").read_text())
                self.assertTrue(list(jsonschema.Draft202012Validator(schema).iter_errors(candidate)))

    def test_R5_legacy_and_existing_config_cells_keep_single_runtime_rule(self):
        for per_config in (False, True):
            with self.subTest(per_config=per_config):
                if per_config:
                    pins, inputs = self.per_cell(two_runtimes=False)
                    for producer in pins["producer_plans"]:
                        for cell in producer["cells"]:
                            del cell["runtime_identity_sha256"]
                        producer["model_runtime_config"]["runtime_identity_sha256"] = next(
                            p["model_runtime_config"]["runtime_identity_sha256"] for p in self.legacy["producer_plans"]
                            if p["plan"]["plan_id"] == producer["plan"]["plan_id"])
                    _repair_v2_pinset_self_hashes(pins)
                else:
                    pins, inputs = self.legacy, self.inputs
                mint._parse_v2_pinset(pins)
                for producer in pins["producer_plans"]:
                    mint._v2_gate_producer_inventory(producer, inputs[producer["plan"]["plan_id"]])
                _, different = self.per_cell()
                producer = pins["producer_plans"][0]
                with self.assertRaisesRegex(mint.MintError, "runtime identity inventory mismatch"):
                    mint._v2_gate_producer_inventory(producer, different[producer["plan"]["plan_id"]])

    def test_R6_nonindexed_builder_emits_each_runtime_and_set(self):
        _, inputs = self.per_cell()
        issued = emitter.build_pinset(contracts=contracts_from_pins(self.legacy), producer_inputs=inputs,
            ledger_snapshot=self.snapshot, relative_plan_paths=[p["plan"]["relative_path"] for p in self.legacy["producer_plans"]],
            pinset_path=self.root / "issued.json", project_commit="0" * 40)
        for producer in issued["producer_plans"]:
            source = inputs[producer["plan"]["plan_id"]]
            values = []
            for cell in producer["cells"]:
                component = source.cells[cell["role"]].absolute
                expected = mint.derive_model_runtime_config(component.source_regime["stack_identity"],
                    component.scientific_config_identity_sha256)["runtime_identity_sha256"]
                self.assertEqual(cell["runtime_identity_sha256"], expected)
                values.append(expected)
            self.assertEqual(producer["model_runtime_config"]["runtime_identity_sha256"], set_digest(values))

    def test_shared_set_encoding(self):
        values = ["b" * 64, "a" * 64, "b" * 64]
        self.assertEqual(detection_floor.floor_mint_runtime_set_sha256(values), set_digest(values))
        self.assertEqual(detection_floor.floor_mint_runtime_set_sha256(values), detection_floor.floor_mint_config_set_sha256(values))

    def test_builder_refuses_different_cell_model_artifacts(self):
        _, inputs = self.per_cell()
        plan_id = self.legacy["producer_plans"][0]["plan"]["plan_id"]
        source = inputs[plan_id]
        cell = source.cells["prefill"]
        regime = copy.deepcopy(cell.absolute.source_regime)
        regime["stack_identity"]["model_artifact_sha256"] = "f" * 64
        inputs[plan_id] = replace(source, cells={**source.cells,
            "prefill": replace(cell, absolute=replace(cell.absolute, source_regime=regime))})
        with self.assertRaisesRegex(mint.MintError, "producer model artifact"):
            emitter.build_pinset(contracts=contracts_from_pins(self.legacy), producer_inputs=inputs,
                ledger_snapshot=self.snapshot, relative_plan_paths=[p["plan"]["relative_path"] for p in self.legacy["producer_plans"]],
                pinset_path=self.root / "issued.json", project_commit="0" * 40)

class MintLaunchLineageReaderTests(unittest.TestCase):
    def hazard_lineage(self):
        from joulewise.window_lineage import HAZARD_LINEAGE_SCHEMA
        return {'schema_version':HAZARD_LINEAGE_SCHEMA,
            'collection_boot_session_id':'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
            'pack_id':'synthetic-floor-pack','plan_id':'synthetic-floor-plan',
            'window_id':'synthetic-window','bracket_session_id':'synthetic-bracket',
            'pack_root':'/synthetic/pack','pack_sha256':'a'*64,'plan_tree_sha256':'a'*64,
            'window_context':{'claim_runs_root':'/synthetic/claim','bound_runs_root':'/synthetic/bound',
                'custody_root':'/synthetic/custody','night_dir':'/synthetic/night',
                'pre_attempt_id':'synthetic-pre','post_attempt_id':'synthetic-post'},
            'launch_record':{'path':'/synthetic/launch.json','sha256':'b'*64}}

    def test_hazard_floor_lineage_routes_to_its_existing_shape_validator(self):
        from joulewise import detection_floor,window_lineage
        lineage=self.hazard_lineage()
        self.assertEqual(window_lineage.validate_lineage(lineage),lineage)
        errors=[]
        detection_floor._validate_launch_lineage_provenance(lineage,'artifact.provenance.launch_lineage',errors)
        self.assertEqual(errors,[])

    def test_hazard_floor_lineage_keeps_closed_keys_and_reference_checks(self):
        from joulewise import detection_floor
        for attack in ('extra','digest','relative'):
            with self.subTest(attack=attack):
                lineage=self.hazard_lineage()
                if attack=='extra':lineage['extra']=True
                elif attack=='digest':lineage['launch_record']['sha256']='invalid'
                else:lineage['launch_record']['path']='relative.json'
                errors=[]
                detection_floor._validate_launch_lineage_provenance(lineage,'artifact.provenance.launch_lineage',errors)
                self.assertTrue(errors)

    def test_distinct_window_lineages_document_aggregate_rule_boundary(self):
        from scripts import mint_floor_artifact_generalized as mint
        from joulewise.window_lineage import validate_lineage
        alpha=self.hazard_lineage();beta=self.hazard_lineage()
        beta.update(pack_id='synthetic-beta-pack',plan_id='synthetic-beta-plan',window_id='synthetic-beta-window')
        for lineage in (alpha,beta):validate_lineage(lineage)
        artifacts=[{'provenance':{'launch_lineage':lineage}} for lineage in (alpha,beta)]
        with self.assertRaisesRegex(mint.MintError,
                'launch_lineage_conflict: aggregate components does not carry one authenticated lineage'):
            mint._common_minted_artifact_launch_lineage(artifacts,label='aggregate components')

    def test_component_transport_retains_source_family_beside_consumer_pins(self):
        import copy
        from scripts import emit_floor_mint_pinset as emit,mint_floor_artifact_generalized as mint
        from tests.test_mint_floor_artifact_generalized import freeze_synthetic_v2_pinset
        from tests.test_emit_floor_mint_pinset import contracts_from_pins
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            path,_,inputs,snapshot=freeze_synthetic_v2_pinset(root)
            original=json.loads(path.read_text())
            for plan_id,source in list(inputs.items()):
                cells={}
                for role,cell in source.cells.items():
                    consumer=copy.deepcopy(cell.allowed_consumer_condition_families[0])
                    consumer['condition_family_id']='consumer-'+consumer['condition_family_id']
                    cells[role]=replace(cell,allowed_consumer_condition_families=(consumer,))
                inputs[plan_id]=replace(source,cells=cells)
            issued=root/'issued.json'
            value=emit.build_pinset(contracts=contracts_from_pins(original),producer_inputs=inputs,
                ledger_snapshot=snapshot,relative_plan_paths=[p['plan']['relative_path'] for p in original['producer_plans']],
                pinset_path=issued,project_commit='0'*40)
            raw=mint._artifact_payload(value);issued.write_bytes(raw)
            import hashlib
            artifact=mint.mint_multi_cell_authenticated_artifact(pinset_path=issued,
                pinset_sha256=hashlib.sha256(raw).hexdigest(),producer_inputs=inputs,
                calibration_ledger_snapshot=snapshot,project_commit='0'*40,project_tree_state='clean')
            for cell,group in zip(artifact['cells'],artifact['transport_groups'],strict=True):
                ids=[f['condition_family_id'] for f in group['allowed_consumer_condition_families']]
                self.assertEqual(ids,[cell['key']['condition_family_id'],'consumer-'+cell['key']['condition_family_id']])


