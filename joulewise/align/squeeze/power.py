"""Synthetic power and adaptive frontiers with independent search/test draws.

Each Monte Carlo trial redraws m benign calibration episodes and one held-out
cohort, all sharing one frozen joint score. The adversary sees that trial's
threshold and minimizes joint detection on independent search simulations.
Power SEs use independent trials, not a pooled binomial fiction across cohorts
which share a random threshold. This is grid adaptation, not a universal attack.
"""

from dataclasses import asdict, dataclass
import math

import numpy as np

from .adversary import Attack, MonitorResponse, Noise, attack_effect
from .detection import JointScore, Threshold, finite, pareto_frontier, positive_int, probability
from .residual import Carrier, ResidualModel


def _attacks(attacks):
    attacks = tuple(attacks)
    if not attacks or any(not isinstance(a, Attack) for a in attacks):
        raise ValueError("provide at least one Attack")
    if len({a.name for a in attacks}) != len(attacks):
        raise ValueError("attack names must be unique")
    return attacks


def _effects(model, carrier, attacks, h, monitor):
    effects = tuple(attack_effect(model, carrier, a, h, monitor) for a in attacks)
    shifts = np.array([(e.monitor_shift, e.residual_shift_j) for e in effects])
    if not np.isfinite(shifts).all():
        raise ValueError("nonfinite attack effect")
    return effects, shifts


def _mean_se(values):
    return float(np.mean(values)), float(np.std(values, ddof=1) / math.sqrt(len(values)))


def wilson_interval(successes, n, z=1.959963984540054):
    """Binomial interval for fixed-threshold evaluation only."""
    n = positive_int(n, "n")
    if isinstance(successes, bool) or not isinstance(successes, (int, np.integer)):
        raise ValueError("successes must be an integer")
    if not 0 <= successes <= n:
        raise ValueError("successes must lie in [0, n]")
    if finite(z, "z") <= 0:
        raise ValueError("z must be positive")
    p = successes / n
    denominator = 1 + z*z/n
    center = (p + z*z/(2*n)) / denominator
    radius = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


def continuous_max_cohort_any_fpr(m, n):
    """Exact iid continuous reference, averaged over shared calibration.

    P(at least one alarm in n benign tests) = n/(m+n), not
    1-(1-1/(m+1))**n. Ties can only lower the former probability.
    """
    m, n = positive_int(m, "m"), positive_int(n, "n")
    return n / (m + n)


@dataclass(frozen=True)
class PowerEstimate:
    m: int
    heldout_size: int
    trials: int
    selection_size: int
    hidden_work_tokens: float
    joint_probability: float
    joint_mc_se: float
    monitor_probability: float
    energy_probability: float
    cohort_any_probability: float
    cohort_any_mc_se: float
    cohort_target_fraction: float
    cohort_target_probability: float
    cohort_target_mc_se: float
    marginal_fpr_bound: float
    realized_fpr_upper_90: float
    benign_cohort_any_continuous_reference: float
    chosen_attack_counts: dict
    flags: tuple

    def to_dict(self):
        return asdict(self)


def estimate_power(model: ResidualModel, *, m, heldout_size, hidden_work_tokens,
                   attacks, noise=Noise(), carrier=Carrier(),
                   monitor=MonitorResponse(), trials=512, selection_size=256,
                   target_fraction=0.8, seed=0):
    """Power averaged over calibration uncertainty and grid-adaptive attacks.

    heldout_size is required; there is no inferred or registered default.
    A target_fraction=.8 report gives the probability that at least ceil(.8*n)
    held-out episodes alarm; it is distinct from per-episode .8 power.
    H=0 is a false-alarm control, never a hidden-work detection result.
    """
    m = positive_int(m, "m")
    n = positive_int(heldout_size, "heldout_size")
    trials = positive_int(trials, "trials")
    if trials < 2:
        raise ValueError("at least two trials are needed for a Monte Carlo SE")
    selection_size = positive_int(selection_size, "selection_size")
    target_fraction = probability(target_fraction, "target_fraction", open_interval=True)
    attacks = _attacks(attacks)
    effects, shifts = _effects(model, carrier, attacks, hidden_work_tokens, monitor)
    # Separate streams ensure evaluation is not used for attack selection.
    seeds = np.random.SeedSequence(seed).spawn(3)
    cal_rng, search_rng, test_rng = [np.random.default_rng(s) for s in seeds]
    rule = JointScore(energy_scale_j=noise.residual_sd_j)
    thresholds = np.max(rule(noise.sample(cal_rng, (trials, m))), axis=1)
    search = noise.sample(search_rng, (trials, selection_size))
    rates = np.stack([np.mean(rule(search + shift) > thresholds[:, None], axis=1)
                      for shift in shifts])
    # Stable first-in-grid tie rule is part of this finite search algorithm.
    chosen = np.argmin(rates, axis=0)
    evaluation = noise.sample(test_rng, (trials, n)) + shifts[chosen, None, :]
    channels = rule.channels(evaluation) > thresholds[:, None, None]
    alarms = np.any(channels, axis=-1)
    fractions = alarms.mean(axis=1)
    joint, joint_se = _mean_se(fractions)
    any_probability, any_se = _mean_se(np.any(alarms, axis=1))
    # Fraction arithmetic avoids ceil(.07*100) == 8 caused by binary rounding.
    from fractions import Fraction
    target_count = math.ceil(Fraction(str(target_fraction)) * n)
    target_probability, target_se = _mean_se(alarms.sum(axis=1) >= target_count)
    null_threshold = Threshold(0.0, m, m)
    flags = {"synthetic_only", "grid_adaptive_not_universal", "assumed_monitor_response",
             "iid_episode_model_not_window_validation"}
    if any(p in (0.0, 1.0) for p in (joint, any_probability, target_probability)):
        flags.add("mc_saturation_is_not_certainty")
    for effect in effects:
        flags.update(effect.flags)
    counts = {attack.name: int(np.count_nonzero(chosen == i))
              for i, attack in enumerate(attacks)}
    return PowerEstimate(m, n, trials, selection_size, float(hidden_work_tokens),
                         joint, joint_se, float(channels[..., 0].mean()),
                         float(channels[..., 1].mean()), any_probability, any_se,
                         target_fraction, target_probability, target_se,
                         null_threshold.marginal_fpr_bound,
                         null_threshold.realized_fpr_upper(),
                         continuous_max_cohort_any_fpr(m, n), counts, tuple(sorted(flags)))


def adaptive_frontier(model: ResidualModel, *, threshold: Threshold, attacks,
                      hidden_work_tokens, heldout_size, noise=Noise(),
                      carrier=Carrier(), monitor=MonitorResponse(),
                      selection_size=4096, seed=0):
    """One fixed-threshold frontier, with selection independent of evaluation.

    Threshold must have been calibrated on JointScore(noise.residual_sd_j)
    using an independent benign sample. The Pareto mask is descriptive on
    held-out simulations; it is never used to choose the reported attacker.
    """
    attacks = _attacks(attacks)
    n = positive_int(heldout_size, "heldout_size")
    selection_size = positive_int(selection_size, "selection_size")
    effects, shifts = _effects(model, carrier, attacks, hidden_work_tokens, monitor)
    rule = JointScore(energy_scale_j=noise.residual_sd_j)
    search_seed, test_seed = np.random.SeedSequence(seed).spawn(2)
    search = noise.sample(np.random.default_rng(search_seed), selection_size)
    evaluation = noise.sample(np.random.default_rng(test_seed), n)
    search_rates = [float(np.mean(rule(search + shift) > threshold.value))
                    for shift in shifts]
    chosen = int(np.argmin(search_rates))
    rows = []
    channel_rates = []
    for i, (attack, effect, shift) in enumerate(zip(attacks, effects, shifts)):
        channels = rule.channels(evaluation + shift) > threshold.value
        count = int(np.any(channels, axis=-1).sum())
        mr, er = channels.mean(axis=0)
        channel_rates.append((mr, er))
        rows.append({"attack": attack.name, "effect": asdict(effect),
                     "selection_probability": search_rates[i],
                     "selected_on_search": i == chosen,
                     "monitor_probability": float(mr), "energy_probability": float(er),
                     "joint_probability": count/n, "joint_wilson_95": wilson_interval(count, n),
                     "heldout_size": n})
    for row, front in zip(rows, pareto_frontier(channel_rates)):
        row["pareto_on_evaluation"] = bool(front)
    return rows


def normal_energy_max_power(shift_j, residual_sd_j, m, *, nodes=96):
    """Gaussian one-channel planning reference integrated over max-of-m.

    E[Phi(Z+shift/SD)**m], Z~N(0,1), via Gauss-Hermite quadrature.
    This is not a conformal power guarantee and assumes a fixed variance.
    """
    shift_j = finite(shift_j, "shift_j")
    if finite(residual_sd_j, "residual_sd_j") <= 0:
        raise ValueError("residual_sd_j must be positive")
    m, nodes = positive_int(m, "m"), positive_int(nodes, "nodes")
    if not 8 <= nodes <= 256:
        raise ValueError("quadrature nodes must lie in [8, 256]")
    x, w = np.polynomial.hermite.hermgauss(nodes)
    z = math.sqrt(2)*x + shift_j/residual_sd_j
    cdf = np.array([0.5*math.erfc(-float(v)/math.sqrt(2)) for v in z])
    return float(np.dot(w, cdf**m) / math.sqrt(math.pi))
