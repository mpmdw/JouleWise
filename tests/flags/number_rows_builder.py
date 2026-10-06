#!/usr/bin/env python3
"""Build ``configs/flags/number_rows.json``: where each NUMBER row is evaluated now.

Input: the gate-prune refusal inventory (``inventory.json``, 1,674 rows of class
NUMBER, taken at ``a0a4f5a7``). Output: one entry per row, keyed by
``(file, function, code, ordinal)`` -- the enclosing function is resolved from
the source at the base commit, so the key survives line shifts.

Every row gets exactly one disposition (plan section 2.4):

``evaluated``
    The check still runs on the block-5 path. ``stage`` says where:
    ``window`` (chain-stage core code, unchanged), ``harvest`` (core code the
    harvest runs on preserved bytes), ``desk_arm`` (an L4 collector, replayed
    at harvest) or ``analysis`` (post-release analysis code, unchanged; a
    refusal there stops a number being issued, never collection, so
    ``flag_code`` is null). ``evaluation_site`` is ``file:function``.
``retired_path``
    The row sits on a path block 5 never runs (``TRANSACTION_PACK`` arm/launch,
    block-4 machinery, the runbook chain). It protects nothing block 5 runs;
    ``equivalent`` names the flag code and the hazard-path site that now
    carries the same concern, and its test.

``test_id`` names a test that exercises the evaluation site: for core code,
the first test (by file, then line) whose body names the function and whose
file names the module; for the hazard path, this lane's tests or, for another
lane's module, that lane's test file (``pending_lane_tests``).

Usage::

    python tests/flags/number_rows_builder.py --inventory <inventory.json> [--check]
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "configs" / "flags" / "number_rows.json"
DEFAULT_INVENTORY = Path("/Users/edr/night-archive/gate-prune/inventory.json")
SCHEMA = "joulewise.number_rows.v1"
BASE = "a0a4f5a7"
EXPECTED_ROWS = 1674

T_COLLECT = "tests/flags/test_flags_collect.py"
T_EXCL = "tests/flags/test_flags_exclusions.py"

# Test files owned by other lanes that do not exist in this lane's tree.
PENDING_LANE_TESTS = {
    "tests/hazards": "L1",
    "tests/test_b5_chain.py": "L2",
    "tests/test_window_lineage.py": "L3",
    "tests/test_harvest_b5_window.py": "L5",
    "tests/test_g10_clock_step_control.py": "L8",
}

# Where a file's checks run on the block-5 path.
RETIRED_FILES = {
    "joulewise/arm_readiness.py", "joulewise/arm_readiness_evidence.py",
    "joulewise/arm_readiness_evidence_t0.py", "scripts/capture_t0_step.py",
    "scripts/author_arm_evidence_t0.py", "scripts/author_arm_readiness_evidence.py",
    "scripts/generate_arm_readiness.py", "scripts/launch_window.py",
    "joulewise/network_time_off.py", "joulewise/dwell.py",
    "scripts/write_v5_qualification_plan.py", "scripts/harvest_v5_qualification.py",
    "scripts/harvest_v5_g2b_window.py", "scripts/v5_s1_desk_closeout.py",
    "scripts/check_v5_arm_abort.py", "scripts/produce_t0_rehearsal_bundle.py",
    "scripts/rehearse_t0_unattended.py", "scripts/restore_v5_null_reservation.py",
    "scripts/assemble_v5_battery_boundaries.py", "joulewise/t0_rehearsal.py",
    "joulewise/v5_qualification.py", "scripts/ed_session/capture_t0_anchor_positive_control.py",
    "joulewise/night_gate.py", "joulewise/arm_retry.py", "joulewise/night_agent_install.py",
    "scripts/gen_g2_phase_d.py", "docs/phase_2/window_runbook.md", "scripts/quiet_mac_prep.sh",
}
WINDOW_FILES = {
    "scripts/run_campaign.py", "joulewise/controller.py", "joulewise/bundle.py",
    "joulewise/reduce.py", "joulewise/whole_window.py", "joulewise/powermetrics_fiducial.py",
    "scripts/validate_powermetrics_fiducial.py", "joulewise/adapters/powermetrics.py",
    "joulewise/adapters/mlx_runtime.py", "joulewise/uncertainty_evidence.py",
    "joulewise/calibration_ledger.py", "joulewise/schemas.py", "joulewise/suite.py",
    "joulewise/environment_admission.py", "joulewise/idle_admission.py",
    "joulewise/idle_dependence.py", "joulewise/interfaces.py", "joulewise/validation.py",
    "joulewise/cooldown_anchor.py", "joulewise/provenance.py", "joulewise/calibration_exits.py",
    "scripts/reserve_calibration_window_bracket.py", "scripts/recover_calibration_ledger.py",
}
HARVEST_FILES = {
    "joulewise/cli.py", "joulewise/bundle_read.py", "joulewise/battery_float.py",
    "joulewise/calibration_bracketing.py", "scripts/check_window_provenance.py",
    "scripts/build_bracket_binding.py", "joulewise/salvage_dangler.py",
    "joulewise/calibration_epoch_continuation.py",
}
DESK_ARM_FILES = {"joulewise/identity_pins.py"}
# Everything else under joulewise/analysis_engine, detection floors, manifests,
# mint and paper code is analysis.

FILE_DEFAULT_CODE = {
    "scripts/run_campaign.py": "member.status_not_succeeded",
    "joulewise/controller.py": "member.status_not_succeeded",
    "joulewise/bundle.py": "member.status_not_succeeded",
    "joulewise/reduce.py": "member.strict_validation_failed",
    "joulewise/whole_window.py": "neg8.bound_not_derived",
    "joulewise/powermetrics_fiducial.py": "calibration.capture_invalid",
    "scripts/validate_powermetrics_fiducial.py": "calibration.capture_invalid",
    "joulewise/adapters/powermetrics.py": "member.status_not_succeeded",
    "joulewise/adapters/mlx_runtime.py": "member.status_not_succeeded",
    "joulewise/uncertainty_evidence.py": "member.anchor_not_bounded",
    "joulewise/calibration_ledger.py": "calibration.session_not_bound",
    "joulewise/schemas.py": "member.status_not_succeeded",
    "joulewise/suite.py": "member.status_not_succeeded",
    "joulewise/environment_admission.py": "member.admission_aborted",
    "joulewise/idle_admission.py": "member.admission_aborted",
    "joulewise/idle_dependence.py": "member.strict_validation_failed",
    "joulewise/interfaces.py": "member.bytes_missing",
    "joulewise/validation.py": "member.strict_validation_failed",
    "joulewise/cooldown_anchor.py": "member.cooldown_evidence_unverified",
    "joulewise/provenance.py": "model.identity_mismatch",
    "joulewise/calibration_exits.py": "calibration.capture_invalid",
    "scripts/reserve_calibration_window_bracket.py": "calibration.session_not_bound",
    "scripts/recover_calibration_ledger.py": "calibration.capture_invalid",
    "joulewise/cli.py": "member.strict_validation_failed",
    "joulewise/bundle_read.py": "member.strict_validation_failed",
    "joulewise/battery_float.py": "battery.capture_pair_failed",
    "joulewise/calibration_bracketing.py": "calibration.bracket_acceptance_failed",
    "scripts/check_window_provenance.py": "member.bytes_missing",
    "scripts/build_bracket_binding.py": "calibration.bracket_acceptance_failed",
    "joulewise/salvage_dangler.py": "roster.foreign_attempt",
    "joulewise/calibration_epoch_continuation.py": "calibration.bracket_acceptance_failed",
    "joulewise/identity_pins.py": "model.identity_mismatch",
}

# Keyword overrides for evaluated core rows (first match wins).
CORE_RULES: list[tuple[str, str]] = [
    (r"anchor_energy_envelope|quarter_metric", "member.anchor_energy_envelope_exceeded"),
    (r"thermal", "thermal.powermetrics_pressure_elevated"),
    (r"insufficient_in_window_samples|in-window samples", "instrument.insufficient_in_window_samples"),
    (r"cadence_ratio|cadence", "instrument.cadence_ratio_below_threshold"),
    (r"idle_window_suspect", "member.idle_window_suspect"),
    (r"cooldown.{0,20}cap|cap_hit", "member.cooldown_cap_hit"),
    (r"cooldown", "member.cooldown_evidence_unverified"),
    (r"neg8|neg-8", "neg8.bound_not_derived"),
    (r"pre.?calibration.{0,40}screen|preflight systematic|pre_calibration_scre", "instrument.precal_screen_failed"),
    (r"battery|amperage|ischarging", "battery.capture_pair_failed"),
    (r"token", "member.token_count_mismatch"),
    (r"precheck|target.phase", "member.target_phase_precheck_failed"),
    (r"clock.anchor|anchor bound|not bounded|clock_anchor_bound", "member.anchor_not_bounded"),
    (r"admission", "member.admission_aborted"),
    (r"model artifact|model_artifact|tokenizer|mlx.?version|runtime identity", "model.identity_mismatch"),
]


def _equiv(code: str | None, site: str, stage: str, test_id: str) -> dict[str, str]:
    return {"flag_code": code, "evaluation_site": site, "stage": stage, "test_id": test_id}


EQUIV = {
    "pack": _equiv("pack.identity_mismatch", "joulewise/flags/collect.py:collect_pack_identity", "desk_arm",
                   f"{T_COLLECT}::PackIdentityCounterfactualTests::test_flipped_config_byte_flags_pack_identity"),
    "pack_uncommitted": _equiv("pack.identity_mismatch", "joulewise/flags/collect.py:committed_pack_tree_sha256",
                               "desk_arm",
                               f"{T_COLLECT}::PackIdentityCounterfactualTests::test_uncommitted_pack_flags_pack_identity"),
    "pinned_artifact": _equiv("pack.identity_mismatch", "joulewise/flags/collect.py:plan_tree_pins", "desk_arm",
                              f"{T_COLLECT}::PackIdentityCounterfactualTests::test_missing_extraction_spec_flags_pack_identity"),
    "run_id": _equiv("pack.identity_mismatch", "joulewise/flags/collect.py:roster_run_ids", "desk_arm",
                     f"{T_COLLECT}::PackIdentityCounterfactualTests::test_duplicate_run_id_flags_pack_identity"),
    "model": _equiv("model.identity_mismatch", "joulewise/flags/collect.py:collect_model_identity", "desk_arm",
                    f"{T_COLLECT}::ModelIdentityTests::test_model_file_digest_change_flags_model_identity"),
    "checkout": _equiv("code.executed_differs_from_sealed", "joulewise/flags/collect.py:collect_checkout_identity",
                       "desk_arm", f"{T_COLLECT}::CheckoutIdentityTests::test_head_not_h_claim_flags_code_identity"),
    "executed": _equiv("code.executed_differs_from_sealed", "joulewise/flags/collect.py:collect_executed_code",
                       "desk_arm", f"{T_COLLECT}::ExecutedCodeTests::test_changed_sealed_file_flags_code_identity"),
    "chain": _equiv("code.executed_differs_from_sealed", "joulewise/flags/collect.py:collect_executed_code",
                    "desk_arm", f"{T_COLLECT}::ExecutedCodeTests::test_chain_sidecar_mismatch_flags_code_identity"),
    "roster_fresh": _equiv("roster.before_chain_started", "joulewise/flags/exclusions.py:compute", "harvest",
                           f"{T_EXCL}::RosterRuleTests::test_foreign_attempt_and_pre_chain_bundles_are_ignored"),
    "roster": _equiv("member.bytes_missing", "joulewise/flags/exclusions.py:compute", "harvest",
                     f"{T_EXCL}::RosterRuleTests::test_missing_bundle_excludes_member_and_its_quad"),
    "claim_usable": _equiv(None, "joulewise/flags/exclusions.py:first_claim_usable", "harvest",
                           f"{T_EXCL}::FirstClaimUsableTests::test_first_claim_usable_attempt_is_analysed"),
    "g10": _equiv("g10.not_discharged", "scripts/g10_clock_step_control.py", "window",
                  "tests/test_g10_clock_step_control.py"),
    "process_group": _equiv(None, "scripts/run_night.py:_terminate_process_group", "window", "@index"),
    "harvest_custody": _equiv(None, "joulewise/b5/harvest.py", "harvest", "tests/test_harvest_b5_window.py"),
    "battery": _equiv("battery.member_span", "joulewise/flags/exclusions.py:battery_span_flags", "harvest",
                      f"{T_EXCL}::BatterySpanTests::test_in_force_publication_out_of_float_flags_member"),
    "thermal": _equiv("thermal.os_level_nonzero", "joulewise/flags/exclusions.py:thermal_span_flags", "harvest",
                      f"{T_EXCL}::ThermalSpanTests::test_nonzero_level_in_span_flags_member"),
    "contention": _equiv("contention.request_overlap", "joulewise/flags/exclusions.py:contention_span_flags",
                         "harvest", f"{T_EXCL}::ContentionSpanTests::test_outside_process_over_limit_flags_member"),
    "clock": _equiv("clock.step_overlap", "joulewise/flags/exclusions.py:clock_span_flags", "harvest",
                    f"{T_EXCL}::ClockSpanTests::test_step_inside_span_flags_member"),
    "clock_systematic": _equiv("clock.systematic", "joulewise/flags/exclusions.py:clock_systematic_flags",
                               "harvest", f"{T_EXCL}::ClockSpanTests::test_clock_systematic_needs_majority_of_five"),
    "cell": _equiv("cell.below_minimum", "joulewise/flags/exclusions.py:compute", "harvest",
                   f"{T_EXCL}::CellMinimumTests::test_three_lost_quads_put_cell_below_minimum"),
    "disk": _equiv("disk.low", "joulewise/hazards/disk.py", "window", "tests/hazards"),
    "instrument": _equiv("instrument.cadence_ratio_below_threshold", "joulewise/hazards/instrument.py", "desk_arm",
                         "tests/hazards"),
    "precal": _equiv("instrument.precal_screen_failed", "joulewise/b5/chain.py", "window", "tests/test_b5_chain.py"),
    "lineage": _equiv("member.config_not_in_inventory", "joulewise/window_lineage.py", "window",
                      "tests/test_window_lineage.py"),
    # Core functions that still run; test ids resolved from the test index.
    "neg8": _equiv("neg8.bound_not_derived", "joulewise/whole_window.py:build_neg8_drift_bound_artifact",
                   "window", "@index"),
    "calibration_capture": _equiv("calibration.capture_invalid", "scripts/validate_powermetrics_fiducial.py:main",
                                  "window", "@index"),
    "calibration_bracket": _equiv("calibration.bracket_acceptance_failed",
                                  "joulewise/calibration_bracketing.py:evaluate_calibration_bracket",
                                  "harvest", "@index"),
    "calibration_session": _equiv("calibration.session_not_bound",
                                  "joulewise/calibration_bracketing.py:build_calibration_bracket_binding",
                                  "harvest", "@index"),
    "token": _equiv("member.token_count_mismatch", "joulewise/cli.py:validate_bundle", "harvest", "@index"),
    "strict": _equiv("member.strict_validation_failed", "joulewise/cli.py:validate_bundle", "harvest", "@index"),
    "anchor": _equiv("member.anchor_not_bounded",
                     "joulewise/uncertainty_evidence.py:derive_powermetrics_clock_evidence_v3", "window", "@index"),
    "runtime_replay": _equiv("model.identity_mismatch",
                             "joulewise/identity_pins.py:derive_model_runtime_config_from_metadata",
                             "harvest", "@index"),
    "admission": _equiv("member.admission_aborted", "joulewise/environment_admission.py:environment_admission_refusals",
                        "window", "@index"),
}

# Retired rows: a whole file's rows that share one equivalent.
RETIRED_FILE_EQUIV = {
    "scripts/ed_session/capture_t0_anchor_positive_control.py": "g10",
}

# Retired rows: the first pattern matching ``code`` and ``checks`` (lower case)
# names the hazard-path equivalent. Order matters: specific before general.
RETIRED_RULES: list[tuple[str, str]] = [
    (r"\bg10\b|positive.control", "g10"),
    (r"process group|launcher_group|group_clear|killpg", "process_group"),
    (r"attempt policy|attempt_policy|claim_eligible", "cell"),
    (r"analysis manifest|analysis_manifest|downstream|manifest not strict|manifest is not a json"
     r"|manifest present", "pinned_artifact"),
    (r"freeze receipt|freeze_receipt|freeze_reference|_load_freeze", "pack"),
    (r"offline_input|\bu11\b", "model"),
    (r"window\.env pack_root|root_not_fresh|roots are empty|four distinct directories|is not empty"
     r"|custody_used|custody_overlap|already exists|leftover|zero.capture|successor_license"
     r"|chain_may_have_started|record_consumed|capability has not already been consumed", "roster_fresh"),
    (r"source_tree_mutated|reharvest|archive|backup|custody changed|harvest_before_completion"
     r"|claim_plan_seal|source census|sources did not change|copy tree", "harvest_custody"),
    (r"prior.session|next_window", "claim_usable"),
    (r"chain_python|interpreter", "runtime_replay"),
    (r"stage.list|before_midpoint|sidecar|chain digest|chain_digest|chain bytes|window_chain"
     r"|chain source|chain path|launch artifact|manifest/window.env|manifest/env/chain"
     r"|foreground argv|consumed argv|evidence chain", "chain"),
    (r"config_inventory|config-digest inventory|inventory digest|campaign config|pre.slot"
     r"|same boot as|lifecycle event", "lineage"),
    (r"registration|protocol digest", "executed"),
    (r"bundle census|extra or missing bundle|phase g|lacks metadata|sampler witness|evidence_absent"
     r"|evidence absent|missing science bundle|partial_or_missing|metadata but no summary|bundle dirs"
     r"|roster_or_order", "roster"),
    (r"measurement_head|checkout|repo= literal|measurement_repo|rev-parse|git status|porcelain"
     r"|working tree is dirty|launch head|refs/heads", "checkout"),
    (r"uncommitted|not committed|untracked|byte-identical to|working bytes differ|exactly committed"
     r"|committed and hashable|committed files|git command|git cannot|utf-8 git|symlink|regular blob"
     r"|missing on disk|executable bit|disk bytes", "pack_uncommitted"),
    (r"pack mapping|pack record|pack bytes|pack digest|pack sha|pack_sha256|pack tree|generator"
     r"|pack files|config file's committed bytes", "pack"),
    (r"battery|amperage", "battery"),
    (r"thermal", "thermal"),
    (r"display|hid|screensaver|graphics|quiescen|fseventsd|load average|\bcpu\b", "contention"),
    (r"free (disk )?space|statvfs|disk space", "disk"),
    (r"cadence", "instrument"),
    (r"systematic_clock|more than half", "clock_systematic"),
    (r"network.?time|sntp|systemsetup|clock step|stepped", "clock"),
    (r"pre.?calibration.{0,40}(screen|fiducial)|fiducial b exceeds|d-079 screen|preflight_systematic"
     r"|pre_cal_fiducial", "precal"),
    (r"neg.?8|drift.bound|whole_window_producer|whole-window-verdict", "neg8"),
    (r"strict|non-bounded|bounded_success|member_failed|member failed", "strict"),
    (r"estimator", "pack"),
    (r"model|tokenizer|identity_pin|projection|readiness_identity|identity unit|identity re-derivation"
     r"|identity_arm_reverification|identity reason", "model"),
    (r"bracket session|bracket_session", "calibration_session"),
    (r"post.?calibration|calibrate_slot|disposition 'valid'|captures both", "calibration_capture"),
    (r"acceptance|bracket", "calibration_bracket"),
    (r"duplicate run", "run_id"),
    (r"extraction|external.input|frozen.plan reference|pinned file|primary artifact|frozen-plan", "pinned_artifact"),
]

ANALYSIS_NOTE = "analysis refuses to issue the number; collection is not involved"


def classify_file(path: str) -> str:
    if path in RETIRED_FILES:
        return "retired"
    if path in WINDOW_FILES:
        return "window"
    if path in HARVEST_FILES:
        return "harvest"
    if path in DESK_ARM_FILES:
        return "desk_arm"
    if path == "scripts/run_night.py":
        return "driver"
    return "analysis"


# ------------------------------------------------------------------ functions


def _function_spans(path: Path) -> list[tuple[int, int, str]]:
    text = path.read_text(encoding="utf-8")
    spans: list[tuple[int, int, str]] = []
    if path.suffix == ".py":
        tree = ast.parse(text)

        def walk(node: ast.AST, prefix: list[str]) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    qual = prefix + [child.name]
                    spans.append((child.lineno, child.end_lineno or child.lineno, ".".join(qual)))
                    walk(child, qual)
                else:
                    walk(child, prefix)

        walk(tree, [])
        return spans
    # Shell and Markdown: the nearest preceding shell function or heading.
    lines = text.splitlines()
    marker = None
    start = 1
    for number, line in enumerate(lines, start=1):
        match = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{", line) or re.match(r"(#+\s+.*)$", line)
        if match:
            if marker is not None:
                spans.append((start, number - 1, marker))
            marker = match.group(1).strip()
            start = number
    if marker is not None:
        spans.append((start, len(lines), marker))
    return spans


def enclosing(spans: list[tuple[int, int, str]], line: int) -> str:
    best = None
    for start, stop, name in spans:
        if start <= line <= stop and (best is None or start >= best[0]):
            best = (start, name)
    return best[1] if best else "<module>"


# ------------------------------------------------------------------ test index


class TestIndex:
    def __init__(self, root: Path) -> None:
        self.files: dict[str, str] = {}
        self._module_cache: dict[str, Any] = {}
        self.tests: list[tuple[str, int, str, set[str]]] = []
        for path in sorted((root / "tests").rglob("test_*.py")):
            rel = path.relative_to(root).as_posix()
            if rel.startswith("tests/flags/"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
                tree = ast.parse(text)
            except (UnicodeDecodeError, SyntaxError):
                continue
            self.files[rel] = text
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                    self._add(rel, node, node.name, text)
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test"):
                            self._add(rel, item, f"{node.name}::{item.name}", text)

    def _add(self, rel: str, node: ast.AST, name: str, text: str) -> None:
        segment = ast.get_source_segment(text, node) or ""
        self.tests.append((rel, node.lineno, name, set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", segment))))

    def _for_module(self, module_token: str) -> tuple[list[tuple[str, int, str, set[str]]], list[str]]:
        cached = self._module_cache.get(module_token)
        if cached is not None:
            return cached
        mentioning = {rel for rel, text in self.files.items() if module_token in text}

        def rank(rel: str) -> int:
            return 0 if Path(rel).stem.startswith(f"test_{module_token}") else 1

        tests = sorted((t for t in self.tests if t[0] in mentioning), key=lambda t: (rank(t[0]), t[0], t[1]))
        files = sorted(mentioning, key=lambda rel: (rank(rel), rel))
        self._module_cache[module_token] = (tests, files)
        return tests, files

    def lookup(self, source_file: str, function: str) -> str | None:
        stem = Path(source_file).stem
        module_token = stem if stem != "__init__" else Path(source_file).parent.name
        leaf = function.split(".")[-1] if function != "<module>" and not function.startswith("#") else None
        owner = function.split(".")[0] if function and function[0].isupper() else None
        tests, files = self._for_module(module_token)
        for name in (leaf, owner):
            if not name or name == "__init__":
                continue
            for rel, _line, test_name, tokens in tests:
                if name in tokens:
                    return f"{rel}::{test_name}"
        return files[0] if files else None


# ------------------------------------------------------------------ build


def _text(row: dict[str, Any]) -> str:
    return " ".join(str(row.get(key) or "") for key in ("code", "checks")).lower()


def _first_rule(rules: list[tuple[str, str]], text: str) -> str | None:
    for pattern, value in rules:
        if re.search(pattern, text):
            return value
    return None


def _driver_row(row: dict[str, Any]) -> tuple[str, str]:
    """run_night.py rows: which are on the HAZARD_PACK branch."""

    code = row["code"]
    if "night_chain_digest_mismatch" in code:
        return "evaluated_chain", "chain"
    if "night_record_exists" in code or "night_chain_already_started" in code:
        return "evaluated_record", "roster_fresh"
    if "EVIDENCE_POWER_RECORDER_REPLAY" in code:
        return "evaluated_replay_switch", "strict"
    return "retired", ""


def build(inventory_path: Path) -> dict[str, Any]:
    raw = inventory_path.read_bytes()
    rows = [row for row in json.loads(raw)["refusals"] if row.get("klass") == "NUMBER"]
    spans_cache: dict[str, list[tuple[int, int, str]]] = {}
    index = TestIndex(REPO)
    index_cache: dict[tuple[str, str], str | None] = {}

    def lookup(file: str, function: str) -> str | None:
        key = (file, function)
        if key not in index_cache:
            index_cache[key] = index.lookup(file, function)
        return index_cache[key]

    def resolve_equiv(key: str) -> dict[str, str]:
        equiv = dict(EQUIV[key])
        if equiv["test_id"] == "@index":
            site_file, _, site_function = equiv["evaluation_site"].partition(":")
            equiv["test_id"] = lookup(site_file, site_function)
        return equiv

    entries = []
    for row in rows:
        file = row["file"]
        if file not in spans_cache:
            spans_cache[file] = _function_spans(REPO / file)
        function = enclosing(spans_cache[file], int(row["line"]))
        text = _text(row)
        category = classify_file(file)
        entry: dict[str, Any] = {
            "file": file,
            "function": function,
            "code": row["code"],
            "line_at_base": int(row["line"]),
            "checks": row["checks"],
            "inventory_action": row.get("action"),
            "caught_real_defect": bool(row.get("caught_real_defect")),
        }
        if category == "driver":
            kind, key = _driver_row(row)
            if kind == "retired":
                category = "retired"
            elif kind == "evaluated_chain":
                equiv = resolve_equiv("chain")
                entry.update(disposition="evaluated", stage="desk_arm", flag_code=equiv["flag_code"],
                             evaluation_site=equiv["evaluation_site"], test_id=equiv["test_id"],
                             note="HAZARD_PACK: the chain digest mismatch becomes this flag (plan 3.5)")
            elif kind == "evaluated_record":
                entry.update(disposition="evaluated", stage="window", flag_code="roster.before_chain_started",
                             evaluation_site=f"{file}:{function}", test_id=lookup(file, function),
                             note="write-once night records stay on the HAZARD_PACK branch (O_EXCL claim)")
            else:
                entry.update(disposition="evaluated", stage="window", flag_code="member.strict_validation_failed",
                             evaluation_site=f"{file}:{function}", test_id=lookup(file, function),
                             note="the replay switch is stripped from the chain environment on every branch")
        if category == "retired":
            key = RETIRED_FILE_EQUIV.get(file) or _first_rule(RETIRED_RULES, text) or "pack"
            entry.update(disposition="retired_path", stage=None, flag_code=None, evaluation_site=None,
                         test_id=None, equivalent=resolve_equiv(key),
                         note="retired path: protects nothing block 5 runs")
        elif category in ("window", "harvest", "desk_arm"):
            code = _first_rule(CORE_RULES, text) or FILE_DEFAULT_CODE[file]
            entry.update(disposition="evaluated", stage=category, flag_code=code,
                         evaluation_site=f"{file}:{function}", test_id=lookup(file, function))
        elif category == "analysis":
            entry.update(disposition="evaluated", stage="analysis", flag_code=None,
                         evaluation_site=f"{file}:{function}", test_id=lookup(file, function),
                         note=ANALYSIS_NOTE)
        entries.append(entry)

    # Stable key with an ordinal for (file, function, code) repeats.
    ordinals: Counter[tuple[str, str, str]] = Counter()
    entries.sort(key=lambda e: (e["file"], e["line_at_base"], e["code"]))
    for entry in entries:
        key = (entry["file"], entry["function"], entry["code"])
        entry["ordinal"] = ordinals[key]
        ordinals[key] += 1
        entry["key"] = f"{entry['file']}::{entry['function']}::{entry['code']}::{entry['ordinal']}"

    by_disposition = Counter(e["disposition"] for e in entries)
    by_stage = Counter(e.get("stage") or "retired" for e in entries)
    return {
        "schema_version": SCHEMA,
        "base_commit": BASE,
        "inventory": {"path": str(inventory_path), "sha256": hashlib.sha256(raw).hexdigest(),
                      "number_rows": len(rows)},
        "method": {
            "key": "(file, enclosing function at base, code, ordinal among repeats)",
            "test_id": ("core rows: first test (by file, then line) whose body names the function, "
                        "preferring tests/test_<module>*.py, among test files naming the module; "
                        "else that module's first test file. Hazard-path rows: this lane's tests "
                        "or another lane's pending test file."),
            "builder": "tests/flags/number_rows_builder.py",
        },
        "pending_lane_tests": PENDING_LANE_TESTS,
        "counts": {"by_disposition": dict(sorted(by_disposition.items())),
                   "by_stage": dict(sorted(by_stage.items()))},
        "rows": entries,
    }


def render(document: dict[str, Any]) -> bytes:
    return json.dumps(document, indent=1, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--check", action="store_true", help="fail if the committed map is stale")
    args = parser.parse_args(argv)
    document = build(args.inventory)
    raw = render(document)
    if args.check:
        current = OUTPUT.read_bytes() if OUTPUT.exists() else b""
        if current != raw:
            print("number_rows.json stale: run python tests/flags/number_rows_builder.py", file=sys.stderr)
            return 1
        print("number_rows.json current")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(raw)
    print(json.dumps(document["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
