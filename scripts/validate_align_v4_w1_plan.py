#!/usr/bin/env python3
"""Validate the fail-closed ALIGN v4 window-1 plan template (a planning sheet).

This is a desk validator only.  It neither writes custody nor invokes any arm
or installation code.  The template is *not* a ``run_night`` plan: the real
night plan (schema ``joulewise.night_plan.v5``, receipt class HAZARD_PACK) is
written by ``align_v4_session.py prepare`` from the kit and its sizing.  The
template therefore carries its own schema and only names the night-plan family
it targets, so no tool can mistake it for a runnable plan.  Its R0/R1 values
must equal ``registration/inputs.json``, which is what the kit installs.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "configs/campaigns/align_v4/night_plan.template.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.b5 import plan as night_plan  # noqa: E402  (window-maximum constants)

from scripts import align_v4_kit as kit  # noqa: E402  (L1 rule, registered roster)

PLACEHOLDER = "PENDING_R1"
TEMPLATE_SCHEMA = "joulewise.align_v4.w1_plan_template.v1"
INPUTS = ROOT / "configs/campaigns/align_v4/registration/inputs.json"
R1_SLOTS = ROOT / "configs/campaigns/align_v4/registration/r1_slots.json"
COLLECTION_PLAN = ROOT / "configs/campaigns/align_v4/collection_plan.json"
MEMBER_BINDINGS = ("ordinal", "role", "run_id", "config_path", "config_sha256")
SPAN_CAP_S = 26_940
WINDOW_CAP_S = 44_640
T0_STAGE_CAP_S = night_plan.T0_STAGE_CAP_S
PAUSE_LIMIT_S = night_plan.PAUSE_LIMIT_S
SESSION_WAIT_BUDGET_S = night_plan.SESSION_WAIT_BUDGET_S


def _fail(message: str) -> None:
    raise ValueError(message)


def _placeholder_paths(value, path="$"):
    if isinstance(value, str) and PLACEHOLDER in value:
        yield path
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _placeholder_paths(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _placeholder_paths(item, f"{path}[{index}]")


def _finite(value, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        _fail(f"{label} must be a finite number")
    return float(value)


def _read_inputs() -> dict:
    return json.loads(INPUTS.read_text(encoding="utf-8"))


def _read_r1_slots() -> dict:
    return json.loads(R1_SLOTS.read_text(encoding="utf-8"))


def build_template(collection_plan: dict | None = None) -> dict:
    """The committed template, regenerated from the registered kit roster.

    Its member bindings (including config_sha256) come from collection_plan.json,
    so any kit regeneration that changes a config hash shows up as template
    drift. Every R1/R0 value is PENDING_R1; D's gate policy is heavy and
    per-turn by construction, so those two keys are fixed true.
    """
    plan = collection_plan if collection_plan is not None else json.loads(COLLECTION_PLAN.read_text())
    pending = PLACEHOLDER
    return {
        "align_v4": {
            "B_D": pending, "I_D": pending, "T_dead": pending, "max_r1_tail_s": pending,
            "arithmetic": {"align_s": pending, "pause_limit_s": PAUSE_LIMIT_S,
                           "programmed_span_s": pending, "scaffold_s": kit.SCAFFOLD_S,
                           "session_wait_budget_s": SESSION_WAIT_BUDGET_S, "span_cap_s": SPAN_CAP_S,
                           "t0_stage_cap_s": T0_STAGE_CAP_S, "window_cap_s": WINDOW_CAP_S},
            "config_root": "configs/campaigns/align_v4", "effort": pending,
            "members": [{**{key: member[key] for key in MEMBER_BINDINGS}, "member_s": pending}
                        for member in plan["members"]],
            "status": pending,
            "thermal_policy": {"classification_sha256": pending,
                               "chunk_tokens": pending, "delta_fast_c": pending, "delta_slow_c": pending,
                               "g0_cap_s": pending, "heavy": True, "per_turn": True,
                               "sensors": {"fan_keys": pending, "r0_sha256": pending,
                                           "s_fast": pending, "s_slow": pending},
                               "turn_cap_s": pending},
            "window": 1,
        },
        "night_plan_schema": "joulewise.night_plan.v5",
        "night_plan_schema_version": 5,
        "plan_id": "align-v4-w1-" + pending,
        "receipt_class": "HAZARD_PACK",
        "schema": TEMPLATE_SCHEMA,
        "window_max_s": pending,
    }


def template_bytes(collection_plan: dict | None = None) -> bytes:
    return (json.dumps(build_template(collection_plan), indent=2, sort_keys=True) + "\n").encode()


def validate(value: dict, inputs: dict | None = None, r1_slots: dict | None = None, *,
             collection_plan: dict | None = None) -> dict:
    pending = list(_placeholder_paths(value))
    if pending:
        _fail("refused PENDING_R1 placeholder(s): " + ", ".join(pending))
    if value.get("schema") != TEMPLATE_SCHEMA:
        _fail(f"template schema must be {TEMPLATE_SCHEMA}; it is not a run_night plan")
    if value.get("night_plan_schema") != "joulewise.night_plan.v5" or value.get("night_plan_schema_version") != 5:
        _fail("window 1 targets the pilot night-plan v5 family")
    if value.get("receipt_class") != "HAZARD_PACK":
        _fail("window 1 receipt_class must be HAZARD_PACK")

    align = value.get("align_v4")
    if not isinstance(align, dict) or align.get("window") != 1:
        _fail("align_v4 window-1 planning block is missing")
    if align.get("config_root") != "configs/campaigns/align_v4":
        _fail("config_root must bind configs/campaigns/align_v4")
    if align.get("effort") not in {"low", "medium", "xhigh"}:
        _fail("effort must be a selected R1-qualified rung")
    budget = align.get("B_D")
    if type(budget) is not int or not 6144 <= budget <= 40960 or budget % 1024:
        _fail("B_D must be a multiple of 1024 in [6144, 40960]")
    idle = _finite(align.get("I_D"), "I_D")
    dead = _finite(align.get("T_dead"), "T_dead")
    tail = _finite(align.get("max_r1_tail_s"), "max_r1_tail_s")
    if not 0 <= idle < 1750 or tail < 0 or not math.isclose(
            dead, kit.l1_t_dead(idle, tail), rel_tol=1e-9, abs_tol=1e-9):
        _fail("T_dead must equal min((1750 - I_D), (1800 - I_D - max_r1_tail_s - 10)) / 1.13544 "
              "(lead ruling L1)")
    kit.check_l1_member_fit(idle, dead, tail)

    policy = align.get("thermal_policy")
    sensor_keys = {"s_fast", "s_slow", "fan_keys", "r0_sha256"}
    if not isinstance(policy, dict) or not isinstance(policy.get("sensors"), dict):
        _fail("thermal_policy and thermal_policy.sensors must be objects")
    if set(policy["sensors"]) != sensor_keys:
        _fail("thermal_policy.sensors must explicitly contain " + ", ".join(sorted(sensor_keys)))
    # The same canonical gate-policy validation the kit applies to D members:
    # the template's own heavy/per_turn keys are validated, never supplied here.
    if "window_reference" in policy:
        _fail("thermal_policy.window_reference is installed per member by the kit, not templated")
    from joulewise.align.apple.thermal_gates import validate_gate_policy
    checked = validate_gate_policy({**kit.gate_policy_fields(policy), "window_reference": {"role": "capture"}})
    if checked["heavy"] is not True or checked["per_turn"] is not True:
        _fail("D thermal_policy must be heavy with per-turn gates and holds")

    # The template is a second copy of values the kit installs from
    # registration/inputs.json; refuse any disagreement.
    inputs = _read_inputs() if inputs is None else inputs
    r1_slots = _read_r1_slots() if r1_slots is None else r1_slots
    r1 = (inputs or {}).get("R1") or {}
    bound = {"B_D": r1.get("B_D"), "I_D": r1.get("I_D"), "T_dead": r1.get("T_dead"),
             "thermal_policy": r1.get("thermal_policy"),
             "effort": ((inputs or {}).get("R0") or {}).get("reasoning_effort")}
    unfilled = sorted(k for k, v in bound.items() if v is None)
    if unfilled:
        _fail("registration/inputs.json is still pending for: " + ", ".join(unfilled))
    mismatched = sorted(k for k, v in bound.items() if align.get(k) != v)
    if mismatched:
        _fail("template disagrees with registration/inputs.json on: " + ", ".join(mismatched))
    if (r1_slots or {}).get("max_r1_tail_s") is None:
        _fail("registration/r1_slots.json is still pending for: max_r1_tail_s")
    if align.get("max_r1_tail_s") != r1_slots["max_r1_tail_s"]:
        _fail("template disagrees with registration/r1_slots.json on: max_r1_tail_s")

    members = align.get("members")
    if not isinstance(members, list) or len(members) != 18:
        _fail("window 1 must contain exactly 18 members")
    ordinals = [row.get("ordinal") for row in members if isinstance(row, dict)]
    if ordinals != list(range(1, 19)):
        _fail("member ordinals must be exactly 1..18")
    roles = [row.get("role") for row in members]
    expected = {"anchor": 4, "X-S": 2, "X-G": 2, "Y-S": 2, "Y-G": 2, "D": 6}
    if {role: roles.count(role) for role in expected} != expected or set(roles) != set(expected):
        _fail("member roles do not match the Amendment-1 window-1 roster")
    registered = (collection_plan if collection_plan is not None
                  else json.loads(COLLECTION_PLAN.read_text()))
    bindings = MEMBER_BINDINGS
    if [[row.get(key) for key in bindings] for row in members] != [
            [row.get(key) for key in bindings] for row in registered["members"]]:
        _fail("members must be the registered configs/campaigns/align_v4 roster")
    seconds = [_finite(row.get("member_s"), f"members[{i}].member_s")
               for i, row in enumerate(members)]
    if any(item <= 0 or item > 1800 for item in seconds):
        _fail("every member_s must be positive and at most the 1,800 s spent cap")

    arithmetic = align.get("arithmetic")
    if not isinstance(arithmetic, dict):
        _fail("arithmetic block is missing")
    scaffold = _finite(arithmetic.get("scaffold_s"), "scaffold_s")
    fixed = {"span_cap_s": SPAN_CAP_S, "t0_stage_cap_s": T0_STAGE_CAP_S,
             "pause_limit_s": PAUSE_LIMIT_S,
             "session_wait_budget_s": SESSION_WAIT_BUDGET_S,
             "window_cap_s": WINDOW_CAP_S}
    if any(arithmetic.get(key) != expected_value for key, expected_value in fixed.items()):
        _fail("night-plan arithmetic constants do not match the pilot schema/amendment table")
    align_s = math.fsum(seconds)
    span_s = math.ceil(scaffold + align_s)
    window_s = 60 * math.ceil((span_s + T0_STAGE_CAP_S + PAUSE_LIMIT_S
                               + SESSION_WAIT_BUDGET_S) / 60)
    if not math.isclose(_finite(arithmetic.get("align_s"), "align_s"), align_s,
                        rel_tol=0, abs_tol=1e-9):
        _fail("align_s does not equal the sum of all member_s values")
    if arithmetic.get("programmed_span_s") != span_s:
        _fail("programmed_span_s must be ceil(scaffold_s + align_s)")
    if value.get("window_max_s") != window_s:
        _fail("window_max_s does not match the pilot window-maximum formula")
    if span_s > SPAN_CAP_S or window_s > WINDOW_CAP_S:
        _fail(f"window exceeds cap: span={span_s}/{SPAN_CAP_S}, window={window_s}/{WINDOW_CAP_S}")
    return {"members": 18, "align_s": align_s, "programmed_span_s": span_s,
            "window_max_s": window_s}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plan", nargs="?", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--inputs", type=Path, default=INPUTS,
                        help="registration/inputs.json the kit installs (default: this checkout's)")
    parser.add_argument("--r1-slots", type=Path, default=R1_SLOTS,
                        help="registration/r1_slots.json (default: this checkout's)")
    parser.add_argument("--regenerate-template", action="store_true",
                        help="rewrite the committed template from collection_plan.json and exit")
    args = parser.parse_args(argv)
    if args.regenerate_template:
        DEFAULT_PLAN.write_bytes(template_bytes())
        print(f"regenerated {DEFAULT_PLAN.relative_to(ROOT)}")
        return 0
    try:
        inputs = json.loads(args.inputs.read_text(encoding="utf-8"))
        r1_slots = json.loads(args.r1_slots.read_text(encoding="utf-8"))
        result = validate(json.loads(args.plan.read_text(encoding="utf-8")), inputs, r1_slots)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "VALID", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
