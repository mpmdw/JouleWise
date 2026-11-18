#!/usr/bin/env python3
"""ALIGN v4 series release entry point.

The release guard owns the withheld document. Released inputs require the
analysis integration owner's authenticated record and bundle mapping.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align.apple import rl176
from joulewise.b5.harvest import write_json_once


def _load_members():
    # The desk guard checks release metadata before calling this provider.
    # It does not authenticate the external record or bundle mapping.
    raise ValueError("series release requires an authenticated final-record and bundle binding")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurement-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = rl176.series_release_prints(
            {"measurement_root": args.measurement_root},
            load_members=_load_members,
            q_words_frozen=True,
        )
        write_json_once(args.output, report)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"series release refused: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
