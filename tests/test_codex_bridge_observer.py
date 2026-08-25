"""Diagnostic lifecycle checks for Claude Code's script bridge."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE = REPO_ROOT / "scripts" / "codex-bridge"


FAKE_CODEX = r'''import json, os, pathlib, sys, time
args = sys.argv[1:]
if os.environ.get("FAKE_ARGS_LOG"):
    pathlib.Path(os.environ["FAKE_ARGS_LOG"]).write_text(json.dumps(args))
session_id = os.environ.get("FAKE_SESSION_ID", "019f0000-0000-7000-8000-000000000123")
print(f"session id: {session_id}", flush=True)
time.sleep(float(os.environ.get("FAKE_DELAY", "0")))
if "-o" in args:
    output = pathlib.Path(args[args.index("-o") + 1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("fake bridge response\n", encoding="utf-8")
raise SystemExit(int(os.environ.get("FAKE_EXIT", "0")))
'''


class _BridgeHarness:
    """Launch machinery shared by the bridge test classes."""

    def launch(
        self,
        tmp_path: Path,
        *bridge_args: str,
        delay: float = 0,
        exit_code: int = 0,
        session_id: str = "019f0000-0000-7000-8000-000000000123",
        service_tier: str | None = None,
        args_log: Path | None = None,
    ) -> tuple[subprocess.Popen[str], Path, Path]:
        fake_codex = tmp_path / "fake_codex.py"
        fake_codex.write_text(FAKE_CODEX, encoding="utf-8")
        observer_dir = tmp_path / "observer"
        bridge_dir = tmp_path / "bridge"
        fake_bin = tmp_path / "fake-codex"
        fake_bin.write_text(
            f"#!{sys.executable}\nexec(open({str(fake_codex)!r}).read())\n",
            encoding="utf-8",
        )
        fake_bin.chmod(0o755)
        environment = {
            **os.environ,
            "CODEX_BIN": str(fake_bin),
            "CODEX_BRIDGE_DIR": str(bridge_dir),
            "CODEX_OBSERVER_DIR": str(observer_dir),
            "FAKE_DELAY": str(delay),
            "FAKE_EXIT": str(exit_code),
            "FAKE_SESSION_ID": session_id,
            # These tests exercise the standalone CLI transport; the desktop
            # app transport is a different launch path with its own helper.
            "CODEX_APP_BRIDGE": "off",
        }
        environment.pop("CODEX_SERVICE_TIER", None)
        if service_tier is not None:
            environment["CODEX_SERVICE_TIER"] = service_tier
        if args_log is not None:
            environment["FAKE_ARGS_LOG"] = str(args_log)
        process = subprocess.Popen(
            [str(BRIDGE), *bridge_args],
            cwd=REPO_ROOT,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(self.stop_process, process)
        return process, observer_dir / "index.jsonl", bridge_dir

    @staticmethod
    def stop_process(process: subprocess.Popen[str]) -> None:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        for stream in (process.stdout, process.stderr):
            if stream is not None and not stream.closed:
                stream.close()

    @staticmethod
    def events(index: Path) -> list[dict]:
        if not index.exists():
            return []
        lines = index.read_text(encoding="utf-8").splitlines()
        events = []
        for position, line in enumerate(lines):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                if position != len(lines) - 1:
                    raise
        return events

    def wait_for_event(self, index: Path, event: str, timeout: float = 5) -> list[dict]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            events = self.events(index)
            if any(item["event"] == event for item in events):
                return events
            time.sleep(0.02)
        self.fail(f"observer did not emit {event}: {self.events(index)}")


class CodexBridgeObserverTests(_BridgeHarness, unittest.TestCase):
    def test_background_run_is_observable_before_bridge_finishes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args_log = Path(tmp) / "args.json"
            process, index, bridge_dir = self.launch(
                Path(tmp),
                "new",
                "background observer proof",
                delay=1.5,
                args_log=args_log,
            )
            events = self.wait_for_event(index, "SESSION_READY")
            self.assertIsNone(process.poll())
            self.assertEqual([item["event"] for item in events], ["RUNNING", "SESSION_READY"])
            running = events[0]
            self.assertEqual(running["transport"], "cli-bridge")
            self.assertEqual(running["caller"], "claude-code")
            self.assertEqual(running["prompt_preview"].strip(), "background observer proof")
            self.assertTrue(running["codex_pid"])
            self.assertEqual(Path(running["status_file"]).read_text().strip(), "RUNNING")

            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertIn("session id:", stdout)
            events = self.wait_for_event(index, "FINISHED")
            self.assertEqual(events[-1]["status"], "OK")
            self.assertEqual(
                [item["event"] for item in events],
                ["RUNNING", "SESSION_READY", "FINISHED"],
            )
            observer_files = list(bridge_dir.glob("*.codex-observer.jsonl"))
            self.assertEqual(len(observer_files), 1)
            local_events = self.events(observer_files[0])
            self.assertEqual(
                [(item["event"], item["status"], item["session_id"]) for item in local_events],
                [(item["event"], item["status"], item["session_id"]) for item in events],
            )
            manifest = json.loads((bridge_dir / "invocation_manifest.jsonl").read_text())
            self.assertEqual(manifest["observer_index"], str(index))
            self.assertEqual(manifest["observer_file"], str(observer_files[0]))
            # 2026-08-08: Codex Fast Mode is the STANDING DEFAULT on the
            # bridge (de759c9, Ed directive); CODEX_SERVICE_TIER=default
            # is the per-call opt-out, covered by its own test below.
            self.assertEqual(manifest["service_tier"], "fast")
            arguments = json.loads(args_log.read_text(encoding="utf-8"))
            tier_index = arguments.index("service_tier=fast")
            self.assertEqual(arguments[tier_index - 1], "-c")

    def test_fast_service_tier_reaches_standalone_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args_log = Path(tmp) / "args.json"
            process, _, _ = self.launch(
                Path(tmp),
                "new",
                "fast service tier proof",
                service_tier="fast",
                args_log=args_log,
            )
            _, stderr = process.communicate(timeout=5)

            self.assertEqual(process.returncode, 0, stderr)
            arguments = json.loads(args_log.read_text(encoding="utf-8"))
            self.assertIn("service_tier=fast", arguments)
            tier_index = arguments.index("service_tier=fast")
            self.assertEqual(arguments[tier_index - 1], "-c")

    def test_invalid_service_tier_fails_closed_before_codex_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args_log = Path(tmp) / "args.json"
            process, _, bridge_dir = self.launch(
                Path(tmp),
                "new",
                "invalid service tier proof",
                service_tier="priority",
                args_log=args_log,
            )
            _, stderr = process.communicate(timeout=5)

            self.assertEqual(process.returncode, 64, stderr)
            self.assertIn(
                "Invalid CODEX_SERVICE_TIER: priority (expected default or fast)",
                stderr,
            )
            self.assertFalse(args_log.exists())
            self.assertFalse((bridge_dir / "invocation_manifest.jsonl").exists())

    def test_failed_codex_run_emits_terminal_failed_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            process, index, _ = self.launch(Path(tmp), "new", "fail", exit_code=7)
            _, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 7, stderr)
            events = self.wait_for_event(index, "FINISHED")
            self.assertEqual(events[-1]["status"], "FAILED rc=7")

    def test_wrapper_termination_closes_running_observer_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            process, index, _ = self.launch(Path(tmp), "new", "interrupt", delay=30)
            self.wait_for_event(index, "RUNNING")
            process.terminate()
            process.wait(timeout=5)
            events = self.wait_for_event(index, "FINISHED")
            self.assertTrue(events[-1]["status"].startswith("FAILED rc="))
            self.assertIn("before normal completion", events[-1]["message"])


class CodexBridgeSandboxEnforcementTests(_BridgeHarness, unittest.TestCase):
    """CODEX-BRIDGE-SANDBOX-01.

    Before this row, `scripts/codex-bridge review` recorded
    `sandbox=read-only` in its observer events while launching
    `codex exec review` with no sandbox flag at all, so the audit trail
    misstated what was actually enforced (live inspection, 2026-08-05).

    The cure is one variable — `observer_sandbox` — that is both the recorded
    value and the launched value. These tests hold that binding from three
    sides: the argv the launch really received, the manifest row that claims
    to describe it, and the script source (no launch site may spell a sandbox
    mode as a literal again).
    """

    SANDBOX_MODES = ("read-only", "workspace-write", "danger-full-access")

    def run_bridge(
        self, tmp: str, *bridge_args: str
    ) -> tuple[list[str], dict, list[dict]]:
        """Run one bridge invocation; return (launched argv, manifest, events)."""
        args_log = Path(tmp) / "args.json"
        process, index, bridge_dir = self.launch(
            Path(tmp), *bridge_args, args_log=args_log
        )
        _, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 0, stderr)
        arguments = json.loads(args_log.read_text(encoding="utf-8"))
        manifest = json.loads(
            (bridge_dir / "invocation_manifest.jsonl").read_text(encoding="utf-8")
        )
        return arguments, manifest, self.events(index)

    def assert_launch_sandbox(self, arguments: list[str], expected: str) -> str:
        """Assert exactly one -s flag, its value, and its position.

        `-s` belongs to `codex exec` itself: `codex exec review` and
        `codex exec resume` reject a `-s` of their own, so the flag must sit
        before the subcommand word.
        """
        flag_positions = [
            position
            for position, argument in enumerate(arguments)
            if argument in ("-s", "--sandbox")
        ]
        self.assertEqual(len(flag_positions), 1, arguments)
        flag_index = flag_positions[0]
        value = arguments[flag_index + 1]
        self.assertEqual(value, expected, arguments)
        for subcommand in ("review", "resume"):
            if subcommand in arguments:
                self.assertLess(flag_index, arguments.index(subcommand), arguments)
        return value

    def test_review_launches_read_only_and_records_what_it_launched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arguments, manifest, events = self.run_bridge(
                tmp, "review", "review sandbox proof"
            )

            self.assertIn("review", arguments)
            launched = self.assert_launch_sandbox(arguments, "read-only")
            self.assertEqual(manifest["mode"], "review")
            self.assertEqual(manifest["sandbox"], "read-only")
            # The defect being cured was precisely a recorded/launched gap.
            self.assertEqual(manifest["sandbox"], launched)
            self.assertTrue(events)
            for event in events:
                self.assertEqual(event["sandbox"], launched)

    def test_new_launches_workspace_write_and_records_what_it_launched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arguments, manifest, events = self.run_bridge(
                tmp, "new", "new sandbox proof"
            )

            launched = self.assert_launch_sandbox(arguments, "workspace-write")
            self.assertEqual(manifest["mode"], "new")
            self.assertEqual(manifest["sandbox"], launched)
            for event in events:
                self.assertEqual(event["sandbox"], launched)

    def test_resume_launches_workspace_write_and_records_what_it_launched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arguments, manifest, events = self.run_bridge(
                tmp, "resume", "--last", "resume sandbox proof"
            )

            self.assertIn("resume", arguments)
            launched = self.assert_launch_sandbox(arguments, "workspace-write")
            self.assertEqual(manifest["mode"], "resume")
            self.assertEqual(manifest["sandbox"], launched)
            for event in events:
                self.assertEqual(event["sandbox"], launched)

    def test_no_launch_site_spells_a_sandbox_mode_literally(self) -> None:
        """Recorded and launched sandbox cannot drift apart again.

        Drift was possible because a launch site named its sandbox mode in
        source while the audit metadata named a different one in a variable.
        Every sandbox flag must therefore take its value from a variable.
        """
        source_lines = [
            line
            for line in BRIDGE.read_text(encoding="utf-8").splitlines()
            if not line.lstrip().startswith("#")
        ]
        source = "\n".join(source_lines)

        literal_flag = re.compile(
            r"(?:-s|--sandbox)[ \t=]+\"?(?:%s)\b" % "|".join(self.SANDBOX_MODES)
        )
        self.assertIsNone(
            literal_flag.search(source),
            "a sandbox flag names a mode literally; use the observer_sandbox "
            "variable so the launched value is the recorded value",
        )
        self.assertIn('sandbox_args=(-s "$observer_sandbox")', source)


if __name__ == "__main__":
    unittest.main()
