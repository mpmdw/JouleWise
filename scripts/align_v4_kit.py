#!/usr/bin/env python3
"""Build the PROVISIONAL, non-claim ALIGN v4 W1 skeleton, without model access.

Generation is allowed with pending inputs; --check is deliberately fail closed.
WP11 supplies D identities, WP18 historical contrast counts, and R0/R1 the
selected policies. This builder never hashes or opens a model/data directory.
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
from scripts.align_pilot_kit import raw_json, sha
from joulewise.align.apple.sampling import episode_seed, turn_seed
from joulewise.b5 import chain

KIT = Path('configs/campaigns/align_v4')
PACK_ID = 'align-v4'
DESK_SCHEMA = 'joulewise.align_pilot_desk.v4'
SOURCE_KIT = Path('configs/campaigns/align_pilot_v3')
ANCHOR_COMMIT = '83e2dac59'
CONTRAST_COMMIT = '45b47f7b6'
COUNCIL_COMMIT = '6eb1ff5be'
WINDOW_PLAN_COMMIT = '40c569cfd'
INPUTS = KIT / 'registration/inputs.json'
D_TAG = 'qwen3.8-27b'
D_REVISION = '815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9'
D_SOURCE = '/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit'
D_SAMPLER = {'temperature': 1.0, 'top_p': 0.95, 'top_k': 20, 'min_p': 0}
D_DEVELOPMENT_INDICES = (1, 91, 92, 93)
SPAN_LIMIT_S = 26940
SCAFFOLD_S = 4995
BUDGET_FLOOR = 6144

# Ordinals remain stable after dropping 17; the late replay remains ordinal 18.
# name, pair, condition, seed index. Arm letters refer only to the contrast.
ROSTER = (
    ('anchor', 'spam_filter_update', 'benign', 1),
    ('anchor', 'bank_transfer_2', 'sabotage', 1),
    ('anchor', 'spam_filter_update', 'sabotage', 1),
    ('anchor', 'bank_transfer_2', 'benign', 1),
    ('D', 'spam_filter_update', 'benign', 1),
    ('X-G', 'spam_filter_update', 'sabotage', 16),
    ('Y-S', 'spam_filter_update', 'benign', 14),
    ('D', 'bank_transfer_2', 'benign', 1),
    ('X-S', 'spam_filter_update', 'sabotage', 16),
    ('Y-G', 'spam_filter_update', 'benign', 14),
    ('D', 'spam_filter_update', 'sabotage', 1),
    ('Y-G', 'spam_filter_update', 'benign', 14),
    ('X-S', 'spam_filter_update', 'sabotage', 16),
    ('D', 'bank_transfer_2', 'sabotage', 1),
    ('Y-S', 'spam_filter_update', 'benign', 14),
    ('X-G', 'spam_filter_update', 'sabotage', 16),
    ('D', 'bank_transfer_2', 'benign', 93),
    ('D', 'spam_filter_update', 'benign', 1),
)


def frozen(root, commit, path):
    """Read repository code/config objects only, never a cited filesystem path."""
    return subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=root,
                          check=True, capture_output=True).stdout


def read_inputs(root=ROOT):
    return json.loads((Path(root) / INPUTS).read_bytes())


def pending_inputs(inputs):
    """Required leaves have no plausible numeric/digest fallback."""
    required = {
        'WP11': ('identity_unit', 'artifact_inventory', 'local_file_verification'),
        'WP18': ('X', 'Y'),
        'R0': ('reasoning_effort',),
        'R1': ('B_D', 'I_D', 'T_dead', 'thermal_policy'),
        'WP15': ('runtime_entrypoint',),
    }
    pending = []
    def visit(value, path):
        if value is None or value == '' or value == {} or value == []:
            pending.append(path)
        elif isinstance(value, dict):
            for key, item in value.items():
                visit(item, f'{path}.{key}')
        elif isinstance(value, str) and value.startswith('PENDING_'):
            pending.append(path)
    for owner, keys in required.items():
        for key in keys:
            visit(inputs.get(owner, {}).get(key), f'{owner}.{key}')
    return pending


def require_ready(inputs):
    pending = pending_inputs(inputs)
    if pending:
        raise ValueError('v4 kit BLOCKED by placeholders: ' + ', '.join(pending))
    # Filled values are not automatically evidence; validate the bounded inputs.
    for name in ('X', 'Y'):
        ref = inputs['WP18'][name]
        if type(ref.get('max_turns')) is not int or ref['max_turns'] <= 0:
            raise ValueError(f'WP18.{name}.max_turns must be a recorded positive integer')
        if not valid_digest(ref.get('token_fixture_sha256')):
            raise ValueError(f'WP18.{name} requires a token fixture SHA256')
    if inputs['R0']['reasoning_effort'] not in ('xhigh', 'medium', 'low'):
        raise ValueError('R0 reasoning effort must be a selected ladder rung')
    slots = inputs['R1']
    validate_budget(slots['B_D'])
    if not finite(slots['I_D']) or not 0 <= slots['I_D'] < 1750:
        raise ValueError('R1.I_D must be finite and in [0, 1750)')
    if not finite(slots['T_dead']) or not math.isclose(
            slots['T_dead'], (1750 - slots['I_D']) / 1.13544, rel_tol=1e-9):
        raise ValueError('R1.T_dead must equal (1750 - I_D) / 1.13544')
    from joulewise.align.apple.thermal_gates import validate_gate_policy
    policy = validate_gate_policy(slots['thermal_policy'])
    if not policy['heavy'] or not policy['per_turn'] or 'window_reference' in policy:
        raise ValueError('D requires heavy/G1/holds; window R is captured by member 5')
    unit = inputs['WP11']['identity_unit']
    if (unit.get('model_source') != D_SOURCE or unit.get('model_revision') != D_REVISION
            or not valid_digest(unit.get('model_artifact_sha256'))):
        raise ValueError('WP11 D identity must bind the pinned 8-bit artifact')


def valid_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_budget(budget):
    if type(budget) is not int or not BUDGET_FLOOR <= budget <= 40960 or budget % 1024:
        raise ValueError('B_D must be a multiple of 1024 in [6144, 40960]')


def fit_roster(budget, member_seconds):
    """Apply A1 prospectively with R1's cost function: 17 first, then B_D.

    member_seconds(ordinal, B_D) must re-estimate costs at each budget, including
    whole-turn overshoot and waits. No unmeasured rate transfer is made here.
    The caller must requalify/freeze the selected budget before prepare.
    """
    validate_budget(budget)
    ordinals, actions = list(range(1, 19)), []
    while True:
        costs = [member_seconds(i, budget) for i in ordinals]
        if any(not finite(v) or v <= 0 for v in costs):
            raise ValueError('R1 member costs must be finite positive seconds')
        span = math.ceil(SCAFFOLD_S + math.fsum(costs))
        if span <= SPAN_LIMIT_S:
            if max(costs) > 1800:
                raise ValueError('R1 member exceeds spent 1800 s cap; return to lead for requalification')
            return {'ordinals': ordinals, 'B_D': budget, 'programmed_span_s': span,
                    'actions': actions, 'requires_R1_requalification': bool(actions)}
        if 17 in ordinals:
            ordinals.remove(17)
            actions.append({'drop_ordinal': 17})
        elif budget > BUDGET_FLOOR:
            budget -= 1024
            actions.append({'B_D': budget})
        else:
            raise ValueError('roster does not fit at B_D=6144 after dropping 17; return to lead')


def _rewrite(value):
    if isinstance(value, str):
        return value.replace(str(SOURCE_KIT), str(KIT)).replace('align-pilot-v3', PACK_ID).replace(
            'align_pilot_v3', 'align_v4')
    if isinstance(value, list):
        return [_rewrite(v) for v in value]
    if isinstance(value, dict):
        return {k: _rewrite(v) for k, v in value.items()}
    return value


def thermal_policy(inputs, *, heavy, per_turn):
    value = deepcopy(inputs['R1']['thermal_policy'])
    if value is None:
        value = dict(sensors=None, delta_fast_c=None, delta_slow_c=None,
                     turn_cap_s=None, chunk_tokens=None)
    value.update(heavy=heavy, per_turn=per_turn)
    # WP15 owns the runtime custody mechanism. Never synthesize a temperature.
    value.pop('window_reference', None)
    return value


def build_files(root=ROOT):
    root = Path(root)
    inputs = read_inputs(root)
    files = {INPUTS: (root / INPUTS).read_bytes()}
    old_tree = json.loads(frozen(root, ANCHOR_COMMIT, SOURCE_KIT / 'plan_tree.json'))
    tree = _rewrite(old_tree)
    stages = [s for s in tree['stage_graph'] if '-episodes-' in s['stage_id']]
    rows_by_stage = [[], []]
    members = []
    source_receipts = []
    anchor_configs = []
    for ordinal, (name, pair, condition, seed_index) in enumerate(ROSTER, 1):
        half = 0 if ordinal <= 9 else 1
        stage = stages[half]
        directory = KIT / 'stages' / ('episodes-a' if half == 0 else 'episodes-b')
        if name == 'anchor':
            source_path = SOURCE_KIT / 'stages/episodes-a' / f'align-pilot-v3-episodes-a-e{ordinal:02}.json'
            raw = frozen(root, ANCHOR_COMMIT, source_path)
            config = json.loads(raw)
            anchor_configs.append(config)
            filename = source_path.name  # Keep the run_id and all config bytes.
            commit = ANCHOR_COMMIT
        else:
            source_index = 25 if name.startswith('X') else 18
            source_path = SOURCE_KIT / 'stages/episodes-b' / f'align-pilot-v3-episodes-b-e{source_index}.json'
            commit = CONTRAST_COMMIT
            config = (deepcopy(anchor_configs[0]) if name == 'D'
                      else json.loads(frozen(root, commit, source_path)))
            config['run_id'] = f'{PACK_ID}-episodes-{"a" if half == 0 else "b"}-e{ordinal:02}'
            config['hardware_target']['notes'] = 'PROVISIONAL ALIGN v4 non-claim skeleton; not admitted for execution.'
            spec = json.loads(config['workload_profile']['prompt_text'])
            spec.pop('max_episode_seconds', None)
            spec.update(condition=condition, seed=seed_index, warmup_condition='benign')
            if name == 'D':
                config['model'].update(name='Qwen3.8-27B-8bit', family='qwen3_5',
                                       source=D_SOURCE, revision=D_REVISION)
                config['quantization'] = {'name': 'int8', 'bits': 8, 'group_size': 64}
                spec.update(sampler=D_SAMPLER, temperature=1.0, assistant_history='reasoning_content',
                            chat_template_kwargs={'reasoning_effort': inputs['R0']['reasoning_effort']},
                            max_episode_decode_tokens=inputs['R1']['B_D'], deadman_s=inputs['R1']['T_dead'],
                            hybrid_checkpoint_limit=0, thermal=thermal_policy(inputs, heavy=True, per_turn=True))
            else:
                spec.update(max_turns=inputs['WP18'][name[0]]['max_turns'],
                            thermal=thermal_policy(inputs, heavy=False, per_turn=name.endswith('G')))
            config['workload_profile']['prompt_text'] = json.dumps(spec, sort_keys=True, separators=(',', ':'), allow_nan=False)
            model_id = D_TAG if name == 'D' else 'qwen3-30b-a3b'
            config['run_metadata']['tags'] = [PACK_ID, 'non-claim', 'launch_lineage_required', 'align', 'align_episode',
                'align-model=' + model_id, 'align-condition=' + condition, 'align-task=' + pair,
                'align-repeat=' + ('2' if ordinal in (12, 13, 15, 16, 18) else '1'),
                'align-stage=episodes-' + ('a' if half == 0 else 'b')]
            raw = raw_json(config)
            filename = config['run_id'] + '.json'
        spec = json.loads(config['workload_profile']['prompt_text'])
        path = directory / filename
        files[path] = raw
        model_id = D_TAG if name == 'D' else 'qwen3-30b-a3b'
        seed = episode_seed(model_id, 'thinking_on', 'shade/' + pair, seed_index)
        replay_of = {12: 10, 13: 9, 15: 7, 16: 6, 18: 5}.get(ordinal)
        row = dict(run_id=config['run_id'], config=filename, config_path=path.as_posix(), config_sha256=sha(raw),
                   index=len(rows_by_stage[half]) + 1, rep=2 if replay_of else 1, role='absolute_repeat',
                   block_id=None, block_index=len(rows_by_stage[half]) + 1, position=None, position_in_block=1,
                   arm=None, model_tag=model_id + '-mlx', workload='align_episode',
                   module_id=PACK_ID + '-' + model_id, pack_id=PACK_ID)
        rows_by_stage[half].append(row)
        member = dict(ordinal=ordinal, run_id=config['run_id'], stage_id=stage['stage_id'],
                      role=name, block='D' if name == 'D' else 'A' if name == 'anchor' else name,
                      model_id=model_id, task_pair=pair, condition=condition, seed_index=seed_index,
                      expected_episode_seed=seed, expected_turn_seed_0=turn_seed(seed, 0),
                      config_path=path.as_posix(), config_sha256=sha(raw), spec=spec,
                      repeat=row['rep'], is_replay=bool(replay_of), non_claim=True, held_out=False)
        if replay_of:
            member['replay_of'] = members[replay_of - 1]['run_id']
        if ordinal == 5:
            member['window_reference_role'] = 'capture_last_60s_idle_before_warmup'
        elif ordinal > 5:
            member['window_reference_role'] = 'consume_member_5_custody_via_WP15'
        if name != 'D':
            source_receipts.append(dict(ordinal=ordinal, commit=commit, path=source_path.as_posix(),
                                        sha256=sha(frozen(root, commit, source_path))))
        members.append(member)
    for stage, rows in zip(stages, rows_by_stage, strict=True):
        manifest = Path(rows[0]['config_path']).parent / 'order_manifest.json'
        raw = raw_json(dict(schema_version='joulewise.order_manifest.v1', manifest_id=stage['stage_id'],
                            planned_n_bundles=len(rows), executed_order=rows))
        files[manifest] = raw
        stage.update(expected_count=len(rows), input=dict(kind='manifest', path=manifest.as_posix(),
                     manifest_id=stage['stage_id'], sha256=sha(raw)))
        stage['launch']['commands'][0]['argv_template']['arguments'][0]['value'] = manifest.parent.as_posix()
    tree['science'] = [dict(row, stage_id=stage['stage_id'])
                       for stage, rows in zip(stages, rows_by_stage, strict=True) for row in rows]
    tree['module_order'] = list(dict.fromkeys(row['module_id'] for row in tree['science']))
    pending = pending_inputs(inputs)
    plan = dict(schema_version='joulewise.align_v4.v1', plan_id=PACK_ID, non_claim=True,
                status='PROVISIONAL_SKELETON' if pending else 'FOR_LEAD_REVIEW', pending_inputs=pending,
                protocol='docs/align/pilot_protocol_v4.md', members=members, midpoint_after_ordinal=9,
                seed_law='align-p4-v1', turn_seed_law='align-p4-turn-v1', seed_bits=64,
                seed_roles=dict(D=dict(tag=D_TAG, development_indices=list(D_DEVELOPMENT_INDICES),
                                      held_out_start=2, held_out_excludes=[91, 92, 93], W1_held_out=0)),
                source_receipts=source_receipts, council_commit=COUNCIL_COMMIT,
                window_plan_commit=WINDOW_PLAN_COMMIT,
                reconciliations=['WP16/A1 D seed 1 overrides window-plan choice 101; held-out starts at 2.',
                                 'Synthesized ruling: checkpoint limit 0 throughout series overrides A1 conditional enablement.'],
                runtime_requirements=dict(D_tools='family-validated XML via qwen3_5', presence_penalty=0,
                                          window_reference='WP15 custody; member 5 captures; later members consume',
                                          launcher=inputs['WP15']['runtime_entrypoint']))
    files[KIT / 'collection_plan.json'] = raw_json(plan)
    seed_table = {}
    for tag, indices in ((D_TAG, (1, 2, 91, 92, 93)), ('qwen3-30b-a3b', (1, 14, 16))):
        seed_table[tag] = {pair: {str(index): episode_seed(tag, 'thinking_on', 'shade/' + pair, index)
                                 for index in indices}
                           for pair in ('spam_filter_update', 'bank_transfer_2')}
    files[KIT / 'registration/seed_manifest.json'] = raw_json(dict(
        seed_law='align-p4-v1', turn_seed_law='align-p4-turn-v1', seed_bits=64,
        non_claim=True, seeds=seed_table,
        note='D 1/91/92/93 development; 2 is the first held-out index, unused in W1.'))
    tree.update(generator=dict(path='scripts/align_v4_kit.py', sha256=sha(Path(__file__).read_bytes())),
                draft_status=plan['status'], arm_attachments={})
    tree['plan'] = dict(path='collection_plan.json', plan_id=PACK_ID,
                        actual_sha256=sha(raw_json(plan)), declared_sha256=sha(raw_json(plan)))
    chain.stage_plan(tree)  # Preserve the real calibrated scaffold's graph.
    files[KIT / 'plan_tree.json'] = raw_json(tree)
    _identities(root, files, members, inputs)
    files[KIT / 'registration/sizing_preview.json'] = raw_json(dict(
        status='PROVISIONAL_NOT_ARM_SIZING', non_claim=True, align_members=18, scaffold_s=SCAFFOLD_S,
        planning_align_s=21931.27, planning_span_s=26927, span_limit_s=SPAN_LIMIT_S,
        planning_window_max_s=44640, planning_two_copy_GB=37.4,
        member_seconds={'anchor': 3131.27 / 4, 'D': 1800, 'G': 1150, 'S': 850},
        fit_rule=['drop ordinal 17', 'lower B_D by 1024 to 6144', 'return to lead'],
        note='R1 must replace guesses, requalify budget, derive sizing_b5.json and disk before prepare.'))
    files[KIT / 'README.md'] = README.encode()
    return files


def _identities(root, files, members, inputs):
    from scripts.bytes_h_session import align_unit_id
    old_pins = json.loads(frozen(root, ANCHOR_COMMIT, SOURCE_KIT / 'registration/identity_pins.json'))
    old_inventory = json.loads(frozen(root, ANCHOR_COMMIT, SOURCE_KIT / 'registration/model_artifact_inventory.json'))
    old_model = next(v for k, v in old_pins['units'].items() if k != 'neg8_reference')
    old_artifact = next(v for k, v in old_inventory['artifacts'].items() if k != 'neg8_reference')
    units = {'neg8_reference': deepcopy(old_pins['units']['neg8_reference'])}
    artifacts = {'neg8_reference': deepcopy(old_inventory['artifacts']['neg8_reference'])}
    for m in members:
        uid = align_unit_id(m['model_id'], m['run_id'])
        if m['model_id'] == D_TAG:
            unit = deepcopy(inputs['WP11']['identity_unit']) or dict(
                model_source=D_SOURCE, model_name='Qwen3.8-27B-8bit', model_revision=D_REVISION,
                model_artifact_sha256=None, stack_identity={}, flags=['PENDING_WP11_D_IDENTITY'])
            artifact = inputs['WP11']['artifact_inventory']
        else:
            unit, artifact = deepcopy(old_model), deepcopy(old_artifact)
        unit.update(config_count=1, config_paths=[m['config_path']])
        units[uid], artifacts[uid] = unit, artifact
    files[KIT / 'registration/identity_pins.json'] = raw_json(dict(
        schema='joulewise.b5_identity_pins.v1', status='PROVISIONAL_PENDING_LIVE_GATES', non_claim=True,
        units=units, runtime_versions=old_pins['runtime_versions'],
        derivation=dict(anchor_commit=ANCHOR_COMMIT, D='WP11', tree_path=str(KIT / 'plan_tree.json'),
                        tree_sha256=sha(files[KIT / 'plan_tree.json']))))
    files[KIT / 'registration/model_artifact_inventory.json'] = raw_json(dict(non_claim=True, artifacts=artifacts))
    files[KIT / 'registration/local_file_verification.json'] = raw_json(dict(
        status='PROVISIONAL_PENDING_WP11', D=inputs['WP11']['local_file_verification'],
        inherited_30B_commit=ANCHOR_COMMIT, note='No local files were inspected by this builder.'))


def generate(output_root=ROOT, *, check=False, source_root=ROOT):
    files = build_files(source_root)
    for path, raw in files.items():
        target = Path(output_root) / path
        if check:
            if not target.is_file() or target.read_bytes() != raw:
                raise ValueError('generated v4 kit drifted: ' + str(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    if check:
        require_ready(read_inputs(source_root))
    return files


README = """# ALIGN v4 W1 skeleton — PROVISIONAL, NON-CLAIM

Build: `python3.13 -B scripts/align_v4_kit.py`. Check: add `--check`.
`--check` MUST FAIL while registration/inputs.json contains pending inputs.
No study/model path is followed. All source configs come from pinned Git objects.

18 members per Amendment A1: four exact original anchors, eight 30B contrast
runs and six D runs. Midpoint follows ordinal 9. D uses seed 1 (both pairs and
conditions), development 93 at ordinal 17, and a replay of 5 at 18. Development
91–92 are reserved for R0; held-out starts at 2, excluding development indices.
The window-plan draft's D index 101 is superseded by synthesized WP16/A1.
Checkpointing is explicitly off for D throughout the series, superseding A1.

WP11 must provide D file identities/inventory/verification; WP18 must provide
X=b-e25/index16 and Y=b-e18/index14 historical max_turns and fixture digests.
No configured 12-turn fallback is used for the contrast. R0 must select effort;
R1 must select B_D, I_D, T_dead, sensors, bands, recovery cap and chunk size.
Missing numeric controls are null and invalid as executable EpisodeSpecs.
The existing qwen3_5 endpoint selects XML tools from the model family.
Presence penalty remains the endpoint's fixed zero; sampler is 1/.95/20/0.

WP15 must wire the thermal launcher and custody for R: 5 captures its last
60 s of idle before neutral warmup; all later sidecar members consume it.
The scaffold's campaign commands remain a skeleton pending that wiring.
No synthetic sensor, reference temperature, model digest or turn count is used.

Sizing_preview.json contains A1's planning guesses only. No arm-compatible
sizing_b5.json is supplied. Use fit_roster with R1 measured cost estimates:
drop only 17 first, then decrease B_D by 1024 down to 6144; otherwise return
to lead. Preserve anchors, contrasts and 5/18. Requalify/freeze changed budgets.
The additive align_v4_session.py refuses prepare/install while inputs are pending.
Its desk is the parameterized pilot instrument desk; WP21 owns full U4–U6,
K-session and contrast reporting. This kit grants no arm or hardware approval.

`night_plan.template.json` is the fail-closed Window-1 planning template in
the pilot night-plan v5 shape. Every R1 value, including every member cost,
is an explicit `PENDING_R1` value. Validate a separately filled copy with
`python3 -B scripts/validate_align_v4_w1_plan.py <copy>`; the command refuses
any placeholder and recomputes both the 26,940 s span cap and 44,640 s window
maximum. The template is not custody, an arm receipt, or an installation.
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        generate(args.output_root, check=args.check)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print('align_v4_kit: ' + str(exc), file=sys.stderr)
        return 1
    print('verified v4 kit inputs (lead admission still required)' if args.check else 'generated PROVISIONAL v4 skeleton')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
