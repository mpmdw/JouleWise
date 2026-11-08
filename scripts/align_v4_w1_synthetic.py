#!/usr/bin/env python3
"""WP22 synthetic W1 dry run: v4 kit -> 18 member configs -> workload -> desk.

SYNTHETIC ONLY. Fake clock, fake SMC transport, fake PM status, fake native
MLX stream, synthetic SHADE-shaped task and a powermetrics-labelled synthetic
GPU rail. No model, SHADE cache, hardware sensor or network is opened. The
output is a dry-run record of where the pipeline diverges from the design
(FINAL-DESIGN 219fb1515 + Amendment 1 6eb1ff5be), never measurement data.

Usage: python3 -B scripts/align_v4_w1_synthetic.py OUTPUT_DIR [--variant kit|design-deadman]
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import align_v4_kit as kit  # noqa: E402
from tests.align import w1_synthetic as syn  # noqa: E402

NS = syn.NS
R0_SHA = hashlib.sha256(b'synthetic-r0-record').hexdigest()
I_D = 516.575
# R1 rehearsal record stand-in: frozen series AC powermode (council ruling 7)
# and the largest post-deadline tail, which binds T_dead by lead ruling L1.
# Shaped like the R1 driver's record, so the kit's evidence binding (executing
# review MEDIUM-3) is exercised; the synthetic source is admitted only because
# build_kit asks require_ready for it explicitly.
SYN_PHASES = {'G0': 60.0, 'G1': 30.0, 'H': 30.0, 'decode': 200.0, 'prefill': 60.0, 'tool': 5.0}
SYN_R1_SLOTS = {'schema': kit.R1_SLOTS_SCHEMA, 'source': kit.R1_SYNTHETIC_SOURCE,
                'ac_powermode': 0, 'slots_ac_powermode': 0,
                'thermometry': {'bar': 'pass', 'D': {'s_fast': syn.FAST, 's_slow': syn.SLOW,
                                                     'die_candidates': [syn.FAST], 'heatsink_candidates': [syn.SLOW],
                                                     'classification_sha256': hashlib.sha256(b'synthetic-r1-classification').hexdigest(),
                                                     'alias_groups': [],
                                                     'sensor_pick_changed': False}},
                'max_r1_tail_s': 30.0,
                # Lead ruling R5-4: B_D, N_chunk, S5/S6 and S7 bind the inputs below.
                'slots': {'I_D': I_D, 'B_D': 6144, 'N_chunk': 2048, 'S5_fast': 1.5, 'S5': 1.0, 'S6': 1.0, 'S7': 120.0},
                'high_power': {'verdict': 'not_adopted'}, 'u5': {'verdict': 'pass', 'c': 1.0},
                # R6-3: 8,000 tokens in 200 s of decode = step-d's 40 tok/s.
                # R6-8 (exec LOW-5): each run's duty verdict; the kit re-derives the bar.
                'deadman_budget': [{'run': name, 'g0_outcome': 'released',
                                    'phases_s': dict(SYN_PHASES, tail=tail), 'decode_tokens': 8000,
                                    'turn_decode_counts': [2000]*4, 'turn_completed': [True]*4,
                                    'admitted_turns': 4, 'x7': False, 'turn_counts_source_sha256': R0_SHA,
                                    'duty_bar': {'pass': True, 'verdict': 'pass'}}
                                   for name, tail in zip(kit.GATED_D_RUN_NAMES, (30.0, 12.0, 12.0))],
                'budget_fit_inputs': {'r_decode_tok_per_s': 40.0, 'r_decode_step_d_tok_per_s': 40.0,
                                      'turn_cap_tokens': 4096},
                'external_volumes': [{'point': 't0', 'verdict': 'PASS'}], 'inconclusive_segments': {},
                'x_g': {'status': 'measured', 'g0_outcome': 'released', 'g0_wait_s': 60.0,
                        'admitted_turns': 5, 'x7': False, 'phases_s': dict(SYN_PHASES)},
                'g0_cap_w1': {'authority': 'LEAD-RULINGS-2 R7-2, R7-12', 'r1_g0_timeout_s': 1200.0,
                              'floor_s': 600.0, 'factor': 1.25,
                              'waits_s': {**dict.fromkeys(kit.GATED_D_RUN_NAMES, 60.0), 'X_G_contrast': 60.0},
                              'censored': [], 'x_g_fallback': False, 'max_g0_s': 60.0, 'value_s': 600,
                              'rule': 'clamp(ceil(1.25 * max counted gated D and X-G G0 wait), 600, R1 g0_timeout_s)'},
                # R6-1: the duty bar ran under W1's inter-member schedule.
                'duty_bar': {'pass': True, 'verdict': 'pass',
                             'schedule': {'authority': 'LEAD-RULINGS-2 R6-1',
                                          'inter_member_idle_s': {'D': 300.0, 'X-G': 300.0}}},
                'status_note': 'SYNTHETIC_WP22_DRY_RUN'}
SYN_INPUTS = {
    'schema_version': 'joulewise.align_v4_inputs.v1',
    'status': 'SYNTHETIC_WP22_DRY_RUN',
    'WP11': {
        'identity_unit': {'model_source': kit.D_SOURCE, 'model_name': 'Qwen3.8-27B-8bit',
                          'model_revision': kit.D_REVISION,
                          'model_artifact_sha256': hashlib.sha256(b'synthetic-d-artifact').hexdigest(),
                          'stack_identity': {'synthetic': True}, 'flags': ['SYNTHETIC_WP22']},
        'artifact_inventory': {'synthetic': True, 'bytes': 1},
        'local_file_verification': {'synthetic': True},
    },
    'WP18': {'X': {'max_turns': 5, 'token_fixture_sha256': hashlib.sha256(b'X').hexdigest()},
             'Y': {'max_turns': 5, 'token_fixture_sha256': hashlib.sha256(b'Y').hexdigest()}},
    'R0': {'reasoning_effort': 'xhigh', 'record_sha256': R0_SHA},
    'R1': {'B_D': 6144, 'I_D': I_D, 'T_dead': kit.l1_t_dead(I_D, SYN_R1_SLOTS['max_r1_tail_s']),
           'thermal_policy': {'classification_sha256': SYN_R1_SLOTS['thermometry']['D']['classification_sha256'],
                              'sensors': {'s_fast': syn.FAST, 's_slow': syn.SLOW, 'fan_keys': [syn.FAN],
                                          'r0_sha256': R0_SHA},
                              'delta_fast_c': 1.5, 'delta_slow_c': 1.0, 'turn_cap_s': 120,
                              'chunk_tokens': 2048, 'g0_cap_s': 600, 'heavy': True, 'per_turn': True}},
    'WP15': {'runtime_entrypoint': ['scripts/align_r1_runtime.py', '--config', 'configs/align/v4/r1_runtime.json']},
}

# Synthetic, complete R11 contrast proof; never native evidence.
_SYN_CONTRAST = kit.w1_contrast_g0_cap(SYN_R1_SLOTS, SYN_INPUTS['WP18']['X']['max_turns'])
SYN_INPUTS['R1']['thermal_policy'].update(contrast_g0_cap_s=_SYN_CONTRAST['value_s'], contrast_fit=_SYN_CONTRAST)

# One of each injected event, on distinct members (ordinal -> event).
# Council ruling 1(g) swapped W1 ordinals 17 and 18: the replay of 5 is 17 and
# development index 93 is 18, so the collector death stays on the development D.
INJECT = {8: 'g0_timeout', 13: 'os_level_nonzero', 11: 'malformed_xml', 14: 'deadman', 18: 'collector_death'}
PAIR_GROUPS = {5: 'D-5-17', 17: 'D-5-17', 6: 'X-G', 16: 'X-G', 9: 'X-S', 13: 'X-S',
               7: 'Y-S', 15: 'Y-S', 10: 'Y-G', 12: 'Y-G'}


def build_kit(inputs, r1_slots=SYN_R1_SLOTS):
    with patch.object(kit, 'read_inputs', lambda root=kit.ROOT: deepcopy(inputs)), \
            patch.object(kit, 'read_r1_slots', lambda root=kit.ROOT: deepcopy(r1_slots)):
        kit.require_ready(deepcopy(inputs), deepcopy(r1_slots), synthetic=True)
        files = kit.build_files(kit.ROOT)
    plan = json.loads(files[kit.KIT / 'collection_plan.json'])
    configs = {m['ordinal']: json.loads(files[Path(m['config_path'])]) for m in plan['members']}
    return plan, configs, files


def mirror(root, family):
    path = root / 'models' / family
    if not path.exists():
        path.mkdir(parents=True)
        (path / 'weights.safetensors').write_bytes(b'synthetic-' + family.encode())
        (path / 'config.json').write_text(json.dumps({'model_type': family, 'max_position_embeddings': 40960,
                                                       'eos_token_id': 0}))
    return str(path)


def synthesize(config, root):
    """Replace only the model mirror and the task factory; keep every control."""
    config = deepcopy(config)
    family = config['model']['family']
    config['model']['source'] = mirror(root, family)
    spec = json.loads(config['workload_profile']['prompt_text'])
    pair = spec['task_kwargs']['task_pair']
    spec['task_factory'] = 'tests.align.w1_synthetic:make_task'
    spec['task_kwargs'] = {'task_pair': pair}
    config['workload_profile']['prompt_text'] = json.dumps(spec, sort_keys=True, separators=(',', ':'),
                                                           allow_nan=False)
    return config


def rebind(configs, capture_ordinal=5):
    """Recompute consumers' custody digest over the synthesized capture config."""
    from joulewise.schemas import BenchmarkConfig
    capture = BenchmarkConfig.from_mapping(configs[capture_ordinal])
    digest = hashlib.sha256(kit.bundle_config_bytes(capture)).hexdigest()
    for ordinal, config in configs.items():
        spec = json.loads(config['workload_profile']['prompt_text'])
        ref = (spec.get('thermal') or {}).get('window_reference')
        if ref and ref.get('role') == 'consume':
            ref['source_config_sha256'] = digest
            config['workload_profile']['prompt_text'] = json.dumps(spec, sort_keys=True, separators=(',', ':'),
                                                                   allow_nan=False)
    return digest


class Delegate:
    """Default adapter registry except a synthetic powermetrics-labelled GPU rail."""
    def __init__(self, world):
        from joulewise import adapters
        self.adapters, self.world = adapters, world

    def __getattr__(self, name):
        return getattr(self.adapters, name)

    def resolve_runtime(self, config, clock):
        return self.adapters.resolve_runtime(config, clock)

    def resolve_telemetry(self, config, clock):
        return syn.SyntheticGpuTelemetry(clock, self.world), None


def thermal_factory(world):
    from joulewise.align.apple.thermal_gates import ThermalSession
    from joulewise.align.apple.smc_reader import Reader

    def factory(policy, clock, context, status_reader=None):
        session = ThermalSession(policy, clock, context, reader=Reader(world.transport()),
                                 status_reader=world.status)
        run_id = context.run_id if context is not None else None
        world.register(session)
        original_wait, original_close = session.wait, session.close

        def wait(kind, **kwargs):
            if kind == 'G0' and run_id in world.injections.g0_hot:
                world.extra_heat_w = 80.0
                try:
                    return original_wait(kind, **kwargs)
                finally:
                    world.extra_heat_w = 0.0
            death = world.injections.collector_death.get(run_id)
            if death is not None and (kind != 'G0' or death == 0) and kwargs.get('turn', 0) >= death \
                    and world.dead_collector is not session:
                # The 1 Hz collector thread dies on a journal write error.
                world.dead_collector = session
                session.sidecar._error = OSError('synthetic journal write failure (ENOSPC)')
                session.sidecar._thread = SimpleNamespace(is_alive=lambda: False, join=lambda: None)
                world.log.append({'run_id': run_id, 'event': 'collector_death', 't': world.clock.now()})
            return original_wait(kind, **kwargs)

        def close():
            world.unregister(session)
            if world.dead_collector is session:
                world.dead_collector = None
            return original_close()
        session.wait, session.close = wait, close
        return session
    return factory


def run_member(world, config_map, runs_root, *, label):
    from joulewise.controller import run_benchmark
    from joulewise.schemas import BenchmarkConfig
    from joulewise.align.apple.registry_select import registry_for_config
    config = BenchmarkConfig.from_mapping(config_map)
    registry = registry_for_config(config)
    gated = registry is not None
    delegate = Delegate(world)
    if gated:
        registry.delegate = delegate
        registry.thermal_factory = thermal_factory(world)
        registry.status_factory = lambda telemetry, clock: world.status
    else:
        registry = delegate
    world.family = config.model.family
    world.run_id = config.run_id
    world.turn = 0
    start = world.clock.now()
    with patch('joulewise.bundle._writer_launch_lineage', return_value=None):
        bundle, summary = run_benchmark(config, runs_root, world.clock, registry=registry)
    return {'label': label, 'run_id': config.run_id, 'bundle': str(bundle), 'gated': gated,
            'status': summary.status.value,
            'failure_reason': getattr(summary.failure_reason, 'value', None),
            'failure_message': (summary.failure_message or '')[:600] if hasattr(summary, 'failure_message') else None,
            'start_s': start, 'end_s': world.clock.now()}


def collect(args, out):
    """Run synthetic pilot-7 references, build the kit, then all W1 members."""
    inj = syn.Injections()
    world = syn.World(injections=inj, leak_per_c=args.leak)
    stack, _ = syn.patches(world)
    results = {'variant': args.variant, 'inject': args.inject, 'leak_per_c': args.leak,
               'members': [], 'pilot7': {}}
    inputs = deepcopy(SYN_INPUTS)
    with stack:
        # WP18 stand-in: the frozen 45b47f7b6 configs run ungated; their
        # recorded turn counts become the contrast arms' max_turns.
        from joulewise.align.apple.workload import read_episode_bundle
        for name, index in (('X', 25), ('Y', 18)):
            source = f'configs/campaigns/align_pilot_v3/stages/episodes-b/align-pilot-v3-episodes-b-e{index}.json'
            config = synthesize(json.loads(kit.frozen(kit.ROOT, kit.CONTRAST_COMMIT, source)), out)
            config['run_id'] = f'pilot7-reference-{name}'
            ref = run_member(world, config, out / 'pilot7', label=f'pilot7-{name}')
            turns = len(read_episode_bundle(Path(ref['bundle'])).turns)
            ref['turns'] = turns
            rows = (Path(ref['bundle']) / 'outputs/align_turns.jsonl').read_bytes()
            inputs['WP18'][name] = {'max_turns': turns, 'token_fixture_sha256': hashlib.sha256(rows).hexdigest()}
            results['pilot7'][name] = ref
            world.clock.sleep(600)
        plan, raw_configs, _ = build_kit(inputs)
        results['inputs'] = inputs
        configs = {o: synthesize(c, out) for o, c in raw_configs.items()}
        members = {m['ordinal']: m for m in plan['members']}
        if args.variant == 'design-deadman':
            # FINAL-DESIGN §1(c)/§2.3: contrast arms stop at the pilot-7 turn
            # count with no deadman. The code requires one for gate cells, so
            # give them D's T_dead instead of the kit's 30B CONTRAST_DEADMAN_S.
            for o, m in members.items():
                if m['role'] not in ('anchor', 'D'):
                    spec = json.loads(configs[o]['workload_profile']['prompt_text'])
                    spec['deadman_s'] = SYN_INPUTS['R1']['T_dead']
                    configs[o]['workload_profile']['prompt_text'] = json.dumps(
                        spec, sort_keys=True, separators=(',', ':'), allow_nan=False)
        results['capture_config_sha256'] = rebind(configs)
        if args.inject == 'all':
            for ordinal, event in INJECT.items():
                run_id = members[ordinal]['run_id']
                if event == 'g0_timeout':
                    inj.g0_hot.add(run_id)
                elif event == 'os_level_nonzero':
                    inj.os_level[run_id] = 1
                elif event == 'malformed_xml':
                    inj.malformed_xml[run_id] = 1
                elif event == 'deadman':
                    inj.slow_decode[run_id] = 0.6
                elif event == 'collector_death':
                    inj.collector_death[run_id] = 1
        if args.inject == 'g0-contrast':
            # Probe: a hot G0 on the first X-G arm (G0 cap 600 s inside its deadman).
            inj.g0_hot.add(members[6]['run_id'])
        if args.inject == 'collector-g0':
            # Probe: the collector dies before G0 (outside run_workload's try).
            inj.collector_death[members[5]['run_id']] = 0
        selected = sorted(members) if args.members == 'all' else [int(x) for x in args.members.split(',')]
        for ordinal in selected:
            result = run_member(world, configs[ordinal], out / 'runs', label=str(ordinal))
            result.update(ordinal=ordinal, role=members[ordinal]['role'],
                          injected=INJECT.get(ordinal) if args.inject == 'all' else None)
            results['members'].append(result)
            print(json.dumps({k: result[k] for k in ('ordinal', 'role', 'status', 'injected')}), flush=True)
    results['world_log'] = world.log
    results['plan_members'] = plan['members']
    (out / 'run_results.json').write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')
    return results, world


# --------------------------------------------------------------------------
# Desk stage and independent design oracle
# --------------------------------------------------------------------------
DELTA = {'fast_c': 1.5, 'slow_c': 1.0}


def episode_json(bundle):
    path = Path(bundle) / 'outputs/align_episode.json'
    return json.loads(path.read_text()) if path.exists() else None


def roster_manifest(out, results):
    """Bridge the sealed collection plan to the desk manifest (no hand tags)."""
    items = []
    for name, ref in sorted(results['pilot7'].items()):
        items.append({'bundle': str(Path(ref['bundle']).relative_to(out)), 'window': 'pilot7-reference'})
    by_run = {m['run_id']: m for m in results['plan_members']}
    for r in results['members']:
        plan = by_run[r['run_id']]
        item = {'bundle': str(Path(r['bundle']).relative_to(out)), 'window': 'W1'}
        ordinal, role = plan['ordinal'], plan['role']
        if ordinal in PAIR_GROUPS:
            item['identical_work_group'] = PAIR_GROUPS[ordinal]
        if role[:1] in ('X', 'Y') and len(role) == 3:
            # Episode ids are the sanitized (lower-case) run ids.
            ref_id = episode_json(results['pilot7'][role[0]]['bundle'])['episode_id']
            item.update(template=role[0], arm=role[2], pilot7_reference_id=ref_id)
        ep = episode_json(r['bundle'])
        if ep is not None:
            g0 = [i for i in (ep['hardware'].get('thermal') or {}).get('intervals', []) if i['kind'] == 'G0']
            item['registered_span_ns'] = [g0[0]['start_ns'] if g0 else ep['start_ns'], ep['end_ns']]
        items.append(item)
    manifest = {'schema': 'wp22.synthetic_w1_manifest', 'members': items}
    (out / 'desk_manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return out / 'desk_manifest.json'


def run_desk(out, world):
    """Drive the unmodified WP21 CLI; only native PM supports are synthesized.

    read_bundle_record builds PM state/clock rows only from raw powermetrics
    plists, which the synthetic GPU rail does not write. The wrapper supplies
    1 s Nominal records on the episode clock when (and only when) that list is
    empty, exactly the shape member_record documents.
    """
    from joulewise.align.apple import thermal_desk
    from scripts import align_v4_thermal_desk as cli
    original = thermal_desk.member_record

    def member_record(episode, journal, *, os_readings, pm_samples, pm_period_s, **kwargs):
        if not pm_samples:
            intervals = (episode.hardware.get('thermal') or {}).get('intervals', [])
            start = min([episode.start_ns, *(i['start_ns'] for i in intervals)]) - NS
            pm_samples = syn.pm_samples(world, start, episode.end_ns + NS)
            pm_period_s = 1.0
        return original(episode, journal, os_readings=os_readings, pm_samples=pm_samples,
                        pm_period_s=pm_period_s, **kwargs)
    manifest = roster_manifest(out, json.loads((out / 'run_results.json').read_text()))
    if (out / 'desk').exists():
        import shutil
        shutil.rmtree(out / 'desk')
    try:
        with patch.object(thermal_desk, 'member_record', member_record):
            cli.main(['--manifest', str(manifest), '--output', str(out / 'desk')])
    except Exception as exc:  # noqa: BLE001 - a desk crash is itself a finding
        import traceback
        return {'status': 'crashed', 'error': f'{type(exc).__name__}: {exc}',
                'traceback': traceback.format_exc()[-3000:]}
    return {'status': 'ok', 'pilot': json.loads((out / 'desk/PILOT.json').read_text())}


def oracle_energy(world, ep):
    """Turn-owned GPU J from the world's own 10 Hz log: prefill+decode+tools, minus holds."""
    if ep is None:
        return None
    holds = [(i['start_ns'], i['end_ns']) for i in (ep['hardware'].get('thermal') or {}).get('intervals', [])
             if i['kind'] == 'H']
    spans = []
    for turn in ep['turns']:
        spans.append((turn['start_ns'], turn['end_ns']))
        spans.extend((c['start_ns'], c['end_ns']) for c in turn['tool_calls'])
    total = 0.0
    for t, w in world.power:
        a, b = round((t - 0.1) * NS), round(t * NS)
        covered = sum(max(0, min(b, y) - max(a, x)) for x, y in spans)
        covered -= sum(max(0, min(b, y) - max(a, x)) for x, y in holds)
        total += w * covered / NS
    return total


def turn_tokens(bundle):
    path = Path(bundle) / 'outputs/align_turns.jsonl'
    if not path.exists():
        return None
    return [[json.loads(line)['generation'].get(k) for k in ('prompt_token_ids', 'output_token_ids')]
            for line in path.read_text().splitlines() if line.strip()]


def ols(x, y):
    n, p = len(y), len(x[0])
    xtx = [[sum(r[i] * r[j] for r in x) for j in range(p)] for i in range(p)]
    xty = [sum(r[i] * v for r, v in zip(x, y)) for i in range(p)]
    # Gauss-Jordan inverse (independent of the desk's implementation).
    aug = [row[:] + [float(i == j) for j in range(p)] for i, row in enumerate(xtx)]
    for c in range(p):
        piv = max(range(c, p), key=lambda r: abs(aug[r][c]))
        aug[c], aug[piv] = aug[piv], aug[c]
        f = aug[c][c]
        aug[c] = [v / f for v in aug[c]]
        for r in range(p):
            if r != c:
                g = aug[r][c]
                aug[r] = [u - g * v for u, v in zip(aug[r], aug[c])]
    inv = [row[p:] for row in aug]
    beta = [sum(inv[i][j] * xty[j] for j in range(p)) for i in range(p)]
    resid = [v - sum(b * t for b, t in zip(beta, r)) for r, v in zip(x, y)]
    s2 = sum(e * e for e in resid) / (n - p)
    return beta, [math.sqrt(s2 * inv[i][i]) for i in range(p)], n - p


T90 = {1: 6.313752, 2: 2.919986, 3: 2.353363, 4: 2.131847, 5: 2.015048, 6: 1.943180}


def contrast_oracle(runs):
    """FINAL-DESIGN §2.5 mechanical rule, independently computed."""
    cells = {(t, a): [r for r in runs if r['template'] == t and r['arm'] == a] for t in 'XY' for a in 'SG'}
    if any(len(c) != 2 for c in cells.values()):
        return {'verdict': 'INCONCLUSIVE', 'reason': 'fewer than 2 token-identical runs in a template/arm'}
    sel = [r for c in cells.values() for r in c]
    t0 = min(r['start_ns'] for r in sel)
    x = [[1.0, float(r['template'] == 'Y'), float(r['arm'] == 'S'), (r['start_ns'] - t0) / 3600 / NS] for r in sel]
    beta, se, df = ols(x, [r['E'] for r in sel])
    delta, half = beta[2], T90[df] * se[2]
    ci = [delta - half, delta + half]
    d = {t: sum(r['E'] for r in cells[t, 'S']) / 2 - sum(r['E'] for r in cells[t, 'G']) / 2 for t in 'XY'}
    if all(abs(v) >= 10 for v in d.values()) and d['X'] * d['Y'] > 0 and (ci[0] > 0 or ci[1] < 0):
        verdict = 'T CONFIRMED'
    elif all(abs(v) <= 6 for v in d.values()) and ci[0] >= -6 and ci[1] <= 6:
        verdict = 'T REJECTED'
    else:
        verdict = 'INCONCLUSIVE'
    return {'verdict': verdict, 'd_template_j': d, 'delta_j': delta, 'ci90_j': ci, 'df': df}


def design_expectations(out, results, world, inject):
    """What FINAL-DESIGN + A1 say each member/model/contrast should yield."""
    members = []
    by_ord = {r['ordinal']: r for r in results['members']}
    plan = {m['ordinal']: m for m in results['plan_members']}
    ref_tokens = {k: turn_tokens(v['bundle']) for k, v in results['pilot7'].items()}
    for o, r in sorted(by_ord.items()):
        ep = episode_json(r['bundle'])
        role = plan[o]['role']
        event = INJECT.get(o) if inject == 'all' else None
        design_x = {'g0_timeout': ['X2'], 'os_level_nonzero': ['X1'], 'malformed_xml': [],
                    'deadman': ['X7'], 'collector_death': ['X4']}.get(event, [])
        members.append({'ordinal': o, 'role': role, 'run_id': r['run_id'], 'status': r['status'],
                        'event': event, 'design_exclusions': design_x,
                        'design_completes_episode': event in (None, 'g0_timeout', 'os_level_nonzero',
                                                              'collector_death', 'malformed_xml'),
                        'E_oracle_j': oracle_energy(world, ep),
                        'start_ns': ep['start_ns'] if ep else None,
                        'tokens': turn_tokens(r['bundle']),
                        'model': 'D' if role == 'D' else '30B'})
    by = {m['ordinal']: m for m in members}
    pairs = {}
    for group in sorted(set(PAIR_GROUPS.values())):
        a, b = (by.get(o) for o in sorted(o for o, g in PAIR_GROUPS.items() if g == group))
        if a is None or b is None or a['E_oracle_j'] is None or b['E_oracle_j'] is None:
            pairs[group] = {'status': 'inconclusive', 'reason': 'member missing'}
            continue
        if 'X4' in a['design_exclusions'] + b['design_exclusions']:
            pairs[group] = {'status': 'excluded_from_U', 'reason': 'X4'}
            continue
        identical = a['tokens'] == b['tokens']
        e = (a['E_oracle_j'] + b['E_oracle_j']) / 2
        margin = 3 * max(2.97, 0.0011 * e)
        delta = b['E_oracle_j'] - a['E_oracle_j']
        pairs[group] = {'status': ('X5' if not identical else 'pass' if abs(delta) <= margin else 'fail'),
                        'delta_j': delta, 'margin_j': margin}
    expected = {}
    for model in ('D', '30B'):
        gated = [m for m in members if m['model'] == model and m['role'] != 'anchor']
        thermal_x = [m['ordinal'] for m in gated if set(m['design_exclusions']) & {'X1', 'X2', 'X3', 'X4'}]
        u1 = 'fail' if len(thermal_x) > 1 else 'pass'
        groups = [g for g in pairs if (g.startswith('D') if model == 'D' else not g.startswith('D'))]
        statuses = [pairs[g]['status'] for g in groups if pairs[g]['status'] not in ('excluded_from_U', 'X5')]
        u3 = ('fail' if 'fail' in statuses else 'inconclusive' if 'inconclusive' in statuses or not statuses
              else 'pass')
        expected[model] = {'U1_thermal_excluded_members': thermal_x, 'U1': u1, 'U3': u3,
                           'U3_pairs': {g: pairs[g] for g in groups},
                           'U4': 'inconclusive', 'U5': 'inconclusive', 'U6': 'inconclusive',
                           'consequence': 'thermal protocol not met' if 'fail' in (u1, u3)
                           else 'U4-U6 not evaluable in W1; no control verdict'}
    runs_strict, runs_eligible = [], []
    for m in members:
        if m['role'][:1] in 'XY' and len(m['role']) == 3 and m['E_oracle_j'] is not None:
            run = {'template': m['role'][0], 'arm': m['role'][2], 'E': m['E_oracle_j'], 'start_ns': m['start_ns']}
            if m['tokens'] == ref_tokens[m['role'][0]] and m['status'] == 'succeeded':
                runs_strict.append(run)
                if not m['design_exclusions']:
                    runs_eligible.append(run)
    return {'members': [{k: v for k, v in m.items() if k != 'tokens'} for m in members],
            'pairs': pairs, 'models': expected,
            'contrast_token_identical_runs': contrast_oracle(runs_strict),
            'contrast_excluding_X_codes': contrast_oracle(runs_eligible)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--variant', choices=('kit', 'design-deadman'), default='kit')
    parser.add_argument('--inject', choices=('all', 'none', 'g0-contrast', 'collector-g0'), default='all')
    parser.add_argument('--leak', type=float, default=0.004, help='GPU power fraction per degC (synthetic)')
    parser.add_argument('--members', default='all', help="comma ordinals, or 'all'")
    parser.add_argument('--desk-only', action='store_true', help='re-run only the desk on OUTPUT_DIR')
    args = parser.parse_args(argv)
    out = args.output.resolve()
    if args.desk_only:
        # Re-read a finished collection; the oracle needs only the power log.
        results = json.loads((out / 'run_results.json').read_text())
        world = syn.World()
        world.power = [tuple(row) for row in json.loads((out / 'world_power.json').read_text())]
        args.inject = results['inject']
    else:
        out.mkdir(parents=True, exist_ok=False)
        results, world = collect(args, out)
        (out / 'world_power.json').write_text(json.dumps(world.power))
    desk = run_desk(out, world)
    expectations = design_expectations(out, results, world, args.inject)
    record = {'desk_status': desk['status'], 'desk_error': desk.get('error'),
              'desk_traceback': desk.get('traceback'), 'expected': expectations,
              'world_power_samples': len(world.power)}
    if desk['status'] == 'ok':
        pilot = desk['pilot']
        record['desk'] = {'model_windows': pilot['model_windows'],
                          'deciding_experiment': {k: v for k, v in pilot['deciding_experiment'].items()
                                                  if k != 'turn_tables'},
                          'members': [{k: m.get(k) for k in ('id', 'model', 'window', 'gated', 'flags',
                                                             'calibration_exclusions', 'turn_owned_j',
                                                             'turn_owned_half_width_j',
                                                             'pilot7_token_identical', 'excluded',
                                                             'template', 'arm', 'identical_work_group')}
                                      for m in pilot['members']]}
    (out / 'dry_run_record.json').write_text(json.dumps(record, indent=2, sort_keys=True, default=str) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
