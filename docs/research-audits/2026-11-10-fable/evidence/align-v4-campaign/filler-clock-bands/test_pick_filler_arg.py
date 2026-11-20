#!/usr/bin/env python3.13
"""Check the picker against the pinned plan at and around each observed boundary."""

from datetime import datetime
from itertools import product
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
DEFAULT = "02:00-02:35"
ALTERNATE = "13:14-13:15"


def epoch(stamp):
    return int(datetime.fromisoformat(stamp).timestamp())


def test_rows(bands):
    grouped = {}
    for case in bands["cases"]:
        size = len(case["legs"])
        if size > 2:  # Item 406 has its own three-leg regression.
            continue
        group = grouped.setdefault((case["pin"], size), {})
        for day in case["days"]:
            for band in day["bands"]:
                interval = (epoch(band["from"]), epoch(band["through"]), band["admitted"])
                group.setdefault(case["batch_window"], set()).add(interval)

    rows = []
    for (pin, size), windows in sorted(grouped.items()):
        intervals = set().union(*windows.values())
        start = min(first for first, _, _ in intervals)
        stop = max(last for _, last, _ in intervals)
        probes = {edge + delta for first, last, _ in intervals
                  for edge in (first, last) for delta in (-1, 0, 1)
                  if start <= edge + delta <= stop}
        choices = [(None, "NO-WINDOW")] if pin == "B" else [(DEFAULT, DEFAULT), (ALTERNATE, ALTERNATE)]
        for t0 in sorted(probes):
            expected = next(
                (label for window, label in choices
                 if any(first <= t0 <= last and admitted for first, last, admitted in windows[window])),
                "NONE",
            )
            rows.append((t0, pin, size, expected))
    return rows


def run_test(shell, mode, rows):
    setup = '. "$1"\n' if mode == "sourced" else ""
    call = 'pick_filler_arg' if mode == "sourced" else '"$1"'
    script = f'''set -eu
{setup}while read -r epoch pin size; do
    {call} "$epoch" "$pin" "$size"
done
'''
    result = subprocess.run(
        [shell, "-c", script, "picker-test", str(ROOT / "pick_filler_arg.sh")],
        input="".join(f"{t0} {pin} {size}\n" for t0, pin, size, _ in rows),
        check=True, text=True, capture_output=True,
    )
    for row, actual in zip(rows, result.stdout.splitlines(), strict=True):
        assert actual == row[3], (shell, mode, row, actual)
    print(f"PASS {shell} {mode}: {len(rows)} picker comparisons")


def main():
    rows = test_rows(json.loads((ROOT / "bands.json").read_text()))
    for shell, mode in product(("bash", "zsh"), ("executed", "sourced")):
        run_test(shell, mode, rows)


if __name__ == "__main__":
    main()
