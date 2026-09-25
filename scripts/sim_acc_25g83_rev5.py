#!/usr/bin/env python3
"""R5/R10 desk simulation; no capture or artifact issuance."""
from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_EVEN
from functools import lru_cache
import json
import math
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from joulewise.calibration_bracketing import (  # noqa: E402
    BRACKET_SCREEN_QUANTUM_S, D125_SCREEN_FLOOR_S,
    PREFLIGHT_LEVEL_SCREEN_QUANTUM_S,
    issued_calibration_allowance_projection, load_calibration_acceptance_bound,
)
from joulewise.detection_floor import comparative_false_effect_floor  # noqa: E402
from joulewise.analysis_engine.claims import evaluate_claim  # noqa: E402
from joulewise.analysis_engine.estimators import (  # noqa: E402
    DeterministicBoundTerm, PairedObservation, estimate_paired_blocks,
)
from joulewise.analysis_engine import estimators as production_estimators  # noqa: E402
from scripts import issue_calibration_acceptance_generation as issuer  # noqa: E402

production_estimators.student_t_quantile = lru_cache(maxsize=None)(
    production_estimators.student_t_quantile
)
issuer.student_t_quantile = lru_cache(maxsize=None)(issuer.student_t_quantile)
MODELS = ("gaussian", "heavy_excursions", "serial_ar1", "block_drift")
SEED = 25098312
PREDECESSOR_C = Decimal("0.010164834757777545")
POWER_STEP_W = 33.0


def exact_binomial_interval_95(events: int, trials: int) -> tuple[float, float]:
    """Two-sided Clopper-Pearson limits by monotone binomial-tail inversion."""
    def tail(probability: float, *, at_least: bool) -> float:
        indices = range(events, trials + 1) if at_least else range(events + 1)
        return sum(math.comb(trials, j) * probability**j *
                   (1 - probability)**(trials - j) for j in indices)

    lower = 0.0
    if events:
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if tail(mid, at_least=True) < .025:
                lo = mid
            else:
                hi = mid
        lower = (lo + hi) / 2
    upper = 1.0
    if events < trials:
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if tail(mid, at_least=False) > .025:
                lo = mid
            else:
                hi = mid
        upper = (lo + hi) / 2
    return lower, upper


def draw_series(rng: random.Random, model: str) -> tuple[list[float], float]:
    """Twenty-four R5 B values and a later, same-model bracket PRE value."""
    base = 0.030
    if model == "gaussian":
        return [max(0.001, base + rng.gauss(0, .002)) for _ in range(24)], max(
            0.001, base + rng.gauss(0, .002)
        )
    if model == "heavy_excursions":
        values = [max(0.001, base + rng.gauss(0, .002)) for _ in range(25)]
        # Fixed, outcome-independent positions; exactly two 0.15 s additions
        # in the 24 registered slots. The later draw has matching 2/24 risk.
        for index in (5, 17):
            values[index] += .15
        if rng.random() < 2 / 24:
            values[24] += .15
        return values[:24], values[24]
    if model == "serial_ar1":
        state = rng.gauss(0, .002)
        values = []
        for _ in range(25):
            state = .8 * state + .002 * math.sqrt(1 - .8**2) * rng.gauss(0, 1)
            values.append(max(.001, base + state))
        return values[:24], values[24]
    if model == "block_drift":
        # Two 12-slot windows. The later sample is in the high block.
        values = [max(.001, base + (.004 if i >= 12 else -.004)
                      + rng.gauss(0, .0015)) for i in range(25)]
        return values[:24], values[24]
    raise ValueError(model)


def issued_numbers(values: list[float]) -> dict[str, float | bool | int]:
    """Production issuer arithmetic with exactly the two ruled Revision 5 edits.

    The production CLI permits n=12 and S=C for the exact Revision 5 epoch.
    Its corpus statistics, prediction, screen and ceiling functions are called
    directly; this helper applies the same C=max(old,Q99,S) and excursion rules.
    """
    members = [{"member_id": f"d{i:02d}", "b_fiducial_s": repr(value)}
               for i, value in enumerate(values, 1)]
    stats = issuer._corpus_statistics(members)
    n = len(values)
    q99 = Decimal(issuer.two_draw_prediction_lexeme(
        issuer.student_t_quantile("0.995", n - 1),
        stats["sample_sd_presentation_s"]["value"],
    ))
    quantized_range = Decimal(stats["range_s"]).quantize(
        BRACKET_SCREEN_QUANTUM_S, rounding=ROUND_HALF_EVEN
    )
    screen = issuer.envelope_screen(quantized_range, D125_SCREEN_FLOOR_S)
    old_ceiling = issuer.envelope_ceiling(PREDECESSOR_C, q99)
    ceiling = max(old_ceiling, screen)  # ruling 2(i)
    excursions = sum(value > .075 for value in values)
    return {
        "level_s": float(stats["maximum_s"]), "screen_s": float(screen),
        "ceiling_s": float(ceiling), "zero_headroom": ceiling == screen,
        "excursions": excursions, "excursion_limited": excursions >= 2,
        "issuable": max(values) <= .25,  # ruling 2(h), never B-exclude
    }


def one_claim(rng: random.Random, numbers: dict, pre: float) -> dict:
    """One zero-effect claim after the projected production bracket arithmetic."""
    post = max(.001, pre + rng.gauss(0, .001))
    drift = abs(pre - post)
    bracket_pass = (numbers["issuable"] and pre <= numbers["level_s"]
                    and drift <= numbers["ceiling_s"])
    allowance = max(drift, numbers["screen_s"])
    operative_b = max(pre, post) + allowance
    width_j = POWER_STEP_W * operative_b
    # A timing artifact of 80% of the allowed displacement; no real effect.
    # Independent local error is used in both the floor sample and claim.
    floor_sample = [rng.gauss(0, .30) for _ in range(10)]
    floor = comparative_false_effect_floor(
        floor_sample, admissible_half_widths_j=[width_j] * 10
    ).guarded_floor_j
    values = [.8 * width_j + rng.gauss(0, .30) for _ in range(10)]
    observations = tuple(PairedObservation(
        f"b{i}", 0.0, value,
        deterministic_terms=(DeterministicBoundTerm("timing", 0.0, width_j),),
    ) for i, value in enumerate(values))
    estimate = estimate_paired_blocks(observations)
    met = estimate.metrology_aware_ci95
    decision = estimate.decision_interval
    floor_pass = abs(estimate.estimate) > floor
    interval_pass = not (decision.lower <= 0 <= decision.upper)
    verdict = evaluate_claim(
        estimate=estimate.estimate,
        metrology_aware_ci95={"lower": met.lower, "upper": met.upper},
        decision_interval={"lower": decision.lower, "upper": decision.upper},
        floor_gate_j=floor, adjusted_rejected=estimate.raw_p < .05,
    )
    return {
        "bracket_pass": bracket_pass, "floor_pass": floor_pass,
        "interval_pass": interval_pass,
        "false_admission": bracket_pass and verdict["outcome"] == "direction_supported",
    }


def run(trials: int, screen_trials: int, valid_probability: float = 30 / 38) -> list[dict]:
    rows = []
    for model_index, model in enumerate(MODELS):
        rng = random.Random(SEED + 1000 * model_index)
        counts = {key: 0 for key in (
            "w1_futility", "w3_opened", "shortfall_after_w3", "issuance_refusal",
            "excursion_limited", "zero_headroom", "later_level_refusal",
            "bracket_pass", "floor_pass", "interval_pass", "false_admission",
        )}
        for _ in range(trials):
            values, later_pre = draw_series(rng, model)
            valid = [rng.random() < valid_probability for _ in range(36)]
            w1 = [value for value, keep in zip(values[:12], valid[:12]) if keep]
            if len(w1) < 6:
                counts["w1_futility"] += 1
                continue
            w2 = [value for value, keep in zip(values[12:24], valid[12:24]) if keep]
            retained = w1 + w2
            if len(retained) < 12:
                counts["w3_opened"] += 1
                extra, _ = draw_series(rng, model)
                retained += [value for value, keep in zip(extra[:12], valid[24:]) if keep]
            if len(retained) < 12:
                counts["shortfall_after_w3"] += 1
                continue
            numbers = issued_numbers(retained)
            counts["issuance_refusal"] += not numbers["issuable"]
            counts["excursion_limited"] += numbers["excursion_limited"]
            counts["zero_headroom"] += numbers["zero_headroom"]
            if Decimal(repr(later_pre)) > Decimal(repr(numbers["level_s"])) .quantize(
                    PREFLIGHT_LEVEL_SCREEN_QUANTUM_S, rounding=ROUND_HALF_EVEN):
                counts["later_level_refusal"] += 1
            claim = one_claim(rng, numbers, later_pre)
            for key in ("bracket_pass", "floor_pass", "interval_pass", "false_admission"):
                counts[key] += claim[key]
        level_interval = exact_binomial_interval_95(counts["later_level_refusal"], trials)
        admission_interval = exact_binomial_interval_95(counts["false_admission"], trials)
        rows.append({"model": model, "trials": trials,
                     "valid_probability": valid_probability, **counts,
                     "false_admission_rate": counts["false_admission"] / trials,
                     "later_level_refusal_rate": counts["later_level_refusal"] / trials,
                     "later_level_refusal_interval_95": level_interval,
                     "false_admission_interval_95": admission_interval,
                     "zero_event_upper_bound_95": 1 - .05 ** (1 / trials)})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=200)
    parser.add_argument("--valid-probability", type=float, default=30 / 38)
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("trials must be positive")
    if not 0 <= args.valid_probability <= 1:
        parser.error("valid probability must be in [0, 1]")
    reference = load_calibration_acceptance_bound()
    if reference is None:
        raise RuntimeError("production bracket reference is unavailable")
    projection = issued_calibration_allowance_projection(
        reference, pre_exact_bound_lexeme_s="0.030",
        post_exact_bound_lexeme_s="0.031",
    )
    if projection is None or projection["allowance_rule"] != "max(observed_drift_s,bracket_screen_s)" or projection["allowance_embedding_count"] != 1:
        raise RuntimeError("production bracket allowance rule changed")
    rows = run(args.trials, args.trials, args.valid_probability)
    print(json.dumps({"seed": SEED, "reference": reference["acceptance_id"],
                      "scenario": "zero true contrast; 80% of bracket timing bound as observed artifact",
                      "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
