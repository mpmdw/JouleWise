"""Compare R0's local D inventory with the Hugging Face pins (WP11).

Usage: align_v4_verify_d_pins.py REPORT_JSON [--pins configs/align/v4/qwen38-27b-8bit-hf-pins.json]

Every pinned file must be present with the pinned size. Files with an LFS sha256
pin must match it exactly. Extra local files fail. Exit 0 on PASS, 1 on FAIL.
"""
import argparse
import json
import sys
from pathlib import Path

DEFAULT_PINS = Path(__file__).resolve().parent.parent / "configs/align/v4/qwen38-27b-8bit-hf-pins.json"


def verify(report, pins):
    rows = [r for r in report.get("checks", []) if r.get("check") == "disk"]
    if len(rows) != 1:
        return ["report has no single disk check"]
    model = rows[0].get("models", {}).get("D")
    if not model:
        return ["disk check has no D inventory"]
    if model.get("revision") != pins["revision"]:
        return [f"revision {model.get('revision')} != pinned {pins['revision']}"]
    local = {f["path"]: f for f in model["files"]}
    problems = []
    for path, pin in sorted(pins["files"].items()):
        got = local.pop(path, None)
        if got is None:
            problems.append(f"missing {path}")
        elif got["bytes"] != pin["size"]:
            problems.append(f"size {path}: {got['bytes']} != {pin['size']}")
        elif pin.get("sha256") and got["sha256"] != pin["sha256"]:
            problems.append(f"sha256 {path}: {got['sha256']} != {pin['sha256']}")
    problems += [f"unpinned local file {p}" for p in sorted(local)]
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("report", type=Path)
    ap.add_argument("--pins", type=Path, default=DEFAULT_PINS)
    args = ap.parse_args(argv)
    pins = json.loads(args.pins.read_text())
    problems = verify(json.loads(args.report.read_text()), pins)
    lfs = sum(1 for p in pins["files"].values() if p.get("sha256"))
    if problems:
        print("FAIL", *problems, sep="\n  ")
        return 1
    print(f"PASS D @ {pins['revision']}: {len(pins['files'])} files, {lfs} LFS sha256 matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
