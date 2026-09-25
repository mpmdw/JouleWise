"""Registration domain and frozen canonical identity witnesses."""
import copy
import hashlib
import json
import unittest

from joulewise.scored_registration import Registration, RegistrationRefusal, REGISTRATION_SCHEMA
from tests.scored_roster_checker import check_registration


def canon_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def fixture(n=6, block_size=1, mode='registered', pred=0.6, worst=1.0, cap=6.0):
    ids = {str(level): [f'L{level}I{i}' for i in range(n)] for level in range(1, 6)}
    models = ('large', 'small')
    predictions = {model: {item: pred for items in ids.values() for item in items} for model in models}
    g = dict(schema=REGISTRATION_SCHEMA, mode=mode, registration_id='reg', plan_id='plan', scorer_id='scorer', arm='decode', arm_to_family={'decode': 'family'}, role_to_model_id={'8B': models[0], '1.7B': models[1]}, sizing_receipt_sha256='a'*64 if mode == 'registered' else None, predictions_sha256=canon_sha(predictions) if mode == 'registered' else None, alpha=0.05, n_boot=10, seed=7, floor_j=0.0, anchor_j=0.0, cap_tokens={'decode': 1}, block_size={'decode': block_size}, item_ids_by_level=ids, envelope_s=cap+1, interior_s=cap, pitch_s=cap+1, offset_s=0, guard_s=0, s_per_token_upper={m: {'decode': worst} for m in models}, prefill_s={m: {'decode': 0.0} for m in models}, ceiling_s={m: {'decode': worst} for m in models}, delta_upper_j_per_block_slot=1.0 if mode == 'registered' else None, budget_j=10000.0 if mode == 'registered' else None, declared_sensitivities=['primary'])
    return g, predictions


class RegistrationTests(unittest.TestCase):
    def test_valid_frozen_and_derived(self):
        g, _ = fixture(n=11, block_size=2)
        r = Registration.from_mapping(g)
        self.assertEqual(r.digest, canon_sha(g))
        self.assertEqual(r.n_per_level, 11)
        self.assertEqual(r.blocks_per_cell, 6)
        self.assertEqual(r.worst('large'), 1.0)
        self.assertEqual(check_registration(r.to_mapping()), [])
        g['plan_id'] = 'changed'
        self.assertEqual(r.plan_id, 'plan')
        copy_ = r.item_ids_by_level
        copy_['1'].clear()
        self.assertEqual(r.n_per_level, 11)

    def test_typed_refusals(self):
        g, _ = fixture()
        cases = [
            (lambda x: x.pop('plan_id'), 'inv_51'),
            (lambda x: x['item_ids_by_level'].update({'6': []}), 'item_ids_by_level_keys'),
            (lambda x: x['item_ids_by_level']['1'].append('extra'), 'unequal_level_sizes'),
            (lambda x: x['cap_tokens'].update({'other': 1}), 'unselected_arm_entry'),
            (lambda x: x['s_per_token_upper']['large'].update({'other': 1}), 'unselected_arm_entry'),
            (lambda x: x.update(alpha=True), 'inv_51'),
            (lambda x: x.update(interior_s=0), 'inv_51'),
            (lambda x: x['ceiling_s']['large'].update(decode=0.5), 'inv_06'),
            (lambda x: x['item_ids_by_level']['1'].__setitem__(0, 'L2I0'), 'inv_09'),
        ]
        for mutate, code in cases:
            with self.subTest(code=code, mutate=mutate):
                bad = copy.deepcopy(g)
                mutate(bad)
                with self.assertRaises(RegistrationRefusal) as caught:
                    Registration.from_mapping(bad)
                self.assertEqual(caught.exception.code, code)

    def test_pilot_nulls(self):
        g, _ = fixture(mode='pilot')
        self.assertIsNone(Registration.from_mapping(g).max_gap)
