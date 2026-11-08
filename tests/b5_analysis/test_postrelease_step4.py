"""Step-4 speculative cleanup, with synthetic child files and no worker pool."""
import contextlib
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

from joulewise.b5_analysis import dry_run as d, parallel
from joulewise.b5_analysis.windows import AnalysisRefusal


class Step4CleanupTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='b5-postrelease-step4-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.s = d.RunState('blind-dry-run', self.root/'index.json', self.root, 'a'*40)
        self.s.rehash = mock.Mock()
        self.s.deadline = SimpleNamespace(firings=0)
        self.s.specs = {'alpha': {}, 'beta': {}}
        self.s.register = mock.Mock(side_effect=lambda role, path: {
            'name': Path(path).relative_to(self.root).as_posix(), 'sha256': 'b'*64})
        self.s.read = mock.Mock(return_value={})
        self.r = d.StepRunner(self.root)
        self.r._counter = 7
        self.results = []

    def dispatch(self, s, r, tasks, contexts):
        base = r._counter
        r._counter += len(tasks)
        for i, (_, argv, _, pack) in enumerate(tasks):
            Path(argv[argv.index('--out')+1]).write_text('{}')
            logs = [self.root/f'{base+i+1}-{pack}.{kind}' for kind in ('stdout', 'stderr')]
            for log in logs:
                log.write_text('')
            self.results.append(parallel.ChildResult(0, *map(str, logs), False, i+1, {}))
        return base, self.results, None

    @contextlib.contextmanager
    def children(self):
        with mock.patch.object(d, '_dispatch', side_effect=self.dispatch):
            yield

    def assert_prefix(self, count):
        self.assertEqual(self.r._counter, 7+count)
        self.assertEqual(self.s.deadline.firings, sum(range(1, count+1)))
        for i, pack in enumerate(('alpha', 'beta')):
            for path in (self.root/f'mint/extraction-{pack}.json',
                         Path(self.results[i].stdout_path), Path(self.results[i].stderr_path)):
                self.assertEqual(path.exists(), i<count, str(path))

    def test_registration_or_classification_exception_discards_later_children(self):
        for seam in ('register', '_step_4_classify'):
            with self.subTest(seam=seam):
                self.results = []
                self.r._counter = 7
                self.s.deadline.firings = 0
                target = self.s if seam == 'register' else d
                failure = OSError('synthetic failure')
                with self.children(), mock.patch.object(target, seam, side_effect=failure):
                    with self.assertRaises(OSError) as caught:
                        d._step_4_parallel(self.s, self.r, ('alpha', 'beta'))
                self.assertIs(caught.exception, failure)
                self.assert_prefix(1)

    def test_reauthentication_exception_discards_the_unstarted_child(self):
        for failure in (AnalysisRefusal('archive_input_changed'), RuntimeError('synthetic failure')):
            with self.subTest(kind=type(failure).__name__):
                self.results = []
                self.r._counter = 7
                self.s.deadline.firings = 0
                self.s.rehash.side_effect = [None, failure]
                with self.children(), self.assertRaises(type(failure)) as caught:
                    d._step_4_parallel(self.s, self.r, ('alpha', 'beta'))
                self.assertIs(caught.exception, failure)
                self.assert_prefix(1)

    def test_token_read_failure_and_interrupt_also_clean_up(self):
        for failure in (OSError('synthetic read failure'), KeyboardInterrupt()):
            with self.subTest(kind=type(failure).__name__):
                self.results = []
                self.r._counter = 7
                self.s.deadline.firings = 0
                def dispatch(*args):
                    base, results, state = self.dispatch(*args)
                    from dataclasses import replace
                    results[0] = replace(results[0], exit_status=2)
                    return base, results, state
                with mock.patch.object(d, '_dispatch', side_effect=dispatch), \
                        mock.patch.object(d.RunnerResult, 'token', side_effect=failure), \
                        self.assertRaises(type(failure)) as caught:
                    d._step_4_parallel(self.s, self.r, ('alpha', 'beta'))
                self.assertIs(caught.exception, failure)
                self.assert_prefix(1)

    def test_success_keeps_both_children_and_accounts_each(self):
        with self.children():
            records = d._step_4_parallel(self.s, self.r, ('alpha', 'beta'))
        self.assertEqual([record.status for record in records], ['ok', 'ok'])
        self.assert_prefix(2)

    def test_registered_refusal_still_stops_at_the_same_child(self):
        self.s.specs = {'alpha': {}, 'beta': {}}
        with self.children(), mock.patch.object(d, 'classify_step4_exit', return_value='refused'):
            records = d._step_4_parallel(self.s, self.r, ('alpha', 'beta'))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].status, 'unclassified_refusal')
        self.assert_prefix(1)
