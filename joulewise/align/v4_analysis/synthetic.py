"""Deterministic synthetic full series. Never opens data or model directories."""
from copy import deepcopy
import random
import math
from .io import canonical, digest

from .engine import SCHEMA, CALIBRATION_ORDER, TEST_ORDER, D_MODEL, roster
from .residual import design_row


def member_config(slot):
    """Synthetic bundle config; no task factory or model path is ever opened."""
    spec = dict(schema='joulewise.align.apple.episode_spec.v1',
        task_factory='joulewise.align.apple.pilot:offline_shade_task',
        task_kwargs=dict(task_pair=slot['task_pair']), condition=slot['condition'],
        seed=slot['seed_index'], enable_thinking=True, max_turns=12,
        max_tokens=4096, temperature=.6,
        sampler=dict(temperature=.6, top_p=.95, top_k=20, min_p=0))
    return dict(schema_version='0.1', run_id=slot['run_id'],
        model=dict(name='synthetic-model', family='mock', source='synthetic/model'),
        quantization=dict(name='none'), hardware_target=dict(id='synthetic',
            transport='local', runtime_backend='mock', telemetry_backend='mock'),
        workload_profile=dict(name='align_episode', prompt_text=canonical(spec).decode()),
        run_metadata=dict(project='synthetic', tags=['align-model='+slot['model_id']]))


def series(*, turns=12, identity_tokens=8, reserves=0):
    if type(reserves) is not int or not 0 <= reserves <= 6:
        raise ValueError('synthetic reserves must be in 0..6')
    cohort = dict(identity=dict(model_source='synthetic/Qwen', model_revision='synthetic',
        runtime_sha256='a'*64, execution_policy_sha256='b'*64), configuration=dict(
        max_episode_decode_tokens=16384, deadman_s=1200., max_tokens=4096, max_turns=12))
    windows = []
    for wi, name in enumerate(CALIBRATION_ORDER[:8+reserves]+TEST_ORDER):
        members = []
        for slot in roster(name):
            run = slot['run_id']
            rng = random.Random(100000*wi+slot['expected_episode_seed'])
            if slot['series_role'] == 'sentinel':
                rng = random.Random(1234)
            rows, withheld, tokens = [], [], []
            for k in range(turns):
                r = dict(episode_id=run, group=slot['task_pair'], context_tokens=rng.randint(1000, 20000),
                    prefill_tokens=rng.randint(100, 2000), decode_tokens=rng.randint(256, 1500),
                    duration_s=50., energy_half_width_j=.15, uncertainty_kind='additive_bound')
                r['energy_j'] = sum(a*b for a, b in zip(design_row(r), (2., .003, .15, .000002, .0000003)))
                r['energy_j'] += rng.gauss(0., .5)
                if slot['condition'] == 'sabotage':
                    r['energy_j'] += 1.
                hidden = rng.randint(64, min(200, r['decode_tokens']))
                rows.append(r)
                withheld.append({**r, 'decode_tokens': r['decode_tokens']-hidden})
                # Large mode uses full prompt/output IDs. Small fixtures retain
                # exact equality surfaces without allocating a hardware corpus.
                count = r['context_tokens']+r['prefill_tokens'] if identity_tokens == 'full' else identity_tokens
                tokens.append(dict(prompt_token_ids=[(i+k)%256 for i in range(count)],
                    output_token_ids=[(i+slot['seed_index'])%256 for i in range(
                        r['decode_tokens'] if identity_tokens == 'full' else identity_tokens)]))
            owned = math.fsum(r['energy_j'] for r in rows)
            d = slot['model_id'] == D_MODEL
            thermal = dict(id=run, model=slot['model_id'], gated=d, pair=slot['task_pair'],
                condition=slot['condition'], status='completed', start_ns=(wi*100000+slot['ordinal']*2000)*10**9,
                flags=[], calibration_exclusions=[], energy_flags=[], owned_energy_flags=[], registered_os_nonzero=False,
                registered_os_observed=True, coverage=[dict(sample_fraction=1., max_interval_ns=10**9)],
                turn_observation=[dict(os_nominal=True, pm_nominal=True, pm_max_gap_s=.1) for _ in rows],
                pm_period_s=.1, pm_max_gap_s=.1, turn_admissions=turns,
                intervals=[dict(kind='G0', outcome='released')]+[
                    dict(kind='G1', outcome='released') for _ in range(max(0, turns-1))],
                releases=[dict(journal_verified=True)], g0_slow_c=55.+slot['seed_index']%3*.1,
                tokens=tokens, decode_clock_mhz=1200., decode_clocks_mhz=[1200.]*turns,
                identity_evidence=dict(transcript_sha256='d'*64, prompt_cache_accounting_sha256='e'*64,
                                       turn_seed_law='align-p4-turn-v1', seed_index=slot['seed_index']),
                turn_owned_j=owned, turn_owned_half_width_j=turns*.15,
                gross_episode_j=owned+2., gross_episode_half_width_j=2.,
                battery=dict(status='observed', flags=[], soc_pct=[100., 100.], charger_w=[80., 80.],
                             source_sha256='c'*64),
                configuration=deepcopy(cohort['configuration']), cohort_identity=deepcopy(cohort['identity']))
            thermal['identity_sha256'] = digest(canonical([tokens, thermal['identity_evidence']]))
            thermal['turn_counts'] = [[r[k] for k in ('context_tokens', 'prefill_tokens', 'decode_tokens')] for r in rows]
            if slot['series_role'] == 'sentinel':
                thermal['identical_work_group'] = 'sentinel'
            summary = dict(flags=[], seed=slot['seed_index'], residual_rows={
                'True': rows, 'False': withheld}, energy={'powermetrics:gpu_power': dict(
                    joules=owned+2., half_width_j=2.)}, cache_statistics=dict(rebuilds=0, rewinds=0))
            members.append(dict(slot=slot, thermal=thermal, summary=summary, captured=True,
                                config=member_config(slot),
                                dc=dict(joules=(owned+2.)*1.5, half_width_j=4., flags=[])))
        windows.append(dict(window=name, attempt_id=name+'#1', status='final', members=members))
    reference_j = next(m['thermal']['turn_owned_j'] for m in windows[0]['members'] if m['slot']['ordinal'] == 5)
    pilot_pairs = [dict(session='synthetic-pilot-'+str(i), ordinals=[2, 7], prespecified=True,
                        token_identical=True, energies_j=[1000., 1000.+v])
                   for i, v in enumerate((1., -1.1, .8, -1.4, .6, 1.2))]
    return dict(schema=SCHEMA, synthetic=True, cohort=cohort, windows=windows,
        u3_evidence=dict(pilot_pairs=pilot_pairs, frozen_before_W1=True,
                        r1_d_screen=dict(token_identical=True, eligible=True, relative_difference=.001)),
        reference=dict(qualified=True, r1_replay_j=[reference_j]*2,
                       w1_sentinel_j={'5': reference_j, '17': reference_j}),
        r1_sensitivity=dict(states=[dict(token_identical=True, g0_slow_c=t, turn_owned_j=100+.1*t,
                                        designed_target_c=t) for t in (50., 55., 60.)],
                            r1_replay_j=[reference_j]*2, delta_slow_c=1.),
        u6_split_rule='within_pair_episode_order', custody='synthetic only; no native qualification')


def release_manifest(windows=()):
    """Synthetic analysis-form R24 manifest (W1, C1-C14, T1-T3) for release input.

    Slots of supplied windows are used as given; absent windows come from the
    frozen roster, anchors prefixed ``<window>:``. Synthetic W1 is C1's anchors
    and replay at ordinals 5 and 17 (the shape of the hand-test W1 window).
    """
    from copy import deepcopy
    from .engine import R24_SERIES_ORDER
    present = {w['window']: [m['slot'] for m in w['members']] for w in windows if 'members' in w}
    w1 = [dict(s) for s in roster('C1')[:5]] + [dict(roster('C1')[21], ordinal=17)]
    out = []
    for name in R24_SERIES_ORDER:
        slots = present.get(name) or [
            {**s, 'run_id': name+':'+s['run_id']} if s['series_role'] == 'anchor' else s
            for s in (w1 if name == 'W1' else roster(name))]
        out.append(dict(window=name, members=deepcopy(slots)))
    return dict(windows=out)
