"""Bounded desk fixture: user-owned stand-ins for sudo and its root child."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--child', action='store_true')
    parser.add_argument('--ignore-term', action='store_true')
    args = parser.parse_args()
    root = args.directory
    parent = os.getppid()
    deadline = time.monotonic()+90
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if args.child:
        if args.ignore_term:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
        (root/'fake-child-ready.json').write_text(json.dumps({'pid': os.getpid()}))
        while os.getppid() == parent and time.monotonic() < deadline:
            time.sleep(.01)
        return 0
    child = subprocess.Popen([sys.executable, '-m', 'tests.quiet_kit.fake_sudo', '--child',
                             '--directory', str(root), *(['--ignore-term'] if args.ignore_term else [])])
    (root/'fake-sudo-child.json').write_text(json.dumps({'pid': child.pid}))
    def relay(sig, frame):
        with (root/'fake-signals.jsonl').open('a') as out:
            out.write(json.dumps({'signal': sig})+'\n')
        try:
            child.send_signal(sig)
        except ProcessLookupError:
            pass
    signal.signal(signal.SIGTERM, relay)
    try:
        while not (root/'fake-child-ready.json').exists():
            if os.getppid() != parent or time.monotonic() >= deadline or child.poll() is not None:
                raise RuntimeError('fake child did not initialize')
            time.sleep(.005)
        (root/'fake-sudo-ready.json').write_text(json.dumps({'pid': os.getpid(), 'child_pid': child.pid}))
        while child.poll() is None and os.getppid() == parent and time.monotonic() < deadline:
            time.sleep(.01)
        return 0
    finally:
        if child.poll() is None:
            child.kill()
        child.wait(timeout=5)


if __name__ == '__main__':
    raise SystemExit(main())
