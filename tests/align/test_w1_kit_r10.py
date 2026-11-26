"""LEAD-RULINGS-2 R10-4: the W1 kit lane for ruling R10 (synthetic R1 records only).

The per-role W1 G0 caps, the D cap below 600 s at the gate, the retired
R10-2(a) receipt (RL-148 section 2, RL-156 section 3.1: the kit refuses one),
and the mechanical post-R1 procedure (scripts/align_w1_budget_procedure.py;
since RL-148 section 2 it takes the typical case). Every R1 record here is
synthetic.
"""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
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


def with_role_fields(inputs, slots):
    """X-G's evidence a post-R10 R1 record carries (12 = WP18 X turns)."""
    slots['x_g'].update(admitted_turns=12, x7=False, phases_s=dict(X_G_PHASES))
    return inputs, slots


def no_hold(row, g1_s, **phases):
    """PR #777 row-2 finding 5: a gated D row with no hold seconds (N_chunk 4,096) whose one recorded G1 wait
    is its whole phases_s.G1 (the kit reconciles the two). The fixtures' G1 + H sums are unchanged."""
    row['phases_s'].update(G1=g1_s, H=0.0, **phases)
    row['gate_waits_s'] = {'G1': [g1_s] if g1_s else []}


def eight_bit_case(*, d_wait=120.0):
    """A synthetic 8-bit R1 record where 1(f) fits at no B_D (a print since RL-148 section 2) and the
    typical case fits. I_D 400, tail 20: T_dead = 1,350 / 1.13544 = 1,188.97 s; r = 11.9 tok/s (3,332 tokens
    in 280 s), G1 30 s, prefill + tool 36 s. (Under the retired R10-2(a) this record armed D at 200 s.)
    """
    inputs, slots = ready_inputs(i_d=400.0, tail=20.0)
    with_role_fields(inputs, slots)
    for row in slots['deadman_budget']:
        no_hold(row, 30.0, G0=d_wait, prefill=30.0, tool=6.0)
    set_decode_rate(slots, 11.9)
    slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
    inputs['R1']['B_D'] = slots['slots']['B_D'] = 6144
    fit = kit.w1_contrast_g0_cap(slots, 12)
    inputs['R1']['thermal_policy'].update(contrast_g0_cap_s=fit['value_s'], contrast_fit=fit)
    return inputs, slots


# A g0_cap_receipt as R10-4 had the policy carry it; RL-156 section 3.1: the kit refuses any.
G0_CAP_RECEIPT = {'authority': thermal_gates.R10_G0_CAP_AUTHORITY, 'receipt_sha256': 'e' * 64}


def arm_receipt(inputs):
    """inputs with a branch (a) style receipt armed: D's cap at 200 s below 600 s and the receipt key."""
    inputs['R1']['thermal_policy'].update(g0_cap_s=200, g0_cap_receipt=dict(G0_CAP_RECEIPT))
    return inputs


class RetiredReceiptTests(unittest.TestCase):
    """RL-148 section 2, RL-156 section 3.1: the R10-2(a) receipt path is retired. A committed
    registration/ruling_1f_receipt.json or a thermal_policy.g0_cap_receipt is refused."""

    def test_without_a_receipt_1f_does_not_refuse(self):
        inputs, slots = eight_bit_case()
        # RL-148 section 2, RL-149 section 1.5: ruling 1(f)'s worst case no longer refuses D;
        # require_ready asks that the typical case fits (tests/align/test_rl149_typical_case.py).
        kit.require_ready(inputs, slots)
        self.assertIsNone(kit.max_fitting_b_d(slots, inputs['R1']['T_dead']))
        self.assertEqual(kit.ruling_1f_fit(slots, 6144, inputs['R1']['T_dead'])['rule'], 'R6-3, R7-2 G0_cap_W1')

    def test_a_receipt_armed_in_the_inputs_is_refused(self):
        inputs, slots = eight_bit_case()
        with self.assertRaisesRegex(ValueError, r'g0_cap_receipt names a ruling 1\(f\) receipt.*RL-156 section 3\.1'):
            kit.require_ready(arm_receipt(inputs), slots)
        # The key alone is enough, whatever it names.
        inputs, slots = eight_bit_case()
        inputs['R1']['thermal_policy']['g0_cap_receipt'] = None
        with self.assertRaisesRegex(ValueError, 'g0_cap_receipt'):
            kit.require_ready(inputs, slots)
        inputs, slots = eight_bit_case()
        policy = dict(inputs['R1']['thermal_policy'], g0_cap_receipt=dict(G0_CAP_RECEIPT))
        with self.assertRaisesRegex(ValueError, 'g0_cap_receipt'):
            kit.check_r1_budget_and_policy(dict(inputs['R1'], thermal_policy=policy), slots, x_max_turns=12)

    def test_a_dangling_symlink_at_the_receipt_path_is_refused(self):
        # PR #790 row-2 NIT 5: os.path.lexists, so a link to nothing still counts.
        inputs, _slots = eight_bit_case()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / kit.RULING_1F_RECEIPT
            path.parent.mkdir(parents=True)
            path.symlink_to(Path(tmp) / 'nowhere.json')
            self.assertFalse(path.exists())
            with self.assertRaisesRegex(ValueError, 'exists'):
                kit.refuse_ruling_1f_receipt(inputs, tmp)

    def test_generation_without_check_writes_no_receipt_armed_config(self):
        # PR #790 row-2 LOW 3: build_files refuses the key and the file before it writes a D spec.
        inputs, slots = eight_bit_case()
        with patch.object(kit, 'read_inputs', lambda root=kit.ROOT: arm_receipt(deepcopy(inputs))), \
                patch.object(kit, 'read_r1_slots', lambda root=kit.ROOT: deepcopy(slots)), \
                self.assertRaisesRegex(ValueError, 'g0_cap_receipt'):
            kit.build_files(kit.ROOT)

    def test_a_committed_receipt_file_is_refused_unread(self):
        inputs, slots = eight_bit_case()
        with tempfile.TemporaryDirectory() as tmp:
            kit.refuse_ruling_1f_receipt(inputs, tmp)
            path = Path(tmp) / kit.RULING_1F_RECEIPT
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'schema': 'joulewise.align_v4.ruling_1f_receipt.v1', 'branch': 'a',
                                        'lead_signature': 'lead: Laptop lead 2026-11-07'}))
            for refuse in (lambda: kit.refuse_ruling_1f_receipt(inputs, tmp),
                           lambda: kit.require_ready(inputs, slots, root=tmp)):
                with self.assertRaisesRegex(ValueError, r'ruling_1f_receipt\.json exists.*RL-156 section 3\.1'):
                    refuse()
            path.write_text('not json')                  # refused by existence, never parsed
            with self.assertRaisesRegex(ValueError, 'exists'):
                kit.refuse_ruling_1f_receipt(inputs, tmp)
        # The repository commits no receipt.
        self.assertFalse((ROOT / kit.RULING_1F_RECEIPT).exists())

    def test_the_receipt_path_is_gone(self):
        inputs, slots = eight_bit_case()
        for call in (lambda: kit.require_ready(inputs, slots, receipt={}),
                     lambda: kit.ruling_1f_fit(slots, 6144, inputs['R1']['T_dead'], receipt={}),
                     lambda: kit.check_r1_budget_and_policy(inputs['R1'], slots, receipt={})):
            with self.assertRaises(TypeError):
                call()
        for name in ('read_ruling_1f_receipt', 'verify_ruling_1f_receipt', 'r10_2_derivation', 'receipt_bytes',
                     'receipt_sha256', 'projected_holds_s', 'RULING_1F_RECEIPT_SCHEMA', 'R10_BRANCHES'):
            self.assertFalse(hasattr(kit, name), name)
        for name in ('sign', '_draft'):
            self.assertFalse(hasattr(proc, name), name)

    def test_a_censored_d_g0_sets_the_printed_d_cap_and_a_rerun_segment_reruns(self):
        for outcome in ('timeout', 'deadman', 'unobserved'):
            _inputs, slots = eight_bit_case()
            slots['deadman_budget'][1]['g0_outcome'] = outcome
            slots['deadman_budget'][1]['phases_s']['G0'] = 900.0
            slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
            with self.subTest(outcome=outcome):
                self.assertEqual(kit.w1_d_g0_cap(slots)['value_s'], 1200)   # R7-2's timeout
                rerun = deepcopy(slots)
                rerun['inconclusive_segments'] = {'planning_turn_R_plus_2C': 'G0 did not release, twice'}
                self.assertEqual(proc.decide(rerun, 12)['step'], 'R1-RERUN')

    def test_where_the_600_s_rule_fits_the_procedure_takes_the_typical_case(self):
        # Cold review MEDIUM-1's record (I_D 400 s, 22 tok/s, 2,200 tokens per gated run): the 600 s rule fits
        # at 6,144; the procedure takes the typical case (RL-148 section 2) and the kit admits with no receipt.
        inputs, slots = ready_inputs(i_d=400.0, tail=20.0)
        with_role_fields(inputs, slots)
        for row in slots['deadman_budget']:
            no_hold(row, 30.0, G0=120.0, prefill=30.0, tool=6.0, decode=100.0)
        set_decode_rate(slots, 22.0)
        slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
        inputs['R1']['B_D'] = slots['slots']['B_D'] = 6144
        self.assertGreaterEqual(kit.max_fitting_b_d(slots, inputs['R1']['T_dead']), 6144)
        self.assertEqual(proc.decide(slots, 12)['step'], 'TYPICAL-CASE')
        current_policy = ready_inputs()[0]['R1']['thermal_policy']
        fit_c = kit.w1_contrast_g0_cap(slots, 12)
        current_policy.update(contrast_g0_cap_s=fit_c['value_s'], contrast_fit=fit_c)
        kit.require_ready(dict(inputs, R1=dict(inputs['R1'], thermal_policy=current_policy)), slots)

    def test_without_a_receipt_every_member_arms_r7_2s_one_cap_as_at_e901(self):
        # Cold review MEDIUM-2: no receipt means the e901eb2a4 kit exactly.
        inputs, slots = ready_inputs()
        slots['x_g']['g0_wait_s'] = 500.0
        slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
        inputs['R1']['thermal_policy']['g0_cap_s'] = 625
        with patch.object(kit, 'read_inputs', lambda root=kit.ROOT: deepcopy(inputs)), \
                patch.object(kit, 'read_r1_slots', lambda root=kit.ROOT: deepcopy(slots)):
            files = kit.build_files(kit.ROOT)
        plan = json.loads(files[kit.KIT / 'collection_plan.json'])
        caps = {m['role']: m['spec']['thermal']['g0_cap_s'] for m in plan['members'] if m['role'] != 'anchor'}
        self.assertEqual(caps['D'], 625)
        self.assertEqual(caps['X-G'], 0)  # missing episode timing: explicit non-veto contrast


class RoleCapTests(unittest.TestCase):
    """R10-4 item 2, cold-review disposition MEDIUM-2, R11: D keeps e901eb2a4's rule (R7-2's one G0_cap_W1,
    X-G included; R7-12's INCONCLUSIVE X-G does not refuse on that alone); contrast members arm their own
    deadman-fitted cap. There is no receipt path (RL-148 section 2, RL-156 section 3.1)."""

    def reviewer_case(self):
        inputs, slots = ready_inputs(i_d=400.0, tail=20.0)
        with_role_fields(inputs, slots)
        slots['x_g'].update(g0_wait_s=560.0)
        slots['x_g']['phases_s'].update(G0=560.0, decode=200.0)
        for row in slots['deadman_budget']:
            no_hold(row, 30.0, G0=120.0, prefill=30.0, tool=6.0)
        set_decode_rate(slots, 20.0)
        slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
        inputs['R1']['B_D'] = slots['slots']['B_D'] = 6144
        return inputs, slots

    def test_without_a_receipt_d_term_and_cap_include_x_g_as_at_e901(self):
        # The reviewer's D-waits-120 / X-G-560 case: the e901 rule refuses (G0 term 700).
        inputs, slots = self.reviewer_case()
        self.assertEqual(slots['g0_cap_w1']['value_s'], 700)
        fit = kit.ruling_1f_fit(slots, 6144, inputs['R1']['T_dead'])
        self.assertEqual(fit['terms_s']['G0_s'], 700)
        self.assertFalse(fit['fits'])
        inputs['R1']['thermal_policy']['g0_cap_s'] = 700
        fit_c = kit.w1_contrast_g0_cap(slots, 12)
        inputs['R1']['thermal_policy'].update(contrast_g0_cap_s=fit_c['value_s'], contrast_fit=fit_c)
        # RL-148 section 2, RL-149 section 1.5: ruling 1(f)'s worst case no longer refuses D;
        # require_ready asks that the typical case fits (tests/align/test_rl149_typical_case.py).
        kit.require_ready(inputs, slots)
        inputs['R1']['thermal_policy']['g0_cap_s'] = 600
        with self.assertRaisesRegex(ValueError, r'r1_slots\.g0_cap_w1\.value_s.*LEAD-RULINGS-2 R7-2'):
            kit.require_ready(inputs, slots)
        # R11: contrast cap is legal without a D receipt; D's fit still fails.
        inputs['R1']['thermal_policy'].update(g0_cap_s=700, contrast_g0_cap_s=700)
        # RL-148 section 2, RL-149 section 1.5: ruling 1(f)'s worst case no longer refuses D;
        # require_ready asks that the typical case fits (tests/align/test_rl149_typical_case.py).
        kit.require_ready(inputs, slots)

    def test_contrast_failure_predeclares_inconclusive_and_never_vetoes_d(self):
        changes = [lambda s: s['x_g'].update(g0_wait_s=560.),
                   lambda s: s['x_g'].update(admitted_turns=11),
                   lambda s: s['x_g'].update(x7=True),
                   lambda s: s['x_g'].update(status='inconclusive', g0_outcome='timeout', g0_wait_s=1200.),
                   *[lambda s, f=f: s['x_g'].pop(f) for f in kit.X_G_EVIDENCE_FIELDS],
                   lambda s: s['x_g']['phases_s'].update(decode=-1.)]
        for change in changes:
            inputs, slots = eight_bit_case()
            change(slots)
            slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
            contrast = kit.w1_contrast_g0_cap(slots, 12)
            self.assertFalse(contrast['fits'])
            self.assertTrue(contrast['predeclared'].startswith('INCONCLUSIVE'))
            # RL-156 section 3.1: no receipt path; the contrast failure is non-veto on the one path left.
            inputs['R1']['thermal_policy'].update(g0_cap_s=slots['g0_cap_w1']['value_s'],
                                                  contrast_g0_cap_s=contrast['value_s'], contrast_fit=contrast)
            kit.require_ready(inputs, slots)

    def test_template_has_no_receipt_slot(self):
        # RL-156 section 3.1: the template no longer carries cold review LOW-5's g0_cap_receipt slot.
        from scripts import validate_align_v4_w1_plan as validator
        template = validator.build_template()
        self.assertNotIn('g0_cap_receipt', template['align_v4']['thermal_policy'])
        self.assertEqual(json.loads((ROOT / validator.DEFAULT_PLAN.relative_to(ROOT)).read_text()), template)


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
        for cap in (0, -1, float('nan'), True, 1300):
            # Cold review LOW-5: the message names the receipt range.
            with self.subTest(cap=cap), self.assertRaisesRegex(ValueError, r'g0_cap_s.*\(0, 1200\] with'):
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

    # Cold review LOW-3: bulk reads expose every key, so they are logged too.
    def _bulk(self, kind):
        self._log.update(f'{self._path}.{k}<{kind}>' for k in dict.keys(self))

    def __iter__(self):
        self._bulk('iter')
        return super().__iter__()

    def items(self):
        self._bulk('items')
        return super().items()

    def keys(self):
        self._bulk('keys')
        return super().keys()

    def values(self):
        self._bulk('values')
        return super().values()

    def __deepcopy__(self, memo):
        self._bulk('deepcopy')
        return {k: deepcopy(dict.__getitem__(self, k), memo) for k in dict.keys(self)}


def _track(value, log, path):
    if isinstance(value, dict):
        return TrackingDict(value, log, path)
    if isinstance(value, list):
        return [_track(v, log, f'{path}[]') for v in value]
    return value


class ProcedureTests(unittest.TestCase):
    """R10-4 item 5: the pre-declared, mechanical post-R1 procedure."""

    def test_steps(self):
        # RL-148 section 2, RL-149 section 1.5, RL-152 section 1.2 (PR #777 row-2 finding 9): TYPICAL-CASE,
        # RESEARCH-LEAD or R1-RERUN; never an R10-2 receipt or a 4-bit route.
        inputs, slots = eight_bit_case()
        self.assertIsNone(kit.max_fitting_b_d(slots, inputs['R1']['T_dead']))     # 1(f) fits at no B_D
        decision = proc.decide(slots, 12)
        self.assertEqual(decision['step'], 'TYPICAL-CASE')
        self.assertFalse({'branch', 'receipt_draft'} & set(decision))
        self.assertTrue(decision['typical_case']['fits'])
        self.assertEqual(decision['turn_opportunity']['status'], 'pass')
        self.assertFalse(decision['worst_case_print_only']['fits'])
        self.assertEqual(decision['set_inputs']['R1.B_D'], slots['slots']['B_D'])
        self.assertEqual(decision['set_inputs']['R1.thermal_policy.g0_cap_s'], kit.w1_g0_cap(slots)['value_s'])
        self.assertEqual(decision['set_inputs']['R1.thermal_policy.contrast_g0_cap_s'], 600)
        self.assertEqual(decision['notes'], [])
        rerun = deepcopy(slots)
        rerun['inconclusive_segments'] = {'planning_turn_R_plus_2C': 'G0 did not release, twice'}
        self.assertEqual(proc.decide(rerun, 12)['step'], 'R1-RERUN')
        # A typical case that does not fit goes to the research lead (900 + 30 + 36 + 280 s > T_dead 1,189 s).
        _, slow = eight_bit_case(d_wait=900.0)
        decision = proc.decide(slow, 12)
        self.assertEqual(decision['step'], 'RESEARCH-LEAD')
        self.assertFalse(decision['typical_case']['fits'])
        self.assertIn('typical case does not fit', decision['reason'])
        self.assertNotIn('set_inputs', decision)
        # A failed duty bar or a contrast that cannot fit is named, not hidden.
        failing = deepcopy(slots)
        failing['duty_bar'].update(verdict='fail', **{'pass': False})
        failing['x_g']['x7'] = True
        notes = ' '.join(proc.decide(failing, 12)['notes'])
        self.assertIn('DUTY BAR', notes)
        self.assertIn('CONTRAST', notes)

    def test_reads_only_timing_and_count_fields(self):
        # Cold review LOW-3: poison every level, nested phases_s included, and
        # log bulk reads (iteration, items, keys, values, deepcopy).
        _, slots = eight_bit_case()
        poison = {'energy_j': 1.0, 'u5_value': 2.0, 'beta_T': 3.0, 'mde_tokens': 4.0, 'temperature_c': 5.0}
        slots.update(poison, u5={'verdict': 'pass', 'c': 1.0, 'beta_T_j_per_c': 99.0},
                     projected_mde={'tokens': 1.0}, planning_temperature={'beta': 1.0})
        for row in slots['deadman_budget']:
            row.update(poison, gross_episode_j=40000.0)
            row['phases_s'].update(poison)
        for block in ('x_g', 'budget_fit_inputs', 'duty_bar', 'slots'):
            slots[block].update(poison)
        slots['x_g']['phases_s'].update(poison)
        log = set()
        decision = proc.decide(TrackingDict(slots, log), 12)
        self.assertEqual(decision['step'], 'TYPICAL-CASE')
        forbidden = ('energy', 'u5', 'mde', 'beta', 'temperature', 'planning_temperature', 'thermometry',
                     'high_power')
        self.assertFalse([p for p in log if any(f in p for f in forbidden)], sorted(log))
        top = {p.split('.')[1].split('[')[0].split('<')[0] for p in log}
        self.assertLessEqual(top, {'schema', 'source', 'slots', 'max_r1_tail_s', 'inconclusive_segments',
                                   'budget_fit_inputs', 'duty_bar', 'deadman_budget', 'x_g'})

    def test_no_gated_decode_evidence_is_an_r1_rerun(self):
        # Cold review LOW-4: no gated D run decoded a token: an R1 re-run.
        _, slots = eight_bit_case()
        for row in slots['deadman_budget']:
            no_hold(row, 0.0, decode=0.0)
            row['decode_tokens'] = 0
        slots['budget_fit_inputs']['r_decode_tok_per_s'] = 11.9
        slots['g0_cap_w1'] = kit.w1_g0_cap(slots)
        self.assertEqual(proc.decide(slots, 12)['step'], 'R1-RERUN')

    def test_never_recommends_a_b_d_below_the_floor(self):
        # Cold review LOW-5, under RL-148 section 2: B_D is the step-d budget, and below the kit's 6,144 floor
        # the procedure recommends nothing.
        _, slots = eight_bit_case()
        for bad in (5120, 6144.0, None):
            slots['slots']['B_D'] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, r'slots\.B_D must be .* at least 6144'):
                proc.decide(slots, 12)

    def test_cli_decides_and_has_no_sign_command(self):
        # RL-148 section 2, RL-156 section 3.1: decide prints the step; there is no receipt to draft or sign.
        inputs, slots = eight_bit_case()
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as printed, \
                redirect_stderr(io.StringIO()) as errors:
            tmp = Path(tmp)
            (tmp / 'r1_slots.json').write_text(json.dumps(slots))
            (tmp / 'inputs.json').write_text(json.dumps(inputs))
            self.assertEqual(proc.main(['decide', '--r1-slots', str(tmp / 'r1_slots.json'),
                                        '--inputs', str(tmp / 'inputs.json')]), 0)
            self.assertEqual(proc.main(['decide', '--r1-slots', '/nonexistent/r1_slots.json']), 1)
            for argv in (['sign', 'draft.json', '--signature', 'lead: Laptop lead 2026-11-07'],
                         ['decide', '--draft-out', str(tmp / 'draft.json')]):
                with self.subTest(argv=argv[0]), self.assertRaises(SystemExit):
                    proc.main(argv)
            self.assertEqual(sorted(p.name for p in tmp.iterdir()), ['inputs.json', 'r1_slots.json'])
        self.assertIn('"step": "TYPICAL-CASE"', printed.getvalue())
        self.assertIn('No such file', errors.getvalue())

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
        # Lead ruling (b): a recorded lead step that must record its source sha.
        result['phases'][1]['result']['g0_wait_s'] = 120.0
        for bad in (None, '', 'a' * 63, 'A' * 64):
            with self.subTest(sha=bad), self.assertRaisesRegex(ValueError, 'r1_result.json sha256'):
                proc.backfill_x_g(old, result, bad)


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


class W1D2ReportTests(unittest.TestCase):
    """Lead ruling on R10 open point (c): the W1 desk reports the D members' X2 count and rate (print-only)."""

    def test_desk_reports_d_member_x2_count_and_rate_print_only(self):
        from scripts import align_v4_session as session

        def episode(g0_outcome, flags=()):
            intervals = [] if g0_outcome is None else [{'kind': 'G0', 'outcome': g0_outcome, 'duration_s': 200.0}]
            return {'hardware': {'ac_powermode': {'value': 0}, 'thermal': {'intervals': intervals}},
                    'flags': list(flags)}

        members = [('d5', 'D', episode('released')), ('d8', 'D', episode('timeout', ['episode.g0_unreleased:0'])),
                   ('d11', 'D', episode('released', ['thermal.gate_timeout:3'])),
                   ('d14', 'D', episode('released')), ('x6', 'X-G', episode('timeout')),
                   ('d17', 'D', None)]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registration = root / 'kit/registration'
            registration.mkdir(parents=True)
            rows = [{'run_id': run, 'role': role, 'ordinal': i + 5, 'ac_powermode': 0}
                    for i, (run, role, _) in enumerate(members)]
            (registration.parent / 'collection_plan.json').write_text(json.dumps({'members': rows}))
            for run, _, record in members:
                if record is not None:
                    outputs = root / 'runs' / run / 'outputs'
                    outputs.mkdir(parents=True)
                    (outputs / 'align_episode.json').write_text(json.dumps(record))
            state = {'registration_dir': str(registration), 'measurement_root': str(root)}
            added, report = session.powermode_desk_check(state=state, members=[], runs_root=root / 'runs',
                                                         kit_path=kit.KIT)
        self.assertEqual(set(added), {'ac_powermode_members', 'v4_registration_evidence'})
        self.assertFalse(added['v4_registration_evidence'])  # no signed/native registration in this fixture
        # X2 remains print-only; the independent missing-registration gate is new.
        x2 = report['d_member_x2']
        self.assertIs(x2['print_only'], True)
        self.assertEqual((x2['d_members'], x2['read'], x2['x2_count'], x2['g0_timeout_x2_count']), (5, 4, 2, 1))
        self.assertAlmostEqual(x2['x2_rate'], 2 / 4)
        self.assertEqual(x2['unread'], ['d17'])
        self.assertEqual([m['run_id'] for m in x2['members'] if m['x2']], ['d8', 'd11'])
