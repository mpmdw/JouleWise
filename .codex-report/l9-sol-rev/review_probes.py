"""Independent synthetic dispatch probes; no real data or full S10 chain.

Run from the repository with PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 and a
TMPDIR under /private/tmp. Step bodies are explicitly test doubles; every
injected deadline is produced by the real governed 59-pulse projection.
"""
import contextlib
import io
import json
import hashlib
import sys
import tarfile
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from joulewise import cli, calibration_bracketing as cb, powermetrics_fiducial as pf, whole_window as ww
from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.deadline_observer import observe_wall_deadline
from tests.b5_analysis.support_s10.calibration import self_consistent_calibration
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER, JumpingClock


class DispatchProbes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence, cls.raw, cls.events = self_consistent_calibration(protocol_id=pf.PROTOCOL_ID)

    def detection(self):
        return pf.rederive_detection_from_artifacts(
            self.raw, self.events, self.evidence['clock_anchor'], protocol_id=pf.PROTOCOL_ID)

    def execute(self, firing_step=None, *, swallowed=False, observer=True):
        executed = []

        def body(step):
            def run(s, r):
                executed.append(step)
                trigger = None
                if step == firing_step:
                    with mock.patch.object(pf, 'time', JumpingClock()):
                        result = self.detection()
                    trigger = result.projection_budget_trigger
                    self.assertEqual(trigger, 'wall_deadline')
                    if swallowed:
                        try:
                            raise ValueError('simulated downstream refusal swallowed')
                        except ValueError:
                            pass
                # Model a caller that would accept a changed number after a firing.
                item = s.write('probe_' + step, 'outputs/probe-' + step + '.json',
                               {'number': 2 if trigger else 1})
                return [s.record(step, outputs=[item])]
            return run

        @contextlib.contextmanager
        def blind_observer():
            class Blind:
                firings = 0
            yield Blind()

        with tempfile.TemporaryDirectory(prefix='sol-dispatch-') as tmp:
            root = Path(tmp)
            (root / 'repo').mkdir()
            index = root / 'index.json'
            index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(d, 'STEPS', tuple((step, body(step)) for step in d.STEP_IDS)))
                if not observer:
                    stack.enter_context(mock.patch(
                        'joulewise.b5_analysis.deadline_observer.observe_wall_deadline', blind_observer))
                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                status = d.run('blind-dry-run', index, root / 'custody',
                               _test_repo_root=root / 'repo', _git=lambda _: 'b' * 40)
            folder = root / 'custody/dry-run'
            record = json.loads((folder / 'B5-BLIND-DRY-RUN-RECORD.json').read_bytes())
            public = sorted(str(p.relative_to(folder)) for p in folder.rglob('*')
                            if p.is_file() and not p.is_relative_to(folder / 'restricted'))
            payloads = {row['step']: [(folder / 'restricted' / out['name']).read_bytes()
                                     for out in row['outputs']] for row in record['steps']}
        return status, record, executed, public, payloads

    def test_every_step_refuses_a_real_firing_even_when_the_caller_returns_ok(self):
        clean = self.execute()
        self.assertEqual(clean[0], 0)
        for index, step in enumerate(d.STEP_IDS):
            with self.subTest(step=step):
                status, record, ran, public, payloads = self.execute(step)
                rows = record['steps']
                self.assertEqual(status, 2)
                self.assertEqual(ran, list(d.STEP_IDS[:index + 1]))
                self.assertEqual((rows[index]['status'], rows[index]['refusal']),
                                 ('tooling_refusal', 'calibration_wall_deadline_fired'))
                self.assertTrue(all(row['status'] == 'not_run' for row in rows[index + 1:]))
                self.assertEqual(public, ['B5-BLIND-DRY-RUN-RECORD.json'])
                self.assertEqual(rows[:index], clean[1]['steps'][:index])
                for prior in d.STEP_IDS[:index]:
                    self.assertEqual(payloads[prior], clean[4][prior])
                print('STEP', step, 'wall_deadline -> tooling_refusal; later=not_run; earlier=identical; public=closed-record')

    def test_swallowed_exception_cannot_hide_the_firing(self):
        status, record, *_ = self.execute('9b', swallowed=True)
        row = next(row for row in record['steps'] if row['step'] == '9b')
        self.assertEqual((status, row['refusal']), (2, 'calibration_wall_deadline_fired'))

    def test_mutation_removing_observation_accepts_a_changed_number(self):
        clean = self.execute()
        status, record, _, _, payloads = self.execute('5', observer=False)
        self.assertEqual(status, 0)
        self.assertTrue(all(row['status'] == 'ok' for row in record['steps']))
        self.assertNotEqual(payloads['5'], clean[4]['5'])
        print('MUTATION observer removed: step 5 ok with changed number; discriminating probe confirmed')

    def test_real_thread_firing_is_observed(self):
        results = []
        with observe_wall_deadline() as observer, mock.patch.object(pf, 'time', JumpingClock()):
            thread = threading.Thread(target=lambda: results.append(self.detection()))
            thread.start()
            thread.join()
        self.assertEqual([r.projection_budget_trigger for r in results], ['wall_deadline'])
        self.assertEqual(observer.firings, 1)

    def test_existing_tool_and_nested_observer_are_preserved(self):
        mon = sys.monitoring
        tool = next(n for n in range(6) if mon.get_tool(n) is None)
        mon.use_tool_id(tool, 'independent-review-existing-tool')
        try:
            with observe_wall_deadline() as first, observe_wall_deadline() as second, \
                    mock.patch.object(pf, 'time', JumpingClock()):
                self.detection()
            self.assertEqual((first.firings, second.firings), (1, 1))
            self.assertEqual(mon.get_tool(tool), 'independent-review-existing-tool')
        finally:
            mon.free_tool_id(tool)

    def test_actual_tool_exhaustion_is_a_classified_refusal(self):
        mon = sys.monitoring
        owned = []
        try:
            for tool in range(6):
                if mon.get_tool(tool) is None:
                    mon.use_tool_id(tool, 'independent-review-occupied')
                    owned.append(tool)
            status, record, ran, *_ = self.execute()
            self.assertEqual(status, 2)
            self.assertEqual(record['steps'][0]['refusal'], 'calibration_deadline_observer_unavailable')
            self.assertEqual(ran, ['0'])
        finally:
            for tool in owned:
                mon.free_tool_id(tool)


class RealSiteProbes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='sol-real-sites-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        with tarfile.open(ARCHIVE) as archive:
            archive.extractall(cls.root, members=[m for m in archive.getmembers() if m.name.startswith(MEMBER)],
                               filter='data')
        cls.member = cls.root / MEMBER

    def command(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                status = cli.main([str(a) for a in argv])
            except SystemExit as exc:
                status = exc.code
        return status, out.getvalue(), err.getvalue()

    def test_exact_cli_streams_and_summary_bytes_with_and_without_cache(self):
        target = self.root / 'same-output.json'
        refits = []
        original = pf.rederive_detection_from_artifacts

        def count(*args, **kwargs):
            refits.append(1)
            return original(*args, **kwargs)

        def run():
            strict = self.command(['validate-bundle', '--strict', self.member])
            reduction = self.command(['reduce', self.member, '--output', target])
            payload = target.read_bytes()
            target.unlink()
            self.assertEqual((strict[0], reduction[0]), (0, 0))
            return strict, reduction, payload

        with mock.patch.object(pf, 'rederive_detection_from_artifacts', count):
            plain = run()
            self.assertEqual(len(refits), 2)
            refits.clear()
            with ww.shared_instrument_calibration_physics_cache({}) as cache:
                cold = run()
                warm = run()
            self.assertEqual(len(refits), 1)
            self.assertEqual(cold, plain)
            self.assertEqual(warm, plain)
        print('CACHE exact CLI stdout/stderr/status + summary bytes identical; uncached refits=2; shared cold+warm=1; keys=', len(cache))
        print('CACHE summary SHA256', hashlib.sha256(plain[2]).hexdigest())

    def test_real_bracket_candidate_loader_observes_forced_firing(self):
        directory = self.member / 'instrument_calibration'
        with observe_wall_deadline() as observer, mock.patch.object(pf, 'time', JumpingClock()):
            result = cb.load_calibration_candidate(directory, runs_root=self.member, mode='read_replay')
        self.assertIsNone(result)
        self.assertEqual(observer.firings, 1)
        print('BRACKET real load_calibration_candidate: candidate refused; observed wall firings=1')


if __name__ == '__main__':
    unittest.main(verbosity=2)
