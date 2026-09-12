"""Adversarial census checks for GIT-FIXTURE-MAINTENANCE-SWEEP-01."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.test_git_fixture_maintenance import (
    MAINTENANCE_ON_EXCEPTIONS,
    _git_init_violations,
)


class GitFixtureHygieneTests(unittest.TestCase):
    def _scan(self, source: str, relative: str = "support/factory.py"):
        with tempfile.TemporaryDirectory() as temporary:
            tests_root = Path(temporary) / "tests"
            module = tests_root / relative
            module.parent.mkdir(parents=True)
            module.write_text(source, encoding="utf-8")
            return _git_init_violations(tests_root)

    def test_unsafe_command_forms_cannot_bypass_census(self) -> None:
        sources = {
            "argv": "subprocess.run(['git', 'init', '-q'])",
            "assigned_argv": "command = ['git', 'init']\nsubprocess.run(command)",
            "alias": "command = ['git', 'init']\nargs = command\nrun(args)",
            "annotated_argv": "command: list = ['git', 'init']\nrun(command)",
            "shell": "subprocess.run('git -C /tmp/fixture init -q', shell=True)",
            "assigned_shell": "command = 'git init -q'\nos.system(command)",
            "shell_path": "os.system('/usr/bin/git init -q')",
            "shell_fstring": "os.system(f'git -C {repository} init -q')",
            "shell_sequence": "os.system('git init; git status')",
            "wrapper": "execute(repository, 'init', '-q')",
            "wrapper_argv": "execute(repository, ['init', '-q'])",
            "subcommand_alias": "verb = 'init'\nexecute(repository, verb)",
            "conditional": "command = ['git', 'status']\nif unsafe:\n    command = ['git', 'init']\nrun(command)",
        }
        for name, source in sources.items():
            with self.subTest(name=name):
                self.assertIn("support/factory.py", self._scan(source))

    def test_constant_concatenation_cannot_bypass_census(self) -> None:
        sources = {
            "string_in_argv": "cmd = ['git', 'in' + 'it']; subprocess.run(cmd)",
            "shell_string": "cmd = 'git ' + 'in' + 'it'; subprocess.run(cmd, shell=True)",
            "list": "cmd = ['git'] + ['in' + 'it']; subprocess.run(cmd)",
            "tuple": "cmd = ('git',) + ('in' + 'it',); subprocess.run(cmd)",
            "nested_list": "cmd = [] + ['g' + 'it'] + ['i' + ('n' + 'it')]; subprocess.run(cmd)",
            "nested_tuple": "cmd = () + ('g' + 'it',) + ('i' + ('n' + 'it'),); subprocess.run(cmd)",
        }
        for name, source in sources.items():
            with self.subTest(name=name):
                self.assertIn("support/factory.py", self._scan(source))

    def test_shared_helper_routes_are_accepted(self) -> None:
        self.assertEqual(self._scan(
            "from tests.git_fixture import init_git_fixture as initialize\n"
            "def fixture(repository):\n"
            "    initialize(repository, '-q')\n"
        ), {})

    def test_alias_cycles_terminate(self) -> None:
        self.assertEqual(self._scan("a = b\nb = a\nrun(a)\n"), {})

    def test_named_maintenance_exceptions_do_not_exempt_other_tests(self) -> None:
        for qualified in MAINTENANCE_ON_EXCEPTIONS["tests/test_calibration_exits.py"]:
            class_name, method = qualified.split(".")
            source = (
                f"class {class_name}:\n"
                f"    def {method}(self):\n"
                "        execute('init', '-q')\n"
            )
            with self.subTest(method=method):
                self.assertEqual(self._scan(source, "test_calibration_exits.py"), {})
                self.assertIn("test_calibration_exits.py", self._scan(
                    source.replace(method, "test_unrelated_fixture"),
                    "test_calibration_exits.py",
                ))


if __name__ == "__main__":
    unittest.main()
