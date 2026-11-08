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


def candidate(*, d_mapping='separate_fit', test_windows=3):
    """Prospective proposal, including BOTH pairs/conditions/seeds in every slot.

    Separate D fit windows avoid assigning a calibrator to fit. The alias option
    instead names D1=C1 etc.; its independent fit source must be admitted.
    """
    if d_mapping not in ('separate_fit', 'alias_calibration') or test_windows not in (3, 6):
        raise ValueError('choose separate_fit|alias_calibration and 3|6 test windows')
    selection = []
    for ordinal, (role, pair, condition, index) in enumerate(w1.ROSTER, 1):
        model = w1.D_TAG if role == 'D' else 'qwen3-30b-a3b'
        seed = episode_seed(model, 'thinking_on', 'shade/' + pair, index)
        selection.append(dict(ordinal=ordinal, pool='selection', role=role, pair=pair,
            condition=condition, seed_index=index, model_id=model, episode_seed=seed,
            turn_seed_0=turn_seed(seed, 0)))
    windows = [{'id': 'W1', 'role': 'selection', 'aliases': [], 'members': selection}]
    groups = ([('D', 'fit', 3, 101)] if d_mapping == 'separate_fit' else [])
    groups += [('C', 'calibration', 8, 2), ('T', 'test', test_windows, 201)]
    for prefix, role, count, start in groups:
        for number in range(1, count + 1):
            indices = list(range(start + 7 * (number - 1), start + 7 * number))
            rows = []
            for pair, condition in zip((PAIRS[0], PAIRS[1], PAIRS[0], PAIRS[1]),
                                       ('benign', 'sabotage', 'sabotage', 'benign')):
                rows.append(dict(pool='anchor', pair=pair, condition=condition, seed_index=1))
            rows.append(dict(pool='sentinel', pair=PAIRS[0], condition='benign', seed_index=1))
            for index in indices:
                for pair in PAIRS:
                    rows.append(dict(pool=role, pair=pair, condition='benign', seed_index=index))
            for pair in PAIRS:
                rows.append(dict(pool=role, pair=pair, condition='sabotage', seed_index=indices[0]))
            rows.append(deepcopy(rows[4]))
            for ordinal, row in enumerate(rows, 1):
                model = 'qwen3-30b-a3b' if row['pool'] == 'anchor' else w1.D_TAG
                seed = episode_seed(model, 'thinking_on', 'shade/' + row['pair'], row['seed_index'])
                row.update(ordinal=ordinal, model_id=model, episode_seed=seed,
                           turn_seed_0=turn_seed(seed, 0))
            name = prefix + str(number)
            aliases = ['D' + str(number)] if prefix == 'C' and number <= 3 and d_mapping == 'alias_calibration' else []
            windows.append(dict(id=name, role=role, aliases=aliases, midpoint_after_ordinal=11, members=rows))
    return dict(schema=SCHEMA, status='PROPOSAL_REQUIRES_LEAD_ADMISSION', d_mapping=d_mapping,
                test_windows=test_windows, order=[r['id'] for r in windows], windows=windows,
                calibration=dict(counted_windows=8, benign_per_pair_per_window=7,
                                 minimum_eligible_per_pair=39, replacements=0),
                sentinel=dict(source='W1:5', late_replay_of=5, extra_on_inconclusive=2),
                seed_law='align-p4-v1', turn_seed_law='align-p4-turn-v1',
                test_shape='v4: 14 benign + 2 sabotage; no v5 attacks or physical controls',
                open_rulings=['D/F/C mapping and independent fit/scorer contract', '3 vs 6 test windows and shape',
                              'C/T/F seed ranges and within-window condition seed reuse',
                              'W1 sentinel/cohort clearance; U4/U5 extra-sentinel disposition',
                              'R13/R14 scorer validity, dependence and threshold freeze'])


def validate(manifest):
    # Accept only the two fully specified designs supported by this builder;
    # changing a slot requires a reviewed builder change, never a silent edit.
    if not isinstance(manifest, dict) or manifest.get('schema') != SCHEMA:
        raise ValueError('missing series manifest')
    expected = candidate(d_mapping=manifest.get('d_mapping'), test_windows=manifest.get('test_windows'))
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


def build_files(root, manifest, name):
    """Materialize an actual stage graph, manifests, configs, pins and sizing.

    No plausible R1 default is introduced. Pending W1 inputs remain pending;
    native prepare always runs require_w1_ready and exact-byte admission first.
    """
    root = Path(root)
    window = selected(manifest, name)
    if window['id'] == 'W1':
        return w1.build_files(root)
    name = window['id']
    directory, pack = kit_path(name), pack_id(name)
    base = w1.build_files(root)
    original = json.loads(base[w1.KIT / 'collection_plan.json'])
    tree = _rewrite(json.loads(base[w1.KIT / 'plan_tree.json']), directory, pack)
    stages = [s for s in tree['stage_graph'] if '-episodes-' in s['stage_id']]
    files, members, orders = {}, [], [[], []]
    reference = None
    for allocation in window['members']:
        ordinal = allocation['ordinal']
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
                'align-task=' + allocation['pair'], 'align-repeat=' + ('2' if ordinal == 22 else '1'),
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
                   rep=2 if ordinal == 22 else 1, module_id=pack + '-' + allocation['model_id'],
                   model_tag=allocation['model_id'] + '-mlx', stage_id=stage['stage_id'], pack_id=pack)
        orders[half].append(row)
        member = dict(ordinal=ordinal, role='anchor' if anchor else 'D', block='A' if anchor else 'D',
            pool_role=allocation['pool'], task_pair=allocation['pair'], condition=allocation['condition'],
            seed_index=allocation['seed_index'], expected_episode_seed=allocation['episode_seed'],
            expected_turn_seed_0=allocation['turn_seed_0'], model_id=allocation['model_id'],
            run_id=config['run_id'], config_path=path.as_posix(), config_sha256=sha(raw),
            spec=json.loads(config['workload_profile']['prompt_text']), stage_id=stage['stage_id'],
            repeat=2 if ordinal == 22 else 1, is_replay=ordinal == 22,
            held_out=allocation['pool'] in ('calibration', 'test'), non_claim=True,
            ac_powermode=original['runtime_requirements']['ac_powermode'])
        if ordinal >= 5:
            member['window_reference_role'] = ('capture_last_60s_idle_before_warmup' if ordinal == 5 else
                                             'consume_member_5_custody_via_WP15')
        if ordinal == 22:
            member['replay_of'] = members[4]['run_id']
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
    files[directory / 'registration/sizing_b5.json'] = raw_json(derive_sizing(root, window, tree, plan))
    files[directory / 'registration/seed_manifest.json'] = raw_json(dict(
        schema='joulewise.align_v4.series_seeds.v1', window=name,
        series_manifest_sha256=plan['series_manifest_sha256'], seed_law='align-p4-v1',
        turn_seed_law='align-p4-turn-v1', allocations=window['members']))
    return files


def derive_sizing(root, window, tree, plan):
    source = json.loads(w1.frozen(root, w1.ANCHOR_COMMIT, w1.SOURCE_KIT / 'registration/sizing_b5.json'))['packs']['align-pilot-v3']
    law = source['disk_member_law']
    # Unchanged 1,800 s D member cap, historical anchor planning law; no shortened idle/scaffold.
    seconds = {str(m['ordinal']): (3131.27 / 4 if m['pool_role'] == 'anchor' else 1800)
               for m in plan['members']}
    upper = {k: math.ceil(law['intercept'] + law['slope'] * v + law['largest_positive_residual'])
             for k, v in seconds.items()}
    scaffold = source['disk_derivation']['scaffold_bytes']
    span = math.ceil(w1.SCAFFOLD_S + sum(seconds.values()))
    from joulewise.b6.plan_inputs import window_max_s
    pack = plan['plan_id']
    return dict(schema_version='joulewise.b5_sizing.v1', non_claim=True,
        sources=dict(series_manifest_sha256=plan['series_manifest_sha256'], window=window['id'],
                     disk_law_commit=w1.ANCHOR_COMMIT), packs={pack: dict(pack_id=pack, flags=[],
        align_members=len(seconds), scaffold_members=sum(s['expected_count'] for s in tree['stage_graph']
            if s['kind'] == 'campaign_collection') - len(seconds),
        member_count=sum(s['expected_count'] for s in tree['stage_graph'] if s['kind'] == 'campaign_collection'),
        member_seconds=seconds, member_upper_bytes=upper, disk_member_law=law,
        programmed_span_s=span, window_max_s=window_max_s({'programmed_span_s': {'seconds': span}}),
        T_stream_max_s=1800, estimated_footprint_bytes=2 * (sum(upper.values()) + scaffold),
        disk_derivation=dict(peak_copies=2, B_bytes=sum(upper.values()) + scaffold,
                             scaffold_bytes=scaffold, extra_wait_peak_bytes=0, fixed_retained_bytes=0))})


def generate(root, name, *, check=False):
    manifest = load(root)
    files = build_files(root, manifest, name)
    for path, raw in files.items():
        target = Path(root) / path
        if check:
            if target.read_bytes() != raw:
                raise ValueError('series kit drifted: ' + str(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    return selected(manifest, name)


def calibration_rows(manifest, history):
    """Validate chronological attempts, zero-capture retry, disjoint roles and finality."""
    order = manifest['order'][1:]
    cursor, rows, previous, trailing_zero = 0, [], 'W1', 0
    seen = set()
    for attempt in history:
        if cursor >= len(order) or attempt['window_id'] != order[cursor]:
            raise ValueError('history skips/reorders a frozen window')
        if attempt['attempt_id'] in seen:
            raise ValueError('duplicate attempt id')
        seen.add(attempt['attempt_id'])
        window = selected(manifest, attempt['window_id'])
        row = dict(window=attempt['attempt_id'], status=attempt['status'], captured_members=attempt['captured_members'],
                   eligible_benign=attempt['eligible_benign'])
        # Validate even F/T rows with the count-only contract.
        cadence.calibration_stop([row])
        if (row['captured_members'] > len(window['members'])
                or sum(row['eligible_benign'].values()) > row['captured_members']
                or (not row['captured_members'] and row['status'] != 'final')):
            raise ValueError('impossible captured/eligible counts')
        trailing_zero = 0 if row['captured_members'] else trailing_zero + 1
        if trailing_zero >= 2:
            raise ValueError('two consecutive zero-capture refusals: escalate_to_lead')
        if window['role'] == 'calibration':
            rows.append(row)
        elif any(row['eligible_benign'].values()):
            raise ValueError('F/T members cannot enter calibration')
        previous = attempt['attempt_id']
        if row['captured_members']:
            cursor += 1
    return rows, (order[cursor] if cursor < len(order) else None), previous


def bind_packet(root, name, packet):
    manifest = load(root)
    target = selected(manifest, name)
    if (packet.get('series_manifest_sha256') != sha((Path(root) / MANIFEST).read_bytes())
            or packet.get('next_window_id') != target['id']):
        raise ValueError('triage packet does not bind the frozen series/window')
    history = packet.get('series_history')
    if not isinstance(history, list):
        raise ValueError('series triage needs chronological history')
    rows, next_id, previous = calibration_rows(manifest, history)
    if target['id'] == 'W1':
        if history or packet.get('previous_window') != 'R1':
            raise ValueError('W1 must follow R1 with no series history')
    elif target['id'] != next_id or packet.get('previous_window') != previous:
        raise ValueError('triage does not arm the next frozen window')
    if packet.get('previous_window_is_w1') is not (target['id'] != 'W1' and not history):
        raise ValueError('previous W1 flag disagrees with series history')
    role = None if target['id'] == 'W1' else ('test' if target['role'] == 'test' else 'calibration')
    if packet.get('next_window_role') != role or packet.get('calibration_windows') != rows:
        raise ValueError('triage role/counts disagree with frozen series history')
    # R216 final-eligibility fence starts at the sixth calibration arm.
    if target['role'] == 'calibration' and int(target['id'][1:]) >= 6 and any(r['status'] != 'final' for r in rows):
        raise ValueError('C6 onward requires final eligibility for prior calibration windows')
    for check in packet.get('checks', {}).values():
        if evidence(check.get('evidence')) != check.get('status'):
            raise ValueError('triage status disagrees with bound evidence')
    for attempt in history:
        expected = {k: attempt[k] for k in ('window_id', 'attempt_id', 'status', 'captured_members', 'eligible_benign')}
        if evidence(attempt.get('evidence')) != expected:
            raise ValueError('history counts disagree with bound eligibility receipt')
    if target['role'] == 'test':
        stop = cadence.calibration_stop(rows)
        if stop['decision'] != 'calibration_complete':
            raise ValueError('calibration_stop: ' + stop['decision'])
        admission = json.loads((Path(root) / ADMISSION).read_bytes())
        freeze = evidence((admission.get('evidence') or {}).get('test_threshold_freeze'))
        if (not isinstance(freeze, dict) or freeze.get('status') != 'pass'
                or freeze.get('manifest_sha256') != packet['series_manifest_sha256']
                or freeze.get('calibration_rows_sha256') != sha(raw_json(rows))):
            raise ValueError('test requires thresholds frozen against these exact final C1-C8 counts')
    return packet


def make_packet(root, name, history, checks, *, code_or_config_changed):
    history, checks = deepcopy(history), deepcopy(checks)
    manifest = load(root)
    target = selected(manifest, name)
    rows, _, previous = calibration_rows(manifest, history)
    packet = dict(schema=cadence.TRIAGE_SCHEMA, series_manifest_sha256=sha((Path(root) / MANIFEST).read_bytes()),
        next_window_id=target['id'], series_history=history, previous_window='R1' if name == 'W1' else previous,
        previous_window_is_w1=target['id'] != 'W1' and not history,
        code_or_config_changed=code_or_config_changed,
        next_window_role=None if name == 'W1' else ('test' if target['role'] == 'test' else 'calibration'),
        calibration_windows=rows, checks=checks)
    bind_packet(root, name, packet)
    result = cadence.next_arm_triage(packet, dict.fromkeys(('series_powermode', 'external_volume', 'charging_battery'), True))
    if not result['admitted']:
        raise ValueError('packet not ready: ' + '; '.join(result['reasons']))
    for reference in ([check['evidence'] for check in checks.values()]
                      + [attempt['evidence'] for attempt in history]):
        evidence(reference)
        if 'content_utf8' not in reference:
            reference['content_utf8'] = Path(reference['path']).read_bytes().decode('utf-8')
        evidence(reference)
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('candidate')
    p.add_argument('--d-mapping', choices=('separate_fit', 'alias_calibration'), default='separate_fit')
    p.add_argument('--test-windows', type=int, choices=(3, 6), default=3)
    p.add_argument('--out', type=Path, required=True)
    for command in ('materialize', 'packet'):
        p = sub.add_parser(command)
        p.add_argument('--root', type=Path, default=ROOT)
        p.add_argument('--window-id', required=True)
        if command == 'materialize':
            p.add_argument('--check', action='store_true')
        else:
            p.add_argument('--sources', type=Path, required=True, help='JSON: history, checks, code_or_config_changed')
            p.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'candidate':
        args.out.write_bytes(raw_json(candidate(d_mapping=args.d_mapping, test_windows=args.test_windows)))
    elif args.command == 'materialize':
        generate(args.root, args.window_id, check=args.check)
    else:
        sources = json.loads(args.sources.read_bytes())
        args.out.write_bytes(raw_json(make_packet(args.root, args.window_id, sources['history'], sources['checks'],
                                                code_or_config_changed=sources['code_or_config_changed'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
