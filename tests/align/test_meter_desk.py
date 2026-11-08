"""Synthetic harvested-meter joins; no collectors, real streams or model files."""
from copy import deepcopy
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align.apple.meter_desk import read_meter_record, member_meter


def record():
    return {'schema': 'joulewise.b5_meter_cross_check.v1',
            'streams': [{'stream': 'stream-001.jsonl', 'status': 'streaming',
                         'aligned': True, 'raw_offset_ns': 50}],
            'members': {'member-1': {'stream': 'stream-001.jsonl', 'offset_source': 'stream',
                'rail_delta_J': 12., 'rho': .1,
                'machine': {'window_ns': [100_000_000_000, 102_000_000_000],
                    'baseline_ns': [90_000_000_000, 95_000_000_000], 'duration_s': 2.,
                    'meter': {'energy_J': 500., 'baseline_W': 200., 'delta_J': 100., 'n': 100},
                    'battery': {'energy_J': 20., 'baseline_W': 0., 'delta_J': 20., 'n': 10},
                    'battery_term_available': True, 'delta_J': 120.}}}}


class MeterDeskTests(unittest.TestCase):
    def test_gross_dc_and_signed_battery_stay_separate_from_rail_delta(self):
        value = record()
        before = deepcopy(value)
        row = member_meter(value, 'member-1')
        self.assertEqual(row['status'], 'diagnostic')
        self.assertEqual(row['meter_gross_j'], 500.)
        self.assertEqual(row['battery_gross_j'], 20.)
        self.assertEqual(row['machine_gross_j'], 520.)
        self.assertEqual(row['machine_delta_j'], 120.)
        self.assertEqual(row['rail_delta_j'], 12.)
        self.assertEqual(row['rho'], .1)
        self.assertEqual(row['window_raw_ns'], [100_000_000_000, 102_000_000_000])
        self.assertEqual(row['flags_status'], 'not_supplied')
        self.assertEqual(value, before)
        self.assertTrue(row['non_claim'])
        self.assertIn('controller request', row['boundary'])

    def test_absent_member_or_record_keeps_nulls_with_reasons(self):
        for value, member in ((None, 'member-1'), (record(), 'missing')):
            row = member_meter(value, member)
            self.assertEqual(row['status'], 'unavailable')
            self.assertIsNone(row['meter_gross_j'])
            self.assertIsNone(row['machine_gross_j'])
            self.assertTrue(row['reasons'])

    def test_missing_battery_never_calls_meter_only_a_machine_number(self):
        value = record()
        machine = value['members']['member-1']['machine']
        machine['battery_term_available'] = False
        machine['battery'] = {'energy_J': None, 'delta_J': None}
        machine['delta_J'] = 100.  # legacy parser's meter-only fallback
        row = member_meter(value, 'member-1')
        self.assertEqual(row['meter_gross_j'], 500.)
        self.assertIsNone(row['machine_gross_j'])
        self.assertIsNone(row['machine_delta_j'])
        self.assertIsNone(row['rho'])
        self.assertIn('battery_term_unavailable', row['reasons'])

    def test_charging_is_signed_and_flags_are_preserved(self):
        value = record()
        value['members']['member-1']['machine']['battery']['energy_J'] = -20.
        flags = [{'code': 'meter.drops_excess'}, {'code': 'meter.battery_activity'},
                 {'code': 'unrelated'}]
        row = member_meter(value, 'member-1', flags=flags)
        self.assertEqual(row['machine_gross_j'], 480.)
        self.assertEqual(row['flags'], ['meter.battery_activity', 'meter.drops_excess'])
        self.assertEqual(row['flags_status'], 'supplied')

    def test_nonfinite_and_malformed_values_are_unavailable_not_zero(self):
        for bad in (float('nan'), float('inf'), 10**400, True, '500'):
            value = record()
            value['members']['member-1']['machine']['meter']['energy_J'] = bad
            row = member_meter(value, 'member-1')
            self.assertIsNone(row['meter_gross_j'])
            self.assertIsNone(row['machine_gross_j'])
            json.dumps(row, allow_nan=False)
        for value in ({'members': []}, {'members': {'member-1': None}}, {'members': {'member-1': {'machine': []}}}):
            self.assertEqual(member_meter(value, 'member-1')['status'], 'unavailable')

    def test_reader_binds_exact_bytes_and_handles_missing_or_invalid_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'meter.json'
            missing = read_meter_record(path)
            self.assertIsNone(missing['record'])
            self.assertTrue(missing['reason'])
            raw = json.dumps(record()).encode()
            path.write_bytes(raw)
            loaded = read_meter_record(path)
            self.assertEqual(loaded['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(loaded['record'], record())
            for raw in (b'{', b'[]', b'{"schema":"wrong","members":{}}'):
                path.write_bytes(raw)
                self.assertIsNone(read_meter_record(path)['record'])

    def test_thermal_cli_joins_the_explicit_record_and_prints_dc_next_to_rails(self):
        from scripts import align_v4_thermal_desk as cli
        # The rest of the thermal calculations are already covered in test_thermal_desk.
        member = {'id': 'member-1', 'calibration_exclusions': [], 'flags': []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'meter.json').write_text(json.dumps(record()))
            manifest = root/'manifest.json'
            manifest.write_text(json.dumps({'meter_record': 'meter.json',
                'members': [{'bundle': 'synthetic-bundle'}]}))
            def report(members, **kwargs):
                return {'members': members, 'model_windows': {},
                        'deciding_experiment': {'verdict': 'INCONCLUSIVE', 'rule': 'synthetic', 'branch': 'synthetic'}}
            with patch.object(cli, 'read_bundle_record', return_value=member), patch.object(cli, 'window_report', side_effect=report):
                self.assertEqual(cli.main(['--manifest', str(manifest), '--output', str(root/'out')]), 0)
            output = json.loads((root/'out/PILOT.json').read_text())
            self.assertEqual(output['members'][0]['dc_input']['meter_gross_j'], 500.)
            self.assertEqual(output['meter_record']['sha256'], hashlib.sha256((root/'meter.json').read_bytes()).hexdigest())
            text = (root/'out/THERMAL.md').read_text()
            self.assertIn('KM003C', text)
            self.assertIn('500.0', text)

    def test_session_desk_reads_harvested_dc_even_when_episode_is_unreadable(self):
        from scripts import align_pilot_session as cli
        from joulewise.align.apple import pilot_analysis as pa
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cli.h.write(root/'session.json', {'session_id': 'synthetic',
                'measurement_root': str(root/'measurement'), 'registration_dir': str(root/'registration'),
                'plan_path': str(root/'plan.json'), 'runs_roots': {'claim': str(root/'runs')}})
            cli.h.write(root/'plan.json', {'custody_root': str(root/'custody')})
            cli.h.write(root/'custody/night/result.json', {})
            cli.h.write(root/'archive/withheld/meter.json', record())
            (root/'staging').mkdir()
            members = [{'run_id': 'member-1', 'task_pair': 'synthetic', 'condition': 'benign',
                        'repeat': 1, 'ordinal': 1}]
            with patch.object(cli, '_member_rows', return_value=members), \
                 patch.object(cli, 'episode_summary', side_effect=ValueError('synthetic unreadable')), \
                 patch.object(cli, 'instrument_checks', side_effect=lambda *args: (
                    {'I4_greedy_repeats_identical_tokens': True, 'chain_eligibility': True}, {}, {})), \
                 patch.object(pa, 'sampling_checks', return_value=({}, {}, {})), \
                 patch.object(pa, 'residual_analysis', return_value={}), redirect_stdout(io.StringIO()) as output:
                result = cli.desk(root, run=lambda *args, **kw: SimpleNamespace(returncode=0, stdout='', stderr=''))
                report = json.loads(Path(result['pilot']).read_text())
                self.assertEqual(report['members'][0]['dc_input']['machine_gross_j'], 520.)
                self.assertIsNone(report['members'][0]['summary'])
                for harvest, code in ((True, 2), (False, 0)):
                    result = cli.desk(root, harvest=harvest,
                        run=lambda *args, **kw: SimpleNamespace(returncode=code, stdout='', stderr=''))
                    stale = json.loads(Path(result['pilot']).read_text())
                    self.assertIsNone(stale['members'][0]['dc_input']['machine_gross_j'])
                    self.assertIn('stale', stale['meter_record']['reason'])
            self.assertIn('whole_request_dc_input:', output.getvalue())


if __name__ == '__main__':
    unittest.main()
