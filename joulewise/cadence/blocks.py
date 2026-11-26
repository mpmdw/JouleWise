"""BLOCK-QUEUE: the ledger of scientific blocks designed ahead of the MBP.

File: ``docs/process/cadence/BLOCK-QUEUE.json`` (schema ``joulewise.cadence_block_queue.v1``).
A *block* is the study's unit of independence (a scientific block); a *span* is
the operational container the MBP runs. One block maps to one or more spans in
``QUEUE.json``; more spans on a day never make more independent blocks.

Statuses, in order: DRAFT -> SPECIFIED -> REVIEWED -> AUTHORIZED -> READY ->
ASSIGNED -> COLLECTED -> DESK_FINAL; side exits HALTED and WITHDRAWN.

``READY`` is earned, not typed: ``validate_ledger`` refuses a block at READY or
later without a kit pin, at least one review record and a ruling. "Designed
except for one ruling" is AUTHORIZED at most. ``ready_ahead`` counts READY blocks
not yet assigned; ``status_lines`` raises DESIGN_QUEUE_LOW below ``ready_min``.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

SCHEMA = "joulewise.cadence_block_queue.v1"
LEDGER_PATH = "docs/process/cadence/BLOCK-QUEUE.json"
ORDER = ("DRAFT", "SPECIFIED", "REVIEWED", "AUTHORIZED", "READY", "ASSIGNED", "COLLECTED", "DESK_FINAL")
SIDE = ("HALTED", "WITHDRAWN")
STATUSES = ORDER + SIDE
BLOCK_KEYS = {"design_id", "title", "question", "phase", "block_definition", "kit", "est_legs", "est_spans",
              "depends_on", "reviews", "ruling", "status", "ready_since", "expires", "assigned_span_ids",
              "owner", "notes"}
TOP_KEYS = {"schema", "updated", "ready_min", "ready_max", "blocks"}
ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,40}")
PHASES = {"pilot", "development", "qualification", "extension", "reserve"}


class LedgerError(ValueError):
    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems))


def at_least(status, floor):
    return status in ORDER and ORDER.index(status) >= ORDER.index(floor)


def validate_ledger(doc, kits_root=None):
    problems = []
    if not isinstance(doc, dict):
        raise LedgerError(["ledger: object"])
    for k in sorted(set(doc) ^ TOP_KEYS):
        problems.append(f"ledger: {'unknown' if k in doc else 'missing'} key {k!r}")
    if doc.get("schema") != SCHEMA:
        problems.append(f"schema: {SCHEMA}")
    lo, hi = doc.get("ready_min"), doc.get("ready_max")
    if not (type(lo) is int and type(hi) is int and 1 <= lo <= hi):
        problems.append("ready_min/ready_max: integers, 1 <= min <= max")
    ids = set()
    for i, b in enumerate(doc.get("blocks") or []):
        where = f"blocks[{i}]"
        if not isinstance(b, dict):
            problems.append(f"{where}: object")
            continue
        for k in sorted(set(b) ^ BLOCK_KEYS):
            problems.append(f"{where}: {'unknown' if k in b else 'missing'} key {k!r}")
        did = b.get("design_id")
        if not (isinstance(did, str) and ID_RE.fullmatch(did)) or did in ids:
            problems.append(f"{where}.design_id: unique lowercase id")
        ids.add(did)
        st = b.get("status")
        if st not in STATUSES:
            problems.append(f"{where}.status: one of {STATUSES}")
            continue
        if b.get("phase") not in PHASES:
            problems.append(f"{where}.phase: one of {sorted(PHASES)}")
        for dep in b.get("depends_on") or []:
            if dep not in ids - {did}:
                problems.append(f"{where}.depends_on: {dep} is not an earlier block")
        kit = b.get("kit")
        if at_least(st, "SPECIFIED") and not (isinstance(b.get("block_definition"), str) and b["block_definition"].strip()):
            problems.append(f"{where}: SPECIFIED needs block_definition (what makes it an independent block)")
        if at_least(st, "REVIEWED") and not b.get("reviews"):
            problems.append(f"{where}: REVIEWED needs at least one review record")
        if at_least(st, "AUTHORIZED") and not (isinstance(b.get("ruling"), str) and re.fullmatch(r"RL-\d+[a-z]?(?: §\d{1,2}(?:\.\d{1,2})?)?", b["ruling"])):
            problems.append(f"{where}: AUTHORIZED needs a ruling RL-<n>")
        if at_least(st, "READY"):
            if not (isinstance(kit, dict) and set(kit) == {"path", "sha256"}):
                problems.append(f"{where}: READY needs kit {{path, sha256}}")
            elif kits_root is not None:
                from joulewise.cadence import kit as kitmod
                try:
                    _, sha = kitmod.load_kit(Path(kits_root) / kit["path"])
                except (OSError, kitmod.KitError) as error:
                    problems.append(f"{where}: kit does not validate ({str(error)[:160]})")
                else:
                    if sha != kit["sha256"]:
                        problems.append(f"{where}: kit sha256 pin differs from the file")
            if not b.get("ready_since"):
                problems.append(f"{where}: READY needs ready_since")
        if at_least(st, "ASSIGNED") and not b.get("assigned_span_ids"):
            problems.append(f"{where}: ASSIGNED needs assigned_span_ids")
    if problems:
        raise LedgerError(problems)
    return doc


def ready_ahead(doc):
    return [b for b in doc["blocks"] if b["status"] == "READY"]


def status_lines(doc):
    lines = [f"{'design_id':<16} {'phase':<13} {'status':<11} {'legs':>5} {'spans':>5}  ruling   title",
             "-" * 88]
    for b in doc["blocks"]:
        lines.append(f"{b['design_id']:<16} {b['phase']:<13} {b['status']:<11} {str(b.get('est_legs') or '-'):>5} "
                     f"{str(b.get('est_spans') or '-'):>5}  {str(b.get('ruling') or '-'):<8} {b['title']}")
    n = len(ready_ahead(doc))
    running = [b["design_id"] for b in doc["blocks"] if b["status"] == "ASSIGNED"]
    lines.append("")
    lines.append(f"ready ahead: {n} (target {doc['ready_min']}-{doc['ready_max']}); running/assigned: {running or 'none'}")
    if n < doc["ready_min"]:
        nxt = next((b["design_id"] for b in doc["blocks"] if b["status"] in ORDER[:4]), None)
        lines.append(f"DESIGN_QUEUE_LOW: fewer than {doc['ready_min']} READY block(s); advance {nxt or 'a new design'}")
    return lines


def load_ledger(path, kits_root=None):
    return validate_ledger(json.loads(Path(path).read_text(encoding="utf-8")), kits_root)
