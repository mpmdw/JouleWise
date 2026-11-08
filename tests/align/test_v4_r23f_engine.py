"""R23f lead-ruling hand tests. All bytes and clock values are synthetic."""
from array import array
import copy
from dataclasses import asdict, replace
from decimal import Decimal
from fractions import Fraction
import io
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.apple import reduce_sol as sol, thermal_desk as td
from joulewise.align.apple.sampler import seconds_ns, stamp_mapping, TRACE_DOMAIN
from joulewise.align.records import ClockMapping, ToolCall, to_json
from joulewise.align.v4_analysis import analyze, acceptance as ac, engine as e, raw
from joulewise.align.v4_analysis.io import canonical, digest, strict_json
from joulewise.align.v4_analysis.synthetic import series
from joulewise.clock import ClockStamp
from tests.align.test_attribution import episode, turn
from tests.align.v4_synthetic import synthetic_frames

NS = 10**9


class RecordedTimeTests(unittest.TestCase):
    def test_production_float_export_offset_and_raw_adapter_check(self):
        # Chosen synthetic epoch/bracket: production's binary-float value
        # yields this literal offset, whereas treating its spelling as an
        # exact decimal yields a different one.
        stamp = ClockStamp(1766814254.4445496, 1000.000000059547,
                           1000.000000059547, 0., 0.)
        production, _ = stamp_mapping([stamp], episode_domain='host')
        self.assertEqual(production.offset_ns, -1766813254444549501)
        decimal_stamp = ClockStamp(**{k: str(v) for k, v in asdict(stamp).items()})
        decimal_mapping, _ = stamp_mapping([decimal_stamp], episode_domain='host')
        self.assertEqual(decimal_mapping.offset_ns, -1766813254444549540)
        slot = e.roster('C1')[5]
        ep = replace(episode(start_ns=1000*NS, end_ns=1001*NS,
            turns=(turn(0, 1000*NS, 1001*NS, 1000*NS+1),), power_traces=(),
            clock_mappings=()), episode_id=slot['run_id'], seed=slot['expected_episode_seed'])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def write(name, data):
                (root/name).write_bytes(data)
                return dict(path=name, sha256=digest(data))
            source = dict(captured=True, episode=write('episode.json', to_json(ep).encode()),
                powermetrics=write('pm.plist', b''.join(synthetic_frames(2))),
                first_record_endpoint_s=stamp.epoch_s, nominal_interval_ns=100_000_000,
                stamps=[asdict(stamp)], offset_ns=production.offset_ns,
                registered_span_ns=[ep.start_ns, ep.end_ns], journal=[])
            # Exactly the normal json.dumps float serialization used by the
            # exporter; no string conversion of recorded float seconds.
            exported = strict_json(json.dumps(source).encode(), exact_seconds=True)
            actual = raw.member(root, slot, exported)
            self.assertEqual(actual['summary']['offset_ns'], production.offset_ns)
            exported['offset_ns'] += 1
            with self.assertRaisesRegex(ValueError, 'exported production clock offset differs'):
                raw.member(root, slot, exported)

    def test_954ns_float_endpoint_accumulates_exact_native_ns(self):
        value = strict_json(b'{"first_record_endpoint_s":4300000000.000000954}', exact_seconds=True)
        anchor = value['first_record_endpoint_s']
        self.assertEqual(Fraction(anchor)-4_300_000_000, Fraction(1, 1048576))
        samples = sol.reduce_stream(io.BytesIO(b''.join(synthetic_frames(3))))
        samples.columns['elapsed_ns'] = array('q', [NS, 100_000_001, 100_000_003])
        base = 4_300_000_000*NS
        expected = [954, 100_000_955, 200_000_958]
        self.assertEqual(seconds_ns(anchor)-base, 954)
        self.assertEqual(list(samples.monotonic_t_ns(anchor, -base)), expected)
        self.assertEqual([r['end_ns'] for r in samples.native_pm_samples(anchor, -base)], expected)
        trace = next(t for t in samples.power_traces(anchor, nominal_interval_ns=NS)[0]
                     if t.channel == 'gpu_power')
        self.assertEqual(trace.t_ns, tuple(base+t for t in expected))
        # Float API and JSON round trip produce identical projected bytes.
        self.assertEqual(canonical(asdict(trace)), canonical(asdict(next(t for t in
            samples.power_traces(4_300_000_000.000001, nominal_interval_ns=NS)[0]
            if t.channel == 'gpu_power'))))

    def test_integer_and_explicit_decimal_remain_exact(self):
        value = strict_json(b'{"epoch_s":4300000000,"first_record_endpoint_s":"4300000000.000000955"}',
                            exact_seconds=True)
        self.assertIs(type(value['epoch_s']), int)
        self.assertEqual(seconds_ns(value['first_record_endpoint_s']), 4_300_000_000*NS+955)
        self.assertEqual(seconds_ns(Decimal('4300000000.000000955')), 4_300_000_000*NS+955)


class OwnedCoverageTests(unittest.TestCase):
    def check(self, turns, *, start=0, seam=0, intervals=()):
        samples = sol.reduce_stream(io.BytesIO(b''.join(synthetic_frames(2))))
        samples.columns['elapsed_ns'] = array('q', [NS, NS])
        samples.columns['gpu_power'] = array('d', [10., 20.])
        base = 9_000_000_000*NS
        samples.endpoint_seconds = lambda _: [Decimal('9000000001'),
            Decimal('9000000002')+Decimal(seam)/NS]
        hardware = ({'thermal': {'policy': {'sensors': {'s_fast': 'F', 's_slow': 'S', 'fan_keys': []}},
                                'intervals': list(intervals)}} if intervals else {})
        ep = episode(start_ns=start, end_ns=2*NS+seam, turns=turns,
            hardware=hardware, power_traces=(),
            clock_mappings=(ClockMapping(TRACE_DOMAIN, 'host', -base, 0, 'synthetic'),))
        table = sol.turn_energy_table(samples, ep, first_record_endpoint_s=0,
                                      nominal_interval_ns=NS)['gpu_power']['attribution']
        traces, _ = samples.power_traces(0, nominal_interval_ns=NS)
        ep = replace(ep, power_traces=traces)
        record = td.member_record(ep, [], os_readings=[], pm_samples=[], pm_period_s=1.)
        p = series(turns=4)
        member = p['windows'][0]['members'][5]
        # Keep the unrelated synthetic thermal qualification intact; carry
        # the production desk's actual energy evidence into the screen.
        for key in ('energy_flags', 'owned_energy_flags'):
            member['thermal'][key] = record[key]
        e._screen_member(member, p['cohort'])
        probe = copy.deepcopy(p['windows'][0]['members'][6])
        probe['thermal']['energy_flags'] = table['flags']  # p7/p8 wiring
        e._screen_member(probe, p['cohort'])
        self.assertEqual(member['eligible'], probe['eligible'])
        fill, _ = analyze({**p, 'windows': p['windows'][:1]})
        return member, table, fill['windows'][0]['eligibility'][5]

    def test_p7_edge_partial_owned_time_excludes(self):
        member, table, _ = self.check((turn(0, -NS//2, 2*NS, 1),), start=-NS//2)
        self.assertFalse(member['eligible'])
        self.assertIn('energy_unavailable', member['rederived_classes'])
        self.assertIn('trace.partial_coverage', table['flags'])

    def test_p8_g1_seam_is_eligible_with_disclosure(self):
        gate = dict(kind='G1', start_ns=NS-1000, end_ns=NS+3000, outcome='released',
                    entry_stamp={}, exit_stamp={})
        member, table, printed = self.check((turn(0, 0, NS-1000, 1),
            turn(1, NS+3000, 2*NS+2000, NS+3001)), seam=2000, intervals=(gate,))
        self.assertTrue(member['eligible'])
        self.assertIn('duty.uncovered', table['total']['flags'])
        self.assertNotIn('duty.uncovered', table['flags'])
        self.assertEqual(printed['coverage_disclosures'], ['duty.uncovered'])

    def test_preturn_edge_is_eligible_with_disclosure(self):
        member, _, printed = self.check((turn(0, 0, 2*NS, 1),), start=-NS//2)
        self.assertTrue(member['eligible'])
        self.assertIn('trace.partial_coverage', printed['coverage_disclosures'])

    def test_interior_owned_seam_and_own_tool_edge_exclude(self):
        member, _, _ = self.check((turn(0, 0, 2*NS+2000, 1),), seam=2000)
        self.assertFalse(member['eligible'])
        member, _, _ = self.check((turn(0, 0, NS, 1,
            calls=(ToolCall('synthetic', -NS//2, 0, 0, 0),)),), start=-NS//2)
        self.assertFalse(member['eligible'])

    def test_seam_inside_hold_is_unowned(self):
        hold = dict(kind='H', turn=0, start_ns=NS-1000, end_ns=NS+3000,
                    outcome='released', entry_stamp={}, exit_stamp={})
        member, _, printed = self.check((turn(0, 0, 2*NS+2000, 1),),
                                        seam=2000, intervals=(hold,))
        self.assertTrue(member['eligible'])
        self.assertIn('duty.uncovered', printed['coverage_disclosures'])


class SealScopeTests(unittest.TestCase):
    def payload(self):
        p = series(turns=6)
        p['windows'] = p['windows'][:1]
        return p

    def test_anchor_sabotage_prints_as_anchor_but_scored_roster_is_sealed(self):
        p = series(turns=6)
        p['windows'] = p['windows'][:3]
        fill, _ = analyze(p)
        self.assertEqual(fill['anchor_sigma_w']['K'], 3)
        for ordinal in (2, 3):
            run = p['windows'][0]['members'][ordinal-1]['slot']['run_id']
            for desk in ('realized_counts', 'cache_diagnostics', 'dc_secondary'):
                row = next(r for r in fill[desk] if r['run_id'] == run)
                self.assertEqual(row['series_role'], 'anchor')
            counts = next(r for r in fill['realized_counts'] if r['run_id'] == run)
            self.assertEqual(len(counts['rows']), 6)
            self.assertTrue(fill['windows'][0]['eligibility'][ordinal-1]['eligible'])
        for ordinal in (9, 18):
            row = fill['windows'][0]['eligibility'][ordinal-1]
            self.assertEqual(row['status'], 'sealed')
            self.assertEqual(set(row), {'run_id', 'status', 'sha256'})

    def test_all_member_verdicts_survive_sealing_beside_benign_only_counts(self):
        p = self.payload()
        target = p['windows'][0]['members'][8]
        target['thermal']['intervals'].append(dict(kind='H', outcome='timeout'))
        # One timeout / 91 entries stays below 2%; its released G0 is
        # excluded from the U2 range by X2.
        fill, _ = analyze(p)
        members = copy.deepcopy(p['windows'][0]['members'])
        for m in members:
            e._screen_member(m, p['cohort'])
        expected = ac.window_checks(members, ac.u3_derivation(p['u3_evidence']), window='C1')[e.D_MODEL]
        actual = fill['acceptance']['C1'][e.D_MODEL]
        for unit in ('U1', 'U2'):
            self.assertEqual(actual[unit]['status'], expected[unit]['status'])
            for key, value in expected[unit].items():
                if key in ('status', 'parts'):
                    continue
                self.assertEqual(actual[unit][key], {'status': 'sealed', 'sha256': digest(canonical(value))})
        self.assertEqual(actual['U1']['benign_only']['turn_admissions'], 80)
        self.assertEqual(actual['U1']['benign_only']['g1_h_timeouts'], 0)
        self.assertEqual(actual['U1']['benign_only']['thermal_excluded_members'], 0)
        self.assertEqual(actual['U1']['thermal_excluded_members']['sha256'], digest(canonical(1)))
        # A second scored thermal exclusion fails the registered all-member
        # U1 and bars the pool, while the benign-only verdict still passes.
        p['windows'][0]['members'][17]['thermal']['intervals'].append(dict(kind='H', outcome='timeout'))
        failed, _ = analyze(p)
        u1 = failed['acceptance']['C1'][e.D_MODEL]['U1']
        self.assertEqual(u1['status'], 'fail')
        self.assertEqual(u1['benign_only']['status'], 'pass')
        self.assertFalse(failed['windows'][0]['pool_entry'])

    def test_no_captured_benign_members_keeps_aggregate_unavailable(self):
        p = self.payload()
        for member in p['windows'][0]['members']:
            if member['slot']['condition'] == 'benign':
                member['captured'] = False
                member['summary'] = None
        fill, _ = analyze(p)
        checks = fill['acceptance']['C1'][e.D_MODEL]
        self.assertEqual(checks['U1']['benign_only']['turn_admissions'], 0)
        self.assertEqual(checks['U1']['benign_only']['status'], 'inconclusive')
        self.assertIsNone(checks['U2']['benign_only']['g0_slow_range_c'])

    def test_not_captured_sealed_member_prints_structural_false_everywhere(self):
        p = self.payload()
        target = p['windows'][0]['members'][8]
        target['captured'] = False
        target['summary'] = None
        fill, _ = analyze(p)
        run = target['slot']['run_id']
        rows = [fill['windows'][0]['eligibility'][8]]
        rows.extend(next(r for r in fill[desk] if r['run_id'] == run)
                    for desk in ('realized_counts', 'cache_diagnostics', 'dc_secondary'))
        for row in rows:
            self.assertEqual(row['status'], 'sealed')
            self.assertIs(row['captured'], False)
            self.assertNotIn('rows', row)

    def test_null_timeout_count_is_zero(self):
        p = self.payload()
        member = p['windows'][0]['members'][5]
        member['thermal']['g1_h_timeouts'] = None
        e._screen_member(member, p['cohort'])
        self.assertTrue(member['eligible'])
        member['thermal']['status'] = 'stopped'
        self.assertEqual(td.thermal_timeout_exclusions(member['thermal']), [])
        member['thermal']['g1_h_timeouts'] = 1
        self.assertTrue(td.thermal_timeout_exclusions(member['thermal']))


if __name__ == '__main__':
    unittest.main()
