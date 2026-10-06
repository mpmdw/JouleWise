#!/usr/bin/env python3
"""Regenerate ``l1_monitor/``: hazard-monitor journals written by lane L1's own code.

The harvest reads the monitor's journals (``joulewise.hazard_journal.v1``).
These fixtures are produced by L1's real ``joulewise.hazards.monitor.Monitor``
driven by L1's ``FakeMac`` test harness, so the harvest's tests read the
exact bytes L1 writes, not a shape the harvest invented.

Run from a tree that holds lane L1 (``joulewise/hazards`` and
``tests/hazards``), for example an integration checkout::

    cd <tree with L1> && python3 -B tests/fixtures/b5_harvest/make_l1_monitor_journals.py

The scenario, on L1's simulated timeline (420 s):

* battery: gauge publications every 60 s; publication 3 is the -447 mA
  AC-attached discharge (L1's synthetic-from-real bytes);
* contention: fseventsd at 0.9 CPU-s/s from 100 s to 112 s; kernel_task at
  0.3 CPU-s/s throughout (excluded in window, its share journaled);
* thermal: OS pressure level 1 from 200 s to 215 s;
* clock: f = -3.17 ppm drift and a 6 ms wall-clock step at 300 s;
* disk: free space drops to 5 GiB at 360 s (``disk.low``).

``expected.json`` records, for named member spans, the findings of L1's own
join (``monitor.member_findings``) and window events, so the harvest's joins
are compared against L1's on the same bytes even where L1 is not importable.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.hazards import battery, contention, monitor, thermal  # noqa: E402
from tests.hazards.fakes import Process, completed  # noqa: E402
from tests.hazards.test_monitor import FakeMac  # noqa: E402

GIB = 1024 ** 3
NS = 1_000_000_000
OUT = HERE / "l1_monitor"
JOURNALS = ("clock", "battery", "thermal", "contention", "disk", "monitor")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="b5-l1-journals-") as scratch:
        custody = Path(scratch)
        mac = FakeMac(custody)
        mac.excursion_index = 3
        mac.table.processes[340].schedule = [(100.0, 112.0, 0.9)]  # fseventsd burst
        mac.table.add(Process(0, 0, "kernel_task", cpu_per_s=0.3, cpu0=5000.0))
        start_raw = mac.clocks.raw_ns

        def elapsed() -> float:
            return (mac.clocks.raw_ns - start_raw) / NS

        mac.runner.handlers[thermal.NOTIFYUTIL_ARGV] = lambda argv: completed(
            argv, f"com.apple.system.thermalpressurelevel {1 if 200 <= elapsed() < 215 else 0}\n".encode())
        mac.statvfs = lambda path: SimpleNamespace(
            f_bavail=(5 if elapsed() >= 360 else 264) * GIB // 4096, f_frsize=4096, f_blocks=10**9)
        mac.clocks.step_at(300.0, 6_000_000)
        instance = mac.monitor()
        instance.open_session(["make_l1_monitor_journals"])
        instance.run(max_seconds=420)
        instance.close_session("fixture end")
        journals = monitor.load_journals(custody)

        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.mkdir()
        for name in JOURNALS:
            shutil.copyfile(monitor.monitor_dir(custody) / f"{name}.jsonl", OUT / f"{name}.jsonl")

    readings = monitor.readings(journals["battery"])
    excursion = next(line for line in readings if line["values"].get("instant_amperage_ma") == -447)
    publication = next(item for item in battery.publications(readings)
                       if item["update_time_s"] == excursion["values"]["update_time_s"])["monotonic_ns"]
    burst = next(item for item in monitor.contention_intervals(journals["contention"])
                 if item.get("outside_over_limit"))["interval"]["monotonic_ns"]
    thermal_hot = [line["finished"]["monotonic_ns"] for line in monitor.readings(journals["thermal"])
                   if line["values"]["level"]]
    step = next(event for event in monitor.window_events(journals)
                if event["code"] == "clock.step")["interval"]["monotonic_ns"]
    clock_lines = monitor.readings(journals["clock"])
    origin = clock_lines[0]["finished"]["monotonic_ns"]
    cases = {
        "quiet": ({"monotonic_ns": [origin + 30 * NS, origin + 50 * NS]}, None),
        "battery_excursion": ({"monotonic_ns": [publication - 20 * NS, publication + 20 * NS]}, None),
        "battery_later": ({"monotonic_ns": [publication + 70 * NS, publication + 110 * NS]}, None),
        "contention_burst": ({"monotonic_ns": [burst[0] - 5 * NS, burst[1] + 5 * NS]},
                             {"monotonic_ns": [burst[0] + NS, burst[1] - NS]}),
        "thermal_nonzero": ({"monotonic_ns": [thermal_hot[0] - 2 * NS, thermal_hot[-1] + 2 * NS]}, None),
        "clock_step": ({"monotonic_ns": [step[0] - 10 * NS, step[1] + 10 * NS]}, None),
    }
    expected = {
        "schema": "joulewise.b5_harvest_l1_journal_fixture.v1",
        "generator": "tests/fixtures/b5_harvest/make_l1_monitor_journals.py",
        "l1_source": "joulewise/hazards/monitor.py member_findings and window_events",
        "cases": {
            name: {"span": span, "request": request,
                   "l1_codes": sorted({finding["code"] for finding in
                                       monitor.member_findings(journals, span=span, request=request)})}
            for name, (span, request) in cases.items()},
        "window_events": sorted({event["code"] for event in monitor.window_events(journals)}),
        "kernel_task_cpu_s_per_s": 0.3,
    }
    (OUT / "expected.json").write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n")
    print(json.dumps(expected["cases"], indent=1, sort_keys=True))
    print("window events:", expected["window_events"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
