"""Additional edge-case pins for Slice 2K NVIDIA node-worker protocol."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from joulewise.adapters.node_client import ClockMarker, NodeWorkerClient, compute_stage_bound
from joulewise.adapters.nvidia_smi import parse_nvidia_smi_csv
from joulewise.adapters.ssh_transport import RunnerCompleted, SshTransport
from joulewise.interfaces import AdapterResult
from joulewise.schemas import FailureReason

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKER_PATH = REPO_ROOT / "joulewise" / "adapters" / "node_worker.py"


def import_node_worker() -> Any:
    spec = importlib.util.spec_from_file_location("node_worker_amplification", WORKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import node_worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


node_worker = import_node_worker()


class SequencedClock:
    def __init__(self, values):
        self.values = list(values)

    def now(self) -> float:
        if not self.values:
            raise AssertionError("clock exhausted")
        return self.values.pop(0)

    def sleep(self, seconds: float) -> None:
        raise AssertionError("sleep is not expected")

    def info(self) -> dict:
        return {"kind": "sequenced"}


class CapturingRunner:
    def __init__(self, result: Optional[RunnerCompleted] = None):
        self.result = result or RunnerCompleted(returncode=0)
        self.calls = []

    def __call__(self, argv, *, timeout):
        self.calls.append((list(argv), timeout))
        return self.result


class ProtocolFakeTransport:
    def __init__(self):
        self.put_destinations = []
        self.put_json_payloads = []
        self.collect_sources = []
        self.run_commands = []
        self.clock_echoes = [
            '{"node_time_s": 1000.0, "monotonic_s": 10.0}\n',
            '{"node_time_s": 1002.0, "monotonic_s": 12.0}\n',
            '{"node_time_s": 2000.0, "monotonic_s": 20.0}\n',
            '{"node_time_s": 2002.0, "monotonic_s": 22.0}\n',
        ]
        self.clock_alignment = None

    def run(self, command, *, timeout_s=None):
        command = list(command)
        self.run_commands.append((command, timeout_s))
        if command[:2] == ["mkdir", "-p"]:
            for path in command[2:]:
                Path(path).mkdir(parents=True, exist_ok=True)
            return AdapterResult(ok=True, metadata={"returncode": 0, "stdout": ""})
        if command[:3] == ["rm", "-rf", "--"]:
            for raw_path in command[3:]:
                path = Path(raw_path)
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink(missing_ok=True)
            return AdapterResult(ok=True, metadata={"returncode": 0, "stdout": ""})
        if "--clock-echo" in command:
            if not self.clock_echoes:
                raise AssertionError("clock echo sequence exhausted")
            return AdapterResult(
                ok=True,
                metadata={"returncode": 0, "stdout": self.clock_echoes.pop(0)},
            )
        if "--task" in command:
            artifacts_dir = Path(command[command.index("--artifacts") + 1])
            task_path = Path(command[command.index("--task") + 1])
            task = json.loads(task_path.read_text(encoding="utf-8"))
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            (artifacts_dir / "worker.log").write_text("fake worker\n", encoding="utf-8")
            (artifacts_dir / "status.json").write_text(
                json.dumps(
                    {
                        "protocol_version": 1,
                        "task_id": task["task_id"],
                        "task_type": task["task_type"],
                        "operation": task["operation"],
                        "node_role": task["node_role"],
                        "status": "unsupported",
                        "failure_reason": "unsupported_workload",
                        "message": "fake unsupported",
                        "started_at_s": 1.0,
                        "ended_at_s": 2.0,
                        "monotonic_started_s": 3.0,
                        "monotonic_ended_s": 4.0,
                        "artifacts": {
                            "status_json": "status.json",
                            "worker_log": "worker.log",
                        },
                        "metadata": {},
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            return AdapterResult(ok=False, failure_reason=FailureReason.UNKNOWN_ERROR)
        raise AssertionError("unexpected command %r" % (command,))

    def put_file(self, source, destination, *, timeout_s=None):
        Path(destination).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        self.put_destinations.append(destination)
        if destination.endswith(".json"):
            self.put_json_payloads.append(json.loads(Path(source).read_text(encoding="utf-8")))
        return AdapterResult(ok=True)

    def collect(self, source, destination, *, timeout_s=None):
        self.collect_sources.append(source)
        shutil.copytree(source, destination)
        return AdapterResult(ok=True)

    def record_clock_alignment(self, alignment):
        self.clock_alignment = dict(alignment)


def worker_task_base() -> dict:
    return {
        "protocol_version": 1,
        "task_id": "task-edge",
        "run_id": "run-edge",
        "task_type": "telemetry",
        "operation": "not_real",
        "node_role": None,
        "paths": {"state_dir": "/tmp/jw-state"},
        "telemetry": {
            "backend": "nvidia_smi",
            "interval_ms": 100,
            "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
            "rail_manifest": ["gpu_board"],
        },
    }


def write_worker_task(root: Path, payload: Any) -> Path:
    path = root / "task.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def read_status(artifacts_dir: Path) -> dict:
    return json.loads((artifacts_dir / "status.json").read_text(encoding="utf-8"))


class ProtocolShapeAmplificationTests(unittest.TestCase):
    def test_ssh_and_scp_argv_are_literal_protocol_pins(self) -> None:
        runner = CapturingRunner()
        transport = SshTransport(
            SequencedClock([]), "-gpu alias with spaces", runner=runner, command_timeout_s=12, file_timeout_s=13
        )

        transport.run(["python3", "/tmp/joulewise/node_worker.py", "--clock-echo"], timeout_s=9)
        transport.put_file("/local/task.json", "/remote/run/tasks/task.json", timeout_s=8)
        transport.collect("/remote/run/artifacts/task", "/local/artifacts/task", timeout_s=7)

        expected = [
            (
                [
                    "ssh",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=10",
                    "--",
                    "-gpu alias with spaces",
                    "python3",
                    "/tmp/joulewise/node_worker.py",
                    "--clock-echo",
                ],
                9,
            ),
            (
                [
                    "scp",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=10",
                    "--",
                    "/local/task.json",
                    "-gpu alias with spaces:/remote/run/tasks/task.json",
                ],
                8,
            ),
            (
                [
                    "scp",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=10",
                    "-r",
                    "--",
                    "-gpu alias with spaces:/remote/run/artifacts/task",
                    "/local/artifacts/task",
                ],
                7,
            ),
        ]
        self.assertEqual(runner.calls, expected)

    def test_same_client_same_task_id_different_run_ids_get_isolated_remote_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            remote_root = str(Path(tmp) / "remote")
            transport = ProtocolFakeTransport()
            client = NodeWorkerClient(
                transport,
                SequencedClock([10.0, 10.4, 11.0, 11.4, 20.0, 20.2, 21.0, 21.2]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
            )
            task_literal = {
                "task_id": "same-task-id",
                "run_id": "run-alpha",
                "task_type": "telemetry",
                "operation": "future_operation",
                "node_role": None,
                "telemetry": {
                    "backend": "nvidia_smi",
                    "interval_ms": 250,
                    "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
                    "rail_manifest": ["gpu_board"],
                },
            }
            second_task = dict(task_literal)
            second_task["run_id"] = "run-beta"

            first = client.run_task(task_literal, timeout_s=30.0)
            second = client.run_task(second_task, timeout_s=45.0)

            self.assertEqual(first.failure_reason, FailureReason.UNSUPPORTED_WORKLOAD)
            self.assertEqual(second.failure_reason, FailureReason.UNSUPPORTED_WORKLOAD)
            self.assertEqual(
                transport.put_destinations,
                [
                    remote_root + "/node_worker.py",
                    remote_root + "/run-alpha/tasks/same-task-id.json",
                    remote_root + "/run-beta/tasks/same-task-id.json",
                ],
            )
            self.assertEqual(
                transport.collect_sources,
                [
                    remote_root + "/run-alpha/artifacts/same-task-id",
                    remote_root + "/run-beta/artifacts/same-task-id",
                ],
            )
            expected_first_json = {
                "protocol_version": 1,
                "task_id": "same-task-id",
                "run_id": "run-alpha",
                "task_type": "telemetry",
                "operation": "future_operation",
                "node_role": None,
                "timeout_s": 30.0,
                "paths": {"state_dir": remote_root + "/run-alpha/state"},
                "telemetry": {
                    "backend": "nvidia_smi",
                    "interval_ms": 250,
                    "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
                    "rail_manifest": ["gpu_board"],
                },
            }
            expected_second_json = dict(expected_first_json)
            expected_second_json["run_id"] = "run-beta"
            expected_second_json["timeout_s"] = 45.0
            expected_second_json["paths"] = {"state_dir": remote_root + "/run-beta/state"}
            self.assertEqual(transport.put_json_payloads, [expected_first_json, expected_second_json])

    def test_status_json_has_exact_documented_top_level_shape_on_validation_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifacts_dir = root / "artifacts"
            task = worker_task_base()
            del task["paths"]
            code = node_worker.main(["--task", str(write_worker_task(root, task)), "--artifacts", str(artifacts_dir)])

            self.assertEqual(code, 1)
            status = read_status(artifacts_dir)
            self.assertEqual(
                set(status.keys()),
                {
                    "protocol_version",
                    "task_id",
                    "task_type",
                    "operation",
                    "node_role",
                    "status",
                    "failure_reason",
                    "message",
                    "started_at_s",
                    "ended_at_s",
                    "monotonic_started_s",
                    "monotonic_ended_s",
                    "artifacts",
                    "metadata",
                },
            )
            self.assertEqual(status["protocol_version"], 1)
            self.assertEqual(status["task_id"], "task-edge")
            self.assertEqual(status["status"], "failed")
            self.assertEqual(status["failure_reason"], "unknown_error")
            self.assertEqual(
                status["artifacts"],
                {"status_json": "status.json", "worker_log": "worker.log"},
            )


class WorkerAdversarialInputTests(unittest.TestCase):
    def test_malformed_task_json_variants_are_failed_unknown_error(self) -> None:
        cases = [
            ("top-level-list", []),
            ("missing-state-dir", {k: v for k, v in worker_task_base().items() if k != "paths"}),
            (
                "ambiguous-blocks",
                {
                    **worker_task_base(),
                    "runtime": {"backend": "vllm"},
                },
            ),
            (
                "runtime-run-with-runtime-block",
                {
                    **worker_task_base(),
                    "task_type": "runtime",
                    "operation": "run_workload",
                    "runtime": {"backend": "vllm"},
                },
            ),
            (
                "telemetry-with-workload-block",
                {
                    **{k: v for k, v in worker_task_base().items() if k != "telemetry"},
                    "operation": "measure_idle",
                    "workload": {"prompt_text": "x"},
                },
            ),
        ]
        for name, payload in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    artifacts_dir = root / "artifacts"
                    code = node_worker.main(
                        ["--task", str(write_worker_task(root, payload)), "--artifacts", str(artifacts_dir)]
                    )

                    status = read_status(artifacts_dir)
                    self.assertEqual(code, 1)
                    self.assertEqual(status["status"], "failed")
                    self.assertEqual(status["failure_reason"], "unknown_error")

    def test_unknown_future_task_type_remains_unsupported_not_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifacts_dir = root / "artifacts"
            task = worker_task_base()
            task["task_type"] = "transfer-send"
            task["operation"] = "stage_payload"

            code = node_worker.main(["--task", str(write_worker_task(root, task)), "--artifacts", str(artifacts_dir)])

            status = read_status(artifacts_dir)
            self.assertEqual(code, 1)
            self.assertEqual(status["status"], "unsupported")
            self.assertEqual(status["failure_reason"], "unsupported_workload")
            self.assertEqual(status["task_type"], "transfer-send")

    def test_existing_artifacts_directory_is_reused_without_dropping_unrelated_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifacts_dir = root / "artifacts"
            artifacts_dir.mkdir()
            (artifacts_dir / "preexisting.txt").write_text("keep me\n", encoding="utf-8")

            code = node_worker.main(
                ["--task", str(write_worker_task(root, worker_task_base())), "--artifacts", str(artifacts_dir)]
            )

            self.assertEqual(code, 1)
            self.assertEqual((artifacts_dir / "preexisting.txt").read_text(encoding="utf-8"), "keep me\n")
            self.assertTrue((artifacts_dir / "status.json").exists())
            self.assertTrue((artifacts_dir / "worker.log").exists())


class ClockMathAmplificationTests(unittest.TestCase):
    def test_bound_formula_handles_extreme_skew_and_negative_offsets(self) -> None:
        pre = ClockMarker(
            controller_before_s=1_000_000.0,
            node_time_s=999_000.25,
            node_monotonic_s=10.0,
            controller_after_s=1_000_000.50,
            offset_estimate_s=-1000.0,
            rtt_bound_s=0.25,
        )
        post = ClockMarker(
            controller_before_s=1_000_010.0,
            node_time_s=998_509.25,
            node_monotonic_s=20.0,
            controller_after_s=1_000_012.0,
            offset_estimate_s=-1501.0,
            rtt_bound_s=1.0,
        )

        self.assertEqual(compute_stage_bound(pre, post), 502.0)
        self.assertEqual(max(pre.rtt_bound_s, post.rtt_bound_s), 1.0)
        self.assertEqual(abs(post.offset_estimate_s - pre.offset_estimate_s), 501.0)

    def test_client_alignment_record_rederives_controller_timestamp_from_raw_node_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            remote_root = str(Path(tmp) / "remote")
            transport = ProtocolFakeTransport()
            client = NodeWorkerClient(
                transport,
                SequencedClock([10.0, 10.4, 11.0, 11.4]),
                remote_work_root=remote_root,
                remote_python=sys.executable,
            )

            result = client.run_task(
                {
                    "task_id": "clock-task",
                    "run_id": "clock-run",
                    "task_type": "telemetry",
                    "operation": "future_operation",
                    "node_role": None,
                    "telemetry": {"backend": "nvidia_smi"},
                },
                timeout_s=30.0,
            )

            alignment = result.metadata["clock_alignment"]
            self.assertEqual(alignment["method"], "node_worker_clock_echo")
            self.assertEqual(alignment["stage"], "telemetry.future_operation")
            self.assertAlmostEqual(alignment["offset_estimate_s"], 990.3)
            self.assertAlmostEqual(alignment["offset_bound_s"], 1.2)
            raw_node_timestamp_s = 1001.3
            self.assertAlmostEqual(raw_node_timestamp_s - alignment["offset_estimate_s"], 11.0)
            self.assertEqual(transport.clock_alignment, alignment)


class FailureTaxonomyAmplificationTests(unittest.TestCase):
    def test_ssh_auth_failure_is_transport_unavailable_not_permission_denied(self) -> None:
        runner = CapturingRunner(
            RunnerCompleted(returncode=255, stderr=b"Permission denied (publickey).\n")
        )
        result = SshTransport(SequencedClock([]), "node-alias", runner=runner).run(["true"])

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_reason, FailureReason.TRANSPORT_UNAVAILABLE)
        self.assertNotEqual(result.failure_reason, FailureReason.PERMISSION_DENIED)
        self.assertEqual(result.metadata["ssh_error_class"], "ssh_transport")

    def test_all_na_nvidia_smi_start_is_unsupported_telemetry_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            fake = bin_dir / "nvidia-smi"
            fake.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env python3",
                        "print('2026/07/07 12:00:00.000, [N/A], 40', flush=True)",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = os.pathsep.join(
                [str(bin_dir), str(Path(sys.executable).resolve().parent), old_path]
            )
            try:
                task = worker_task_base()
                task["operation"] = "start_sampling"
                task["paths"] = {"state_dir": str(root / "state")}
                artifacts_dir = root / "artifacts"
                code = node_worker.main(
                    ["--task", str(write_worker_task(root, task)), "--artifacts", str(artifacts_dir)]
                )
            finally:
                os.environ["PATH"] = old_path

            status = read_status(artifacts_dir)
            self.assertEqual(code, 1)
            self.assertEqual(status["status"], "unsupported")
            self.assertEqual(status["failure_reason"], "telemetry_unavailable")
            self.assertIn("no numeric power.draw sample", status["message"])
            self.assertNotIn("nvidia-smi unavailable", status["message"])
            self.assertEqual(status["metadata"]["readiness"]["csv_rows_seen"], 1)
            self.assertEqual(status["metadata"]["readiness"]["unsupported_power_rows"], 1)
            self.assertEqual(status["metadata"]["readiness"]["numeric_power_rows"], 0)

    def test_worker_unknown_operation_is_unsupported_workload_while_bad_json_is_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unsupported_dir = root / "unsupported"
            failed_dir = root / "failed"

            unsupported_code = node_worker.main(
                ["--task", str(write_worker_task(root, worker_task_base())), "--artifacts", str(unsupported_dir)]
            )
            bad_json_path = root / "bad.json"
            bad_json_path.write_text("{", encoding="utf-8")
            failed_code = node_worker.main(["--task", str(bad_json_path), "--artifacts", str(failed_dir)])

            unsupported = read_status(unsupported_dir)
            failed = read_status(failed_dir)
            self.assertEqual(unsupported_code, 1)
            self.assertEqual(unsupported["status"], "unsupported")
            self.assertEqual(unsupported["failure_reason"], "unsupported_workload")
            self.assertEqual(failed_code, 1)
            self.assertEqual(failed["status"], "failed")
            self.assertEqual(failed["failure_reason"], "unknown_error")


class NvidiaSmiParserAmplificationTests(unittest.TestCase):
    def test_tz_offsets_plus_minus_and_dst_ambiguous_wall_stamp_are_explicit(self) -> None:
        plus_rows = parse_nvidia_smi_csv(
            "2026/07/07 12:00:00.000, 10.0, 40\n",
            node_utc_offset_s=5.5 * 3600,
        )
        minus_rows = parse_nvidia_smi_csv(
            "2026/07/07 12:00:00.000, 10.0, 40\n",
            node_utc_offset_s=-7 * 3600,
        )
        self.assertEqual(
            plus_rows[0].node_timestamp_s,
            datetime(2026, 7, 7, 12, 0, tzinfo=timezone(timedelta(hours=5, minutes=30))).timestamp(),
        )
        self.assertEqual(
            minus_rows[0].node_timestamp_s,
            datetime(2026, 7, 7, 12, 0, tzinfo=timezone(timedelta(hours=-7))).timestamp(),
        )

        ambiguous_pdt = parse_nvidia_smi_csv(
            "2026/11/01 01:30:00.000, 10.0, 40\n",
            node_utc_offset_s=-7 * 3600,
        )[0]
        ambiguous_pst = parse_nvidia_smi_csv(
            "2026/11/01 01:30:00.000, 10.0, 40\n",
            node_utc_offset_s=-8 * 3600,
        )[0]
        self.assertEqual(ambiguous_pst.node_timestamp_s - ambiguous_pdt.node_timestamp_s, 3600.0)

    def test_all_na_and_empty_csv_are_empty_captures_not_parse_errors(self) -> None:
        diagnostics = {}
        rows = parse_nvidia_smi_csv(
            "2026/07/07 12:00:00.000, [N/A], [N/A]\n"
            "2026/07/07 12:00:01.000, [Not Supported], [N/A]\n",
            node_utc_offset_s=0.0,
            diagnostics=diagnostics,
        )

        self.assertEqual(rows, [])
        self.assertEqual(diagnostics["timestamp_timezone_source"], "node_utc_offset_s")
        self.assertEqual(diagnostics["truncated_final_rows_skipped"], 0)
        self.assertEqual(parse_nvidia_smi_csv("", node_utc_offset_s=0.0), [])


if __name__ == "__main__":
    unittest.main()
