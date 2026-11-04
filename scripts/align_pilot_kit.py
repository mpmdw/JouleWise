#!/usr/bin/env python3
"""Generate the non-claim align pilot v3 Mac session; never register it or edit loop.json.

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

KIT = Path("configs/campaigns/align_pilot_v3")
PACK_ID = "align-pilot-v3"
SOURCE_KIT = Path("configs/campaigns/bytes_mac_check")
# Model-specific BYTES configs retain their exact model/revision pins.
SHADE_CACHE = "/Users/edr/.cache/joulewise/shade"
BLOCKS = (
    {"block": "A", "model_id": "qwen3-30b-a3b", "enable_thinking": True, "max_tokens": 4096, "max_turns": 12},
)
CONTEXT_CAP = 40960  # Lead ruling: same context regime for all blocks.
ALIGN_IDLE_S = 300  # quiet_mac_exploratory cooldown.cap_s; align members only.


def base_config_path(model_id):
    return Path(f"configs/campaigns/bytes_v1/{model_id}/01_decode_absolute/bytes-{model_id}-abs-r01.json")


def raw_json(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


SAMPLER = {"temperature": 0.6, "top_p": 0.95, "top_k": 20, "min_p": 0}
TIME_GUARD_S = 120
# Independent pre-registration, cold-pass F1; never derive this table from the
# runtime law. Both conditions and each replay share the pair/seed-index value.
EXPECTED_EPISODE_SEEDS = {
    "bank_transfer_2": (1001552758911679671, 8139346561588466007, 286457666795484560,
                        304571486172760106, 16726874887165336052, 12685500607006618793,
                        9590288282068465104, 14994728377087409958, 10452994169483960014,
                        5212558227230803783, 12699264629597988571, 11636965341270972789),
    "spam_filter_update": (2570132319625341959, 4097311025052448992, 6169586229110087908,
                           18211783659995252033, 10515714233578474446, 8438206852662645142,
                           10900152454805747463, 2618380097672501688, 5842603386054999094,
                           2294347453123286324, 10022564881829687868, 3030301297807311119),
}
# Seed block k runs seed index SEED_BLOCKS[k-1]; block 1 and the four seed-1
# replays are the cross-session anchors shared with pilots 4 and 5.
SEED_BLOCKS = (1, 7, 8, 9, 10, 11)
ANCHOR_SEED_INDEX = 1


def ordered_members():
    """Six balanced four-cell seed blocks, four replays spread away from originals."""
    cells = (("spam_filter_update", "benign"), ("bank_transfer_2", "sabotage"),
             ("spam_filter_update", "sabotage"), ("bank_transfer_2", "benign"))
    members = []
    block = BLOCKS[0]
    # Replay seed 1 after seed blocks 2,3,4,6. The earliest replay is eight
    # positions after its original; all later ones are further away.
    replay_after = {2: cells[0], 3: cells[1], 4: cells[2], 6: cells[3]}
    def member(pair, condition, seed, replay=False):
        spec = pilot.EpisodeSpec(
            task_factory=pilot.FACTORY, condition=condition, seed=seed,
            max_turns=block["max_turns"], max_tokens=block["max_tokens"], temperature=SAMPLER["temperature"],
            enable_thinking=True, max_context_tokens=CONTEXT_CAP, prompt_cache="episode_prefix",
            sampler=SAMPLER, max_episode_seconds=TIME_GUARD_S,
            task_kwargs={"cache_dir": SHADE_CACHE, "task_pair": pair, "give_hint": True})
        return {**block, "repeat": 2 if replay else 1, "seed_index": seed, "is_replay": replay,
                "base_config": base_config_path(block["model_id"]).as_posix(), "spec": spec}
    for ordinal, seed in enumerate(SEED_BLOCKS, 1):
        for pair, condition in cells if ordinal % 2 else reversed(cells):
            members.append(member(pair, condition, seed))
        if ordinal in replay_after:
            members.append(member(*replay_after[ordinal], ANCHOR_SEED_INDEX, replay=True))
    return members


def ordered_specs():
    return tuple(m["spec"] for m in ordered_members())


def episode_config(base, spec, run_id, label, model_id, repeat=1):
    value = build_config(base, model_id + "-mlx", WORKLOAD_KIND, spec.max_tokens, spec.max_tokens, 1)
    value["run_id"] = run_id
    value["hardware_target"]["notes"] = "ALIGN pilot 4 non-claim cache instrument check; never a registered pack."
    value["run_metadata"]["tags"] = [
        "align-pilot-v3", "non-claim", "launch_lineage_required", "align", WORKLOAD_KIND,
        "align-model=" + model_id, "align-condition=" + spec.condition,
        "align-task=" + spec.task_kwargs["task_pair"], f"align-repeat={repeat}", "align-stage=" + label]
    value["sampling"]["idle_seconds"] = ALIGN_IDLE_S
    value["workload_profile"] = {"name": WORKLOAD_KIND, "prompt_text": spec.to_text(),
                                 "repetitions": 1, "warmup_runs": base["workload_profile"]["warmup_runs"]}
    return BenchmarkConfig.from_mapping(value).to_dict()


def planning_sizing(tree, members, evidence):
    """Pilot-3 A member law, pooled disk law, and explicit guarded cases."""
    import math
    def fit(rows, xkey, ykey):
        x, y = [r[xkey] for r in rows], [r[ykey] for r in rows]
        mx, my = math.fsum(x) / len(x), math.fsum(y) / len(y)
        slope = math.fsum((a-mx)*(b-my) for a,b in zip(x,y)) / math.fsum((a-mx)**2 for a in x)
        intercept = my - slope * mx
        residual = [b - intercept - slope*a for a,b in zip(x,y)]
        return {"intercept": intercept, "slope": slope, "n": len(x),
                "residual_sd": math.sqrt(math.fsum(r*r for r in residual)/(len(x)-2)),
                "largest_abs_residual": max(map(abs, residual)), "largest_positive_residual": max(residual)}
    observations = evidence["member_observations"]
    law = fit([r for r in observations if r["block"] == "A"], "episode_s", "member_s")
    disk = fit(observations, "member_s", "bundle_bytes")
    n = len(members)
    scaffold_count = sum(s["expected_count"] for s in tree["stage_graph"] if s["kind"] == "campaign_collection") - n
    scaffold_bytes = sum(r["bytes"] for r in evidence["scaffold_bundle_bytes"])
    def case(episode_s):
        member_s = law["intercept"] + law["slope"] * episode_s
        capture = n * (disk["intercept"] + disk["slope"] * member_s) + scaffold_bytes
        return {"episode_s": episode_s, "member_s": member_s, "align_s": n * member_s,
                "collection_span_s": n * member_s + evidence["scaffold_s"],
                "capture_bytes": math.ceil(capture), "peak_bytes": 2 * math.ceil(capture)}
    inputs = evidence["planning_turn_observations"]
    decode_rate = inputs["slowest_decode"]["planning_tok_s"]
    prefill_s = inputs["largest_fed_prefill"]["planning_s"]
    expected, observed, planning = case(110), case(120 + 41.9), case(120 + 4096 / decode_rate + prefill_s)
    upper_bytes = math.ceil(disk["intercept"] + disk["slope"] * planning["member_s"] + disk["largest_positive_residual"])
    B = n * upper_bytes + scaffold_bytes
    # scripts/run_campaign.py: HAZARD_MEMBER_CAP_S (1800) + effective wait
    # min(WAIT_CAP_S=1500, remaining SESSION_WAIT_BUDGET_S=7200): 3300
    # with unspent wait budget, 1800 after the session budget is spent.
    block = {**BLOCKS[0], "count": n, "episode_upper_s": planning["episode_s"],
             "member_upper_s": planning["member_s"], "block_upper_s": n * planning["member_s"],
             "member_upper_bytes": upper_bytes, "block_upper_bytes": n * upper_bytes,
             "member_cap_unspent_s": 3300, "member_cap_spent_s": 1800,
             "fits_unspent_cap": planning["member_s"] <= 3300, "fits_spent_cap": planning["member_s"] <= 1800,
             "flags": ["sizing.planning_bound_unmeasured"]}
    return {"schema_version": "joulewise.b5_sizing.v1", "non_claim": True,
        "derivation": "Pilot3 A OLS member_s = intercept + slope*episode_s (300 s idle already included); pooled pilot3 OLS bundle_bytes(member_s). Expected: mean spam100/bank120 =110 s; bank120 is a lower-bound planning input for a guard-limited episode unless it finishes first. Observed-turn case:120+41.9 s. Planning:120+4096/41.95+16.842 s; all pilot3 A turns, minimum observed decode rate rounded down to 0.01 tok/s and maximum observed fed-prefill phase rounded up to 0.001 s. The guard admits a whole turn; these are transfers, not physical or thermal guarantees. Scaffold added once; harvest+desk 5400 s separately, from observed pilot3 89 min (24 members) and pilot2 90 min (12 members); scaffold sets this time, not align count. Disk upper adds largest positive source residual.",
        "packs": {PACK_ID: {"pack_id": PACK_ID, "flags": ["sizing.planning_bound_unmeasured"],
            "member_law": {"intercept_s": law["intercept"], "slope": law["slope"], "n": law["n"],
                           "residual_sd_s": law["residual_sd"], "largest_abs_residual_s": law["largest_abs_residual"], "flags": []},
            "disk_member_law": disk, "blocks": [block], "scaffold_s": evidence["scaffold_s"],
            "scaffold_flags": [], "dwell_increase_s": 0, "harvest_and_desk_planned_s": 5400,
            "member_cap": {"unspent_s": 3300, "spent_s": 1800, "session_wait_budget_s": 7200},
            "expected_cached": expected, "observed_worst_turn": observed, "planning_case": planning,
            "planning_turn_observations": inputs,
            "member_count": n + scaffold_count, "align_members": n, "scaffold_members": scaffold_count,
            "programmed_span_s": planning["collection_span_s"], "T_stream_max_s": planning["member_s"],
            "estimated_footprint_bytes": 2 * B,
            "disk_derivation": {"formula": "ceil(OLS bundle_bytes(member_s) + largest positive pilot3 residual) per member; plus measured scaffold; two copies", "peak_copies": 2, "B_bytes": B,
                                "scaffold_bytes": scaffold_bytes, "extra_wait_peak_bytes": 0, "fixed_retained_bytes": 0}}}}


def kit_identity_pins(root, tree, members, *, identity=None):
    """File identities for every unit this kit dispatches.

    Without ``identity`` reuse verified pilot-2 Mac file hashes, authenticated
    against its receipt and the BYTES pins. At the Mac,
    registration/derive_identity_pins.py passes the real read-only hasher and
    local-file verification instead. Each align episode is its own identity unit
    (scripts/bytes_h_session.py align_unit_id): its spec is its workload.
    """
    from scripts.bytes_h_session import ALIGN_EPISODE, align_unit_id

    source = json.loads((root / "configs/bytes/identity_pins.json").read_bytes())
    inventory = {"artifacts": source["model_artifact_inventory"]}
    mac_dir = root / "configs/campaigns/align_pilot_v1/registration"
    mac_verification = json.loads((mac_dir / "local_file_verification.json").read_bytes())
    mac_raw = (mac_dir / "identity_pins.json").read_bytes()
    if sha(mac_raw) != mac_verification["identity_pins_sha256"]:
        raise ValueError("pilot2 Mac identity receipt does not match its pins")
    mac_pins = json.loads(mac_raw)
    mac_units = {u["model_source"]: u for u in mac_pins["units"].values()}

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
                pinned = mac_units[model["source"]]
                if pinned["model_artifact_sha256"] != source["units"][model_id]["model_artifact_sha256"]:
                    raise ValueError("Mac/BYTES artifact identities differ")
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
    document = {"schema": "joulewise.b5_identity_pins.v1", "status": "NON_CLAIM_FILE_IDENTITIES_ONLY", "non_claim": True, "units": units, "runtime_versions": mac_pins["runtime_versions"],
                "derivation": {"copied_from": "configs/bytes/identity_pins.json",
                               "source_sha256": sha((root / "configs/bytes/identity_pins.json").read_bytes()),
                               "mac_pins": (mac_dir / "identity_pins.json").relative_to(root).as_posix(),
                               "mac_pins_sha256": sha(mac_raw),
                               "mac_verification_sha256": sha((mac_dir / "local_file_verification.json").read_bytes()),
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
    # midpoint at a block boundary (A | C) so no configuration block is split.
    half = len(roster) // 2

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
            raw = raw_json(episode_config(base, spec, run_id, label, model_id, member["repeat"]))
            filename = run_id + ".json"
            files[directory / filename] = raw
            entry = {"run_id": run_id, "config": filename, "config_path": (directory / filename).as_posix(),
                     "config_sha256": sha(raw), "index": index, "rep": member["repeat"],
                     "role": "absolute_repeat", "block_id": None, "block_index": index,
                     "position": None, "position_in_block": 1, "arm": None,
                     "model_tag": model_id + "-mlx", "workload": WORKLOAD_KIND,
                     "module_id": f"{PACK_ID}-{model_id}", "pack_id": PACK_ID}
            rows.append(entry)
            members.append({"run_id": run_id, "stage_id": stage["stage_id"],
                            "task_pair": spec.task_kwargs["task_pair"], "condition": spec.condition,
                            "repeat": member["repeat"], "ordinal": offset + index, "non_claim": True,
                            "seed_index": member["seed_index"], "is_replay": member["is_replay"],
                            "expected_episode_seed": EXPECTED_EPISODE_SEEDS[spec.task_kwargs["task_pair"]][spec.seed - 1],
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
                     fixed_bytes=None, campaign_id="align_pilot_v3")
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
                roots={"claim_root_leaf": "runs_align_pilot_v3", "bound_root_leaf": "runs_align_pilot_v3_bound"},
                generator={"path": "scripts/align_pilot_kit.py", "sha256": sha(Path(__file__).read_bytes())})
    collection_plan = {
        "schema_version": "joulewise.align_pilot.v1", "plan_id": PACK_ID, "non_claim": True,
        "status": "DRAFT_FOR_LEAD", "protocol": "docs/align/pilot_protocol_v3.md",
        "prompt_cache": "episode_prefix", "repetition_policy": "observe_only",
        "pilot3_spec_differences": ["sampler", "temperature", "seed", "max_episode_seconds"],
        "sampler": SAMPLER, "seed_law": "align-p4-v1", "turn_seed_law": "align-p4-turn-v1",
        "seed_bits": 64, "max_episode_seconds": TIME_GUARD_S,
        "blocks": list(BLOCKS), "max_context_tokens": CONTEXT_CAP, "idle_seconds": ALIGN_IDLE_S, "shade_cache": SHADE_CACHE,
        "task_pairs": list(pilot.PILOT_V0_PAIRS), "conditions": list(pilot.PILOT_V0_CONDITIONS),
        "seeds_per_cell": 6, "seed_indices": list(SEED_BLOCKS), "replays_per_cell": 1, "anchor_seed_index": ANCHOR_SEED_INDEX,
        "cross_session_anchor_of": ["align-pilot-20261103T134903416190Z", "align-pilot-20261103T224628898457Z"],
        "order_policy": "alternating_four_cells_per_seed_block_replays_after_seed_blocks_2_3_4_6",
        "members": members}
    originals = {(m["task_pair"], m["condition"], m["seed_index"]): m["run_id"] for m in members if not m["is_replay"]}
    for m in members:
        if m["is_replay"]:
            m["replay_of"] = originals[m["task_pair"], m["condition"], m["seed_index"]]
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
    local = root / registration / "local_file_verification.json"
    if local.is_file() and "inherited_from" not in json.loads(local.read_bytes()):
        verified = json.loads(local.read_bytes())
        pinned_raw = (root / registration / "identity_pins.json").read_bytes()
        if verified["identity_pins_sha256"] != sha(pinned_raw):
            raise ValueError("local identity verification digest mismatch")
        local_pins = json.loads(pinned_raw)
        local_inventory = json.loads((root / registration / "model_artifact_inventory.json").read_bytes())
        if set(local_pins["units"]) != set(pins["units"]):
            raise ValueError("local identity unit roster changed; rederive pins")
        for name, unit in pins["units"].items():
            if any(local_pins["units"][name][k] != unit[k] for k in ("model_source", "model_artifact_sha256", "config_paths")):
                raise ValueError("local identity inputs changed; rederive pins")
        if local_pins["derivation"]["tree_sha256"] != sha(files[KIT / "plan_tree.json"]):
            raise ValueError("local identity tree changed; rederive pins")
        pins, inventory = local_pins, local_inventory
        files[registration / "local_file_verification.json"] = local.read_bytes()
    if not local.is_file() or "inherited_from" in json.loads(local.read_bytes()):
        inherited_path = root / "configs/campaigns/align_pilot_v1/registration/local_file_verification.json"
        inherited = json.loads(inherited_path.read_bytes())
        files[registration / "local_file_verification.json"] = raw_json({
            **inherited, "identity_pins_sha256": sha(raw_json(pins)),
            "scope": "Inherited pilot2 Mac file hashes and package observations; no new model hashing, no C4 stack identity",
            "inherited_from": inherited_path.relative_to(root).as_posix(), "inherited_sha256": sha(inherited_path.read_bytes())})
    files[registration / "identity_pins.json"] = raw_json(pins)
    files[registration / "model_artifact_inventory.json"] = raw_json(inventory)
    files[registration / "sizing_b5.json"] = raw_json(planning_sizing(tree, members, json.loads((root / KIT / "registration/sizing_evidence.json").read_bytes())))
    acceptance = json.loads((root / SOURCE_KIT / "registration/acceptance.json").read_bytes())
    acceptance["pack_id"] = PACK_ID
    files[registration / "acceptance.json"] = raw_json(acceptance)
    files[registration / "registration.json"] = raw_json({
        "pack_id": PACK_ID, "non_claim": True,
        "note": "Non-claim ALIGN pilot 4 archives; no grouped claim blinding or estimator registration."})
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


README = """# ALIGN pilot 4 (non-claim)

Generate: `python3 scripts/align_pilot_kit.py`; verify: `--check`.
Protocol: `docs/align/pilot_protocol_v3.md`. Session: `scripts/align_pilot_session.py`.
28 A-only members: 2 pairs x 2 conditions x seed blocks 1,7,8,9,10,11 + seed1 replay per cell.
Pilot-6 anchors: the seed-1 block (ordinals 1-4) and the four seed-1 replays (9,14,19,28)
repeat pilots 4-5 at the same ordinals; seeds 7-11 are new trajectories.
Qwen3 thinking sampler 0.6/0.95/20/0, per-turn SHA256 64-bit reseed; guard120s.
Seed-law task identifiers are exactly `shade/spam_filter_update` and
`shade/bank_transfer_2` (the task's task_pair attribute, not task_kwargs.task_pair).
Every member's expected_episode_seed is pre-registered in collection_plan.json.
Cache episode_prefix, cap40960, 12x4096, hint on, idle300s, repetition observe-only.
Odd seed-block ordinal: spam/benign,bank/sabotage,spam/sabotage,bank/benign; even reversed.
Replays after seed blocks2,3,4,6, all at least six members after originals.
25 scaffold members and calibration bracket unchanged. Hardware rehearsal required.
`registration/derive_sizing.py --pilot-session <pilot3 root>` derives file-digested
receipts without MLX. Identity pins retain verified Mac hashes and package readings.
Sizing transfers remain PROVISIONAL; harvest+desk allowance90min, no claim power.
The allowance comes from pilot3 89min (24 members) and pilot2 90min (12 members);
the scaffold sets the time, not align count. Bank expected120s is a lower bound
for a guard-limited episode unless it finishes first; an admitted turn completes.
`desk --no-harvest` writes inspection/ under the supplied session root: point it
at a copy of an archived session.
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
