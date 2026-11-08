#!/usr/bin/env python3
"""Compare closed-file manifest hashing; run on the MBP only in a window gap.

Defaults to generated synthetic bytes under /private/tmp. --closed-root reads
only the operator-selected, already closed tree; never writes it, launches a
measurement/analysis, pushes, copies or deletes evidence. Output is timing,
counts and equality only. Cache/page-cache warmth is NOT controlled here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.file_hashes import FileHashes, WORKER_COUNTS
from scripts.harvest_window import inventory, json_bytes, HarvestRefusal


def legacy_inventory(root):
    """Pre-change algorithm, retained as the byte equality/timing oracle."""
    rows = {}
    for path in [root, *sorted(root.rglob("*"))]:
        st = path.lstat()
        row = {"mode": st.st_mode, "size": st.st_size, "mtime_ns": st.st_mtime_ns}
        if path.is_symlink():
            row["link"] = os.readlink(path)
        elif path.is_file():
            row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise HarvestRefusal("unsupported evidence file type")
        rows[path.relative_to(root).as_posix()] = row
    return rows


def benchmark(root, *, workers, passes, repeats):
    records = []
    reference = None
    for repeat in range(repeats):
        for count in (None, *workers):
            hashes = FileHashes(count) if count is not None else None
            timings = []
            for _ in range(passes):
                started = time.perf_counter()
                rows = legacy_inventory(root) if hashes is None else inventory(root, hashes=hashes)
                timings.append(time.perf_counter() - started)
                raw = json_bytes(rows)
                if reference is None:
                    reference = raw
                if raw != reference:
                    raise ValueError("manifest bytes differ or closed tree changed")
            records.append({"repeat": repeat + 1, "workers": count,
                            "mode": "legacy" if count is None else "incremental_streaming",
                            "close_s": timings[0], "repeat_s": sum(timings[1:]),
                            "total_s": sum(timings), "manifest_equal": True})
    medians = []
    for count in (None, *workers):
        selected = [r for r in records if r["workers"] == count]
        medians.append({"workers": count, "mode": selected[0]["mode"],
                        **{field: statistics.median(r[field] for r in selected)
                           for field in ("close_s", "repeat_s", "total_s")}})
    return {"files": sum("sha256" in r for r in rows.values()),
            "bytes": sum(r["size"] for r in rows.values() if "sha256" in r),
            "passes": passes, "repeats": repeats, "manifest_equal": True,
            "manifest_sha256": hashlib.sha256(reference).hexdigest(),
            "records": records, "medians": medians}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closed-root", type=Path, help="read-only closed tree (gap only)")
    parser.add_argument("--files", type=int, default=32, help="synthetic file count")
    parser.add_argument("--mib", type=int, default=8, help="MiB per synthetic file")
    parser.add_argument("--passes", type=int, default=3, help="close + repeated finalize/publish inventories")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--workers", type=int, choices=WORKER_COUNTS, nargs="+", default=list(WORKER_COUNTS))
    args = parser.parse_args(argv)
    if min(args.files, args.mib, args.passes, args.repeats) < 1:
        parser.error("files, mib, passes and repeats must be positive")
    if args.closed_root is not None:
        root = args.closed_root.absolute()
        if root.is_symlink() or not root.is_dir():
            parser.error("closed-root must be a nonsymlink directory")
        result = benchmark(root, workers=args.workers, passes=args.passes, repeats=args.repeats)
        result["input_kind"] = "operator_selected_closed_files"
    else:
        with tempfile.TemporaryDirectory(prefix="jw-finalize-bench-", dir="/private/tmp") as directory:
            root = Path(directory)
            chunk = bytes(range(256)) * 4096
            for number in range(args.files):
                with (root / f"closed-{number:04d}.bin").open("xb") as handle:
                    for _ in range(args.mib):
                        handle.write(chunk)
                    handle.flush()
                    os.fsync(handle.fileno())
            result = benchmark(root, workers=args.workers, passes=args.passes, repeats=args.repeats)
        result["input_kind"] = "synthetic"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
