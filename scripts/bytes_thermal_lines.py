#!/usr/bin/env python3
"""Blinded exclusion-only inputs for the two BYTES §21 thermal lines.

Unchanged archive files are symlinked, never decoded. Keep the source archive
available. Only selected JSON subtrees and CSV identity/code fields are decoded;
measurement lexemes remain opaque. No estimator or harvest policy lives here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.b5 import harvest as h

CODE = "thermal.os_level_nonzero"
FIELD = "thermal_os_level_nonzero_member_hull"
LABELS = {
    "hull-p2": "member-hull OS window (pass-1 registered window)",
    "request-end-p1": "request-end OS-window sensitivity (post hoc; not a registered result)",
}
# Lex JSON without decoding numbers or string values. Object keys alone are
# decoded during navigation. This also supplies exact replacement offsets.
TOKEN = re.compile(r'\s*("(?:[^"\\]|\\.)*"|[{}\[\]:,]|[^\s{}\[\]:,]+)')


def end_value(tokens, index):
    value = tokens[index].group(1)
    if value not in ("{", "["):
        return index + 1
    close = "}" if value == "{" else "]"
    index += 1
    while tokens[index].group(1) != close:
        if tokens[index].group(1) in (",", ":"):
            index += 1
        else:
            index = end_value(tokens, index)
    return index + 1


def field_span(raw, keys):
    tokens = list(TOKEN.finditer(raw))
    index = 0
    for key in keys:
        if tokens[index].group(1) != "{":
            raise ValueError("expected JSON object")
        index += 1
        while tokens[index].group(1) != "}":
            candidate = json.loads(tokens[index].group(1))
            start = index + 2
            end = end_value(tokens, start)
            if candidate == key:
                index = start
                break
            index = end + (tokens[end].group(1) == ",")
        else:
            raise ValueError(f"missing structural field: {key}")
    end = end_value(tokens, index)
    return tokens[index].start(1), tokens[end - 1].end(1)


def selected(raw, *keys):
    a, z = field_span(raw, keys)
    return json.loads(raw[a:z])


def csv_fields(raw):
    """Raw RFC4180 field spans, including quotes; retain all separators."""
    rows, row, start, index, quoted = [], [], 0, 0, False
    while index < len(raw):
        char = raw[index]
        if char == '"':
            if quoted and index + 1 < len(raw) and raw[index + 1] == '"':
                index += 2
                continue
            quoted = not quoted
        if not quoted and char in ',\r\n':
            row.append((start, index))
            if char != ',':
                rows.append(row)
                row = []
                if char == '\r' and index + 1 < len(raw) and raw[index + 1] == '\n':
                    index += 1
            start = index + 1
        index += 1
    if quoted:
        raise ValueError("unterminated CSV field")
    if start < len(raw) or row:
        row.append((start, len(raw)))
        rows.append(row)
    return rows


def decode_field(raw, span):
    return next(csv.reader([raw[slice(*span)]]))[0] if span[0] != span[1] else ""


def encode_field(value):
    out = io.StringIO(newline="")
    csv.writer(out, lineterminator="\r\n").writerow([value])
    return out.getvalue()[:-2]


def replace(raw, replacements):
    for a, z, value in sorted(replacements, reverse=True):
        raw = raw[:a] + value + raw[z:]
    return raw


def transform(mode, archive, output, export=None):
    archive, output = Path(archive).resolve(), Path(output).resolve()
    export = Path(export).resolve() if export else None
    for source in (archive, export):
        if source and (output.is_relative_to(source) or source.is_relative_to(output)):
            raise ValueError("output overlaps source archive/export")
    if output.exists():
        raise ValueError("output must be a new directory")
    sources = {}

    def read(path):
        raw = path.read_bytes()
        sources[str(path)] = hashlib.sha256(raw).hexdigest()
        return raw.decode("utf-8")

    acceptance_path = archive / "derived/b6-acceptance.json"
    raw_acceptance = read(acceptance_path)
    exclusions = selected(raw_acceptance, "excluding")
    roster = selected(read(archive / "derived/roster.json"), "members")
    before = {m["run_id"]: set() for m in roster}
    for row in exclusions:
        if row.get("scope") == "member":
            before.setdefault(row["run_id"], set()).add(row["code"])
    after = {run: set(codes) for run, codes in before.items()}
    notices, changes = [], []
    if mode == "hull-p2":
        assessments = read(archive / "withheld/member-assessments.json")
    else:
        spans = selected(read(archive / "withheld/spans.json"), "spans")
        # This is the exact resolved threshold record the harvest sealed,
        # including explicit overrides. Do not resolve a mutable live plan.
        thresholds = {"thermal_unmeasured_gap_s": selected(
            read(archive / "derived/harvest-thresholds.json"), "values", "thermal_unmeasured_gap_s")}
        journal = archive / "sources/night-custody/hazards/monitor/thermal.jsonl"
        if not journal.is_file():
            raise ValueError("archived thermal journal unavailable; no evaluation written")
        sources[str(journal)] = hashlib.sha256(journal.read_bytes()).hexdigest()
        readings, malformed = h.read_monitor_journal(journal, "thermal")
        if malformed:
            notices.append({"code": "records.monitor_line_malformed"})
    for member in roster:
        run = member["run_id"]
        if member.get("kind") != "science":
            notices.append({"run_id": run, "code": "reference.unchanged"})
            continue
        if mode == "hull-p2":
            record = selected(assessments, "members", run, FIELD)
            if not record["journal_available"]:
                notices.append({"run_id": run, "code": "thermal.unmeasured"})
                continue
            if record["excluded"] is None:
                notices.append({"run_id": run, "code": "member.span_unknown"})
                continue
            if record["excluded"] is True:
                after[run].add(CODE)
        else:
            span = spans.get(run, {})
            if span.get("member") is None or span.get("request") is None:
                notices.append({"run_id": run, "code": "request_span.absent_keep_hull"})
                continue
            stamps = [span["member"][0], span["request"][1]]
            if any(type(v) is not int for v in stamps):
                raise ValueError(f"noninteger span: {run}")
            found = {code for code, *_ in h.thermal_member_flags(stamps, readings, thresholds)}
            if CODE in found and CODE not in before[run]:
                raise ValueError(f"request-end would add {CODE}: {run}")
            if CODE not in found:
                after[run].discard(CODE)
        if after[run] != before[run]:
            changes.append({"run_id": run, "code": CODE,
                            "action": "added" if CODE in after[run] else "removed",
                            "reason": LABELS[mode]})
    new_exclusions = [row for row in exclusions if not (
        row.get("scope") == "member" and row["code"] not in after[row["run_id"]])]
    for change in changes:
        if change["action"] == "added":
            new_exclusions.append({"scope": "member", "run_id": change["run_id"], "code": CODE, "why": CODE})
    a, z = field_span(raw_acceptance, ("excluding",))
    new_acceptance = (raw_acceptance if not changes else
                      replace(raw_acceptance, [(a, z, json.dumps(new_exclusions, ensure_ascii=False))]))
    exports = {}
    if export:
        session = selected(raw_acceptance, "session_id")
        path = export / (session + ".runs.csv")
        raw = read(path)
        rows = csv_fields(raw)
        header = [decode_field(raw, s) for s in rows[0]]
        rid, codes = header.index("run_id"), header.index("exclusion_codes")
        edits, seen = [], set()
        for row in rows[1:]:
            run = decode_field(raw, row[rid])
            original = set(filter(None, decode_field(raw, row[codes]).split(";")))
            if run not in before or original != before[run] or run in seen:
                raise ValueError(f"CSV/archive exclusion mismatch or duplicate: {run}")
            seen.add(run)
            if after[run] != original:
                edits.append((*row[codes], encode_field(";".join(sorted(after[run])))))
        if any(c["run_id"] not in seen for c in changes):
            raise ValueError("changed member absent from CSV")
        exports[path.name] = replace(raw, edits)
    units = {}
    for member in roster:
        for unit in member.get("units", []):
            key = (unit["cell_id"], unit["stratum"], unit["unit_id"])
            units.setdefault(key, []).append(member["run_id"])
    record = {"label": LABELS[mode], "source_sha256": sources,
              "producing_commit": subprocess.check_output(
                  ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1], text=True).strip(),
              "changes": changes, "notices": notices, "equals_registered_line": not changes,
              "restored_members": sorted(r for r in before if before[r] and not after[r]),
              "dropped_members": [{"run_id": r, "codes": sorted(c)} for r, c in sorted(after.items()) if c],
              # Units are printed as run-id lists; the analysis owns validity,
              # whole-unit counts, and the five-unit minimum.
              "restored_units": [runs for runs in units.values() if any(before[r] for r in runs)
                                 and not any(after[r] for r in runs)],
              "dropped_units": [runs for runs in units.values() if any(after[r] for r in runs)]}
    output.mkdir(parents=True)
    for path in archive.rglob("*"):
        rel = path.relative_to(archive)
        dest = output / rel
        if path.is_dir():
            dest.mkdir(exist_ok=True)
        elif rel != Path("derived/b6-acceptance.json") and rel != Path("thermal_line.json"):
            dest.symlink_to(path.resolve())
    (output / "derived/b6-acceptance.json").write_bytes(new_acceptance.encode("utf-8"))
    if exports:
        (output / "export").mkdir(exist_ok=True)
        for name, content in exports.items():
            (output / "export" / name).write_bytes(content.encode("utf-8"))
    (output / "thermal_line.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode in LABELS:
        cmd = sub.add_parser(mode)
        cmd.add_argument("archive", type=Path)
        cmd.add_argument("output", type=Path)
        cmd.add_argument("--export", type=Path)
    args = parser.parse_args(argv)
    try:
        record = transform(args.mode, args.archive, args.output, args.export)
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
