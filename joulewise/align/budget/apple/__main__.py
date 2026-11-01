"""D3 Apple replication: explicit offline rehearsal or hardware via --live."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from joulewise.align.budget.apple.models import MODEL_SIZES, resolve_model
from joulewise.align.budget.apple.run import run_dry, run_live
from joulewise.align.budget.conditions import LocalEndpoint
from joulewise.align.budget.items import ItemBatch
from joulewise.align.budget.run import Settings
from joulewise.align.budget.score import HintMonitor
from joulewise.align.records import from_json, to_json
from joulewise.schemas import BenchmarkConfig


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True,
                        help="existing BenchmarkConfig JSON; dry-run uses only sampling settings")
    parser.add_argument("--count", type=int, default=2, help="synthetic item count only")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--model", choices=tuple(MODEL_SIZES))
    parser.add_argument("--revision", help="full cached commit SHA; no downloads")
    parser.add_argument("--cache", type=Path,
                        default=Path(os.environ.get("HF_HUB_CACHE", Path.home() / ".cache/huggingface/hub")))
    parser.add_argument("--config", type=Path, help="live settings, frozen roster path and fixed remote monitor")
    args = parser.parse_args(argv)
    try:
        benchmark = BenchmarkConfig.from_mapping(json.loads(args.benchmark.read_text()))
        if args.dry_run:
            result = run_dry(output=args.output, config=benchmark, count=args.count, seed=args.seed)
        else:
            if not args.model or args.config is None:
                raise ValueError("--live requires --model and --config")
            cfg = json.loads(args.config.read_text(encoding="utf-8"))
            model = resolve_model(args.model, args.cache, args.revision)
            roster = Path(cfg["roster"])
            if not roster.is_absolute():
                roster = args.config.parent / roster
            items = from_json(ItemBatch, roster.read_text(encoding="utf-8"))
            entry = cfg["monitor"]
            endpoint = LocalEndpoint(entry["base_url"], entry["model"], entry["backend"],
                                     entry["timeout_s"], options=entry.get("options", {}))
            monitor = HintMonitor(endpoint, model=entry["model"], revision=entry["runtime_revision"],
                                  max_tokens=entry.get("max_tokens", 2048), seed=entry.get("seed", 0))
            result = run_live(output=args.output, config=benchmark, model=model, items=items,
                              monitor=monitor, settings=Settings(**cfg["settings"]), seed=args.seed,
                              controls_verified=cfg.get("controls_verified", False),
                              condition_order=cfg.get("condition_order"))
        print(to_json({"status": "PROVISIONAL_UNREGISTERED", "synthetic": args.dry_run,
                       "trials": len(result.trials), "run_sha256": result.run_sha256,
                       "flags": result.flags}))
        return 0
    except Exception as exc:
        print(to_json({"status": "failed", "error": f"{type(exc).__name__}:{exc}"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
