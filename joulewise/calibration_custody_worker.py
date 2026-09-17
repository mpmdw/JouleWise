"""Read-only custody verification core and subprocess protocol.

This module has no ledger, lease, recovery, or append imports. Requests contain
frozen observations, never a writer capability. All filesystem opens are reads.
The parent enforces the deadline, including a blocked filesystem system call.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import stat
import sys
import time
from typing import Callable, Mapping

from joulewise.authentication_io import (
    read_authentication_input,
    read_authentication_input_nofollow,
)

INVALID = "calibration_ledger_custody_invalid"


def observation_custody_reasons(observation_id, artifacts, root, *,
                                reader=read_authentication_input, progress=None):
    """The synchronous byte/hash comparison shared with ordinary callers."""
    for relative, expected in artifacts.items():
        if progress is not None:
            progress(relative)
        try:
            actual = hashlib.sha256(reader(
                root / relative, grammar="raw",
                label=f"calibration ledger custody {observation_id} artifact {relative}",
            )).hexdigest()
        except OSError:
            return {INVALID}
        if actual != expected:
            return {INVALID}
    return set()


def artifact_hashes(root, artifacts, *, reader=read_authentication_input, progress=None):
    result = {}
    for relative in artifacts:
        if progress is not None:
            progress(relative)
        path = root / relative
        if path.is_file():
            result[relative] = hashlib.sha256(reader(
                path, grammar="raw", label=f"calibration custody artifact {relative}",
            )).hexdigest()
    return result


def assert_custody_directory(directory):
    path = Path(directory)
    if not path.is_absolute():
        raise ValueError("custody locator is not absolute")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        if stat.S_ISLNK(os.lstat(current).st_mode):
            raise ValueError(f"custody locator resolves through a symlink: {path}")
    if not stat.S_ISDIR(os.stat(path, follow_symlinks=False).st_mode):
        raise ValueError(f"custody locator is not a directory: {path}")
    return path


def custody_state(path, artifacts, read_governed, *, read_errors=(OSError, ValueError)):
    """Shared state classifier; readers retain their own authentication context."""
    try:
        if not path.exists():
            return "absent"
        if not path.is_dir():
            return "unreadable"
        present = {name for name in artifacts if (path / name).is_file()}
    except OSError:
        return "unreadable"
    if not present:
        return "empty"
    if present == set(artifacts):
        try:
            raw = read_governed(path)
            manifest = json.loads(raw["manifest.json"])
            evidence = json.loads(raw["instrument_evidence.json"])
        except (*read_errors, UnicodeDecodeError, json.JSONDecodeError):
            return "unreadable"
        if not isinstance(manifest, Mapping) or not isinstance(evidence, Mapping):
            return "unreadable"
        return "complete"
    return "partial"


def run_request(request, emit: Callable[[dict], None]):
    request_id = request["request_id"]
    budget = float(request["remaining_budget_s"])
    if not isinstance(request_id, str) or not request_id or not math.isfinite(budget):
        raise ValueError("invalid custody request")
    started = time.monotonic()
    observations = request["observations"]

    def progress(observation, artifact=None, stage="artifact_read"):
        if time.monotonic() - started >= budget:
            raise TimeoutError("custody deadline expired")
        emit({"request_id": request_id, "progress": {
            "observation_id": observation["observation_id"],
            "locator": observation["locator"], "artifact": artifact,
            "stage": stage, "elapsed_s": time.monotonic() - started,
            "pid": os.getpid(),
        }})

    reasons = set()
    result = {}
    for observation in observations:
        root = Path(observation["locator"])
        progress(observation, stage="metadata_probe")
        operation = request.get("operation", "verify")
        if operation == "hashes":
            result["artifact_sha256"] = artifact_hashes(
                root, request["governed_artifacts"],
                progress=lambda name: progress(observation, name),
            )
        elif operation == "state":
            artifacts = request["governed_artifacts"]

            def read_governed(path):
                path = assert_custody_directory(path)
                raw = {}
                for name in artifacts:
                    progress(observation, name)
                    raw[name] = read_authentication_input_nofollow(
                        path, name, grammar="raw", label=f"governed calibration artifact {path / name}")
                return raw

            result["state"] = custody_state(root, artifacts, read_governed)
        elif operation == "verify":
            artifacts = observation["artifact_sha256"]
            if not artifacts:
                if observation["disposition"] == "abandoned":
                    continue
                reasons.add(INVALID)
                break
            try:
                available = root.exists() and root.is_dir()
            except OSError:
                available = False
            if not available:
                reasons.add(INVALID)
                break
            reasons.update(observation_custody_reasons(
                observation["observation_id"], artifacts, root,
                progress=lambda name: progress(observation, name),
            ))
            if reasons:
                break
        else:
            raise ValueError("unknown custody operation")
    if time.monotonic() - started >= budget:
        raise TimeoutError("custody deadline expired")
    return {"request_id": request_id, "result": {
        "reasons": sorted(reasons), "elapsed_s": time.monotonic() - started,
        "observations": len(observations), **result,
    }}


def main():
    request = json.load(sys.stdin)
    emit = lambda value: print(json.dumps(value, sort_keys=True), flush=True)
    try:
        emit(run_request(request, emit))
    except TimeoutError:
        emit({"request_id": request["request_id"], "timeout": True})
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
