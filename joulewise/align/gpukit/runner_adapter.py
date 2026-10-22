"""Translate campaign rows into the runner's factory/config format.

Only operator-requested config keys cross this seam. Placeholders substitute
session bindings without assuming a factory constructor signature.
"""

from __future__ import annotations

import json
import math
import uuid
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.align.gpukit.matrix import validate


def runner_matrix(matrix: Mapping[str, Any], *, model: str, endpoint: str,
                  output_dir: Path, settings: Mapping[str, Any],
                  session_id: str | None = None, monitor_endpoint: str | None = None,
                  judge_endpoint: str | None = None,
                  device_indices: Sequence[int] = ()) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Bind explicit *_config placeholders; pass optional clock settings through."""
    flags = list(validate(matrix))
    flags.append("runner_adapter_provisional")
    if matrix.get("kind") == "budget":
        flags.append("budget_runner_adapter_required")
    models = {m["id"]: m for m in matrix.get("models", ())}
    if model not in models:
        flags.append("runner_adapter_model_unknown")
    kinds = ("task", "endpoint", "sampler", "token_counter")
    if monitor_endpoint is not None:
        kinds += ("monitor",)
    for kind in kinds:
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

    def api(url: str | None) -> str | None:
        return url.rstrip("/").removesuffix("/v1") + "/v1" if url else None

    bindings = {
        "agent_model": model, "agent_base_url": api(endpoint),
        "agent_revision": models[model].get("revision"),
        "monitor_model": matrix["monitor_model"], "monitor_base_url": api(monitor_endpoint),
        "judge_model": matrix.get("judge_model", matrix["monitor_model"]),
        "judge_base_url": api(judge_endpoint),
        "interval_ns": matrix["sampling"]["interval_ns"],
        "device_indices": list(device_indices),
        "router_logging": matrix["kind"] == "moe_stage_a",
    }

    def fill(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: fill(v) for k, v in value.items()}
        if isinstance(value, list):
            return [fill(v) for v in value]
        if isinstance(value, str):
            for key, replacement in bindings.items():
                if value == "{" + key + "}":
                    return replacement
            # Ordinary text/braces are preserved; only named placeholders expand.
            for key, replacement in bindings.items():
                value = value.replace("{" + key + "}", str(replacement))
        return value

    def component(kind: str) -> dict[str, Any]:
        return {"factory": settings[kind + "_factory"],
                "config": fill(settings.get(kind + "_config", {}))}

    result = {
        "matrix_id": matrix["name"] + ":" + model + ":" + (session_id or uuid.uuid4().hex),
        "order_seed": settings["order_seed"],
        "task_pairs": [{**component("task"), "task_pair": task} for task in matrix["tasks"]],
        "conditions": list(matrix["conditions"]), "seeds": list(matrix["seeds"]),
        "endpoints": [component("endpoint")],
        "monitors": ([{**component("monitor"), "visibilities": list(matrix["monitor_visibilities"])}]
                     if monitor_endpoint is not None else []),
        "samplers": [component("sampler")], "token_counter": component("token_counter"),
        "max_turns": settings["max_turns"], "max_tokens": settings["max_tokens"],
        "temperature": temperature, "output_dir": str(output_dir.resolve()),
    }
    if imports:
        result["imports"] = list(imports)
    for key in ("clock", "clock_domain"):
        if key in settings:
            result[key] = fill(settings[key])
    return result, tuple(flags)


def write_runner_matrix(path: Path, matrix: Mapping[str, Any], *, model: str,
                        endpoint: str, output_dir: Path, settings: Mapping[str, Any],
                        **bindings: Any) -> tuple[str, ...]:
    """Write the translated matrix and return its integration flags."""
    value, flags = runner_matrix(matrix, model=model, endpoint=endpoint,
                                 output_dir=output_dir, settings=settings, **bindings)
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
                          encoding="utf-8")
    return flags
