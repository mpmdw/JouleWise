"""Reader-only host, transfer and overlap evidence for synthetic R12 roots."""
from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path

from b6_r12_verify import child, sha


def overlap_facts(roots):
    result = []
    for raw in roots:
        root = Path(raw).absolute()
        allowed = (Path("/Volumes/JW-EXT/jwsol/squeeze/p1-b6-r12c/tmp"), Path("/private/tmp/r12-mbp-tmp"))
        if (not any(root.is_relative_to(parent) for parent in allowed)
                or root != root.resolve() or "restricted" in root.parts):
            raise ValueError("explicit synthetic overlap root required")
        path = root / "parent.json"
        value = json.loads(path.read_bytes())
        result.append({"root": str(root), "parent_sha256": sha(path),
                       "status": value["status"], "pid": value.get("pid"),
                       "supervisor_pid": value.get("supervisor_pid"),
                       "basis": "recorded orchestrator-launched generator; no host process census"})
    return result


def mbp_native_interval(outer, root, sid, original, times_path, hashes_path):
    times_path, hashes_path = Path(times_path), Path(hashes_path)
    if times_path != Path(str(outer) + ".mbp-mtimes.txt") or hashes_path != Path(str(outer) + ".mbp-sha256.txt"):
        raise ValueError("named MBP transfer sidecars required")
    times, hashes = {}, {}
    for line in times_path.read_text().splitlines():
        stamp, size, name = line.split(" ", 2)
        if name in times:
            raise ValueError("duplicate native timestamp")
        ns = Decimal(stamp) * 1_000_000_000
        if ns != ns.to_integral_value():
            raise ValueError("native timestamp precision is not integer nanoseconds")
        times[name] = (int(ns), int(size))
    for line in hashes_path.read_text().splitlines():
        digest, name = line.split("  ", 1)
        if name in hashes or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("invalid transfer hash record")
        hashes[name] = digest
    metadata = json.loads((root / "sessions" / sid / "session.json").read_bytes())
    archive = child(root, metadata["paths"]["archive"])
    endpoints = [root / "fixture-manifests" / (sid + ".json"), Path(str(archive) + ".desk/compression.jsonl")]
    observed = []
    for path in endpoints:
        child(root, str(path))
        key = str(path.relative_to(outer.parent))
        stamp, size = times[key]
        if path.stat().st_size != size or sha(path) != hashes[key]:
            raise ValueError("MBP native endpoint bytes differ from authenticated transfer")
        observed.append({"path": key, "mtime_ns": stamp, "sha256": hashes[key], "bytes": size})
    if observed[1]["mtime_ns"] < observed[0]["mtime_ns"]:
        raise ValueError("MBP native interval reversed")
    return {**original, "method": "MBP-side stat %Fm nanosecond timestamps, authenticated endpoint bytes",
        "generation_host": "MBP Mac15,9", "air_copy_native_interval": original,
        "start_mtime_ns": observed[0]["mtime_ns"], "end_mtime_ns": observed[1]["mtime_ns"],
        "wall_s": (observed[1]["mtime_ns"] - observed[0]["mtime_ns"]) / 1e9,
        "mbp_native_endpoints": observed,
        "transfer_sha256": {times_path.name: sha(times_path), hashes_path.name: sha(hashes_path)},
        "transfer_basis": "orchestrator verified all regular files; this reader independently authenticates both native endpoints"}
