#!/usr/bin/env python3
"""Resident-memory and per-token latency of the off-GPU n-gram table.

Builds a SCALED synthetic table with the real row geometry (160-dim rows, the
real Flash-Next hash spec: 16 heads, splitmix multipliers, ~20M primes) and
measures the host gather path the model runs every forward:

    hash (numpy int64) -> row gather (mmap or pread) -> dequantize -> mx.array

Run with the pinned MLX venv, e.g.::

    nice -n 10 /path/to/venv-mlx/bin/python scripts/align_qwen4_exp_twin_ngram_bench.py \
        --dir /private/tmp/jwtwin-tmp/ngram_bench --rows 6000000 --format q4

The table is written through an ``F_NOCACHE`` descriptor so its pages are not
left in the file cache; the first mmap pass is therefore (mostly) cold.
Hashed ids are reduced modulo the scaled row count, which keeps the access
pattern uniform-random like the real 320,001,536-row table.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / ".engine" / "hf-flashnext" / "config.json"
PAGE = os.sysconf("SC_PAGE_SIZE")


def rss_bytes() -> int:
    out = subprocess.run(["ps", "-o", "rss=", "-p", str(os.getpid())],
                         capture_output=True, text=True, check=True).stdout
    return int(out.strip()) * 1024


def majflt() -> int:
    return resource.getrusage(resource.RUSAGE_SELF).ru_majflt


def build_table(tw, np, path: Path, rows: int, dim: int, fmt: str, group: int, seed: int):
    rec = tw.ngram_record_layout(fmt, dim, group)["record_bytes"]
    rng = np.random.default_rng(seed)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        fcntl.fcntl(fd, 48, 1)  # F_NOCACHE
        chunk = 1 << 17
        for lo in range(0, rows, chunk):
            n = min(chunk, rows - lo)
            block = tw.encode_ngram_rows(rng.standard_normal((n, dim), dtype=np.float32), fmt, group)
            os.write(fd, block.tobytes())
    finally:
        os.close(fd)
    return rec


def pct(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(q * (len(values) - 1) + 0.5))]


def run_pass(tw, np, mx, spec, table, tokens, rows, prefill_len, eos):
    """Decode-style: one token per call, then one prefill-sized call.

    Timed per token, host side only (what the model adds to each step before
    its graph is built): hash, row gather + dequantize, and creation of the
    lazy bf16 mx.array. No extra ``mx.eval``: inside the model this array is
    part of the step graph, so it adds no GPU round trip of its own.
    """
    ctx = np.full((1, spec.context_len), eos, dtype=np.int64)
    lat_total, lat_hash, lat_gather, lat_mx, keep = [], [], [], [], []
    rss0, flt0, mx0 = rss_bytes(), majflt(), mx.get_active_memory()
    for tok in tokens:
        t0 = time.perf_counter()
        hist = np.concatenate([ctx, np.array([[tok]], dtype=np.int64)], axis=1)
        ids = spec.ngram_ids(hist, 1) % rows
        t1 = time.perf_counter()
        rows_f32 = table.gather(ids)
        t2 = time.perf_counter()
        emb = mx.array(rows_f32.reshape(1, 1, -1)).astype(mx.bfloat16)
        t3 = time.perf_counter()
        keep.append(emb)
        if len(keep) == 64:                 # evaluate off the clock, in batches
            mx.eval(keep)
            keep = []
        ctx = hist[:, -spec.context_len:]
        lat_hash.append((t1 - t0) * 1e6)
        lat_gather.append((t2 - t1) * 1e6)
        lat_mx.append((t3 - t2) * 1e6)
        lat_total.append((t3 - t0) * 1e6)
    mx.eval(keep)
    rss1, flt1, mx1 = rss_bytes(), majflt(), mx.get_active_memory()
    pre = np.asarray(tokens[:prefill_len], dtype=np.int64)[None, :]
    hist = np.concatenate([np.full((1, spec.context_len), eos, np.int64), pre], axis=1)
    t0 = time.perf_counter()
    ids = spec.ngram_ids(hist, pre.shape[1]) % rows
    emb = mx.array(table.gather(ids).reshape(1, pre.shape[1], -1)).astype(mx.bfloat16)
    mx.eval(emb)
    prefill_ms = (time.perf_counter() - t0) * 1e3
    n = len(tokens)
    return {
        "tokens": n,
        "per_token_us": {"mean": statistics.fmean(lat_total), "p50": pct(lat_total, 0.5),
                         "p90": pct(lat_total, 0.9), "p99": pct(lat_total, 0.99),
                         "max": max(lat_total)},
        "hash_us_mean": statistics.fmean(lat_hash),
        "gather_dequant_us_mean": statistics.fmean(lat_gather),
        "gather_dequant_us_p99": pct(lat_gather, 0.99),
        "to_mx_us_mean": statistics.fmean(lat_mx),
        "rss_growth_mb": (rss1 - rss0) / 1e6,
        "rss_growth_kb_per_token": (rss1 - rss0) / 1e3 / n,
        "rss_after_mb": rss1 / 1e6,
        "major_faults": flt1 - flt0,
        "major_faults_per_token": (flt1 - flt0) / n,
        "mlx_active_growth_bytes": mx1 - mx0,
        "prefill_tokens": int(pre.shape[1]),
        "prefill_gather_ms": prefill_ms,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", required=True, type=Path)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--rows", type=int, default=6_000_000)
    ap.add_argument("--format", default="q4", choices=("q8", "q4", "bf16"))
    ap.add_argument("--group-size", type=int, default=32)
    ap.add_argument("--tokens", type=int, default=2048)
    ap.add_argument("--prefill", type=int, default=2048)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--keep", action="store_true", help="keep the synthetic table")
    opts = ap.parse_args(argv)

    sys.path.insert(0, str(REPO_ROOT))
    import mlx.core as mx
    import numpy as np
    from joulewise.align.models import qwen4_exp_twin as tw

    cfg = json.loads(opts.config.read_text())
    args = tw.TextModelArgs.from_dict(cfg.get("text_config", cfg))
    spec = tw.NgramHashSpec(args, 0)
    real_rec = {f: tw.ngram_record_layout(f, spec.head_dim, opts.group_size)["record_bytes"]
                for f in ("q4", "q8", "bf16")}
    opts.dir.mkdir(parents=True, exist_ok=True)
    path = opts.dir / f"synthetic.{opts.format}.bin"

    t0 = time.perf_counter()
    rec = build_table(tw, np, path, opts.rows, spec.head_dim, opts.format, opts.group_size, opts.seed)
    build_s = time.perf_counter() - t0

    rng = np.random.default_rng(opts.seed + 1)
    tokens = rng.integers(0, args.vocab_size, size=opts.tokens).tolist()
    for i in range(0, len(tokens), 211):
        tokens[i] = args.eos_id                  # occasional EOS resets

    result = {
        "table": {"rows": opts.rows, "dim": spec.head_dim, "format": opts.format,
                  "group_size": opts.group_size, "record_bytes": rec,
                  "bytes": path.stat().st_size, "build_seconds": build_s,
                  "scale_vs_real_rows": opts.rows / spec.padded_vocab_size},
        "real_table": {"rows": spec.padded_vocab_size, "heads": spec.ngram_heads,
                       "bytes_by_format": {f: r * spec.padded_vocab_size for f, r in real_rec.items()},
                       "lookups_per_token": spec.ngram_heads},
        "page_bytes": PAGE,
        "passes": {},
    }
    base_rss = rss_bytes()
    result["process_rss_before_mb"] = base_rss / 1e6
    # A second, byte-identical file gives an independent cold mapping for the
    # prefetch pass (no root needed to drop the file cache).
    path_b = opts.dir / f"synthetic_b.{opts.format}.bin"
    build_table(tw, np, path_b, opts.rows, spec.head_dim, opts.format, opts.group_size, opts.seed)

    def table(p, io, prefetch):
        return tw.NgramTable(p, opts.rows, spec.head_dim, opts.format, opts.group_size,
                             io=io, prefetch=prefetch)

    pread_t = table(path, "pread", False)
    result["passes"]["pread_nocache"] = run_pass(tw, np, mx, spec, pread_t, tokens, opts.rows,
                                                 opts.prefill, args.eos_id)
    pread_t.close()
    mm_a = table(path, "mmap", False)
    result["passes"]["mmap_cold_no_prefetch"] = run_pass(tw, np, mx, spec, mm_a, tokens, opts.rows,
                                                         opts.prefill, args.eos_id)
    result["passes"]["mmap_warm"] = run_pass(tw, np, mx, spec, mm_a, tokens, opts.rows,
                                             opts.prefill, args.eos_id)
    mm_b = table(path_b, "mmap", True)
    result["passes"]["mmap_cold_prefetch"] = run_pass(tw, np, mx, spec, mm_b, tokens, opts.rows,
                                                      opts.prefill, args.eos_id)
    result["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    # Upper bound for the REAL table: every lookup in a distinct page.
    result["real_page_cache_upper_bound"] = {
        "bytes_per_token": spec.ngram_heads * PAGE,
        "bytes_at_40960_tokens": min(spec.ngram_heads * PAGE * 40960,
                                     real_rec[opts.format] * spec.padded_vocab_size),
    }
    if not opts.keep:
        path.unlink()
        path_b.unlink()
    text = json.dumps(result, indent=2)
    if opts.json:
        opts.json.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
