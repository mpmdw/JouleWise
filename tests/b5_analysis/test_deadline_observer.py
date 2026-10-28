"""Any calibration wall-deadline firing in a dry run is one tooling refusal (L9-REV-1 MINOR-5).

Forced firings use powermetrics_fiducial's clock only (a host that blew the
frozen 120 s deadline); the deadline, the budgets and every governed byte are
unchanged. Synthetic: one committed S10 ALPHA member.
"""
import contextlib
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import cli, powermetrics_fiducial as pf, whole_window as ww
from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.deadline_observer import (
    CALIBRATION_WALL_DEADLINE, OBSERVER_UNAVAILABLE, observe_wall_deadline)
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER, JumpingClock


def quiet(function, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            return function(*args, **kwargs)
        except SystemExit as exc:
            return exc.code


def forced():
    return mock.patch.object(pf, 'time', JumpingClock())


class ObserverSitesTests(unittest.TestCase):
    """Each refit path the reviewer listed: the observer sees its firing."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='deadline-observer-')
        cls.addClassCleanup(cls.tmp.cleanup)
        with tarfile.open(ARCHIVE) as blob:
            members = [m for m in blob.getmembers() if m.name.startswith(MEMBER)]
            blob.extractall(Path(cls.tmp.name), members=members, filter='data')
        cls.member = Path(cls.tmp.name) / MEMBER
        cal = cls.member / 'instrument_calibration'
        cls.evidence = json.loads((cal / 'instrument_evidence.json').read_bytes())
        cls.raw = (cal / 'raw/powermetrics.plist').read_bytes()
        cls.events = (cal / 'events.jsonl').read_bytes()

    def observed(self, call):
        with observe_wall_deadline() as observer:
            self.assertIsNotNone(observer)
            value = call()
        return observer.firings, value

    def test_unforced_refits_are_not_firings(self):
        firings, _ = self.observed(lambda: pf.verify_stored_evidence_physics(self.evidence, self.raw, self.events))
        self.assertEqual(firings, 0)

    def test_step2_reduce_firing_is_observed(self):
        out = Path(self.tmp.name) / 'reduce.json'
        with forced():
            firings, code = self.observed(lambda: quiet(cli.main, ['reduce', str(self.member), '--output', str(out)]))
        self.assertEqual(code, 0, 'reduce itself does not refuse a firing')
        self.assertEqual(firings, 1)

    def test_bracket_refit_firing_is_observed(self):
        # bracket.py -> calibration_bracketing -> verify_stored_evidence_physics (not cached).
        def call():
            try:
                return pf.verify_stored_evidence_physics(self.evidence, self.raw, self.events)
            except ValueError as exc:
                return exc
        with forced():
            firings, value = self.observed(call)
        self.assertIsInstance(value, ValueError)
        self.assertEqual(firings, 1)

    def test_neg8_replay_strict_invalid_callback_firing_is_observed(self):
        # sources_replay -> _derived_neg8_decision's strict_invalid callback: without the
        # observer a firing here is a strict_invalid loss of a real reference.
        self.assertFalse(ww._archive_reference_strict_invalid('end', self.member))
        with forced():
            firings, invalid = self.observed(lambda: ww._archive_reference_strict_invalid('end', self.member))
        self.assertTrue(invalid)
        self.assertEqual(firings, 1)

    def test_neg8_energy_rederivation_firing_is_observed(self):
        with forced():
            firings, value = self.observed(lambda: ww._reference_energy_evidence_detail(self.member))
        self.assertEqual(value[3], ww.ENERGY_CAUSE_PRECHECK_INELIGIBLE)
        self.assertEqual(firings, 1)

    def test_observer_resolves_a_wrapped_projection(self):
        original = pf.detect_pulses

        def wrapper(*args, **kwargs):
            return original(*args, **kwargs)
        wrapper.__wrapped__ = original
        with mock.patch.object(pf, 'detect_pulses', wrapper), forced():
            firings, _ = self.observed(lambda: ww._archive_reference_strict_invalid('end', self.member))
        self.assertEqual(firings, 1)

    def test_no_free_monitoring_tool_yields_none(self):
        with mock.patch('sys.monitoring.get_tool', return_value='busy'):
            with observe_wall_deadline() as observer:
                self.assertIsNone(observer)


class SharedCacheSiteTests(unittest.TestCase):
    """MINOR-3: the NEG-8 energy re-derivation site under the run cache."""

    def test_reference_energy_evidence_uses_the_run_cache(self):
        with tempfile.TemporaryDirectory(prefix='energy-cache-') as tmp:
            with tarfile.open(ARCHIVE) as blob:
                blob.extractall(tmp, members=[m for m in blob.getmembers() if m.name.startswith(MEMBER)],
                                filter='data')
            member = Path(tmp) / MEMBER
            calls = []
            original = pf.rederive_detection_from_artifacts

            def counted(*args, **kwargs):
                calls.append(1)
                return original(*args, **kwargs)
            with mock.patch.object(pf, 'rederive_detection_from_artifacts', counted):
                plain = [ww._reference_energy_evidence_detail(member) for _ in range(2)]
                self.assertEqual(len(calls), 2)
                calls.clear()
                with ww.shared_instrument_calibration_physics_cache({}):
                    shared = [ww._reference_energy_evidence_detail(member) for _ in range(2)]
                self.assertEqual(len(calls), 1)
            self.assertEqual(plain, shared)


def driver(steps, *, observer=None):
    with tempfile.TemporaryDirectory(prefix='deadline-driver-') as tmp:
        root = Path(tmp)
        (root / 'repo').mkdir()
        index = root / 'index.json'
        index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
        patches = [mock.patch.object(d, 'STEPS', tuple(steps))]
        if observer is not None:
            patches.append(mock.patch('joulewise.b5_analysis.deadline_observer.observe_wall_deadline', observer))
        with contextlib.ExitStack() as stack:
            for patch in patches:
                stack.enter_context(patch)
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
            try:
                d.run('blind-dry-run', index, root / 'custody', _test_repo_root=root / 'repo', _git=lambda repo: 'b' * 40)
            except Exception:  # noqa: BLE001 - only the step records matter here
                pass


class DriverDeadlineTests(unittest.TestCase):
    def steps(self, firing_step):
        member = ObserverSitesTests.member

        def step(name):
            def function(s, r):
                if name == firing_step:
                    with forced():
                        ww._archive_reference_strict_invalid('end', member)
                return [s.record(name)]
            return function
        return [(name, step(name)) for name in ('0', '1', '2', '3')]

    @classmethod
    def setUpClass(cls):
        ObserverSitesTests.setUpClass()
        cls.addClassCleanup(ObserverSitesTests.tmp.cleanup)

    def run_rows(self, firing_step, **kwargs):
        rows = []

        def capture(**record_kwargs):
            rows.extend(record.as_dict() for record in record_kwargs['steps'])
            raise RuntimeError('captured')
        with mock.patch.object(d, 'build_dry_run_record', side_effect=capture):
            driver(self.steps(firing_step), **kwargs)
        return [(row['step'], row['status'], row['refusal']) for row in rows]

    def test_firing_step_refuses_with_the_single_code_and_later_steps_do_not_run(self):
        rows = self.run_rows('2')
        self.assertEqual(rows[:4], [('0', 'ok', None), ('1', 'ok', None),
                                    ('2', 'tooling_refusal', CALIBRATION_WALL_DEADLINE), ('3', 'not_run', None)])
        self.assertIn(CALIBRATION_WALL_DEADLINE, d.refusal_classes()['tooling_refusal'])

    def test_unforced_records_equal_a_run_without_the_observer(self):
        @contextlib.contextmanager
        def counting_only():
            class Never:
                firings = 0
            yield Never()
        with_observer = self.run_rows(None)
        without = self.run_rows(None, observer=counting_only)
        self.assertEqual(with_observer, without)
        self.assertTrue(all(status == 'ok' for _, status, _ in with_observer[:4]))

    def test_without_the_observer_a_firing_inside_an_ok_step_passes(self):
        # Mutation proof for the refusal above.
        @contextlib.contextmanager
        def blind():
            class Never:
                firings = 0
            yield Never()
        rows = self.run_rows('2', observer=blind)
        self.assertEqual(rows[2], ('2', 'ok', None))

    def test_unavailable_observer_refuses_the_first_step(self):
        @contextlib.contextmanager
        def unavailable():
            yield None
        rows = self.run_rows(None, observer=unavailable)
        self.assertEqual(rows[0], ('0', 'tooling_refusal', OBSERVER_UNAVAILABLE))
        self.assertEqual(rows[1][1], 'not_run')
        self.assertIn(OBSERVER_UNAVAILABLE, d.refusal_classes()['tooling_refusal'])


if __name__ == '__main__':
    unittest.main()


class MintRefusalCodeTests(unittest.TestCase):
    """L9-REV-1 MINOR-5: the step-5 mint's consumption-session refusal is classified."""

    def result(self, stderr):
        tmp = Path(tempfile.mkdtemp(prefix='mint-refusal-'))
        self.addCleanup(lambda: __import__('shutil').rmtree(tmp, ignore_errors=True))
        (tmp / 'out.log').write_text('')
        (tmp / 'err.log').write_text(stderr)
        return d.RunnerResult(2, tmp / 'out.log', tmp / 'err.log')

    def record(self, code):
        return d.step_record('5', exit_status=2, refusal_code=code, classes=d.refusal_classes())

    def test_consumption_session_refusal_is_a_classified_tooling_code(self):
        result = self.result('error: alpha producer report: authenticated whole-window consumption refused: '
                             'whole_window_verdict_provenance_invalid\n')
        # Counterfactual: the raw token is the input label, an unclassified refusal.
        self.assertEqual(self.record(result.token()).status, 'unclassified_refusal')
        code = d.mint_refusal_code(result, result.token())
        self.assertEqual(code, d.MINT_CONSUMPTION_REFUSED)
        self.assertEqual((self.record(code).status, self.record(code).refusal),
                         ('tooling_refusal', d.MINT_CONSUMPTION_REFUSED))

    def test_other_mint_refusals_keep_their_token(self):
        result = self.result('error: floor_mint_kept_unit_mismatch: manifest exclusions_sha256 differs\n')
        self.assertEqual(d.mint_refusal_code(result, result.token()), 'floor_mint_kept_unit_mismatch')


class ObserverSetupFailureTests(unittest.TestCase):
    """L9-SOL-REV MINOR-1: setup failures are the classified refusal, with a record."""

    def test_missing_monitoring_api_yields_none(self):
        with mock.patch.object(__import__('sys'), 'monitoring', None):
            with observe_wall_deadline() as observer:
                self.assertIsNone(observer)

    def test_lost_tool_id_race_yields_none_and_keeps_the_winner(self):
        import sys
        monitoring = sys.monitoring
        reserved = []
        original = monitoring.use_tool_id

        def race(tool, name):
            # Another tool takes the id between the availability read and the reservation.
            original(tool, 'competing-test-tool')
            reserved.append(tool)
            return original(tool, name)
        try:
            with mock.patch.object(monitoring, 'use_tool_id', race):
                with observe_wall_deadline() as observer:
                    self.assertIsNone(observer)
            self.assertEqual(monitoring.get_tool(reserved[0]), 'competing-test-tool')
        finally:
            for tool in reserved:
                monitoring.free_tool_id(tool)

    def test_driver_records_the_classified_refusal_when_setup_fails(self):
        rows = []

        def capture(**record_kwargs):
            rows.extend((r.step, r.status, r.refusal) for r in record_kwargs['steps'])
            raise RuntimeError('captured')
        steps = [(name, lambda s, r, name=name: [s.record(name)]) for name in ('0', '1', '2')]
        with mock.patch.object(__import__('sys'), 'monitoring', None), \
             mock.patch.object(d, 'build_dry_run_record', side_effect=capture):
            driver(steps)
        self.assertEqual(rows[0], ('0', 'tooling_refusal', OBSERVER_UNAVAILABLE))
        self.assertEqual([status for _, status, _ in rows[1:]], ['not_run', 'not_run'])
