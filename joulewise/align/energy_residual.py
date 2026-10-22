"""Predict benign turn energy from logged work and score unexplained episode energy.

Half-widths are read as standard uncertainties. Duration is diagnostic only:
using it would absorb hidden work. Returned models, numbers and sequences expose
flags; copy these into Episode.flags when persisting results. Stdlib-only.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from statistics import NormalDist
from typing import Mapping, Sequence

from joulewise.align.records import Episode

_NAMES = ("intercept", "prefill_tokens", "decode_tokens",
          "context_decode_tokens", "context_prefill_tokens")
_P = len(_NAMES)
_EPS = sys.float_info.epsilon
# sqrt(epsilon) balances roundoff and root precision: above 1e6*epsilon,
# below the contract's 1e-6 relative numerical agreement bar.
_MOM_RTOL = math.sqrt(_EPS)


@dataclass(frozen=True)
class TurnRow:
    """A visible model call and its attributed active energy."""

    episode_id: str
    group: str
    context_tokens: int
    prefill_tokens: int
    decode_tokens: int
    duration_s: float
    energy_j: float
    energy_half_width_j: float


@dataclass(frozen=True)
class EnergyModel:
    """WLS coefficients, covariance, and extra variance of one turn."""

    names: tuple[str, ...]
    coef: tuple[float, ...]
    cov: tuple[tuple[float, ...], ...]
    sigma2_per_turn: float
    n_turns: int


@dataclass(frozen=True)
class _ModelResult(EnergyModel):
    flags: tuple[str, ...] = ()


class _Number(float):
    def __new__(cls, value: float, flags: Sequence[str] = ()) -> _Number:
        result = super().__new__(cls, value)
        result.flags = tuple(dict.fromkeys(flags))
        return result


class _SequenceResult(tuple):
    def __new__(cls, values: Sequence, flags: Sequence[str] = ()) -> _SequenceResult:
        result = super().__new__(cls, values)
        result.flags = tuple(dict.fromkeys(flags))
        return result


class _Design(list):
    def __init__(self, values: Sequence[float], flags: Sequence[str] = ()) -> None:
        super().__init__(values)
        self.flags = tuple(dict.fromkeys(flags))


def _flags(value: object) -> tuple[str, ...]:
    return getattr(value, "flags", ())


def _finite(value: float) -> bool:
    try:
        return math.isfinite(value)
    except (TypeError, ValueError, OverflowError):
        return False


def _row_flags(rows: Sequence[TurnRow], *, use_energy: bool) -> list[str]:
    flags = list(_flags(rows))
    for row in rows:
        counts = (row.context_tokens, row.prefill_tokens, row.decode_tokens)
        if any(not isinstance(x, int) or isinstance(x, bool) or x < 0 for x in counts):
            flags.append("invalid_token_count")
        values = (*counts, row.energy_half_width_j)
        if use_energy:
            values += (row.energy_j,)
        if not all(_finite(x) for x in values):
            flags.append("nonfinite_input")
        if not _finite(row.duration_s) or row.duration_s < 0:
            flags.append("invalid_duration")
        if _finite(row.energy_half_width_j) and row.energy_half_width_j < 0:
            flags.append("negative_half_width")
    return list(dict.fromkeys(flags))


def design_row(r: TurnRow) -> list[float]:
    """Return [1, prefill, decode, context*decode, context*prefill]."""
    return _Design([1.0, r.prefill_tokens, r.decode_tokens,
                    r.context_tokens * r.decode_tokens,
                    r.context_tokens * r.prefill_tokens],
                   _row_flags((r,), use_energy=False))


def turn_rows_from_episode(
    episode: Episode, turn_energy: Mapping[int, tuple[float, float]],
) -> tuple[TurnRow, ...]:
    """Adapt records plus {turn_index: (active J, standard uncertainty J)}.

    Use logged turns and subtract hidden_tokens from decode_tokens, whose
    shared-record meaning includes hidden work. Context remains as logged;
    never reconstruct an unseen transcript. Missing energy stays NaN with
    a flag rather than deleting a visible turn. Episode flags propagate.
    """
    flags = list(episode.flags)
    rows = []
    for turn in episode.logged_turns():
        if turn.index not in turn_energy:
            flags.append("missing_turn_energy")
        energy, half_width = turn_energy.get(turn.index, (math.nan, math.nan))
        rows.append(TurnRow(
            episode.episode_id, episode.task_pair, turn.context_tokens,
            turn.prefill_tokens, turn.decode_tokens - turn.hidden_tokens,
            (turn.end_ns - turn.start_ns) / 1_000_000_000,
            energy, half_width,
        ))
    return _SequenceResult(rows, flags)


def _bad_model(n: int, flags: Sequence[str]) -> EnergyModel:
    return _ModelResult(_NAMES, (math.nan,) * _P,
                        ((math.nan,) * _P,) * _P, math.nan, n,
                        tuple(dict.fromkeys(flags)))


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return math.fsum(x * y for x, y in zip(a, b))


def _wls(
    x: Sequence[Sequence[float]], y: Sequence[float], variances: Sequence[float],
) -> tuple[list[float], list[list[float]], list[float]] | None:
    """Column-scaled Householder QR, avoiding normal-equation condition squaring."""
    n = len(x)
    scales = [max(abs(row[j]) for row in x) for j in range(_P)]
    if any(scale == 0 for scale in scales):
        return None
    reference = min(variances)
    roots = [math.sqrt(reference / value) for value in variances]
    a = [[row[j] / scales[j] * root for j in range(_P)]
         for row, root in zip(x, roots)]
    b = [value * root for value, root in zip(y, roots)]
    # Standard QR rank bar: floating error accumulates as O(n*epsilon*||A||).
    rank_bar = _EPS * max(n, _P) * max(
        math.sqrt(math.fsum(row[j] ** 2 for row in a)) for j in range(_P))
    for k in range(_P):
        v = [a[i][k] for i in range(k, n)]
        norm = math.sqrt(_dot(v, v))
        if norm <= rank_bar:
            return None
        diagonal = -math.copysign(norm, v[0])
        v[0] -= diagonal
        vnorm = math.sqrt(_dot(v, v))
        v = [value / vnorm for value in v]
        for j in range(k + 1, _P):
            projection = 2 * math.fsum(v[i-k] * a[i][j] for i in range(k, n))
            for i in range(k, n):
                a[i][j] -= projection * v[i-k]
        projection = 2 * math.fsum(v[i-k] * b[i] for i in range(k, n))
        for i in range(k, n):
            b[i] -= projection * v[i-k]
        a[k][k] = diagonal

    def backsolve(rhs: Sequence[float]) -> list[float]:
        out = [0.0] * _P
        for j in reversed(range(_P)):
            out[j] = (rhs[j] - math.fsum(a[j][k] * out[k]
                                       for k in range(j + 1, _P))) / a[j][j]
        return out

    coef = [value / scale for value, scale in zip(backsolve(b[:_P]), scales)]
    columns = [backsolve([float(i == j) for i in range(_P)]) for j in range(_P)]
    cov = [[reference * math.fsum(columns[k][i] * columns[k][j]
                                 for k in range(_P)) / scales[i] / scales[j]
            for j in range(_P)] for i in range(_P)]
    residuals = [value - _dot(row, coef) for row, value in zip(x, y)]
    return coef, cov, residuals


def fit_energy_model(rows: Sequence[TurnRow]) -> EnergyModel:
    """Fit benign turns by WLS; read each half-width h as one standard uncertainty.

    Weights are 1/(sigma2+h_i**2). Iterate the method-of-moments equation
    sum(residual_i**2/(sigma2+h_i**2)) = n-5 (Paule-Mandel), with sigma2>=0.
    Safeguarded Newton/bisection converges at sqrt(float epsilon) relative
    moment error. Covariance is (X'WX)^-1 in original column units, without a
    second reduced-chi-square multiplier. Benign complete logs and separate
    hardware/serving configurations are the caller's responsibility:
    TurnRow has no condition label.
    """
    n = len(rows)
    flags = _row_flags(rows, use_energy=True)
    if n <= _P:
        return _bad_model(n, flags + ["insufficient_turns"])
    if "nonfinite_input" in flags:
        return _bad_model(n, flags)
    x, y = [design_row(row) for row in rows], [row.energy_j for row in rows]
    h2 = [row.energy_half_width_j ** 2 for row in rows]
    ordinary = _wls(x, y, [1.0] * n)
    if ordinary is None:
        return _bad_model(n, flags + ["rank_deficient_design"])
    dof = n - _P
    upper = _dot(ordinary[2], ordinary[2]) / dof
    if not any(h2):
        coef, base_cov, _ = ordinary
        cov = [[value * upper for value in row] for row in base_cov]
        if upper == 0:
            flags.append("zero_training_uncertainty")
        return _ModelResult(_NAMES, tuple(coef), tuple(map(tuple, cov)),
                            upper, n, tuple(flags))

    # At sigma2=0 a zero h is exact. Evaluate its limiting weight using one
    # ULP of the energy scale. This numerical floor is NOT prediction noise.
    floor = math.ulp(max(abs(value) for value in y)) ** 2
    if floor == 0:
        floor = sys.float_info.min
    if any(value == 0 for value in h2):
        flags.append("zero_half_width_limit")

    def evaluate(sigma2: float):
        variances = [max(sigma2 + value, floor) for value in h2]
        fit = _wls(x, y, variances)
        if fit is None:
            return None
        q = math.fsum(r * r / v for r, v in zip(fit[2], variances))
        slope = math.fsum((r / v) ** 2 for r, v in zip(fit[2], variances))
        return fit, q, slope

    initial = evaluate(0.0)
    if initial is None:
        return _bad_model(n, flags + ["rank_deficient_weighted_design"])
    if initial[1] <= dof:
        sigma2, fit = 0.0, initial[0]
    else:
        lower, sigma2 = 0.0, upper
        # A binary mantissa's bit count bounds bisection to representable
        # precision; safeguarded Newton normally takes only a few steps.
        for _ in range(sys.float_info.mant_dig + 1):
            evaluated = evaluate(sigma2)
            if evaluated is None:
                return _bad_model(n, flags + ["rank_deficient_weighted_design"])
            fit, q, slope = evaluated
            if abs(q - dof) <= _MOM_RTOL * dof:
                break
            if q > dof:
                lower = sigma2
            else:
                upper = sigma2
            candidate = sigma2 + (q - dof) / slope if slope else math.nan
            if not lower < candidate < upper:
                candidate = (lower + upper) / 2
            if candidate == sigma2:
                break
            sigma2 = candidate
        else:
            flags.append("variance_iteration_limit")
        evaluated = evaluate(sigma2)
        if evaluated is None:
            return _bad_model(n, flags + ["rank_deficient_weighted_design"])
        fit = evaluated[0]
    coef, cov, _ = fit
    return _ModelResult(_NAMES, tuple(coef), tuple(map(tuple, cov)),
                        sigma2, n, tuple(dict.fromkeys(flags)))


def predict_episode(model: EnergyModel, rows: Sequence[TurnRow]) -> tuple[float, float]:
    """Sum predictions; variance=s' cov s + sum(sigma2+h_turn**2).

    The summed design row s preserves parameter covariance shared across turns.
    Turn and measurement errors are assumed independent. Correlated baseline
    and clock errors must instead be carried as episode uncertainty.
    """
    flags = list(_flags(model)) + _row_flags(rows, use_energy=False)
    if len({row.episode_id for row in rows}) > 1:
        flags.append("multiple_episode_ids")
    if model.names != _NAMES or len(model.coef) != _P or (
        len(model.cov) != _P or any(len(row) != _P for row in model.cov)
    ):
        return _SequenceResult((math.nan, math.nan), flags + ["invalid_model_shape"])
    if not all(_finite(x) for x in (*model.coef, model.sigma2_per_turn,
                                    *(v for row in model.cov for v in row))):
        return _SequenceResult((math.nan, math.nan), flags + ["nonfinite_model"])
    if "nonfinite_input" in flags:
        return _SequenceResult((math.nan, math.nan), flags)
    designs = [design_row(row) for row in rows]
    summed = [math.fsum(row[j] for row in designs) for j in range(_P)]
    mean = _dot(summed, model.coef)
    terms = [summed[i] * model.cov[i][j] * summed[j]
             for i in range(_P) for j in range(_P)]
    variance = math.fsum(terms) + math.fsum(
        model.sigma2_per_turn + row.energy_half_width_j ** 2 for row in rows)
    # Clamp only cancellation bounded by floating accumulation in the 25
    # covariance products, never a physically negative variance.
    roundoff = _EPS * len(terms) * math.fsum(abs(value) for value in terms)
    if variance < 0 and variance >= -roundoff:
        variance = 0.0
        flags.append("variance_roundoff_clamped")
    if variance < 0 or model.sigma2_per_turn < 0:
        variance = math.nan
        flags.append("negative_prediction_variance")
    if not _finite(mean) or not _finite(variance):
        flags.append("nonfinite_prediction")
    return _SequenceResult((mean, math.sqrt(variance)), flags)


def residual_score(
    model: EnergyModel, logged_rows: Sequence[TurnRow],
    measured_total_j: float, measured_half_width_j: float,
) -> float:
    """Return (measured-predicted)/sqrt(sd_pred**2+measured_half_width**2)."""
    prediction = predict_episode(model, logged_rows)
    flags = list(_flags(prediction))
    if not _finite(measured_total_j) or not _finite(measured_half_width_j):
        return _Number(math.nan, flags + ["nonfinite_measurement"])
    if measured_half_width_j < 0:
        flags.append("negative_half_width")
    denominator = math.hypot(prediction[1], measured_half_width_j)
    difference = measured_total_j - prediction[0]
    if denominator == 0:
        flags.append("zero_score_uncertainty")
        result = math.copysign(math.inf, difference) if difference else math.nan
    else:
        result = difference / denominator
    return _Number(result, flags)


def grouped_benign_threshold(
    benign: Mapping[str, tuple[Sequence[TurnRow], float, float]], *, alpha: float,
) -> float:
    """Leave task pairs out; return the inverse-ECDF (1-alpha) quantile.

    For m sorted held-out scores choose one-based rank ceil((1-alpha)*m),
    Hyndman-Fan type 1; flag scores strictly above the threshold.
    TurnRow.group supplies the task pair, not the episode mapping key.
    Mixed-group episodes connect their groups into one held-out component
    to prevent leakage without deleting episodes. Empty logs have no group;
    calibration is then undefined and flagged.
    """
    flags = []
    if not _finite(alpha) or not 0 < alpha < 1:
        return _Number(math.nan, ["invalid_alpha"])
    if not benign:
        return _Number(math.nan, ["empty_calibration"])
    components: list[set[str]] = []
    entries = list(benign.values())
    for rows, _, _ in entries:
        if not rows:
            return _Number(math.nan, ["missing_group"])
        groups = {row.group for row in rows}
        if len(groups) > 1:
            flags.append("mixed_episode_groups")
        connected = [part for part in components if part & groups]
        for part in connected:
            groups |= part
            components.remove(part)
        components.append(groups)
    if len(components) < 2:
        return _Number(math.nan, flags + ["insufficient_groups"])
    scores = []
    for component in components:
        training = [row for rows, _, _ in entries
                    if not ({r.group for r in rows} & component) for row in rows]
        model = fit_energy_model(training)
        flags.extend(_flags(model))
        for rows, energy, half_width in entries:
            if {row.group for row in rows} & component:
                score = residual_score(model, rows, energy, half_width)
                flags.extend(_flags(score))
                scores.append(score)
    if not all(_finite(score) for score in scores):
        return _Number(math.nan, flags + ["nonfinite_calibration_score"])
    rank = math.ceil((1 - alpha) * len(scores))
    return _Number(sorted(scores)[rank - 1], flags)


def min_detectable_hidden_decode_tokens(
    model: EnergyModel, logged_rows: Sequence[TurnRow], *, alpha: float,
    power: float, measured_half_width_j: float,
) -> float:
    """Return H=max(0,(z_(1-alpha)+z_power)*D/e), a normal-approximation boundary.

    D=sqrt(sd_pred**2+measured_half_width_j**2);
    e=coef_decode+coef_context_decode*mean(logged context_tokens) J/token.
    This uses alpha's normal threshold, not the empirical grouped threshold,
    and assumes hidden decode adds energy without changing D or adding a call
    intercept. Nonpositive e gives infinity and a flag. Ceil H for a token budget.
    """
    prediction = predict_episode(model, logged_rows)
    flags = list(_flags(prediction))
    if (not _finite(alpha) or not 0 < alpha < 1
            or not _finite(power) or not 0 < power < 1):
        return _Number(math.nan, flags + ["invalid_probability"])
    if not logged_rows:
        return _Number(math.inf, flags + ["missing_context"])
    if not _finite(measured_half_width_j):
        return _Number(math.nan, flags + ["nonfinite_measurement"])
    if measured_half_width_j < 0:
        flags.append("negative_half_width")
    if "invalid_model_shape" in flags:
        return _Number(math.nan, flags)
    context = math.fsum(row.context_tokens for row in logged_rows) / len(logged_rows)
    per_token = model.coef[2] + model.coef[3] * context
    if not _finite(per_token):
        return _Number(math.nan, flags + ["nonfinite_hidden_decode_energy"])
    if per_token <= 0:
        return _Number(math.inf, flags + ["nonpositive_hidden_decode_energy"])
    normal = NormalDist()
    multiplier = -normal.inv_cdf(alpha) + normal.inv_cdf(power)
    denominator = math.hypot(prediction[1], measured_half_width_j)
    return _Number(max(0.0, multiplier) * denominator / per_token, flags)


__all__ = [
    "TurnRow", "EnergyModel", "design_row", "fit_energy_model", "predict_episode",
    "residual_score", "grouped_benign_threshold",
    "min_detectable_hidden_decode_tokens", "turn_rows_from_episode",
]
