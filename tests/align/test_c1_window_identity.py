"""Lead micro-fix J1-J3 (PR #896): one C1 window identity, from materializer to installer.

The narrow check of `e25e5bb71` materialized a fresh synthetic 24-member C1
kit. Its collection plan declared window `C1`, but its plan tree's window
identity (which the reservation's `--window-id` points at) said
`align-v4-c1`. Production then refused at three stages:
- the reservation, with `plan_window_mismatch`;
- the packet builder, exit 2;
- the installer, which did not recognise the night plan as C1 and refused
  its pinned commit with `execution_commit_unexpected`.

The lite adapter hid all three, because it passed a literal `C1`.
"""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import v4_registration as closure
from joulewise.b5 import chain
from scripts import align_v4_kit as w1, align_v4_series as series
from scripts import reserve_calibration_window_bracket as reservation
from tests.align import test_v4_next_arm_packet as fixtures
from tests.align.c1_closure_lite import adapter
from tests.align.c1_closure_lite.suite import lite_adapter

HERE = Path(adapter.__file__).parent
ROOT = HERE.parents[2]
IDENTITY_FLAGS = ('--window-id', '--plan-id', '--plan-sha256', '--evidence-root-id')
# J2: identity literals the adapter must never pass. Each pattern is checked
# against a line the pre-fix adapter contained, so none of them is vacuous.
IDENTITY_LITERALS = {
    'a series window ID': (r"""['"][WCTR][0-9]{1,2}['"]""", "KIT = series.kit_path('C1')"),
    'a pack or plan ID': (r"""['"]align-v4[-a-z0-9]*['"]""", "pack_plan_id='align-v4-c1'"),
    'an invented session, attempt, evidence or plan ID': (
        r"""['"]fixture-(?:session|pre|post|evidence|plan)['"]""", "bracket_session_id='fixture-session',"),
    'an identity field set to a literal': (
        r"""\b['"]?(?:window_id|window|plan_id|pack_id|pack_plan_id|session_id|bracket_session_id|"""
        r"""evidence_root_id|attempt_id|pre_attempt_id|post_attempt_id|attempt|execution_commit|"""
        r"""repo_head|measurement_head)['"]?\s*[:=]\s*(?:['"]|[0-9])""", "'attempt': 1,"),
    'an identity flag paired with a literal value': (
        r"""['"]--(?:window-id|plan-id|plan-sha256|evidence-root-id|session-id|pre-attempt-id|"""
        r"""post-attempt-id)['"]\s*,\s*['"]""", "(('--window-id', 'C1'),"),
    'a hex object ID or digest': (r"""['"](?:[0-9a-f]{40}|[0-9a-f]{64})['"]""",
                                  "'" + '3' * 40 + "'"),
    'a repeated-character digest': (r"""['"][0-9a-fA-F]['"]\s*\*\s*(?:40|64)\b""", "plan_sha256='a' * 64,"),
}


class Synthetic(fixtures.Scenario):
    """The repo's invented series fixtures, with the canonical public generator template."""
    def write(self, path, value):
        if Path(path) == w1.SOURCE_KIT / 'plan_tree.json':
            value = subprocess.check_output(['git', '-C', str(series.ROOT), 'show',
                                             f'{w1.ANCHOR_COMMIT}:{path}'])
        return super().write(path, value)


def materialize(root):
    """A fresh synthetic 24-member C1 kit from the real materializer, with --check."""
    seed = Synthetic(root, 'R1')
    fixtures.seed_materializer(seed)
    seed.write('configs/align/v4/r1_runtime.json', {
        'sensors': {'s_fast': 'T001', 's_slow': 'T002', 'fan_keys': [],
                    'r0_sha256': '1' * 64, 'record_keys': ['T002']},
        'r0_picks': {'s_slow': 'T002'}})
    args = ['materialize', '--root', str(root), '--window-id', closure.C1_WINDOW, '--extra-sentinels', '2']
    with redirect_stdout(io.StringIO()):
        if series.main(args) != 0 or series.main([*args, '--check']) != 0:
            raise AssertionError('the materializer refused its synthetic seed')
    kit = root / series.kit_path(closure.C1_WINDOW)
    return kit, closure.decode((kit / 'plan_tree.json').read_bytes())


def reservation_operands(tree):
    stage = next(row for row in tree['stage_graph'] if row['kind'] == 'bracket_reservation')
    args = adapter.arguments(stage)
    return {flag: args[args.index(adapter.literal(flag)) + 1] for flag in IDENTITY_FLAGS}


class C1WindowIdentityTests(unittest.TestCase):
    def work(self):
        work = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.enterContext(patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}))
        for name in ('CALIBRATION_LEDGER', 'LEDGER_HEAD_PIN', 'JOULEWISE_C1_INPUTS'):
            os.environ.pop(name, None)
        return work

    def test_j3_a_materialized_kit_builds_reserves_and_installs(self):
        """The narrow check's reproduction, as a regression. The fresh kit's identity
        passes the materializer, the reservation, the build and the real installer,
        through both host checkpoints."""
        work = self.work()
        seed = work / 'seed'
        seed.mkdir()
        kit, tree = materialize(seed)
        plan_path = kit / series.C1_PLAN
        plan = closure.decode(plan_path.read_bytes())
        self.assertEqual(24, len(plan['members']))
        operands = reservation_operands(tree)
        stage = next(s for s in chain.stage_plan(tree, c1=True) if s.kind == 'bracket_reservation')
        argv = stage.commands[0].arguments
        resolved = {flag: chain.bind_argument(argv[next(i for i, item in enumerate(argv)
                                                        if item.get('value') == flag) + 1], {}, tree, seed)
                    for flag in IDENTITY_FLAGS}
        # J1: one identity. The materializer writes it in the tree and in the
        # plan; the reservation reads it through its tree pointer.
        self.assertEqual(closure.window_identity(closure.C1_WINDOW, plan['plan_id']), tree['window_identity'])
        self.assertEqual(closure.C1_WINDOW, plan['window_id'])
        self.assertEqual(plan['window_id'], resolved['--window-id'])
        self.assertEqual(tree['window_identity']['evidence_root_id'], resolved['--evidence-root-id'])
        self.assertEqual(plan['plan_id'], resolved['--plan-id'])
        # The production reservation admits the generated plan with what the chain passes it.
        reservation.verify_frozen_plan(plan_path, plan_id=resolved['--plan-id'],
                                       plan_sha256=resolved['--plan-sha256'], window_id=resolved['--window-id'])

        def generated_identity(source):
            # The generated identity and its operands replace the attempt's own.
            source['window_identity'] = tree['window_identity']
            stage = next(row for row in source['stage_graph'] if row['kind'] == 'bracket_reservation')
            args = adapter.arguments(stage)
            for flag, operand in operands.items():
                args[args.index(adapter.literal(flag)) + 1] = operand
            return {}

        attempt_work = work / 'attempt'
        attempt_work.mkdir()
        subprocess.run(['git', 'clone', '-q', '--bare', HERE / 'suite/history.bundle',
                        attempt_work / 'history.git'], check=True)
        attempt = adapter.Attempt(attempt_work, 'valid_24_closure', 'copy', generated_identity)
        code, packet = attempt.build()
        self.assertEqual(0, code, attempt.build_error)
        attempt.deliver(packet)
        routes = lite_adapter.consumer_decisions(attempt.install, attempt.direct_arm)
        self.assertEqual(dict(cli=0, arm='admit', host_cli=1, host_arm=1), routes, attempt.cli_error)
        (call,) = attempt.installer_calls
        self.assertEqual(0, call['exit'], call['stderr'])
        pack = call['prepared'].plan.hazard_window['pack']
        self.assertEqual(tree['window_identity'], {key: pack[key] for key in ('window_id', 'evidence_root_id')})
        self.assertEqual([], call['git'])

    def test_j1_one_window_identity_on_the_c1_route(self):
        """The C1 route names the window only through v4_registration.C1_WINDOW."""
        identity = closure.window_identity(closure.C1_WINDOW, series.pack_id(closure.C1_WINDOW))
        self.assertEqual(closure.C1_WINDOW, identity['window_id'])
        literal = re.compile(r"""['"]C1['"]""")
        for relative in ('joulewise/night_agent_install.py', 'joulewise/align/apple/v4_registration.py',
                         'scripts/bytes_h_session.py', 'scripts/align_v4_session.py',
                         'scripts/align_v4_next_arm_packet.py', 'scripts/align_v4_series.py'):
            with self.subTest(module=relative):
                lines = [line.strip() for line in (ROOT / relative).read_text(encoding='utf-8').splitlines()
                         if literal.search(line)]
                expected = ["C1_WINDOW = 'C1'"] if relative.endswith('v4_registration.py') else []
                self.assertEqual(expected, lines)

    def test_j2_the_adapter_passes_no_identity_literals(self):
        """Every identity a production step compares comes from the previous step's output."""
        text = ADAPTER.read_text(encoding='utf-8')
        for name, (pattern, sample) in IDENTITY_LITERALS.items():
            with self.subTest(literal=name):
                self.assertRegex(sample, pattern)
                hits = [f'{number}: {line.strip()}' for number, line in enumerate(text.splitlines(), 1)
                        if re.search(pattern, line)]
                self.assertEqual([], hits)


ADAPTER = Path(adapter.__file__)


if __name__ == '__main__':
    unittest.main()
