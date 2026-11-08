"""R23e lead-ruling hand witnesses; all records are constructed synthetic data."""
from array import array
from decimal import Decimal
from dataclasses import replace
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import reduce_sol as sol
from joulewise.align.apple.sampler import seconds_ns, stamp_mapping, TRACE_DOMAIN
from joulewise.align.attribution import trace_energy
from joulewise.align.records import ClockMapping, to_json
from joulewise.align.power.windows import window_supports
from joulewise.align.v4_analysis import analyze, engine as e, exclusions as ex, raw
from joulewise.align.v4_analysis.io import canonical, strict_json, digest
from joulewise.align.v4_analysis.synthetic import series
from joulewise.clock import ClockStamp
from tests.align.test_attribution import episode, turn
from tests.align.test_v4_r23_engine import w1_window
from tests.align.v4_synthetic import synthetic_frames

NS = 1_000_000_000


class TimeoutTests(unittest.TestCase):
    def timeout(self, member, kind):
        # A timeout is a stop in the protocol even if the exporter left the
        # general status at its default. There is deliberately no X2 flag.
        member['thermal']['intervals'].append(dict(kind=kind, outcome='timeout'))

    def test_w1_timeout_excludes_anchor_without_recorded_x2(self):
        for kind in ('G1', 'H'):
            with self.subTest(kind=kind):
                p = series(turns=4)
                p['windows'] = p['windows'][:10]  # eight C + two T blocks
                w1 = w1_window(p)
                self.timeout(w1['members'][0], kind)
                p['windows'].insert(0, w1)
                fill, _ = analyze(p)
                self.assertEqual(fill['anchor_sigma_w']['K'], 10)
                self.assertEqual(fill['anchor_sigma_w']['W1_anchor_block'], 'excluded:X2')

    def test_timeout_union_reaches_u_units_fits_and_calibration(self):
        p = series(turns=6)  # one timeout / 56 entries stays below U1's 2% bar
        p['windows'] = p['windows'][:1]
        target = p['windows'][0]['members'][5]  # held-out benign
        self.timeout(target, 'H')
        target['source_flags'] = ['X3']
        # This extreme value must not reach the U2 range.
        target['thermal']['g0_slow_c'] = 99.
        fill, _ = analyze(p)
        row = fill['windows'][0]['eligibility'][5]
        self.assertEqual(row['rederived_classes'], ['X2'])
        self.assertEqual(row['recorded_classes'], ['X3'])
        self.assertEqual(row['classes'], ['X2', 'X3'])
        self.assertFalse(row['eligible'])
        checks = fill['windows'][0]['checks'][e.D_MODEL]
        self.assertEqual(checks['U1']['benign_only']['thermal_excluded_members'], 1)
        self.assertLess(checks['U2']['benign_only']['g0_slow_range_c'], 1.)
        pair = target['slot']['task_pair']
        self.assertEqual(fill['ledger'][0]['eligible_benign'][e.KEYS[pair]], 6)
        for convention in e.CONVENTIONS:
            cutoff = fill['thresholds'][convention+'/'+e.KEYS[pair]]
            self.assertEqual(cutoff['m'], 6)
            self.assertNotIn('C1/'+target['slot']['run_id'], cutoff['calibration_members'])
        for fit in fill['fits']:
            self.assertNotIn(target['slot']['run_id'], [r['run_id'] for r in fit['scores']])
            for score in fit['scores']:
                self.assertNotIn(target['slot']['run_id'], score['training_trajectories'])

    def test_explicit_timeout_count_on_stopped_episode_derives_x2(self):
        p = series(turns=4)
        member = p['windows'][0]['members'][5]
        member['thermal'].update(status='stopped', g1_h_timeouts=1)
        e._screen_member(member, p['cohort'])
        self.assertIn('X2', member['rederived_classes'])


class ExactTimeTests(unittest.TestCase):
    def samples(self, endpoints):
        samples = sol.reduce_stream(io.BytesIO(b''.join(synthetic_frames(len(endpoints)))))
        samples.columns['elapsed_ns'] = array('q', [NS]*len(endpoints))
        samples.columns['gpu_power'] = array('d', [10., 20.][:len(endpoints)])
        samples.endpoint_seconds = lambda _: endpoints
        return samples

    def test_exact_float_decimal_and_text_rounding_at_43e8_epoch(self):
        base = 4_300_000_000*NS
        # The exact float is base + 953.67431640625 ns. The ns product
        # previously rounded it a second time to base + 1024 ns.
        self.assertEqual(seconds_ns(4_300_000_000.000001), base+954)
        for value in ('4300000000.000000954', Decimal('4300000000.000000954')):
            self.assertEqual(seconds_ns(value), base+954)
        for value, expected in (('0.0000000005', 0), ('0.0000000015', 2),
                                ('-0.0000000015', -2)):
            self.assertEqual(seconds_ns(value), expected)
        samples = self.samples([4_300_000_000.000001])
        self.assertEqual(samples.monotonic_t_ns(0, -base)[0], 954)
        self.assertEqual(samples.native_pm_samples(0, -base)[0]['start_ns'], 954-NS)
        self.assertEqual(samples.mapped_columns(0, -base)['power_start_ns'][0], 954-NS)
        trace = next(t for t in samples.power_traces(0, nominal_interval_ns=NS)[0]
                     if t.channel == 'gpu_power')
        self.assertEqual(trace.t_ns, (base+954,))
        self.assertEqual(json.loads(trace.notes)['sample_support_ns'], [[base+954-NS, base+954]])

    def test_raw_json_float_is_recovered_before_exact_conversion(self):
        value = strict_json(b'{"first_record_endpoint_s":4300000000.000000954,"configuration":{"deadman_s":1200.0}}',
                            exact_seconds=True)
        self.assertIs(type(value['configuration']['deadman_s']), float)
        self.assertIs(type(value['first_record_endpoint_s']), float)
        samples = sol.reduce_stream(io.BytesIO(b''.join(synthetic_frames(2))))
        samples.columns['elapsed_ns'] = array('q', [NS, NS])
        self.assertEqual(list(samples.monotonic_t_ns(value['first_record_endpoint_s'], -4_300_000_000*NS)),
                         [954, NS+954])

    def test_paired_clock_offset_uses_exact_seconds_before_subtraction(self):
        mapping, _ = stamp_mapping([ClockStamp('4300000000.000000954', '100.000000001',
            '100.000000003', '0', '0')], episode_domain='host')
        self.assertEqual(mapping.offset_ns, -4_300_000_000*NS+100*NS-952)

    def test_large_epoch_gaps_stay_uncovered_and_exclude_members(self):
        for seam in (1900, 2000):
            with self.subTest(seam=seam):
                base = 9_000_000_000*NS
                samples = self.samples([Decimal('9000000001'),
                    Decimal('9000000002')+Decimal(seam)/NS])
                traces, _ = samples.power_traces(0, nominal_interval_ns=NS)
                trace = next(t for t in traces if t.channel == 'gpu_power')
                supports = [[base, base+NS], [base+NS+seam, base+2*NS+seam]]
                self.assertEqual(json.loads(trace.notes)['sample_support_ns'], supports)
                # The shared legacy reader must also never snap > 1 us,
                # even if the trace did not carry Sol's A37 marker.
                legacy_notes = json.loads(trace.notes)
                legacy_notes.pop('support_policy', None)
                legacy = replace(trace, notes=json.dumps(legacy_notes))
                self.assertEqual(window_supports(legacy), tuple(tuple(s) for s in supports))
                energy = trace_energy(trace, base, base+2*NS+seam)
                self.assertIn('duty.uncovered', energy.flags)
                # No energy may be invented by interpolating the gap.
                self.assertEqual(energy.joules, 30.)
                gap = trace_energy(trace, base+NS, base+NS+seam)
                self.assertEqual(gap.joules, 0.)
                self.assertIn('duty.uncovered', gap.flags)
                ep = episode(start_ns=0, end_ns=2*NS+seam,
                    turns=(turn(0, 0, 2*NS+seam, 1),), power_traces=(),
                    clock_mappings=(ClockMapping(TRACE_DOMAIN, 'host', -base, 0, 'synthetic'),))
                table = sol.turn_energy_table(samples, ep, first_record_endpoint_s=0,
                                              nominal_interval_ns=NS)['gpu_power']
                p = series(turns=4)
                for member in p['windows'][0]['members'][5:7]:
                    member['thermal']['energy_flags'] = table['attribution']['flags']
                    e._screen_member(member, p['cohort'])
                    self.assertFalse(member['eligible'])
                    self.assertIn('energy_unavailable', member['classes'])

    def test_raw_adapter_excludes_unflagged_owned_gap_at_large_epoch(self):
        p = series(turns=4)
        base = 9_000_000_000*NS
        samples = self.samples([Decimal('9000000001'), Decimal('9000000002.0000019')])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def write(name, data):
                (root/name).write_bytes(data)
                return dict(path=name, sha256=digest(data))
            pm = write('synthetic.plist', b''.join(synthetic_frames(2)))
            for slot in e.roster('C1')[5:7]:
                ep = episode(start_ns=0, end_ns=2*NS+1900,
                    turns=(turn(0, 0, 2*NS+1900, 1),), power_traces=(), clock_mappings=())
                ep = replace(ep, episode_id=slot['run_id'], seed=slot['expected_episode_seed'])
                source = dict(captured=True, episode=write('synthetic-episode.json', to_json(ep).encode()),
                    powermetrics=pm, first_record_endpoint_s='9000000001', nominal_interval_ns=NS,
                    stamps=[dict(epoch_s='9000000000', monotonic_before_s='0', monotonic_after_s='0',
                                 wall_resolution_s='0', monotonic_resolution_s='0')],
                    registered_span_ns=[0, 2*NS+1900], journal=[], exclusion_codes=[],
                    cohort_identity=p['cohort']['identity'], configuration=p['cohort']['configuration'])
                source = strict_json(canonical(source), exact_seconds=True)
                with patch.object(sol, 'reduce_file', return_value=samples):
                    member = raw.member(root, slot, source)
                e._screen_member(member, p['cohort'])
                self.assertEqual(member['summary']['offset_ns'], -base)
                self.assertIn('duty.uncovered', member['thermal']['energy_flags'])
                self.assertIn('energy_unavailable', member['rederived_classes'])
                self.assertNotIn('cohort_changed', member['rederived_classes'])
                self.assertFalse(member['eligible'])

    def test_2026_epoch_contiguous_fixture_keeps_energy_and_eligibility(self):
        base = 1_767_225_600*NS
        samples = self.samples([1_767_225_601., 1_767_225_602.])
        trace = next(t for t in samples.power_traces(0, nominal_interval_ns=NS)[0]
                     if t.channel == 'gpu_power')
        self.assertEqual(json.loads(trace.notes)['sample_support_ns'],
                         [[base, base+NS], [base+NS, base+2*NS]])
        energy = trace_energy(trace, base, base+2*NS)
        self.assertEqual(energy.joules, 30.)
        self.assertNotIn('energy_unavailable', ex.classes(energy.flags))


class SealTests(unittest.TestCase):
    def test_c_sabotage_member_is_hash_only_in_every_output_desk(self):
        p = series(turns=4)
        p['windows'] = p['windows'][:1]
        fill, _ = analyze(p)
        targets = {m['slot']['run_id'] for m in p['windows'][0]['members']
                   if m['slot']['series_role'] == 'sabotage'}
        found = set()
        def visit(value):
            if isinstance(value, dict):
                if value.get('run_id') in targets:
                    found.add(value['run_id'])
                    self.assertEqual(set(value)-{'window', 'run_id'}, {'status', 'sha256'})
                    self.assertEqual(value['status'], 'sealed')
                    self.assertEqual(len(value['sha256']), 64)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        visit(fill)
        self.assertEqual(found, targets)
        for i, row in enumerate(fill['realized_counts']):
            if row['run_id'] in targets:
                self.assertFalse(any(path['pointer'].startswith('/realized_counts/'+str(i)+'/rows')
                                     for path in fill['leaf_inventory']))
        before = next(r for r in fill['realized_counts'] if r['run_id'] in targets)
        changed = copy.deepcopy(p)
        target = next(m for m in changed['windows'][0]['members'] if m['slot']['run_id'] == before['run_id'])
        target['summary']['residual_rows']['True'][0]['decode_tokens'] += 1
        after, _ = analyze(changed)
        after = next(r for r in after['realized_counts'] if r['run_id'] == before['run_id'])
        self.assertNotEqual(before['sha256'], after['sha256'])
        self.assertNotIn('decode_tokens', canonical(after).decode())


if __name__ == '__main__':
    unittest.main()
