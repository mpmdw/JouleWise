"""V4 registration evidence. Pure stdlib; no probes, data discovery or weights."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess

REGISTRATION = 'configs/campaigns/align_v4/registration/'
RECEIPT_SCHEMA = 'joulewise.align_v4.registration_receipt.v1'
U3_SCHEMA = 'joulewise.align_v4.u3_bar.v1'
WP19_SCHEMA = 'joulewise.align_v4.wp19_identity.v1'
RULINGS = (4, 5, 6, 9, 11, 15, 17, 18, 20)
_NAMED_ARTIFACTS = (
    'docs/align/pilot_protocol_v4.md', 'docs/align/v4/DEVIATIONS.md',
    'docs/align/v4/W1-BLOCKERS-sol.md',
    'docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md',
    'scripts/align_w1_budget_procedure.py', 'joulewise/align/apple/km003c.py',
    'scripts/validate_align_v4_w1_plan.py', 'joulewise/align/apple/pilot_analysis.py',
    'joulewise/align/energy_residual.py',
    'scripts/align_v4_kit.py', 'scripts/align_v4_session.py',
    'scripts/align_v4_thermal_desk.py', 'scripts/align_pilot_session.py',
    'scripts/align_v4_u3_bar.py', 'scripts/align_v4_u3_export.py', 'scripts/align_v4_wp19.py', 'scripts/align_v4_offloads.py',
    'joulewise/align/apple/v4_u3.py', 'joulewise/align/apple/v4_battery.py',
    'scripts/align_v4_battery_log.py',
    'joulewise/align/apple/v4_registration.py', 'joulewise/align/apple/v4_estimands.py',
    'joulewise/align/apple/thermal_desk.py', 'joulewise/align/apple/thermal_gates.py',
    'joulewise/align/apple/endpoint.py', 'joulewise/align/apple/workload.py',
    'scripts/run_night.py', REGISTRATION+'inputs.json', REGISTRATION+'r1_slots.json',
    REGISTRATION+'identity_pins.json', REGISTRATION+'model_artifact_inventory.json',
    REGISTRATION+'local_file_verification.json',
    REGISTRATION+'w1_plan.json', REGISTRATION+'u3_bar.json', REGISTRATION+'wp19_receipt.json',
    REGISTRATION+'battery_window_policy.json',
    REGISTRATION+'r1_soak_reference.json',
    'configs/campaigns/align_v4/plan_tree.json', 'configs/campaigns/align_v4/collection_plan.json',
    # Configured and launched entry points the static walk cannot be trusted to find (delta2):
    # WP15.runtime_entrypoint of registration/inputs.json and the R1 runtime config w1_g0_cap reads,
    # the module-launched package entry (`python -m joulewise`), the registration helpers, and the
    # committed dynamic trace that proves the synthetic W1/D/R1 chain stays inside this set.
    'scripts/align_r1_runtime.py', 'configs/align/v4/r1_runtime.json', 'joulewise/__main__.py',
    'scripts/align_r1_to_w1_chain.py', 'scripts/align_v4_w1_synthetic.py', 'scripts/align_v4_wp18_fixtures.py',
    'scripts/align_v4_dynamic_trace.py', 'docs/align/v4/dynamic_closure_trace.json',
)


# Static execution closure (stdlib ``ast``; imports at module and function level, parent
# packages included, plus script launch edges: exact ``scripts/<name>`` string constants
# and shell tokens) of the episode path and the W1/D/R1 entry points (endpoint.py,
# scripts/run_night.py, align_v4_session.py, align_v4_kit.py, align_w1_budget_procedure.py,
# the night_chains wrappers). R11 lead ruling 3 and delta H01 / DELTA-S2-H1: the
# exact-candidate receipt binds the executed code, scripts included.
# tests/align/test_v4_executed_closure.py recomputes the closure and fails if it is not a
# subset of ARTIFACTS. Not seen by a static walk: importlib string imports, computed
# paths and third-party modules (declared separately).
EXECUTED_CLOSURE = (
    'joulewise/align/apple/v4_u3.py',
    'joulewise/align/apple/v4_battery.py',
    'joulewise/__init__.py',
    'joulewise/adapters/__init__.py',
    'joulewise/adapters/local_transport.py',
    'joulewise/adapters/mlx_runtime.py',
    'joulewise/adapters/mock_runtime.py',
    'joulewise/adapters/mock_spec_runtime.py',
    'joulewise/adapters/mock_telemetry.py',
    'joulewise/adapters/node_client.py',
    'joulewise/adapters/nvidia_smi.py',
    'joulewise/adapters/powermetrics.py',
    'joulewise/adapters/suite_control.py',
    'joulewise/agent_identity.py',
    'joulewise/aggregate.py',
    'joulewise/align/__init__.py',
    'joulewise/align/apple/__init__.py',
    'joulewise/align/apple/budget.py',
    'joulewise/align/apple/campaign.py',
    'joulewise/align/apple/diagnostics.py',
    'joulewise/align/apple/external_volume.py',
    'joulewise/align/apple/generation.py',
    'joulewise/align/apple/pilot.py',
    'joulewise/align/apple/powermode.py',
    'joulewise/align/apple/prompt_cache.py',
    'joulewise/align/apple/r1_runtime.py',
    'joulewise/align/apple/r1_runtime_contract.py',
    'joulewise/align/apple/registry_select.py',
    'joulewise/align/apple/sampler.py',
    'joulewise/align/apple/sampling.py',
    'joulewise/align/apple/smc_enumeration.py',
    'joulewise/align/apple/smc_reader.py',
    'joulewise/align/apple/stop_precedence.py',
    'joulewise/align/apple/thermal.py',
    'joulewise/align/apple/v4_cadence.py',
    'joulewise/align/apple/v4_topup.py',
    'joulewise/align/apple/xml_tool_calls.py',
    'joulewise/align/attribution.py',
    'joulewise/align/endpoints.py',
    'joulewise/align/interfaces.py',
    'joulewise/align/mock_world.py',
    'joulewise/align/power/__init__.py',
    'joulewise/align/power/windows.py',
    'joulewise/align/r0.py',
    'joulewise/align/r0_host.py',
    'joulewise/align/r0_mlx.py',
    'joulewise/align/r0_runner.py',
    'joulewise/align/r0_step.py',
    'joulewise/align/records.py',
    'joulewise/align/runner.py',
    'joulewise/align/shade/__init__.py',
    'joulewise/align/shade/monitor.py',
    'joulewise/align/shade/task.py',
    'joulewise/align/shade/upstream.py',
    'joulewise/analysis_engine/__init__.py',
    'joulewise/analysis_engine/artifact.py',
    'joulewise/analysis_engine/claims.py',
    'joulewise/analysis_engine/distributions.py',
    'joulewise/analysis_engine/estimators.py',
    'joulewise/analysis_engine/inputs.py',
    'joulewise/analysis_engine/multiplicity.py',
    'joulewise/analysis_engine/ratio.py',
    'joulewise/analysis_engine/registry.py',
    'joulewise/analysis_engine/sensitivity.py',
    'joulewise/analysis_manifest.py',
    'joulewise/analysis_manifest_v3.py',
    'joulewise/arm_readiness.py',
    'joulewise/arm_readiness_evidence.py',
    'joulewise/arm_readiness_evidence_t0.py',
    'joulewise/arm_retry.py',
    'joulewise/authentication_io.py',
    'joulewise/axi_decode_config.py',
    'joulewise/b5/__init__.py',
    'joulewise/b5/chain.py',
    'joulewise/b5/driver.py',
    'joulewise/b5/harvest.py',
    'joulewise/b5/plan.py',
    'joulewise/b6/__init__.py',
    'joulewise/b6/acceptance.py',
    'joulewise/b6/acceptance_interface.py',
    'joulewise/b6/agent_pause.py',
    'joulewise/b6/analysis_lane.py',
    'joulewise/b6/archive.py',
    'joulewise/b6/blinding.py',
    'joulewise/b6/calibration.py',
    'joulewise/b6/capture_list.py',
    'joulewise/b6/capture_screen.py',
    'joulewise/b6/code_check.py',
    'joulewise/b6/compose.py',
    'joulewise/b6/courier.py',
    'joulewise/b6/desk_identity.py',
    'joulewise/b6/desk_lane.py',
    'joulewise/b6/driver_lane.py',
    'joulewise/b6/export_runs.py',
    'joulewise/b6/fingerprint.py',
    'joulewise/b6/idle_wait.py',
    'joulewise/b6/lanes.py',
    'joulewise/b6/model_files.py',
    'joulewise/b6/pack_registration.py',
    'joulewise/b6/plan_inputs.py',
    'joulewise/b6/precheck.py',
    'joulewise/b6/precheck_lane.py',
    'joulewise/b6/queue.py',
    'joulewise/b6/registration.py',
    'joulewise/b6/session.py',
    'joulewise/b6/session_paths.py',
    'joulewise/b6/sleep_guard.py',
    'joulewise/b6/smoke.py',
    'joulewise/b6/survivor_screen.py',
    'joulewise/battery_float.py',
    'joulewise/bundle.py',
    'joulewise/bundle_read.py',
    'joulewise/calibration_bracketing.py',
    'joulewise/calibration_custody_worker.py',
    'joulewise/calibration_dispositions.py',
    'joulewise/calibration_epoch_continuation.py',
    'joulewise/calibration_exits.py',
    'joulewise/calibration_ledger.py',
    'joulewise/campaign_generator_core.py',
    'joulewise/campaign_provenance.py',
    'joulewise/cli.py',
    'joulewise/clock.py',
    'joulewise/clock_reference.py',
    'joulewise/controller.py',
    'joulewise/cooldown.py',
    'joulewise/cooldown_anchor.py',
    'joulewise/corecaptured_loop.py',
    'joulewise/desk_compress.py',
    'joulewise/desk_restore.py',
    'joulewise/detection_floor.py',
    'joulewise/detection_floor_registry.py',
    'joulewise/determinism_gate.py',
    'joulewise/doctor.py',
    'joulewise/dominance_closeout.py',
    'joulewise/dwell.py',
    'joulewise/envelope_gate.py',
    'joulewise/environment.py',
    'joulewise/environment_admission.py',
    'joulewise/external/__init__.py',
    'joulewise/external/km003c_parse.py',
    'joulewise/external/km003c_usb.py',
    'joulewise/flags/__init__.py',
    'joulewise/flags/catalog.py',
    'joulewise/flags/collect.py',
    'joulewise/flags/core.py',
    'joulewise/flags/exclusions.py',
    'joulewise/flags/schema.py',
    'joulewise/flags/sink.py',
    'joulewise/floor_extraction.py',
    'joulewise/floor_mint_estimator.py',
    'joulewise/hazards/__init__.py',
    'joulewise/hazards/arm.py',
    'joulewise/hazards/base.py',
    'joulewise/hazards/battery.py',
    'joulewise/hazards/clock.py',
    'joulewise/hazards/contention.py',
    'joulewise/hazards/disk.py',
    'joulewise/hazards/instrument.py',
    'joulewise/hazards/monitor.py',
    'joulewise/hazards/smc.py',
    'joulewise/hazards/thermal.py',
    'joulewise/identity_pins.py',
    'joulewise/idle_admission.py',
    'joulewise/idle_dependence.py',
    'joulewise/interfaces.py',
    'joulewise/kernel_clock.py',
    'joulewise/kv_size.py',
    'joulewise/measurement_liveness.py',
    'joulewise/model_panel.py',
    'joulewise/network_time_off.py',
    'joulewise/night_agent_install.py',
    'joulewise/night_gate.py',
    'joulewise/night_kinds.py',
    'joulewise/night_plan_writer.py',
    'joulewise/output_identity.py',
    'joulewise/powermetrics_fiducial.py',
    'joulewise/prewindow.py',
    'joulewise/provenance.py',
    'joulewise/publication_privacy.py',
    'joulewise/quiet_admission.py',
    'joulewise/quiet_predicate_campaign.py',
    'joulewise/receipt_oracle.py',
    'joulewise/reduce.py',
    'joulewise/report.py',
    'joulewise/salvage_dangler.py',
    'joulewise/sampler_teardown.py',
    'joulewise/schemas.py',
    'joulewise/session_structure.py',
    'joulewise/suite.py',
    'joulewise/t0_rehearsal.py',
    'joulewise/tolerances.py',
    'joulewise/uncertainty_evidence.py',
    'joulewise/v5_qualification.py',
    'joulewise/validation.py',
    'joulewise/whole_window.py',
    'joulewise/window_lineage.py',
    'joulewise/zero_capture_facts.py',
    'scripts/advance_b5_ledger_pin.py',
    'scripts/align_pilot_kit.py',
    'scripts/align_r0_checks.py',
    'scripts/align_r1_rehearsal.py',
    'scripts/align_r1_turn_counts_export.py',
    'scripts/align_smc_enumerate.py',
    'scripts/author_arm_evidence_t0.py',
    'scripts/author_arm_readiness_evidence.py',
    'scripts/b5_window_calibration_verdict.py',
    'scripts/b6_courier.sh',
    'scripts/backup_runs.sh',
    'scripts/build_bracket_binding.py',
    'scripts/build_family_marker.py',
    'scripts/bytes_gates.py',
    'scripts/bytes_h_session.py',
    'scripts/calibration_cadence_report.py',
    'scripts/cap_replay_harness.py',
    'scripts/capture_t0_step.py',
    'scripts/check_v5_arm_abort.py',
    'scripts/check_window_provenance.py',
    'scripts/collect_clock_reference.py',
    'scripts/collect_window_flags.py',
    'scripts/ed_session/capture_t0_anchor_positive_control.py',
    'scripts/fixture_orphan_census.py',
    'scripts/g10_clock_step_control.py',
    'scripts/gen_derivation_night.py',
    'scripts/gen_evidence_night.py',
    'scripts/gen_g2_phase_d.py',
    'scripts/generate_g2a_probe_inputs.py',
    'scripts/generate_matrix.py',
    'scripts/harvest_b5_window.py',
    'scripts/harvest_b6_session.py',
    'scripts/harvest_g2a_window.py',
    'scripts/harvest_v5_g2b_window.py',
    'scripts/harvest_v5_qualification.py',
    'scripts/harvest_window.py',
    'scripts/hazard_monitor.py',
    'scripts/install_night_agent.sh',
    'scripts/issue_calibration_acceptance_generation.py',
    'scripts/km003c_monitor.py',
    'scripts/launch_window.py',
    'scripts/magistrate_watchdog.py',
    'scripts/mint_floor_artifact_generalized.py',
    'scripts/night_chains/align_r1_rehearsal.zsh',
    'scripts/night_chains/calibration_derivation_only.zsh',
    'scripts/night_chains/quiet_predicate_evidence.zsh',
    'scripts/prewindow_check.sh',
    'scripts/produce_t0_rehearsal_bundle.py',
    'scripts/quiet_mac_prep.sh',
    'scripts/recover_calibration_ledger.py',
    'scripts/rehearse_t0_unattended.py',
    'scripts/replay_powermetrics_frames.py',
    'scripts/reserve_calibration_window_bracket.py',
    'scripts/restore_v5_null_reservation.py',
    'scripts/run_campaign.py',
    'scripts/sample_quiet_predicate_evidence.py',
    'scripts/select_g2a_prefill_length.py',
    'scripts/summarize_g2a_prefill_probe.py',
    'scripts/v5_s1_desk_closeout.py',
    'scripts/validate_powermetrics_fiducial.py',
    'scripts/verify_family_marker.py',
    'scripts/write_derivation_night_inputs.py',
    'scripts/write_v5_qualification_plan.py',
)
ARTIFACTS = _NAMED_ARTIFACTS + tuple(p for p in EXECUTED_CLOSURE if p not in _NAMED_ARTIFACTS)

# Two tiers (Opus cold review MED-1; delta2 inverted the default). STRICT is the default:
# every bound path is strict, and a change is a re-registration (new receipt, signature, both
# gates). AMENDMENT is a short explicit allowlist of modules proven NOT executed on the
# W1/D/R1 path: each is classified retired, analysis, mock, other-hardware, acceptance or desk
# in the reviewed refusal census (configs/gates/hazard_refusals.json scan.not_scanned) and none
# is executed by the committed dynamic trace (docs/align/v4/dynamic_closure_trace.json). A
# change to one is admitted only through a lead-signed ``amendments`` row in the receipt.
AMENDMENT_ALLOWLIST = (
    # other_hardware: another platform's adapter; never selected on the Mac
    'joulewise/adapters/node_client.py', 'joulewise/adapters/nvidia_smi.py',
    # retired: the ARM/T0 and v5 qualification path; block 5 does not run it
    'joulewise/arm_readiness_evidence.py', 'joulewise/arm_readiness_evidence_t0.py',
    'joulewise/night_agent_install.py', 'joulewise/quiet_predicate_campaign.py',
    'joulewise/t0_rehearsal.py', 'joulewise/v5_qualification.py', 'joulewise/zero_capture_facts.py',
    'scripts/capture_t0_step.py', 'scripts/check_v5_arm_abort.py',
    'scripts/produce_t0_rehearsal_bundle.py', 'scripts/write_v5_qualification_plan.py',
    # analysis: desk analysis after the harvest; decides no collection and no window exclusion
    'joulewise/envelope_gate.py', 'joulewise/floor_extraction.py', 'joulewise/kv_size.py', 'joulewise/report.py',
    # desk: tooling run before the arm or after the harvest; never inside a window
    'joulewise/b6/precheck.py', 'joulewise/b6/smoke.py', 'joulewise/session_structure.py',
    'scripts/advance_b5_ledger_pin.py', 'scripts/bytes_gates.py', 'scripts/install_night_agent.sh',
    # mock / acceptance: test doubles; desk issuing of instrument acceptances before any window
    'scripts/fixture_orphan_census.py', 'scripts/issue_calibration_acceptance_generation.py',
)
# A small independent inventory of the actual W1/D/R1 launch spine (delta2 S2): launched,
# configured or chain-named programs that must be bound and strict. The tests derive more of
# them from plan_tree.json, the chain tool table, inputs.json (WP15) and the dynamic trace.
STRICT_SCRIPTS = (
    'scripts/run_night.py', 'scripts/align_pilot_kit.py', 'scripts/align_pilot_session.py',
    'scripts/align_r1_rehearsal.py', 'scripts/align_r1_runtime.py', 'scripts/align_r1_turn_counts_export.py',
    'scripts/align_v4_kit.py', 'scripts/align_v4_offloads.py', 'scripts/align_v4_session.py',
    'scripts/align_v4_thermal_desk.py', 'scripts/align_v4_u3_bar.py', 'scripts/align_v4_wp19.py',
    'scripts/align_w1_budget_procedure.py', 'scripts/align_v4_battery_log.py',
    'scripts/validate_align_v4_w1_plan.py', 'scripts/bytes_h_session.py', 'scripts/launch_window.py',
    'scripts/hazard_monitor.py', 'scripts/km003c_monitor.py', 'scripts/collect_window_flags.py',
    'scripts/collect_clock_reference.py', 'scripts/g10_clock_step_control.py', 'scripts/run_campaign.py',
    'scripts/magistrate_watchdog.py', 'scripts/prewindow_check.sh', 'scripts/quiet_mac_prep.sh',
    'scripts/backup_runs.sh', 'scripts/b6_courier.sh', 'scripts/reserve_calibration_window_bracket.py',
    'scripts/validate_powermetrics_fiducial.py', 'scripts/b5_window_calibration_verdict.py',
    'joulewise/__main__.py', 'configs/align/v4/r1_runtime.json',
)


def is_strict(path):
    return path not in AMENDMENT_ALLOWLIST


AMENDMENT_FIELDS = ('path', 'old_sha256', 'new_sha256', 'reason', 'lead_signature')


def _amendment_chains(receipt, bindings):
    """Validate the lead-signed amendment rows; return {path: final new_sha256}."""
    from scripts.align_v4_kit import valid_lead_signature
    rows = receipt.get('amendments', [])
    if not isinstance(rows, list):
        raise ValueError('registration_receipt amendments malformed')
    final = {}
    for row in rows:
        if (not isinstance(row, dict) or set(row) != set(AMENDMENT_FIELDS)
                or not is_digest(row['old_sha256']) or not is_digest(row['new_sha256'])
                or not isinstance(row['reason'], str) or not row['reason'].strip()
                or not valid_lead_signature(row['lead_signature'])):
            raise ValueError('registration_receipt amendment row malformed')
        path = row['path']
        if path not in bindings or path not in ARTIFACTS:
            raise ValueError(f'registration_receipt amendment names an unbound path: {path}')
        if is_strict(path):
            raise ValueError(f'registration_receipt amendment refused for a strict-tier path: {path} (re-register)')
        if row['old_sha256'] != final.get(path, bindings[path]):
            raise ValueError(f'registration_receipt amendment chain broken: {path}')
        final[path] = row['new_sha256']
    return final


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def is_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _local(root, path):
    """Refuse traversal/symlinks before reading any receipt-supplied path."""
    p = Path(path)
    if p.is_absolute() or not p.parts or any(x in ('.', '..', 'restricted', 'night-custody', 'night-archive') for x in p.parts):
        raise ValueError('registration receipt path refused')
    target = Path(root)
    for part in p.parts:
        target = target / part
        if target.is_symlink():
            raise ValueError('registration receipt symlink refused')
    return target


def artifact_set_digest(root):
    """One digest over the current bytes of every bound artifact (missing ones marked).

    The arm derives "code or config changed since the last desk-passed state" by
    comparing this with the digest recorded when that desk passed; the packet's own
    flag is only cross-checked. ``python3 -m joulewise.align.apple.v4_registration``
    prints it for the desk-pass record.
    """
    h = hashlib.sha256()
    for path in sorted(ARTIFACTS):
        try:
            value = digest(_local(root, path).read_bytes())
        except (OSError, ValueError):
            value = 'missing'
        h.update(f'{path}\0{value}\n'.encode())
    return h.hexdigest()


def _committed_bytes(root, commit, paths):
    """Bytes of ``commit:path`` for every path in one ``git cat-file --batch``.

    A path absent at the commit maps to None. One process keeps a receipt over
    the full executed-module closure cheap.
    """
    request = ''.join(f'{commit}:{path}\n' for path in paths).encode()
    try:
        out = subprocess.run(['git', 'cat-file', '--batch'], cwd=root, input=request,
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError('registration_receipt commit unreadable') from exc
    result, offset = {}, 0
    for path in paths:
        end = out.index(b'\n', offset)
        header = out[offset:end].split()
        offset = end+1
        if len(header) == 3 and header[1] == b'blob':
            size = int(header[2])
            result[path] = out[offset:offset+size]
            offset += size+1
        else:
            result[path] = None
    return result


def validate_receipt(receipt, root):
    """Bind reviewed bytes to one existing Git commit and current working bytes.

    Gate judgments and signature are lead-owned assertions, not fabricated by
    this validator. A receipt never creates its own approval or gate reports.
    """
    from scripts.align_v4_kit import valid_lead_signature
    if not isinstance(receipt, dict) or receipt.get('schema') != RECEIPT_SCHEMA or receipt.get('status') != 'registered':
        raise ValueError('registration_receipt is pending or malformed')
    if not valid_lead_signature(receipt.get('lead_signature')):
        raise ValueError('registration_receipt requires a lead signature')
    commit = receipt.get('commit', '')
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('registration_receipt requires a full commit')
    if receipt.get('rulings') != {str(n): 'installed' for n in RULINGS}:
        raise ValueError('registration_receipt ruling installation incomplete')
    artifacts = receipt.get('artifacts')
    if not isinstance(artifacts, dict) or set(artifacts) != set(ARTIFACTS):
        raise ValueError('registration_receipt artifact set incomplete')
    gates = receipt.get('gates')
    if not isinstance(gates, dict) or set(gates) != {'A', 'B'}:
        raise ValueError('registration_receipt requires both gate verdicts')
    bindings = dict(artifacts)
    for stage, gate in gates.items():
        if not isinstance(gate, dict) or gate.get('verdict') != 'ADMIT':
            raise ValueError(f'registration_receipt stage {stage} not admitted')
        path = gate.get('path')
        if not isinstance(path, str) or not path.startswith('docs/align/v4/'):
            raise ValueError('registration_receipt gate report path refused')
        _local(root, path)
        bindings[path] = gate.get('sha256')
    for path, expected in bindings.items():
        if not is_digest(expected):
            raise ValueError(f'registration_receipt invalid digest: {path}')
    pinned = _committed_bytes(root, commit, list(bindings))
    amended = _amendment_chains(receipt, bindings)
    for path, expected in bindings.items():
        try:
            raw = _local(root, path).read_bytes()
        except OSError as exc:
            raise ValueError(f'registration_receipt missing committed artifact: {path}') from exc
        if pinned.get(path) is None:
            raise ValueError(f'registration_receipt missing committed artifact: {path}')
        if digest(pinned[path]) != expected:
            raise ValueError(f'registration_receipt digest drift: {path}')
        if digest(raw) != expected and digest(raw) != amended.get(path):
            tier = 'strict tier: re-register' if is_strict(path) else 'amendment tier: needs a lead-signed amendment'
            raise ValueError(f'registration_receipt digest drift: {path} ({tier})')
    return receipt


def require_registration(root):
    path = REGISTRATION+'registration_receipt.json'
    try:
        receipt = json.loads(_local(root, path).read_bytes())
    except (OSError, ValueError) as exc:
        raise ValueError('registration_receipt.json missing or unreadable; W1 is not registered') from exc
    validate_receipt(receipt, root)
    bar = json.loads(_local(root, REGISTRATION+'u3_bar.json').read_bytes())
    validate_u3(bar, root=root, commit=receipt['commit'])
    from joulewise.align.apple.v4_battery import validate_policy
    validate_policy(json.loads(_local(root, REGISTRATION+'battery_window_policy.json').read_bytes()))
    wp19 = json.loads(_local(root, REGISTRATION+'wp19_receipt.json').read_bytes())
    validate_wp19(wp19)
    return receipt


def derive_u3(pairs, source_sha256, *, policy=None):
    if not isinstance(source_sha256, dict) or not source_sha256 or not all(is_digest(v) for v in source_sha256.values()):
        raise ValueError('U3 requires input sha256 digests')
    from joulewise.align.apple import v4_u3
    relative = v4_u3.relative_pairs(pairs)
    if policy is not None:
        if not isinstance(policy, dict):
            raise ValueError('U3 predictive policy must be an object')
        if policy.get('transfer_justification_sha256') not in source_sha256.values():
            raise ValueError('U3 requires digest-bound D transfer justification source')
        return json.loads(v4_u3.canonical(v4_u3.derive(pairs, source_sha256, policy)))
    return {'schema': U3_SCHEMA, 'status': 'PENDING', 'n': len(relative),
            's_rel_sample': statistics.stdev(relative), 'signed_relative_differences': relative,
            'source_sha256': source_sha256, 'pairs': pairs,
            'derivation_required': ['frozen predictive distribution and small-sample uncertainty',
                                    'operating-characteristic and series/dependence sensitivity',
                                    'explicit limitation of 30B-to-D transfer',
                                    'lead-adopted bar and independent registration gate'],
            'limitations': 'Descriptive pilot summary only; no multiplier, margin or false-fail guarantee.'}


def validate_u3(bar, *, root=None, commit=None):
    from joulewise.align.apple import v4_u3
    try:
        if (not isinstance(bar, dict) or not isinstance(bar.get('source_sha256'), dict)
                or not bar['source_sha256'] or not all(is_digest(v) for v in bar['source_sha256'].values())):
            raise ValueError('U3 PENDING source digests')
        v4_u3.validate_cached(v4_u3.canonical(bar))
        for path in (*bar['source_sha256'], bar['independent_gate']['path']):
            # Lexical path policy also applies to a detached desk artifact.
            if not isinstance(path, str) or any(c in path for c in ('\n', '\r', '\0')):
                raise ValueError('U3 source/gate path refused')
            _local(Path('.'), path)
        # Validate source and gate bytes at registration, including Git custody.
        if root is not None:
            bindings = {**bar['source_sha256'], bar['independent_gate']['path']: bar['independent_gate']['sha256']}
            pinned = _committed_bytes(root, commit, list(bindings)) if commit else {}
            found_export = False
            for path, expected in bindings.items():
                raw = _local(root, path).read_bytes()
                if digest(raw) != expected or (commit and (pinned.get(path) is None or digest(pinned[path]) != expected)):
                    raise ValueError('U3 source/gate custody drift')
                if path == bar['independent_gate']['path']:
                    gate = json.loads(raw)
                    if (not isinstance(gate, dict) or gate.get('verdict') != 'ADMIT'
                            or gate.get('derivation_sha256') != bar['derivation_sha256']):
                        raise ValueError('U3 independent gate bytes do not admit this derivation')
                if path in bar['source_sha256']:
                    try:
                        source = json.loads(raw)
                    except ValueError:
                        continue  # A supporting report can be Markdown.
                    found_export |= (isinstance(source, dict) and source.get('pairs') == bar['pairs']
                                     and source.get('policy') == bar['policy'])
            if not found_export:
                raise ValueError('U3 source export does not reproduce pairs and policy')
    except (TypeError, KeyError, AttributeError, OverflowError, OSError) as exc:
        raise ValueError('U3 malformed or missing derivation evidence') from exc
    return bar


def u3_margin(mean_energy_j, bar, *, population='30B', configuration_sha256=None):
    validate_u3(bar)
    if (type(mean_energy_j) not in (int, float) or not math.isfinite(mean_energy_j) or mean_energy_j <= 0
            or population not in ('30B', 'D')):
        raise ValueError('U3 requires positive finite energy and a qualified population')
    if population == 'D' and bar['prediction'].get('d_screen') != 'not_refuted':
        raise ValueError(f"U3 D transfer screen {bar['prediction'].get('d_screen')}: D U3 inconclusive (ruling 6)")
    if population == 'D' and configuration_sha256 is not None and configuration_sha256 != bar['policy']['d_configuration_sha256']:
        raise ValueError('U3 D configuration changed; new prospective qualification required')
    return mean_energy_j*bar['prediction']['relative_bar_'+population]


# Protocol section 4 / AGREEMENT-FINAL R02: arm within about 30 minutes of a
# completed top-up. The wording is the registered bound; no slack is added.
TOPUP_WINDOW_S = 30*60


def battery_arm(observation, attested_by, topup=None, *, now_epoch_s=None):
    """Arm-time battery predicate (R02).

    ``topup`` is source- and time-bound completion evidence,
    ``{'completed_at_epoch_s': float, 'source': str}``. UpdateTime dates the
    current ioreg observation, not the end of charging, so a fresh observation
    never substitutes for it. Missing, future-dated or older-than-window
    evidence refuses.
    """
    reasons = []
    if not isinstance(attested_by, str) or not attested_by.strip():
        reasons.append('OBC off requires --obc-off-attested-by')
    age, soc, current = (observation.get(k) for k in ('update_age_s', 'current_capacity_pct', 'instant_amperage_ma'))
    finite = lambda x: type(x) in (int, float) and math.isfinite(x)
    if (observation.get('passed') is not True or observation.get('probe_error') is not False
            or observation.get('external_connected') is not True or observation.get('is_charging') is not False
            or not finite(age) or not 0 <= age <= 180 or not finite(soc) or not 99 <= soc <= 100
            or not finite(current) or abs(current) > 200):
        reasons.append('battery top-up incomplete/unobserved: require fresh AC, >=99%, not charging, |InstantAmperage| <=200 mA')
    topup_age = None
    completed = topup.get('completed_at_epoch_s') if isinstance(topup, dict) else None
    source = topup.get('source') if isinstance(topup, dict) else None
    if not finite(completed) or not isinstance(source, str) or not source.strip():
        reasons.append('completed top-up evidence missing or inadmissible: require --battery-log showing a completed charge within 30 min or continuous float since')
    elif not finite(now_epoch_s):
        reasons.append('completed top-up cannot be timed: arm time unavailable')
    else:
        topup_age = now_epoch_s-completed
        if topup_age < 0:
            reasons.append('completed top-up time is after the arm time')
        elif topup_age > TOPUP_WINDOW_S:
            reasons.append(f'completed top-up is stale: {topup_age:.0f} s > {TOPUP_WINDOW_S} s before arm')
    return {'admitted': not reasons, 'reasons': reasons, 'obc_off_attested_by': attested_by,
            'topup': topup if isinstance(topup, dict) else None, 'topup_age_s': topup_age,
            'topup_window_s': TOPUP_WINDOW_S, 'observation': observation}


def wp19_identity(fixtures, rendered_prompt_ids, live_x_turns, *, live_source_sha256):
    if not is_digest(live_source_sha256):
        raise ValueError('WP19 requires live X source digest')
    checks = {}
    for arm in ('X', 'Y'):
        turns = fixtures[arm]['turns']
        rendered = rendered_prompt_ids.get(arm, [])
        checks[arm] = bool(turns) and len(rendered) == len(turns) and all(
            row == turn['prompt_token_ids'] for row, turn in zip(rendered, turns))
    x = fixtures['X']['turns']
    live_ok = bool(live_x_turns) and len(live_x_turns) <= len(x) and all(
        all(row.get(k) == ref[k] for k in ('turn', 'prompt_token_ids', 'output_token_ids'))
        for row, ref in zip(live_x_turns, x))
    passed = all(checks.values()) and live_ok and len(live_x_turns) == len(x)
    return {'schema': WP19_SCHEMA, 'verdict': 'pass' if passed else 'fail',
            'render_all_turns': checks, 'live_x_identical': live_ok,
            'live_x_turns_compared': len(live_x_turns), 'live_x_complete': len(live_x_turns) == len(x),
            'live_source_sha256': live_source_sha256,
            'contrast_predeclared': None if passed else 'INCONCLUSIVE: identity broken',
            'static_proof': {'warmup': 'joulewise/adapters/mlx_runtime.py:MlxRuntimeAdapter.warmup (greedy; no episode cache)',
                             'reseed': 'joulewise/align/apple/endpoint.py:MlxEndpoint (turn_seed before measured draw)'}}


def validate_wp19(receipt):
    if (not isinstance(receipt, dict) or receipt.get('schema') != WP19_SCHEMA
            or receipt.get('verdict') not in ('pass', 'fail') or not is_digest(receipt.get('live_source_sha256'))
            or type(receipt.get('live_x_turns_compared')) is not int or receipt['live_x_turns_compared'] < 0
            or set(receipt.get('render_all_turns', {})) != {'X', 'Y'}
            or any(type(v) is not bool for v in receipt.get('render_all_turns', {}).values())
            or not receipt.get('static_proof')
            or (receipt['verdict'] == 'pass' and (not all(receipt['render_all_turns'].values())
                                                 or receipt['live_x_turns_compared'] < 1
                                                 or receipt.get('live_x_identical') is not True
                                                 or receipt.get('live_x_complete') is not True))
            # R11 R07: zero native X turns is a retained non-veto failed
            # identity (INCONCLUSIVE contrast), never a PASS or complete X.
            or (receipt['live_x_turns_compared'] == 0 and (receipt['verdict'] != 'fail'
                                                          or receipt.get('live_x_identical') is True
                                                          or receipt.get('live_x_complete') is True))
            or (receipt['verdict'] == 'fail' and receipt.get('contrast_predeclared') != 'INCONCLUSIVE: identity broken')):
        raise ValueError('wp19_receipt.json pending or malformed')
    return receipt


def cohort_identity(config, spec, runtime):
    """Bind model/quantization source, observed stack and effective controls.

    Capture/consumer custody locators differ by member; their effective
    thermal controls stay in the identity. Never substitute requested stack
    versions for an absent runtime observation.
    """
    policy = spec.execution_policy_projection()
    if 'thermal' in policy:
        policy['thermal'] = {k: v for k, v in policy['thermal'].items() if k != 'window_reference'}
    canonical = lambda value: digest(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                               allow_nan=False).encode())
    model = config.get('model', {})
    observed = all(runtime.get(k) for k in ('mlx_version', 'mlx_lm_version', 'model_artifact_identity'))
    return {'model_source': model.get('source'), 'model_revision': model.get('revision'),
            'runtime_sha256': canonical(runtime) if observed else None,
            'execution_policy_sha256': canonical(policy)}


def desk_diagnostics(members, *, r1_soak=None, battery_policy=None):
    """Rulings 11/15/17/18 and B printouts; missing evidence stays unavailable."""
    from joulewise.align.apple import v4_estimands as v4
    d = [r for r in members if r.get('role') == 'D']
    by_ordinal = {r.get('ordinal'): r for r in d}
    candidates = {i: v4.sentinel_admissibility(by_ordinal.get(i, {})) for i in (5, 18)}
    chosen = next((i for i in (5, 18) if candidates[i]['admissible']), None)
    sentinel = {'ordinal': chosen, 'candidates': candidates,
                'E_ref_basis': 'R1 replay pair plus W1 5/17' if chosen == 5 else
                               'PENDING matched alternate reference and prospective recovery' if chosen == 18 else
                               'unresolved; no admissible original or alternate',
                'reference_status': 'candidate; final-policy comparison required' if chosen == 5 else 'unresolved',
                'predecessor_disclosure': 'W1 5/17 follow 30B; alternate 18 and D_k late sentinel follow D'}
    reference = next((r.get('window_reference') for r in members if r.get('ordinal') == 5), {}) or {}
    waits = [{'ordinal': r['ordinal'],
              'G0_wait_s': sum(i.get('duration_s', 0) for i in r.get('intervals', []) if i['kind'] == 'G0'),
              'G1_wait_s': sum(i.get('duration_s', 0) for i in r.get('intervals', []) if i['kind'] == 'G1')}
             for r in members if r.get('ordinal') is not None]
    from joulewise.align.apple.v4_battery import window_consequences
    windows = window_consequences(members, battery_policy)
    return {'sentinel': sentinel, 'battery_windows': windows,
            'warm_reference': v4.warm_reference_diagnostic(reference, r1_soak or {}, waits),
            'd_cohort': v4.d_configuration_assertion(d),
            'rebuilds': [{'id': r['id'], 'ordinal': r.get('ordinal'),
                          'cache_statistics': r.get('cache_statistics', {'status': 'not_recorded'})} for r in members],
            'no_rebuild_sensitivity': {'status': 'print_only', 'member_ids': [r['id'] for r in members
                if r.get('cache_statistics', {}).get('rebuilds') == 0]}}


if __name__ == '__main__':
    import sys
    print(artifact_set_digest(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[3]))
