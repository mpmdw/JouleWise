"""Independent fixture oracles for RL-176's rank tails and decode statistic."""

from fractions import Fraction
from itertools import product
from math import comb, sqrt
from statistics import mean

from joulewise.align.apple.rl176 import S_SUPERIORITY_ALPHA


def exact_tails(populations, assigned):
    def rank_value(candidate, alternatives):
        half_wins = sum(2 if candidate > y else candidate == y for y in alternatives)
        return Fraction(half_wins, 2 * len(alternatives))

    ranks = [
        [rank_value(value, row[:j] + row[j + 1:]) for j, value in enumerate(row)]
        for row in populations
    ]
    observed = sum(row[choice] for row, choice in zip(ranks, assigned))
    possible = [sum(assignment) for assignment in product(*ranks)]
    return (observed / len(ranks), Fraction(sum(v >= observed for v in possible), len(possible)),
            Fraction(sum(v <= observed for v in possible), len(possible)))


def held_decode_score(training, held):
    """Centered two-predictor regression, independent of production's QR."""
    d, z, y = zip(*((row[1], row[2], joules) for row, joules, _ in training))
    d_mean, z_mean, y_mean = map(mean, (d, z, y))
    centered = [(a - d_mean, b - z_mean, c - y_mean) for a, b, c in zip(d, z, y)]
    dd = sum(a * a for a, _, _ in centered)
    dz = sum(a * b for a, b, _ in centered)
    zz = sum(b * b for _, b, _ in centered)
    dy = sum(a * c for a, _, c in centered)
    zy = sum(b * c for _, b, c in centered)
    determinant = dd * zz - dz * dz
    beta_d = (zz * dy - dz * zy) / determinant
    beta_z = (dd * zy - dz * dy) / determinant
    variance = sum((c - a * beta_d - b * beta_z) ** 2 for a, b, c in centered) / (len(d) - 3)
    a = sum(row[1] - d_mean for row, _, _ in held)
    b = sum(row[2] - z_mean for row, _, _ in held)
    k = len(held)
    expected = k * y_mean + a * beta_d + b * beta_z
    leverage = k * k / len(d) + (a * a * zz - 2 * a * b * dz + b * b * dd) / determinant
    bound = sum(width for _, _, width in held)
    sd = sqrt(variance * (k + leverage) + bound * bound + 3 * k)
    return (sum(joules for _, joules, _ in held) - expected) / sd


def held_prefill_score(training, held):
    """Five predictors and two timing edges, via scaled normal equations."""
    def features(row):
        p, d, c = row.prefill_tokens, row.decode_tokens, row.context_tokens
        return (1, p, d, d * (c + p + d / 2), p * (c + p / 2))

    x = [features(row) for row in training]
    scale = list(map(max, zip(*x)))
    columns = [[value / unit for value in feature] for feature, unit in zip(zip(*x), scale)]
    y = [row.energy_j for row in training]
    summed = [sum(c) / unit for c, unit in zip(zip(*(features(row) for row in held)), scale)]

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    equations = [[dot(a, b) for b in columns] + [dot(a, y), z] for a, z in zip(columns, summed)]
    for k in range(5):
        pivot = max(range(k, 5), key=lambda j: abs(equations[j][k]))
        equations[k], equations[pivot] = equations[pivot], equations[k]
        div = equations[k][k]
        equations[k] = [v / div for v in equations[k]]
        for i, eq in enumerate(equations):
            if i != k:
                equations[i] = [v - eq[k] * w for v, w in zip(eq, equations[k])]
    coef, projection = (list(v) for v in zip(*(eq[-2:] for eq in equations)))
    sigma2 = sum((v - dot(coef, row)) ** 2 for v, row in zip(y, zip(*columns))) / (len(y) - 5)
    variance = (sigma2 * (len(held) + dot(projection, summed))
                + sum(r.query_half_width_j for r in held) ** 2 + 2 * len(held))
    return (sum(r.energy_j for r in held) - dot(coef, summed)) / sqrt(variance)


def q_by_second(episode, watts, ns):
    """Independent integral on constant-per-second synthetic fixtures."""
    def charges(t):
        turns = episode.turns
        calls = [call for turn in turns for call in turn.tool_calls]
        if any(row["start_ns"] <= t < row["end_ns"] for row in episode.hardware.get("thermal", {}).get("intervals", ())):
            return 0
        owned = any(span.start_ns <= t < span.end_ns for span in (*turns, *calls))
        return watts[t // ns + 1] if owned else 0

    times = range(episode.start_ns, episode.end_ns, ns)
    total = sum(charges(t) for t in times)
    first = episode.turns[0].first_token_ns
    if first is None:
        return 0, total, None
    prefill_start = episode.turns[0].start_ns
    tools = [call for turn in episode.turns for call in turn.tool_calls]
    prefill = sum(charges(t) for t in times if prefill_start <= t < first
                  and all(not (c.start_ns <= t < c.end_ns) for c in tools))
    q = sum(charges(t) for t in times if t >= first)
    return q, total, prefill


def complete_strata_signature(wins, strata):
    """Count bounded compositions of the null support by inclusion-exclusion."""
    misses = 7 * strata - wins
    count = sum((-1) ** j * comb(strata, j) * comb(misses - 8 * j + strata, strata)
                for j in range(min(strata, misses // 8) + 1))
    p = Fraction(count, 8 ** strata)
    return p, p <= S_SUPERIORITY_ALPHA


def decode_length_ratio(instructed, benign):
    return mean(instructed) / mean(benign)
