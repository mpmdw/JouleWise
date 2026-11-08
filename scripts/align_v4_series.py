#!/usr/bin/env python3
"""Frozen v4 F/C/T allocation and executable kits; no model/data discovery.

The checked-in candidate is NOT a scientific ruling. Admission binds its exact
bytes, W1 clearance, scorer/fit contract and the lead's explicit choices. Kits
use the same calibrated stage graph and session/HAZARD_PACK path as W1.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import align_v4_kit as w1
from scripts.align_pilot_kit import raw_json, sha
from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple.sampling import episode_seed, turn_seed
from joulewise.b5 import chain

SCHEMA = 'joulewise.align_v4.series.v1'
ADMISSION_SCHEMA = 'joulewise.align_v4.series_admission.v1'
MANIFEST = w1.KIT / 'series/series_manifest.json'
ADMISSION = w1.KIT / 'series/admission.json'
PAIRS = ('spam_filter_update', 'bank_transfer_2')
PAIR_KEYS = dict(zip(PAIRS, cadence.CAL_PAIRS))


def kit_path(window_id):
    return Path('configs/campaigns') / ('align_v4_' + window_id.lower())


def pack_id(window_id):
    return 'align-v4-' + window_id.lower()


RESERVED_INDICES = frozenset({1, *range(91, 100)})   # development: W1 1/93, R0 91-92, reserve 94-99
HELD_OUT_START = 2
CALIBRATION_WINDOWS = 8                              # counted calibration windows
REPLACEMENT_WINDOWS = cadence.REPLACEMENT_WINDOWS   # R22-2 cap: C9, C10 are armable, only after a structural bar
RESERVE_WINDOWS = 4                                  # seeds are allocated for C9-C12; C11, C12 can NOT be armed (cap C10)
RESERVE_POOL_START = 100                             # contiguous pool after the T range and the reserved 91-99
TEST_WINDOWS = 3                                     # RUN_STATE 226 R15
SABOTAGE_ORDINALS = (9, 18)                          # Amendment 1: spread, one per half
D_CEILING_S = 59520                                  # Ed Q4
ESCALATED_CEILING_S = 62400                          # RUN_STATE 226 R15: +2-sentinel windows only


def candidate():
    """The frozen series (RUN_STATE 226 R15): Sol code base, Opus allocation.

    W1, then C1-C8 (D_k is C_k: no separate fit windows), the two pre-declared blind replacement windows
    C9 and C10 (R22-2; armed only after a structural bar of a C window), then T1-T3 (C11 and C12 hold reserve seeds only). Every C/T
    window: anchors 1-4 (original bytes), early W1:5 sentinel at 5, sixteen fresh
    held-out D members at 6-21 alternating pair by pair (odd windows spam first,
    even bank first; first pair on even ordinals) with sabotage at 9 (second
    pair) and 18 (first pair), late sentinel at 22; midpoint after 11. Held-out
    seed indices are distinct, consumed per pair in kit order (window order,
    then ordinal) from 2, skipping 1 and 91-99: C1-C8 use 2-65 and T1-T3 66-89 (exactly as R15; the paired
    seed check MATCHed them). The reserve pool for C9-C12 is the contiguous range 100-131 (8 per pair per
    window): 91-99 are reserved development indices, so it starts at 100. Only C9 and C10 are armable (the
    R22-2 cap); C11 and C12 have fixed seeds but the ledger refuses to arm them. A
    C-window sabotage member is pool ``known_h`` and counts toward nothing.
    """
    selection = []
    for ordinal, (role, pair, condition, index) in enumerate(w1.ROSTER, 1):
        model = w1.D_TAG if role == 'D' else 'qwen3-30b-a3b'
        seed = episode_seed(model, 'thinking_on', 'shade/' + pair, index)
        selection.append(dict(ordinal=ordinal, pool='selection', role=role, pair=pair,
            condition=condition, seed_index=index, model_id=model, episode_seed=seed,
            turn_seed_0=turn_seed(seed, 0)))
    windows = [{'id': 'W1', 'role': 'selection', 'aliases': [], 'members': selection}]
    next_index = dict.fromkeys(PAIRS, HELD_OUT_START)
    # Seeds are consumed per pair in kit order: C1-C8, then T1-T3 (both exactly as R15), then the contiguous
    # RESERVE pool for C9-C12 from index 100 (91-99 are reserved development indices; 90 is left unused so the
    # pool is one contiguous range). Run order is C1-C8, C9/C10 only as owed, then T1-T3.
    plan = ([('C', 'calibration', n, False) for n in range(1, CALIBRATION_WINDOWS + 1)]
            + [('T', 'test', n, False) for n in range(1, TEST_WINDOWS + 1)]
            + [('C', 'calibration', CALIBRATION_WINDOWS + n, True) for n in range(1, RESERVE_WINDOWS + 1)])
    built = {}
    for prefix, role, number, reserve in plan:
        if reserve and number == CALIBRATION_WINDOWS + 1:
            assert RESERVE_POOL_START > max(next_index.values()) and RESERVE_POOL_START not in RESERVED_INDICES
            next_index = dict.fromkeys(PAIRS, RESERVE_POOL_START)
        first = PAIRS[0] if number % 2 else PAIRS[1]
        second = PAIRS[1] if first == PAIRS[0] else PAIRS[0]
        rows = [dict(pool='anchor', pair=pair, condition=condition, seed_index=1)
                for pair, condition in zip((PAIRS[0], PAIRS[1], PAIRS[0], PAIRS[1]),
                                           ('benign', 'sabotage', 'sabotage', 'benign'))]
        rows.append(dict(pool='sentinel', pair=PAIRS[0], condition='benign', seed_index=1))
        for ordinal in range(6, 22):
            pair = first if ordinal % 2 == 0 else second
            sabotage = ordinal in SABOTAGE_ORDINALS
            while next_index[pair] in RESERVED_INDICES:
                next_index[pair] += 1
            pool = role if not sabotage or role == 'test' else 'known_h'
            rows.append(dict(pool=pool, pair=pair, condition='sabotage' if sabotage else 'benign',
                             seed_index=next_index[pair]))
            next_index[pair] += 1
        rows.append(deepcopy(rows[4]))
        for ordinal, row in enumerate(rows, 1):
            model = 'qwen3-30b-a3b' if row['pool'] == 'anchor' else w1.D_TAG
            seed = episode_seed(model, 'thinking_on', 'shade/' + row['pair'], row['seed_index'])
            row.update(ordinal=ordinal, model_id=model, episode_seed=seed, turn_seed_0=turn_seed(seed, 0))
        extra = {}
        if reserve:
            extra['replacement'] = True
            if number > CALIBRATION_WINDOWS + REPLACEMENT_WINDOWS:
                extra['armable'] = False             # beyond the cap: seeds fixed, the ledger refuses to arm it
        built[prefix + str(number)] = dict(id=prefix + str(number), role=role,
            aliases=['D' + str(number)] if prefix == 'C' and not reserve else [],
            midpoint_after_ordinal=11, members=rows, **extra)
    run_order = ([f'C{n}' for n in range(1, CALIBRATION_WINDOWS + REPLACEMENT_WINDOWS + 1)]
                 + [f'T{n}' for n in range(1, TEST_WINDOWS + 1)])
    windows += [built[name] for name in run_order]
    windows += [built[f'C{n}'] for n in range(CALIBRATION_WINDOWS + REPLACEMENT_WINDOWS + 1,
                                              CALIBRATION_WINDOWS + RESERVE_WINDOWS + 1)]
    return dict(schema=SCHEMA, status='FROZEN_PER_RUN_STATE_226_R15_R22_PENDING_PAIRED_SEED_CHECK',
                d_mapping='alias_calibration', test_windows=TEST_WINDOWS, order=['W1', *run_order],
                windows=windows,
                calibration=dict(counted_windows=CALIBRATION_WINDOWS, benign_per_pair_per_window=7,
                                 minimum_eligible_per_pair=39, replacements=0, fence_from='C6',
                                 replacement_windows=['C9', 'C10'], replacement_cap=REPLACEMENT_WINDOWS,
                                 reserve_windows_not_armable=['C11', 'C12'],
                                 replacement_rule='R22-2: armed only after a STRUCTURAL bar of a C window '
                                                  '(U1-U3 fail, whole-window capture failure, zero-capture '
                                                  'refusal beyond the retry); never on scores or counts'),
                seed_allocation=dict(held_out_start=HELD_OUT_START, reserved=sorted(RESERVED_INDICES),
                                     order='per pair, kit order: C1-C8, T1-T3 (as R15), then the reserve pool for '
                                           'C9-C12; distinct indices',
                                     reserve_pool=dict(start=RESERVE_POOL_START, per_pair_per_window=8,
                                                       windows=['C9', 'C10', 'C11', 'C12'], armable=['C9', 'C10'],
                                                       why_after_90='indices 91-99 are reserved development indices '
                                                                    '(W1 1/93, R0 91-92, reserve 94-99)'),
                                     zero_capture_rearm='reuses the same seeds'),
                sentinel=dict(source='W1:5', late_replay_of=5, extra_on_inconclusive=2,
                              escalated_ceiling_s=ESCALATED_CEILING_S),
                seed_law='align-p4-v1', turn_seed_law='align-p4-turn-v1',
                test_shape='v4: 14 benign + 2 sabotage; no v5 attacks or physical controls',
                authority='RUN_STATE 226 R15',
                open_rulings=['paired seed check of these manifest bytes before signing',
                              'Sol simulation of the R22-2 replacement rule (FPR at the fixed-8 level under drift) '
                              'before registration'])


def validate(manifest):
    # Accept only the frozen design (RUN_STATE 226 R15); changing a slot needs a
    # reviewed builder change and a new paired seed check, never a silent edit.
    if not isinstance(manifest, dict) or manifest.get('schema') != SCHEMA:
        raise ValueError('missing series manifest')
    expected = candidate()
    if manifest != expected:
        raise ValueError('series allocation differs from the frozen executable design')
    return manifest


def selected(manifest, name):
    validate(manifest)
    for row in manifest['windows']:
        if name == row['id'] or name in row['aliases']:
            return row
    raise ValueError('window is not in the frozen series: ' + str(name))


def load(root):
    raw = (Path(root) / MANIFEST).read_bytes()
    manifest = validate(json.loads(raw))
    if raw != raw_json(manifest):
        raise ValueError('series manifest must use canonical frozen bytes')
    return manifest


def evidence(ref):
    """Read only an explicitly supplied, digest-bound JSON object and pointer."""
    if not isinstance(ref, dict) or not w1.valid_digest(ref.get('sha256')):
        raise ValueError('evidence needs a path, SHA-256 and JSON pointer')
    # Retain exact source bytes for transport from Air to MBP. The original
    # path becomes provenance text; SHA-256 still binds every source byte.
    raw = (ref['content_utf8'].encode('utf-8') if isinstance(ref.get('content_utf8'), str)
           else Path(ref['path']).read_bytes())
    if sha(raw) != ref['sha256']:
        raise ValueError('series evidence bytes changed: ' + str(ref['path']))
    value = json.loads(raw)
    pointer = ref.get('pointer')
    if not isinstance(pointer, str) or (pointer and not pointer.startswith('/')):
        raise ValueError('evidence needs an explicit JSON pointer')
    for key in pointer.split('/')[1:] if pointer else ():
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def require_admission(root, manifest, *, post_w1=True):
    receipt = json.loads((Path(root) / ADMISSION).read_bytes())
    if (receipt.get('schema') != ADMISSION_SCHEMA
            or receipt.get('manifest_sha256') != sha((Path(root) / MANIFEST).read_bytes())
            or not w1.valid_lead_signature(receipt.get('lead_signature'))):
        raise ValueError('series requires exact-byte lead admission')
    choices = receipt.get('choices') or {}
    if choices != {k: manifest[k] for k in ('d_mapping', 'test_windows', 'test_shape', 'sentinel')}:
        raise ValueError('lead admission must explicitly accept mapping, test shape and sentinel')
    if receipt.get('w1_collection_sha256') != sha((Path(root) / w1.KIT / 'collection_plan.json').read_bytes()):
        raise ValueError('series admission belongs to another W1 configuration')
    required = ['scorer_fit_contract', 'seed_allocation', 'r13_r14_gate', 'paired_build_agreement']
    if post_w1:
        required += ['w1_clearance']
    for name in required:
        if evidence((receipt.get('evidence') or {}).get(name)) != 'pass':
            raise ValueError('series admission pending: ' + name)
    return receipt


def _rewrite(value, directory, pack):
    if isinstance(value, str):
        return value.replace(w1.KIT.as_posix(), directory.as_posix()).replace(w1.PACK_ID, pack)
    if isinstance(value, list):
        return [_rewrite(v, directory, pack) for v in value]
    if isinstance(value, dict):
        return {k: _rewrite(v, directory, pack) for k, v in value.items()}
    return value


def escalation_allocations(window):
    """R20: the two supplemental escalation sentinels (ordinals 23 and 24).

    Exact replays of the admitted W1:5 trajectory: same D model, spam/benign, seed index 1 (hence the
    same episode and turn seeds under the seed law), and, because they are built from the same member
    template, the same sampler, budgets, cache policy and stack. They draw no held-out seed.
    """
    base = next(m for m in window['members'] if m['ordinal'] == 5)
    return [dict(deepcopy(base), ordinal=22+k, escalation_sentinel=k) for k in (1, 2)]


def build_files(root, manifest, name, *, extra_sentinels=0):
    """Materialize an actual stage graph, manifests, configs, pins and sizing.

    No plausible R1 default is introduced. Pending W1 inputs remain pending;
    native prepare always runs require_w1_ready and exact-byte admission first.
    """
    root = Path(root)
    window = selected(manifest, name)
    if window.get('armable') is False:
        raise ValueError(f'{window["id"]} is a reserve window beyond the R22-2 cap (C10): its seeds are fixed '
                         'but it can not be materialized or armed without a ruling')
    if extra_sentinels not in (0, 2):
        raise ValueError('a window carries 0 or 2 escalation sentinels')
    if window['id'] == 'W1':
        if extra_sentinels:
            raise ValueError('U4/U5 are not evaluable in W1: it carries no escalation sentinels')
        return w1.build_files(root)
    name = window['id']
    directory, pack = kit_path(name), pack_id(name)
    base = w1.build_files(root)
    original = json.loads(base[w1.KIT / 'collection_plan.json'])
    tree = _rewrite(json.loads(base[w1.KIT / 'plan_tree.json']), directory, pack)
    stages = [s for s in tree['stage_graph'] if '-episodes-' in s['stage_id']]
    files, members, orders = {}, [], [[], []]
    reference = None
    allocations = list(window['members']) + (escalation_allocations(window) if extra_sentinels else [])
    for allocation in allocations:
        ordinal = allocation['ordinal']
        repeat = {22: 2, 23: 3, 24: 4}.get(ordinal, 1)
        anchor = allocation['pool'] == 'anchor'
        src = original['members'][ordinal - 1 if anchor else 4]
        config = json.loads(base[Path(src['config_path'])])
        half = int(ordinal > 11)
        stage = stages[half]
        if not anchor:
            config['run_id'] = f'{pack}-e{ordinal:02}'
            spec = json.loads(config['workload_profile']['prompt_text'])
            spec.update(condition=allocation['condition'], seed=allocation['seed_index'])
            spec['task_kwargs']['task_pair'] = allocation['pair']
            spec['thermal']['window_reference'] = ({'role': 'capture'} if ordinal == 5 else
                {'role': 'consume', 'source_run_id': reference[0], 'source_config_sha256': reference[1]})
            config['workload_profile']['prompt_text'] = json.dumps(spec, sort_keys=True, separators=(',', ':'))
            config['run_metadata']['tags'] = [pack, 'non-claim', 'launch_lineage_required', 'align', 'align_episode',
                'align-model=' + w1.D_TAG, 'align-condition=' + allocation['condition'],
                'align-task=' + allocation['pair'], 'align-repeat=' + str(repeat),
                'align-stage=episodes-' + ('a' if half == 0 else 'b')]
        raw = base[Path(src['config_path'])] if anchor else raw_json(config)
        path = directory / 'stages' / ('episodes-a' if half == 0 else 'episodes-b') / (config['run_id'] + '.json')
        files[path] = raw
        if ordinal == 5:
            from joulewise.schemas import BenchmarkConfig
            reference = (config['run_id'], sha(w1.bundle_config_bytes(BenchmarkConfig.from_mapping(config))))
        row = deepcopy(tree['science'][0])
        row.update(run_id=config['run_id'], config=path.name, config_path=path.as_posix(), config_sha256=sha(raw),
                   index=len(orders[half]) + 1, block_index=len(orders[half]) + 1,
                   rep=repeat, module_id=pack + '-' + allocation['model_id'],
                   model_tag=allocation['model_id'] + '-mlx', stage_id=stage['stage_id'], pack_id=pack)
        orders[half].append(row)
        member = dict(ordinal=ordinal, role='anchor' if anchor else 'D', block='A' if anchor else 'D',
            pool_role=allocation['pool'], task_pair=allocation['pair'], condition=allocation['condition'],
            seed_index=allocation['seed_index'], expected_episode_seed=allocation['episode_seed'],
            expected_turn_seed_0=allocation['turn_seed_0'], model_id=allocation['model_id'],
            run_id=config['run_id'], config_path=path.as_posix(), config_sha256=sha(raw),
            spec=json.loads(config['workload_profile']['prompt_text']), stage_id=stage['stage_id'],
            repeat=repeat, is_replay=ordinal >= 22,
            held_out=allocation['pool'] in ('calibration', 'known_h', 'test'), non_claim=True,
            counts_toward=('calibration' if allocation['pool'] == 'calibration' else
                           'test' if allocation['pool'] == 'test' else 'none'),
            ac_powermode=original['runtime_requirements']['ac_powermode'])
        if ordinal >= 5:
            member['window_reference_role'] = ('capture_last_60s_idle_before_warmup' if ordinal == 5 else
                                             'consume_member_5_custody_via_WP15')
        if ordinal >= 22:
            member['replay_of'] = members[4]['run_id']
        if allocation.get('escalation_sentinel'):
            # R20: supplemental diagnostics. U4's W and W-1 df are unchanged, no held-out seed is used, and
            # the desk reports them descriptively (they join no identical-work group).
            member.update(supplemental=True, escalation_sentinel=allocation['escalation_sentinel'],
                          counts_toward='none')
        members.append(member)
    for stage, rows in zip(stages, orders):
        path = Path(rows[0]['config_path']).parent / 'order_manifest.json'
        raw = raw_json(dict(schema_version='joulewise.order_manifest.v1', manifest_id=stage['stage_id'],
                            planned_n_bundles=len(rows), executed_order=rows))
        files[path] = raw
        stage.update(expected_count=len(rows), input=dict(kind='manifest', path=path.as_posix(),
                     manifest_id=stage['stage_id'], sha256=sha(raw)))
        stage['launch']['commands'][0]['argv_template']['arguments'][0]['value'] = path.parent.as_posix()
    tree['science'] = [r for group in orders for r in group]
    tree['module_order'] = list(dict.fromkeys(r['module_id'] for r in tree['science']))
    plan = dict(schema_version='joulewise.align_v4.series_window.v1', plan_id=pack, window_id=name,
                series_manifest_sha256=sha(raw_json(manifest)), series_role=window['role'], non_claim=True,
                members=members, midpoint_after_ordinal=11,
                runtime_requirements=deepcopy(original['runtime_requirements']))
    if extra_sentinels:
        plan['extra_sentinels'] = extra_sentinels
    plan['runtime_requirements']['window_reference'].update(capture_run_id=reference[0],
                                                          capture_config_sha256=reference[1])
    w1.check_window_reference_roles(plan)
    files[directory / 'collection_plan.json'] = raw_json(plan)
    tree['plan'] = dict(path='collection_plan.json', plan_id=pack,
                       actual_sha256=sha(raw_json(plan)), declared_sha256=sha(raw_json(plan)))
    tree['generator'] = dict(path='scripts/align_v4_series.py', sha256=sha(Path(__file__).read_bytes()))
    chain.stage_plan(tree)
    files[directory / 'plan_tree.json'] = raw_json(tree)
    identity_files = {}
    identity_files[w1.KIT / 'plan_tree.json'] = files[directory / 'plan_tree.json']
    w1._identities(root, identity_files, members, w1.read_inputs(root))
    for path, raw in identity_files.items():
        if path.name != 'plan_tree.json':
            value = json.loads(raw)
            if path.name == 'identity_pins.json':
                value['derivation']['tree_path'] = str(directory / 'plan_tree.json')
            files[directory / path.relative_to(w1.KIT)] = raw_json(value)
    # Retain the admitted registration evidence; sizing/identity are role-specific.
    for path in (root / w1.KIT / 'registration').iterdir():
        target = directory / 'registration' / path.name
        if path.is_file() and path.suffix == '.json' and target not in files and path.name != 'sizing_b5.json':
            files[target] = path.read_bytes()
    files[directory / 'registration/sizing_b5.json'] = raw_json(derive_sizing(root, window, tree, plan,
                                                                          extra_sentinels=extra_sentinels))
    files[directory / 'registration/seed_manifest.json'] = raw_json(dict(
        schema='joulewise.align_v4.series_seeds.v1', window=name,
        series_manifest_sha256=plan['series_manifest_sha256'], seed_law='align-p4-v1',
        turn_seed_law='align-p4-turn-v1', allocations=window['members']))
    return files


def member_seconds(root, plan):
    """Per-member planning seconds (RUN_STATE 226 R15: D members at the largest W1 D member time).

    From the committed R1-filled W1 plan when it exists: anchors keep their W1
    member_s and every D member takes the largest W1 D member_s. Before R1 there
    is no W1 plan; the Amendment-1 planning allowances (anchors 3131.27/4, D
    1,800 s) are used and flagged, and native prepare refuses anyway (W1 not ready).
    """
    raw = w1.read_w1_plan_bytes(root)
    if raw is None:
        return ({str(m['ordinal']): (3131.27 / 4 if m['pool_role'] == 'anchor' else 1800) for m in plan['members']},
                ['sizing.planning_allowances_pending_r1_w1_plan'], None)
    rows = json.loads(raw)['align_v4']['members']
    anchors = {row['ordinal']: row['member_s'] for row in rows if row['role'] == 'anchor'}
    d_max = max(row['member_s'] for row in rows if row['role'] == 'D')
    return ({str(m['ordinal']): (anchors[m['ordinal']] if m['pool_role'] == 'anchor' else d_max)
             for m in plan['members']}, [], sha(raw))


def window_ceiling_s(extra_sentinels=0):
    """59,520 s for an ordinary D/C/T window; 62,400 s with the two escalation sentinels (R15)."""
    if extra_sentinels not in (0, 2):
        raise ValueError('a window carries 0 or 2 escalation sentinels')
    return ESCALATED_CEILING_S if extra_sentinels else D_CEILING_S


def derive_sizing(root, window, tree, plan, *, extra_sentinels=0):
    source = json.loads(w1.frozen(root, w1.ANCHOR_COMMIT, w1.SOURCE_KIT / 'registration/sizing_b5.json'))['packs']['align-pilot-v3']
    law = source['disk_member_law']
    seconds, flags, w1_plan_sha256 = member_seconds(root, plan)
    upper = {k: math.ceil(law['intercept'] + law['slope'] * v + law['largest_positive_residual'])
             for k, v in seconds.items()}
    scaffold = source['disk_derivation']['scaffold_bytes']
    span = math.ceil(w1.SCAFFOLD_S + math.fsum(seconds.values()))
    from joulewise.b6.plan_inputs import window_max_s
    maximum = window_max_s({'programmed_span_s': {'seconds': span}})
    ceiling = window_ceiling_s(extra_sentinels)
    if maximum > ceiling or max(seconds.values()) > w1.MEMBER_CAP_S:
        raise ValueError(f'{window["id"]}: window maximum {maximum} s exceeds the {ceiling} s ceiling '
                         'or a member exceeds 1,800 s; return to lead')
    pack = plan['plan_id']
    return dict(schema_version='joulewise.b5_sizing.v1', non_claim=True,
        sources=dict(series_manifest_sha256=plan['series_manifest_sha256'], window=window['id'],
                     disk_law_commit=w1.ANCHOR_COMMIT, w1_plan_sha256=w1_plan_sha256), packs={pack: dict(pack_id=pack, flags=flags,
        align_members=len(seconds), scaffold_members=sum(s['expected_count'] for s in tree['stage_graph']
            if s['kind'] == 'campaign_collection') - len(seconds),
        member_count=sum(s['expected_count'] for s in tree['stage_graph'] if s['kind'] == 'campaign_collection'),
        member_seconds=seconds, member_upper_bytes=upper, disk_member_law=law,
        programmed_span_s=span, window_max_s=maximum, window_ceiling_s=ceiling,
        T_stream_max_s=max(seconds.values()), estimated_footprint_bytes=2 * (sum(upper.values()) + scaffold),
        disk_derivation=dict(peak_copies=2, B_bytes=sum(upper.values()) + scaffold,
                             scaffold_bytes=scaffold, extra_wait_peak_bytes=0, fixed_retained_bytes=0))})


def generate(root, name, *, check=False, extra_sentinels=0):
    manifest = load(root)
    files = build_files(root, manifest, name, extra_sentinels=extra_sentinels)
    for path, raw in files.items():
        target = Path(root) / path
        if check:
            if target.read_bytes() != raw:
                raise ValueError('series kit drifted: ' + str(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    return selected(manifest, name)


RELEASE_FIELDS = ('ruling_id', 'text_sha256', 'resets', 'after_window', 'lead_signature')


def calibration_rows(manifest, history):
    """Validate the chronological series ledger; return (calibration rows, next window, previous window, releases).

    ``history`` holds attempt entries (``window_id``, ``attempt_id``, ``status``,
    ``captured_members``, ``eligible_benign``, ``evidence``; optionally
    ``desk_eligible_benign``, the desk's provisional counts, which the final
    adjudication may lower but never raise, and ``barred``, a STRUCTURAL bar of the
    window: ``u1_u3_fail`` or ``whole_window_capture_failure``) and ``lead_release``
    entries. F/T and known-H rows never count.

    R22-2: calibration is exactly 8 COUNTED windows over C1-C8 plus up to two
    pre-declared blind replacement windows, C9 and C10. A window barred for a
    structural reason (``barred``, or a zero-capture attempt whose retry is also a
    zero capture) is not counted and owes a replacement; C9 then C10 are armed after
    C8 only while fewer than 8 windows are counted and never on scores or counts.
    Only a zero-capture bar beyond the two replacements escalates, and only a
    lead_release naming the last attempt (resets ``zero_capture_escalation``,
    signed, text digest) resumes the series (RUN_STATE 226 R15).
    """
    cal_ids = [w['id'] for w in manifest['windows'] if w['role'] == 'calibration']
    # only the first REPLACEMENT_WINDOWS reserve windows are armable; C11 and C12 hold seeds, never an arm
    primary = cal_ids[:CALIBRATION_WINDOWS]
    replacements = cal_ids[CALIBRATION_WINDOWS:CALIBRATION_WINDOWS + REPLACEMENT_WINDOWS]
    test_ids = [w['id'] for w in manifest['windows'] if w['role'] == 'test']
    consumed, zeros = {}, {}
    rows, previous, releases = [], 'W1', []
    seen, last_attempt, escalated = set(), None, False

    def counted():
        return sum(v == 'counted' for k, v in consumed.items() if k in cal_ids)

    def barred():
        return sum(v == 'barred' for k, v in consumed.items() if k in cal_ids)

    def next_window():
        if barred() > REPLACEMENT_WINDOWS:
            return None                                   # 8 counted windows are out of reach
        for slot in primary:
            if slot not in consumed:
                return slot
        if counted() < CALIBRATION_WINDOWS:
            for slot in replacements:
                if slot not in consumed:
                    return slot
            return None
        for slot in test_ids:
            if slot not in consumed:
                return slot
        return None

    for attempt in history:
        if 'lead_release' in attempt:
            release = attempt['lead_release']
            if (set(attempt) != {'lead_release'} or not isinstance(release, dict) or set(release) != set(RELEASE_FIELDS)
                    or release['resets'] not in cadence.RULING_RESETS or not w1.valid_digest(release['text_sha256'])
                    or not isinstance(release['ruling_id'], str) or not release['ruling_id'].strip()
                    or not w1.valid_lead_signature(release['lead_signature'])):
                raise ValueError('lead_release needs ruling_id, text_sha256, resets, after_window, lead_signature')
            if not escalated or release['after_window'] != last_attempt:
                raise ValueError('lead_release must follow an escalation and name its last attempt')
            escalated = False
            releases.append(dict(release))
            continue
        if escalated:
            raise ValueError('zero-capture refusal beyond the replacement windows: escalate_to_lead')
        if next_window() != attempt['window_id']:
            raise ValueError('history skips/reorders a frozen window')
        if attempt['attempt_id'] in seen:
            raise ValueError('duplicate attempt id')
        seen.add(attempt['attempt_id'])
        window = selected(manifest, attempt['window_id'])
        row = dict(window=attempt['attempt_id'], status=attempt['status'], captured_members=attempt['captured_members'],
                   eligible_benign=attempt['eligible_benign'])
        if attempt.get('barred') is not None:
            row['barred'] = attempt['barred']
        # Validate even F/T rows with the count-only contract.
        cadence.calibration_stop([row])
        if (row['captured_members'] > len(window['members'])
                or sum(row['eligible_benign'].values()) > row['captured_members']
                or (not row['captured_members'] and row['status'] != 'final')):
            raise ValueError('impossible captured/eligible counts')
        if row.get('barred') and window['role'] != 'calibration':
            raise ValueError('only a calibration window can be barred and replaced')
        desk = attempt.get('desk_eligible_benign')
        if desk is not None and (not isinstance(desk, dict) or set(desk) != set(row['eligible_benign'])
                                 or any(row['eligible_benign'][k] > desk[k] for k in desk)):
            raise ValueError('final adjudication may lower the desk counts, never raise them')
        slot = attempt['window_id']
        if window['role'] == 'calibration':
            rows.append(row)
        elif any(row['eligible_benign'].values()):
            raise ValueError('F/T members cannot enter calibration')
        previous, last_attempt = slot, attempt['attempt_id']
        if row['captured_members']:
            consumed[slot] = 'barred' if row.get('barred') else 'counted'
        else:
            zeros[slot] = zeros.get(slot, 0) + 1
            if zeros[slot] >= 2:
                if window['role'] != 'calibration':
                    raise ValueError('two consecutive zero-capture refusals of a test window: escalate_to_lead')
                consumed[slot] = 'barred'                       # the retry is also a zero capture
                escalated = barred() > REPLACEMENT_WINDOWS
    if escalated:
        raise ValueError('zero-capture refusal beyond the replacement windows: escalate_to_lead')
    return rows, next_window(), previous, releases


def desk_row(manifest, window_id, members, u_pass):
    """The desk's provisional counts for one window: captures and ``desk_eligible_benign``.

    ``members``: one row per planned member ``{'run_id', 'captured', 'excluded'}``
    (captured: the run bundle exists; excluded: any harvest or X1-X8 exclusion).
    A calibrator counts when captured and not excluded. A U1-U3 FAIL of the D
    model window bars the whole window from the pool, though it still counts
    toward the eight (RUN_STATE 226 R15); a U verdict that is neither pass nor
    fail is flagged for the final adjudication. Counts only, never a score.
    """
    window = selected(manifest, window_id)
    rows = {row['run_id']: row for row in members}
    planned = {pack_id(window['id']) + f"-e{m['ordinal']:02}" if m['pool'] != 'anchor' else None: m
               for m in window['members']}
    planned.pop(None, None)
    # R20: the supplemental escalation sentinels (ordinals 23, 24) are diagnostics; they never count
    # as captured window members.
    supplemental = {pack_id(window['id']) + f'-e{ordinal:02}' for ordinal in (23, 24)}
    captured = sum(bool(row['captured']) for row in members if row['run_id'] not in supplemental)
    counts = dict.fromkeys(cadence.CAL_PAIRS, 0)
    for run_id, member in planned.items():
        row = rows.get(run_id)
        if member['pool'] == 'calibration' and row and row['captured'] and not row['excluded']:
            counts[PAIR_KEYS[member['pair']]] += 1
    flags, barred = [], None
    if window['role'] != 'calibration':
        counts = dict.fromkeys(cadence.CAL_PAIRS, 0)
    elif captured and u_pass is False:
        # R22-2: a U1-U3 FAIL is a STRUCTURAL bar. The window enters no pool, is not counted toward the eight
        # and is replaced by C9/C10 (superseding R15, where it still counted).
        counts = dict.fromkeys(cadence.CAL_PAIRS, 0)
        flags.append('u1_u3_failed:window_barred_and_replaced')
        barred = 'u1_u3_fail'
    elif captured and u_pass is None:
        flags.append('u1_u3_not_pass_or_fail:final_adjudication_decides')
    return {'window_id': window['id'], 'captured_members': captured, 'desk_eligible_benign': counts,
            'status': 'provisional', 'flags': flags, **({'barred': barred} if barred else {})}


def _attempts(history):
    return [entry for entry in history if 'lead_release' not in entry]


def slot_of(window_id):
    """The frozen slot of an attempt id: ``C3#2`` (a validated zero-capture retry) is slot ``C3``.

    Only the registered ``<slot>#<k>`` form is normalized; anything else is returned unchanged and
    therefore fails to match a slot. Full attempt ids stay in records, chain and ruling references.
    """
    return cadence.slot_of(window_id)


def bind_packet(root, name, packet, *, authenticated_by_rebuild=False):
    """Bind a packet to the frozen series window.

    ``authenticated_by_rebuild``: the packet is the ARM's OWN rebuild (a supplied packet is only a
    pointer); its history and counts were derived from hash-chained, authenticated records, so the
    embedded-evidence receipts of a hand-produced packet are not required (and not trusted either way).
    """
    manifest = load(root)
    target = selected(manifest, name)
    if (packet.get('series_manifest_sha256') != sha((Path(root) / MANIFEST).read_bytes())
            or packet.get('next_window_id') != target['id']):
        raise ValueError('triage packet does not bind the frozen series/window')
    history = packet.get('series_history')
    if not isinstance(history, list):
        raise ValueError('series triage needs chronological history')
    rows, next_id, previous, releases = calibration_rows(manifest, history)
    if target['id'] != 'W1' and rows:
        released = [r for r in releases if r['after_window'] in {row['window'] for row in rows}]
        if cadence.calibration_stop(rows, released)['decision'] == 'insufficient_calibration':
            raise ValueError('calibration_stop: insufficient_calibration')
    if target['id'] == 'W1':
        if history or packet.get('previous_window') != 'R1':
            raise ValueError('W1 must follow R1 with no series history')
    elif target['id'] != next_id or slot_of(packet.get('previous_window')) != previous:
        raise ValueError(f'triage does not arm the next frozen window ({next_id})')
    if 'previous_window_is_w1' in packet and packet['previous_window_is_w1'] is not (previous == 'W1' and target['id'] != 'W1'):
        raise ValueError('previous W1 flag disagrees with series history')
    role = None if target['id'] == 'W1' else ('test' if target['role'] == 'test' else 'calibration')
    if packet.get('next_window_role') != role or packet.get('calibration_windows') != rows:
        raise ValueError('triage role/counts disagree with frozen series history')
    cal_attempts = {r['window'] for r in rows}
    if packet.get('lead_rulings', []) != [r for r in releases if r['after_window'] in cal_attempts]:
        raise ValueError('lead_rulings disagree with the lead_release entries of the series history')
    # R216 final-eligibility fence starts at the sixth calibration arm (kept by R15).
    if target['role'] == 'calibration' and int(target['id'][1:]) >= 6 and any(r['status'] != 'final' for r in rows):
        raise ValueError('C6 onward requires final eligibility for prior calibration windows')
    if not authenticated_by_rebuild:
        for check in packet.get('checks', {}).values():
            if evidence(check.get('evidence')) != check.get('status'):
                raise ValueError('triage status disagrees with bound evidence')
        for attempt in _attempts(history):
            expected = {k: attempt[k] for k in ('window_id', 'attempt_id', 'status', 'captured_members', 'eligible_benign',
                                                'barred') if k in attempt}
            if evidence(attempt.get('evidence')) != expected:
                raise ValueError('history counts disagree with bound eligibility receipt')
    if target['role'] == 'test':
        stop = cadence.calibration_stop(rows, packet.get('lead_rulings', []))
        if stop['decision'] != 'calibration_complete':
            raise ValueError('calibration_stop: ' + stop['decision'])
        admission = json.loads((Path(root) / ADMISSION).read_bytes())
        freeze = evidence((admission.get('evidence') or {}).get('test_threshold_freeze'))
        if (not isinstance(freeze, dict) or freeze.get('status') != 'pass'
                or freeze.get('manifest_sha256') != packet['series_manifest_sha256']
                or freeze.get('calibration_rows_sha256') != sha(raw_json(rows))):
            raise ValueError('test requires thresholds frozen against these exact final C1-C8 counts')
    return packet


def _commit_exists(root, commit):
    import re
    import subprocess
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        return False
    try:
        return subprocess.run(['git', 'cat-file', '-e', f'{commit}^{{commit}}'], cwd=root,
                              capture_output=True, timeout=20, check=False).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def make_packet(root, name, history, checks, *, record_commit, last_desk_passed_artifact_set_sha256,
                valid_until_epoch_s, now_epoch_s, record_path='staging/window-record.json',
                record_sha256='e' * 64, commit_check=None, record_check=None):
    """A SYNTHETIC/dev R12 packet for ``name``: derived from the ledger, evidence bytes embedded.

    Production arms never trust a supplied packet: the arm rebuilds it with
    ``align_v4_next_arm_packet.build_packet`` from the hash-chained records and binds its own build
    (``bind_packet(..., authenticated_by_rebuild=True)``). This producer is a dev/test aid whose
    pre-check is advisory; it needs an explicit expiry and the arm clock because both are mandatory.

    The W1-flag and code/config-changed flags are DERIVED by the arm
    (v4_cadence); they are not written here. ``record_commit`` is the previous
    record's commit; ``last_desk_passed_artifact_set_sha256`` the bound-artifact
    digest recorded when the last full desk passed.
    """
    from joulewise.align.apple import v4_registration
    history, checks = deepcopy(history), deepcopy(checks)
    manifest = load(root)
    target = selected(manifest, name)
    rows, _, previous, releases = calibration_rows(manifest, history)
    cal_attempts = {r['window'] for r in rows}
    packet = dict(schema=cadence.TRIAGE_SCHEMA, series_manifest_sha256=sha((Path(root) / MANIFEST).read_bytes()),
        next_window_id=target['id'], series_history=history, previous_window='R1' if name == 'W1' else previous,
        record_commit=record_commit, record_path=record_path, record_sha256=record_sha256,
        valid_until_epoch_s=valid_until_epoch_s,
        last_desk_passed_artifact_set_sha256=last_desk_passed_artifact_set_sha256,
        next_window_role=None if name == 'W1' else ('test' if target['role'] == 'test' else 'calibration'),
        calibration_windows=rows, lead_rulings=[r for r in releases if r['after_window'] in cal_attempts],
        checks=checks)
    bind_packet(root, name, packet)
    identity = {'artifact_set_sha256': v4_registration.artifact_set_digest(root),
                'record_commit_exists': (commit_check or _commit_exists)(root, record_commit),
                'record_bound': bool((record_check or (lambda root, packet: True))(root, packet))}
    result = cadence.next_arm_triage(
        packet, dict.fromkeys(('series_powermode', 'external_volume', 'charging_battery', 'meter_reader_live'), True),
        identity, now_epoch_s=now_epoch_s)
    if not result['admitted']:
        raise ValueError('packet not ready: ' + '; '.join(result['reasons']))
    for reference in ([check['evidence'] for check in checks.values()]
                      + [attempt['evidence'] for attempt in _attempts(history)]):
        evidence(reference)
        if 'content_utf8' not in reference:
            reference['content_utf8'] = Path(reference['path']).read_bytes().decode('utf-8')
        evidence(reference)
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('candidate')
    p.add_argument('--out', type=Path, required=True)
    for command in ('materialize', 'packet'):
        p = sub.add_parser(command)
        p.add_argument('--root', type=Path, default=ROOT)
        p.add_argument('--window-id', required=True)
        if command == 'materialize':
            p.add_argument('--check', action='store_true')
            p.add_argument('--extra-sentinels', type=int, default=0, choices=(0, 2),
                           help='R20: append the two supplemental escalation sentinels (ordinals 23, 24) '
                                'after a U4/U5-inconclusive window; ceiling 62,400 s')
        else:
            p.add_argument('--sources', type=Path, required=True,
                           help='JSON: history, checks, record_commit, last_desk_passed_artifact_set_sha256')
            p.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'candidate':
        args.out.write_bytes(raw_json(candidate()))
    elif args.command == 'materialize':
        generate(args.root, args.window_id, check=args.check, extra_sentinels=args.extra_sentinels)
    else:
        sources = json.loads(args.sources.read_bytes())
        args.out.write_bytes(raw_json(make_packet(
            args.root, args.window_id, sources['history'], sources['checks'], record_commit=sources['record_commit'],
            last_desk_passed_artifact_set_sha256=sources['last_desk_passed_artifact_set_sha256'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
