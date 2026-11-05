#!/usr/bin/env python3
"""Run a writer in a new process group; poll each filesystem every five seconds.

On low/unknown free space, stop the entire writer group and exit 75. Never
resume or delete automatically. Ed must disposition the stopped group/partials.
"""
import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys

FLOOR = 30_000_000_000
INTERVAL = 5


def free_bytes(path):
    s = os.statvfs(path)
    return s.f_bavail * s.f_frsize


def device_id(path):
    return os.stat(path).st_dev


def check(paths, devices):
    for p in paths:
        if device_id(p) != devices[p]:
            raise RuntimeError('volume identity changed')
        if free_bytes(p) < FLOOR:
            raise RuntimeError('disk floor')


def stop_group(child):
    if child.poll() is None:
        try:
            os.killpg(child.pid, signal.SIGSTOP)
        except ProcessLookupError:
            pass


def run(paths, argv):
    devices = {p: device_id(p) for p in paths}
    check(paths, devices)  # no writer if admission already fails
    child = subprocess.Popen(argv, start_new_session=True)
    print('GUARDED_WRITER_PGID=' + str(child.pid), flush=True)
    try:
        while True:
            check(paths, devices)
            try:
                return child.wait(timeout=INTERVAL)
            except subprocess.TimeoutExpired:
                pass
    except BaseException:
        stop_group(child)
        print('STOPPED_WRITER_PGID=' + str(child.pid) + '; preserve partials; Ed ruling required',
              file=sys.stderr, flush=True)
        return 75


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--path', action='append', type=Path, required=True)
    p.add_argument('argv', nargs=argparse.REMAINDER)
    args = p.parse_args()
    argv = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
    if not argv:
        p.error('writer command required after --')
    return run(args.path, argv)


if __name__ == '__main__':
    sys.exit(main())
