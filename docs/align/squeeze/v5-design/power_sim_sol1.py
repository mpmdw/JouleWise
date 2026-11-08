#!/usr/bin/env python3
"""Independent revision-5/7 planning experiment; stdlib, synthetic data only.

Written from RULING-DRAFT.md before reading ruling_power_sim.py. No imports
from JouleWise or the author's simulation, no input files, no model/data access.
Run --self-test for bounded unittest checks, or --reps 3000 --null-reps 10000.
The grid MDE is the first *tested* effect with estimated Holm power >= .80;
it is neither a fitted detector model nor a guarantee between grid points.
Revision 7 adds optional window/H4 counts; the default power law, roster,
seeds and random-number order are unchanged. Honest gate: <=22/280.
"""

import argparse
import itertools
import math
import random
import time
import unittest
from dataclasses import dataclass


ALPHA = 0.05
OFFSETS = (0, 1, 2, 1, 2, 0)
SOLO = 0.95
JOINT = math.sqrt(SOLO)
PRIOR_N, PRIOR_MEAN, PRIOR_SECOND, CAP = 20, 0.05, 0.12, 0.5
LOSS = 0.1
# Rule positions: M, E, time+M, S, J_ME, J_SE.
CONTRASTS = ((4, 0), (4, 1), (4, 2), (5, 3))


def roster(windows=28, h4pw=8):
    """A literal, sealed, chronological 224/336 subset, cells supported."""
    rng = random.Random(734819)
    if windows < 1 or h4pw not in (8, 10):
        raise ValueError("Positive window count; H4 count must be 8 or 10")
    result = []
    for w in range(windows):
        rows = []
        for cell, offset in enumerate(OFFSETS):
            phase = (w + offset) % 3
            classes = ((0, 1), (0, 2), (1, 2))[phase]
            rows.extend((cell, cls != 0) for cls in classes)
        rng.shuffle(rows)
        if h4pw == 10:
            # Prospectively convert two cover assignments, rotating cells.
            # This is a synthetic reallocation, not an approved class roster.
            covers = [i for i, (_, subset) in enumerate(rows) if not subset]
            for i in (covers[w % 4], covers[(w + 1) % 4]):
                rows[i] = (rows[i][0], True)
        result.append(tuple(rows))
    return tuple(result)


ROSTER = roster()


def stake(total, second, n):
    # Both moments have the same denominator n+20, which cancels.
    return min(CAP, max(0.0, (PRIOR_N * PRIOR_MEAN + total)
                        / (PRIOR_N * PRIOR_SECOND + second)))


def terminal_p(values):
    total = second = 0.0
    capital = 1.0
    for n, value in enumerate(values):
        capital *= 1.0 + stake(total, second, n) * value
        total += value
        second += value * value
    return min(1.0, 1.0 / capital)


def holm(pvalues):
    rejected = [False] * 4
    for rank, h in enumerate(sorted(range(4), key=pvalues.__getitem__)):
        if pvalues[h] > ALPHA / (4 - rank):
            break
        rejected[h] = True
    return rejected


def wilson(hits, n):
    z = 1.959963984540054
    p = hits / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, center - half), min(1.0, center + half)


def interval(hits, n):
    lo, hi = wilson(hits, n)
    return f"{hits / n:.4f}[{lo:.4f},{hi:.4f}]"


@dataclass(frozen=True)
class Scenario:
    name: str
    rho: float
    regression: float = 0.02
    missing: float = 0.02
    calibration: str = "none"


SCENARIOS = (
    Scenario("coupled-rho0", 0.0),
    Scenario("coupled-rho05", 0.05),
    Scenario("coupled-rho15", 0.15),
    Scenario("coupled-stress", 0.30, 0.05, 0.05),
    Scenario("calibration-iid", 0.15, calibration="iid"),
    Scenario("calibration-date", 0.15, calibration="date"),
)


def window_rescue(rng, mean, rho, regression):
    """Bounded beta shock: exact rescue ICC rho, before missingness.

    Categories A and B each have probability p; C has .1p. All are
    mutually exclusive, leaving common regressions of probability r.
    H1/H2 rescues are necessarily disjoint: J_ME is a calibrated max.
    A Bernoulli rescue has Var(p_w)/(p*(1-p)) = rho, including H3/H4.
    """
    if rho == 0:
        return mean
    ceiling = (1 - regression) / (2 + LOSS)
    concentration = (ceiling - mean) / (rho * (1 - mean)) - 1
    if concentration <= 0:
        raise ValueError("Requested rescue ICC is infeasible at this effect")
    mu = mean / ceiling
    return ceiling * rng.betavariate(mu * concentration,
                                    (1 - mu) * concentration)


def rules(channels):
    m, e, t, s = channels
    return (m, e, max(t, m), s, max(m, e), max(s, e))


def honest_channels(rng, common):
    # Contemporaneous score dependence, including shared maxima.
    shared = rng.random()
    return tuple(shared if rng.random() < common else rng.random()
                 for _ in range(4))


def calibration_and_honest(rng, kind):
    """Same C for all rules; 49/pair, k=48; 140 honest tests/pair.

    iid: C rows independent, channels independent, but max rules share
    channels. date: seven date-constant groups of seven calibrators,
    and five date-constant honest members/pair/window (28 windows).
    These are transparent sensitivities, not measured correlation laws.
    """
    thresholds = []
    counts = [0] * 6
    for _pair in range(2):
        columns = [[] for _ in range(6)]
        for _date in range(7):
            date_value = honest_channels(rng, 0.0)
            for _member in range(7):
                channels = date_value if kind == "date" else honest_channels(rng, 0.0)
                for column, score in zip(columns, rules(channels)):
                    column.append(score)
        cutoff = tuple(sorted(column)[47] for column in columns)
        thresholds.append(cutoff)
        for _window in range(28):
            date_value = honest_channels(rng, 0.0)
            for _member in range(5):
                channels = date_value if kind == "date" else honest_channels(rng, 0.0)
                for h, score in enumerate(rules(channels)):
                    counts[h] += score > cutoff[h]
    # Availability is fixed at 100%: even this favorable case can lose gates.
    return thresholds, all(count <= 22 for count in counts), counts


def attack(rng, p, regression, nominal_effect, thresholds, pair, missing):
    """Shared side success and four raw channel scores for one attempt.

    A: E high/M low; B: M high/E low; C: E high/M medium.
    A occasionally loses H3/H4 rescues to T/S; C restores their means.
    All four pre-missing nominal means are exactly nominal_effect.
    Regression: M/E/S medium, T high => all contrasts -1.
    No rule is simulated as an independent ternary stream.
    """
    u = rng.random()
    if u < p:
        # Integer bands: 0=below solo, 1=solo only, 2=above joint.
        bands = (0, 2, 2 if rng.random() < LOSS else 0,
                 2 if rng.random() < LOSS else 0)
        alarm = (0, 1, int(bands[2] == 2), int(bands[3] == 2), 1, 1)
        success = True
    elif u < 2 * p:
        bands = (2, 0, 0, 0)
        alarm = (1, 0, 1, 0, 1, 0)
        success = True
    elif u < (2 + LOSS) * p:
        bands = (1, 2, 0, 0)
        alarm = (1, 1, 0, 0, 1, 1)
        success = True
    elif u < (2 + LOSS) * p + regression:
        bands = (1, 1, 2, 1)
        alarm = (1, 1, 1, 1, 0, 0)
        success = True
    else:
        bands = (0, 0, 0, 0)
        alarm = (0,) * 6
        # Ensures marginal side success .60 at every tested nominal effect.
        occupied_mean = (2 + LOSS) * (nominal_effect + regression) + regression
        residual_success = (0.60 - occupied_mean) / (1 - occupied_mean)
        if not 0 <= residual_success <= 1:
            raise ValueError("Effect incompatible with synthetic side success .60")
        success = rng.random() < residual_success
    unknown = rng.random() < missing
    if thresholds is not None:
        bounds = ((0.0, SOLO), (SOLO, JOINT), (JOINT, 1.0))
        channels = tuple(rng.uniform(*bounds[band]) for band in bands)
        alarm = tuple(int(score > threshold) for score, threshold
                      in zip(rules(channels), thresholds[pair]))
    differences = tuple(alarm[a] - alarm[b] for a, b in CONTRASTS)
    # Unknown side: min over success=0/1; negatives preserved coherently.
    observed = tuple(min(0, d) if unknown else int(success) * d
                     for d in differences)
    return observed, int(success and not unknown)


def replicate(rng, effect, scenario, attack_roster=ROSTER):
    if scenario.calibration != "none" and attack_roster != ROSTER:
        raise ValueError("Calibration sensitivity uses the original 280-honest roster")
    thresholds = None
    honest_gate = True
    if scenario.calibration != "none":
        thresholds, honest_gate, _ = calibration_and_honest(rng, scenario.calibration)
    total = [0.0] * 4
    second = [0.0] * 4
    capital = [1.0] * 4
    n = [0] * 4
    successes = [0, 0]
    pair_successes = [[0, 0], [0, 0]]
    pair_counts = [[0, 0], [0, 0]]
    for window in attack_roster:
        p = window_rescue(rng, effect + scenario.regression,
                          scenario.rho, scenario.regression)
        for cell, subset in window:
            pair = cell // 3
            values, success = attack(rng, p, scenario.regression, effect,
                                     thresholds, pair, scenario.missing)
            successes[0] += success
            successes[1] += subset * success
            pair_successes[0][pair] += success
            pair_successes[1][pair] += subset * success
            pair_counts[0][pair] += 1
            pair_counts[1][pair] += subset
            for h in range(4 if subset else 3):
                value = values[h]
                capital[h] *= 1 + stake(total[h], second[h], n[h]) * value
                total[h] += value
                second[h] += value * value
                n[h] += 1
    pvalues = tuple(min(1.0, 1 / c) for c in capital)
    rejection = holm(pvalues)
    capability = all(successes[group] >= 0.30 * sum(pair_counts[group])
                     and all(pair_successes[group][pair] >= 0.20 * pair_counts[group][pair]
                             for pair in range(2)) for group in range(2))
    strong = all(rejection[:3]) and honest_gate and capability
    return rejection, strong, strong and rejection[3], honest_gate, total


def power_row(seed, reps, effect, scenario, attack_roster=ROSTER):
    rng = random.Random(seed)
    hits = [0] * 8
    means = [0.0] * 4
    totals = [sum(len(w) for w in attack_roster)] * 3 + [
        sum(s for w in attack_roster for _, s in w)]
    for _ in range(reps):
        rejected, strong, beyond, honest, total = replicate(
            rng, effect, scenario, attack_roster)
        values = (*rejected, all(rejected[:3]), strong, beyond, honest)
        for h, value in enumerate(values):
            hits[h] += value
        for h in range(4):
            means[h] += total[h] / totals[h]
    return hits, [value / reps for value in means]


def null_replicate(rng, law):
    """Conditional-null laws, shared attempts/variance and fresh signs.

    Window variance may be revealed by earlier attempts. Each law retains
    E[delta_i | all earlier attempts] <= 0, even with that information.
    No positive random-mean shock is mislabelled as a conditional null.
    """
    streams = [[] for _ in range(4)]
    for w, window in enumerate(ROSTER):
        activation = rng.uniform(0.01, 0.45)
        for _, subset in window:
            common = rng.random()
            for h in range(4 if subset else 3):
                u = common if rng.random() < 0.7 else rng.random()
                if law == "window-variance":
                    value = 1 if u < activation / 2 else (-1 if u < activation else 0)
                elif law == "rare-regression":
                    value = -1 if u < 0.018 else (0.02 if u < 0.918 else 0)
                elif law == "drift":
                    prob = 0.02 + 0.40 * w / 27
                    value = 1 if u < prob / 2 else (-1 if u < prob else 0)
                elif law == "adaptive":
                    prob = 0.40 if streams[h] and streams[h][-1] > 0 else 0.04
                    value = 1 if u < prob / 2 else (-1 if u < prob else 0)
                else:
                    raise ValueError(law)
                streams[h].append(min(0, value) if rng.random() < 0.02 else value)
    return tuple(terminal_p(stream) for stream in streams)


def honest_upper(alarms, n, alpha=0.05):
    """One explicit valid alternative, NOT attributed to the draft.

    Hoeffding mixture for A_n=sum E[R_i|past], S_n=sum R_i:
      sum w_j exp(eta_j*(A_n-S_n) - n*eta_j**2/8).
    It is a nonnegative supermartingale at the true predictable A_n.
    Ville + monotone inversion gives a CS for A_n/n without a constant
    per-attempt conditional rate. Fixed eta and equal weights sum to 1.
    """
    etas = (0.125, 0.25, 0.5, 1.0)

    def wealth(q):
        return sum(math.exp(eta * (n * q - alarms) - n * eta * eta / 8)
                   for eta in etas) / len(etas)

    if wealth(1.0) < 1 / alpha:
        return 1.0
    lo, hi = alarms / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if wealth(mid) < 1 / alpha:
            lo = mid
        else:
            hi = mid
    return hi


class Checks(unittest.TestCase):
    def test_roster(self):
        self.assertEqual(sum(len(w) for w in ROSTER), 336)
        self.assertEqual(sum(s for w in ROSTER for _, s in w), 224)
        totals = [sum(s for w in ROSTER for c, s in w if c == cell)
                  for cell in range(6)]
        self.assertEqual(totals, [37, 37, 38, 37, 38, 37])
        for window in ROSTER:
            self.assertEqual(sum(s for _, s in window), 8)
            self.assertEqual({c for c, s in window if s}, set(range(6)))

    def test_sizing_rosters(self):
        for windows in (28, 36, 44, 52, 60):
            for h4pw in (8, 10):
                assignment = roster(windows, h4pw)
                self.assertEqual(sum(map(len, assignment)), 12 * windows)
                self.assertEqual(sum(s for w in assignment for _, s in w), h4pw * windows)
                for window in assignment:
                    self.assertEqual(sum(s for _, s in window), h4pw)
                    self.assertEqual({c for c, s in window if s}, set(range(6)))

    def test_stakes_and_null_expectation(self):
        self.assertAlmostEqual(stake(0, 0, 0), 5 / 12)
        self.assertEqual(stake(100, 100, 100), 0.5)
        self.assertEqual(stake(-2, 2, 2), 0)
        # Exact enumeration, not a Monte Carlo assertion: E[K_7]=1.
        expected = 0.0
        for values in itertools.product((-1, 0, 1), repeat=7):
            probability = math.prod(0.8 if x == 0 else 0.1 for x in values)
            total = second = 0
            capital = 1.0
            for n, value in enumerate(values):
                lam = stake(total, second, n)
                self.assertGreaterEqual(lam, 0)
                self.assertLessEqual(lam, 0.5)
                capital *= 1 + lam * value
                self.assertGreater(capital, 0)
                total += value
                second += value * value
            expected += probability * capital
        self.assertAlmostEqual(expected, 1.0, places=12)

    def test_exact_holm_and_degenerate(self):
        self.assertEqual(holm([0.0125, 0.05 / 3, 0.025, 0.05]), [True] * 4)
        self.assertEqual(holm([0.01250001] * 4), [False] * 4)
        self.assertEqual(holm([0.01, 0.01666, 0.025, 1]), [True, True, True, False])
        self.assertEqual(terminal_p([0] * 224), 1)
        self.assertAlmostEqual(terminal_p([1, 1]), 8 / 17)
        # A losing suffix must be charged: terminal capital, not its maximum.
        self.assertGreater(terminal_p([1] * 20 + [-1] * 10),
                           terminal_p([1] * 20))

    def test_pathwise_adverse_bound_and_shared_rules(self):
        for alarms in itertools.product((0, 1), repeat=4):
            m, e, t, s = alarms
            # At a common threshold, all joint rules are literal maxima.
            actual = rules(alarms)
            for a, b in CONTRASTS:
                d = actual[a] - actual[b]
                for success in (0, 1):
                    self.assertLessEqual(min(0, d), success * d)
            self.assertLessEqual(actual[4], m or e)

    def test_mean_and_icc_and_calibration_order(self):
        rng = random.Random(123)
        ps = [window_rescue(rng, 0.12, 0.15, 0.02) for _ in range(30000)]
        mean = sum(ps) / len(ps)
        var = sum((p - mean) ** 2 for p in ps) / len(ps)
        self.assertAlmostEqual(mean, 0.12, delta=0.003)
        self.assertAlmostEqual(var / (0.12 * 0.88), 0.15, delta=0.008)
        totals = [0] * 4
        for _ in range(30000):
            values, _ = attack(rng, 0.12, 0.02, 0.10, None, 0, 0)
            for h, value in enumerate(values):
                totals[h] += value
        for total in totals:
            self.assertAlmostEqual(total / 30000, 0.10, delta=0.008)
        cutoffs, _, _ = calibration_and_honest(rng, "iid")
        for cutoff in cutoffs:
            self.assertGreaterEqual(cutoff[4], max(cutoff[0], cutoff[1]))
            self.assertGreaterEqual(cutoff[2], cutoff[0])
            self.assertGreaterEqual(cutoff[5], max(cutoff[1], cutoff[3]))

    def test_honest_cs_target(self):
        self.assertGreater(honest_upper(14, 280), 0.05)
        self.assertLess(honest_upper(0, 280), honest_upper(14, 280))
        # Nonconstant conditional means: .01 for 140 then .09 for 140.
        # The explicit mixture's expectation at true A is <=1 exactly.
        for eta in (0.125, 0.25, 0.5, 1.0):
            expected_log = sum(eta * p - eta * eta / 8
                               + math.log1p(p * math.expm1(-eta))
                               for p in [0.01] * 140 + [0.09] * 140)
            self.assertLessEqual(expected_log, 1e-12)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--reps", type=int, default=3000)
    parser.add_argument("--null-reps", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=850137)
    parser.add_argument("--scenarios", nargs="+", choices=[s.name for s in SCENARIOS])
    parser.add_argument("--effects", nargs="+", type=float,
                        default=[0.04, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.14, 0.16])
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=[__file__], verbosity=2)
        return
    if args.reps <= 0 or args.null_reps < 0:
        parser.error("replication counts must be positive (null-reps may be zero)")
    start = time.monotonic()
    print(f"seed={args.seed} reps={args.reps} null_reps={args.null_reps}", flush=True)
    print("Counts H1-H3=336 H4=224; 28x12 with literal phased H4 subset.")
    print("All intervals: pointwise 95% Wilson MC; MDE: first tested grid power>=.8.")
    print("Power columns H1 H2 H3 H4 H123 strong beyond honest_gate; adverse mean.")
    for index, scenario in enumerate(SCENARIOS):
        if args.scenarios and scenario.name not in args.scenarios:
            continue
        mdes = [None] * 7
        print(f"SCENARIO {scenario}", flush=True)
        for effect in sorted(args.effects):
            # Independent deterministic seed per law/effect, no inherited code/seed.
            row_seed = args.seed + index * 1000000 + round(effect * 100000)
            try:
                hits, means = power_row(row_seed, args.reps, effect, scenario)
            except ValueError as error:
                print(f"effect={effect:.3f} SKIP: {error}", flush=True)
                continue
            for h in range(7):
                if mdes[h] is None and hits[h] / args.reps >= 0.8:
                    mdes[h] = effect
            print(f"effect={effect:.3f} " + " ".join(interval(h, args.reps) for h in hits)
                  + " mean=" + ",".join(f"{v:.4f}" for v in means), flush=True)
        print("GRID_MDE H1 H2 H3 H4 H123 strong beyond=" + str(mdes), flush=True)
    for index, law in enumerate(("window-variance", "rare-regression", "drift", "adaptive")):
        if not args.null_reps:
            break
        rng = random.Random(args.seed + 9000000 + index)
        family = 0
        thresholds = (ALPHA / 4, ALPHA / 3, ALPHA / 2, ALPHA)
        hits = [[0] * 4 for _ in range(4)]
        for _ in range(args.null_reps):
            pvalues = null_replicate(rng, law)
            family += any(holm(pvalues))
            for h, pvalue in enumerate(pvalues):
                for j, threshold in enumerate(thresholds):
                    hits[h][j] += pvalue <= threshold
        print(f"NULL {law} FWER={interval(family, args.null_reps)}", flush=True)
        for h in range(4):
            print(f"  H{h+1} threshold_rejections="
                  + " ".join(interval(k, args.null_reps) for k in hits[h]), flush=True)
    print(f"Explicit Hoeffding-mixture honest U(14/280)={honest_upper(14, 280):.6f}")
    print(f"elapsed_s={time.monotonic() - start:.2f}", flush=True)


if __name__ == "__main__":
    main()
