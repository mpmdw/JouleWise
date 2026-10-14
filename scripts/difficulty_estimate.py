#!/usr/bin/env python3
"""Estimate DIFFICULTY accuracy, energy, token effects and crossover."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.packs.difficulty.config import load_config
from joulewise.packs.difficulty.estimators import estimate_tables, read_csv, write_tables


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("bench", "energy", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--confidence", type=float)
    parser.add_argument("--exclude-flags")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config) if args.config else {}
        bench, energy = read_csv(args.bench), read_csv(args.energy)
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError) as exc:
        print(f"unusable config or table file: {exc}", file=sys.stderr)
        return 2
    confidence = args.confidence if args.confidence is not None else config.get("confidence", 0.95)
    if not 0 < confidence < 1:
        parser.error("--confidence must be between 0 and 1")
    exclude = (args.exclude_flags.split(",") if args.exclude_flags is not None
               else config.get("exclude_flags", []))
    tables = estimate_tables(bench, energy, confidence, [flag.strip() for flag in exclude if flag.strip()])
    write_tables(args.out, tables)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
