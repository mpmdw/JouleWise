from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

import joulewise.adapters as adapters
from joulewise.adapters.node_client import NodeWorkerClient
from joulewise.adapters.nvidia_smi import parse_nvidia_smi_csv
from joulewise.clock import Clock
from joulewise.cli import validate_bundle
from joulewise.controller import run_benchmark, run_experiment
from joulewise.interfaces import AdapterResult
from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "configs" / "examples" / "nvidia_vllm_ssh.json"
PROMPT_TOKEN_DOMAIN = "joulewise.prompt_token_ids.v1"
NODE_UTC_OFFSET_S = -28800


class AutoClock:
    def __init__(self, start: float = 1_700_000_000.0, step: float = 0.1) -> None:
        self._now = float(start)
        self._step = float(step)
        self.last_value = float(start)

    def now(self) -> float:
        value = self._now
        self.last_value = value
        self._now += self._step
        return value

    def sleep(self, seconds: float) -> None:
        self._now += seconds

    def info(self) -> dict[str, Any]:
        return {"kind": "auto-test", "step_s": self._step}


def load_config(run_id: str, *, host: str = "fake-nvidia-node") -> BenchmarkConfig:
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    payload["run_id"] = run_id
    payload["hardware_target"]["host"] = host
    return BenchmarkConfig.from_mapping(payload)


def load_generated_config(*, host: str = "fake-nvidia-node") -> BenchmarkConfig:
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    payload.pop("run_id", None)
    payload["hardware_target"]["host"] = host
    return BenchmarkConfig.from_mapping(payload)


def _csv_timestamp(epoch_s: float) -> str:
    tz = timezone(timedelta(seconds=NODE_UTC_OFFSET_S))
    return datetime.fromtimestamp(epoch_s, tz=tz).strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]


def expected_prompt_token_hash(token_ids: list[int]) -> str:
    canonical = json.dumps(token_ids, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256((PROMPT_TOKEN_DOMAIN + "\0" + canonical).encode("utf-8")).hexdigest()


class StubNode:
    def __init__(self, *, mode: str = "success", offset_s: float = 10.0) -> None:
        self.mode = mode
        self.offset_s = offset_s
        self.remote_files: dict[str, bytes] = {}
        self.remote_artifacts: dict[str, Path] = {}
        self.tmp = tempfile.TemporaryDirectory()
        self.add_cleanup: Any = None
        self.stop_csv_text = ""
        self.runtime_events_text = ""
        self.runtime_tokens_text = ""
        self.power_sample_controller_times: list[float] = []
        self.task_run_ids: list[str] = []
        self.task_paths: list[str] = []
        self.artifact_paths: list[str] = []

    def cleanup(self) -> None:
        self.tmp.cleanup()

    def marker_stdout(self, clock: AutoClock) -> str:
        return json.dumps(
            {
                "node_time_s": clock.last_value + self.offset_s,
                "monotonic_s": clock.last_value / 2.0,
            },
            sort_keys=True,
        ) + "\n"

    def put_file(self, source: str, destination: str) -> None:
        self.remote_files[destination] = Path(source).read_bytes()

    def run_task(self, task_path: str, artifacts_path: str, clock: AutoClock) -> int:
        task = json.loads(self.remote_files[task_path].decode("utf-8"))
        self.task_run_ids.append(task["run_id"])
        self.task_paths.append(task_path)
        self.artifact_paths.append(artifacts_path)
        local_dir = Path(self.tmp.name) / artifacts_path.strip("/").replace("/", "__")
        if local_dir.exists():
            shutil.rmtree(local_dir)
        local_dir.mkdir(parents=True)
        self.remote_artifacts[artifacts_path] = local_dir
        (local_dir / "worker.log").write_text(
            "%s/%s\n" % (task["task_type"], task["operation"]),
            encoding="utf-8",
        )

        if self.mode == "missing_vllm" and task["task_type"] == "runtime":
            if task["operation"] == "prepare":
                self._write_status(
                    local_dir,
                    task,
                    "unsupported",
                    FailureReason.RUNTIME_UNAVAILABLE,
                    "vLLM launcher unavailable: vllm not found",
                )
                return 1
        if self.mode == "missing_nvidia_smi" and task["task_type"] == "telemetry":
            if task["operation"] in {"measure_idle", "start_sampling"}:
                self._write_status(
                    local_dir,
                    task,
                    "unsupported",
                    FailureReason.TELEMETRY_UNAVAILABLE,
                    "nvidia-smi unavailable: nvidia-smi not found",
                )
                return 1

        if task["task_type"] == "runtime":
            return self._runtime_task(local_dir, task, clock)
        if task["task_type"] == "telemetry":
            return self._telemetry_task(local_dir, task, clock)
        self._write_status(
            local_dir,
            task,
            "unsupported",
            FailureReason.UNSUPPORTED_WORKLOAD,
            "unsupported task",
        )
        return 1

    def _runtime_task(self, local_dir: Path, task: dict[str, Any], clock: AutoClock) -> int:
        operation = task["operation"]
        artifacts: dict[str, str] = {}
        if operation == "cleanup" and self.mode == "runtime_cleanup_survives":
            self._write_status(
                local_dir,
                task,
                "failed",
                FailureReason.CLEANUP_FAILED,
                "vLLM server process survived cleanup",
                metadata={"pid": 4242, "process_survived": True},
            )
            return 1
        if operation == "run_workload":
            base = clock.last_value - 0.05
            self.power_sample_controller_times = [base + 0.05, base + 0.15, base + 0.25]
            event_rows = [
                {
                    "timestamp_s": base + self.offset_s,
                    "event_type": "phase_start",
                    "phase": "prefill",
                    "message": "start",
                    "metadata": {},
                },
                {
                    "timestamp_s": base + 0.05 + self.offset_s,
                    "event_type": "phase_end",
                    "phase": "prefill",
                    "message": "prefill done",
                    "metadata": {},
                },
                {
                    "timestamp_s": base + 0.10 + self.offset_s,
                    "event_type": "phase_start",
                    "phase": "decode",
                    "message": "decode start",
                    "metadata": {},
                },
                {
                    "timestamp_s": base + 0.35 + self.offset_s,
                    "event_type": "phase_end",
                    "phase": "decode",
                    "message": "decode done",
                    "metadata": {"emitted_tokens": 3},
                },
            ]
            token_rows = [
                {"timestamp_s": base + 0.15 + self.offset_s, "index": 0, "text": "A"},
                {"timestamp_s": base + 0.25 + self.offset_s, "index": 1, "text": "B"},
                {"timestamp_s": base + 0.35 + self.offset_s, "index": 2, "text": "C"},
            ]
            self.runtime_events_text = "".join(
                json.dumps(row, sort_keys=True) + "\n" for row in event_rows
            )
            self.runtime_tokens_text = "".join(
                json.dumps(row, sort_keys=True) + "\n" for row in token_rows
            )
            (local_dir / "events.jsonl").write_text(self.runtime_events_text, encoding="utf-8")
            (local_dir / "response.txt").write_text("ABC", encoding="utf-8")
            (local_dir / "tokens.jsonl").write_text(self.runtime_tokens_text, encoding="utf-8")
            artifacts.update(
                {
                    "events_jsonl": "events.jsonl",
                    "response_txt": "response.txt",
                    "tokens_jsonl": "tokens.jsonl",
                }
            )
            workload_metadata: dict[str, Any] = {
                "prompt_token_ids": [701, 702, 703, 704, 705, 706, 707, 708, 709]
            }
            if self.mode == "usage_omitted":
                workload_metadata.update(
                    {
                        "emitted_tokens": 3,
                        "token_count_source": "stream_chunk_fallback",
                    }
                )
            self._write_status(
                local_dir,
                task,
                "succeeded",
                None,
                "ok",
                artifacts,
                metadata=workload_metadata,
            )
            return 0
        self._write_status(local_dir, task, "succeeded", None, "ok", artifacts)
        return 0

    def _telemetry_task(self, local_dir: Path, task: dict[str, Any], clock: AutoClock) -> int:
        operation = task["operation"]
        artifacts: dict[str, str] = {}
        if operation == "measure_idle":
            start = clock.last_value + self.offset_s
            text = self._nvidia_csv([start, start + 0.5, start + 1.0], [8.0, 8.5, 9.0])
            (local_dir / "nvidia_smi_idle.csv").write_text(text, encoding="utf-8")
            artifacts["nvidia_smi_idle_csv"] = "nvidia_smi_idle.csv"
        elif operation == "stop_sampling":
            if self.mode == "sampler_survives":
                self._write_status(
                    local_dir,
                    task,
                    "failed",
                    FailureReason.CLEANUP_FAILED,
                    "nvidia-smi sampler process survived stop_sampling",
                    metadata={
                        "pid": 4343,
                        "process_survived": True,
                        "node_utc_offset_s": NODE_UTC_OFFSET_S,
                    },
                )
                return 1
            controller_times = self.power_sample_controller_times or [
                clock.last_value,
                clock.last_value + 0.1,
                clock.last_value + 0.2,
            ]
            node_times = [value + self.offset_s for value in controller_times]
            self.stop_csv_text = self._nvidia_csv(node_times, [12.0, 13.0, 14.0])
            (local_dir / "nvidia_smi.csv").write_text(self.stop_csv_text, encoding="utf-8")
            artifacts["nvidia_smi_csv"] = "nvidia_smi.csv"
        self._write_status(
            local_dir,
            task,
            "succeeded",
            None,
            "ok",
            artifacts,
            metadata={"node_utc_offset_s": NODE_UTC_OFFSET_S, "node_tzname": "PST"},
        )
        return 0

    def _nvidia_csv(self, timestamps: list[float], powers: list[float]) -> str:
        rows = [
            "%s, %.1f, %d" % (_csv_timestamp(timestamp), power, 40 + index)
            for index, (timestamp, power) in enumerate(zip(timestamps, powers))
        ]
        return "\n".join(rows) + "\n"

    def _write_status(
        self,
        local_dir: Path,
        task: dict[str, Any],
        status: str,
        failure_reason: FailureReason | None,
        message: str,
        artifacts: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        mapped = {
            "status_json": "status.json",
            "worker_log": "worker.log",
        }
        mapped.update(artifacts or {})
        payload = {
            "protocol_version": 1,
            "correlation_token": task["correlation_token"],
            "task_id": task["task_id"],
            "run_id": task["run_id"],
            "task_type": task["task_type"],
            "operation": task["operation"],
            "node_role": task["node_role"],
            "status": status,
            "failure_reason": failure_reason.value if failure_reason else None,
            "message": message,
            "artifacts": mapped,
            "metadata": {"stub_node": self.mode, **(metadata or {})},
        }
        (local_dir / "status.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


class StubSshTransport:
    name = "ssh"

    def __init__(self, clock: Clock, destination: str, *, node: StubNode) -> None:
        self.clock = clock
        self.destination = destination
        self.node = node
        self.clock_alignment: dict[str, Any] | None = None

    def connection_metadata(self, config: BenchmarkConfig, context=None) -> dict[str, Any]:
        return {"transport": "ssh", "host": self.destination}

    def run_command(self, config: BenchmarkConfig, command: list[str], context=None) -> AdapterResult:
        return self.run(command)

    def collect_artifact(
        self, config: BenchmarkConfig, source: str, destination: str, context=None
    ) -> AdapterResult:
        return self.collect(source, destination)

    def run(self, command: list[str], *, timeout_s: float | None = None) -> AdapterResult:
        del timeout_s
        if command[:2] == ["mkdir", "-p"]:
            return AdapterResult(ok=True, metadata={"returncode": 0, "stdout": ""})
        if command[:3] == ["rm", "-rf", "--"]:
            if self.node.mode == "directory_cleanup_failure":
                return AdapterResult(
                    ok=False,
                    failure_reason=FailureReason.UNKNOWN_ERROR,
                    message="injected remote directory cleanup failure",
                )
            for target in command[3:]:
                for path in list(self.node.remote_files):
                    if path == target or path.startswith(target.rstrip("/") + "/"):
                        self.node.remote_files.pop(path, None)
                for path in list(self.node.remote_artifacts):
                    if path == target or path.startswith(target.rstrip("/") + "/"):
                        self.node.remote_artifacts.pop(path, None)
            return AdapterResult(ok=True, metadata={"returncode": 0, "stdout": ""})
        if "--clock-echo" in command:
            assert isinstance(self.clock, AutoClock)
            return AdapterResult(
                ok=True,
                metadata={"returncode": 0, "stdout": self.node.marker_stdout(self.clock)},
            )
        if "--task" in command:
            task_path = command[command.index("--task") + 1]
            artifacts_path = command[command.index("--artifacts") + 1]
            assert isinstance(self.clock, AutoClock)
            returncode = self.node.run_task(task_path, artifacts_path, self.clock)
            return AdapterResult(ok=True, metadata={"returncode": returncode, "stdout": ""})
        return AdapterResult(ok=True, metadata={"returncode": 0, "stdout": ""})

    def put_file(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        del timeout_s
        self.node.put_file(source, destination)
        return AdapterResult(ok=True)

    def collect(
        self, source: str, destination: str, *, timeout_s: float | None = None
    ) -> AdapterResult:
        del timeout_s
        if source not in self.node.remote_artifacts:
            return AdapterResult(
                ok=False,
                failure_reason=FailureReason.TRANSPORT_UNAVAILABLE,
                message="missing fake remote artifact: %s" % source,
            )
        shutil.copytree(self.node.remote_artifacts[source], destination)
        return AdapterResult(ok=True)

    def record_clock_alignment(self, alignment: dict[str, Any]) -> None:
        self.clock_alignment = dict(alignment)


class NvidiaNodeIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.retention_root = Path(tmp.name) / "node-custody"
        self.retention_client_index = 0

        def node_client_factory(*args: Any, **kwargs: Any) -> NodeWorkerClient:
            self.retention_client_index += 1
            return NodeWorkerClient(
                *args,
                retention_root=(
                    self.retention_root
                    / f"client-{self.retention_client_index:03d}"
                ),
                **kwargs,
            )

        client_patch = patch(
            "joulewise.adapters.node_client.NodeWorkerClient",
            new=node_client_factory,
        )
        client_patch.start()
        self.addCleanup(client_patch.stop)

    def run_with_node(self, config: BenchmarkConfig, node: StubNode):
        self.addCleanup(node.cleanup)

        def factory(clock: Clock, destination: str, **kwargs: Any) -> StubSshTransport:
            del kwargs
            return StubSshTransport(clock, destination, node=node)

        with patch("joulewise.adapters.ssh_transport.SshTransport", side_effect=factory):
            return run_benchmark(config, self.runs_root, AutoClock(), environment_snapshot={})

    def test_registry_resolved_vllm_nvidia_smi_controller_e2e(self) -> None:
        node = StubNode()
        bundle_path, summary = self.run_with_node(load_config("nvidia-node-e2e"), node)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertEqual((bundle_path / "outputs" / "response.txt").read_text(), "ABC")
        self.assertEqual(
            (bundle_path / "logs" / "task-runtime-run_workload-003_worker.log").read_text(
                encoding="utf-8"
            ),
            "runtime/run_workload\n",
        )
        self.assertEqual(
            (bundle_path / "logs" / "task-telemetry-stop_sampling-003_worker.log").read_text(
                encoding="utf-8"
            ),
            "telemetry/stop_sampling\n",
        )
        self.assertEqual(
            (bundle_path / "raw" / "nvidia_smi.csv").read_text(encoding="utf-8"),
            node.stop_csv_text,
        )
        self.assertEqual(
            (bundle_path / "raw" / "vllm_events.jsonl").read_text(encoding="utf-8"),
            node.runtime_events_text,
        )
        self.assertEqual(
            (bundle_path / "raw" / "vllm_tokens.jsonl").read_text(encoding="utf-8"),
            node.runtime_tokens_text,
        )

        output_tokens = [
            json.loads(line)
            for line in (bundle_path / "outputs" / "tokens.jsonl").read_text().splitlines()
        ]
        raw_tokens = [json.loads(line) for line in node.runtime_tokens_text.splitlines()]
        self.assertEqual([token["text"] for token in output_tokens], ["A", "B", "C"])
        self.assertLess(output_tokens[0]["timestamp_s"], raw_tokens[0]["timestamp_s"])
        self.assertGreater(raw_tokens[0]["timestamp_s"] - output_tokens[0]["timestamp_s"], 9.0)

        with (bundle_path / "power_trace.csv").open(newline="") as handle:
            trace_rows = list(csv.DictReader(handle))
        self.assertEqual(len(trace_rows), 3)
        self.assertEqual(trace_rows[0]["source"], "nvidia_smi")

        events = [
            json.loads(line)
            for line in (bundle_path / "events.jsonl").read_text().splitlines()
        ]
        self.assertIn(("phase_start", "prefill"), [(e["event_type"], e["phase"]) for e in events])
        metadata = json.loads((bundle_path / "metadata.json").read_text())
        self.assertEqual(validate_bundle(bundle_path, strict=True), [])
        self.assertEqual(
            metadata["workload_provenance"]["prompt"]["realized_token_count"],
            9,
        )
        self.assertEqual(
            metadata["workload_provenance"]["prompt"]["token_ids_sha256"],
            expected_prompt_token_hash([701, 702, 703, 704, 705, 706, 707, 708, 709]),
        )
        self.assertEqual(metadata["workload_provenance"]["generator"]["name"], "vllm_node_worker")
        self.assertEqual(metadata["connection"], {"transport": "ssh", "host": "fake-nvidia-node"})
        self.assertEqual(metadata["adapters"]["runtime"]["name"], "vllm")
        self.assertEqual(metadata["adapters"]["telemetry"]["name"], "nvidia_smi")
        self.assertEqual(
            metadata["adapters"]["telemetry"]["worker_metadata"]["node_utc_offset_s"],
            NODE_UTC_OFFSET_S,
        )
        self.assertEqual(
            metadata["adapters"]["runtime"]["worker_metadata"]["prompt_token_ids"],
            [701, 702, 703, 704, 705, 706, 707, 708, 709],
        )
        runtime_alignments = metadata["adapters"]["runtime"]["clock_alignments"]
        telemetry_alignments = metadata["adapters"]["telemetry"]["clock_alignments"]
        self.assertEqual(
            [alignment["stage"] for alignment in runtime_alignments],
            [
                "runtime.prepare",
                "runtime.warmup",
                "runtime.run_workload",
                "runtime.cleanup",
            ],
        )
        self.assertEqual(
            [alignment["stage"] for alignment in telemetry_alignments],
            ["telemetry.measure_idle", "telemetry.start_sampling", "telemetry.stop_sampling"],
        )
        stop_alignment = next(
            alignment
            for alignment in telemetry_alignments
            if alignment["stage"] == "telemetry.stop_sampling"
        )
        previous_tz = os.environ.get("TZ")
        os.environ["TZ"] = "UTC"
        if hasattr(time, "tzset"):
            time.tzset()
        try:
            raw_rows = parse_nvidia_smi_csv(
                (bundle_path / "raw" / "nvidia_smi.csv").read_text(encoding="utf-8"),
                node_utc_offset_s=metadata["adapters"]["telemetry"]["worker_metadata"][
                    "node_utc_offset_s"
                ],
            )
        finally:
            if previous_tz is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = previous_tz
            if hasattr(time, "tzset"):
                time.tzset()
        self.assertLess(
            float(trace_rows[0]["timestamp_s"]),
            raw_rows[0].node_timestamp_s,
        )
        self.assertGreater(
            raw_rows[0].node_timestamp_s - float(trace_rows[0]["timestamp_s"]),
            9.0,
        )
        rederived = raw_rows[0].node_timestamp_s - stop_alignment["offset_estimate_s"]
        self.assertAlmostEqual(rederived, float(trace_rows[0]["timestamp_s"]))

    def test_generated_run_id_is_used_for_remote_task_isolation(self) -> None:
        node = StubNode()
        bundle_path, summary = self.run_with_node(load_generated_config(), node)

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        generated_run_id = bundle_path.name
        self.assertNotEqual(generated_run_id, "pending-run-id")
        self.assertTrue(generated_run_id)
        self.assertEqual(set(node.task_run_ids), {generated_run_id})
        self.assertTrue(all(f"/{generated_run_id}/tasks/" in path for path in node.task_paths))
        self.assertTrue(all(f"/{generated_run_id}/artifacts/" in path for path in node.artifact_paths))

    def test_registry_node_clients_do_not_share_retention_manifest(self) -> None:
        config = load_config("nvidia-node-retention-isolation")
        node = StubNode()
        self.addCleanup(node.cleanup)

        def factory(clock: Clock, destination: str, **kwargs: Any) -> StubSshTransport:
            del kwargs
            return StubSshTransport(clock, destination, node=node)

        simulated_default = self.runs_root.parent / "simulated-default-custody"
        with (
            patch(
                "joulewise.adapters.node_client.DEFAULT_RETENTION_ROOT",
                simulated_default,
            ),
            patch(
                "joulewise.adapters.ssh_transport.SshTransport",
                side_effect=factory,
            ),
        ):
            runtime, runtime_failure = adapters.resolve_runtime(config, AutoClock())
            telemetry, telemetry_failure = adapters.resolve_telemetry(
                config, AutoClock()
            )

        self.assertIsNone(runtime_failure)
        self.assertIsNone(telemetry_failure)
        self.assertIsNotNone(runtime)
        self.assertIsNotNone(telemetry)
        assert runtime is not None
        assert telemetry is not None
        runtime_client = runtime._client
        telemetry_client = telemetry._client

        token = "retention-isolation-token"
        task_id = "task-retention-isolation"
        run_id = "run-retention-isolation"
        paths = runtime_client._remote_paths_for_run(run_id)
        prepared_task = {
            "correlation_token": token,
            "protocol_version": 1,
            "task_type": "telemetry",
            "operation": "measure_idle",
            "node_role": None,
        }
        record = runtime_client._new_retention_record(
            token=token,
            task_id=task_id,
            run_id=run_id,
            prepared_task=prepared_task,
            paths=paths,
            remote_task_path=runtime_client._contained_remote_path(
                run_id, "tasks", f"{task_id}.json"
            ),
            remote_artifacts_path=runtime_client._contained_remote_path(
                run_id, "artifacts", task_id
            ),
            context=None,
        )
        runtime_client._register_retention(record)

        telemetry_client._sweep_retained_artifacts()
        runtime_client._mark_worker_may_have_run(token)

        self.assertNotEqual(
            runtime_client.retention_root,
            telemetry_client.retention_root,
        )
        for retention_root in (
            runtime_client.retention_root,
            telemetry_client.retention_root,
        ):
            retention_root.relative_to(self.runs_root.parent)
        self.assertIn(
            token,
            {
                item["token"]
                for item in runtime_client._load_retention_records()
            },
        )

    def test_nvidia_smi_raw_tamper_fails_strict_lineage(self) -> None:
        node = StubNode()
        bundle_path, summary = self.run_with_node(
            load_config("nvidia-node-raw-tamper"),
            node,
        )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        tampered = self.runs_root / "nvidia-node-raw-tamper-copy"
        shutil.copytree(bundle_path, tampered)
        raw_path = tampered / "raw" / "nvidia_smi.csv"
        rows = raw_path.read_text(encoding="utf-8").splitlines()
        cells = [cell.strip() for cell in rows[0].split(",")]
        cells[1] = str(float(cells[1]) + 1.0)
        rows[0] = ", ".join(cells)
        raw_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

        problems = validate_bundle(tampered, strict=True)

        raw_problem = next(
            problem for problem in problems if "strict: raw-to-trace:" in problem
        )
        self.assertIn("nvidia_smi", raw_problem)
        self.assertIn("power_w", raw_problem)

    def test_generated_id_multi_rep_experiment_executes_cooldown(self) -> None:
        # NV-2 (ARC-7): a generated-experiment-id config has run_id == None,
        # and the D-014 cooldown gate calls measure_idle with no RunContext.
        # Before the fix nvidia_smi's run-id requirement raised AdapterFailure
        # and every cooldown was silently recorded as "skipped". The gate must
        # EXECUTE (result in the executed vocabulary) and record the
        # cooldown-scoped run id it used for node-side task isolation.
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload.pop("run_id", None)
        payload["hardware_target"]["host"] = "fake-nvidia-node"
        payload["workload_profile"]["repetitions"] = 2
        config = BenchmarkConfig.from_mapping(payload)

        node = StubNode()
        self.addCleanup(node.cleanup)

        def factory(clock: Clock, destination: str, **kwargs: Any) -> StubSshTransport:
            del kwargs
            return StubSshTransport(clock, destination, node=node)

        with patch("joulewise.adapters.ssh_transport.SshTransport", side_effect=factory):
            manifest_path, results = run_experiment(config, self.runs_root, AutoClock())

        self.assertEqual(
            [summary.status for _, summary in results],
            [RunStatus.SUCCEEDED, RunStatus.SUCCEEDED],
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        cooldown = manifest["cooldown"]
        self.assertEqual(len(cooldown), 1)
        note = cooldown[0]
        self.assertIn(note["result"], {"recovered", "cap_hit"})
        expected_cooldown_run_id = (
            f"{manifest['experiment_id']}-cooldown-{note['after_member']}"
        )
        self.assertEqual(note["cooldown_run_id"], expected_cooldown_run_id)
        # The node actually received tasks under the cooldown-scoped id, so
        # the manifest is auditable against node-side artifacts.
        self.assertIn(expected_cooldown_run_id, node.task_run_ids)

    def test_missing_vllm_launcher_surfaces_structured_unsupported(self) -> None:
        bundle_path, summary = self.run_with_node(
            load_config("nvidia-node-missing-vllm"),
            StubNode(mode="missing_vllm"),
        )

        self.assertEqual(summary.status, RunStatus.UNSUPPORTED)
        self.assertEqual(summary.failure_reason, FailureReason.RUNTIME_UNAVAILABLE)
        self.assertIn("vLLM launcher unavailable", summary.failure_message)
        self.assertFalse((bundle_path / "power_trace.csv").exists())

    def test_missing_nvidia_smi_surfaces_structured_unsupported(self) -> None:
        bundle_path, summary = self.run_with_node(
            load_config("nvidia-node-missing-nvidia-smi"),
            StubNode(mode="missing_nvidia_smi"),
        )

        self.assertEqual(summary.status, RunStatus.UNSUPPORTED)
        self.assertEqual(summary.failure_reason, FailureReason.TELEMETRY_UNAVAILABLE)
        self.assertIn("nvidia-smi unavailable", summary.failure_message)
        self.assertFalse((bundle_path / "power_trace.csv").exists())

    def test_surviving_runtime_process_demotes_run_to_cleanup_failed(self) -> None:
        bundle_path, summary = self.run_with_node(
            load_config("nvidia-node-runtime-cleanup-survives"),
            StubNode(mode="runtime_cleanup_survives"),
        )

        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.CLEANUP_FAILED)
        self.assertIn("survived cleanup", summary.failure_message)
        metadata = json.loads((bundle_path / "metadata.json").read_text(encoding="utf-8"))
        self.assertTrue(
            metadata["adapters"]["runtime"]["cleanup_metadata"]["worker_metadata"][
                "process_survived"
            ]
        )

    def test_surviving_sampler_process_demotes_run_to_cleanup_failed(self) -> None:
        _, summary = self.run_with_node(
            load_config("nvidia-node-sampler-survives"),
            StubNode(mode="sampler_survives"),
        )

        self.assertEqual(summary.status, RunStatus.FAILED)
        self.assertEqual(summary.failure_reason, FailureReason.CLEANUP_FAILED)
        self.assertIn("sampler process survived", summary.failure_message)

    def test_usage_omission_propagates_null_metrics_and_per_token_ineligibility(self) -> None:
        _, summary = self.run_with_node(
            load_config("nvidia-node-usage-omitted"),
            StubNode(mode="usage_omitted"),
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNone(summary.energy_token_j)
        self.assertIsNone(summary.energy_output_token_j)
        self.assertIsNone(summary.throughput_tokens_s)
        self.assertEqual(
            summary.measurement_quality.token_count_source,
            "stream_chunk_fallback",
        )
        self.assertEqual(
            summary.window_evidence_precheck["per_token"],
            {
                "eligible": False,
                "reasons": ["token_count_stream_chunk_fallback"],
                "token_count_source": "stream_chunk_fallback",
            },
        )

    def test_directory_cleanup_failure_is_quality_only(self) -> None:
        bundle_path, summary = self.run_with_node(
            load_config("nvidia-node-directory-cleanup-fails"),
            StubNode(mode="directory_cleanup_failure"),
        )

        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertIsNotNone(summary.measurement_quality.remote_cleanup_failed)
        self.assertTrue(summary.measurement_quality.remote_cleanup_failed)
        metadata = json.loads((bundle_path / "metadata.json").read_text(encoding="utf-8"))
        report = metadata["extra"]["node_cleanup"]
        self.assertTrue(any(item["removed"] is False for item in report))
        self.assertTrue(
            all(item["scope"] in {"local", "remote"} for item in report)
        )

    def test_example_config_validates_and_resolves_through_registry(self) -> None:
        config = BenchmarkConfig.from_mapping(json.loads(EXAMPLE.read_text(encoding="utf-8")))
        clock = AutoClock()
        node = StubNode()
        self.addCleanup(node.cleanup)

        with patch(
            "joulewise.adapters.ssh_transport.SshTransport",
            side_effect=lambda clock, destination, **kwargs: StubSshTransport(
                clock, destination, node=node
            ),
        ):
            transport, transport_failure = adapters.resolve_transport(config)
            runtime, runtime_failure = adapters.resolve_runtime(config, clock)
            telemetry, telemetry_failure = adapters.resolve_telemetry(config, clock)

        self.assertIsNone(transport_failure)
        self.assertIsNone(runtime_failure)
        self.assertIsNone(telemetry_failure)
        self.assertEqual(transport.name, "ssh")
        self.assertEqual(runtime.name, "vllm")
        self.assertEqual(telemetry.name, "nvidia_smi")


if __name__ == "__main__":
    unittest.main()
