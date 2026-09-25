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

HARNESS = Path(__file__).resolve().parent
ROOT = HARNESS.parents[2]


def file_fingerprint(path: Path) -> dict:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return {"sha256": digest.hexdigest(), "size": size}


def tree_manifest(directory: Path) -> dict:
    """Bind every regular file in a cell, including files unknown to the analyzer."""
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError(f"missing or linked cell directory: {directory}")
    result = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink() or (not path.is_file() and not path.is_dir()):
            raise ValueError(f"unsupported cell entry: {path}")
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = file_fingerprint(path)
    return result


def stage_binding(location: Path, config_path: Path, config: dict) -> dict:
    effective = file_fingerprint(config_path)
    if getattr(config, "loaded_path", None) == config_path.resolve() and \
            getattr(config, "loaded_fingerprint", effective) != effective:
        raise ValueError("effective config changed since load_config read it")
    source = Path(config["source_config"])
    if not source.is_absolute():
        source = ROOT / source
    return {
        "command_sequence": file_fingerprint(location / "command_sequence.json"),
        "config_path": str(config_path.resolve()),
        "config": effective,
        "harness": {path.name: file_fingerprint(path) for path in sorted(HARNESS.glob("*.py"))},
        "source_config_path": str(source.resolve()),
        "source_config": file_fingerprint(source),
    }


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
    cell_path = directory / "cell.json"
    if require_bundle_files and not cell_path.is_file():
        raise ValueError(f"accepted cell is missing cell.json: {directory}")
    cell = json.loads(cell_path.read_text()) if cell_path.is_file() else {}
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
            "runs": runs, "manifest": tree_manifest(directory)}


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
