"""The block-6 session index: where each session's bytes are, tied by digest.

Block 5's window index (``joulewise.b5_window_index.v1``) names one window per
pack under block-5 pins and cannot name block-6 sessions.  This index lists
every session of the loop's acceptance census (design §4.4).  A session's
paths come from its session record (``sessions/<id>/session.json``, written
by ``joulewise.b6.driver_lane``), because a re-harvest moves the archive to
``archive.reharvest-<n>`` (design §1); without a record, the loop's layout
(``joulewise.b6.session_paths.for_session``, S-2) locates it.  Each row binds
the SHA-256 of the archive's ``harvest.json`` and of its acceptance record
``derived/b6-acceptance.json``; the index binds the two loop files the census
was read from, so a stale index is refused.

Building the index hashes those files and reads no field of them.  The index
itself is structure: identities, rounds, counting, paths and digests.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from joulewise.b6 import session_paths
from joulewise.b6.analysis.census import load_census, structure_record

INDEX_SCHEMA = "joulewise.b6_session_index.v1"
HARVEST_RECORD = "harvest.json"
ACCEPTANCE_RECORD = "derived/b6-acceptance.json"
SESSION_RECORD = "session.json"


class IndexRefusal(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _sha(path: Path) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except FileNotFoundError:
        return None


def _locations(measurement: Path, loop_root: Path, session_id: str, block_root: Path | None) -> dict:
    try:
        layout = session_paths.for_session(measurement, loop_root, session_id, block_root=block_root)
    except ValueError:
        raise IndexRefusal("session_path_invalid") from None
    record_path = layout.archive.parent / SESSION_RECORD
    paths = {"archive": layout.archive, "custody": layout.custody}
    runs_roots: list[str] = []
    if record_path.exists():
        try:
            record = json.loads(record_path.read_bytes())
            paths = {key: Path(record["paths"][key]) for key in ("archive", "custody")}
            runs_roots = [str(root) for root in record.get("runs_roots") or []]
        except (OSError, ValueError, KeyError, TypeError):
            raise IndexRefusal("session_record_unreadable") from None
    return {"archive_root": str(paths["archive"]), "custody_root": str(paths["custody"]),
            "runs_roots": runs_roots, "session_record_sha256": _sha(record_path),
            "session_record": str(record_path)}


def build_session_index(loop_root: Path, *, measurement: Path, block_root: Path | None = None) -> dict:
    loop_root = Path(loop_root)
    census = load_census(loop_root)
    sessions = []
    for entry, row in zip(census.entries, structure_record(census)["sessions"]):
        where = _locations(measurement, loop_root, entry.session_id, block_root)
        archive = Path(where["archive_root"])
        harvest, acceptance = _sha(archive / HARVEST_RECORD), _sha(archive / ACCEPTANCE_RECORD)
        if entry.decided and (harvest is None or acceptance is None):
            raise IndexRefusal("harvest_record_absent" if harvest is None else "acceptance_record_absent")
        sessions.append({**row, **where, "claim_runs_root": str(archive / "sources/claim-runs"),
                         "compression_record": str(archive) + ".desk/compression.jsonl",
                         "harvest_record_sha256": harvest if entry.decided else None,
                         "acceptance_record_sha256": acceptance if entry.decided else None})
    return {"schema_version": INDEX_SCHEMA, "loop_root": str(loop_root.resolve()),
            "measurement": str(Path(measurement).resolve()),
            "attempts_sha256": _sha(loop_root / "attempts.jsonl"), "state_sha256": _sha(loop_root / "state.json"),
            "closed": census.closed, "sessions": sessions}


def load_session_index(path: Path, *, loop_root: Path | None = None) -> dict:
    """Read an index and re-check every digest it binds."""
    try:
        index = json.loads(Path(path).read_bytes())
        if index["schema_version"] != INDEX_SCHEMA or not isinstance(index["sessions"], list):
            raise ValueError()
        rows = [(Path(row["archive_root"]), row["harvest_record_sha256"], row["acceptance_record_sha256"],
                 Path(row["session_record"]), row["session_record_sha256"]) for row in index["sessions"]]
    except (OSError, ValueError, KeyError, TypeError):
        raise IndexRefusal("session_index_malformed") from None
    for archive, harvest, acceptance, record, record_sha in rows:
        if harvest is not None and _sha(archive / HARVEST_RECORD) != harvest:
            raise IndexRefusal("session_index_digest_mismatch")
        if acceptance is not None and _sha(archive / ACCEPTANCE_RECORD) != acceptance:
            raise IndexRefusal("session_index_digest_mismatch")
        if _sha(record) != record_sha:
            raise IndexRefusal("session_index_digest_mismatch")
    if loop_root is not None:
        loop_root = Path(loop_root)
        if (index.get("attempts_sha256") != _sha(loop_root / "attempts.jsonl")
                or index.get("state_sha256") != _sha(loop_root / "state.json")):
            raise IndexRefusal("session_index_stale")
    return index
