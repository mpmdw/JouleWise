"""CAP 10 closing step (PR #896): a C1 attempt installs through the real installer.

Audit 10 found two installer refusals of a correct C1 attempt. The lite
adapter hid both because it stubbed the downstream installer:

1. Identity. The installer read ``repo_head`` with git in the directory its
   own module resolves to. For C1 that is the repo export, which has no .git.
2. Publication. C1 prepare published the night plan in S/controls. The
   installer admits only the custody root's night plan.

These tests run the real installer on fresh synthetic attempts:
bytes_h_session.install, then the installer module's own argument parser,
identity check and publication check. The module is loaded from an export
directory with no .git, as in production. Only host steps are mocked.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from joulewise import night_gate
from joulewise.align.apple import v4_registration as closure
from scripts import bytes_h_session as staging
from tests.align.c1_closure_lite import adapter
from tests.align.c1_closure_lite.suite import lite_adapter

HERE = Path(adapter.__file__).parent
ROOT = HERE.parents[2]


def option(argv, flag):
    return argv[argv.index(flag) + 1] if flag in argv else None


def replace_option(argv, flag, value):
    """``argv`` with ``flag`` set to ``value``, or without it when ``value`` is None."""
    out, items = [], iter(argv)
    for item in items:
        if item == flag:
            next(items)
            continue
        out.append(item)
    return out + ([flag, value] if value is not None else [])


class C1InstallerContractTests(unittest.TestCase):
    def attempt(self, make_attempt=adapter.Attempt):
        work = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.enterContext(patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}))
        for name in ('CALIBRATION_LEDGER', 'LEDGER_HEAD_PIN', 'JOULEWISE_C1_INPUTS'):
            os.environ.pop(name, None)
        subprocess.run(['git', 'clone', '-q', '--bare', HERE / 'suite/history.bundle', work / 'history.git'],
                       check=True)
        return make_attempt(work, 'valid_24_closure', 'copy', None)

    def installed(self):
        """A fresh attempt, built, delivered and run through both consumers."""
        attempt = self.attempt()
        code, packet = attempt.build()
        self.assertEqual(code, 0, attempt.build_error)
        attempt.deliver(packet)
        routes = lite_adapter.consumer_decisions(attempt.install, attempt.direct_arm)
        self.assertEqual(dict(cli=0, arm='admit', host_cli=1, host_arm=1), routes, attempt.cli_error)
        return attempt

    def test_cap10_i3_fresh_attempt_end_to_end_through_the_real_installer(self):
        """Build, then the real installer's identity and publication checks, then both host checkpoints."""
        attempt = self.installed()
        (call,) = attempt.installer_calls
        self.assertEqual(0, call['exit'], call['stderr'])
        published = night_gate.night_plan_path(attempt.custody_path())
        # The argv is bytes_h_session.install's own, for this attempt.
        self.assertEqual(str(Path(attempt.state['measurement_root']) / 'scripts/install_night_agent.sh'),
                         call['argv'][0])
        self.assertEqual(str(published), option(call['argv'], '--plan'))
        self.assertEqual(attempt.execution, option(call['argv'], '--execution-commit'))
        # The installer's validation ran to the end and returned the prepared
        # install, so its identity, publication and time admission all passed.
        prepared = call['prepared']
        self.assertEqual(published.resolve(), prepared.plan_path)
        self.assertEqual((attempt.execution, attempt.execution),
                         (prepared.plan.repo_head, prepared.plan.measurement_head))
        # As in production, the module resolves into an export with no .git,
        # and the installer never asks git for its identity.
        self.assertFalse(os.path.lexists(call['module_root'] / '.git'))
        self.assertFalse(call['module_root'].is_relative_to(ROOT))
        self.assertEqual([], call['git'])

    def test_cap10_audit_identity_is_the_pinned_execution_commit(self):
        """Audit 10 HIGH 1: identity comes from the pinned execution commit, never from a .git lookup."""
        attempt = self.installed()
        (call,) = attempt.installer_calls
        argv = call['argv']
        other = attempt.rev()  # the delivery commit, which is not the execution commit
        self.assertNotEqual(other, attempt.execution)
        cases = (
            ('pinned', argv, 0, None),
            ('missing', replace_option(argv, '--execution-commit', None), 3, 'execution_commit_missing'),
            ('malformed', replace_option(argv, '--execution-commit', 'HEAD'), 3, 'execution_commit_missing'),
            ('disagreeing', replace_option(argv, '--execution-commit', other), 3, 'execution_commit_mismatch'),
        )
        for name, variant, code, reason in cases:
            with self.subTest(case=name):
                result = attempt.run_installer(variant)
                self.assertEqual(code, result['exit'], result['stderr'])
                if reason:
                    self.assertIn(reason, result['stderr'])
                self.assertNotIn('unable to read repo_head', result['stderr'])
                self.assertEqual([], result['git'])
        # The one function supplies the commit to the launch view and the installer.
        self.assertEqual(attempt.execution, closure.execution_commit(attempt.handoff))
        for handoff in ({}, {'execution_commit': None}, {'execution_commit': 'HEAD'}):
            with self.subTest(handoff=handoff), self.assertRaisesRegex(ValueError, 'execution_commit_missing'):
                closure.execution_commit(handoff)
        # The C1 install route never calls the installer without the commit.
        calls = []
        with self.assertRaisesRegex(ValueError, 'execution_commit_missing'):
            staging.install(attempt.install_root(), state=dict(attempt.state), now=lambda: adapter.NOW,
                            home=attempt.work / 'fixture-home', run=lambda argv, **_: calls.append(argv))
        self.assertEqual([], calls)

    def test_cap10_audit_installer_admits_the_plan_where_c1_prepare_publishes_it(self):
        """Audit 10 HIGH 2: one plan location. What C1 prepare publishes, the installer admits."""
        attempt = self.installed()
        (call,) = attempt.installer_calls
        published = night_gate.night_plan_path(attempt.custody_path())
        self.assertEqual(str(published), attempt.state['plan_path'])
        self.assertEqual(0, call['exit'], call['stderr'])
        # The same bytes anywhere else still refuse. The first case is where
        # C1 prepare published the plan before CAP 10.
        for outside in (attempt.stage / 'controls' / night_gate.PLAN_BASENAME,
                        attempt.work / 'elsewhere' / night_gate.PLAN_BASENAME):
            with self.subTest(plan=str(outside.relative_to(attempt.work))):
                outside.parent.mkdir(parents=True, exist_ok=True)
                outside.write_bytes(published.read_bytes())
                result = attempt.run_installer(replace_option(call['argv'], '--plan', str(outside)))
                self.assertEqual(2, result['exit'], result['stderr'])
                self.assertIn('plan_outside_custody_root', result['stderr'])
                outside.unlink()

    def test_cap10_one_plan_location_function(self):
        """The producer, the C1 closure and the installer all name the plan through night_plan_path."""
        self.assertEqual(Path('/synthetic/custody/night_plan.json'),
                         night_gate.night_plan_path('/synthetic/custody'))
        for relative in ('scripts/bytes_h_session.py', 'joulewise/night_agent_install.py',
                         'joulewise/align/apple/v4_registration.py', 'joulewise/b5/plan.py'):
            with self.subTest(module=relative):
                text = (ROOT / relative).read_text(encoding='utf-8')
                self.assertIn('night_plan_path(', text)
                self.assertNotIn("'night_plan.json'", text)
                self.assertNotIn('"night_plan.json"', text)
                self.assertNotIn("custody/night_plan.json", text)


if __name__ == '__main__':
    unittest.main()
