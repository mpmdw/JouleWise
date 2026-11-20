"""Fixture transport adapter. The assertions use queue positions, records and digests."""
import hashlib
import json
from pathlib import Path


def canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode()


def position(desk):
    queue = json.loads(desk.queue)
    entry = next(row for row in queue["spans"] if row["span_id"] == desk.item["span"])
    return hashlib.sha256(desk.queue).hexdigest(), entry["seq"]


def queue_file(desk):
    digest, seq = position(desk)
    return desk.args.queue_hold_root / f"{digest}-{seq}.json"


def read_custody(desk):
    """Read stored bytes without calling a candidate journal, verifier or admission decision."""
    opens, clears, immutable = {}, {}, {}
    ledger = desk.args.custody / "hp-02-arms"
    for path in sorted(ledger.glob("holds-*/*.json")):
        data = path.read_bytes()
        event = json.loads(data)
        sequence = int(path.name.split("-", 1)[0])
        immutable[str(path)] = hashlib.sha256(data).hexdigest()
        for hold in event["holds"]:
            opens[hold["id"]] = {**hold, "issue_id": event["issue_id"], "ledger_sequence": sequence}
        for clearance in event["clears"]:
            clears[clearance["hold_id"]] = clearance
            opens.pop(clearance["hold_id"], None)
    root = desk.args.queue_hold_root
    queue_sha, queue_seq = position(desk)
    for path in sorted(root.rglob("*.json")) if root.exists() else ():
        data = path.read_bytes()
        event = json.loads(data)
        if (event.get("queue_sha"), event.get("queue_seq")) != (queue_sha, queue_seq):
            continue
        # An implementation can adapt this wire projection to another file layout.
        for hold in event.get("holds", [event] if "id" in event else []):
            opens[hold["id"]] = {**hold, "queue_sha": queue_sha, "queue_seq": queue_seq}
        for clearance in event.get("clears", []):
            clears[clearance["hold_id"]] = clearance
            opens.pop(clearance["hold_id"], None)
    return opens, clears, immutable
