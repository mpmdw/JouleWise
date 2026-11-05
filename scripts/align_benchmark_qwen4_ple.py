#!/usr/bin/env python3
"""Bounded synthetic PLE mmap/eager comparison; never reads model/study data."""
import argparse
import json
import os
import resource
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.align.models.qwen4_exp_tables import MMapTable, encode_rows


def rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def worker(path, mode, rows, dim, tokens):
    import numpy as np
    before = rss_bytes()
    table = MMapTable(path, rows, dim, "bf16")
    if mode == "eager":
        eager = np.array(table._map)
        # Ensure materialization; the mmap baseline never scans all rows.
        checksum = int(eager.sum(dtype=np.uint64))
    else:
        checksum = 0
    loaded = rss_bytes()
    rng = np.random.default_rng(55)
    times, pages = [], set()
    for _ in range(tokens):
        ids = rng.integers(rows, size=(1, 16))
        start = time.perf_counter_ns()
        if mode == "mmap":
            result = table.lookup(ids)
        else:
            result = (eager[ids].astype(np.uint32) << 16).view(np.float32)
        checksum += float(result.sum())
        times.append((time.perf_counter_ns() - start) / 1000)
        for i in ids.ravel():
            first, last = int(i) * dim * 2, (int(i) + 1) * dim * 2 - 1
            pages.update(range(first // 16384, last // 16384 + 1))
    return dict(mode=mode, file_bytes=rows * dim * 2, tokens=tokens,
                peak_rss_before_bytes=before, peak_rss_loaded_bytes=loaded, peak_rss_after_bytes=rss_bytes(),
                lookup_us_median=float(np.median(times)), lookup_us_p95=float(np.percentile(times, 95)),
                logical_bytes_per_token=16 * dim * 2,
                unique_page_span_bytes_16k=len(pages) * 16384,
                checksum=checksum)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--worker", choices=("mmap", "eager"))
    p.add_argument("--path")
    p.add_argument("--mib", type=int, default=128)
    p.add_argument("--tokens", type=int, default=128)
    a = p.parse_args()
    if not 1 <= a.mib <= 256 or not 1 <= a.tokens <= 4096:
        p.error("Synthetic safety bounds: 1..256 MiB, 1..4096 tokens")
    dim, rows = 256, a.mib * 1024 * 1024 // 512
    if a.worker:
        print(json.dumps(worker(a.path, a.worker, rows, dim, a.tokens)))
        return
    import numpy as np
    with tempfile.TemporaryDirectory(prefix="jw-ple-", dir="/private/tmp") as d:
        path = Path(d) / "synthetic.bf16"
        rng = np.random.default_rng(44)
        with path.open("wb") as out:
            for start in range(0, rows, 2048):
                out.write(encode_rows(rng.standard_normal((min(2048, rows - start), dim)), "bf16").tobytes())
        reports = []
        for mode in ("mmap", "eager"):
            result = subprocess.check_output([sys.executable, "-B", __file__, "--worker", mode,
                                              "--path", str(path), "--mib", str(a.mib),
                                              "--tokens", str(a.tokens)], text=True)
            reports.append(json.loads(result))
        print(json.dumps(dict(synthetic_only=True, cold_disk_io=False,
                              note="File is warm from creation; RSS is process high-water RSS, not whole-machine page-cache residency.",
                              results=reports), indent=2))


if __name__ == "__main__":
    main()
