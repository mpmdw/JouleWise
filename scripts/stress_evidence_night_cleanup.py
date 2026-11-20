#!/usr/bin/env python3
"""Offline stress of the builder-error test with real, delayed Git maintenance.

Three tiny synthetic packs force automatic GC. A pre-auto-gc hook holds that
real child until the CLI returns, then releases it and observes its writes.
The harness waits for that child before normal unittest cleanup, so a failing
run reports the leak without leaving its own writer behind. No cleanup retries
or error suppression are used. Run from any directory; no network is needed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise import evidence_night as entry
from tests.git_fixture import init_git_fixture
from tests.test_evidence_night import PrepareTests


def git(*args, input=None):
    return subprocess.check_output(["git", *map(str, args)], input=input, text=True).strip()


def events(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def wait_for(predicate):
    deadline = time.monotonic() + 10
    while not predicate():
        if time.monotonic() >= deadline:
            raise TimeoutError("synthetic Git maintenance did not reach its barrier/exit")
        time.sleep(0.01)


def snapshot(root):
    return {str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=20)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    if not Path("/bin/zsh").is_file():
        parser.error("/bin/zsh is required by the test under stress")
    start = time.monotonic()
    result = unittest.TestResult()
    live_returns = writes = 0
    first_changed_paths = []
    first_late_commands = []
    with patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                                 "GIT_CONFIG_COUNT": "0"}), \
            tempfile.TemporaryDirectory(prefix="evidence-flake-stress-") as tmp:
        base = Path(tmp).resolve()
        remote = base / "remote"
        remote.mkdir()
        init_git_fixture(remote, "-q")
        git("-C", remote, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "synthetic fixture", "--allow-empty")
        head = git("-C", remote, "rev-parse", "HEAD")
        git("-C", remote, "update-ref", "refs/heads/main", head)
        for index in range(3):
            oid = git("-C", remote, "hash-object", "-w", "--stdin", input=f"pack fixture {index}\n")
            git("-C", remote, "pack-objects", ".git/objects/pack/pack", input=oid + "\n")
        hooks = base / "hooks"
        hooks.mkdir()
        ready, release = base / "ready", base / "release"
        hook = hooks / "pre-auto-gc"
        hook.write_text("#!/bin/sh\n" + f": > {shlex.quote(str(ready))}\n"
                        + "count=0\n"
                        + f"while [ ! -e {shlex.quote(str(release))} ]; do\n"
                        + '  count=$((count + 1)); [ "$count" -lt 1000 ] || exit 1\n'
                        + "  sleep 0.01\ndone\n")
        hook.chmod(0o755)
        trace = base / "git-trace.jsonl"
        settings = {"gc.autoPackLimit": "1", "gc.autoDetach": "true",
                    "maintenance.auto": "true", "maintenance.autoDetach": "true",
                    "core.hooksPath": str(hooks)}
        env = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_TRACE2_EVENT": str(trace), "GIT_CONFIG_COUNT": str(len(settings))}
        for index, (key, value) in enumerate(settings.items()):
            env[f"GIT_CONFIG_KEY_{index}"] = key
            env[f"GIT_CONFIG_VALUE_{index}"] = value
        # Reuse the exact CI test and its normal setUp/cleanup, replacing only
        # the class's expensive full-repository remote with this tiny fixture.
        PrepareTests.base, PrepareTests.remote, PrepareTests.head = base, remote, head
        PrepareTests.bin = base / "bin"
        PrepareTests.bin.mkdir()
        original_main = entry.main

        def observed_main(*argv, **kwargs):
            nonlocal live_returns, writes, first_changed_paths, first_late_commands
            try:
                code = original_main(*argv, **kwargs)
                # The target test supplies its own per-case trace destination.
                active_trace = Path(os.environ["GIT_TRACE2_EVENT"])
                rows = events(active_trace)
                maintenance = [row for row in rows if row.get("event") == "child_start"
                               and "maintenance" in row.get("argv", ())]
                if not maintenance:
                    return code
                wait_for(ready.exists)
                rows = events(active_trace)
                sid = next(row["sid"] for row in rows if row.get("event") == "start"
                           and "maintenance" in row.get("argv", ()))
                offset = len(rows)
                live_returns += 1
                measurement = next(base.glob("case-*/roots/night-custody/measurement/*"))
                before = snapshot(measurement / ".git")
            finally:
                release.touch()
            wait_for(lambda: any(row.get("sid") == sid and row.get("event") == "atexit"
                                 for row in events(active_trace)[offset:]))
            after = snapshot(measurement / ".git")
            changed = before != after
            writes += changed
            if not first_changed_paths:
                first_changed_paths = sorted(path for path in before.keys() | after.keys()
                                             if before.get(path) != after.get(path))
                first_late_commands = [row["argv"] for row in events(active_trace)[offset:]
                                       if row.get("event") == "start"]
            raise AssertionError(f"Git maintenance alive after CLI return; writes after return: {changed}")

        with patch.dict(os.environ, env), patch.object(entry, "main", side_effect=observed_main):
            for index in range(args.runs):
                for path in (ready, release, trace):
                    path.unlink(missing_ok=True)
                PrepareTests("test_unexpected_builder_is_error_exit_one").run(result)
                if (index + 1) % 20 == 0:
                    print(f"{index + 1}/{args.runs}: failures={len(result.failures)}, "
                          f"errors={len(result.errors)}", flush=True)
        print(json.dumps({"runs": result.testsRun, "failures": len(result.failures),
                          "errors": len(result.errors), "live_children_after_return": live_returns,
                          "writes_after_return": writes,
                          "first_changed_paths": first_changed_paths,
                          "first_commands_after_return": first_late_commands,
                          "seconds": round(time.monotonic() - start, 3)}, indent=2))
        for _, detail in (result.failures + result.errors)[:1]:
            print(detail)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
