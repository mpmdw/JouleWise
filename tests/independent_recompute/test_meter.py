"""Raw KM003C fixtures with a known clock and hand-computed energy terms."""
import json
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest
from .support import recompute as r, full_pack, run_cli, dump


def stream_file(path, power, battery=lambda t: 0., count=2251, end_offset=0, duplicate=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    base = 10**12
    rows = [{'k': 'h', 'schema': 'joulewise.km003c_stream.v1', 'rate_idx': 2,
             'start_raw_ns': base, 'start_mono_ns': base}]
    for i in range(count):
        t = i * .02
        p = struct.pack('<HHiiHHHH', (i * 20) % 65536, 0, 10_000_000,
                        round(power(t) * 100_000), 0, 0, 0, 0)
        row = {'k': 'b', 'tx': base + i * 20_000_000 - 100_000, 'rx': base + i * 20_000_000,
               'n': 1, 'p': p.hex()}
        current = battery(t)
        if current is not None:
            row['smc'] = {'B0AC': -current * 100., 'B0AV': 10_000}
        rows.append(row)
        if duplicate and i == 10: rows.append(dict(row))
    rows.append({'k': 't', 'end_raw_ns': base + count * 20_000_000 + end_offset,
                 'end_mono_ns': base + count * 20_000_000})
    path.write_text(''.join(json.dumps(x) + '\n' for x in rows))
    return base


def member(reader, rail_phase=30., rail_idle=.047):
    return SimpleNamespace(run_id='synthetic-r01', reader=reader, origin=0.,
        metadata={'clock_anchor': {'wall_minus_monotonic_lower_s': -1000.,
                                  'wall_minus_monotonic_upper_s': -1000.},
                  'idle_baseline': {'power_w_mean': rail_idle}},
        events=[{'event_type': 'stage_started', 'phase': 'idle_baseline', 'timestamp_s': .5},
                {'event_type': 'stage_started', 'phase': 'idle_baseline', 'timestamp_s': 1.},
                {'event_type': 'stage_completed', 'phase': 'idle_baseline', 'timestamp_s': 3.}],
        edges={'decode': (20., 22.), 'request': (20., 22.)}, _rail_idle_power=rail_idle,
        records=[(0., 19., rail_idle), (19., 24., rail_phase), (24., 46., rail_idle)])


class MeterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.flags = []
        self.reader = r.Reader('ALPHA', self.flags)

    def test_constant_power_exact_100_samples_and_battery_unavailable(self):
        for available in (True, False):
            with self.subTest(battery_available=available):
                path = self.root / ('available' if available else 'unavailable') / 'stream-001.jsonl'
                stream_file(path, lambda t: 50. if t >= 15. else 10.,
                            battery=(lambda t: 0.) if available else (lambda t: None))
                stream = r.MeterStream(path, self.reader)
                row = r.machine_member(member(self.reader), 'request', [stream], [], .045)
                self.assertEqual(row['meter']['n'], 100)
                self.assertEqual(row['duration_s'], 2.)
                self.assertEqual(row['meter']['baseline_W'], 10.)
                self.assertEqual(row['delta_J'], 80.)
                self.assertEqual(row['battery_term_available'], available)
                if not available:
                    self.assertIsNone(row['battery'])
                    self.assertTrue(any(f['code'] == 'meter_battery_unavailable' for f in self.flags))
                self.assertEqual(row['boundary'], r.MACHINE_BOUNDARY)
                self.assertEqual(row['metadata_idle_baseline_power_w_mean'], .047)
                self.assertEqual(row['baseline_ns'], [1_001_000_000_000., 1_003_000_000_000.])

    def test_offset_disagreement_over_one_ms_uses_nearest_journal(self):
        path = self.root / 'stream-001.jsonl'
        base = stream_file(path, lambda t: 50. if t >= 15. else 10., end_offset=2_000_000)
        stream = r.MeterStream(path, self.reader)
        journal = [{'finished': {'monotonic_ns': base, 'monotonic_raw_ns': base + 400_000}},
                   {'finished': {'monotonic_ns': base + 21_000_000_000, 'monotonic_raw_ns': base + 21_000_000_000 + 200_000}}]
        row = r.machine_member(member(self.reader), 'request', [stream], journal, .045)
        self.assertEqual(row['offset_source'], 'journal')
        self.assertEqual(row['window_ns'][0], base + 20_000_000_000 + 200_000)
        self.assertTrue(any(f['code'] == 'meter_offset_from_journal' for f in self.flags))
        absent = r.machine_member(member(self.reader), 'request', [stream], [], .045)
        self.assertIsNone(absent['delta_J'])
        self.assertTrue(any(f['code'] == 'meter_offset_unavailable' for f in self.flags))

    def test_no_fit_and_uncovered_span_are_null_records(self):
        path = self.root / 'stream-001.jsonl'
        stream_file(path, lambda t: 50., count=19)
        stream = r.MeterStream(path, self.reader)
        self.assertIsNone(stream.fit)
        row = r.machine_member(member(self.reader), 'request', [stream], [], .045)
        self.assertIsNone(row['delta_J'])
        self.assertTrue({'meter_no_fit', 'meter_span_uncovered'} <= {f['code'] for f in self.flags})

    def test_each_edge_corner_sign_and_fixed_baseline(self):
        path = self.root / 'stream-001.jsonl'
        def power(t):
            return 10. if t < 19. else (40. if t < 20. else (50. if t < 22. else 60.))
        stream_file(path, power)
        stream = r.MeterStream(path, self.reader)
        m = member(self.reader)
        primary = r.machine_member(m, 'request', [stream], [], .062)
        for corner, sign in (((-1, -1), -1), ((-1, 1), 1), ((1, -1), -1), ((1, 1), 1)):
            with self.subTest(corner=corner):
                row = r.machine_member(m, 'request', [stream], [], .062, corner)
                self.assertGreater(sign * (row['delta_J'] - primary['delta_J']), 0.)
                self.assertEqual(row['baseline_ns'], primary['baseline_ns'])
                self.assertAlmostEqual(row['duration_s'], 2. + (corner[1] - corner[0]) * .062, delta=1e-12)

    def test_reconcile_worked_example_and_battery_length_correction(self):
        path = self.root / 'stream-001.jsonl'
        stream_file(path, lambda t: 9. if t < 19. else 72.,
                    lambda t: 0. if t < 19. else .5)
        stream = r.MeterStream(path, self.reader)
        # A known latency residual contributes 17 ms to the sensitivity delta.
        stream.r_max_s = .017
        m = member(self.reader)
        row = r.machine_member(m, 'request', [stream], [], .045)
        self.assertEqual(row['meter']['energy_J'], 144.)
        self.assertEqual(row['meter']['delta_J'], 126.)
        self.assertEqual(row['battery']['delta_J'], 1.)
        self.assertEqual(row['delta_J'], 127.)
        self.assertAlmostEqual(row['rail_delta_J'], 59.906, delta=1e-12)
        self.assertAlmostEqual(row['rho'], .4717, delta=.00005)
        corner = r.machine_member(m, 'request', [stream], [], .045, (-1, 1))
        self.assertEqual(corner['duration_s'], 2.124)
        self.assertAlmostEqual(corner['meter']['delta_J'] - row['meter']['delta_J'], 7.812, delta=1e-12)
        # REG 3523-3527: battery energy uses changed T too. The example's
        # 7.81 J is the meter-only change; the machine change also adds .062 J.
        self.assertAlmostEqual(corner['delta_J'] - row['delta_J'], 7.874, delta=1e-12)

    def test_duplicates_signed_unwrap_and_long_poll_gap(self):
        path = self.root / 'stream-001.jsonl'
        stream_file(path, lambda t: 50., count=4000, duplicate=True)
        stream = r.MeterStream(path, self.reader)
        self.assertEqual(stream.fit['duplicates_dropped'], 1)
        self.assertEqual(len(stream.times), 4000)
        self.assertAlmostEqual(stream.times[-1] - stream.times[0], 79.98e9, delta=.001)
        rows = [json.loads(x) for x in path.read_text().splitlines()]
        # Retain polls around a 40-second gap, including the 16-bit wrap.
        rows = [x for x in rows if x.get('k') != 'b' or x['rx'] < 10**12 + 20e9 or x['rx'] >= 10**12 + 60e9]
        path.write_text(''.join(json.dumps(x) + '\n' for x in rows))
        stream = r.MeterStream(path, self.reader)
        self.assertAlmostEqual(stream.times[-1] - stream.times[0], 79.98e9, delta=.001)

    def test_bin_minima_fit_and_residual_are_rederived(self):
        path = self.root / 'stream-001.jsonl'
        stream_file(path, lambda t: 50.)
        rows = [json.loads(x) for x in path.read_text().splitlines()]
        for row in rows:
            if row.get('k') == 'b':
                # In every 10-second device bin, exactly one poll arrives on
                # the true line; the others arrive 17 ms above it.
                latency = 0 if (row['rx'] - 10**12) % 10_000_000_000 == 0 else 17_000_000
                row['rx'] += latency; row['tx'] += latency
        path.write_text(''.join(json.dumps(x) + '\n' for x in rows))
        stream = r.MeterStream(path, self.reader)
        self.assertEqual(stream.fit['intercept_ns'], 10**12)
        self.assertEqual(stream.fit['slope_ns_per_ms'], 1_000_000.)
        self.assertEqual(stream.fit['minimum_bins'], 5)
        self.assertAlmostEqual(stream.r_max_s, .017, delta=1e-15)

    def test_machine_weighting_missing_unit_and_gamma_side_exact_t(self):
        def m(rid): return SimpleNamespace(run_id=rid)
        repeats = [(f'r{i}', [m(f'r{i}')]) for i in range(6)]
        quads = [(f'b{i}', [m(f'b{i}-{p}') for p in r.POSITIONS]) for i in range(6)]
        values = {ms[0].run_id: {'delta_J': float(i + 1), 'rho': .5, 'battery_term_available': True}
                  for i, (_, ms) in enumerate(repeats)}
        for i, (_, ms) in enumerate(quads):
            for x in ms:
                values[x.run_id] = {'delta_J': float(i + 2), 'rho': .4, 'battery_term_available': False}
        values['b0-b2']['delta_J'] = None
        line = r.machine_mean(repeats, quads, values)
        self.assertEqual((line['n_r'], line['n_b']), (6, 5))
        self.assertEqual(line['missing_units_by_stratum'], {'repeat': 0, 'quad': 1})
        self.assertAlmostEqual(line['mean_j'], .2 * 3.5 + .8 * 5., delta=1e-12)
        self.assertEqual(line['battery_unavailable_members'], 20)
        self.assertEqual(line['rho_n'], 26)
        side = r.machine_mean([], quads, values, 'a')
        self.assertEqual(side['n'], 5)
        self.assertEqual(side['mean_j'], 5.)
        self.assertAlmostEqual(side['h_j'], 2.7764451051977987 * (2.5 / 5.) ** .5, delta=1e-12)
        self.assertEqual(side['rho_n'], 10)
        values['r0']['delta_J'] = None; values['r1']['delta_J'] = None
        low = r.machine_mean(repeats, quads, values)
        self.assertEqual(low['note'], 'below the registered minimum')
        one = r.machine_mean(repeats[2:3], quads[1:2], values)
        self.assertAlmostEqual(one['mean_j'], 3.)
        self.assertIsNone(one['h_j'])
        self.assertEqual(one['note'], 'below the registered minimum')

    def test_meter_dir_override_and_cells_have_all_four_corner_changes(self):
        a = full_pack(self.root, 'ALPHA', 5)
        # Fixtures run at wall seconds 0-4; map those onto the meter at seconds 20-24.
        for path in (a / 'sources/claim-runs').glob('*/metadata.json'):
            d = json.loads(path.read_text())
            d['clock_anchor'] = {'wall_minus_monotonic_lower_s': -1020., 'wall_minus_monotonic_upper_s': -1020.}
            dump(path, d)
            events = path.parent / 'events.jsonl'
            rows = [{'event_type': 'stage_started', 'phase': 'idle_baseline', 'timestamp_s': -19.},
                    {'event_type': 'stage_completed', 'phase': 'idle_baseline', 'timestamp_s': -17.}]
            events.write_text(''.join(json.dumps(x) + '\n' for x in rows) + events.read_text())
        meter_dir = self.root / 'override'
        stream_file(meter_dir / 'stream-001.jsonl', lambda t: 10. if t < 15. else 50.)
        rc, out, _ = run_cli({'ALPHA': a}, self.root / 'machine.json', ('--meter-dir', str(meter_dir)))
        self.assertEqual(rc, 0)
        cells = out['disclosures']['whole_machine']['windows']['ALPHA']['cells']
        self.assertEqual(len(cells), 3)
        for cid, cell in cells.items():
            with self.subTest(cell=cid):
                self.assertEqual(len(cell['edge_shift_sensitivity']['corners']), 4)
                self.assertEqual(cell['boundary'], r.PHASE_MACHINE_BOUNDARY)
                if 'p42' in cid:
                    # A 31-ms diagnostic phase has an inverted span at the
                    # inward 2*b_op corner, so that corner has no phase value.
                    self.assertIsNone(cell['edge_shift_sensitivity']['max_abs_change_j'])
                else:
                    self.assertIsNotNone(cell['edge_shift_sensitivity']['max_abs_change_j'])
        self.assertIn('diagnostic', cells['df-ph-prefill-p42-qwen3-1p7b']['label'])
