"""Synthetic two-pack evidence, minted by the real generalized v2 producer.

No runtime, sampler, or launch is started. Immutable raw bytes come from the
strict seed bundle; model/plan identities and calibration endpoints are fixtures.
The mint, artifact validation, strict bundle validation, and loader are real.
"""

from __future__ import annotations

import json
import os
import plistlib
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from unittest import mock

from joulewise import detection_floor
from joulewise.analysis_engine.inputs import load_analysis_inputs
from joulewise.cli import validate_bundle
from joulewise.adapters.powermetrics import rich_telemetry_jsonl
from joulewise.reduce import reduce_bundle
from joulewise.identity_pins import build_stack_identity, scientific_config_identity_sha256
from scripts import generate_matrix, mint_floor_artifact_generalized as mint
from tests import test_mint_floor_artifact_generalized as fixtures


ROOT = Path(__file__).resolve().parents[3]
SEED = ROOT / "tests/fixtures/d117_v2_production/strict_seed_bundle"
ROOT_IDS = ("evidence-d117-floor-qwen3-1p7b-v5", "evidence-d117-floor-qwen3-8b-v5")
RUNS_LEAVES = ("runs_d117_floor_qwen3-1p7b_v5", "runs_d117_floor_qwen3-8b_v5")


def write_json(path: Path, value: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return fixtures.file_sha256(path)


def _copy_seed(source: str, destination: str) -> str:
    # Only raw evidence is hard linked, and it is never edited by these tests.
    if Path(source).name in {"config.json", "metadata.json", "summary_metrics.json"}:
        return shutil.copyfile(source, destination)
    os.link(source, destination)
    return destination


def install(root: Path) -> SimpleNamespace:
    # Preserve every record, time, power, energy and GPU state needed for the
    # strict replay; omit the large unused CPU census from this synthetic seed.
    seed = root / "seed"
    shutil.copytree(SEED, seed)
    for path in (seed / "raw").glob("*.plist"):
        documents = [plistlib.loads(frame.strip()) for frame in path.read_bytes().split(b"\0") if frame.strip()]
        compact = []
        for document in documents:
            projected = {key: document[key] for key in (
                "timestamp", "elapsed_ns", "gpu", "thermal_pressure", "is_delta") if key in document}
            projected["processor"] = {key: value for key, value in document["processor"].items()
                                      if key.endswith("_power") or key.endswith("_energy")}
            compact.append(plistlib.dumps(projected))
        path.write_bytes(b"\0".join(compact) + b"\0")
    metadata = fixtures.load_json(seed / "metadata.json")
    endpoint = metadata["uncertainty_evidence"]["clock_anchor"]["first_sample_end_point_epoch_s"]
    (seed / "rich_telemetry.jsonl").write_text(rich_telemetry_jsonl(
        (seed / "raw/powermetrics.plist").read_bytes(), first_record_endpoint_s=endpoint))
    summary = fixtures.load_json(seed / "summary_metrics.json")
    write_json(seed / "summary_metrics.json", reduce_bundle(
        seed, reducer_version=summary["summary_provenance"]["reducer_version"]).to_dict())
    pinset, sources, _ = fixtures.synthetic_v2_fixture()
    inputs = {}
    receipts, observations, sessions = [], [], {}
    evidence_roots = {}
    plan_paths, order_paths = [], []
    for index, producer in enumerate(pinset["producer_plans"]):
        source = sources[producer["plan"]["plan_id"]]
        root_id = ROOT_IDS[index]
        runs_root = root / RUNS_LEAVES[index]
        runs_root.mkdir()
        evidence_roots[root_id] = runs_root
        plan_id = f"plan-d117-floor-qwen3-{'1p7b' if index == 0 else '8b'}-v5"
        pack = root / "packs" / RUNS_LEAVES[index]
        plan_path = pack / "calibration_plan.json"
        plan = {"plan_id": plan_id, "calibration_scope": "production_window",
                "order_manifest": "order_manifest.json", "fixture": "SYNTHETIC"}
        plan_sha = write_json(plan_path, plan)
        plan_paths.append(plan_path)
        producer["plan"].update(plan_id=plan_id, sha256=plan_sha,
                                declared_sha256=plan_sha,
                                relative_path=plan_path.relative_to(root).as_posix())
        producer["evidence_root_id"] = root_id
        pinset["aggregate"]["component_artifacts"][index]["plan_id"] = plan_id
        binding, rows, obs, session = fixtures._synthetic_bracket_evidence(
            index, plan_id=plan_id, plan_sha256=plan_sha, evidence_root_id=root_id,
            runs_root=runs_root, sequence_start=1 + 3 * index,
        )
        receipts.extend(rows)
        observations.extend(obs)
        sessions[session.session_id] = session
        member_order = [m.bundle_id for c in (source.cells["decode"].absolute,
                                              source.cells["decode"].comparative)
                        for m in c.members]
        order = {"manifest_id": f"{plan_id}-order", "plan_id": plan_id,
                 "calibration_plan_sha256": plan_sha,
                 "executed_order": [{"bundle_id": name} for name in member_order]}
        order_path = pack / "order_manifest.json"
        order_sha = write_json(order_path, order)
        order_paths.append(order_path)
        log_path = runs_root / "campaign_log.jsonl"
        log_path.write_text("".join(json.dumps(row) + "\n" for row in order["executed_order"]))
        log_sha = fixtures.file_sha256(log_path)
        blocks = {name: (block["block_id"], position)
                  for block in source.cells["decode"].comparative.spec_cell["blocks"]
                  for position, name in block["members"].items()}
        bundle_data = {}
        for name in member_order:
            bundle = runs_root / name
            shutil.copytree(seed, bundle, copy_function=_copy_seed)
            config = fixtures.load_json(bundle / "config.json")
            metadata = fixtures.load_json(bundle / "metadata.json")
            config["run_id"] = name
            config["model"]["name"] = "Qwen3-1.7B" if index == 0 else "Qwen3-8B"
            tags = ["SYNTHETIC", f"calibration-plan-sha256={plan_sha}"]
            if name in blocks:
                block_id, position = blocks[name]
                tags += [f"calibration-abba-block-id={block_id}",
                         f"calibration-abba-label={position[0]}",
                         f"calibration-abba-sequence-index={('A1','B1','B2','A2').index(position)+1}"]
            config["run_metadata"]["tags"] = tags
            config_sha = write_json(bundle / "config.json", config)
            metadata.update(run_id=name, config_sha256=config_sha, model=config["model"])
            metadata["workload_provenance"]["sampler"] = {}
            metadata["adapters"]["runtime"]["prepare_metadata"]["version"] = "0.1.0"
            for side in ("start", "end"):
                metadata["source_provenance"][side].update(
                    tracked="clean", staged="clean", untracked="clean")
            metadata["source_provenance"].update(claim_eligible=True, reason_codes=[])
            write_json(bundle / "metadata.json", metadata)
            bundle_data[name] = (config, metadata, fixtures.load_json(bundle / "summary_metrics.json"),
                                 detection_floor.complete_bundle_sha256(bundle), config_sha)
        role_inputs = {}
        for cell_pin in producer["cells"]:
            role = cell_pin["role"]
            converted = {}
            for kind in ("absolute", "comparative"):
                component = getattr(source.cells[role], kind)
                members = tuple(replace(
                    member, raw_config=bundle_data[member.bundle_id][0],
                    metadata=bundle_data[member.bundle_id][1],
                    summary=bundle_data[member.bundle_id][2],
                    metric_value_j=bundle_data[member.bundle_id][2]["phase_energy_j"][role],
                    bundle_sha256=bundle_data[member.bundle_id][3],
                    config_sha256=bundle_data[member.bundle_id][4],
                ) for member in component.members)
                stack = build_stack_identity(members[0].raw_config, members[0].metadata)
                assert stack is not None
                regime = {**component.source_regime, "stack_identity": stack,
                          "stack_identity_sha256": detection_floor.canonical_domain_sha256(
                              detection_floor.STACK_IDENTITY_DOMAIN, stack)}
                component = replace(
                    component, members=members, source_regime=regime,
                    scientific_config_identity_sha256=scientific_config_identity_sha256(members[0].raw_config),
                    evidence_root_id=root_id, order_manifest=order,
                    order_manifest_sha256=order_sha, campaign_log_sha256=log_sha,
                    whole_window_calibration_bracket=fixtures._synthetic_verdict_bracket(obs),
                )
                converted[kind] = component
            role_inputs[role] = replace(source.cells[role], **converted)
        report_cells = [fixtures._production_report_cell(getattr(cell, kind))
                        for cell in role_inputs.values() for kind in ("absolute", "comparative")]
        report = {**source.cells["decode"].absolute.report, "cells": report_cells}
        report_sha = fixtures._fixture_artifact_sha256(report)
        for cell_pin in producer["cells"]:
            role = cell_pin["role"]
            cell = role_inputs[role]
            converted = {}
            for kind in ("absolute", "comparative"):
                component = getattr(cell, kind)
                component = replace(component, report=report, report_sha256=report_sha,
                                    cell=next(r for r in report_cells if r["cell_id"] == component.calibration_cell_id))
                converted[kind] = component
                cell_pin[kind] = fixtures._v2_component_pin(component)
            cell = replace(cell, **converted)
            role_inputs[role] = cell
            cell_pin["postcollection"] = fixtures._v2_postcollection(
                cell.absolute, cell.comparative, acceptance_id=source.calibration_acceptance["acceptance_id"],
                bracket_binding=binding, bracket_binding_sha256=fixtures._fixture_artifact_sha256(binding),
                extraction_report_sha256=report_sha)
        first = role_inputs["decode"].absolute
        producer["model_runtime_config"] = mint.derive_model_runtime_config(
            first.source_regime["stack_identity"], first.scientific_config_identity_sha256)
        inputs[plan_id] = replace(
            source, plan=plan, plan_sha256=plan_sha, plan_declared_sha256=plan_sha,
            cells=role_inputs, evidence_root=runs_root, bracket_binding=binding,
            bracket_binding_sha256=fixtures._fixture_artifact_sha256(binding),
            authenticated_pre_observation=obs[0], authenticated_post_observation=obs[1])
    snapshot = SimpleNamespace(valid=True, ledger_schema=fixtures.LEDGER_SCHEMA,
                               receipts=tuple(receipts), observations=tuple(observations),
                               bracket_session_by_id=sessions, head_sequence=len(receipts),
                               head_digest=receipts[-1]["receipt_digest"])
    for producer in pinset["producer_plans"]:
        for cell in producer["cells"]:
            cell["postcollection"]["terminal_ledger_head_sha256"] = snapshot.head_digest
    fixtures._repair_v2_pinset_self_hashes(pinset)
    pinset_path, digest = fixtures.write_pinset(root, pinset)
    _, components = mint._build_v2_artifacts(
        pinset=mint.load_pinset(pinset_path, digest), pinset_path=pinset_path,
        pinset_sha256=digest, producer_inputs=inputs, calibration_ledger_snapshot=snapshot,
        project_commit="0" * 40, project_tree_state="clean")
    for producer, entry, component in zip(pinset["producer_plans"], pinset["aggregate"]["component_artifacts"], components):
        producer["component_artifact"]["sha256"] = fixtures._fixture_artifact_sha256(component)
        entry["sha256"] = producer["component_artifact"]["sha256"]
    fixtures._repair_v2_pinset_self_hashes(pinset)
    pinset_path, digest = fixtures.write_pinset(root, pinset)
    artifact = mint.mint_multi_cell_authenticated_artifact(
        pinset_path=pinset_path, pinset_sha256=digest, producer_inputs=inputs,
        calibration_ledger_snapshot=snapshot, project_commit="0" * 40, project_tree_state="clean")
    floor_path = root / "floor.json"
    write_json(floor_path, artifact)
    registry = root / "registry"
    registry.mkdir()
    shutil.copyfile(pinset_path, registry / "pinset.json")
    matrix = root / "analysis-configs"
    assert generate_matrix.main(["--base", str(ROOT / "configs/examples/mock_local.json"),
                                 "--model-tag", "fixture", "--out-dir", str(matrix)]) == 0
    analysis_root = root / "analysis-runs"
    analysis_root.mkdir()
    strict_results = {}

    def strict_validator(path, strict=True):
        if not path.is_dir():
            return validate_bundle(path, strict)
        digest = detection_floor.complete_bundle_sha256(path)
        if digest not in strict_results:
            strict_results[digest] = validate_bundle(path, strict)
        return strict_results[digest]

    return SimpleNamespace(root=root, artifact=artifact, floor_path=floor_path, pinset=pinset,
                           pinset_path=pinset_path, evidence_roots=evidence_roots,
                           plan_paths=plan_paths, order_paths=order_paths,
                           snapshot=snapshot, analysis_root=analysis_root,
                           manifest_path=matrix / "analysis_manifest.json", strict_validator=strict_validator,
                           producer_inputs=inputs)


def load(fixture, **kwargs):
    return load_analysis_inputs(
        fixture.manifest_path, fixture.analysis_root, fixture.floor_path,
        strict_validator=fixture.strict_validator, evidence_roots=fixture.evidence_roots,
        calibration_ledger_snapshot=fixture.snapshot, **kwargs)


class MintedAnalysisV2TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="analysis-v2-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.fixture = install(Path(cls.temporary.name))

    def setUp(self):
        # Registry discovery points at the fixture pinset; validation stays real.
        self.enterContext(mock.patch.object(
            detection_floor, "_FLOOR_MINT_PINSET_DIRECTORY", self.fixture.root / "registry"))
