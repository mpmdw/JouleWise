#!/usr/bin/env python3
"""Write the block-5 model and runtime identity pins (``joulewise.b5_identity_pins.v1``).

The driver passes ``configs/campaigns/v5_claim_25g83/identity_pins.json`` to the
arm's model-identity collector (``--identity-pins``) and the harvest reads it as
``identity_pins.json``. Per identity unit it carries ``model_artifact_sha256``
and ``runtime_identity_sha256``; at the top it carries
``runtime_versions_sha256``. This program derives them without running a model.

Where each pin comes from
-------------------------
The ``_v5`` packs carry no frozen pins: every unit's
``arm_attachments.identity_pin_projection.model_runtime_config`` is null and no
``identity_pin_projection.receipts/`` exist (state ``unprojected``). The only
committed freeze path (``identity_pins.freeze_projection``) loads each model
through ``runtime.prepare``, which this program must not do. So:

* ``model_artifact_sha256`` is the model artifact digest that real block-3
  bundles of the same model, at the same revision and source, recorded in
  ``workload_provenance.model.artifact_identity`` (archived harvests). All
  reference bundles of a model must agree. A frozen pin in a plan tree, if one
  ever appears, must equal it. ``--hash-local-models`` also hashes the local
  mirror read-only (``provenance.model_artifact_identity``) and refuses on a
  difference.
* ``runtime_identity_sha256`` is the digest the harvest recomputes from each
  bundle (``identity_pins.derive_model_runtime_config_from_metadata``): the
  eleven-field stack identity. Ten of its fields come from the runtime and the
  machine (OS, MLX version, tokenizer, sampler, device...), so they are taken
  from the reference bundles of the same model, quantization and hardware
  target. The eleventh, the output policy, depends on how the unit's configs
  run: a config with a suite manifest runs ``run_suite`` (policy name from the
  manifest, requested tokens = the planned output tokens of its items,
  ``suite_completed``); any other config runs ``run_workload``
  (``fixed_budget_exact``, ``output_tokens``, ``requested_tokens_emitted``).
  The same rule applied to each reference config must reproduce that bundle's
  recorded policy, or the program refuses. Note: the projection probe
  (``identity_projection_metadata``) writes ``requested_tokens_emitted`` for
  every unit, so a projection-derived runtime pin would not match a suite
  bundle at harvest; this file uses the bundle form the harvest compares.
* ``runtime_versions_sha256`` is ``flags.collect.runtime_versions_sha256`` of
  ``flags.collect.runtime_versions`` run on the measurement interpreter
  (``importlib.metadata`` only, nothing imported from MLX). The reference
  bundles must have been measured under the same Python, MLX, mlx-lm and
  transformers versions and the same ``platform.platform()`` as that
  interpreter reports now, or the stack would be stale; otherwise it refuses.

The file is a draft: ``status`` is ``UNSEALED_DRAFT`` until the seal replaces
it. Nothing here arms, installs, launches, or loads a model.

Example::

    python scripts/write_b5_identity_pins.py            # writes the default output
    python scripts/write_b5_identity_pins.py --check    # exit 1 if the file differs
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.flags.collect import (  # noqa: E402
    IDENTITY_PINS_SCHEMA,
    runtime_versions,
    runtime_versions_sha256,
)
from joulewise.identity_pins import (  # noqa: E402
    STACK_IDENTITY_FIELDS,
    build_stack_identity,
    canonical_json_sha256,
    identity_unit_config_set_sha256,
    scientific_config_identity_sha256,
    stack_identity_sha256,
)
from joulewise.provenance import fixed_budget_outcome_name, model_artifact_identity  # noqa: E402
from joulewise.schemas import BenchmarkConfig, SchemaError  # noqa: E402
from joulewise.suite import (  # noqa: E402
    SuiteManifest,
    canonical_effective_manifest,
    migrate_suite_manifest,
    realized_order,
    suite_manifest_sha256,
)

STATUS_UNSEALED = "UNSEALED_DRAFT"
DEFAULT_OUTPUT = "configs/campaigns/v5_claim_25g83/identity_pins.json"
DEFAULT_PACKS = (
    "configs/campaigns/d117_floor_qwen3-1p7b_v5",
    "configs/campaigns/d117_floor_qwen3-8b_v5",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
)
# Block 3's last window (b3w1, re-harvested 2026-10-04): real Qwen3-1.7B and
# Qwen3-8B bundles under the runtime block 5 runs.
DEFAULT_REFERENCE_ROOTS = (
    "/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/g2a-root/runs",
)
# The measurement interpreter: the chain runs <checkout>/.venv/bin/python.
DEFAULT_RUNTIME_PYTHON = "/Users/edr/code/JouleWise/.venv/bin/python"

# mlx_runtime.run_suite / run_workload literals (joulewise/adapters/mlx_runtime.py).
SUITE_STOP_CONDITION = "suite_completed"
SINGLE_STOP_CONDITION = "requested_tokens_emitted"
OUTPUT_POLICY_KEYS = ("name", "requested_tokens", "stop_condition")
# Reference prepare-metadata fields and the runtime-probe package each must equal.
REFERENCE_PACKAGE_FIELDS = (("mlx_version", "mlx"), ("mlx_lm_version", "mlx-lm"),
                            ("transformers_version", "transformers"))
_PLATFORM_PROBE = ("import json, platform\n"
                   "print(json.dumps({'platform': platform.platform(), 'machine': platform.machine()}, "
                   "sort_keys=True))\n")


class IdentityPinsError(ValueError):
    """The pins cannot be derived; nothing was written."""


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise IdentityPinsError(detail)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path, label: str) -> tuple[Any, bytes]:
    try:
        raw = path.read_bytes()
        return json.loads(raw), raw
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdentityPinsError(f"{label} {path} cannot be read: {exc}") from exc


def _relative_inside(root: Path, value: Any, label: str) -> Path:
    _require(isinstance(value, str) and value and not PurePosixPath(value).is_absolute()
             and ".." not in PurePosixPath(value).parts, f"{label} must be a relative path without '..'")
    return root / value


def _typed(config: Mapping[str, Any], where: str) -> BenchmarkConfig:
    try:
        return BenchmarkConfig.from_mapping(dict(config))
    except (SchemaError, TypeError, ValueError) as exc:
        raise IdentityPinsError(f"{where} is not a valid benchmark config: {exc}") from exc


def stack_relevant_config(config: Mapping[str, Any], where: str = "config") -> dict[str, Any]:
    """The config fields a bundle's stack identity can depend on, other than the output policy.

    ``build_stack_identity`` reads the config's ``hardware_target.id``; the
    runtime derives the tokenizer identity and the model artifact from
    ``model.source`` and ``model.revision``; the controller writes
    ``asdict(config.quantization)``. Two configs with equal values here run
    under one stack apart from the output policy.
    """

    typed = _typed(config, where)
    return {
        "model": {"name": typed.model.name, "source": typed.model.source, "revision": typed.model.revision,
                  "weight_format": typed.model.weight_format},
        "quantization": asdict(typed.quantization),
        "hardware_target": {"id": typed.hardware_target.id,
                            "runtime_backend": typed.hardware_target.runtime_backend.value,
                            "telemetry_backend": typed.hardware_target.telemetry_backend.value},
    }


def load_suite_manifest(config: Mapping[str, Any], repo_root: Path, where: str = "config") -> SuiteManifest | None:
    """The config's suite manifest, loaded and authenticated as the controller does; None without one."""

    typed = _typed(config, where)
    profile = typed.workload_profile
    if profile.suite_manifest_ref is None:
        return None
    path = _relative_inside(repo_root, profile.suite_manifest_ref, f"{where} suite_manifest_ref")
    raw_manifest, _raw = _read_json(path, "suite manifest")
    try:
        source_hash = suite_manifest_sha256(canonical_effective_manifest(raw_manifest))
        effective = migrate_suite_manifest(raw_manifest)
        manifest = SuiteManifest.from_mapping(effective)
        manifest_hash = suite_manifest_sha256(effective)
    except Exception as exc:  # noqa: BLE001 - the controller fails such a member the same way
        raise IdentityPinsError(f"{where}: suite manifest {path} cannot be loaded: {exc}") from exc
    _require(profile.suite_manifest_sha256 in {source_hash, manifest_hash},
             f"{where}: suite manifest {path} does not hash to the config's suite_manifest_sha256")
    return manifest


def predicted_output_policy(config: Mapping[str, Any], repo_root: Path, where: str = "config") -> dict[str, Any]:
    """The ``{name, requested_tokens, stop_condition}`` a completed member of this config records.

    The stack identity keeps exactly these three keys of
    ``workload_provenance.output_policy``. ``mlx_runtime.run_suite`` writes
    the manifest's ``default_output_policy``, the planned output tokens of
    the realized items and ``suite_completed``; ``run_workload`` writes the
    outcome name of an exact run, ``output_tokens`` and
    ``requested_tokens_emitted``.
    """

    typed = _typed(config, where)
    manifest = load_suite_manifest(config, repo_root, where)
    if manifest is not None:
        try:
            items = realized_order(manifest, order_row=None)
        except SchemaError:
            items = realized_order(manifest, order_row=0)  # rows are permutations; the sum is the same
        return {"name": manifest.execution_policy.default_output_policy,
                "requested_tokens": sum(item.item.shape.planned_output_tokens for item in items),
                "stop_condition": SUITE_STOP_CONDITION}
    requested = typed.workload_profile.output_tokens
    _require(isinstance(requested, int) and requested > 0,
             f"{where}: workload_profile.output_tokens must be set for a single-prompt member")
    return {"name": fixed_budget_outcome_name(requested_tokens=requested, emitted_tokens=requested,
                                              stop_condition=SINGLE_STOP_CONDITION),
            "requested_tokens": requested, "stop_condition": SINGLE_STOP_CONDITION}


@dataclasses.dataclass(frozen=True)
class Unit:
    pack_id: str
    unit_id: str
    declared: Mapping[str, Any]
    configs: tuple[tuple[str, Mapping[str, Any], str], ...]  # (pack-relative path, config, sha256)
    frozen: Mapping[str, Any]


def load_pack_units(pack_root: Path, repo_root: Path) -> tuple[list[Unit], dict[str, Any]]:
    """The identity units of one pack's ``identity_pin_projection``, with their config bytes checked."""

    tree, raw = _read_json(pack_root / "plan_tree.json", "plan tree")
    projection = ((tree.get("arm_attachments") or {}).get("identity_pin_projection")
                  if isinstance(tree, Mapping) else None)
    _require(isinstance(projection, Mapping), f"{pack_root}: plan tree has no identity_pin_projection")
    rows = projection.get("identity_units")
    _require(isinstance(rows, list) and bool(rows), f"{pack_root}: identity_pin_projection lists no units")
    units = []
    for row in rows:
        unit_id = row.get("identity_unit_id") if isinstance(row, Mapping) else None
        _require(isinstance(unit_id, str) and unit_id, f"{pack_root}: an identity unit has no id")
        inventory = row.get("config_inventory")
        _require(isinstance(inventory, list) and bool(inventory), f"{pack_root} unit {unit_id}: no config_inventory")
        configs = []
        for entry in inventory:
            relative = entry.get("path") if isinstance(entry, Mapping) else None
            path = _relative_inside(pack_root, relative, f"unit {unit_id} config path")
            config, config_raw = _read_json(path, f"unit {unit_id} config")
            digest = sha256_bytes(config_raw)
            _require(digest == entry.get("sha256"),
                     f"{pack_root} unit {unit_id}: {relative} hashes to {digest}, the inventory says {entry.get('sha256')}")
            _require(isinstance(config, Mapping), f"{path} is not a JSON object")
            configs.append((relative, config, digest))
        units.append(Unit(pack_root.name, unit_id, dict(row.get("declared_identity") or {}), tuple(configs),
                          dict(row.get("model_runtime_config") or {})))
    source = {"pack_id": pack_root.name, "plan_tree": {"path": _display(pack_root / "plan_tree.json", repo_root),
                                                        "sha256": sha256_bytes(raw)},
              "projection_state": projection.get("state")}
    return units, source


def _display(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


@dataclasses.dataclass(frozen=True)
class Reference:
    run_id: str
    path: Path
    config: Mapping[str, Any]
    metadata: Mapping[str, Any]
    stack: Mapping[str, Any]
    config_sha256: str
    metadata_sha256: str


def load_references(roots: Sequence[Path]) -> tuple[list[Reference], list[dict[str, str]]]:
    """Bundles (``config.json`` + ``metadata.json``) under each root whose stack identity derives.

    Only those two files are read; no energy, power or summary file is opened.
    """

    references, skipped = [], []
    for root in roots:
        _require(root.is_dir(), f"reference root {root} is not a directory")
        for bundle in sorted(child for child in root.iterdir() if child.is_dir()):
            if not ((bundle / "config.json").is_file() and (bundle / "metadata.json").is_file()):
                continue
            config, config_raw = _read_json(bundle / "config.json", "reference config")
            metadata, metadata_raw = _read_json(bundle / "metadata.json", "reference metadata")
            stack = build_stack_identity(config, metadata)
            if stack is None:
                skipped.append({"path": str(bundle), "reason": "stack identity not derivable from its metadata"})
                continue
            references.append(Reference(bundle.name, bundle, config, metadata, stack,
                                        sha256_bytes(config_raw), sha256_bytes(metadata_raw)))
    return references, skipped


def _invariant(stack: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(stack))
    result["sampler_output_policy"] = {"sampler": result["sampler_output_policy"]["sampler"]}
    return result


def _recorded_policy(stack: Mapping[str, Any]) -> dict[str, Any]:
    return dict(stack["sampler_output_policy"]["output_policy"])


def select_reference_stack(key: Mapping[str, Any], references: Sequence[Reference], repo_root: Path,
                           where: str) -> tuple[dict[str, Any], list[Reference]]:
    """The runtime-invariant stack shared by every reference bundle of the same model, quantization and target."""

    matching = [reference for reference in references
                if stack_relevant_config(reference.config, f"reference {reference.run_id}") == key]
    _require(bool(matching), f"{where}: no reference bundle ran {key['model']['name']} at revision "
                             f"{key['model']['revision']} with this quantization and hardware target")
    invariants = {canonical_json_sha256(_invariant(reference.stack)) for reference in matching}
    _require(len(invariants) == 1, f"{where}: the reference bundles of {key['model']['name']} disagree on the "
                                   f"runtime stack ({len(invariants)} distinct): {[r.run_id for r in matching]}")
    for reference in matching:
        expected = predicted_output_policy(reference.config, repo_root, f"reference {reference.run_id}")
        _require(expected == _recorded_policy(reference.stack),
                 f"positive control failed: reference {reference.run_id} recorded output policy "
                 f"{_recorded_policy(reference.stack)}, the rule predicts {expected}")
    return _invariant(matching[0].stack), matching


def check_runtime_environment(references: Sequence[Reference], probe: Mapping[str, Any]) -> dict[str, Any]:
    """The references ran under the interpreter and OS the windows will use, or this refuses."""

    packages = probe.get("packages") or {}
    expected = {"python_version": probe.get("python"), "platform": probe.get("platform"),
                "machine": probe.get("machine")}
    expected.update({field: packages.get(package) for field, package in REFERENCE_PACKAGE_FIELDS})
    for reference in references:
        prepare = ((reference.metadata.get("adapters") or {}).get("runtime") or {}).get("prepare_metadata") or {}
        observed = {"python_version": reference.metadata.get("python_version"),
                    "platform": reference.metadata.get("platform"), "machine": reference.metadata.get("machine")}
        observed.update({field: prepare.get(field) for field, _package in REFERENCE_PACKAGE_FIELDS})
        differences = {name: {"reference": observed[name], "now": expected[name]}
                       for name in expected if observed[name] != expected[name]}
        _require(not differences, f"reference {reference.run_id} ran under another runtime than the measurement "
                                  f"interpreter reports now, so its stack identity would be stale: {differences}")
    return expected


def probe_runtime(python: str) -> dict[str, Any]:
    """``flags.collect.runtime_versions`` plus ``platform.platform()`` of the measurement interpreter."""

    versions = dict(runtime_versions(python))
    try:
        completed = subprocess.run([python, "-B", "-c", _PLATFORM_PROBE], capture_output=True, timeout=60,
                                   check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise IdentityPinsError(f"platform probe with {python} could not run: {exc}") from exc
    _require(completed.returncode == 0, f"platform probe with {python} exited {completed.returncode}")
    try:
        platform_info = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdentityPinsError(f"platform probe with {python} printed no JSON: {exc}") from exc
    return {"versions": versions, "platform": platform_info.get("platform"), "machine": platform_info.get("machine")}


def _artifact_digest(identity: Mapping[str, Any]) -> str | None:
    if identity.get("status") != "ok":
        return None
    return identity.get("sha256") or identity.get("folded_sha256")


def derive_document(*, repo_root: Path, packs: Sequence[Path], reference_roots: Sequence[Path],
                    runtime_probe: Mapping[str, Any], runtime_python: str,
                    local_artifact: Callable[[str], Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """The pins document. ``runtime_probe`` is :func:`probe_runtime`'s result; tests pass a fixed one."""

    versions = dict(runtime_probe["versions"])
    references, skipped = load_references(reference_roots)
    _require(bool(references), "no reference bundle with a derivable stack identity was found")
    environment = check_runtime_environment(references, {**versions, "platform": runtime_probe.get("platform"),
                                                         "machine": runtime_probe.get("machine")})
    units_out: dict[str, Any] = {}
    pack_sources = []
    used: dict[str, Reference] = {}
    local_checks: dict[str, str] = {}
    for pack in packs:
        units, source = load_pack_units(pack, repo_root)
        pack_sources.append(source)
        for unit in units:
            where = f"{unit.pack_id} unit {unit.unit_id}"
            _require(unit.unit_id not in units_out, f"{where}: identity unit id is also declared by another pack")
            keys = {canonical_json_sha256(stack_relevant_config(config, f"{where} {path}")): path
                    for path, config, _digest in unit.configs}
            _require(len(keys) == 1, f"{where}: its configs name more than one model, quantization or target")
            key = stack_relevant_config(unit.configs[0][1], where)
            declared = unit.declared
            _require(declared.get("model_source") == key["model"]["source"]
                     and declared.get("model_revision") == key["model"]["revision"],
                     f"{where}: the configs' model differs from the unit's declared identity")
            policies = {canonical_json_sha256(predicted_output_policy(config, repo_root, f"{where} {path}")): path
                        for path, config, _digest in unit.configs}
            _require(len(policies) == 1, f"{where}: its configs run under more than one output policy")
            policy = predicted_output_policy(unit.configs[0][1], repo_root, where)
            invariant, matching = select_reference_stack(key, references, repo_root, where)
            for reference in matching:
                used[reference.run_id + "\0" + str(reference.path)] = reference
            stack = copy.deepcopy(invariant)
            stack["sampler_output_policy"]["output_policy"] = {name: policy[name] for name in OUTPUT_POLICY_KEYS}
            _require(set(stack) == set(STACK_IDENTITY_FIELDS), f"{where}: stack identity fields are not the governed set")
            model_sha256 = stack["model_artifact_sha256"]
            runtime_sha256 = stack_identity_sha256(stack)
            frozen_model = unit.frozen.get("model_artifact_sha256")
            _require(frozen_model in (None, model_sha256),
                     f"{where}: the plan tree's frozen model pin {frozen_model} differs from the bundles' {model_sha256}")
            if local_artifact is not None:
                source_path = key["model"]["source"]
                if source_path not in local_checks:
                    digest = _artifact_digest(local_artifact(source_path))
                    _require(digest == model_sha256, f"{where}: the local model mirror {source_path} hashes to "
                                                     f"{digest}, the reference bundles recorded {model_sha256}")
                    local_checks[source_path] = digest
            scientific = [scientific_config_identity_sha256(config) for _path, config, _digest in unit.configs]
            units_out[unit.unit_id] = {
                "model_artifact_sha256": model_sha256,
                "runtime_identity_sha256": runtime_sha256,
                "config_set_sha256": identity_unit_config_set_sha256(scientific),
                "pack_id": unit.pack_id,
                "model_name": key["model"]["name"],
                "model_source": key["model"]["source"],
                "model_revision": key["model"]["revision"],
                "execution_path": "run_suite" if policy["stop_condition"] == SUITE_STOP_CONDITION else "run_workload",
                "output_policy": {name: policy[name] for name in OUTPUT_POLICY_KEYS},
                "config_count": len(unit.configs),
                "config_inventory_sha256": canonical_json_sha256(
                    [{"path": path, "sha256": digest} for path, _config, digest in unit.configs]),
                "frozen_projection_runtime_identity_sha256": unit.frozen.get("runtime_identity_sha256"),
                "reference_run_ids": sorted({reference.run_id for reference in matching}),
                "stack_identity": stack,
            }
    reference_rows = sorted(({"run_id": reference.run_id, "path": str(reference.path),
                              "model_name": reference.config.get("model", {}).get("name"),
                              "config_sha256": reference.config_sha256,
                              "metadata_sha256": reference.metadata_sha256,
                              "runtime_identity_sha256": stack_identity_sha256(reference.stack)}
                             for reference in used.values()), key=lambda row: (row["path"]))
    return {
        "schema": IDENTITY_PINS_SCHEMA,
        "status": STATUS_UNSEALED,
        "sealed": False,
        "note": ("UNSEALED DRAFT. Generated by scripts/write_b5_identity_pins.py from the three _v5 packs' "
                 "identity units, real block-3 reference bundles of the same models and the measurement "
                 "interpreter's package versions; no model was loaded. The seal replaces status and binds "
                 "this file's SHA-256 (registration 12)."),
        "units": dict(sorted(units_out.items())),
        "runtime_versions_sha256": runtime_versions_sha256(versions),
        "runtime_versions": versions,
        "derivation": {
            "model_artifact_sha256": "workload_provenance.model.artifact_identity recorded by every reference "
                                     "bundle of the unit's model (all must agree)",
            "runtime_identity_sha256": "identity_pins.stack_identity_sha256 of the reference bundles' stack "
                                       "identity with the unit's own output policy, the form the harvest "
                                       "recomputes per bundle (derive_model_runtime_config_from_metadata)",
            "runtime_versions_sha256": "flags.collect.runtime_versions_sha256(flags.collect.runtime_versions("
                                       "measurement interpreter))",
            "config_set_sha256": "identity_pins.identity_unit_config_set_sha256 of the unit's configs' "
                                 "scientific identities",
        },
        "sources": {
            "packs": pack_sources,
            "reference_bundles": reference_rows,
            "reference_bundles_skipped": skipped,
            "runtime_probe": {"python": runtime_python, **environment},
        },
    }


def render(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT, help="checkout holding the packs (default: this one)")
    parser.add_argument("--pack", action="append", default=None,
                        help="pack directory, relative to --repo (repeatable; default: the three _v5 packs)")
    parser.add_argument("--reference-root", action="append", type=Path, default=None,
                        help="directory of real bundles to take the runtime stack from (repeatable)")
    parser.add_argument("--runtime-python", default=DEFAULT_RUNTIME_PYTHON,
                        help="the measurement interpreter (package metadata and platform only)")
    parser.add_argument("--hash-local-models", action="store_true",
                        help="also hash each model's local mirror (read-only) and refuse on a difference")
    parser.add_argument("--out", type=Path, default=None, help=f"output (default: <repo>/{DEFAULT_OUTPUT})")
    parser.add_argument("--check", action="store_true", help="compare with the existing file instead of writing")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo = args.repo.resolve()
    packs = [repo / relative for relative in (args.pack or DEFAULT_PACKS)]
    roots = list(args.reference_root or [Path(root) for root in DEFAULT_REFERENCE_ROOTS])
    out = args.out or (repo / DEFAULT_OUTPUT)
    try:
        probe = probe_runtime(args.runtime_python)
        document = derive_document(repo_root=repo, packs=packs, reference_roots=roots, runtime_probe=probe,
                                   runtime_python=args.runtime_python,
                                   local_artifact=model_artifact_identity if args.hash_local_models else None)
    except Exception as exc:  # noqa: BLE001 - every refusal is reported the same way
        print(f"REFUSED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    raw = render(document)
    if args.check:
        current = out.read_bytes() if out.is_file() else None
        if current != raw:
            print(f"DIFFERS: {out} is not what the generator writes now", file=sys.stderr)
            return 1
        print(f"OK {out} sha256={sha256_bytes(raw)}")
        return 0
    _atomic_write(out, raw)
    summary = {unit: {key: value[key] for key in ("model_artifact_sha256", "runtime_identity_sha256",
                                                   "execution_path")}
               for unit, value in document["units"].items()}
    print(json.dumps({"path": str(out), "sha256": sha256_bytes(raw), "status": document["status"],
                      "runtime_versions_sha256": document["runtime_versions_sha256"], "units": summary},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
