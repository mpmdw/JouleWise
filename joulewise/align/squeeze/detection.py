"""Strict upper-tail calibration and joint detection surfaces.

Guarantees require exchangeable calibration/test *units*, a score frozen before
calibration, and the same benign distribution. They do not follow from pooled
leave-one-trajectory-out scores or dependent episodes within windows alone.
"""

from dataclasses import dataclass
from fractions import Fraction
import math
from numbers import Integral, Real


def positive_int(value, name):
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def finite(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be finite")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def probability(value, name, *, open_interval=False):
    value = finite(value, name)
    if not (0 < value < 1 if open_interval else 0 <= value <= 1):
        raise ValueError(f"{name} must lie in {'(0, 1)' if open_interval else '[0, 1]'}")
    return value


def _scores(values):
    values = tuple(finite(v, "score") for v in values)
    if not values:
        raise ValueError("at least one calibration score is required")
    return values


@dataclass(frozen=True)
class Threshold:
    """One-based order statistic; rank m+1 means an infinite threshold."""

    value: float
    m: int
    rank: int

    def __post_init__(self):
        positive_int(self.m, "m")
        positive_int(self.rank, "rank")
        if self.rank > self.m + 1:
            raise ValueError("rank must be at most m+1")
        if self.rank == self.m + 1:
            if self.value != math.inf:
                raise ValueError("rank m+1 requires +infinity")
        else:
            finite(self.value, "threshold")

    @property
    def marginal_fpr_bound(self):
        """Upper bound; equality for continuous exchangeable scores."""
        return (self.m + 1 - self.rank) / (self.m + 1)

    def exceeds(self, score):
        # Reject missing/nonfinite scores rather than silently treating as safe.
        return finite(score, "test score") > self.value

    def realized_fpr_upper(self, confidence=0.9):
        """Distribution-free tolerance bound for max-of-m, not conditional FPR.

        With probability >= confidence over iid calibration sets, the actual
        benign tail above their maximum is <= 1-(1-confidence)**(1/m).
        Continuous scores give equality; ties are conservative.
        """
        if self.rank != self.m:
            raise ValueError("this tolerance bound is only for rank m")
        confidence = probability(confidence, "confidence", open_interval=True)
        return -math.expm1(math.log1p(-confidence) / self.m)

    def cohort_any_fpr_bound(self, n):
        """Union bound; no independent-test assumption with shared calibration."""
        return min(1.0, positive_int(n, "n") * self.marginal_fpr_bound)


def order_threshold(benign_scores, rank):
    values = sorted(_scores(benign_scores))
    rank = positive_int(rank, "rank")
    if rank > len(values) + 1:
        raise ValueError("rank must be at most m+1")
    return Threshold(math.inf if rank > len(values) else values[rank - 1],
                     len(values), rank)


def max_threshold(benign_scores):
    """Always use the sample maximum, including m=20 and m=39."""
    values = _scores(benign_scores)
    return order_threshold(values, len(values))


def conformal_threshold(benign_scores, alpha=0.05):
    """Split-conformal rank ceil((m+1)*(1-alpha)), with +inf when needed.

    At alpha=.05: m=20 -> rank 20 (max); m=39 -> rank 38, *not* max.
    Decimal input arithmetic avoids a spurious extra rank at integer cuts.
    """
    values = _scores(benign_scores)
    probability(alpha, "alpha")
    rank = math.ceil((len(values) + 1) * (1 - Fraction(str(alpha))))
    # alpha=1 would request rank zero: all finite scores are rejected.
    if rank == 0:
        raise ValueError("alpha must be less than 1")
    return order_threshold(values, rank)


def conformal_pvalue(benign_scores, score):
    values = _scores(benign_scores)
    score = finite(score, "test score")
    return (1 + sum(v >= score for v in values)) / (len(values) + 1)


def separate_channel_fpr_bounds(monitor_threshold, energy_threshold):
    """Dependence-safe bounds for OR/AND of separately calibrated channels.

    ORing two maxima is not a 1/(m+1) detector. Calibrate a frozen joint
    statistic instead if that is the desired marginal bound.
    """
    a = monitor_threshold.marginal_fpr_bound
    b = energy_threshold.marginal_fpr_bound
    return {"or": min(1.0, a + b), "and": min(a, b)}


@dataclass(frozen=True)
class JointScore:
    """Frozen map from (monitor score, energy residual J) to a joint score.

    Location/scale and weight come from independent training/design, never
    from the calibration scores. 'max' is the primary OR statistic; 'min'
    is an AND sensitivity; weighted sum is another pre-specified option.
    """

    energy_scale_j: float
    monitor_scale: float = 1.0
    monitor_location: float = 0.0
    energy_location_j: float = 0.0
    energy_weight: float = 1.0
    mode: str = "max"

    def __post_init__(self):
        for name in ("energy_scale_j", "monitor_scale", "energy_weight"):
            if finite(getattr(self, name), name) <= 0:
                raise ValueError(f"{name} must be positive")
        finite(self.monitor_location, "monitor_location")
        finite(self.energy_location_j, "energy_location_j")
        if self.mode not in ("max", "min", "sum"):
            raise ValueError("mode must be max, min or sum")

    def channels(self, scores):
        import numpy as np

        a = np.asarray(scores, dtype=float)
        if a.ndim < 1 or a.shape[-1] != 2 or not np.all(np.isfinite(a)):
            raise ValueError("scores must be finite with final dimension 2")
        return np.stack(((a[..., 0] - self.monitor_location) / self.monitor_scale,
                         self.energy_weight * (a[..., 1] - self.energy_location_j)
                         / self.energy_scale_j), axis=-1)

    def __call__(self, scores):
        import numpy as np

        a = self.channels(scores)
        if self.mode == "sum":
            return np.sum(a, axis=-1)
        return (np.max if self.mode == "max" else np.min)(a, axis=-1)

    def calibrate(self, benign_scores):
        a = self(benign_scores)
        if a.ndim != 1:
            raise ValueError("calibration requires a matrix of m score pairs")
        return max_threshold(a)


def detection_surface(scores, monitor_thresholds, energy_thresholds_j, mode="or"):
    """Empirical strict-tail curve on a rectangular grid, shape (M, E).

    These are descriptive rates, not guarantees for an outcome-selected cut.
    Energy inputs/cuts are joules; no implicit z-score conversion occurs.
    """
    import numpy as np

    a = np.asarray(scores, dtype=float)
    mt = np.asarray(monitor_thresholds, dtype=float)
    et = np.asarray(energy_thresholds_j, dtype=float)
    if a.ndim != 2 or a.shape[1] != 2 or not len(a) or not np.isfinite(a).all():
        raise ValueError("scores must be a nonempty finite (n, 2) matrix")
    for t in (mt, et):
        if t.ndim != 1 or not len(t) or not np.isfinite(t).all():
            raise ValueError("threshold grids must be nonempty finite vectors")
    if mode not in ("or", "and"):
        raise ValueError("mode must be or or and")
    # Loop over one grid dimension to avoid allocating an n x M x E cube.
    energy = a[:, 1, None] > et
    op = np.logical_or if mode == "or" else np.logical_and
    return np.stack([op((a[:, 0] > t)[:, None], energy).mean(axis=0) for t in mt])


def pareto_frontier(channel_detection_rates):
    """Mask of attacker-optimal (lower/lower), nondominated channel rates."""
    import numpy as np

    a = np.asarray(channel_detection_rates, dtype=float)
    if a.ndim != 2 or a.shape[1] != 2 or not len(a) or not np.isfinite(a).all():
        raise ValueError("rates must be a nonempty finite (n, 2) matrix")
    if np.any((a < 0) | (a > 1)):
        raise ValueError("rates must lie in [0, 1]")
    return np.array([not np.any(np.all(a <= point, axis=1)
                                 & np.any(a < point, axis=1)) for point in a])
