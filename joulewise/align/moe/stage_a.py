"""Stage A comparison of routing, logged counts, and their combination.

Task groups define both label exchangeability and held-out classifier folds.
All episodes remain in the report; unavailable measurements are flagged.
This is an offline screening analysis, not a registered decision or power claim.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

from joulewise.align.records import Episode, RouterLog, read_episodes
from joulewise.align.moe.stats import episode_stats, grouped_permutation_test, routing_flags

METADATA_FEATURES = ("prefill_tokens", "visible_decode_tokens", "turns", "tool_calls")


@dataclass(frozen=True)
class StatisticResult:
    """Raw difference and standardized difference, each with a cluster-bootstrap CI."""

    effect: float
    interval: tuple[float, float]
    standardized_effect: float
    standardized_interval: tuple[float, float]
    p_value: float
    p_holm: float
    n_perm_used: int
    n_bootstrap_valid: int
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class StageAResult:
    """Episode-aligned evidence and counts-versus-routing held-out comparison."""

    episode_ids: tuple[str, ...]
    labels: tuple[int, ...]
    groups: tuple[str, ...]
    episode_features: tuple[dict[str, float], ...]
    statistics: dict[str, StatisticResult]
    aucs: dict[str, float]
    auc_intervals: dict[str, tuple[float, float]]
    predictions: dict[str, tuple[float, ...]]
    auc_gain: float
    auc_gain_interval: tuple[float, float]
    n_bootstrap: int
    confidence: float
    seed: int
    flags: tuple[str, ...]


def _mean(values: Sequence[float]) -> float:
    return math.fsum(values) / len(values) if values else math.nan


def _difference(values: Sequence[float], labels: Sequence[int]) -> float:
    if any(not math.isfinite(value) for value in values) or any(y not in (0, 1) for y in labels):
        return math.nan
    return _mean([x for x, y in zip(values, labels) if y == 1]) - _mean(
        [x for x, y in zip(values, labels) if y == 0])


def _standardized(values: Sequence[float], labels: Sequence[int]) -> float:
    classes = [[x for x, y in zip(values, labels) if y == label] for label in (0, 1)]
    if any(len(part) < 2 for part in classes) or any(not math.isfinite(x) for x in values):
        return math.nan
    means = [_mean(part) for part in classes]
    variance = math.fsum(math.fsum((x - mean)**2 for x in part)
                         for part, mean in zip(classes, means)) / (len(values) - 2)
    effect = means[1] - means[0]
    if variance == 0:
        return 0.0 if effect == 0 else math.nan
    return effect / math.sqrt(variance)


def mann_whitney_auc(scores: Sequence[float], labels: Sequence[int]) -> float:
    """AUC = P(score_sabotage > score_benign) + half the tie probability.

    The spine has no stats-lane AUC implementation, so this local rank-sum
    implementation is used. It is O(n log n), with exact tie ranks.
    """
    if (len(scores) != len(labels) or any(y not in (0, 1) for y in labels)
            or any(not math.isfinite(x) for x in scores)):
        return math.nan
    n1 = sum(labels)
    n0 = len(labels) - n1
    if not n0 or not n1:
        return math.nan
    ordered = sorted(zip(scores, labels))
    twice_positive_ranks = 0
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and ordered[end][0] == ordered[start][0]:
            end += 1
        twice_rank = (start + 1) + end
        twice_positive_ranks += twice_rank * sum(y for _, y in ordered[start:end])
        start = end
    return (twice_positive_ranks - n1 * (n1 + 1)) / (2 * n0 * n1)


def _quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (position - lower) * (ordered[upper] - ordered[lower])


def _interval(values: Sequence[float], confidence: float) -> tuple[float, float]:
    finite = [x for x in values if math.isfinite(x)]
    if not 0 < confidence < 1:
        return math.nan, math.nan
    alpha = (1 - confidence) / 2
    return _quantile(finite, alpha), _quantile(finite, 1 - alpha)


def _bootstrap_indices(groups: Sequence[str], count: int, seed: int) -> list[tuple[int, ...]]:
    blocks: dict[str, list[int]] = {}
    for index, group in enumerate(groups):
        blocks.setdefault(group, []).append(index)
    choices = list(blocks.values())
    if not choices or count <= 0:
        return []
    rng = random.Random(seed)
    return [tuple(index for _ in choices for index in rng.choice(choices)) for _ in range(count)]


def _held_out_scores(features: Sequence[Sequence[float]], labels: Sequence[int],
                     groups: Sequence[str]) -> tuple[tuple[float, ...], tuple[str, ...]]:
    """Leave-one-task-group-out standardized nearest-centroid classifier.

    Means, missing-value imputation, population standard deviations, and class
    centroids use training rows only. Constant columns receive zero weight.
    There is no tuning, feature selection, or access to held-out labels.
    """
    flags = []
    scores = [math.nan] * len(features)
    for group in dict.fromkeys(groups):
        train = [i for i, value in enumerate(groups) if value != group]
        test = [i for i, value in enumerate(groups) if value == group]
        if not train or set(labels[i] for i in train) != {0, 1}:
            flags.append("held_out_training_class_or_group_missing")
            continue
        dimensions = len(features[0])
        columns = [[features[i][j] for i in train] for j in range(dimensions)]
        centers = [_mean([x for x in column if math.isfinite(x)]) for column in columns]
        centers = [x if math.isfinite(x) else 0.0 for x in centers]
        columns = [[x if math.isfinite(x) else center for x in column]
                   for column, center in zip(columns, centers)]
        scales = [math.sqrt(_mean([(x - center)**2 for x in column]))
                  for column, center in zip(columns, centers)]
        weights = []
        for column, scale in zip(columns, scales):
            difference = _difference(column, [labels[i] for i in train])
            weights.append(difference / scale if scale else 0.0)
        # Difference of squared distances to the two class centroids has the
        # same ordering as this centered linear discriminant.
        class_midpoints = []
        for column in columns:
            class_midpoints.append((_mean([x for x, i in zip(column, train) if labels[i] == 1])
                                    + _mean([x for x, i in zip(column, train) if labels[i] == 0])) / 2)
        for i in test:
            terms = []
            for x, center, midpoint, scale, weight in zip(
                    features[i], centers, class_midpoints, scales, weights):
                if not math.isfinite(x):
                    x = center
                    flags.append("nonfinite_classifier_feature_imputed_from_training")
                terms.append((x - midpoint) / scale * weight if scale else 0.0)
            scores[i] = math.fsum(terms) / dimensions if dimensions else 0.0
    if any(not math.isfinite(x) for row in features for x in row):
        flags.append("nonfinite_classifier_feature_imputed_from_training")
    return tuple(scores), tuple(dict.fromkeys(flags))


def analyze_stage_a(episodes: Sequence[Episode], *, n_bootstrap: int,
                    confidence: float = 0.95, n_perm: int | None = None,
                    seed: int = 0) -> StageAResult:
    """Compute all 12 routing tests, Holm adjustment, effect CIs and held-out AUCs.

    Resample whole task groups with replacement, preserving every episode in a
    chosen group. Percentile intervals use the caller's bootstrap budget.
    AUC intervals resample fixed out-of-fold predictions and are conditional on
    those fitted models; they do not account for classifier-refitting uncertainty.
    Both undefined and valid bootstrap replicate counts are disclosed.
    """
    episodes = tuple(episodes)
    labels = tuple({"benign": 0, "sabotage": 1}.get(e.condition, -1) for e in episodes)
    groups = tuple(e.task_pair for e in episodes)
    flags = []
    if len(set(e.episode_id for e in episodes)) != len(episodes):
        flags.append("duplicate_episode_ids")
    if len(set(e.agent_model for e in episodes)) > 1:
        flags.append("mixed_agent_models_may_confound_routing")
    if not episodes:
        flags.append("no_episodes")
    if set(labels) != {0, 1}:
        flags.append("both_conditions_required_for_inference")
    if len(set(groups)) < 2:
        flags.append("fewer_than_two_task_groups")
    if not isinstance(n_bootstrap, int) or n_bootstrap <= 0:
        flags.append("invalid_bootstrap_budget")
        n_bootstrap = 0
    if not 0 < confidence < 1:
        flags.append("invalid_interval_confidence")
    for group in dict.fromkeys(groups):
        if len({y for y, g in zip(labels, groups) if g == group}) < 2:
            flags.append(f"group_has_no_label_exchangeability:{group}")
    features = []
    keys = tuple(episode_stats(RouterLog("empty", 1, 1, (0,), (), ())))
    for episode in episodes:
        if episode.router_log is None:
            routing = dict.fromkeys(keys, math.nan)
            flags.append(f"{episode.episode_id}:router_log_missing")
        else:
            routing = episode_stats(episode.router_log)
            flags.extend(f"{episode.episode_id}:{flag}" for flag in routing_flags(episode.router_log))
        totals = episode.totals(logged_only=True)
        # hidden_tokens are part of decode_tokens in the shared records contract.
        visible_decode = sum(t.decode_tokens - t.hidden_tokens for t in episode.logged_turns())
        metadata = dict(zip(METADATA_FEATURES,
                            map(float, (totals["prefill_tokens"], visible_decode,
                                        totals["turns"], totals["tool_calls"]))))
        features.append({**routing, **metadata})
        flags.extend(f"{episode.episode_id}:episode_flag:{flag}" for flag in episode.flags)
    bootstrap = _bootstrap_indices(groups, n_bootstrap, seed)
    raw = {}
    for name in keys:
        values = tuple(row[name] for row in features)
        effect, p, used = grouped_permutation_test(values, labels, groups, n_perm=n_perm, seed=seed)
        draws = [_difference([values[i] for i in indices], [labels[i] for i in indices])
                 for indices in bootstrap]
        standardized = [_standardized([values[i] for i in indices], [labels[i] for i in indices])
                        for indices in bootstrap]
        valid = sum(math.isfinite(x) for x in draws)
        local_flags = []
        if not math.isfinite(p):
            local_flags.append("statistic_not_estimable")
        if valid != n_bootstrap:
            local_flags.append(f"undefined_effect_bootstrap_replicates:{n_bootstrap - valid}")
        invalid_standardized = sum(not math.isfinite(x) for x in standardized)
        if invalid_standardized:
            local_flags.append(f"undefined_standardized_bootstrap_replicates:{invalid_standardized}")
        raw[name] = StatisticResult(effect, _interval(draws, confidence), _standardized(values, labels),
                                    _interval(standardized, confidence), p, math.nan, used, valid,
                                    tuple(local_flags))
    # The family always contains all 12 planned tests, even when a phase is
    # unavailable. This prevents missing capture from reducing multiplicity.
    adjusted = {}
    running = 0.0
    ordered = sorted((name for name in keys if math.isfinite(raw[name].p_value)),
                     key=lambda name: raw[name].p_value)
    for rank, name in enumerate(ordered):
        running = max(running, min(1.0, (len(keys) - rank) * raw[name].p_value))
        adjusted[name] = running
    statistics = {name: StatisticResult(**{**asdict(result), "p_holm": adjusted.get(name, math.nan)})
                  for name, result in raw.items()}
    predictions = {}
    aucs = {}
    intervals = {}
    for name, columns in (("metadata", METADATA_FEATURES), ("routing", keys),
                          ("combined", METADATA_FEATURES + keys)):
        matrix = [tuple(row[column] for column in columns) for row in features]
        scores, local_flags = _held_out_scores(matrix, labels, groups)
        flags.extend(f"{name}:{flag}" for flag in local_flags)
        predictions[name] = scores
        aucs[name] = mann_whitney_auc(scores, labels)
        draws = [mann_whitney_auc([scores[i] for i in indices], [labels[i] for i in indices])
                 for indices in bootstrap]
        intervals[name] = _interval(draws, confidence)
        undefined = sum(not math.isfinite(x) for x in draws)
        if undefined:
            flags.append(f"{name}:undefined_auc_bootstrap_replicates:{undefined}")
    gains = [mann_whitney_auc([predictions["combined"][i] for i in indices],
                              [labels[i] for i in indices])
             - mann_whitney_auc([predictions["metadata"][i] for i in indices],
                               [labels[i] for i in indices]) for indices in bootstrap]
    return StageAResult(tuple(e.episode_id for e in episodes), labels, groups, tuple(features),
                        statistics, aucs, intervals, predictions, aucs["combined"] - aucs["metadata"],
                        _interval(gains, confidence), n_bootstrap, confidence, seed,
                        tuple(dict.fromkeys(flags)))


def _json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def main(argv: Sequence[str] | None = None) -> int:
    """Read shared Episode JSONL and print a finite JSON analysis report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episodes", type=Path)
    parser.add_argument("--n-bootstrap", type=int, required=True)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--n-perm", type=int)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)
    result = analyze_stage_a(read_episodes(args.episodes), n_bootstrap=args.n_bootstrap,
                             confidence=args.confidence, n_perm=args.n_perm, seed=args.seed)
    print(json.dumps(_json_safe(asdict(result)), sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["METADATA_FEATURES", "StatisticResult", "StageAResult", "mann_whitney_auc", "analyze_stage_a"]
