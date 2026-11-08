#!/usr/bin/env python3
"""Non-claim archive replay; stdout and markdown contain structure only."""

from __future__ import annotations

import argparse
import json
import os
import sys
import subprocess
import tempfile
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6.archive import bindings, read_json
from joulewise.b6.export_runs import export
from joulewise.b6.session import accept_archive
from joulewise.b6.registration import SCHEMA

FORBIDDEN_ROOTS = ("/Users/edr/night-custody", "/Users/edr/night-b5", "/Users/edr/night-g2a")
FORBIDDEN_ARCHIVE_PREFIX = "/Users/edr/night-archive/harvest-v5-b5-"


def forbidden(path: str) -> bool:
    return any(path == root or path.startswith(root + "/") for root in FORBIDDEN_ROOTS) or path.startswith(FORBIDDEN_ARCHIVE_PREFIX)


class ReadPolicy:
    """Audit actual opens too: owning readers may follow paths in metadata.

    The hook is inactive outside the replay, including temporary cleanup.
    A denied read is noted even if a tolerant owning reader catches OSError.
    """
    def __init__(self):
        self.active = False
        self.notes = []

    def check(self, path):
        if isinstance(path, int):
            return
        lexical = os.path.abspath(os.fsdecode(path) if path is not None else ".")
        if forbidden(lexical) or forbidden(os.path.realpath(lexical)):
            self.notes.append("source_skipped: protected path")
            raise PermissionError("replay source is protected")

    def audit(self, event, args):
        if self.active and event in ("open", "os.listdir", "os.scandir"):
            self.check(args[0])
        elif self.active and event == "subprocess.Popen":
            executable, argv, cwd, _env = args
            self.check(executable)
            if cwd is not None:
                self.check(cwd)
            # Git is used only for the local code check, never an archive program.
            for value in argv:
                if isinstance(value, str) and value.startswith("/"):
                    self.check(value)

    @contextmanager
    def enabled(self):
        self.active = True
        try:
            yield
        finally:
            self.active = False


def _registration(source: Path, destination: Path, plan: dict) -> dict:
    roster = read_json(source / "derived/roster.json", {})
    bound = bindings(plan)
    pack_id = roster.get("pack_id") or bound.get("pack_id") or "replay-pack"
    code = read_json(source / "derived/code-identity.json", {})
    registered = code.get("executed_head") or subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    registration = {"schema": SCHEMA, "pack_id": pack_id,
        "registered_commit": registered,
        "calibration": {"alignment_reference_s": "0.036462861644980",
                        "bracket_screen_s": "0.014531", "max_budgetable_drift_s": "0.015502",
                        "operative_bound_stop_s": None, "acceptance_corpus": []}}
    # Optional SPEC 1.1.1 keys are deliberately omitted to exercise defaults.
    destination.mkdir(parents=True)
    (destination / "acceptance.json").write_text(json.dumps(registration) + "\n")
    pins_path = source / "sources/inputs/identity_pins.json"
    pins = read_json(pins_path)
    (destination / "identity_pins.json").write_text(json.dumps(pins or {}) + "\n")
    return {"defaults": "SPEC 1.1.1", "identity_pins": "archive" if pins is not None else "empty",
            "calibration": "SPEC worked times; stop null; acceptance corpus empty", "capture_list": "empty"}


def replay(source: Path, scratch: Path, policy: ReadPolicy) -> dict:
    row = {"source": str(source), "notes": []}
    policy.notes.clear()
    with policy.enabled():
        try:
            policy.check(source)
            plan = None
            for path in (source / "sources/plan", source / "sources/night-custody/night_plan.json",
                         source / "night_plan.json"):
                plan = read_json(path)
                if plan is not None:
                    break
            if plan is None:
                raise ValueError("archive plan absent")
            reg_dir = scratch / "registration"
            row["registration"] = _registration(source, reg_dir, plan)
            result, evidence = accept_archive(source, plan, reg_dir, ledger_rows=[],
                                              screen_output_root=scratch / "desk")
            exported = export(source, plan, reg_dir, scratch / "keys", scratch / "export", non_claim=True,
                              evidence=evidence, acceptance_record=result.record)
            row.update(verdict=result.verdict, counting=result.counting, structural=result.structural,
                       flag_counts=result.record["flag_counts"], export_rows=exported.row_count,
                       exclusion_counts=dict(sorted(Counter(item["code"] for item in result.record["excluding"]).items())))
        except Exception as exc:
            row["notes"].append("source_skipped: " + type(exc).__name__)
    if policy.notes:
        row = {"source": str(source), "notes": sorted(set(policy.notes)), "skipped": True}
    return row


def markdown(rows: list[dict]) -> str:
    return "# Block-six non-claim replay\n\n" + "\n\n".join(
        "```json\n" + json.dumps(row, sort_keys=True, indent=2) + "\n```" for row in rows) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", type=Path, nargs="+")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--non-claim", action="store_true", default=True)
    args = parser.parse_args(argv)
    policy = ReadPolicy()
    sys.addaudithook(policy.audit)
    with tempfile.TemporaryDirectory(prefix="b6-replay-") as tmp:
        rows = [replay(source, Path(tmp) / str(i), policy) for i, source in enumerate(args.archives)]
        rendered = markdown(rows)
        if args.out:
            policy.check(args.out)
            args.out.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
