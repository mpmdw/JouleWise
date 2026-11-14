"""Desk release guard (desk-leak audit 2026-11-13): before release a C/T desk prints and records no member's
energy, score, task outcome, tool structure or battery discharge; W1 seals its configured minimum.

Synthetic only: the pilot-4 native fixture (fake MLX, synthetic GPU samples) builds the bundles; the values
planted here are distinctive and must never reach stdout, PILOT.json or desk.json before release.
"""
import copy
import csv
import hashlib
import io
import json
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import km003c, light_triage, v4_battery, v4_contention, v4_desk_seal as seal, v4_registration
from joulewise.align.apple import thermal_desk
from joulewise.align.apple.workload import read_episode_bundle
from scripts import align_pilot_session as pilot, align_v4_series as series, align_v4_session as session
from scripts import align_v4_kit as kit, align_v4_thermal_desk as v4_thermal
from tests.align.test_pilot4 import native

GPU = 'powermetrics:gpu_power'
CPU = 'powermetrics:cpu_power'
FORBIDDEN_KEYS = ('residual_j', 'predicted_j', 'score', 'joules', 'per_turn_j', 'tool_names_per_turn', 'bank_stage',
                  'state_changing_calls', 'episode_seconds', 'side_task_success', 'main_task_score',
                  'battery_discharge')
# (seed, condition, label, pair, pool_role); ordinals follow the order.
CASES = ((1, 'benign', 'e01', 'spam_filter_update', 'calibration'), (2, 'benign', 'e02', 'spam_filter_update', 'calibration'),
         (3, 'sabotage', 'e03', 'spam_filter_update', 'calibration'), (1, 'benign', 'e04', 'bank_transfer_2', 'calibration'),
         (2, 'benign', 'e05', 'bank_transfer_2', 'sentinel'), (3, 'sabotage', 'e06', 'bank_transfer_2', 'calibration'))


def plant(i):
    """Distinctive per-member values (index ``i``); each str() must never print before release."""
    return {'gpu_j': 73519.86421357 + i, 'cpu_j': 42424.24242421 + i, 'turn_j': 31415.92653589 + i,
            'main': 0.86420975 + i / 1000, 'side': f'PLANTED_SIDE_{i}_QX', 'tool': f'planted_tool_{i}_zq',
            'bank': f'planted_bank_stage_{i}_zz', 'calls': 975318642 + i, 'seconds': 6543.21987 + i,
            'battery': 1357.92468 + i, 'dc': 2468.13579 + i, 'owned': 5551.23457 + i, 'gross': 5552.34568 + i,
            'latency': 913752468.0 + i, 'thermal_battery': 1212.34343 + i, 'u3_delta': 7777.12345,
            'arm': 3333.44445, 'warm': 909.090901 + i, 'tool_turn': 864213579 + i}


# RL-149 carve-out plants: (member index, where, flag). Truncation / heat-ended codes must never print per member.
CARVED = ((0, 'summary', 'episode.deadman:2'), (2, 'summary', 'turn_token_budget_reached:1'),
          (2, 'thermal', 'thermal.gate_timeout:G1:1'), (3, 'harvest', 'thermal.hold_timeout'))
KEPT = ((5, 'thermal', 'thermal.start_gate_timeout'), (0, 'harvest', 'meter.planted_instrument'))


class Fixture:
    """One synthetic six-member session (built once); each case rewrites only session.json."""

    def __init__(self, root):
        self.root = Path(root)
        self.runs = self.root / 'runs'
        self.rows = []
        for ordinal, (seed, condition, label, pair, pool) in enumerate(CASES, 1):
            bundle, status, _, _ = native(self.root / 'native' / label, seed=seed, condition=condition, pair=pair)
            assert status.status.value == 'succeeded'
            trace = bundle / 'power_trace.csv'
            with trace.open() as stream:
                reader = csv.DictReader(stream)
                fields, samples = reader.fieldnames, list(reader)
            for sample in samples:
                sample.update(source='powermetrics', rail='gpu_power')
            with trace.open('w') as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(samples)
            run_id = 'align-v4-c3-' + label
            shutil.copytree(bundle, self.runs / run_id)
            expected = pilot.episode_summary(bundle)['sampler_seed_inputs']['episode_seed']
            self.rows.append({'run_id': run_id, 'task_pair': pair, 'condition': condition, 'repeat': 1,
                              'ordinal': ordinal, 'block': 'A', 'role': 'D', 'pool_role': pool, 'ac_powermode': 0,
                              'model_id': 'm', 'expected_episode_seed': expected})
        self.index = {r['run_id']: i for i, r in enumerate(self.rows)}
        self.nonbenign = {r['run_id'] for r in self.rows if r['condition'] != 'benign'}
        self.measurement = self.root / 'measurement'
        self.registration = self.measurement / 'kit/registration'
        (self.registration.parent).mkdir(parents=True, exist_ok=True)
        (self.registration.parent / 'collection_plan.json').write_text(json.dumps({'members': self.rows}))
        manifest = self.measurement / seal.SERIES_MANIFEST
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_bytes(b'{"synthetic": "series manifest"}\n')
        self.custody = self.root / 'custody'
        pilot.h.write(self.custody / 'night/result.json', {})
        pilot.h.write(self.root / 'plan.json', {'custody_root': str(self.custody)})
        self.thermals = {}
        for row in self.rows:
            ep = read_episode_bundle(self.runs / row['run_id'])
            self.thermals[row['run_id']] = {'readings_monotonic_ns_level': [[ep.start_ns - 1, 0], [ep.end_ns + 1, 0]]}

    def values(self, run_id=None):
        ids = [run_id] if run_id else list(self.index)
        return [plant(self.index[r]) for r in ids]

    def session(self, name, v4_series=None):
        root = self.root / 'sessions' / name
        root.mkdir(parents=True)
        state = {'session_id': 'align-v4-' + name, 'plan_path': str(self.root / 'plan.json'),
                 'measurement_root': str(self.measurement), 'source_measurement_root': str(self.measurement),
                 'registration_dir': str(self.registration), 'runs_roots': {'claim': str(self.runs)},
                 'inputs': {'custody_root': str(self.custody)}}
        if v4_series:
            state['v4_series'] = v4_series
        pilot.h.write(root / 'session.json', state)
        pilot.h.write(root / 'archive/derived/exclusions.json', {'members_excluded': []})
        pilot.h.write(root / 'archive/withheld/battery-assist.json',
                      {'members': {rid: {'discharge_j': plant(i)['battery']} for rid, i in self.index.items()}})
        rows = [{'code': flag, 'scope': {'run_id': self.rows[i]['run_id']}} for i, where, flag in CARVED + KEPT
                if where == 'harvest']
        (root / 'archive/derived/flags.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
        return root

    def planted_flags(self, run_id, where):
        return [flag for i, w, flag in CARVED + KEPT if w == where and self.rows[i]['run_id'] == run_id]

    # --- planted sources ------------------------------------------------------------------------
    def summary(self, original):
        def planted(bundle, **kwargs):
            out = original(bundle, **kwargs)
            v = plant(self.index[Path(bundle).name])
            gpu = out['energy'][GPU]
            gpu.update(joules=v['gpu_j'], segment_sum_j=v['gpu_j'], per_turn_j=[v['turn_j']])
            out['energy'][CPU] = {**copy.deepcopy(gpu), 'joules': v['cpu_j'], 'segment_sum_j': v['cpu_j'],
                                  'per_turn_j': [v['cpu_j']]}
            out['flags'] = [*out['flags'], *self.planted_flags(Path(bundle).name, 'summary')]
            out.update(main_task_score=v['main'], side_task_success=v['side'], bank_stage=v['bank'],
                       state_changing_calls=v['calls'], duration_s=v['seconds'],
                       tool_names_per_turn=[[v['tool']]])
            return out
        return planted

    def dc_report(self):
        return {'schema': 'joulewise.align_v4.km003c_secondary.v1', 'label': km003c.LABEL, 'print_only': True,
                'members': {r['run_id']: {**km003c._empty(), 'status': 'available', 'dc_in_energy_j': plant(i)['dc'],
                                          'dc_in_delta_j': plant(i)['dc'], 'dc_in_residual_j': plant(i)['dc'],
                                          'score': plant(i)['dc'], 'flags': []}
                            for i, r in enumerate(self.rows)},
                'models': [{'model': {'coef': [plant(0)['dc']]}}]}

    def record(self, path):
        run_id = Path(path).name
        v = plant(self.index[run_id])
        return {'id': run_id, 'gated': True, 'model': 'm',
                'flags': [f'thermal.planted:{v["seconds"]}', *self.planted_flags(run_id, 'thermal')],
                'tokens': [{'prompt_token_ids': [self.index[run_id]], 'output_token_ids': [v['calls']]}],
                'intervals': [], 'turn_observation': [{'os_nominal': True, 'pm_nominal': True, 'pm_max_gap_s': .1}],
                'coverage': [], 'pm_period_s': .1, 'pm_max_gap_s': .1, 'calibration_exclusions': [],
                'turn_owned_j': v['owned'], 'gross_episode_j': v['gross'], 'gross_latency_s': v['latency'],
                'status': 'completed', 'turns': 4, 'x_flags': [],
                'configuration': {'max_turns': 8}, 'cohort_identity': {'model_source': 'synthetic'}}

    def window_report(self, records, **_):
        window = records[0]['window']
        return {'schema': 'joulewise.align.thermal_desk.v1',
                'model_windows': {f'm/{window}': {
                    'U1': {'status': 'pass', 'thermal_excluded_members': []},
                    'U2': {'status': 'pass', 'g0_slow_range_c': 61.23456789},
                    'U3': {'status': 'pass', 'pairs': [{'status': 'pass', 'token_identical': True,
                                                        'delta_j': plant(0)['u3_delta']}]},
                    'U4': {'status': 'inconclusive'}, 'U5': {'status': 'inconclusive'}, 'U6': {'status': 'inconclusive'},
                    'hardware_control': 'pass', 'monitoring_calibration': 'inconclusive', 'consequence': 'under control'}},
                'deciding_experiment': {'arm_effect_j': plant(0)['arm']}, 'members': records,
                'tool_call_flags': {'members': [{'id': r['id'], 'malformed_json_turns': [plant(self.index[r['id']])['tool_turn']]}
                                                for r in records],
                                    'turn_totals': {'malformed_json_turns': len(records)}}}

    def diagnostics(self, records, **_):
        window = records[0]['window']
        return {'sentinel': {'ordinal': None, 'candidates': {}},
                'battery_windows': {f'm/{window}': {
                    'B_count': 0, 'unobserved_count': 0, 'assist_count': 0, 'assist_outside_request_count': 0,
                    'bar_pass': True, 'status': 'pass', 'consequence': 'retain',
                    'no_assist_sensitivity': {'status': 'print_only', 'member_ids': [r['id'] for r in records]},
                    'members': [{'id': r['id'], **r['battery']} for r in records]}},
                'warm_reference': {'status': 'print_only', 'R_minus_R1_soak_c': {'slow': 1.5}, 'thermal.reference_warm': True,
                                   'wait_against_ordinal': [{'ordinal': r['ordinal'], 'G0_wait_s': 0,
                                                             'G1_wait_s': plant(self.index[r['id']])['warm']}
                                                            for r in records]},
                'no_rebuild_sensitivity': {'status': 'print_only', 'member_ids': [r['id'] for r in records]},
                'd_cohort': {'instrument_ok': True},
                'rebuilds': [{'id': r['id'], 'cache_statistics': {'rebuilds': r['turns']}} for r in records]}

    def battery(self, record, path, journal):
        v = plant(self.index[Path(path).name])
        record['battery'] = {'status': 'observed', 'discharge_j': v['thermal_battery'], 'flags': []}
        return record

    def run_desk(self, root, *, released=False):
        """Run the v4 desk (``harvest=False``) with planted sources; returns (stdout, PILOT, desk.json, output dir)."""
        with ExitStack() as stack:
            enter = stack.enter_context
            enter(patch.object(pilot, 'episode_summary', self.summary(pilot.episode_summary)))
            enter(patch('joulewise.align.apple.diagnostics.member_thermal_readings', return_value=self.thermals))
            enter(patch.object(session, 'bundle_ac_powermode', return_value=0))
            enter(patch.object(km003c, 'session_report', return_value=self.dc_report()))
            enter(patch.object(v4_thermal, 'registration_evidence', return_value=({'policy': {}}, {})))
            enter(patch.object(v4_thermal, 'enrich_record', side_effect=lambda record, path: record))
            enter(patch.object(v4_thermal, 'r1_soak_c', return_value={}))
            enter(patch.object(v4_thermal, 'contrast_predeclaration', return_value=None))
            enter(patch.object(thermal_desk, 'read_bundle_record', side_effect=self.record))
            enter(patch.object(thermal_desk, 'window_report', side_effect=self.window_report))
            enter(patch.object(v4_registration, 'desk_diagnostics', side_effect=self.diagnostics))
            enter(patch.object(v4_battery, 'attach', side_effect=self.battery))
            enter(patch.object(v4_contention, 'attach', side_effect=lambda r, path, journal: r.update(
                contention={'span_s': None, 'disclosed_codes': [], 'flags': []}) or r))
            enter(patch.object(kit, 'read_inputs', return_value={}))
            enter(patch.object(series, 'load', return_value={}))
            enter(patch.object(series, 'desk_row', side_effect=lambda manifest, wid, members, u_pass: {
                'window_id': wid, 'desk_eligible_benign': {'spam': 2, 'bank': 1}}))
            out = io.StringIO()
            with redirect_stdout(out):
                status = session.desk(root, harvest=False)
        output = Path(status['pilot']).parent
        return out.getvalue(), json.loads(Path(status['pilot']).read_text()), json.loads((output / 'desk.json').read_text()), output


def leaks(texts, values, keys=FORBIDDEN_KEYS):
    """The test's detector: every planted value or forbidden key found in any of ``texts``."""
    found = []
    for name, text in texts.items():
        for value in values:
            if str(value) in text:
                found.append((name, value))
        for key in keys:
            if f'"{key}"' in text:
                found.append((name, key))
    return found


def planted_values(values, fields=None):
    fields = fields or ('gpu_j', 'cpu_j', 'turn_j', 'main', 'side', 'tool', 'bank', 'calls', 'seconds', 'battery',
                        'dc', 'owned', 'gross', 'latency', 'thermal_battery', 'u3_delta', 'arm', 'warm', 'tool_turn')
    out = []
    for v in values:
        for f in fields:
            out.append(int(v[f]) if f == 'latency' else v[f])
    return sorted(set(out), key=str)


class ReleaseGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='jw-desk-guard-')
        cls.fx = Fixture(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def texts(self, printed, report, desk):
        return {'stdout': printed, 'PILOT.json': json.dumps(report, sort_keys=True),
                'desk.json': json.dumps(desk, sort_keys=True)}

    def assert_sealed(self, name, window):
        root = self.fx.session(name, {'window_id': window, 'role': 'calibration' if window.startswith('C') else 'test'})
        printed, report, desk, output = self.fx.run_desk(root)
        self.assertEqual(leaks(self.texts(printed, report, desk), planted_values(self.fx.values())), [])
        # Every printed member line and every recorded member carries only allowlisted keys.
        allowed = set(seal.MEMBER_ALLOWLIST) | {'withheld'}
        printed_members = 0
        for line in printed.splitlines():
            for rid in self.fx.index:
                if line.startswith(rid + ' harvest_flags: '):
                    self.assertLessEqual(set(json.loads(line.split(': ', 1)[1])), {'flag_codes', 'withheld'})
                elif line.startswith(rid + ': {'):
                    printed_members += 1
                    self.assertLessEqual(set(json.loads(line.split(': ', 1)[1])), allowed, line)
        self.assertEqual(printed_members, len(self.fx.rows))
        for member in report['members']:
            self.assertLessEqual(set(member), allowed)
            self.assertEqual(member['withheld']['status'], seal.WITHHELD)
        for key in ('residual_analysis', 'raw_within_cell_energy_sd', 'repeat_energy_spread', 'I4_prime'):
            self.assertEqual(report[key]['status'], seal.WITHHELD)
            self.assertEqual(len(report[key]['sha256']), 64)
        pooled = report['residual_analysis']['pooled']['scopes']['all_members_diagnostic']['counts_logged_headline']
        self.assertEqual(pooled['members_scored'], len(self.fx.rows))
        # The unsealed PILOT is kept for the release run, inside the withheld archive, and bound by digest.
        full_path = output / seal.WITHHELD_PILOT
        full = full_path.read_bytes()
        self.assertEqual(hashlib.sha256(full).hexdigest(), report['release_guard']['withheld_pilot_sha256'])
        self.assertIn(str(self.fx.values()[0]['gpu_j']).encode(), full)
        self.assertEqual(report['release_guard']['scope'], window[0])
        # What the finality predicate, the harvest-off ``final`` and the packet builder read survives.
        # (``--no-harvest`` records harvest_status not_run; a completed harvest's desk carries the same fields.)
        self.assertIsNone(light_triage.final_adjudication_error({**desk, 'harvest_status': 'ok'}, report,
                                                                {'members_excluded': []}, report['plan_id'],
                                                                captured=True))
        thermal = report['extra_checks']['thermal']
        eligibility = light_triage.member_eligibility(thermal['members'], self.fx.rows,
                                                      captured=set(self.fx.index), final=True)
        self.assertEqual(eligibility['status'], 'pass')
        self.assertEqual(light_triage.thermal_escalation(thermal)['status'], 'pass')
        tokens = {m['id']: m['tokens'] for m in thermal['members']}
        self.assertTrue(all(isinstance(t, str) and t.startswith('sha256:') for t in tokens.values()))
        self.assertTrue(report['extra_checks']['km003c']['members'][self.fx.rows[0]['run_id']]['sealed'])
        self.assertEqual(report['extra_checks']['balance_check']['status'], seal.WITHHELD)
        self.assertIn('full_desk_gate: ', printed)
        # RL-149 carve-out: truncation / heat-ended codes appear only as window counts over all members.
        self.assert_carved_only_as_counts(printed, report, desk, range(len(self.fx.rows)))
        self.assertEqual(report['carve_out_flag_counts']['counts'],
                         {'episode.deadman': 1, 'thermal.hold_timeout': 1, 'turn_token_budget_reached': 1})
        self.assertEqual(report['carve_out_flag_counts']['members'], len(self.fx.rows))
        self.assertEqual(thermal['carve_out_flag_counts']['counts'], {'thermal.gate_timeout': 1})
        by_id = {m['id']: m for m in thermal['members']}
        self.assertIn('thermal.start_gate_timeout', by_id[self.fx.rows[5]['run_id']]['flags'])  # G0 stays per member
        self.assertIn('meter.planted_instrument', printed)                                      # instrument codes stay
        for row in report['extra_checks']['d_member_x2']['members']:
            self.assertLessEqual(set(row), set(seal.X2_ROW_KEEP))
        self.assertIn('gate_timeout_x2_count', report['extra_checks']['d_member_x2'])
        return printed, report, desk

    def assert_carved_only_as_counts(self, printed, report, desk, indices):
        report = copy.deepcopy(report)
        report.pop('carve_out_flag_counts', None)
        thermal = (report.get('extra_checks') or {}).get('thermal') or {}
        thermal.pop('carve_out_flag_counts', None)
        texts = self.texts(printed, report, desk)
        for i, _where, flag in CARVED:
            if i in indices:
                code = flag.split(':')[0]
                self.assertEqual([name for name, text in texts.items() if code in text], [], code)

    def test_a_calibration_window_desk_prints_and_records_no_planted_value_or_key(self):
        self.assert_sealed('c3', 'C3')

    def test_a_test_window_desk_prints_and_records_no_planted_value_or_key(self):
        self.assert_sealed('t2', 'T2')

    def test_the_detector_fires_when_the_hook_is_removed(self):
        root = self.fx.session('c3-mutant', {'window_id': 'C3', 'role': 'calibration'})
        with patch.object(seal, 'desk_policy', return_value=None):
            printed, report, desk, _ = self.fx.run_desk(root)
        found = leaks(self.texts(printed, report, desk), planted_values(self.fx.values()))
        self.assertIn(('PILOT.json', self.fx.values()[0]['gpu_j']), found)
        self.assertIn(('stdout', self.fx.values()[0]['battery']), found)
        self.assertIn(('stdout', self.fx.values()[0]['tool']), found)
        for key in ('residual_j', 'battery_discharge', 'tool_names_per_turn'):
            self.assertIn(('stdout', key), found)
        self.assertIn(('PILOT.json', 'main_task_score'), found)

    def test_a_registered_release_event_opens_the_fields(self):
        measurement = self.fx.measurement
        record = {'schema': seal.SERIES_COMPLETE_SCHEMA, 'event': 'series_complete', 'last_admitted_test_window': 'T3',
                  'test_windows_final_eligibility': {'T1': 'final', 'T2': 'final', 'T3': 'final'},
                  'series_manifest_sha256': hashlib.sha256((measurement / seal.SERIES_MANIFEST).read_bytes()).hexdigest(),
                  'record_commit': 'a' * 40}
        raw = json.dumps(record).encode()
        complete, receipt = measurement / seal.SERIES_COMPLETE, measurement / seal.RELEASE_RECEIPT
        complete.write_bytes(raw)
        self.addCleanup(complete.unlink)
        good = {'schema': seal.RELEASE_RECEIPT_SCHEMA, 'release_run': True,
                'series_complete_sha256': hashlib.sha256(raw).hexdigest(), 'lead_signature': 'lead: synthetic 2027-01-01'}
        state = {'measurement_root': str(measurement)}
        # Fail closed: no receipt, an unsigned receipt, or a receipt for other bytes never releases.
        self.assertFalse(seal.released(state))
        for bad in ({**good, 'lead_signature': 'PENDING_LEAD_SIGNATURE'}, {**good, 'series_complete_sha256': '0' * 64},
                    {**good, 'release_run': False}):
            receipt.write_text(json.dumps(bad))
            self.assertFalse(seal.released(state), bad)
        receipt.write_text(json.dumps(good))
        self.addCleanup(receipt.unlink)
        self.assertTrue(seal.released(state))
        root = self.fx.session('c3-released', {'window_id': 'C3', 'role': 'calibration'})
        printed, report, desk, _ = self.fx.run_desk(root)
        found = leaks(self.texts(printed, report, desk), planted_values(self.fx.values()))
        self.assertIn(('PILOT.json', self.fx.values()[2]['gpu_j']), found)
        self.assertIn(('stdout', self.fx.values()[2]['battery']), found)
        self.assertIn(('stdout', 'residual_j'), found)
        self.assertNotIn('release_guard', report)

    def test_today_nothing_is_released(self):
        repo = Path(__file__).resolve().parents[2]
        self.assertFalse(seal.released({'measurement_root': str(repo)}))
        self.assertFalse((repo / seal.SERIES_COMPLETE).exists())
        self.assertFalse((repo / seal.RELEASE_RECEIPT).exists())

    def nonbenign_values(self):
        return [self.fx.values(r)[0] for r in sorted(self.fx.nonbenign)]

    def test_w1_switch_is_on_as_ruled_and_withholds_non_benign_outcomes(self):
        self.assertIs(seal.W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES, True)        # RL-149 section 3(a)
        root = self.fx.session('w1-on')
        printed, report, desk, _ = self.fx.run_desk(root)
        texts = self.texts(printed, report, desk)
        sabotage = self.nonbenign_values()
        self.assertEqual(leaks(texts, planted_values(sabotage, (
            'gpu_j', 'cpu_j', 'turn_j', 'main', 'side', 'tool', 'bank', 'calls', 'seconds', 'battery', 'dc', 'owned',
            'gross', 'latency', 'thermal_battery', 'warm', 'tool_turn')), keys=()), [])
        for configuration in report['residual_analysis']:
            for scope in configuration['scopes'].values():
                for label in ('counts_logged_headline', 'counts_withheld'):
                    for row in scope[label]['residuals']:
                        self.assertTrue(row.get('status') == seal.WITHHELD or row['run_id'] not in self.fx.nonbenign)
        nonbenign = {m['run_id'] for m in report['members'] if m['run_id'] in self.fx.nonbenign}
        for member in report['members']:
            if member['run_id'] in nonbenign:
                self.assertLessEqual(set(member), set(seal.MEMBER_ALLOWLIST) | {'withheld'})
        # The exception class prints as registered: the deciding contrast's statistics and U1-U6 (U3's |dE|).
        thermal = report['extra_checks']['thermal']
        self.assertEqual(thermal['deciding_experiment'], {'arm_effect_j': plant(0)['arm']})
        self.assertEqual(thermal['model_windows']['m/W1']['U3']['pairs'][0]['delta_j'], plant(0)['u3_delta'])
        self.assertEqual(report['release_guard']['scope'], 'W1')
        self.assertTrue(report['release_guard']['w1_withhold_sabotage_gpu_and_outcomes'])
        self.assertIn('deciding contrast (thermal.deciding_experiment)', report['release_guard']['w1_exceptions'])
        # Benign members and registered window counts still print.
        benign = [self.fx.values(r['run_id'])[0] for r in self.fx.rows if r['condition'] == 'benign']
        self.assertTrue(leaks(texts, planted_values(benign, ('battery', 'warm', 'tool_turn', 'main')), keys=()))
        self.assertIn('balance (R22-3): ' + seal.WITHHELD, printed)
        self.assertIn('m/W1 battery: ', printed)
        # Carve-out for the non-benign members; window counts over all members.
        self.assert_carved_only_as_counts(printed, report, desk,
                                          [i for i, r in enumerate(self.fx.rows) if r['run_id'] in self.fx.nonbenign])
        self.assertEqual(report['carve_out_flag_counts']['members'], len(self.fx.rows))
        for row in report['extra_checks']['d_member_x2']['members']:
            if row['run_id'] in self.fx.nonbenign:
                self.assertLessEqual(set(row), set(seal.X2_ROW_KEEP))
        for cell in report['I4_prime'].values():
            for row in cell['accounting']:
                if row['run_id'] in self.fx.nonbenign:
                    self.assertNotIn('turns', row)

    def test_w1_exception_list_names_protocol_lines_and_handling(self):
        names = [e['output'] for e in seal.W1_EXCEPTIONS]
        self.assertEqual(len(names), len(set(names)))
        for entry in seal.W1_EXCEPTIONS:
            self.assertEqual(set(entry), {'output', 'protocol', 'reads', 'in_class', 'handling'})
            self.assertTrue(entry['protocol'] and entry['handling'])
        in_class = {e['output'] for e in seal.W1_EXCEPTIONS if e['in_class']}
        self.assertIn('deciding contrast (thermal.deciding_experiment)', in_class)
        self.assertTrue({'U3 (thermal.model_windows[*].U3 pairs)', 'U4-U6'} <= in_class)

    def test_w1_switch_off_keeps_only_the_med4_minimum(self):
        root = self.fx.session('w1-min')
        with patch.object(seal, 'W1_WITHHOLD_SABOTAGE_GPU_AND_OUTCOMES', False):
            printed, report, desk, _ = self.fx.run_desk(root)
        texts = self.texts(printed, report, desk)
        sabotage = self.nonbenign_values()
        self.assertEqual(leaks(texts, planted_values(sabotage, ('cpu_j', 'battery', 'dc', 'thermal_battery')), keys=()), [])
        self.assertTrue(leaks({'stdout': printed}, planted_values(sabotage, ('main', 'tool')), keys=()))
        self.assertFalse(report['release_guard']['w1_withhold_sabotage_gpu_and_outcomes'])


class SealUnitTests(unittest.TestCase):
    def test_withheld_digest_is_the_canonical_json_sha256(self):
        value = {'b': [1, 2.5], 'a': 'x'}
        self.assertEqual(seal.withheld(value), {'status': seal.WITHHELD, 'sha256': hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()})

    def test_unknown_top_level_and_extra_keys_fail_closed(self):
        sealed = seal.seal_pilot({'plan_id': 'p', 'status': 'instrument_ok', 'checks': {}, 'members': [],
                                  'new_energy_table': {'x': 123.456}, 'extra_checks': {'new_rail': [9.87]}},
                                 [], 'C1')
        self.assertEqual(sealed['new_energy_table']['status'], seal.WITHHELD)
        self.assertEqual(sealed['extra_checks']['new_rail']['status'], seal.WITHHELD)
        self.assertNotIn('123.456', json.dumps(sealed))

    def test_scope_fails_closed_for_unknown_roles(self):
        self.assertEqual(seal.window_scope({}), 'W1')
        self.assertEqual(seal.window_scope({'v4_series': {'window_id': 'W1', 'role': 'selection'}}), 'W1')
        self.assertEqual(seal.window_scope({'v4_series': {'window_id': 'C9', 'role': 'calibration'}}), 'C')
        self.assertEqual(seal.window_scope({'v4_series': {'window_id': 'T4', 'role': 'test'}}), 'T')
        self.assertEqual(seal.window_scope({'v4_series': {'window_id': 'X1', 'role': 'other'}}), 'C')

    def test_the_v3_desk_default_is_identity(self):
        import inspect
        self.assertIsNone(inspect.signature(pilot.desk).parameters['print_policy'].default)


if __name__ == '__main__':
    unittest.main()
