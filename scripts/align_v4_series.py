#!/usr/bin/env python3
"""Build the ALIGN v4 series after W1: frozen manifest + one armable kit per window.

Opus build (RUN_STATE 220). Generates, without model or data access:

* ``configs/campaigns/align_v4_series/series_manifest.json``: the frozen order,
  roles, seeds and pairs/conditions of C1-C8 (D1-D8) and the tests
  (``joulewise.align.apple.v4_series.build_manifest``);
* one kit per C/T window under ``configs/campaigns/align_v4_series/<w>/`` in
  the W1 kit's layout (collection_plan.json, plan_tree.json, stages/, and the
  registration identity files), so the window arms through the same session
  route as W1: ``align_v4_session.py prepare --window <W>`` ->
  shared prepare/plan writer -> ``install`` (R12 triage + series binding) ->
  shared installer -> HAZARD_PACK ``run_night``;
* ``registration/sizing_b5.json`` per window once R1 has filled the W1 plan.

D-class member configs are built exactly like W1's D members (the same frozen
anchor-1 clone, D model, sampler, effort, B_D, T_dead and thermal policy from
registration/inputs.json); only run id, pair, condition, seed and the window
reference role differ. Anchors keep their original bytes. ``--check`` fails on
any drift. ``next`` and ``packet`` drive the cadence from the series ledger.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import align_v4_kit as kit  # noqa: E402
from scripts.align_pilot_kit import raw_json, sha  # noqa: E402
from joulewise.align.apple import km003c, v4_series as series  # noqa: E402
from joulewise.align.apple.sampling import turn_seed  # noqa: E402
from joulewise.b5 import chain  # noqa: E402

SERIES_KIT = Path(series.SERIES_KIT)
MANIFEST_PATH = SERIES_KIT / 'series_manifest.json'
# The frozen test-cohort shape. Changing it is a lead ruling (DCT-SERIES-opus.md R-2).
TEST_SHAPE = series.DEFAULT_TEST_SHAPE


def _rewrite(value, kit_dir, pack):
    if isinstance(value, str):
        return value.replace(str(kit.SOURCE_KIT), str(kit_dir)).replace('align-pilot-v3', pack).replace(
            'align_pilot_v3', pack.replace('-', '_'))
    if isinstance(value, list):
        return [_rewrite(v, kit_dir, pack) for v in value]
    if isinstance(value, dict):
        return {k: _rewrite(v, kit_dir, pack) for k, v in value.items()}
    return value


def _d_config(anchor, spec_row, pack, inputs, reference):
    """A D member config built exactly as align_v4_kit builds W1's D members."""
    config = deepcopy(anchor)
    config['run_id'] = spec_row['run_id']
    config['hardware_target']['notes'] = (f'PROVISIONAL ALIGN v4 series {pack} non-claim skeleton; '
                                          'not admitted for execution.')
    spec = json.loads(config['workload_profile']['prompt_text'])
    spec.pop('max_episode_seconds', None)
    spec.update(condition=spec_row['condition'], seed=spec_row['seed_index'], warmup_condition='benign')
    spec['task_kwargs'] = {**spec['task_kwargs'], 'task_pair': spec_row['task_pair']}
    config['model'].update(name='Qwen3.8-27B-8bit', family='qwen3_5', source=kit.D_SOURCE, revision=kit.D_REVISION)
    config['quantization'] = {'name': 'int8', 'bits': 8, 'group_size': 64}
    spec.update(sampler=kit.D_SAMPLER, temperature=1.0, assistant_history='reasoning_content',
                chat_template_kwargs={'reasoning_effort': inputs['R0']['reasoning_effort']},
                max_episode_decode_tokens=inputs['R1']['B_D'], deadman_s=inputs['R1']['T_dead'],
                hybrid_checkpoint_limit=0,
                thermal=kit.thermal_policy(inputs, heavy=True, per_turn=True, window_reference=reference))
    config['workload_profile']['prompt_text'] = json.dumps(spec, sort_keys=True, separators=(',', ':'),
                                                           allow_nan=False)
    config['run_metadata']['tags'] = [
        pack, 'non-claim', 'launch_lineage_required', 'align', 'align_episode', 'align-model=' + kit.D_TAG,
        'align-condition=' + spec_row['condition'], 'align-task=' + spec_row['task_pair'],
        'align-repeat=' + ('2' if spec_row['series_role'] == 'sentinel' else '1'),
        'align-stage=episodes-' + spec_row['stage'], 'align-series-role=' + spec_row['series_role']]
    return config


def build_window_files(root, manifest, window_id, inputs, r1_slots, files):
    from joulewise.schemas import BenchmarkConfig
    spec = series.window(manifest, window_id)
    kit_dir, pack = Path(spec['kit']), spec['pack_id']
    ac_powermode = r1_slots.get('ac_powermode')
    tree = _rewrite(json.loads(kit.frozen(root, kit.ANCHOR_COMMIT, kit.SOURCE_KIT / 'plan_tree.json')), kit_dir, pack)
    stages = [s for s in tree['stage_graph'] if '-episodes-' in s['stage_id']]
    anchors = {}
    for ordinal in range(1, 5):
        path = kit.SOURCE_KIT / 'stages/episodes-a' / f'align-pilot-v3-episodes-a-e{ordinal:02}.json'
        anchors[ordinal] = (path, kit.frozen(root, kit.ANCHOR_COMMIT, path))
    rows_by_stage, members, receipts = [[], []], [], []
    capture = None
    for row in spec['members']:
        half = 0 if row['stage'] == 'a' else 1
        directory = kit_dir / 'stages' / ('episodes-a' if half == 0 else 'episodes-b')
        if row['series_role'] == 'anchor':
            source_path, raw = anchors[row['ordinal']]
            config = json.loads(raw)
            if config['run_id'] != row['run_id']:
                raise ValueError(f'{window_id} anchor {row["ordinal"]} run id drifted')
            filename = source_path.name
            receipts.append(dict(ordinal=row['ordinal'], commit=kit.ANCHOR_COMMIT, path=source_path.as_posix(),
                                 sha256=sha(raw)))
        else:
            if row['window_reference'] == 'capture':
                reference = {'role': 'capture'}
            else:
                reference = {'role': 'consume', 'source_run_id': capture[0], 'source_config_sha256': capture[1]}
            config = _d_config(json.loads(anchors[1][1]), row, pack, inputs, reference)
            raw = raw_json(config)
            if row['window_reference'] == 'capture':
                capture = (config['run_id'], sha(kit.bundle_config_bytes(BenchmarkConfig.from_mapping(config))))
            filename = config['run_id'] + '.json'
        path = directory / filename
        files[path] = raw
        member_spec = json.loads(config['workload_profile']['prompt_text'])
        replay = row['series_role'] == 'sentinel'
        order_row = dict(ac_powermode=ac_powermode, run_id=config['run_id'], config=filename,
                         config_path=path.as_posix(), config_sha256=sha(raw), index=len(rows_by_stage[half]) + 1,
                         rep=2 if replay else 1, role='absolute_repeat', block_id=None,
                         block_index=len(rows_by_stage[half]) + 1, position=None, position_in_block=1, arm=None,
                         model_tag=row['model_id'] + '-mlx', workload='align_episode',
                         module_id=pack + '-' + row['model_id'], pack_id=pack)
        rows_by_stage[half].append(order_row)
        member = dict(ac_powermode=ac_powermode, ordinal=row['ordinal'], run_id=config['run_id'],
                      stage_id=stages[half]['stage_id'], role=row['role'], series_role=row['series_role'],
                      block='A' if row['role'] == 'anchor' else 'D', model_id=row['model_id'],
                      task_pair=row['task_pair'], condition=row['condition'], seed_index=row['seed_index'],
                      expected_episode_seed=row['expected_episode_seed'],
                      expected_turn_seed_0=turn_seed(row['expected_episode_seed'], 0),
                      config_path=path.as_posix(), config_sha256=sha(raw), spec=member_spec,
                      repeat=2 if replay else 1, is_replay=replay, non_claim=True, held_out=row['held_out'],
                      counts_toward=row['counts_toward'], window=window_id)
        if replay:
            member.update(replay_of=row['replay_of'], replay_of_window=row['replay_of_window'])
        if row['ordinal'] == kit.WINDOW_REFERENCE_CAPTURE_ORDINAL:
            member['window_reference_role'] = 'capture_last_60s_idle_before_warmup'
        elif row['ordinal'] > kit.WINDOW_REFERENCE_CAPTURE_ORDINAL:
            member['window_reference_role'] = 'consume_member_5_custody_via_WP15'
        members.append(member)
    for stage, rows in zip(stages, rows_by_stage, strict=True):
        manifest_path = Path(rows[0]['config_path']).parent / 'order_manifest.json'
        raw = raw_json(dict(schema_version='joulewise.order_manifest.v1', manifest_id=stage['stage_id'],
                            planned_n_bundles=len(rows), executed_order=rows))
        files[manifest_path] = raw
        stage.update(expected_count=len(rows), input=dict(kind='manifest', path=manifest_path.as_posix(),
                     manifest_id=stage['stage_id'], sha256=sha(raw)))
        stage['launch']['commands'][0]['argv_template']['arguments'][0]['value'] = manifest_path.parent.as_posix()
    tree['science'] = [dict(row, stage_id=stage['stage_id'])
                       for stage, rows in zip(stages, rows_by_stage, strict=True) for row in rows]
    tree['module_order'] = list(dict.fromkeys(row['module_id'] for row in tree['science']))
    pending = kit.pending_inputs(inputs)
    plan = dict(schema_version='joulewise.align_v4.v1', plan_id=pack, non_claim=True,
                status='PROVISIONAL_SKELETON' if pending else 'FOR_LEAD_REVIEW', pending_inputs=pending,
                protocol='docs/align/pilot_protocol_v4.md', series_window=window_id, series_role=spec['role'],
                series_alias=spec.get('alias'), series_manifest=MANIFEST_PATH.as_posix(),
                series_manifest_sha256=series.manifest_sha256(manifest), members=members,
                midpoint_after_ordinal=spec['midpoint_after_ordinal'], seed_law='align-p4-v1',
                turn_seed_law='align-p4-turn-v1', seed_bits=64, source_receipts=receipts,
                runtime_requirements=dict(
                    km003c=km003c.REQUIREMENT.copy(), ac_powermode=ac_powermode,
                    D_tools='family-validated XML via qwen3_5', presence_penalty=0,
                    window_reference=dict(capture_ordinal=kit.WINDOW_REFERENCE_CAPTURE_ORDINAL,
                                          capture_run_id=capture[0], capture_config_sha256=capture[1],
                                          rule='the early sentinel (ordinal 5) captures its last 60 s of idle '
                                               'before warmup; every later D member consumes it'),
                    w1_launcher='per-member configs via the plan_tree stage commands (the specs carry the roles)'))
    kit.check_window_reference_roles(plan)
    files[kit_dir / 'collection_plan.json'] = raw_json(plan)
    tree.update(generator=dict(path='scripts/align_v4_series.py', sha256=sha((ROOT / 'scripts/align_v4_series.py').read_bytes()),
                               member_builder='scripts/align_v4_kit.py',
                               member_builder_sha256=sha((ROOT / 'scripts/align_v4_kit.py').read_bytes())),
                draft_status=plan['status'], arm_attachments={})
    tree['plan'] = dict(path='collection_plan.json', plan_id=pack, actual_sha256=sha(raw_json(plan)),
                        declared_sha256=sha(raw_json(plan)))
    chain.stage_plan(tree)
    files[kit_dir / 'plan_tree.json'] = raw_json(tree)
    # The W1 identity builder, relocated to this window's kit (no change to W1 bytes).
    scratch = {kit.KIT / 'plan_tree.json': files[kit_dir / 'plan_tree.json']}
    kit._identities(root, scratch, members, inputs)
    pins = json.loads(scratch[kit.KIT / 'registration/identity_pins.json'])
    pins['derivation']['tree_path'] = str(kit_dir / 'plan_tree.json')
    files[kit_dir / 'registration/identity_pins.json'] = raw_json(pins)
    for name in ('model_artifact_inventory.json', 'local_file_verification.json'):
        files[kit_dir / 'registration' / name] = scratch[kit.KIT / 'registration' / name]
    w1_plan_raw = kit.read_w1_plan_bytes(root)
    if w1_plan_raw is not None:
        files[kit_dir / 'registration/sizing_b5.json'] = raw_json(
            derive_window_sizing(root, json.loads(w1_plan_raw), w1_plan_raw, inputs, r1_slots, tree, plan))
    return files


def derive_window_sizing(root, w1_plan, w1_plan_raw, inputs, r1_slots, tree, plan):
    """sizing_b5.json for a series window from the R1-filled W1 plan.

    Anchors keep their W1 member_s; every D member takes the largest W1 D
    member_s (the R1-measured D planning member). Span/maximum use the W1
    validator's formula with the D ceiling 59,520 s (Ed Q4); disk uses W1's
    pilot-3 law, two copies. A window that misses the ceiling returns to the lead.
    """
    from scripts import validate_align_v4_w1_plan as validator
    validator.validate(w1_plan, inputs, r1_slots)
    rows = w1_plan['align_v4']['members']
    by_ordinal = {row['ordinal']: row['member_s'] for row in rows}
    d_member_s = max(row['member_s'] for row in rows if row['role'] == 'D')
    seconds = {m['ordinal']: (by_ordinal[m['ordinal']] if m['role'] == 'anchor' else d_member_s)
               for m in plan['members']}
    sized = series.window_sizing([seconds[k] for k in sorted(seconds)])
    if not sized['fits_ceiling']:
        raise ValueError(f'{plan["series_window"]} misses the {series.D_WINDOW_CEILING_S} s ceiling '
                         f'({sized["window_max_s"]} s); return to lead')
    law_path = kit.SOURCE_KIT / 'registration/sizing_b5.json'
    law_raw = kit.frozen(root, kit.ANCHOR_COMMIT, law_path)
    source = json.loads(law_raw)['packs']['align-pilot-v3']
    disk = source['disk_member_law']
    scaffold_bytes = source['disk_derivation']['scaffold_bytes']
    member_bytes = {k: math.ceil(disk['intercept'] + disk['slope'] * v + disk['largest_positive_residual'])
                    for k, v in seconds.items()}
    n = len(seconds)
    scaffold_count = sum(s['expected_count'] for s in tree['stage_graph'] if s['kind'] == 'campaign_collection') - n
    b_bytes = sum(member_bytes.values()) + scaffold_bytes
    pack = plan['plan_id']
    return {'schema_version': 'joulewise.b5_sizing.v1', 'non_claim': True,
            'derivation': ('ALIGN v4 series window sizing from the R1-filled W1 plan: anchors keep W1 member_s, '
                           'every D member takes the largest W1 D member_s; span/maximum per the W1 validator '
                           'formula against the 59,520 s D ceiling; disk per the W1 pilot-3 law, two copies.'),
            'sources': {'w1_plan': {'path': kit.W1_PLAN.as_posix(), 'sha256': sha(w1_plan_raw)},
                        'disk_law': {'commit': kit.ANCHOR_COMMIT, 'path': law_path.as_posix(),
                                     'sha256': sha(law_raw), 'pointer': '/packs/align-pilot-v3/disk_member_law'}},
            'packs': {pack: {
                'pack_id': pack, 'flags': [], 'align_members': n, 'scaffold_members': scaffold_count,
                'member_count': n + scaffold_count, 'B_D': inputs['R1']['B_D'],
                'member_seconds': {str(k): v for k, v in sorted(seconds.items())},
                'align_s': sized['align_s'], 'scaffold_s': series.SCAFFOLD_S,
                'programmed_span_s': sized['programmed_span_s'], 'window_max_s': sized['window_max_s'],
                'window_ceiling_s': series.D_WINDOW_CEILING_S, 'T_stream_max_s': sized['T_stream_max_s'],
                'member_cap': {'spent_s': series.MEMBER_CAP_S}, 'fits_spent_cap': True, 'disk_member_law': disk,
                'member_upper_bytes': {str(k): v for k, v in sorted(member_bytes.items())},
                'estimated_footprint_bytes': 2 * b_bytes,
                'disk_derivation': {'formula': 'W1 pilot-3 law per member plus measured scaffold; two copies',
                                    'peak_copies': 2, 'B_bytes': b_bytes, 'scaffold_bytes': scaffold_bytes,
                                    'extra_wait_peak_bytes': 0, 'fixed_retained_bytes': 0}}}}


def build_files(root=ROOT, *, test_shape=TEST_SHAPE, windows=None):
    """All series files, or the manifest plus only ``windows``' kits."""
    root = Path(root)
    manifest = series.build_manifest(test_shape)
    inputs = kit.read_inputs(root)
    r1_slots = kit.read_r1_slots(root)
    files = {MANIFEST_PATH: raw_json(manifest)}
    for row in manifest['windows']:
        if row['role'] != 'selection' and (windows is None or row['window'] in windows):
            build_window_files(root, manifest, row['window'], inputs, r1_slots, files)
    if windows is None:
        files[SERIES_KIT / 'README.md'] = README.encode()
    return files


def generate(output_root=ROOT, *, check=False, source_root=ROOT, windows=None):
    files = build_files(source_root, windows=windows)
    for path, raw in files.items():
        target = Path(output_root) / path
        if check:
            if not target.is_file() or target.read_bytes() != raw:
                raise ValueError('generated v4 series kit drifted: ' + str(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    return files


def read_manifest(root=ROOT):
    return series.validate_manifest(json.loads((Path(root) / MANIFEST_PATH).read_bytes()))


def require_sizing(root, window_id):
    """prepare needs the window's sizing_b5.json, derived from the committed W1 plan."""
    spec = series.window(read_manifest(root), window_id)
    path = Path(root) / spec['kit'] / 'registration/sizing_b5.json'
    w1_plan = kit.read_w1_plan_bytes(root)
    if w1_plan is None or not path.is_file():
        raise ValueError(f'v4 series BLOCKED: {path.relative_to(root)} is not derivable until R1 fills '
                         f'{kit.W1_PLAN}; regenerate the series after the W1 plan is committed')
    pinned = json.loads(path.read_bytes()).get('sources', {}).get('w1_plan', {})
    if pinned.get('sha256') != sha(w1_plan):
        raise ValueError(f'{path.relative_to(root)} is stale for {kit.W1_PLAN}; regenerate the series')


def require_window_ready(root, window):
    """W1 registration still ready, the series byte-identical, and this window sized.

    Returns ``(window_id, window_spec, manifest)``. W1 itself arms through the W1
    kit; this route is for C/T windows only.
    """
    manifest = read_manifest(root)
    window_id = series.resolve_window(manifest, window)
    if window_id == 'W1':
        raise ValueError('W1 arms through the W1 kit (no --window); the series route is for C/T windows')
    kit.generate(root, check=True, source_root=root)
    generate(root, check=True, source_root=root, windows=(window_id,))   # manifest + this window's kit
    require_sizing(root, window_id)
    return window_id, series.window(manifest, window_id), manifest


README = """# ALIGN v4 series after W1 (Opus build) — PROVISIONAL, NON-CLAIM

Build: `python3.13 -B scripts/align_v4_series.py`. Check: add `--check` (drift only).
Generated from `registration/inputs.json` and `r1_slots.json` of the W1 kit and the
frozen manifest `series_manifest.json` (`joulewise.align.apple.v4_series`).

Order: W1 (existing kit), C1-C8 (calibration; aliases D1-D8, so D1-D3 are C1-C3),
then T1-T3 (locked test). Every C/T window has the default D shape (22 members):
anchors 1-4 (original bytes), early sentinel 5 (replay of W1 ordinal 5; captures R),
16 fresh held-out D members alternating pair by pair (7 benign + 1 sabotage per
pair; sabotage at 9 and 18), late sentinel 22; midpoint after 11. Odd windows start
with spam, even with bank. Held-out seeds per pair start at 2 in kit order and skip
the development indices 1 and 91-99: C1-C8 use 2-65, T1-T3 66-89.

Arm a window: `align_v4_session.py prepare --window C1 ...`, then `install` with a
`--next-arm-triage` packet from `align_v4_series.py packet --ledger L --checks C`.
The arm refuses unless the packet's series binding names this window as the next
frozen window of the ledger it carries (`v4_series.check_arm_binding`), on top of the
R12 triage (`v4_cadence.next_arm_triage`, fixed-8 `calibration_stop`).
`prepare` refuses until R1 has filled the W1 plan and this window's sizing_b5.json
is regenerated from it. Open lead rulings: docs/align/v4/DCT-SERIES-opus.md.
"""


def _read_json(path):
    return json.loads(Path(path).read_bytes())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output-root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    commands = parser.add_subparsers(dest='command')
    nxt = commands.add_parser('next', help='print the cadence decision for a series ledger')
    nxt.add_argument('--ledger', type=Path, required=True)
    pkt = commands.add_parser('packet', help='write the R12 next-arm packet from a ledger and check evidence')
    pkt.add_argument('--ledger', type=Path, required=True)
    pkt.add_argument('--checks', type=Path, required=True,
                     help='JSON: each off-MBP triage id -> {status, basis, evidence_sha256}')
    pkt.add_argument('--code-or-config-changed', action='store_true')
    pkt.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'next':
            print(json.dumps(series.plan_next(read_manifest(ROOT), _read_json(args.ledger)), sort_keys=True))
            return 0
        if args.command == 'packet':
            packet = series.build_packet(read_manifest(ROOT), _read_json(args.ledger),
                                         code_or_config_changed=args.code_or_config_changed,
                                         checks=_read_json(args.checks))
            with Path(args.out).open('x') as handle:
                handle.write(json.dumps(packet, indent=2, sort_keys=True) + '\n')
            print(f'packet for {packet["series"]["window"]}#{packet["series"]["attempt"]}: {args.out}')
            return 0
        generate(args.output_root, check=args.check)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print('align_v4_series: ' + str(exc), file=sys.stderr)
        return 1
    print('verified v4 series kit (no drift)' if args.check else 'generated PROVISIONAL v4 series kit')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
