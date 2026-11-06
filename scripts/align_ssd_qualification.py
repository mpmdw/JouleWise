#!/usr/bin/env python3
"""Always-attached SSD hardware qualification (DRAFT; non-claim; by day, nothing armed).

  plan       write the segment schedule (default blocks attached,detached,attached,detached,attached,
             6 idle and 6 decode pairs per block: 125 segments, about 6.8 h)
  run        execute a schedule: idle and fixed-work decode segments, write pattern,
             teardown bursts, 1 Hz SMC, metadata-daemon CPU; journal on internal disk
  extract    mean rail power per segment from one continuous powermetrics capture
  evaluate   Q1-Q3, Q5 (there is no Q4) and the strongest option (A / A-lite / B / C) the data allow
  write-pattern
             replay the window write pattern alone into a directory (e.g. during R1)

The powermetrics capture is started by the operator BEFORE `run` and stopped
after it, as ONE continuous capture (a constant anchor offset then cancels):

  sudo powermetrics -b 0 -i 100 --samplers cpu_power,gpu_power,ane_power,thermal \\
       --format plist -o <internal path>/qual.plist

See docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md section 6.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple import external_volume as ev  # noqa: E402
from joulewise.align.apple import ssd_qualification as q  # noqa: E402

PRESENCE_TIMEOUT_S = 1800


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def decode_runner(argv: list[str]):
    """The fixed-work decode command must print one JSON line with
    work_start_epoch_s and work_end_epoch_s stamped around the decode only."""

    def decode():
        result = subprocess.run(argv, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"decode command exit {result.returncode}: {result.stderr[-500:]}")
        for line in reversed(result.stdout.splitlines()):
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if isinstance(value, dict) and {"work_start_epoch_s", "work_end_epoch_s"} <= set(value):
                return value
        raise RuntimeError("decode command printed no work_start_epoch_s/work_end_epoch_s line")
    return decode


def presence_waiter(mount_point: str):
    def wait(kind: str) -> None:
        want = kind == "attached"
        if os.path.ismount(mount_point) == want:
            return
        action = "ATTACH the SSD (cable to the same port)" if want else "EJECT in Finder, then UNPLUG the SSD"
        print(f"[{time.strftime('%H:%M:%S')}] operator: {action}; waiting for {mount_point} "
              f"to be {'mounted' if want else 'absent'}", flush=True)
        deadline = time.monotonic() + PRESENCE_TIMEOUT_S
        while os.path.ismount(mount_point) != want:
            if time.monotonic() > deadline:
                raise RuntimeError(f"presence change to {kind} not seen within {PRESENCE_TIMEOUT_S} s")
            time.sleep(2)
    return wait


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--blocks", default=",".join(q.DEFAULT_BLOCKS))
    p.add_argument("--idle-pairs", type=int, default=q.DEFAULT_IDLE_PAIRS)
    p.add_argument("--decode-pairs", type=int, default=6)
    p.add_argument("--segment-s", type=float, default=120.0)
    p.add_argument("--gap-s", type=float, default=60.0)
    p.add_argument("--settle-s", type=float, default=600.0)
    r = sub.add_parser("run")
    r.add_argument("--plan", type=Path, required=True)
    r.add_argument("--journal", type=Path, required=True, help="internal-disk JSONL")
    r.add_argument("--volume-config", type=Path, required=True, help="external_log_volume config, status qualification")
    r.add_argument("--internal-dir", type=Path, required=True, help="internal write-control target")
    r.add_argument("--burst-bytes", type=int, default=q.TEARDOWN_BYTES)
    r.add_argument("--burst-copies", type=int, default=2)
    r.add_argument("--smc-extra-key", action="append", default=[], help="e.g. the S_slow/S_fast keys from R1 slots")
    r.add_argument("--decode-argv", nargs=argparse.REMAINDER, required=True)
    e = sub.add_parser("extract")
    e.add_argument("--plist", type=Path, required=True)
    e.add_argument("--journal", type=Path, required=True)
    e.add_argument("--out", type=Path, required=True)
    e.add_argument("--guard-s", type=float, default=5.0)
    v = sub.add_parser("evaluate")
    v.add_argument("--rows", type=Path, required=True)
    v.add_argument("--journal", type=Path, required=True)
    v.add_argument("--out", type=Path, required=True)
    v.add_argument("--s-slow-key")
    v.add_argument("--s-r-min-j", type=float, default=q.DEFAULT_S_R_MIN_J)
    v.add_argument("--t-episode-s", type=float, default=q.DEFAULT_T_EPISODE_S)
    w = sub.add_parser("write-pattern")
    w.add_argument("--target", type=Path, required=True)
    w.add_argument("--seconds", type=float, required=True)
    w.add_argument("--worst-case", action="store_true", help="add the 10 Hz powermetrics-sized stream")
    args = parser.parse_args(argv)

    if args.command == "plan":
        schedule = q.plan(blocks=args.blocks.split(","), idle_pairs=args.idle_pairs,
                          decode_pairs=args.decode_pairs, segment_s=args.segment_s, gap_s=args.gap_s,
                          settle_s=args.settle_s)
        _write(args.out, schedule)
        print(f"{len(schedule['segments'])} segments; planned {schedule['planned_total_s'] / 3600:.2f} h "
              "(decode segments run as long as the fixed work)")
        return 0
    if args.command == "write-pattern":
        pattern = {**q.WINDOW_PATTERN, **(q.WORST_CASE_EXTRA if args.worst_case else {})}
        print(json.dumps(q.PatternWriter(args.target, pattern=pattern).run(args.seconds), sort_keys=True))
        return 0
    if args.command == "extract":
        rows = q.extract(args.plist.read_bytes(), _read_jsonl(args.journal), guard_s=args.guard_s)
        _write(args.out, rows)
        print(f"{len(rows)} segment rows")
        return 0
    if args.command == "evaluate":
        rows = json.loads(args.rows.read_text(encoding="utf-8"))
        ops = q.summarize_ops(_read_jsonl(args.journal), s_slow_key=args.s_slow_key)
        verdict = q.evaluate(rows, ops=ops, s_r_min_j=args.s_r_min_j, t_episode_s=args.t_episode_s)
        verdict["ops_inputs"] = ops
        _write(args.out, verdict)
        print(json.dumps({"criteria": verdict["criteria"],
                          "strongest_option_allowed": verdict["strongest_option_allowed"]}, sort_keys=True))
        return 0

    # run
    config = ev.load_config(args.volume_config)
    if config["status"] != "qualification":
        print("refused: run needs the volume config in status 'qualification'", file=sys.stderr)
        return 2
    external_dir = Path(config["mount_point"]) / config["subdir"] / "qualification"
    schedule = json.loads(args.plan.read_text(encoding="utf-8"))
    smc_read = None
    try:
        from joulewise.hazards import smc
        reader = smc.Reader()
        keys = tuple(smc.KEYS) + tuple(args.smc_extra_key)
        smc_read = lambda: reader.read(keys)  # noqa: E731
    except Exception as exc:  # recorded; Q5 then fails on missing battery evidence
        print(f"SMC reader unavailable: {exc}", file=sys.stderr)

    def arm(stage: str) -> None:
        verdict = ev.arm_check(config, ev.census())
        line = {"kind": "arm_check", "stage": stage, "verdict": verdict["verdict"],
                "reasons": verdict["reasons"], "epoch_s": time.time()}
        args.journal.parent.mkdir(parents=True, exist_ok=True)
        with args.journal.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(line, sort_keys=True) + "\n")
        print(json.dumps(line, sort_keys=True), flush=True)

    wait = presence_waiter(config["mount_point"])
    wait(schedule["segments"][0]["presence"])
    arm("start")
    q.run_session(schedule, journal_path=args.journal, external_dir=external_dir, internal_dir=args.internal_dir,
                  decode=decode_runner(args.decode_argv), wait_presence=wait, smc_read=smc_read,
                  burst_bytes=args.burst_bytes, burst_copies=args.burst_copies,
                  ps_text=lambda: subprocess.run(list(q.PS_ARGV), text=True, capture_output=True,
                                                 check=False).stdout,
                  is_attached=lambda: os.path.ismount(config["mount_point"]))
    arm("end")
    print("done; remove the qualification files on the SSD and the internal control dir when the record is saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
