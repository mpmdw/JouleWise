#!/usr/bin/env python3.13
"""BSD script-shaped bounded wrapper, preserving stdin and teeing stdout."""

import os
from pathlib import Path
import re
import signal
import subprocess
import sys


def main():
    if any(re.search(r"(?i)claude|codex", arg) for arg in sys.argv):
        raise AssertionError("unsafe fixture argv")
    signal.alarm(19)
    if len(sys.argv) < 5 or sys.argv[1] != "-q":
        return 2
    process = None
    def terminate(signum, frame):
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        raise SystemExit(0)
    signal.signal(signal.SIGTERM, terminate)
    with Path(sys.argv[2]).open("wb", buffering=0) as transcript:
        process = subprocess.Popen(sys.argv[3:], stdin=sys.stdin, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline, b""):
            transcript.write(line)
            os.write(sys.stdout.fileno(), line)
        return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
