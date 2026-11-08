#!/usr/bin/env python3
"""Compression benchmark for the Air offload on synthetic powermetrics-plist-shaped data.

The generator is calibrated on the two real committed M3 Max (Mac15,9) captures in
tests/fixtures (10 Hz, samplers cpu_power,gpu_power,ane_power,thermal): it keeps their exact
XML skeleton and re-draws every field that varies between real samples. `--validate` compares
the synthetic and real compression ratios at equal sample counts. A synthetic member bundle
follows the pilot-v3 inventory (configs/campaigns/align_pilot_v3/registration/sizing_evidence.json):
three plists 89.4 %, rich telemetry 9.3 %, small files the rest. Docs: docs/ops/AIR-OFFLOAD-opus.md.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import random
import re
import resource
import shutil
import statistics
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = (ROOT / "tests/fixtures/d078_r01/raw/powermetrics.plist", ROOT / "tests/fixtures/powermetrics_sample.plist")
SLOT = re.compile(rb"<(integer|real|date)>([^<]*)</\1>")
# Mean bytes per pilot-v3 member (sizing_evidence.json member_observations, n = 24).
MEMBER = {"raw/powermetrics.plist": 212.84e6, "raw/powermetrics_idle.plist": 157.01e6,
          "instrument_calibration/raw/powermetrics.plist": 83.58e6, "rich_telemetry.jsonl": 27.10e6,
          "rich_telemetry_idle.jsonl": 19.91e6, "raw/powermetrics_idle_post.plist": 2.62e6,
          "outputs/align_turns.jsonl": 1.48e6, "power_trace.csv": 1.05e6, "events.jsonl": 0.57e6}


def real_samples():
    out = []
    for path in FIXTURES:
        out += [s for s in path.read_bytes().split(b"\0") if s.strip()]
    return out


class Generator:
    """Per real skeleton (one per fixture): fields that vary between real samples are re-drawn."""

    def __init__(self, seed=7):
        self.rng = random.Random(seed)
        groups = {}
        for sample in real_samples():
            pieces, values, kinds, last = [], [], [], 0
            for m in SLOT.finditer(sample):
                pieces.append(sample[last:m.start(2)])
                kinds.append(m.group(1).decode())
                values.append(m.group(2))
                last = m.end(2)
            pieces.append(sample[last:])
            groups.setdefault(tuple(pieces), []).append((kinds, values))
        self.skeletons = []
        for pieces, rows in groups.items():
            n = len(rows[0][1])
            dynamic = [len({r[1][i] for r in rows}) > 1 for i in range(n)]
            pool = [[r[1][i] for r in rows if r[1][i] != b"0"] for i in range(n)]
            elapsed = {i for i in range(n) if pieces[i].endswith(b"<key>elapsed_ns</key><integer>")}
            self.skeletons.append((list(pieces), rows, dynamic, pool, elapsed))

    def value(self, pool, kind, v):
        rng = self.rng
        if v == b"0" and (rng.random() < 0.9 or not pool):
            return b"0"
        if v == b"0":
            v = rng.choice(pool)
        x = float(v) * rng.lognormvariate(0.0, 0.3)
        return str(int(x)).encode() if kind == "integer" else (b"%g" % x)

    def sample(self, t):
        pieces, rows, dynamic, pool, elapsed = self.rng.choice(self.skeletons)
        kinds, values = self.rng.choice(rows)
        out = [pieces[0]]
        for i, (kind, v) in enumerate(zip(kinds, values)):
            if kind == "date":
                v = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(t))).encode()
            elif i in elapsed:
                v = str(int(100e6 * self.rng.gauss(1.0, 0.05))).encode()
            elif dynamic[i]:
                v = self.value(pool[i], kind, v)
            out += [v, pieces[i + 1]]
        return b"".join(out) + b"\0"

    def plist(self, path: Path, target_bytes: float, t0=1_800_000_000.0):
        size, i = 0, 0
        with open(path, "wb") as out:
            while size < target_bytes:
                chunk = self.sample(t0 + i / 10)
                out.write(chunk)
                size += len(chunk)
                i += 1
        return i

    def jsonl(self, path: Path, target_bytes: float, kind: str):
        rng, size, i = self.rng, 0, 0
        with open(path, "w") as out:
            while size < target_bytes:
                if kind == "telemetry":  # a reduced JSON re-encoding of one plist sample, ~7 kB
                    row = {"t": 1_800_000_000 + i / 10, "gpu_power_mw": round(rng.uniform(5, 40000), 3),
                           "clusters": [{"name": n, "cpus": [{"cpu": c, "freq_hz": rng.uniform(7e8, 4e9),
                                                              "idle_ratio": rng.random(), "down_ratio": 0.0}
                                                             for c in range(k)],
                                         "dvfm_states": [{"freq": f, "used_ns": rng.randrange(0, 10**8),
                                                          "used_ratio": round(rng.random(), 6)} for f in range(m)]}
                                        for n, k, m in (("E", 4, 6), ("P0", 6, 20), ("P1", 6, 20))]}
                elif kind == "turns":
                    row = {"turn": i, "decode_tokens": rng.randrange(50, 900), "text": "".join(
                        rng.choice("abcdefghijklmnopqrstuvwxyz ,.") for _ in range(300))}
                else:
                    row = {"event_type": rng.choice(["stage_started", "stage_completed", "sample"]), "t_ns": 10**18 + i}
                line = json.dumps(row) + "\n"
                out.write(line)
                size += len(line)
                i += 1

    def member(self, root: Path):
        for rel, target in MEMBER.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel.endswith(".plist"):
                self.plist(path, target)
            elif rel.endswith(".csv"):
                with open(path, "w") as out:
                    size = 0
                    while size < target:
                        line = f"{time.time_ns()},{self.rng.uniform(0, 40):.6f},{self.rng.uniform(0, 9):.6f}\n"
                        out.write(line)
                        size += len(line)
            else:
                self.jsonl(path, target, "telemetry" if "telemetry" in rel else
                           "turns" if "turns" in rel else "events")


def zstd_size(data: bytes, level: int) -> int:
    return len(subprocess.run(["zstd", f"-{level}", "-q", "-c"], input=data, capture_output=True, check=True).stdout)


def validate(gen: Generator) -> list[dict]:
    rows = []
    for path in FIXTURES:
        real = path.read_bytes()
        n = len([s for s in real.split(b"\0") if s.strip()])
        synth = b"".join(gen.sample(1_800_000_000 + i / 10) for i in range(n))
        for level in (3, 9):
            rows.append({"fixture": path.relative_to(ROOT).as_posix(), "samples": n, "level": level,
                         "real_bytes_per_sample": len(real) / n, "synthetic_bytes_per_sample": len(synth) / n,
                         "real_ratio": len(real) / zstd_size(real, level),
                         "synthetic_ratio": len(synth) / zstd_size(synth, level)})
    return rows


def timed(argv, *, stdin=None, stdout=subprocess.DEVNULL):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    subprocess.run(argv, stdin=stdin, stdout=stdout, check=True)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return wall, (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)


def bench_cli(tar: Path, work: Path, levels, threads, repeats) -> list[dict]:
    raw = tar.stat().st_size
    rows = []
    for level in levels:
        for t in threads:
            walls, cpus, out = [], [], work / "out.zst"
            for _ in range(repeats):
                out.unlink(missing_ok=True)
                wall, cpu = timed(["zstd", f"-{level}", f"-T{t}", "-q", "-f", str(tar), "-o", str(out)])
                walls.append(wall)
                cpus.append(cpu)
            size = out.stat().st_size
            wall = statistics.median(walls)
            dwall, _ = timed(["zstd", "-d", "-q", "-c", str(out)])
            rows.append({"codec": "zstd-cli", "level": level, "threads": t, "ratio": raw / size,
                         "compress_mb_s": raw / 1e6 / wall, "cpu_s_per_gb": statistics.median(cpus) / (raw / 1e9),
                         "decompress_mb_s": raw / 1e6 / dwall})
            out.unlink()
    return rows


def bench_stdlib(tar: Path) -> list[dict]:
    data, rows = tar.read_bytes(), []
    candidates = []
    try:
        import compression.zstd as z
        candidates += [("zstd-stdlib", 3, lambda d: z.compress(d, level=3))]
    except ImportError:
        pass
    import gzip
    candidates += [("gzip-stdlib", lvl, lambda d, lvl=lvl: gzip.compress(d, compresslevel=lvl, mtime=0)) for lvl in (1, 6)]
    for name, level, fn in candidates:
        start, cpu0 = time.perf_counter(), time.process_time()
        size = len(fn(data))
        wall = time.perf_counter() - start
        rows.append({"codec": name, "level": level, "threads": 1, "ratio": len(data) / size,
                     "compress_mb_s": len(data) / 1e6 / wall,
                     "cpu_s_per_gb": (time.process_time() - cpu0) / (len(data) / 1e9)})
    return rows


def bench_pipeline(member: Path, work: Path) -> dict:
    """The real code path: Offload.pack on the MBP side, Gate.verify (decompress, sha256, extract) on the Air."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import offload_window as ow
    sums = work / "SHA256SUMS"
    lines = []
    for path in sorted(p for p in member.rglob("*") if p.is_file()):
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(member).as_posix()}\n")
    sums.write_text("".join(lines))
    raw = sum(p.stat().st_size for p in member.rglob("*") if p.is_file())
    out = {}
    for threads in (1, 4):
        state, air = work / f"state{threads}", work / f"air{threads}"
        air.mkdir()
        off = ow.Offload(state, "bench")
        cpu0, start = os.times(), time.perf_counter()
        manifest = off.pack(member, sums, hashlib.sha256(sums.read_bytes()).hexdigest(),
                            codec=ow.choose_codec("zstd-cli", 3, threads))
        pack_s = time.perf_counter() - start
        cpu1 = os.times()
        inbox = air / "inbox/bench"
        inbox.mkdir(parents=True)
        for name in [p["name"] for p in manifest["parts"]] + ["offload-manifest.json", "record-manifest.bin"]:
            src = state / "bench" / ("parts/" + name if name.startswith("part-") else name)
            shutil.copyfile(src, inbox / name)
        start = time.perf_counter()
        ow.Gate(air).verify("bench")
        verify_s = time.perf_counter() - start
        out[f"T{threads}"] = {
            "raw_bytes": raw, "compressed_bytes": manifest["compressed_bytes"], "pack_s": pack_s,
            "pack_raw_mb_s": raw / 1e6 / pack_s,
            "pack_cpu_s": (cpu1.user + cpu1.system + cpu1.children_user + cpu1.children_system)
                          - (cpu0.user + cpu0.system + cpu0.children_user + cpu0.children_system),
            "air_verify_s": verify_s, "air_verify_raw_mb_s": raw / 1e6 / verify_s}
        shutil.rmtree(state)
        shutil.rmtree(air)
    return out


def window_model(ratio: float, pack_mb_s: float, verify_mb_s: float) -> list[dict]:
    rows = []
    for name, gb in (("W1", 18.6), ("D", 26.4)):
        for net in (50, 100, 300):
            pack = gb * 1e3 / pack_mb_s
            push = gb * 1e3 / ratio / net
            verify = gb * 1e3 / verify_mb_s
            rows.append({"window": name, "raw_gb": gb, "net_mb_s": net, "pack_s": pack, "push_s": push,
                         "verify_s": verify, "total_s": pack + push + verify + 10})
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True, help="scratch directory (about 1.2 GB free needed)")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--skip-pipeline", action="store_true")
    args = parser.parse_args(argv)
    args.work.mkdir(parents=True, exist_ok=True)
    gen = Generator()
    result = {"host": os.uname().machine, "cpu": subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                                                capture_output=True, text=True).stdout.strip(),
              "zstd": subprocess.run(["zstd", "--version"], capture_output=True, text=True).stdout.strip(),
              "validation": validate(gen)}
    member = args.work / "member"
    if not member.exists():
        gen.member(member)
    tar = args.work / "member.tar"
    with tarfile.open(tar, "w", format=tarfile.PAX_FORMAT) as handle:
        handle.add(member, arcname="member")
    result["member_bytes"] = tar.stat().st_size
    result["cli"] = bench_cli(tar, args.work, (1, 3, 6, 9), (1, 4), args.repeats)
    result["stdlib"] = bench_stdlib(tar)
    tar.unlink()
    if not args.skip_pipeline:
        result["pipeline"] = bench_pipeline(member, args.work)
        p = result["pipeline"]["T4"]
        result["window_model"] = window_model(p["raw_bytes"] / p["compressed_bytes"], p["pack_raw_mb_s"],
                                              p["air_verify_raw_mb_s"])
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
