#!/usr/bin/env python3
"""Advance and commit the calibration ledger pin after a block-5 window's chain exits (desk only).

Usage::

    python scripts/advance_b5_ledger_pin.py --plan <window>/night_plan.json --operator-identity <id>

The desk order is chain exit, this pin advance, then the harvest (registration
section 11). A window's post-calibration finalizes its bracket session, so the
ledger's physical head moves past the committed pin. The harvest's desk
whole-window verdict reads the ledger through the committed pin, and so does
the next window's bracket reservation; both refuse until the pin is advanced and
committed (``joulewise.b5.plan.write_window_plan`` refuses the next plan at the
desk for the same reason). A window that stopped before its post-calibration
leaves its session open: abort it first (``recover_calibration_ledger.py
abort-session``); the abort is then the session's terminal head.

This program, for the plan's measurement checkout and bracket session:

1. reads the session's terminal head from the ledger. With
   ``--harvest-archive`` (a re-advance after a harvest) it must also equal that
   harvest's ``derived/terminal-pin.json``; a harvest of a session that never
   finalized writes none, and then the ledger's terminal head is used alone
   and the record says so (``terminal_pin_source``);
2. advances the pin through ``recover_calibration_ledger``'s guarded
   ``advance-head-pin`` path;
3. makes a pin-only commit of ``configs/calibration/calibration_ledger_head.json``
   (registration section 11 item 1(i)) and checks it changes that path alone.

It never arms, launches or touches custody. Exit 0 with the JSON record
(``status`` ADVANCED or NOT_NEEDED); exit 2 with ``{"status": "REFUSED", ...}``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.b5 import plan as b5_plan  # noqa: E402

DEFAULT_REASON = "block-5 window terminal head; pin-only commit (registration section 11 item 1(i))"
TERMINAL_PIN_RELATIVE = Path("derived") / "terminal-pin.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", type=Path, required=True, help="the window's night_plan.json")
    parser.add_argument("--harvest-archive", type=Path,
                        help="optional: a harvest archive root whose derived/terminal-pin.json, when it has one, "
                             "must match the ledger's terminal head")
    parser.add_argument("--operator-identity", required=True)
    parser.add_argument("--attestation-reason", default=DEFAULT_REASON)
    parser.add_argument("--no-commit", action="store_true", help="advance the pin without the pin-only commit")
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        window = plan.get("hazard_window") if isinstance(plan, dict) else None
        if not isinstance(window, dict):
            raise ValueError("the plan has no hazard_window")
        session_id = window.get("bracket_session_id")
        measurement = plan.get("measurement_root")
        if not isinstance(session_id, str) or not isinstance(measurement, str):
            raise ValueError("the plan names no bracket session or measurement root")
        expected = None
        source = "ledger"
        if args.harvest_archive is not None:
            if not args.harvest_archive.is_dir():
                raise ValueError(f"the harvest archive is not a directory: {args.harvest_archive}")
            terminal = args.harvest_archive / TERMINAL_PIN_RELATIVE
            if terminal.is_file():
                expected = json.loads(terminal.read_text(encoding="utf-8"))
                source = "ledger_matched_harvest_archive"
            else:
                # The harvest writes no terminal pin for a session that never
                # finalized (a chain stopped before its post-calibration, whose
                # session the desk aborted): the ledger's terminal head stands alone.
                source = "ledger_harvest_archive_has_no_terminal_pin"
        record = b5_plan.advance_ledger_pin(
            Path(measurement), session_id=session_id, operator_identity=args.operator_identity,
            attestation_reason=args.attestation_reason, expected_pin=expected, commit=not args.no_commit)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": type(exc).__name__, "detail": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({**record, "terminal_pin_source": source}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
