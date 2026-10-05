#!/usr/bin/env python3
"""Author final v2 mint pins from two frozen packs and postcollection evidence.

This is an authoring step, not floor issuance. The generalized mint independently
authenticates the emitted pins. Register the final pinset in
scripts/floor_mint_pinsets/ for claim-side family discovery. Production packs
provide producer_contract.json, calibration_plan.json, extraction_spec.json,
order_manifest.json and plan_tree.json; completed windows provide reports,
bracket bindings and a terminal calibration ledger.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import tempfile
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.authentication_io import V2AuthenticationReadSession, V2AuthenticationInputError  # noqa: E402
from joulewise.identity_pins import scientific_config_identity_sha256  # noqa: E402
from scripts import mint_floor_artifact_generalized as mint  # noqa: E402


def _read(path: Path) -> tuple[Mapping[str, Any], str]:
    value, raw = mint._strict_json_file(path, str(path))
    if not isinstance(value, Mapping):
        raise mint.MintError(f"{path}: expected a JSON object")
    return value, hashlib.sha256(raw).hexdigest()


def _equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise mint.MintError(f"{label}: source pin mismatch")


def _one(rows: Sequence[Mapping[str, Any]], key: str, value: str) -> Mapping[str, Any]:
    matches = [row for row in rows if row.get(key) == value]
    if len(matches) != 1:
        raise mint.MintError(f"expected exactly one {key}={value!r}")
    return matches[0]


def _family_pins(bindings: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    return [{key: row[key] for key in ("condition_family_id", "condition_family_sha256")}
            for row in bindings]


def _postcollection(absolute: Mapping[str, Any], comparative: Mapping[str, Any],
                    binding: Mapping[str, Any], binding_hash: str, report_hash: str,
                    snapshot: Any, allowance: Mapping[str, Any]) -> dict[str, Any]:
    values = [Decimal(str(cell["floor"]["drift_widened_guarded_floor_j"]))
              for cell in (absolute, comparative)]
    if any(not value.is_finite() or value < 0 for value in values):
        raise mint.MintError("report floors must be finite nonnegative numbers")
    post: dict[str, Any] = {}
    for name, cell in (("absolute", absolute), ("comparative", comparative)):
        post[f"{name}_evaluation_basis_sha256"] = cell["evaluation_basis_sha256"]
        post[f"{name}_evaluation_basis_members"] = cell["evaluation_basis_members"]
    for role in ("pre", "post"):
        endpoint = binding["endpoints"][role]
        post[f"{role}_receipt_sha256"] = endpoint["receipt_digest"]
        post[f"{role}_content_sha256"] = endpoint["content_digest"]
    post.update(bracket_binding_sha256=binding_hash,
                terminal_ledger_head_sha256=(getattr(snapshot, "committed_head_digest", None)
                                             or snapshot.head_digest),
                extraction_report_sha256=report_hash, **allowance)
    for name, value in zip(("absolute", "comparative", "operative"),
                           (*values, max(values)), strict=True):
        post[f"{name}_floor_full_precision"] = format(value, "f")
        post[f"{name}_floor_six_decimal"] = format(
            value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN), ".6f")
    return post


def _aggregate(contracts: Sequence[Mapping[str, Any]], producers: list[dict]) -> dict:
    _equal([c["producer_index"] for c in contracts], [1, 2], "producer order")
    first = contracts[0]
    for contract in contracts:
        for key in ("plan_set_id", "aggregate_artifact_id", "cell_composition_rule", "consumer_floor_rule"):
            _equal(contract[key], first[key], f"producer contract {key}")
    return {
        "artifact_id": first["aggregate_artifact_id"], "plan_set_id": first["plan_set_id"],
        "producer_set_sha256": mint._canonical_json_sha256(producers),
        "calibration_scope": "production_window", "source_class": "prospective",
        "cell_composition_rule": first["cell_composition_rule"],
        "consumer_floor_rule": first["consumer_floor_rule"],
        "component_artifacts": [
            {"plan_id": p["plan"]["plan_id"], **p["component_artifact"],
             "producer_pin_sha256": mint._canonical_json_sha256(p)} for p in producers],
        "cell_ids": [c["cell_id"] for p in producers for c in p["cells"]],
        "transport_allowlists": [
            {"transport_group_id": c["transport_group_id"], "cell_ids": [c["cell_id"]],
             "allowed_consumer_condition_families": c["allowed_consumer_condition_families"]}
            for p in producers for c in p["cells"]],
    }


def _document(contracts: Sequence[Mapping[str, Any]], producers: list[dict]) -> dict:
    return {"schema_version": mint.PINSET_SCHEMA_VERSION_V2,
            "mint_tool_version": mint.V2_MINT_TOOL_VERSION,
            "producer_plans": producers, "aggregate": _aggregate(contracts, producers)}


def _component_pins(component: Any) -> dict:
    return {
        "evidence_root_id": component.evidence_root_id,
        "calibration_cell_id": component.calibration_cell_id,
        "evaluation_basis_sha256": component.whole_window_evaluation_basis_sha256,
        "evaluation_basis_members": component.evaluation_basis_member_count,
        "extraction_spec_sha256": component.spec_sha256,
        "extraction_spec_members": len(set(mint._v2_spec_member_ids(component.spec))),
        "expected_n": component.cell["floor"]["n"],
        "drift_allowance_j": component.whole_window_drift_allowance["allowance_j"],
        "order_manifest_id": component.order_manifest["manifest_id"],
        "order_manifest_sha256": component.order_manifest_sha256,
        "consumption_semantics_id": component.consumption_semantics_id,
        "members": [{"bundle_id": m.bundle_id, "config_sha256": m.config_sha256}
                    for m in component.members],
    }


def _registered_cell_config_sha256(tree: Mapping[str, Any], mapping: Mapping[str, Any]) -> str:
    """Derive a workload pin from every prospectively registered member config.

    Bundle config bytes may be reserialized by the harness. Scientific identity
    is the stable workload binding; the existing mint-member pins still bind the
    exact collected config bytes separately.
    """
    hashes = set()
    core = mint._fresh_original_core()
    for member in mapping["members"]:
        row = _one(tree["science"], "run_id", member["bundle_id"])
        relative = core._safe_relative_posix(row["config_path"], "registered config path")
        config, byte_hash = _read(REPO_ROOT / relative)
        _equal(byte_hash, row["config_sha256"], "registered config bytes")
        _equal(byte_hash, member["config_sha256"], "registered config member")
        hashes.add(scientific_config_identity_sha256(config))
    if len(hashes) != 1:
        raise mint.MintError("registered config cell must have exactly one scientific identity")
    return hashes.pop()


def build_pinset(*, contracts: Sequence[Mapping[str, Any]],
                 producer_inputs: Mapping[str, mint.V2ProducerInputs],
                 ledger_snapshot: Any, relative_plan_paths: Sequence[str],
                 pinset_path: Path, project_commit: str) -> dict:
    """Freeze inventory and deterministic component hashes through the real builder.

    Inputs are the generalized mint's authenticated producer objects. No artifact
    is issued here, and no output pins are supplied by an operator.
    """
    if len(contracts) != 2 or len(relative_plan_paths) != 2:
        raise mint.MintError("exactly two producer packs are required")
    producers = []
    for contract, relative in zip(contracts, relative_plan_paths, strict=True):
        source = producer_inputs[contract["plan"]["plan_id"]]
        core = mint._fresh_original_core()
        core._safe_relative_posix(relative, "producer plan relative path")
        cells = []
        for role in ("decode", "prefill"):
            cell_inputs = source.cells[role]
            mapping = _one(contract["roles"], "artifact_cell_id", contract["selected_cells"][role])
            absolute, comparative = cell_inputs.absolute, cell_inputs.comparative
            config_hash = mapping.get("scientific_config_identity_sha256", absolute.scientific_config_identity_sha256)
            for component in (absolute, comparative):
                _equal(component.scientific_config_identity_sha256, config_hash, f"{role} scientific config")
            binding = core._definition_binding(absolute)
            _equal(absolute.calibration_cell_id, mapping["absolute_calibration_cell_id"], "absolute cell")
            _equal(comparative.calibration_cell_id, mapping["comparative_calibration_cell_id"], "comparative cell")
            _equal(binding["condition_family_id"], mapping["condition_family_id"], "producer family")
            absolute_pins, comparative_pins = map(_component_pins, (absolute, comparative))
            post = _postcollection(
                {**absolute.cell, **absolute_pins}, {**comparative.cell, **comparative_pins},
                source.bracket_binding, source.bracket_binding_sha256, absolute.report_sha256,
                ledger_snapshot, source.calibration_allowance_projection)
            cells.append({
                "role": role, "cell_id": mapping["artifact_cell_id"],
                "scientific_config_identity_sha256": config_hash,
                "transport_group_id": mapping["transport_group_id"],
                **_family_pins([binding])[0], "metric": mapping["metric"], "window_class": "phase",
                "target_precheck_path": mapping["target_precheck_path"],
                "allowed_consumer_condition_families": _family_pins(cell_inputs.allowed_consumer_condition_families),
                "absolute": absolute_pins, "comparative": comparative_pins, "postcollection": post,
            })
        first = source.cells["decode"].absolute
        runtime = mint.derive_model_runtime_config(
            first.source_regime["stack_identity"], first.scientific_config_identity_sha256)
        runtime["config_set_sha256"] = mint.detection_floor.floor_mint_config_set_sha256(
            [cell["scientific_config_identity_sha256"] for cell in cells])
        producers.append({
            "plan": {"plan_id": source.plan["plan_id"], "sha256": source.plan_sha256,
                     "declared_sha256": source.plan_declared_sha256,
                     "sidecar_sha256": source.plan_sidecar_sha256, "relative_path": relative,
                     "declared_calibration_scope": source.plan["calibration_scope"],
                     "artifact_calibration_scope": "production_window"},
            "evidence_root_id": contract["evidence_root_id"],
            "component_artifact": {"artifact_id": contract["component_artifact_id"], "sha256": "0" * 64},
            "model_runtime_config": runtime,
            "extraction_spec": {"sha256": first.spec_sha256,
                                "member_count": len(set(mint._v2_spec_member_ids(first.spec)))},
            "calibration_acceptance": {
                "acceptance_id": source.calibration_acceptance["acceptance_id"],
                "artifact_sha256": source.calibration_acceptance_sha256,
                "derivation_sha256": source.calibration_acceptance["derivation_sha256"],
                "derivation_rule_id": source.calibration_acceptance["schema_version"]}, "cells": cells,
        })
    provisional = _document(contracts, producers)
    loaded = mint._parse_v2_pinset(provisional)
    # The builder authenticates inventory, postcollection values and both estimators.
    # A sentinel permits common-mode authoring; the mint still requires its real output flag.
    with tempfile.TemporaryDirectory(prefix="floor-component-pins-") as tmp:
        temporary = Path(tmp) / pinset_path.name
        raw = mint._artifact_payload(provisional)
        temporary.write_bytes(raw)
        _artifact, components = mint._build_v2_artifacts(
            pinset=loaded, pinset_path=temporary,
            pinset_sha256=hashlib.sha256(raw).hexdigest(),
            producer_inputs=producer_inputs, calibration_ledger_snapshot=ledger_snapshot,
            project_commit=project_commit, project_tree_state="clean", d165_replay_out=Path("authoring-replay.json"))
    for producer, component in zip(producers, components, strict=True):
        producer["component_artifact"]["sha256"] = mint._artifact_sha256(component)
    value = _document(contracts, producers)
    mint._validate_v2_pin_hashes(mint._parse_v2_pinset(value))
    return value


def _bootstrap_producer(pack: Path, runs: Path, report_path: Path, bracket_path: Path,
                        consumer_bindings: Mapping[str, Mapping[str, Any]], acceptance: Mapping[str, Any],
                        acceptance_hash: str, snapshot: Any, relative: str, prefill_role: str) -> tuple[dict, dict, dict]:
    core = mint._fresh_original_core()
    tree, tree_hash = _read(pack / "plan_tree.json")
    from joulewise.authentication_io import read_authentication_input
    tree_sidecar = read_authentication_input(pack / "plan_tree.sha256", grammar="raw", label="plan tree sidecar")
    _equal(tree_sidecar.decode().split(), [tree_hash, "plan_tree.json"], "plan tree sidecar")
    contract, contract_hash = _read(pack / "producer_contract.json")
    _equal(contract["schema_version"], "joulewise.d117_floor_producer_contract.v1", "producer contract schema")
    _equal(contract_hash, tree["downstream_contract"]["producer_contract"]["sha256"], "producer contract")
    plan_path = pack / "calibration_plan.json"
    plan, plan_hash = _read(plan_path)
    sidecar_path = pack / "calibration_plan.sha256"
    sidecar_raw = read_authentication_input(sidecar_path, grammar="raw", label="producer plan sidecar")
    _equal(sidecar_raw.decode().split(), [plan_hash, plan_path.name], "producer plan sidecar")
    sidecar_hash = hashlib.sha256(sidecar_raw).hexdigest()
    for declaration in (tree["plan"], contract["plan"]):
        _equal(declaration["plan_id"], plan["plan_id"], "producer plan id")
        _equal(declaration.get("sha256", declaration.get("actual_sha256")), plan_hash, "producer plan")
        _equal(declaration["sidecar_sha256"], sidecar_hash, "producer plan sidecar bytes")
    _equal(tree["plan"]["declared_sha256"], plan_hash, "declared producer plan")
    spec_path, order_path = pack / "extraction_spec.json", pack / "order_manifest.json"
    spec, spec_hash = _read(spec_path)
    order, order_hash = _read(order_path)
    _equal(spec_hash, contract["extraction_spec"]["sha256"], "extraction spec")
    _equal(order_hash, contract["order_manifest"]["sha256"], "order manifest")
    report, report_hash = _read(report_path)
    binding, binding_hash = _read(bracket_path)
    pre, post = mint.validate_calibration_bracket_binding(
        binding, snapshot, window_id=binding["window_id"], plan_id=plan["plan_id"], plan_sha256=plan_hash,
        evidence_root_id=contract["evidence_root_id"], runs_root=runs) or (None, None)
    if pre is None or post is None:
        raise mint.MintError("producer bracket binding failed authentication")
    allowance = mint._v2_allowance_projection(mint.V2ProducerInputs(
        plan=plan, plan_sha256=plan_hash, cells={}, evidence_root=runs,
        plan_declared_sha256=plan_hash, plan_sidecar_sha256=sidecar_hash,
        calibration_acceptance=acceptance, calibration_acceptance_sha256=acceptance_hash,
        bracket_binding=binding, bracket_binding_sha256=binding_hash), pre, post)
    log_rows = [mint._strict_json_value(line.encode(), "campaign log")
                for line in read_authentication_input(runs / "campaign_log.jsonl", grammar="jsonl",
                                                     label="campaign log").decode().splitlines() if line.strip()]
    cells, manifest_cells = [], []
    contract = copy.deepcopy(dict(contract))
    contract["selected_cells"] = {}
    runtime = None
    for role, pack_role in (("decode", "decode"), ("prefill", prefill_role)):
        mapping = _one(contract["roles"], "role", pack_role)
        config_hash = _registered_cell_config_sha256(tree, mapping)
        # This in-memory projection carries the pack-derived pin into the final
        # author after independent bundle authentication; the frozen pack stays intact.
        mapping["scientific_config_identity_sha256"] = config_hash
        contract["selected_cells"][role] = mapping["artifact_cell_id"]
        allowed = [consumer_bindings[name] for name in mapping["allowed_consumer_families"]]
        projected_components, component_paths = {}, {}
        report_cells = {}
        for kind in ("absolute", "comparative"):
            cell_id = mapping[f"{kind}_calibration_cell_id"]
            cell = _one(report["cells"], "cell_id", cell_id)
            spec_cell = _one(spec["cells"], "cell_id", cell_id)
            if not cell.get("extractable") or cell.get("refusal_reasons") or cell.get("excluded_slots"):
                raise mint.MintError(f"{cell_id}: report cell is not fully extractable")
            drift = cell["whole_window_drift_allowance"]
            basis = core._authenticated_evaluation_basis(log_rows, drift["whole_window_evaluation_basis_sha256"])
            pins = {"evidence_root_id": contract["evidence_root_id"], "calibration_cell_id": cell_id,
                    "evaluation_basis_sha256": drift["whole_window_evaluation_basis_sha256"],
                    "evaluation_basis_members": len(basis["member_occurrences"]),
                    "extraction_spec_sha256": spec_hash, "extraction_spec_members": len(set(mint._v2_spec_member_ids(spec))),
                    "expected_n": cell["floor"]["n"], "drift_allowance_j": drift["allowance_j"],
                    "order_manifest_id": order["manifest_id"], "order_manifest_sha256": order_hash,
                    "consumption_semantics_id": report["consumption_semantics_id"],
                    "members": [{"bundle_id": m["bundle_id"], "config_sha256": m["config_sha256"]}
                                for m in cell["members"]]}
            projected_components[kind] = pins
            report_cells[kind] = {**cell, **pins}
            component_paths[kind] = {"evidence_root": str(runs), "report": str(report_path),
                                     "spec": str(spec_path), "order_manifest": str(order_path)}
            if runtime is None:
                member = pins["members"][0]["bundle_id"]
                config, _ = _read(runs / member / "config.json")
                metadata, _ = _read(runs / member / "metadata.json")
                runtime = mint.derive_model_runtime_config(core.build_stack_identity(config, metadata),
                    core.canonical_json_sha256(core.scientific_config_identity(config)))
            if kind == "absolute":
                family = spec_cell["condition_family_definitions"]["all"]
                _equal(family["condition_family_id"], mapping["condition_family_id"], "producer family")
        cells.append({"role": role, "cell_id": mapping["artifact_cell_id"],
                      "scientific_config_identity_sha256": config_hash,
                      "transport_group_id": mapping["transport_group_id"], **_family_pins([family])[0],
                      "metric": mapping["metric"], "window_class": "phase", "target_precheck_path": mapping["target_precheck_path"],
                      "allowed_consumer_condition_families": _family_pins(allowed), **projected_components,
                      "postcollection": _postcollection(report_cells["absolute"], report_cells["comparative"],
                          binding, binding_hash, report_hash, snapshot, allowance)})
        manifest_cells.append({"role": role, **component_paths, "allowed_consumer_condition_families": allowed})
    runtime["config_set_sha256"] = mint.detection_floor.floor_mint_config_set_sha256(
        [cell["scientific_config_identity_sha256"] for cell in cells])
    producer = {"plan": {"plan_id": plan["plan_id"], "sha256": plan_hash, "declared_sha256": plan_hash,
                         "sidecar_sha256": sidecar_hash, "relative_path": relative,
                         "declared_calibration_scope": plan["calibration_scope"], "artifact_calibration_scope": "production_window"},
                "evidence_root_id": contract["evidence_root_id"],
                "component_artifact": {"artifact_id": contract["component_artifact_id"], "sha256": "0" * 64},
                "model_runtime_config": runtime,
                "extraction_spec": {"sha256": spec_hash, "member_count": len(set(mint._v2_spec_member_ids(spec)))},
                "calibration_acceptance": {"acceptance_id": acceptance["acceptance_id"], "artifact_sha256": acceptance_hash,
                                           "derivation_sha256": acceptance["derivation_sha256"], "derivation_rule_id": acceptance["schema_version"]},
                "cells": cells}
    manifest_row = {"plan_id": plan["plan_id"], "calibration_plan": str(plan_path),
                    "calibration_plan_sidecar": str(sidecar_path), "bracket_binding": str(bracket_path), "cells": manifest_cells}
    return contract, producer, manifest_row


def build_input_manifest(*, acceptance_path: Path, ledger_path: Path,
                         head_pin_path: Path, producer_rows: Sequence[Mapping[str, Any]]) -> dict:
    """Route each producer's own plan, root, report, spec, order and bracket."""
    if len(producer_rows) != 2:
        raise mint.MintError("input manifest requires exactly two producers")
    return {"schema_version": "joulewise.floor_mint_inputs.v2",
            "calibration_acceptance": str(acceptance_path.resolve()),
            "calibration_ledger": str(ledger_path.resolve()),
            "calibration_ledger_head_pin": str(head_pin_path.resolve()),
            "producer_plans": copy.deepcopy(list(producer_rows))}


def _write_pair(pinset_path: Path, manifest_path: Path, pinset: dict, manifest: dict) -> str:
    paths = (pinset_path.absolute(), manifest_path.absolute())
    if paths[0] == paths[1] or any(p.exists() or p.is_symlink() for p in paths):
        raise mint.MintError("emitter outputs must be distinct absent paths")
    written = []
    try:
        for path, value in zip(paths, (pinset, manifest), strict=True):
            with path.open("xb") as stream:
                written.append(path)
                stream.write(mint._artifact_payload(value))
    except OSError:
        for path in written:
            path.unlink()
        raise
    return hashlib.sha256(mint._artifact_payload(pinset)).hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("producer-pack", "runs-root", "extraction-report", "bracket-binding", "plan-relative-path"):
        parser.add_argument(f"--{flag}", action="append", required=True,
                            type=str if flag == "plan-relative-path" else Path)
    parser.add_argument("--prefill-role", default="prefill_p2048")
    for flag in ("consumer-pack", "calibration-acceptance", "calibration-ledger", "calibration-ledger-head-pin", "pinset-out", "input-manifest-out"):
        parser.add_argument(f"--{flag}", required=True, type=Path)
    parser.add_argument("--calibration-custody-store", type=Path)
    parser.add_argument("--project-commit", required=True, help="exact commit the subsequent mint will record")
    args = parser.parse_args(argv)
    try:
        from joulewise.cli import validate_bundle
        with V2AuthenticationReadSession():
            acceptance, acceptance_hash = _read(args.calibration_acceptance)
            core = mint._fresh_original_core()
            acceptance = core.load_calibration_acceptance_bound(args.calibration_acceptance)
            if acceptance is None:
                raise mint.MintError("issued calibration acceptance failed authentication")
            snapshot = mint._load_v2_ledger_snapshot(core, acceptance=acceptance,
                ledger_path=args.calibration_ledger, head_pin_path=args.calibration_ledger_head_pin,
                calibration_custody_store=args.calibration_custody_store)
            if not snapshot.valid:
                raise mint.MintError("calibration ledger failed authentication")
            consumer = args.consumer_pack.resolve(strict=True)
            prospective, _ = _read(consumer / "analysis_manifest_v3.json")
            from joulewise.analysis_manifest_v3 import validate_prospective_analysis_manifest_v3
            refusals = validate_prospective_analysis_manifest_v3(
                prospective, manifest_dir=consumer, plan_tree_path=consumer / "plan_tree.json")
            if refusals:
                raise mint.MintError(f"consumer registration refused: {refusals[0]}")
            from joulewise.detection_floor import CONDITION_FAMILY_DOMAIN, canonical_domain_sha256
            bindings = {}
            for row in prospective["condition_families"]:
                path = consumer / row["path"]
                definition, byte_hash = _read(path)
                _equal(byte_hash, row["sha256"], "consumer family bytes")
                digest = canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition)
                _equal(digest, row["canonical_domain_sha256"], "consumer family")
                bindings[row["condition_family_id"]] = {"condition_family_id": row["condition_family_id"],
                    "condition_family_sha256": digest, "condition_family_definition": definition}
            groups = (args.producer_pack, args.runs_root, args.extraction_report, args.bracket_binding, args.plan_relative_path)
            if any(len(group) != 2 for group in groups):
                raise mint.MintError("supply exactly two of each producer argument, in producer order")
            triples = [_bootstrap_producer(pack.resolve(strict=True), runs.resolve(strict=True),
                        report.resolve(strict=True), bracket.resolve(strict=True), bindings,
                        acceptance, acceptance_hash, snapshot, relative, args.prefill_role)
                       for pack, runs, report, bracket, relative in zip(*groups, strict=True)]
            contracts, producers, rows = map(list, zip(*triples, strict=True))
            manifest = build_input_manifest(acceptance_path=args.calibration_acceptance,
                ledger_path=args.calibration_ledger, head_pin_path=args.calibration_ledger_head_pin, producer_rows=rows)
            provisional = _document(contracts, producers)
            with tempfile.TemporaryDirectory(prefix="floor-pin-author-") as tmp:
                temporary = Path(tmp) / "pins.json"
                temporary.write_bytes(mint._artifact_payload(provisional))
                loaded = mint.load_pinset(temporary, hashlib.sha256(temporary.read_bytes()).hexdigest())
                inputs, _roots, snapshot = mint._authenticate_v2_inputs(
                    pinset=loaded, pinset_path=temporary, pinset_sha256=hashlib.sha256(temporary.read_bytes()).hexdigest(),
                    input_manifest_path=Path(tmp) / "inputs.json", input_manifest=manifest,
                    strict_validator=lambda path, strict: validate_bundle(path, strict=strict),
                    consumption_semantics_id=None, calibration_custody_store=args.calibration_custody_store)
                value = build_pinset(contracts=contracts, producer_inputs=inputs, ledger_snapshot=snapshot,
                    relative_plan_paths=args.plan_relative_path, pinset_path=args.pinset_out, project_commit=args.project_commit)
            digest = _write_pair(args.pinset_out, args.input_manifest_out, value, manifest)
        print(json.dumps({"status": "EMITTED", "pinset_sha256": digest,
                          "pinset": str(args.pinset_out), "input_manifest": str(args.input_manifest_out)}, sort_keys=True))
        return 0
    except (mint.MintError, V2AuthenticationInputError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
