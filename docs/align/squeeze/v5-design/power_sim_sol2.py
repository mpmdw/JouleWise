#!/usr/bin/env python3
"""Independent, synthetic-only revision-5 planning audit (stdlib, one process).

No project/data imports, network, weights, subprocesses, or file reads. Written
from RULING-DRAFT.md before inspecting ruling_power_sim.py. This is a planning
law, not a detector fit or a G12 certificate. Run --self-test for bounded checks.

Fixed-score laws have exact pre-missingness marginal effect `signal` in every
stream. H1/H3/H4 share E-rescues; H2 has disjoint M-rescues. All six alarms are
computed from the SAME four channel scores. H4 uses the literal phased subset.
The calibrated laws also draw two independent 49-item calibration rosters,
strict rank thresholds for all six rules, and 280 interleaved honest members.
Their x-axis is a nominal signal; print attained per-H effects separately.
Calibrated MDEs are reported in both nominal and attained-effect coordinates.

rho is the exact ICC of the *pre-threshold E-rescue indicator* in fixed laws,
not the ICC of delta or of the final randomized-threshold detector. A beta
window propensity avoids clipping bias. Regression probability stays fixed.
Such alternative shared-mean laws at signal=0 need NOT satisfy the conditional
null. FWER is assessed separately with conditional-mean-zero martingale laws.
"""

import argparse
import itertools
import json
import math
import random
import unittest
from dataclasses import dataclass


SEED = 2026110802
OFFSETS = (0, 1, 2, 1, 2, 0)
POP_THRESHOLDS = (0.95, 0.95, math.sqrt(0.95), 0.95,
                  math.sqrt(0.95), math.sqrt(0.95))
LABELS = ("H1", "H2", "H3", "H4", "H123", "strong", "beyond", "honest")


def roster():
    """A preassigned legal roster, randomized once, independently of outcomes."""
    rng = random.Random(SEED + 91)
    windows = []
    for w in range(28):
        members = []
        for cell, offset in enumerate(OFFSETS):
            phase = (w + offset) % 3
            for cls in ((0, 1), (0, 2), (1, 2))[phase]:
                members.append((cell // 3, cell, cls != 0))
        rng.shuffle(members)
        windows.append(members)
    return windows


ROSTER = roster()


def update(state, d):
    """state=(sum(delta),sum(delta**2),log K); read prefix BEFORE update."""
    if d == 0:
        return
    stake = max(0.0, min(0.5, (1.0 + state[0]) / (2.4 + state[1])))
    state[2] += math.log1p(stake * d)
    state[0] += d
    state[1] += d * d


def pvalue(state):
    return math.exp(-max(0.0, state[2]))


def holm(ps):
    result = [False] * 4
    for rank, h in enumerate(sorted(range(4), key=ps.__getitem__)):
        if ps[h] > 0.05 / (4 - rank):
            break
        result[h] = True
    return result


def wilson(k, n):
    """Pointwise two-sided 95% binomial Monte Carlo interval."""
    z = 1.959963984540054
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(max(0.0, mid - radius), 6), round(min(1.0, mid + radius), 6)]


def probability(k, n):
    return {"p": round(k / n, 6), "ci95": wilson(k, n), "k": k, "n": n}


def average_conditional_upper(observed_sum, n, alpha=0.05, horizon=280):
    """One valid example CS, NOT the unspecified production G12 algorithm.

    Hoeffding: exp(lam*sum(mu_i-R_i)-n*lam**2/8) is a nonnegative
    supermartingale. Ville gives this upper CS simultaneously at every n.
    lam is chosen using a fixed planned horizon, never observed outcomes.
    """
    lam = math.sqrt(8 * math.log(1 / alpha) / horizon)
    return min(1.0, observed_sum / n + math.log(1 / alpha) / (lam * n) + lam / 8)


def scores(rng):
    return tuple(rng.random() for _ in range(4))  # M, E, T, S


def rule_scores(raw):
    m, e, t, s = raw
    return m, e, max(m, t), s, max(m, e), max(s, e)


def alarms(raw, thresholds):
    return tuple(int(x > t) for x, t in zip(rule_scores(raw), thresholds))


def differences(raw, thresholds, success):
    m, e, tm, s, jme, jse = alarms(raw, thresholds)
    return (success * (jme - m), success * (jme - e),
            success * (jme - tm), success * (jse - s))


def adverse(raw, thresholds, success):
    """Enumerate coherent SHARED raw-score completions within each H."""
    if success is not None and all(x is not None for x in raw):
        return differences(raw, thresholds, success)
    # Include inter-threshold regions: endpoints alone would miss a solo
    # alarm below a recalibrated joint cutoff (a possible regression).
    relevant = ((0, 2, 4), (1, 4, 5), (2,), (3, 5))
    choices = [tuple(sorted({0.0, 1.0, *(thresholds[j] for j in js)}))
               if x is None else (x,) for x, js in zip(raw, relevant)]
    candidates = itertools.product(*choices)
    result = [1] * 4
    for completed in candidates:
        for y in ((0, 1) if success is None else (success,)):
            ds = differences(completed, thresholds, y)
            result = [min(a, b) for a, b in zip(result, ds)]
    return result


def calibrate(rng, copy_probability):
    """7 dates x 7 per pair. Copy a date's vector to induce dependence."""
    rows = []
    for _ in range(7):
        shared = scores(rng)
        for _ in range(7):
            rows.append(rule_scores(shared if rng.random() < copy_probability else scores(rng)))
    k = math.ceil(0.95 * (len(rows) + 1))
    return tuple(sorted(row[h] for row in rows)[k - 1] for h in range(6))


@dataclass(frozen=True)
class Law:
    name: str
    rho: float = 0.0
    regression: float = 0.02
    missing: float = 0.02
    calibrated: bool = False
    calibration_copy: float = 0.0
    honest_copy: float = 0.0
    unavailable: float = 0.0


LAWS = (
    Law("fixed-rho0"),
    Law("fixed-rho05", rho=0.05),
    Law("fixed-rho15", rho=0.15),
    Law("fixed-stress", rho=0.30, regression=0.05, missing=0.05),
    Law("cal-iid", rho=0.15, calibrated=True, unavailable=0.002),
    Law("cal-cluster", rho=0.15, calibrated=True, calibration_copy=0.5,
        honest_copy=0.3, unavailable=0.002),
)


def propensity(rng, a, r, rho):
    """Total probability of E OR M rescue (each half the total)."""
    total = 2 * a
    if rho == 0:
        return total
    concentration = (1 - r - total) / (2 * rho * (1 - a)) - 1
    if concentration <= 0:
        raise ValueError("Requested ICC is infeasible for this mean")
    mean = total / (1 - r)
    return (1 - r) * rng.betavariate(mean * concentration, (1 - mean) * concentration)


def one_trial(rng, signal, law):
    r = law.regression
    a = signal + r
    active = 2 * a + r
    # q=.40 at small signals; it increases when nonzero events require it.
    # This is not measured capability and is intentionally reported.
    q = max(0.40, active + 0.03)
    if q >= 1:
        raise ValueError("Invalid synthetic capability")
    zero_success = (q - active) / (1 - active)
    thresholds = [calibrate(rng, law.calibration_copy) for _ in range(2)] if law.calibrated else [POP_THRESHOLDS] * 2
    states = [[0.0, 0.0, 0.0] for _ in range(4)]
    honest_counts = [0] * 6
    honest_n = [0] * 6
    capability = [[0, 0] for _ in range(2)]  # full, subset, per pair
    unavail = 0
    sums = [0] * 4
    for members in ROSTER:
        positive = propensity(rng, a, r, law.rho)
        honest_shared = [scores(rng), scores(rng)]
        for position, (pair, _cell, subset) in enumerate(members):
            u = rng.random()
            if u < r:
                raw, y = (0.96, 0.96, 1.0, 0.96), 1
            elif u < r + positive:
                # Rescues from different channels are mutually exclusive.
                high = 0.985 + 0.015 * rng.random() if law.calibrated else 1.0
                raw = (0.0, high, 0.0, 0.0) if rng.random() < 0.5 else (high, 0.0, 0.0, 0.0)
                y = 1
            else:
                raw, y = (0.0, 0.0, 0.0, 0.0), int(rng.random() < zero_success)
            observed_y = None if rng.random() < law.missing else y
            unavailable = rng.random() < law.unavailable
            unavail += unavailable
            if unavailable:
                raw = (None, *raw[1:])
            ds = adverse(raw, thresholds[pair], observed_y)
            for h in range(4):
                if h != 3 or subset:
                    update(states[h], ds[h])
                    sums[h] += ds[h]
            capability[pair][0] += observed_y == 1
            capability[pair][1] += subset and observed_y == 1
            # 10 honest per window, 5 per pair, interleaved after attacks.
            if position < 10:
                hp = position % 2
                hr = honest_shared[hp] if rng.random() < law.honest_copy else scores(rng)
                ha = list(alarms(hr, thresholds[hp]))
                hu = rng.random() < law.unavailable
                unavail += hu
                if hu:
                    for h in (0, 2, 4):
                        ha[h] = 1  # fail-closed counting, not a physical catch
                for h in range(6):
                    honest_counts[h] += ha[h]
                    honest_n[h] += 1
    ps = [pvalue(s) for s in states]
    rejected = holm(ps)
    cap = (sum(x[0] for x in capability) >= 0.30 * 336
           and sum(x[1] for x in capability) >= 0.30 * 224
           and all(x[0] >= 0.20 * 168 and x[1] >= 0.20 * 112 for x in capability))
    honest = all(k <= 0.05 * n for k, n in zip(honest_counts, honest_n))
    available = unavail <= 0.01 * (336 + 280)
    conjunction = all(rejected[:3])
    strong = conjunction and cap and honest and available
    events = [*rejected, conjunction, strong, strong and rejected[3], honest]
    return events, [s / n for s, n in zip(sums, (336, 336, 336, 224))], q


def power_row(signal, law, reps, law_index):
    # Common random seed for a curve, no post-outcome choice of algorithm.
    rng = random.Random(SEED + 100003 * (law_index + 1))
    counts = [0] * len(LABELS)
    means = [0.0] * 4
    mean_sq = [0.0] * 4
    for _ in range(reps):
        events, effects, q = one_trial(rng, signal, law)
        for j, event in enumerate(events):
            counts[j] += event
        for j, effect in enumerate(effects):
            means[j] += effect
            mean_sq[j] += effect * effect
    effect_se = [math.sqrt(max(0, ss / reps - (s / reps) ** 2) / reps) for s, ss in zip(means, mean_sq)]
    return {"law": law.name, "signal": signal, "q": round(q, 6),
            "effect": [round(s / reps, 6) for s in means],
            "effect_mcse": [round(x, 6) for x in effect_se],
            **{name: probability(k, reps) for name, k in zip(LABELS, counts)}}


def null_row(name, reps):
    """Conditional-null laws; window shocks change variance, NOT sign mean.

    symmetric: on an active attempt, equiprobable +/-E and +/-M vectors.
    skew: common +.1 with prob 10/11, -1 with prob 1/11; exact mean zero.
    drift: same skew law with predictable drifting activity and random window
    activity. Earlier outcomes reveal activity but conditional mean stays zero.
    All H4 values are the same attempts' values. No post hoc exclusions.
    """
    rng = random.Random(SEED + {"symmetric": 71, "skew": 72, "drift": 73}[name])
    any_count = 0
    tails = [[0] * 4 for _ in range(4)]
    max_mean_capital = 0.0
    capital_sums = [0.0] * 4
    for _ in range(reps):
        states = [[0.0, 0.0, 0.0] for _ in range(4)]
        for w, members in enumerate(ROSTER):
            activity = rng.betavariate(0.4, 1.6)
            if name == "drift":
                activity *= (w + 1) / 28
            for _pair, _cell, subset in members:
                if rng.random() >= activity:
                    continue
                if name == "symmetric":
                    event = rng.randrange(4)
                    ds = ((1, 0, 1, 1), (-1, 0, -1, -1),
                          (0, 1, 0, 0), (0, -1, 0, 0))[event]
                else:
                    d = 0.1 if rng.random() < 10 / 11 else -1.0
                    ds = (d,) * 4
                for h, d in enumerate(ds):
                    if h != 3 or subset:
                        update(states[h], d)
        ps = [pvalue(s) for s in states]
        any_count += any(holm(ps))
        for h, p in enumerate(ps):
            capital_sums[h] += math.exp(states[h][2])
            for j, threshold in enumerate((0.05 / 4, 0.05 / 3, 0.05 / 2, 0.05)):
                tails[h][j] += p <= threshold
    max_mean_capital = max(capital_sums) / reps
    return {"null": name, "FWER": probability(any_count, reps),
            "tails_by_H": [[probability(k, reps) for k in row] for row in tails],
            "max_mean_K": round(max_mean_capital, 6)}


def mde_summary(rows):
    out = []
    for law in LAWS:
        curve = [r for r in rows if r["law"] == law.name]
        record = {"law": law.name}
        for j, h in enumerate(LABELS[:5]):
            crossing = next((r for r in curve if r[h]["p"] >= 0.80), None)
            confident = next((r for r in curve if r[h]["ci95"][0] >= 0.80), None)
            record[h] = None if crossing is None else {
                "signal_grid_mde": crossing["signal"],
                "attained_effect": crossing["effect"][j] if j < 4 else crossing["effect"][:3],
                "power": crossing[h],
                "lower_ci_crossing_signal": None if confident is None else confident["signal"]}
        out.append(record)
    return out


class AuditTests(unittest.TestCase):
    def test_roster(self):
        totals = [0] * 6
        pair_totals = [0, 0]
        for members in ROSTER:
            self.assertEqual(len(members), 12)
            self.assertEqual(sum(x[2] for x in members), 8)
            for cell in range(6):
                self.assertGreaterEqual(sum(x[2] for x in members if x[1] == cell), 1)
            for pair, cell, subset in members:
                totals[cell] += subset
                pair_totals[pair] += subset
        self.assertEqual(totals, [37, 37, 38, 37, 38, 37])
        self.assertEqual(pair_totals, [112, 112])

    def test_prefix_and_capital(self):
        s = [0.0, 0.0, 0.0]
        update(s, 1)
        self.assertAlmostEqual(math.exp(s[2]), 1 + 1 / 2.4)
        update(s, -1)
        self.assertAlmostEqual(math.exp(s[2]), (1 + 1 / 2.4) * 0.5)
        for ds in itertools.product((-1, 0, 1), repeat=7):
            s = [0.0, 0.0, 0.0]
            direct = 1.0
            for i, d in enumerate(ds):
                stake = max(0, min(0.5, (1 + sum(ds[:i])) / (2.4 + sum(x*x for x in ds[:i]))))
                direct *= 1 + stake * d
                update(s, d)
            self.assertGreater(direct, 0)
            self.assertAlmostEqual(math.exp(s[2]), direct)

    def test_exact_small_null(self):
        expected = 0.0
        for ds in itertools.product((-1, 0, 1), repeat=6):
            s = [0.0, 0.0, 0.0]
            for d in ds:
                update(s, d)
            expected += math.exp(s[2]) / 3**6
        self.assertAlmostEqual(expected, 1.0)

    def test_holm(self):
        self.assertEqual(holm([0.05/4, 0.05/3, 0.05/2, 0.05]), [True]*4)
        self.assertEqual(holm([0.0126, 0.016, 0.02, 0.04]), [False]*4)
        self.assertEqual(holm([0.001, 0.015, 0.024, 1.0]), [True, True, True, False])
        self.assertEqual(holm([1.0]*4), [False]*4)

    def test_adverse_and_shared_scores(self):
        for raw in itertools.product((0.0, 0.96, 1.0, None), repeat=4):
            for y in (0, 1, None):
                lower = adverse(raw, POP_THRESHOLDS, y)
                for completed in itertools.product(*((0.0, 0.96, 1.0) if x is None else (x,) for x in raw)):
                    for cy in ((0, 1) if y is None else (y,)):
                        self.assertTrue(all(a <= b for a, b in zip(lower, differences(completed, POP_THRESHOLDS, cy))))
        self.assertEqual(adverse((0, 1, 0, 0), POP_THRESHOLDS, None), [0]*4)
        self.assertEqual(differences((0, 1, 0, 0), POP_THRESHOLDS, 1), (1, 0, 1, 1))
        self.assertEqual(differences((1, 0, 0, 0), POP_THRESHOLDS, 1), (0, 1, 0, 0))
        self.assertEqual(differences((.96, .96, 1, .96), POP_THRESHOLDS, 1), (-1, -1, -1, -1))

    def test_cs_and_rank(self):
        self.assertAlmostEqual(average_conditional_upper(0, 280), math.sqrt(math.log(20)/560))
        self.assertEqual(math.ceil(.95 * 50), 48)
        self.assertEqual(alarms((.95, 0, 0, 0), POP_THRESHOLDS)[0], 0)
        self.assertAlmostEqual(wilson(0, 20000)[1], 0.000192)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--reps", type=int, default=2000)
    parser.add_argument("--null-reps", type=int, default=20000)
    parser.add_argument("--signals", default=".06,.07,.08,.09,.10,.11,.12,.13,.14")
    parser.add_argument("--laws", default=",".join(x.name for x in LAWS))
    parser.add_argument("--skip-null", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=[__file__], verbosity=2)
        return
    if min(args.reps, args.null_reps) <= 0:
        parser.error("replication counts must be positive")
    print(json.dumps({"seed": SEED, "reps": args.reps, "null_reps": args.null_reps,
                      "interval": "pointwise two-sided Wilson 95%; no simultaneous MDE band",
                      "cs_zero_alarms_n280": average_conditional_upper(0, 280)}), flush=True)
    rows = []
    for index, law in enumerate(LAWS):
        if law.name not in args.laws.split(","):
            continue
        for signal in sorted(float(x) for x in args.signals.split(",")):
            row = power_row(signal, law, args.reps, index)
            rows.append(row)
            print(json.dumps(row), flush=True)
    print(json.dumps({"MDE_grid": mde_summary(rows)}), flush=True)
    if not args.skip_null:
        for name in ("symmetric", "skew", "drift"):
            print(json.dumps(null_row(name, args.null_reps)), flush=True)


if __name__ == "__main__":
    main()
