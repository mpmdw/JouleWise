"""CI runner for one shard of the frozen admission-closure matrix (not a test module; ``unittest`` does not discover it).

    python tests/cadence/ci_interim_admission.py INDEX TOTAL

Runs ``test_interim_admission_closure.py --report INDEX/TOTAL --separate-audit`` (shard 0 also runs the five audit-3
reproductions with ``--report audit``), reads its per-case JSON lines and fails on any case with a problem, except the
cases ``interim_admission_open.json`` holds open by id. A held-open case that passes also fails the shard, so the list
cannot go stale. Every case of the shard must appear exactly once.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
MODULE = HERE / "test_interim_admission_closure.py"
OPEN = set(json.loads((HERE / "interim_admission_open.json").read_text())["open"])


def run(argument, *flags):
    process = subprocess.run([sys.executable, "-B", str(MODULE), "--report", argument, *flags],
                             capture_output=True, text=True)
    rows = [json.loads(line) for line in process.stdout.splitlines() if line.startswith("{")]
    if process.returncode:
        print(process.stderr[-4000:])
        raise SystemExit(f"the suite's report mode exited {process.returncode}")
    return rows


def main(index, total):
    rows = run(f"{index}/{total}", "--separate-audit")
    if index == 0:
        rows += run("audit")
    names = [row["case"] for row in rows]
    if len(set(names)) != len(names):
        raise SystemExit("a case ran twice")
    failed = {row["case"]: row["problems"] for row in rows if row["problems"]}
    unexpected = {case: why for case, why in failed.items() if case not in OPEN}
    stale = sorted(case for case in OPEN if case in set(names) and case not in failed)
    print(f"SHARD {index}/{total}: {len(rows)} cases, {len(failed)} failing, {len(failed) - len(unexpected)} held open")
    for case, why in sorted(unexpected.items())[:40]:
        print(f"FAIL {case}: {why}")
    for case in stale:
        print(f"STALE open case now passes: {case}")
    return 1 if unexpected or stale else 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]), int(sys.argv[2])))
