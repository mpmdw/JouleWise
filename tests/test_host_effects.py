"""Synthetic-only host-effect classification and fixed-allowlist reader tests."""
from __future__ import annotations

import builtins
import contextlib
from dataclasses import FrozenInstanceError, replace
import io
import json
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise import host_effects as h


def clean(**changes):
    facts = h.HostFacts(network_time_on=True, ac_powermode=0, markers=(),
                        night_lock_held=False, active_plan_spans=(), now=100,
                        labels=tuple(h.LabelFact(label, False, False) for label in h.NIGHT_LABELS),
                        desk_fence_observed=True, spotlight_stopped=False, keep_awake_agent=False)
    return replace(facts, **changes)


def effect_rows(facts, effect, outcome=None):
    return [r for r in h.owed_effects(facts, outcome) if r.effect is effect]


class ClassifierTests(unittest.TestCase):
    def test_exact_effect_table(self):
        self.assertEqual([e.name for e in h.Effect], [
            'NETWORK_TIME_OFF', 'AC_HIGH_POWER', 'HIGH_POWER_MARKERS', 'NIGHT_PLISTS',
            'NIGHT_LOCK', 'SPOTLIGHT_STOPPED', 'KEEP_AWAKE_AGENT'])

    def test_every_effect_truth_table(self):
        span = (('p', 90, 110),)
        for effect, set_fields, explanation, debt, unknown in (
            (h.Effect.NETWORK_TIME_OFF, {'network_time_on': False},
             {'active_plan_spans': span}, {}, {'network_time_on': None}),
            (h.Effect.AC_HIGH_POWER, {'ac_powermode': 2},
             {'night_lock_held': True}, {}, {'ac_powermode': None}),
            (h.Effect.HIGH_POWER_MARKERS, {'markers': (h.MarkerFact('high-power.marker', True, 'p', h.R1_TAG),)},
             {'night_lock_held': True}, {}, {'markers': None}),
            (h.Effect.NIGHT_PLISTS, {'labels': tuple(h.LabelFact(l, True, True, 'p', True) for l in h.NIGHT_LABELS)},
             {'active_plan_spans': span}, {}, {'labels': tuple(h.LabelFact(l) for l in h.NIGHT_LABELS)}),
            (h.Effect.NIGHT_LOCK, {'night_lock_held': True, 'night_lock_owner_plan_id': 'p'},
             {'active_plan_spans': span}, {}, {'night_lock_held': None}),
            (h.Effect.SPOTLIGHT_STOPPED, {'spotlight_stopped': True},
             {'desk_fence': h.DeskFence('r0', 123, 110, True)}, {}, {'spotlight_stopped': None}),
            (h.Effect.KEEP_AWAKE_AGENT, {'keep_awake_agent': True},
             {}, {'keep_awake_expected': False}, {'keep_awake_agent': None}),
        ):
            for status, fields in (('explained', explanation), ('owed', debt), ('unknown', unknown)):
                with self.subTest(effect=effect, status=status):
                    rows = effect_rows(clean(**(set_fields | fields)), effect)
                    self.assertTrue(rows)
                    self.assertEqual({r.status for r in rows}, {status})
                    self.assertEqual({r.owed for r in rows}, {True if status == 'owed' else
                                                            None if status == 'unknown' else False})
                    if status == 'explained':
                        self.assertTrue(all(r.explained_by for r in rows))
            with self.subTest(effect=effect, status='clear'):
                self.assertEqual({r.status for r in effect_rows(clean(), effect)}, {'clear'})

    def test_all_unobserved_are_unknown(self):
        rows = h.owed_effects(h.HostFacts())
        self.assertEqual({r.effect for r in rows if r.owed is None}, set(h.Effect))
        self.assertFalse(any(r.owed is False for r in rows))

    def test_network_invariant_full_table(self):
        for on in (True, False, None):
            for spans in ((), (('p', 90, 110),), None):
                with self.subTest(on=on, spans=spans):
                    expected = 'pass' if on is True or spans == (('p', 90, 110),) else (
                        'violated' if on is False and spans == () else 'unknown')
                    check = h.invariant_network_time_on_without_active_span(clean(network_time_on=on, active_plan_spans=spans))
                    self.assertEqual(check.status, expected)
                    if expected == 'violated':
                        self.assertEqual(check.reason, 'NETWORK_TIME_OFF_WITHOUT_ACTIVE_SPAN')

    def test_ac_invariant_full_table(self):
        for mode in (0, 1, 2, 99, None):
            for lock in (True, False, None):
                with self.subTest(mode=mode, lock=lock):
                    expected = 'pass' if mode == 0 or lock is True else (
                        'violated' if mode is not None and lock is False else 'unknown')
                    check = h.invariant_ac_automatic_without_night_lock(clean(ac_powermode=mode, night_lock_held=lock))
                    self.assertEqual(check.status, expected)
                    if expected == 'violated':
                        self.assertEqual(check.reason, 'AC_NONZERO_WITHOUT_NIGHT_LOCK')

    def test_span_boundaries_census_and_owner(self):
        for now, expected in ((89, True), (90, False), (109.999, False), (110, True), (None, None)):
            rows = effect_rows(clean(network_time_on=False, active_plan_spans=[['p', 90, 110]], now=now), h.Effect.NETWORK_TIME_OFF)
            self.assertIs(rows[0].owed, expected)
        for effect, fields in (
            (h.Effect.NETWORK_TIME_OFF, {'network_time_on': False}),
            (h.Effect.NIGHT_LOCK, {'night_lock_held': True}),
            (h.Effect.HIGH_POWER_MARKERS, {'markers': (h.MarkerFact('m', True, 'p'),)}),
        ):
            with self.subTest(effect=effect):
                self.assertIsNone(effect_rows(clean(active_plan_spans=None, **fields), effect)[0].owed)
        # A lock cannot excuse network time with no active span. A span cannot
        # excuse a nonzero mode without the lock.
        self.assertTrue(effect_rows(clean(network_time_on=False, night_lock_held=True), h.Effect.NETWORK_TIME_OFF)[0].owed)
        self.assertTrue(effect_rows(clean(ac_powermode=2, active_plan_spans=(('p', 90, 110),)), h.Effect.AC_HIGH_POWER)[0].owed)
        self.assertIsNone(effect_rows(clean(ac_powermode=2, night_lock_held=None), h.Effect.AC_HIGH_POWER)[0].owed)

    def test_marker_explanation_and_owner_mismatch(self):
        for owner, span, lock, expected, reason in (
            ('p', (('p', 90, 110),), False, False, 'OWNER_PLAN_SPAN'),
            ('old', (('p', 90, 110),), False, True, 'HIGH_POWER_MARKER_ORPHANED'),
            (None, (('p', 90, 110),), False, None, 'EXPLANATION_UNOBSERVED'),
            ('old', None, True, False, 'NIGHT_LOCK_HELD'),
            ('old', (), None, None, 'EXPLANATION_UNOBSERVED'),
        ):
            with self.subTest(owner=owner, lock=lock, span=span):
                facts = clean(markers=(h.MarkerFact('m', True, owner),), active_plan_spans=span, night_lock_held=lock)
                row = effect_rows(facts, h.Effect.HIGH_POWER_MARKERS)[0]
                self.assertIs(row.owed, expected)
                self.assertEqual(row.reason, reason)
        for exists, status in ((False, 'clear'), (None, 'unknown')):
            self.assertEqual(effect_rows(clean(markers=(h.MarkerFact('m', exists),)), h.Effect.HIGH_POWER_MARKERS)[0].status, status)

    def test_labels_full_presence_and_result_table(self):
        for disk in (True, False, None):
            for loaded in (True, False, None):
                for result in (True, False, None):
                    with self.subTest(disk=disk, loaded=loaded, result=result):
                        label = h.LabelFact(h.NIGHT_LABELS[0], disk, loaded, result_present=result)
                        facts = clean(labels=(label, h.LabelFact(h.NIGHT_LABELS[1], False, False)))
                        rows = effect_rows(facts, h.Effect.NIGHT_PLISTS)
                        set_ = disk is True or loaded is True
                        expected = 'owed' if set_ and result is True else 'clear' if disk is False and loaded is False else 'unknown'
                        self.assertEqual(rows[0].status, expected)
                        unknown_fields = {r.subject for r in rows[1:] if r.owed is None}
                        self.assertEqual(label.label + ':loaded' in unknown_fields, set_ and loaded is None)
                        self.assertEqual(label.label + ':on_disk' in unknown_fields, set_ and disk is None)
                        check = h.invariant_terminal_night_label_uninstalled(facts, label)
                        self.assertEqual(check.status, 'pass' if loaded is False or result is False else
                                         'violated' if loaded is True and result is True else 'unknown')
        label = h.LabelFact(h.NIGHT_LABELS[0], True, True, 'old')
        facts = clean(labels=(label, h.LabelFact(h.NIGHT_LABELS[1], False, False)), result_present=True,
                      active_plan_spans=(('p', 90, 110),))
        self.assertTrue(effect_rows(facts, h.Effect.NIGHT_PLISTS)[0].owed)
        self.assertEqual(h.invariant_terminal_night_label_uninstalled(facts, label).status, 'violated')
        facts = replace(facts, active_plan_spans=None)
        self.assertEqual(h.invariant_terminal_night_label_uninstalled(facts, label).status, 'unknown')

    def test_optional_outcomes_fail_closed_and_state_report(self):
        from joulewise.window_state import StateReport, WindowState, WindowOutcome, OutcomeReport
        facts = clean(labels=tuple(h.LabelFact(l, True, True) for l in h.NIGHT_LABELS))
        for word in ('MEASURED_OK', 'MEASURED_WITH_FLAGS', 'CHAIN_FAILED', 'REFUSED_PRE_CHAIN', 'ABORTED',
                     WindowOutcome.REFUSED_PRE_CHAIN,
                     StateReport(WindowState.REFUSED_PRE_CHAIN, OutcomeReport(WindowOutcome.REFUSED_PRE_CHAIN, {}, [], []))):
            with self.subTest(word=word):
                self.assertTrue(all(r.owed for r in effect_rows(facts, h.Effect.NIGHT_PLISTS, word)))
                self.assertEqual(h.invariant_terminal_night_label_uninstalled(facts, facts.labels[0], word).status, 'violated')
        for unknown in ('GO', 'REFUSED', 'UNKNOWN', 'new_success', object(),
                        StateReport(WindowState.UNKNOWN, None)):
            with self.subTest(unknown=unknown):
                rows = effect_rows(facts, h.Effect.NIGHT_PLISTS, unknown)
                self.assertTrue(all(r.owed is None for r in rows))
                self.assertTrue(any(r.reason == 'OUTCOME_UNRECOGNIZED' for r in rows))
                self.assertTrue(any(r.owed is None for r in h.owed_effects(clean(), unknown)))
        # A live span explains the labels, while an unknown outcome remains visible.
        facts = replace(facts, active_plan_spans=(('p', 90, 110),))
        self.assertEqual(h.invariant_terminal_night_label_uninstalled(facts, facts.labels[0]).status, 'pass')

    def test_fence_liveness_deadline_and_keep_awake_policy(self):
        for alive, deadline, now, expected in ((True, 101, 100, False), (False, 101, 100, True),
                                               (None, 100, 100, True), (True, 100, 100, True),
                                               (None, 101, 100, None), (True, 101, None, None)):
            with self.subTest(alive=alive, deadline=deadline, now=now):
                facts = clean(spotlight_stopped=True, desk_fence=h.DeskFence('r0', 123, deadline, alive), now=now)
                self.assertIs(effect_rows(facts, h.Effect.SPOTLIGHT_STOPPED)[0].owed, expected)
        self.assertIsNone(effect_rows(clean(spotlight_stopped=True, desk_fence_observed=False), h.Effect.SPOTLIGHT_STOPPED)[0].owed)
        self.assertIsNone(effect_rows(clean(keep_awake_agent=True, keep_awake_expected=None), h.Effect.KEEP_AWAKE_AGENT)[0].owed)

    def test_audit_november_10_three_obligations(self):
        facts = clean(network_time_on=False, network_time_owner_plan_id='r1-nov10',
                      labels=tuple(h.LabelFact(l, True, True, 'r1-nov10', True) for l in h.NIGHT_LABELS))
        owed = [r for r in h.owed_effects(facts, 'REFUSED_PRE_CHAIN') if r.owed]
        self.assertEqual([(r.effect.name, r.subject, r.owner_plan_id, r.reason) for r in owed], [
            ('NETWORK_TIME_OFF', 'network_time', 'r1-nov10', 'NETWORK_TIME_OFF_WITHOUT_ACTIVE_SPAN'),
            ('NIGHT_PLISTS', h.NIGHT_LABELS[0], 'r1-nov10', 'NIGHT_LABEL_TERMINAL_WITHOUT_ACTIVE_SPAN'),
            ('NIGHT_PLISTS', h.NIGHT_LABELS[1], 'r1-nov10', 'NIGHT_LABEL_TERMINAL_WITHOUT_ACTIVE_SPAN')])

    def test_audit_november_8_non_w1_killed_group(self):
        facts = clean(ac_powermode=2, markers=tuple(h.MarkerFact(n, True, 'r1-not-w1', h.R1_TAG) for n in h.MARKER_NAMES))
        owed = [r for r in h.owed_effects(facts) if r.owed]
        self.assertEqual([r.effect for r in owed], [h.Effect.AC_HIGH_POWER, h.Effect.HIGH_POWER_MARKERS, h.Effect.HIGH_POWER_MARKERS])
        self.assertEqual([r.owner_plan_id for r in owed], ['r1-not-w1'] * 3)
        conflicting = replace(facts, markers=(h.MarkerFact('a', True, 'a'), h.MarkerFact('b', True, 'b')))
        self.assertIsNone(effect_rows(conflicting, h.Effect.AC_HIGH_POWER)[0].owner_plan_id)

    def test_purity_frozen_snapshots_and_no_io(self):
        spans = [['p', 90, 110]]
        facts = clean(network_time_on=False, active_plan_spans=spans)
        spans[0][0] = 'changed'
        self.assertEqual(facts.active_plan_spans, (('p', 90, 110),))
        with self.assertRaises(FrozenInstanceError):
            facts.now = 101
        with mock.patch.object(builtins, 'open', side_effect=AssertionError('IO')), \
             mock.patch.object(os, 'open', side_effect=AssertionError('IO')), \
             mock.patch.object(os, 'stat', side_effect=AssertionError('IO')), \
             mock.patch.object(os, 'kill', side_effect=AssertionError('signal')), \
             mock.patch.object(h.time, 'time', side_effect=AssertionError('clock')), \
             mock.patch.object(subprocess, 'run', side_effect=AssertionError('command')), \
             mock.patch.object(socket, 'socket', side_effect=AssertionError('network')):
            first = h.owed_effects(facts)
            first.clear()
            self.assertEqual(h.owed_effects(facts), h.owed_effects(facts))
            self.assertEqual(facts.now, 100)

    def test_observation_issue_remains_unknown_with_otherwise_clean_facts(self):
        facts = clean(observation_issues=((h.Effect.HIGH_POWER_MARKERS, 'm', 'MARKER_OWNER_CONFLICT'),))
        unknowns = [r for r in h.owed_effects(facts) if r.owed is None]
        self.assertEqual(unknowns, [h.Owed(h.Effect.HIGH_POWER_MARKERS, 'm', None, None, None, None,
                                         'MARKER_OWNER_CONFLICT')])

    def test_invalid_facts_rejected(self):
        for kwargs in ({'network_time_on': 1}, {'ac_powermode': True}, {'ac_powermode': -1},
                       {'now': float('nan')}, {'markers': [True]}, {'labels': []},
                       {'active_plan_spans': [('p', 2, 1)]}, {'active_plan_spans': [(None, 1, 2)]},
                       {'network_time_owner_plan_id': ''}, {'desk_fence_observed': None}, {'desk_fence': {}}):
            with self.subTest(kwargs=kwargs), self.assertRaises((TypeError, ValueError)):
                h.HostFacts(**kwargs)
        for args in (('', 123, 1), ('r0', True, 1), ('r0', 123, float('inf'))):
            with self.assertRaises(ValueError):
                h.DeskFence(*args)
        with self.assertRaises(ValueError):
            h.LabelFact('new-night-label')


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value if isinstance(value, str) else json.dumps(value))
        return path

    def test_default_tmpdir_empty_is_partial_never_live_clean(self):
        with mock.patch.object(subprocess, 'run', side_effect=AssertionError('command')):
            facts = h.observe_host_state_dir(self.root)
        self.assertEqual([m.exists for m in facts.markers], [False, False])
        self.assertIsNone(facts.night_lock_held)
        self.assertIsNone(facts.network_time_on)
        self.assertIsNone(facts.active_plan_spans)
        self.assertTrue(facts.desk_fence_observed)
        self.assertFalse(facts.observation_issues)
        self.assertTrue(any(r.owed is None for r in h.owed_effects(facts)))

    def test_both_marker_generations_and_opaque_owner_matching(self):
        plan = self.root / 'plan'
        self.write('plan/night_plan.json', {'plan_id': 'p', 'custody_root': '/do/not/follow'})
        self.write('plan/night/result.json', 'not read as JSON')
        self.write('high-power.marker', h.W1_TAG + '\n' + json.dumps({'plan_path': str(plan / 'night_plan.json')}) + '\n')
        self.write('.align-r1-high-power', h.R1_TAG + '\n')
        self.write('night.lock', {'pid': 999999, 'role': 'night:p'})
        self.write('desk_fence.json', {'purpose': 'r0', 'pid': 123, 'deadline': 200})
        self.write('spotlight-stopped', '123 corespotlightd\n')
        for l in h.NIGHT_LABELS:
            self.write(l + '.plist', 'existence only')
        facts = h.observe_host_state_dir(self.root, plan_dirs=(plan,))
        self.assertEqual([(m.exists, m.owner_plan_id, m.tag) for m in facts.markers[:2]],
                         [(True, 'p', h.W1_TAG), (True, None, h.R1_TAG)])
        self.assertEqual(facts.desk_fence, h.DeskFence('r0', 123, 200))
        self.assertIsNone(facts.spotlight_stopped)
        self.assertIsNone(facts.night_lock_held)
        self.assertTrue(all(l.on_disk and l.result_present for l in facts.labels))
        self.assertTrue(all(l.loaded is None for l in facts.labels))
        self.assertFalse(facts.observation_issues)
        self.write('high-power.marker', h.W1_TAG + ' (legacy suffix)\n')
        facts = h.observe_host_state_dir(self.root)
        self.assertFalse(facts.observation_issues)

    def test_custody_owner_and_conflicts(self):
        self.write('plan/night_plan.json', {'plan_id': 'p'})
        self.write('high-power.marker', h.W1_TAG + '\n' + json.dumps({'custody_root': str(self.root / 'plan')}) + '\n')
        self.assertEqual(h.observe_host_state_dir(self.root, plan_dirs=(self.root / 'plan',)).markers[0].owner_plan_id, 'p')
        self.write('high-power.marker', h.W1_TAG + '\n' + json.dumps({'custody_root': str(self.root / 'plan'), 'plan_id': 'other'}) + '\n')
        facts = h.observe_host_state_dir(self.root, plan_dirs=(self.root / 'plan',))
        self.assertIsNone(facts.markers[0].owner_plan_id)
        self.assertIn('MARKER_OWNER_CONFLICT', [r for _, _, r in facts.observation_issues])

    def test_receipt_names_both_locations_no_live_inference(self):
        for prefix in ('', 'night/'):
            for name, schema, key in (('network_time_off.json', 'joulewise.network_time_off.v1', 'exit_code'),
                                      ('network_time_off.action.json', 'joulewise.b5_network_time_off_action.v1', 'returncode')):
                with self.subTest(prefix=prefix, name=name):
                    path = self.write(prefix + name, {'schema': schema, key: 0, 'plan_id': 'p'})
                    facts = h.observe_host_state_dir(self.root)
                    self.assertEqual(facts.network_time_owner_plan_id, 'p')
                    self.assertIsNone(facts.network_time_on)
                    self.assertFalse(facts.observation_issues)
                    path.unlink()
        self.write('night_plan.json', {'plan_id': 'p'})
        self.write('network_time_off.action.json', {'schema': 'joulewise.b5_network_time_off_action.v1', 'returncode': 0})
        self.assertEqual(h.observe_host_state_dir(self.root).network_time_owner_plan_id, 'p')
        self.write('network_time_off.json', {'schema': 'joulewise.network_time_off.v1', 'exit_code': 0, 'plan_id': 'q'})
        facts = h.observe_host_state_dir(self.root)
        self.assertIsNone(facts.network_time_owner_plan_id)
        self.assertIn('NETWORK_TIME_OWNER_CONFLICT', [r for _, _, r in facts.observation_issues])

    def test_failed_or_unknown_receipts_are_unknown(self):
        for doc in ({}, {'schema': 'future'}, {'schema': 'joulewise.network_time_off.v1', 'exit_code': True},
                    {'schema': 'joulewise.network_time_off.v1', 'exit_code': 1},
                    {'schema': 'joulewise.network_time_off.v1', 'exit_code': 0, 'plan_id': []},
                    {'schema': 'joulewise.network_time_off.v1', 'exit_code': 0, 'error': 'failed'},
                    {'schema': 'joulewise.network_time_off.v1', 'exit_code': 0, 'timed_out': True}):
            with self.subTest(doc=doc):
                self.write('network_time_off.json', doc)
                facts = h.observe_host_state_dir(self.root)
                self.assertIsNone(facts.network_time_owner_plan_id)
                self.assertTrue(any(r.owed is None for r in h.owed_effects(facts)))
                self.assertIn('OFF_RECEIPT_UNCONFIRMED', [r for _, _, r in facts.observation_issues])

    def test_malformed_records_are_not_clean(self):
        for name, content, code in (
            ('high-power.marker', h.R1_TAG + '\n[]', 'MARKER_OWNER_MALFORMED'),
            ('high-power.marker', h.R1_TAG + '\n{', 'MARKER_OWNER_MALFORMED'),
            ('high-power.marker', 'future-tag', 'MARKER_TAG_UNRECOGNIZED'),
            ('high-power.marker', h.R1_TAG + '\n' + json.dumps({'plan_id': []}), 'MARKER_OWNER_MALFORMED'),
            ('desk_fence.json', '{}', 'DESK_FENCE_MALFORMED'),
            ('desk_fence.json', '[]', 'RECORD_MALFORMED'),
            ('desk_fence.json', '{', 'RECORD_MALFORMED'),
            ('night_plan.json', '{}', 'PLAN_ID_UNRECOGNIZED'),
        ):
            with self.subTest(name=name, content=content):
                path = self.write(name, content)
                facts = h.observe_host_state_dir(self.root)
                self.assertIn(code, [r for _, _, r in facts.observation_issues])
                if name == 'desk_fence.json':
                    self.assertFalse(facts.desk_fence_observed)
                path.unlink()
        for content in (b'\xff', b'x' * (h.MAX_RECORD_BYTES + 1)):
            (self.root / 'high-power.marker').write_bytes(content)
            facts = h.observe_host_state_dir(self.root)
            self.assertTrue(facts.markers[0].exists)
            self.assertIn('RECORD_UNREADABLE', [r for _, _, r in facts.observation_issues])

    def test_missing_root_and_permission_error_remain_unknown(self):
        facts = h.observe_host_state_dir(self.root / 'missing')
        self.assertIsNone(facts.markers)
        self.assertTrue(all(p.on_disk is None for p in facts.labels))
        with mock.patch.object(os, 'open', side_effect=PermissionError('synthetic root')):
            denied_root = h.observe_host_state_dir(self.root)
        self.assertIsNone(denied_root.markers)
        self.assertTrue(all(p.on_disk is None for p in denied_root.labels))
        original = os.open
        def denied(path, *args, **kwargs):
            if path == 'high-power.marker':
                raise PermissionError('synthetic')
            return original(path, *args, **kwargs)
        with mock.patch.object(os, 'open', side_effect=denied):
            facts = h.observe_host_state_dir(self.root)
        self.assertIsNone(facts.markers[0].exists)
        self.assertIn('RECORD_UNREADABLE', [r for _, _, r in facts.observation_issues])

    def test_symlinks_root_leaf_intermediate_and_plan_refused(self):
        target = self.root / 'target'
        target.mkdir()
        link = self.root / 'alias'
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            h.observe_host_state_dir(link)
        with self.assertRaises((ValueError, OSError)):
            h.observe_host_state_dir(target, plan_dirs=(link,))
        for name in ('high-power.marker', 'network_time_off.json', 'night.lock', 'desk_fence.json',
                     'night_plan.json', h.NIGHT_LABELS[0] + '.plist', 'spotlight-stopped', 'night'):
            with self.subTest(name=name):
                path = target / name
                path.symlink_to(self.root / 'never-open', target_is_directory=name == 'night')
                with self.assertRaises((ValueError, OSError)):
                    h.observe_host_state_dir(target)
                path.unlink()

    def test_ancestor_alias_allowed_and_no_path_follow_or_enumeration(self):
        target = self.root / 'target'
        target.mkdir()
        state = target / 'state'
        state.mkdir()
        alias = self.root / 'ancestor'
        alias.symlink_to(target, target_is_directory=True)
        (state / 'high-power.marker').write_text(h.W1_TAG + '\n' + json.dumps({
            'plan_path': '/never/read/plan.json', 'custody_root': '/never/read/custody'}) + '\n')
        (state / 'unlisted').symlink_to('/never/read')
        with mock.patch.object(os, 'listdir', side_effect=AssertionError('enumeration')), \
             mock.patch.object(os, 'scandir', side_effect=AssertionError('enumeration')), \
             mock.patch.object(os, 'kill', side_effect=AssertionError('process probe')):
            facts = h.observe_host_state_dir(alias / 'state')
        self.assertTrue(facts.markers[0].exists)
        self.assertIsNone(facts.markers[0].owner_plan_id)

    def test_only_allowed_files_read_and_no_files_changed(self):
        self.write('night/result.json', 'presence only')
        self.write('restricted/measurement-secret', 'synthetic ignored')
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        original = os.open
        opened = []
        def record(path, *args, **kwargs):
            opened.append(str(path))
            self.assertFalse(args[0] & (os.O_CREAT | os.O_TRUNC | os.O_WRONLY | os.O_RDWR))
            return original(path, *args, **kwargs)
        with mock.patch.object(os, 'open', side_effect=record):
            h.observe_host_state_dir(self.root)
        self.assertFalse(any('restricted' in p for p in opened))
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            code = h.main(args)
        return code, output.getvalue()

    def test_exit_codes_and_json_unknown_precedence(self):
        self.assertEqual(dict(h.EXIT_CODES), {'clean': 0, 'owed': 1, 'usage': 2, 'unknown': 3})
        with tempfile.TemporaryDirectory() as root:
            base = ('--state-dir', root, '--json')
            complete = ('--network-time', 'on', '--ac-powermode', '0', '--night-lock', 'free',
                        '--no-active-spans', '--no-loaded-labels', '--spotlight', 'running')
            code, output = self.run_cli(*base)
            self.assertEqual(code, 3)
            self.assertTrue(json.loads(output)['unknowns'])
            code, output = self.run_cli(*base, *complete)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output)['owed'], [])
            self.assertEqual(json.loads(output)['unknowns'], [])
            code, output = self.run_cli(*base, '--network-time', 'off', '--no-active-spans')
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(output)['owed'][0]['reason'], 'NETWORK_TIME_OFF_WITHOUT_ACTIVE_SPAN')
            self.assertTrue(json.loads(output)['unknowns'])
            code, output = self.run_cli(*base, *complete, '--outcome', 'future')
            self.assertEqual(code, 3)
            self.assertEqual(json.loads(output)['unknowns'][0]['reason'], 'OUTCOME_UNRECOGNIZED')
            code, text = self.run_cli('--state-dir', root, *complete)
            self.assertEqual(code, 0)
            self.assertIn('No owed effects or unknowns', text)
            code, text = self.run_cli('--state-dir', root)
            self.assertEqual(code, 3)
            self.assertIn('unknown NETWORK_TIME_OFF', text)

    def test_loaded_labels_outcome_and_active_plan(self):
        with tempfile.TemporaryDirectory() as root:
            code, out = self.run_cli('--state-dir', root, '--no-active-spans', '--outcome', 'REFUSED_PRE_CHAIN',
                                     '--loaded-label', h.NIGHT_LABELS[0], '--loaded-label', h.NIGHT_LABELS[1], '--json')
            self.assertEqual(code, 1)
            self.assertEqual(len(json.loads(out)['owed']), 2)
            code, out = self.run_cli('--state-dir', root, '--no-active-spans', '--outcome', 'REFUSED_PRE_CHAIN',
                                     '--loaded-label', *h.NIGHT_LABELS, '--json')
            self.assertEqual(code, 1)
            self.assertEqual(len(json.loads(out)['owed']), 2)
            code, out = self.run_cli('--state-dir', root, '--network-time', 'off', '--active-plan', 'p', '1', '9999999999', '--json')
            self.assertEqual(code, 3)
            row = next(r for r in json.loads(out)['effects'] if r['effect'] == 'NETWORK_TIME_OFF')
            self.assertEqual(row['status'], 'explained')

    def test_usage_invalid_flags_conflicts_and_symlink(self):
        with tempfile.TemporaryDirectory() as root:
            for extra in (['--network-time', 'maybe'], ['--ac-powermode', '-1'], ['--loaded-label', 'unknown'],
                          ['--active-plan', 'p', 'nan', '1'], ['--active-plan', 'p', '2', '1'],
                          ['--no-active-spans', '--active-plan', 'p', '1', '2'],
                          ['--no-loaded-labels', '--loaded-label', h.NIGHT_LABELS[0]],
                          ['--no-loaded-labels', '--keep-awake', 'loaded']):
                with self.subTest(extra=extra), self.assertRaises(SystemExit) as cm:
                    self.run_cli('--state-dir', root, *extra)
                self.assertEqual(cm.exception.code, 2)
            link = Path(root) / 'link'
            link.symlink_to(root, target_is_directory=True)
            with self.assertRaises(SystemExit) as cm:
                self.run_cli('--state-dir', str(link))
            self.assertEqual(cm.exception.code, 2)
        with self.assertRaises(SystemExit) as cm:
            self.run_cli()
        self.assertEqual(cm.exception.code, 2)

    def test_module_entry_point(self):
        with tempfile.TemporaryDirectory() as root:
            run = subprocess.run([sys.executable, '-B', '-m', 'joulewise.host_effects', '--state-dir', root, '--json'],
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 3, run.stderr)
            self.assertTrue(json.loads(run.stdout)['unknowns'])

    def test_optional_window_state_import_missing_and_dependency_error(self):
        original = builtins.__import__
        def missing(name, *args, **kwargs):
            if name == 'joulewise.window_state':
                raise ModuleNotFoundError(name=name)
            return original(name, *args, **kwargs)
        with mock.patch.object(builtins, '__import__', side_effect=missing):
            module = runpy.run_path(h.__file__)
        self.assertIsNone(module['StateReport'])
        self.assertEqual(module['_outcome_word'](object()), 'UNKNOWN')
        def broken(name, *args, **kwargs):
            if name == 'joulewise.window_state':
                raise ModuleNotFoundError(name='broken_dependency')
            return original(name, *args, **kwargs)
        with mock.patch.object(builtins, '__import__', side_effect=broken), self.assertRaises(ModuleNotFoundError):
            runpy.run_path(h.__file__)


if __name__ == '__main__':
    unittest.main()
