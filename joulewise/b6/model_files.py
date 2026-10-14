"""Compare the computation a run records with its registered model and stack."""

from __future__ import annotations

from typing import Any, Mapping

PACKAGES = ("mlx", "mlx-lm", "transformers")


def run_identity(metadata: Mapping) -> dict[str, Any]:
    runtime = (metadata.get("adapters") or {}).get("runtime") or {}
    prepare = runtime.get("prepare_metadata") or {}
    artifact = prepare.get("model_artifact_identity") or {}
    # Accept the normalized identity handed over by precheck too.
    if "model_artifact_sha256" in metadata:
        return {key: metadata.get(key) for key in
                ("model_source", "model_artifact_sha256", "status", "packages", "quantization", "runtime")}
    return {"model_source": prepare.get("model_source"),
            "model_artifact_sha256": artifact.get("folded_sha256", artifact.get("sha256")),
            "status": artifact.get("status", "missing"),
            "packages": {"mlx": prepare.get("mlx_version"),
                         "mlx-lm": prepare.get("mlx_lm_version"),
                         "transformers": prepare.get("transformers_version")},
            "quantization": metadata.get("quantization", prepare.get("quantization")),
            "runtime": runtime.get("name")}


def expected(identity_pins: Mapping) -> dict[str, Any]:
    models: dict[str, dict] = {}
    for unit in (identity_pins.get("units") or {}).values():
        source, digest = unit.get("model_source"), unit.get("model_artifact_sha256")
        if not source:
            continue
        entry = models.setdefault(source, {"sha256s": [], "stacks": []})
        if digest not in entry["sha256s"]:
            entry["sha256s"].append(digest)
        stack = unit.get("stack_identity") or {}
        actual = {"runtime": (stack.get("runtime_version") or {}).get("name"),
                  "quantization": stack.get("quantization")}
        if actual not in entry["stacks"]:
            entry["stacks"].append(actual)
    return {"models": models, "runtime_versions": {
        "packages": {key: (identity_pins.get("runtime_versions", {}).get("packages") or {}).get(key)
                     for key in PACKAGES}}}


def compare(expected: Mapping, observed: Mapping) -> list[dict]:
    if observed.get("status") != "ok" or not observed.get("model_artifact_sha256"):
        return [{"code": "model.identity_unrecorded", "fields": []}]
    mismatches = []
    source = observed.get("model_source")
    pin = expected.get("models", {}).get(source)
    if pin is None or observed["model_artifact_sha256"] not in pin["sha256s"]:
        mismatches.append({"code": "model.files_differ_from_registered", "fields": ["model_artifact_sha256"]})
    fields = []
    versions = expected.get("runtime_versions", {}).get("packages", {})
    for key in PACKAGES:
        if (observed.get("packages") or {}).get(key) != versions.get(key):
            fields.append(key)
    if pin:
        candidate = {"runtime": observed.get("runtime"), "quantization": observed.get("quantization")}
        # Prepare records sometimes name quantization only; metadata normally
        # supplies its complete registered object.
        stacks = pin["stacks"]
        matches = [stack for stack in stacks if all(
            candidate[key] == stack[key] or
            (key == "quantization" and isinstance(candidate[key], str)
             and isinstance(stack[key], Mapping) and candidate[key] == stack[key].get("name"))
            for key in candidate)]
        if not matches:
            fields.extend(key for key in candidate if not any(
                candidate[key] == stack[key] for stack in stacks))
            if not fields:
                fields.extend(candidate)
    if fields:
        mismatches.append({"code": "model.stack_differs_from_registered", "fields": sorted(set(fields))})
    return mismatches
