#!/usr/bin/env python3
"""Synthetic-only B3 operating characteristics; Python stdlib, one CPU process.

No repository runtime, data/model reader, native backend, or network import.
Inputs are constants/CLI numbers. Output is JSON plus a compact quoted summary.
See B3-SIM-sol2.md for authority, estimands, assumptions and limitations.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import random
import time


PAIRS = ("spam_filter_update", "bank_transfer_2")
WINDOW_CAP = 8
PER_PAIR = 7
TARGET = 39
HOT_PROB = 0.25
SCALES = (0.0, 0.25, 0.5)
DESIGNS = ("count6", "count7", "fixed8")
SQRT3 = math.sqrt(3)
Z95 = 1.959963984540054


@dataclass(frozen=True)
class Scenario:
    name: str
    exclusion: float
    informative: bool = False
    one_window_lost: bool = False

    def rates(self):
        # .75*(p/2) + .25*(2.5*p) == p.
        p = self.exclusion
        return (p / 2, 2.5 * p) if self.informative else (p, p)


SCENARIOS = tuple(
    Scenario(f"{kind}{round(100*p):02d}", p, informative)
    for kind, informative in (("iid", False), ("hot", True))
    for p in (0.05, 0.10, 0.20)
) + (Scenario("lost1_iid10", 0.10, one_window_lost=True),)


def rank05(m):
    """One-based ceil(.95*(m+1)), without float-boundary ambiguity."""
    return (19 * (m + 1) + 19) // 20


def thresholds(values):
    if len(values) < TARGET:
        raise ValueError("insufficient calibration; no threshold")
    values = sorted(values)
    return {"max": values[-1], "rank05": values[rank05(len(values)) - 1],
            "literal38": values[37]}


def stop_window(cumulative, minimum):
    """Check both pairs after final adjudication; failed attempts consume cap."""
    for n in range(minimum, WINDOW_CAP + 1):
        if all(m >= TARGET for m in cumulative[n - 1]):
            return n
    return WINDOW_CAP


def eligible_hot_weight(scenario):
    cold_q, hot_q = scenario.rates()
    hot_yield = HOT_PROB * (1 - hot_q)
    return hot_yield / (hot_yield + (1 - HOT_PROB) * (1 - cold_q))


def future_tail(threshold, tau, scenario, shift=0.0):
    """P(S > threshold | eligible), analytic mixture; epsilon ~ N(0,1).

    A future assigned episode's H is independent of calibration. Eligibility
    uses the SAME H-dependent rule. Equal slots/window imply this eligible-row
    mixture, rather than giving each nonempty future window equal weight.
    """
    hot_weight = eligible_hot_weight(scenario)
    hot_mean = SQRT3 * tau + shift
    cold_mean = -tau / SQRT3 + shift
    hot_tail = 0.5 * math.erfc((threshold - hot_mean) / math.sqrt(2))
    cold_tail = 0.5 * math.erfc((threshold - cold_mean) / math.sqrt(2))
    return hot_weight * hot_tail + (1 - hot_weight) * cold_tail


def transport_allowance(tau):
    # Window intercept in [-tau/sqrt(3), sqrt(3)*tau]; future extra shift <= tau.
    return (1 + 4 / SQRT3) * tau


@dataclass
class Moments:
    n: int = 0
    total: float = 0.0
    total2: float = 0.0

    def add(self, x):
        self.n += 1
        self.total += x
        self.total2 += x * x

    def result(self):
        if not self.n:
            return {"n": 0, "mean": None, "mc_se": None, "mc95": None}
        mean = self.total / self.n
        variance = max(0.0, (self.total2 - self.total**2 / self.n) / (self.n - 1)) if self.n > 1 else 0.0
        se = math.sqrt(variance / self.n)
        return {"n": self.n, "mean": mean, "mc_se": se,
                "mc95": [mean - Z95 * se, mean + Z95 * se]}


@dataclass
class PairMoments:
    # Each tape is one independent MC unit; pairs share H, so average FIRST.
    average: Moments = field(default_factory=Moments)
    pair0: Moments = field(default_factory=Moments)
    pair1: Moments = field(default_factory=Moments)

    def add(self, values):
        self.average.add((values[0] + values[1]) / 2)
        self.pair0.add(values[0])
        self.pair1.add(values[1])

    def result(self):
        return {"pair_average": self.average.result(),
                PAIRS[0]: self.pair0.result(), PAIRS[1]: self.pair1.result()}


def wilson(hits, n):
    p = hits / n
    denom = 1 + Z95**2 / n
    center = (p + Z95**2 / (2*n)) / denom
    radius = Z95 * math.sqrt(p*(1-p)/n + Z95**2/(4*n*n)) / denom
    return {"hits": hits, "n": n, "probability": p,
            "mc95": [max(0.0, center-radius), min(1.0, center+radius)]}


def binomial_tail(n, eligible_probability, k=TARGET):
    return math.fsum(math.comb(n, j) * eligible_probability**j *
                     (1-eligible_probability)**(n-j) for j in range(k, n+1))


def exact_count_reference(p, slots=PER_PAIR):
    by_n = {str(n): binomial_tail(n*slots, 1-p)**2 for n in (6, 7, 8)}
    return {"both_by_window": by_n,
            "mean_count6_windows": 8-by_n["6"]-by_n["7"],
            "mean_count7_windows": 8-by_n["7"]}


def review_counterexample():
    """Enumerate Sol2 review's exact clustered example as an independent oracle."""
    success = {d: 0.0 for d in DESIGNS}
    false_alarm = {d: 0.0 for d in DESIGNS}
    for tape in itertools.product((0, 1), repeat=8):
        # hot: P=.1, three eligible scores of 1; cold: seven scores of 0.
        mass = .1**sum(tape) * .9**(8-sum(tape))
        cumulative = [(sum(3 if h else 7 for h in tape[:n]),)*2 for n in range(1, 9)]
        for design, minimum in zip(DESIGNS, (6, 7, 8)):
            n = stop_window(cumulative, minimum)
            if cumulative[n-1][0] < TARGET:
                continue
            success[design] += mass
            if not any(tape[:n]):
                false_alarm[design] += mass * .1
    return {d: {"success": success[d], "fpr_given_success": false_alarm[d]/success[d]}
            for d in DESIGNS}


def add_metrics(store, metrics):
    for name, values in metrics.items():
        store.setdefault(name, PairMoments()).add(values)


def simulate(scenario, replicates, seed):
    rng = random.Random(seed)
    hist = {d: {str(n): 0 for n in (6, 7, 8)} for d in DESIGNS}
    by_n_hits = {str(n): 0 for n in (6, 7, 8)}
    successful = 0
    hot_fraction_if_stop6 = Moments()
    first_hot_if_stop6 = Moments()
    hot_fraction_all = Moments()
    stats = {str(tau): {d: {} for d in DESIGNS} for tau in SCALES}
    deltas = {str(tau): {d: {} for d in DESIGNS[:2]} for tau in SCALES}
    cold_q, hot_q = scenario.rates()

    for _ in range(replicates):
        hot = [rng.random() < HOT_PROB for _ in range(WINDOW_CAP)]
        lost = rng.randrange(WINDOW_CAP) if scenario.one_window_lost else -1
        eps = []
        cumulative = []
        totals = [0, 0]
        for w in range(WINDOW_CAP):
            q = 1.0 if w == lost else hot_q if hot[w] else cold_q
            window = [[rng.gauss(0, 1) for _ in range(PER_PAIR) if rng.random() >= q]
                      for _ in PAIRS]
            eps.append(window)
            totals = [totals[p]+len(window[p]) for p in range(2)]
            cumulative.append(totals)
        used = {"count6": stop_window(cumulative, 6),
                "count7": stop_window(cumulative, 7), "fixed8": 8}
        for d in DESIGNS:
            hist[d][str(used[d])] += 1
        for n in (6, 7, 8):
            by_n_hits[str(n)] += all(m >= TARGET for m in cumulative[n-1])
        hot_fraction_all.add(sum(hot)/8)
        if used["count6"] == 6:
            hot_fraction_if_stop6.add(sum(hot[:6])/6)
            first_hot_if_stop6.add(float(hot[0]))
        if not all(m >= TARGET for m in totals):
            continue  # unresolved at cap; NEVER interpret failure as zero FPR.
        successful += 1
        for tau in SCALES:
            metrics_by_n = {}
            for n in set(used.values()):
                values = [[e + (SQRT3*tau if hot[w] else -tau/SQRT3)
                           for w in range(n) for e in eps[w][p]] for p in range(2)]
                cutoffs = [thresholds(v) for v in values]
                m = cumulative[n-1]
                metrics = {
                    "m": m,
                    "hot_eligible_fraction": [sum(len(eps[w][p]) for w in range(n) if hot[w])/m[p]
                                              for p in range(2)],
                    "iid_max_fpr_reference": [1/(x+1) for x in m],
                    "iid_rank05_fpr_reference": [(x+1-rank05(x))/(x+1) for x in m],
                    "iid_literal38_fpr_reference": [(x+1-38)/(x+1) for x in m],
                }
                for cutoff in ("max", "rank05", "literal38"):
                    t = [c[cutoff] for c in cutoffs]
                    metrics["threshold_"+cutoff] = t
                    for regime, shift in (("stable", 0.0), ("hotter", tau)):
                        metrics[f"fpr_{regime}_{cutoff}"] = [future_tail(x, tau, scenario, shift) for x in t]
                    if cutoff != "literal38":
                        metrics[f"fpr_hotter_{cutoff}_allowance"] = [
                            future_tail(x+transport_allowance(tau), tau, scenario, tau) for x in t]
                metrics_by_n[n] = metrics
            for d in DESIGNS:
                add_metrics(stats[str(tau)][d], metrics_by_n[used[d]])
            # Paired differences: same tape, success set and future population.
            for d in DESIGNS[:2]:
                a, b = metrics_by_n[used[d]], metrics_by_n[8]
                names = ("threshold_max", "threshold_rank05", "fpr_stable_max",
                         "fpr_stable_rank05", "fpr_hotter_max", "fpr_hotter_rank05")
                add_metrics(deltas[str(tau)][d], {k: [x-y for x, y in zip(a[k], b[k])] for k in names})

    # Nested prefixes imply pathwise monotone maxima and FPRs; catch bugs.
    for tau in SCALES:
        for d in DESIGNS[:2]:
            assert deltas[str(tau)][d]["threshold_max"].average.total <= 1e-8
            assert deltas[str(tau)][d]["fpr_stable_max"].average.total >= -1e-8
    return {
        "scenario": scenario.__dict__, "seed": seed, "replicates": replicates,
        "q_cold": cold_q, "q_hot": hot_q,
        "future_eligible_hot_weight": eligible_hot_weight(scenario),
        "success_both_by_cap": wilson(successful, replicates),
        "both_by_window": {n: wilson(k, replicates) for n, k in by_n_hits.items()},
        "windows": {d: {"histogram": hist[d],
                        "probabilities": {n: wilson(k, replicates) for n, k in hist[d].items()},
                        "mean": sum(int(n)*k for n, k in hist[d].items())/replicates}
                    for d in DESIGNS},
        "state_diagnostics": {"hot_fraction_all_eight": hot_fraction_all.result(),
                              "hot_fraction_given_stop6": hot_fraction_if_stop6.result(),
                              "first_window_hot_given_stop6": first_hot_if_stop6.result()},
        "metrics_given_both_success": {
            tau: {d: {k: v.result() for k, v in metrics.items()} for d, metrics in designs.items()}
            for tau, designs in stats.items()},
        "paired_delta_vs_fixed8": {
            tau: {d: {k: v.result() for k, v in metrics.items()} for d, metrics in designs.items()}
            for tau, designs in deltas.items()},
    }


def mean(result, tau, design, metric):
    return result["metrics_given_both_success"][str(tau)][design][metric]["pair_average"]["mean"]


def pct_ci(stat):
    lo, hi = stat["mc95"]
    return f'{100*stat["mean"]:.3f} [{100*lo:.3f},{100*hi:.3f}]'


def summarize(payload):
    out = [f'B3-SIM-sol2: {payload["replicates"]} tapes/scenario; seed={payload["seed"]}',
           "SYNTHETIC ONLY. FPR = eligible future row, conditional on BOTH pairs succeeding.",
           "FPR entries are percentages; intervals are 95% Monte Carlo intervals.",
           "\nCOUNTS (all tapes; N8 includes failures; same cap success for every design)",
           "scenario N6% N7% N8% E[N] P(both>=39 by8)% [Wilson95] E[N|min7]"]
    for r in payload["results"]:
        w = r["windows"]
        hist = w["count6"]["histogram"]
        cap = r["success_both_by_cap"]
        out.append(f'{r["scenario"]["name"]:12} '+" ".join(f'{100*hist[str(n)]/r["replicates"]:.3f}' for n in (6,7,8))+
                   f' {w["count6"]["mean"]:.4f} {100*cap["probability"]:.3f} '
                   f'[{100*cap["mc95"][0]:.3f},{100*cap["mc95"][1]:.3f}] {w["count7"]["mean"]:.4f}')
    out.extend(["\nFPR: max / rank05 (rank38 at m=39, actual rank at actual m)",
                "scenario tau regime count6 max/r05 count7 max/r05 fixed8 max/r05 count6+allowance max/r05"])
    for r in payload["results"]:
        for tau in SCALES:
            for regime in ("stable", "hotter"):
                vals = [f'{100*mean(r,tau,d,"fpr_"+regime+"_max"):.3f}/'
                        f'{100*mean(r,tau,d,"fpr_"+regime+"_rank05"):.3f}' for d in DESIGNS]
                allowance = (f'{100*mean(r,tau,"count6","fpr_hotter_max_allowance"):.3f}/'
                             f'{100*mean(r,tau,"count6","fpr_hotter_rank05_allowance"):.3f}') if regime == "hotter" else "-"
                out.append(f'{r["scenario"]["name"]:12} {tau:.2f} {regime:6} '+" ".join(vals)+" "+allowance)
    out.extend(["\nPAIRED hotter FPR DELTA count6-fixed8, percentage points [MC95]",
                "scenario tau max delta [MC95] rank05 delta [MC95] mean max threshold delta(s_r)"])
    for r in payload["results"]:
        for tau in SCALES:
            d = r["paired_delta_vs_fixed8"][str(tau)]["count6"]
            out.append(f'{r["scenario"]["name"]:12} {tau:.2f} '+
                       pct_ci(d["fpr_hotter_max"]["pair_average"])+" "+
                       pct_ci(d["fpr_hotter_rank05"]["pair_average"])+
                       f' {d["threshold_max"]["pair_average"]["mean"]:.4f}')
    out.extend(["\nSELF-CHECKS: see checks in results JSON (exact counts, iid rank identities, review counterexample).",
                "All per-pair MC intervals, threshold means, iid references, state diagnostics and paired deltas: results JSON."])
    return "\n".join(out)+"\n"


def audit_results(results):
    checks = []
    for r in results:
        scenario = r["scenario"]
        if scenario["informative"] or scenario["one_window_lost"]:
            continue
        reference = exact_count_reference(scenario["exclusion"])
        for n in (6, 7, 8):
            p = reference["both_by_window"][str(n)]
            observed = r["both_by_window"][str(n)]["probability"]
            se = math.sqrt(p*(1-p)/r["replicates"])
            assert abs(observed-p) <= 6*se+1/r["replicates"], (scenario, n, observed, p)
        checks.append({"scenario": scenario["name"], "exact_count_reference": reference})
    # At tau=0, stopping/eligibility are independent of residuals, even in hot/lost scenarios.
    for r in results:
        for d in DESIGNS:
            metrics = r["metrics_given_both_success"]["0.0"][d]
            for cutoff in ("max", "rank05", "literal38"):
                obs = metrics[f"fpr_stable_{cutoff}"]["pair_average"]
                ref = metrics[f"iid_{cutoff}_fpr_reference"]["pair_average"]
                assert abs(obs["mean"]-ref["mean"]) < 6*(obs["mc_se"]+ref["mc_se"]), (r["scenario"], d, cutoff)
    checks.append({"tau0_iid_order_statistic_identities": "PASS: all scenarios/designs/cutoffs within 6 MC SE"})
    oracle = review_counterexample()
    assert math.isclose(oracle["count6"]["fpr_given_success"], .05316705, abs_tol=1e-8)
    assert math.isclose(oracle["fixed8"]["fpr_given_success"], .04306531, abs_tol=1e-8)
    checks.append({"exact_review_counterexample": oracle})
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=60000)
    parser.add_argument("--seed", type=int, default=20261108)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    if args.replicates < 10000:
        parser.error("use >=10000 independent tapes for the MC audit")
    start = time.monotonic()
    results = []
    for i, scenario in enumerate(SCENARIOS):
        results.append(simulate(scenario, args.replicates, args.seed + 1009*i))
        print(f'completed {scenario.name}: {args.replicates} tapes', flush=True)
    payload = {"schema": "b3-sim-sol2/v1", "synthetic_only": True,
               "created_utc": datetime.now(timezone.utc).isoformat(),
               "python": platform.python_version(), "seed": args.seed,
               "replicates": args.replicates, "elapsed_s": time.monotonic()-start,
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "base_commit": "50c99e4f83b9e4d1442745fbe4492e0a1cc6446c",
               "r12_source_commit": "c07b388e90d9f085e6428a1e0d96b0361ff417f0",
               "scales_sr": SCALES, "hot_probability": HOT_PROB,
               "future_extra_shift_sr": "0 (stable) or tau (hotter); independent new window",
               "transport_allowance_sr": "(1+4/sqrt(3))*tau; model-conditional bounded drift",
               "fpr_unit": "eligible future assigned episode, conditional on both-pair calibration success",
               "intervals": "95% MC: normal tape-level mean; Wilson count probability; pairs averaged inside tape",
               "checks": audit_results(results),
               "fit_slot_sensitivity_exact": {str(p): exact_count_reference(p, slots=5) for p in (.05,.1,.2)},
               "results": results}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/"results-sol2.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    summary = summarize(payload)
    (args.output/"output-sol2.txt").write_text(summary)
    print(summary, end="")
    print(f'PASS: analytic audits; elapsed={payload["elapsed_s"]:.2f}s', flush=True)


if __name__ == "__main__":
    main()
