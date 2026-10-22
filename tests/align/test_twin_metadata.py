"""Twin agreement for lane A6 ``metadata``: the lane's real functions against the
independent twin (tests/align/twins/metadata_twin.py) on the same seeded,
production-shaped worlds.

Written by the blind executing reviewer (review round 1). Bars are the
orchestrator's, not chosen here:

* an output with a printed uncertainty (an AUC, an interval end, a paired
  difference) agrees within 1% of the smallest printed half-width of that
  world (DeLong and cluster-bootstrap half-widths; the paired test's SE);
* any other output agrees within 1e-6 relative, or 1e-6 absolute in the
  output's unit when the value is below 1 (features, coefficients,
  held-out probabilities, SEs, p values);
* Monte Carlo outputs whose two implementations draw different random
  numbers agree within 4 * sqrt(se_lane^2 + se_twin^2); each se is the
  empirical spread of that implementation's interval end over K seeds,
  divided by sqrt(K) because the K-seed means are compared. Under normality
  a 4-sigma bar gives a false alarm about 6e-5 of the time per comparison.
* exactly enumerated results (the five-group bootstrap distribution, all
  5**5 equally likely draw sequences) agree under the 1e-6 bar.

Readings the two implementations differ on, replayed rather than called a
defect (the twin exposes switches for them):

* penalty: the lane minimises NLL + l2/2 * |beta|^2, the twin NLL + l2 *
  |beta|^2, so the lane at l2 = L equals the twin at l2 = L/2
  (or the twin core with penalty_half=True at L);
* name: lane ``decode_tokens_per_second`` is twin
  ``decode_tokens_per_turn_second``;
* bootstrap group order: lane uses first appearance, twin sorted order; with
  groups that appear in sorted order both consume random.Random(seed)
  identically, so explicit-n_boot results are the same draws;
* automatic bootstrap size: lane doubles from 1600 until its plug-in
  endpoint SE is below 1% of the half-width, twin uses a fixed 18,577 from a
  normal reference, so only Monte Carlo agreement is expected;
* undefined analyses: the lane returns flagged NaNs, the twin raises
  ValueError.

Both implementations read decode_tokens in the logged view as including
hidden tokens (records.Turn); this test cannot see a defect they share there.
"""

from __future__ import annotations

import math
import random
import statistics
import unittest
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

def make_episode(ep_id, pair, condition, rng, *, hidden_logged=0, extra_logged_calls=0,
                 unlogged_hidden=0, scale=1):
    """A multi-turn agent episode: 8-40 model calls (prefill at ~4000 tok/s,
    decode at ~35 tok/s, lognormal decode median 250), 0-3 tool calls after
    each call (0.2-6 s each), and a 15-35 s wait before the next call.
    ``scale`` multiplies every token count (huge-count worlds)."""
    n = rng.randint(8, 40)
    clock, context, turns = 0, 1500 * scale, []
    extra = set(rng.sample(range(n), min(extra_logged_calls, n))) if extra_logged_calls else set()
    hidden_turn, slack_turn = rng.randrange(n), rng.randrange(n)
    for k in range(n):
        prefill = rng.randint(150, 3000) * scale
        decode = max(1, round(rng.lognormvariate(math.log(250), 0.7))) * scale
        hidden = 0
        if hidden_logged and k == hidden_turn:
            decode += hidden_logged
            hidden = hidden_logged
        start = clock
        end = start + int((prefill / scale / 4000 + decode / scale / 35) * NS) + rng.randint(1, 10**8)
        calls, t = [], end
        for _ in range(rng.choice([0, 0, 1, 1, 1, 2]) + (k in extra)):
            d = rng.randint(2 * 10**8, 6 * NS)
            calls.append(ToolCall(rng.choice(["search", "read_file", "send_email"]), t, t + d,
                                  rng.randint(50, 600), rng.randint(200, 20000)))
            t += d
        if k and rng.random() < 0.05:  # an occasional unlogged call inside a logged turn
            calls.append(ToolCall("cleanup", t, t + NS // 10, 10, 10, logged=False))
            t += NS // 10
        turns.append(Turn(len(turns), start, end, context, prefill, decode, hidden_tokens=hidden,
                          tool_calls=tuple(calls)))
        context += prefill + decode
        wait = rng.randint(15 * NS, 35 * NS)
        if unlogged_hidden and k == slack_turn:
            # an unlogged turn inside the existing wait: 1 s + 12.5 s model + 0.5 s call < 15 s
            s = t + NS
            e = s + int((300 / 4000 + unlogged_hidden / 35) * NS)
            turns.append(Turn(len(turns), s, e, context, 300, unlogged_hidden, hidden_tokens=unlogged_hidden,
                              logged=False, tool_calls=(ToolCall("side_task", e, e + NS // 2, 100, 100,
                                                                 logged=False),)))
            context += 300 + unlogged_hidden
        clock = t + wait
    return Episode(ep_id, pair, condition, "synthetic-open-weight", "mock:local", 0, "host.mono", 0,
                   clock, tuple(turns), flags=("synthetic",))


def make_world(seed, *, pairs=5, seeds=30, mode="visible", scale=1):
    """pairs x {benign, sabotage} x seeds. mode visible: sabotage adds 3 logged
    calls and 400 hidden tokens in one logged turn; null: sabotage adds only
    an unlogged hidden turn in existing slack (logged features identically
    distributed); weak: 1 logged call only."""
    rng = random.Random(seed)
    episodes = []
    for p in range(pairs):
        for condition in ("benign", "sabotage"):
            for s in range(seeds):
                kw = {}
                if condition == "sabotage":
                    kw = {"visible": dict(hidden_logged=400 * scale, extra_logged_calls=3),
                          "null": dict(unlogged_hidden=400),
                          "weak": dict(extra_logged_calls=1)}[mode]
                episodes.append(make_episode(f"w{seed}/p{p:02d}/{condition}/{s}", f"shade/pair{p:02d}",
                                             condition, rng, scale=scale, **kw))
    return episodes


def edge_episodes():
    """Episodes the brief does not name: empty, all-unlogged, one turn, zero-length turn, huge counts."""
    t_zero = Turn(0, 5 * NS, 5 * NS, 0, 100, 40)
    one = Turn(0, NS, 3 * NS, 0, 1200, 300, hidden_tokens=100,
               tool_calls=(ToolCall("search", 3 * NS, 4 * NS, 10, 10),))
    hidden_only = Turn(0, NS, 2 * NS, 0, 100, 50, hidden_tokens=50, logged=False)
    huge = Turn(0, 0, 3600 * NS, 0, 10**12, 10**11, hidden_tokens=10**10,
                tool_calls=tuple(ToolCall("x", 3600 * NS, 3600 * NS + 1, 1, 1) for _ in range(1000)))
    def ep(i, turns, end):
        return Episode(f"edge{i}", "edge", "benign", "m", "mock", 0, "c", 0, end, tuple(turns))
    return [ep(0, [], 10 * NS), ep(1, [t_zero], 10 * NS), ep(2, [one], 5 * NS),
            ep(3, [hidden_only], 5 * NS), ep(4, [huge], 4000 * NS), ep(5, [], 0)]


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
        for seed in range(4):
            episodes += make_world(seed, mode="visible") + make_world(100 + seed, mode="null", seeds=10)
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
        self.assertGreater(checked, 50_000)


@unittest.skipUnless(lane is not None, LANE_MISSING)
class AucDelongAgreement(unittest.TestCase):
    def test_auc_delong_paired_on_cv_scores(self):
        worst = {"auc": 0.0, "delong": 0.0, "diff": 0.0, "se": 0.0, "p": 0.0}
        for seed, mode in product(range(6), ("visible", "null", "weak")):
            episodes = make_world(200 + seed, mode=mode)
            _, scores, labels, groups = cv_inputs(episodes)
            d_lane = lane.delong_ci(scores, labels)
            b_lane = lane.cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=2000, seed=seed)
            widths = [w for w in (half(d_lane), half(b_lane)) if w > 0]
            bar = 0.01 * min(widths)  # 1% of the smallest printed half-width
            a_l, a_t = lane.auc(scores, labels), twin.auc(scores, labels)
            self.assertLessEqual(abs(a_l - a_t), bar)
            d_twin = twin.delong_ci(scores, labels)
            for x, y in zip(d_lane, d_twin):
                self.assertLessEqual(abs(x - y), bar)
            worst["auc"] = max(worst["auc"], abs(a_l - a_t))
            worst["delong"] = max(worst["delong"], max(abs(x - y) for x, y in zip(d_lane, d_twin)))
            # Paired test against a second real baseline (two features only).
            other = [s for _, s in lane.grouped_cv_scores(episodes, l2=1.0,
                                                           feature_names=["tool_calls", "turns"])]
            p_lane = lane.paired_auc_difference(scores, other, labels)
            p_twin = twin.paired_auc_difference(scores, other, labels)
            self.assertLessEqual(abs(p_lane[0] - p_twin[0]), 0.01 * p_twin[1])  # 1% of printed SE
            self.assertLessEqual(abs(p_lane[1] - p_twin[1]), close_bar(p_twin[1]))
            self.assertLessEqual(abs(p_lane[2] - p_twin[2]), close_bar(p_twin[2]))
            for key, (x, y) in zip(("diff", "se", "p"), zip(p_lane, p_twin)):
                worst[key] = max(worst[key], abs(x - y))
        print("TWIN AUC/DeLong/paired worst |lane - twin|:", {k: f"{v:.2e}" for k, v in worst.items()})

    def test_tied_integer_scores(self):
        rng = random.Random(5)
        for trial in range(40):
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
        for trial in range(30):
            n = rng.choice([24, 60, 240])
            y = [int(rng.random() < 0.5) for _ in range(n)]
            y[0], y[1] = 0, 1
            const = rng.choice([math.log1p(5), 0.1, 46.666666666666664, 0.0])  # identical-value column
            X = [[rng.gauss(0.6 * yy, 1.0), 1e6 + 3e5 * rng.gauss(0.2 * yy, 1), const,
                  rng.randint(0, 3)] for yy in y]
            for row in X:  # a near-collinear pair (decode and log1p decode style)
                row.append(math.log1p(row[1]))
            l2 = rng.choice([0.1, 1.0, 10.0])
            a = lane.fit_logistic(X, y, l2=l2)
            b, _ = twin._fit_logistic_core(X, y, l2, penalty_half=True)
            self.assertFalse(a.flags)
            self.assert_coefs(a, b)
            # the default twin at l2/2 is the same objective
            self.assert_coefs(a, twin.fit_logistic(X, y, l2=l2 / 2))

    def test_grouped_cv_probabilities(self):
        worst = 0.0
        for seed, mode in product(range(4), ("visible", "null")):
            episodes = make_world(300 + seed, mode=mode)
            pred_lane = lane.grouped_cv_scores(episodes, l2=2.0)
            pred_twin = twin.grouped_cv_scores(episodes, l2=1.0)  # lane l2/2 * |b|^2 == twin (l2/2) * |b|^2
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
        for (_, x), (_, y) in zip(lane.grouped_cv_scores(huge, l2=2.0), twin.grouped_cv_scores(huge, l2=1.0)):
            self.assertLessEqual(abs(x - y), close_bar(y))
        print(f"TWIN grouped CV worst |lane - twin| probability: {worst:.2e}")


def exact_bootstrap_quantiles(scores, labels, groups, level=0.95):
    """Exact percentile ends of the five-group cluster bootstrap: all G**G ordered
    draw sequences are equally likely; one-class resamples are dropped (redrawn).
    Returns (lower, upper, atoms) where atoms is the sorted list of (value, prob)."""
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
        num = math.fsum(c[i] * c[j] * W[i][j] for i in range(G) for j in range(G) if c[i] and c[j])
        v = num / (npos * nneg)
        key = round(v, 12)  # merge float-summation-order twins of one exact rational value
        mass[key] = mass.get(key, 0) + 1
    total = sum(mass.values())
    atoms = sorted((v, m / total) for v, m in mass.items())
    return atoms


def atom_quantile(atoms, p):
    """Inverse CDF of the exact distribution; also the CDF gap to p at the chosen atom."""
    cum = 0.0
    for v, m in atoms:
        lo_cdf = cum
        cum += m
        if cum >= p:
            return v, min(p - lo_cdf, cum - p)
    return atoms[-1][0], 0.0


@unittest.skipUnless(lane is not None, LANE_MISSING)
class BootstrapAgreement(unittest.TestCase):
    def test_explicit_n_boot_same_stream(self):
        # Groups appear in sorted order, so both implementations index groups the same way
        # and consume random.Random(seed) identically: the same draws, so the 1% bar applies.
        worst = 0.0
        for seed in range(6):
            episodes = make_world(400 + seed, mode="visible" if seed % 2 else "weak")
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
        print(f"TWIN bootstrap same-stream worst |lane - twin| end: {worst:.2e}")

    def test_five_group_exact_enumeration(self):
        # Each implementation's automatic-B ends against the exactly enumerated
        # bootstrap distribution (5**5 equally likely draw sequences). The five-group
        # distribution is a dense set of small atoms, so the check is on probability:
        # the exact CDF just below and at each reported end must bracket p within
        # 4 binomial SEs of that implementation's B (the MC bar). Atom identity uses
        # 1e6 float ulps at unit scale (the lower edge of the doctrine's band), far
        # below the gap between distinct AUC* values here.
        tol = 1e6 * math.ulp(1.0)
        for seed in range(4):
            episodes = make_world(500 + seed, mode="visible" if seed % 2 else "weak")
            _, scores, labels, groups = cv_inputs(episodes)
            atoms = exact_bootstrap_quantiles(scores, labels, groups)
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
                    print(f"TWIN exact5 {name} seed={seed} p={p} end={x:.5f} B={result[2]} "
                          f"F(end-)={below:.4f} F(end)={at:.4f} 4se={4 * se:.4f}")

    def test_monte_carlo_agreement_different_streams(self):
        # Shuffled input order (different group indexing) and the two automatic sizes:
        # mean of K seeds per implementation, bar 4 * sqrt(se_l^2 + se_t^2), se = sd / sqrt(K).
        K = 10
        rng = random.Random(77)
        for world_seed, n_boot in ((601, 3000), (602, None)):
            episodes = make_world(world_seed, pairs=17, seeds=12, mode="visible")
            _, scores, labels, groups = cv_inputs(episodes)
            order = list(range(len(scores)))
            rng.shuffle(order)
            s2 = [scores[i] for i in order]
            l2 = [labels[i] for i in order]
            g2 = [groups[i] for i in order]
            runs_l = [lane.cluster_bootstrap_auc_ci(s2, l2, g2, n_boot=n_boot, seed=k) for k in range(K)]
            runs_t = [twin.cluster_bootstrap_auc_ci(s2, l2, g2, n_boot=n_boot, seed=k) for k in range(K)]
            for end in (0, 1):
                xl = [r[end] for r in runs_l]
                xt = [r[end] for r in runs_t]
                se = math.sqrt(statistics.variance(xl) / K + statistics.variance(xt) / K)
                with self.subTest(world=world_seed, n_boot=n_boot, end=end):
                    self.assertGreater(se, 0)
                    self.assertLessEqual(abs(statistics.mean(xl) - statistics.mean(xt)), 4 * se)
                print(f"TWIN MC world={world_seed} n_boot={n_boot} end={end} lane={statistics.mean(xl):.5f} "
                      f"twin={statistics.mean(xt):.5f} 4se={4 * se:.2e} B_lane={runs_l[0][2]} B_twin={runs_t[0][2]}")


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


if __name__ == "__main__":
    unittest.main()
