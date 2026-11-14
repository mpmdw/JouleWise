"""RL-122 item 3(a) planning-release desk: every classification branch on synthetic journals.

Temperature journals only, built in a temp dir; no host or study data.
"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts import align_v4_kit as kit
from scripts import align_w1_3a_desk as desk
from tests.align.test_w1_rl122_kit import planning_slots, release_for

NS = desk.NS
T0 = 1_000 * NS
TARGET, DELTA = 30.0, 1.5          # band edge 31.5; threshold 31.2
# RL-152 section 1.1: the heater key is the configured s_slow (TV1h since RL-145), never a literal.
HEATER = kit.planning_heater_key()


def build_member(root, phase, *, outcome='timeout', duration_s=1200, key=HEATER, target=TARGET, os_level=0,
                 pm_state='Nominal', early=40.0, late=30.0, last_s=None, delta=DELTA, step_s=1, run='m',
                 pm_observed=True, fast_offset=None):
    """One member journal: `early` for the first part of G0, `late` for the last 300 s (or last_s)."""
    last_s = desk.WINDOW_S if last_s is None else last_s
    start, end = T0, T0 + int(duration_s * NS)
    rows = [{'kind': 'session_start', 'values': {'thermal': {'s_fast': 'TV0h', 's_slow': key}}}]
    for second in range(0, int(duration_s) + 1, step_s):
        t = start + second * NS
        value = late if t >= end - last_s * NS else early
        # TV0h and TV1h are one thermometer (RL-145 close section 5): the fast key reads the heater's value
        # unless ``fast_offset`` = (seconds before the end, offset) puts an unequal row in.
        fast = value
        if fast_offset is not None and t == end - int(fast_offset[0] * NS) and value is not None:
            fast = value + fast_offset[1]
        sensors = {'TV0h': fast, key: value}
        rows.append({'kind': 'reading', 'started': {'monotonic_ns': t},
                     'values': {'sensors': sensors, 'errors': {},
                                'status': {'os_level': os_level, 'pm_state': pm_state,
                                           'pm_observed_ns': t if pm_observed else None}}})
    rows.append({'kind': 'align_thermal_gate', 'values': {'state': 'end', 'gate': {
        'kind': 'G0', 'turn': 0, 'outcome': outcome, 'start_ns': start, 'end_ns': end,
        'duration_s': duration_s, 'reference': {'fast_c': 150.0, 'slow_c': target}}}})
    out = root / phase / 'runs' / run / 'outputs'
    out.mkdir(parents=True)
    (out / desk.JOURNAL).write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    (root / phase / 'runs' / run / 'config.json').write_text(json.dumps({'workload_profile': {
        'prompt_text': json.dumps({'thermal': {'delta_slow_c': delta}})}}))


def write_result(root, phases):
    """A minimal r1_result.json: {phase name: result dict}."""
    (root / 'r1_result.json').write_text(json.dumps({'phases': [
        {'name': name, 'result': result} for name, result in phases.items()]}))


def base_phase(phase):
    return desk.turn_info(phase)[3]


class Desk3aTests(unittest.TestCase):
    def run_desk(self, phase='planning_turn_R_plus_2C', precool=True, **kwargs):
        """precool True/False: r1_result.json carries the preceding idle-until-soak; None: no r1_result.json."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_member(root, phase, **kwargs)
            if precool is not None:
                phases = {phase: {'g0_outcome': kwargs.get('outcome', 'timeout')}}
                if desk.turn_info(phase)[1]:
                    phases[desk.precool_phase(base_phase(phase))] = {
                        'released': precool, 'recovery_curve': [[0, 33.0], [100, 30.5]]}
                write_result(root, phases)
            report = desk.desk(tmp)
        self.assertEqual(len(report['g0_intervals']), 1)
        return report, report['g0_intervals'][0]

    def test_released_g0_needs_no_ruling(self):
        _, row = self.run_desk(outcome='released', duration_s=400, late=30.5)
        self.assertEqual(row['classification'], 'released')

    def test_planning_timeout_at_the_band_edge_is_3a(self):
        for phase in ('planning_turn_R_plus_0C', 'planning_turn_R_plus_2C', 'planning_turn_R_plus_4C'):
            with self.subTest(phase=phase):
                report, row = self.run_desk(phase, late=31.4)
                self.assertEqual(row['classification'], 'planning-release-3a', row['reasons'])
                self.assertEqual((row['heater_key'], row['target_c'], row['band_edge_c']), (HEATER, 30.0, 31.5))
                self.assertEqual(row[desk.PEAK_FIELD], 31.4)
                self.assertAlmostEqual(row['margin_to_threshold_c'], 0.2)
                self.assertEqual(row['whole_g0_max_c'], 40.0)       # disclosure only
                self.assertEqual(row['os_levels'], [0])
                self.assertEqual(report['kit_record_segments'][phase], {
                    'band_edge_c': 31.5, 'heater_key': HEATER, desk.PEAK_FIELD: 31.4,
                    'os_levels': [0], 'pm_states': ['Nominal']})

    def test_unequal_fast_and_slow_rows_in_the_last_300_s_are_counted(self):
        # RL-152 section 1.1 (RL-149 section 1.7): print only; the class does not read it.
        _, row = self.run_desk(late=31.4)
        self.assertEqual(row['fast_slow_unequal_last_300s'], 0)
        _, row = self.run_desk(late=31.4, fast_offset=(120, 0.25))
        self.assertEqual(row['fast_slow_unequal_last_300s'], 1)
        self.assertEqual(row['classification'], 'planning-release-3a')
        _, row = self.run_desk(late=31.4, fast_offset=(400, 0.25))      # before the last 300 s: not counted
        self.assertEqual(row['fast_slow_unequal_last_300s'], 0)

    def test_crossing_the_edge_is_3a(self):
        _, row = self.run_desk(late=32.0)
        self.assertEqual(row['classification'], 'planning-release-3a')

    def test_boundary_exactly_at_minus_0_3(self):
        # band edge 31.5 - 0.3 = 31.2: at the boundary counts, 0.01 C below does not.
        _, at = self.run_desk(late=31.2)
        self.assertEqual(at['classification'], 'planning-release-3a', at['reasons'])
        self.assertEqual(at['margin_to_threshold_c'], 0.0)
        _, below = self.run_desk(late=31.19)
        self.assertEqual(below['classification'], 'to-research-lead')
        self.assertLess(below['margin_to_threshold_c'], 0)

    def test_key_well_inside_the_band_goes_to_the_lead(self):
        # The whole-G0 peak (40 C, preheat overshoot) is not the pattern.
        report, row = self.run_desk(late=29.5)
        self.assertEqual(row['classification'], 'to-research-lead')
        self.assertTrue(any('not at the band edge' in r for r in row['reasons']), row['reasons'])
        self.assertEqual(row['whole_g0_max_c'], 40.0)
        self.assertEqual(report['kit_record_segments'], {})

    def test_last_300s_not_whole_g0(self):
        # At the edge only before the last 300 s: the window excludes it.
        _, row = self.run_desk(early=31.5, late=29.0)
        self.assertEqual(row['classification'], 'to-research-lead')
        self.assertEqual(row[desk.PEAK_FIELD], 29.0)

    def test_os_level_1_goes_to_the_lead(self):
        _, row = self.run_desk(late=31.4, os_level=1)
        self.assertEqual(row['classification'], 'to-research-lead')
        self.assertEqual(row['os_level_max'], 1)
        self.assertTrue(any('OS level above 0' in r for r in row['reasons']))

    def test_non_nominal_goes_to_the_lead(self):
        _, row = self.run_desk(late=31.4, pm_state='Moderate')
        self.assertEqual(row['classification'], 'to-research-lead')
        self.assertFalse(row['nominal_throughout'])
        self.assertTrue(any('Nominal' in r for r in row['reasons']))

    def test_unobserved_state_is_not_nominal(self):
        _, row = self.run_desk(late=31.4, pm_state=None)
        self.assertEqual(row['classification'], 'to-research-lead')

    def test_timeout_outside_the_planning_turns_goes_to_the_lead(self):
        for phase in ('step_D_prefill_10k_decode_4096', 'high_power_A1', 'planning_turn_R_plus_0C.precool',
                      'planning_turn_R_plus_6C'):
            with self.subTest(phase=phase):
                _, row = self.run_desk(phase, late=31.4)
                self.assertEqual(row['classification'], 'to-research-lead')
                self.assertTrue(any('outside the planning turns' in r for r in row['reasons']))

    def test_superseded_attempts_are_labelled_and_never_emitted(self):
        for phase in ('planning_turn_R_plus_0C.g0_timeout1', 'planning_turn_R_plus_0C.rejected1'):
            with self.subTest(phase=phase):
                report, row = self.run_desk(phase, late=31.4)
                self.assertEqual(row['turn_label'], 'planning R+0')
                self.assertTrue(row['superseded'])
                self.assertEqual(row['classification'], 'planning-release-3a')   # same rule as its turn
                self.assertEqual(report['kit_record_segments'], {})
                self.assertIn('(superseded)', desk.render(report))

    def test_interval_shorter_than_300s_goes_to_the_lead(self):
        _, row = self.run_desk(duration_s=200, late=31.4)
        self.assertTrue(row['short_interval'])
        self.assertEqual(row['classification'], 'to-research-lead')
        self.assertTrue(any('shorter than 300 s' in r for r in row['reasons']))

    def test_override_is_display_only_and_never_releases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_member(root, 'planning_turn_R_plus_2C', late=31.4)
            write_result(root, {'planning_turn_R_plus_2C': {'g0_outcome': 'timeout'},
                                'planning_turn_R_plus_2C.precool': {'released': True}})
            (root / 'planning_turn_R_plus_2C/runs/m/config.json').unlink()
            report = desk.desk(tmp)
            self.assertEqual(report['g0_intervals'][0]['classification'], 'to-research-lead')
            self.assertIsNone(report['g0_intervals'][0]['band_edge_c'])
            report = desk.desk(tmp, delta_slow_override=DELTA)
            row = report['g0_intervals'][0]
            self.assertEqual(row['delta_slow_source'], '--delta-slow-c')
            self.assertEqual(row['band_edge_c'], 31.5)                        # shown
            self.assertEqual(row['classification'], 'to-research-lead')
            self.assertTrue(any('override' in r for r in row['reasons']))
            self.assertEqual(report['kit_record_segments'], {})

    def test_precool_must_have_released(self):
        report, row = self.run_desk(late=31.4, precool=True)
        self.assertEqual(row['classification'], 'planning-release-3a')
        self.assertEqual(row['precool'], {'phase': 'planning_turn_R_plus_2C.precool', 'released': True,
                                          'last_curve_c': 30.5})
        report, row = self.run_desk(late=31.4, precool=False)
        self.assertEqual(row['classification'], 'to-research-lead')
        self.assertFalse(row['precool']['released'])
        self.assertTrue(any('precool' in r for r in row['reasons']))
        self.assertEqual(report['kit_record_segments'], {})
        report, row = self.run_desk(late=31.4, precool=None)               # no r1_result.json
        self.assertEqual(row['classification'], 'to-research-lead')
        self.assertIsNone(row['precool']['released'])
        self.assertIn('not reconciled', report['reconciliation']['status'])
        self.assertIsNone(report['kit_record_segments_note'])

    def test_precool_phase_names_follow_the_phase_table(self):
        from joulewise.align.apple import r1_phase_table
        names = [n for n, *_ in r1_phase_table.phase_plan()]
        for offset in desk.PLANNING_OFFSETS:
            turn = f'planning_turn_R_plus_{offset}C'
            self.assertEqual(names[names.index(turn) - 1], desk.precool_phase(turn))

    def test_cooldown_after_d_is_the_r_plus_4_precool(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_member(root, 'planning_turn_R_plus_4C', late=31.4)
            write_result(root, {'planning_turn_R_plus_4C': {'g0_outcome': 'timeout'},
                                'cooldown_after_D': {'released': True, 'recovery_curve': [[0, 36.0]]},
                                'planning_turn_R_plus_4C.precool': {'released': False}})
            row = desk.desk(tmp)['g0_intervals'][0]
            self.assertEqual(row['classification'], 'planning-release-3a')
            self.assertEqual(row['precool']['phase'], 'cooldown_after_D')

    def test_unobserved_and_deadman_exits_go_to_the_lead(self):
        for outcome in ('unobserved', 'deadman'):
            with self.subTest(outcome=outcome):
                _, row = self.run_desk(late=31.4, outcome=outcome)
                self.assertEqual(row['classification'], 'to-research-lead')
                self.assertTrue(any('not a timeout' in r for r in row['reasons']))

    def test_fewer_than_270_samples_in_the_last_300s_goes_to_the_lead(self):
        _, row = self.run_desk(late=31.4, step_s=2)            # 151 samples
        self.assertEqual(row['samples_last_300s'], 151)
        self.assertEqual(row['classification'], 'to-research-lead')
        self.assertTrue(any('valid heater-key sample' in r for r in row['reasons']))

    def test_reconciliation_counts_and_mismatches(self):
        report, _ = self.run_desk(late=31.4)
        self.assertEqual(report['reconciliation']['status'],
                         'reconciled: 1 r1_result phase(s) with g0_outcome, 1 desk row(s)')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_member(root, 'planning_turn_R_plus_2C', late=31.4)
            write_result(root, {'planning_turn_R_plus_2C': {'g0_outcome': 'released'},
                                'planning_turn_R_plus_2C.precool': {'released': True},
                                'step_30b': {'g0_outcome': 'released'}})
            report = desk.desk(tmp)
            self.assertEqual(len(report['reconciliation']['mismatches']), 2)   # outcome + missing step_30b
            self.assertEqual(report['kit_record_segments'], {})
            self.assertEqual(report['kit_record_segments_note'],
                             'kit_record_segments withheld: reconciliation mismatch')
            self.assertIn('kit_record_segments withheld: reconciliation mismatch', desk.render(report))
            out = root / 'out.json'
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(desk.main([tmp, '--format', 'json', '--json-out', str(out)]), 2)
            self.assertTrue(out.is_file())

    def test_duplicate_rows_for_one_segment_release_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_member(root, 'planning_turn_R_plus_2C', late=31.4, run='a')
            build_member(root, 'planning_turn_R_plus_2C', late=31.4, run='b')
            write_result(root, {'planning_turn_R_plus_2C.precool': {'released': True}})
            report = desk.desk(tmp)
            rows = report['g0_intervals']
            self.assertEqual([r['classification'] for r in rows], ['to-research-lead'] * 2)
            self.assertTrue(all(any('G0 rows under one segment' in x for x in r['reasons']) for r in rows))
            self.assertEqual(report['kit_record_segments'], {})

    def test_disclosure_columns_do_not_change_the_class(self):
        report, row = self.run_desk(late=31.4)
        self.assertEqual(row['last_300s_median_c'], 31.4)
        self.assertEqual(row['last_300s_count_ge_threshold'], 301)
        self.assertEqual(row['stale_power_state_samples'], 0)
        self.assertIsNone(row['exit_slope_c_per_min'])
        self.assertEqual(len(row['journal_sha256']), 64)
        _, stale = self.run_desk(late=31.4, pm_observed=False)
        self.assertEqual(stale['stale_power_state_samples'], stale['samples'])
        self.assertEqual(stale['classification'], 'planning-release-3a')

    def test_output_is_deterministic_and_has_no_wall_clock(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_member(Path(tmp), 'planning_turn_R_plus_4C', late=31.4)
            first = json.dumps(desk.desk(tmp), sort_keys=True)
            self.assertEqual(first, json.dumps(desk.desk(tmp), sort_keys=True))
            self.assertEqual(desk.render(desk.desk(tmp)), desk.render(desk.desk(tmp)))

    def test_constants_match_the_kit(self):
        self.assertEqual((desk.PEAK_FIELD, desk.WINDOW_S, desk.EDGE_C),
                         (kit.PLANNING_RELEASE_PEAK_FIELD, kit.PLANNING_RELEASE_WINDOW_S,
                          kit.PLANNING_RELEASE_EDGE_C))
        self.assertEqual(sorted(f'planning_turn_R_plus_{n}C' for n in desk.PLANNING_OFFSETS),
                         sorted(kit.PLANNING_SEGMENTS))

    def test_the_emitted_rows_pass_the_kits_own_check(self):
        names = ['planning_turn_R_plus_2C', 'planning_turn_R_plus_4C']
        inputs, slots = planning_slots(names)
        for late in (31.2, 31.4, 32.0):                                    # boundary, edge, crossing
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                phases = {}
                for name in names:
                    build_member(root, name, late=late)
                    phases[name] = {'g0_outcome': 'timeout'}
                    phases[desk.precool_phase(name)] = {'released': True}
                write_result(root, phases)
                report = desk.desk(tmp)
            with self.subTest(late=late):
                self.assertEqual(sorted(report['kit_record_segments']), names)
                record = release_for(slots, names)
                record['segments'] = report['kit_record_segments']
                self.assertEqual(kit.planning_released_segments(slots, record), set(names))
                kit.require_ready(inputs, slots, planning_release=record)
        # RL-152 section 1.1: a record naming the RL-122 key TVh0 (no role since RL-145) is refused by the
        # kit, which accepts exactly the configured s_slow.
        self.assertNotEqual(HEATER, 'TVh0')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            phases = {}
            for name in names:
                build_member(root, name, late=31.4, key='TVh0')
                phases[name] = {'g0_outcome': 'timeout'}
                phases[desk.precool_phase(name)] = {'released': True}
            write_result(root, phases)
            stale = desk.desk(tmp)['kit_record_segments']
        self.assertEqual({row['heater_key'] for row in stale.values()}, {'TVh0'})
        record = release_for(slots, names)
        record['segments'] = stale
        with self.assertRaisesRegex(ValueError, f"heater key 'TVh0' is not '{HEATER}'.*research lead rules"):
            kit.planning_released_segments(slots, record)
        # Just below the boundary the desk emits nothing, and the kit would refuse the same numbers.
        record = release_for(slots, names, heater_key_max_last_300s_c=31.19)
        with self.assertRaisesRegex(ValueError, 'band edge'):
            kit.planning_released_segments(slots, record)


if __name__ == '__main__':
    unittest.main()
