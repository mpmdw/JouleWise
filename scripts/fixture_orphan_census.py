#!/usr/bin/env python3
"""Report registered test-fixture processes reparented to PID 1; never signal them."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Sequence


DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / "tests/fixture_signatures.json"
PS_ARGV = ["ps", "-axww", "-o", "pid=,ppid=,lstart=,rss=,command="]


def load_signatures(path: Path = DEFAULT_REGISTRY) -> list[tuple[str, re.Pattern[str]]]:
    """An unavailable/invalid registry is an error, never a clean census."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or not value:
        raise ValueError("fixture signature registry must be a non-empty list")
    signatures = []
    seen = set()
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("fixture signature must be an object")
        name, pattern = row.get("id"), row.get("command_regex")
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ValueError("fixture signature IDs must be non-empty and unique")
        if not isinstance(pattern, str) or not pattern.strip():
            raise ValueError(f"fixture signature {name} has no command_regex")
        compiled = re.compile(pattern)
        if compiled.search(""):
            raise ValueError(f"fixture signature {name} matches an empty command")
        signatures.append((name, compiled))
        seen.add(name)
    return signatures


def process_inventory() -> str:
    # quiet_guard_process's kernel table has no RSS. This observational ps
    # snapshot is deliberately separate from the identity/culling authority.
    result = subprocess.run(
        PS_ARGV, check=True, capture_output=True, text=True, timeout=10,
        env={**os.environ, "LC_ALL": "C"},
    )
    if not result.stdout.strip():
        raise ValueError("ps returned an empty process inventory")
    return result.stdout


def census(
    inventory: str,
    signatures: Sequence[tuple[str, re.Pattern[str]]],
    *,
    now: float | None = None,
) -> list[dict[str, object]]:
    if not signatures:
        raise ValueError("fixture signature registry must not be empty")
    observed_at = time.time() if now is None else now
    matches = []
    for line in inventory.splitlines():
        if not line.strip():
            continue
        # Five lstart fields; maxsplit preserves the complete displayed command.
        fields = line.split(None, 8)
        if len(fields) != 9:
            raise ValueError("malformed ps inventory row")
        pid, ppid, rss = int(fields[0]), int(fields[1]), int(fields[7])
        if pid < 0 or ppid < 0 or rss < 0:
            raise ValueError("negative ps inventory field")
        if ppid != 1:
            continue
        for name, pattern in signatures:
            if not pattern.search(fields[8]):
                continue
            # ps lstart is local wall time. mktime resolves DST at the start
            # date rather than applying today's offset to an older process.
            started = time.mktime(time.strptime(" ".join(fields[2:7]), "%a %b %d %H:%M:%S %Y"))
            matches.append({
                "pid": pid,
                "ppid": ppid,
                "start": dt.datetime.fromtimestamp(started, dt.timezone.utc).isoformat(),
                "age_s": max(0.0, observed_at - started),
                "rss_kb": rss,
                "signature": name,
            })
            break  # Registry order breaks ties; report each PID once.
    return sorted(matches, key=lambda row: row["pid"])


def collect(registry: Path = DEFAULT_REGISTRY) -> list[dict[str, object]]:
    signatures = load_signatures(registry)
    return census(process_inventory(), signatures)


def launch_observation() -> dict[str, object]:
    """Informational launch record, including visible acquisition failures."""
    try:
        rows = collect()
    except (OSError, ValueError, re.error, subprocess.SubprocessError) as exc:
        return {"count": None, "rows": None, "error": f"{type(exc).__name__}: {exc}"}
    return {"count": len(rows), "rows": rows, "error": None}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--fail-on-orphans", action="store_true")
    args = parser.parse_args(argv)
    try:
        rows = collect(args.registry)
    except (OSError, ValueError, re.error, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        return 2
    print(json.dumps(rows, sort_keys=True))
    return 1 if args.fail_on_orphans and rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
