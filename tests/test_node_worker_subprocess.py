"""NV-5 localhost contract coverage for the real node client and worker."""

from __future__ import annotations

import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from joulewise.adapters.node_client import NodeWorkerClient
from joulewise.clock import SystemClock
from joulewise.interfaces import AdapterResult
from joulewise.schemas import FailureReason


def _localhost_socket_probe() -> tuple[bool, str | None]:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        probe.bind(("127.0.0.1", 0))
        probe.listen(1)
    except OSError as exc:
        return False, f"{exc.__class__.__name__}: {exc}"
    finally:
        probe.close()
    return True, None


class LocalSubprocessTransport:
    """Local-filesystem transport that still launches the real worker process."""

    def __init__(self, env: dict[str, str]) -> None:
        self.env = dict(env)
        self.put_destinations: list[str] = []
        self.collect_sources: list[str] = []

    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                env=self.env,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message=f"local subprocess transport failed: {exc}",
            )
        metadata = {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr_tail": completed.stderr[-2000:],
        }
        # A worker task returns nonzero for structured failed/unsupported
        # status. Transport succeeded as long as the process was launched;
        # status.json remains authoritative.
        if "--task" in command or completed.returncode == 0:
            return AdapterResult(ok=True, metadata=metadata)
        return AdapterResult(
            ok=False,
            failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
            message=completed.stderr[-2000:] or "local command failed",
            metadata=metadata,
        )

    def put_file(
        self,
        source: str,
        destination: str,
        *,
        timeout_s: float | None = None,
    ) -> AdapterResult:
        del timeout_s
        try:
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        except OSError as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message=str(exc),
            )
        self.put_destinations.append(destination)
        return AdapterResult(ok=True)

    def collect(
        self,
        source: str,
        destination: str,
        *,
        timeout_s: float | None = None,
    ) -> AdapterResult:
        del timeout_s
        try:
            shutil.copytree(source, destination)
        except OSError as exc:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message=str(exc),
            )
        self.collect_sources.append(source)
        return AdapterResult(ok=True)


class NodeWorkerSubprocessTests(unittest.TestCase):
    def test_real_client_worker_artifact_contract_over_localhost(self) -> None:
        sockets_ok, reason = _localhost_socket_probe()
        if not sockets_ok:
            message = (
                "NV-5 ACCEPTANCE GATE SKIP: localhost sockets unavailable; "
                f"real client-worker subprocess parity was not exercised ({reason})"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            self._write_fake_vllm(bin_dir / "vllm")
            self._write_fake_nvidia_smi(bin_dir / "nvidia-smi")
            env = dict(os.environ)
            env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
            transport = LocalSubprocessTransport(env)
            remote_root = root / "remote"
            client = NodeWorkerClient(
                transport,
                SystemClock(),
                remote_work_root=str(remote_root),
                remote_python=sys.executable,
            )
            run_id = "nv5-localhost-contract"
            server_pid: int | None = None
            try:
                prepare = client.run_task(
                    self._runtime_task(run_id, "prepare", "task-runtime-prepare"),
                    timeout_s=15.0,
                )
                self.assertTrue(prepare.ok, prepare)
                self._assert_artifact_name_parity(prepare)
                pidfile = remote_root / run_id / "state" / "vllm.pid"
                pid_payload = json.loads(pidfile.read_text(encoding="utf-8"))
                server_pid = int(pid_payload["pid"])

                workload = client.run_task(
                    {
                        "task_id": "task-runtime-run-workload",
                        "run_id": run_id,
                        "task_type": "runtime",
                        "operation": "run_workload",
                        "node_role": None,
                        "workload": {
                            "prompt_text": "alpha beta",
                            "output_tokens": 3,
                            "sampling_params": {
                                "max_tokens": 3,
                                "temperature": 0.0,
                                "top_p": 1.0,
                                "seed": 0,
                            },
                        },
                    },
                    timeout_s=15.0,
                )
                self.assertTrue(workload.ok, workload)
                self._assert_artifact_name_parity(workload)
                self.assertEqual(
                    workload.raw_status["artifacts"],
                    {
                        "events_jsonl": "events.jsonl",
                        "response_txt": "response.txt",
                        "status_json": "status.json",
                        "tokens_jsonl": "tokens.jsonl",
                        "worker_log": "worker.log",
                    },
                )
                tokens = [
                    json.loads(line)
                    for line in workload.artifacts["tokens.jsonl"]
                    .decode("utf-8")
                    .splitlines()
                ]
                self.assertEqual([row["text"] for row in tokens], ["AB", "C"])
                self.assertEqual({row["record_unit"] for row in tokens}, {"sse_chunk"})
                self.assertEqual(
                    workload.raw_status["metadata"]["token_count_source"],
                    "server_usage",
                )
                self.assertEqual(workload.raw_status["metadata"]["emitted_tokens"], 3)
                self.assertEqual(workload.raw_status["metadata"]["stream_chunk_count"], 2)

                idle = client.run_task(
                    {
                        "task_id": "task-telemetry-measure-idle",
                        "run_id": run_id,
                        "task_type": "telemetry",
                        "operation": "measure_idle",
                        "node_role": None,
                        "telemetry": {
                            "backend": "nvidia_smi",
                            "interval_ms": 20,
                            "idle_seconds": 0.08,
                            "query_fields": [
                                "timestamp",
                                "power.draw",
                                "temperature.gpu",
                            ],
                            "rail_manifest": ["gpu_board"],
                        },
                    },
                    timeout_s=15.0,
                )
                self.assertTrue(idle.ok, idle)
                self._assert_artifact_name_parity(idle)
                self.assertIn("nvidia_smi_idle_csv", idle.raw_status["artifacts"])
                self.assertIn(b", 12.5, 41", idle.artifacts["nvidia_smi_idle.csv"])

                sampling_task = {
                    "run_id": run_id,
                    "task_type": "telemetry",
                    "node_role": None,
                    "telemetry": {
                        "backend": "nvidia_smi",
                        "interval_ms": 20,
                        "query_fields": [
                            "timestamp",
                            "power.draw",
                            "temperature.gpu",
                        ],
                        "rail_manifest": ["gpu_board"],
                    },
                }
                sampling_start = client.run_task(
                    {
                        **sampling_task,
                        "task_id": "task-telemetry-start-sampling",
                        "operation": "start_sampling",
                    },
                    timeout_s=15.0,
                )
                self.assertTrue(sampling_start.ok, sampling_start)
                self.assertEqual(
                    sampling_start.raw_status["artifacts"],
                    {
                        "nvidia_smi_pidfile": "nvidia_smi.pid",
                        "status_json": "status.json",
                        "worker_log": "worker.log",
                    },
                )
                self.assertIn(b'"command"', sampling_start.artifacts["nvidia_smi.pid"])
                sampler_pidfile = remote_root / run_id / "state" / "nvidia_smi.pid"
                sampler_payload = json.loads(sampler_pidfile.read_text(encoding="utf-8"))
                self._pin_pidfile_to_live_script_command(
                    sampler_pidfile, int(sampler_payload["pid"])
                )

                sampling_stop = client.run_task(
                    {
                        **sampling_task,
                        "task_id": "task-telemetry-stop-sampling",
                        "operation": "stop_sampling",
                    },
                    timeout_s=15.0,
                )
                self.assertTrue(sampling_stop.ok, sampling_stop)
                self.assertEqual(
                    sampling_stop.raw_status["artifacts"],
                    {
                        "nvidia_smi_csv": "nvidia_smi.csv",
                        "nvidia_smi_pidfile": "nvidia_smi.pid",
                        "status_json": "status.json",
                        "worker_log": "worker.log",
                    },
                )
                self.assertIn(b", 12.5, 41", sampling_stop.artifacts["nvidia_smi.csv"])
                # The test re-pins the pidfile to the live resolved command
                # between start and stop (identity-aware worker), so compare
                # the semantic identity, not raw bytes.
                stop_pid_payload = json.loads(
                    sampling_stop.artifacts["nvidia_smi.pid"].decode("utf-8")
                )
                start_pid_payload = json.loads(
                    sampling_start.artifacts["nvidia_smi.pid"].decode("utf-8")
                )
                self.assertEqual(
                    stop_pid_payload["pid"], start_pid_payload["pid"]
                )

                self._pin_pidfile_to_live_script_command(pidfile, server_pid)
                cleanup = client.run_task(
                    self._runtime_task(run_id, "cleanup", "task-runtime-cleanup"),
                    timeout_s=15.0,
                )
                self.assertTrue(cleanup.ok, cleanup)
                self._assert_artifact_name_parity(cleanup)
                self.assertFalse((remote_root / run_id).exists())
                self.assertTrue(client.cleanup_report())
                self.assertTrue(
                    all(row["removed"] for row in client.cleanup_report()),
                    client.cleanup_report(),
                )
            finally:
                if server_pid is not None and self._pid_alive(server_pid):
                    os.kill(server_pid, signal.SIGKILL)

    def _runtime_task(self, run_id: str, operation: str, task_id: str) -> dict[str, Any]:
        return {
            "task_id": task_id,
            "run_id": run_id,
            "task_type": "runtime",
            "operation": operation,
            "node_role": None,
            "runtime": {
                "backend": "vllm",
                "model": {
                    "name": "fake/model",
                    "source": "/fake/model",
                    "revision": "test",
                    "weight_format": "safetensors",
                },
                "quantization": {"name": "none"},
                "options": {
                    "tensor_parallel_size": 1,
                    "gpu_memory_utilization": 0.1,
                    "served_model_name": "nv5-fake-model",
                },
            },
        }

    def _assert_artifact_name_parity(self, result: Any) -> None:
        self.assertIsInstance(result.raw_status, dict)
        for logical_name, filename in result.raw_status["artifacts"].items():
            with self.subTest(logical_name=logical_name, filename=filename):
                self.assertIn(filename, result.artifacts)

    def _pin_pidfile_to_live_script_command(self, pidfile: Path, pid: int) -> None:
        command = subprocess.run(
            ["ps", "-p", str(pid), "-o", "args="],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip().split()
        lstart = subprocess.run(
            ["ps", "-p", str(pid), "-o", "lstart="],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        payload = json.loads(pidfile.read_text(encoding="utf-8"))
        payload["command"] = command
        payload["ps_lstart"] = lstart
        pidfile.write_text(json.dumps(payload), encoding="utf-8")

    def _pid_alive(self, pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except OSError:
            return True
        return True

    def _write_fake_vllm(self, path: Path) -> None:
        path.write_text(
            f"""#!{sys.executable}
import json
import signal
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

port = int(sys.argv[sys.argv.index('--port') + 1])

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', '0'))
        payload = json.loads(self.rfile.read(length) or b'{{}}')
        if self.path == '/tokenize':
            body = json.dumps({{'token_ids': [101, 202]}}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == '/v1/completions' and payload.get('stream'):
            body = (
                'data: {{"choices":[{{"text":"AB"}}]}}\\n\\n'
                'data: {{"choices":[{{"text":"C"}}]}}\\n\\n'
                'data: {{"choices":[],"usage":{{"completion_tokens":3}}}}\\n\\n'
                'data: [DONE]\\n\\n'
            ).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        body = json.dumps({{'choices': [{{'text': 'W'}}]}}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))
server.serve_forever()
""",
            encoding="utf-8",
        )
        path.chmod(0o755)

    def _write_fake_nvidia_smi(self, path: Path) -> None:
        path.write_text(
            """#!/bin/sh
trap 'exit 0' TERM INT
i=0
while [ "$i" -lt 5 ]; do
    printf '2026/07/07 12:00:0%s.000, 12.5, 41\n' "$i"
    i=$((i + 1))
done
while :; do
    printf '2026/07/07 12:00:05.000, 12.5, 41\n'
    sleep 0.02
done
""",
            encoding="utf-8",
        )
        path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
