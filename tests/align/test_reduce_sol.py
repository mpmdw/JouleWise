"""Synthetic and committed-fixture parity; no corpus discovery or live capture."""
from dataclasses import asdict, replace
import gzip
import hashlib
import io
import json
import math
from fractions import Fraction
from pathlib import Path
import plistlib
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from joulewise.adapters.powermetrics import (
    _parse_powermetrics_records, decode_rich_telemetry, parse_powermetrics_records, samples_from_records,
)
from joulewise.align.apple import reduce_sol as sol
from joulewise.align.apple.sampler import power_records, TRACE_DOMAIN
from joulewise.align.attribution import attribute_episode, owned_energy_flags
from joulewise.align.records import ClockMapping, ToolCall
from joulewise.align.records import to_json
from joulewise.interfaces import PowerSample
from scripts.bench_reduce_sol import synthetic_frames as realistic_frames
from tests.align.v4_synthetic import synthetic_frames
from tests.align.test_attribution import episode, turn

FIXTURES = Path(__file__).resolve().parents[1] / 'fixtures'
ENDPOINT = 1767225600.0
OFFSET = -1767225500000000000
EVIDENCE = {'clock_anchor': {'status': 'bounded', 'method': 'synthetic-test',
                              'effective_clock_anchor_bound_s': .031}}


def encoded(data, **kwargs):
    return sol.encode_columns(sol.reduce_stream(io.BytesIO(data), **kwargs))


def synthetic_episode(duration_ns=3_000_000_000):
    start = round(ENDPOINT * 1e9) + OFFSET - 100_000_000
    return episode(start_ns=start, end_ns=start + duration_ns,
                   turns=(turn(0, start, start + duration_ns // 2, start + 20_000_000,
                               calls=(ToolCall('test', start + 100_000_000, start + 150_000_000, 0, 0),)),
                          turn(1, start + duration_ns // 2 + 50_000_000, start + duration_ns,
                               start + duration_ns // 2 + 70_000_000)),
                   power_traces=(),
                   clock_mappings=(ClockMapping(TRACE_DOMAIN, 'host', OFFSET, 31_000_000, 'synthetic'),))


def a37_starts(supports):
    """Reference rule over adapter supports, independent of Sol code."""
    result = [list(s) for s in supports]
    for previous, current in zip(result, result[1:]):
        if 0 < abs(current[0]-previous[1]) <= 1000 and previous[1] < current[1]:
            current[0] = previous[1]
    return result


def reference_traces(records, *, evidence=EVIDENCE):
    # Snap the original observation sequence, before the sampler projects it.
    adapter_samples = samples_from_records(records)[::len(sol.RAILS)]
    native_supports = a37_starts([(round(Fraction(r.interval_start_s)*1_000_000_000),
                                  round(Fraction(r.interval_end_s)*1_000_000_000)) for r in adapter_samples])
    ends = [s[1] for s in native_supports]
    projected = [PowerSample(Fraction(end, 1_000_000_000), r.rail_power_w[rail], 'powermetrics', rail,
                            Fraction(support[0], 1_000_000_000), Fraction(end, 1_000_000_000))
                 for r, end, support in zip(records, ends, native_supports) for rail in sol.RAILS]
    traces, flags = power_records(projected, nominal_interval_ns=100_000_000,
                                  evidence=evidence)
    result, flags = [], list(flags)
    for trace in traces:
        notes = json.loads(trace.notes)
        retained = {}
        for i in sorted(range(len(records)), key=lambda i: records[i].timestamp_s):
            if math.isfinite(records[i].rail_power_w[trace.channel]):
                retained.setdefault(native_supports[i][1], native_supports[i])
        supports = [retained[t] for t in trace.t_ns]
        if supports != notes['sample_support_ns']:
            notes['sample_support_ns'] = supports
            flag = 'support_edge_snapped:'+trace.channel
            flags.append(flag); notes['flags'].append(flag)
        widths = {b-a for a,b in supports}
        variable_flag = 'variable_averaging_support:'+trace.channel
        flags = [f for f in flags if f != variable_flag]
        notes['flags'] = [f for f in notes['flags'] if f != variable_flag]
        notes['support_policy'] = 'A37'
        if len(widths) > 1:
            flags.append(variable_flag); notes['flags'].append(variable_flag)
        trace = replace(trace, notes=json.dumps(notes,sort_keys=True),
                        averaging_window_ns=next(iter(widths)) if len(widths)==1 else None)
        result.append(trace)
    return tuple(result), tuple(flags)


def reference_table(data, ep, *, endpoint=ENDPOINT, evidence=EVIDENCE):
    records = parse_powermetrics_records(data, first_record_endpoint_s=endpoint)
    traces, flags = reference_traces(records, evidence=evidence)
    joined = replace(ep, power_traces=traces, flags=tuple(dict.fromkeys((*ep.flags, *flags))))
    result = {}
    for rail in sol.RAILS:
        attributed = attribute_episode(joined, source='powermetrics', channel=rail)
        record = asdict(attributed)
        record['flags'] = owned_energy_flags(attributed)
        result[rail] = {'attribution': record, 'turns': [
            {'turn': t.index, 'owned_j': sum(s.energy.joules for s in attributed.segments if s.turn == t.index),
             'owned_half_width_j': sum(s.energy.half_width_j for s in attributed.segments if s.turn == t.index)}
            for t in ep.turns]}
    return result


class ExtractorEqualityTests(unittest.TestCase):
    def test_a37_hand_written_reference(self):
        # Inclusive ±1000ns interior seams close. ±1001ns seams and the
        # outside edges stay put. Expected starts are literal, not derived.
        supports = [[-20, 10000], [11000, 20000], [19000, 30000],
                    [31001, 40000], [38999, 50000]]
        expected = [[-20, 10000], [10000, 20000], [20000, 30000],
                    [31001, 40000], [38999, 50000]]
        self.assertEqual(a37_starts(supports), expected)
        starts = [s[0] for s in supports]
        sol._snap_interior_starts(starts, [s[1] for s in supports])
        self.assertEqual(starts, [-20, 10000, 20000, 31001, 38999])
        self.assertEqual(supports[0][0], -20)

    def assert_reference(self, data):
        samples = sol.reduce_stream(io.BytesIO(data))
        # Bytes, not tolerances: catches even one bit of reordered arithmetic.
        self.assertEqual(encoded(data, reference=True), sol.encode_columns(samples))
        records, diagnostic = _parse_powermetrics_records(data, first_record_endpoint_s=ENDPOINT)
        rich = decode_rich_telemetry(data, first_record_endpoint_s=ENDPOINT)
        self.assertEqual(len(samples), len(records))
        self.assertEqual(samples.raw_sha256, hashlib.sha256(data).hexdigest())
        self.assertEqual(samples.raw_size, len(data))
        self.assertEqual(samples.dropped_tail, asdict(diagnostic) if diagnostic else None)
        endpoints = [r.timestamp_s for r in records]
        self.assertEqual(list(samples.endpoint_seconds(ENDPOINT)), endpoints)
        pm = []
        adapter_samples = samples_from_records(records)[::len(sol.RAILS)]
        for native, detail, endpoint, support in zip(records, rich, endpoints, adapter_samples):
            end = round(Fraction(endpoint) * 1_000_000_000) + OFFSET
            states = (detail.get('gpu') or {}).get('dvfm_states', ())
            active = sum(s.get('used_ns', 0) for s in states)
            clock = sum(s['freq'] * s.get('used_ns', 0) for s in states) / active if active else None
            pm.append({'start_ns': round(Fraction(support.interval_start_s)*1_000_000_000) + OFFSET,
                       'end_ns': end, 'state': native.thermal_pressure,
                       'active_ns': active, 'clock_mhz': clock})
        for row, support in zip(pm, a37_starts([(r['start_ns'],r['end_ns']) for r in pm])):
            row['start_ns'] = support[0]
        self.assertEqual(samples.native_pm_samples(ENDPOINT, OFFSET), pm)
        self.assertEqual(json.dumps(samples.native_pm_samples(ENDPOINT, OFFSET), sort_keys=True),
                         json.dumps(pm, sort_keys=True))
        mapped = samples.mapped_columns(ENDPOINT, OFFSET)
        self.assertEqual(list(mapped['t_ns']), [r['end_ns'] for r in pm])
        self.assertEqual(list(mapped['thermal_start_ns']), [r['start_ns'] for r in pm])
        self.assertEqual(list(mapped['power_start_ns']), [r['start_ns'] for r in pm])
        for i, native in enumerate(records):
            self.assertEqual(samples.columns['native_timestamp_ns'][i], native.metadata['plist_timestamp_ns'])
            for rail in sol.RAILS:
                self.assertEqual(samples.columns[rail][i], native.rail_power_w[rail])
        self.assertEqual(samples.power_traces(ENDPOINT, nominal_interval_ns=100_000_000, evidence=EVIDENCE),
                         reference_traces(records))
        return samples

    def test_committed_real_and_small_fixtures(self):
        # Exact allowlist. Never glob for measurement material.
        for name in ('powermetrics_sample.plist', 'd078_r01/raw/powermetrics.plist',
                     'd117_v2_production/strict_seed_bundle/raw/powermetrics.plist',
                     'd117_v2_production/strict_seed_bundle/raw/powermetrics_idle.plist',
                     'd117_v2_production/strict_seed_bundle/raw/powermetrics_idle_post.plist',
                     'replay/envelope-01/raw/powermetrics-idle-1.plist',
                     'controller_g2b/block3-pre/raw/powermetrics.plist.gz'):
            with self.subTest(fixture=name):
                data = (FIXTURES / name).read_bytes()
                if name.endswith('.gz'):
                    data = gzip.decompress(data)
                self.assert_reference(data)

    def test_synthetic_realistic_skeleton(self):
        data = b''.join(realistic_frames(40))
        samples = self.assert_reference(data)
        self.assertGreater(len(data) / len(samples), 50_000)
        self.assertLess(len(sol.encode_columns(samples)), len(data) / 100)

    def test_chunk_boundaries_empty_frames_and_final_tear(self):
        data = b'\0\n\0' + b''.join(synthetic_frames(3)) + b'\0 \0<?xml broken'
        expected = sol.reduce_stream(io.BytesIO(data))
        original = sol._frames
        for chunk in (1, 19, 4096, 65536):
            with self.subTest(chunk=chunk), patch.object(sol, '_frames',
                    lambda h, d, s: original(h, d, s, chunk_bytes=chunk)):
                self.assert_reference(data)
                self.assertEqual(sol.reduce_stream(io.BytesIO(data)), expected)

    def test_random_field_order_whitespace_numbers_and_nested_collisions(self):
        rng = random.Random(731)
        doc = plistlib.loads(next(synthetic_frames(1)).rstrip(b'\0'))
        for _ in range(10):
            doc['elapsed_ns'] = rng.randrange(90_000_000, 120_000_000)
            doc['processor']['cpu_power'] = rng.uniform(-1, 50_000)
            doc['processor']['extra'] = {'gpu_power': 999999, 'thermal_pressure': 'wrong'}
            items = list(doc.items()); rng.shuffle(items)
            data = plistlib.dumps(dict(items), sort_keys=False)
            self.assert_reference(data)

    def test_duplicate_keys_and_escaped_strings(self):
        data = next(synthetic_frames(1))
        data = data.replace(b'<key>thermal_pressure</key>',
                            b'<key>thermal_pressure</key><string>wrong</string><key>thermal_pressure</key>', 1)
        data = data.replace(b'<string>Moderate</string>', b'<string>A &amp; B &lt; C</string>')
        self.assert_reference(data)

    def test_unknown_valid_scalar_uses_reference_fallback(self):
        data = next(synthetic_frames(1)).replace(b'<key>elapsed_ns</key>',
                    b'<key>blob</key><data>YWJj</data><key>elapsed_ns</key>', 1)
        self.assert_reference(data)
        self.assert_reference(next(synthetic_frames(1)).replace(b'<integer>100</integer>',
                                                              b'<integer>0XFF</integer>', 1))

    def test_float_active_counter_type_and_missing_clock_are_preserved(self):
        doc = plistlib.loads(next(synthetic_frames(1)).rstrip(b'\0'))
        for state in doc['gpu']['dvfm_states']:
            state['used_ns'] = 0.125
        self.assert_reference(plistlib.dumps(doc))
        doc['gpu'] = {}
        self.assert_reference(plistlib.dumps(doc))

    def test_empty_and_ratio_only_gpu_states_preserve_reference_diagnostics(self):
        doc = plistlib.loads(next(synthetic_frames(1)).rstrip(b'\0'))
        for states in ([{},dict(freq=300,used_ns=1)], [dict(used_ratio=.5),dict(freq=300,used_ns=1)],
                       [dict(used_ratio=[]),dict(freq=300,used_ns=1)]):
            doc['gpu']['dvfm_states'] = states
            data = plistlib.dumps(doc)
            outputs = []
            for reference in (True,False):
                try:
                    outputs.append(encoded(data, reference=reference))
                except Exception as exc:
                    outputs.append((type(exc),str(exc)))
            self.assertEqual(*outputs)

    def test_reference_fallback_without_compiler_or_unusual_xml(self):
        data = next(synthetic_frames(1))
        with patch.object(sol.native,'SCAN',None):
            self.assert_reference(data)
        for value in (b'<integer>bad</integer>',b'<date>2026-02-30T00:00:00Z</date>',
                      b'<string>bad]]&gt;</string>',b'<string>bad]]></string>'):
            changed = data.replace(b'<key>elapsed_ns</key>',b'<key>unused</key>'+value+b'<key>elapsed_ns</key>',1)
            a,b = [],[]
            for reference,output in ((True,a),(False,b)):
                try:
                    output.append(encoded(changed,reference=reference))
                except Exception as exc:
                    output.append((type(exc),str(exc)))
            self.assertEqual(a,b)

    def test_non_plist_iso_dates_do_not_bypass_reference_refusal(self):
        frame = next(synthetic_frames(1))
        for date in (b'2026-01-01 00:00:00Z', b'2026-01-01x00:00:00Z'):
            data = frame.replace(b'2026-01-01T00:00:00Z', date)
            errors = []
            for reference in (True, False):
                try:
                    sol.reduce_stream(io.BytesIO(data), reference=reference)
                except Exception as exc:
                    errors.append((type(exc), str(exc)))
            self.assertEqual(len(errors), 2)
            self.assertEqual(*errors)

    def test_semantic_refusals_and_malformed_frames_match_reference(self):
        frame = next(synthetic_frames(1))
        cases = [b'', b' \0\n', b'<?xml broken', b'<?xml broken\0' + frame,
                 frame + b'<?xml broken\0' + frame,
                 frame.replace(b'<key>cpu_energy</key>', b'<key>other_energy</key>'),
                 frame.replace(b'<key>gpu_power</key>', b'<key>other_power</key>'),
                 frame.replace(b'<real>1000.0</real>', b'<real>nan</real>'),
                 frame.replace(b'<integer>100</integer>', b'<integer>bad</integer>', 1),
                 frame.replace(b'<plist version="1.0">',
                    b'<!DOCTYPE plist [<!ENTITY x "entity">]><plist version="1.0">'),
                 plistlib.dumps([1, 2]) + b'\0',
                 frame.replace(b'<key>elapsed_ns</key>',
                      b'<key>unused</key><dict><string>bad</string></dict><key>elapsed_ns</key>', 1)]
        for data in cases:
            with self.subTest(prefix=data[:50]):
                errors = []
                for reference in (True, False):
                    try:
                        sol.reduce_stream(io.BytesIO(data), reference=reference)
                    except Exception as exc:
                        errors.append((type(exc), str(exc)))
                    else:
                        errors.append(None)
                self.assertIsNotNone(errors[0])
                self.assertEqual(errors[0], errors[1])

    def test_streaming_preserves_xml_error_priority_over_earlier_semantic_fault(self):
        frame = next(synthetic_frames(1))
        data = frame.replace(b'<key>cpu_energy</key>',b'<key>missing_energy</key>')+b'broken\0'+frame
        errors=[]
        for function in (lambda: _parse_powermetrics_records(data,first_record_endpoint_s=ENDPOINT),
                         lambda: sol.reduce_stream(io.BytesIO(data))):
            try:
                function()
            except Exception as exc:
                errors.append((type(exc),str(exc)))
        self.assertEqual(len(errors),2)
        self.assertEqual(*errors)

    def test_gpu_schema_fault_also_defers_to_later_xml_failure(self):
        frame=next(synthetic_frames(1))
        doc=plistlib.loads(frame.rstrip(b'\0'))
        doc['gpu']['dvfm_states']=[dict(used_ratio=.5),dict(freq=300,used_ns=1)]
        data=plistlib.dumps(doc)+b'\0broken\0'+frame
        errors=[]
        for reference in (True,False):
            try:
                sol.reduce_stream(io.BytesIO(data),reference=reference)
            except Exception as exc:
                errors.append((type(exc),str(exc)))
        self.assertEqual(len(errors),2)
        self.assertEqual(*errors)


class EnergyEqualityTests(unittest.TestCase):
    def test_exact_turn_tool_hold_gate_energies_uncertainties_and_flags(self):
        data = b''.join(synthetic_frames(40))
        samples = sol.reduce_stream(io.BytesIO(data))
        ep = synthetic_episode()
        start = ep.start_ns
        intervals = [
            {'kind': 'G0', 'start_ns': start - 1_000_000, 'end_ns': start},
            {'kind': 'H', 'turn': 0, 'start_ns': start + 200_000_000, 'end_ns': start + 250_000_000},
            {'kind': 'G1', 'start_ns': ep.turns[0].end_ns + 1, 'end_ns': ep.turns[1].start_ns - 1},
        ]
        for hardware in ({}, {'thermal': {'intervals': intervals}}):
            record = replace(ep, hardware=hardware)
            expected = reference_table(data, record)
            actual = sol.turn_energy_table(samples, record, first_record_endpoint_s=ENDPOINT,
                                          nominal_interval_ns=100_000_000, evidence=EVIDENCE)
            self.assertEqual(json.dumps(actual, sort_keys=True), json.dumps(expected, sort_keys=True))

    def test_turn_tables_are_recomputed_when_boundaries_and_clock_change(self):
        samples = sol.reduce_stream(io.BytesIO(b''.join(synthetic_frames(40))))
        ep = synthetic_episode()
        def table(record):
            return sol.turn_energy_table(samples, record, first_record_endpoint_s=ENDPOINT,
                                         nominal_interval_ns=100_000_000, evidence=EVIDENCE)
        before = table(ep)
        after = table(replace(ep, turns=ep.turns[:1]))
        self.assertEqual(len(before['gpu_power']['turns']), 2)
        self.assertEqual(len(after['gpu_power']['turns']), 1)
        changed_clock = replace(ep, clock_mappings=(replace(ep.clock_mappings[0], offset_ns=OFFSET+10_000_000),))
        self.assertNotEqual(before, table(changed_clock))

    def test_invalid_thermal_custody_still_refuses(self):
        samples = sol.reduce_stream(io.BytesIO(b''.join(synthetic_frames(40))))
        ep = synthetic_episode()
        bad = replace(ep, hardware={'thermal': {'intervals': [
            {'kind': 'H', 'turn': 1, 'start_ns': ep.start_ns, 'end_ns': ep.start_ns + 100_000_000}]}})
        with self.assertRaisesRegex(ValueError, 'hold must be contained'):
            sol.turn_energy_table(samples, bad, first_record_endpoint_s=ENDPOINT, nominal_interval_ns=100_000_000)


class CacheTests(unittest.TestCase):
    def test_cache_miss_reads_raw_once(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory)/'raw.plist'
            raw.write_bytes(next(synthetic_frames(1)))
            opened = []
            original = Path.open
            def witness(path, *args, **kwargs):
                if path == raw:
                    opened.append(path)
                return original(path, *args, **kwargs)
            with patch.object(Path, 'open', witness):
                sol.reduce_file(raw, cache_dir=Path(directory)/'cache')
            self.assertEqual(len(opened), 1)

    def test_hits_are_bound_to_bytes_and_refusals_are_not_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); raw = root / 'raw.plist'; cache = root / 'cache'
            raw.write_bytes(b''.join(synthetic_frames(3)))
            first = sol.reduce_file(raw, cache_dir=cache)
            calls = []
            previous = sys.getprofile()
            def witness(frame, event, arg):
                if event == 'call':
                    calls.append(frame.f_code)
            try:
                sys.setprofile(witness)
                hit = sol.reduce_file(raw, cache_dir=cache)
            finally:
                sys.setprofile(previous)
            self.assertIn(sol._sha_file.__code__, calls)
            self.assertNotIn(sol.reduce_stream.__code__, calls)
            self.assertEqual(sol.encode_columns(first), sol.encode_columns(hit))
            raw.write_bytes(raw.read_bytes().replace(b'1000.0', b'2000.0'))
            changed = sol.reduce_file(raw, cache_dir=cache)
            self.assertNotEqual(first.raw_sha256, changed.raw_sha256)
            self.assertNotEqual(first.columns['cpu_power'], changed.columns['cpu_power'])
            before = sorted(cache.rglob('*.jwsr'))
            raw.write_bytes(b'bad')
            with self.assertRaises(ValueError):
                sol.reduce_file(raw, cache_dir=cache)
            self.assertEqual(before, sorted(cache.rglob('*.jwsr')))

    def test_checksum_damage_rebuilds_and_loaded_code_rotates_namespace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); raw = root / 'raw'; cache = root / 'cache'
            raw.write_bytes(next(synthetic_frames(1)))
            first = sol.reduce_file(raw, cache_dir=cache)
            path = sol.cache_path(cache, first.raw_sha256)
            payload = path.read_bytes()
            path.write_bytes(payload[:-1] + bytes([payload[-1] ^ 1]))
            rebuilt = sol.reduce_file(raw, cache_dir=cache)
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(sol.encode_columns(first), sol.encode_columns(rebuilt))
            identity = sol.producer_sha256()
            original = sol._gpu_clock
            def changed_clock(document):
                active, clock = original(document)
                return active, clock + 1 if clock is not None else None
            with patch.object(sol, '_gpu_clock', changed_clock):
                self.assertNotEqual(identity, sol.producer_sha256())
                changed = sol.reduce_file(raw, cache_dir=cache)
                self.assertNotEqual(first.columns['clock_mhz'], changed.columns['clock_mhz'])
                self.assertNotEqual(path, sol.cache_path(cache, first.raw_sha256))

    def test_raw_change_during_single_parse_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); raw = root / 'raw'; raw.write_bytes(next(synthetic_frames(1)))
            original = sol.reduce_stream
            def raced(handle, **kwargs):
                result = original(handle, **kwargs)
                raw.write_bytes(raw.read_bytes().replace(b'1000.0', b'2000.0'))
                return result
            with patch.object(sol, 'reduce_stream', raced), self.assertRaisesRegex(ValueError, 'raw changed'):
                sol.reduce_file(raw, cache_dir=root / 'cache')
            self.assertFalse((root / 'cache').exists())

    def test_source_checkout_location_is_not_executable_identity(self):
        identity = sol.producer_sha256()
        original = sol._gpu_clock.__code__
        # No filesystem access: alter only in-memory debug metadata.
        try:
            sol._gpu_clock.__code__ = original.replace(co_filename='/synthetic-other-clone/reduce_sol.py')
            self.assertEqual(identity, sol.producer_sha256())
        finally:
            sol._gpu_clock.__code__ = original

    def test_serial_parallel_order_bytes_and_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); paths = []
            for i in (3, 1, 2):
                path = root / f'raw-{i}.plist'; path.write_bytes(b''.join(synthetic_frames(i))); paths.append(path)
            serial = sol.reduce_members(paths)
            parallel = sol.reduce_members(paths, workers=2)
            self.assertEqual([sol.encode_columns(s) for s in serial], [sol.encode_columns(s) for s in parallel])
            paths[1].write_bytes(b'bad')
            messages = []
            for workers in (1, 2):
                with self.assertRaises(ValueError) as error:
                    sol.reduce_members(paths, workers=workers)
                messages.append(str(error.exception))
            self.assertEqual(*messages)


class CommandTests(unittest.TestCase):
    def test_explicit_jobs_serial_parallel_bytes_and_no_partial_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'raw.plist').write_bytes(b''.join(synthetic_frames(35)))
            (root/'episode.json').write_text(to_json(synthetic_episode()))
            members = [{'id': 'm1', 'raw': 'raw.plist', 'episode': 'episode.json',
                        'first_record_endpoint_s': ENDPOINT, 'nominal_interval_ns': 100_000_000,
                        'uncertainty_evidence': EVIDENCE}]
            jobs = root/'jobs.json'; jobs.write_text(json.dumps({'members': members}))
            script = Path(__file__).resolve().parents[2]/'scripts/reduce_powermetrics_sol.py'
            def run(output, workers):
                return subprocess.run([sys.executable, '-B', str(script), '--jobs', str(jobs),
                        '--cache', str(root/'cache'), '--output', str(output), '--workers', str(workers)],
                        capture_output=True, text=True, timeout=30)
            first, second = root/'first.json', root/'second.json'
            result = run(first, 1); self.assertEqual(result.returncode, 0, result.stderr)
            result = run(second, 2); self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            report = json.loads(first.read_bytes())['members'][0]
            self.assertEqual(report['episode_sha256'], hashlib.sha256((root/'episode.json').read_bytes()).hexdigest())
            self.assertEqual(report['first_record_endpoint_s'], ENDPOINT)
            self.assertEqual(len(report['native_pm']), 35)
            self.assertEqual(len(report['energy']['gpu_power']['turns']), 2)
            for name in ('raw.plist', 'jobs.json', 'episode.json'):
                input_path = root/name
                before = input_path.read_bytes()
                result = run(input_path, 1)
                self.assertEqual(result.returncode, 2)
                self.assertIn('aliases an input', result.stderr)
                self.assertEqual(before, input_path.read_bytes())
            alias = root/'hardlink.plist'
            alias.hardlink_to(root/'raw.plist')
            result = run(alias, 1)
            self.assertEqual(result.returncode, 2)
            self.assertIn('aliases an input', result.stderr)
            members[0]['episode'] = 'absent.json'
            jobs.write_text(json.dumps({'members': members}))
            failed = root/'failed.json'
            result = run(failed, 1); self.assertEqual(result.returncode, 2)
            self.assertFalse(failed.exists())


if __name__ == '__main__':
    unittest.main()
