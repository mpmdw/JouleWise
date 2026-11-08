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
from joulewise.align.apple import km003c, r1_runtime, thermal_gates
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
        # R11 contrast evidence deliberately retains unknown timings; its exact
        # non-veto record is validated separately, never treated as D input.
        if path == 'R1.thermal_policy.contrast_fit':
            return
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


def check_r1_evidence(inputs, r1_slots, *, synthetic=False, receipt=None):
    """Bind r1_slots to R1 evidence (executing review MEDIUM-3).

    The record must be the R1 driver's own (schema and hardware source; the
    synthetic source only for the WP22/tests harness that asks for it), its
    step-d I_D must equal inputs.R1.I_D, the frozen AC powermode must follow
    the A-B-A verdict, max_r1_tail_s must be the largest gated-run tail, U5
    must carry a verdict, every ruling 20 census must have passed, and the
    duty bar must pass or carry a recorded lead fallback step (ruling 1(e)).
    ``receipt`` is the lead's committed ruling 1(f) receipt or None
    (LEAD-RULINGS-2 R10-4); R11 binds a non-veto contrast cap/fit on every path.
    """
    if not isinstance(r1_slots, dict) or r1_slots.get('schema') != R1_SLOTS_SCHEMA:
        raise ValueError(f'R1 r1_slots must be a {R1_SLOTS_SCHEMA} record')
    allowed = (R1_HARDWARE_SOURCE, R1_SYNTHETIC_SOURCE) if synthetic else (R1_HARDWARE_SOURCE,)
    if r1_slots.get('source') not in allowed:
        raise ValueError(f'R1 r1_slots source must be {R1_HARDWARE_SOURCE!r}, not {r1_slots.get("source")!r}')
    inconclusive = r1_slots.get('inconclusive_segments')
    if not isinstance(inconclusive, dict):
        raise ValueError('R1 r1_slots must record inconclusive_segments (LEAD-RULINGS-2 R6-2)')
    if STEP_D_SEGMENT in inconclusive:
        # LEAD-RULINGS-2 R6-2: recorded by the driver, refused here (fail closed at the kit).
        raise ValueError(f'R1 step-d was INCONCLUSIVE ({inconclusive[STEP_D_SEGMENT]}): no slots, no thermometry '
                         'bar and no gated runs; W1 cannot be sized from this R1 record; '
                         'the remedy is an R1 re-run, which is the magistrate\'s call, '
                         'with no per-occurrence lead ruling (LEAD-RULINGS-2 R7-3)')
    if {k: v for k, v in inconclusive.items() if k != 'X_G_contrast'}:
        # A designed start state that was never reached leaves beta_T (U5)
        # without a point; before R6-2 it refused the night, so it still
        # refuses W1 here (Sol critique of round 6).
        raise ValueError('R1 calibration segment(s) INCONCLUSIVE (R6-2): ' + ', '.join(sorted(inconclusive))
                         + '; the remedy is an R1 re-run, which is the magistrate\'s call, '
                         'with no per-occurrence lead ruling (LEAD-RULINGS-2 R7-3)')
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
    digest = policy.get('classification_sha256') if isinstance(policy, dict) else None
    if not valid_digest(digest) or digest != classified.get('classification_sha256'):
        raise ValueError('inputs.R1.thermal_policy.classification_sha256 must be a 64-hex digest matching '
                         'r1_slots.thermometry.D.classification_sha256')
    sensors = policy.get('sensors') if isinstance(policy, dict) else None
    aliases = classified.get('alias_groups')
    seen = set()
    if not isinstance(aliases, list):
        raise ValueError('R1 thermometry.D.alias_groups must record the classification aliases '
                         '(LEAD-RULINGS-2 R7-13); missing aliases cannot verify independence')
    for group in aliases:
        if (not isinstance(group, list) or len(group) < 2
                or not all(isinstance(key, str) and key for key in group)
                or group != sorted(set(group)) or seen.intersection(group)):
            raise ValueError('R1 thermometry.D.alias_groups must be sorted groups of at least two strings, '
                             'with no key in two groups (LEAD-RULINGS-2 R7-13)')
        seen.update(group)
    if isinstance(sensors, dict):
        fast, slow = sensors.get('s_fast'), sensors.get('s_slow')
        if fast == slow or any(fast in group and slow in group for group in aliases):
            raise ValueError('R1.thermal_policy s_fast/s_slow: aliased keys are one thermometer '
                             '(LEAD-RULINGS-2 R7-13)')
        if sensors.get('s_fast') not in (classified.get('die_candidates') or ()):
            raise ValueError(f'R1.thermal_policy s_fast {sensors.get("s_fast")!r} is not in the R1 die list')
        if sensors.get('s_slow') not in (classified.get('heatsink_candidates') or ()):
            raise ValueError(f'R1.thermal_policy s_slow {sensors.get("s_slow")!r} is not in the R1 heatsink list')
        if any(sensors.get(role) != classified.get(role) for role in ('s_fast', 's_slow')):
            raise ValueError('R1.thermal_policy sensors must equal the R1 thermometry.D picks')
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
    check_r1_fast_band(inputs['R1'], r1_slots)
    check_r1_budget_and_policy(inputs['R1'], r1_slots, receipt=receipt,
                               x_max_turns=((inputs.get('WP18') or {}).get('X') or {}).get('max_turns'))
    check_duty_bar_consistency(r1_slots)
    duty = r1_slots.get('duty_bar')
    if not isinstance(duty, dict) or type(duty.get('pass')) is not bool:
        raise ValueError('R1 r1_slots must carry the ruling 1(d) duty bar verdict')
    # LEAD-RULINGS-2 R6-1: the bar was measured under W1's inter-member schedule.
    schedule = duty.get('schedule')
    expected = w1_inter_member_idle_s()
    if (not isinstance(schedule, dict) or schedule.get('authority') != 'LEAD-RULINGS-2 R6-1'
            or schedule.get('inter_member_idle_s') != expected):
        raise ValueError('R1 duty bar must record the R6-1 schedule: each gated D run and X-G after a D turn with '
                         f'only W1\'s configured idle {expected} (duty_bar.schedule)')
    if not duty['pass']:
        raise ValueError('R1 duty bar failed: no lead fallback step alone qualifies; supply a qualified remeasured '
                         'final R1 record. Idle-450/4-bit steps are not expressible in this 8-bit kit (R11/R08)')
    opportunity = turn_opportunity(r1_slots, inputs['R1']['B_D'])
    if opportunity['status'] != 'pass':
        raise ValueError('R11 turn opportunity at chosen B_D is ' + opportunity['status'] +
                         '; qualified per-turn counts and >=3 admitted turns per gated D run required')


STEP_D_SEGMENT = 'step_D_prefill_10k_decode_4096'
W1_PLAN_TEMPLATE = KIT / 'night_plan.template.json'
W1_SCHEDULE_ROLES = ('D', 'X-G')


def w1_inter_member_idle_s(root=ROOT):
    """LEAD-RULINGS-2 R6-1: W1's inter-member schedule per roster role (D and
    X-G): the configured idle (``sampling.idle_seconds``) of the member
    configs the W1 plan template lists. One value per role, or ValueError."""
    plan = json.loads((Path(root) / W1_PLAN_TEMPLATE).read_bytes())
    by_role = {}
    for member in plan['align_v4']['members']:
        config = json.loads((Path(root) / member['config_path']).read_bytes())
        idle = config['sampling']['idle_seconds']
        if not finite(idle) or idle < 0:
            raise ValueError(f'{member["config_path"]}: sampling.idle_seconds must be finite and >= 0')
        by_role.setdefault(member['role'], set()).add(float(idle))
    out = {}
    for role in W1_SCHEDULE_ROLES:
        values = by_role.get(role, set())
        if len(values) != 1:
            raise ValueError(f'W1 plan: the {role} members do not share one configured idle ({sorted(values)})')
        out[role] = values.pop()
    return out


def _close(a, b):
    return finite(a) and finite(b) and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def check_r1_fast_band(r1_inputs, r1_slots):
    """Cold LOW-1 (lead ruling R6-8): delta_fast_c binds a recorded R1 fast band.

    Unchanged picks: the soak fast band of the gate keys (slots.S5_fast).
    Round-6 integration, with R6-4: when R1 changes the picks, S5_fast still
    describes R0's fast key, so delta_fast_c binds the fast band computed for
    the R1 picks (thermometry.D.s7_for_r1_picks.band_c.s_fast), like S6/S7."""
    policy = r1_inputs.get('thermal_policy')
    policy = policy if isinstance(policy, dict) else {}
    classified = (r1_slots.get('thermometry') or {}).get('D') or {}
    if classified.get('sensor_pick_changed') is True:
        computed = classified.get('s7_for_r1_picks')
        band = computed.get('band_c') if isinstance(computed, dict) else None
        fast = band.get('s_fast') if isinstance(band, dict) else None
        source = 'r1_slots.thermometry.D.s7_for_r1_picks.band_c.s_fast'
        if not finite(fast) or fast <= 0:
            raise ValueError(f'{source}: the R1-pick fast band was not computed (finite, positive required)')
    else:
        fast = (r1_slots.get('slots') or {}).get('S5_fast')
        source = 'r1_slots.slots.S5_fast'
    if not _close(policy.get('delta_fast_c'), fast):
        raise ValueError(f'inputs.R1.thermal_policy.delta_fast_c must equal {source}')


def rederive_r1_pick_s7(computed, source):
    """LEAD-RULINGS-2 R9-2: re-derive the changed-pick bands and S7 with the
    runtime's own functions (r1_runtime.pick_band, r1_runtime.pick_s7), on the
    classifier's D2 baseline (last-60 s quiet median, OLS residual SD). A record
    computed on another baseline (the pre-R9-2 whole-window median and raw SD)
    or whose numbers differ from the re-derivation cannot bind W1."""
    if computed.get('rule') != r1_runtime.R1_PICK_S7_RULE:
        raise ValueError(f'{source}.rule is not the R9-2 rule (the classifier\'s D2 baseline: last-60 s quiet '
                         f'median and OLS residual SD); got {computed.get("rule")!r}')
    noise = computed.get('noise_c') if isinstance(computed.get('noise_c'), dict) else {}
    band = computed.get('band_c') if isinstance(computed.get('band_c'), dict) else {}
    for role in ('s_fast', 's_slow'):
        sd = noise.get(role)
        if not finite(sd) or sd < 0:
            raise ValueError(f'{source}.noise_c.{role} must be the finite, non-negative D2 residual SD (R9-2)')
        if not _close(band.get(role), r1_runtime.pick_band(sd)):
            raise ValueError(f'{source}.band_c.{role} {band.get(role)!r} differs from the re-derivation '
                             f'max(1.0, 3 x noise_c.{role}) = {r1_runtime.pick_band(sd)!r} (R9-2)')
    recovery = computed.get('recovery_s')
    if not finite(recovery) or recovery < 1.0:
        raise ValueError(f'{source}.recovery_s must be a finite recovery of at least 1 s (R9-2)')
    if not _close(computed.get('S7'), r1_runtime.pick_s7(recovery)):
        raise ValueError(f'{source}.S7 {computed.get("S7")!r} differs from the re-derivation '
                         f'min(300, 3 x recovery_s) = {r1_runtime.pick_s7(recovery)!r} (R9-2)')


def check_duty_bar_consistency(r1_slots):
    """Re-derive FAIL > INCONCLUSIVE > PASS from the driver's per-run bars."""
    rows = r1_slots.get('deadman_budget')
    bars = [row.get('duty_bar') for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    verdicts = [bar.get('verdict') if isinstance(bar, dict) else None for bar in bars]
    if not verdicts or any(v not in ('pass', 'inconclusive', 'fail') for v in verdicts):
        raise ValueError('R1 deadman_budget must carry a duty_bar.verdict for every run')
    verdict = 'fail' if 'fail' in verdicts else 'inconclusive' if 'inconclusive' in verdicts else 'pass'
    duty = r1_slots.get('duty_bar')
    if not isinstance(duty, dict) or duty.get('verdict') != verdict or duty.get('pass') is not (verdict == 'pass'):
        raise ValueError('R1 duty_bar verdict/pass disagrees with the per-run duty verdicts')
    if verdict == 'pass' and any(row.get('x7') is not False for row in rows):
        raise ValueError('R11: no X7/deadman waiver is installed; passing duty labels require explicit no-X7 evidence')


# The R1 driver's three gated D runs (council ruling 1(b)); ruling 1(f) is
# judged over all three, never a subset.
GATED_D_RUN_NAMES = ('D_spam_benign_s1_gated_held_a', 'D_spam_benign_s1_gated_held_b',
                     'D_bank_benign_s1_gated_held')


def turn_opportunity(r1_slots, b_d):
    """Count observed whole-turn admissions at W1's chosen B_D (R11/R16).

    Count exports are lead-owned backfills from explicit bundle bytes; their
    source digest binds the export. Missing/censored completion evidence never
    implies a third turn or qualifies a budget-X7 exception.
    """
    rows = r1_slots.get('deadman_budget', [])
    if (type(b_d) is not int or b_d <= 0 or not isinstance(rows, list)
            or len(rows) != 3 or any(not isinstance(r, dict) for r in rows)
            or {r.get('run') for r in rows} != set(GATED_D_RUN_NAMES)):
        return {'status': 'inconclusive', 'B_D': b_d, 'runs': [], 'reason': 'missing gated D roster/budget'}
    results = []
    cap = (r1_slots.get('budget_fit_inputs') or {}).get('turn_cap_tokens')
    for row in rows:
        counts, completed = row.get('turn_decode_counts'), row.get('turn_completed')
        valid = (type(cap) is int and isinstance(counts, list) and bool(counts)
                 and all(type(n) is int and 0 <= n <= cap for n in counts)
                 and isinstance(completed, list) and len(completed) == len(counts)
                 and all(type(v) is bool for v in completed)
                 and all(completed[:-1]) and sum(counts) == row.get('decode_tokens')
                 and row.get('admitted_turns') == len(counts)
                 and valid_digest(row.get('turn_counts_source_sha256')))
        used = admitted = 0
        if valid:
            for n in counts:
                if used >= b_d:
                    break
                admitted += 1
                used += n
        results.append({'run': row.get('run'), 'admitted_at_B_D': admitted if valid else None,
                        'status': ('pass' if admitted >= 3 else 'fail') if valid else 'inconclusive'})
    status = ('inconclusive' if any(r['status'] == 'inconclusive' for r in results)
              else 'fail' if any(r['status'] == 'fail' for r in results) else 'pass')
    return {'status': status, 'B_D': b_d, 'runs': results,
            'limitation': 'Observed benign opportunity only; no guarantee before EOS/context/deadman or of sabotage capability.'}


GATED_PHASES = ('G0', 'G1', 'H', 'decode', 'prefill', 'tool', 'tail')
S6_TUNING_CAP_C = 2.0   # council ruling 1(e) step 1: delta_slow capped at 2.0 C


def d_turn_cap_tokens(root=ROOT):
    """The per-turn decode cap every W1 D member inherits (D configs are cloned
    from anchor 1 at ANCHOR_COMMIT and keep its ``max_tokens``)."""
    raw = frozen(root, ANCHOR_COMMIT, SOURCE_KIT / 'stages/episodes-a/align-pilot-v3-episodes-a-e01.json')
    return json.loads(json.loads(raw)['workload_profile']['prompt_text'])['max_tokens']


def r1_g0_timeout_s(root=ROOT):
    """The single configured R1 G0 timeout (LEAD-RULINGS-2 R7-2)."""
    config = json.loads((Path(root) / 'configs/align/v4/r1_runtime.json').read_bytes())
    value = config.get('g0_timeout_s') if isinstance(config, dict) else None
    if not finite(value) or not thermal_gates.G0_CAP_DEFAULT_S <= value <= thermal_gates.G0_CAP_MAX_S:
        raise ValueError('R1 g0_timeout_s must be finite and in '
                         f'[{thermal_gates.G0_CAP_DEFAULT_S}, {thermal_gates.G0_CAP_MAX_S}]')
    return float(value)


def w1_g0_cap(r1_slots, root=ROOT):
    """Re-derive W1's G0 cap from every gated D and X-G wait (R7-2, R7-12).

    Unreleased/censored G0 intervals count at the full R1 timeout. An X-G
    without a measured release falls back to that timeout and still admits.
    """
    timeout = r1_g0_timeout_s(root)
    rows = r1_slots.get('deadman_budget') if isinstance(r1_slots, dict) else None
    names = [row.get('run') if isinstance(row, dict) else None for row in rows] if isinstance(rows, list) else []
    if sorted(map(str, names)) != sorted(GATED_D_RUN_NAMES):
        raise ValueError('R1 deadman_budget must hold exactly the three gated D runs (ruling 1(f), R7-2)')
    waits, censored = {}, []

    def count(name, outcome, wait):
        if outcome not in ('released', 'timeout', 'deadman', 'unobserved'):
            raise ValueError(f'{name}: missing or malformed g0_outcome (LEAD-RULINGS-2 R7-2)')
        if not finite(wait) or wait < 0:
            raise ValueError(f'{name}: G0 wait must be finite and non-negative (LEAD-RULINGS-2 R7-2)')
        # A G0 that did not release is censored: it counts at the full R1 timeout.
        waits[name] = float(wait) if outcome == 'released' else timeout
        if outcome != 'released':
            censored.append(name)

    for row in rows:
        phases = row.get('phases_s')
        count(row['run'], row.get('g0_outcome'), phases.get('G0') if isinstance(phases, dict) else None)
    x_g = r1_slots.get('x_g')
    if not isinstance(x_g, dict) or x_g.get('status') not in ('measured', 'inconclusive', 'not_run'):
        raise ValueError('R1 r1_slots.x_g must be an object with a measured/inconclusive/not_run status (R7-12)')
    # R7-12: an X-G that is not measured (INCONCLUSIVE) uses the R1 timeout
    # for W1's D-to-X G0 term and records x_g_fallback; that alone never
    # refuses, so its outcome and wait are recorded but not required.
    fallback = x_g['status'] != 'measured'
    if fallback:
        waits['X_G_contrast'] = timeout
        if x_g.get('g0_outcome') != 'released':
            censored.append('X_G_contrast')
    elif x_g['status'] == 'measured' and x_g.get('g0_outcome') != 'released':
        raise ValueError('X_G_contrast: a measured X-G needs a released g0_outcome (LEAD-RULINGS-2 R7-2)')
    else:
        count('X_G_contrast', 'released', x_g.get('g0_wait_s'))
    maximum = max(waits.values())
    floor, factor = float(thermal_gates.G0_CAP_DEFAULT_S), 1.25
    return {'authority': 'LEAD-RULINGS-2 R7-2, R7-12', 'r1_g0_timeout_s': timeout,
            'floor_s': floor, 'factor': factor, 'waits_s': waits, 'censored': censored,
            'x_g_fallback': fallback, 'max_g0_s': maximum,
            'value_s': int(min(max(math.ceil(factor * min(maximum, timeout)), floor), timeout)),
            'rule': 'clamp(ceil(1.25 * max counted gated D and X-G G0 wait), 600, R1 g0_timeout_s)'}


def gated_fit_inputs(r1_slots):
    """The three gated D rows, their phase seconds, r_decode and the turn cap
    (ruling 1(f), R6-3), validated as ruling_1f_fit always has."""
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
    step_rate = (fit or {}).get('r_decode_step_d_tok_per_s') if isinstance(fit, dict) else None
    cap = (fit or {}).get('turn_cap_tokens') if isinstance(fit, dict) else None
    if not finite(step_rate) or step_rate <= 0 or type(cap) is not int or cap <= 0:
        raise ValueError('R1 r1_slots must carry budget_fit_inputs (r_decode_step_d_tok_per_s, turn_cap_tokens) '
                         'for ruling 1(f)')
    rates = [step_rate]
    for row, p in zip(rows, phases):
        tokens = row.get('decode_tokens')
        if type(tokens) is not int or tokens < 0 or (tokens and p['decode'] <= 0):
            raise ValueError(f'ruling 1(f): {row.get("run")} must record its decode_tokens (an int >= 0, with '
                             'positive decode seconds when > 0) for the observed decode rate (R6-3)')
        if tokens:
            rates.append(tokens / p['decode'])
    rate = min(rates)
    recorded = fit.get('r_decode_tok_per_s')
    if not finite(recorded) or not math.isclose(recorded, rate, rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError(f'ruling 1(f): budget_fit_inputs.r_decode_tok_per_s {recorded!r} is not min(step-d, '
                         f'every gated run\'s observed decode rate) = {rate!r} (R6-3)')
    if cap != d_turn_cap_tokens():
        raise ValueError(f'ruling 1(f): the gated runs armed a {cap}-token turn cap, but W1 D members carry '
                         f'{d_turn_cap_tokens()}')
    return rows, phases, rate, cap


def projected_holds_s(rows, phases, tokens_target):
    """Audit-corrected D-f (LEAD-RULINGS-2 R10-4): each gated run's G1 + H
    projected per decoded token to ``tokens_target`` (symmetric with the decode
    term), never below what the run recorded; the maximum over the runs. A run
    that decoded nothing projects nothing, and refuses if it still recorded
    G1 or hold seconds."""
    values = []
    for row, p in zip(rows, phases):
        held, tokens = p['G1'] + p['H'], row['decode_tokens']
        if not tokens:
            if held > 0:
                raise ValueError(f'ruling 1(f): {row.get("run")} recorded {held} s of G1 + H with no decoded '
                                 'token, so its holds cannot be projected per token (R10-4)')
            values.append(0.0)
        else:
            values.append(max(held, held / tokens * tokens_target))
    return max(values)


def ruling_1f_fit(r1_slots, b_d, t_dead, *, receipt=None, x_max_turns=None):
    """Council ruling 1(f) for a B_D (lead ruling R5-4): the worst case R1
    measured must fit T_dead.

    worst = G0 term + holds + max (prefill + tool) over the gated D runs
            + (B_D + turn_cap_tokens) / r_decode

    Without a lead receipt (exactly the e901eb2a4 rule; cold-review
    disposition MEDIUM-2): the G0 term is R7-2's G0_cap_W1 over the three
    gated D waits and X-G (unreleased waits and an INCONCLUSIVE X-G at the R1
    timeout, R7-12) and holds is the recorded max (G1 + H).
    With a verified R10-2(a) receipt (``receipt``): the G0 term is the
    receipt's sub-600 s D cap, the armed cap, and holds is projected per
    decoded token to B_D + turn_cap_tokens (R10-4, the audit's corrected D-f).
    A turn is admitted while fewer than B_D decode tokens are spent and then
    keeps its full per-turn cap (FD:263), so B_D + cap bounds the episode
    decode. LEAD-RULINGS-2 R6-3: r_decode = min(step-d's measured rate, every
    gated run's observed rate), re-derived here from
    ``budget_fit_inputs.r_decode_step_d_tok_per_s`` and each deadman_budget
    row's ``decode_tokens`` / ``phases_s.decode`` (a run that decoded nothing
    has no rate). Returns the arithmetic.
    """
    rows, phases, rate, cap = gated_fit_inputs(r1_slots)
    g0_cap = w1_g0_cap(r1_slots)
    d_cap = w1_d_g0_cap(r1_slots)
    if receipt is None:
        g0_term, holds, rule = g0_cap['value_s'], max(p['G1'] + p['H'] for p in phases), 'R6-3, R7-2 G0_cap_W1'
    else:
        verified = verify_ruling_1f_receipt(receipt, r1_slots, t_dead, x_max_turns)
        g0_term = verified['derivation']['d_g0_cap_s']
        holds = projected_holds_s(rows, phases, b_d + cap)
        rule = 'R10-2(a) receipt'
    terms = {'G0_s': g0_term, 'holds_s': holds,
             'prefill_tool_s': max(p['prefill'] + p['tool'] for p in phases),
             'decode_s': (b_d + cap) / rate}
    worst = math.fsum(terms.values())
    return {'B_D': b_d, 'T_dead_s': t_dead, 'terms_s': terms, 'r_decode_tok_per_s': rate, 'worst_s': worst,
            'g0_cap_w1': g0_cap, 'd_g0_cap': d_cap, 'rule': rule, 'fits': worst <= t_dead + 1e-6}


G0_CAP_FACTOR = 1.25


def _role_cap(wait, timeout):
    """R7-2's clamp(ceil(1.25 x wait), 600, R1 timeout)."""
    floor = float(thermal_gates.G0_CAP_DEFAULT_S)
    return int(min(max(math.ceil(G0_CAP_FACTOR * min(wait, timeout)), floor), timeout))


def w1_d_g0_cap(r1_slots, root=ROOT):
    """LEAD-RULINGS-2 R10-4: W1's D-role G0 cap, from the three gated D waits
    only (X-G no longer sets D's term). Unreleased waits count at the R1
    timeout (R7-2), as in w1_g0_cap, which re-derives the recorded R7-2 slot."""
    combined = w1_g0_cap(r1_slots, root)
    waits = {name: combined['waits_s'][name] for name in GATED_D_RUN_NAMES}
    timeout = combined['r1_g0_timeout_s']
    maximum = max(waits.values())
    return {'authority': 'LEAD-RULINGS-2 R7-2, R10-4', 'role': 'D', 'r1_g0_timeout_s': timeout,
            'waits_s': waits, 'censored': [n for n in combined['censored'] if n in waits],
            'max_g0_s': maximum, 'value_s': _role_cap(maximum, timeout),
            'rule': 'clamp(ceil(1.25 * max counted gated D G0 wait), 600, R1 g0_timeout_s)'}


CONTRAST_EPISODE_PHASES = ('G1', 'H', 'prefill', 'decode', 'tool')
X_G_EVIDENCE_FIELDS = ('admitted_turns', 'x7', 'phases_s')


def w1_contrast_g0_cap(r1_slots, x_max_turns, root=ROOT):
    """R11/R07: deadman-bounded, non-veto contrast on every W1 path.

    A missing/negative available span gives a zero-cap G0 timeout, never an
    invented episode estimate. This preserves the member/predecessor order,
    but its changed heat history must be disclosed in all downstream D rows.
    """
    timeout = r1_g0_timeout_s(root)
    x_g = r1_slots.get('x_g') if isinstance(r1_slots, dict) else None
    x_g = x_g if isinstance(x_g, dict) else {}
    wait = x_g.get('g0_wait_s')
    measured = (x_g.get('status') == 'measured' and x_g.get('g0_outcome') == 'released'
                and finite(wait) and wait >= 0)
    reasons = []
    if not measured:
        reasons.append('X-G released wait unavailable')
    nominal = _role_cap(float(wait) if measured else timeout, timeout)
    turns, x7, phases = (x_g.get(k) for k in X_G_EVIDENCE_FIELDS)
    if type(x_max_turns) is not int or x_max_turns <= 0 or type(turns) is not int or turns != x_max_turns:
        reasons.append('X-G did not establish the complete WP18 X turn count')
    if x7 is not False:
        reasons.append('X-G completion/no-deadman evidence unavailable')
    episode = None
    if isinstance(phases, dict) and all(finite(phases.get(k)) and phases[k] >= 0 for k in CONTRAST_EPISODE_PHASES):
        episode = math.fsum(phases[k] for k in CONTRAST_EPISODE_PHASES)
    else:
        reasons.append('X-G episode timing unavailable')
    available = None if episode is None else math.floor(CONTRAST_DEADMAN_S - episode - 10)
    value = 0 if available is None else max(0, min(nominal, available))
    if value == 0:
        reasons.append('no qualified positive contrast cap; immediate G0 timeout')
    if measured and value < math.ceil(1.25*wait):
        reasons.append('deadman-fitted cap is below the released-wait allowance')
    if value < nominal:
        reasons.append('reduced contrast cap can change predecessor heat for downstream W1 D')
    # Native X/Y identity is a separate WP19 requirement, never inferred here.
    return {'authority': 'LEAD-RULINGS-2 R11 / RUN_STATE 212', 'role': 'contrast',
            'r1_g0_timeout_s': timeout, 'x_g_wait_s': float(wait) if measured else None,
            'x_g_fallback': not measured, 'value_s': value, 'x_max_turns': x_max_turns,
            'episode_s': episode, 'available_cap_s': available, 'nominal_cap_s': nominal,
            'worst_s': None if episode is None else value+episode, 'deadman_s': CONTRAST_DEADMAN_S,
            'fits': not reasons, 'reasons': reasons,
            'predeclared': 'INCONCLUSIVE: ' + '; '.join(reasons) if reasons else None,
            'history_disclosure': 'A skipped/capped contrast changes predecessor heat for W1 D; W1 is development only.',
            'rule': 'cap_c=max(0,min(nominal,floor(contrast_deadman-X_G_episode-10))); missing timing gives 0; non-veto INCONCLUSIVE'}


# LEAD-RULINGS-2 R10-2 / R10-4: the lead's ruling 1(f) receipt.
RULING_1F_RECEIPT = KIT / 'registration/ruling_1f_receipt.json'
RULING_1F_RECEIPT_SCHEMA = 'joulewise.align_v4.ruling_1f_receipt.v1'
R10_AUTHORITY = 'LEAD-RULINGS-2 R10-2'
R10_BRANCHES = {'a': 'budget-sized D G0 cap (8-bit)', 'b': '4-bit D, after its own R1-4bit gated night',
                'c': 'window council'}
UNSIGNED = 'PENDING_LEAD_SIGNATURE'
PROCEDURE_SCRIPT = Path('scripts/align_w1_budget_procedure.py')
DEVIATION_PREFIX = 'DEVIATION R10-2(a)'


def valid_lead_signature(signature):
    """Cold-review disposition LOW-1: 'lead: <name/session> <ISO date>',
    stripped, with no PENDING_LEAD_SIGNATURE in any case."""
    import datetime
    import re
    if not isinstance(signature, str):
        return False
    text = signature.strip()
    match = re.fullmatch(r'lead: (\S.*\S|\S) (\d{4}-\d{2}-\d{2})', text)
    if text != signature or match is None or UNSIGNED.lower() in text.lower():
        return False
    try:
        datetime.date.fromisoformat(match.group(2))
    except ValueError:
        return False
    return True


def r1_record_identity(r1_slots):
    """The R1 record a receipt names (disposition LOW-2)."""
    slots = r1_slots.get('slots') if isinstance(r1_slots.get('slots'), dict) else {}
    return {'schema': r1_slots.get('schema'), 'source': r1_slots.get('source'), 'I_D': slots.get('I_D'),
            'max_r1_tail_s': r1_slots.get('max_r1_tail_s')}


def r10_2_derivation(r1_slots, t_dead, x_max_turns, root=ROOT):
    """LEAD-RULINGS-2 R10-2(a), mechanical: G0* = T_dead - holds - prefill/tool
    - 10,240/r with r = min(step-d and gated decode rates) and holds projected
    per decoded token to the same 10,240 tokens (R10-4). Branch (a) when
    no gated D G0 is censored (timeout, deadman or unobserved: the lead's
    ruling on R10 builder decision (i), the audit's section 6), ceil(1.25 x
    the longest released gated D G0 wait) <= G0*, and the armed cap
    floor(G0*) is below 600 s
    ('lead' when it is not). It is 'current' whenever the e901 600 s rule
    fits at some B_D (MEDIUM-1) and 'rerun' when no gated D run decoded a
    token (LOW-4); otherwise (b), 4-bit next. Reads only R1 timing and count
    fields."""
    rows, phases, rate, cap = gated_fit_inputs(r1_slots)
    tokens = BUDGET_FLOOR + cap
    d_cap = w1_d_g0_cap(r1_slots, root)
    holds = projected_holds_s(rows, phases, tokens)
    prefill_tool = max(p['prefill'] + p['tool'] for p in phases)
    decode = tokens / rate
    g0_star = t_dead - holds - prefill_tool - decode
    largest_current = max_fitting_b_d(r1_slots, t_dead)
    decoded = any(row['decode_tokens'] > 0 for row in rows)
    released = [d_cap['waits_s'][name] for name in GATED_D_RUN_NAMES if name not in d_cap['censored']]
    w_d = max(released) if released else None
    bound = math.ceil(G0_CAP_FACTOR * w_d) if released else None
    armed = math.floor(g0_star) if g0_star >= 1 else None
    if largest_current is not None:
        # Cold-review disposition MEDIUM-1: the current 600 s rule fits at some
        # B_D (protocol v4; R10-2's order), so no R10-2 deviation applies.
        branch = 'current'
    elif not decoded:
        # Disposition LOW-4: no gated D run decoded a token, so neither the
        # rate nor the holds term has gated evidence: an R1 re-run.
        branch = 'rerun'
    elif armed is not None and bound is not None and bound <= g0_star and not d_cap['censored']:
        # G0* >= 600 s while the e901 rule (X-G included) misses: outside what
        # R10-2(a) was ruled for (a D cap below 600 s); return to the lead.
        branch = 'a' if armed < thermal_gates.G0_CAP_DEFAULT_S else 'lead'
    else:
        branch = 'b'
    gated = {row['run']: {'g0_outcome': row.get('g0_outcome'), 'decode_tokens': row['decode_tokens'],
                          **{f'{k}_s': p[k] for k in ('G0', 'G1', 'H', 'prefill', 'tool', 'decode')}}
             for row, p in zip(rows, phases)}
    return {'branch': branch,
            'inputs': {'T_dead_s': t_dead, 'r1_g0_timeout_s': d_cap['r1_g0_timeout_s'],
                       'budget_floor_tokens': BUDGET_FLOOR, 'turn_cap_tokens': cap,
                       'r_decode_tok_per_s': rate, 'gated_d': gated},
            'derivation': {'tokens': tokens, 'decode_s': decode, 'holds_proj_s': holds,
                           'prefill_tool_s': prefill_tool, 'G0_star_s': g0_star,
                           'W_D_s': w_d, 'censored_D': d_cap['censored'], 'admit_bound_s': bound,
                           'current_rule_largest_fitting_B_D': largest_current, 'gated_decode_evidence': decoded,
                           'd_g0_cap_s': armed if branch == 'a' else None, 'branch': branch},
            'contrast': w1_contrast_g0_cap(r1_slots, x_max_turns, root)}


def receipt_bytes(receipt):
    return raw_json(receipt)


def receipt_sha256(receipt):
    return sha(receipt_bytes(receipt))


def read_ruling_1f_receipt(root=ROOT):
    """The committed lead receipt (a canonical raw_json file), or None."""
    path = Path(root) / RULING_1F_RECEIPT
    if not path.is_file():
        return None
    raw = path.read_bytes()
    receipt = json.loads(raw)
    if not isinstance(receipt, dict) or raw != receipt_bytes(receipt):
        raise ValueError(f'{RULING_1F_RECEIPT} must be a canonical JSON object (indent 2, sorted keys); '
                         'write it with scripts/align_w1_budget_procedure.py sign')
    return receipt


def _mismatches(recorded, derived, path):
    """Paths where a receipt differs from the re-derivation (floats to 1e-9)."""
    if isinstance(derived, dict):
        if not isinstance(recorded, dict) or set(recorded) != set(derived):
            return [path]
        return [m for key in sorted(derived) for m in _mismatches(recorded[key], derived[key], f'{path}.{key}')]
    if isinstance(derived, list):
        if not isinstance(recorded, list) or len(recorded) != len(derived):
            return [path]
        return [m for i, (a, b) in enumerate(zip(recorded, derived)) for m in _mismatches(a, b, f'{path}[{i}]')]
    if type(derived) is float or (type(recorded) is float and type(derived) is int):
        return [] if finite(recorded) and math.isclose(recorded, derived, rel_tol=1e-9, abs_tol=1e-9) else [path]
    return [] if type(recorded) is type(derived) and recorded == derived else [path]


def verify_ruling_1f_receipt(receipt, r1_slots, t_dead, x_max_turns, root=ROOT):
    """LEAD-RULINGS-2 R10-2/R10-4: a signed receipt that takes branch (a) and
    whose inputs and derivation equal the kit's re-derivation from the R1
    record. Branches (b) and (c) never admit 8-bit W1. Returns the derivation."""
    if (not isinstance(receipt, dict) or receipt.get('schema') != RULING_1F_RECEIPT_SCHEMA
            or receipt.get('authority') != R10_AUTHORITY):
        raise ValueError(f'ruling 1(f) receipt must be a {RULING_1F_RECEIPT_SCHEMA} record with authority '
                         f'{R10_AUTHORITY!r}')
    if not valid_lead_signature(receipt.get('lead_signature')):
        raise ValueError('ruling 1(f) receipt is not signed: lead_signature must be the lead\'s signature line '
                         "'lead: <name/session> <ISO date>'")
    branch = receipt.get('branch')
    if branch not in R10_BRANCHES:
        raise ValueError(f'ruling 1(f) receipt branch must be one of {sorted(R10_BRANCHES)}; got {branch!r}')
    if branch != 'a':
        raise ValueError(f'ruling 1(f): the lead\'s receipt takes R10-2 branch ({branch}), '
                         f'{R10_BRANCHES[branch]}; 8-bit W1 does not arm on it')
    derived = r10_2_derivation(r1_slots, t_dead, x_max_turns, root)
    wrong = (_mismatches(receipt.get('inputs'), derived['inputs'], 'inputs')
             + _mismatches(receipt.get('derivation'), derived['derivation'], 'derivation')
             + _mismatches(receipt.get('contrast'), derived['contrast'], 'contrast'))
    if wrong:
        raise ValueError('ruling 1(f) receipt does not match the re-derivation from the R1 record at: '
                         + ', '.join(wrong) + ' (LEAD-RULINGS-2 R10-4)')
    d = derived['derivation']
    if derived['branch'] == 'current':
        raise ValueError('ruling 1(f) receipt (R10-2(a)) refused: the current 600 s rule fits (largest fitting B_D '
                         f'{d["current_rule_largest_fitting_B_D"]}), so no R10-2 deviation applies (R10-2\'s order; '
                         'protocol v4)')
    if derived['branch'] == 'rerun':
        raise ValueError('ruling 1(f) receipt (R10-2(a)) refused: no gated D run decoded a token; the remedy is an '
                         'R1 re-run (cold-review disposition LOW-4)')
    if derived['branch'] == 'lead':
        raise ValueError('ruling 1(f) receipt (R10-2(a)) refused: G0* is at least 600 s while the current rule does '
                         'not fit; return to the lead')
    if derived['branch'] != 'a':
        raise ValueError(f'ruling 1(f) receipt (R10-2(a)) refused: ceil(1.25 x the longest released gated D G0 '
                         f'wait) = {d["admit_bound_s"]} s against G0* = {d["G0_star_s"]:.1f} s, censored gated D G0 '
                         f'{d["censored_D"]} (any one blocks (a)), or G0* is not below '
                         f'{thermal_gates.G0_CAP_DEFAULT_S} s (then the current rule applies and no receipt is '
                         'needed)')
    # Cold-review disposition LOW-2: the receipt's text fields are bound too.
    deviation = receipt.get('deviation_log')
    if not isinstance(deviation, str) or not deviation.startswith(DEVIATION_PREFIX):
        raise ValueError(f'ruling 1(f) receipt deviation_log must be the public deviation entry '
                         f"('{DEVIATION_PREFIX}: ...'; R10-2(a))")
    script = Path(root) / PROCEDURE_SCRIPT
    expected = {'path': PROCEDURE_SCRIPT.as_posix(), 'sha256': sha(script.read_bytes()) if script.is_file() else None}
    if receipt.get('procedure') != expected:
        raise ValueError(f'ruling 1(f) receipt procedure must be {expected} (the committed procedure script)')
    if _mismatches(receipt.get('r1_record'), r1_record_identity(r1_slots), 'r1_record'):
        raise ValueError(f'ruling 1(f) receipt r1_record {receipt.get("r1_record")!r} is not the bound R1 record '
                         f'{r1_record_identity(r1_slots)!r}')
    return derived


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


def check_r1_budget_and_policy(r1_inputs, r1_slots, *, receipt=None, x_max_turns=None):
    """Lead ruling R5-4 (executing review MEDIUM-2, cold pass MEDIUM-2).

    inputs.R1.B_D may only be lowered from R1's step-d budget (A1's fit rule),
    the thermal policy must be the one R1 measured (chunk_tokens = N_chunk,
    delta_slow_c = S6, which is S5 until the lead's FD 2.6 S6 tuning,
    turn_cap_s = S7), and the frozen B_D must satisfy ruling 1(f) against the
    frozen T_dead. When R1 changes the picks, R6-4 binds S6/S7 to
    thermometry.D.s7_for_r1_picks instead; S6 tuning starts from its slow band.
    With no receipt, D retains the e901eb2a4 G0 term/cap (X-G included).
    A verified R10-2(a) receipt binds D's sub-600 s cap and receipt digest.
    R11 supersedes the contrast-only restriction: both paths bind the
    separate deadman-fitted contrast cap and non-veto predeclaration.
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
    derived = w1_g0_cap(r1_slots)
    recorded = r1_slots.get('g0_cap_w1')
    if (not isinstance(recorded, dict) or type(recorded.get('value_s')) is not int
            or type(recorded.get('x_g_fallback')) is not bool
            or not finite(recorded.get('r1_g0_timeout_s'))
            or any(recorded.get(key) != derived[key] for key in ('value_s', 'x_g_fallback', 'r1_g0_timeout_s',
                                                                  'waits_s', 'max_g0_s', 'floor_s', 'factor'))
            or not isinstance(recorded.get('censored'), list)
            or sorted(map(str, recorded['censored'])) != sorted(derived['censored'])):
        raise ValueError('r1_slots.g0_cap_w1 is missing or stale; must match the re-derivation '
                         f'{derived} (LEAD-RULINGS-2 R7-2, R7-12)')
    if receipt is None:
        # Cold-review disposition MEDIUM-2: no receipt is the e901eb2a4 kit.
        if 'g0_cap_receipt' in policy:
            raise ValueError('inputs.R1.thermal_policy.g0_cap_receipt names a ruling 1(f) receipt, but no receipt '
                             f'is committed at {RULING_1F_RECEIPT} (LEAD-RULINGS-2 R10-4)')
        if not finite(policy.get('g0_cap_s')) or policy['g0_cap_s'] != derived['value_s']:
            raise ValueError('inputs.R1.thermal_policy.g0_cap_s must equal r1_slots.g0_cap_w1.value_s '
                             f'{derived["value_s"]} (LEAD-RULINGS-2 R7-2)')
    else:
        verified = verify_ruling_1f_receipt(receipt, r1_slots, r1_inputs['T_dead'], x_max_turns)
        d_cap, source = verified['derivation']['d_g0_cap_s'], 'the R10-2(a) receipt\'s d_g0_cap_s'
        expected = {'authority': thermal_gates.R10_G0_CAP_AUTHORITY, 'receipt_sha256': receipt_sha256(receipt)}
        if policy.get('g0_cap_receipt') != expected:
            raise ValueError(f'inputs.R1.thermal_policy.g0_cap_receipt must be {expected} (the committed '
                             'receipt\'s digest; LEAD-RULINGS-2 R10-4)')
        if not finite(policy.get('g0_cap_s')) or policy['g0_cap_s'] != d_cap:
            raise ValueError(f'inputs.R1.thermal_policy.g0_cap_s must equal {source}, {d_cap}')
    contrast = w1_contrast_g0_cap(r1_slots, x_max_turns)
    if policy.get('contrast_g0_cap_s') != contrast['value_s'] or policy.get('contrast_fit') != contrast:
        raise ValueError('R11 contrast_fit/contrast_g0_cap_s must bind the rederived non-veto contrast on every path')
    classified = (r1_slots.get('thermometry') or {}).get('D') or {}
    changed = classified.get('sensor_pick_changed') is True
    bindings = [('chunk_tokens', slots.get('N_chunk'), 'r1_slots.slots.N_chunk')]
    if changed:
        # R6-4: R0's soak slots describe the old keys. Bind the new keys to
        # the recovery and quiet-window band computed from R1's inventory.
        source = 'r1_slots.thermometry.D.s7_for_r1_picks'
        computed = classified.get('s7_for_r1_picks')
        computed = computed if isinstance(computed, dict) else {}
        band = computed.get('band_c')
        s6 = band.get('s_slow') if isinstance(band, dict) else None
        s7 = computed.get('S7')
        if not finite(s6) or s6 <= 0 or not finite(s7) or s7 <= 0:
            raise ValueError(f'{source}: R1-pick S6/S7 were not computed (finite, positive '
                             'band_c.s_slow and S7 required)')
        rederive_r1_pick_s7(computed, source)
        # The R1-pick S6/S7 describe the keys they were computed for; the
        # policy must gate on exactly those (Sol critique of round 6).
        keys = computed.get('keys') if isinstance(computed.get('keys'), dict) else {}
        sensors = policy.get('sensors') if isinstance(policy.get('sensors'), dict) else {}
        if any(sensors.get(role) != keys.get(role) or keys.get(role) is None for role in ('s_fast', 's_slow')):
            raise ValueError(f'inputs.R1.thermal_policy.sensors {sensors.get("s_fast")!r}/{sensors.get("s_slow")!r} '
                             f'are not the keys {source}.keys {keys.get("s_fast")!r}/{keys.get("s_slow")!r} '
                             'that the R1-pick S6/S7 were computed for')
        bindings.append(('turn_cap_s', s7, source + '.S7'))
        if not _close(policy.get('delta_slow_c'), s6):
            tuning = r1_slots.get('s6_tuning')
            if (not isinstance(tuning, dict) or not isinstance(tuning.get('authority'), str)
                    or not tuning['authority'].strip() or not _close(tuning.get('from_c'), s6)
                    or not _close(tuning.get('to_c'), policy.get('delta_slow_c'))):
                raise ValueError(f'inputs.R1.thermal_policy.delta_slow_c differs from {source}.band_c.s_slow '
                                 'without a recorded lead s6_tuning {authority, from_c = R1-pick S6, '
                                 'to_c = delta_slow_c}')
            if policy['delta_slow_c'] > S6_TUNING_CAP_C + 1e-9:
                raise ValueError(f'{source}: a tuned S6 must stay within the {S6_TUNING_CAP_C} C cap '
                                 '(council ruling 1(e))')
    else:
        bindings.extend((name, slots.get(slot), f'r1_slots.slots.{slot}')
                        for name, slot in (('delta_slow_c', 'S6'), ('turn_cap_s', 'S7')))
    for name, target, source in bindings:
        if not _close(policy.get(name), target):
            raise ValueError(f'inputs.R1.thermal_policy.{name} {policy.get(name)!r} differs from '
                             f'{source} {target!r}')
    if not changed and not _close(slots.get('S6'), slots.get('S5')):
        tuning = r1_slots.get('s6_tuning')
        if (not isinstance(tuning, dict) or not isinstance(tuning.get('authority'), str)
                or not tuning['authority'].strip() or not _close(tuning.get('from_c'), slots.get('S5'))
                or not _close(tuning.get('to_c'), slots.get('S6'))):
            raise ValueError('r1_slots.slots.S6 differs from S5 without a recorded lead S6 tuning '
                             '(s6_tuning {authority, from_c = S5, to_c = S6})')
        if slots['S6'] > S6_TUNING_CAP_C + 1e-9:
            raise ValueError(f'a tuned S6 must stay within the {S6_TUNING_CAP_C} C cap (council ruling 1(e))')
    fit = ruling_1f_fit(r1_slots, r1_inputs['B_D'], r1_inputs['T_dead'], receipt=receipt, x_max_turns=x_max_turns)
    if not fit['fits']:
        raise ValueError(f'ruling 1(f): B_D {fit["B_D"]} does not fit T_dead {fit["T_dead_s"]:.1f} s: worst '
                         f'{fit["worst_s"]:.1f} s = ' + ' + '.join(f'{k} {v:.1f}' for k, v in fit['terms_s'].items())
                         + f' ({fit["rule"]}); the largest fitting B_D is '
                         f'{max_fitting_b_d(r1_slots, r1_inputs["T_dead"])}'
                         + f'; g0_cap_w1 = {fit["g0_cap_w1"]}; d_g0_cap = {fit["d_g0_cap"]}')
    return fit


def require_ready(inputs, r1_slots=None, *, synthetic=False, receipt=None):
    """W1 readiness. ``receipt`` is the lead's ruling 1(f) receipt (LEAD-RULINGS-2
    R10-4); None is the R6-3 rule, which refuses whenever 1(f) does not fit."""
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
    r0_digest = inputs['R0'].get('record_sha256')
    sensor_digest = ((inputs['R1'].get('thermal_policy') or {}).get('sensors') or {}).get('r0_sha256')
    if not valid_digest(r0_digest) or sensor_digest != r0_digest:
        raise ValueError('R0.record_sha256 must bind thermal_policy.sensors.r0_sha256')
    slots = inputs['R1']
    validate_budget(slots['B_D'])
    if not finite(slots['I_D']) or not 0 <= slots['I_D'] < 1750:
        raise ValueError('R1.I_D must be finite and in [0, 1750)')
    tail = r1_slots.get('max_r1_tail_s')
    if not finite(tail) or tail < 0:
        raise ValueError('R1 r1_slots must record a finite, non-negative max_r1_tail_s')
    check_r1_evidence(inputs, r1_slots, synthetic=synthetic, receipt=receipt)
    expected = l1_t_dead(slots['I_D'], tail)
    if not finite(slots['T_dead']) or not math.isclose(slots['T_dead'], expected, rel_tol=1e-9):
        raise ValueError('R1.T_dead must equal min((1750 - I_D) / 1.13544, '
                         '(1800 - I_D - max_r1_tail_s - 10) / 1.13544) (lead ruling L1)')
    check_l1_member_fit(slots['I_D'], slots['T_dead'], tail)
    from joulewise.align.apple.thermal_gates import validate_gate_policy
    policy_input = gate_policy_fields(slots['thermal_policy'])
    # R1 supplies the numeric/sensor template.  Custody roles and the source
    # bundle digest are deterministically installed per member below.
    policy_input['window_reference'] = {'role': 'capture'}
    policy = validate_gate_policy(policy_input)
    if not policy['heavy'] or not policy['per_turn']:
        raise ValueError('D requires heavy/G1/holds')
    # R10-4: the contrast members' policy (their own G0 cap, no receipt) is valid too.
    validate_gate_policy({**gate_policy_fields(slots['thermal_policy'], role='contrast'),
                          'heavy': False, 'per_turn': True, 'window_reference': {'role': 'capture'}})
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


def check_wp18_turn_contents(fixture, label):
    """Validate the turn and source shape written by align_v4_wp18_fixtures."""
    for index, turn in enumerate(fixture['turns']):
        if not isinstance(turn, dict) or type(turn.get('turn')) is not int or turn['turn'] != index:
            raise ValueError(f'{label}: turn must equal its zero-based index {index}')
        for field in ('prompt_token_ids', 'output_token_ids'):
            ids = turn.get(field)
            if not isinstance(ids, list) or not ids or any(type(v) is not int or v < 0 for v in ids):
                raise ValueError(f'{label}: turn {index} {field} must be non-empty non-negative integer token IDs')
    sources = fixture.get('sources')
    if (not isinstance(sources, dict) or set(sources) != {'align_turns_jsonl_sha256', 'p7_pilot_json_sha256'}
            or not all(valid_digest(value) for value in sources.values())):
        raise ValueError(f'{label}: sources must hold exactly the two source sha256 digests')


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
        check_wp18_turn_contents(fixture, relative)


def require_w1_ready(root=ROOT):
    """Everything W1 prepare/arm needs from the kit: inputs, D identity, R1 sizing, WP18 fixtures."""
    try:
        collection_plan = json.loads((Path(root) / KIT / 'collection_plan.json').read_bytes())
    except (OSError, ValueError) as exc:
        raise ValueError('RUN_STATE 210 / squeeze ruling: W1/D requires a readable collection plan '
                         'that enables KM003C capture') from exc
    km003c.require_enabled(collection_plan)
    inputs = read_inputs(root)
    if not any(p.startswith('WP11.') for p in pending_inputs(inputs)):
        pins_raw = (Path(root) / D_PINS).read_bytes()
        validate_d_identity(inputs['WP11'], json.loads(pins_raw), pins_raw=pins_raw)
    require_ready(inputs, read_r1_slots(root), receipt=read_ruling_1f_receipt(root))
    require_sizing(root)
    validate_wp18_fixtures(inputs, root)
    from joulewise.align.apple.v4_registration import require_registration
    require_registration(root)


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


def gate_policy_fields(policy, role='D'):
    """Copy runtime gate controls, excluding the inputs-only R1 digest (R6-5).

    R11: D carries its normal or receipt-bound G0 cap. Contrast carries its
    own deadman-fitted cap and contrast_fit on every path, never D's receipt.
    """
    if role not in ('D', 'contrast'):
        raise ValueError(f'unknown W1 gate-policy role {role!r}')
    fields = {key: deepcopy(value) for key, value in policy.items()
              if key not in ('classification_sha256', 'contrast_g0_cap_s', 'contrast_fit')}
    if role == 'contrast':
        fields.pop('g0_cap_receipt', None)
        if 'contrast_g0_cap_s' in policy:
            fields['g0_cap_s'] = deepcopy(policy['contrast_g0_cap_s'])
            fields['contrast_fit'] = deepcopy(policy.get('contrast_fit'))
    return fields


def thermal_policy(inputs, *, heavy, per_turn, window_reference, role='D'):
    value = inputs['R1']['thermal_policy']
    if value is None:
        value = dict(sensors=None, delta_fast_c=None, delta_slow_c=None,
                     turn_cap_s=None, chunk_tokens=None)
    else:
        value = gate_policy_fields(value, role)
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
                                                   window_reference=reference, role='contrast'))
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
                    km003c=km003c.REQUIREMENT.copy(),
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
        if member.get('role') == 'D' and member['spec'].get('max_turns') != 12:
            raise ValueError('D max_turns must remain frozen at 12')
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
W1's g0_cap_s binds r1_slots.g0_cap_w1.value_s (LEAD-RULINGS-2 R7-2, R7-12):
clamp(ceil(1.25 * max counted gated D and X-G G0 wait), 600 s, R1 g0_timeout_s).
Unreleased G0s count at the full R1 timeout; an inconclusive X-G records
x_g_fallback. Ruling 1(f) uses this cap + max(G1 + H) + max(prefill + tool)
+ (B_D + turn_cap_tokens) / min(step-d and gated decode rates), and refuses
when that misses T_dead. Only a signed lead receipt
(registration/ruling_1f_receipt.json, LEAD-RULINGS-2 R10-2(a), drafted by
scripts/align_w1_budget_procedure.py) changes that, and only when the 600 s
rule fits at no B_D: D then arms G0* = T_dead - holds projected to 10,240
tokens - prefill/tool - 10,240 / r, below 600 s, named in
thermal_policy.g0_cap_receipt; contrast members arm their own
thermal_policy.contrast_g0_cap_s and contrast_fit on EVERY path (R11, RUN_STATE 212).
Failed/incomplete proof predeclares non-veto INCONCLUSIVE. Missing/nonpositive
available cap gives immediate G0 timeout; changed predecessor heat is disclosed.
D sizing/receipt checks remain unchanged. The kit re-derives every number.
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
W1 arm requires --obc-off-attested-by, --battery-log, --next-arm-triage and --w1-disk-config. By-day
scripts/align_v4_offloads.py verifies configured inventories; the disk config
names daytime_offload_receipt and an explicit lead-signed
daytime_offload_freshness policy (max_age_s, lead_signature); no default duration. Arm checks >=80 decimal GB
free without remounting/re-hashing the SSD. Empty offloads require explicit
offloads_owed: none. Battery arm requires fresh AC, >=99%, not charging and
|InstantAmperage| <=200 mA, retaining raw ioreg and pmset evidence (pmset is evidence only).
Top-up evidence is derived from the logged battery record (--battery-log; a completed charge within
30 min or continuous float since), never typed. DC residuals print for benign members only.
R12: a window ends at authenticated terminal completion (the 59,520 s maximum is a
ceiling, not a reservation). W1/D arm also requires --next-arm-triage, the frozen
B2 list (joulewise/align/apple/v4_cadence.NEXT_ARM_TRIAGE), every entry gating.
Calibration is a fixed 8 counted windows (v4_cadence.calibration_stop, RUN_STATE 217): no
early stop, 39 eligible benign per pair after 8, else insufficient_calibration.
require_w1_ready also requires registration_receipt.json, bound to current and
committed protocol/kit/desk/estimand/deviation/U3/WP19 bytes, two admitted gate
reports and the lead signature. The committed pending template never admits.
U3 needs a lead-signed u3_bar.json (session_zero_rms_series_exact_v1, N=16) with an
independent gate; no k or fixed energy bar exists. Historical k=3 receipts cannot admit W1.
Generate wp19_receipt.json from all-turn X/Y rendering plus complete native X-G.
The B window rule needs a lead-signed battery_window_policy.json (zero_B_auto_resume_v1);
the qualified full-span mount audit remains a lead-owned pending gate. R0.record_sha256 must bind sensor provenance.
R16 checks actual per-turn opportunity at the chosen B_D, never a capability guarantee.
The additive align_v4_session.py refuses prepare/install while inputs are pending.
Its desk is the parameterized pilot instrument desk; WP21 owns full U4–U6,
K-session and contrast reporting. This kit grants no arm or hardware approval.

RUN_STATE 210 / squeeze: runtime_requirements.km003c explicitly enables the
Block HAZARD_PACK driver's existing reader and supervision, before the first
idle baseline through the final member, in hazards/meter/ with closing hashes.
require_w1_ready refuses a missing/disabled/changed declaration. The v4 desk
prints per-member DC integrals and a separate five-term DC residual, labelled
SECONDARY / not yet registered. Missing coverage or one dropped counter makes
that member's DC channel missing and never changes powermetrics eligibility.
See docs/align/squeeze/KM003C-ALIGN.md for custody and remaining live gates.

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
