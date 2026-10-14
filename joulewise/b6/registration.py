"""The parts of a pack registration read by acceptance; no custody layer."""

from __future__ import annotations

import json
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "joulewise.b6_acceptance_registration.v1"
NUMBER_BEARING_PATHS = (
    "joulewise/adapters/mlx_runtime.py", "joulewise/adapters/powermetrics.py",
    "joulewise/reduce.py", "joulewise/powermetrics_fiducial.py",
    "joulewise/controller.py", "joulewise/clock.py", "joulewise/kernel_clock.py",
    "joulewise/idle_admission.py", "joulewise/bundle.py", "joulewise/suite.py",
    "scripts/run_campaign.py", "joulewise/b5/driver.py", "joulewise/b5/chain.py",
)
DEFAULTS = {
    "catalog": "configs/b6/flag_catalog_b6.json",
    "neg8": {"corpus_minimum": 6, "corpus_cap": 12,
             "planned": {"start": 3, "midpoint": 1, "end": 3}},
    "cell_unit_minimum": 5,
    "number_bearing_paths": list(NUMBER_BEARING_PATHS),
    "reviewed_commits_path": "configs/b6/executing_reviews.json",
}


def decimal_s(value: Any) -> Decimal:
    """Finite nonnegative time, preserving a JSON number's decimal lexeme."""
    if isinstance(value, bool):
        raise ValueError("registration time must be a number")
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError("registration time must be finite and nonnegative")
    return result


def load(path: Path | str) -> dict[str, Any]:
    target = Path(path)
    if target.is_dir():
        target /= "acceptance.json"
    value = json.loads(target.read_text(encoding="utf-8"), parse_float=Decimal)
    if not isinstance(value, dict) or value.get("schema", value.get("schema_version")) != SCHEMA:
        raise ValueError("acceptance registration schema is invalid")
    for key in ("pack_id", "registered_commit"):
        if not isinstance(value.get(key), str) or not value[key]:
            raise ValueError("acceptance registration identity is missing")
    used: list[str] = []

    def defaults(dst: dict, src: Mapping, prefix: str = "") -> None:
        for key, default in src.items():
            if key not in dst:
                dst[key] = deepcopy(default)
                used.append(prefix + key)
            elif isinstance(default, dict):
                if not isinstance(dst[key], dict):
                    raise ValueError("acceptance registration object is malformed")
                defaults(dst[key], default, prefix + key + ".")

    defaults(value, DEFAULTS)
    cal = value["calibration"]
    defaults(cal, {"operative_bound_stop_s": None})
    for key in ("alignment_reference_s", "bracket_screen_s", "max_budgetable_drift_s"):
        cal[key] = decimal_s(cal[key])
    if cal["operative_bound_stop_s"] is not None:
        cal["operative_bound_stop_s"] = decimal_s(cal["operative_bound_stop_s"])
    cal["acceptance_corpus"] = [decimal_s(item) for item in cal["acceptance_corpus"]]
    for key in ("corpus_minimum", "corpus_cap"):
        if type(value["neg8"][key]) is not int or value["neg8"][key] < 2:
            raise ValueError("NEG8 corpus count is invalid")
    if value["neg8"]["corpus_cap"] < value["neg8"]["corpus_minimum"]:
        raise ValueError("NEG8 corpus cap is below minimum")
    for count in value["neg8"]["planned"].values():
        if type(count) is not int or count < 0:
            raise ValueError("NEG8 planned count is invalid")
    if type(value["cell_unit_minimum"]) is not int or value["cell_unit_minimum"] < 5:
        raise ValueError("cell unit minimum cannot lower the registered estimator minimum")
    value["defaults_used"] = sorted(used)
    return value
