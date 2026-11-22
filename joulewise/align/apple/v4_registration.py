"""V4 registration evidence. Pure stdlib; no probes, data discovery or weights."""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import importlib
import json
import math
import os
import re
from pathlib import Path
import stat
import statistics
import subprocess
import unicodedata

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
    'scripts/zero_ntp_frequency.c',
    'scripts/watchdog_status.py', 'scripts/launch_align_r0.py',
    'scripts/run_align_r1_smoke.py',
    'joulewise/align/apple/r1_phase_table.py',
    'scripts/align_r1_followup_kit.py', 'scripts/align_r1_thermal_replay.py',
    'scripts/run_align_r0_launchagent.sh', 'scripts/post_window_unstrand.sh',
    'scripts/install_magistrate_watchdog.sh', 'tests/fixtures/night_plan_v1_retired.json',
    # RL-62: the flag catalog the v4 desk harvest resolves to (scripts/harvest_b6_session.py falls through to
    # joulewise.b6.registration.DEFAULTS['catalog']); it decides members_excluded, so it is bound, strict.
    'configs/b6/flag_catalog_b6.json',
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
    # The arm rebuilds the next-arm packet with this builder (a packet is a pointer, never trusted data).
    'scripts/align_v4_next_arm_packet.py',
    # Production launch-argument templates (delta3 S1 F02): night_agent_install reads the night and
    # probe templates to build the job's ProgramArguments/environment; the watchdog and b6-loop
    # installers read theirs. A changed template changes what runs, so each is strict.
    'configs/launchd/com.joulewise.night.plist.template', 'configs/launchd/com.joulewise.night-probe.plist.template',
    'configs/launchd/com.joulewise.magistrate.plist.template', 'configs/launchd/com.joulewise.b6loop.plist.template',
    # RUN_STATE 226 R15: the frozen D/C/T series (order, roles, seeds) and its builder bind with W1.
    'scripts/align_v4_series.py', 'configs/campaigns/align_v4/series/series_manifest.json',
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
    'joulewise/adapters/powermetrics_reap.py',
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
    'joulewise/align/apple/light_triage.py',
    'joulewise/align/apple/pilot.py',
    'joulewise/align/apple/powermode.py',
    'joulewise/align/apple/prompt_cache.py',
    'joulewise/align/apple/r1_runtime.py',
    'joulewise/align/apple/r1_runtime_contract.py',
    'joulewise/align/apple/registry_select.py',
    # RL-145 rows 6-7 (reached from the smoke launcher through the follow-up kit): the Part C evaluator
    # and the desk's per-turn prints. Bound with the rest of the executed closure (PR #777 review).
    'joulewise/align/apple/rl145_prints.py',
    'joulewise/align/apple/sampler.py',
    'joulewise/align/apple/sampling.py',
    'joulewise/align/apple/smc_enumeration.py',
    'joulewise/align/apple/smc_reader.py',
    'joulewise/align/apple/stop_precedence.py',
    'joulewise/align/apple/thermal.py',
    'joulewise/align/apple/v4_balance.py',
    'joulewise/align/apple/v4_cadence.py',
    'joulewise/align/apple/v4_contention.py',
    'joulewise/align/apple/v4_desk_seal.py',
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
    'joulewise/harvest_profile.py',
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
    'joulewise/timing_receipts.py',
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
    'scripts/align_r1_part_c.py',
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

# Two tiers (Opus cold review MED-1; delta2 inverted the default; delta3 emptied the allowlist).
# STRICT is the default: every bound path is strict, and a change is a re-registration (new
# receipt, signature, both gates). AMENDMENT is an explicit allowlist, and it may hold only a
# module absent from BOTH the static closure of every execution entry point AND the full dynamic
# trace (docs/align/v4/dynamic_closure_trace.json, which includes the production hazard-pack
# night-runner scenario). Python executes a module body on import, so a statically reachable
# module is never "not executed"; the refusal census's not-scanned classes describe that
# census's scope, not execution. Every bound path is statically reachable by construction, so
# the allowlist is empty: if in doubt, strict; re-registration on such a change is the accepted
# cost. A change to a listed path is admitted only through a lead-signed ``amendments`` row;
# an amendment row naming a strict path always refuses.
AMENDMENT_ALLOWLIST = ()
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


def artifact_set_digest_from(reader):
    """One digest over every bound artifact; ``reader(path)`` returns its bytes or None (marked missing)."""
    h = hashlib.sha256()
    for path in sorted(ARTIFACTS):
        raw = reader(path)
        h.update(f'{path}\0{digest(raw) if raw is not None else "missing"}\n'.encode())
    return h.hexdigest()


def artifact_set_digest(root):
    """The artifact-set digest of the working tree at ``root`` (missing files marked).

    The arm derives "code or config changed since the last desk-passed state" by comparing this
    with the digest recorded for the last desk pass; the packet's own flag is only cross-checked.
    ``python3 -m joulewise.align.apple.v4_registration`` prints it.
    """
    def reader(path):
        try:
            return _local(root, path).read_bytes()
        except (OSError, ValueError):
            return None
    return artifact_set_digest_from(reader)


def confined_reader(root, *other_roots):
    """Read repository-relative files, following links within the named roots.

    Check each target before touching it. In particular, resolving an
    escaping link must not stat the file or directory it names.
    """
    aliases = {Path(path).absolute(): Path(path).resolve(strict=True) for path in (root, *other_roots)}
    aliases.update({path: path for path in tuple(aliases.values())})
    ordered_aliases = sorted(aliases, key=lambda path: -len(path.parts))
    roots = sorted(set(aliases.values()), key=lambda path: -len(path.parts))
    prefixes = {parent for scope in roots for parent in scope.parents}
    blocked = {'.git', 'restricted', 'night-custody', 'night-archive'}

    def scope_for(path):
        return next((scope for scope in roots if path.is_relative_to(scope)), None)

    def read(relative, *, metadata_only=False):
        relative = Path(relative)
        if relative.is_absolute() or not relative.parts or '..' in relative.parts:
            raise ValueError('staged input needs a repository-relative path')
        directory = aliases[Path(root).absolute()]
        parts = relative.parts
        links = 0
        while parts:
            name, *parts = parts
            if name == '..':
                directory = directory.parent
                continue
            target = directory / name
            scope = scope_for(target)
            if scope is None:
                if target in prefixes and parts:
                    directory = target
                    continue
                raise ValueError(f'staged input escapes its allowed roots: {relative}')
            if any(part in blocked or part.startswith('jw-b5-') for part in target.relative_to(scope).parts):
                raise ValueError(f'staged input names a restricted path: {relative}')
            status = target.lstat()
            if stat.S_ISLNK(status.st_mode):
                links += 1
                if links > 40:
                    raise ValueError(f'staged input has a symlink loop: {relative}')
                link = Path(os.readlink(target))
                if link.is_absolute():
                    alias = next((scope for scope in ordered_aliases if link.is_relative_to(scope)), None)
                    if alias is None:
                        raise ValueError(f'staged input escapes its allowed roots: {relative}')
                    directory = aliases[alias]
                    link = link.relative_to(alias)
                parts = [*link.parts, *parts]
            elif parts:
                if not stat.S_ISDIR(status.st_mode):
                    raise ValueError(f'staged input parent is not a directory: {relative}')
                directory = target
            elif stat.S_ISREG(status.st_mode):
                return None if metadata_only else target.read_bytes()
        raise ValueError(f'staged input is not a regular file: {relative}')

    return read


# C1 execution export and prepared-input closure.

SCHEMA = 'joulewise.c1_staged_closure.v1'
PACKET = 'series/c1-next-arm.json'
OUTPUTS = 'prepare-outputs.json'
RESTRICTED = frozenset({'.git', 'restricted', 'night-custody', 'night-archive'})
HEX = re.compile(r'[0-9a-f]+')
PIN = re.compile(r'[0-9a-f]{64}')


def decode(raw):
    def unique(pairs):
        values = {}
        for key, value in pairs:
            if key in values:
                raise ValueError(f'duplicate JSON key: {key}')
            values[key] = value
        return values
    return json.loads(raw, object_pairs_hook=unique)


def key(name):
    if not isinstance(name, str) or '\0' in name or any(
            part in ('', '.', '..') for part in name.split('/')):
        raise ValueError(f'invalid closure path: {name!r}')
    for part in name.split('/'):
        if part in RESTRICTED or part.startswith('jw-b5-'):
            raise ValueError(f'restricted closure path: {name}')
    return name


def distinct(names):
    spellings = set()
    for name in names:
        normalized = unicodedata.normalize('NFC', key(name)).casefold()
        if normalized in spellings:
            raise ValueError(f'aliased closure path: {name}')
        spellings.add(normalized)


def git(root, *args):
    env = {**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_OPTIONAL_LOCKS': '0'}
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
        env.pop(name, None)
    result = subprocess.run(['git', '--literal-pathspecs', '-C', str(root), *args],
                            env=env, capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f'C1 Git authority unavailable: {args[0]}')
    return result.stdout


def full_oid(root, value, *, object_format=None):
    fmt = object_format or git(root, 'rev-parse', '--show-object-format').decode().strip()
    lengths = {'sha1': 40, 'sha256': 64}
    if fmt not in lengths or not isinstance(value, str) or len(value) != lengths[fmt] or not HEX.fullmatch(value):
        raise ValueError('C1 authority requires a full Git object ID')
    if git(root, 'rev-parse', '--verify', value + '^{commit}').decode().strip() != value:
        raise ValueError('C1 authority must identify a commit object')
    return value


def tree_identity(authority, commit):
    fmt = git(authority, 'rev-parse', '--show-object-format').decode().strip()
    commit = full_oid(authority, commit, object_format=fmt)
    return {'object_format': fmt, 'commit': commit,
            'tree': git(authority, 'rev-parse', commit + '^{tree}').decode().strip()}


class Roots:
    """Resolve each link hop before touching its target, retaining logical names."""
    def __init__(self, repo, stage):
        self.alias = {Path(p).absolute(): Path(p).absolute().resolve(strict=True) for p in (repo, stage)}
        self.repo, self.stage = (self.alias[Path(p).absolute()] for p in (repo, stage))
        if self.repo.is_relative_to(self.stage) or self.stage.is_relative_to(self.repo):
            raise ValueError('C1 repo and stage roots must be disjoint')
        self.allowed = tuple(self.alias.values())
        self.alias.update({p: p for p in self.allowed})
        self.prefixes = {parent for root in self.allowed for parent in root.parents}

    def path(self, path):
        path = Path(path)
        if not path.is_absolute():
            raise ValueError(f'staged path must be absolute: {path}')
        root = next((p for p in self.alias if path.is_relative_to(p)), None)
        if root is None:
            raise ValueError(f'staged path is outside R/S: {path}')
        current = self.alias[root]
        parts = list(path.relative_to(root).parts)
        hops = 0
        while parts:
            part = parts.pop(0)
            if part == '..':
                current = current.parent
                if current not in self.prefixes and not any(current.is_relative_to(p) for p in self.allowed):
                    raise ValueError(f'staged link escapes R/S: {path}')
                continue
            target = current / part
            scope = next((p for p in self.allowed if target.is_relative_to(p)), None)
            if scope is None:
                if target in self.prefixes and parts:
                    current = target
                    continue
                raise ValueError(f'staged link escapes R/S: {path}')
            key(target.relative_to(scope).as_posix()) if target != scope else None
            mode = target.lstat().st_mode
            if stat.S_ISLNK(mode):
                hops += 1
                if hops > 40:
                    raise ValueError(f'staged link cycle: {path}')
                link = Path(os.readlink(target))
                if link.is_absolute():
                    base = next((p for p in self.alias if link.is_relative_to(p)), None)
                    if base is None:
                        raise ValueError(f'staged link escapes R/S: {path}')
                    current = self.alias[base]
                    link = link.relative_to(base)
                parts = list(link.parts) + parts
            else:
                if parts and not stat.S_ISDIR(mode):
                    raise ValueError(f'staged path parent is not a directory: {path}')
                current = target
        if not any(current.is_relative_to(p) for p in self.allowed):
            raise ValueError(f'staged path is outside R/S: {path}')
        return current

    def regular(self, path):
        result = self.path(path)
        if not stat.S_ISREG(result.lstat().st_mode):
            raise ValueError(f'staged input is not a regular file: {path}')
        return result

    def walk(self, root, *, symlinks=()):
        def descend(physical, prefix, ancestors):
            if physical in ancestors:
                raise ValueError(f'staged directory cycle: {prefix}')
            parents = ancestors | {physical}
            for entry in sorted(physical.iterdir()):
                name = key(prefix + entry.name)
                if name in symlinks:
                    if not entry.is_symlink():
                        raise ValueError(f'expected a Git symlink: {name}')
                    target = self.path(entry)
                    if not (target.is_file() or target.is_dir()):
                        raise ValueError(f'unsupported Git symlink target: {name}')
                    yield name, '120000', os.fsencode(os.readlink(entry))
                    continue
                target = self.path(entry)
                mode = target.lstat().st_mode
                if stat.S_ISDIR(mode):
                    yield name, '040000', None
                    yield from descend(target, name + '/', parents)
                elif stat.S_ISREG(mode):
                    yield name, '100755' if mode & stat.S_IXUSR else '100644', target
                else:
                    raise ValueError(f'unsupported staged entry: {name}')
        root = self.path(root)
        if not root.is_dir():
            raise ValueError('C1 closure root must be a directory')
        yield from descend(root, '', set())


def blob_id(fmt, kind, raw):
    digest = hashlib.new(fmt)
    digest.update(f'{kind} {len(raw)}\0'.encode())
    digest.update(raw)
    return digest.hexdigest()


def tree_entries(authority, commit):
    entries = {}
    for entry in git(authority, 'ls-tree', '-rzt', '--full-tree', commit).split(b'\0'):
        if entry:
            header, raw_name = entry.split(b'\t', 1)
            mode, _, oid = header.decode().split()
            name = key(raw_name.decode())
            if mode not in {'040000', '100644', '100755', '120000'}:
                raise ValueError(f'unsupported Git entry: {name}')
            entries[name] = (mode, oid)
    distinct(entries)
    return entries


def verify_repo(authority, roots, identity):
    expected = tree_identity(authority, identity['commit'])
    if identity != expected:
        raise ValueError('C1 execution tree identity does not match the authority')
    fmt = expected['object_format']
    entries = tree_entries(authority, expected['commit'])
    verified = {}
    directories = {'': []}
    for name, mode, path in roots.walk(roots.repo,
                                      symlinks={p for p, (mode, _) in entries.items() if mode == '120000'}):
        if entries.get(name, (None,))[0] != mode:
            raise ValueError(f'unexpected repository path or mode: {name}')
        parent, _, leaf = name.rpartition('/')
        directories[parent].append((leaf, mode, name))
        if mode == '040000':
            directories[name] = []
        else:
            oid = blob_id(fmt, 'blob', path if mode == '120000' else path.read_bytes())
            if oid != entries[name][1]:
                raise ValueError(f'repository blob mismatch: {name}')
            verified[name] = oid
    if missing := entries.keys() - verified.keys() - directories.keys():
        raise ValueError(f'missing repository path: {min(missing)}')
    for name, children in reversed(directories.items()):
        raw = b''.join((mode.lstrip('0') + ' ' + leaf + '\0').encode() + bytes.fromhex(verified[path])
                       for leaf, mode, path in sorted(children, key=lambda item: item[0] + ('/' if item[1] == '040000' else '')))
        verified[name] = blob_id(fmt, 'tree', raw)
    if verified[''] != expected['tree']:
        raise ValueError('observed repository tree ID differs')


def stage_pins(pins):
    if not isinstance(pins, dict) or PACKET in pins:
        raise ValueError('invalid staged inventory or reserved packet collision')
    distinct([*pins, PACKET])
    if any(not isinstance(digest, str) or not PIN.fullmatch(digest) for digest in pins.values()):
        raise ValueError('invalid staged SHA-256 pin')
    return pins


@dataclass(frozen=True)
class VerifiedView:
    roots: Roots
    packet: dict
    packet_sha256: str
    stage_files: dict

    def stage_read(self, relative):
        name = key(Path(relative).as_posix())
        if name not in self.stage_files:
            raise ValueError(f'staged input is not pinned: {name}')
        raw = self.roots.regular(self.roots.stage / name).read_bytes()
        if digest(raw) != self.stage_files[name]:
            raise ValueError(f'staged SHA-256 mismatch: {name}')
        return raw


def verify_view(authority, repo, stage, *, delivery_ref, delivery_commit, execution_commit=None):
    """Authenticate the fixed packet, then compare both complete physical walks."""
    if not isinstance(delivery_ref, str) or not delivery_ref.startswith('refs/'):
        raise ValueError('C1 delivery needs a named ref')
    commit = full_oid(authority, delivery_commit)
    if git(authority, 'show-ref', '--verify', '--hash', delivery_ref).decode().strip() != commit:
        raise ValueError('C1 delivery ref does not name the supplied commit')
    row = git(authority, 'ls-tree', commit, '--', PACKET)
    if row.split()[:2] not in ([b'100644', b'blob'], [b'100755', b'blob']):
        raise ValueError('C1 delivery packet must be a committed regular blob')
    raw = git(authority, 'show', f'{commit}:{PACKET}')
    roots = Roots(repo, stage)
    if roots.regular(roots.stage / PACKET).read_bytes() != raw:
        raise ValueError('staged packet differs from the delivery blob')
    packet = decode(raw)
    closure = packet['c1_closure']
    if closure['schema'] != SCHEMA or (execution_commit is not None and closure['repo']['commit'] != execution_commit):
        raise ValueError('invalid C1 staged closure identity')
    pins = {**stage_pins(closure['stage_files']), PACKET: digest(raw)}
    verify_repo(authority, roots, closure['repo'])
    seen = set()
    for name, mode, path in roots.walk(roots.stage):
        if mode == '040000':
            continue
        if name not in pins:
            raise ValueError(f'unlisted staged file: {name}')
        if digest(path.read_bytes()) != pins[name]:
            raise ValueError(f'staged SHA-256 mismatch: {name}')
        seen.add(name)
    if missing := pins.keys() - seen:
        raise ValueError(f'missing staged file: {min(missing)}')
    return VerifiedView(roots, packet, digest(raw), pins)


def declare_outputs(repo, stage, paths):
    """Record known prepare outputs. This never enumerates staging."""
    roots = Roots(repo, stage)
    files = {}
    for name in paths:
        name = key(Path(name).as_posix())
        if name in {OUTPUTS, PACKET} or name in files:
            raise ValueError(f'duplicate or reserved prepared output: {name}')
        files[name] = digest(roots.regular(roots.stage / name).read_bytes())
    distinct(files)
    descriptor = roots.stage / OUTPUTS
    with descriptor.open('xb') as handle:
        handle.write((json.dumps(files, sort_keys=True) + '\n').encode())
    return descriptor


def declared_pins(repo, stage):
    roots = Roots(repo, stage)
    raw = roots.regular(roots.stage / OUTPUTS).read_bytes()
    pins = stage_pins(decode(raw))
    if OUTPUTS in pins:
        raise ValueError('prepare manifest contains itself')
    for name, expected in pins.items():
        if digest(roots.regular(roots.stage / name).read_bytes()) != expected:
            raise ValueError(f'prepared output changed: {name}')
    return {**pins, OUTPUTS: digest(raw)}

LEDGER = 'runs/calibration_observation_ledger.jsonl'
PACK = Path('configs/campaigns/align-v4-c1')
# The pinned campaign runner probes at most six ancestors of a resolved
# config directory. Keep its last probe inside S without editing the runner.
C1_DISPATCH = Path('members/dispatch')


def ledger_pin(roots, path, pins):
    physical = roots.regular(path)
    if not physical.is_relative_to(roots.stage):
        raise ValueError('the starting ledger must reside in S')
    name = physical.relative_to(roots.stage).as_posix()
    if name not in pins:
        raise ValueError('the starting ledger has no prepared inventory row')
    return {'path': str(physical), 'sha256': pins[name]}


def check_ledger(path, pin, *, starting=False):
    """Check one physical ledger. Only reservation checks its starting bytes."""
    named = Path(pin['path'])
    path = Path(path).resolve(strict=True)
    if path != named or not named.is_absolute() or not path.is_file():
        raise ValueError('ledger does not resolve to the canonical C1 path')
    if starting and digest(path.read_bytes()) != pin['sha256']:
        raise ValueError('C1 starting ledger SHA-256 mismatch')
    return path


class LaunchView:
    """The legacy command namespace is a projection of the two verified trees."""
    def __init__(self, roots, view):
        self.roots, self.root = roots, Path(view).absolute()

    def locate(self, path, *, directory=False):
        try:
            return self._locate(path, directory=directory)
        except FileNotFoundError as exc:
            raise FileNotFoundError(exc.errno, 'staged input is missing', str(path)) from exc

    def _locate(self, path, *, directory):
        path = Path(path)
        if not path.is_absolute():
            path = self.root / path
        if path.is_relative_to(self.root):
            name = path.relative_to(self.root)
            if '..' in name.parts:
                raise ValueError(f'path escapes the C1 launch view: {path}')
            # Resolve the actual launch alias using the same fence as the walks.
            current = self.root
            for index, part in enumerate(name.parts):
                key(part)
                current /= part
                mode = current.lstat().st_mode
                if stat.S_ISLNK(mode):
                    link = Path(os.readlink(current))
                    target = link if link.is_absolute() else current.parent / link
                    result = self.roots.path(target.joinpath(*name.parts[index + 1:]))
                    break
                if not stat.S_ISDIR(mode):
                    raise ValueError(f'undeclared file in the launch view: {path}')
            else:
                if not directory:
                    raise ValueError(f'staged input is not a file: {path}')
                return current
        else:
            result = self.roots.path(path)
        mode = result.lstat().st_mode
        if not (stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)):
            raise ValueError(f'invalid staged input type: {path}')
        return result


def launch_aliases(roots):
    """Return the launch aliases. The pack remains one physical directory."""
    leaves, folders = {}, set()
    for root in (roots.repo, roots.stage):
        for directory, dirs, names in os.walk(root, followlinks=False):
            parent = Path(directory)
            folders.add(parent.relative_to(root))
            links = [name for name in dirs if (parent / name).is_symlink()]
            if root == roots.stage and parent == root / PACK.parent and PACK.name in dirs:
                links.append(PACK.name)
                dirs.remove(PACK.name)
            for name in [*names, *links]:
                path = parent / name
                relative = path.relative_to(root)
                key(relative.as_posix())
                if relative.as_posix() == PACKET:
                    continue
                if relative in leaves:
                    raise ValueError(f'overlapping R/S logical entry: {relative}')
                leaves[relative] = path
    if leaves.keys() & folders:
        raise ValueError('R/S launch namespace has a file/directory overlap')
    return folders, leaves


def link_launch_view(roots, view, *, runtime=None, git_link=None):
    view = Path(view)
    folders, leaves = launch_aliases(roots)
    for relative in sorted(folders):
        (view / relative).mkdir(parents=True, exist_ok=True)
    for name, path in (('.venv', runtime), ('.git', git_link)):
        if path is not None:
            leaves[Path(name)] = Path(path)
    for relative, path in sorted(leaves.items()):
        alias = view / relative
        if alias.is_symlink() and Path(os.readlink(alias)) == path:
            continue
        alias.symlink_to(path)
    return LaunchView(roots, view)


def verify_launch_view(roots, view, *, runtime=None, git_link=None):
    view = Path(view)
    if view.is_symlink() or not view.is_dir():
        raise ValueError('the launch view must be a regular directory')
    folders, leaves = launch_aliases(roots)
    for name, path in (('.venv', runtime), ('.git', git_link)):
        if path is not None:
            leaves[Path(name)] = Path(path)
    observed = set()
    for directory, dirs, names in os.walk(view, followlinks=False):
        parent = Path(directory)
        relative = parent.relative_to(view)
        if relative not in folders:
            raise ValueError(f'unlisted launch directory: {relative}')
        observed.add(relative)
        for name in [*names, *(d for d in dirs if (parent / d).is_symlink())]:
            path = parent / name
            relative = path.relative_to(view)
            if relative not in leaves or not path.is_symlink() or Path(os.readlink(path)) != leaves[relative]:
                raise ValueError(f'wrong launch alias: {relative}')
            observed.add(relative)
    if missing := (leaves.keys() | folders) - observed:
        raise ValueError(f'missing launch path: {min(missing)}')
    return LaunchView(roots, view)


def export_repo(authority, commit, dest):
    """Export the execution commit with raw Git modes and no worktree fallbacks."""
    entries = tree_entries(authority, commit)
    dest = Path(dest)
    dest.mkdir()
    blobs = [oid for mode, oid in entries.values() if mode != '040000']
    # Use one Git process. A batch record includes the exact object length.
    env = {**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_OPTIONAL_LOCKS': '0'}
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
        env.pop(name, None)
    result = subprocess.run(['git', '-C', str(authority), 'cat-file', '--batch'],
                            input=('\n'.join(blobs) + '\n').encode(), env=env,
                            check=True, capture_output=True)
    from io import BytesIO
    stream = BytesIO(result.stdout)
    for name, (mode, oid) in entries.items():
        path = dest / name
        if mode == '040000':
            path.mkdir()
            continue
        header = stream.readline().split()
        if len(header) != 3 or header[:2] != [oid.encode(), b'blob']:
            raise ValueError(f'cannot export Git blob: {name}')
        raw = stream.read(int(header[2]))
        if stream.read(1) != b'\n':
            raise ValueError(f'truncated Git blob: {name}')
        if mode == '120000':
            path.symlink_to(os.fsdecode(raw))
        else:
            path.write_bytes(raw)
            path.chmod(0o755 if mode == '100755' else 0o644)


def load_prepared(view, read):
    state = decode(read('session.json'))
    if (state.get('v4_series') or {}).get('window_id') != 'C1':
        raise ValueError('the C1 handoff requires a C1 prepared session')
    if (Path(state['source_measurement_root']) != view.roots.repo
            or Path(state['measurement_root']) != view.root):
        raise ValueError('prepared launch view differs from the C1 handoff')
    night_path = view.roots.regular(state['plan_path'])
    if not night_path.is_relative_to(view.roots.stage):
        raise ValueError('the prepared night plan must reside in S')
    raw = read(night_path.relative_to(view.roots.stage))
    if digest(raw) != state['plan_sha256']:
        raise ValueError('prepared night plan digest differs')
    night = decode(raw)
    hazard = night['hazard_window']
    for path in (night['chain_path'], night['chain_sha256_path'], hazard['window_env']['path']):
        target = view.roots.regular(path)
        if not target.is_relative_to(view.roots.stage):
            raise ValueError('the prepared chain controls must reside in S')
        read(target.relative_to(view.roots.stage))
    for descriptor in (hazard['window_env'], hazard.get('registration')):
        if descriptor is not None:
            path = view.locate(descriptor['path'])
            if digest(path.read_bytes()) != descriptor['sha256']:
                raise ValueError(f'prepared control SHA-256 mismatch: {path}')
    return state, night


def shade_dependency(spec):
    """Run the SHADE consumer's own offline resolver in the chain environment."""
    from joulewise.align.apple import pilot
    from joulewise.align.shade.upstream import PinnedUpstream

    kwargs = spec.get('task_kwargs') or {}
    if not isinstance(kwargs, dict):
        raise ValueError('SHADE task arguments must be a mapping')
    if kwargs.get('cache_dir') is None and 'XDG_CACHE_HOME' not in os.environ:
        # Otherwise the consumer would fall back to the launching user's home.
        raise ValueError('SHADE dependency is absent from the staged view: no cache_home binds its cache')
    try:
        if spec.get('task_factory') == pilot.FACTORY:
            # The align workload's own resolution of its configured factory.
            module, name = pilot.FACTORY.split(':', 1)
            upstream = getattr(importlib.import_module(module), name)(**kwargs).upstream
        else:
            upstream = PinnedUpstream(allow_fetch=False, **{
                name: kwargs[name] for name in ('cache_dir', 'commit', 'file_sha256') if name in kwargs})
    except (TypeError, ValueError) as exc:
        raise ValueError(f'SHADE task arguments are invalid: {exc}') from exc
    if upstream.prepare() is None:
        if 'upstream_manifest_mismatch' in upstream.flags:
            raise ValueError('staged SHADE manifest differs from the configured pin: '
                             + ', '.join(upstream.flags))
        raise ValueError('SHADE dependency is absent from the staged view: ' + ', '.join(upstream.flags))


def config_references(data, config, view, runner):
    def resolve(reference, parent, *, base=view.root):
        path = Path(reference)
        if path.is_absolute():
            return view.locate(path)
        try:
            return view.locate(base / path)
        except FileNotFoundError:
            return view.locate(parent / path)

    suite = runner.suite_manifest_ref_from_config(data)
    refs = (runner.generator_sidecar_ref_from_config(data), suite)
    visited = set()
    documents = [(data, config.parent)]
    for ref in filter(None, refs):
        path = resolve(ref, config.parent, base=view.roots.repo)
        documents.append((decode(path.read_bytes()), path.parent))
    if suite:
        manifest = resolve(suite, config.parent, base=view.roots.repo)
        annotated = manifest.with_name(f'{manifest.stem}_annotations.json')
        try:
            path = view.locate(annotated)
        except FileNotFoundError:
            pass
        else:
            documents.append((decode(path.read_bytes()), path.parent))
    # Digest-bearing source descriptors can nest in config and sidecar
    # documents. Generated bundle locators have a different field name.
    while documents:
        item, parent = documents.pop()
        if isinstance(item, dict):
            if isinstance(item.get('path'), str) and isinstance(item.get('sha256'), str):
                path = resolve(item['path'], parent)
                raw = path.read_bytes()
                if digest(raw) != item['sha256']:
                    raise ValueError(f'staged descriptor SHA-256 mismatch: {item["path"]}')
                if path.suffix == '.json' and path not in visited:
                    visited.add(path)
                    documents.append((decode(raw), path.parent))
            documents.extend((value, parent) for value in item.values())
        elif isinstance(item, list):
            documents.extend((value, parent) for value in item)

    workload = data.get('workload_profile') or {}
    spec = decode(workload.get('prompt_text') or '{}') if workload.get('name') == 'align_episode' else {}
    factory = spec.get('task_factory')
    if factory == 'joulewise.align.apple.pilot:offline_shade_task' or 'shade' in str(workload.get('name', '')).casefold():
        shade_dependency(spec)


@contextmanager
def consumer_environment(environment, cwd):
    """Run consumer checks with the chain's variables and working directory."""
    from joulewise.b5 import chain

    saved, previous = dict(os.environ), os.getcwd()
    try:
        os.environ.clear()
        os.environ.update(chain.apply_c1_environment(environment, saved))
        os.chdir(cwd)
        yield
    finally:
        os.chdir(previous)
        os.environ.clear()
        os.environ.update(saved)


def consumer_check(consumer, call):
    """Report a consumer's own refusal as a C1 preflight refusal."""
    from joulewise.calibration_exits import RefusalCode
    from joulewise.calibration_ledger import CalibrationLedgerError

    try:
        result = call()
    except CalibrationLedgerError as exc:
        code = exc.code.value if exc.code else 'refused'
        raise ValueError(f'C1 {consumer} refuses: {code}') from exc
    if isinstance(result, tuple) and result and isinstance(result[0], RefusalCode):
        raise ValueError(f'C1 {consumer} refuses: {result[0].value}')
    return result


def check_selections(view, tree, night, pin, *, c1_inputs, starting=True):
    """Run the consumers' own parsers and pre-host checks on the rendered chain.

    The checks run with the variables and working directory that the rendered
    chain gives its consumers, never the caller's environment.
    """
    from joulewise.b5 import chain

    hazard = night['hazard_window']
    if hazard['pack']['pack_root'] != str(view.root / PACK):
        raise ValueError('prepared pack is outside its C1 launch location')
    bindings = hazard['bindings']
    if Path(bindings['repo_root']) != view.root:
        raise ValueError('prepared repo_root binding differs')
    # O2a: a ledger pointer in the caller's shell must name the one live file.
    # The chain replaces it, so this check only refuses; it selects nothing.
    if launch_ledger := os.environ.get('CALIBRATION_LEDGER'):
        check_ledger(view.locate(launch_ledger), pin, starting=starting)
    stages = chain.stage_plan(tree, c1=True)
    environment, launches = chain.c1_chain_environment(
        stages=stages, bindings=bindings, tree=tree, measurement_root=view.root,
        plan_id=night['plan_id'], c1_inputs=c1_inputs)
    with consumer_environment(environment, view.root):
        return _check_consumers(view, tree, stages, launches, bindings, pin, starting=starting)


# The HAZARD reservation's identity vectors are measured on the host at launch.
MEASURED_AT_LAUNCH = 'measured on the host at launch'


def _check_consumers(view, tree, stages, launches, bindings, pin, *, starting):
    from joulewise import calibration_ledger as ledger
    from joulewise.b5 import chain
    from scripts import reserve_calibration_window_bracket as reservation, run_campaign as runner
    from scripts import validate_powermetrics_fiducial as fiducial

    default_ledger = view.root / LEDGER
    # The name used by the chain writer and all reader spellings must select
    # the same physical file, even if an alternate file has identical bytes.
    for candidate in (default_ledger, bindings['ledger_path'], os.environ['CALIBRATION_LEDGER']):
        check_ledger(view.locate(candidate), pin, starting=starting)
    selections = {}
    generated_bound = None

    def check_order(manifest_path, args):
        directory = view.root / Path(manifest_path).parent
        resolved = view.locate(directory, directory=True)
        # Keep the bound-file decoder's duplicate-key check and use the
        # campaign's own directory selection and manifest validation.
        decode(view.locate(manifest_path).read_bytes())
        order, _ = runner.load_order_entries(directory)
        for entry in order:
            if '/' in key(entry.config):
                raise ValueError(f'invalid dispatched config name: {entry.config}')
        analysis = directory / runner.ANALYSIS_MANIFEST_NAME
        if analysis.is_file():
            data = decode(view.locate(analysis).read_bytes())
            if data.get('schema_version') == runner.AXI_MANIFEST_SCHEMA_VERSION:
                raise ValueError('C1 dispatch must use its sealed order manifest')
            config_references(data, analysis, view, runner)
        manifest = runner.load_analysis_manifest(directory)
        if manifest is not None and not manifest.valid:
            raise ValueError('C1 campaign analysis manifest validation failed before execution')
        configs = runner.apply_order_manifest(runner.discover_configs(directory), order)
        for config in configs:
            raw = view.locate(config).read_bytes()
            config_references(decode(raw), config, view, runner)
        scope = next(root for root in view.roots.allowed if resolved.is_relative_to(root))
        if len(resolved.relative_to(scope).parts) < runner.MAX_ANALYSIS_MANIFEST_V3_ANCESTOR_DEPTH:
            raise ValueError('campaign ancestor lookup would leave the verified roots')
        _, marker = runner._reachable_analysis_manifest_v3(directory)
        if marker is not None:
            config_references(decode(marker.read_bytes()), marker, view, runner)
        runner.resolve_prospective_analysis_manifest_v3(directory)
        # The runner's own pre-launch gates on the dispatched configs.
        gate = runner.config_warning_gate(configs, acknowledge=args.ack_config_warnings, mode='campaign')
        if gate['details']['errors'] or gate['status'] == 'fail':
            raise ValueError(f"C1 campaign config gate refuses: {gate['summary']}")
        items = runner.read_config_infos(configs, runner.order_entry_by_config(order))
        if errors := [item.message for item in items if isinstance(item, runner.ConfigError)]:
            raise ValueError(f'C1 campaign config refuses: {errors[0]}')
        if (duplicate := runner.duplicate_run_id_error(items)) is not None:
            raise ValueError(f'C1 campaign config refuses: {duplicate}')

    for stage in stages:
        if not stage.in_chain:
            # Desk commands are not emitted on the measuring chain.
            for command in stage.commands:
                for arg in command.arguments:
                    chain.bind_argument(arg, bindings, tree, view.root)
            continue
        launch = launches[stage.stage_id]
        view.locate(launch.argv[1])
        args = launch.args
        if stage.kind == 'bracket_reservation':
            if args.session_kind != 'bracket' or args.allow_uncommitted_pin_for_test or args.test_writer_crash_authorization:
                raise ValueError('C1 reservation requires the ordinary bracket')
            selections['ledger'] = check_ledger(view.locate(args.ledger), pin, starting=starting)
            selections['head_pin'] = view.locate(args.head_pin)
            selections['session_kind'] = args.session_kind
            for path in (args.plan, args.identity_epoch_json, args.t1_bindings_json):
                view.locate(path)
            if view.locate(args.plan) != view.locate(view.root / PACK / 'collection_plan.json'):
                raise ValueError('reservation selects a different C1 collection plan')
            if not args.execute or args.verify_only:
                # Without --execute the reservation validates and exits 0 without
                # reserving; the capture then finds no session.
                raise ValueError('C1 reservation must append its session (--execute)')
            # The reservation's own gates on its prepared inputs, before any host work.
            consumer_check('reservation', lambda: runtime_ledger(args.ledger, starting=True))
            consumer_check('reservation', lambda: ledger.CustodyDeadline(
                args.custody_budget_s, args.custody_deadline_epoch_s, telemetry_stream=None))
            consumer_check('reservation', lambda: reservation.verify_frozen_plan(
                args.plan, plan_id=args.plan_id, plan_sha256=args.plan_sha256))
            # The HAZARD reservation measures both identity vectors on the host
            # at launch. Each field is a stand-in here; the validator judges
            # every prepared input: session, runs root, slots and custody.
            epoch = dict.fromkeys(ledger.IDENTITY_EPOCH_FIELDS, MEASURED_AT_LAUNCH)
            t1 = dict.fromkeys(ledger.T1_FIELDS, MEASURED_AT_LAUNCH)
            consumer_check('reservation', lambda: reservation.reservation_inputs(args, epoch, t1))
        elif stage.kind == 'calibration_capture':
            if args.slot != stage.slot:
                raise ValueError('C1 capture resolved to the wrong slot')
            if args.rederive_from is not None or args.output is not None:
                raise ValueError('C1 capture must be a live bracket capture')
            check_ledger(view.locate(args.ledger), pin, starting=starting)
            view.locate(args.head_pin)
            for field in ('identity_epoch_json', 't1_bindings_json', 'plan',
                          'identity_epoch_json_for_test', 'battery_probe_fixture_for_test',
                          'test_writer_crash_authorization'):
                if value := getattr(args, field, None):
                    view.locate(value)
            # The capture writer's own argument gates. Launch lineage, the
            # reserved session and the host identity exist only after launch.
            consumer_check('capture', lambda: runtime_ledger(args.ledger))
            if (error := fiducial._capture_fixture_error(args)) is not None:
                raise ValueError(f'C1 capture refuses: {error}')
            consumer_check('capture', lambda: ledger.CustodyDeadline(
                args.custody_budget_s, args.custody_deadline_epoch_s, telemetry_stream=None))
            consumer_check('capture', lambda: fiducial._capture_mode_refusal(args))
            consumer_check('capture', lambda: fiducial._live_capture_refusal(args))
        else:
            check_ledger(view.locate(args.calibration_ledger), pin, starting=starting)
            view.locate(args.head_pin)
            _, runs_binding = chain.c1_dispatch_selection(stage, tree)
            if view.root / args.runs_dir != view.root / bindings[runs_binding]:
                raise ValueError('C1 campaign resolves to a different runs directory')
            if stage.kind == 'bound_derivation':
                selections['derivation'] = view.locate(args.derive_neg8_drift_bound)
                generated_bound = view.root / args.neg8_drift_bound_output
                if '..' in generated_bound.parts or not generated_bound.is_absolute():
                    raise ValueError('invalid same-attempt bound output')
                config_references(decode(selections['derivation'].read_bytes()),
                                  selections['derivation'], view, runner)
                # Corpus bundle names describe same-attempt products.
                manifest = decode(selections['derivation'].read_bytes())
                for member in manifest['members']:
                    name = member['bundle_path']
                    key(name)
            else:
                # A shakedown gate requires --backup, which C1 refuses, so the
                # runner would refuse that stage before collection.
                if (args.cli_cmd or args.backup is not None or args.check_prompt_hashes
                        or args.whole_window_verdict or args.record_supersession
                        or args.shakedown_gate is not None):
                    raise ValueError('unsupported C1 campaign mode')
                selections['policy'] = view.locate(args.campaign_policy)
                # The runner's own loaders on the exact bytes it will read.
                runner.load_campaign_policy(args.campaign_policy)
                runner._require_external_campaign_log(
                    Path(args.log) if args.log else Path(args.runs_dir) / 'campaign_log.jsonl')
                for field in ('waivers', 'environment_override', 'salvage_closure',
                              'window_membership_binding', 'bracket_session_binding'):
                    if value := getattr(args, field, None):
                        view.locate(value)
                runner.load_waivers(args.waivers)
                if args.neg8_drift_bound and view.root / args.neg8_drift_bound != generated_bound:
                    view.locate(args.neg8_drift_bound)
                    runner.load_neg8_drift_bound_artifact(args.neg8_drift_bound)
                if args.instrument_calibration_dir:
                    selected = view.root / args.instrument_calibration_dir
                    if selected != Path(bindings['pre_calibration_dir']):
                        view.locate(selected, directory=True)
                check_order(Path(args.config_dir) / 'order_manifest.json', args)
                for path in (stage.spare_sets or {}).values():
                    check_order(path, args)
    return selections


def execution_inputs(handoff, ledger):
    names = ('git', 'repo', 'stage', 'view', 'execution_commit', 'cache_home')
    return {**{name: handoff[name] for name in names if name in handoff}, 'ledger': ledger}


def verify_chain(view, handoff, ledger, tree, tree_sha256, night):
    """Compare the staged chain to the actual renderer and prepared bindings."""
    from joulewise.b5 import chain

    hazard = night['hazard_window']
    runbook = view.locate(chain.RUNBOOK_RELATIVE).read_text(encoding='utf-8')
    expected = chain.render_chain(
        tree=tree, tree_sha256=tree_sha256, stages=chain.stage_plan(tree, c1=True),
        bindings=hazard['bindings'], measurement_root=view.root, pack_root=view.root / PACK,
        plan_id=night['plan_id'], runbook_text=runbook, settle_s=hazard['settle_s'],
        c1_inputs=execution_inputs(handoff, ledger))
    script = view.locate(night['chain_path'])
    sidecar = view.locate(night['chain_sha256_path'])
    if script.read_bytes() != expected or sidecar.read_bytes() != chain.sidecar_bytes(expected, script.name):
        raise ValueError('prepared chain differs from the resolved C1 dispatch')


def prepared_closure(authority, verified_roots, handoff, read):
    """Derive the inventory from prepare's declaration and check required inputs."""
    view = verify_launch_view(verified_roots, handoff['view'],
                              runtime=handoff.get('runtime'), git_link=handoff.get('git_link'))
    state, night = load_prepared(view, read)
    pins = declared_pins(verified_roots.repo, verified_roots.stage)
    ledger = ledger_pin(verified_roots, view.locate(view.root / LEDGER), pins)
    tree_raw = read(PACK / 'plan_tree.json')
    expected = f'{digest(tree_raw)}  plan_tree.json\n'.encode()
    if read(PACK / 'plan_tree.sha256') != expected:
        raise ValueError('staged plan tree sidecar differs')
    tree = decode(tree_raw)
    selections = check_selections(view, tree, night, ledger, c1_inputs=execution_inputs(handoff, ledger))
    verify_chain(view, handoff, ledger, tree, digest(tree_raw), night)
    closure = {'schema': SCHEMA, 'repo': tree_identity(authority, handoff['execution_commit']),
               'stage_files': pins, 'ledger': ledger}
    return closure, state, night, tree, view, selections


def finalize(authority, handoff):
    """Read only declared outputs when finalizing an attempt's packet."""
    roots = Roots(handoff['repo'], handoff['stage'])
    verify_repo(authority, roots, tree_identity(authority, handoff['execution_commit']))
    pins = declared_pins(roots.repo, roots.stage)
    prepared = VerifiedView(roots, {}, '', pins)
    return prepared_closure(authority, roots, handoff, prepared.stage_read)[0]


def runtime_input_context():
    """The prepared chain carries the already verified attempt context."""
    return decode(raw) if (raw := os.environ.get('JOULEWISE_C1_INPUTS')) else None


def runtime_ledger(path, *, starting=False):
    context = runtime_input_context()
    return check_ledger(path, context['ledger'], starting=starting) if context else Path(path)


def artifact_set_digest_at(root, commit):
    """The same digest computed from the committed bytes of ``commit`` (the last desk-passed code state)."""
    blobs = _committed_bytes(root, commit, list(ARTIFACTS))
    return artifact_set_digest_from(lambda path: blobs.get(path))


def artifact_hashes_at(root, commit):
    """Expected staged artifact bytes, including required absences."""
    return {path: digest(raw) if raw is not None else None
            for path, raw in _committed_bytes(root, commit, list(ARTIFACTS)).items()}


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


R1_EXECUTED_SOURCES = (
    "scripts/align_r1_rehearsal.py", "scripts/align_r1_runtime.py",
    "joulewise/align/apple/r1_runtime.py", "joulewise/align/apple/r1_runtime_contract.py",
    "joulewise/align/apple/smc_enumeration.py",
    "joulewise/align/apple/thermal_gates.py", "configs/align/v4/r1_runtime.json",
    "joulewise/align/apple/r1_phase_table.py", "joulewise/align/apple/workload.py",
    "joulewise/align/apple/thermal.py",
)


def verify_r1_executed_sources(root, slots):
    """RL-61/72/78/84 condition 13. Compare to the night's full commit."""
    commit = slots.get("executed_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("R1 slots require executed_commit (condition 13)")
    blobs = _committed_bytes(root, commit, R1_EXECUTED_SOURCES)
    for path in R1_EXECUTED_SOURCES:
        try:
            raw = _local(root, path).read_bytes()
        except OSError as error:
            raise ValueError(f"R1 executed source missing: {path}") from error
        if blobs.get(path) is None or raw != blobs[path]:
            raise ValueError(f"R1 executed source differs (condition 13): {path}")
    return commit


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
    verify_r1_executed_sources(root, json.loads(_local(root, REGISTRATION+'r1_slots.json').read_bytes()))
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
        v4_u3.validate(v4_u3.canonical(bar))
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
