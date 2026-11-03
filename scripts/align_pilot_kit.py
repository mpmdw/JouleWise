#!/usr/bin/env python3
"""Generate the non-claim align pilot v2 Mac session; never register it or edit loop.json.

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

KIT = Path("configs/campaigns/align_pilot_v2")
PACK_ID = "align-pilot-v2"
SOURCE_KIT = Path("configs/campaigns/bytes_mac_check")
# Model-specific BYTES configs retain their exact model/revision pins.
SHADE_CACHE = "/Users/edr/.cache/joulewise/shade"
BLOCKS = (
    {"block": "A", "model_id": "qwen3-30b-a3b", "enable_thinking": True, "max_tokens": 4096, "max_turns": 12},
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
    """Contiguous A/C; alternating pair order and matched condition order."""
    members = []
    for block in BLOCKS:
        for repeat in range(1, 4):
            pairs = pilot.PILOT_V0_PAIRS if repeat % 2 else tuple(reversed(pilot.PILOT_V0_PAIRS))
            for pair in pairs:
                pair_index = pilot.PILOT_V0_PAIRS.index(pair)
                conditions = pilot.PILOT_V0_CONDITIONS
                if (repeat - 1 + pair_index) % 2:
                    conditions = tuple(reversed(conditions))
                for condition in conditions:
                    spec = pilot.EpisodeSpec(
                        task_factory=pilot.FACTORY, condition=condition, seed=1,
                        max_turns=block["max_turns"], max_tokens=block["max_tokens"], temperature=0.0,
                        enable_thinking=block["enable_thinking"], max_context_tokens=CONTEXT_CAP,
                        prompt_cache="episode_prefix",
                        task_kwargs={"cache_dir": SHADE_CACHE, "task_pair": pair, "give_hint": True})
                    members.append({**block, "repeat": repeat,
                                    "base_config": base_config_path(block["model_id"]).as_posix(), "spec": spec})
    return members


def ordered_specs():
    return tuple(m["spec"] for m in ordered_members())


def episode_config(base, spec, run_id, label, model_id, repeat=1):
    value = build_config(base, model_id + "-mlx", WORKLOAD_KIND, spec.max_tokens, spec.max_tokens, 1)
    value["run_id"] = run_id
    value["hardware_target"]["notes"] = "ALIGN pilot 3 non-claim cache instrument check; never a registered pack."
    value["run_metadata"]["tags"] = [
        "align-pilot-v2", "non-claim", "launch_lineage_required", "align", WORKLOAD_KIND,
        "align-model=" + model_id, "align-condition=" + spec.condition,
        "align-task=" + spec.task_kwargs["task_pair"], f"align-repeat={repeat}", "align-stage=" + label]
    value["sampling"]["idle_seconds"] = ALIGN_IDLE_S
    value["workload_profile"] = {"name": WORKLOAD_KIND, "prompt_text": spec.to_text(),
                                 "repetitions": 1, "warmup_runs": base["workload_profile"]["warmup_runs"]}
    return BenchmarkConfig.from_mapping(value).to_dict()


def planning_sizing(tree, members, evidence):
    """Cache envelope with pilot-2 timing/disk laws; all transfers flagged."""
    import math

    def fit(x, y):
        mx, my = math.fsum(x) / len(x), math.fsum(y) / len(y)
        slope = math.fsum((a-mx)*(b-my) for a,b in zip(x,y)) / math.fsum((a-mx)**2 for a in x)
        intercept = my - slope * mx
        residuals = [b - intercept - slope*a for a,b in zip(x,y)]
        return {"intercept": intercept, "slope": slope, "n": len(x),
                "residual_sd": math.sqrt(math.fsum(r*r for r in residuals)/(len(x)-2)),
                "largest_abs_residual": max(map(abs, residuals)),
                "largest_positive_residual": max(residuals)}

    observations = evidence["member_observations"]
    law = fit([r["episode_s"] for r in observations], [r["member_s"] for r in observations])
    disk = fit([r["member_s"] for r in observations], [r["bundle_bytes"] for r in observations])
    factors = {"prefill": 1.0, "decode": 1.0}
    tool_s = evidence["tool_s_per_turn"]
    calls_per_turn = evidence["tool_calls_per_turn_observed_max"]
    observation_s = evidence["state_observation_s_per_call"]
    tool_allowance = evidence["tool_allowance_s_per_turn"]
    first_prompt = evidence["smallest_first_prompt_tokens"]
    dwell_per_member = ALIGN_IDLE_S - evidence["pilot2_idle_s"]
    # scripts/run_campaign.py: HAZARD_MEMBER_CAP_S + min(WAIT_CAP_S,
    # remaining session wait budget); no runner change.
    cap_unspent, cap_spent = 1800 + 1500, 1800
    rows = []
    for block in BLOCKS:
        model = block["model_id"]
        rates = {phase: min(r[phase + "_tok_s"] for r in evidence["phase_rates"][block["block"]])
                 for phase in ("prefill", "decode")}
        bound_rates = rates
        prompt_bound = CONTEXT_CAP - block["max_tokens"]

        def bound(turns):
            decode = min(turns * block["max_tokens"], CONTEXT_CAP - first_prompt)
            prefill = CONTEXT_CAP + turns * block["max_tokens"]
            episode = prefill / bound_rates["prefill"] + decode / bound_rates["decode"] + turns * tool_allowance
            return prefill, decode, episode, law["intercept"] + law["slope"] * episode + dwell_per_member

        turns = block["max_turns"]
        while turns and bound(turns)[3] > cap_unspent:
            turns -= 1
        if turns != block["max_turns"]:
            raise ValueError(f"block {block['block']} needs max_turns={turns}; update BLOCKS and regenerate")
        prefill, decode, episode_s, member_s = bound(turns)
        member_bytes = math.ceil(disk["intercept"] + disk["slope"] * member_s + disk["largest_positive_residual"])
        rows.append({**block, "short_context_rates_tok_s": rates, "bound_rates_tok_s": bound_rates,
                     "prompt_tokens_per_turn_upper": prompt_bound, "first_prompt_lower_tokens": first_prompt,
                     "episode_prefill_tokens_upper": prefill, "episode_decode_tokens_upper": decode,
                     "decode_if_reasoning_retained_upper": min(turns * block["max_tokens"], CONTEXT_CAP - first_prompt),
                     "tool_s_per_turn": tool_s, "tool_calls_per_turn_observed_max": calls_per_turn,
                     "state_observation_s_per_call": observation_s, "tool_allowance_s_per_turn": tool_allowance,
                     "episode_upper_s": episode_s, "idle_increase_s": dwell_per_member, "member_upper_s": member_s,
                     "member_cap_unspent_s": cap_unspent, "member_cap_spent_s": cap_spent,
                     "fits_unspent_cap": member_s <= cap_unspent, "fits_spent_cap": member_s <= cap_spent,
                     "count": 12, "block_upper_s": 12 * member_s,
                     "member_upper_bytes": member_bytes, "block_upper_bytes": 12 * member_bytes,
                     "flags": ["sizing.planning_bound_unmeasured"]})
    scaffold = sum(s["expected_count"] for s in tree["stage_graph"] if s["kind"] == "campaign_collection") - len(members)
    dwell = len(members) * dwell_per_member
    span = evidence["scaffold_s"] + math.fsum(r["block_upper_s"] for r in rows)
    count = len(members) + scaffold
    scaffold_bytes = sum(r["bytes"] for r in evidence["scaffold_bundle_bytes"])
    B = sum(r["block_upper_bytes"] for r in rows) + scaffold_bytes
    forecasts = [r for r in evidence["cache_trajectory_forecasts"] if r["block"] in {b["block"] for b in BLOCKS}]
    expected_members = [law["intercept"] + law["slope"] * r["cached_episode_forecast_s"] for r in forecasts]
    expected_align = 3 * math.fsum(expected_members)
    expected_bytes = 3 * math.fsum(disk["intercept"] + disk["slope"] * t for t in expected_members) + scaffold_bytes
    uncached_align = 3 * math.fsum(r["member_s"] for r in observations if r["block"] in {b["block"] for b in BLOCKS})
    return {"schema_version": "joulewise.b5_sizing.v1", "non_claim": True,
        "derivation": "Cache planning: prefill <= cap + turns*budget, conditional on each rewind <= one output budget (whole-cache rebuilds can exceed this transferred bound). Decode <= min(turns*budget,cap-smallest pilot2 first prompt). Rates are the slowest pilot2 prefill/decode phase for this block. Episode = prefill/rate + decode/rate + turns*pilot1 tool allowance. Member = pilot2 OLS intercept+slope*episode; idle 300 s already included. Scaffold added once. Rehearsal must replace transfers; not a physical worst-case guarantee.",
        "packs": {PACK_ID: {"pack_id": PACK_ID, "flags": ["sizing.planning_bound_unmeasured"],
            "member_law": {"intercept_s": law["intercept"], "slope": law["slope"], "n": law["n"],
                           "residual_sd_s": law["residual_sd"], "largest_abs_residual_s": law["largest_abs_residual"], "flags": []},
            "long_context_factors": factors, "blocks": rows, "scaffold_s": evidence["scaffold_s"],
            "scaffold_flags": [], "dwell_increase_s": dwell,
            "member_cap": {"unspent_s": cap_unspent, "spent_s": cap_spent, "session_wait_budget_s": 7200,
                           "spent_corner": "Only repeated failed idle admissions spend the budget: a nonquiet Mac, already physics-flagged; lead accepts this corner."},
            "expected_cached": {"align_s": expected_align, "collection_span_s": expected_align + evidence["scaffold_s"],
                                "capture_bytes": expected_bytes, "peak_bytes": 2 * expected_bytes,
                                "derivation": evidence["forecast_derivation"]},
            "no_cache_savings": {"align_s": uncached_align, "collection_span_s": uncached_align + evidence["scaffold_s"],
                                 "derivation": "three times measured pilot2 A/C member durations plus measured scaffold"},
            "member_count": count, "align_members": len(members), "scaffold_members": scaffold,
            "programmed_span_s": span, "T_stream_max_s": max(r["member_upper_s"] for r in rows),
            "estimated_footprint_bytes": 2 * B,
            "disk_member_law": disk,
            "disk_derivation": {"formula": "ceil(OLS bundle_bytes(member_s) + largest positive pilot2 residual) per block member; sum + measured scaffold bytes; peak copies=2 (capture plus backup)",
                                "peak_copies": 2, "B_bytes": B, "scaffold_bytes": scaffold_bytes,
                                "extra_wait_peak_bytes": 0, "fixed_retained_bytes": 0}}}}


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
                     fixed_bytes=None, campaign_id="align_pilot_v2")
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
                roots={"claim_root_leaf": "runs_align_pilot_v2", "bound_root_leaf": "runs_align_pilot_v2_bound"},
                generator={"path": "scripts/align_pilot_kit.py", "sha256": sha(Path(__file__).read_bytes())})
    collection_plan = {
        "schema_version": "joulewise.align_pilot.v1", "plan_id": PACK_ID, "non_claim": True,
        "status": "DRAFT_FOR_LEAD", "protocol": "docs/align/pilot_protocol_v2.md",
        "prompt_cache": "episode_prefix", "repetition_policy": "observe_only",
        "pilot2_spec_differences": ["prompt_cache"],
        "blocks": list(BLOCKS), "max_context_tokens": CONTEXT_CAP, "idle_seconds": ALIGN_IDLE_S, "shade_cache": SHADE_CACHE,
        "task_pairs": list(pilot.PILOT_V0_PAIRS), "conditions": list(pilot.PILOT_V0_CONDITIONS),
        "repeats": 3, "order_policy": "matched_condition_abba",
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
        "note": "Non-claim ALIGN pilot 3 archives; no grouped claim blinding or estimator registration."})
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


README = """# ALIGN pilot 3 (non-claim)

Generate with `python3 scripts/align_pilot_kit.py`; verify with `--check`.
Protocol: `docs/align/pilot_protocol_v2.md`. Prepare/desk:
`scripts/align_pilot_session.py` (desk accepts `--compare-session <pilot2>`).

24 members: A thinking-on 12 x 4096, then C template-default 20 x 2048;
2 pairs x 2 conditions x 3 repeats, hint on, cap 40960, episode prefix cache
on throughout. Pair order alternates each repeat; condition order alternates
within each pair. Midpoint after A; idle 300 s. Fresh process per member.

Specs equal pilot2 A/C except prompt_cache; seed remains 1 in every repeat.
Repetition flags observe only. Thermal/contention eligibility is unchanged.
Sizing is a transferred planning bound, not hardware validation. Read its
conditional cache derivation before freezing a span. Rehearse first.

`registration/derive_sizing.py --pilot-session <pilot2 root>` derives receipts
without model work. `derive_identity_pins.py --runtime-python <measurement
python>` hashes local files without loading MLX. Generation preserves verified
Mac identity pins and refuses changed inputs instead of silently replacing them.
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
