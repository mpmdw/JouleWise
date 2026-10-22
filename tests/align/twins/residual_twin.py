"""Independent reference implementation ("twin") of lane A7 `residual` (energy residual detector).

What this module is for: lane A7 builds `joulewise/align/energy_residual.py` from the
build brief `align/briefs/residual.md` (night-archive forward-20261021). This twin is
written by a different model from the same brief, without reading the lane's code, so
that the two can be run on the same synthetic worlds and any disagreement points at a
defect in one of them (docs/align/PIPELINE.md: "Each number-producing analysis has a
second, independent implementation written by a different model").

It is written for transparency, not speed: plain lists, direct formulas, every sum through
``math.fsum`` (correctly rounded, so every result here is independent of row order to the
last bit), stdlib only. Each public name and signature is exactly the brief's.

READINGS (where the brief leaves a choice open, the most literal reading taken here):

R1  Turn half-width. ``energy_half_width_j`` is read as a standard uncertainty: turn i
    contributes measurement variance h_i**2 (the brief: "h_i is the turn's half-width
    read as a standard uncertainty"). ``measured_half_width_j`` of an episode total is
    read the same way.
R2  sigma2 estimator. "the extra per-turn variance, estimated by iterating the method of
    moments to convergence" is read as the iterated generalized method of moments of
    meta-regression (DerSimonian and Kacker 2007): with weights a_i = 1/(s + h_i**2),
    weighted leverages lev_i = a_i x_i' (X'AX)^-1 x_i and WLS residuals r_i, the moment
    equation E[sum a_i r_i**2] = s*sum a_i(1-lev_i) + sum a_i h_i**2 (1-lev_i) is solved
    for s and the weights are recomputed, repeated until the update stops moving:
        s <- max(0, sum a_i (r_i**2 - h_i**2 (1 - lev_i)) / sum a_i (1 - lev_i)).
    The first step uses unit weights (the ordinary least squares moment estimate). The
    fixed point satisfies the Paule-Mandel equation sum r_i**2/(s + h_i**2) = n - p when
    s > 0, and is s = 0 when that sum is already <= n - p at s = 0 (a variance is not
    negative, so the moment estimate is truncated at zero).
R3  Convergence bar. The iteration stops when |s_new - s_old| <= 1e6 * eps *
    (s_new + mean h_i**2), eps the float64 machine epsilon: the floor of the pipeline's
    agreement band ("1e6 times the float noise"), on the scale of the total per-turn
    variance that the weights use. An iteration cap that is never reached in a converging
    run raises RuntimeError instead of returning an unconverged number.
R4  Conditioning. The design columns are scaled by their weighted 2-norms
    d_j = sqrt(sum_i a_i x_ij**2) before forming the normal matrix, so the normal matrix
    has a unit diagonal (the token products reach 1e7 while the intercept is 1); it is
    factored by Cholesky; coefficients and covariance are unscaled afterwards. A column
    that is zero on every row raises ValueError (the model cannot be fitted).
R5  ``cov`` is the WLS parameter covariance (X'WX)^-1 with W = diag(1/(s + h_i**2)) at the
    converged s, not rescaled by the weighted residual sum over its degrees of freedom.
R6  predict_episode's "per-turn variances" are sigma2_per_turn once per turn passed in, so
    var = S' cov S + len(rows) * sigma2_per_turn, S the summed design row. The turns' own
    half-widths are not added: the episode total's measurement uncertainty enters once,
    through ``measured_half_width_j`` in residual_score.
R7  grouped_benign_threshold. The mapping key is the episode id (used only to order the
    episodes); an episode's task pair is the single ``group`` value of its rows (rows
    disagreeing, or no rows, raise ValueError, since the episode cannot be placed in a
    fold). For each group, the model is fitted on every row of every benign episode in the
    other groups and each episode of this group is scored with its own rows, measured
    total and half-width. Quantile definition: the inverse of the empirical distribution
    function (Hyndman and Fan 1996, definition 1), the k-th smallest held-out score with
    k = ceil((1 - alpha) * n). alpha is read as the decimal number its repr prints and the
    product is formed in exact rational arithmetic, so (1 - 0.05) * 20 is exactly 19. The
    detection rule this threshold implies is "flag when score > threshold"; at most a
    fraction alpha of the held-out benign scores lie above it.
R8  min_detectable_hidden_decode_tokens. "the threshold implied by alpha" is the one-sided
    normal quantile z_alpha = Phi^-1(1 - alpha) (the detector flags excess energy only),
    not the empirical threshold; z_power = Phi^-1(power). The per-token energy is
    coef[2] + coef[3] * mean context, positions taken from the design_row order (decode,
    context x decode) rather than from ``names``, so a model whose names differ still
    works; "the episode's mean context" is the arithmetic mean of ``context_tokens`` over
    ``logged_rows``. The score's denominator is sqrt(sd_pred**2 + measured_half_width_j**2)
    with sd_pred from predict_episode on ``logged_rows``. The formula is returned as is: a
    float, not rounded up to a whole token and not clamped at zero (it is negative only
    when power < alpha). A per-token energy <= 0 returns math.inf (no number of hidden
    tokens is detectable).
R9  names = ("intercept", "prefill_tokens", "decode_tokens", "context_x_decode",
    "context_x_prefill"), in design_row order. TurnRow does no validation of its fields
    (the brief gives none). fit_energy_model needs more turns than parameters (n > 5) so
    that the moment equation has degrees of freedom; fewer raises ValueError. A weight
    that would be infinite (s = 0 and a turn with zero half-width) raises ValueError.

Helpers below the public API (``held_out_benign_scores``, ``empirical_quantile``,
``weighted_fit``, ``weighted_q``) are not part of the brief's API; they expose
intermediate numbers so a disagreement with the lane's module can be localized.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from fractions import Fraction
from statistics import NormalDist
from typing import Mapping, Sequence

NAMES: tuple[str, ...] = (
    "intercept", "prefill_tokens", "decode_tokens", "context_x_decode", "context_x_prefill",
)
P = len(NAMES)

# R3: floor of the agreement band, 1e6 times float64 machine epsilon (about 2.2e-10).
CONVERGENCE_REL = 1e6 * sys.float_info.epsilon
# Safety stop for the sigma2 iteration. It bounds run time only; it never sets a number,
# because reaching it raises instead of returning (R3).
MAX_ITERATIONS = 100_000


@dataclass(frozen=True)
class TurnRow:
    episode_id: str
    group: str            # task pair, for grouped cross-validation
    context_tokens: int
    prefill_tokens: int
    decode_tokens: int
    duration_s: float     # turn wall time
    energy_j: float       # attributed active energy of the turn
    energy_half_width_j: float


@dataclass(frozen=True)
class EnergyModel:
    names: tuple[str, ...]
    coef: tuple[float, ...]
    cov: tuple[tuple[float, ...], ...]   # parameter covariance
    sigma2_per_turn: float               # residual variance of one turn beyond measurement half-width
    n_turns: int


# ---------------------------------------------------------------- the brief's API

def design_row(r: TurnRow) -> list[float]:
    """Brief: "`design_row`: [1, prefill_tokens, decode_tokens, context_tokens * decode_tokens,
    context_tokens * prefill_tokens] ... Duration is NOT a regressor".

    The products are formed in integer arithmetic and converted once, so they are exact for
    any product below 2**53.
    """
    return [
        1.0,
        float(r.prefill_tokens),
        float(r.decode_tokens),
        float(r.context_tokens * r.decode_tokens),
        float(r.context_tokens * r.prefill_tokens),
    ]


def fit_energy_model(rows: Sequence[TurnRow]) -> EnergyModel:
    """Brief: "`fit_energy_model`: weighted least squares with per-turn weight 1 / (sigma2 + h_i^2),
    where h_i is the turn's half-width read as a standard uncertainty (state that reading), and
    sigma2 the extra per-turn variance, estimated by iterating the method of moments to
    convergence (state the bar). Solve by QR or Cholesky on the normal equations with the
    columns scaled ... `cov` is the WLS parameter covariance."

    Readings R1 (h_i standard uncertainty), R2 (the iterated moment update), R3 (the bar),
    R4 (column scaling and Cholesky), R5 (cov unscaled), R9 (n > 5).
    """
    rows = list(rows)
    n = len(rows)
    if n <= P:
        raise ValueError(f"fit_energy_model needs more than {P} turns, got {n}")
    X = [design_row(r) for r in rows]
    y = [float(r.energy_j) for r in rows]
    hv = [float(r.energy_half_width_j) ** 2 for r in rows]
    mean_hv = math.fsum(hv) / n

    # Step 0 (R2): the moment estimate with unit weights.
    fit = weighted_fit(X, y, [1.0] * n)
    s = _moment_update([1.0] * n, fit["resid"], fit["leverage"], hv)
    for _ in range(MAX_ITERATIONS):
        a = _weights(s, hv)
        fit = weighted_fit(X, y, a)
        s_new = _moment_update(a, fit["resid"], fit["leverage"], hv)
        if abs(s_new - s) <= CONVERGENCE_REL * (s_new + mean_hv):
            s = s_new
            break
        s = s_new
    else:
        raise RuntimeError(f"sigma2 iteration did not converge in {MAX_ITERATIONS} steps")

    final = weighted_fit(X, y, _weights(s, hv))
    return EnergyModel(
        names=NAMES,
        coef=tuple(final["coef"]),
        cov=tuple(tuple(row) for row in final["cov"]),
        sigma2_per_turn=s,
        n_turns=n,
    )


def predict_episode(model: EnergyModel, rows: Sequence[TurnRow]) -> tuple[float, float]:
    """Brief: "`predict_episode`: sum of turn predictions; sd from the parameter covariance (the
    summed design row's quadratic form) plus the per-turn variances."

    mean = S . coef, var = S' cov S + len(rows) * sigma2_per_turn, S = sum of design rows
    (reading R6). Returns (mean J, sd J).
    """
    rows = list(rows)
    p = len(model.coef)
    design = [design_row(r) for r in rows]
    S = [math.fsum(x[j] for x in design) for j in range(p)]
    mean = math.fsum(S[j] * model.coef[j] for j in range(p))
    quad = math.fsum(S[j] * model.cov[j][k] * S[k] for j in range(p) for k in range(p))
    var = quad + len(rows) * model.sigma2_per_turn
    return mean, math.sqrt(var)


def residual_score(model: EnergyModel, logged_rows: Sequence[TurnRow], measured_total_j: float,
                   measured_half_width_j: float) -> float:
    """Brief: "`residual_score`: (measured - predicted) / sqrt(sd_pred^2 + (measured_half_width)^2)."

    predicted and sd_pred from predict_episode on the logged rows; the half-width is read as
    a standard uncertainty (R1).
    """
    predicted, sd_pred = predict_episode(model, logged_rows)
    denominator = math.sqrt(sd_pred ** 2 + float(measured_half_width_j) ** 2)
    if denominator == 0.0:
        raise ValueError("residual_score denominator is zero (no predictive or measurement uncertainty)")
    return (float(measured_total_j) - predicted) / denominator


def grouped_benign_threshold(benign: Mapping[str, tuple[Sequence[TurnRow], float, float]], *,
                             alpha: float) -> float:
    """Brief: "`grouped_benign_threshold`: for each task pair, fit on the other pairs' benign
    episodes, score this pair's benign episodes; the threshold is the (1 - alpha) empirical
    quantile of all held-out benign scores (state the quantile definition)."

    Reading R7: leave-one-group-out folds keyed on the rows' ``group``; the quantile is the
    inverse empirical distribution function, x_(k) with k = ceil((1 - alpha) * n).
    """
    _check_probability("alpha", alpha)
    scores = [score for _, _, score in held_out_benign_scores(benign)]
    return empirical_quantile(scores, 1 - _decimal(alpha))


def min_detectable_hidden_decode_tokens(model: EnergyModel, logged_rows: Sequence[TurnRow], *,
                                        alpha: float, power: float,
                                        measured_half_width_j: float) -> float:
    """Brief: "hidden decode tokens add (decode coefficient + context-product coefficient x the
    episode's mean context) joules each; the minimum H such that the shifted score exceeds the
    threshold implied by alpha with probability `power`, under the normal approximation
    (z_alpha + z_power) x the score's denominator / the per-token energy."

    Formula (reading R8):
        e     = coef[decode] + coef[context x decode] * mean(context_tokens over logged_rows)
        D     = sqrt(sd_pred**2 + measured_half_width_j**2),  sd_pred from predict_episode
        H_min = (Phi^-1(1 - alpha) + Phi^-1(power)) * D / e
    Why: H hidden tokens shift the score by H*e/D; the shifted score Z + H*e/D exceeds
    z_alpha with probability Phi(H*e/D - z_alpha), which equals ``power`` at H_min.
    Returns math.inf when e <= 0.
    """
    _check_probability("alpha", alpha)
    _check_probability("power", power)
    rows = list(logged_rows)
    if not rows:
        raise ValueError("min_detectable_hidden_decode_tokens needs at least one logged row (mean context)")
    mean_context = math.fsum(float(r.context_tokens) for r in rows) / len(rows)
    per_token_j = model.coef[2] + model.coef[3] * mean_context
    _, sd_pred = predict_episode(model, rows)
    denominator = math.sqrt(sd_pred ** 2 + float(measured_half_width_j) ** 2)
    z_alpha = NormalDist().inv_cdf(1 - alpha)
    z_power = NormalDist().inv_cdf(power)
    if per_token_j <= 0.0:
        return math.inf
    return (z_alpha + z_power) * denominator / per_token_j


# ---------------------------------------------------------------- helpers (not the brief's API)

def held_out_benign_scores(benign: Mapping[str, tuple[Sequence[TurnRow], float, float]]
                           ) -> list[tuple[str, str, float]]:
    """(episode_id, group, held-out score) for every benign episode, in group then id order (R7)."""
    groups: dict[str, str] = {}
    for episode_id in sorted(benign):
        rows = list(benign[episode_id][0])
        found = {r.group for r in rows}
        if len(found) != 1:
            raise ValueError(f"episode {episode_id!r} has rows in groups {sorted(found)}; need exactly one")
        groups[episode_id] = found.pop()
    distinct = sorted(set(groups.values()))
    if len(distinct) < 2:
        raise ValueError("grouped_benign_threshold needs at least two task pairs")
    out: list[tuple[str, str, float]] = []
    for g in distinct:
        train = [r for eid in sorted(benign) if groups[eid] != g for r in benign[eid][0]]
        model = fit_energy_model(train)
        for eid in sorted(benign):
            if groups[eid] == g:
                rows, total_j, half_width_j = benign[eid]
                out.append((eid, g, residual_score(model, rows, total_j, half_width_j)))
    return out


def empirical_quantile(values: Sequence[float], q: Fraction | float) -> float:
    """Inverse empirical distribution function (Hyndman-Fan 1): x_(k), k = ceil(q * n), 1-indexed."""
    xs = sorted(values)
    n = len(xs)
    if n == 0:
        raise ValueError("empirical_quantile of no values")
    q = Fraction(q)
    if not 0 < q <= 1:
        raise ValueError(f"quantile level {q} outside (0, 1]")
    k = math.ceil(q * n)
    return xs[k - 1]


def weighted_fit(X: Sequence[Sequence[float]], y: Sequence[float], a: Sequence[float]) -> dict:
    """WLS of y on X with weights a, columns scaled to unit weighted norm, Cholesky (R4).

    Returns coef, cov = (X'AX)^-1, resid = y - X coef, leverage_i = a_i x_i'(X'AX)^-1 x_i, and
    the scaled normal matrix and right-hand side (for conditioning checks).
    """
    n = len(X)
    p = len(X[0])
    d = []
    for j in range(p):
        dj = math.sqrt(math.fsum(a[i] * X[i][j] * X[i][j] for i in range(n)))
        if dj == 0.0:
            raise ValueError(f"design column {j} is zero on every row; the model cannot be fitted")
        d.append(dj)
    Z = [[X[i][j] / d[j] for j in range(p)] for i in range(n)]
    M = [[math.fsum(a[i] * Z[i][j] * Z[i][k] for i in range(n)) for k in range(p)] for j in range(p)]
    v = [math.fsum(a[i] * Z[i][j] * y[i] for i in range(n)) for j in range(p)]
    L = _cholesky(M)
    b = _cholesky_solve(L, v)
    M_inv = [_cholesky_solve(L, [1.0 if i == j else 0.0 for i in range(p)]) for j in range(p)]
    coef = [b[j] / d[j] for j in range(p)]
    cov = [[M_inv[j][k] / (d[j] * d[k]) for k in range(p)] for j in range(p)]
    resid = [math.fsum([y[i]] + [-X[i][j] * coef[j] for j in range(p)]) for i in range(n)]
    leverage = [a[i] * math.fsum(Z[i][j] * M_inv[j][k] * Z[i][k] for j in range(p) for k in range(p))
                for i in range(n)]
    return {"coef": coef, "cov": cov, "resid": resid, "leverage": leverage,
            "scaled_normal": M, "scaled_rhs": v, "scaled_coef": b, "scale": d}


def weighted_q(rows: Sequence[TurnRow], sigma2: float) -> float:
    """Q(s) = sum r_i**2 / (s + h_i**2) of the WLS fit at s; equals n - p at the R2 fixed point."""
    rows = list(rows)
    hv = [float(r.energy_half_width_j) ** 2 for r in rows]
    a = _weights(sigma2, hv)
    fit = weighted_fit([design_row(r) for r in rows], [float(r.energy_j) for r in rows], a)
    return math.fsum(a[i] * fit["resid"][i] ** 2 for i in range(len(rows)))


def _moment_update(a: Sequence[float], resid: Sequence[float], leverage: Sequence[float],
                   hv: Sequence[float]) -> float:
    n = len(a)
    numerator = math.fsum(a[i] * (resid[i] ** 2 - hv[i] * (1.0 - leverage[i])) for i in range(n))
    denominator = math.fsum(a[i] * (1.0 - leverage[i]) for i in range(n))
    return max(0.0, numerator / denominator)


def _weights(s: float, hv: Sequence[float]) -> list[float]:
    out = []
    for h2 in hv:
        total = s + h2
        if total <= 0.0:
            raise ValueError("a turn has zero half-width while sigma2 is zero: its weight would be infinite")
        out.append(1.0 / total)
    return out


def _cholesky(M: Sequence[Sequence[float]]) -> list[list[float]]:
    p = len(M)
    L = [[0.0] * p for _ in range(p)]
    for j in range(p):
        diag = M[j][j] - math.fsum(L[j][k] * L[j][k] for k in range(j))
        if diag <= 0.0:
            raise ValueError("normal matrix is not positive definite (collinear design columns)")
        L[j][j] = math.sqrt(diag)
        for i in range(j + 1, p):
            L[i][j] = (M[i][j] - math.fsum(L[i][k] * L[j][k] for k in range(j))) / L[j][j]
    return L


def _cholesky_solve(L: Sequence[Sequence[float]], b: Sequence[float]) -> list[float]:
    p = len(L)
    w = [0.0] * p
    for i in range(p):
        w[i] = (b[i] - math.fsum(L[i][k] * w[k] for k in range(i))) / L[i][i]
    x = [0.0] * p
    for i in reversed(range(p)):
        x[i] = (w[i] - math.fsum(L[k][i] * x[k] for k in range(i + 1, p))) / L[i][i]
    return x


def _decimal(value: float) -> Fraction:
    """The decimal number repr(value) prints, as an exact fraction (R7)."""
    return Fraction(repr(float(value)))


def _check_probability(name: str, value: float) -> None:
    if not 0.0 < value < 1.0:
        raise ValueError(f"{name} must lie strictly between 0 and 1, got {value!r}")


__all__ = [
    "TurnRow", "EnergyModel", "design_row", "fit_energy_model", "predict_episode", "residual_score",
    "grouped_benign_threshold", "min_detectable_hidden_decode_tokens",
]
