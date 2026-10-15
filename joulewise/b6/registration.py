"""The parts of a pack registration read by acceptance; no custody layer."""

from __future__ import annotations

import json
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping
import math

SCHEMA = "joulewise.b6_acceptance_registration.v1"
# Stage-1 integration: the one block-6 registration directory of a measurement
# checkout, read by the pre-session check, the smoke desk and the session
# harvest alike: acceptance.json (this module's schema), identity_pins.json,
# and for the pre-session check sizing_b5.json and an optional
# precheck_thresholds.json. The registration seat writes it; for a replication
# the pins and sizing are copies of configs/campaigns/v5_claim_25g83's.
DEFAULT_DIR_RELATIVE = "configs/b6/registration"
IDENTITY_SCHEMA = "joulewise.b5_identity_pins.v1"
SIZING_SCHEMA = "joulewise.b5_sizing.v1"
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
    """Load complete acceptance values; callers record unavailable registrations."""
    try:
        return _load_acceptance(path)
    except (KeyError, TypeError, ArithmeticError) as exc:
        raise ValueError("acceptance registration is incomplete or malformed") from exc


def _load_acceptance(path: Path | str) -> dict[str, Any]:
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
    if not isinstance(cal, dict) or not isinstance(cal.get("acceptance_corpus"), list):
        raise ValueError("acceptance calibration or corpus is malformed")
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


def _document(path, filename, schema, key="schema"):
    target = Path(path)
    if target.is_dir():
        target /= filename
    value = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get(key) != schema:
        raise ValueError(f"{filename} schema is invalid")
    return value


def load_identity_pins(path: Path | str) -> dict:
    value = _document(path, "identity_pins.json", IDENTITY_SCHEMA)
    runtime, units = value.get("runtime_versions"), value.get("units")
    if (not isinstance(runtime, dict) or not isinstance(runtime.get("python"), str)
            or not isinstance(runtime.get("packages"), dict) or not isinstance(units, dict) or not units):
        raise ValueError("identity pins require runtime versions and model units")
    if any(not isinstance(k, str) or not isinstance(v, str) or not v
           for k, v in runtime["packages"].items()):
        raise ValueError("identity package versions must be nonempty strings")
    for unit in units.values():
        if (not isinstance(unit, dict) or not isinstance(unit.get("model_source"), str)
                or not unit["model_source"] or not isinstance(unit.get("model_artifact_sha256"), str)
                or len(unit["model_artifact_sha256"]) != 64
                or any(c not in "0123456789abcdef" for c in unit["model_artifact_sha256"])
                or not isinstance(unit.get("stack_identity"), dict)):
            raise ValueError("identity model unit is malformed")
    return value


def load_sizing(path: Path | str) -> dict:
    value = _document(path, "sizing_b5.json", SIZING_SCHEMA, "schema_version")
    packs = value.get("packs")
    if not isinstance(packs, dict) or not packs:
        raise ValueError("sizing packs are missing")
    for sized in packs.values():
        if not isinstance(sized, dict) or not isinstance(sized.get("pack_id"), str):
            raise ValueError("sizing pack identity is missing")
        for key in ("programmed_span_s", "T_stream_max_s"):
            seconds = sized.get(key)
            if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
                raise ValueError(f"sizing {key} must be finite and positive")
    return value


def load_precheck_thresholds(path: Path | str) -> dict:
    """Optional sparse overrides of the existing precheck contract; no new values."""
    from joulewise.b6.precheck import PRECHECK_DEFAULTS
    target = Path(path)
    if target.is_dir():
        target /= "precheck_thresholds.json"
    if not target.exists():
        return {}
    value = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) - set(PRECHECK_DEFAULTS):
        raise ValueError("precheck threshold object is invalid")
    for key, item in value.items():
        default = PRECHECK_DEFAULTS[key]
        if isinstance(default, dict):
            if not isinstance(item, dict) or set(item) - set(default):
                raise ValueError(f"precheck {key} thresholds are invalid")
            numbers = item.values()
        else:
            numbers = (item,)
        if any(type(number) not in (int, float) or not math.isfinite(number) or number < 0
               for number in numbers):
            raise ValueError("precheck thresholds must be finite nonnegative numbers")
    return value
