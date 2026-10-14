"""The DIFFICULTY v2 configuration; numeric policy has no defaults."""
import json
import math
from pathlib import Path


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError("config must be a JSON object")
    for key in ("confidence", "energy_per_level"):
        if key in config:
            raise ValueError(f"{key}: replaced in v2 by descriptive_confidence/decision_confidence and sizes")
    if config.get("schema_version") != "difficulty_config.v2":
        raise ValueError("schema_version must equal difficulty_config.v2")

    def string(value, key):
        if not isinstance(value, str) or not value:
            raise ValueError(f"{key} must be a nonempty string")

    def integer(value, key, minimum):
        if type(value) is not int or value < minimum:
            raise ValueError(f"{key} must be an integer >= {minimum}")

    def number(value, key, lower, upper, inclusive_upper=False):
        if (type(value) not in (int, float) or not lower < value
                or (value > upper if inclusive_upper else value >= upper) or not math.isfinite(value)):
            raise ValueError(f"{key} must be in ({lower}, {upper}{']' if inclusive_upper else ')'}")

    def strings(value, key):
        if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            raise ValueError(f"{key} must be a list of strings")

    def object_keys(value, key, keys):
        if not isinstance(value, dict) or set(value) != set(keys):
            raise ValueError(f"{key} must have exactly {', '.join(keys)}")

    for key in ("version", "seed"):
        string(config.get(key), key)
    integer(config.get("n_per_level"), "n_per_level", 1)
    sizes = config.get("sizes")
    object_keys(sizes, "sizes", ("off", "on"))
    for mode in ("off", "on"):
        object_keys(sizes[mode], f"sizes.{mode}", ("bench", "energy"))
        for role in ("bench", "energy"):
            object_keys(sizes[mode][role], f"sizes.{mode}.{role}", tuple(map(str, range(1, 6))))
            for level, value in sizes[mode][role].items():
                integer(value, f"sizes.{mode}.{role}.{level}", 0)
        for level in map(str, range(1, 6)):
            if not 0 <= sizes[mode]["energy"][level] <= sizes[mode]["bench"][level] <= config["n_per_level"]:
                raise ValueError(f"sizes.{mode}.{level} must satisfy 0 <= energy <= bench <= n_per_level")
    boundaries = config.get("boundaries")
    strings(boundaries, "boundaries")
    if not boundaries or len(set(boundaries)) != len(boundaries):
        raise ValueError("boundaries must be nonempty and distinct")
    roster = config.get("configurations")
    if not isinstance(roster, list):
        raise ValueError("configurations must be a list")
    identifiers = set()
    for entry in roster:
        if not isinstance(entry, dict):
            raise ValueError("configurations entries must be objects")
        string(entry.get("model"), "configurations.model")
        if entry.get("mode") not in ("off", "on"):
            raise ValueError("configurations.mode must be off or on")
        integer(entry.get("output_cap"), "configurations.output_cap", 1)
        if entry.get("status") not in ("measured", "optional"):
            raise ValueError("configurations.status must be measured or optional")
        identifier = entry["model"] + "/" + entry["mode"]
        if identifier in identifiers:
            raise ValueError("configurations identifiers must be distinct")
        identifiers.add(identifier)
    comparison = config.get("primary_comparison")
    if not isinstance(comparison, dict):
        raise ValueError("primary_comparison must be an object")
    for key in ("a", "b"):
        if not isinstance(comparison.get(key), str) or comparison[key] not in identifiers:
            raise ValueError(f"primary_comparison.{key} must be in configurations")
    if comparison["a"] == comparison["b"]:
        raise ValueError("primary_comparison.a and primary_comparison.b must be distinct")
    for key in ("descriptive_confidence", "decision_confidence"):
        number(config.get(key), key, 0.5, 1)
    bootstrap = config.get("bootstrap")
    if not isinstance(bootstrap, dict):
        raise ValueError("bootstrap must be an object")
    string(bootstrap.get("seed"), "bootstrap.seed")
    integer(bootstrap.get("replicates"), "bootstrap.replicates", 20)
    for key in ("exclude_flags", "physical_exclude_flags", "exclude_item_id_files"):
        strings(config.get(key), key)
    if set(config["exclude_flags"]) & set(config["physical_exclude_flags"]):
        raise ValueError("physical_exclude_flags and exclude_flags must have empty intersection")
    if type(config.get("exclude_importer_sets")) is not bool:
        raise ValueError("exclude_importer_sets must be a boolean")
    loop = config.get("loop_detector")
    if not isinstance(loop, dict):
        raise ValueError("loop_detector must be an object")
    number(loop.get("tail_fraction"), "loop_detector.tail_fraction", 0, 1, True)
    integer(loop.get("min_span"), "loop_detector.min_span", 1)
    integer(loop.get("min_repeats"), "loop_detector.min_repeats", 2)
    return config


def load_config(path):
    return validate_config(json.loads(Path(path).expanduser().read_text(encoding="utf-8")))
