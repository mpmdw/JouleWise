"""Independent fixture oracles for RL-176's rank tails and decode statistic."""

from fractions import Fraction
from itertools import product
from math import sqrt
from statistics import mean


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
