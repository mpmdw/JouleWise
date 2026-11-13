"""RL-122 item 3(a) planning-release desk: every classification branch on synthetic journals.

Temperature journals only, built in a temp dir; no host or study data.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts import align_v4_kit as kit
from scripts import align_w1_3a_desk as desk
from tests.align.test_w1_rl122_kit import planning_slots, release_for

NS = desk.NS
T0 = 1_000 * NS
TARGET, DELTA = 30.0, 1.5          # band edge 31.5; threshold 31.2


def build_member(root, phase, *, outcome='timeout', duration_s=1200, key='TVh0', target=TARGET, os_level=0,
                 pm_state='Nominal', early=40.0, late=30.0, last_s=None, delta=DELTA, step_s=1, run='m',
                 pm_observed=True):
    """One member journal: `early` for the first part of G0, `late` for the last 300 s (or last_s)."""
    last_s = desk.WINDOW_S if last_s is None else last_s
    start, end = T0, T0 + int(duration_s * NS)
    rows = [{'kind': 'session_start', 'values': {'thermal': {'s_fast': 'TV0h', 's_slow': key}}}]
    for second in range(0, int(duration_s) + 1, step_s):
        t = start + second * NS
        value = late if t >= end - last_s * NS else early
        rows.append({'kind': 'reading', 'started': {'monotonic_ns': t},
                     'values': {'sensors': {'TV0h': 34.0, key: value}, 'errors': {},
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
        # Just below the boundary the desk emits nothing, and the kit would refuse the same numbers.
        record = release_for(slots, names, heater_key_max_last_300s_c=31.19)
        with self.assertRaisesRegex(ValueError, 'band edge'):
            kit.planning_released_segments(slots, record)



# ---------------------------------------------------------------- RL-131 item 2.4 (--precool-fast-rule rl131)
R_FAST = 34.907400131225586           # an 11-12-like step-D window reference fast_c
BASE_COMMIT = 'e2696f023464daa339ae1517e33e99a19c74b4ee'   # the tool before the option existed


def build_precool(root, precool_phase, *, fast_last, slow_last=30.5, n=40, invalid_tail_s=0, fast_key='TV0h',
                  slow_key='TVh0'):
    """An idle-until-soak sensors journal: TV0h cooling to fast_last, s_slow ending at slow_last."""
    rows = [{'kind': 'session_start', 'values': {'thermal': {'s_fast': fast_key, 's_slow': slow_key}}}]
    for i in range(n):
        t = T0 + i * NS
        fast = fast_last + 0.01 * (n - 1 - i)
        sensors = {fast_key: fast, slow_key: slow_last + 0.001 * (n - 1 - i)}
        errors = {}
        if i >= n - invalid_tail_s:
            sensors[fast_key] = None
            errors[fast_key] = 'missing'
        rows.append({'kind': 'reading', 'started': {'monotonic_ns': t},
                     'values': {'sensors': sensors, 'errors': errors, 'status': {}}})
    out = root / precool_phase / 'sensors'
    out.mkdir(parents=True)
    (out / desk.JOURNAL).write_text('\n'.join(json.dumps(r) for r in rows) + '\n')


def build_step_d_reference(root, fast_c=R_FAST):
    out = root / desk.STEP_D_PHASE / 'runs' / 'r' / 'outputs'
    out.mkdir(parents=True)
    (out / 'align_window_reference.json').write_text(json.dumps({'fast_c': fast_c, 'slow_c': 35.0}) + '\n')


def load_base_module():
    import importlib.util
    import subprocess
    source = subprocess.run(['git', 'show', f'{BASE_COMMIT}:scripts/align_w1_3a_desk.py'], capture_output=True,
                            check=True, cwd=Path(__file__).resolve().parents[2]).stdout
    tmp = Path(tempfile.mkdtemp()) / 'align_w1_3a_desk_base.py'
    tmp.write_bytes(source)
    spec = importlib.util.spec_from_file_location('align_w1_3a_desk_base', tmp)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PrecoolFastRuleTests(unittest.TestCase):
    def night(self, tmp, phase='planning_turn_R_plus_2C', *, fast_last=R_FAST + 0.99, journal=True, reference=True,
              invalid_tail_s=0, curve_last=30.5, outcome='timeout', late=31.4):
        root = Path(tmp)
        build_member(root, phase, late=late, outcome=outcome, duration_s=1200 if outcome == 'timeout' else 400)
        base = base_phase(phase)
        precool = desk.precool_phase(base)
        write_result(root, {phase: {'g0_outcome': outcome},
                            precool: {'released': True, 'recovery_curve': [[0, 33.0], [100, curve_last]]}})
        if journal:
            build_precool(root, precool, fast_last=fast_last, invalid_tail_s=invalid_tail_s)
        if reference:
            build_step_d_reference(root)
        return root

    def row(self, report, phase='planning_turn_R_plus_2C'):
        return next(r for r in report['g0_intervals'] if r['phase'] == phase)

    def test_default_option_adds_no_fast_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.night(tmp)
            report = desk.desk(tmp)
            text = json.dumps(report)
            self.assertNotIn('fast_', text)
            self.assertNotIn('precool_fast', report['rule'])
            self.assertEqual(json.dumps(report, sort_keys=True), json.dumps(desk.desk(tmp, None, 'none'),
                                                                            sort_keys=True))

    def test_default_option_is_byte_identical_to_the_base_tool(self):
        base = load_base_module()
        for kwargs in ({}, {'outcome': 'released', 'late': 30.5}, {'journal': False}):
            with self.subTest(**kwargs), tempfile.TemporaryDirectory() as tmp:
                self.night(tmp, **kwargs)
                build_member(Path(tmp), 'planning_turn_R_plus_4C', late=31.4)
                build_member(Path(tmp), 'step_30b', outcome='released', duration_s=400, late=30.0)
                for fmt in ('json', 'text'):
                    outs = []
                    for module, extra in ((base, []), (desk, []), (desk, ['--precool-fast-rule', 'none'])):
                        buf = io.StringIO()
                        out = Path(tmp) / f'out-{len(outs)}.json'
                        with contextlib.redirect_stdout(buf):
                            rc = module.main([tmp, '--format', fmt, '--json-out', str(out)] + extra)
                        outs.append((rc, buf.getvalue(), out.read_bytes()))
                    self.assertEqual(outs[0], outs[1])
                    self.assertEqual(outs[0], outs[2])

    def test_edge_classes(self):
        for delta, expected in ((0.99, 'planning-release-3a'), (1.0, 'planning-release-3a'),
                                (1.01, 'to-research-lead')):
            with self.subTest(delta=delta), tempfile.TemporaryDirectory() as tmp:
                self.night(tmp, fast_last=R_FAST + delta)
                report = desk.desk(tmp, None, 'rl131')
                row = self.row(report)
                self.assertEqual(row['classification'], expected, row['reasons'])
                pre = row['precool']
                self.assertEqual(pre['fast_key'], 'TV0h')
                self.assertEqual(pre['r_fast_c'], round(R_FAST, 6))
                self.assertEqual(pre['delta_fast_edge_c'], round(R_FAST + 1.0, 6))
                self.assertEqual(pre['fast_ok'], expected == 'planning-release-3a')
                self.assertEqual(report['rule']['precool_fast']['option'], 'rl131')
                self.assertIn('RL-131 item 2.4', report['rule']['precool_fast']['authority'])
                if expected == 'to-research-lead':
                    self.assertTrue(any(r.startswith('RL-131 2.4: precool TV0h last sample') and
                                        'above R_fast + 1.0' in r for r in row['reasons']), row['reasons'])
                    self.assertNotIn('planning_turn_R_plus_2C', report['kit_record_segments'])
                else:
                    self.assertIn('planning_turn_R_plus_2C', report['kit_record_segments'])
                self.assertIn('RL-131 2.4 precool TV0h', desk.render(report))

    def test_unavailable_inputs_go_to_the_lead(self):
        cases = {'journal absent': {'journal': False}, 'reference absent': {'reference': False},
                 'last TV0h invalid for 6 s': {'invalid_tail_s': 6},
                 'last curve disagrees': {'curve_last': 30.6}}
        for name, kwargs in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                self.night(tmp, **kwargs)
                row = self.row(desk.desk(tmp, None, 'rl131'))
                self.assertEqual(row['classification'], 'to-research-lead')
                self.assertIsNone(row['precool']['fast_ok'])
                self.assertTrue(any(r.startswith('RL-131 2.4: precool TV0h not available (') for r in row['reasons']),
                                row['reasons'])
        with tempfile.TemporaryDirectory() as tmp:            # 5 s of invalid tail is still admissible
            self.night(tmp, invalid_tail_s=5, fast_last=R_FAST + 0.9)    # last valid sample R_f + 0.95
            row = self.row(desk.desk(tmp, None, 'rl131'))
            self.assertEqual(row['classification'], 'planning-release-3a', row['reasons'])
            self.assertEqual(row['precool']['fast_last_age_s'], 5.0)

    def test_absent_precool_layout_is_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.night(tmp, journal=False)
            report = desk.desk(tmp, None, 'rl131')
            layout = report['rule']['precool_fast']['layout']
            self.assertFalse(layout['confirmed'])
            self.assertIn('LAYOUT ASSUMPTION NOT CONFIRMED', layout['note'])
            self.assertIn('LAYOUT ASSUMPTION NOT CONFIRMED', desk.render(report))
            self.assertEqual(report['kit_record_segments'], {})

    def test_precool_journal_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.night(tmp, 'planning_turn_R_plus_4C')
            row = self.row(desk.desk(tmp, None, 'rl131'), 'planning_turn_R_plus_4C')
            self.assertEqual(row['precool']['journal'], 'cooldown_after_D/sensors/align_thermal.jsonl')
            self.assertEqual(row['classification'], 'planning-release-3a', row['reasons'])
        with tempfile.TemporaryDirectory() as tmp:
            self.night(tmp, 'planning_turn_R_plus_2C')
            row = self.row(desk.desk(tmp, None, 'rl131'))
            self.assertEqual(row['precool']['journal'], 'planning_turn_R_plus_2C.precool/sensors/align_thermal.jsonl')
            self.assertEqual(len(row['precool']['journal_sha256']), 64)

    def test_released_planning_g0_keeps_its_class_and_prints_the_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.night(tmp, outcome='released', late=30.5, fast_last=R_FAST + 2.0)
            row = self.row(desk.desk(tmp, None, 'rl131'))
            self.assertEqual(row['classification'], 'released')
            self.assertFalse(row['precool']['fast_ok'])
            self.assertIn('fast_last_c', row['precool'])

    def test_superseded_attempt_is_labelled_and_never_emitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.night(tmp, 'planning_turn_R_plus_2C.g0_timeout1', fast_last=R_FAST + 1.5)
            report = desk.desk(tmp, None, 'rl131')
            row = self.row(report, 'planning_turn_R_plus_2C.g0_timeout1')
            self.assertTrue(row['superseded'])
            self.assertFalse(row['precool']['fast_ok'])
            self.assertEqual(row['classification'], 'to-research-lead')
            self.assertEqual(report['kit_record_segments'], {})
            self.assertIn('(superseded)', desk.render(report))

    def test_mutants_are_killed(self):
        """'>= 0' -> '> 0' on the margin, and dropping the self-check, each change a class above."""
        import importlib.util
        source = Path(desk.__file__).read_text()
        mutants = {
            'margin > 0': ("out['fast_ok'] = out['fast_margin_c'] >= 0", "out['fast_ok'] = out['fast_margin_c'] > 0"),
            'no self-check': ("agrees = (last_slow is not None and finite(curve) and abs(last_slow - curve) <= "
                              "RL131_SELF_CHECK_C)", "agrees = True"),
        }
        for name, (old, new) in mutants.items():
            self.assertEqual(source.count(old), 1, name)
            path = Path(tempfile.mkdtemp()) / 'mutant.py'
            path.write_text(source.replace(old, new))
            spec = importlib.util.spec_from_file_location('mutant_3a', path)
            mutant = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mutant)
            killed = False
            for kwargs, expected in (({'fast_last': R_FAST + 1.0}, 'planning-release-3a'),
                                     ({'curve_last': 30.6}, 'to-research-lead')):
                with tempfile.TemporaryDirectory() as tmp:
                    self.night(tmp, **kwargs)
                    if self.row(mutant.desk(tmp, None, 'rl131'))['classification'] != expected:
                        killed = True
            self.assertTrue(killed, f'mutant survived: {name}')


@unittest.skipUnless(os.environ.get('JW_SLOT_DESK_NIGHT_1112'),
                     'step 0 only: JW_SLOT_DESK_NIGHT_1112=<11-12 copy>/night/align-r1')
class Step0Regression1112(unittest.TestCase):
    """Spec 2.2 item 8, on the 11-12 session copy (run after chain.exited; never on the MBP while armed)."""
    V2_SHA256 = '4b1a66c07ebc18018baeefc6a6d7c3bcbcfb41f8ace80401af8f26cb9f88d758'

    def test_default_output_equals_the_v2_print(self):
        night = os.environ['JW_SLOT_DESK_NIGHT_1112']
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'v2.json'
            with contextlib.redirect_stdout(io.StringIO()):
                desk.main([night, '--format', 'json', '--json-out', str(out)])
            import hashlib
            self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(), self.V2_SHA256)

    def test_rl131_self_check_passes_on_all_three_precools(self):
        report = desk.desk(os.environ['JW_SLOT_DESK_NIGHT_1112'], None, 'rl131')
        rows = {r['phase']: r for r in report['g0_intervals'] if r['planning_turn'] and not r['superseded']}
        expected = {'planning_turn_R_plus_4C': 34.904121, 'planning_turn_R_plus_2C': 35.998047,
                    'planning_turn_R_plus_0C': 36.000591}
        for phase, last in expected.items():
            pre = rows[phase]['precool']
            self.assertTrue(pre['self_check']['agrees'], pre)
            self.assertAlmostEqual(pre['self_check']['journal_last_slow_c'], last, places=6)
            self.assertIsNotNone(pre['fast_last_c'])
        print('\n11-12 rl131 (not evidence, RL-124 item 9):', json.dumps(
            {p: {k: rows[p]['precool'][k] for k in ('fast_last_c', 'fast_last_age_s', 'fast_margin_c', 'fast_ok')}
             | {'class': rows[p]['classification']} for p in expected}, sort_keys=True))


if __name__ == '__main__':
    unittest.main()
