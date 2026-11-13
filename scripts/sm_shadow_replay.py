#!/usr/bin/env python3
"""Shadow replay of the state-machine modules over closed, delivered nights (RL-108).

Runs on the Air over the published night-results records. Reads only a fixed
allowlist of structure files (markers, result/refusal/chain records, courier
records). Emits a DERIVED, structure-only JSON: states, outcomes, owed effects,
exit classes, invariant names, and a per-night agreement summary. No measured
value (temperature, energy, power, timing, token count) is printed. The output
is derived off the Mac and is not custody. Disagreements are listed, not
resolved; a writer defect is reported to the research lead, not fixed here.

Sources:
  --git-ref-glob 'origin/night-results/*'   read refs with git show / ls-tree
  --tree DIR                                 DIR/<night>/ filesystem layout (tests)
Nothing is written into any source tree.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from joulewise import exit_contract, host_effects, window_state  # noqa: E402

NIGHT_SUBDIR = "docs/process_traces/night-results"
JSON_FILES = frozenset(window_state.JSON_MARKERS) | {"chain.exit-census.json",
                                                      "network_time_off.action.json"}
EXISTENCE_FILES = frozenset(window_state.EXISTENCE_MARKERS)
ALLOWLIST = JSON_FILES | EXISTENCE_FILES
POST_EXIT_STATES = {"ChainExited", "ResultWritten", "Delivered", "DeadmanTail",
                    "Stranded", "Uninstalled"}
POST_RESULT_STATES = {"ResultWritten", "Delivered", "DeadmanTail", "Stranded", "Uninstalled"}
DELIVERED_STATES = {"Delivered", "Stranded", "Uninstalled"}
# GO is admission only (exit_contract note), so it constrains nothing about the chain class.
VERDICT_CLASS = {"REFUSED": {"refused"}, "ABORTED": {"stopped"},
                 "CHAIN_STOPPED": {"stopped", "failed", "refused"}}
# M4 family gate: closed ALIGN nights only by default. Any other family needs an explicit --family.
DEFAULT_FAMILIES = ("align-r1-", "align-pilot-")


def family_allowed(night_name: str, families) -> bool:
    return night_name.startswith(tuple(families))


def chain_contract_for(night_name: str) -> str:
    """Which chain exit vocabulary a night's chain.exited code is read under.

    align-r1-* nights are driven by the R1 driver (exit_contract "r1_driver": 3 = refused).
    What ran the align-pilot-* chains is not established, so their exit codes are not classed.
    Families passed explicitly via --family keep the old b5_chain reading.
    """
    if night_name.startswith("align-r1-"):
        return "r1_driver"
    if night_name.startswith("align-pilot-"):
        return "unknown"
    return "b5_chain"


# RL-108 item 6: each violated invariant is explained as module defect, fixture gap or writer defect.
def explain_invariant(inv, rec, fault_reason_count):
    if inv == "COURIER_SENT_WITHOUT_DELIVERY":
        return ("input_gap", "courier send recorded; delivery receipt and courier_mode (night_plan.json) are not "
                "observable from the allowlist; the shadow reader needs a legacy-courier rule or a courier_mode input"
                + ("; see audit A-02 (file-only courier marks courier.sent)" if rec.get("night", "").startswith("align-r1-") else ""))
    if inv == "COURIER_SENT_WITHOUT_RESULT":
        return ("writer_candidate", "courier.sent without result.json in the delivered tree")
    if inv == "NONZERO_EXIT_WITHOUT_FAULT":
        if fault_reason_count and not rec["fault_boolean_present"]:
            return ("legacy_schema_gap", "fault reasons recorded but no boolean fault field (pre-W1 schema); "
                    "fault recorded, cause unknown; the reasons need not relate to the nonzero exit (audit A-01)")
        if fault_reason_count:
            return ("writer_candidate", "boolean fault is false while fault reasons and a nonzero exit are recorded")
        return ("writer_candidate", "nonzero chain exit with neither a fault flag nor fault reasons recorded")
    return ("unclassified", "no explanation rule")


# --- projection (M2) -------------------------------------------------------------
# Every JSON is reduced to the keys the checks read BEFORE it is kept or written anywhere.
# Free-text and identifier values are replaced by placeholders that keep only presence/count.
TMP_ROOT = Path(os.environ.get("SM_SHADOW_TMP", "/Volumes/JW-EXT/tmp"))
_RESULT_KEYS = ("verdict", "chain_exit_code", "fault", "measurement_outcome", "chain_outcome", "ended_epoch_s")


def _reasons(v):
    return ["r"] * len(v) if isinstance(v, list) else v


def _pick(doc, keys):
    return {k: doc[k] for k in keys if k in doc}


def project_doc(name, doc):
    """Return the allowlisted-key projection of a parsed JSON object (or None if not an object)."""
    if not isinstance(doc, dict):
        return None
    if name in ("result.json", "hazard_result.json"):
        out = _pick(doc, _RESULT_KEYS)
        if "fault_reasons" in doc:
            out["fault_reasons"] = _reasons(doc["fault_reasons"])
        if isinstance(doc.get("faults"), dict) and "reasons" in doc["faults"]:
            out["faults"] = {"reasons": _reasons(doc["faults"]["reasons"])}
        elif "faults" in doc:
            out["faults"] = {}
        if name == "hazard_result.json" and isinstance(doc.get("chain"), dict):
            out["chain"] = _pick(doc["chain"], ("exit_code",))
        elif name == "hazard_result.json" and "chain" in doc:
            out["chain"] = {}
        if name == "hazard_result.json":
            out.pop("ended_epoch_s", None)
        return out
    if name == "chain.exited":
        return _pick(doc, ("exit_code",))
    if name == "courier.json":
        out = _pick(doc, ("sent",))
        for k in ("message_id", "mail_message_id"):
            if isinstance(doc.get(k), str):
                out[k] = "x" if doc[k].strip() else ""
        return out
    if name == "courier.delivery.json":
        return _pick(doc, ("transport", "commit", "result_sha256", "ref"))
    if name == "chain.exit-census.json":
        surv = doc.get("survivors")
        return {"survivors": [None] * len(surv)} if isinstance(surv, list) else {}
    return {}  # presence-only JSON (chain.started, refusal.json, network_time_off.action.json, ...)


def project_bytes(name, raw):
    try:
        doc = json.loads(raw)
    except ValueError:
        return b"not-json"  # keep "unreadable" visible to the reader without keeping content
    proj = project_doc(name, doc)
    return b"[]" if proj is None else json.dumps(proj).encode()


class Files(dict):
    """name -> projected bytes for allowlisted files; .all_names = every file name listed (names only)."""
    all_names: frozenset = frozenset()


# --- sources -------------------------------------------------------------------

def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False)


def list_git_nights(ref_glob: str, repo: Path):
    out = _git(["for-each-ref", "--format=%(refname:short)", ref_glob.replace("origin/", "refs/remotes/origin/", 1)
                if ref_glob.startswith("origin/") else ref_glob], repo).stdout.decode().split()
    return sorted(out)


def load_git_night(ref: str, repo: Path):
    """Return (night_name, files dict or None). Allowlisted names only are read."""
    name = ref.split("night-results/", 1)[-1]
    base = f"{ref}:{NIGHT_SUBDIR}/{name}"
    tree = _git(["ls-tree", "--name-only", f"{ref}:{NIGHT_SUBDIR}/{name}"], repo)
    if tree.returncode != 0:
        return name, None
    listed = {n for n in tree.stdout.decode().split("\n") if n}
    files = Files()
    files.all_names = frozenset(listed)
    for f in sorted(listed & ALLOWLIST):
        if f in EXISTENCE_FILES:
            files[f] = b""  # M1: presence from ls-tree only; contents are never fetched
        else:
            files[f] = project_bytes(f, _git(["show", f"{base}/{f}"], repo).stdout)
    return name, files


def load_tree_night(path: Path):
    files = Files()
    files.all_names = frozenset(p.name for p in path.iterdir())
    for f in sorted(ALLOWLIST):
        p = path / f
        if p.is_file() and not p.is_symlink():
            files[f] = b"" if f in EXISTENCE_FILES else project_bytes(f, p.read_bytes())
    return path.name, files


# --- replay --------------------------------------------------------------------

def _json(files, name):
    raw = files.get(name)
    if raw is None:
        return None
    try:
        doc = json.loads(raw)
    except ValueError:
        return None
    return doc if isinstance(doc, dict) else None


def _int(value):
    return value if type(value) is int else None


def recorded_facts(files):
    """What the night's own records say, read independently of the shadow modules."""
    res, ex = _json(files, "result.json"), _json(files, "chain.exited")
    haz = _json(files, "hazard_result.json")
    cen = _json(files, "chain.exit-census.json")
    courier = _json(files, "courier.json")
    hz_chain = haz.get("chain") if isinstance(haz, dict) and isinstance(haz.get("chain"), dict) else {}
    surv = cen.get("survivors") if isinstance(cen, dict) else None
    act = _json(files, "network_time_off.action.json")
    names = getattr(files, "all_names", None) or frozenset(files)
    off_alt = "network_time_off.json" in names
    return {
        "result_present": "result.json" in files,
        "refusal_present": "refusal.json" in files,
        "fault_boolean_present": any(isinstance(d, dict) and type(d.get("fault")) is bool for d in (res, haz)),
        "chain_outcome": next((d["chain_outcome"] for d in (res, haz) if isinstance(d, dict)
                               and isinstance(d.get("chain_outcome"), str)), None),
        "verdict": res.get("verdict") if res and isinstance(res.get("verdict"), str) else None,
        "chain_started": "chain.started" in files,
        "chain_exited": "chain.exited" in files,
        "exit_code_chain_exited": _int(ex.get("exit_code")) if ex else None,
        "exit_code_result": _int(res.get("chain_exit_code")) if res else None,
        "exit_code_hazard_result": _int(hz_chain.get("exit_code")),
        "courier_sent_marker": "courier.sent" in files,
        "courier_sent_field": courier.get("sent") if courier and isinstance(courier.get("sent"), bool) else None,
        "exit_census_survivor_count": len(surv) if isinstance(surv, list) else None,
        "network_time_off_action_record": act is not None or off_alt,
        # file NAMES only (full ls-tree listing); fields inside delivered files are not inspected
        "restore_record_in_delivered_tree": any("restore" in n.lower() for n in names),
    }


def shadow_replay(files, now_epoch_s):
    if not TMP_ROOT.is_dir():
        raise SystemExit(f"temp root {TMP_ROOT} is missing; mount the SSD or set SM_SHADOW_TMP "
                         "(the internal disk is deliberately not a fallback)")
    with tempfile.TemporaryDirectory(prefix="sm-shadow-", dir=TMP_ROOT) as tmp:
        night = Path(tmp) / "night"
        night.mkdir()
        for name, raw in files.items():
            (night / name).write_bytes(raw if name in JSON_FILES else b"")  # raw is already projected
        obs = window_state.observe_night_dir(Path(tmp))
    report = window_state.derive_window_state(obs, now_epoch_s)
    host = host_effects.HostFacts(result_present="result.json" in files)
    owed = host_effects.owed_effects(host, report)
    return obs, report, owed


def classify_exit(rec, night_name=""):
    code = rec["exit_code_chain_exited"]
    if code is None:
        code = rec["exit_code_result"]
    if code is None:
        return None
    tool = chain_contract_for(night_name)
    if tool == "unknown":
        return {"tool": tool, "word": "unclassed", "class": "unknown", "declared": False}
    c = exit_contract.classify(tool, code)
    return {"tool": tool, "word": c.word, "class": c.exit_class.value, "declared": c.declared}


def expected_outcome(rec):
    if not rec["result_present"]:
        return "UNKNOWN"
    if rec["verdict"] == "REFUSED" and not (rec["chain_started"] or rec["chain_exited"]):
        return "REFUSED_PRE_CHAIN"
    if rec["verdict"] == "ABORTED":
        return "ABORTED"
    if rec["verdict"] == "REHEARSAL_ONLY":
        return "UNKNOWN"  # rehearsal is not a measurement (window_state's stated rule)
    code = rec["exit_code_chain_exited"] if rec["chain_exited"] else None
    if code is None:
        return "UNKNOWN"
    return "CHAIN_FAILED" if code != 0 else "MEASURED"


def agreement(rec, report, exit_cls, night_name=""):
    checks = []

    def add(cid, status, detail):
        checks.append({"id": cid, "status": status, "detail": detail})

    state, outcome = report.state.value, report.outcome.outcome.value
    exp = expected_outcome(rec)
    got = "MEASURED" if outcome.startswith("MEASURED") else outcome
    add("outcome", "agree" if exp == got else "disagree", f"records imply {exp}; shadow derives {outcome}")

    if rec["chain_outcome"] is not None:
        # W1-style record: GO kept by design, failure carried in chain_outcome / fault. Compare, do not mask.
        rec_out = {"COMPLETE": "MEASURED"}.get(rec["chain_outcome"], rec["chain_outcome"])
        add("recorded_chain_outcome", "agree" if rec_out in (got, "UNKNOWN") else "disagree",
            f"record carries chain_outcome {rec['chain_outcome']}; shadow derives {outcome}")
    elif rec["verdict"] == "GO" and outcome in {"CHAIN_FAILED", "ABORTED"}:
        checks.append({"id": "verdict_masks_outcome", "status": "disagree", "kind": "writer_candidate",
                       "detail": f"result verdict GO (admission) while the derived outcome is {outcome}; "
                                 "the record's verdict word does not carry the chain's failure (audit finding A-01 pattern)"})
    problems = []
    if rec["chain_exited"] and not rec["chain_started"]:
        problems.append("chain.exited without chain.started")
    if rec["chain_exited"] and state not in POST_EXIT_STATES:
        problems.append(f"chain.exited present but state {state}")
    if rec["chain_started"] and not rec["chain_exited"] and not rec["result_present"] \
            and state not in {"ChainOpen", "ChainUnkilled"}:
        problems.append(f"chain open in records but state {state}")
    if rec["refusal_present"] and not (rec["chain_started"] or rec["chain_exited"]) \
            and state != "RefusedPreChain" and state not in POST_RESULT_STATES:
        problems.append(f"refusal without chain but state {state}")
    if rec["refusal_present"] and rec["verdict"] == "GO":
        problems.append("refusal.json present with verdict GO")
    add("chain_lifecycle", "disagree" if problems else "agree", "; ".join(problems) or "consistent")

    codes = {k: rec[k] for k in ("exit_code_chain_exited", "exit_code_result", "exit_code_hazard_result")
             if rec[k] is not None}
    if len(set(codes.values())) > 1:
        add("exit_code_sources", "disagree", "sources differ: " + ", ".join(sorted(codes)))
    else:
        add("exit_code_sources", "agree" if codes else "n/a",
            "single value across " + ", ".join(sorted(codes)) if codes else "no exit code recorded")

    if exit_cls is None or rec["verdict"] is None:
        add("verdict_vs_exit_class", "n/a", "no exit code or no verdict")
    elif rec["verdict"] in VERDICT_CLASS:
        ok = exit_cls["class"] in VERDICT_CLASS[rec["verdict"]]
        add("verdict_vs_exit_class", "agree" if ok else "disagree",
            f"verdict {rec['verdict']}; {exit_cls['tool']} word {exit_cls['word']}"
            + ("" if exit_cls["declared"] else "; undeclared code"))
    elif rec["verdict"] == "GO":
        add("verdict_vs_exit_class", "agree" if exit_cls["declared"] else "note",
            f"GO is admission only; {exit_cls['tool']} word {exit_cls['word']}, class {exit_cls['class']}"
            + ("" if exit_cls["declared"] else "; undeclared code"))
    else:
        add("verdict_vs_exit_class", "n/a", "verdict " + str(rec["verdict"]))

    if rec["result_present"]:
        sent = rec["courier_sent_marker"] or rec["courier_sent_field"] is True
        if sent and state not in DELIVERED_STATES:
            add("delivery", "disagree", f"courier sent but state {state}")
        elif not sent and state in DELIVERED_STATES:
            add("delivery", "disagree", f"state {state} without courier send record")
        else:
            add("delivery", "agree", "state matches courier records")
    else:
        add("delivery", "n/a", "no result.json")

    frc = dict(report.outcome.evidence).get("fault_reason_count", 0)
    rec = {**rec, "night": night_name}
    for inv in report.violated_invariants:
        kind, why = explain_invariant(inv, rec, frc)
        checks.append({"id": "invariant:" + inv, "status": "disagree", "kind": kind, "detail": why})

    if rec["network_time_off_action_record"] and not rec["restore_record_in_delivered_tree"]:
        add("restore_records", "note",
            "network-time-off action recorded; no restore record is delivered (host effect unobserved)")
    else:
        add("restore_records", "n/a", "no network-time-off action record or restore record present")
    surv = rec["exit_census_survivor_count"]
    if surv:
        add("chain_survivors", "note", f"exit census lists {surv} survivor(s)")
    return checks


def replay_night(name, files, now_epoch_s):
    if files is None:
        return {"night": name, "missing": True, "files_present": [],
                "agreement": {"checks": [], "disagreements": [{"id": "night_dir", "detail": "night directory absent in source"}]}}
    rec = recorded_facts(files)
    obs, report, owed = shadow_replay(files, now_epoch_s)
    exit_cls = classify_exit(rec, name)
    checks = agreement(rec, report, exit_cls, name)
    return {
        "night": name,
        "derived": True,
        "custody": False,
        "files_present": sorted(files),
        "recorded": rec,
        "shadow": {
            "state": report.state.value,
            "outcome": report.outcome.outcome.value,
            "outcome_reasons": report.outcome.reasons,
            "reasons": report.reasons,
            "violated_invariants": report.violated_invariants,
            "reader_errors": list(obs.errors),
            "markers": sorted(obs.markers),
            "state_sequence": state_sequence(rec, report),
        },
        "exit_class": exit_cls,
        "owed_effects": [{"effect": o.effect.value, "subject": o.subject, "status": o.status,
                          "reason": o.reason} for o in owed],
        "agreement": {"checks": checks,
                      "disagreements": [c for c in checks if c["status"] == "disagree"],
                      "notes": [c for c in checks if c["status"] == "note"]},
    }


def state_sequence(rec, report):
    """Ordered states the markers support. Derived from record presence, not time."""
    seq = []
    if rec["refusal_present"] and not rec["chain_started"]:
        seq.append("RefusedPreChain")
    if rec["chain_started"]:
        seq.append("ChainOpen")
    if rec["chain_exited"]:
        seq.append("ChainExited")
    if rec["result_present"]:
        seq.append("ResultWritten")
    if rec["courier_sent_marker"] or rec["courier_sent_field"] is True:
        seq.append("Delivered")
    return seq + ([] if report.state.value in seq else ["(derived final) " + report.state.value])


def summarize(nights):
    rows = []
    for n in nights:
        dis = n["agreement"]["disagreements"]
        sh = n.get("shadow", {})
        rows.append({"night": n["night"], "state": sh.get("state"), "outcome": sh.get("outcome"),
                     "disagreements": [d["id"] for d in dis], "agree": not dis})
    return {"nights": len(rows), "agree": sum(r["agree"] for r in rows),
            "disagree": sum(not r["agree"] for r in rows), "rows": rows}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--git-ref-glob", help="e.g. 'origin/night-results/*'")
    src.add_argument("--tree", type=Path, help="directory of night directories")
    ap.add_argument("--repo", type=Path, default=REPO, help="git repo (git mode)")
    ap.add_argument("--night", action="append", help="restrict to these night names")
    ap.add_argument("--family", action="append", default=None,
                    help="night-name prefix to replay; default is only align-r1-* and align-pilot-* "
                         "(closed ALIGN nights). Any other family must be named here explicitly.")
    ap.add_argument("--exclude", action="append", default=[], help="night names to exclude")
    ap.add_argument("--out", type=Path, help="write derived JSON here (default stdout)")
    ap.add_argument("--now", type=float, default=None, help="epoch for now-dependent invariants")
    args = ap.parse_args(argv)
    now = args.now if args.now is not None else time.time()
    families = tuple(args.family) if args.family else DEFAULT_FAMILIES
    loaded, skipped = [], 0
    # The gate runs on the name BEFORE anything is loaded: gated-out nights are never opened.
    if args.git_ref_glob:
        for ref in list_git_nights(args.git_ref_glob, args.repo):
            if not family_allowed(ref.split("night-results/", 1)[-1], families):
                skipped += 1
                continue
            loaded.append(load_git_night(ref, args.repo))
    else:
        for d in sorted(p for p in args.tree.iterdir() if p.is_dir()):
            if not family_allowed(d.name, families):
                skipped += 1
                continue
            loaded.append(load_tree_night(d))
    loaded = [(n, f) for n, f in loaded
              if (not args.night or n in args.night) and n not in args.exclude]
    nights = [replay_night(n, f, now) for n, f in loaded]
    doc = {"schema": "joulewise.sm_shadow_replay.v1", "derived": True, "custody": False,
           "structure_only": True, "families": list(families),
           "skipped_by_family_gate": skipped, "summary": summarize(nights), "nights": nights}
    text = json.dumps(doc, indent=1, sort_keys=True)
    if args.out:
        args.out.write_text(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
