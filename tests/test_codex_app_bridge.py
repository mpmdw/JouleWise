import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import tempfile
import threading
import time
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "scripts" / "codex-app-bridge.mjs"
THREAD_ID = "019f77a6-3612-7332-9f5e-be9fbde56be5"
TURN_ID = "019f77a9-2827-7de1-accf-ac2eda21927e"


def recv_frame(connection):
    header = connection.recv(4)
    if not header:
        return None
    length = struct.unpack("<I", header)[0]
    chunks = []
    remaining = length
    while remaining:
        chunk = connection.recv(remaining)
        if not chunk:
            raise EOFError("socket closed during frame")
        chunks.append(chunk)
        remaining -= len(chunk)
    return json.loads(b"".join(chunks))


def send_frame(connection, message):
    payload = json.dumps(message).encode()
    connection.sendall(struct.pack("<I", len(payload)) + payload)


class FakeDesktopRouter:
    def __init__(self, socket_path, rollout_path, *, complete=True):
        self.socket_path = socket_path
        self.rollout_path = rollout_path
        self.complete = complete
        self.requests = []
        self.interrupted = threading.Event()
        self.ready = threading.Event()
        self.thread = threading.Thread(target=self._serve, daemon=True)

    def start(self):
        self.thread.start()
        self.assert_ready()

    def assert_ready(self):
        if not self.ready.wait(3):
            raise RuntimeError("fake desktop router did not start")

    def _serve(self):
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(self.socket_path))
        server.listen(1)
        self.ready.set()
        connection, _ = server.accept()
        with connection, server:
            while True:
                request = recv_frame(connection)
                if request is None:
                    return
                self.requests.append(request)
                method = request["method"]
                if method == "initialize":
                    result = {"clientId": "fake-bridge-client"}
                elif method == "thread-follower-start-turn":
                    result = {"method": method, "result": {"result": {"turn": {"id": TURN_ID}}}}
                    if self.complete:
                        threading.Thread(target=self._complete, daemon=True).start()
                elif method == "thread-follower-interrupt-turn":
                    self.interrupted.set()
                    result = {"method": method, "result": {"ok": True}}
                else:
                    send_frame(
                        connection,
                        {
                            "type": "response",
                            "requestId": request["requestId"],
                            "resultType": "error",
                            "error": "unexpected-method",
                        },
                    )
                    continue
                send_frame(
                    connection,
                    {
                        "type": "response",
                        "requestId": request["requestId"],
                        "resultType": "success",
                        "result": result,
                    },
                )

    def _complete(self):
        time.sleep(0.2)
        record = {
            "type": "event_msg",
            "payload": {
                "type": "task_complete",
                "turn_id": TURN_ID,
                "last_agent_message": "FAKE_APP_BRIDGE_OK",
            },
        }
        with self.rollout_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")


class CodexAppBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp")
        self.root = Path(self.temp.name)
        self.codex_home = self.root / ".codex"
        (self.codex_home / "ipc").mkdir(parents=True)
        session_dir = self.codex_home / "sessions" / "2026" / "07" / "18"
        session_dir.mkdir(parents=True)
        self.rollout = session_dir / f"rollout-test-{THREAD_ID}.jsonl"
        self.rollout.write_text('{"type":"session_meta"}\n', encoding="utf-8")
        self.prompt = self.root / "prompt.txt"
        self.prompt.write_text("BRIDGE_ORIGIN: claude\nWRITE_SCOPE: []\n", encoding="utf-8")
        self.output = self.root / "response.md"
        self.lock = self.root / "bridge.lock"
        self.socket_path = self.codex_home / "ipc" / "ipc.sock"
        probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            probe.bind(str(self.socket_path))
        except PermissionError as error:
            self.skipTest(f"sandbox does not permit Unix socket fixtures: {error}")
        finally:
            probe.close()
        self.socket_path.unlink(missing_ok=True)

    def tearDown(self):
        self.temp.cleanup()

    def command(self, sandbox="read-only", service_tier=None):
        command = [
            "node",
            str(HELPER),
            "--thread-id",
            THREAD_ID,
            "--prompt-file",
            str(self.prompt),
            "--output-file",
            str(self.output),
            "--cwd",
            str(REPO_ROOT),
            "--model",
            "gpt-5.6-sol",
            "--effort",
            "high",
            "--sandbox",
            sandbox,
            "--lock-file",
            str(self.lock),
            "--timeout-ms",
            "5000",
        ]
        if service_tier is not None:
            command.extend(("--service-tier", service_tier))
        return command

    def environment(self):
        return {**os.environ, "CODEX_HOME": str(self.codex_home)}

    def test_runs_turn_through_desktop_owner_and_captures_answer(self):
        router = FakeDesktopRouter(self.socket_path, self.rollout)
        router.start()
        result = subprocess.run(
            self.command(),
            cwd=REPO_ROOT,
            env=self.environment(),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"session id: {THREAD_ID}", result.stdout)
        self.assertIn(f"turn id: {TURN_ID}", result.stdout)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "FAKE_APP_BRIDGE_OK\n")
        self.assertFalse(self.lock.exists())
        start = next(item for item in router.requests if item["method"] == "thread-follower-start-turn")
        params = start["params"]["turnStartParams"]
        self.assertEqual(params["model"], "gpt-5.6-sol")
        self.assertEqual(params["effort"], "high")
        self.assertEqual(params["serviceTier"], "default")
        self.assertEqual(params["sandboxPolicy"]["type"], "readOnly")
        self.assertEqual(start["version"], 1)

    def test_fast_service_tier_reaches_turn_start_params(self):
        router = FakeDesktopRouter(self.socket_path, self.rollout)
        router.start()
        result = subprocess.run(
            self.command(service_tier="fast"),
            cwd=REPO_ROOT,
            env=self.environment(),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        start = next(
            item
            for item in router.requests
            if item["method"] == "thread-follower-start-turn"
        )
        self.assertEqual(start["params"]["turnStartParams"]["serviceTier"], "fast")

    def test_termination_interrupts_app_owned_turn_and_removes_lock(self):
        router = FakeDesktopRouter(self.socket_path, self.rollout, complete=False)
        router.start()
        process = subprocess.Popen(
            self.command(),
            cwd=REPO_ROOT,
            env=self.environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 5
        while time.time() < deadline and not any(
            request["method"] == "thread-follower-start-turn" for request in router.requests
        ):
            time.sleep(0.05)
        process.terminate()
        process.communicate(timeout=10)

        self.assertEqual(process.returncode, 143)
        self.assertTrue(router.interrupted.wait(2))
        interrupt = next(item for item in router.requests if item["method"] == "thread-follower-interrupt-turn")
        self.assertEqual(interrupt["version"], 2)
        self.assertFalse(self.lock.exists())


if __name__ == "__main__":
    unittest.main()
