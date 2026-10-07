"""Desk-time writer of one block-5 HAZARD_PACK window plan.

Input is one reviewed JSON object (schema ``joulewise.b5_window_plan_inputs.v2``),
never defaults for the registration's values: the thresholds are copied from
the sealed registration by whoever writes the inputs, and the two sizing
inputs (``programmed_span_s``, ``T_stream_max_s``) are sizing allowances read
from a committed sizing output in the measurement checkout. The writer:

1. reads the pack's committed ``plan_tree.json`` and walks its stage graph
   (``joulewise.b5.chain.stage_plan``); checks the thresholds against the
   hazard modules' contract (``joulewise.hazards.arm.default_thresholds``):
   every key a module reads must be present and numeric, so a missing key is
   refused here at the desk rather than raising at the real arm; the two sized
   keys (``disk.planned_bytes``, ``clock.t_stream_max_s``) are always the
   window's own values; every difference from the module defaults is recorded;
2. binds all fourteen launch bindings of ``arm_attachments.launch.bindings``,
   with ``ledger_path`` fixed to the measurement checkout's default ledger --
   the controller's pre-slot route reads
   ``<repo>/runs/calibration_observation_ledger.jsonl`` (controller.py:629), so
   a different ledger is refused here, at the desk (memo 1.18); and refuses a
   ledger whose physical head is not the committed pin (or whose pin is not
   committed, or that holds an open bracket session), because the chain's
   reservation would refuse it at exit 10 after the whole arm. The cure is
   the desk pin advance after each window's chain exits, before its harvest
   (:func:`advance_ledger_pin`, ``scripts/advance_b5_ledger_pin.py``;
   registration 11: chain exit, pin advance, harvest);
3. creates the claim and bound runs roots with an exclusive mkdir, so a
   leftover root from an earlier attempt can never be reused (memo 1.17);
4. writes ``window.env`` from the 25-key allowlist, the chain and its GNU
   sidecar, and a ``joulewise.night_plan.v5`` HAZARD_PACK plan carrying the
   ``hazard_window`` record the driver, the hazard modules and the lineage
   writer read.

It never arms, installs or launches anything. Every refusal happens before
the first write.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import os
import re
import shlex
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from joulewise import night_gate
from joulewise.b5 import chain as b5_chain

INPUT_SCHEMA = "joulewise.b5_window_plan_inputs.v2"
RECORD_SCHEMA = "joulewise.b5_window_plan_record.v1"
# Addendum E's T-0 stage cap. It holds the whole arm: census, instant reads,
# network time OFF, the record-only collectors, the ~40 s cadence probe, the
# 600-2700 s dwell and the final reads (gate-prune plan section 2.2).
T0_STAGE_CAP_S = 3300
DWELL_CAP_S = 2700
DEFAULT_LEDGER_RELATIVE = "runs/calibration_observation_ledger.jsonl"
HEAD_PIN_RELATIVE = "configs/calibration/calibration_ledger_head.json"
PLAN_BASENAME = "night_plan.json"
CHAIN_BASENAME = "chain.zsh"
WINDOW_ENV_BASENAME = "window.env"
RECORD_BASENAME = "b5-window-plan-record.json"
POWER_POLICY = "ac_high_power"
# Threshold keys whose value is the window's own sizing, never a copied value.
SIZED_THRESHOLD_KEYS = (("disk", "planned_bytes"), ("clock", "t_stream_max_s"))
THRESHOLD_CONTRACT_SOURCE = "joulewise.hazards.arm.default_thresholds"

_INPUT_KEYS = {
    "schema", "plan_id", "attempt", "pack_root", "measurement_root", "measurement_head",
    "repo_head", "custody_root", "runs_parent", "claim_backup_destination",
    "bound_backup_destination", "bracket_session_id", "pre_attempt_id", "post_attempt_id",
    "identity_epoch_json", "t1_bindings_json", "t0_epoch_s", "programmed_span_s",
    "T_stream_max_s", "bytes_per_member", "thresholds", "g10", "registration",
}
_OPTIONAL_INPUT_KEYS = {"ledger_path"}
# The 25-key window environment allowlist (the exact key set of the T-0
# window.env contract, copied so this module stays off the retired arm path).
WINDOW_ENV_KEYS = (
    "MEASUREMENT_REPO", "WINDOW_ID", "BRACKET_SESSION_ID", "FROZEN_PLAN", "PACK_ROOT",
    "PACK_ID", "PLAN_ID", "EVIDENCE_ROOT_ID", "IDENTITY_EPOCH_JSON", "T1_BINDINGS_JSON",
    "PRE_ATTEMPT_ID", "POST_ATTEMPT_ID", "RUNS_ROOT", "BOUND_RUNS_ROOT", "CALIBRATION_LEDGER",
    "LEDGER_HEAD_PIN", "ARM_READINESS_CUSTODY_ROOT", "CUSTODY_ROOT", "WINDOW_CUSTODY_ROOT",
    "QUARANTINE_ROOT", "CLAIM_BACKUP_DEST", "BOUND_BACKUP_DEST", "WAIVER_PATH", "POWER_POLICY",
    "SETTLE_S",
)
_BINDING_TYPES = {
    "repo_root": {"existing_absolute_directory"},
    "ledger_path": {"existing_absolute_file"},
    "claim_runs_root": {"fresh_absolute_directory", "fresh_absolute_directory_with_declared_leaf"},
    "bound_runs_root": {"fresh_absolute_directory", "fresh_absolute_directory_with_declared_leaf"},
    "operator_log_root": {"absolute_directory"},
    "pre_calibration_dir": {"absolute_directory"},
    "post_calibration_dir": {"absolute_directory"},
    "claim_backup_destination": {"absolute_path"},
    "bound_backup_destination": {"absolute_path"},
    "bracket_session_id": {"nonempty_string", "non_path_string"},
    "pre_attempt_id": {"nonempty_string", "non_path_string"},
    "post_attempt_id": {"nonempty_string", "non_path_string"},
    "identity_epoch_json": {"authenticated_absolute_file"},
    "t1_bindings_json": {"authenticated_absolute_file"},
}
_DERIVED_PATH_RULES = [
    "pre_calibration_dir=claim_runs_root/instrument_validation/pre_attempt_id",
    "post_calibration_dir=claim_runs_root/instrument_validation/post_attempt_id",
]
_IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_HEAD_RE = re.compile(r"[0-9a-f]{40}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class WindowPlanError(ValueError):
    """The inputs or the pack cannot produce a window plan; nothing was written."""


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise WindowPlanError(detail)


# ---------------------------------------------------------------------------
# Interface J3 (gate-prune 2, PLAN2 3.2 and section 2.1 row 14): the stage
# dispatch resolver. What a collection stage launches is decided by its own
# argv, not by the plan tree's ``input_ref`` (null on the floor packs): the
# campaign runner's first argument is a config directory whose
# ``order_manifest.json`` lists the members in order, and ``--runs-dir`` names
# the runs root. One run id names one bundle directory per runs root, and the
# runner skips a run id whose complete bundle already exists, so a (runs root,
# run id) pair two stages launch is measured once and its later planned
# positions never are. The desk refuses such a plan (WindowPlanError), the CI
# lint (scripts/check_b5_chain.py) reports it for every committed pack, and the
# harvest and driver read the same resolver.
# ---------------------------------------------------------------------------

DISPATCH_SCHEMA = "joulewise.b5_stage_dispatch.v1"


@dataclasses.dataclass(frozen=True)
class StageDispatch:
    """One collection stage: its runs root and the bundle directories it launches, in order."""

    stage_id: str
    ordinal: int | None
    runs_root_binding: str | None
    runs_root: str | None  # the bound path when bindings were given
    config_dir: str | None  # repository-relative
    order_manifest_sha256: str | None
    run_ids: tuple[str, ...] | None  # sanitized as the runner names bundle directories
    error: str | None

    def record(self) -> dict[str, Any]:
        return {"stage_id": self.stage_id, "ordinal": self.ordinal, "runs_root_binding": self.runs_root_binding,
                "runs_root": self.runs_root, "config_dir": self.config_dir,
                "order_manifest_sha256": self.order_manifest_sha256,
                "run_ids": list(self.run_ids) if self.run_ids is not None else None, "error": self.error}


def _dispatch_of(row: Any, repo_root: Path, bindings: Mapping[str, str] | None) -> StageDispatch:
    stage_id = str(row.get("stage_id")) if isinstance(row, Mapping) else "?"
    ordinal = row.get("ordinal") if isinstance(row, Mapping) and type(row.get("ordinal")) is int else None
    binding: str | None = None
    config: str | None = None

    def failed(detail: str, digest: str | None = None) -> StageDispatch:
        bound = bindings.get(binding) if bindings is not None and binding is not None else None
        return StageDispatch(stage_id, ordinal, binding, bound, config, digest, None, detail)

    try:
        commands = row["launch"]["commands"]
        arguments = commands[0]["argv_template"]["arguments"]
        _require(isinstance(commands, list) and len(commands) == 1 and isinstance(arguments, list),
                 "launch has not exactly one command")
    except (KeyError, IndexError, TypeError, WindowPlanError):
        return failed("the collection stage has no single campaign command")
    for flag, value in zip(arguments, arguments[1:]):
        if isinstance(flag, Mapping) and flag.get("kind") == "literal" and flag.get("value") == "--runs-dir" \
                and isinstance(value, Mapping) and value.get("kind") == "binding" \
                and isinstance(value.get("value"), str):
            if binding is not None:
                return failed("--runs-dir appears more than once")
            binding = value["value"]
    first = arguments[0] if arguments else None
    if not (isinstance(first, Mapping) and first.get("kind") == "repo_path" and isinstance(first.get("value"), str)
            and first["value"] and not Path(first["value"]).is_absolute() and ".." not in Path(first["value"]).parts):
        return failed("the campaign command's first argument is not a repository-relative config directory")
    config = first["value"]
    if binding is None:
        return failed("the campaign command names no --runs-dir binding")
    if bindings is not None and not isinstance(bindings.get(binding), str):
        return failed(f"--runs-dir binding {binding} is not bound")
    path = Path(repo_root) / config / "order_manifest.json"
    try:
        raw = path.read_bytes()
        manifest = json.loads(raw)
    except (OSError, ValueError) as exc:
        return failed(f"order manifest {config}/order_manifest.json is unreadable: {type(exc).__name__}")
    order = manifest.get("executed_order") if isinstance(manifest, Mapping) else None
    if not isinstance(order, list) or not all(isinstance(entry, Mapping) and isinstance(entry.get("run_id"), str)
                                              and entry["run_id"] for entry in order):
        return failed("order manifest executed_order does not list a run_id for every member", _sha256(raw))
    from joulewise.bundle import BundleError, sanitize_id_component  # the runner's bundle-directory rule

    try:
        run_ids = tuple(sanitize_id_component(entry["run_id"]) for entry in order)
    except BundleError as exc:
        return failed(f"a run id sanitizes to nothing: {exc}", _sha256(raw))
    return StageDispatch(stage_id, ordinal, binding, bindings.get(binding) if bindings is not None else None,
                         config, _sha256(raw), run_ids, None)


def resolve_stage_dispatches(tree: Mapping[str, Any], repo_root: Path | str, *,
                             bindings: Mapping[str, str] | None = None) -> list[StageDispatch]:
    """Every ``campaign_collection`` stage of the plan tree, in ordinal order, resolved from its own argv.

    ``repo_root`` is the checkout the stage's config directory is relative to
    (the measurement checkout, or the harvest's preserved copy). With
    ``bindings`` each runs root is also given as a path. Never raises on a
    malformed stage: its ``error`` says what could not be read and its
    ``run_ids`` is None (unresolved).
    """

    graph = tree.get("stage_graph") if isinstance(tree, Mapping) else None
    rows = [row for row in graph if isinstance(row, Mapping) and row.get("kind") == "campaign_collection"] \
        if isinstance(graph, list) else []
    rows.sort(key=lambda row: row.get("ordinal") if type(row.get("ordinal")) is int else 1 << 30)
    return [_dispatch_of(row, Path(repo_root), bindings) for row in rows]


def duplicate_dispatches(dispatches: Sequence[StageDispatch]) -> list[dict[str, Any]]:
    """Each (runs root, run id) pair launched more than once, with the stages that launch it, in order."""

    seen: dict[tuple[str | None, str], list[str]] = {}
    for dispatch in dispatches:
        for run_id in dispatch.run_ids or ():
            seen.setdefault((dispatch.runs_root_binding, run_id), []).append(dispatch.stage_id)
    return [{"runs_root_binding": root, "run_id": run_id, "stages": stages}
            for (root, run_id), stages in seen.items() if len(stages) > 1]


def dispatch_refusal(dispatches: Sequence[StageDispatch]) -> str | None:
    """The desk refusal for a stage graph the chain cannot collect as planned, or None."""

    unresolved = [f"{dispatch.stage_id} ({dispatch.error})" for dispatch in dispatches if dispatch.run_ids is None]
    if unresolved:
        return "collection stages whose members cannot be resolved from their own argv: " + "; ".join(unresolved)
    duplicates = duplicate_dispatches(dispatches)
    if duplicates:
        return ("run ids launched more than once into one runs root (the runner measures each once, so every later "
                "planned position is never measured and the harvest excludes the window as roster.duplicate_run_id): "
                + "; ".join(f"{row['run_id']} into {row['runs_root_binding']} by {', '.join(row['stages'])}"
                            for row in duplicates))
    return None


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _absolute(value: Any, field: str) -> Path:
    _require(isinstance(value, str) and value and os.path.isabs(value)
             and not any(c in value for c in "\0\n\r"), f"{field} must be an absolute path")
    path = Path(value)
    _require(".." not in path.parts, f"{field} must not contain '..'")
    return path


def _identifier(value: Any, field: str) -> str:
    _require(isinstance(value, str) and _IDENTIFIER_RE.fullmatch(value) is not None,
             f"{field} must match [A-Za-z0-9][A-Za-z0-9._-]*")
    return value


def _number(value: Any, field: str, *, integer: bool = False) -> float | int:
    ok = (not isinstance(value, bool) and isinstance(value, int if integer else (int, float))
          and math.isfinite(value) and value > 0)
    _require(ok, f"{field} must be a positive {'integer' if integer else 'number'}")
    return value


def _locator(value: Any, field: str, *, base: Path | None = None) -> tuple[Path, str]:
    _require(isinstance(value, Mapping) and set(value) == {"path", "sha256"},
             f"{field} must be a {{path, sha256}} locator")
    path_text = value["path"]
    _require(isinstance(path_text, str) and path_text, f"{field}.path must be a non-empty string")
    path = Path(path_text)
    if not path.is_absolute():
        _require(base is not None and ".." not in path.parts, f"{field}.path must be absolute")
        path = base / path
    _require(isinstance(value["sha256"], str) and _SHA256_RE.fullmatch(value["sha256"]) is not None,
             f"{field}.sha256 must be a SHA-256 digest")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise WindowPlanError(f"{field}.path is unreadable: {exc}") from exc
    _require(_sha256(raw) == value["sha256"], f"{field}: sha256 does not match the file")
    return path, value["sha256"]


def read_plan_tree(pack_root: Path) -> tuple[dict[str, Any], str]:
    path = Path(pack_root) / "plan_tree.json"
    try:
        raw = path.read_bytes()
        tree = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise WindowPlanError(f"plan_tree.json is unreadable: {exc}") from exc
    _require(isinstance(tree, dict), "plan_tree.json must be an object")
    return tree, _sha256(raw)


def hazard_threshold_defaults() -> dict[str, dict[str, Any]]:
    """The hazard modules' threshold contract: every key each module reads, with its default.

    Lane L1's ``joulewise.hazards.arm.default_thresholds``. Imported at call
    time from the checkout the driver runs, which is the code that will read
    the thresholds at the real arm.
    """

    from joulewise.hazards.arm import default_thresholds
    return default_thresholds()


def _is_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def audit_thresholds(thresholds: Mapping[str, Any], defaults: Mapping[str, Any], *,
                     sized: Mapping[tuple[str, str], Any]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Check copied thresholds against the modules' contract; return (thresholds, audit).

    Refuses when a module lacks a key its defaults carry, or a value is not a
    finite number: the module's judge would raise on it at the real arm, which
    the driver reads as a NULL window. A key whose default is null is an
    optional limit that the module judges only when registered (L1's
    ``contention.aggregate_cpu_limit_s_per_s``): it may be absent, and when
    present it must be null or a positive finite number, the module's own rule
    (``contention.aggregate_limit``). The sized keys are replaced by the
    window's own values. The audit records every value that differs from the
    module default, every key the contract does not know, every optional key
    left out, and every copied sized value that was replaced.
    """

    _require(isinstance(defaults, Mapping) and set(defaults) == set(night_gate.HAZARD_MODULES)
             and all(isinstance(defaults[name], Mapping) for name in night_gate.HAZARD_MODULES),
             f"the threshold contract ({THRESHOLD_CONTRACT_SOURCE}) must name the six hazard modules")
    missing, not_numeric = [], []
    differences, unknown, replaced, optional_absent = [], [], [], []
    result: dict[str, dict[str, Any]] = {}
    for module in night_gate.HAZARD_MODULES:
        copied, contract = thresholds[module], defaults[module]
        values = json.loads(json.dumps(copied))
        for key, default in contract.items():
            if (module, key) in sized:
                continue
            if default is None:
                if key not in values:
                    optional_absent.append(f"{module}.{key}")
                    continue
                if values[key] is not None and not (_is_number(values[key]) and values[key] > 0):
                    not_numeric.append(f"{module}.{key}")
                elif values[key] is not None:
                    differences.append({"key": f"{module}.{key}", "value": values[key], "default": None})
            elif key not in values:
                missing.append(f"{module}.{key}")
            elif _is_number(default) and not _is_number(values[key]):
                not_numeric.append(f"{module}.{key}")
            elif values[key] != default:
                differences.append({"key": f"{module}.{key}", "value": values[key], "default": default})
        unknown += [f"{module}.{key}" for key in values if key not in contract]
        for (sized_module, key), value in sized.items():
            if sized_module != module:
                continue
            if key in values and values[key] != value:
                replaced.append({"key": f"{module}.{key}", "copied": values[key], "window": value})
            values[key] = value
        result[module] = values
    _require(not missing, "thresholds lack keys the hazard modules read (copy them from the sealed "
             f"registration): {', '.join(missing)}")
    _require(not not_numeric, "thresholds must be finite numbers (an optional limit: null or a positive "
             f"finite number): {', '.join(not_numeric)}")
    audit = {"contract": THRESHOLD_CONTRACT_SOURCE, "differences_from_defaults": differences,
             "keys_not_in_contract": unknown, "optional_keys_absent": optional_absent,
             "sized_keys_replaced": replaced,
             "sized_keys": [f"{module}.{key}" for module, key in sized]}
    return result, audit


def read_allowance(value: Any, field: str, *, measurement: Path) -> tuple[float | int, dict[str, Any]]:
    """One sizing allowance, ``{seconds, source: {path, sha256}, source_pointer}``.

    The form of block 4's committed sizing adapter
    (``configs/campaigns/v5_qualification_25g83/sizing_allowances.json``), so a
    total from a committed sizing output is pasted verbatim. The source is a
    file in the measurement checkout (a path relative to it); its bytes must
    hash to ``source.sha256`` and the JSON pointer must resolve to exactly
    ``seconds``.
    """

    _require(isinstance(value, Mapping) and set(value) == {"seconds", "source", "source_pointer"},
             f"{field} must be a sizing allowance {{seconds, source, source_pointer}} from a committed "
             "sizing output, not a free number")
    seconds = value["seconds"]
    _require(_is_number(seconds) and seconds > 0, f"{field}.seconds must be a positive number")
    source, pointer = value["source"], value["source_pointer"]
    _require(isinstance(source, Mapping) and isinstance(source.get("path"), str) and source["path"]
             and not os.path.isabs(source["path"]),
             f"{field}.source.path must be relative to the measurement checkout")
    path, digest = _locator(source, f"{field}.source", base=measurement)
    try:
        node: Any = json.loads(path.read_bytes())
    except (OSError, ValueError) as exc:
        raise WindowPlanError(f"{field}.source is not readable JSON: {exc}") from exc
    _require(isinstance(pointer, str) and pointer.startswith("/"), f"{field}.source_pointer must start with /")
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        elif isinstance(node, Mapping) and part in node:
            node = node[part]
        else:
            raise WindowPlanError(f"{field}.source_pointer {pointer!r} does not resolve")
    _require(_is_number(node) and node == seconds,
             f"{field}.seconds ({seconds!r}) is not the value at {pointer} in the source ({node!r})")
    return seconds, {"seconds": seconds, "source": {"path": source["path"], "sha256": digest},
                     "source_pointer": pointer}


def declared_bindings(tree: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """The pack's launch bindings; they must be exactly the fourteen v5 bindings.

    Two committed shapes exist: the floor packs list ``bindings`` rows with
    ``derived_path_rules``; the contrast pack carries ``closed_bindings`` with a
    ``calibration_directory_relation``. Both declare the same fourteen names,
    the same binding types (two spellings of each) and the same two
    calibration directories under the claim runs root.
    """

    launch = (tree.get("arm_attachments") or {}).get("launch") if isinstance(tree, Mapping) else None
    _require(isinstance(launch, Mapping) and launch.get("schema_version") == "joulewise.stage_launch_bindings.v1",
             "plan tree arm_attachments.launch must be joulewise.stage_launch_bindings.v1")
    declared: dict[str, dict[str, Any]] = {}
    if "bindings" in launch:
        rows = launch.get("bindings")
        _require(isinstance(rows, list), "launch bindings must be a list")
        for row in rows:
            _require(isinstance(row, Mapping) and isinstance(row.get("name"), str), "malformed launch binding")
            _require(row["name"] not in declared, f"launch binding {row['name']} is declared twice")
            declared[row["name"]] = dict(row)
        _require(launch.get("derived_path_rules") == _DERIVED_PATH_RULES,
                 "the pack's derived path rules are not the two v5 calibration rules")
    else:
        closed = launch.get("closed_bindings")
        _require(isinstance(closed, Mapping), "launch must carry bindings or closed_bindings")
        declared = {name: {"name": name, "type": kind} for name, kind in closed.items()}
        _require(launch.get("calibration_directory_relation") == {
            "pre": "claim_runs_root/instrument_validation/pre_attempt_id",
            "post": "claim_runs_root/instrument_validation/post_attempt_id"},
            "the pack's calibration directory relation is not the v5 relation")
    _require(set(declared) == set(night_gate.HAZARD_LAUNCH_BINDINGS),
             "the pack must declare exactly the fourteen v5 launch bindings")
    for name, kinds in _BINDING_TYPES.items():
        _require(declared[name].get("type") in kinds, f"launch binding {name} must have a type in {sorted(kinds)}")
    return declared


def _inside(child: Path, parent: Path) -> bool:
    return child == parent or parent in child.parents


def _create_once(path: Path, raw: bytes, mode: int = 0o600) -> dict[str, str]:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {"path": str(path), "sha256": _sha256(raw)}


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def window_env_bytes(values: Mapping[str, str]) -> bytes:
    _require(tuple(values) == WINDOW_ENV_KEYS, "window.env must carry exactly the allowlisted keys in order")
    lines = ["# HAZARD_PACK window environment (joulewise/b5/plan.py); literal values only."]
    for key, value in values.items():
        _require(isinstance(value, str) and value and "$" not in value
                 and not any(c in value for c in "\0\n\r"), f"window.env {key} must be a single literal word")
        lines.append(f"{key}={shlex.quote(value)}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def _validate_inputs(inputs: Mapping[str, Any]) -> None:
    _require(isinstance(inputs, Mapping), "inputs must be an object")
    keys = set(inputs)
    missing, extra = _INPUT_KEYS - keys, keys - _INPUT_KEYS - _OPTIONAL_INPUT_KEYS
    _require(not missing and not extra, f"input keys are not exact (missing={sorted(missing)}, extra={sorted(extra)})")
    _require(inputs["schema"] == INPUT_SCHEMA, f"inputs schema must be {INPUT_SCHEMA}")
    for name in ("plan_id", "bracket_session_id", "pre_attempt_id", "post_attempt_id"):
        _identifier(inputs[name], name)
    _require(len({inputs["pre_attempt_id"], inputs["post_attempt_id"]}) == 2, "pre and post attempt ids must differ")
    _require(type(inputs["attempt"]) is int and inputs["attempt"] >= 1, "attempt must be an integer >= 1")
    for name in ("measurement_head", "repo_head"):
        _require(isinstance(inputs[name], str) and _HEAD_RE.fullmatch(inputs[name]) is not None,
                 f"{name} must be 40 lowercase hexadecimal characters")
    t0 = inputs["t0_epoch_s"]
    _require(not isinstance(t0, bool) and isinstance(t0, (int, float)) and math.isfinite(t0) and t0 > 0
             and float(t0) % 60 == 0, "t0_epoch_s must be a positive whole-minute epoch")
    # programmed_span_s and T_stream_max_s are sizing allowances, read against
    # their committed source once the measurement checkout is known.
    _number(inputs["bytes_per_member"], "bytes_per_member", integer=True)
    _require(type(inputs["g10"]) is bool, "g10 must be a boolean")
    thresholds = inputs["thresholds"]
    _require(isinstance(thresholds, Mapping) and set(thresholds) == set(night_gate.HAZARD_MODULES)
             and all(isinstance(thresholds[name], Mapping) for name in night_gate.HAZARD_MODULES),
             "thresholds must give an object for each of the six hazard modules (copied from the registration)")


# Ledger states the chain's bracket reservation refuses at open
# (calibration_ledger.append_bracket_session_receipt and the reservation
# script's pre-reserve readiness): the physical head is not the committed pin,
# the pin is not committed, the ledger or pin is unreadable, or an earlier
# bracket session is still open.
LEDGER_HEAD_BLOCKING_REASONS = frozenset({
    "calibration_ledger_head_mismatch", "calibration_ledger_rollback", "calibration_ledger_head_uncommitted",
    "calibration_ledger_malformed", "calibration_ledger_missing", "calibration_ledger_bracket_session_open",
})
PIN_ADVANCE_SCRIPT = "scripts/advance_b5_ledger_pin.py"
PIN_ADVANCE_SCHEMA = "joulewise.b5_ledger_pin_advance.v1"


class PinAdvanceError(ValueError):
    """The desk pin advance could not run; the pin and the checkout are unchanged unless stated."""


def _refusal_text(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    return str(getattr(code, "value", None) or exc)


def ledger_head_status(measurement: Path) -> dict[str, Any]:
    """Read-only: the measurement checkout's calibration ledger head against its committed pin.

    The same snapshot the reservation authenticates
    (``calibration_ledger.load_calibration_ledger_snapshot`` with the pin
    required to be committed at the checkout's HEAD); custody is not read.
    ``blocking`` lists the reasons the chain's reservation would refuse.
    """

    from joulewise.calibration_ledger import load_calibration_ledger_snapshot

    ledger, pin = Path(measurement) / DEFAULT_LEDGER_RELATIVE, Path(measurement) / HEAD_PIN_RELATIVE
    try:
        snapshot = load_calibration_ledger_snapshot(
            ledger, pin, require_committed_pin=True, verify_custody=False, mode="read_replay",
            repo_root=Path(measurement))
    except Exception as exc:  # noqa: BLE001 - a ledger the snapshot cannot read is not reservable
        return {"physical": None, "pinned": None, "open_sessions": [],
                "reasons": [f"snapshot_failed:{type(exc).__name__}"],
                "blocking": [f"snapshot_failed:{type(exc).__name__}"]}
    reasons = sorted({str(getattr(reason, "value", reason)) for reason in snapshot.refusal_reasons})
    open_sessions = sorted(session.session_id for session in snapshot.bracket_sessions
                           if session.state == "open")
    return {
        "physical": {"sequence": snapshot.head_sequence, "head_digest": snapshot.head_digest},
        "pinned": {"sequence": snapshot.committed_head_sequence, "head_digest": snapshot.committed_head_digest},
        "open_sessions": open_sessions,
        "open_session_next_slots": {session_id: _open_session_next_slot(ledger, pin, session_id, measurement)
                                    for session_id in open_sessions},
        "reasons": reasons,
        "blocking": sorted(set(reasons) & LEDGER_HEAD_BLOCKING_REASONS),
    }


def _open_session_next_slot(ledger: Path, pin: Path, session_id: str, measurement: Path) -> dict[str, Any]:
    """Read-only: an open bracket session's next slot and the custody state there.

    ``custody_state`` ``complete`` means the slot's capture custody is whole
    but was never finalized into the ledger (the chain stopped between the
    capture and its finalize): ``abort-session`` refuses that with
    ``calibration_custody_complete_use_resume`` and the cure is
    ``resume-finalize`` (rehearsal round 3, R3-6).  A status that cannot be
    read is recorded with its error and the refusal names the abort, as before.
    """

    from joulewise.calibration_ledger import calibration_session_status

    try:
        status = calibration_session_status(
            ledger, pin, session_id=session_id, require_committed_pin=True, repo_root=Path(measurement),
            custody_mode="read_replay", custody_state_scope="next_slot")
    except Exception as exc:  # noqa: BLE001 - the desk refusal still names a cure
        return {"next_slot": None, "custody_state": None, "error": f"{type(exc).__name__}: {exc}"}
    next_slot = status.get("next_slot")
    slot = (status.get("slots") or {}).get(next_slot) or {}
    return {"next_slot": next_slot, "custody_state": slot.get("custody_state"),
            "refusal_code": status.get("refusal_code"), "error": None}


def ledger_head_refusal(status: Mapping[str, Any], measurement: Path) -> str:
    """The desk refusal for a ledger the reservation would refuse, naming the step that cures it."""

    physical, pinned = status.get("physical") or {}, status.get("pinned") or {}
    # The desk order is chain exit, pin advance, harvest (registration 11), so
    # the advance reads the session's terminal head from the ledger and needs
    # no harvest archive; a window that stopped before its post-calibration
    # has none to offer either (its harvest writes no derived/terminal-pin.json).
    cure = (f"run the desk pin advance for the last window that ran: python {PIN_ADVANCE_SCRIPT} --plan "
            "<that window's night_plan.json> --operator-identity <id>, which reads its bracket session's "
            "terminal head from the ledger (recover_calibration_ledger.py advance-head-pin --session-id "
            "<its bracket session> --expected-sequence/--expected-digest <terminal pin> --execute, then a "
            f"pin-only commit of {HEAD_PIN_RELATIVE}, registration section 11 item 1(i)), before that "
            "window's harvest")
    if "calibration_ledger_bracket_session_open" in status.get("blocking", ()):
        slots = status.get("open_session_next_slots") or {}
        complete = {session_id: entry["next_slot"] for session_id, entry in sorted(slots.items())
                    if isinstance(entry, Mapping) and entry.get("custody_state") == "complete"}
        if complete:
            # R3-6: the capture's custody is whole but was never finalized;
            # abort-session refuses it (calibration_custody_complete_use_resume).
            named = "; ".join(f"recover_calibration_ledger.py resume-finalize --session-id {session_id} "
                              f"--slot {slot} --plan <that window's frozen reservation plan>"
                              for session_id, slot in complete.items())
            cure = ("finalize the open bracket session's complete capture custody first (" + named + "; "
                    "abort-session refuses complete custody with calibration_custody_complete_use_resume); "
                    "if the session is still open after that, abort it (recover_calibration_ledger.py "
                    "abort-session), then " + cure)
        else:
            cure = ("abort the open bracket session first (recover_calibration_ledger.py abort-session; a chain "
                    "that stopped before its post-calibration leaves it open), then " + cure)
    return (f"the measurement checkout's calibration ledger cannot be reserved: {', '.join(status['blocking'])} "
            f"(physical head sequence {physical.get('sequence')}, committed pin sequence "
            f"{pinned.get('sequence')}, checkout {measurement}); the chain's reservation would refuse it at "
            f"exit 10 after the arm. To cure it, {cure}")


def advance_ledger_pin(measurement: Path | str, *, session_id: str, operator_identity: str,
                       attestation_reason: str, expected_pin: Mapping[str, Any] | None = None,
                       commit: bool = True, git: str = "git") -> dict[str, Any]:
    """The desk step between a window's chain exit and its harvest: advance and commit the ledger pin.

    The window's post-calibration (or an abort of its bracket session) moved
    the ledger past the committed pin.  The harvest's desk verdict reads the
    ledger through the committed pin, and so does the next window's
    reservation, so the advance comes first (registration 11: chain exit, pin
    advance, harvest).

    1. The terminal head of ``session_id`` (the window's bracket session) is
       read from the measurement checkout's ledger
       (``calibration_ledger.terminal_head_pin_for_session``); when an
       ``expected_pin`` is given (an earlier harvest's
       ``derived/terminal-pin.json``), the two must agree.
    2. ``calibration_ledger.advance_calibration_head_pin`` (the guarded
       ``recover_calibration_ledger.py advance-head-pin`` path) writes the pin.
    3. A pin-only commit of ``configs/calibration/calibration_ledger_head.json``
       in the measurement checkout (registration 11 item 1(i)); the commit is
       checked to change that path alone.

    Already exact and committed: nothing changes (``status`` ``NOT_NEEDED``).
    Raises :class:`PinAdvanceError` on any refusal.
    """

    import subprocess

    from joulewise.calibration_exits import RefusalCode
    from joulewise.calibration_ledger import (
        CalibrationLedgerError, advance_calibration_head_pin, terminal_head_pin_for_session)

    measurement = Path(measurement)
    ledger, pin = measurement / DEFAULT_LEDGER_RELATIVE, measurement / HEAD_PIN_RELATIVE
    before = ledger_head_status(measurement)
    record: dict[str, Any] = {"schema": PIN_ADVANCE_SCHEMA, "measurement_root": str(measurement),
                              "session_id": session_id, "before": before, "advanced": None, "commit": None}
    if not before["blocking"]:
        return {**record, "status": "NOT_NEEDED", "after": before}
    if set(before["blocking"]) - {"calibration_ledger_head_mismatch", "calibration_ledger_head_uncommitted"}:
        raise PinAdvanceError(f"the ledger is not in a pin-advance state: {', '.join(before['blocking'])}")

    def run_git(*arguments: str) -> str:
        completed = subprocess.run([git, "-C", str(measurement), *arguments], capture_output=True, text=True,
                                   check=False, timeout=60)
        if completed.returncode != 0:
            raise PinAdvanceError(f"git {' '.join(arguments[:2])} failed: {completed.stderr.strip()[:300]}")
        return completed.stdout

    try:
        candidate = terminal_head_pin_for_session(ledger, session_id=session_id)
    except CalibrationLedgerError as exc:
        raise PinAdvanceError(f"no terminal head for session {session_id}: {_refusal_text(exc)}") from exc
    if expected_pin is not None and (candidate.get("sequence"), candidate.get("head_digest")) != (
            expected_pin.get("sequence"), expected_pin.get("head_digest")):
        raise PinAdvanceError(f"the ledger's terminal head for {session_id} (sequence {candidate.get('sequence')}) "
                              f"is not the harvested terminal pin (sequence {expected_pin.get('sequence')})")
    if "calibration_ledger_head_mismatch" in before["blocking"]:
        try:
            advanced = advance_calibration_head_pin(
                ledger, pin, session_id=session_id, expected_sequence=int(candidate["sequence"]),
                expected_digest=str(candidate["head_digest"]), operator_identity=operator_identity,
                attestation_reason=attestation_reason, execute=True, require_committed_pin=True,
                repo_root=measurement)
        except CalibrationLedgerError as exc:
            if exc.code != RefusalCode.PIN_ADVANCEMENT_NOT_NEEDED:
                raise PinAdvanceError(f"advance-head-pin refused: {_refusal_text(exc)}") from exc
            advanced = None
        record["advanced"] = dict(advanced) if advanced is not None else None
    if commit:
        if run_git("status", "--porcelain", "--", HEAD_PIN_RELATIVE).strip():
            message = (f"Pin-only: calibration ledger head at sequence {candidate['sequence']} "
                       f"(bracket session {session_id})\n\nRegistration section 11 item 1(i): this commit "
                       f"changes only {HEAD_PIN_RELATIVE}.\n")
            run_git("commit", "--only", "-m", message, "--", HEAD_PIN_RELATIVE)
            changed = [line for line in run_git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
                       .splitlines() if line.strip()]
            if changed != [HEAD_PIN_RELATIVE]:
                raise PinAdvanceError(f"the pin commit is not pin-only: {changed}")
            record["commit"] = {"head": run_git("rev-parse", "HEAD").strip(), "changed_paths": changed}
    after = ledger_head_status(measurement)
    record["after"] = after
    if commit and after["blocking"]:
        raise PinAdvanceError(f"the ledger still cannot be reserved after the advance: {', '.join(after['blocking'])}")
    return {**record, "status": "ADVANCED" if commit else "ADVANCED_UNCOMMITTED"}


def write_window_plan(inputs: Mapping[str, Any], *, settle_s: int | float = b5_chain.SETTLE_S,
                      now: Callable[[], float] = time.time,
                      pack_digest: Callable[[Path], str] | None = None,
                      threshold_defaults: Callable[[], Mapping[str, Any]] | None = None,
                      horizon_s: int = b5_chain.CALIBRATION_HORIZON_S) -> dict[str, Any]:
    """Validate everything, then create the window's custody once; return the record.

    ``settle_s`` and ``horizon_s`` are keywords for the mock-runtime render
    only; the command line always renders the registered 60 s
    (``chain.SETTLE_S``) and the 24 h calibration horizon
    (``chain.CALIBRATION_HORIZON_S``). ``threshold_defaults`` returns the
    hazard modules' threshold contract (default:
    :func:`hazard_threshold_defaults`). A stage graph whose collection stages
    launch a (runs root, run id) pair twice, or whose members cannot be
    resolved from a stage's own argv (interface J3), is refused here.
    """

    _validate_inputs(inputs)
    measurement = _absolute(inputs["measurement_root"], "measurement_root")
    _require(measurement.is_dir(), "measurement_root must be an existing directory")
    pack_root = _absolute(inputs["pack_root"], "pack_root")
    _require(_inside(pack_root, measurement / "configs/campaigns") and pack_root.parent == measurement / "configs/campaigns",
             "pack_root must be a pack directory under <measurement_root>/configs/campaigns")
    _require(pack_root.is_dir(), "pack_root must be an existing directory")
    custody = _absolute(inputs["custody_root"], "custody_root")
    _require(not custody.exists() or (custody.is_dir() and not any(custody.iterdir())),
             "custody_root must be absent or an empty directory")
    _require(custody.parent.is_dir(), "custody_root's parent must exist")
    runs_parent = _absolute(inputs["runs_parent"], "runs_parent")
    _require(runs_parent.is_dir(), "runs_parent must be an existing directory")

    tree, tree_sha256 = read_plan_tree(pack_root)
    declared = declared_bindings(tree)
    try:
        stages = b5_chain.stage_plan(tree)
    except b5_chain.ChainRenderError as exc:
        raise WindowPlanError(f"stage graph: {exc}") from exc
    members = sum(stage.expected_count for stage in stages
                  if stage.in_chain and stage.kind == "campaign_collection")
    dispatches = resolve_stage_dispatches(tree, measurement)
    refusal = dispatch_refusal(dispatches)
    _require(refusal is None, f"stage dispatch: {refusal}")
    planned_bytes = inputs["bytes_per_member"] * members
    span_seconds, span_allowance = read_allowance(inputs["programmed_span_s"], "programmed_span_s",
                                                  measurement=measurement)
    programmed_span_s = math.ceil(span_seconds)
    t_stream_max_s, stream_allowance = read_allowance(inputs["T_stream_max_s"], "T_stream_max_s",
                                                      measurement=measurement)
    try:
        defaults = (threshold_defaults or hazard_threshold_defaults)()
    except Exception as exc:  # noqa: BLE001 - without the contract the thresholds cannot be checked
        raise WindowPlanError(f"the hazard modules' threshold contract ({THRESHOLD_CONTRACT_SOURCE}) "
                              f"is unavailable: {type(exc).__name__}: {exc}") from exc
    thresholds, thresholds_audit = audit_thresholds(
        inputs["thresholds"], defaults, sized=dict(zip(SIZED_THRESHOLD_KEYS, (planned_bytes, t_stream_max_s))))
    roots = tree.get("roots") or {}
    claim_leaf, bound_leaf = roots.get("claim_root_leaf"), roots.get("bound_root_leaf")
    _require(isinstance(claim_leaf, str) and isinstance(bound_leaf, str) and claim_leaf != bound_leaf
             and "/" not in claim_leaf and "/" not in bound_leaf
             and declared["claim_runs_root"].get("leaf", claim_leaf) == claim_leaf
             and declared["bound_runs_root"].get("leaf", bound_leaf) == bound_leaf,
             "plan tree roots and fresh-root binding leaves disagree")
    claim_root, bound_root = runs_parent / claim_leaf, runs_parent / bound_leaf
    for root in (claim_root, bound_root):
        _require(not os.path.lexists(root), f"runs root {root} already exists; a window never reuses a runs root")
    _require(not _inside(claim_root, custody) and not _inside(custody, runs_parent / claim_leaf),
             "custody_root and the runs roots must be disjoint")
    default_ledger = measurement / DEFAULT_LEDGER_RELATIVE
    if "ledger_path" in inputs:
        _require(_absolute(inputs["ledger_path"], "ledger_path") == default_ledger,
                 "ledger_path must be the measurement checkout's default ledger "
                 f"({default_ledger}); the controller's pre-slot route reads only that file")
    _require(default_ledger.is_file(), f"the default ledger {default_ledger} must exist")
    head_pin = measurement / HEAD_PIN_RELATIVE
    _require(head_pin.is_file(), f"the ledger head pin {head_pin} must exist")
    # The chain's first stage reserves the bracket session, and the
    # reservation refuses unless the ledger's physical head equals the
    # committed pin (calibration_ledger.append_bracket_session_receipt): a
    # stale pin would stop the chain at exit 10 after the whole arm.
    ledger_status = ledger_head_status(measurement)
    _require(not ledger_status["blocking"], ledger_head_refusal(ledger_status, measurement))
    identity_path, _ = _locator(inputs["identity_epoch_json"], "identity_epoch_json")
    t1_path, _ = _locator(inputs["t1_bindings_json"], "t1_bindings_json")
    registration = None
    if inputs["registration"] is not None:
        path, digest = _locator(inputs["registration"], "registration", base=measurement)
        registration = {"path": str(path), "sha256": digest}
    backups = {name: _absolute(inputs[name + "_backup_destination"], name + "_backup_destination")
               for name in ("claim", "bound")}
    _require(backups["claim"] != backups["bound"], "backup destinations must differ")
    for destination in backups.values():
        for source in (custody, claim_root, bound_root, measurement):
            _require(not _inside(destination, source) and not _inside(source, destination),
                     f"backup destination {destination} overlaps {source}")

    plan_meta = tree.get("plan") or {}
    identity = tree.get("window_identity") or {}
    for value, field in ((plan_meta.get("plan_id"), "plan.plan_id"), (plan_meta.get("path"), "plan.path"),
                         (identity.get("window_id"), "window_identity.window_id"),
                         (identity.get("evidence_root_id"), "window_identity.evidence_root_id")):
        _require(isinstance(value, str) and value, f"plan tree {field} is missing")
    bindings = {
        "repo_root": str(measurement),
        "ledger_path": str(default_ledger),
        "claim_runs_root": str(claim_root),
        "bound_runs_root": str(bound_root),
        "operator_log_root": str(custody / "operator-logs"),
        "pre_calibration_dir": str(claim_root / "instrument_validation" / inputs["pre_attempt_id"]),
        "post_calibration_dir": str(claim_root / "instrument_validation" / inputs["post_attempt_id"]),
        "claim_backup_destination": str(backups["claim"]),
        "bound_backup_destination": str(backups["bound"]),
        "bracket_session_id": inputs["bracket_session_id"],
        "pre_attempt_id": inputs["pre_attempt_id"],
        "post_attempt_id": inputs["post_attempt_id"],
        "identity_epoch_json": str(identity_path),
        "t1_bindings_json": str(t1_path),
    }
    chain_path = custody / CHAIN_BASENAME
    try:
        runbook_text = (measurement / b5_chain.RUNBOOK_RELATIVE).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WindowPlanError(f"the measurement checkout's runbook is unreadable: {exc}") from exc
    try:
        chain_raw = b5_chain.render_chain(
            tree=tree, tree_sha256=tree_sha256, stages=stages, bindings=bindings,
            measurement_root=measurement, pack_root=pack_root, plan_id=inputs["plan_id"],
            runbook_text=runbook_text, settle_s=settle_s, horizon_s=horizon_s)
    except b5_chain.ChainRenderError as exc:
        raise WindowPlanError(f"chain: {exc}") from exc
    env_values = {
        "MEASUREMENT_REPO": str(measurement), "WINDOW_ID": identity["window_id"],
        "BRACKET_SESSION_ID": inputs["bracket_session_id"],
        "FROZEN_PLAN": str(pack_root / plan_meta["path"]), "PACK_ROOT": str(pack_root),
        "PACK_ID": pack_root.name, "PLAN_ID": plan_meta["plan_id"],
        "EVIDENCE_ROOT_ID": identity["evidence_root_id"],
        "IDENTITY_EPOCH_JSON": str(identity_path), "T1_BINDINGS_JSON": str(t1_path),
        "PRE_ATTEMPT_ID": inputs["pre_attempt_id"], "POST_ATTEMPT_ID": inputs["post_attempt_id"],
        "RUNS_ROOT": str(claim_root), "BOUND_RUNS_ROOT": str(bound_root),
        "CALIBRATION_LEDGER": str(default_ledger), "LEDGER_HEAD_PIN": str(head_pin),
        "ARM_READINESS_CUSTODY_ROOT": str(custody / "hazards"), "CUSTODY_ROOT": str(custody),
        "WINDOW_CUSTODY_ROOT": str(custody), "QUARANTINE_ROOT": str(custody / "quarantine"),
        "CLAIM_BACKUP_DEST": str(backups["claim"]), "BOUND_BACKUP_DEST": str(backups["bound"]),
        "WAIVER_PATH": "none", "POWER_POLICY": POWER_POLICY,
        "SETTLE_S": str(int(settle_s)) if float(settle_s).is_integer() else repr(float(settle_s)),
    }
    env_raw = window_env_bytes(env_values)
    window_max_s = 60 * math.ceil((programmed_span_s + T0_STAGE_CAP_S) / 60)
    pack_sha256, pack_digest_error = None, None
    try:
        if pack_digest is None:
            from joulewise.arm_readiness import committed_pack_tree_sha256 as pack_digest
        pack_sha256 = pack_digest(pack_root)
        if not isinstance(pack_sha256, str) or _SHA256_RE.fullmatch(pack_sha256) is None:
            pack_digest_error, pack_sha256 = f"unexpected digest {pack_sha256!r}", None
    except Exception as exc:  # noqa: BLE001 - recorded; the harvest recomputes pack identity
        pack_digest_error = f"{type(exc).__name__}: {exc}"
    hazard_window = {
        "schema": night_gate.HAZARD_WINDOW_SCHEMA,
        "attempt": inputs["attempt"],
        "pack": {"pack_id": pack_root.name, "pack_root": str(pack_root), "pack_sha256": pack_sha256,
                 "plan_tree_sha256": tree_sha256, "pack_plan_id": plan_meta["plan_id"],
                 "window_id": identity["window_id"], "evidence_root_id": identity["evidence_root_id"]},
        "bracket_session_id": inputs["bracket_session_id"],
        "bindings": bindings,
        "runs_roots": {"claim": str(claim_root), "bound": str(bound_root)},
        "T_stream_max_s": t_stream_max_s,
        "planned_bytes": planned_bytes,
        "member_count": members,
        "thresholds": thresholds,
        "g10": inputs["g10"],
        "programmed_span_s": programmed_span_s,
        "t0_stage_cap_s": T0_STAGE_CAP_S,
        "settle_s": settle_s,
        "window_env": {"path": str(custody / WINDOW_ENV_BASENAME), "sha256": _sha256(env_raw)},
        "registration": registration,
        "chain_deviations": list(b5_chain.DEVIATIONS),
        "disk_volumes": [str(claim_root), str(bound_root), str(custody),
                         str(backups["claim"]), str(backups["bound"])],
        "stages": [stage.summary() for stage in stages],
    }
    plan_value = {
        "schema": night_gate.HAZARD_PLAN_SCHEMA,
        "schema_version": night_gate.HAZARD_PLAN_SCHEMA_VERSION,
        "plan_id": inputs["plan_id"],
        "receipt_class": night_gate.HAZARD_PACK,
        "t0_epoch_s": inputs["t0_epoch_s"],
        "window_max_s": window_max_s,
        "authored_epoch_s": float(now()),
        "repo_head": inputs["repo_head"],
        "measurement_root": str(measurement),
        "measurement_head": inputs["measurement_head"],
        "chain_path": str(chain_path),
        "chain_sha256_path": str(chain_path) + ".sha256",
        "custody_root": str(custody),
        "registration_path": registration["path"] if registration else None,
        "hazard_window": hazard_window,
    }
    try:
        night_gate.NightPlan.from_mapping(plan_value)
    except night_gate.PlanError as exc:
        raise WindowPlanError(f"the plan does not parse: {exc}") from exc
    plan_raw = (json.dumps(plan_value, indent=2, sort_keys=True) + "\n").encode("utf-8")

    # Every refusal is above this line. Create custody, then publish once.
    if not custody.exists():
        os.mkdir(custody, 0o700)
    for root in (claim_root, bound_root):
        os.mkdir(root, 0o755)  # exclusive: FileExistsError if a root appeared meanwhile
    _fsync_directory(runs_parent)
    (custody / "operator-logs").mkdir()
    window_env = _create_once(custody / WINDOW_ENV_BASENAME, env_raw)
    chain = _create_once(chain_path, chain_raw)
    sidecar = _create_once(Path(str(chain_path) + ".sha256"), b5_chain.sidecar_bytes(chain_raw, chain_path.name))
    plan = _create_once(custody / PLAN_BASENAME, plan_raw)
    record = {
        "schema": RECORD_SCHEMA, "status": "STAGED", "plan": plan, "chain": chain, "sidecar": sidecar,
        "window_env": window_env, "runs_roots": {"claim": str(claim_root), "bound": str(bound_root)},
        "window_max_s": window_max_s, "member_count": members,
        "planned_bytes": hazard_window["planned_bytes"], "pack_sha256": pack_sha256,
        "pack_digest_error": pack_digest_error, "plan_tree_sha256": tree_sha256,
        "inputs_sha256": _sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()),
        "sizing": {"programmed_span_s": span_allowance, "T_stream_max_s": stream_allowance},
        "thresholds_audit": thresholds_audit,
        "chain_deviations": list(b5_chain.DEVIATIONS),
        "ledger_head": ledger_status,
        # J3: what each collection stage launches, resolved from its own argv
        # (outside hazard_window, whose key set night_gate checks exactly).
        "stage_dispatches": [dispatch.record() for dispatch in dispatches],
        # Row 17: the collection deadline the chain applies, and the margin the
        # programmed span leaves before it (negative: a window that ran its
        # whole allowance would be truncated at the deadline, never lose its
        # post capture to the horizon).
        "collection_deadline": {
            "horizon_s": horizon_s, "post_reserve_s": b5_chain.HORIZON_POST_RESERVE_S,
            "member_allowance_s": b5_chain.HORIZON_MEMBER_ALLOWANCE_S,
            "stage_overhead_s": b5_chain.HORIZON_STAGE_OVERHEAD_S,
            "programmed_span_s": programmed_span_s,
            "margin_s": horizon_s - b5_chain.HORIZON_POST_RESERVE_S - programmed_span_s,
            "record": "$NIGHT_DIR/transcript/" + b5_chain.COLLECTION_DEADLINE_RECORD,
        },
        "driver_argv": ["<python>", "<repo>/scripts/run_night.py", "run", "--plan", plan["path"]],
    }
    _create_once(custody / RECORD_BASENAME, (json.dumps(record, indent=2, sort_keys=True) + "\n").encode())
    _fsync_directory(custody)
    return record
