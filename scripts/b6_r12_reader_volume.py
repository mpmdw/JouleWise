#!/usr/bin/env python3
"""Synthetic production-size desk reader benchmark, NOT an R12 session.

No driver, measurement, model, meter device or host action runs. Only local
synthetic bytes, the original desk compressor and read_bytes are exercised.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import resource
import struct
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from joulewise import desk_compress
from b6_r12_session_fixture import git_blobs
from b6_r12_chain_fixture import PIN
from b6_r12_verify import safe_root, sha

SIZING = "configs/b6/registration/sizing_b5.json"
PM_CONFIG = "configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r01.json"
PLAN = "joulewise/b5/plan.py"
USB = "joulewise/external/km003c_usb.py"
MONITOR = "scripts/km003c_monitor.py"
DESK = "joulewise/desk_compress.py"
SAMPLE = struct.Struct("<HHiiHHHH")


def constants(raw):
    values = {}
    for node in ast.parse(raw).body:
        if isinstance(node, ast.Assign):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    values[target.id] = value
    return values


def specification():
    blobs = git_blobs([SIZING, PM_CONFIG, PLAN, USB, MONITOR, DESK])
    sizes = json.loads(blobs[SIZING])["packs"]
    plan, usb = constants(blobs[PLAN]), constants(blobs[USB])
    defaults = {}
    for node in ast.walk(ast.parse(blobs[MONITOR])):
        if (isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant)
                and node.args[0].value in ("--poll-ms", "--rate")):
            defaults[node.args[0].value] = next(ast.literal_eval(k.value) for k in node.keywords if k.arg == "default")
    span = max(row["programmed_span_s"] for row in sizes.values())
    caps = {name: plan[name] for name in ("T0_STAGE_CAP_S", "PAUSE_LIMIT_S", "SESSION_WAIT_BUDGET_S")}
    window = 60 * math.ceil((math.ceil(span) + sum(caps.values())) / 60)
    poll_ns = round(defaults["--poll-ms"] * 1e6)
    hz = json.loads(blobs[PM_CONFIG])["sampling"]["power_hz"]
    stream_s = max(row["T_stream_max_s"] for row in sizes.values())
    meter_hz = usb["RATES_SPS"][defaults["--rate"]]
    polls = window * 1_000_000_000 // poll_ns + 1  # writer polls at both endpoints
    samples_per_poll = meter_hz * poll_ns // 1_000_000_000
    return {"pin": PIN, "synthetic_only": True, "r12_fixture": False,
        "generator_sha256": sha(Path(__file__)),
        "sources_sha256": {p: hashlib.sha256(raw).hexdigest() for p, raw in blobs.items()},
        "programmed_span_s": span, "caps_s": caps, "window_s": window,
        "meter_hz": meter_hz, "meter_poll_ns": poll_ns, "meter_rate_idx": defaults["--rate"],
        "meter_schema": constants(blobs[MONITOR])["SCHEMA"],
        "meter_polls": polls, "samples_per_poll": samples_per_poll,
        "meter_samples": polls * samples_per_poll,
        "plist_stream_s": stream_s, "plist_hz": hz, "plist_frames": round(stream_s * hz),
        "cpus_per_frame": 16, "plist_cpu_entries": 16 * round(stream_s * hz),
        "prediction": "original desk compresses both full streams; compressed read_bytes restores exact sizes/SHA and cadence counts; no R12/session claim"}


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def prepare(root, *, tiny=False):
    root = safe_root(root)
    if root.exists():
        raise ValueError("fresh reader-volume root required")
    spec = specification()
    if tiny:
        spec.update(window_s=1, meter_polls=6, meter_samples=60,
                    plist_stream_s=1, plist_frames=10, plist_cpu_entries=160, fraction="tiny control only")
    else:
        spec["fraction"] = "1/1 registered maximum"
    root.mkdir()
    dump(root / "declaration.json", spec)  # prediction before any stream byte
    started = time.monotonic()
    inputs, custody = root / "reader-inputs", root / "control"
    sources = inputs / "sources"
    sources.mkdir(parents=True)
    (custody / "night").mkdir(parents=True)
    # Minimal compressor readiness control, explicitly not a session archive.
    dump(inputs / "harvest.json", {"verdict": "COLLECTED", "scope": "reader volume control only; NOT a session"})
    (custody / "night/chain.exited").touch()
    meter = sources / "meter.jsonl"
    origin, wall = 1_000_000_000_000, 1_800_000_000_000_000_000
    smc = {"PDTR": 10.0, "PSTR": 10.0, "PPBR": 0.0, "B0AC": 0, "B0AV": 12000}
    header = {"k": "h", "schema": spec["meter_schema"], "status": "streaming",
        "reason": None, "model": "POWER-Z KM003C", "vid": "5fc9", "pid": "0063",
        "rate_idx": spec["meter_rate_idx"], "sps": spec["meter_hz"], "poll_s": spec["meter_poll_ns"] / 1e9,
        "qos": "default", "init_errors": [], "process_id": 0, "smc_keys": list(smc),
        "smc_units": {"PDTR": "W", "PSTR": "W", "PPBR": "W", "B0AC": "mA", "B0AV": "mV"},
        "raw_start_ns": origin, "mono_start_ns": origin, "rt_start_ns": wall}
    with meter.open("wb") as stream:
        def row(value):
            stream.write(json.dumps(value, separators=(",", ":")).encode() + b"\n")
        row(header)
        for index in range(spec["meter_polls"]):
            n = spec["samples_per_poll"]
            payload = b"".join(SAMPLE.pack(((index * n + j - n + 1) * 20) % 65536,
                0, 28_000_000, 357143, 0, 0, 0, 0) for j in range(n))
            offset = index * spec["meter_poll_ns"]
            row({"k": "b", "tx": origin + offset, "rx": origin + offset + 1_000_000,
                 "rt": wall + offset + 1_000_000, "n": n, "p": payload.hex(), "smc": smc})
        row({"k": "t", "polls": spec["meter_polls"], "empties": 0, "bad": 0,
             "usb_errors": 0, "elapsed_s": spec["window_s"], "reason": "duration",
             "raw_end_ns": origin + spec["window_s"] * 1_000_000_000})
    plist = sources / "powermetrics.plist"
    with plist.open("wb") as stream:
        for index in range(spec["plist_frames"]):
            if index:
                stream.write(b"\0")
            document = {"timestamp": dt.datetime.fromtimestamp(wall / 1e9 + (index + 1) / spec["plist_hz"], dt.UTC),
                "is_delta": True, "elapsed_ns": round(1e9 / spec["plist_hz"]),
                "thermal_pressure": "Nominal", "hw_model": "Mac15,9", "kern_osversion": "25G83",
                "processor": {"cpu_power": 500.0, "gpu_power": 6000.0, "ane_power": 0.0,
                    "combined_power": 6500.0, "cpu_energy": 50.0, "gpu_energy": 600.0, "ane_energy": 0.0,
                    "clusters": [{"name": "E-Cluster", "idle_ratio": .99, "down_ratio": 0.0, "online_ratio": 1.0,
                        "cpus": [{"cpu": i, "idle_ratio": .99, "down_ratio": 0.0, "freq_hz": 1020000000.0}
                                 for i in range(spec["cpus_per_frame"])]}]},
                "gpu": {"idle_ratio": 0.0, "freq_hz": 1500.0}}
            stream.write(plistlib.dumps(document))
    prepared = {"files": {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p in (meter, plist)},
                "generation_wall_s": time.monotonic() - started, "complete": True}
    dump(root / "prepared.json", prepared)
    return prepared


def exercise(root):
    root = safe_root(root)
    spec, prepared = (json.loads((root / n).read_bytes()) for n in ("declaration.json", "prepared.json"))
    if sha(REPO / DESK) != spec["sources_sha256"][DESK]:
        raise ValueError("the desk implementation must equal the pinned original")
    if not prepared["complete"]:
        raise ValueError("incomplete volume inputs")
    inputs = root / "reader-inputs"
    for name, expected in prepared["files"].items():
        path = inputs / "sources" / name
        if sha(path) != expected["sha256"] or path.stat().st_size != expected["bytes"]:
            raise ValueError("volume input changed")
    started = time.monotonic()
    code, summary = desk_compress.compress(archive=inputs, custody=root / "control",
        min_bytes=1 if spec["fraction"] == "tiny control only" else 1048576)
    if code != 0 or summary["files"] != 2 or summary["mismatches"]:
        raise ValueError("original desk did not compress both inputs: " + str(summary))
    observed = {"compression": summary, "files": {}, "r12_fixture": False, "fraction": spec["fraction"]}
    for name, expected in prepared["files"].items():
        path = inputs / "sources" / name
        if path.exists() or not Path(str(path) + ".zst").is_file():
            raise ValueError("compressed sibling path must actually be used")
        before = time.monotonic()
        data = desk_compress.read_bytes(path)
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != expected["bytes"] or digest != expected["sha256"]:
            raise ValueError("production reader bytes differ")
        if name == "meter.jsonl":
            polls = data.count(b'"k":"b"')
            if polls != spec["meter_polls"] or data.count(b"\n") != polls + 2:
                raise ValueError("meter row census differs")
            census = {"polls": polls, "wire_samples": polls * spec["samples_per_poll"]}
        else:
            frames, cpus = data.count(b"</plist>"), data.count(b"<key>cpu</key>")
            if frames != spec["plist_frames"] or cpus != spec["plist_cpu_entries"]:
                raise ValueError("plist frame/CPU census differs")
            census = {"frames": frames, "cpu_entries": cpus}
        observed["files"][name] = {"bytes": len(data), "sha256": digest, **census,
            "compressed_bytes": Path(str(path) + ".zst").stat().st_size,
            "read_and_check_wall_s": time.monotonic() - before}
        del data
    observed.update(compression_and_read_wall_s=time.monotonic() - started,
        self_peak_rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        child_peak_rss=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        rss_units="bytes" if sys.platform == "darwin" else "KiB",
        rss_method="getrusage per-process peaks; not a concurrent process-tree peak",
        complete=True)
    dump(root / "reader-volume-observations.json", observed)
    return observed


def execute_tests(root):
    started = time.monotonic()
    result = subprocess.run([sys.executable, "-B", "-m", "unittest",
        "tests.test_b6_r12_reader_volume.ProductionReaderTests"], cwd=REPO, check=False,
        env={**os.environ, "R12_READER_VOLUME_ROOT": str(root)})
    receipt = {"actual_test_exit": result.returncode, "wall_s": time.monotonic() - started,
        "peak_rss": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "rss_units": "bytes" if sys.platform == "darwin" else "KiB",
        "rss_method": "getrusage(RUSAGE_CHILDREN), largest individual process peak; fallback, not time -l"}
    dump(root / "test-process.json", receipt)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("prepare", "measure", "execute-tests"))
    args = parser.parse_args()
    root = safe_root(args.root)
    if args.mode == "prepare":
        print(json.dumps(prepare(root), sort_keys=True))
        return 0
    if args.mode == "execute-tests":
        return execute_tests(root)
    with (root / "reader-test.stdout").open("xb") as out, (root / "reader-test.time").open("xb") as err:
        result = subprocess.run(["/usr/bin/time", "-l", sys.executable, "-B", str(Path(__file__)),
            "--root", str(root), "--mode", "execute-tests"], cwd=REPO, stdout=out, stderr=err, check=False)
    receipt = json.loads((root / "test-process.json").read_bytes())
    receipt.update(time_wrapper_exit=result.returncode, generator_sha256=sha(Path(__file__)),
                   observation_sha256=sha(root / "reader-volume-observations.json"))
    dump(root / "reader-volume-receipt.json", receipt)
    print(json.dumps(receipt, sort_keys=True))
    return receipt["actual_test_exit"]


if __name__ == "__main__":
    raise SystemExit(main())
