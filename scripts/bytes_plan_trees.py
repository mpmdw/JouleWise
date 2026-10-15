#!/usr/bin/env python3
"""Freeze compose.layout output as BYTES draft fixed trees for both passes.

Pass one lives in each sub-pack's plan_tree.json; pass two in pass2/plan_tree.json.
The pass map is data for the future driver: stage 1 selects only plan_tree_ref
and does not yet consume pass_plan_tree_refs or reverse the BYTES slots.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.b6 import compose, queue
from joulewise.b6.pack_registration import Registration, validate
from joulewise.flags.catalog import load_catalog

spec = importlib.util.spec_from_file_location("bytes_configs", ROOT / "configs/campaigns/bytes_v1/generate_configs.py")
configs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(configs)
GROUPS = (("qwen3-1p7b", "qwen3-4b"), ("qwen3-8b", "qwen3-30b-a3b"),
          ("qwen3-14b", "qwen3-next-80b"), ("qwen3-32b", "qwen3-8b-8bit"),
          ("llama-70b",), ("qwen35-122b",))
# Planning only, from the pilot workload time + inherited 57.6 s idle and
# 5 s settle per run, x50, x1.2 margin. R8 Mac sizing supersedes these.

def estimate_minutes(model_id):
    pilot = next(s[3] for s in configs.ROSTER if s[0] == model_id)
    if pilot is None:
        return 150.0  # R1's explicit planning estimate for 8B-8bit
    value = json.loads((ROOT / "docs/design/bytes_pilot" / pilot).read_bytes())
    runs = value["runs"]
    seconds = max(r["total_s"] for r in runs)
    return round((seconds + 57.6 + 5.0) * 50 * 1.2 / 60, 3)


def registration(number):
    pack_id = f"bytes-s{number}"
    path = Path("configs/b6/packs") / pack_id
    value = json.loads((ROOT / "configs/b6/registration_template.json").read_bytes())
    value.update(pack_id=pack_id, title=f"BYTES sub-pack s{number}",
                 question="Does decode energy follow format-derived bytes per token, resident size, or decode time?",
                 status="draft", kind="new", session_shape="fixed", plan_tree_ref=(path / "plan_tree.json").as_posix(),
                 target_sessions=2, minimum_sessions=1, estimators=[], flag_catalog="configs/b6/flag_catalog_b6.json",
                 stopping={"count": 2, "end_t0_before": "2026-11-02T00:00:00-08:00", "precision": None},
                 blinding_group="bytes", interleave="none", reference_cadence="session_half")
    value["modules"] = [{"module_id": "bytes-" + model_id, "kind": "floor", "phase": "decode",
                         "config_dirs": configs.config_dirs(model_id), "run_count": 50,
                         "est_minutes": estimate_minutes(model_id)} for model_id in GROUPS[number - 1]]
    value["pack_unit"] = [m["module_id"] for m in value["modules"]]
    value["pass_plan_tree_refs"] = {"1": value["plan_tree_ref"], "2": (path / "pass2/plan_tree.json").as_posix()}
    catalog = load_catalog(ROOT / value["flag_catalog"])
    value["flag_effects"] = {code: catalog.entry(code)["effect"] for code in sorted(catalog.codes)}
    value["draft_notes"] = [
        "Ruling: docs/design/bytes_pack_design.md R1-R6; not registered or armable.",
        "One blinding_group=bytes is preserved as top-level data; stage-1 validator permits it but current blinding code does not consume it. C6/C7 remain R8 item 7.",
        "Stage 1 uses only plan_tree_ref: selecting pass_plan_tree_refs[2] and reversing BYTES slot order require the later driver before pass 2; do not collect pass 2 using pass 1's tree.",
        "R8 C4/C5 identity pins, runtime budget, contention, clock and disk gates await Mac desk checks; 8B-8bit revision is pending R8 item 5.",
        "R8 analysis, independent twin, estimator registration, cold gate and smoke fingerprints remain before first t0.",
        "R6 disagreement requiring an inclusion ruling before registration: 'catalog unchanged' retains 43 EXCLUDE_MEMBER and 19 EXCLUDE_WINDOW codes (including nonthermal), whereas 'the rest are flags' can mean nonthermal disclosure only. Drafts preserve the existing catalog pending that ruling.",
        "Planning minutes use pilot maximum request seconds plus inherited idle/settle, 50 runs and 20% margin; 8B-8bit uses R1's 150 minutes. These are not measured session footprints.",
    ]
    return value


def tree_files(value, pass_number, repo_root):
    pack_id = value["pack_id"]
    working = deepcopy(value)
    working["session_shape"] = "modular"
    if pass_number == 2:
        working["modules"].reverse()
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
    tree, files = compose.render(layout)
    directory = Path(value["pass_plan_tree_refs"][str(pass_number)]).parent
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
    tree.update(draft_status="draft", window_identity={"window_id": f"{pack_id}-pass{pass_number}",
                "evidence_root_id": f"evidence-{pack_id}-pass{pass_number}"},
                roots={"claim_root_leaf": f"runs_{pack_id}_pass{pass_number}",
                       "bound_root_leaf": f"runs_{pack_id}_pass{pass_number}_bound"},
                generator={"path": "scripts/bytes_plan_trees.py", "sha256": configs.sha(Path(__file__).read_bytes())},
                arm_attachments={}, bytes_pass=pass_number, blinding_group="bytes",
                module_order=[m["module_id"] for m in working["modules"]],
                draft_notes=value["draft_notes"])
    tree["attempt_policy"] = {"science_member_replacements": 0, "outcome_dependent_top_up": "forbidden",
                              "minimum_kept_units_per_stratum": 5, "authority": "R6; Block-6 catalog unchanged"}
    # The bracket reservation authenticates plan id/digest, without requiring
    # the old floor-plan schema. Bind BYTES membership, never BETA's plan.
    collection = {"schema_version": "joulewise.bytes_collection_plan.v1", "status": "draft",
                  "plan_id": f"{pack_id}-pass{pass_number}", "pack_id": pack_id,
                  "pass": pass_number, "modules": working["modules"], "corpus": value["corpus"],
                  "minimum_kept_units_per_stratum": 5, "science": tree["science"],
                  "draft_notes": ["Draft collection membership; analysis/estimator contracts remain R8 items 3-4 and registration remains item 8."]}
    collection_raw = configs.raw_json(collection)
    collection_path = directory / "collection_plan.json"
    tree["plan"] = {"path": "collection_plan.json", "plan_id": collection["plan_id"],
                    "actual_sha256": configs.sha(collection_raw), "declared_sha256": configs.sha(collection_raw)}
    tree["external_inputs"] = [ref for ref in tree["external_inputs"]
                               if "d117_floor_qwen3-8b_v5" not in json.dumps(ref)]
    for stage in tree["stage_graph"]:
        for command in stage["launch"]["commands"]:
            for arg in command["argv_template"]["arguments"]:
                if arg == {"kind": "repo_path", "value": "configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.json"}:
                    arg["value"] = collection_path.as_posix()
    files["collection_plan.json"] = collection_raw
    files["plan_tree.json"] = configs.raw_json(tree)
    return {directory / path: raw for path, raw in files.items()}


def build_files(repo_root=ROOT):
    files = {}
    catalog = load_catalog(ROOT / "configs/b6/flag_catalog_b6.json")
    for number in range(1, 7):
        value = registration(number)
        errors = validate(Registration(value), catalog, root=repo_root)
        if errors:
            raise ValueError(f"{value['pack_id']}: {errors}")
        path = Path("configs/b6/packs") / value["pack_id"] / "registration.json"
        files[path] = configs.raw_json(value)
        for pass_number in (1, 2):
            files.update(tree_files(value, pass_number, repo_root))
    files[configs.PACK / "pass_order.json"] = configs.raw_json({
        "status": "draft", "blinding_group": "bytes",
        "passes": {"1": [f"bytes-s{n}" for n in range(1, 7)], "2": [f"bytes-s{n}" for n in range(6, 0, -1)]},
        "interleaving": "After replication round 1, then next BYTES slots after each replication round; replication and GAMMA order unchanged; lost attempts retry in the next BYTES slot."})
    return files


def generate(output_root=ROOT, check=False, source_root=ROOT):
    files = build_files(source_root)
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
    print(("verified" if args.check else "generated") + " 6 BYTES draft registrations and 12 fixed pass trees")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
