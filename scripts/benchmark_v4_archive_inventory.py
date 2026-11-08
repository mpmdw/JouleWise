#!/usr/bin/env python3
"""Synthetic-only v4 archive inventory experiment; never accepts a data path.

Extract only the pinned lane's hash/inventory/clone functions from Git objects.
Do not import or run its harvest/analysis/compression pipeline. Each source,
destination and final source inventory uses fresh hashes, as custody requires.
Page-cache warmth and competing machine load are uncontrolled.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.file_hashes import FileHashes

LANE = "e901eb2a480d51377a494be9d797733dfcd0220b"


def lane_functions():
    raw = subprocess.check_output(
        ["git", "show", f"{LANE}:joulewise/b5/harvest.py"], cwd=ROOT)
    tree = ast.parse(raw)
    names = {"sha256_file", "tree_inventory", "clone_tree"}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in nodes} != names:
        raise ValueError("pinned lane function inventory differs")
    namespace = dict(Path=Path, os=os, sys=sys, shutil=shutil, subprocess=subprocess, hashlib=hashlib)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<pinned-v4-inventory>", "exec"), namespace)
    return namespace["tree_inventory"], namespace["clone_tree"], hashlib.sha256(raw).hexdigest()


def parallel_inventory(root, workers):
    hashes = FileHashes(workers)
    def entry(path):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            return name, {"link": os.readlink(path)}
        if path.is_file():
            return name, {"sha256": hashes.sha256(path), "size": path.stat().st_size}
        return None
    return dict(row for row in hashes.map(entry, sorted(root.rglob("*"))) if row is not None)


def benchmark(*, files, mib, repeats, workers):
    inventory, clone, program_sha = lane_functions()
    records = []
    with tempfile.TemporaryDirectory(prefix="jw-v4-inventory-", dir="/private/tmp") as directory:
        root = Path(directory)
        source = root / "synthetic-source"
        source.mkdir()
        chunk = bytes(range(256)) * 4096
        for number in range(files):
            with (source / f"file-{number:04d}.bin").open("xb") as stream:
                for _ in range(mib):
                    stream.write(chunk)
        (source / "literal-link").symlink_to("file-0000.bin")
        reference = inventory(source)
        for repeat in range(repeats):
            for count in (None, *workers):
                read = inventory if count is None else lambda path: parallel_inventory(path, count)
                destination = root / f"copy-{repeat}-{count}"
                phases = {}
                for phase, action in (
                    ("source_s", lambda: read(source)),
                    ("clone_s", lambda: clone(source, destination)),
                    ("destination_s", lambda: read(destination)),
                    ("source_recheck_s", lambda: read(source)),
                ):
                    start = time.perf_counter()
                    result = action()
                    phases[phase] = time.perf_counter() - start
                    if phase != "clone_s" and result != reference:
                        raise ValueError("inventory mismatch")
                records.append(dict(repeat=repeat + 1, workers=count,
                                    mode="lane_serial" if count is None else "candidate_fresh_streams",
                                    total_s=sum(phases.values()), **phases))
                shutil.rmtree(destination)
    medians = []
    for count in (None, *workers):
        selected = [row for row in records if row["workers"] == count]
        medians.append(dict(workers=count, **{
            key: statistics.median(row[key] for row in selected)
            for key in ("source_s", "clone_s", "destination_s", "source_recheck_s", "total_s")}))
    return dict(lane_commit=LANE, lane_harvest_sha256=program_sha, input_kind="synthetic",
                files=files, bytes=files * mib * 1024 * 1024, repeats=repeats,
                manifest_equal=True, fresh_inventory_passes=3, records=records, medians=medians)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", type=int, default=16)
    parser.add_argument("--mib", type=int, default=4)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--workers", type=int, choices=(1, 2, 4), nargs="+", default=(1, 2, 4))
    args = parser.parse_args()
    if min(args.files, args.mib, args.repeats) < 1:
        parser.error("files, mib and repeats must be positive")
    print(json.dumps(benchmark(**vars(args)), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
