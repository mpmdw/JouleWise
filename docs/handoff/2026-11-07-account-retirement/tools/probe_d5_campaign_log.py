"""Structure-only D5 probe: why the claim gate's GAMMA floor resolutions refused with artifact_schema_invalid.

For the lead to run, on the dry-run custody, from a clean checkout whose joulewise tree equals the pinned analysis
commit (main at d271fb476 does). It replays step 9's input loading (joulewise.cli._cmd_analyze_claims: the same
block5_claim_gate_inputs and analyze_claims call, the same arguments dry_run.step_9 builds) and captures:

  * the claim-side floor evidence binding (analysis_engine.inputs.bind_floor_artifact_evidence): every global and
    per-cell problem, reduced to a fixed label (the code word before ':' or a phrase from the binder's source);
  * which floor cells were bound;
  * what each GAMMA arm's floor request returned (request / identity codes / empty);
  * each contrast's resolution status and reason codes;

then STOPS (a BaseException raised right after both contrasts' floors are resolved), before any claim artifact is
written. stdout/stderr of the engine are discarded. It prints only labels, cell ids, words and counts, and refuses
output with a decimal.

Usage (from the checkout root):
  python3.13 -I docs/process_traces/2026-11-07-b5-release-trace/probe_d5_binding.py <repo root> <custody root> <window index>
"""
import collections
import contextlib
import io
import json
import logging
import re
import shutil
import sys
import tempfile
from pathlib import Path

# Free-text binder problems (analysis_engine/inputs.py bind_floor_artifact_evidence and helpers at 929fc65c9).
PHRASES = (
    (r"complete bundle sha256 mismatch", "complete_bundle_sha256_mismatch"),
    (r"config sha256 mismatch", "config_sha256_mismatch"),
    (r"stored floor metric does not match strict summary", "stored_metric_mismatch"),
    (r"scientific config identity is unavailable", "scientific_identity_unavailable"),
    (r"stack identity is unavailable", "stack_identity_unavailable"),
    (r"calibration bundle status is not succeeded", "bundle_status_not_succeeded"),
    (r"calibration bundle_id is not a safe basename", "bundle_id_unsafe"),
    (r"does not have one scientific config identity", "cell_identity_not_single"),
    (r"stack identity does not match the floor cell", "cell_stack_identity_mismatch"),
    (r"phase window_class cell must extract", "phase_cell_metric_mismatch"),
    (r"bound to non-phase window_class", "phase_metric_window_class_mismatch"),
    (r"^metadata\.source_provenance", "source_provenance_problem"),
    (r"floor evidence binding was not loaded", "binding_not_loaded"),
)


def label(problem):
    text = str(problem)
    m = re.match(r"strict validation raised ([A-Za-z_]+)", text)
    if m:
        return "strict_validation_raised:" + m.group(1)
    m = re.match(r"([a-z][a-z0-9_]{2,80})(:|$)", text)
    if m:
        return m.group(1)
    for pattern, name in PHRASES:
        if re.search(pattern, text):
            return name
    # Unclassified (strict-validator or other free text): its alphabetic words only, digits stripped.
    words = [w for w in re.findall(r"[A-Za-z_][A-Za-z_.]*", text) if not re.search(r"\d", w)][:6]
    return "unclassified:" + "_".join(w.lower().strip(".") for w in words)


class Stop(BaseException):
    pass


def outputs(record):
    names = set()
    for step in record.get("steps", []):
        for item in step.get("outputs") or []:
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                names.add(item["name"])
    return sorted(names)


def one(names, pattern):
    found = [n for n in names if re.fullmatch(pattern, n)]
    if len(found) != 1:
        raise SystemExit("refused: custody output %s found %d times" % (pattern.split("/")[-1], len(found)))
    return found[0]


def main(repo, custody, window_index):
    repo, custody = Path(repo).resolve(), Path(custody).resolve()
    sys.path.insert(0, str(repo))
    import os
    os.chdir(repo)
    logging.disable(logging.CRITICAL)
    from joulewise import cli
    from joulewise import analysis_engine as engine
    from joulewise.analysis_engine import inputs as inputs_mod
    from scripts import produce_b5_disclosures as pbd

    record = json.loads((custody / "dry-run/B5-BLIND-DRY-RUN-RECORD.json").read_bytes())
    restricted = custody / "dry-run/restricted"
    names = outputs(record)
    floor_path = restricted / one(names, r"mint/[0-9a-f]{64}-aggregate-floor\.json")
    manifest_path = restricted / one(names, r"finalized/[^/]+\.finalized\.json")
    extraction = {p: json.loads((restricted / one(names, r"mint/[0-9a-f]{64}-extraction-%s\.json" % p)).read_bytes())
                  for p in ("alpha", "beta")}
    floor = json.loads(floor_path.read_bytes())

    pins = pbd.SealPins.load()
    table = pbd.sealed_pack_table(seal_pins=pins)
    index = pbd.load_window_index(Path(window_index), seal_pins=pins, pack_table=table)
    records = tuple(pbd.open_attempt_record(e, seal_pins=pins, pack_table=table) for e in index.entries)
    windows = pbd.select_analysed_attempts(index, records, seal_pins=pins)
    evidence_roots = {k: Path(v) for k, v in pbd._evidence_roots(floor, extraction, windows).items()}
    runs_root = Path(windows["gamma"].claim_runs_root)


    import collections as C
    ENUM = re.compile(r"^[a-z][a-z0-9_]{0,40}$")
    out = {}
    for ci, cell in enumerate(floor.get("cells", [])):
        if not isinstance(cell, dict) or "d117" not in str(cell.get("cell_id")):
            continue
        prov = cell.get("provenance") or {}
        for comp in ("absolute", "comparative"):
            c = prov.get(comp) or {}
            rid = c.get("evidence_root_id")
            root = evidence_roots.get(rid)
            rec = {"root_mapped": root is not None}
            if root is None:
                out["%s|%s" % (cell.get("cell_id"), comp)] = rec; continue
            path = Path(root) / "campaign_log.jsonl"
            rows = [json.loads(l) for l in path.read_bytes().splitlines() if l.strip()]
            rec["rows"] = len(rows)
            rec["row_keysets"] = dict(C.Counter(",".join(sorted(r.keys())) for r in rows if isinstance(r, dict)))
            ev = C.Counter()
            for r in rows:
                if isinstance(r, dict):
                    for k in ("event", "kind", "type", "status", "phase", "action", "stage", "outcome"):
                        v = r.get(k)
                        if isinstance(v, str) and ENUM.match(v):
                            ev["%s=%s" % (k, v)] += 1
            rec["enum_words"] = dict(ev)
            members = inputs_mod._order_member_ids(rows, campaign_log=True) or []
            pos = C.Counter(members)
            seqs = [q for q in inputs_mod._component_order_sequences(cell, comp) if q]
            cnt = C.Counter()
            dup_ev = C.Counter()
            for q in seqs:
                for b in q:
                    n = pos.get(b, 0); cnt["count_%s" % (n if n < 3 else "3plus")] += 1
                    if n > 1:
                        for r in rows:
                            if isinstance(r, dict) and (r.get("bundle_id") == b or r.get("run_id") == b or b in (r.get("bundle_ids") or [])):
                                for k in ("event", "kind", "type", "status", "phase", "action"):
                                    v = r.get(k)
                                    if isinstance(v, str) and ENUM.match(v):
                                        dup_ev["%s=%s" % (k, v)] += 1
            rec["sequences"] = len(seqs); rec["seq_member_counts"] = dict(cnt); rec["dup_row_enum_words"] = dict(dup_ev)
            rec["log_members_total"] = len(members); rec["log_members_distinct"] = len(pos)
            out["%s|%s" % (cell.get("cell_id"), comp)] = rec
    text = json.dumps(out, sort_keys=True, indent=1)
    if re.search(r"\d\.\d|\de[-+]?\d", text):
        raise SystemExit("refused: output would carry a decimal")
    print(text)


if __name__ == "__main__":
    main(*sys.argv[1:])
