"""The shared agent-census matcher (joulewise/agent_identity.py; Opus triple audit F3).

The census probe ``pgrep -a -lf '[c]odex|[c]laude'`` lists every process
whose command line contains one of the substrings.  A window whose custody
root contained one of them (before the T3 prune of 2026-10-07 also ``t3``, as
in an ``attempt3`` id) listed its own processes, and the census stopped the
window for a string.  These tests start real processes and
build the census line exactly as pgrep prints it (pid, a space, the argv joined
by spaces) from the kernel's argv, so they hold on Darwin and Linux alike.
"""

from __future__ import annotations

import json
import os
import shutil
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

    def test_a_listed_window_process_is_not_an_agent(self):
        process = self.window_process()
        stdout = _line(process)
        observed, refusal = night_gate.agent_census(_census_probes(stdout))
        self.assertIsNone(refusal, observed)
        self.assertEqual((1, ""), (observed.exit_code, observed.stdout))
        self.assertIn(f"pid {process.pid} not_agent_executable", observed.stderr)
        self.assertIn("pgrep exit 0", observed.stderr)

    def test_an_agent_named_process_is_still_an_agent(self):
        window = self.window_process()
        for name in ("claude", "codex"):
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
            ("/opt/homebrew/bin/node", ("node", "/opt/homebrew/bin/codex", "exec")): True,
            ("/opt/homebrew/bin/node", ("node", "scripts/claude-bridge-mcp.mjs")): True,
            # A runtime naming an agent anywhere in its arguments (orchestrator ruling, 2026-10-07).
            ("/opt/homebrew/bin/node", ("node", "scripts/run.mjs", "codex")): True,
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
            # The package path as an argument of another script is still an agent: anywhere counts.
            ("/opt/homebrew/bin/node", ("node", "scripts/run.mjs", f"{modules}/@anthropic-ai/claude-code/cli.js")):
                True,
        }
        for (executable, argv), expected in cases.items():
            with self.subTest(argv=argv):
                self.assertIs(expected, agent_identity.is_agent(executable, argv))

    def test_a_runtime_naming_an_agent_anywhere_is_an_agent(self):
        """Orchestrator ruling (2026-10-07): runtime options are never parsed.

        Parsing failed twice: Sol delta audit A4 (``--require <preload>`` read as
        the script) and delta audit 2 R1 (``--trace-require-module all``: ``all``
        read as the script, so real Codex read as no agent and the census clean).
        """
        modules = "/opt/homebrew/lib/node_modules"
        cli = f"{modules}/@anthropic-ai/claude-code/cli.js"
        codex_cli = f"{modules}/@openai/codex/cli.js"
        agents = [
            ("node", "--trace-require-module", "all", codex_cli),  # R1's exact trigger
            ("node", "--trace-require-module", "all", cli, "-p", "x"),
            ("node", "--require", "/tmp/preload.cjs", cli),  # A4's exact trigger
            ("node", "-r", "/tmp/preload.cjs", cli, "-p", "x"),
            ("node", "--import", "/tmp/loader.mjs", cli),
            ("node", "--loader", "/tmp/loader.mjs", "--no-warnings", cli),
            ("node", "--inspect-port", "9229", cli),
            ("node", "-C", "development", cli),
            ("node", "--require", "/tmp/preload.cjs", "/opt/homebrew/bin/codex", "exec"),
            ("node", "--import=/tmp/loader.mjs", cli),
            ("node", "--", cli),
            ("node", "--some-future-option", "/tmp/value", cli),  # an option no table knows
            ("node", "--require", f"{modules}/@anthropic-ai/claude-code/preload.js", "/tmp/app.js"),
            # Inline code that names the package.
            ("node", "-e", f"require('{cli}')"),
            ("node", "--eval", "import('@openai/codex').then(m => m.run())"),
            ("node", "-pe", "require.resolve(\"@anthropic-ai/claude-code\")"),
            ("deno", "eval", "await import('npm:@openai/codex')"),
            # Launchers and install directories seen live on this machine (2026-10-07).
            # The desk dry arm's hit (pid 81281): a Codex seat run by its installed launcher.
            ("node", "/opt/homebrew/bin/codex", "exec", "-m", "gpt-6.1-sol", "-c", "model_reasoning_effort=xhigh",
             "-C", "/Users/edr/code/JouleWise-wt-int5", "-s", "workspace-write", "-o", "/tmp/REPORT.md", "prompt"),
            ("node", "/usr/local/bin/claude", "-p", "x"),
            ("node", "/usr/local/lib/node_modules/claude-code/cli.js"),
            ("node", "/Users/edr/.npm/_npx/d3e0db43a6e4314a/node_modules/.bin/codex", "mcp-server"),
            ("node", "/Users/edr/.local/share/claude/versions/2.1.289/cli.js"),
            ("bun", "--preload", "/tmp/p.ts", "run", f"{modules}/@openai/codex/dist/main.js"),
            ("bun", "x", "@anthropic-ai/claude-code"),
            ("deno", "run", "-A", "npm:@anthropic-ai/claude-code"),
            ("node22", "--trace-require-module", "all", codex_cli),  # a versioned runtime name
        ]
        for argv in agents:
            with self.subTest(argv=argv):
                executable = f"/opt/homebrew/bin/{argv[0]}"
                self.assertEqual("agent", agent_identity.identify(executable, argv))
                self.assertIs(True, agent_identity.is_agent(executable, argv))
        # ``npm exec`` retitles its node process: argv[0] carries the package, the rest is empty.
        npm_exec = ('npm exec @openai/codex@0.153.3 mcp-server -c model="gpt-5.6-sol"', "", "")
        self.assertEqual("agent", agent_identity.identify("/opt/homebrew/Cellar/node/23.7.0/bin/node", npm_exec))
        # A runtime that names no agent but runs code no argument names stays a hit.
        undecided = [
            ("node", "-"),
            ("node", "-e", "process.exit(0)"),
            ("node", "-pe", "1"),
            ("node", "--eval=1"),
            ("bun", "-e", "1"),
            ("deno", "eval", "1"),
        ]
        node = "/opt/homebrew/bin/node"
        for argv in undecided:
            with self.subTest(argv=argv):
                self.assertEqual("undecided", agent_identity.identify(node, argv))
                self.assertIs(True, agent_identity.is_agent(node, argv))
        # Runtime controls: no argument names an agent, so not an agent.
        window = [
            ("node", "somescript.js", "--path", f"{ATTEMPT3_ROOT}/members/m01"),
            ("node", "--trace-require-module", "all", "/tmp/app/cli.js"),
            ("node", "/Users/edr/.claude/hooks/notify.js"),
            ("node", f"{modules}/@anthropic-ai/sdk/dist/index.js"),
            ("node", "--version"),
        ]
        for argv in window:
            with self.subTest(argv=argv):
                self.assertEqual("not_agent", agent_identity.identify(node, argv))
        # Not a runtime: arguments are never read, whatever they name.  These are
        # the window's own shapes (the rendered chain runs /bin/zsh -f and python).
        snapshot = "/Users/edr/.claude/shell-snapshots/snapshot-zsh-1791188896438-of8k3h.sh"
        for executable, argv in (
                ("/usr/bin/python3", ("python3", "-m", "scripts.run_campaign", ATTEMPT3_ROOT)),
                ("/bin/zsh", ("/bin/zsh", "-f", f"{ATTEMPT3_ROOT}/chain.zsh")),
                ("/bin/zsh", ("/bin/zsh", "-c", f"source {snapshot} 2>/dev/null || true && eval 'claude -p x'")),
                ("/opt/homebrew/bin/python3.13", ("python3.13", "-B", "-c", "import x  # codex", "-e",
                                                  f"/Users/edr/.claude/{cli}")),
                ("/private/tmp/b5/measurement/.venv/bin/python", ("python", "-B", "-c", "pass", "--",
                                                                  "/Users/edr/.claude/custody/codex-run"))):
            with self.subTest(argv=argv):
                self.assertEqual("not_agent", agent_identity.identify(executable, argv))

    def test_sol_r1_live_node_launch_is_a_census_hit(self):
        """Delta audit 2 R1, live: a real node process with ``--trace-require-module all``."""
        node = shutil.which("node") or "/opt/homebrew/bin/node"
        if not os.access(node, os.X_OK):
            self.skipTest("no node runtime on this machine")
        package = Path(self.tmp.name) / "node_modules" / "@openai" / "codex"
        package.mkdir(parents=True)
        cli = package / "cli.js"
        cli.write_text("setInterval(() => {}, 1000);\n", encoding="utf-8")
        process = self.spawn([node, "--trace-require-module", "all", str(cli)])
        info = agent_identity.inspect(process.pid)
        self.assertEqual("agent", agent_identity.identify(info.executable, info.argv))
        decided = agent_identity.filter_census(_line(process))
        self.assertEqual([(process.pid, "agent_executable")], [(item["pid"], item["reason"]) for item in decided.kept])
        result, refusal = night_gate.agent_census(_census_probes(_line(process)))
        self.assertEqual(0, result.exit_code)
        self.assertIsNotNone(refusal)
        self.assertIn(str(process.pid), result.stdout)

    def test_an_undecided_interpreter_launch_is_kept_with_its_reason(self):
        # A stand-in kernel view: the census line is decided against it as against a live pid.
        rows = {
            4101: ("/opt/homebrew/bin/node", ("node", "-", "b5-gamma-attempt3")),
            4102: ("/opt/homebrew/bin/node", ("node", "--require", "/tmp/preload.cjs",
                                              "/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/cli.js")),
            4103: ("/opt/homebrew/bin/node", ("node", "scripts/run.mjs", ATTEMPT3_ROOT)),
        }

        def inspector(pid):
            executable, argv = rows[pid]
            return agent_identity.ProcessInfo(pid, 1, pid, executable, argv)

        stdout = "".join(f"{pid} {' '.join(argv)}\n" for pid, (_, argv) in rows.items())
        decided = agent_identity.filter_census(stdout, inspector=inspector)
        self.assertEqual([(4101, "undecided_launch"), (4102, "agent_executable")],
                         [(item["pid"], item["reason"]) for item in decided.kept])
        self.assertEqual([(4103, "not_agent_executable")],
                         [(item["pid"], item["reason"]) for item in decided.ignored])
        self.assertNotIn("4103 ", decided.kept_text)

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


# The census as the driver and the hazard arm run it, from inside a process
# tree the test builds (see AncestorCensusLiveTests).  It prints one JSON line.
_ANCESTOR_CENSUS_CHILD = r"""
import json, os, subprocess, sys, time
from types import SimpleNamespace
from joulewise import agent_identity, night_gate
from joulewise.hazards import arm, base

own_marker = sys.argv[1]
own = subprocess.Popen([own_marker, "60"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        info = agent_identity.inspect(own.pid)
        if info is not None and info.argv and info.argv[0] == own_marker:
            break
        time.sleep(0.02)

    def run(argv):
        done = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        return night_gate.ProbeResult(tuple(argv), done.returncode, done.stdout, done.stderr,
                                      time.monotonic_ns())

    probes = SimpleNamespace(run=run, monotonic_ns=time.monotonic_ns)
    gate, refusal = night_gate.agent_census(probes, own_tree_root=os.getpid())

    def ctx_run(argv, timeout):
        done = subprocess.run(argv, capture_output=True, timeout=timeout)
        return base.Completed(tuple(argv), done.returncode, done.stdout, done.stderr)

    stamp = SimpleNamespace(to_json=lambda: {})
    hazard = arm.agent_census(SimpleNamespace(run=ctx_run, stamp=lambda: stamp))
finally:
    own.kill()
    own.wait()
print(json.dumps({"census_pid": os.getpid(), "chain_pid": os.getppid(), "own_pid": own.pid,
                  "gate": {"argv": list(gate.argv), "exit_code": gate.exit_code, "stdout": gate.stdout,
                           "stderr": gate.stderr, "refusal": refusal.reason if refusal else None},
                  "hazard": {"argv": hazard["argv"], "stdout": hazard["stdout"], "clean": hazard["clean"],
                             "ignored": hazard.get("ignored", [])}}))
"""


def _listed_pids(stdout: str) -> set[int]:
    return {int(line.split(" ", 1)[0]) for line in stdout.splitlines() if line.split(" ", 1)[0].isdecimal()}


class AncestorCensusLiveTests(unittest.TestCase):
    """Dry-records F1 (2026-10-07): the census must see an agent that is its ancestor.

    Darwin pgrep leaves the caller and all of its ancestors out of its list
    unless given ``-a``.  The tree built here is the desk dry arm's shape:

        test -> "claude" (a zsh named claude: the agent session)
             -> zsh running .../b5-gamma-attempt3/chain.zsh (argv-substring only)
             -> python running the census (the driver: own_tree_root)
             -> "codex" (a sleep named codex: the window's own descendant)

    plus a foreign ``run_campaign`` under an ``attempt3`` path.  Only owned pids
    are asserted: this test may run inside a real agent session, whose own
    processes the census also (correctly) lists.
    """

    def setUp(self) -> None:
        if sys.platform != "darwin":
            self.skipTest("Darwin pgrep ancestor exclusion; Linux pgrep has no such rule")
        probe = subprocess.run(night_gate.AGENT_CENSUS_ARGV, capture_output=True, text=True, timeout=30)
        if probe.returncode == 3 and "Cannot get process list" in probe.stderr:
            self.skipTest("/usr/bin/pgrep unavailable in sandbox: exit 3, Cannot get process list")
        self.tmp = tempfile.TemporaryDirectory(prefix="census-ancestor-")
        self.addCleanup(self.tmp.cleanup)
        self.processes: list[subprocess.Popen] = []
        self.addCleanup(self._reap)

    def _reap(self) -> None:
        for process in self.processes:
            if process.poll() is None:
                process.kill()
            process.wait()

    def test_an_agent_ancestor_is_a_hit_and_the_window_is_not(self):
        root = Path(self.tmp.name)
        agent = root / "claude"
        agent.symlink_to("/bin/zsh")
        own_marker = root / "codex"
        own_marker.symlink_to("/bin/sleep")
        # Under a .claude directory, so pgrep lists the foreign run_campaign by
        # argv substring alone (before the T3 prune the attempt3 id did).
        custody = root / ".claude" / "night-custody" / "b5-gamma-attempt3" / "custody"
        custody.mkdir(parents=True)
        chain = custody / "chain.zsh"
        chain.write_text('#!/bin/zsh -f\n"$1" "$2" "$3"\n:\n', encoding="utf-8")
        chain.chmod(0o755)
        child = root / "census_child.py"
        child.write_text(_ANCESTOR_CENSUS_CHILD, encoding="utf-8")
        runner = custody / "run_campaign"
        runner.symlink_to("/bin/sleep")
        foreign = _live([str(runner), "60"])
        self.processes.append(foreign)

        env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
        command = f"'{chain}' '{sys.executable}' '{child}' '{own_marker}'; :"
        session = subprocess.Popen([str(agent), "-f", "-c", command], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, env=env)
        self.processes.append(session)
        stdout, stderr = session.communicate(timeout=120)
        self.assertEqual(0, session.returncode, stderr)
        result = json.loads(stdout.strip().splitlines()[-1])

        for name in ("gate", "hazard"):
            with self.subTest(census=name):
                observed = result[name]
                self.assertEqual(list(night_gate.AGENT_CENSUS_ARGV), observed["argv"])
                kept = _listed_pids(observed["stdout"])
                # (1) the agent that launched the census is a hit.
                self.assertIn(session.pid, kept, f"argv={observed['argv']} kept={sorted(kept)}")
                # (2) the window's own descendant, though agent-named, is ignored as own tree.
                self.assertNotIn(result["own_pid"], kept)
                # (3) argv-substring-only processes are ignored by executable identity:
                # the ancestor shell running .../attempt3/chain.zsh and a foreign run_campaign.
                self.assertNotIn(result["chain_pid"], kept)
                self.assertNotIn(foreign.pid, kept)
                self.assertNotIn(result["census_pid"], kept)
        gate = result["gate"]
        self.assertEqual("night_refused_agent_present", gate["refusal"])
        self.assertIn(f"pid {result['own_pid']} own_tree", gate["stderr"])
        self.assertIn(f"pid {result['chain_pid']} not_agent_executable", gate["stderr"])
        self.assertIn(f"pid {foreign.pid} not_agent_executable", gate["stderr"])
        hazard = result["hazard"]
        self.assertFalse(hazard["clean"])
        reasons = {item["pid"]: item["reason"] for item in hazard["ignored"]}
        self.assertEqual("own_tree", reasons.get(result["own_pid"]))
        self.assertEqual("not_agent_executable", reasons.get(result["chain_pid"]))
        self.assertEqual("not_agent_executable", reasons.get(foreign.pid))


if __name__ == "__main__":
    unittest.main()
