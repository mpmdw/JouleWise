"""Block-6 analysis driver (registration §13).

Order: census from the loop's acceptance (§4, item 53) → §11.4 pre-admission
→ pairing (§6.2) → per-session block-5 steps through the L9 adapter, as a DAG
(§9) → §11.4 admission → §10, §11.1, §11.2 and §11.4 lines → restricted
objects and a structure-only public record (§12).

Modes:

* ``blind-dry-run``: every session, then the block-6 lines.
* ``session``: one newly harvested session (and the floor sessions it pairs
  with) the day it lands, blind (§12.2).  No between-session line.
* ``release``: the same run as the blind dry run from identical bytes; every
  restricted output digest must equal the dry run's (§13).

Exit 0: complete with no tooling refusal; 3: complete, some step stopped with
a registered outcome class; 2: anything else.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import traceback
from dataclasses import asdict
from pathlib import Path

from joulewise.b6.analysis import census as census_module
from joulewise.b6.analysis import inclusive, pairing, replication, schedule, slots, summary
from joulewise.b6.analysis.adapter import COMPLETED, SessionAnalysis, SessionRequest
from joulewise.b6.analysis.public import Custody, CustodyRefusal, preflight, public_token, sha256

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "configs/b6/analysis/driver.json"
RECORD_SCHEMA = "joulewise.b6_analysis_record.v1"
MODES = ("blind-dry-run", "session", "release")


def load_config(path: Path = CONFIG_PATH) -> tuple[dict, str]:
    raw = Path(path).read_bytes()
    return json.loads(raw), sha256(raw)


def analysis_checkout(repo_root: Path = ROOT) -> str:
    """HEAD of a checkout with no tracked change, as L9 binds its own run."""
    try:
        head = subprocess.run(["git", "-C", str(repo_root), "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()
        changes = subprocess.run(["git", "-C", str(repo_root), "status", "--porcelain", "--untracked-files=no"],
                                 check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.SubprocessError):
        raise CustodyRefusal("analysis_checkout_not_clean") from None
    if re.fullmatch(r"[0-9a-f]{40}", head) is None or changes:
        raise CustodyRefusal("analysis_checkout_not_clean")
    return head


def _codes_public(codes, catalog) -> dict:
    """Flag codes as §12.1 releases them: a restricted code only as a count."""
    shown, hidden = [], 0
    for code in codes:
        try:
            blinding = catalog.entry(code).get("blinding", "STRUCTURE")
        except (KeyError, ValueError):
            blinding = "RESTRICTED"
        if blinding == "STRUCTURE" and public_token(code) == code:
            shown.append(code)
        else:
            hidden += 1
    return {"codes": sorted(shown), "restricted_codes_removed": hidden}


def plan(census, config, *, only: str | None = None):
    """The nodes to run, the pairings, and the §11.4 pre-admission of every session."""
    rules = config["section_11_4"]
    pre = {(e.pack, e.session_id): inclusive.pre_admission(e, rules) for e in census.entries}
    chosen = [e for e in census.entries if pre[(e.pack, e.session_id)][0] in (inclusive.COUNTING, inclusive.CANDIDATE)]
    pairings = {g.session_id: pairing.pair(census, g) for g in chosen if g.pack == "gamma"}
    if only is not None:
        target = census.get(only)
        if pre[(target.pack, target.session_id)][0] not in (inclusive.COUNTING, inclusive.CANDIDATE):
            raise CustodyRefusal("session_not_analysable")
        keep = {(target.pack, target.session_id)}
        if target.pack == "gamma":
            keep |= {(f.pack, f.session_id) for f in pairings[target.session_id].floors}
        chosen = [e for e in chosen if (e.pack, e.session_id) in keep]
        pairings = {k: v for k, v in pairings.items() if ("gamma", k) in keep}

    nodes = []
    needed_block5 = set(config["packs"]) if only is None else {
        f.pack for p in pairings.values() for f in p.floors if f.from_block5}
    for pack in config["packs"]:
        if pack in needed_block5:
            nodes.append(schedule.Node(schedule.BLOCK5, SessionRequest(pairing.BLOCK5, pack, 0)))
    for entry in chosen:
        request = SessionRequest(entry.session_id, entry.pack, entry.round)
        if entry.pack in config["floor_packs"]:
            nodes.append(schedule.Node(schedule.FLOOR, request))
        else:
            floors = pairings[entry.session_id].floors
            depends = tuple(schedule.node_id(schedule.BLOCK5 if f.from_block5 else schedule.FLOOR, f.pack, f.session_id)
                            for f in floors)
            nodes.append(schedule.Node(schedule.GAMMA, request, depends))
    return tuple(nodes), pairings, pre


def _session_record(analysis: SessionAnalysis) -> dict:
    return asdict(analysis) | {"steps": [list(step) for step in analysis.steps]}


def block6_lines(census, config, results: dict, pairings: dict, admissions: dict) -> dict:
    """§10, §11.1, §11.2 and §11.4 over analysed sessions.  Restricted."""
    def analysis(entry):
        kind = schedule.FLOOR if entry.pack in config["floor_packs"] else schedule.GAMMA
        return results.get(schedule.node_id(kind, entry.pack, entry.session_id))

    lines = {"summary": {}, "side_by_side": {}, "flagged_inclusive": {}, "replication": {}, "whole_machine": {}}
    blocks5 = {pack: results.get(schedule.node_id(schedule.BLOCK5, pack, pairing.BLOCK5)) for pack in config["packs"]}
    for pack in config["packs"]:
        b5 = blocks5[pack]
        counting = [analysis(e) for e in census.counting(pack)]
        added = [analysis(e) for e in census.pack(pack) if admissions[(e.pack, e.session_id)][0] == inclusive.ADDED]
        if b5 is None or b5.status not in COMPLETED or any(a is None or a.status not in COMPLETED for a in counting):
            lines["summary"][pack] = lines["side_by_side"][pack] = {"refused": "input_session_not_analysed"}
            lines["flagged_inclusive"][pack] = {"refused": "input_session_not_analysed"}
            continue
        lines["summary"][pack] = summary.pack_summary(b5, counting)
        lines["side_by_side"][pack] = summary.side_by_side(b5, counting)
        inclusive_sessions = sorted(counting + added, key=lambda a: census_module.order_key(census.get(a.session_id, pack)))
        lines["flagged_inclusive"][pack] = {
            "label": summary.INCLUSIVE_LABEL.format(n=1 + len(inclusive_sessions)),
            "added_sessions": [a.session_id for a in added],
            "summary": summary.pack_summary(b5, inclusive_sessions)}
    lines["whole_machine"] = {}
    for node_key, result in sorted(results.items()):
        if result.status not in COMPLETED:
            continue
        try:
            lines["whole_machine"][node_key] = slots.s15_quantities(result.pack, result.quantities)
        except slots.SlotRefusal as exc:
            lines["whole_machine"][node_key] = {"refused": exc.code}
    gamma_b5 = blocks5.get(config["contrast_pack"])
    counting_gamma = [analysis(e) for e in census.counting(config["contrast_pack"])]
    added_gamma = [analysis(e) for e in census.pack(config["contrast_pack"])
                   if admissions[(e.pack, e.session_id)][0] == inclusive.ADDED]
    for contrast in config["contrasts"]:
        if (gamma_b5 is None or gamma_b5.status not in COMPLETED
                or any(a is None or a.status not in COMPLETED for a in counting_gamma)):
            lines["replication"][contrast] = {"refused": "input_session_not_analysed"}
            continue
        lines["replication"][contrast] = replication.contrast_word(
            contrast, gamma_b5, counting_gamma, target=config["target_counting_sessions"],
            floor_from_block5={g: p.floor_from_block5 for g, p in pairings.items()}, inclusive=added_gamma)
    return lines


def analyse(loop_root: Path, custody: Path, adapter, *, mode: str = "blind-dry-run", workers: int = 1,
            only: str | None = None, config_path: Path = CONFIG_PATH, repo_root: Path = ROOT,
            checkout=analysis_checkout, catalog=None) -> int:
    from joulewise.flags.catalog import load_catalog

    def say(line: str) -> None:
        print(line, file=sys.stderr)

    if mode not in MODES or (mode == "session") != (only is not None):
        say("analysis - tooling_refusal")
        return 2
    try:
        directory = preflight(custody, mode, repo_root)
        previous = _previous_record(Path(custody)) if mode == "release" else None
        commit = checkout(repo_root)
        config, config_sha = load_config(config_path)
        catalog = catalog or load_catalog(repo_root / config["flag_catalog"])
        census = census_module.load_census(loop_root)
        nodes, pairings, pre = plan(census, config, only=only)
        directory.mkdir(parents=True)
        store = Custody(directory)
    except (CustodyRefusal, census_module.CensusRefusal) as exc:
        say(f"analysis - tooling_refusal {public_token(exc.code)}")
        return 2
    except Exception:
        say("analysis - tooling_refusal")
        return 2

    try:
        return _finish(adapter, nodes, store, census, config, config_sha, pairings, pre, mode=mode, only=only,
                       workers=workers, commit=commit, catalog=catalog, previous=previous, say=say)
    except CustodyRefusal as exc:
        say(f"analysis - tooling_refusal {public_token(exc.code)}")
        return 2
    except Exception:
        # Exception text may carry a value; it goes to restricted custody only.
        with (store.restricted / "driver-traceback.log").open("a", encoding="utf-8") as log:
            traceback.print_exc(file=log)
        say("analysis - tooling_refusal")
        return 2


def _finish(adapter, nodes, store, census, config, config_sha, pairings, pre, *, mode, only, workers, commit,
            catalog, previous, say) -> int:
    results = schedule.execute(adapter, nodes, store.restricted, workers=workers)
    node_rows = []
    for node in nodes:
        result = results[node.id]
        node_rows.append({"node": node.id, "status": result.status,
                          "code": public_token(result.code) if result.status in ("tooling_refusal", "not_run") else None,
                          "steps": [[step, status] for step, status in result.steps],
                          "kept_units": {c: dict(s) for c, s in sorted(result.kept_units.items())},
                          "b_op_defined": result.b_op_defined, "drift_screen": result.drift_screen,
                          "outputs": dict(sorted(result.outputs.items()))})
        say(f"node {node.id} {result.status}")

    admissions = {}
    for entry in census.entries:
        if only is not None:
            admissions[(entry.pack, entry.session_id)] = pre[(entry.pack, entry.session_id)]
            continue
        kind = schedule.FLOOR if entry.pack in config["floor_packs"] else schedule.GAMMA
        admissions[(entry.pack, entry.session_id)] = inclusive.admission(
            entry, results.get(schedule.node_id(kind, entry.pack, entry.session_id)), config["section_11_4"])

    store.put("sessions", [_session_record(results[n.id]) for n in nodes])
    store.put("pairings", [pairings[g].as_record() for g in sorted(pairings, key=lambda g: census.get(g, "gamma").round)])
    line_refusals = []
    if only is None:
        for role, value in block6_lines(census, config, results, pairings, admissions).items():
            store.put(role, value)
            line_refusals += [[role, key, public_token(item["refused"])] for key, item in sorted(value.items())
                              if isinstance(item, dict) and "refused" in item]

    index = [{"session_id": e.session_id, "pack": e.pack, "round": e.round, "status": e.status,
              "counting": e.counting, "admission": admissions[(e.pack, e.session_id)][0],
              "reasons": admissions[(e.pack, e.session_id)][1], "flags": _codes_public(e.codes, catalog)}
             for e in census.entries]
    completed = all(row["status"] in COMPLETED for row in node_rows) and not line_refusals
    record = {"schema_version": RECORD_SCHEMA, "mode": mode, "only": only, "analysis_commit": commit,
              "config_sha256": config_sha, "adapter": adapter.describe(),
              "census": census_module.structure_record(census), "pairings": store.get(store.roles["pairings"]),
              "session_index": index, "nodes": node_rows, "line_refusals": line_refusals,
              "restricted": dict(sorted(store.roles.items())),
              "completed_without_tooling_refusal": completed}
    if previous is not None:
        difference = _release_difference(previous, record)
        if difference is not None:
            record["release_difference"] = difference
            record["completed_without_tooling_refusal"] = completed = False
    path, digest = store.write_public(record)
    print(f"{path} {digest}")
    if not completed:
        return 2
    return 3 if any(row["status"] == "outcome_class" for row in node_rows) else 0


def _previous_record(custody: Path) -> dict:
    try:
        record = json.loads((custody / "dry-run" / "B6-ANALYSIS-RECORD.json").read_bytes())
        if record["completed_without_tooling_refusal"] is not True or record["mode"] != "blind-dry-run":
            raise ValueError()
        return record
    except (OSError, ValueError, KeyError, TypeError):
        raise CustodyRefusal("dry_run_record_missing_or_incomplete") from None


def _release_difference(previous: dict, record: dict) -> dict | None:
    """The first binding or output digest the release run does not reproduce."""
    for key in ("analysis_commit", "config_sha256", "census", "pairings", "session_index", "nodes",
                "line_refusals", "restricted"):
        if previous.get(key) != record.get(key):
            return {"differs": key}
    return None
