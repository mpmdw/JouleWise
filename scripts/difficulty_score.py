#!/usr/bin/env python3
"""Score recorded generations into the DIFFICULTY bench table."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.packs.difficulty.config import load_config
from joulewise.packs.difficulty.score import BENCH_COLUMNS, score_generations
from joulewise.packs.difficulty.estimators import write_csv


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("manifest", "config", "generations", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.expanduser().read_text(encoding="utf-8"))
        config = load_config(args.config)
        generations = []
        for line in args.generations.expanduser().read_text(encoding="utf-8").splitlines():
            try:
                generations.append(json.loads(line))
            except ValueError:
                generations.append({})
        rows = score_generations(manifest, config, generations)
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError) as exc:
        print(f"unusable config or manifest: {exc}", file=sys.stderr)
        return 2
    write_csv(args.out.expanduser(), BENCH_COLUMNS, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
