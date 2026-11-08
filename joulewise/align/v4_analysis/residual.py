"""V4 sequence-design adapter to the byte-pinned cda28a5ef/4d54cb47b fitter.

The vendored module is unchanged (sha256 in ENGINE-sol.md). No legacy import is
rebound. Parameter covariance, moment iteration, rank and bound flags survive.
"""
from dataclasses import asdict
import math

from . import _frozen_residual as er


def turn(row):
    values = {k: row[k] for k in er.TurnRow.__dataclass_fields__ if k in row}
    return er.TurnRow(**{'episode_id': '', 'group': '', 'duration_s': 0., 'energy_j': 0.,
                        'energy_half_width_j': 0., **values})


def design_row(row):
    return list(er.design_row(turn(row), design='sequence'))


def fit(rows):
    turns = [turn(r) for r in rows]
    model = er.fit_energy_model(turns, design='sequence')
    flags = list(model.flags)
    rank = 5 - sum(f.startswith('unidentified_column:') for f in flags)
    return {**asdict(model), 'flags': flags, 'rank': rank,
            'df': model.n_turns-rank, 'design': 'sequence',
            'support': {name: [min((r[name] for r in rows), default=None),
                               max((r[name] for r in rows), default=None)]
                        for name in ('context_tokens', 'prefill_tokens', 'decode_tokens')}}


def predict(model, rows, *, measured_j, measured_half_width_j, uncertainty_kind='additive_bound'):
    restored = er.EnergyModel(*(model[k] for k in
        ('names', 'coef', 'cov', 'sigma2_per_turn', 'n_turns')))
    turns = [turn(r) for r in rows]
    prediction = er.predict_episode(restored, turns)
    # residual_score calls predict_episode again. Reuse this identical prediction
    # within the operation; no score/fit/decision is cached. Preserve its exact
    # arithmetic, diagnostic order and nonfinite/zero-denominator behavior.
    score_flags = [*prediction.flags, *er._uncertainty_flags(uncertainty_kind)]
    denominator = math.hypot(prediction[1], measured_half_width_j)
    difference = measured_j-prediction[0]
    if not er._finite(measured_j) or not er._finite(measured_half_width_j):
        score_value = math.nan
        score_flags.append('nonfinite_measurement')
    else:
        if measured_half_width_j < 0:
            score_flags.append('negative_half_width')
        if denominator == 0:
            score_flags.append('zero_score_uncertainty')
            score_value = math.copysign(math.inf, difference) if difference else math.nan
        else:
            score_value = difference/denominator
    flags = list(dict.fromkeys([*model['flags'], *prediction.flags, *score_flags]))
    outside = [i for i, row in enumerate(rows) if any(
        bounds[0] is not None and not bounds[0] <= row[name] <= bounds[1]
        for name, bounds in model['support'].items())]
    if outside:
        flags.append('out_of_support')
    return dict(predicted_j=prediction[0], prediction_sd_j=prediction[1],
                residual_j=difference, score=score_value, denominator_j=denominator,
                turn_residuals_j=[r.energy_j-er._dot(er.design_row(r, design='sequence'), model['coef'])
                                  for r in turns],
                out_of_support_turns=outside, flags=flags)


def strip(rows, dose):
    """Strip exactly dose logged reasoning tokens, earliest turn first; keep C/P/J.

    Count withholding never invents unlogged work. The caller reports actual
    dose separately when the requested grid point exceeds available reasoning.
    """
    remaining = dose
    result = []
    for row in rows:
        hidden = min(remaining, row['reasoning_tokens'])
        remaining -= hidden
        result.append({**row, 'decode_tokens': row['decode_tokens']-hidden})
    return result, dose-remaining
