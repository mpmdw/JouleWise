"""DRAFT x86 pilot session driver; reuses the shared SHADE episode loop.

No imports load MLX, NVML, models, a meter or /proc. All devices are opened
only by run_session. One immutable directory per attempt retains a rejected
original and its single redo. This never runs a registered Apple window.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import time

from joulewise.align.records import to_json
from joulewise.align.runner import run_episode


def wall_meter_flags(episode):
    traces = [t for t in episode.power_traces if t.source == "wall_meter"]
    flags = []
    if not traces or not any(len(t.t_ns) >= 2 for t in traces):
        flags.append("wall_meter.missing_stream")
    if any(t.t_ns and (t.t_ns[0] > episode.start_ns or t.t_ns[-1] < episode.end_ns) for t in traces):
        flags.append("wall_meter.partial_coverage")
    for trace in traces:
        try:
            notes = json.loads(trace.notes or "{}")
        except ValueError:
            notes = {"flags": ["invalid_meter_notes"]}
        if not isinstance(notes, dict):
            notes = {"flags": ["invalid_meter_notes"]}
        if notes.get("flags"):
            flags.append("wall_meter.stream_errors")
        if "SYNTHETIC" in notes.get("identity", ""):
            flags.append("wall_meter.synthetic_replay")
    return tuple(dict.fromkeys(flags))


def run_member(task, condition, endpoint, samplers, guard, *, attempt=0, **kwargs):
    """The caller supplies a fresh task/endpoint/guard for every attempt."""
    guard.start()  # missing CPU observation refuses before the model request
    try:
        episode, transcript = run_episode(task, condition, endpoint, samplers=samplers, **kwargs)
    finally:
        quiet = guard.stop(attempt)
    flags = [*episode.flags, *wall_meter_flags(episode), "x86.draft_provisional"]
    if quiet["decision"] != "keep":
        flags.append("quiet." + quiet["decision"])
    elif any(row["flagged"] for row in quiet.get("intervals", ())):
        flags.append("quiet.contention_recorded")
    if any(row.get(key) for row in quiet.get("intervals", ()) for key in
           ("unaccounted_started", "unaccounted_exited", "disappeared_during_snapshot")):
        flags.append("quiet.unaccounted_process_churn")
    hardware = dict(episode.hardware)
    hardware["linux_quiet"] = quiet
    return replace(episode, flags=tuple(dict.fromkeys(flags)), hardware=hardware), transcript, quiet


def write_attempt(directory, episode, transcript, config, quiet):
    """Exclusive files; no overwrite/resume may erase a measured attempt."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    artifacts = {
        "episode.json": to_json(episode) + "\n",
        "transcript.jsonl": "".join(to_json(m) + "\n" for m in transcript),
        "turns.jsonl": "".join(to_json(t) + "\n" for t in episode.turns),
        "quiet.json": to_json(quiet) + "\n",
        "config.json": to_json(config) + "\n",
    }
    for name, data in artifacts.items():
        with (directory / name).open("x", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    manifest = {name: hashlib.sha256(data.encode()).hexdigest() for name, data in artifacts.items()}
    with (directory / "manifest.json").open("x", encoding="utf-8") as handle:
        handle.write(to_json({"status": "DRAFT_PROVISIONAL", "sha256": manifest,
                              "flags": episode.flags, "decision": quiet["decision"]}) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def validate_config(config):
    if config.get("status") != "DRAFT":
        raise ValueError("this driver supports DRAFT engineering pilots only")
    if config.get("conditions") != ["benign", "sabotage"]:
        raise ValueError("pilot requires paired benign/sabotage conditions")
    pairs = config.get("task_pairs", [])
    if len(pairs) != 2 or len(set(pairs)) != 2 or any(not p.startswith("shade/") for p in pairs):
        raise ValueError("pilot requires two distinct SHADE task pairs")
    if not config.get("seeds") or any(type(s) is not int or s < 0 for s in config["seeds"]):
        raise ValueError("seeds must be nonnegative integer SHADE seed indices")
    for key in ("max_turns", "max_tokens"):
        if type(config.get(key)) is not int or config[key] <= 0:
            raise ValueError(key + " must be a positive integer")
    value = config.get("temperature")
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("temperature must be finite and nonnegative")
    if not config.get("endpoint", {}).get("seed_model_id"):
        raise ValueError("explicit ALIGN seed_model_id required")
    if type(config.get("server_pid")) is not int or config["server_pid"] <= 1:
        raise ValueError("set server_pid to the running llama-server PID on the rig")
    provenance = config.get("provenance", {})
    for key, length in (("gguf_sha256", 64), ("llama_cpp_commit", 40)):
        value = provenance.get(key)
        if not isinstance(value, str) or len(value) != length or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("record actual lowercase hex " + key)
    poll = config.get("poll_interval_s", 1.0)
    if type(poll) not in (int, float) or not math.isfinite(poll) or poll <= 0:
        raise ValueError("poll_interval_s must be positive and finite")
    return config


def run_session(config, output):
    from joulewise.align.linux.backend import LlamaCppBackend
    from joulewise.align.linux.quiet import LinuxQuietGuard
    from joulewise.align.linux.samplers import (
        CsvReplayWallMeter, HttpJsonWallMeter, RaplSampler, WallMeterSampler,
    )
    from joulewise.align.power.nvml import NvmlSampler

    validate_config(config)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    domain = socket.gethostname() + ":monotonic"
    backend = LlamaCppBackend(config["endpoint"], config["shade_cache"])
    # Offline source verification/imports are outside every measurement.
    probe = backend.task(config["task_pairs"][0])
    if probe.upstream.prepare() is None:
        raise ValueError("pinned offline SHADE cache unavailable: " + repr(probe.upstream.flags))
    for pair in config["task_pairs"]:
        for seed in config["seeds"]:
            for condition in config["conditions"]:
                for attempt in (0, 1):
                    task = backend.task(pair)
                    task.reset(seed)
                    if task._definition is None:
                        raise ValueError("SHADE task unavailable: " + repr(task.flags))
                    meter = config.get("wall_meter")
                    adapter = None
                    if meter is not None:
                        settings = dict(meter)
                        kind = settings.pop("kind")
                        adapter = (HttpJsonWallMeter(**settings) if kind == "http_json" else
                                   CsvReplayWallMeter(**settings) if kind == "csv_replay" else None)
                        if adapter is None:
                            raise ValueError("unknown wall meter adapter: " + str(kind))
                    poll = {"interval_s": config.get("poll_interval_s", 1.0), "clock_domain": domain}
                    samplers = [NvmlSampler(config.get("gpu_indices", [0]), clock_domain=domain,
                                            interval_ns=round(poll["interval_s"] * 1e9)),
                                RaplSampler(config.get("rapl_root", "/sys/class/powercap"), **poll),
                                WallMeterSampler(adapter, **poll)]
                    guard = LinuxQuietGuard(tree_roots=(os.getpid(), config["server_pid"]))
                    # Give short episodes a full 30 s observed CPU window.
                    # This dwell is outside episode energy, but is raw quiet evidence.
                    guard.check()
                    if guard.errors:
                        raise RuntimeError(guard.errors[-1])
                    time.sleep(30)
                    episode, transcript, quiet = run_member(task, condition, backend.new_session(pair),
                        samplers, guard, attempt=attempt, seed=seed,
                        max_turns=config["max_turns"], max_tokens=config["max_tokens"],
                        temperature=config["temperature"], clock_domain=domain,
                        matrix_id=config["matrix_id"])
                    directory = output / f"{pair.split('/')[-1]}-s{seed}-{condition}-attempt{attempt}"
                    write_attempt(directory, episode, transcript, config, quiet)
                    if quiet["decision"] == "indeterminate":
                        raise RuntimeError("quiet CPU observation indeterminate; evidence retained")
                    if quiet["decision"] != "redo":
                        break
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    config = validate_config(json.loads(args.config.read_text()))
    if args.validate_only:
        print("DRAFT configuration valid; no devices opened")
    else:
        run_session(config, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
