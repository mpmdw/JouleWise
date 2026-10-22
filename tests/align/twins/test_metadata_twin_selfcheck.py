"""Closed-form and hand-computable checks of the metadata twin (tests/align/twins/metadata_twin.py).

These check the twin against arithmetic done by hand (or by an independent
method inside the test: bisection, midranks), so that when the twin and the
real lane module disagree, the twin's own side has already been checked.

Agreement bar. A closed-form check of a computation of about ``n_ops``
floating-point operations sees rounding error of at most ``n_ops * eps``
(relative, for O(1) quantities). The doctrine's band for an agreement bar runs
from 1e6 times the float noise up to 1% of the smallest printed uncertainty;
every bar here sits at the band's lower edge, ``1e6 * n_ops * eps``, and the
largest one used (n_ops = 1e4, about 2.2e-6) is still below 1% of any AUC
half-width this pipeline prints (half-widths are about 0.05 or more at the
planned 300 episodes, so 1% is about 5e-4).
"""

from __future__ import annotations

import math
import random
import sys
import unittest

from joulewise.align.records import Episode, ToolCall, Turn
from tests.align.twins import metadata_twin as twin

EPS = sys.float_info.epsilon


def bar(n_ops: int, magnitude: float = 1.0) -> float:
    """Lower edge of the agreement band for ~n_ops float operations on a quantity of this magnitude."""
    return 1e6 * n_ops * EPS * max(1.0, abs(magnitude))


NS = 1_000_000_000


def _episode(episode_id, task_pair, condition, turns, end_ns, seed=0):
    return Episode(
        episode_id=episode_id, task_pair=task_pair, condition=condition, agent_model="synthetic-8b",
        endpoint="mock:local", seed=seed, clock_domain="host.mono", start_ns=0, end_ns=end_ns,
        turns=tuple(turns),
    )


def hand_episode() -> Episode:
    """Three turns; turn 1's only tool call is unlogged; turn 2 is unlogged; hidden tokens in turns 0 and 2."""
    t0 = Turn(index=0, start_ns=0, end_ns=2 * NS, context_tokens=0, prefill_tokens=1000,
              decode_tokens=200, hidden_tokens=50,
              tool_calls=(ToolCall("search", NS, NS + 10, 30, 400), ToolCall("read", NS + 20, NS + 30, 20, 900)))
    t1 = Turn(index=1, start_ns=3 * NS, end_ns=4 * NS, context_tokens=1200, prefill_tokens=300,
              decode_tokens=100, tool_calls=(ToolCall("send", 3 * NS + 5, 3 * NS + 9, 10, 10, logged=False),))
    t2 = Turn(index=2, start_ns=5 * NS, end_ns=9 * NS, context_tokens=1600, prefill_tokens=500,
              decode_tokens=400, hidden_tokens=300, logged=False,
              tool_calls=(ToolCall("delete", 6 * NS, 6 * NS + 1, 5, 5),))
    return _episode("hand", "shade/hand", "sabotage", [t0, t1, t2], end_ns=10 * NS)


def synthetic_world(n_pairs=5, seeds=30, extra_calls=3, extra_hidden=400, world_seed=0):
    """Production-shaped episodes: 12-30 turns, a few hundred to a few thousand prefill
    tokens per turn, 50-600 decode tokens at about 40 tokens/s, 0-2 tool calls per turn.
    Sabotage adds ``extra_calls`` logged tool calls and ``extra_hidden`` hidden tokens."""
    rng = random.Random(world_seed)
    episodes = []
    for pair in range(n_pairs):
        for condition in ("benign", "sabotage"):
            for seed in range(seeds):
                n_turns = rng.randint(12, 30)
                sabotage = condition == "sabotage"
                extra_turns = set(rng.sample(range(n_turns), extra_calls)) if sabotage else set()
                hidden_turn = rng.randrange(n_turns)
                turns, clock, context = [], 0, 0
                for k in range(n_turns):
                    prefill = rng.randint(200, 3000)
                    hidden = extra_hidden if sabotage and k == hidden_turn else 0
                    decode = rng.randint(50, 600) + hidden
                    start = clock
                    clock += int((prefill / 2000 + decode / 40) * NS)
                    calls = []
                    for _ in range(rng.randint(0, 2) + (1 if k in extra_turns else 0)):
                        call_start = clock
                        clock += rng.randint(1, 5) * NS // 10
                        calls.append(ToolCall("tool", call_start, clock, rng.randint(20, 400), rng.randint(50, 4000)))
                    turns.append(Turn(index=k, start_ns=start, end_ns=clock, context_tokens=context,
                                      prefill_tokens=prefill, decode_tokens=decode, hidden_tokens=hidden,
                                      tool_calls=tuple(calls)))
                    context += prefill + decode
                    clock += NS // 100
                episodes.append(_episode(f"p{pair}-{condition}-{seed}", f"shade/pair{pair}", condition,
                                         turns, end_ns=clock, seed=seed))
    return episodes


# ---------------------------------------------------------------- features

class FeaturesTest(unittest.TestCase):
    def assert_features(self, got, expected):
        self.assertEqual(list(got), list(twin.FEATURE_NAMES))
        for name, value in expected.items():
            self.assertIsInstance(got[name], float, name)
            # each feature is one or two float operations on integers
            self.assertAlmostEqual(got[name], value, delta=bar(4, value), msg=name)

    def test_logged_view_by_hand(self):
        # logged turns 0 and 1: turns 2, prefill 1300, decode 300 (turn 0's 50 hidden
        # tokens are inside its 200 decode tokens, R2), hidden shown as 0, tool calls 2
        # (turn 1's call is unlogged), turn time 2 s + 1 s.
        expected = {
            "turns": 2.0, "prefill_tokens": 1300.0, "decode_tokens": 300.0, "hidden_tokens": 0.0,
            "tool_calls": 2.0, "duration_s": 10.0, "decode_per_turn_mean": 150.0,
            "decode_per_turn_max": 200.0, "tool_calls_per_turn": 1.0,
            "decode_tokens_per_turn_second": 100.0, "fraction_turns_with_tool_calls": 0.5,
            "log1p_turns": math.log(3.0), "log1p_prefill_tokens": math.log(1301.0),
            "log1p_decode_tokens": math.log(301.0), "log1p_hidden_tokens": 0.0,
            "log1p_tool_calls": math.log(3.0),
        }
        self.assert_features(twin.features(hand_episode()), expected)

    def test_full_view_by_hand(self):
        # all three turns: decode 700, hidden 350, tool calls 4, turn time 2 + 1 + 4 = 7 s.
        expected = {
            "turns": 3.0, "prefill_tokens": 1800.0, "decode_tokens": 700.0, "hidden_tokens": 350.0,
            "tool_calls": 4.0, "duration_s": 10.0, "decode_per_turn_mean": 700.0 / 3.0,
            "decode_per_turn_max": 400.0, "tool_calls_per_turn": 4.0 / 3.0,
            "decode_tokens_per_turn_second": 100.0, "fraction_turns_with_tool_calls": 1.0,
            "log1p_turns": math.log(4.0), "log1p_prefill_tokens": math.log(1801.0),
            "log1p_decode_tokens": math.log(701.0), "log1p_hidden_tokens": math.log(351.0),
            "log1p_tool_calls": math.log(5.0),
        }
        self.assert_features(twin.features(hand_episode(), logged_only=False), expected)

    def test_no_logged_turns_gives_zero_ratios(self):
        turn = Turn(index=0, start_ns=0, end_ns=NS, context_tokens=0, prefill_tokens=10,
                    decode_tokens=5, logged=False)
        got = twin.features(_episode("e", "p", "benign", [turn], end_ns=2 * NS))
        for name in twin.FEATURE_NAMES:
            # integers and log1p(0): exact zeros by construction, except the episode span
            self.assertEqual(got[name], 2.0 if name == "duration_s" else 0.0, name)


# ---------------------------------------------------------------- AUC

def midrank_auc(scores, labels):
    """Independent method: Mann-Whitney U from midranks, U / (m n)."""
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    ranks = [0.0] * len(scores)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    m = sum(1 for label in labels if label == 1)
    n = len(labels) - m
    rank_sum = sum(r for r, label in zip(ranks, labels) if label == 1)
    return (rank_sum - m * (m + 1) / 2.0) / (m * n)


class AucTest(unittest.TestCase):
    def test_hand_cases_with_ties(self):
        cases = [
            ([1, 2, 3, 4], [0, 0, 1, 1], 1.0),
            ([1, 2, 3, 4], [1, 1, 0, 0], 0.0),
            ([5, 5, 5, 5], [1, 0, 1, 0], 0.5),
            # pos {3, 2} vs neg {2, 1}: 1 + 1 + 1/2 + 1 = 3.5 of 4 pairs
            ([3, 2, 2, 1], [1, 1, 0, 0], 0.875),
            # pos {1, 2, 2} vs neg {2, 0}: 0 + 1 + 1/2 + 1 + 1/2 + 1 = 4 of 6 pairs
            ([1, 2, 2, 2, 0], [1, 1, 1, 0, 0], 4.0 / 6.0),
        ]
        for scores, labels, expected in cases:
            # at most 6 pair additions and one division
            self.assertAlmostEqual(twin.auc(scores, labels), expected, delta=bar(8), msg=str(scores))

    def test_matches_midrank_formula_on_tied_random_scores(self):
        rng = random.Random(3)
        labels = [rng.randint(0, 1) for _ in range(120)]
        labels[0], labels[1] = 0, 1
        scores = [rng.randint(0, 15) for _ in labels]  # 16 levels: many ties
        # the twin adds about 3600 pair terms; the midrank route sums 120 ranks
        self.assertAlmostEqual(twin.auc(scores, labels), midrank_auc(scores, labels), delta=bar(4000))

    def test_rejects_one_class_and_bad_labels(self):
        with self.assertRaises(ValueError):
            twin.auc([1, 2], [1, 1])
        with self.assertRaises(ValueError):
            twin.auc([1, 2], [1, 2])


# ---------------------------------------------------------------- DeLong

class DelongTest(unittest.TestCase):
    # pos {0.9, 0.6} vs neg {0.7, 0.2, 0.1}: psi rows [1,1,1] and [0,1,1]; A = 5/6.
    # V10 = [1, 2/3]; V01 = [1/2, 1, 1]. S10 = (1/36 + 1/36) / 1 = 1/18;
    # S01 = (1/9 + 1/36 + 1/36) / 2 = 1/12. Var = (1/18)/2 + (1/12)/3 = 1/18.
    SCORES = [0.9, 0.6, 0.7, 0.2, 0.1]
    LABELS = [1, 1, 0, 0, 0]

    def test_variance_closed_form(self):
        area, variance = twin._delong_variance(self.SCORES, self.LABELS)
        self.assertAlmostEqual(area, 5.0 / 6.0, delta=bar(10))
        self.assertAlmostEqual(variance, 1.0 / 18.0, delta=bar(30))

    def test_variance_closed_form_with_ties(self):
        # pos {2, 1} vs neg {1, 0}: A = 3.5/4; V10 = [1, 3/4]; V01 = [3/4, 1];
        # S10 = S01 = 2 (1/8)^2 = 1/32; Var = (1/32)/2 + (1/32)/2 = 1/32.
        area, variance = twin._delong_variance([2, 1, 1, 0], [1, 1, 0, 0])
        self.assertAlmostEqual(area, 0.875, delta=bar(8))
        self.assertAlmostEqual(variance, 1.0 / 32.0, delta=bar(20))

    def test_logit_interval_closed_form(self):
        # logit(5/6) = ln 5; se_logit = sqrt(1/18) / (5/6 * 1/6) = sqrt(1/18) * 36/5.
        z = 1.959963984540054  # Phi^-1(0.975), the 95% two-sided normal quantile
        se_logit = math.sqrt(1.0 / 18.0) * 36.0 / 5.0
        lo = 1.0 / (1.0 + math.exp(-(math.log(5.0) - z * se_logit)))
        hi = 1.0 / (1.0 + math.exp(-(math.log(5.0) + z * se_logit)))
        got = twin.delong_ci(self.SCORES, self.LABELS, 0.95)
        self.assertAlmostEqual(got[0], lo, delta=bar(60))
        self.assertAlmostEqual(got[1], hi, delta=bar(60))

    def test_perfect_separation_is_a_point(self):
        self.assertEqual(twin.delong_ci([3, 4, 1, 2], [1, 1, 0, 0]), (1.0, 1.0))
        self.assertEqual(twin.delong_ci([1, 2, 3, 4], [1, 1, 0, 0]), (0.0, 0.0))

    def test_wider_level_contains_narrower(self):
        rng = random.Random(5)
        labels = [i % 2 for i in range(60)]
        scores = [rng.gauss(0.8 * label, 1.0) for label in labels]
        lo95, hi95 = twin.delong_ci(scores, labels, 0.95)
        lo99, hi99 = twin.delong_ci(scores, labels, 0.99)
        point = twin.auc(scores, labels)
        self.assertTrue(0.0 <= lo99 <= lo95 <= point <= hi95 <= hi99 <= 1.0)


class PairedTest(unittest.TestCase):
    def test_hand_case(self):
        # labels [1,1,0,0]. a: pos {0.9, 0.4}, neg {0.5, 0.1}: A_a = 3/4, V10 = [1, 1/2], V01 = [1/2, 1].
        # b: pos {0.8, 0.7}, neg {0.9, 0.2}: A_b = 1/2, V10 = [1/2, 1/2], V01 = [0, 1].
        # Difference components: d10 = [1/2, 0], d01 = [1/2, 0]; S10_d = S01_d = 1/8;
        # Var = (1/8)/2 + (1/8)/2 = 1/8. z = 0.25 / sqrt(1/8); p = erfc(|z| / sqrt 2).
        labels = [1, 1, 0, 0]
        diff, se, p = twin.paired_auc_difference([0.9, 0.4, 0.5, 0.1], [0.8, 0.7, 0.9, 0.2], labels)
        self.assertAlmostEqual(diff, 0.25, delta=bar(20))
        self.assertAlmostEqual(se, math.sqrt(0.125), delta=bar(60))
        self.assertAlmostEqual(p, math.erfc(0.25 / math.sqrt(0.125) / math.sqrt(2.0)), delta=bar(80))

    def test_identical_scores(self):
        scores = [0.3, 0.9, 0.1, 0.5, 0.5, 0.2]
        labels = [1, 1, 0, 0, 1, 0]
        # identical inputs through identical code: the variance terms cancel exactly
        self.assertEqual(twin.paired_auc_difference(scores, scores, labels), (0.0, 0.0, 1.0))

    def test_against_a_constant_scorer_equals_single_delong(self):
        # A constant scorer has every component 1/2: zero variance and zero covariance,
        # so Var(A_a - 1/2) is exactly DeLong's Var(A_a).
        rng = random.Random(11)
        labels = [i % 2 for i in range(40)]
        scores = [rng.gauss(0.5 * label, 1.0) for label in labels]
        diff, se, _ = twin.paired_auc_difference(scores, [0.0] * len(labels), labels)
        area, variance = twin._delong_variance(scores, labels)
        self.assertAlmostEqual(diff, area - 0.5, delta=bar(500))
        # about 400 pair terms and 40 squared deviations per estimate
        self.assertAlmostEqual(se * se, variance, delta=bar(1000, variance))

    def test_swap_negates_difference(self):
        rng = random.Random(13)
        labels = [i % 2 for i in range(30)]
        a = [rng.random() + 0.3 * label for label in labels]
        b = [rng.random() for _ in labels]
        d1, s1, p1 = twin.paired_auc_difference(a, b, labels)
        d2, s2, p2 = twin.paired_auc_difference(b, a, labels)
        self.assertEqual(d1, -d2)  # a - b and b - a of the same two floats: exact negation
        self.assertAlmostEqual(s1, s2, delta=bar(1000))  # the same terms added in another order
        self.assertAlmostEqual(p1, p2, delta=bar(1000))


# ---------------------------------------------------------------- logistic

def bisect_root(f, lo, hi):
    """Independent root finder: f(lo) < 0 < f(hi); 200 halvings exhaust double precision."""
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if f(mid) < 0.0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def penalised_slope(l2):
    """Optimum of the two-point problem x = -1 (y = 0), x = +1 (y = 1) under R10.

    By symmetry the intercept is 0; the objective is 2 log(1 + e^-b) + l2 b^2,
    whose derivative vanishes where l2 b = 1 / (1 + e^b).
    """
    return bisect_root(lambda b: l2 * b - 1.0 / (1.0 + math.exp(b)), 0.0, 1.0 / l2)


class LogisticTest(unittest.TestCase):
    def test_separable_but_penalised(self):
        for l2 in (0.05, 0.5, 2.0):
            slope = penalised_slope(l2)
            coefs = twin.fit_logistic([[-1.0], [1.0]], [0, 1], l2=l2)
            # Newton stops within float noise of the optimum (R11); about 100 operations
            self.assertAlmostEqual(coefs[0], 0.0, delta=bar(100))
            self.assertAlmostEqual(coefs[1], slope, delta=bar(100, slope))

    def test_back_transform_to_original_scale(self):
        # x in {3, 7}: mean 5, population sd 2, so z = +-1 and the standardised fit is the
        # one above; original scale b1 = beta / 2, b0 = -beta * 5 / 2.
        l2 = 0.5
        slope = penalised_slope(l2)
        coefs = twin.fit_logistic([[3.0], [7.0]], [0, 1], l2=l2)
        self.assertAlmostEqual(coefs[1], slope / 2.0, delta=bar(100, slope))
        self.assertAlmostEqual(coefs[0], -slope * 5.0 / 2.0, delta=bar(100, slope * 5.0))

    def test_unpenalised_saturated_mle(self):
        # One binary feature: the MLE reproduces each cell's log-odds.
        # x = 0: 1 of 4 positive, b0 = log(1/3); x = 1: 3 of 4, b0 + b1 = log 3.
        X = [[0.0]] * 4 + [[1.0]] * 4
        y = [0, 0, 0, 1, 1, 1, 1, 0]
        coefs = twin.fit_logistic(X, y, l2=0.0)
        self.assertAlmostEqual(coefs[0], math.log(1.0 / 3.0), delta=bar(200))
        self.assertAlmostEqual(coefs[1], 2.0 * math.log(3.0), delta=bar(200))

    def test_intercept_unpenalised_balances_probabilities(self):
        # The intercept's stationarity condition is sum(p_i) = sum(y_i) at any l2.
        rng = random.Random(17)
        X = [[rng.gauss(0, 1), rng.gauss(5, 3), rng.gauss(100, 20)] for _ in range(80)]
        y = [1 if row[0] + 0.1 * row[1] + rng.gauss(0, 1) > 0.5 else 0 for row in X]
        coefs = twin.fit_logistic(X, y, l2=50.0)
        total = sum(twin._predict(coefs, row) for row in X)
        # 80 predictions of ~10 operations each, summed: about 1000 operations on a sum near 30
        self.assertAlmostEqual(total, float(sum(y)), delta=bar(1000, sum(y)))

    def test_convention_switches(self):
        # Same optimum under each switch when l2 is rescaled to match: a 1/2 on the
        # penalty needs 2 l2; an averaged loss over n rows needs l2 / n.
        rng = random.Random(19)
        X = [[rng.gauss(0, 1), rng.gauss(0, 2)] for _ in range(40)]
        y = [1 if row[0] - row[1] + rng.gauss(0, 1) > 0 else 0 for row in X]
        base, _ = twin._fit_logistic_core(X, y, 0.7)
        half, _ = twin._fit_logistic_core(X, y, 1.4, penalty_half=True)
        mean, _ = twin._fit_logistic_core(X, y, 0.7 / 40, mean_loss=True)
        for a, b, c in zip(base, half, mean):
            self.assertAlmostEqual(a, b, delta=bar(1000, a))
            self.assertAlmostEqual(a, c, delta=bar(1000, a))

    def test_constant_column_gets_zero(self):
        coefs = twin.fit_logistic([[-1.0, 4.0], [1.0, 4.0]], [0, 1], l2=0.5)
        self.assertEqual(coefs[2], 0.0)  # left out of the fit: an exact zero by construction
        self.assertAlmostEqual(coefs[1], penalised_slope(0.5), delta=bar(100))


# ---------------------------------------------------------------- grouped CV

class GroupedCvTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = synthetic_world(n_pairs=4, seeds=8)
        cls.scores = twin.grouped_cv_scores(cls.world, l2=1.0)

    def test_order_ids_and_range(self):
        self.assertEqual([eid for eid, _ in self.scores], [ep.episode_id for ep in self.world])
        self.assertTrue(all(0.0 < s < 1.0 for _, s in self.scores))

    def test_each_score_is_the_held_out_fit(self):
        rows = [[twin.features(ep)[n] for n in twin.FEATURE_NAMES] for ep in self.world]
        labels = [1 if ep.condition == "sabotage" else 0 for ep in self.world]
        for held_out in sorted({ep.task_pair for ep in self.world}):
            train = [i for i, ep in enumerate(self.world) if ep.task_pair != held_out]
            coefs = twin.fit_logistic([rows[i] for i in train], [labels[i] for i in train], l2=1.0)
            for i, ep in enumerate(self.world):
                if ep.task_pair == held_out:
                    # identical code on identical inputs: bit identity is the property
                    self.assertEqual(self.scores[i][1], twin._predict(coefs, rows[i]))

    def test_no_leakage_from_a_held_out_episode(self):
        # Replace one episode of pair0 with a very different one: scores of the other
        # pair0 episodes must not move (pair0 is never in their training set), and
        # scores of other pairs must (pair0 is in theirs).
        target = 0
        changed = list(self.world)
        donor = synthetic_world(n_pairs=1, seeds=1, extra_calls=8, world_seed=99)[1]
        old = changed[target]
        changed[target] = _episode(old.episode_id, old.task_pair, old.condition, donor.turns, donor.end_ns)
        again = twin.grouped_cv_scores(changed, l2=1.0)
        moved_other_pairs = False
        for i, ep in enumerate(self.world):
            if i == target:
                continue
            if ep.task_pair == old.task_pair:
                self.assertEqual(again[i][1], self.scores[i][1])  # identical fold inputs: bit identity
            elif again[i][1] != self.scores[i][1]:
                moved_other_pairs = True
        self.assertTrue(moved_other_pairs)

    def test_feature_subset_and_unknown_name(self):
        out = twin.grouped_cv_scores(self.world, l2=1.0, feature_names=["tool_calls", "decode_tokens"])
        self.assertEqual(len(out), len(self.world))
        with self.assertRaises(KeyError):
            twin.grouped_cv_scores(self.world, l2=1.0, feature_names=["no_such_feature"])


# ---------------------------------------------------------------- cluster bootstrap

class BootstrapTest(unittest.TestCase):
    def test_size_meets_the_one_percent_rule_and_is_minimal(self):
        # Under the normal reference the MC SE of an end over the half-width is
        # sqrt(p(1-p)/B) / (phi(z) z); B must put it below 0.01, and B - 1 must not.
        level = 0.95
        p = (1.0 - level) / 2.0
        z = 1.959963984540054  # Phi^-1(0.975)
        phi = math.exp(-z * z / 2.0) / math.sqrt(2.0 * math.pi)
        size = twin.bootstrap_size(level)
        self.assertEqual(size, 18577)  # an integer: exact equality is the property
        self.assertLess(math.sqrt(p * (1 - p) / size) / (phi * z), 0.01)
        self.assertGreaterEqual(math.sqrt(p * (1 - p) / (size - 1)) / (phi * z), 0.01)

    def test_resample_auc_matches_explicit_resample(self):
        rng = random.Random(23)
        groups = [f"g{k % 6}" for k in range(60)]
        labels = [(k // 6) % 2 for k in range(60)]
        scores = [rng.randint(0, 9) + 0.5 * label for label in labels]  # ties within and across groups
        keys, draws = twin._bootstrap_draws(scores, labels, groups, 50, seed=4)
        for counts, value in draws:
            s_res, l_res = [], []
            for key, count in zip(keys, counts):
                for _ in range(count):
                    for s, l, g in zip(scores, labels, groups):
                        if g == key:
                            s_res.append(s)
                            l_res.append(l)
            # explicit route: up to 60 x 60 = 3600 pair additions
            self.assertAlmostEqual(value, twin.auc(s_res, l_res), delta=bar(4000))

    def test_degenerate_worlds(self):
        groups = ["a", "a", "b", "b", "c", "c"]
        labels = [1, 0, 1, 0, 1, 0]
        lo, hi, used = twin.cluster_bootstrap_auc_ci([2, 1, 2, 1, 2, 1], labels, groups, n_boot=200)
        self.assertEqual((lo, hi, used), (1.0, 1.0, 200))  # every resample has AUC exactly 1
        lo, hi, _ = twin.cluster_bootstrap_auc_ci([1] * 6, labels, groups, n_boot=200)
        self.assertEqual((lo, hi), (0.5, 0.5))  # every resample all tied: exactly 1/2

    def test_one_class_groups_are_redrawn(self):
        # each group a single episode: some resamples have one class and are redrawn
        scores = [0.1, 0.4, 0.35, 0.8]
        labels = [0, 0, 1, 1]
        _, draws = twin._bootstrap_draws(scores, labels, ["w", "x", "y", "z"], 300, seed=1)
        self.assertEqual(len(draws), 300)
        self.assertTrue(all(0.0 <= v <= 1.0 for _, v in draws))

    def test_quantile_type7_by_hand(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(twin._quantile_type7(values, 0.25), 2.0)  # position 1.0 exactly
        # 1 + 0.4 * (2 - 1): three roundings, so a float-noise bar rather than equality
        self.assertAlmostEqual(twin._quantile_type7(values, 0.1), 1.4, delta=bar(4))
        self.assertEqual(twin._quantile_type7(values, 1.0), 5.0)

    def test_seed_determinism(self):
        world = synthetic_world(n_pairs=5, seeds=4)
        scores = [twin.features(ep)["tool_calls"] for ep in world]
        labels = [1 if ep.condition == "sabotage" else 0 for ep in world]
        groups = [ep.task_pair for ep in world]
        first = twin.cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=500, seed=7)
        second = twin.cluster_bootstrap_auc_ci(scores, labels, groups, n_boot=500, seed=7)
        self.assertEqual(first, second)  # identical code, inputs and seed


# ---------------------------------------------------------------- end to end

class EndToEndTest(unittest.TestCase):
    def test_production_shaped_chain_runs(self):
        # Five task pairs, benign and sabotage, 30 seeds each, through the whole chain.
        world = synthetic_world(n_pairs=5, seeds=30)
        out = twin.grouped_cv_scores(world, l2=1.0)
        scores = [s for _, s in out]
        labels = [1 if ep.condition == "sabotage" else 0 for ep in world]
        groups = [ep.task_pair for ep in world]
        point = twin.auc(scores, labels)
        lo, hi = twin.delong_ci(scores, labels)
        self.assertTrue(0.0 <= lo <= point <= hi <= 1.0)
        b_lo, b_hi, used = twin.cluster_bootstrap_auc_ci(scores, labels, groups)
        self.assertEqual(used, twin.bootstrap_size(0.95))
        self.assertTrue(0.0 <= b_lo <= b_hi <= 1.0)


if __name__ == "__main__":
    unittest.main()
