"""RL-183 transfer execution boundary for a dedicated worker after admission.

The caller supplies the admitted destinations, metadata preflight and scorer.
This module has no command line or way to discover real scoring inputs.
"""

from __future__ import annotations

import builtins
import json
import os
from pathlib import Path
import re
import sys
import traceback
import warnings

from .manifest_dispatch import PRE_READ_REFUSAL, finish_notice, redirect_to_devnull, save_public_stderr

CUSTODY_NAMES = frozenset(("scores.json", "stdout", "stderr"))
HASHES = ("manifest_sha256", "stage1_roster_sha256", "freeze2_sha256")
HASH_PATTERN = "[0-9a-f]{64}"
WORDS = {"transfer_interval": ("estimated", "not_evaluable"), "stage2_error": ("no",)}
POST_READ_FAILURE = 1

_BUILTIN_ERRORS = tuple(
    (candidate, name)
    for name, candidate in vars(builtins).items()
    if isinstance(candidate, type) and issubclass(candidate, BaseException)
    and candidate.__module__ == "builtins" and candidate.__name__ == name
)
_REFUSAL = "REFUSE transfer look before read\n"


def validate_public(record):
    if type(record) is not dict or record.keys() != set(HASHES) | WORDS.keys():
        raise ValueError("unexpected transfer public fields")
    for name, allowed in WORDS.items():
        if type(record[name]) is not str or record[name] not in allowed:
            raise ValueError(f"unexpected public word: {name}")
    for name in HASHES:
        if type(record[name]) is not str or re.fullmatch(HASH_PATTERN, record[name]) is None:
            raise ValueError(f"invalid public hash: {name}")


def _public_record(hashes, interval_status):
    record = {**hashes, "transfer_interval": interval_status, "stage2_error": "no"}
    validate_public(record)
    return record


def _failure_type(error):
    try:
        cls = type(error)
        if issubclass(cls, BaseException):
            if cls is json.JSONDecodeError:
                return "JSONDecodeError"
            if cls is getattr(sys.modules.get("numpy.linalg"), "LinAlgError", None):
                return "LinAlgError"
            for candidate, name in _BUILTIN_ERRORS:
                if cls is candidate:
                    return name
    except BaseException:
        pass
    return "OtherError"


def _write_json(path, record):
    payload = (json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _redirect(restricted):
    for fd, name in ((2, "stderr"), (1, "stdout")):
        stream = os.open(restricted / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.dup2(stream, fd)
        finally:
            os.close(stream)
        # A missing Python stream can be recreated after its descriptor is private.
        if getattr(sys, name) is None:
            setattr(sys, name, os.fdopen(fd, "w", encoding="utf-8", closefd=False))


def run_transfer_worker(*, restricted: Path, public: Path, execution_host: str, local_host: str,
                        ledger_status: str, preflight, score) -> int:
    """Run one look boundary in a worker whose process exits with the returned status.

    The caller binds the per-ID RESTRICTED and PUBLIC.json destinations and host from the admitted ledger.
    The blind preflight must prove all other gates and return exactly the three authenticated
    public hashes. Score returns (private result, primary interval status). It must call
    mark_read immediately upon opening its first scoring input, before consuming bytes,
    including when the shared coefficient reader opens that input. Nothing else may open
    scoring inputs. Once reserved, the worker keeps its streams confined through shutdown.
    """
    original_stderr = None
    try:
        warnings.simplefilter("ignore")
        sys.warnoptions = []
        original_stderr = save_public_stderr()
        redirect_to_devnull(2)
        if finish_notice(0, flush_streams=True):
            raise OSError("worker streams could not be flushed")
    except OSError:
        try:
            return finish_notice(PRE_READ_REFUSAL, stderr=_REFUSAL, stderr_fd=original_stderr)
        finally:
            if original_stderr is not None:
                os.close(original_stderr)
    read_started = False
    redirected = False

    def mark_read():
        nonlocal read_started
        read_started = True

    try:
        if not execution_host or execution_host != local_host or ledger_status != "stage1_committed":
            raise ValueError("host or ledger state refuses execution")
        if os.path.lexists(restricted) or os.path.lexists(public):
            raise FileExistsError("look ID is spent")
        if restricted.parent.stat().st_dev != public.parent.stat().st_dev:
            raise ValueError("atomic publication requires one filesystem")
        hashes = dict(preflight())
        if hashes.keys() != set(HASHES):
            raise ValueError("preflight must supply the exact public hash fields")
        _public_record(hashes, "not_evaluable")

        restricted.mkdir(mode=0o700)
        _redirect(restricted)
        redirected = True
        _sync_directory(restricted.parent)
        scores, interval_status = score(mark_read)
        if not read_started and interval_status == "estimated":
            raise ValueError("estimated interval requires a scoring input")
        record = _public_record(hashes, interval_status)
        _write_json(restricted / "scores.json", scores)
        if {path.name for path in restricted.iterdir()} != CUSTODY_NAMES:
            raise ValueError("unexpected transfer custody entries")
        pending = restricted / ".publication"
        _write_json(pending, record)
        if os.path.lexists(public):
            raise FileExistsError("look ID already has a public result")
        # The exclusive reservation admits only this publisher. Rename removes
        # the private staging name while exposing one complete public record.
        pending.rename(public)
        return 0
    except Exception as error:
        if redirected:
            try:
                traceback.print_exc()
            except Exception:
                pass
        if read_started:
            notice = f"stage2_error\n{_failure_type(error)}\n"
            return finish_notice(POST_READ_FAILURE, stderr=notice, stderr_fd=original_stderr)
        return finish_notice(PRE_READ_REFUSAL, stderr=_REFUSAL, stderr_fd=original_stderr)
    finally:
        os.close(original_stderr)
