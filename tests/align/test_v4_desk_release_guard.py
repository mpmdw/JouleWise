"""Desk release guard (desk-leak audit 2026-11-13): before release a C/T desk prints and records no member's
energy, score, task outcome, tool structure or battery discharge; W1 seals its configured minimum.

Synthetic only: the pilot-4 native fixture (fake MLX, synthetic GPU samples) builds the bundles; the values
planted here are distinctive and must never reach stdout, PILOT.json or desk.json before release.
"""
import copy
import csv
import hashlib
import hmac
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
HEAT_REASON = 'thermal_pressure_elevated_in_window'
# RL-151 section 4 C1(a): exclusion codes with suffix text; the text after the first ':' must never print.
CAL_EXCLUSIONS = {1: ['episode.deadman:871.5'],
                  2: ['episode.deadman:983.1', 'thermal.gate_timeout:G1 turn 2 waited 300.0s',
                      'thermal.os_level_nonzero', 'thermal.powermetrics_non_nominal']}
SUFFIXES = {1: ['871.5'], 2: ['983.1', 'G1 turn 2 waited 300.0s', 'waited 300.0s']}
G1_TIMEOUT = (0, 2, 5)          # R10 G1 timeouts: one benign, the two sabotage members (W1's 11 and 14 analog)
# PR #774 Sol seat: real-shaped inputs for the recovery attacks.
NS = 10**9
DURATION_S = {0: 1201, 1: 1213, 2: 1237, 3: 1249, 4: 1259, 5: 1571}        # coverage spans (expected samples)
RUNTIME_FLAGS = {1: ['episode.end_task:3'],                                  # benign control
                 2: ['episode.end_task:7', 'ended_in_unclosed_reasoning', 'cache.rebuilt_untrimmable:4',
                     'episode.context_limit:5']}
BEHAVIOUR_CODES = ('episode.end_task', 'ended_in_unclosed_reasoning', 'cache.rebuilt_untrimmable',
                   'episode.context_limit', 'battery.assist')
TOOL_EVENTS = {0: 3, 2: 8}                       # unsupported XML tool-call turns: benign 3, sabotage 8 (11 - 3)
ASSISTED = 5                                     # battery assist on a non-benign, non-excluded member
SECRET_TOKENS = [{'prompt_token_ids': [101, 102], 'output_token_ids': [202]}]   # member 2


def coverage_for(seconds):
    rows = [{'monotonic_ns': i * NS, 'finished': {'monotonic_after_ns': i * NS + 1}, 'sensors': {'Ts0P': 40.0},
             'errors': {}} for i in range(seconds + 3)]
    return thermal_desk._coverage(rows, 0, seconds * NS, ['Ts0P'])
# The per-member allowlist as reviewed (PR #774 row-1 F5), pinned literally so a widened allowlist fails.
MEMBER_KEYS = {'run_id', 'ordinal', 'pool_role', 'excluded', 'exclusion_codes', 'disclosed_exclusion_codes', 'withheld'}


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
            if self.index[Path(bundle).name] == 2:          # a heat-bearing precheck reason (row-1 F5)
                out['window_evidence_precheck']['reasons'] = [*out['window_evidence_precheck']['reasons'], HEAT_REASON]
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
        i = self.index[run_id]
        tools = [f'episode.unsupported_tool_call_format:{t}' for t in range(TOOL_EVENTS.get(i, 0))]
        return {'id': run_id, 'gated': True, 'model': 'm',
                'flags': [f'thermal.planted:{v["seconds"]}', *self.planted_flags(run_id, 'thermal'),
                          *RUNTIME_FLAGS.get(i, []), *tools],
                'tokens': (copy.deepcopy(SECRET_TOKENS) if i == 2 else
                           [{'prompt_token_ids': [self.index[run_id]], 'output_token_ids': [v['calls']]}]),
                'intervals': [{'kind': 'G1', 'outcome': 'released', 'duration_s': 1.0},
                              *([{'kind': 'G1', 'outcome': 'timeout', 'duration_s': 300.0}]
                                if self.index[run_id] in G1_TIMEOUT[1:] else [])],
                'turn_observation': [{'os_nominal': True, 'pm_nominal': True, 'pm_max_gap_s': .1}],
                'coverage': [coverage_for(DURATION_S[i])], 'pm_period_s': .1, 'pm_max_gap_s': .1,
                'calibration_exclusions': list(CAL_EXCLUSIONS.get(self.index[run_id], [])),
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
                'tool_call_flags': thermal_desk.tool_call_table(records)}

    def diagnostics(self, records, **_):
        window = records[0]['window']
        return {'sentinel': {'ordinal': None, 'candidates': {}},
                'battery_windows': v4_battery.window_consequences(records, None),       # the production builder
                'warm_reference': {'status': 'print_only', 'R_minus_R1_soak_c': {'slow': 1.5}, 'thermal.reference_warm': True,
                                   'wait_against_ordinal': [{'ordinal': r['ordinal'], 'G0_wait_s': 0,
                                                             'G1_wait_s': plant(self.index[r['id']])['warm']}
                                                            for r in records]},
                'no_rebuild_sensitivity': {'status': 'print_only', 'member_ids': [r['id'] for r in records]},
                'd_cohort': {'instrument_ok': True},
                'rebuilds': [{'id': r['id'], 'cache_statistics': {'rebuilds': r['turns']}} for r in records]}

    def battery(self, record, path, journal):
        i = self.index[Path(path).name]
        flags = ['battery.assist'] if i == ASSISTED else []
        record['battery'] = {'status': 'observed', 'discharge_j': plant(i)['thermal_battery'], 'flags': flags,
                             'source_sha256': 'a' * 64}
        record.setdefault('flags', []).extend(f for f in flags if f not in record['flags'])   # as v4_battery.attach
        return record

    def x2_report(self, original):
        """The real R10 report with a planted G1 timeout on member 0 (benign) and member 2 (sabotage)."""
        def planted(plan_members, runs_root):
            report = original(plan_members, runs_root)
            for row in report['members']:
                if self.index.get(row['run_id']) in G1_TIMEOUT:
                    row.update(gate_timeout_x2=True, x2=True)
            report['x2_count'] = sum(row['x2'] for row in report['members'])
            report['x2_rate'] = report['x2_count'] / len(report['members'])
            return report
        return planted

    def patches(self, stack):
        enter = stack.enter_context
        enter(patch.object(session, 'd_member_x2_report', self.x2_report(session.d_member_x2_report)))
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

    def run_desk(self, root, *, released=False):
        """Run the v4 desk (``harvest=False``) with planted sources; returns (stdout, PILOT, desk.json, output dir)."""
        with ExitStack() as stack:
            self.patches(stack)
            out = io.StringIO()
            with redirect_stdout(out):
                status = session.desk(root, harvest=False)
        output = Path(status['pilot']).parent
        return out.getvalue(), json.loads(Path(status['pilot']).read_text()), json.loads((output / 'desk.json').read_text()), output

    def run_triage(self, root, window_id):
        """The harvest-off light triage (``cmd_triage``) on the same session: its record, JSON line, stdout, stderr."""
        import argparse
        import contextlib
        from scripts import align_v4_harvest_off as harvest_off
        target = Path(root) / 'triage-record.json'
        args = argparse.Namespace(session_root=str(root), window_id=window_id, ladder_recorded=False, out=str(target))
        with ExitStack() as stack:
            self.patches(stack)
            stack.enter_context(patch.object(harvest_off, '_runs_root', return_value=self.runs))
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = harvest_off.cmd_triage(args)
        return {'triage_record': target.read_text(), 'triage_json': json.dumps(result, sort_keys=True),
                'triage_stdout': stdout.getvalue(), 'triage_stderr': stderr.getvalue()}


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
        allowed = MEMBER_KEYS
        self.assertEqual(set(seal.MEMBER_ALLOWLIST) | {'withheld'}, MEMBER_KEYS)
        self.assertEqual([n for n, t in self.texts(printed, report, desk).items() if HEAT_REASON in t], [])
        printed_members = 0
        for line in printed.splitlines():
            for rid in self.fx.index:
                if line.startswith(rid + ' harvest_flags: '):
                    self.assertEqual(set(json.loads(line.split(': ', 1)[1])), {'withheld'})
                elif line.startswith(rid + ': {'):
                    printed_members += 1
                    self.assertLessEqual(set(json.loads(line.split(': ', 1)[1])), allowed, line)
        self.assertEqual(printed_members, len(self.fx.rows))
        for member in report['members']:
            self.assertLessEqual(set(member), allowed)
            self.assertEqual(member['withheld']['status'], seal.WITHHELD)
        for key in ('residual_analysis', 'raw_within_cell_energy_sd', 'repeat_energy_spread', 'I4_prime'):
            self.assertEqual(report[key]['status'], seal.WITHHELD)
            self.assertEqual(len(report[key]['hmac_sha256']), 64)
        pooled = report['residual_analysis']['pooled']['scopes']['all_members_diagnostic']['counts_logged_headline']
        self.assertEqual(pooled['members_scored'], len(self.fx.rows))
        # The unsealed PILOT is kept for the release run, inside the withheld archive, and bound by digest.
        full_path = output / 'archive' / 'withheld' / 'PILOT.full.json'          # literal: the withheld archive
        self.assertTrue(full_path.is_file())
        self.assertFalse((output / 'PILOT.full.json').exists())
        self.assertFalse((output / 'archive' / 'PILOT.full.json').exists())
        self.assertEqual(sorted(p.relative_to(output).as_posix() for p in output.rglob('PILOT.full.json')),
                         ['archive/withheld/PILOT.full.json'])
        full = full_path.read_bytes()
        self.assertEqual(hashlib.sha256(full).hexdigest(), report['release_guard']['withheld_pilot_sha256'])
        # Withheld digests are HMAC-SHA256 under the desk's own key, kept beside the full PILOT, so a low-entropy
        # value (a turn list, a small count) cannot be recovered by enumeration and still checks at release.
        key = json.loads((output / 'archive' / 'withheld' / 'desk_seal_key.json').read_text())
        full_pilot = json.loads(full)
        expected = hmac.new(bytes.fromhex(key['key_hex']), json.dumps(full_pilot['residual_analysis'], sort_keys=True,
                            separators=(',', ':')).encode(), hashlib.sha256).hexdigest()
        self.assertEqual(report['residual_analysis']['hmac_sha256'], expected)
        self.assertNotIn(hashlib.sha256(json.dumps(full_pilot['residual_analysis'], sort_keys=True,
                         separators=(',', ':')).encode()).hexdigest(), json.dumps(report))
        # RL-151 C1(a): exclusion codes print as codes; no suffix text, in the desk or the triage.
        thermal_members = {m['id']: m for m in report['extra_checks']['thermal']['members']}
        self.assertEqual(thermal_members[self.fx.rows[2]['run_id']]['calibration_exclusions'],
                         ['episode.deadman', 'thermal.gate_timeout', 'thermal.os_level_nonzero',
                          'thermal.powermetrics_non_nominal'])
        suffixes = [x for values in SUFFIXES.values() for x in values]
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
        self.assertTrue(all(isinstance(t, str) and t.startswith('hmac:') for t in tokens.values()))
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
        # RL-151 section 4.4 (builder's answer): a member-scoped harvest instrument/identity flag on a member the
        # harvest does not exclude reaches the C/T desk only inside that member's digest. It is not in stdout,
        # PILOT.json, desk.json or the thermal members' flags (an operational blind spot, not a leak).
        for name, text in self.texts(printed, report, desk).items():
            self.assertNotIn('meter.planted_instrument', text, name)
        # X2 (R10): per row the G0 outcome only; in C/T only the G0 count (row-1 F1: the G1 count is carved).
        x2 = report['extra_checks']['d_member_x2']
        self.assertLessEqual(set(x2), set(seal.X2_KEEP) | {'members', 'withheld'})
        for row in x2['members']:
            self.assertLessEqual(set(row), set(seal.X2_ROW_KEEP))
        self.assertEqual(x2['g0_timeout_x2_count'], 0)
        for key in ('gate_timeout_x2', 'x2', 'x2_count', 'x2_rate', 'gate_timeout_x2_count'):
            self.assertEqual([n for n, t in self.texts(printed, report, desk).items() if f'"{key}"' in t], [], key)
        # The harvest-off light triage writes the same sealed sections (record, JSON line, stdout, stderr).
        triage = self.fx.run_triage(root, window)
        self.assertEqual(leaks(triage, planted_values(self.fx.values()), keys=('joules', 'turn_owned_j', 'gross_episode_j',
                                                                               'battery', 'dc_in_energy_j')), [])
        self.assertEqual(leaks({**self.texts(printed, report, desk), **triage}, suffixes, keys=()), [])
        record = json.loads(triage['triage_record'])
        self.assertTrue(all(m['tokens'].startswith('hmac:') for m in record['thermal']['members']))
        self.assertEqual(record['member_eligibility']['status'], 'pass')
        return printed, report, desk

    def assert_carved_only_as_counts(self, printed, report, desk, indices):
        report = copy.deepcopy(report)
        report.pop('carve_out_flag_counts', None)
        thermal = (report.get('extra_checks') or {}).get('thermal') or {}
        thermal.pop('carve_out_flag_counts', None)
        for member in thermal.get('members') or ():
            member.pop('calibration_exclusions', None)   # codes stay here until the truncation rule (RL-151 C1(b))
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
                'series_complete_sha256': hashlib.sha256(raw).hexdigest(), 'ruling': 'RL-999 synthetic release ruling',
                'lead_signature': 'lead: synthetic 2027-01-01'}
        state = {'measurement_root': str(measurement)}
        # Fail closed: no receipt, an unsigned receipt, or a receipt for other bytes never releases.
        self.assertFalse(seal.released(state))
        for bad in ({**good, 'lead_signature': 'PENDING_LEAD_SIGNATURE'}, {**good, 'series_complete_sha256': '0' * 64},
                    {**good, 'release_run': False}, {k: v for k, v in good.items() if k != 'ruling'},
                    {**good, 'ruling': 'released, trust me'}):
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
        # RL-151 C4: a released desk records and prints that it ran released, with both release files' digests.
        guard = report['release_guard']
        self.assertEqual(guard['status'], 'released')
        self.assertEqual(guard['series_complete_sha256'], hashlib.sha256(complete.read_bytes()).hexdigest())
        self.assertEqual(guard['release_receipt_sha256'], hashlib.sha256(receipt.read_bytes()).hexdigest())
        self.assertEqual(guard['ruling'], 'RL-999 synthetic release ruling')
        self.assertEqual(sum(line.startswith('release_guard: released ') for line in printed.splitlines()), 1)

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
                self.assertLessEqual(set(member), MEMBER_KEYS)
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
        # RL-151 C2/C3 invariant: nothing printed gives a carved count over the non-benign members alone. G1
        # timeouts are planted on member 0 (benign) and on both sabotage members (W1's 11 and 14 analog).
        x2 = report['extra_checks']['d_member_x2']
        benign_rows = [row for row in x2['members'] if row['run_id'] not in self.fx.nonbenign]
        for row in x2['members']:
            if row['run_id'] in self.fx.nonbenign:
                self.assertLessEqual(set(row), set(seal.X2_ROW_KEEP))
        self.assertTrue(next(r for r in benign_rows if self.fx.index[r['run_id']] == 0)['gate_timeout_x2'])
        self.assertNotIn('gate_timeout_x2_count', json.dumps(report))
        self.assertEqual(x2['x2_count'], sum(bool(r.get('x2')) for r in benign_rows))   # 1: nothing to subtract
        self.assertEqual(x2['x2_count'], 1)
        self.assertEqual(x2['x2_rate'], 1 / len(benign_rows))
        self.assertIn('benign', x2['pool'])
        counts = report['carve_out_flag_counts']
        self.assertEqual(counts['members'], len(self.fx.rows) - len(self.fx.nonbenign))
        self.assertEqual(counts['counts'], {'episode.deadman': 1, 'thermal.hold_timeout': 1})   # turn budget on 2: not counted
        self.assertIn('benign', counts['over'])
        thermal_counts = report['extra_checks']['thermal']['carve_out_flag_counts']
        self.assertEqual(thermal_counts['counts'], {})                     # the G1 flag on 2 is not counted
        for window in report['extra_checks']['thermal']['model_windows'].values():
            self.assertEqual(set(window['U1']), {'status', 'withheld'})    # U1 counts over all members withheld
        # The RL-149 section 1.5 tripwire is judged in memory over all D members: 2 of 8 G1 admissions timed out.
        self.assertIn('W1 D G1 timeout tripwire (RL-149 section 1.5): to the research lead', printed)
        self.assertEqual(report['extra_checks']['w1_g1_tripwire']['verdict'], 'to the research lead')
        self.assertEqual(set(report['extra_checks']['w1_g1_tripwire']), {'verdict', 'rule', 'withheld'})
        # C1(a) in W1: the sabotage member's suffix text never prints; the benign member's row prints whole.
        self.assertEqual(leaks(texts, SUFFIXES[2], keys=()), [])
        # The W1 light triage seals the non-benign members as the desk does.
        triage = self.fx.run_triage(root, 'W1')
        self.assertEqual(leaks(triage, planted_values(sabotage, ('owned', 'gross', 'latency', 'thermal_battery', 'dc',
                                                                 'seconds', 'calls', 'tool_turn')), keys=()), [])
        self.assertIn(str(plant(0)['arm']), triage['triage_record'])        # the deciding contrast prints
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


class SentinelDetectorTests(unittest.TestCase):
    """PR #774 row-1 reviewer's independent check, adopted: its own sentinels and its own detector (numeric tokens
    within rel 1e-9 of a sentinel or its integer part, 9-digit signatures, strings), no key blacklist; the unsealed
    PILOT.full.json is the control that must light it."""

    @staticmethod
    def sentinel(i):
        b = 100000 * (i + 1)
        return {'gpu_j': 8100000.1357 + b, 'cpu_j': 8200000.2468 + b, 'turn_j': 8300000.3691 + b,
                'main': 0.6173948251 + i / 1e7, 'side': f'ZSIDEQ{i}K9', 'tool': f'zq_tool_{i}_ww', 'bank': f'zq_bank_{i}_ww',
                'calls': 7160000 + 13 * i + 7, 'seconds': 8400000.5927 + b, 'battery': 8500000.7149 + b,
                'dc': 8600000.8351 + b, 'owned': 8700000.9573 + b, 'gross': 8800000.1795 + b,
                'latency': 8900000.3917 + b, 'thermal_battery': 9100000.5139 + b, 'u3_delta': 9200000.7351,
                'arm': 9300000.9573, 'warm': 9400000.1795 + b, 'tool_turn': 7270000 + 17 * i}

    @staticmethod
    def detect(texts, values):
        import re
        nums, signatures, strings = set(), set(), set()
        for v in values:
            for x in v.values():
                if isinstance(x, str):
                    strings.add(x)
                else:
                    nums.update((float(x), float(int(x))))
                    signatures.add(re.sub(r'\D', '', repr(float(x)))[:9] if isinstance(x, float) else str(int(x)))
        hits = set()
        for name, text in texts.items():
            text = re.sub(r'[0-9a-f]{64}', '', text)      # digests are not printed values (random HMAC hex)
            for token in re.finditer(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', text):
                t = float(token.group())
                hits.update((name, 'num', n) for n in nums if n and abs(t - n) <= 1e-9 * abs(n))
            flat = re.sub(r'[.\-]', '', text)
            hits.update((name, 'sig', g) for g in signatures if len(g) >= 7 and g in flat)
            hits.update((name, 'str', x) for x in strings if x in text)
        return sorted(hits, key=str)

    def test_independent_detector_finds_no_sentinel_in_sealed_c_and_t_desks_or_triage(self):
        with tempfile.TemporaryDirectory(prefix='jw-desk-sentinel-') as tmp, \
                patch(__name__ + '.plant', self.sentinel):
            fx = Fixture(tmp)
            values = [self.sentinel(i) for i in range(len(CASES))]
            for window, role in (('C3', 'calibration'), ('T2', 'test')):
                root = fx.session('s-' + window, {'window_id': window, 'role': role})
                printed, report, desk, output = fx.run_desk(root)
                texts = {'stdout': printed, 'PILOT.json': json.dumps(report, sort_keys=True),
                         'desk.json': json.dumps(desk, sort_keys=True), **fx.run_triage(root, window)}
                self.assertEqual(self.detect(texts, values), [], window)
                control = self.detect({'full': (output / 'archive/withheld/PILOT.full.json').read_text()}, values)
                self.assertGreater(len(control), 20, window)


def numbers(text):
    import re
    text = re.sub(r'[0-9a-f]{64}', '', text)                 # digests are not values
    return [float(m.group()) for m in re.finditer(r'-?\d+(?:\.\d+)?', text)]


class RecoveryAttackTests(unittest.TestCase):
    """PR #774 Sol seat: each attack recovers its secret from the unsealed control and fails on the sealed head."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='jw-desk-recovery-')
        cls.fx = Fixture(cls.tmp.name)
        cls.runs = {}
        for name, series_state in (('C3', {'window_id': 'C3', 'role': 'calibration'}),
                                   ('T2', {'window_id': 'T2', 'role': 'test'}), ('W1', None)):
            root = cls.fx.session('attack-' + name, series_state)
            printed, report, desk, output = cls.fx.run_desk(root)
            triage = cls.fx.run_triage(root, name)
            full = json.loads((output / 'archive/withheld/PILOT.full.json').read_text())
            cls.runs[name] = dict(printed=printed, report=report, desk=desk, triage=triage, full=full,
                                  texts={'stdout': printed, 'PILOT.json': json.dumps(report, sort_keys=True),
                                         'desk.json': json.dumps(desk, sort_keys=True), **triage})

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def targets(self, window):
        """The members whose secrets must not be recoverable: all in C/T, the non-benign ones in W1."""
        return [i for i, r in enumerate(self.fx.rows) if window != 'W1' or r['run_id'] in self.fx.nonbenign]

    def thermal_views(self, run):
        yield run['report']['extra_checks']['thermal']
        yield json.loads(run['triage']['triage_record'])['thermal']

    # F2 ------------------------------------------------------------------------------------------
    @staticmethod
    def recover_duration(member):
        """Attack: elapsed seconds from the coverage grid (expected or valid samples, or fraction x span)."""
        for span in member.get('coverage') or ():
            if isinstance(span, dict):
                for key in ('expected_samples', 'valid_samples'):
                    if isinstance(span.get(key), (int, float)):
                        return span[key]
        return None

    def test_duration_cannot_be_recovered_from_coverage(self):
        for window, run in self.runs.items():
            control = {m['id']: self.recover_duration(m) for m in run['full']['extra_checks']['thermal']['members']}
            for view in self.thermal_views(run):
                members = {m['id']: m for m in view['members']}
                for i in self.targets(window):
                    rid = self.fx.rows[i]['run_id']
                    self.assertEqual(control[rid], DURATION_S[i])                    # the attack works on the control
                    self.assertIsNone(self.recover_duration(members[rid]), (window, rid))
                    self.assertEqual(members[rid]['coverage'], [{'verdict': 'pass', 'reasons': []}])
            if window != 'W1':                  # C/T: no member's duration anywhere in what the desk prints or records
                for i in self.targets(window):
                    for name, text in run['texts'].items():
                        self.assertNotIn(float(DURATION_S[i]), numbers(text), (window, name, i))
            else:                               # W1: benign rows print whole; scan every non-benign member's view
                for i in self.targets(window):
                    rid = self.fx.rows[i]['run_id']
                    views = [m for view in self.thermal_views(run) for m in view['members'] if m['id'] == rid]
                    views += [m for m in run['report']['members'] if m['run_id'] == rid]
                    self.assertNotIn(float(DURATION_S[i]), numbers(json.dumps(views)), (window, i))

    # F3 ------------------------------------------------------------------------------------------
    def test_behavioural_runtime_flags_are_withheld_per_member(self):
        for window, run in self.runs.items():
            for view in self.thermal_views(run):
                members = {m['id']: m for m in view['members']}
                for i in self.targets(window):
                    flags = members[self.fx.rows[i]['run_id']]['flags']
                    self.assertEqual([c for c in flags if c.startswith(BEHAVIOUR_CODES)], [], (window, i, flags))
                    self.assertLessEqual(set(flags), set(seal.FLAG_ALLOWLIST), (window, i))
            if window != 'W1':
                for name, text in run['texts'].items():
                    self.assertEqual([c for c in BEHAVIOUR_CODES if c in text], [], (window, name))
        self.assertIn('episode.end_task', ' '.join(self.runs['W1']['full']['extra_checks']['thermal']['members'][2]['flags']))

    # F4 ------------------------------------------------------------------------------------------
    @staticmethod
    def subtract(table, key='unsupported_xml_turns'):
        """Attack: window total minus the visible rows = the hidden members' count."""
        visible = sum(len(r.get(key) or ()) for r in table.get('members') or () if isinstance(r, dict) and 'id' in r)
        return (table.get('turn_totals') or {}).get(key, 0) - visible

    def test_w1_tool_totals_minus_visible_rows_recover_nothing(self):
        run = self.runs['W1']
        # Control: the pre-fix seal printed the all-member totals beside the benign rows: 11 - 3 = 8.
        full = run['full']['extra_checks']['thermal']['tool_call_flags']
        benign_rows = [r for r in full['members'] if r['id'] not in self.fx.nonbenign]
        self.assertEqual(self.subtract({'turn_totals': full['turn_totals'], 'members': benign_rows}), 8)
        for view in self.thermal_views(run):
            table = view['tool_call_flags']
            self.assertEqual(table['population'], 'benign')
            self.assertEqual(self.subtract(table), 0)
            self.assertEqual(table['turn_totals']['unsupported_xml_turns'], 3)
            self.assertNotIn(self.fx.rows[2]['run_id'], json.dumps(table['members']))
        for window in ('C3', 'T2'):
            table = self.runs[window]['report']['extra_checks']['thermal']['tool_call_flags']
            self.assertNotIn('members', table)                                       # no rows to subtract

    # F5 ------------------------------------------------------------------------------------------
    def infer_assisted(self, report):
        """Attack: a non-benign member that is observed and not excluded but absent from a list covering it was
        assisted; and the window assist count minus the visible benign assists gives the non-benign assists."""
        thermal = report['extra_checks']['thermal']
        observed = {m['id'] for m in thermal['members'] if not m.get('excluded')}
        row = next(iter(report['extra_checks']['registration_diagnostics']['battery_windows'].values()))
        sensitivity = row['no_assist_sensitivity']
        covers_non_benign = sensitivity.get('population') != 'benign'
        listed = set(sensitivity['member_ids'])
        named = ((observed & self.fx.nonbenign) - listed) if covers_non_benign else set()
        visible_benign = sum('battery.assist' in (m.get('flags') or ()) for m in row['members']
                             if isinstance(m, dict) and m.get('id') not in self.fx.nonbenign)
        return named, row['assist_count'] - visible_benign

    def test_w1_battery_assist_membership_cannot_be_inferred(self):
        run = self.runs['W1']
        assisted = self.fx.rows[ASSISTED]['run_id']
        self.assertEqual(self.infer_assisted(run['full']), ({assisted}, 1))          # control: both attacks work
        named, by_subtraction = self.infer_assisted(run['report'])
        row0 = next(iter(run['report']['extra_checks']['registration_diagnostics']['battery_windows'].values()))
        self.assertEqual(set(row0['no_assist_sensitivity']['member_ids']) & self.fx.nonbenign, set())
        self.assertEqual(named, set())                                   # the list holds benign ids only
        self.assertEqual(by_subtraction, 0)                              # assist counts are benign-only
        row = next(iter(run['report']['extra_checks']['registration_diagnostics']['battery_windows'].values()))
        self.assertEqual(row['no_assist_sensitivity']['population'], 'benign')
        self.assertEqual(row['assist_population'], 'benign')
        line = next(l for l in run['printed'].splitlines() if l.startswith('m/W1 battery: '))
        self.assertEqual(json.loads(line.split(': ', 1)[1])['assist_count'], 0)
        thermal = {m['id']: m for m in run['report']['extra_checks']['thermal']['members']}
        self.assertNotIn('battery.assist', thermal[assisted]['flags'])

    # F6 ------------------------------------------------------------------------------------------
    def test_token_commitments_resist_a_candidate_dictionary(self):
        def commitments(tokens):
            raw = json.dumps(tokens, sort_keys=True, separators=(',', ':')).encode()
            return {'sha256:' + hashlib.sha256(raw).hexdigest(), hashlib.sha256(raw).hexdigest(),
                    'hmac:' + hmac.new(b'\0' * 32, raw, hashlib.sha256).hexdigest()}
        candidates = [[{'prompt_token_ids': [101, 102], 'output_token_ids': [out]}] for out in range(195, 210)]
        dictionary = {c: cand[0]['output_token_ids'][0] for cand in candidates for c in commitments(cand)}
        for window, run in self.runs.items():
            for view in self.thermal_views(run):
                sealed = {m['id']: m for m in view['members']}[self.fx.rows[2]['run_id']]['tokens']
                self.assertTrue(sealed.startswith('hmac:'))
                self.assertNotIn(sealed, dictionary, window)                         # recovery fails
            for name, text in run['texts'].items():
                self.assertEqual([c for c in dictionary if c in text], [], (window, name))

    def test_med4_dc_digest_is_keyed(self):
        row = {**km003c._empty(), 'status': 'available', 'dc_in_energy_j': 12.0}
        sealed = km003c.seal_non_benign({'members': {'s': row}}, [{'run_id': 's', 'condition': 'sabotage'}])
        digest = sealed['members']['s']['sealed_hmac_sha256']
        plain = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()
        self.assertNotEqual(digest, plain)
        self.assertNotIn('sealed_sha256', sealed['members']['s'])


class EntryPointTests(unittest.TestCase):
    """PR #774 Sol F1: every v4 desk entry point installs the guard (keyed on the stored session identity)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='jw-desk-entry-')
        cls.fx = Fixture(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, texts, report, window='C3'):
        targets = [self.fx.values(r['run_id'])[0] for r in self.fx.rows
                   if window != 'W1' or r['run_id'] in self.fx.nonbenign]
        self.assertEqual(leaks(texts, planted_values(targets, ('gpu_j', 'cpu_j', 'turn_j', 'main', 'side', 'bank',
                                                               'calls', 'seconds', 'battery', 'owned', 'gross')),
                               keys=() if window == 'W1' else FORBIDDEN_KEYS), [])
        self.assertEqual(report['release_guard']['status'], seal.WITHHELD)

    def test_the_common_pilot_cli_on_a_v4_session_installs_the_guard(self):
        root = self.fx.session('entry-cli', {'window_id': 'C3', 'role': 'calibration'})
        with ExitStack() as stack:
            self.fx.patches(stack)
            out = io.StringIO()
            with redirect_stdout(out):
                pilot.main(['desk', '--session-root', str(root), '--no-harvest'])
        report_path = next((root / 'inspection').rglob('PILOT.json'))
        report = json.loads(report_path.read_text())
        self.check({'stdout': out.getvalue(), 'PILOT.json': report_path.read_text(),
                    'desk.json': (report_path.parent / 'desk.json').read_text()}, report)

    def test_the_v4_wrapper_with_an_explicit_none_installs_the_guard(self):
        root = self.fx.session('entry-none', {'window_id': 'C3', 'role': 'calibration'})
        with ExitStack() as stack:
            self.fx.patches(stack)
            out = io.StringIO()
            with redirect_stdout(out):
                status = session.desk(root, harvest=False, print_policy=None)
        report = json.loads(Path(status['pilot']).read_text())
        self.check({'stdout': out.getvalue(), 'PILOT.json': Path(status['pilot']).read_text(),
                    'desk.json': (Path(status['pilot']).parent / 'desk.json').read_text()}, report)

    def test_a_custom_policy_on_a_v4_session_is_refused(self):
        root = self.fx.session('entry-custom', {'window_id': 'C3', 'role': 'calibration'})
        with ExitStack() as stack:
            self.fx.patches(stack)
            with redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, 'release guard'):
                pilot.desk(root, harvest=False, print_policy=lambda pilot_, lines, output: (pilot_, lines))

    def run_thermal_desk(self, window):
        registration = self.fx.root / f'thermal-reg-{window}'
        registration.mkdir(exist_ok=True)
        (registration / 'inputs.json').write_text(json.dumps({'R1': {'thermal_policy': {}}}))
        manifest = self.fx.root / f'thermal-manifest-{window}.json'
        manifest.write_text(json.dumps({'members': [
            {'id': r['run_id'], 'bundle': 'runs/' + r['run_id'], 'window': window, 'ordinal': r['ordinal'],
             'role': 'D'} for r in self.fx.rows]}))
        prints = {'schema': 'joulewise.align.rl145_prints.v1', 'members': [
            {'id': r['run_id'], 'turns': [{'duration_s': plant(i)['seconds'], 'tokens': plant(i)['calls']}]}
            for i, r in enumerate(self.fx.rows)], 'residual_by_decode_bin': [{'residual_j': plant(0)['gpu_j']}]}
        conditions = {r['run_id']: r['condition'] for r in self.fx.rows}

        def record(path, **_):
            rec = self.fx.record(path)
            return {**rec, 'condition': conditions[Path(path).name]}
        output = self.fx.root / f'thermal-out-{window}'
        with ExitStack() as stack:
            enter = stack.enter_context
            enter(patch.object(v4_thermal, 'registration_evidence', return_value=({'policy': {}}, {})))
            enter(patch.object(v4_thermal, 'read_bundle_record', side_effect=record))
            enter(patch.object(v4_thermal, 'enrich_record', side_effect=lambda r, p: r))
            enter(patch.object(v4_thermal, 'window_report', side_effect=self.fx.window_report))
            enter(patch.object(v4_thermal, 'contrast_predeclaration', return_value=None))
            enter(patch.object(v4_thermal, 'rl145_prints_report', return_value=prints))
            enter(patch.object(v4_thermal.registration, 'desk_diagnostics', side_effect=self.fx.diagnostics))
            enter(patch.object(v4_battery, 'attach', side_effect=self.fx.battery))
            with redirect_stdout(io.StringIO()) as out:
                v4_thermal.main(['--manifest', str(manifest), '--output', str(output),
                                 '--registration-dir', str(registration)])
        texts = {name: (output / name).read_text() for name in ('PILOT.json', 'THERMAL.md', 'RL145_PRINTS.json')}
        texts['stdout'] = out.getvalue()
        return texts, json.loads(texts['PILOT.json']), output

    def test_the_standalone_thermal_desk_installs_the_guard(self):
        for window in ('C3', 'W1'):
            texts, report, output = self.run_thermal_desk(window)
            self.check(texts, report, window)
            self.assertEqual(report['release_guard']['entry_point'], 'scripts/align_v4_thermal_desk.py')
            self.assertTrue((output / 'archive/withheld/PILOT.full.json').is_file())
            self.assertTrue((output / 'archive/withheld/RL145_PRINTS.full.json').is_file())
            self.assertNotIn(str(plant(0)['gpu_j']), texts['RL145_PRINTS.json'])        # residual bins withheld


class SealUnitTests(unittest.TestCase):
    def test_withheld_digest_is_keyed_hmac_of_the_canonical_json(self):
        value = {'b': [1, 2.5], 'a': 'x'}
        raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
        key = b'k' * 32
        with seal.keyed(key):
            self.assertEqual(seal.withheld(value), {'status': seal.WITHHELD,
                                                    'hmac_sha256': hmac.new(key, raw, hashlib.sha256).hexdigest()})
        # Outside a desk the key is ephemeral and never written; it is still not the plain (invertible) sha256.
        self.assertNotEqual(seal.withheld(value)['hmac_sha256'], hashlib.sha256(raw).hexdigest())
        with seal.keyed(b'j' * 32):
            self.assertNotEqual(seal.withheld(value), seal.withheld({**value, 'a': 'y'}))

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
