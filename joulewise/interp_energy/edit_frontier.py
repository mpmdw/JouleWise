"""Exploratory, cap-conditional energy/capability frontiers from supplied items.

Reuses the behaviour channel's prefill/decode/integrated-context law. No model
loading, measurement discovery, calibration fitting or optional imports occur.
See docs/design/interp_energy_edit_frontier.md for estimands and limitations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
from typing import Mapping, Sequence

from .behaviour_channel import Answer, EnergyModel, answer_energy, summarize_answers


WU_REFERENCE = {
    "authors": "Wu, Han, Ruf, Grari, Detyniecki",
    "title": "Prefill, Decode, and Context: A Measured Energy Law for Agentic LLM Serving",
    "venue": "NeurIPS 2026 workshop",
    "url": "https://neurips.cc/virtual/2026/170701",
    "provenance": "Repository study checks, section 13; not independently fetched by this tool",
}


@dataclass(frozen=True)
class Variant:
    """One variant, one attempt per independent problem and one explicit cap.

    Observations, if supplied, are full-window gross joules on the report's
    physical boundary. Their source is opaque text and is never dereferenced.
    All variants in a report must have observations or all must omit them.
    """

    name: str
    cap_tokens: int
    model: EnergyModel
    answers: Sequence[Answer]
    observed_gross_j: Mapping[str, float] | None = None
    observation_source: str | None = None

    def __post_init__(self) -> None:
        _text("variant name", self.name)
        if type(self.cap_tokens) is not int or self.cap_tokens <= 0:
            raise ValueError("cap_tokens must be a positive integer")
        if not isinstance(self.model, EnergyModel):
            raise ValueError("model must be an EnergyModel")
        answers = tuple(self.answers)
        if len(answers) < 2 or any(not isinstance(a, Answer) for a in answers):
            raise ValueError("each variant needs at least two Answer instances")
        ids = {a.problem_id for a in answers}
        if len(ids) != len(answers):
            raise ValueError("problem_id must be unique; repeated seeds need cluster analysis")
        if any(a.decode_tokens > self.cap_tokens for a in answers):
            raise ValueError("decode_tokens exceeds the variant cap_tokens")
        object.__setattr__(self, "answers", answers)
        if self.observed_gross_j is None:
            if self.observation_source is not None:
                raise ValueError("observation_source requires observed_gross_j")
        else:
            _text("observation_source", self.observation_source)
            if not isinstance(self.observed_gross_j, Mapping) or set(self.observed_gross_j) != ids:
                raise ValueError("observed_gross_j must match the exact problem_id roster")
            values = dict(self.observed_gross_j)
            for value in values.values():
                if (isinstance(value, bool) or not isinstance(value, (int, float))
                        or not math.isfinite(value) or value < 0):
                    raise ValueError("observed gross joules must be finite and nonnegative")
            object.__setattr__(self, "observed_gross_j", values)


def _text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")


def pareto_frontier(points: Mapping[str, tuple[float | None, float]]) -> list[str]:
    """Minimize cost, maximize accuracy; exact ties both survive.

    An undefined J/correct cost (None) is excluded rather than treated as zero.
    This is point-estimate dominance, never a statistical dominance claim.
    """
    valid = {}
    for name, (cost, accuracy) in points.items():
        if not math.isfinite(accuracy) or not 0 <= accuracy <= 1:
            raise ValueError("frontier accuracy must be in [0, 1]")
        if cost is not None:
            if not math.isfinite(cost) or cost < 0:
                raise ValueError("frontier cost must be finite and nonnegative")
            valid[name] = (cost, accuracy)
    return sorted(name for name, (cost, accuracy) in valid.items()
                  if not any(other_cost <= cost and other_accuracy >= accuracy
                             and (other_cost < cost or other_accuracy > accuracy)
                             for other_cost, other_accuracy in valid.values()))


def _quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lo = int(position)
    fraction = position - lo
    return ordered[lo] * (1 - fraction) + ordered[min(lo + 1, len(ordered) - 1)] * fraction


def _interval(estimate: float | None, draws: Sequence[float | None], confidence: float) -> dict:
    undefined = sum(value is None for value in draws)
    result = {"estimate": estimate, "lower": None, "upper": None,
              "resamples": len(draws), "undefined_resamples": undefined}
    if estimate is None or undefined:
        result["status"] = "zero_correct" if estimate is None else "undefined_zero_correct_resamples"
    else:
        tail = (1 - confidence) / 2
        result.update(status="ok", lower=_quantile(draws, tail),
                      upper=_quantile(draws, 1 - tail))
    return result


def _metrics(rows: Sequence[dict], indices: Sequence[int]) -> dict:
    n = len(indices)
    correct = sum(rows[i]["correct"] for i in indices)
    result = {"accuracy": correct / n}
    for source in ("predicted", "observed", "tokens"):
        if source in rows[0]:
            total = math.fsum(rows[i][source] for i in indices)
            result[source + "_per_answer"] = total / n
            result[source + "_per_correct"] = total / correct if correct else None
    return result


def _difference(left: float | None, right: float | None) -> float | None:
    return None if left is None or right is None else left - right


def _comparisons(metrics: Mapping[str, dict], baseline: str) -> dict:
    base = metrics[baseline]
    comparisons = {}
    for name, values in metrics.items():
        if name == baseline:
            continue
        delta = {key: _difference(value, base[key]) for key, value in values.items()}
        if "observed_per_answer" in values:
            for unit in ("answer", "correct"):
                delta["residual_per_" + unit] = _difference(
                    delta["observed_per_" + unit], delta["predicted_per_" + unit])
        comparisons[name] = delta
    return comparisons


def analyze_variants(variants: Sequence[Variant], *, baseline: str, model_id: str,
                     boundary: str, evaluation_id: str, confidence: float = 0.95,
                     bootstrap_samples: int = 2000, seed: int = 0) -> dict:
    """Resample whole matched problems across ALL variants with a shared draw.

    Coordinates get marginal percentile CIs. Frontier inclusion frequencies
    describe bootstrap stability, not posterior probabilities or simultaneous
    confidence sets. Any zero-correct draw withholds the affected ratio CI;
    an incomplete ratio frontier withholds ALL its inclusion frequencies.
    """
    for field, value in (("model_id", model_id), ("boundary", boundary),
                         ("evaluation_id", evaluation_id), ("baseline", baseline)):
        _text(field, value)
    if boundary not in ("dc", "rails", "gpu_rail"):
        raise ValueError("boundary must be dc, rails or gpu_rail")
    if (isinstance(confidence, bool) or not isinstance(confidence, (float, int))
            or not math.isfinite(confidence) or not 0 < confidence < 1):
        raise ValueError("confidence must be strictly between 0 and 1")
    if type(bootstrap_samples) is not int or bootstrap_samples < 100:
        raise ValueError("bootstrap_samples must be an integer >= 100")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    variants = sorted(variants, key=lambda variant: variant.name)
    names = [variant.name for variant in variants]
    if len(variants) < 2 or len(set(names)) != len(names) or baseline not in names:
        raise ValueError("need >=2 uniquely named variants, including the baseline")
    roster = sorted(a.problem_id for a in variants[0].answers)
    has_observations = variants[0].observed_gross_j is not None
    rows = {}
    for variant in variants:
        by_id = {answer.problem_id: answer for answer in variant.answers}
        if set(by_id) != set(roster):
            raise ValueError("all variants must have exactly the same problem_id roster")
        if (variant.observed_gross_j is not None) != has_observations:
            raise ValueError("observations must be supplied for all variants or none")
        if variant.model.coefficient_basis != variants[0].model.coefficient_basis:
            raise ValueError("all variants must use the same coefficient_basis")
        rows[variant.name] = []
        for problem_id in roster:
            answer = by_id[problem_id]
            row = {"correct": answer.correct,
                   "predicted": answer_energy(answer, variant.model)["gross_j"],
                   "tokens": answer.prefill_tokens + answer.decode_tokens}
            if has_observations:
                row["observed"] = variant.observed_gross_j[problem_id]
            rows[variant.name].append(row)
    indices = list(range(len(roster)))
    estimates = {name: _metrics(rows[name], indices) for name in names}
    contrasts = _comparisons(estimates, baseline)
    draws = {name: {key: [] for key in estimates[name]} for name in names}
    contrast_draws = {name: {key: [] for key in values} for name, values in contrasts.items()}
    axes = [key for key in estimates[baseline] if key != "accuracy"]
    hits = {axis: dict.fromkeys(names, 0) for axis in axes}
    invalid_frontiers = dict.fromkeys(axes, 0)
    rng = random.Random(seed)
    for _ in range(bootstrap_samples):
        sample = [rng.randrange(len(roster)) for _ in roster]
        metrics = {name: _metrics(rows[name], sample) for name in names}
        for name, values in metrics.items():
            for key, value in values.items():
                draws[name][key].append(value)
        for name, values in _comparisons(metrics, baseline).items():
            for key, value in values.items():
                contrast_draws[name][key].append(value)
        for axis in axes:
            if any(metrics[name][axis] is None for name in names):
                invalid_frontiers[axis] += 1
                continue
            for name in pareto_frontier({name: (metrics[name][axis], metrics[name]["accuracy"])
                                         for name in names}):
                hits[axis][name] += 1
    frontiers = {}
    for axis in axes:
        invalid = invalid_frontiers[axis]
        frontiers[axis] = {
            "members": pareto_frontier({name: (estimates[name][axis], estimates[name]["accuracy"])
                                        for name in names}),
            "excluded_undefined": [name for name in names if estimates[name][axis] is None],
            "bootstrap_status": "undefined_zero_correct_resamples" if invalid else "ok",
            "undefined_resamples": invalid,
            "inclusion_frequency": {name: None if invalid else hits[axis][name] / bootstrap_samples
                                    for name in names},
        }
    summaries = {}
    for variant in variants:
        summary = summarize_answers(variant.answers, variant.model)
        summaries[variant.name] = {
            "cap_tokens": variant.cap_tokens,
            "cap_hits": sum(a.decode_tokens == variant.cap_tokens for a in variant.answers),
            "n_correct": summary["n_correct"], "n_answers": len(roster),
            "sparse_correct": summary["n_correct"] < 3,
            "energy_model": asdict(variant.model),
            "observation_source": variant.observation_source,
            "behaviour_channel_summary": summary,
            "metrics": {key: _interval(value, draws[variant.name][key], confidence)
                        for key, value in estimates[variant.name].items()},
        }
    warnings = [
        "Exploratory sampling intervals; no hardware validation or claim gate.",
        "J/correct includes ALL supplied attempts' energy, including wrong and cap-hit attempts.",
        "CIs condition on supplied coefficients and omit calibration, meter and systematic errors.",
        "Frontier inclusion frequencies are resampling stability, not confidence of optimality.",
        "Coordinate CIs are marginal, not simultaneous confidence bands for a frontier.",
        "Token counts are a diagnostic; the comparator is the full behaviour-channel law.",
        "Caps are treatment settings: no inference about uncapped completion or other caps.",
    ]
    if any(v["sparse_correct"] for v in summaries.values()):
        warnings.append("Fewer than three correct in a variant; J/correct is sparse and unstable.")
    if any(estimates[name]["accuracy"] in (0, 1) for name in names):
        warnings.append("Boundary accuracy: resampling cannot recover unseen outcomes.")
    if any(variant.model.context_j_per_token_squared == 0 for variant in variants):
        warnings.append("A zero context coefficient asserts no context premium for that variant.")
    if has_observations:
        warnings.append("Observation provenance is caller asserted; residuals do not identify switching.")
    return {
        "schema": "interp-energy-edit-frontier/v1", "status": "exploratory_desk_analysis",
        "energy_basis": "gross", "model_id": model_id, "boundary": boundary,
        "evaluation_id": evaluation_id, "baseline": baseline, "problem_ids": roster,
        "inference": {"sampling_unit": "independent problem_id; one attempt per variant",
                      "paired_across_all_variants": True, "confidence": confidence,
                      "bootstrap_samples": bootstrap_samples, "seed": seed,
                      "coefficient_uncertainty": "not included"},
        "units": {"predicted": "gross J from behaviour law", "observed": "supplied gross J",
                  "tokens": "prefill + decode tokens; no joule conversion"},
        "variants": summaries, "frontiers": frontiers,
        "comparisons_to_baseline": {
            name: {key: _interval(value, contrast_draws[name][key], confidence)
                   for key, value in values.items()} for name, values in contrasts.items()},
        "comparison_sign": "variant minus baseline; residual = observed delta - predicted delta",
        "context_convention": "K = p*d + d*(d-1)/2; one charge per reported decode token",
        "law_reference": WU_REFERENCE, "warnings": warnings,
    }
