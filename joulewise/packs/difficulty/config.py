"""The DIFFICULTY pack's JSON configuration."""
import json
from pathlib import Path


def load_config(path):
    config = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("config must be a JSON object")
    config = {"confidence": 0.95, "exclude_flags": [],
              "exclude_importer_sets": True, "exclude_item_id_files": [], **config}
    for key in ("version", "seed"):
        if not isinstance(config.get(key), str) or not config[key]:
            raise ValueError(f"{key} must be a nonempty string")
    for key in ("n_per_level", "energy_per_level"):
        if type(config.get(key)) is not int or config[key] < 0:
            raise ValueError(f"{key} must be an integer >= 0")
    if not 0 < config["confidence"] < 1:
        raise ValueError("confidence must be between 0 and 1")
    if not isinstance(config.get("configurations"), list):
        raise ValueError("configurations must be a list")
    for entry in config["configurations"]:
        if not isinstance(entry, dict):
            raise ValueError("each configuration must be a JSON object")
        if not isinstance(entry.get("model"), str) or not entry["model"]:
            raise ValueError("configuration model must be a nonempty string")
        if entry.get("mode") not in ("off", "on"):
            raise ValueError("configuration mode must be off or on")
        if type(entry.get("output_cap")) is not int or entry["output_cap"] <= 0:
            raise ValueError("output_cap must be a positive integer")
    for key in ("exclude_flags", "exclude_item_id_files"):
        if not isinstance(config[key], list) or any(not isinstance(value, str) for value in config[key]):
            raise ValueError(f"{key} must be a list of strings")
    return config
