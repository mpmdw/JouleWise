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
                        night_lock_held=False, plan_spans=(), now=100,
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
             {'plan_spans': span}, {}, {'network_time_on': None}),
            (h.Effect.AC_HIGH_POWER, {'ac_powermode': 2},
             {'night_lock_held': True}, {}, {'ac_powermode': None}),
            (h.Effect.HIGH_POWER_MARKERS, {'markers': (h.MarkerFact('high-power.marker', True, 'p', h.R1_TAG),)},
             {'night_lock_held': True}, {}, {'markers': None}),
            (h.Effect.NIGHT_PLISTS, {'labels': tuple(h.LabelFact(l, True, True, 'p', True) for l in h.NIGHT_LABELS)},
             {'plan_spans': span}, {}, {'labels': tuple(h.LabelFact(l) for l in h.NIGHT_LABELS)}),
            (h.Effect.NIGHT_LOCK, {'night_lock_held': True, 'night_lock_owner_plan_id': 'p'},
             {'plan_spans': span}, {}, {'night_lock_held': None}),
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
                    check = h.invariant_network_time_on_without_active_span(clean(network_time_on=on, plan_spans=spans))
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

    def test_mode_one_is_set_and_owed_without_lock(self):
        row = effect_rows(clean(ac_powermode=1), h.Effect.AC_HIGH_POWER)[0]
        self.assertEqual(row, h.Owed(h.Effect.AC_HIGH_POWER, 'ac_powermode', True,
                                   None, None, True, 'AC_NONZERO_WITHOUT_NIGHT_LOCK'))

    def test_power_owner_requires_observed_present_marker(self):
        for exists in (False, None):
            with self.subTest(exists=exists):
                facts = clean(ac_powermode=1, markers=(h.MarkerFact('old', exists, 'old'),
                                                      h.MarkerFact('present', True, 'p'),
                                                      h.MarkerFact('anonymous', True)))
                self.assertEqual(effect_rows(facts, h.Effect.AC_HIGH_POWER)[0].owner_plan_id, 'p')
                facts = replace(facts, markers=(h.MarkerFact('old', exists, 'old'),))
                self.assertIsNone(effect_rows(facts, h.Effect.AC_HIGH_POWER)[0].owner_plan_id)

    def test_power_and_keep_awake_explanation_codes(self):
        for observed, reason in ((True, 'NIGHT_LOCK_HELD'), (False, 'AC_NONZERO_WITHOUT_NIGHT_LOCK'),
                                 (None, 'EXPLANATION_UNOBSERVED')):
            with self.subTest(lock=observed):
                row = effect_rows(clean(ac_powermode=1, night_lock_held=observed), h.Effect.AC_HIGH_POWER)[0]
                self.assertEqual(row.reason, reason)
                self.assertEqual(row.explained_by, reason if observed is True else None)
        for authorized, reason in ((True, 'STANDING_KEEP_AWAKE_AUTHORIZATION'),
                                   (False, 'KEEP_AWAKE_AUTHORIZATION_WITHDRAWN'),
                                   (None, 'EXPLANATION_UNOBSERVED')):
            with self.subTest(authorized=authorized):
                row = effect_rows(clean(keep_awake_agent=True, keep_awake_expected=authorized),
                                  h.Effect.KEEP_AWAKE_AGENT)[0]
                self.assertEqual(row.reason, reason)
                self.assertEqual(row.explained_by, reason if authorized is True else None)

    def test_owned_label_timeline_and_boundaries(self):
        for label_name in h.NIGHT_LABELS:
            for now, phase in ((89, 'before'), (90, 'active'), (109.999, 'active'),
                               (110, 'after'), (111, 'after'), (None, None)):
                for result in (True, False, None):
                    with self.subTest(label=label_name, now=now, result=result):
                        labels = tuple(h.LabelFact(l, True, True, 'p', result) for l in h.NIGHT_LABELS)
                        facts = clean(labels=labels, plan_spans=(('p', 90, 110),), now=now)
                        row = next(r for r in effect_rows(facts, h.Effect.NIGHT_PLISTS)
                                   if r.subject == label_name)
                        expected, reason = None, 'LABEL_SPANS_OR_RESULT_UNKNOWN'
                        if phase == 'active':
                            expected, reason = False, 'ACTIVE_PLAN_SPAN'
                        elif phase == 'before' and result is True:
                            reason = 'RESULT_BEFORE_PLAN_SPAN'
                        elif phase == 'before' and result is False:
                            expected, reason = False, 'AWAITING_PLAN_SPAN'
                        elif phase == 'after' and result is not None:
                            expected = True
                            reason = ('NIGHT_LABEL_TERMINAL_WITHOUT_ACTIVE_SPAN' if result else
                                      'NIGHT_LABEL_AFTER_SPAN_WITHOUT_RESULT')
                        self.assertIs(row.owed, expected)
                        self.assertEqual(row.reason, reason)
                        self.assertEqual(row.explained_by, reason if expected is False else None)
                        check = h.invariant_terminal_night_label_uninstalled(
                            facts, next(l for l in labels if l.label == label_name))
                        self.assertEqual(check.status, 'unknown' if expected is None else
                                         'violated' if expected else 'pass')
                        self.assertEqual(check.reason, reason if expected is not False else 'SATISFIED')

    def test_owned_network_and_lock_timeline_and_boundaries(self):
        for effect, fields, ended_reason in (
            (h.Effect.NETWORK_TIME_OFF, {'network_time_on': False, 'network_time_owner_plan_id': 'p'},
             'NETWORK_TIME_OFF_WITHOUT_ACTIVE_SPAN'),
            (h.Effect.NIGHT_LOCK, {'night_lock_held': True, 'night_lock_owner_plan_id': 'p'},
             'NIGHT_LOCK_WITHOUT_ACTIVE_SPAN'),
        ):
            for now, expected, reason in ((89, False, 'AWAITING_PLAN_SPAN'),
                                          (90, False, 'ACTIVE_PLAN_SPAN'),
                                          (109.999, False, 'ACTIVE_PLAN_SPAN'),
                                          (110, True, ended_reason), (111, True, ended_reason),
                                          (None, None, 'EXPLANATION_UNOBSERVED')):
                with self.subTest(effect=effect, now=now):
                    # Another active plan cannot hide the owner's waiting/ended state.
                    facts = clean(**fields, plan_spans=(('p', 90, 110), ('q', 1, 200)), now=now)
                    row = effect_rows(facts, effect)[0]
                    self.assertIs(row.owed, expected)
                    self.assertEqual(row.reason, reason)
                    self.assertEqual(row.explained_by, reason if expected is False else None)

    def test_plan_census_missing_owner_and_ambiguous_inactive_spans(self):
        for spans, owner, now, phase in (
            (None, 'p', 100, None), ((), 'p', None, 'inactive'),
            ((('q', 90, 110),), 'p', 100, 'inactive'),
            ((('p', 90, 110),), 'p', None, None),
            ((('p', 1, 2), ('p', 200, 210)), 'p', 100, None),
            ((('p', 90, 110), ('p', 200, 210)), 'p', 100, 'active'),
            ((('p', 200, 210),), None, 100, 'inactive'),
        ):
            with self.subTest(spans=spans, owner=owner, now=now):
                facts = clean(plan_spans=spans, now=now, network_time_on=False,
                              network_time_owner_plan_id=owner, night_lock_held=True,
                              night_lock_owner_plan_id=owner,
                              labels=tuple(h.LabelFact(l, True, True, owner, False) for l in h.NIGHT_LABELS))
                for effect in (h.Effect.NETWORK_TIME_OFF, h.Effect.NIGHT_LOCK):
                    row = effect_rows(facts, effect)[0]
                    self.assertIs(row.owed, None if phase is None else phase == 'inactive')
                label_rows = effect_rows(facts, h.Effect.NIGHT_PLISTS)
                self.assertTrue(all(r.owed is (False if phase == 'active' else None) for r in label_rows))

    def test_label_result_fallback_and_unknown_outcomes_at_each_phase(self):
        for now in (89, 100, 110):
            for recorded in (True, False, None):
                for global_result in (True, False, None):
                    with self.subTest(now=now, recorded=recorded, global_result=global_result):
                        facts = clean(plan_spans=(('p', 90, 110),), now=now,
                                      result_present=global_result,
                                      labels=tuple(h.LabelFact(l, True, True, 'p', recorded) for l in h.NIGHT_LABELS))
                        effective = recorded if recorded is not None else global_result
                        expected = False if now == 100 else (None if effective is None else
                                   True if now == 110 else False if effective is False else None)
                        self.assertTrue(all(r.owed is expected for r in effect_rows(facts, h.Effect.NIGHT_PLISTS)))
                        for outcome in ('UNKNOWN', 'future'):
                            rows = effect_rows(facts, h.Effect.NIGHT_PLISTS, outcome)
                            self.assertTrue(any(r.reason == 'OUTCOME_UNRECOGNIZED' for r in rows))
                            self.assertTrue(all(r.owed is (False if now == 100 else None)
                                                for r in rows if r.subject != 'outcome'))
                        rows = effect_rows(facts, h.Effect.NIGHT_PLISTS, 'ABORTED')
                        self.assertTrue(all(r.owed is (False if now == 100 else True if now == 110 else None)
                                            for r in rows))
                        if now == 89:
                            self.assertEqual({r.reason for r in rows}, {'RESULT_BEFORE_PLAN_SPAN'})

    def test_network_invariant_remains_literal_before_owner_span(self):
        facts = clean(network_time_on=False, network_time_owner_plan_id='p',
                      plan_spans=(('p', 101, 110),))
        self.assertEqual(h.invariant_network_time_on_without_active_span(facts).status, 'violated')
        self.assertEqual(effect_rows(facts, h.Effect.NETWORK_TIME_OFF)[0].reason, 'AWAITING_PLAN_SPAN')

    def test_span_boundaries_census_and_owner(self):
        for now, expected in ((89, True), (90, False), (109.999, False), (110, True), (None, None)):
            rows = effect_rows(clean(network_time_on=False, plan_spans=[['p', 90, 110]], now=now), h.Effect.NETWORK_TIME_OFF)
            self.assertIs(rows[0].owed, expected)
        for effect, fields in (
            (h.Effect.NETWORK_TIME_OFF, {'network_time_on': False}),
            (h.Effect.NIGHT_LOCK, {'night_lock_held': True}),
            (h.Effect.HIGH_POWER_MARKERS, {'markers': (h.MarkerFact('m', True, 'p'),)}),
        ):
            with self.subTest(effect=effect):
                self.assertIsNone(effect_rows(clean(plan_spans=None, **fields), effect)[0].owed)
        # A lock cannot excuse network time with no active span. A span cannot
        # excuse a nonzero mode without the lock.
        self.assertTrue(effect_rows(clean(network_time_on=False, night_lock_held=True), h.Effect.NETWORK_TIME_OFF)[0].owed)
        self.assertTrue(effect_rows(clean(ac_powermode=2, plan_spans=(('p', 90, 110),)), h.Effect.AC_HIGH_POWER)[0].owed)
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
                facts = clean(markers=(h.MarkerFact('m', True, owner),), plan_spans=span, night_lock_held=lock)
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
                        self.assertEqual(check.status, 'pass' if loaded is False else
                                         'violated' if loaded is True and result is True else 'unknown')
        label = h.LabelFact(h.NIGHT_LABELS[0], True, True, 'old')
        facts = clean(labels=(label, h.LabelFact(h.NIGHT_LABELS[1], False, False)), result_present=True,
                      plan_spans=(('p', 90, 110),))
        self.assertTrue(effect_rows(facts, h.Effect.NIGHT_PLISTS)[0].owed)
        self.assertEqual(h.invariant_terminal_night_label_uninstalled(facts, label).status, 'violated')
        facts = replace(facts, plan_spans=None)
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
        facts = replace(facts, plan_spans=(('p', 90, 110),))
        self.assertEqual(h.invariant_terminal_night_label_uninstalled(facts, facts.labels[0]).status, 'pass')

    def test_fence_liveness_deadline_and_keep_awake_policy(self):
        for alive, deadline, now, expected in ((True, 101, 100, False), (False, 101, 100, True),
                                               (None, 100, 100, True), (True, 100, 100, True),
                                               (None, 101, 100, None), (True, 101, None, None)):
            with self.subTest(alive=alive, deadline=deadline, now=now):
                facts = clean(spotlight_stopped=True, desk_fence=h.DeskFence('r0', 123, deadline, alive), now=now)
                row = effect_rows(facts, h.Effect.SPOTLIGHT_STOPPED)[0]
                self.assertIs(row.owed, expected)
                reason = ('LIVE_DESK_FENCE' if expected is False else 'SPOTLIGHT_WITHOUT_LIVE_DESK_FENCE'
                          if expected is True else 'EXPLANATION_UNOBSERVED')
                self.assertEqual(row.reason, reason)
                self.assertEqual(row.explained_by, reason if expected is False else None)
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
        facts = clean(network_time_on=False, plan_spans=spans)
        spans[0][0] = 'changed'
        self.assertEqual(facts.plan_spans, (('p', 90, 110),))
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
                       {'plan_spans': [('p', 2, 1)]}, {'plan_spans': [(None, 1, 2)]},
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
        self.assertIsNone(facts.plan_spans)
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
        self.write('sealed-like/measurement-secret', 'synthetic ignored')
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        original = os.open
        opened = []
        def record(path, *args, **kwargs):
            opened.append(str(path))
            self.assertFalse(args[0] & (os.O_CREAT | os.O_TRUNC | os.O_WRONLY | os.O_RDWR))
            return original(path, *args, **kwargs)
        with mock.patch.object(os, 'open', side_effect=record):
            h.observe_host_state_dir(self.root)
        self.assertFalse(any('sealed-like' in p for p in opened))
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

    def test_plan_span_flags_keep_legacy_aliases_byte_identical(self):
        with tempfile.TemporaryDirectory() as root, mock.patch.object(h.time, 'time', return_value=100):
            for new, legacy in ((('--no-plan-spans',), ('--no-active-spans',)),
                                (('--plan-span', 'p', '90', '110'), ('--active-plan', 'p', '90', '110'))):
                self.assertEqual(self.run_cli('--state-dir', root, '--json', *new),
                                 self.run_cli('--state-dir', root, '--json', *legacy))

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
