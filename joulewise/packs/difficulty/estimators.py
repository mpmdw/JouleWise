"""DIFFICULTY v2 parsing, stratified bootstrap and registered comparisons."""
import csv
import json
import math
import platform
import random
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from statistics import NormalDist, mean

from .score import BENCH_COLUMNS

ENERGY_COLUMNS = ("model", "mode", "level", "item_id", "boundary", "attempt", "energy_j",
                  "prompt_tokens", "generated_tokens", "flags")
CELL_COLUMNS = tuple("variant boundary model mode level cell_status n_bench_target n_bench "
    "k_correct accuracy acc_lo acc_hi mean_generated_tokens_bench cap_hit_rate_bench "
    "loop_rate_bench n_holdout_target n_holdout k_holdout holdout_accuracy "
    "mean_prompt_tokens_holdout mean_generated_tokens_holdout m_energy_target m_energy "
    "mean_energy_j energy_lo_j energy_hi_j model_energy_j epc_model_j epc_model_lo_j "
    "epc_model_hi_j epc_model_status epc_direct_j epc_direct_lo_j epc_direct_hi_j "
    "epc_direct_status epc_j epc_lo_j epc_hi_j epc_status primary_source primary_reason "
    "j_per_token jpt_lo jpt_hi token_mismatch_count rows_not_used replaced_rows".split())
DECOMPOSITION_COLUMNS = tuple("variant boundary model mode N a_j a_se a_lo_j a_hi_j "
    "b_prompt_j_per_tok b_prompt_se b_prompt_lo b_prompt_hi b_gen_j_per_tok b_gen_se "
    "b_gen_lo b_gen_hi r2 r2_gen_only gen_share status".split())
RESIDUAL_COLUMNS = tuple("variant boundary model mode level m mean_residual_j lo_j hi_j "
    "contains_zero boot_lo_j boot_hi_j misfit".split())
PRIMARY_COLUMNS = tuple("variant boundary level a b epc_a_j epc_b_j source_a source_b log_ratio "
    "ratio desc_lo desc_hi dec_lo dec_hi status cheaper reason".split())
RIVAL_COLUMNS = tuple("variant boundary level cheapest rival log_ratio desc_lo desc_hi dec_lo "
    "dec_hi beaten reason".split())
CROSSOVER_COLUMNS = tuple("variant boundary level cheapest cheapest_epc_j status tied incomplete".split())
ALWAYS_EXCLUDE = {"bad_number", "bad_level", "bad_mode", "unknown_item", "unknown_config",
                  "not_selected", "unknown_boundary", "duplicate"}
BENCH_EXCLUDE = ALWAYS_EXCLUDE | {"missing_text"}
VARIANTS = ("primary", "flagged_inclusive")


def _beta_fraction(a, b, x):
    """Lentz continued fraction for the regularized incomplete beta."""
    # Numerical guards: 1e-300 avoids zero divisors with finite reciprocals;
    # 2e-15 (~9 double epsilons) stops the continued fraction well below the
    # registered 1e-6 agreement scale. Neither constant is an agreement bar.
    tiny, eps = 1e-300, 2e-15
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 10001):
        for aa in (m * (b - m) * x / ((qam + 2*m) * (a + 2*m)),
                   -(a + m) * (qab + m) * x / ((a + 2*m) * (qap + 2*m))):
            d = 1 + aa * d
            c = 1 + aa / c
            d = 1 / (d if abs(d) > tiny else tiny)
            c = c if abs(c) > tiny else tiny
            delta = d * c
            h *= delta
        if abs(delta - 1) < eps:
            return h
    return h


def _regularized_beta(x, a, b):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    scale = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                     + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return scale * _beta_fraction(a, b, x) / a
    return 1 - scale * _beta_fraction(b, a, 1 - x) / b


@lru_cache(maxsize=256)
def student_t_quantile(probability, df):
    if not 0 < probability < 1 or df <= 0:
        raise ValueError("t quantile needs 0 < probability < 1 and df > 0")
    if probability == 0.5:
        return 0.0
    if probability < 0.5:
        return -student_t_quantile(1 - probability, df)
    target, lo, hi = 1 - probability, 0.0, 1.0
    def tail(t):
        return 0.5 * _regularized_beta(df / (df + t*t), df / 2, 0.5)
    while tail(hi) > target:
        hi *= 2
    # Numerical stop width: dimensionless t width 1e-13 is seven orders below
    # the 1e-6 agreement bar; the midpoint identity check stops float stagnation.
    while hi - lo > 1e-13:
        mid = (lo + hi) / 2
        if mid == lo or mid == hi:
            break
        if tail(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def wilson(k, n, confidence=0.95):
    if not n:
        return None, None, None
    p, z = k / n, NormalDist().inv_cdf((1 + confidence) / 2)
    denom = 1 + z*z / n
    centre = (p + z*z / (2*n)) / denom
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denom
    return p, max(0.0, centre - half), min(1.0, centre + half)


def mean_interval(values, confidence=0.95):
    m = len(values)
    if m < 2:
        return None, None, None
    avg = mean(values)
    variance = math.fsum((value - avg)**2 for value in values) / (m - 1)
    half = student_t_quantile((1 + confidence) / 2, m - 1) * math.sqrt(variance / m)
    return float(avg), avg - half, avg + half


def energy_per_correct(k, n, energies, confidence=0.95):
    p, p_lo, p_hi = wilson(k, n, confidence)
    avg, lo, hi = mean_interval(energies, confidence)
    epc = epc_lo = epc_hi = None
    if not k:
        status = "not_estimable_zero_correct"
    elif len(energies) < 2:
        status = "not_estimable_few_attempts"
    else:
        epc, d = avg / p, math.log(avg) - math.log(p)
        epc_hi = math.exp(d + math.hypot(math.log(hi / avg), math.log(p / p_lo)))
        if lo <= 0:
            epc_lo, status = 0.0, "energy_lower_nonpositive"
        else:
            epc_lo = math.exp(d - math.hypot(math.log(avg / lo), math.log(p_hi / p)))
            status = "ok"
    return {"mean_energy_j": avg, "energy_lo_j": lo, "energy_hi_j": hi,
            "epc_j": epc, "epc_lo_j": epc_lo, "epc_hi_j": epc_hi, "epc_status": status}


def joules_per_token(energies, tokens, confidence=0.95):
    m, total_g = len(energies), sum(tokens)
    if m < 2 or not total_g:
        return None, None, None
    ratio = math.fsum(energies) / total_g
    variance = math.fsum((e - ratio*g)**2 for e, g in zip(energies, tokens)) / (m - 1)
    se = math.sqrt(variance / (m * (total_g/m)**2))
    half = student_t_quantile((1 + confidence) / 2, m - 1) * se
    return ratio, ratio - half, ratio + half


def decomposition(rows, confidence=0.95):
    n = len(rows)
    fit = dict.fromkeys(DECOMPOSITION_COLUMNS[5:-1])
    fit.update(N=n, status="few_rows" if n < 4 else "singular")
    if n < 4:
        return fit, []
    p, g, e = ([row[key] for row in rows] for key in ("prompt_tokens", "generated_tokens", "energy_j"))
    pm, gm, em = mean(p), mean(g), mean(e)
    pc, gc, ec = ([value - avg for value in values] for values, avg in ((p, pm), (g, gm), (e, em)))
    # Token counts are integers: exact cross-products identify collinearity
    # without a tolerance that could discard an invertible design.
    pp_n = n*sum(x*x for x in p) - sum(p)**2
    gg_n = n*sum(x*x for x in g) - sum(g)**2
    pg_n = n*sum(x*y for x, y in zip(p, g)) - sum(p)*sum(g)
    if pp_n*gg_n - pg_n*pg_n == 0:
        return fit, []
    pp, gg, pg, pe, ge, tss = (math.fsum(x*y for x, y in zip(xs, ys))
                             for xs, ys in ((pc, pc), (gc, gc), (pc, gc), (pc, ec), (gc, ec), (ec, ec)))
    det = pp*gg - pg*pg
    if det <= 0:
        return fit, []
    bp, bg = (pe*gg - ge*pg) / det, (ge*pp - pe*pg) / det
    a = em - bp*pm - bg*gm
    residuals = [y - math.fsum((a, bp*x, bg*z)) for x, z, y in zip(p, g, e)]
    rss = math.fsum(value*value for value in residuals)
    sigma2 = rss / (n - 3)
    a_var = sigma2 * (1/n + (pm*pm*gg - 2*pm*gm*pg + gm*gm*pp)/det)
    fit.update(a_j=a, a_se=math.sqrt(max(0.0, a_var)), b_prompt_j_per_tok=bp,
               b_prompt_se=math.sqrt(sigma2*gg/det), b_gen_j_per_tok=bg,
               b_gen_se=math.sqrt(sigma2*pp/det), r2=1-rss/tss if tss else None,
               r2_gen_only=ge*ge/(gg*tss) if gg and tss else None,
               gen_share=bg*gm/em if em else None, status="ok")
    t = student_t_quantile((1 + confidence) / 2, n - 3)
    for point, se, lo, hi in (("a_j", "a_se", "a_lo_j", "a_hi_j"),
                              ("b_prompt_j_per_tok", "b_prompt_se", "b_prompt_lo", "b_prompt_hi"),
                              ("b_gen_j_per_tok", "b_gen_se", "b_gen_lo", "b_gen_hi")):
        fit[lo], fit[hi] = fit[point] - t*fit[se], fit[point] + t*fit[se]
    by_level = defaultdict(list)
    for row, residual in zip(rows, residuals):
        by_level[row["level"]].append(residual)
    level_rows = []
    for level, values in sorted(by_level.items()):
        avg, lo, hi = mean_interval(values, confidence)
        level_rows.append({"level": level, "m": len(values), "mean_residual_j": float(mean(values)),
                           "lo_j": lo, "hi_j": hi,
                           "contains_zero": int(lo <= 0 <= hi) if lo is not None else None})
    return fit, level_rows


def percentile(values, confidence):
    """Symmetric order statistics, with no interpolation; infinity is allowed."""
    if not values:
        return None, None
    values = sorted(values)
    # Registered §8.7 rounding guard: 1e-9 of one order-statistic rank prevents
    # a float just below an integer from selecting the preceding rank. It is
    # far below one rank and does not round a printed numerical output.
    k = max(1, math.floor(len(values) * (1 - confidence) / 2 + 1e-9))
    return values[k - 1], values[len(values) - k]


def _integer(value):
    if isinstance(value, bool):
        return None
    try:
        text = str(value).strip()
        if re.fullmatch(r"[+-]?[0-9]+", text) is None:
            return None
        number = int(text)
        return number if number >= 0 else None
    except (ValueError, TypeError):
        return None


def _flags(value):
    return {flag.strip() for flag in value.split(";") if flag.strip()} if isinstance(value, str) else set()


def selection_lists(selections):
    """Read only the selection lists; malformed/missing data gives empty lists."""
    source = selections.get("selections", {}) if isinstance(selections, dict) else {}
    result = {}
    for mode in ("off", "on"):
        for role in ("bench", "energy"):
            for level in range(1, 6):
                try:
                    values = source[mode][role][str(level)]
                except (KeyError, TypeError):
                    values = []
                result[mode, role, level] = values if isinstance(values, list) and all(
                    isinstance(value, str) for value in values) else []
    return result


def _selection_check(row, role, config, selected):
    if (row["model"], row["mode"]) not in {(c["model"], c["mode"]) for c in config["configurations"]}:
        row["flags"].add("unknown_config")
    if row["item_id"] not in selected.get((row["mode"], role, row["level"]), set()):
        row["flags"].add("not_selected")


def _parse_common(original, numbers, config, selected, role):
    row = dict(original)
    row["flags"] = _flags(row.get("flags"))
    for key in ("model", "mode", "item_id"):
        row[key] = row.get(key) or ""
    for key in numbers:
        row[key] = _integer(row.get(key))
        if (row[key] is None or (key in ("correct", "cap_hit") and row[key] not in (0, 1))
                or (key == "attempt" and row[key] == 0)):
            row["flags"].add("bad_number")
            if key == "attempt":
                row[key] = None
    row["level"] = _integer(row.get("level"))
    if row["level"] not in range(1, 6):
        row["flags"].add("bad_level")
    if row["mode"] not in ("off", "on"):
        row["flags"].add("bad_mode")
    _selection_check(row, role, config, selected)
    return row


def _row_key(row, role):
    key = row["model"], row["mode"], row["item_id"]
    return (row["boundary"], *key) if role == "energy" else key


def mark_duplicates(rows, role, config):
    """Same-attempt duplicates, then attempts after the first primary usable row."""
    always = BENCH_EXCLUDE if role == "bench" else ALWAYS_EXCLUDE
    # Section 6.2/14.2: keep this policy in one expression for a possible narrowing.
    replaceable_flags = always | set(config["exclude_flags"]) | set(config["physical_exclude_flags"])
    groups, seen = defaultdict(list), set()
    for row in rows:
        if row["attempt"] is None:
            continue
        key = _row_key(row, role)
        attempt_key = key, row["attempt"]
        if attempt_key in seen:
            row["flags"].add("duplicate")
        seen.add(attempt_key)
        groups[key].append(row)
    for group in groups.values():
        ordered = sorted(group, key=lambda row: row["attempt"])
        selected = next((row for row in ordered if not row["flags"] & replaceable_flags), None)
        if selected is not None:
            for row in ordered:
                if row["attempt"] > selected["attempt"]:
                    row["flags"].add("duplicate")
    return rows


def parse_bench(rows, config, selections):
    selected = {key: set(values) for key, values in selection_lists(selections).items()}
    parsed = [_parse_common(row, ("correct", "cap_hit", "prompt_tokens", "generated_tokens", "attempt"),
                            config, selected, "bench") for row in rows]
    return mark_duplicates(parsed, "bench", config)


def parse_energy(rows, bench, config, selections):
    selected = {key: set(values) for key, values in selection_lists(selections).items()}
    lookup = {}
    for row in bench:
        lookup.setdefault((row["model"], row["mode"], row["item_id"]), row)
    parsed = []
    for original in rows:
        row = _parse_common(original, ("prompt_tokens", "generated_tokens", "attempt"), config, selected, "energy")
        row["boundary"] = row.get("boundary") or ""
        if row["boundary"] not in config["boundaries"]:
            row["flags"].add("unknown_boundary")
        try:
            row["energy_j"] = float(row.get("energy_j"))
            if not math.isfinite(row["energy_j"]) or row["energy_j"] <= 0:
                row["flags"].add("bad_number")
        except (TypeError, ValueError, OverflowError):
            row["energy_j"] = None
            row["flags"].add("bad_number")
        reference = lookup.get((row["model"], row["mode"], row["item_id"]))
        if reference is None:
            row["flags"].add("not_in_bench")
        elif (row["generated_tokens"] is not None and reference["generated_tokens"] is not None
              and row["generated_tokens"] != reference["generated_tokens"]):
            row["flags"].add("token_mismatch")
        parsed.append(row)
    return mark_duplicates(parsed, "energy", config)


def used_rows(rows, role, config, variant):
    exclusion = (BENCH_EXCLUDE if role == "bench" else ALWAYS_EXCLUDE) | set(config["exclude_flags"])
    if variant == "primary":
        exclusion |= set(config["physical_exclude_flags"])
    used, keys = [], set()
    for row in sorted(rows, key=lambda row: row["attempt"] if row["attempt"] is not None else math.inf):
        key = _row_key(row, role)
        if key not in keys and not row["flags"] & exclusion:
            used.append(row)
            keys.add(key)
    return used


def _bootstrap_fit(rows):
    """Centred OLS coefficients only, with the same exact token singularity test."""
    n = len(rows)
    if n < 4:
        return None
    p, g, e = ([row[i] for row in rows] for i in range(3))
    sp, sg = sum(p), sum(g)
    pp_n = n*sum(x*x for x in p) - sp*sp
    gg_n = n*sum(x*x for x in g) - sg*sg
    pg_n = n*sum(x*y for x, y in zip(p, g)) - sp*sg
    if pp_n*gg_n - pg_n*pg_n == 0:
        return None
    pm, gm, em = sp/n, sg/n, math.fsum(e)/n
    pc, gc, ec = ([x - avg for x in values] for values, avg in ((p, pm), (g, gm), (e, em)))
    pp, gg, pg, pe, ge = (math.fsum(x*y for x, y in zip(xs, ys))
                         for xs, ys in ((pc, pc), (gc, gc), (pc, gc), (pc, ec), (gc, ec)))
    det = pp*gg - pg*pg
    if det <= 0:
        return None
    bp, bg = (pe*gg - ge*pg)/det, (ge*pp - pe*pg)/det
    return em - bp*pm - bg*gm, bp, bg


def misfit_statistic(energy_mean, prompt_mean, generated_mean, coefficients):
    """Section 8.8: residual mean under the replicate's pooled refit."""
    a, bp, bg = coefficients
    return energy_mean - math.fsum((a, bp*prompt_mean, bg*generated_mean))


def bootstrap(energy, holdout, config, variant, boundary, model, mode):
    """One stream, energies L1..L5 then holdouts L1..L5 on every replicate."""
    rng = random.Random(f"{config['bootstrap']['seed']}/{variant}/{boundary}/{model}/{mode}")
    en = [[(r["prompt_tokens"], r["generated_tokens"], r["energy_j"])
           for r in sorted(energy.get(level, []), key=lambda row: row["item_id"])] for level in range(1, 6)]
    ho = [[(r["prompt_tokens"], r["generated_tokens"], r["correct"])
           for r in sorted(holdout.get(level, []), key=lambda row: row["item_id"])] for level in range(1, 6)]
    result = {level: {"model": [], "direct": [], "residual": [], "invalid": 0} for level in range(1, 6)}
    for _ in range(config["bootstrap"]["replicates"]):
        energies = [[rows[rng.randrange(len(rows))] for _ in rows] for rows in en]
        holdouts = [[rows[rng.randrange(len(rows))] for _ in rows] for rows in ho]
        fit = _bootstrap_fit([row for rows in energies for row in rows])
        for level, (er, hr) in enumerate(zip(energies, holdouts), 1):
            out = result[level]
            if not er:
                continue
            em = math.fsum(row[2] for row in er)/len(er)
            if fit is not None:
                out["residual"].append(misfit_statistic(em, sum(row[0] for row in er)/len(er),
                                                      sum(row[1] for row in er)/len(er), fit))
            if not hr:
                continue
            k, n = sum(row[2] for row in hr), len(hr)
            out["direct"].append(em/(k/n) if k else math.inf)
            if fit is None:
                out["invalid"] += 1
                out["model"].append(None)
                continue
            mu = math.fsum((fit[0], fit[1]*sum(row[0] for row in hr)/n, fit[2]*sum(row[1] for row in hr)/n))
            if mu <= 0:
                out["invalid"] += 1
                out["model"].append(None)
            else:
                out["model"].append(mu/(k/n) if k else math.inf)
    return result


def model_epc(fit, holdout, m_energy, invalid=0):
    """Point and status; a computable point survives an invalid interval."""
    n, k = len(holdout), sum(row["correct"] for row in holdout)
    mu = epc = None
    if fit["status"] == "ok" and n:
        mu = math.fsum((fit["a_j"], fit["b_prompt_j_per_tok"]*sum(r["prompt_tokens"] for r in holdout)/n,
                       fit["b_gen_j_per_tok"]*sum(r["generated_tokens"] for r in holdout)/n))
        epc = mu/(k/n) if k else None
    if fit["status"] != "ok":
        status = "fit_" + fit["status"]
    elif m_energy < 2:
        status = "few_attempts"
    elif not k:
        status = "zero_correct"
    elif mu <= 0:
        status = "nonpositive"
    elif invalid:
        status = "bootstrap_invalid"
    else:
        status = "ok"
    return {"model_energy_j": mu, "epc_model_j": epc, "epc_model_status": status}


def _identifier(cell):
    return cell["model"] + "/" + cell["mode"]


def incomplete_reason(cell):
    if cell["cell_status"] != "complete":
        return _identifier(cell) + ":" + cell["cell_status"]
    if cell["epc_status"] != "ok":
        return _identifier(cell) + ":" + cell["epc_status"]
    return ""


def log_ratio_replicates(a, b):
    return [0.0 if x == y == math.inf else math.log(x) - math.log(y) for x, y in zip(a, b)]


def compare_replicates(log_ratio, replicates, descriptive_confidence, decision_confidence):
    desc_lo, desc_hi = percentile(replicates, descriptive_confidence)
    dec_lo, dec_hi = percentile(replicates, decision_confidence)
    return {"log_ratio": log_ratio, "desc_lo": desc_lo, "desc_hi": desc_hi,
            "dec_lo": dec_lo, "dec_hi": dec_hi,
            "status": "resolved" if dec_lo > 0 or dec_hi < 0 else "unresolved"}


def primary_comparison(a, b, replicates, config):
    row = dict.fromkeys(PRIMARY_COLUMNS[3:])
    row.update(a=_identifier(a), b=_identifier(b), epc_a_j=a["epc_j"], epc_b_j=b["epc_j"],
               source_a=a["primary_source"], source_b=b["primary_source"], cheaper="", reason="")
    reasons = [reason for reason in (incomplete_reason(a), incomplete_reason(b)) if reason]
    if reasons:
        row.update(status="unresolved_incomplete", reason=";".join(reasons))
    else:
        ratio = a["epc_j"]/b["epc_j"]
        row.update(compare_replicates(math.log(ratio), log_ratio_replicates(
            replicates[_identifier(a)], replicates[_identifier(b)]),
            config["descriptive_confidence"], config["decision_confidence"]))
        row["ratio"] = ratio
        if row["status"] == "resolved":
            row["cheaper"] = row["b"] if row["dec_lo"] > 0 else row["a"]
    return row


def crossover(cells, replicates, config):
    eligible = [cell for cell in cells if not incomplete_reason(cell)]
    incomplete = sorted(filter(None, (incomplete_reason(cell) for cell in cells)))
    row = {"cheapest": None, "cheapest_epc_j": None, "status": "none_estimable", "tied": "",
           "incomplete": ";".join(incomplete)}
    if not eligible:
        return row, []
    winner = min(eligible, key=lambda cell: (cell["epc_j"], _identifier(cell)))
    row.update(cheapest=_identifier(winner), cheapest_epc_j=winner["epc_j"])
    rivals, tied = [], []
    for cell in sorted(cells, key=_identifier):
        if cell is winner:
            continue
        rival = dict.fromkeys(RIVAL_COLUMNS[3:])
        rival.update(cheapest=row["cheapest"], rival=_identifier(cell), reason=incomplete_reason(cell))
        if not rival["reason"]:
            comparison = compare_replicates(math.log(cell["epc_j"]/winner["epc_j"]),
                log_ratio_replicates(replicates[_identifier(cell)], replicates[row["cheapest"]]),
                config["descriptive_confidence"], config["decision_confidence"])
            rival.update({key: comparison[key] for key in ("log_ratio", "desc_lo", "desc_hi", "dec_lo", "dec_hi")})
            rival["beaten"] = int(rival["dec_lo"] > 0)
            if not rival["beaten"]:
                tied.append(rival["rival"])
        rivals.append(rival)
    row.update(status="unresolved_incomplete" if incomplete else "unresolved" if tied else "resolved",
               tied=";".join(tied))
    return row, rivals


def primary_verdict(rows):
    levels = {str(row["level"]): {key: row[key] for key in ("status", "cheaper", "log_ratio", "dec_lo", "dec_hi")}
              for row in rows}
    winners = {row["cheaper"] for row in rows if row["status"] == "resolved"}
    return {"verdict": "cheaper_size_changes_with_level" if len(winners) > 1 else "no_resolved_change",
            "levels": levels}


def crossover_verdict(rows):
    winners = {str(row["level"]): row["cheapest"] for row in rows if row["status"] == "resolved"}
    return {"verdict": "crossover_resolved" if len(set(winners.values())) > 1 else "no_resolved_crossover",
            "resolved_winners": winners}


def _not_used_counts(original, used, role):
    used_ids = {id(row) for row in used}
    keys = {_row_key(row, role) for row in used}
    unused = [row for row in original if id(row) not in used_ids]
    return len(unused), sum(_row_key(row, role) in keys for row in unused)


def estimate_tables(bench_rows, energy_rows, config, selections):
    bench = parse_bench(bench_rows, config, selections)
    energy = parse_energy(energy_rows, bench, config, selections)
    lists = selection_lists(selections)
    roster = {}
    for entry in config["configurations"]:
        identifier = entry["model"] + "/" + entry["mode"]
        present = any((row["model"], row["mode"]) == (entry["model"], entry["mode"]) for row in bench + energy)
        roster[identifier] = "not_measured" if entry["status"] == "optional" and not present else entry["status"]
    parties = [entry for entry in config["configurations"] if roster[entry["model"] + "/" + entry["mode"]] != "not_measured"]
    tables = {name: [] for name in ("cells", "decomposition", "level_residuals", "primary", "rivals", "crossover")}
    summary = {"variants": {variant: {} for variant in VARIANTS}, "roster": roster, "targets": config["sizes"],
        "descriptive_confidence": config["descriptive_confidence"], "decision_confidence": config["decision_confidence"],
        "bootstrap": config["bootstrap"], "python_version": platform.python_version(),
        "exclusions": {"always": sorted(BENCH_EXCLUDE), "exclude_flags": config["exclude_flags"],
                       "physical_exclude_flags": config["physical_exclude_flags"]},
        "flag_counts": {name: dict(sorted(Counter(flag for row in rows for flag in row["flags"]).items()))
                        for name, rows in (("bench", bench), ("energy", energy))},
        "selection_size_mismatch": [f"selection_size_mismatch:{mode}:{role}:{level}"
            for mode in ("off", "on") for role in ("bench", "energy") for level in range(1, 6)
            if len(lists[mode, role, level]) != config["sizes"][mode][role][str(level)]]}
    cd = config["descriptive_confidence"]
    cell_lookup, primary_reps = {}, {}
    for variant in VARIANTS:
        used_bench = used_rows(bench, "bench", config, variant)
        used_energy = used_rows(energy, "energy", config, variant)
        for boundary in sorted(config["boundaries"]):
            misfits = []
            for entry in sorted(parties, key=lambda c: (c["model"], c["mode"])):
                model, mode = entry["model"], entry["mode"]
                identity = {"variant": variant, "boundary": boundary, "model": model, "mode": mode}
                b_all = [row for row in bench if (row["model"], row["mode"]) == (model, mode)
                         and not row["flags"] & {"bad_level", "bad_mode"}]
                e_all = [row for row in energy if (row["boundary"], row["model"], row["mode"]) == (boundary, model, mode)
                         and not row["flags"] & {"bad_level", "bad_mode"}]
                b = {level: [row for row in used_bench if (row["model"], row["mode"], row["level"]) == (model, mode, level)]
                     for level in range(1, 6)}
                e = {level: [row for row in used_energy if (row["boundary"], row["model"], row["mode"], row["level"]) ==
                            (boundary, model, mode, level)] for level in range(1, 6)}
                h = {level: [row for row in b[level] if row["item_id"] not in set(lists[mode, "energy", level])]
                     for level in range(1, 6)}
                pooled = [row for level in range(1, 6) for row in e[level]]
                fit, residuals = decomposition(pooled, cd)
                tables["decomposition"].append({**identity, **fit})
                boot = bootstrap(e, h, config, variant, boundary, model, mode)
                # Registered §8.8 arithmetic: tau=1e-9*max(1 J, pooled mean J).
                # No physical/printed-precision derivation is registered; retain
                # this source-switch threshold for the next registration revision.
                tolerance = 1e-9 * max(1, mean(row["energy_j"] for row in pooled) if pooled else 1)
                residual_by_level = {row["level"]: row for row in residuals}
                for level in range(1, 6):
                    er, br, hr = e[level], b[level], h[level]
                    nh, kh, n, k, m = len(hr), sum(row["correct"] for row in hr), len(br), sum(row["correct"] for row in br), len(er)
                    reps = boot[level]
                    # Section 8.7 percentiles are over B values; a singular refit leaves fewer, so the
                    # residual interval is blank and the misfit is not assessed (the model is
                    # bootstrap_invalid in that case, so the primary is direct either way).
                    complete = len(reps["residual"]) == config["bootstrap"]["replicates"]
                    rlo, rhi = percentile(reps["residual"], cd) if complete else (None, None)
                    misfit = rlo is not None and (rlo > tolerance or rhi < -tolerance)
                    if level in residual_by_level:
                        tables["level_residuals"].append({**identity, **residual_by_level[level],
                            "boot_lo_j": rlo, "boot_hi_j": rhi, "misfit": int(misfit)})
                    if misfit:
                        misfits.append(f"{model}/{mode}:{level}")
                    cell = dict.fromkeys(CELL_COLUMNS)
                    cell.update(identity, level=level, n_bench=n, k_correct=k, n_holdout=nh, k_holdout=kh, m_energy=m)
                    cell["n_bench_target"] = config["sizes"][mode]["bench"][str(level)]
                    cell["m_energy_target"] = config["sizes"][mode]["energy"][str(level)]
                    cell["n_holdout_target"] = cell["n_bench_target"] - cell["m_energy_target"]
                    cell["cell_status"] = "complete" if (n, nh, m) == (cell["n_bench_target"], cell["n_holdout_target"], cell["m_energy_target"]) else "missing" if n == m == 0 else "short"
                    cell["accuracy"], cell["acc_lo"], cell["acc_hi"] = wilson(k, n, cd)
                    cell["mean_generated_tokens_bench"] = sum(row["generated_tokens"] for row in br)/n if n else None
                    cell["cap_hit_rate_bench"] = sum(row["cap_hit"] for row in br)/n if n else None
                    cell["loop_rate_bench"] = sum("repetition_loop" in row["flags"] for row in br)/n if n else None
                    cell["holdout_accuracy"] = kh/nh if nh else None
                    cell["mean_prompt_tokens_holdout"] = sum(row["prompt_tokens"] for row in hr)/nh if nh else None
                    cell["mean_generated_tokens_holdout"] = sum(row["generated_tokens"] for row in hr)/nh if nh else None
                    energies = [row["energy_j"] for row in er]
                    direct = energy_per_correct(kh, nh, energies, cd)
                    for key in ("mean_energy_j", "energy_lo_j", "energy_hi_j"):
                        cell[key] = direct[key]
                    for key in ("epc_j", "epc_lo_j", "epc_hi_j", "epc_status"):
                        cell[key.replace("epc_", "epc_direct_")] = direct[key]
                    cell.update(model_epc(fit, hr, m, reps["invalid"]))
                    if cell["epc_model_status"] == "ok":
                        cell["epc_model_lo_j"], cell["epc_model_hi_j"] = percentile(reps["model"], cd)
                    source = None
                    if cell["epc_model_status"] == "ok" and not misfit:
                        source, reason = "model", ""
                    elif kh >= 1 and m >= 2:
                        source, reason = "direct", "misfit" if misfit else "model_" + cell["epc_model_status"]
                    else:
                        reason = ""
                    cell["primary_source"], cell["primary_reason"] = source, reason
                    if source:
                        cell["epc_j"] = cell[f"epc_{source}_j"]
                        cell["epc_lo_j"], cell["epc_hi_j"] = percentile(reps[source], cd)
                        cell["epc_status"] = "ok"
                    else:
                        cell["epc_status"] = direct["epc_status"]
                    cell["j_per_token"], cell["jpt_lo"], cell["jpt_hi"] = joules_per_token(energies, [row["generated_tokens"] for row in er], cd)
                    cell["token_mismatch_count"] = sum("token_mismatch" in row["flags"] for row in er)
                    counts = [_not_used_counts([row for row in original if row["level"] == level], used, role)
                              for original, used, role in ((b_all, br, "bench"), (e_all, er, "energy"))]
                    cell["rows_not_used"], cell["replaced_rows"] = (sum(pair[i] for pair in counts) for i in (0, 1))
                    tables["cells"].append(cell)
                    cell_lookup[variant, boundary, level, f"{model}/{mode}"] = cell
                    primary_reps[variant, boundary, level, f"{model}/{mode}"] = reps[source] if source else []
            primary_rows, secondary_rows = [], []
            for level in range(1, 6):
                identity = {"variant": variant, "boundary": boundary, "level": level}
                comparison = config["primary_comparison"]
                # Measured primary arms are present even if their tables are empty.
                pair = [cell_lookup.get((variant, boundary, level, comparison[side])) for side in ("a", "b")]
                reps = {entry["model"] + "/" + entry["mode"]: primary_reps[variant, boundary, level, entry["model"] + "/" + entry["mode"]]
                        for entry in parties}
                if all(cell is not None for cell in pair):
                    row = {**identity, **primary_comparison(*pair, reps, config)}
                else:
                    row = dict.fromkeys(PRIMARY_COLUMNS)
                    row.update(identity, a=comparison["a"], b=comparison["b"], status="unresolved_incomplete", cheaper="",
                               reason=";".join(filter(None, (comparison[side] + ":not_measured" if cell is None
                                   else incomplete_reason(cell) for side, cell in zip(("a", "b"), pair)))))
                    for side, cell in zip(("a", "b"), pair):
                        if cell is not None:
                            row[f"epc_{side}_j"] = cell["epc_j"]
                            row[f"source_{side}"] = cell["primary_source"]
                primary_rows.append(row)
                cells = [cell_lookup[variant, boundary, level, entry["model"] + "/" + entry["mode"]] for entry in parties]
                result, rivals = crossover(cells, reps, config)
                secondary_rows.append({**identity, **result})
                tables["rivals"].extend({**identity, **rival} for rival in rivals)
            tables["primary"].extend(primary_rows)
            tables["crossover"].extend(secondary_rows)
            summary["variants"][variant][boundary] = {"primary_question": primary_verdict(primary_rows),
                "secondary": crossover_verdict(secondary_rows), "misfit_cells": sorted(misfits)}
    switched = sorted(f"{row['variant']}/{row['boundary']}/{row['model']}/{row['mode']}:{row['level']}"
                      for row in tables["cells"] if row["primary_reason"] == "misfit")
    summary["method_note"] = (
        "Primary EPC uses a pooled model per configuration and holdout token means; direct EPC is secondary. "
        # Description of §8.8's registered threshold above, not an agreement bar;
        # its physical/printed-precision derivation is owed at the next revision.
        "A descriptive bootstrap residual interval excluding zero beyond 1e-9*max(1, pooled mean energy) "
        "selects direct EPC at misfit levels. Switched cells (variant/boundary/configuration:level): "
        + (", ".join(switched) if switched else "none") + ". "
        f"Problem-level bootstrap is stratified by level, B={config['bootstrap']['replicates']}, with percentile order statistics. "
        f"Descriptive confidence is {cd}; decisions use only decision confidence {config['decision_confidence']}. "
        "Incomplete parties make comparisons unresolved. Retries replace any excluded attempt; later attempts after "
        "a usable primary result are duplicates. Flagged-inclusive uses the first usable attempt including physical flags. "
        "Headline accuracy uses all bench rows; EPC uses the selection-defined holdout. Gross whole-request energy "
        "includes prefill and decode, with no idle subtraction. Published level is a stratum, not a cause."
    )
    tables["summary"] = summary
    for name in ("cells", "decomposition", "level_residuals"):
        tables[name].sort(key=lambda row: tuple(row[key] for key in ("variant", "boundary", "model", "mode") ) +
                          ((row["level"],) if name != "decomposition" else ()))
    for name in ("primary", "crossover", "rivals"):
        keys = ("variant", "boundary", "level", "cheapest", "rival") if name == "rivals" else ("variant", "boundary", "level")
        tables[name].sort(key=lambda row: tuple(row[key] for key in keys))
    return tables


def read_csv(path):
    with Path(path).expanduser().open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, columns, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: repr(row[key]) if type(row.get(key)) is float else row.get(key) for key in columns})


def write_tables(out_dir, tables):
    directory = Path(out_dir).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    for name, columns in (("cells", CELL_COLUMNS), ("decomposition", DECOMPOSITION_COLUMNS),
                          ("level_residuals", RESIDUAL_COLUMNS), ("primary", PRIMARY_COLUMNS),
                          ("rivals", RIVAL_COLUMNS), ("crossover", CROSSOVER_COLUMNS)):
        write_csv(directory / (name + ".csv"), columns, tables[name])
    (directory / "summary.json").write_text(json.dumps(tables["summary"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
