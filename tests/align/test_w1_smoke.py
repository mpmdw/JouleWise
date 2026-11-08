"""Synthetic native-output parser/recorder checks; commands are injected."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.align import w1_smoke as smoke


def evidence(case):
    if case in smoke.REFUSALS:
        return {'refusal': {'admitted': False, 'reasons': [smoke.REFUSALS[case][1]]}}
    if case == 'r1-chain':
        return {'chain': {'synthetic_only': True, 'steps': dict.fromkeys(
            ('export', 'backfill-x-g', 'backfill-turn-counts', 'derive-contrast', 'kit-check'), 0)}}
    return {'night_result': {'verdict': 'GO', 'chain_exit_code': 0, 'aborted_reason': None},
            'hazard_result': {'meter': {'streams': [{'path': 'synthetic'}], 'stop': {'proven_stopped': True}}},
            'dc_members': {'members': {'member': {'status': 'missing' if case == 'meter-killed' else 'available',
                'flags': ['meter.member_span_uncovered'] if case == 'meter-killed' else [],
                'powermetrics_admissibility_unchanged': True}}},
            'gpu_members': {'member': {'energy': {'powermetrics:gpu_power': {'joules': 12., 'flags': []}},
                                        'flags': []}},
            'finalize': {'status': 'ok'}, 'terminal': {'terminal': True}}


def command(case):
    return {'schema': smoke.SCHEMA, 'case': case, 'timed_out': False,
            'returncode': smoke.REFUSALS.get(case, (0, ''))[0],
            'stderr': 'registration_receipt digest drift: bound.py' if case == 'receipt-digest' else '',
            'chain_start': {'path': 'synthetic/chain.started', 'present': False}}


class EvaluateTests(unittest.TestCase):
    def test_every_positive_and_documented_negative(self):
        for case in smoke.CASES:
            with self.subTest(case=case):
                self.assertTrue(smoke.evaluate(case, command(case), evidence(case)))

    def test_every_unrelated_refusal_and_unexpected_success_fails(self):
        for case in smoke.REFUSALS:
            for kind in ('success', 'wrong-reason', 'no-observation', 'launched'):
                record, artifacts = command(case), evidence(case)
                if kind == 'success': record['returncode'] = 0
                if kind == 'wrong-reason':
                    artifacts['refusal']['reasons'] = ['unrelated disk full']
                    record['stderr'] = 'unrelated disk full'
                if kind == 'no-observation':
                    artifacts.clear()
                    record['stderr'] = ''
                if kind == 'launched': record['chain_start']['present'] = True
                with self.subTest(case=case, kind=kind), self.assertRaises(ValueError):
                    smoke.evaluate(case, record, artifacts)

    def test_timeouts_wrong_schema_or_case_never_pass(self):
        for case in smoke.CASES:
            for key, value in (('timed_out', True), ('schema', 'unknown'), ('case', 'other'), ('returncode', None)):
                record = command(case)
                record[key] = value
                with self.subTest(case=case, key=key), self.assertRaises(ValueError):
                    smoke.evaluate(case, record, evidence(case))

    def test_window_requires_chain_meter_finalize_terminal_and_gpu_preservation(self):
        mutations = [lambda x: x['night_result'].update(verdict='REFUSED'),
                     lambda x: x['night_result'].update(chain_exit_code=7),
                     lambda x: x['hazard_result']['meter']['stop'].update(proven_stopped=False),
                     lambda x: x['hazard_result']['meter'].update(streams=[]),
                     lambda x: x['finalize'].update(status='failed'),
                     lambda x: x['terminal'].update(terminal=False),
                     lambda x: x['gpu_members']['member']['energy']['powermetrics:gpu_power'].update(joules=None),
                     lambda x: x['gpu_members']['member'].update(flags=['trace.missing']),
                     lambda x: x['dc_members']['members']['member'].update(powermetrics_admissibility_unchanged=False),
                     lambda x: x['dc_members']['members'].clear(),
                     lambda x: x['dc_members']['members'].update({str(i): {} for i in range(3)})]
        for mutate in mutations:
            value = evidence('window')
            mutate(value)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                smoke.evaluate('window', command('window'), value)
        missing = evidence('window')
        missing['dc_members']['members']['member']['status'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'missing DC'):
            smoke.evaluate('window', command('window'), missing)

    def test_reader_kill_requires_explicit_member_missing_flag(self):
        for status, flags in (('available', []), ('missing', []), ('missing', ['unrelated'])):
            value = evidence('meter-killed')
            value['dc_members']['members']['member'].update(status=status, flags=flags)
            with self.subTest(status=status), self.assertRaises(ValueError):
                smoke.evaluate('meter-killed', command('meter-killed'), value)

    def test_chain_dryrun_requires_all_five_steps_and_synthetic_label(self):
        for step in evidence('r1-chain')['chain']['steps']:
            value = evidence('r1-chain')
            value['chain']['steps'][step] = 1
            with self.subTest(step=step), self.assertRaises(ValueError):
                smoke.evaluate('r1-chain', command('r1-chain'), value)
        value = evidence('r1-chain')
        value['chain']['synthetic_only'] = False
        with self.assertRaises(ValueError):
            smoke.evaluate('r1-chain', command('r1-chain'), value)


class TranscriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='w1-smoke-parser-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'smoke'
        smoke.init(self.root, 'a' * 40)

    def build(self, case, *, timeout=False):
        pairs = []
        for name, data in evidence(case).items():
            relative = f'inputs/{case}-{name}.json'
            smoke.write_once(smoke.local(self.root, relative), data)
            pairs.append((name, relative))
        calls = []
        def run(argv, **kwargs):
            calls.append((argv, kwargs))
            if timeout:
                raise subprocess.TimeoutExpired(argv, 1)
            return SimpleNamespace(returncode=command(case)['returncode'], stdout='synthetic stdout',
                                   stderr=command(case)['stderr'])
        record = smoke.capture(self.root, case, ['synthetic', case], run=run, artifacts=pairs,
                               chain_start='synthetic/chain.started')
        self.assertEqual(calls[0][0], ['synthetic', case])
        self.assertEqual(calls[0][1]['timeout'], 120)
        smoke.teardown(self.root, case, [['verify-owned-resources-gone']], run=lambda *a, **k:
                       SimpleNamespace(returncode=0, stdout='', stderr=''))
        return record

    def test_missing_cases_are_fail_not_skip(self):
        result = smoke.report(self.root)
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(sum(r['status'] == 'fail' for r in result['checks']), len(smoke.CASES))
        self.assertIn('| window | FAIL |', smoke.table(result))

    def test_complete_transcript_passes_and_edited_artifact_fails(self):
        for case in smoke.CASES:
            self.build(case)
        self.assertEqual(smoke.report(self.root)['status'], 'pass')
        target = self.root / 'inputs/window-night_result.json'
        target.write_bytes(target.read_bytes() + b' ')
        result = smoke.report(self.root)
        self.assertEqual(result['status'], 'fail')
        self.assertIn('edited artifact', result['checks'][0]['detail'])

    def test_failed_or_missing_cleanup_never_passes(self):
        for case in smoke.CASES:
            self.build(case)
        path = self.root / 'disk-image/teardown.json'
        cleanup = json.loads(path.read_text())
        cleanup['commands'][0]['returncode'] = 1
        path.write_text(json.dumps(cleanup))
        self.assertEqual(smoke.report(self.root)['status'], 'fail')
        path.unlink()
        self.assertEqual(smoke.report(self.root)['status'], 'fail')

    def test_no_duplicate_case_or_output_overwrite(self):
        self.build('window')
        with self.assertRaises(FileExistsError):
            self.build('window')
        with self.assertRaises(FileExistsError):
            smoke.init(self.root, 'b' * 40)

    def test_native_wall_time_includes_gaps_between_commands(self):
        for case in smoke.CASES:
            self.build(case)
        path = self.root / 'r1-chain/teardown.json'
        cleanup = json.loads(path.read_text())
        cleanup['ended_epoch_s'] += 2701
        path.write_text(json.dumps(cleanup))
        self.assertEqual(smoke.report(self.root)['checks'][-1]['status'], 'fail')

    def test_timeout_retains_failure_and_does_not_call_it_an_expected_refusal(self):
        record = self.build('disk-image', timeout=True)
        self.assertTrue(record['timed_out'])
        self.assertEqual(smoke.report(self.root)['status'], 'fail')

    def test_chain_start_after_attempt_is_still_a_failure(self):
        self.build('disk-image')
        path = self.root / 'synthetic/chain.started'
        path.parent.mkdir()
        path.write_text('unexpected start')
        row = next(r for r in smoke.report(self.root)['checks'] if r['check'] == 'disk-image')
        self.assertEqual(row['status'], 'fail')

    def test_unlabelled_poolable_or_analyzable_roots_refuse(self):
        path = self.root / 'SMOKE.json'
        label = json.loads(path.read_text())
        for key in ('registrable', 'pool_eligible', 'analysis_eligible'):
            path.write_text(json.dumps({**label, key: True}))
            with self.subTest(key=key), self.assertRaises(ValueError):
                smoke.report(self.root)

    def test_safe_relative_paths_only_without_following_links(self):
        (self.root / 'link').symlink_to('/unread')
        for name in ('/outside', '../outside', 'restricted/a', 'night-archive/a', 'link/a'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                smoke.local(self.root, name)

    def test_timeout_stops_only_owned_command_group(self):
        process = SimpleNamespace(pid=123456, returncode=-15,
            communicate=unittest.mock.Mock(side_effect=[subprocess.TimeoutExpired(['synthetic'], 1), ('out', 'err')]))
        with patch.object(smoke.subprocess, 'Popen', return_value=process) as popen, \
                patch.object(smoke.os, 'killpg') as kill:
            with self.assertRaises(subprocess.TimeoutExpired):
                smoke.bounded_run(['synthetic'], timeout=1)
        self.assertTrue(popen.call_args.kwargs['start_new_session'])
        kill.assert_called_once_with(123456, smoke.signal.SIGTERM)

    def test_malformed_case_record_yields_fail_row(self):
        self.build('window')
        (self.root / 'window/command.json').write_text('[]')
        self.assertEqual(smoke.report(self.root)['checks'][0]['status'], 'fail')

    def test_mixed_candidate_cases_are_not_combined(self):
        self.build('window')
        path = self.root / 'window/command.json'
        record = json.loads(path.read_text())
        record['candidate'] = 'b' * 40
        path.write_text(json.dumps(record))
        row = smoke.report(self.root)['checks'][0]
        self.assertEqual(row['status'], 'fail')
        self.assertIn('different candidate', row['detail'])


if __name__ == '__main__':
    unittest.main()
