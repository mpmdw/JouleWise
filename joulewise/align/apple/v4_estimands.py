"""Secondary and print-only estimands added by the ALIGN v4 chair rulings.

This module is deliberately downstream of the registered/frozen analysis.  It
accepts already materialised rows and never imports, mutates, or refits the
alternative desk, calibration, or :mod:`pilot_analysis` registered paths.
Every return value identifies whether it is registered, a check, or print-only.
"""
from __future__ import annotations

from collections import defaultdict
import math
import random
from statistics import fmean, median


H_STAR_GRID = (128, 256, 384, 512, 768, 1024, 1536, 2048)
FROZEN_D_SLOT_KEYS = ("max_episode_decode_tokens", "deadman_s", "max_tokens", "max_turns")


def subturn_h_star(scores, threshold, *, grid=H_STAR_GRID):
    """Registered H*: first exact sub-turn hidden-token count reaching threshold."""
    by_h = {int(h): float(score) for h, score in scores}
    ordered = tuple(int(h) for h in grid)
    reached = next((h for h in ordered if h in by_h and by_h[h] >= threshold), None)
    return {"estimand": "H*_i", "status": "registered_secondary", "h_star": reached,
            "bounded_above": reached is not None, "grid": list(ordered)}


def _quantile(values, probability):
    values = sorted(values)
    if not values:
        return None
    index = (len(values) - 1) * probability
    lo, hi = math.floor(index), math.ceil(index)
    return values[lo] if lo == hi else values[lo] + (index-lo)*(values[hi]-values[lo])


def _crossing(points, probability):
    points = sorted(points)
    for (h0, p0), (h1, p1) in zip(points, points[1:]):
        if p0 >= probability:
            return h0
        if p0 < probability <= p1:
            return h0 + (h1-h0) * (probability-p0) / (p1-p0)
    return points[-1][0] if points and points[-1][1] >= probability else None


def benign_carrier_curve(rows, *, bootstrap_replicates=1000, seed=0):
    """Registered leave-one-carrier-out detection curve and window bootstrap.

    Rows contain ``pair``, ``window``, ``carrier``, ``h`` and ``score``.
    At each H a carrier is detected against rank-ceil(.95*m) of *other*
    carriers' scores at that H. Bootstrap resampling is by whole window.
    """
    def estimate(sample):
        grouped = defaultdict(list)
        for row in sample:
            grouped[(row["pair"], int(row["h"]))].append(row)
        curves = defaultdict(list)
        for (pair, h), group in grouped.items():
            detections = []
            for carrier in group:
                others = sorted(r["score"] for r in group if r["carrier"] != carrier["carrier"])
                if not others:
                    continue
                rank = min(len(others), math.ceil(.95 * len(others)))
                detections.append(carrier["score"] >= others[rank-1])
            if detections:
                curves[pair].append((h, sum(detections)/len(detections)))
        return {pair: {"curve": sorted(points), "H50": _crossing(points, .5),
                       "H90": _crossing(points, .9)} for pair, points in curves.items()}

    point = estimate(rows)
    windows = sorted({r["window"] for r in rows})
    draws = defaultdict(lambda: defaultdict(list))
    rng = random.Random(seed)
    if windows:
        by_window = {w: [r for r in rows if r["window"] == w] for w in windows}
        for _ in range(bootstrap_replicates):
            sampled = []
            for draw, window in enumerate(rng.choices(windows, k=len(windows))):
                sampled.extend({**r, "window": f"{draw}:{window}"} for r in by_window[window])
            for pair, result in estimate(sampled).items():
                for name in ("H50", "H90"):
                    if result[name] is not None:
                        draws[pair][name].append(result[name])
    for pair, result in point.items():
        result["window_cluster_bootstrap"] = {
            name: [_quantile(draws[pair][name], .05), _quantile(draws[pair][name], .95)]
            for name in ("H50", "H90")}
    return {"estimand": "benign_carrier_detection", "status": "registered_secondary",
            "pairs": point, "bootstrap_unit": "window"}


def full_omission_rows(rows, omitted_turn):
    """Print-only real-omission sensitivity, including later prompt/context rows.

    Decode counts are monitor/log counts. P/C counts are runtime counts.  The
    frozen decode-only strip remains untouched; this returns copied rows.
    """
    result = []
    for row in rows:
        turn, kind = row.get("turn"), row.get("kind")
        if turn == omitted_turn and kind in {"reasoning", "decode"}:
            continue
        if turn is not None and turn > omitted_turn and kind in {"P", "C", "prompt", "context"}:
            continue
        result.append(dict(row))
    return {"variant": "full-omission", "status": "print_only",
            "count_sources": {"decode": "monitor_log", "P/C": "runtime"}, "rows": result}


def residual_by_hold_count(rows):
    """Ruling 2e print: residual means grouped by trajectory hold count."""
    groups = defaultdict(list)
    for row in rows:
        groups[(row["trajectory"], int(row["hold_count"]))].append(float(row["residual_j"]))
    return {"status": "print_only", "rows": [
        {"trajectory": key[0], "hold_count": key[1], "mean_residual_j": fmean(values)}
        for key, values in sorted(groups.items())]}


def u6_stability(rows, *, cell_residual_sd):
    """U6 early/late stability with trajectory-clustered standard errors."""
    if cell_residual_sd < 0:
        raise ValueError("cell_residual_sd must be non-negative")
    values = [(float(r["residual_j"]), 1 if r["half"] == "late" else 0,
               r["trajectory"]) for r in rows]
    early = [y for y, late, _ in values if not late]
    late = [y for y, is_late, _ in values if is_late]
    margin = .5 * cell_residual_sd
    if not early or not late or len({c for _, _, c in values}) < 2:
        return {"status": "registered_acceptance", "verdict": "calibration unresolved: imprecise",
                "margin_j": margin, "se_kind": "trajectory_clustered"}
    effect = fmean(late) - fmean(early)
    # Cluster sandwich for the late coefficient in y = intercept + late.
    n0, n1 = len(early), len(late)
    means = (fmean(early), fmean(late))
    meat = [[0., 0.], [0., 0.]]
    for cluster in {c for _, _, c in values}:
        score = [0., 0.]
        for y, is_late, c in values:
            if c == cluster:
                residual = y - means[is_late]
                score[0] += residual
                score[1] += residual * is_late
        for i in range(2):
            for j in range(2):
                meat[i][j] += score[i] * score[j]
    inv = [[1/n0, -1/n0], [-1/n0, 1/n0 + 1/n1]]
    variance = sum(inv[1][i] * meat[i][j] * inv[j][1] for i in range(2) for j in range(2))
    se = math.sqrt(max(0., variance))
    ci = [effect - 1.645*se, effect + 1.645*se]
    verdict = "fail" if abs(effect) > margin else "pass" if ci[0] >= -margin and ci[1] <= margin else "calibration unresolved: imprecise"
    return {"status": "registered_acceptance", "effect_j": effect, "ci90_j": ci,
            "margin_j": margin, "trajectory_clustered_se_j": se,
            "se_kind": "trajectory_clustered", "verdict": verdict}


def d_turn_position_means(rows):
    """Registered D replacement for the underpowered turn-index slope."""
    groups = defaultdict(list)
    for row in rows:
        groups[int(row["turn_position"])].append(float(row["residual_j"]))
    return {"status": "registered_acceptance", "estimand": "per_turn_position_residual_means",
            "means_j": {position: fmean(values) for position, values in sorted(groups.items())}}


def u4_reference(r1_replay_pair, w1_sentinels, d_window_energies):
    """U4 inputs with W1 counted as a window and the ruled multi-run E_ref."""
    reference_runs = [*map(float, r1_replay_pair), *map(float, w1_sentinels)]
    if len(reference_runs) != 4:
        raise ValueError("E_ref requires the R1 replay pair and W1 ordinals 5 and 18")
    windows = {"W1": list(map(float, w1_sentinels))}
    windows.update({str(name): list(map(float, values)) for name, values in d_window_energies.items()})
    return {"status": "registered_acceptance", "E_ref_j": fmean(reference_runs),
            "windows": windows, "window_count": len(windows),
            "sigma_w_30b": {"status": "print_only"}}


def acceptance_labels():
    """Ruled classification; prevents tautologies being presented as evidence."""
    return {"U1(a)": "implementation_check", "U2(b)": "implementation_check",
            "U4": "registered_acceptance", "U6": "registered_acceptance"}


def contrast_delivery(rows, *, delta_slow_c):
    """Manipulation check on admitted temperature or actual G1 waiting."""
    s = [float(r["admission_slow_c"]) for r in rows if r["arm"] == "S" and r.get("admission_slow_c") is not None]
    g = [float(r["admission_slow_c"]) for r in rows if r["arm"] == "G" and r.get("admission_slow_c") is not None]
    g_turns = [wait for r in rows if r["arm"] == "G" for wait in r.get("g1_wait_s_by_turn", [])]
    temperature_effect = fmean(s) - fmean(g) if s and g else None
    waited_fraction = sum(wait > 0 for wait in g_turns)/len(g_turns) if g_turns else None
    delivered = ((temperature_effect is not None and temperature_effect >= delta_slow_c/2)
                 or (waited_fraction is not None and waited_fraction >= .5))
    return {"status": "implementation_check", "delivered": delivered,
            "mean_delta_slow_s_minus_g_c": temperature_effect,
            "arm_g_g1_wait_fraction": waited_fraction}


def contrast_verdict(rows, *, delta_slow_c, effect_floor_j=10):
    """Stage-adjusted ruled contrast verdict (secondary v4 code path)."""
    delivery = contrast_delivery(rows, delta_slow_c=delta_slow_c)
    base = {"status": "registered_acceptance", "delivery": delivery,
            "model": "energy ~ arm * template + stage", "df": len(rows)-5}
    if not delivery["delivered"]:
        return {**base, "verdict": "treatment not delivered"}
    cells = defaultdict(list)
    stage_means = defaultdict(list)
    for row in rows:
        stage_means[row["stage"]].append(float(row["energy_j"]))
    grand = fmean(float(row["energy_j"]) for row in rows)
    for row in rows:
        adjusted = float(row["energy_j"]) - fmean(stage_means[row["stage"]]) + grand
        cells[(row["template"], row["arm"])].append(adjusted)
    if any((template, arm) not in cells for template in ("X", "Y") for arm in ("S", "G")):
        return {**base, "verdict": "INCONCLUSIVE", "reason": "missing contrast cell"}
    effects = {template: fmean(cells[(template, "S")])-fmean(cells[(template, "G")])
               for template in ("X", "Y")}
    d = fmean(effects.values())
    same_positive = all(value >= effect_floor_j for value in effects.values()) and d > 0
    verdict = "T CONFIRMED" if same_positive else "T REJECTED" if all(abs(v) < effect_floor_j for v in effects.values()) else "INCONCLUSIVE"
    return {**base, "verdict": verdict, "d_template_j": effects, "d_j": d}


def d_configuration_assertion(members):
    """Require one frozen four-slot cohort across held-out D1-Dn members."""
    keys = []
    for member in members:
        configuration = member.get("configuration", {})
        keys.append(tuple(configuration.get(name) for name in FROZEN_D_SLOT_KEYS))
    unique = sorted(set(keys), key=repr)
    ok = bool(keys) and len(unique) == 1 and None not in unique[0]
    return {"status": "implementation_check", "slot_keys": list(FROZEN_D_SLOT_KEYS),
            "configuration_keys": [list(key) for key in unique], "one_cohort": ok,
            "instrument_ok": ok,
            "rule": "any slot change starts a new cohort"}


def conformal_threshold_diagnostics(rows, *, confidence=.90):
    """Registered FPR wording inputs and print-only stability diagnostics."""
    scores = sorted(float(row["score"]) for row in rows)
    m = len(scores)
    if m < 2:
        raise ValueError("at least two benign scores are required")
    rank_m, rank_m_minus_1 = scores[-1], scores[-2]
    by_window = defaultdict(list)
    for row in rows:
        by_window[row["window"]].append(float(row["score"]))
    pooled_ranks = {}
    for index, value in enumerate(sorted((float(r["score"]), i) for i, r in enumerate(rows)), 1):
        pooled_ranks[value[1]] = index
    n = m
    rank_sums = defaultdict(float)
    counts = defaultdict(int)
    for i, row in enumerate(rows):
        rank_sums[row["window"]] += pooled_ranks[i]
        counts[row["window"]] += 1
    h = 12/(n*(n+1))*sum(rank_sums[w]**2/counts[w] for w in counts)-3*(n+1)
    ratio = math.inf if rank_m_minus_1 == 0 else rank_m/rank_m_minus_1
    alpha = 1-confidence
    return {"status": "registered_secondary",
            "fpr_statement": (f"Marginal FPR <= 1/(m+1) = {1/(m+1):.6g}; "
                              f"with {confidence:.0%} confidence, realized FPR <= "
                              f"1-{alpha:.6g}^(1/m) = {1-alpha**(1/m):.6g}."),
            "marginal_fpr_bound": 1/(m+1),
            "realized_fpr_upper": 1-alpha**(1/m),
            "mde": {"rank_m": rank_m, "rank_m_minus_1": rank_m_minus_1},
            "threshold_instability_flag": ratio > 1.5,
            "threshold_to_next_ratio": ratio,
            "window_heterogeneity": {"test": "Kruskal-Wallis", "H": h,
                "per_window_medians": {w: median(v) for w, v in sorted(by_window.items())},
                "status": "print_only"}}


def sentinel_admissibility(member):
    """Ruled sentinel admission and pre-named fallback metadata."""
    flags = list(member.get("x_flags", ()))
    completed = member.get("status") == "completed"
    turns = int(member.get("turns", 0))
    admissible = completed and not flags and turns >= 3
    return {"status": "implementation_check", "admissible": admissible,
            "requirements": {"completed": completed, "no_x_flags": not flags,
                             "at_least_three_turns": turns >= 3},
            "alternate": {"seed": 93, "pair": "bank", "condition": "benign",
                          "index_role": "development"},
            "predecessor_disclosure": "late sentinel follows a D member"}


def warm_reference_diagnostic(reference_sensors, r1_soak_sensors, gate_rows):
    """Print-only R-minus-soak and gate-wait-by-ordinal diagnostic."""
    sensors = sorted(set(reference_sensors) | set(r1_soak_sensors))
    differences = {sensor: (None if reference_sensors.get(sensor) is None
                            or r1_soak_sensors.get(sensor) is None
                            else float(reference_sensors[sensor])-float(r1_soak_sensors[sensor]))
                   for sensor in sensors}
    table = []
    for row in sorted(gate_rows, key=lambda item: item["ordinal"]):
        table.append({"ordinal": int(row["ordinal"]), "G0_wait_s": row.get("G0_wait_s"),
                      "G1_wait_s": row.get("G1_wait_s")})
    observed = [value for value in differences.values() if value is not None]
    return {"status": "print_only", "R_minus_R1_soak_c": differences,
            "thermal.reference_warm": bool(observed) and any(value > 0 for value in observed),
            "wait_against_ordinal": table,
            "reference_capture_rule": "unchanged: four anchors then ordinal 5"}
