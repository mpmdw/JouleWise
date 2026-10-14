"""Deterministic precision arithmetic and public-output isolation on synthetic data."""
from contextlib import redirect_stdout, redirect_stderr
import copy
from datetime import date
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
import unittest

from joulewise import pack_stopping as stopping
from joulewise.aggregate import student_t_critical_95


class PackStoppingTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.registration = {'pack_id': 'BYTES', 'stopping': {'target_sessions': 3, 'min_sessions': 2,
                              'session_cap': 3, 'max_attempts': 5, 'end_date': '2026-11-01'}}
        self.today = date(2026, 10, 14)
        self.keydir = self.root / 'blinding'
        self.keydir.mkdir()
        (self.keydir / 'pack.json').write_text('{"factor":1.2}')
        config = hashlib.sha256(b'config-one').hexdigest()[:16]
        (self.keydir / f'config-{config}.json').write_text('{"factor":1.0}')

    def precision(self, interval='reported', scale='conservative', target=1):
        self.registration['stopping'].update(session_cap=10)
        self.registration['stopping']['precision'] = {'scale': scale, 'quantities': [
            {'id': 'q', 'config_id': 'config-one', 'interval': interval, 'half_width_j': target}]}

    def sessions(self, values, counting=None, widths=None):
        return [({'pack_id': 'BYTES', 'session_id': f's{i}', 'attempt': i + 1,
                  'counting': counting[i] if counting is not None else True},
                 {'schema': stopping.PRECISION_SCHEMA, 'session_id': f's{i}', 'pack_id': 'BYTES',
                  'quantities': {'q': {'config_id': 'config-one', 'value': value,
                                       'half_width': widths[i] if widths else value}}})
                for i, value in enumerate(values)]

    def evaluate(self, sessions, **kwargs):
        return stopping.evaluate(self.registration, sessions, today=kwargs.pop('today', self.today), **kwargs)

    def test_replication_count_attempt_and_date_rules(self):
        cases = [(self.sessions([0, 0]), self.today, 'CONTINUE', False),
                 (self.sessions([0, 0, 0]), self.today, 'STOP_CAP', False),
                 (self.sessions([0] * 5, [True, False, False, False, False]), self.today, 'PAUSE_ATTEMPTS', False),
                 (self.sessions([0]), date(2026, 11, 2), 'STOP_END_DATE', True)]
        for sessions, today, decision, short in cases:
            with self.subTest(decision=decision):
                public, _ = self.evaluate(sessions, today=today)
                self.assertEqual((public['decision'], public['short']), (decision, short))
        self.assertEqual(self.evaluate(self.sessions([0]), today=date(2026, 11, 1))[0]['decision'], 'CONTINUE')

    def test_between_session_arithmetic_hand_values(self):
        for values, critical in (([1, 3], 12.706), ([1, 2, 3], 4.303), ([1, 2, 3, 4], 3.182)):
            with self.subTest(k=len(values)):
                self.assertEqual(student_t_critical_95(len(values) - 1), critical)
                expected = critical * statistics.stdev(values) / math.sqrt(len(values))
                self.assertAlmostEqual(stopping.between_sessions_half_width(values), expected, places=12)
                self.precision('between_sessions', target=expected / 0.776 * 1.001)
                public, private = self.evaluate(self.sessions(values))
                self.assertEqual(public['decision'], 'STOP_PRECISION')
                self.assertAlmostEqual(private['quantities']['q']['blinded_half_width'], expected, places=12)
                self.assertEqual(private['quantities']['q']['df'], len(values) - 1)

    def test_location_invariance_and_estimate_independence(self):
        self.precision('between_sessions', target=1)
        for base in ([1, 1.1, 1.2], [1, 3, 5]):
            reference = self.evaluate(self.sessions(base))[0]
            for offset in (1000, -1000, 100000):
                public, _ = self.evaluate(self.sessions([value + offset for value in base]))
                self.assertEqual(public, reference)

    def test_keyed_unscales_exactly_and_conservative_boundary(self):
        self.precision(scale='keyed')
        public, private = self.evaluate(self.sessions([1.2, 1.2]), key_dir=self.keydir)
        self.assertEqual(public['decision'], 'STOP_PRECISION')
        self.assertEqual(private['quantities']['q']['blinded_half_width'], 1.2)
        self.assertEqual(self.evaluate(self.sessions([1.2001] * 2), key_dir=self.keydir)[0]['decision'], 'CONTINUE')
        self.precision()
        self.assertEqual(self.evaluate(self.sessions([0.776] * 2))[0]['decision'], 'STOP_PRECISION')
        self.assertEqual(self.evaluate(self.sessions([0.78] * 2))[0]['decision'], 'CONTINUE')

    def test_cross_configuration_quantity_is_unavailable(self):
        self.precision()
        quantity = self.registration['stopping']['precision']['quantities'][0]
        for config in (None, ['config-one', 'config-two']):
            with self.subTest(config=config):
                quantity['config_id'] = config
                record, _ = self.evaluate(self.sessions([0.1] * 2))
                self.assertEqual(record['quantities']['q']['reached'], 'precision_unavailable')
                self.assertEqual(record['decision'], 'CONTINUE')
                self.assertEqual(self.evaluate(self.sessions([0.1]), today=date(2026, 11, 2))[0]['decision'], 'STOP_END_DATE')
                self.registration['stopping']['session_cap'] = 3
                self.assertEqual(self.evaluate(self.sessions([0.1] * 3))[0]['decision'], 'STOP_CAP')

    def test_decision_precedence_and_minimum_precision_sessions(self):
        self.precision()
        self.registration['stopping']['session_cap'] = 3
        self.assertEqual(self.evaluate(self.sessions([0.1] * 3), today=date(2026, 11, 2))[0]['decision'], 'STOP_CAP')
        self.assertEqual(self.evaluate(self.sessions([0.1] * 2), today=date(2026, 11, 2))[0]['decision'], 'STOP_PRECISION')
        self.assertEqual(self.evaluate(self.sessions([0.1] * 5, [True, False, False, False, False]),
                                       today=date(2026, 11, 2))[0]['decision'], 'STOP_END_DATE')
        self.assertEqual(self.evaluate(self.sessions([0.1]))[0]['decision'], 'CONTINUE')

    def test_reported_uses_latest_counting_session_and_all_quantities(self):
        self.precision()
        sessions = self.sessions([0.1, 0.9, 0.001], [True, True, False])
        self.assertEqual(self.evaluate(sessions)[0]['decision'], 'CONTINUE')
        sessions[1][1]['quantities']['q']['half_width'] = 0.1
        self.assertEqual(self.evaluate(sessions)[0]['decision'], 'STOP_PRECISION')
        other = copy.deepcopy(self.registration['stopping']['precision']['quantities'][0])
        other['id'] = 'q2'
        self.registration['stopping']['precision']['quantities'].append(other)
        self.assertEqual(self.evaluate(sessions)[0]['decision'], 'CONTINUE')

    def test_missing_mismatched_or_nonfinite_analysis_is_unavailable(self):
        self.precision('between_sessions')
        for modification in ('missing', 'config', 'pack', 'session', 'nan'):
            with self.subTest(modification=modification):
                sessions = self.sessions([0.1] * 2)
                analysis = sessions[1][1]
                if modification == 'missing':
                    sessions[1] = (sessions[1][0], None)
                elif modification == 'config':
                    analysis['quantities']['q']['config_id'] = 'config-two'
                elif modification == 'nan':
                    analysis['quantities']['q']['value'] = float('nan')
                else:
                    analysis[modification + '_id'] = 'wrong'
                self.assertEqual(self.evaluate(sessions)[0]['quantities']['q']['reached'], 'precision_unavailable')

    def test_bad_keys_have_sanitized_exception_and_unavailable_record(self):
        config = hashlib.sha256(b'config-one').hexdigest()[:16]
        (self.keydir / f'config-{config}.json').write_text('{"factor":98765.4321}')
        with self.assertRaisesRegex(ValueError, '^precision_unavailable$'):
            stopping.read_factor(self.keydir, 'config-one')
        self.precision(scale='keyed')
        public, private = self.evaluate(self.sessions([0.1] * 2), key_dir=self.keydir)
        self.assertEqual(public['quantities']['q']['reached'], 'precision_unavailable')
        self.assertNotIn('98765.4321', json.dumps(public) + json.dumps(private))

    def test_cli_order_output_firewall_and_withheld_directory(self):
        self.precision(scale='keyed', target=100000)
        sessions_dir = self.root / 'sessions'
        for i, (record, analysis) in enumerate(self.sessions([98765.4321] * 2, widths=[200000, 98765.4321])):
            directory = sessions_dir / f'reverse-{2-i}'
            directory.mkdir(parents=True)
            (directory / 'structure.json').write_text(json.dumps(record))
            (directory / 'precision.json').write_text(json.dumps(analysis))
        reg = self.root / 'registration.json'
        reg.write_text(json.dumps(self.registration))
        records, withheld = self.root / 'records', self.root / 'private'
        args = ['--registration', str(reg), '--sessions-dir', str(sessions_dir), '--record-dir', str(records),
                '--key-dir', str(self.keydir), '--withheld-dir', str(withheld), '--today', self.today.isoformat()]
        result = subprocess.run([sys.executable, 'scripts/pack_stopping.py', *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('decision=STOP_PRECISION', result.stdout)
        public = (records / 'stopping.json').read_text() + result.stdout + result.stderr
        for secret in ('98765.4321', 'half_width', 'factor', '1.2'):
            self.assertNotIn(secret, public)
        self.assertIn('98765.4321', (withheld / 'stopping-withheld.json').read_text())
        self.assertFalse((records / 'withheld').exists())

    def test_unparsable_registration_exit_two_without_sensitive_error(self):
        reg = self.root / 'registration.json'
        output = io.StringIO()
        for text in ('bad-json 98765.4321', '[]', '{}'):
            reg.write_text(text)
            with self.subTest(text=text), redirect_stderr(output), self.assertRaises(SystemExit) as caught:
                stopping.main(['--registration', str(reg), '--sessions-dir', str(self.root), '--record-dir', str(self.root / 'records')])
            self.assertEqual(caught.exception.code, 2)
        self.assertNotIn('98765.4321', output.getvalue())
        self.assertFalse((self.root / 'records').exists())
