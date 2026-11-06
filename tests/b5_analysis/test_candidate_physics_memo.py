"""b5 under-90 round 2: the candidate-physics memo and its prefetch change no value (synthetic)."""
from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import calibration_bracketing as cb
from joulewise.b5_analysis import bracket


class Deadline:
    def __init__(self):
        self.firings = 0


class MemoTests(unittest.TestCase):
    def call(self):
        return cb._verified_candidate_bound(b'{"e": 1}', {'e': 1}, b'plist', b'events')

    def test_outside_a_run_every_call_refits(self):
        with mock.patch.object(cb, 'verify_stored_evidence_physics', side_effect=[0.5, 0.5]) as verify:
            self.assertEqual((self.call(), self.call()), (0.5, 0.5))
        self.assertEqual(verify.call_count, 2)

    def test_a_run_remembers_a_clean_value_by_input_digests(self):
        with arc.analysis_run_caches({}) as caches:
            caches.deadline = Deadline()
            with mock.patch.object(cb, 'verify_stored_evidence_physics', return_value=0.25) as verify:
                self.assertEqual((self.call(), self.call()), (0.25, 0.25))
                other = cb._verified_candidate_bound(b'{"e": 1}', {'e': 1}, b'plist2', b'events')
            self.assertEqual(verify.call_count, 2)
            self.assertEqual(other, 0.25)
            self.assertEqual(len(caches.memos[cb.CANDIDATE_PHYSICS_MEMO]), 2)

    def test_firings_refusals_and_missing_observer_are_never_remembered(self):
        with arc.analysis_run_caches({}) as caches:
            deadline = caches.deadline = Deadline()

            def firing(*_args):
                deadline.firings += 1
                return 0.25
            with mock.patch.object(cb, 'verify_stored_evidence_physics', side_effect=firing):
                self.call()
            with mock.patch.object(cb, 'verify_stored_evidence_physics', side_effect=ValueError('no')):
                with self.assertRaises(ValueError):
                    self.call()
            caches.deadline = None
            with mock.patch.object(cb, 'verify_stored_evidence_physics', return_value=0.25):
                self.call()
            self.assertEqual(caches.memos.get(cb.CANDIDATE_PHYSICS_MEMO, {}), {})


class PrefetchTests(unittest.TestCase):
    def snapshot(self, count=3):
        return SimpleNamespace(observations=[
            SimpleNamespace(disposition='valid', content_id=f'c{i}', is_historical_import=False,
                            custody_locator=f'/runs/root/cal-{i}') for i in range(count)]
            + [SimpleNamespace(disposition='invalid', content_id='x', is_historical_import=False,
                               custody_locator='/runs/root/bad')])

    def test_only_clean_successful_float_values_merge(self):
        outcomes = [SimpleNamespace(ok=True, firings=0, vdl_new={'memos': {cb.CANDIDATE_PHYSICS_MEMO: {'a': 0.5}}}),
                    SimpleNamespace(ok=True, firings=1, vdl_new={'memos': {cb.CANDIDATE_PHYSICS_MEMO: {'b': 0.5}}}),
                    SimpleNamespace(ok=False, firings=0, vdl_new={'memos': {cb.CANDIDATE_PHYSICS_MEMO: {'c': 0.5}}}),
                    SimpleNamespace(ok=True, firings=0, vdl_new={'memos': {cb.CANDIDATE_PHYSICS_MEMO: {'d': 'x'}}})]
        with arc.analysis_run_caches({}, workers=3) as caches:
            with mock.patch('joulewise.analysis_member_pool.member_map', return_value=outcomes) as mapped:
                bracket._prefetch_candidate_physics(self.snapshot(), 'issuing')
            self.assertEqual(caches.memos[cb.CANDIDATE_PHYSICS_MEMO], {'a': 0.5})
        args = mapped.call_args
        self.assertEqual([call[0][0] for call in args.args[1]], ['/runs/root/cal-0', '/runs/root/cal-1',
                                                                 '/runs/root/cal-2'])
        self.assertEqual(args.kwargs, {'account': False})

    def test_no_pool_or_one_candidate_does_nothing_and_errors_are_swallowed(self):
        with mock.patch('joulewise.analysis_member_pool.member_map') as mapped:
            with arc.analysis_run_caches({}, workers=1):
                bracket._prefetch_candidate_physics(self.snapshot(), 'issuing')
            with arc.analysis_run_caches({}, workers=3):
                bracket._prefetch_candidate_physics(self.snapshot(1), 'issuing')
                mapped.side_effect = RuntimeError('pool')
                bracket._prefetch_candidate_physics(self.snapshot(), 'issuing')
        self.assertEqual(mapped.call_count, 1)


if __name__ == '__main__':
    unittest.main()
