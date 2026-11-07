"""b5 under-90: the reserved-key walk returns what the located walk returned (synthetic only)."""
from __future__ import annotations

from collections import OrderedDict
import json
import random
import sys
import time
import unittest
from types import MappingProxyType
from typing import Mapping

from joulewise import authentication_io as aio


def located(value, where):
    """The r2 walk, verbatim (authentication_io._reserved_vocabulary_path at 929fc65c9)."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{where}.{key}"
            if key == "estimator_registration":
                return child_path
            nested = located(child, child_path)
            if nested is not None:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nested = located(child, f"{where}[{index}]")
            if nested is not None:
                return nested
    return None


def tree(rng, depth, plant):
    roll = rng.random()
    if depth <= 0 or roll < 0.3:
        return rng.choice(['x', 1, 2.5, True, None, 'estimator_registration', -7, ''])
    if roll < 0.65:
        keys = rng.sample(['a', 'b', 'c', 'd', 'estimator', 'registration', 'e'], rng.randint(0, 5))
        if plant and rng.random() < 0.08:
            keys.insert(rng.randint(0, len(keys)), 'estimator_registration')
        return {key: tree(rng, depth - 1, plant) for key in keys}
    return [tree(rng, depth - 1, plant) for _ in range(rng.randint(0, 5))]


class ReservedVocabularyTests(unittest.TestCase):
    def test_random_documents_match_the_located_walk(self):
        rng = random.Random(20261106)
        found = 0
        for case in range(4000):
            value = tree(rng, rng.randint(0, 7), plant=case % 2 == 0)
            expected = located(value, 'label')
            found += expected is not None
            self.assertEqual(aio._reserved_vocabulary_path(value, 'label'), expected)
            # Through the real parser and its hooks, as _strict_json sees it.
            parsed = json.loads(json.dumps(value), object_pairs_hook=aio._duplicate_key)
            self.assertEqual(aio._reserved_vocabulary_path(parsed, 'label'), located(parsed, 'label'))
        self.assertGreater(found, 200)

    def test_other_mapping_and_sequence_types_follow_the_original_rules(self):
        cases = [
            OrderedDict([('a', 1), ('estimator_registration', 2)]),
            MappingProxyType({'z': [{'estimator_registration': 0}]}),
            {'a': ({'estimator_registration': 1},)},          # tuples are not walked
            {'a': [[], [{'b': {'estimator_registration': None}}]]},
            [{'estimator_registration': 1}, {'estimator_registration': 2}],
            {'estimator_registration': {'estimator_registration': 1}},
            {1: 'x', 'estimator_registration': 1},
            'estimator_registration', 3, None, [], {},
        ]
        for value in cases:
            self.assertEqual(aio._reserved_vocabulary_path(value, 'L'), located(value, 'L'), value)

    def test_strict_json_verdicts_and_messages_are_unchanged(self):
        documents = [b'{"a": {"estimator_registration": {}}}', b'{"a": [1, {"b": 2}]}',
                     b'[{"x": [{"estimator_registration": 1}]}]', b'{"a": 1, "a": 2}']
        for raw in documents:
            for allow in (False, True):
                try:
                    aio._strict_json(raw, 'doc', allow_governed_spec_vocabulary=allow)
                    outcome = None
                except aio.V2AuthenticationInputError as exc:
                    outcome = (exc.reason, exc.detail)
                value = None
                try:
                    value = json.loads(raw, object_pairs_hook=aio._duplicate_key)
                except aio.V2AuthenticationInputError as exc:
                    expected = (exc.reason, 'doc: ' + exc.detail)
                else:
                    path = located(value, 'doc')
                    expected = (None if path is None or allow else
                                ('v2_authentication_forbidden_json_key',
                                 "forbidden key 'estimator_registration' at " + path))
                self.assertEqual(outcome, expected, (raw, allow))

    def test_recursion_limit_is_reached_at_the_same_nesting(self):
        def nested(depth, leaf):
            value = leaf
            for _ in range(depth):
                value = {'k': value}
            return value

        def outcome(walk, value):
            try:
                return ('ok', walk(value, 'L'))
            except RecursionError:
                return ('recursion', None)

        limit = sys.getrecursionlimit()
        sys.setrecursionlimit(400)
        try:
            for depth in range(300, 420):
                for leaf in (1, {'estimator_registration': 1}):
                    value = nested(depth, leaf)
                    self.assertEqual(outcome(aio._reserved_vocabulary_path, value), outcome(located, value),
                                     (depth, leaf))
        finally:
            sys.setrecursionlimit(limit)

    def test_timing_ledger(self):
        rng = random.Random(7)
        rows = [{'run_id': f'r{i:04d}', 'cells': [{'cell_id': f'c{j}', 'values': [rng.random() for _ in range(20)],
                 'meta': {'k': i, 'ok': True, 'names': ['a', 'b', 'c']}} for j in range(12)]} for i in range(400)]
        value = {'schema_version': 'x', 'rows': rows}
        started = time.perf_counter()
        expected = located(value, 'doc')
        before = time.perf_counter() - started
        started = time.perf_counter()
        actual = aio._reserved_vocabulary_path(value, 'doc')
        after = time.perf_counter() - started
        self.assertEqual(actual, expected)
        print(f'\nreserved-key walk on a {len(json.dumps(value)) / 1e6:.1f} MB document: '
              f'located {before:.3f} s, pre-checked {after:.3f} s')


if __name__ == '__main__':
    unittest.main()
