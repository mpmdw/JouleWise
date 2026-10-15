"""The archive desk steps shared by the wrapper and non-claim replay."""

from __future__ import annotations

from dataclasses import replace
from collections import Counter
import os
from pathlib import Path
import tempfile

from joulewise.b6.acceptance import ACCEPTANCE, evidence_from_archive, write_result
from joulewise.b6.archive import bindings, bundle_roots, executed_porcelain, ordered_roster, plan_tree, read_json
from joulewise.b6 import survivor_screen
from joulewise.b6 import registration
from joulewise.b6.acceptance_interface import AcceptanceResult
from joulewise.flags.catalog import load_catalog
from joulewise.flags.exclusions import compute
from joulewise.flags.schema import make_flag, make_scope, make_source

ROOT = Path(__file__).resolve().parents[2]


def accept_archive(archive: Path, plan: dict, registration_dir: Path, *, ledger_path: Path | None = None,
                   ledger_rows=None, screen_output_root: Path | None = None,
                   plan_path: Path | None = None, smoke: bool = False, replace_existing: bool = False):
    bound = bindings(plan)
    output = screen_output_root or archive
    try:
        registration.load(registration_dir)
    except (OSError, ValueError):
        evidence = evidence_from_archive(archive, plan, registration_dir)
        catalog = load_catalog(ROOT / registration.DEFAULTS["catalog"])
        code = "precheck.acceptance_unavailable"
        entry = catalog.entry(code)
        flag = make_flag(code=code, family=entry["family"], klass=entry["klass"],
                         scope=make_scope("window"), source=make_source("harvest", "b6.session"),
                         catalog_sha256=catalog.sha256,
                         emitted={"wall_s": 0, "monotonic_ns": 0, "boot_session_uuid": None})
        record = {"schema": "joulewise.b6_acceptance.v1", "verdict": "UNAVAILABLE", "counting": False,
                  "structural": False, "session_id": bound.get("bracket_session_id", plan.get("plan_id")),
                  "pack_id": evidence.pack_id, "mode": "smoke" if smoke else "archive",
                  "flag_counts": {code: 1}, "emitted_flags": [flag],
                  "flags": [code], "excluding": [], "pending": ["acceptance_registration"]}
        result = AcceptanceResult("UNAVAILABLE", (code,), (code,), False, False, record)
        _write_result(output, result, replace_existing=replace_existing)
        return result, evidence
    evidence = evidence_from_archive(archive, plan, registration_dir)
    tree, pack_root = plan_tree(archive, plan, evidence.pack_id)
    code = read_json(archive / "derived/code-identity.json", {})
    code["repo_root"] = ROOT
    code["status_porcelain"] = executed_porcelain(archive, plan, plan_path)
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
    if not (archive / "withheld/b6-neg8.json").is_file():
        screen = survivor_screen.screen(roster, excluded, survivor_screen.archive_energy_of(
            archive, bundle_roots(archive, plan)), prepared.registration)
        survivor_screen.write(output, screen)
        internal = {**internal, "neg8": screen.acceptance_evidence()}
    evidence = replace(evidence, runtime={**evidence.runtime, "_b6": {**internal, "smoke": smoke or internal.get("smoke", False)}})
    result = ACCEPTANCE.evaluate(prepared, evidence)
    _write_result(output, result, replace_existing=replace_existing)
    return result, evidence


def _write_result(output, result, *, replace_existing):
    """Replace only derived judgments; preserve the harvested source evidence."""
    output = Path(output)
    if not replace_existing:
        write_result(output, result)
        return
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="b6-judgment-", dir=output) as temp:
        write_result(Path(temp), result)
        (output / "derived").mkdir(exist_ok=True)
        for name in ("b6-acceptance.json", "b6-flags.jsonl"):
            os.replace(Path(temp) / "derived" / name, output / "derived" / name)
