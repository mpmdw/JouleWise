"""Rebuild ``configs/gates/physics_rows.json`` (provenance tool, not a test).

Reads the gate-prune inventory (``inventory.json``: every refusal site,
classified), keeps the 460 PHYSICS_DIRECT and PHYSICS_PROXY rows, keys each
by (file, function, code, occurrence) at the base commit, and maps it to
exactly one of (plan §2.4):

- ``protects``: one hazard module's ``PROTECTS`` now performs this check;
- ``unchanged_in_core``: the check still runs unchanged on the block-5 path,
  at the named ``file:function``;
- ``retired_proxy``: a proxy on a path block 5 no longer runs, replaced by
  the named module's direct measurement (listed in its ``SUPERSEDES``);
- ``retired_path``: on a path block 5 does not run, with no hazard-path
  counterpart needed (receipt freshness, launch capability, owner steps).

Every row carries a test id.  For ``unchanged_in_core`` rows the test is an
existing test found by searching the test suite for the row's code tokens.

    python3 tests/fixtures/hazards/tools/build_physics_rows.py \
        /Users/edr/night-archive/gate-prune/inventory.json
"""
from __future__ import annotations

import ast
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "configs" / "gates" / "physics_rows.json"
BASE_COMMIT = "a0a4f5a7"

H = "tests/hazards/"
T = {
    "clk_gate": H + "test_clock.py::FrequencyGateTests::test_frequency_3p7_ppm_at_335_s_refuses",
    "clk_skew": H + "test_clock.py::InstantJudgeTests::test_read_skew_over_1ms_refuses",
    "clk_probe": H + "test_clock.py::InstantJudgeTests::test_frequency_probe_failure_is_unmeasured",
    "clk_timex": H + "test_clock.py::InstantJudgeTests::test_corrupted_timex_bytes_are_unmeasured",
    "clk_step": H + "test_clock.py::DwellResidualTests::test_injected_6ms_step_refuses",
    "clk_fchg": H + "test_clock.py::DwellResidualTests::test_changed_frequency_word_refuses",
    "clk_boot": H + "test_clock.py::DwellResidualTests::test_boot_session_change_refuses",
    "bat_chg": H + "test_battery.py::ArmJudgeTests::test_charging_1716_ma_of_0925_refuses",
    "bat_447": H + "test_battery.py::ArmJudgeTests::test_minus_447_ma_on_ac_of_0930_0555Z_refuses",
    "bat_ac": H + "test_battery.py::ArmJudgeTests::test_on_battery_refuses",
    "bat_stale": H + "test_battery.py::ArmJudgeTests::test_reading_older_than_180_s_refuses",
    "bat_gram": H + "test_battery.py::ArmJudgeTests::test_grammar_refusal_is_unmeasured",
    "bat_probe": H + "test_battery.py::ArmJudgeTests::test_ioreg_timeout_and_exit_are_unmeasured",
    "th_lvl": H + "test_thermal.py::ThermalJudgeTests::test_injected_level_1_refuses",
    "th_probe": H + "test_thermal.py::ThermalJudgeTests::test_notifyutil_failure_is_unmeasured_and_refuses_at_arm",
    "th_pmset": H + "test_thermal.py::ThermalJudgeTests::test_pmset_therm_is_recorded_but_never_judged",
    "ct_daemon": H + "test_contention.py::DwellTests::test_fseventsd_184_and_mediaanalysisd_114_percent_refuse_at_2700_s",
    "ct_dwell": H + "test_contention.py::DwellTests::test_first_sample_xprotect_at_36p8_percent_resets_then_600_s_clean_is_ready",
    "ct_probe": H + "test_contention.py::DwellTests::test_failed_snapshots_are_unmeasured_and_break_the_run",
    "dk_low": H + "test_disk.py::DiskJudgeTests::test_free_space_below_the_requirement_refuses",
    "dk_backup": H + "test_disk.py::DiskJudgeTests::test_backup_destination_needs_its_own_headroom",
    "dk_probe": H + "test_disk.py::DiskJudgeTests::test_missing_target_is_unmeasured",
    "in_slow": H + "test_instrument.py::CadenceProbeTests::test_0919_launchd_capture_at_244_to_250_ms_refuses",
    "in_start": H + "test_instrument.py::CadenceProbeTests::test_powermetrics_that_cannot_start_is_unmeasured",
    "arm_census": H + "test_arm.py::ArmTests::test_agent_present_refuses_at_the_census_before_any_action",
    "arm_census_fail": H + "test_arm.py::ArmTests::test_census_that_cannot_run_refuses",
    "arm_unmeasured": H + "test_arm.py::ArmTests::test_unmeasured_refuses_at_arm_for_every_module",
    "arm_go": H + "test_arm.py::ArmTests::test_quiet_float_mac_arms_go_in_the_registered_order",
    "imp": H + "test_import_graph.py::ImportGraphTests::test_hazard_modules_reach_no_retired_module",
}

RETIRED_NOTE = {
    "freshness": "receipt freshness (boot, expiry, temporal budget): the hazard path measures every quantity live inside the launchd job, so there is no receipt to age",
    "launch": "ARM/GO launch capability lifecycle of TRANSACTION_PACK; HAZARD_PACK launches through run_night's no-pack path",
    "caffeinate": "literal launch-argv check of the retired launcher; the HAZARD_PACK chain launch is run_night's (lane L2)",
    "resync": "the T-0 network-time resync is removed (plan §2.3 note); the clock module measures steps and drift directly",
    "owner": "owner-typed confirmation removed by Ed's G10 ruling 6 (agent-run)",
    "policy": "policy text check on the retired harvest; the sealed catalog decides exclusions",
    "lock": "runs-root campaign.lock receipt check of the retired arm; run_campaign's own lock refusal is unchanged in the core",
    "runbook": "runbook-rendered chain body; block 5 renders its chain from the pack plan tree (lane L2) and run_campaign's own lock refusal is unchanged",
    "tooling": "test-fixture tooling, not run by block 5",
    "lowpower": "power mode is not one of the six hazards; pmset -g custom is kept in arm.json as a recorded diagnostic",
    "retry": "magistrate re-arm policy of the retired path; a block-5 pack is re-armed until claim_usable",
    "settle": "post-launch settle literal of the retired T-0 capture",
    "qualification": "block-4 qualification sizing literal; block 4 folds into block 5",
    "boot_at_go": "TRANSACTION_PACK ARM boot/expiry at GO; HAZARD_PACK has no ARM receipt",
}


def P(module, test, note=""):
    return ("protects", module, test, note)


def R(module, test, note=""):
    return ("retired_proxy", module, test, note)


def X(why):
    return ("retired_path", None, "imp", RETIRED_NOTE[why])


def C(site=None, note=""):
    return ("unchanged_in_core", site, None, note)


# (file, line) -> rule; (file, line, code-prefix) for several codes on one line.
RULES = {}
FILE_DEFAULT = {
    "joulewise/adapters/powermetrics.py": C(), "joulewise/analysis_engine/claims.py": C(),
    "joulewise/analysis_engine/inputs.py": C(), "joulewise/analysis_manifest_v3.py": C(),
    "joulewise/calibration_exits.py": C(), "joulewise/calibration_ledger.py": C(),
    "joulewise/controller.py": C(), "joulewise/detection_floor.py": C(),
    "joulewise/environment.py": C(), "joulewise/environment_admission.py": C(),
    "joulewise/idle_admission.py": C(), "joulewise/measurement_liveness.py": C(),
    "joulewise/powermetrics_fiducial.py": C(), "joulewise/reduce.py": C(),
    "joulewise/sampler_teardown.py": C(), "joulewise/schemas.py": C(),
    "joulewise/uncertainty_evidence.py": C(), "joulewise/whole_window.py": C(),
    "scripts/check_window_provenance.py": C(), "scripts/magistrate_watchdog.py": C(),
    "scripts/recover_calibration_ledger.py": C(), "scripts/run_campaign.py": C(),
    "scripts/validate_powermetrics_fiducial.py": C(),
    "joulewise/dwell.py": R("contention", "ct_dwell"),
    "joulewise/network_time_off.py": R("clock", "clk_fchg", "OFF receipt and settle: the clock module checks f identical at dwell start, end and GO and the residual within 1 ms"),
    "joulewise/arm_readiness_evidence.py": R("clock", "clk_fchg", "doctrine-pin text scans about network time"),
    "joulewise/arm_retry.py": X("retry"),
    "joulewise/clock_reference.py": R("clock", "clk_step"),
    "joulewise/corecaptured_loop.py": P("clock", "clk_step"),
    "joulewise/doctor.py": R("instrument", "in_start"),
    "joulewise/kernel_clock.py": P("clock", "clk_timex"),
    "joulewise/v5_qualification.py": P("battery", "bat_chg"),
    "scripts/author_arm_evidence_t0.py": R("arm", "arm_go"),
    "scripts/fixture_orphan_census.py": X("tooling"),
    "scripts/launch_window.py": X("launch"),
}


def rules():
    def add(file, lines, rule):
        for line in ([lines] if isinstance(lines, (int, tuple)) else lines):
            RULES[(file, line) if isinstance(line, int) else (file, *line)] = rule

    f = "docs/phase_2/window_runbook.md"
    add(f, 1530, X("runbook"))
    add(f, [1542, 1649], C(("scripts/validate_powermetrics_fiducial.py", 2368)))

    f = "joulewise/arm_readiness.py"
    add(f, 108, R("clock", "clk_fchg"))
    add(f, [968, 971, 6868, 6883, 7036], R("clock", "clk_step"))
    add(f, [1085, 1116, 7046], R("contention", "ct_dwell"))
    add(f, 1094, R("thermal", "th_lvl"))
    add(f, [1123, 10314], R("arm", "arm_census"))
    add(f, 1132, R("instrument", "in_start"))
    add(f, 1136, P("battery", "bat_447"))
    add(f, 1148, R("disk", "dk_backup"))
    add(f, 2860, R("arm", "arm_go"))
    add(f, [5288, 5336, 6366, 6376, 6605, 6616, 6705, 8809, 9203, 9207, 9250], X("freshness"))
    add(f, [5893, 6433], R("clock", "clk_gate"))
    add(f, 6827, P("clock", "clk_probe"))
    add(f, [6911, 6981], P("clock", "clk_fchg"))
    add(f, [6920, 10049], P("clock", "clk_gate"))
    add(f, 6923, P("clock", "clk_step"))
    add(f, 6947, P("clock", "clk_skew"))
    add(f, 6965, P("clock", "clk_boot"))
    for code, rule in (("readiness_clock_preflight_refused (row clock.network_time_of", R("clock", "clk_fchg")),
                       ("readiness_dependency_refused (row t0.power_path", R("battery", "bat_447")),
                       ("readiness_dependency_refused (row t0.display_thermal_idle", R("thermal", "th_lvl")),
                       ("readiness_machine_preflight_refused (row t0.machine_readines", R("contention", "ct_dwell")),
                       ("readiness_dependency_refused (row t0.no_stray_keepawake", R("arm", "arm_census")),
                       ("readiness_backup_preflight_refused (row t0.storage_backup_ca", R("disk", "dk_backup")),
                       ("readiness_dependency_refused (row t0.passwordless_powermetri", R("instrument", "in_start"))):
        add(f, [(7168, code)], rule)
    add(f, 8618, X("lock"))
    add(f, 9518, X("caffeinate"))
    add(f, [9900, 9904, 10036, 10058, 10240, 10242, 10441, 10750, 10757, 11013, 11178], X("launch"))

    f = "joulewise/arm_readiness_evidence_t0.py"
    add(f, [492, 494, 524], P("arm", "arm_unmeasured"))
    add(f, [733, 737, 742, 1185], R("clock", "clk_step", "absolute UTC offset from sntp enters no energy (plan §2.3 note); stepping is measured directly"))
    add(f, [771, 1147, 1269], P("clock", "clk_skew"))
    add(f, 776, P("clock", "clk_timex"))
    add(f, 779, R("clock", "clk_gate"))
    add(f, 996, X("caffeinate"))
    add(f, [1219, 1221, 1320, 1336], R("clock", "clk_fchg"))
    add(f, 1258, P("clock", "clk_gate"))
    add(f, 1260, P("clock", "clk_probe"))
    add(f, 1264, P("clock", "clk_step"))
    add(f, 1266, P("clock", "clk_fchg"))
    add(f, [1398, 1402, 1404, 1499, 1509], R("contention", "ct_dwell"))
    add(f, 1414, R("arm", "arm_census"))
    add(f, [1437, 1441], P("contention", "ct_probe"))
    add(f, 1443, P("contention", "ct_daemon"))
    add(f, 1482, P("thermal", "th_probe"))
    add(f, 1493, P("thermal", "th_lvl", "pmset -g therm is vacuous on this Mac; the OS pressure level replaces it and pmset is kept as a diagnostic"))
    add(f, 1933, P("instrument", "in_start"))
    add(f, 1970, P("battery", "bat_ac"))
    add(f, 1972, X("lowpower"))
    add(f, [1976, 1984], R("battery", "bat_ac", "adapter wattage is recorded from AdapterDetails in the same ioreg bytes"))
    add(f, 1999, P("battery", "bat_gram"))
    add(f, 2002, P("battery", "bat_chg"))
    add(f, 2070, R("disk", "dk_backup"))

    f = "joulewise/battery_float.py"
    add(f, [105, 108, 247, 250, 254, 399], P("battery", "bat_gram"))
    add(f, 273, P("battery", "bat_stale"))
    add(f, 283, P("battery", "bat_ac"))
    add(f, 285, P("battery", "bat_chg"))
    add(f, [287, 401], P("battery", "bat_447"))
    add(f, [322, 362, 493, 507, 955], C())

    f = "joulewise/night_agent_install.py"
    add(f, [463, 589, 593, 621, 676, 1051, 1075, 1095, 1164], C())
    add(f, 897, R("instrument", "in_slow", "reads the install probe's receipt, up to 6 h old; the arm-time cadence probe inside the launchd job is the gate"))
    add(f, 1254, P("battery", "bat_gram", "lane L2: for HAZARD_PACK the install-time reading is recorded; the arm battery module is the gate"))
    add(f, 1272, P("battery", "bat_447", "lane L2: for HAZARD_PACK the install-time reading is recorded; the arm battery module is the gate"))

    f = "joulewise/night_gate.py"
    add(f, [750, 761], C(note="the driver's census and the in-chain 30 s census still run (doctrine)"))
    add(f, [887, 1826, 1832], P("contention", "ct_probe"))
    add(f, 1326, X("qualification"))
    add(f, [1640, 1643], R("contention", "ct_dwell"))
    add(f, 1664, P("battery", "bat_ac"))
    add(f, 1693, P("battery", "bat_gram"))
    add(f, 1695, P("battery", "bat_447"))
    add(f, [1727, 1733, 1799], R("contention", "ct_daemon"))
    add(f, [1756, 1766], R("thermal", "th_pmset"))
    add(f, 1836, P("contention", "ct_daemon"))

    f = "joulewise/prewindow.py"
    add(f, [12, 19, 22, 64], P("contention", "ct_probe"))
    add(f, 59, P("contention", "ct_daemon"))
    add(f, [74, 78], R("battery", "bat_ac"))
    add(f, 94, P("disk", "dk_low"))
    add(f, 98, P("disk", "dk_probe"))
    add(f, [105, 109], R("arm", "arm_census"))
    add(f, 146, P("contention", "ct_dwell"))

    f = "joulewise/t0_rehearsal.py"
    add(f, [509, 512, 513, 869, 885], R("contention", "ct_dwell", "HID idle (user input) is a proxy for activity; contention is measured directly"))
    add(f, [818, 1332, 1366], R("arm", "arm_census"))
    add(f, [970, 1049], P("clock", "clk_skew"))
    add(f, 1002, P("clock", "clk_probe"))
    add(f, [1035, 1074, 1084, 1100, 1602, 1605], R("clock", "clk_fchg"))
    add(f, [1038, 1043], P("clock", "clk_step"))
    add(f, 1041, R("clock", "clk_gate"))

    f = "scripts/capture_t0_step.py"
    add(f, 352, X("settle"))
    add(f, [648, 771, 822, 832], R("clock", "clk_fchg"))
    add(f, [659, 665, 869], R("contention", "ct_dwell"))
    add(f, [739, 767], X("resync"))
    add(f, [758, 809], P("clock", "clk_fchg"))
    add(f, 763, R("clock", "clk_step"))
    add(f, [798, 840], P("clock", "clk_boot"))
    add(f, 818, P("clock", "clk_gate"))
    add(f, 861, P("contention", "ct_dwell"))

    f = "scripts/check_v5_arm_abort.py"
    add(f, 148, P("battery", "bat_chg"))
    add(f, [191, 192, 199, 201], R("clock", "clk_fchg"))

    f = "scripts/ed_session/capture_t0_anchor_positive_control.py"
    add(f, [215, 227, 240, 272, 314], P("clock", "clk_boot"))
    add(f, 233, P("clock", "clk_fchg"))
    add(f, 236, P("clock", "clk_gate"))
    add(f, [245, 287, 289], P("clock", "clk_step"))
    add(f, [263, 349], R("clock", "clk_fchg"))
    add(f, 457, R("clock", "clk_skew"))
    add(f, [532, 535], X("owner"))

    f = "scripts/harvest_v5_g2b_window.py"
    add(f, 621, C(("joulewise/controller.py", 1390), "re-evaluated at harvest from the core's own admission record"))
    add(f, 675, C(("joulewise/whole_window.py", 5619)))
    add(f, 679, X("policy"))
    add(f, 694, P("battery", "bat_chg"))
    add(f, [696, 712], R("clock", "clk_fchg"))

    f = "scripts/harvest_v5_qualification.py"
    add(f, [88, 110], P("battery", "bat_chg"))
    add(f, 89, C(("joulewise/controller.py", 1390)))
    add(f, [(107, "g4_not_passed")], P("clock", "clk_step"))
    add(f, [(107, "g8_not_passed")], R("arm", "arm_census"))

    f = "scripts/prewindow_check.sh"
    add(f, 90, P("contention", "ct_daemon"))
    add(f, 101, R("contention", "ct_daemon"))
    add(f, 111, R("battery", "bat_ac"))
    add(f, 154, P("disk", "dk_low"))
    add(f, 165, R("arm", "arm_census"))
    add(f, [181, 222], P("contention", "ct_dwell"))

    f = "scripts/produce_t0_rehearsal_bundle.py"
    add(f, [99, 131, 144, 551], R("arm", "arm_census"))
    add(f, [272, 377, 378, 565], R("clock", "clk_fchg"))

    f = "scripts/run_night.py"
    add(f, [568, 884, 1201, 1239, 4160, 4286, 4374, 4642, 4873],
        C(note="driver launch path and install probe, unchanged for HAZARD_PACK (lane L2)"))
    add(f, 1212, C(note="the in-chain 30 s agent census is kept by doctrine"))
    add(f, 2338, R("arm", "arm_go"))
    add(f, [3044, 3803, 3976], P("arm", "arm_go"))
    add(f, [2419, 3062, 3122, 3162, 3912], R("arm", "arm_census"))
    add(f, 2948, R("arm", "arm_census_fail"))
    add(f, 2425, X("boot_at_go"))
    add(f, [2767, 2826, 3160, 3204], P("contention", "ct_probe"))
    add(f, [3049, 3148], P("clock", "clk_boot"))
    add(f, [3051, 3180], P("clock", "clk_step"))
    add(f, 3070, P("contention", "ct_dwell"))
    add(f, [3354, 3356, 3368, 4053], R("clock", "clk_fchg"))
    add(f, [3585, 3687, 3709], R("contention", "ct_dwell"))
    add(f, 3901, P("arm", "arm_unmeasured"))

    f = "scripts/v5_s1_desk_closeout.py"
    add(f, [173, 175, 184], R("clock", "clk_fchg"))
    add(f, 181, R("arm", "arm_census"))

    f = "scripts/write_v5_qualification_plan.py"
    add(f, 211, R("clock", "clk_gate"))
    add(f, 556, P("clock", "clk_gate"))


# Existing tests chosen by hand where the token search found a weak match.
TEST_OVERRIDES = {
    ("joulewise/adapters/powermetrics.py", 370): "tests/test_powermetrics.py::PowermetricsAdapterTests::test_run_fails_at_idle_without_fabricated_baseline_or_warmup",
    ("joulewise/adapters/powermetrics.py", 1146): "tests/test_powermetrics.py::PowermetricsAdapterTests::test_probe_missing_binary_is_telemetry_unavailable",
    ("joulewise/adapters/powermetrics.py", 1203): "tests/test_powermetrics.py::PowermetricsAdapterTests::test_run_fails_at_idle_without_fabricated_baseline_or_warmup",
    ("joulewise/adapters/powermetrics.py", 1212): "tests/test_powermetrics.py::PowermetricsAdapterTests::test_run_fails_at_idle_without_fabricated_baseline_or_warmup",
    ("joulewise/adapters/powermetrics.py", 1764): "tests/test_audit_powermetrics_parser.py::PowermetricsParserBugPins::test_parser_rejects_truncated_stream_with_zero_complete_frames",
    ("joulewise/analysis_engine/claims.py", 168): "tests/test_floor_extraction.py::CpuAndWholeWindowClaimBarrierTests::test_floor_refuses_missing_and_explicitly_unenforced_cpu_admission",
    ("scripts/check_window_provenance.py", 886): "tests/test_check_window_provenance.py::CheckWindowProvenanceTests::test_verdict_status_flipped_isolated_to_f5_2",
    ("joulewise/environment_admission.py", 40): "tests/test_reduce.py::D078R01RegressionTests::test_current_admission_recomputes_snapshot_instead_of_trusting_eligible_true",
    ("joulewise/controller.py", 1390): "tests/test_controller_retry_backoff.py::RetryBackoffTests::test_second_rejection_aborts_with_unchanged_reason_and_no_third_attempt",
    ("scripts/harvest_v5_g2b_window.py", 621): "tests/test_controller_retry_backoff.py::RetryBackoffTests::test_second_rejection_aborts_with_unchanged_reason_and_no_third_attempt",
    ("scripts/harvest_v5_qualification.py", 89): "tests/test_controller_retry_backoff.py::RetryBackoffTests::test_second_rejection_aborts_with_unchanged_reason_and_no_third_attempt",
    ("scripts/run_campaign.py", 3317): "tests/test_run_campaign.py::RunCampaignTests::test_lock_blocks_real_run_is_removed_after_success_and_dry_run_ignores_it",
    ("scripts/run_campaign.py", 4061): "tests/test_run_campaign.py::RunCampaignTests::test_cooldown_v2_contaminated_reference_falls_back_to_frozen_anchor",
    ("scripts/recover_calibration_ledger.py", 447): "tests/test_calibration_ledger.py::CalibrationLedgerTests::test_recovery_cli_has_no_payload_source_and_governs_operator_tail",
}


# --------------------------------------------------------------------------
# Functions at the base, and existing tests for core rows

_SPANS = {}


def spans(path):
    if path not in _SPANS:
        text = (ROOT / path).read_text()
        found = []
        if path.endswith(".py"):
            def walk(node, prefix):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        name = prefix + child.name
                        found.append((child.lineno, child.end_lineno, name))
                        walk(child, name + ".")
                    else:
                        walk(child, prefix)
            walk(ast.parse(text), "")
        _SPANS[path] = (found, text.splitlines())
    return _SPANS[path]


def function_at(path, line):
    found, lines = spans(path)
    if path.endswith(".py"):
        best = None
        for start, end, name in found:
            if start <= line <= end and (best is None or start >= best[0]):
                best = (start, name)
        return best[1] if best else "<module>"
    if path.endswith(".sh"):
        current = "<script>"
        for number, text in enumerate(lines[:line], 1):
            match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{", text)
            if match:
                current = match.group(1)
        return current
    for text in reversed(lines[:line]):
        if text.startswith("#"):
            return text.lstrip("#").strip()
    return "<document>"


def test_index():
    index = []
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        source = path.read_text().splitlines()
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test"):
                        body = "\n".join(source[item.lineno - 1:item.end_lineno])
                        index.append((f"tests/{path.name}::{node.name}::{item.name}", path.name, body))
    return index


STOP = {"ValueError", "RuntimeError", "ProbeError", "TimeoutExpired", "AdapterFailure", "UNKNOWN_ERROR",
        "TELEMETRY_UNAVAILABLE", "not_resolvable", "eligible", "false", "keep", "Refused", "via", "from",
        "status", "line", "lines", "also", "raised", "registry", "row", "the", "and", "decision",
        "failed", "None", "True", "False", "exit", "caller", "refusal"}


def tokens(code):
    out = []
    for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{5,}", code):
        if token not in STOP and token not in out:
            out.append(token)
    for phrase in re.findall(r"'([^']{8,})'", code):
        out.append(phrase.split("<")[0].strip())
    return sorted(out, key=lambda item: (-("_" in item), -len(item)))


def find_test(index, file, function, code):
    stem = Path(file).stem
    preferred = [entry for entry in index if stem in entry[1]]
    others = [entry for entry in index if stem not in entry[1]]
    for token in tokens(code) + [function.split(".")[-1]]:
        if len(token) < 6:
            continue
        for pool in (preferred, others):
            for test_id, _name, body in pool:
                if token in body:
                    return test_id, token
    for test_id, _name, body in preferred:
        return test_id, f"module {stem}"
    return None, None


def main(inventory_path):
    rules()
    data = Path(inventory_path).read_bytes()
    rows = [row for row in json.loads(data)["refusals"] if row["klass"].startswith("PHYSICS")]
    rows.sort(key=lambda row: (row["file"], row["line"] or 0, row["code"]))
    occurrences = collections.Counter()
    index = test_index()
    out, problems = [], []
    for row in rows:
        file, line, code = row["file"], row["line"], row["code"]
        function = function_at(file, line)
        occurrences[(file, function, code)] += 1
        key = {"file": file, "function": function, "code": code,
               "occurrence": occurrences[(file, function, code)]}
        rule = next((value for item, value in RULES.items() if len(item) == 3
                     and item[0] == file and item[1] == line and code.startswith(item[2])), None)
        rule = rule or RULES.get((file, line)) or FILE_DEFAULT.get(file)
        if rule is None:
            problems.append(f"unmapped {file}:{line} {code}")
            continue
        disposition, target, test_key, note = rule
        entry = {"key": key, "line_at_base": line, "klass": row["klass"], "checks": row["checks"],
                 "inventory_action": row["action"], "disposition": disposition}
        if disposition == "unchanged_in_core":
            site_file, site_line = target if target else (file, line)
            site_function = function_at(site_file, site_line)
            entry["site"] = f"{site_file}:{site_function}"
            site_code = code if not target else _row_code(rows, site_file, site_line) or code
            test_id, token = find_test(index, site_file, site_function, site_code)
            if test_id is None:
                problems.append(f"no existing test for {file}:{line} {code}")
                continue
            override = TEST_OVERRIDES.get((file, line))
            entry["test"] = override or test_id
            entry["test_matched_on"] = "chosen by hand" if override else token
            entry["mapping"] = f"unchanged in core: {entry['site']}"
        elif disposition == "protects":
            entry["module"] = target
            entry["test"] = T[test_key]
            entry["mapping"] = f"protected by {target}"
        elif disposition == "retired_proxy":
            entry["module"] = target
            entry["test"] = T[test_key]
            entry["mapping"] = f"retired proxy, replaced by {target}"
        else:
            entry["test"] = T[test_key]
            entry["mapping"] = "on retired path, not run by block 5"
        if note:
            entry["note"] = note
        out.append(entry)
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    document = {
        "schema": "joulewise.physics_rows.v1",
        "source": {"inventory": "night-archive/gate-prune/inventory.json",
                   "inventory_sha256": hashlib.sha256(data).hexdigest(),
                   "base_commit": BASE_COMMIT,
                   "classes": dict(collections.Counter(row["klass"] for row in rows))},
        "dispositions": dict(collections.Counter(entry["disposition"] for entry in out)),
        "rows": out,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    print(json.dumps(document["dispositions"]), len(out))
    for module in ("clock", "battery", "thermal", "contention", "disk", "instrument", "arm"):
        for disposition, name in (("protects", "PROTECTS"), ("retired_proxy", "SUPERSEDES")):
            keys = [entry["key"] for entry in out
                    if entry["disposition"] == disposition and entry.get("module") == module]
            print(f"## {module}.{name} {len(keys)}")


def _row_code(rows, file, line):
    for row in rows:
        if row["file"] == file and row["line"] == line:
            return row["code"]
    return None


if __name__ == "__main__":
    main(sys.argv[1])
