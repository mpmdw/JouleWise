"""Durable, sealed stage decisions and process ownership events."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time


# Every bundle path opened by analyze.py, including diagnostic-only inputs.
BUNDLE_FILES = ("summary_metrics.json", "metadata.json", "outputs/tokens.jsonl",
                "power_trace.csv", "events.jsonl")


def bundle_fingerprint(bundle: Path) -> dict:
    result = {}
    for name in BUNDLE_FILES:
        data = (bundle / name).read_bytes()
        result[name] = {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
    return result


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


def cell_entry(directory: Path, *, slot: int, arm: str, label: str,
               require_bundle_files: bool = False) -> dict:
    cell = json.loads((directory / "cell.json").read_text())
    runs = []
    for run in cell.get("runs", []):
        entry = {key: run.get(key) for key in ("run_id", "bundle", "materialized_sha256")}
        bundle = run.get("bundle")
        if bundle and require_bundle_files:
            entry["bundle_files"] = bundle_fingerprint(Path(bundle))
        elif bundle and all((Path(bundle) / name).is_file() for name in BUNDLE_FILES):
            entry["bundle_files"] = bundle_fingerprint(Path(bundle))
        elif require_bundle_files:
            raise ValueError(f"accepted run lacks analyzer bundle files: {bundle}")
        runs.append(entry)
    return {"slot": slot, "arm": arm, "dir": str(directory.resolve()), "label": label,
            "runs": runs}


def owned_tolerant(path: Path) -> tuple[dict[str, dict], list[str]]:
    """Recover all parseable ownership events without erasing damaged evidence."""
    if not path.exists():
        return {}, []
    pending, errors = {}, []
    raw = path.read_bytes()
    lines = raw.split(b"\n")
    for number, line in enumerate(lines, 1):
        if not line:
            if number != len(lines) or not raw.endswith(b"\n"):
                errors.append(f"invalid ownership line {number}: empty line")
            continue
        if number == len(lines) and not raw.endswith(b"\n"):
            errors.append(f"torn ownership line {number}: {path}")
            continue
        try:
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError("record is not an object")
            label, event = record["label"], record["event"]
            if not isinstance(label, str):
                raise ValueError("label is not a string")
            if event == "acquire":
                if label in pending or not isinstance(record.get("action"), dict):
                    raise ValueError("duplicate or invalid acquisition")
                pending[label] = record
            elif event == "update":
                if label not in pending:
                    raise ValueError("update without acquisition")
                pending[label].update(record)
            elif event == "release":
                if label not in pending:
                    raise ValueError("release without acquisition")
                del pending[label]
            else:
                raise ValueError("invalid ownership event")
        except (ValueError, KeyError, UnicodeDecodeError) as exc:
            errors.append(f"invalid ownership line {number}: {exc}")
    return pending, errors


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
