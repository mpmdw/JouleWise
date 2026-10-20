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
DECODE_RETRY_TIMEOUT_S = 5.0


def _draw(bounds: tuple[float, float]) -> float:
    return secrets.SystemRandom().uniform(*bounds)


def _stored_or_draw(directory: Path, name: str, bounds: tuple[float, float],
                    identity: Mapping, session_id: str | None) -> float:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    deadline = time.monotonic() + DECODE_RETRY_TIMEOUT_S
    while True:
        try:
            return json.loads(path.read_text(encoding="utf-8"))["factor"]
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            # An exclusive creator has opened the file and is still writing.
            if time.monotonic() >= deadline:
                raise ValueError(f"blinding key unreadable: {path}") from None
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


# R5 fixes these three 4-bit models as the fit set; all other science
# configurations are held out. Addendum 3.1 releases NEG-8 with the fit set.
FIT_MODELS = frozenset({"Qwen3-1.7B-4bit", "Qwen3-4B-4bit", "Qwen3-8B-4bit"})
REFERENCE_KEY = "neg8_reference"


def configuration_stage(config: Mapping) -> str:
    return "fit" if (config.get("model") or {}).get("name") in FIT_MODELS else "heldout"


def registered_keys(registrations_root: Path | str, group: str, project_root: Path | str) -> dict[str, str]:
    """Configuration membership comes from the group's registered modules."""
    keys = {}
    for path in sorted(Path(registrations_root).glob("*/registration.json")):
        registration = json.loads(path.read_text(encoding="utf-8"))
        if registration.get("blinding_group") != group:
            continue
        keys[REFERENCE_KEY] = "fit"
        for module in registration.get("modules", []):
            for relative in module.get("config_dirs", []):
                directory = Path(project_root) / relative
                for config_path in sorted(directory.glob("*.json")):
                    config = json.loads(config_path.read_text(encoding="utf-8"))
                    # Config directories also contain collection-plan metadata;
                    # only run configurations define releasable identities.
                    if not (config.get("model") or {}).get("name"):
                        continue
                    key = configuration_key(config)
                    stage = configuration_stage(config)
                    if key in keys and keys[key] != stage:
                        raise ValueError("blinding configuration has conflicting release stages")
                    keys[key] = stage
    return keys


def withheld_path(key_dir: Path, pack_id: str, session_id: str) -> Path:
    """The withheld store stays under the same custody root as the group keys."""
    for identity in (pack_id, session_id):
        if not isinstance(identity, str) or identity in (".", "..") or Path(identity).name != identity:
            raise ValueError("blinding withheld identity must be one path component")
    path = key_dir.parent / "withheld" / pack_id / (session_id + ".runs.csv")
    if not path.resolve().is_relative_to(key_dir.parent.resolve()):
        raise ValueError("blinding withheld path escapes group custody")
    return path


def key_directory(pack_records_root: Path | str, pack_id: str, registration: Mapping) -> Path:
    """C6 custody: grouped packs share keys; replication paths stay unchanged."""
    identity = registration.get("blinding_group") or pack_id
    if not isinstance(identity, str) or identity in (".", "..") or Path(identity).name != identity:
        raise ValueError("blinding key directory must be one records-root child")
    root = Path(pack_records_root).resolve()
    directory = Path(pack_records_root) / identity / "blinding"
    if not directory.resolve().is_relative_to(root):
        raise ValueError("blinding key directory escapes records root")
    return directory


def pack_factor(directory: Path | str, *, session_id: str | None = None) -> float:
    directory = Path(directory)
    return _stored_or_draw(directory, "pack.json", PACK_RANGE,
                           {"pack_id": directory.parent.name}, session_id)


def config_factor(directory: Path | str, key: str, *, session_id: str | None = None) -> float:
    return _stored_or_draw(Path(directory), _config_filename(key), CONFIG_RANGE, {"key": key}, session_id)


def _config_filename(key: str) -> str:
    return "config-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16] + ".json"


def stored_factor(directory: Path | str, key: str) -> float:
    """Read both existing keys for release; never draw or create a file."""
    values = []
    for name in ("pack.json", _config_filename(key)):
        path = Path(directory) / name
        try:
            value = json.loads(path.read_text(encoding="utf-8"))["factor"]
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 < value < float("inf"):
                raise ValueError
        except (OSError, ValueError, KeyError, TypeError):
            raise ValueError(f"blinding key missing or unreadable: {path}") from None
        values.append(value)
    return values[0] * values[1]


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
