"""The block-6 session index: where each session's bytes are, tied by digest.

Block 5's window index (``joulewise.b5_window_index.v1``) names one window per
pack under block-5 pins and cannot name block-6 sessions.  This index lists
every session of the loop's acceptance census and locates it with the
session loop's own layout (``joulewise.b6.session_paths.for_session``, S-2):
its harvest archive, the archive's copy of the claim runs, and the SHA-256 of
the archive's ``harvest.json``.  It also binds the digests of the two loop
files the census was read from, so a stale index is refused.

Building the index hashes ``harvest.json`` and reads no field of it.  The
index itself is structure: identities, rounds, counting, paths and digests.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from joulewise.b6 import session_paths
from joulewise.b6.analysis.census import load_census, structure_record

INDEX_SCHEMA = "joulewise.b6_session_index.v1"
HARVEST_RECORD = "harvest.json"


class IndexRefusal(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _sha(path: Path) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except FileNotFoundError:
        return None


def build_session_index(loop_root: Path, *, measurement: Path, block_root: Path | None = None) -> dict:
    loop_root = Path(loop_root)
    census = load_census(loop_root)
    sessions = []
    for entry, row in zip(census.entries, structure_record(census)["sessions"]):
        try:
            paths = session_paths.for_session(measurement, loop_root, entry.session_id, block_root=block_root)
        except ValueError:
            raise IndexRefusal("session_path_invalid") from None
        digest = _sha(paths.archive / HARVEST_RECORD) if entry.decided else None
        if entry.decided and digest is None:
            raise IndexRefusal("harvest_record_absent")
        sessions.append({**row, "archive_root": str(paths.archive),
                         "claim_runs_root": str(paths.archive / "sources/claim-runs"),
                         "harvest_record_sha256": digest})
    return {"schema_version": INDEX_SCHEMA, "loop_root": str(loop_root.resolve()),
            "attempts_sha256": _sha(loop_root / "attempts.jsonl"), "state_sha256": _sha(loop_root / "state.json"),
            "closed": census.closed, "sessions": sessions}


def load_session_index(path: Path, *, loop_root: Path | None = None) -> dict:
    """Read an index and re-check every digest it binds."""
    try:
        index = json.loads(Path(path).read_bytes())
        if index["schema_version"] != INDEX_SCHEMA or not isinstance(index["sessions"], list):
            raise ValueError()
        rows = [(row["session_id"], Path(row["archive_root"]), row["harvest_record_sha256"]) for row in index["sessions"]]
    except (OSError, ValueError, KeyError, TypeError):
        raise IndexRefusal("session_index_malformed") from None
    for _, archive, digest in rows:
        if digest is not None and _sha(archive / HARVEST_RECORD) != digest:
            raise IndexRefusal("session_index_digest_mismatch")
    if loop_root is not None:
        loop_root = Path(loop_root)
        if (index.get("attempts_sha256") != _sha(loop_root / "attempts.jsonl")
                or index.get("state_sha256") != _sha(loop_root / "state.json")):
            raise IndexRefusal("session_index_stale")
    return index
