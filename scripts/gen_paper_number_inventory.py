#!/usr/bin/env python3
"""Regenerate the reviewed paper-number inventory; --check compares committed bytes.

Bindings and census seeds are authoring inputs here, independent of the generated
JSON. Pins and ratchet ceilings are deliberately fixed, never renewed from the
current paper or source bytes. Census contexts locate literals without line
numbers. The original census TSV was external to this checkout; its retained
unbound rows below preserve the context, offset, and duplicate occurrence data.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "joulewise-paper-number-inventory/v1"

SOURCES = {
 "XD": {"path": "docs/paper/round7/excursion-decomposition.json",
        "sha256": "21618026dfc677165b2a1acd511ff0d3130bd3837fa344c9ca9fbac95d7e058b",
        "pin": {"kind": "registry_line", "pattern": [
            r"^- XD = docs/paper/round7/excursion-decomposition\.json, sha256 ([0-9a-f]{64}) ",
            r"^\| DX-001 — XD artifact identity; no draft site \| ([0-9a-f]{64}) \|"]}},
 "WEX": {"path": "docs/paper/figures/worked-examples.json",
         "sha256": "6fba73a8741224ad67f9aacd6de116213d057843fc5bc733752ebc80b6b6bc16",
         "pin": {"kind": "registry_line", "pattern": r"^WEX = `docs/paper/figures/worked-examples\.json`, SHA-256 `([0-9a-f]{64})`"}},
 "S17": {"path": "configs/calibration/calibration_acceptance_d079_v2_n17_r3.json",
         "sha256": "73f022633e7bc22e9e129617f3f2ad8797293adaff3b53923dc41f75da2ae917",
         "pin": {"kind": "python_constant", "file": "joulewise/calibration_bracketing.py",
                 "name": "ANCHOR_V3_ACCEPTANCE_BOUND_SHA256"}},
}
GROUPS = []

def B(expr, render, **kw):
    d = {"class": "bound", "expr": expr, "render": render}; d.update(kw); return d
def T(expr, render, why, **kw):
    d = {"class": "tied", "expr": expr, "render": render, "why": why}; d.update(kw); return d
def C(literal, reason, **kw):
    d = {"class": "classed", "literal": literal, "reason": reason}; d.update(kw); return d

ON = "XD:summary.onset_best_fit_lag"
OFF = "XD:summary.offset_best_fit_lag"
DX = {
 "id": "dx",
 "title": "Section 2 historical current-method edge result and Figure 2 caption; registry DX-010/011/012/013, D-174 amendment",
 "entries": [
  {"id": "dx.capture", "anchor": "The source is the single capture `⟦capture⟧`, re-derived under the current rate-aware anchor `⟦anchor⟧`.",
   "slots": {"capture": B("XD:capture_member_id", "text", kind="text"),
             "anchor": B("XD:anchor_method", "text", kind="text")}},
  {"id": "dx.counts", "anchor": "The ⟦onset_n⟧ onset lags are all positive; ⟦off_neg⟧ of ⟦off_n⟧ offset lags are negative, ⟦off_pos⟧ positive, and ⟦off_zero⟧ zero.",
   "slots": {"onset_n": B(ON + ".count", "integer"),
             "off_neg": B(OFF + ".count_negative", "integer", registry="DX-013"),
             "off_n": B(OFF + ".count", "integer", registry="DX-013"),
             "off_pos": B(OFF + ".count_positive", "word_int"),
             "off_zero": B(OFF + ".count_zero", "word_int")}},
  {"id": "dx.medians", "anchor": "Their medians are ⟦onset_median⟧ ms and ⟦offset_median⟧ ms.",
   "slots": {"onset_median": B(ON + ".median_ms", "signed_1", registry="DX-010"),
             "offset_median": B(OFF + ".median_ms", "signed_1", registry="DX-011")}},
  {"id": "dx.edges", "anchor": "These are ⟦onset_n⟧ onset and ⟦off_n⟧ offset values (⟦edges⟧ edges) from one capture",
   "slots": {"onset_n": B(ON + ".count", "integer"),
             "off_n": B(OFF + ".count", "integer"),
             "edges": B("XD:summary.all_118_worst_excursions.count", "integer")}},
  {"id": "dx.caption_axis", "anchor": "The horizontal axis is pulse index ⟦first⟧–⟦last⟧ in command order",
   "slots": {"first": C("0", "index: first pulse index (0-based)"),
             "last": B("XD:per_pulse|last_index", "integer")}},
  {"id": "dx.caption_marks", "anchor": "Blue circles are the ⟦onset_n⟧ fitted onset lags; orange squares are the ⟦off_n⟧ fitted offset lags.",
   "slots": {"onset_n": B("XD:per_pulse[*].onset_best_fit_lag_ms|len", "integer"),
             "off_n": B("XD:per_pulse[*].offset_best_fit_lag_ms|len", "integer")}},
  {"id": "dx.caption_medians", "anchor": "Blue and orange dashed horizontal lines mark the respective medians, ⟦onset_median⟧ ms and ⟦offset_median⟧ ms;",
   "slots": {"onset_median": B(ON + ".median_ms", "signed_1", registry="DX-010"),
             "offset_median": B(OFF + ".median_ms", "signed_1", registry="DX-011")}},
  {"id": "dx.caption_leader", "anchor": "The leader at pulse index ⟦idx⟧ marks its ⟦lead⟧-ms best-fit onset.",
   "slots": {"idx": C("9", "index: the leader pulse; the predicate 'leader' checks per_pulse[pulse_index=9] holds the onset maximum"),
             "lead": B(ON + ".max_ms", "signed_int")}},
  {"id": "dx.caption_bound", "anchor": "the largest endpoint displacement in an accepted region, ⟦disp⟧ ms on that onset, equals the retained worst edge excursion. Adding the ⟦anchor_ms⟧-ms clock-anchor allowance gives ⟦bound_ms⟧ ms.",
   "slots": {"disp": B("REG:DG-042|strip_unit", "s_to_ms_exact", registry="DG-042",
                       note="the full-precision residual is replay-fenced (DG-042, check_paper_replay_fence); XD carries it only to 6 decimals, checked by predicate 'worst excursion'"),
             "anchor_ms": B("XD:bound_terms.b_anchor_s", "s_to_ms_exact",
                            cross=[{"expr": "REG:DG-026|strip_unit", "render": "s_to_ms_exact"}]),
             "bound_ms": B("XD:bound_terms.b_fiducial_s", "s_to_ms_exact",
                           cross=[{"expr": "REG:DG-027|strip_unit", "render": "s_to_ms_exact"}])}},
  {"id": "dx.caption_grid", "anchor": "The ⟦grid⟧-ms fitted lag grid reflects the search step;",
   "slots": {"grid": T("CONST:joulewise/powermetrics_fiducial.py#FIT_FINE_STEP_S", "s_to_ms_exact",
                       "method constant: the fine lag-search step")}},
  {"id": "dx.source_map", "anchor": "DX-012/013 bind the ⟦on_pos⟧/⟦on_n⟧ and ⟦off_neg⟧/⟦off_n⟧ counts. The same JSON's `per_pulse` array supplies each mark; its `summary.offset_best_fit_lag` supplies the ⟦off_pos⟧ positive and ⟦off_zero⟧ zero counts.",
   "slots": {"on_pos": B(ON + ".count_positive", "integer", registry="DX-012"),
             "on_n": B(ON + ".count", "integer", registry="DX-012"),
             "off_neg": B(OFF + ".count_negative", "integer", registry="DX-013"),
             "off_n": B(OFF + ".count", "integer", registry="DX-013"),
             "off_pos": B(OFF + ".count_positive", "word_int"),
             "off_zero": B(OFF + ".count_zero", "word_int")}},
 ],
 "predicates": [
  {"why": "onset median re-derived from the 59 per-pulse onset lags", "lhs": "XD:per_pulse[*].onset_best_fit_lag_ms|median", "rhs": ON + ".median_ms"},
  {"why": "offset median re-derived from the 59 per-pulse offset lags", "lhs": "XD:per_pulse[*].offset_best_fit_lag_ms|median", "rhs": OFF + ".median_ms"},
  {"why": "onset lags all positive (per_pulse)", "lhs": "XD:per_pulse[*].onset_best_fit_lag_ms|count_pos", "rhs": ON + ".count"},
  {"why": "negative offsets re-counted from per_pulse", "lhs": "XD:per_pulse[*].offset_best_fit_lag_ms|count_neg", "rhs": OFF + ".count_negative"},
  {"why": "positive offsets re-counted from per_pulse", "lhs": "XD:per_pulse[*].offset_best_fit_lag_ms|count_pos", "rhs": OFF + ".count_positive"},
  {"why": "zero offsets re-counted from per_pulse", "lhs": "XD:per_pulse[*].offset_best_fit_lag_ms|count_zero", "rhs": OFF + ".count_zero"},
  {"why": "negative + positive + zero offsets exhaust the 59 (D-174 amendment)", "lhs": [OFF + ".count_negative", OFF + ".count_positive", OFF + ".count_zero"], "rhs": OFF + ".count"},
  {"why": "59 onset + 59 offset = 118 edges", "lhs": [ON + ".count", OFF + ".count"], "rhs": "XD:summary.all_118_worst_excursions.count"},
  {"why": "leader: pulse index 9 carries the onset maximum", "lhs": "XD:per_pulse[pulse_index=9].onset_best_fit_lag_ms", "rhs": ON + ".max_ms"},
  {"why": "worst excursion: DG-042 residual (s) x1000 rounds to XD's 6-decimal worst edge excursion", "lhs": "REG:DG-042|strip_unit|float|x1000|round6", "rhs": "XD:bound_terms.max_worst_edge_excursion_ms"},
 ],
 "registry_checks": [
  {"key": "DX-010", "value": "⟦dx.medians.onset_median⟧ ms", "supplier_contains": ["XD#summary.onset_best_fit_lag.median_ms", "R7F_RENDER=signed_1_ms"]},
  {"key": "DX-011", "value": "⟦dx.medians.offset_median⟧ ms", "supplier_contains": ["XD#summary.offset_best_fit_lag.median_ms", "R7F_RENDER=signed_1_ms"]},
  {"key": "DX-012", "value": "⟦dx.source_map.on_pos⟧ of ⟦dx.source_map.on_n⟧", "supplier_contains": ["XD#summary.onset_best_fit_lag.count_positive", "XD#summary.onset_best_fit_lag.count"]},
  {"key": "DX-013", "value": "⟦dx.counts.off_neg⟧ of ⟦dx.counts.off_n⟧", "supplier_contains": ["XD#summary.offset_best_fit_lag.count_negative", "XD#summary.offset_best_fit_lag.count"]},
 ],
}
GROUPS.append(DX)

# ---- Section 4 overlap worked example and table; DG-131/132
G = "WEX:historical.geometry"
def ov(g, k):
    return B(None, "positive_overlap_decimal",
             inputs=[f"{G}[{g}].start", f"{G}[{g}].end", f"{G}[{g}].records[{k}].start", f"{G}[{g}].records[{k}].end"],
             cross=[{"expr": f"{G}[{g}].records[{k}].overlap", "render": "decimal_string"}])
def row(run, g, k):
    p = f"{run}_{k}"
    return (f"| {run} | ⟦{p}_idx⟧ | ⟦{p}_start⟧ | ⟦{p}_end⟧ | ⟦{p}_ov⟧ |",
            {f"{p}_idx": B(f"{G}[{g}].records[{k}].index", "integer"),
             f"{p}_start": B(f"{G}[{g}].records[{k}].start", "decimal_string"),
             f"{p}_end": B(f"{G}[{g}].records[{k}].end", "decimal_string"),
             f"{p}_ov": ov(g, k)})
rows = [row("r03", 0, k) for k in range(4)] + [row("r08", 1, k) for k in range(5)]
table_anchor = ("| Run | Record index (⟦zb⟧-based) | Start (relative s) | End (relative s) | Positive-overlap duration (s) |\n"
                "|---|---:|---:|---:|---:|\n" + "\n".join(r[0] for r in rows) + "\n\n")
table_slots = {"zb": C("0", "notation: 0-based indexing")}
for r in rows:
    table_slots.update(r[1])
for k in list(table_slots):
    if k.endswith("_ov"):
        table_slots[k] = dict(table_slots[k]); table_slots[k].pop("expr")
S4 = {
 "id": "s4_overlap",
 "title": "Section 4 record-overlap worked example and table; registry DG-131/132; source WEX historical.geometry",
 "entries": [
  {"id": "s4.r03_prose",
   "anchor": "In the 1.5B run r03, relative to epoch ⟦origin⟧ s, the phase [⟦ps⟧,⟦pe⟧] overlaps records [⟦a_s⟧,⟦a_e⟧] and [⟦b_s⟧,⟦b_e⟧] for ⟦a_ov⟧ and ⟦b_ov⟧ s: this phase fails the three-record minimum.",
   "slots": {"origin": B(f"{G}[0].origin", "integer"),
             "ps": B(f"{G}[0].start", "decimal_string"), "pe": B(f"{G}[0].end", "decimal_string"),
             "a_s": B(f"{G}[0].records[1].start", "decimal_string"), "a_e": B(f"{G}[0].records[1].end", "decimal_string"),
             "b_s": B(f"{G}[0].records[2].start", "decimal_string"), "b_e": B(f"{G}[0].records[2].end", "decimal_string"),
             "a_ov": {k: v for k, v in ov(0, 1).items() if k != "expr"},
             "b_ov": {k: v for k, v in ov(0, 2).items() if k != "expr"}}},
  {"id": "s4.r08_prose",
   "anchor": "r08 provides a three-overlap case: relative to epoch ⟦origin⟧ s, its phase is [⟦ps⟧,⟦pe⟧].",
   "slots": {"origin": B(f"{G}[1].origin", "integer"),
             "ps": B(f"{G}[1].start", "decimal_string"), "pe": B(f"{G}[1].end", "decimal_string")}},
  {"id": "s4.table", "anchor": table_anchor, "slots": table_slots},
  {"id": "s4.binary64", "anchor": "(the usual ⟦bits⟧-bit floating-point format)",
   "slots": {"bits": C("64", "notation: IEEE-754 binary64 width")}},
 ],
 "predicates": [
  {"why": "geometry[0] is run r03", "lhs": f"{G}[0].bundle", "rhs": "p2015-df-ph-decode-abs-r03"},
  {"why": "geometry[1] is run r08", "lhs": f"{G}[1].bundle", "rhs": "p2015-df-ph-decode-abs-r08"},
  {"why": "r03 table lists 4 records", "lhs": f"{G}[0].records|len", "rhs": 4},
  {"why": "r08 table lists 5 records", "lhs": f"{G}[1].records|len", "rhs": 5},
 ],
 "registry_checks": [
  {"key": "DG-131", "value": "phase [⟦s4.r03_prose.ps⟧,⟦s4.r03_prose.pe⟧] relative to ⟦s4.r03_prose.origin⟧ s",
   "supplier_contains": ["WEX#historical.geometry[0].{start,end,origin,records}",
                         "overlaps [⟦s4.table.r03_0_ov⟧,⟦s4.table.r03_1_ov⟧,⟦s4.table.r03_2_ov⟧,⟦s4.table.r03_3_ov⟧] s"]},
  {"key": "DG-132", "value": "phase [⟦s4.r08_prose.ps⟧,⟦s4.r08_prose.pe⟧] relative to ⟦s4.r08_prose.origin⟧ s",
   "supplier_contains": ["WEX#historical.geometry[1]",
                         "overlaps [⟦s4.table.r08_0_ov⟧,⟦s4.table.r08_1_ov⟧,⟦s4.table.r08_2_ov⟧,⟦s4.table.r08_3_ov⟧,⟦s4.table.r08_4_ov⟧] s"]},
 ],
}
GROUPS.append(S4)

# ---- Appendix A.3.8 retained calibration corpus; DG-128; source S17
M = "S17:derivation_corpus.members"
# Reviewed member count from the pinned S17 source; changes require review.
nrows = 17
a38_anchor = ("| Capture member | \\(b_{\\mathrm{fiducial}}\\) (s) |\n|---|---:|\n"
              + "\n".join(f"| `⟦m{k}⟧` | ⟦v{k}⟧ |" for k in range(nrows)) + "\n\n")
a38_slots = {}
for k in range(nrows):
    a38_slots[f"m{k}"] = B(f"{M}[{k}].member_id", "text", kind="text")
    a38_slots[f"v{k}"] = B(f"{M}[{k}].b_fiducial_s", "decimal_string")
A38 = {
 "id": "a38",
 "title": "Appendix A.3.8 retained calibration corpus; registry DG-128; source S17 (pinned by joulewise.calibration_bracketing.ANCHOR_V3_ACCEPTANCE_BOUND_SHA256)",
 "entries": [
  {"id": "a38.heading", "anchor": "#### A.3.8 Retained calibration corpus (⟦first⟧ to ⟦last⟧ instrument-validation captures), diagnostic, not campaign data",
   "slots": {"first": C("2026-07-22", "date: heading framing (first member's capture date)", kind="text"),
             "last": C("2026-07-25", "date: heading framing (last member's capture date)", kind="text")}},
  {"id": "a38.intro", "anchor": "These are the ⟦n⟧ per-capture \\(b_{\\mathrm{fiducial}}\\) bounds used by the n17 acceptance generation",
   "slots": {"n": B("S17:derivation_corpus.n", "integer", registry="DG-128")}},
  {"id": "a38.excluded", "anchor": "⟦n_excl⟧ predecessor members were excluded because",
   "slots": {"n_excl": B("S17:derivation_notes.excluded_predecessor_members|len", "word_int", case="capitalize")}},
  {"id": "a38.table", "anchor": a38_anchor, "slots": a38_slots},
 ],
 "predicates": [
  {"why": "member list length equals derivation_corpus.n", "lhs": f"{M}|len", "rhs": "S17:derivation_corpus.n"},
 ],
 "registry_checks": [
  {"key": "DG-128", "value": "⟦a38.intro.n⟧ b_fiducial_s bounds (table)",
   "supplier_contains": ["S17#derivation_corpus.members[].b_fiducial_s"]},
 ],
}
GROUPS.append(A38)

# Frozen unresolved rows from the 2026-09-28 census (line-independent).
UNBOUND_RESULTS = [
 {
  "literal": "50",
  "ctx": "50 phases: 33 crossed three reco",
  "offset": 0,
  "census_status": "UNPOLICED-REGISTERED",
  "occurrence": 0,
  "occurrences": 2
 },
 {
  "literal": "17",
  "ctx": "derives two constants from its retained 17-capture corpus. Student-\\(t\\)",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "17",
  "ctx": "cause the spread is estimated from only 17 captures—sets the maximum per",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "17",
  "ctx": " permitted pre/post difference. For \\(n=17\\) per-capture bounds, the sam",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "2.460856",
  "ctx": "(n-1\\) formula of Section 3) is \\(s_b = 2.460856\\) ms (retained SD operand, \\(",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "2.460856207694636",
  "ctx": "= 2.460856\\) ms (retained SD operand, \\(2.460856207694636\\) ms) and \\(t_{0.995,16}\\) is",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "10",
  "ctx": "times s_b\\times\\sqrt{2}\\) records about 10 ms (retained as 10.1648347577",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "10.164834757777545",
  "ctx": "t{2}\\) records about 10 ms (retained as 10.164834757777545 ms for byte-exact replay), pr",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "10.164835",
  "ctx": "or byte-exact replay), printed as the \\(10.164835\\)-ms maximum permitted pre/po",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "9.723589288793850",
  "ctx": "wance** starts from the corpus range, \\(9.723589288793850\\) ms, rounded to the nearest ",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "9.724",
  "ctx": "ven digit (`ROUND_HALF_EVEN`), giving \\(9.724\\) ms; Appendix A.3.8 prints t",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "17",
  "ctx": "\\(9.724\\) ms; Appendix A.3.8 prints the 17 bounds from the retained cali",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "9.724",
  "ctx": "ax(|B_{\\mathrm{post}}-B_{\\mathrm{pre}}|,9.724\\ \\mathrm{ms})\\), added once. ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "10.164835",
  "ctx": "t-window bound differ by 4 ms, pass the 10.164835-ms limit, and give \\(b=29+\\ma",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "9.724",
  "ctx": "164835-ms limit, and give \\(b=29+\\max(4,9.724)=38.724\\) ms. If the post-win",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0000010000000000000002",
  "ctx": "in every row is about 1 µs (retained as 0.0000010000000000000002 s for byte-exact replay).",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "50",
  "ctx": "prompt-processing phases in 50 bundles: 10 from `runs_window",
  "offset": 28,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "10",
  "ctx": "prompt-processing phases in 50 bundles: 10 from `runs_window_a10_2026072",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "40",
  "ctx": "and 40 from `runs_window_c_20260726`",
  "offset": 4,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "37",
  "ctx": "population, 37 of 50 phases overlapped two s",
  "offset": 12,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "50",
  "ctx": "population, 37 of 50 phases overlapped two samplin",
  "offset": 18,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "13",
  "ctx": "13 of 50 overlapped three. Accor",
  "offset": 0,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "50",
  "ctx": "13 of 50 overlapped three. Accordingly",
  "offset": 6,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "13",
  "ctx": "mum (`not_resolvable_sample_count`) and 13 passed",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "37",
  "ctx": "ecords failed the three-record minimum: 37 of the 50 1.5B",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "50",
  "ctx": "led the three-record minimum: 37 of the 50 1.5B",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "50",
  "ctx": "phases and none of the 50 7B phases, which overlapped t",
  "offset": 23,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.121034145",
  "ctx": "lasted 0.121034145 s, rendered as 0.121 s for th",
  "offset": 7,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.121",
  "ctx": "lasted 0.121034145 s, rendered as 0.121 s for the comparison below. O",
  "offset": 34,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "406",
  "ctx": "run's retained power trace, the 406 sampling records had a record",
  "offset": 32,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "405",
  "ctx": "ument’s physical resolution. Across the 405 differences",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "100",
  "ctx": "dg071-dg075-statistics.md) reports that 100 of 405 boundaries",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "405",
  "ctx": "g075-statistics.md) reports that 100 of 405 boundaries",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0000004",
  "ctx": "e a nonzero gap and that the largest is 0.0000004 s. The enforced endpoint",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.121",
  "ctx": "The 0.121-s phase is only barely longer",
  "offset": 4,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "37",
  "ctx": "record width; 37 phases had only two overlaps.",
  "offset": 14,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "37",
  "ctx": " map: registry DG-067/068/069 binds the 37/50/13 counts to",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "50",
  "ctx": "p: registry DG-067/068/069 binds the 37/50/13 counts to",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "13",
  "ctx": "registry DG-067/068/069 binds the 37/50/13 counts to",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "30",
  "ctx": "about 30 ms (retained as 0.03006793175",
  "offset": 6,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.030067931757111657",
  "ctx": "about 30 ms (retained as 0.030067931757111657 s for byte-exact replay). <!-",
  "offset": 25,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "59",
  "ctx": "The 59 of 59 onsets late and 49 of 5",
  "offset": 4,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "59",
  "ctx": "The 59 of 59 onsets late and 49 of 59 offs",
  "offset": 10,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "49",
  "ctx": "The 59 of 59 onsets late and 49 of 59 offsets early form a on",
  "offset": 29,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "59",
  "ctx": "The 59 of 59 onsets late and 49 of 59 offsets early form a one-dire",
  "offset": 35,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "50",
  "ctx": "50 members of `runs_window_7bflo",
  "offset": 0,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "50",
  "ctx": "(7B) passed in all 50 phases: 33 crossed three reco",
  "offset": 19,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "111",
  "ctx": "22T145535-e941c821`, record 0): *e_0* = 111 242 541 ns; the parsed channe",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "242",
  "ctx": "45535-e941c821`, record 0): *e_0* = 111 242 541 ns; the parsed channel po",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "541",
  "ctx": "5-e941c821`, record 0): *e_0* = 111 242 541 ns; the parsed channel powers",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.9169149999999999",
  "ctx": "2 541 ns; the parsed channel powers are 0.9169149999999999 W + 0.00898937 W + 0.0 W, giv",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.00898937",
  "ctx": "annel powers are 0.9169149999999999 W + 0.00898937 W + 0.0 W, giving *p_0* = 0.9",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0",
  "ctx": "e 0.9169149999999999 W + 0.00898937 W + 0.0 W, giving *p_0* = 0.925904369",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.9259043699999999",
  "ctx": " + 0.00898937 W + 0.0 W, giving *p_0* = 0.9259043699999999 W; counters 102 + 1 + 0 mJ gi",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "102",
  "ctx": " *p_0* = 0.9259043699999999 W; counters 102 + 1 + 0 mJ give *E_0* = 0.103",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1",
  "ctx": " = 0.9259043699999999 W; counters 102 + 1 + 0 mJ give *E_0* = 0.103 J; ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0",
  "ctx": ".9259043699999999 W; counters 102 + 1 + 0 mJ give *E_0* = 0.103 J; and ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.103",
  "ctx": "W; counters 102 + 1 + 0 mJ give *E_0* = 0.103 J; and *p_0* · 0.111242541 s ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.111242541",
  "ctx": " 0 mJ give *E_0* = 0.103 J; and *p_0* · 0.111242541 s = 0.10299995484180416 J, wh",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.10299995484180416",
  "ctx": " = 0.103 J; and *p_0* · 0.111242541 s = 0.10299995484180416 J, which differs from *E_0* b",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "4.5",
  "ctx": "84180416 J, which differs from *E_0* by 4.5·10⁻⁸ J, far inside the tolera",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.0000010000000000000002",
  "ctx": "very stamp reports a wall resolution of 0.0000010000000000000002 s (the closest binary64 value",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "4",
  "ctx": " to 1 µs) and a monotonic resolution of 4.166666666666666e-8 s, so *r* ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0000010000000000000002",
  "ctx": "ion of 4.166666666666666e-8 s, so *r* = 0.0000010000000000000002 s for every stamp.",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784298599.0949996",
  "ctx": " largest raw upper offset *w* − *mb* is 1784298599.0949996 s (at S_stop) and the smalles",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "1784298599.0945535",
  "ctx": "smallest raw lower offset *w* − *ma* is 1784298599.0945535 s (at S_pre); the difference ",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.00044608116149902344",
  "ctx": " s (at S_pre); the difference is span = 0.00044608116149902344 s (446 µs), the second of the",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "446",
  "ctx": "nce is span = 0.00044608116149902344 s (446 µs), the second of the four t",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "111",
  "ctx": "ly that amount. Worked example: *e_0* = 111 242 541 ns and *r_pre* = 0.00",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "242",
  "ctx": "hat amount. Worked example: *e_0* = 111 242 541 ns and *r_pre* = 0.000001",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "541",
  "ctx": "amount. Worked example: *e_0* = 111 242 541 ns and *r_pre* = 0.0000010000",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0000010000000000000002",
  "ctx": "e: *e_0* = 111 242 541 ns and *r_pre* = 0.0000010000000000000002 s ≈ 1000 ns, so *k_pre* = 111",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "111",
  "ctx": "0000000000002 s ≈ 1000 ns, so *k_pre* = 111 241 541 ns; and *k_parse* = (",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "241",
  "ctx": "000000002 s ≈ 1000 ns, so *k_pre* = 111 241 541 ns; and *k_parse* = (4587",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "541",
  "ctx": "00002 s ≈ 1000 ns, so *k_pre* = 111 241 541 ns; and *k_parse* = (458737.5",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "458737.509840291",
  "ctx": "pre* = 111 241 541 ns; and *k_parse* = (458737.509840291 − 458736.4081875)·10⁹ + 1000 ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "458736.4081875",
  "ctx": "ns; and *k_parse* = (458737.509840291 − 458736.4081875)·10⁹ + 1000 ns = 1.1016537909",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1.1016537909669094",
  "ctx": "40291 − 458736.4081875)·10⁹ + 1000 ns = 1.1016537909669094·10⁹ ns, i.e. record 0 ended b",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.111",
  "ctx": "094·10⁹ ns, i.e. record 0 ended between 0.111 s and 1.102 s after *m_0*. If",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "1.102",
  "ctx": "i.e. record 0 ended between 0.111 s and 1.102 s after *m_0*. If *k_pre* > *",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "1665",
  "ctx": "ausal rows (two native rows per record; 1665 records give 3330 rows on the",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "3330",
  "ctx": "tive rows per record; 1665 records give 3330 rows on the example capture).",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.05247795879145338",
  "ctx": "exceeded`. On the example capture it is 0.05247795879145338 s.",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757336.5519202",
  "ctx": ", wall origin the Unix epoch): *A_lo* = 1784757336.5519202 s and *A_hi* = 1784757336.553",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757336.5532944",
  "ctx": "lo* = 1784757336.5519202 s and *A_hi* = 1784757336.5532944 s after outward rounding, poi",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757336.5526073",
  "ctx": "er outward rounding, point anchor *A* = 1784757336.5526073 s, and the four terms are",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0006869160344978743",
  "ctx": "    H      = 0.0006869160344978743",
  "offset": 13,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.00044608116149902344",
  "ctx": "    span   = 0.00044608116149902344",
  "offset": 13,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0000010000000000000002",
  "ctx": "    r_max  = 0.0000010000000000000002",
  "offset": 13,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.000001",
  "ctx": "    pad    = 0.000001",
  "offset": 13,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0011349971959968977402",
  "ctx": "    sum    = 0.0011349971959968977402  →  roundup  →  0.00113499719",
  "offset": 13,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0011349971959968978",
  "ctx": ".0011349971959968977402  →  roundup  →  0.0011349971959968978 s",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0011349971959968978",
  "ctx": "so *B_anchor* = 0.0011349971959968978 s (1.135 ms). The sum is exac",
  "offset": 16,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1.135",
  "ctx": "o *B_anchor* = 0.0011349971959968978 s (1.135 ms). The sum is exact in deci",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0006871223449707031",
  "ctx": "lo*)/2 from the printed endpoints gives 0.0006871223449707031 s, 0.0000002063105 s above th",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0000002063105",
  "ctx": "ndpoints gives 0.0006871223449707031 s, 0.0000002063105 s above the exact *H* — less ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1.78",
  "ctx": "binary64 spacing at the epoch magnitude 1.78·10⁹ s, which is 2.4·10⁻⁷ s — ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "2.4",
  "ctx": "he epoch magnitude 1.78·10⁹ s, which is 2.4·10⁻⁷ s — because each endpoin",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1.0000022202281935",
  "ctx": "printed endpoints. Fitted rate window: [1.0000022202281935, 1.0000022646196323], i.e. th",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1.0000022646196323",
  "ctx": "itted rate window: [1.0000022202281935, 1.0000022646196323], i.e. the wall clock ran abo",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "2.2",
  "ctx": "6196323], i.e. the wall clock ran about 2.2 ppm fast against the monotoni",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "197",
  "ctx": "st against the monotonic clock over the 197-second capture; 197 rollovers",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "197",
  "ctx": "onic clock over the 197-second capture; 197 rollovers and 1665 records we",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1665",
  "ctx": "e 197-second capture; 197 rollovers and 1665 records were checked.",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0",
  "ctx": "mple capture the idle GPU channel reads 0.0 W throughout the baseline set",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.0",
  "ctx": "aseline set, so \\(P_{\\mathrm{rest}}\\) = 0.0 W, the MAD is 0, and the floo",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0",
  "ctx": "P_{\\mathrm{rest}}\\) = 0.0 W, the MAD is 0, and the floor engages: σ = 0",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.001",
  "ctx": "he MAD is 0, and the floor engages: σ = 0.001 W.",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "40.6667",
  "ctx": "Example (pulse 0 of the capture): *a* = 40.6667 W, SNR = 40 666.7. All pulse-",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "40",
  "ctx": "of the capture): *a* = 40.6667 W, SNR = 40 666.7. All pulse-0 fit values",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "666.7",
  "ctx": "the capture): *a* = 40.6667 W, SNR = 40 666.7. All pulse-0 fit values quote",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757336.5528765",
  "ctx": "rocessed, under an earlier anchor point 1784757336.5528765 s, about 0.27 ms later than t",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.27",
  "ctx": "nchor point 1784757336.5528765 s, about 0.27 ms later than the current poi",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "2",
  "ctx": "e: pulse 0's on-stamp has *ma* − *mb* = 2.500019036233425e-7 s as execu",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.0000010000000000000002",
  "ctx": "e-7 s as executed in binary64 and *r* = 0.0000010000000000000002 s, so *u_on* = 1.125000951811",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1",
  "ctx": "0.0000010000000000000002 s, so *u_on* = 1.1250009518116714e-6 s. Its re",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.014921970702173189",
  "ctx": "der the earlier anchor noted above) is [0.014921970702173189, 0.017213039063451813] s and ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.017213039063451813",
  "ctx": " noted above) is [0.014921970702173189, 0.017213039063451813] s and its offset region is [",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "−0.012269482911167666",
  "ctx": "9063451813] s and its offset region is [−0.012269482911167666, −0.009886278807582334] s: th",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "−0.009886278807582334",
  "ctx": "ffset region is [−0.012269482911167666, −0.009886278807582334] s: the instrument reported t",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "16",
  "ctx": "ment reported this pulse starting about 16 ms late and ending about 11 m",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "11",
  "ctx": "rting about 16 ms late and ending about 11 ms early, and the model-defin",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "2.3",
  "ctx": "del-defined allowed onset band is about 2.3 ms wide; it is not a physical",
  "offset": 40,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.030067931757111657",
  "ctx": "hor estimator of A.3.3): *B_fiducial* = 0.030067931757111657 s, of which *B_anchor* = 0.00",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0011349971959968978",
  "ctx": "67931757111657 s, of which *B_anchor* = 0.0011349971959968978 s and the difference between ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.0289329345611147592",
  "ctx": "rence between the two printed bounds is 0.0289329345611147592 s (28.9 ms). That difference ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "28.9",
  "ctx": "nted bounds is 0.0289329345611147592 s (28.9 ms). That difference is what ",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757381.2856488",
  "ctx": "(1784757381.2856488, 458782.19098725, 458782.1909",
  "offset": 1,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "458782.19098725",
  "ctx": "(1784757381.2856488, 458782.19098725, 458782.190989791) s;",
  "offset": 21,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "458782.190989791",
  "ctx": "(1784757381.2856488, 458782.19098725, 458782.190989791) s;",
  "offset": 38,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757382.293089",
  "ctx": "its off command has (1784757382.293089, 458783.198425958,",
  "offset": 21,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "458783.198425958",
  "ctx": "its off command has (1784757382.293089, 458783.198425958,",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "458783.198426833",
  "ctx": "458783.198426833) s. Both resolutions are the ",
  "offset": 0,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757336",
  "ctx": "The native record-0 label is 1784757336 s and q₀=0, giving the numeri",
  "offset": 29,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757335.99975",
  "ctx": "1784757335.99975 ≤ A ≤ 1784757337.00025 s. Rec",
  "offset": 0,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "1784757337.00025",
  "ctx": "1784757335.99975 ≤ A ≤ 1784757337.00025 s. Record 1 has",
  "offset": 23,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.118530666",
  "ctx": "q₁=0.118530666 s and the same label, giving",
  "offset": 3,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757335.99975",
  "ctx": "1784757335.99975 ≤ A+β(0.118530666) ≤ 17847573",
  "offset": 0,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.118530666",
  "ctx": "1784757335.99975 ≤ A+β(0.118530666) ≤ 1784757337.00025 s.",
  "offset": 23,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757337.00025",
  "ctx": "1784757335.99975 ≤ A+β(0.118530666) ≤ 1784757337.00025 s.",
  "offset": 38,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "0.111241541",
  "ctx": "its causal constants are k_pre=0.111241541 s and",
  "offset": 31,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "1.1016537909669094",
  "ctx": "k_parse=1.1016537909669094 s. All 1665 native labels and",
  "offset": 8,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "1665",
  "ctx": "k_parse=1.1016537909669094 s. All 1665 native labels and elapsed cou",
  "offset": 34,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "1784757336.5526073",
  "ctx": "Table A3 uses the current point anchor 1784757336.5526073 s and \\(P_{\\mathrm{rest}}=0\\)",
  "offset": 39,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0",
  "ctx": "57336.5526073 s and \\(P_{\\mathrm{rest}}=0\\) W,",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.001",
  "ctx": "σ=0.001 W, pulse height a=42.5514 W. ",
  "offset": 2,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "42.5514",
  "ctx": "σ=0.001 W, pulse height a=42.5514 W. Every local record is show",
  "offset": 26,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "+0.027",
  "ctx": "shifts (+0.027,−0.007) s. Display columns ar",
  "offset": 8,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "−0.007",
  "ctx": "shifts (+0.027,−0.007) s. Display columns are round",
  "offset": 15,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "42.5514",
  "ctx": "ng a record’s overlap fraction f into ŷ=42.5514 f",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "0.001",
  "ctx": "then x=(y−ŷ)/0.001 gives its displayed Huber con",
  "offset": 13,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "13724.280240837228",
  "ctx": "Loss*=13724.280240837228; the no-pulse loss is 478338.",
  "offset": 6,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "478338.47061854997",
  "ctx": "3724.280240837228; the no-pulse loss is 478338.47061854997.",
  "offset": 40,
  "census_status": "UNPOLICED-REGISTERED"
 },
 {
  "literal": "239169.23530927498",
  "ctx": "Thus Loss*<239169.23530927498 passes the half-flat-loss che",
  "offset": 11,
  "census_status": "UNPOLICED-UNREGISTERED"
 },
 {
  "literal": "14410.494252879089",
  "ctx": "Λ=Loss*+0.05 Loss*=14410.494252879089.",
  "offset": 19,
  "census_status": "UNPOLICED-REGISTERED"
 }
]

CENSUS_PROVENANCE = {
 "census": "docs/process_traces/2026-09-27-activation-d528efb2/62-paper-number-census/results_bearing_unpoliced.tsv",
 "census_sha256": "a9cfc5b2f80b8dcc7924fb73d12ed12fd96a910a06ebda1dd9f7db136b611e66",
 "rule": "every census row whose literal no group slot claims; ctx is the census context string; offset is the literal's offset in ctx"
}

def generate_inventory() -> dict:
    return {
        "schema": SCHEMA,
        "status": "Bound, tied and classed slots are checked; unresolved numeric literals are count-ratcheted.",
        "skeleton": "docs/paper/draft-v2-skeleton.md",
        "skeleton_sha256_at_authoring": "56a008525beef55e6d922b458a37b8cd8f8a0cbe30ab5cee1650c48d9c1d76a5",
        "registry": "docs/paper/results-fill-registry.md",
        "sources": copy.deepcopy(SOURCES),
        "groups": copy.deepcopy(GROUPS),
        "spelled_out_expected_total": 307,
        "ratchet": {"unbound-results": 155, "unaccounted": 853},
        "unbound_results_provenance": copy.deepcopy(CENSUS_PROVENANCE),
        "unbound_results": copy.deepcopy(UNBOUND_RESULTS),
    }


def render_inventory() -> str:
    return json.dumps(generate_inventory(), indent=1, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="compare bytes without writing")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/paper/number-inventory.json")
    args = parser.parse_args(argv)
    expected = render_inventory().encode("utf-8")
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != expected:
            print("PAPER-NUMBER-INVENTORY GENERATOR: FAIL (run scripts/gen_paper_number_inventory.py)")
            return 1
        print("PAPER-NUMBER-INVENTORY GENERATOR: PASS")
        return 0
    args.output.write_bytes(expected)
    print("PAPER-NUMBER-INVENTORY GENERATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
