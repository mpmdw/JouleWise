"""Empirical calibration on the four null worlds required by fix-round review.

World sizes and bootstrap budgets are review fixtures, not inference thresholds.
The false-addition bar is alpha/2 plus two binomial standard errors at n worlds,
as set by the lead for the lower side of a conventional two-sided 95% interval.
No network or optional packages are used.
"""

from __future__ import annotations

import math
import random
import statistics
import unittest

from joulewise.align.records import Episode, RouterLog, ToolCall, Turn
from joulewise.align.moe.stage_a import analyze_stage_a
from joulewise.align.moe.synthetic import TopicWorld, topic_episodes


def topk_weighted(rng, weights, k):
    # Efraimidis-Spirakis weighted sampling without replacement.
    keys = [(rng.random() ** (1.0 / w), e) for e, w in enumerate(weights)]
    keys.sort(reverse=True)
    return tuple(e for _, e in keys[:k])


def make_world(*, seed, groups=17, per_condition=2, E=32, K=4, L=4, turns=(3, 6),
               prefill=(40, 120), first_prefill=200, decode=(10, 60), f=0.0, rho=0.3,
               count_ratio=1.0, zipf=0.8):
    """Reviewer's independent Zipf-affinity generator, ported without changes."""
    rng = random.Random(seed)
    episodes = []
    for g in range(groups):
        task_aff = []
        side_aff = []
        for l in range(L):
            perm = list(range(E)); rng.shuffle(perm)
            w = [0.0] * E
            for rank, e in enumerate(perm):
                w[e] = 1.0 / (rank + 1) ** zipf
            task_aff.append(w)
            perm2 = list(range(E)); rng.shuffle(perm2)
            w2 = [0.0] * E
            for rank, e in enumerate(perm2):
                w2[e] = 1.0 / (rank + 1) ** (zipf + 1.0)
            side_aff.append(w2)
        for cond in ("benign", "sabotage"):
            for rep in range(per_condition):
                n_turns = rng.randint(*turns)
                t_ns = 0; ctx = 0
                tlist, phases, rows = [], [], []
                prev = None
                for ti in range(n_turns):
                    p = first_prefill if ti == 0 else rng.randint(*prefill)
                    d = rng.randint(*decode)
                    if cond == "sabotage":
                        d = max(1, round(d * count_ratio))
                    start = t_ns
                    first = start + p * 400_000
                    end = first + d * 25_000_000
                    calls = ()
                    if ti + 1 < n_turns:
                        calls = (ToolCall("tool", end, end + 150_000_000, 100, 1500),)
                        end_turn = end + 150_000_000
                    else:
                        end_turn = end
                    tlist.append(Turn(ti, start, end_turn, ctx, p, d, first_token_ns=first, tool_calls=calls))
                    ctx += p + d
                    t_ns = end_turn
                    for ph, n in (("prefill", p), ("decode", d)):
                        for _ in range(n):
                            side = cond == "sabotage" and ph == "decode" and rng.random() < f
                            row = []
                            for l in range(L):
                                if prev is not None and rng.random() < rho:
                                    row.append(prev[l])
                                else:
                                    row.append(topk_weighted(rng, side_aff[l] if side else task_aff[l], K))
                            row = tuple(row)
                            rows.append(row); phases.append(ph); prev = row
                log = RouterLog("rev/zipf", E, K, tuple(range(L)), tuple(phases), tuple(rows))
                episodes.append(Episode(f"rev-{seed}-{g}-{cond}-{rep}", f"task{g}", cond, "rev-model",
                                        "synthetic", seed, "mono", 0, t_ns, tuple(tlist), router_log=log))
    return episodes


def calibration(generator, *, n_worlds: int, n_bootstrap: int, first_seed: int,
                confidence: float = 0.95) -> dict[str, float]:
    """Run real generation -> statistics -> tests -> classification -> refit CI."""
    gains, widths, auc_r, auc_m, auc_c = [], [], [], [], []
    lower = upper = fixed_lower = fixed_upper = covered = cells = raw_rej = raw_total = holm_any = 0
    for seed in range(n_worlds):
        result = analyze_stage_a(generator(first_seed + seed), n_bootstrap=n_bootstrap,
                                 confidence=confidence, seed=seed)
        lo, hi = result.auc_gain_interval
        flo, fhi = result.auc_gain_fixed_prediction_interval
        gains.append(result.auc_gain)
        # For comparison with r10's implied-SD column: 1.96 is Phi^-1(.975),
        # the normal quantile for the conventional two-sided 95% interval.
        widths.append((hi - lo) / (2 * statistics.NormalDist().inv_cdf((1 + confidence) / 2)))
        lower += lo > 0
        upper += hi < 0
        fixed_lower += flo > 0
        fixed_upper += fhi < 0
        auc_r.append(result.aucs["routing"])
        auc_m.append(result.aucs["metadata"])
        auc_c.append(result.aucs["combined"])
        holm_any += any(st.p_holm < 1 - confidence for st in result.statistics.values())
        for st in result.statistics.values():
            if math.isfinite(st.interval[0]):
                covered += st.interval[0] <= 0 <= st.interval[1]
                cells += 1
            raw_rej += st.p_value < 1 - confidence
            raw_total += 1
    tail = (1 - confidence) / 2
    return {
        "worlds": n_worlds, "gain_mean": statistics.mean(gains),
        "gain_sd": statistics.pstdev(gains), "mean_interval_implied_sd": statistics.mean(widths),
        "refit_lower_rate": lower / n_worlds, "refit_upper_rate": upper / n_worlds,
        "fixed_lower_rate": fixed_lower / n_worlds, "fixed_upper_rate": fixed_upper / n_worlds,
        "effect_coverage": covered / cells, "raw_p_rate": raw_rej / raw_total,
        "holm_any_rate": holm_any / n_worlds,
        "routing_auc_mean": statistics.mean(auc_r), "metadata_auc_mean": statistics.mean(auc_m),
        "combined_auc_mean": statistics.mean(auc_c),
        # Lead's rate bar: binomial SE across independent seeded worlds.
        "lower_rate_bar": tail + 2 * math.sqrt(tail * (1 - tail) / n_worlds),
    }


class GainCalibrationTests(unittest.TestCase):
    # The review uses 120 lane worlds and 150 reviewer worlds; 120 for all four
    # exceeds its >=100 requirement with a derived lower-side rate bar 0.0535.
    n_worlds = 120
    n_bootstrap = 200  # Same explicit empirical budget as r10/r4.

    def check_world(self, name, generator, first_seed):
        result = calibration(generator, n_worlds=self.n_worlds, n_bootstrap=self.n_bootstrap,
                             first_seed=first_seed)
        print("MOE_GAIN_CALIBRATION", name, result, flush=True)
        self.assertLessEqual(result["refit_lower_rate"], result["lower_rate_bar"])

    def test_lane_12_groups(self):
        self.check_world("lane12", lambda seed: topic_episodes(
            0.0, design=TopicWorld(turns=3, prefill_tokens=48, decode_tokens=64),
            seed=seed, independent_noise=True), 5000)

    def test_lane_17_groups_two_repeats(self):
        self.check_world("lane17", lambda seed: topic_episodes(
            0.0, design=TopicWorld(groups=17, repeats=2, turns=3, prefill_tokens=48, decode_tokens=64),
            seed=seed, independent_noise=True), 5000)

    def test_reviewer_null_a(self):
        self.check_world("reviewA", lambda seed: make_world(
            seed=seed, turns=(2, 4), prefill=(20, 60), first_prefill=80, decode=(10, 40),
            count_ratio=1.0), 1000)

    def test_reviewer_null_b_counts_only(self):
        self.check_world("reviewB", lambda seed: make_world(
            seed=seed, turns=(2, 4), prefill=(20, 60), first_prefill=80, decode=(10, 40),
            count_ratio=1.3), 1000)


if __name__ == "__main__":
    unittest.main()
