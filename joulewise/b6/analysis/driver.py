"""Block-6 analysis driver (registration §13; design §4.3, §5, §10, §11, §14).

Order: census from the loop's acceptance, checked session by session against
each acceptance record (§4, item 53, audit L5) → §11.4 (i) → pairing (§6.2)
→ block 5's steps per session through the L9 adapter, as a DAG (§9), with
each session's desk-compressed bytes restored once per run (design §4.1, as
corrected) → analysis counting checked against acceptance counting → §11.4
(ii) → §10, §11.1, §11.2 and §11.4 → restricted objects and a structure-only
record (§12).

Phases (design §14; audit B6-4):

* ``per-session``: floor and GAMMA units, any time.  A GAMMA unit whose
  pairing needs block 5's floor is deferred to the cross-block phase.  Run it
  twice (``run=1``, then ``run=2`` on the same host): the second run's record
  must equal the first's, digest for digest, or it refuses.
* ``cross-block``: after block 5's release and the close (§12.3 items 1, 2):
  block 5's sessions, the deferred GAMMA units and the block-6 lines, over the
  first per-session run's results (authenticated by digest).  Also twice.
* ``session``: one newly harvested session and its paired floor sessions,
  blind, the day it lands (§12.2).  No between-session line.

Exit 0: complete with no tooling refusal; 3: complete, some step stopped with
a registered outcome class; 2: anything else.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import traceback
from dataclasses import asdict
from pathlib import Path

from joulewise.b6.analysis import census as census_module
from joulewise.b6.analysis import comparison, inclusive, pairing, replication, schedule, slots, summary
from joulewise.b6.analysis.acceptance_counting import (CountingRefusal, analysis_counting_problems,
                                                       require_loop_equals_acceptance)
from joulewise.b6.analysis.adapter import COMPLETED, DEFERRED, SessionAnalysis, SessionRequest
from joulewise.b6.analysis.public import (PUBLIC_RECORD, Custody, CustodyRefusal, preflight, public_token,
                                          sha256)
from joulewise.b6.analysis.restore import Lifecycle, SessionBytes
from joulewise.b6.analysis.session_index import IndexRefusal, load_session_index

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "configs/b6/analysis/driver.json"
REGISTRATION_PATH = ROOT / "docs/registrations/block6_replication_DRAFT.md"
RECORD_SCHEMA = "joulewise.b6_blind_dry_run.v1"
MODES = ("per-session", "cross-block", "session")
# What two runs of one phase must reproduce exactly (B6-4).  Timing and the
# run's own identity are left out.
COMPARED = ("analysis_commit", "config_sha256", "bindings", "census", "sessions", "pairings", "nodes",
            "line_refusals", "sessions_unaccounted", "restricted")
SIDE_BY_SIDE_FACTS = (
    "Block 6 makes record conditions flags; the rules for which runs and sessions enter differ between the "
    "blocks (REG §8).",
    "Each block's own calibration acceptance sets its b_op: s_bracket 14.531 ms in block 5, 10.818 ms in block 6.")


class DriverRefusal(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


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


def run_directory(mode: str, run: int, only: str | None) -> str:
    return f"session-{only}" if mode == "session" else f"{mode}-{run}"


def require_synthetic_roots(paths) -> None:
    """With JW_B5_SYNTHETIC_ONLY=1 every root must lie under $TMPDIR (design §17):
    the restore writes into session directories."""
    if os.environ.get("JW_B5_SYNTHETIC_ONLY") != "1":
        return
    tmp = Path(tempfile.gettempdir()).resolve()
    for path in paths:
        if not Path(path).absolute().resolve().is_relative_to(tmp):
            raise DriverRefusal("synthetic_root_outside_tmpdir")


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


def session_node(config, entry) -> str:
    kind = schedule.FLOOR if entry.pack in config["floor_packs"] else schedule.GAMMA
    return schedule.node_id(kind, entry.pack, entry.session_id)


def plan(census, config, *, only: str | None = None):
    """Every unit with its dependencies and sessions, the pairings, and §11.4 (i).

    Returns ``(units, pairings, pre)``; ``units`` includes the GAMMA units that
    need a block-5 floor, which only the cross-block phase runs."""
    rules = config["section_11_4"]
    pre = {(e.pack, e.session_id): inclusive.pre_admission(e, rules) for e in census.entries}
    chosen = [e for e in census.entries if pre[(e.pack, e.session_id)][0] in (inclusive.COUNTING, inclusive.CANDIDATE)]
    pairings = {g.session_id: pairing.pair(census, g) for g in chosen if g.pack == "gamma"}
    if only is not None:
        target = census.get(only)
        if pre[(target.pack, target.session_id)][0] not in (inclusive.COUNTING, inclusive.CANDIDATE):
            raise DriverRefusal("session_not_analysable")
        keep = {(target.pack, target.session_id)}
        if target.pack == "gamma":
            keep |= {(f.pack, f.session_id) for f in pairings[target.session_id].floors}
        chosen = [e for e in chosen if (e.pack, e.session_id) in keep]
        pairings = {k: v for k, v in pairings.items() if ("gamma", k) in keep}
    units = []
    for entry in chosen:
        request = SessionRequest(entry.session_id, entry.pack, entry.round)
        if entry.pack in config["floor_packs"]:
            units.append(schedule.Node(schedule.FLOOR, request, sessions=(entry.session_id,)))
            continue
        floors = pairings[entry.session_id].floors
        depends = tuple(schedule.node_id(schedule.BLOCK5 if f.from_block5 else schedule.FLOOR, f.pack, f.session_id)
                        for f in floors)
        sessions = (entry.session_id,) + tuple(f.session_id for f in floors if not f.from_block5)
        units.append(schedule.Node(schedule.GAMMA, request, depends, sessions=sessions))
    return tuple(units), pairings, pre


def _needs_block5(node) -> bool:
    return any(d.startswith(schedule.BLOCK5 + ":") for d in node.depends)


def _session_record(node_id: str, analysis: SessionAnalysis) -> dict:
    return {"node": node_id, **asdict(analysis), "steps": [list(step) for step in analysis.steps]}


def _from_record(row: dict) -> SessionAnalysis:
    fields = {k: v for k, v in row.items() if k != "node"}
    fields["steps"] = tuple(tuple(step) for step in fields.get("steps", ()))
    return SessionAnalysis(**fields)


def block6_lines(census, config, results: dict, pairings: dict, admissions: dict) -> dict:
    """§10, §11.1, §11.2 and §11.4 over analysed sessions.  Restricted."""
    def analysis(entry):
        return results.get(session_node(config, entry))

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
        # The quantities §10 prints, as the comparison contract names them, plus
        # S-15's whole-machine values where the binding supplies them.
        keys = sorted(set(comparison.summarised_quantities(pack)) | {
            k for a in [b5, *counting, *added] for k in a.quantities if k.startswith(slots.WHOLE_MACHINE_PREFIX)})
        lines["summary"][pack] = summary.pack_summary(b5, counting, keys)
        lines["side_by_side"][pack] = {**summary.side_by_side(b5, counting, keys), "facts": list(SIDE_BY_SIDE_FACTS),
                                       "note": None if counting else "no counting block-6 session"}
        inclusive_sessions = sorted(counting + added, key=lambda a: census_module.order_key(census.get(a.session_id, pack)))
        lines["flagged_inclusive"][pack] = {
            "label": (summary.INCLUSIVE_LABEL.format(n=1 + len(inclusive_sessions)) if added
                      else summary.INCLUSIVE_NONE),
            "added_sessions": [{"session_id": a.session_id, "codes": list(census.get(a.session_id, pack).codes)}
                               for a in added],
            "summary": summary.pack_summary(b5, inclusive_sessions, keys)}
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


def comparison_output(census, config, results: dict, lines: dict | None, *, single_session: bool):
    """The restricted table the independent recompute joins key by key, in the
    shape its comparator reads (``{sessions: {id: {quantities,
    run_phase_energy_j}}, block: {quantities}}``) and nothing else, plus its
    metadata kept apart.  Returns ``(table, meta, refusals)``."""
    refusals, sessions = [], {}
    for entry in census.entries:
        result = results.get(session_node(config, entry))
        if result is None or result.status not in COMPLETED:
            continue
        try:
            sessions[entry.session_id] = {
                "quantities": comparison.session_values(result, single_session=single_session),
                "run_phase_energy_j": comparison.run_values(result)}
        except comparison.ComparisonRefusal as exc:
            refusals.append(["comparison", entry.session_id, exc.code])
    table = {"sessions": sessions}
    if lines is not None:
        try:
            table["block"] = {"quantities": comparison.block_values(lines, config["packs"])}
        except comparison.ComparisonRefusal as exc:
            refusals.append(["comparison", "block", exc.code])
    meta = {"schema_version": comparison.VALUES_SCHEMA, "keys_schema": comparison.KEYS_SCHEMA,
            "single_session": single_session,
            "packs": {e.session_id: comparison.PACK_NAMES[e.pack] for e in census.entries if e.session_id in sessions}}
    return table, meta, refusals


def _completed_record(custody: Path, name: str) -> tuple[dict, str]:
    """An earlier run's record that completed and, if it was a repeat, matched."""
    try:
        raw = (Path(custody) / name / PUBLIC_RECORD).read_bytes()
        record = json.loads(raw)
        if record["completed_without_tooling_refusal"] is not True or (record.get("comparison") or {}).get("differs"):
            raise ValueError()
        return record, sha256(raw)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        raise DriverRefusal(name.replace("-", "_") + "_missing_or_incomplete") from None


def _difference(previous: dict, record: dict) -> str | None:
    for key in COMPARED:
        if previous.get(key) != record.get(key):
            return key
    return None


def analyse(loop_root: Path, index_path: Path, custody: Path, adapter, *, mode: str = "per-session", run: int = 1,
            only: str | None = None, workers: int = 1, block5_release_record: Path | None = None,
            config_path: Path = CONFIG_PATH, repo_root: Path = ROOT, checkout=analysis_checkout, catalog=None,
            restore: bool = True, lifecycle_class=Lifecycle) -> int:
    from joulewise.flags.catalog import load_catalog

    def say(line: str) -> None:
        print(line, file=sys.stderr)

    if (mode not in MODES or (mode == "session") != (only is not None) or run not in (1, 2)
            or (mode == "session" and run != 1)):
        say("analysis - tooling_refusal")
        return 2
    custody = Path(custody)
    previous = previous_sha = earlier = None
    try:
        require_synthetic_roots([loop_root, index_path, custody] + ([block5_release_record] if block5_release_record else []))
        directory = preflight(custody, run_directory(mode, run, only), repo_root)
        if mode == "per-session" and run == 2:
            previous, previous_sha = _completed_record(custody, "per-session-1")
        if mode == "cross-block":
            earlier, earlier_sha = _completed_record(custody, "per-session-1")
            _completed_record(custody, "per-session-2")
            if run == 2:
                previous, previous_sha = _completed_record(custody, "cross-block-1")
        commit = checkout(repo_root)
        config, config_sha = load_config(config_path)
        catalog = catalog or load_catalog(repo_root / config["flag_catalog"])
        census = census_module.load_census(loop_root)
        index = load_session_index(index_path, loop_root=loop_root)
        require_synthetic_roots([root for row in index["sessions"]
                                 for root in (row["archive_root"], row["custody_root"], *row["runs_roots"])])
        accepted = require_loop_equals_acceptance(census, index)
        units, pairings, pre = plan(census, config, only=only)
        bindings = {"registration_sha256": sha256(REGISTRATION_PATH.read_bytes()) if REGISTRATION_PATH.exists() else None,
                    "catalog_sha256": sha256((repo_root / config["flag_catalog"]).read_bytes()),
                    "session_index_sha256": sha256(Path(index_path).read_bytes()),
                    "attempts_sha256": index["attempts_sha256"], "state_sha256": index["state_sha256"],
                    "harvest_records": {r["session_id"]: r["harvest_record_sha256"] for r in index["sessions"]},
                    "acceptance_records": {r["session_id"]: r["acceptance_record_sha256"] for r in index["sessions"]}}
        if mode == "cross-block":
            if not census.closed:
                raise DriverRefusal("block6_not_closed")
            if block5_release_record is None or not Path(block5_release_record).is_file():
                raise DriverRefusal("block5_not_released")
            if earlier["analysis_commit"] != commit or earlier["config_sha256"] != config_sha:
                raise DriverRefusal("analysis_commit_differs_from_per_session_run")
            bindings["block5_release_record_sha256"] = sha256(Path(block5_release_record).read_bytes())
            bindings["per_session_record_sha256"] = earlier_sha
        directory.mkdir(parents=True)
        store = Custody(directory)
    except (CustodyRefusal, census_module.CensusRefusal, IndexRefusal, CountingRefusal, DriverRefusal) as exc:
        say(f"analysis - tooling_refusal {public_token(exc.code)}")
        return 2
    except Exception:
        say("analysis - tooling_refusal")
        return 2

    try:
        return _finish(adapter, units, store, census, index, accepted, config, config_sha, bindings, pairings, pre,
                       mode=mode, run=run, only=only, workers=workers, commit=commit, catalog=catalog,
                       previous=previous, previous_sha=previous_sha, earlier=earlier, restore=restore,
                       lifecycle_class=lifecycle_class, say=say)
    except (CustodyRefusal, DriverRefusal) as exc:
        say(f"analysis - tooling_refusal {public_token(exc.code)}")
        return 2
    except Exception:
        # Exception text may carry a value; it goes to restricted custody only.
        with (store.restricted / "driver-traceback.log").open("a", encoding="utf-8") as log:
            traceback.print_exc(file=log)
        say("analysis - tooling_refusal")
        return 2


def _earlier_results(earlier: dict, custody_root: Path) -> dict:
    """The first per-session run's results, authenticated by the digest its record names."""
    objects = custody_root / "per-session-1" / "restricted" / "objects"
    digest = earlier["restricted"]["sessions"]
    raw = (objects / f"{digest}.json").read_bytes()
    if sha256(raw) != digest:
        raise CustodyRefusal("restricted_object_digest_mismatch")
    return {row["node"]: _from_record(row) for row in json.loads(raw)}


def _finish(adapter, units, store, census, index, accepted, config, config_sha, bindings, pairings, pre, *, mode, run,
            only, workers, commit, catalog, previous, previous_sha, earlier, restore, lifecycle_class, say) -> int:
    initial, deferred = {}, {}
    if mode == "cross-block":
        initial = {k: v for k, v in _earlier_results(earlier, store.directory.parent).items() if v.status != DEFERRED}
        nodes = [schedule.Node(schedule.BLOCK5, SessionRequest(pairing.BLOCK5, pack, 0)) for pack in config["packs"]]
        nodes += [u for u in units if _needs_block5(u)]
    else:
        nodes = [u for u in units if not _needs_block5(u)]
        deferred = {u.id: SessionAnalysis(u.request.session_id, u.request.pack, DEFERRED, code="block5_not_released")
                    for u in units if _needs_block5(u)}
    nodes = tuple(nodes)

    lifecycle = None
    if restore:
        rows = {row["session_id"]: row for row in index["sessions"]}
        users: dict[str, int] = {}
        for node in nodes:
            for session_id in node.sessions:
                users[session_id] = users.get(session_id, 0) + 1
        lifecycle = lifecycle_class({s: SessionBytes.from_index_row(rows[s], Path(index["measurement"])) for s in users},
                                    users)
    try:
        results = schedule.execute(adapter, nodes, store.restricted, workers=workers, lifecycle=lifecycle,
                                   initial=initial)
    finally:
        if lifecycle is not None:
            lifecycle.close_all()
    results.update(deferred)
    ran = {n.id for n in nodes}
    order = [n.id for n in nodes if n.kind == schedule.BLOCK5]
    order += [u.id for u in sorted(units, key=lambda u: census_module.order_key(
        census.get(u.request.session_id, u.request.pack))) if u.id in results]

    node_rows = []
    for node_id in order:
        result = results[node_id]
        node_rows.append({"node": node_id, "status": result.status,
                          "code": (public_token(result.code)
                                   if result.status in ("tooling_refusal", "not_run", DEFERRED) else None),
                          "steps": [[step, status] for step, status in result.steps],
                          "kept_units": {c: dict(s) for c, s in sorted(result.kept_units.items())},
                          "b_op_defined": result.b_op_defined, "drift_screen": result.drift_screen,
                          "analysis_counting": result.analysis_counting,
                          "outputs": dict(sorted(result.outputs.items()))})
        if node_id in ran:
            say(f"node {node_id} {result.status}")

    line_refusals = [["restore", session_id, public_token(code)]
                     for session_id, code in (lifecycle.refusals() if lifecycle else [])]
    analysis_counting = {e.session_id: getattr(results.get(session_node(config, e)), "analysis_counting", None)
                         for e in census.entries}
    analysed = {e.session_id: analysis_counting[e.session_id] for e in census.entries
                if getattr(results.get(session_node(config, e)), "status", None) in COMPLETED}
    line_refusals += [["counting", *problem] for problem in analysis_counting_problems(census, accepted, analysed)]

    admissions = {}
    for entry in census.entries:
        key = (entry.pack, entry.session_id)
        result = results.get(session_node(config, entry))
        if only is not None:
            admissions[key] = pre[key]
        elif result is not None and result.status == DEFERRED:
            admissions[key] = ("deferred", [])
        else:
            admissions[key] = inclusive.admission(entry, result, config["section_11_4"])

    store.put("sessions", [_session_record(node_id, results[node_id]) for node_id in order])
    store.put("pairings", [pairings[g].as_record() for g in sorted(pairings, key=lambda g: census.get(g, "gamma").round)])
    lines = None
    if mode == "cross-block":
        lines = block6_lines(census, config, results, pairings, admissions)
        for role, value in lines.items():
            store.put(role, value)
            line_refusals += [[role, key, public_token(item["refused"])] for key, item in sorted(value.items())
                              if isinstance(item, dict) and "refused" in item]
    compared, meta, refusals = comparison_output(census, config, results, lines, single_session=only is not None)
    store.put("comparison", compared)
    store.put("comparison_meta", meta)
    line_refusals += refusals

    # §12.3 item 3 (lead ruling of 2026-10-27): every collected session is
    # analysed without a tooling refusal, or recorded with its registered
    # structural reason (§11.4 (i)); in the per-session phase a GAMMA unit
    # waiting for block 5's floor is accounted as deferred.
    accounted = COMPLETED + ((DEFERRED,) if mode != "cross-block" else ())
    unaccounted = [] if only is not None else [
        e.session_id for e in census.entries
        if admissions[(e.pack, e.session_id)][0] != inclusive.NOT_REGISTERED
        and getattr(results.get(session_node(config, e)), "status", None) not in accounted]
    sessions = [{"session_id": e.session_id, "pack": e.pack, "round": e.round, "t0": e.t0,
                 "loop_status": e.status, "loop_counting": e.counting,
                 "acceptance_counting": accepted.get(e.session_id),
                 "analysis_counting": analysis_counting[e.session_id],
                 "analysed": session_node(config, e) in results,
                 "admission": admissions[(e.pack, e.session_id)][0],
                 "reasons": admissions[(e.pack, e.session_id)][1], "flags": _codes_public(e.codes, catalog)}
                for e in census.entries]
    completed = all(row["status"] in accounted for row in node_rows) and not line_refusals and not unaccounted
    cycles = {} if lifecycle is None else {
        session_id: {"files_restored": cycle.get("files", 0), "logical_bytes": cycle.get("logical_bytes", 0),
                     "disk_bytes": cycle.get("disk_bytes", 0), "apfs_compressed": cycle.get("apfs_compressed"),
                     "restore_seconds": int(round(cycle.get("restore_seconds", 0))),
                     "refusal": public_token(cycle.get("refusal")), "after_check": cycle.get("after_check")}
        for session_id, cycle in sorted(lifecycle.cycles.items())}
    record = {"schema_version": RECORD_SCHEMA, "mode": mode, "run": run, "only": only, "analysis_commit": commit,
              "config_sha256": config_sha, "adapter": adapter.describe(), "bindings": bindings,
              "census": census_module.structure_record(census), "sessions": sessions,
              "pairings": store.get(store.roles["pairings"]), "nodes": node_rows, "line_refusals": line_refusals,
              "sessions_unaccounted": unaccounted, "restore_cycles": cycles,
              "cross_block": "ok" if mode == "cross-block" else "not_run",
              "restricted": dict(sorted(store.roles.items())),
              "comparison": None, "completed_without_tooling_refusal": completed}
    if previous is not None:
        differs = _difference(previous, record)
        record["comparison"] = {"against_sha256": previous_sha, "differs": differs}
        if differs is not None:
            record["completed_without_tooling_refusal"] = completed = False
    path, digest = store.write_public(record)
    print(f"{path} {digest}")
    if not completed:
        return 2
    return 3 if any(row["status"] == "outcome_class" for row in node_rows) else 0
