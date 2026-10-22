"""Independent arithmetic twin of the registered GAMMA analysis engine.

Written from B5-PLAN sections 7.1--7.3, B6 registration section 9.4,
analysis_engine_trio sections B4--B6/B9--B10, and paper_claim_side_bound.
No production estimator, distribution, multiplicity, or claim code is imported.
This module accepts already selected, authenticated kept units; it cannot issue
claims or authenticate exclusions, floors, manifests, or measurement evidence.
All comparisons in its companion tests use synthetic worlds.
"""

from dataclasses import dataclass, field
from math import exp, fsum, isfinite, lgamma, log, log1p, sqrt
from statistics import mean, stdev
from typing import Mapping, Sequence


def _beta_fraction(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta, evaluated by modified Lentz."""
    tiny = 1e-300
    c = 1.0
    d = 1.0 - (a + b) * x / (a + 1.0)
    d = 1.0 / (d if abs(d) > tiny else tiny)
    value = d
    for k in range(1, 1001):
        for numerator in (
            k * (b - k) * x / ((a + 2*k - 1) * (a + 2*k)),
            -(a + k) * (a + b + k) * x / ((a + 2*k) * (a + 2*k + 1)),
        ):
            d = 1.0 + numerator * d
            c = 1.0 + numerator / c
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = c if abs(c) > tiny else tiny
            change = c * d
            value *= change
        if abs(change - 1.0) < 2e-15:
            return value
    raise ArithmeticError("incomplete beta did not converge")


def _beta(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    front = exp(lgamma(a+b) - lgamma(a) - lgamma(b)
                + a*log(x) + b*log1p(-x))
    if x < (a+1) / (a+b+2):
        return front * _beta_fraction(a, b, x) / a
    return 1 - front * _beta_fraction(b, a, 1-x) / b


def t_two_sided(statistic: float, df: int) -> float:
    if df < 1 or statistic != statistic:
        raise ValueError("invalid Student-t arguments")
    return _beta(df/2, 0.5, df/(df + statistic*statistic))


def t_critical(df: int, *, rounded: bool = True) -> float:
    """0.975 quantile; registered contrast CI rounds it to three places."""
    if df < 1:
        raise ValueError("positive degrees of freedom required")
    lo, hi = 0.0, 1.0
    while t_two_sided(hi, df) > 0.05:
        hi *= 2
    for _ in range(90):
        mid = (lo + hi) / 2
        if t_two_sided(mid, df) > 0.05:
            lo = mid
        else:
            hi = mid
    answer = (lo + hi) / 2
    return round(answer, 3) if rounded else answer


@dataclass(frozen=True)
class Run:
    energy: float
    # Only governed, independent stochastic variances belong here. For the
    # registered phase metrics this is zero; empirical scatter is not added.
    variance: float = 0.0
    bounds: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Block:
    key: str
    a: tuple[Run, ...]
    b: tuple[Run, ...]
    # Explicit contrast bounds replace summed arm bounds of the same kind.
    contrast_bounds: Mapping[str, float] = field(default_factory=dict)
    covariance: float = 0.0  # covariance of the two arm means, when declared


@dataclass(frozen=True)
class Estimate:
    n: int
    point: float
    sd: float
    se_repeat: float
    se_metrology: float
    se_total: float
    ci: tuple[float, float]
    repeat_ci: tuple[float, float]
    bounds: Mapping[str, float]
    decision: tuple[float, float]
    p: float

    @property
    def direction(self) -> str:
        return "positive" if self.point > 0 else "negative" if self.point < 0 else "zero"


def estimate(blocks: Sequence[Block]) -> Estimate:
    """B-A arm means with block-level df, variance, and deterministic bounds."""
    n = len(blocks)
    if n < 2 or len({b.key for b in blocks}) != n:
        raise ValueError("at least two distinct complete blocks required")
    differences, variances, by_kind = [], [], {}
    for block in blocks:
        if not block.a or not block.b:
            raise ValueError("incomplete block")
        for run in (*block.a, *block.b):
            if not isfinite(run.energy) or not isfinite(run.variance) or run.variance < 0:
                raise ValueError("nonfinite energy or invalid variance")
            if any(not isfinite(x) or x < 0 for x in run.bounds.values()):
                raise ValueError("invalid bound")
        if any(not isfinite(x) or x < 0 for x in block.contrast_bounds.values()):
            raise ValueError("invalid contrast bound")
        differences.append(mean(r.energy for r in block.b) - mean(r.energy for r in block.a))
        v = (fsum(r.variance for r in block.a)/len(block.a)**2
             + fsum(r.variance for r in block.b)/len(block.b)**2
             - 2*block.covariance)
        if not isfinite(v) or v < 0:
            raise ValueError("invalid contrast variance")
        variances.append(v)
        kinds = set(block.contrast_bounds)
        for run in (*block.a, *block.b):
            kinds.update(run.bounds)
        for kind in kinds:
            bound = block.contrast_bounds.get(kind)
            if bound is None:
                bound = (mean(r.bounds.get(kind, 0.0) for r in block.a)
                         + mean(r.bounds.get(kind, 0.0) for r in block.b))
            by_kind.setdefault(kind, []).append(bound)
    point, sd = mean(differences), stdev(differences)
    se_repeat, se_metrology = sd/sqrt(n), sqrt(fsum(variances))/n
    se_total = sqrt(se_repeat**2 + se_metrology**2)
    critical = t_critical(n-1)
    ci = (point-critical*se_total, point+critical*se_total)
    repeat_ci = (point-critical*se_repeat, point+critical*se_repeat)
    bounds = {kind: fsum(values)/n for kind, values in sorted(by_kind.items())}
    total = fsum(bounds.values())
    p = t_two_sided(point/se_total, n-1) if se_total else (0.0 if point else 1.0)
    return Estimate(n, point, sd, se_repeat, se_metrology, se_total, ci,
                    repeat_ci, bounds, (ci[0]-total, ci[1]+total), p)


def adjust(pvalues: Mapping[str, float | None], m: int, method: str = "holm") -> dict[str, float | None]:
    """Frozen family size is retained when a member is not estimable."""
    if m != len(pvalues) or m < 1 or method not in {"holm", "bh"}:
        raise ValueError("invalid frozen family")
    if any(p is not None and (not isfinite(p) or not 0 <= p <= 1) for p in pvalues.values()):
        raise ValueError("invalid p-value")
    ordered = sorted((p, key) for key, p in pvalues.items() if p is not None)
    result = dict.fromkeys(pvalues)
    if method == "holm":
        running = 0.0
        for rank, (p, key) in enumerate(ordered, 1):
            running = min(1.0, max(running, (m-rank+1)*p))
            result[key] = running
    else:
        running = 1.0
        for rank in range(len(ordered), 0, -1):
            p, key = ordered[rank-1]
            running = min(running, m*p/rank)
            result[key] = running
    return result


NOT_ESTIMABLE = frozenset({
    "analysis_manifest_invalid", "analysis_manifest_not_frozen", "order_manifest_hash_mismatch",
    "floor_artifact_invalid", "metric_missing_or_nonfinite", "insufficient_complete_blocks",
    "runtime_token_denominator_required", "stop_reason_required", "output_policy_required",
    "tokenizer_identity_mismatch",
})


def outcome(value: Estimate | None, floor: float | None, adjusted_p: float | None,
            *, reasons: Sequence[str] = (), alpha: float = 0.05) -> str:
    """B5-PLAN 7.2. Caller supplies evidence-gate reasons, never raw evidence."""
    if value is None or NOT_ESTIMABLE.intersection(reasons):
        return "not_estimable"
    # This arithmetic API accepts only blocking input-gate reasons. Sensitivity
    # and exploratory-demotion concerns are handled separately by family().
    if reasons or floor is None:
        return "not_resolvable"
    if not isfinite(floor) or floor < 0:
        raise ValueError("invalid floor")
    interpolation = value.bounds.get("E_interpolation_joint_edge_bound_j", 0.0)
    ci_zero = value.ci[0] <= 0 <= value.ci[1]
    decision_zero = value.decision[0] <= 0 <= value.decision[1]
    if (abs(value.point) <= floor or interpolation >= floor
            or interpolation >= abs(value.point)/2 or decision_zero and not ci_zero):
        return "not_resolvable"
    if ci_zero or adjusted_p is None or adjusted_p > alpha:
        return "unresolved"
    return "direction_supported"


def family(contrasts: Mapping[str, Sequence[Block]], floors: Mapping[str, float | None],
           *, confirmatory: bool = True, current: bool = True) -> dict[str, dict]:
    """Full frozen family plus family-wide leave-one-block-out and L2 ceiling.

    Contrasts use the registered positive direction. Keys shared between
    contrasts identify the same block and are omitted together in LOO.
    """
    def compute(inputs):
        estimates = {key: estimate(rows) if len(rows) >= 2 else None for key, rows in inputs.items()}
        adjusted = adjust({key: v.p if v else None for key, v in estimates.items()}, len(inputs))
        return {key: {"estimate": v, "adjusted_p": adjusted[key],
                      "outcome": outcome(v, floors[key], adjusted[key])}
                for key, v in estimates.items()}

    results = compute(contrasts)
    for key, rows in contrasts.items():
        original = results[key]
        v, floor = original["estimate"], floors[key]
        loo = []
        if v is not None and len(rows) <= 10:
            for block in rows:
                reduced = {cid: [b for b in bs if b.key != block.key] for cid, bs in contrasts.items()}
                replicate = compute(reduced)[key]
                rv = replicate["estimate"]
                triggers = []
                if rv is None:
                    triggers.append("outcome")
                else:
                    if rv.direction != v.direction:
                        triggers.append("sign")
                    if floor is not None:
                        if (abs(rv.point) > floor) != (abs(v.point) > floor):
                            triggers.append("floor")
                        if abs(rv.point-v.point) > 0.25*floor:
                            triggers.append("magnitude")
                    if (replicate["adjusted_p"] <= 0.05) != (original["adjusted_p"] <= 0.05):
                        triggers.append("adjusted_verdict")
                    if replicate["outcome"] != original["outcome"]:
                        triggers.append("outcome")
                loo.append({"omitted": block.key, **replicate, "triggers": triggers})
        influential = any(set(row["triggers"])-{"magnitude"} for row in loo)
        original["loo"] = loo
        original["ceiling"] = ("L2" if v and original["outcome"] == "direction_supported"
                               and v.point > 0 and confirmatory and current and not influential else "L1")
    return results


def descriptive(blocks: Sequence[Block], tokens: int) -> dict:
    """B5-PLAN 7.3: exact-t geometric ratio and constant-token differences."""
    if tokens <= 0:
        raise ValueError("positive registered token count required")
    value = estimate(blocks)
    logs = []
    for block in blocks:
        a, b = mean(r.energy for r in block.a), mean(r.energy for r in block.b)
        if min(a, b) <= 0:
            raise ValueError("positive arm energies required for log ratio")
        logs.append(log(b/a))
    center = mean(logs)
    half = t_critical(len(blocks)-1, rounded=False)*stdev(logs)/sqrt(len(blocks))
    return {"ratio": exp(center), "ratio_interval": (exp(center-half), exp(center+half)),
            "per_token": value.point/tokens,
            "per_token_ci": tuple(x/tokens for x in value.ci),
            "per_token_decision": tuple(x/tokens for x in value.decision)}
