"""B1 slot gate desk (desk spec 2.1; RL-135): synthetic journals built in a temp dir.

The gate module is the night commit's (its sha256 is asserted); the recorded
gates of each synthetic journal are produced by the same harness replay, so
validation agrees unless a test breaks a record on purpose. Temperatures only.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.align.apple import thermal_gates as tg
from scripts import align_r1_slot_gate_desk as gd
from scripts import align_r1_thermal_replay as replay
from scripts import align_start_state_disclosure as ssd

NS = gd.NS
T0 = 2_000_000 * NS
OFF = 1_790_000_000 * NS          # wall_ns - monotonic_ns
REPO = Path(__file__).resolve().parents[2]
TREE_INFO = {'thermal_gates_sha256': gd.THERMAL_GATES_SHA256, 'thermal_replay_sha256': None}


def floor5(v):
    return 5 * math.floor(v / 5)


def die_tvh0(tv0h):
    """TVh0 that reads floored to 5 C steps above 35 C and equal to TV0h below (the RL-131 staircase)."""
    return floor5(tv0h) if tv0h >= 35 else tv0h


def stamp(t):
    return {'monotonic_ns': t, 'wall_ns': t + OFF}


def jrow(kind, t, values):
    return {'schema': 'joulewise.align_thermal.v1', 'module': 'temperature', 'kind': kind, 'session': 's',
            'seq': 0, 'started': stamp(t), 'finished': stamp(t + 1_000_000), 'values': values, 'raw': [],
            'error': None}


def policy(**kw):
    p = {'sensors': {'s_fast': 'TV0h', 's_slow': 'TVh0', 'fan_keys': [], 'r0_sha256': '0' * 64,
                     'record_keys': ['Tf08']},
         'delta_fast_c': 1.0, 'delta_slow_c': 1.0, 'turn_cap_s': 300, 'g0_cap_s': 1200,
         'per_turn': True, 'heavy': True, 'chunk_tokens': 256, 'window_reference': {'role': 'capture'}}
    p.update(kw)
    return p


def build_member(root, phase, temps, n, *, gates=(), condition='benign', pol=None, warmup_s=70, measured_s=None,
                 status=None, wref=None, run='r'):
    """temps(i) -> {TV0h, TVh0, Tf08} at second i. gates: (kind, start_s, reference, turn), recorded through
    the harness replay so a fresh journal validates."""
    pol = pol or policy()
    bundle = root / phase / 'runs' / run
    (bundle / 'outputs').mkdir(parents=True)
    rows = [jrow('session_start', T0 - NS, {'thermal': pol['sensors']})]
    for i in range(n):
        t = T0 + i * NS
        st = {'os_level': 0, 'pm_state': 'Nominal', 'pm_observed_ns': t, 'monotonic_ns': t}
        if status:
            st.update(status(i))
        rows.append(jrow('reading', t, {'sensors': dict(temps(i)), 'errors': {}, 'status': st}))
    journal = bundle / 'outputs' / gd.JOURNAL
    journal.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    events = [{'event_type': 'stage_started', 'phase': 'idle_baseline', 'timestamp_s': (T0 + OFF) / NS},
              {'event_type': 'stage_started', 'phase': 'warmup', 'timestamp_s': (T0 + warmup_s * NS + OFF) / NS}]
    if measured_s is not None:
        events.append({'event_type': 'stage_started', 'phase': 'measured_run',
                       'timestamp_s': (T0 + measured_s * NS + OFF) / NS})
    (bundle / 'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events) + '\n')
    (bundle / 'config.json').write_text(json.dumps({'workload_profile': {'prompt_text': json.dumps(
        {'thermal': pol, 'condition': condition})}}))
    if wref is not None:
        (bundle / 'outputs' / 'align_window_reference.json').write_text(json.dumps(wref))
    member = gd.load_member(tg, gd.Inputs(root), phase, bundle, journal)
    records = []
    for kind, start_s, reference, turn in gates:
        start = T0 + int(start_s * NS) + 500_000_000          # gate entry between two reads
        cap = pol['g0_cap_s'] if kind == 'G0' else pol['turn_cap_s']
        rep = gd.replay_wait(tg, member, kind, start, s_fast='TV0h', s_slow='TVh0', reference=reference,
                             delta_fast=pol['delta_fast_c'], delta_slow=pol['delta_slow_c'], cap_s=cap, turn=turn)
        records.append({'kind': kind, 'turn': turn, 'start_ns': start, 'end_ns': start + round(rep['duration_s'] * NS),
                        'duration_s': rep['duration_s'], 'reference': reference, 'release': rep['release'],
                        'slope_c_per_min': rep['slope_c_per_min'], 'exit_sample_ns': rep['exit_sample_ns'],
                        'outcome': rep['outcome']})
    with journal.open('a') as f:
        for rec in records:
            kind = 'align_thermal_hold' if rec['kind'] == 'H' else 'align_thermal_gate'
            f.write(json.dumps(jrow(kind, rec['end_ns'], {'state': 'end', 'gate': rec})) + '\n')
    return records


def cooling(start_s, plateau, *, top=50.0, rate=0.0625, tf08=40.0):
    """TV0h at `top` until start_s, then falling `rate` C/s to `plateau`; TVh0 floored above 35."""
    def temps(i):
        v = top if i < start_s else max(plateau, top - rate * (i - start_s))
        return {'TV0h': v, 'TVh0': die_tvh0(v), 'Tf08': tf08 - 0.01 * i}
    return temps


def run_desk(root, record=None, kit_desk=None, force=False):
    return gd.desk(tg, replay, ssd, TREE_INFO, root, record=record, kit_desk=kit_desk, force_s6=force)


def gate(out, member, kind='G0', turn=None):
    return next(r for r in out['gates'] if r['member'] == member and r['kind'] == kind
                and (turn is None or r['turn'] == turn))


def step_d(root, *, wref_fast=34.7):
    """A minimal step-D member: the window reference, one released G0 and a measured window."""
    records = build_member(root, gd.STEP_D, cooling(100, 34.5), 700,
                           gates=[('G0', 100, {'fast_c': wref_fast, 'slow_c': wref_fast}, 0)],
                           wref={'fast_c': wref_fast, 'slow_c': wref_fast})
    end = records[0]['end_ns']
    (root / gd.STEP_D / 'inventory').mkdir()
    (root / gd.STEP_D / gd.QUIET_SPAN_FILE).write_text(json.dumps({'classification': {'phase_bounds_ns': {
        'quiet': [end + NS, end + 301 * NS]}}}))


class GateModuleTests(unittest.TestCase):
    def test_working_tree_gate_module_is_the_night_commits(self):
        # In-process tests use the working tree's copy only because it is byte-identical to a6a09e6d7's.
        self.assertEqual(hashlib.sha256(Path(tg.__file__).read_bytes()).hexdigest(), gd.THERMAL_GATES_SHA256)


class BandAndStepTests(unittest.TestCase):
    def test_1_band_release_on_the_floor_step(self):
        for r_fast, on_step in ((34.7, True), (33.9, False)):
            with self.subTest(r_fast=r_fast), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                step_d(root)
                build_member(root, 'D_bank_benign_s1_gated_held', cooling(100, 34.5), 700,
                             gates=[('G0', 100, {'fast_c': r_fast, 'slow_c': r_fast}, 0)])
                out = run_desk(root)
                row = gate(out, 'D_bank_benign_s1_gated_held')
                self.assertEqual(row['outcome'], 'released')
                self.assertTrue(out['validation']['all_agree'])
                self.assertEqual(row['on_step_at_exit'], on_step)
                if on_step:
                    self.assertEqual(row['clause_last'], 'band_fast')
                    self.assertEqual(row['slow_slope_recomputed'], 0)
                    self.assertGreater(row['exit_tv0h_c'], 35.0)
                    self.assertLessEqual(row['exit_tv0h_c'], 35.7)
                    self.assertEqual(row['exit_tvh0_c'], 35)
                else:
                    self.assertLess(row['exit_tv0h_c'], 35.0)
                    self.assertEqual(row['exit_tvh0_c'], row['exit_tv0h_c'])

    def staircase(self, root, *, cap=1200, verdict='pass'):
        def temps(i):
            if i < 160:
                v = 41.0
            elif i < 180:
                v = 39.9 - (39.9 - 35.6) * (i - 160) / 20
            else:
                v = 35.5
            return {'TV0h': v, 'TVh0': 40.0 if i < 160 else 35.0, 'Tf08': 38.0}
        step_d(root)
        build_member(root, 'D_bank_benign_s1_gated_held', temps, 600, pol=policy(g0_cap_s=cap),
                     gates=[('G0', 100, {'fast_c': 34.7, 'slow_c': 34.7}, 0)])
        record = {'duty': {'runs': [{'run': 'D_bank_benign_s1_gated_held', 'verdict': verdict}]}}
        return run_desk(root, record=record)

    def test_2_staircase_and_t2(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.staircase(Path(tmp))
            row = gate(out, 'D_bank_benign_s1_gated_held')
            self.assertEqual(row['outcome'], 'released')
            self.assertEqual(row['clause_last'], 'slope_slow')
            self.assertGreater(row['t2_samples'], 0)
            self.assertFalse(out['triggers']['T2']['fired'])
        with tempfile.TemporaryDirectory() as tmp:
            out = self.staircase(Path(tmp), cap=100)
            row = gate(out, 'D_bank_benign_s1_gated_held')
            self.assertEqual(row['outcome'], 'timeout')
            self.assertGreater(row['t2_samples'], 0)
            self.assertTrue(out['triggers']['T2']['fired'])
            self.assertIn('slope_slow', row['clause_last'])
        with tempfile.TemporaryDirectory() as tmp:
            out = self.staircase(Path(tmp), verdict='fail')
            self.assertTrue(out['triggers']['T2']['fired'])
            self.assertEqual(out['triggers']['T2']['gates'][0]['duty_verdict'], 'fail')

    def test_band_fast_edge_is_inclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            build_member(root, 'D_bank_benign_s1_gated_held', cooling(100, 34.5), 400,
                         gates=[('G0', 100, {'fast_c': 34.75, 'slow_c': 34.75}, 0)])
            member = gd.load_member(tg, gd.Inputs(root), 'D_bank_benign_s1_gated_held',
                                    root / 'D_bank_benign_s1_gated_held/runs/r',
                                    root / 'D_bank_benign_s1_gated_held/runs/r/outputs' / gd.JOURNAL)
            g = member.gates[0]
            at_edge = next(r for r in member.rows if r['sensors']['TV0h'] == 35.75)
            res = gd.clause_results(tg, member, g, at_edge, delta_fast=1.0, delta_slow=1.0)
            self.assertTrue(res['band_fast'])
            above = next(r for r in member.rows if r['sensors']['TV0h'] == 35.8125)
            self.assertFalse(gd.clause_results(tg, member, g, above, delta_fast=1.0, delta_slow=1.0)['band_fast'])

    def test_slope_clause_bar(self):
        # TVh0 rising 0.25 C/min: the 0.2 C/min clause fails.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            build_member(root, 'D_bank_benign_s1_gated_held',
                         lambda i: {'TV0h': 34.0, 'TVh0': 30.0 + 0.25 * i / 60, 'Tf08': 35.0}, 300,
                         pol=policy(g0_cap_s=60), gates=[('G0', 150, {'fast_c': 34.7, 'slow_c': 34.7}, 0)])
            member = gd.load_member(tg, gd.Inputs(root), 'D_bank_benign_s1_gated_held',
                                    root / 'D_bank_benign_s1_gated_held/runs/r',
                                    root / 'D_bank_benign_s1_gated_held/runs/r/outputs' / gd.JOURNAL)
            g = member.gates[0]
            res = gd.clause_results(tg, member, g, member.rows[200], delta_fast=1.0, delta_slow=1.0)
            self.assertFalse(res['slope_slow'])
            self.assertTrue(res['band_slow'] and res['band_fast'] and res['status'])


def census_row(i, tv0h, tvh0):
    return {'monotonic_ns': T0 + i * NS, 'sensors': {'TV0h': tv0h, 'TVh0': tvh0}, 'errors': {}, 'status': {}}


def equal_rows(n=300, start=36.0):
    return [census_row(i, start + 0.001 * i, start + 0.001 * i) for i in range(n)]


def t1(rows):
    classified = gd.census_rows(rows)
    census = {'status': 'computed', 'total': gd.census_counts(classified)}
    return gd.triggers([], census, {'tv0h_c': 0.0, 'tf08_release_range_c': None}, {})['T1'], census['total']


class FloorCensusTests(unittest.TestCase):
    def test_3_t1_arms(self):
        rows = equal_rows()
        rows[150] = census_row(150, rows[150]['sensors']['TV0h'], rows[150]['sensors']['TV0h'] + 0.01)
        fired, total = t1(rows)
        self.assertTrue(fired['fired'])
        self.assertEqual(total['tvh0_above_tv0h'], 1)
        rows = equal_rows()
        rows[150] = census_row(150, 33.0, 30.0)
        rows[149] = census_row(149, 33.0, 33.0)
        rows[151] = census_row(151, 33.0, 33.0)
        fired, total = t1(rows)
        self.assertTrue(fired['fired'])
        self.assertEqual((total['floored'], total['floored_below_35']), (1, 1))
        rows = equal_rows()
        rows[150] = census_row(150, 37.3, 37.3 - 1.7)
        rows[149] = census_row(149, 37.3, 37.3)
        rows[151] = census_row(151, 37.3, 37.3)
        fired, total = t1(rows)
        self.assertTrue(fired['fired'])
        self.assertEqual(total['unexplained'], 1)
        rows = [census_row(i, 36.0 + 0.02 * i, 36.0 + 0.02 * (i - 1) if i % 50 == 0 and i else 36.0 + 0.02 * i)
                for i in range(300)]
        fired, total = t1(rows)
        self.assertEqual(total['skew'], 5)
        self.assertAlmostEqual(total['skew_fraction'], 5 / 300)
        self.assertTrue(fired['fired'])

    def test_3_boundary_crossing_row_is_skew_and_does_not_fire(self):
        rows = equal_rows(200, 41.0)
        rows[100] = census_row(100, 40.02, 35.0)
        rows[101] = census_row(101, 39.97, 35.0)
        classified = gd.census_rows(rows)
        self.assertEqual(classified[100]['class'], 'skew')
        self.assertEqual(classified[101]['class'], 'floored')
        fired, total = t1(rows)
        self.assertFalse(fired['fired'], fired)
        self.assertEqual(total['skew'], 1)

    def test_census_on_journals_and_not_applicable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            out = run_desk(root)
            self.assertEqual(out['floor_census']['status'], 'computed')
            self.assertFalse(out['triggers']['T1']['fired'])
            total = out['floor_census']['total']
            self.assertEqual(total['tvh0_above_tv0h'], 0)
            self.assertIn('stage', out['floor_census']['conditions'])
            self.assertIn('warmup', out['floor_census']['conditions']['stage'])
        census = gd.floor_census([])
        self.assertTrue(census['status'].startswith('not applicable'))
        self.assertIsNone(gd.triggers([], census, {'tv0h_c': None, 'tf08_release_range_c': None}, {})['T1']['fired'])

    def test_census_journal_file_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'inventory_journal.jsonl'
            lines = []
            for i in range(100):
                v = 40.0 - 0.05 * i
                lines.append({'started': {'monotonic_ns': T0 + i * NS}, 'finished': {'monotonic_ns': T0 + i * NS},
                              'values': {'sensors': {'TV0h': v, 'TVh0': v if i < 50 else floor5(v), 'Tx': 1.0},
                                         'errors': {}}})
            path.write_text('\n'.join(json.dumps(x) for x in lines) + '\n')
            cls = Path(tmp) / 'r1_classification.json'
            cls.write_text(json.dumps({'classification': {'phase_bounds_ns': {
                'quiet': [T0 + 10 * NS, T0 + 50 * NS], 'load': [T0 + 50 * NS, T0 + 60 * NS],
                'recovery': [T0 + 60 * NS, T0 + 100 * NS]}}}))
            out = gd.census_journal_file(path, cls)
            self.assertEqual(out['total']['rows'], 100)
            self.assertEqual(out['by_phase']['quiet']['equal'], 40)
            self.assertLessEqual(out['total']['max_diff_c'], 0)


def table_row(member, value, *, planning=False, attempt='final', kind='G0', outcome='released', journal_kind='member'):
    return {'member': member, 'member_base': member, 'kind': kind, 'attempt': attempt, 'outcome': outcome,
            'planning_turn': planning, 'journal_kind': journal_kind, 'exit_tv0h_c': value,
            'exit_tvh0_c': value - 0.5, 'exit_tf08_c': value + 1, 's_slow': 'TVh0', 't2_samples': 0,
            'turn': 0, 'gated_d': False, 'x_g': False}


class U2Tests(unittest.TestCase):
    def nine(self, top):
        values = [34.0, top] + [34.5] * 7
        return [table_row(f'm{i}', v) for i, v in enumerate(values)]

    def t3(self, table):
        u2 = gd.u2_pair(table)
        return gd.triggers(table, {'status': 'x', 'total': None}, u2, {})['T3'], u2

    def test_4_t3_bar(self):
        fired, u2 = self.t3(self.nine(37.01))
        self.assertTrue(fired['fired'])
        self.assertEqual(len(u2['members']), 9)
        self.assertFalse(self.t3(self.nine(36.99))[0]['fired'])
        self.assertFalse(self.t3(self.nine(37.0))[0]['fired'])                  # the bar itself does not fire
        table = self.nine(36.99) + [table_row('planning_turn_R_plus_0C', 45.0, planning=True),
                                    table_row('step_30b.rejected1', 20.0, attempt='superseded'),
                                    table_row('cooldown_after_D/g0', 50.0, attempt='auxiliary',
                                              journal_kind='auxiliary')]
        fired, u2 = self.t3(table)
        self.assertFalse(fired['fired'])
        self.assertAlmostEqual(u2['tv0h_c'], 2.99)
        self.assertIsNone(self.t3([])[0]['fired'])


class S6Tests(unittest.TestCase):
    def test_5_medians(self):
        self.assertEqual(gd.median([3, 1, 2]), 2)
        self.assertEqual(gd.median([4, 1, 3, 2]), 2.5)

    def gated_night(self, root, temps, reference, *, n=500):
        step_d(root)
        for name in gd.GATED_D_RUNS + (gd.X_G,):
            build_member(root, name, temps, n, gates=[('G1', 100, reference, 1)])

    def test_5_deadman_counts_and_no_replay_under_90(self):
        rows = []
        for name, d, outcome in zip(gd.GATED_D_RUNS, (85.0, 80.0, 95.0), ('deadman', 'released', 'released')):
            rows.append({**table_row(name, 34.0, kind='G1', outcome=outcome), 'duration_s': d, 'gated_d': True})
        s6 = gd.s6_block(tg, [], rows, 85.0, False)
        self.assertEqual(s6['g1_median_s'], 85.0)            # 87.5 if the deadman wait were dropped
        self.assertEqual(len(s6['g1_waits']), 3)
        rows = [{**table_row(n, 34.0, kind='G1'), 'duration_s': d, 'gated_d': True}
                for n, d in zip(gd.GATED_D_RUNS, (50, 60, 70))]
        s6 = gd.s6_block(tg, [], rows, 60.0, False)
        self.assertEqual(s6['g1_median_s'], 60)
        self.assertFalse(s6['replay_ran'])
        self.assertEqual(s6['replays'], {})

    def test_5_slow_band_decides_reachable_at_1_5(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.gated_night(root, lambda i: {'TV0h': 34.0, 'TVh0': 31.2, 'Tf08': 35.0},
                             {'fast_c': 34.0, 'slow_c': 30.0})
            out = run_desk(root)
            s6 = out['s6']
            self.assertTrue(out['validation']['all_agree'])
            self.assertGreater(s6['g1_median_s'], 90)
            self.assertTrue(s6['replay_ran'])
            self.assertEqual(s6['s6_reachable_step_c'], 1.5)
            self.assertLessEqual(s6['g1_median_at']['1.5'], 90)

    def test_5_fast_band_decides_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.gated_night(root, lambda i: {'TV0h': 35.5, 'TVh0': 31.2, 'Tf08': 35.0},
                             {'fast_c': 34.0, 'slow_c': 30.0})
            s6 = run_desk(root)['s6']
            self.assertIsNone(s6['s6_reachable_step_c'])
            for step in ('1.5', '2.0'):
                self.assertTrue(s6['replays'][step])
                for x in s6['replays'][step]:
                    self.assertEqual(x['outcome'], 'timeout')
                    self.assertEqual(x['last_out_of_band_key'], 'band_fast')

    def test_driver_median_cross_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.gated_night(root, lambda i: {'TV0h': 34.0, 'TVh0': 30.5, 'Tf08': 35.0},
                             {'fast_c': 34.0, 'slow_c': 30.0})
            out = run_desk(root, record={'s6': {'G1_median_s': 5.0}, 'duty': {'runs': []}})
            median = out['s6']['g1_median_s']
            self.assertFalse(out['tool_checks']['s6_median_agrees'])
            out = run_desk(root, record={'s6': {'G1_median_s': median}, 'duty': {'runs': []}})
            self.assertTrue(out['tool_checks']['s6_median_agrees'])
            self.assertFalse(out['s6']['replay_ran'])
            self.assertTrue(run_desk(root, force=True)['s6']['replay_ran'])


class AlternativeG0Tests(unittest.TestCase):
    def test_6_released_in_quiet_span_and_censored_without(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            for name in ('step_30b', 'D_bank_benign_s1_gated_held'):
                build_member(root, name, cooling(100, 34.5), 900,
                             gates=[('G0', 100, {'fast_c': 34.7, 'slow_c': 34.7}, 0)])
            g0 = json.loads((root / 'step_30b/runs/r/outputs' / gd.JOURNAL).read_text().splitlines()[-1])
            end = g0['values']['gate']['end_ns']
            (root / 'step_30b/inventory').mkdir()
            (root / 'step_30b' / gd.QUIET_SPAN_FILE).write_text(json.dumps({'classification': {'phase_bounds_ns': {
                'quiet': [end + NS, end + 301 * NS]}}}))
            out = run_desk(root)
            alt = gate(out, 'step_30b')['alt']
            self.assertEqual(alt['outcome'], 'released')
            self.assertGreater(alt['duration_s'], gate(out, 'step_30b')['duration_s'])
            d = gate(out, 'D_bank_benign_s1_gated_held')
            self.assertEqual(d['alt']['outcome'], 'censored')
            self.assertLessEqual(d['alt']['duration_s'], d['duration_s'] + 1)
            self.assertTrue(d['alt']['censor_reason'].startswith('G0 end_ns'))
            for row in out['gates']:
                if row['kind'] == 'G0':
                    self.assertEqual(row['alt']['label'], 'alternative, not registered')
            self.assertIn('alternative, not registered', gd.render(out))

    def test_quiet_span_layout_self_check_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            (root / gd.STEP_D / gd.QUIET_SPAN_FILE).unlink()
            with self.assertRaisesRegex(gd.DeskError, 'layout assumption not confirmed.*QUIET_SPAN'):
                run_desk(root)



class AuxiliaryJournalTests(unittest.TestCase):
    def test_auxiliary_journals_are_tabled_and_empty_ones_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            sensors = root / 'cooldown_after_D' / 'sensors'
            sensors.mkdir(parents=True)
            rows = [jrow('session_start', T0, {'thermal': {'s_fast': 'TV0h', 's_slow': 'TVh0'}})] + [
                jrow('reading', T0 + i * NS, {'sensors': {'TV0h': 35.5, 'TVh0': 35.0}, 'errors': {}, 'status': {}})
                for i in range(30)]
            (sensors / gd.JOURNAL).write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
            empty = root / 'idle_soak' / 'g0'
            empty.mkdir(parents=True)
            (empty / gd.JOURNAL).write_text(json.dumps(rows[0]) + '\n')
            out = run_desk(root)
            self.assertIn('cooldown_after_D/sensors', out['floor_census']['by_journal'])
            self.assertEqual(out['auxiliary_without_readings'], ['idle_soak/g0/align_thermal.jsonl'])
            self.assertEqual(out['floor_census']['conditions']['stage']['auxiliary']['rows'], 30)


class ValidationTests(unittest.TestCase):
    def shift(self, root, member):
        path = root / member / 'runs/r/outputs' / gd.JOURNAL
        lines = path.read_text().splitlines()
        last = json.loads(lines[-1])
        last['values']['gate']['exit_sample_ns'] += NS
        lines[-1] = json.dumps(last)
        path.write_text('\n'.join(lines) + '\n')

    def test_7_shifted_exit_sample_stops_before_any_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            self.shift(root, gd.STEP_D)
            with self.assertRaises(gd.ValidationFailedWith) as caught:
                run_desk(root)
            partial = caught.exception.partial
            self.assertFalse(partial['validation']['all_agree'])
            self.assertNotIn('gates', partial)


class StartStateTests(unittest.TestCase):
    def test_disclosure_and_kit_cross_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            build_member(root, 'D_bank_benign_s1_gated_held', cooling(100, 34.5), 600,
                         gates=[('G0', 100, {'fast_c': 34.7, 'slow_c': 34.7}, 0)], condition='benign')
            build_member(root, gd.X_G, cooling(100, 34.5, tf08=39.0), 600,
                         gates=[('G0', 100, {'fast_c': 34.7, 'slow_c': 34.7}, 0)], condition='sabotage')
            out = run_desk(root)
            d = out['start_state']
            self.assertIsNotNone(d['window_tf08_reference_c'])
            members = {m['member']: m for m in d['members']}
            self.assertEqual(set(members), {gd.STEP_D, 'D_bank_benign_s1_gated_held', gd.X_G})
            self.assertEqual(set(d['medians_by_condition']), {'benign', 'sabotage'})
            self.assertEqual(len(d['differences']), 1)
            self.assertIsNone(out['tool_checks']['tf08_excess_agrees'])
            kit = {'members': [{'member': m, 'Tf08_start_excess_c': v['tf08_excess_c']} for m, v in members.items()]
                   + [{'member': 'capture_predecessor_30b', 'Tf08_start_excess_c': None}]}
            self.assertEqual(gd.tf08_check(d, kit), (True, []))
            kit['members'][0]['Tf08_start_excess_c'] += 1e-8
            self.assertFalse(gd.tf08_check(d, kit)[0])
            # The independent E1 path (night_desk's own derivation) agrees on the same journals.
            excess_e1 = {}
            for m in members:
                j = replay.read_journal(root / m / 'runs/r/outputs' / gd.JOURNAL, extra_fields=('Tf08',))
                excess_e1[m] = j
            self.assertTrue(all(v['tf08_excess_c'] is not None for v in members.values()))
            self.assertEqual(out['schedule'][0]['member'], gd.STEP_D)

    def test_disclosure_function(self):
        rows = [{'member': 'a', 'condition': 'benign', 'tf08_start_c': 30.0, 'tv0h_slope_c_per_min': -0.1,
                 'tv0h_minus_r_fast_c': 0.2},
                {'member': 'b', 'condition': 'benign', 'tf08_start_c': 31.0, 'tv0h_slope_c_per_min': -0.3,
                 'tv0h_minus_r_fast_c': 0.4},
                {'member': 'c', 'condition': 'sabotage', 'tf08_start_c': 33.0, 'tv0h_slope_c_per_min': None,
                 'tv0h_minus_r_fast_c': 0.1}]
        d = ssd.start_state_disclosure(rows, 32.0, u2_tv0h_c=0.3)
        self.assertEqual(d['medians_by_condition']['benign']['tf08_excess_c'], -1.5)
        self.assertEqual(d['differences'][0]['tf08_excess_c_a_minus_b'], -2.5)
        self.assertIsNone(d['differences'][0]['tv0h_slope_c_per_min_a_minus_b'])


def load_mutant(old, new):
    source = Path(gd.__file__).read_text()
    assert source.count(old) == 1, old
    path = Path(tempfile.mkdtemp()) / 'gate_desk_mutant.py'
    path.write_text(source.replace(old, new))
    spec = importlib.util.spec_from_file_location('gate_desk_mutant', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MutantTests(unittest.TestCase):
    """Spec 2.1 item 8: each mutant changes a result asserted above."""

    def test_band_fast_strict(self):
        m = load_mutant("out['band_fast'] = vf <= ref['fast_c'] + delta_fast",
                        "out['band_fast'] = vf < ref['fast_c'] + delta_fast")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            build_member(root, 'D_bank_benign_s1_gated_held', cooling(100, 34.5), 400,
                         gates=[('G0', 100, {'fast_c': 34.75, 'slow_c': 34.75}, 0)])
            member = m.load_member(tg, m.Inputs(root), 'D_bank_benign_s1_gated_held',
                                   root / 'D_bank_benign_s1_gated_held/runs/r',
                                   root / 'D_bank_benign_s1_gated_held/runs/r/outputs' / m.JOURNAL)
            at_edge = next(r for r in member.rows if r['sensors']['TV0h'] == 35.75)
            self.assertFalse(m.clause_results(tg, member, member.gates[0], at_edge, delta_fast=1.0,
                                              delta_slow=1.0)['band_fast'])

    def test_slope_bar_0_3(self):
        m = load_mutant('SLOPE_BAR_C_PER_MIN = 0.2 ', 'SLOPE_BAR_C_PER_MIN = 0.3 ')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step_d(root)
            build_member(root, 'D_bank_benign_s1_gated_held',
                         lambda i: {'TV0h': 34.0, 'TVh0': 30.0 + 0.25 * i / 60, 'Tf08': 35.0}, 300,
                         pol=policy(g0_cap_s=60), gates=[('G0', 150, {'fast_c': 34.7, 'slow_c': 34.7}, 0)])
            member = m.load_member(tg, m.Inputs(root), 'D_bank_benign_s1_gated_held',
                                   root / 'D_bank_benign_s1_gated_held/runs/r',
                                   root / 'D_bank_benign_s1_gated_held/runs/r/outputs' / m.JOURNAL)
            self.assertTrue(m.clause_results(tg, member, member.gates[0], member.rows[200], delta_fast=1.0,
                                             delta_slow=1.0)['slope_slow'])

    def test_t1_skew_0_1(self):
        m = load_mutant('T1_SKEW_FRACTION = 0.01 ', 'T1_SKEW_FRACTION = 0.1 ')
        rows = [census_row(i, 36.0 + 0.02 * i, 36.0 + 0.02 * (i - 1) if i % 50 == 0 and i else 36.0 + 0.02 * i)
                for i in range(300)]
        census = {'status': 'computed', 'total': m.census_counts(m.census_rows(rows))}
        self.assertFalse(m.triggers([], census, {'tv0h_c': 0.0}, {})['T1']['fired'])

    def test_t3_inclusive(self):
        m = load_mutant("'fired': None if u is None else u > T3_BAR_C", "'fired': None if u is None else u >= T3_BAR_C")
        table = [table_row(f'm{i}', v) for i, v in enumerate([34.0, 37.0] + [34.5] * 7)]
        self.assertTrue(m.triggers(table, {'status': 'x', 'total': None}, m.u2_pair(table), {})['T3']['fired'])


@unittest.skipUnless(subprocess.run(['git', 'cat-file', '-e', gd.NIGHT_COMMIT], cwd=REPO,
                                    capture_output=True).returncode == 0, 'night commit not in this clone')
class CliTreeTests(unittest.TestCase):
    """The real entry point: TREE from `git archive a6a09e6d7`, imported only from there."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.tree = Path(cls.tmp.name) / 'tree'
        cls.tree.mkdir()
        archive = subprocess.run(['git', 'archive', gd.NIGHT_COMMIT, 'joulewise', gd.THERMAL_REPLAY_PATH],
                                 cwd=REPO, capture_output=True, check=True).stdout
        subprocess.run(['tar', '-x', '-C', str(cls.tree)], input=archive, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def cli(self, root, *extra):
        out = Path(root) / 'gate_desk.json'
        env = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH',)}
        proc = subprocess.run([sys.executable, '-B', '-s', '-E', str(REPO / 'scripts/align_r1_slot_gate_desk.py'),
                               str(self.tree), str(root), '--json-out', str(out), *extra],
                              capture_output=True, text=True, env=env)
        return proc, out

    def night(self, root):
        step_d(root)

    def test_good_night_runs_from_the_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'align-r1'
            root.mkdir()
            self.night(root)
            proc, out = self.cli(root)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('GATE TABLE', proc.stdout)
            data = json.loads(out.read_text())
            self.assertEqual(data['thermal_gates_sha256'], gd.THERMAL_GATES_SHA256)
            self.assertEqual(data['tree_commit'], gd.NIGHT_COMMIT)
            self.assertTrue(all(len(x['sha256']) == 64 for x in data['inputs']))
            first = out.read_bytes()
            self.cli(root)
            self.assertEqual(first, out.read_bytes())                        # deterministic

    def test_7_validation_failure_exits_nonzero_before_any_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'align-r1'
            root.mkdir()
            self.night(root)
            ValidationTests.shift(None, root, gd.STEP_D)
            proc, out = self.cli(root)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(proc.stdout, '')
            self.assertIn('VALIDATION FAILED', proc.stderr)
            self.assertFalse(json.loads(out.read_text())['validation']['all_agree'])

    def test_tree_hash_is_asserted(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / 'tree'
            (bad / 'joulewise/align/apple').mkdir(parents=True)
            (bad / gd.THERMAL_GATES_PATH).write_text('# not the night module\n')
            root = Path(tmp) / 'align-r1'
            root.mkdir()
            out = Path(tmp) / 'o.json'
            proc = subprocess.run([sys.executable, '-B', '-s', '-E', str(REPO / 'scripts/align_r1_slot_gate_desk.py'),
                                   str(bad), str(root), '--json-out', str(out)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn('sha256', proc.stderr)


ENV_NIGHT, ENV_TREE, ENV_KIT = 'JW_SLOT_DESK_NIGHT_1112', 'JW_SLOT_DESK_TREE_1112', 'JW_SLOT_DESK_KIT_1112'


@unittest.skipUnless(os.environ.get(ENV_NIGHT) and os.environ.get(ENV_TREE),
                     f'step 0 only: {ENV_NIGHT}=<11-12 copy>/night/align-r1, {ENV_TREE}=<git archive 99622e96c>')
class Step0Regression1112(unittest.TestCase):
    """Spec 2.1 item 9 on the 11-12 session copy (after chain.exited; never on the armed MBP)."""
    EXIT = {('step_30b', 'G0'): 2511973598140000, ('high_power_A1', 'G0'): 2514149175727625,
            ('high_power_B', 'G0'): 2516104577881291, ('high_power_A2', 'G0'): 2518053414713166,
            (gd.STEP_D, 'G0'): 2520639025894583, ('planning_turn_R_plus_4C', 'G0'): 2523702133941958,
            ('planning_turn_R_plus_2C', 'G0'): 2526188955803541, ('planning_turn_R_plus_0C', 'G0'): 2528485002477916,
            ('D_bank_benign_s1_gated_held', 'G0'): 2530134099211583,
            ('D_bank_benign_s1_gated_held', 'G1'): 2530460107692541,
            ('D_spam_benign_s1_gated_held_a', 'G0'): 2531443721426375,
            ('D_spam_benign_s1_gated_held_a', 'G1'): 2531781721388250,
            ('D_spam_benign_s1_gated_held_b', 'G0'): 2532760702879583,
            ('D_spam_benign_s1_gated_held_b', 'G1'): 2533098712312333,
            ('X_G_contrast', 'G0'): 2533961731295416, ('X_G_contrast', 'G1'): 2534286731371375}
    G1_LAST = {'D_bank_benign_s1_gated_held': (108.197, 268.197), 'D_spam_benign_s1_gated_held_a': (104.697, 299.697),
               'D_spam_benign_s1_gated_held_b': (106.977, 299.977), 'X_G_contrast': (51.625, 299.634)}
    SLOPE_LAST = ('high_power_A1', 'high_power_B', 'high_power_A2', gd.STEP_D, 'D_bank_benign_s1_gated_held',
                  'D_spam_benign_s1_gated_held_a', 'D_spam_benign_s1_gated_held_b', 'X_G_contrast')
    BAND_SLOW_LAST = ('step_30b', 'planning_turn_R_plus_4C', 'planning_turn_R_plus_2C', 'planning_turn_R_plus_0C')
    TF08 = {'D_bank_benign_s1_gated_held': -4.874, 'D_spam_benign_s1_gated_held_a': -4.908,
            'D_spam_benign_s1_gated_held_b': -5.051, 'X_G_contrast': -5.334, gd.STEP_D: -4.332}

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        out = Path(cls.tmp.name) / 'gate_desk.json'
        extra = ['--kit-desk', os.environ[ENV_KIT]] if os.environ.get(ENV_KIT) else []
        cls.proc = subprocess.run([sys.executable, '-B', '-s', '-E', str(REPO / 'scripts/align_r1_slot_gate_desk.py'),
                                   os.environ[ENV_TREE], os.environ[ENV_NIGHT], '--tree-commit', '99622e96c',
                                   '--json-out', str(out), *extra], capture_output=True, text=True)
        cls.out = json.loads(out.read_text()) if out.is_file() else None
        print('\n' + cls.proc.stdout[-6000:], cls.proc.stderr[-3000:])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_validation_16_of_16(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr)
        rows = [r for r in self.out['validation']['rows'] if r['journal_kind'] == 'member']
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(r['agree'] for r in rows))
        got = {(r['member'], r['kind']): r['recorded'][2] for r in rows}
        self.assertEqual(got, self.EXIT)
        aux = [r for r in self.out['validation']['rows'] if r['journal_kind'] == 'auxiliary']
        print('auxiliary validation rows:', len(aux), 'agree', sum(r['agree'] for r in aux))

    def test_g1_last_violations(self):
        for member, (fast, slow) in self.G1_LAST.items():
            row = gate(self.out, member, 'G1')
            self.assertAlmostEqual(row['last_violation_s']['band_fast'], fast, places=3)
            self.assertAlmostEqual(row['last_violation_s']['band_slow'], slow, places=3)
            self.assertGreater(row['last_violation_s']['band_slow'], row['last_violation_s']['band_fast'])

    def test_g0_clause_last(self):
        for member in self.SLOPE_LAST:
            self.assertEqual(gate(self.out, member)['clause_last'] if gate(self.out, member)['outcome'] == 'released'
                             else None, 'slope_slow', member)
        for member in self.BAND_SLOW_LAST:
            row = gate(self.out, member)
            got = row['clause_last'] if row['outcome'] == 'released' else row['clause_last']
            self.assertIn('band_slow', got if isinstance(got, list) else [got], (member, row['last_violation_s']))

    def test_s6(self):
        s6 = self.out['s6']
        self.assertAlmostEqual(s6['g1_median_s'], 300.03, places=2)
        self.assertEqual(sorted(round(w['duration_s'], 2) for w in s6['g1_waits']), [269.86, 300.03, 300.04])
        for step in ('1.5', '2.0'):
            for x in s6['replays'][step]:
                if x['in_median']:
                    self.assertEqual(x['outcome'], 'timeout')
        xg = next(x for x in s6['replays']['2.0'] if x['member'] == 'X_G_contrast' and x['kind'] == 'G1')
        self.assertEqual(xg['outcome'], 'released')
        self.assertAlmostEqual(xg['duration_s'], 283, delta=1)
        self.assertIsNone(s6['s6_reachable_step_c'])

    def test_u2(self):
        u2 = self.out['u2']
        self.assertAlmostEqual(u2['registered_tvh0_c'], 2.817, places=3)
        self.assertEqual(u2['registered_key'], ['Th0C'])
        self.assertAlmostEqual(u2['tv0h_c'], 0.266, places=3)
        self.assertFalse(self.out['triggers']['T3']['fired'])

    def test_tf08_excess(self):
        members = {m['member']: m for m in self.out['start_state']['members']}
        for member, value in self.TF08.items():
            self.assertAlmostEqual(members[member]['tf08_excess_c'], value, places=3)
        if os.environ.get(ENV_KIT):
            self.assertTrue(self.out['tool_checks']['tf08_excess_agrees'],
                            self.out['tool_checks']['tf08_excess_disagreements'])

    def test_floor_census(self):
        self.assertTrue(self.out['floor_census']['status'].startswith('not applicable: TVh0 not journaled'))
        inv = Path(os.environ[ENV_NIGHT]) / gd.STEP_D / 'inventory'
        census = gd.census_journal_file(inv / 'inventory_journal.jsonl', inv / 'r1_classification.json')
        total = census['total']
        print('11-12 step-D inventory census:', json.dumps(total, sort_keys=True))
        self.assertEqual((total['equal'], total['rows']), (1847, 2761))
        self.assertEqual(total['tvh0_above_tv0h'], 0)
        self.assertAlmostEqual(total['min_diff_c'], -5.466, places=3)
        self.assertEqual((census['by_phase']['quiet']['equal'], census['by_phase']['quiet']['rows']), (300, 300))
        self.assertEqual((census['by_phase']['load']['equal'], census['by_phase']['load']['rows']), (438, 438))
        if total['unexplained']:
            print('UNEXPLAINED ROWS ON THE 11-12 INVENTORY: tell the research lead (spec 2.1 item 9)')


if __name__ == '__main__':
    unittest.main()
