#!/usr/bin/env python3
"""Blinded exclusion-only inputs for the two BYTES §21 thermal lines.

Unchanged archive files are symlinked, never decoded. Keep the source archive
available. Only selected JSON subtrees and CSV identity/code fields are decoded;
measurement lexemes remain opaque. No estimator or harvest policy lives here.
"""
from __future__ import annotations

import argparse
import csv
from functools import lru_cache
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
TOKEN = re.compile(r'[ \t\r\n]*("(?:[^"\\]|\\.)*"|[{}\[\]:,]|[^\s{}\[\]:,]+)')
# RFC 8259 strings, with paired UTF-16 escapes only. No value is decoded here.
UNICODE_ESCAPE = (r'\\u(?:[0-9a-cA-Ce-fE-F][0-9a-fA-F]{3}|[dD][0-7][0-9a-fA-F]{2}|'
                  r'[dD][89aAbB][0-9a-fA-F]{2}\\u[dD][c-fC-F][0-9a-fA-F]{2})')
STRING = re.compile(r'"(?:[^"\\\x00-\x1f\ud800-\udfff]|\\["\\/bfnrt]|' + UNICODE_ESCAPE + r')*"')
NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')
LITERALS = frozenset({"true", "false", "null"})


def lex(raw):
    """Tokens of exactly one complete JSON text; ValueError otherwise.

    Every lexeme must match the JSON lexical grammar, the tokens must form one
    value under the JSON grammar (checked with an explicit stack, so depth
    cannot crash the check), objects may not repeat a key (the producers
    serialize dicts), and nothing but whitespace may follow the value. Values
    are matched, never converted: measurement lexemes stay opaque.
    """
    tokens, position = [], 0
    for match in TOKEN.finditer(raw):
        if match.start() != position:
            raise ValueError("JSON text contains unlexable bytes")
        position = match.end()
        lexeme = match.group(1)
        if lexeme[0] == '"':
            if STRING.fullmatch(lexeme) is None:
                raise ValueError("invalid JSON string lexeme")
        elif lexeme not in "{}[]:," and lexeme not in LITERALS and NUMBER.fullmatch(lexeme) is None:
            raise ValueError("invalid JSON lexeme")
        tokens.append(match)
    if raw[position:].strip(" \t\r\n"):
        raise ValueError("JSON text has trailing bytes")
    if not tokens:
        raise ValueError("empty JSON text")
    stack, index, expect = [], 0, "value"
    while True:
        if index >= len(tokens):
            raise ValueError("incomplete JSON text")
        lexeme = tokens[index].group(1)
        index += 1
        if expect == "value":
            if lexeme == "{":
                stack.append(("{", set()))
                expect = "key-or-close"
                continue
            if lexeme == "[":
                stack.append(("[", None))
                expect = "value-or-close"
                continue
            if lexeme in "{}[]:,":
                raise ValueError("JSON value expected")
        elif expect in ("key-or-close", "key"):
            if lexeme == "}" and expect == "key-or-close":
                stack.pop()
            elif lexeme[0] == '"':
                key = json.loads(lexeme)
                if key in stack[-1][1]:
                    raise ValueError("JSON object repeats a key")
                stack[-1][1].add(key)
                expect = "colon"
                continue
            else:
                raise ValueError("JSON object key expected")
        elif expect == "colon":
            if lexeme != ":":
                raise ValueError("JSON colon expected")
            expect = "value"
            continue
        elif expect == "value-or-close":
            if lexeme == "]":
                stack.pop()
            else:
                index -= 1
                expect = "value"
                continue
        # A value has just ended: close containers or continue the enclosing one.
        while True:
            if not stack:
                if index != len(tokens):
                    raise ValueError("JSON text has more than one value")
                return tokens
            if index >= len(tokens):
                raise ValueError("incomplete JSON text")
            lexeme = tokens[index].group(1)
            index += 1
            if lexeme == ",":
                expect = "key" if stack[-1][0] == "{" else "value"
                break
            if (lexeme == "}" and stack[-1][0] == "{") or (lexeme == "]" and stack[-1][0] == "["):
                stack.pop()
                continue
            raise ValueError("JSON separator or close expected")


def end_value(tokens, index):
    """Skip a validated value without recursion, including opaque deep subtrees."""
    if tokens[index].group(1) not in ("{", "["):
        return index + 1
    depth = 1
    index += 1
    while depth:
        value = tokens[index].group(1)
        depth += (value in ("{", "[")) - (value in ("}", "]"))
        index += 1
    return index


# Bounded compatibility cache for the public offset helpers. Validators own their
# source documents; there is no process-wide retention of every archive read.
@lru_cache(maxsize=8)
def tokens_of(raw):
    return lex(raw)


def field_span(raw, keys):
    tokens = tokens_of(raw)
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


def item_spans(raw, keys):
    """Exact offsets of each element of the JSON array at ``keys``."""
    tokens = tokens_of(raw)
    start, _end = field_span(raw, keys)
    index = next(i for i, token in enumerate(tokens) if token.start(1) == start)
    if tokens[index].group(1) != "[":
        raise ValueError("expected JSON array")
    spans, index = [], index + 1
    while tokens[index].group(1) != "]":
        end = end_value(tokens, index)
        spans.append((tokens[index].start(1), tokens[end - 1].end(1)))
        index = end + (tokens[end].group(1) == ",")
    return spans


class JsonValue:
    """A view of validated tokens. Decode only explicitly consumed scalars."""
    def __init__(self, raw, tokens=None, index=0):
        self.raw = raw
        self.tokens = lex(raw) if tokens is None else tokens
        self.index = index

    @property
    def kind(self):
        return self.tokens[self.index].group(1)[0]

    def field(self, key):
        for name, value in self.fields():
            if name == key:
                return value
        raise ValueError("missing structural field: " + key)

    def fields(self):
        if self.kind != "{":
            raise ValueError("expected JSON object")
        index = self.index + 1
        while self.tokens[index].group(1) != "}":
            key = json.loads(self.tokens[index].group(1))
            yield key, JsonValue(self.raw, self.tokens, index + 2)
            index = end_value(self.tokens, index + 2)
            index += self.tokens[index].group(1) == ","

    def elements(self):
        if self.kind != "[":
            raise ValueError("expected JSON array")
        index = self.index + 1
        while self.tokens[index].group(1) != "]":
            yield JsonValue(self.raw, self.tokens, index)
            index = end_value(self.tokens, index)
            index += self.tokens[index].group(1) == ","

    def scalar(self):
        if self.kind in "{[":
            raise ValueError("expected JSON scalar")
        return json.loads(self.tokens[self.index].group(1))

    def optional(self, key):
        try:
            return self.field(key).scalar()
        except ValueError:
            return None

    def text(self):
        end = end_value(self.tokens, self.index)
        return self.raw[self.tokens[self.index].start(1):self.tokens[end - 1].end(1)]


def document(raw):
    value = JsonValue(raw)
    if value.kind != "{":
        raise ValueError("expected JSON object")
    return value


def unit_valid(unit):
    return (isinstance(unit, dict) and {"cell_id", "stratum", "unit_id"} <= unit.keys()
            and all(type(unit[k]) in (str, int) for k in ("cell_id", "stratum", "unit_id")))


def validate_roster(raw):
    """Project roster identities and units; structural absence is a stop (X10)."""
    doc = document(raw)
    members, reason = [], None
    for node in doc.field("members").elements():
        if node.kind != "{":
            raise ValueError("roster members is not a list of objects")
        run, kind = node.optional("run_id"), node.optional("kind")
        if not isinstance(run, str):
            reason = reason or "roster member missing run_id"
            run = None
        if not isinstance(kind, str):
            reason = reason or "roster member kind invalid"
            kind = "science"
        units = []
        try:
            for unit in node.field("units").elements():
                values = {k: unit.optional(k) for k in ("cell_id", "stratum", "unit_id")}
                if not unit_valid(values):
                    raise ValueError("invalid unit")
                units.append(values)
        except ValueError:
            reason = reason or "roster member units invalid"
        members.append({"run_id": run, "kind": kind, "units": units})
    return members, doc.optional("pack_id"), reason


def validate_acceptance(raw, roster):
    """Project identity/code fields, leaving every retained row byte-opaque."""
    doc = document(raw)
    before = {m["run_id"]: set() for m in roster}
    structural, reason, rows = {}, None, []
    try:
        nodes = list(doc.field("excluding").elements())
    except ValueError:
        nodes = []
        reason = "acceptance excluding is not a list"
    for node in nodes:
        if node.kind != "{":
            rows.append(None)
            reason = reason or "acceptance exclusion row is not an object"
            continue
        row = {key: node.optional(key) for key in ("scope", "run_id", "code")}
        rows.append(row)
        if not isinstance(row["scope"], str):
            reason = reason or "exclusion row missing scope"
        if row["scope"] != "member":
            continue
        run, code = row["run_id"], row["code"]
        if not isinstance(run, str):
            reason = reason or "exclusion row missing run_id"
        elif run not in before:
            reason = reason or "exclusion row names a run outside the roster"
        elif not isinstance(code, str):
            structural[run] = "exclusion row missing code"
        else:
            before[run].add(code)
    return rows, before, structural, reason, doc.optional("session_id")


def validate_plan(read, archive, pack_id, mode):
    """Only the roster-named pack tree can carry pass identity (X6)."""
    if (not isinstance(pack_id, str) or not pack_id or ".." in pack_id
            or "/" in pack_id or "\\" in pack_id):
        return "pass mismatch"
    trees = [p for p in (archive / "sources/repo").rglob("plan_tree.json") if p.parent.name == pack_id]
    if len(trees) != 1:
        return "pass mismatch"
    try:
        value = document(read(trees[0])).field("bytes_pass").scalar()
        if type(value) is int and value == (2 if mode == "hull-p2" else 1):
            return None
    except (OSError, ValueError):
        pass
    return "pass mismatch"


def validate_hull(doc, run, notices):
    try:
        value = doc.field("members").field(run).field(FIELD)
        excluded, available = value.field("excluded").scalar(), value.field("journal_available").scalar()
        if type(available) is not bool or (excluded is not None and type(excluded) is not bool):
            raise ValueError("invalid hull assessment")
        if not available:
            notices.append({"run_id": run, "code": "thermal.unmeasured"})
        if excluded is None:
            notices.append({"run_id": run, "code": "member.span_unknown"})
        if available and excluded is not None:
            return excluded, None
    except ValueError:
        pass
    return None, "hull assessment unavailable"


def validate_spans(doc, run):
    try:
        node = doc.field("spans").field(run)
        spans = []
        for key in ("member", "request"):
            value = node.field(key)
            if value.kind == "n":
                spans.append(None)
                continue
            span = [v.scalar() for v in value.elements()]
            if len(span) != 2 or any(type(v) is not int or v < 0 for v in span):
                raise ValueError("invalid span")
            if span[0] > span[1]:
                raise ValueError("invalid span")
            spans.append(span)
        member, request = spans
        if request is not None and (member is None or not (member[0] <= request[0] <= request[1] <= member[1])):
            raise ValueError("invalid span")
        return (member, request), None
    except ValueError:
        return None, "invalid span"


def validate_seal(raw):
    try:
        node = document(raw)
        for key in ("hazards", "thermal", "continuous", "journal", "sha256"):
            node = node.field(key)
        digest = node.scalar()
        if isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest):
            return digest, None
    except ValueError:
        pass
    return None, "journal provenance unavailable"


def validate_journal(journal, expected, sources):
    """Identity check and the production parser; per-member replay follows spans."""
    try:
        raw = h.read_bytes(journal)
        actual = journal if journal.is_file() else Path(str(journal) + ".zst")
        sources[str(actual)] = hashlib.sha256(actual.read_bytes()).hexdigest()
        try:
            readings, malformed = h.read_monitor_journal(journal, "thermal")
        except RecursionError:
            # An unreadable sealed stream cannot reproduce a registered exclusion.
            readings, malformed = [], 1
        reason = ("journal provenance unavailable" if expected is None else
                  "journal differs from the harvest's" if hashlib.sha256(raw).hexdigest() != expected else None)
        return readings, malformed, reason
    except (OSError, ValueError):
        return [], 0, "archived thermal journal unavailable"


def validate_replay(member, request, readings, present, thresholds, reason, run):
    """V2 is checked before X5, using the unchanged production helper."""
    found = {code for code, *_ in h.thermal_member_flags([member[0], request[1]], readings, thresholds)}
    if CODE in found and not present and not reason:
        raise ValueError(f"request-end would add {CODE}: {run}")
    reason, disagrees = validate_hull_replay(member, readings, present, thresholds, reason)
    return CODE in found, reason, disagrees


def validate_hull_replay(member, readings, present, thresholds, reason):
    if reason:
        return reason, False
    replayed = (None if member is None else
                CODE in {code for code, *_ in h.thermal_member_flags(member, readings, thresholds)})
    disagrees = replayed is None or replayed != present
    return ("journal does not reproduce the registered hull decision" if disagrees else None), disagrees


def validate_sidecar(raw):
    try:
        node = document(raw)
        for key in ("blinding", "withheld", "path"):
            node = node.field(key)
        value = node.scalar()
        if isinstance(value, str) and value:
            return value, None
    except ValueError:
        pass
    return None, "withheld store locator unavailable"


def csv_fields(raw):
    """Raw RFC4180 field spans, including quotes; retain all separators."""
    rows, row, start, index, quoted, closed = [], [], 0, 0, False, False
    while index < len(raw):
        char = raw[index]
        if char == '"':
            if quoted and index + 1 < len(raw) and raw[index + 1] == '"':
                index += 2
                continue
            if not quoted and (index != start or closed):
                raise ValueError("quote inside unquoted CSV field")
            quoted = not quoted
            closed = not quoted
        elif closed and char not in ',\r\n':
            raise ValueError("bytes after closing CSV quote")
        if not quoted and char in ',\r\n':
            row.append((start, index))
            if char != ',':
                rows.append(row)
                row = []
                if char == '\r' and index + 1 < len(raw) and raw[index + 1] == '\n':
                    index += 1
            start = index + 1
            closed = False
        index += 1
    if quoted:
        raise ValueError("unterminated CSV field")
    if start < len(raw) or row:
        row.append((start, len(raw)))
        rows.append(row)
    return rows


def decode_field(raw, span):
    return next(csv.reader([raw[slice(*span)]]))[0] if span[0] != span[1] else ""


def validate_export(raw):
    """Lex all fields, decoding only headers and identity/code columns."""
    try:
        rows = csv_fields(raw)
        if not rows:
            raise ValueError("empty export CSV")
        header = [decode_field(raw, span) for span in rows[0]]
        if "run_id" not in header or "exclusion_codes" not in header:
            raise ValueError("export CSV missing run_id or exclusion_codes column")
        if len(set(header)) != len(header):
            raise ValueError("export CSV repeats a header")
        if any(len(row) != len(header) for row in rows[1:]):
            raise ValueError("export CSV row width differs from header")
        rid, codes = header.index("run_id"), header.index("exclusion_codes")
        identities = [(decode_field(raw, row[rid]), set(filter(None, decode_field(raw, row[codes]).split(";"))))
                      for row in rows[1:]]
        return (rows, header, identities), None
    except (ValueError, csv.Error) as exc:
        return None, str(exc)


def encode_field(value):
    if value == "":
        # DictWriter writes this field within a multi-column exporter row.
        return ""
    out = io.StringIO(newline="")
    csv.writer(out, lineterminator="\r\n").writerow([value])
    return out.getvalue()[:-2]


def replace(raw, replacements):
    for a, z, value in sorted(replacements, reverse=True):
        raw = raw[:a] + value + raw[z:]
    return raw


def member_status(mode, original_has_code, untrusted_reason, candidate_equal, records_fault=None):
    """Direction alone determines the invariant members, even without evidence."""
    if records_fault:
        return "not defined (" + records_fault + ")"
    if untrusted_reason:
        mutable = original_has_code if mode == "request-end-p1" else not original_has_code
        return "not defined (" + untrusted_reason + ")" if mutable else "equals registered line"
    return "equals registered line" if candidate_equal else "evaluated"


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
    roster_raw = read(archive / "derived/roster.json")
    roster, pack_id, roster_reason = validate_roster(roster_raw)
    exclusions, before, structural, global_fault, session = validate_acceptance(raw_acceptance, roster)
    global_fault = global_fault or roster_reason
    pass_mismatch = validate_plan(read, archive, pack_id, mode) is not None
    after = {run: set(codes) for run, codes in before.items()}
    notices, changes, statuses = [], [], {}
    if pass_mismatch:
        notices.append({"code": "records.thermal_pass_mismatch", "reason": "pass mismatch"})
    unavailable, journal_reason = None, None
    assessments, spans, readings = None, None, []
    # This argument affects only the discarded thermal.unmeasured projection.
    thresholds = {"thermal_unmeasured_gap_s": 0}
    try:
        if mode == "hull-p2":
            assessments = document(read(archive / "withheld/member-assessments.json"))
        else:
            spans = document(read(archive / "withheld/spans.json"))
            try:
                expected, seal_reason = validate_seal(read(archive / "derived/window_flags.json"))
            except (OSError, ValueError):
                expected, seal_reason = None, "journal provenance unavailable"
            if seal_reason:
                notices.append({"code": "records.thermal_journal_provenance_unavailable"})
            journal = archive / "sources/night-custody/hazards/monitor/thermal.jsonl"
            readings, malformed, journal_reason = validate_journal(journal, expected, sources)
            if journal_reason == "journal differs from the harvest's":
                notices.append({"code": "records.thermal_journal_mismatch"})
            if malformed:
                notices.append({"code": "records.monitor_line_malformed"})
    except (OSError, ValueError):
        unavailable = "archived thermal journal unavailable" if mode == "request-end-p1" else "hull assessment unavailable"

    def undefined(run, reason):
        statuses[run] = member_status(mode, False, None, True, records_fault=reason)
        notices.append({"run_id": run, "code": "records.thermal_line_undefined", "reason": reason})

    for member in roster:
        run = member.get("run_id")
        if member.get("kind") != "science":
            notices.append({"run_id": run, "code": "reference.unchanged"})
            continue
        reason = global_fault or structural.get(run) or ("pass mismatch" if pass_mismatch else unavailable)
        candidate = set(before[run])
        if not reason and mode == "hull-p2":
            excluded, reason = validate_hull(assessments, run, notices)
            if excluded:
                candidate.add(CODE)
        elif not reason:
            span, span_reason = validate_spans(spans, run)
            reason = journal_reason or span_reason
            if span is not None:
                member_span, request_span = span
                if request_span is None:
                    notices.append({"run_id": run, "code": "request_span.absent_keep_hull"})
                    reason, disagrees = validate_hull_replay(
                        member_span, readings, CODE in before[run], thresholds, reason)
                    if disagrees:
                        notices.append({"run_id": run, "code": "records.thermal_hull_replay_disagrees"})
                else:
                    found, reason, disagrees = validate_replay(
                        member_span, request_span, readings, CODE in before[run], thresholds, reason, run)
                    if disagrees:
                        notices.append({"run_id": run, "code": "records.thermal_hull_replay_disagrees"})
                    if not found:
                        candidate.discard(CODE)
        status = member_status(mode, CODE in before[run], reason, candidate == before[run],
                               records_fault=global_fault or structural.get(run))
        statuses[run] = status
        if status.startswith("not defined"):
            undefined(run, status[len("not defined ("):-1])
        elif not reason:
            after[run] = candidate
        if after[run] != before[run]:
            changes.append({"run_id": run, "code": CODE,
                            "action": "added" if CODE in after[run] else "removed",
                            "reason": LABELS[mode]})
    exports = {}
    withheld_runs = set()
    if export:
        if not isinstance(session, str):
            session = None
            for member in roster:
                if member.get("kind") == "science":
                    run = member.get("run_id")
                    undefined(run, "acceptance missing session_id")
                    after[run] = set(before[run])
            changes = []
        path = export / ((session or "") + ".runs.csv")
        inputs = [(path, Path(path.name), False)] if session else []
        sidecar = export / ((session or "") + ".session.json")
        if sidecar.is_file():
            try:
                raw_sidecar = read(sidecar)
                locator, _reason = validate_sidecar(raw_sidecar)
                if not isinstance(locator, str) or not locator:
                    locator = None
            except UnicodeDecodeError:
                raw_sidecar, locator = sidecar.read_bytes(), None
            except ValueError:
                locator = None
            if locator:
                try:
                    store = (export / locator).resolve()
                except (OSError, ValueError):
                    locator = None
            if locator:
                store_rel = Path("withheld") / (session + ".withheld.csv")
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
            except UnicodeDecodeError:
                exports[relative] = source.read_bytes()
                for member in roster:
                    if member.get("kind") == "science":
                        run = member.get("run_id")
                        bad.add(run)
                        undefined(run, "export CSV is not UTF-8")
                continue
            except OSError:
                continue
            table, export_reason = validate_export(raw)
            if export_reason:
                exports[relative] = raw
                for member in roster:
                    if member.get("kind") == "science":
                        bad.add(member.get("run_id"))
                        undefined(member.get("run_id"), export_reason)
                continue
            rows, header, identities = table
            rid, codes = header.index("run_id"), header.index("exclusion_codes")
            for run, original in identities:
                if run not in before or original != before[run] or run in seen:
                    bad.add(run)
                    undefined(run, "CSV/archive code disagreement: " + run)
                seen.add(run)
                if withheld:
                    withheld_runs.add(run)
            tables.append((relative, raw, rows, header, identities))
        for change in changes:
            run = change["run_id"]
            if run not in seen and run not in bad:
                bad.add(run)
                undefined(run, "changed member absent from export")
        for run in bad:
            if run in before:
                after[run] = set(before[run])
        changes = [c for c in changes if c["run_id"] not in bad]
        for relative, raw, rows, header, identities in tables:
            rid, codes = header.index("run_id"), header.index("exclusion_codes")
            edits = []
            for row, (run, _original) in zip(rows[1:], identities):
                if run not in bad and after[run] != before[run]:
                    edits.append((*row[codes], encode_field(";".join(sorted(after[run])))))
                    if "excluded" in header:
                        edits.append((*row[header.index("excluded")], str(bool(after[run]))))
            exports[relative] = replace(raw, edits)
    # Retained rows keep their exact source lexemes (spliced, never
    # re-encoded); only removed rows leave and added rows are appended.
    new_acceptance = raw_acceptance
    if changes:
        kept = [raw_acceptance[p:q] for row, (p, q) in zip(exclusions, item_spans(raw_acceptance, ("excluding",)))
                if not (isinstance(row, dict) and row.get("scope") == "member" and isinstance(row.get("code"), str)
                        and isinstance(row.get("run_id"), str) and row["run_id"] in after
                        and row["code"] not in after[row["run_id"]])]
        for change in changes:
            if change["action"] == "added":
                kept.append(json.dumps({"scope": "member", "run_id": change["run_id"], "code": CODE, "why": CODE},
                                       ensure_ascii=False))
        a, z = field_span(raw_acceptance, ("excluding",))
        new_acceptance = replace(raw_acceptance, [(a, z, "[" + ", ".join(kept) + "]")])
    units = {}
    for member in roster:
        for unit in (member.get("units") if isinstance(member.get("units"), list) else []):
            if unit_valid(unit):
                key = (unit["cell_id"], unit["stratum"], unit["unit_id"])
                units.setdefault(key, []).append(member.get("run_id"))
    undefined_statuses = sorted({value for value in statuses.values() if value.startswith("not defined")})
    line_status = ("; ".join(undefined_statuses) if undefined_statuses else
                   "evaluated" if changes else "equals registered line")
    try:
        producing_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1],
            text=True, stderr=subprocess.DEVNULL).strip()
        producing_tree_dirty = bool(subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=Path(__file__).resolve().parents[1], text=True, stderr=subprocess.DEVNULL).strip())
    except (OSError, subprocess.CalledProcessError):
        producing_commit = producing_tree_dirty = None
    record = {"label": LABELS[mode], "source_sha256": sources,
              "producing_commit": producing_commit,
              "producing_tree_dirty": producing_tree_dirty,
              "records.thermal_view_changed": False,
              "status": line_status,
              "member_statuses": [{"run_id": m.get("run_id"),
                  "status": statuses.get(m.get("run_id"), "equals registered line"),
                  "blinded_status": "not defined at blinded stage (row withheld)"
                      if m.get("run_id") in withheld_runs else statuses.get(m.get("run_id"), "equals registered line")}
                  for m in roster],
              "changes": changes, "notices": notices, "equals_registered_line": not changes and not undefined_statuses,
              "restored_members": sorted((r for r in before if before[r] and not after[r]), key=str),
              "dropped_members": [{"run_id": r, "codes": sorted(c)} for r, c in sorted(after.items(), key=lambda item: str(item[0])) if c],
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
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    path.chmod(0o444)


def linked_roots(output):
    """Archive roots the view's own links point into: target minus the link's relative path."""
    roots = []
    for path in output.rglob("*"):
        if not path.is_symlink():
            continue
        relative = path.relative_to(output).parts
        try:
            target = path.resolve(strict=True)
        except OSError:
            continue
        # Strip the view-relative depth even if a damaged link renamed its tail.
        # Such damage must not erase inside-source protection during recovery.
        if len(target.parents) >= len(relative):
            roots.append(target.parents[len(relative) - 1])
    return roots


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


class RetainedNotice(dict):
    def __init__(self, code, raw):
        super().__init__(code=code)
        self.raw = raw


class ControlRecord(dict):
    """Only verify's consumed fields are decoded; all other bytes stay opaque."""
    def __init__(self, raw, **fields):
        super().__init__(fields)
        self.raw = raw


def validate_record(raw):
    doc = document(raw)
    notices = []
    for node in doc.field("notices").elements():
        code = node.field("code").scalar()
        if not isinstance(code, str):
            raise ValueError("invalid notice code")
        notices.append(RetainedNotice(code, node.text()))
    sources = {}
    for source, node in doc.field("source_sha256").fields():
        digest = node.scalar()
        if (not Path(source).is_absolute() or ".." in Path(source).parts
                or Path(source).parent == Path("/") or not isinstance(digest, str)
                or re.fullmatch(r"[0-9a-f]{64}", digest) is None):
            raise ValueError("invalid recorded source")
        sources[source] = digest
    binding = doc.field("view_manifest_sha256").scalar()
    if not isinstance(binding, str) or re.fullmatch(r"[0-9a-f]{64}", binding) is None:
        raise ValueError("invalid manifest binding")
    return ControlRecord(raw, notices=notices, source_sha256=sources, view_manifest_sha256=binding)


def render_record(record):
    if not isinstance(record, ControlRecord):
        return json.dumps(record, indent=2)
    edits, additions = [], []
    for key in ("notices", "source_differing_paths", "records.thermal_view_changed", "view_differing_paths"):
        value = record[key]
        encoded = ("[" + ", ".join(n.raw if isinstance(n, RetainedNotice) else json.dumps(n) for n in value) + "]"
                   if key == "notices" else json.dumps(value))
        try:
            a, z = field_span(record.raw, (key,))
            edits.append((a, z, encoded))
        except ValueError:
            additions.append(json.dumps(key) + ": " + encoded)
    if additions:
        # A valid record already contains required fields, so a comma is needed.
        close = tokens_of(record.raw)[-1].start(1)
        edits.append((close, close, ", " + ", ".join(additions)))
    return replace(record.raw, edits)


def validate_manifest(raw):
    doc = document(raw)
    rows = []
    for node in doc.field("files").elements():
        rows.append({key: value.scalar() for key, value in node.fields()
                     if key in {"path", "size", "sha256", "mtime_ns", "inode"}})
    return manifest_entries({"files": rows})


def verify(output):
    output = Path(output).resolve()
    if not output.is_dir():
        return ["output missing"]
    record_path = output / "thermal_line.json"
    different, reasons = [], []
    # Roots from links survive damage to the record; record paths count only
    # after the entire control document and its consumed fields validate.
    source_roots = linked_roots(output)
    try:
        if record_path.is_dir():
            raise ValueError("thermal line record is a directory")
        record = validate_record(record_path.read_bytes().decode("utf-8"))
        for source in record["source_sha256"]:
            path = Path(source).resolve()
            source_roots.append(path.parent.parent if path.name == "b6-acceptance.json" else path.parent)
    except (OSError, ValueError, TypeError, RecursionError):
        record = {"notices": []}
        different.append("thermal_line.json")
        reasons.append("thermal line record missing or invalid")
    manifest_path = output / "view_manifest.json"
    try:
        if sha256(manifest_path) != record["view_manifest_sha256"]:
            different.append("view_manifest.json")
            reasons.append("manifest SHA-256 differs from recorded binding")
        expected = validate_manifest(manifest_path.read_bytes().decode("utf-8"))
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        expected = {}
        different.append("view_manifest.json")
        reasons.append("manifest invalid: " + (str(exc) if type(exc) is ValueError else type(exc).__name__))
    current = {row["path"]: row for row in view_files(output)}
    different.extend(path for path in sorted(expected.keys() | current.keys())
                     if expected.get(path) != current.get(path))
    changed_sources = []
    for source, digest in record.get("source_sha256", {}).items():
        try:
            changed = sha256(Path(source)) != digest
        except (OSError, ValueError):
            changed = True
        if changed:
            changed_sources.append(source)
    record["source_differing_paths"] = sorted(changed_sources)
    record["records.thermal_view_changed"] = bool(different or changed_sources)
    record["notices"] = [notice for notice in record["notices"]
                         if notice["code"] != "records.thermal_view_changed"]
    if different or changed_sources:
        if changed_sources:
            reasons.append("source changed since transform")
        record["notices"].append({"code": "records.thermal_view_changed",
                                  "reason": "; ".join(reasons) if reasons else "payload differs from manifest"})
    record["view_differing_paths"] = sorted(set(different))
    if any(output.is_relative_to(root) for root in source_roots) or record_path.is_dir():
        print(render_record(record))
    else:
        write_copy(record_path, render_record(record) + "\n", output)
    return record["view_differing_paths"] + [
        "source changed since transform: " + path for path in record["source_differing_paths"]]


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
