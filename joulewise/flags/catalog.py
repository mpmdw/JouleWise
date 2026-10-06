"""The flag catalog: for each flag code, its family, class and effect.

The sealed catalog is ``configs/campaigns/v5_claim_25g83/flag_catalog.json``
(lane L6, sealed with the registration). It is the only authority on effects.
The harvester looks effects up; it never decides them. A code the catalog does
not list gets ``UNCLASSIFIED``: that blocks the release event until a blind
classification, and never blocks collection.

File format, schema ``joulewise.flag_catalog.v1``::

    {
      "schema_version": "joulewise.flag_catalog.v1",
      "codes": {
        "<code>": {"family": "...", "klass": "...", "effect": "...",
                   "blinding": "STRUCTURE"|"RESTRICTED"   (optional)},
        ...
      },
      "rules": {"cell_unit_minimum": 8}                    (optional)
    }

``DRAFT_CODES`` below is this lane's proposal, transcribed from plan sections
3.4 and 3.5. It exists so that L6 can seal from it and so that the tests and
the NUMBER coverage map have a fixed vocabulary before the seal. It is not a
catalog in force: :func:`load_catalog` never falls back to it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from joulewise.flags.schema import BLINDINGS, CODE_RE, FAMILIES, KLASSES

CATALOG_SCHEMA = "joulewise.flag_catalog.v1"
SEALED_CATALOG_RELATIVE_PATH = "configs/campaigns/v5_claim_25g83/flag_catalog.json"

EXCLUDE_WINDOW = "EXCLUDE_WINDOW"
EXCLUDE_MEMBER = "EXCLUDE_MEMBER"
DISCLOSE = "DISCLOSE"
UNCLASSIFIED = "UNCLASSIFIED"
EFFECTS = (EXCLUDE_WINDOW, EXCLUDE_MEMBER, DISCLOSE)

DEFAULT_CELL_UNIT_MINIMUM = 8


class CatalogError(ValueError):
    """The catalog file is unreadable or malformed."""


def _code(family: str, klass: str, effect: str, blinding: str = "STRUCTURE") -> dict[str, str]:
    return {"family": family, "klass": klass, "effect": effect, "blinding": blinding}


# Plan section 3.5, EXCLUDE_WINDOW.
_WINDOW_CODES = {
    "pack.identity_mismatch": _code("PACK_IDENTITY", "NUMBER", EXCLUDE_WINDOW),
    "code.executed_differs_from_sealed": _code("CODE_IDENTITY", "NUMBER", EXCLUDE_WINDOW),
    "model.identity_mismatch": _code("MODEL_IDENTITY", "NUMBER", EXCLUDE_WINDOW),
    "calibration.capture_invalid": _code("CALIBRATION", "NUMBER", EXCLUDE_WINDOW),
    "calibration.bracket_acceptance_failed": _code("CALIBRATION", "NUMBER", EXCLUDE_WINDOW),
    "calibration.session_not_bound": _code("CALIBRATION", "NUMBER", EXCLUDE_WINDOW),
    "calibration.no_bracket": _code("CALIBRATION", "NUMBER", EXCLUDE_WINDOW),
    "neg8.bound_not_derived": _code("NEG8", "NUMBER", EXCLUDE_WINDOW),
    "neg8.screen_failed": _code("NEG8", "NUMBER", EXCLUDE_WINDOW),
    "instrument.precal_screen_failed": _code("INSTRUMENT", "NUMBER", EXCLUDE_WINDOW),
    "clock.step_overlap_calibration": _code("CLOCK_SYSTEMATIC", "PHYSICS", EXCLUDE_WINDOW),
    "clock.systematic": _code("CLOCK_SYSTEMATIC", "NUMBER", EXCLUDE_WINDOW),
    "cell.below_minimum": _code("ROSTER", "NUMBER", EXCLUDE_WINDOW),
}

# Plan section 3.5, EXCLUDE_MEMBER: validity, physics in span, roster.
_MEMBER_CODES = {
    "member.status_not_succeeded": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.strict_validation_failed": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.anchor_not_bounded": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.token_count_mismatch": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.target_phase_precheck_failed": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.anchor_energy_envelope_exceeded": _code(
        "MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER, "RESTRICTED"
    ),
    "member.idle_window_suspect": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.cooldown_cap_hit": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.cooldown_evidence_unverified": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.admission_aborted": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.config_not_in_inventory": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.bytes_missing": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "battery.capture_pair_failed": _code("MEMBER_VALIDITY", "PHYSICS", EXCLUDE_MEMBER),
    "battery.member_span": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "battery.accumulator_excursion": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "battery.unmeasured": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "thermal.os_level_nonzero": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "thermal.powermetrics_pressure_elevated": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "contention.request_overlap": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "contention.unmeasured": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "clock.step_overlap": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "instrument.insufficient_in_window_samples": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "instrument.cadence_ratio_below_threshold": _code("PHYSICS_IN_SPAN", "PHYSICS", EXCLUDE_MEMBER),
    "roster.not_in_plan": _code("ROSTER", "NUMBER", EXCLUDE_MEMBER),
    "roster.foreign_attempt": _code("ROSTER", "NUMBER", EXCLUDE_MEMBER),
    "roster.before_chain_started": _code("ROSTER", "NUMBER", EXCLUDE_MEMBER),
}

# Plan section 3.5, DISCLOSE only.
_DISCLOSE_CODES = {
    "records.receipt": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "records.lineage_formality": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "records.attempt_history": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "records.pin_ledger": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "records.provenance_digest": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "records.naming": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "records.notice": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "network_time.off_output": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "clock.sntp_offset": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "clock.step": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "clock.frequency_changed": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "clock.unmeasured": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "thermal.unmeasured": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "disk.low": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "contention.kernel_task_share": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "monitor.probe_in_phase": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "battery.capture_pair_missing_covered": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "battery.accumulator_diagnostic": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "g10.discharged": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "g10.not_discharged": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "diagnostic.s1_structural": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "calibration.ledger_not_ready": _code("CALIBRATION", "REPRESENTATION", DISCLOSE),
    "model.identity_unpinned": _code("MODEL_IDENTITY", "REPRESENTATION", DISCLOSE),
}

DRAFT_CODES: Mapping[str, Mapping[str, str]] = {
    **_WINDOW_CODES,
    **_MEMBER_CODES,
    **_DISCLOSE_CODES,
}

# Codes the cell rule and the roster rule of exclusions.compute derive
# themselves (they are not read from flags).
DERIVED_CODES = (
    "cell.below_minimum",
    "roster.not_in_plan",
    "roster.foreign_attempt",
    "roster.before_chain_started",
    "member.bytes_missing",
)


@dataclass(frozen=True)
class Catalog:
    codes: Mapping[str, Mapping[str, str]]
    sha256: str | None
    path: str | None = None
    rules: Mapping[str, Any] = field(default_factory=dict)

    def entry(self, code: str) -> Mapping[str, str]:
        found = self.codes.get(code)
        if found is None:
            return {"family": None, "klass": None, "effect": UNCLASSIFIED, "blinding": None}
        return found

    def effect(self, code: str) -> str:
        return self.entry(code)["effect"]

    @property
    def cell_unit_minimum(self) -> int:
        value = self.rules.get("cell_unit_minimum", DEFAULT_CELL_UNIT_MINIMUM)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise CatalogError("rules.cell_unit_minimum must be a positive integer")
        return value


def validate_catalog(value: Any) -> list[str]:
    problems: list[str] = []
    if not isinstance(value, Mapping):
        return ["catalog must be a JSON object"]
    if value.get("schema_version") != CATALOG_SCHEMA:
        problems.append(f"schema_version must be {CATALOG_SCHEMA}")
    extra = sorted(set(value) - {"schema_version", "codes", "rules", "notes"})
    if extra:
        problems.append(f"unknown top-level keys: {extra}")
    codes = value.get("codes")
    if not isinstance(codes, Mapping) or not codes:
        problems.append("codes must be a nonempty object")
        return problems
    for code, entry in codes.items():
        if not isinstance(code, str) or CODE_RE.fullmatch(code) is None:
            problems.append(f"bad code {code!r}")
            continue
        if not isinstance(entry, Mapping):
            problems.append(f"{code}: entry must be an object")
            continue
        unknown = sorted(set(entry) - {"family", "klass", "effect", "blinding", "note"})
        if unknown:
            problems.append(f"{code}: unknown keys {unknown}")
        if entry.get("family") not in FAMILIES:
            problems.append(f"{code}: family must be one of {FAMILIES}")
        if entry.get("klass") not in KLASSES:
            problems.append(f"{code}: klass must be one of {KLASSES}")
        if entry.get("effect") not in EFFECTS:
            problems.append(f"{code}: effect must be one of {EFFECTS}")
        if entry.get("blinding", "STRUCTURE") not in BLINDINGS:
            problems.append(f"{code}: blinding must be one of {BLINDINGS}")
    rules = value.get("rules", {})
    if not isinstance(rules, Mapping):
        problems.append("rules must be an object")
    return problems


def catalog_from_bytes(raw: bytes, *, path: str | None = None) -> Catalog:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError(f"catalog is not UTF-8 JSON: {exc}") from exc
    problems = validate_catalog(value)
    if problems:
        raise CatalogError("; ".join(problems))
    codes = {
        code: {
            "family": entry["family"],
            "klass": entry["klass"],
            "effect": entry["effect"],
            "blinding": entry.get("blinding", "STRUCTURE"),
        }
        for code, entry in value["codes"].items()
    }
    catalog = Catalog(
        codes=codes,
        sha256=hashlib.sha256(raw).hexdigest(),
        path=path,
        rules=dict(value.get("rules", {})),
    )
    catalog.cell_unit_minimum  # validates the rule eagerly
    return catalog


def load_catalog(path: Path | str) -> Catalog:
    """Load a sealed catalog; ``sha256`` is over the exact file bytes."""

    target = Path(path)
    try:
        raw = target.read_bytes()
    except OSError as exc:
        raise CatalogError(f"cannot read catalog {target}: {exc}") from exc
    return catalog_from_bytes(raw, path=str(target))


def draft_catalog_document() -> dict[str, Any]:
    """The draft table as a catalog document (for L6 to seal from, and for tests)."""

    return {
        "schema_version": CATALOG_SCHEMA,
        "codes": {code: dict(entry) for code, entry in sorted(DRAFT_CODES.items())},
        "rules": {"cell_unit_minimum": DEFAULT_CELL_UNIT_MINIMUM},
    }


def draft_catalog() -> Catalog:
    raw = json.dumps(draft_catalog_document(), sort_keys=True, indent=2).encode("utf-8") + b"\n"
    return catalog_from_bytes(raw, path=None)


def missing_codes(catalog: Catalog, codes: Any) -> list[str]:
    """Codes from ``codes`` the catalog does not classify (sorted)."""

    return sorted({code for code in codes if code not in catalog.codes})
