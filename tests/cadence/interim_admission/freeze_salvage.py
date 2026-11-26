"""Construct the operational files on the failed-episode salvage path, using pinned writers.

Usage: freeze_salvage.py PIN SOURCE_TREE CORPUS_DIR
The input journal uses the matching pin's endpoint-error profile. No hardware is used.
"""
from pathlib import Path
from types import SimpleNamespace
import gzip
import json
import sys
import tempfile

pin, source, corpus = sys.argv[1:]
sys.path.insert(0, str(Path(source).resolve()))
from joulewise.align.apple.workload import EpisodeRuntimeAdapter
from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.controller import _Execution
from joulewise.interfaces import RuntimeEvent, RuntimeResult
from joulewise.schemas import BenchmarkConfig, FailureReason

directory = Path(corpus)
docs = json.loads(gzip.decompress((directory / f"{pin}-endpoint-error.json.gz").read_bytes()))
episode_events = [RuntimeEvent(**r) for r in docs["events.jsonl"]]
adapter = object.__new__(EpisodeRuntimeAdapter)
adapter._failed_episode_result = RuntimeResult(
    events=episode_events, output_artifacts={}, output_token_count=0, token_count=0,
    workload_provenance={"episode_outcome": {"stop_condition": "endpoint_error"}},
)
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    outputs = root / "outputs"
    outputs.mkdir()
    acknowledged = []
    context = SimpleNamespace(outputs_dir=outputs, acknowledge_custody=lambda token, paths: acknowledged.append((token, paths)))
    adapter.salvage_custody(context)
    salvage = outputs / "align_runtime_events.jsonl"
    assert len(acknowledged) == 1 and salvage in acknowledged[0][1]
    docs["outputs/align_runtime_events.jsonl"] = [json.loads(line) for line in salvage.read_bytes().splitlines()]

    # Exercise the controller's lifecycle record producers and the terminal bundle serializer.
    clock = FakeClock(episode_events[0].timestamp_s - 1)
    run = object.__new__(_Execution)
    run._clock, run._events = clock, []
    run._config = BenchmarkConfig.from_mapping(docs["config.json"])
    run._battery_monotonic_ns = lambda: round(clock.now() * 10**9)
    run_id = run._config.run_id
    run._buffer_event("run_started", "run", f"run {run_id} started", {"run_id": run_id})
    for name in ("validate", "prepare", "idle_baseline", "warmup"):
        run._begin_stage(name)
        clock.sleep(0.01)
        run._complete_stage(name)
    run._begin_stage("measured_run")
    clock.sleep(episode_events[-1].timestamp_s - clock.now() + 0.1)
    run._buffer_event("failure", "measured_run", "endpoint_error: synthetic stream exception",
                      {"failure_reason": FailureReason.UNKNOWN_ERROR.value})
    writer = object.__new__(RunBundleWriter)
    writer._path, writer._clock, writer._closed = root, clock, False
    writer._staged_summary = {"synthetic": True}
    for event in run._events:
        writer.append_event(event)
    writer.finalize()
    docs["events.jsonl"] = [json.loads(line) for line in (root / "events.jsonl").read_bytes().splitlines()]
    assert docs["events.jsonl"][-1]["event_type"] == "run_finalized"

payload = json.dumps(docs, separators=(",", ":"), sort_keys=True, allow_nan=False).encode()
(directory / f"{pin}-salvaged-failure.json.gz").write_bytes(gzip.compress(payload, mtime=0))
