#!/usr/bin/env python3
"""Generate the non-claim align pilot v1 Mac session; never register it or edit loop.json.

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

KIT = Path("configs/campaigns/align_pilot_v1")
PACK_ID = "align-pilot-v1"
SOURCE_KIT = Path("configs/campaigns/bytes_mac_check")
# Model-specific BYTES configs retain their exact model/revision pins.
SHADE_CACHE = "/Users/edr/.cache/joulewise/shade"
BLOCKS = (
    {"block": "A", "model_id": "qwen3-30b-a3b", "enable_thinking": True, "max_tokens": 4096, "max_turns": 12},
    {"block": "B", "model_id": "qwen3-30b-a3b", "enable_thinking": False, "max_tokens": 2048, "max_turns": 20},
    {"block": "C", "model_id": "qwen3-next-80b", "enable_thinking": None, "max_tokens": 2048, "max_turns": 20},
)
CONTEXT_CAP = 40960  # Lead ruling: same context regime for all blocks.
ALIGN_IDLE_S = 300  # quiet_mac_exploratory cooldown.cap_s; align members only.


def base_config_path(model_id):
    return Path(f"configs/campaigns/bytes_v1/{model_id}/01_decode_absolute/bytes-{model_id}-abs-r01.json")


def raw_json(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def ordered_members():
    """Pair adjacent ABBA / BAAB / ABBA blocks, one repeat, hint on."""
    members = []
    for index, block in enumerate(BLOCKS):
        for pair_index, pair in enumerate(pilot.PILOT_V0_PAIRS):
            conditions = pilot.PILOT_V0_CONDITIONS
            if (index + pair_index) % 2:
                conditions = tuple(reversed(conditions))
            for condition in conditions:
                spec = pilot.EpisodeSpec(
                    task_factory=pilot.FACTORY, condition=condition, seed=1,
                    max_turns=block["max_turns"], max_tokens=block["max_tokens"], temperature=0.0,
                    enable_thinking=block["enable_thinking"], max_context_tokens=CONTEXT_CAP,
                    task_kwargs={"cache_dir": SHADE_CACHE, "task_pair": pair, "give_hint": True})
                members.append({**block, "base_config": base_config_path(block["model_id"]).as_posix(), "spec": spec})
    return members


def ordered_specs():
    return tuple(m["spec"] for m in ordered_members())


def episode_config(base, spec, run_id, label, model_id):
    value = build_config(base, model_id + "-mlx", WORKLOAD_KIND, spec.max_tokens, spec.max_tokens, 1)
    value["run_id"] = run_id
    value["hardware_target"]["notes"] = "Align pilot v1 non-claim instrument check; never a registered pack."
    value["run_metadata"]["tags"] = [
        "align-pilot-v1", "non-claim", "launch_lineage_required", "align", WORKLOAD_KIND,
        "align-model=" + model_id, "align-condition=" + spec.condition,
        "align-task=" + spec.task_kwargs["task_pair"], f"align-repeat={spec.seed}", "align-stage=" + label]
    value["sampling"]["idle_seconds"] = ALIGN_IDLE_S
    value["workload_profile"] = {"name": WORKLOAD_KIND, "prompt_text": spec.to_text(),
                                 "repetitions": 1, "warmup_runs": base["workload_profile"]["warmup_runs"]}
    return BenchmarkConfig.from_mapping(value).to_dict()


def planning_sizing(tree, members, evidence):
    """Measured member law/scaffold; transferred context factors remain planning."""
    import math
    observations = evidence["member_observations"]
    x = [r["episode_s"] for r in observations]
    y = [r["member_s"] for r in observations]
    mx, my = math.fsum(x) / len(x), math.fsum(y) / len(y)
    slope = math.fsum((a-mx)*(b-my) for a,b in zip(x,y)) / math.fsum((a-mx)**2 for a in x)
    intercept = my - slope * mx
    residuals = [b - intercept - slope * a for a,b in zip(x,y)]
    factors = {phase: evidence["long_context_end"][phase + "_tok_s"] / evidence["long_context_start"][phase + "_tok_s"]
               for phase in ("prefill", "decode")}
    rows = []
    for block in BLOCKS:
        model = block["model_id"]
        rates = {phase: math.fsum(r[phase + "_tok_s"] for r in evidence["bytes_rates"][model]) / len(evidence["bytes_rates"][model])
                 for phase in ("prefill", "decode")}
        bound_rates = {phase: rates[phase] * factors[phase] for phase in rates}
        # Planning envelope inherited from the consult: full cap every turn,
        # full output budget, one second for local environment tool work.
        turn_s = CONTEXT_CAP / bound_rates["prefill"] + block["max_tokens"] / bound_rates["decode"] + 1
        episode_s = block["max_turns"] * turn_s
        member_s = intercept + slope * episode_s
        rows.append({**block, "short_context_rates_tok_s": rates, "bound_rates_tok_s": bound_rates,
                     "context_tokens": CONTEXT_CAP, "tool_s_per_turn": 1, "turn_upper_s": turn_s,
                     "episode_upper_s": episode_s, "member_upper_s": member_s,
                     "count": 4, "block_upper_s": 4 * member_s,
                     "flags": ["sizing.planning_bound_unmeasured"]})
    scaffold = sum(s["expected_count"] for s in tree["stage_graph"] if s["kind"] == "campaign_collection") - len(members)
    dwell = len(members) * (ALIGN_IDLE_S - evidence["pilot1_idle_s"])
    span = evidence["scaffold_s"] + math.fsum(r["block_upper_s"] for r in rows) + dwell
    count = len(members) + scaffold
    # Inherited v0 disk planning envelope; unmeasured for the larger models.
    bytes_per_member = 200_000_000
    return {"schema_version": "joulewise.b5_sizing.v1", "non_claim": True,
        "derivation": "OLS(member_s ~ 1 + episode_s), measured scaffold + sum(4*(intercept+slope*turns*(40960/prefill_bound+budget/decode_bound+1))) + 12*(300-pilot1_idle). Bound rates = BYTES short rates * pilot1 late/early factors. Tool second, transferred factors, new-model overhead and disk are planning, not measurements.",
        "packs": {PACK_ID: {"pack_id": PACK_ID, "flags": ["sizing.planning_bound_unmeasured"],
            "member_law": {"intercept_s": intercept, "slope": slope, "n": len(x),
                           "residual_sd_s": math.sqrt(math.fsum(r*r for r in residuals)/(len(x)-2)),
                           "largest_abs_residual_s": max(map(abs, residuals)), "flags": []},
            "long_context_factors": factors, "blocks": rows, "scaffold_s": evidence["scaffold_s"],
            "scaffold_flags": [], "dwell_increase_s": dwell,
            "member_count": count, "align_members": len(members), "scaffold_members": scaffold,
            "programmed_span_s": span, "T_stream_max_s": max(r["member_upper_s"] for r in rows) + ALIGN_IDLE_S-evidence["pilot1_idle_s"],
            "estimated_footprint_bytes": 2*count*bytes_per_member,
            "disk_derivation": {"peak_copies": 2, "B_bytes": count*bytes_per_member,
                                "extra_wait_peak_bytes": 0, "fixed_retained_bytes": 0}}}}


def kit_identity_pins(root, tree, members, *, identity=None):
    """File identities for every unit this kit dispatches.

    Without ``identity`` the hashes are copied from the BYTES kit's pins: the
    same pinned model directories, so the same files. At the Mac,
    registration/derive_identity_pins.py passes the real read-only hasher and
    local-file verification instead. Each align episode is its own identity unit
    (scripts/bytes_h_session.py align_unit_id): its spec is its workload.
    """
    from scripts.bytes_h_session import ALIGN_EPISODE, align_unit_id

    source = json.loads((root / "configs/bytes/identity_pins.json").read_bytes())
    inventory = {"artifacts": source["model_artifact_inventory"]}
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
                pinned = source["units"][model_id]
                artifact = inventory["artifacts"][model_id]
                if identity is not None:
                    if model["source"] not in hashed:
                        hashed[model["source"]] = identity(model["source"])
                    observed = hashed[model["source"]]
                    digest = observed.get("folded_sha256") or observed.get("sha256")
                    if observed.get("status") != "ok" or digest != pinned["model_artifact_sha256"]:
                        raise ValueError("local model differs from BYTES identity: " + model["source"])
                unit = {"model_source": model["source"], "model_name": model["name"],
                        "model_revision": model.get("revision"), "stack_identity": {},
                        "flags": ["runtime_stack_unobserved"],
                        "model_artifact_sha256": pinned["model_artifact_sha256"]}
                artifacts[name] = artifact
                units[name] = {**unit, "config_paths": []}
            units[name]["config_paths"].append(config_path.as_posix())
    for unit in units.values():
        unit["config_count"] = len(unit["config_paths"])
    tree_raw = members.get(KIT / "plan_tree.json") or (root / KIT / "plan_tree.json").read_bytes()
    document = {"schema": "joulewise.b5_identity_pins.v1", "status": "NON_CLAIM_FILE_IDENTITIES_ONLY", "non_claim": True, "units": units, "runtime_versions": source["runtime_versions"],
                "derivation": {"copied_from": "configs/bytes/identity_pins.json",
                               "source_sha256": sha((root / "configs/bytes/identity_pins.json").read_bytes()),
                               "tree_path": (KIT / "plan_tree.json").as_posix(), "tree_sha256": sha(tree_raw)}}
    return document, {"non_claim": True, "artifacts": dict(sorted(artifacts.items()))}


def build_files(root=ROOT):
    root = Path(root)
    reg = load(root / "configs/b6/packs/bytes-s1-p1/registration.json")
    seed = compose.layout(queue.Selection((reg.pack_id,), 1), {reg.pack_id: reg}, root)
    source_science = next(s for s in seed.stages if s["stage_id"].endswith("-absolute"))
    files, members = {}, []
    roster = ordered_members()
    # Keep the two science stages and midpoint reference of pilot 1. Put the
    # midpoint at a block boundary (A | B,C) so no configuration block is split.
    half = 4

    def collection(label, chunk, offset):
        stage = deepcopy(source_science)
        stage.update(stage_id=f"{PACK_ID}-{label}", entries=[], expected_count=len(chunk))
        directory = KIT / "stages" / label
        rows = []
        for index, member in enumerate(chunk, 1):
            spec = member["spec"]
            model_id = member["model_id"]
            base = json.loads((root / member["base_config"]).read_bytes())
            run_id = f"{PACK_ID}-{label}-e{offset + index:02}"
            raw = raw_json(episode_config(base, spec, run_id, label, model_id))
            filename = run_id + ".json"
            files[directory / filename] = raw
            entry = {"run_id": run_id, "config": filename, "config_path": (directory / filename).as_posix(),
                     "config_sha256": sha(raw), "index": index, "rep": index,
                     "role": "absolute_repeat", "block_id": None, "block_index": index,
                     "position": None, "position_in_block": 1, "arm": None,
                     "model_tag": model_id + "-mlx", "workload": WORKLOAD_KIND,
                     "module_id": f"{PACK_ID}-{model_id}", "pack_id": PACK_ID}
            rows.append(entry)
            members.append({"run_id": run_id, "stage_id": stage["stage_id"],
                            "task_pair": spec.task_kwargs["task_pair"], "condition": spec.condition,
                            "repeat": spec.seed, "ordinal": offset + index, "non_claim": True,
                            "model_id": model_id, "block": member["block"], "base_config": member["base_config"],
                            "config_path": entry["config_path"], "spec": json.loads(spec.to_text())})
        files[directory / "order_manifest.json"] = raw_json({
            "schema_version": "joulewise.order_manifest.v1", "manifest_id": stage["stage_id"],
            "planned_n_bundles": len(rows), "executed_order": rows})
        stage["entries"] = rows
        return stage

    first = collection("episodes-a", roster[:half], 0)
    second = collection("episodes-b", roster[half:], half)
    fixed = [deepcopy(s) for s in seed.stages if not any(
        s["stage_id"].startswith(m["module_id"] + "-") for m in reg.modules)]
    # Corpus and start references, the first half, the shared midpoint
    # reference, the second half, end references and closing calibration.
    stages = fixed[:5] + [first] + [fixed[5]] + [second] + fixed[6:]
    for stage in stages:
        stage["stage_id"] = stage["stage_id"].replace("bytes-s1-p1", PACK_ID)
        stage.pop("spare_retry", None)
    layout = replace(seed, session_id=PACK_ID, packs=(PACK_ID,), stages=tuple(stages),
                     fixed_bytes=None, campaign_id="align_pilot_v1")
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
                roots={"claim_root_leaf": "runs_align_pilot_v1", "bound_root_leaf": "runs_align_pilot_v1_bound"},
                generator={"path": "scripts/align_pilot_kit.py", "sha256": sha(Path(__file__).read_bytes())})
    collection_plan = {
        "schema_version": "joulewise.align_pilot.v1", "plan_id": PACK_ID, "non_claim": True,
        "status": "DRAFT_FOR_LEAD", "protocol": "docs/align/pilot_protocol_v1.md",
        "blocks": list(BLOCKS), "max_context_tokens": CONTEXT_CAP, "idle_seconds": ALIGN_IDLE_S, "shade_cache": SHADE_CACHE,
        "task_pairs": list(pilot.PILOT_V0_PAIRS), "conditions": list(pilot.PILOT_V0_CONDITIONS),
        "repeats": 1, "order_policy": "matched_condition_abba",
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
    for name in ("derive_identity_pins.py", "derive_sizing.py", "sizing_evidence.json"):
        files[registration / name] = (root / registration / name).read_bytes()
    files[KIT / "plan_tree.json"] = raw_json(tree)
    pins, inventory = kit_identity_pins(root, tree, files)
    files[registration / "identity_pins.json"] = raw_json(pins)
    files[registration / "model_artifact_inventory.json"] = raw_json(inventory)
    files[registration / "sizing_b5.json"] = raw_json(planning_sizing(tree, members, json.loads((root / KIT / "registration/sizing_evidence.json").read_bytes())))
    acceptance = json.loads((root / SOURCE_KIT / "registration/acceptance.json").read_bytes())
    acceptance["pack_id"] = PACK_ID
    files[registration / "acceptance.json"] = raw_json(acceptance)
    files[registration / "registration.json"] = raw_json({
        "pack_id": PACK_ID, "non_claim": True,
        "note": "Non-claim align pilot v1 archives; no grouped claim blinding or estimator registration."})
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


README = """# ALIGN pilot 2: capability screen (non-claim)

Generate with `python3 scripts/align_pilot_kit.py`; check with `--check`.
Protocol: `docs/align/pilot_protocol_v1.md`. Prepare/desk:
`scripts/align_pilot_session.py`. No registration, loop.json entry or claim.

Three four-member blocks: 30B-A3B thinking on (4096 x 12), thinking off
(2048 x 20), Next-80B instruct (2048 x 20). Both judge-free task pairs,
both conditions, hint on, one repeat, cap 40960. ABBA / BAAB / ABBA.
Align idle 300 s from cooldown.cap_s. Scaffold unchanged; midpoint after A.

Models are contiguous in the roster. The current campaign still launches a
fresh process and loads/cleans up MLX for each member; grouping does not
implement one persistent load per block. That requires separate authority.

`registration/derive_identity_pins.py --runtime-python <measurement python>`
reads local model files without loading MLX. `derive_sizing.py` records the
pilot-1 member law/scaffold and BYTES rate evidence; long-context transfer,
tool allowance, model overhead transfer and disk remain planning flags.
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
