"""Block-5 window harvest: always the numbers plus the flags.

Doctrine (Ed, 2026-10-05, "Physics refuses; everything else is a flag"): arm
and t0 refuse only on a measured physical hazard.  After the chain has run,
nothing here refuses on data.  Every check this module runs is written as a
``joulewise.flag.v1`` record, and the sealed flag catalog, applied by the
exclusion function of lane L4, decides what a flag excludes.  This module
measures, replays and records; it never decides an effect.

Verdicts:

* ``COLLECTED``: ``night/chain.started`` exists.  Numbers and flags are
  emitted whatever the flags say.
* ``NULL``: the chain never started.
* ``HARVEST_FAULT``: this program failed on present bytes.  Every output that
  could be written is still written; ``claim_usable`` is forced false until a
  fixed harvest is re-run on the identical archived bytes.

Layout under the archive root (created once; a re-harvest uses a new root):

* ``sources/``: a clone of every input byte, with ``SHA256SUMS``.
* ``derived/``: structure only (flags, window summary, exclusions, roster,
  terminal ledger-head candidate, bracket binding, the registered harvest
  thresholds with their provenance, the NEG-8 bound check, the NEG-8 screen's
  re-evaluation against a collected-subset bound).  These files may leave
  custody.
* ``withheld/``: the numbers (re-reduced summaries), member spans, bracket
  evaluation, the re-evaluated NEG-8 bracket, member assessments and
  transcripts.  Restricted custody.
* ``harvest.json``: the verdict and the digests of every output.

Other-lane seams.  The harvest reads files written by lanes that land in the
same integration change: the hazard monitor journals and the arm record (L1),
L1's accumulator reader (``hazards.battery.accumulator_interval``), the window
plan, the arm-time executed-file inventory and the driver's
``night/hazard_result.json`` NEG-8 corpus locator (L2), the launch-lineage
audit (L3, ``window_lineage.audit_window_lineage``), the desk, arm and driver
flag files, the collectors' run log and the driver's record of the arm-time
collector call, and the exclusion function (L4), the registration's harvest
thresholds (section 6.9), the sealed inventory and flag catalog (L6).  Each
format is read in exactly one function here (``_plan_value``,
``resolve_thresholds``, ``parse_monitor_line``, ``accumulator_member_flags``,
``_arm_modules``, ``_inventory_map``, ``_collected_corpus_bytes``,
``lineage_audit``, ``flag_problems``, ``_fold_collector_run``,
``_arm_collector_records``, ``Catalog.load``,
``l4_exclusion_inputs``/``_l4_exclusions``), so an integration fix touches
one place.  The formats are the ones those lanes write, not shapes invented
here: ``tests/fixtures/b5_harvest/l1_monitor`` holds journals written by L1's
own monitor, and the tests run L4's real ``exclusions.compute`` and
``validate_flag`` whenever ``joulewise.flags`` is importable.
"""
from __future__ import annotations

import concurrent.futures
import dataclasses
import hashlib
import importlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

SCHEMA = "joulewise.harvest_b5_window.v1"
FLAG_SCHEMA = "joulewise.flag.v1"
WINDOW_FLAGS_SCHEMA = "joulewise.window_flags.v1"
ROSTER_SCHEMA = "joulewise.b5_harvest_roster.v1"
TERMINAL_BOUNDARY_SCHEMA = "joulewise.b5_terminal_boundary.v1"
NEG8_CHECK_SCHEMA = "joulewise.b5_neg8_bound_check.v1"
NEG8_SCREEN_SCHEMA = "joulewise.b5_neg8_screen.v1"
NEG8_BOUND_NAME = "neg8-drift-bound.json"      # in the bound runs root (the pack's bound-derivation output)
HAZARD_RESULT_NAME = "hazard_result.json"      # L2's driver terminal record, night/
# L4's collector run log beside the flag files (scripts/collect_window_flags.py);
# its rows are joulewise.flags.collect.COLLECTOR_RUN_SCHEMA records, not flags.
COLLECTOR_RUNS_NAME = "collector_runs.jsonl"
HAZARD_PACK_CLASS = "HAZARD_PACK"              # night_gate.HAZARD_PACK, the block-5 plan's receipt class
COLLECTOR_RUN_SCHEMA = "joulewise.flag_collector_run.v1"

COLLECTED, NULL, HARVEST_FAULT = "COLLECTED", "NULL", "HARVEST_FAULT"
FAMILIES = (
    "PACK_IDENTITY", "CODE_IDENTITY", "MODEL_IDENTITY", "CALIBRATION", "NEG8",
    "INSTRUMENT", "MEMBER_VALIDITY", "PHYSICS_IN_SPAN", "CLOCK_SYSTEMATIC",
    "ROSTER", "RECORDS", "DIAGNOSTIC",
)
KLASSES = ("PHYSICS", "NUMBER", "REPRESENTATION")
EFFECTS = ("EXCLUDE_WINDOW", "EXCLUDE_MEMBER", "DISCLOSE")
UNCLASSIFIED = "UNCLASSIFIED"
STRUCTURE, RESTRICTED = "STRUCTURE", "RESTRICTED"

# A commit between windows that changes only these paths keeps H_claim's code
# identity (plan section 6 item 13).  They are data, not code.
PIN_ONLY_PATHS = frozenset({"configs/calibration/calibration_ledger_head.json"})
CODE_PREFIXES = ("joulewise/", "scripts/")
SEALED_DIRECTORY = "configs/campaigns/v5_claim_25g83"
# joulewise.flags.collect.read_identity_pins documents this file; its "units"
# map is read here as the per-unit pin override.
IDENTITY_PINS_SCHEMA = "joulewise.b5_identity_pins.v1"

# Thresholds.  The harvest reads the flat block of registration section 6.9
# ("Harvest thresholds"), never a default: the registration the window plan
# names (``hazard_window.registration`` {path, sha256}, the plan writer's
# record) and, when the plan carries one, the plan's own flat copy
# (``hazard_window.harvest_thresholds``).  A key no registered source gives,
# two sources that disagree, an unreadable block or an invalid value is a
# recorded harvest fault (HARVEST_FAULT, never claim-usable until a harvest
# with the registered block is re-run on the same bytes).  The plan's
# ``hazard_window.thresholds`` is the arm's nested per-module block
# (registration 4.3) and is not read here.
HARVEST_THRESHOLD_KEYS = (
    "battery_limit_ma",                    # #421; 200 mA
    "battery_unmeasured_gap_s",            # no publication for > 120 s
    "battery_accumulator_watts_per_unit",  # 0.001: L1's confirmed mW per unit
    "thermal_unmeasured_gap_s",            # 5 s poll; three missed polls
    "contention_cpu_s_per_s",              # 5 % of one core
    "clock_step_ns",                       # 1 ms residual move between samples
    "clock_unmeasured_gap_s",              # 1 Hz journal
    "disk_low_bytes",                      # 10 GiB
    "clock_systematic_min_recorded",       # at least 5 recorded anchors
)
INTEGER_THRESHOLD_KEYS = frozenset({"clock_systematic_min_recorded"})
PLAN_HARVEST_THRESHOLDS_KEY = "harvest_thresholds"
THRESHOLDS_SCHEMA = "joulewise.b5_harvest_thresholds.v1"
# The section heading of registration 6.9, numbered or not ("### 6.9 Harvest thresholds").
_THRESHOLD_HEADING_RE = re.compile(r"^#{2,6}[ \t]+(?:[0-9]+(?:\.[0-9]+)*[ \t]+)?Harvest thresholds[ \t]*$",
                                   re.MULTILINE | re.IGNORECASE)
_ANY_HEADING_RE = re.compile(r"^#{1,6}[ \t]", re.MULTILINE)
_JSON_FENCE_RE = re.compile(r"^```json[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
CONTENTION_EXEMPT = frozenset({"kernel_task"})
INSTRUMENT_REASONS = frozenset({"insufficient_in_window_samples", "cadence_ratio_below_threshold"})
ENVELOPE_REASON = "anchor_energy_envelope_exceeds_quarter_metric"
ANCHOR_STATUSES = frozenset({"bounded", "unbounded", "invalid", "missing", "not recorded"})
REQUIRED_BUNDLE_FILES = ("config.json", "metadata.json", "events.jsonl", "summary_metrics.json",
                         "raw/powermetrics.plist")


# ---------------------------------------------------------------------------
# The codes this harvest emits.  family/klass/blinding are the emitter's own
# description; the sealed catalog may restate family and klass, and only the
# catalog gives an effect.  ``legacy`` names the check the code replaces.
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class CodeSpec:
    family: str
    klass: str
    blinding: str = STRUCTURE
    legacy: str | None = None


def _spec(family, klass, blinding=STRUCTURE, legacy=None):
    return CodeSpec(family, klass, blinding, legacy)


# Codes use lane L4's vocabulary (``joulewise.flags.catalog.DRAFT_CODES``)
# wherever L4 names the same fact, with L4's family and klass; the rest are
# listed in ``L5_ONLY_CODES`` for the draft and sealed catalogs (L4, L6).
CODES: dict[str, CodeSpec] = {
    # Pack, code and model identity: the arm-path NUMBER checks, replayed.
    "pack.identity_mismatch": _spec("PACK_IDENTITY", "NUMBER", legacy="joulewise/arm_readiness.py:3077"),
    "pack.identity_unmeasured": _spec("PACK_IDENTITY", "NUMBER"),
    "code.executed_differs_from_sealed": _spec("CODE_IDENTITY", "NUMBER", legacy="scripts/run_night.py:4022"),
    "code.identity_unmeasured": _spec("CODE_IDENTITY", "NUMBER"),
    "model.identity_mismatch": _spec("MODEL_IDENTITY", "NUMBER", legacy="joulewise/identity_pins.py:2401"),
    "model.identity_inconsistent_in_window": _spec("MODEL_IDENTITY", "NUMBER"),
    "model.identity_underivable": _spec("MODEL_IDENTITY", "NUMBER", legacy="joulewise/identity_pins.py:405"),
    "model.identity_unpinned": _spec("MODEL_IDENTITY", "NUMBER"),
    # Calibration bracket and ledger.
    "calibration.capture_invalid": _spec("CALIBRATION", "NUMBER"),
    "calibration.bracket_acceptance_failed": _spec("CALIBRATION", "NUMBER",
                                                   legacy="scripts/harvest_v5_g2b_window.py:279"),
    "calibration.binding_failed": _spec("CALIBRATION", "NUMBER"),
    "calibration.session_not_bound": _spec("CALIBRATION", "NUMBER"),
    "calibration.no_bracket": _spec("CALIBRATION", "NUMBER"),
    "calibration.ledger_snapshot_refused": _spec("CALIBRATION", "NUMBER"),
    "calibration.acceptance_mismatch": _spec("CALIBRATION", "NUMBER", legacy="scripts/harvest_v5_g2b_window.py:286"),
    "clock.step_overlap_calibration": _spec("CLOCK_SYSTEMATIC", "PHYSICS"),
    "calibration.capture_battery_pair_failed": _spec("CALIBRATION", "PHYSICS", legacy="joulewise/battery_float.py:1092"),
    # NEG-8 bound and the whole-window verdict.
    "neg8.bound_not_derived": _spec("NEG8", "NUMBER"),
    "neg8.screen_failed": _spec("NEG8", "NUMBER"),
    "whole_window.not_passed": _spec("NEG8", "NUMBER"),
    "whole_window.verdict_absent": _spec("NEG8", "NUMBER"),
    "whole_window.verdict_unauthenticated": _spec("NEG8", "REPRESENTATION"),
    "whole_window.producer_failed": _spec("NEG8", "REPRESENTATION"),
    # Clock.
    "clock.systematic": _spec("CLOCK_SYSTEMATIC", "NUMBER", legacy="scripts/harvest_v5_g2b_window.py:347"),
    "clock.step_overlap": _spec("PHYSICS_IN_SPAN", "PHYSICS"),
    "clock.step": _spec("DIAGNOSTIC", "PHYSICS"),
    "clock.frequency_changed": _spec("DIAGNOSTIC", "PHYSICS"),
    "clock.unmeasured": _spec("DIAGNOSTIC", "PHYSICS"),
    # Member validity.
    "member.bytes_missing": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.bytes_ambiguous": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.unreadable": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.status_not_succeeded": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.admission_aborted": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.strict_validation_failed": _spec("MEMBER_VALIDITY", "NUMBER", legacy="joulewise/cli.py:392"),
    "member.reduction_mismatch": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.anchor_not_bounded": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.anchor_recompute_mismatch": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.token_count_mismatch": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.target_phase_precheck_failed": _spec("MEMBER_VALIDITY", "NUMBER",
                                                 legacy="joulewise/analysis_engine/inputs.py:3493"),
    "member.anchor_energy_envelope_exceeded": _spec("MEMBER_VALIDITY", "NUMBER", RESTRICTED,
                                                    legacy="joulewise/analysis_engine/inputs.py:3493"),
    "member.idle_window_suspect": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.cooldown_cap_hit": _spec("MEMBER_VALIDITY", "NUMBER"),
    "member.cooldown_evidence_unverified": _spec("MEMBER_VALIDITY", "NUMBER",
                                                 legacy="joulewise/analysis_engine/inputs.py:2095"),
    "member.config_not_in_inventory": _spec("MEMBER_VALIDITY", "NUMBER", legacy="joulewise/arm_readiness.py:11451"),
    "member.span_unknown": _spec("PHYSICS_IN_SPAN", "PHYSICS"),
    # Physics in span (plan section 3.4).
    "battery.member_span": _spec("PHYSICS_IN_SPAN", "PHYSICS"),
    "battery.unmeasured": _spec("PHYSICS_IN_SPAN", "PHYSICS"),
    "battery.accumulator_excursion": _spec("PHYSICS_IN_SPAN", "PHYSICS"),
    "battery.accumulator_activity": _spec("DIAGNOSTIC", "PHYSICS"),
    "battery.accumulator_unavailable": _spec("DIAGNOSTIC", "PHYSICS"),
    "battery.capture_pair_failed": _spec("MEMBER_VALIDITY", "PHYSICS", legacy="joulewise/battery_float.py:1049"),
    "battery.capture_pair_missing_covered": _spec("DIAGNOSTIC", "PHYSICS"),
    "battery.capture_pair_missing": _spec("RECORDS", "REPRESENTATION"),
    "thermal.os_level_nonzero": _spec("PHYSICS_IN_SPAN", "PHYSICS"),
    "thermal.powermetrics_pressure_elevated": _spec("PHYSICS_IN_SPAN", "PHYSICS",
                                                    legacy="joulewise/environment_admission.py:279"),
    "thermal.unmeasured": _spec("DIAGNOSTIC", "PHYSICS"),
    "contention.request_overlap": _spec("PHYSICS_IN_SPAN", "PHYSICS"),
    "contention.unmeasured": _spec("PHYSICS_IN_SPAN", "PHYSICS"),
    "contention.kernel_task_share": _spec("DIAGNOSTIC", "PHYSICS"),
    "instrument.insufficient_in_window_samples": _spec("PHYSICS_IN_SPAN", "PHYSICS",
                                                       legacy="joulewise/analysis_engine/claims.py:43"),
    "instrument.cadence_ratio_below_threshold": _spec("PHYSICS_IN_SPAN", "PHYSICS",
                                                      legacy="joulewise/analysis_engine/claims.py:44"),
    "disk.low": _spec("DIAGNOSTIC", "PHYSICS"),
    # Roster.
    "roster.not_in_plan": _spec("ROSTER", "NUMBER"),
    "roster.before_chain_started": _spec("ROSTER", "NUMBER"),
    "roster.run_id_mismatch": _spec("ROSTER", "REPRESENTATION"),
    "roster.no_science_bundles": _spec("ROSTER", "NUMBER"),
    # A run id the plan tree launches (or lists) more than once: its later
    # planned positions can never be measured (rehearsal round 1, B3).
    "roster.duplicate_run_id": _spec("ROSTER", "NUMBER"),
    # Records.
    "records.monitor_journal_absent": _spec("RECORDS", "REPRESENTATION"),
    "records.monitor_line_malformed": _spec("RECORDS", "REPRESENTATION"),
    "records.arm_record_absent": _spec("RECORDS", "REPRESENTATION"),
    "records.terminal_record_absent": _spec("RECORDS", "REPRESENTATION"),
    "records.source_changed_during_harvest": _spec("RECORDS", "NUMBER"),
    "records.collector_failed": _spec("RECORDS", "REPRESENTATION"),
    # An earlier flag line (desk, arm, driver) that is not a valid flag.  It
    # may have been an exclusion, so it is never classified: L4's
    # NEVER_CLASSIFIED_CODES, which blocks the release event until read.
    "records.malformed_flag": _spec("RECORDS", "REPRESENTATION"),
    "g3.assertion_failed": _spec("RECORDS", "REPRESENTATION", legacy="scripts/check_window_provenance.py"),
    "g3.recompute_failed": _spec("NEG8", "NUMBER", legacy="scripts/check_window_provenance.py:837"),
    "g3.not_applicable": _spec("DIAGNOSTIC", "REPRESENTATION"),
    # The s1-structural diagnostics (plan section 4), read on the first real
    # window; ``observed.check`` names which one.
    "diagnostic.s1_structural": _spec("DIAGNOSTIC", "REPRESENTATION"),
    # Lane L3's launch-lineage audit (joulewise.window_lineage.audit_window_lineage),
    # one code per finding, with the family and klass L3 gives it.
    **{code: _spec("RECORDS", "REPRESENTATION", legacy="joulewise/window_lineage.py:audit_window_lineage")
       for code in ("lineage.locator_unreadable", "lineage.locator_sidecar_mismatch", "lineage.locator_noncanonical",
                    "lineage.locator_root_path_differs", "lineage.locator_role_differs",
                    "lineage.sibling_lineage_differs", "lineage.context_root_differs",
                    "lineage.record_chain_unverified", "lineage.arm_decision_digest_differs",
                    "lineage.completion_records_absent", "lineage.bundle_stamp_absent",
                    "lineage.bundle_stamp_differs", "lineage.bundle_locator_digest_differs",
                    "lineage.pack_digest_unrecorded", "lineage.collection_boot_unrecorded",
                    "lineage.arm_decision_unrecorded")},
    "lineage.plan_tree_digest_differs": _spec("PACK_IDENTITY", "NUMBER",
                                              legacy="joulewise/window_lineage.py:audit_window_lineage"),
    # Gate-prune core prune (DESIGN.md section 5).  The capture battery from
    # the continuous journal (N7) and the NEG-8 corpus drop rule (N2):
    "calibration.capture_battery_span": _spec("CALIBRATION", "PHYSICS"),
    "calibration.capture_battery_unmeasured": _spec("CALIBRATION", "PHYSICS"),
    "neg8.corpus_member_dropped": _spec("NEG8", "REPRESENTATION"),
    # Written by protected-core code on the HAZARD_PACK path into
    # <custody>/flags/core-*.jsonl, or printed behind UNWRITTEN_MARKER when
    # that write failed (N8); the harvest folds them, it never emits them.
    # Family and klass as joulewise.flags.core.CORE_FLAG_CODES gives them.
    **{code: _spec(family, klass) for code, (family, klass) in (
        ("calibration.capture_battery_pair_unverified", ("CALIBRATION", "PHYSICS")),
        ("records.pin_ledger", ("RECORDS", "REPRESENTATION")),
        ("calibration.power_policy_unverified", ("CALIBRATION", "REPRESENTATION")),
        ("instrument.binary_identity_unmeasured", ("INSTRUMENT", "NUMBER")),
        ("env.member_quiet_state_violated", ("MEMBER_VALIDITY", "PHYSICS")),
        ("env.member_guard_flagged", ("DIAGNOSTIC", "REPRESENTATION")),
        ("member.idle_admission_telemetry_missing", ("MEMBER_VALIDITY", "PHYSICS")),
        ("teardown.survivors", ("DIAGNOSTIC", "PHYSICS")),
        ("cooldown.result_unknown", ("DIAGNOSTIC", "PHYSICS")),
        ("env.stage_preflight_not_admitted", ("DIAGNOSTIC", "REPRESENTATION")),
        ("campaign.runner_record_flagged", ("RECORDS", "REPRESENTATION")),
        ("calibration.writer_record_flagged", ("CALIBRATION", "REPRESENTATION")),
    )},
}
# The codes above that only protected-core writers emit (the harvest folds them).
CORE_WRITER_CODES = frozenset({
    "calibration.capture_battery_pair_unverified", "records.pin_ledger", "calibration.power_policy_unverified",
    "instrument.binary_identity_unmeasured", "env.member_quiet_state_violated", "env.member_guard_flagged",
    "member.idle_admission_telemetry_missing", "teardown.survivors", "cooldown.result_unknown",
    "env.stage_preflight_not_admitted", "campaign.runner_record_flagged", "calibration.writer_record_flagged",
})
# joulewise.flags.core.UNWRITTEN_MARKER, read and never imported: a core flag
# whose write failed is printed whole to the stage's stderr behind it (N8).
UNWRITTEN_MARKER = "JOULEWISE_UNWRITTEN_FLAG "
# The producer's own lock (scripts/run_campaign.py acquire_campaign_lock), which
# it creates and removes inside the runs root: no dot before it (sweep V3; it
# was listed as ".campaign.lock").  Spelled in two parts so the emitted-code
# scan of this file does not read a file name as a flag code.
CAMPAIGN_LOCK_NAME = "campaign" ".lock"
LINEAGE_CODES = frozenset(code for code in CODES if code.startswith("lineage."))
NEVER_CLASSIFIED_CODES = frozenset({"records.malformed_flag"})
# Codes L4's draft catalog does not name (handed to L4 and L6 for the draft
# and the sealed catalog).  ``tests/test_harvest_b5_window.py`` keeps this
# list equal to CODES minus the draft whenever joulewise.flags is importable.
L5_ONLY_CODES = frozenset({
    "model.identity_inconsistent_in_window", "model.identity_underivable",
    "calibration.binding_failed", "calibration.ledger_snapshot_refused", "calibration.acceptance_mismatch",
    "calibration.capture_battery_pair_failed",
    # whole_window.not_passed is in L4's draft since the core prune (DISCLOSE, revision 3).
    "whole_window.verdict_absent", "whole_window.verdict_unauthenticated",
    "whole_window.producer_failed",
    "member.unreadable", "member.reduction_mismatch", "member.anchor_recompute_mismatch", "member.span_unknown",
    # battery.accumulator_activity and battery.accumulator_unavailable are in
    # L4's draft since fix lane fx-flags (2026-10-06), with this family and klass.
    "battery.capture_pair_missing",
    *LINEAGE_CODES,
    "roster.run_id_mismatch", "roster.no_science_bundles", "roster.duplicate_run_id",
    "records.monitor_journal_absent", "records.monitor_line_malformed", "records.arm_record_absent",
    "records.terminal_record_absent", "records.source_changed_during_harvest", "records.collector_failed",
    "records.malformed_flag",
    "g3.assertion_failed", "g3.recompute_failed", "g3.not_applicable",
})


def restricted_reason(code: str) -> bool:
    """True for a precheck reason computed from a science energy."""
    return "energy" in code or code.endswith("_metric") or "effect" in code


class HarvestFault(RuntimeError):
    """The program failed on present bytes; cured by R3 and a re-run."""


class NotReady(RuntimeError):
    """The chain's process group is alive or the driver has not finished."""


# ---------------------------------------------------------------------------
# Bytes and JSON.
# ---------------------------------------------------------------------------

def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_bytes())


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """``json.loads`` hook: a duplicated key makes the bytes ambiguous, so refuse them."""
    keys = [key for key, _value in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate JSON key")
    return dict(pairs)


def _corpus_member_status(runs_root: Path | None, member: Any) -> str | None:
    """A NEG-8 corpus member's recorded status, read as the chain's prune step reads it."""
    relative = member.get("bundle_path") if isinstance(member, Mapping) else None
    if runs_root is None or not isinstance(relative, str) or not relative or relative.startswith("/") \
            or ".." in relative.split("/"):
        return None
    try:
        status = read_json(runs_root / relative / "summary_metrics.json").get("status")
    except (OSError, ValueError, AttributeError):
        return None
    return status if isinstance(status, str) else None


def neg8_mint_drops(runs_root: Path | None, committed: Mapping[str, Any],
                    succeeded: Sequence[Any]) -> tuple[dict[str, str], str]:
    """What the core's HAZARD NEG-8 mint drops from the corpus members that succeeded.

    Returns ``({bundle_id: reason}, rule)``, mirroring the chain's
    ``PRUNE_HELPER``: on a HAZARD bound root (the mint's own dispatch,
    ``window_lineage.is_hazard_runs_root``) the core's
    ``whole_window.neg8_corpus_mint_drops`` names, with the predicate each
    failed, the members the mint leaves out of the manifest it binds its bound
    to (core-prune A3).  It is evaluated here on the same bound root over the
    same members (the committed members whose status is ``succeeded``), so the
    harvest accepts exactly the chain's drops.  No drop is authorized (an empty
    map) when the root is not HAZARD (the mint there is all-or-nothing), when
    the core lacks the function, or when it raises; ``rule`` says which.
    """
    try:
        from joulewise import whole_window as ww
        from joulewise import window_lineage
        hazard = runs_root is not None and window_lineage.is_hazard_runs_root(runs_root)
        function = getattr(ww, "neg8_corpus_mint_drops", None)
    except Exception as exc:  # an unusable core authorizes nothing
        return {}, f"unavailable: {type(exc).__name__}"
    if not hazard:
        return {}, "not_hazard"
    if function is None:
        return {}, "unavailable: whole_window.neg8_corpus_mint_drops"
    try:
        with tempfile.TemporaryDirectory() as scratch:
            staged = Path(scratch) / "succeeded-members.json"
            staged.write_bytes((json.dumps({**committed, "members": list(succeeded)}, indent=2, sort_keys=True)
                                + "\n").encode("utf-8"))
            rows = function(Path(runs_root), staged)
        reasons = {row["bundle_id"]: row["reason"] for row in rows}
    except Exception as exc:  # unknown evidence never authorizes an omission
        return {}, f"raised: {type(exc).__name__}"
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in reasons.items()):
        return {}, "raised: malformed drops"
    return reasons, "joulewise.whole_window.neg8_corpus_mint_drops"


def neg8_bound_member_problems(bound: Mapping[str, Any], runs_root: Path) -> list[str]:
    """Each corpus member a NEG-8 bound names, re-checked against its bundle in the bound root.

    The bound's arithmetic and its manifest identity are validated by the
    core; this ties its numbers to the bytes.  For each member: exactly one
    ordinary bundle in ``runs_root`` (``whole_window.ordinary_present_bundle_paths``,
    not a symlink) whose complete file inventory hashes to the recorded
    ``bundle_evidence_sha256``; the mint's per-member predicates hold (custody
    triangle, current strict mint, the bound's canonical condition); and both
    claim-family points re-derive from the bundle by the core's own path
    (``whole_window._reference_energy_evidence``) to the recorded values, to
    the core's tolerance.  Problems name the member, never a number.
    """
    from joulewise import whole_window as ww
    corpus = bound.get("reference_corpus") if isinstance(bound, Mapping) else None
    members = corpus.get("members") if isinstance(corpus, Mapping) else None
    if not isinstance(members, list) or not members:
        return ["bound_names_no_members"]
    problems: list[str] = []
    for member in members:
        bundle_id = member.get("bundle_id") if isinstance(member, Mapping) else None
        paths = ww.ordinary_present_bundle_paths(runs_root, bundle_id) \
            if isinstance(bundle_id, str) and bundle_id else []
        if len(paths) != 1 or paths[0].is_symlink():
            problems.append(f"bound_member_not_one_bundle:{bundle_id}")
            continue
        path = paths[0]
        try:
            digest = ww._bundle_evidence_sha256(path)
        except (OSError, ValueError):
            digest = None
        if digest is None or digest != member.get("bundle_evidence_sha256"):
            problems.append(f"bound_member_bytes_differ:{bundle_id}")
            continue
        try:
            summary = ww._read_json_object(path / "summary_metrics.json")
            metadata = ww._read_json_object(path / "metadata.json")
            identity, canonical = ww._scientific_config_identity(path)
            strict = (not ww._custody_strict_invalid(path, summary, metadata)
                      and ww._current_strict_summary(summary, path))
            gross, idle, problem = ww._reference_energy_evidence(path)
        except Exception:  # a member that cannot be re-derived does not support the bound
            problems.append(f"bound_member_not_rederived:{bundle_id}")
            continue
        if not strict:
            problems.append(f"bound_member_not_strict:{bundle_id}")
        elif identity is None or not canonical or identity != corpus.get("scientific_config_sha256"):
            problems.append(f"bound_member_condition_differs:{bundle_id}")
        elif problem is not None or not isinstance(gross, Mapping) or not _close(
                gross.get("point_j"), member.get("point_gross_j")) \
                or not _close(idle, member.get("point_idle_subtracted_j")):
            problems.append(f"bound_member_energy_differs:{bundle_id}")
    return problems


def _close(fresh: Any, recorded: Any) -> bool:
    """Equal to the tolerance whole_window uses for a stored and a fresh reduction."""
    numbers = (fresh, recorded)
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
           for value in numbers):
        return False
    return math.isclose(float(fresh), float(recorded), rel_tol=1e-9, abs_tol=1e-9)


# Fields of one NEG-8 claim-family record that depend on the bound (or, for
# window_duration_s, on the writer's own reference spans, which the replay
# evaluator does not receive); every other field is fixed by the reference
# bundles alone.
_NEG8_BOUND_DEPENDENT_FIELDS = frozenset({
    "derived_repeatability_bound_j", "screen_passed", "drift_allowance_j", "provenance", "window_duration_s"})


def _neg8_endpoints(bracket: Any) -> dict[str, Any] | None:
    """A NEG-8 bracket's claim families without their bound-dependent fields (None if malformed)."""
    families = bracket.get("claim_families") if isinstance(bracket, Mapping) else None
    if not isinstance(families, Mapping) or not families:
        return None
    endpoints: dict[str, Any] = {}
    for family, record in families.items():
        if not isinstance(record, Mapping):
            return None
        endpoints[family] = {key: value for key, value in record.items() if key not in _NEG8_BOUND_DEPENDENT_FIELDS}
    return endpoints


def _epoch_s(text: Any) -> float | None:
    """An ISO-8601 instant with a zone (the verdict writer's ``utc_timestamp``) as epoch seconds."""
    if not isinstance(text, str) or not text:
        return None
    try:
        moment = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    except ValueError:
        return None
    return moment.timestamp() if moment.tzinfo is not None else None


def verdict_neg8_sources(row: Mapping[str, Any], runs_root: Path) \
        -> tuple[list[Mapping[str, Any]], bool, Mapping[str, Any]] | str:
    """The inputs from which ``validate_whole_window_verdict_row`` re-derives a row's NEG-8 bracket.

    The same selection as the row validator (``whole_window._validate_row_uncached``):
    the row's source campaign manifests, each authenticated by
    ``campaign_provenance.load_authenticated_campaign_manifest`` at its
    recorded SHA-256 and carrying the row's campaign policy; projected by
    ``whole_window._basis_source_manifests`` onto the evaluation basis's
    occurrences when the row has a basis; the current-strict evidence path;
    and the repo-registered bracket policy for the row's policy digest.
    Returns ``(manifests, current, policy)``, or a problem name.
    """
    from joulewise import whole_window as ww
    from joulewise.campaign_provenance import load_authenticated_campaign_manifest
    root = Path(runs_root)
    policy = row.get("campaign_policy")
    policy_sha = policy.get("sha256") if isinstance(policy, Mapping) else None
    registered = ww._registered_bracket_policy(policy_sha)
    if registered is None:
        return "policy_unregistered"
    basis = ww._validated_evaluation_basis(row, root)
    if "evaluation_basis" in row and basis is None:
        return "evaluation_basis_invalid"
    provenance = row.get("row_provenance")
    descriptors = provenance.get("source_campaign_manifests") if isinstance(provenance, Mapping) else None
    if not isinstance(descriptors, list) or not descriptors:
        return "source_manifests_unrecorded"
    verified: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []
    manifests: list[Mapping[str, Any]] = []
    seen: set[str] = set()
    for descriptor in descriptors:
        text = descriptor.get("path") if isinstance(descriptor, Mapping) else None
        path = ww._safe_source_path(root, text)
        if path is None or text in seen:
            return "source_manifest_path_invalid"
        seen.add(text)
        record = load_authenticated_campaign_manifest(root, path, root / "campaign_log.jsonl")
        if record is None or sha256_bytes(record.raw_bytes) != descriptor.get("sha256"):
            return "source_manifest_unauthenticated"
        manifest_policy = record.value.get("campaign_policy")
        if not isinstance(manifest_policy, Mapping) or manifest_policy.get("sha256") != policy_sha:
            return "source_manifest_policy_differs"
        verified.append((descriptor, record.value))
        if basis is None:
            if ww._manifest_members(record.value, root) is None:
                return "source_manifest_members_invalid"
            manifests.append(record.value)
    if basis is not None:
        projected = ww._basis_source_manifests(basis=basis, verified_sources=verified, row=row, runs_root=root)
        if projected is None:
            return "evaluation_basis_projection_failed"
        current = False
        for occurrence in basis.get("member_occurrences", []):
            path = ww._safe_source_path(root, occurrence.get("bundle_path")) \
                if isinstance(occurrence, Mapping) else None
            if path is not None and ww._current_strict_summary(ww._read_json_object(path / "summary_metrics.json"),
                                                                path):
                current = True
                break
        return projected, current, registered
    bundle_ids = row.get("bundle_ids")
    referenced = {item for item in bundle_ids if isinstance(item, str)} if isinstance(bundle_ids, list) else set()
    current = ww._row_references_current_strict_member(row, root, referenced)
    if not current:  # the row validator replays such a row on the frozen gross-only bracket, which has no bound
        return "not_point_drift"
    return manifests, current, registered


def _fsync_dir(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def write_once(path: Path, raw: bytes) -> str:
    """Create ``path`` exclusively, fsync it and its directory; return sha256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_dir(path.parent)
    return sha256_bytes(raw)


def write_json_once(path: Path, value: Any) -> str:
    return write_once(path, (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode())


def write_jsonl_once(path: Path, rows: Iterable[Mapping[str, Any]]) -> str:
    """One canonical JSON object per line, each line fsynced as written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with path.open("xb") as handle:
        for row in rows:
            line = canonical_json_bytes(row) + b"\n"
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
            digest.update(line)
    _fsync_dir(path.parent)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Flag records (joulewise.flag.v1, plan section 3.1) and the catalog.
# ---------------------------------------------------------------------------

# The record is lane L4's ``joulewise.flags.schema`` form of plan section 3.1:
# the plan's fourteen fields plus ``schema_version``, and a flag_id that also
# covers the interval (two intervals are two facts).
FLAG_KEYS = frozenset({"schema_version", "flag_id", "code", "family", "klass", "scope", "interval", "source",
                       "observed", "expected", "evidence", "detail", "emitted", "catalog_sha256", "blinding"})
SCOPE_KEYS = ("level", "plan_id", "attempt", "stage_id", "run_id", "bundle_id")
INTERVAL_KEYS = ("monotonic_ns", "monotonic_raw_ns", "wall_s")
SOURCE_KEYS = ("stage", "collector", "legacy_site", "legacy_code")
EMITTED_KEYS = ("wall_s", "monotonic_ns", "boot_session_uuid")
LEVELS = ("window", "stage", "quad", "member")
STAGES = ("desk", "arm", "window", "harvest")
CODE_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$")
NULL_INTERVAL = {"monotonic_ns": None, "monotonic_raw_ns": None, "wall_s": None}


def default_flag_id(code: str, scope: Mapping[str, Any], observed: Any, source: Mapping[str, Any],
                    interval: Mapping[str, Any] | None = None) -> str:
    """``sha256(canonical({code, scope, observed, source, interval}))[:20]``, the dedup key.

    Identical to L4's ``joulewise.flags.schema.compute_flag_id``.
    """
    return sha256_bytes(canonical_json_bytes(
        {"code": code, "scope": dict(scope), "observed": observed, "source": dict(source),
         "interval": dict(interval) if interval is not None else dict(NULL_INTERVAL)}))[:20]


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return _is_int(value) or (isinstance(value, float) and math.isfinite(value))


def _pair_problem(value: Any, where: str, integer: bool) -> list[str]:
    check = _is_int if integer else _is_number
    if value is None or (isinstance(value, list) and len(value) == 2 and all(check(item) for item in value)
                         and value[0] <= value[1]):
        return []
    return [f"{where} must be null or an ordered pair [a, b]"]


def flag_problems(value: Any) -> list[str]:
    """Every ``joulewise.flag.v1`` problem in ``value`` (empty: it conforms).

    The rules of L4's ``joulewise.flags.schema.validate_flag``, which owns the
    schema; the tests compare the two whenever L4 is importable.
    """
    if not isinstance(value, Mapping):
        return ["flag must be a JSON object"]
    missing = sorted(FLAG_KEYS - set(value))
    extra = sorted(set(value) - FLAG_KEYS)
    if missing or extra:
        return [f"missing fields: {missing}"] * bool(missing) + [f"unknown fields: {extra}"] * bool(extra)
    problems: list[str] = []
    if value["schema_version"] != FLAG_SCHEMA:
        problems.append(f"schema_version must be {FLAG_SCHEMA}")
    if not isinstance(value["code"], str) or CODE_RE.fullmatch(value["code"]) is None:
        problems.append("code must be dotted lower-case")
    if value["family"] not in FAMILIES:
        problems.append("family is unknown")
    if value["klass"] not in KLASSES:
        problems.append("klass is unknown")
    if value["blinding"] not in (STRUCTURE, RESTRICTED):
        problems.append("blinding is unknown")
    scope = value["scope"]
    if not isinstance(scope, Mapping) or set(scope) != set(SCOPE_KEYS):
        problems.append(f"scope must have exactly {SCOPE_KEYS}")
    else:
        if scope["level"] not in LEVELS:
            problems.append("scope.level is unknown")
        for key in ("plan_id", "stage_id", "run_id", "bundle_id"):
            if scope[key] is not None and not isinstance(scope[key], str):
                problems.append(f"scope.{key} must be a string or null")
        if scope["attempt"] is not None and not isinstance(scope["attempt"], str) and not _is_int(scope["attempt"]):
            problems.append("scope.attempt must be a string, integer or null")
        if scope["level"] == "member" and not scope["run_id"]:
            problems.append("a member-level flag needs scope.run_id")
        if scope["level"] == "stage" and not scope["stage_id"]:
            problems.append("a stage-level flag needs scope.stage_id")
    interval = value["interval"]
    if not isinstance(interval, Mapping) or set(interval) != set(INTERVAL_KEYS):
        problems.append(f"interval must have exactly {INTERVAL_KEYS}")
    else:
        problems += _pair_problem(interval["monotonic_ns"], "interval.monotonic_ns", True)
        problems += _pair_problem(interval["monotonic_raw_ns"], "interval.monotonic_raw_ns", True)
        problems += _pair_problem(interval["wall_s"], "interval.wall_s", False)
    source = value["source"]
    if not isinstance(source, Mapping) or set(source) != set(SOURCE_KEYS):
        problems.append(f"source must have exactly {SOURCE_KEYS}")
    else:
        if source["stage"] not in STAGES:
            problems.append("source.stage is unknown")
        if not isinstance(source["collector"], str) or not source["collector"]:
            problems.append("source.collector must be a nonempty string")
        for key in ("legacy_site", "legacy_code"):
            if source[key] is not None and not isinstance(source[key], str):
                problems.append(f"source.{key} must be a string or null")
    evidence = value["evidence"]
    if not isinstance(evidence, list) or any(
            not isinstance(item, Mapping) or set(item) != {"path", "sha256"} or not isinstance(item["path"], str)
            or not item["path"] or item["path"].startswith("/") or ".." in item["path"].split("/")
            or not _is_sha256(item["sha256"]) for item in evidence):
        problems.append("evidence must be [{path relative to custody, sha256}]")
    if not isinstance(value["detail"], str) or "\n" in value["detail"]:
        problems.append("detail must be one line of text")
    emitted = value["emitted"]
    if not isinstance(emitted, Mapping) or set(emitted) != set(EMITTED_KEYS) or not _is_number(emitted["wall_s"]) \
            or not _is_int(emitted["monotonic_ns"]) or not (emitted["boot_session_uuid"] is None
                                                            or isinstance(emitted["boot_session_uuid"], str)):
        problems.append(f"emitted must have exactly {EMITTED_KEYS} with numeric clocks")
    if value["catalog_sha256"] is not None and not _is_sha256(value["catalog_sha256"]):
        problems.append("catalog_sha256 must be a SHA-256 or null")
    try:
        canonical_json_bytes({"observed": value["observed"], "expected": value["expected"]})
    except (TypeError, ValueError):
        return problems + ["observed/expected must be finite JSON"]
    if not isinstance(value["flag_id"], str) or re.fullmatch(r"[0-9a-f]{20}", value["flag_id"]) is None:
        problems.append("flag_id must be 20 lower-case hex characters")
    elif not problems and value["flag_id"] != default_flag_id(value["code"], scope, value["observed"], source,
                                                               interval):
        problems.append("flag_id does not match canonical(code, scope, observed, source, interval)")
    return problems


@dataclasses.dataclass(frozen=True)
class Catalog:
    """The sealed catalog: code -> {family, klass, effect}.  Never decided here."""

    path: str | None
    sha256: str | None
    entries: Mapping[str, Mapping[str, Any]]
    raw: Any = None

    @staticmethod
    def load(path: Path | str | None) -> "Catalog":
        if path is None or not Path(path).is_file():
            return Catalog(str(path) if path is not None else None, None, {}, None)
        raw_bytes = Path(path).read_bytes()
        value = json.loads(raw_bytes)
        entries: dict[str, Mapping[str, Any]] = {}
        table = value.get("codes", value.get("flags", value.get("entries"))) if isinstance(value, Mapping) else value
        if table is None and isinstance(value, Mapping):
            table = {key: item for key, item in value.items() if isinstance(item, Mapping)}
        if isinstance(table, Mapping):
            entries = {str(key): item for key, item in table.items() if isinstance(item, Mapping)}
        elif isinstance(table, list):
            entries = {str(item["code"]): item for item in table
                       if isinstance(item, Mapping) and isinstance(item.get("code"), str)}
        return Catalog(str(path), sha256_bytes(raw_bytes), entries, value)

    def effect(self, code: str) -> str:
        entry = self.entries.get(code)
        effect = entry.get("effect") if isinstance(entry, Mapping) else None
        return effect if effect in EFFECTS else UNCLASSIFIED


class FlagLedger:
    """Every flag of one harvest, deduplicated by ``flag_id``, in emission order."""

    def __init__(self, *, plan_id: str | None, attempt: Any, catalog: Catalog,
                 boot_session_uuid: str | None, flag_id: Callable[..., str] = default_flag_id,
                 now: Callable[[], float] = time.time, monotonic_ns: Callable[[], int] = time.monotonic_ns):
        self.plan_id, self.attempt, self.catalog = plan_id, attempt, catalog
        self._boot, self._flag_id, self._now, self._mono = boot_session_uuid, flag_id, now, monotonic_ns
        self._records: dict[str, dict[str, Any]] = {}

    def emit(self, code: str, *, level: str, collector: str, run_id: str | None = None,
             stage_id: str | None = None, bundle_id: str | None = None, observed: Any = None,
             expected: Any = None, evidence: Sequence[Mapping[str, str]] = (), detail: str = "",
             interval: Mapping[str, Any] | None = None, stage: str = "harvest",
             legacy_code: str | None = None, blinding: str | None = None,
             spec: CodeSpec | None = None) -> dict[str, Any]:
        # ``spec`` only for a code another lane's collector names that this
        # harvest does not list yet; the catalog leaves it UNCLASSIFIED.
        spec = spec if spec is not None and code not in CODES else CODES[code]
        catalog_entry = self.catalog.entries.get(code, {})
        family = catalog_entry.get("family") if catalog_entry.get("family") in FAMILIES else spec.family
        klass = catalog_entry.get("klass") if catalog_entry.get("klass") in KLASSES else spec.klass
        scope = {"level": level, "plan_id": self.plan_id, "attempt": self.attempt, "stage_id": stage_id,
                 "run_id": run_id, "bundle_id": bundle_id if bundle_id is not None else run_id}
        source = {"stage": stage, "collector": collector, "legacy_site": spec.legacy, "legacy_code": legacy_code}
        interval_value = {**NULL_INTERVAL, **(interval or {})}
        record = {
            "schema_version": FLAG_SCHEMA,
            "flag_id": self._flag_id(code, scope, observed, source, interval_value),
            "code": code, "family": family, "klass": klass, "scope": scope,
            "interval": interval_value,
            "source": source, "observed": observed, "expected": expected,
            "evidence": [dict(item) for item in evidence],
            "detail": " ".join(str(detail).split())[:300],
            "emitted": {"wall_s": self._now(), "monotonic_ns": self._mono(), "boot_session_uuid": self._boot},
            "catalog_sha256": self.catalog.sha256,
            "blinding": blinding or spec.blinding,
        }
        canonical_json_bytes(record)  # JSON-safe or raise now, at the emitter
        return self._records.setdefault(record["flag_id"], record)

    def absorb(self, record: Any) -> list[str]:
        """Merge a flag written earlier (desk, arm, driver) by its own writer.

        Returns the record's schema problems; a record with problems is not
        merged (the caller records it as ``records.malformed_flag``).
        """
        problems = flag_problems(record)
        if not problems:
            self._records.setdefault(record["flag_id"], dict(record))
        return problems

    @property
    def records(self) -> list[dict[str, Any]]:
        return list(self._records.values())


# ---------------------------------------------------------------------------
# Inputs: the window plan plus explicit overrides.
# ---------------------------------------------------------------------------

_PLAN_CONTAINERS = ((), ("hazard_window",), ("hazard_window", "bindings"), ("hazard_window", "pack"),
                    ("hazard_window", "bracket_session"), ("bindings",), ("launch_bindings",),
                    ("hazard_window", "launch_bindings"), ("pack",), ("pack_night",))


def _plan_value(plan: Mapping[str, Any], *names: str) -> Any:
    """First value of any ``names`` in the plan's known containers (L2 seam)."""
    for container in _PLAN_CONTAINERS:
        node: Any = plan
        for key in container:
            node = node.get(key) if isinstance(node, Mapping) else None
        if not isinstance(node, Mapping):
            continue
        for name in names:
            value = node.get(name)
            if value is not None and not isinstance(value, Mapping):
                return value
    return None


@dataclasses.dataclass
class WindowInputs:
    plan_path: Path
    plan: Mapping[str, Any]
    plan_id: str | None
    attempt: Any
    custody_root: Path
    night_dir: Path
    measurement_root: Path
    pack_root: Path
    pack_id: str
    claim_runs_root: Path
    bound_runs_root: Path | None
    chain_path: Path | None
    chain_sha256_path: Path | None
    ledger_path: Path
    head_pin_path: Path
    acceptance_path: Path | None
    bracket_session_id: str | None
    pre_attempt_id: str | None
    post_attempt_id: str | None
    h_claim: str | None
    sealed_inventory_path: Path | None
    executed_inventory_path: Path | None
    catalog_path: Path | None
    identity_pins_path: Path | None
    monitor_dir: Path
    arm_record_path: Path
    flags_dir: Path
    thresholds: dict[str, Any]
    # Where each threshold came from, the registration read, and every
    # problem; each problem is a recorded harvest fault.
    thresholds_provenance: dict[str, Any] = dataclasses.field(default_factory=dict)
    registration_path: Path | None = None


def parse_registration_thresholds(raw: bytes) -> dict[str, Any]:
    """The flat JSON block under the registration's "Harvest thresholds" heading (section 6.9).

    Exactly one such heading; the first ```json fence after it and before
    the next heading.  Raises ValueError naming what is wrong.
    """
    text = raw.decode("utf-8")
    headings = list(_THRESHOLD_HEADING_RE.finditer(text))
    if len(headings) != 1:
        raise ValueError(f"expected one 'Harvest thresholds' heading, found {len(headings)}")
    start = headings[0].end()
    following = _ANY_HEADING_RE.search(text, start)
    section = text[start:following.start() if following else len(text)]
    fence = _JSON_FENCE_RE.search(section)
    if fence is None:
        raise ValueError("no ```json block under the 'Harvest thresholds' heading")
    value = json.loads(fence.group(1), object_pairs_hook=_unique_pairs)
    if not isinstance(value, dict):
        raise ValueError("the harvest-threshold block is not a JSON object")
    return value


def _threshold_problem(key: str, value: Any) -> str | None:
    if key in INTEGER_THRESHOLD_KEYS:
        return None if _is_int(value) and value >= 1 else f"invalid:{key}:must be an integer >= 1"
    return None if _is_number(value) and value > 0 else f"invalid:{key}:must be a finite number > 0"


def resolve_thresholds(plan: Mapping[str, Any], measurement_root: Path, *,
                       registration_override: Path | str | None = None,
                       overrides: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """The registered harvest thresholds and their provenance (registration 6.9).

    Sources, both registered: the registration the plan names (its bytes must
    hash to the digest the plan recorded) and the plan's flat copy.  An
    explicit override (``--thresholds``) never replaces a registered value;
    one that differs from it, or that supplies a key no registered source
    gives, is a problem.  Every problem is a harvest fault; a missing or
    invalid key is left out of the values, so the step that needs it faults.
    """
    hazard = plan.get("hazard_window") if isinstance(plan.get("hazard_window"), Mapping) else {}
    problems: list[str] = []
    sources: dict[str, Mapping[str, Any]] = {}
    recorded = hazard.get("registration") if isinstance(hazard.get("registration"), Mapping) else {}
    recorded_sha = recorded.get("sha256") if _is_sha256(recorded.get("sha256")) else None
    named = registration_override or recorded.get("path") or plan.get("registration_path")
    registration: dict[str, Any] = {"path": None, "sha256": None, "recorded_sha256": recorded_sha}
    if isinstance(named, (str, Path)) and str(named):
        path = Path(named)
        path = path if path.is_absolute() else measurement_root / path
        registration["path"] = str(path)
        try:
            raw = path.read_bytes()
        except OSError as exc:
            problems.append(f"registration_unreadable:{type(exc).__name__}")
        else:
            registration["sha256"] = sha256_bytes(raw)
            if recorded_sha is not None and registration["sha256"] != recorded_sha:
                # Not the bytes the plan was written from: not a registered source.
                problems.append("registration_digest_differs_from_plan")
            else:
                try:
                    sources["registration"] = parse_registration_thresholds(raw)
                except (UnicodeDecodeError, ValueError) as exc:
                    problems.append(f"registration_block_unreadable:{str(exc)[:120]}")
    plan_block = hazard.get(PLAN_HARVEST_THRESHOLDS_KEY, plan.get(PLAN_HARVEST_THRESHOLDS_KEY))
    if plan_block is not None:
        if isinstance(plan_block, Mapping):
            sources["plan"] = plan_block
        else:
            problems.append("plan_harvest_thresholds_not_an_object")
    if not sources and not problems:
        problems.append("harvest_thresholds_unregistered")
    for name, block in sources.items():
        unknown = sorted(set(block) - set(HARVEST_THRESHOLD_KEYS))
        if unknown:
            problems.append(f"unknown_keys:{name}:{','.join(unknown)}")
    values: dict[str, Any] = {}
    key_sources: dict[str, list[str]] = {}
    for key in HARVEST_THRESHOLD_KEYS:
        given = {name: block[key] for name, block in sources.items() if key in block}
        if not given:
            continue
        if len({canonical_json_bytes(value) for value in given.values()}) > 1:
            problems.append(f"sources_disagree:{key}")
        values[key] = given.get("registration", next(iter(given.values())))
        key_sources[key] = sorted(given)
    for key, value in (overrides or {}).items():
        if key not in HARVEST_THRESHOLD_KEYS:
            problems.append(f"override_unknown_key:{key}")
        elif key in values:
            if canonical_json_bytes(value) != canonical_json_bytes(values[key]):
                problems.append(f"override_differs_from_registered:{key}")  # the registered value stands
        else:
            values[key] = value
            key_sources[key] = ["override"]
            problems.append(f"override_supplies_unregistered:{key}")
    for key in HARVEST_THRESHOLD_KEYS:
        if key not in values:
            problems.append(f"missing:{key}")
            continue
        problem = _threshold_problem(key, values[key])
        if problem is not None:
            problems.append(problem)
            del values[key]
    provenance = {"schema": THRESHOLDS_SCHEMA, "values": dict(values), "key_sources": key_sources,
                  "sources": sorted(sources), "registration": registration, "problems": problems}
    return values, provenance


def resolve_inputs(plan_path: Path | str, overrides: Mapping[str, Any] | None = None) -> WindowInputs:
    """Resolve every input path from the plan, letting explicit overrides win."""
    overrides = {key: value for key, value in (overrides or {}).items() if value is not None}
    plan_path = Path(plan_path).absolute()
    plan = read_json(plan_path)
    if not isinstance(plan, Mapping):
        raise HarvestFault("plan_not_an_object")

    def pick(name: str, *keys: str) -> Any:
        return overrides[name] if name in overrides else _plan_value(plan, *(keys or (name,)))

    def path(name: str, *keys: str, base: Path | None = None) -> Path | None:
        value = pick(name, *keys)
        if value is None:
            return None
        result = Path(str(value))
        return result if result.is_absolute() or base is None else base / result

    custody = path("custody_root") or plan_path.parent
    measurement = path("measurement_root", "measurement_root", "repo_root")
    if measurement is None:
        raise HarvestFault("input_unresolved:measurement_root")
    pack_root = path("pack_root", "pack_root", "root", base=measurement)
    pack_id = pick("pack_id")
    if pack_root is None and isinstance(pack_id, str):
        pack_root = measurement / "configs" / "campaigns" / pack_id
    if pack_root is None:
        raise HarvestFault("input_unresolved:pack_root")
    claim = path("claim_runs_root")
    if claim is None:
        raise HarvestFault("input_unresolved:claim_runs_root")
    thresholds, thresholds_provenance = resolve_thresholds(
        plan, measurement, registration_override=overrides.get("registration_path"),
        overrides=overrides.get("thresholds"))
    registration = thresholds_provenance["registration"]["path"]
    session = pick("bracket_session_id", "bracket_session_id", "session_id")
    return WindowInputs(
        plan_path=plan_path, plan=plan, plan_id=pick("plan_id"), attempt=pick("attempt"),
        custody_root=custody, night_dir=custody / "night", measurement_root=measurement,
        pack_root=pack_root, pack_id=str(pack_id or pack_root.name), claim_runs_root=claim,
        bound_runs_root=path("bound_runs_root"),
        chain_path=path("chain_path"), chain_sha256_path=path("chain_sha256_path"),
        ledger_path=path("ledger_path") or measurement / "runs" / "calibration_observation_ledger.jsonl",
        head_pin_path=path("head_pin_path", "head_pin_path", "head_pin")
        or measurement / "configs" / "calibration" / "calibration_ledger_head.json",
        acceptance_path=path("acceptance_path", "acceptance_path", base=measurement),
        bracket_session_id=session if isinstance(session, str) else None,
        pre_attempt_id=pick("pre_attempt_id"), post_attempt_id=pick("post_attempt_id"),
        h_claim=pick("h_claim", "h_claim", "measurement_head"),
        # L6 seals the inventory beside the catalog; L2's driver writes the
        # arm-time inventory as night/executed_inventory.json.
        sealed_inventory_path=path("sealed_inventory_path", "sealed_inventory_path", "sealed_inventory",
                                   base=measurement) or measurement / SEALED_DIRECTORY / "sealed_inventory.json",
        executed_inventory_path=path("executed_inventory_path", "executed_inventory_path",
                                     "executed_inventory", base=custody)
        or custody / "night" / "executed_inventory.json",
        catalog_path=path("catalog_path", "catalog_path", "flag_catalog", base=measurement)
        or measurement / SEALED_DIRECTORY / "flag_catalog.json",
        identity_pins_path=path("identity_pins_path", base=measurement)
        or measurement / SEALED_DIRECTORY / "identity_pins.json",
        monitor_dir=path("monitor_dir") or custody / "hazards" / "monitor",
        arm_record_path=path("arm_record_path") or custody / "hazards" / "arm.json",
        flags_dir=path("flags_dir") or custody / "flags",
        thresholds=thresholds,
        thresholds_provenance=thresholds_provenance,
        registration_path=Path(registration) if registration else None,
    )


# ---------------------------------------------------------------------------
# Archive: an APFS clone where possible, verified byte for byte.
# ---------------------------------------------------------------------------

def tree_inventory(root: Path) -> dict[str, dict[str, Any]]:
    """Relative path -> {sha256, size} for every regular file; links kept literal."""
    rows: dict[str, dict[str, Any]] = {}
    if root.is_file():
        return {".": {"sha256": sha256_file(root), "size": root.stat().st_size}}
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            rows[name] = {"link": os.readlink(path)}
        elif path.is_file():
            rows[name] = {"sha256": sha256_file(path), "size": path.stat().st_size}
    return rows


def clone_tree(source: Path, target: Path) -> None:
    """``cp -c`` uses clonefile(2) and falls back to a byte copy across volumes."""
    target.parent.mkdir(parents=True, exist_ok=True)
    cp = Path("/bin/cp")
    if cp.exists() and sys.platform == "darwin":
        result = subprocess.run([str(cp), "-c", "-pR", str(source), str(target)],
                                capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return
        if target.is_dir() and not target.is_symlink():  # a partial copy must not block the fallback
            shutil.rmtree(target)
        elif target.exists() or target.is_symlink():
            target.unlink()
    if source.is_dir():
        shutil.copytree(source, target, symlinks=True)
    else:
        shutil.copy2(source, target)


def archive_sources(sources: Mapping[str, Path], destination: Path, *,
                    clone: Callable[[Path, Path], None] = clone_tree) -> dict[str, dict[str, Any]]:
    """Copy each source under ``destination/sources/<name>`` and prove the copy."""
    original: dict[str, dict[str, Any]] = {}
    for name, source in sources.items():
        if not source.exists():
            continue
        original[name] = tree_inventory(source)
        target = destination / "sources" / name
        clone(source, target)
        if tree_inventory(target) != original[name]:
            raise HarvestFault(f"archive_copy_mismatch:{name}")
    lines = "".join(f"{row['sha256']}  {name}{'' if rel == '.' else '/' + rel}\n"
                    for name, rows in original.items() for rel, row in rows.items() if "sha256" in row)
    write_once(destination / "sources" / "SHA256SUMS", lines.encode())
    return original


# ---------------------------------------------------------------------------
# Roster: members, their cells and units, from the preserved pack bytes.
# ---------------------------------------------------------------------------

def _resolve_repo_path(relative: str, pack_root: Path, repo_root: Path) -> Path:
    return repo_root / relative if relative.startswith("configs/") else pack_root / relative


def _condition_tag(config: Mapping[str, Any]) -> str | None:
    tags = config.get("run_metadata", {}).get("tags", []) if isinstance(config.get("run_metadata"), Mapping) else []
    for tag in tags if isinstance(tags, list) else []:
        if isinstance(tag, str) and tag.startswith("df-condition="):
            return tag.split("=", 1)[1]
    return None


def _family_workload(definition: Any) -> Mapping[str, Any]:
    if not isinstance(definition, Mapping):
        return {}
    for item in definition.values():
        inner = item.get("condition_family_definition") if isinstance(item, Mapping) else None
        workload = inner.get("workload_profile") if isinstance(inner, Mapping) else None
        if isinstance(workload, Mapping):
            return workload
    return {}


def build_roster(pack_root: Path, repo_root: Path) -> dict[str, Any]:
    """Every planned member with the cells it feeds and its unit in each.

    Floor packs name cells in ``extraction_spec.json`` (absolute cells list
    repeats; comparative cells list quads as blocks).  The contrast pack names
    them in ``analysis_manifest_v3.json`` contrasts.  A quad member's unit is its
    block, so one flagged member removes the whole quad (plan section 3.5).
    """
    tree = read_json(pack_root / "plan_tree.json")
    members: dict[str, dict[str, Any]] = {}
    for row in tree.get("science", []):
        run_id = row["run_id"]
        members[run_id] = {
            "run_id": run_id, "kind": "science", "ordinal": row.get("ordinal"),
            "stage_id": row.get("stage_id"), "role": row.get("role"), "block_id": row.get("block_id"),
            "position": row.get("position"), "arm": row.get("arm"),
            "config_path": row.get("config_path"), "config_sha256": row.get("config_sha256"),
            "cells": [],
        }
    # A run id listed twice (two science rows, two external inputs, or both)
    # is one roster member; every listing is kept here for the
    # roster.duplicate_run_id flag (rehearsal round 1, B3).
    listings: dict[str, list[str]] = {}
    for row in tree.get("science", []):
        listings.setdefault(row["run_id"], []).append(f"science:{row.get('stage_id')}")
    external = tree.get("external_inputs")
    manifests = external.get("manifests", []) if isinstance(external, Mapping) else (external or [])
    for manifest in manifests:
        input_id = manifest.get("external_input_id") or manifest.get("input_id")
        for row in manifest.get("members", []):
            listings.setdefault(row["run_id"], []).append(f"external_input:{input_id}")
            members.setdefault(row["run_id"], {
                "run_id": row["run_id"], "kind": "auxiliary", "ordinal": row.get("ordinal"),
                "stage_id": input_id, "role": input_id, "block_id": None, "position": None, "arm": None,
                "config_path": row.get("path"), "config_sha256": row.get("sha256"), "cells": [],
            })
    cells: list[dict[str, Any]] = []

    def attach(run_id: str, cell: Mapping[str, Any], unit_kind: str, unit_id: str) -> None:
        member = members.get(run_id)
        if member is None:
            return
        member["cells"].append({"cell_id": cell["cell_id"], "unit_kind": unit_kind, "unit_id": unit_id,
                                "target_precheck_path": cell.get("target_precheck_path"),
                                "registered_workload": cell.get("registered_workload", {})})

    spec_path = pack_root / "extraction_spec.json"
    manifest_path = pack_root / "analysis_manifest_v3.json"
    if spec_path.is_file():
        for cell in read_json(spec_path).get("cells", []):
            entry = {"cell_id": cell["cell_id"], "kind": cell.get("kind"),
                     "target_precheck_path": cell.get("target_precheck_path"),
                     "condition_family_id": cell.get("condition_family_id"), "expected_n": cell.get("expected_n"),
                     "registered_workload": dict(_family_workload(cell.get("condition_family_definitions")))}
            cells.append(entry)
            for member in cell.get("members", []) or []:
                attach(member.get("bundle_id"), entry, "repeat", member.get("bundle_id"))
            for block in cell.get("blocks", []) or []:
                for run_id in (block.get("members") or {}).values():
                    attach(run_id, entry, "quad", block["block_id"])
    elif manifest_path.is_file():
        for contrast in read_json(manifest_path).get("contrasts", []):
            entry = {"cell_id": contrast["contrast_id"], "kind": "contrast",
                     "target_precheck_path": contrast.get("target_precheck_path"),
                     "condition_family_id": None, "expected_n": len(contrast.get("block_ids", [])),
                     "registered_workload": {}}
            cells.append(entry)
            for member in contrast.get("members", []):
                attach(member["run_id"], entry, "quad", member["block_id"])
    else:  # Fallback from the plan tree's own roles.
        fallback: dict[str, dict[str, Any]] = {}
        for member in members.values():
            if member["kind"] != "science":
                continue
            unit_kind = "repeat" if member["role"] == "absolute_repeat" else "quad"
            cell = fallback.setdefault(f"{member['stage_id']}", {
                "cell_id": f"{member['stage_id']}", "kind": "absolute" if unit_kind == "repeat" else "comparative",
                "target_precheck_path": None, "condition_family_id": None, "expected_n": None,
                "registered_workload": {}})
            attach(member["run_id"], cell, unit_kind, member["run_id"] if unit_kind == "repeat" else member["block_id"])
        cells.extend(fallback.values())
    for member in members.values():
        relative = member.get("config_path")
        if isinstance(relative, str):
            config_path = _resolve_repo_path(relative, pack_root, repo_root)
            try:
                member["condition_family_id"] = _condition_tag(read_json(config_path))
            except (OSError, ValueError):
                member["condition_family_id"] = None
    # Target cells (registration 0.9 and 6.6): a floor member's target phase
    # is the phase of its own condition family, the ``df-condition`` tag of its
    # config (decode members: phase.decode; p2048 members: phase.prefill).  A
    # floor cell whose family is no feeding member's own -- the p42 cells,
    # read from the decode members' prefill -- is not a target cell: its
    # precheck is no member's target-phase precheck and its unit count is not
    # under the minimum.  A member whose own family cannot be read keeps every
    # cell it feeds as a target (the stricter reading).  Contrast cells and
    # fallback cells are target cells.
    for cell in cells:
        target = True
        if cell.get("kind") in ("absolute", "comparative") and isinstance(cell.get("condition_family_id"), str):
            own = [member.get("condition_family_id") for member in members.values()
                   if any(item["cell_id"] == cell["cell_id"] for item in member["cells"])]
            target = (not own) or any(tag is None for tag in own) or cell["condition_family_id"] in own
        cell["target"] = target
    target_of = {cell["cell_id"]: cell["target"] for cell in cells}
    for member in members.values():
        for item in member["cells"]:
            item["target"] = target_of.get(item["cell_id"], True)
    return {"schema": ROSTER_SCHEMA, "pack_id": pack_root.name,
            "plan_tree_sha256": sha256_file(pack_root / "plan_tree.json"),
            "window_identity": tree.get("window_identity"), "plan": tree.get("plan"),
            "campaign_policy": tree.get("campaign_policy"), "acceptance_policy": tree.get("acceptance_policy"),
            "duplicate_listings": {run_id: places for run_id, places in sorted(listings.items()) if len(places) > 1},
            "cells": cells, "members": sorted(members.values(), key=lambda m: (m["kind"] != "science",
                                                                              m.get("ordinal") or 0, m["run_id"]))}


def _stage_runs_root_binding(stage: Mapping[str, Any]) -> str | None:
    """The binding a collection stage passes to ``--runs-dir`` (claim_runs_root or bound_runs_root)."""
    commands = (stage.get("launch") or {}).get("commands") if isinstance(stage.get("launch"), Mapping) else None
    for command in commands if isinstance(commands, list) else []:
        template = command.get("argv_template") if isinstance(command, Mapping) else None
        arguments = template.get("arguments") if isinstance(template, Mapping) else None
        arguments = arguments if isinstance(arguments, list) else []
        for flag, value in zip(arguments, arguments[1:]):
            if isinstance(flag, Mapping) and flag.get("kind") == "literal" and flag.get("value") == "--runs-dir" \
                    and isinstance(value, Mapping) and value.get("kind") == "binding":
                return value.get("value") if isinstance(value.get("value"), str) else None
    return None


def stage_dispatches(tree: Mapping[str, Any], pack_root: Path) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    """Every run id the plan tree's collection stages launch, stage by stage, with the runs root.

    A stage's members are its ``input_ref``'s: an external input's member
    rows, or a pack manifest's ``executed_order``.  run_campaign skips a run
    id whose complete bundle already exists in its runs root, so a run id two
    stages launch into one root is measured once and its later planned
    positions are never measured (rehearsal round 1, B3).  Returns
    ``({run_id: [{stage_id, ordinal, runs_root}]}, [stages whose members could not be read])``.
    """
    external = tree.get("external_inputs")
    manifests = external.get("manifests", []) if isinstance(external, Mapping) else (external or [])
    inputs = {str(row.get("input_id") or row.get("external_input_id")): row
              for row in manifests if isinstance(row, Mapping)}
    dispatches: dict[str, list[dict[str, Any]]] = {}
    unresolved: list[str] = []
    for stage in tree.get("stage_graph") or []:
        if not isinstance(stage, Mapping) or stage.get("kind") != "campaign_collection":
            continue
        reference = stage.get("input_ref") if isinstance(stage.get("input_ref"), Mapping) else {}
        run_ids: list[Any] | None = None
        if reference.get("kind") == "external_input":
            members = (inputs.get(str(reference.get("input_id"))) or {}).get("members")
            if isinstance(members, list):
                run_ids = [row.get("run_id") for row in members if isinstance(row, Mapping)]
        elif reference.get("kind") == "pack_manifest" and isinstance(reference.get("path"), str):
            try:
                rows = read_json(pack_root / reference["path"]).get("executed_order")
                run_ids = [row.get("run_id") for row in rows if isinstance(row, Mapping)] \
                    if isinstance(rows, list) else None
            except (OSError, ValueError, AttributeError):
                run_ids = None
        if run_ids is None or not all(isinstance(run_id, str) and run_id for run_id in run_ids):
            unresolved.append(str(stage.get("stage_id")))
            continue
        for run_id in run_ids:
            dispatches.setdefault(run_id, []).append({"stage_id": stage.get("stage_id"),
                                                      "ordinal": stage.get("ordinal"),
                                                      "runs_root": _stage_runs_root_binding(stage)})
    return dispatches, unresolved


def pinned_files(tree: Any, *, pack_root: Path, repo_root: Path) -> list[dict[str, str]]:
    """Every (relative path, sha256) pair the plan tree pins, deduplicated."""
    seen: dict[str, str] = {}
    conflicts: list[dict[str, str]] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                if not isinstance(value, str) or not (key == "path" or key.endswith("_path")):
                    continue
                candidates = ("sha256", "byte_sha256", "actual_sha256", "artifact_sha256") if key == "path" \
                    else (key[: -len("path")] + "sha256",)
                digest = next((node[name] for name in candidates if _is_sha256(node.get(name))), None)
                if digest is None or value.startswith("/") or ".." in Path(value).parts:
                    continue
                target = _resolve_repo_path(value, pack_root, repo_root)
                try:
                    relative = target.relative_to(repo_root).as_posix()
                except ValueError:
                    continue
                if relative in PIN_ONLY_PATHS:
                    continue
                if seen.setdefault(relative, digest) != digest:
                    conflicts.append({"path": relative, "sha256": digest})
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(tree)
    rows = [{"path": path, "sha256": digest} for path, digest in sorted(seen.items())]
    return rows + conflicts


# ---------------------------------------------------------------------------
# Member assessment.  Runs in worker processes; returns structure and writes
# the re-reduced summary bytes (numbers) into restricted custody itself.
# ---------------------------------------------------------------------------

def _stamp_ns(stamp: Any, field: str) -> int | None:
    value = stamp.get(field) if isinstance(stamp, Mapping) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        return None
    return math.floor(value * 1_000_000_000)


def member_spans(metadata: Mapping[str, Any], events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Member span and request span in the controller's ``monotonic_ns`` domain.

    Member span: the hull of the sampler stream (``pre_spawn`` to
    ``post_parse`` clock stamps, falling back to the sampling markers) and the
    controller's battery span (``idle_baseline`` start to ``idle_drift_sentinel``
    end, when recorded).  The hull over-covers rather than under-covers.
    Request span: ``sampling_started`` to ``sampling_stopped``, the measured run.
    """
    anchor = metadata.get("uncertainty_evidence", {}).get("clock_anchor", {}) \
        if isinstance(metadata.get("uncertainty_evidence"), Mapping) else {}
    stamps = anchor.get("clock_stamps") if isinstance(anchor, Mapping) else None
    stamps = stamps if isinstance(stamps, Mapping) else {}
    starts = [_stamp_ns(stamps.get(name), "monotonic_before_s") for name in ("pre_spawn", "sampling_started")]
    ends = [_stamp_ns(stamps.get(name), "monotonic_after_s") for name in ("post_parse", "sampling_stopped")]
    for event in events:
        meta = event.get("metadata") if isinstance(event.get("metadata"), Mapping) else {}
        value = meta.get("monotonic_ns")
        if type(value) is not int or value < 0:
            continue
        if event.get("event_type") == "stage_started" and event.get("phase") == "idle_baseline":
            starts.append(value)
        if event.get("event_type") == "stage_completed" and event.get("phase") == "idle_drift_sentinel":
            ends.append(value)
    starts = [value for value in starts if value is not None]
    ends = [value for value in ends if value is not None]
    member = [min(starts), max(ends)] if starts and ends and min(starts) <= max(ends) else None
    request_start = _stamp_ns(stamps.get("sampling_started"), "monotonic_before_s")
    request_end = _stamp_ns(stamps.get("sampling_stopped"), "monotonic_after_s")
    request = [request_start, request_end] if request_start is not None and request_end is not None \
        and request_start <= request_end else None
    return {"member": member, "request": request}


def bundle_creation_ns(metadata: Mapping[str, Any], events: Sequence[Mapping[str, Any]], *,
                       spans: Mapping[str, Any] | None = None,
                       chain_started: Mapping[str, Any] | None = None) -> tuple[int | None, str | None]:
    """When a bundle was created, in the controller's ``monotonic_ns`` domain, and from which stamp.

    In order: the start of the member span (``member_spans``); the earliest
    controller monotonic stamp the bundle recorded (any clock-anchor stamp,
    any event's ``metadata.monotonic_ns``: the battery span's idle_baseline
    start is written before idle admission, so an aborted member has it);
    the ``run_started`` event's wall time, mapped through ``chain.started``'s
    stamps taken at one instant (``monotonic_ns + (wall - epoch_s)``).  The
    result only places the bundle before or after the chain started.
    ``(None, None)`` when the bundle recorded no usable stamp.
    """
    member = spans.get("member") if isinstance(spans, Mapping) else None
    if member is None:
        try:
            member = member_spans(metadata, events)["member"]
        except Exception:  # unreadable stamps place nothing
            member = None
    if member:
        return int(member[0]), "member_span"
    stamps: list[int] = []
    anchor = metadata.get("uncertainty_evidence", {}).get("clock_anchor", {}) \
        if isinstance(metadata.get("uncertainty_evidence"), Mapping) else {}
    clock_stamps = anchor.get("clock_stamps") if isinstance(anchor, Mapping) else None
    for stamp in (clock_stamps.values() if isinstance(clock_stamps, Mapping) else ()):
        for field in ("monotonic_before_s", "monotonic_after_s"):
            value = _stamp_ns(stamp, field)
            if value is not None:
                stamps.append(value)
    for event in events:
        meta = event.get("metadata") if isinstance(event, Mapping) and isinstance(event.get("metadata"), Mapping) \
            else {}
        value = meta.get("monotonic_ns")
        if type(value) is int and value >= 0:
            stamps.append(value)
    if stamps:
        return min(stamps), "controller_monotonic_stamp"
    started = next((event for event in events if isinstance(event, Mapping)
                    and event.get("event_type") == "run_started"), None)
    wall = _num(started.get("timestamp_s")) if isinstance(started, Mapping) else None
    epoch = _num(chain_started.get("epoch_s")) if isinstance(chain_started, Mapping) else None
    anchor_ns = chain_started.get("monotonic_ns") if isinstance(chain_started, Mapping) else None
    if wall is not None and epoch is not None and _is_int(anchor_ns):
        return anchor_ns + round((wall - epoch) * 1_000_000_000), "run_started_wall_via_chain_started"
    return None, None


def _same_path(first: Path, second: Path) -> bool:
    return os.path.abspath(first) == os.path.abspath(second)


def recompute_anchor_status(bundle: Path, clock_anchor: Mapping[str, Any]) -> str:
    """Re-derive the clock anchor from the raw plist and paired clock stamps."""
    from joulewise.adapters.powermetrics import (
        RAW_SAMPLES_NAME, anchor_records_from_powermetrics, parse_powermetrics_records)
    from joulewise.uncertainty_evidence import (
        CLOCK_METHOD, derive_powermetrics_clock_evidence, resolve_clock_evidence_deriver, stamp_from_mapping)
    method = clock_anchor.get("method")
    stamps = {name: stamp_from_mapping(value) for name, value in (clock_anchor.get("clock_stamps") or {}).items()
              if isinstance(value, Mapping)}
    records = parse_powermetrics_records((bundle / "raw" / RAW_SAMPLES_NAME).read_bytes())
    if method == CLOCK_METHOD:
        expected, _point = derive_powermetrics_clock_evidence(
            stamps=stamps, elapsed_s=[record.elapsed_ns / 1_000_000_000.0 for record in records],
            plist_timestamp_s=[float(record.metadata["plist_timestamp_s"]) for record in records])
    else:
        expected, _point = resolve_clock_evidence_deriver(method)(
            stamps=stamps, records=anchor_records_from_powermetrics(records))
    status = expected.get("clock_anchor", {}).get("status")
    return status if status in ANCHOR_STATUSES else "unbounded"


def _events(bundle: Path) -> list[dict[str, Any]]:
    rows = []
    for line in (bundle / "events.jsonl").read_bytes().splitlines():
        if line.strip():
            value = json.loads(line)
            if isinstance(value, dict):
                rows.append(value)
    return rows


def _precheck_structure(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Codes and eligibility only; the evidence numbers stay behind."""
    root = summary.get("window_evidence_precheck")
    result: dict[str, Any] = {}
    if not isinstance(root, Mapping):
        return result

    def reduce_entry(entry: Any) -> dict[str, Any] | None:
        if not isinstance(entry, Mapping) or "reasons" not in entry:
            return None
        reasons = entry.get("reasons")
        return {"eligible": entry.get("eligible"),
                "reasons": list(reasons) if isinstance(reasons, list) else None}

    for key, entry in root.items():
        reduced = reduce_entry(entry)
        if reduced is not None:
            result[key] = reduced
        elif isinstance(entry, Mapping):
            result[key] = {child: reduce_entry(value) for child, value in entry.items()
                           if reduce_entry(value) is not None}
    return result


def assess_member(task: Mapping[str, Any]) -> dict[str, Any]:
    """Strict validation, re-reduction, anchor recompute and identity for one bundle."""
    from joulewise import battery_float
    from joulewise.cli import validate_bundle
    from joulewise.identity_pins import derive_model_runtime_config_from_metadata
    from joulewise.reduce import reduce_bundle
    from joulewise.schemas import is_admissible_succeeded_summary

    run_id, bundle = task["run_id"], Path(task["bundle_path"])
    result: dict[str, Any] = {"run_id": run_id, "bundle_path": str(bundle), "present": bundle.is_dir(),
                              "errors": {}}
    if not result["present"]:
        return result
    result["files_missing"] = [name for name in REQUIRED_BUNDLE_FILES if not (bundle / name).is_file()]

    def guarded(name: str, function: Callable[[], Any]) -> Any:
        try:
            return function()
        except Exception as exc:  # recorded per member; never a harvest fault
            result["errors"][name] = f"{type(exc).__name__}: {exc}"[:500]
            return None

    metadata = guarded("metadata", lambda: read_json(bundle / "metadata.json")) or {}
    summary_raw = guarded("summary", lambda: (bundle / "summary_metrics.json").read_bytes())
    summary = guarded("summary_json", lambda: json.loads(summary_raw)) if summary_raw is not None else None
    summary = summary if isinstance(summary, Mapping) else {}
    config_raw = guarded("config", lambda: (bundle / "config.json").read_bytes())
    config = guarded("config_json", lambda: json.loads(config_raw)) if config_raw is not None else None
    events = guarded("events", lambda: _events(bundle)) or []
    result["status"] = summary.get("status")
    admission = metadata.get("environment_admission") if isinstance(metadata, Mapping) else None
    result["admission_decision"] = admission.get("decision") if isinstance(admission, Mapping) else None
    result["thermal_pressure_elevated"] = "thermal_pressure_elevated_in_window" in json.dumps(admission or {})
    result["metadata_run_id"] = metadata.get("run_id") if isinstance(metadata, Mapping) else None
    result["config_sha256"] = sha256_bytes(config_raw) if config_raw is not None else None
    result["stored_summary_sha256"] = sha256_bytes(summary_raw) if summary_raw is not None else None
    problems = guarded("strict", lambda: list(validate_bundle(bundle, strict=True)))
    result["strict_problems"] = problems
    result["strict_valid"] = problems == []
    anchor = metadata.get("uncertainty_evidence", {}).get("clock_anchor") \
        if isinstance(metadata.get("uncertainty_evidence"), Mapping) else None
    recorded = anchor.get("status") if isinstance(anchor, Mapping) else None
    result["anchor_recorded"] = recorded if recorded in ANCHOR_STATUSES else (
        "not recorded" if recorded is None else "unbounded")
    result["anchor_recomputed"] = guarded("anchor", lambda: recompute_anchor_status(bundle, anchor)) \
        if isinstance(anchor, Mapping) else None
    provenance = summary.get("summary_provenance") if isinstance(summary.get("summary_provenance"), Mapping) else {}

    def rereduce() -> dict[str, Any]:
        payload = reduce_bundle(bundle, reducer_version=provenance.get("reducer_version")).to_dict()
        raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
        target = Path(task["withheld_dir"]) / "reductions" / f"{run_id}.summary_metrics.rereduced.json"
        digest = write_once(target, raw)
        return {"sha256": digest, "path": str(target), "identical_to_stored": raw == summary_raw,
                "admissible": bool(is_admissible_succeeded_summary(payload))}

    result["rereduced"] = guarded("rereduce", rereduce)
    result["spans"] = guarded("spans", lambda: member_spans(metadata, events)) or {"member": None, "request": None}
    observed = metadata.get("workload_observed") if isinstance(metadata.get("workload_observed"), Mapping) else {}
    workload = metadata.get("workload_provenance") if isinstance(metadata.get("workload_provenance"), Mapping) else {}
    prompt = workload.get("prompt") if isinstance(workload.get("prompt"), Mapping) else {}
    policy = workload.get("output_policy") if isinstance(workload.get("output_policy"), Mapping) else {}
    result["tokens"] = {"output_realized": observed.get("output_token_count"),
                        "output_requested": policy.get("requested_tokens"),
                        "output_emitted": policy.get("emitted_tokens"),
                        "prompt_realized": prompt.get("realized_token_count")}
    result["precheck"] = _precheck_structure(summary)
    quality = summary.get("measurement_quality") if isinstance(summary.get("measurement_quality"), Mapping) else {}
    result["quality"] = {"idle_window_suspect": quality.get("idle_window_suspect"),
                         "cooldown_cap_hit": quality.get("cooldown_cap_hit")}

    def identity() -> dict[str, str]:
        _stack, triple = derive_model_runtime_config_from_metadata(config, metadata)
        return {key: triple[key] for key in ("model_artifact_sha256", "runtime_identity_sha256")}

    result["identity"] = guarded("identity", identity) if isinstance(config, Mapping) else None

    def battery() -> dict[str, Any]:
        verdict = battery_float.authenticate_bundle(bundle)
        return {"status": verdict.status, "reasons": list(verdict.reasons)}

    result["battery_pair"] = guarded("battery_pair", battery)
    started = next((event for event in events if event.get("event_type") == "run_started"), None)
    stamp = started.get("timestamp_s") if isinstance(started, Mapping) else None
    result["run_started_epoch_s"] = stamp if isinstance(stamp, (int, float)) and not isinstance(stamp, bool) else None
    raw_plist = bundle / "raw" / "powermetrics.plist"
    result["stream_bytes"] = raw_plist.stat().st_size if raw_plist.is_file() else None
    return result


def assess_members(tasks: Sequence[Mapping[str, Any]], *, workers: int = 1) -> list[dict[str, Any]]:
    if workers <= 1 or len(tasks) <= 1:
        return [assess_member(task) for task in tasks]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(assess_member, tasks))


# ---------------------------------------------------------------------------
# Hazard monitor journals (L1 seam) and the physics-in-span joins.
#
# Lane L1's monitor (``joulewise.hazards.monitor.Monitor``) writes one JSON
# line per observation, schema ``joulewise.hazard_journal.v1``:
#
#     {schema, module, session, seq, kind, started, finished, values, error, raw}
#
# ``started`` and ``finished`` are {wall_ns, monotonic_ns, monotonic_raw_ns};
# monotonic_ns is the controller's ``time.monotonic_ns`` domain, the one member
# spans are stamped in.  Observations are ``reading`` lines (battery, thermal,
# clock, disk) and contention ``interval`` lines; a non-null ``error`` means the
# probe failed.  The other kinds are bookkeeping.  ``parse_monitor_line`` is
# the one reader of this format; tests/fixtures/b5_harvest/l1_monitor holds
# journals L1's own monitor wrote.
# ---------------------------------------------------------------------------

JOURNAL_SCHEMA = "joulewise.hazard_journal.v1"
MONITOR_MODULES = ("battery", "thermal", "contention", "clock", "disk")
OBSERVATION_KIND = {"battery": "reading", "thermal": "reading", "clock": "reading", "disk": "reading",
                    "contention": "interval"}
BOOKKEEPING_KINDS = frozenset({"session_start", "session_end", "snapshot", "event", "cost"})
STAMP_KEYS = ("wall_ns", "monotonic_ns", "monotonic_raw_ns")
FREQUENCY_SCALE = 1 << 16  # ntp_adjtime frequency-word units per ppm (kernel_clock.FREQUENCY_SCALE)
ACCUMULATOR_PAIRS = {"charge": ("AccumulatedBatteryPower", "BatteryPowerAccumulatorCount"),
                     "discharge": ("AccumulatedBatteryDischarge", "BatteryDischargeAccumulatorCount")}


class MonitorLineError(ValueError):
    """A line that is not a ``joulewise.hazard_journal.v1`` line of the expected module."""


@dataclasses.dataclass(frozen=True)
class Reading:
    """One observation line of a monitor journal.

    ``monotonic_ns``, ``monotonic_raw_ns`` and ``wall_ns`` are the line's
    ``finished`` stamp (L1 times thermal and clock samples there);
    ``started_*`` is its ``started`` stamp (L1 maps a battery UpdateTime
    through it).  ``status`` is ``ok`` for a good observation, ``error`` for a
    failed probe (it observes nothing), or ``event`` for a disk.low marker.
    """
    module: str
    monotonic_ns: int
    monotonic_raw_ns: int
    wall_ns: int
    started_monotonic_ns: int
    started_wall_ns: int
    values: Mapping[str, Any]
    status: str = "ok"
    interval: tuple[int, int] | None = None  # contention: the ps interval in monotonic_ns


def _num(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return value


def _int(value: Any) -> int | None:
    number = _num(value)
    return int(number) if number is not None else None


def _pair(value: Any) -> tuple[int, int] | None:
    if isinstance(value, Mapping):
        value = value.get("monotonic_ns")
    if isinstance(value, (list, tuple)) and len(value) == 2 and all(_is_int(item) for item in value) \
            and value[0] <= value[1]:
        return (value[0], value[1])
    return None


def _stamp(value: Any, where: str) -> dict[str, int]:
    if not isinstance(value, Mapping) or any(not _is_int(value.get(key)) for key in STAMP_KEYS):
        raise MonitorLineError(f"{where} is not a {{wall_ns, monotonic_ns, monotonic_raw_ns}} stamp")
    return {key: value[key] for key in STAMP_KEYS}


def parse_monitor_line(module: str, value: Any) -> Reading | None:
    """One L1 journal line -> :class:`Reading`; ``None`` for a bookkeeping line.

    Raises :class:`MonitorLineError` for a line that is not this module's
    ``joulewise.hazard_journal.v1`` line; the caller counts it as malformed.
    """
    if not isinstance(value, Mapping) or value.get("schema") != JOURNAL_SCHEMA:
        raise MonitorLineError(f"not a {JOURNAL_SCHEMA} line")
    if value.get("module") != module:
        raise MonitorLineError(f"a {value.get('module')!r} line in the {module} journal")
    kind, values = value.get("kind"), value.get("values")
    disk_event = (module == "disk" and kind == "event" and isinstance(values, Mapping)
                  and values.get("code") == "disk.low")
    if kind != OBSERVATION_KIND[module] and not disk_event:
        if kind in BOOKKEEPING_KINDS:
            return None
        raise MonitorLineError(f"unknown kind {kind!r}")
    started, finished = _stamp(value.get("started"), "started"), _stamp(value.get("finished"), "finished")
    values = {} if values is None else values
    if not isinstance(values, Mapping):
        raise MonitorLineError("values is not an object")
    interval = None
    if module == "contention":
        interval = _pair(values.get("interval"))
        if interval is None:
            raise MonitorLineError("contention interval lacks interval.monotonic_ns")
    status = "event" if disk_event else ("error" if value.get("error") is not None else "ok")
    return Reading(module, finished["monotonic_ns"], finished["monotonic_raw_ns"], finished["wall_ns"],
                   started["monotonic_ns"], started["wall_ns"], values, status, interval)


def read_monitor_journal(path: Path, module: str) -> tuple[list[Reading], int]:
    """Every observation of one journal in ``finished`` order, and the malformed-line count."""
    readings, malformed = [], 0
    for line in path.read_bytes().splitlines():
        if not line.strip():
            continue
        try:
            reading = parse_monitor_line(module, json.loads(line))
        except ValueError:  # not JSON, not UTF-8, or MonitorLineError
            malformed += 1
            continue
        if reading is not None:
            readings.append(reading)
    readings.sort(key=lambda item: (item.monotonic_ns, item.started_monotonic_ns))
    return readings, malformed


def in_force(times: Sequence[int], start: int, end: int) -> list[int]:
    """Indexes in force for [start, end]: last at/before start, all inside, first at/after end."""
    indexes = [index for index, stamp in enumerate(times) if start < stamp < end]
    before = [index for index, stamp in enumerate(times) if stamp <= start]
    after = [index for index, stamp in enumerate(times) if stamp >= end]
    if before:
        indexes.insert(0, before[-1])
    if after:
        indexes.append(after[0])
    return sorted(set(indexes))


def _overlaps(first: Sequence[int], second: Sequence[int]) -> bool:
    return first[0] <= second[1] and second[0] <= first[1]


def _uncovered(times: Sequence[int], span: Sequence[int], gap_ns: int) -> list[list[int | None]]:
    """Intervals longer than ``gap_ns`` without an observation that overlap ``span``.

    A hole is reported by the observations that bound it (``None`` where no
    observation exists on that side), never by the member span's own edges:
    span edges would publish the stream's timing in structure-only outputs.
    """
    if not times:
        return [[None, None]]
    holes: list[list[int | None]] = []
    edges = [None, *sorted(times), None]
    for left, right in zip(edges, edges[1:]):
        lo = span[0] - gap_ns - 1 if left is None else left
        hi = span[1] + gap_ns + 1 if right is None else right
        if hi - lo > gap_ns and _overlaps((lo, hi), span):
            holes.append([left, right])
    return holes


def _hole_interval(hole: Sequence[int | None]) -> dict[str, Any]:
    return {"monotonic_ns": list(hole) if None not in hole else None}


@dataclasses.dataclass(frozen=True)
class Publication:
    """One battery gauge publication: the first good reading of a new ``UpdateTime``."""
    monotonic_ns: int
    update_time_s: int
    instant_ma: float | None
    amperage_ma: float | None
    is_charging: bool | None
    external_connected: bool | None
    voltage_mv: float | None
    accumulators: Mapping[str, tuple[float | None, float | None]]
    values: Mapping[str, Any] = dataclasses.field(default_factory=dict)  # the reading's L1 values


def _bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def battery_publications(readings: Sequence[Reading]) -> list[Publication]:
    """Distinct gauge publications in time order (L1's ``battery.publications`` rule).

    A publication takes effect at its UpdateTime, mapped into the monotonic
    domain through the (wall, monotonic) pair of the reading's own ``started``
    stamp.  The gauge publishes every 60 s and every field, the accumulators
    included, is frozen between publications.
    """
    seen: dict[int, Publication] = {}
    for reading in readings:
        values = reading.values
        update = _int(values.get("update_time_s"))
        if reading.status != "ok" or update is None or update in seen:
            continue
        telemetry = values.get("power_telemetry") if isinstance(values.get("power_telemetry"), Mapping) else {}
        seen[update] = Publication(
            monotonic_ns=update * 1_000_000_000 - (reading.started_wall_ns - reading.started_monotonic_ns),
            update_time_s=update, instant_ma=_num(values.get("instant_amperage_ma")),
            amperage_ma=_num(values.get("amperage_ma")), is_charging=_bool(values.get("is_charging")),
            external_connected=_bool(values.get("external_connected")), voltage_mv=_num(values.get("voltage_mv")),
            accumulators={label: (_num(telemetry.get(total)), _num(telemetry.get(count)))
                          for label, (total, count) in ACCUMULATOR_PAIRS.items()},
            values=values)
    return sorted(seen.values(), key=lambda item: (item.monotonic_ns, item.update_time_s))


def _float_reasons(instant: Any, amperage: Any, charging: Any, external: Any, limit: float) -> list[str]:
    reasons = []
    if instant is not None and abs(instant) > limit:
        reasons.append("instant_amperage_above_limit")
    if amperage is not None and abs(amperage) > limit:
        reasons.append("amperage_above_limit")
    if charging is True:
        reasons.append("is_charging")
    if external is False:
        reasons.append("external_disconnected")
    return reasons


def battery_member_flags(span: Sequence[int], readings: Sequence[Reading], thresholds: Mapping[str, Any]
                         ) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    """(code, observed, interval) for one member span under the in-force rule (plan 3.4)."""
    out: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    limit = float(thresholds["battery_limit_ma"])
    publications = battery_publications(readings)
    times = [item.monotonic_ns for item in publications]
    violations, missing_fields = [], []
    for index in in_force(times, span[0], span[1]):
        item = publications[index]
        if None in (item.instant_ma, item.amperage_ma, item.is_charging, item.external_connected):
            missing_fields.append(item.monotonic_ns)
        reasons = _float_reasons(item.instant_ma, item.amperage_ma, item.is_charging, item.external_connected, limit)
        if reasons:
            violations.append({"publication_monotonic_ns": item.monotonic_ns, "update_time_s": item.update_time_s,
                               "instant_ma": item.instant_ma, "amperage_ma": item.amperage_ma, "reasons": reasons})
    for reading in readings:  # every good poll inside the span, published or not
        if reading.status == "ok" and span[0] <= reading.monotonic_ns <= span[1]:
            values = reading.values
            reasons = _float_reasons(None, None, _bool(values.get("is_charging")),
                                     _bool(values.get("external_connected")), limit)
            if reasons:
                violations.append({"poll_monotonic_ns": reading.monotonic_ns, "reasons": reasons})
    if violations:
        first = violations[0].get("publication_monotonic_ns", violations[0].get("poll_monotonic_ns"))
        out.append(("battery.member_span", {"rule": "in_force_publication", "violations": violations[:8],
                                            "violation_count": len(violations)},
                    {"monotonic_ns": [first, first]}))
    holes = _uncovered(times, span, int(float(thresholds["battery_unmeasured_gap_s"]) * 1e9))
    if holes or missing_fields:
        out.append(("battery.unmeasured", {"holes_monotonic_ns": holes[:8],
                                           "publications_missing_fields": missing_fields[:8]},
                    _hole_interval(holes[0]) if holes else {"monotonic_ns": [missing_fields[0]] * 2}))
    out.extend(accumulator_member_flags([publications[index] for index in in_force(times, span[0], span[1])],
                                        thresholds))
    return out


def accumulator_member_flags(in_force_publications: Sequence[Publication], thresholds: Mapping[str, Any]
                             ) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    """The accumulator rule of registration 6.4, on L1's own interval reader.

    For each interval between consecutive in-force publications (the same
    intervals as L1's ``battery.span_findings``), L1's
    ``joulewise.hazards.battery.accumulator_interval`` gives, per sign, the
    accumulated value per counted tick (mW on L1's units check) or why that
    sign cannot be read.  With the registered scale (W per accumulator unit,
    0.001) a sign whose mean battery power exceeds limit_ma x the
    publication's voltage is ``battery.accumulator_excursion``; a nonzero
    mean at or below it is ``battery.accumulator_activity``; a sign that
    cannot be read, or an interval without a voltage, is
    ``battery.accumulator_unavailable`` (the publication rule still applies).
    There is no unscaled path: without a registered positive scale this
    raises, and the harvest records the fault.
    """
    from joulewise.hazards.battery import ACCUMULATOR_SIGNS, accumulator_interval
    unit = thresholds["battery_accumulator_watts_per_unit"]
    if not _is_number(unit) or unit <= 0:
        raise ValueError("battery_accumulator_watts_per_unit is not a registered positive scale")
    limit_ma = float(thresholds["battery_limit_ma"])
    signs = [label for label, _total, _count in ACCUMULATOR_SIGNS]
    excursions, activity, unavailable_rows = [], [], []
    for earlier, later in zip(in_force_publications, in_force_publications[1:]):
        delta = accumulator_interval(earlier.values, later.values)
        voltage = later.voltage_mv or earlier.voltage_mv
        interval = [earlier.monotonic_ns, later.monotonic_ns]
        unavailable = {label: delta[f"{label}_unavailable"] for label in signs if delta[f"{label}_unavailable"]}
        if not voltage:
            unavailable = {label: "Voltage not read at either publication" for label in signs}
        if unavailable:
            unavailable_rows.append({"interval_monotonic_ns": interval, "update_times_s": [earlier.update_time_s,
                                                                                         later.update_time_s],
                                     "unavailable": unavailable})
        if not voltage:
            continue
        limit_w = limit_ma / 1000.0 * float(voltage) / 1000.0
        for label in signs:
            mean = delta[f"{label}_mean_mw"]
            if label in unavailable or mean is None:
                continue
            entry = {"accumulator": label, "ticks": delta[f"{label}_ticks"], "mean_per_tick": mean,
                     "mean_w": abs(mean) * float(unit), "limit_w": limit_w, "voltage_mv": voltage,
                     "interval_monotonic_ns": interval}
            (excursions if entry["mean_w"] > limit_w else activity).append(entry)
    out: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    for code, rows, rule in (("battery.accumulator_excursion", excursions, "accumulator_mean_power"),
                             ("battery.accumulator_activity", activity, "accumulator_mean_power_at_or_below_limit"),
                             ("battery.accumulator_unavailable", unavailable_rows, "accumulator_not_evaluated")):
        if rows:
            out.append((code, {"rule": rule, "intervals": rows[:8], "count": len(rows),
                               "watts_per_unit": unit},
                        {"monotonic_ns": rows[0]["interval_monotonic_ns"]}))
    return out


def thermal_member_flags(span: Sequence[int], readings: Sequence[Reading], thresholds: Mapping[str, Any]
                         ) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    """``thermal.os_level_nonzero`` for any in-force 5 s sample above 0; coverage holes."""
    samples = [(reading.monotonic_ns, _int(reading.values.get("level"))) for reading in readings
               if reading.status == "ok"]
    samples = [(stamp, level) for stamp, level in samples if level is not None]
    out = []
    times = [stamp for stamp, _level in samples]
    nonzero = [{"monotonic_ns": samples[index][0], "level": samples[index][1]}
               for index in in_force(times, span[0], span[1]) if samples[index][1] != 0]
    if nonzero:
        out.append(("thermal.os_level_nonzero", {"samples": nonzero[:8]},
                    {"monotonic_ns": [nonzero[0]["monotonic_ns"], nonzero[-1]["monotonic_ns"]]}))
    holes = _uncovered(times, span, int(float(thresholds["thermal_unmeasured_gap_s"]) * 1e9))
    if holes:
        out.append(("thermal.unmeasured", {"holes_monotonic_ns": holes[:8]}, _hole_interval(holes[0])))
    return out


def _outside_processes(values: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Processes outside the measurement tree in one L1 interval.

    L1 lists them in ``outside_over_limit`` (above the monitor's limit) and
    ``outside_listed`` (at least 0.005 CPU-s/s); both are read so the
    harvest's own limit applies.  kernel_task is excluded by the monitor and
    journaled in ``kernel_task_cpu_s_per_s``.
    """
    rows: dict[tuple[Any, Any], dict[str, Any]] = {}
    for key in ("outside_over_limit", "outside_listed"):
        listed = values.get(key)
        for row in listed if isinstance(listed, list) else []:
            rate = _num(row.get("cpu_s_per_s")) if isinstance(row, Mapping) else None
            if rate is None:
                continue
            identity = (row.get("pid"), row.get("command"))
            if identity not in rows or rows[identity]["cpu_s_per_s"] < rate:
                rows[identity] = {"pid": row.get("pid"), "command": row.get("command"), "cpu_s_per_s": rate}
    return list(rows.values())


def contention_member_flags(request: Sequence[int], readings: Sequence[Reading], thresholds: Mapping[str, Any]
                            ) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    """``contention.request_overlap`` and ``contention.unmeasured`` for one request."""
    limit = float(thresholds["contention_cpu_s_per_s"])
    intervals = [reading for reading in readings if reading.status == "ok" and reading.interval]
    offenders = []
    for reading in intervals:
        if not _overlaps(reading.interval, request):
            continue
        for row in _outside_processes(reading.values):
            if row["command"] in CONTENTION_EXEMPT or row["cpu_s_per_s"] <= limit:
                continue
            offenders.append({**row, "interval_monotonic_ns": list(reading.interval)})
    out = []
    if offenders:
        out.append(("contention.request_overlap", {"offenders": offenders[:8], "offender_count": len(offenders)},
                    {"monotonic_ns": offenders[0]["interval_monotonic_ns"]}))
    # A hole is named by the interval edges around it (None where the journal
    # has no interval on that side), never by the request's own edges.  A
    # failed ps interval covers nothing.
    every = sorted(reading.interval for reading in intervals)
    ended = [end for _start, end in every if end <= request[0]]
    previous_end: int | None = max(ended) if ended else None
    cursor: int = request[0]
    holes: list[list[int | None]] = []
    for start, end in every:
        if end <= request[0]:
            continue
        if start > cursor:
            holes.append([previous_end, start])
        if end > cursor:
            cursor, previous_end = end, end
        if cursor >= request[1]:
            break
    if cursor < request[1]:
        following = [start for start, _end in every if start >= request[1]]
        holes.append([previous_end, min(following) if following else None])
    if holes:
        out.append(("contention.unmeasured", {"holes_monotonic_ns": holes[:8]}, _hole_interval(holes[0])))
    return out


def clock_member_flags(span: Sequence[int], readings: Sequence[Reading], thresholds: Mapping[str, Any]
                       ) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    """``clock.unmeasured`` when the 1 Hz anchor journal has a hole overlapping the span."""
    times = [reading.monotonic_ns for reading in readings
             if reading.status == "ok" and isinstance(reading.values.get("anchor"), Mapping)]
    holes = _uncovered(times, span, int(float(thresholds["clock_unmeasured_gap_s"]) * 1e9))
    return [("clock.unmeasured", {"holes_monotonic_ns": holes[:8]}, _hole_interval(holes[0]))] if holes else []


def clock_steps(readings: Sequence[Reading], thresholds: Mapping[str, Any]
                ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Clock steps and frequency-word changes in the 1 Hz journal (L1's ``clock.window_events`` rule).

    A step is a residual move above ``clock_step_ns`` between consecutive good
    samples: the anchor's movement (REALTIME - MONOTONIC_RAW) minus f times the
    MONOTONIC_RAW time elapsed, exactly, with the f in force at the earlier
    sample.  Samples before the first f read cannot be judged; a failed sample
    breaks the chain.
    """
    step_ns = int(thresholds["clock_step_ns"])
    steps: list[dict[str, Any]] = []
    changes: list[dict[str, Any]] = []
    word: int | None = None
    previous: tuple[Reading, tuple[int, int]] | None = None
    for reading in readings:
        anchor = reading.values.get("anchor") if reading.status == "ok" else None
        point = (_int(anchor.get("anchor_ns")), _int(anchor.get("monotonic_raw_ns"))) \
            if isinstance(anchor, Mapping) else (None, None)
        if point[0] is None or point[1] is None:
            previous = None
            continue
        if previous is not None and word is not None:
            (earlier, (anchor0, raw0)) = previous
            moved = Fraction(point[0] - anchor0) - Fraction(word * (point[1] - raw0), FREQUENCY_SCALE * 1_000_000)
            if abs(moved) > step_ns:
                steps.append({"interval_monotonic_ns": [earlier.started_monotonic_ns, reading.monotonic_ns],
                              "residual_move_ns": int(moved)})
        frequency = reading.values.get("frequency")
        raw_word = _int(frequency.get("raw_word")) if isinstance(frequency, Mapping) else None
        if raw_word is not None:
            if word is not None and raw_word != word:
                changes.append({"monotonic_ns": reading.monotonic_ns, "ppm": raw_word / FREQUENCY_SCALE,
                                "previous_ppm": word / FREQUENCY_SCALE})
            word = raw_word
        previous = (reading, point)
    return steps, changes


def disk_low(readings: Sequence[Reading], thresholds: Mapping[str, Any]) -> tuple[list[Reading], list[str]]:
    """Readings with a target below ``disk_low_bytes``, a nonempty L1 ``low`` list, or a disk.low
    marker, and the paths they name."""
    limit = float(thresholds["disk_low_bytes"])
    low: list[Reading] = []
    paths: set[str] = set()
    for reading in readings:
        if reading.status not in ("ok", "event"):
            continue
        targets, listed = reading.values.get("targets"), reading.values.get("low")
        below = [row for row in (targets if isinstance(targets, list) else [])
                 if isinstance(row, Mapping) and _num(row.get("free_bytes")) is not None and row["free_bytes"] < limit]
        marked = [row for row in (listed if isinstance(listed, list) else []) if isinstance(row, Mapping)]
        if reading.status == "event" or below or marked:
            low.append(reading)
            paths.update(row["path"] for row in below + marked if isinstance(row.get("path"), str))
    return low, sorted(paths)


# ---------------------------------------------------------------------------
# The harvest.
# ---------------------------------------------------------------------------

def group_alive(pgid: int) -> bool:
    """Signal 0 probes a process group without touching it."""
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def boot_session_uuid() -> str | None:
    try:
        result = subprocess.run(["/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"], capture_output=True,
                                text=True, check=False, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


STRATUM_OF_CELL_KIND = {"absolute": "repeat", "comparative": "quad", "contrast": "quad"}


def l4_exclusion_inputs(roster: Mapping[str, Any], spans: Mapping[str, Mapping[str, Any]], *, plan_id: Any,
                        attempt: Any, chain_started_monotonic_ns: int | None = None,
                        bundles: Sequence[Mapping[str, Any]] | None = None
                        ) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """The roster and spans in the shape L4's ``joulewise.flags.exclusions.compute`` reads.

    roster: ``{plan_id, attempt, chain_started_monotonic_ns, members: [{run_id,
    stage_id, units: [{cell_id, stratum, unit_id}]}], cells: [{cell_id,
    target, strata}], bundles: [{bundle_id, run_id, attempt,
    created_monotonic_ns}]}``; spans: ``{run_id: {monotonic_ns,
    request_monotonic_ns}}`` in the controller's ``time.monotonic_ns`` domain.

    A floor's reported quantity is its condition family: the extraction
    spec's absolute cell (repeat units) and comparative cell (quad units) of
    one family become one L4 cell with strata ``["quad", "repeat"]``, so the
    unit minimum applies to each stratum (plan 3.5).  A GAMMA contrast is one
    cell of quad units.  Strata come from the cells' kinds, not from the units
    present, so a cell that lost a whole stratum is below the minimum.
    """
    target_of: dict[str, str] = {}
    strata: dict[str, set[str]] = {}
    is_target: dict[str, bool] = {}
    for cell in roster.get("cells", []):
        family, kind = cell.get("condition_family_id"), cell.get("kind")
        target = family if kind in ("absolute", "comparative") and isinstance(family, str) and family \
            else str(cell["cell_id"])
        target_of[cell["cell_id"]] = target
        declared = strata.setdefault(target, set())
        if kind in STRATUM_OF_CELL_KIND:
            declared.add(STRATUM_OF_CELL_KIND[kind])
        # A reported quantity is a target cell when any of its extraction
        # cells is (build_roster: the p42 floor cells are not; registration 6.6).
        is_target[target] = is_target.get(target, False) or cell.get("target", True) is not False
    members, stage_of = [], {}
    for member in roster.get("members", []):
        stage_of[member["run_id"]] = member.get("stage_id")
        members.append({"run_id": member["run_id"], "stage_id": member.get("stage_id"), "kind": member.get("kind"),
                        "units": [{"cell_id": target_of.get(cell["cell_id"], str(cell["cell_id"])),
                                   "stratum": cell["unit_kind"], "unit_id": str(cell["unit_id"])}
                                  for cell in member.get("cells", [])]})
    document: dict[str, Any] = {
        "schema": ROSTER_SCHEMA, "pack_id": roster.get("pack_id"), "plan_id": plan_id, "attempt": attempt,
        "chain_started_monotonic_ns": chain_started_monotonic_ns, "members": members,
        "cells": [{"cell_id": cell_id, "target": is_target.get(cell_id, True), "strata": sorted(declared)}
                  for cell_id, declared in sorted(strata.items())]}
    if bundles is not None:
        document["bundles"] = [dict(bundle) for bundle in bundles]
    spans_document = {
        run_id: {"monotonic_ns": list(span["member"]) if span.get("member") else None,
                 "request_monotonic_ns": list(span["request"]) if span.get("request") else None,
                 "stage_id": stage_of.get(run_id), "bundle_id": run_id}
        for run_id, span in sorted(spans.items())}
    return document, spans_document


def _l4_exclusions(flags: list[dict[str, Any]], roster: Mapping[str, Any], spans: Mapping[str, Any],
                   catalog: Catalog) -> Any:
    """L4's ``joulewise.flags.exclusions.compute`` over the catalog read by L4's own loader."""
    if catalog.path is None or catalog.sha256 is None:
        raise HarvestFault("flag_catalog_absent")
    exclusions = importlib.import_module("joulewise.flags.exclusions")
    load_catalog = importlib.import_module("joulewise.flags.catalog").load_catalog
    return exclusions.compute(flags, roster, spans, load_catalog(Path(catalog.path)))


@dataclasses.dataclass
class Seams:
    """Process and other-lane seams.  Tests replace these; production does not."""
    runner: Callable[..., Any] = subprocess.run
    group_alive: Callable[[int], bool] = group_alive
    exclusions_compute: Callable[..., Any] = _l4_exclusions
    clone: Callable[[Path, Path], None] = clone_tree
    now: Callable[[], float] = time.time
    monotonic_ns: Callable[[], int] = time.monotonic_ns
    boot_session_uuid: Callable[[], str | None] = boot_session_uuid
    workers: int = 1
    python: str = sys.executable


def readiness(inputs: WindowInputs, seams: Seams, *, allow_missing_terminal: bool = False) -> dict[str, Any]:
    """The harvest opens at chain exit plus the driver's terminal record."""
    started = inputs.night_dir / "chain.started"
    terminal = inputs.night_dir / "result.json"
    state = {"chain_started": started.is_file(), "terminal_record": terminal.is_file(), "group_alive": False}
    if state["chain_started"]:
        try:
            pgid = read_json(started).get("pgid")
        except (OSError, ValueError, AttributeError):
            pgid = None
        if type(pgid) is int and pgid > 1:
            state["group_alive"] = bool(seams.group_alive(pgid))
    if state["group_alive"]:
        raise NotReady("chain_process_group_alive")
    if not state["terminal_record"] and not allow_missing_terminal:
        raise NotReady("terminal_record_absent")
    return state


class _Harvest:
    def __init__(self, inputs: WindowInputs, archive_root: Path, seams: Seams, *, prepare_desk: bool,
                 run_g3: bool):
        self.inputs, self.archive, self.seams = inputs, archive_root, seams
        self.prepare_desk, self.run_g3 = prepare_desk, run_g3
        self.derived, self.withheld = archive_root / "derived", archive_root / "withheld"
        self.catalog = Catalog.load(inputs.catalog_path)
        self.flags = FlagLedger(plan_id=inputs.plan_id, attempt=inputs.attempt, catalog=self.catalog,
                                boot_session_uuid=seams.boot_session_uuid(), now=seams.now,
                                monotonic_ns=seams.monotonic_ns)
        self.collector_errors: list[dict[str, Any]] = []
        # Desk and arm collectors that did not finish (plan 3.2): folded from
        # their own run records into window_flags.json collector_errors.
        self.prior_collector_errors: list[dict[str, Any]] = []
        self._prior_error_keys: set[tuple[Any, ...]] = set()
        self.error_details: list[dict[str, Any]] = []
        self.faults: list[dict[str, Any]] = []
        self.roster: dict[str, Any] = {}
        self.members: dict[str, dict[str, Any]] = {}
        self.capture_assessments: dict[str, dict[str, Any]] = {}
        self.spans: dict[str, dict[str, Any]] = {}
        self.hazards: dict[str, Any] = {}
        self.outputs: dict[str, str] = {}
        self.repo_copy: Path | None = None
        self.pair_missing: dict[str, Any] = {}  # run_id -> #421 pair status, joined to coverage later
        self.exclusion_roster: dict[str, Any] | None = None
        self.exclusion_spans: dict[str, Any] | None = None
        self.h_claim = inputs.h_claim
        self.neg8: dict[str, Any] | None = None  # the NEG-8 bound check (neg8_bound)
        # The bound neg8_bound validated against the collected 10/11-member
        # manifest (an energy: it never leaves this object or withheld/).
        self.neg8_collected_bound: Mapping[str, Any] | None = None

    # -- step wrappers ------------------------------------------------------
    def step(self, name: str, function: Callable[[], Any], *, fault: bool = True) -> Any:
        started = time.monotonic()
        try:
            return function()
        except Exception as exc:
            self._record_error(name, exc, round(time.monotonic() - started, 3), fault=fault)
            return None

    def _record_error(self, name: str, exc: BaseException, elapsed_s: float, *, fault: bool) -> None:
        """The type goes to the structure summary; the message (which can quote
        data values) goes only to restricted custody."""
        entry = {"collector": name, "error": type(exc).__name__, "elapsed_s": elapsed_s}
        self.error_details.append({**entry, "detail": f"{exc}"[:2000]})
        self.collector_errors.append(entry)
        if fault:
            self.faults.append(entry)
        else:
            self.flags.emit("records.collector_failed", level="window", collector=name,
                            observed={"collector": name, "error_type": type(exc).__name__})

    def fault(self, collector: str, problem: str) -> None:
        """A harvest fault found on present bytes that is not an exception (a threshold problem)."""
        entry = {"collector": collector, "error": problem[:200], "elapsed_s": 0.0}
        self.error_details.append({**entry, "detail": problem})
        self.collector_errors.append(entry)
        self.faults.append(entry)

    def emit(self, code: str, **kwargs: Any) -> dict[str, Any]:
        return self.flags.emit(code, **kwargs)

    # -- 0. registered thresholds (registration 6.9) ----------------------------
    def record_thresholds(self) -> None:
        """Write where every threshold came from; each problem is a harvest fault, never a default."""
        provenance = dict(self.inputs.thresholds_provenance) or {
            "schema": THRESHOLDS_SCHEMA, "values": dict(self.inputs.thresholds), "problems": ["provenance_absent"]}
        self.outputs["derived/harvest-thresholds.json"] = write_json_once(
            self.derived / "harvest-thresholds.json", provenance)
        for problem in provenance.get("problems") or []:
            self.fault("thresholds", str(problem))

    # -- 1. archive -----------------------------------------------------------
    def archive_inputs(self) -> None:
        inputs = self.inputs
        sources: dict[str, Path] = {"night-custody": inputs.custody_root}
        for name, path in (("claim-runs", inputs.claim_runs_root), ("bound-runs", inputs.bound_runs_root),
                           ("chain", inputs.chain_path), ("chain-sidecar", inputs.chain_sha256_path),
                           ("plan", inputs.plan_path)):
            if path is not None and not _under(path, inputs.custody_root):
                sources[name] = path
        sources["ledger/calibration_observation_ledger.jsonl"] = inputs.ledger_path
        sources["ledger/calibration_ledger_head.json"] = inputs.head_pin_path
        for name, path in (("acceptance.json", self._acceptance_path()),
                           ("sealed_inventory.json", inputs.sealed_inventory_path),
                           ("flag_catalog.json", inputs.catalog_path),
                           ("identity_pins.json", inputs.identity_pins_path),
                           ("registration.md", inputs.registration_path)):
            if path is not None and path.is_file():
                sources[f"inputs/{name}"] = path
        # The pack and every repo file the plan tree pins, at repo-relative paths.
        repo_files: dict[str, Path] = {}
        pack_relative = _relative_to(inputs.pack_root, inputs.measurement_root)
        if pack_relative is not None:
            sources[f"repo/{pack_relative}"] = inputs.pack_root
        try:
            tree = read_json(inputs.pack_root / "plan_tree.json")
            for row in pinned_files(tree, pack_root=inputs.pack_root, repo_root=inputs.measurement_root):
                if pack_relative is not None and row["path"].startswith(pack_relative + "/"):
                    continue
                repo_files[row["path"]] = inputs.measurement_root / row["path"]
        except (OSError, ValueError):
            pass
        policy = self._policy_path()
        if policy is not None:
            relative = _relative_to(policy, inputs.measurement_root)
            if relative is not None:
                repo_files.setdefault(relative, policy)
        for relative, path in sorted(repo_files.items()):
            sources[f"repo/{relative}"] = path
        self.sources = {name: path for name, path in sources.items() if path.exists()}
        self.original = archive_sources(self.sources, self.archive, clone=self.seams.clone)
        self.repo_copy = self.archive / "sources" / "repo"

    def _acceptance_path(self) -> Path:
        if self.inputs.acceptance_path is not None:
            return self.inputs.acceptance_path
        from joulewise.calibration_bracketing import DEFAULT_ACCEPTANCE_BOUND_PATH
        relative = _relative_to(Path(DEFAULT_ACCEPTANCE_BOUND_PATH), Path(__file__).resolve().parents[2])
        candidate = self.inputs.measurement_root / relative if relative else None
        return candidate if candidate is not None and candidate.is_file() else Path(DEFAULT_ACCEPTANCE_BOUND_PATH)

    def _policy_path(self) -> Path | None:
        try:
            policy = read_json(self.inputs.pack_root / "plan_tree.json").get("campaign_policy", {})
        except (OSError, ValueError):
            return None
        relative = policy.get("path") if isinstance(policy, Mapping) else None
        return self.inputs.measurement_root / relative if isinstance(relative, str) else None

    # -- 2. roster and member assessment --------------------------------------
    def build_roster(self) -> None:
        repo = self.repo_copy if self.repo_copy and self.repo_copy.is_dir() else self.inputs.measurement_root
        pack_relative = _relative_to(self.inputs.pack_root, self.inputs.measurement_root)
        pack = repo / pack_relative if pack_relative else self.inputs.pack_root
        self.pack_copy, self.repo_root_copy = pack, repo
        self.roster = build_roster(pack, repo)

    def roster_dispatch(self) -> None:
        """``roster.duplicate_run_id`` for a run id the plan launches or lists more than once.

        One run id names one bundle directory per runs root, and the campaign
        runner skips a run id whose complete bundle already exists, so every
        launch after the first is never measured and the roster (keyed by run
        id) cannot show the missing positions.  Recorded from the preserved
        plan tree; the sealed catalog decides the effect.
        """
        tree = read_json(self.pack_copy / "plan_tree.json")
        dispatches, _unresolved = stage_dispatches(tree, self.pack_copy)
        listings = self.roster.get("duplicate_listings") or {}
        for run_id in sorted(set(listings) | {key for key, rows in dispatches.items() if len(rows) > 1}):
            rows = dispatches.get(run_id, [])
            stages = [row["stage_id"] for row in rows]
            self.emit("roster.duplicate_run_id", level="window", collector="roster",
                      observed={"run_id": run_id, "dispatch_count": len(rows), "stages": stages,
                                "runs_roots": sorted({str(row["runs_root"]) for row in rows}),
                                "listings": list(listings.get(run_id, []))},
                      expected={"dispatch_count": 1},
                      detail=f"{run_id} is launched by {len(rows)} stages"
                             + (f" and listed by {len(listings[run_id])} plan-tree inputs" if run_id in listings else "")
                             + "; one bundle per run id, so later planned positions are never measured")

    def locate(self, run_id: str) -> Path | None:
        found = [root / run_id for root in self._runs_roots() if (root / run_id).is_dir()]
        if len(found) > 1:  # which bytes are the member is ambiguous; neither is used (L4's rule)
            self.emit("member.bytes_ambiguous", level="member", run_id=run_id, collector="roster",
                      observed={"locations": [str(path.parent) for path in found]})
        return found[0] if found else None

    def _runs_roots(self) -> list[Path]:
        return [root for root in (self.inputs.claim_runs_root, self.inputs.bound_runs_root) if root is not None]

    def assess(self) -> None:
        tasks = []
        for member in self.roster["members"]:
            path = self.locate(member["run_id"])
            if path is None:
                self.emit("member.bytes_missing", level="member", run_id=member["run_id"], collector="members",
                          stage_id=member.get("stage_id"), observed={"bundle": "absent"})
                continue
            tasks.append({"run_id": member["run_id"], "bundle_path": str(path),
                          "withheld_dir": str(self.withheld)})
        for result in assess_members(tasks, workers=self.seams.workers):
            self.members[result["run_id"]] = result
            self.spans[result["run_id"]] = result.get("spans") or {"member": None, "request": None}
        self.assessments_evidence = [{"path": "withheld/member-assessments.json", "sha256": write_json_once(
            self.withheld / "member-assessments.json",
            {"schema": "joulewise.b5_member_assessments.v1", "members": self.members})}]
        write_json_once(self.withheld / "spans.json", {"schema": "joulewise.b5_member_spans.v1",
                                                       "domain": "time.monotonic_ns", "spans": self.spans})

    def member_flags(self) -> None:
        roster = {member["run_id"]: member for member in self.roster["members"]}
        for run_id, result in self.members.items():
            member = roster[run_id]
            kwargs = {"level": "member", "run_id": run_id, "stage_id": member.get("stage_id"), "collector": "members"}
            if result.get("files_missing"):
                self.emit("member.bytes_missing", observed={"files_missing": result["files_missing"]}, **kwargs)
            unreadable = sorted(set(result["errors"]) & {"metadata", "summary", "summary_json", "config",
                                                          "config_json", "events"})
            if unreadable:
                self.emit("member.unreadable", observed={"parts": unreadable}, **kwargs)
            status = result.get("status")
            if status != "succeeded":
                if result.get("admission_decision") == "abort":
                    self.emit("member.admission_aborted", observed={"status": status}, **kwargs)
                else:
                    self.emit("member.status_not_succeeded", observed={"status": status}, **kwargs)
            if result.get("strict_problems") is None or result.get("strict_problems"):
                self.emit("member.strict_validation_failed", observed={
                    "problem_count": len(result.get("strict_problems") or []),
                    "validator_error": "strict" in result["errors"]},
                    evidence=getattr(self, "assessments_evidence", ()), **kwargs)
            rereduced = result.get("rereduced")
            if status == "succeeded" and (not isinstance(rereduced, Mapping) or not rereduced.get("identical_to_stored")):
                self.emit("member.reduction_mismatch", observed={
                    "rereduced": isinstance(rereduced, Mapping),
                    "identical_to_stored": rereduced.get("identical_to_stored") if isinstance(rereduced, Mapping) else None},
                    **kwargs)
            recorded, recomputed = result.get("anchor_recorded"), result.get("anchor_recomputed")
            if status == "succeeded" and recorded != "bounded":
                self.emit("member.anchor_not_bounded", observed={"recorded": recorded}, **kwargs)
            if recomputed is not None and recomputed != recorded:
                self.emit("member.anchor_recompute_mismatch",
                          observed={"recorded": recorded, "recomputed": recomputed}, **kwargs)
            elif recomputed is None and recorded not in (None, "not recorded") and status == "succeeded":
                self.emit("member.anchor_recompute_mismatch",
                          observed={"recorded": recorded, "recomputed": None}, **kwargs)
            quality = result.get("quality") or {}
            if quality.get("idle_window_suspect") is True:
                self.emit("member.idle_window_suspect", observed={"idle_window_suspect": True}, **kwargs)
            if quality.get("cooldown_cap_hit") is True:
                self.emit("member.cooldown_cap_hit", observed={"source": "summary"}, **kwargs)
            if result.get("thermal_pressure_elevated"):
                self.emit("thermal.powermetrics_pressure_elevated", observed={"source": "environment_admission"},
                          **kwargs)
            metadata_run_id = result.get("metadata_run_id")
            if metadata_run_id is not None and metadata_run_id != run_id:
                self.emit("roster.run_id_mismatch", observed={"recorded": metadata_run_id}, **kwargs)
            self._precheck_flags(member, result, kwargs)
            self._token_flags(member, result, kwargs)
            pair = result.get("battery_pair")
            if isinstance(pair, Mapping) and pair.get("status") in ("battery_float_confounded",):
                self.emit("battery.capture_pair_failed", observed={"status": pair["status"],
                                                                   "reasons": pair.get("reasons", [])[:8]}, **kwargs)
            elif not isinstance(pair, Mapping) or pair.get("status") in ("battery_float_evidence_missing",
                                                                        "unobserved_historical"):
                # Emitted by monitor_joins, which knows whether the journal covers the member.
                self.pair_missing[run_id] = pair.get("status") if isinstance(pair, Mapping) else None
            if result.get("spans", {}).get("member") is None and result.get("present"):
                self.emit("member.span_unknown", observed={"member_span": None}, **kwargs)

    def _precheck_flags(self, member: Mapping[str, Any], result: Mapping[str, Any], kwargs: Mapping[str, Any]) -> None:
        """The member's target-phase precheck, one flag per failing reason.

        Only target cells are read (``build_roster``): a non-target cell's
        precheck -- p42 on a decode member, which the registration expects to
        fail on every member (0.5) -- is no target-phase precheck, so it is
        disclosed through the s1-structural precheck counts and excludes
        nothing.
        """
        precheck = result.get("precheck") or {}
        for cell in member.get("cells", []):
            if cell.get("target") is False:
                continue
            path = cell.get("target_precheck_path")
            if not isinstance(path, list) or not path:
                continue
            node: Any = precheck.get(path[0])
            if len(path) > 1:
                node = node.get(path[1]) if isinstance(node, Mapping) else None
            reasons = node.get("reasons") if isinstance(node, Mapping) else None
            eligible = node.get("eligible") if isinstance(node, Mapping) else None
            if not isinstance(reasons, list):
                reasons = ["window_evidence_precheck_missing"]
            elif eligible is not True and not reasons:
                reasons = ["window_evidence_precheck_missing"]
            target = "/".join(map(str, path))
            for reason in sorted(set(reasons)):
                if reason in INSTRUMENT_REASONS:
                    self.emit(f"instrument.{reason}", observed={"target": target}, **kwargs)
                elif reason == "cooldown_cap_hit":
                    self.emit("member.cooldown_cap_hit", observed={"source": "precheck", "target": target}, **kwargs)
            if ENVELOPE_REASON in reasons:  # computed from a science energy: blinding RESTRICTED
                self.emit("member.anchor_energy_envelope_exceeded", observed={"target": target}, **kwargs)
            other = sorted(set(reasons) - INSTRUMENT_REASONS - {"cooldown_cap_hit", ENVELOPE_REASON})
            if other:
                restricted = any(restricted_reason(reason) for reason in other)
                self.emit("member.target_phase_precheck_failed", observed={"target": target, "reasons": other},
                          blinding=RESTRICTED if restricted else STRUCTURE, **kwargs)

    def _token_flags(self, member: Mapping[str, Any], result: Mapping[str, Any], kwargs: Mapping[str, Any]) -> None:
        if result.get("status") != "succeeded":
            return
        tokens = result.get("tokens") or {}
        registered_output = registered_prompt = None
        relative = member.get("config_path")
        if isinstance(relative, str):
            try:
                config = read_json(_resolve_repo_path(relative, self.pack_copy, self.repo_root_copy))
                workload = config.get("workload_profile", {})
                registered_output = workload.get("output_tokens")
                registered_prompt = workload.get("prompt_tokens")
            except (OSError, ValueError, AttributeError):
                pass
        for cell in member.get("cells", []):
            workload = cell.get("registered_workload") or {}
            if type(workload.get("prompt_tokens")) is int:
                registered_prompt = workload["prompt_tokens"]
            if type(workload.get("output_tokens")) is int and registered_output is None:
                registered_output = workload["output_tokens"]
        mismatches = {}
        if type(registered_output) is int:
            for name in ("output_realized", "output_requested", "output_emitted"):
                if tokens.get(name) != registered_output:
                    mismatches[name] = tokens.get(name)
        if type(registered_prompt) is int and tokens.get("prompt_realized") != registered_prompt:
            mismatches["prompt_realized"] = tokens.get("prompt_realized")
        if mismatches:
            self.emit("member.token_count_mismatch", observed=mismatches,
                      expected={"output_tokens": registered_output, "prompt_tokens": registered_prompt}, **kwargs)

    def roster_checks(self) -> None:
        known = {member["run_id"] for member in self.roster["members"]}
        chain_epoch = None
        try:
            chain_epoch = _num(read_json(self.inputs.night_dir / "chain.started").get("epoch_s"))
        except (OSError, ValueError, AttributeError):
            pass
        calibration = {name for name in (self.inputs.pre_attempt_id, self.inputs.post_attempt_id) if name}
        for root in self._runs_roots():
            if not root.is_dir():
                continue
            for path in sorted(root.iterdir()):
                if not path.is_dir() or path.name in {"campaign_manifests", "instrument_validation"} | calibration:
                    continue
                if path.name not in known and (path / "metadata.json").exists():
                    self.emit("roster.not_in_plan", level="member", run_id=path.name, collector="roster",
                              observed={"runs_root": root.name})
        for run_id, result in self.members.items():
            started = result.get("run_started_epoch_s")
            if chain_epoch is not None and started is not None and started < chain_epoch:
                self.emit("roster.before_chain_started", level="member", run_id=run_id, collector="roster",
                          observed={"run_started_before_chain_start": True})
        science = [member["run_id"] for member in self.roster["members"] if member["kind"] == "science"]
        if science and not any(run_id in self.members for run_id in science):
            self.emit("roster.no_science_bundles", level="window", collector="roster",
                      observed={"science_planned": len(science), "science_present": 0})

    def cooldown(self) -> None:
        from joulewise.analysis_engine.inputs import campaign_cooldown_evidence
        manifest_id = None
        manifest = self.pack_copy / "analysis_manifest_v3.json"
        if manifest.is_file():
            manifest_id = read_json(manifest).get("manifest_id")
        joined: dict[str, Any] = {}
        for root in self._runs_roots():
            if root.is_dir():
                for identifier in {manifest_id, None}:
                    try:
                        joined.update({key: value for key, value in campaign_cooldown_evidence(root, identifier).items()
                                       if key not in joined})
                    except Exception:  # an unreadable join verifies nothing
                        continue
        for run_id, result in self.members.items():
            if result.get("status") != "succeeded":
                continue
            evidence = joined.get(run_id)
            verdict = evidence.get("result") if isinstance(evidence, Mapping) else None
            verified = isinstance(evidence, Mapping) and evidence.get("verified") is True
            if verdict == "cap_hit":
                self.emit("member.cooldown_cap_hit", level="member", run_id=run_id, collector="cooldown",
                          observed={"source": "campaign_cooldown_evidence"})
            if not (verified and verdict in {"recovered", "first_run_exempt", "cap_hit"}):
                self.emit("member.cooldown_evidence_unverified", level="member", run_id=run_id, collector="cooldown",
                          observed={"verified": verified, "result": verdict})

    # -- 3. calibration bracket (memo 3.3 cure) --------------------------------
    def calibration(self) -> None:
        from joulewise import battery_float, calibration_bracketing as brackets
        from joulewise.calibration_ledger import load_calibration_ledger_snapshot, terminal_head_pin_for_session
        from joulewise.schemas import CampaignPolicy

        inputs = self.inputs
        roster = self.roster
        plan = roster.get("plan") or {}
        identity = roster.get("window_identity") or {}
        frozen_path = self.pack_copy / str(plan.get("path", "calibration_plan.json"))
        plan_sha = sha256_file(frozen_path) if frozen_path.is_file() else None
        acceptance_path = self.archive / "sources" / "inputs" / "acceptance.json"
        try:
            acceptance = brackets.load_calibration_acceptance_bound(acceptance_path) \
                if acceptance_path.is_file() else None
        except Exception:  # an unreadable acceptance sets no bound; flagged below
            acceptance = None
        # The acceptance sets the bracket bound, so its bytes are pinned against
        # the plan tree: floor trees carry issued_acceptance.artifact_sha256,
        # the contrast tree issued_artifact_sha256 (harvest_v5_g2b_window.py:286).
        expected_sha, pin_key = acceptance_pin(roster.get("acceptance_policy"))
        observed_sha = sha256_file(acceptance_path) if acceptance_path.is_file() else None
        if acceptance is None or expected_sha is None or observed_sha != expected_sha:
            self.emit("calibration.acceptance_mismatch", level="window", collector="calibration",
                      observed={"acceptance_loaded": acceptance is not None, "sha256": observed_sha},
                      expected={"sha256": expected_sha, "pin": pin_key})
        session_id = inputs.bracket_session_id
        ledger = self.archive / "sources" / "ledger" / "calibration_observation_ledger.jsonl"
        committed_pin = self.archive / "sources" / "ledger" / "calibration_ledger_head.json"
        if session_id is None or not ledger.is_file():
            self.emit("calibration.no_bracket", level="window", collector="calibration",
                      observed={"session_id": session_id, "ledger": ledger.is_file()})
            return
        try:
            candidate = terminal_head_pin_for_session(ledger, session_id=session_id)
        except Exception as exc:
            self.emit("calibration.no_bracket", level="window", collector="calibration",
                      observed={"terminal_pin": f"{type(exc).__name__}"})
            return
        candidate_path = self.derived / "terminal-pin.json"
        self.outputs["derived/terminal-pin.json"] = write_json_once(candidate_path, candidate)
        cutoff = (acceptance or {}).get("ledger_cutoff") or {}
        # The decision view carries the acceptance's ledger cutoff as its
        # baseline (memo 3.3).  Without it the bracket refuses
        # calibration_ledger_baseline_missing on good bytes.  Custody mode:
        # the harvest opens at chain exit and reads the captures at the
        # locators the ledger recorded, which is "issuing" resolution.
        # "read_replay" only adds remapping to relocated backup roots; a
        # re-harvest from relocated custody needs that mode and its own row
        # in tests/fixtures/custody_read_replay_allowlist.json.
        # Ledger custody is not re-verified wholesale (older captures may sit
        # elsewhere); this window's two captures are verified byte for byte
        # below, and bracket discovery reads every valid capture it uses.
        snapshot = load_calibration_ledger_snapshot(
            ledger, candidate_path, require_committed_pin=False, verify_custody=False, mode="issuing",
            repo_root=inputs.measurement_root, baseline_sequence=cutoff.get("sequence"),
            baseline_digest=cutoff.get("head_digest"))
        self.snapshot = snapshot
        committed = load_calibration_ledger_snapshot(
            ledger, committed_pin, require_committed_pin=False, verify_custody=False, mode="issuing",
            repo_root=inputs.measurement_root, baseline_sequence=cutoff.get("sequence"),
            baseline_digest=cutoff.get("head_digest")) if committed_pin.is_file() else None
        committed_value = read_json(committed_pin) if committed_pin.is_file() else {}
        relation = "equal" if committed_value.get("sequence") == candidate.get("sequence") else (
            "physical_ahead" if isinstance(committed_value.get("sequence"), int)
            and committed_value["sequence"] < candidate.get("sequence", -1) else "other")
        session = snapshot.bracket_session_by_id.get(session_id)
        committed_reasons = sorted(map(str, committed.refusal_reasons)) if committed is not None else []
        boundary = {"schema": TERMINAL_BOUNDARY_SCHEMA, "session_id": session_id,
                    "session_state": getattr(session, "state", None), "pin_relation": relation,
                    "refusal_code": ("calibration_ledger_head_mismatch"
                                     if "calibration_ledger_head_mismatch" in committed_reasons
                                     else (committed_reasons[0] if committed_reasons else None)),
                    "committed_pin_refusal_reasons": committed_reasons,
                    "terminal_head_pin_candidate": candidate}
        self.outputs["derived/terminal-boundary.json"] = write_json_once(self.derived / "terminal-boundary.json",
                                                                         boundary)
        if snapshot.refusal_reasons:
            self.emit("calibration.ledger_snapshot_refused", level="window", collector="calibration",
                      observed={"reasons": sorted(map(str, snapshot.refusal_reasons))})
        if session is None or session.state != "finalized":
            self.emit("calibration.no_bracket", level="window", collector="calibration",
                      observed={"session_state": getattr(session, "state", None)})
            return
        bound = {"plan_id": (session.plan_id, plan.get("plan_id")), "plan_sha256": (session.plan_sha256, plan_sha),
                 "runs_root": (session.runs_root, str(inputs.claim_runs_root)),
                 "window_id": (session.window_id, identity.get("window_id")),
                 "evidence_root_id": (session.evidence_root_id, identity.get("evidence_root_id"))}
        unbound = {key: {"session": pair[0], "plan": pair[1]} for key, pair in bound.items() if pair[0] != pair[1]}
        if unbound:
            self.emit("calibration.session_not_bound", level="window", collector="calibration",
                      observed=unbound)
        invalid = [slot for slot in ("pre", "post") if session.finalized_slots.get(slot) is None
                   or session.finalized_slots[slot].disposition != "valid"]
        if invalid:
            self.emit("calibration.capture_invalid", level="window", collector="calibration",
                      observed={"slots": invalid})
        for slot, observation in session.finalized_slots.items():
            capture = Path(observation.custody_locator)
            assessment = {"slot": slot, "path": str(capture), "present": capture.is_dir()}
            recorded = dict(observation.artifact_sha256 or {})
            differing = sorted(relative for relative, digest in recorded.items()
                               if not (capture / relative).is_file() or sha256_file(capture / relative) != digest)
            if not recorded or differing:
                self.emit("calibration.capture_invalid", level="window", collector="calibration",
                          observed={"slot": slot, "artifacts_differing": differing[:8],
                                    "artifacts_recorded": len(recorded)})
            try:
                evidence = read_json(capture / "instrument_evidence.json")
                anchor = evidence.get("clock_anchor") if isinstance(evidence.get("clock_anchor"), Mapping) else {}
                status = anchor.get("status")
                assessment["anchor"] = (status if status in ANCHOR_STATUSES
                                        else "not recorded" if status is None else "unbounded")
                assessment["span"] = member_spans({"uncertainty_evidence": {"clock_anchor": anchor}}, [])["member"]
            except (OSError, ValueError):
                assessment["anchor"] = "not recorded"
                assessment["span"] = None
            try:
                verdict = battery_float.authenticate_capture(capture)
                assessment["battery_pair"] = verdict.status
                if verdict.status == "battery_float_confounded":
                    self.emit("calibration.capture_battery_pair_failed", level="window", collector="calibration",
                              observed={"slot": slot, "reasons": list(verdict.reasons)[:8]})
            except battery_float.CustodyFailure:
                # A battery raw file whose recorded digest no longer matches its
                # bytes.  Battery raw files are not governed ledger artifacts,
                # so nothing else checks them (core-prune N7.1).
                assessment["battery_pair"] = "error:CustodyFailure"
                self.emit("calibration.capture_invalid", level="window", collector="calibration",
                          observed={"slot": slot, "reason": "battery_raw_custody_failed"})
            except Exception as exc:
                assessment["battery_pair"] = f"error:{type(exc).__name__}"
            self.capture_assessments[observation.attempt_id] = assessment
        try:
            binding = brackets.build_calibration_bracket_binding(
                snapshot, session_id=session_id, window_id=identity.get("window_id"), plan_id=plan.get("plan_id"),
                plan_sha256=plan_sha, evidence_root_id=identity.get("evidence_root_id"),
                runs_root=inputs.claim_runs_root)
        except Exception as exc:
            self.emit("calibration.binding_failed", level="window", collector="calibration",
                      observed={"error_type": type(exc).__name__})
            return
        self.binding = binding
        self.outputs["derived/bracket-binding.json"] = write_once(
            self.derived / "bracket-binding.json", canonical_json_bytes(binding) + b"\n")
        policy_relative = (self.roster.get("campaign_policy") or {}).get("path")
        if not isinstance(policy_relative, str):
            raise HarvestFault("campaign_policy_unpinned")
        policy = CampaignPolicy.from_mapping(read_json(self.repo_root_copy / policy_relative))
        valid = [Path(result["bundle_path"]) for run_id, result in sorted(self.members.items())
                 if result.get("strict_valid") and result.get("status") == "succeeded"
                 and result.get("anchor_recorded") == "bounded"
                 and _under(Path(result["bundle_path"]), inputs.claim_runs_root)]
        assessment, reasons = brackets.calibration_bracket_for_bundles(
            inputs.claim_runs_root, valid, policy.calibration_bracketing, mode="issuing",
            ledger_snapshot=snapshot, bracket_binding=binding, bracket_window_id=identity.get("window_id"),
            bracket_plan_id=plan.get("plan_id"), bracket_plan_sha256=plan_sha,
            bracket_evidence_root_id=identity.get("evidence_root_id"))
        write_json_once(self.withheld / "bracket-evaluation.json",
                        {"assessment": assessment, "reasons": list(reasons), "members": len(valid)})
        if assessment.get("status") != "passed" or reasons:
            self.emit("calibration.bracket_acceptance_failed", level="window", collector="calibration",
                      observed={"status": assessment.get("status"), "reasons": sorted(map(str, reasons))})

    # -- NEG-8 bound (registration 5.3) ---------------------------------------
    def neg8_bound(self) -> None:
        """Is the window's NEG-8 bound derived?  ``neg8.bound_not_derived`` unless it is.

        Derived means the bound artifact in the bound runs root validates
        (``whole_window.validate_neg8_drift_bound_artifact``, arithmetic and
        corpus identity) against either

        * the committed 12-member corpus (``load_neg8_drift_bound_artifact``), or
        * the window's collected corpus manifest (registration 5.3: at least
          10 of the 12): the manifest the chain's prune step wrote, located by
          ``night/hazard_result.json`` ``neg8_corpus.collected_manifest``, whose
          bytes hash to the recorded SHA-256, whose header equals the committed
          manifest's, whose members are committed members in committed order
          (at least ``NEG8_DRIFT_MINIMUM_N``), and which left out only members
          that did not succeed, or, on a HAZARD bound root, that succeeded but
          the core's mint drops (``neg8_mint_drops``; each such drop is
          ``neg8.corpus_member_dropped``).  Validation then takes those
          custodied bytes as ``reference_corpus_bytes`` with
          ``require_corpus_identity=True``.

        On a HAZARD bound root the bound carries no launch-lineage stamp, so
        either way it counts as derived only when every member it names is one
        bundle in the bound root whose bytes, mint predicates and both
        claim-family points re-derive to what the bound recorded
        (``neg8_bound_member_problems``).

        The committed manifest is the archived repo copy the pack's
        bound-derivation stage names, checked against the plan tree's pin.
        Structure only goes to ``derived/neg8-bound.json``; the bound itself
        (an energy) never leaves the bound runs root.
        """
        from joulewise import whole_window as ww
        check: dict[str, Any] = {
            "schema": NEG8_CHECK_SCHEMA, "artifact": None, "derived_from": None,
            "minimum_n": ww.NEG8_DRIFT_MINIMUM_N, "committed_manifest": None, "collected_manifest": None,
            "members_committed": None, "members_collected": None, "dropped_bundle_ids": None, "mint_rule": None,
            "problems": []}
        self.neg8 = check
        problems: list[str] = check["problems"]
        bound_root = self.inputs.bound_runs_root
        bound_path = bound_root / NEG8_BOUND_NAME if bound_root is not None else None
        raw: bytes | None = None
        if bound_path is None:
            problems.append("bound_runs_root_unresolved")
        else:
            try:
                raw = bound_path.read_bytes()
            except OSError:
                problems.append("bound_artifact_absent")
        value: Any = None
        if raw is not None:
            check["artifact"] = {"path": NEG8_BOUND_NAME, "sha256": sha256_bytes(raw)}
            try:
                value = json.loads(raw, object_pairs_hook=_unique_pairs)
            except ValueError:
                problems.append("bound_artifact_unreadable")
        if isinstance(value, Mapping):
            try:
                registered = ww.load_neg8_drift_bound_artifact(bound_path) is not None
            except Exception:  # the core reader failing verifies nothing
                registered = False
            derived_from = "registered_corpus" if registered else None
            if not registered:
                collected = self._collected_corpus_bytes(check)
                valid = False
                if collected is not None:
                    try:
                        valid = ww.validate_neg8_drift_bound_artifact(
                            value, reference_corpus_bytes=collected, require_corpus_identity=True)
                    except Exception:
                        valid = False
                    if not valid:
                        problems.append("bound_does_not_validate_against_collected_corpus")
                derived_from = "collected_subset" if valid else None
            if derived_from is not None and self._bound_root_is_hazard():
                # The HAZARD bound carries no launch-lineage stamp: tie its
                # numbers to the bundles in this bound root (core-prune N2, F2).
                check["members_rederived"] = False
                try:
                    member_problems = neg8_bound_member_problems(value, bound_root)
                except Exception as exc:
                    member_problems = [f"bound_member_check_failed:{type(exc).__name__}"]
                if member_problems:
                    problems.extend(member_problems[:8])
                    derived_from = None
                else:
                    check["members_rederived"] = True
            check["derived_from"] = derived_from
            if derived_from == "collected_subset":
                self.neg8_collected_bound = value
        elif value is not None:
            problems.append("bound_artifact_not_an_object")
        self.outputs["derived/neg8-bound.json"] = write_json_once(self.derived / "neg8-bound.json", check)
        if check["derived_from"] is None:
            self.emit("neg8.bound_not_derived", level="window", collector="neg8",
                      observed={"artifact": raw is not None, "problems": problems[:8],
                                "members_collected": check["members_collected"],
                                "minimum_n": check["minimum_n"]})

    def _bound_root_is_hazard(self) -> bool:
        """The core mint's own dispatch: the bound runs root carries the hazard lineage locator."""
        from joulewise import window_lineage
        root = self.inputs.bound_runs_root
        return root is not None and window_lineage.is_hazard_runs_root(root)

    def _committed_corpus_bytes(self, check: dict[str, Any]) -> bytes | None:
        """The committed settled-corpus manifest the pack's bound derivation names, from preserved bytes."""
        problems = check["problems"]
        tree = read_json(self.pack_copy / "plan_tree.json")
        named = set()
        for stage in tree.get("stage_graph") or []:
            if not isinstance(stage, Mapping) or stage.get("kind") != "bound_derivation":
                continue
            for command in ((stage.get("launch") or {}).get("commands") or []):
                arguments = ((command or {}).get("argv_template") or {}).get("arguments") or []
                for flag, argument in zip(arguments, arguments[1:]):
                    if isinstance(flag, Mapping) and flag.get("value") == "--derive-neg8-drift-bound" \
                            and isinstance(argument, Mapping) and argument.get("kind") == "repo_path" \
                            and isinstance(argument.get("value"), str):
                        named.add(argument["value"])
        if len(named) != 1:
            problems.append(f"committed_manifest_unnamed:{len(named)}")
            return None
        relative = named.pop()
        pins = {row["sha256"] for row in pinned_files(tree, pack_root=self.pack_copy, repo_root=self.repo_root_copy)
                if row["path"] == relative}
        check["committed_manifest"] = {"path": relative, "pinned_sha256": sorted(pins)}
        if len(pins) != 1:
            problems.append("committed_manifest_unpinned")
            return None
        try:
            raw = (self.repo_root_copy / relative).read_bytes()
        except OSError:
            problems.append("committed_manifest_absent")
            return None
        check["committed_manifest"]["sha256"] = sha256_bytes(raw)
        if sha256_bytes(raw) not in pins:
            problems.append("committed_manifest_differs_from_pin")
            return None
        return raw

    def _collected_corpus_bytes(self, check: dict[str, Any]) -> bytes | None:
        """The custodied collected manifest, if it is a valid subset of the committed one (else None)."""
        problems = check["problems"]
        try:
            record = read_json(self.inputs.night_dir / HAZARD_RESULT_NAME)
        except (OSError, ValueError):
            problems.append("hazard_result_unreadable")
            return None
        corpus = record.get("neg8_corpus") if isinstance(record, Mapping) else None
        locator = corpus.get("collected_manifest") if isinstance(corpus, Mapping) else None
        if not isinstance(locator, Mapping) or not isinstance(locator.get("path"), str) \
                or not _is_sha256(locator.get("sha256")):
            problems.append("collected_manifest_unrecorded")
            return None
        recorded = Path(locator["path"])
        raw = None
        # The recorded absolute path, or the same file in this custody root if it moved.
        for candidate in (recorded, self.inputs.night_dir / "transcript" / recorded.name):
            try:
                raw = candidate.read_bytes()
                break
            except OSError:
                continue
        if raw is None:
            problems.append("collected_manifest_absent")
            return None
        check["collected_manifest"] = {"sha256": sha256_bytes(raw), "recorded_sha256": locator["sha256"]}
        if sha256_bytes(raw) != locator["sha256"]:
            problems.append("collected_manifest_differs_from_recorded_sha256")
            return None
        committed_raw = self._committed_corpus_bytes(check)
        if committed_raw is None:
            return None
        try:
            collected = json.loads(raw, object_pairs_hook=_unique_pairs)
            committed = json.loads(committed_raw, object_pairs_hook=_unique_pairs)
        except ValueError:
            problems.append("corpus_manifest_unreadable")
            return None
        header = ("schema_version", "corpus_id", "freeze_status", "condition_id")
        if not isinstance(collected, Mapping) or not isinstance(committed, Mapping) \
                or set(collected) != set(committed) or any(collected.get(key) != committed.get(key) for key in header):
            problems.append("collected_manifest_header_differs")
            return None
        kept, listed = collected.get("members"), committed.get("members")
        if not isinstance(kept, list) or not isinstance(listed, list):
            problems.append("corpus_members_unreadable")
            return None
        check["members_committed"], check["members_collected"] = len(listed), len(kept)
        listed_rows = [canonical_json_bytes(member) for member in listed]
        position = 0  # kept must be listed members, each once, in committed order
        for member in kept:
            row = canonical_json_bytes(member)
            while position < len(listed_rows) and listed_rows[position] != row:
                position += 1
            if position == len(listed_rows):
                problems.append("collected_manifest_not_a_member_subset")
                return None
            position += 1
        kept_rows = {canonical_json_bytes(member) for member in kept}
        dropped = [member for member in listed if canonical_json_bytes(member) not in kept_rows]
        check["dropped_bundle_ids"] = [member.get("bundle_id") if isinstance(member, Mapping) else None
                                       for member in dropped]
        from joulewise.whole_window import NEG8_DRIFT_MINIMUM_N
        if len(kept) < NEG8_DRIFT_MINIMUM_N:
            problems.append("collected_members_below_minimum")
            return None
        # The registered rule (5.3) keeps every corpus member that was collected
        # and succeeded; a dropped member that succeeded is a selected corpus,
        # unless the core's HAZARD mint, evaluated here on the same bound root
        # over the same succeeded members, drops it (core-prune N2, A3).
        root = self.inputs.bound_runs_root
        dropped_succeeded = [member for member in dropped if _corpus_member_status(root, member) == "succeeded"]
        reasons: dict[str, str] = {}
        if dropped_succeeded:
            reasons, check["mint_rule"] = neg8_mint_drops(
                root, committed, [member for member in listed if _corpus_member_status(root, member) == "succeeded"])
        omitted = [(member.get("bundle_id"), reasons[member.get("bundle_id")]) for member in dropped_succeeded
                   if member.get("bundle_id") in reasons]
        selected = [member.get("bundle_id") for member in dropped_succeeded if member.get("bundle_id") not in reasons]
        if selected:
            problems.append("dropped_member_succeeded:" + ",".join(map(str, selected[:4])))
            return None
        for bundle_id, reason in omitted:
            placed = isinstance(bundle_id, str) and bool(bundle_id)
            self.emit("neg8.corpus_member_dropped", level="member" if placed else "window",
                      run_id=bundle_id if placed else None, collector="neg8",
                      observed={"bundle_id": bundle_id, "reason": reason})
        return raw

    # -- whole-window verdict and the NEG-8 screen ----------------------------
    def whole_window(self) -> None:
        from joulewise.whole_window import validate_whole_window_verdict_row
        inputs = self.inputs
        runs = inputs.claim_runs_root
        verdict_path = runs / "whole-window-verdict.json"
        if not verdict_path.is_file():
            # whole_window.verdict_absent removes the window; the screen it would hold is absent with it.
            self.emit("whole_window.verdict_absent", level="window", collector="whole_window",
                      observed={"verdict": "absent"})
            return
        raw = verdict_path.read_bytes()
        log = runs / "campaign_log.jsonl"
        rows = [line for line in (log.read_bytes().splitlines(keepends=True) if log.is_file() else []) if line.strip()]
        matches = [line for line in rows if b'"idle_admission_whole_window_verdict"' in line]
        try:
            row = json.loads(raw)
        except ValueError:
            row = None
        if not isinstance(row, Mapping):
            self.emit("whole_window.verdict_unauthenticated", level="window", collector="whole_window",
                      observed={"verdict": "malformed"})
            # The NEG-8 screen's result is held in the verdict; unreadable is not passed.
            self.emit("neg8.screen_failed", level="window", collector="whole_window",
                      observed={"reasons": ["verdict_unreadable"], "decision": None, "conditions": []})
            return
        authentic = False
        try:
            authentic = bool(len(matches) == 1 and matches[0] == raw
                             and validate_whole_window_verdict_row(row, runs, set(row.get("bundle_ids", []))).authentic)
        except Exception:
            authentic = False
        if not authentic:
            self.emit("whole_window.verdict_unauthenticated", level="window", collector="whole_window",
                      observed={"verdict_rows": len(matches)})
        status = row.get("status")
        if status != "passed":
            conditions = (row.get("idle_admission_core") or {}).get("conditions") \
                if isinstance(row.get("idle_admission_core"), Mapping) else None
            self.emit("whole_window.not_passed", level="window", collector="whole_window",
                      observed={"status": status, "conditions": sorted(map(str, conditions or []))})
        self.neg8_screen(row, authentic=authentic)

    def neg8_screen(self, row: Mapping[str, Any], *, authentic: bool = False) -> None:
        """``neg8.screen_failed`` from the verdict's NEG-8 result (registration 6.5).

        ``whole_window.not_passed`` is disclosed only, because any one member's
        admission failure fails it; the NEG-8 screen it holds is window-level
        and carried here.  Not passed means any of: no NEG-8 bracket in the
        verdict's core, a bracket decision other than ``passed``, or any
        ``neg8_*`` condition in the core or the bracket (the registered ones,
        ``whole_window.NEG8_POINT_DRIFT_CONDITION_CODES``, and the bracket's
        shape conditions).

        One case is evaluated again.  The verdict writer
        (``run_campaign --whole-window-verdict``) authenticates a bound only
        against the committed 12-member corpus, so a bound derived from the
        collected 10 or 11 members (``neg8_bound``: ``collected_subset``)
        always reaches its screen as no bound, and the stored bracket carries
        the two ``*_UNDERIVED`` conditions.  When those are the verdict's only
        NEG-8 conditions, ``_neg8_rescreen`` evaluates the screen with the
        core's own evaluator against the validated collected bound, and that
        result alone decides ``neg8.screen_failed``
        (``observed.collected_bound_rescreen``).  A re-evaluation that cannot
        run leaves the screen failed.
        """
        from joulewise import whole_window as ww
        core = row.get("idle_admission_core") if isinstance(row.get("idle_admission_core"), Mapping) else None
        bracket = core.get("neg8_bracket") if core is not None else None
        bracket = bracket if isinstance(bracket, Mapping) else None
        listed = list(core.get("conditions") or []) if core is not None and isinstance(core.get("conditions"), list) \
            else []
        conditions = {item for item in listed if isinstance(item, str) and item.startswith("neg8_")}
        if bracket is not None and isinstance(bracket.get("conditions"), list):
            conditions |= {item for item in bracket["conditions"] if isinstance(item, str)}
        decision = bracket.get("decision") if bracket is not None else None
        reasons = []
        if bracket is None:
            reasons.append("bracket_absent")
        elif decision != "passed":
            reasons.append("bracket_not_passed")
        if conditions:
            reasons.append("neg8_conditions")
        if not reasons:
            return
        observed: dict[str, Any] = {
            "reasons": reasons, "decision": decision if isinstance(decision, str) else None,
            "conditions": sorted(conditions)[:16],
            "registered_conditions": sorted(conditions & ww.NEG8_POINT_DRIFT_CONDITION_CODES)}
        underived = {ww.CONDITION_NEG8_DRIFT_BOUND_UNDERIVED, ww.CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED}
        if (self.neg8 or {}).get("derived_from") == "collected_subset" and conditions & underived:
            rescreen = self._neg8_rescreen(row, bracket, conditions - underived, authentic=authentic)
            observed["collected_bound_rescreen"] = rescreen
            if rescreen["evaluated"] and rescreen["decision"] == "passed" and not rescreen["conditions"]:
                return  # the screen passed against the window's own validated bound
        self.emit("neg8.screen_failed", level="window", collector="whole_window", observed=observed)

    def _neg8_rescreen(self, row: Mapping[str, Any], bracket: Mapping[str, Any] | None, other_conditions: set[str],
                       *, authentic: bool) -> dict[str, Any]:
        """The verdict's NEG-8 screen evaluated against the validated collected bound.

        Runs only when the stored screen failed for want of a bound alone: a
        bracket whose NEG-8 conditions (with the core's) are the two
        ``*_UNDERIVED`` ones and nothing else.  The bracket is re-derived from
        primary evidence by ``whole_window._derived_neg8_decision``, the
        evaluator ``validate_whole_window_verdict_row`` replays, over the
        inputs that validator selects (``verdict_neg8_sources``: source
        manifests authenticated at their recorded digests, projected onto the
        evaluation basis), with the collected bound in place of the absent one
        and the bound's freshness evaluated at the verdict's completion time.
        Each family's bound-independent fields (endpoints, protocol, point
        delta) must then equal the stored bracket's: otherwise these are not
        the reference bundles the verdict was written from, and nothing is
        evaluated.

        Row authenticity is recorded (``verdict_authenticated``), not
        required: the harvest validates rows without a consumption session,
        which the row validator requires under every consumption semantics, so
        no row is authentic here (``whole_window.verdict_unauthenticated`` is
        disclosed), and the screen is re-derived rather than read from the row.

        The re-derived bracket (energies) goes to
        ``withheld/neg8-rescreen-bracket.json``; its decision, conditions and
        freshness verdict go to ``derived/neg8-screen.json``.
        """
        from joulewise import whole_window as ww
        result: dict[str, Any] = {"evaluated": False, "decision": None, "conditions": [], "freshness": None,
                                  "evaluated_at_source": None, "verdict_authenticated": bool(authentic),
                                  "problems": []}
        problems: list[str] = result["problems"]
        if bracket is None:
            problems.append("bracket_absent")
        if other_conditions:
            problems.append("conditions_beyond_bound_underived")
        bound = getattr(self, "neg8_collected_bound", None)
        if bound is None:
            problems.append("collected_bound_unavailable")
        evaluated_at = None
        scope = row.get("evaluation_scope")
        for source, text in (("evaluation_scope.completed_at", scope.get("completed_at")
                               if isinstance(scope, Mapping) else None), ("timestamp", row.get("timestamp"))):
            evaluated_at = _epoch_s(text)
            if evaluated_at is not None:
                result["evaluated_at_source"] = source
                break
        if evaluated_at is None:
            problems.append("evaluation_time_unrecorded")
        derived: Any = None
        if not problems:
            runs = self.inputs.claim_runs_root
            try:
                sources = verdict_neg8_sources(row, runs)
                if isinstance(sources, str):
                    problems.append(sources)
                else:
                    manifests, current, policy = sources
                    derived, problem = ww._derived_neg8_decision(
                        manifests, runs, policy, current=current, point_drift=True,
                        drift_bound_artifact=bound, return_bracket=True,
                        freshness_evaluated_at_s=evaluated_at)
                    if problem is not None:
                        problems.append(f"rederivation_failed:{problem}")
                    elif not isinstance(derived, Mapping):
                        problems.append("rederivation_invalid")
                    elif _neg8_endpoints(derived) is None or _neg8_endpoints(derived) != _neg8_endpoints(bracket) \
                            or derived.get("estimand") != (bracket or {}).get("estimand"):
                        problems.append("rederivation_differs_from_stored_bracket")
            except Exception as exc:  # the core failing evaluates nothing
                problems.append(f"rederivation_raised:{type(exc).__name__}")
        if isinstance(derived, Mapping):
            write_json_once(self.withheld / "neg8-rescreen-bracket.json",
                            {"schema": NEG8_SCREEN_SCHEMA, "bracket": derived})
            if not problems:
                freshness = derived.get("bound_freshness") if isinstance(derived.get("bound_freshness"), Mapping) \
                    else {}
                listed = derived.get("conditions") if isinstance(derived.get("conditions"), list) else ["unreadable"]
                result.update({
                    "evaluated": True,
                    "decision": derived.get("decision") if isinstance(derived.get("decision"), str) else None,
                    "conditions": sorted(map(str, listed)),
                    "freshness": {"decision": freshness.get("decision"),
                                  "triggers": list(freshness.get("triggered_rederivation_reasons") or [])}})
        decision = bracket.get("decision") if bracket is not None else None
        self.outputs["derived/neg8-screen.json"] = write_json_once(self.derived / "neg8-screen.json", {
            "schema": NEG8_SCREEN_SCHEMA, "bound_derived_from": (self.neg8 or {}).get("derived_from"),
            "stored": {"decision": decision if isinstance(decision, str) else None,
                       "conditions_beyond_bound_underived": sorted(other_conditions)},
            "rescreen": result})
        return result

    def prepare_desk_verdict(self) -> None:
        """Produce the whole-window verdict with the production writer, if absent.

        Runs before the archive.  Only the bracket binding, the verdict file and
        one appended campaign-log row may change; anything else is a flag.
        """
        inputs = self.inputs
        runs = inputs.claim_runs_root
        if (runs / "whole-window-verdict.json").exists() or inputs.bracket_session_id is None:
            return
        binding_target = runs / "bracket-binding.json"
        before = tree_inventory(runs)
        log = runs / "campaign_log.jsonl"
        old_log = log.read_bytes() if log.is_file() else b""
        policy = self._policy_path()
        python = inputs.measurement_root / ".venv" / "bin" / "python"
        argv = [str(python if python.exists() else self.seams.python), "-B",
                str(inputs.measurement_root / "scripts" / "run_campaign.py"), "--whole-window-verdict",
                "--runs-dir", str(runs), "--log", str(log), "--campaign-policy", str(policy),
                "--bracket-binding", str(binding_target),
                "--whole-window-verdict-output", str(runs / "whole-window-verdict.json"),
                "--calibration-ledger", str(inputs.ledger_path), "--head-pin", str(inputs.head_pin_path)]
        if inputs.bound_runs_root is not None:
            argv += ["--neg8-drift-bound", str(inputs.bound_runs_root / "neg8-drift-bound.json")]
        if not binding_target.exists():
            binding = self._desk_binding()
            if binding is None:
                self.emit("whole_window.producer_failed", level="window", collector="desk",
                          observed={"step": "bracket_binding"})
                return
            write_once(binding_target, canonical_json_bytes(binding) + b"\n")
        result = self.seams.runner(argv, capture_output=True, text=True, check=False, timeout=1800,
                                   cwd=str(inputs.measurement_root))
        transcript = (getattr(result, "stdout", "") or "") + (getattr(result, "stderr", "") or "")
        self._desk_transcript = transcript
        if result.returncode not in (0, 1):
            self.emit("whole_window.producer_failed", level="window", collector="desk",
                      observed={"step": "whole_window_verdict", "returncode": result.returncode})
        after = tree_inventory(runs)
        allowed = {"campaign_log.jsonl", "bracket-binding.json", "whole-window-verdict.json", CAMPAIGN_LOCK_NAME}
        changed = sorted(name for name in set(before) | set(after)
                         if name not in allowed and before.get(name) != after.get(name))
        appended_ok = (log.read_bytes().startswith(old_log) if log.is_file() else not old_log)
        if changed or not appended_ok:
            self.emit("records.source_changed_during_harvest", level="window", collector="desk",
                      observed={"changed": changed[:16], "log_prefix_preserved": appended_ok})

    def _desk_binding(self) -> dict[str, Any] | None:
        from joulewise import calibration_bracketing as brackets
        from joulewise.calibration_ledger import load_calibration_ledger_snapshot, terminal_head_pin_for_session
        inputs = self.inputs
        try:
            tree = read_json(inputs.pack_root / "plan_tree.json")
            acceptance = brackets.load_calibration_acceptance_bound(self._acceptance_path()) or {}
            cutoff = acceptance.get("ledger_cutoff") or {}
            with tempfile.TemporaryDirectory(prefix="b5-desk-pin-") as scratch:
                pin = Path(scratch) / "terminal-pin.json"
                pin.write_text(json.dumps(terminal_head_pin_for_session(inputs.ledger_path,
                                                                        session_id=inputs.bracket_session_id)))
                snapshot = load_calibration_ledger_snapshot(
                    inputs.ledger_path, pin, require_committed_pin=False, verify_custody=False, mode="issuing",
                    repo_root=inputs.measurement_root, baseline_sequence=cutoff.get("sequence"),
                    baseline_digest=cutoff.get("head_digest"))
                frozen = inputs.pack_root / tree["plan"]["path"]
                return brackets.build_calibration_bracket_binding(
                    snapshot, session_id=inputs.bracket_session_id, window_id=tree["window_identity"]["window_id"],
                    plan_id=tree["plan"]["plan_id"], plan_sha256=sha256_file(frozen),
                    evidence_root_id=tree["window_identity"]["evidence_root_id"], runs_root=inputs.claim_runs_root)
        except Exception:
            return None

    # -- clock systematic -----------------------------------------------------
    def clock_systematic(self) -> None:
        """Port of harvest_v5_g2b_window.capture_clock_members (:347) and clock_majority."""
        statuses = [result.get("anchor_recorded", "not recorded") for result in self.members.values()]
        statuses += [capture.get("anchor", "not recorded") for capture in self.capture_assessments.values()]
        recorded = [status for status in statuses if status != "not recorded"]
        non_bounded = sum(status != "bounded" for status in recorded)
        minimum = int(self.inputs.thresholds["clock_systematic_min_recorded"])
        if len(recorded) >= minimum and 2 * non_bounded > len(recorded):
            self.emit("clock.systematic", level="window", collector="clock_systematic",
                      observed={"recorded": len(recorded), "non_bounded": non_bounded})

    # -- 4. arm-path NUMBER replay from preserved bytes -----------------------
    def pack_identity(self) -> None:
        pack, repo = self.pack_copy, self.repo_root_copy
        tree_path = pack / "plan_tree.json"
        tree = read_json(tree_path)
        mismatches = []
        for row in pinned_files(tree, pack_root=pack, repo_root=repo):
            target = repo / row["path"]
            observed = sha256_file(target) if target.is_file() else "absent"
            if observed != row["sha256"]:
                mismatches.append({"path": row["path"], "expected": row["sha256"], "observed": observed})
        sidecar = pack / "plan_tree.sha256"
        tree_sha = sha256_file(tree_path)
        if sidecar.is_file():
            token = sidecar.read_text().split()[0] if sidecar.read_text().split() else ""
            if token != tree_sha:
                mismatches.append({"path": f"{_relative_to(tree_path, repo)}", "expected": token,
                                   "observed": tree_sha, "pin": "sidecar"})
        sealed = self._sealed()
        tree_relative = _relative_to(tree_path, repo)
        if sealed is None or tree_relative not in sealed:
            # The plan tree's own pins were still compared above; what could not
            # be compared is the plan tree against its digest registered at H_claim.
            self.emit("pack.identity_unmeasured", level="window", collector="pack_identity",
                      observed={"check": "registered_digests", "plan_tree": tree_relative,
                                "missing_input": "sealed_inventory" if sealed is None else "plan_tree_row"})
        else:
            pack_relative = _relative_to(pack, repo) or ""
            for relative, digest in sorted(sealed.items()):
                if not relative.startswith(pack_relative + "/") or relative in PIN_ONLY_PATHS:
                    continue
                target = repo / relative
                observed = sha256_file(target) if target.is_file() else "absent"
                if observed != digest:
                    mismatches.append({"path": relative, "expected": digest, "observed": observed, "pin": "sealed"})
        if mismatches:
            self.emit("pack.identity_mismatch", level="window", collector="pack_identity",
                      observed={"mismatches": mismatches[:32], "mismatch_count": len(mismatches)},
                      evidence=[{"path": "sources/SHA256SUMS", "sha256": sha256_file(self.archive / "sources" / "SHA256SUMS")}])
        # Member config bytes: the bundle's config.json is the normalized form of
        # the pinned pack config.  Wrong bytes mean a different member was measured.
        from joulewise.schemas import BenchmarkConfig
        for member in self.roster["members"]:
            result = self.members.get(member["run_id"])
            relative = member.get("config_path")
            if result is None or not isinstance(relative, str) or result.get("config_sha256") is None:
                continue
            source = _resolve_repo_path(relative, pack, repo)
            try:
                raw = source.read_bytes()
                normalized = (json.dumps(BenchmarkConfig.from_mapping(json.loads(raw)).to_dict(), indent=2,
                                         sort_keys=True) + "\n").encode()
                expected = sha256_bytes(normalized)
                pinned_ok = sha256_bytes(raw) == member.get("config_sha256")
            except Exception:
                expected, pinned_ok = None, False
            if expected != result["config_sha256"] or not pinned_ok:
                self.emit("member.config_not_in_inventory", level="member", run_id=member["run_id"],
                          collector="pack_identity",
                          observed={"bundle_config_sha256": result["config_sha256"], "pack_config_pinned": pinned_ok},
                          expected={"normalized_pack_config_sha256": expected})

    def _sealed(self) -> dict[str, str] | None:
        path = self.archive / "sources" / "inputs" / "sealed_inventory.json"
        return _inventory_map(read_json(path))[0] if path.is_file() else None

    def code_identity(self) -> None:
        inputs = self.inputs
        differences: list[dict[str, Any]] = []
        unmeasured: list[dict[str, Any]] = []
        chain = inputs.chain_path
        if chain is not None and inputs.chain_sha256_path is not None:
            observed = sha256_file(chain) if chain.is_file() else "absent"
            sidecar = inputs.chain_sha256_path.read_text().split() if inputs.chain_sha256_path.is_file() else []
            if not sidecar or sidecar[0] != observed:
                differences.append({"check": "chain_sidecar", "observed": observed,
                                    "expected": sidecar[0] if sidecar else "absent",
                                    "legacy_code": "night_chain_digest_mismatch"})
        else:
            unmeasured.append({"check": "chain_sidecar", "missing_input": "chain_path" if chain is None
                               else "chain_sha256_path"})
        sealed_path = self.archive / "sources" / "inputs" / "sealed_inventory.json"
        sealed_value = read_json(sealed_path) if sealed_path.is_file() else None
        sealed, sealed_head = _inventory_map(sealed_value)
        executed_path = inputs.executed_inventory_path
        executed = executed_head = porcelain = None
        if executed_path is not None and executed_path.is_file():
            value = read_json(executed_path)
            executed, executed_head = _inventory_map(value)
            porcelain = _inventory_checkout(value).get("status_porcelain")
            if not executed:
                unmeasured.append({"check": "executed_inventory", "missing_input": "executed_files"})
        else:
            unmeasured.append({"check": "executed_inventory", "missing_input": "executed_inventory"})
        if sealed is None:
            unmeasured.append({"check": "executed_inventory", "missing_input": "sealed_inventory"})
        if sealed is not None and executed:
            # Executed code is what the driver inventories: joulewise/, scripts/
            # and the pack (L2, joulewise.b5.driver.executed_inventory), always.
            # A sealed file outside those roots is not executed code here, and
            # declared sealed roots only narrow them, never widen them: the same
            # scope as joulewise.flags.collect._window_scope (registration 14 Q2),
            # so a sealed inventory listing every pack never makes a window
            # differ.  A path both inventories list is compared wherever it lies.
            declared = sealed_value.get("roots") if isinstance(sealed_value, Mapping) else None
            declared_roots = tuple(str(root).rstrip("/") for root in declared) \
                if isinstance(declared, list) and declared else None
            pack_relative = _relative_to(inputs.pack_root, inputs.measurement_root)
            roots = CODE_PREFIXES + ((pack_relative + "/",) if pack_relative else ())

            def in_scope(relative: str) -> bool:
                return relative.startswith(roots) and (declared_roots is None or any(
                    relative == root or relative.startswith(root + "/") for root in declared_roots))

            for relative in sorted(set(sealed) | set(executed)):
                if relative in PIN_ONLY_PATHS or not (in_scope(relative) or (relative in sealed
                                                                             and relative in executed)):
                    continue
                if sealed.get(relative) != executed.get(relative):
                    differences.append({"check": "executed_inventory", "path": relative,
                                        "expected": sealed.get(relative, "absent"),
                                        "observed": executed.get(relative, "absent")})
        # H_claim is the head sealed with the registration; the plan's copy is a fallback.
        h_claim = self.h_claim = sealed_head or inputs.h_claim
        if h_claim is None:
            unmeasured.append({"check": "head", "missing_input": "h_claim"})
        elif executed_head is None:
            if executed is not None:
                unmeasured.append({"check": "head", "missing_input": "executed_head"})
        elif executed_head != h_claim:
            changed = self._changed_paths(h_claim, executed_head)
            if changed is None:
                unmeasured.append({"check": "head", "missing_input": "git_diff", "head": executed_head,
                                   "h_claim": h_claim})
            elif set(changed) - PIN_ONLY_PATHS:
                differences.append({"check": "head", "observed": executed_head, "expected": h_claim,
                                    "changed_paths": sorted(set(changed) - PIN_ONLY_PATHS)[:16]})
        if isinstance(porcelain, str):
            tracked = [line for line in porcelain.splitlines() if line.strip() and not line.startswith("??")]
            if tracked:
                differences.append({"check": "tracked_edits", "observed": tracked[:16]})
        elif executed is not None:
            unmeasured.append({"check": "tracked_edits", "missing_input": "status_porcelain"})
        if differences:
            self.emit("code.executed_differs_from_sealed", level="window", collector="code_identity",
                      observed={"differences": differences[:32], "difference_count": len(differences)})
        if unmeasured:
            self.emit("code.identity_unmeasured", level="window", collector="code_identity",
                      observed={"unmeasured": unmeasured})

    def _changed_paths(self, base: str, head: str) -> list[str] | None:
        try:
            result = self.seams.runner(["git", "-C", str(self.inputs.measurement_root), "diff", "--name-only",
                                        f"{base}..{head}"], capture_output=True, text=True, check=False, timeout=60)
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        return [line for line in result.stdout.splitlines() if line.strip()]

    def model_identity(self) -> None:
        tree = read_json(self.pack_copy / "plan_tree.json")
        units = (((tree.get("arm_attachments") or {}).get("identity_pin_projection") or {}).get("identity_units") or [])
        pins_path = self.archive / "sources" / "inputs" / "identity_pins.json"
        override = read_json(pins_path) if pins_path.is_file() else None
        if isinstance(override, Mapping) and override.get("schema") == IDENTITY_PINS_SCHEMA:
            override = override.get("units")  # the sealed file the arm collector also reads
        unit_of: dict[str, str] = {}
        frozen: dict[str, Mapping[str, Any]] = {}
        for unit in units:
            unit_id = unit.get("identity_unit_id")
            for row in unit.get("config_inventory") or []:
                unit_of[str(row.get("path"))] = unit_id
            triple = unit.get("model_runtime_config") or {}
            if isinstance(override, Mapping) and isinstance(override.get(unit_id), Mapping):
                triple = override[unit_id]
            if _is_sha256(triple.get("model_artifact_sha256")):
                frozen[unit_id] = triple
        if not frozen:
            self.emit("model.identity_unpinned", level="window", collector="model_identity",
                      observed={"identity_units": [unit.get("identity_unit_id") for unit in units]})
        pack_relative = _relative_to(self.pack_copy, self.repo_root_copy) or ""
        seen: dict[str, set[tuple[str, str]]] = {}
        for member in self.roster["members"]:
            result = self.members.get(member["run_id"])
            if result is None or result.get("status") != "succeeded":
                continue
            relative = str(member.get("config_path") or "")
            if relative.startswith(pack_relative + "/"):
                relative = relative[len(pack_relative) + 1:]
            # Auxiliary members (NEG-8 corpus, references) may run another model;
            # each auxiliary input is its own consistency group.
            unit_id = unit_of.get(relative) or f"{member.get('kind')}:{member.get('stage_id')}"
            triple = result.get("identity")
            if not isinstance(triple, Mapping):
                self.emit("model.identity_underivable", level="member", run_id=member["run_id"],
                          collector="model_identity", observed={"error": "identity" in result.get("errors", {})})
                continue
            seen.setdefault(str(unit_id), set()).add((triple["model_artifact_sha256"], triple["runtime_identity_sha256"]))
            pins = frozen.get(unit_id)
            if pins is not None and (triple["model_artifact_sha256"] != pins.get("model_artifact_sha256")
                                     or triple["runtime_identity_sha256"] != pins.get("runtime_identity_sha256")):
                self.emit("model.identity_mismatch", level="member", run_id=member["run_id"],
                          collector="model_identity", observed=dict(triple),
                          expected={key: pins.get(key) for key in ("model_artifact_sha256", "runtime_identity_sha256")})
        for unit_id, identities in sorted(seen.items()):
            if len(identities) > 1:
                self.emit("model.identity_inconsistent_in_window", level="window", collector="model_identity",
                          observed={"identity_unit": unit_id, "distinct": sorted(map(list, identities))[:8]})

    # -- launch lineage (lane L3's records audit) ------------------------------
    def lineage_audit(self) -> None:
        """Each finding of ``window_lineage.audit_window_lineage`` as a flag.

        Records, never refusals (doctrine): the sealed catalog decides each
        code's effect (all ``lineage.*`` codes are DISCLOSE except
        ``lineage.plan_tree_digest_differs``, a pack-identity fact).  The
        audit reads the live roots, where the locators record their own
        paths; ``sources_unchanged`` proves they matched the archive.  A
        finding about a member's bundle is a member-level flag.

        The audit never raises for a records problem, so an exception here
        (or no bound runs root to audit) is this program failing, and the
        step is a harvest fault: recorded only as ``records.collector_failed``
        (disclosed), it would drop the plan-tree comparison, whose finding
        excludes the window, without anything excluding it.
        """
        from joulewise import window_lineage
        inputs = self.inputs
        if inputs.bound_runs_root is None:
            raise HarvestFault("bound_runs_root_unresolved")
        bundles = [Path(result["bundle_path"]) for _run_id, result in sorted(self.members.items())
                   if result.get("present")]
        findings = window_lineage.audit_window_lineage(
            claim_runs_root=inputs.claim_runs_root, bound_runs_root=inputs.bound_runs_root, bundle_paths=bundles)
        for finding in findings:
            self._lineage_flag(finding)

    def _lineage_flag(self, finding: Any) -> None:
        code = finding.get("code") if isinstance(finding, Mapping) else None
        if not isinstance(code, str) or CODE_RE.fullmatch(code) is None:
            self.emit("records.collector_failed", level="window", collector="lineage",
                      observed={"collector": "lineage", "error_type": "malformed_finding"})
            return
        scope = finding.get("scope") if isinstance(finding.get("scope"), Mapping) else {}
        bundle = scope.get("bundle_path")
        roster = {member["run_id"]: member for member in self.roster.get("members", [])}
        run_id = Path(bundle).name if isinstance(bundle, str) and bundle else None
        member = roster.get(run_id) if run_id is not None else None
        observed: dict[str, Any] = {"root_role": scope.get("root_role"),
                                    "bundle": run_id if member is None else None}
        if "observed" in finding:
            observed["observed"] = finding.get("observed")
        evidence, outside = self._archive_evidence(finding.get("evidence") or [])
        if outside:
            observed["evidence_outside_archive"] = outside[:8]
        spec = None
        if code not in CODES:  # a code L3 added since: listed with L3's own family and klass, UNCLASSIFIED
            spec = CodeSpec(finding.get("family") if finding.get("family") in FAMILIES else "RECORDS",
                            finding.get("klass") if finding.get("klass") in KLASSES else "REPRESENTATION")
        self.emit(code, level="member" if member is not None else "window",
                  run_id=run_id if member is not None else None,
                  stage_id=member.get("stage_id") if member is not None else None, collector="lineage",
                  observed=observed, expected=finding.get("expected"), evidence=evidence,
                  detail=str(finding.get("detail") or ""), spec=spec)

    def _archive_evidence(self, items: Any) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
        """Live evidence paths -> the same bytes' place in this archive, or listed as outside it."""
        evidence: list[dict[str, str]] = []
        outside: list[dict[str, Any]] = []
        sources = sorted(getattr(self, "sources", {}).items(), key=lambda item: -len(str(item[1])))
        for item in items if isinstance(items, list) else []:
            path = item.get("path") if isinstance(item, Mapping) else None
            digest = item.get("sha256") if isinstance(item, Mapping) else None
            located = None
            if isinstance(path, str) and _is_sha256(digest):
                for name, source in sources:
                    relative = _relative_to(Path(path), source)
                    if relative is not None:
                        located = f"sources/{name}" + ("" if relative == "." else f"/{relative}")
                        break
            if located is not None:
                evidence.append({"path": located, "sha256": digest})
            else:
                outside.append({"path": path if isinstance(path, str) else None,
                                "sha256": digest if _is_sha256(digest) else None})
        return evidence, outside

    # -- 5. monitor joins ------------------------------------------------------
    def monitor_joins(self) -> None:
        directory = self.inputs.monitor_dir
        thresholds = self.inputs.thresholds
        journals: dict[str, list[Reading]] = {}
        for module in MONITOR_MODULES:
            path = directory / f"{module}.jsonl"
            if not path.is_file():
                self.emit("records.monitor_journal_absent", level="window", collector="monitor",
                          observed={"module": module})
                self.hazards.setdefault(module, {})["continuous"] = {"phase": "continuous", "journal": None}
                continue
            readings, malformed = read_monitor_journal(path, module)
            journals[module] = readings
            if malformed:
                self.emit("records.monitor_line_malformed", level="window", collector="monitor",
                          observed={"module": module, "lines": malformed})
            self.hazards.setdefault(module, {})["continuous"] = {
                "phase": "continuous", "journal": {
                    "path": f"{module}.jsonl", "sha256": sha256_file(path), "readings": len(readings),
                    "failed_probes": sum(reading.status == "error" for reading in readings), "malformed": malformed}}
        roster = {member["run_id"]: member for member in self.roster["members"]}
        battery_covered: set[str] = set()
        failed: set[str] = set()  # a module whose join raised (a missing threshold): a fault, recorded once
        for run_id, spans in sorted(self.spans.items()):
            member_span, request = spans.get("member"), spans.get("request")
            kwargs = {"level": "member", "run_id": run_id, "stage_id": roster.get(run_id, {}).get("stage_id"),
                      "collector": "monitor"}
            if member_span is None:
                continue
            for module, join, span in (("battery", battery_member_flags, member_span),
                                       ("thermal", thermal_member_flags, member_span),
                                       ("contention", contention_member_flags, request or member_span),
                                       ("clock", clock_member_flags, member_span)):
                readings = journals.get(module)
                if readings is None:
                    self.emit(f"{module}.unmeasured", observed={"journal": "absent"}, **kwargs)
                    continue
                if module in failed:
                    continue
                try:
                    found = join(span, readings, thresholds)
                except Exception as exc:  # the other modules' joins still run
                    self._record_error(f"monitor.{module}", exc, 0.0, fault=True)
                    failed.add(module)
                    continue
                if module == "battery" and not any(code == "battery.unmeasured" for code, *_rest in found):
                    battery_covered.add(run_id)
                for code, observed, interval in found:
                    self.emit(code, observed=observed, interval=interval, **kwargs)
        # Plan 3.5: a missing #421 per-capture pair is only disclosed when the
        # continuous journal covers the member; otherwise battery.unmeasured
        # stands for it and the missing pair is recorded beside it.
        for run_id, status in sorted(self.pair_missing.items()):
            code = "battery.capture_pair_missing_covered" if run_id in battery_covered else "battery.capture_pair_missing"
            self.emit(code, level="member", run_id=run_id, stage_id=roster.get(run_id, {}).get("stage_id"),
                      collector="battery_pair", observed={"status": status})
        self._capture_battery_joins(journals.get("battery"), thresholds)
        steps, changes = clock_steps(journals.get("clock", []), thresholds)
        if changes:
            self.emit("clock.frequency_changed", level="window", collector="monitor",
                      observed={"changes": changes[:16], "count": len(changes)},
                      interval={"monotonic_ns": [changes[0]["monotonic_ns"], changes[-1]["monotonic_ns"]]})
        capture_spans = {attempt: capture.get("span") for attempt, capture in self.capture_assessments.items()}
        for step in steps:
            hit = False
            for run_id, spans in self.spans.items():
                if spans.get("member") and _overlaps(step["interval_monotonic_ns"], spans["member"]):
                    hit = True
                    self.emit("clock.step_overlap", level="member", run_id=run_id, collector="monitor",
                              observed=step, interval={"monotonic_ns": step["interval_monotonic_ns"]})
            for attempt, span in capture_spans.items():
                if span and _overlaps(step["interval_monotonic_ns"], span):
                    hit = True
                    self.emit("clock.step_overlap_calibration", level="window", collector="monitor",
                              observed={**step, "capture": attempt},
                              interval={"monotonic_ns": step["interval_monotonic_ns"]})
            if not hit:
                self.emit("clock.step", level="window", collector="monitor", observed=step,
                          interval={"monotonic_ns": step["interval_monotonic_ns"]})
        low, paths = disk_low(journals.get("disk", []), thresholds)
        if low:
            self.emit("disk.low", level="window", collector="monitor",
                      observed={"readings_below": len(low), "paths": paths[:8]},
                      interval={"monotonic_ns": [low[0].monotonic_ns, low[-1].monotonic_ns]})
        self._kernel_task_share(journals.get("contention", []))

    def _capture_battery_joins(self, readings: Sequence[Reading] | None, thresholds: Mapping[str, Any]) -> None:
        """Each calibration capture's battery physics from the continuous journal (core-prune N7.2).

        The controller no longer refuses a window whose pre-slot battery pair
        did not pass (core-prune A1), so the capture's battery is measured here
        as members have it: the member join over the capture's span.  An
        on-battery or accumulator excursion in the span removes the window;
        a pair that did not pass with no journal coverage (no span, no
        journal, a hole, or a join that could not run) removes it too.
        """
        for attempt, capture in sorted(self.capture_assessments.items()):
            span, pair = capture.get("span"), capture.get("battery_pair")
            codes: list[str] = []
            reason = None
            if not span:
                reason = "capture_span_unknown"
            elif readings is None:
                reason = "battery_journal_absent"
            else:
                try:
                    codes = sorted({code for code, *_rest in battery_member_flags(span, readings, thresholds)})
                except Exception as exc:  # a missing threshold: also a recorded fault
                    self._record_error("monitor.capture_battery", exc, 0.0, fault=True)
                    reason = "join_failed"
                if "battery.unmeasured" in codes:
                    reason = "journal_gap"
            observed = {"capture": attempt, "slot": capture.get("slot"), "pair": pair, "codes": codes}
            interval = {"monotonic_ns": list(span)} if span else None
            if {"battery.member_span", "battery.accumulator_excursion"} & set(codes):
                self.emit("calibration.capture_battery_span", level="window", collector="monitor",
                          observed=observed, interval=interval)
            if pair != "pass" and reason is not None:
                self.emit("calibration.capture_battery_unmeasured", level="window", collector="monitor",
                          observed={**observed, "reason": reason}, interval=interval)

    def _kernel_task_share(self, readings: Sequence[Reading]) -> None:
        """kernel_task's CPU-seconds during requests (excluded in window, disclosed)."""
        total = 0.0
        for reading in readings:
            rate = _num(reading.values.get("kernel_task_cpu_s_per_s"))
            if reading.status != "ok" or not reading.interval or rate is None:
                continue
            for spans in self.spans.values():
                request = spans.get("request")
                if request and _overlaps(reading.interval, request):
                    overlap = min(reading.interval[1], request[1]) - max(reading.interval[0], request[0])
                    total += max(0, overlap) / 1e9 * rate
        if total:
            self.emit("contention.kernel_task_share", level="window", collector="monitor",
                      observed={"kernel_task_cpu_s_in_requests": round(total, 6)})

    # -- arm record and earlier flag files -------------------------------------
    def arm_and_desk_records(self) -> None:
        path = self.inputs.arm_record_path
        arm_value: Any = None
        if path.is_file():
            arm_value = read_json(path)
            for module, phases in _arm_modules(arm_value).items():
                self.hazards.setdefault(module, {})["arm"] = phases
        elif (self.inputs.night_dir / "chain.started").is_file():
            self.emit("records.arm_record_absent", level="window", collector="arm", observed={"arm_record": None})
        # Every flag file written before harvest: L4's desk and arm collectors,
        # L2's driver.jsonl.  A line that is not a valid flag may have been an
        # exclusion, so it becomes records.malformed_flag, never classified.
        # The collectors' run log (collector_runs.jsonl, written beside the
        # flag files by scripts/collect_window_flags.py) holds run records, not
        # flags: it is read by _collector_run_records, and so is a run record
        # found in any other file of the directory.
        directory = self.inputs.flags_dir
        for flag_file in sorted(directory.glob("*.jsonl")) if directory.is_dir() else []:
            if flag_file.name == COLLECTOR_RUNS_NAME:
                self._collector_run_records(flag_file)
                continue
            for number, line in enumerate(flag_file.read_bytes().split(b"\n"), start=1):
                if not line.strip():
                    continue
                value: Any = None
                try:
                    value = json.loads(line)
                except ValueError as exc:
                    problems = [f"not JSON: {type(exc).__name__}"]
                else:
                    if isinstance(value, Mapping) and value.get("schema_version") == COLLECTOR_RUN_SCHEMA:
                        self._fold_collector_run(value, source=f"flags/{flag_file.name}:{number}")
                        continue
                    problems = self.flags.absorb(value)
                if problems:
                    self._malformed_flag_line(flag_file.name, number, line, value, problems)
        self._unwritten_core_flags()
        self._arm_collector_records(arm_value)

    def _malformed_flag_line(self, file: str, number: int | None, line: bytes, value: Any,
                             problems: Sequence[str]) -> None:
        salvaged = value.get("code") if isinstance(value, Mapping) else None
        self.emit("records.malformed_flag", level="window", collector="flags",
                  observed={"file": file, "line": number, "line_sha256": sha256_bytes(line),
                            "salvaged_code": salvaged if isinstance(salvaged, str) else None,
                            "problems": list(problems)[:5]})

    def _unwritten_core_flags(self) -> None:
        """Core flags whose flag-file write failed, recovered from stderr (core-prune N8).

        ``joulewise.flags.core.emit`` prints such a flag whole, behind
        ``UNWRITTEN_MARKER``, to its process's stderr.  The chain sends stage
        stderr to ``<custody>/operator-logs/*.log``; the desk verdict's stderr
        is this harvest's desk transcript.  Each marked line goes through the
        flag-file path: a valid flag is absorbed (it is the flag, nothing more
        is emitted), anything else is ``records.malformed_flag``, which is never
        classified and so blocks release.  A log that cannot be read may hold
        such a line, so it is recorded the same way.
        """
        marker = UNWRITTEN_MARKER.encode("utf-8")
        directories = [self.inputs.custody_root / "operator-logs"]
        planned = _plan_value(self.inputs.plan, "operator_log_root")
        if isinstance(planned, str) and os.path.isabs(planned) \
                and all(not _same_path(Path(planned), known) for known in directories):
            directories.append(Path(planned))
        sources: list[tuple[str, bytes | None]] = []
        for directory in directories:
            label = "operator-logs" if directory == directories[0] else str(directory)
            for path in sorted(directory.glob("*.log")) if directory.is_dir() else []:
                try:
                    sources.append((f"{label}/{path.name}", path.read_bytes()))
                except OSError:
                    sources.append((f"{label}/{path.name}", None))
        transcript = getattr(self, "_desk_transcript", None)
        if isinstance(transcript, str):
            sources.append(("desk-transcript", transcript.encode("utf-8", "replace")))
        for source, raw in sources:
            if raw is None:
                self._malformed_flag_line(source, None, b"", None, ["operator log unreadable"])
                continue
            if marker not in raw:
                continue
            for number, line in enumerate(raw.split(b"\n"), start=1):
                if not line.startswith(marker):
                    continue
                remainder = line[len(marker):].rstrip(b"\r")
                value: Any = None
                try:
                    value = json.loads(remainder)
                except ValueError as exc:
                    problems = [f"not JSON: {type(exc).__name__}"]
                else:
                    problems = self.flags.absorb(value)
                if problems:
                    self._malformed_flag_line(source, number, remainder, value, problems)

    def _prior_collector_error(self, *, stage: str, collector: str, status: str, error: Any, elapsed_s: Any,
                               source: str) -> None:
        """One desk/arm collector that did not finish: a window_flags collector_errors entry and a flag.

        Never a harvest fault: these collectors are records.  A collector that
        did not finish has also left its own ``*_unmeasured`` flag where its
        writer could write one (``joulewise.flags.collect.run_collectors``).
        """
        text = " ".join(str(error if error is not None else status).split())
        entry = {"collector": f"{stage}.{collector}", "error": text[:200],
                 "elapsed_s": elapsed_s if _is_number(elapsed_s) else None,
                 "stage": stage, "status": status, "source": source}
        key = (entry["collector"], entry["status"], entry["error"], source)
        if key in self._prior_error_keys:
            return
        self._prior_error_keys.add(key)
        self.prior_collector_errors.append(entry)
        self.error_details.append({**entry, "detail": text[:2000]})
        self.emit("records.collector_failed", level="window", collector="flags",
                  observed={"collector": collector, "stage": stage, "status": status, "source": source})

    def _fold_collector_run(self, record: Mapping[str, Any], *, source: str) -> None:
        """A ``joulewise.flag_collector_run.v1`` record: every collector whose status is not ``ok``."""
        stage = record.get("stage") if isinstance(record.get("stage"), str) else "unknown"
        rows = record.get("collectors") if isinstance(record.get("collectors"), list) else []
        listed = record.get("collector_errors") if isinstance(record.get("collector_errors"), list) else []
        failed = [row for row in rows if isinstance(row, Mapping) and row.get("status") != "ok"]
        named = {row.get("collector") for row in failed}
        failed += [{"collector": row.get("collector"), "status": "error", "error": row.get("error"),
                    "elapsed_s": row.get("elapsed_s")}
                   for row in listed if isinstance(row, Mapping) and row.get("collector") not in named]
        for row in failed:
            self._prior_collector_error(stage=stage, collector=str(row.get("collector") or "unknown"),
                                        status=str(row.get("status") or "error"), error=row.get("error"),
                                        elapsed_s=row.get("elapsed_s"), source=source)

    def _collector_run_records(self, path: Path) -> None:
        for number, line in enumerate(path.read_bytes().split(b"\n"), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except ValueError:
                value = None
            source = f"flags/{path.name}:{number}"
            if isinstance(value, Mapping) and value.get("schema_version") == COLLECTOR_RUN_SCHEMA:
                self._fold_collector_run(value, source=source)
            else:
                self._prior_collector_error(stage="unknown", collector="collector_runs", status="malformed",
                                            error="not a joulewise.flag_collector_run.v1 record",
                                            elapsed_s=None, source=source)

    def _arm_collector_records(self, arm_value: Any) -> None:
        """The arm-time collector subprocess as a whole: the driver's records, else L1's arm record.

        ``night/arm_collectors*.json`` (``joulewise.b5.driver``) record the
        call of ``scripts/collect_window_flags.py --stage arm``; a call that
        timed out, failed to spawn or exited nonzero wrote no run record of its
        own, so it is folded here.  Without a driver record, the arm record's
        ``record_only`` entries are read the same way.
        """
        night = self.inputs.night_dir
        records = []
        for path in sorted(night.glob("arm_collectors*.json")) if night.is_dir() else []:
            try:
                records.append((path, read_json(path)))
            except (OSError, ValueError):
                self._prior_collector_error(stage="arm", collector=path.name, status="malformed",
                                            error="unreadable driver collector record", elapsed_s=None,
                                            source=f"night/{path.name}")
        results: list[tuple[str, Mapping[str, Any]]] = []
        for path, record in records:
            if not isinstance(record, Mapping):
                continue
            source = f"night/{path.name}"
            items = [item for item in record.get("results") or [] if isinstance(item, Mapping)] \
                if isinstance(record.get("results"), list) else []
            if items:  # the arm ran them; its collector_error only joins these results' errors
                results += [(source, item) for item in items]
            elif record.get("collector_error"):  # the driver ran the subprocess itself
                self._prior_collector_error(stage="arm", collector="flags.arm", status="error",
                                            error=record.get("collector_error"), elapsed_s=record.get("elapsed_s"),
                                            source=source)
        if not records and isinstance(arm_value, Mapping):
            results = [("hazards/arm.json", item) for item in arm_value.get("record_only") or []
                       if isinstance(item, Mapping)]
        for source, item in results:
            failed = item.get("error") or item.get("timed_out") or (
                _is_int(item.get("returncode")) and item.get("returncode") != 0)
            if failed:
                status = "timeout" if item.get("timed_out") else "error"
                error = item.get("error") or ("timed out" if item.get("timed_out")
                                              else f"exit {item.get('returncode')}")
                self._prior_collector_error(stage="arm", collector=str(item.get("name") or "collector"),
                                            status=status, error=error, elapsed_s=item.get("elapsed_s"),
                                            source=source)

    # -- G3 provenance checker -------------------------------------------------
    def g3(self, *, skipped: bool = False) -> None:
        """Run the G3 checker on a pack it applies to (one with an analysis manifest).

        G3's F5-2 is the one independent recompute of the whole-window verdict
        (``whole_window()`` itself trusts the row's stored status), so its
        absence is never silent: unless the report exists and holds an F5-2
        row with status PASS, ``g3.recompute_failed`` is emitted, whether the
        checker was skipped, could not run, crashed, timed out, exited outside
        {0, 1}, or reported F5-2 as FAIL or SKIP.  Other FAIL rows are
        ``g3.assertion_failed``.
        """
        inputs = self.inputs
        pack = inputs.pack_root
        runs = inputs.claim_runs_root
        if not (pack / "analysis_manifest_v3.json").is_file():
            self.emit("g3.not_applicable", level="window", collector="g3",
                      observed={"reason": "pack_has_no_analysis_manifest"})
            return

        def recompute_failed(**observed: Any) -> None:
            self.emit("g3.recompute_failed", level="window", collector="g3", observed=observed)

        if skipped:
            recompute_failed(reason="g3_skipped")
            return
        needed = [runs / "bracket-binding.json", runs / "whole-window-verdict.json",
                  self.derived / "terminal-pin.json", self.derived / "terminal-boundary.json"]
        missing = [path.name for path in needed if not path.is_file()]
        if missing:
            recompute_failed(reason="desk_outputs_absent", missing=missing)
            return
        report = self.withheld / "g3-report.json"
        common = _common_root([runs, inputs.ledger_path.parent, self.derived])
        argv = [self.seams.python, "-B", str(Path(__file__).resolve().parents[2] / "scripts" / "check_window_provenance.py"),
                "--runs-root", str(runs), "--pack-root", str(pack), "--custody-root", str(common),
                "--bracket-binding", str(runs / "bracket-binding.json"),
                "--whole-window-verdict", str(runs / "whole-window-verdict.json"),
                "--calibration-ledger", str(inputs.ledger_path), "--head-pin", str(self.derived / "terminal-pin.json"),
                "--terminal-boundary-record", str(self.derived / "terminal-boundary.json"),
                "--acceptance", str(self._acceptance_path()), "--report-json", str(report)]
        if self.inputs.plan.get("receipt_class") == HAZARD_PACK_CLASS:
            # A claim window holds every member of the pack, not one block:
            # G3's full-window roster (root order plus the claim-root references).
            argv += ["--full-window", "--plan-tree", str(pack / "plan_tree.json"),
                     "--repo-root", str(inputs.measurement_root)]
        started = time.monotonic()
        try:
            result = self.seams.runner(argv, capture_output=True, text=True, check=False, timeout=3600)
        except Exception as exc:  # timeout or spawn failure: recorded, never a fault
            self._record_error("g3", exc, round(time.monotonic() - started, 3), fault=False)
            recompute_failed(reason="runner_error", error_type=type(exc).__name__)
            return
        write_once(self.withheld / "transcripts" / "g3.txt",
                   ((getattr(result, "stdout", "") or "") + (getattr(result, "stderr", "") or "")).encode())
        returncode = getattr(result, "returncode", None)
        rows: Any = None
        if report.is_file():
            try:
                rows = read_json(report).get("assertions")
            except (OSError, ValueError, AttributeError):
                rows = None
        rows = [row for row in rows if isinstance(row, Mapping)] if isinstance(rows, list) else None
        for row in rows if rows is not None else _g3_lines(getattr(result, "stdout", "")):
            if row.get("status") == "FAIL" and row.get("id") != "F5-2":
                self.emit("g3.assertion_failed", level="window", collector="g3", observed={"assertion": row.get("id")})
        f52 = sorted({str(row.get("status")) for row in rows or [] if row.get("id") == "F5-2"})
        if rows is None or returncode not in (0, 1) or f52 != ["PASS"]:
            recompute_failed(reason="report_absent" if rows is None else "f5_2_not_passed",
                             returncode=returncode if _is_int(returncode) else None, f5_2=f52)

    # -- diagnostics -----------------------------------------------------------
    def diagnostics(self) -> None:
        sizes = sorted((result["stream_bytes"], run_id) for run_id, result in self.members.items()
                       if isinstance(result.get("stream_bytes"), int))
        if sizes:
            self.emit("diagnostic.s1_structural", level="window", collector="diagnostics",
                      observed={"check": "stream_sizes",
                                "shortest": {"run_id": sizes[0][1], "bytes": sizes[0][0]},
                                "longest": {"run_id": sizes[-1][1], "bytes": sizes[-1][0]}, "streams": len(sizes)})
        spans = sorted(span["member"] for span in self.spans.values() if span.get("member"))
        if len(spans) > 1:
            gaps = [max(0, right[0] - left[1]) for left, right in zip(spans, spans[1:])]
            self.emit("diagnostic.s1_structural", level="window", collector="diagnostics",
                      observed={"check": "time_outside_members", "gaps": len(gaps), "total_s": round(sum(gaps) / 1e9, 3),
                                "max_s": round(max(gaps) / 1e9, 3)})
        counts = Counter()
        for member in self.roster["members"]:
            result = self.members.get(member["run_id"])
            if result is None:
                continue
            for cell in member.get("cells", []):
                path = cell.get("target_precheck_path")
                if not isinstance(path, list) or not path:
                    continue
                node: Any = (result.get("precheck") or {}).get(path[0])
                if len(path) > 1 and isinstance(node, Mapping):
                    node = node.get(path[1])
                ok = isinstance(node, Mapping) and node.get("eligible") is True and not node.get("reasons")
                counts[(cell["cell_id"], "eligible" if ok else "ineligible")] += 1
        if counts:
            # Eligibility can turn on an energy envelope, so the counts are RESTRICTED.
            self.emit("diagnostic.s1_structural", level="window", collector="diagnostics", blinding=RESTRICTED,
                      observed={"check": "precheck_counts",
                                **{f"{cell}:{state}": count for (cell, state), count in sorted(counts.items())}})
        strict_valid = sum(bool(result.get("strict_valid")) for result in self.members.values())
        identical = sum(bool((result.get("rereduced") or {}).get("identical_to_stored")) for result in self.members.values())
        self.emit("diagnostic.s1_structural", level="window", collector="diagnostics",
                  observed={"check": "l10a_prefix", "bundles": len(self.members), "strict_valid": strict_valid,
                            "rereduced_identical": identical})

    # -- exclusion-function inputs (L4 seam) ------------------------------------
    def exclusion_inputs(self) -> None:
        chain_started = None
        try:
            value = read_json(self.inputs.night_dir / "chain.started").get("monotonic_ns")
            chain_started = value if _is_int(value) else None
        except (OSError, ValueError, AttributeError):
            pass
        self.exclusion_roster, self.exclusion_spans = l4_exclusion_inputs(
            self.roster, self.spans, plan_id=self.inputs.plan_id, attempt=self.inputs.attempt,
            chain_started_monotonic_ns=chain_started, bundles=self.bundle_records())

    def bundle_records(self) -> list[dict[str, Any]]:
        """Every bundle directory in the runs roots, for L4's roster rule.

        ``created_monotonic_ns`` places the bundle against ``chain.started``
        (:func:`bundle_creation_ns`): the earliest stamp of its own stream,
        else any controller monotonic stamp it recorded, else its
        ``run_started`` wall time mapped through ``chain.started``'s paired
        (wall, monotonic) stamps.  A member that never reached the sampler
        (aborted at idle admission) is placed by the last two.  With no stamp
        at all it stays ``None``, which L4 records as
        ``roster.creation_unplaced``; ``created_source`` says which was used.

        ``attempt``: the plan writer creates the claim and bound runs roots
        with an exclusive mkdir for one attempt (``hazard_window.runs_roots``),
        so a bundle in those roots is bound to the plan's attempt.  A root the
        plan does not name as its own (an override) gives ``None``.
        """
        calibration = {name for name in (self.inputs.pre_attempt_id, self.inputs.post_attempt_id) if name}
        assessed = {result["bundle_path"]: result for result in self.members.values()}
        chain = None
        try:
            chain = read_json(self.inputs.night_dir / "chain.started")
        except (OSError, ValueError):
            chain = None
        fresh = self._fresh_runs_roots()
        rows = []
        for label, root in (("claim", self.inputs.claim_runs_root), ("bound", self.inputs.bound_runs_root)):
            if root is None or not root.is_dir():
                continue
            attempt = self.inputs.attempt if label in fresh and _same_path(root, fresh[label]) else None
            for path in sorted(root.iterdir()):
                if not path.is_dir() or path.name in {"campaign_manifests", "instrument_validation"} | calibration \
                        or not (path / "metadata.json").is_file():
                    continue
                result = assessed.get(str(path))
                try:
                    metadata = read_json(path / "metadata.json")
                except (OSError, ValueError):
                    metadata = None
                try:
                    events = _events(path)
                except (OSError, ValueError):
                    events = []
                spans = result.get("spans") if isinstance(result, Mapping) else None
                created, source = bundle_creation_ns(metadata if isinstance(metadata, Mapping) else {}, events,
                                                     spans=spans, chain_started=chain)
                rows.append({"bundle_id": f"{label}/{path.name}", "run_id": path.name, "attempt": attempt,
                             "created_monotonic_ns": created, "created_source": source})
        return rows

    def _fresh_runs_roots(self) -> dict[str, Path]:
        """The runs roots the plan writer created for this plan's attempt (``hazard_window.runs_roots``)."""
        hazard = self.inputs.plan.get("hazard_window") if isinstance(self.inputs.plan, Mapping) else None
        roots = hazard.get("runs_roots") if isinstance(hazard, Mapping) else None
        if not isinstance(roots, Mapping):
            return {}
        return {label: Path(value) for label, value in roots.items()
                if label in ("claim", "bound") and isinstance(value, str) and os.path.isabs(value)}

    # -- outputs ---------------------------------------------------------------
    def sources_unchanged(self) -> None:
        changed = [name for name, path in self.sources.items() if tree_inventory(path) != self.original.get(name)]
        if changed:
            self.emit("records.source_changed_during_harvest", level="window", collector="archive",
                      observed={"sources": sorted(changed)})

    def finish(self, verdict: str) -> dict[str, Any]:
        if self.exclusion_roster is not None:
            # Structure only: the bundle creation stamps and the chain start
            # are stream timing and stay in withheld/ with the spans.
            self.outputs["derived/roster.json"] = write_json_once(self.derived / "roster.json", {
                key: value for key, value in self.exclusion_roster.items()
                if key not in ("bundles", "chain_started_monotonic_ns")})
            write_json_once(self.withheld / "exclusion-inputs.json",
                            {"schema": "joulewise.b5_exclusion_inputs.v1", "roster": self.exclusion_roster,
                             "spans": self.exclusion_spans})

        def ordered() -> list[dict[str, Any]]:
            return sorted(self.flags.records, key=lambda row: (row["scope"]["level"], row["scope"].get("run_id") or "",
                                                               row["code"], row["flag_id"]))

        flags = ordered()
        exclusions: Any
        if verdict == NULL:
            exclusions = {"status": "NULL", "members_excluded": [], "cells": [], "claim_usable": False,
                          "reasons": ["window.null"]}
        else:
            try:
                if self.exclusion_roster is None:
                    raise HarvestFault("exclusion_inputs_unavailable")
                exclusions = self.seams.exclusions_compute(flags, self.exclusion_roster, self.exclusion_spans,
                                                           self.catalog)
            except Exception as exc:
                # Absent or failing L4 function: numbers and flags still stand;
                # the window is simply not claim-usable until it is computed.
                self._record_error("exclusions", exc, 0.0, fault=False)
                exclusions = {"status": "UNAVAILABLE", "members_excluded": [], "cells": [], "claim_usable": False,
                              "reasons": ["exclusions.function_unavailable"]}
                flags = ordered()
        self.outputs["derived/flags.jsonl"] = write_jsonl_once(self.derived / "flags.jsonl", flags)
        exclusions = dict(exclusions) if isinstance(exclusions, Mapping) else {"value": exclusions}
        self.outputs["derived/exclusions.json"] = write_json_once(self.derived / "exclusions.json", exclusions)
        write_json_once(self.withheld / "collector-errors.json",
                        {"schema": "joulewise.b5_collector_errors.v1", "errors": self.error_details})
        if self.faults:
            verdict = HARVEST_FAULT
        claim_usable = bool(exclusions.get("claim_usable")) and verdict == COLLECTED
        effects = Counter(self.catalog.effect(row["code"]) for row in flags)
        summary = {
            "schema": WINDOW_FLAGS_SCHEMA,
            "window": {"plan_id": self.inputs.plan_id, "pack_id": self.inputs.pack_id, "attempt": self.inputs.attempt,
                       "t0_epoch_s": self.inputs.plan.get("t0_epoch_s"),
                       "boot_session_uuid": self.flags._boot, "head": self.h_claim,
                       "custody_root": str(self.inputs.custody_root)},
            "catalog": {"path": self.catalog.path, "sha256": self.catalog.sha256},
            "hazards": self.hazards,
            "flags": {"total": len(flags), "by_code": dict(sorted(Counter(row["code"] for row in flags).items())),
                      "by_family": dict(sorted(Counter(row["family"] for row in flags).items())),
                      "by_effect": dict(sorted(effects.items())),
                      "unclassified": sorted({row["code"] for row in flags
                                              if self.catalog.effect(row["code"]) == UNCLASSIFIED})},
            "collector_errors": self.collector_errors + self.prior_collector_errors,
            "exclusions": {"members_excluded": exclusions.get("members_excluded", []),
                           "cells": exclusions.get("cells", []),
                           "claim_usable": claim_usable,
                           "release_blocked": exclusions.get("release_blocked", True),
                           "unclassified": exclusions.get("unclassified", []),
                           "reasons": list(exclusions.get("reasons", []))
                           + (["harvest.fault"] if verdict == HARVEST_FAULT else [])},
        }
        self.outputs["derived/window_flags.json"] = write_json_once(self.derived / "window_flags.json", summary)
        record = {"schema": SCHEMA, "verdict": verdict, "plan_id": self.inputs.plan_id,
                  "pack_id": self.inputs.pack_id, "attempt": self.inputs.attempt,
                  "archive_root": str(self.archive), "claim_usable": claim_usable,
                  "flags": len(flags), "members_assessed": len(self.members),
                  "faults": [{"collector": item["collector"]} for item in self.faults],
                  "outputs": dict(sorted(self.outputs.items()))}
        write_json_once(self.archive / "harvest.json", record)
        return record


def acceptance_pin(policy: Any) -> tuple[str | None, str | None]:
    """The plan tree's digest of the issued calibration acceptance, and the key it came from."""
    if not isinstance(policy, Mapping):
        return None, None
    issued = policy.get("issued_acceptance")
    if isinstance(issued, Mapping) and _is_sha256(issued.get("artifact_sha256")):
        return issued["artifact_sha256"], "acceptance_policy.issued_acceptance.artifact_sha256"
    if _is_sha256(policy.get("issued_artifact_sha256")):
        return policy["issued_artifact_sha256"], "acceptance_policy.issued_artifact_sha256"
    return None, None


def _arm_modules(value: Any) -> dict[str, list[dict[str, Any]]]:
    """L1's arm record (``joulewise.hazard_arm.v1``) -> {module: [phase entries]}.

    L1 writes ``hazards: {module: [{phase, verdict, measurement}, ...]}``, one
    entry per phase (instant, probe, dwell, final, dwell_and_go).
    """
    hazards = value.get("hazards") if isinstance(value, Mapping) else None
    out: dict[str, list[dict[str, Any]]] = {}
    for module, entries in (hazards.items() if isinstance(hazards, Mapping) else ()):
        rows = entries if isinstance(entries, list) else [entries]
        phases = []
        for entry in rows:
            if not isinstance(entry, Mapping):
                continue
            verdict = entry.get("verdict") if isinstance(entry.get("verdict"), Mapping) else {}
            phases.append({"phase": entry.get("phase"), "verdict": verdict.get("status"),
                           "reasons": verdict.get("reasons"), "thresholds": verdict.get("thresholds"),
                           "measurement": entry.get("measurement")})
        out[str(module)] = phases
    return out


def _inventory_checkout(value: Any) -> Mapping[str, Any]:
    """L2's executed inventory nests the checkout under ``measurement_checkout``."""
    if isinstance(value, Mapping) and isinstance(value.get("measurement_checkout"), Mapping):
        return value["measurement_checkout"]
    return value if isinstance(value, Mapping) else {}


def _inventory_map(value: Any) -> tuple[dict[str, str] | None, str | None]:
    """Sealed (L6) or executed (L2) inventory -> ({relative path: sha256}, head).

    Shapes read: ``{files: {path: sha256} | [{path, sha256}], head?}`` (L4's
    sealed-inventory reader accepts the same), L2's
    ``{measurement_checkout: {head, status_porcelain, files}, chain, ...}``,
    and a bare ``{path: sha256}`` map.
    """
    if not isinstance(value, Mapping):
        return None, None
    checkout = _inventory_checkout(value)
    head = checkout.get("head") or checkout.get("h_claim") or checkout.get("git_head")
    files = checkout.get("files", checkout.get("inventory"))
    result: dict[str, str] = {}
    if isinstance(files, Mapping):
        result = {str(key): item for key, item in files.items() if _is_sha256(item)}
    elif isinstance(files, list):
        result = {str(row["path"]): row["sha256"] for row in files
                  if isinstance(row, Mapping) and isinstance(row.get("path"), str) and _is_sha256(row.get("sha256"))}
    elif files is None:
        result = {str(key): item for key, item in checkout.items() if _is_sha256(item)}
    return result, head if isinstance(head, str) else None


def _g3_lines(stdout: str) -> list[dict[str, str]]:
    rows = []
    for line in (stdout or "").splitlines():
        match = re.match(r"(PASS|FAIL|SKIP) (\S+)", line)
        if match and match.group(2) != "CLI":
            rows.append({"status": match.group(1), "id": match.group(2)})
    return rows


def _under(path: Path, root: Path) -> bool:
    try:
        Path(os.path.abspath(path)).relative_to(os.path.abspath(root))
    except ValueError:
        return False
    return True


def _relative_to(path: Path, root: Path) -> str | None:
    try:
        return Path(os.path.abspath(path)).relative_to(os.path.abspath(root)).as_posix()
    except ValueError:
        return None


def _common_root(paths: Sequence[Path]) -> Path:
    return Path(os.path.commonpath([os.path.abspath(path) for path in paths]))


def harvest(inputs: WindowInputs, archive_root: Path | str, *, seams: Seams | None = None,
            prepare_desk: bool = False, run_g3: bool = True, allow_missing_terminal: bool = False) -> dict[str, Any]:
    """Harvest one window.  Raises NotReady before the chain group is gone."""
    seams = seams or Seams()
    archive = Path(archive_root).absolute()
    state = readiness(inputs, seams, allow_missing_terminal=allow_missing_terminal)
    if archive.exists():
        raise HarvestFault("archive_root_exists")
    for source in (inputs.custody_root, inputs.claim_runs_root, inputs.bound_runs_root):
        if source is not None and (_under(archive, source) or _under(source, archive)):
            raise HarvestFault("archive_overlaps_source")
    archive.mkdir(parents=True)
    run = _Harvest(inputs, archive, seams, prepare_desk=prepare_desk, run_g3=run_g3)
    if not state["terminal_record"]:
        run.emit("records.terminal_record_absent", level="window", collector="readiness", observed={"result_json": None})
    if not state["chain_started"]:
        run.step("archive", run.archive_inputs)
        run.step("arm_records", run.arm_and_desk_records)
        return run.finish(NULL)
    run.step("thresholds", run.record_thresholds)
    if prepare_desk:
        run.step("desk", run.prepare_desk_verdict, fault=False)
    run.step("archive", run.archive_inputs)
    run.step("arm_records", run.arm_and_desk_records)
    if run.step("roster", run.build_roster) is None and not run.roster:
        return run.finish(HARVEST_FAULT)
    run.step("roster_dispatch", run.roster_dispatch)
    run.step("members", run.assess)
    run.step("member_flags", run.member_flags)
    run.step("roster_checks", run.roster_checks)
    run.step("cooldown", run.cooldown)
    run.step("calibration", run.calibration)
    run.step("neg8_bound", run.neg8_bound)
    run.step("whole_window", run.whole_window)
    run.step("clock_systematic", run.clock_systematic)
    run.step("pack_identity", run.pack_identity)
    run.step("code_identity", run.code_identity)
    run.step("model_identity", run.model_identity)
    run.step("lineage", run.lineage_audit)
    run.step("monitor", run.monitor_joins)
    run.step("exclusion_inputs", run.exclusion_inputs)
    run.step("g3", lambda: run.g3(skipped=not run_g3), fault=False)
    run.step("diagnostics", run.diagnostics, fault=False)
    run.step("sources_unchanged", run.sources_unchanged)
    return run.finish(COLLECTED)
