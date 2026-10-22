"""Run a synthetic smoke or a configured local-server pilot from the command line."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path

from joulewise.align.budget.energy import episode_energy
from joulewise.align.budget.conditions import Condition, LocalEndpoint, default_conditions
from joulewise.align.budget.items import HubMMLUSource, HubPin, ItemBatch, stratified_roster
from joulewise.align.budget.run import ModelSpec, Settings, run_matrix, summarize, summary_table
from joulewise.align.budget.score import DEFAULT_MONITOR_MODEL, HintMonitor
from joulewise.align.budget.storage import write_episode_views, write_result
from joulewise.align.budget.synthetic import run_synthetic
from joulewise.align.records import ClockMapping, to_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--synthetic", action="store_true")
    mode.add_argument("--config", type=Path, help="JSON configuration for local serving endpoints")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--count", type=int, default=200,
                        help="item limit; config dataset.count takes precedence (default: 200)")
    parser.add_argument("--seeds", default="0")
    parser.add_argument("--sizes", default="4")
    args = parser.parse_args(argv)
    try:
        seeds = tuple(int(s) for s in args.seeds.split(","))
        energy_options = {}
        if args.synthetic:
            result = run_synthetic(count=args.count, seeds=seeds,
                                   sizes_b=tuple(float(s) for s in args.sizes.split(",")),
                                   checkpoint=args.checkpoint)
            confidence = 0.95
        else:
            config = json.loads(args.config.read_text(encoding="utf-8"))
            if any(key not in config for key in ("models", "monitor", "settings")):
                raise ValueError("config requires models, monitor and settings")
            source = config.get("dataset", {})
            kwargs = {"timeout_s": source.get("timeout_s", 60), "seed": source.get("seed", 0)}
            if "pin" in source:
                kwargs["pin"] = HubPin(**source["pin"])
            batch = HubMMLUSource(**kwargs).load()
            # The selected roster is deterministic, fixed before any model runs,
            # and included byte-for-byte in the resume fingerprint.
            count = source.get("count", args.count)
            items = stratified_roster(batch, count, seed=source.get("roster_seed", source.get("seed", 0)))
            energy_options = config.get("energy", {})
            models = []
            for entry in config["models"]:
                endpoint = LocalEndpoint(entry["base_url"], entry["model"], entry["backend"],
                                         entry["timeout_s"], options=entry.get("options", {}))
                models.append(ModelSpec(
                    entry["model"], entry["size_b"], entry["backend"],
                    endpoint.identity + ":" + entry["runtime_revision"], endpoint, endpoint.configured,
                    entry["attention_design"], entry["clock_domain"],
                    tuple(ClockMapping(**m) for m in entry.get("clock_mappings", ())),
                    entry.get("controls_verified", False)))
            monitor_config = config["monitor"]
            monitor_endpoint = LocalEndpoint(
                monitor_config["base_url"], monitor_config.get("model", DEFAULT_MONITOR_MODEL),
                monitor_config["backend"], monitor_config["timeout_s"],
                options=monitor_config.get("options", {}))
            monitor = HintMonitor(monitor_endpoint, model=monitor_endpoint.model,
                                  max_tokens=monitor_config.get("max_tokens", 2048),
                                  seed=monitor_config.get("seed", 0),
                                  revision=monitor_config["runtime_revision"])
            settings = Settings(**config["settings"])
            confidence = settings.confidence
            conditions = (tuple(Condition(**c) for c in config["conditions"])
                          if "conditions" in config else default_conditions())
            sampler_factory = None
            if "sampler" in config:
                sampler_config = config["sampler"]
                def sampler_factory(model):
                    # Construction belongs inside the runner's flagged sampler-error path.
                    module, name = sampler_config["factory"].split(":")
                    constructor = getattr(importlib.import_module(module), name)
                    return constructor(**sampler_config.get("kwargs", {}))
            result = run_matrix(items, models, conditions, seeds=seeds, settings=settings,
                                monitor=monitor, checkpoint=args.checkpoint,
                                sampler_factory=sampler_factory,
                                run_metadata={"energy": energy_options})
        rows = summarize(result.trials, confidence=confidence,
                         energy_reducer=lambda ep: episode_energy(ep, **energy_options))
        args.output.mkdir(parents=True, exist_ok=True)
        write_result(args.output / "result.json", result)
        (args.output / "summary.json").write_text(to_json(rows) + "\n", encoding="utf-8")
        (args.output / "summary.md").write_text(summary_table(rows), encoding="utf-8")
        write_episode_views(args.output / "episodes.jsonl", (t.episode for t in result.trials))
        write_episode_views(args.output / "paired_episodes.jsonl", (t.paired.episode for t in result.trials
                                                             if t.source_trial_id is None))
        write_episode_views(args.output / "calibration_episodes.jsonl",
                       (e for c in result.calibrations for e in c.episodes))
        print(summary_table(rows), end="")
        print(to_json({"run_sha256": result.run_sha256, "flags": result.flags}))
    except Exception as exc:
        print(to_json({"flags": [f"pilot_error:{type(exc).__name__}"]}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
