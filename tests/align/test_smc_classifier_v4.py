"""WP14(a) synthetic regression tests for the single v4 classifier."""
import math
import random
import unittest
from unittest import mock

from joulewise.align.apple import thermal
from joulewise.align.apple.smc_enumeration import rank, select_keys
from tests.align.test_smc_selection import capture


def jittered_capture():
    """Synthetic full-length R0 step; values follow the actual read starts."""
    rng = random.Random(195)
    phases = [("idle", 0, 300), ("load", 300, 1200), ("recovery", 1200, 1800)]
    # Heating/cooling constants in seconds, rise in degC: die t63 ~3 s;
    # heatsink full-rise t63 ~50 s and cooling tau ~120 s, with 8 >= 3.0 degC (three 1 degC bands).
    specs = {"TDIE": (3, 3, 18), "THEA": (50, 120, 8)}
    # 403 channels match the real census: two responders plus 401 quiet
    # non-stale channels with no load response. All reads share the jitter.
    specs.update({f'T{i:03X}': (20, 20, 0) for i in range(401)})
    samples = []
    for phase, begin, end in phases:
        for tick in range(begin, end):
            # Inclusive measured-shape bounds: 0-150 ms late, 50-400 ms read.
            started = tick * thermal.NS + rng.randint(0, 150_000_000)
            finished = started + rng.randint(50_000_000, 400_000_000)
            t = started / thermal.NS
            values = {}
            for key, (heat, cool, rise) in specs.items():
                response = (0 if phase == "idle" else
                            1 - math.exp(-(t - begin) / heat) if phase == "load" else
                            (1 - math.exp(-900 / heat)) * math.exp(-(t - begin) / cool))
                # Non-stale idle noise stays small relative to both rises.
                values[key] = 30 + rise * response + .1 * math.sin(t * 1.7)
            samples.append({"phase": phase, "elapsed_s": t,
                            "started": {"monotonic_ns": started},
                            "finished": {"monotonic_ns": finished},
                            "values": {"sensors": values, "errors": {}}})
    return {"started": {"monotonic_ns": 0}, "finished": {"monotonic_ns": 1800 * thermal.NS},
            "inventory": {"keys": [{"key": key, "unit": "degC", "data_type": "flt "}
                                     for key in specs]},
            "phases": [{"phase": phase, "start_s": begin, "end_s": end}
                       for phase, begin, end in phases], "samples": samples}


def source_spread_capture():
    """Two-pole die cooling reproduces the cold3 first-read sensitivity."""
    # Cold3 rises: Tf18 45.68, Tf2B 45.63; a lower-gain sibling spans
    # the measured 0.46 C co-located spread. Ts0h's rise is 38.5 C.
    data = capture({'Tf18': (3, 30.8, 45.68, .02),
                    'Tf2B': (3, 30.3, 45.63, .02),
                    'Tf1B': (3, 30.5, 45.22, .02),
                    'Ts0h': (3, 27.6, 38.5, .02),
                    'TVH3': (5, 33.3, 64.1, .02),
                    'TaLP': (60, 86.2, 20.5, .02)})
    for phase in data['phases']:
        phase['deadline_s'] = phase['end_s']
    for sample in data['samples']:
        if sample['phase'] == 'recovery':
            t = sample['elapsed_s'] - 900  # 300 idle +600 load in capture().
            for key, slow, rise in [('Tf18', 30.8, 45.68), ('Tf2B', 30.3, 45.63),
                                    ('Tf1B', 30.5, 45.22)]:
                # 18% with 0.7 s decay gives the measured ~6 C first-second
                # drop; the remaining 82% cools near 31 s. Stable crossing
                # is slow*(1+ln(.82)) ~=24.2-24.7 s, within a 1 Hz tie.
                sample['values']['sensors'][key] = 30 + rise*(
                    .18*math.exp(-t/.7) + .82*math.exp(-t/slow))
    return data


class SmcClassifierV4Tests(unittest.TestCase):
    def test_erratum4_reference_survives_delay_overrun_and_reference_holes(self):
        # Required cold3 perturbations: one-cell recovery delay, +1.3 s
        # exit latency, first reference read lost, and two adjacent load
        # cells 236-237 lost. All are below the 1% per-phase error bar.
        for case in ('recovery_delay', 'overrun_load', 'miss_first', 'hole2'):
            data = source_spread_capture()
            if case == 'recovery_delay':
                data['phases'][2]['start_s'] += 1.0  # One 1 Hz cell.
                data['samples'] = [s for s in data['samples']
                                   if s['phase'] != 'recovery' or s['elapsed_s'] >= 901]
            elif case == 'overrun_load':
                data['phases'][1]['end_s'] += 1.3  # Cold3 load exit latency.
                data['phases'][2]['start_s'] += 1.3
                for s in data['samples']:
                    if s['phase'] == 'recovery' and s['elapsed_s'] < 901.3:
                        s['phase'] = 'load'
            else:
                phase, indices = ('recovery', (0,)) if case == 'miss_first' else ('load', (236, 237))
                samples = [s for s in data['samples'] if s['phase'] == phase]
                for i in indices:
                    samples[i]['values']['errors']['Tf2B'] = 'cold3 missed read'
            for stage in ('r0', 'r1'):
                with self.subTest(case=case, stage=stage):
                    result = rank(data, stage=stage)
                    self.assertEqual(result['selection'], {'s_fast': 'Tf18', 's_slow': 'TaLP'})
                    self.assertEqual([r['key'] for r in result['ranking']
                                      if r['heat_ordering_excluded']], ['TVH3'])
                    self.assertEqual(result['heat_ordering_reference'], 'Tf18')
                    if case == 'hole2':
                        row = next(r for r in result['ranking'] if r['key'] == 'Tf2B')
                        self.assertIn('D6', row['reason'])

    def test_reference_stable_crossing_uses_load_rise_and_actual_load_end(self):
        data = source_spread_capture()
        result = rank(data)
        row = next(r for r in result['ranking'] if r['key'] == 'Tf18')
        # 30.8*(1+ln(.82)) is the slow-pole crossing (the 0.7 s pole
        # has decayed); allow one sampling period for interpolation/noise.
        self.assertAlmostEqual(row['reference_cooling_s'], 30.8*(1+math.log(.82)), delta=1)
        data['phases'][1]['end_s'] += 1.3
        shifted = next(r for r in rank(data)['ranking'] if r['key'] == 'Tf18')
        self.assertAlmostEqual(shifted['reference_cooling_s'], row['reference_cooling_s']-1.3)
        self.assertEqual(shifted['tau_s'], row['tau_s'])  # D4/D5 class tau stays unchanged.

    def test_deadline_grid_does_not_extend_an_early_phase_end(self):
        data = source_spread_capture()
        # Fable overrun_load:1.6 moves recovery admission but leaves its end
        # unchanged, shortening it by 1.6 s. That is a duration flag, not
        # two imaginary reader cells after the actual phase has ended.
        data['phases'][2]['deadline_s'] += 1.6
        result = rank(data)
        self.assertEqual(result['selection'], {'s_fast': 'Tf18', 's_slow': 'TaLP'})
        for row in result['ranking']:
            self.assertEqual(row['phase_max_empty_cells']['recovery'], 0)

    def test_noisy_shortest_tau_cannot_anchor_heat_ordering(self):
        data = capture({'Tf18': (3, 24.7, 45.7, .06),
                        'Tp0M': (3, 5, 30, 1), 'TaLP': (60, 86.2, 20.5, .02)})
        for stage in ('r0', 'r1'):
            with self.subTest(stage=stage):
                result = rank(data, stage=stage)
                rows = {r['key']: r for r in result['ranking']}
                flicker = rows['Tp0M']
                # Passes D1(a)-(c) and resolves, but fails D4's noise bar.
                # Its smaller rise would incorrectly exclude Tf18 as a source.
                self.assertTrue(flicker['resolving'])
                self.assertFalse(flicker['below_ambient'])
                self.assertFalse(flicker['above_junction'])
                self.assertFalse(flicker['clamped'])
                self.assertLessEqual(flicker['max_one_second_change'], flicker['observed_rise']/2)
                self.assertGreater(flicker['noise'], 1/3)
                self.assertLess(flicker['tau_s'], rows['Tf18']['tau_s'])
                self.assertLess(flicker['observed_rise'] + 3*flicker['noise_floor'],
                                rows['Tf18']['observed_rise'])
                self.assertEqual(result['heat_ordering_reference'], 'Tf18')
                self.assertFalse(rows['Tf18']['heat_ordering_excluded'])
                self.assertEqual(result['selection'], {'s_fast': 'Tf18', 's_slow': 'TaLP'})

    def test_clamped_shortest_tau_cannot_anchor_heat_ordering(self):
        data = capture({'TDIE': (3, 25, 18, .02), 'TCLP': (3, 5, 12, .02),
                        'THEA': (60, 90, 8, .02)})
        for sample in data['samples'][:240]:
            sample['values']['sensors']['TCLP'] = 30
        result = rank(data)
        rows = {r['key']: r for r in result['ranking']}
        self.assertTrue(rows['TCLP']['clamped'])
        self.assertTrue(rows['TCLP']['resolving'])
        self.assertLess(rows['TCLP']['tau_s'], rows['TDIE']['tau_s'])
        self.assertEqual(result['heat_ordering_reference'], 'TDIE')
        self.assertEqual(result['selection'], {'s_fast': 'TDIE', 's_slow': 'THEA'})

    def test_slow_role_alone_has_no_heat_ordering_reference(self):
        result = rank(capture({'THEA': (60, 90, 8, .02)}))
        self.assertTrue(result['ranking'][0]['resolving'])
        self.assertGreater(result['ranking'][0]['tau_s'], 60)
        self.assertIsNone(result['heat_ordering_reference'])
        self.assertEqual(result['selection'], {'s_fast': None, 's_slow': 'THEA'})

    def test_fable_f1_lighter_step_rejects_derived_heat_ordering(self):
        # Fable followups.py: scale each key about its own idle baseline by
        # 0.85 (a 15% lighter step). Replay rises are Tf18=45.7, TVH3=64.1;
        # cooling taus 24.7/33.3 s put the physical source first.
        data = capture({'Tf18': (3, 24.7, 45.7, .06),
                        'TVH3': (5, 33.3, 64.1, .06), 'TaLP': (60, 86.2, 20.5, .02)})
        for sample in data['samples']:
            for key, value in sample['values']['sensors'].items():
                sample['values']['sensors'][key] = 30 + .85*(value-30)
        for stage in ('r0', 'r1'):
            result = rank(data, stage=stage)
            self.assertEqual(result['selection'], {'s_fast': 'Tf18', 's_slow': 'TaLP'})
            derived = next(r for r in result['ranking'] if r['key'] == 'TVH3')
            self.assertFalse(derived['above_junction'])
            self.assertIn('D1(d)', derived['reason'])
            self.assertFalse(derived['eligible'])

    def test_heat_ordering_uses_band_margin_and_lexical_rise_ties(self):
        data = capture({'TSRC': (3, 25, 18, .02), 'TCMP': (5, 35, 18, .02)})
        original = rank(data)
        source = next(r for r in original['ranking'] if r['key'] == 'TSRC')
        compare = next(r for r in original['ranking'] if r['key'] == 'TCMP')
        # Erratum 4: 1 C is the gate band floor, resolving sensor gain/offset
        # spread rather than one sensor's residual noise.
        margin = 1.0
        for extra, excluded in ((margin/2, False), (2*margin, True)):
            import copy
            variant = copy.deepcopy(data)
            offset = source['observed_rise']-compare['observed_rise']+extra
            for sample in variant['samples']:
                if sample['phase'] == 'load' and sample['elapsed_s'] >= 840:
                    # Final 10% of the 600 s load is the full-rise statistic.
                    sample['values']['sensors']['TCMP'] += offset
            result = rank(variant)
            row = next(r for r in result['ranking'] if r['key'] == 'TCMP')
            self.assertEqual(row['heat_ordering_excluded'], excluded)
        # Exact copies have equal tau, so lexical order picks the reference;
        # reporting aliases does not remove a selectable copy.
        data = capture({'TB00': (3, 25, 18, .02), 'TA00': (3, 25, 18, .02),
                        'THEA': (60, 90, 8, .02)})
        result = rank(data)
        self.assertEqual(result['heat_ordering_reference'], 'TA00')
        self.assertEqual(result['selected_key_aliases'], {'TA00': ['TB00'], 'THEA': []})
        self.assertTrue(next(r for r in result['ranking'] if r['key'] == 'TB00')['eligible'])

    def test_two_empty_cells_drop_the_key_and_next_key_supplies_role(self):
        data = capture({'Tf18': (3, 25, 18, .02), 'Tf2B': (3, 25, 17, .02),
                        'TaLP': (60, 90, 8, .02)})
        # Two missed cells /600 load cells =99.67% and <1% errors; only
        # the new consecutive-empty-cell bar can reject Tf18 here.
        for sample in data['samples'][700:702]:
            sample['values']['errors']['Tf18'] = 'miss'
        for stage in ('r0', 'r1'):
            result = rank(data, stage=stage)
            self.assertEqual(result['selection'], {'s_fast': 'Tf2B', 's_slow': 'TaLP'})
            row = next(r for r in result['ranking'] if r['key'] == 'Tf18')
            self.assertEqual(row['phase_max_empty_cells']['load'], 2)
            self.assertIn('D6', row['reason'])

    def test_phase_edge_holes_are_not_hidden_by_first_success(self):
        for start in (900, 1498):
            data = capture({'TDIE': (3, 25, 18, .02), 'THEA': (60, 90, 8, .02)})
            # Two adjacent missing recovery cells, at either edge; 598/600
            # exceeds 99%, but the U1(c) cell-run bar still excludes the key.
            for sample in data['samples'][start:start+2]:
                sample['values']['errors']['TDIE'] = 'miss'
            result = rank(data)
            self.assertIsNone(result['s_fast'])
            row = next(r for r in result['ranking'] if r['key'] == 'TDIE')
            self.assertEqual(row['phase_max_empty_cells']['recovery'], 2)

    def test_nonpositive_rise_has_no_d1b_reason(self):
        data = capture({'TDIP': (20, 25, -1, .02)})
        row = rank(data)['ranking'][0]
        self.assertLess(row['observed_rise'], 0)
        self.assertNotIn('D1(b)', row['reason'])

    def test_derived_137_degree_key_is_record_only_in_both_stages(self):
        data = capture({'TDIE': (3, 25, 18, .05), 'THEA': (60, 90, 8, .02),
                        'TDRV': (10, 25, 107, .02)})
        # A firmware-derived channel rises from 30 to 137 degC (107 degC
        # excursion), as TVH3 did. Its rise would beat the physical fast key;
        # its 25 s tau also fits 25*ln(107) < the 300 s band-return cap.
        for row in data['samples']:
            row['values']['sensors']['TDRV'] = min(137.0, row['values']['sensors']['TDRV'])
        self.assertEqual(max(row['values']['sensors']['TDRV'] for row in data['samples']), 137.0)
        for stage in ('r0', 'r1'):
            with self.subTest(stage=stage):
                result = rank(data, stage=stage)
                derived = next(r for r in result['ranking'] if r['key'] == 'TDRV')
                self.assertTrue(derived['above_junction'])
                self.assertFalse(derived['eligible'])
                self.assertEqual(derived['class'], 'record-only')
                self.assertIn('D1(c)', derived['reason'])
                self.assertIn('D1(d)', derived['reason'])
                self.assertEqual(result['selection'], {'s_fast': 'TDIE', 's_slow': 'THEA'})

    def test_junction_ceiling_is_strict_and_ignores_failed_readings(self):
        data = capture({'TDRV': (10, 25, 95, .02)})
        # 30 degC baseline +95 degC excursion reaches exactly the 125 degC
        # ceiling. D1(c) rejects only values above it, not equality.
        for row in data['samples']:
            row['values']['sensors']['TDRV'] = min(125.0, row['values']['sensors']['TDRV'])
        result = rank(data)
        self.assertEqual(result['s_fast'], 'TDRV')
        self.assertFalse(result['ranking'][0]['above_junction'])
        # One failed load read out of 600 is <1%; a reported error cannot
        # make its synthetic 137 degC payload a valid D1(c) reading.
        data['samples'][800]['values']['sensors']['TDRV'] = 137.0
        data['samples'][800]['values']['errors']['TDRV'] = 'failed read'
        result = rank(data)
        self.assertEqual(result['s_fast'], 'TDRV')
        self.assertFalse(result['ranking'][0]['above_junction'])

    def test_power_gated_negative_zero_and_positive_placeholders_cannot_win(self):
        for placeholder in (-2.75, 0.0, 20.0):
            data = capture({'TDIE': (3, 25, 18, .05), 'THEA': (60, 90, 8, .02),
                            'TGAT': (2, 2, 60, .01)})
            for row in data['samples']:
                if row['phase'] != 'load':
                    # A parked key wakes for one of every 20 idle/recovery
                    # readings: 95% placeholders, matching the real Tg pattern.
                    # Positive sentinel: 65-20 =45 > half the 60 degC
                    # load rise, so D1(b) catches it independently of D1(a).
                    row['values']['sensors']['TGAT'] = (65 + .01*math.sin(row['elapsed_s'])
                        if int(row['elapsed_s']) % 20 == 0 else placeholder)
                else:
                    row['values']['sensors']['TGAT'] = 80 + .01*math.sin(row['elapsed_s'])
            result = rank(data)
            gated = next(r for r in result['ranking'] if r['key'] == 'TGAT')
            with self.subTest(placeholder=placeholder):
                self.assertFalse(gated['eligible'])
                self.assertIn('D1(a)' if placeholder < 10 else 'D1(b)', gated['reason'])
                self.assertEqual(result['s_fast'], 'TDIE')

    def test_clamp_keeps_class_but_is_excluded_from_picks(self):
        data = capture({'TDIE': (3, 25, 18, .05), 'THEA': (60, 90, 8, .02),
                        'TCLM': (3, 25, 18, .02)})
        for row in data['samples']:
            if row['phase'] == 'idle':
                t = row['elapsed_s']
                row['values']['sensors']['TCLM'] = 30 if int(t) % 2 == 0 else 30+.02*abs(math.sin(t))
        result = rank(data)
        clamp = next(r for r in result['ranking'] if r['key'] == 'TCLM')
        # Half the 300 idle samples occupy the exact floor, above the
        # derived 40% bar; the other half provide >=10 distinct values.
        # Match the physical source's rise so D1(d) does not also exclude it.
        self.assertGreaterEqual(clamp['idle_mode_fraction'], .4)
        self.assertTrue(clamp['clamped'])
        self.assertTrue(clamp['eligible'])
        self.assertEqual(clamp['class'], 'die')
        self.assertEqual(result['s_fast'], 'TDIE')

    def test_unsettled_baseline_uses_last_minute_and_residual_noise(self):
        data = capture({'TDIE': (3, 25, 18, .02), 'THEA': (60, 90, 8, .02)})
        for row in data['samples']:
            if row['phase'] == 'idle':
                for key in row['values']['sensors']:
                    row['values']['sensors'][key] += (300-row['elapsed_s'])/60
        result = rank(data)
        for r in result['ranking']:
            self.assertTrue(r['baseline_unsettled'])
            # Added drift is -1 degC/min; 0.02 degC sine perturbs the
            # 60-point OLS slope by <0.01 degC/min.
            self.assertAlmostEqual(r['baseline_slope_c_min'], -1, delta=.01)
            # Detrending leaves at most the 0.02 degC sine amplitude.
            self.assertLess(r['noise'], .02)
            # Last-minute median samples t=240..299: drift median=30.5/60.
            self.assertAlmostEqual(r['baseline'], 30+30.5/60, delta=.02)
        self.assertEqual(result['s_fast'], 'TDIE')

    def test_airflow_dip_cannot_supply_either_role(self):
        for tau in (25, 90):
            data = capture({'TDIP': (20, tau, 18, .02)})
            for row in data['samples']:
                if row['phase'] == 'load':
                    t = row['elapsed_s']-300
                    row['values']['sensors']['TDIP'] = (30-min(t/50, 1) if t <= 60 else
                                                        29+19*(1-math.exp(-(t-60)/20)))
            result = rank(data)
            row = result['ranking'][0]
            # Baseline ~30 degC, early dip to 29 gives -1 degC; both
            # tau=25 (fast) and tau=90 (slow) require positive >3 floors.
            self.assertLess(row['delta_t60'], 0)
            # A smooth dip has no unresolved half-rise jump; R4 alone must refuse.
            self.assertLessEqual(row['max_one_second_change'], row['observed_rise']/2)
            self.assertFalse(row['eligible'])

    def test_role_specific_residual_noise_bars(self):
        # Sinusoid SD = amplitude/sqrt(2): .42/.50 bracket D4's 1/3;
        # .18/.24 bracket D5's .15. Rises and cooling times otherwise resolve.
        result = rank(capture({'TFOK': (3, 25, 18, .42), 'TFNO': (3, 25, 18, .50),
                               'TSOK': (60, 90, 8, .18), 'TSNO': (60, 90, 8, .24)}))
        rows = {r['key']: r for r in result['ranking']}
        self.assertEqual(rows['TFOK']['class'], 'die')
        self.assertEqual(rows['TSOK']['class'], 'heatsink')
        self.assertFalse(rows['TFNO']['eligible'])
        self.assertFalse(rows['TSNO']['eligible'])

    def test_production_jitter_resolves_both_picks_only_with_cell_tolerance(self):
        data = jittered_capture()
        coverage_type = thermal.Coverage

        def narrow_coverage(*args, **kwargs):
            kwargs["tolerance_ns"] = thermal.NS // 10
            return coverage_type(*args, **kwargs)

        for stage in ("r0", "r1"):
            with self.subTest(stage=stage):
                # Force the previous one-tenth-period window through real rank.
                with mock.patch.object(thermal, "Coverage", side_effect=narrow_coverage):
                    before = rank(data, stage=stage)
                for sensor in before["ranking"]:
                    for fraction in sensor["phase_coverage"].values():
                        # The unchanged quality bar requires 99% occupied cells.
                        self.assertLess(fraction, .99)
                self.assertEqual(before["selection"], {"s_fast": None, "s_slow": None})
                self.assertEqual(before["status"], "inconclusive")

                after = rank(data, stage=stage)
                for sensor in after["ranking"]:
                    for fraction in sensor["phase_coverage"].values():
                        # Every tick is present; jitter must clear the same 99% bar.
                        self.assertGreaterEqual(fraction, .99)
                self.assertEqual(after["selection"], {"s_fast": "TDIE", "s_slow": "THEA"})
                self.assertEqual(after["status"], "pass")
                sensors = {row["key"]: row for row in after["ranking"]}
                self.assertEqual(sensors["TDIE"]["class"], "die")
                self.assertEqual(sensors["THEA"]["class"], "heatsink")
                # A 3 s exponential reaches 63.2% at ~3 s; allow one sample period.
                self.assertAlmostEqual(sensors["TDIE"]["t63_s"], 3, delta=1)
                # Full-rise t63 is ~50 s. One period plus noise/slope
                # (0.1 / (8 / (50*e)) ~= 1.7 s) fits within three seconds.
                self.assertAlmostEqual(sensors["THEA"]["t63_end_s"], 50, delta=3)
                # Cooling tau is 120 s; one period plus noise/slope
                # (0.1 / (8 / (120*e)) ~= 4.1 s) fits within six seconds.
                self.assertAlmostEqual(sensors["THEA"]["tau_s"], 120, delta=6)
                # D4/D5: 3.0 degC = three times the 1 degC band floor.
                self.assertGreaterEqual(sensors["THEA"]["observed_rise"], 3.0)

    def test_two_percent_missing_load_cells_still_refuse_selection(self):
        data = jittered_capture()
        # Remove every 50th load tick: 900 / 50 = 18 missing of 900 (2%).
        # Interior removals leave the phase's first-reading grid unchanged.
        data["samples"] = [row for row in data["samples"]
                           if row["phase"] != "load" or int(row["elapsed_s"]) % 50 != 25]
        result = rank(data)
        for sensor in result["ranking"]:
            # 882 occupied / 900 expected cells = 98%, below the 99% bar.
            self.assertAlmostEqual(sensor["phase_coverage"]["load"], 882 / 900)
            self.assertLess(sensor["phase_coverage"]["load"], .99)
            self.assertEqual(sensor["class"], "record-only")
            self.assertIn("insufficient phase coverage", sensor["reason"])
        self.assertEqual(result["selection"], {"s_fast": None, "s_slow": None})
        self.assertEqual(result["status"], "inconclusive")

    def test_two_pole_die_uses_sixty_second_rise(self):
        data = capture({'TDIE': (1.5, 30, 40, .1)})
        for row in data['samples']:
            if row['phase'] == 'load':
                t = row['elapsed_s'] - 300
                row['values']['sensors']['TDIE'] = 30 + 20*(1-math.exp(-t/1.5)) + 20*(1-math.exp(-t/200))
        result = rank(data, stage='r1')
        sensor = result['ranking'][0]
        self.assertEqual(sensor['class'], 'die')
        self.assertLessEqual(sensor['t63_s'], 5)
        self.assertGreater(sensor['t63_end_s'], 5)

    def test_heatsink_longest_cooling_wins_and_null_never_falls_back(self):
        result = rank(capture({'TDIE': (2, 2, 18, .1), 'TH90': (60, 90, 8, .1),
                               'T250': (60, 250, 8, .1), 'T600': (60, 600, 8, .1)}), stage='r1')
        # 250*ln(8) >300 s, while 90*ln(8) <300 s: only TH90 is releasable.
        self.assertEqual(result['s_slow'], 'TH90')
        self.assertEqual(next(r for r in result['ranking'] if r['key'] == 'T600')['class'], 'record-only')
        only_die = rank(capture({'TDIE': (2, 2, 18, .1)}), stage='r0')
        self.assertIsNone(only_die['s_slow'])
        self.assertEqual(only_die['status'], 'inconclusive')

    def test_classes_are_disjoint_property(self):
        random.seed(14)
        for _ in range(200):
            tau = random.uniform(1, 500)
            # 60 s is one slope window; 300 s is the G1/H cap.
            cls = 'die' if tau <= 60 else 'heatsink' if tau <= 300 else 'record-only'
            rows = [{'key': 'TKEY', 'class': cls, 'observed_rise': 10, 'tau_s': tau, 't_band_s': tau*math.log(10)}]
            picks = select_keys(rows)
            self.assertFalse(picks['s_fast'] and picks['s_slow'])

    def test_non_temperature_and_one_percent_errors_are_record_only(self):
        data = capture({'F0Ac': (2, 2, 18, .1), 'TDIE': (2, 2, 18, .1)})
        data['inventory']['keys'][0]['unit'] = 'rpm'
        for row in data['samples'][300:306]:
            row['values']['errors']['TDIE'] = 'failed'
        result = rank(data, stage='r1')
        self.assertIsNone(result['s_fast'])


if __name__ == '__main__':
    unittest.main()
