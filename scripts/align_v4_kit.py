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
R1_SLOTS = KIT / 'registration/r1_slots.json'
# The R1-filled copy of night_plan.template.json (validate_align_v4_w1_plan.py).
# FINAL-DESIGN B8: W1 sizing comes from R1, so sizing_b5.json is derived from
# this file and does not exist before it is committed.
W1_PLAN = KIT / 'registration/w1_plan.json'
SIZING = KIT / 'registration/sizing_b5.json'
D_PINS = Path('configs/align/v4/qwen38-27b-8bit-hf-pins.json')
# Lead ruling R5-8: the WP18 token-id fixtures are committed here and are a
# hard W1 prerequisite (scripts/align_v4_wp18_fixtures.py writes them).
WP18_FIXTURES = {
    'X': KIT / 'registration/wp18_x_token_ids.json',
    'Y': KIT / 'registration/wp18_y_token_ids.json',
}
WP18_FIXTURE_SCHEMA = 'joulewise.align_v4.wp18_token_fixture.v1'
WP18_RUN_IDS = {'X': 'align-pilot-v3-episodes-b-e25', 'Y': 'align-pilot-v3-episodes-b-e18'}
D_REPO = 'mlx-community/Qwen3.8-27B-8bit'
D_TAG = 'qwen3.8-27b'
D_REVISION = '815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9'
D_SOURCE = '/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit'
D_SAMPLER = {'temperature': 1.0, 'top_p': 0.95, 'top_k': 20, 'min_p': 0}
D_DEVELOPMENT_INDICES = (1, 91, 92, 93)
SPAN_LIMIT_S = 26940
SCAFFOLD_S = 4995
BUDGET_FLOOR = 6144

# Ordinals are stable. After council ruling 1(g)'s swap the late replay of 5 is
# ordinal 17 and development index 93 is ordinal 18.
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
    ('D', 'spam_filter_update', 'benign', 1),
    ('D', 'bank_transfer_2', 'benign', 93),
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
        # Empty fan_keys is a valid policy choice (no fan telemetry selected).
        if value is None or value == '' or value == {} or (value == [] and not path.endswith('.fan_keys')):
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


# What each owner's placeholder is waiting for. require_ready prints the
# reason for every owner that is still pending, so the block names its source.
PENDING_REASONS = {
    'WP11': ('D identity unit, artifact inventory and local file verification for the pinned '
             '8-bit artifact (the R0 record\'s model_artifact_identity checked against '
             'configs/align/v4/qwen38-27b-8bit-hf-pins.json).'),
    'WP18': ('Mac-side (lead + magistrate), not derivable off the Mac: X = pilot-7 '
             'align-pilot-v3-episodes-b-e25 (spam/sabotage, seed index 16) and Y = '
             'align-pilot-v3-episodes-b-e18 (spam/benign, index 14). max_turns = that member\'s '
             'recorded pilot-7 turn count (FINAL-DESIGN 2.5; Amendment 1: both arms stop at the '
             'recorded pilot-7 turn count), never the configured 12-turn ceiling. '
             'token_fixture_sha256 = SHA-256 of the committed WP18 token-id fixture built from those '
             'two members\' align_turns.jsonl in the pilot 6-7 offload copy and p7-PILOT.json '
             '(plan WP18; CHAIR ruling 9(d)); scripts/align_v4_wp18_fixtures.py writes both fixtures '
             '(registration/wp18_x_token_ids.json, wp18_y_token_ids.json) and these leaves.'),
    'R0': 'R0.reasoning_effort stays a placeholder until R0 passes.',
    'R1': ('R1 hardware rehearsal (scripts/align_r1_rehearsal.py): B_D, I_D, T_dead (lead ruling L1) '
           'and the thermal policy.'),
    'WP15': 'WP15 supplies the operator-pinned W1 runtime entrypoint.',
}


def pending_message(pending):
    owners = list(dict.fromkeys(path.split('.', 1)[0] for path in pending))
    return ('v4 kit BLOCKED by placeholders: ' + ', '.join(pending) + ' | '
            + ' | '.join(f'{owner}: {PENDING_REASONS.get(owner, "pending")}' for owner in owners))


def read_r1_slots(root=ROOT):
    return json.loads((Path(root) / R1_SLOTS).read_bytes())


def read_w1_plan_bytes(root=ROOT):
    """The committed R1-filled W1 plan's bytes, or None while R1 has not supplied it."""
    path = Path(root) / W1_PLAN
    return path.read_bytes() if path.is_file() else None


def read_w1_plan(root=ROOT):
    raw = read_w1_plan_bytes(root)
    return None if raw is None else json.loads(raw)


def read_d_pins(root=ROOT):
    return json.loads((Path(root) / D_PINS).read_bytes())


R1_SLOTS_SCHEMA = 'joulewise.align.r1_slots.v1'
R1_HARDWARE_SOURCE = 'R1 hardware rehearsal'
R1_SYNTHETIC_SOURCE = 'R1 synthetic rehearsal'
HIGH_POWER_VERDICTS = ('adopt', 'not_adopted', 'inconclusive')
U5_VERDICTS = ('pass', 'fail', 'inconclusive')
# Council ruling 1(e): steps 1-3 of the named fallback order. A recorded step
# lets a failed duty bar admit; nothing else does. Step 4 ("D screen-only;
# return to council") means D does not run, so it never admits a W1 arm
# (Fable cold pass round 4 LOW-1).
DUTY_FALLBACK_STEPS = (1, 2, 3)


def check_r1_evidence(inputs, r1_slots, *, synthetic=False):
    """Bind r1_slots to R1 evidence (executing review MEDIUM-3).

    The record must be the R1 driver's own (schema and hardware source; the
    synthetic source only for the WP22/tests harness that asks for it), its
    step-d I_D must equal inputs.R1.I_D, the frozen AC powermode must follow
    the A-B-A verdict, max_r1_tail_s must be the largest gated-run tail, U5
    must carry a verdict, every ruling 20 census must have passed, and the
    duty bar must pass or carry a recorded lead fallback step (ruling 1(e)).
    """
    if not isinstance(r1_slots, dict) or r1_slots.get('schema') != R1_SLOTS_SCHEMA:
        raise ValueError(f'R1 r1_slots must be a {R1_SLOTS_SCHEMA} record')
    allowed = (R1_HARDWARE_SOURCE, R1_SYNTHETIC_SOURCE) if synthetic else (R1_HARDWARE_SOURCE,)
    if r1_slots.get('source') not in allowed:
        raise ValueError(f'R1 r1_slots source must be {R1_HARDWARE_SOURCE!r}, not {r1_slots.get("source")!r}')
    slots = r1_slots.get('slots')
    if not isinstance(slots, dict) or not finite(slots.get('I_D')):
        raise ValueError('R1 r1_slots must carry the step-d slots with a finite I_D')
    if not finite(inputs['R1']['I_D']) or not math.isclose(inputs['R1']['I_D'], slots['I_D'],
                                                           rel_tol=0, abs_tol=1e-9):
        raise ValueError(f'inputs.R1.I_D {inputs["R1"]["I_D"]!r} differs from r1_slots.slots.I_D {slots["I_D"]!r}')
    high = r1_slots.get('high_power')
    if not isinstance(high, dict) or high.get('verdict') not in HIGH_POWER_VERDICTS:
        raise ValueError('R1 r1_slots must carry the ruling 16 A-B-A verdict')
    if r1_slots['ac_powermode'] != (2 if high['verdict'] == 'adopt' else 0):
        raise ValueError('R1 r1_slots ac_powermode disagrees with the A-B-A verdict')
    # LEAD-RULINGS-2 R5-5 (protocol v4 :243-251): the slots come from the D
    # step run under the adopted series mode, and R1's own full-inventory
    # classification of that step must give both picks (thermometry bar).
    if r1_slots.get('slots_ac_powermode') != r1_slots['ac_powermode']:
        raise ValueError('R1 slots were not measured under the adopted series AC powermode '
                         f'({r1_slots.get("slots_ac_powermode")!r} != {r1_slots["ac_powermode"]!r})')
    thermometry = r1_slots.get('thermometry')
    if not isinstance(thermometry, dict) or thermometry.get('bar') != 'pass':
        raise ValueError('R1 thermometry bar did not pass: the full-inventory classification of the D step '
                         'must give both a die and a heatsink pick (protocol v4 WP14(a))')
    classified = thermometry.get('D') if isinstance(thermometry.get('D'), dict) else {}
    # Protocol v4 :249-253: W1's gate keys must be in R1's die/heatsink lists,
    # and a pick R1 changed (S6/S7 recomputed for the R1 picks) needs the
    # lead's recorded verification before the W1 freeze (Sol critique HIGH).
    policy = inputs['R1'].get('thermal_policy')
    sensors = policy.get('sensors') if isinstance(policy, dict) else None
    if isinstance(sensors, dict):
        if sensors.get('s_fast') not in (classified.get('die_candidates') or ()):
            raise ValueError(f'R1.thermal_policy s_fast {sensors.get("s_fast")!r} is not in the R1 die list')
        if sensors.get('s_slow') not in (classified.get('heatsink_candidates') or ()):
            raise ValueError(f'R1.thermal_policy s_slow {sensors.get("s_slow")!r} is not in the R1 heatsink list')
    if classified.get('sensor_pick_changed') is not False:
        verification = thermometry.get('lead_verification')
        if (not isinstance(verification, dict) or not isinstance(verification.get('authority'), str)
                or not verification['authority'].strip()):
            raise ValueError('R1 changed (or did not report) the R0 sensor picks (r1.sensor_pick_changed); '
                             'the lead must record thermometry.lead_verification of S6/S7 for the R1 picks')
    u5 = r1_slots.get('u5')
    if not isinstance(u5, dict) or u5.get('verdict') not in U5_VERDICTS or u5.get('c') != 1.0:
        raise ValueError('R1 r1_slots must carry the U5 verdict with c = 1.0 (lead ruling L2)')
    budget = r1_slots.get('deadman_budget')
    tails = [((row or {}).get('phases_s') or {}).get('tail') for row in budget] if isinstance(budget, list) else []
    if not tails or not all(finite(t) for t in tails) or r1_slots['max_r1_tail_s'] != max(tails):
        raise ValueError('R1 r1_slots max_r1_tail_s must be the largest gated-run tail in deadman_budget')
    volumes = r1_slots.get('external_volumes')
    if not isinstance(volumes, list) or not volumes or any(
            (row or {}).get('verdict') != 'PASS' for row in volumes):
        raise ValueError('R1 r1_slots must record passing external-volume censuses (ruling 20)')
    check_r1_budget_and_policy(inputs['R1'], r1_slots)
    duty = r1_slots.get('duty_bar')
    if not isinstance(duty, dict) or type(duty.get('pass')) is not bool:
        raise ValueError('R1 r1_slots must carry the ruling 1(d) duty bar verdict')
    if not duty['pass']:
        fallback = duty.get('lead_fallback')
        if (not isinstance(fallback, dict) or fallback.get('step') not in DUTY_FALLBACK_STEPS
                or not isinstance(fallback.get('authority'), str) or not fallback['authority'].strip()):
            raise ValueError('R1 duty bar failed and no lead fallback step (ruling 1(e)) is recorded')


def _close(a, b):
    return finite(a) and finite(b) and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


# The R1 driver's three gated D runs (council ruling 1(b)); ruling 1(f) is
# judged over all three, never a subset.
GATED_D_RUN_NAMES = ('D_spam_benign_s1_gated_held_a', 'D_spam_benign_s1_gated_held_b',
                     'D_bank_benign_s1_gated_held')
GATED_PHASES = ('G0', 'G1', 'H', 'decode', 'prefill', 'tool', 'tail')
S6_TUNING_CAP_C = 2.0   # council ruling 1(e) step 1: delta_slow capped at 2.0 C


def d_turn_cap_tokens(root=ROOT):
    """The per-turn decode cap every W1 D member inherits (D configs are cloned
    from anchor 1 at ANCHOR_COMMIT and keep its ``max_tokens``)."""
    raw = frozen(root, ANCHOR_COMMIT, SOURCE_KIT / 'stages/episodes-a/align-pilot-v3-episodes-a-e01.json')
    return json.loads(json.loads(raw)['workload_profile']['prompt_text'])['max_tokens']


def ruling_1f_fit(r1_slots, b_d, t_dead):
    """Council ruling 1(f) for a B_D (lead ruling R5-4): the worst case R1
    measured must fit T_dead.

    worst = max G0 + max (G1 + H) + max (prefill + tool) over the gated D runs
            + (B_D + turn_cap_tokens) / r_decode

    A turn is admitted while fewer than B_D decode tokens are spent and then
    keeps its full per-turn cap (FD:263), so B_D + cap bounds the episode
    decode; r_decode is step-d's measured rate. Returns the arithmetic.
    """
    budget = r1_slots.get('deadman_budget')
    rows = budget if isinstance(budget, list) else []
    names = [row.get('run') if isinstance(row, dict) else None for row in rows]
    if sorted(map(str, names)) != sorted(GATED_D_RUN_NAMES):
        raise ValueError('R1 r1_slots deadman_budget must hold exactly the three gated D runs '
                         f'{list(GATED_D_RUN_NAMES)} (ruling 1(f)); got {names}')
    phases = [row.get('phases_s') for row in rows]
    if not all(isinstance(p, dict) and all(finite(p.get(k)) and p[k] >= 0 for k in GATED_PHASES) for p in phases):
        raise ValueError('R1 r1_slots deadman_budget must give finite, non-negative '
                         + ', '.join(GATED_PHASES) + ' seconds per gated run (ruling 1(f))')
    fit = r1_slots.get('budget_fit_inputs')
    rate = (fit or {}).get('r_decode_tok_per_s') if isinstance(fit, dict) else None
    cap = (fit or {}).get('turn_cap_tokens') if isinstance(fit, dict) else None
    if not finite(rate) or rate <= 0 or type(cap) is not int or cap <= 0:
        raise ValueError('R1 r1_slots must carry budget_fit_inputs (r_decode_tok_per_s, turn_cap_tokens) '
                         'for ruling 1(f)')
    if cap != d_turn_cap_tokens():
        raise ValueError(f'ruling 1(f): the gated runs armed a {cap}-token turn cap, but W1 D members carry '
                         f'{d_turn_cap_tokens()}')
    terms = {'G0_s': max(p['G0'] for p in phases), 'holds_s': max(p['G1'] + p['H'] for p in phases),
             'prefill_tool_s': max(p['prefill'] + p['tool'] for p in phases),
             'decode_s': (b_d + cap) / rate}
    worst = math.fsum(terms.values())
    return {'B_D': b_d, 'T_dead_s': t_dead, 'terms_s': terms, 'worst_s': worst, 'fits': worst <= t_dead + 1e-6}


def max_fitting_b_d(r1_slots, t_dead):
    """The largest admissible B_D (a multiple of 1024 in [6144, r1_slots B_D])
    that satisfies ruling 1(f), or None: a sizing aid for the lead."""
    top = (r1_slots.get('slots') or {}).get('B_D')
    if type(top) is not int:
        return None
    for b_d in range(min(top, 40960) // 1024 * 1024, BUDGET_FLOOR - 1, -1024):
        if ruling_1f_fit(r1_slots, b_d, t_dead)['fits']:
            return b_d
    return None


def check_r1_budget_and_policy(r1_inputs, r1_slots):
    """Lead ruling R5-4 (executing review MEDIUM-2, cold pass MEDIUM-2).

    inputs.R1.B_D may only be lowered from R1's step-d budget (A1's fit rule),
    the thermal policy must be the one R1 measured (chunk_tokens = N_chunk,
    delta_slow_c = S6, which is S5 until the lead's FD 2.6 S6 tuning,
    turn_cap_s = S7), and the frozen B_D must satisfy ruling 1(f) against the
    frozen T_dead.
    """
    slots = r1_slots.get('slots') or {}
    if not finite(r1_inputs.get('T_dead')) or r1_inputs['T_dead'] <= 0:
        raise ValueError('R1.T_dead must be finite and positive')
    top = slots.get('B_D')
    if type(top) is not int or not 1024 <= top <= 40960 or top % 1024:
        raise ValueError('R1 r1_slots.slots.B_D must be the step-d decode budget (a multiple of 1024 in '
                         '[1024, 40960])')
    if type(r1_inputs['B_D']) is not int or r1_inputs['B_D'] > top:
        raise ValueError(f'inputs.R1.B_D {r1_inputs["B_D"]!r} exceeds r1_slots.slots.B_D {top} '
                         '(the fit rule only lowers B_D)')
    policy = r1_inputs.get('thermal_policy')
    if not isinstance(policy, dict):
        raise ValueError('inputs.R1.thermal_policy must be an object')
    for name, slot in (('chunk_tokens', 'N_chunk'), ('delta_slow_c', 'S6'), ('turn_cap_s', 'S7')):
        if not _close(policy.get(name), slots.get(slot)):
            raise ValueError(f'inputs.R1.thermal_policy.{name} {policy.get(name)!r} differs from '
                             f'r1_slots.slots.{slot} {slots.get(slot)!r}')
    if not _close(slots.get('S6'), slots.get('S5')):
        tuning = r1_slots.get('s6_tuning')
        if (not isinstance(tuning, dict) or not isinstance(tuning.get('authority'), str)
                or not tuning['authority'].strip() or not _close(tuning.get('from_c'), slots.get('S5'))
                or not _close(tuning.get('to_c'), slots.get('S6'))):
            raise ValueError('r1_slots.slots.S6 differs from S5 without a recorded lead S6 tuning '
                             '(s6_tuning {authority, from_c = S5, to_c = S6})')
        if slots['S6'] > S6_TUNING_CAP_C + 1e-9:
            raise ValueError(f'a tuned S6 must stay within the {S6_TUNING_CAP_C} C cap (council ruling 1(e))')
    fit = ruling_1f_fit(r1_slots, r1_inputs['B_D'], r1_inputs['T_dead'])
    if not fit['fits']:
        raise ValueError(f'ruling 1(f): B_D {fit["B_D"]} does not fit T_dead {fit["T_dead_s"]:.1f} s: worst '
                         f'{fit["worst_s"]:.1f} s = ' + ' + '.join(f'{k} {v:.1f}' for k, v in fit['terms_s'].items())
                         + f'; the largest fitting B_D is {max_fitting_b_d(r1_slots, r1_inputs["T_dead"])}')
    return fit


def require_ready(inputs, r1_slots=None, *, synthetic=False):
    pending = pending_inputs(inputs)
    if pending:
        raise ValueError(pending_message(pending))
    if r1_slots is None:
        r1_slots = read_r1_slots()
    if r1_slots.get('ac_powermode') not in (0, 2):
        raise ValueError('R1 r1_slots must freeze AC powermode 0 or 2')
    # Filled values are not automatically evidence; validate the bounded inputs.
    for name in ('X', 'Y'):
        ref = inputs['WP18'][name]
        if type(ref.get('max_turns')) is not int or ref['max_turns'] <= 0:
            raise ValueError(f'WP18.{name}.max_turns must be a recorded positive integer')
        if not valid_digest(ref.get('token_fixture_sha256')):
            raise ValueError(f'WP18.{name} requires a token fixture SHA256')
    entry = inputs['WP15']['runtime_entrypoint']
    if not isinstance(entry, list) or not entry or not all(isinstance(a, str) and a for a in entry):
        # Fable LOW-3: the runtime is an argv list, never one shell string.
        raise ValueError('WP15.runtime_entrypoint must be a non-empty argv list of strings')
    if inputs['R0']['reasoning_effort'] not in ('xhigh', 'medium', 'low'):
        raise ValueError('R0.reasoning_effort stays a placeholder until R0 passes; then it must be '
                         'the selected ladder rung (xhigh, medium or low)')
    slots = inputs['R1']
    validate_budget(slots['B_D'])
    if not finite(slots['I_D']) or not 0 <= slots['I_D'] < 1750:
        raise ValueError('R1.I_D must be finite and in [0, 1750)')
    tail = r1_slots.get('max_r1_tail_s')
    if not finite(tail) or tail < 0:
        raise ValueError('R1 r1_slots must record a finite, non-negative max_r1_tail_s')
    check_r1_evidence(inputs, r1_slots, synthetic=synthetic)
    expected = l1_t_dead(slots['I_D'], tail)
    if not finite(slots['T_dead']) or not math.isclose(slots['T_dead'], expected, rel_tol=1e-9):
        raise ValueError('R1.T_dead must equal min((1750 - I_D) / 1.13544, '
                         '(1800 - I_D - max_r1_tail_s - 10) / 1.13544) (lead ruling L1)')
    check_l1_member_fit(slots['I_D'], slots['T_dead'], tail)
    from joulewise.align.apple.thermal_gates import validate_gate_policy
    policy_input = deepcopy(slots['thermal_policy'])
    # R1 supplies the numeric/sensor template.  Custody roles and the source
    # bundle digest are deterministically installed per member below.
    policy_input['window_reference'] = {'role': 'capture'}
    policy = validate_gate_policy(policy_input)
    if not policy['heavy'] or not policy['per_turn']:
        raise ValueError('D requires heavy/G1/holds')
    unit = inputs['WP11']['identity_unit']
    if (unit.get('model_source') != D_SOURCE or unit.get('model_revision') != D_REVISION
            or not valid_digest(unit.get('model_artifact_sha256'))):
        raise ValueError('WP11 D identity must bind the pinned 8-bit artifact')


# Lead ruling L1 (LEAD-RULINGS-1, restating council ruling 1(f)): a worst-case
# D member fits under the 1,800 s member cap with the largest R1 tail.
DEADMAN_FACTOR = 1.13544
MEMBER_CAP_S = 1800
L1_MARGIN_S = 10

# Contrast (30B) deadman: FD's T_dead,m = (1750 - I_m) / 1.13544 with the
# 30B member intercept I_m measured in pilot 3 (align_pilot_v3
# registration/sizing_b5.json member_law.intercept_s; it already contains the
# 300 s idle, load, warmup and teardown). The deadman is armed at G0 entry and
# covers G0, any G1 waits and the pilot-7-count episode, so the member stays
# under the runner's 1,800 s kill (HAZARD_MEMBER_CAP_S) and keeps its bundle.
# Neither 330 s (shorter than the planned X-G episode alone) nor 1800/1.13544
# (which ignores the intercept: 516.6 + 1800 > 1800) satisfies that.
CONTRAST_MEMBER_INTERCEPT_S = 516.5751274713251
CONTRAST_DEADMAN_S = (1750 - CONTRAST_MEMBER_INTERCEPT_S) / DEADMAN_FACTOR


def l1_t_dead(i_d, max_r1_tail_s):
    """T_dead = min((1750 - I_D)/1.13544, (1800 - I_D - max_R1_tail - 10)/1.13544)."""
    return min((1750 - i_d) / DEADMAN_FACTOR,
               (MEMBER_CAP_S - i_d - max_r1_tail_s - L1_MARGIN_S) / DEADMAN_FACTOR)


def check_l1_member_fit(i_d, t_dead, max_r1_tail_s):
    """Kit assertion: I_D + 1.13544 T_dead + max_R1_tail + 10 <= 1800."""
    worst = i_d + DEADMAN_FACTOR * t_dead + max_r1_tail_s + L1_MARGIN_S
    if t_dead <= 0 or worst > MEMBER_CAP_S + 1e-6:
        raise ValueError(f'L1: I_D + 1.13544*T_dead + max_r1_tail_s + 10 = {worst:.3f} s '
                         f'exceeds the {MEMBER_CAP_S} s member cap (or T_dead <= 0)')
    return worst


def validate_d_identity(wp11, pins, *, pins_raw=None):
    """WP11 binds the exact pinned D weights, independently of the Mac's record.

    The artifact inventory is the governed model_artifact_identity file set the
    R0 load recorded on the Mac. Every weight shard's sha256 and size must equal
    the HF LFS pin at D_REVISION, and the folded sha256 must recompute from the
    pins, so a wrong or partial copy cannot be registered as D.
    """
    from joulewise.provenance import folded_model_artifact_sha256
    unit = wp11.get('identity_unit') if isinstance(wp11, dict) else None
    inventory = wp11.get('artifact_inventory') if isinstance(wp11, dict) else None
    verification = wp11.get('local_file_verification') if isinstance(wp11, dict) else None
    if not all(isinstance(v, dict) for v in (unit, inventory, verification)):
        raise ValueError('WP11 D identity, inventory and verification must be objects')
    if (unit.get('model_source') != D_SOURCE or unit.get('model_revision') != D_REVISION
            or not valid_digest(unit.get('model_artifact_sha256'))):
        raise ValueError('WP11 D identity must bind the pinned 8-bit artifact')
    if pins.get('repo') != D_REPO or pins.get('revision') != D_REVISION:
        raise ValueError('D HF pins must name the pinned repo and revision')
    # Sol w1rev: the local verification receipt names the pins document and,
    # given its bytes, binds their sha256 (a stale receipt is refused).
    pin_receipt = verification.get('hf_pins')
    if (not isinstance(pin_receipt, dict) or pin_receipt.get('path') != D_PINS.as_posix()
            or pin_receipt.get('repo') != D_REPO or pin_receipt.get('revision') != D_REVISION):
        raise ValueError('WP11 local verification must identify the D HF pins document')
    if pins_raw is not None and pin_receipt.get('sha256') != sha(pins_raw):
        raise ValueError('WP11 local verification HF pins sha256 does not match the committed pins bytes')
    weights = {name: row for name, row in pins['files'].items() if name.endswith('.safetensors')}
    if not weights or any(not valid_digest(row.get('sha256')) for row in weights.values()):
        raise ValueError('D HF pins must carry an LFS sha256 for every weight shard')
    if (inventory.get('kind') != 'file_set' or inventory.get('algorithm') != 'sha256'
            or inventory.get('status') != 'ok' or inventory.get('root') != D_SOURCE):
        raise ValueError('WP11 artifact inventory must be an ok sha256 file_set rooted at the D source')
    expected = {name: row['sha256'] for name, row in weights.items()}
    if inventory.get('files') != expected:
        raise ValueError('WP11 artifact inventory files must equal the HF LFS pins of the D weight shards')
    rows = inventory.get('inventory')
    if not isinstance(rows, list) or sorted(
            (r.get('path'), r.get('sha256'), r.get('size_bytes')) for r in rows if isinstance(r, dict)
    ) != sorted((name, row['sha256'], row['size']) for name, row in weights.items()) or len(rows) != len(weights):
        raise ValueError('WP11 artifact inventory rows must equal the pinned shard names, hashes and sizes')
    folded = folded_model_artifact_sha256(expected)
    if not (folded == inventory.get('folded_sha256') == unit['model_artifact_sha256']
            == verification.get('folded_sha256')):
        raise ValueError('WP11 D artifact sha256 must be the folded sha256 of the pinned weight shards')
    if verification.get('status') != 'verified':
        raise ValueError('WP11 local_file_verification must record status verified')
    return folded


def derive_sizing(root, w1_plan, inputs, r1_slots, tree, collection_plan, w1_plan_raw):
    """sizing_b5.json from the R1-filled W1 plan (FINAL-DESIGN B8, Amendment 1 arithmetic).

    Member seconds are R1's (the validated plan's member_s). Span, window and the
    1,800 s spent cap are the validator's. Disk is the pilot-3 law the design uses
    (FINAL-DESIGN 2.5: per member ceil(OLS bundle_bytes(member_s) + largest positive
    residual), plus the measured scaffold bytes, two copies), read from the frozen
    align_pilot_v3 sizing at ANCHOR_COMMIT.
    """
    from scripts import validate_align_v4_w1_plan as validator
    result = validator.validate(w1_plan, inputs, r1_slots, collection_plan=collection_plan)
    law_path = SOURCE_KIT / 'registration/sizing_b5.json'
    law_raw = frozen(root, ANCHOR_COMMIT, law_path)
    source = json.loads(law_raw)['packs']['align-pilot-v3']
    disk = source['disk_member_law']
    scaffold_bytes = source['disk_derivation']['scaffold_bytes']
    rows = w1_plan['align_v4']['members']
    seconds = {row['ordinal']: row['member_s'] for row in rows}
    member_bytes = {ordinal: math.ceil(disk['intercept'] + disk['slope'] * value
                                       + disk['largest_positive_residual'])
                    for ordinal, value in seconds.items()}
    n = len(rows)
    scaffold_count = sum(s['expected_count'] for s in tree['stage_graph']
                         if s['kind'] == 'campaign_collection') - n
    b_bytes = sum(member_bytes.values()) + scaffold_bytes
    t_stream = max(seconds.values())
    return {'schema_version': 'joulewise.b5_sizing.v1', 'non_claim': True,
            'derivation': ('ALIGN v4 W1 sizing from the R1-filled W1 plan (FINAL-DESIGN B8). member_s per '
                           'member is R1\'s; programmed_span_s = ceil(scaffold_s + sum member_s); '
                           'T_stream_max_s = max member_s (<= 1,800 s spent cap). Disk per member = '
                           'ceil(pilot-3 OLS bundle_bytes(member_s) + largest positive pilot-3 residual); '
                           'B = sum + measured pilot-3 scaffold bytes; two copies (FINAL-DESIGN 2.5, '
                           'Amendment 1: 18.71 GB per copy at the planning member_s).'),
            'sources': {'w1_plan': {'path': W1_PLAN.as_posix(), 'sha256': sha(w1_plan_raw)},
                        'disk_law': {'commit': ANCHOR_COMMIT, 'path': law_path.as_posix(),
                                     'sha256': sha(law_raw), 'pointer': '/packs/align-pilot-v3/disk_member_law'}},
            'packs': {PACK_ID: {
                'pack_id': PACK_ID, 'flags': [], 'align_members': n, 'scaffold_members': scaffold_count,
                'member_count': n + scaffold_count, 'B_D': inputs['R1']['B_D'],
                'member_seconds': {str(k): v for k, v in sorted(seconds.items())},
                'align_s': result['align_s'], 'scaffold_s': SCAFFOLD_S,
                'programmed_span_s': result['programmed_span_s'], 'window_max_s': result['window_max_s'],
                'span_limit_s': SPAN_LIMIT_S, 'T_stream_max_s': t_stream,
                'member_cap': {'spent_s': MEMBER_CAP_S}, 'fits_spent_cap': t_stream <= MEMBER_CAP_S,
                'disk_member_law': disk,
                'member_upper_bytes': {str(k): v for k, v in sorted(member_bytes.items())},
                'estimated_footprint_bytes': 2 * b_bytes,
                'disk_derivation': {'formula': ('ceil(pilot-3 OLS bundle_bytes(member_s) + largest positive '
                                                'pilot-3 residual) per member; plus measured pilot-3 scaffold; '
                                                'two copies'),
                                    'peak_copies': 2, 'B_bytes': b_bytes, 'scaffold_bytes': scaffold_bytes,
                                    'extra_wait_peak_bytes': 0, 'fixed_retained_bytes': 0}}}}


def require_sizing(root=ROOT):
    """prepare needs registration/sizing_b5.json; it exists only once R1 has filled the W1 plan."""
    if read_w1_plan_bytes(root) is None:
        raise ValueError(
            f'v4 kit BLOCKED: {SIZING} is not derivable yet. W1 sizing comes from R1 (FINAL-DESIGN B8): '
            'fill a copy of night_plan.template.json with R1\'s member_s, B_D, I_D, T_dead, '
            f'max_r1_tail_s and thermal policy, commit it as {W1_PLAN} (it must pass '
            'scripts/validate_align_v4_w1_plan.py), then regenerate the kit, which derives sizing_b5.json.')
    if not (Path(root) / SIZING).is_file():
        raise ValueError(f'{SIZING} is missing; regenerate the kit from {W1_PLAN}')
    # Sol w1rev: sizing_b5.json must be derived from the committed W1 plan's bytes.
    try:
        sizing = json.loads((Path(root) / SIZING).read_bytes())
        pinned = sizing['sources']['w1_plan']
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError(f'{SIZING} does not carry its W1-plan provenance: {exc}') from exc
    if not isinstance(pinned, dict) or pinned.get('path') != W1_PLAN.as_posix() \
            or pinned.get('sha256') != sha(read_w1_plan_bytes(root)):
        raise ValueError(f'{SIZING} is stale for {W1_PLAN}; regenerate the kit')


def validate_wp18_fixtures(inputs, root=ROOT):
    """Lead ruling R5-8: each filled WP18 digest binds a committed fixture.

    The fixture bytes are historical pilot-7 inputs, not kit output; a bare
    digest in inputs.json is not evidence that those bytes exist, so W1
    readiness requires both files, their sha256 and their recorded turn count.
    """
    root = Path(root)
    for name, relative in WP18_FIXTURES.items():
        path = root / relative
        if not path.is_file():
            raise ValueError(f'WP18.{name} token fixture is missing: commit {relative} '
                             '(scripts/align_v4_wp18_fixtures.py)')
        raw = path.read_bytes()
        expected = inputs['WP18'][name]['token_fixture_sha256']
        if sha(raw) != expected:
            raise ValueError(f'WP18.{name}.token_fixture_sha256 does not match {relative}: '
                             f'expected {expected}, observed {sha(raw)}')
        try:
            fixture = json.loads(raw)
        except ValueError as exc:
            raise ValueError(f'{relative} is not JSON: {exc}') from exc
        if (not isinstance(fixture, dict) or fixture.get('schema') != WP18_FIXTURE_SCHEMA
                or fixture.get('arm') != name or fixture.get('run_id') != WP18_RUN_IDS[name]
                or fixture.get('max_turns') != inputs['WP18'][name]['max_turns']
                or not isinstance(fixture.get('turns'), list) or len(fixture['turns']) != fixture['max_turns']):
            raise ValueError(f'{relative} is not the WP18 {name} fixture for {WP18_RUN_IDS[name]} with '
                             f'max_turns {inputs["WP18"][name]["max_turns"]}')


def require_w1_ready(root=ROOT):
    """Everything W1 prepare/arm needs from the kit: inputs, D identity, R1 sizing, WP18 fixtures."""
    inputs = read_inputs(root)
    if not any(p.startswith('WP11.') for p in pending_inputs(inputs)):
        pins_raw = (Path(root) / D_PINS).read_bytes()
        validate_d_identity(inputs['WP11'], json.loads(pins_raw), pins_raw=pins_raw)
    require_ready(inputs, read_r1_slots(root))
    require_sizing(root)
    validate_wp18_fixtures(inputs, root)


def valid_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def bundle_config_bytes(config):
    """Serialize a normalized config exactly as RunBundleWriter.create does."""
    return (json.dumps(config.to_dict(), indent=2, sort_keys=True) + '\n').encode('utf-8')


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
        if 18 in ordinals:
            ordinals.remove(18)
            actions.append({'drop_ordinal': 18})
        elif budget > BUDGET_FLOOR:
            budget -= 1024
            actions.append({'B_D': budget})
        else:
            raise ValueError('roster does not fit at B_D=6144 after dropping 18; return to lead')


def _rewrite(value):
    if isinstance(value, str):
        return value.replace(str(SOURCE_KIT), str(KIT)).replace('align-pilot-v3', PACK_ID).replace(
            'align_pilot_v3', 'align_v4')
    if isinstance(value, list):
        return [_rewrite(v) for v in value]
    if isinstance(value, dict):
        return {k: _rewrite(v) for k, v in value.items()}
    return value


def thermal_policy(inputs, *, heavy, per_turn, window_reference):
    value = deepcopy(inputs['R1']['thermal_policy'])
    if value is None:
        value = dict(sensors=None, delta_fast_c=None, delta_slow_c=None,
                     turn_cap_s=None, chunk_tokens=None)
    value.update(heavy=heavy, per_turn=per_turn)
    value['window_reference'] = window_reference
    return value


def build_files(root=ROOT):
    root = Path(root)
    inputs = read_inputs(root)
    files = {INPUTS: (root / INPUTS).read_bytes(), R1_SLOTS: (root / R1_SLOTS).read_bytes()}
    w1_plan_raw = read_w1_plan_bytes(root)
    if w1_plan_raw is not None:
        files[W1_PLAN] = w1_plan_raw
    ac_powermode = read_r1_slots(root).get("ac_powermode")
    old_tree = json.loads(frozen(root, ANCHOR_COMMIT, SOURCE_KIT / 'plan_tree.json'))
    tree = _rewrite(old_tree)
    stages = [s for s in tree['stage_graph'] if '-episodes-' in s['stage_id']]
    rows_by_stage = [[], []]
    members = []
    source_receipts = []
    anchor_configs = []
    capture_run_id = None
    capture_config_sha256 = None
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
            # D members are cloned from anchor 1 (spam); the runtime builds the
            # task from task_kwargs, so the roster pair must be written here.
            spec['task_kwargs'] = {**spec['task_kwargs'], 'task_pair': pair}
            if name == 'D':
                config['model'].update(name='Qwen3.8-27B-8bit', family='qwen3_5',
                                       source=D_SOURCE, revision=D_REVISION)
                config['quantization'] = {'name': 'int8', 'bits': 8, 'group_size': 64}
                reference = ({'role': 'capture'} if ordinal == 5 else
                             {'role': 'consume', 'source_run_id': capture_run_id,
                              'source_config_sha256': capture_config_sha256})
                spec.update(sampler=D_SAMPLER, temperature=1.0, assistant_history='reasoning_content',
                            chat_template_kwargs={'reasoning_effort': inputs['R0']['reasoning_effort']},
                            max_episode_decode_tokens=inputs['R1']['B_D'], deadman_s=inputs['R1']['T_dead'],
                            hybrid_checkpoint_limit=0, thermal=thermal_policy(
                                inputs, heavy=True, per_turn=True, window_reference=reference))
            else:
                reference = {'role': 'consume', 'source_run_id': capture_run_id,
                             'source_config_sha256': capture_config_sha256}
                spec.update(max_turns=inputs['WP18'][name[0]]['max_turns'],
                            deadman_s=CONTRAST_DEADMAN_S,
                            thermal=thermal_policy(inputs, heavy=False, per_turn=name.endswith('G'),
                                                   window_reference=reference))
            config['workload_profile']['prompt_text'] = json.dumps(spec, sort_keys=True, separators=(',', ':'), allow_nan=False)
            model_id = D_TAG if name == 'D' else 'qwen3-30b-a3b'
            config['run_metadata']['tags'] = [PACK_ID, 'non-claim', 'launch_lineage_required', 'align', 'align_episode',
                'align-model=' + model_id, 'align-condition=' + condition, 'align-task=' + pair,
                'align-repeat=' + ('2' if ordinal in (12, 13, 15, 16, 17) else '1'),
                'align-stage=episodes-' + ('a' if half == 0 else 'b')]
            raw = raw_json(config)
            if ordinal == 5:
                from joulewise.schemas import BenchmarkConfig
                capture_run_id = config['run_id']
                capture_config_sha256 = sha(bundle_config_bytes(BenchmarkConfig.from_mapping(config)))
            filename = config['run_id'] + '.json'
        spec = json.loads(config['workload_profile']['prompt_text'])
        path = directory / filename
        files[path] = raw
        model_id = D_TAG if name == 'D' else 'qwen3-30b-a3b'
        seed = episode_seed(model_id, 'thinking_on', 'shade/' + pair, seed_index)
        replay_of = {12: 10, 13: 9, 15: 7, 16: 6, 17: 5}.get(ordinal)
        row = dict(ac_powermode=ac_powermode, run_id=config['run_id'], config=filename, config_path=path.as_posix(), config_sha256=sha(raw),
                   index=len(rows_by_stage[half]) + 1, rep=2 if replay_of else 1, role='absolute_repeat',
                   block_id=None, block_index=len(rows_by_stage[half]) + 1, position=None, position_in_block=1,
                   arm=None, model_tag=model_id + '-mlx', workload='align_episode',
                   module_id=PACK_ID + '-' + model_id, pack_id=PACK_ID)
        rows_by_stage[half].append(row)
        member = dict(ac_powermode=ac_powermode, ordinal=ordinal, run_id=config['run_id'], stage_id=stage['stage_id'],
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
                runtime_requirements=dict(
                    ac_powermode=ac_powermode, D_tools='family-validated XML via qwen3_5', presence_penalty=0,
                    # Fable cold pass LOW-7 (LEAD-RULINGS-2 R5-7): W1 members run
                    # from their own configs through the plan's stage commands;
                    # their specs carry the custody roles (member 5 captures,
                    # members 6-18 consume member 5). The WP15 R1 runtime is the
                    # R1 rehearsal's argv only and is never a W1 launcher.
                    window_reference=dict(capture_ordinal=WINDOW_REFERENCE_CAPTURE_ORDINAL,
                                          capture_run_id=capture_run_id,
                                          capture_config_sha256=capture_config_sha256,
                                          rule='member 5 captures its last 60 s of idle before warmup '
                                               '(role capture); every later thermal member consumes it '
                                               '(role consume, bound to member 5 run_id and config bytes)'),
                    w1_launcher='per-member configs via the plan_tree stage commands (the specs carry the roles)',
                    r1_runtime_entrypoint=inputs['WP15']['runtime_entrypoint']))
    check_window_reference_roles(plan)
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
    if w1_plan_raw is not None:
        files[SIZING] = raw_json(derive_sizing(root, json.loads(w1_plan_raw), inputs, read_r1_slots(root),
                                               tree, plan, w1_plan_raw))
    files[KIT / 'registration/sizing_preview.json'] = raw_json(dict(
        status='PROVISIONAL_NOT_ARM_SIZING', non_claim=True, align_members=18, scaffold_s=SCAFFOLD_S,
        planning_align_s=21931.27, planning_span_s=26927, span_limit_s=SPAN_LIMIT_S,
        planning_window_max_s=44640, planning_two_copy_GB=37.4,
        member_seconds={'anchor': 3131.27 / 4, 'D': 1800, 'G': 1150, 'S': 850},
        fit_rule=['drop ordinal 18', 'lower B_D by 1024 to 6144', 'return to lead'],
        note=('R1 must replace guesses and requalify budget; sizing_b5.json is derived from the '
              'R1-filled registration/w1_plan.json, never from this preview.')))
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
            # Like the inherited 30B units: no C4 stack identity is observed.
            unit.setdefault('stack_identity', {})
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
        status=('PROVISIONAL_PENDING_WP11' if inputs['WP11']['local_file_verification'] is None
                else 'WP11_D_FROM_R0_RECORD'), D=inputs['WP11']['local_file_verification'],
        inherited_30B_commit=ANCHOR_COMMIT, note='No local files were inspected by this builder.'))


WINDOW_REFERENCE_CAPTURE_ORDINAL = 5


def check_window_reference_roles(plan):
    """Protocol v4 WP14(b): member 5 captures R; every later thermal member
    consumes member 5's custody (cold pass LOW-7). Refuse a plan whose specs
    say anything else, or whose runtime block names another launcher."""
    members = plan['members']
    capture = next(m for m in members if m['ordinal'] == WINDOW_REFERENCE_CAPTURE_ORDINAL)
    for member in members:
        thermal = member['spec'].get('thermal')
        if thermal is None:
            if member['ordinal'] >= WINDOW_REFERENCE_CAPTURE_ORDINAL:
                raise ValueError(f'member {member["ordinal"]} has no thermal policy (window reference)')
            continue
        role = thermal.get('window_reference')
        if member['ordinal'] == WINDOW_REFERENCE_CAPTURE_ORDINAL:
            expected = {'role': 'capture'}
        elif member['ordinal'] > WINDOW_REFERENCE_CAPTURE_ORDINAL:
            expected = {'role': 'consume', 'source_run_id': capture['run_id'],
                        'source_config_sha256': capture['config_sha256']}
        else:
            raise ValueError(f'member {member["ordinal"]} precedes the capture member but carries a thermal policy')
        if role != expected:
            raise ValueError(f'member {member["ordinal"]} window_reference {role!r} != {expected!r}')
    block = plan['runtime_requirements']
    if 'launcher' in block:
        raise ValueError('runtime_requirements.launcher is ambiguous: the R1 runtime is not the W1 launcher')
    reference = block.get('window_reference') or {}
    if (reference.get('capture_ordinal') != WINDOW_REFERENCE_CAPTURE_ORDINAL
            or reference.get('capture_run_id') != capture['run_id']
            or reference.get('capture_config_sha256') != capture['config_sha256']):
        raise ValueError('runtime_requirements.window_reference does not name member 5 as the capture member')


def validate_powermode_members(plan, observed_by_run):
    """Arm/desk secondary validation; frozen pilot analysis remains untouched.

    A member whose plan carries no frozen series value (expected not 0 or 2)
    is a mismatch even when nothing was observed: None == None is not a match
    (cold pass LOW 1).
    """
    mismatches = []
    for member in plan['members']:
        expected = member.get('ac_powermode')
        observed = observed_by_run.get(member['run_id'])
        if type(expected) is not int or expected not in (0, 2) or observed != expected:
            mismatches.append({'run_id': member['run_id'], 'expected': expected, 'observed': observed})
    return {'instrument_ok': not mismatches, 'powermode_mismatches': mismatches}


def arm_powermode_check(plan, observed_ac_powermode):
    expected = plan.get('runtime_requirements', {}).get('ac_powermode')
    if type(expected) is not int or expected not in (0, 2):
        raise ValueError(f'AC powermode: the plan freezes no series value (got {expected!r})')
    if observed_ac_powermode != expected:
        raise ValueError(f'AC powermode mismatch: expected {expected}, observed {observed_ac_powermode}')


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
        require_w1_ready(source_root)
    return files


README = """# ALIGN v4 W1 skeleton — PROVISIONAL, NON-CLAIM

Build: `python3.13 -B scripts/align_v4_kit.py`. Check: add `--check`.
`--check` MUST FAIL while registration/inputs.json contains pending inputs.
No study/model path is followed. All source configs come from pinned Git objects.

18 members per Amendment A1: four exact original anchors, eight 30B contrast
runs and six D runs. Midpoint follows ordinal 9. D uses seed 1 (both pairs and
conditions), development 93 at ordinal 18, and a replay of 5 at 17. Development
91–92 are reserved for R0; held-out starts at 2, excluding development indices.
The window-plan draft's D index 101 is superseded by synthesized WP16/A1.
Checkpointing is explicitly off for D throughout the series, superseding A1.

WP11 (supplied) binds D's six weight shards: the R0 re-run record's governed
model_artifact_identity, checked shard by shard against the HF LFS pins at
815b83c0 (configs/align/v4/qwen38-27b-8bit-hf-pins.json); the folded sha256
recomputes from the pins alone. WP18 (Mac-side) must provide X=b-e25/index16
and Y=b-e18/index14 recorded pilot-7 turn counts and the token-id fixture
digest. No configured 12-turn fallback is used for the contrast.
R0.reasoning_effort stays a placeholder until R0 passes.
R1 must select B_D, I_D, T_dead, sensors, bands, recovery cap and chunk size.
T_dead follows lead ruling L1: min((1750 - I_D), (1800 - I_D - max_r1_tail_s
- 10)) / 1.13544, with max_r1_tail_s from r1_slots; --check asserts that
I_D + 1.13544 T_dead + max_r1_tail_s + 10 <= 1800.
Missing numeric controls are null and invalid as executable EpisodeSpecs.
The existing qwen3_5 endpoint selects XML tools from the model family.
Presence penalty remains the endpoint's fixed zero; sampler is 1/.95/20/0.

Window reference R: member 5 captures its last 60 s of idle before neutral
warmup (role capture); all later sidecar members consume it (role consume,
bound to member 5's run_id and config bytes). The plan records this in
runtime_requirements.window_reference and --check refuses any other roles.
W1 members run from their own configs through the plan's stage commands; the
WP15 R1 runtime (runtime_requirements.r1_runtime_entrypoint) runs R1 only.
The scaffold's campaign commands remain a skeleton pending the W1 wiring.
No synthetic sensor, reference temperature, model digest or turn count is used.

Sizing_preview.json contains A1's planning guesses only. sizing_b5.json comes
from R1 (FINAL-DESIGN B8): once registration/w1_plan.json (the R1-filled copy
of night_plan.template.json) is committed and validates, the kit derives
sizing_b5.json from its member_s (span, window, T_stream_max_s) and the
pilot-3 disk law (two copies). Until then --check and prepare refuse with
that reason. Use fit_roster with R1 measured cost estimates:
drop only 18 first, then decrease B_D by 1024 down to 6144; otherwise return
to lead. Preserve anchors, contrasts and 5/17. Requalify/freeze changed budgets.
W1 arm (align_v4_session.py install --w1-disk-config) runs the R0 host
w1_disk_gate: >=80 decimal GB free after R0 and every configured offload
re-hashed; anything but pass refuses the arm.
The additive align_v4_session.py refuses prepare/install while inputs are pending.
Its desk is the parameterized pilot instrument desk; WP21 owns full U4–U6,
K-session and contrast reporting. This kit grants no arm or hardware approval.

`night_plan.template.json` is the fail-closed Window-1 planning sheet for the
pilot night-plan v5 family; it is not itself a run_night plan (prepare writes
that). Every R1 value, including every member cost, is an explicit
`PENDING_R1` value. Validate a separately filled copy with
`python3 -B scripts/validate_align_v4_w1_plan.py <copy>`; the command refuses
any placeholder or disagreement with registration/inputs.json (and with
r1_slots.json max_r1_tail_s), applies lead ruling L1 to T_dead, validates the
template's own heavy/per_turn gate policy, and recomputes both the 26,940 s
span cap and 44,640 s window maximum. After any kit regeneration, rebuild the
template's member bindings with `--regenerate-template`. The template is not
custody, an arm receipt, or an installation.
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
