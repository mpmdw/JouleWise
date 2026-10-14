"""Compare the computation a run records with its registered model and stack."""

from __future__ import annotations

from typing import Any, Mapping

from joulewise.identity_pins import _path_independent_identifier

PACKAGES = ("mlx", "mlx-lm", "transformers", "mlx-metal")


def _tokenizer(value: Mapping) -> dict:
    return {key: _path_independent_identifier(item) if key == "identifier" else item
            for key in ("identifier", "revision", "vocab_size")
            if (item := value.get(key)) is not None}


def run_identity(metadata: Mapping) -> dict[str, Any]:
    runtime = (metadata.get("adapters") or {}).get("runtime") or {}
    prepare = runtime.get("prepare_metadata") or {}
    artifact = prepare.get("model_artifact_identity") or {}
    # Accept the normalized identity handed over by precheck too.
    if "model_artifact_sha256" in metadata:
        identity = {key: metadata[key] for key in
                    ("model_source", "model_artifact_sha256", "status", "packages", "quantization", "runtime",
                     "runtime_version", "kernel_library", "tokenizer") if key in metadata}
        if identity.get("tokenizer"):
            identity["tokenizer"] = _tokenizer(identity["tokenizer"])
        return identity
    environment = (metadata.get("environment") or {}).get("python_packages") or {}
    versions = {"mlx": prepare.get("mlx_version"), "mlx-lm": prepare.get("mlx_lm_version"),
                "transformers": prepare.get("transformers_version"),
                "mlx-metal": prepare.get("mlx_metal_version", prepare.get("mlx-metal_version"))}
    for key in PACKAGES:
        entry = environment.get(key)
        if versions[key] is None:
            versions[key] = entry.get("version") if isinstance(entry, Mapping) else entry
    identity = {"model_source": prepare.get("model_source"),
            "model_artifact_sha256": artifact.get("folded_sha256", artifact.get("sha256")),
            "status": artifact.get("status", "missing"),
            "packages": {key: value for key, value in versions.items() if value is not None},
            "quantization": metadata.get("quantization", prepare.get("quantization")),
            "runtime": runtime.get("name")}
    for key, value in {
        "runtime_version": prepare.get("version") or prepare.get("mlx_version") or prepare.get("mlx_lm_version"),
        "kernel_library": prepare.get("kernel_library"),
        "tokenizer": _tokenizer((metadata.get("workload_provenance") or {}).get("tokenizer") or {}),
    }.items():
        if value is not None and value != {}:
            identity[key] = value
    return identity


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
                  "runtime_version": (stack.get("runtime_version") or {}).get("version"),
                  "kernel_library": stack.get("kernel_library"),
                  "tokenizer": _tokenizer(stack.get("tokenizer_identity") or {}),
                  "quantization": stack.get("quantization"), "model_artifact_sha256": digest}
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
    if pin is None:
        mismatches.append({"code": "model.source_unpinned", "fields": ["model_source"]})
    elif observed["model_artifact_sha256"] not in pin["sha256s"]:
        mismatches.append({"code": "model.files_differ_from_registered", "fields": ["model_artifact_sha256"]})
    fields = []
    versions = expected.get("runtime_versions", {}).get("packages", {})
    for key in PACKAGES:
        value = (observed.get("packages") or {}).get(key)
        if value is not None and value != versions.get(key):
            fields.append(key)
    if pin:
        candidate = {key: observed[key] for key in ("runtime", "runtime_version", "quantization", "kernel_library")
                     if observed.get(key) is not None and not (key == "kernel_library" and observed[key] == "unavailable")}
        tokenizer = _tokenizer(observed.get("tokenizer") or {})

        def differs(stack: Mapping) -> list[str]:
            fields = [key for key, value in candidate.items() if value != stack.get(key) and not
                      (key == "quantization" and isinstance(value, str) and isinstance(stack.get(key), Mapping)
                       and value == stack[key].get("name"))]
            fields.extend("tokenizer." + key for key, value in tokenizer.items()
                          if value != (stack.get("tokenizer") or {}).get(key))
            return fields
        # Prepare records sometimes name quantization only; metadata normally
        # supplies its complete registered object.
        stacks = [stack for stack in pin["stacks"]
                  if stack["model_artifact_sha256"] == observed["model_artifact_sha256"]] or pin["stacks"]
        differences = [differs(stack) for stack in stacks]
        if differences and all(differences):
            fields.extend(min(differences, key=lambda items: (len(items), items)))
    if fields:
        mismatches.append({"code": "model.stack_differs_from_registered", "fields": sorted(set(fields))})
    return mismatches
