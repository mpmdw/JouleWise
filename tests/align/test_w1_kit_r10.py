"""LEAD-RULINGS-2 R10-4: the W1 kit lane for ruling R10 (synthetic R1 records only).

R10-2(a)'s receipt, the per-role W1 G0 caps, the D cap below 600 s, the
holds projected per decoded token, and the mechanical post-R1 procedure
(scripts/align_w1_budget_procedure.py). Every R1 record here is synthetic.
"""
from copy import deepcopy
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import thermal_gates
from scripts import align_v4_kit as kit
from scripts import align_w1_budget_procedure as proc
from tests.align.test_v4_kit import ready_inputs, set_decode_rate

ROOT = Path(__file__).resolve().parents[2]
X_G_PHASES = {'G0': 120.0, 'G1': 60.0, 'H': 0.0, 'decode': 300.0, 'prefill': 60.0, 'tool': 6.0, 'tail': 0.0}
SIGNATURE = 'Laptop lead (synthetic test signature), 2026-11-07'


def with_role_fields(inputs, slots, *, contrast_cap=600):
    """The R10-4 fields a post-R10 record and inputs carry (12 = WP18 X turns)."""
    inputs['R1']['thermal_policy']['contrast_g0_cap_s'] = contrast_cap
    slots['x_g'].update(admitted_turns=12, x7=False, phases_s=dict(X_G_PHASES))
    return inputs, slots


def eight_bit_case(*, d_wait=120.0):
    """A synthetic 8-bit R1 record where 1(f) refuses and R10-2(a) fits.

    I_D 400, tail 20: T_dead = 1,350 / 1.13544 = 1,188.97 s. r = 11.9 tok/s
    (3,332 tokens in 280 s), G1 + H = 30 s projected to 10,240 tokens =
    92.20 s, prefill + tool = 36 s, decode 10,240 / 11.9 = 860.50 s, so
    G0* = 200.27 s; D waits of 120 s give ceil(150) <= G0*: D arms 200 s.
    """
    inputs, slots = ready_inputs(i_d=400.0, tail=20.0)
    with_role_fields(inputs, slots)
    for row in slots['deadman_budget']:
        row['phases_s'].update(G0=d_wait, G1=20.0, H=10.0, prefill=30.0, tool=6.0)
    set_decode_rate(slots, 11.9)
    slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
    inputs['R1']['B_D'] = 6144
    return inputs, slots


def signed_receipt(slots):
    decision = proc.decide(slots, 12)
    return proc.sign(decision['receipt_draft'], SIGNATURE)


def arm_receipt(inputs, receipt):
    policy = inputs['R1']['thermal_policy']
    policy['g0_cap_s'] = receipt['derivation']['d_g0_cap_s']
    policy['g0_cap_receipt'] = {'authority': thermal_gates.R10_G0_CAP_AUTHORITY,
                                'receipt_sha256': kit.receipt_sha256(receipt)}
    return inputs


class ReceiptTests(unittest.TestCase):
    """R10-4 items 1 and 3: the lead receipt honoured by ruling_1f_fit."""

    def test_without_a_receipt_1f_still_refuses_unconditionally(self):
        inputs, slots = eight_bit_case()
        with self.assertRaisesRegex(ValueError, r'ruling 1\(f\): B_D 6144 does not fit.*largest fitting B_D is None'):
            kit.require_ready(inputs, slots)
        self.assertIsNone(kit.max_fitting_b_d(slots, inputs['R1']['T_dead']))

    def test_signed_branch_a_receipt_arms_d_at_g0_star_and_admits(self):
        inputs, slots = eight_bit_case()
        receipt = signed_receipt(slots)
        self.assertEqual(receipt['branch'], 'a')
        d = receipt['derivation']
        t_dead = (1750 - 400.0) / 1.13544
        holds = 30.0 / 3332 * 10240
        g0_star = t_dead - holds - 36.0 - 10240 / 11.9
        self.assertAlmostEqual(d['G0_star_s'], g0_star)
        self.assertAlmostEqual(d['holds_proj_s'], holds)
        self.assertEqual(d['admit_bound_s'], 150)
        self.assertEqual(d['d_g0_cap_s'], math.floor(g0_star))
        self.assertEqual(d['d_g0_cap_s'], 200)
        arm_receipt(inputs, receipt)
        kit.require_ready(inputs, slots, receipt=receipt)
        fit = kit.ruling_1f_fit(slots, 6144, inputs['R1']['T_dead'], receipt=receipt, x_max_turns=12)
        self.assertEqual(fit['terms_s']['G0_s'], 200)
        self.assertAlmostEqual(fit['terms_s']['holds_s'], holds)
        self.assertTrue(fit['fits'])
        # B_D above the floor does not fit the budget-sized cap.
        inputs['R1']['B_D'] = 7168
        with self.assertRaisesRegex(ValueError, r'ruling 1\(f\): B_D 7168 does not fit'):
            kit.require_ready(inputs, slots, receipt=receipt)

    def test_kit_rederives_the_receipt_and_refuses_any_mismatch(self):
        inputs, slots = eight_bit_case()
        good = signed_receipt(slots)
        for path, value in ((('derivation', 'G0_star_s'), 300.0), (('derivation', 'd_g0_cap_s'), 199),
                            (('derivation', 'holds_proj_s'), 30.0), (('derivation', 'W_D_s'), 100.0),
                            (('inputs', 'r_decode_tok_per_s'), 20.0), (('inputs', 'T_dead_s'), 1200.0),
                            (('inputs', 'gated_d', kit.GATED_D_RUN_NAMES[0], 'G0_s'), 10.0),
                            (('contrast', 'value_s'), 700)):
            receipt = deepcopy(good)
            target = receipt
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            case_inputs = arm_receipt(deepcopy(inputs), receipt)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'does not match the re-derivation'):
                kit.require_ready(case_inputs, slots, receipt=receipt)
        # The same receipt against a changed R1 record: a D wait the receipt did not see.
        changed = deepcopy(slots)
        changed['deadman_budget'][0]['phases_s']['G0'] = 130.0
        changed['g0_cap_w1'] = kit.w1_g0_cap(changed)
        with self.assertRaisesRegex(ValueError, 'does not match the re-derivation'):
            kit.require_ready(arm_receipt(deepcopy(inputs), good), changed, receipt=good)

    def test_long_d_wait_refuses_even_a_self_consistent_branch_a_receipt(self):
        # 1.25 x 170 = 212.5 > G0* = 200.27: R10-2(a) does not fit.
        inputs, slots = eight_bit_case(d_wait=170.0)
        decision = proc.decide(slots, 12)
        self.assertEqual(decision['step'], 'R10-2(b)')
        forged = proc.sign(dict(decision['receipt_draft'], branch='a'), SIGNATURE)
        inputs['R1']['thermal_policy']['g0_cap_receipt'] = {
            'authority': thermal_gates.R10_G0_CAP_AUTHORITY, 'receipt_sha256': kit.receipt_sha256(forged)}
        with self.assertRaisesRegex(ValueError, r'receipt \(R10-2\(a\)\) refused: ceil\(1.25'):
            kit.require_ready(inputs, slots, receipt=forged)

    def test_a_censored_d_g0_never_takes_branch_a(self):
        inputs, slots = eight_bit_case()
        slots['deadman_budget'][1]['g0_outcome'] = 'deadman'
        slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
        decision = proc.decide(slots, 12)
        self.assertEqual(decision['branch'], 'b')
        self.assertEqual(decision['derived']['derivation']['W_D_s'], 1200.0)

    def test_receipt_is_refused_where_the_current_rule_already_fits(self):
        inputs, slots = ready_inputs()        # 50 tok/s: the 600 s rule fits
        with_role_fields(inputs, slots)
        derived = kit.r10_2_derivation(slots, inputs['R1']['T_dead'], 12)
        self.assertEqual(derived['branch'], 'current')
        forged = proc.sign(proc._draft('a', derived, proc.timing_view(slots)), SIGNATURE)
        with self.assertRaisesRegex(ValueError, r'not below 600 s'):
            kit.require_ready(inputs, slots, receipt=forged)

    def test_unsigned_and_non_a_receipts_refuse(self):
        inputs, slots = eight_bit_case()
        draft = proc.decide(slots, 12)['receipt_draft']
        self.assertTrue(draft['lead_signature'].startswith(kit.UNSIGNED))
        for bad in (draft, dict(draft, lead_signature=' '), dict(draft, lead_signature=None)):
            with self.subTest(signature=bad['lead_signature']), self.assertRaisesRegex(ValueError, 'not signed'):
                kit.require_ready(arm_receipt(deepcopy(inputs), bad), slots, receipt=bad)
        for branch, text in (('b', '4-bit'), ('c', 'window council')):
            receipt = proc.sign(dict(draft, branch=branch), SIGNATURE)
            with self.subTest(branch=branch), self.assertRaisesRegex(ValueError, f'branch \\({branch}\\).*{text}'):
                kit.require_ready(inputs, slots, receipt=receipt)
        for bad in (dict(draft, schema='x'), dict(draft, authority='LEAD-RULINGS-2 R7-2'),
                    proc.sign(dict(draft, branch='d'), SIGNATURE)):
            with self.subTest(bad=bad.get('schema'), branch=bad['branch']), self.assertRaises(ValueError):
                kit.require_ready(inputs, slots, receipt=bad)

    def test_policy_binds_the_receipt_cap_and_digest(self):
        inputs, slots = eight_bit_case()
        receipt = signed_receipt(slots)
        # A g0_cap_receipt without a committed receipt.
        armed = arm_receipt(deepcopy(inputs), receipt)
        with self.assertRaisesRegex(ValueError, 'no receipt is committed'):
            kit.require_ready(armed, slots)
        # The receipt, but D still at 600 s, or another cap, or another digest.
        for change in ({'g0_cap_s': 600}, {'g0_cap_s': 199}):
            case = arm_receipt(deepcopy(inputs), receipt)
            case['R1']['thermal_policy'].update(change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "receipt's d_g0_cap_s"):
                kit.require_ready(case, slots, receipt=receipt)
        case = arm_receipt(deepcopy(inputs), receipt)
        case['R1']['thermal_policy']['g0_cap_receipt']['receipt_sha256'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'g0_cap_receipt must be'):
            kit.require_ready(case, slots, receipt=receipt)
        case = arm_receipt(deepcopy(inputs), receipt)
        del case['R1']['thermal_policy']['g0_cap_receipt']
        with self.assertRaisesRegex(ValueError, 'g0_cap_receipt must be'):
            kit.require_ready(case, slots, receipt=receipt)

    def test_committed_receipt_file_is_read_and_must_be_canonical(self):
        inputs, slots = eight_bit_case()
        receipt = signed_receipt(slots)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(kit.read_ruling_1f_receipt(tmp))
            path = Path(tmp) / kit.RULING_1F_RECEIPT
            path.parent.mkdir(parents=True)
            path.write_bytes(kit.receipt_bytes(receipt))
            self.assertEqual(kit.read_ruling_1f_receipt(tmp), receipt)
            path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'canonical'):
                kit.read_ruling_1f_receipt(tmp)
        # The repository commits no receipt: W1 readiness reads None (R6-3 rule).
        self.assertFalse((ROOT / kit.RULING_1F_RECEIPT).exists())

    def test_d_members_arm_the_receipt_cap_and_contrast_members_their_own(self):
        inputs, slots = eight_bit_case()
        receipt = signed_receipt(slots)
        arm_receipt(inputs, receipt)
        with patch.object(kit, 'read_inputs', lambda root=kit.ROOT: deepcopy(inputs)), \
                patch.object(kit, 'read_r1_slots', lambda root=kit.ROOT: deepcopy(slots)):
            files = kit.build_files(kit.ROOT)
        plan = json.loads(files[kit.KIT / 'collection_plan.json'])
        for member in plan['members']:
            thermal = member['spec'].get('thermal')
            if member['role'] == 'D':
                self.assertEqual(thermal['g0_cap_s'], 200)
                self.assertEqual(thermal['g0_cap_receipt'], inputs['R1']['thermal_policy']['g0_cap_receipt'])
                thermal_gates.validate_gate_policy(thermal)
            elif member['role'] != 'anchor':
                self.assertEqual(thermal['g0_cap_s'], 600, member['ordinal'])
                self.assertNotIn('g0_cap_receipt', thermal)
                self.assertNotIn('contrast_g0_cap_s', thermal)
                thermal_gates.validate_gate_policy(thermal)


class RoleCapTests(unittest.TestCase):
    """R10-4 item 2: separate W1 G0 caps for D and contrast members."""

    def test_d_cap_comes_from_the_gated_d_waits_only(self):
        inputs, slots = ready_inputs()
        with_role_fields(inputs, slots, contrast_cap=625)
        slots['x_g']['g0_wait_s'] = 500.0      # X-G (D-to-X) 500 s; D waits 120 s
        slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
        self.assertEqual(slots['g0_cap_w1']['value_s'], 625)     # R7-2's combined record, still bound
        self.assertEqual(kit.w1_d_g0_cap(slots)['value_s'], 600)
        fit = kit.ruling_1f_fit(slots, 8192, inputs['R1']['T_dead'])
        self.assertEqual(fit['terms_s']['G0_s'], 600)
        contrast = kit.w1_contrast_g0_cap(slots, 12)
        self.assertEqual(contrast['value_s'], 625)
        self.assertTrue(contrast['fits'])
        self.assertAlmostEqual(contrast['worst_s'], 625 + 426.0)
        kit.require_ready(inputs, slots)
        inputs['R1']['thermal_policy']['g0_cap_s'] = 625      # the old single cap on D
        with self.assertRaisesRegex(ValueError, 'D-role G0 cap'):
            kit.require_ready(inputs, slots)
        inputs['R1']['thermal_policy'].update(g0_cap_s=600, contrast_g0_cap_s=600)
        with self.assertRaisesRegex(ValueError, 'contrast_g0_cap_s must equal the W1 contrast-role G0 cap 625'):
            kit.require_ready(inputs, slots)

    def test_contrast_cap_must_fit_the_contrast_deadman_on_x_g_s_record(self):
        def refused(change, pattern):
            inputs, slots = ready_inputs()
            with_role_fields(inputs, slots)
            change(slots)
            slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
            inputs['R1']['thermal_policy']['contrast_g0_cap_s'] = kit.w1_contrast_g0_cap(slots, 12)['value_s']
            self.assertFalse(kit.w1_contrast_g0_cap(slots, 12)['fits'])
            with self.assertRaisesRegex(ValueError, r'R10-2\(a\): the contrast members.*' + pattern):
                kit.require_ready(inputs, slots)
        self.assertAlmostEqual(kit.CONTRAST_DEADMAN_S, 1086.3, places=1)
        # 1.25 x 560 = 700; 700 + 426 = 1,126 > 1,086.3.
        refused(lambda s: s['x_g'].update(g0_wait_s=560.0), 'exceeds the contrast deadman')
        refused(lambda s: s['x_g'].update(admitted_turns=11), 'not the complete WP18 X count 12')
        refused(lambda s: s['x_g'].update(x7=True), 'no deadman')
        refused(lambda s: s['x_g'].update(status='inconclusive', g0_outcome='timeout', g0_wait_s=1200.0), 'R7-12')
        for field in kit.X_G_EVIDENCE_FIELDS:
            refused(lambda s, f=field: s['x_g'].pop(f), {'admitted_turns': 'admitted None turns',
                                                          'x7': 'x7 false', 'phases_s': 'phases_s'}[field])
        refused(lambda s: s['x_g']['phases_s'].update(decode=-1.0), 'phases_s')

    def test_contrast_validator_and_template_carry_their_own_cap(self):
        from scripts import validate_align_v4_w1_plan as validator
        template = validator.build_template()
        self.assertEqual(template['align_v4']['thermal_policy']['contrast_g0_cap_s'], validator.PLACEHOLDER)
        self.assertEqual(json.loads((ROOT / validator.DEFAULT_PLAN.relative_to(ROOT)).read_text()), template)


class HoldsProjectionTests(unittest.TestCase):
    """R10-4 item 4: holds projected per decoded token (the audit's corrected D-f)."""

    def test_projection_is_symmetric_with_the_decode_term_and_never_below_the_record(self):
        inputs, slots = eight_bit_case()
        rows, phases, rate, cap = kit.gated_fit_inputs(slots)
        self.assertAlmostEqual(kit.projected_holds_s(rows, phases, 10240), 30.0 / 3332 * 10240)
        self.assertEqual(kit.projected_holds_s(rows, phases, 100), 30.0)   # never below the recorded G1 + H
        rows[0]['decode_tokens'] = 0
        phases[0]['G1'] = phases[0]['H'] = 0.0
        self.assertAlmostEqual(kit.projected_holds_s(rows, phases, 10240), 30.0 / 3332 * 10240)
        phases[0]['G1'] = 5.0
        with self.assertRaisesRegex(ValueError, 'no decoded token'):
            kit.projected_holds_s(rows, phases, 10240)

    def test_receipt_branch_uses_the_projected_holds_term(self):
        inputs, slots = eight_bit_case()
        receipt = signed_receipt(slots)
        fit = kit.ruling_1f_fit(slots, 6144, inputs['R1']['T_dead'], receipt=receipt, x_max_turns=12)
        self.assertGreater(fit['terms_s']['holds_s'], 30.0)
        self.assertAlmostEqual(fit['worst_s'], 200 + 30.0 / 3332 * 10240 + 36.0 + 10240 / 11.9)


class GatePolicyTests(unittest.TestCase):
    """R10-4 item 3: validate_gate_policy accepts a D cap below 600 s only with the receipt."""

    def policy(self, **updates):
        return {'sensors': {'s_fast': 'Tfak', 's_slow': 'Tslw', 'fan_keys': [], 'r0_sha256': 'a' * 64},
                'delta_fast_c': 1., 'delta_slow_c': 1., 'turn_cap_s': 30., 'per_turn': True, 'heavy': True,
                'chunk_tokens': 256, 'window_reference': {'role': 'capture'}, **updates}

    RECEIPT = {'authority': 'LEAD-RULINGS-2 R10-2(a)', 'receipt_sha256': 'e' * 64}

    def test_sub_600_cap_needs_the_receipt(self):
        validate = thermal_gates.validate_gate_policy
        for cap in (200, 599, 0.5):
            with self.subTest(cap=cap), self.assertRaisesRegex(ValueError, "ruling 1\\(f\\) receipt"):
                validate(self.policy(g0_cap_s=cap))
            self.assertEqual(validate(self.policy(g0_cap_s=cap, g0_cap_receipt=dict(self.RECEIPT)))['g0_cap_s'], cap)
        for cap in (0, -1, float('nan'), True):
            with self.subTest(cap=cap), self.assertRaisesRegex(ValueError, 'g0_cap_s'):
                validate(self.policy(g0_cap_s=cap, g0_cap_receipt=dict(self.RECEIPT)))
        for cap in (600, 1200, None):
            updates = {'g0_cap_receipt': dict(self.RECEIPT)}
            if cap is not None:
                updates['g0_cap_s'] = cap
            with self.subTest(cap=cap), self.assertRaisesRegex(ValueError, 'only accompanies'):
                validate(self.policy(**updates))
        for bad in ({}, {'authority': 'LEAD-RULINGS-2 R7-2', 'receipt_sha256': 'e' * 64},
                    {'authority': 'LEAD-RULINGS-2 R10-2(a)', 'receipt_sha256': 'E' * 64},
                    {**self.RECEIPT, 'extra': 1}, 'e' * 64):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'g0_cap_receipt must be'):
                validate(self.policy(g0_cap_s=200, g0_cap_receipt=bad))

    def test_an_unobserved_g0_never_outlasts_a_sub_300_armed_cap(self):
        from tests.align import test_thermal_gate as gates
        obj, _ = gates.session(config=gates.policy(g0_cap_s=200, g0_cap_receipt=dict(self.RECEIPT)))
        self.addCleanup(obj.close)
        obj.reader._transport.values = lambda t: (None, None)
        gate = obj.wait('G0')
        self.assertEqual(gate['duration_s'], 200)
        self.assertEqual(gate['outcome'], 'unobserved')


class TrackingDict(dict):
    """Logs every key read (blinding: the procedure reads timing/count fields only)."""

    def __init__(self, data, log, path=''):
        super().__init__({k: _track(v, log, f'{path}.{k}') for k, v in data.items()})
        self._log, self._path = log, path

    def __getitem__(self, key):
        self._log.add(f'{self._path}.{key}')
        return super().__getitem__(key)

    def get(self, key, default=None):
        self._log.add(f'{self._path}.{key}')
        return super().get(key, default)

    def __contains__(self, key):
        self._log.add(f'{self._path}.{key}')
        return super().__contains__(key)


def _track(value, log, path):
    if isinstance(value, dict):
        return TrackingDict(value, log, path)
    if isinstance(value, list):
        return [_track(v, log, f'{path}[]') for v in value]
    return value


class ProcedureTests(unittest.TestCase):
    """R10-4 item 5: the pre-declared, mechanical post-R1 procedure."""

    def test_steps(self):
        inputs, slots = eight_bit_case()
        decision = proc.decide(slots, 12)
        self.assertEqual((decision['step'], decision['branch']), ('R10-2(a)', 'a'))
        self.assertEqual(decision['set_inputs']['R1.B_D'], 6144)
        self.assertEqual(decision['set_inputs']['R1.thermal_policy.g0_cap_s'], 200)
        self.assertEqual(decision['set_inputs']['R1.thermal_policy.contrast_g0_cap_s'], 600)
        self.assertEqual(decision['notes'], [])
        self.assertIn('ends X2 before turn 1', decision['receipt_draft']['x2_exposure'])
        fast_inputs, fast = ready_inputs()
        with_role_fields(fast_inputs, fast)
        decision = proc.decide(fast, 12)
        self.assertEqual(decision['step'], 'CURRENT-RULE')
        self.assertIsNone(decision['receipt_draft'])
        self.assertEqual(decision['set_inputs']['R1.B_D'], 8192)
        rerun = deepcopy(slots)
        rerun['inconclusive_segments'] = {'planning_turn_R_plus_2C': 'G0 did not release, twice'}
        self.assertEqual(proc.decide(rerun, 12)['step'], 'R1-RERUN')
        _, slow = eight_bit_case(d_wait=400.0)
        decision = proc.decide(slow, 12)
        self.assertEqual((decision['step'], decision['receipt_draft']['branch']), ('R10-2(b)', 'b'))
        self.assertIsNone(decision['receipt_draft']['x2_exposure'])
        # A failed duty bar or a contrast that cannot fit is named, not hidden.
        failing = deepcopy(slots)
        failing['duty_bar'].update(verdict='fail', **{'pass': False})
        failing['x_g']['x7'] = True
        notes = ' '.join(proc.decide(failing, 12)['notes'])
        self.assertIn('DUTY BAR', notes)
        self.assertIn('CONTRAST', notes)

    def test_reads_only_timing_and_count_fields(self):
        _, slots = eight_bit_case()
        slots.update(u5={'verdict': 'pass', 'c': 1.0, 'beta_T_j_per_c': 99.0},
                     projected_mde={'tokens': 1.0}, planning_temperature={'beta': 1.0})
        for row in slots['deadman_budget']:
            row.update(energy_j=31000.0, gross_episode_j=40000.0)
        slots['x_g']['energy_j'] = 9000.0
        log = set()
        decision = proc.decide(TrackingDict(slots, log), 12)
        self.assertEqual(decision['branch'], 'a')
        forbidden = ('energy', 'u5', 'mde', 'beta', 'planning_temperature', 'thermometry', 'high_power')
        self.assertFalse([p for p in log if any(f in p for f in forbidden)], sorted(log))
        top = {p.split('.')[1].split('[')[0] for p in log}
        self.assertLessEqual(top, {'schema', 'source', 'slots', 'max_r1_tail_s', 'inconclusive_segments',
                                   'budget_fit_inputs', 'duty_bar', 'deadman_budget', 'x_g'})

    def test_cli_drafts_signs_and_the_kit_reads_the_receipt(self):
        inputs, slots = eight_bit_case()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / 'r1_slots.json').write_text(json.dumps(slots))
            (tmp / 'inputs.json').write_text(json.dumps(inputs))
            draft = tmp / 'draft.json'
            self.assertEqual(proc.main(['decide', '--r1-slots', str(tmp / 'r1_slots.json'),
                                        '--inputs', str(tmp / 'inputs.json'), '--draft-out', str(draft)]), 0)
            out = tmp / kit.RULING_1F_RECEIPT
            out.parent.mkdir(parents=True)
            self.assertEqual(proc.main(['sign', str(draft), '--signature', SIGNATURE, '--out', str(out)]), 0)
            receipt = kit.read_ruling_1f_receipt(tmp)
        self.assertEqual(receipt['lead_signature'], SIGNATURE)
        kit.require_ready(arm_receipt(inputs, receipt), slots, receipt=receipt)
        self.assertEqual(proc.main(['decide', '--r1-slots', '/nonexistent/r1_slots.json']), 1)

    def test_backfill_copies_x_g_timing_from_r1_result(self):
        inputs, slots = eight_bit_case()
        old = deepcopy(slots)
        for field in kit.X_G_EVIDENCE_FIELDS:
            old['x_g'].pop(field)
        result = {'phases': [{'name': 'D_spam_benign_s1_gated_held_b', 'result': {}},
                             {'name': 'X_G_contrast', 'result': {
                                 'g0_outcome': 'released', 'g0_wait_s': 120.0, 'admitted_turns': 12,
                                 'phases_s': dict(X_G_PHASES), 'energy_j': 9000.0,
                                 'episode_flags': ['tool_call.malformed:3']}}]}
        filled = proc.backfill_x_g(old, result, 'a' * 64)
        self.assertEqual({k: filled['x_g'][k] for k in kit.X_G_EVIDENCE_FIELDS},
                         {'admitted_turns': 12, 'x7': False, 'phases_s': X_G_PHASES})
        self.assertEqual(filled['x_g']['backfill']['r1_result_sha256'], 'a' * 64)
        self.assertNotIn('energy_j', filled['x_g'])
        self.assertTrue(kit.w1_contrast_g0_cap(filled, 12)['fits'])
        result['phases'][1]['result']['episode_flags'] = ['episode.deadman:7']
        self.assertIs(proc.backfill_x_g(old, result, 'a' * 64)['x_g']['x7'], True)
        with self.assertRaisesRegex(ValueError, 'nothing is overwritten'):
            proc.backfill_x_g(slots, result, 'a' * 64)
        result['phases'][1]['result']['g0_wait_s'] = 121.0
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            proc.backfill_x_g(old, result, 'a' * 64)


class DriverXGEvidenceTests(unittest.TestCase):
    """R10-4: the R1 driver records X-G's turns, deadman flag and phases in r1_slots.x_g."""

    def test_x_g_evidence_fields(self):
        from scripts import align_r1_rehearsal as r1
        self.assertEqual(r1.x_g_evidence({'admitted_turns': 12, 'episode_flags': [], 'phases_s': X_G_PHASES}),
                         {'admitted_turns': 12, 'x7': False, 'phases_s': X_G_PHASES})
        self.assertIs(r1.x_g_evidence({'episode_flags': ['episode.deadman:4']})['x7'], True)
        self.assertEqual(r1.x_g_evidence({}), {'admitted_turns': None, 'x7': None, 'phases_s': None})

    def test_synthetic_night_registers_the_x_g_evidence(self):
        from scripts import align_r1_rehearsal as r1
        from tests.align import test_r1_rehearsal as base

        class World(base.FakeWorld):
            def __call__(self, argv):
                result = super().__call__(argv)
                argv = tuple(str(v) for v in argv)
                if '--r1-kind' in argv and argv[argv.index('--r1-kind') + 1] == 'x-g' and result.stdout:
                    payload = json.loads(result.stdout)
                    payload.update(admitted_turns=12, episode_flags=[], phases_s=dict(X_G_PHASES))
                    return base.completed(argv, out=json.dumps(payload))
                return result

        clock = patch.object(r1, '_now_local', lambda: base.NOON_SAFE)
        clock.start()
        self.addCleanup(clock.stop)
        with tempfile.TemporaryDirectory() as td:
            args = base.R1Tests.args(self, td)
            with patch.object(r1, '_run', World()):
                self.assertEqual(r1.run(args), 0)
            registration = json.loads((Path(td) / 'registration/r1_slots.json').read_text())
        self.assertEqual({k: registration['x_g'][k] for k in kit.X_G_EVIDENCE_FIELDS},
                         {'admitted_turns': 12, 'x7': False, 'phases_s': X_G_PHASES})


if __name__ == '__main__':
    unittest.main()
