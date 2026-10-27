#!/usr/bin/env python3
"""Generate the non-claim align pilot v0 Mac session; never register it or edit loop.json.

The fixed tree reuses the block-6 composer's calibrated scaffold exactly as
scripts/bytes_mac_kit.py does (bracket reservation, calibration captures,
NEG-8 corpus and bound derivation, start/midpoint/end references, verdict,
backup) and replaces the science stages with align_episode members. The
session runner is scripts/align_pilot_session.py. DRAFT for the lead.
"""
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
from joulewise.align.apple import pilot
from joulewise.align.apple.campaign import _counterbalanced
from joulewise.align.apple.workload import WORKLOAD_KIND
from joulewise.b5 import chain
from joulewise.b6 import compose, queue
from joulewise.b6.pack_registration import load
from joulewise.schemas import BenchmarkConfig
from scripts.generate_matrix import build_config

KIT = Path("configs/campaigns/align_pilot_v0")
PACK_ID = "align-pilot-v0"
SOURCE_KIT = Path("configs/campaigns/bytes_mac_check")
MODEL_ID = "qwen3-8b"
# The same Qwen3-8B-4bit member BYTES runs: model path, revision, MLX and
# powermetrics backends, sampling and idle policy are taken verbatim from it.
BASE_CONFIG = Path("configs/campaigns/bytes_v1/qwen3-8b/01_decode_absolute/bytes-qwen3-8b-abs-r01.json")
# The night agent runs as the Mac user; the cache is prepared at a desk with
# `python3.13 -m joulewise.align.apple.pilot prefetch --cache-dir` this path.
SHADE_CACHE = "/Users/edr/.cache/joulewise/shade"

# Planning parameters for sizing only; none is a measured rate. The pilot
# itself measures them (docs/align/pilot_protocol_v0.md, "Time budget").
PLANNING = {
    "decode_tok_s": 60,  # below the 69-73 tok/s 8B decode cited in docs/align/apple_path.md
    "prefill_tok_s": 400,  # planning guess for 8B-4bit prefill on M3 Max; unmeasured here
    "context_tokens_max": 32768,  # Qwen3-8B native context; every prompt is re-rendered in full
    "tool_s_per_turn": 1,  # SHADE tools mutate local mock objects only
    # member overhead: model load, BYTES idle 57.6 s, warm-up, 300 s cooldown
    # cap (quiet_mac_exploratory.json), post-window dwell, reduction.
    "member_overhead_s": 30 + 57.6 + 60 + 300 + 1 + 30,
    # Scaffold members (NEG-8 corpus, references) and the two calibration
    # captures are sized at the Mac from BYTES's registered allowances; this
    # planning row uses a flat allowance and flags it.
    "scaffold_member_s": 300,
    "calibration_capture_s": 900,
    "bytes_per_member": 200_000_000,
}


def raw_json(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def ordered_specs():
    """Repeat-major roster so ABBA pairs alternate task pairs through the session."""
    specs = pilot.pilot_specs(task_kwargs={"cache_dir": SHADE_CACHE})
    by_repeat = sorted(specs, key=lambda s: (s.seed, pilot.PILOT_V0_PAIRS.index(s.task_kwargs["task_pair"])))
    ordered, flags = _counterbalanced(by_repeat)
    if flags:
        raise ValueError("pilot roster must pair every benign episode with a sabotage episode")
    return ordered


def episode_config(base, spec, run_id, label):
    value = build_config(base, MODEL_ID + "-mlx", WORKLOAD_KIND, spec.max_tokens, spec.max_tokens, 1)
    value["run_id"] = run_id
    value["hardware_target"]["notes"] = "Align pilot v0 non-claim instrument check; never a registered pack."
    value["run_metadata"]["tags"] = [
        "align-pilot-v0", "non-claim", "launch_lineage_required", "align", WORKLOAD_KIND,
        "align-model=" + MODEL_ID, "align-condition=" + spec.condition,
        "align-task=" + spec.task_kwargs["task_pair"], f"align-repeat={spec.seed}", "align-stage=" + label]
    value["workload_profile"] = {"name": WORKLOAD_KIND, "prompt_text": spec.to_text(),
                                 "repetitions": 1, "warmup_runs": base["workload_profile"]["warmup_runs"]}
    return BenchmarkConfig.from_mapping(value).to_dict()


def planning_sizing(tree, members):
    p = PLANNING
    turn_s = p["context_tokens_max"] / p["prefill_tok_s"] + pilot.PILOT_V0_MAX_TOKENS / p["decode_tok_s"] + p["tool_s_per_turn"]
    episode_s = pilot.PILOT_V0_MAX_TURNS * turn_s
    member_s = episode_s + p["member_overhead_s"]
    scaffold = sum(s["expected_count"] for s in tree["stage_graph"] if s["kind"] == "campaign_collection") - len(members)
    captures = sum(1 for s in tree["stage_graph"] if s["kind"] == "calibration_capture")
    span = len(members) * member_s + scaffold * p["scaffold_member_s"] + captures * p["calibration_capture_s"]
    count = len(members) + scaffold
    footprint = 2 * count * p["bytes_per_member"]
    return {
        "schema_version": "joulewise.b5_sizing.v1", "non_claim": True,
        "derivation": ("PLANNING BOUND, not measured: episode = max_turns*(context_max/prefill + "
                       "max_tokens/decode + tool); member = episode + overhead; span = members*member + "
                       "scaffold*flat + captures*flat. Re-derive at the Mac before arming."),
        "packs": {PACK_ID: {
            "pack_id": PACK_ID, "flags": ["sizing.planning_bound_unmeasured"],
            "planning_parameters": dict(p), "episode_upper_s": episode_s,
            "member_count": count, "align_members": len(members), "scaffold_members": scaffold,
            "programmed_span_s": span, "T_stream_max_s": member_s,
            "estimated_footprint_bytes": footprint,
            # The fixed-kit arm encodes P = peak_copies * B + wait + fixed.
            "disk_derivation": {"peak_copies": 2, "B_bytes": count * p["bytes_per_member"],
                                "extra_wait_peak_bytes": 0, "fixed_retained_bytes": 0},
        }},
    }


def kit_identity_pins(root, tree, members, *, identity=None, versions=None, runtime_python=None):
    """File identities for every unit this kit dispatches.

    Without ``identity`` the hashes are copied from the BYTES kit's pins: the
    same two model directories, so the same files. At the Mac,
    registration/derive_identity_pins.py passes the real read-only hasher and
    interpreter census instead. Each align episode is its own identity unit
    (scripts/bytes_h_session.py align_unit_id): its spec is its workload.
    """
    from scripts.bytes_h_session import ALIGN_EPISODE, align_unit_id

    source = json.loads((root / SOURCE_KIT / "registration/identity_pins.json").read_bytes())
    inventory = json.loads((root / SOURCE_KIT / "registration/model_artifact_inventory.json").read_bytes())
    names = {u["model_source"]: name for name, u in source["units"].items()}
    units, artifacts, hashed = {}, {}, {}
    for stage in tree["stage_graph"]:
        ref = stage.get("input") or {}
        if stage["kind"] != "campaign_collection" or ref.get("kind") != "manifest":
            continue
        manifest = Path(ref["path"])
        raw = members.get(manifest) or (root / manifest).read_bytes()
        for row in json.loads(raw)["executed_order"][:stage["expected_count"]]:
            config_path = manifest.parent / row["config"]
            config = json.loads(members.get(config_path) or (root / config_path).read_bytes())
            model = config["model"]
            model_id = names[model["source"]]
            name = (align_unit_id(model_id, row["run_id"])
                    if config["workload_profile"]["name"] == ALIGN_EPISODE else model_id)
            if name not in units:
                if identity is None:
                    unit = deepcopy(source["units"][model_id])
                    unit["flags"] = sorted(set(unit.get("flags", [])) | {"file_identity_copied_from_bytes_mac_check"})
                    artifacts[name] = inventory["artifacts"][model_id]
                else:
                    if model["source"] not in hashed:
                        hashed[model["source"]] = identity(model["source"])
                    artifact = hashed[model["source"]]
                    digest = artifact.get("folded_sha256") or artifact.get("sha256")
                    if artifact.get("status") != "ok" or not digest:
                        raise ValueError("model files unavailable: " + model["source"])
                    unit = {"model_source": model["source"], "model_name": model["name"],
                            "model_revision": model.get("revision"), "stack_identity": {},
                            "flags": ["runtime_stack_unobserved"], "model_artifact_sha256": digest}
                    artifacts[name] = artifact
                units[name] = {**unit, "config_paths": []}
            units[name]["config_paths"].append(config_path.as_posix())
    for unit in units.values():
        unit["config_count"] = len(unit["config_paths"])
    document = {**{k: v for k, v in source.items() if k != "units"}, "units": units}
    document["derivation"] = {**source["derivation"], "tree_path": (KIT / "plan_tree.json").as_posix(),
                              "tree_sha256": sha((root / KIT / "plan_tree.json").read_bytes())
                              if identity is not None else "copied before the tree was final; re-derive at the Mac"}
    if identity is None:
        document["derivation"]["copied_from"] = (SOURCE_KIT / "registration/identity_pins.json").as_posix()
    else:
        document["runtime_python_observed"] = str(runtime_python)
        document["runtime_versions"] = versions(str(runtime_python))
    return document, {"non_claim": True, "artifacts": dict(sorted(artifacts.items()))}


def build_files(root=ROOT):
    root = Path(root)
    reg = load(root / "configs/b6/packs/bytes-s1-p1/registration.json")
    seed = compose.layout(queue.Selection((reg.pack_id,), 1), {reg.pack_id: reg}, root)
    source_science = next(s for s in seed.stages if s["stage_id"].endswith("-absolute"))
    base = json.loads((root / BASE_CONFIG).read_bytes())
    files, members = {}, []
    specs = ordered_specs()
    half = len(specs) // 2

    def collection(label, chunk, offset):
        stage = deepcopy(source_science)
        stage.update(stage_id=f"{PACK_ID}-{label}", entries=[], expected_count=len(chunk))
        directory = KIT / "stages" / label
        rows = []
        for index, spec in enumerate(chunk, 1):
            run_id = f"{PACK_ID}-{label}-e{offset + index:02}"
            raw = raw_json(episode_config(base, spec, run_id, label))
            filename = run_id + ".json"
            files[directory / filename] = raw
            entry = {"run_id": run_id, "config": filename, "config_path": (directory / filename).as_posix(),
                     "config_sha256": sha(raw), "index": index, "rep": index,
                     "role": "absolute_repeat", "block_id": None, "block_index": index,
                     "position": None, "position_in_block": 1, "arm": None,
                     "model_tag": MODEL_ID + "-mlx", "workload": WORKLOAD_KIND,
                     "module_id": f"{PACK_ID}-{MODEL_ID}", "pack_id": PACK_ID}
            rows.append(entry)
            members.append({"run_id": run_id, "model_id": MODEL_ID, "stage_id": stage["stage_id"],
                            "task_pair": spec.task_kwargs["task_pair"], "condition": spec.condition,
                            "repeat": spec.seed, "ordinal": offset + index, "non_claim": True,
                            "config_path": entry["config_path"], "spec": json.loads(spec.to_text())})
        files[directory / "order_manifest.json"] = raw_json({
            "schema_version": "joulewise.order_manifest.v1", "manifest_id": stage["stage_id"],
            "planned_n_bundles": len(rows), "executed_order": rows})
        stage["entries"] = rows
        return stage

    first = collection("episodes-a", specs[:half], 0)
    second = collection("episodes-b", specs[half:], half)
    fixed = [deepcopy(s) for s in seed.stages if not any(
        s["stage_id"].startswith(m["module_id"] + "-") for m in reg.modules)]
    # Corpus and start references, the first half, the shared midpoint
    # reference, the second half, end references and closing calibration.
    stages = fixed[:5] + [first] + [fixed[5]] + [second] + fixed[6:]
    for stage in stages:
        stage["stage_id"] = stage["stage_id"].replace("bytes-s1-p1", PACK_ID)
        stage.pop("spare_retry", None)
    layout = replace(seed, session_id=PACK_ID, packs=(PACK_ID,), stages=tuple(stages),
                     fixed_bytes=None, campaign_id="align_pilot_v0")
    tree, _ = compose.render(layout)
    for stage, source in zip(tree["stage_graph"], stages):
        entries = source["entries"]
        if entries:
            manifest = Path(entries[0]["config_path"]).parent / "order_manifest.json"
            raw = files[manifest] if manifest in files else (root / manifest).read_bytes()
            value = json.loads(raw)
            stage["input"] = {"kind": "manifest", "path": manifest.as_posix(),
                              "manifest_id": value["manifest_id"], "sha256": sha(raw)}
            stage["launch"]["commands"][0]["argv_template"]["arguments"][0]["value"] = manifest.parent.as_posix()
    # The scaffold reads the sealed NEG-8 corpus and window-reference
    # manifests exactly as the frozen BYTES Mac check tree does (the moving
    # pass-1 seed names pack-local copies the item-H view cannot relocate).
    frozen = json.loads((root / SOURCE_KIT / "plan_tree.json").read_bytes())
    scaffold = {s["stage_id"].removeprefix("bytes-mac-check-"): s for s in frozen["stage_graph"]}
    for stage in tree["stage_graph"]:
        source = scaffold.get(stage["stage_id"].removeprefix(PACK_ID + "-"))
        if source and (source.get("input") or {}).get("kind") == "manifest" and stage["kind"] == "campaign_collection":
            if source["expected_count"] != stage["expected_count"]:
                raise ValueError("scaffold count differs from the frozen kit: " + stage["stage_id"])
            stage["input"] = deepcopy(source["input"])
            stage["launch"]["commands"][0]["argv_template"]["arguments"][0] = deepcopy(
                source["launch"]["commands"][0]["argv_template"]["arguments"][0])
    for key in ("condition_families", "downstream_contract", "decode_workload", "runtime_budget",
                "bytes_pass", "blinding_group", "draft_notes"):
        tree.pop(key, None)
    tree.update(non_claim=True, draft_status="non-claim", arm_attachments={},
                window_identity={"window_id": PACK_ID, "evidence_root_id": "evidence-" + PACK_ID},
                roots={"claim_root_leaf": "runs_align_pilot_v0", "bound_root_leaf": "runs_align_pilot_v0_bound"},
                generator={"path": "scripts/align_pilot_kit.py", "sha256": sha(Path(__file__).read_bytes())})
    collection_plan = {
        "schema_version": "joulewise.align_pilot.v0", "plan_id": PACK_ID, "non_claim": True,
        "status": "DRAFT_FOR_LEAD", "protocol": "docs/align/pilot_protocol_v0.md",
        "model_id": MODEL_ID, "base_config": BASE_CONFIG.as_posix(), "shade_cache": SHADE_CACHE,
        "task_pairs": list(pilot.PILOT_V0_PAIRS), "conditions": list(pilot.PILOT_V0_CONDITIONS),
        "repeats": pilot.PILOT_V0_REPEATS, "max_turns": pilot.PILOT_V0_MAX_TURNS,
        "max_tokens_per_turn": pilot.PILOT_V0_MAX_TOKENS, "order_policy": "matched_condition_abba",
        "members": members}
    raw = raw_json(collection_plan)
    files[KIT / "collection_plan.json"] = raw
    tree["plan"] = {"path": "collection_plan.json", "plan_id": PACK_ID,
                    "actual_sha256": sha(raw), "declared_sha256": sha(raw)}
    tree["external_inputs"] = [r for r in tree["external_inputs"] if "d117_floor_qwen3-8b_v5" not in json.dumps(r)]
    for stage in tree["stage_graph"]:
        for command in stage["launch"]["commands"]:
            for arg in command["argv_template"]["arguments"]:
                if arg == {"kind": "repo_path", "value": "configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.json"}:
                    arg["value"] = (KIT / "collection_plan.json").as_posix()
    chain.stage_plan(tree)
    # No plan_tree.sha256 here: the session's measurement view writes the
    # staged tree's sidecar itself (scripts/bytes_h_session.py).
    files[KIT / "plan_tree.json"] = raw_json(tree)
    files[KIT / "README.md"] = README.encode()
    registration = KIT / "registration"
    pins, inventory = kit_identity_pins(root, tree, files)
    files[registration / "identity_pins.json"] = raw_json(pins)
    files[registration / "model_artifact_inventory.json"] = raw_json(inventory)
    files[registration / "sizing_b5.json"] = raw_json(planning_sizing(tree, members))
    acceptance = json.loads((root / SOURCE_KIT / "registration/acceptance.json").read_bytes())
    acceptance["pack_id"] = PACK_ID
    files[registration / "acceptance.json"] = raw_json(acceptance)
    files[registration / "registration.json"] = raw_json({
        "pack_id": PACK_ID, "non_claim": True,
        "note": "Non-claim align pilot v0 archives; no grouped claim blinding or estimator registration."})
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


README = """# Align pilot v0: non-claim Mac instrument check (DRAFT for the lead)

Generated by `python3.13 scripts/align_pilot_kit.py`; verify with `--check`.
Protocol: `docs/align/pilot_protocol_v0.md`. Session runner:
`scripts/align_pilot_session.py` (prepare / install / desk), the BYTES item-H
runner's prepare and install with this kit. It has no pack registration, never
enters loop.json/base_order and is never claim data.

The fixed tree keeps the block-6 calibrated scaffold of the BYTES Mac check
(bracket reservation, pre/post calibration, 18 NEG-8 corpus members and the
bound derivation, 3 start, 1 midpoint and 3 end references, verdict, backup)
and runs 12 `align_episode` members of Qwen3-8B-4bit (the BYTES qwen3-8b
source, revision 545dc425): SHADE-Arena pairs `spam_filter_update` and
`bank_transfer_2`, benign and sabotage, three greedy repeats, matched ABBA,
six before and six after the midpoint reference. Each member runs one whole
episode (at most 12 turns of at most 1,536 generated tokens) under the
unchanged controller, powermetrics sampling and hazard policy.

Before the first arm, at a desk on the Mac (no agent session active while
anything is armed):

1. `python3.13 -m joulewise.align.apple.pilot prefetch --cache-dir /Users/edr/.cache/joulewise/shade`
   (one public HTTPS git fetch of jkutaso/SHADE-Arena at 6614e771, 2.9 MB,
   verified against the 151-file manifest). Members never fetch; a missing or
   changed cache stops each member at prepare as runtime_unavailable.
2. Install the SHADE environment packages into the measurement `.venv`
   (docs/align/shade_port.md, "What can run offline"); no service is called.
3. Re-derive `registration/identity_pins.json` and
   `model_artifact_inventory.json` with `registration/derive_identity_pins.py
   --runtime-python <measurement .venv python>` (the committed copies carry the
   BYTES kit's file hashes for the same two model directories).
4. Replace the planning row in `registration/sizing_b5.json`
   (`sizing.planning_bound_unmeasured`) with the scaffold allowances BYTES
   registered, or accept the planning bound as the window maximum.

The planning sizing is an upper bound from stated rates, not a measurement.
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    generate(args.output_root, check=args.check)
    print("verified align pilot kit" if args.check else "generated align pilot kit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
