"""The shared agent-census matcher (joulewise/agent_identity.py; Opus triple audit F3).

The census probe ``pgrep -lf '[c]odex|[c]laude|[t]3'`` lists every process
whose command line contains one of the substrings.  A window whose custody
root or attempt id contains ``attempt3`` listed its own processes, and the
census stopped the window for a string.  These tests start real processes and
build the census line exactly as pgrep prints it (pid, a space, the argv joined
by spaces) from the kernel's argv, so they hold on Darwin and Linux alike.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from joulewise import agent_identity, night_gate
from joulewise.hazards import arm, base

ATTEMPT3_ROOT = "/Users/edr/night-custody/b5-gamma-attempt3/custody"


def _live(argv: list[str]) -> subprocess.Popen:
    process = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:  # wait for the exec to land in the kernel's argv
        info = agent_identity.inspect(process.pid)
        if info is not None and info.argv and tuple(info.argv) == tuple(argv):
            return process
        time.sleep(0.02)
    process.kill()
    process.wait()
    raise unittest.SkipTest("the kernel did not report the child's argv")


def _line(process: subprocess.Popen) -> str:
    return f"{process.pid} {' '.join(process.args)}\n"


def _census_probes(stdout: str, exit_code: int = 0):
    def run(argv):
        return night_gate.ProbeResult(tuple(argv), exit_code, stdout, "", 10)
    return SimpleNamespace(run=run, monotonic_ns=lambda: 10)


class AgentIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        if agent_identity.inspect(os.getpid()) is None:
            self.skipTest("no kernel process reader on this platform")
        self.processes: list[subprocess.Popen] = []
        self.tmp = tempfile.TemporaryDirectory(prefix="agent-identity-")
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self._reap)

    def _reap(self) -> None:
        for process in self.processes:
            process.kill()
            process.wait()

    def spawn(self, argv: list[str]) -> subprocess.Popen:
        process = _live(argv)
        self.processes.append(process)
        return process

    def marker(self, name: str) -> str:
        # A symlink to sleep: the kernel executable is sleep, the process name
        # (argv[0]) is the agent's name.
        path = Path(self.tmp.name) / name
        path.symlink_to("/bin/sleep")
        return str(path)

    def window_process(self) -> subprocess.Popen:
        """A window process: sleep started from an attempt3 custody path as ``run_campaign``."""

        root = Path(self.tmp.name) / "night-custody" / "b5-gamma-attempt3" / "custody"
        root.mkdir(parents=True, exist_ok=True)
        runner = root / "run_campaign"
        if not runner.exists():
            runner.symlink_to("/bin/sleep")
        return self.spawn([str(runner), "60"])

    def test_a_window_process_whose_argv_contains_t3_is_not_an_agent(self):
        process = self.window_process()
        stdout = _line(process)
        self.assertRegex(stdout, "[c]odex|[c]laude|[t]3")  # pgrep's own pattern lists it
        observed, refusal = night_gate.agent_census(_census_probes(stdout))
        self.assertIsNone(refusal, observed)
        self.assertEqual((1, ""), (observed.exit_code, observed.stdout))
        self.assertIn(f"pid {process.pid} not_agent_executable", observed.stderr)
        self.assertIn("pgrep exit 0", observed.stderr)

    def test_an_agent_named_process_is_still_an_agent(self):
        window = self.window_process()
        for name in ("claude", "codex", "T3 Code (Alpha)"):
            with self.subTest(name=name):
                agent = self.spawn([self.marker(name), "60"])
                stdout = _line(window) + _line(agent)
                observed, refusal = night_gate.agent_census(_census_probes(stdout))
                self.assertEqual("night_refused_agent_present", refusal.reason)
                self.assertEqual(_line(agent), observed.stdout)
                self.assertIn(str(agent.pid), refusal.detail)
                self.assertNotIn(str(window.pid), observed.stdout)

    def test_the_callers_own_tree_is_ignored_even_when_agent_named(self):
        agent = self.spawn([self.marker("codex"), "60"])
        stdout = _line(agent)
        _, refusal = night_gate.agent_census(_census_probes(stdout))
        self.assertEqual("night_refused_agent_present", refusal.reason)
        observed, refusal = night_gate.agent_census(_census_probes(stdout), own_tree_root=os.getpid())
        self.assertIsNone(refusal)
        self.assertIn(f"pid {agent.pid} own_tree", observed.stderr)

    def test_an_undecidable_line_stays_a_hit(self):
        # A pid that is not running, a pid whose argv differs from the line, and
        # a continuation line: none can be decided, so all stay hits.
        stdout = f"99999999 claude\n{os.getpid()} codex --not-my-argv\nsecond line of an argv\n"
        decided = agent_identity.filter_census(stdout)
        self.assertEqual(stdout, decided.kept_text)
        self.assertEqual([], decided.ignored)

    def test_a_multiline_argv_record_is_decided_as_one_record(self):
        process = self.window_process()
        process_line = _line(process)
        decided = agent_identity.filter_census(process_line.replace(" 60\n", "\n60\n"))
        self.assertEqual(process_line.replace(" 60\n", "\n60\n"), decided.kept_text)  # argv differs: kept
        process = self.spawn([self.marker("worker\nb5-gamma-attempt3"), "60"])
        decided = agent_identity.filter_census(_line(process))
        self.assertEqual("", decided.kept_text)
        self.assertEqual([process.pid], [item["pid"] for item in decided.ignored])

    def test_executable_identity_rules(self):
        cases = {
            ("/Users/edr/.local/share/claude/versions/2.1.289", ("claude",)): True,
            ("/opt/homebrew/lib/node_modules/@openai/codex/vendor/bin/codex-code-mode-host", None): True,
            ("/Applications/ChatGPT.app/Contents/Resources/codex", None): True,
            ("/Applications/T3 Code (Alpha).app/Contents/MacOS/T3 Code (Alpha)", None): True,
            ("/opt/homebrew/bin/node", ("node", "/opt/homebrew/bin/codex", "exec")): True,
            ("/opt/homebrew/bin/node", ("node", "scripts/claude-bridge-mcp.mjs")): True,
            ("/opt/homebrew/bin/node", ("node", "scripts/run.mjs", "codex")): False,
            ("/bin/zsh", ("/bin/zsh", "-c", "source /Users/edr/.claude/shell-snapshots/x.sh")): False,
            ("/usr/bin/python3", ("python3", "-m", "scripts.run_campaign", ATTEMPT3_ROOT)): False,
        }
        for (executable, argv), expected in cases.items():
            with self.subTest(executable=executable, argv=argv):
                self.assertIs(expected, agent_identity.is_agent(executable, argv))

    def test_an_agent_package_script_run_by_its_real_path_is_an_agent(self):
        """Cold pass 2 N5: ``node .../@anthropic-ai/claude-code/cli.js`` (basename ``cli.js``) was missed."""
        modules = "/opt/homebrew/lib/node_modules"
        cases = {
            ("/opt/homebrew/bin/node", ("node", f"{modules}/@anthropic-ai/claude-code/cli.js", "-p", "x")): True,
            ("/opt/homebrew/bin/node", ("node", "--no-warnings", f"{modules}/@anthropic-ai/claude-code/cli.js")):
                True,
            ("/opt/homebrew/bin/bun", ("bun", "/Users/edr/.bun/install/global/node_modules/@anthropic-ai/"
                                              "claude-agent-sdk/cli.js")): True,
            ("/opt/homebrew/bin/node", ("node", f"{modules}/@openai/codex/dist/main.js", "exec")): True,
            ("/usr/local/bin/node", ("node", "/usr/local/lib/node_modules/claude-code/cli.js")): True,
            # Not agent packages: other scopes, a path that merely mentions an agent, a .claude directory.
            ("/opt/homebrew/bin/node", ("node", f"{modules}/@anthropic-ai/sdk/dist/index.js")): False,
            ("/opt/homebrew/bin/node", ("node", f"{modules}/@openai/agents/cli.js")): False,
            ("/opt/homebrew/bin/node", ("node", "/Users/edr/.claude/hooks/notify.js")): False,
            ("/opt/homebrew/bin/node", ("node", "scripts/run.mjs", f"{modules}/@anthropic-ai/claude-code/cli.js")):
                False,
        }
        for (executable, argv), expected in cases.items():
            with self.subTest(argv=argv):
                self.assertIs(expected, agent_identity.is_agent(executable, argv))

    def test_the_hazard_arm_census_uses_the_same_matcher(self):
        window = self.window_process()

        def ctx_for(stdout: bytes):
            def run(argv, timeout):
                return base.Completed(tuple(argv), 0, stdout, b"")
            stamp = SimpleNamespace(to_json=lambda: {})
            return SimpleNamespace(run=run, stamp=lambda: stamp)

        census = arm.agent_census(ctx_for(_line(window).encode()))
        self.assertTrue(census["clean"], census)
        self.assertEqual((1, 0), (census["returncode"], census["raw_returncode"]))
        self.assertEqual([window.pid], [item["pid"] for item in census["ignored"]])
        # The arm ignores its own tree, so the agent must be someone else's:
        # a detached grandchild whose parent shell has exited.
        marker = self.marker("claude")
        shell = subprocess.run(["/bin/sh", "-c", f"'{marker}' 60 "
                                "</dev/null >/dev/null 2>&1 & echo $!"],
                               capture_output=True, text=True, start_new_session=True, check=True)
        pid = int(shell.stdout.strip())
        self.addCleanup(os.kill, pid, 9)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            info = agent_identity.inspect(pid)
            if info is not None and info.argv and info.argv[0] == marker:
                break
            time.sleep(0.02)
        line = f"{pid} {' '.join(agent_identity.inspect(pid).argv)}\n"
        census = arm.agent_census(ctx_for((_line(window) + line).encode()))
        self.assertFalse(census["clean"])
        self.assertIn(str(pid), census["detail"])
        self.assertEqual(line, census["stdout"])


if __name__ == "__main__":
    unittest.main()
