#!/usr/bin/env python3
"""R0 SMC inventory and optional fixed GPU step; run only after all agents exit."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.hazards import smc, smc_enumeration as r0, temperature
from joulewise.hazards.base import Context
from joulewise.hazards.base import write_create_once
from joulewise.hazards.monitor import Journal


def markdown(report, digest):
    result = report["response"]
    lines = ["# ALIGN R0 SMC desk report", "", "Status: **PROVISIONAL**. Sensor locations are unverified.",
             "", result["rule"], "", f"S_fast: `{result['s_fast']}`; S_slow: `{result['s_slow']}`.",
             "", "| Key | Unit | Amplitude | Idle noise | Tau (s) | A/noise | R2 | Result |",
             "|---|---|---:|---:|---:|---:|---:|---|"]
    def number(v):
        return "—" if v is None else f"{v:.5g}"
    for row in result["ranking"]:
        cells = [row["key"], row["unit"], *(number(row[k]) for k in (
            "amplitude", "noise", "tau_s", "amplitude_to_noise", "fit_r2")), row["reason"]]
        lines.append("| " + " | ".join(cells) + " |")
    lines += ["", f"R0 JSON SHA-256: `{digest}`.",
              f"Complete-sensor sample fraction: {report['coverage']['all_keys']['sample_fraction']}",
              "", "Review all per-key coverage and gaps in the JSON. Fans are never temperature candidates."]
    if result["s_fast"] and result["s_slow"]:
        policy = {"smc_temperature": {"s_fast": result["s_fast"], "s_slow": result["s_slow"],
                   "fan_keys": [s["key"] for s in report["inventory"]["keys"] if s["unit"] == "rpm"],
                   "r0_sha256": digest}}
        lines += ["", "Candidate campaign-policy extension (review on Mac15,9 before pinning):", "", "```json",
                  json.dumps(policy, indent=2), "```"]
    else:
        lines += ["", "No complete policy proposal: a required time-constant class was not resolved."]
    return "\n".join(lines) + "\n"


def host_metadata():
    result = {"platform": platform.platform(), "machine": platform.machine()}
    for field in ("hw.model", "hw.memsize"):
        probe = subprocess.run(["/usr/sbin/sysctl", "-n", field], capture_output=True,
                               text=True, timeout=5, check=False)
        result[field] = probe.stdout.strip() if probe.returncode == 0 else None
    return result


def main(argv=None, *, reader_factory=smc.Reader, quiet_check=r0.require_quiet,
         ctx_factory=Context, load_factory=r0.GpuLoad, metadata=host_metadata):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new, nonexisting desk-custody directory")
    parser.add_argument("--seconds", type=int, default=60, help="inventory-only idle sample duration")
    parser.add_argument("--gpu-step", action="store_true", help="opt in to fixed 2048x2048 MLX matmul; no model")
    parser.add_argument("--idle-seconds", type=int, default=300)
    parser.add_argument("--load-seconds", type=int, default=600)
    parser.add_argument("--recovery-seconds", type=int, default=600)
    args = parser.parse_args(argv)
    if min(args.seconds, args.idle_seconds, args.load_seconds, args.recovery_seconds) <= 0:
        parser.error("durations must be positive")
    reader, journal = None, None
    old_handlers = {}
    def interrupted(signum, _frame):
        raise InterruptedError(f"capture interrupted by signal {signum}")
    try:
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            old_handlers[sig] = signal.signal(sig, interrupted)
        admission = quiet_check()  # before directory creation, metadata or backend construction
        args.output.mkdir(parents=True, exist_ok=False)
        journal = Journal(args.output / "samples.jsonl", fsync_interval_s=5)
        reader = reader_factory()
        capture = r0.collect(reader, seconds=args.seconds, idle_s=args.idle_seconds,
                             load_s=args.load_seconds, recovery_s=args.recovery_seconds,
                             gpu_step=args.gpu_step, quiet_check=quiet_check, ctx=ctx_factory(),
                             sink=journal.write, load_factory=load_factory)
        selected = [s["key"] for s in capture["inventory"]["keys"]]
        report = {"schema": "joulewise.align_smc_r0.v1", "status": "PROVISIONAL",
                  "hardware": metadata(), "admission": admission, "gpu_step": args.gpu_step,
                  "gpu_load": {"backend": "mlx", "shape": [2048, 2048], "dtype": "float32"}
                              if args.gpu_step else None,
                  **{k: v for k, v in capture.items() if k != "samples"},
                  "samples_journal": "samples.jsonl",
                  "samples_sha256": hashlib.sha256((args.output / "samples.jsonl").read_bytes()).hexdigest(),
                  "coverage": temperature.coverage(capture["samples"], capture["started"]["monotonic_ns"],
                                                   capture["finished"]["monotonic_ns"], selected),
                  "response": r0.rank(capture)}
        raw = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
        write_create_once(args.output / "r0.json", raw)
        write_create_once(args.output / "summary.md", markdown(report, hashlib.sha256(raw).hexdigest()).encode())
        print(f"PROVISIONAL R0 report: {args.output / 'summary.md'}")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        # Preserve partial samples for a failed capture; never produce a success
        # report or silently retry. Backend and worker cleanup live in finally.
        print(f"R0 refused/failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        if journal is not None:
            stamp = ctx_factory().stamp().to_json()
            journal.write({"schema": "joulewise.hazard_journal.v1", "module": "temperature",
                           "kind": "event", "started": stamp, "finished": stamp,
                           "session": "r0-failure", "seq": 1, "raw": [],
                           "values": {"event": "capture_failed"}, "error": f"{type(exc).__name__}: {exc}"})
        return 3
    finally:
        if reader is not None:
            reader.close()
        if journal is not None:
            journal.close()
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)


if __name__ == "__main__":
    raise SystemExit(main())
