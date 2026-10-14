"""Pack stopping from registered spreads and counts; public output is words only."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import math
import os
from pathlib import Path
import statistics

from joulewise.aggregate import student_t_critical_95

try:
    from joulewise.b6.blinding import PACK_FACTOR_RANGE, CONFIG_FACTOR_RANGE
except ImportError:
    # Design 16 item 3; merge item: repoint this import/key reader to b6.blinding.
    PACK_FACTOR_RANGE = (0.8, 1.25)
    CONFIG_FACTOR_RANGE = (0.97, 1.03)

PRECISION_SCHEMA = "joulewise.b6_precision_input.v1"


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def read_factor(key_dir: Path, config_id: str) -> float:
    """Read existing keys only; merge can repoint this function at blinding.factor."""
    try:
        digest = hashlib.sha256(config_id.encode("utf-8")).hexdigest()[:16]
        pack = json.loads((Path(key_dir) / "pack.json").read_text())["factor"]
        config = json.loads((Path(key_dir) / f"config-{digest}.json").read_text())["factor"]
        if (not _finite(pack) or not _finite(config)
                or not PACK_FACTOR_RANGE[0] <= pack <= PACK_FACTOR_RANGE[1]
                or not CONFIG_FACTOR_RANGE[0] <= config <= CONFIG_FACTOR_RANGE[1]):
            raise ValueError
        return pack * config
    except (OSError, ValueError, TypeError, KeyError):
        raise ValueError("precision_unavailable") from None


def between_sessions_half_width(values):
    if len(values) < 2 or not all(_finite(value) for value in values):
        raise ValueError("precision_unavailable")
    return student_t_critical_95(len(values) - 1) * statistics.stdev(values) / math.sqrt(len(values))


def validate_registration(registration):
    """Validate without echoing registration values into exception text."""
    try:
        stopping = registration["stopping"]
        for name in ("target_sessions", "min_sessions", "session_cap", "max_attempts"):
            if type(stopping[name]) is not int or stopping[name] < 1:
                raise ValueError
        if not stopping["min_sessions"] <= stopping["target_sessions"] <= stopping["session_cap"]:
            raise ValueError
        date.fromisoformat(stopping["end_date"])
        precision = stopping.get("precision")
        if precision is not None:
            if precision["scale"] not in ("keyed", "conservative"):
                raise ValueError
            quantities = precision["quantities"]
            if not isinstance(quantities, list) or not quantities:
                raise ValueError
            ids = set()
            for quantity in quantities:
                ident = quantity["id"]
                if not isinstance(ident, str) or not ident or ident in ids:
                    raise ValueError
                ids.add(ident)
                if quantity["interval"] not in ("reported", "between_sessions"):
                    raise ValueError
                if not _finite(quantity["half_width_j"]) or quantity["half_width_j"] <= 0:
                    raise ValueError
                # Missing/list config_id denotes an ineligible cross-config contrast.
                config_id = quantity.get("config_id")
                if config_id is not None and not isinstance(config_id, (str, list)):
                    raise ValueError
        return stopping
    except (KeyError, ValueError, TypeError, AttributeError):
        raise ValueError("unparsable registration") from None


def evaluate(registration, sessions, *, today: date, key_dir: Path | None = None):
    """sessions: ordered (structure record, precision record or None) pairs."""
    stopping = validate_registration(registration)
    pack_id = registration.get("pack_id", "UNKNOWN")
    counting_sessions = [(record, analysis) for record, analysis in sessions
                         if record.get("counting") is True]
    counting, attempts = len(counting_sessions), len(sessions)
    precision = stopping.get("precision")
    quantities, withheld = {}, {}
    for quantity in precision["quantities"] if precision else ():
        ident, config_id = quantity["id"], quantity.get("config_id")
        reached = "precision_unavailable"
        width = None
        k = counting
        df = counting - 1 if quantity["interval"] == "between_sessions" and counting >= 2 else None
        try:
            if not isinstance(config_id, str) or not config_id or not counting_sessions:
                raise ValueError
            inputs = []
            for structure, analysis in counting_sessions:
                if (not isinstance(analysis, dict) or analysis.get("schema") != PRECISION_SCHEMA
                        or analysis.get("pack_id") != pack_id):
                    raise ValueError
                expected_session = structure.get("session_id", structure.get("plan_id"))
                if expected_session is not None and analysis.get("session_id") != expected_session:
                    raise ValueError
                item = analysis["quantities"][ident]
                if item.get("config_id") != config_id:
                    raise ValueError
                inputs.append(item)
            if quantity["interval"] == "reported":
                width = inputs[-1]["half_width"]
            else:
                width = between_sessions_half_width([item["value"] for item in inputs])
            if not _finite(width) or width < 0:
                width = None
                raise ValueError
            if precision["scale"] == "keyed":
                if key_dir is None:
                    raise ValueError
                reached = width / read_factor(key_dir, config_id) <= quantity["half_width_j"]
            else:
                reached = width <= quantity["half_width_j"] * PACK_FACTOR_RANGE[0] * CONFIG_FACTOR_RANGE[0]
        except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
            reached = "precision_unavailable"
        quantities[ident] = {"reached": reached}
        withheld[ident] = {"blinded_half_width": width, "k": k, "df": df}
    short = False
    limit = "session_cap" if precision else "target_sessions"
    if counting >= stopping[limit]:
        decision, reason = "STOP_CAP", limit
    elif (precision and counting >= max(stopping["min_sessions"], 2)
          and all(row["reached"] is True for row in quantities.values())):
        decision, reason = "STOP_PRECISION", "registered_precision_reached"
    elif today > date.fromisoformat(stopping["end_date"]):
        decision, reason = "STOP_END_DATE", "end_date"
        short = counting < stopping["min_sessions"]
    elif attempts >= stopping["max_attempts"] and counting < stopping["target_sessions"]:
        decision, reason = "PAUSE_ATTEMPTS", "max_attempts"
    else:
        decision, reason = "CONTINUE", "target_pending"
    public = {"schema": "joulewise.b6_pack_stopping.v1", "pack_id": pack_id,
              "decision": decision, "reason": reason, "counting": counting, "attempts": attempts,
              "quantities": quantities, "date": today.isoformat(), "short": short}
    private = {"schema": "joulewise.b6_stopping_withheld.v1", "pack_id": pack_id,
               "quantities": withheld}
    return public, private


def stopping_line(record):
    reached = sum(row["reached"] is True for row in record["quantities"].values())
    return (f"pack={record['pack_id']} decision={record['decision']} counting={record['counting']} "
            f"attempts={record['attempts']} reached={reached}/{len(record['quantities'])}")


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.partial")
    temporary.write_text(json.dumps(value, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("registration", "sessions-dir", "record-dir"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    parser.add_argument("--key-dir", type=Path)
    parser.add_argument("--withheld-dir", type=Path)
    parser.add_argument("--precision-dir", type=Path,
                        help="optional analysis directory containing <session_id>.json; default: session/precision.json")
    args = parser.parse_args(argv)
    try:
        registration = _load(args.registration)
        validate_registration(registration)
    except (OSError, ValueError, TypeError):
        parser.error("unparsable registration")
    sessions = []
    try:
        for path in args.sessions_dir.rglob("structure.json"):
            record = _load(path)
            if record.get("pack_id") != registration.get("pack_id", "UNKNOWN"):
                continue
            attempt = record.get("attempt")
            if isinstance(attempt, str) and attempt.isdecimal():
                attempt = int(attempt)
            if type(attempt) is not int or attempt < 1:
                raise ValueError
            analysis = None
            if record.get("counting") is True and registration["stopping"].get("precision"):
                ident = record.get("session_id", record.get("plan_id", path.parent.name))
                if not isinstance(ident, str) or Path(ident).name != ident:
                    raise ValueError
                analysis_path = args.precision_dir / (ident + ".json") if args.precision_dir else path.parent / "precision.json"
                try:
                    analysis = _load(analysis_path)
                except (OSError, ValueError):
                    pass  # Missing or malformed analysis is a recorded unavailable precision.
            sessions.append((attempt, record, analysis))
        sessions.sort(key=lambda row: row[0])
        if len({row[0] for row in sessions}) != len(sessions):
            raise ValueError
    except (OSError, ValueError, TypeError, AttributeError):
        parser.error("unparsable session records")
    public, private = evaluate(registration, [(record, analysis) for _, record, analysis in sessions],
                               today=args.today, key_dir=args.key_dir)
    _write(args.record_dir / "stopping.json", public)
    _write((args.withheld_dir or args.record_dir / "withheld") / "stopping-withheld.json", private)
    print(stopping_line(public))
    return 0
