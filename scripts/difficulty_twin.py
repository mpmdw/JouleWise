#!/usr/bin/env python3
"""Independent DIFFICULTY v2 recomputation from SPEC-v2.md, stdlib only.

No repository modules are imported. The numerical primitives retained from
v1.1 were also independently derived; all v2 analysis follows sections 6–10.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from functools import lru_cache
import json
import math
from pathlib import Path
import platform
import random
import re
from statistics import NormalDist


BENCH_COLUMNS = "model mode item_id level attempt outcome correct prompt_tokens generated_tokens cap_hit flags".split()
ENERGY_COLUMNS = "model mode level item_id boundary attempt energy_j prompt_tokens generated_tokens flags".split()
CELL_COLUMNS = "variant boundary model mode level cell_status n_bench_target n_bench k_correct accuracy acc_lo acc_hi mean_generated_tokens_bench cap_hit_rate_bench loop_rate_bench n_holdout_target n_holdout k_holdout holdout_accuracy mean_prompt_tokens_holdout mean_generated_tokens_holdout m_energy_target m_energy mean_energy_j energy_lo_j energy_hi_j model_energy_j epc_model_j epc_model_lo_j epc_model_hi_j epc_model_status epc_direct_j epc_direct_lo_j epc_direct_hi_j epc_direct_status epc_j epc_lo_j epc_hi_j epc_status primary_source primary_reason j_per_token jpt_lo jpt_hi token_mismatch_count rows_not_used replaced_rows".split()
DECOMPOSITION_COLUMNS = "variant boundary model mode N a_j a_se a_lo_j a_hi_j b_prompt_j_per_tok b_prompt_se b_prompt_lo b_prompt_hi b_gen_j_per_tok b_gen_se b_gen_lo b_gen_hi r2 r2_gen_only gen_share status".split()
RESIDUAL_COLUMNS = "variant boundary model mode level m mean_residual_j lo_j hi_j contains_zero boot_lo_j boot_hi_j misfit".split()
PRIMARY_COLUMNS = "variant boundary level a b epc_a_j epc_b_j source_a source_b log_ratio ratio desc_lo desc_hi dec_lo dec_hi status cheaper reason".split()
RIVAL_COLUMNS = "variant boundary level cheapest rival log_ratio desc_lo desc_hi dec_lo dec_hi beaten reason".split()
CROSSOVER_COLUMNS = "variant boundary level cheapest cheapest_epc_j status tied incomplete".split()
ALWAYS = {"bad_number", "bad_level", "bad_mode", "unknown_item", "unknown_config", "not_selected", "unknown_boundary", "duplicate"}
VARIANTS = ("primary", "flagged_inclusive")
LEVELS = range(1, 6)
SCHEMAS = {"cells.csv": CELL_COLUMNS, "decomposition.csv": DECOMPOSITION_COLUMNS,
           "level_residuals.csv": RESIDUAL_COLUMNS, "primary.csv": PRIMARY_COLUMNS,
           "rivals.csv": RIVAL_COLUMNS, "crossover.csv": CROSSOVER_COLUMNS}
KEYS = {name: columns[:4] + (["level"] if name in {"cells.csv", "level_residuals.csv"} else [])
        for name, columns in SCHEMAS.items()}
KEYS.update({"primary.csv": ["variant", "boundary", "level"],
             "rivals.csv": ["variant", "boundary", "level", "cheapest", "rival"],
             "crossover.csv": ["variant", "boundary", "level"]})


def _beta_fraction(a: float, b: float, x: float) -> float:
    """Incomplete-beta continued fraction, evaluated by modified Lentz."""
    tiny = 1e-300

    def nonzero(value):
        return value if abs(value) >= tiny else math.copysign(tiny, value)

    c = 1.0
    d = 1.0 / nonzero(1.0 - (a+b)*x/(a+1.0))
    h = d
    for j in range(1, 1001):
        even = j*(b-j)*x / ((a+2*j-1)*(a+2*j))
        d = 1.0 / nonzero(1.0 + even*d)
        c = nonzero(1.0 + even/c)
        h *= d*c
        odd = -(a+j)*(a+b+j)*x / ((a+2*j)*(a+2*j+1))
        d = 1.0 / nonzero(1.0 + odd*d)
        c = nonzero(1.0 + odd/c)
        change = d*c
        h *= change
        if abs(change-1.0) <= 4e-16:
            return h
    raise ArithmeticError("incomplete-beta continued fraction did not converge")


def regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    factor = math.exp(
        math.lgamma(a+b) - math.lgamma(a) - math.lgamma(b)
        + a*math.log(x) + b*math.log1p(-x)
    )
    if x < (a+1.0)/(a+b+2.0):
        return factor*_beta_fraction(a, b, x)/a
    return 1.0 - factor*_beta_fraction(b, a, 1.0-x)/b


@lru_cache(maxsize=256)
def student_t_quantile(probability: float, df: int) -> float:
    """Invert Student t survival probability to absolute 1e-13."""
    if df < 1 or not 0.0 < probability < 1.0:
        raise ValueError("t quantile needs df >= 1 and 0 < probability < 1")
    if probability == 0.5:
        return 0.0
    if probability < 0.5:
        return -student_t_quantile(1.0-probability, df)
    tail = 1.0-probability

    def survival(t):
        return 0.5*regularized_beta(df/(df+t*t), df/2.0, 0.5)

    left, right = 0.0, 1.0
    while survival(right) > tail:
        right *= 2.0
    for _ in range(200):
        middle = (left+right)/2.0
        if middle == left or middle == right or right-left <= 1e-13:
            return middle
        if survival(middle) > tail:
            left = middle
        else:
            right = middle
    raise ArithmeticError("t quantile bisection did not converge")


def wilson(k: int, n: int, confidence: float):
    if not n:
        return None, None, None
    p = k/n
    z = NormalDist().inv_cdf((1.0+confidence)/2.0)
    z2 = z*z
    denominator = 1.0+z2/n
    centre = (p+z2/(2*n))/denominator
    half = z*math.sqrt(p*(1.0-p)/n+z2/(4*n*n))/denominator
    # Pin mathematical endpoints so roundoff cannot enter a logarithm.
    return p, 0.0 if k == 0 else centre-half, 1.0 if k == n else centre+half


def mean_interval(values, confidence):
    m = len(values)
    if m < 2:
        return None, None, None
    mean = math.fsum(values)/m
    variance = math.fsum((value-mean)**2 for value in values)/(m-1)
    half = student_t_quantile((1.0+confidence)/2.0, m-1)*math.sqrt(variance/m)
    return mean, mean-half, mean+half


def energy_per_correct(mean, elo, ehi, p, plo, phi, k, m):
    if k == 0:
        return None, None, None, "not_estimable_zero_correct"
    if m < 2:
        return None, None, None, "not_estimable_few_attempts"
    point = mean/p
    log_mean, log_p = math.log(mean), math.log(p)
    d = log_mean-log_p
    upper = math.exp(d+math.hypot(math.log(ehi)-log_mean, log_p-math.log(plo)))
    if elo <= 0.0:
        return point, 0.0, upper, "energy_lower_nonpositive"
    lower = math.exp(d-math.hypot(log_mean-math.log(elo), math.log(phi)-log_p))
    return point, lower, upper, "ok"


def joules_per_token(energies, tokens, confidence):
    m = len(energies)
    total_tokens = sum(tokens)
    if m < 2 or total_tokens == 0:
        return None, None, None
    ratio = math.fsum(energies)/total_tokens
    deviations = [energy-ratio*g for energy, g in zip(energies, tokens)]
    variance = math.fsum(d*d for d in deviations)/(m-1)
    se = math.sqrt(variance/(m*(total_tokens/m)**2))
    half = student_t_quantile((1.0+confidence)/2.0, m-1)*se
    return ratio, ratio-half, ratio+half


def _integer(text, minimum=0, maximum=None):
    text = (text or "").strip()
    if re.fullmatch(r"[+-]?[0-9]+", text) is None:
        return None
    value = int(text)
    if value < minimum or (maximum is not None and value > maximum):
        return None
    return value


def _flags(text):
    return {part.strip() for part in (text or "").split(";") if part.strip()}


def read_table(path, columns):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(columns):
            raise ValueError(f"{path}: expected columns {','.join(columns)}")
        return list(reader)


def validate_config(config):
    """Validate number-bearing inputs without substituting defaults (§2)."""
    def require(condition, key):
        if not condition:
            raise ValueError(f"invalid config key: {key}")

    def integer(value, low):
        return type(value) is int and value >= low

    def string(value):
        return isinstance(value, str) and bool(value.strip())

    def number(value, low, high, inclusive=False):
        return (type(value) in (int, float) and math.isfinite(value)
                and low < value and (value <= high if inclusive else value < high))

    require(isinstance(config, dict), "config")
    if "confidence" in config or "energy_per_level" in config:
        raise ValueError("confidence/energy_per_level replaced in v2 by descriptive_confidence/decision_confidence and sizes")
    require(config.get("schema_version") == "difficulty_config.v2", "schema_version")
    for key in ("version", "seed"):
        require(string(config.get(key)), key)
    require(integer(config.get("n_per_level"), 1), "n_per_level")
    sizes = config.get("sizes")
    require(isinstance(sizes, dict) and set(sizes) == {"off", "on"}, "sizes")
    for mode in ("off", "on"):
        require(isinstance(sizes[mode], dict) and set(sizes[mode]) == {"bench", "energy"}, f"sizes.{mode}")
        for role in ("bench", "energy"):
            values = sizes[mode][role]
            require(isinstance(values, dict) and set(values) == set(map(str, LEVELS)), f"sizes.{mode}.{role}")
            for level, value in values.items():
                require(integer(value, 0), f"sizes.{mode}.{role}.{level}")
        for level in map(str, LEVELS):
            require(0 <= sizes[mode]["energy"][level] <= sizes[mode]["bench"][level] <= config["n_per_level"], f"sizes.{mode}.{level}")
    boundaries = config.get("boundaries")
    require(isinstance(boundaries, list) and bool(boundaries) and all(isinstance(b, str) for b in boundaries), "boundaries")
    require(len(set(boundaries)) == len(boundaries), "boundaries")
    roster = config.get("configurations")
    require(isinstance(roster, list) and bool(roster), "configurations")
    identifiers = set()
    for i, entry in enumerate(roster):
        prefix = f"configurations.{i}"
        require(isinstance(entry, dict), prefix)
        require(string(entry.get("model")), prefix + ".model")
        require(isinstance(entry.get("mode"), str) and entry["mode"] in {"off", "on"}, prefix + ".mode")
        require(integer(entry.get("output_cap"), 1), prefix + ".output_cap")
        require(isinstance(entry.get("status"), str) and entry["status"] in {"measured", "optional"}, prefix + ".status")
        identifier = entry["model"] + "/" + entry["mode"]
        require(identifier not in identifiers, prefix + ".model/mode")
        identifiers.add(identifier)
    pair = config.get("primary_comparison")
    require(isinstance(pair, dict), "primary_comparison")
    for key in ("a", "b"):
        require(isinstance(pair.get(key), str) and pair[key] in identifiers, "primary_comparison." + key)
    require(pair["a"] != pair["b"], "primary_comparison")
    for key in ("descriptive_confidence", "decision_confidence"):
        require(number(config.get(key), 0.5, 1), key)
    bootstrap = config.get("bootstrap")
    require(isinstance(bootstrap, dict), "bootstrap")
    require(integer(bootstrap.get("replicates"), 20), "bootstrap.replicates")
    require(string(bootstrap.get("seed")), "bootstrap.seed")
    for key in ("exclude_flags", "physical_exclude_flags"):
        require(isinstance(config.get(key), list) and all(isinstance(v, str) for v in config[key]), key)
    require(not set(config["exclude_flags"]) & set(config["physical_exclude_flags"]), "physical_exclude_flags")
    loop = config.get("loop_detector")
    require(isinstance(loop, dict), "loop_detector")
    require(number(loop.get("tail_fraction"), 0, 1, True), "loop_detector.tail_fraction")
    require(integer(loop.get("min_span"), 1), "loop_detector.min_span")
    require(integer(loop.get("min_repeats"), 2), "loop_detector.min_repeats")
    return config


def row_key(row, energy=False):
    key = row["model"], row["mode"], row["item_id"]
    return (row["boundary"], *key) if energy else key


def exclusion(config, variant, energy=False):
    flags = ALWAYS | set(config["exclude_flags"])
    if not energy:
        flags = flags | {"missing_text"}
    if variant == "primary":
        flags = flags | set(config["physical_exclude_flags"])
    return flags


def mark_retries(rows, excluded, energy=False):
    """File-order same-attempt duplicates, then primary-based later attempts."""
    seen, groups = set(), defaultdict(list)
    for row in rows:
        attempt = row["attempt"]
        if attempt is None:
            continue
        key = row_key(row, energy)
        signature = key, attempt
        if signature in seen:
            row["flags"].add("duplicate")
        seen.add(signature)
        groups[key].append(row)
    for group in groups.values():
        selected = next((r for r in sorted(group, key=lambda r: r["attempt"])
                         if not r["flags"] & excluded), None)
        if selected is not None:
            for row in group:
                if row["attempt"] > selected["attempt"]:
                    row["flags"].add("duplicate")


def parse_tables(bench, energy, config, selections):
    roster = {(c["model"], c["mode"]) for c in config["configurations"]}
    result = []
    # The v1.1 generated-token check uses the first bench row for the key.
    lookup = {}
    for raw_rows, role in ((bench, "bench"), (energy, "energy")):
        parsed = []
        for raw in raw_rows:
            row = dict(raw)
            flags = _flags(raw.get("flags"))
            row["flags"] = flags
            row["level"] = _integer(raw.get("level"), 1, 5)
            row["attempt"] = _integer(raw.get("attempt"), 1)
            fields = ["prompt_tokens", "generated_tokens"]
            if role == "bench":
                fields += ["correct", "cap_hit"]
            for field in fields:
                row[field] = _integer(raw.get(field), 0, 1 if field in {"correct", "cap_hit"} else None)
            if row["level"] is None:
                flags.add("bad_level")
            if row["mode"] not in {"off", "on"}:
                flags.add("bad_mode")
            if row["attempt"] is None or any(row[f] is None for f in fields):
                flags.add("bad_number")
            if (row["model"], row["mode"]) not in roster:
                flags.add("unknown_config")
            selected = selections.get(row["mode"], {}).get(role, {}).get(str(row["level"]), [])
            if row["item_id"] not in selected:
                flags.add("not_selected")
            if role == "energy":
                try:
                    value = float(raw.get("energy_j") or "")
                except (ValueError, OverflowError):
                    value = math.nan
                row["energy_j"] = value
                if not math.isfinite(value) or value <= 0:
                    flags.add("bad_number")
                if row["boundary"] not in config["boundaries"]:
                    flags.add("unknown_boundary")
                reference = lookup.get(row_key(row))
                if reference is None:
                    flags.add("not_in_bench")
                elif (row["generated_tokens"] is not None and reference["generated_tokens"] is not None
                      and row["generated_tokens"] != reference["generated_tokens"]):
                    flags.add("token_mismatch")
            else:
                lookup.setdefault(row_key(row), row)
            parsed.append(row)
        mark_retries(parsed, exclusion(config, "primary", role == "energy"), role == "energy")
        result.append(parsed)
    return result


def used_rows(rows, excluded, energy=False):
    chosen = {}
    for row in sorted(rows, key=lambda r: r["attempt"] if r["attempt"] is not None else math.inf):
        if not row["flags"] & excluded:
            chosen.setdefault(row_key(row, energy), row)
    return list(chosen.values())


def ols(rows):
    """Centred two-predictor fit, checking singularity in exact integers."""
    n = len(rows)
    if n < 4:
        return {"N": n, "status": "few_rows"}
    p = [r["prompt_tokens"] for r in rows]
    g = [r["generated_tokens"] for r in rows]
    e = [r["energy_j"] for r in rows]
    ip = n * sum(x*x for x in p) - sum(p)**2
    ig = n * sum(x*x for x in g) - sum(g)**2
    ipg = n * sum(x*y for x, y in zip(p, g)) - sum(p)*sum(g)
    if ip*ig - ipg*ipg == 0:
        return {"N": n, "status": "singular"}
    pm, gm, em = (math.fsum(values)/n for values in (p, g, e))
    pc, gc, ec = ([v-mean for v in values] for values, mean in ((p, pm), (g, gm), (e, em)))
    pp = math.fsum(v*v for v in pc)
    gg = math.fsum(v*v for v in gc)
    pg = math.fsum(x*y for x, y in zip(pc, gc))
    pe = math.fsum(x*y for x, y in zip(pc, ec))
    ge = math.fsum(x*y for x, y in zip(gc, ec))
    determinant = pp*gg - pg*pg
    bp = (pe*gg-ge*pg)/determinant
    bg = (ge*pp-pe*pg)/determinant
    return {"N": n, "status": "ok", "a_j": em-bp*pm-bg*gm,
            "b_prompt_j_per_tok": bp, "b_gen_j_per_tok": bg,
            "_pm": pm, "_gm": gm, "_em": em, "_pp": pp, "_gg": gg,
            "_pg": pg, "_ge": ge, "_tss": math.fsum(v*v for v in ec), "_det": determinant}


def predict(fit, p, g):
    return fit["a_j"] + fit["b_prompt_j_per_tok"]*p + fit["b_gen_j_per_tok"]*g


def decompose(rows, confidence):
    fit = ols(rows)
    if fit["status"] != "ok":
        return fit, []
    n = len(rows)
    residuals = [r["energy_j"]-predict(fit, r["prompt_tokens"], r["generated_tokens"]) for r in rows]
    rss = math.fsum(r*r for r in residuals)
    sigma2 = rss/(n-3)
    pm, gm, pp, gg, pg, det = (fit[f"_{k}"] for k in ("pm", "gm", "pp", "gg", "pg", "det"))
    fit.update(a_se=math.sqrt(max(0, sigma2*(1/n + (pm*pm*gg-2*pm*gm*pg+gm*gm*pp)/det))),
               b_prompt_se=math.sqrt(sigma2*gg/det), b_gen_se=math.sqrt(sigma2*pp/det),
               r2=1-rss/fit["_tss"] if fit["_tss"] else None,
               r2_gen_only=fit["_ge"]**2/(gg*fit["_tss"]) if gg and fit["_tss"] else None,
               gen_share=fit["b_gen_j_per_tok"]*gm/fit["_em"])
    t = student_t_quantile((1+confidence)/2, n-3)
    for point, se, lower, upper in (("a_j", "a_se", "a_lo_j", "a_hi_j"),
                                  ("b_prompt_j_per_tok", "b_prompt_se", "b_prompt_lo", "b_prompt_hi"),
                                  ("b_gen_j_per_tok", "b_gen_se", "b_gen_lo", "b_gen_hi")):
        fit[lower], fit[upper] = fit[point]-t*fit[se], fit[point]+t*fit[se]
    by_level = defaultdict(list)
    for row, residual in zip(rows, residuals):
        by_level[row["level"]].append(residual)
    levels = []
    for level, values in sorted(by_level.items()):
        mean, lo, hi = mean_interval(values, confidence)
        if len(values) == 1:
            mean = values[0]
        levels.append(dict(level=level, m=len(values), mean_residual_j=mean, lo_j=lo, hi_j=hi,
                           contains_zero=int(lo <= 0 <= hi) if lo is not None else None))
    return fit, levels


def average(rows, field):
    return math.fsum(r[field] for r in rows)/len(rows) if rows else None


def percentile(values, confidence):
    if not values or any(v is None for v in values):
        return None, None
    ordered = sorted(values)
    k = max(1, math.floor(len(values)*(1-confidence)/2 + 1e-9))
    return ordered[k-1], ordered[-k]


def bootstrap(energy_levels, holdout_levels, config, variant, boundary, model, mode):
    """§8.7: all EN draws, then all HO draws, refit; keep replicate indices."""
    rng = random.Random(f"{config['bootstrap']['seed']}/{variant}/{boundary}/{model}/{mode}")
    en = {l: sorted(energy_levels[l], key=lambda r: r["item_id"]) for l in LEVELS}
    ho = {l: sorted(holdout_levels[l], key=lambda r: r["item_id"]) for l in LEVELS}
    output = {l: {"direct": [], "model": [], "residual": []} for l in LEVELS}
    for _ in range(config["bootstrap"]["replicates"]):
        es = {l: [en[l][rng.randrange(len(en[l]))] for _ in en[l]] for l in LEVELS}
        hs = {l: [ho[l][rng.randrange(len(ho[l]))] for _ in ho[l]] for l in LEVELS}
        fit = ols([r for l in LEVELS for r in es[l]])
        for l in LEVELS:
            values = output[l]
            em = average(es[l], "energy_j")
            residual = None
            if es[l] and fit["status"] == "ok":
                residual = em - predict(fit, average(es[l], "prompt_tokens"), average(es[l], "generated_tokens"))
            values["residual"].append(residual)
            direct = model_epc = None
            if es[l] and hs[l]:
                k = sum(r["correct"] for r in hs[l])
                ph = k/len(hs[l])
                direct = em/ph if k else math.inf
                if fit["status"] == "ok":
                    mu = predict(fit, average(hs[l], "prompt_tokens"), average(hs[l], "generated_tokens"))
                    if mu > 0:
                        model_epc = mu/ph if k else math.inf
            values["direct"].append(direct)
            values["model"].append(model_epc)
    return output


def make_cell(config, selection, variant, boundary, model, mode, level, b, e, h, raw_b, raw_e, fit, boot, misfit):
    confidence = config["descriptive_confidence"]
    row = dict.fromkeys(CELL_COLUMNS)
    n, k, m, nh, kh = len(b), sum(r["correct"] for r in b), len(e), len(h), sum(r["correct"] for r in h)
    nt = config["sizes"][mode]["bench"][str(level)]
    mt = config["sizes"][mode]["energy"][str(level)]
    status = "complete" if (n, nh, m) == (nt, nt-mt, mt) else "missing" if n == m == 0 else "short"
    p, plo, phi = wilson(k, n, confidence)
    ph, phlo, phhi = wilson(kh, nh, confidence)
    em, elo, ehi = mean_interval([r["energy_j"] for r in e], confidence)
    direct, dlo, dhi, direct_status = energy_per_correct(em, elo, ehi, ph, phlo, phhi, kh, m)
    mu = predict(fit, average(h, "prompt_tokens"), average(h, "generated_tokens")) if h and fit["status"] == "ok" else None
    model_epc = mu/ph if mu is not None and kh else None
    # §8.6 lists structural fit errors first, then level-specific errors.
    if fit["status"] != "ok":
        model_status = "fit_" + fit["status"]
    elif m < 2:
        model_status = "few_attempts"
    elif kh == 0:
        model_status = "zero_correct"
    elif mu <= 0:
        model_status = "nonpositive"
    elif any(v is None for v in boot["model"]):
        model_status = "bootstrap_invalid"
    else:
        model_status = "ok"
    mlo, mhi = percentile(boot["model"], confidence) if model_status == "ok" else (None, None)
    source, reason, point, lo, hi, epc_status = "", "", None, None, None, direct_status
    if model_status == "ok" and not misfit:
        source, point, epc_status = "model", model_epc, "ok"
    elif kh >= 1 and m >= 2:
        source, reason, point, epc_status = "direct", "misfit" if misfit else "model_" + model_status, direct, "ok"
    if source:
        lo, hi = percentile(boot[source], confidence)
    ratio, rlo, rhi = joules_per_token([r["energy_j"] for r in e], [r["generated_tokens"] for r in e], confidence)
    used_b, used_e = {id(r) for r in b}, {id(r) for r in e}
    bkeys, ekeys = {row_key(r) for r in b}, {row_key(r, True) for r in e}
    not_used_b = [r for r in raw_b if id(r) not in used_b]
    not_used_e = [r for r in raw_e if id(r) not in used_e]
    row.update(variant=variant, boundary=boundary, model=model, mode=mode, level=level, cell_status=status,
               n_bench_target=nt, n_bench=n, k_correct=k, accuracy=p, acc_lo=plo, acc_hi=phi,
               mean_generated_tokens_bench=average(b, "generated_tokens"), cap_hit_rate_bench=average(b, "cap_hit"),
               loop_rate_bench=sum("repetition_loop" in r["flags"] for r in b)/n if n else None,
               n_holdout_target=nt-mt, n_holdout=nh, k_holdout=kh, holdout_accuracy=ph,
               mean_prompt_tokens_holdout=average(h, "prompt_tokens"), mean_generated_tokens_holdout=average(h, "generated_tokens"),
               m_energy_target=mt, m_energy=m, mean_energy_j=em, energy_lo_j=elo, energy_hi_j=ehi,
               model_energy_j=mu, epc_model_j=model_epc, epc_model_lo_j=mlo, epc_model_hi_j=mhi, epc_model_status=model_status,
               epc_direct_j=direct, epc_direct_lo_j=dlo, epc_direct_hi_j=dhi, epc_direct_status=direct_status,
               epc_j=point, epc_lo_j=lo, epc_hi_j=hi, epc_status=epc_status, primary_source=source, primary_reason=reason,
               j_per_token=ratio, jpt_lo=rlo, jpt_hi=rhi,
               token_mismatch_count=sum("token_mismatch" in r["flags"] for r in e),
               rows_not_used=len(not_used_b)+len(not_used_e),
               replaced_rows=sum(row_key(r) in bkeys for r in not_used_b)+sum(row_key(r, True) in ekeys for r in not_used_e))
    return row


def ineligible(cell):
    if cell is None:
        return "not_measured"
    if cell["cell_status"] != "complete":
        return cell["cell_status"]
    if cell["epc_status"] != "ok":
        return cell["epc_status"]
    return ""


def log_replicates(x, y):
    return [0.0 if math.isinf(a) and math.isinf(b) else math.log(a)-math.log(b) for a, b in zip(x, y)]


def intervals(x, y, config):
    values = log_replicates(x, y)
    return (*percentile(values, config["descriptive_confidence"]), *percentile(values, config["decision_confidence"]))


def primary_verdict(rows):
    return "cheaper_size_changes_with_level" if len({r["cheaper"] for r in rows if r["status"] == "resolved"}) > 1 else "no_resolved_change"


def make_comparisons(config, variant, boundary, cells, draws):
    primary, rivals, crossovers = [], [], []
    a, b = (config["primary_comparison"][key] for key in ("a", "b"))
    parties = sorted(cells)
    for level in LEVELS:
        ca, cb = cells.get(a, {}).get(level), cells.get(b, {}).get(level)
        row = dict.fromkeys(PRIMARY_COLUMNS)
        row.update(variant=variant, boundary=boundary, level=level, a=a, b=b, cheaper="", reason="",
                   epc_a_j=ca["epc_j"] if ca else None, epc_b_j=cb["epc_j"] if cb else None,
                   source_a=ca["primary_source"] if ca else "", source_b=cb["primary_source"] if cb else "")
        failures = [f"{identifier}:{ineligible(cell)}" for identifier, cell in ((a, ca), (b, cb)) if ineligible(cell)]
        if failures:
            row.update(status="unresolved_incomplete", reason=";".join(failures))
        else:
            d = math.log(ca["epc_j"]/cb["epc_j"])
            dl, dh, cl, ch = intervals(draws[a][level], draws[b][level], config)
            cheaper = b if cl > 0 else a if ch < 0 else ""
            row.update(log_ratio=d, ratio=ca["epc_j"]/cb["epc_j"], desc_lo=dl, desc_hi=dh,
                       dec_lo=cl, dec_hi=ch, status="resolved" if cheaper else "unresolved", cheaper=cheaper)
        primary.append(row)
        eligible = [identifier for identifier in parties if not ineligible(cells[identifier][level])]
        incomplete = [f"{identifier}:{ineligible(cells[identifier][level])}" for identifier in parties if ineligible(cells[identifier][level])]
        cross = dict(variant=variant, boundary=boundary, level=level, cheapest="", cheapest_epc_j=None,
                     status="none_estimable", tied="", incomplete=";".join(incomplete))
        if not eligible:
            # No cheapest exists: there can be no rows 'other than cheapest'.
            crossovers.append(cross)
            continue
        cheapest = min(eligible, key=lambda identifier: (cells[identifier][level]["epc_j"], identifier))
        tied = []
        for rival in parties:
            if rival == cheapest:
                continue
            r = dict.fromkeys(RIVAL_COLUMNS)
            r.update(variant=variant, boundary=boundary, level=level, cheapest=cheapest, rival=rival, reason="")
            why = ineligible(cells[rival][level])
            if why:
                r["reason"] = f"{rival}:{why}"
            else:
                dl, dh, cl, ch = intervals(draws[rival][level], draws[cheapest][level], config)
                r.update(log_ratio=math.log(cells[rival][level]["epc_j"]/cells[cheapest][level]["epc_j"]),
                         desc_lo=dl, desc_hi=dh, dec_lo=cl, dec_hi=ch, beaten=int(cl > 0))
                if cl <= 0:
                    tied.append(rival)
            rivals.append(r)
        cross.update(cheapest=cheapest, cheapest_epc_j=cells[cheapest][level]["epc_j"], tied=";".join(tied),
                     status="unresolved_incomplete" if incomplete else "unresolved" if tied else "resolved")
        crossovers.append(cross)
    winners = {str(r["level"]): r["cheapest"] for r in crossovers if r["status"] == "resolved"}
    summary = {"primary_question": {"verdict": primary_verdict(primary), "levels": {
        str(r["level"]): {key: r[key] for key in ("status", "cheaper", "log_ratio", "dec_lo", "dec_hi")} for r in primary}},
        "secondary": {"verdict": "crossover_resolved" if len(set(winners.values())) > 1 else "no_resolved_crossover", "resolved_winners": winners}}
    return primary, rivals, crossovers, summary


def analyze(config, selections, bench, energy):
    braw, eraw = parse_tables(bench, energy, config, selections)
    present = {row_key(r)[:2] for r in braw + eraw}
    roster = {f"{c['model']}/{c['mode']}": "not_measured" if c["status"] == "optional" and (c["model"], c["mode"]) not in present else c["status"] for c in config["configurations"]}
    parties = sorted((c for c in config["configurations"] if roster[f"{c['model']}/{c['mode']}"] != "not_measured"), key=lambda c: (c["model"], c["mode"]))
    tables = {name: [] for name in SCHEMAS}
    summary = {"variants": {}, "roster": roster, "targets": config["sizes"],
               "descriptive_confidence": config["descriptive_confidence"], "decision_confidence": config["decision_confidence"],
               "bootstrap": config["bootstrap"], "python_version": platform.python_version(),
               "exclusions": {"always": sorted(ALWAYS | {"missing_text"}), "exclude_flags": config["exclude_flags"],
                              "physical_exclude_flags": config["physical_exclude_flags"]},
               "flag_counts": {role: dict(sorted(Counter(f for r in rows for f in r["flags"]).items())) for role, rows in (("bench", braw), ("energy", eraw))},
               "selection_size_mismatch": [f"selection_size_mismatch:{mode}:{role}:{l}" for mode in ("off", "on") for role in ("bench", "energy") for l in map(str, LEVELS) if len(selections[mode][role][l]) != config["sizes"][mode][role][l]]}
    for variant in VARIANTS:
        b = used_rows(braw, exclusion(config, variant))
        e = used_rows(eraw, exclusion(config, variant, True), True)
        summary["variants"][variant] = {}
        for boundary in sorted(config["boundaries"]):
            cells, draws, misfits = {}, {}, []
            for party in parties:
                model, mode = party["model"], party["mode"]
                identifier = model + "/" + mode
                def bench_cell(r, l):
                    return (r["model"], r["mode"], r["level"]) == (model, mode, l) and not r["flags"] & {"bad_level", "bad_mode"}
                def energy_cell(r, l):
                    return r["boundary"] == boundary and bench_cell(r, l)
                bl = {l: sorted([r for r in b if bench_cell(r, l)], key=lambda r: r["item_id"]) for l in LEVELS}
                el = {l: sorted([r for r in e if energy_cell(r, l)], key=lambda r: r["item_id"]) for l in LEVELS}
                hl = {l: [r for r in bl[l] if r["item_id"] not in selections[mode]["energy"][str(l)]] for l in LEVELS}
                pooled = [r for l in LEVELS for r in el[l]]
                fit, residuals = decompose(pooled, config["descriptive_confidence"])
                identity = dict(variant=variant, boundary=boundary, model=model, mode=mode)
                tables["decomposition.csv"].append(identity | {k: v for k, v in fit.items() if not k.startswith("_")})
                boot = bootstrap(el, hl, config, variant, boundary, model, mode)
                tol = 1e-9*max(1, average(pooled, "energy_j") or 0)
                misfit_levels = set()
                for residual in residuals:
                    l = residual["level"]
                    # NEEDS_RULING: §8.7 specifies B order statistics but does
                    # not say how §8.8 handles a singular refit's missing r*.
                    # Best reading: a partial list cannot form that interval.
                    lo, hi = percentile(boot[l]["residual"], config["descriptive_confidence"])
                    misfit = lo is not None and (lo > tol or hi < -tol)
                    residual.update(boot_lo_j=lo, boot_hi_j=hi, misfit=int(misfit))
                    tables["level_residuals.csv"].append(identity | residual)
                    if misfit:
                        misfit_levels.add(l)
                        misfits.append(f"{identifier}:{l}")
                cells[identifier], draws[identifier] = {}, {}
                for l in LEVELS:
                    cell = make_cell(config, selections, variant, boundary, model, mode, l, bl[l], el[l], hl[l],
                                     [r for r in braw if bench_cell(r, l)], [r for r in eraw if energy_cell(r, l)], fit, boot[l], l in misfit_levels)
                    tables["cells.csv"].append(cell)
                    cells[identifier][l] = cell
                    draws[identifier][l] = boot[l][cell["primary_source"]] if cell["primary_source"] else []
            primary, rivals, crossovers, part_summary = make_comparisons(config, variant, boundary, cells, draws)
            tables["primary.csv"].extend(primary)
            tables["rivals.csv"].extend(rivals)
            tables["crossover.csv"].extend(crossovers)
            summary["variants"][variant][boundary] = part_summary | {"misfit_cells": sorted(misfits)}
    summary["method_note"] = (
        "Primary EPC uses a pooled token model per configuration and holdout token means; direct EPC is secondary. "
        "The descriptive bootstrap residual interval excluding zero beyond 1e-9 times pooled mean energy switches misfit cells to direct: "
        + json.dumps({v: {b: s['misfit_cells'] for b, s in bs.items()} for v, bs in summary['variants'].items()}, sort_keys=True)
        + f". Problem-level bootstrap is stratified by level, B={config['bootstrap']['replicates']}, percentile order statistics. "
        + f"Descriptive confidence {config['descriptive_confidence']}; decisions use only {config['decision_confidence']}. "
        "Incomplete parties keep comparisons unresolved. Excluded attempts may be retried; after the first primary-usable attempt later runs are duplicates. "
        "Flagged-inclusive uses the first physically flagged attempt, retaining one row per problem. Level is a published stratum, not a cause."
    )
    for name, rows in tables.items():
        rows.sort(key=lambda r: tuple(r[k] for k in KEYS[name]))
    return tables, summary


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow("" if row.get(c) is None else repr(row[c]) if isinstance(row[c], float) else str(row[c]) for c in columns)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("config", "selections", "bench", "energy", "out"):
        parser.add_argument("--" + option, type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        config = validate_config(json.loads(args.config.read_text(encoding="utf-8")))
        selection_file = json.loads(args.selections.read_text(encoding="utf-8"))
        selections = selection_file["selections"]
        # Selection-length mismatch is data, not an invalid config (§7).
        for mode in ("off", "on"):
            for role in ("bench", "energy"):
                for l in map(str, LEVELS):
                    values = selections[mode][role][l]
                    if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
                        raise ValueError(f"invalid selections: {mode}/{role}/{l}")
        bench = read_table(args.bench, BENCH_COLUMNS)
        energy = read_table(args.energy, ENERGY_COLUMNS)
        tables, summary = analyze(config, selections, bench, energy)
        args.out.mkdir(parents=True, exist_ok=True)
        for name, columns in SCHEMAS.items():
            write_csv(args.out/name, columns, tables[name])
        (args.out/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, csv.Error, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
