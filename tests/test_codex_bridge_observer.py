"""Diagnostic lifecycle checks for Claude Code's script bridge."""

from __future__ import annotations

import json
import os
from pathlib import Path
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


class CodexBridgeObserverTests(unittest.TestCase):
    def launch(
        self,
        tmp_path: Path,
        *bridge_args: str,
        delay: float = 0,
        exit_code: int = 0,
        session_id: str = "019f0000-0000-7000-8000-000000000123",
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
        process = subprocess.Popen(
            [str(BRIDGE), *bridge_args],
            cwd=REPO_ROOT,
            env={
                **os.environ,
                "CODEX_BIN": str(fake_bin),
                "CODEX_BRIDGE_DIR": str(bridge_dir),
                "CODEX_OBSERVER_DIR": str(observer_dir),
                "FAKE_DELAY": str(delay),
                "FAKE_EXIT": str(exit_code),
                "FAKE_SESSION_ID": session_id,
            },
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

    def test_background_run_is_observable_before_bridge_finishes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            process, index, bridge_dir = self.launch(
                Path(tmp), "new", "background observer proof", delay=1.5
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


if __name__ == "__main__":
    unittest.main()
