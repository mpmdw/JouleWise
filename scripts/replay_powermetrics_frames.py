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
into memory -- splits the chunks on NUL, and writes frame *i* to ``--out`` at the instant
``spawn + (cumulative elapsed_ns of frames 1..i)`` -- where ``spawn`` is the
feeder's own start instant on its own monotonic clock -- flushing after every
frame so the collector's first-complete-frame poll and its final parse see
exactly the byte stream a live recorder would have produced.

The FIRST frame is paced too, and that is not a nicety.  A powermetrics frame
carries its own ``elapsed_ns`` -- the span it accumulated over -- and a real
recorder cannot emit such a frame before that span has actually passed since
it was spawned.  The production anchor deriver enforces exactly that causality
(`joulewise/uncertainty_evidence.py`, ``k_pre_spawn`` vs ``k_first_parse``):
the collector's pre-spawn stamp plus the first frame's ``elapsed_ns`` must not
lie after the collector's first-parse stamp, or the anchor is `unresolved`
with ``clock_stamp_invalid``.  This feeder used to write frame 1 the moment
its digest pre-pass finished (~55 ms), so on a quiet machine the collector
parsed a frame claiming 257 ms of accumulation 165 ms after spawn, and the
first two slots of the full bench replay both came back `clock_stamp_invalid`.
Waiting ``elapsed_ns[0]`` before the first write, and pacing everything after
it from ``spawn`` rather than from that first write, is the cure.

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
# target instant is recomputed from the SPAWN instant on every iteration, so
# the error is one quantum, not a sum of them, and 5 ms against a ~260 ms
# archived interval is under 2 %.  HOLD_POLL_S is the coarser quantum used only after
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


def source_sha256(path):
    """The WHOLE source file's digest, in its own pass, before any pacing.

    Folding the digest into the pacing pass (as this feeder first did) made
    `source_sha256` a digest of however much had been READ when SIGTERM
    arrived -- and SIGTERM is the normal stop, so the sidecar's own
    provenance field named a 130 MB file and digested a prefix of it.  It was
    observed live: envelope-01 of the first `auto` smoke recorded
    `ee01f351…` against the file's true `ef4429b4…` (execution lens 17b S2).
    A separate streaming pass costs one read of the source before the first
    frame is due and cannot be truncated by a stop.
    """

    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def source_frames(path):
    """Yield whole frames, one at a time, never holding the file in memory."""
    pending = b""
    with Path(path).open("rb") as stream:
        while chunk := stream.read(CHUNK_BYTES):
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


def run(args, spawn_monotonic_s=None):
    # ``spawn_monotonic_s`` is the feeder's OWN start instant, taken by
    # ``main`` before any work at all (the digest pre-pass included), because
    # every frame's due instant is measured from it.
    spawn_monotonic_s = time.monotonic() if spawn_monotonic_s is None else spawn_monotonic_s
    stop = [False]

    def stopping(_signum, _frame):
        stop[0] = True

    signal.signal(signal.SIGTERM, stopping)
    signal.signal(signal.SIGINT, stopping)
    # The whole-file digest is taken HERE, before the first frame is due, so
    # a SIGTERM mid-stream cannot truncate it (17b S2).
    source_digest = source_sha256(args.source)
    out_digest = hashlib.sha256()
    interval_ns = int(round(args.interval_ms * 1e6))
    frames = source_frames(args.source)
    written, writes, labels, cumulative_ns, first_due = 0, [], [], 0, None
    # Frame i is due ``pacing_base + (cumulative elapsed_ns of frames 1..i)``.
    # The base is the spawn instant, and is re-seated exactly once, when the
    # `auto` wall target pushes frame 1 later than causality alone required --
    # otherwise frames 2..n, whose due instants would already be in the past,
    # would all fire back to back and the archived cadence would be lost.
    pacing_base = spawn_monotonic_s
    shift_s, shift_basis, endpoint = 0, None, None
    exit_reason = "source_exhausted_then_term"
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    started_epoch_s, started_monotonic_s = None, None
    with out.open("wb") as stream:
        try:
            for frame in frames:
                elapsed_ns = parse_elapsed_ns(frame, interval_ns)
                # Frame i is due once the feeder's own clock has run as long
                # as the accumulation frames 1..i claim: a frame that says it
                # covered 257 ms cannot be visible 165 ms after spawn, and the
                # production anchor deriver refuses such a stream outright
                # (``clock_stamp_invalid``).  Measuring from SPAWN, not from
                # the previous write or from the first write, keeps a slow
                # write from accumulating into the replayed cadence AND keeps
                # frame 1 itself honest.
                cumulative_ns += elapsed_ns
                due = pacing_base + cumulative_ns / 1e9
                if written == 0:
                    if args.label_shift == "auto":
                        endpoint, shift_basis = archived_endpoint_epoch_s(args.session, frame)
                        # Whole seconds only: a fractional shift would have to
                        # rewrite the label's SECONDS field into something the
                        # archived stream never contained.
                        shift_s = int(math.ceil(time.time() - endpoint))
                        # The wall instant the shifted endpoint names, so the
                        # live first-parse stamp brackets it.  Whichever of
                        # the two constraints is LATER governs: neither may be
                        # violated, and under `auto` this one usually is the
                        # later of the pair (K rounds up to a whole second).
                        target = endpoint + shift_s
                        due = max(due, time.monotonic() + max(0.0, target - time.time()))
                    # Re-seat the base so the archived spacing is kept from
                    # whichever constraint governed frame 1 (no-op when that
                    # was the causality floor itself).  The base never moves
                    # EARLIER than spawn, so every later frame still satisfies
                    # ``spawn + cumulative elapsed_ns``.
                    pacing_base, first_due = due - elapsed_ns / 1e9, due
                sleep_until(due, stop)
                payload = shift_frame(frame, shift_s) + b"\0"
                stream.write(payload)
                stream.flush()
                out_digest.update(payload)
                written += 1
                writes.append(elapsed_ns)
                labels.append(time.monotonic())
                if written == 1:
                    started_epoch_s, started_monotonic_s = time.time(), labels[0]
            exit_reason = "source_exhausted_then_term"
            hold_until_term(stop)
        except Stopped:
            exit_reason = "term" if written else "term_before_first_frame"
    deltas = [b - a for a, b in zip(labels, labels[1:])]
    write_sidecar(args.sidecar, {
        "schema": SCHEMA, "source": str(args.source), "session": str(args.session),
        "out": str(out), "source_sha256": source_digest,
        "source_sha256_scope": "whole source file, digested in its own pass before pacing",
        "written_stream_sha256": out_digest.hexdigest(),
        "label_shift": args.label_shift, "label_shift_s": shift_s,
        "label_shift_basis": shift_basis, "archived_endpoint_epoch_s": endpoint,
        "interval_ms": args.interval_ms, "frames_written": written,
        "first_write_epoch_s": started_epoch_s, "first_write_monotonic_s": started_monotonic_s,
        # The three numbers that show the first-frame causality was honoured:
        # when the feeder started, how long after that frame 1 became visible,
        # and how much accumulation frame 1 claimed.  The second must not be
        # less than the third.
        "spawn_monotonic_s": spawn_monotonic_s,
        "first_write_delay_s": (labels[0] - spawn_monotonic_s) if written else None,
        "first_frame_elapsed_s": (writes[0] / 1e9) if written else None,
        # Lateness against the instant frame 1 was DUE (its own elapsed_ns
        # after spawn, or the `auto` wall target when that is later).  A slow
        # digest pre-pass -- ~55 ms here, but a cold or busy disk could exceed
        # the 257 ms first interval -- shows up as a positive number rather
        # than as a failure: the frame is simply written as soon as the
        # pre-pass ends, which is still no EARLIER than causality allows.
        "first_write_late_s": (max(0.0, labels[0] - first_due)) if written else None,
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
    # FIRST, before argument parsing and before the digest pre-pass: every
    # frame's due instant is measured from here, so anything charged to this
    # process before this line would be silently subtracted from frame 1's
    # own interval.
    spawn_monotonic_s = time.monotonic()
    args = parser().parse_args(sys.argv[1:] if argv is None else argv)
    if args.interval_ms <= 0:
        print("error: interval must be positive", file=sys.stderr)
        return 2
    try:
        return run(args, spawn_monotonic_s)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
