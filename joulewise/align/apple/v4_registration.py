"""V4 registration evidence. Pure stdlib; no probes, data discovery or weights."""
from __future__ import annotations

import functools
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess

REGISTRATION = 'configs/campaigns/align_v4/registration/'
RECEIPT_SCHEMA = 'joulewise.align_v4.registration_receipt.v1'
WP19_SCHEMA = 'joulewise.align_v4.wp19_identity.v1'
RULINGS = (4, 5, 6, 9, 11, 15, 17, 18, 20)
_NAMED_ARTIFACTS = (
    'docs/align/pilot_protocol_v4.md', 'docs/align/v4/DEVIATIONS.md',
    'docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md',
    'scripts/align_w1_budget_procedure.py', 'joulewise/align/apple/km003c.py',
    'scripts/validate_align_v4_w1_plan.py', 'joulewise/align/apple/pilot_analysis.py',
    'joulewise/align/energy_residual.py',
    'scripts/align_v4_kit.py', 'scripts/align_v4_session.py',
    'scripts/align_v4_thermal_desk.py', 'scripts/align_pilot_session.py',
    'scripts/align_v4_u3_bar.py', 'scripts/align_v4_wp19.py', 'scripts/align_v4_offloads.py',
    'joulewise/align/apple/v4_registration.py', 'joulewise/align/apple/v4_estimands.py',
    'joulewise/align/apple/thermal_desk.py', 'joulewise/align/apple/thermal_gates.py',
    'joulewise/align/apple/endpoint.py', 'joulewise/align/apple/workload.py',
    'scripts/run_night.py', REGISTRATION+'inputs.json', REGISTRATION+'r1_slots.json',
    REGISTRATION+'identity_pins.json', REGISTRATION+'model_artifact_inventory.json',
    REGISTRATION+'local_file_verification.json',
    REGISTRATION+'w1_plan.json', REGISTRATION+'u3_bar.json', REGISTRATION+'wp19_receipt.json',
    REGISTRATION+'r1_soak_reference.json',
    'configs/campaigns/align_v4/plan_tree.json', 'configs/campaigns/align_v4/collection_plan.json',
)


# Static import closure (stdlib ``ast``; module- and function-level imports,
# parent packages included) of the episode path and the W1/D night entry points
# (endpoint.py, scripts/run_night.py, scripts/align_v4_session.py), restricted to
# joulewise/. R11 lead ruling 3 (Sol2 F01): the exact-candidate receipt binds the
# executed code, not a hand-picked subset. tests/align/test_v4_executed_closure.py
# recomputes this closure and fails if it is not a subset of ARTIFACTS.
# Not seen by a static walk: importlib string imports and third-party modules.
EXECUTED_CLOSURE = (
    'joulewise/align/apple/v4_cadence.py',
    'joulewise/align/apple/prompt_cache.py',
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
    'joulewise/align/apple/r1_runtime.py',
    'joulewise/align/apple/r1_runtime_contract.py',
    'joulewise/align/apple/registry_select.py',
    'joulewise/align/apple/sampler.py',
    'joulewise/align/apple/sampling.py',
    'joulewise/align/apple/smc_enumeration.py',
    'joulewise/align/apple/smc_reader.py',
    'joulewise/align/apple/stop_precedence.py',
    'joulewise/align/apple/thermal.py',
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
    'joulewise/b6/calibration.py',
    'joulewise/b6/capture_list.py',
    'joulewise/b6/capture_screen.py',
    'joulewise/b6/code_check.py',
    'joulewise/b6/compose.py',
    'joulewise/b6/courier.py',
    'joulewise/b6/desk_identity.py',
    'joulewise/b6/desk_lane.py',
    'joulewise/b6/driver_lane.py',
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
    'joulewise/flags/__init__.py',
    'joulewise/flags/catalog.py',
    'joulewise/flags/core.py',
    'joulewise/flags/exclusions.py',
    'joulewise/flags/schema.py',
    'joulewise/flags/sink.py',
    'joulewise/floor_extraction.py',
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
)
ARTIFACTS = _NAMED_ARTIFACTS + tuple(p for p in EXECUTED_CLOSURE if p not in _NAMED_ARTIFACTS)


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
    for path, expected in bindings.items():
        try:
            raw = _local(root, path).read_bytes()
        except OSError as exc:
            raise ValueError(f'registration_receipt missing committed artifact: {path}') from exc
        if pinned.get(path) is None:
            raise ValueError(f'registration_receipt missing committed artifact: {path}')
        if digest(raw) != expected or digest(pinned[path]) != expected:
            raise ValueError(f'registration_receipt digest drift: {path}')
    return receipt


def require_registration(root):
    path = REGISTRATION+'registration_receipt.json'
    try:
        receipt = json.loads(_local(root, path).read_bytes())
    except (OSError, ValueError) as exc:
        raise ValueError('registration_receipt.json missing or unreadable; W1 is not registered') from exc
    validate_receipt(receipt, root)
    bar = json.loads(_local(root, REGISTRATION+'u3_bar.json').read_bytes())
    validate_u3(bar, root=root)
    wp19 = json.loads(_local(root, REGISTRATION+'wp19_receipt.json').read_bytes())
    validate_wp19(wp19)
    return receipt


# ---------------------------------------------------------------------------
# U3 (R03; RUN_STATE 212 R11-2): a frozen derivation, never an installed constant.
#
# Procedure U3_PROCEDURE (docs/align/v4/W1-BLOCKERS-opus.md section 1):
#   unit      r = (E_late - E_early) / mean(E_early, E_late) per token-identical,
#             within-session replay pair whose ordinals are >= 3 apart;
#   scale     s0 = sqrt(mean(r^2)), the RMS about ZERO with n degrees of freedom:
#             mean drift between early and late replays inflates the scale; no
#             fitted drift is ever subtracted or credited;
#   quantile  q solves E_U[1 - (1 - P(|Z| > q U))^N] = beta, U^2 ~ chi2_n / n:
#             the probability, under the fitted model and including the
#             small-sample uncertainty of s0 shared by every later test, that ANY
#             of the series' N registered pair tests fails falsely is beta;
#   bar       a pair fails U3 iff |E_b - E_a| > (q s0) mean(E_a, E_b).
# N and beta are lead-frozen parameters. A bar is valid only for the source
# model family; another family needs its own replay evidence (transfer pairs,
# e.g. R1's D_spam a/b), which can refute but never qualify the transfer.
# validate_u3 recomputes everything from the embedded inputs, so a hand-typed
# multiplier, k=3, 2.576 or a fitted-normal guarantee cannot pass.
# ---------------------------------------------------------------------------
U3_SCHEMA = 'joulewise.align_v4.u3_bar.v2'
U3_PROCEDURE = 'u3.zero_centred_rms.series_predictive_t.v1'
U3_MIN_SEPARATION = 3
U3_PARAMETERS = ('series_pair_tests', 'series_false_fail_budget', 'min_pairs', 'oc_seed', 'oc_reps')
U3_N_GRID = (5, 8, 12, 20, 40)
_U3_DERIVED_KEYS = ('schema', 'procedure', 'parameters', 'source_sha256', 'pairs', 'transfer_pairs',
                    'synthetic', 'source_family', 'n', 'df', 'signed_relative_differences',
                    'mean_relative_difference', 'sample_sd_relative', 'rms_relative_scale',
                    'series_quantile_q', 'per_pair_false_fail', 'series_false_fail', 'relative_bar',
                    'transfer', 'scope', 'operating_characteristics', 'limitations')


def _u3_parameters(parameters):
    p = parameters if isinstance(parameters, dict) else {}
    if (set(p) != set(U3_PARAMETERS)
            or type(p['series_pair_tests']) is not int or p['series_pair_tests'] < 1
            or type(p['series_false_fail_budget']) is not float
            or not 0 < p['series_false_fail_budget'] < .5
            or type(p['min_pairs']) is not int or p['min_pairs'] < 3
            or type(p['oc_seed']) is not int or type(p['oc_reps']) is not int or p['oc_reps'] < 100):
        raise ValueError('U3 requires lead-frozen parameters: series_pair_tests (int>=1), '
                         'series_false_fail_budget (float in (0,.5)), min_pairs (int>=3), oc_seed, oc_reps>=100')
    return p


def _u3_relative(pair, *, transfer):
    ordinals = pair.get('ordinals') if isinstance(pair, dict) else None
    values = pair.get('energies_j') if isinstance(pair, dict) else None
    if (not isinstance(pair, dict) or pair.get('token_identical') is not True
            or not isinstance(ordinals, list) or len(ordinals) != 2 or any(type(v) is not int for v in ordinals)
            or ordinals[1] - ordinals[0] < (1 if transfer else U3_MIN_SEPARATION)
            or not isinstance(values, list) or len(values) != 2
            or any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in values)
            or not isinstance(pair.get('session'), str) or not pair['session']
            or not isinstance(pair.get('family'), str) or not pair['family']):
        raise ValueError('U3 requires separated-ordinal, within-session token-identical positive-energy pairs '
                         'with session and model family' if not transfer else
                         'U3 transfer pairs must be ordered, token-identical, positive-energy replays with family')
    return (values[1] - values[0]) / statistics.fmean(values)


def _chi_expect(n, fn, steps=2000):
    """E[fn(U)] for U = sqrt(X/n), X ~ chi-square(n), n >= 3 (composite Simpson)."""
    hi = n + 14 * math.sqrt(2 * n) + 40
    h = hi / steps
    log_c = -(n / 2) * math.log(2) - math.lgamma(n / 2)
    total = 0.0
    for i in range(1, steps + 1):
        x = i * h
        weight = 1 if i == steps else 4 if i % 2 else 2
        total += weight * math.exp(log_c + (n / 2 - 1) * math.log(x) - x / 2) * fn(math.sqrt(x / n))
    return total * h / 3


def _u3_tail(z):
    return math.erfc(z / math.sqrt(2))


@functools.lru_cache(maxsize=4096)
def u3_series_false_fail(q, n, tests):
    return _chi_expect(n, lambda u: -math.expm1(tests * math.log1p(-min(_u3_tail(q * u), 1 - 1e-16))))


@functools.lru_cache(maxsize=4096)
def u3_per_pair_false_fail(q, n):
    """P(|T_n| > q): the exact predictive false-fail of one new null pair."""
    return _chi_expect(n, lambda u: _u3_tail(q * u))


@functools.lru_cache(maxsize=256)
def u3_quantile(n, tests, beta):
    lo, hi = 0.0, 200.0
    for _ in range(64):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if u3_series_false_fail(mid, n, tests) > beta else (lo, mid)
    return hi


def u3_operating_characteristics(parameters, n):
    """Seeded Monte Carlo OC of the frozen rule; depends on (parameters, n) only, never on data.

    Every scenario re-derives s0 from n fresh pilot-like pairs and applies the
    bar to the series' N future pair tests. Rates are fractions of oc_reps.
    """
    import random
    p = _u3_parameters(parameters)
    tests, beta, reps = p['series_pair_tests'], p['series_false_fail_budget'], p['oc_reps']
    q = u3_quantile(n, tests, beta)
    rng = random.Random(p['oc_seed'])
    gauss = rng.gauss

    def t4():
        return gauss(0, 1) / math.sqrt(sum(gauss(0, 1) ** 2 for _ in range(4)) / 4) / math.sqrt(2)

    def clustered(count, size, rho):
        out = []
        while len(out) < count:
            shared = gauss(0, 1) * math.sqrt(rho)
            out.extend(shared + gauss(0, 1) * math.sqrt(1 - rho) for _ in range(min(size, count - len(out))))
        return out

    def w1_clustered(count, rho):
        # W1 shape: one model-window of up to 4 pairs (30B), then singletons (D windows).
        head = clustered(min(4, count), 4, rho)
        return head + [gauss(0, 1) for _ in range(count - len(head))]

    scenarios = {
        'null_normal': (lambda: [gauss(0, 1) for _ in range(n)], lambda: [gauss(0, 1) for _ in range(tests)]),
        'drift_0.5_sigma': (lambda: [gauss(.5, 1) for _ in range(n)], lambda: [gauss(.5, 1) for _ in range(tests)]),
        'drift_1.0_sigma': (lambda: [gauss(1, 1) for _ in range(n)], lambda: [gauss(1, 1) for _ in range(tests)]),
        'heavy_tail_t4': (lambda: [t4() for _ in range(n)], lambda: [t4() for _ in range(tests)]),
        'dependence_rho_0.3': (lambda: clustered(n, 3, .3), lambda: w1_clustered(tests, .3)),
        'transfer_scale_0.5': (lambda: [gauss(0, 1) for _ in range(n)], lambda: [gauss(0, .5) for _ in range(tests)]),
        'transfer_scale_1.5': (lambda: [gauss(0, 1) for _ in range(n)], lambda: [gauss(0, 1.5) for _ in range(tests)]),
        'transfer_scale_2.0': (lambda: [gauss(0, 1) for _ in range(n)], lambda: [gauss(0, 2) for _ in range(tests)]),
    }
    oc = {'q': q, 'n': n, 'series_pair_tests': tests, 'reps': reps,
          'exact_series_false_fail': u3_series_false_fail(q, n, tests),
          'exact_per_pair_false_fail': u3_per_pair_false_fail(q, n),
          'series_false_fail': {}, 'per_pair_detection': {},
          'q_by_n': {str(k): u3_quantile(k, tests, beta) for k in sorted({*U3_N_GRID, n})}}
    for name, (derive, future) in scenarios.items():
        hits = 0
        for _ in range(reps):
            s0 = math.sqrt(math.fsum(r * r for r in derive()) / n)
            hits += any(abs(r) > q * s0 for r in future())
        oc['series_false_fail'][name] = hits / reps
    for shift in (3, 5, 8):
        hits = 0
        for _ in range(reps):
            s0 = math.sqrt(math.fsum(gauss(0, 1) ** 2 for _ in range(n)) / n)
            hits += abs(gauss(shift, 1)) > q * s0
        oc['per_pair_detection'][f'shift_{shift}_sigma'] = hits / reps
    return oc


def derive_u3(pairs, source_sha256, *, parameters, transfer_pairs=(), synthetic=False):
    """Frozen U3 derivation (unsigned). Inputs are explicit exports; nothing is discovered."""
    p = _u3_parameters(parameters)
    if not isinstance(source_sha256, dict) or not source_sha256 or not all(is_digest(v) for v in source_sha256.values()):
        raise ValueError('U3 requires input sha256 digests')
    pairs, transfer_pairs = list(pairs), list(transfer_pairs)
    relative, seen = [], set()
    for pair in pairs:
        relative.append(_u3_relative(pair, transfer=False))
        key = (pair['session'], *pair['ordinals'])
        if key in seen:
            raise ValueError('duplicate U3 replay pair')
        seen.add(key)
    families = {pair['family'] for pair in pairs}
    if len(families) != 1:
        raise ValueError('U3 derivation pairs must come from exactly one model family')
    n = len(relative)
    if n < p['min_pairs']:
        raise ValueError(f'U3 requires at least min_pairs={p["min_pairs"]} eligible replay pairs, got {n}')
    s0 = math.sqrt(math.fsum(r * r for r in relative) / n)
    if not s0 > 0:
        raise ValueError('U3 scale is degenerate (all replay differences zero)')
    q = u3_quantile(n, p['series_pair_tests'], p['series_false_fail_budget'])
    bar = q * s0
    source = families.pop()
    transfer = {}
    for pair in transfer_pairs:
        r = _u3_relative(pair, transfer=True)
        if pair['family'] == source:
            raise ValueError('U3 transfer pairs must be from another model family')
        row = transfer.setdefault(pair['family'], {'pairs': [], 'status': 'not_refuted'})
        row['pairs'].append({'session': pair['session'], 'ordinals': pair['ordinals'], 'relative_difference': r,
                             'within_bar': abs(r) <= bar,
                             'predictive_tail': u3_per_pair_false_fail(abs(r) / s0, n)})
        if abs(r) > bar:
            row['status'] = 'refuted'
    return {'schema': U3_SCHEMA, 'procedure': U3_PROCEDURE, 'status': 'derived', 'parameters': p,
            'source_sha256': source_sha256, 'pairs': pairs, 'transfer_pairs': transfer_pairs,
            'synthetic': bool(synthetic), 'source_family': source, 'n': n, 'df': n,
            'signed_relative_differences': relative,
            'mean_relative_difference': statistics.fmean(relative),
            'sample_sd_relative': statistics.stdev(relative),
            'rms_relative_scale': s0, 'series_quantile_q': q,
            'per_pair_false_fail': u3_per_pair_false_fail(q, n),
            'series_false_fail': u3_series_false_fail(q, n, p['series_pair_tests']),
            'relative_bar': bar, 'transfer': transfer,
            'scope': {source: 'source', **{family: row['status'] for family, row in transfer.items()}},
            'operating_characteristics': u3_operating_characteristics(p, n),
            'limitations': [
                'Model: exchangeable zero-centred normal replay differences; drift inflates s0 and is never credited.',
                'False-fail rates are conditional on that model; OC sensitivities show drift, heavy-tail, '
                'dependence and scale-transfer departures.',
                'A transfer pair can refute, never qualify, use of the bar on another model family.',
                'One bar for the whole registered series; no re-derivation from windows it judges.']}


def sign_u3(bar, *, lead_signature, gate):
    """Attach the lead signature and the independent gate receipt; validate the result."""
    signed = {**bar, 'status': 'registered', 'lead_signature': lead_signature, 'independent_gate': gate}
    return validate_u3(signed, allow_synthetic=bool(bar.get('synthetic')))


def _close(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return (type(a) in (int, float) and type(b) in (int, float)
                and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_close(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_close(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b


_U3_VALIDATED = {}


def validate_u3(bar, *, root=None, allow_synthetic=False):
    """Admit only a signed bar whose every derived value recomputes from its embedded inputs.

    A pending/v1/historical k=3 artifact, an unsigned derivation, a synthetic
    bar (unless the caller is a dry run), a missing independent gate or any
    edited number refuses. ``root`` also binds the gate report bytes.
    """
    from scripts.align_v4_kit import valid_lead_signature
    if not isinstance(bar, dict) or bar.get('schema') != U3_SCHEMA or bar.get('procedure') != U3_PROCEDURE:
        raise ValueError('U3 PENDING frozen predictive derivation and operating-characteristic sensitivity '
                         '(R11/R03): u3_bar.json is not a v2 derivation')
    if bar.get('status') != 'registered':
        raise ValueError('U3 PENDING: u3_bar.json is derived but not registered (lead signature + gate)')
    if bar.get('synthetic') is not False and not allow_synthetic:
        raise ValueError('U3 synthetic bar refused outside a dry run')
    if not valid_lead_signature(bar.get('lead_signature')):
        raise ValueError('U3 bar requires a lead signature')
    gate = bar.get('independent_gate')
    if (not isinstance(gate, dict) or gate.get('verdict') != 'ADMIT' or not is_digest(gate.get('sha256'))
            or not isinstance(gate.get('path'), str) or not gate['path'].startswith('docs/align/v4/')):
        raise ValueError('U3 bar requires an ADMIT independent gate receipt under docs/align/v4/')
    if root is not None:
        try:
            raw = _local(root, gate['path']).read_bytes()
        except OSError as exc:
            raise ValueError('U3 gate report missing') from exc
        if digest(raw) != gate['sha256']:
            raise ValueError('U3 gate report digest drift')
    key = json.dumps({k: bar.get(k) for k in _U3_DERIVED_KEYS}, sort_keys=True, allow_nan=False)
    if key not in _U3_VALIDATED:
        try:
            expected = derive_u3(bar.get('pairs') or [], bar.get('source_sha256'), parameters=bar.get('parameters'),
                                 transfer_pairs=bar.get('transfer_pairs') or [],
                                 synthetic=bar.get('synthetic') is True)
        except (TypeError, KeyError, AttributeError) as exc:
            raise ValueError('U3 bar inputs malformed') from exc
        drift = [k for k in _U3_DERIVED_KEYS if k != 'operating_characteristics' and not _close(bar.get(k), expected[k])]
        oc, ref = bar.get('operating_characteristics'), expected['operating_characteristics']
        tolerance = 3 / bar['parameters']['oc_reps']
        if not (isinstance(oc, dict) and set(oc) == set(ref) and all(
                _close(oc[k], ref[k]) if k not in ('series_false_fail', 'per_pair_detection') else
                isinstance(oc[k], dict) and set(oc[k]) == set(ref[k])
                and all(type(oc[k][s]) in (int, float) and abs(oc[k][s] - ref[k][s]) <= tolerance for s in ref[k])
                for k in ref)):
            drift.append('operating_characteristics')
        if drift:
            raise ValueError(f'U3 bar does not recompute from its inputs: {", ".join(drift)}')
        _U3_VALIDATED[key] = True
    return bar


def u3_family(model, scope):
    """Model string -> the bar's family key; None when unmapped (the pair is then inconclusive)."""
    if model in scope:
        return model
    text = str(model or '').lower()
    return '30B' if '30b' in text else 'D' if ('qwen3.8' in text or '27b' in text) else None


def u3_margin(mean_energy_j, bar, *, model=None):
    validate_u3(bar)
    family = u3_family(model, bar['scope'])
    status = bar['scope'].get(family)
    if status not in ('source', 'not_refuted'):
        raise ValueError(f'U3 bar does not apply to model {model!r} (family {family}: {status or "no transfer evidence"})')
    return bar['relative_bar'] * mean_energy_j


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
        reasons.append('completed top-up evidence missing: require --topup-completed-at and --topup-source')
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


# Chair ruling 4 / R02 battery window rule (docs/align/v4/W1-BLOCKERS-opus.md section 2).
# B = battery.member_span (charging or AC loss read inside the member span):
# a member exclusion. Missing or ambiguous battery evidence (battery.unmeasured,
# battery.accumulator_excursion) is a POSSIBLE B. Tolerance mirrors U1's
# ">=2 X1-X4 members per model-window fails": with B the known B members and U
# the possible ones, a model-window passes iff B+U <= 1 (true under every
# resolution of U), fails iff B >= 2, and is otherwise unavailable. Battery
# assist (discharge on AC) is printed only: v4's registered residual is GPU
# energy, and the KM003C DC-in channel is SECONDARY in v4.
B_WINDOW_TOLERANCE = 1
B_CODE = 'battery.member_span'
B_POSSIBLE_CODES = ('battery.unmeasured', 'battery.accumulator_excursion')
B_ASSIST_CODES = ('battery.assist',)
B_FAIL_CONSEQUENCE = ('battery float not maintained: B members stay excluded; the window desk fails '
                      'v4_B_bar, so no next arm (D1 after W1) until a fresh completed top-up, OBC attestation '
                      'and a lead disposition of the cause are recorded; non-B members are not removed')


def battery_window(selected):
    """One model-window's B verdict from harvest battery codes; never infers absent evidence."""
    rows, b, possible, unevaluated, assist = [], [], [], [], []
    for r in selected:
        codes = [str(c) for c in (*r.get('flags', []), *r.get('battery_codes', []))]
        rid = r.get('id')
        if any(c.startswith(B_CODE) for c in codes):
            b.append(rid)
        elif any(c.startswith(B_POSSIBLE_CODES) for c in codes):
            possible.append(rid)
        elif r.get('battery_evaluated') is not True:
            unevaluated.append(rid)
        if any(c.startswith(B_ASSIST_CODES) for c in codes):
            assist.append(rid)
        rows.append({'id': rid, **r.get('battery', {'soc_pct': None, 'charger_w': None})})
    unknown = len(possible) + len(unevaluated)
    if len(b) > B_WINDOW_TOLERANCE:
        verdict, consequence = False, B_FAIL_CONSEQUENCE
    elif len(b) + unknown <= B_WINDOW_TOLERANCE:
        verdict, consequence = True, 'B within tolerance; B members (if any) stay excluded'
    else:
        verdict, consequence = None, ('battery evidence unavailable for the window bar: '
                                      'not a pass; lead disposition required before the next arm')
    return {'B_count': len(b), 'B_members': b, 'possible_B_members': possible,
            'battery_unevaluated_members': unevaluated, 'assist_members_print_only': assist,
            'tolerance': B_WINDOW_TOLERANCE, 'bar_pass': verdict,
            'status': 'pass' if verdict else 'fail' if verdict is False else 'unavailable',
            'consequence': consequence, 'members': rows}


def desk_diagnostics(members, *, r1_soak=None):
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
    windows = {model: battery_window([r for r in members if r.get('model') == model])
               for model in {r.get('model') for r in members}}
    return {'sentinel': sentinel, 'battery_windows': windows,
            'warm_reference': v4.warm_reference_diagnostic(reference, r1_soak or {}, waits),
            'd_cohort': v4.d_configuration_assertion(d),
            'rebuilds': [{'id': r['id'], 'ordinal': r.get('ordinal'),
                          'cache_statistics': r.get('cache_statistics', {'status': 'not_recorded'})} for r in members],
            'no_rebuild_sensitivity': {'status': 'print_only', 'member_ids': [r['id'] for r in members
                if r.get('cache_statistics', {}).get('rebuilds') == 0]}}
