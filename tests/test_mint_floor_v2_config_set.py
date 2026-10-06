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

from joulewise import detection_floor
from joulewise.identity_pins import scientific_config_identity_sha256
from scripts import emit_floor_mint_pinset as emitter
from scripts import mint_floor_artifact_generalized as mint
from tests.test_emit_floor_mint_pinset import ROOT, contracts_from_pins
from tests.test_mint_floor_artifact_generalized import (
    SYNTHETIC_COMPONENT_SHA256S,
    _repair_v2_pinset_self_hashes,
    freeze_synthetic_v2_pinset,
)

PACK_NAMES = ("d117_floor_qwen3-1p7b_v5", "d117_floor_qwen3-8b_v5")


def config_set_hash(hashes):
    # Independent wire oracle: no production hashing helper.
    return hashlib.sha256(json.dumps(sorted(set(hashes)), separators=(",", ":")).encode()).hexdigest()


def registered_v5_hashes():
    result = []
    for name in PACK_NAMES:
        pack = ROOT / "configs/campaigns" / name
        tree = json.loads((pack / "plan_tree.json").read_text())
        contract = json.loads((pack / "producer_contract.json").read_text())
        science = {row["run_id"]: row for row in tree["science"]}
        hashes = {}
        for role in ("decode", "prefill_p2048"):
            mapping = next(row for row in contract["roles"] if row["role"] == role)
            observed = set()
            for member in mapping["members"]:
                row = science[member["bundle_id"]]
                raw = (ROOT / row["config_path"]).read_bytes()
                assert hashlib.sha256(raw).hexdigest() == row["config_sha256"] == member["config_sha256"]
                observed.add(scientific_config_identity_sha256(json.loads(raw)))
            assert len(observed) == 1
            hashes["decode" if role == "decode" else "prefill"] = observed.pop()
        assert hashes["decode"] != hashes["prefill"]
        result.append(hashes)
    return result


def v5_inputs(root):
    path, _digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
    pins = json.loads(path.read_text())
    contracts = contracts_from_pins(pins)
    for producer, contract, hashes in zip(pins["producer_plans"], contracts, registered_v5_hashes(), strict=True):
        source = inputs[producer["plan"]["plan_id"]]
        cells = {}
        for role, cell in source.cells.items():
            cells[role] = replace(cell,
                absolute=replace(cell.absolute, scientific_config_identity_sha256=hashes[role]),
                comparative=replace(cell.comparative, scientific_config_identity_sha256=hashes[role]))
            next(row for row in contract["roles"] if row["role"] == role)[
                "scientific_config_identity_sha256"
            ] = hashes[role]
        inputs[producer["plan"]["plan_id"]] = replace(source, cells=cells)
    return pins, contracts, inputs, snapshot


def emit_pair(root, *, two_workloads=True):
    if two_workloads:
        original, contracts, inputs, snapshot = v5_inputs(root)
    else:
        path, _digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
        original = json.loads(path.read_text())
        contracts = contracts_from_pins(original)
    issued = root / "issued.json"
    value = emitter.build_pinset(contracts=contracts, producer_inputs=inputs,
        ledger_snapshot=snapshot,
        relative_plan_paths=[p["plan"]["relative_path"] for p in original["producer_plans"]],
        pinset_path=issued, project_commit="0" * 40)
    issued.write_bytes(mint._artifact_payload(value))
    digest = hashlib.sha256(issued.read_bytes()).hexdigest()
    return issued, digest, value, inputs, snapshot


def real_pipeline(root):
    issued, digest, pins, inputs, snapshot = emit_pair(root)
    artifact = mint.mint_multi_cell_authenticated_artifact(
        pinset_path=issued, pinset_sha256=digest, producer_inputs=inputs,
        calibration_ledger_snapshot=snapshot, project_commit="0" * 40, project_tree_state="clean")
    floor = root / "floor.json"
    floor.write_bytes(mint._artifact_payload(artifact))
    checkout = root / "claim-checkout"
    shutil.copytree(ROOT / "joulewise", checkout / "joulewise", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "configs/analysis_registry", checkout / "configs/analysis_registry")
    registry = checkout / "scripts/floor_mint_pinsets"
    registry.mkdir(parents=True)
    shutil.copy2(issued, registry / "issued.json")
    command = [sys.executable, "-B", "-c",
        "from pathlib import Path; import sys; from joulewise.analysis_engine.inputs import load_floor_artifact; "
        "print(load_floor_artifact(Path(sys.argv[1])).value['artifact_id'])", str(floor)]
    loaded = subprocess.run(command, cwd=checkout, capture_output=True, text=True)
    if loaded.returncode:
        raise AssertionError(loaded.stderr)
    assert loaded.stdout.strip() == artifact["artifact_id"]
    return pins, artifact


class V2ConfigSetTests(unittest.TestCase):
    def test_real_v5_two_workload_emitter_mint_claim_reader_rc_zero(self):
        # Real producers at all three seams; fixture components are explicitly
        # synthetic, while every workload hash comes from the registered packs.
        with tempfile.TemporaryDirectory() as tmp:
            command = [sys.executable, "-B", "-c",
                "from pathlib import Path; import sys; "
                "from tests.test_mint_floor_v2_config_set import real_pipeline; "
                "p,a=real_pipeline(Path(sys.argv[1])); print(a['artifact_id'])", tmp]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout.strip(), "synthetic-d117-four-cell-floor")

    def test_emitter_pins_each_workload_and_artifact_records_sorted_config_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins, artifact = real_pipeline(Path(tmp))
            expected = []
            for producer, hashes in zip(pins["producer_plans"], registered_v5_hashes(), strict=True):
                self.assertEqual(producer["model_runtime_config"]["config_set_sha256"], config_set_hash(hashes.values()))
                cells = []
                for cell in producer["cells"]:
                    self.assertEqual(cell["scientific_config_identity_sha256"], hashes[cell["role"]])
                    cells.append({"cell_id": cell["cell_id"], "scientific_config_identity_sha256": hashes[cell["role"]]})
                expected.append({"plan_id": producer["plan"]["plan_id"],
                    "config_set_sha256": config_set_hash(hashes.values()), "cells": cells})
            self.assertEqual(artifact["provenance"]["producer_config_sets"], expected)

    def test_other_workload_and_set_preserving_swap_refuse_per_cell(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest, pins, inputs, snapshot = emit_pair(Path(tmp))
            plan_id = pins["producer_plans"][0]["plan"]["plan_id"]
            source = inputs[plan_id]
            for swapped_roles in (("decode",), ("prefill",), ("decode", "prefill")):
                for kind in ("absolute", "comparative", "both"):
                    with self.subTest(roles=swapped_roles, kind=kind):
                        cells = dict(source.cells)
                        for role in swapped_roles:
                            other = "prefill" if role == "decode" else "decode"
                            wrong = source.cells[other].absolute.scientific_config_identity_sha256
                            changes = {name: replace(getattr(cells[role], name), scientific_config_identity_sha256=wrong)
                                for name in ("absolute", "comparative") if kind in (name, "both")}
                            cells[role] = replace(cells[role], **changes)
                        attacked = {**inputs, plan_id: replace(source, cells=cells)}
                        with self.assertRaisesRegex(mint.MintError, "per-cell scientific config identity mismatch"):
                            mint.mint_multi_cell_authenticated_artifact(pinset_path=path, pinset_sha256=digest,
                                producer_inputs=attacked, calibration_ledger_snapshot=snapshot,
                                project_commit="0" * 40, project_tree_state="clean")

    def test_partial_malformed_or_wrong_set_pins_refuse_in_both_readers(self):
        with tempfile.TemporaryDirectory() as tmp:
            _path, _digest, pins, _inputs, _snapshot = emit_pair(Path(tmp))
            for attack in ("partial", "malformed", "set"):
                with self.subTest(attack=attack):
                    candidate = copy.deepcopy(pins)
                    producer = candidate["producer_plans"][0]
                    if attack == "partial":
                        del producer["cells"][0]["scientific_config_identity_sha256"]
                    elif attack == "malformed":
                        producer["cells"][0]["scientific_config_identity_sha256"] = None
                    else:
                        producer["model_runtime_config"]["config_set_sha256"] = "0" * 64
                    _repair_v2_pinset_self_hashes(candidate)
                    with self.assertRaises(mint.MintError):
                        mint._parse_v2_pinset(candidate)
                    self.assertIsNone(detection_floor._project_floor_mint_pinset_v2(candidate))

    def test_artifact_config_inventory_is_bound_to_registered_pins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, digest, _pins, inputs, snapshot = emit_pair(root)
            artifact = mint.mint_multi_cell_authenticated_artifact(pinset_path=path, pinset_sha256=digest,
                producer_inputs=inputs, calibration_ledger_snapshot=snapshot,
                project_commit="0" * 40, project_tree_state="clean")
            for attack in ("missing", "hash", "swap", "extra", "null"):
                with self.subTest(attack=attack):
                    candidate = copy.deepcopy(artifact)
                    if attack == "missing":
                        del candidate["provenance"]["producer_config_sets"]
                    elif attack == "null":
                        candidate["provenance"]["producer_config_sets"] = None
                    elif attack == "hash":
                        candidate["provenance"]["producer_config_sets"][0]["config_set_sha256"] = "0" * 64
                    elif attack == "extra":
                        candidate["provenance"]["producer_config_sets"][0]["operator_override"] = True
                    else:
                        cells = candidate["provenance"]["producer_config_sets"][0]["cells"]
                        cells[0]["scientific_config_identity_sha256"], cells[1]["scientific_config_identity_sha256"] = (
                            cells[1]["scientific_config_identity_sha256"], cells[0]["scientific_config_identity_sha256"])
                    errors = detection_floor.validate_floor_artifact(candidate, pinset_path=path, expected_pinset_sha256=digest)
                    self.assertTrue(errors, attack)
                    self.assertTrue(any("config" in error for error in errors), errors)

    def test_registered_config_hashes_are_read_from_all_real_pack_members(self):
        for name, expected in zip(PACK_NAMES, registered_v5_hashes(), strict=True):
            pack = ROOT / "configs/campaigns" / name
            tree = json.loads((pack / "plan_tree.json").read_text())
            contract = json.loads((pack / "producer_contract.json").read_text())
            for role in ("decode", "prefill_p2048"):
                mapping = next(row for row in contract["roles"] if row["role"] == role)
                digest = emitter._registered_cell_config_sha256(tree, mapping)
                self.assertEqual(digest, expected["decode" if role == "decode" else "prefill"])
                changed = copy.deepcopy(tree)
                next(row for row in changed["science"] if row["run_id"] == mapping["members"][-1]["bundle_id"])["config_sha256"] = "0" * 64
                with self.assertRaisesRegex(mint.MintError, "registered config"):
                    emitter._registered_cell_config_sha256(changed, mapping)

    def test_single_config_new_and_legacy_v2_still_mint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy_path, legacy_digest, inputs, snapshot = freeze_synthetic_v2_pinset(root)
            original = json.loads(legacy_path.read_text())
            legacy = mint.mint_multi_cell_authenticated_artifact(pinset_path=legacy_path, pinset_sha256=legacy_digest,
                producer_inputs=inputs, calibration_ledger_snapshot=snapshot,
                project_commit="0" * 40, project_tree_state="clean")
            self.assertNotIn("producer_config_sets", legacy["provenance"])
            _artifact, components = mint._build_v2_artifacts(pinset=mint.load_pinset(legacy_path, legacy_digest),
                pinset_path=legacy_path, pinset_sha256=legacy_digest, producer_inputs=inputs,
                calibration_ledger_snapshot=snapshot, project_commit="0" * 40, project_tree_state="clean")
            self.assertEqual(tuple(mint._artifact_sha256(c) for c in components), SYNTHETIC_COMPONENT_SHA256S)
            directory = root / "new"
            directory.mkdir()
            path, digest, pins, inputs, snapshot = emit_pair(directory, two_workloads=False)
            for producer in pins["producer_plans"]:
                hashes = [cell["scientific_config_identity_sha256"] for cell in producer["cells"]]
                self.assertEqual(len(set(hashes)), 1)
                self.assertEqual(producer["model_runtime_config"]["config_set_sha256"], config_set_hash(hashes))
            new = mint.mint_multi_cell_authenticated_artifact(pinset_path=path, pinset_sha256=digest,
                producer_inputs=inputs, calibration_ledger_snapshot=snapshot,
                project_commit="0" * 40, project_tree_state="clean")
            self.assertEqual(new["cells"], legacy["cells"])
            self.assertEqual(new["transport_groups"], legacy["transport_groups"])
            self.assertEqual([p["plan"] for p in pins["producer_plans"]], [p["plan"] for p in original["producer_plans"]])

    def test_schema_accepts_new_and_legacy_and_rejects_partial_or_malformed_bindings(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("optional jsonschema dependency is absent")
        schema = json.loads((ROOT / "scripts/floor_mint_pinsets/schema_v2.json").read_text())
        validator = jsonschema.Draft202012Validator(schema)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _path, _digest, pins, _inputs, _snapshot = emit_pair(root)
            validator.validate(pins)
            legacy_dir = root / "legacy"
            legacy_dir.mkdir()
            path, _digest, _inputs, _snapshot = freeze_synthetic_v2_pinset(legacy_dir)
            validator.validate(json.loads(path.read_text()))
            for replacement in (None, "uppercase" * 8, "absent"):
                with self.subTest(replacement=replacement):
                    candidate = copy.deepcopy(pins)
                    if replacement == "absent":
                        del candidate["producer_plans"][0]["cells"][0]["scientific_config_identity_sha256"]
                    else:
                        candidate["producer_plans"][0]["cells"][0]["scientific_config_identity_sha256"] = replacement
                    self.assertTrue(list(validator.iter_errors(candidate)))

    def test_model_runtime_and_exact_member_config_checks_remain_in_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest, pins, inputs, snapshot = emit_pair(Path(tmp))
            producer = pins["producer_plans"][0]
            plan_id = producer["plan"]["plan_id"]
            source = inputs[plan_id]
            cell = source.cells["decode"]
            for field, value, message in (
                ("model_artifact_sha256", "0" * 64, "model artifact inventory mismatch"),
                ("os_version", "different-runtime", "runtime identity inventory mismatch"),
            ):
                with self.subTest(field=field):
                    regime = copy.deepcopy(cell.absolute.source_regime)
                    regime["stack_identity"][field] = value
                    attacked_cell = replace(cell, absolute=replace(cell.absolute, source_regime=regime))
                    attacked_source = replace(source, cells={**source.cells, "decode": attacked_cell})
                    with self.assertRaisesRegex(mint.MintError, message):
                        mint._v2_gate_producer_inventory(producer, attacked_source)
            first, *rest = cell.absolute.members
            wrong_member = replace(first, config_sha256="0" * 64)
            attacked_cell = replace(cell, absolute=replace(cell.absolute, members=(wrong_member, *rest)))
            attacked = {**inputs, plan_id: replace(source, cells={**source.cells, "decode": attacked_cell})}
            with self.assertRaisesRegex(mint.MintError, "exact member/config pins mismatch"):
                mint.mint_multi_cell_authenticated_artifact(pinset_path=path, pinset_sha256=digest,
                    producer_inputs=attacked, calibration_ledger_snapshot=snapshot,
                    project_commit="0" * 40, project_tree_state="clean")


if __name__ == "__main__":
    unittest.main()
