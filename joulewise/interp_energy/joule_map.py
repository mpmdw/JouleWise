"""PROVISIONAL fixed-token marginal component energy maps; stdlib-only.

Inputs are already integrated decode-only episode energies, never raw capture
paths. No measurement data, collectors, or model files are opened here. Each
six-member unit contains a randomized palindrome of full/clamped/removed arms.
Interpolate each arm's two observations to a common measured midpoint to remove
linear drift in J/token, even with unequal episode durations. Nonlinear drift,
instrument calibration and clamp overhead remain caller-supplied bounds.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
import math
import random
import re
from statistics import fmean
from typing import Iterable

from ._common import canonical_sha256
from .forced_decode import token_sequence_sha256
from .power import plan_power

SCHEMA = "interp_energy.joule_map.v1"
ARMS = ("full", "clamped", "removed")
TERMS = {"full": (1, 0, 0), "raw_saving": (1, 0, -1),
         "control_shift": (1, -1, 0), "corrected_saving": (0, 1, -1)}


def _number(value, name, *, minimum=0, strict=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite numeric")
    if value < minimum or (strict and value == minimum):
        raise ValueError(f"{name} is out of range")


def _integer(value, name, minimum=1):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


@dataclass(frozen=True)
class Episode:
    """One decode-only member. All supplied bounds are worst-case half-widths.

    Energy/idle may be signed for a precomputed DC-minus-rails residual boundary.
    source_kind is a label, not proof of native validity. Identity strings are
    opaque digests, never locators. replacement_sha256 is shared by all arms of
    a target; differing targets may use different tapes. No per-token samples
    are treated as independent statistical observations.
    """

    stratum_id: str
    boundary: str
    component_id: str
    unit_id: str
    arm: str
    midpoint_s: float
    duration_s: float
    energy_j: float
    idle_w: float
    energy_bound_j: float
    idle_bound_w: float
    output_tokens: int
    context_tokens: int
    prompt_sha256: str
    token_sequence_sha256: str
    replay_policy_sha256: str
    model_weights_sha256: str
    replacement_sha256: str
    source_kind: str

    def __post_init__(self):
        for name in ("stratum_id", "boundary", "component_id", "unit_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} must be nonempty")
        if self.arm not in ARMS:
            raise ValueError("unknown arm")
        if self.source_kind not in ("synthetic", "unvalidated-native"):
            raise ValueError("source_kind must be synthetic or unvalidated-native")
        for name in ("midpoint_s", "energy_bound_j", "idle_bound_w"):
            _number(getattr(self, name), name)
        _number(self.idle_w, "idle_w", minimum=-math.inf)
        _number(self.duration_s, "duration_s", strict=True)
        _number(self.energy_j, "energy_j", minimum=-math.inf)
        if self.midpoint_s < self.duration_s / 2:
            raise ValueError("episode starts before the monotonic time origin")
        if not math.isfinite(self.midpoint_s + self.duration_s / 2):
            raise ValueError("episode end time overflows")
        for name in ("output_tokens", "context_tokens"):
            _integer(getattr(self, name), name)
        for name in ("prompt_sha256", "token_sequence_sha256", "replay_policy_sha256",
                     "model_weights_sha256", "replacement_sha256"):
            if not isinstance(getattr(self, name), str) or not re.fullmatch(
                    r"[0-9a-f]{64}", getattr(self, name)):
                raise ValueError(f"{name} must be a lowercase SHA-256 digest")


def interleaved_plan(component_ids: Iterable[str], n_units: int, *, seed: int = 0) -> list[dict]:
    """Randomize target order per unit and arm order within each palindrome."""
    components = tuple(component_ids)
    if not components or any(not isinstance(c, str) or not c for c in components):
        raise ValueError("nonempty component IDs required")
    if len(set(components)) != len(components):
        raise ValueError("duplicate component IDs")
    _integer(n_units, "n_units")
    rng, rows = random.Random(seed), []
    for unit in range(n_units):
        order = list(components)
        rng.shuffle(order)
        for component in order:
            arms = list(ARMS)
            rng.shuffle(arms)
            for slot, arm in enumerate(arms + arms[::-1]):
                rows.append({"unit_id": f"u{unit:04d}", "component_id": component,
                             "slot": slot, "arm": arm})
    return rows


def _unit(rows):
    rows = sorted(rows, key=lambda r: r.midpoint_s)
    if len(rows) != 6 or tuple(r.arm for r in rows[3:]) != tuple(r.arm for r in rows[:3][::-1]) or set(
            r.arm for r in rows[:3]) != set(ARMS):
        raise ValueError("each unit must be a complete six-member arm palindrome")
    for a, b in zip(rows, rows[1:]):
        if a.midpoint_s >= b.midpoint_s or a.midpoint_s + a.duration_s / 2 > b.midpoint_s - b.duration_s / 2:
            raise ValueError("overlapping or unordered episode intervals")
    target = rows[2].midpoint_s + (rows[3].midpoint_s - rows[2].midpoint_s) / 2
    values, bounds = {}, {}
    for basis in ("gross", "above_idle"):
        arm_values, arm_bounds = [], []
        for arm in ARMS:
            a, b = [r for r in rows if r.arm == arm]
            w = (b.midpoint_s - target) / (b.midpoint_s - a.midpoint_s)
            def value(r):
                result = (r.energy_j - (r.idle_w * r.duration_s if basis == "above_idle" else 0)) / r.output_tokens
                _number(result, "derived energy", minimum=-math.inf)
                return result
            def bound(r):
                result = (r.energy_bound_j + (r.idle_bound_w * r.duration_s if basis == "above_idle" else 0)) / r.output_tokens
                _number(result, "derived bound")
                return result
            arm_values.append(w * value(a) + (1 - w) * value(b))
            arm_bounds.append(w * bound(a) + (1 - w) * bound(b))
        for term, coefficients in TERMS.items():
            key = f"{basis}.{term}"
            values[key] = sum(c * v for c, v in zip(coefficients, arm_values))
            bounds[key] = sum(abs(c) * v for c, v in zip(coefficients, arm_bounds))
            _number(values[key], "derived contrast", minimum=-math.inf)
            _number(bounds[key], "derived contrast bound")
    return (values, bounds, rows[0].midpoint_s - rows[0].duration_s / 2,
            rows[-1].midpoint_s + rows[-1].duration_s / 2)


def _quantile(values, p):
    position = p * (len(values) - 1)
    i = int(position)
    return values[i] + (values[min(i + 1, len(values) - 1)] - values[i]) * (position - i)


def analyze_map(episodes: Iterable[Episode], *, confidence=.95, bootstrap_replicates=2000,
                bootstrap_block_units=1, seed=0, additivity=()) -> dict:
    """Circular moving-block percentile CIs, resampling matched units jointly.

    Each stratum/boundary is separate. All targets in it need the same unit
    roster and identical work/weight identities. A unit is a six-run contrast,
    not a power sample. Choose block length prospectively from a noise pilot;
    length one assumes independent units. At least four resampling blocks are
    required. These are pointwise approximate CIs, not simultaneous intervals,
    claim decisions, detection floors, or a guarantee against schedule drift.

    Optional audit dicts have name, parts (disjoint component IDs), joint, and
    budget_j_per_token. They estimate sum(parts) - joint with paired covariance.
    Systematic bounds widen endpoints linearly and never average down with n.
    """
    _number(confidence, "confidence", strict=True)
    if confidence >= 1:
        raise ValueError("confidence must be below one")
    _integer(bootstrap_replicates, "bootstrap_replicates", 100)
    _integer(bootstrap_block_units, "bootstrap_block_units")
    if bootstrap_replicates * (1 - confidence) / 2 < 5:
        raise ValueError("too few bootstrap replicates for requested confidence tails")
    rows = list(episodes)
    if not rows:
        raise ValueError("episodes must not be empty")
    grouped = defaultdict(list)
    for row in rows:
        if not isinstance(row, Episode):
            raise TypeError("expected Episode records")
        grouped[row.stratum_id, row.boundary].append(row)
    audits = list(additivity)
    maps = []
    for (stratum, boundary), group in sorted(grouped.items()):
        chronological = sorted(group, key=lambda r: r.midpoint_s)
        for a, b in zip(chronological, chronological[1:]):
            if a.midpoint_s >= b.midpoint_s or a.midpoint_s + a.duration_s / 2 > b.midpoint_s - b.duration_s / 2:
                raise ValueError("overlapping episode intervals within stratum/boundary")
        identity_names = ("output_tokens", "context_tokens", "prompt_sha256", "token_sequence_sha256",
                          "replay_policy_sha256", "model_weights_sha256", "source_kind")
        if len({tuple(getattr(r, k) for k in identity_names) for r in group}) != 1:
            raise ValueError("mixed work, policy, weights or source identity within a stratum/boundary")
        cells = defaultdict(lambda: defaultdict(list))
        for row in group:
            cells[row.component_id][row.unit_id].append(row)
        rosters = {frozenset(units) for units in cells.values()}
        if len(rosters) != 1:
            raise ValueError("targets require the same paired unit roster")
        n = len(next(iter(rosters)))
        if n // bootstrap_block_units < 4:
            raise ValueError("at least four resampling blocks required")
        units = {c: {u: _unit(rs) for u, rs in us.items()} for c, us in cells.items()}
        for c, us in cells.items():
            if len({r.replacement_sha256 for rs in us.values() for r in rs}) != 1:
                raise ValueError("replacement tape identity changed within target")
        order = sorted(next(iter(rosters)), key=lambda u: min(us[u][2] for us in units.values()))
        # A cross-target unit must finish before the next unit begins.
        for a, b in zip(order, order[1:]):
            if max(us[a][3] for us in units.values()) > min(us[b][2] for us in units.values()):
                raise ValueError("units overlap/interleave; chronological blocks are ambiguous")
        series = {}
        for c, us in units.items():
            for term in next(iter(us.values()))[0]:
                series[c, term] = ([us[u][0][term] for u in order], [us[u][1][term] for u in order])
        audit_meta = {}
        for audit in audits:
            if not isinstance(audit, dict) or set(audit) != {"name", "parts", "joint", "budget_j_per_token"}:
                raise ValueError("invalid additivity audit fields")
            if not isinstance(audit["parts"], (list, tuple)) or any(
                    not isinstance(c, str) for c in audit["parts"]) or not isinstance(audit["joint"], str):
                raise ValueError("audit parts must be an array of component IDs; joint must be an ID")
            name, parts, joint = audit["name"], tuple(audit["parts"]), audit["joint"]
            if not isinstance(name, str) or not name or name in cells or name in audit_meta:
                raise ValueError("invalid/duplicate audit name")
            if not parts or len(set(parts)) != len(parts) or joint in parts or any(c not in cells for c in (*parts, joint)):
                raise ValueError("audit needs distinct existing parts and a separate joint target")
            _number(audit["budget_j_per_token"], "additivity budget")
            audit_meta[name] = audit
            for basis in ("gross", "above_idle"):
                term = basis + ".corrected_saving"
                series[name, term] = (
                    [sum(series[p, term][0][i] for p in parts) - series[joint, term][0][i] for i in range(n)],
                    [sum(series[p, term][1][i] for p in parts) + series[joint, term][1][i] for i in range(n)])
        rng = random.Random(seed)
        draws = {k: [] for k in series}
        for _ in range(bootstrap_replicates):
            indices = []
            while len(indices) < n:
                start = rng.randrange(n)
                indices.extend((start + j) % n for j in range(bootstrap_block_units))
            indices = indices[:n]
            for key, (values, _) in series.items():
                draws[key].append(fmean(values[i] for i in indices))
        estimates, audit_results = {}, {}
        for (target, term), (values, bounds) in series.items():
            samples = sorted(draws[target, term])
            alpha = (1 - confidence) / 2
            lo, hi = _quantile(samples, alpha), _quantile(samples, 1 - alpha)
            bound = fmean(bounds)
            result = {"j_per_token": fmean(values), "ci": [lo, hi], "systematic_bound_j_per_token": bound,
                      "sensitivity_interval": [lo - bound, hi + bound]}
            if target in audit_meta:
                budget = audit_meta[target]["budget_j_per_token"]
                result["within_budget"] = lo - bound >= -budget and hi + bound <= budget
                audit_results.setdefault(target, {"spec": audit_meta[target]})[term] = result
            else:
                estimates.setdefault(target, {})[term] = result
        maps.append({"stratum_id": stratum, "boundary": boundary, "n_units": n,
                     "identity": {k: getattr(group[0], k) for k in identity_names},
                     "replacement_identities": {c: next(iter(us.values()))[0].replacement_sha256 for c, us in cells.items()},
                     "unit_order": order, "components": estimates, "additivity": audit_results})
    return {"schema": SCHEMA, "status": "PROVISIONAL_DESK_ANALYSIS", "confidence": confidence,
            "ci_scope": "pointwise percentile; no multiplicity or instrument-floor decision",
            "bootstrap_replicates": bootstrap_replicates, "bootstrap_block_units": bootstrap_block_units,
            "seed": seed, "maps": maps}


def synthetic_demo(n_units=12, *, seed=0):
    """Known component costs plus a downstream perturbation; no physical data."""
    costs = {"embedding": .001, "lm_head": .015,
             "layer0.attention": .02, "layer0.mlp": .04, "layer0.joint": .055,
             "layer1.attention": .018, "layer1.mlp": .038}
    schedule = interleaved_plan(costs, n_units, seed=seed)
    rng, rows, now = random.Random(seed + 1), [], 1.0
    identity = {"prompt_sha256": token_sequence_sha256([1, 2, 3]),
                "token_sequence_sha256": token_sequence_sha256([4, 0] * 50),
                "replay_policy_sha256": canonical_sha256({"synthetic_policy": 1}),
                "model_weights_sha256": canonical_sha256({"synthetic_weights": 1}),
                "replacement_sha256": canonical_sha256({"synthetic_zero_tape": 1})}
    for item in schedule:
        c, arm = item["component_id"], item["arm"]
        duration = {"full": 10., "clamped": 10., "removed": 8.}[arm]
        midpoint = now + duration / 2
        # Downstream perturbation +.01 is held identical in clamped/removed.
        net = .3 + (.01 if arm != "full" else 0) - (costs[c] if arm == "removed" else 0)
        net += .000001 * midpoint + rng.gauss(0, .0003)
        rows.append(Episode("tiny-synthetic", "synthetic_dc", c, item["unit_id"], arm,
                            midpoint, duration, 100 * net + 3 * duration, 3., .02, .001,
                            100, 3, **identity, source_kind="synthetic"))
        now += duration + .5
    return rows, [{"name": "nonadditivity", "parts": ["layer0.attention", "layer0.mlp"],
                   "joint": "layer0.joint", "budget_j_per_token": .002}]


def desk_plan():
    """Illustrative planning assumptions, NOT a request for measurement time."""
    sizing = plan_power(effect_fraction=10 / 2000, unit_sd_fraction=3 / 2000,
                        unit_seconds=6 * 100, budget_hours=2,
                        systematic_bound_fraction=2 / 2000)
    return {"schema": SCHEMA, "status": "BANKED_DESK_PLAN", "assumptions": {
        "member_energy_j": 2000, "member_seconds": 100, "unit_members": 6,
        "unit_contrast_sd_j": 3, "target_contrast_j": 10, "systematic_bound_j": 2,
        "note": "Illustrative only; fresh A/A and clamp-null pilot required. No collectors."},
        "power": asdict(sizing), "minimum_analysis_units": 4,
        "example": {"contexts": [512, 4096, 16384], "targets_per_context": 8, "units": 12,
                    "members": 1728, "member_only_hours": 48,
                    "overhead": "warmup, tapes, idle brackets, cooldowns and nulls are additional"}}
