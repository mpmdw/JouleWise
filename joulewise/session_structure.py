"""Structure-only desk record; no member contents or energy records are opened."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import re

from joulewise.flags.schema import BLINDINGS, KLASSES

PHYSICS_STOP_REASONS = ("clock", "battery", "thermal", "contention", "disk", "sampler", "agent-pause-budget")
REQUIRED_RECORDS = ("harvest.json", "derived/yield.json", "derived/roster.json",
                    "derived/exclusions.json", "derived/flags.jsonl", "night/chain-stages.jsonl",
                    "night/result.json", "instrument_validation/opening", "instrument_validation/closing")
REQUIRED_MEMBER_FILES = ("metadata.json", "summary_metrics.json", "events.jsonl",
                         "power_trace.csv", "raw/powermetrics.plist")
COUNT_FIELDS = ("planned", "present", "raw_valid", "succeeded")
HARVEST_VERDICTS = ("COLLECTED", "NO_COLLECTION", "NULL", "HARVEST_FAULT")


def _physical(reason):
    if not isinstance(reason, str):
        return None
    word = reason.lower().replace("_", "-")
    return next((item for item in PHYSICS_STOP_REASONS
                 if word == item or re.match(re.escape(item) + r"[.\s:-]", word)), None)


def _number(value):
    return value if type(value) in (int, float) and math.isfinite(value) else None


def _count(value):
    return value if type(value) is int and value >= 0 else 0


def _json(path, invalid):
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError
        return value
    except (OSError, ValueError):
        invalid.append(path.name)
        return {}


def _lines(path, invalid):
    if not path.is_file():
        return []
    try:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if any(not isinstance(row, dict) for row in rows):
            raise ValueError
        return rows
    except (OSError, ValueError):
        invalid.append(path.name)
        return []


def _captures(roots, role):
    tokens = ("opening", "pre", "start") if role == "opening" else ("closing", "post", "end")
    for root in roots:
        for parent in root.rglob("instrument_validation") if root.exists() else ():
            if parent.is_dir():
                for child in parent.iterdir():
                    if child.is_dir() and any(token in child.name.lower().replace("-", "_").split("_")
                                               for token in tokens):
                        return True
    return False


def _bundle(member, roots):
    # The block-5 derived roster contains run_id, not a bundle locator.
    run_id = member.get("run_id")
    if not isinstance(run_id, str) or not run_id or Path(run_id).name != run_id:
        return None
    for root in roots:
        direct = root / run_id
        if direct.is_dir():
            return direct
        for match in root.rglob(run_id) if root.exists() else ():
            if match.is_dir():
                return match
    return None


def check(*, archive: Path, custody: Path, registration: dict, harvest_rc=0,
          runs_roots=(), previous=(), handover_record: Path | None = None,
          attempt: int | None = None, session_id: str | None = None):
    """Return the public structure record, reading only the named desk inputs."""
    archive, custody = Path(archive), Path(custody)
    invalid = []
    harvest = _json(archive / "harvest.json", invalid)
    yielded = _json(archive / "derived/yield.json", invalid)
    roster = _json(archive / "derived/roster.json", invalid)
    exclusions = _json(archive / "derived/exclusions.json", invalid)
    flags = _lines(archive / "derived/flags.jsonl", invalid)
    stages = _lines(custody / "night/chain-stages.jsonl", invalid)
    result = _json(custody / "night/result.json", invalid)
    started = _json(custody / "night/chain.started", invalid)
    exited = _json(custody / "night/chain.exited", invalid)
    structure = registration.get("structure", {})
    physical = _physical(result.get("aborted_reason"))
    roots = [Path(path) for path in runs_roots] or [archive / "sources/claim-runs", archive / "sources/bound-runs"]
    roots += [custody]
    defects = []
    terminal = custody / "night/result.json"
    if not terminal.is_file():
        defects.append("terminal_record_missing")
    if not physical and (any(_number(row.get("rc")) not in (None, 0) for row in stages)
                         or _number(exited.get("rc", exited.get("exit_code"))) not in (None, 0)):
        defects.append("chain_crashed")
    for name in structure.get("required_records", REQUIRED_RECORDS):
        if name in ("instrument_validation/opening", "instrument_validation/closing"):
            exists = _captures(roots, name.rsplit("/", 1)[1])
        else:
            exists = ((custody if name.startswith("night/") else archive) / name).exists()
        if not exists:
            defects.append("record_class_missing:" + name)
    if invalid:
        defects.extend("record_class_invalid:" + name for name in sorted(set(invalid)))
    members = roster.get("members", [])
    if not isinstance(members, list):
        members = []
        defects.append("record_class_invalid:roster.json")
    roster_counts = yielded.get("per_roster_stage", [])
    if not isinstance(roster_counts, list) or any(not isinstance(row, dict) for row in roster_counts):
        roster_counts = []
        defects.append("record_class_invalid:yield.json")
    excluded_members = exclusions.get("members_excluded", [])
    if (not isinstance(excluded_members, list)
            or any(not isinstance(row, dict) or not isinstance(row.get("codes", []), list)
                   or any(not isinstance(code, str) for code in row.get("codes", []))
                   for row in excluded_members)):
        excluded_members = []
        defects.append("record_class_invalid:exclusions.json")
    missing = 0
    for member in members:
        if not isinstance(member, dict):
            missing += 1
            continue
        bundle = _bundle(member, roots)
        # A planned but absent member is a loss, not a structural code failure.
        if bundle is not None and any(not (bundle / name).is_file() and not Path(str(bundle / name) + ".zst").is_file()
                                      for name in structure.get("required_member_files", REQUIRED_MEMBER_FILES)):
            missing += 1
    if missing:
        defects.append(f"member_files_missing:{missing}")
    unresolved = yielded.get("unresolved_collection_stages", [])
    if isinstance(unresolved, list) and unresolved and not physical:
        defects.append(f"stage_unresolved:{len(unresolved)}")
    if handover_record is not None:
        transitions = _lines(Path(handover_record), invalid)
        if not any(row.get("transition") == "chain-exit-to-desk"
                   or (row.get("from") == "chain-exit" and row.get("to") == "desk") for row in transitions):
            defects.append("handover_missing")
    if not (custody / "night/chain.exited").is_file():
        verdict, reasons = "NOT_READY", ["chain_not_exited"]
    elif harvest_rc in (2, 3) or harvest.get("verdict") == "HARVEST_FAULT":
        verdict, reasons = "HARVEST_FAULT", ["harvest_fault"]
    elif defects:
        verdict, reasons = "STRUCTURE_DEFECT", defects
    else:
        verdict, reasons = "STRUCTURE_OK", []
    public_flags = Counter()
    restricted = 0
    classifications = {}
    excluding = set(structure.get("excluding_flags", structure.get("excluding_codes", [])))
    excluding_seen = set()
    for flag in flags:
        code = flag.get("code")
        public = flag.get("blinding") == BLINDINGS[0] and flag.get("klass") in KLASSES
        if isinstance(code, str):
            classifications[code] = classifications.get(code, True) and public
            if code in excluding:
                excluding_seen.add(code)
            if public:
                public_flags[code] += 1
            else:
                restricted += 1
    # A code with any restricted/unknown occurrence is never named publicly.
    for code in list(public_flags):
        if not classifications[code]:
            restricted += public_flags.pop(code)
    excluded = Counter()
    restricted_exclusions = 0
    for member in excluded_members:
        codes = member.get("codes", []) if isinstance(member, dict) else []
        public_codes = [code for code in codes if classifications.get(code, False)]
        excluded.update(set(public_codes))
        if not codes or any(not classifications.get(code, False) for code in codes):
            restricted_exclusions += 1
    harvest_verdict = harvest.get("verdict")
    if harvest_verdict not in HARVEST_VERDICTS:
        harvest_verdict = "UNKNOWN"
    counting_reasons = []
    if verdict != "STRUCTURE_OK":
        counting_reasons.append("structure:" + verdict)
    if harvest_verdict != "COLLECTED":
        counting_reasons.append("verdict:" + harvest_verdict)
    if harvest.get("claim_usable") is not True:
        counting_reasons.append("claim_unusable")
    if physical:
        counting_reasons.append("physical_stop:" + physical)
    counting_reasons.extend("excluding_flag:" + code for code in sorted(excluding_seen)
                            if classifications.get(code, False))
    if any(not classifications.get(code, False) for code in excluding_seen):
        counting_reasons.append("excluding_flag:RESTRICTED")
    stage_counts = [{"stage_id": row.get("stage_id"), **{key: _count(row.get(key)) for key in COUNT_FIELDS}}
                    for row in roster_counts]
    stage_records = []
    for row in stages:
        begin, end = _number(row.get("started_epoch_s")), _number(row.get("ended_epoch_s"))
        stage_records.append({"stage_id": row.get("stage_id"), "kind": row.get("kind"),
                              "rc": _number(row.get("rc")),
                              "seconds": max(0, end - begin) if begin is not None and end is not None else None})
    begin, end = _number(started.get("epoch_s")), _number(exited.get("epoch_s"))
    prior = [_json(Path(path), []) for path in previous]
    pack_id = harvest.get("pack_id", registration.get("pack_id"))
    return {"schema": "joulewise.b6_session_structure.v1", "verdict": verdict,
            "harvest_verdict": harvest_verdict, "reasons": reasons,
            "action": {"STRUCTURE_DEFECT": "HOLD_LOOP", "HARVEST_FAULT": "REHARVEST"}.get(verdict, "CONTINUE"),
            "counting": not counting_reasons, "counting_reasons": counting_reasons,
            "pack_id": pack_id, "plan_id": harvest.get("plan_id") or session_id,
            "attempt": harvest.get("attempt") if harvest.get("attempt") is not None else attempt,
            "first_session_of_pack": not any(row.get("pack_id") == pack_id for row in prior),
            "counts": {key: _count(yielded.get(key)) for key in COUNT_FIELDS},
            "per_roster_stage": stage_counts, "excluded_members": len(excluded_members),
            "exclusions": {"STRUCTURE": dict(excluded), "RESTRICTED": restricted_exclusions},
            "flags": {"STRUCTURE": dict(public_flags), "RESTRICTED": restricted},
            "stages": stage_records, "stages_rc_nonzero": sum(row["rc"] not in (None, 0) for row in stage_records),
            "chain_seconds": max(0, end - begin) if begin is not None and end is not None else None}


def session_line(record):
    counts, flags = record["counts"], record["flags"]
    return (f"structure={record['verdict']} counting={str(record['counting']).lower()} "
            f"verdict={record['harvest_verdict']} members={counts['present']}/{counts['planned']} "
            f"excluded={record['excluded_members']} flags=STRUCTURE:{sum(flags['STRUCTURE'].values())},"
            f"RESTRICTED:{flags['RESTRICTED']} stages_rc_nonzero={record['stages_rc_nonzero']} "
            f"chain_s={record['chain_seconds']} action={record['action']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", "custody", "registration", "record-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--harvest-rc", type=int, default=0)
    parser.add_argument("--runs-root", type=Path, action="append", default=[])
    parser.add_argument("--previous", type=Path, action="append", default=[])
    parser.add_argument("--handover-record", type=Path)
    parser.add_argument("--attempt", type=int, help="session attempt when harvest metadata is absent")
    parser.add_argument("--session-id", help="session identifier when harvest metadata is absent")
    args = parser.parse_args(argv)
    if args.attempt is not None and args.attempt < 1:
        parser.error("attempt must be positive")
    try:
        registration = json.loads(args.registration.read_text(encoding="utf-8"))
        if not isinstance(registration, dict) or not isinstance(registration.get("structure", {}), dict):
            raise ValueError
        structure = registration.get("structure", {})
        for key in ("required_records", "required_member_files", "excluding_flags", "excluding_codes"):
            if key in structure and (not isinstance(structure[key], list)
                                     or any(not isinstance(name, str) for name in structure[key])):
                raise ValueError
        for key in ("required_records", "required_member_files"):
            if any(Path(name).is_absolute() or ".." in Path(name).parts for name in structure.get(key, [])):
                raise ValueError
    except (OSError, ValueError):
        parser.error("unparsable registration")
    record = check(archive=args.archive, custody=args.custody, registration=registration,
                   harvest_rc=args.harvest_rc, runs_roots=args.runs_root, previous=args.previous,
                   handover_record=args.handover_record, attempt=args.attempt, session_id=args.session_id)
    args.record_dir.mkdir(parents=True, exist_ok=True)
    target = args.record_dir / "structure.json"
    temporary = target.with_suffix(".json.partial")
    temporary.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, target)
    print(session_line(record))
    return 0
