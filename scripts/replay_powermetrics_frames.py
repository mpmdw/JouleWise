#!/usr/bin/env python3
"""Replay an ARCHIVED powermetrics plist onto a file at its own recorded cadence.

Never a measurement, never sudo, never a sampler.  This is the injected
recorder of the ruled daytime bench replay (cold gate #3 ruling 10 Q7; A269
ruling 10 Q3 replacement R6): it stands in for ``sudo -n powermetrics`` so
that the real evidence chain and the real collector can be run at the
registered cadence on a desk machine, and the chain-level ``start_drift_s``
the run produces can be measured against the ruled 0.5 s bar.

What it does, exactly.  A powermetrics plist stream is a sequence of complete
XML plist documents separated by NUL bytes; each document carries an integer
``elapsed_ns`` (that frame's own interval) and a whole-second UTC ``<date>``
timestamp.  This feeder reads the source ONE CHUNK AT A TIME -- the archived
plists are ~130 MB each and are read-only inputs that are never copied whole
into memory -- splits the chunks on NUL, and writes frame *i* to ``--out`` at
the instant ``first_write + (cumulative elapsed_ns of frames 2..i)``, flushing
after every frame so the collector's first-complete-frame poll and its final
parse see exactly the byte stream a live recorder would have produced.

Two label modes (brief D4):

``--label-shift none``  Frame bytes are emitted VERBATIM.  The archived labels
  carry the night's own wall time, so on any later day the production anchor
  deriver finds no admissible endpoint (``rate_aware_native_set_empty``) and
  reports ``unresolved``.  That is a safety property -- a replay cannot be
  mistaken for a measurement -- but it also means ``align_frames`` returns no
  frames, so the per-round integration and the interior reduction never run
  and the replay under-measures the very finalisation tail it exists to time.

``--label-shift auto``  Every ``<date>`` label is shifted by ONE constant
  whole-second count K, and the first frame is written at wall
  ``A_archived + K``, where ``A_archived`` is the archived anchor's
  ``first_sample_end_point_epoch_s``.  K is a whole number of seconds, so
  labels keep their whole-second form; rollovers, inter-frame spacing and
  ``elapsed_ns`` are the archived ones.  The first frame's endpoint therefore
  lands inside the live ``pre_spawn``/``first_parse`` bracket, the anchor
  resolves ``bounded``, and the full tail runs.  NO other byte is ever
  changed in either mode.

On SIGTERM -- which is how the collector stops its recorder -- the feeder stops
at a frame boundary, writes its sidecar and exits 0, like a recorder that was
asked to stop.  When the source is exhausted before the collector's deadline it
HOLDS (writing nothing) until SIGTERM, because a recorder that exits early
makes the collector raise instead of measuring a tail.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import signal
import statistics
import sys
import time

SCHEMA = "joulewise.powermetrics_replay_feeder.v1"
# The feeder rewrites this and nothing else, and only under --label-shift auto.
DATE_PATTERN = re.compile(rb"<key>timestamp</key><date>([^<]*)</date>")
ELAPSED_PATTERN = re.compile(rb"<key>elapsed_ns</key><integer>(\d+)</integer>")
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
CHUNK_BYTES = 1 << 20
# Two poll quanta.  WRITE_POLL_S bounds how late a frame can be written: the
# target instant is recomputed from the FIRST write on every iteration, so the
# error is one quantum, not a sum of them, and 5 ms against a ~260 ms archived
# interval is under 2 %.  HOLD_POLL_S is the coarser quantum used only after
# the source is exhausted, where nothing is being paced and the only question
# is how promptly SIGTERM is honoured against a teardown budget in seconds.
WRITE_POLL_S = 0.005
HOLD_POLL_S = 0.05


class Stopped(Exception):
    """SIGTERM arrived at a frame boundary."""


def parse_label(frame):
    match = DATE_PATTERN.search(frame)
    if match is None:
        raise ValueError("replay frame carries no timestamp label")
    text = match.group(1).decode()
    return match, datetime.strptime(text, DATE_FORMAT).replace(tzinfo=timezone.utc)


def parse_elapsed_ns(frame, fallback_ns):
    match = ELAPSED_PATTERN.search(frame)
    return int(match.group(1)) if match else fallback_ns


def shift_frame(frame, shift_s):
    """Rewrite ONLY the timestamp label, by a whole number of seconds."""
    if not shift_s:
        return frame
    match, stamp = parse_label(frame)
    shifted = (stamp.timestamp() + shift_s)
    text = datetime.fromtimestamp(shifted, timezone.utc).strftime(DATE_FORMAT).encode()
    return frame[:match.start(1)] + text + frame[match.end(1):]


def archived_endpoint_epoch_s(session_path, first_frame):
    """The archived anchor's endpoint, or the first label when it never resolved.

    The shift K exists to put the replayed first endpoint inside the live
    spawn bracket.  The archived anchor's own
    ``first_sample_end_point_epoch_s`` is the exact instant to move; when the
    archived envelope's anchor was itself unresolved (three of the twelve
    pilot envelopes were) there is no such field, and the first frame's
    whole-second label is used instead -- within one second of the endpoint,
    which is inside the +-2 s native box the deriver allows.
    """

    try:
        session = json.loads(Path(session_path).read_text())
        anchor = (session.get("power") or {}).get("anchor") or {}
        endpoint = anchor.get("first_sample_end_point_epoch_s")
        if anchor.get("status") == "bounded" and isinstance(endpoint, (int, float)):
            return float(endpoint), "archived_anchor_first_sample_end_point"
    except (OSError, ValueError, AttributeError, TypeError):
        pass
    return parse_label(first_frame)[1].timestamp(), "first_frame_label"


def source_frames(path, digest):
    """Yield whole frames, one at a time, never holding the file in memory."""
    pending = b""
    with Path(path).open("rb") as stream:
        while chunk := stream.read(CHUNK_BYTES):
            digest.update(chunk)
            pending += chunk
            while (index := pending.find(b"\0")) >= 0:
                yield pending[:index]
                pending = pending[index + 1:]
    if pending.strip():
        # A truncated tail: the archived recorder was killed mid-frame.  A
        # partial document is not a frame and is never emitted as one.
        return


def sleep_until(monotonic_target, stop):
    while not stop[0]:
        remaining = monotonic_target - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(WRITE_POLL_S, remaining))
    raise Stopped


def hold_until_term(stop):
    while not stop[0]:
        time.sleep(HOLD_POLL_S)
    raise Stopped


def write_sidecar(path, payload):
    if path is None:
        return
    Path(path).write_text(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n")


def run(args):
    stop = [False]

    def stopping(_signum, _frame):
        stop[0] = True

    signal.signal(signal.SIGTERM, stopping)
    signal.signal(signal.SIGINT, stopping)
    source_digest, out_digest = hashlib.sha256(), hashlib.sha256()
    interval_ns = int(round(args.interval_ms * 1e6))
    frames = source_frames(args.source, source_digest)
    written, writes, labels, since_first_ns = 0, [], [], 0
    shift_s, shift_basis, endpoint = 0, None, None
    exit_reason = "source_exhausted_then_term"
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    started_epoch_s, started_monotonic_s, first_write = None, None, None
    with out.open("wb") as stream:
        try:
            for frame in frames:
                elapsed_ns = parse_elapsed_ns(frame, interval_ns)
                if written == 0:
                    if args.label_shift == "auto":
                        endpoint, shift_basis = archived_endpoint_epoch_s(args.session, frame)
                        # Whole seconds only: a fractional shift would have to
                        # rewrite the label's SECONDS field into something the
                        # archived stream never contained.
                        shift_s = int(math.ceil(time.time() - endpoint))
                        # Sleep to the wall instant the shifted endpoint names,
                        # so the live first-parse stamp brackets it.
                        target = endpoint + shift_s
                        sleep_until(time.monotonic() + max(0.0, target - time.time()), stop)
                else:
                    # Frame i is due its own ``elapsed_ns`` after frame i-1,
                    # measured from the FIRST write, so a slow write never
                    # accumulates into the replayed cadence.
                    since_first_ns += elapsed_ns
                    sleep_until(first_write + since_first_ns / 1e9, stop)
                payload = shift_frame(frame, shift_s) + b"\0"
                stream.write(payload)
                stream.flush()
                out_digest.update(payload)
                written += 1
                writes.append(elapsed_ns)
                labels.append(time.monotonic())
                if written == 1:
                    # The cadence is paced from the instant frame 1 became
                    # VISIBLE to the collector, not from the instant the write
                    # was begun: otherwise frame 1's own write cost is
                    # subtracted from the first inter-frame interval and every
                    # recorded delta but the first is right only in sum.
                    first_write = labels[0]
                    started_epoch_s, started_monotonic_s = time.time(), labels[0]
            exit_reason = "source_exhausted_then_term"
            hold_until_term(stop)
        except Stopped:
            exit_reason = "term" if written else "term_before_first_frame"
    deltas = [b - a for a, b in zip(labels, labels[1:])]
    write_sidecar(args.sidecar, {
        "schema": SCHEMA, "source": str(args.source), "session": str(args.session),
        "out": str(out), "source_sha256": source_digest.hexdigest(),
        "written_stream_sha256": out_digest.hexdigest(),
        "label_shift": args.label_shift, "label_shift_s": shift_s,
        "label_shift_basis": shift_basis, "archived_endpoint_epoch_s": endpoint,
        "interval_ms": args.interval_ms, "frames_written": written,
        "first_write_epoch_s": started_epoch_s, "first_write_monotonic_s": started_monotonic_s,
        "frame_elapsed_ns": writes if written <= 256 else None,
        "write_monotonic_s": labels if written <= 256 else None,
        "write_delta_s": {
            "min": min(deltas) if deltas else None,
            "median": statistics.median(deltas) if deltas else None,
            "max": max(deltas) if deltas else None},
        "exit_reason": exit_reason})
    return 0


def parser():
    ap = argparse.ArgumentParser(description="Replay an archived powermetrics plist; never a measurement.")
    ap.add_argument("--source", required=True, help="archived powermetrics plist (read-only, never copied)")
    ap.add_argument("--session", required=True, help="the archived envelope's session.json")
    ap.add_argument("--out", required=True, help="stream to write, in the collector's raw directory")
    ap.add_argument("--interval-ms", type=float, default=100.0,
                    help="declared cadence; used only for a frame with no elapsed_ns")
    ap.add_argument("--label-shift", choices=("none", "auto"), default="none")
    ap.add_argument("--sidecar", default=None, help="where the run's own record is written")
    return ap


def main(argv=None):
    args = parser().parse_args(sys.argv[1:] if argv is None else argv)
    if args.interval_ms <= 0:
        print("error: interval must be positive", file=sys.stderr)
        return 2
    try:
        return run(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
