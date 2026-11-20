"""Synthetic custody: the closed shape ``scripts/cadence_look_synth.write_custody`` writes.

No pinned writer issues ``"synthetic": true``; this repository's generator is the only producer, and its spans are
admitted only as a whole roster (``admission.validate_roster``). A synthetic span's receipt, soak reference, leg
records and summaries are exactly the generator's; its runtime bundles are writer-shaped and go through the same
journal grammar as a written span's (``admission_journals``).
"""
from __future__ import annotations

from joulewise.cadence_looks import admission_journals as journals
from joulewise.cadence_looks.admission_shape import (
    BOOL, INT, NAT, NUM, POS, arr, const, decode, decode_lines, enum, nullable, obj, refuse, rx)

RECEIPT_SCHEMA = "joulewise.cadence_span_receipt.v1"
SOAK_SCHEMA = "joulewise.align.r1_soak_reference.v1"
LEG_ID = rx(r"[LH][0-9]{3}")                 # the generator's development (L) and describe (H) legs
_STEPS = [{"name": "soak", "rc": 0}]


def _locator(name, where):
    if type(name) is not str or "\0" in name or not name or any(p in ("", ".", "..") for p in name.split("/")):
        refuse(where, "invalid runtime bundle path (RL-184 F01)")


_RECEIPT = obj({"schema": const(RECEIPT_SCHEMA), "started": obj({"epoch_s": NUM}), "roster": arr(LEG_ID, least=1),
                "synthetic": const(True), "rc": const(0), "steps": lambda v, w: None})
_RESULT = obj({"leg_status": enum("complete", "incomplete", "g0_unreleased"), "decode_cap_reached": BOOL,
               "g0_released": BOOL, "ac_powermode": obj({"value": INT}),
               "bundle": nullable(_locator), "prefill_tokens": nullable(NAT)})


def validate_span(files, receipt, docs, where):
    at = f"{where}/runner_receipt.json"
    _RECEIPT(receipt, at)
    if receipt["steps"] != _STEPS or type(receipt["steps"][0]["rc"]) is not int:
        refuse(f"{at}.steps", "not the generator's soak step")
    roster = receipt["roster"]
    if len(set(roster)) != len(roster):
        refuse(f"{at}.roster", "a leg selected twice")
    raw = files.read("soak/soak_reference.json")
    if raw is None:
        refuse(f"{where}/soak/soak_reference.json", "absent")
    docs["soak/soak_reference.json"] = decode(raw, f"{where}/soak/soak_reference.json")
    from joulewise.cadence_looks import admission
    admission._soak_reference(docs["soak/soak_reference.json"], f"{where}/soak/soak_reference.json", False)
    for position, leg_id in enumerate(roster):
        record_rel, summary_rel = f"legs/{leg_id}/leg_record.json", f"legs/{leg_id}/leg_summary.json"
        raw_record, raw_summary = files.read(record_rel), files.read(summary_rel)
        if raw_record is None and raw_summary is None:
            continue                                    # the span stopped before this leg (R-21)
        if raw_record is None or raw_summary is None:
            refuse(f"{where}/{record_rel if raw_record is None else summary_rel}", "absent beside its pair")
        record = docs[record_rel] = decode(raw_record, f"{where}/{record_rel}")
        summary = docs[summary_rel] = decode(raw_summary, f"{where}/{summary_rel}")
        obj({"spec": obj({"leg_id": const(leg_id), "prefill_tokens": nullable(NAT)},
                         {"g0_role": enum("capture", "consume"), "leg_type": const("T")}),
             "attempts": arr(obj({"attempt": POS, "contaminated": BOOL}), most=1),
             "result": _RESULT})(record, f"{where}/{record_rel}")
        for index, attempt in enumerate(record["attempts"]):
            if attempt["attempt"] != index + 1:
                refuse(f"{where}/{record_rel}.attempts[{index}].attempt", "not numbered from 1")
        obj({"leg_id": const(leg_id)}, {"span_reference": obj(
            {"leg_id": const(roster[0]), "attempt": const(1), "redone": BOOL, "excluded": BOOL})})(
            summary, f"{where}/{summary_rel}")
        if ("span_reference" in summary) != (record["spec"].get("g0_role") == "consume" and position > 0):
            refuse(f"{where}/{summary_rel}.span_reference", "exactly on a consumer of the span reference")
        bundle = record["result"]["bundle"]
        if bundle is None:
            continue
        base = f"legs/{leg_id}/runtime/{bundle}"
        if files.exists(f"{base}/{journals.SALVAGE.split('/')[-1]}"):
            refuse(f"{where}/{base}/align_runtime_events.jsonl", "salvage events outside outputs/")
        present = {}
        for name in (journals.CONFIG, journals.EVENTS, journals.TURNS, journals.THERMAL, journals.SALVAGE):
            raw = files.read(f"{base}/{name}")
            if raw is not None:
                rel = f"{base}/{name}"
                docs[rel] = present[name] = decode_lines(raw, f"{where}/{rel}") if name.endswith(".jsonl") else \
                    decode(raw, f"{where}/{rel}")
        if present:
            journals.validate_bundle(present, f"{where}/{base}", {"pin": None, "leg_id": leg_id,
                                                                  "result": record["result"], "spec": record["spec"]})
