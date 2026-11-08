"""Lifecycle hooks for existing collectors; no new sampler or energy reducer.

Invoked only by explicit native CLI flags, on a lead-controlled quiet Mac.
Imports of the collectors are lazy. Each hook owns only the process it starts.
"""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import sys
import time


def _meter_header(process, path, clock, timeout=15.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            with path.open() as stream:
                line = stream.readline()
            if line.endswith("\n"):
                header = json.loads(line)
                if header.get("k") != "h" or header.get("status") != "streaming":
                    raise RuntimeError(f"requested KM003C unavailable: {header.get('reason')}")
                return header
        if process.poll() is not None:
            raise RuntimeError("KM003C monitor exited before its streaming header")
        clock.sleep(0.05)
    raise RuntimeError("KM003C monitor readiness timed out")


def _config():
    from joulewise.schemas import BenchmarkConfig
    return BenchmarkConfig.from_mapping({
        "schema_version": "0.1", "model": {"name": "synthetic-operand-ladder"},
        "quantization": {"name": "none"},
        "hardware_target": {"id": "interp_energy_mac", "transport": "local",
                            "runtime_backend": "mock", "telemetry_backend": "powermetrics"},
        "workload_profile": {"name": "synthetic_matmul", "prompt_tokens": 1, "output_tokens": 1},
        "sampling": {"power_hz": 10.0, "idle_seconds": 15.0},
    })


@contextmanager
def existing_capture(directory: Path, clock, *, powermetrics=False, km003c=False):
    """Bracket one prewarmed geometry/dtype block and retain native evidence.

    The synthetic config only supplies the existing adapter's cadence and
    identity fields; no model runtime/controller or study config is loaded.
    Metadata explicitly says diagnostic, not a validated run bundle.
    """
    directory.mkdir(parents=True, exist_ok=False)
    for child in ("raw", "logs", "outputs"):
        (directory / child).mkdir()
    metadata = {"status": "PROVISIONAL diagnostic capture; not a claim bundle"}
    meter = adapter = context = config = started = None
    try:
        if km003c:
            script = Path(__file__).resolve().parents[2] / "scripts" / "km003c_monitor.py"
            path = directory / "raw" / "km003c.jsonl"
            command = [sys.executable, "-B", str(script), "--out", str(path), "--poll-ms", "200", "--rate", "2"]
            metadata["km003c"] = {"command": command, "raw_artifact": "raw/km003c.jsonl"}
            meter = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            metadata["km003c"]["header"] = _meter_header(meter, path, clock)
        if powermetrics:
            from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
            from joulewise.interfaces import RunContext
            config = _config()
            context = RunContext(config, clock, directory.name, directory,
                                 directory / "raw", directory / "logs", directory / "outputs")
            adapter = PowermetricsTelemetryAdapter(clock)
            ready = adapter.start_sampling(config, context)
            metadata["powermetrics"] = {"start": ready.metadata, "ready": ready.ok}
            if not ready.ok:
                raise RuntimeError(f"requested powermetrics unavailable: {ready.message}")
            started = clock.stamp()
        yield metadata
    except BaseException as exc:
        metadata["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        try:
            if adapter is not None:
                try:
                    if started is not None:
                        stopped = adapter.stop_sampling_with_evidence(
                            config, context, sampling_started=started, sampling_stopped=clock.stamp())
                        metadata["powermetrics"].update(sample_count=len(stopped.samples),
                                                        clock_evidence=stopped.uncertainty_evidence)
                    else:
                        metadata["powermetrics_salvage"] = adapter.salvage_custody(context)
                except BaseException as exc:
                    metadata["powermetrics_stop_error"] = f"{type(exc).__name__}: {exc}"
                    raise
        finally:
            try:
                if meter is not None:
                    if meter.poll() is None:
                        meter.terminate()
                    else:
                        metadata["km003c"]["exited_before_stop"] = True
                    try:
                        metadata["km003c"]["returncode"] = meter.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        # Only this hook's child, never an existing capture.
                        meter.kill()
                        meter.wait(timeout=5)
                        metadata["km003c"]["forced_stop"] = True
            finally:
                (directory / "capture.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
