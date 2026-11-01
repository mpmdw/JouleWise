"""Stream budget records and keep each immutable power trace once in a sidecar.

In-memory trials still contain ordinary shared Episodes. The compact disk format
uses trace references; read_result restores shared Episodes for attribution.
The shared records.to_json API remains a fully materialized compatibility view.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, TextIO, TYPE_CHECKING

if TYPE_CHECKING:
    from joulewise.align.budget.run import MatrixResult

from joulewise.align.records import Episode, PowerTrace, from_json, to_json


class TraceStore:
    """Content-addressed JSONL trace store shared by all records in one export."""

    def __init__(self, path: Path | None):
        self.path = path
        self.traces: dict[str, PowerTrace] = {}
        self.flags: list[str] = []
        self.references: dict[int, tuple[PowerTrace, str]] = {}
        if path is not None and path.exists():
            try:
                with path.open(encoding="utf-8") as handle:
                    for line in handle:
                        try:
                            entry = json.loads(line)
                            trace = from_json(PowerTrace, json.dumps(entry["trace"]))
                            if hashlib.sha256(to_json(trace).encode()).hexdigest() != entry["id"]:
                                raise ValueError("trace digest mismatch")
                            self.traces[entry["id"]] = trace
                        except (KeyError, ValueError, TypeError):
                            self.flags.append("trace_store_line_invalid")
            except OSError as exc:
                self.flags.append(f"trace_store_read_error:{type(exc).__name__}")

    def default(self, value: Any) -> Any:
        if isinstance(value, PowerTrace):
            cached = self.references.get(id(value))
            key = cached[1] if cached is not None and cached[0] is value else None
            if key is None:
                raw = to_json(value)
                key = hashlib.sha256(raw.encode()).hexdigest()
                if key not in self.traces:
                    if self.path is not None:
                        self.path.parent.mkdir(parents=True, exist_ok=True)
                        needs_newline = self.path.exists() and self.path.stat().st_size > 0
                        if needs_newline:
                            with self.path.open("rb") as handle:
                                handle.seek(-1, 2)
                                needs_newline = handle.read(1) != b"\n"
                        with self.path.open("a", encoding="utf-8") as handle:
                            if needs_newline:
                                handle.write("\n")
                            handle.write('{"id":' + json.dumps(key) + ',"trace":' + raw + '}\n')
                            handle.flush()
                    self.traces[key] = value
                self.references[id(value)] = (value, key)
            return {"$trace": key}
        if is_dataclass(value):
            # Return only the next object's fields, never recursively build
            # the entire matrix's Python/JSON representation.
            return {f.name: getattr(value, f.name) for f in fields(value)}
        raise TypeError(f"cannot serialize {type(value).__name__}")

    def expand(self, value: Any) -> Any:
        if isinstance(value, dict):
            if set(value) == {"$trace"}:
                trace = self.traces[value["$trace"]]
                return {f.name: getattr(trace, f.name) for f in fields(trace)}
            return {k: self.expand(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.expand(v) for v in value]
        return value

    def dump(self, value: Any, handle: TextIO) -> None:
        json.dump(value, handle, default=self.default, sort_keys=True,
                  separators=(",", ":"), allow_nan=False)


def write_result(path: Path, result: MatrixResult) -> None:
    """Stream result.json; referenced traces live beside it in result.traces.jsonl."""
    path = Path(path)
    trace_path = path.with_suffix(".traces.jsonl")
    store = TraceStore(trace_path)
    payload = {f.name: getattr(result, f.name) for f in fields(result)}
    payload["trace_file"] = trace_path.name
    with path.open("w", encoding="utf-8") as handle:
        store.dump(payload, handle)
        handle.write("\n")


def read_result(path: Path) -> MatrixResult:
    """Hydrate a compact export or a legacy fully materialized MatrixResult."""
    from joulewise.align.budget.run import MatrixResult

    path = Path(path)
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    trace_file = payload.pop("trace_file", None)
    if trace_file is not None:
        # Exports refer only to a sibling file, never an arbitrary path.
        if Path(trace_file).name != trace_file:
            raise ValueError("trace_file must be a sibling filename")
        payload = TraceStore(path.with_name(trace_file)).expand(payload)
    return from_json(MatrixResult, json.dumps(payload))


def read_trial_episode(path: Path, trial_id: str) -> Episode:
    """Read an ordinary shared Episode from a compact result export."""
    return next(t.episode for t in read_result(path).trials if t.trial_id == trial_id)


def write_episode_views(path: Path, episodes: Iterable[Episode], *,
                        trace_file: str = "result.traces.jsonl") -> None:
    """Stream Episode views referencing the result's shared trace sidecar."""
    path = Path(path)
    store = TraceStore(path.with_name(trace_file))
    with path.open("w", encoding="utf-8") as handle:
        for episode in episodes:
            store.dump({"episode": episode, "trace_file": trace_file}, handle)
            handle.write("\n")


def read_episode_views(path: Path) -> Iterator[Episode]:
    """Yield hydrated shared Episodes from compact JSONL, one record at a time."""
    path = Path(path)
    stores: dict[str, TraceStore] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            entry = json.loads(line)
            name = entry["trace_file"]
            if Path(name).name != name:
                raise ValueError("trace_file must be a sibling filename")
            if name not in stores:
                stores[name] = TraceStore(path.with_name(name))
            yield from_json(Episode, json.dumps(stores[name].expand(entry["episode"])))
