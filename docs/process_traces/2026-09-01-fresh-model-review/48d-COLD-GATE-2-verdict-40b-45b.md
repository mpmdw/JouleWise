<!-- Cold Fable gate #2 (fresh Fable subagent, no loop context). Packet: rulings 40b + 45b. Harvested 2026-09-01. -->

# Cold-gate verdict on 40b and 45b

Cold Fable seat, read-only, no loop context. Inputs read: the two draft rulings, reports 40/31/31c/35 and 45/37, the prior cold gate on the dependence stream (32/32b), D-161 (`docs/decision_log.md:188` and the T26 addendum `docs/process_traces/2026-08-27-t26/threat-model-prune/04-MAGISTRATE-RULING.md:8-15`), and the cited code in both worktrees. Bench runs are listed under each packet.

---

## Packet 1 — 40b (D-165 close-out core, `feat/d165-dominance-closeout-core` @ 88e96f60)

### Bench observations

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout` (wt-closeout): `Ran 18 tests in 10.040s` / `OK` — the suite the delta seat could not run is green.
- F1 reproduced concretely (scratchpad probe using the test fixtures): a sidecar mapping with block 0's operands scaled by 0.9, `derived_split` and `result` recomputed so the mapping is self-consistent, paired with the ORIGINAL sidecar bytes →
  `FORGED build accepted: branch= A licensed= True refusal= None`;
  `closeout.replay_sidecar_sha256 == sha256(authentic bytes): True`;
  `closeout.sources.replay_sidecar.canonical_json_sha256 == hash(forged mapping): True`;
  `validator errors on forged pair: []`;
  when the mapping is replaced by `json.loads(bytes)`: `['closeout.sources.replay_sidecar: source-hash mismatch', "…['cell-decode-a']: source result mismatch"]`.
  The close-out record thus carries two digests that authenticate two different artifacts (`joulewise/dominance_closeout.py:1340-1351` hashes bytes; `:1370-1377` hashes the mapping) and nothing ties them together.
- The CLI is NOT exposed: `scripts/build_d165_dominance_closeout.py:197-205,224-237` reads each file once and passes object+bytes from the same read. The defect lives only in the Python API (`build_d165_dominance_closeout` `:52-59`, `validate_d165_closeout` `:1322-1329`).
- Branch state: `main` is not an ancestor of 88e96f60 (5 commits ahead, 7 behind); the rebase blocked in report 35 (`35-terra-fix-31b-closeout.md:20,60-65`) has still not happened.

### Dispositions

| Item | Verdict |
|---|---|
| F1 classification ("EVIDENCE fence, not adversary fence") | **AMEND.** Under D-161's operative test (MISTAKE vs DELIBERATE, T26 ruling `:8-15`), a mismatched object/bytes pair is produced either by a forger (out of the threat model) or by a caller's programming error — the "tool's own bugs" class D-161 explicitly keeps fail-closed. It is a C-mistake, not class A physics/evidence. The conclusion (fix it) stands; the label should not, because "evidence fence" is the phrase that licenses adding guards, and this defect should be cured by REMOVING one channel, not by adding a check. Also record that no paper-facing close-out is exposed at this head (CLI single-source, above) — the exposure is API-only. |
| F1 cure: single-channel bytes-only API | **AGREE — preferred form only.** Decode inside the consumer; delete the mapping parameters. **STRIKE the alternative** ("keyword-only private-prefixed object parameter + new refusal `replay_sidecar_object_bytes_mismatch`"): that is exactly a deliberate-only guard whose only tripper is a test author, i.e. the over-engineering D-161 prunes. Tests that need to mutate a source mutate the dict and re-encode (`tests/test_d165_dominance_closeout.py:111-115` already has `_file_json_bytes`). The seat's own second alternative in report 40 ("or compare decoded objects before validation", `40-luna-delta-closeout.md:191`) keeps the split channel and should be struck for the same reason. **AMEND the API shape:** make all THREE sources bytes-only, including `floor_artifact` — at this head it is mapping-only (`scripts/build_d165_dominance_closeout.py:227` discards `raw`), and the manifest already seals its digest at `joulewise/analysis_manifest_v3.py:3649-3654`; checking it is three lines, uses an existing field, and avoids a second API churn later. |
| F1 severity "blocker" | **AMEND to "must-fix, API soundness; no claim exposure at 88e96f60".** Merge-blocking either way; the label matters because the CLI-built close-outs are sound and the magistrate should not treat this as a licensed-sentence contamination event. |
| F2 (unhashable inputs → `TypeError`) | **AMEND the cure.** Accept the finding, but not "type-guard every set/map element at `:333`, `:1046`, `:1216`" — that spreads three guards for one failure. One `try/except TypeError` around the census/membership computations mapping to a single named refusal (neither branch) is the D-161-shaped cure; one regression per entry path, not per site. |
| F3 (isolated top-level replay-digest test; partial attachment; schema mismatch) | **AGREE.** Cheap, and the mutation table (`40-luna-delta-closeout.md:223`) shows the guard at `dominance_closeout.py:1346-1350` is currently deletable without a failing test. |
| F4 (contract first-use failures; no runnable invocation) | **AGREE.** Ed's writing standard applies; the exact invocation with flags from `scripts/build_d165_dominance_closeout.py:208-218` and the `output_already_exists` refusal (`:251-259`). |
| Round-3 fixer = Sol | **AGREE.** Sol wrote the original (12) and round 1 (31); the split channel was introduced in round 2 by terra (`35-terra-fix-31b-closeout.md:29`, "validator rechecks supplied bytes"). Sol has no sunk cost in the defective shape, and the fix is not bench-sized (two signatures, ~20 test call sites, a helper, contract pass). |
| Delta by Opus 5 | **AGREE**, with one addition: the delta brief must include an API-surface assertion (no mapping parameter remains on the public builder/validator) and the forged-pair probe above re-expressed as "close-out built from bytes X validated against bytes Y". |

### Structural verdict (b)

**RESHAPE.** The three rounds do not share a defect signature: round 1 ended in a correct `NEEDS_RULING` (the brief asked for an operand comparison against a manifest that records no operands — `31-sol-fix-12-closeout.md:127-130`), round 2 implemented ruling 31c faithfully, and the delta found a defect the cure introduced — which is exactly what delta re-audits exist to catch. What DID repeat is the meta-pattern: each brief specified WHAT to check and left the interface SHAPE to the fixer (31c says "the close-out hashes the file bytes it is given", `31c:56-58`, never "bytes are the only channel"), and the fixer chose the additive shape (keep mappings, add bytes) because adding is safer than deleting under a WRITE_SCOPE'd brief. Round 3 should therefore carry the shape as a decision, not a preference: bytes-only for all three sources, the alternative form struck, F2 as one catch, and a `mutate_then_encode` test helper named in the brief. With that, one round closes it; a consult would only re-derive what the bench probe already settled.

### Missed

1. Third source unbound: `floor_artifact` is never checked against `evidence.aggregate_floor_artifact.sha256` (`analysis_manifest_v3.py:3649-3654`). Values are covered indirectly (sidecar `independent` records must equal the floor's, `dominance_closeout.py:1118-1126`, and the sidecar is manifest-bound), so it is not a hole today, but the honest-drift refusal a re-minted floor should produce ("floor is not the one the manifest sealed") currently surfaces as `…independent: source mismatch`. Fold into the single-channel decision.
2. The branch is 7 commits behind `main` and un-rebased since report 35 flagged it; round 3 should land on a rebased head or the delta seat audits stale context.
3. Report 40's residual-risk line (`:230`) is right that producer→finalizer custody is unproven until `D165-SIDECAR-EMIT-01`; the test fixture injects the attachment (`tests/test_d165_dominance_closeout.py:123`). Not a round-3 item, but the paper cannot cite a close-out until that stream lands — worth a kernel-row check.

---

## Packet 2 — 45b (dependence-sensitivity sheet, `feat/2026-09-01-dependence` @ 35716229)

### Bench observations

- Documented R7 command run verbatim from `docs/paper/round7/dependence-sensitivity.md:97` (cwd = worktree): exit 2, `dependence_sensitivity.py: error: --block-deltas is not valid JSON: Expecting value`. A1 is real.
- The extracted argument (`od -c`) is `` `[5.,7.6,5.5,.2,.7,6.8,5.5,3.6,3.9,3.2]` ``. The seat's diagnosis is incomplete: inside single quotes `tr -d '\\140'` is the set {`\`, `1`, `4`, `0`}, so the pipeline strips digits 0/1/4 from the data as well as leaving the backticks. Any cure that removes the backticks by another route while leaving that `tr` would still corrupt the deltas.
- Single-backslash form (`tr -d '\140'`): exit 0, tail `"direction_gate_outcomes_agree": false`. Matches the seat.
- Report 37's V3 (`37-luna-fix-dependence-2.md:70`) shows the fixer ran the WORKING form (JSON-escaped `\\140` = shell `\140`) and transcribed the escaped form into the sheet — the verification was re-typed, not extracted from the document.
- A2 confirmed: `draft-v1.md:292` is `## 7. Discussion and limitations`; `:294` is the Limitation 1 sentence; sheet rows at `:112,:114` anchor 292 while naming 294.
- p-values come from the project's own `joulewise/analysis_engine/distributions.py:166` (`two_sided_student_t_p_value`, incomplete beta via Lentz at `:49-115`); critical values from `student_t_quantile` (`:131`) rounded to 3 dp at `scripts/dependence_sensitivity.py:194`, and the sheet documents that rounding at `:35`.

### Dispositions

| Item | Verdict |
|---|---|
| A1 rated blocker | **AMEND the label, keep the consequence.** It is not a soundness defect (every printed number is right; the delta seat replicated s, ρ̂, V, n_eff and all three t by hand, `45-sol-delta-dep2.md:295-344`). It IS the ruled R7 acceptance unmet — the one command a reader is told to run fails — so it blocks acceptance of the round. Call it "ruled-item-unmet, must-fix" so the process does not treat it as a two-refuter blocker. |
| A1 cure (`\140` + subprocess golden test) | **AMEND.** Two acceptable cures; prefer the second. (i) The seat's: fix the escape and have the golden test execute the command AS EXTRACTED FROM THE SHEET (regex the fenced line out of the doc and run it via `subprocess`), never a re-typed copy — that is the gap that let 37 certify it. (ii) Better: drop the grep/cut/tr pipeline and print the literal list in the command; have the golden test parse EVERY bracketed ten-number list in the sheet and assert each equals `EXAMPLE_BLOCK_DELTAS_J` (the "one list" requirement from cold gate 32 Q4.4 is then enforced by test, not by a fragile shell extraction that has already broken once). |
| A2 | **AGREE** (anchor 294). |
| A3 (bounded document assertions) | **AGREE**, with the bound restated as a rule rather than a list — see structural verdict. |
| B1 (table numbers uncovered) | **AGREE.** Parse the three table rows; compare each cell to the rendered field. |
| B2 (one-way meta-test) | **AGREE.** Mandated row-name set asserted exactly. |
| C1 (print the tail formula) | **AGREE, at that level, with one amendment.** A standard table cannot reproduce a 9-decimal p-value, so "cite a table" fails the replication standard for what the sheet prints; the identity `p = I_x(ν/2, 1/2)`, `x = ν/(ν+t²)` with the three worked x values is the minimum that lets a reader replay them with any library. Amend: name the implementing function (`joulewise/analysis_engine/distributions.py:166`, and `:131` for the quantile behind 2.262/2.776) so the reader knows the sheet and the script use one routine, and gloss `I_x` in plain words as 45b already says. The alternative — demote the p-values to 3 significant figures since `:51` calls them audit values — is coherent but weaker; not recommended. |
| C2, C3 | **AGREE.** |
| Round-3 fixer = terra, delta = Opus | **AGREE** on seats. |

### Structural verdict (b)

**RESHAPE.** Here the signature DOES repeat, and it has now fired three times on one stream: report 26 (golden test pinned the script's own constants, so a doc/script divergence was certified), cold gate 32 prescribed "the sheet is parsed by the test" (`32:31`), round 2 built that for the delta list — and report 45 finds the same class on every surface the brief did not enumerate: the CLI line (A1), the draft anchors (A2/A3), the table cells (B1), and the reverse direction of the meta-test (B2). Each time the fixer implemented exactly the enumerated assertions and reported green; each time the delta seat found the next un-enumerated surface. The producing cause is the brief style, not the fixer: rulings R1–R8 specify document CONTENT cures with per-item tests, so coverage is always one round behind. The consult the doctrine calls for would ask "what rule makes the sheet self-verifying?" — and the answer is already in hand, so spend it as the round-3 brief instead: (1) state the rule "the sheet is the fixture": every fenced command in the sheet is extracted and executed by a test; every number in the sheet, prose and table, is matched to a rendered field; every `draft-v1.md` anchor is resolved against the named sentence; the refusal-row set is asserted two-way; (2) acceptance is a mutation table with zero survivors across those four surfaces, run by the fixer and re-run by the delta seat; (3) the fixer's verification of any documented command is `sed -n 'Np' sheet | bash`, stdout pasted, never re-typed. Bench-sized items (A2, C2, C3, the one-character escape if cure (i) is chosen) may be done by the magistrate before the round so terra's round is test design plus C1.

### Missed

1. The `tr` over-escape corrupts the data (digits 0/1/4 deleted), not just the delimiters — the seat's cure is correct but its diagnosis understates the fragility of a shell-extraction pipeline in a reader-facing sheet; this is the argument for cure (ii).
2. Sheet `:11` cites generator LINE numbers (1859, 2578) despite cold gate 32 Q4.2 ruling "cite the field names, not line numbers"; at 35716229 the `multiplicity` block starts at `generate_configs.py:2576` (2578 is its `alpha` line). Unpinned line numbers in a frozen-doc citation will drift again; drop them or pin them by test.
3. The fixer's V3 in report 37 passed on a command different from the one written into the sheet — a report-vs-artifact divergence the delta seat had to find by execution. Adopt the "extract, don't re-type" rule for every fixer report that cites a documented command, across streams.
4. The sheet prints "critical value 2.262000" (`:79`) — a 3-dp-rounded quantity rendered at 6 dp; harmless, but a reader following `:35` may wonder which precision entered the half-width. One clause.

---

VERDICT-40b: RESHAPE
VERDICT-45b: RESHAPE
