"""Structure-only falsification probe for the 2026-11-07 B5 release-hold trace (for the lead to run).

Prints ONLY counts, file presence, and enum words checked against fixed vocabularies. Never a value.
Usage: python3 -I probe_release_hold.py <OUT>/comparison.json <analysed_windows.json> [<dry-run custody root>]
The third argument (optional) enables the D5 probe, which reads only floor.resolutions[*].{status,reason_codes}
from L9's claim-verdicts and refuses any word outside the engine's resolution vocabulary.
"""
import collections
import glob
import json
import math
import os
import re
import sys

RESOLUTION_STATUS = {"exact", "transported", "refused"}
RESOLUTION_CODES = {  # joulewise/analysis_engine/inputs.py + __init__.py resolution reason codes
    "cell_missing", "cell_stale", "transport_group_incomplete", "cell_not_claim_ready", "artifact_schema_invalid",
    "consumer_term_unknown", "consumer_identity_undeclared", "consumer_identity_set_unauthenticated"}
SUMMARY_STATUS = {"succeeded", "failed", "partial", "aborted", None}
ANCHOR_STATUS = {"bounded", "unbounded", "not recorded", None}
DECISIONS = {"admit", "abort", "continue", "retry", "admitted", "rejected", None}


def word(value, vocabulary):
    return value if value in vocabulary else ("<other-word>" if isinstance(value, str) else "<non-word>")


def load_rows(path):
    rows = json.load(open(path))["comparisons"]
    rail_diff, rail_same, rc_only, rc_null = set(), set(), set(), set()
    for r in rows:
        p = r["key"].split("/")
        if r["family"] == "routing_id" and p[0] == "machine" and len(p) == 3 and r["l9"] is None and r["recompute"] is not None:
            rc_only.add((p[1], p[2]))
        if p[0] == "machine" and len(p) == 5 and p[4] == "rail_delta_J":
            a, b = r["l9"], r["recompute"]
            if all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in (a, b)):
                (rail_same if r["verdict"] == "AGREE" else rail_diff).add((p[1], p[2]))
            elif isinstance(a, (int, float)) and b is None:
                rc_null.add((p[1], p[2]))
    return rail_diff, rail_same, rc_only, rc_null


def roots(index_path):
    out = {}
    for a in json.load(open(index_path))["attempts"]:
        if a.get("claim_usable") is True:
            out[a["pack"]] = (a["claim_runs_root"], a["bound_runs_root"], a["archive_root"])
    return out


def member_dir(pack_roots, rid):
    claim, bound, _ = pack_roots
    for root in (claim, bound):
        if os.path.isdir(os.path.join(root, rid)):
            return os.path.join(root, rid)
    return None


def metadata(path):
    try:
        return json.load(open(os.path.join(path, "metadata.json")))
    except (OSError, ValueError):
        return {}


def main(cmp_path, index_path, custody=None):
    rail_diff, rail_same, rc_only, rc_null = load_rows(cmp_path)
    packs = roots(index_path)
    out = {}
    # D2: idle re-measurement (an attempt-N rich idle file, N >= 2) in members whose rail differs vs agrees.
    for label, members in (("rail_differs", rail_diff), ("rail_agrees", rail_same)):
        c = collections.Counter()
        for pack, rid in members:
            d = member_dir(packs[pack], rid) if pack in packs else None
            if d is None:
                c["member_dir_unavailable"] += 1
                continue
            retry = bool(glob.glob(os.path.join(d, "rich_telemetry_idle_attempt_*.jsonl")))
            attempts = (metadata(d).get("environment_admission") or {}).get("attempts")
            c["attempt_file_present" if retry else "attempt_file_absent"] += 1
            c["metadata_attempts_%s" % (len(attempts) if isinstance(attempts, list) else "none")] += 1
        out["D2_" + label] = dict(c)
    # D4: recompute-only members: sampling clock stamps present?
    c = collections.Counter()
    for pack, rid in rc_only:
        d = member_dir(packs[pack], rid) if pack in packs else None
        if d is None:
            c["member_dir_unavailable"] += 1
            continue
        stamps = ((metadata(d).get("uncertainty_evidence") or {}).get("clock_anchor") or {}).get("clock_stamps") or {}
        c["stamps_%s" % ("both" if {"sampling_started", "sampling_stopped"} <= set(stamps) else "missing")] += 1
        c["admission_decision_%s" % word((metadata(d).get("environment_admission") or {}).get("decision"), DECISIONS)] += 1
    out["D4_recompute_only"] = dict(c)
    # D3: L9-number / recompute-null members: summary and anchor status words.
    c = collections.Counter()
    for pack, rid in rc_null:
        d = member_dir(packs[pack], rid) if pack in packs else None
        if d is None:
            c["member_dir_unavailable"] += 1
            continue
        try:
            status = json.load(open(os.path.join(d, "summary_metrics.json"))).get("status")
        except (OSError, ValueError):
            status = None
        anchor = ((metadata(d).get("uncertainty_evidence") or {}).get("clock_anchor") or {}).get("status")
        c["status_%s/anchor_%s" % (word(status, SUMMARY_STATUS), word(anchor, ANCHOR_STATUS))] += 1
    out["D3_l9_only_values"] = dict(c)
    # D6: BETA's NEG-8 rescreen bracket: protocol word and which bound terms are finite (presence only).
    if "beta" in packs:
        path = os.path.join(packs["beta"][2], "withheld/neg8-rescreen-bracket.json")
        try:
            gross = ((json.load(open(path)).get("bracket") or {}).get("claim_families") or {}).get("gross_energy") or {}
            out["D6_beta_bracket"] = {
                "protocol": word(gross.get("endpoint_protocol"), {"replicated_endpoints", "planned", "legacy"}),
                **{k + "_finite": isinstance(gross.get(k), (int, float)) and math.isfinite(gross[k])
                   for k in ("bound_envelope_j", "bound_prediction_j")}}
        except (OSError, ValueError):
            out["D6_beta_bracket"] = "unavailable"
    # D5: L9 contrast floor-resolution words only (opt-in; reads the claim-verdicts output).
    if custody:
        names = glob.glob(os.path.join(custody, "**", "*-claim-verdicts.json"), recursive=True)
        c = collections.Counter()
        for name in names:
            for row in json.load(open(name)).get("contrasts", []):
                for res in ((row.get("floor") or {}).get("resolutions") or []):
                    codes = tuple(word(x, RESOLUTION_CODES) for x in res.get("reason_codes") or [])
                    c["%s:%s" % (word(res.get("status"), RESOLUTION_STATUS), ",".join(codes) or "-")] += 1
        out["D5_resolution_words"] = dict(c)
        out["D5_files"] = len(names)
    text = json.dumps(out, sort_keys=True, indent=1)
    if re.search(r"\d\.\d|\de[-+]?\d", text):
        raise SystemExit("refused: output would carry a decimal")
    print(text)


if __name__ == "__main__":
    main(*sys.argv[1:])
