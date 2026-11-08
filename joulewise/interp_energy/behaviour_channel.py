"""Conditional energy predictions for the free-running behaviour channel.

No telemetry, model loading, calibration fitting, or measurement-file discovery
occurs here. See README.md beside this module for units, inference assumptions,
the symmetric decomposition, and public repository parameter-source pointers.
All confidence intervals condition on the supplied energy coefficients.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
from statistics import NormalDist
from typing import Sequence


FEATURES = ("prefill", "decode", "context", "duration", "fixed")
PARAMETER_REFERENCES = (
    "docs/research-audits/2026-11-07/interp-weight-edit-energy.md#12-how-big-is-the-behaviour-term-for-astra",
    "docs/research_question_bank.md (PC-4/PC-5/PC-6: decode and KV-growth planning)",
    "docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md (J/GB, not J/token)",
    "docs/registrations/bytes_known_bytes_reading_rule_DRAFT.md (baseline and boundary accounting)",
)


def _nonnegative(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite nonnegative number")
    try:
        valid = math.isfinite(value) and value >= 0
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"{name} must be a finite nonnegative number")


def _count(name: str, value: int) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _probability(name: str, value: float) -> None:
    _nonnegative(name, value)
    if value > 1:
        raise ValueError(f"{name} must be in [0, 1]")


@dataclass(frozen=True)
class Answer:
    """One attempt from an independent problem; seeds pair across arms.

    Context exposure is sum(p + k for k in range(d)). The convention charges
    every reported decode token at context p, p+1, ..., p+d-1. Calibration
    counts must use this same convention. Duration is the complete answer
    window, including prefill, decode and included overhead.
    """

    problem_id: str
    prefill_tokens: int
    decode_tokens: int
    correct: bool
    duration_s: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.problem_id, str) or not self.problem_id.strip():
            raise ValueError("problem_id must be a nonempty string")
        _count("prefill_tokens", self.prefill_tokens)
        _count("decode_tokens", self.decode_tokens)
        if type(self.correct) is not bool:
            raise ValueError("correct must be a boolean")
        if self.duration_s is not None:
            _nonnegative("duration_s", self.duration_s)

    @property
    def context_exposure(self) -> int:
        p, d = self.prefill_tokens, self.decode_tokens
        return p * d + d * (d - 1) // 2


@dataclass(frozen=True)
class EnergyModel:
    """E = fixed + a*p + b*d + c*context_exposure + idle_w*duration.

    In above_idle mode the coefficients/fixed term exclude idle, so adding
    idle_w*duration predicts gross energy. In gross mode coefficients already
    include idle: idle_w must be zero and no above-idle view is identified.
    source is an opaque provenance string, never a path to follow.
    """

    prefill_j_per_token: float
    decode_j_per_token: float
    context_j_per_token_squared: float = 0.0
    idle_w: float = 0.0
    fixed_j: float = 0.0
    coefficient_basis: str = "above_idle"
    source: str = "user supplied; calibration not verified"

    def __post_init__(self) -> None:
        for name in ("prefill_j_per_token", "decode_j_per_token",
                     "context_j_per_token_squared", "idle_w", "fixed_j"):
            _nonnegative(name, getattr(self, name))
        if self.coefficient_basis not in ("above_idle", "gross"):
            raise ValueError("coefficient_basis must be above_idle or gross")
        if self.coefficient_basis == "gross" and self.idle_w != 0:
            raise ValueError("gross coefficients require idle_w=0 (avoid double counting)")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a nonempty provenance string")

    @property
    def coefficients(self) -> tuple[float, ...]:
        return (self.prefill_j_per_token, self.decode_j_per_token,
                self.context_j_per_token_squared, self.idle_w, self.fixed_j)


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    value = math.fsum(a * b for a, b in zip(left, right))
    if not math.isfinite(value):
        raise ValueError("energy calculation overflowed; check counts and units")
    return value


def _row(answer: Answer, model: EnergyModel) -> tuple[float, ...]:
    if model.idle_w and answer.duration_s is None:
        raise ValueError("duration_s is required when idle_w is nonzero")
    return (answer.prefill_tokens, answer.decode_tokens, answer.context_exposure,
            answer.duration_s or 0.0, 1.0, float(answer.correct))


def answer_energy(answer: Answer, model: EnergyModel) -> dict:
    """Return modeled gross energy and, if identified, the above-idle view."""
    row = _row(answer, model)
    parts = {name: coefficient * value
             for name, coefficient, value in zip(FEATURES, model.coefficients, row)}
    gross = _dot(model.coefficients, row)
    return {
        "problem_id": answer.problem_id,
        "correct": answer.correct,
        "gross_j": gross,
        "above_idle_j": (_dot(model.coefficients[:3] + (0.0, model.fixed_j), row)
                         if model.coefficient_basis == "above_idle" else None),
        "components_j": parts,
    }


def _mean(rows: Sequence[Sequence[float]]) -> tuple[float, ...]:
    return tuple(math.fsum(row[i] for row in rows) / len(rows) for i in range(6))


def _summary(mean: Sequence[float], model: EnergyModel, n: int | None) -> dict:
    energy = _dot(model.coefficients, mean)
    accuracy = mean[5]
    return {
        "n_answers": n,
        "n_correct": round(accuracy * n) if n is not None else None,
        "accuracy": accuracy,
        "mean_prefill_tokens": mean[0],
        "mean_decode_tokens": mean[1],
        "mean_context_exposure": mean[2],
        "gross_j_per_answer": energy,
        "gross_j_per_correct": energy / accuracy if accuracy else None,
        "total_gross_j": energy * n if n is not None else None,
        "above_idle_j_per_answer": (
            _dot(model.coefficients[:3] + (0.0, model.fixed_j), mean)
            if model.coefficient_basis == "above_idle" else None),
        "decode_tokens_per_correct": mean[1] / accuracy if accuracy else None,
        "total_tokens_per_correct": (mean[0] + mean[1]) / accuracy if accuracy else None,
    }


def summarize_answers(answers: Sequence[Answer], model: EnergyModel) -> dict:
    """J/correct is energy of ALL attempts divided by the number correct."""
    if not answers:
        raise ValueError("an arm must contain at least one answer")
    return _summary(_mean([_row(a, model) for a in answers]), model, len(answers))


def _metric_weights(base: EnergyModel, edited: EnergyModel) -> dict:
    """Each metric is q_base . u_base + q_edited . u_edited."""
    if base.coefficient_basis != edited.coefficient_basis:
        raise ValueError("both arms must use the same coefficient_basis for decomposition")
    b, e = base.coefficients, edited.coefficients
    zero = (0.0,) * 5
    midpoint = tuple((x + y) / 2 for x, y in zip(b, e))
    half_change = tuple((y - x) / 2 for x, y in zip(b, e))
    metrics = {
        "base_j": (b, zero),
        "edited_j": (zero, e),
        "delta_j": (tuple(-x for x in b), e),
        "behaviour_j": (tuple(-x for x in midpoint), midpoint),
        "rate_j": (half_change, half_change),
    }
    for name, indices, coefficients, behaviour in (
        ("token_count_j", (0, 1, 2), midpoint, True),
        ("per_token_j", (0, 1, 2), half_change, False),
        ("idle_duration_j", (3,), midpoint, True),
        ("idle_power_j", (3,), half_change, False),
        ("fixed_count_j", (4,), midpoint, True),
        ("fixed_rate_j", (4,), half_change, False),
    ):
        weights = tuple(x if i in indices else 0.0 for i, x in enumerate(coefficients))
        metrics[name] = (tuple(-x for x in weights) if behaviour else weights, weights)
    return metrics


def _linear_ratio(mean: Sequence[float], weights: Sequence[float],
                  per_correct: bool) -> float | None:
    if not any(weights):
        return 0.0
    if per_correct and mean[5] == 0:
        return None
    return _dot(weights, mean) / (mean[5] if per_correct else 1.0)


def _estimate(means: Sequence[Sequence[float]], weights: Sequence[Sequence[float]],
              per_correct: bool) -> float | None:
    terms = [_linear_ratio(mean, q, per_correct) for mean, q in zip(means, weights)]
    return None if None in terms else math.fsum(terms)


def _influences(rows: Sequence[Sequence[float]], mean: Sequence[float],
                weights: Sequence[float], per_correct: bool) -> list[float]:
    if not any(weights):
        return [0.0] * len(rows)
    denominator = mean[5] if per_correct else 1.0
    value = _dot(weights, mean) / denominator
    return [(_dot(weights, tuple(x - m for x, m in zip(row, mean)))
             - (value * (row[5] - mean[5]) if per_correct else 0.0)) / denominator
            for row in rows]


def _variance_of_mean(values: Sequence[float]) -> float:
    mean = math.fsum(values) / len(values)
    return math.fsum((v - mean) ** 2 for v in values) / (len(values) * (len(values) - 1))


def _quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lo = int(position)
    fraction = position - lo
    return ordered[lo] * (1 - fraction) + ordered[min(lo + 1, len(ordered) - 1)] * fraction


def _intervals(rows: Sequence[Sequence[Sequence[float]]], means: Sequence[Sequence[float]],
               metrics: dict, per_correct: bool, paired: bool,
               confidence: float, bootstrap_means: list) -> dict:
    tail = (1 - confidence) / 2
    z = -NormalDist().inv_cdf(tail)
    results = {}
    for name, weights in metrics.items():
        estimate = _estimate(means, weights, per_correct)
        draws = [_estimate(sample, weights, per_correct) for sample in bootstrap_means]
        undefined = sum(value is None for value in draws)
        if estimate is None:
            delta_interval = {"status": "zero_correct", "lower": None, "upper": None,
                              "standard_error": None}
        else:
            influences = [_influences(arm, mean, q, per_correct)
                          for arm, mean, q in zip(rows, means, weights)]
            if paired:
                variance = _variance_of_mean([a + b for a, b in zip(*influences)])
            else:
                variance = math.fsum(_variance_of_mean(arm) for arm in influences)
            se = math.sqrt(variance)
            delta_interval = {"status": "ok", "lower": estimate - z * se,
                              "upper": estimate + z * se, "standard_error": se}
        if undefined:
            # Never silently condition a ratio interval on nonzero-correct draws.
            bootstrap = {"status": "undefined_zero_correct_resamples",
                         "lower": None, "upper": None}
        else:
            bootstrap = {"status": "ok", "lower": _quantile(draws, tail),
                         "upper": _quantile(draws, 1 - tail)}
        bootstrap.update({"resamples": len(draws), "undefined_resamples": undefined})
        results[name] = {"estimate": estimate, "delta_method": delta_interval,
                         "bootstrap_percentile": bootstrap}
    return results


def compare_answers(base: Sequence[Answer], edited: Sequence[Answer],
                    base_model: EnergyModel, edited_model: EnergyModel | None = None,
                    *, paired: bool = True, confidence: float = 0.95,
                    bootstrap_samples: int = 2000, seed: int = 0) -> dict:
    """Compare arms; paired units must be unique independent problem IDs.

    Delta-method normal CIs use empirical influence functions, including the
    energy/correctness covariance. Bootstrap resamples whole paired problems
    (or independent answers with paired=False), recomputing every denominator.
    These are exploratory sampling intervals, not metrological claim gates.
    """
    edited_model = edited_model or base_model
    if type(paired) is not bool:
        raise ValueError("paired must be boolean")
    _probability("confidence", confidence)
    if confidence == 0 or confidence == 1:
        raise ValueError("confidence must be strictly between 0 and 1")
    if type(bootstrap_samples) is not int or bootstrap_samples < 100:
        raise ValueError("bootstrap_samples must be an integer >= 100")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    metrics = _metric_weights(base_model, edited_model)
    base, edited = list(base), list(edited)
    if min(len(base), len(edited)) < 2:
        raise ValueError("each arm needs at least two independent sampling units")
    for arm in (base, edited):
        if len({a.problem_id for a in arm}) != len(arm):
            raise ValueError("problem_id must be unique within each arm; repeated problems need cluster analysis")
        if (base_model.idle_w or edited_model.idle_w) and any(a.duration_s is None for a in arm):
            raise ValueError("duration_s is required in both arms when either idle_w is nonzero")
    if paired:
        edited_by_id = {a.problem_id: a for a in edited}
        if {a.problem_id for a in base} != set(edited_by_id):
            raise ValueError("paired arms must have exactly the same problem_id roster")
        edited = [edited_by_id[a.problem_id] for a in base]
    rows = ([_row(a, base_model) for a in base], [_row(a, edited_model) for a in edited])
    means = tuple(_mean(arm) for arm in rows)
    rng = random.Random(seed)
    samples = []
    for _ in range(bootstrap_samples):
        indices = [rng.randrange(len(base)) for _ in base]
        other = indices if paired else [rng.randrange(len(edited)) for _ in edited]
        samples.append((_mean([rows[0][i] for i in indices]),
                        _mean([rows[1][i] for i in other])))
    warnings = [
        "Predictions, not measured energy; intervals condition on supplied coefficients.",
        "Sampling CIs exclude calibration error, meter error and systematic baseline bounds.",
        "Normal delta-method CIs can be unreliable with few correct answers; no claim gate is applied.",
    ]
    if any(mean[5] in (0, 1) for mean in means):
        warnings.append("An accuracy is at a sample boundary; resampling cannot recover unseen outcomes.")
    return {
        "schema": "interp-energy-behaviour/v1",
        "status": "exploratory_model_prediction",
        "energy_basis": "gross",
        "inference": {"paired": paired, "sampling_unit": "problem_id",
                      "confidence": confidence, "bootstrap_samples": bootstrap_samples,
                      "seed": seed, "coefficient_uncertainty": "not included"},
        "models": {"base": asdict(base_model), "edited": asdict(edited_model)},
        "base": _summary(means[0], base_model, len(base)),
        "edited": _summary(means[1], edited_model, len(edited)),
        "answers": {"base": [answer_energy(a, base_model) for a in base],
                    "edited": [answer_energy(a, edited_model) for a in edited]},
        "per_answer": _intervals(rows, means, metrics, False, paired, confidence, samples),
        "per_correct": _intervals(rows, means, metrics, True, paired, confidence, samples),
        "decomposition": {
            "sign": "edited minus base; negative means lower modeled energy",
            "identity": "delta_j = behaviour_j + rate_j",
            "behaviour_j": "token_count_j + idle_duration_j + fixed_count_j",
            "rate_j": "per_token_j + idle_power_j + fixed_rate_j",
            "token_count_j": "prefill/decode counts and integrated context exposure",
            "per_correct": "work per correct includes ALL attempts and the accuracy denominator",
            "allocation": "symmetric midpoint (half of the work/rate interaction to each)",
        },
        "warnings": warnings,
        "parameter_references": list(PARAMETER_REFERENCES),
    }


@dataclass(frozen=True)
class CapScenario:
    """Two-point decode-length mixture; accuracy need not depend on cap status.

    duration_s is expected full-window duration, required for nonzero idle_w.
    No distribution or sample size is invented from published percentages.
    """

    cap_hit_fraction: float
    accuracy: float
    noncap_decode_tokens: int
    prefill_tokens: int = 0
    cap_tokens: int = 32768
    duration_s: float | None = None

    def __post_init__(self) -> None:
        _probability("cap_hit_fraction", self.cap_hit_fraction)
        _probability("accuracy", self.accuracy)
        _count("noncap_decode_tokens", self.noncap_decode_tokens)
        _count("prefill_tokens", self.prefill_tokens)
        _count("cap_tokens", self.cap_tokens)
        if self.cap_tokens == 0 or self.noncap_decode_tokens >= self.cap_tokens:
            raise ValueError("noncap_decode_tokens must be below a positive cap_tokens")
        if self.duration_s is not None:
            _nonnegative("duration_s", self.duration_s)

    def mean_features(self, model: EnergyModel) -> tuple[float, ...]:
        q = self.cap_hit_fraction
        capped = Answer("cap", self.prefill_tokens, self.cap_tokens, False, self.duration_s)
        short = Answer("short", self.prefill_tokens, self.noncap_decode_tokens, False, self.duration_s)
        c, s = _row(capped, model), _row(short, model)
        return tuple(q * x + (1 - q) * y for x, y in zip(c[:5], s[:5])) + (self.accuracy,)


def compare_scenarios(base: CapScenario, edited: CapScenario, base_model: EnergyModel,
                      edited_model: EnergyModel | None = None) -> dict:
    """Expected values only: cap fractions do not identify a sampling CI."""
    edited_model = edited_model or base_model
    metrics = _metric_weights(base_model, edited_model)
    if (base_model.idle_w or edited_model.idle_w) and (
        base.duration_s is None or edited.duration_s is None
    ):
        raise ValueError("duration_s is required in both scenarios when either idle_w is nonzero")
    means = (base.mean_features(base_model), edited.mean_features(edited_model))
    summaries = (_summary(means[0], base_model, None), _summary(means[1], edited_model, None))
    base_correct = summaries[0]["gross_j_per_correct"]
    edited_correct = summaries[1]["gross_j_per_correct"]
    return {
        "schema": "interp-energy-behaviour-scenario/v1",
        "status": "assumption_based_projection_not_measurement",
        "energy_basis": "gross",
        "models": {"base": asdict(base_model), "edited": asdict(edited_model)},
        "assumptions": {"base": asdict(base), "edited": asdict(edited)},
        "base": summaries[0], "edited": summaries[1],
        "per_answer": {name: _estimate(means, q, False) for name, q in metrics.items()},
        "per_correct": {name: _estimate(means, q, True) for name, q in metrics.items()},
        "energy_per_correct_reduction_factor": (
            base_correct / edited_correct if base_correct is not None and edited_correct else None),
        "decode_tokens_per_correct_reduction_factor": (
            summaries[0]["decode_tokens_per_correct"] / summaries[1]["decode_tokens_per_correct"]
            if base.accuracy and edited.accuracy and summaries[1]["decode_tokens_per_correct"] else None),
        "warnings": ["No CIs: scenario percentages and lengths are assumptions, not a sample.",
                     "Context uses the mixture of exposures, not exposure at mean token count.",
                     "Coefficients require calibration for the actual model, dtype, device and boundary."],
        "parameter_references": list(PARAMETER_REFERENCES),
    }
