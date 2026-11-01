"""Independent twin of lane A6 ``metadata`` (``joulewise/align/metadata_baseline.py`` and ``stats.py``).

Written by Claude Opus 5.5 from the lane brief alone (the "Public API" and
"Definitions" of ``briefs/metadata.md``), ``docs/align/PIPELINE.md`` and
``joulewise/align/records.py``, without reading the lane's own code. It is run
beside the real module on the same inputs: where the two disagree by more than
the agreement bar, one of them has a defect, or the two read an open choice
differently. READINGS below lists every open choice this twin made, so the
comparer can tell the two apart.

Stdlib only and written for transparency over speed: the AUC is the explicit
double loop over positive-negative pairs, DeLong's components are the explicit
row and column means of that pair matrix, and the logistic fit is plain
Newton-Raphson with a hand-written Gaussian elimination.

READINGS
========
Each entry is a choice the brief leaves open, the reading taken (the most
literal one), and what a different reading would change.

R1  Feature names. The brief fixes the quantities, not the strings. This twin
    uses ``FEATURE_NAMES`` below, in that order. The comparer maps names.

R2  ``decode_tokens`` includes hidden tokens. ``records.Turn`` says hidden
    tokens "are part of ``decode_tokens``", and the brief says to take the
    counts "from ``episode.totals(logged_only=...)``". So with
    ``logged_only=True`` the twin's ``decode_tokens`` (and every decode-derived
    feature: per-turn mean and max, per second, log1p) still counts hidden
    tokens; only the ``hidden_tokens`` feature (and its log1p) is set to zero.
    If the real module instead subtracts hidden tokens from decode in the
    logged view, every decode feature differs by the hidden count. This choice
    decides whether hidden reasoning is visible to the baseline at all, so it
    changes the baseline's AUC on any world whose sabotage adds hidden tokens.

R3  Zero denominators. A ratio with a zero denominator (no turns in the
    view, or zero turn time) is 0.0, and the per-turn max over no turns is 0.0.

R4  "decode tokens per second of turn time" is the view's total decode count
    divided by the summed turn durations (``end_ns - start_ns``) of the same
    turns, in seconds; not the mean of per-turn rates, and not over the episode
    duration.

R5  ``duration_s`` is ``totals()["duration_ns"] / 1e9``, the episode's span,
    the same in both views. Duration is not a count, so it has no log1p
    feature; the five counts (turns, prefill, decode, hidden, tool calls) do.

R6  "fraction of turns with tool calls" counts a turn when it holds at least
    one tool call that the view counts (in the logged view: a logged call on a
    logged turn, the same rule ``totals()`` uses for ``tool_calls``).

R7  ``auc`` requires labels in {0, 1} (1 = sabotage), at least one of each,
    and no NaN score; otherwise ``ValueError``.

R8  DeLong. Components V10 (one per positive: the share of negatives it beats,
    ties one half) and V01 (one per negative: the share of positives that beat
    it); S10 and S01 are their sample variances with the n - 1 divisor;
    Var(AUC) = S10 / n_pos + S01 / n_neg (DeLong, DeLong and Clarke-Pearson
    1988). Requires at least two of each class.
    Interval (logit transform, as the brief asks): with A the AUC and
    z = Phi^-1((1 + level) / 2),
        se_logit = sqrt(Var) / (A (1 - A))            (delta method)
        (lo, hi) = expit(logit(A) -/+ z se_logit), then clipped to [0, 1].
    At A = 0 or A = 1 the logit is infinite; Var is exactly zero there (every
    pair agrees), so the interval is (A, A).

R9  Paired DeLong. diff = AUC_a - AUC_b; the 2x2 covariances of the
    components (n - 1 divisor) give Var(diff) = S_aa + S_bb - 2 S_ab with
    S = S10 / n_pos + S01 / n_neg; p = erfc(|diff / se| / sqrt 2). If se is
    zero: p = 1 when diff is zero, else 0 (the limit).

R10 Logistic objective. On the standardised scale (z_j = (x_j - mean_j) / sd_j),
    minimise  sum_i [log(1 + exp(eta_i)) - y_i eta_i] + l2 * sum_{j>=1} beta_j^2
    (summed log-loss, not averaged; penalty l2 times the squared norm, no 1/2;
    intercept beta_0 unpenalised). sd is the population standard deviation
    (divisor n). A column whose values are all identical gets coefficient 0 on
    both scales (it is left out of the fit). Back-transform:
    b_j = beta_j / sd_j, b_0 = beta_0 - sum_j beta_j mean_j / sd_j.
    Other conventions (averaged loss, a 1/2 on the penalty, sample sd) change
    the returned coefficients; ``_fit_logistic_core`` takes them as switches so
    the comparer can replay the real module's convention before calling a
    disagreement a defect.

R11 Convergence. Newton-Raphson from beta = 0; stop when the largest absolute
    full Newton step is below 1e-10 * max(1, max_j |beta_j|) (standardised scale,
    current iterate; the max with 1 keeps the bar meaningful when every
    coefficient is near zero). If a full step raises the objective by more
    than the objective's own float noise, (n_rows + width + 3) * eps * value,
    it is halved until it does not (this changes the path, never the optimum).
    Why 1e-10 is far below anything printed: Newton converges quadratically,
    so after a step that small the remaining error is of order its square,
    i.e. float noise. Even an error of 1e-10 per coefficient moves a
    standardised linear predictor by at most 1e-10 * sum_j |z_j| (about 1e-8
    for 16 features at |z| <= 5) and a probability by a quarter of that, while
    probabilities and AUCs print to 3 decimals (resolution 1e-3).

R12 Grouped CV. Groups are ``Episode.task_pair``; label 1 when ``condition ==
    "sabotage"``, 0 when "benign". Features are ``features(ep)`` with the
    default ``logged_only=True`` (the baseline sees only the log).
    ``feature_names=None`` means all of ``FEATURE_NAMES``. Standardisation
    happens inside ``fit_logistic`` on the training rows only. The returned
    list is in the input episode order. A training fold with one class
    raises ``ValueError`` (its unpenalised intercept has no finite optimum).

R13 Cluster bootstrap. Distinct groups are sorted; the RNG is
    ``random.Random(seed)``; each resample draws G group indices with
    ``randrange(G)`` (G = number of distinct groups), keeps every episode of a
    drawn group, as many times as it was drawn. A resample with no positive or
    no negative has no AUC; it is redrawn and not counted. The percentile
    interval uses the linear-interpolation quantile (type 7, numpy's default)
    at (1 - level) / 2 and (1 + level) / 2.
    The AUC of a resample is computed exactly from per-group-pair sums: if
    group g is drawn c_g times, every pair (i in g, j in h) appears c_g c_h
    times, so AUC* = sum_{g,h} c_g c_h W[g][h] / (sum_g c_g P_g)(sum_h c_h N_h),
    with W[g][h] the pair-score sum between g's positives and h's negatives and
    P_g, N_g the class counts. The self-check replays resamples through
    ``auc`` on the explicitly concatenated episodes.

R14 Bootstrap size when ``n_boot`` is None. The quantile standard-error formula
    used: SE(q_p) = sqrt(p (1 - p) / B) / f(q_p), with f the density of the
    bootstrap distribution at the quantile, taken from a normal reference
    (f = phi(z_p) / sigma) whose half-width is z_p sigma. Requiring
    SE < 0.01 * half-width, sigma cancels:
        B > p (1 - p) / (0.01 z_p phi(z_p))^2,   p = (1 - level) / 2,
    so B = floor(that) + 1: 18,577 at level 0.95. It does not depend on the
    data. A data-driven density estimate (from a pilot bootstrap) would give a
    different B; the interval ends then agree only within the Monte Carlo
    error, as they do anyway since the two RNG streams differ.
"""

from __future__ import annotations

import math
import random
import sys
from statistics import NormalDist
from typing import Any, Sequence

from joulewise.align.records import Episode

_STD_NORMAL = NormalDist()
_EPS = sys.float_info.epsilon

COUNT_NAMES: tuple[str, ...] = ("turns", "prefill_tokens", "decode_tokens", "hidden_tokens", "tool_calls")

FEATURE_NAMES: tuple[str, ...] = (
    "turns",
    "prefill_tokens",
    "decode_tokens",
    "hidden_tokens",
    "tool_calls",
    "duration_s",
    "decode_per_turn_mean",
    "decode_per_turn_max",
    "tool_calls_per_turn",
    "decode_tokens_per_turn_second",
    "fraction_turns_with_tool_calls",
    "log1p_turns",
    "log1p_prefill_tokens",
    "log1p_decode_tokens",
    "log1p_hidden_tokens",
    "log1p_tool_calls",
)

# The convergence bar of R11: a full Newton step below this fraction of the
# coefficient scale ends the fit. Set by the brief; R11 says why it is far
# below anything printed.
NEWTON_STEP_BAR = 1e-10

# Hang guards, not tolerances: reaching either one never returns a number.
# Newton with step halving on this smooth, convex objective converges in tens
# of iterations; 200 is room for a badly scaled start, and hitting it raises.
_MAX_NEWTON_ITERATIONS = 200
# After 64 halvings the step is 2**-64 of a Newton step, below one unit in the
# last place of any coefficient of the step's own size; the halving stops there.
_MAX_HALVINGS = 64

# The brief: "the Monte Carlo standard error of each interval end is below 1%
# of the interval's half-width".
_BOOTSTRAP_MC_FRACTION = 0.01


# ---------------------------------------------------------------- features

def _ratio(numerator: float, denominator: float) -> float:
    """numerator / denominator, or 0.0 when the denominator is zero (R3)."""
    return numerator / denominator if denominator else 0.0


def features(episode: Episode, *, logged_only: bool = True) -> dict[str, float]:
    """Counts the log holds, with no energy (brief: "features: from
    ``episode.totals(logged_only=...)``: turns, prefill, decode, hidden (zero
    when logged_only, since a log does not show hidden tokens; say so in the
    docstring), tool calls, duration in seconds; plus decode per turn (mean,
    max), tool calls per turn, decode tokens per second of turn time, the
    fraction of turns with tool calls, and the log1p of each count").

    ``hidden_tokens`` is zero when ``logged_only`` is true, because a log does
    not show hidden tokens. ``decode_tokens`` is taken from ``totals()`` as is,
    and ``records.Turn`` counts hidden tokens inside it (R2).
    """
    totals = episode.totals(logged_only=logged_only)
    view_turns = episode.logged_turns() if logged_only else episode.turns
    if len(view_turns) != totals["turns"]:
        raise AssertionError("features: turn view disagrees with Episode.totals")

    counts = {
        "turns": totals["turns"],
        "prefill_tokens": totals["prefill_tokens"],
        "decode_tokens": totals["decode_tokens"],
        "hidden_tokens": 0 if logged_only else totals["hidden_tokens"],
        "tool_calls": totals["tool_calls"],
    }

    per_turn_decode = [turn.decode_tokens for turn in view_turns]
    turn_time_ns = sum(turn.end_ns - turn.start_ns for turn in view_turns)
    turns_with_calls = 0
    for turn in view_turns:
        counted_calls = [call for call in turn.tool_calls if call.logged or not logged_only]
        if counted_calls:
            turns_with_calls += 1

    out: dict[str, float] = {name: float(counts[name]) for name in COUNT_NAMES}
    out["duration_s"] = totals["duration_ns"] / 1e9
    out["decode_per_turn_mean"] = _ratio(counts["decode_tokens"], counts["turns"])
    out["decode_per_turn_max"] = float(max(per_turn_decode)) if per_turn_decode else 0.0
    out["tool_calls_per_turn"] = _ratio(counts["tool_calls"], counts["turns"])
    out["decode_tokens_per_turn_second"] = _ratio(counts["decode_tokens"], turn_time_ns / 1e9)
    out["fraction_turns_with_tool_calls"] = _ratio(turns_with_calls, counts["turns"])
    for name in COUNT_NAMES:
        out["log1p_" + name] = math.log1p(counts[name])
    return {name: out[name] for name in FEATURE_NAMES}


# ---------------------------------------------------------------- AUC and DeLong

def _psi(positive_score: float, negative_score: float) -> float:
    """Mann-Whitney kernel: 1 if the positive outscores the negative, 1/2 on a tie, else 0."""
    if positive_score > negative_score:
        return 1.0
    if positive_score == negative_score:
        return 0.5
    return 0.0


def _split(scores: Sequence[float], labels: Sequence[int]) -> tuple[list[float], list[float]]:
    """Scores of the positives (label 1) and of the negatives (label 0), in input order (R7)."""
    if len(scores) != len(labels):
        raise ValueError("scores and labels differ in length")
    positives: list[float] = []
    negatives: list[float] = []
    for score, label in zip(scores, labels):
        score = float(score)
        if math.isnan(score):
            raise ValueError("NaN score")
        if label == 1:
            positives.append(score)
        elif label == 0:
            negatives.append(score)
        else:
            raise ValueError(f"label {label!r} is not 0 or 1")
    if not positives or not negatives:
        raise ValueError("AUC needs at least one positive and one negative")
    return positives, negatives


def _pair_matrix(positives: Sequence[float], negatives: Sequence[float]) -> list[list[float]]:
    """psi[i][j] for positive i against negative j."""
    return [[_psi(x, y) for y in negatives] for x in positives]


def auc(scores: Sequence[float], labels: Sequence[int]) -> float:
    """Brief: "auc: the Mann-Whitney probability that a positive (label 1,
    sabotage) outscores a negative, ties counting one half".

    The explicit double loop: sum of psi over every (positive, negative) pair,
    divided by the number of pairs.
    """
    positives, negatives = _split(scores, labels)
    total = 0.0
    for x in positives:
        for y in negatives:
            total += _psi(x, y)
    return total / (len(positives) * len(negatives))


def _delong_components(scores: Sequence[float], labels: Sequence[int]) -> tuple[float, list[float], list[float]]:
    """(AUC, V10, V01): V10[i] = mean_j psi[i][j] per positive, V01[j] = mean_i psi[i][j] per negative (R8)."""
    positives, negatives = _split(scores, labels)
    m, n = len(positives), len(negatives)
    psi = _pair_matrix(positives, negatives)
    v10 = [sum(psi[i][j] for j in range(n)) / n for i in range(m)]
    v01 = [sum(psi[i][j] for i in range(m)) / m for j in range(n)]
    area = sum(sum(row) for row in psi) / (m * n)
    return area, v10, v01


def _delong_variance(scores: Sequence[float], labels: Sequence[int]) -> tuple[float, float]:
    """(AUC, DeLong variance S10 / m + S01 / n) with n - 1 divisors (R8)."""
    area, v10, v01 = _delong_components(scores, labels)
    m, n = len(v10), len(v01)
    if m < 2 or n < 2:
        raise ValueError("DeLong variance needs at least two positives and two negatives")
    s10 = sum((v - area) ** 2 for v in v10) / (m - 1)
    s01 = sum((v - area) ** 2 for v in v01) / (n - 1)
    return area, s10 / m + s01 / n


def _expit(t: float) -> float:
    """1 / (1 + exp(-t)) without overflow."""
    if t >= 0.0:
        return 1.0 / (1.0 + math.exp(-t))
    e = math.exp(t)
    return e / (1.0 + e)


def _two_sided_z(level: float) -> float:
    if not 0.0 < level < 1.0:
        raise ValueError("level must lie strictly between 0 and 1")
    return _STD_NORMAL.inv_cdf(0.5 + level / 2.0)


def delong_ci(scores: Sequence[float], labels: Sequence[int], level: float = 0.95) -> tuple[float, float]:
    """Brief: "delong_ci: DeLong's variance with the logit transform of the AUC
    for the interval (state it), clipped to [0, 1]".

    Stated: (lo, hi) = expit(logit(A) -/+ z sqrt(Var) / (A (1 - A))), with
    z = Phi^-1((1 + level) / 2) and Var the DeLong variance; (A, A) when A is
    0 or 1 (R8).
    """
    z = _two_sided_z(level)
    area, variance = _delong_variance(scores, labels)
    if area <= 0.0 or area >= 1.0:
        clipped = min(1.0, max(0.0, area))
        return clipped, clipped
    se_logit = math.sqrt(variance) / (area * (1.0 - area))
    centre = math.log(area / (1.0 - area))
    lo = _expit(centre - z * se_logit)
    hi = _expit(centre + z * se_logit)
    return min(1.0, max(0.0, lo)), min(1.0, max(0.0, hi))


def _covariance(u: Sequence[float], v: Sequence[float], mean_u: float, mean_v: float) -> float:
    """Sample covariance with the n - 1 divisor, centred on the given means."""
    return sum((a - mean_u) * (b - mean_v) for a, b in zip(u, v)) / (len(u) - 1)


def paired_auc_difference(scores_a: Sequence[float], scores_b: Sequence[float],
                          labels: Sequence[int]) -> tuple[float, float, float]:
    """Brief: "paired_auc_difference: DeLong's paired test on the same labels";
    returns (diff, se, two-sided p) with diff = AUC_a - AUC_b (R9).
    """
    if not len(scores_a) == len(scores_b) == len(labels):
        raise ValueError("scores_a, scores_b and labels differ in length")
    area_a, v10_a, v01_a = _delong_components(scores_a, labels)
    area_b, v10_b, v01_b = _delong_components(scores_b, labels)
    m, n = len(v10_a), len(v01_a)
    if m < 2 or n < 2:
        raise ValueError("DeLong variance needs at least two positives and two negatives")

    s10_aa = _covariance(v10_a, v10_a, area_a, area_a)
    s10_bb = _covariance(v10_b, v10_b, area_b, area_b)
    s10_ab = _covariance(v10_a, v10_b, area_a, area_b)
    s01_aa = _covariance(v01_a, v01_a, area_a, area_a)
    s01_bb = _covariance(v01_b, v01_b, area_b, area_b)
    s01_ab = _covariance(v01_a, v01_b, area_a, area_b)

    var_aa = s10_aa / m + s01_aa / n
    var_bb = s10_bb / m + s01_bb / n
    cov_ab = s10_ab / m + s01_ab / n
    variance = var_aa + var_bb - 2.0 * cov_ab
    # A true zero can come out as a tiny negative after the subtraction; the
    # variance of a difference is never negative.
    variance = max(variance, 0.0)
    se = math.sqrt(variance)
    diff = area_a - area_b
    if se == 0.0:
        p = 1.0 if diff == 0.0 else 0.0
    else:
        p = math.erfc(abs(diff / se) / math.sqrt(2.0))
    return diff, se, p


# ---------------------------------------------------------------- logistic regression

def _log1pexp(t: float) -> float:
    """log(1 + exp(t)) without overflow."""
    return max(t, 0.0) + math.log1p(math.exp(-abs(t)))


def _solve(matrix: Sequence[Sequence[float]], rhs: Sequence[float]) -> list[float]:
    """Solve matrix @ x = rhs by Gaussian elimination with partial pivoting."""
    size = len(rhs)
    aug = [list(map(float, row)) + [float(b)] for row, b in zip(matrix, rhs)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(aug[r][col]))
        if aug[pivot][col] == 0.0:
            raise ValueError("singular Newton system (an unpenalised fit with collinear columns?)")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        for r in range(col + 1, size):
            factor = aug[r][col] / aug[col][col]
            if factor != 0.0:
                for k in range(col, size + 1):
                    aug[r][k] -= factor * aug[col][k]
    x = [0.0] * size
    for r in reversed(range(size)):
        tail = sum(aug[r][k] * x[k] for k in range(r + 1, size))
        x[r] = (aug[r][size] - tail) / aug[r][r]
    return x


def _fit_logistic_core(X: Sequence[Sequence[float]], y: Sequence[int], l2: float, *,
                       penalty_half: bool = False, mean_loss: bool = False,
                       sample_sd: bool = False) -> tuple[list[float], dict[str, Any]]:
    """The fit of R10/R11, with switches for the conventions other readings use.

    Defaults are this twin's reading. ``penalty_half`` puts 1/2 on the penalty,
    ``mean_loss`` averages the log-loss over rows, ``sample_sd`` standardises
    with the n - 1 divisor. Returns (coefficients on the original scale,
    intercept first; details: standardised coefficients, means, sds, iterations).
    """
    if l2 < 0.0 or math.isnan(l2):
        raise ValueError("l2 must be non-negative")
    rows = [[float(v) for v in row] for row in X]
    n_rows = len(rows)
    if n_rows == 0 or n_rows != len(y):
        raise ValueError("X and y must be non-empty and the same length")
    n_features = len(rows[0])
    if any(len(row) != n_features for row in rows):
        raise ValueError("X rows differ in length")
    labels = []
    for label in y:
        if label not in (0, 1):
            raise ValueError(f"label {label!r} is not 0 or 1")
        labels.append(float(label))

    # Standardise each column on these rows; a column of identical values is left out (R10).
    means: list[float] = []
    sds: list[float] = []
    active: list[int] = []
    for j in range(n_features):
        column = [row[j] for row in rows]
        mean = sum(column) / n_rows
        means.append(mean)
        if max(column) == min(column):
            sds.append(0.0)
            continue
        divisor = n_rows - 1 if sample_sd else n_rows
        sd = math.sqrt(sum((v - mean) ** 2 for v in column) / divisor)
        sds.append(sd)
        active.append(j)
    design = [[1.0] + [(row[j] - means[j]) / sds[j] for j in active] for row in rows]
    width = 1 + len(active)

    loss_weight = 1.0 / n_rows if mean_loss else 1.0
    penalty_weight = (0.5 if penalty_half else 1.0) * l2

    def objective(beta: Sequence[float]) -> float:
        loss = 0.0
        for z_row, label in zip(design, labels):
            eta = sum(b * z for b, z in zip(beta, z_row))
            loss += _log1pexp(eta) - label * eta
        return loss_weight * loss + penalty_weight * sum(b * b for b in beta[1:])

    beta = [0.0] * width
    current = objective(beta)
    iterations = 0
    converged = False
    while iterations < _MAX_NEWTON_ITERATIONS:
        iterations += 1
        gradient = [0.0] * width
        hessian = [[0.0] * width for _ in range(width)]
        for z_row, label in zip(design, labels):
            eta = sum(b * z for b, z in zip(beta, z_row))
            prob = _expit(eta)
            weight = prob * (1.0 - prob)
            for a in range(width):
                gradient[a] += loss_weight * (prob - label) * z_row[a]
                for b in range(width):
                    hessian[a][b] += loss_weight * weight * z_row[a] * z_row[b]
        for a in range(1, width):  # the intercept (a = 0) is unpenalised
            gradient[a] += 2.0 * penalty_weight * beta[a]
            hessian[a][a] += 2.0 * penalty_weight
        step = _solve(hessian, gradient)
        scale = max(1.0, max(abs(b) for b in beta))
        if max(abs(s) for s in step) < NEWTON_STEP_BAR * scale:
            beta = [b - s for b, s in zip(beta, step)]
            converged = True
            break
        # Float noise of the objective: a sum of n_rows non-negative terms, each
        # from about width + 3 roundings, so its rounding error is at most
        # (n_rows + width + 3) * eps * value. A rise smaller than that is not a
        # rise; without this allowance a tiny last step could be halved away.
        noise = (n_rows + width + 3) * _EPS * current
        fraction = 1.0
        candidate = [b - s for b, s in zip(beta, step)]
        value = objective(candidate)
        halvings = 0
        while value > current + noise and halvings < _MAX_HALVINGS:
            fraction /= 2.0
            halvings += 1
            candidate = [b - fraction * s for b, s in zip(beta, step)]
            value = objective(candidate)
        beta, current = candidate, value
    if not converged:
        raise RuntimeError("logistic fit did not converge (separable data with l2 = 0?)")

    coefs = [0.0] * (n_features + 1)
    intercept = beta[0]
    for position, j in enumerate(active, start=1):
        coefs[j + 1] = beta[position] / sds[j]
        intercept -= beta[position] * means[j] / sds[j]
    coefs[0] = intercept
    details = {"beta_standardised": beta, "active": active, "means": means, "sds": sds,
               "iterations": iterations}
    return coefs, details


def fit_logistic(X: Sequence[Sequence[float]], y: Sequence[int], *, l2: float) -> list[float]:
    """Brief: "fit_logistic: L2-penalised logistic regression (the intercept
    unpenalised) by Newton-Raphson with features standardised inside the fit
    and coefficients returned on the original scale; convergence when the max
    absolute step falls below 1e-10 relative to the coefficient scale".

    Returns [intercept, b_1, ..., b_k] on the original scale. Objective and
    conventions: R10; convergence bar and why it is far below anything
    printed: R11.
    """
    coefs, _ = _fit_logistic_core(X, y, l2)
    return coefs


def _predict(coefs: Sequence[float], row: Sequence[float]) -> float:
    """Predicted probability expit(b_0 + sum_j b_j x_j) on the original scale."""
    eta = coefs[0] + sum(b * float(x) for b, x in zip(coefs[1:], row))
    return _expit(eta)


# ---------------------------------------------------------------- grouped cross-validation

def _label_of(episode: Episode) -> int:
    if episode.condition == "sabotage":
        return 1
    if episode.condition == "benign":
        return 0
    raise ValueError(f"episode {episode.episode_id!r} has condition {episode.condition!r}")


def grouped_cv_scores(episodes: Sequence[Episode], *, l2: float,
                      feature_names: Sequence[str] | None = None) -> list[tuple[str, float]]:
    """Brief: "grouped_cv_scores: leave-one-task-pair-out; standardisation and
    fitting only on the training folds; the score is the held-out predicted
    probability".

    Returns (episode_id, held-out probability of sabotage) for every episode,
    in input order (R12).
    """
    names = list(FEATURE_NAMES) if feature_names is None else list(feature_names)
    rows = []
    for episode in episodes:
        feats = features(episode)  # logged_only=True: the baseline sees only the log
        rows.append([feats[name] for name in names])
    labels = [_label_of(episode) for episode in episodes]
    groups = [episode.task_pair for episode in episodes]
    distinct = sorted(set(groups))
    if len(distinct) < 2:
        raise ValueError("leave-one-task-pair-out needs at least two task pairs")

    scores: list[float | None] = [None] * len(episodes)
    for held_out in distinct:
        train = [i for i in range(len(episodes)) if groups[i] != held_out]
        test = [i for i in range(len(episodes)) if groups[i] == held_out]
        train_labels = [labels[i] for i in train]
        if len(set(train_labels)) < 2:
            raise ValueError(f"training fold without {held_out!r} has one class")
        coefs = fit_logistic([rows[i] for i in train], train_labels, l2=l2)
        for i in test:
            scores[i] = _predict(coefs, rows[i])
    return [(episode.episode_id, float(score)) for episode, score in zip(episodes, scores)]


# ---------------------------------------------------------------- cluster bootstrap

def bootstrap_size(level: float = 0.95) -> int:
    """B so that each percentile end's Monte Carlo SE is below 1% of the half-width (R14).

    SE(q_p) = sqrt(p (1 - p) / B) / f(q_p) with a normal-reference density
    f = phi(z_p) / sigma and half-width z_p sigma:
    B > p (1 - p) / (0.01 z_p phi(z_p))^2, p = (1 - level) / 2.
    """
    z = _two_sided_z(level)
    p = (1.0 - level) / 2.0
    phi = _STD_NORMAL.pdf(z)
    bound = p * (1.0 - p) / (_BOOTSTRAP_MC_FRACTION * z * phi) ** 2
    return math.floor(bound) + 1


def _quantile_type7(sorted_values: Sequence[float], prob: float) -> float:
    """Linear-interpolation quantile (Hyndman-Fan type 7) of an ascending list."""
    if not sorted_values:
        raise ValueError("quantile of an empty list")
    position = (len(sorted_values) - 1) * prob
    low = math.floor(position)
    high = min(low + 1, len(sorted_values) - 1)
    weight = position - low
    return sorted_values[low] + weight * (sorted_values[high] - sorted_values[low])


def _group_tables(scores: Sequence[float], labels: Sequence[int], groups: Sequence[Any]):
    """Distinct groups (sorted), W[g][h] pair-score sums, positives and negatives per group (R13)."""
    if not len(scores) == len(labels) == len(groups):
        raise ValueError("scores, labels and groups differ in length")
    _split(scores, labels)  # validates labels, NaNs and that both classes exist
    keys = sorted(set(groups))
    index = {key: k for k, key in enumerate(keys)}
    pos_by_group: list[list[float]] = [[] for _ in keys]
    neg_by_group: list[list[float]] = [[] for _ in keys]
    for score, label, group in zip(scores, labels, groups):
        (pos_by_group if label == 1 else neg_by_group)[index[group]].append(float(score))
    pair_sums = [[sum(_psi(x, yv) for x in pos_by_group[g] for yv in neg_by_group[h])
                  for h in range(len(keys))] for g in range(len(keys))]
    n_pos = [len(p) for p in pos_by_group]
    n_neg = [len(q) for q in neg_by_group]
    return keys, pair_sums, n_pos, n_neg


def _bootstrap_draws(scores: Sequence[float], labels: Sequence[int], groups: Sequence[Any],
                     n_boot: int, seed: int) -> tuple[list[Any], list[tuple[list[int], float]]]:
    """n_boot accepted resamples as (draw counts per sorted group, AUC*) (R13)."""
    keys, pair_sums, n_pos, n_neg = _group_tables(scores, labels, groups)
    n_groups = len(keys)
    rng = random.Random(seed)
    draws: list[tuple[list[int], float]] = []
    while len(draws) < n_boot:
        counts = [0] * n_groups
        for _ in range(n_groups):
            counts[rng.randrange(n_groups)] += 1
        total_pos = sum(c * p for c, p in zip(counts, n_pos))
        total_neg = sum(c * q for c, q in zip(counts, n_neg))
        if total_pos == 0 or total_neg == 0:
            continue  # no AUC on a one-class resample: redrawn, not counted
        drawn = [g for g in range(n_groups) if counts[g]]
        numerator = 0.0
        for g in drawn:
            for h in drawn:
                numerator += counts[g] * counts[h] * pair_sums[g][h]
        draws.append((counts, numerator / (total_pos * total_neg)))
    return keys, draws


def cluster_bootstrap_auc_ci(scores, labels, groups, *, level: float = 0.95,
                             n_boot: int | None = None, seed: int = 0) -> tuple[float, float, int]:
    """Brief: "cluster_bootstrap_auc_ci: resample task-pair groups with
    replacement (episodes inside a drawn group kept together), percentile
    interval; if n_boot is None, choose it so the Monte Carlo standard error
    of each interval end is below 1% of the interval's half-width, using the
    stated quantile-standard-error formula, and return how many were used".

    Returns (lo, hi, n_boot_used). Resampling and quantile: R13; the size
    rule: R14.
    """
    _two_sided_z(level)  # validates level
    used = bootstrap_size(level) if n_boot is None else int(n_boot)
    if used < 1:
        raise ValueError("n_boot must be at least 1")
    _, draws = _bootstrap_draws(scores, labels, groups, used, seed)
    values = sorted(value for _, value in draws)
    lo = _quantile_type7(values, (1.0 - level) / 2.0)
    hi = _quantile_type7(values, (1.0 + level) / 2.0)
    return lo, hi, used


__all__ = [
    "COUNT_NAMES", "FEATURE_NAMES", "NEWTON_STEP_BAR", "features", "auc", "delong_ci",
    "paired_auc_difference", "fit_logistic", "grouped_cv_scores", "cluster_bootstrap_auc_ci",
    "bootstrap_size",
]
