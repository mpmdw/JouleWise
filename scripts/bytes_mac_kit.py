#!/usr/bin/env python3
"""Generate the R8.6 non-claim Mac session; never register it or edit loop.json."""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.b5 import chain
from joulewise.b6 import compose, queue
from joulewise.b6.pack_registration import load

KIT = Path("configs/campaigns/bytes_mac_check")
LONG = ("llama-70b", "qwen35-122b", "qwen3-next-80b")
# R8.6 specifies five structural runs per model and twelve additional soak
# runs for 70B/122B. Test 7: threshold note §4 row 7 specifies two large runs
# at each end; design §14 alternates them with two reference runs at each end.
CHECK_RUNS = 5
SOAK_RUNS = 12
TEST7_PAIRS = 2


def raw_json(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def build_files(root=ROOT):
    root = Path(root)
    # Use the actual block-6 composer for the calibrated reference/launch
    # scaffold. The kit is a fixed session, with no pack registration at all.
    reg = load(root / "configs/b6/packs/bytes-s1-p1/registration.json")
    seed = compose.layout(queue.Selection((reg.pack_id,), 1), {reg.pack_id: reg}, root)
    roster = json.loads((root / "configs/campaigns/bytes_v1/roster.json").read_bytes())["models"]
    source_science = next(s for s in seed.stages if s["stage_id"].endswith("-absolute"))
    reference = next(s for s in seed.stages if s["stage_id"].endswith("-reference-start"))["entries"][0]
    files, members = {}, []

    def collection(label, conditions):
        stage = deepcopy(source_science)
        stage.update(stage_id="bytes-mac-check-" + label, entries=[], expected_count=len(conditions))
        directory = KIT / "stages" / label
        rows = []
        for index, (source, model_id, purpose, end) in enumerate(conditions, 1):
            cfg = json.loads((root / source["config_path"]).read_bytes())
            run_id = f"bytes-mac-check-{label}-r{index:02}"
            cfg["run_id"] = run_id
            cfg["hardware_target"]["notes"] = "R8.6 non-claim structural session; never a registered pack."
            cfg["run_metadata"]["tags"] = ["bytes-mac-check", "non-claim", "launch_lineage_required",
                "bytes-model=" + model_id, "bytes-purpose=" + purpose, "bytes-end=" + end]
            raw = raw_json(cfg)
            filename = run_id + ".json"
            files[directory / filename] = raw
            entry = {"run_id": run_id, "config": filename, "config_path": (directory / filename).as_posix(),
                     "config_sha256": sha(raw), "index": index, "rep": index,
                     "role": "absolute_repeat", "block_id": None, "block_index": index,
                     "position": None, "position_in_block": 1, "arm": None,
                     "model_tag": model_id + "-mlx", "workload": cfg["workload_profile"]["name"],
                     "module_id": "bytes-mac-check-" + model_id, "pack_id": "bytes-mac-check"}
            rows.append(entry)
            members.append({"run_id": run_id, "model_id": model_id, "purpose": purpose, "end": end,
                            "stage_id": stage["stage_id"], "non_claim": True,
                            "config_path": entry["config_path"]})
        files[directory / "order_manifest.json"] = raw_json({
            "schema_version": "joulewise.order_manifest.v1", "manifest_id": stage["stage_id"],
            "planned_n_bundles": len(rows), "executed_order": rows})
        stage["entries"] = rows
        return stage

    sources = {}
    for model in roster:
        model_id = model["model_id"]
        directory = Path("configs/campaigns/bytes_v1") / model_id / "01_decode_absolute"
        entry = json.loads((root / directory / "order_manifest.json").read_bytes())["executed_order"][0]
        sources[model_id] = {**entry, "config_path": (directory / entry["config"]).as_posix()}

    def transfer(end):
        return [collection(f"test7-{model_id}-{end}", [
            (source, mid, "test7", end) for _ in range(TEST7_PAIRS)
            for source, mid in ((sources[model_id], model_id), (reference, "reference"))]) for model_id in LONG]

    checks = [collection("check-" + mid, [(sources[mid], mid, "check", "middle")] * CHECK_RUNS)
              for mid in sources]
    soaks = [collection("soak-" + mid, [(sources[mid], mid, "soak", "middle")] * SOAK_RUNS)
             for mid in LONG[:2]]
    fixed = [deepcopy(s) for s in seed.stages if not any(
        s["stage_id"].startswith(m["module_id"] + "-") for m in reg.modules)]
    # Corpus/start precede test 7, then all checks, shared midpoint and soaks,
    # test 7 at the end, end references and closing calibration.
    stages = fixed[:5] + transfer("start") + checks + [fixed[5]] + soaks + transfer("end") + fixed[6:]
    for stage in stages:
        stage["stage_id"] = stage["stage_id"].replace("bytes-s1-p1", "bytes-mac-check")
        stage.pop("spare_retry", None)
    layout = replace(seed, session_id="bytes-mac-check", packs=("bytes-mac-check",),
                     stages=tuple(stages), fixed_bytes=None, campaign_id="bytes_mac_check")
    tree, _ = compose.render(layout)
    # Use whole source manifests, with repository paths the fixed reader accepts.
    # Render's default manifests relocate config paths; these committed inputs
    # avoid '..' locators and keep each config digest independently checkable.
    for stage, source in zip(tree["stage_graph"], stages):
        entries = source["entries"]
        if entries:
            manifest = Path(entries[0]["config_path"]).parent / "order_manifest.json"
            raw = files[manifest] if manifest in files else (root / manifest).read_bytes()
            value = json.loads(raw)
            stage["input"] = {"kind": "manifest", "path": manifest.as_posix(),
                              "manifest_id": value["manifest_id"], "sha256": sha(raw)}
            stage["launch"]["commands"][0]["argv_template"]["arguments"][0]["value"] = manifest.parent.as_posix()
    for key in ("condition_families", "downstream_contract", "decode_workload", "runtime_budget", "bytes_pass", "blinding_group", "draft_notes"):
        tree.pop(key, None)
    tree.update(non_claim=True, draft_status="non-claim", arm_attachments={},
                window_identity={"window_id": "bytes-mac-check", "evidence_root_id": "evidence-bytes-mac-check"},
                roots={"claim_root_leaf": "runs_bytes_mac_check", "bound_root_leaf": "runs_bytes_mac_check_bound"},
                generator={"path": "scripts/bytes_mac_kit.py", "sha256": sha(Path(__file__).read_bytes())})
    collection_plan = {"schema_version": "joulewise.bytes_mac_check.v1", "plan_id": "bytes-mac-check",
                       "non_claim": True, "members": members,
                       "check_runs_per_model": CHECK_RUNS, "soak_runs_per_model": SOAK_RUNS,
                       "test7_pairs_per_end": TEST7_PAIRS, "long_regimes": list(LONG),
                       "authority": "BYTES R2/R8.6; block-6 design §14; threshold note §4 test 7"}
    raw = raw_json(collection_plan)
    files[KIT / "collection_plan.json"] = raw
    tree["plan"] = {"path": "collection_plan.json", "plan_id": "bytes-mac-check",
                    "actual_sha256": sha(raw), "declared_sha256": sha(raw)}
    # Bind reservations to this kit rather than the inherited BETA floor plan.
    tree["external_inputs"] = [r for r in tree["external_inputs"] if "d117_floor_qwen3-8b_v5" not in json.dumps(r)]
    for stage in tree["stage_graph"]:
        for command in stage["launch"]["commands"]:
            for arg in command["argv_template"]["arguments"]:
                if arg == {"kind": "repo_path", "value": "configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.json"}:
                    arg["value"] = (KIT / "collection_plan.json").as_posix()
    chain.stage_plan(tree)
    files[KIT / "plan_tree.json"] = raw_json(tree)
    smoke_path = Path("configs/b6/smoke_keep.json")
    smoke = json.loads((root / smoke_path).read_bytes())
    smoke["bytes_mac_check"] = compose.smoke_keep(layout)
    files[smoke_path] = raw_json(smoke)
    return files


def generate(output_root=ROOT, *, check=False, source_root=ROOT):
    files = build_files(source_root)
    for path, raw in files.items():
        target = Path(output_root) / path
        if check:
            if target.read_bytes() != raw:
                raise ValueError("generated kit drifted: " + str(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    generate(args.output_root, check=args.check)
    print("verified non-claim Mac kit" if args.check else "generated non-claim Mac kit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
