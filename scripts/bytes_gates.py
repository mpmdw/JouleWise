#!/usr/bin/env python3
"""C5 desk arithmetic on the R8.6 NON-CLAIM harvest and measured receipts.

Inputs are a native *.runs.csv with its *.session.json sidecar, the generated
kit collection plan, and a measured-receipts JSON (see the generated README).
No archive/key discovery, measurement, registration or roster change occurs.
Outputs are candidates for registration; absent T10/T_phase stays flag only.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.b5.chain import SETTLE_S

KIT = ROOT / "configs/campaigns/bytes_mac_check/collection_plan.json"
# Operational reserve from block-6 design §15 / BYTES R6, not a physics bound.
RESERVE_BYTES = 150 * 1024**3
# Registration §8.6 / D8: the 5 ms per-run clock budget is retained;
# h=0 for the pre-arm HOLD and the registered frequency margin is 0.25 ppm.
CLOCK_LIMIT_MS = Decimal("5")
FREQUENCY_MARGIN_PPM = Decimal("0.25")
# The per-run receipts MEASUREMENTS.json leaves null for a member that never ran.
TIMING_FIELDS = ("request_s", "member_wall_s", "stream_s", "thermal_level", "outside_cpu_s", "census_quanta")


def read(path):
    return json.loads(Path(path).read_text(), parse_float=Decimal)


def number(value, name, *, positive=False):
    if isinstance(value, bool):
        raise ValueError(name + " must be a finite measured number")
    result = Decimal(str(value))
    if not result.is_finite() or result < 0 or (positive and result == 0):
        raise ValueError(name + " must be finite and " + ("positive" if positive else "nonnegative"))
    return result


def optional(value, name, *, positive=False):
    """An optional desk receipt: null (not derived) stays None; anything else must be a valid number."""
    return None if value is None else number(value, name, positive=positive)


def integer(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(name + " must be a nonnegative integer byte/count value")
    return value


def average(values):
    return sum(values) / len(values)


def line(gate, status, **detail):
    return {"gate": gate, "status": status, **detail}


def clock_line(name, stream_s, clock):
    # Units: 5 ms * 1000 / seconds = ppm. Equality clears the registered
    # > hold; Decimal preserves the JSON decimal at the decision boundary.
    limit = CLOCK_LIMIT_MS * 1000 / stream_s - FREQUENCY_MARGIN_PPM
    rate = Decimal(str(clock["rate_ppm"]))
    word = Decimal(str(clock["frequency_word_ppm"]))
    if not rate.is_finite() or not word.is_finite():
        raise ValueError("clock rate and frequency word must be finite")
    return line("clock:" + name, "pass" if abs(rate) <= limit else "fail",
                T_stream_max_s=stream_s, hold_above_abs_ppm=limit,
                measured_rate_ppm=rate, frequency_word_ppm=word,
                frequency_word_clears_gate=abs(word) <= limit,
                frequency_word_status="diagnostic",
                formula="abs(measured rate) <= 5000/T_stream_max_s - 0.25 ppm")


def calculate(rows, sidecar, measured, plan, *, repo_root=ROOT):
    if (measured.get("schema_version") != "joulewise.bytes_mac_measurements.v1"
            or measured.get("non_claim") is not True or sidecar.get("non_claim") is not True
            or sidecar.get("pack_id") != "bytes-mac-check" or plan.get("non_claim") is not True):
        raise ValueError("C5 accepts only the non-claim bytes-mac-check session")
    session = measured["session_id"]
    if sidecar["session_id"] != session or not rows:
        raise ValueError("harvest session identity is absent or mismatched")
    exported = {}
    for row in rows:
        if (row["non_claim"] != "True" or row["pack_id"] != "bytes-mac-check" or row["session_id"] != session
                or row["run_id"] in exported):
            raise ValueError("harvest contains claim, foreign or duplicate rows")
        exported[row["run_id"]] = row
    receipts = measured["runs"]
    if set(receipts) != set(exported):
        raise ValueError("measurement receipt membership differs from harvest")
    planned = {m["run_id"]: m for m in plan["members"]}
    if not set(planned).issubset(exported):
        raise ValueError("harvest is missing planned kit members")
    # A planned member that never ran (session stopped early) is exported
    # with a non-succeeded status and every timing receipt null. It enters no
    # arithmetic: completeness lines report it, and spreads/means use the
    # members that ran. A succeeded member with null timing is still malformed.
    unmeasured = sorted(r for r, receipt in receipts.items()
                        if exported[r]["status"] != "succeeded" and all(receipt.get(f) is None for f in TIMING_FIELDS))
    measured_ids = set(receipts) - set(unmeasured)
    # Read all scaffold members too: their streams and bytes contribute to
    # the session clock and disk even though they are not roster checks.
    for run_id, receipt in receipts.items():
        integer(receipt["retained_bytes"], "retained_bytes")
        if run_id not in measured_ids:
            continue
        for field in ("request_s", "member_wall_s", "stream_s"):
            receipt[field] = number(receipt[field], run_id + "." + field, positive=True)
        if receipt["member_wall_s"] < receipt["request_s"] or receipt["stream_s"] < receipt["request_s"]:
            raise ValueError("member/stream duration is shorter than its request")
        integer(receipt["thermal_level"], "thermal_level")
    cpu = measured["cpu_contention"]
    # Optional desk receipts: null means not derived; dependent lines are
    # printed "unavailable" instead of withholding every other line.
    w = optional(cpu["w_j_per_cpu_s"], "CPU contention w", positive=True)
    cq = optional(cpu["c_q_cpu_s"], "quiet CPU seconds per quantum")
    groups, checks, spread_groups = {}, {}, []
    for run_id, member in planned.items():
        if member["model_id"] == "reference":
            continue
        if member["purpose"] in ("check", "soak"):
            groups.setdefault(member["model_id"], []).append(run_id)
            if member["purpose"] == "check":
                checks.setdefault(member["model_id"], []).append(run_id)
    gates = []
    for model, run_ids in groups.items():
        for purpose, expected in (("check", plan["check_runs_per_model"]),
                                  ("soak", plan["soak_runs_per_model"])):
            selected = [r for r in run_ids if planned[r]["purpose"] == purpose]
            if purpose == "soak" and model not in plan["long_regimes"][:2]:
                continue
            succeeded = sum(exported[r]["status"] == "succeeded" for r in selected)
            gates.append(line("completeness:" + model + ":" + purpose,
                              "pass" if len(selected) == expected == succeeded else "fail",
                              planned=len(selected), succeeded=succeeded, required=expected))
            times = [receipts[r]["request_s"] for r in selected
                     if exported[r]["status"] == "succeeded" and r in measured_ids]
            # Brief §5 P6: largest measured max/min - 1 over the five
            # check runs or twelve soak runs. No fixed percentage margin.
            # An incomplete group keeps its failing completeness line and its
            # spread over the runs it has (none below two runs), labelled.
            spread_groups.append({"model_id": model, "purpose": purpose, "runs": len(times),
                                  "complete": len(times) == expected,
                                  "spread": max(times) / min(times) - 1 if len(times) >= 2 else None})
    margin = max(g["spread"] for g in spread_groups if g["spread"] is not None)
    margin_complete = all(g["complete"] for g in spread_groups)
    models, cpu_alternative = {}, []
    reference_ids = (set(exported) - {r for r, m in planned.items() if m["model_id"] != "reference"}) & measured_ids
    if not reference_ids:
        raise ValueError("reference sizing observations are absent")
    ref_mean_wall = average([receipts[r]["member_wall_s"] for r in reference_ids])
    ref_stream = max(receipts[r]["stream_s"] for r in reference_ids)
    # Registration S-7: these are run-level paired clock-stamp spans,
    # never the whole kit/meter stream or a calibration-capture duration.
    ran = [receipts[r] for r in sorted(measured_ids)]
    all_stream = max(r["stream_s"] for r in ran)
    gates.append(clock_line("session", all_stream, measured["clock"]))
    gates.append(line("thermal", "pass" if all(r["thermal_level"] == 0 for r in ran)
                      and not any(set(row["flag_codes"].split(";")) & {"thermal.os_level_nonzero", "thermal.powermetrics_pressure_elevated"}
                                  for row in rows) else "fail",
                      maximum_level=max(r["thermal_level"] for r in ran),
                      rule="block-6 catalog: thermal OS level above zero excludes the run"))
    for model, run_ids in groups.items():
        regime = measured["regimes"][model]
        floor = optional(regime["F_min_j"], "F_min_j", positive=True)
        resolution = optional(regime["census_resolution_w"], "census_resolution_w", positive=True)
        outside = optional(regime["outside_power_w"], "outside_power_w")
        regime_absent = [k for k, v in (("F_min_j", floor), ("census_resolution_w", resolution),
                                        ("outside_power_w", outside)) if v is None]
        run_ids = [r for r in run_ids if r in measured_ids]
        # R6 specifies the longest measured phase, not full sampler stream.
        # Include test-7 workloads; ignoring one could loosen P_limit.
        all_model = [r for r, m in planned.items() if m["model_id"] == model and r in measured_ids]
        tmax = max(number(exported[r]["dur_decode_s"], "decode duration", positive=True) for r in all_model)
        if regime_absent:
            gates.append(line("contention:" + model, "unavailable", T_max_s=tmax,
                              reason="regime receipt absent: " + ",".join(regime_absent)))
        else:
            p_limit = floor / (4 * tmax)  # R6 quarter-floor energy budget, joules/(4 seconds) = watts.
            registered_phase = regime.get("registered_T_phase_s")
            registered_p = None if registered_phase is None else floor / (4 * number(registered_phase, "registered T_phase", positive=True))
            flag_reason = ("registered_T_phase_absent" if registered_p is None else
                           "below_census_resolution" if registered_p < resolution else None)
            gates.append(line("contention:" + model,
                              "flag_only" if flag_reason else "pass" if outside < registered_p else "fail",
                              P_limit_w=p_limit, F_min_j=floor, T_max_s=tmax,
                              below_census_resolution=p_limit < resolution,
                              census_resolution_w=resolution, observed_outside_power_w=outside,
                              registered_P_limit_w=registered_p, reason=flag_reason,
                              alternative_exceeds_quarter_floor=outside >= p_limit))
        if w is None or cq is None or floor is None:
            gates.append(line("cpu_contention:" + model, "unavailable", rule="w * max(0, C - k*c_q) >= F_min/4",
                              reason="cpu_contention or regime receipt absent"))
        else:
            alternative = []
            for run_id in all_model:
                receipt = receipts[run_id]
                c = number(receipt["outside_cpu_s"], "outside CPU seconds")
                k = integer(receipt["census_quanta"], "census quanta")
                # Registration §8.5 / S-8: subtract quiet CPU time once per
                # census quantum, clamp negative excess to zero, then multiply w.
                excess = max(Decimal(0), c - k * cq)
                alternative.append({"run_id": run_id, "model_id": model, "C_cpu_s": c, "k": k,
                                    "excess_cpu_s": excess, "added_energy_j": w * excess,
                                    "quarter_floor_j": floor / 4, "would_exclude": w * excess >= floor / 4})
            cpu_alternative.extend(alternative)
            gates.append(line("cpu_contention:" + model, "flag_only",
                              would_exclude=sum(r["would_exclude"] for r in alternative),
                              rule="w * max(0, C - k*c_q) >= F_min/4",
                              reason="registered round-1 exclusion not adopted; labelled alternative only"))
        t10 = regime.get("registered_T10_s")
        bound = optional(regime["operative_bound_s"], "operative_bound_s")
        gates.append(line("calibration_T10:" + model, "flag_only" if t10 is None else
                          "unavailable" if bound is None else
                          "pass" if bound <= number(t10, "registered T10", positive=True) else "fail",
                          registered_T10_s=t10, operative_bound_s=bound,
                          reason="registered_T10_absent" if t10 is None else
                          "operative bound absent" if bound is None else None))
        energies = [number(exported[r]["phase_decode_j"], "decode energy") for r in checks[model] if r in measured_ids]
        # R8.6 is structure only. Do not invent an energy/SNR cut to drop
        # 8B-8bit: report the measured floor ratios for registration review.
        gates.append(line("resolvability:" + model, "unavailable" if floor is None else "flag_only",
                          minimum_decode_to_floor=None if floor is None else min(energies) / floor,
                          reason="regime receipt absent: F_min_j" if floor is None else
                          "non-claim diagnostic; roster is frozen only at registration"))
        mean_request = average([receipts[r]["request_s"] for r in run_ids])
        mean_wall = average([receipts[r]["member_wall_s"] for r in run_ids])
        stream = max(ref_stream, *(receipts[r]["stream_s"] for r in all_model))
        # Each science module has fifty runs (R6). Member wall time already
        # includes load, warm-up, idle, settle within a run and reduction.
        models[model] = {"request_mean_s": mean_request, "member_wall_mean_s": mean_wall,
                         "measured_margin": margin, "est_minutes": 50 * mean_wall * (1 + margin) / 60,
                         "T_stream_max_s": stream,
                         "bytes_per_member": max(receipts[r]["retained_bytes"] for r in all_model)}
        if not margin_complete:
            models[model].update(measured_margin_complete=False, runs_measured=len(run_ids))
        gates.append(clock_line(model, stream, measured["clock"]))
    disk = measured["disk"]
    fixed_bytes = integer(disk["fixed_retained_bytes"], "fixed retained bytes")
    footprint = fixed_bytes + sum(r["retained_bytes"] for r in receipts.values())
    free = integer(disk["pre_arm_free_bytes"], "pre-arm free bytes")
    gates.append(line("disk:kit", "pass" if free >= footprint + RESERVE_BYTES else "fail",
                      measured_footprint_bytes=footprint, reserve_bytes=RESERVE_BYTES,
                      required_free_bytes=footprint + RESERVE_BYTES, pre_arm_free_bytes=free))
    sizing = measured["sizing"]
    # Explicitly measured desk/stage overheads, never block-5 pilot proxies.
    fixed_s = optional(sizing["fixed_desk_s"], "fixed desk seconds")
    stage_s = optional(sizing["collection_stage_overhead_s"], "collection stage overhead")
    sizing_absent = [k for k, v in (("fixed_desk_s", fixed_s), ("collection_stage_overhead_s", stage_s)) if v is None]
    ref_bytes = max(receipts[r]["retained_bytes"] for r in reference_ids)
    sessions = {}
    for n in range(1, 7):
        for pass_id in (1, 2):
            pack_id = f"bytes-s{n}-p{pass_id}"
            tree = read(Path(repo_root) / "configs/campaigns" / pack_id / "plan_tree.json")
            mids = [m.removeprefix("bytes-") for m in tree["module_order"]]
            collections = [s for s in tree["stage_graph"] if s["kind"] == "campaign_collection"]
            science_count = len(tree["science"])
            reference_count = sum(s["expected_count"] for s in collections) - science_count
            # SETTLE_S is registered by the chain, before pre-calibration
            # and every collection. Fixed desk seconds excludes these and
            # member time; the README defines the disjoint measured terms.
            seconds = None if sizing_absent else (
                (sum(50 * models[m]["member_wall_mean_s"] for m in mids)
                 + reference_count * ref_mean_wall) * (1 + margin)
                + (len(collections) + 1) * SETTLE_S + len(collections) * stage_s + fixed_s)
            projected_bytes = fixed_bytes + reference_count * ref_bytes + sum(50 * models[m]["bytes_per_member"] for m in mids)
            sessions[pack_id] = {"programmed_span_s": seconds, "est_minutes": None if seconds is None else seconds / 60,
                                 "T_stream_max_s": max(models[m]["T_stream_max_s"] for m in mids),
                                 "measured_margin": margin, "projected_footprint_bytes": projected_bytes,
                                 "required_free_bytes": projected_bytes + RESERVE_BYTES,
                                 "modules": {m: models[m] for m in mids}, "non_claim": True}
            if not margin_complete:
                sessions[pack_id]["measured_margin_complete"] = False
            gates.append(line("disk:" + pack_id, "pass" if free >= projected_bytes + RESERVE_BYTES else "fail",
                              **{k: sessions[pack_id][k] for k in ("projected_footprint_bytes", "required_free_bytes")},
                              pre_arm_free_bytes=free))
            if sizing_absent:
                gates.append(line("sizing:" + pack_id, "unavailable", est_minutes=None,
                                  reason="sizing receipt absent: " + ",".join(sizing_absent)))
            else:
                gates.append(line("sizing:" + pack_id, "pass" if margin_complete else "flag_only",
                                  est_minutes=seconds / 60,
                                  note="fixed session bypasses modular 265-minute cap (Addendum 5.5)",
                                  **({} if margin_complete else
                                     {"reason": "margin from incomplete check/soak groups (see spread_groups)"})))
    statuses = {g["status"] for g in gates}
    return {"schema_version": "joulewise.bytes_c5.v1", "non_claim": True, "session_id": session,
            "measured_margin": margin, "spread_groups": spread_groups,
            "models": models, "sessions": sessions, "gates": gates,
            "cpu_contention_alternative": cpu_alternative,
            "status": "fail" if "fail" in statuses else "unavailable" if "unavailable" in statuses else "pass",
            "unmeasured_members": unmeasured,
            "registration_ready": False,
            "notes": ["Candidates only: no registered pack, thresholds or roster is written.",
                      "Registered clock HOLD uses 5 ms with h=0 and run-level paired stamp spans, not kit/capture streams.",
                      "Registration S-7 uses measured rate r; R6 live frequency word is reported separately as diagnostic.",
                      "Absent registered T10/T_phase is flag only (round-2 rule 282a81a02).",
                      "No fixed planning margin: max measured request max/min - 1 (brief P6)."]}


def json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError("unsupported JSON value")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--measurements", type=Path, required=True)
    parser.add_argument("--kit-plan", type=Path, default=KIT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    sidecar_path = args.runs.with_name(args.runs.name.removesuffix(".runs.csv") + ".session.json")
    try:
        with args.runs.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        result = calculate(rows, read(sidecar_path), read(args.measurements), read(args.kit_plan))
        result["inputs"] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (args.runs, sidecar_path, args.measurements, args.kit_plan)}
    except (OSError, ValueError, KeyError, TypeError, ArithmeticError) as exc:
        print("bytes_gates: " + str(exc), file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, default=json_default, allow_nan=False) + "\n")
    for gate in result["gates"]:
        print(gate["gate"] + ": " + gate["status"].replace("_", " "))
    # 1 also covers a written C5 whose lines are "unavailable" (receipt absent).
    return 2 if result["status"] == "fail" else 1 if result["status"] == "unavailable" else 0


if __name__ == "__main__":
    raise SystemExit(main())
