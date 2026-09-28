"""Build 10-issuance-text.json (design ruling D138-25G83-DESIGN-01 §7.1) by COPYING
disclosure and hold sentences verbatim from the rulings (markdown bold markers removed).
Run from the repository root: python3 -B <this> ; refuses if any source text is missing."""
import hashlib, json, re, sys
G = "docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/"
SCI, A1 = G + "21-science-gate-ruling.md", G + "31-addendum-ruling.md"
A2 = "docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/21-ruling.md"
A3 = "docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md"
LOG = "docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/evidence/timed-full-20260926T0000-20260927T1840-PDT.syslog.txt.gz"
LOG_PLAIN_SHA = "2f9bf739fde57accdce86e27a9494303585c976132e5dc5063a2cd31a5880b5c"
CAND = "docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json"
OUT = "docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/10-issuance-text.json"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
clean = lambda t: re.sub(r"\*\*", "", t).strip()
def line(path, prefix):
    hits = [l for l in open(path, encoding="utf-8").read().splitlines() if l.startswith(prefix)]
    if len(hits) != 1: sys.exit(f"FAIL {path}: {len(hits)} lines start with {prefix!r}")
    return clean(hits[0][2:] if hits[0].startswith("> ") else hits[0][2:] if hits[0].startswith("- ") else hits[0])
sci = {f"D{i}": line(SCI, f"- **D{i}.") for i in range(1, 7)}
d1_second_old = "The 12 others: 8 stopped by the 165,000-cell work cap, 3 by a wall-clock step above 5 ms during capture, 1 by an infeasible clock fit."
assert d1_second_old in sci["D1"], sci["D1"]
d1_new = line(A3, "> **D1 (replaces the second sentence).**").removeprefix("D1 (replaces the second sentence).").strip()
d3_add = line(A3, "> **D3 (adds).**").removeprefix("D3 (adds).").strip()
D = dict(sci)
D["D1"] = sci["D1"].replace(d1_second_old, d1_new)
D["D3"] = sci["D3"] + " " + d3_add
a1 = [l for l in open(A1, encoding="utf-8").read().splitlines() if l.startswith("> **A1.3 Hold")]
assert len(a1) == 1
D["D7"] = "D7. " + clean(a1[0].split("D7: ", 1)[1])
D["D8"] = line(A3, "> **D8. Network time was ON during both capture windows.**")  # A3 §4.1 replaces A2's D8 in full
D["D8"] = "D8. Network time was ON during both capture windows. " + D["D8"] if not D["D8"].startswith("D8.") else D["D8"]
H = {"H1": clean(line(A1, "> H1. No claim-bearing window"))}  # the A1 §7 appended text, not the §5.3 draft
H["H1"] = "H1. " + H["H1"] if not H["H1"].startswith("H1.") else H["H1"]
a3 = open(A3, encoding="utf-8").read().splitlines()
for h in ("H5", "H7"):  # A3 §4.4 (H5) and §4.6 (H7): one quoted paragraph each
    hits = [l for l in a3 if l.startswith(f"> **{h}.")]
    assert len(hits) == 1, h
    H[h] = clean(hits[0][2:])
# A3 §4.5 H6: the contiguous quoted block that starts "> **H6."; paragraphs joined with a blank line
i = [k for k, l in enumerate(a3) if l.startswith("> **H6.")]
assert len(i) == 1
blk = []
for l in a3[i[0]:]:
    if not l.startswith(">"): break
    blk.append(l[2:] if l.startswith("> ") else "")
H["H6"] = clean("\n\n".join(x for x in blk if x.strip()))
# A1 §7 A1.1 "adds to ... D2" and A1.4(d) corrects D4: carried verbatim (lead, after the issuing-record draft flagged the gap)
a1_lines = open(A1, encoding="utf-8").read().splitlines()
a11 = [l for l in a1_lines if l.startswith("> **A1.1 Classification of F1")]
a14d = [l for l in a1_lines if l.startswith("> (d) D4:")]
assert len(a11) == 1 and len(a14d) == 1, (a11, a14d)
D["D2"] = D["D2"] + " " + clean(a11[0][2:])
D["D4"] = D["D4"] + " A1.4 correction: " + clean(a14d[0][2:])
for k in ("D1", "D2", "D3", "D4", "D5", "D6"):
    if not D[k].startswith(k + "."): D[k] = k + ". " + D[k] if not D[k].startswith(k) else D[k]
cand = json.load(open(CAND))
def member_id(suffix):
    ids = [m["member_id"] for m in cand["derivation_corpus"]["members"] if m["member_id"].endswith(suffix)]
    assert len(ids) == 1, (suffix, ids)
    return ids[0]
import gzip
assert hashlib.sha256(gzip.open(LOG).read()).hexdigest() == LOG_PLAIN_SHA
claim_meaning = ("these bytes are an authentic issued calibration, and its numbers may serve as the timing-uncertainty "
                 "basis of a reported result. It is a property of the file. It is not permission to start a window. "
                 "Permission to start a claim-bearing window is separate; H1 withholds it, and H5 to H7 condition it.")
text = {
  "reason": "issued by the D-138 transaction of epoch 25G83 under design ruling D138-25G83-DESIGN-01, after cold science gate SCI-25G83-CANDIDATE-01 (PROCEED TO ISSUANCE) and addenda SCI-25G83-CANDIDATE-01-A1, -A2 and -A3 (PROCEED); identity and publication approved by the owner on 2026-09-27 (activation d528efb2 record item 17)",
  "required_verification": "complete: cold science gate SCI-25G83-CANDIDATE-01 over exclusions, per-night diagnostics, the screen-challenge outcome and the D-125 default; addenda A1 and A2; design ruling D138-25G83-DESIGN-01 and the gate of its section 9",
  "network_time_provenance": {  # content ruled by A3 §4.7 item 1
      "per_member_state": "on",
      "state_source": "after the fact, from the timed log and each capture's paired clock readings",
      "authenticated_off_admission": False,
      "members_with_correction_during_capture": [member_id("w1-20260927-d12")],
      "members_with_correction_tail_during_capture": [member_id("w2-20260927-d01")],
      "disclosure_id": "D8",
      "source_rulings": [{"id": "SCI-25G83-CANDIDATE-01-A2", "relative_path": A2, "file_sha256": sha(A2)},
                         {"id": "SCI-25G83-CANDIDATE-01-A3", "relative_path": A3, "file_sha256": sha(A3)}],
      "preserved_log": {"relative_path": LOG, "plain_text_sha256": LOG_PLAIN_SHA},
      "text": D["D8"]},
  "issuance_record": {
    "transaction": "D-138 issuance of epoch 25G83, design ruling D138-25G83-DESIGN-01",
    "source_candidate": {"relative_path": CAND, "file_sha256": sha(CAND), "derivation_sha256": cand["derivation_sha256"]},
    "rulings": [{"id": "SCI-25G83-CANDIDATE-01", "relative_path": SCI, "file_sha256": sha(SCI)},
                {"id": "SCI-25G83-CANDIDATE-01-A1", "relative_path": A1, "file_sha256": sha(A1)},
                {"id": "SCI-25G83-CANDIDATE-01-A2", "relative_path": A2, "file_sha256": sha(A2)},
                {"id": "SCI-25G83-CANDIDATE-01-A3", "relative_path": A3, "file_sha256": sha(A3)}],
    "disclosures": [{"id": f"D{i}", "text": D[f"D{i}"]} for i in range(1, 9)],
    "holds": [{"id": h, "text": H[h]} for h in ("H1", "H5", "H6", "H7")],
    "claim_eligible_meaning": claim_meaning,
    "hold_enforcement": "H1 is enforced outside these bytes, at the arm admission list; lifting it changes no byte of this file"}}
assert sha(CAND) == "dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2"
open(OUT, "w", encoding="utf-8").write(json.dumps(text, indent=2, ensure_ascii=False) + "\n")
for x in text["issuance_record"]["disclosures"] + text["issuance_record"]["holds"]: print(x["id"], len(x["text"]), x["text"][:90])
print("wrote", OUT, sha(OUT))
