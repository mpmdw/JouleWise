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
    # Registration 6.3 (block-5 revision 4): a member the whole-window verdict
    # fails for a reason no other member code carries (the harvest's
    # WHOLE_WINDOW_MEMBER_FAILURE_REASONS).
    "member.whole_window_member_failure": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
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
    # Battery-assist ruling (orchestrator, 2026-10-06): discharge on AC in a
    # member's measured request (a negative B0AC, or the registry fallback,
    # or a discharge-accumulator mean beyond 200 mA x V) is disclosed, never
    # excluded; charging, AC loss and missing evidence stay battery.member_span
    # / battery.unmeasured.  The discharged energy goes to withheld/, never
    # into the flag's observed fields.
    "battery.assist": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    # The same when only the phases outside the measured request were
    # assisted (ruling item 5: reported apart, decides nothing).
    "battery.assist_outside_request": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    # The KM003C whole-machine DC-in stream (joulewise.external.km003c_parse):
    # a recorded diagnostic, never a refusal or a claim number.
    "meter.absent": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.drops_excess": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.duplicates": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.clock_fit_residual": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.pdtr_gain_out_of_band": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.battery_activity": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "meter.vbus_out_of_contract": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    # Lane P3-DRV: the driver could not start, keep up (crash loop) or prove
    # stopped the meter process. Changes no number; the meter never refuses.
    "meter.supervision_fault": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
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
    # Gate-prune round 2, lane P2-RC (scripts/run_campaign.py; PLAN2 row 8, yield E).
    "member.timeout": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    # A record not written (orchestrator 2026-10-06, "physics refuses; everything else is a flag"):
    "member.stderr_uncopied": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    # The harvest (joulewise.b5.harvest).
    "neg8.corpus_member_dropped": _code("NEG8", "REPRESENTATION", DISCLOSE),
    "calibration.capture_battery_span": _code("CALIBRATION", "PHYSICS", EXCLUDE_WINDOW),
    "calibration.capture_battery_unmeasured": _code("CALIBRATION", "PHYSICS", EXCLUDE_WINDOW),
    "whole_window.not_passed": _code("NEG8", "NUMBER", DISCLOSE),
}

# Gate-prune round 2 (night-archive gate-prune/prune2/PLAN2.md sections 2.2 G and 3.1;
# lane P2-HARV registers them).  Every one changes no number except
# member.timeout: a member killed at its wall cap is not measured.
_PRUNE2_CODES = {
    "member.timeout": _code("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "census.unmeasured": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "monitor.crash_loop": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "calibration.refit_cache_miss": _code("CALIBRATION", "REPRESENTATION", DISCLOSE),
    "roster.horizon_truncated": _code("ROSTER", "REPRESENTATION", DISCLOSE),
    "member.retried": _code("ROSTER", "REPRESENTATION", DISCLOSE),
    "yield.stage_zero": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "yield.stage_low": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "yield.stage_stalled": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "stage.members_refused_pre_bundle_identical": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "records.runs_root_override": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "yield.harvest_disagrees_with_window": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "collection.zero_yield": _code("ROSTER", "REPRESENTATION", DISCLOSE),
    "collection.failure_histogram": _code("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "chain.stopped_before_collection": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "roster.dispatch_unresolved": _code("ROSTER", "REPRESENTATION", DISCLOSE),
    "records.identity_unmeasured_superseded": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "thermal.stage_battery_rise": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "thermal.battery_temperature_unmeasured": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    # Registered at integration (int3).  P2-CTL: the external-member match raised
    # (the refusal stands; its cause is recorded).  P2-DRV: a census journal
    # append failed; a supervision step raised and the pass went on; the
    # monitor wrote no battery or contention reading for the outage bound and
    # the driver stopped the chain (PLAN2 row 11: a stop like disk.low, which
    # is DISCLOSE; the members in the silent stretch carry battery.unmeasured
    # and contention.unmeasured, EXCLUDE_MEMBER, from the joins).
    "records.auxiliary_match_raised": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "census.journal_write_failed": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "supervision.pass_failed": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    "monitor.outage": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
}

# Gate-prune round 3, lane P3-HARV (joulewise.b5.harvest PRUNE3_CODES).  The
# battery-assist ruling (2026-10-06): discharge while on AC and not charging is
# disclosed, never excluded; charging, AC loss, a charge accumulator above the
# limit and missing evidence stay exclusions (battery.member_span,
# battery.accumulator_excursion, battery.unmeasured).  battery.assist marks a
# member whose measured request was assisted (the analysis's sensitivity line
# recomputes every cell without those members); assist only outside the
# request decides nothing.  A #421 endpoint pair (member or capture) that failed
# on its endpoint current alone, where the SMC journal shows no charging, is
# disclosed in place of the pair exclusion.  The historical calibration
# custody pass (P2-VPF S5): an earlier capture whose bytes changed excludes the
# window, a pass that could not run is disclosed.  battery.smc_unavailable and
# the meter.* codes are in _DISCLOSE_CODES above.
_PRUNE3_CODES = {
    "battery.assist": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "battery.assist_outside_request": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "battery.capture_pair_assist": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "calibration.capture_battery_assist": _code("CALIBRATION", "PHYSICS", DISCLOSE),
    "calibration.capture_battery_pair_assist": _code("CALIBRATION", "PHYSICS", DISCLOSE),
    "calibration.historical_custody_mismatch": _code("CALIBRATION", "NUMBER", EXCLUDE_WINDOW),
    "calibration.historical_custody_unmeasured": _code("CALIBRATION", "NUMBER", DISCLOSE),
    "records.window_not_launched": _code("RECORDS", "REPRESENTATION", DISCLOSE),
}

# Integration int4 (cooldown smoke, 2026-10-06; doctrine "physics refuses;
# everything else is a flag"): the driver's pre-launch lineage check found a
# locator that is absent, unreadable, rejected by the members' authenticator
# or naming another window's identity. It is recorded and the chain launches;
# only a changed boot refuses (night_refused_boot_changed).
_INT4_CODES = {
    "records.lineage_prelaunch_mismatch": _code("RECORDS", "REPRESENTATION", DISCLOSE),
    # Refusal-census triage (d), 2026-10-07: present bytes differ in an earlier
    # capture this window's acceptance neither derived from nor judged.
    "calibration.historical_custody_mismatch_unused": _code("CALIBRATION", "NUMBER", DISCLOSE),
    # P4 (orchestrator, 2026-10-06): a whole-window verdict that did not pass
    # and whose member_failures is absent or malformed names no failed member,
    # so member.whole_window_member_failure cannot be applied.
    "whole_window.member_failures_unreadable": _code("NEG8", "NUMBER", EXCLUDE_WINDOW),
}

# Audit-fix batch 1 (2026-10-07, Astra triple audit).  A1: a NEG-8 window
# reference (start, midpoint or end) carries a PHYSICS member exclusion
# (contention, battery, thermal, clock step, instrument sampling).  The
# reference has no cells, so the member exclusion removes nothing, while the
# drift allowance and screen computed from it stay in use; the bracket cannot
# be re-derived without it (3+1+3), so the window is excluded.
_AUDFIX1_CODES = {
    "neg8.reference_member_excluded": _code("NEG8", "PHYSICS", EXCLUDE_WINDOW),
    # Audit A3: an UNMEASURED arm verdict of a module other than the instrument
    # (a failed probe, not a measured hazard) is recorded by the driver and the
    # window goes on; the in-window monitor measures the module per member span.
    **{f"{module}.arm_unmeasured": _code("DIAGNOSTIC", "PHYSICS", DISCLOSE)
       for module in ("clock", "battery", "thermal", "contention", "disk")},
}

DRAFT_CODES: Mapping[str, Mapping[str, str]] = {
    **_WINDOW_CODES,
    **_MEMBER_CODES,
    **_DISCLOSE_CODES,
    **_CORE_PRUNE_CODES,
    **_PRUNE2_CODES,
    **_PRUNE3_CODES,
    **_INT4_CODES,
    **_AUDFIX1_CODES,
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
