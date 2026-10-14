"""The archive desk steps shared by the wrapper and non-claim replay."""

from __future__ import annotations

from dataclasses import replace
from collections import Counter
from pathlib import Path

from joulewise.b6.acceptance import ACCEPTANCE, evidence_from_archive, write_result
from joulewise.b6.archive import bindings, bundle_roots, ordered_roster, plan_tree, read_json
from joulewise.b6 import survivor_screen
from joulewise.flags.exclusions import compute

ROOT = Path(__file__).resolve().parents[2]


def accept_archive(archive: Path, plan: dict, registration_dir: Path, *, ledger_path: Path | None = None,
                   ledger_rows=None, screen_output_root: Path | None = None):
    bound = bindings(plan)
    evidence = evidence_from_archive(archive, plan, registration_dir)
    tree, pack_root = plan_tree(archive, plan, evidence.pack_id)
    code = read_json(archive / "derived/code-identity.json", {})
    code["repo_root"] = ROOT
    prepared = ACCEPTANCE.prepare(
        ledger_path=ledger_path or Path(bound.get("ledger_path") or archive / "capture-list.jsonl"),
        ledger_rows=ledger_rows, plan_tree=tree, registration_dir=registration_dir,
        code_identity=code, pack_root=pack_root)
    roster = ordered_roster(read_json(archive / "derived/roster.json", {}), evidence)
    internal = evidence.runtime["_b6"]
    effects = compute(internal["flags"], roster, internal["spans"], prepared.catalog, pack_scoped=False)
    excluded = {row["run_id"]: row["codes"] for row in effects["members_excluded"]}
    for run_id, count in Counter(m["run_id"] for m in roster["members"]).items():
        if count > 1:
            excluded.setdefault(run_id, []).append("member.bytes_ambiguous")
    screen = survivor_screen.screen(roster, excluded, survivor_screen.archive_energy_of(
        archive, bundle_roots(archive, plan)), prepared.registration)
    output = screen_output_root or archive
    survivor_screen.write(output, screen)
    evidence = replace(evidence, runtime={**evidence.runtime, "_b6": {**internal, "neg8": screen.acceptance_evidence()}})
    result = ACCEPTANCE.evaluate(prepared, evidence)
    write_result(output, result)
    return result, evidence
