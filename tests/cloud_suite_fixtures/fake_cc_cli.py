#!/usr/bin/env python3.13
"""Bounded fake CLI: emit a created line, request trust, or emit nothing."""

import os
from pathlib import Path
import re
import select
import signal
import sys
import time


def main():
    if any(re.search(r"(?i)claude|codex", arg) for arg in sys.argv):
        raise AssertionError("unsafe fixture argv")
    signal.alarm(19)
    mode = os.environ.get("FAKE_CC_MODE", "created")
    record = os.environ.get("FAKE_CC_RECORD")
    def terminate(signum, frame):
        if record:
            with Path(record).open("a") as stream:
                stream.write(f"terminated {os.getpid()}\n")
        raise SystemExit(0)
    signal.signal(signal.SIGTERM, terminate)
    if record:
        with Path(record).open("a") as stream:
            stream.write(f"started {os.getpid()}\n")
    if mode == "trust":
        print("Do you trust this folder?", flush=True)
        answer = bytearray()
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and len(answer) < 4:
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                value = os.read(sys.stdin.fileno(), 4 - len(answer))
                if not value:
                    return 1
                answer.extend(value)
        if record:
            with Path(record).open("a") as stream:
                stream.write(f"trust {bytes(answer).hex()}\n")
        if bytes(answer) != b"\x1b[B\r":
            return 1
    if mode != "silent":
        # The URL belongs in output, never argv (the agent census reads argv).
        print("Created cloud session: session_A123 View: "
              "https://claude.ai/code/session_A123", flush=True)
    time.sleep(12)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
