#!/usr/bin/env python3
"""Freeze compose.layout output as BYTES draft fixed trees for both passes.

Each pass has its own fixed pack and campaign directory. The stage-1 driver
reads plan_tree_ref directly; loop base_order puts all pass-one packs before
pass two, reversing the sub-pack order for the second pass.
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import importlib.util
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.b6 import compose, queue
from joulewise.b5.plan import declared_bindings, resolve_stage_dispatches
from joulewise.b6.pack_registration import Registration, validate
from joulewise.flags.catalog import load_catalog
from joulewise.identity_pins import (
    IDENTITY_PIN_DERIVATION_CONTRACT, IDENTITY_PIN_PROJECTION_WORK_ORDER,
    MODEL_RUNTIME_CONFIG_FIELDS, validate_identity_pin_projection,
)
from joulewise.schemas import BenchmarkConfig

spec = importlib.util.spec_from_file_location("bytes_configs", ROOT / "configs/campaigns/bytes_v1/generate_configs.py")
configs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(configs)
GROUPS = (("qwen3-1p7b", "qwen3-4b"), ("qwen3-8b", "qwen3-30b-a3b"),
          ("qwen3-14b", "qwen3-next-80b"), ("qwen3-32b", "qwen3-8b-8bit"),
          ("llama-70b",), ("qwen35-122b",))
SIZING_PATH = Path("configs/b6/registration/sizing_b5.json")


def module_estimate(model_id, number, repo_root):
    """Use C5's own per-model member allowance, without a second margin.

    Module minutes exclude shared reference/calibration/custody overhead;
    the native writer consumes the row's full programmed_span_s separately.
    Pass two uses the same model costs, in reversed order.
    """
    raw = (Path(repo_root) / SIZING_PATH).read_bytes()
    label = f"bytes-s{number}-p1"
    row = json.loads(raw)["packs"][label]["disk_derivation"]["allowances_by_model"][model_id]
    seconds = row["member_allowance_s"]
    minutes = Fraction(seconds["numerator"], seconds["denominator"]) * row["count"] / 60
    return {"est_minutes": float(minutes), "est_minutes_source": {
        "path": SIZING_PATH.as_posix(), "sha256": configs.sha(raw),
        "source_pointer": f"/packs/{label}/disk_derivation/allowances_by_model/{model_id}",
        "formula": "count * member_allowance_s / 60; no additional margin"}}


# Registration section 13: the pass-one twin agrees at Addendum 8's bar at
# this joulewise/bytes_analysis.py SHA-256. Pass-two versions remain null.
AGREED_ESTIMATOR_VERSION = "18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71"
ESTIMATORS = [{"name": name, "library": "joulewise.bytes_analysis", "function": function, "version": None}
              for name, function in (("bytes_phase_cells", "reduce_models"),
                                     ("bytes_frozen_predictions", "frozen_predictions"),
                                     ("bytes_held_out_evaluation", "evaluate"))]


def launch_declaration(tree, repo_root):
    """Reuse the production floor declaration, as the non-claim H author does.

    These are typed declarations, not session destinations. DriverLane binds
    the latter through session_paths using loop_bytes.json at preparation.
    """
    floor = Path(repo_root) / "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json"
    launch = deepcopy(json.loads(floor.read_bytes())["arm_attachments"]["launch"])
    for row in launch["bindings"]:
        if row["name"] == "claim_runs_root":
            row["leaf"] = tree["roots"]["claim_root_leaf"]
        elif row["name"] == "bound_runs_root":
            row["leaf"] = tree["roots"]["bound_root_leaf"]
    declared_bindings({"arm_attachments": {"launch": launch}})
    return launch


def identity_projection(tree, directory, repo_root):
    """Bind every dispatched config, including auxiliary references, as in H.

    The projection reader requires regular files inside the pack. Copy the
    exact source bytes and relocate manifests and science locators together;
    no scientific config, member order or count changes. A no-model-load desk
    build cannot issue a frozen execution receipt: its pins remain null.
    """
    root = Path(repo_root)
    roster = json.loads((root / configs.PACK / "roster.json").read_bytes())
    names = {row["model"]["source"]: row["model_id"] for row in roster["models"]}
    external = {row["manifest"]["path"]: row["external_input_id"]
                for row in tree["external_inputs"]["manifests"]}
    science = {row["run_id"] for row in tree["science"]}
    dispatches = {d.stage_id: d for d in resolve_stage_dispatches(tree, root)}
    units, files, relocated, manifests = {}, {}, {}, []
    for stage in tree["stage_graph"]:
        if stage["kind"] != "campaign_collection":
            continue
        dispatch = dispatches[stage["stage_id"]]
        if dispatch.error:
            raise ValueError(dispatch.error)
        source = Path(dispatch.config_dir) / "order_manifest.json"
        manifest = json.loads((root / source).read_bytes())
        if len(manifest["executed_order"]) != stage["expected_count"]:
            raise ValueError("dispatched member count differs: " + stage["stage_id"])
        local = directory / "members" / stage["stage_id"]
        members = []
        for row in manifest["executed_order"]:
            origin = source.parent / row["config"]
            raw = (root / origin).read_bytes()
            digest = configs.sha(raw)
            if row.get("config_sha256", digest) != digest:
                raise ValueError("source config digest differs: " + origin.as_posix())
            target = local / origin.name
            files[target] = raw
            relative = target.as_posix()
            relocated[origin.as_posix()] = relative
            if "config_path" in row:
                row["config_path"] = relative
            row.update(config=target.name, config_sha256=digest)
            typed = BenchmarkConfig.from_mapping(json.loads(raw)).to_dict()
            model, hardware = typed["model"], typed["hardware_target"]
            unit_id = names.get(model["source"], "neg8_reference")
            declared = {"hardware_target": hardware["id"], "runtime_backend": hardware["runtime_backend"],
                "telemetry_backend": hardware["telemetry_backend"], "model_name": model["name"],
                "model_source": model["source"], "model_revision": model.get("revision"),
                "quantization": typed["quantization"], "workload_profile": typed["workload_profile"]}
            unit = units.setdefault(unit_id, {"identity_unit_id": unit_id,
                "producer_plan_reference": {"plan_id": tree["window_identity"]["window_id"],
                                            "path": "collection_plan.json"},
                "consumer_bindings": [{"arm": unit_id, "family": unit_id,
                                       "measurement_arm": typed["workload_profile"]["name"]}],
                "declared_identity": declared, "config_inventory": [],
                "model_runtime_config": dict.fromkeys(MODEL_RUNTIME_CONFIG_FIELDS)})
            if unit["declared_identity"] != declared:
                raise ValueError("dispatched configs disagree on identity: " + unit_id)
            unit["config_inventory"].append({"path": target.relative_to(directory).as_posix(), "sha256": digest})
            if row["run_id"] not in science:
                members.append({"run_id": row["run_id"], "ordinal": row.get("index"),
                                "path": relative, "sha256": digest})
        manifest_path = local / "order_manifest.json"
        raw = configs.raw_json(manifest)
        files[manifest_path] = raw
        ref = {"kind": "manifest", "path": manifest_path.as_posix(),
               "manifest_id": manifest["manifest_id"], "sha256": configs.sha(raw)}
        stage["input"] = ref
        stage["launch"]["commands"][0]["argv_template"]["arguments"][0] = {
            "kind": "repo_path", "value": local.as_posix()}
        if members:
            manifests.append({"external_input_id": external[source.as_posix()], "manifest": dict(ref),
                              "expected_count": len(members), "members": members})
    for row in tree["science"]:
        row["config_path"] = relocated[row["config_path"]]
    for unit in units.values():
        unit["config_inventory"].sort(key=lambda row: row["path"])
    tree["external_inputs"]["manifests"] = manifests
    tree["arm_attachments"]["identity_pin_projection"] = validate_identity_pin_projection({
        "work_order": IDENTITY_PIN_PROJECTION_WORK_ORDER, "mode": "derive_never_operator_enter",
        "state": "unprojected", "required_before_arm": True,
        "derivation_contract": IDENTITY_PIN_DERIVATION_CONTRACT,
        "identity_units": [units[name] for name in sorted(units)],
        "projection_receipt": None, "supersedes": []})
    return files


def registration(number, pass_number, repo_root=ROOT):
    pack_id = f"bytes-s{number}-p{pass_number}"
    path = Path("configs/campaigns") / pack_id
    value = json.loads((ROOT / "configs/b6/registration_template.json").read_bytes())
    value.update(pack_id=pack_id, title=f"BYTES sub-pack s{number}, pass {pass_number}",
                 question="Does decode energy follow format-derived bytes per token, resident size, or decode time?",
                 status="draft", kind="new", session_shape="fixed", plan_tree_ref=(path / "plan_tree.json").as_posix(),
                 target_sessions=1, minimum_sessions=1, estimators=deepcopy(ESTIMATORS),
                 flag_catalog="configs/b6/flag_catalog_b6.json",
                 stopping={"count": 1, "end_t0_before": "2026-11-02T00:00:00-08:00", "precision": None},
                 blinding_group="bytes", interleave="none", reference_cadence="session_half")
    if pass_number == 1:
        for estimator in value["estimators"]:
            estimator["version"] = AGREED_ESTIMATOR_VERSION
    value["modules"] = [{"module_id": "bytes-" + model_id, "kind": "floor", "phase": "decode",
                         "config_dirs": configs.config_dirs(model_id), "run_count": 50,
                         **module_estimate(model_id, number, repo_root)} for model_id in GROUPS[number - 1]]
    if pass_number == 2:
        value["modules"].reverse()
    value["pack_unit"] = [m["module_id"] for m in value["modules"]]
    value["bytes_pass"] = pass_number
    catalog = load_catalog(ROOT / value["flag_catalog"])
    value["flag_effects"] = {code: catalog.entry(code)["effect"] for code in sorted(catalog.codes)}
    value["flag_effects"]["cell.below_minimum"] = "DISCLOSE"
    value["flag_catalog_sha256"] = catalog.sha256
    value["draft_notes"] = [
        "Ruling: docs/design/bytes_pack_design.md R1-R8 and Addenda 1-8 at 298a292a7. Registration prose: docs/registrations/bytes_pack_v1.md, a draft with Mac and B2 slots open; not registered or armable.",
        "C6/C7 use blinding_group=bytes. Group keys: <pack_records_root>/bytes/blinding; withheld rows: <pack_records_root>/bytes/withheld/<pack_id>/<session_id>.runs.csv; missing-store flag: bytes.withheld_missing. The stage1-commit interface is validated now; its actual prediction hash is supplied at held-out release (BYTES-P0 ruling 7). Runtime config: configs/b6/loop_bytes.json.",
        "Lead blinding ruling 2026-10-20 (registration section 11): held-out configuration rows stay out of the analysis export, blinded in a withheld store, until the stage-1 prediction hash is recorded; rows visible before that carry no clock stamps.",
        "Stage 1 reads this pass's plan_tree_ref directly. Both passes have target/minimum 1/1 (minimum_sessions is read only by precision stopping, which BYTES does not use; that pass 2 is optional is a rule of the analysis, Addendum 6). loop.json base_order places all pass-1 packs before pass-2 packs, with reversed sub-pack order in pass 2.",
        "Addendum 5: 512 decode forward passes, one of which yields no returned token. The pinned stream_generate(max_tokens=512) includes look-ahead inside the measured request: e=E_dec/512, tau=T_dec/512, BW=b/tau; KV averages snapshots at 2048 and 2560 positions.",
        "C5 uses the six H/BY-H2 sizing rows in configs/b6/registration/sizing_b5.json, including measured T_stream_max_s and P = 2(B+WAIT)+fixed without an added reserve. C4 file and installed runtime evidence is in configs/b6/registration/identity_pins.json; full model stacks and frozen projection receipts remain unobserved.",
        "Estimator versions are null until the twin agrees with joulewise/bytes_analysis.py at the Addendum 8 bar; each version then becomes that file's SHA-256 at the agreeing pin (registration section 13). Cold gate and smoke fingerprints remain before first t0.",
        "Addendum 2 resolves R6: the Block-6 flag catalog is unchanged, including nonthermal exclusions. The flagged-inclusive line restores every catalog-excluded unit with valid energy records (Addenda 1 and 3).",
        "Model sources include HF cache snapshot directories; C4 file hashes follow their symlinks and bind tokenizer/config files and checkpoint quantization separately from observed installed packages. model.context_window is unused by the runtime. The desk build does not load a model or freeze an execution stack.",
        "Qwen3-8B-8bit file evidence, source roster and configs pin revision 48a0b75b1ae72503e21e1558d040bc227510ff06 and verify bits=8, group_size=64. Generated config copies preserve those exact source bytes.",
        "For single-model sub-packs s5 and s6, compose places the midpoint between the quad halves after 30 runs; analysis must not assume it splits models.",
        "Fixed packs bypass the 265-minute science cap. The native window maximum comes from the C5 programmed span plus the existing stage, pause and session-wait allowances, not the former s4 pilot estimate.",
        "Module minutes = C5 count * own member_allowance_s / 60, using the exact rational sizing operands and no additional margin. Shared references, calibration and custody stay in the full programmed span. Pass two reuses the same measured model costs in reverse order.",
    ]
    return value


def tree_files(value, repo_root):
    pack_id = value["pack_id"]
    pass_number = value["bytes_pass"]
    working = deepcopy(value)
    working["session_shape"] = "modular"
    reg = Registration(working)
    layout = compose.layout(queue.Selection((pack_id,), pass_number), {pack_id: reg}, repo_root)
    # compose decides whole-module placement and the shared midpoint. Give every
    # inherited stage a BYTES name before rendering its manifest and command ids.
    stages = []
    for stage in layout.stages:
        s = deepcopy(stage)
        s["stage_id"] = s["stage_id"].replace("beta-", pack_id + "-")
        stages.append(s)
    layout = replace(layout, stages=tuple(stages))
    keep = compose.smoke_keep(layout)
    tree, files = compose.render(layout)
    directory = Path(value["plan_tree_ref"]).parent
    # The fixed reader forbids '..' in config locators. Each compose floor
    # piece is already one whole committed manifest, as are the references.
    # Reuse those source manifests instead of render's relocated copies.
    for stage, source_stage in zip(tree["stage_graph"], layout.stages):
        entries = source_stage["entries"]
        if not entries:
            continue
        source = Path(entries[0]["config_path"]).parent / "order_manifest.json"
        raw = (Path(repo_root) / source).read_bytes()
        manifest = json.loads(raw)
        expected = [row["run_id"] for row in entries]
        if [row["run_id"] for row in manifest["executed_order"]] != expected:
            raise ValueError("compose piece is not a whole source manifest")
        stage["input"] = {"kind": "manifest", "path": source.as_posix(),
                          "manifest_id": manifest["manifest_id"], "sha256": configs.sha(raw)}
        stage["launch"]["commands"][0]["argv_template"]["arguments"][0]["value"] = source.parent.as_posix()
        stage.pop("spare_retry", None)  # Block 6 does not use the inherited spares.
    files = {}
    # These inherited BETA attachments describe a different workload/window.
    # Keep its common reference/launch scaffold, remove its asserted authority.
    for key in ("plan", "condition_families", "downstream_contract", "decode_workload", "runtime_budget"):
        tree.pop(key, None)
    tree.update(draft_status="draft", window_identity={"window_id": pack_id,
                "evidence_root_id": f"evidence-{pack_id}"},
                roots={"claim_root_leaf": f"runs_{pack_id}",
                       "bound_root_leaf": f"runs_{pack_id}_bound"},
                generator={"path": "scripts/bytes_plan_trees.py", "sha256": configs.sha(Path(__file__).read_bytes())},
                arm_attachments={}, bytes_pass=pass_number, blinding_group="bytes",
                module_order=[m["module_id"] for m in working["modules"]],
                draft_notes=value["draft_notes"])
    tree["arm_attachments"]["launch"] = launch_declaration(tree, repo_root)
    tree["attempt_policy"] = {"science_member_replacements": 0, "outcome_dependent_top_up": "forbidden",
                              "minimum_kept_units_per_stratum": 5, "authority": "R6; Block-6 catalog unchanged"}
    projected = identity_projection(tree, directory, repo_root)
    # The bracket reservation authenticates plan id/digest, without requiring
    # the old floor-plan schema. Bind BYTES membership, never BETA's plan.
    collection = {"schema_version": "joulewise.bytes_collection_plan.v1", "status": "draft",
                  "plan_id": pack_id, "pack_id": pack_id,
                  "pass": pass_number, "modules": working["modules"], "corpus": value["corpus"],
                  "minimum_kept_units_per_stratum": 5, "science": tree["science"],
                  "draft_notes": ["Draft collection membership and C5 module allowances; estimator versions remain null until the agreeing SHA, registration cold gate and smoke fingerprints remain before first t0."]}
    collection_raw = configs.raw_json(collection)
    collection_path = directory / "collection_plan.json"
    tree["plan"] = {"path": "collection_plan.json", "plan_id": collection["plan_id"],
                    "actual_sha256": configs.sha(collection_raw), "declared_sha256": configs.sha(collection_raw)}
    external = tree["external_inputs"]
    if not isinstance(external, Mapping):
        raise ValueError("template external_inputs must be a mapping")
    tree["external_inputs"] = {key: [ref for ref in refs
        if "d117_floor_qwen3-8b_v5" not in json.dumps(ref)] for key, refs in external.items()}
    cells = []
    covered = []
    for module in working["modules"]:
        module_id = module["module_id"]
        science = [row for row in tree["science"] if row["module_id"] == module_id]
        common = {"condition_family_id": module_id + "-decode", "metric": "phase_energy_j.decode",
                  "window_class": "phase", "target_precheck_path": ["phase", "decode"], "expected_n": 10}
        repeats = [row for row in science if row["role"] == "absolute_repeat"]
        quads = {}
        for row in science:
            if row["role"] == "comparative_abba_member":
                quads.setdefault(row["block_id"], {})[row["position"]] = row["run_id"]
        if len(repeats) != 10 or len(quads) != 10 or any(set(q) != {"A1", "B1", "B2", "A2"} for q in quads.values()):
            raise ValueError("BYTES requires ten repeats and ten complete quads per module")
        cells.extend([{**common, "cell_id": module_id + "-decode-absolute", "kind": "absolute",
                       "members": [{"bundle_id": row["run_id"]} for row in repeats]},
                      {**common, "cell_id": module_id + "-decode-comparative", "kind": "comparative",
                       "blocks": [{"block_id": block, "members": members} for block, members in quads.items()]}])
        covered.extend(row["run_id"] for row in repeats)
        covered.extend(run_id for members in quads.values() for run_id in members.values())
    if len(covered) != len(set(covered)) or set(covered) != {row["run_id"] for row in tree["science"]}:
        raise ValueError("extraction cells must cover every science run exactly once")
    extraction = configs.raw_json({"schema_version": "joulewise.detection_floor_extraction_spec.v1",
                                  "draft_status": "draft", "cells": cells})
    files["extraction_spec.json"] = extraction
    tree["downstream_contract"] = {"extraction_spec": {
        "path": (directory / "extraction_spec.json").as_posix(), "sha256": configs.sha(extraction)}}
    for stage in tree["stage_graph"]:
        for command in stage["launch"]["commands"]:
            for arg in command["argv_template"]["arguments"]:
                if arg == {"kind": "repo_path", "value": "configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.json"}:
                    arg["value"] = collection_path.as_posix()
    files["collection_plan.json"] = collection_raw
    files["plan_tree.json"] = configs.raw_json(tree)
    return {**{directory / path: raw for path, raw in files.items()}, **projected}, keep


def build_files(repo_root=ROOT):
    files = {}
    catalog = load_catalog(ROOT / "configs/b6/flag_catalog_b6.json")
    smoke_path = Path("configs/b6/smoke_keep.json")
    smoke = json.loads((Path(repo_root) / smoke_path).read_bytes())
    passes = {"1": [f"bytes-s{n}-p1" for n in range(1, 7)],
              "2": [f"bytes-s{n}-p2" for n in range(6, 0, -1)]}
    for number in range(1, 7):
        for pass_number in (1, 2):
            value = registration(number, pass_number, repo_root)
            errors = validate(Registration(value), catalog, root=repo_root)
            if errors:
                raise ValueError(f"{value['pack_id']}: {errors}")
            path = Path("configs/b6/packs") / value["pack_id"] / "registration.json"
            files[path] = configs.raw_json(value)
            trees, keep = tree_files(value, repo_root)
            files.update(trees)
            smoke[value["pack_id"]] = keep
    files[smoke_path] = configs.raw_json(smoke)
    loop_path = Path("configs/b6/loop.json")
    loop_raw = (Path(repo_root) / loop_path).read_text()
    loop = json.loads(loop_raw)
    bytes_ids = set(passes["1"] + passes["2"] + [f"bytes-s{n}" for n in range(1, 7)])
    loop["base_order"] = [p for p in loop["base_order"] if p not in bytes_ids] + passes["1"] + passes["2"]
    files[loop_path] = re.sub(r'("base_order"\s*:\s*)\[[^\]]*\]',
                              lambda m: m[1] + json.dumps(loop["base_order"]), loop_raw).encode()
    files[configs.PACK / "pass_order.json"] = configs.raw_json({
        "status": "draft", "blinding_group": "bytes", "passes": passes,
        "interleaving": "After replication round 1, then next BYTES slots after each replication round; replication and GAMMA order unchanged; lost attempts retry in the next BYTES slot."})
    return files


def generate(output_root=ROOT, check=False, source_root=ROOT):
    files = build_files(source_root)
    # Remove only the five obsolete generated files in each old pack. Preserve
    # any unrelated files; pass-specific packs replace the unreachable pass map.
    for n in range(1, 7):
        for leaf in ("registration.json", "plan_tree.json", "collection_plan.json",
                     "pass2/plan_tree.json", "pass2/collection_plan.json"):
            old = Path(output_root) / f"configs/b6/packs/bytes-s{n}" / leaf
            if old.exists():
                if check:
                    raise ValueError(f"obsolete BYTES pack file: {old}")
                old.unlink()
    for path, raw in files.items():
        target = Path(output_root) / path
        if check:
            if target.read_bytes() != raw:
                raise ValueError(f"generated bytes drifted: {path}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    generate(args.output_root, args.check)
    print(("verified" if args.check else "generated") + " 12 BYTES draft registrations and 12 fixed pass trees")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
