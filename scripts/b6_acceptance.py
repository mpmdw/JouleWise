#!/usr/bin/env python3
"""Write one structure-only block-six acceptance and its emitted flags."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6.acceptance import ACCEPTANCE, _bindings, evidence_from_archive
from joulewise.flags.schema import render_line, validate_flag


def write_result(archive: Path, result) -> None:
    derived = archive / "derived"
    derived.mkdir(parents=True, exist_ok=True)
    rows = result.record["emitted_flags"]
    for row in rows:
        if validate_flag(row):
            raise ValueError("acceptance emitted an invalid flag")
    # Reserve both create-once names before writing either payload.
    with (derived / "b6-acceptance.json").open("x", encoding="utf-8") as record_stream:
        with (derived / "b6-flags.jsonl").open("xb") as flags_stream:
            json.dump(result.record, record_stream, sort_keys=True, indent=2, allow_nan=False)
            record_stream.write("\n")
            for row in rows:
                flags_stream.write(render_line(row))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--registration-dir", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        bindings = _bindings(plan)
        pack_root = Path(bindings["pack_root"]) if bindings.get("pack_root") else None
        tree = json.loads((pack_root / "plan_tree.json").read_text()) if pack_root else plan.get("plan_tree", {})
        code = json.loads((args.archive / "derived/code-identity.json").read_text())
        code["repo_root"] = bindings.get("measurement_root", ROOT)
        prepared = ACCEPTANCE.prepare(ledger_path=args.ledger or Path(bindings.get("ledger_path", args.archive / "capture-list.jsonl")),
                                      plan_tree=tree, registration_dir=args.registration_dir,
                                      code_identity=code, pack_root=pack_root)
        evidence = evidence_from_archive(args.archive, plan, args.registration_dir)
        if args.smoke:
            evidence = dataclasses.replace(evidence, runtime={**evidence.runtime,
                "_b6": {**evidence.runtime.get("_b6", {}), "smoke": True}})
        result = ACCEPTANCE.evaluate(prepared, evidence)
        write_result(args.archive, result)
        print(json.dumps({"verdict": result.verdict, "counting": result.counting,
                          "structural": result.structural, "flag_counts": result.record["flag_counts"]}, sort_keys=True))
        return 0
    except Exception as exc:
        print("block-six acceptance program fault: " + type(exc).__name__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
