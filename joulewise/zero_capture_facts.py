"""Read-only, fail-closed disk facts shared by release and successor admission.

The disk scan uses the Python standard library and selects the recognised
night-kind row. A missing scan root is empty only after the real custody root
and delivered result/receipt are established.
"""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shlex
import stat


@dataclass(frozen=True)
class ZeroCaptureFacts:
    custody_root_present: bool = False
    courier_sent: bool = False
    result_readable: bool = False
    receipt_readable: bool = False
    chain_started: int = 0
    reservation_markers_found: int = 0
    capture_entries_found: int = 0
    envelope_index_state: str = "unknown"
    envelopes_captured: int = 0
    scan_complete: bool = False

    @property
    def clean(self):
        return (self.custody_root_present and self.courier_sent
                and self.result_readable and self.receipt_readable
                and self.scan_complete and self.chain_started == 0
                and self.reservation_markers_found == 0
                and self.capture_entries_found == 0
                and self.envelope_index_state in ("absent", "empty", "not_applicable")
                and self.envelopes_captured == 0)


def _mode(path):
    try:
        return os.lstat(path).st_mode
    except FileNotFoundError:
        return None


def _tree_count(root, predicate):
    """Count matches at every depth; symlinks and irregular roots are facts."""
    mode = _mode(root)
    if mode is None:
        return 0
    if not stat.S_ISDIR(mode):
        return 1
    count = 0
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_symlink():
                    count += 1
                elif entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))
                elif predicate(entry.name):
                    count += 1
    return count


def _literal(text, name):
    matches = re.findall(r"^export " + re.escape(name) + r"=(.*)$", text, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError("missing or ambiguous chain literal: " + name)
    words = shlex.split(matches[0])
    if len(words) != 1 or any(c in words[0] for c in "$`\n\r"):
        raise ValueError("nonliteral chain value: " + name)
    return words[0]


def zero_capture_facts(plan):
    """Return immutable facts for a delivered plan, never licensing torn custody."""
    custody = Path(plan.custody_root)
    root_mode = _mode(custody)
    if root_mode is None or not stat.S_ISDIR(root_mode):
        return ZeroCaptureFacts()
    night = custody / "night"
    sent = _mode(night / "courier.sent") is not None
    try:
        result = json.loads((night / "result.json").read_text(encoding="utf-8"))
        receipt = json.loads((night / "receipt.json").read_text(encoding="utf-8"))
        if not isinstance(result, dict) or not isinstance(receipt, dict):
            raise ValueError("result and receipt must be objects")
    except (OSError, UnicodeError, ValueError, TypeError):
        return ZeroCaptureFacts(custody_root_present=True, courier_sent=sent)
    base = dict(custody_root_present=True, courier_sent=sent,
                result_readable=True, receipt_readable=True)
    if not sent:
        return ZeroCaptureFacts(**base)
    try:
        chain = Path(plan.chain_path).read_text(encoding="utf-8")
        from joulewise.night_gate import probe_payload_kind
        from joulewise.night_kinds import kind_row
        row = kind_row(probe_payload_kind(chain))
        if row.handler not in ("evidence", "calibration") or not row.successor_release:
            raise ValueError("payload kind has no approved successor handler")
        evidence = row.handler == "evidence"
        runs_root = None
        if not evidence:
            runs_root = Path(_literal(chain, "RUNS_ROOT"))
            # run_night.py:536 creates chain.started before the chain starts at
            # run_night.py:3170; any ledger session is appended inside that
            # chain. No chain.started therefore also means no ledger session.
            if not runs_root.is_absolute():
                raise ValueError("relative calibration root")
        reservations = _tree_count(custody, lambda name: name.endswith(".consumed.json"))
        if runs_root is not None:
            reservations += _tree_count(runs_root, lambda name: name.endswith(".consumed.json"))
            captures = _tree_count(runs_root / "instrument_validation", lambda _: True)
            index_state = "not_applicable"
            envelopes = 0
        else:
            captures = _tree_count(night / row.artifact_dir, lambda _: True)
            index = night / row.envelope_index_name
            index_mode = _mode(index)
            if index_mode is None:
                index_state, envelopes = "absent", 0
            elif not stat.S_ISREG(index_mode):
                index_state, envelopes = "invalid", 1
            else:
                raw = index.read_bytes()
                index_state = "empty" if not raw else "nonempty"
                rows = [json.loads(line) for line in raw.splitlines()]
                if any(not isinstance(row, dict) for row in rows):
                    raise ValueError("non-object envelope row")
                # A start-drift abort writes a row before that slot's capture.
                envelopes = sum("collector_exit" in row for row in rows)
        return ZeroCaptureFacts(**base, chain_started=int(_mode(night / "chain.started") is not None),
            reservation_markers_found=reservations, capture_entries_found=captures,
            envelope_index_state=index_state, envelopes_captured=envelopes,
            scan_complete=True)
    except (OSError, UnicodeError, ValueError, TypeError):
        return ZeroCaptureFacts(**base)


__all__ = ["zero_capture_facts"]
