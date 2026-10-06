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

``NEVER_CLASSIFIED_CODES`` must not appear in any catalog; the loader refuses
one that lists them, so they always block release.

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

# Codes this package emits that must never be classified, so that they always
# block the release event until a person looks: a flag record that failed
# validation (its exclusion may be lost) and a collector the package does not
# know how to class.
NEVER_CLASSIFIED_CODES = ("records.malformed_flag", "collector.unmeasured")


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
    # A NUMBER identity check that could not run (collector error or timeout,
    # or a missing input such as H_claim or the sealed inventory) leaves the
    # identity unverified, so the window is not claim-usable (review 2026-10-05).
    "pack.identity_unmeasured": _code("PACK_IDENTITY", "NUMBER", EXCLUDE_WINDOW),
    "code.identity_unmeasured": _code("CODE_IDENTITY", "NUMBER", EXCLUDE_WINDOW),
    "model.identity_unmeasured": _code("MODEL_IDENTITY", "NUMBER", EXCLUDE_WINDOW),
    # No frozen pin for the model artifact or the runtime versions: a changed
    # weight file or MLX version would otherwise reach a claim with only a
    # disclosure. Excluding until L6 seals the pins (review 2026-10-05).
    "model.identity_unpinned": _code("MODEL_IDENTITY", "NUMBER", EXCLUDE_WINDOW),
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
    "member.bytes_ambiguous": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
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
    # A bundle with no stamp that places it after chain.started (gate-prune
    # rehearsal round 1, B7): not used, like an early one, but named apart.
    "roster.creation_unplaced": _code("ROSTER", "NUMBER", EXCLUDE_MEMBER),
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
    # Lane L1's monitor join (joulewise.hazards.battery.span_findings) emits
    # these two; the block-5 catalog (revision 3) classifies them so. Brief
    # battery assist below 200 mA x V is disclosed; an interval whose
    # accumulator rule could not run is disclosed (the publication rule still
    # applies to it).
    "battery.accumulator_activity": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "battery.accumulator_unavailable": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    # Lane 2026-10-06-smc-battery-meter: the battery current is judged on SMC
    # B0AC (1 Hz); a span (or an arm read) without good B0AC reads falls back
    # to the registry InstantAmperage and is disclosed.
    "battery.smc_unavailable": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    # The KM003C whole-machine DC-in stream (joulewise.external.km003c_parse):
    # a recorded diagnostic, never a refusal or a claim number.
    "meter.absent": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.drops_excess": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.duplicates": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.clock_fit_residual": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.pdtr_gain_out_of_band": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.battery_activity": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.vbus_out_of_contract": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "g10.discharged": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "g10.not_discharged": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "diagnostic.s1_structural": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "calibration.ledger_not_ready": _code("CALIBRATION", "REPRESENTATION", DISCLOSE),
    "calibration.ledger_readiness_unmeasured": _code("CALIBRATION", "REPRESENTATION", DISCLOSE),
    "records.checkout_untracked": _code("RECORDS", "REPRESENTATION", DISCLOSE),
}

# Gate-prune core prune (night-archive gate-prune/core-prune DESIGN.md section
# 5): the codes protected-core writers emit on the HAZARD_PACK path
# (joulewise.flags.core.CORE_FLAG_CODES, with that family and klass), the codes
# the harvest adds for them, and whole_window.not_passed, which the block-5
# draft catalog (revision 3) discloses because one member's failure fails the
# aggregate verdict. records.pin_ledger, code.executed_differs_from_sealed and
# calibration.capture_invalid are already above.
_CORE_PRUNE_CODES = {
    # Protected-core writers (core-controller, core-run_campaign, core-fiducial, core-reservation).
    "calibration.capture_battery_pair_unverified": _code("CALIBRATION", "PHYSICS", DISCLOSE),
    "calibration.power_policy_unverified": _code("CALIBRATION", "REPRESENTATION", DISCLOSE),
    "instrument.binary_identity_unmeasured": _code("INSTRUMENT", "NUMBER", EXCLUDE_MEMBER),
    "env.member_quiet_state_violated": _code("MEMBER_VALIDITY", "PHYSICS", EXCLUDE_MEMBER),
    "env.member_guard_flagged": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "member.idle_admission_telemetry_missing": _code("MEMBER_VALIDITY", "PHYSICS", EXCLUDE_MEMBER),
    "teardown.survivors": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "cooldown.result_unknown": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "env.stage_preflight_not_admitted": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "campaign.runner_record_flagged": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "calibration.writer_record_flagged": _code("CALIBRATION", "REPRESENTATION", DISCLOSE),
    # The harvest (joulewise.b5.harvest).
    "neg8.corpus_member_dropped": _code("NEG8", "REPRESENTATION", DISCLOSE),
    "calibration.capture_battery_span": _code("CALIBRATION", "PHYSICS", EXCLUDE_WINDOW),
    "calibration.capture_battery_unmeasured": _code("CALIBRATION", "PHYSICS", EXCLUDE_WINDOW),
    "whole_window.not_passed": _code("NEG8", "NUMBER", DISCLOSE),
}

DRAFT_CODES: Mapping[str, Mapping[str, str]] = {
    **_WINDOW_CODES,
    **_MEMBER_CODES,
    **_DISCLOSE_CODES,
    **_CORE_PRUNE_CODES,
}

# Codes the cell rule and the roster rule of exclusions.compute derive
# themselves (they are not read from flags).
DERIVED_CODES = (
    "cell.below_minimum",
    "roster.not_in_plan",
    "roster.foreign_attempt",
    "roster.before_chain_started",
    "roster.creation_unplaced",
    "member.bytes_missing",
    "member.bytes_ambiguous",
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
        if code in NEVER_CLASSIFIED_CODES:
            problems.append(f"{code} must stay unclassified (it always blocks release)")
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
