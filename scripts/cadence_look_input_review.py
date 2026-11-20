#!/usr/bin/env python3
"""The one-time review record of a look's pinned inputs (RL-194 section 1, conditions 5 and 6).

    python3 -B scripts/cadence_look_input_review.py template --manifest MANIFEST.json --repo DIR
    python3 -B scripts/cadence_look_input_review.py review --manifest MANIFEST.json --repo DIR --custody ROOT
        [--span-dir SPAN_ID=PATH ...] [--run-state RUN_STATE.md] --seat-model NAME --seat-family NAME
        --out RECORD.json
    python3 -B scripts/cadence_look_input_review.py check RECORD.json --manifest MANIFEST.json --repo DIR

``template`` prints the record with every slot the seat and the lead fill left null. ``review`` is the executing
seat's run. It opens operational files only (each span's receipt, soak reference, leg records and summaries and the
selected bundles' journals), every one through its pin: the bytes are read once, hashed, compared with the pin and
only then decoded. A trace, telemetry or meter file is bound by its pin and never opened here. For each receipt it
records the shape found for RL-184 section 3.3's F01 to F05, the pinned writer's file and lines that produce the
shape, and whether the shape is one the rule admits; the criteria are the rule's as written, and nothing is decided
on seeing a file. The span's verdict is the pinned grammar validator's. The desk's verdict is the lead's to copy in
from the row-7 desk record. For each span the record also carries how its public Check item names the offload
manifest (RL-194a section 2): the full digest, the text exactly as the Check prints it, the item number, and a slot
for any second record made at the time, which is cited when one exists and is not required. ``--run-state`` reads a
file; the default is RUN_STATE.md on origin/main. ``check`` requires a filled record to carry the manifest's pins, every slot, and the same
verdict from the desk and the seat on every span; a disagreement or an inadmissible span goes to the research lead as
a count and a shape before anything is changed.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise.cadence_looks import admission, custody_pins, manifest as lm  # noqa: E402

SCHEMA = "joulewise.cadence_look_input_review.v1"
VERDICTS = ("admissible", "inadmissible")
RULES = ("F01", "F02", "F03", "F04", "F05")
ATTEMPT_KEYS = ["attempt", "output_dir", "refused", "started_epoch_s"]
# The pinned writer lines that produce each shape, as GRAMMAR.md of the frozen admission packet cites them; the seat
# confirms them at the span's pin. F01 is the leg result's bundle locator; F02 to F05 are the runner's soak history.
WRITER = {
    "F01": {"A": ("joulewise/align/apple/cadence_leg.py", "82-148"), "B": ("joulewise/align/apple/cadence_leg.py", "150-225"),
            "C": ("joulewise/align/apple/cadence_leg.py", "150-225")},
    **{rule: {"A": ("scripts/cadence_legs_runner.py", "365-466"), "B": ("scripts/cadence_legs_runner.py", "368-491"),
              "C": ("scripts/cadence_legs_runner.py", "453,575-605")} for rule in ("F02", "F03", "F04", "F05")},
}
CRITERIA = ("RL-184 section 3.3's rule and F01 to F05 as written; operational files only; nothing re-decided on "
            "seeing the files (RL-194 condition 5)")


class PinnedOperational:
    """One span's operational files, each read once through its pin. Anything else is not opened."""

    def __init__(self, span, directory, opened):
        self.span, self.directory, self.opened = span, Path(directory), opened
        self.pins = {entry["path"]: entry for entry in span["files"]}
        self.cache = {}

    def exists(self, rel):
        return rel in self.pins

    def read(self, rel):
        if rel in self.cache:
            return self.cache[rel]
        if not lm.is_operational_path(rel):
            raise custody_pins.PinRefusal(f"{self.span['span_id']}/{rel}: not an operational file; the review does not open it")
        pin = self.pins.get(rel)
        if pin is None:
            return None                              # an optional operational file the span does not have
        path = self.directory.joinpath(*rel.split("/"))
        if path.is_symlink():
            raise custody_pins.PinRefusal(f"{self.span['span_id']}/{rel}: a symlink")
        data = path.read_bytes()
        if len(data) != pin["size"] or hashlib.sha256(data).hexdigest() != pin["sha256"]:
            raise custody_pins.PinRefusal(f"{self.span['span_id']}/{rel}: its bytes are not its pin")
        self.opened.append(f"{self.span['span_id']}/{rel}")
        self.cache[rel] = data
        return data


def _spelling(locator):
    if locator is None:
        return "absent"
    if not isinstance(locator, str) or not locator or "\0" in locator or locator.startswith("/") \
            or any(part in ("", ".", "..") for part in locator.split("/")):
        return "invalid"
    return "nested" if "/" in locator else "single_component"


def receipt_shapes(receipt, records, pin):
    """The shape of one receipt for F01 to F05 and whether the rule admits it. ``records`` maps each roster leg id to
    its decoded leg record or None; ``pin`` is the writer revision letter (A, B or C)."""
    steps = receipt.get("steps") if isinstance(receipt.get("steps"), list) else []
    soak_steps = [step for step in steps if isinstance(step, dict) and isinstance(step.get("name"), str)
                  and (step["name"] == "soak" or step["name"].startswith("soak.a"))]
    attempts = receipt.get("soak_attempts")
    rows = attempts if isinstance(attempts, list) else []
    locators = sorted({(record.get("result") or {}).get("bundle") for record in records.values()
                       if isinstance(record, dict) and isinstance(record.get("result") or {}, dict)},
                      key=lambda value: (value is None, str(value)))
    spellings = sorted({_spelling(value) for value in locators}) or ["absent"]
    f01 = {"shape": {"bundle_spelling": spellings, "locators": locators},
           "verdict": "inadmissible" if "invalid" in spellings else "admissible"}

    if "soak_attempts" not in receipt:
        state = "absent"
    elif not isinstance(attempts, list):
        state = "not_a_list"
    elif not rows:
        state = "empty"
    else:
        refused = [isinstance(row, dict) and row.get("refused") is not None for row in rows]
        state = {(False,): "one_accepted", (True,): "one_refused", (True, False): "refused_then_accepted",
                 (True, True): "refused_twice"}.get(tuple(refused), f"{len(rows)}_rows")
    admitted = (state == "absent") if pin in ("A", "B") else (
        state in ("one_accepted", "one_refused", "refused_then_accepted", "refused_twice")
        or (state == "empty" and not soak_steps))
    f02 = {"shape": {"soak_attempts": state, "soak_steps": len(soak_steps)},
           "verdict": "admissible" if admitted else "inadmissible"}

    key_sets = sorted({json.dumps(sorted(row) if isinstance(row, dict) else None) for row in rows})
    rc_states = sorted({"absent" if "rc" not in step else "null" if step["rc"] is None
                        else "integer" if type(step["rc"]) is int else "other" for step in soak_steps})
    f03 = {"shape": {"attempt_keys": [json.loads(keys) for keys in key_sets], "soak_step_rc": rc_states},
           "verdict": "admissible" if all(json.loads(keys) == ATTEMPT_KEYS for keys in key_sets)
           and "other" not in rc_states else "inadmissible"}

    names = [step["name"] for step in soak_steps]
    if pin in ("A", "B"):
        coherent = names in ([], ["soak"])
        history = "no_soak_step" if not names else "one_soak_step" if coherent else "repeated_soak_steps"
    else:
        expected = ["soak", "soak.a2"][:len(rows)]
        numbered = [row.get("attempt") if isinstance(row, dict) else None for row in rows] == list(range(1, len(rows) + 1))
        coherent = numbered and len(rows) <= 2 and (names == expected or (bool(rows) and names == expected[:-1]))
        history = "one_row_per_soak_step" if coherent and names == expected else \
            "last_row_one_ahead" if coherent else "rows_and_steps_differ"
    f04 = {"shape": {"history": history, "soak_step_names": names}, "verdict": "admissible" if coherent else "inadmissible"}

    kinds = sorted({str(row.get("kind")) for row in receipt.get("soak_refusals") or [] if isinstance(row, dict)}) \
        if isinstance(receipt.get("soak_refusals"), list) else []
    f05 = {"shape": {"soak_refusals": "absent" if "soak_refusals" not in receipt else "present", "kind_values": kinds},
           "verdict": "admissible" if "soak_refusals" not in receipt or set(kinds) <= {"slope", "load"} else "inadmissible"}
    return {"F01": f01, "F02": f02, "F03": f03, "F04": f04, "F05": f05}


def template(pin_list, pin_list_sha256, manifest_sha256):
    """The record with the pins filled from the manifest and every slot the seat and the lead fill left null."""
    return {
        "schema": SCHEMA, "look_id": lm.INTERIM_LOOK_ID,
        "header": {"pin_list_sha256": pin_list_sha256, "manifest_sha256": manifest_sha256,
                   "seat": {"model": None, "family": None}, "command": None, "date": None, "files_opened": None,
                   "criteria": CRITERIA},
        "spans": [{
            **{key: span[key] for key in custody_pins.SPAN_KEYS},
            "check": {"item": span["check_item"], "offload_manifest_sha256": span["offload_manifest_sha256"],
                      "as_printed": None, "form": None, "second_record": None},
            "receipt": {"path": admission.RECEIPT, "writer_pin": admission.PINS.get(span["runner_commit"]),
                        "kit_frozen_commit": None, "kit_frozen_commit_is_runner_commit": None,
                        "shapes": {rule: {"shape": None, "writer": _writer(rule, admission.PINS.get(span["runner_commit"])),
                                          "verdict": None} for rule in RULES}},
            "verdicts": {"desk": None, "executing_seat": None, "executing_seat_refusal": None},
        } for span in pin_list["spans"]],
    }


def _writer(rule, pin):
    cite = WRITER[rule].get(pin)
    return {"file": cite[0], "lines": cite[1]} if cite else {"file": None, "lines": None}


def review(pin_list, pin_list_sha256, manifest_sha256, sdir_of, *, seat_model, seat_family, command, run_state):
    """The executing seat's record: shapes and verdicts from the operational files, each read through its pin, and
    how each span's Check item in ``run_state`` (the public RUN_STATE's text) prints its offload manifest digest."""
    record = template(pin_list, pin_list_sha256, manifest_sha256)
    opened = []
    for span, row in zip(pin_list["spans"], record["spans"]):
        binding = custody_pins.check_binding(span, run_state)
        row["check"].update(as_printed=binding["as_printed"], form=binding["form"])
        files = PinnedOperational(span, sdir_of(span["span_id"]), opened)
        try:
            receipt = admission.decode(files.read(admission.RECEIPT), f"{span['span_id']}/{admission.RECEIPT}")
            roster = receipt.get("roster") if isinstance(receipt, dict) else None
            records = {}
            for leg_id in roster if isinstance(roster, list) else []:
                raw = files.read(f"legs/{leg_id}/leg_record.json") if isinstance(leg_id, str) and leg_id else None
                records[leg_id if isinstance(leg_id, str) else repr(leg_id)] = (
                    admission.decode(raw, f"{span['span_id']}/legs/{leg_id}/leg_record.json") if raw is not None else None)
            frozen = (receipt.get("kit") or {}).get("frozen_commit") if isinstance(receipt.get("kit"), dict) else None
            pin = row["receipt"]["writer_pin"] or admission.PINS.get(frozen)
            row["receipt"].update(writer_pin=pin, kit_frozen_commit=frozen,
                                  kit_frozen_commit_is_runner_commit=frozen == span["runner_commit"])
            for rule, found in receipt_shapes(receipt, records, pin).items():
                row["receipt"]["shapes"][rule].update(found, writer=_writer(rule, pin))
            admission.validate_span(files, span["span_id"])
            row["verdicts"].update(executing_seat="admissible")
        except admission.Refusal as refusal:
            row["verdicts"].update(executing_seat="inadmissible", executing_seat_refusal=str(refusal))
    record["header"].update(seat={"model": seat_model, "family": seat_family}, command=command,
                            date=date.today().isoformat(), files_opened=opened)
    return record


def record_problems(record, pin_list, pin_list_sha256, manifest_sha256):
    """Problems of a filled record against the manifest's pins. A disagreement between the desk and the seat, or an
    inadmissible span, is a problem here: it goes to the research lead before anything is changed."""
    problems = []
    if not isinstance(record, dict) or record.get("schema") != SCHEMA or record.get("look_id") != lm.INTERIM_LOOK_ID:
        return ["the record is not a joulewise.cadence_look_input_review.v1 record of lm-interim-01"]
    header = record.get("header") or {}
    if header.get("pin_list_sha256") != pin_list_sha256:
        problems.append("header.pin_list_sha256 is not the manifest's inputs pin")
    if header.get("manifest_sha256") != manifest_sha256:
        problems.append("header.manifest_sha256 is not this manifest")
    seat = header.get("seat") or {}
    for key in ("model", "family"):
        if not (isinstance(seat.get(key), str) and seat[key]):
            problems.append(f"header.seat.{key}: the executing seat's, not the builder's")
    if not (isinstance(header.get("command"), list) and header["command"] and all(isinstance(w, str) for w in header["command"])):
        problems.append("header.command: the command the seat ran")
    if not (isinstance(header.get("date"), str) and header["date"]):
        problems.append("header.date")
    opened = header.get("files_opened")
    if not (isinstance(opened, list) and opened and all(isinstance(name, str) for name in opened)):
        problems.append("header.files_opened: the files the seat opened")
    else:
        for name in opened:
            sid, _, rel = name.partition("/")
            if not lm.is_operational_path(rel):
                problems.append(f"header.files_opened: {name} is not an operational file")
    spans = record.get("spans")
    if not isinstance(spans, list) or [s.get("span_id") if isinstance(s, dict) else None for s in spans] != [
            span["span_id"] for span in pin_list["spans"]]:
        return problems + ["spans: not the manifest's pinned spans, in its order"]
    counts = {"agree": 0, "disagree": 0, "inadmissible": 0}
    for row, span in zip(spans, pin_list["spans"]):
        sid = span["span_id"]
        if any(row.get(key) != span[key] for key in custody_pins.SPAN_KEYS):
            problems.append(f"{sid}: its pins or Check items are not the manifest's")
        check = row.get("check") or {}
        printed = check.get("as_printed")
        if check.get("item") != span["check_item"] or check.get("offload_manifest_sha256") != span["offload_manifest_sha256"]:
            problems.append(f"{sid}: check does not carry the manifest's Check item and full offload manifest digest")
        elif check.get("form") == "full" and printed == span["offload_manifest_sha256"]:
            pass
        elif check.get("form") == "abbreviated" and isinstance(printed, str) and custody_pins.check_binding(
                span, f"{span['check_item']}. **as printed** {printed}\n")["as_printed"] == printed:
            pass
        else:
            problems.append(f"{sid}: its Check item does not print a digest every character of which matches; the "
                            "span is held and returns to the research lead")
        if check.get("second_record") is not None and not (isinstance(check["second_record"], str) and check["second_record"]):
            problems.append(f"{sid}: check.second_record is a citation or null")
        shapes = ((row.get("receipt") or {}).get("shapes") or {})
        for rule in RULES:
            slot = shapes.get(rule) or {}
            writer = slot.get("writer") or {}
            if slot.get("shape") is None or slot.get("verdict") not in VERDICTS \
                    or not (isinstance(writer.get("file"), str) and isinstance(writer.get("lines"), str)):
                problems.append(f"{sid}: {rule} lacks its shape, its writer file and lines, or its verdict")
            elif slot["verdict"] == "inadmissible":
                problems.append(f"{sid}: {rule} shape is inadmissible; to the research lead as a count and a shape")
        verdicts = row.get("verdicts") or {}
        desk, seat_verdict = verdicts.get("desk"), verdicts.get("executing_seat")
        if desk not in VERDICTS or seat_verdict not in VERDICTS:
            problems.append(f"{sid}: the desk's and the executing seat's verdicts are both required")
        elif desk != seat_verdict:
            counts["disagree"] += 1
            problems.append(f"{sid}: the desk and the executing seat disagree; the disagreement returns to the research lead")
        else:
            counts["agree"] += 1
            if desk == "inadmissible":
                counts["inadmissible"] += 1
                problems.append(f"{sid}: inadmissible; to the research lead as a count and a shape, nothing is changed")
    return problems


def _load(args):
    doc = lm.load_json(Path(args.manifest))
    pin_list, sha = lm.input_pins(args.repo, doc, complete=True)
    return pin_list, sha, lm.sha256_file(Path(args.manifest))


def dump(record):
    return (json.dumps(record, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("template", "review", "check"):
        command = sub.add_parser(name)
        if name == "check":
            command.add_argument("record")
        command.add_argument("--manifest", required=True)
        command.add_argument("--repo", required=True)
    run = sub.choices["review"]
    run.add_argument("--custody", required=True)
    run.add_argument("--span-dir", action="append", default=[])
    run.add_argument("--run-state")
    run.add_argument("--seat-model", required=True)
    run.add_argument("--seat-family", required=True)
    run.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        pin_list, sha, manifest_sha = _load(args)
        if args.cmd == "template":
            sys.stdout.buffer.write(dump(template(pin_list, sha, manifest_sha)))
            return 0
        if args.cmd == "check":
            problems = record_problems(json.loads(Path(args.record).read_bytes()), pin_list, sha, manifest_sha)
            for problem in problems:
                print(f"REFUSE {problem}")
            if not problems:
                print(f"ok {len(pin_list['spans'])} of {len(pin_list['spans'])} spans admissible; the desk and the "
                      f"executing seat agree on all; record sha256 {lm.sha256_file(Path(args.record))}")
            return 1 if problems else 0
        overrides = dict(pair.partition("=")[::2] for pair in args.span_dir)
        run_state = (Path(args.run_state).read_text(encoding="utf-8") if args.run_state
                     else lm.public_run_state(args.repo))
        record = review(pin_list, sha, manifest_sha,
                        lambda sid: Path(overrides.get(sid) or os.path.join(args.custody, sid)),
                        run_state=run_state, seat_model=args.seat_model, seat_family=args.seat_family,
                        command=[Path(sys.argv[0]).name, *(argv if argv is not None else sys.argv[1:])])
        Path(args.out).write_bytes(dump(record))
        seat = [row["verdicts"]["executing_seat"] for row in record["spans"]]
        print(f"wrote {args.out} sha256={lm.sha256_file(Path(args.out))}: {seat.count('admissible')} admissible, "
              f"{seat.count('inadmissible')} inadmissible by the executing seat; "
              f"{len(record['header']['files_opened'])} operational files opened")
        return 0
    except lm.ManifestError as error:
        for problem in error.problems:
            print(f"REFUSE {problem}")
        return 1
    except custody_pins.PinRefusal as refusal:
        print(f"REFUSE custody pins: {refusal}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
