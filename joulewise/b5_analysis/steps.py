"""Step-record primitives; S10 supplies the driver and the tracked class table."""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Mapping, Sequence


def require_primary_context(*objects) -> None:
    """Fence registered writers from the unregistered sensitivity bound.

    Deliberately duck-typed: importing step records must not load whole_window.
    Containers are expanded once; contexts and sessions expose the same field.
    """
    from .windows import AnalysisRefusal

    for obj in objects:
        values = (obj.values() if isinstance(obj, Mapping) else obj
                  if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)) else (obj,))
        for value in values:
            if value is not None and getattr(value, "sensitivity_bound_s", None) is not None:
                raise AnalysisRefusal("sensitivity_context_on_registered_path")


# Every step-4 exit-1 branch names itself through dry_run_refusal_classes.json:
# the registered p42 exit, one outcome class, or a tooling code (plan section 3.1).
STEP4_P42_FLOOR_CELLS_ONLY = "p42_floor_cells_only"
STEP4_FLOOR_CELL_NOT_EXTRACTABLE = "floor_cell_not_extractable"
STEP4_REPORT_MALFORMED = "extraction_report_malformed"
STEP4_SPEC_MALFORMED = "extraction_spec_malformed"
STEP4_SPEC_MEMBERSHIP_REFUSED = "extraction_spec_membership_refused"
STEP4_CELL_IDS_DUPLICATED = "extraction_cell_ids_duplicated"
STEP4_CELL_SET_DIFFERS = "extraction_cell_set_differs_from_spec"
STEP4_EXTRACTABLE_NOT_BOOLEAN = "extraction_extractable_not_boolean"
STEP4_EXIT_WITHOUT_REFUSED_CELL = "extraction_exit_without_refused_cell"


def classify_step4_exit(exit_status: int, report: Mapping[str, Any], spec: Mapping[str, Any]) -> str:
    """Name a step-4 exit: "ok", the registered p42 exit, a registered code, or "refused".

    "refused" is left only for an exit status other than 0 or 1, whose code
    the driver takes from the extractor's own refusal line.
    """
    if type(exit_status) is not int:
        return "refused"
    if exit_status == 0:
        return "ok"
    if exit_status != 1:
        return "refused"
    if not isinstance(report, Mapping):
        return STEP4_REPORT_MALFORMED
    cells, omitted = report.get("cells"), report.get("spec_membership_refusals")
    if not isinstance(cells, list) or not isinstance(omitted, list):
        return STEP4_REPORT_MALFORMED
    if any(not isinstance(cell, Mapping) or type(cell.get("cell_id")) is not str or not cell["cell_id"]
           for cell in cells):
        return STEP4_REPORT_MALFORMED
    # A kept member omitted from the spec is never the registered p42 outcome.
    if omitted:
        return STEP4_SPEC_MEMBERSHIP_REFUSED
    wanted = spec.get("cells") if isinstance(spec, Mapping) else None
    if (not isinstance(wanted, list)
            or any(not isinstance(cell, Mapping) or type(cell.get("cell_id")) is not str or not cell["cell_id"]
                   or type(cell.get("kind")) is not str or type(cell.get("condition_family_id")) is not str
                   for cell in wanted)):
        return STEP4_SPEC_MALFORMED
    # The sealed spec identifies these non-target floor cells by their p42 family.
    p42 = {cell["cell_id"] for cell in wanted if cell["kind"] in ("absolute", "comparative")
           and "p42" in cell["condition_family_id"].split("-")}
    ids = [cell["cell_id"] for cell in cells]
    spec_ids = [cell["cell_id"] for cell in wanted]
    if len(ids) != len(set(ids)) or len(spec_ids) != len(set(spec_ids)):
        return STEP4_CELL_IDS_DUPLICATED
    if set(ids) != set(spec_ids):
        return STEP4_CELL_SET_DIFFERS
    if any(type(cell.get("extractable")) is not bool for cell in cells):
        return STEP4_EXTRACTABLE_NOT_BOOLEAN
    refused = {cell["cell_id"] for cell in cells if cell["extractable"] is False}
    if not refused:
        return STEP4_EXIT_WITHOUT_REFUSED_CELL
    # "Only the p42 floor cells": every refused cell is one, not necessarily all.
    return STEP4_P42_FLOOR_CELLS_ONLY if refused <= p42 else STEP4_FLOOR_CELL_NOT_EXTRACTABLE


@dataclass(frozen=True)
class StepRecord:
    step: str
    window: str | None
    status: str
    exit_status: int | None = None
    registered_exit: str | None = None
    schema_valid: bool | None = None
    outputs: tuple[Mapping[str, str], ...] = ()
    refusal: str | None = None
    flags: tuple[Any, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        def plain(value):
            if isinstance(value, Mapping):
                return {key: plain(item) for key, item in value.items()}
            if isinstance(value, (list, tuple)):
                return [plain(item) for item in value]
            return value
        return {item.name: plain(getattr(self, item.name)) for item in fields(self)}


def step_record(step: str, *, window: str | None = None, exit_status: int | None = None,
                refusal_code: str | None = None, classes: Mapping[str, Any] | None = None,
                flags=(), **kwargs) -> StepRecord:
    """Keep outcome and unclassified codes out of the blind record."""
    classes = classes or {}
    registered_p42 = (str(step) == "4" and exit_status == 1
                      and kwargs.get("registered_exit") == "p42_floor_cells_only")
    if refusal_code is None and exit_status not in (None, 0) and not registered_p42:
        status, refusal = "unclassified_refusal", f"unclassified refusal at step {step}"
    elif refusal_code is None:
        status, refusal = "ok", None
    elif refusal_code in classes.get("tooling", classes.get("tooling_refusal", ())):
        status, refusal = "tooling_refusal", refusal_code
    elif refusal_code in classes.get("outcome", classes.get("outcome_class", ())):
        status, refusal = "outcome_class", f"outcome-class refusal at step {step}"
    else:
        status, refusal = "unclassified_refusal", f"unclassified refusal at step {step}"
    return StepRecord(str(step), window, status, exit_status=exit_status, refusal=refusal, flags=tuple(flags), **kwargs)
