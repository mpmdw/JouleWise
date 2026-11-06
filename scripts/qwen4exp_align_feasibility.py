#!/usr/bin/env python3
"""Planning-only worst-case wall clock for Flash-Next as the ALIGN v4 D model.

Every budget comes from the ALIGN v4 kit, never from this module or a new
file format.  The kit lives on ``lane/2026-11-05-align-v4-assembled``
(``scripts/align_v4_kit.py`` at fc83cfe1d) and this reader consumes only the
JSON that kit already writes under ``configs/campaigns/align_v4``:

- ``registration/inputs.json`` (``joulewise.align_v4_inputs.v1``):
  ``R0.reasoning_effort``, ``R1.B_D``, ``R1.I_D``, ``R1.T_dead``;
- ``collection_plan.json`` (``joulewise.align_v4.v1``): the D member specs'
  per-turn cap ``max_tokens`` (4096), ``max_context_tokens`` (40960) and
  ``max_turns``, plus the roster roles;
- ``registration/sizing_preview.json``: scaffold, span limit, the planning
  window maximum and A1's planning member seconds for the non-D roles;
- ``registration/r1_slots.json`` (optional): ``max_r1_tail_s`` for lead
  ruling L1 (docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-1.md).

The kit's numeric rules are vendored below with their source.  The plan
tree's recorded generator digest is compared with the kit digest they were
vendored from; a mismatch prints RULES_UNVERIFIED.

Worst case per D episode (docs/align/token_admission_budget.md): a turn is
admitted while cumulative decode < B_D and keeps its full per-turn cap, so
decode reaches B_D - 1 + max_tokens (bounded by max_turns x max_tokens and
the context cap).  The context guard keeps every rendered prompt within
max_context_tokens - max_tokens.  Prefill is reported two ways: with the
episode-prefix cache holding (each context position prefilled once) and with
no reuse (every turn re-prefills a full prompt; D runs with
hybrid_checkpoint_limit 0).  Each token is charged at the slowest measured
median across the context rungs up to the cap.  Tool time is not modelled.

Usage (the kit is read from Git objects, like the kit's own ``frozen()``):

    python -B scripts/qwen4exp_align_feasibility.py \\
      --align-ref origin/lane/2026-11-05-align-v4-assembled \\
      --performance "$RUN/performance-512.json" "$RUN/performance-2048.json"

``--align-kit DIR`` reads a checked-out ``configs/campaigns/align_v4``.
Synthetic-artifact performance reports are refused: they are not D evidence.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
KIT_PATH = "configs/campaigns/align_v4"
CONTEXT_RUNGS = (4096, 16384, 40960)  # qwen4exp_mbp_live measurement geometry

# Vendored from scripts/align_v4_kit.py at fc83cfe1d (sha256 KIT_SHA256).
KIT_SHA256 = "73d1b1f558e24015538b766ca1c4da5dd00e8657fdf1777d9457b08611722dda"
INPUTS_SCHEMA = "joulewise.align_v4_inputs.v1"
PLAN_SCHEMA = "joulewise.align_v4.v1"
R1_SLOTS_SCHEMA = "joulewise.align.r1_slots.v1"
BUDGET_FLOOR = 6144          # validate_budget: multiple of 1024 in [6144, 40960]
BUDGET_CEILING = 40960
BUDGET_STEP = 1024
MEMBER_CAP_S = 1800          # fit_roster: "R1 member exceeds spent 1800 s cap"
DEADMAN_NUMERATOR_S = 1750   # require_ready: T_dead == (1750 - I_D) / 1.13544
MEMBER_SLOPE = 1.13544
L1_MARGIN_S = 10             # LEAD-RULINGS-1 L1: I_D + 1.13544 T_dead + tail + 10 <= 1800
EFFORTS = ("xhigh", "medium", "low")  # require_ready: R0 ladder rungs
ROLE_COST_KEY = {"anchor": "anchor", "D": "D", "X-G": "G", "Y-G": "G", "X-S": "S", "Y-S": "S"}
KIT_FILES = ("registration/inputs.json", "collection_plan.json", "registration/sizing_preview.json",
             "plan_tree.json", "registration/r1_slots.json")


# --------------------------------------------------------------------------- kit reader

def _json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}: top level must be an object")
    return value


def kit_reader(*, kit_dir: Path | None = None, ref: str | None = None,
               repo: Path = ROOT) -> tuple[Callable[[str], bytes | None], str]:
    """Return (read(relative) -> bytes or None, identity) for one kit source."""
    if (kit_dir is None) == (ref is None):
        raise ValueError("give exactly one of --align-kit or --align-ref")
    if kit_dir is not None:
        def read(rel):
            path = Path(kit_dir) / rel
            return path.read_bytes() if path.is_file() else None
        return read, str(kit_dir)

    def read(rel):
        proc = subprocess.run(["git", "show", f"{ref}:{KIT_PATH}/{rel}"], cwd=repo, capture_output=True)
        return proc.stdout if proc.returncode == 0 else None
    return read, f"{ref}:{KIT_PATH}"


def _pending(value) -> bool:
    # align_v4_kit.pending_inputs: null/empty/"PENDING_*" leaves are pending.
    return (value is None or value in ("", {}, [])
            or (isinstance(value, str) and value.startswith("PENDING_")))


def _finite(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def validate_budget(budget) -> None:
    if (type(budget) is not int or not BUDGET_FLOOR <= budget <= BUDGET_CEILING
            or budget % BUDGET_STEP):
        raise ValueError("B_D must be a multiple of 1024 in [6144, 40960]")


def t_dead_rule(i_d: float, tail: float | None) -> float:
    """Ruling 1(f) as restated by lead ruling L1; the kit's rule when the tail is unknown."""
    first = (DEADMAN_NUMERATOR_S - i_d) / MEMBER_SLOPE
    if tail is None:
        return first
    return min(first, (MEMBER_CAP_S - i_d - tail - L1_MARGIN_S) / MEMBER_SLOPE)


def load_kit(read: Callable[[str], bytes | None], identity: str) -> dict[str, Any]:
    raw = {name: read(name) for name in KIT_FILES}
    for name in KIT_FILES[:3]:
        if raw[name] is None:
            raise ValueError(f"{identity}: missing {name}; is this the ALIGN v4 kit?")
    inputs = _json(raw["registration/inputs.json"], "inputs.json")
    plan = _json(raw["collection_plan.json"], "collection_plan.json")
    sizing = _json(raw["registration/sizing_preview.json"], "sizing_preview.json")
    if inputs.get("schema_version") != INPUTS_SCHEMA:
        raise ValueError(f"inputs.json: expected {INPUTS_SCHEMA}")
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise ValueError(f"collection_plan.json: expected {PLAN_SCHEMA}")
    generator = None
    if raw["plan_tree.json"] is not None:
        generator = (_json(raw["plan_tree.json"], "plan_tree.json").get("generator") or {}).get("sha256")

    members = plan.get("members")
    if not isinstance(members, list) or not members or not all(isinstance(m, dict) for m in members):
        raise ValueError("collection_plan.json: no members")
    d_specs = [m.get("spec") for m in members if m.get("role") == "D"]
    if not d_specs or not all(isinstance(s, dict) for s in d_specs):
        raise ValueError("collection_plan.json: no D member specs")
    caps = {(s.get("max_tokens"), s.get("max_context_tokens"), s.get("max_turns")) for s in d_specs}
    if len(caps) != 1:
        raise ValueError("collection_plan.json: D members disagree on max_tokens/max_context_tokens/max_turns")
    turn_cap, context_cap, max_turns = caps.pop()
    for value, label in ((turn_cap, "max_tokens"), (context_cap, "max_context_tokens"), (max_turns, "max_turns")):
        if type(value) is not int or value <= 0:
            raise ValueError(f"collection_plan.json: D {label} must be a positive integer")
    if not turn_cap < context_cap <= BUDGET_CEILING:
        raise ValueError("collection_plan.json: D caps must satisfy max_tokens < max_context_tokens <= 40960")
    roles = []
    for m in members:
        if m.get("role") not in ROLE_COST_KEY or type(m.get("ordinal")) is not int:
            raise ValueError(f"collection_plan.json: unknown member role/ordinal {m.get('role')!r}")
        roles.append((m["ordinal"], m["role"]))

    member_seconds = sizing.get("member_seconds")
    window = {k: sizing.get(k) for k in ("scaffold_s", "span_limit_s", "planning_window_max_s")}
    if (not isinstance(member_seconds, dict)
            or not all(_finite(member_seconds.get(k)) and member_seconds[k] > 0 for k in ("anchor", "G", "S"))
            or not all(_finite(v) and v > 0 for v in window.values())):
        raise ValueError("sizing_preview.json: missing scaffold/span/window limits or member seconds")

    r0 = (inputs.get("R0") or {}).get("reasoning_effort")
    if not _pending(r0) and r0 not in EFFORTS:
        raise ValueError("R0 reasoning effort must be a selected ladder rung")
    tail = None
    if raw["registration/r1_slots.json"] is not None:
        slots = _json(raw["registration/r1_slots.json"], "r1_slots.json")
        if slots.get("schema") != R1_SLOTS_SCHEMA:
            raise ValueError(f"r1_slots.json: expected {R1_SLOTS_SCHEMA}")
        if not _pending(slots.get("max_r1_tail_s")):
            tail = slots["max_r1_tail_s"]
            if not _finite(tail) or tail < 0:
                raise ValueError("r1_slots.max_r1_tail_s must be finite and >= 0")

    r1 = inputs.get("R1") or {}
    pending_r1 = [k for k in ("B_D", "I_D", "T_dead") if _pending(r1.get(k))]
    if pending_r1 and len(pending_r1) != 3:
        raise ValueError("R1 B_D/I_D/T_dead must be filled together; pending: " + ", ".join(pending_r1))
    budget = None
    if not pending_r1:
        validate_budget(r1["B_D"])
        if not _finite(r1["I_D"]) or not 0 <= r1["I_D"] < DEADMAN_NUMERATOR_S:
            raise ValueError("R1.I_D must be finite and in [0, 1750)")
        expected = t_dead_rule(r1["I_D"], tail)
        if not _finite(r1["T_dead"]) or not math.isclose(r1["T_dead"], expected, rel_tol=1e-9):
            raise ValueError(f"R1.T_dead must equal {expected!r} (kit rule, lead ruling L1)")
        if tail is not None and r1["I_D"] + MEMBER_SLOPE * r1["T_dead"] + tail + L1_MARGIN_S > MEMBER_CAP_S + 1e-9:
            raise ValueError("L1: I_D + 1.13544 T_dead + max_R1_tail + 10 exceeds the 1800 s member cap")
        budget = {"B_D": r1["B_D"], "I_D": r1["I_D"], "T_dead": r1["T_dead"]}

    return {"identity": identity, "generator_sha256": generator, "rules_verified": generator == KIT_SHA256,
            "turn_cap": turn_cap, "context_cap": context_cap, "max_turns": max_turns,
            "roles": sorted(roles), "member_seconds": member_seconds, "window": window,
            "reasoning_effort": None if _pending(r0) else r0, "r1": budget, "max_r1_tail_s": tail}


# --------------------------------------------------------------------------- performance

def load_performance(paths: list[Path]) -> dict[tuple[str, int], dict[str, float]]:
    """Medians from supervisor reports; the worker's rows live under ``results``."""
    cells: dict[tuple[str, int], dict[str, float]] = {}
    profiles = set()
    for path in paths:
        try:
            report = _json(path.read_bytes(), str(path))
        except OSError as exc:
            raise ValueError(f"cannot read {path}: {exc}") from exc
        if report.get("schema") != "qwen4exp-mbp-live/v1" or report.get("command") != "performance":
            raise ValueError(f"{path}: not a qwen4exp performance report")
        results = report.get("results")
        if report.get("synthetic", False) is not False or (
                isinstance(results, dict) and results.get("synthetic", False) is not False):
            raise ValueError(f"{path}: synthetic-artifact performance report is not D evidence")
        if (report.get("verdict") != "completed" or not isinstance(results, dict)
                or results.get("verdict") != "completed"):
            raise ValueError(f"{path}: performance report is not completed")
        medians = results.get("medians")
        if not isinstance(medians, list) or not medians:
            raise ValueError(f"{path}: performance report has no median rows")
        profiles.add(report.get("profile"))
        if len(profiles) > 1:
            raise ValueError(f"{path}: performance reports mix artifact profiles {sorted(map(str, profiles))}")
        for row in medians:
            try:
                key = (str(row["reasoning_effort"]), int(row["context"]))
                value = {"prefill_tps": float(row["prefill_tps"]), "decode_tps": float(row["decode_tps"])}
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"{path}: malformed median row") from exc
            if min(value.values()) <= 0 or not all(math.isfinite(v) for v in value.values()):
                raise ValueError(f"{path}: median rates must be finite and positive")
            # Two chunk-size reports are alternatives, not samples to pool:
            # the later CLI argument (normally 2048) wins.
            cells[key] = value
    return cells


# --------------------------------------------------------------------------- calculation

def slowest(rates, effort: str, context_cap: int) -> dict[str, float]:
    rungs = [r for r in CONTEXT_RUNGS if r < context_cap] + [context_cap]
    missing = [r for r in rungs if (effort, r) not in rates]
    if missing:
        raise ValueError(f"missing measured median for {effort} at context {missing}")
    return {k: min(rates[(effort, r)][k] for r in rungs) for k in ("prefill_tps", "decode_tps")}


def episode_seconds(kit, rate, budget: int) -> dict[str, float]:
    turn, context, turns = kit["turn_cap"], kit["context_cap"], kit["max_turns"]
    decode = min(budget - 1 + turn, turns * turn, context)
    decode_s = decode / rate["decode_tps"]
    return {"decode_tokens": decode, "decode_s": decode_s,
            "cached_s": decode_s + max(context - decode, 0) / rate["prefill_tps"],
            "uncached_s": decode_s + turns * (context - turn) / rate["prefill_tps"]}


def _verdict(cost, deadline) -> str:
    if cost["uncached_s"] <= deadline:
        return "FITS"
    if cost["cached_s"] <= deadline:
        return "FITS_ONLY_IF_PREFIX_CACHE_HOLDS"
    return "DEADMAN_RISK"


def fit_roster(kit, d_member_seconds: Callable[[int], float], budget: int) -> dict[str, Any]:
    """align_v4_kit.fit_roster, with sizing_preview planning seconds for non-D roles."""
    window, role = kit["window"], dict(kit["roles"])
    ordinals, actions = [o for o, _ in kit["roles"]], []
    while True:
        costs = [d_member_seconds(budget) if role[o] == "D"
                 else kit["member_seconds"][ROLE_COST_KEY[role[o]]] for o in ordinals]
        span = math.ceil(window["scaffold_s"] + math.fsum(costs))
        fits = span <= window["span_limit_s"]
        if fits or (17 not in ordinals and budget <= BUDGET_FLOOR):
            return {"ordinals": ordinals, "B_D": budget, "programmed_span_s": span,
                    "span_limit_s": window["span_limit_s"],
                    "planning_window_max_s": window["planning_window_max_s"],
                    "actions": actions, "fits": fits and max(costs) <= MEMBER_CAP_S}
        if 17 in ordinals:
            ordinals.remove(17)
            actions.append({"drop_ordinal": 17})
        else:
            budget -= BUDGET_STEP
            actions.append({"B_D": budget})


def calculate(kit: dict[str, Any], rates: dict[tuple[str, int], dict[str, float]]) -> dict[str, Any]:
    efforts = [kit["reasoning_effort"]] if kit["reasoning_effort"] else [
        e for e in EFFORTS if any(k[0] == e for k in rates)]
    if not efforts:
        raise ValueError("performance reports measure none of the ALIGN effort rungs")
    rows = []
    for effort in efforts:
        rate = slowest(rates, effort, kit["context_cap"])
        if kit["r1"]:
            r1 = kit["r1"]
            cost = episode_seconds(kit, rate, r1["B_D"])

            def member(b, rate=rate, r1=r1):
                worst = episode_seconds(kit, rate, b)["uncached_s"]
                return r1["I_D"] + MEMBER_SLOPE * min(worst, r1["T_dead"])
            rows.append({"effort": effort, "mode": "R1", **r1, **cost, "rate": rate,
                         "verdict": _verdict(cost, r1["T_dead"]), "member_s_worst": member(r1["B_D"]),
                         "window": fit_roster(kit, member, r1["B_D"])})
            continue
        # R1 pending: I_D = 0 gives the most permissive deadman the kit allows.
        # Report the largest kit-legal B_D for each prefill assumption and the
        # I_D ceiling R1 must then measure for that B_D's worst case to fit.
        limit = DEADMAN_NUMERATOR_S / MEMBER_SLOPE
        best = {}
        for mode in ("uncached_s", "cached_s"):
            best[mode] = None
            for b in range(BUDGET_CEILING, BUDGET_FLOOR - 1, -BUDGET_STEP):
                cost = episode_seconds(kit, rate, b)
                if cost[mode] <= limit:
                    best[mode] = {"B_D": b, "episode_s": cost[mode],
                                  "I_D_max": DEADMAN_NUMERATOR_S - MEMBER_SLOPE * cost[mode]}
                    break
        rows.append({"effort": effort, "mode": "R1_PENDING", "rate": rate, "best": best,
                     "verdict": _verdict(episode_seconds(kit, rate, BUDGET_FLOOR), limit) + "_AT_B_D_FLOOR",
                     "window": fit_roster(kit, lambda b: MEMBER_CAP_S, BUDGET_CEILING)})
    return {"label": "PLANNING ESTIMATE — NOT ENERGY EVIDENCE", "rows": rows, "kit": kit}


def render(result: dict[str, Any]) -> str:
    kit = result["kit"]
    lines = [result["label"], f"ALIGN kit: {kit['identity']}"]
    if not kit["rules_verified"]:
        lines.append(f"RULES_UNVERIFIED: kit generator {kit['generator_sha256']} != vendored {KIT_SHA256}; "
                     "re-check the vendored rules before relying on this estimate")
    lines.append(f"D caps from the kit: {kit['turn_cap']} tokens/turn, {kit['max_turns']} turns, "
                 f"context {kit['context_cap']}; member cap {MEMBER_CAP_S} s; span limit "
                 f"{kit['window']['span_limit_s']} s; planning window max {kit['window']['planning_window_max_s']} s")
    for row in result["rows"]:
        rate, window = row["rate"], row["window"]
        lines.append(f"{row['effort']:<6} slowest medians: prefill {rate['prefill_tps']:.1f} tok/s, "
                     f"decode {rate['decode_tps']:.1f} tok/s"
                     + ("" if row["mode"] == "R1" else "  (R1 pending: deadman at I_D = 0)"))
        if row["mode"] == "R1":
            lines += [f"  R1 B_D={row['B_D']} I_D={row['I_D']} T_dead={row['T_dead']:.1f} s: worst decode "
                      f"{row['decode_tokens']} tokens; episode {row['cached_s']:.1f} s (prefix cache) / "
                      f"{row['uncached_s']:.1f} s (no reuse); member <= {row['member_s_worst']:.1f} s; "
                      f"{row['verdict']}",
                      f"  window: span {window['programmed_span_s']} s of {window['span_limit_s']} s after "
                      f"{window['actions'] or 'no actions'}; "
                      + ("fits" if window["fits"] else "DOES NOT FIT: return to lead")]
            continue
        for mode, label in (("uncached_s", "no reuse"), ("cached_s", "prefix cache")):
            best = row["best"][mode]
            lines.append(f"  {label:<12}: " + ("no kit-legal B_D fits" if best is None else
                         f"largest B_D {best['B_D']} (episode {best['episode_s']:.1f} s) if R1 measures "
                         f"I_D <= {best['I_D_max']:.1f} s"))
        lines.append(f"  verdict {row['verdict']}; window with D at the {MEMBER_CAP_S} s cap: span "
                     f"{window['programmed_span_s']} s of {window['span_limit_s']} s")
    lines.append("Non-D member seconds are sizing_preview planning guesses; tool time is not modelled.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--performance", nargs="+", required=True, type=Path, metavar="JSON")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--align-kit", type=Path, metavar="DIR", help="checked-out configs/campaigns/align_v4")
    source.add_argument("--align-ref", metavar="REF", help="Git ref holding the ALIGN v4 kit (read with git show)")
    parser.add_argument("--repo", type=Path, default=ROOT, help="repository for --align-ref")
    args = parser.parse_args(argv)
    try:
        read, identity = kit_reader(kit_dir=args.align_kit, ref=args.align_ref, repo=args.repo)
        print(render(calculate(load_kit(read, identity), load_performance(args.performance))))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
