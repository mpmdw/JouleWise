#!/usr/bin/env python3
"""Compare the two row readers on the first invented instrument leg."""

import argparse
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from joulewise.cadence_looks.description import project_gpu_rows, step3_reader
from tests.test_desc_looks_acceptance import traces


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False, add_help=False)
    parser.add_argument("--invented-world", required=True, choices=("first-instrument",))
    if sys.argv[1:] != ["--invented-world", "first-instrument"]:
        parser.error("expected --invented-world first-instrument")
    parser.parse_args()
    with tempfile.TemporaryDirectory() as scratch:
        source = Path(scratch)
        traces(source, 1, 0)
        with (source / "power_trace.csv").open(encoding="utf-8", newline="") as stream:
            rows = project_gpu_rows(stream)
        print(json.dumps({"description": rows, "pinned_step3": step3_reader().load_gpu_trace(source)},
                         separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
