#!/usr/bin/env python3
"""Profile ONLY newly generated synthetic BYTES archives (no archive argument)."""
import argparse
import cProfile
from contextlib import nullcontext
import inspect
import io
import json
from pathlib import Path
import pstats
import statistics
import subprocess
import sys
import tempfile
from threading import Lock
import time
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6 import export_runs
from tests.b6.export_profile_support import fixture, serial_exporter, SERIAL_EXPORT_COMMIT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compressed", action="store_true")
    parser.add_argument("--workers", type=int, choices=range(1, 9), default=1)
    parser.add_argument("--references", type=int, default=16)
    parser.add_argument("--science", type=int, default=7)
    parser.add_argument("--blob-mib", type=int, default=2)
    parser.add_argument("--samples", type=int, default=2048)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--interval-trace", action="store_true")
    parser.add_argument("--compare-serial", action="store_true",
                        help="time and byte-compare the pinned pre-optimization exporter on the SAME inputs")
    args = parser.parse_args()
    if min(args.references, args.samples) < 2 or args.science < 7 or args.blob_mib < 0 or args.repeats < 1:
        parser.error("references/samples >= 2, science >= 7, blob-mib >= 0, repeats >= 1 required")
    # This tiny generated fixture uses the same disk-space seam as restore
    # tests. Keep production's 40 GiB reserve untouched on this shared host.
    if args.references * args.blob_mib > 256:
        parser.error("synthetic raw payload must be <= 256 MiB")
    with (serial_exporter() if args.compare_serial else nullcontext(None)) as serial, \
            tempfile.TemporaryDirectory(prefix="bytes-export-synthetic-") as temporary, patch(
            "joulewise.desk_restore.shutil.disk_usage",
            return_value=SimpleNamespace(free=100 * 1024**3)):
        root = Path(temporary)
        archive, registration, plan, pack = fixture(root, references=args.references, science=args.science,
            blob_bytes=args.blob_mib * 1024**2, samples=args.samples, compressed=args.compressed,
            interval_trace=args.interval_trace)
        kwargs = {"pack_registration": pack}
        if "read_workers" in inspect.signature(export_runs.export).parameters:
            kwargs["read_workers"] = args.workers
        elif args.workers != 1:
            parser.error("this revision has only the serial exporter")
        def run():
            return export_runs.export(archive, plan, registration, root / "packs", root / "out", **kwargs)
        def reference():
            return serial.export(archive, plan, registration, root / "packs", root / "out", pack_registration=pack)
        # Separate first-time key creation from repeated export timings. All
        # timing comparisons reuse these exact synthetic factors and outputs.
        start = time.perf_counter()
        result = reference() if serial else run()
        first = time.perf_counter() - start
        side = json.loads(result.sidecar_path.read_bytes())
        store = result.csv_path.parent / side["blinding"]["withheld"]["path"]
        expected = [p.read_bytes() for p in (result.csv_path, result.sidecar_path, store)]
        times, reference_times = [], []
        for _ in range(args.repeats):
            if serial:
                start = time.perf_counter()
                reference()
                reference_times.append(time.perf_counter() - start)
                assert expected == [p.read_bytes() for p in (result.csv_path, result.sidecar_path, store)]
            start = time.perf_counter()
            result = run()
            times.append(time.perf_counter() - start)
            assert expected == [p.read_bytes() for p in (result.csv_path, result.sidecar_path, store)]
        # Count real decompressor launches outside the timing samples, including
        # worker threads (cProfile itself records only the calling thread).
        popen = subprocess.Popen
        counter_lock = Lock()
        def decompressions(function):
            count = 0
            def launch(command, *a, **kw):
                nonlocal count
                if Path(str(command[0])).name == "zstd" and any(x in command for x in ("-d", "-dc")):
                    with counter_lock:
                        count += 1
                return popen(command, *a, **kw)
            with patch("subprocess.Popen", side_effect=launch):
                function()
            return count
        reference_decompressions = decompressions(reference) if serial else None
        optimized_decompressions = decompressions(run)
        profile = cProfile.Profile()
        profile.runcall(run)
        output = io.StringIO()
        pstats.Stats(profile, stream=output).strip_dirs().sort_stats("cumulative").print_stats(22)
        print(json.dumps({"synthetic_only": True, "synthetic_space_seam": True,
                          "compressed": args.compressed, "workers": args.workers,
                          "references": args.references, "science": args.science,
                          "blob_mib": args.blob_mib, "samples": args.samples,
                          "interval_trace": args.interval_trace,
                          "serial_commit": SERIAL_EXPORT_COMMIT if serial else None,
                          "serial_seconds": reference_times,
                          "serial_median_seconds": statistics.median(reference_times) if serial else None,
                          "serial_decompressions": reference_decompressions,
                          "optimized_decompressions": optimized_decompressions,
                          "first_seconds": first, "seconds": times, "median_seconds": statistics.median(times),
                          "csv_sidecar_withheld_bytes_equal": True}, sort_keys=True))
        print(output.getvalue())


if __name__ == "__main__":
    main()
