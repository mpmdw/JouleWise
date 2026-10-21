"""Non-claim H preparation, real harvest/export/receipt/gate chain and handoff."""
from __future__ import annotations

import base64
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from configs.campaigns.bytes_mac_check.registration import derive_identity_pins as inputs
from joulewise.b5 import plan
from joulewise.b6 import registration
from joulewise.provenance import folded_model_artifact_sha256
from scripts import bytes_h_session as h, harvest_b6_session

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / inputs.KIT / 'registration'


def setUpModule():
    global _temporary, _old_tempdir, _old_env
    _old_tempdir = tempfile.tempdir
    _old_env = {k: os.environ.get(k) for k in ('TMPDIR', 'JW_B5_SYNTHETIC_ONLY')}
    _temporary = tempfile.TemporaryDirectory(prefix='bytes-h-module-', dir='/private/tmp' if Path('/private/tmp').exists() else None)
    os.environ.update(TMPDIR=_temporary.name, JW_B5_SYNTHETIC_ONLY='1')
    tempfile.tempdir = _temporary.name


def tearDownModule():
    tempfile.tempdir = _old_tempdir
    for key, value in _old_env.items():
        if value is None: os.environ.pop(key, None)
        else: os.environ[key] = value
    _temporary.cleanup()


class RegistrationInputTests(unittest.TestCase):
    def test_dispatch_roster_includes_ten_models_and_reference(self):
        observed = []
        def identity(source):
            observed.append(source)
            return {'status': 'ok', 'sha256': hashlib.sha256(source.encode()).hexdigest()}
        document, artifacts = inputs.derive(ROOT, '/synthetic/python', identity=identity,
            versions=lambda _: {'python': 'synthetic', 'packages': {}})
        # R8.6: 98 kit + 18 corpus + 3 start + 1 midpoint + 3 end = 123.
        # Twelve test-7 references join 25 scaffold references = 37.
        self.assertEqual(len(set(observed)), 11)
        self.assertEqual(sum(u['config_count'] for u in document['units'].values()), 123)
        self.assertEqual(document['units']['neg8_reference']['config_count'], 37)
        self.assertEqual(set(document['units']), set(artifacts['artifacts']))
        self.assertTrue(all(u['stack_identity'] == {} for u in document['units'].values()))

    def test_missing_model_is_not_written_as_a_pin(self):
        with self.assertRaisesRegex(ValueError, 'model files unavailable'):
            inputs.derive(ROOT, '/synthetic/python', identity=lambda _: {'status': 'unavailable'},
                          versions=lambda _: self.fail('runtime must follow successful model hashing'))

    def test_stored_pins_match_hash_inventory_and_roster(self):
        pins = registration.load_identity_pins(REG)
        inventory = h.read(REG / 'model_artifact_inventory.json')['artifacts']
        roster = h.read(ROOT / 'configs/campaigns/bytes_v1/roster.json')['models']
        self.assertEqual(set(pins['units']) - {'neg8_reference'}, {m['model_id'] for m in roster})
        for name, unit in pins['units'].items():
            artifact = inventory[name]
            digest = folded_model_artifact_sha256(artifact['files']) if artifact['kind'] == 'file_set' else artifact['sha256']
            self.assertEqual(unit['model_artifact_sha256'], digest)

    def test_acceptance_and_smoke_are_isolated_copies(self):
        target = registration.load(REG)
        source = registration.load(ROOT / registration.DEFAULT_DIR_RELATIVE)
        self.assertEqual(target['calibration'], source['calibration'])
        self.assertEqual(target['pack_id'], h.PACK_ID)
        self.assertTrue(target['non_claim'])
        self.assertIsNone(target['calibration']['operative_bound_stop_s'])
        self.assertEqual(h.read(REG / 'smoke_keep.json'),
            {'bytes_mac_check': h.read(ROOT / 'configs/b6/smoke_keep.json')['bytes_mac_check']})

    def test_f2_interpolation_is_between_measured_dense_weight_bytes(self):
        sized = registration.load_sizing(REG)['packs'][h.PACK_ID]
        models = sized['models']; row = models['qwen3-8b-8bit']; derivation = row['interpolation']
        lo, hi = models[derivation['lower_model']], models[derivation['upper_model']]
        self.assertLess(lo['weight_bytes'], row['weight_bytes'])
        self.assertLess(row['weight_bytes'], hi['weight_bytes'])
        self.assertEqual(row['flag'], 'sizing.planning_bound_interpolated')
        fraction = (row['weight_bytes'] - lo['weight_bytes']) / (hi['weight_bytes'] - lo['weight_bytes'])
        for a, b, value in zip(lo['request_s'], hi['request_s'], row['request_s'], strict=True):
            # Brief agreement bar: 1e-6 relative or absolute in seconds.
            self.assertTrue(math.isclose(value, a + fraction * (b-a), rel_tol=1e-6, abs_tol=1e-6))
        self.assertEqual(derivation['sources'], [lo['source'], hi['source']])
        self.assertEqual(sum(sized['counts_by_model'].values()), 123)
        expected = (sum(row['request_s']) / len(row['request_s']) + row['load_s']
                    + h.read(REG / 'sizing_evidence.json')['max_non_request_s']) * (1 + sized['measured_margin'])
        self.assertTrue(math.isclose(row['member_allowance_s'], expected, rel_tol=1e-6, abs_tol=1e-6))
        self.assertEqual(sized['disk_derivation']['reserve_bytes'], h.RESERVE_BYTES)


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.measurement = self.root / 'measurement'
        self.session = self.root / 'session'
        m = self.measurement
        (m / 'configs/campaigns').mkdir(parents=True)
        for p in (ROOT / 'configs').iterdir():
            if p.name != 'campaigns': (m / 'configs' / p.name).symlink_to(p, target_is_directory=p.is_dir())
        for p in (ROOT / 'configs/campaigns').iterdir():
            if p.name != 'bytes_mac_check': (m / 'configs/campaigns' / p.name).symlink_to(p, target_is_directory=p.is_dir())
        shutil.copytree(ROOT / h.KIT, m / h.KIT)
        for name in ('scripts', 'joulewise', 'docs'):
            (m / name).symlink_to(ROOT / name, target_is_directory=True)
        (m / '.venv/bin').mkdir(parents=True)
        (m / '.venv/bin/python').symlink_to(sys.executable)
        (m / plan.DEFAULT_LEDGER_RELATIVE).parent.mkdir(parents=True)
        (m / plan.DEFAULT_LEDGER_RELATIVE).write_text('')
        reg = m / h.KIT / 'registration'
        pins = h.read(reg / 'identity_pins.json')
        inventory = h.read(reg / 'model_artifact_inventory.json')
        fake = self.root / 'models'; fake.mkdir(); (fake / 'weight').write_bytes(b'synthetic')
        for name, unit in pins['units'].items():
            unit['model_source'] = str(fake)
            inventory['artifacts'][name]['inventory'] = [{'path': 'weight', 'size_bytes': 9}]
        h.write(reg / 'identity_pins.json', pins)
        h.write(reg / 'model_artifact_inventory.json', inventory)

    def producer(self, argv, **kwargs):
        if '-c' in argv:
            payload = base64.b64encode(b'{"synthetic":true}\n').decode()
            return SimpleNamespace(returncode=0, stdout=json.dumps({k: payload for k in h.desk_identity.EXPECTED}), stderr='')
        return SimpleNamespace(returncode=0, stdout='a'*40 if 'rev-parse' in argv else '', stderr='')

    def prepared(self):
        # The calibration ledger's authentication belongs to its owning tests.
        # Only this fixture boundary is synthetic; write_window_plan is real.
        with patch.object(plan, 'ledger_head_status', return_value={'blocking': []}), redirect_stdout(io.StringIO()):
            return h.prepare(self.measurement, self.session, run=self.producer, now=lambda: 1700000000,
                disk_usage=lambda _: SimpleNamespace(free=10**12))

    def test_prepare_uses_real_writer_without_install_or_loop_registration(self):
        state = self.prepared()
        record = h.read(state['plan_path'])
        self.assertEqual(state['preparation_status'], 'STAGED')
        self.assertEqual(record['hazard_window']['member_count'], 123)
        self.assertEqual(record['window_max_s'], h.plan_inputs.window_max_s(state['inputs']))
        self.assertEqual(record['t0_epoch_s'], 60*math.ceil((1700000000+420)/60))
        self.assertFalse((self.session / 'collection.active').exists())
        self.assertNotIn('install', state)
        self.assertEqual(Path(state['inputs']['pack_root']), self.session / 'measurement/configs/campaigns' / h.PACK_ID)
        from joulewise.b6 import precheck
        limits = precheck.thresholds_for(state['measurement_root'], h.PACK_ID, state['registration_dir'])
        self.assertTrue(math.isclose(limits['clock']['t_stream_max_s'],
            state['inputs']['T_stream_max_s']['seconds'], rel_tol=1e-6, abs_tol=1e-6))
        self.assertTrue(Path(state['plan_path']).is_file())

    def test_prepare_and_native_arm_budget_the_same_peak_disk_bytes(self):
        from joulewise.b5 import driver
        state = self.prepared()
        record = h.read(state['plan_path'])
        hazard = record['hazard_window']
        copies = sum(t['copies'] for t in driver.disk_targets(hazard, arm=True))
        required = copies * hazard['planned_bytes'] + hazard['thresholds']['disk']['headroom_bytes']
        # Byte counts and native copy multiplicity are integers; exact equality
        # is appropriate for these two independent budget entry points.
        self.assertEqual(required, state['disk']['required_free_bytes'])
        sized = registration.load_sizing(self.measurement / h.KIT / 'registration')['packs'][h.PACK_ID]
        self.assertEqual(sized['disk_derivation']['window_max_s'], record['window_max_s'])
        self.assertGreater(sized['extra_wait_peak_bytes'], 0)

    def test_prepare_flags_missing_ledger_without_fabricating_a_plan(self):
        (self.measurement / plan.DEFAULT_LEDGER_RELATIVE).unlink()
        with redirect_stdout(io.StringIO()):
            state = h.prepare(self.measurement, self.session, run=self.producer, now=lambda: 1700000000,
                disk_usage=lambda _: SimpleNamespace(free=10**12))
        self.assertEqual(state['preparation_status'], 'INPUTS_ONLY')
        self.assertIn('plan.not_written', [f['kind'] for f in state['flags']])
        self.assertFalse(Path(state['plan_path']).exists())

    def test_physical_disk_hazard_stops_before_identity_or_plan(self):
        with self.assertRaises(h.PhysicalHazard), redirect_stdout(io.StringIO()):
            h.prepare(self.measurement, self.session, run=lambda *a, **k: self.fail('no producer before disk gate'),
                      disk_usage=lambda _: SimpleNamespace(free=h.RESERVE_BYTES-1))
        self.assertFalse((self.session / 'custody').exists())

    def test_missing_model_is_a_physical_hazard(self):
        (self.root / 'models/weight').unlink()
        with self.assertRaisesRegex(h.PhysicalHazard, 'models missing'):
            h.prepare(self.measurement, self.session)

    def test_install_calls_only_the_real_installer_interface_with_stub(self):
        state = self.prepared()
        calls = []
        def installer(argv, **kwargs):
            calls.append(argv)
            return SimpleNamespace(returncode=0, stdout='stub installed\n', stderr='')
        with redirect_stdout(io.StringIO()) as out:
            installed = h.install(self.session, run=installer, home=self.root / 'home')
        self.assertEqual(calls, [[str(self.session / 'measurement/scripts/install_night_agent.sh'), '--plan', state['plan_path'],
            '--python', str(self.session / 'measurement/.venv/bin/python'), '--courier-bin',
            str(self.session / 'measurement/scripts/b6_courier.sh'), '--launchctl-bin', 'launchctl']])
        self.assertEqual(len(installed['plist_paths']), 2)
        self.assertIn('com.joulewise.night.deadman.plist', out.getvalue())
        self.assertFalse((self.session / 'collection.active').exists())
        self.assertFalse((self.root / 'home').exists())

    def test_desk_requires_terminal_record(self):
        self.prepared()
        with self.assertRaisesRegex(ValueError, 'terminal record'):
            h.desk(self.session, run=lambda *a, **kw: self.fail('must not harvest before terminal'))

    def seed_collection(self, state):
        """All production manifests, native seed bundles; no model/collector runs."""
        clock, journal, thermal, contention, clocks = [], [], [], [], []
        tree = h.read(self.measurement / h.KIT / 'plan_tree.json')
        seed = ROOT / 'tests/fixtures/d117_v2_production/strict_seed_bundle'
        order = 0
        for stage in tree['stage_graph']:
            start = 1000 + order * 20
            if stage['kind'] == 'campaign_collection':
                manifest = h.read(self.measurement / stage['input']['path'])
                for row in manifest['executed_order']:
                    rid = row['run_id']
                    key = 'bound' if 'bound-collection' in stage['stage_id'] else 'claim'
                    bundle = Path(state['runs_roots'][key]) / rid
                    shutil.copytree(seed, bundle)
                    config = h.read((self.measurement / stage['input']['path']).parent / row['config'])
                    h.write(bundle / 'config.json', config)
                    meta = h.read(bundle / 'metadata.json'); meta['run_id'] = rid
                    h.write(bundle / 'metadata.json', meta)
                    summary = h.read(bundle / 'summary_metrics.json'); summary['run_id'] = rid
                    h.write(bundle / 'summary_metrics.json', summary)
                    a = (1000 + order * 20)*10**9; b = a + 15*10**9
                    for event, stamp in [('start', a), ('end', b)]:
                        clock.append({'run_id': rid, 'event': event, 'clock': {'wall_s': stamp/1e9,
                            'monotonic_ns': stamp, 'monotonic_raw_ns': stamp}})
                    thermal.append({'started': {'monotonic_ns': a}, 'finished': {'monotonic_ns': b}, 'values': {'level': 0}})
                    contention.append({'values': {'interval': {'monotonic_ns': [a,b]}, 'outside_total_cpu_s_per_s': .01, 'elapsed_s': (b-a)/1e9}})
                    for stamp in [a,b]:
                        clocks.append({'started': {'monotonic_ns': stamp}, 'finished': {'monotonic_ns': stamp},
                            'values': {'anchor': {'monotonic_raw_ns': stamp, 'anchor_ns': 10**12},
                                       'frequency': {'raw_word': 0}}})
                    order += 1
                end = 1000 + order*20
            else:
                end = start + 1
            journal.append({'stage_id': stage['stage_id'], 'kind': stage['kind'], 'rc': 0,
                            'started_epoch_s': start, 'ended_epoch_s': end})
        custody = self.session / 'custody'
        def jsonl(path, values):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(''.join(json.dumps(v)+'\n' for v in values))
        jsonl(custody / 'collection/run_clock.jsonl', clock)
        jsonl(custody / 'night/chain-stages.jsonl', journal)
        for name, values in [('thermal', thermal), ('contention', contention), ('clock', clocks)]:
            jsonl(custody / 'hazards/monitor' / (name+'.jsonl'), values)
        h.write(custody / 'night/chain.started', {'pgid': None})
        h.write(custody / 'night/chain.exited', {'exit_code': 0})
        h.write(custody / 'night/result.json', {'chain_exit_code': 0})

    def test_fully_observed_native_export_extracts_and_clears_c5(self):
        from tests.test_bytes_gates import synthetic_harvest
        state = self.prepared()
        exported, supplied = synthetic_harvest(self.session)
        state['inputs']['bracket_session_id'] = supplied['session_id']
        sidecar = h.read(exported.sidecar_path)
        # Controlled synthetic calibration receipt, in native sidecar form.
        sidecar['operative_bound_s'] = .04
        h.write(exported.sidecar_path, sidecar)
        clock, thermal, contention, clock_fits = [], [], [], []
        spans = {}
        with exported.csv_path.open(newline='') as stream:
            native_rows = list(csv.DictReader(stream))
        spacing = math.ceil(max(r['member_wall_s'] for r in supplied['runs'].values())) + 1
        for index, row in enumerate(native_rows):
            rid = row['run_id']; receipt = supplied['runs'][rid]
            bundle = self.session / 'archive/sources/claim-runs' / rid
            events = h.rows(bundle / 'events.jsonl')
            begin = 1000 + index * spacing
            shift = begin + 5 - events[0]['timestamp_s']
            for event in events: event['timestamp_s'] += shift
            request = receipt['request_s']; wall = receipt['member_wall_s']
            events = [{'event_type': 'sampling_started', 'timestamp_s': begin}, *events,
                      {'event_type': 'sampling_stopped', 'timestamp_s': begin+request}]
            (bundle / 'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
            h.write(bundle / 'metadata.json', {'uncertainty_evidence': {'clock_anchor': {'clock_stamps': {
                'pre_spawn': {'monotonic_before_s': begin-30},
                'post_parse': {'monotonic_after_s': begin-30+receipt['stream_s']},
                'sampling_started': {'monotonic_before_s': begin},
                'sampling_stopped': {'monotonic_after_s': begin+request}}}}})
            a, b = int((begin-40)*1e9), int((begin-40+wall)*1e9)
            for event, stamp in [('start', a), ('end', b)]:
                clock.append({'run_id': rid, 'event': event, 'clock': {'wall_s': stamp/1e9,
                    'monotonic_ns': stamp, 'monotonic_raw_ns': stamp}})
                clock_fits.append({'started': {'monotonic_ns': stamp}, 'finished': {'monotonic_ns': stamp},
                    'values': {'anchor': {'monotonic_raw_ns': stamp, 'anchor_ns': 10**12, 'read_skew_ns': 0},
                               'frequency': {'raw_word': 0}}})
            thermal.append({'started': {'monotonic_ns': a}, 'finished': {'monotonic_ns': b}, 'values': {'level': 0}})
            contention.append({'values': {'interval': {'monotonic_ns': [a,b]}, 'outside_total_cpu_s_per_s': .01, 'elapsed_s': (b-a)/1e9}})
            spans.setdefault(row['stage_id'], []).append((a/1e9,b/1e9))
        def jsonl(path, values):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(''.join(json.dumps(v)+'\n' for v in values))
        custody = self.session / 'custody'
        jsonl(custody/'collection/run_clock.jsonl', clock)
        for name, values in [('thermal', thermal), ('contention', contention), ('clock', clock_fits)]:
            jsonl(custody/'hazards/monitor'/(name+'.jsonl'), values)
        stages = []
        for stage in h.read(self.measurement / h.KIT / 'plan_tree.json')['stage_graph']:
            values = spans.get(stage['stage_id'], [(0,1)])
            stages.append({'stage_id': stage['stage_id'], 'kind': stage['kind'],
                'started_epoch_s': min(a for a,b in values), 'ended_epoch_s': max(b for a,b in values)})
        jsonl(custody/'night/chain-stages.jsonl', stages)
        h.write(custody/'hazards/arm.json', {'hazards': {'disk': [{'measurement': {
            'values': {'targets': [{'free_bytes': 10**12}]}}}]}})
        for name, values in [('regimes', supplied['regimes']), ('cpu_contention', supplied['cpu_contention'])]:
            h.write(self.session/'receipts'/(name+'.json'), {'schema_version': 'joulewise.bytes_h_'+name+'.v1',
                'non_claim': True, 'session_id': supplied['session_id'], 'values': values,
                'derivation': 'Controlled synthetic arithmetic from tests.test_bytes_gates.synthetic_harvest; never live evidence.'})
        measured = h.measurements(state, exported.csv_path)
        h.write(self.session/'MEASUREMENTS.json', measured)
        child = subprocess.run([sys.executable, str(ROOT/'scripts/bytes_gates.py'), '--runs', str(exported.csv_path),
            '--measurements', str(self.session/'MEASUREMENTS.json'), '--out', str(self.session/'C5.json')],
            capture_output=True, text=True)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertEqual(h.read(self.session/'C5.json')['status'], 'pass')
        self.assertEqual(len(measured['runs']), 123)
        self.assertEqual(measured['disk']['pre_arm_free_bytes'], 10**12)
        for rid, row in measured['runs'].items():
            for key in ('request_s', 'member_wall_s', 'stream_s'):
                self.assertTrue(math.isclose(row[key], supplied['runs'][rid][key], rel_tol=1e-6, abs_tol=1e-6))
        self.assertIsNone(measured['regimes']['qwen3-8b-8bit']['registered_T10_s'])
        self.assertFalse(h.read(self.session/'C5.json')['registration_ready'])
        # A truncated monitor journal and a wrong-shaped metadata record are
        # unavailable observations, not reasons to lose the measurement file.
        (custody/'hazards/monitor/thermal.jsonl').write_text('{truncated\n')
        first = native_rows[0]['run_id']
        h.write(self.session/'archive/sources/claim-runs'/first/'metadata.json', None)
        unavailable = h.measurements(state, exported.csv_path)
        self.assertTrue(all(r['thermal_level'] is None for r in unavailable['runs'].values()))
        self.assertIsNone(unavailable['runs'][first]['stream_s'])
        cpu_receipt = self.session/'receipts/cpu_contention.json'
        bad_cpu = h.read(cpu_receipt)
        bad_cpu['values']['w_j_per_cpu_s'] = 'NaN'
        h.write(cpu_receipt, bad_cpu)
        invalid = h.measurements(state, exported.csv_path)
        self.assertIsNone(invalid['cpu_contention']['w_j_per_cpu_s'])
        self.assertIn('records.measurement_source_unreadable', [f['code'] for f in unavailable['flags']])

    def test_prepare_to_real_nonclaim_harvest_to_measurements_to_gates(self):
        state = self.prepared()
        self.seed_collection(state)
        # Actual CLI subprocesses: real harvest, acceptance and native export,
        # then real bytes_gates. The seed intentionally lacks this session's
        # calibration/floor receipts: unavailable C5 is the truthful outcome.
        def real_child(argv, **kwargs):
            # Four independent synthetic member assessments, using the CLI's
            # existing pool. No harvest/acceptance/export result is stubbed.
            if 'harvest_b6_session.py' in Path(argv[1]).name:
                argv = [*argv, '--workers', '4']
            return subprocess.run(argv, **kwargs)
        with redirect_stdout(io.StringIO()):
            result = h.desk(self.session, run=real_child)
        self.assertEqual(result['harvest_exit'], 0)
        self.assertEqual(result['gates_exit'], 1)
        measured = h.read(self.session / 'MEASUREMENTS.json')
        self.assertEqual(len(measured['runs']), 123)
        self.assertTrue(measured['non_claim'])
        self.assertTrue(measured['flags'])
        self.assertIsNone(measured['regimes']['qwen3-8b-8bit']['F_min_j'])
        self.assertFalse((self.session / 'private').exists())
        self.assertIn('--non-claim', result['harvest_argv'])
        with Path(result['export']['csv']).open(newline='') as stream:
            exported = list(csv.DictReader(stream))
        self.assertEqual(len(exported), 123)
        self.assertTrue(all(r['non_claim'] == 'True' and r['pack_id'] == h.PACK_ID for r in exported))
        self.assertEqual(measured['session_id'], exported[0]['session_id'])
        self.assertGreater(sum(r['retained_bytes'] for r in measured['runs'].values()), 0)


class ReceiptMathTests(unittest.TestCase):
    def test_cpu_counts_whole_native_request_overlap_quanta_without_prorating(self):
        journal = [{'values': {'interval': {'monotonic_ns': [0,10**9]}, 'outside_total_cpu_s_per_s': .2, 'elapsed_s': 1}},
                   {'values': {'interval': {'monotonic_ns': [10**9,2*10**9]}, 'outside_total_cpu_s_per_s': .4, 'elapsed_s': 1}}]
        cpu, count = h.cpu_overlap(journal, 5*10**8, 15*10**8)
        self.assertEqual(count, 2)
        self.assertTrue(math.isclose(cpu, .6, rel_tol=1e-6, abs_tol=1e-6))
        self.assertEqual(h.cpu_overlap(journal[:1], 0,2*10**9), (None,None))
        self.assertEqual(h.cpu_overlap(journal*2, 0,2*10**9), (None,None))

    def test_paired_stream_includes_idle_and_never_uses_request_or_calibration(self):
        meta = {'uncertainty_evidence': {'clock_anchor': {'clock_stamps': {
            'pre_spawn': {'monotonic_before_s': 10}, 'post_parse': {'monotonic_after_s': 110},
            'sampling_started': {'monotonic_before_s': 90}, 'sampling_stopped': {'monotonic_after_s': 100}}}}}
        self.assertTrue(math.isclose(h.clock_span(meta), 100, rel_tol=1e-6, abs_tol=1e-6))
        self.assertIsNone(h.clock_span({}))


if __name__ == '__main__':
    unittest.main()
