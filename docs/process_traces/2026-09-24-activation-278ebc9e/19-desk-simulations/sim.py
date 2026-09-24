#!/usr/bin/env python3
"""R-Q4(a) desk Monte Carlo. Run from this directory; stdlib only.

All admission/floor decisions call repository production functions. The only
synthetic adapter is the equivalence-night session's already-retained rows:
ledger authentication cannot be fabricated from generated numbers. The real
evaluate_session function performs the numerical decision.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from functools import lru_cache
import json
import math
from pathlib import Path
import random
import statistics
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from joulewise.detection_floor import _floor_estimate, comparative_false_effect_floor
from joulewise.dominance_closeout import dominance_ratio
from joulewise.analysis_engine.claims import evaluate_claim
from joulewise.analysis_engine.estimators import (PairedObservation,
    DeterministicBoundTerm, estimate_paired_blocks, tost_p_value)
from joulewise.analysis_engine import estimators as production_estimators
from joulewise.analysis_engine.distributions import student_t_quantile
from joulewise.analysis_engine.multiplicity import holm_adjust
from scripts import epoch_equivalence_check as eq

student_t_quantile = lru_cache(maxsize=None)(student_t_quantile)
# Memoize the production quantile used by estimate_paired_blocks; its only
# varying input here is df=9 or 29. The implementation and results are intact.
production_estimators.student_t_quantile = lru_cache(maxsize=None)(production_estimators.student_t_quantile)

HERE = Path(__file__).resolve().parent
SEEDS = {"smoke": 278, "floor": 278407, "equivalence": 316407}
MODELS = {
    "gaussian": "Independent standard Gaussian local errors with one shared night shock across twelve components.",
    "heavy_t3": "Variance-one Student t with three degrees of freedom, plus one shared night shock.",
    "linear_drift": "Gaussian local errors plus a centered linear trend across each night's ordered blocks.",
    "shared_local": "Gaussian error has shared and local terms; timing offset is split into w/2 shared across the night and w/2 local per block.",
}


def noise(rng, model, n, shared=0.0):
    if model == "heavy_t3":
        local = [rng.gauss(0, 1) / math.sqrt(rng.gammavariate(1.5, 2 / 3) * 3) for _ in range(n)]
    else:
        local = [rng.gauss(0, 1) for _ in range(n)]
    if model == "linear_drift":
        return [x + shared + 1.5 * (i - (n - 1) / 2) / max(n - 1, 1) for i, x in enumerate(local)]
    if model == "shared_local":
        return [shared + x / math.sqrt(2) for x in local]
    return [shared + x for x in local]


def shared_shock(rng, model):
    return rng.gauss(0, 1 / math.sqrt(2)) if model == "shared_local" else rng.gauss(0, 0.5)


def mean(xs):
    return math.fsum(xs) / len(xs)


def ci_dict(interval):
    return {"lower": interval.lower, "upper": interval.upper}


def one_floor(values, w):
    point = _floor_estimate("comparative", values, mean(values), abs(mean(values)))
    widened = comparative_false_effect_floor(values, admissible_half_widths_j=[w] * len(values))
    ratio = dominance_ratio(corner_widened_unguarded_floor_j=widened.unguarded_floor_j,
                            point_unguarded_floor_j=point.unguarded_floor_j)
    return widened, ratio


def claim(values, floor, w, *, equivalence=False, adjusted_rejected=None):
    observations = tuple(PairedObservation(f"b{i}", 0.0, value,
        deterministic_terms=(DeterministicBoundTerm("timing", 0.0, w),))
        for i, value in enumerate(values))
    estimate = estimate_paired_blocks(observations)
    rejected = estimate.raw_p < 0.05 if adjusted_rejected is None else adjusted_rejected
    kwargs = {}
    if equivalence:
        margin = 4.0
        rejected = tost_p_value(estimate.estimate, estimate.se_total, estimate.df, margin)[2] < 0.05
        kwargs["equivalence"] = {"method": "tost_v1", "margin": margin}
    verdict = evaluate_claim(estimate=estimate.estimate,
        metrology_aware_ci95=ci_dict(estimate.metrology_aware_ci95),
        decision_interval=ci_dict(estimate.decision_interval), floor_gate_j=floor,
        adjusted_rejected=rejected, **kwargs)
    return estimate, verdict


def floor_grid(trials):
    rng = random.Random(SEEDS["floor"])
    rows = []
    # Calibration n, analysis n, effect, and w/sigma form a full Cartesian grid.
    for model in MODELS:
        for ncal in (5, 8):
            for w in (0.5, 1.0, 2.0):
                for nanal in (10, 30):
                    for effect in (0.0, 2.0, 5.0):
                        counts = dict(false_admission=0, missed_effect=0, coverage=0,
                            decision_coverage=0, refusal=0, equiv_admission=0,
                            equiv_refusal=0,
                            joint12_dominance=0, component_dominance=0,
                            floor_predictive_coverage=0)
                        ratios, floors = [], []
                        for _ in range(trials):
                            shock = shared_shock(rng, model)
                            timing_shared = rng.uniform(-w/2, w/2) if model == "shared_local" else 0.0
                            passing = []
                            components = []
                            for component in range(12):
                                cal = noise(rng, model, ncal, shock)
                                if model == "shared_local":
                                    cal = [x + timing_shared + rng.uniform(-w/2, w/2) for x in cal]
                                floor, ratio = one_floor(cal, w)
                                ratios.append(ratio["ratio"])
                                floors.append(floor.guarded_floor_j)
                                passing.append(ratio["passes"])
                                data = [effect + x for x in noise(rng, model, nanal, shock)]
                                if model == "shared_local":
                                    data = [x + timing_shared + rng.uniform(-w/2, w/2) for x in data]
                                provisional, _ = claim(data, floor.guarded_floor_j, w)
                                components.append((data, floor.guarded_floor_j, provisional))
                            adjusted = holm_adjust({str(i): c[2].raw_p for i, c in enumerate(components)}, m=12)
                            for i, (data, floor_value, _) in enumerate(components):
                                est, verdict = claim(data, floor_value, w,
                                    adjusted_rejected=adjusted[str(i)] < 0.05)
                                _, equiv = claim(data, floor_value, w, equivalence=True)
                                direction = verdict["outcome"] == "direction_supported"
                                counts["false_admission"] += effect == 0 and direction
                                counts["missed_effect"] += effect != 0 and not direction
                                counts["coverage"] += est.metrology_aware_ci95.lower <= effect <= est.metrology_aware_ci95.upper
                                counts["decision_coverage"] += est.decision_interval.lower <= effect <= est.decision_interval.upper
                                counts["floor_predictive_coverage"] += abs(data[0]-effect) + w <= floor_value
                                counts["refusal"] += verdict["outcome"] in ("not_estimable", "not_resolvable")
                                counts["equiv_admission"] += equiv["outcome"] == "equivalent"
                                counts["equiv_refusal"] += equiv["outcome"] in ("not_estimable", "not_resolvable")
                            counts["joint12_dominance"] += all(passing)
                            counts["component_dominance"] += sum(passing)
                        den = trials * 12
                        rows.append(dict(model=model, calibration_n=ncal, analysis_n=nanal,
                            effect_sigma=effect, w_over_sigma=w, trials=trials,
                            timing_shared_width_sigma=w/2 if model == "shared_local" else 0.0,
                            timing_local_width_sigma=w/2 if model == "shared_local" else w,
                            false_admission=counts["false_admission"] / den if effect == 0 else "",
                            missed_effect=counts["missed_effect"] / den if effect != 0 else "",
                            coverage=counts["coverage"] / den,
                            decision_coverage=counts["decision_coverage"] / den,
                            floor_predictive_coverage=counts["floor_predictive_coverage"] / den,
                            refusal=counts["refusal"] / den,
                            equiv_admission=counts["equiv_admission"] / den,
                            equiv_refusal=counts["equiv_refusal"] / den,
                            component_dominance=counts["component_dominance"] / den,
                            joint12_dominance=counts["joint12_dominance"] / trials,
                            median_r=statistics.median(ratios),
                            median_guarded_floor_sigma=statistics.median(floors)))
    return rows


def real_old_rule(old, new):
    # Numerical decision of evaluate_session is real; replace only authenticated
    # ledger extraction with declared synthetic retained values.
    retained = [{"slot": f"d{i:02d}", "attempt_id": f"sim{i}",
                 "b_fiducial_s": str(Decimal(str(x)))} for i, x in enumerate(new, 1)]
    fake = SimpleNamespace(session_kind="derivation", state="finalized",
        abort_reason=None, declared_slots=tuple(x["slot"] for x in retained))
    envelope = {"level_screen_s": str(max(old)), "bracket_screen_s": str(max(old)-min(old))}
    original = eq._slot_outcomes
    try:
        eq._slot_outcomes = lambda session: ([], retained)
        return eq.evaluate_session(fake, "synthetic", envelope)["verdict"]
    finally:
        eq._slot_outcomes = original


def replacement(old, new, margin, variance_bound, alpha):
    if len(old) < 17 or len(new) < 12:
        return "INCONCLUSIVE"
    delta = mean(new) - mean(old)
    old_v, new_v = statistics.variance(old), statistics.variance(new)
    se = math.sqrt(old_v / len(old) + new_v / len(new))
    # Conservative Welch lower df, rounded down; valid for this design's
    # independent samples and deliberately wider than the Welch interval.
    df = min(len(old)-1, len(new)-1)
    critical = student_t_quantile(1-alpha, df)
    ratio = new_v / old_v
    return "PASS" if (abs(delta) + critical * se < margin and
        1 / variance_bound <= ratio <= variance_bound) else "FAIL"


def equivalence_grid(trials):
    rng = random.Random(SEEDS["equivalence"])
    rows = []
    for model in MODELS:
        for old_n in (12, 17):
            for m in (4, 6, 7, 12):
                for shift, variance_mult in ((0.0, 1.0), (3.0, 1.0), (5.0, 1.0), (0.0, 4.0)):
                    for margin, vr in ((1.5, 4.0), (2.0, 6.0), (2.5, 8.0),
                                       (3.5, 10.0), (3.5, 20.0), (4.0, 30.0)):
                        old_pass = new_pass = old_fail = new_fail = coverage = 0
                        for _ in range(trials):
                            old = noise(rng, model, old_n, shared_shock(rng, model))
                            fresh = noise(rng, model, m, shared_shock(rng, model))
                            new = [shift + math.sqrt(variance_mult) * x for x in fresh]
                            old_verdict = real_old_rule(old, new)
                            new_verdict = replacement(old, new, margin, vr, 0.05)
                            old_pass += old_verdict == "PASS"
                            new_pass += new_verdict == "PASS"
                            old_fail += old_verdict == "FAIL"
                            new_fail += new_verdict == "FAIL"
                            se = math.sqrt(statistics.variance(old)/len(old) + statistics.variance(new)/len(new))
                            half = student_t_quantile(0.95, min(len(old)-1,len(new)-1))*se
                            coverage += abs((mean(new)-mean(old))-shift) <= half
                        rows.append(dict(model=model, old_n=old_n, retained_m=m,
                            shift_sigma=shift, variance_multiplier=variance_mult,
                            margin_sigma=margin, variance_ratio_bound=vr, alpha=0.05,
                            trials=trials, old_pass=old_pass/trials,
                            proposed_pass=new_pass/trials,
                            old_false_alarm=old_fail/trials if shift == 0 and variance_mult == 1 else "",
                            proposed_false_alarm=new_fail/trials if shift == 0 and variance_mult == 1 else "",
                            old_missed_change=old_pass/trials if shift or variance_mult != 1 else "",
                            proposed_missed_change=new_pass/trials if shift or variance_mult != 1 else "",
                            ci90_coverage=coverage/trials,
                            old_refusal=1-(old_pass+old_fail)/trials,
                            proposed_refusal=1-(new_pass+new_fail)/trials))
    return rows


def smoke(trials):
    rng = random.Random(SEEDS["smoke"])
    out = []
    point_floors = []
    for _ in range(trials):
        values = [rng.gauss(0, 1) for _ in range(10)]
        point_floors.append(one_floor(values, 0.0)[0].guarded_floor_j)
    print(f"n=10 point-only median_F={statistics.median(point_floors):.3f} sigma; SD(mean)={1/math.sqrt(10):.3f} sigma")
    rng = random.Random(SEEDS["smoke"])
    for w in (0.5, 0.75, 1.0, 1.5, 2.0):
        passes = 0
        floors = []
        for _ in range(trials):
            values = [rng.gauss(0, 1) for _ in range(10)]
            floor, ratio = one_floor(values, w)
            passes += ratio["passes"]
            floors.append(floor.guarded_floor_j)
        out.append((w, passes/trials, statistics.median(floors)))
    return out


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--equivalence-only", action="store_true")
    parser.add_argument("--trials", type=int)
    args = parser.parse_args()
    if args.smoke:
        for w, rate, floor in smoke(args.trials or 400):
            print(f"w/sigma={w:.2f} P(R>=2)={rate:.3f} median_F={floor:.3f}")
        return
    n = args.trials or 40
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    floors = [] if args.equivalence_only else floor_grid(n)
    if floors:
        write_csv(out / "floor_claim_cells.csv", floors)
        (out / "floor_claim_cells.json").write_text(json.dumps(floors, indent=2) + "\n")
    equiv = equivalence_grid(max(500, 20*n))
    write_csv(out / "equivalence_cells.csv", equiv)
    (out / "equivalence_cells.json").write_text(json.dumps(equiv, indent=2) + "\n")
    metadata = {"seeds": SEEDS, "models": MODELS, "floor_trials_per_cell": n,
        "equivalence_trials_per_cell": max(500, 20*n), "sigma": 1.0,
        "dependence": "Each trial shares a night shock across twelve components; joint verdict evaluated directly.",
        "floor_cells": len(floors) if floors else 144, "equivalence_cells": len(equiv),
        "old_rule_adapter": "Synthetic retained rows bypass ledger authentication; real evaluate_session makes numerical verdict.",
        "replacement_status": "PROPOSED; not registered or installed."}
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"floor_claim_cells={len(floors) if floors else 144} trials={n}")
    print(f"equivalence_cells={len(equiv)} trials={max(500,20*n)}")
    print("results: floor_claim_cells.csv/.json equivalence_cells.csv/.json metadata.json")


if __name__ == "__main__":
    main()
