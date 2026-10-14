"""DIFFICULTY table parsing and the estimators in the pack specification."""
import csv
import json
import math
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from statistics import NormalDist, mean

from .score import BENCH_COLUMNS

ENERGY_COLUMNS = ("model", "mode", "level", "item_id", "boundary", "energy_j",
                  "prompt_tokens", "generated_tokens", "flags")
CELL_COLUMNS = ("boundary", "model", "mode", "level", "n_bench", "k_correct", "accuracy",
                "acc_lo", "acc_hi", "mean_generated_tokens_bench", "cap_hit_rate_bench",
                "m_energy", "mean_energy_j", "energy_lo_j", "energy_hi_j", "epc_j",
                "epc_lo_j", "epc_hi_j", "epc_status", "j_per_token", "jpt_lo", "jpt_hi",
                "token_mismatch_count", "excluded_rows")
DECOMPOSITION_COLUMNS = ("boundary", "model", "mode", "N", "a_j", "a_se",
                         "b_prompt_j_per_tok", "b_prompt_se", "b_gen_j_per_tok", "b_gen_se",
                         "r2", "r2_gen_only", "gen_share", "status")
RESIDUAL_COLUMNS = ("boundary", "model", "mode", "level", "m", "mean_residual_j",
                    "lo_j", "hi_j", "contains_zero")
CROSSOVER_COLUMNS = ("boundary", "level", "cheapest", "cheapest_epc_j", "status", "tied")
ALWAYS_EXCLUDE = {"bad_number", "bad_level", "bad_mode", "duplicate", "unknown_item", "unknown_config"}
BENCH_EXCLUDE = ALWAYS_EXCLUDE | {"missing_text"}
METHOD_NOTE = (
    "Accuracy uses Wilson intervals; mean gross whole-request energy uses Student t intervals; "
    "energy per correct answer uses log-scale MOVER. The numerator averages all attempts. "
    "Accuracy and energy are treated as independent although the energy subset overlaps the "
    "bench and wrong answers can run longer; the neglected dependence scales with m/n. "
    "Crossover comparisons treat configurations as independent although they answer the same "
    "problems, tending toward unresolved results. Confidence is unadjusted for multiple "
    "comparisons; pack registration sets that policy. Published MATH level is a stratum, "
    "not a causal measure. Joules per generated token includes prompt energy."
)


def _beta_fraction(a, b, x):
    """Lentz continued fraction for the regularized incomplete beta."""
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
    fit = dict.fromkeys(DECOMPOSITION_COLUMNS[4:-1])
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


def crossover(cells):
    candidates = [row for row in cells if row["epc_status"] in ("ok", "energy_lower_nonpositive")]
    if not candidates:
        return {"cheapest": None, "cheapest_epc_j": None, "status": "none_estimable", "tied": ""}
    winner = min(candidates, key=lambda row: (row["epc_j"], row["model"], row["mode"]))
    tied = []
    for rival in candidates:
        if rival is winner:
            continue
        lower = -math.inf if rival["epc_lo_j"] <= 0 else (
            math.log(rival["epc_j"] / winner["epc_j"]) - math.hypot(
                math.log(rival["epc_j"] / rival["epc_lo_j"]),
                math.log(winner["epc_hi_j"] / winner["epc_j"])))
        if lower <= 0:
            tied.append(rival["model"] + "/" + rival["mode"])
    return {"cheapest": winner["model"] + "/" + winner["mode"], "cheapest_epc_j": winner["epc_j"],
            "status": "unresolved" if tied else "resolved", "tied": ";".join(sorted(tied))}


def crossover_verdict(rows):
    winners = {str(row["level"]): row["cheapest"] for row in rows if row["status"] == "resolved"}
    return {"verdict": "crossover_resolved" if len(set(winners.values())) > 1 else "no_resolved_crossover",
            "resolved_winners": winners}


def _integer(value):
    if isinstance(value, bool):
        return None
    try:
        text = str(value).strip()
        if not text or not text.lstrip("+-").isdigit():
            return None
        number = int(text)
        return number if number >= 0 else None
    except (ValueError, TypeError):
        return None


def _flags(value):
    return {flag.strip() for flag in (value or "").split(";") if flag.strip()}


def parse_bench(rows):
    parsed, seen = [], set()
    for original in rows:
        row = dict(original)
        flags = _flags(row.get("flags"))
        for key in ("correct", "cap_hit", "prompt_tokens", "generated_tokens"):
            row[key] = _integer(row.get(key))
            if row[key] is None or (key in ("correct", "cap_hit") and row[key] not in (0, 1)):
                flags.add("bad_number")
        row["level"] = _integer(row.get("level"))
        if row["level"] not in range(1, 6):
            flags.add("bad_level")
        if row.get("mode") not in ("off", "on"):
            flags.add("bad_mode")
        for key in ("model", "mode", "item_id"):
            row[key] = row.get(key) or ""
        key = row["model"], row["mode"], row["item_id"]
        if key in seen:
            flags.add("duplicate")
        seen.add(key)
        row["flags"] = flags
        parsed.append(row)
    return parsed


def parse_energy(rows, bench):
    lookup = {}
    for row in bench:
        lookup.setdefault((row["model"], row["mode"], row["item_id"]), row)
    parsed, seen = [], set()
    for original in rows:
        row = dict(original)
        flags = _flags(row.get("flags"))
        for key in ("model", "mode", "item_id", "boundary"):
            row[key] = row.get(key) or ""
        for key in ("prompt_tokens", "generated_tokens"):
            row[key] = _integer(row.get(key))
            if row[key] is None:
                flags.add("bad_number")
        try:
            row["energy_j"] = float(row.get("energy_j"))
            if not math.isfinite(row["energy_j"]) or row["energy_j"] <= 0:
                flags.add("bad_number")
        except (TypeError, ValueError, OverflowError):
            row["energy_j"] = None
            flags.add("bad_number")
        row["level"] = _integer(row.get("level"))
        if row["level"] not in range(1, 6):
            flags.add("bad_level")
        if row["mode"] not in ("off", "on"):
            flags.add("bad_mode")
        key = row["model"], row["mode"], row["item_id"]
        if (*key, row["boundary"]) in seen:
            flags.add("duplicate")
        seen.add((*key, row["boundary"]))
        reference = lookup.get(key)
        if reference is None:
            flags.add("not_in_bench")
        else:
            if row["level"] != reference["level"]:
                flags.add("level_mismatch")
            if row["generated_tokens"] is not None and reference["generated_tokens"] is not None and row["generated_tokens"] != reference["generated_tokens"]:
                flags.add("token_mismatch")
        row["flags"] = flags
        parsed.append(row)
    return parsed


def estimate_tables(bench_rows, energy_rows, confidence=0.95, exclude_flags=()):
    bench = parse_bench(bench_rows)
    energy = parse_energy(energy_rows, bench)
    exclude = set(exclude_flags)
    bench_cells, energy_cells, excluded = defaultdict(list), defaultdict(list), Counter()
    for row in bench:
        if not row["flags"] & (BENCH_EXCLUDE | exclude):
            bench_cells[row["model"], row["mode"], row["level"]].append(row)
    for row in energy:
        key = row["boundary"], row["model"], row["mode"], row["level"]
        if row["flags"] & (ALWAYS_EXCLUDE | exclude):
            if not row["flags"] & {"bad_level", "bad_mode"}:
                excluded[key] += 1
        else:
            energy_cells[key].append(row)
    boundaries = sorted({key[0] for key in energy_cells})
    keys = set(energy_cells) | {(boundary, *key) for boundary in boundaries for key in bench_cells}
    cells = []
    for boundary, model, mode, level in sorted(keys):
        key = boundary, model, mode, level
        b = bench_cells.get((model, mode, level), [])
        e = energy_cells.get(key, [])
        n, k, m = len(b), sum(row["correct"] for row in b), len(e)
        p, p_lo, p_hi = wilson(k, n, confidence)
        energies, tokens = [row["energy_j"] for row in e], [row["generated_tokens"] for row in e]
        ratio, ratio_lo, ratio_hi = joules_per_token(energies, tokens, confidence)
        cells.append({"boundary": boundary, "model": model, "mode": mode, "level": level,
                      "n_bench": n, "k_correct": k, "accuracy": p, "acc_lo": p_lo, "acc_hi": p_hi,
                      "mean_generated_tokens_bench": float(mean(row["generated_tokens"] for row in b)) if n else None,
                      "cap_hit_rate_bench": sum(row["cap_hit"] for row in b)/n if n else None,
                      "m_energy": m, **energy_per_correct(k, n, energies, confidence),
                      "j_per_token": ratio, "jpt_lo": ratio_lo, "jpt_hi": ratio_hi,
                      "token_mismatch_count": sum("token_mismatch" in row["flags"] for row in e),
                      "excluded_rows": excluded[key]})
    groups = defaultdict(list)
    for key, rows in energy_cells.items():
        groups[key[:3]].extend(rows)
    fits, residuals = [], []
    for (boundary, model, mode), rows in sorted(groups.items()):
        identity = {"boundary": boundary, "model": model, "mode": mode}
        fit, level_rows = decomposition(rows, confidence)
        fits.append({**identity, **fit})
        residuals.extend({**identity, **row} for row in level_rows)
    comparisons = defaultdict(list)
    for row in cells:
        comparisons[row["boundary"], row["level"]].append(row)
    crossovers = [{"boundary": boundary, "level": level, **crossover(rows)}
                  for (boundary, level), rows in sorted(comparisons.items())]
    summary = {"boundaries": {boundary: crossover_verdict(
        [row for row in crossovers if row["boundary"] == boundary]) for boundary in boundaries},
        "flag_counts": {name: dict(sorted(Counter(flag for row in rows for flag in row["flags"]).items()))
                        for name, rows in (("bench", bench), ("energy", energy))},
        "confidence": confidence, "method_note": METHOD_NOTE}
    return {"cells": cells, "decomposition": fits, "level_residuals": residuals,
            "crossover": crossovers, "summary": summary}


def read_csv(path):
    with Path(path).expanduser().open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, columns, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: repr(row[key]) if type(row.get(key)) is float else row.get(key)
                             for key in columns})


def write_tables(out_dir, tables):
    directory = Path(out_dir).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    for name, columns in (("cells", CELL_COLUMNS), ("decomposition", DECOMPOSITION_COLUMNS),
                          ("level_residuals", RESIDUAL_COLUMNS), ("crossover", CROSSOVER_COLUMNS)):
        write_csv(directory / (name + ".csv"), columns, tables[name])
    (directory / "summary.json").write_text(json.dumps(tables["summary"], indent=2, sort_keys=True)
                                            + "\n", encoding="utf-8")
