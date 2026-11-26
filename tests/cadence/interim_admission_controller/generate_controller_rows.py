"""Generate the pinned controller's own journal rows with its mock backends and a fake clock.

    python3 -I -B generate_controller_rows.py PIN PINNED_SOURCE_TREE OUT_DIR MOCK_CONFIG.json

Three journals, each written by the pinned ``joulewise.controller`` and ``joulewise.bundle`` serializers:

* ``complete``: ``run_benchmark`` on the tree's example mock config, start to ``run_finalized``;
* ``failed``: the same run with the runtime adapter's ``run_workload`` raising inside the measured window, so the failure
  path writes its ``failure`` row, its closing sampling marker and ``run_finalized``;
* ``timing``: the rows ``_Execution._buffer_timing_boundary`` buffers for a ``timing_receipts.Writer`` set up as the
  controller sets it up for an ``align_episode`` bundle: a span, a nested span and a span that raises.

Nothing here is a measurement: the mock telemetry and runtime invent every value, and the clock is the fake one.
"""
import gzip
import json
from pathlib import Path
import sys
import tempfile

pin, src, out, example = sys.argv[1:]
root = Path(src).resolve()
sys.path.insert(0, str(root))
from joulewise import timing_receipts  # noqa: E402
from joulewise.bundle import RunBundleWriter  # noqa: E402
from joulewise.clock import FakeClock  # noqa: E402
from joulewise.controller import _Execution, run_benchmark  # noqa: E402
from joulewise.schemas import BenchmarkConfig  # noqa: E402

CONFIG = Path(example)          # the pinned revision's configs/examples/mock_local.json


def config(run_id):
    data = json.loads(CONFIG.read_text())
    data["run_id"] = run_id
    return BenchmarkConfig.from_mapping(data)


def rows(bundle):
    return [json.loads(line) for line in (Path(bundle) / "events.jsonl").read_bytes().splitlines()]


docs = {}
with tempfile.TemporaryDirectory() as tmp:
    bundle, _ = run_benchmark(config("generated-complete"), Path(tmp) / "a", FakeClock(start=1_700_000_000.0))
    docs["complete"] = rows(bundle)

    import joulewise.adapters.mock_runtime as mock_runtime
    original = mock_runtime.MockRuntimeAdapter.run_workload

    def failing(self, *args, **kwargs):
        raise RuntimeError("generated runtime failure")
    mock_runtime.MockRuntimeAdapter.run_workload = failing
    try:
        bundle, _ = run_benchmark(config("generated-failed"), Path(tmp) / "b", FakeClock(start=1_700_000_000.0))
    finally:
        mock_runtime.MockRuntimeAdapter.run_workload = original
    docs["failed"] = rows(bundle)

    clock = FakeClock(start=1_700_000_000.0)
    directory = Path(tmp) / "c"
    directory.mkdir()
    execution = object.__new__(_Execution)
    execution._events = []
    info = clock.stamp()
    writer = timing_receipts.Writer(
        execution._buffer_timing_boundary, producer="bundle", member="generated-timing", plan_id=None,
        boot_session_id=None, stamp=lambda: timing_receipts.clock_stamp(clock), clock_domain="synthetic-controller",
        wall_resolution_s=info.wall_resolution_s, monotonic_resolution_s=info.monotonic_resolution_s)
    with timing_receipts.bind(writer):
        with timing_receipts.span("prepare", "generated_outer", requested_s=1.5, stage="prepare"):
            clock.sleep(0.25)
            with timing_receipts.span("prepare", "generated_inner"):
                clock.sleep(0.25)
        try:
            with timing_receipts.span("finalize", "bundle_finalize"):
                clock.sleep(0.25)
                raise TimeoutError("generated")
        except TimeoutError:
            pass
    sink = type("Sink", (), {"_path": directory})()
    for event in execution._events:
        RunBundleWriter._append_event_record(sink, event)
    docs["timing"] = rows(directory)

Path(out, f"{pin}-controller-rows.json.gz").write_bytes(
    gzip.compress(json.dumps(docs, sort_keys=True, separators=(",", ":")).encode(), mtime=0))
