"""D-188 SHIP-FIX: regressions for the three CONFIRMED Sol hunter findings on de0cf3209.

Synthetic only (the committed S10 ALPHA member, temporary trees, stub programs).
Each class is one hunter reproducer turned into a test; each fails on de0cf3209.

* A (P2, /private/tmp/jwsol-ha probe_l5.py): the L5 thermal memo keyed a float
  clock stamp and the mapping {"float": its hex} identically, so a warm memo (and
  a VDL fill/hit on top of it, in on and in shadow mode) returned () where the
  serial evaluation returns environment_admission_missing.
* B (P1, /private/tmp/jwsol-hc repro_prefix.py): the whole-window member pool
  merged every worker's store entries (and poison) before the caller consumed
  its first member, so members after a first authentication refusal reached the
  run's store. Deadline firings stay counted eagerly: tag b5/analysis-r1's
  member_map does exactly that (analysis_member_pool.py:149-156 at the tag), and
  result equivalence with r1 is the gate.
* C (P1, /private/tmp/jwsol-hc repro_step_position.py): step-codes rows carried
  only the StepRecord ordinal, so a refusal at step 5's first program and one at
  its second (or at another bundle of one pack) were the same decision.
"""
from __future__ import annotations

import contextlib
import copy
import dataclasses
import io
import json
import os
from pathlib import Path
import re
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import analysis_member_pool as pool, analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import environment_admission as ea
from joulewise.authentication_io import (
    V2AuthenticationInputError, V2AuthenticationReadSession, read_authentication_input,
)
from joulewise.b5_analysis import dry_run as d
from tests.b5_analysis import test_vdl_shipping as fx
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER

MISSING = ('environment_admission_missing',)
FILES = ('metadata.json', 'events.jsonl', 'rich_telemetry_idle.jsonl', 'raw/powermetrics.plist',
         'raw/powermetrics_idle.plist')


class InjectiveMemoKeyTests(unittest.TestCase):
    """Finding A: the shared canonical_key is injective and type-tagged."""

    def test_a_float_never_shares_a_key_with_its_tagged_mapping(self):
        key = arc.canonical_key
        for value in (0.1, -0.0, 1e300, float('inf')):
            with self.subTest(value=value):
                self.assertNotEqual(key([value]), key([{'float': value.hex()}]))
                self.assertNotEqual(key({'epoch_s': value}), key({'epoch_s': {'float': value.hex()}}))
        self.assertNotEqual(key([0.0]), key([-0.0]))
        self.assertNotEqual(key([1]), key([True]))
        self.assertNotEqual(key([[1, 2]]), key([(1, 2)]))
        self.assertNotEqual(key(['ab', 'c']), key(['a', 'bc']))
        self.assertNotEqual(key({'a': 'b'}), key([['a', 'b']]))
        self.assertEqual(key({'b': 1.5, 'a': [None]}), key({'a': [None], 'b': 1.5}))


class L5ThermalMemoTests(unittest.TestCase):
    """Finding A: cold, warm, VDL on and VDL shadow agree on the float-to-mapping substitution."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='sol-hunt-l5-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name) / 'member'
        with tarfile.open(ARCHIVE) as archive:
            for name in FILES:
                target = cls.root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(MEMBER + name).read())
        cls.good = json.loads((cls.root / 'metadata.json').read_bytes())
        from joulewise.bundle_read import BundleReader
        cls.window = BundleReader(cls.root).measured_window()
        cls.bad = copy.deepcopy(cls.good)
        stamps = cls.bad['uncertainty_evidence']['clock_anchor']['clock_stamps']
        name = next(iter(stamps))
        value = stamps[name]['epoch_s']
        assert isinstance(value, float)
        stamps[name]['epoch_s'] = {'float': value.hex()}

    def setUp(self):
        (self.root / 'metadata.json').write_text(json.dumps(self.good))

    def scan(self, metadata):
        return ea.current_environment_refusals(
            metadata, bundle_path=self.root,
            measured_window_start_s=self.window.start_s, measured_window_end_s=self.window.end_s)

    def test_cold_serial_reference(self):
        self.assertEqual(self.scan(self.good), ())
        self.assertEqual(self.scan(self.bad), MISSING)

    def test_warm_memo_returns_the_serial_result(self):
        with arc.analysis_run_caches({}):
            self.assertEqual(self.scan(self.good), ())
            self.assertEqual(self.scan(self.bad), MISSING, 'a warm memo must not serve the float key')
            self.assertEqual(self.scan(self.bad), MISSING)
            self.assertEqual(self.scan(self.good), ())

    def test_store_on_and_shadow_fill_and_hit_the_serial_result(self):
        for mode in (vdl.ON, vdl.Mode('shadow', 1000)):
            with self.subTest(mode=mode.name):
                (self.root / 'metadata.json').write_text(json.dumps(self.good))
                with arc.analysis_run_caches({}, vdl_mode=mode) as caches:
                    caches.deadline = SimpleNamespace(firings=0)

                    def leaf(metadata):
                        return caches.vdl.call(
                            'L5_environment_refusals', ea.current_environment_refusals, metadata,
                            bundle_path=self.root, measured_window_start_s=self.window.start_s,
                            measured_window_end_s=self.window.end_s)
                    self.assertEqual(leaf(self.good), ())
                    (self.root / 'metadata.json').write_text(json.dumps(self.bad))
                    self.assertEqual(leaf(self.bad), MISSING, 'fill')
                    self.assertEqual(leaf(self.bad), MISSING, 'hit')
                    self.assertFalse(caches.vdl.defect_pending())


class _Done:
    def __init__(self, value):
        self.value = value

    def result(self):
        return self.value


class _PreparedPool:
    def __init__(self, values):
        self.values = iter(values)

    def submit(self, worker, task):
        return _Done(next(self.values))


class ConsumedOnlyMergeTests(unittest.TestCase):
    """Finding B: entries, memos and poison merge only from consumed outcomes."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='sol-hunt-prefix-')
        self.addCleanup(tmp.cleanup)
        registration = vdl._registered(fx.SPEC)
        registration.__enter__()
        self.addCleanup(registration.__exit__, None, None, None)
        self.roots = []
        for i in range(3):
            root = Path(tmp.name) / f'm{i}'
            root.mkdir()
            (root / 'meta.json').write_text('{}')
            (root / 'data.bin').write_bytes(b'data')
            self.roots.append(root)
        self.calls = [((str(root), 3), {}) for root in self.roots]

    def outcomes(self):
        outcomes = []
        for args, kwargs in self.calls:
            task = pool.MemberTask(f'{fx.MODULE}:ship_leaf', args, kwargs, True, {},
                                   {'mode': vdl.BLIND_ON, 'commit': 'test', 'entries': None, 'memos': {}})
            outcomes.append(pool.run_member(task))
        return outcomes

    def retained(self, caches, root):
        return any(str(root) in identity for entry in caches.vdl._entries.values() for identity, _ in entry.trees)

    def test_members_after_the_first_refusal_reach_nothing_but_r1_accounting(self):
        session = V2AuthenticationReadSession()
        with session:
            read_authentication_input(self.roots[0] / 'data.bin', grammar='raw', label='earlier first digest')
        (self.roots[0] / 'data.bin').write_bytes(b'changed')
        outcomes = self.outcomes()
        memo_name = pool.SHIPPED_MEMOS[0]
        outcomes[1] = dataclasses.replace(outcomes[1], vdl_new={
            **outcomes[1].vdl_new, 'memos': {memo_name: {'later-member-key': ()}}})
        outcomes[2] = dataclasses.replace(outcomes[2], firings=1, vdl_new={
            **outcomes[2].vdl_new, 'poisoned': ['later-member-poison']})
        with arc.analysis_run_caches({}, workers=2, vdl_mode=vdl.BLIND_ON, vdl_commit='test') as caches, session:
            caches.deadline = SimpleNamespace(firings=0)
            with mock.patch.object(pool, '_pool', return_value=_PreparedPool(outcomes)):
                # The whole-window call site's default (account=True), unchanged.
                ready = pool.member_map(fx.ship_leaf, self.calls)
            self.assertEqual(len(caches.vdl._entries), 0, 'nothing merges before the first consumption')
            with self.assertRaises(V2AuthenticationInputError) as raised:
                pool.consume(ready[0], lambda: fx.ship_leaf(*self.calls[0][0]))
            self.assertEqual(raised.exception.reason, 'v2_authentication_input_changed')
            self.assertEqual(len(caches.vdl._entries), 0, 'the refused member stores nothing either')
            self.assertFalse(any(self.retained(caches, root) for root in self.roots))
            self.assertNotIn('later-member-key', caches.memos.get(memo_name, {}))
            self.assertNotIn('later-member-poison', caches.vdl._poisoned)
            # Tag b5/analysis-r1 counts every outcome's firing when the batch returns
            # (analysis_member_pool.py:149-156 at the tag); equivalence keeps that.
            self.assertEqual(caches.deadline.firings, 1)

    def test_a_consumed_member_merges_its_own_entry_only(self):
        outcomes = self.outcomes()
        with arc.analysis_run_caches({}, workers=2, vdl_mode=vdl.BLIND_ON, vdl_commit='test') as caches, \
                V2AuthenticationReadSession():
            caches.deadline = SimpleNamespace(firings=0)
            with mock.patch.object(pool, '_pool', return_value=_PreparedPool(outcomes)):
                ready = pool.member_map(fx.ship_leaf, self.calls)
            value = pool.consume(ready[0], lambda: fx.ship_leaf(*self.calls[0][0]))
            self.assertEqual(value, fx.ship_leaf(*self.calls[0][0]))
            self.assertEqual([self.retained(caches, root) for root in self.roots], [True, False, False])
            pool.consume(ready[1], lambda: fx.ship_leaf(*self.calls[1][0]))
            self.assertEqual([self.retained(caches, root) for root in self.roots], [True, True, False])


class SideChannelMergeTests(unittest.TestCase):
    """Finding B (review of #640): the any-outcome side channel carries defects
    and counters only; poison, entries and memos never come from it (the
    contract parallel.py's module docstring states)."""

    def test_side_channel_merges_defects_and_counters_only(self):
        payload = {'schema': vdl.SCHEMA, 'entries': {'unconsumed-entry': object()},
                   'poisoned': ['unconsumed-poison'], 'defects': ['side-defect'],
                   'memos': {pool.SHIPPED_MEMOS[0]: {'unconsumed-memo': ()}},
                   'counters': {'side-counter': 2}}
        with vdl._registered(fx.SPEC), \
                arc.analysis_run_caches({}, workers=2, vdl_mode=vdl.ON, vdl_commit='test') as caches:
            pool.merge_side_channel(caches, payload)
            self.assertEqual(caches.vdl._defects, ['side-defect'])
            self.assertEqual(caches.vdl.restricted_counters().get('side-counter'), 2)
            self.assertNotIn('unconsumed-poison', caches.vdl._poisoned)
            self.assertNotIn('unconsumed-entry', caches.vdl._entries)
            self.assertNotIn('unconsumed-memo', caches.memos.get(pool.SHIPPED_MEMOS[0], {}))
            # The consumed path is where poison does merge.
            pool.merge_consumed_poison(caches, payload)
            self.assertIn('unconsumed-poison', caches.vdl._poisoned)
            self.assertNotIn('unconsumed-entry', caches.vdl._entries)


class StepCodePositionTests(unittest.TestCase):
    """Finding C: the refusing invocation and bundle are decision fields of the step codes."""

    @classmethod
    def setUpClass(cls):
        cls.cmp = fx._load_comparator()
        cls.cfg = cls.cmp.load_config()

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='sol-hunt-position-')
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def side(self, label, steps):
        """One stub run: ``steps`` is [(step, window, member or None, exit status)] runner invocations."""
        root = self.tmp / label
        s = d.RunState('blind-dry-run', root / 'index.json', root / 'restricted', 'a' * 40)
        s.index = SimpleNamespace(sha256='c' * 64)
        runner = d.StepRunner(s.restricted)
        s._runner = runner

        def program(status):
            def main(argv):
                if status:
                    print('error: example_refusal')
                return status
            return main
        last = None
        for step, window, member, status in steps:
            result = runner.run(program(status), [], step=step, window=window)
            if member is not None:
                s.note_member(result, member)
            last = (step, window)
        record = {'steps': [s.record(last[0], window=last[1], exit_status=2, code='example_refusal').as_dict()]}
        with contextlib.redirect_stdout(io.StringIO()):
            d._commit_sidecars(s, record, 'off', salted=False)
        raw = (s.restricted / d.STEP_CODES_NAME).read_bytes()
        artifact = SimpleNamespace(name=d.STEP_CODES_NAME, raw=raw, role='decisions-audit/step-codes')
        return raw, SimpleNamespace(record=record, artifacts={'codes': artifact}, step_keys=[['codes']], label=label)

    def compare(self, ref_steps, cand_steps):
        (raw_ref, ref), (raw_cand, cand) = self.side('ref', ref_steps), self.side('cand', cand_steps)
        structures, source = self.cmp.decision_structure(ref, cand, self.cfg, None)
        self.assertEqual(source, 'step-codes')
        return raw_ref, raw_cand, structures['ref'][0], structures['cand'][0]

    def test_step5_first_and_second_program_refusals_differ(self):
        raw_ref, raw_cand, ref, cand = self.compare([('5', None, None, 2)], [('5', None, None, 0), ('5', None, None, 2)])
        self.assertNotEqual(raw_ref, raw_cand)
        self.assertNotEqual(ref, cand)
        rows = [json.loads(raw_ref), json.loads(raw_cand)]
        self.assertEqual([row['invocation'] for row in rows], [1, 2])

    def test_same_ordinal_other_bundle_differs_and_names_no_id(self):
        raw_ref, raw_cand, ref, cand = self.compare([('1', 'alpha', 'run-ident-a', 2)],
                                                    [('1', 'alpha', 'run-ident-b', 2)])
        self.assertNotEqual(ref, cand)
        for raw in (raw_ref, raw_cand):
            row = json.loads(raw)
            self.assertEqual(row['invocation'], 1)
            self.assertRegex(row['member'], '^[0-9a-f]{64}$')
            self.assertNotIn(b'run-ident', raw, 'a keyed digest, never the raw bundle id')

    def test_identical_positions_are_equal(self):
        steps = [('1', 'alpha', 'run-ident-a', 0), ('1', 'alpha', 'run-ident-b', 2)]
        raw_ref, raw_cand, ref, cand = self.compare(steps, steps)
        self.assertEqual((raw_ref, ref), (raw_cand, cand))
        self.assertEqual(json.loads(raw_ref)['invocation'], 2)

    def test_the_comparator_refuses_a_malformed_position(self):
        _, side = self.side('ref', [('5', None, None, 2)])
        for field, value in (('invocation', 0), ('invocation', '1'), ('member', 'run-ident-a'),
                             ('member', 'A' * 64)):
            with self.subTest(field=field, value=value):
                row = json.loads(side.artifacts['codes'].raw)
                row[field] = value
                side.artifacts['codes'].raw = (json.dumps(row) + '\n').encode()
                with self.assertRaises(self.cmp.ComparatorError):
                    self.cmp.read_step_codes(side)

    def test_blinded_vocabulary_is_unchanged_and_digit_free(self):
        self.assertIn('decisions:step_codes', self.cfg.vocabulary)
        self.assertFalse(any(re.search(r'[0-9]', name) for name in self.cfg.vocabulary))


if __name__ == '__main__':
    unittest.main()
