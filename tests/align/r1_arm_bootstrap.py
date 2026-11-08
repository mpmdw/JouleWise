"""SYNTHETIC ONLY: the measurement interpreter (``$PY``) of the R1 arm-route end-to-end test.

The synthetic measurement checkout's ``.venv/bin/python`` execs this file with
the argv the night chain gave ``$PY``. It is the process boundary at which the
existing R1 seams apply, nothing more:

* the R1 driver (``scripts/align_r1_rehearsal.py``) runs unchanged through its
  own ``main``, with ``--synthetic`` appended (a record label), ``_now_local``
  pinned outside the 11:45-13:15 window, and only its ``sudo``/``pmset``/
  ``mount``/``diskutil`` boundary answered by ``FakeWorld``; every runtime
  segment is a real subprocess of ``scripts/align_r1_runtime.py`` on the
  synthetic backend (``tests.align.r1_synthetic``). ``__main__`` is not used,
  so the host-state test seam ($JOULEWISE_HOST_STATE_DIR) stays honoured;
* ``scripts/km003c_monitor.py`` is answered by a synthetic streaming meter
  that writes the real stream framing until its ``--stop-file`` appears;
* anything else is executed by this interpreter unchanged.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import sys
import time

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _meter(argv):
    out = Path(argv[argv.index("--out") + 1])
    stop = Path(argv[argv.index("--stop-file") + 1])
    stopping = []
    for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(number, lambda *_: stopping.append(1))
    polls = 0
    with out.open("x") as stream:
        stream.write(json.dumps({"k": "h", "schema": "joulewise.km003c_stream.v1", "status": "streaming",
                                 "synthetic": True, "process_id": os.getpid()}) + "\n")
        while not stop.exists() and not stopping:
            stream.write(json.dumps({"k": "b", "tx": time.monotonic_ns(), "n": 0, "p": ""}) + "\n")
            stream.flush()
            polls += 1
            time.sleep(0.2)
        stream.write(json.dumps({"k": "t", "polls": polls,
                                 "stop": "stop_file" if stop.exists() else "signal"}) + "\n")
    return 0


def _driver(argv):
    from scripts import align_r1_rehearsal as r1
    from tests.align.test_r1_rehearsal import NOON_SAFE, FakeWorld
    world = FakeWorld()
    mode_file = os.environ.get("R1_ARM_TEST_MODE_FILE")
    real = r1._run

    def boundary(command):
        if "--r1-kind" in command:
            return real(command)
        result = world(command)
        if mode_file:
            Path(mode_file).write_text(str(world.mode))
        return result
    r1._run = boundary
    r1._now_local = lambda: NOON_SAFE
    code = r1.main([*argv, "--synthetic"])
    Path(os.environ["R1_ARM_TEST_WORLD"]).write_text(json.dumps(
        {"mode": world.mode, "calls": [list(c) for c in world.calls if "--r1-kind" not in c]}))
    return code


def main(argv):
    args = [a for a in argv if a != "-B"]
    if args and args[0].endswith("scripts/align_r1_rehearsal.py"):
        return _driver(args[1:])
    if args and args[0].endswith("scripts/km003c_monitor.py"):
        return _meter(args[1:])
    os.execv(sys.executable, [sys.executable, *argv])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
