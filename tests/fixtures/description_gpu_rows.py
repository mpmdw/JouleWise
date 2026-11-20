#!/usr/bin/env python3
"""Compare the two row readers on the first invented instrument leg."""

import argparse
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from joulewise.cadence_looks.description import NS_PER_SECOND, Signals, step3_reader
from tests.test_desc_looks_acceptance import read, traces


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False, add_help=False)
    parser.add_argument("--invented-world", required=True, choices=("first-instrument",))
    if sys.argv[1:] != ["--invented-world", "first-instrument"]:
        parser.error("expected --invented-world first-instrument")
    parser.parse_args()
    with tempfile.TemporaryDirectory() as scratch:
        source = Path(scratch)
        traces(source, 1, 0)
        support = read(source / "support.json")
        pinned = step3_reader()
        signal = Signals(support, {"power_trace.csv": source / "power_trace.csv"}, lambda: None, pinned)
        bounds = support["rail_intervals"]
        rows = signal.interval_values("gpu_rail", (bounds[0][0], bounds[-1][1]))
        seconds_rows = [(a / NS_PER_SECOND, b / NS_PER_SECOND, watts, t / NS_PER_SECOND)
                        for a, b, watts, t in rows]
        print(json.dumps({"description": seconds_rows, "pinned_step3": pinned.load_gpu_trace(source)},
                         separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
