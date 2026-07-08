"""CI-safe tests for the self-contained node worker harness (Slice 2K U1)."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKER_PATH = REPO_ROOT / "joulewise" / "adapters" / "node_worker.py"


def import_node_worker():
    spec = importlib.util.spec_from_file_location("node_worker", WORKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import node_worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


node_worker = import_node_worker()


def valid_task(**overrides: Any) -> dict[str, Any]:
    task: dict[str, Any] = {
        "protocol_version": 1,
        "task_id": "task-telemetry-idle-001",
        "run_id": "run-3050-smoke-001",
        "task_type": "telemetry",
        "operation": "measure_idle",
        "node_role": None,
        "paths": {"state_dir": ""},
        "telemetry": {
            "backend": "nvidia_smi",
            "interval_ms": 100,
            "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
            "rail_manifest": ["gpu_board"],
        },
    }
    task.update(overrides)
    return task


def valid_runtime_task(**overrides: Any) -> dict[str, Any]:
    task: dict[str, Any] = {
        "protocol_version": 1,
        "task_id": "task-runtime-prepare-001",
        "run_id": "run-3050-smoke-001",
        "task_type": "runtime",
        "operation": "prepare",
        "node_role": None,
        "paths": {"state_dir": ""},
        "runtime": {
            "backend": "vllm",
            "model": {
                "name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                "revision": "main",
                "weight_format": "safetensors",
            },
            "quantization": {"name": "none"},
            "options": {
                "tensor_parallel_size": 1,
                "gpu_memory_utilization": 0.82,
                "served_model_name": "jw-3050-smoke",
            },
        },
    }
    task.update(overrides)
    return task


def valid_workload_task(**overrides: Any) -> dict[str, Any]:
    task: dict[str, Any] = {
        "protocol_version": 1,
        "task_id": "task-runtime-run-001",
        "run_id": "run-3050-smoke-001",
        "task_type": "runtime",
        "operation": "run_workload",
        "node_role": None,
        "paths": {"state_dir": ""},
        "workload": {
            "prompt_text": "alpha beta",
            "prompt_tokens": 2,
            "output_tokens": 3,
            "sampling_params": {
                "max_tokens": 3,
                "temperature": 0.0,
                "top_p": 1.0,
                "seed": 0,
            },
        },
    }
    task.update(overrides)
    return task


class NodeWorkerTests(unittest.TestCase):
    def write_task(self, tmpdir: Path, task: dict[str, Any]) -> Path:
        task.setdefault("paths", {})["state_dir"] = str(tmpdir / "state")
        task_path = tmpdir / "task.json"
        task_path.write_text(json.dumps(task), encoding="utf-8")
        return task_path

    def read_status(self, artifacts_dir: Path) -> dict[str, Any]:
        return json.loads((artifacts_dir / "status.json").read_text(encoding="utf-8"))

    def run_subprocess(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(WORKER_PATH), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_import_node_worker_directly(self) -> None:
        self.assertEqual(node_worker.PROTOCOL_VERSION, 1)
        self.assertTrue(callable(node_worker.main))

    def test_in_process_valid_unimplemented_telemetry_task_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            artifacts_dir = tmpdir / "artifacts"
            task_path = self.write_task(tmpdir, valid_task(operation="bogus_operation"))

            code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

            self.assertEqual(code, 1)
            status = self.read_status(artifacts_dir)
            self.assertEqual(status["status"], "unsupported")
            self.assertEqual(status["failure_reason"], "unsupported_workload")
            self.assertIn("not implemented in this worker build", status["message"])
            self.assertEqual(
                status["artifacts"],
                {"status_json": "status.json", "worker_log": "worker.log"},
            )
            self.assertTrue((artifacts_dir / "worker.log").exists())
            self.assertTrue((tmpdir / "state").is_dir())
            self.assertLessEqual(status["started_at_s"], status["ended_at_s"])
            self.assertLessEqual(status["monotonic_started_s"], status["monotonic_ended_s"])

    def test_subprocess_valid_unimplemented_telemetry_task_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            artifacts_dir = tmpdir / "artifacts"
            task_path = self.write_task(tmpdir, valid_task(operation="bogus_operation"))

            result = self.run_subprocess(
                "--task",
                str(task_path),
                "--artifacts",
                str(artifacts_dir),
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            status = self.read_status(artifacts_dir)
            self.assertEqual(status["task_id"], "task-telemetry-idle-001")
            self.assertEqual(status["status"], "unsupported")
            self.assertEqual(status["failure_reason"], "unsupported_workload")
            self.assertEqual(status["artifacts"]["worker_log"], "worker.log")
            self.assertTrue((artifacts_dir / "worker.log").exists())

    def test_malformed_json_writes_failed_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            artifacts_dir = tmpdir / "artifacts"
            task_path = tmpdir / "task.json"
            task_path.write_text("{", encoding="utf-8")

            result = self.run_subprocess(
                "--task",
                str(task_path),
                "--artifacts",
                str(artifacts_dir),
            )

            self.assertEqual(result.returncode, 1)
            status = self.read_status(artifacts_dir)
            self.assertEqual(status["status"], "failed")
            self.assertEqual(status["failure_reason"], "unknown_error")
            self.assertIn("malformed task JSON", status["message"])
            self.assertIsNone(status["task_id"])
            self.assertTrue((artifacts_dir / "worker.log").exists())

    def test_missing_required_field_names_the_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            artifacts_dir = tmpdir / "artifacts"
            task = valid_task()
            del task["task_id"]
            task_path = self.write_task(tmpdir, task)

            code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

            self.assertEqual(code, 1)
            status = self.read_status(artifacts_dir)
            self.assertEqual(status["status"], "failed")
            self.assertEqual(status["failure_reason"], "unknown_error")
            self.assertIn("task_id", status["message"])

    def test_wrong_protocol_version_names_version(self) -> None:
        cases = [
            ("int", {"protocol_version": 2}),
            ("string", {"protocol_version": "1"}),
            ("missing", {}),
        ]
        for name, patch in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    tmpdir = Path(tmp)
                    artifacts_dir = tmpdir / "artifacts"
                    task = valid_task()
                    if name == "missing":
                        del task["protocol_version"]
                    else:
                        task.update(patch)
                    task_path = self.write_task(tmpdir, task)

                    code = node_worker.main(
                        ["--task", str(task_path), "--artifacts", str(artifacts_dir)]
                    )

                    self.assertEqual(code, 1)
                    status = self.read_status(artifacts_dir)
                    self.assertEqual(status["status"], "failed")
                    self.assertEqual(status["failure_reason"], "unknown_error")
                    self.assertIn("protocol_version", status["message"])

    def test_unknown_task_type_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            artifacts_dir = tmpdir / "artifacts"
            task_path = self.write_task(tmpdir, valid_task(task_type="bogus"))

            code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

            self.assertEqual(code, 1)
            status = self.read_status(artifacts_dir)
            self.assertEqual(status["status"], "unsupported")
            self.assertEqual(status["failure_reason"], "unsupported_workload")
            self.assertEqual(status["task_type"], "bogus")

    def test_status_json_atomicity_leaves_no_tmp_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            artifacts_dir = tmpdir / "artifacts"
            task_path = self.write_task(tmpdir, valid_task())

            code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

            self.assertEqual(code, 1)
            leftovers = [path.name for path in artifacts_dir.iterdir() if ".status.json.tmp." in path.name]
            self.assertEqual(leftovers, [])

    def test_artifacts_path_existing_file_is_catastrophic_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            artifacts_file = tmpdir / "artifacts"
            artifacts_file.write_text("not a directory", encoding="utf-8")
            task_path = self.write_task(tmpdir, valid_task())

            result = self.run_subprocess(
                "--task",
                str(task_path),
                "--artifacts",
                str(artifacts_file),
            )

            self.assertEqual(result.returncode, 2)

    def test_clock_echo_prints_parseable_json(self) -> None:
        result = self.run_subprocess("--clock-echo")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIsInstance(payload["node_time_s"], float)
        self.assertIsInstance(payload["monotonic_s"], float)

    def test_telemetry_start_stop_with_fake_nvidia_smi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            bin_dir = tmpdir / "bin"
            self.write_fake_nvidia_smi(bin_dir)
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path
            try:
                start_artifacts = tmpdir / "start-artifacts"
                start_task = self.write_task(
                    tmpdir,
                    valid_task(operation="start_sampling", task_id="task-start"),
                )

                start_code = node_worker.main(
                    ["--task", str(start_task), "--artifacts", str(start_artifacts)]
                )

                self.assertEqual(start_code, 0)
                start_status = self.read_status(start_artifacts)
                self.assertEqual(start_status["status"], "succeeded")
                self.assertEqual(start_status["failure_reason"], None)
                self.assertEqual(
                    start_status["artifacts"]["nvidia_smi_pidfile"],
                    "nvidia_smi.pid",
                )
                self.assertIn("node_utc_offset_s", start_status["metadata"])
                self.assertIn("node_tzname", start_status["metadata"])
                self.assertTrue((tmpdir / "state" / "nvidia_smi.pid").exists())
                start_pid_payload = json.loads(
                    (tmpdir / "state" / "nvidia_smi.pid").read_text(encoding="utf-8")
                )
                self.assertIn("node_utc_offset_s", start_pid_payload)
                self.assertIn("node_tzname", start_pid_payload)
                self.assertIn("ps_lstart", start_pid_payload)
                self.assertTrue((tmpdir / "state" / "nvidia_smi.csv").exists())
                self.assertFalse((start_artifacts / "nvidia_smi.csv").exists())

                stop_artifacts = tmpdir / "stop-artifacts"
                stop_task = self.write_task(
                    tmpdir,
                    valid_task(operation="stop_sampling", task_id="task-stop"),
                )

                stop_code = node_worker.main(
                    ["--task", str(stop_task), "--artifacts", str(stop_artifacts)]
                )

                self.assertEqual(stop_code, 0)
                stop_status = self.read_status(stop_artifacts)
                self.assertEqual(stop_status["status"], "succeeded")
                self.assertEqual(stop_status["artifacts"]["nvidia_smi_csv"], "nvidia_smi.csv")
                csv_text = (stop_artifacts / "nvidia_smi.csv").read_text(encoding="utf-8")
                self.assertIn("2026/07/07 12:00:00.000", csv_text)
            finally:
                os.environ["PATH"] = old_path

    def test_telemetry_measure_idle_with_fake_nvidia_smi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            bin_dir = tmpdir / "bin"
            self.write_fake_nvidia_smi(bin_dir)
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path
            try:
                artifacts_dir = tmpdir / "artifacts"
                task = valid_task(task_id="task-idle")
                task["telemetry"]["idle_seconds"] = 0.2
                task["telemetry"]["interval_ms"] = 50
                task_path = self.write_task(tmpdir, task)

                code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

                self.assertEqual(code, 0)
                status = self.read_status(artifacts_dir)
                self.assertEqual(status["status"], "succeeded")
                self.assertEqual(status["artifacts"]["nvidia_smi_idle_csv"], "nvidia_smi_idle.csv")
                self.assertIn("node_utc_offset_s", status["metadata"])
                self.assertIn("node_tzname", status["metadata"])
                csv_text = (artifacts_dir / "nvidia_smi_idle.csv").read_text(encoding="utf-8")
                self.assertIn("2026/07/07 12:00:00.000", csv_text)
            finally:
                os.environ["PATH"] = old_path

    def test_telemetry_missing_nvidia_smi_is_telemetry_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            bin_dir = tmpdir / "empty-bin"
            bin_dir.mkdir()
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = str(bin_dir)
            try:
                artifacts_dir = tmpdir / "artifacts"
                task_path = self.write_task(
                    tmpdir,
                    valid_task(operation="start_sampling", task_id="task-start-missing"),
                )

                code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

                self.assertEqual(code, 1)
                status = self.read_status(artifacts_dir)
                self.assertEqual(status["status"], "unsupported")
                self.assertEqual(status["failure_reason"], "telemetry_unavailable")
                self.assertIn("nvidia-smi unavailable", status["message"])
            finally:
                os.environ["PATH"] = old_path

    def test_runtime_prepare_warmup_run_cleanup_with_fake_vllm(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            bin_dir = tmpdir / "bin"
            self.write_fake_vllm(bin_dir)
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path
            old_wait = node_worker._wait_for_vllm_health
            old_post = node_worker._vllm_json_post
            old_stream = node_worker._vllm_stream_completion
            node_worker._wait_for_vllm_health = lambda process, port, stderr_path, timeout_s: {  # type: ignore[assignment]
                "ok": True,
                "ready_check": "fake_http_health",
                "status": 200,
            }
            node_worker._vllm_json_post = lambda port, path, payload: {"choices": [{"text": "W"}]}  # type: ignore[assignment]
            node_worker._vllm_stream_completion = lambda port, path, payload, timeout_s: iter(["A", "B", "C"])  # type: ignore[assignment]
            port = 32123
            try:
                runtime = valid_runtime_task()["runtime"]
                runtime["options"] = {**runtime["options"], "port": port}
                prepare_artifacts = tmpdir / "prepare-artifacts"
                prepare_task = self.write_task(
                    tmpdir,
                    valid_runtime_task(task_id="task-prepare", runtime=runtime),
                )

                prepare_code = node_worker.main(
                    ["--task", str(prepare_task), "--artifacts", str(prepare_artifacts)]
                )

                self.assertEqual(prepare_code, 0)
                prepare_status = self.read_status(prepare_artifacts)
                self.assertEqual(prepare_status["status"], "succeeded")
                self.assertEqual(prepare_status["artifacts"]["vllm_pidfile"], "vllm.pid")
                pidfile = tmpdir / "state" / "vllm.pid"
                self.assertTrue(pidfile.exists())
                pid_payload = json.loads(pidfile.read_text(encoding="utf-8"))
                self.assertEqual(pid_payload["port"], port)
                self.assertEqual(pid_payload["served_model_name"], "jw-3050-smoke")
                self.assertIn("ps_lstart", pid_payload)

                warmup_artifacts = tmpdir / "warmup-artifacts"
                warmup_task = self.write_task(
                    tmpdir,
                    valid_runtime_task(
                        task_id="task-warmup",
                        operation="warmup",
                        runtime=runtime,
                    ),
                )
                warmup_code = node_worker.main(
                    ["--task", str(warmup_task), "--artifacts", str(warmup_artifacts)]
                )
                self.assertEqual(warmup_code, 0)
                warmup_status = self.read_status(warmup_artifacts)
                self.assertEqual(warmup_status["status"], "succeeded")

                run_artifacts = tmpdir / "run-artifacts"
                run_task = self.write_task(
                    tmpdir,
                    valid_workload_task(task_id="task-run"),
                )
                run_code = node_worker.main(
                    ["--task", str(run_task), "--artifacts", str(run_artifacts)]
                )
                self.assertEqual(run_code, 0)
                run_status = self.read_status(run_artifacts)
                self.assertEqual(run_status["status"], "succeeded")
                self.assertEqual(run_status["artifacts"]["events_jsonl"], "events.jsonl")
                self.assertEqual(run_status["artifacts"]["response_txt"], "response.txt")
                self.assertEqual(run_status["artifacts"]["tokens_jsonl"], "tokens.jsonl")
                self.assertEqual((run_artifacts / "response.txt").read_text(encoding="utf-8"), "ABC")
                tokens = [
                    json.loads(line)
                    for line in (run_artifacts / "tokens.jsonl").read_text(encoding="utf-8").splitlines()
                ]
                self.assertEqual([token["text"] for token in tokens], ["A", "B", "C"])
                self.assertEqual([token["index"] for token in tokens], [0, 1, 2])
                self.assertTrue(all(isinstance(token["timestamp_s"], float) for token in tokens))
                events = [
                    json.loads(line)
                    for line in (run_artifacts / "events.jsonl").read_text(encoding="utf-8").splitlines()
                ]
                self.assertEqual(
                    [(event["event_type"], event["phase"]) for event in events],
                    [
                        ("phase_start", "prefill"),
                        ("phase_end", "prefill"),
                        ("phase_start", "decode"),
                        ("phase_end", "decode"),
                    ],
                )

                cleanup_artifacts = tmpdir / "cleanup-artifacts"
                cleanup_task = self.write_task(
                    tmpdir,
                    valid_runtime_task(
                        task_id="task-cleanup",
                        operation="cleanup",
                        runtime=runtime,
                    ),
                )
                cleanup_code = node_worker.main(
                    ["--task", str(cleanup_task), "--artifacts", str(cleanup_artifacts)]
                )
                self.assertEqual(cleanup_code, 0)
                cleanup_status = self.read_status(cleanup_artifacts)
                self.assertEqual(cleanup_status["status"], "succeeded")
                self.assertFalse(pidfile.exists())

                cleanup_again_artifacts = tmpdir / "cleanup-again-artifacts"
                cleanup_again_task = self.write_task(
                    tmpdir,
                    valid_runtime_task(
                        task_id="task-cleanup-again",
                        operation="cleanup",
                        runtime=runtime,
                    ),
                )
                cleanup_again_code = node_worker.main(
                    ["--task", str(cleanup_again_task), "--artifacts", str(cleanup_again_artifacts)]
                )
                self.assertEqual(cleanup_again_code, 0)
                cleanup_again_status = self.read_status(cleanup_again_artifacts)
                self.assertEqual(cleanup_again_status["status"], "succeeded")
                self.assertEqual(cleanup_again_status["metadata"]["termination"], "no_pidfile")
            finally:
                os.environ["PATH"] = old_path
                node_worker._wait_for_vllm_health = old_wait
                node_worker._vllm_json_post = old_post
                node_worker._vllm_stream_completion = old_stream

    def test_runtime_missing_vllm_launcher_is_runtime_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            bin_dir = tmpdir / "empty-bin"
            bin_dir.mkdir()
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = str(bin_dir)
            try:
                artifacts_dir = tmpdir / "artifacts"
                runtime = valid_runtime_task()["runtime"]
                runtime["options"] = {**runtime["options"], "port": 32124}
                task_path = self.write_task(
                    tmpdir,
                    valid_runtime_task(task_id="task-vllm-missing", runtime=runtime),
                )

                code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

                self.assertEqual(code, 1)
                status = self.read_status(artifacts_dir)
                self.assertEqual(status["status"], "unsupported")
                self.assertEqual(status["failure_reason"], "runtime_unavailable")
                self.assertIn("vLLM launcher unavailable", status["message"])
            finally:
                os.environ["PATH"] = old_path

    def test_runtime_vllm_oom_during_prepare_is_did_not_fit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            bin_dir = tmpdir / "bin"
            self.write_fake_vllm(bin_dir)
            old_path = os.environ.get("PATH", "")
            old_mode = os.environ.get("JW_FAKE_VLLM_MODE")
            os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path
            os.environ["JW_FAKE_VLLM_MODE"] = "oom"
            try:
                artifacts_dir = tmpdir / "artifacts"
                runtime = valid_runtime_task()["runtime"]
                runtime["options"] = {**runtime["options"], "port": 32125}
                task_path = self.write_task(
                    tmpdir,
                    valid_runtime_task(task_id="task-vllm-oom", runtime=runtime),
                )

                code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

                self.assertEqual(code, 1)
                status = self.read_status(artifacts_dir)
                self.assertEqual(status["status"], "unsupported")
                self.assertEqual(status["failure_reason"], "did_not_fit")
                self.assertIn("oom_patterns", status["metadata"])
                self.assertIn("CUDA out of memory", status["metadata"]["stderr_tail"])
            finally:
                os.environ["PATH"] = old_path
                if old_mode is None:
                    os.environ.pop("JW_FAKE_VLLM_MODE", None)
                else:
                    os.environ["JW_FAKE_VLLM_MODE"] = old_mode

    def test_runtime_vllm_import_error_during_readiness_is_runtime_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            bin_dir = tmpdir / "bin"
            self.write_fake_vllm(bin_dir)
            old_path = os.environ.get("PATH", "")
            old_mode = os.environ.get("JW_FAKE_VLLM_MODE")
            os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path
            os.environ["JW_FAKE_VLLM_MODE"] = "import_error"
            try:
                artifacts_dir = tmpdir / "artifacts"
                runtime = valid_runtime_task()["runtime"]
                runtime["options"] = {**runtime["options"], "port": 32126}
                task_path = self.write_task(
                    tmpdir,
                    valid_runtime_task(task_id="task-vllm-import-error", runtime=runtime),
                )

                code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

                self.assertEqual(code, 1)
                status = self.read_status(artifacts_dir)
                self.assertEqual(status["status"], "unsupported")
                self.assertEqual(status["failure_reason"], "runtime_unavailable")
                self.assertIn("ModuleNotFoundError", status["metadata"]["stderr_tail"])
            finally:
                os.environ["PATH"] = old_path
                if old_mode is None:
                    os.environ.pop("JW_FAKE_VLLM_MODE", None)
                else:
                    os.environ["JW_FAKE_VLLM_MODE"] = old_mode

    def test_vllm_prepare_honors_task_readiness_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            bin_dir = tmpdir / "bin"
            self.write_fake_vllm(bin_dir)
            old_path = os.environ.get("PATH", "")
            old_wait = node_worker._wait_for_vllm_health
            captured: dict[str, float] = {}
            os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path

            def fake_wait(process, port, stderr_path, timeout_s):
                captured["timeout_s"] = timeout_s
                return {"ok": False, "message": "not ready"}

            node_worker._wait_for_vllm_health = fake_wait  # type: ignore[assignment]
            try:
                artifacts_dir = tmpdir / "artifacts"
                runtime = valid_runtime_task()["runtime"]
                runtime["options"] = {**runtime["options"], "port": 32127}
                task = valid_runtime_task(task_id="task-vllm-timeout", runtime=runtime)
                task["timeout_s"] = 123.0
                task_path = self.write_task(tmpdir, task)

                code = node_worker.main(["--task", str(task_path), "--artifacts", str(artifacts_dir)])

                self.assertEqual(code, 1)
                self.assertEqual(captured["timeout_s"], 123.0)
                status = self.read_status(artifacts_dir)
                self.assertEqual(status["metadata"]["readiness_timeout_s"], 123.0)
            finally:
                os.environ["PATH"] = old_path
                node_worker._wait_for_vllm_health = old_wait

    def test_vllm_http_error_body_participates_in_oom_classification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            state_dir = tmpdir / "state"
            artifacts_dir = tmpdir / "artifacts"
            state_dir.mkdir()
            artifacts_dir.mkdir()
            pidfile = state_dir / "vllm.pid"
            pidfile.write_text(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "command": ["python"],
                        "port": 32128,
                        "served_model_name": "jw-3050-smoke",
                        "stderr_path": str(state_dir / "vllm.stderr"),
                    }
                ),
                encoding="utf-8",
            )
            old_stream = node_worker._vllm_stream_completion
            node_worker._vllm_stream_completion = (  # type: ignore[assignment]
                lambda port, path, payload, timeout_s: (_ for _ in ()).throw(
                    node_worker.VllmHttpError("HTTP 500: CUDA out of memory in body")
                )
            )
            try:
                status, reason, message, artifacts, metadata = node_worker.handle_vllm_run_workload(
                    valid_workload_task(paths={"state_dir": str(state_dir)}),
                    str(artifacts_dir),
                    lambda line: None,
                )
            finally:
                node_worker._vllm_stream_completion = old_stream

            self.assertEqual(status, "unsupported")
            self.assertEqual(reason, "did_not_fit")
            self.assertIn("out-of-memory", message)
            self.assertIn("CUDA out of memory", metadata["exception"])

    def test_vllm_cleanup_stale_pidfile_does_not_signal_reused_pid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            state_dir = tmpdir / "state"
            state_dir.mkdir()
            pidfile = state_dir / "vllm.pid"
            pidfile.write_text(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "command": ["definitely-not-this-process"],
                        "node_started_at_s": 1.0,
                    }
                ),
                encoding="utf-8",
            )
            old_kill = node_worker.os.kill
            calls: list[tuple[int, int]] = []

            def fake_kill(pid: int, sig: int) -> None:
                calls.append((pid, sig))
                raise AssertionError("stale pidfile should not signal")

            node_worker.os.kill = fake_kill  # type: ignore[assignment]
            try:
                status, reason, message, artifacts, metadata = node_worker.handle_vllm_cleanup(
                    valid_runtime_task(operation="cleanup", paths={"state_dir": str(state_dir)}),
                    str(tmpdir / "artifacts"),
                    lambda line: None,
                )
            finally:
                node_worker.os.kill = old_kill  # type: ignore[assignment]

            self.assertEqual(status, "succeeded")
            self.assertIsNone(reason)
            self.assertIn("stale", message)
            self.assertFalse(pidfile.exists())
            self.assertEqual(calls, [])

    def test_vllm_cleanup_same_argv_different_start_time_does_not_signal_reused_pid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            state_dir = tmpdir / "state"
            state_dir.mkdir()
            pidfile = state_dir / "vllm.pid"
            pidfile.write_text(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "command": ["vllm", "serve", "model"],
                        "ps_lstart": "Tue Jul  7 00:00:00 2026",
                    }
                ),
                encoding="utf-8",
            )
            old_kill = node_worker.os.kill
            old_cmdline = node_worker._live_process_cmdline
            old_lstart = node_worker._process_lstart
            calls: list[tuple[int, int]] = []

            def fake_kill(pid: int, sig: int) -> None:
                calls.append((pid, sig))
                raise AssertionError("stale pidfile should not signal")

            node_worker.os.kill = fake_kill  # type: ignore[assignment]
            node_worker._live_process_cmdline = lambda pid: ["vllm", "serve", "model"]  # type: ignore[assignment]
            node_worker._process_lstart = lambda pid: "Tue Jul  7 00:01:00 2026"  # type: ignore[assignment]
            try:
                status, reason, message, artifacts, metadata = node_worker.handle_vllm_cleanup(
                    valid_runtime_task(operation="cleanup", paths={"state_dir": str(state_dir)}),
                    str(tmpdir / "artifacts"),
                    lambda line: None,
                )
            finally:
                node_worker.os.kill = old_kill  # type: ignore[assignment]
                node_worker._live_process_cmdline = old_cmdline  # type: ignore[assignment]
                node_worker._process_lstart = old_lstart  # type: ignore[assignment]

            self.assertEqual(status, "succeeded")
            self.assertIsNone(reason)
            self.assertIn("stale", message)
            self.assertEqual(metadata["pid_verification"], "start_time_mismatch")
            self.assertFalse(pidfile.exists())
            self.assertEqual(calls, [])

    def test_nvidia_smi_stop_stale_pidfile_does_not_signal_reused_pid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            state_dir = tmpdir / "state"
            artifacts_dir = tmpdir / "artifacts"
            state_dir.mkdir()
            artifacts_dir.mkdir()
            pidfile = state_dir / "nvidia_smi.pid"
            pidfile.write_text(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "command": ["definitely-not-nvidia-smi"],
                        "node_started_at_s": 1.0,
                    }
                ),
                encoding="utf-8",
            )
            old_kill = node_worker.os.kill
            calls: list[tuple[int, int]] = []

            def fake_kill(pid: int, sig: int) -> None:
                calls.append((pid, sig))
                raise AssertionError("stale pidfile should not signal")

            node_worker.os.kill = fake_kill  # type: ignore[assignment]
            try:
                status, reason, message, artifacts, metadata = node_worker.handle_nvidia_smi_stop_sampling(
                    valid_task(operation="stop_sampling", paths={"state_dir": str(state_dir)}),
                    str(artifacts_dir),
                    lambda line: None,
                )
            finally:
                node_worker.os.kill = old_kill  # type: ignore[assignment]

            self.assertEqual(status, "failed")
            self.assertEqual(reason, "unknown_error")
            self.assertIn("stale", message)
            self.assertNotIn("nvidia_smi_csv", artifacts)
            self.assertFalse(pidfile.exists())
            self.assertEqual(calls, [])

    def test_nvidia_smi_stop_same_argv_different_start_time_does_not_signal_reused_pid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            state_dir = tmpdir / "state"
            artifacts_dir = tmpdir / "artifacts"
            state_dir.mkdir()
            artifacts_dir.mkdir()
            pidfile = state_dir / "nvidia_smi.pid"
            pidfile.write_text(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "command": [
                            "nvidia-smi",
                            "--query-gpu=timestamp,power.draw,temperature.gpu",
                            "--format=csv,noheader,nounits",
                            "-lms",
                            "100",
                        ],
                        "ps_lstart": "Tue Jul  7 00:00:00 2026",
                    }
                ),
                encoding="utf-8",
            )
            old_kill = node_worker.os.kill
            old_cmdline = node_worker._live_process_cmdline
            old_lstart = node_worker._process_lstart
            calls: list[tuple[int, int]] = []

            def fake_kill(pid: int, sig: int) -> None:
                calls.append((pid, sig))
                raise AssertionError("stale pidfile should not signal")

            node_worker.os.kill = fake_kill  # type: ignore[assignment]
            node_worker._live_process_cmdline = (  # type: ignore[assignment]
                lambda pid: [
                    "nvidia-smi",
                    "--query-gpu=timestamp,power.draw,temperature.gpu",
                    "--format=csv,noheader,nounits",
                    "-lms",
                    "100",
                ]
            )
            node_worker._process_lstart = lambda pid: "Tue Jul  7 00:01:00 2026"  # type: ignore[assignment]
            try:
                status, reason, message, artifacts, metadata = node_worker.handle_nvidia_smi_stop_sampling(
                    valid_task(operation="stop_sampling", paths={"state_dir": str(state_dir)}),
                    str(artifacts_dir),
                    lambda line: None,
                )
            finally:
                node_worker.os.kill = old_kill  # type: ignore[assignment]
                node_worker._live_process_cmdline = old_cmdline  # type: ignore[assignment]
                node_worker._process_lstart = old_lstart  # type: ignore[assignment]

            self.assertEqual(status, "failed")
            self.assertEqual(reason, "unknown_error")
            self.assertIn("stale", message)
            self.assertEqual(metadata["pid_verification"], "start_time_mismatch")
            self.assertNotIn("nvidia_smi_csv", artifacts)
            self.assertFalse(pidfile.exists())
            self.assertEqual(calls, [])

    def write_fake_nvidia_smi(self, bin_dir: Path) -> Path:
        bin_dir.mkdir()
        path = bin_dir / "nvidia-smi"
        path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import signal",
                    "import time",
                    "running = True",
                    "def stop(signum, frame):",
                    "    global running",
                    "    running = False",
                    "signal.signal(signal.SIGTERM, stop)",
                    "i = 0",
                    "while running:",
                    "    print(f'2026/07/07 12:00:{i % 60:02d}.000, {10.0 + i:.2f}, {40 + i % 10}', flush=True)",
                    "    i += 1",
                    "    time.sleep(0.05)",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path

    def write_fake_vllm(self, bin_dir: Path) -> Path:
        bin_dir.mkdir()
        path = bin_dir / "vllm"
        path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import json",
                    "import os",
                    "import signal",
                    "import sys",
                    "import time",
                    "",
                    "if os.environ.get('JW_FAKE_VLLM_MODE') == 'oom':",
                    "    print('CUDA out of memory while loading fake model', file=sys.stderr, flush=True)",
                    "    sys.exit(3)",
                    "if os.environ.get('JW_FAKE_VLLM_MODE') == 'import_error':",
                    "    print('ModuleNotFoundError: No module named vllm', file=sys.stderr, flush=True)",
                    "    sys.exit(4)",
                    "running = True",
                    "def stop(signum, frame):",
                    "    global running",
                    "    running = False",
                    "signal.signal(signal.SIGTERM, stop)",
                    "while running:",
                    "    time.sleep(0.05)",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path


if __name__ == "__main__":
    unittest.main()
