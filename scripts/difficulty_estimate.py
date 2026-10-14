#!/usr/bin/env python3
"""Estimate DIFFICULTY accuracy, energy, token effects and crossover."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.packs.difficulty.config import load_config
from joulewise.packs.difficulty.estimators import estimate_tables, read_csv, write_tables


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("config", "selections", "bench", "energy", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        selection_text = args.selections.expanduser().read_text(encoding="utf-8")
        try:
            selections = json.loads(selection_text)
        except ValueError:
            selections = {}
        bench, energy = read_csv(args.bench), read_csv(args.energy)
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError) as exc:
        print(f"unusable config or table file: {exc}", file=sys.stderr)
        return 2
    tables = estimate_tables(bench, energy, config, selections)
    write_tables(args.out, tables)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
