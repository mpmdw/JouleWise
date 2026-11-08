"""R12 (RUN_STATE 214/215): next-arm triage list (B2) and the fixed-8 calibration predicate (B3).

Synthetic only. The stop tests check the predicate, not exchangeability.
"""
import itertools
from pathlib import Path
import unittest

from joulewise.align.apple import v4_cadence as cad

PAIRS = cad.CAL_PAIRS


ARTIFACT_SET = 'a' * 64
RECORD_COMMIT = 'b' * 40
# What the arm derives itself (artifact-set digest, commit existence); never taken from the packet.
IDENTITY = {'artifact_set_sha256': ARTIFACT_SET, 'record_commit_exists': True, 'record_bound': True}


def passing_packet(**overrides):
    """A complete passing packet for a calibration arm after window C2."""
    packet = {'schema': cad.TRIAGE_SCHEMA, 'previous_window': 'C2',
              'record_commit': RECORD_COMMIT, 'record_path': 'staging/window-record.json',
              'record_sha256': 'e' * 64, 'last_desk_passed_artifact_set_sha256': ARTIFACT_SET,
              'valid_until_epoch_s': 1000.0,
              'next_window_role': 'calibration',
              'calibration_windows': [window('C1', 7, 7), window('C2', 7, 7)],
              'checks': {row['id']: {'status': 'recorded' if row.get('gating', True) is False else 'pass',
                                     'basis': 'synthetic'}
                         for row in cad.NEXT_ARM_TRIAGE if row['source'] == cad.PACKET}}
    packet.update(overrides)
    return packet


def arm_seams():
    """Arm seams for tests that hand the arm a ready-made synthetic packet dict.

    The arm rebuilds the packet itself in production (a packet is a pointer, never trusted data);
    this seam stands for "the rebuild agrees with the supplied packet", fixes only what the arm
    derives (its own artifact-set digest, an unexpired window) and mocks the live meter and Git.
    """
    import copy

    def builder(root, supplied, *, now_epoch_s, current_artifact_set_sha256):
        if supplied is None:
            raise ValueError('no packet')
        built = copy.deepcopy(supplied)
        built['last_desk_passed_artifact_set_sha256'] = current_artifact_set_sha256
        built['valid_until_epoch_s'] = now_epoch_s + 600.0
        return built, True
    return dict(packet_builder=builder, meter_probe=lambda root: {'live': True, 'samples': 40},
                commit_check=lambda root, commit: True, record_check=lambda root, packet: True)


def write_battery_log(path, now, *, completion_age=600, step=100, end_age=30):
    """A synthetic battery log: charging, then a completed charge ``completion_age`` s ago, then float."""
    import json
    start = now-completion_age-2*step
    rows, t = [], start
    while t <= now-end_age:
        charging = t < now-completion_age
        rows.append({'schema': 'joulewise.battery_float.v1', 'probe_error': False, 'wall_time_s': t,
                     'external_connected': True, 'is_charging': charging,
                     'current_capacity_pct': 97 if charging else 100, 'passed': not charging})
        t += step
    Path(path).write_text(''.join(json.dumps(r) + '\n' for r in rows))
    return path


def window(name, spam, bank, status='final', captured=18):
    return {'window': name, 'status': status, 'captured_members': captured,
            'eligible_benign': {'spam': spam, 'bank': bank}}


INTERNAL = {'series_powermode': True, 'external_volume': True, 'charging_battery': True, 'meter_reader_live': True}
NOW_EPOCH = 500.0          # the arm's own clock in these synthetic packets (before valid_until_epoch_s)


class TriageListTests(unittest.TestCase):
    def test_every_listed_check_is_present_and_gating(self):
        # The frozen list enumerates the next-arm-dependent checks named by R12/R215.
        self.assertEqual(set(cad.TRIAGE_IDS), {
            'record_committed', 'terminal_completion', 'quiet_start_state', 'series_powermode',
            'external_volume', 'charging_battery', 'meter_reader_live', 'meter_coverage', 'capture_faults',
            'thermal_escalation', 'cohort_pool_rules', 'sentinel_roster', 'member_eligibility',
            'calibration_stop', 'full_desk_gate'})
        self.assertEqual(len(cad.TRIAGE_IDS), len(set(cad.TRIAGE_IDS)))
        ok = cad.next_arm_triage(passing_packet(), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertTrue(ok['admitted'], ok['reasons'])
        self.assertEqual(set(ok['checks']), set(cad.TRIAGE_IDS))
        # Each GATING check gates: failing, or removing, any one refuses the arm.
        self.assertEqual(set(cad.TRIAGE_IDS)-set(cad.GATING_IDS), {'meter_coverage'})
        for name in cad.GATING_IDS:
            with self.subTest(failing=name):
                internal, packet = dict(INTERNAL), passing_packet()
                if name in internal:
                    internal[name] = False
                elif name == 'calibration_stop':
                    packet['next_window_role'] = 'test'      # still 'continue' after two windows
                else:
                    packet['checks'][name]['status'] = 'fail'
                self.assertFalse(cad.next_arm_triage(packet, internal, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
            if name in passing_packet()['checks']:
                with self.subTest(missing=name):
                    packet = passing_packet()
                    del packet['checks'][name]
                    self.assertFalse(cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
            if name in INTERNAL:
                with self.subTest(unevaluated=name):
                    internal = dict(INTERNAL)
                    del internal[name]
                    self.assertFalse(cad.next_arm_triage(passing_packet(), internal, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])

    def test_packet_cannot_supply_or_override_arm_computed_checks(self):
        packet = passing_packet()
        packet['checks']['series_powermode'] = {'status': 'pass', 'basis': 'forged'}
        self.assertFalse(cad.next_arm_triage(packet, {**INTERNAL, 'series_powermode': False}, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        packet = passing_packet()
        packet['checks']['extra_check'] = {'status': 'pass', 'basis': 'unlisted'}
        self.assertFalse(cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])

    def test_malformed_packet_refuses(self):
        for packet in (None, {}, passing_packet(schema='x'), passing_packet(previous_window=''),
                       passing_packet(previous_window='W9x'), passing_packet(previous_window_is_w1=None),
                       passing_packet(code_or_config_changed='no')):
            with self.subTest(packet=packet):
                self.assertFalse(cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        blank = passing_packet()
        blank['checks']['record_committed']['basis'] = ' '
        self.assertFalse(cad.next_arm_triage(blank, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])

    def test_full_desk_gate_is_required_after_w1_and_after_code_or_config_change(self):
        # Both conditions are DERIVED: the window id, and the artifact-set digest vs the last desk pass.
        for case in ({'previous_window': 'W1', 'calibration_windows': []},
                     {'last_desk_passed_artifact_set_sha256': 'c' * 64},
                     {'last_desk_passed_artifact_set_sha256': None}):
            packet = passing_packet(**case)
            packet['checks']['full_desk_gate'] = {'status': 'deferred', 'basis': 'desk running off MBP'}
            with self.subTest(case=case):
                refused = cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
                self.assertFalse(refused['admitted'])
                self.assertTrue(refused['full_desk_required'])
                packet['checks']['full_desk_gate'] = {'status': 'pass', 'basis': 'desk complete'}
                self.assertTrue(cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        # An unchanged later window need not wait for the desk's pass, but must report it.
        later = passing_packet()
        later['checks']['full_desk_gate'] = {'status': 'deferred', 'basis': 'running on laptop'}
        self.assertTrue(cad.next_arm_triage(later, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        later['checks']['full_desk_gate'] = {'status': 'not_applicable', 'basis': 'running on laptop'}
        self.assertFalse(cad.next_arm_triage(later, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        other = passing_packet()
        other['checks']['record_committed'] = {'status': 'deferred', 'basis': 'commit running'}
        self.assertFalse(cad.next_arm_triage(other, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        # No identity from the arm: nothing is assumed unchanged.
        unknown = passing_packet()
        unknown['checks']['full_desk_gate'] = {'status': 'deferred', 'basis': 'running'}
        self.assertFalse(cad.next_arm_triage(unknown, INTERNAL)['admitted'])

    def test_a_contradictory_packet_flag_refuses_and_agreeing_flags_are_accepted(self):
        # DELTA-S2-M2: a stale flag can never waive the post-W1 desk or the code-change desk.
        packet = passing_packet(previous_window='W1', previous_window_is_w1=False, calibration_windows=[])
        packet['checks']['full_desk_gate'] = {'status': 'deferred', 'basis': 'running'}
        result = cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertFalse(result['admitted'])
        self.assertTrue(any('contradicts' in r for r in result['reasons']))
        stale = passing_packet(code_or_config_changed=False, last_desk_passed_artifact_set_sha256='c' * 64)
        stale['checks']['full_desk_gate'] = {'status': 'deferred', 'basis': 'running'}
        self.assertFalse(cad.next_arm_triage(stale, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        agreeing = passing_packet(previous_window_is_w1=False, code_or_config_changed=False)
        self.assertTrue(cad.next_arm_triage(agreeing, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        derived = cad.next_arm_triage(passing_packet(previous_window='W1', previous_window_is_w1=True,
                                                     calibration_windows=[]), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertTrue(derived['derived']['previous_window_is_w1'])

    def test_expiry_is_mandatory_and_checked_against_the_arms_clock(self):
        self.assertTrue(cad.next_arm_triage(passing_packet(), INTERNAL, IDENTITY, now_epoch_s=1000.0)['admitted'])
        for bad in (None, 'soon', float('nan'), True):
            packet = passing_packet(valid_until_epoch_s=bad)
            self.assertFalse(cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        gone = passing_packet()
        del gone['valid_until_epoch_s']
        self.assertFalse(cad.next_arm_triage(gone, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        self.assertFalse(cad.next_arm_triage(passing_packet(), INTERNAL, IDENTITY, now_epoch_s=1000.1)['admitted'])
        self.assertFalse(cad.next_arm_triage(passing_packet(), INTERNAL, IDENTITY)['admitted'])      # no arm clock
        self.assertFalse(cad.next_arm_triage(passing_packet(), INTERNAL, IDENTITY, now_epoch_s=float('inf'))['admitted'])

    def test_window_ids_accept_an_attempt_suffix_and_nothing_else(self):
        for good in ('R1', 'W1', 'C1', 'C8', 'T3', 'D2', 'C3#2', 'C12#10'):
            self.assertTrue(cad.WINDOW_ID.match(good), good)
        for bad in ('C0', 'C3#', 'C3#0', 'C3#2#3', 'C-1', 'C1-refusal-1', 'c1', 'W1#2x', '', 'C3 #2'):
            self.assertFalse(cad.WINDOW_ID.match(bad), bad)
        rows = [window('C1', 7, 7), window('C2', 0, 0, captured=0), window('C2#2', 7, 7)]
        self.assertEqual(cad.calibration_stop(rows)['attempted'], 2)
        self.assertEqual(cad.calibration_stop(rows)['zero_capture_refusals'], 1)
        packet = passing_packet(previous_window='C2#2', calibration_windows=rows)
        self.assertTrue(cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])

    def test_record_commit_must_name_a_commit_the_arm_found(self):
        self.assertTrue(cad.next_arm_triage(passing_packet(), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        self.assertFalse(cad.next_arm_triage(passing_packet(), INTERNAL,
                                             {**IDENTITY, 'record_commit_exists': False}, now_epoch_s=NOW_EPOCH)['admitted'])
        for bad in (None, 'abc', 'B' * 40):
            self.assertFalse(cad.next_arm_triage(passing_packet(record_commit=bad), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        # smoke G1: the packet must also be bound to the last committed record
        self.assertFalse(cad.next_arm_triage(passing_packet(), INTERNAL, {**IDENTITY, 'record_bound': False})['admitted'])
        self.assertFalse(cad.next_arm_triage(passing_packet(record_sha256=None), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        self.assertFalse(cad.next_arm_triage(passing_packet(record_path=None), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])

    def test_meter_coverage_is_recorded_with_gaps_and_never_gates(self):
        packet = passing_packet()
        packet['checks']['meter_coverage'] = {'status': 'recorded', 'basis': 'two members had a dropped counter',
                                              'gaps': ['D_spam_benign_s1_gated_held_a: counter drop']}
        result = cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertTrue(result['admitted'], result['reasons'])
        self.assertEqual(result['checks']['meter_coverage']['gaps'], ['D_spam_benign_s1_gated_held_a: counter drop'])
        del packet['checks']['meter_coverage']                       # even an absent tabulation never blocks v4
        absent = cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertTrue(absent['admitted'])
        self.assertEqual(absent['checks']['meter_coverage']['status'], 'missing')
        # only a meter reader that is not verified live gates
        self.assertFalse(cad.next_arm_triage(passing_packet(), {**INTERNAL, 'meter_reader_live': False}, IDENTITY,
                                             now_epoch_s=NOW_EPOCH)['admitted'])
        # the packet cannot assert the live meter: it is arm-computed
        packet = passing_packet()
        packet['checks']['meter_reader_live'] = {'status': 'pass', 'basis': 'lead-entered'}
        self.assertFalse(cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])

    def test_arm_result_retains_the_packet_its_digest_and_the_calibration_summary(self):
        a = cad.next_arm_triage(passing_packet(), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        b = cad.next_arm_triage(passing_packet(calibration_windows=[window('C1', 6, 6), window('C2', 7, 7)]),
                                INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertEqual(a['packet'], passing_packet())
        self.assertNotEqual(a['packet_sha256'], b['packet_sha256'])
        self.assertEqual(b['calibration']['eligible_by_pair'], {'spam': 13, 'bank': 13})

    def test_template_lists_every_packet_check_and_fails_closed_until_filled(self):
        template = cad.triage_template('C2')
        self.assertEqual(set(template['checks']), {r['id'] for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.PACKET})
        self.assertFalse(cad.next_arm_triage(template, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])

    def test_not_applicable_is_only_for_previous_window_checks_before_w1(self):
        first = passing_packet(previous_window='R1', calibration_windows=[], next_window_role=None)
        for name in ('thermal_escalation', 'cohort_pool_rules', 'sentinel_roster', 'member_eligibility'):
            first['checks'][name] = {'status': 'not_applicable', 'basis': 'previous window is R1'}
        self.assertTrue(cad.next_arm_triage(first, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'], cad.next_arm_triage(first, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['reasons'])
        first['checks']['record_committed'] = {'status': 'not_applicable', 'basis': 'skip'}
        self.assertFalse(cad.next_arm_triage(first, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        later = passing_packet()
        later['checks']['thermal_escalation'] = {'status': 'not_applicable', 'basis': 'skip'}
        self.assertFalse(cad.next_arm_triage(later, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])


class CalibrationStopTests(unittest.TestCase):
    def test_constants_are_the_ruled_fixed_8_and_39_per_pair(self):
        self.assertEqual((cad.CAL_WINDOWS, cad.CAL_TARGET_PER_PAIR), (8, 39))
        for gone in ('CAL_MIN_WINDOWS', 'CAL_CAP_WINDOWS'):
            self.assertFalse(hasattr(cad, gone))        # no minimum, no early stop (RUN_STATE 217)

    def test_no_early_stop_even_when_six_or_seven_windows_already_meet_the_target(self):
        for n in (6, 7):
            rows = [window(f'C{i}', 7, 7) for i in range(1, n+1)]       # 42/42 or 49/49 >= 39
            result = cad.calibration_stop(rows)
            self.assertEqual((result['decision'], result['attempted']), ('continue', n))
        self.assertEqual(cad.calibration_stop([])['decision'], 'continue')
        rows = [window(f'C{i}', 7, 7, 'provisional') for i in range(1, 8)]
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'continue')     # provisional is fine before 8

    def test_exactly_eight_final_windows_decide(self):
        done = [window(f'C{i}', 7, 7) for i in range(1, 9)]
        self.assertEqual(cad.calibration_stop(done)['decision'], 'calibration_complete')
        pending = done[:7] + [window('C8', 7, 7, 'provisional')]
        self.assertEqual(cad.calibration_stop(pending)['decision'], 'pending_final_eligibility')
        with self.assertRaises(ValueError):
            cad.calibration_stop(done + [window('C9', 7, 7)])             # no ninth counted window

    def test_both_pairs_must_reach_39_after_eight(self):
        rows = [window(f'C{i}', 7, 4) for i in range(1, 9)]               # spam 56, bank 32
        result = cad.calibration_stop(rows)
        self.assertEqual((result['decision'], result['eligible_by_pair']['bank']), ('insufficient_calibration', 32))
        edge = [window(f'C{i}', 7, 5) for i in range(1, 8)] + [window('C8', 7, 4)]        # bank 39 exactly
        self.assertEqual(cad.calibration_stop(edge)['decision'], 'calibration_complete')
        short = [window(f'C{i}', 7, 5) for i in range(1, 8)] + [window('C8', 7, 3)]       # bank 38
        self.assertEqual(cad.calibration_stop(short)['decision'], 'insufficient_calibration')

    def test_lost_whole_window_still_counts_and_can_leave_the_target_unmet(self):
        # One whole-window loss: 7 x 7 = 49 >= 39 still completes; losing 2 of 8 leaves 42 and completes;
        # five losses leave 21 and fail closed.
        lost = lambda n: [window(f'C{i}', 7, 7) for i in range(1, 9-n)] + [window(f'L{i}', 0, 0) for i in range(n)]
        self.assertEqual(cad.calibration_stop(lost(1))['decision'], 'calibration_complete')
        self.assertEqual(cad.calibration_stop(lost(2))['decision'], 'calibration_complete')
        self.assertEqual(cad.calibration_stop(lost(5))['decision'], 'insufficient_calibration')

    def test_zero_capture_windows_do_not_count_and_two_in_a_row_escalate(self):
        refused = lambda name: window(name, 0, 0, captured=0)
        rows = [window('C1', 7, 7), refused('C2-refusal-1'), window('C2', 7, 7)]
        result = cad.calibration_stop(rows)
        self.assertEqual((result['decision'], result['attempted'], result['zero_capture_refusals']),
                         ('continue', 2, 1))
        self.assertEqual(cad.calibration_stop([window('C1', 0, 0, captured=1)])['attempted'], 1)   # one member counts
        eight = [window(f'C{i}', 7, 7) for i in range(1, 9)]
        self.assertEqual(cad.calibration_stop(eight + [refused('R1')])['decision'], 'calibration_complete')
        with self.assertRaises(ValueError):
            cad.calibration_stop(eight + [window('C9', 7, 7)])
        two = [window('C1', 7, 7), refused('R1'), refused('R2')]
        self.assertEqual(cad.calibration_stop(two)['decision'], 'escalate_to_lead')
        self.assertEqual(cad.calibration_stop([refused('R1'), window('C1', 7, 7), refused('R2')])['decision'], 'continue')
        for role in ('calibration', 'test'):
            self.assertFalse(cad.next_arm_triage(passing_packet(calibration_windows=two, next_window_role=role),
                                                 INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        with self.assertRaises(ValueError):
            cad.calibration_stop([window('C1', 3, 0, captured=0)])         # zero-capture cannot carry eligible members
        with self.assertRaises(ValueError):
            cad.calibration_stop([{'window': 'C1', 'status': 'final', 'eligible_benign': {'spam': 0, 'bank': 0}}])

    def test_decision_uses_only_counts_and_status(self):
        rows = [dict(window('C1', 7, 7), score=9.9, alarm=True)] + [window(f'C{i}', 7, 7) for i in range(2, 9)]
        self.assertEqual(cad.calibration_stop(rows), cad.calibration_stop([window(f'C{i}', 7, 7) for i in range(1, 9)]))

    def test_invalid_rows_are_refused(self):
        good = [window(f'C{i}', 7, 7) for i in range(1, 8)]
        for bad in (good + [window('C8', 8, 7)], good + [window('C8', -1, 7)], good + [window('C8', True, 7)],
                    good + [window('C1', 7, 7)], good + [window('C8', 7, 7, 'done')], good + [{'window': 'C8'}]):
            with self.subTest(bad=bad[-1]), self.assertRaises(ValueError):
                cad.calibration_stop(bad)

    def test_contradictory_count_rows_never_authorize_completion_or_test_entry(self):
        # DELTA H02: eligible benign members cannot outnumber the members captured.
        impossible = [window(f'C{i}', 7, 7, captured=1) for i in range(1, 9)]
        with self.assertRaises(ValueError):
            cad.calibration_stop(impossible)
        result = cad.next_arm_triage(passing_packet(calibration_windows=impossible, next_window_role='test'),
                                     INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertFalse(result['admitted'])
        self.assertTrue(any('contradictory' in r for r in result['reasons']))
        # boundary: exactly the captured members eligible is fine; one more is not
        ok = [window(f'C{i}', 7, 7, captured=14) for i in range(1, 9)]
        self.assertEqual(cad.calibration_stop(ok)['decision'], 'calibration_complete')
        for bad in (window('C1', 7, 7, captured=13), window('C1', 7, 7, captured=25), window('C1', -1, 7),
                    window('C1', 7.0, 7), window('C1', True, 7),
                    dict(window('C1', 3, 3), eligible_total=7)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                cad.calibration_stop([bad])
        self.assertEqual(cad.calibration_stop([dict(window('C1', 3, 3), eligible_total=6)])['attempted'], 1)

    def test_two_added_sentinels_do_not_make_capture_counts_impossible(self):
        # delta2 S2 M1: 22 + 2 added sentinels = 24 captured, still 7 eligible benign per pair.
        rows = [window(f'C{i}', 7, 7, captured=24) for i in range(1, 9)]
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'calibration_complete')
        self.assertEqual(cad.CAPTURED_MAX, 24)
        with self.assertRaises(ValueError):
            cad.calibration_stop([window('C1', 7, 7, captured=25)])      # beyond any authorized roster

    def test_calibration_totals_in_the_packet_must_sum_from_the_rows(self):
        rows = [window(f'C{i}', 7, 7) for i in range(1, 9)]
        good = cad.next_arm_triage(passing_packet(calibration_windows=rows, next_window_role='test',
                                                  calibration_totals={'spam': 56, 'bank': 56}), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertTrue(good['admitted'], good['reasons'])
        bad = cad.next_arm_triage(passing_packet(calibration_windows=rows, next_window_role='test',
                                                 calibration_totals={'spam': 56, 'bank': 40}), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertFalse(bad['admitted'])

    def test_an_unfinished_zero_capture_window_holds_the_gate_pending(self):
        # DELTA M01: provisional + zero captures is in flight, not a terminal refusal.
        rows = [window(f'C{i}', 6, 6) for i in range(1, 7)]
        rows.append(window('C7', 0, 0, status='provisional', captured=0))
        result = cad.calibration_stop(rows)
        self.assertEqual(result['decision'], 'pending_final_eligibility')
        self.assertFalse(result['counts_are_final'])
        self.assertEqual(result['unfinished_zero_capture_windows'], 1)
        # once it is final it is a refusal (not counted) and the gate continues
        rows[-1] = window('C7', 0, 0, status='final', captured=0)
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'continue')
        # an unfinished window never lets two refusals around it escalate
        chain = [window('R1', 0, 0, captured=0), window('R2', 0, 0, status='provisional', captured=0)]
        self.assertEqual(cad.calibration_stop(chain)['decision'], 'pending_final_eligibility')

    def test_a_signed_lead_ruling_resets_the_zero_capture_escalation_and_is_retained(self):
        refused = lambda name: window(name, 0, 0, captured=0)
        rows = [window('C1', 7, 7), refused('R1'), refused('R2')]
        ruling = {'ruling_id': 'RUN_STATE-218', 'text_sha256': 'd' * 64, 'resets': 'zero_capture_escalation',
                  'after_window': 'R2', 'lead_signature': 'lead: synthetic-ruling 2026-11-08'}
        self.assertEqual(cad.calibration_stop(rows)['decision'], 'escalate_to_lead')
        result = cad.calibration_stop(rows, [ruling])
        self.assertEqual((result['decision'], result['lead_rulings_applied']), ('continue', ['RUN_STATE-218']))
        self.assertEqual(result['zero_capture_refusals'], 2)         # the history is kept
        # another refusal pair after the ruling escalates again
        again = rows + [refused('R3'), refused('R4')]
        self.assertEqual(cad.calibration_stop(again, [ruling])['decision'], 'escalate_to_lead')
        # through the triage: admitted with the ruling, refused without; the ruling is retained
        packet = passing_packet(calibration_windows=rows, lead_rulings=[ruling])
        admitted = cad.next_arm_triage(packet, INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertTrue(admitted['admitted'], admitted['reasons'])
        self.assertEqual(admitted['lead_rulings'], [ruling])
        self.assertFalse(cad.next_arm_triage(passing_packet(calibration_windows=rows), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        for bad in ({**ruling, 'lead_signature': 'PENDING_LEAD_SIGNATURE'}, {**ruling, 'after_window': 'nope'},
                    {**ruling, 'resets': 'anything'}, {**ruling, 'text_sha256': 'x'}, {**ruling, 'ruling_id': ' '},
                    {k: v for k, v in ruling.items() if k != 'text_sha256'}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                cad.calibration_stop(rows, [bad])

    def test_triage_role_follows_the_fixed_8_decision(self):
        done = [window(f'C{i}', 7, 7) for i in range(1, 9)]
        self.assertFalse(cad.next_arm_triage(passing_packet(calibration_windows=done), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        test = cad.next_arm_triage(passing_packet(calibration_windows=done, next_window_role='test'), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)
        self.assertTrue(test['admitted'], test['reasons'])
        # Seven windows: a test arm is refused (no early stop), a calibration arm is allowed.
        seven = done[:7]
        self.assertTrue(cad.next_arm_triage(passing_packet(calibration_windows=seven), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        self.assertFalse(cad.next_arm_triage(passing_packet(calibration_windows=seven, next_window_role='test'),
                                             INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])
        failed = [window(f'C{i}', 0, 0) for i in range(1, 9)]
        for role in ('calibration', 'test'):
            self.assertFalse(cad.next_arm_triage(passing_packet(calibration_windows=failed,
                                                                next_window_role=role), INTERNAL, IDENTITY, now_epoch_s=NOW_EPOCH)['admitted'])


class RegistrationTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        text = (root / 'docs/align/pilot_protocol_v4.md').read_text()
        start = text.index('## R12 window cadence')
        cls.section = ' '.join(text[start:text.index('\n## ', start+10)].split())
        cls.r1 = (root / 'docs/align/r1_runtime_contract.md').read_text()

    def test_protocol_states_b1_b2_b3_and_lists_every_triage_check(self):
        for name in cad.TRIAGE_IDS:
            self.assertIn(f'`{name}`', self.section)
        for phrase in ('ceiling, not a reservation', 'authenticated terminal completion', 'RUN_STATE 217',
                       'insufficient_calibration', 'calibration_complete', 'fixed 8', 'not satisfied by counts alone',
                       'Open statistics item', 'minimum of 7', '0.5 s_r', 'zero-capture', 'escalate to the lead',
                       'lead_ruling', 'meter_reader_live', 'NON-GATING', 'derived by the arm', '67,371 s', '96,427 s', '--next-arm-triage'):
            self.assertIn(phrase, self.section)

    def test_protocol_states_tiers_stage_a_checklist_topup_evidence_and_dc_sealing(self):
        text = ' '.join((Path(__file__).resolve().parents[2] / 'docs/align/pilot_protocol_v4.md').read_text().split())
        for phrase in ('Stage A checklist additions', 'JW_WP22_FULL=1', '**Strict:**', '**Amendment:**', '`amendments` row',
                       '**strict is the default**', 'AMENDMENT_ALLOWLIST', 'dynamic closure', 'dynamic_closure_trace.json',
                       '--battery-log', 'derived from a logged battery record', 'continuous float',
                       'sample --loop', 'consecutive', 'no continuity rule', 'No sampler runs during a window',
                       '--window-battery-journal', 'stop --pidfile P',
                       'BENIGN members only', 'sealed (hash only)', 'U3 inconclusive'):
            self.assertIn(phrase, text)

    def test_stale_r1_sizing_is_marked_and_corrected(self):
        self.assertIn('STALE', self.r1)
        self.assertIn('67,371 s', self.r1)
        self.assertIn('96,427 s', self.r1)
        self.assertNotIn('window_max_s` is set from this table', self.r1)


if __name__ == '__main__':
    unittest.main()
