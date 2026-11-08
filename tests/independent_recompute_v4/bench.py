"""Speed bench for the v4 independent recompute (synthetic only). Not a test; run by hand.

    python3.13 -B tests/independent_recompute_v4/bench.py series --dir D [--period-s 5] [--workers 1 10]
    python3.13 -B tests/independent_recompute_v4/bench.py member --dir D [--frames 9640] [--copies 10]

``series`` writes an 11-window x 22-member series with realistic 52.6 kB frames (fewer frames per member
than a real 960 s capture, to fit the disk) and times the full recompute serially and in parallel,
cold, cache-miss and cache-hit, checking the outputs are byte-identical. ``member`` writes one full-size
member (9,640 frames, about 507 MB) and times its reduction alone and, with hard-linked copies, in a pool.
"""
import argparse
import concurrent.futures
import json
import multiprocessing
import os
from pathlib import Path
import random
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
import synth  # noqa: E402
import independent_recompute_v4 as rc  # noqa: E402


def series(args):
    root = Path(args.dir) / "series"
    if not root.exists():
        t0 = time.perf_counter()
        synth.write_series(root, period_ns=int(args.period_s * 1e9), w1=False, saboteur_extra=20.0)
        print(json.dumps({"write_s": time.perf_counter() - t0}))
    raw = sum(p.stat().st_size for p in root.rglob("powermetrics.plist"))
    members = sum(1 for _ in root.rglob("powermetrics.plist"))
    rows, outputs = [], {}
    for workers in args.workers:
        for mode in ("cold", "miss", "hit"):
            cache = None if mode == "cold" else Path(args.dir) / f"cache-{workers}"
            if mode == "miss" and cache.exists():
                shutil.rmtree(cache)
            timings = {}
            t0 = time.perf_counter()
            out = rc.recompute(root, workers=workers, cache_dir=cache, timings=timings)
            wall = time.perf_counter() - t0
            data = rc.canonical(out)
            outputs[(workers, mode)] = data
            rows.append({"workers": workers, "mode": mode, "wall_s": round(wall, 3),
                         "member_stage_s": round(timings["member_stage_s"], 3),
                         "fit_stage_s": round(timings["fit_stage_s"], 3),
                         "decision_stage_s": round(timings["decision_stage_s"], 3),
                         "raw_MB_per_s": round(raw / 1e6 / timings["member_stage_s"], 1)})
            print(json.dumps(rows[-1]), flush=True)
    identical = len(set(outputs.values())) == 1
    print(json.dumps({"members": members, "raw_bytes": raw, "outputs_byte_identical": identical}))


def member(args):
    base = Path(args.dir) / "member"
    first = base / "windows/C1/members/m00"
    raw = first / "raw/powermetrics.plist"
    if not raw.exists():
        rng = random.Random(3)
        m = synth.Member("m00", "spam", "benign", "benign", "D", 0, rng, 8, (40.0, 0.004, 0.25, 2e-6, 1e-7), 3.0,
                         100_000_000, synth.FrameTemplate())
        m.run_id = "m00"
        synth.write_member(base, "C1", m, synth.EPOCH0_S * synth.NS, full_frames=args.frames)
    for i in range(1, args.copies):
        d = base / f"windows/C1/members/m{i:02d}"
        if not d.exists():
            shutil.copytree(first, d, copy_function=os.link)
    size = raw.stat().st_size
    t0 = time.perf_counter()
    red = rc.reduce_stream(raw)
    t_reduce = time.perf_counter() - t0
    t0 = time.perf_counter()
    rc.file_sha256(raw)
    t_hash = time.perf_counter() - t0
    t0 = time.perf_counter()
    rc.fast_frame  # noqa: B018
    frames = red["counts"]["frames"]
    tasks = [("C1", f"m{i:02d}", str(base / f"windows/C1/members/m{i:02d}"), None) for i in range(args.copies)]
    t0 = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(args.copies, mp_context=multiprocessing.get_context("spawn")) as pool:
        list(pool.map(rc.process_member, tasks, chunksize=1))
    t_pool = time.perf_counter() - t0
    print(json.dumps({"raw_bytes": size, "frames": frames, "reduce_serial_s": round(t_reduce, 3),
                      "reduce_MB_per_s_one_core": round(size / 1e6 / t_reduce, 1),
                      "sha256_only_s": round(t_hash, 3), "pool_members": args.copies,
                      "pool_wall_s": round(t_pool, 3),
                      "pool_MB_per_s": round(args.copies * size / 1e6 / t_pool, 1),
                      "note": "hard-linked copies share one inode: page-cache warm, CPU-bound figure"}))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("series")
    s.add_argument("--dir", required=True)
    s.add_argument("--period-s", type=float, default=5.0)
    s.add_argument("--workers", type=int, nargs="+", default=[1, 10])
    m = sub.add_parser("member")
    m.add_argument("--dir", required=True)
    m.add_argument("--frames", type=int, default=9640)
    m.add_argument("--copies", type=int, default=10)
    args = p.parse_args()
    (series if args.cmd == "series" else member)(args)


if __name__ == "__main__":
    main()
