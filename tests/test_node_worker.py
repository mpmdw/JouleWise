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
                self.assertTrue((tmpdir / "state" / "nvidia_smi.pid").exists())
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


if __name__ == "__main__":
    unittest.main()
