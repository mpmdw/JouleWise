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
    output_existed = Path(output).exists() or Path(output).is_symlink()
    archive, output = Path(archive).resolve(), Path(output).resolve()
    export = Path(export).resolve() if export else None
    for source in (archive, export):
        if source and (output.is_relative_to(source) or source.is_relative_to(output)):
            raise ValueError("output overlaps source archive/export")
    if output_existed or output.exists() or output.is_symlink():
        raise ValueError("output must be a new directory")
    source_roots = [source for source in (archive, export) if source]
    sources = {}

    def read(path):
        raw = path.read_bytes()
        sources[str(path)] = hashlib.sha256(raw).hexdigest()
        return raw.decode("utf-8")

    acceptance_path = archive / "derived/b6-acceptance.json"
    raw_acceptance = read(acceptance_path)
    exclusions = selected(raw_acceptance, "excluding")
    roster_raw = read(archive / "derived/roster.json")
    roster = selected(roster_raw, "members")
    pass_mismatch = False
    for tree in sorted((archive / "sources/repo").rglob("plan_tree.json")):
        tree_raw = read(tree)
        try:
            pass_id = selected(tree_raw, "bytes_pass")
        except ValueError:
            continue
        if pass_id != (2 if mode == "hull-p2" else 1):
            pass_mismatch = True
    before = {m["run_id"]: set() for m in roster}
    for row in exclusions:
        if row.get("scope") == "member":
            before.setdefault(row["run_id"], set()).add(row["code"])
    after = {run: set(codes) for run, codes in before.items()}
    notices, changes, statuses = [], [], {}
    unavailable = None
    mismatch = False
    provenance_unavailable = False
    assessments, spans, readings = None, {}, []
    # The gap threshold affects only thermal.unmeasured. This projection never
    # consumes that flag, so the production function's gap argument is immaterial.
    thresholds = {"thermal_unmeasured_gap_s": 0}
    try:
        if mode == "hull-p2":
            assessments = read(archive / "withheld/member-assessments.json")
        else:
            spans = selected(read(archive / "withheld/spans.json"), "spans")
            flags = archive / "derived/window_flags.json"
            try:
                expected = selected(read(flags), "hazards", "thermal", "continuous", "journal", "sha256")
            except (OSError, ValueError):
                expected = None
            provenance_unavailable = not isinstance(expected, str) or not expected
            if provenance_unavailable:
                notices.append({"code": "records.thermal_journal_provenance_unavailable"})
            journal = archive / "sources/night-custody/hazards/monitor/thermal.jsonl"
            if not journal.is_file() and not Path(str(journal) + ".zst").is_file():
                unavailable = "archived thermal journal unavailable"
            else:
                # read_bytes has the harvest's plain/.zst decompression semantics;
                # the sealed digest binds decompressed journal bytes too.
                digest = hashlib.sha256(h.read_bytes(journal)).hexdigest()
                actual = journal if journal.is_file() else Path(str(journal) + ".zst")
                sources[str(actual)] = hashlib.sha256(actual.read_bytes()).hexdigest()
                mismatch = not provenance_unavailable and digest != expected
                if mismatch:
                    notices.append({"code": "records.thermal_journal_mismatch"})
                readings, malformed = h.read_monitor_journal(journal, "thermal")
                if malformed:
                    notices.append({"code": "records.monitor_line_malformed"})
    except (OSError, ValueError):
        unavailable = "archived thermal journal unavailable" if mode == "request-end-p1" else "hull assessment unavailable"

    def undefined(run, reason):
        statuses[run] = "not defined (" + reason + ")"
        notices.append({"run_id": run, "code": "records.thermal_line_undefined", "reason": reason})

    for member in roster:
        run = member["run_id"]
        if member.get("kind") != "science":
            notices.append({"run_id": run, "code": "reference.unchanged"})
            continue
        statuses[run] = "equals registered line"
        if pass_mismatch:
            undefined(run, "pass mismatch")
            continue
        if unavailable:
            if (CODE not in before[run]) if mode == "hull-p2" else (CODE in before[run]):
                undefined(run, unavailable)
            continue
        if mode == "hull-p2":
            try:
                record = selected(assessments, "members", run, FIELD)
                if (not isinstance(record, dict) or type(record.get("journal_available")) is not bool
                        or "excluded" not in record or record["excluded"] not in (True, False, None)):
                    raise ValueError("invalid hull assessment")
            except (ValueError, TypeError, IndexError):
                if CODE not in before[run]:
                    undefined(run, "hull assessment unavailable")
                continue
            if not record["journal_available"]:
                notices.append({"run_id": run, "code": "thermal.unmeasured"})
            if record["excluded"] is None:
                notices.append({"run_id": run, "code": "member.span_unknown"})
            if not record["journal_available"] or record["excluded"] is None:
                if CODE not in before[run]:
                    undefined(run, "hull assessment unavailable")
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
                undefined(run, "noninteger span")
                continue
            found = {code for code, *_ in h.thermal_member_flags(stamps, readings, thresholds)}
            if CODE in found and CODE not in before[run]:
                raise ValueError(f"request-end would add {CODE}: {run}")
            if CODE not in found:
                if (mismatch or provenance_unavailable) and CODE in before[run]:
                    undefined(run, "journal provenance unavailable" if provenance_unavailable
                              else "journal differs from the harvest's")
                    continue
                after[run].discard(CODE)
        if after[run] != before[run]:
            statuses[run] = "evaluated"
            changes.append({"run_id": run, "code": CODE,
                            "action": "added" if CODE in after[run] else "removed",
                            "reason": LABELS[mode]})
    exports = {}
    withheld_runs = set()
    if export:
        session = selected(raw_acceptance, "session_id")
        path = export / (session + ".runs.csv")
        inputs = [(path, Path(path.name), False)]
        sidecar = export / (session + ".session.json")
        if sidecar.is_file():
            raw_sidecar = read(sidecar)
            try:
                locator = selected(raw_sidecar, "blinding", "withheld", "path")
            except ValueError:
                locator = None
            if locator:
                store_rel = Path("withheld") / (session + ".withheld.csv")
                store = (export / locator).resolve()
                if output.is_relative_to(store) or store.is_relative_to(output):
                    raise ValueError("output overlaps source withheld store")
                inputs.append((store, store_rel, True))
                a, z = field_span(raw_sidecar, ("blinding", "withheld", "path"))
                raw_sidecar = replace(raw_sidecar, [(a, z, json.dumps(store_rel.as_posix()))])
            exports[Path(sidecar.name)] = raw_sidecar
        tables, seen, bad = [], set(), set()
        for source, relative, withheld in inputs:
            try:
                raw = read(source)
            except OSError:
                continue
            rows = csv_fields(raw)
            header = [decode_field(raw, span) for span in rows[0]]
            rid, codes = header.index("run_id"), header.index("exclusion_codes")
            for row in rows[1:]:
                run = decode_field(raw, row[rid])
                original = set(filter(None, decode_field(raw, row[codes]).split(";")))
                if run not in before or original != before[run] or run in seen:
                    bad.add(run)
                    undefined(run, "CSV/archive code disagreement: " + run)
                seen.add(run)
                if withheld:
                    withheld_runs.add(run)
            tables.append((relative, raw, rows, header))
        for change in changes:
            run = change["run_id"]
            if run not in seen:
                bad.add(run)
                undefined(run, "changed member absent from export")
        for run in bad:
            if run in before:
                after[run] = set(before[run])
        changes = [c for c in changes if c["run_id"] not in bad]
        for relative, raw, rows, header in tables:
            rid, codes = header.index("run_id"), header.index("exclusion_codes")
            edits = []
            for row in rows[1:]:
                run = decode_field(raw, row[rid])
                if run not in bad and after[run] != before[run]:
                    edits.append((*row[codes], encode_field(";".join(sorted(after[run])))))
                    if "excluded" in header:
                        edits.append((*row[header.index("excluded")], str(bool(after[run]))))
            exports[relative] = replace(raw, edits)
    new_exclusions = [row for row in exclusions if not (
        row.get("scope") == "member" and row["code"] not in after[row["run_id"]])]
    for change in changes:
        if change["action"] == "added":
            new_exclusions.append({"scope": "member", "run_id": change["run_id"], "code": CODE, "why": CODE})
    a, z = field_span(raw_acceptance, ("excluding",))
    new_acceptance = (raw_acceptance if not changes else
                      replace(raw_acceptance, [(a, z, json.dumps(new_exclusions, ensure_ascii=False))]))
    units = {}
    for member in roster:
        for unit in member.get("units", []):
            key = (unit["cell_id"], unit["stratum"], unit["unit_id"])
            units.setdefault(key, []).append(member["run_id"])
    undefined_statuses = sorted({value for value in statuses.values() if value.startswith("not defined")})
    line_status = ("; ".join(undefined_statuses) if undefined_statuses else
                   "evaluated" if changes else "equals registered line")
    record = {"label": LABELS[mode], "source_sha256": sources,
              "producing_commit": subprocess.check_output(
                  ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1], text=True).strip(),
              "producing_tree_dirty": bool(subprocess.check_output(
                  ["git", "status", "--porcelain", "--untracked-files=no"],
                  cwd=Path(__file__).resolve().parents[1], text=True).strip()),
              "records.thermal_view_changed": False,
              "status": line_status,
              "member_statuses": [{"run_id": m["run_id"],
                  "status": statuses.get(m["run_id"], "equals registered line"),
                  "blinded_status": "not defined at blinded stage (row withheld)"
                      if m["run_id"] in withheld_runs else statuses.get(m["run_id"], "equals registered line")}
                  for m in roster],
              "changes": changes, "notices": notices, "equals_registered_line": not changes and not undefined_statuses,
              "restored_members": sorted(r for r in before if before[r] and not after[r]),
              "dropped_members": [{"run_id": r, "codes": sorted(c)} for r, c in sorted(after.items()) if c],
              # Units are printed as run-id lists; the analysis owns validity,
              # whole-unit counts, and the five-unit minimum.
              "restored_units": [runs for runs in units.values() if any(before[r] for r in runs)
                                 and not any(after[r] for r in runs)],
              "dropped_units": [runs for runs in units.values() if any(after[r] for r in runs)]}
    output.mkdir(parents=True, exist_ok=False)
    for path in archive.rglob("*"):
        rel = path.relative_to(archive)
        dest = output / rel
        guard_destination(dest, output, source_roots)
        if path.is_dir():
            guard_destination(dest / "_directory_check", output, source_roots)
            dest.mkdir(exist_ok=True)
        elif rel != Path("derived/b6-acceptance.json") and rel not in (Path("thermal_line.json"), Path("view_manifest.json")):
            if dest.exists() or dest.is_symlink():
                dest.unlink()
            dest.symlink_to(path.resolve())
    write_copy(output / "derived/b6-acceptance.json", new_acceptance, output, source_roots)
    if exports:
        guard_destination(output / "export", output, source_roots)
        guard_destination(output / "export/_directory_check", output, source_roots)
        (output / "export").mkdir(exist_ok=True)
        for name, content in exports.items():
            destination = output / "export" / name
            write_copy(destination, content, output, source_roots)
    manifest = {"files": view_files(output)}
    write_copy(output / "view_manifest.json", json.dumps(manifest, indent=2) + "\n", output, source_roots)
    record["view_manifest_sha256"] = sha256(output / "view_manifest.json")
    write_copy(output / "thermal_line.json", json.dumps(record, indent=2) + "\n", output, source_roots)
    return record


# Control files cannot hash themselves. The manifest covers every exposed payload
# file; thermal_line binds the manifest. verify checks both in that order.
CONTROL = {"view_manifest.json", "thermal_line.json"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard_destination(path, output, sources=()):
    """Check every destination directory before creating or replacing a leaf."""
    relative = path.relative_to(output)
    directory = output
    for part in (None, *relative.parts[:-1]):
        if part is not None:
            directory = directory / part
        if directory.is_symlink():
            raise ValueError("destination directory is a symlink: " + str(directory))
        if any(directory.resolve().is_relative_to(source) for source in sources):
            raise ValueError("destination directory resolves inside source: " + str(directory))


def write_copy(path, content, output=None, sources=()):
    output = output if output is not None else path.parent
    guard_destination(path, output, sources)
    path.parent.mkdir(parents=True, exist_ok=True)
    guard_destination(path, output, sources)
    if path.exists() or path.is_symlink():
        path.unlink()
    path.write_bytes(content.encode("utf-8"))
    path.chmod(0o444)


def view_files(output):
    files = []
    for path in sorted(output.rglob("*")):
        relative = path.relative_to(output).as_posix()
        if relative not in CONTROL and (path.is_file() or path.is_symlink()):
            try:
                stat = path.stat()
                entry = {"path": relative, "size": stat.st_size, "sha256": sha256(path)}
                # Only linked source identities must disclose re-acceptance.
                # Fresh copied payloads have different inodes and timestamps.
                if path.is_symlink():
                    entry.update(mtime_ns=stat.st_mtime_ns, inode=stat.st_ino)
                files.append(entry)
            except OSError:
                files.append({"path": relative, "size": None, "sha256": None})
    return files


def manifest_entries(value):
    """Validate control data before using paths as mapping keys or sorting them."""
    if not isinstance(value, dict) or set(value) != {"files"} or not isinstance(value["files"], list):
        raise ValueError("manifest must be an object containing a files list")
    expected = {}
    for row in value["files"]:
        if not isinstance(row, dict) or not {"path", "size", "sha256"} <= row.keys():
            raise ValueError("manifest entry must contain path, size and sha256")
        if row.keys() - {"path", "size", "sha256", "mtime_ns", "inode"}:
            raise ValueError("manifest entry contains unknown fields")
        path = row["path"]
        if (not isinstance(path, str) or not path or Path(path).is_absolute()
                or any(part in ("", ".", "..") for part in path.split("/"))
                or "\\" in path or path in CONTROL or path in expected):
            raise ValueError("manifest entry path must be unique, relative and normalized")
        size, digest = row["size"], row["sha256"]
        if size is None and digest is None:
            if set(row) != {"path", "size", "sha256"}:
                raise ValueError("unavailable manifest entry has metadata")
        elif (type(size) is not int or size < 0 or not isinstance(digest, str)
              or re.fullmatch(r"[0-9a-f]{64}", digest) is None):
            raise ValueError("manifest entry requires a nonnegative integer size and SHA-256")
        if ("mtime_ns" in row) != ("inode" in row):
            raise ValueError("manifest entry requires both identity stamps")
        if any(type(row[key]) is not int for key in ("mtime_ns", "inode") if key in row):
            raise ValueError("manifest identity stamps must be integers")
        expected[path] = row
    return expected


def verify(output):
    output = Path(output)
    record_path = output / "thermal_line.json"
    record = json.loads(record_path.read_bytes())
    manifest_path = output / "view_manifest.json"
    different, reasons = [], []
    try:
        if sha256(manifest_path) != record["view_manifest_sha256"]:
            different.append("view_manifest.json")
            reasons.append("manifest SHA-256 differs from recorded binding")
        expected = manifest_entries(json.loads(manifest_path.read_bytes()))
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        expected = {}
        different.append("view_manifest.json")
        reasons.append("manifest invalid: " + (str(exc) if type(exc) is ValueError else type(exc).__name__))
    current = {row["path"]: row for row in view_files(output)}
    different.extend(path for path in sorted(expected.keys() | current.keys())
                     if expected.get(path) != current.get(path))
    record["records.thermal_view_changed"] = bool(different)
    record["notices"] = [notice for notice in record["notices"]
                         if notice["code"] != "records.thermal_view_changed"]
    if different:
        record["notices"].append({"code": "records.thermal_view_changed",
                                  "reason": "; ".join(reasons) if reasons else "payload differs from manifest"})
    record["view_differing_paths"] = sorted(set(different))
    write_copy(record_path, json.dumps(record, indent=2) + "\n", output)
    return record["view_differing_paths"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode in LABELS:
        cmd = sub.add_parser(mode)
        cmd.add_argument("archive", type=Path)
        cmd.add_argument("output", type=Path)
        cmd.add_argument("--export", type=Path)
    cmd = sub.add_parser("verify")
    cmd.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    if args.mode == "verify":
        different = verify(args.output)
        print("\n".join(different) if different else "view verified")
        return
    try:
        record = transform(args.mode, args.archive, args.output, args.export)
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
