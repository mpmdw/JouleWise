"""Synthetic W1 candidate checks; no real registration, models or data."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align import prequal, w1_prequal as w1
from joulewise.align.apple import v4_registration as reg

ROOT = Path(__file__).resolve().parents[2]


def series():
    return {'schema': w1.SERIES_SCHEMA, 'windows': [dict(window='W1', role='w1')] +
            [dict(window=f'C{i}', role='calibration', benign_per_pair={'spam': 7, 'bank': 7})
             for i in range(1, 9)] + [dict(window='T1', role='test')]}


def deadline(kind='r1', *, attempts=1, maximum=100000):
    return {'window_max_s': maximum, 'smoke_deadline_projection': {'kind': kind,
        'segments': [{'bound_s': 56207, 'attempts': attempts, 'batch_encounters': 1}],
        'bracket_s': 100, 'close_s': 200, 'harvest_s': 300}}


class SeriesTests(unittest.TestCase):
    def test_planned_fixed_eight_zero_capture_partial_loss_and_finality(self):
        result = w1.validate_series(series())
        self.assertEqual(result['decisions'], ['continue'] * 8 + ['calibration_complete'])
        self.assertTrue(result['zero_capture_does_not_count'])
        self.assertTrue(result['two_zero_captures_escalate'])

    def test_no_inferred_series_missing_cohort_reorder_or_seventh_stop(self):
        cases = [{}, series(), series(), series(), series(), series(), series()]
        cases[1]['windows'].pop(8)
        cases[2]['windows'][1:3] = reversed(cases[2]['windows'][1:3])
        cases[3]['windows'][1]['benign_per_pair']['bank'] = 6
        cases[4]['windows'][1]['window'] = 'C2'
        cases[5]['windows'].pop()
        cases[6]['windows'].insert(0, cases[6]['windows'].pop())
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError):
                w1.validate_series(value)

    def test_projection_binds_source_bytes_and_missing_inputs_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = b'synthetic frozen series source'
            (root / 'source.json').write_bytes(raw)
            data = series()
            data['source'] = {'path': 'source.json', 'sha256': hashlib.sha256(raw).hexdigest()}
            (root / 'series.json').write_text(json.dumps(data))
            ctx = prequal.Context(repo=root, w1_series='series.json')
            self.assertEqual(w1.series_check(ctx)['status'], 'pass')
            (root / 'source.json').write_bytes(raw + b' ')
            with self.assertRaisesRegex(ValueError, 'frozen source'):
                w1.series_check(ctx)
            with self.assertRaisesRegex(ValueError, '--w1-series'):
                w1.series_check(prequal.Context(repo=root))


class DeadlineTests(unittest.TestCase):
    def test_no_redo_corrected_floor_with_overheads(self):
        plan = deadline(maximum=67371+600)
        self.assertEqual(w1.validate_deadline(plan)['required_s'], 67971)
        for old in (56207, 61607, 67371):
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, 'corrected requirement'):
                w1.validate_deadline(deadline(maximum=old))

    def test_redo_and_each_encounter_are_budgeted(self):
        plan = deadline(attempts=2, maximum=200000)
        self.assertGreater(w1.validate_deadline(plan)['required_s'], 96427)
        plan['smoke_deadline_projection']['segments'][0]['bound_s'] = 20000
        plan['smoke_deadline_projection']['segments'][0]['batch_encounters'] = 2
        plan['window_max_s'] = 96427+600
        self.assertEqual(w1.validate_deadline(plan)['required_s'], 97027)
        plan['window_max_s'] = 90663+600
        with self.assertRaises(ValueError):
            w1.validate_deadline(plan)

    def test_w1_does_not_inherit_r1_floors(self):
        plan = deadline('w1', maximum=59520)
        plan['smoke_deadline_projection']['segments'] = [dict(bound_s=40527, attempts=1, batch_encounters=0)]
        self.assertEqual(w1.validate_deadline(plan)['required_s'], 41127)
        plan['window_max_s'] = 40527
        with self.assertRaises(ValueError):
            w1.validate_deadline(plan)

    def test_malformed_schedule_cannot_pass(self):
        for key, value in [('attempts', 0), ('attempts', True), ('batch_encounters', -1),
                           ('batch_encounters', 2), ('bound_s', float('nan'))]:
            plan = deadline()
            plan['smoke_deadline_projection']['segments'][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                w1.validate_deadline(plan)
        with self.assertRaises(ValueError):
            w1.validate_deadline({'window_max_s': 999999})


class ReceiptTests(unittest.TestCase):
    def test_executed_closure_is_recomputed_and_bound(self):
        closure = w1.closure(ROOT)
        self.assertIn('joulewise/align/apple/prompt_cache.py', closure)
        self.assertIn('joulewise/external/km003c_parse.py', closure)
        self.assertFalse({p for p in closure if p.startswith('joulewise/')} - set(reg.ARTIFACTS))

    def test_exact_commit_receipt_accepts_then_refuses_changed_bound_file(self):
        # An isolated synthetic Git repository; no alternate, model or data.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = ('joulewise/align/apple/endpoint.py', 'scripts/run_night.py', 'scripts/align_v4_session.py')
            gates = ('docs/align/v4/a.json', 'docs/align/v4/b.json')
            for path in paths + gates:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(b'{}' if path.endswith('.json') else b'# synthetic\n')
            env = {**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'}
            def git(*args):
                return subprocess.run(['git', '-c', 'user.name=smoke', '-c', 'user.email=smoke@example.invalid',
                    '-c', 'commit.gpgsign=false', *args], cwd=root, env=env, check=True,
                    capture_output=True, text=True).stdout.strip()
            git('init', '-q')
            git('add', '.')
            git('commit', '-qm', 'Synthetic candidate')
            head = git('rev-parse', 'HEAD')
            receipt = {'schema': reg.RECEIPT_SCHEMA, 'status': 'registered', 'commit': head,
                'lead_signature': 'lead: synthetic test 2026-11-08',
                'rulings': {str(n): 'installed' for n in reg.RULINGS},
                'artifacts': {p: reg.digest((root/p).read_bytes()) for p in paths},
                'gates': {stage: {'verdict': 'ADMIT', 'path': p, 'sha256': reg.digest((root/p).read_bytes())}
                          for stage, p in zip(('A', 'B'), gates)}}
            with patch.object(reg, 'ARTIFACTS', paths):
                reg.validate_receipt(receipt, root)
                receipt_path = root / reg.REGISTRATION / 'registration_receipt.json'
                receipt_path.parent.mkdir(parents=True)
                receipt_path.write_text(json.dumps(receipt))
                git('add', '.')
                git('commit', '-qm', 'Synthetic receipt')
                def run(argv, **kwargs):
                    return subprocess.run(argv, env=env, **kwargs)
                ctx = prequal.Context(repo=root, w1_candidate=head, w1_run=run)
                self.assertEqual(w1.receipt_check(ctx)['candidate'], head)
                ctx.w1_candidate = git('rev-parse', 'HEAD')
                with self.assertRaisesRegex(ValueError, 'requested candidate'):
                    w1.receipt_check(ctx)
                ctx.w1_candidate = head
                (root / paths[0]).write_bytes(b'# EDITED synthetic\n')
                with self.assertRaisesRegex(ValueError, 'digest drift'):
                    w1.receipt_check(ctx)
                (root / paths[0]).write_bytes(b'# synthetic\n')
                receipt['commit'] = '0' * 40
                with self.assertRaisesRegex(ValueError, 'missing committed artifact'):
                    reg.validate_receipt(receipt, root)

    def test_candidate_pending_is_fail_never_skip(self):
        ctx = prequal.Context(repo=ROOT)
        with patch.object(w1, 'read_local', return_value=b'{"status":"PENDING"}'), \
                patch.object(w1, 'closure', return_value=set()), \
                self.assertRaisesRegex(ValueError, 'pending or malformed'):
            w1.receipt_check(ctx)


class RunnerTests(unittest.TestCase):
    def test_injected_command_error_and_skip_do_not_pass(self):
        for rc, stderr in ((1, 'broken'), (0, 'OK (skipped=1)'), (0, 'Ran 0 tests')):
            run = lambda *a, **k: SimpleNamespace(returncode=rc, stdout='', stderr=stderr)
            ctx = prequal.Context(repo=ROOT, w1_run=run)
            with self.subTest(stderr=stderr), self.assertRaises(ValueError):
                w1.probe(ctx, ['synthetic.target'])
        run = lambda *a, **k: SimpleNamespace(returncode=0, stdout='', stderr='Ran 2 tests\nOK')
        self.assertEqual(w1.probe(prequal.Context(repo=ROOT, w1_run=run), ['target'])['status'], 'pass')

    def test_exception_becomes_failure_and_omitted_required_checks_incomplete(self):
        def boom(ctx):
            raise ValueError('synthetic fault')
        with patch.object(prequal, 'W1_CHECKS', (('bad', boom), ('good', lambda c: {'status': 'pass'}))):
            result = prequal.run(prequal.Context(repo=ROOT), w1_only=True)
            self.assertEqual(result['status'], 'fail')
            self.assertEqual(result['failed'], ['bad'])
            result = prequal.run(prequal.Context(repo=ROOT), only={'good'}, w1_only=True)
            self.assertEqual(result['status'], 'incomplete')
            self.assertEqual(result['scope'], 'w1-software-extension-only')

    def test_stale_valid_packet_gap_is_a_red_table_row(self):
        result = w1.triage_integrity_check(None)
        self.assertEqual(result['status'], 'fail')
        self.assertTrue(result['stale_valid_packet_admitted'])

    def test_input_guards_refuse_external_and_symlink_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'link').symlink_to('/unread')
            for path in ('/forbidden', '../outside', 'restricted/a', 'night-custody/a', 'link/a'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    w1.read_local(root, path)


if __name__ == '__main__':
    unittest.main()
