"""Conditionless scripted controls, RL-149 §2.5 / RL-151 §3.3 / RL-174 B.4.

The script is kit data. No control outcome, rail value or fitted constant is read here.
Draft kits plan and rehearse but cannot pass the production preflight.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import math

from joulewise.cadence import kit as base, kit_v11

SCHEMA = "joulewise.cadence_campaign_kit.ctl.v1"
RUNNER_KIND = "cadence-ctl-v1"
SPEC_SCHEMA = "joulewise.cadence_leg_spec.ctl.v1"
LAW = "sha256-scripts-v1"
MASTER_SEED = 2026111601
HIDDEN_DOSES = (128, 256, 512)
TURN_CAPS = {"hidden": [1024], "extra-turn": [1024, 1024], "cpu": [512, 512],
             "split": [342, 341, 341], "plain": [1024]}
KINDS = {"hidden", "extra-turn", "cpu", "split", "plain"}
SCRIPT_KEYS = {"kind", "turn_tokens", "hidden_tokens", "cpu_s", "gap_s", "recovery_s"}


def validate_script(script):
    problems = []
    if not base._closed(script, SCRIPT_KEYS, "script", problems):
        raise base.KitError(problems)
    kind = script["kind"]
    turns = script["turn_tokens"]
    if not isinstance(kind, str) or kind not in KINDS:
        problems.append("script.kind: unknown script")
    if not (isinstance(turns, list) and turns and len(turns) <= 3
            and all(base._is_int(n, 1, 4096) for n in turns) and sum(turns) <= 4096):
        problems.append("script.turn_tokens: 1..3 positive caps, total <= 4096")
    for k, maximum in (("hidden_tokens", 4096), ("cpu_s", 600), ("gap_s", 600)):
        if not base._is_int(script[k], 0, maximum):
            problems.append(f"script.{k}: integer 0..{maximum}")
    recovery = script["recovery_s"]
    if type(recovery) not in (int, float) or not 0 <= recovery <= 600:
        problems.append("script.recovery_s: seconds 0..600")
    if problems:
        raise base.KitError(problems)
    expected_turns = {"hidden": 1, "extra-turn": 2, "cpu": 2, "split": 3, "plain": 1}
    if len(turns) != expected_turns[kind]:
        problems.append(f"script.turn_tokens: {kind} needs {expected_turns[kind]} turns")
    if (script["hidden_tokens"] > 0) != (kind == "hidden"):
        problems.append("script.hidden_tokens: positive only for hidden")
    if (script["cpu_s"] > 0) != (kind == "cpu"):
        problems.append("script.cpu_s: positive only for cpu")
    if script["gap_s"] and kind != "split":
        problems.append("script.gap_s: only split has gaps")
    if problems:
        raise base.KitError(problems)
    return script


def generate_legs(campaign_id, law, defaults):
    scripts = law["scripts"]
    # The split/plain pair is one shuffle unit, preserving adjacency and a shared reference.
    singles = [s for s in scripts if s["kind"] not in {"split", "plain", "extra-turn"}]
    singles = kit_v11._permute(singles, campaign_id, law["master_seed"], "singles")
    # RL-186: captures are extra-turn and CPU; the hidden doses and split/plain pair consume.
    first = next(s for s in scripts if s["kind"] == "extra-turn")
    second = next(s for s in singles if s["kind"] == "cpu")
    singles.remove(second)
    pilot = singles[:2]
    units = [[s] for s in singles[2:]]
    pair = [s for s in scripts if s["kind"] in {"split", "plain"}]
    if pair:
        units.append(kit_v11._permute(pair, campaign_id, law["master_seed"], "pair"))
    ordered = [first, *pilot, second,
               *(s for unit in kit_v11._permute(units, campaign_id, law["master_seed"], "scripts") for s in unit)]
    seeds = base.generate_legs(campaign_id, {"method": "sha256-v1", "master_seed": law["master_seed"],
                                          "n_legs": len(ordered), "bands": law["bands"]})
    pair_seed = next(leg["seed"] for leg, script in zip(seeds, ordered) if script["kind"] == "split")
    return [{**leg, "seed": pair_seed if script["kind"] in {"split", "plain"} else leg["seed"],
             "prefill_tokens": defaults["prefill_tokens"], "decode_tokens": sum(script["turn_tokens"]),
             "g0_shape": "span", "script": deepcopy(script)} for leg, script in zip(seeds, ordered)]


def validate_kit(kit, *, batch_window=base.OS_BATCH_WINDOW):
    problems = []
    if not base._closed(kit, base.TOP_KEYS | {"status", "layout"}, "kit", problems):
        raise base.KitError(problems)
    for field in ("runner", "seed_law", "ruling", "frozen", "span_template"):
        if not isinstance(kit[field], dict):
            problems.append(f"{field}: object")
    if not isinstance(kit["status"], str):
        problems.append("status: text")
    if problems:
        raise base.KitError(problems)
    if kit["schema"] != SCHEMA or kit["runner"].get("kind") != RUNNER_KIND:
        problems.append("ctl schema and runner kind must agree")
    if kit["status"] not in {"draft", "issued"}:
        problems.append("status: draft or issued")
    law = kit["seed_law"]
    if base._closed(law, {"method", "master_seed", "n_legs", "bands", "scripts"}, "seed_law", problems):
        if law["method"] != LAW or law["n_legs"] != 12:
            problems.append("seed_law: sha256-scripts-v1, exactly 12 legs")
        if law["master_seed"] != MASTER_SEED or type(law["master_seed"]) is not int or law["bands"] != ["q0"]:
            problems.append("seed_law: RL-186 master_seed 2026111601 and q0 history required")
        scripts = law["scripts"]
        if not isinstance(scripts, list) or len(scripts) != 12:
            problems.append("seed_law.scripts: twelve scripts")
        else:
            for script in scripts:
                try:
                    validate_script(script)
                except base.KitError as error:
                    problems.extend(error.problems)
            if not problems:
                counts = {k: sum(s["kind"] == k for s in scripts) for k in KINDS}
                if counts != {"hidden": 6, "extra-turn": 1, "cpu": 3, "split": 1, "plain": 1}:
                    problems.append("scripts: six hidden, one extra-turn, three cpu, split/plain pair")
                hidden = [s["hidden_tokens"] for s in scripts if s["kind"] == "hidden"]
                if len(set(hidden)) != 3 or any(n < 128 or hidden.count(n) != 2 for n in hidden):
                    problems.append("scripts: three hidden doses at least 128, two legs each")
                if sorted(s["cpu_s"] for s in scripts if s["kind"] == "cpu") != [10, 30, 90]:
                    problems.append("scripts: RL-186 CPU doses 10, 30 and 90 seconds")
                if any(s["turn_tokens"] != TURN_CAPS[s["kind"]] for s in scripts):
                    problems.append("scripts: turn caps must match RL-186")
                if len({s["recovery_s"] for s in scripts}) != 1 or scripts[0]["recovery_s"] < 120:
                    problems.append("scripts: one common recovery from 120 to 600 seconds")
                split = next((s for s in scripts if s["kind"] == "split"), None)
                if split and split["gap_s"] < 10:
                    problems.append("scripts: the split gap is at least 10 seconds")
    if problems:
        raise base.KitError(problems)
    defaults = kit["leg_defaults"]
    if not (isinstance(defaults, dict) and set(defaults) == {"prefill_tokens"}
            and base._is_int(defaults["prefill_tokens"], 256, 32768)):
        raise base.KitError(["leg_defaults: prefill_tokens 256..32768"])
    if kit["legs"] != generate_legs(kit["campaign_id"], law, defaults):
        problems.append("legs: not the script seed law's list")
    expected_layout = [[f"L{i:03d}" for i in range(1,4)], [f"L{i:03d}" for i in range(4,13)]]
    if kit["layout"] != expected_layout:
        problems.append("layout: this seed law defines 3 + 9, fixed before collection")
    if not base._is_int(kit["span_template"].get("legs_per_span"), 1, 9):
        problems.append("span_template.legs_per_span: at most nine (RL-172 b)")
    if kit["ruling"].get("authorizes_spans") is not (kit["status"] == "issued"):
        problems.append("ruling.authorizes_spans: false for draft, true for issued")
    if kit["status"] == "issued" and (kit["frozen"].get("commit") == "0"*40 or
                                        not kit["frozen"].get("paths")):
        problems.append("issued kit needs a real frozen pin")
    # Reuse all v1.1 safety/checklist/stop rules on a neutral view, without changing its validator.
    view = deepcopy(kit)
    view.pop("status")
    view.pop("layout")
    view.update(schema=kit_v11.SCHEMA, ruling={**kit["ruling"], "authorizes_spans": True},
                runner={**kit["runner"], "kind": kit_v11.RUNNER_KIND},
                leg_defaults={"decode_tokens": 4096},
                seed_law={"method": kit_v11.LAW, "master_seed": law["master_seed"], "n_legs": 12,
                          "bands": law["bands"], "prompt_tokens": [defaults["prefill_tokens"]],
                          "g0_shapes": ["own", "span"]})
    view["legs"] = kit_v11.generate_legs(view["campaign_id"], view["seed_law"], view["leg_defaults"])
    try:
        kit_v11.validate_kit(view, batch_window=batch_window)
    except base.KitError as error:
        problems.extend(error.problems)
    if problems:
        raise base.KitError(problems)
    from joulewise.cadence import legs
    try:
        for roster in kit["layout"]:
            legs.leg_specs(kit, roster)
    except legs.PlanError as error:
        raise base.KitError(error.problems) from error
    return kit


def require_issued(kit):
    if kit.get("status") != "issued":
        raise base.KitError(["ctl kit is DRAFT / UNFROZEN: research-lead lm-inst-01 read and lead issue required"])


def apply_instrument_read(kit, *, below_gpu_floor, below_dc_in_floor, return_time_s, decode_end_lag_s,
                          prompt_sizes, raised_doses=None):
    """Apply RL-186 to the lead's scalar inputs, returning a draft for cold review."""
    validate_kit(kit)
    if kit["status"] != "draft":
        raise base.KitError(["RL-186 parameters can only be applied to a draft"])
    if not all(type(flag) is bool for flag in (below_gpu_floor, below_dc_in_floor)):
        raise base.KitError(["RL-186 needs both floor comparisons for the 128 dose"])
    if below_gpu_floor and below_dc_in_floor:
        if (not isinstance(raised_doses, (list, tuple)) or len(raised_doses) != 3
                or any(not base._is_int(n, 129, 4096) for n in raised_doses)
                or len(set(raised_doses)) != 3):
            raise base.KitError(["RL-186 needs three raised doses from the research lead"])
        doses = sorted(raised_doses)
    else:
        if raised_doses is not None:
            raise base.KitError(["RL-186 changes the hidden doses only when both floors exclude 128"])
        doses = HIDDEN_DOSES
    for value in (return_time_s, decode_end_lag_s):
        if type(value) not in (int, float) or not 0 <= value < math.inf:
            raise base.KitError(["RL-186 times must be finite nonnegative seconds"])
    recovery = min(600, max(120, 5 * Decimal(str(return_time_s))))
    recovery_s = int(recovery) if recovery == int(recovery) else float(recovery)
    gap = max(10, math.ceil(5 * Decimal(str(decode_end_lag_s))))
    if (not isinstance(prompt_sizes, (list, tuple)) or not prompt_sizes
            or any(not base._is_int(n, 256, 32768) for n in prompt_sizes)):
        raise base.KitError(["RL-186 needs the prompt sizes represented in lm-inst-01"])
    distance = min(abs(n - 2000) for n in prompt_sizes)
    nearest = {n for n in prompt_sizes if abs(n - 2000) == distance}
    if len(nearest) != 1:
        raise base.KitError(["RL-186: a tie for nearest prompt size needs a research-lead choice"])

    updated = deepcopy(kit)
    law = updated["seed_law"]
    original_doses = sorted({s["hidden_tokens"] for s in law["scripts"] if s["kind"] == "hidden"})
    replacements = dict(zip(original_doses, doses))
    for script in law["scripts"]:
        script["recovery_s"] = recovery_s
        if script["kind"] == "hidden":
            script["hidden_tokens"] = replacements[script["hidden_tokens"]]
        if script["kind"] == "split":
            script["gap_s"] = gap
    updated["leg_defaults"]["prefill_tokens"] = nearest.pop()
    updated["legs"] = generate_legs(updated["campaign_id"], law, updated["leg_defaults"])
    return validate_kit(updated)


def script_seconds(script, model):
    calls = len(script["turn_tokens"]) + bool(script["hidden_tokens"])
    return ((sum(script["turn_tokens"]) + script["hidden_tokens"]) / model["decode_tokens_per_s"]
            + script["cpu_s"] + (len(script["turn_tokens"])-1)*script["gap_s"] + script["recovery_s"], calls)


def post_g0_budget_s(spec, model):
    seconds, calls = script_seconds(spec["script"], model)
    # Existing EpisodeSpec's deadman limit; no change to that shared workload contract.
    return math.ceil(seconds + calls*spec["prefill_tokens"]*model["prefill_s_per_token"] + 60)
