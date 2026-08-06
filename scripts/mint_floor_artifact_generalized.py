#!/usr/bin/env python3
"""Mint a floor artifact with a digest-authenticated per-plan pinset.

This is the generalized sibling of ``mint_floor_artifact.py``.  It reuses
that mint's authentication, construction, binding, validation, and exclusive
write path through the review-pinned mint-core interface.  Every value that
the original tool hard-coded is required in one exact-schema JSON pinset,
whose exact file bytes must match a separately supplied SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import itertools
import json
import math
import re
import stat
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.whole_window import (  # noqa: E402
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    MINTED_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
)


PINSET_SCHEMA_VERSION = "joulewise.floor_mint_pinset.v1"
_ORIGINAL_MINT_PATH = Path(__file__).with_name("mint_floor_artifact.py")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SIX_DECIMAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)\.[0-9]{6}$")
_EVIDENCE_ROOT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SEMANTICS_IDS = {
    MINTED_CONSUMPTION_SEMANTICS_ID,
    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
}
_CORE_SEQUENCE = itertools.count()
_CORE_CONFIG_GLOBALS = frozenset(
    {
        "MINT_TOOL_VERSION",
        "CELL_ID",
        "TRANSPORT_GROUP_ID",
        "CONDITION_FAMILY_ID",
        "CONDITION_FAMILY_SHA256",
        "PLAN_SHA256",
        "A10_EVALUATION_BASIS_SHA256",
        "WINDOW_C_EVALUATION_BASIS_SHA256",
        "A10_EVALUATION_BASIS_MEMBERS",
        "WINDOW_C_EVALUATION_BASIS_MEMBERS",
        "A10_SPEC_MEMBERS",
        "WINDOW_C_SPEC_MEMBERS",
        "EXPECTED_ABSOLUTE_N",
        "EXPECTED_COMPARATIVE_N_BLOCKS",
        "A10_DRIFT_ALLOWANCE_J",
        "WINDOW_C_DRIFT_ALLOWANCE_J",
        "EXPECTED_OPERATIVE_FLOOR_TEXT",
        "A10_ORDER_MANIFEST_ID",
        "WINDOW_C_ORDER_MANIFEST_ID",
        "A10_CELL_ID",
        "WINDOW_C_CELL_ID",
        "METRIC",
        "WINDOW_CLASS",
        "TARGET_PRECHECK_PATH",
        "CALIBRATION_SCOPE",
        "PLAN_DECLARED_SCOPE",
        "SOURCE_CLASS",
    }
)
_CORE_SIGNATURES = {
    "ComponentPaths": (
        "(evidence_root_id: 'str', evidence_root: 'Path', report_path: 'Path', "
        "spec_path: 'Path', order_manifest_path: 'Path', "
        "calibration_cell_id: 'str', expected_kind: 'str') -> None"
    ),
    "pre_registration_gate": (
        "(*, plan: 'Mapping[str, Any]', plan_sha256: 'str', "
        "absolute: 'AuthenticatedComponent', "
        "comparative: 'AuthenticatedComponent') -> 'None'"
    ),
    "mint_authenticated_artifact": (
        "(*, artifact_id: 'str', plan: 'Mapping[str, Any]', "
        "plan_sha256: 'str', calibration_plan_relative_path: 'str', "
        "absolute: 'AuthenticatedComponent', "
        "comparative: 'AuthenticatedComponent', project_commit: 'str', "
        "project_tree_state: 'str') -> 'dict[str, Any]'"
    ),
    "validate_floor_artifact": (
        "(value: 'Mapping', *, pinset_path: 'Path | None' = None, "
        "expected_pinset_sha256: 'str | None' = None) -> 'list'"
    ),
    "mint_floor_artifact": (
        "(*, artifact_id: 'str', floor_path: 'Path', statement_path: 'Path', "
        "calibration_plan_path: 'Path', "
        "calibration_plan_relative_path: 'str', "
        "absolute_paths: 'ComponentPaths', comparative_paths: 'ComponentPaths', "
        "project_commit: 'str', project_tree_state: 'str', "
        "strict_validator: 'StrictValidator', "
        "consumption_semantics_id: 'str | None' = None, "
        "calibration_ledger_snapshot: 'CalibrationLedgerSnapshot | None' = None) "
        "-> 'Mapping[str, Any]'"
    ),
}
# D-109 R1.4 added the immutable ledger-snapshot parameter. Any future
# change requires explicit signature-pin review plus parity evidence.
StrictValidator = Callable[[Path, bool], Sequence[str]]


class MintError(ValueError):
    """A pinset or delegated mint gate failed; no artifact may be written."""


@dataclass(frozen=True)
class PlanPins:
    plan_id: str
    sha256: str
    declared_calibration_scope: str
    artifact_calibration_scope: str


@dataclass(frozen=True)
class ArtifactPins:
    cell_id: str
    transport_group_id: str
    source_class: str


@dataclass(frozen=True)
class CellPins:
    condition_family_id: str
    condition_family_sha256: str
    metric: str
    window_class: str
    target_precheck_path: tuple[str, ...]
    operative_floor_six_decimal: str


@dataclass(frozen=True)
class ComponentPins:
    evidence_root_id: str
    calibration_cell_id: str
    evaluation_basis_sha256: str
    evaluation_basis_members: int
    extraction_spec_members: int
    expected_n: int
    drift_allowance_j: float
    order_manifest_id: str


@dataclass(frozen=True)
class MintPinset:
    mint_tool_version: str
    plan: PlanPins
    artifact: ArtifactPins
    cell: CellPins
    absolute: ComponentPins
    comparative: ComponentPins


@dataclass(frozen=True)
class ComponentInputs:
    evidence_root: Path
    report_path: Path
    spec_path: Path
    order_manifest_path: Path


def _object(
    value: object,
    label: str,
    expected_keys: set[str],
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise MintError(f"{label} must be an object")
    keys = set(value)
    missing = sorted(expected_keys - keys)
    extra = sorted(keys - expected_keys)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing={missing}")
        if extra:
            details.append(f"extra={extra}")
        raise MintError(f"{label} schema mismatch: {'; '.join(details)}")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise MintError(f"{label} must be a nonempty trimmed string")
    return value


def _evidence_root_id(value: object, label: str) -> str:
    text = _string(value, label)
    if _EVIDENCE_ROOT_ID_RE.fullmatch(text) is None:
        raise MintError(
            f"{label} must be a portable identifier containing only letters, "
            "digits, dot, underscore, or hyphen"
        )
    return text


def _sha256(value: object, label: str) -> str:
    text = _string(value, label)
    if _SHA256_RE.fullmatch(text) is None:
        raise MintError(f"{label} must be 64 lowercase hexadecimal characters")
    return text


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise MintError(f"{label} must be a positive integer")
    return value


def _nonnegative_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise MintError(f"{label} must be a finite nonnegative number")
    converted = float(value)
    if not math.isfinite(converted) or converted < 0.0:
        raise MintError(f"{label} must be a finite nonnegative number")
    return converted


def _component_pins(value: object, label: str) -> ComponentPins:
    row = _object(
        value,
        label,
        {
            "evidence_root_id",
            "calibration_cell_id",
            "evaluation_basis_sha256",
            "evaluation_basis_members",
            "extraction_spec_members",
            "expected_n",
            "drift_allowance_j",
            "order_manifest_id",
        },
    )
    return ComponentPins(
        evidence_root_id=_evidence_root_id(
            row["evidence_root_id"], f"{label}.evidence_root_id"
        ),
        calibration_cell_id=_string(
            row["calibration_cell_id"], f"{label}.calibration_cell_id"
        ),
        evaluation_basis_sha256=_sha256(
            row["evaluation_basis_sha256"],
            f"{label}.evaluation_basis_sha256",
        ),
        evaluation_basis_members=_positive_int(
            row["evaluation_basis_members"],
            f"{label}.evaluation_basis_members",
        ),
        extraction_spec_members=_positive_int(
            row["extraction_spec_members"],
            f"{label}.extraction_spec_members",
        ),
        expected_n=_positive_int(row["expected_n"], f"{label}.expected_n"),
        drift_allowance_j=_nonnegative_number(
            row["drift_allowance_j"], f"{label}.drift_allowance_j"
        ),
        order_manifest_id=_string(
            row["order_manifest_id"], f"{label}.order_manifest_id"
        ),
    )


def _parse_pinset(value: object) -> MintPinset:
    root = _object(
        value,
        "pinset",
        {
            "schema_version",
            "mint_tool_version",
            "plan",
            "artifact",
            "cell",
            "absolute",
            "comparative",
        },
    )
    if root["schema_version"] != PINSET_SCHEMA_VERSION:
        raise MintError(
            "pinset.schema_version must equal " f"{PINSET_SCHEMA_VERSION!r}"
        )
    plan = _object(
        root["plan"],
        "pinset.plan",
        {
            "plan_id",
            "sha256",
            "declared_calibration_scope",
            "artifact_calibration_scope",
        },
    )
    artifact = _object(
        root["artifact"],
        "pinset.artifact",
        {"cell_id", "transport_group_id", "source_class"},
    )
    cell = _object(
        root["cell"],
        "pinset.cell",
        {
            "condition_family_id",
            "condition_family_sha256",
            "metric",
            "window_class",
            "target_precheck_path",
            "operative_floor_six_decimal",
        },
    )
    precheck_path = cell["target_precheck_path"]
    if not isinstance(precheck_path, list) or not precheck_path:
        raise MintError("pinset.cell.target_precheck_path must be a nonempty array")
    precheck = tuple(
        _string(part, f"pinset.cell.target_precheck_path[{index}]")
        for index, part in enumerate(precheck_path)
    )
    operative_value = cell["operative_floor_six_decimal"]
    if (
        not isinstance(operative_value, str)
        or _SIX_DECIMAL_RE.fullmatch(operative_value) is None
    ):
        raise MintError(
            "pinset.cell.operative_floor_six_decimal must be a nonnegative "
            "six-decimal literal"
        )
    operative = operative_value
    pinset = MintPinset(
        mint_tool_version=_string(
            root["mint_tool_version"], "pinset.mint_tool_version"
        ),
        plan=PlanPins(
            plan_id=_string(plan["plan_id"], "pinset.plan.plan_id"),
            sha256=_sha256(plan["sha256"], "pinset.plan.sha256"),
            declared_calibration_scope=_string(
                plan["declared_calibration_scope"],
                "pinset.plan.declared_calibration_scope",
            ),
            artifact_calibration_scope=_string(
                plan["artifact_calibration_scope"],
                "pinset.plan.artifact_calibration_scope",
            ),
        ),
        artifact=ArtifactPins(
            cell_id=_string(artifact["cell_id"], "pinset.artifact.cell_id"),
            transport_group_id=_string(
                artifact["transport_group_id"],
                "pinset.artifact.transport_group_id",
            ),
            source_class=_string(
                artifact["source_class"], "pinset.artifact.source_class"
            ),
        ),
        cell=CellPins(
            condition_family_id=_string(
                cell["condition_family_id"],
                "pinset.cell.condition_family_id",
            ),
            condition_family_sha256=_sha256(
                cell["condition_family_sha256"],
                "pinset.cell.condition_family_sha256",
            ),
            metric=_string(cell["metric"], "pinset.cell.metric"),
            window_class=_string(
                cell["window_class"], "pinset.cell.window_class"
            ),
            target_precheck_path=precheck,
            operative_floor_six_decimal=operative,
        ),
        absolute=_component_pins(root["absolute"], "pinset.absolute"),
        comparative=_component_pins(
            root["comparative"], "pinset.comparative"
        ),
    )
    fixed_decode_contract = {
        "pinset.plan.artifact_calibration_scope": (
            pinset.plan.artifact_calibration_scope,
            "production_window",
        ),
        "pinset.artifact.source_class": (
            pinset.artifact.source_class,
            "prospective",
        ),
        "pinset.cell.metric": (
            pinset.cell.metric,
            "phase_energy_j.decode",
        ),
        "pinset.cell.window_class": (pinset.cell.window_class, "phase"),
    }
    for label, (observed, expected) in fixed_decode_contract.items():
        if observed != expected:
            raise MintError(f"{label} must equal {expected!r}")
    if pinset.cell.target_precheck_path != ("phase", "decode"):
        raise MintError(
            "pinset.cell.target_precheck_path must equal ['phase', 'decode']"
        )
    return pinset


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MintError(f"pinset contains duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_json(value: str) -> None:
    raise MintError(f"pinset contains non-finite JSON number {value!r}")


def load_pinset(path: Path, expected_sha256: str) -> MintPinset:
    """Authenticate exact pinset bytes, then enforce the closed v1 schema."""

    expected = _sha256(expected_sha256, "pinset sha256 argument")
    path = Path(path)
    try:
        file_stat = path.lstat()
    except OSError as exc:
        raise MintError(f"pinset cannot be inspected: {exc.strerror or type(exc).__name__}") from exc
    if stat.S_ISLNK(file_stat.st_mode):
        raise MintError("pinset must not be a symlink")
    if not stat.S_ISREG(file_stat.st_mode):
        raise MintError("pinset must be a regular file")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise MintError(f"pinset cannot be read: {exc.strerror or type(exc).__name__}") from exc
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise MintError(
            f"pinset sha256 mismatch: expected {expected}, observed {actual}"
        )
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_json,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MintError(f"pinset is not valid UTF-8 JSON: {exc}") from exc
    return _parse_pinset(value)


def _assert_core_interface(module: ModuleType) -> None:
    missing = sorted(
        (_CORE_CONFIG_GLOBALS | set(_CORE_SIGNATURES) | {"MintError"})
        - set(vars(module))
    )
    if missing:
        raise MintError(
            "review-pinned mint-core interface drift: missing or renamed "
            f"symbols {missing}"
        )
    if not isinstance(module.MintError, type) or not issubclass(
        module.MintError, ValueError
    ):
        raise MintError(
            "review-pinned mint-core interface drift: MintError is not a "
            "ValueError type"
        )
    for symbol, expected in _CORE_SIGNATURES.items():
        try:
            observed = str(inspect.signature(getattr(module, symbol)))
        except (TypeError, ValueError) as exc:
            raise MintError(
                "review-pinned mint-core interface drift: cannot inspect "
                f"{symbol} signature"
            ) from exc
        if observed != expected:
            raise MintError(
                "review-pinned mint-core interface drift: "
                f"{symbol} signature expected {expected}, observed {observed}"
            )
    # Rendered-signature equality is spoofable: a default object whose
    # repr() is "None" renders identically while defeating the core's
    # `is None` load-on-absent behavior. Identity-check the sentinel
    # defaults structurally.
    mint_params = inspect.signature(module.mint_floor_artifact).parameters
    for name in ("consumption_semantics_id", "calibration_ledger_snapshot"):
        if mint_params[name].default is not None:
            raise MintError(
                "review-pinned mint-core interface drift: mint_floor_artifact "
                f"parameter {name} default is not the None sentinel"
            )


def _fresh_original_core() -> ModuleType:
    name = f"_joulewise_generalized_floor_mint_core_{next(_CORE_SEQUENCE)}"
    spec = importlib.util.spec_from_file_location(name, _ORIGINAL_MINT_PATH)
    if spec is None or spec.loader is None:
        raise MintError("cannot load the review-pinned mint-core interface")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        _assert_core_interface(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    sys.modules.pop(name, None)
    return module


def _configured_artifact_validator(
    core: ModuleType,
    pinset_path: Path,
    expected_pinset_sha256: str,
) -> Callable[[Mapping[str, Any]], list[Any]]:
    original_validator = core.validate_floor_artifact

    def validate(artifact: Mapping[str, Any]) -> list[Any]:
        return original_validator(
            artifact,
            pinset_path=pinset_path,
            expected_pinset_sha256=expected_pinset_sha256,
        )

    return validate


def _configured_core(
    pinset: MintPinset,
    *,
    pinset_path: Path,
    expected_pinset_sha256: str,
) -> ModuleType:
    """Load an isolated mint-1 core and replace only its hard-pin globals."""

    core = _fresh_original_core()
    original_gate = core.pre_registration_gate
    assignments = {
        "MINT_TOOL_VERSION": pinset.mint_tool_version,
        "CELL_ID": pinset.artifact.cell_id,
        "TRANSPORT_GROUP_ID": pinset.artifact.transport_group_id,
        "CONDITION_FAMILY_ID": pinset.cell.condition_family_id,
        "CONDITION_FAMILY_SHA256": pinset.cell.condition_family_sha256,
        "PLAN_SHA256": pinset.plan.sha256,
        "A10_EVALUATION_BASIS_SHA256": (
            pinset.absolute.evaluation_basis_sha256
        ),
        "WINDOW_C_EVALUATION_BASIS_SHA256": (
            pinset.comparative.evaluation_basis_sha256
        ),
        "A10_EVALUATION_BASIS_MEMBERS": (
            pinset.absolute.evaluation_basis_members
        ),
        "WINDOW_C_EVALUATION_BASIS_MEMBERS": (
            pinset.comparative.evaluation_basis_members
        ),
        "A10_SPEC_MEMBERS": pinset.absolute.extraction_spec_members,
        "WINDOW_C_SPEC_MEMBERS": pinset.comparative.extraction_spec_members,
        "EXPECTED_ABSOLUTE_N": pinset.absolute.expected_n,
        "EXPECTED_COMPARATIVE_N_BLOCKS": pinset.comparative.expected_n,
        "A10_DRIFT_ALLOWANCE_J": pinset.absolute.drift_allowance_j,
        "WINDOW_C_DRIFT_ALLOWANCE_J": pinset.comparative.drift_allowance_j,
        "EXPECTED_OPERATIVE_FLOOR_TEXT": (
            pinset.cell.operative_floor_six_decimal
        ),
        "A10_ORDER_MANIFEST_ID": pinset.absolute.order_manifest_id,
        "WINDOW_C_ORDER_MANIFEST_ID": pinset.comparative.order_manifest_id,
        "A10_CELL_ID": pinset.absolute.calibration_cell_id,
        "WINDOW_C_CELL_ID": pinset.comparative.calibration_cell_id,
        "METRIC": pinset.cell.metric,
        "WINDOW_CLASS": pinset.cell.window_class,
        "TARGET_PRECHECK_PATH": pinset.cell.target_precheck_path,
        "CALIBRATION_SCOPE": pinset.plan.artifact_calibration_scope,
        "PLAN_DECLARED_SCOPE": pinset.plan.declared_calibration_scope,
        "SOURCE_CLASS": pinset.artifact.source_class,
    }
    for name, value in assignments.items():
        setattr(core, name, value)

    core.validate_floor_artifact = _configured_artifact_validator(
        core,
        pinset_path,
        expected_pinset_sha256,
    )

    def generalized_gate(
        *,
        plan: Mapping[str, Any],
        plan_sha256: str,
        absolute: Any,
        comparative: Any,
    ) -> None:
        if plan_sha256 != pinset.plan.sha256:
            raise core.MintError(
                "pre-registration gate: calibration plan sha256 mismatch"
            )
        if (
            plan.get("plan_id") != pinset.plan.plan_id
            or plan.get("calibration_scope")
            != pinset.plan.declared_calibration_scope
        ):
            raise core.MintError(
                "pre-registration gate: calibration plan identity mismatch"
            )
        if absolute.evidence_root_id != pinset.absolute.evidence_root_id:
            raise core.MintError(
                "pre-registration gate: absolute evidence-root id mismatch"
            )
        if comparative.evidence_root_id != pinset.comparative.evidence_root_id:
            raise core.MintError(
                "pre-registration gate: comparative evidence-root id mismatch"
            )
        if (
            absolute.order_manifest.get("plan_id") != pinset.plan.plan_id
            or comparative.order_manifest.get("plan_id")
            != pinset.plan.plan_id
        ):
            raise core.MintError(
                "pre-registration gate: order manifest plan id mismatch"
            )

        # The original gate has three historical identity literals embedded
        # in its function body.  Normalize only those already-hard-checked
        # values for the call; every other check executes unchanged against
        # the configured pin globals.  Construction later receives the real
        # plan and components, so no normalized value reaches the artifact.
        legacy_plan_id = "p2-015-window-a-m3max-qwen25-1p5b-v1"
        normalized_plan = dict(plan)
        normalized_plan["plan_id"] = legacy_plan_id

        def normalized_component(component: Any, root_id: str) -> Any:
            order_manifest = dict(component.order_manifest)
            order_manifest["plan_id"] = legacy_plan_id
            return replace(
                component,
                evidence_root_id=root_id,
                order_manifest=order_manifest,
            )

        original_gate(
            plan=normalized_plan,
            plan_sha256=plan_sha256,
            absolute=normalized_component(absolute, "a10"),
            comparative=normalized_component(comparative, "window_c"),
        )

    core.pre_registration_gate = generalized_gate
    return core


def pre_registration_gate(
    *,
    pinset_path: Path,
    pinset_sha256: str,
    plan: Mapping[str, Any],
    plan_sha256: str,
    absolute: Any,
    comparative: Any,
) -> None:
    """Run the configured pre-registration gate without building an artifact."""

    pinset = load_pinset(pinset_path, pinset_sha256)
    core = _configured_core(
        pinset,
        pinset_path=pinset_path,
        expected_pinset_sha256=pinset_sha256,
    )
    try:
        core.pre_registration_gate(
            plan=plan,
            plan_sha256=plan_sha256,
            absolute=absolute,
            comparative=comparative,
        )
    except core.MintError as exc:
        raise MintError(str(exc)) from exc


def mint_authenticated_artifact(
    *,
    pinset_path: Path,
    pinset_sha256: str,
    artifact_id: str,
    plan: Mapping[str, Any],
    plan_sha256: str,
    calibration_plan_relative_path: str,
    absolute: Any,
    comparative: Any,
    project_commit: str,
    project_tree_state: str,
) -> Mapping[str, Any]:
    """Gate and build from already-authenticated component fixtures/evidence."""

    pinset = load_pinset(pinset_path, pinset_sha256)
    core = _configured_core(
        pinset,
        pinset_path=pinset_path,
        expected_pinset_sha256=pinset_sha256,
    )
    try:
        return core.mint_authenticated_artifact(
            artifact_id=artifact_id,
            plan=plan,
            plan_sha256=plan_sha256,
            calibration_plan_relative_path=calibration_plan_relative_path,
            absolute=absolute,
            comparative=comparative,
            project_commit=project_commit,
            project_tree_state=project_tree_state,
        )
    except core.MintError as exc:
        raise MintError(str(exc)) from exc


def validate_floor_artifact(
    *,
    artifact: Mapping[str, Any],
    pinset_path: Path,
    pinset_sha256: str,
) -> list[Any]:
    """Validate an artifact against both schema v2 and its root-id pins."""

    pinset = load_pinset(pinset_path, pinset_sha256)
    core = _configured_core(
        pinset,
        pinset_path=pinset_path,
        expected_pinset_sha256=pinset_sha256,
    )
    return core.validate_floor_artifact(artifact)


def mint_floor_artifact(
    *,
    pinset_path: Path,
    pinset_sha256: str,
    artifact_id: str,
    floor_path: Path,
    statement_path: Path,
    calibration_plan_path: Path,
    calibration_plan_relative_path: str,
    absolute_inputs: ComponentInputs,
    comparative_inputs: ComponentInputs,
    project_commit: str,
    project_tree_state: str,
    strict_validator: StrictValidator,
    consumption_semantics_id: str | None = None,
) -> Mapping[str, Any]:
    """Authenticate, gate, construct, bind, validate, and write one artifact."""

    pinset = load_pinset(pinset_path, pinset_sha256)
    core = _configured_core(
        pinset,
        pinset_path=pinset_path,
        expected_pinset_sha256=pinset_sha256,
    )
    try:
        return core.mint_floor_artifact(
            artifact_id=artifact_id,
            floor_path=floor_path,
            statement_path=statement_path,
            calibration_plan_path=calibration_plan_path,
            calibration_plan_relative_path=calibration_plan_relative_path,
            absolute_paths=core.ComponentPaths(
                evidence_root_id=pinset.absolute.evidence_root_id,
                evidence_root=absolute_inputs.evidence_root,
                report_path=absolute_inputs.report_path,
                spec_path=absolute_inputs.spec_path,
                order_manifest_path=absolute_inputs.order_manifest_path,
                calibration_cell_id=pinset.absolute.calibration_cell_id,
                expected_kind="absolute",
            ),
            comparative_paths=core.ComponentPaths(
                evidence_root_id=pinset.comparative.evidence_root_id,
                evidence_root=comparative_inputs.evidence_root,
                report_path=comparative_inputs.report_path,
                spec_path=comparative_inputs.spec_path,
                order_manifest_path=comparative_inputs.order_manifest_path,
                calibration_cell_id=pinset.comparative.calibration_cell_id,
                expected_kind="comparative",
            ),
            project_commit=project_commit,
            project_tree_state=project_tree_state,
            strict_validator=strict_validator,
            consumption_semantics_id=consumption_semantics_id,
        )
    except core.MintError as exc:
        raise MintError(str(exc)) from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pinset", required=True, type=Path)
    parser.add_argument("--pinset-sha256", required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--single-count-out", required=True, type=Path)
    parser.add_argument("--calibration-plan", required=True, type=Path)
    parser.add_argument("--calibration-plan-relative-path", required=True)
    parser.add_argument("--absolute-root", required=True, type=Path)
    parser.add_argument("--absolute-report", required=True, type=Path)
    parser.add_argument("--absolute-spec", required=True, type=Path)
    parser.add_argument("--absolute-order-manifest", required=True, type=Path)
    parser.add_argument("--comparative-root", required=True, type=Path)
    parser.add_argument("--comparative-report", required=True, type=Path)
    parser.add_argument("--comparative-spec", required=True, type=Path)
    parser.add_argument(
        "--comparative-order-manifest", required=True, type=Path
    )
    parser.add_argument("--project-commit", required=True)
    parser.add_argument(
        "--project-tree-state", choices=("clean", "dirty"), required=True
    )
    parser.add_argument(
        "--consumption-semantics-id",
        choices=tuple(sorted(_SEMANTICS_IDS)),
        help=(
            "optional exact semantics dispatch; when supplied both component "
            "reports must use this id"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    from joulewise.cli import validate_bundle

    args = _parser().parse_args(argv)
    try:
        mint_floor_artifact(
            pinset_path=args.pinset,
            pinset_sha256=args.pinset_sha256,
            artifact_id=args.artifact_id,
            floor_path=args.out,
            statement_path=args.single_count_out,
            calibration_plan_path=args.calibration_plan,
            calibration_plan_relative_path=(
                args.calibration_plan_relative_path
            ),
            absolute_inputs=ComponentInputs(
                evidence_root=args.absolute_root,
                report_path=args.absolute_report,
                spec_path=args.absolute_spec,
                order_manifest_path=args.absolute_order_manifest,
            ),
            comparative_inputs=ComponentInputs(
                evidence_root=args.comparative_root,
                report_path=args.comparative_report,
                spec_path=args.comparative_spec,
                order_manifest_path=args.comparative_order_manifest,
            ),
            project_commit=args.project_commit,
            project_tree_state=args.project_tree_state,
            strict_validator=lambda path, strict: validate_bundle(
                path, strict=strict
            ),
            consumption_semantics_id=args.consumption_semantics_id,
        )
    except MintError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
