"""Smoke G2: the R1 -> W1 chain doc is a tested script; the kit is regenerated before --check."""
import contextlib
from functools import partial
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_r1_to_w1_chain as chain
from scripts import align_w1_budget_procedure as procedure
from tests.align.test_w1_kit_r10 import X_G_PHASES

DOC = Path(__file__).resolve().parents[2] / 'docs/align/R1-TO-W1-CHAIN.md'


def doc_commands():
    block = re.search(r'```sh\n(.*?)```', DOC.read_text(), re.S).group(1)
    commands, current = [], ''
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith('#') or re.match(r'^[A-Z]+=', line):
            continue
        current += line.rstrip('\\').strip() + ' '
        if not line.rstrip().endswith('\\'):
            commands.append(shlex.split(current))
            current = ''
    return commands


class ChainDocTests(unittest.TestCase):
    def test_the_doc_block_is_exactly_the_scripts_command_sequence(self):
        scripted = [shlex.split(c) for _s, c in chain.render()]
        self.assertEqual(doc_commands(), scripted)

    def test_kit_regeneration_sits_between_installing_the_slots_and_the_check(self):
        steps = [s for s, _c in chain.render()]
        self.assertEqual(steps, list(chain.STEPS))
        self.assertLess(steps.index('install-slots'), steps.index('regenerate-kit'))
        self.assertLess(steps.index('regenerate-kit'), steps.index('kit-check'))
        commands = dict(chain.render())
        self.assertTrue(commands['regenerate-kit'].endswith('scripts/align_v4_kit.py'))
        self.assertTrue(commands['kit-check'].endswith('scripts/align_v4_kit.py --check'))
        self.assertLess(steps.index('derive-contrast'), steps.index('regenerate-kit'))


class ChainScriptTests(unittest.TestCase):
    def run_chain(self, *extra, runner=None, fail_at=None):
        calls = []

        def fake(argv, **kwargs):
            calls.append(argv)
            code = 1 if fail_at and fail_at in ' '.join(argv) else 0
            return subprocess.CompletedProcess(argv, code, '{"contrast_g0_cap_s": 0}' if 'derive-contrast' in argv else '', '')
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = chain.main(['--run-dir', 'RUN', '--slots', 'SLOTS', '--work', str(Path(tmp) / 'work'), *extra],
                                  runner=runner or fake, root=tmp)
        return code, calls, out.getvalue()

    def test_dry_run_prints_the_eight_steps_and_runs_nothing(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(chain.main(['--run-dir', 'RUN', '--slots', 'SLOTS', '--work', 'WORK', '--dry-run']), 0)
        self.assertEqual(buffer.getvalue().count('# '), 8)

    def test_all_steps_run_in_order_and_a_failure_stops_the_chain(self):
        code, calls, _ = self.run_chain()
        self.assertEqual((code, len(calls)), (0, 8))
        self.assertEqual(calls[-2][-1], 'scripts/align_v4_kit.py')          # regenerate before --check
        self.assertEqual(calls[-1][-1], '--check')
        code, calls, _ = self.run_chain(fail_at='backfill-turn-counts')
        self.assertEqual(code, 1)
        self.assertEqual(len(calls), 3)
        code, calls, output = self.run_chain(fail_at='--check')
        self.assertEqual((code, len(calls)), (1, 8))
        self.assertIn('expected until', output)

    def test_until_stops_early(self):
        code, calls, _ = self.run_chain('--until', 'install-slots')
        self.assertEqual((code, len(calls)), (0, 4))

    def test_steps_one_to_three_run_for_real_on_a_synthetic_lane_record(self):
        # The real exporter and backfills (no kit run) on a lane-shaped synthetic record.
        from tests.align import test_r1_turn_counts_export as export_tests
        with tempfile.TemporaryDirectory() as tmp:
            case = export_tests.ExportTests('test_export_matches_the_driver_and_binds_every_input_file')
            case.setUp()
            self.addCleanup(case.tearDown) if hasattr(case, 'tearDown') else None
            export_tests.write_bundles(case.run_dir)
            lane = json.loads((Path(case.tmp) / 'registration/r1_slots.json').read_text())
            for key in ('admitted_turns', 'x7', 'phases_s'):          # a lane record predates R10-4 / R16
                lane['x_g'].pop(key, None)
            for row in lane['deadman_budget']:
                for key in ('turn_decode_counts', 'turn_completed', 'turn_counts_source_sha256'):
                    row.pop(key, None)
            slots = Path(tmp) / 'lane_slots.json'
            slots.write_text(json.dumps(lane))
            root = Path(__file__).resolve().parents[2]
            work = Path(tmp) / 'work'
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = chain.main(['--run-dir', str(case.run_dir), '--slots', str(slots), '--work', str(work),
                                   '--until', 'backfill-counts'], root=root)
            self.assertEqual(code, 0, out.getvalue())
            done = json.loads((work / 'r1_slots.json').read_text())
            self.assertTrue(all(r['turn_counts_source_sha256'] for r in done['deadman_budget']))
            self.assertIn('admitted_turns', done['x_g'])


class ContrastWriterTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.registration = self.root / chain.REGISTRATION
        self.registration.mkdir(parents=True)
        self.inputs = self.registration / 'inputs.json'
        self.installed = self.registration / 'r1_slots.json'
        self.slots = self.root / 'counted.json'
        self.slots.write_text(json.dumps({
            'x_g': {'status': 'measured', 'g0_outcome': 'released', 'g0_wait_s': 120.0,
                    'admitted_turns': 12, 'x7': False, 'phases_s': dict(X_G_PHASES, decode=712.0)},
        }))
        runtime = self.root / 'configs/align/v4/r1_runtime.json'
        runtime.parent.mkdir(parents=True)
        runtime.write_text('{"g0_timeout_s": 1200}')
        self.base_policy = {'g0_cap_s': 600, 'classification_sha256': 'b' * 64}
        self.write_inputs(self.base_policy)
        self.enterContext(patch.object(procedure.kit, 'w1_contrast_g0_cap',
                                       partial(procedure.kit.w1_contrast_g0_cap, root=self.root)))
        self.printed = self.derive(self.slots)
        self.derived = json.loads(self.printed)
        self.assertEqual(self.derived['contrast_g0_cap_s'], 238)
        self.assertFalse(self.derived['contrast_fit']['fits'])

    def write_inputs(self, policy):
        self.inputs.write_text(json.dumps({'R1': {'thermal_policy': policy}, 'WP18': {'X': {'max_turns': 12}}},
                                          indent=2, sort_keys=True) + '\n')
        return self.inputs.read_bytes()

    def derive(self, slots):
        before = self.inputs.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = procedure.main(['derive-contrast', '--r1-slots', str(slots), '--inputs', str(self.inputs)])
        self.assertEqual(code, 0)
        self.assertEqual(self.inputs.read_bytes(), before)
        return out.getvalue()

    def run_writer(self, *flags, child_code=0):
        work = self.root / 'work'
        commands = [shlex.split(command) for _, command in chain.render('RUN', 'SLOTS', str(work))]
        calls = []

        def runner(argv, **kwargs):
            self.assertEqual(argv, commands[len(calls)])
            step = chain.STEPS[len(calls)]
            calls.append(step)
            if step == 'install-slots':
                self.installed.write_bytes(self.slots.read_bytes())
            if step == 'derive-contrast':
                return subprocess.CompletedProcess(argv, child_code, self.derive(self.installed), '')
            return subprocess.CompletedProcess(argv, 0, '', '')

        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = chain.main(['--run-dir', 'RUN', '--slots', 'SLOTS', '--work', str(work), *flags],
                              runner=runner, root=self.root)
        self.assertEqual(self.installed.read_bytes(), self.slots.read_bytes())
        return code, calls, out.getvalue(), err.getvalue()

    def assert_preserved(self, before):
        after = self.inputs.read_bytes()
        self.assertEqual(sha256(after).hexdigest(), sha256(before).hexdigest())
        self.assertEqual(after, before)

    def assert_step_five_refusal(self, before, field):
        code, calls, out, err = self.run_writer('--write-contrast')
        self.assert_preserved(before)
        self.assertEqual(calls, list(chain.STEPS[:5]), out)
        self.assertNotEqual(code, 0)
        self.assertIn('derive-contrast', err)
        self.assertIn(field, err)
        self.assertNotIn('Traceback', err)

    def test_null_policy_is_a_controlled_refusal(self):
        self.assert_step_five_refusal(self.write_inputs(None), 'thermal_policy')

    def test_conflicting_existing_value_is_preserved(self):
        policy = dict(self.base_policy, **self.derived)
        policy['contrast_g0_cap_s'] = 239
        self.assert_step_five_refusal(self.write_inputs(policy), 'contrast_g0_cap_s')

    def test_matching_values_replay_without_changing_bytes(self):
        before = self.write_inputs(dict(self.base_policy, **self.derived))
        code, calls, _, _ = self.run_writer('--write-contrast')
        self.assertEqual((code, calls), (0, list(chain.STEPS)))
        self.assert_preserved(before)

    def test_missing_values_are_added_to_a_present_policy(self):
        before = self.inputs.read_bytes()
        code, calls, _, _ = self.run_writer('--write-contrast')
        self.assertEqual((code, calls), (0, list(chain.STEPS)))
        expected = json.loads(before)
        expected['R1']['thermal_policy'].update(self.derived)
        self.assertEqual(json.loads(self.inputs.read_bytes()), expected)

    def test_print_only_does_not_require_a_thermal_policy(self):
        before = self.write_inputs(None)
        code, calls, out, err = self.run_writer('--until', 'derive-contrast')
        self.assertEqual((code, calls, err), (0, list(chain.STEPS[:5]), ''))
        self.assertIn(self.printed, out)
        self.assert_preserved(before)

    def test_failed_derive_child_exit_is_returned_before_the_writer(self):
        before = self.write_inputs(None)
        code, calls, _, err = self.run_writer('--write-contrast', child_code=23)
        self.assertEqual((code, calls), (23, list(chain.STEPS[:5])))
        self.assertIn('step derive-contrast failed with exit 23', err)
        self.assert_preserved(before)

    def test_matching_values_preserve_noncanonical_formatting(self):
        canonical = self.write_inputs(dict(self.base_policy, **self.derived))
        before = json.dumps(json.loads(canonical), separators=(',', ':')).encode()
        self.inputs.write_bytes(before)
        code, calls, _, _ = self.run_writer('--write-contrast')
        self.assertEqual((code, calls), (0, list(chain.STEPS)))
        self.assert_preserved(before)


if __name__ == '__main__':
    unittest.main()
