"""Pack and configuration offsets, used only at export and release."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PACK_RANGE = (0.8, 1.25)
CONFIG_RANGE = (0.97, 1.03)


def _draw(bounds: tuple[float, float]) -> float:
    return secrets.SystemRandom().uniform(*bounds)


def _stored_or_draw(directory: Path, name: str, bounds: tuple[float, float],
                    identity: Mapping, session_id: str | None) -> float:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    while True:
        try:
            return json.loads(path.read_text(encoding="utf-8"))["factor"]
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            # An exclusive creator has opened the file and is still writing.
            time.sleep(0.001)
            continue
        value = _draw(bounds)
        document = {**identity, "factor": value,
                    "distribution": {"name": "uniform", "low": bounds[0], "high": bounds[1]},
                    "drawn_utc": datetime.now(timezone.utc).isoformat(),
                    "drawn_by_session": session_id}
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        return value


def pack_factor(directory: Path | str, *, session_id: str | None = None) -> float:
    directory = Path(directory)
    return _stored_or_draw(directory, "pack.json", PACK_RANGE,
                           {"pack_id": directory.parent.name}, session_id)


def config_factor(directory: Path | str, key: str, *, session_id: str | None = None) -> float:
    name = "config-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16] + ".json"
    return _stored_or_draw(Path(directory), name, CONFIG_RANGE, {"key": key}, session_id)


def factor(directory: Path | str, key: str, *, session_id: str | None = None) -> float:
    return pack_factor(directory, session_id=session_id) * config_factor(directory, key, session_id=session_id)


def _condition_tag(config: Mapping[str, Any]) -> str | None:
    tags = config.get("run_metadata", {}).get("tags", []) if isinstance(config.get("run_metadata"), Mapping) else []
    for tag in tags if isinstance(tags, list) else []:
        if isinstance(tag, str) and tag.startswith("df-condition="):
            return tag.split("=", 1)[1]
    return None


def configuration_key(config: Mapping) -> str:
    tagged = _condition_tag(config)
    if tagged is not None:
        return tagged
    workload = config.get("workload_profile") or {}
    return "|".join(str(item) for item in ((config.get("model") or {}).get("name", ""),
                                         workload.get("name", ""),
                                         workload.get("output_tokens", config.get("output_tokens", ""))))


def _scale(row: Mapping, f: float, inverse: bool) -> dict:
    result = dict(row)
    for key, value in row.items():
        degree = 2 if key.endswith(("_j2", "_w2")) else 1 if key.endswith(("_j", "_w")) else 0
        if degree and value is not None and value != "":
            number = float(value)
            result[key] = number / f ** degree if inverse else number * f ** degree
    return result


def apply(row: Mapping, f: float) -> dict:
    return _scale(row, f, False)


def unblind(row: Mapping, f: float) -> dict:
    return _scale(row, f, True)
