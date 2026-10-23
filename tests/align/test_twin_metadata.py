"""Twin agreement for lane A6 ``metadata`` (review round 3): the lane's real
functions against the independent twin (tests/align/twins/metadata_twin.py) on
the same seeded, production-shaped worlds.

Round 3 (lane head ed1a3175c, whose executable code equals round 2's
f1af7ae9a; only comments and one test assertion changed) keeps every round-2
check and adds ``Round3WorldAgreement``: worlds from a third, independent
generator with a startup gap before the first turn (turn time differs from
episode span), unlogged side-task turns that hold logged=True tool calls (the
log still never shows them), zero-duration turns, crashed-run class imbalance
and 6-45-turn pairs; the features of those episodes are also checked against
values accumulated while the episode is built (not via ``totals()``).

Written by the blind executing reviewers of rounds 2 and 3. Lane and twin
both keep hidden tokens in logged decode, per the 2026-10-22 lead ruling;
they receive the same episodes, including the hidden annotations.

Bars are the orchestrator's, not chosen here:

* an output with a printed uncertainty (an AUC, an interval end, a paired
  difference) agrees within 1% of the smallest printed half-width of that
  world (the DeLong and cluster-bootstrap half-widths; the paired test's SE);
* any other output agrees within 1e-6 relative, or 1e-6 absolute in the
  output's unit when the value is below 1 (features, coefficients, held-out
  probabilities, SEs, p values from closed forms);
* Monte Carlo outputs whose two implementations draw different random numbers
  agree within 4 * sqrt(se_1^2 + se_2^2) (false alarm about 6e-5 per
  comparison under normality); for a permutation p from B shuffles,
  se = sqrt(p (1 - p) / B) / (1 + 1/B) about the exact p;
* exactly enumerated results (the five-group bootstrap distribution, every
  within-pair label arrangement of a small permutation world) are the
  reference that each Monte Carlo output is held to.

Readings the two implementations differ on, replayed rather than called a
defect:

* penalty: lane minimises NLL + l2/2 |beta|^2, twin NLL + l2 |beta|^2, so the
  lane at l2 = L equals the twin at l2 = L/2;
* name: lane ``decode_tokens_per_second`` is twin
  ``decode_tokens_per_turn_second``;
* bootstrap group order: lane uses first appearance, twin sorted order; with
  groups that appear in sorted order both consume random.Random(seed)
  identically;
* automatic bootstrap size: lane starts at the normal-reference B and doubles
  while its plug-in endpoint SE is above 1% of the half-width; twin uses the
  fixed normal-reference B, so only Monte Carlo agreement is expected;
* undefined analyses: lane returns flagged NaNs, twin raises ValueError;
* the lane's grouped_cv_permutation_test has no twin function; this file
  replays it with the twin's grouped CV and AUC and an independent shuffle.
"""

from __future__ import annotations

import math
import random
import statistics
import unittest
from dataclasses import replace
from itertools import product

from joulewise.align.records import Episode, ToolCall, Turn
from tests.align.twins import metadata_twin as twin

try:  # The lane modules exist only once the lane branch is merged with this one.
    from joulewise.align import metadata_baseline as lane
    from joulewise.align import stats as lane_stats
except ImportError:  # pragma: no cover - twin branch alone
    lane = lane_stats = None

LANE_MISSING = "joulewise.align.metadata_baseline (lane A6) is not on this branch"

NS = 10**9  # integer nanoseconds per SI second (records clock rule)
NAME_MAP = {"decode_tokens_per_second": "decode_tokens_per_turn_second"}
REL = 1e-6  # orchestrator bar where no uncertainty is printed


def close_bar(expected: float) -> float:
    """1e-6 relative, or 1e-6 absolute in the output's unit below 1 (orchestrator bar)."""
    return REL * max(1.0, abs(expected))


# ---------------------------------------------------------------- worlds

def _pair_params(rng):
    """Each task pair has its own operating point (heterogeneous pairs)."""
    return dict(turns_mu=rng.uniform(8, 30), decode_med=rng.uniform(120, 700),
                tool_rate=rng.uniform(0.3, 1.6), tok_s=rng.uniform(20, 70),
                think_frac=rng.uniform(0.2, 0.9), prefill_tok_s=rng.uniform(2000, 8000))


def make_episode(ep_id, pair, condition, rng, pp, *, extra_calls=0, extra_hidden=0,
                 unlogged_hidden=0, scale=1):
    """A thinking-model agent episode: 25%-SD turn count about the pair's mean,
    lognormal visible decode, a stripped <think> block in a fraction of turns
    (benign too), 0-2 logged tool calls of 0.1-8 s after each model call, a
    rare tamper-removed call, 10-40 s waits. ``scale`` multiplies token counts."""
    n = max(1, int(round(rng.gauss(pp["turns_mu"], pp["turns_mu"] * 0.25))))
    tok_s = pp["tok_s"] * rng.uniform(0.85, 1.15)
    clock = start = rng.randint(0, 10**6)
    context, turns = rng.randint(800, 3000), []
    extra = set(rng.sample(range(n), min(extra_calls, n))) if extra_calls else set()
    hid_turn, slack_turn = rng.randrange(n), rng.randrange(n)
    for k in range(n):
        prefill = rng.randint(100, 2500) * scale
        visible = max(1, int(rng.lognormvariate(math.log(pp["decode_med"]), 0.6))) * scale
        think = int(rng.lognormvariate(math.log(300), 0.8)) * scale if rng.random() < pp["think_frac"] else 0
        if extra_hidden and k == hid_turn:
            think += extra_hidden * scale
        decode = visible + think
        s = clock
        e = s + int((prefill / scale / pp["prefill_tok_s"] + decode / scale / tok_s) * NS) + rng.randint(1, 3 * 10**8)
        calls, t = [], e
        for _ in range(sum(rng.random() < pp["tool_rate"] / 2 for _ in range(2)) + (k in extra)):
            d = rng.randint(10**8, 8 * NS)
            calls.append(ToolCall(rng.choice(["search", "read_file", "send_email"]), t, t + d,
                                  rng.randint(20, 900), rng.randint(100, 50000)))
            t += d
        if rng.random() < 0.04:
            calls.append(ToolCall("cleanup", t, t + NS // 5, 10, 10, logged=False))
            t += NS // 5
        turns.append(Turn(len(turns), s, e, context, prefill, decode, hidden_tokens=think, tool_calls=tuple(calls)))
        context += prefill + decode
        wait = rng.randint(10 * NS, 40 * NS)
        if unlogged_hidden and k == slack_turn:  # side task in an unlogged turn inside existing slack
            us = t + NS
            ue = us + int((300 / pp["prefill_tok_s"] + unlogged_hidden / tok_s) * NS)
            wait = max(wait, ue - t + 3 * NS)
            turns.append(Turn(len(turns), us, ue, context, 300 * scale, unlogged_hidden * scale,
                              hidden_tokens=unlogged_hidden * scale, logged=False,
                              tool_calls=(ToolCall("side_task", ue, ue + NS // 2, 100, 100, logged=False),)))
            context += (300 + unlogged_hidden) * scale
        clock = t + wait
    return Episode(ep_id, pair, condition, "synthetic-thinking-model", "mock:vllm", 0, "host.mono", start, clock,
                   tuple(turns), flags=("synthetic",))


def make_world(seed, *, pairs=5, seeds=30, mode="visible", scale=1, imbalance=True):
    """pairs x {benign, sabotage}; up to a quarter of sabotage and a sixth of
    benign runs missing per pair when ``imbalance``. Modes: visible (1-3 logged
    calls and 400 hidden tokens in a logged turn), weak (one logged call half
    the time), null (no change), slack (unlogged 400-token turn in slack)."""
    rng = random.Random(seed)
    episodes = []
    for p in range(pairs):
        pp = _pair_params(rng)
        nb = seeds - (rng.randint(0, seeds // 6) if imbalance else 0)
        ns = seeds - (rng.randint(0, seeds // 4) if imbalance else 0)
        for condition, count in (("benign", nb), ("sabotage", ns)):
            for s in range(count):
                kw = {}
                if condition == "sabotage":
                    kw = {"visible": dict(extra_calls=rng.choice([1, 2, 3]), extra_hidden=400),
                          "weak": dict(extra_calls=int(rng.random() < 0.5)),
                          "null": {}, "slack": dict(unlogged_hidden=400)}[mode]
                episodes.append(make_episode(f"r2w{seed}/p{p:02d}/{condition}/{s}", f"shade/pair{p:02d}",
                                             condition, rng, pp, scale=scale, **kw))
    return episodes


def edge_episodes():
    """Episodes the brief does not name: empty, all-unlogged, all-hidden, one turn, zero-length turn, huge counts."""
    t_zero = Turn(0, 5 * NS, 5 * NS, 0, 100, 40)
    one = Turn(0, NS, 3 * NS, 0, 1200, 300, hidden_tokens=100, tool_calls=(ToolCall("search", 3 * NS, 4 * NS, 10, 10),))
    hidden_only = Turn(0, NS, 2 * NS, 0, 100, 50, hidden_tokens=50, logged=False)
    all_hidden = Turn(0, NS, 2 * NS, 0, 100, 50, hidden_tokens=50)
    huge = Turn(0, 0, 3600 * NS, 0, 10**12, 10**11, hidden_tokens=10**10,
                tool_calls=tuple(ToolCall("x", 3600 * NS, 3600 * NS + 1, 1, 1) for _ in range(1000)))

    def ep(i, turns, end):
        return Episode(f"edge{i}", "edge", "benign", "m", "mock", 0, "c", 0, end, tuple(turns))
    return [ep(0, [], 10 * NS), ep(1, [t_zero], 10 * NS), ep(2, [one], 5 * NS), ep(3, [hidden_only], 5 * NS),
            ep(4, [huge], 4000 * NS), ep(5, [], 0), ep(6, [all_hidden], 3 * NS)]


def cv_inputs(episodes, l2_lane=1.0):
    pred = lane.grouped_cv_scores(episodes, l2=l2_lane)
    scores = [s for _, s in pred]
    labels = [int(e.condition == "sabotage") for e in episodes]
    groups = [e.task_pair for e in episodes]
    return pred, scores, labels, groups


def half(interval):
    return (interval[1] - interval[0]) / 2


# ---------------------------------------------------------------- tests

@unittest.skipUnless(lane is not None, LANE_MISSING)
class FeatureAgreement(unittest.TestCase):
    def test_features_agree_on_worlds_and_edges(self):
        checked = 0
        episodes = edge_episodes()
        for seed in range(3):
            episodes += make_world(seed, mode="visible") + make_world(100 + seed, mode="slack", seeds=10)
        episodes += make_world(9, mode="visible", seeds=5, scale=10**6)  # 1e8-1e9-token episodes
        for episode in episodes:
            for logged_only in (True, False):
                a = lane.features(episode, logged_only=logged_only)
                b = twin.features(episode, logged_only=logged_only)
                self.assertEqual({NAME_MAP.get(k, k) for k in a}, set(b))
                for key, value in a.items():
                    expected = b[NAME_MAP.get(key, key)]
                    with self.subTest(episode=episode.episode_id, logged=logged_only, key=key):
                        self.assertLessEqual(abs(value - expected), close_bar(expected))
                    checked += 1
        self.assertGreater(checked, 30_000)


@unittest.skipUnless(lane is not None, LANE_MISSING)
class AucDelongAgreement(unittest.TestCase):
    def test_auc_delong_paired_on_cv_scores(self):
        worst = {"auc": 0.0, "delong": 0.0, "diff": 0.0, "se": 0.0, "p": 0.0}
        nondegenerate = 0
        for seed, mode in product(range(4), ("visible", "null", "weak")):
            episodes = make_world(200 + seed, mode=mode)
            _, scores, labels, groups = cv_inputs(episodes)
            d_lane = lane.delong_ci(scores, labels)
            b_lane = lane.cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=2000, seed=seed)
            widths = [w for w in (half(d_lane), half(b_lane)) if w > 0]
            a_l, a_t = lane.auc(scores, labels), twin.auc(scores, labels)
            d_twin = twin.delong_ci(scores, labels)
            if not widths:  # AUC 0 or 1: both must report the same point interval
                self.assertEqual(a_l, a_t)
                self.assertEqual(tuple(d_lane), tuple(d_twin))
                continue
            nondegenerate += 1
            bar = 0.01 * min(widths)  # 1% of the smallest printed half-width
            self.assertLessEqual(abs(a_l - a_t), bar)
            for x, y in zip(d_lane, d_twin):
                self.assertLessEqual(abs(x - y), bar)
            worst["auc"] = max(worst["auc"], abs(a_l - a_t))
            worst["delong"] = max(worst["delong"], max(abs(x - y) for x, y in zip(d_lane, d_twin)))
            other = [s for _, s in lane.grouped_cv_scores(episodes, l2=1.0, feature_names=["tool_calls", "turns"])]
            p_lane = lane.paired_auc_difference(scores, other, labels)
            p_twin = twin.paired_auc_difference(scores, other, labels)
            self.assertLessEqual(abs(p_lane[0] - p_twin[0]), 0.01 * p_twin[1])  # 1% of printed SE
            self.assertLessEqual(abs(p_lane[1] - p_twin[1]), close_bar(p_twin[1]))
            self.assertLessEqual(abs(p_lane[2] - p_twin[2]), close_bar(p_twin[2]))
            for key, (x, y) in zip(("diff", "se", "p"), zip(p_lane, p_twin)):
                worst[key] = max(worst[key], abs(x - y))
        self.assertGreaterEqual(nondegenerate, 8)  # the worlds must exercise the interval code
        print("TWIN2 AUC/DeLong/paired worst |lane - twin|:", {k: f"{v:.2e}" for k, v in worst.items()},
              f"nondegenerate_worlds={nondegenerate}")

    def test_tied_integer_scores(self):
        rng = random.Random(5)
        for _ in range(40):
            n = rng.randint(4, 400)
            labels = [rng.randint(0, 1) for _ in range(n)]
            labels[0], labels[1], labels[2], labels[3] = 0, 1, 0, 1
            scores = [rng.randint(0, rng.randint(1, 12)) for _ in range(n)]
            d_lane = lane.delong_ci(scores, labels)
            a_l, a_t = lane.auc(scores, labels), twin.auc(scores, labels)
            bar = 0.01 * half(d_lane) if half(d_lane) > 0 else close_bar(a_t)
            self.assertLessEqual(abs(a_l - a_t), bar)
            for x, y in zip(d_lane, twin.delong_ci(scores, labels)):
                self.assertLessEqual(abs(x - y), bar)


@unittest.skipUnless(lane is not None, LANE_MISSING)
class LogisticAgreement(unittest.TestCase):
    def assert_coefs(self, a, b):
        self.assertEqual(len(a), len(b))
        for x, y in zip(a, b):
            self.assertLessEqual(abs(x - y), close_bar(y), (list(a), list(b)))

    def test_fit_logistic_replays_penalty_convention(self):
        rng = random.Random(11)
        for _ in range(30):
            n = rng.choice([24, 60, 240])
            y = [int(rng.random() < 0.5) for _ in range(n)]
            y[0], y[1] = 0, 1
            const = rng.choice([math.log1p(5), 0.1, 0.9088184001853248, 231.92200537667162, 0.0])
            X = [[rng.gauss(0.6 * yy, 1.0), 1e6 + 3e5 * rng.gauss(0.2 * yy, 1), const, rng.randint(0, 3)] for yy in y]
            for row in X:  # a near-collinear pair (decode and log1p decode style)
                row.append(math.log1p(row[1]))
            l2 = rng.choice([0.1, 1.0, 10.0])
            a = lane.fit_logistic(X, y, l2=l2)
            b, _ = twin._fit_logistic_core(X, y, l2, penalty_half=True)
            self.assertFalse(a.flags)
            # Held-out probabilities (the printed quantity) at shifted rows, including a
            # different value of the constant column, agree under the 1e-6 bar.
            for row in X[:5]:
                shifted = [row[0] + 0.5, row[1] * 1.1, const * 1.01 + 1e-3, row[3], math.log1p(row[1] * 1.1)]
                pl = 1 / (1 + math.exp(-(a[0] + sum(c * v for c, v in zip(a[1:], shifted)))))
                self.assertLessEqual(abs(pl - twin._predict(b, shifted)), close_bar(pl))
            for k in (0, 1, 2, 4):  # coefficients of the well-conditioned columns
                self.assertLessEqual(abs(a[k] - b[k]), close_bar(b[k]), (k, list(a), list(b)))

    def test_grouped_cv_probabilities(self):
        worst = 0.0
        for seed, mode in product(range(3), ("visible", "null", "slack")):
            episodes = make_world(300 + seed, mode=mode)
            pred_lane = lane.grouped_cv_scores(episodes, l2=2.0)
            pred_twin = twin.grouped_cv_scores(episodes, l2=1.0)  # lane l2/2 |b|^2 == twin (l2/2) |b|^2
            self.assertEqual([k for k, _ in pred_lane], [k for k, _ in pred_twin])
            for (_, x), (_, y) in zip(pred_lane, pred_twin):
                self.assertLessEqual(abs(x - y), close_bar(y))
                worst = max(worst, abs(x - y))
            names = ["decode_tokens_per_second", "tool_calls", "duration_s"]
            sub_l = lane.grouped_cv_scores(episodes, l2=2.0, feature_names=names)
            sub_t = twin.grouped_cv_scores(episodes, l2=1.0, feature_names=[NAME_MAP.get(k, k) for k in names])
            for (_, x), (_, y) in zip(sub_l, sub_t):
                self.assertLessEqual(abs(x - y), close_bar(y))
        huge = make_world(9, mode="visible", seeds=10, scale=10**6)
        for (_, x), (_, y) in zip(lane.grouped_cv_scores(huge, l2=2.0),
                                  twin.grouped_cv_scores(huge, l2=1.0)):
            self.assertLessEqual(abs(x - y), close_bar(y))
        print(f"TWIN2 grouped CV worst |lane - twin| probability: {worst:.2e}")


def exact_bootstrap_atoms(scores, labels, groups):
    """Exact distribution of the G-group cluster bootstrap AUC: all G**G ordered
    draw sequences equally likely; one-class resamples dropped (redrawn)."""
    keys = sorted(set(groups))
    G = len(keys)
    pos = [[s for s, l, g in zip(scores, labels, groups) if g == k and l == 1] for k in keys]
    neg = [[s for s, l, g in zip(scores, labels, groups) if g == k and l == 0] for k in keys]
    W = [[sum((a > b) + 0.5 * (a == b) for a in pos[i] for b in neg[j]) for j in range(G)] for i in range(G)]
    mass = {}
    for seq in product(range(G), repeat=G):
        c = [0] * G
        for i in seq:
            c[i] += 1
        npos = sum(ci * len(p) for ci, p in zip(c, pos))
        nneg = sum(ci * len(q) for ci, q in zip(c, neg))
        if not npos or not nneg:
            continue
        v = math.fsum(c[i] * c[j] * W[i][j] for i in range(G) for j in range(G) if c[i] and c[j]) / (npos * nneg)
        key = round(v, 12)  # merge float-summation-order twins of one exact rational value
        mass[key] = mass.get(key, 0) + 1
    total = sum(mass.values())
    return sorted((v, m / total) for v, m in mass.items())


@unittest.skipUnless(lane is not None, LANE_MISSING)
class BootstrapAgreement(unittest.TestCase):
    def test_explicit_n_boot_same_stream(self):
        # Groups appear in sorted order, so both implementations index groups the same
        # way and consume random.Random(seed) identically: the same draws, 1% bar.
        worst = 0.0
        compared = 0
        for seed in range(6):
            episodes = make_world(400 + seed, mode="weak" if seed % 2 else "null")
            _, scores, labels, groups = cv_inputs(episodes)
            for n_boot in (1, 2, 999, 5000):
                a = lane.cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=n_boot, seed=seed)
                b = twin.cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=n_boot, seed=seed)
                self.assertEqual(a[2], b[2])
                hw = [w for w in (half(a), half(lane.delong_ci(scores, labels))) if w > 0]
                bar = 0.01 * min(hw)
                for x, y in zip(a[:2], b[:2]):
                    self.assertLessEqual(abs(x - y), bar)
                    worst = max(worst, abs(x - y))
                compared += 1
        self.assertEqual(compared, 24)
        print(f"TWIN2 bootstrap same-stream worst |lane - twin| end: {worst:.2e}")

    def test_five_group_exact_enumeration(self):
        # Each implementation's automatic-B ends against the exact 5**5 enumeration:
        # the exact CDF just below and at each reported end must bracket p within
        # 4 binomial SEs of that implementation's B (the MC bar). Atom identity uses
        # 1e6 float ulps at unit scale (the lower edge of the doctrine's band), far
        # below the gap between distinct AUC* values here (asserted).
        tol = 1e6 * math.ulp(1.0)
        checked = 0
        for seed in range(6):
            episodes = make_world(500 + seed, mode="weak" if seed % 2 else "null")
            _, scores, labels, groups = cv_inputs(episodes)
            atoms = exact_bootstrap_atoms(scores, labels, groups)
            values = [v for v, _ in atoms]
            gaps = [b - a for a, b in zip(values, values[1:])]
            self.assertGreater(min(gaps), 2 * tol)
            for name, impl in (("lane", lane), ("twin", twin)):
                result = impl.cluster_bootstrap_auc_ci(scores, labels, groups, seed=seed)
                for p, x in ((0.025, result[0]), (0.975, result[1])):
                    below = sum(m for v, m in atoms if v < x - tol)
                    at = sum(m for v, m in atoms if v <= x + tol)
                    se = math.sqrt(p * (1 - p) / result[2])
                    with self.subTest(impl=name, seed=seed, p=p):
                        self.assertLessEqual(below - 4 * se, p)
                        self.assertLessEqual(p, at + 4 * se)
                    checked += 1
                    print(f"TWIN2 exact5 {name} seed={seed} p={p} end={x:.5f} B={result[2]} "
                          f"F(end-)={below:.4f} F(end)={at:.4f} 4se={4 * se:.4f}")
        self.assertEqual(checked, 24)

    def test_monte_carlo_agreement_different_streams(self):
        # Shuffled input order (different group indexing) and the two automatic sizes:
        # mean of K seeds per implementation, bar 4 * sqrt(se_l^2 + se_t^2), se = sd / sqrt(K).
        K = 10
        rng = random.Random(77)
        for world_seed, n_boot in ((601, 3000), (602, None)):
            episodes = make_world(world_seed, pairs=17, seeds=12, mode="weak")
            _, scores, labels, groups = cv_inputs(episodes)
            order = list(range(len(scores)))
            rng.shuffle(order)
            s2, l2, g2 = [scores[i] for i in order], [labels[i] for i in order], [groups[i] for i in order]
            runs_l = [lane.cluster_bootstrap_auc_ci(s2, l2, g2, n_boot=n_boot, seed=k) for k in range(K)]
            runs_t = [twin.cluster_bootstrap_auc_ci(s2, l2, g2, n_boot=n_boot, seed=k) for k in range(K)]
            for end in (0, 1):
                xl = [r[end] for r in runs_l]
                xt = [r[end] for r in runs_t]
                se = math.sqrt(statistics.variance(xl) / K + statistics.variance(xt) / K)
                with self.subTest(world=world_seed, n_boot=n_boot, end=end):
                    self.assertGreater(se, 0)
                    self.assertLessEqual(abs(statistics.mean(xl) - statistics.mean(xt)), 4 * se)
                print(f"TWIN2 MC world={world_seed} n_boot={n_boot} end={end} lane={statistics.mean(xl):.5f} "
                      f"twin={statistics.mean(xt):.5f} 4se={4 * se:.2e} B_lane={runs_l[0][2]} B_twin={runs_t[0][2]}")


def twin_cv_auc(episodes, labels, l2_twin, feature_names):
    relabelled = [replace(e, condition="sabotage" if y else "benign") for e, y in zip(episodes, labels)]
    scores = [s for _, s in twin.grouped_cv_scores(relabelled, l2=l2_twin, feature_names=feature_names)]
    return twin.auc(scores, labels)


def small_permutation_world(seed):
    """Four task pairs, two benign and two sabotage each (6**4 = 1296 within-pair
    label arrangements, all enumerable); sabotage adds one logged tool call half the time."""
    rng = random.Random(seed)
    episodes = []
    for p in range(4):
        pp = _pair_params(rng)
        for condition in ("benign", "benign", "sabotage", "sabotage"):
            kw = {"extra_calls": int(rng.random() < 0.5)} if condition == "sabotage" else {}
            episodes.append(make_episode(f"perm{seed}/p{p}/{condition}/{len(episodes)}", f"pair{p}",
                                         condition, rng, pp, **kw))
    return episodes


@unittest.skipUnless(lane is not None, LANE_MISSING)
class PermutationAgreement(unittest.TestCase):
    FEATS = ["tool_calls", "turns"]

    def exact_p(self, episodes):
        """Every within-pair label arrangement, scored by the twin's CV and AUC."""
        labels = [int(e.condition == "sabotage") for e in episodes]
        observed = twin_cv_auc(episodes, labels, 0.5, self.FEATS)
        pairs = sorted({e.task_pair for e in episodes})
        idx = [[i for i, e in enumerate(episodes) if e.task_pair == p] for p in pairs]
        arrangements = []
        for rows in idx:
            k = sum(labels[i] for i in rows)
            opts = []
            for combo in product((0, 1), repeat=len(rows)):
                if sum(combo) == k:
                    opts.append(combo)
            arrangements.append(opts)
        extreme = total = 0
        for choice in product(*arrangements):
            lab = list(labels)
            for rows, combo in zip(idx, choice):
                for i, v in zip(rows, combo):
                    lab[i] = v
            a = twin_cv_auc(episodes, lab, 0.5, self.FEATS)
            # The lane's statistic |AUC - 0.5|, ties extreme; with 8 positives and 8
            # negatives AUCs are multiples of 1/128 (ties count 1/2), exact in binary64,
            # so this comparison of exact rationals is exact.
            extreme += abs(a - 0.5) >= abs(observed - 0.5)
            total += 1
        return observed, extreme / total, total

    def test_lane_permutation_p_against_exact_enumeration(self):
        for seed in (1, 2):
            episodes = small_permutation_world(seed)
            observed_t, p_exact, total = self.exact_p(episodes)
            B = 400  # compute budget; its MC SE enters the bar below
            obs_l, p_lane, used = lane.grouped_cv_permutation_test(
                episodes, l2=1.0, n_permutations=B, seed=seed, feature_names=self.FEATS)
            self.assertEqual(used, B)
            self.assertLessEqual(abs(obs_l - observed_t), close_bar(observed_t))
            # p_lane = (1 + k)/(B + 1), k ~ Bin(B, p_exact): mean (1 + B p)/(B + 1).
            mean = (1 + B * p_exact) / (B + 1)
            se = math.sqrt(B * p_exact * (1 - p_exact)) / (B + 1)
            print(f"TWIN2 permutation seed={seed} arrangements={total} observed={observed_t:.5f} "
                  f"p_exact={p_exact:.5f} p_lane={p_lane:.5f} expected={mean:.5f} 4se={4 * se:.4f}")
            self.assertLessEqual(abs(p_lane - mean), 4 * se)

    def test_lane_permutation_p_against_independent_replay(self):
        # Production-shaped world; independent shuffles (random.sample, other seed)
        # through the twin's CV. Both p values are MC estimates of the same exact p.
        episodes = make_world(700, pairs=5, seeds=12, mode="weak")
        labels = [int(e.condition == "sabotage") for e in episodes]
        feats = ["tool_calls", "tool_calls_per_turn", "turns"]
        B = 60  # compute budget for each implementation; MC SE enters the bar
        obs_l, p_lane, _ = lane.grouped_cv_permutation_test(episodes, l2=1.0, n_permutations=B, seed=3,
                                                            feature_names=feats)
        twin_feats = [NAME_MAP.get(f, f) for f in feats]
        observed = twin_cv_auc(episodes, labels, 0.5, twin_feats)
        self.assertLessEqual(abs(obs_l - observed), close_bar(observed))
        rng = random.Random(10**6 + 3)
        groups = sorted({e.task_pair for e in episodes})
        idx = [[i for i, e in enumerate(episodes) if e.task_pair == g] for g in groups]
        extreme = 0
        for _ in range(B):
            lab = list(labels)
            for rows in idx:
                vals = rng.sample([labels[i] for i in rows], len(rows))
                for i, v in zip(rows, vals):
                    lab[i] = v
            extreme += abs(twin_cv_auc(episodes, lab, 0.5, twin_feats) - 0.5) >= abs(observed - 0.5)
        p_twin = (1 + extreme) / (B + 1)
        p_mid = (p_lane + p_twin) / 2
        se = math.sqrt(2 * B * p_mid * (1 - p_mid)) / (B + 1)
        print(f"TWIN2 permutation replay observed={observed:.5f} p_lane={p_lane:.4f} p_twin={p_twin:.4f} 4se={4 * se:.4f}")
        self.assertLessEqual(abs(p_lane - p_twin), 4 * se)


@unittest.skipUnless(lane is not None, LANE_MISSING)
class UndefinedCasesAgree(unittest.TestCase):
    def test_lane_flags_where_twin_raises(self):
        cases = [([1.0, 2.0], [1, 1]), ([1.0, math.nan], [0, 1]), ([1.0, 2.0], [0, 2])]
        for scores, labels in cases:
            with self.assertRaises(ValueError):
                twin.auc(scores, labels)
            result = lane.auc(scores, labels)
            self.assertTrue(math.isnan(result) and result.flags)
        with self.assertRaises(ValueError):
            twin.delong_ci([0.1, 0.2, 0.3], [0, 1, 1])
        self.assertIn("insufficient_class_size", lane.delong_ci([0.1, 0.2, 0.3], [0, 1, 1]).flags)
        self.assertIs(lane_stats.auc, lane.auc)


# ---------------------------------------------------------------- round 3

def _r3_pair_params(rng):
    return dict(turns_mu=rng.uniform(6, 45), decode_med=rng.uniform(80, 900),
                tool_rate=rng.uniform(0.2, 2.5), tok_s=rng.uniform(15, 90),
                think_p=rng.uniform(0.1, 0.95), pf_tok_s=rng.uniform(1500, 9000))


def r3_episode(ep_id, pair, cond, rng, pp, *, extra_calls=0, extra_hidden=0, slack_hidden=0, scale=1):
    """One agent run plus the features accumulated while building it (logged and all views).

    The episode clock starts at a large monotonic offset and the first turn
    after a 2-90 s startup gap; 2% of turns have zero duration; 5% of turns
    carry a tamper-removed call; ``slack_hidden`` adds an unlogged turn holding
    one logged=True and one logged=False call inside existing slack."""
    n = max(1, int(round(rng.gauss(pp["turns_mu"], pp["turns_mu"] * 0.3))))
    tok_s = pp["tok_s"] * rng.uniform(0.8, 1.2)
    ep_start = rng.randint(10**14, 4 * 10**14)
    clock = ep_start + rng.randint(2 * NS, 90 * NS)
    ctx = rng.randint(500, 4000)
    turns = []
    acc = {v: dict(turns=0, prefill=0, decode=0, hidden=0, calls=0, tsec_ns=0, with_calls=0, dmax=0)
           for v in ("logged", "all")}
    extra_at = set(rng.sample(range(n), min(extra_calls, n))) if extra_calls else set()
    hid_at, slack_at = rng.randrange(n), rng.randrange(n)
    for k in range(n):
        prefill = rng.randint(50, 6000) * scale
        visible = max(0, int(rng.lognormvariate(math.log(pp["decode_med"]), 0.7))) * scale
        think = int(rng.lognormvariate(math.log(400), 0.9)) * scale if rng.random() < pp["think_p"] else 0
        if extra_hidden and k == hid_at:
            think += extra_hidden * scale
        decode = visible + think
        dur = 0 if rng.random() < 0.02 else (
            int((prefill / scale / pp["pf_tok_s"] + decode / scale / tok_s) * NS) + rng.randint(1, 2 * 10**8))
        s, e = clock, clock + dur
        t, calls, nlog, nall = e, [], 0, 0
        for _ in range(sum(rng.random() < pp["tool_rate"] / 3 for _ in range(3)) + (k in extra_at)):
            d = rng.randint(5 * 10**7, 12 * NS)
            calls.append(ToolCall(rng.choice(["search", "read_file", "send_email", "bank_api"]), t, t + d,
                                  rng.randint(10, 2000), rng.randint(50, 80000)))
            t += d
            nlog += 1
            nall += 1
        if rng.random() < 0.05:
            calls.append(ToolCall("cleanup", t, t + NS // 4, 5, 5, logged=False))
            t += NS // 4
            nall += 1
        turns.append(Turn(len(turns), s, e, ctx, prefill, decode, hidden_tokens=think,
                          first_token_ns=s + dur // 3, tool_calls=tuple(calls)))
        ctx += prefill + decode
        for v, ncalls, dec in (("logged", nlog, decode), ("all", nall, decode)):
            a = acc[v]
            a["turns"] += 1
            a["prefill"] += prefill
            a["decode"] += dec
            a["calls"] += ncalls
            a["tsec_ns"] += dur
            a["with_calls"] += ncalls > 0
            a["dmax"] = max(a["dmax"], dec)
        acc["all"]["hidden"] += think
        wait = rng.randint(8 * NS, 45 * NS)
        if slack_hidden and k == slack_at:
            us = t + NS
            ue = us + int((250 / pp["pf_tok_s"] + slack_hidden / tok_s) * NS)
            ucalls = (ToolCall("transfer", ue, ue + NS, 50, 50, logged=True),
                      ToolCall("delete_trace", ue + NS, ue + 2 * NS, 5, 5, logged=False))
            wait = max(wait, ue + 4 * NS - t)
            turns.append(Turn(len(turns), us, ue, ctx, 250 * scale, slack_hidden * scale,
                              hidden_tokens=slack_hidden * scale, tool_calls=ucalls, logged=False))
            ctx += (250 + slack_hidden) * scale
            a = acc["all"]
            a["turns"] += 1
            a["prefill"] += 250 * scale
            a["decode"] += slack_hidden * scale
            a["hidden"] += slack_hidden * scale
            a["calls"] += 2
            a["tsec_ns"] += ue - us
            a["with_calls"] += 1
            a["dmax"] = max(a["dmax"], slack_hidden * scale)
        clock = t + wait
    ep_end = clock + rng.randint(0, 5 * NS)
    episode = Episode(ep_id, pair, cond, "synthetic-thinking", "mock:vllm", rng.randint(0, 10**6), "host.mono",
                      ep_start, ep_end, tuple(turns), flags=("synthetic",))
    truth = {}
    for v, d in acc.items():
        m = d["turns"]
        f = {"turns": m, "prefill_tokens": d["prefill"], "decode_tokens": d["decode"],
             "hidden_tokens": d["hidden"] if v == "all" else 0, "tool_calls": d["calls"],
             "duration_s": (ep_end - ep_start) / NS,
             "decode_per_turn_mean": d["decode"] / m if m else 0.0, "decode_per_turn_max": d["dmax"],
             "tool_calls_per_turn": d["calls"] / m if m else 0.0,
             "decode_tokens_per_second": d["decode"] / (d["tsec_ns"] / NS) if d["tsec_ns"] else 0.0,
             "fraction_turns_with_tool_calls": d["with_calls"] / m if m else 0.0}
        for c in ("turns", "prefill_tokens", "decode_tokens", "hidden_tokens", "tool_calls"):
            f["log1p_" + c] = math.log1p(f[c])
        truth[v] = f
    return episode, truth


def r3_world(seed, *, pairs=5, seeds=30, mode="visible", scale=1):
    """pairs x {benign, sabotage}; up to a fifth of benign and a third of sabotage
    runs missing per pair. Modes: visible (2-4 logged calls + 400 hidden tokens in a
    logged turn), calls_only (3 logged calls), hidden_only (400 hidden tokens in a
    logged turn, physical timing), slack (unlogged side-task turn in slack), null."""
    rng = random.Random(seed)
    episodes, truths = [], []
    for p in range(pairs):
        pp = _r3_pair_params(rng)
        nb = seeds - rng.randint(0, seeds // 5)
        ns = seeds - rng.randint(0, seeds // 3)
        for cond, count in (("benign", nb), ("sabotage", ns)):
            for s in range(count):
                kw = {}
                if cond == "sabotage":
                    kw = {"visible": dict(extra_calls=rng.choice([2, 3, 4]), extra_hidden=400),
                          "calls_only": dict(extra_calls=3), "hidden_only": dict(extra_hidden=400),
                          "slack": dict(slack_hidden=400), "null": {}}[mode]
                ep, tr = r3_episode(f"r3w{seed}/p{p:02d}/{cond}/{s}", f"shade/pair{p:02d}", cond, rng, pp,
                                    scale=scale, **kw)
                episodes.append(ep)
                truths.append(tr)
    return episodes, truths


@unittest.skipUnless(lane is not None, LANE_MISSING)
class Round3WorldAgreement(unittest.TestCase):
    def test_features_construction_truth_and_twin(self):
        checked = 0
        for seed, mode, scale in ((1, "visible", 1), (2, "slack", 1), (3, "hidden_only", 1), (4, "null", 1),
                                  (5, "slack", 10**7)):
            episodes, truths = r3_world(seed, mode=mode, scale=scale)
            for episode, truth in zip(episodes, truths):
                for view, logged_only in (("logged", True), ("all", False)):
                    a = lane.features(episode, logged_only=logged_only)
                    b = twin.features(episode, logged_only=logged_only)
                    self.assertEqual(set(a), set(truth[view]))
                    for key, value in a.items():
                        exact = truth[view][key]
                        # No printed uncertainty: orchestrator's 1e-6 relative bar (absolute below 1).
                        self.assertLessEqual(abs(value - exact), close_bar(exact), (episode.episode_id, view, key))
                        tv = b[NAME_MAP.get(key, key)]
                        self.assertLessEqual(abs(value - tv), close_bar(tv), (episode.episode_id, view, key))
                        checked += 1
        self.assertGreater(checked, 40_000)
        print(f"TWIN3 features vs construction truth and twin: values={checked}")

    def test_grouped_cv_auc_delong_paired(self):
        worst = {"prob": 0.0, "auc": 0.0, "delong": 0.0, "diff": 0.0, "se": 0.0, "p": 0.0}
        for mode, seed in product(("visible", "calls_only", "hidden_only", "slack", "null"), (21, 22)):
            episodes, _ = r3_world(seed, mode=mode)
            pred_l = lane.grouped_cv_scores(episodes, l2=2.0)
            pred_t = twin.grouped_cv_scores(episodes, l2=1.0)  # lane l2/2 |b|^2 at 2 == twin l2 |b|^2 at 1
            self.assertEqual([k for k, _ in pred_l], [k for k, _ in pred_t])
            for (_, x), (_, y) in zip(pred_l, pred_t):
                self.assertLessEqual(abs(x - y), close_bar(y))  # probabilities: no printed uncertainty
                worst["prob"] = max(worst["prob"], abs(x - y))
            scores = [s for _, s in pred_l]
            labels = [int(e.condition == "sabotage") for e in episodes]
            groups = [e.task_pair for e in episodes]
            d_l = lane.delong_ci(scores, labels)
            b_l = lane.cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=2000, seed=seed)
            widths = [w for w in (half(d_l), half(b_l)) if w > 0]
            self.assertTrue(widths, mode)
            bar = 0.01 * min(widths)  # 1% of the smallest printed half-width of this world
            a_l, a_t = lane.auc(scores, labels), twin.auc(scores, labels)
            self.assertLessEqual(abs(a_l - a_t), bar)
            d_t = twin.delong_ci(scores, labels)
            for x, y in zip(d_l, d_t):
                self.assertLessEqual(abs(x - y), bar)
            worst["auc"] = max(worst["auc"], abs(a_l - a_t))
            worst["delong"] = max(worst["delong"], max(abs(x - y) for x, y in zip(d_l, d_t)))
            other = [s for _, s in lane.grouped_cv_scores(episodes, l2=2.0,
                                                          feature_names=["decode_tokens_per_second", "turns"])]
            p_l = lane.paired_auc_difference(scores, other, labels)
            p_t = twin.paired_auc_difference(scores, other, labels)
            self.assertLessEqual(abs(p_l[0] - p_t[0]), 0.01 * p_t[1])  # 1% of the printed SE
            self.assertLessEqual(abs(p_l[1] - p_t[1]), close_bar(p_t[1]))
            self.assertLessEqual(abs(p_l[2] - p_t[2]), close_bar(p_t[2]))
            for key, (x, y) in zip(("diff", "se", "p"), zip(p_l, p_t)):
                worst[key] = max(worst[key], abs(x - y))
            print(f"TWIN3 world mode={mode} seed={seed} n={len(episodes)} auc={a_l:.4f} "
                  f"delong={tuple(round(v, 4) for v in d_l)} paired={tuple(round(v, 4) for v in p_l)}")
        print("TWIN3 worst |lane - twin|:", {k: f"{v:.2e}" for k, v in worst.items()})

    def test_bootstrap_same_stream_and_automatic(self):
        # Groups appear in sorted order, so explicit n_boot consumes random.Random(seed)
        # identically in both: 1% of the smallest printed half-width. Automatic sizes
        # differ (lane doubles from the normal-reference B), so those ends are compared
        # as Monte Carlo estimates: mean of K seeds each, 4 * sqrt(se_l^2 + se_t^2).
        episodes, _ = r3_world(23, mode="calls_only")
        _, scores, labels, groups = cv_inputs(episodes, l2_lane=2.0)
        for n_boot in (1, 500, 4000):
            a = lane.cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=n_boot, seed=5)
            b = twin.cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=n_boot, seed=5)
            self.assertEqual(a[2], b[2])
            hw = [w for w in (half(a), half(lane.delong_ci(scores, labels))) if w > 0]
            for x, y in zip(a[:2], b[:2]):
                self.assertLessEqual(abs(x - y), 0.01 * min(hw))
        K = 8
        runs_l = [lane.cluster_bootstrap_auc_ci(scores, labels, groups, seed=k) for k in range(K)]
        runs_t = [twin.cluster_bootstrap_auc_ci(scores, labels, groups, seed=100 + k) for k in range(K)]
        for end in (0, 1):
            xl = [r[end] for r in runs_l]
            xt = [r[end] for r in runs_t]
            se = math.sqrt(statistics.variance(xl) / K + statistics.variance(xt) / K)
            if se == 0:
                # Five groups make the bootstrap distribution discrete (at most 126
                # compositions): at these B every seed of both lands on the same atom,
                # so the ends are deterministic and must coincide (1% of half-width).
                self.assertLessEqual(abs(xl[0] - xt[0]), 0.01 * half(runs_l[0]))
            else:
                self.assertLessEqual(abs(statistics.mean(xl) - statistics.mean(xt)), 4 * se)
            print(f"TWIN3 auto bootstrap end={end} lane={statistics.mean(xl):.5f} twin={statistics.mean(xt):.5f} "
                  f"4se={4 * se:.2e} B_lane={sorted({r[2] for r in runs_l})} B_twin={runs_t[0][2]}")


if __name__ == "__main__":
    unittest.main()
