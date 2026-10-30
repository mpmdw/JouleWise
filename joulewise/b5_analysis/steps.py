"""Step-record primitives; S10 supplies the driver and the tracked class table."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from functools import lru_cache
from pathlib import Path
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
# the registered p42 exit or a tooling code. Plan section 3.1 registers no other
# step-4 result, so no step-4 exit is an outcome class (L9-STEP4-3 ruling).
STEP4_P42_FLOOR_CELLS_ONLY = "p42_floor_cells_only"
STEP4_REPORT_MALFORMED = "extraction_report_malformed"
STEP4_SPEC_MALFORMED = "extraction_spec_malformed"
STEP4_SPEC_MEMBERSHIP_REFUSED = "extraction_spec_membership_refused"
STEP4_CELL_IDS_DUPLICATED = "extraction_cell_ids_duplicated"
STEP4_CELL_SET_DIFFERS = "extraction_cell_set_differs_from_spec"
STEP4_EXTRACTABLE_NOT_BOOLEAN = "extraction_extractable_not_boolean"
STEP4_EXIT_WITHOUT_REFUSED_CELL = "extraction_exit_without_refused_cell"
STEP4_CELL_TOOLING_REFUSAL = "extraction_cell_tooling_refusal"
STEP4_CELL_R3_REFUSAL = "extraction_cell_r3_refusal"

_STEP4_REASON_TABLE = Path(__file__).resolve().parents[2] / "configs/analysis/b5/step4_reason_classes.json"


@lru_cache(maxsize=1)
def step4_r3_reasons() -> frozenset[str]:
    """The plan section 2.2 R3 codes recorded beside the blind table (L9-STEP4-3 and -4 rulings)."""
    return frozenset(json.loads(_STEP4_REASON_TABLE.read_bytes())["r3"])


def classify_step4_exit(exit_status: int, report: Mapping[str, Any], spec: Mapping[str, Any]) -> str:
    """Name a step-4 exit: "ok", the registered p42 exit, a registered code, or "refused".

    "refused" is left only for an exit status other than 0 or 1, whose code
    the driver takes from the extractor's own refusal line.
    """
    if type(exit_status) is not int:
        return "refused"
    if exit_status == 0:
        return "ok" if isinstance(report, Mapping) and isinstance(spec, Mapping) else "refused"
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
    refused = [cell for cell in cells if cell["extractable"] is False]
    if not refused:
        return STEP4_EXIT_WITHOUT_REFUSED_CELL
    # Every refused cell, p42 included, carries its terminal reasons as a list of codes.
    if any(type(cell.get("refusal_reasons")) is not list
           or any(type(reason) is not str for reason in cell["refusal_reasons"]) for cell in refused):
        return STEP4_REPORT_MALFORMED
    # "Only the p42 floor cells": every refused cell is one, not necessarily all.
    # A refused p42 cell's reasons are irrelevant to the registered exit.
    targets = [cell for cell in refused if cell["cell_id"] not in p42]
    if not targets:
        return STEP4_P42_FLOOR_CELLS_ONLY
    # Any other refused cell stops the run. A refusal must name its reasons.
    if any(not cell["refusal_reasons"] for cell in targets):
        return STEP4_REPORT_MALFORMED
    # A section 2.2 R3 code anywhere is cured by an Ed ruling, never a code change,
    # so it wins over tooling; every other code, listed or not, is cured by a fix and rerun.
    r3 = step4_r3_reasons()
    if any(reason in r3 for cell in targets for reason in cell["refusal_reasons"]):
        return STEP4_CELL_R3_REFUSAL
    return STEP4_CELL_TOOLING_REFUSAL


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
