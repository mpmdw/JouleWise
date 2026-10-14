#!/usr/bin/env python3
"""Independent stdlib DIFFICULTY recomputation, derived from SPEC.md v1.1.

No production estimator is imported. Parsing, t inversion, centred least
squares, and interval propagation are independently implemented here.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from functools import lru_cache
import json
import math
import re
from statistics import NormalDist
import sys
from pathlib import Path


BENCH_COLUMNS = (
    "model", "mode", "item_id", "level", "outcome", "correct",
    "prompt_tokens", "generated_tokens", "cap_hit", "flags",
)
ENERGY_COLUMNS = (
    "model", "mode", "level", "item_id", "boundary", "energy_j",
    "prompt_tokens", "generated_tokens", "flags",
)
CELL_COLUMNS = (
    "boundary", "model", "mode", "level", "n_bench", "k_correct",
    "accuracy", "acc_lo", "acc_hi", "mean_generated_tokens_bench",
    "cap_hit_rate_bench", "m_energy", "mean_energy_j", "energy_lo_j",
    "energy_hi_j", "n_holdout", "k_holdout", "epc_j", "epc_lo_j", "epc_hi_j", "epc_status",
    "j_per_token", "jpt_lo", "jpt_hi", "token_mismatch_count", "excluded_rows",
)
DECOMPOSITION_COLUMNS = (
    "boundary", "model", "mode", "N", "a_j", "a_se", "b_prompt_j_per_tok",
    "b_prompt_se", "b_gen_j_per_tok", "b_gen_se", "r2", "r2_gen_only",
    "gen_share", "status",
)
RESIDUAL_COLUMNS = (
    "boundary", "model", "mode", "level", "m", "mean_residual_j",
    "lo_j", "hi_j", "contains_zero",
)
CROSSOVER_COLUMNS = (
    "boundary", "level", "cheapest", "cheapest_epc_j", "status", "tied",
)
ENERGY_ALWAYS_EXCLUDE = {
    "bad_number", "bad_level", "bad_mode", "duplicate", "unknown_item",
    "unknown_config",
}
BENCH_ALWAYS_EXCLUDE = {
    "unknown_item", "unknown_config", "duplicate", "bad_number", "missing_text",
    "bad_level", "bad_mode",
}


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


def parse_tables(bench, energy, exclude_flags):
    bench_cells = defaultdict(list)
    bench_lookup = {}
    bench_flag_counts, energy_flag_counts = Counter(), Counter()
    for raw in bench:
        row = dict(raw)
        row["level"] = _integer(raw.get("level"))
        for field in ("prompt_tokens", "generated_tokens", "correct", "cap_hit"):
            row[field] = _integer(raw.get(field), 0, 1 if field in {"correct", "cap_hit"} else None)
        flags = _flags(raw.get("flags"))
        if row["level"] not in range(1, 6):
            flags.add("bad_level")
        if row["mode"] not in {"off", "on"}:
            flags.add("bad_mode")
        if any(row[field] is None for field in ("prompt_tokens", "generated_tokens", "correct", "cap_hit")):
            flags.add("bad_number")
        identity = (row["model"], row["mode"], row["item_id"])
        if identity in bench_lookup:
            flags.add("duplicate")
        bench_flag_counts.update(flags)
        bench_lookup.setdefault(identity, row)
        if row["level"] is not None and not flags & (BENCH_ALWAYS_EXCLUDE | exclude_flags):
            bench_cells[row["model"], row["mode"], row["level"]].append(row)

    energy_cells = defaultdict(list)
    excluded = Counter()
    seen = set()
    for raw in energy:
        row = dict(raw)
        flags = _flags(raw.get("flags"))
        row["level"] = _integer(raw.get("level"))
        if row["level"] not in range(1, 6):
            flags.add("bad_level")
        if row["mode"] not in {"off", "on"}:
            flags.add("bad_mode")
        try:
            value = float(raw.get("energy_j") or "")
        except (ValueError, OverflowError):
            value = math.nan
        row["energy_j"] = value
        for field in ("prompt_tokens", "generated_tokens"):
            row[field] = _integer(raw.get(field))
        if not math.isfinite(value) or value <= 0.0 or any(row[field] is None for field in ("prompt_tokens", "generated_tokens")):
            flags.add("bad_number")
        identity = (row["boundary"], row["model"], row["mode"], row["item_id"])
        if identity in seen:
            flags.add("duplicate")
        seen.add(identity)
        reference = bench_lookup.get((row["model"], row["mode"], row["item_id"]))
        if reference is None:
            flags.add("not_in_bench")
        else:
            if row["level"] != reference["level"]:
                flags.add("level_mismatch")
            if (row["generated_tokens"] is not None and reference["generated_tokens"] is not None
                    and row["generated_tokens"] != reference["generated_tokens"]):
                flags.add("token_mismatch")
        row["flags"] = flags
        energy_flag_counts.update(flags)
        key = (row["boundary"], row["model"], row["mode"], row["level"])
        if flags & (ENERGY_ALWAYS_EXCLUDE | exclude_flags):
            if not flags & {"bad_level", "bad_mode"}:
                excluded[key] += 1
        else:
            energy_cells[key].append(row)
    return bench_cells, energy_cells, excluded, bench_flag_counts, energy_flag_counts


def make_cells(bench_cells, energy_cells, excluded, confidence, energy_items):
    boundaries = {key[0] for key in energy_cells}
    keys = set(energy_cells)
    keys.update((boundary, *key) for boundary in boundaries for key in bench_cells)
    result = []
    for boundary, model, mode, level in sorted(keys):
        key = (boundary, model, mode, level)
        b = bench_cells.get((model, mode, level), [])
        e = energy_cells.get(key, [])
        n, k, m = len(b), sum(row["correct"] for row in b), len(e)
        p, plo, phi = wilson(k, n, confidence)
        holdout = [row for row in b if row["item_id"] not in energy_items[model, mode]]
        nh, kh = len(holdout), sum(row["correct"] for row in holdout)
        ph, phlo, phhi = wilson(kh, nh, confidence)
        energies = [row["energy_j"] for row in e]
        mean, elo, ehi = mean_interval(energies, confidence)
        epc, epclo, epchi, status = energy_per_correct(mean, elo, ehi, ph, phlo, phhi, kh, m)
        ratio, rlo, rhi = joules_per_token(energies, [row["generated_tokens"] for row in e], confidence)
        result.append(dict(zip(CELL_COLUMNS, (
            boundary, model, mode, level, n, k, p, plo, phi,
            math.fsum(row["generated_tokens"] for row in b)/n if n else None,
            sum(row["cap_hit"] for row in b)/n if n else None,
            m, mean, elo, ehi, nh, kh, epc, epclo, epchi, status, ratio, rlo, rhi,
            sum("token_mismatch" in row["flags"] for row in e), excluded[key],
        ))))
    return result


def decompose(rows, confidence):
    """Solve centred two-predictor normal equations and recover intercept."""
    n = len(rows)
    output = {column: None for column in DECOMPOSITION_COLUMNS[3:]}
    output["N"] = n
    if n < 4:
        output["status"] = "few_rows"
        return output, []
    p = [row["prompt_tokens"] for row in rows]
    g = [row["generated_tokens"] for row in rows]
    e = [row["energy_j"] for row in rows]
    pm, gm, em = (math.fsum(values)/n for values in (p, g, e))
    pc, gc, ec = ([value-mean for value in values] for values, mean in ((p, pm), (g, gm), (e, em)))
    pp = math.fsum(value*value for value in pc)
    gg = math.fsum(value*value for value in gc)
    pg = math.fsum(x*y for x, y in zip(pc, gc))
    pe = math.fsum(x*y for x, y in zip(pc, ec))
    ge = math.fsum(x*y for x, y in zip(gc, ec))
    determinant = pp*gg-pg*pg
    if determinant <= 0.0:
        output["status"] = "singular"
        return output, []
    bp = (pe*gg-ge*pg)/determinant
    bg = (ge*pp-pe*pg)/determinant
    a = em-bp*pm-bg*gm
    residuals = [energy-(a+bp*prompt+bg*generated) for prompt, generated, energy in zip(p, g, e)]
    rss = math.fsum(value*value for value in residuals)
    tss = math.fsum(value*value for value in ec)
    sigma2 = rss/(n-3)
    output.update(
        a_j=a, a_se=math.sqrt(sigma2*(1/n+(pm*pm*gg-2*pm*gm*pg+gm*gm*pp)/determinant)),
        b_prompt_j_per_tok=bp, b_prompt_se=math.sqrt(sigma2*gg/determinant),
        b_gen_j_per_tok=bg, b_gen_se=math.sqrt(sigma2*pp/determinant),
        r2=1-rss/tss if tss else None,
        r2_gen_only=ge*ge/(gg*tss) if gg and tss else None,
        gen_share=bg*gm/em, status="ok",
    )
    by_level = defaultdict(list)
    for row, residual in zip(rows, residuals):
        by_level[row["level"]].append(residual)
    levels = []
    for level, values in sorted(by_level.items()):
        mean, lo, hi = mean_interval(values, confidence)
        # Section 5.5 defines the level mean even for one residual. Only
        # its t interval requires a positive df; section 5.2's blank mean
        # rule applies specifically to whole-request energy per attempt.
        if len(values) == 1:
            mean = values[0]
        levels.append(dict(zip(RESIDUAL_COLUMNS[3:], (
            level, len(values), mean, lo, hi,
            int(lo <= 0.0 <= hi) if lo is not None else None,
        ))))
    return output, levels


def make_decompositions(energy_cells, confidence):
    pooled = defaultdict(list)
    for key, rows in sorted(energy_cells.items()):
        pooled[key[:3]].extend(rows)
    decomposition, residuals = [], []
    for key, rows in sorted(pooled.items()):
        identity = dict(zip(DECOMPOSITION_COLUMNS[:3], key))
        fit, levels = decompose(rows, confidence)
        decomposition.append(identity | fit)
        residuals.extend(identity | level for level in levels)
    return decomposition, residuals


def make_crossovers(cells):
    groups = defaultdict(list)
    for row in cells:
        groups[row["boundary"], row["level"]].append(row)
    result, summary = [], {}
    for (boundary, level), rows in sorted(groups.items()):
        eligible = [row for row in rows if row["epc_status"] in {"ok", "energy_lower_nonpositive"}]
        if not eligible:
            result.append(dict(zip(CROSSOVER_COLUMNS, (boundary, level, None, None, "none_estimable", ""))))
            summary.setdefault(boundary, {})
            continue
        cheapest = min(eligible, key=lambda row: (row["epc_j"], row["model"], row["mode"]))
        tied = []
        for rival in eligible:
            if rival is cheapest:
                continue
            lower = -math.inf if rival["epc_lo_j"] == 0.0 else (
                math.log(rival["epc_j"]/cheapest["epc_j"])
                - math.hypot(math.log(rival["epc_j"]/rival["epc_lo_j"]), math.log(cheapest["epc_hi_j"]/cheapest["epc_j"]))
            )
            if lower <= 0.0:
                tied.append(f"{rival['model']}/{rival['mode']}")
        status = "unresolved" if tied else "resolved"
        winner = f"{cheapest['model']}/{cheapest['mode']}"
        result.append(dict(zip(CROSSOVER_COLUMNS, (boundary, level, winner, cheapest["epc_j"], status, ";".join(sorted(tied))))))
        winners = summary.setdefault(boundary, {})
        if status == "resolved":
            winners[str(level)] = winner
    return result, {
        boundary: {"verdict": "crossover_resolved" if len(set(winners.values())) > 1 else "no_resolved_crossover", "resolved_winners": winners}
        for boundary, winners in sorted(summary.items())
    }


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow("" if row.get(column) is None else repr(row[column]) if isinstance(row[column], float) else str(row[column]) for column in columns)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bench", required=True, type=Path)
    parser.add_argument("--energy", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--exclude-flags", default="runtime_failed")
    args = parser.parse_args(argv)
    if not math.isfinite(args.confidence) or not 0 < args.confidence < 1 or (1+args.confidence)/2 == 1:
        parser.error("--confidence must be strictly between 0 and 1")
    try:
        bench = read_table(args.bench, BENCH_COLUMNS)
        energy = read_table(args.energy, ENERGY_COLUMNS)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        parser.error(str(error))
    exclude = {flag.strip() for flag in args.exclude_flags.split(",") if flag.strip()}
    b, e, excluded, bench_flags, energy_flags = parse_tables(bench, energy, exclude)
    energy_items = defaultdict(set)
    for row in energy:
        energy_items[row["model"], row["mode"]].add(row["item_id"])
    cells = make_cells(b, e, excluded, args.confidence, energy_items)
    decompositions, residuals = make_decompositions(e, args.confidence)
    crossovers, boundary_summary = make_crossovers(cells)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename, columns, rows in (
        ("cells.csv", CELL_COLUMNS, cells),
        ("decomposition.csv", DECOMPOSITION_COLUMNS, decompositions),
        ("level_residuals.csv", RESIDUAL_COLUMNS, residuals),
        ("crossover.csv", CROSSOVER_COLUMNS, crossovers),
    ):
        write_csv(args.out / filename, columns, rows)
    summary = {
        "boundaries": boundary_summary, "confidence": args.confidence,
        "flag_counts": {"bench": dict(sorted(bench_flags.items())), "energy": dict(sorted(energy_flags.items()))},
        "method_note": (
            "Wilson accuracy intervals and Student t energy intervals are combined by log-scale MOVER. "
            "EPC accuracy uses the used bench problems outside the energy subset, excluding every item "
            "with an energy row for the same model and mode across all boundaries, flagged or not. "
            "The combined intervals are independent; headline accuracy uses all used bench problems. "
            "Crossover comparisons treat configurations as independent despite "
            "shared problems; correlated accuracies would narrow the ratio interval, so the rule errs "
            "toward unresolved. Confidence is unadjusted for multiple comparisons."
        ),
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
