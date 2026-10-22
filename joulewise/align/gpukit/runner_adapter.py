"""Provisional translation to the runner lane's factory-based matrix format.

Based on docs/align/runner.md from lane/2026-10-21-align-runner. No runner
implementation is copied here. Budget effort trials still need their own driver.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

from joulewise.align.gpukit.matrix import validate


def runner_matrix(matrix: Mapping[str, Any], *, model: str, endpoint: str,
                  output_dir: Path, settings: Mapping[str, Any]) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Translate one model with caller-supplied factory names and run limits.

    Settings require task/endpoint/monitor/sampler/token_counter_factory,
    order_seed, max_turns, max_tokens and temperature. Optional *_config objects
    and imports are passed to the runner. Unavailable integrations stay flags.
    """
    flags = list(validate(matrix))
    flags.append("runner_adapter_provisional")
    if matrix.get("kind") == "budget":
        flags.append("budget_runner_adapter_required")
    models = {m["id"]: m for m in matrix.get("models", ())}
    if model not in models:
        flags.append("runner_adapter_model_unknown")
    for kind in ("task", "endpoint", "monitor", "sampler", "token_counter"):
        if not isinstance(settings.get(kind + "_factory"), str) or not settings[kind + "_factory"]:
            flags.append("runner_adapter_factory_missing:" + kind)
        if not isinstance(settings.get(kind + "_config", {}), dict):
            flags.append("runner_adapter_config_invalid:" + kind)
    for key in ("max_turns", "max_tokens"):
        if type(settings.get(key)) is not int or settings[key] <= 0:
            flags.append("runner_adapter_limit_invalid:" + key)
    if type(settings.get("order_seed")) is not int:
        flags.append("runner_adapter_order_seed_invalid")
    temperature = settings.get("temperature")
    if (isinstance(temperature, bool) or not isinstance(temperature, (int, float))
            or not math.isfinite(temperature) or temperature < 0):
        flags.append("runner_adapter_temperature_invalid")
    imports = settings.get("imports", [])
    if not isinstance(imports, list) or any(not isinstance(x, str) for x in imports):
        flags.append("runner_adapter_imports_invalid")
    if any(f != "runner_adapter_provisional" for f in flags):
        return {}, tuple(sorted(set(flags)))

    def component(kind: str, **extra: Any) -> dict[str, Any]:
        return {"factory": settings[kind + "_factory"],
                "config": {**settings.get(kind + "_config", {}), **extra}}

    model_spec = models[model]
    result = {
        "matrix_id": matrix["name"] + ":" + model,
        "order_seed": settings["order_seed"],
        "task_pairs": [component("task", task_pair=task) for task in matrix["tasks"]],
        "conditions": list(matrix["conditions"]),
        "seeds": list(matrix["seeds"]),
        "endpoints": [component("endpoint", model=model, revision=model_spec.get("revision"),
                                base_url=endpoint.rstrip("/") + "/v1",
                                router_logging=matrix["kind"] == "moe_stage_a")],
        "monitors": [{**component("monitor", model=matrix["monitor_model"]),
                      "visibilities": list(matrix["monitor_visibilities"])}],
        "samplers": [component("sampler", interval_ns=matrix["sampling"]["interval_ns"])],
        "token_counter": component("token_counter", model=model,
                                   revision=model_spec.get("revision"),
                                   base_url=endpoint.rstrip("/") + "/v1"),
        "max_turns": settings["max_turns"],
        "max_tokens": settings["max_tokens"],
        "temperature": temperature,
        "output_dir": str(output_dir.resolve()),
    }
    # Runner also reads the task_pair at the component's outer level when
    # deriving coordinates; its factory receives config unchanged.
    for task, name in zip(result["task_pairs"], matrix["tasks"]):
        task["task_pair"] = name
    if imports:
        result["imports"] = list(imports)
    return result, tuple(flags)


def write_runner_matrix(path: Path, matrix: Mapping[str, Any], *, model: str,
                        endpoint: str, output_dir: Path,
                        settings: Mapping[str, Any]) -> tuple[str, ...]:
    """Write a translated matrix for review, preserving adapter flags separately."""
    value, flags = runner_matrix(matrix, model=model, endpoint=endpoint,
                                 output_dir=output_dir, settings=settings)
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
                          encoding="utf-8")
    return flags
