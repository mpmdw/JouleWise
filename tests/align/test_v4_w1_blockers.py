"""Prospective W1 blocker contract; entirely synthetic, no hardware probes."""
from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_registration as reg
from tests.align.v4_registration_fixtures import export, signed_bar, battery_policy


class U3Tests(unittest.TestCase):
    def test_source_export_report_and_gate_are_bound_to_same_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = export()
            report = root/'transfer.md'
            report.write_text('Synthetic transfer justification\n')
            data['policy']['transfer_justification_sha256'] = reg.digest(report.read_bytes())
            source = root/'pairs.json'
            source.write_text(json.dumps(data))
            from scripts import align_v4_u3_bar as cli
            draft, adopted = root/'draft.json', root/'bar.json'
            with patch.object(cli, 'ROOT', root):
                self.assertEqual(cli.main(['--input', str(source), '--supporting-source', str(report),
                                           '--output', str(draft)]), 0)
            bar = json.loads(draft.read_bytes())
            gate = root/'docs/align/v4/gate.json'
            gate.parent.mkdir(parents=True)
            gate.write_text(json.dumps({'verdict': 'ADMIT', 'derivation_sha256': bar['derivation_sha256']}))
            with patch.object(cli, 'ROOT', root):
                argv = ['--adopt-draft', str(draft), '--gate', str(gate),
                        '--lead-signature', 'lead: synthetic 2026-11-08', '--output', str(adopted)]
                self.assertEqual(cli.main(argv), 0)
                with self.assertRaises(FileExistsError):
                    cli.main(argv)
            bar = json.loads(adopted.read_bytes())
            original_gate = gate.read_bytes()
            gate.write_text(json.dumps({'verdict': 'REFUSE', 'derivation_sha256': bar['derivation_sha256']}))
            forged = deepcopy(bar)
            forged['independent_gate']['sha256'] = reg.digest(gate.read_bytes())
            with self.assertRaisesRegex(ValueError, 'gate bytes'):
                reg.validate_u3(forged, root=root)
            gate.write_bytes(original_gate)
            def git(*args):
                return subprocess.run(['git', *args], cwd=root, capture_output=True, check=True).stdout.decode().strip()
            git('init', '-q')
            git('add', '.')
            git('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                'commit', '-qm', 'synthetic source custody')
            commit = git('rev-parse', 'HEAD')
            reg.validate_u3(bar, root=root, commit=commit)
            for path in (source, report, gate):
                original = path.read_bytes()
                path.write_bytes(original+b'drift')
                with self.subTest(path=path.name), self.assertRaises(ValueError):
                    reg.validate_u3(bar, root=root, commit=commit)
                path.write_bytes(original)
            with self.assertRaises(ValueError):
                reg.validate_u3(bar, root=root, commit='0'*40)

    def test_predictive_quantiles_against_closed_form_and_small_sample(self):
        from joulewise.align.apple.v4_u3 import critical
        self.assertAlmostEqual(critical(.05, 1), 1/math.tan(math.pi*.05/2), places=9)
        z = .95
        self.assertAlmostEqual(critical(.05, 2), math.sqrt(2)*z/math.sqrt(1-z*z), places=9)
        self.assertGreater(critical(.05/16, 2)*math.sqrt(1+1/3),
                           critical(.05/16, 6)*math.sqrt(1+1/7))

    def test_signed_predictive_derivation_accepts_and_scales(self):
        bar = signed_bar()
        self.assertIs(reg.validate_u3(bar), bar)
        self.assertGreater(reg.u3_margin(30000, bar, population='D'), 0)
        self.assertAlmostEqual(reg.u3_margin(60000, bar, population='D'),
                               2*reg.u3_margin(30000, bar, population='D'))
        self.assertEqual(bar['prediction']['df'], 6)
        self.assertEqual(bar['prediction']['series_comparisons'], 16)
        self.assertGreater(bar['prediction']['t_critical'], 3.)
        self.assertTrue(bar['oc']['scenarios'])

    def test_d_replay_checks_target_identity_battery_and_frozen_window_scope(self):
        from tests.align.test_thermal_desk import member
        from joulewise.align.apple import thermal_desk
        a, b = member('a', energy=30000), member('b', energy=30030)
        for row in (a, b):
            row.update(role='D', window='W1', identical_work_group='same', u3_configuration_sha256='b'*64)
        bar = signed_bar()
        self.assertEqual(thermal_desk.identical_pair(a, b, u3_bar=bar)['status'], 'pass')
        b['u3_configuration_sha256'] = 'e'*64
        self.assertEqual(thermal_desk.identical_pair(a, b, u3_bar=bar)['status'], 'inconclusive')
        b['u3_configuration_sha256'] = 'b'*64
        b['calibration_exclusions'] = ['battery.member_span']
        self.assertEqual(thermal_desk.identical_pair(a, b, u3_bar=bar)['status'], 'inconclusive')
        b['calibration_exclusions'] = []
        a['window'] = b['window'] = 'UNREGISTERED'
        result = thermal_desk.window_report([a, b], v4=True, u3_bar=bar)['model_windows']['synthetic/UNREGISTERED']
        self.assertEqual(result['U3']['status'], 'inconclusive')
        self.assertIn('scope', result['U3']['reason'])

    def test_refuses_pending_unsigned_forged_unqualified_or_self_calibrated(self):
        bar = signed_bar()
        for change in ('pending', 'signature', 'gate', 'margin', 'oc', 'D', 'W1', 'duplicate'):
            bad = deepcopy(bar)
            if change == 'pending': bad['status'] = 'PENDING'
            if change == 'signature': bad['lead_signature'] = ''
            if change == 'gate': bad['independent_gate']['derivation_sha256'] = 'e'*64
            if change == 'margin': bad['prediction']['relative_bar_30B'] *= 2
            if change == 'oc': bad['oc']['scenarios'][0]['series_failures'] += 1
            if change == 'D': bad['pairs'][-1]['configuration_sha256'] = 'e'*64
            if change == 'W1': bad['pairs'][0]['phase'] = 'W1'
            if change == 'duplicate': bad['pairs'][1]['session'] = bad['pairs'][0]['session']
            with self.subTest(change=change), self.assertRaises(ValueError):
                reg.validate_u3(bad)
        for energy in (0, -1, math.nan, math.inf, True):
            with self.subTest(energy=energy), self.assertRaises(ValueError):
                reg.u3_margin(energy, bar)

    def test_small_sample_and_larger_series_widen_prediction(self):
        data = export()
        base = reg.derive_u3(data['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=data['policy'])
        data['policy']['checks_by_window']['T4'] = {'30B': 0, 'D': 10}
        wider = reg.derive_u3(data['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=data['policy'])
        self.assertGreater(wider['prediction']['relative_bar_30B'], base['prediction']['relative_bar_30B'])
        data['pairs'][-1]['energies_j'] = [100, 200]
        bad = reg.derive_u3(data['pairs'], {'x': 'a'*64, 'transfer.md': 'f'*64}, policy=data['policy'])
        self.assertFalse(bad['prediction']['d_qualification_pass'])


class BatteryTests(unittest.TestCase):
    def test_raw_span_join_observes_idle_charging_assist_missing_and_malformed(self):
        from joulewise.align.apple import v4_battery as battery
        from joulewise.b5.harvest import JOURNAL_SCHEMA
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'metadata.json').write_text(json.dumps({'uncertainty_evidence': {'clock_anchor': {
                'clock_stamps': {'pre_spawn': {'monotonic_before_s': 2},
                                 'post_parse': {'monotonic_after_s': 10},
                                 'sampling_started': {'monotonic_before_s': 3},
                                 'sampling_stopped': {'monotonic_after_s': 9}}}}}))
            (root/'events.jsonl').write_text('\n'.join(json.dumps(r) for r in (
                {'event_type': 'stage_started', 'phase': 'idle_baseline', 'metadata': {'monotonic_ns': 10**9}},
                {'event_type': 'stage_completed', 'phase': 'idle_drift_sentinel', 'metadata': {'monotonic_ns': 12*10**9}})))
            path = root/'journal.jsonl'
            for mode in ('clean', 'assist', 'charge_idle', 'ac_loss', 'missing', 'malformed'):
                rows = []
                for sec in range(14):
                    stamp = dict(wall_ns=sec*10**9, monotonic_ns=sec*10**9, monotonic_raw_ns=sec*10**9)
                    current = -500 if mode == 'assist' else 500 if mode == 'charge_idle' and sec < 2 else 0
                    values = dict(update_time_s=sec, instant_amperage_ma=0, external_connected=mode != 'ac_loss',
                                  is_charging=False, current_capacity_pct=100, voltage_mv=12000,
                                  smc={'values': {'B0AC': current, 'B0AV': 12000+sec%2}, 'errors': {}})
                    rows.append(json.dumps(dict(schema=JOURNAL_SCHEMA, module='battery', kind='reading',
                                                started=stamp, finished=stamp, values=values, error=None)))
                path.write_text('' if mode == 'missing' else '\n'.join(rows)+('\ninvalid' if mode == 'malformed' else ''))
                evidence = battery.bundle_evidence(root, battery.load_journal(path))
                with self.subTest(mode=mode):
                    if mode in ('missing', 'malformed'):
                        self.assertEqual(evidence['status'], 'unavailable')
                    else:
                        self.assertEqual(evidence['status'], 'observed', evidence)
                        if mode == 'assist': self.assertIn('battery.assist', evidence['flags'])
                        if mode in ('charge_idle', 'ac_loss'): self.assertIn('battery.member_span', evidence['flags'])
                        if mode == 'clean': self.assertNotIn('battery.member_span', evidence['flags'])

    def test_clean_pass_assist_disclosed_charging_fail_missing_inconclusive(self):
        row = {'id': 'one', 'model': 'D', 'window': 'W1', 'flags': [],
               'battery': {'status': 'observed', 'source_sha256': 'a'*64, 'flags': [],
                           'soc_pct': [100], 'charger_w': [140]}}
        def check(r):
            return reg.desk_diagnostics([r], battery_policy=battery_policy())['battery_windows']['D/W1']
        self.assertIs(check(row)['bar_pass'], True)
        assisted = deepcopy(row)
        assisted['battery']['flags'] = ['battery.assist']
        self.assertIs(check(assisted)['bar_pass'], True)
        self.assertEqual(check(assisted)['assist_count'], 1)
        charging = deepcopy(row)
        charging['battery']['flags'] = ['battery.member_span']
        self.assertIs(check(charging)['bar_pass'], False)
        self.assertIn('no pool entry', check(charging)['consequence'])
        row.pop('battery')
        self.assertIsNone(check(row)['bar_pass'])
        self.assertIsNone(reg.desk_diagnostics([row])['battery_windows']['D/W1']['bar_pass'])

    def test_empty_window_never_vacuously_passes(self):
        from scripts import align_v4_session as session
        self.assertFalse(session.battery_windows_pass({}))


if __name__ == '__main__':
    unittest.main()
