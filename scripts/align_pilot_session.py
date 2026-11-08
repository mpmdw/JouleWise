#!/usr/bin/env python3
"""Prepare, hand off, and desk one NON-CLAIM ALIGN pilot 4 session.

prepare and install are the BYTES item-H runner's (scripts/bytes_h_session.py)
with the align kit: the same measurement view, real window-plan writer,
installer interface and in-chain agent census. desk reads every align member's
bundle read-only into the instrument-check summary (PILOT.json), then runs the
real harvest with --non-claim. Nothing here is registered or claim data.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import bytes_h_session as h

KIT = Path('configs/campaigns/align_pilot_v3')
PACK_ID = 'align-pilot-v3'
SCHEMA = 'joulewise.align_pilot_desk.v3'
# Instrument flags whose presence makes a member's energy unusable for the
# pilot's checks; each is emitted by joulewise.align (sampler/attribution).
ENERGY_BLOCKING = ('power_unavailable', 'trace.missing', 'trace.ambiguous', 'clock_anchor_unresolved')
# Reason code for an estimate the strict JSON writer cannot carry (an
# unresolved anchor gives an infinite half-width): the value becomes null.
NONFINITE = 'estimate.nonfinite'
# Per-turn token counts that define one episode's work (protocol I4).
TURN_COUNTS = ('context_tokens', 'prefill_tokens', 'decode_tokens', 'hidden_tokens')


def prepare(measurement_root, session_root, *, kit=KIT, pack_id=PACK_ID,
            session_prefix='align-pilot-', **kwargs):
    return h.prepare(measurement_root, session_root, kit=kit, pack_id=pack_id,
                     session_prefix=session_prefix, **kwargs)


def install(session_root, **kwargs):
    return h.install(session_root, **kwargs)


def _member_rows(state, *, kit=KIT):
    directory = Path(state.get('registration_dir', Path(state['measurement_root']) / kit / 'registration')).parent
    plan = h.read(directory / 'collection_plan.json')
    return plan['members']


def _estimate(values):
    """Finite floats as is; a nonfinite one as null with its reason under 'unavailable'."""
    out, unavailable = {}, {}
    for name, value in values.items():
        if math.isfinite(value):
            out[name] = value
        else:
            out[name] = None
            unavailable[name] = f'{NONFINITE}:{value}'
    if unavailable:
        out['unavailable'] = unavailable
    return out


def turn_counts(summary):
    """The per-turn (context, prefill, decode, hidden) token tuples of one summary."""
    return tuple(zip(*(summary['per_turn_' + name] for name in TURN_COUNTS), strict=True))


def episode_summary(bundle, *, target_precheck_paths=None, expected_episode_seed=None):
    """One member's episode, energy per recorded power channel, and flags."""
    from joulewise.align.apple.workload import read_episode_bundle
    from joulewise.align.attribution import attribute_episode

    episode = read_episode_bundle(bundle)
    energy = {}
    residual_rows = {}
    for trace in episode.power_traces:
        result = attribute_episode(episode, source=trace.source, channel=trace.channel)
        if trace.source == 'powermetrics' and trace.channel == 'gpu_power':
            from dataclasses import asdict
            from joulewise.align import energy_residual as er
            for logged in (True, False):
                residual_rows[str(logged)] = [asdict(r) for r in er.turn_rows_from_episode(
                    episode, er.turn_energy_from_attribution(result), hidden_token_counts_logged=logged)]
        energy[f'{trace.source}:{trace.channel}'] = {
            **_estimate({'joules': result.total.joules, 'half_width_j': result.total.half_width_j,
                         'segment_sum_j': math.fsum(s.energy.joules for s in result.segments)}),
            'method': result.total.method, 'segments': len(result.segments), 'flags': list(result.flags),
            'per_turn_j': [math.fsum(s.energy.joules for s in result.segments if s.turn == t.index)
                           for t in episode.turns],
            'per_turn_segments': [{'turn': s.turn, 'kind': s.kind, **_estimate({'joules': s.energy.joules})}
                                  for s in result.segments]}
    from joulewise.align.apple.diagnostics import tool_inventory, end_state, evidence_precheck, telemetry_diagnostics, action_diagnostics
    from joulewise.desk_compress import read_bytes
    inventory = tool_inventory(episode, bundle)
    try:
        turn_rows = [json.loads(line) for line in read_bytes(Path(bundle) / 'outputs/align_turns.jsonl').splitlines() if line.strip()]
    except FileNotFoundError:
        turn_rows = []
    calls = [[c.name for c in t.tool_calls] for t in episode.turns]
    totals = episode.totals()
    logged = episode.totals(logged_only=True)
    from joulewise.align.apple.diagnostics import cache_statistics, phase_reason_counts
    precheck = evidence_precheck(bundle, target_precheck_paths)
    from joulewise.align.apple.workload import EpisodeSpec
    from joulewise.schemas import BenchmarkConfig
    from joulewise.align.apple.pilot_analysis import check_turns
    config = BenchmarkConfig.from_mapping(json.loads(read_bytes(Path(bundle) / 'config.json')))
    spec = EpisodeSpec.from_text(config.workload_profile.prompt_text)
    messages = [json.loads(line) for line in read_bytes(Path(bundle) / 'outputs/align_transcript.jsonl').splitlines() if line.strip()]
    transcript = []
    for message in messages:
        if message['role'] == 'assistant':
            transcript.append([message])
        elif transcript:
            transcript[-1].append(message)
    controls = {k: getattr(spec, k) for k in ('enable_thinking', 'sampler', 'prompt_cache', 'max_context_tokens', 'max_episode_seconds')}
    controls['model'] = config.model.name
    return {'configuration': controls, 'residual_rows': residual_rows,
            **check_turns(episode, turn_rows, spec, config, transcript, expected_episode_seed=expected_episode_seed),
            'episode_start_ns': episode.start_ns, 'episode_end_ns': episode.end_ns,
            'turn_starts_ns': [t.start_ns for t in episode.turns],
            'per_turn_output_token_ids': [r.get('generation', {}).get('output_token_ids') for r in turn_rows],
            'per_turn_prompt_token_ids': [r.get('generation', {}).get('prompt_token_ids') for r in turn_rows],
            'cache_statistics': cache_statistics(turn_rows),
            'repetition_flags_per_turn': [[f for f in r.get('flags', []) if f.startswith('repetition.')]
                                          for r in turn_rows],
            'phase_window_reason_counts': phase_reason_counts(precheck),
            'episode_id': episode.episode_id, 'task_pair': episode.task_pair,
            'condition': episode.condition, 'seed': episode.seed,
            'duration_s': totals['duration_ns'] / 1e9, 'totals': totals, 'logged_totals': logged,
            **{'per_turn_' + name: [getattr(t, name) for t in episode.turns] for name in TURN_COUNTS},
            'main_task_score': episode.main_task_score, 'side_task_success': episode.side_task_success,
            'energy': energy, 'flags': list(episode.flags),
            'tool_inventory': inventory, 'tool_names_per_turn': calls,
            **action_diagnostics(episode),
            'unknown_tool_names': sorted({n for turn in calls for n in turn} - set(inventory['names'])),
            'end_state': end_state(episode, turn_rows),
            'ended_in_unclosed_reasoning': bool(episode.turns and not episode.turns[-1].tool_calls and turn_rows
                and 'unclosed_reasoning_span' in turn_rows[-1].get('flags', ())),
            'task_diagnostics': episode.hardware.get('task_diagnostics', {}),
            'window_evidence_precheck': precheck,
            **telemetry_diagnostics(bundle, episode)}


def instrument_checks(members):
    """The pilot's success criteria as an instrument check; never a hypothesis test.

    I4 compares exact emitted token IDs. Fewer than two comparable repeats is
    not_evaluated. Energy spreads additionally require equal accounting tuples
    and prompt IDs, so equal output counts cannot certify identical work.
    """
    readable = [m for m in members if m.get('summary')]
    usable = [m for m in readable if any(e['joules'] is not None for e in m['summary']['energy'].values())
              and not any(f.startswith(ENERGY_BLOCKING) for f in m['summary']['flags'])]
    # Agreement allowance: 0.5% of the smallest recorded attribution half-width
    # (about 1 J per real run), far above 1e6 x double summation roundoff.
    # Minimal synthetic dictionaries without uncertainty use that 1 J scale.
    widths = [e.get('half_width_j', 1.0) for m in usable for e in m['summary']['energy'].values()
              if e.get('half_width_j', 1.0) is not None and e.get('half_width_j', 1.0) > 0]
    agreement_j = 0.005 * min(widths) if widths else 0.005
    tiled = all(e['joules'] is not None and e['segment_sum_j'] is not None
                and abs(e['segment_sum_j'] - e['joules']) <= agreement_j
                for m in usable for e in m['summary']['energy'].values())
    cells = defaultdict(list)
    for m in readable:
        if m['summary'].get('configuration', {}).get('sampler') is not None:
            continue  # repeat_token_identity is a legacy greedy-only diagnostic.
        # Configuration blocks are different work, never greedy repeats of each other.
        cell = (m.get('block'), m['task_pair'], m['condition'])
        cells[cell].append(m['summary'])
    deterministic, spreads = {}, {}
    for (block, pair, condition), rows in sorted(cells.items(), key=lambda x: str(x[0])):
        key = (f'{block}/' if block else '') + f'{pair}/{condition}'
        comparable = [r for r in rows if comparable_ids(r)]
        deterministic[key] = ('not_evaluated' if len(comparable) < 2 else
                              len({output_ids(r) for r in comparable}) == 1)
        if deterministic[key] is not True or len(comparable) != len(rows):
            continue
        if len({turn_counts(r) for r in rows}) != 1 or len({prompt_ids(r) for r in rows}) != 1:
            continue
        for channel in sorted({c for r in rows for c in r['energy']}):
            values = [r['energy'][channel]['joules'] for r in rows
                      if channel in r['energy'] and r['energy'][channel]['joules'] is not None]
            if len(values) > 1:
                mean = math.fsum(values) / len(values)
                sd = math.sqrt(math.fsum((v - mean) ** 2 for v in values) / (len(values) - 1))
                spreads.setdefault(key, {})[channel] = {'n': len(values), 'mean_j': mean, 'sd_j': sd,
                                                        'range_j': max(values) - min(values),
                    'thermal_ineligible': any(any(code.startswith('thermal.') for code in r.get('exclusion_codes', []))
                        or 'thermal_pressure_elevated_in_window' in r.get('window_evidence_precheck', {}).get('reasons', [])
                        for r in rows),
                    'per_turn_j': [r['energy'][channel].get('per_turn_j', []) for r in rows if channel in r['energy']]}
    checks = {'I1_all_bundles_readable': len(readable) == len(members),
              'I2_energy_on_every_episode': len(usable) == len(members),
              'I3_attribution_tiles_episode': bool(usable) and tiled,
              'I4_greedy_repeats_identical_tokens': (False if any(v is False for v in deterministic.values()) else
                  'not_evaluated' if not deterministic or any(v == 'not_evaluated' for v in deterministic.values()) else True)}
    prechecks = [m['summary'].get('window_evidence_precheck', {}) for m in readable]
    checks['chain_eligibility'] = len(readable) == len(members) and bool(prechecks) and all(p.get('eligible') is True for p in prechecks)
    checks['no_member_exclusions'] = not any(m.get('excluded') for m in members)
    return checks, deterministic, spreads


def comparable_ids(summary):
    ids = summary.get('per_turn_output_token_ids')
    return bool(ids) and len(ids) == len(summary['per_turn_decode_tokens']) and all(
        isinstance(row, list) and len(row) == n and all(type(x) is int for x in row)
        for row, n in zip(ids, summary['per_turn_decode_tokens'], strict=True))


def output_ids(summary):
    return tuple(tuple(t) for t in summary['per_turn_output_token_ids'])


def prompt_ids(summary):
    return tuple(tuple(t) if t is not None else None for t in summary.get('per_turn_prompt_token_ids', []))


def cross_pilot_identity(members, compare_session):
    """Read comparator bundles only; never harvest or alter the prior session."""
    from joulewise.desk_compress import read_bytes
    root = Path(compare_session).resolve()
    state = h.read(root / 'session.json')
    runs = Path(state['runs_roots']['claim'])
    cells = defaultdict(list)
    for row in _member_rows(state):
        raw = read_bytes(runs / row['run_id'] / 'outputs/align_turns.jsonl')
        turns = [json.loads(line)['generation'] for line in raw.splitlines() if line.strip()]
        cells[(row.get('block'), row['task_pair'], row['condition'])].append((row['run_id'], turns))
    result = defaultdict(list)
    for member in members:
        cell = (member.get('block'), member['task_pair'], member['condition'])
        key = '/'.join(str(c) for c in cell if c is not None)
        summary = member.get('summary')
        references = cells.get(cell, [])
        if not summary or not references or not comparable_ids(summary):
            result[key].append({'run_id': member['run_id'], 'status': 'not_evaluated'})
            continue
        for reference_id, turns in references:
            divergence = None
            fields = []
            current = list(zip(summary['per_turn_prompt_token_ids'], summary['per_turn_output_token_ids'], strict=True))
            if any(t.get('prompt_token_ids') is None or t.get('output_token_ids') is None for t in turns):
                result[key].append({'run_id': member['run_id'], 'reference_run_id': reference_id, 'status': 'not_evaluated'})
                continue
            for index in range(max(len(current), len(turns))):
                if index >= len(current) or index >= len(turns):
                    divergence, fields = index, ['turn_count']
                    break
                p, o = current[index]
                fields = [name for name, a, b in (('prompt_token_ids', p, turns[index]['prompt_token_ids']),
                           ('output_token_ids', o, turns[index]['output_token_ids'])) if a != b]
                if fields:
                    divergence = index
                    break
            result[key].append({'run_id': member['run_id'], 'reference_run_id': reference_id,
                                'status': 'identical' if divergence is None else 'divergent',
                                'first_divergent_turn': divergence, 'fields': fields})
    return dict(result)


def desk(session_root, *, run=subprocess.run, harvest=True, compare_session=None,
         kit=KIT, desk_schema=SCHEMA, extra_checks=None):
    session = Path(session_root).resolve()
    state = h.read(session / 'session.json')
    plan = h.read(state['plan_path'])
    custody = Path(plan['custody_root'])
    if not (custody / 'night/result.json').is_file():
        raise ValueError('terminal record is required before desk')
    claim_root = state.get('runs_roots', {}).get('claim')
    if not claim_root:
        registration = Path(state.get('registration_dir', Path(state['measurement_root']) / kit / 'registration'))
        tree = h.read(registration.parent / 'plan_tree.json')
        claim_root = Path(state['inputs']['runs_parent']) / tree['roots']['claim_root_leaf']
    runs_root = Path(claim_root)
    from joulewise.align.apple.diagnostics import member_thermal_readings, thermal_onset
    thermal = member_thermal_readings(custody)
    targets = {}
    pack_root = state.get('inputs', {}).get('pack_root')
    if pack_root:
        from joulewise.b5.harvest import build_roster
        for member in build_roster(Path(pack_root), Path(state['measurement_root']))['members']:
            targets[member['run_id']] = [c['target_precheck_path'] for c in member.get('cells', [])
                if c.get('target') is not False and isinstance(c.get('target_precheck_path'), list) and c['target_precheck_path']]
    members = []
    for row in _member_rows(state, kit=kit):
        bundle = runs_root / row['run_id']
        entry = {k: row[k] for k in ('run_id', 'task_pair', 'condition', 'repeat', 'ordinal')}
        for key in ('model_id', 'block'):
            if key in row:
                entry[key] = row[key]
        try:
            entry['summary'] = episode_summary(bundle, target_precheck_paths=targets.get(row['run_id']),
                                               expected_episode_seed=row.get('expected_episode_seed'))
            summary = entry['summary']
            summary['os_thermal'] = thermal_onset(summary['episode_start_ns'], summary['episode_end_ns'],
                summary['turn_starts_ns'], thermal.get(row['run_id'], {}))
        except Exception as exc:
            entry['summary'] = None
            entry['unreadable'] = f'{type(exc).__name__}: {exc}'
        members.append(entry)
    # Read-only extraction first; the harvest may compress the runs afterwards.
    measurement = Path(state['measurement_root'])
    argv = [str(measurement / '.venv/bin/python'), str(measurement / 'scripts/harvest_b6_session.py'),
            '--plan', state['plan_path'], '--archive-root', str(session / 'archive'),
            '--registration-dir', state['registration_dir'], '--pack-records-root', str(session / 'private'),
            '--export-dir', str(session / 'export'), '--non-claim']
    if harvest:
        result = run(argv, check=False, capture_output=True, text=True, timeout=h.HARVEST_TIMEOUT_S)
        (session / 'staging/harvest.stdout').write_text(result.stdout or '')
        (session / 'staging/harvest.stderr').write_text(result.stderr or '')
        output = session
    else:
        from types import SimpleNamespace
        result = SimpleNamespace(returncode=None, stdout='', stderr='')
        inspection = session / 'inspection'
        inspection.mkdir(exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ-'),
                                       dir=inspection))
    exclusion_path = session / 'archive/derived/exclusions.json'
    exclusions = h.read(exclusion_path) if exclusion_path.is_file() else None
    excluded = {m['run_id']: m.get('codes', []) for m in (exclusions or {}).get('members_excluded', [])}
    for member in members:
        codes = excluded.get(member['run_id'], [])
        member.update(excluded=member['run_id'] in excluded, exclusion_codes=codes)
        if member['summary'] is not None:
            summary = member['summary']
            summary.update(excluded=member['excluded'], exclusion_codes=codes)
            pre = summary['window_evidence_precheck']
            summary['chain_eligible'] = pre['eligible'] is True and not member['excluded']
    from joulewise.desk_compress import read_bytes
    flag_path = session / 'archive/derived/flags.jsonl'
    harvest_flags = defaultdict(list)
    if flag_path.is_file():
        for line in read_bytes(flag_path).splitlines():
            if line.strip():
                flag = json.loads(line)
                harvest_flags[flag.get('scope', {}).get('run_id')].append(flag)
    battery_path = session / 'archive/withheld/battery-assist.json'
    battery = h.read(battery_path).get('members', {}) if battery_path.is_file() else {}
    for member in members:
        member['harvest_flags'] = harvest_flags.get(member['run_id'], [])
        member['battery_discharge'] = battery.get(member['run_id'])
    # Add the existing harvested whole-request DC integral alongside the rails.
    # This remains a diagnostic: v4's frozen rail fit and checks do not read it.
    from joulewise.align.apple.meter_desk import read_meter_record, member_meter
    meter = read_meter_record(session / 'archive/withheld/meter.json') if harvest and result.returncode in (0, 6) else {
        'record': None, 'reason': 'harvest not run or failed; stored archive may be stale',
        'path': None, 'sha256': None}
    for member in members:
        member['dc_input'] = member_meter(meter['record'], member['run_id'],
            flags=(harvest_flags.get(None, []) + member['harvest_flags']) if flag_path.is_file() else None)
    comparison = cross_pilot_identity(members, compare_session) if compare_session else None
    checks, deterministic, _legacy_spreads = instrument_checks(members)
    from joulewise.align.apple.pilot_analysis import sampling_checks, residual_analysis, episode_eligible, episode_ineligibility_reasons
    i4, spreads, raw_spread = sampling_checks(members)
    residuals = residual_analysis(members)
    # I4' replaces the greedy check for sampled cohorts. Collisions are
    # observations; they never alter instrument pass/fail.
    checks.pop('I4_greedy_repeats_identical_tokens')
    replay_results = [r for cell in i4.values() if isinstance(cell['replay_identity'], list) for r in cell['replay_identity']]
    checks['I4_replay_identity'] = (all(r['status'] == 'identical' for r in replay_results) if replay_results else 'not_evaluated')
    for field in ('accounting', 'sampler_provenance'):
        values = [r['status'] for cell in i4.values() for r in cell[field]]
        checks['I4_' + field] = (False if 'fail' in values else True if values and all(v == 'pass' for v in values) else 'not_evaluated')
    checks['chain_eligibility'] = checks['chain_eligibility'] and not excluded
    checks['harvest_exclusions_recorded'] = exclusions is not None
    # Pack-specific instrument checks (v4: ruling 7 powermode); v3 passes none.
    extra_report = None
    if extra_checks is not None:
        added, extra_report = extra_checks(state=state, members=members, runs_root=runs_root, kit_path=kit)
        checks.update(added)
    pilot = {'schema_version': desk_schema, 'non_claim': True, 'session_id': state['session_id'],
             'plan_id': state['session_id'], 'runs_root': str(runs_root), 'members': members,
             'checks': checks, 'repeat_token_identity': deterministic, 'repeat_energy_spread': spreads,
             'I4_prime': i4, 'raw_within_cell_energy_sd': raw_spread, 'residual_analysis': residuals,
             'registered_eligible_members': [m['run_id'] for m in members if not m['excluded']],
             'episode_scope_alternative_eligible_members': [m['run_id'] for m in members if m.get('summary') and episode_eligible(m)],
             'episode_scope_alternative_ineligible_reasons': {m['run_id']: episode_ineligibility_reasons(m)
                 for m in members if m.get('summary') and not episode_eligible(m)},
             'exclusions_path': str(exclusion_path), 'members_excluded': (exclusions or {}).get('members_excluded', []),
             'cross_pilot_token_identity': comparison,
             'session_harvest_flags': harvest_flags.get(None, []),
             'meter_record': {k: v for k, v in meter.items() if k != 'record'},
             'harvest_flags_status': 'recorded' if flag_path.is_file() else 'not_recorded',
             **({'extra_checks': extra_report} if extra_checks is not None else {}),
             'status': 'instrument_ok' if all(v is True for v in checks.values()) else 'instrument_incomplete'}
    from joulewise.align.apple.pilot_analysis import finite_json
    pilot = finite_json(pilot)
    h.write(output / 'PILOT.json', pilot)
    status = {'schema_version': desk_schema, 'non_claim': True, 'plan_id': state['session_id'],
              'pilot': str(output / 'PILOT.json'), 'pilot_status': pilot['status'], 'checks': checks,
              'harvest_argv': argv, 'harvest_exit': result.returncode,
              'members_excluded': pilot['members_excluded'],
              'harvest_status': ('not_run' if not harvest else 'program_fault' if result.returncode not in (0, 6)
                                 else 'members_excluded' if excluded else 'exclusions_unavailable' if exclusions is None else 'ok')}
    h.write(output / 'desk.json', status)
    print('pilot_report: ' + status['pilot'])
    print('pilot_status: ' + pilot['status'])
    for name, ok in checks.items():
        print(f'{name}: {"not_evaluated" if ok == "not_evaluated" else "pass" if ok is True else "fail"}')
    print('model.identity_mismatch: under NON_CLAIM_FILE_IDENTITIES_ONLY pins the runtime identity is unsealed (null); this is expected and is not a claim identity pass.')
    print('session harvest_flags: ' + json.dumps(pilot['session_harvest_flags'], sort_keys=True))
    for member in members:
        print(member['run_id'] + ' harvest_flags: ' + json.dumps({'flags': member['harvest_flags'],
              'battery_discharge': member['battery_discharge']}, sort_keys=True))
        summary = member.get('summary')
        if summary is None:
            print(member['run_id'] + ': unreadable ' + member['unreadable'] + ' ' + json.dumps({
                'excluded': member['excluded'], 'exclusion_codes': member['exclusion_codes']}, sort_keys=True))
            continue
        pre = summary['window_evidence_precheck']
        print(member['run_id'] + ': ' + json.dumps({
            'end_state': summary['end_state'], 'state_changing_calls': summary['state_changing_calls'],
            'episode_seconds': summary['duration_s'], 'sampler_policy': summary['configuration']['sampler'],
            'cap_hits': sum(f.startswith('turn_token_budget_reached:') for f in summary['flags']),
            **{k: summary[k] for k in ('acted_beyond_read_marking', 'bank_stage', 'cache_statistics', 'repetition_flags_per_turn', 'phase_window_reason_counts')},
            **{k: summary[k] for k in ('classification', 'counted_tool_names', 'read_only_tool_names', 'unobserved_tool_names', 'exclusion_codes', 'excluded', 'os_thermal')},
            'tool_names_per_turn': summary['tool_names_per_turn'], 'unknown_tool_names': summary['unknown_tool_names'],
            'thermal_pressure_seconds': summary['thermal_pressure_seconds'],
            'active_gpu_clock_mhz': summary['active_gpu_clock_mhz'],
            'per_turn_active_gpu_clock_mhz': summary['per_turn_active_gpu_clock_mhz'],
            'chain_eligible': summary['chain_eligible'], 'chain_reasons': pre['reasons'] + summary['exclusion_codes'],
            'target_precheck_eligible': pre['eligible'],
            'request_window_diagnostics': pre['request_windows'],
            'window_evidence_precheck': {r['window']: {'eligible': r['eligible'], 'reasons': r['reasons']} for r in pre['windows']},
            'ended_in_unclosed_reasoning': summary['ended_in_unclosed_reasoning']}, sort_keys=True))
    print('repeat_token_identity (greedy-only; sampled configurations skipped): ' + json.dumps(deterministic, sort_keys=True))
    if comparison is not None:
        print('cross_pilot_token_identity: ' + json.dumps(comparison, sort_keys=True))
    for key in ('I4_prime', 'registered_eligible_members', 'episode_scope_alternative_eligible_members',
                'episode_scope_alternative_ineligible_reasons',
                'raw_within_cell_energy_sd', 'residual_analysis'):
        print(key + ': ' + json.dumps(pilot[key], sort_keys=True, allow_nan=False))
    print('whole_request_dc_input: ' + json.dumps({m['run_id']: m['dc_input'] for m in pilot['members']},
                                               sort_keys=True, allow_nan=False))
    print('repeat_energy_spread: ' + json.dumps(spreads, sort_keys=True))
    print('harvest_exit: ' + str(result.returncode))
    print('harvest_status: ' + status['harvest_status'])
    return status


def main(argv=None, *, kit=KIT, pack_id=PACK_ID, desk_schema=SCHEMA,
         prepare_fn=prepare, install_fn=install, session_prefix='align-pilot-',
         desk_extra_checks=None, install_options=()):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('--measurement-root', type=Path, required=True)
    p.add_argument('--session-root', type=Path, required=True)
    for name in ('install', 'desk'):
        commands.add_parser(name).add_argument('--session-root', type=Path, required=True)
    commands.choices['desk'].add_argument('--no-harvest', action='store_true', help='Extract to session/inspection/<utc>-<unique>/; preserve harvest files and skip archive/compression.')
    commands.choices['desk'].add_argument('--compare-session', type=Path)
    # Kit-specific install arguments (flag, argparse options), forwarded as keywords.
    for flag, options in install_options:
        commands.choices['install'].add_argument(flag, **options)
    args = parser.parse_args(argv)
    try:
        if args.command == 'prepare':
            prepare_fn(args.measurement_root, args.session_root, kit=kit, pack_id=pack_id,
                       session_prefix=session_prefix)
        elif args.command == 'install':
            extra = {flag.lstrip('-').replace('-', '_'): getattr(args, flag.lstrip('-').replace('-', '_'))
                     for flag, _ in install_options}
            install_fn(args.session_root, **extra)
        else:
            status = desk(args.session_root, harvest=not args.no_harvest, compare_session=args.compare_session,
                          kit=kit, desk_schema=desk_schema,
                          **({'extra_checks': desk_extra_checks} if desk_extra_checks is not None else {}))
            return 0 if status['harvest_status'] in ('ok', 'not_run') and status['pilot_status'] == 'instrument_ok' else 2
        return 0
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print('align_pilot_session: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
