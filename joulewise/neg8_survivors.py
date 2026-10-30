"""Claim-time NEG-8 reference predicate; collection imports stay independent."""
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class ReferenceStrictVerdict:
    invalid: bool
    problems: tuple[str, ...]
    triangle_disagrees: bool
    strict_ran: bool


def neg8_reference_strict_invalid(bundle_path, *, strict_problems=None, validator=None,
                                  summary=None, metadata=None) -> ReferenceStrictVerdict:
    """Writer's full strict-validation and custody-triangle legs, no config leg."""
    from joulewise import whole_window as ww
    path = Path(bundle_path)
    ran = strict_problems is None
    if ran:
        if validator is None:
            from joulewise.cli import validate_bundle
            validator = validate_bundle
        try:
            strict_problems = validator(path, strict=True)
        except Exception as exc:
            strict_problems = (f"strict_validation_raised:{type(exc).__name__}",)
    problems = tuple(str(item) for item in strict_problems)
    if summary is None:
        summary = ww._read_json_object(path / "summary_metrics.json")
    if metadata is None:
        metadata = ww._read_json_object(path / "metadata.json")
    triangle = ww._custody_strict_invalid(path, summary, metadata)
    return ReferenceStrictVerdict(bool(problems) or triangle, problems, triangle, ran)


def neg8_reference_energy_unreadable(stored_summary) -> bool:
    from joulewise.whole_window import _neg8_writer_reference_energy
    return None in _neg8_writer_reference_energy(stored_summary)


def neg8_stored_conditions(core) -> frozenset[str]:
    """Stored conditions belonging to the closed verdict-writer vocabulary."""
    from joulewise.whole_window import NEG8_STORED_CONDITION_CODES
    if not isinstance(core, Mapping):
        return frozenset()
    conditions = core.get("conditions")
    bracket = core.get("neg8_bracket")
    bracket_conditions = bracket.get("conditions") if isinstance(bracket, Mapping) else None
    return frozenset(word for word in (conditions if isinstance(conditions, list) else [])
                     if isinstance(word, str) and word in NEG8_STORED_CONDITION_CODES) | frozenset(
        word for word in (bracket_conditions if isinstance(bracket_conditions, list) else [])
        if isinstance(word, str) and word in NEG8_STORED_CONDITION_CODES)
