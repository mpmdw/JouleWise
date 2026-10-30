"""A calibration refit that hits the wall deadline stops the dry run (ED-RULING item 6 condition).

The governed projection's 120 s host-safety deadline is left as it is. These
tests force it by giving powermetrics_fiducial a clock that jumps past it,
then run the real step-1/step-2 programs on one committed synthetic S10 member.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import cli, powermetrics_fiducial as pf
from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER, JumpingClock

import contextlib
import io
import tarfile


def quiet_cli(*argv):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            return cli.main([str(arg) for arg in argv])
        except SystemExit as exc:
            return exc.code


def legacy_step_2(s, r):
    """step_2 exactly as at BASE_HEAD 0576a734d, for the byte-identity check."""
    from joulewise.cli import main
    outputs = []
    for pack, run_id, bundle in s.kept_bundles():
        output = s.path('rereduced/'+pack+'/'+run_id+'.rereduced.json')
        result, found, code, exit_status = s.invoke(r, main, ['reduce', bundle, '--output', output], step='2', window=pack,
                                                     outputs=[('rereduced_'+pack+'_'+run_id, output)])
        outputs.extend(found)
        if exit_status: return [s.record('2', window=pack, exit_status=exit_status, code=code, outputs=outputs)]
    return [s.record('2', outputs=outputs)]


class StepState:
    """The RunState surface step 2 uses, with the driver's own methods."""
    path = d.RunState.path
    register = d.RunState.register
    record = d.RunState.record
    invoke = d.RunState.invoke
    rehash = d.RunState.rehash

    def __init__(self, restricted, bundles):
        self.restricted = restricted
        self.outputs = {}
        self.classes = d.refusal_classes()
        self.contexts = ()
        self.bundles = bundles

    def kept_bundles(self):
        return list(self.bundles)


class DeadlineRunner(d.StepRunner):
    """Real StepRunner; the clock jumps only during the program calls listed."""
    forced_calls = ()

    def __init__(self, restricted):
        super().__init__(restricted)
        self.calls = 0

    def run(self, main, argv, **kwargs):
        self.calls += 1
        if self.calls in self.forced_calls:
            with mock.patch.object(pf, 'time', JumpingClock()):
                return super().run(main, argv, **kwargs)
        return super().run(main, argv, **kwargs)


class DeadlineTripwireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='deadline-tripwire-')
        cls.addClassCleanup(cls.tmp.cleanup)
        root = Path(cls.tmp.name)
        with tarfile.open(ARCHIVE) as blob:
            members = [m for m in blob.getmembers() if m.name.startswith(MEMBER)]
            blob.extractall(root / 'source', members=members, filter='data')
        cls.member = root / 'source' / MEMBER
        cls.serial = 0

    def custody(self):
        type(self).serial += 1
        restricted = Path(self.tmp.name) / ('custody-' + str(self.serial)) / 'restricted'
        restricted.mkdir(parents=True)
        return restricted

    def step_2(self, forced_calls, function=d.step_2):
        restricted = self.custody()
        bundles = [('alpha', 'first', self.member), ('alpha', 'second', self.member)]
        state = StepState(restricted, bundles)
        runner = DeadlineRunner(restricted)
        runner.forced_calls = forced_calls
        records = function(state, runner)
        return state, restricted, [record.as_dict() for record in records]

    def test_step1_strict_validation_refuses_a_deadline_hit_refit(self):
        self.assertEqual(quiet_cli('validate-bundle', '--strict', self.member), 0)
        with mock.patch.object(pf, 'time', JumpingClock()):
            self.assertEqual(quiet_cli('validate-bundle', '--strict', self.member), 2)
        self.assertIn('kept_bundle_strict_validation_failed', d.refusal_classes()['tooling_refusal'])

    def test_tripwire_refuses_a_deadline_hit_rereduction_and_admits_the_control(self):
        out = Path(self.tmp.name) / 'direct'
        out.mkdir(exist_ok=True)
        self.assertEqual(quiet_cli('reduce', self.member, '--output', out / 'control.json'), 0)
        d.require_rereduction_matches_stored(self.member, out / 'control.json')
        with mock.patch.object(pf, 'time', JumpingClock()):
            self.assertEqual(quiet_cli('reduce', self.member, '--output', out / 'forced.json'), 0)
        forced = json.loads((out / 'forced.json').read_bytes())
        self.assertEqual(forced['status'], 'succeeded')
        self.assertEqual(forced['energy_uncertainty_status'], 'not_estimable')
        with self.assertRaises(AnalysisRefusal) as caught:
            d.require_rereduction_matches_stored(self.member, out / 'forced.json')
        self.assertEqual(caught.exception.code, d.REREDUCTION_REFIT_DIFFERS)

    def test_step2_deadline_hit_is_a_tooling_refusal_with_no_output_past_it(self):
        state, restricted, records = self.step_2(forced_calls=(2,))
        self.assertEqual(len(records), 1)
        row = records[0]
        self.assertEqual((row['step'], row['window'], row['status'], row['refusal']),
                         ('2', 'alpha', 'tooling_refusal', d.REREDUCTION_REFIT_DIFFERS))
        self.assertIn(d.REREDUCTION_REFIT_DIFFERS, d.refusal_classes()['tooling_refusal'])
        # The first, unforced re-reduction is the only registered output.
        self.assertEqual(list(state.outputs), ['rereduced_alpha_first'])
        self.assertEqual([o['name'] for o in row['outputs']], ['rereduced/alpha/first.rereduced.json'])
        self.assertEqual(sorted(p.name for p in (restricted / 'rereduced/alpha').iterdir()),
                         ['first.rereduced.json'])

    def test_without_the_tripwire_the_forced_deadline_passes_silently(self):
        # Mutation proof: with the check removed, the same forced run records ok
        # and registers a changed re-reduction, so the refusal above is the tripwire's.
        with mock.patch.object(d, 'require_rereduction_matches_stored', lambda bundle, output: None):
            state, restricted, records = self.step_2(forced_calls=(2,))
        self.assertEqual([r['status'] for r in records], ['ok'])
        second = json.loads((restricted / 'rereduced/alpha/second.rereduced.json').read_bytes())
        self.assertEqual(second['energy_uncertainty_status'], 'not_estimable')

    def test_unforced_step2_record_and_outputs_are_byte_identical_to_base(self):
        _, new_root, new = self.step_2(forced_calls=())
        _, old_root, old = self.step_2(forced_calls=(), function=legacy_step_2)
        self.assertEqual(new, old)
        self.assertEqual([r['status'] for r in new], ['ok'])
        for output in new[0]['outputs']:
            self.assertEqual((new_root / output['name']).read_bytes(), (old_root / output['name']).read_bytes())

    def test_failed_reduce_leaves_no_unregistered_output(self):
        # NIT-5: a non-zero reduce exit that still wrote its output is a refusal with no file left.
        class FailingRunner(DeadlineRunner):
            def run(self, main, argv, **kwargs):
                result = super().run(main, argv, **kwargs)
                return replace(result, exit_status=2) if self.calls == 2 else result
        from dataclasses import replace
        restricted = self.custody()
        state = StepState(restricted, [('alpha', 'first', self.member), ('alpha', 'second', self.member)])
        records = [r.as_dict() for r in d.step_2(state, FailingRunner(restricted))]
        self.assertEqual((records[0]['step'], records[0]['window'], records[0]['exit_status']), ('2', 'alpha', 2))
        self.assertEqual(list(state.outputs), ['rereduced_alpha_first'])
        self.assertEqual(sorted(p.name for p in (restricted / 'rereduced/alpha').iterdir()), ['first.rereduced.json'])

    def test_driver_stops_at_the_refused_step(self):
        ran = []

        def ok(step):
            def function(s, r):
                ran.append(step)
                return [s.record(step)]
            return function

        def refused(s, r):
            ran.append('2')
            return [s.record('2', window='alpha', exit_status=2, code=d.REREDUCTION_REFIT_DIFFERS)]
        steps = [(step, refused if step == '2' else ok(step)) for step in d.STEP_IDS]
        with tempfile.TemporaryDirectory(prefix='deadline-driver-') as tmp:
            root = Path(tmp)
            (root / 'repo').mkdir()
            index = root / 'index.json'
            index.write_bytes(d._canonical({'schema': 'joulewise.b5_window_index.v1', 'attempts': []}))
            with mock.patch.object(d, 'STEPS', steps), \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = d.run('blind-dry-run', index, root / 'custody', _test_repo_root=root / 'repo',
                             _git=lambda repo: 'b' * 40)
        self.assertEqual(code, 2)
        self.assertEqual(ran, list(d.STEP_IDS[:d.STEP_IDS.index('2') + 1]))


if __name__ == '__main__':
    unittest.main()
