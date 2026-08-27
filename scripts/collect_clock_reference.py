#!/usr/bin/env python3
"""Collect and canonically emit one ruled T-0 clock-reference report."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import BinaryIO, Callable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402
from joulewise import clock_reference  # noqa: E402


GOVERNED_SUBPROCESS_ENVIRONMENT = {
    "LANG": "C",
    "LC_ALL": "C",
    "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
}


def _parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="emit the fixed-policy T-0 clock-reference observations"
    )


def _run_sntp(argv: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    """Run one report-only SNTP leg with no shell, prompt, or inherited env."""

    return subprocess.run(
        list(argv),
        cwd=REPO_ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=GOVERNED_SUBPROCESS_ENVIRONMENT,
        shell=False,
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    runner: clock_reference.SampleRunner | None = None,
    clock_gettime_ns: clock_reference.ClockGettimeNs = time.clock_gettime_ns,
    boot_session_id_reader: Callable[[], str] = readiness._current_boot_session_id,
    stdout: BinaryIO | None = None,
) -> int:
    """Collect once and write exactly one D-134 canonical object to stdout."""

    _parser().parse_args(argv)
    value = clock_reference.build_clock_reference(
        boot_session_id=boot_session_id_reader(),
        runner=_run_sntp if runner is None else runner,
        clock_gettime_ns=clock_gettime_ns,
    )
    output = sys.stdout.buffer if stdout is None else stdout
    output.write(readiness.render_json(value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
