"""Smoke G2: the R1 -> W1 chain doc is a tested script; the kit is regenerated before --check."""
import contextlib
import io
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import unittest

from scripts import align_r1_to_w1_chain as chain

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


if __name__ == '__main__':
    unittest.main()
