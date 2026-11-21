"""Dedicated process and publication boundary for the description looks."""

from __future__ import annotations

import argparse
from contextlib import suppress
import os
from pathlib import Path
import stat
import sys
import tempfile
import traceback
import warnings

from . import description as reader
from .manifest_dispatch import (
    PRE_READ_REFUSAL, exit_with_failure, finish_notice, save_public_stderr,
)
from .transfer_release import _failure_type, _redirect, _sync_directory


def _arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="stage", required=True)
    for stage in ("stage1", "stage2", "validate-public"):
        cmd = commands.add_parser(stage, allow_abbrev=False)
        cmd.add_argument("--repo", required=True, type=Path)
        cmd.add_argument("--look-id", required=True, choices=reader.IDS)
        if stage == "validate-public":
            cmd.add_argument("--candidate", required=True, type=Path)
    return parser.parse_args(argv)


def _write(stream, payload):
    stream.write(payload)
    stream.flush()
    os.fsync(stream.fileno())


def _write_private(path, payload):
    with path.open("xb") as stream:
        os.fchmod(stream.fileno(), stat.S_IRUSR | stat.S_IWUSR)
        _write(stream, payload)


def _stage1(snapshot, document):
    destination = snapshot.book.root / snapshot.stage_name
    reader.exact_path(destination.parent, directory=True)
    reader.require(not os.path.lexists(destination), "stage 1 already exists")
    with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".description-", delete=False) as stream:
        pending = Path(stream.name)
        try:
            _write(stream, reader.canonical(document))
            os.link(pending, destination, follow_symlinks=False)
        finally:
            pending.unlink()
    _sync_directory(destination.parent)


def _candidate(snapshot, path):
    path = reader.public_path(path.absolute())
    reader.require(reader._disjoint(path, snapshot.copy_root, snapshot.restricted.parent.parent),
                   "candidate path overlaps the scoring or custody root")
    return reader.decode(reader.exact_path(path).read_bytes())


def _failure(error, read_started, confined):
    if confined:
        with suppress(BaseException):
            traceback.print_exception(error)
    if read_started:
        return f"stage2_error\n{_failure_type(error)}\n"
    return "REFUSE description look before read\n"


def _public_after_scoring(snapshot, expected, prebound, prints):
    if not snapshot.instrument:
        return prebound
    mismatch = reader.missing(reader.INTERVAL_LEDGER_MISMATCH)
    mismatched = sum(hold == mismatch for hold in prints["hold"].values())
    if snapshot.input_files is None:
        reader.require(mismatched == 0, "interval mismatch requires the RL-194 public count")
        return prebound
    final = dict(expected, **{reader.INTERVAL_LEDGER_COUNT: mismatched})
    return snapshot.validate_public(final, final)


def main(argv=None):
    saved = None
    read_started = False
    confined = False

    def mark_read():
        nonlocal read_started
        read_started = True

    try:
        args = _arguments(argv)
        warnings.simplefilter("ignore")
        sys.warnoptions = []
        saved = save_public_stderr()
        if finish_notice(0, flush_streams=True):
            raise OSError("worker streams could not be flushed")
        snapshot = reader.Snapshot(args.repo.absolute(), args.look_id, args.stage)
        document, qualified = reader.census(snapshot)
        sources = reader.verify_gates(snapshot, qualified)
        if args.stage == "stage1":
            _stage1(snapshot, document)
            os._exit(0)

        snapshot.check_stage1(document)
        expected = snapshot.public_record(document)
        if args.stage == "validate-public":
            reader.require(snapshot.input_files is None, "mismatch count requires confined scoring")
            snapshot.validate_public(_candidate(snapshot, args.candidate), expected)
            os._exit(0)
        public_bytes = snapshot.validate_public(expected, expected)

        snapshot.restricted.mkdir(mode=0o700)
        _redirect(snapshot.restricted)
        confined = True
        _sync_directory(snapshot.restricted.parent)
        prints = reader.score(snapshot, sources, qualified, mark_read)
        public_bytes = _public_after_scoring(snapshot, expected, public_bytes, prints)
        for name, report in prints.items():
            _write_private(snapshot.restricted / f"{name}.json", reader.canonical(report))
        reader.require({path.name for path in snapshot.restricted.iterdir()}
                       == set(reader.private_names(snapshot.instrument)), "wrong custody inventory")
        pending = snapshot.restricted / ".publication"
        _write_private(pending, public_bytes)
        # The published record is public by contract. The pending file remains
        # within the reserved mode-0700 directory until the atomic publication.
        pending.chmod(0o644)
        if finish_notice(0, flush_streams=True):
            raise OSError("worker streams could not be flushed")
        reader.exact_path(snapshot.public.parent, directory=True)
        reader.require(not os.path.lexists(snapshot.public), "look already published")
        pending.rename(snapshot.public)
    except BaseException as error:
        status = 1 if read_started else PRE_READ_REFUSAL
        exit_with_failure(status, lambda: _failure(error, read_started, confined),
                          stderr_fd=saved, flush_streams=confined)
    os._exit(0)
