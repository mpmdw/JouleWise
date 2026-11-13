"""RL-122 item 3(a) planning-release desk: every classification branch on synthetic journals.

Temperature journals only, built in a temp dir; no host or study data.
"""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import align_v4_kit as kit
from scripts import align_w1_3a_desk as desk

NS = desk.NS
T0 = 1_000 * NS
TARGET, DELTA = 30.0, 1.5          # band edge 31.5; threshold 31.2


def build_member(root, phase, *, outcome='timeout', duration_s=1200, key='TVh0', target=TARGET, os_level=0,
                 pm_state='Nominal', early=40.0, late=30.0, last_s=None, delta=DELTA):
    """One member journal: `early` for the first part of G0, `late` for the last 300 s (or last_s)."""
    last_s = desk.WINDOW_S if last_s is None else last_s
    start, end = T0, T0 + int(duration_s * NS)
    rows = [{'kind': 'session_start', 'values': {'thermal': {'s_fast': 'TV0h', 's_slow': key}}}]
    for second in range(0, int(duration_s) + 1):
        t = start + second * NS
        value = late if t >= end - last_s * NS else early
        rows.append({'kind': 'reading', 'started': {'monotonic_ns': t},
                     'values': {'sensors': {'TV0h': 34.0, key: value}, 'errors': {},
                                'status': {'os_level': os_level, 'pm_state': pm_state}}})
    rows.append({'kind': 'align_thermal_gate', 'values': {'state': 'end', 'gate': {
        'kind': 'G0', 'turn': 0, 'outcome': outcome, 'start_ns': start, 'end_ns': end,
        'duration_s': duration_s, 'reference': {'fast_c': 150.0, 'slow_c': target}}}})
    out = root / phase / 'runs' / 'm' / 'outputs'
    out.mkdir(parents=True)
    (out / desk.JOURNAL).write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    (root / phase / 'runs' / 'm' / 'config.json').write_text(json.dumps({'workload_profile': {
        'prompt_text': json.dumps({'thermal': {'delta_slow_c': delta}})}}))


class Desk3aTests(unittest.TestCase):
    def run_desk(self, phase='planning_turn_R_plus_2C', **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            build_member(Path(tmp), phase, **kwargs)
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
                self.assertEqual((row['heater_key'], row['target_c'], row['band_edge_c']), ('TVh0', 30.0, 31.5))
                self.assertEqual(row[desk.PEAK_FIELD], 31.4)
                self.assertAlmostEqual(row['margin_to_threshold_c'], 0.2)
                self.assertEqual(row['whole_g0_max_c'], 40.0)       # disclosure only
                self.assertEqual(row['os_levels'], [0])
                self.assertEqual(report['kit_record_segments'][phase], {
                    'band_edge_c': 31.5, 'heater_key': 'TVh0', desk.PEAK_FIELD: 31.4,
                    'os_levels': [0], 'pm_states': ['Nominal']})

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

    def test_custody_copy_suffix_is_still_a_planning_turn(self):
        report, row = self.run_desk('planning_turn_R_plus_0C.g0_timeout1', late=31.4)
        self.assertEqual(row['turn_label'], 'planning R+0')
        self.assertEqual(row['classification'], 'planning-release-3a')
        # Only the kit's own segment names go into the record rows.
        self.assertEqual(report['kit_record_segments'], {})

    def test_interval_shorter_than_300s_goes_to_the_lead(self):
        _, row = self.run_desk(duration_s=200, late=31.4)
        self.assertTrue(row['short_interval'])
        self.assertEqual(row['classification'], 'to-research-lead')
        self.assertTrue(any('shorter than 300 s' in r for r in row['reasons']))

    def test_missing_delta_slow_goes_to_the_lead(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_member(Path(tmp), 'planning_turn_R_plus_2C', late=31.4)
            (Path(tmp) / 'planning_turn_R_plus_2C/runs/m/config.json').unlink()
            row = desk.desk(tmp)['g0_intervals'][0]
            self.assertEqual(row['classification'], 'to-research-lead')
            row = desk.desk(tmp, delta_slow_override=DELTA)['g0_intervals'][0]
            self.assertEqual(row['classification'], 'planning-release-3a')
            self.assertEqual(row['delta_slow_source'], '--delta-slow-c')

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

    def test_a_3a_row_passes_the_kit_check_for_the_same_numbers(self):
        # The desk's record rows are exactly what planning_released_segments inspects.
        report, row = self.run_desk('planning_turn_R_plus_2C', late=31.2)
        segment = report['kit_record_segments']['planning_turn_R_plus_2C']
        self.assertFalse(segment[desk.PEAK_FIELD] < segment['band_edge_c'] - kit.PLANNING_RELEASE_EDGE_C)
        self.assertEqual(segment['heater_key'], 'TVh0')


if __name__ == '__main__':
    unittest.main()
