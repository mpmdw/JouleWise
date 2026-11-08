"""Synthetic challenge planning, never a registration or a model-artifact reader.

The unit for binary power is an independent COPY decision, not a replay, meter
sample, or seed of the same edited artifact. Normal equivalence arithmetic is
kept separate from exact binomial forced-choice power.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
from statistics import NormalDist

from ._common import canonical_sha256


def _count(name, value, minimum=1):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def _positive(name, value, allow_zero=False):
    if not math.isfinite(value) or value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"invalid {name}")


def _binomial_probabilities(n, p):
    """Mode-centered recursion avoids underflow of the initial p**n term."""
    mode = min(n, math.floor((n + 1) * p))
    values = [0.0] * (n + 1)
    values[mode] = math.exp(math.lgamma(n + 1) - math.lgamma(mode + 1)
                            - math.lgamma(n - mode + 1)
                            + mode * math.log(p) + (n - mode) * math.log1p(-p))
    for k in range(mode, 0, -1):
        values[k - 1] = values[k] * k / (n - k + 1) * (1 - p) / p
    for k in range(mode, n):
        values[k + 1] = values[k] * (n - k) / (k + 1) * p / (1 - p)
    return values


def binomial_tail(n: int, probability: float, successes: int) -> float:
    """P[X >= successes], including the all-successes and impossible cutoffs."""
    _count("n", n)
    _count("successes", successes, 0)
    if not 0 < probability < 1:
        raise ValueError("probability must be strictly between zero and one")
    return min(1.0, math.fsum(_binomial_probabilities(n, probability)[successes:]))


@dataclass(frozen=True)
class BinaryPlan:
    copies_per_class: int
    reject_at_successes: int
    null_probability: float
    alternative_probability: float
    family_alpha: float
    families: int
    achieved_size: float
    achieved_power: float


def plan_binary(*, null_probability=.5, alternative_probability=.6,
                family_alpha=.05, families=1, target_power=.8, max_copies=5000) -> BinaryPlan:
    """Smallest n with a one-sided exact binomial rejection rule at alpha/m.

    Default: weak forced-choice identification (60%) against chance (50%).
    For a sensitivity calculation one can instead supply .05 versus .15;
    that null FPR must be justified independently, not estimated then fixed.
    """
    _count("families", families)
    _count("max_copies", max_copies)
    if not (0 < null_probability < alternative_probability < 1
            and 0 < family_alpha < 1 and .5 < target_power < 1):
        raise ValueError("invalid probabilities, alpha or target power")
    alpha = family_alpha / families
    for n in range(1, max_copies + 1):
        probs = _binomial_probabilities(n, null_probability)
        size, critical = 0.0, n + 1
        for k in range(n, -1, -1):
            candidate = size + probs[k]
            if candidate > alpha:
                break
            size, critical = candidate, k
        power = binomial_tail(n, alternative_probability, critical)
        if power >= target_power:
            return BinaryPlan(n, critical, null_probability, alternative_probability,
                              family_alpha, families, size, power)
    raise ValueError("power target exceeds max_copies; no undersized plan returned")


def equivalence_power(*, copies: int, replays_per_copy: int, sessions: int,
                      margin_j: float, systematic_bound_j: float,
                      pair_sd_j=2.97, copy_sd_j=.3, session_sd_j=4.7, alpha=.05) -> dict:
    """Known-SD normal TOST power at true zero with balanced crossed sessions.

    Var(mean) = pair_sd²/(C*R) + copy_sd²/C + session_sd²/S.
    Assumes ideal balanced session weights and a connected crossed design;
    each copy can visit a subset of sessions. With unequal session weights,
    replace 1/S by sum(weight_s**2) in the session term before using the plan.
    A fixed systematic bound consumes margin and NEVER averages down.
    Unknown SD, sparse sessions or nested/unbalanced designs require another
    estimator; this is a sensitivity calculation, not a claim test.
    """
    for name, value in (("copies", copies), ("replays_per_copy", replays_per_copy),
                        ("sessions", sessions)):
        _count(name, value)
    if sessions > copies * replays_per_copy:
        raise ValueError("more sessions than replay pairs")
    _positive("margin_j", margin_j)
    for name, value in (("systematic_bound_j", systematic_bound_j),
                        ("pair_sd_j", pair_sd_j), ("copy_sd_j", copy_sd_j),
                        ("session_sd_j", session_sd_j)):
        _positive(name, value, True)
    if not 0 < alpha < .5:
        raise ValueError("alpha must be between zero and .5")
    se = math.sqrt(pair_sd_j**2 / (copies * replays_per_copy)
                   + copy_sd_j**2 / copies + session_sd_j**2 / sessions)
    available = margin_j - systematic_bound_j
    z = NormalDist().inv_cdf(1 - alpha)
    power = (max(0.0, 2 * NormalDist().cdf(available / se - z) - 1) if se
             else float(available > 0))
    return {"status": "NORMAL_KNOWN_SD_PLANNING_ONLY", "power_at_true_zero": power,
            "standard_error_j": se, "available_margin_j": available,
            "half_width_plus_bound_j": z * se + systematic_bound_j}


def make_challenge(classes: tuple[str, ...], *, seed: int, replays_per_copy=8,
                   families: int | None = None, alternative_probability=.6,
                   pair_seconds=200.0) -> tuple[dict, dict]:
    """Return analyst roster and SEPARATE curator key, all synthetic.

    The analyst sees opaque IDs and randomized pair slots only. Never give the
    analyst the seed/key: IDs are pseudorandom for reproducible DESK tests,
    not cryptographic concealment from an adversary who knows the seed.
    Every tamper copy has a separate matched sham copy, so prevalence is 1/2.
    pair_seconds includes both members; loading/setup/guards are additional.
    """
    if (not classes or "sham" in classes or len(set(classes)) != len(classes)
            or any(not isinstance(c, str) or not c.strip() for c in classes)):
        raise ValueError("classes must be distinct nonempty names; sham is reserved")
    _count("replays_per_copy", replays_per_copy)
    _positive("pair_seconds", pair_seconds)
    families = len(classes) if families is None else families
    _count("families", families)
    if families < len(classes):
        raise ValueError("multiplicity family cannot omit challenge classes")
    plan = plan_binary(families=families, alternative_probability=alternative_probability)
    rng = random.Random(seed)
    key, ids = {}, []
    for name in classes:
        for _ in range(plan.copies_per_class):
            pair_id = f"{rng.getrandbits(128):032x}"
            for label in (name, "sham"):
                copy_id = f"{rng.getrandbits(128):032x}"
                key[copy_id] = {"class": label, "matched_pair": pair_id,
                                "edit_seed": rng.getrandbits(128)}
                ids.append(copy_id)
    slots = []
    for repeat in range(replays_per_copy):
        order = rng.sample(ids, len(ids))
        slots.extend({"copy_id": copy_id, "repeat": repeat} for copy_id in order)
    public = {"status": "SYNTHETIC_DESIGN_NOT_REGISTERED", "binary_plan": asdict(plan),
              "replays_per_copy": replays_per_copy, "copy_count": len(ids),
              "pair_seconds_assumed": pair_seconds,
              "acquisition_hours_excluding_overhead": len(slots) * pair_seconds / 3600,
              "slots": slots}
    public["roster_sha256"] = canonical_sha256(public)
    return public, {"roster_sha256": public["roster_sha256"], "copies": key}
