#!/usr/bin/env python3
"""A stand-in for /usr/bin/powermetrics at the hardware seam of the cadence probe.

Accepts the production argv (``-n N -b 0 -i 100 --samplers ... --format plist
-o PATH``) and writes N NUL-framed plist frames whose ``elapsed_ns`` come from
an archived real capture (``FAKE_PM_FIXTURE``, a cadence fixture JSON).
Controls, all optional: ``FAKE_PM_EXIT`` (exit status), ``FAKE_PM_FRAMES``
(frames to write instead of N), ``FAKE_PM_SLEEP_S`` (sleep before exiting),
``FAKE_PM_ARGV_LOG`` (append the argv as one JSON line), ``FAKE_PM_SPAWN_ORPHAN``
(leave a sleeping child in the process group).
"""
import datetime
import json
import os
import plistlib
import subprocess
import sys
import time


def main(argv):
    if os.environ.get("FAKE_PM_ARGV_LOG"):
        with open(os.environ["FAKE_PM_ARGV_LOG"], "a") as handle:
            handle.write(json.dumps(argv) + "\n")
    count = int(argv[argv.index("-n") + 1]) if "-n" in argv else 1
    output = argv[argv.index("-o") + 1]
    fixture = json.load(open(os.environ["FAKE_PM_FIXTURE"]))
    frames = int(os.environ.get("FAKE_PM_FRAMES", count))
    stamp = datetime.datetime.fromisoformat(fixture["first_timestamp"])
    with open(output, "wb") as handle:
        for index in range(frames):
            elapsed = fixture["elapsed_ns"][index % len(fixture["elapsed_ns"])]
            if index:
                stamp += datetime.timedelta(microseconds=elapsed // 1000)
            document = {"timestamp": stamp, "elapsed_ns": elapsed, "is_delta": True,
                        "processor": dict(fixture["processor"]),
                        "thermal_pressure": fixture.get("thermal_pressure") or "Nominal"}
            handle.write(plistlib.dumps(document) + b"\0")
    if os.environ.get("FAKE_PM_SPAWN_ORPHAN"):
        subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    time.sleep(float(os.environ.get("FAKE_PM_SLEEP_S", "0")))
    return int(os.environ.get("FAKE_PM_EXIT", "0"))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
