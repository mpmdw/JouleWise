"""Run a round-3 repro script unchanged at the reviewed commit. Round 4 (K2) makes the
clock fields mandatory in scan receipts; the round-3 scripts predate them. This shim
adds the lead-measured Mac clock (getres 4.2e-8 s, timebase 125/3 ns, conversion unknown)
to any scan receipt that lacks `clock`, and to stream() receipts via clock_metadata.
Usage: python3.13 -B run_with_clock.py /tmp/jw SCRIPT.py [script args...]
"""
import runpy, sys
from pathlib import Path
sys.path[:0] = [sys.argv[1], str(Path(__file__).parent)]
from scripts import bytes_stream_test as p
MAC = {"clock": "CLOCK_MONOTONIC_RAW", "clock_resolution_s": 4.2e-8, "clock_tick_num_ns": 125,
       "clock_tick_den": 3, "clock_tick_source": "lead measurement 2026-10-28 (synthetic)",
       "clock_ns_conversion": "unknown", "clock_ns_conversion_source": "unknown"}
_scan = p.knee_scan
def knee_scan(receipts):
    return _scan([r if "clock" in r else {**r, **MAC} for r in receipts])
p.knee_scan = knee_scan
p.clock_metadata = lambda: {**MAC, "clock_duration_bound_ns": 86.0}
script = sys.argv[2]
sys.argv = [script] + sys.argv[1:2] + sys.argv[3:]
runpy.run_path(script, run_name="__main__")
