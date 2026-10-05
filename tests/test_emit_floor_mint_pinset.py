from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from scripts import mint_floor_artifact_generalized as mint
from tests.test_mint_floor_artifact_generalized import freeze_synthetic_v2_pinset

ROOT = Path(__file__).resolve().parents[1]


def contracts_from_pins(pins: dict) -> list[dict]:
    contracts = []
    aggregate = pins["aggregate"]
    for index, producer in enumerate(pins["producer_plans"], 1):
        contracts.append({
            "schema_version": "joulewise.d117_floor_producer_contract.v1",
            "producer_index": index, "plan": copy.deepcopy(producer["plan"]),
            "plan_set_id": aggregate["plan_set_id"], "aggregate_artifact_id": aggregate["artifact_id"],
            "cell_composition_rule": aggregate["cell_composition_rule"],
            "consumer_floor_rule": aggregate["consumer_floor_rule"],
            "component_artifact_id": producer["component_artifact"]["artifact_id"],
            "evidence_root_id": producer["evidence_root_id"],
            "selected_cells": {c["role"]: c["cell_id"] for c in producer["cells"]},
            "roles": [{"role": c["role"], "artifact_cell_id": c["cell_id"],
                       "transport_group_id": c["transport_group_id"], "metric": c["metric"],
                       "target_precheck_path": c["target_precheck_path"],
                       "condition_family_id": c["condition_family_id"],
                       "absolute_calibration_cell_id": c["absolute"]["calibration_cell_id"],
                       "comparative_calibration_cell_id": c["comparative"]["calibration_cell_id"]}
                      for c in producer["cells"]],
        })
    return contracts


class FloorMintEmitterTests(unittest.TestCase):
    def test_emitted_pinset_mints_and_loads_once_registered(self) -> None:
        # No emitter, mint, artifact validator or claim loader is mocked.
        from scripts.emit_floor_mint_pinset import build_pinset, build_input_manifest, _write_pair
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
            original = json.loads(path.read_text())
            issued = root / "issued.json"
            value = build_pinset(contracts=contracts_from_pins(original), producer_inputs=inputs,
                ledger_snapshot=snapshot, relative_plan_paths=[p["plan"]["relative_path"] for p in original["producer_plans"]],
                pinset_path=issued, project_commit="0" * 40)
            # Legacy fixture goldens remain immutable. New pins add the config
            # inventory to provenance, so component hashes necessarily change.
            for actual, expected in zip(value["producer_plans"], original["producer_plans"], strict=True):
                for key in ("plan", "evidence_root_id", "extraction_spec", "calibration_acceptance"):
                    self.assertEqual(actual[key], expected[key])
                for key in ("model_artifact_sha256", "runtime_identity_sha256"):
                    self.assertEqual(actual["model_runtime_config"][key], expected["model_runtime_config"][key])
                self.assertEqual([{k: v for k, v in cell.items() if k != "scientific_config_identity_sha256"}
                                  for cell in actual["cells"]], expected["cells"])
            rows = []
            for producer in original["producer_plans"]:
                plan_id = producer["plan"]["plan_id"]
                source = inputs[plan_id]
                cells = []
                for role, components in source.cells.items():
                    paths = {kind: {"evidence_root": str(source.evidence_root),
                                    "report": str(root / f"{plan_id}-report.json"),
                                    "spec": str(root / f"{plan_id}-spec.json"),
                                    "order_manifest": str(root / f"{plan_id}-order.json")}
                             for kind in ("absolute", "comparative")}
                    cells.append({"role": role, **paths,
                                  "allowed_consumer_condition_families": list(components.allowed_consumer_condition_families)})
                rows.append({"plan_id": plan_id, "calibration_plan": str(root / f"{plan_id}.json"),
                             "calibration_plan_sidecar": str(root / f"{plan_id}.sha256"),
                             "bracket_binding": str(root / f"{plan_id}-binding.json"), "cells": cells})
            manifest = build_input_manifest(acceptance_path=root / "acceptance.json", ledger_path=root / "ledger.jsonl",
                                            head_pin_path=root / "head.json", producer_rows=rows)
            digest = _write_pair(issued, root / "inputs.json", value, manifest)
            self.assertEqual(digest, hashlib.sha256(issued.read_bytes()).hexdigest())
            self.assertEqual(mint._load_v2_input_manifest(root / "inputs.json"), manifest)
            self.assertEqual(manifest["producer_plans"], rows)
            artifact = mint.mint_multi_cell_authenticated_artifact(
                pinset_path=issued, pinset_sha256=digest, producer_inputs=inputs,
                calibration_ledger_snapshot=snapshot, project_commit="0" * 40, project_tree_state="clean")
            floor_path = root / "floor.json"
            floor_path.write_bytes(mint._artifact_payload(artifact))
            # Claim discovery is rooted in a real temporary checkout namespace.
            checkout = root / "claim-checkout"
            shutil.copytree(ROOT / "joulewise", checkout / "joulewise", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(ROOT / "configs/analysis_registry", checkout / "configs/analysis_registry")
            registry = checkout / "scripts" / "floor_mint_pinsets"
            registry.mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/floor_mint_pinsets/schema_v2.json", registry)
            command = [sys.executable, "-B", "-c",
                "from pathlib import Path; import sys; from joulewise.analysis_engine.inputs import load_floor_artifact; "
                "print(load_floor_artifact(Path(sys.argv[1])).value['artifact_id'])", str(floor_path)]
            refused = subprocess.run(command, cwd=checkout, capture_output=True, text=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("no pinset matches artifact family identity", refused.stderr)
            shutil.copy2(issued, registry / "fixture-issued.json")
            loaded = subprocess.run(command, cwd=checkout, capture_output=True, text=True)
            self.assertEqual(loaded.returncode, 0, loaded.stdout + loaded.stderr)
            self.assertEqual(loaded.stdout.strip(), artifact["artifact_id"])

    def test_output_pair_is_exclusive_and_does_not_replace_a_pin(self) -> None:
        from scripts.emit_floor_mint_pinset import _write_pair
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "pins.json"
            existing.write_bytes(b"preserved\n")
            with self.assertRaisesRegex(mint.MintError, "distinct absent"):
                _write_pair(existing, root / "inputs.json", {}, {})
            self.assertEqual(existing.read_bytes(), b"preserved\n")
            self.assertFalse((root / "inputs.json").exists())
            with self.assertRaises(OSError):
                _write_pair(root / "new.json", root / "missing" / "inputs.json", {}, {})
            self.assertFalse((root / "new.json").exists())

    def test_contract_drift_refuses_without_an_artifact(self) -> None:
        from scripts.emit_floor_mint_pinset import build_pinset
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
            pins = json.loads(path.read_text())
            contracts = contracts_from_pins(pins)
            contracts[1]["plan_set_id"] = "different-set"
            with self.assertRaisesRegex(mint.MintError, "source pin mismatch"):
                build_pinset(contracts=contracts, producer_inputs=inputs, ledger_snapshot=snapshot,
                             relative_plan_paths=[p["plan"]["relative_path"] for p in pins["producer_plans"]],
                             pinset_path=root / "issued.json", project_commit="0" * 40)
            self.assertFalse((root / "issued.json").exists())

    def test_bootstrap_refuses_changed_plan_bytes_from_real_v5_pack(self) -> None:
        from scripts.emit_floor_mint_pinset import _bootstrap_producer
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "pack"
            shutil.copytree(ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5", pack)
            plan = pack / "calibration_plan.json"
            plan.write_bytes(plan.read_bytes() + b"\n")
            with self.assertRaisesRegex(mint.MintError, "plan sidecar: source pin mismatch"):
                _bootstrap_producer(pack, root / "runs", root / "report.json", root / "bracket.json",
                                    {}, {}, "0" * 64, None, "alpha/calibration_plan.json", "prefill_p2048")
            self.assertFalse((root / "issued.json").exists())

    def test_v5_decode_and_p2048_inventory_mints_under_the_lead_ruling(self) -> None:
        from scripts.emit_floor_mint_pinset import build_pinset
        from joulewise.identity_pins import scientific_config_identity_sha256
        pack_names = ("d117_floor_qwen3-1p7b_v5", "d117_floor_qwen3-8b_v5")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
            pins = json.loads(path.read_text())
            for producer, pack_name in zip(pins["producer_plans"], pack_names, strict=True):
                pack = ROOT / "configs/campaigns" / pack_name
                contract = json.loads((pack / "producer_contract.json").read_text())
                tree = json.loads((pack / "plan_tree.json").read_text())
                configs = {r["run_id"]: r["config_path"] for r in tree["science"]}
                hashes = {}
                for role in contract["roles"]:
                    if role["role"] in ("decode", "prefill_p2048"):
                        config = json.loads((ROOT / configs[role["members"][0]["bundle_id"]]).read_text())
                        hashes[role["role"]] = scientific_config_identity_sha256(config)
                self.assertNotEqual(hashes["decode"], hashes["prefill_p2048"])
                plan_id = producer["plan"]["plan_id"]
                source = inputs[plan_id]
                updated = {}
                for role, cell in source.cells.items():
                    digest = hashes["decode" if role == "decode" else "prefill_p2048"]
                    updated[role] = replace(cell,
                        absolute=replace(cell.absolute, scientific_config_identity_sha256=digest),
                        comparative=replace(cell.comparative, scientific_config_identity_sha256=digest))
                inputs[plan_id] = replace(source, cells=updated)
            value = build_pinset(contracts=contracts_from_pins(pins), producer_inputs=inputs,
                ledger_snapshot=snapshot, relative_plan_paths=[p["plan"]["relative_path"] for p in pins["producer_plans"]],
                pinset_path=root / "issued.json", project_commit="0" * 40)
            for producer in value["producer_plans"]:
                source = inputs[producer["plan"]["plan_id"]]
                for cell in producer["cells"]:
                    self.assertEqual(cell["scientific_config_identity_sha256"],
                                     source.cells[cell["role"]].absolute.scientific_config_identity_sha256)
            self.assertFalse((root / "issued.json").exists())

    def test_emitted_document_conforms_to_schema_v2_when_available(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("optional jsonschema dependency is absent")
        from scripts.emit_floor_mint_pinset import build_pinset
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
            original = json.loads(path.read_text())
            value = build_pinset(contracts=contracts_from_pins(original), producer_inputs=inputs,
                ledger_snapshot=snapshot, relative_plan_paths=[p["plan"]["relative_path"] for p in original["producer_plans"]],
                pinset_path=root / "issued.json", project_commit="0" * 40)
            schema = json.loads((ROOT / "scripts/floor_mint_pinsets/schema_v2.json").read_text())
            jsonschema.Draft202012Validator(schema).validate(value)


if __name__ == "__main__":
    unittest.main()
