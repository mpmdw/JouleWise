#!/usr/bin/env python3
"""Offline re-grade a finished Qwen4 gold work directory under the current gate.

No worker, framework runtime, network access, or report verdict is trusted.  Each
case's fingerprint-bound request/result/array inventory is authenticated and all
trace metrics and unit verdicts are recomputed.  The original run is immutable;
results are written to ``regate.json`` (or ``--output``).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.align.qwen4_gold.core import IndexedCheckpoint, digest, write_json  # noqa: E402
from joulewise.align.qwen4_gold.runner import Harness, artifacts, reusable  # noqa: E402


def regate_work(work, checkpoint):
    work = Path(work).resolve()
    harness = object.__new__(Harness)
    harness.checkpoint = checkpoint
    units = {}
    for unit_dir in sorted(p for p in work.iterdir() if p.is_dir() and (p.name.startswith("layer-") or p.name in {"embed", "final", "head"})):
        unit = unit_dir.name[6:].lstrip("0") or "0" if unit_dir.name.startswith("layer-") else unit_dir.name
        cases = []
        for case in sorted(p for p in unit_dir.iterdir() if p.is_dir() and ".attempt-" not in p.name):
            path = case / "report.json"
            if not path.is_file():
                continue
            old = json.loads(path.read_text())
            fp = old.get("fingerprint")
            if not fp or not reusable(path, fp):
                cases.append({"case": case.name, "status": "EVIDENCE_ERROR",
                              "reason": "fingerprint-bound artifact inventory failed"})
                continue
            dtype = "bf16" if "-bf16-" in case.name else "fp32"
            mode = old.get("input_mode", case.name.rsplit("-", 1)[-1])
            fresh = harness.grade_saved(unit, dtype, case, fp, mode, old.get("random_scale"))
            fresh["artifacts"] = artifacts(case)
            fresh["evidence_digest"] = digest({"fingerprint": fp, "artifacts": fresh["artifacts"]})
            cases.append(fresh)
        status = "PASS" if cases and all(c["status"] == "PASS" for c in cases) else "INCOMPLETE_OR_FAILED"
        units[unit] = {"unit": unit, "status": status, "cases": cases}
    return {"schema": "qwen4-gold/regate-v1", "work_dir": str(work), "units": units,
            "status": "PASS" if units and all(u["status"] == "PASS" for u in units.values()) else "INCOMPLETE_OR_FAILED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--checkpoint", required=True, help="local checkpoint/view containing compared norm weights")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    result = regate_work(args.work_dir, IndexedCheckpoint(Path(args.checkpoint).resolve()))
    output = Path(args.output) if args.output else Path(args.work_dir) / "regate.json"
    write_json(output, result)
    for unit, row in result["units"].items():
        print(f"{unit}: {row['status']} ({len(row['cases'])} cases)")
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
