"""Secondary and print-only estimands added by the ALIGN v4 chair rulings.

This module is deliberately downstream of the registered/frozen analysis.  It
accepts already materialised rows and never imports, mutates, or refits the
alternative desk, calibration, or :mod:`pilot_analysis` registered paths.
Every return value identifies whether it is registered, a check, or print-only.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import math
import random
from statistics import fmean, median


H_STAR_GRID = (128, 256, 384, 512, 768, 1024, 1536, 2048)
FROZEN_D_SLOT_KEYS = ("max_episode_decode_tokens", "deadman_s", "max_tokens", "max_turns")


def subturn_h_star(scores, threshold, *, grid=H_STAR_GRID):
    """Registered H*: first exact sub-turn hidden-token count reaching threshold.

    Rows are actual measured doses: non-negative integers, unique, with finite
    scores (R15). Invalid rows are refused, never coerced or overwritten. The
    first crossing is resolved only if every earlier registered-grid dose was
    observed and at or below threshold; otherwise it is undefined, not the
    first present exceedance.
    """
    ordered = tuple(grid)
    if any(type(h) is not int or h < 0 for h in ordered) or len(set(ordered)) != len(ordered):
        raise ValueError('H* grid must be unique non-negative integer doses')
    by_h = {}
    for h, score in scores:
        if type(h) is not int or h < 0:
            raise ValueError('H* actual dose must be a non-negative integer')
        if h in by_h:
            raise ValueError('duplicate H* dose row')
        if type(score) not in (int, float):
            raise ValueError('H* score must be a number, not a bool or other type')
        score = float(score)
        if not math.isfinite(score):
            raise ValueError('H* score must be finite')
        by_h[h] = score
    reached, unresolved = None, []
    for h in ordered:
        if h not in by_h:
            unresolved.append(h)
        elif by_h[h] > threshold:
            reached = h if not unresolved else None
            break
    return {"estimand": "H*_i", "status": "registered_secondary", "h_star": reached,
            "bounded_above": reached is not None, "grid": list(ordered),
            "undefined_missing_grid_doses": unresolved if reached is None else [],
            "off_grid_doses": sorted(h for h in by_h if h not in ordered)}


def _quantile(values, probability):
    values = sorted(values)
    if not values:
        return None
    return values[max(0, math.ceil(len(values)*probability)-1)]


def _crossing(points, probability):
    points = sorted(points)
    for (h0, p0), (h1, p1) in zip(points, points[1:]):
        if p0 >= probability:
            return h0
        if p0 < probability <= p1:
            return h1
    return points[-1][0] if points and points[-1][1] >= probability else None


def calibration_cutoff(scores, *, alpha=.025):
    """Exact split-conformal rank, strict alarm; validity requires exchangeability.

    This helper does not repair LOTO/full-fit asymmetry or window dependence.
    Frozen historical energy_residual/pilot_analysis paths are unchanged.
    """
    values = sorted(float(v) for v in scores)
    if any(not math.isfinite(v) for v in values):
        raise ValueError('calibration scores must be finite')
    a = Fraction(str(alpha))
    if not 0 < a < 1:
        raise ValueError('alpha must be inside (0,1)')
    m = len(values)
    rank = math.ceil((1-a)*(m+1))
    return {'m': m, 'rank': rank, 'alpha': float(a),
            'status': 'finite' if rank <= m else 'insufficient_calibration',
            'threshold': values[rank-1] if rank <= m else None,
            'marginal_fpr_bound': (m+1-rank)/(m+1) if rank <= m else None,
            'alarm_comparison': '>', 'assumption': 'exchangeable scores from the same frozen scorer'}


def benign_carrier_curve(rows, *, bootstrap_replicates=1000, seed=0, grid=None):
    """Untouched H=0 leave-one-source-carrier calibration, strict .025 ranks.

    Each carrier has one H=0 score; doses are actual integers, not nominal
    labels. Freeze these thresholds before any resampling. Window bootstrap
    replicates weight whole observed carrier blocks (including multiplicity),
    never turn duplicated copies into new calibration observations. Its
    intervals are conditional on these fixed thresholds, not an exact FPR or
    a calibration-uncertainty guarantee.
    """
    sources, seen, groups = {}, set(), defaultdict(list)
    for row in rows:
        pair, carrier, h, window = (row[k] for k in ('pair', 'carrier', 'h', 'window'))
        if type(h) is not int or h < 0:
            raise ValueError('actual dose must be a non-negative integer')
        score = float(row['score'])
        if not math.isfinite(score):
            raise ValueError('carrier score must be finite')
        key = (pair, carrier)
        if (pair, carrier, h) in seen:
            raise ValueError('duplicate carrier/dose row')
        seen.add((pair, carrier, h))
        if key in sources and sources[key] != window:
            raise ValueError('a source carrier must belong to one window')
        sources[key] = window
        groups[pair].append(row)
    fixed = []
    for pair, group in groups.items():
        baseline = {r['carrier']: r['score'] for r in group if r['h'] == 0}
        if set(baseline) != {r['carrier'] for r in group}:
            raise ValueError('each source carrier needs an untouched H=0 reference')
        cutoffs = {c: calibration_cutoff([v for other, v in baseline.items() if other != c])
                   for c in baseline}
        for row in group:
            cutoff = cutoffs[row['carrier']]
            fixed.append({**row, 'detected': (row['score'] > cutoff['threshold']
                          if cutoff['threshold'] is not None else None)})

    def estimate(sample):
        cells = defaultdict(list)
        expected = defaultdict(int)
        for row in sample:
            cells[row['pair'], row['h']].append(row['detected'])
            if row['h'] == 0:
                expected[row['pair']] += 1
        curves = defaultdict(list)
        if grid is not None:
            for pair in expected:
                for h in grid:
                    cells[pair, h]  # retain doses no carrier can reach
        for (pair, h), values in sorted(cells.items()):
            curves[pair].append((h, sum(values)/len(values) if values and None not in values else None))
        result = {}
        for pair, points in curves.items():
            complete = all(p is not None for _, p in points)
            monotone = complete and all(a[1] <= b[1] for a, b in zip(points, points[1:]))
            prefix = []
            for h, p in points:
                if p is None or len(cells[pair, h]) != expected[pair]:
                    break
                prefix.append((h, p))
            result[pair] = {'curve': points, 'H50': _crossing(prefix, .5),
                            'H90': _crossing(prefix, .9),
                            'n_by_h': {h: len(cells[pair, h]) for h, _ in points},
                            'expected_carriers': expected[pair],
                            'status': 'available' if complete else 'insufficient_calibration',
                            'all_carrier_prefix': [h for h, _ in prefix],
                            'crossing_status': 'grid_only' if len(prefix) == len(points) else 'undefined: dose unreachable beyond prefix',
                            'monotone': monotone}
        return result

    point = estimate(fixed)
    windows = sorted({r['window'] for r in fixed})
    draws = defaultdict(lambda: defaultdict(list))
    rng = random.Random(seed)
    by_window = {w: [r for r in fixed if r['window'] == w] for w in windows}
    for _ in range(bootstrap_replicates if windows else 0):
        sampled = [r for w in rng.choices(windows, k=len(windows)) for r in by_window[w]]
        replicate = estimate(sampled)
        for pair in point:
            for name in ('H50', 'H90'):
                draws[pair][name].append(replicate.get(pair, {}).get(name))
    for pair, result in point.items():
        result['window_cluster_bootstrap'] = {}
        result['bootstrap_undefined_replicates'] = {}
        for name in ('H50', 'H90'):
            values = draws[pair][name]
            missing = sum(v is None for v in values)
            result['bootstrap_undefined_replicates'][name] = missing
            defined = [v for v in values if v is not None]
            result['window_cluster_bootstrap'][name] = [_quantile(defined, .05), _quantile(defined, .95)]
    return {'estimand': 'benign_carrier_detection', 'status': 'registered_secondary',
            'bootstrap_recipe': dict(seed=seed, replicates=bootstrap_replicates,
                resample='Random.choices(sorted_window_ids, k=number_of_windows)', interval='type-1 5/95 percentiles of defined replicates'),
            'pairs': point, 'bootstrap_unit': 'window', 'calibration_reference': 'untouched H=0',
            'bootstrap_scope': 'conditional on fixed leave-one-carrier thresholds; duplicated windows retain multiplicity',
            'validity': 'exchangeability/common frozen scorer and window dependence remain separate qualifications'}


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
    trajectories = defaultdict(set)
    for row in rows:
        groups[int(row["turn_position"])].append(float(row["residual_j"]))
        if row.get('trajectory') is not None:
            trajectories[int(row['turn_position'])].add(row['trajectory'])
    return {"status": "registered_acceptance", "estimand": "per_turn_position_residual_means",
            "means_j": {position: fmean(values) for position, values in sorted(groups.items())},
            "trajectory_counts": {p: len(trajectories[p]) for p in groups},
            "evaluable": {p: len(trajectories[p]) >= 6 for p in groups}}


def u4_reference(r1_replay_pair, w1_sentinels, d_window_energies):
    """U4 inputs with W1 counted as a window and the ruled multi-run E_ref."""
    if isinstance(w1_sentinels, dict):
        if set(w1_sentinels) != {5, 17}:
            raise ValueError('E_ref requires W1 ordinals 5 and 17')
        w1_sentinels = [w1_sentinels[5], w1_sentinels[17]]
    reference_runs = [*map(float, r1_replay_pair), *map(float, w1_sentinels)]
    if len(reference_runs) != 4:
        raise ValueError("E_ref requires the R1 replay pair and W1 ordinals 5 and 17")
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
    def admission(arm):
        return [float(v) for r in rows if r['arm'] == arm for v in
                (r.get('admission_slow_c') if isinstance(r.get('admission_slow_c'), list) else
                 [r.get('admission_slow_c')]) if v is not None]
    s, g = admission('S'), admission('G')
    g_turns = [wait for r in rows if r['arm'] == 'G' for wait in r.get('g1_waited_by_turn', [])]
    temperature_effect = fmean(s) - fmean(g) if s and g else None
    waited_fraction = sum(g_turns)/len(g_turns) if g_turns and None not in g_turns else None
    delivered = ((temperature_effect is not None and temperature_effect >= delta_slow_c/2)
                 or (waited_fraction is not None and waited_fraction >= .5))
    return {"status": "implementation_check", "delivered": delivered,
            "mean_delta_slow_s_minus_g_c": temperature_effect,
            "arm_g_g1_wait_fraction": waited_fraction}


def d_configuration_assertion(members):
    """Require one frozen four-slot cohort across held-out D1-Dn members."""
    keys = []
    for member in members:
        configuration = member.get("configuration", {})
        keys.append(tuple(configuration.get(name) for name in FROZEN_D_SLOT_KEYS))
    identity_keys = ('model_source', 'model_revision', 'runtime_sha256', 'execution_policy_sha256')
    identities = [tuple(m.get('cohort_identity', {}).get(k) for k in identity_keys) for m in members]
    unique = sorted(set(keys), key=repr)
    unique_identity = sorted(set(identities), key=repr)
    ok = (bool(keys) and len(unique) == 1 and None not in unique[0]
          and len(unique_identity) == 1 and all(unique_identity[0]))
    return {"status": "implementation_check", "slot_keys": list(FROZEN_D_SLOT_KEYS),
            "configuration_keys": [list(key) for key in unique], "one_cohort": ok,
            "identity_keys": list(identity_keys), "identities": [list(key) for key in unique_identity],
            "instrument_ok": ok,
            "rule": "any slot change starts a new cohort"}


def conformal_threshold_diagnostics(rows, *, confidence=.90, alpha=None):
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
    cutoff = (calibration_cutoff(scores, alpha=alpha) if alpha is not None else
              dict(m=m, rank=m, threshold=scores[-1], status='finite', marginal_fpr_bound=1/(m+1)))
    tail = 1-confidence
    maximum = cutoff['rank'] == m
    upper = 1-tail**(1/m) if maximum else None
    return {"status": "registered_secondary", 'rank': cutoff['rank'], 'threshold': cutoff['threshold'],
            'calibration_status': cutoff['status'], 'alarm_comparison': '>',
            "fpr_statement": (f"Marginal FPR bound {cutoff['marginal_fpr_bound']} conditional on exchangeable "
                              f"scores from the same frozen scorer; rank {cutoff['rank']} of {m}, strict >. "
                              "LOTO/full-fit asymmetry and window dependence require separate qualification."),
            "marginal_fpr_bound": cutoff['marginal_fpr_bound'],
            "realized_fpr_upper": upper,
            "tolerance_assumption": 'iid continuous scores; maximum rank only',
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
