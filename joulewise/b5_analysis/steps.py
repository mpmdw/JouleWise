"""Step-record primitives; S10 supplies the driver and the tracked class table."""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Mapping


def classify_step4_exit(exit_status: int, report: Mapping[str, Any], spec: Mapping[str, Any]) -> str:
    if exit_status == 0:
        return "ok"
    if exit_status != 1 or report.get("spec_membership_refusals") != []:
        return "refused"
    cells, wanted = report.get("cells"), spec.get("cells")
    if not isinstance(cells, list) or not isinstance(wanted, list):
        return "refused"
    # The sealed spec identifies these non-target floor cells by their p42 family.
    p42 = {cell["cell_id"] for cell in wanted if cell.get("kind") in ("absolute", "comparative")
           and "p42" in cell.get("condition_family_id", "").split("-")}
    ids = [cell.get("cell_id") for cell in cells]
    spec_ids = [cell.get("cell_id") for cell in wanted]
    if len(ids) != len(set(ids)) or set(ids) != set(spec_ids):
        return "refused"
    if any(type(cell.get("extractable")) is not bool for cell in cells):
        return "refused"
    refused = {cell["cell_id"] for cell in cells if cell["extractable"] is False}
    return "p42_floor_cells_only" if p42 and refused == p42 else "refused"


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
    if refusal_code is None:
        status, refusal = "ok", None
    elif refusal_code in classes.get("tooling", classes.get("tooling_refusal", ())):
        status, refusal = "tooling_refusal", refusal_code
    elif refusal_code in classes.get("outcome", classes.get("outcome_class", ())):
        status, refusal = "outcome_class", f"outcome-class refusal at step {step}"
    else:
        status, refusal = "unclassified_refusal", f"unclassified refusal at step {step}"
    return StepRecord(str(step), window, status, exit_status=exit_status, refusal=refusal, flags=tuple(flags), **kwargs)
