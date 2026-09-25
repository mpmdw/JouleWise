"""Durable, sealed stage decisions and process ownership events."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time


def canonical(record: dict) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def append(path: Path, record: dict, *, sealed: bool = False) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {**record, "wall_ns": time.time_ns()}
    if sealed:
        record["seal"] = hashlib.sha256(canonical(record)).hexdigest()
    with path.open("ab") as stream:
        stream.write(canonical(record) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    return record


def read(path: Path, *, sealed: bool = False) -> list[dict]:
    if not path.is_file():
        raise ValueError(f"missing ledger: {path}")
    raw = path.read_bytes()
    if not raw or not raw.endswith(b"\n"):
        raise ValueError(f"ledger has incomplete final line: {path}")
    records = []
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError("record is not an object")
            if sealed:
                seal = record.pop("seal")
                if seal != hashlib.sha256(canonical(record)).hexdigest():
                    raise ValueError("seal mismatch")
                record["seal"] = seal
            records.append(record)
        except (ValueError, KeyError, UnicodeDecodeError) as exc:
            raise ValueError(f"invalid ledger line {number}: {exc}") from exc
    return records


def cell_entry(directory: Path, *, slot: int, arm: str, label: str) -> dict:
    cell = json.loads((directory / "cell.json").read_text())
    return {"slot": slot, "arm": arm, "dir": str(directory.resolve()), "label": label,
            "runs": [{key: run.get(key) for key in ("run_id", "bundle", "materialized_sha256")}
                     for run in cell.get("runs", [])]}


def owned(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    pending = {}
    for record in read(path):
        if record.get("event") == "acquire":
            if record["label"] in pending:
                raise ValueError(f"duplicate ownership: {record['label']}")
            pending[record["label"]] = record
        elif record.get("event") == "update":
            if record["label"] not in pending:
                raise ValueError(f"ownership update without acquire: {record['label']}")
            pending[record["label"]].update(record)
        elif record.get("event") == "release":
            if record["label"] not in pending:
                raise ValueError(f"ownership release without acquire: {record['label']}")
            del pending[record["label"]]
        else:
            raise ValueError("invalid ownership event")
    return pending
