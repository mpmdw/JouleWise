#!/usr/bin/env python3
"""Run a writer in a new process group; poll each filesystem every five seconds.

On low/unknown free space, stop the entire writer group and exit 75. Never
resume or delete automatically. Ed must disposition the stopped group/partials.
"""
import argparse
import os
from pathlib import Path
import signal
import select
import subprocess
import sys
import time

FLOOR = 30_000_000_000
INTERVAL = 5
HEARTBEAT_TIMEOUT = 15
STOP_SIGNALS = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT, signal.SIGQUIT)


def writer_wrapper(fd, argv):
    """Child supervisor shares the writer's group; pipe EOF survives SIGKILL.

    Only the guard owns the pipe's write end. The actual writer never inherits
    either end. No detached/session-changing writers are allowed.
    """
    def stop():
        os.killpg(os.getpgrp(), signal.SIGSTOP)
        # A manual SIGCONT does not authorize an unguarded restart.
        raise SystemExit(75)

    for sig in STOP_SIGNALS:
        signal.signal(sig, lambda *_: stop())
    # The parent blocks termination signals across spawn/publication.
    signal.pthread_sigmask(signal.SIG_UNBLOCK, STOP_SIGNALS)
    if not os.read(fd, 1):
        stop()
    child = subprocess.Popen(argv, close_fds=True)
    last = time.monotonic()
    try:
        while child.poll() is None:
            ready, _, _ = select.select([fd], [], [], 0.2)
            if ready:
                if not os.read(fd, 4096):
                    stop()
                last = time.monotonic()
            if time.monotonic() - last > HEARTBEAT_TIMEOUT:
                stop()
        return child.returncode
    except BaseException:
        stop()


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
    # A dead group leader can still leave live writer descendants.
    try:
        os.killpg(child.pid, signal.SIGSTOP)
    except ProcessLookupError:
        pass


def run(paths, argv):
    devices = {p: device_id(p) for p in paths}
    check(paths, devices)  # no writer if admission already fails
    child = None
    read_fd, write_fd = os.pipe()
    previous = {}
    def completed(code):
        if code != 0:
            stop_group(child)
        return code

    def on_signal(sig, frame):
        if child is not None:
            stop_group(child)
        raise SystemExit(128 + sig)

    old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, STOP_SIGNALS)
    try:
        for sig in STOP_SIGNALS:
            previous[sig] = signal.signal(sig, on_signal)
        child = subprocess.Popen(
            [sys.executable, '-I', '-B', str(Path(__file__).resolve()),
             '--writer-wrapper', str(read_fd), '--', *argv],
            start_new_session=True, pass_fds=(read_fd,))
        os.close(read_fd)
        read_fd = None
        os.write(write_fd, b'.')
        print('GUARDED_WRITER_PGID=' + str(child.pid), flush=True)
        signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)
        while True:
            check(paths, devices)
            try:
                os.write(write_fd, b'.')
            except BrokenPipeError:
                return completed(child.wait())
            try:
                return completed(child.wait(timeout=INTERVAL))
            except subprocess.TimeoutExpired:
                pass
    except BaseException:
        if child is not None:
            stop_group(child)
            print('STOPPED_WRITER_PGID=' + str(child.pid) + '; preserve partials; Ed ruling required',
                  file=sys.stderr, flush=True)
        return 75
    finally:
        os.close(write_fd)
        if read_fd is not None:
            os.close(read_fd)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)


def main():
    if sys.argv[1:2] == ['--writer-wrapper']:
        return writer_wrapper(int(sys.argv[2]), sys.argv[4:])
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
