# ROW L10-SACRIFICIAL-FULL-LIFECYCLE — SACRIFICIAL FULL LIFECYCLE (GATING)
Original verdict: NOT-READY (1 blocker / 3 should-fix / 1 nit / coverage 15/18)
Seat: `docs/process_traces/2026-08-15-readiness-council/seat-reports/L10-SACRIFICIAL-FULL-LIFECYCLE-report.md`
Row line in sealed packet: `sitting-packet-FINAL.md:30` — `| L10-SACRIFICIAL-FULL-LIFECYCLE | GATING | NOT_READY | 15/18 | 1 | 3 | 1 | 13 | 5 | 1 |`
Seat report sha (packet §1 index): `c8f2e0530da08faa`

**Assembly note on WHERE evidence lives:** worktree HEAD at assembly = `79a4cd0` on
`impl/r2-s0-mint-resolver` (the brief's `d10881b` is an ancestor of this head; both branch-only).
`main == origin/main == 0099382`; 49 commits on HEAD not on origin/main; merge-base `311d8016`.

---

## L10-B1 — Frozen packs' claim-consumption edge is unbuilt

### (a) Original finding (VERBATIM)
> ### L10-SACRIFICIAL-FULL-LIFECYCLE B1: Frozen packs' claim-consumption edge is unbuilt: analyze-claims refuses the packs' v3.prospective manifests, the U7-designed prospective builder/validator do not exist, and the final-v3 wire is hard-pinned to splitwise
> at: joulewise/analysis_engine/inputs.py:556-568; joulewise/analysis_manifest_v3.py:613,630-663; configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json:2
> scenario: The funded gamma window collects clean, the verdict passes, alpha/beta floors mint into the aggregate — and the contrast claim cannot be consumed: analyze-claims refuses 'unsupported analysis manifest schema_version: joulewise.analysis_manifest.v3.prospective' (executed); validate_analysis_manifest_v3 hard-requires design_id splitwise_decode_cross_model_abba_v1, the splitwise generator path/plan sha, exactly two stages and n=10, so no hand-authored final D-117 manifest can validate either; grep finds zero implementations of the U7-specified build_prospective_analysis_manifest_v3 / validate_prospective_analysis_manifest_v3 and no postcollection-attachment finalizer; no TASK_QUEUE row tracks this edge. The window is spent and its REQUIRED OUTPUT cannot trace through a claim consumer without landing new code post-hoc, colliding with L1 same-session custody discipline.

Citation: `sitting-packet-FINAL.md` §3 heading "L10-SACRIFICIAL-FULL-LIFECYCLE B1" (lines 64-66);
seat report §5 F1 (BLOCKER) and §3 "Claim consumption" transcript entry (a);
refuter verdicts `refuter-outputs/refuter-verdicts.md` — ECF-contract "All four CONFIRMED (L10-B1
consumption edge, …)" with the qualification "L1 custody discipline does not categorically bar
post-collection implementation (but heightened proof burden -> blocker stands)"; ECF-execution
"V2 load_manifest refuses v3.prospective schema verbatim". CONFIRMED by two distinct lenses.

### (b) What changed since 2026-08-15
**The edge EXISTS IN CODE. It does NOT yet reach the frozen packs.** Both halves verified at HEAD.

*The code that landed:*
- **`d54db78`** — "Merge pull request #155 from mpmdw/impl/wo-consumption-edge —
  WO-CONSUMPTION-EDGE: prospective validator, outcome-blind finalizer, finalized-v3 consumption
  edge", 2026-08-16. **WHERE: merged to main** (`git merge-base --is-ancestor d54db78 origin/main`
  → YES). 9 files, **+6162 / -65**: `joulewise/analysis_manifest_v3.py` +3226,
  `joulewise/analysis_engine/inputs.py` +308, `analysis_engine/artifact.py` +190,
  `analysis_engine/__init__.py` +128, `scripts/finalize_analysis_manifest.py` **+87 (new file)**,
  `tests/test_analysis_finalizer.py` +948, `tests/test_analysis_integration.py` +671,
  `tests/test_analysis_manifest_v3.py` +596, `docs/decision_log.md` +73.
  Branch lineage: `05b6b44` (contract adopted) → `0cba93d` (scoped build, NEEDS_SCOPE pause) →
  `189feab`/`aa5d9c0` (family-semantics validation in artifact.py, cross-arm LOO block strata) →
  `fa87666` (fix round 3: two-tier boundary classification) → merged.
- **The U7-named functions now exist**, contradicting the finding's "zero implementations":
  `joulewise/analysis_manifest_v3.py:2777 validate_prospective_analysis_manifest_v3`,
  `:2831 build_prospective_analysis_manifest_v3`, `:1885` the unchecked inner validator,
  `:3722 finalize_prospective_analysis_manifest_v3`, `:4062 validate_finalized_analysis_manifest_v3`,
  all in `__all__` at `:4168-4178`. The finalizer CLI is `scripts/finalize_analysis_manifest.py`.
- **The consumer wire changed:** `joulewise/analysis_engine/inputs.py:593` routes
  `ANALYSIS_MANIFEST_FINALIZED_V3_SCHEMA` (`joulewise.analysis_manifest.v3.finalized`,
  defined `analysis_manifest_v3.py:27`) to `validate_finalized_analysis_manifest_v3`; the
  prospective schema now yields a **registered** refusal at `inputs.py:604` —
  `analysis_manifest_prospective_not_consumable: frozen prospective manifests must pass the
  outcome-blind finalizer` — instead of the seat's `unsupported analysis manifest schema_version`.
- **The splitwise pin is confined, not removed.** `analysis_manifest_v3.py:33` `PLAN_ID =
  "splitwise-decode-v1-m3max-qwen25-1p5b-vs-7b"`, `:48 ROOT_ORDER_SHA256`, `:63` the
  `swdec-contrast-b(NN)-(a1|b1|b2|a2)` regex, `:412` the splitwise generator path, `:585,:713`
  `design_id: splitwise_decode_cross_model_abba_v1` — all still present, but only on the
  *historical* `validate_analysis_manifest_v3` / `build_analysis_manifest_v3` path, which
  `load_manifest` still reaches via the `ANALYSIS_MANIFEST_V3_SCHEMA` branch. The new
  prospective/finalized functions are design-agnostic (they read a `design` block from the
  manifest).
- **A TASK_QUEUE row now tracks the edge** (the finding said none did): `TASK_QUEUE.md:537`
  (generated region) and `:631` — row **A2 `WO-CONSUMPTION-EDGE`**, kernel
  `docs/process/state_kernel.json:3171-3207`.
- Refusal vocabulary registered as a D-078 amendment in the same PR (33 spellings across
  prospective / finalization / consumer tiers) — `docs/decision_log.md` "D-078 amendment —
  2026-08-15: analysis-manifest consumption-edge refusal registry". **Merged to main.**

*What "PARTIAL; READY [AGENT]" means (asked directly by the brief):*
- Kernel/queue status text, `TASK_QUEUE.md:537` and `docs/process/state_kernel.json:3207`
  (`status_note`), VERBATIM: "Code MERGED #155 (d54db78). D-139 rules delivered: Holm m=2 family
  (decode+prefill, alpha=0.05, two-sided) adopted; p256 floor = dedicated artifact (cells already
  frozen, #138). **Remaining before close: the production freeze (rides Phase 2) + the same-head
  production-pack L10 replay**".
- The third acceptance criterion is unmet by its own words:
  `state_kernel.json:3176` — "Analyze-claims accepts only the immutable finalized v3 artifact
  **and the L10 sacrificial rehearsal passes at one head**". No such rehearsal record exists
  (searched `docs/run_reports/`, `docs/process/`, `docs/process_traces/`).
- The row-note "0418bfc" sweep commit explicitly downgraded this row: "T9 sweep applied (11
  findings): work-selection truth (**consumption-edge + detect-pulses → partial, not READY**)".
- Scientific dependencies were cleared by **D-139 A2** (`docs/decision_log.md:10063` ff, merged to
  main): Holm α=0.05, m=2 (decode + prefill_p256), two-sided, frozen cross-arm block-strata
  mapping "(mechanism merged in #155)"; dedicated p256 floor artifact; the
  `analysis_manifest_transport_ruling_pending` branch "remains permanently refusing (dormant), as
  designed."

*Consult custody:* `docs/process_traces/2026-08-15-consumption-edge-consult/` contains exactly two
files — `consult-prompt.md` and `consult.md` (no README, no verdict file). Merged to main.

*EXECUTED by this assembler at HEAD (read-only, in-process):*
```
validate_prospective_analysis_manifest_v3(
    json(configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/analysis_manifest_v3.json),
    manifest_dir=…, plan_tree_path=…/plan_tree.json)
→ 4 refusals
  analysis_prospective_schema_invalid  : manifest: missing key(s): design, families,
      finalization_contract, freeze_status, frozen_semantics_sha256, manifest_id, replacement_policy
  analysis_prospective_unknown_key     : manifest: unrecognized key(s): draft_status,
      postcollection_attachments
  analysis_prospective_unresolved_slot : manifest contains an EMPTY/TODO placeholder
  analysis_prospective_not_frozen      : manifest.freeze_status must be 'frozen'
```
Identical 4 refusals on the `_v1` pack. `grep -rl frozen_semantics_sha256 configs/ tests/ docs/`
→ only `tests/test_analysis_manifest_v3.py` and
`docs/process_traces/2026-08-15-consumption-edge-consult/consult.md`. **No committed pack manifest
carries the schema the shipped validator requires**, including the `_v3` family frozen in this very
transaction.

*The `_v3` pack family (asked directly by the brief — did the successor family change the
schema_version or the splitwise pin?):* **NO to both.** All three
`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v{1,2,3}/analysis_manifest_v3.json` still declare
`schema_version: joulewise.analysis_manifest.v3.prospective` and carry `design_id: None` (there is
no design_id key). `diff` of the v1 vs v3 manifests shows **only** identity/sha churn:
`draft_status` `unfrozen_draft` → `as_generated_pre_d134_freeze`, `plan_id …-v1` → `…-v3`,
`evidence_root_id …-v1` → `…-v3`, and every `manifest_sha256` / `config_sha256`. Top-level keys
unchanged: `['schema_version','draft_status','plan','evidence_root_id','root_order_manifest',
'stage_manifests','condition_families','contrasts','postcollection_attachments']` — **no `families`
block**, which D-139 A2 says must "enter the gamma prospective manifest's families block at the
production freeze."
Freeze-0003 receipts DO exist in the `_v3` packs
(`configs/campaigns/d117_*_v3/arm_readiness.freeze.receipts/freeze-0003.json` + `.sha256`), minted
by `5e38f1e` (1p5b_v3), `eb7f6c6` (7b_v3), `94dc3b3` (contrast_v3), table filled by `8b2b021` —
**all four branch-only** (`on-main=NO`, `on-HEAD=YES`).

*Runbook wiring:* `grep -n "finalize_analysis_manifest\|analyze-claims" docs/phase_2/window_runbook.md`
→ **zero hits.** The finalizer has no operator step. `grep -n "prospective\|finaliz\|analysis_manifest"
docs/process/phase2-transaction-runsheet.md` → **zero hits.** The Phase-2 transaction runsheet
(steps 1-8, lines 54-112) schedules merges, `_v2` generation, D-079 reissue, registry install,
freeze, Ed confirmation, post-publication — **nothing about the analysis manifests.**

### (c) Candidate disposition for the seat
**STILL-OPEN (major code repair merged; terminal edge still does not reach the frozen packs).**
The seat is adjudicating whether a merged, tested, design-agnostic prospective→finalized→consumer
lifecycle discharges a blocker whose scenario was "the window is spent and its REQUIRED OUTPUT
cannot trace through a claim consumer" — when all three production pack manifests are refused by
that very validator on four counts, no producer converts them, and no runsheet/runbook/queue step
schedules the conversion.

### (d) Skeptical probes
1. Reproduce the 4 refusals against `d117_contrast_qwen25_1p5b_vs_7b_v3`, then ask the direct
   question: **what artifact, produced by what command, does `finalize_analysis_manifest.py`
   consume tonight?** If the answer is "a manifest that does not exist yet", the blocker's
   scenario is unchanged in substance.
2. `git show 94dc3b3 --stat` — the contrast `_v3` freeze. Ask why a freeze executed *after* #155
   landed (08-16) froze bytes the shipped validator rejects. Either the freeze predates awareness,
   or the conversion is deliberately deferred past freeze — in which case D-140's "all pack bytes
   are immutable after mint" (runsheet step 5) has to be reconciled.
3. `state_kernel.json:3176` names "the L10 sacrificial rehearsal passes at one head" as acceptance.
   Demand that rehearsal's transcript. Assembler found no record of it anywhere in
   `docs/run_reports/`, `docs/process/`, or `docs/process_traces/`.
4. Check whether `load_manifest`'s historical `ANALYSIS_MANIFEST_V3_SCHEMA` branch (splitwise-pinned)
   is still reachable, and whether a D-117 artifact could land on it. The finding's "no hand-authored
   final D-117 manifest can validate either" clause was never refuted — it was routed around.
5. The refuter qualification is on the record: "L1 custody discipline does not categorically bar
   post-collection implementation (but heightened proof burden → blocker stands)". Ask what the
   heightened proof is, now that the remaining work (manifest conversion) is *still* scheduled
   post-freeze and arguably post-collection.
6. `grep -c "" joulewise/analysis_manifest_v3.py` — the module gained 3226 lines. Ask which
   independent lens has audited it. `refuter-outputs/` predates it entirely.

---

## L10-SF-1 — Runbook §11 extraction command as frozen refuses at argparse

### (a) Original finding (VERBATIM)
> - [should_fix] [L10] Runbook §11 extraction command as frozen refuses at argparse: --evaluation-basis-sha256 without the co-required --consumption-semantics-id

Citation: `sitting-packet-FINAL.md` §4 line 148. Full text, seat report §5 F2 (VERBATIM):
> - **F2 (SHOULD-FIX).** Runbook §11 extraction command refuses as frozen (missing `--consumption-semantics-id`). `docs/phase_2/window_runbook.md:1485-1491` vs `scripts/extract_detection_floors.py:100-106`.

Executed at the sitting, seat report §3: "**Extraction (frozen spec).** Exact §11 runbook form (no
`--consumption-semantics-id`) → argparse exit 2 (**finding F2**; refusal itself is correct CLI
hygiene)."

### (b) What changed since 2026-08-15
**NO-REPAIR-FOUND.** Verified at HEAD `79a4cd0`:
- The runbook command is unchanged in substance, only relocated by the +505-line runbook growth.
  `docs/phase_2/window_runbook.md:1766-1771`:
  ```sh
  .venv/bin/python scripts/extract_detection_floors.py \
    --runs-root "$RUNS_ROOT" \
    --spec "$WINDOW_PLAN_ROOT/extraction_spec.json" \
    --out "$WINDOW_CUSTODY_ROOT/detection-floor-extraction.json" \
    --evaluation-basis-sha256 "$WHOLE_WINDOW_BASIS_SHA256" \
    --hash-bundles
  ```
  `--consumption-semantics-id` is **still absent.**
- The co-requirement is still enforced: `scripts/extract_detection_floors.py:100-106` —
  `if (args.evaluation_basis_sha256 is None) != (args.consumption_semantics_id is None):
  parser.error("--evaluation-basis-sha256 and --consumption-semantics-id are required together")`.
  So the frozen command still exits 2 at argparse.
- The only other `--consumption-semantics-id` occurrence in the runbook is at **line 1537**, in the
  §9/§10 salvage-dangler dispatch (`salvage_dangler_exclusion_v1`) — a different command.
- **The "runsheet + runbook corrections" commit the brief points at does NOT contain this fix.**
  `de6ccd7` ("Merge-gate docs batch: D-140/D-141, residual registration, consult amendments,
  runsheet + runbook corrections (magistrate-drafted)", 2026-08-18, **merged to main**) touches
  `docs/phase_2/window_runbook.md` by only **10 lines (+6/-4)**: (i) `RUNS_ROOT` /
  `BOUND_RUNS_ROOT` flipped from `…_v1` to `…_v2`, (ii) a freeze-receipt numbering paragraph
  (`freeze-000<N>` + `--predecessor-pack-root`). Nothing in §11.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating a one-token documentation defect that was found by
execution, ratified into the should-fix batch (`council-verdict.md` Phase 1), survived a
magistrate-drafted runbook correction pass on 2026-08-18, and still guarantees an argparse exit 2
at the exact frozen close-out step.

### (d) Skeptical probes
1. `sed -n '1766,1772p' docs/phase_2/window_runbook.md` and `sed -n '99,107p' scripts/extract_detection_floors.py`
   — confirm the mismatch yourself in two commands.
2. Ask which semantics id the runbook *should* name for a normal (non-salvage) window. The seat had
   to guess `d078_minted_envelopes_v1` in its rehearsal (§3). If the runbook cannot say, the defect
   is not purely editorial.
3. `git log --oneline --since=2026-08-15 -- docs/phase_2/window_runbook.md` — enumerate every
   runbook commit since the council and ask why a known, executed, one-line defect at the
   claim-bearing step survived all of them.
4. Note the compounding: `--spec "$WINDOW_PLAN_ROOT/extraction_spec.json"` while §11's recorder
   step says "`PACK_ROOT` is the frozen campaign pack containing `plan_tree.json`;
   `WINDOW_PLAN_ROOT` is not a valid substitute" (line 1745). Ask whether the extraction spec
   really lives under `WINDOW_PLAN_ROOT`, or whether that is a second frozen-command defect.

---

## L10-SF-2 — Runbook §11 margins-recorder identity mismatch

### (a) Original finding (VERBATIM)
> - [should_fix] [L10] Runbook §11 margins-recorder identity mismatch: --pack-identity "$WINDOW_ID" (window_a9_YYYYMMDD convention per §4) can never satisfy the recorder's plan-derived window_id requirement

Citation: `sitting-packet-FINAL.md` §4 line 149. Full text, seat report §5 F3 (VERBATIM):
> - **F3 (SHOULD-FIX).** Runbook §11 margins-recorder `--pack-identity "$WINDOW_ID"` can never satisfy the recorder's plan-derived `window_id` requirement (`joulewise/window_duration_margins.py:374-379`); all three packs' true identities are `plan-d117-…-v1`, not the §4 `window_a9_YYYYMMDD` convention.

Executed at the sitting, seat report §3: "`--pack-identity` with runbook `$WINDOW_ID` convention
and with the pack dirname → both `{"reason": "pack_identity_invalid", "status": "REFUSE"}`; with the
true plan-derived `plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1` → advanced to `member_missing`."

### (b) What changed since 2026-08-15
**REPAIRED — by the §4 variable definition, not by the §11 command.**
- The §11 command text at `docs/phase_2/window_runbook.md:1737-1742` is **unchanged**; it still
  reads `--pack-identity "$WINDOW_ID"`.
- What changed is what `$WINDOW_ID` *means*. `docs/phase_2/window_runbook.md:190` (the frozen
  `window.env` example, §4) now reads
  `WINDOW_ID=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v2` — a **plan-derived**
  identity that satisfies the recorder.
- Provenance, via `git log -L 190,190:docs/phase_2/window_runbook.md`:
  - **`a61ac92`** — "WO-T0-PRODUCER: T-0 acquisition capture tool + R2 resolver + D-127 clock route
    + dwell/env hardening (#152)", 2026-08-15. **WHERE: merged to main.** This is the commit that
    replaced `WINDOW_ID=window_a9_YYYYMMDD` (and `BRACKET_SESSION_ID`, `FROZEN_PLAN`, `PACK_ROOT`)
    with `WINDOW_ID=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1`. It cures F3 as a
    side effect of the R2 FROZEN_PLAN identity ruling, not as an F3 fix.
  - **`844453a`** — "Bookkeeping follow-ups: … window.env example flipped whole to the _v2 family
    with real generated identities …", 2026-08-18. **WHERE: merged to main.** Moved the example
    from `…-v1` to `…-v2`.
- The recorder requirement the finding cited is unchanged and still binding — current head
  `joulewise/window_duration_margins.py:358` (`_PACK_ID_RE` namespace-safety) and `:382-388`
  (`plan.get("plan_id") != pack_identity or window_identity.get("window_id") != pack_identity` →
  `_refuse("pack_identity_invalid", "operator pack identity is not pack-derived")`).
- **RESIDUAL — a new mismatch of the same shape.** The runbook example names the **`_v2`** family;
  the family actually frozen in this transaction is **`_v3`** (freeze-0003, branch-only). `grep -n
  "_v3\|freeze-0003" docs/phase_2/window_runbook.md` → **zero hits.** Every `window.env` value in
  §4 (`WINDOW_ID`, `FROZEN_PLAN`, `PACK_ROOT`, `PACK_ID`, `PLAN_ID`, `EVIDENCE_ROOT_ID`,
  `RUNS_ROOT`, `BOUND_RUNS_ROOT`) points at `_v2`. Assembler confirmed the true `_v3` identity by
  reading the pack: `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3`, and the recorder
  accepts it (executed: `_pack_inventory` OK, 3 cells).

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED, WITH A REGENERATED RESIDUAL.** The seat is adjudicating whether the F3
defect class is cured (the convention flipped to plan-derived, main-merged) or merely re-instantiated
one generation later — the frozen operator document names `_v2` identities while the frozen packs
are `_v3`, so a tired operator copying §4 verbatim still hits `pack_identity_invalid`.

### (d) Skeptical probes
1. `grep -n "_v2\|_v3" docs/phase_2/window_runbook.md | head -20` — count how many `_v2` bindings
   the operator document carries and whether *any* `_v3` binding exists. Assembler found zero `_v3`.
2. Read the true `_v3` plan ids out of the packs
   (`python3 -c "import json;print(json.load(open('configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json'))['plan']['plan_id'])"`)
   and diff them against every §4 value.
3. The runsheet is also written for `_v2` / `freeze-0002`
   (`docs/process/phase2-transaction-runsheet.md:64-88`) while the executed transaction produced
   `_v3` / `freeze-0003`. Ask whether the runsheet is stale or the transaction deviated, and which
   document an operator is meant to obey.
4. Ask whether the F3 cure was ever *tested*: is there a regression that runs the runbook's §4
   values against `_pack_inventory`? A documentation value with no test regenerates exactly this
   defect at every family bump — it just did.

---

## L10-SF-3 — L1 same-custody-session limitation vs the three-window design; FLOOR-BIND-01 unclosed

### (a) Original finding (VERBATIM)
> - [should_fix] [L10] L1 same-custody-session limitation structurally conflicts with the three-window design's cross-session floor consumption; FLOOR-BIND-01 is READY but unclosed

Citation: `sitting-packet-FINAL.md` §4 line 150. Full text, seat report §5 F4 (VERBATIM):
> - **F4 (SHOULD-FIX).** L1 (extraction and floor-consuming analysis in one custody session; TASK_QUEUE FLOOR-BIND-01 fence, READY not closed) structurally conflicts with gamma's consumption of alpha/beta floors minted in earlier sessions. Needs FLOOR-BIND-01 closure or a prospective ruling **before** the windows.

Seat verdict §6: "It is NOT-READY because … the L1/cross-window contradiction is **unruled** (F4)."

### (b) What changed since 2026-08-15
**NO-REPAIR-FOUND. FLOOR-BIND-01 is still open, and no prospective ruling was found.**
- `TASK_QUEUE.md:542` (generated region) — row **A10 `FLOOR-BIND-01` | P1 Phase Gate | READY
  [AGENT]**. Duplicated at `:636` as `READY`. Kernel entry
  `docs/process/state_kernel.json:1237-1268`. Status text unchanged from the sitting: "Minted
  2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until
  closed."
- The fence text is still live, VERBATIM from `TASK_QUEUE.md:542`: "Fence: Until this row closes,
  claim-bearing analysis may consume floor artifacts only from **same-custody-session** governed
  extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1)."
- Authority is unchanged: `docs/decision_log.md:4540` ("produced by the governed extraction in the
  same custody session as the …") and `:4554` (registered limitation L1 / FLOOR-BIND-01). No newer
  decision-log entry touching cross-session floor consumption was found — `grep -n
  "same-custody\|same custody session\|cross-session floor\|FLOOR-BIND" docs/decision_log.md`
  returns only those two pre-existing lines.
- **Partial, indirect mitigation only.** The #155 finalizer added
  `analysis_finalization_floor_dependency_unsatisfied` and an `aggregate_floor_artifact` /
  `floor_dependency` binding (`joulewise/analysis_manifest_v3.py:1058,1096,1129,1163,1618,1788,2391-2408`)
  — the finalizer authenticates "aggregate floor lineage" per the A2 acceptance text. That is a
  *mechanical lineage check*, not a ruling that cross-session consumption is admissible. The L1
  fence is a claim-admissibility rule; nothing found retires or waives it.
- The three-window design remains cross-session by construction: alpha and beta floors mint on their
  own nights, gamma consumes them later (`RUN_STATE.md:2190,2296` both cite the FLOOR-BIND-01 fence
  as still governing).

### (c) Candidate disposition for the seat
**STILL-OPEN (unruled, exactly as the seat left it).** The seat is adjudicating whether the
three-window claim path can be graded READY while the standing L1 fence says gamma's consumption of
alpha/beta floors is non-claim-bearing, with FLOOR-BIND-01 still `READY [AGENT]` and no prospective
ruling on the record.

### (d) Skeptical probes
1. `grep -n "FLOOR-BIND-01" TASK_QUEUE.md docs/process/state_kernel.json` — confirm the row is
   still open, then ask the direct question: **on the night gamma is consumed, is the claim
   admissible under L1 or not?** A yes requires either FLOOR-BIND-01 closed or a ruling; assembler
   found neither.
2. Ask whether the #155 `floor_dependency` / `aggregate_floor_artifact` machinery was *intended* to
   discharge L1. If it was, there should be a decision-log clause saying so — search for one. If it
   was not, the mechanism is orthogonal and the fence is untouched.
3. FLOOR-BIND-01's own acceptance names three evidence items (floor cells bound to extraction report
   + source-member disposition; refusal on width/corner/membership deviation; integration
   regressions rejecting width substitution and member omission). Ask which, if any, #155 delivers.
4. The row is `READY [AGENT]` — i.e. an agent could do it now. Ask why a launch-gating structural
   contradiction is queued behind the sitting rather than closed before it.

---

## L10-NIT-1 — backup_runs.sh bundle miscount

### (a) Original finding (VERBATIM)
> - [nit] [L10] backup_runs.sh counts campaign_manifests/ as a bundle in operator-facing output (reported 5 bundles for a 4-member window)

Citation: `sitting-packet-FINAL.md` §4 line 151. Full text, seat report §5 F5 (VERBATIM):
> - **F5 (NIT).** `backup_runs.sh:25-36` counts `campaign_manifests/` as a bundle (reported 5 for a 4-member window) — operator-facing miscount vs §12's count-by-bundle-ID rule.

### (b) What changed since 2026-08-15
**NO-REPAIR-FOUND.**
- `git log --oneline -- scripts/backup_runs.sh` → **one commit in the file's entire history**:
  `5b12332` "P0-002: measurement-corpus backup script (R-016, playbook M2)". Untouched since.
- The defect is verbatim present at `scripts/backup_runs.sh:25-35`:
  `find "$RUNS_DIR" -mindepth 1 -maxdepth 1 -type d ! -name experiments -print` — every top-level
  directory except `experiments` counts as a bundle, so `campaign_manifests/` (and
  `instrument_validation/`, which the whole-window verdict requires under `RUNS_ROOT`) inflate the
  count.
- The count is written into the operator-facing log line (`:38-41`,
  `printf … bundle_count=%s … >> "$DEST/backup.log"`), so the miscount is durable in custody, not
  just on screen.
- The §12 rule it contradicts is still in force: `docs/phase_2/window_runbook.md:1832` — "member
  counts by distinct bundle ID, never by campaign-log line."

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating a nit that persists at HEAD and writes a wrong number
into a custody log the close-out record cites.

### (d) Skeptical probes
1. `sed -n '25,41p' scripts/backup_runs.sh` — read the `find` and the `append_log` printf.
2. Note the escalation the seat did not: `instrument_validation/` is *required* to sit under
   `RUNS_ROOT` (seat report §3, whole-window verdict condition list). So a real window inflates by
   at least two, not one. Ask whether the recorded `bundle_count` is ever used as a check.
3. `grep -n "bundle_count\|backup.log" docs/phase_2/window_runbook.md` — ask whether §12 tells the
   operator to reconcile this number against the true bundle-ID count, or to record it as-is.

---

## L10-COVERAGE — 15/18 examined-and-executed

### (a) Original finding (VERBATIM)
Seat report §2 (VERBATIM):
> **15 / 18 examined-and-executed.** Unexecuted obligations, plainly: #7 salvage dispatch (no synthetic salvage closure authorable without defeating its own authentication — correct), #8 supersession recording, #13 v2 aggregate CLI mint (suite-covered only), #18 waiver path; the CLI-level PASSED-basis chain is impossible from a sandbox (→ ED-QUALIFICATION ED-L10-1). Item 15 examined statically + by executed consumer refusal.

Post-verdict adjudication: `council-verdict.md` VERDICT §2 — "**The work-order program is NOT
CERTIFIED COMPLETE** … every seat's evidence universe was self-nominated, and the one denominator
adversarially tested fell … the READY-candidate re-audit must re-enumerate every universe
independently and run the adversarial coverage attack as a standing packet element."

### (b) What changed since 2026-08-15
- **The council-ordered adversarial coverage re-enumeration has NOT been run.** It remains Phase 3:
  `council-verdict.md` "**Phase 3:** baseline-manifest SUPERSESSION … + adversarial coverage
  re-enumeration of all universes"; still forward-looking at
  `docs/process/phase2-transaction-runsheet.md:115` and `RUN_STATE.md:450,604`.
- **The denominator is materially stale.** `git diff --stat 8937dec..HEAD` over L10-scope files
  (`scripts/run_campaign.py`, `scripts/backup_runs.sh`, `scripts/extract_detection_floors.py`,
  `scripts/mint_floor_artifact_generalized.py`, `joulewise/analysis_engine/`,
  `joulewise/analysis_manifest_v3.py`, `joulewise/window_duration_margins.py`,
  `docs/phase_2/window_runbook.md`) = **9 files, +4579 / -206**, of which
  `analysis_manifest_v3.py` +3226 (item 15's wire, wholly rewritten), `analysis_engine/inputs.py`
  +403 (item 14), `run_campaign.py` +158 (items 1, 5, 6, 7, 8), runbook +505 (item 17). Adding
  `configs/campaigns/` (items 11, 12, 15's pack side) brings the L10+L4 combined scope drift to
  **900 files / 134,721 insertions.**
- **New universe members exist that were never in the 18:** `scripts/finalize_analysis_manifest.py`
  (new, the finalizer CLI — arguably the single most consumption-critical item for this seat),
  `scripts/capture_t0_step.py` (PR #152), the `_v2` and `_v3` pack families with their
  `freeze-0002`/`freeze-0003` receipts, and three new test modules
  (`tests/test_analysis_finalizer.py`, `tests/test_analysis_manifest_v3.py`, and the +671 growth of
  `tests/test_analysis_integration.py`).
- **Charter final-head invalidation applies:** `docs/process/instrument-readiness-audit-charter.md:79-91`
  — "final-head invalidation — any repo change after the baseline manifest voids affected lens
  results." The 442-test pass-path proof in seat report §3 was executed at `8937dec`.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating a self-nominated 18-item denominator, never adversarially
attacked, over a scope whose central item (the claim-consumption wire) has been entirely rebuilt
since — with the ordered re-enumeration unexecuted and the baseline manifest not superseded.

### (d) Skeptical probes
1. Run the standing adversarial coverage attack: independently enumerate the L10 universe at HEAD.
   Predict at minimum `scripts/finalize_analysis_manifest.py`, the three `_v3` freeze receipts, and
   the launch-binding downstream reauthentication gates from `b9c7d0a` (which added gates to
   "analysis admission, NEG-8 bound, whole-window verdict, extraction, mint" — five of L10's items).
2. Ask which of the seat's 442 executed tests were re-run at HEAD. None is recorded in this packet.
3. `docs/process/audit-baseline-manifest.json:20` at HEAD still reads
   `"head_commit": "ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b"` (assembler-verified) — the Phase-3
   supersession has not happened. Ask what document binds this sitting's baseline.
4. The seat's own §2 declares item 15 "examined statically + by executed consumer refusal." That
   consumer refusal is now a *different* refusal (`analysis_manifest_prospective_not_consumable`).
   Ask whether item 15 has any current examination at all.

---

## L10-UNEXECUTED — the four CLI-level obligations and ED-L10-1

### (a) Original findings (VERBATIM)
`sitting-packet-FINAL.md` §6, lines 235-239:
> - [L10] §9 D-100 salvage-dangler verdict dispatch (--consumption-semantics-id salvage_dangler_exclusion_v1 with membership binding + salvage closure) — not exercised at the CLI (no synthetic salvage closure); covered only by suite evidence
> - [L10] §10 --record-supersession quarantine/supersession flow — not exercised at the CLI
> - [L10] v2 multi-cell aggregate mint route (--v2-input-manifest + schema_v2 pinset), the route the gamma consumption depends on — not exercised at the CLI; covered by tests/test_mint_floor_artifact_generalized.py (passed)
> - [L10] Waiver path: --waivers producing a 'flagged' verdict and extraction refusing the flagged basis — not exercised
> - [L10] CLI-level PASSED-basis end-to-end (verdict passed → margins PASS → extraction admitted → mint minted) — impossible from the desk without a real window corpus; see ED-QUALIFICATION row

`sitting-packet-FINAL.md` §5 line 190 (the ED row, VERBATIM):
> - [L10] ED-L10-1 (stable capability, any tap block, no live measurement): one desk replay of the complete post-collection chain against a RETAINED real window corpus (a9/a10 custody, Ed-held off-repo) — whole-window verdict (expect passed), duration-margins recorder, backup, governed extraction with the matching spec and basis sha — pasting every command and exit code. This supplies the CLI-level PASSED-basis positive proof that no sandboxed desk rehearsal can produce, because a passing basis requires real calibration-bracket, NEG-8 corpus, and reference-triplet evidence that only a live sudo/powermetrics window can mint.

Charter constraint: `docs/process/instrument-readiness-audit-charter.md:70-78` — ED-QUALIFICATION
rows are performed BEFORE the sitting; "**Only T0 rows may remain open at the sitting.**"
ED-L10-1 is explicitly labelled "stable capability, any tap block, no live measurement".

### (b) What changed since 2026-08-15
- **ED-L10-1: NO CLOSURE RECORD FOUND — the row appears to have lost its identifier.**
  `grep -rn "ED-L10-1" .` outside the council directory returns **zero hits**: it is in no queue,
  no kernel row, no Ed packet, no run report. Its content survives under the informal name
  "a9/a10 desk replay", which is listed as **still ED-OWED**: `RUN_STATE.md:459` and `:546` both
  enumerate it inside "ED-OWED (ONE batched session when Phase 1 nears close)" alongside the
  qualification script; `docs/process/ed-batch-packet.md:57` and
  `docs/process/ed-evening-checklist.md:24` likewise list it as an owed desk item.
- **It was NOT done at Ed's 2026-08-17 qualification evening.** The results table in
  `docs/run_reports/2026-08-18-t10-session.md:99-112` lists D-127 sudoers, sampler lifecycle, rail
  probe, backlight rows, ED-QUAL-L4-1, ED-Q-L9-3 quiet census, and dress rehearsal (**OPEN**) —
  **the a9/a10 desk replay is not in the table at all.** `grep -n "a9"` across that report, the
  morning packet, and `docs/process/ed-s5-mint-decision-2026-08-19.md` produced no closure record.
  `docs/process/ed-morning-packet-2026-08-18.md:126` says "OPEN: the dress rehearsal (item 4) only"
  — which does not mention the desk replay either way.
- **The four CLI-level obligations: NO EXECUTION RECORD FOUND.** Searched `docs/run_reports/`,
  `docs/process/`, `RUN_STATE.md` for `record-supersession`, `v2-input-manifest`,
  `salvage_dangler_exclusion_v1`, and `--waivers` execution evidence. The only
  `salvage_dangler_exclusion_v1` hits are `docs/run_reports/2026-08-01-desk-adjudication-session.md:95`
  and `RUN_STATE.md:3369`, both pre-council design references. No CLI transcript for any of the four.
- **The v2 multi-cell aggregate mint route — "the route the gamma consumption depends on" — has
  additionally CHANGED since it was declared unexecuted.** `scripts/mint_floor_artifact_generalized.py`
  is +102 lines since baseline, and `joulewise/detection_floor.py` gained `cef3306` "S0 kernel:
  generation-resolved mint policy (D-147 S2/S4); genesis digest rename; schema generation
  conditionals" — **branch-only** on `impl/r2-s0-mint-resolver`, not on main. So the seat's
  suite-only coverage now covers a route that has been modified by unmerged work.
- **The one substitute proof that DID land** is ED-QUAL-L4-1 (decisive replay, `DECISIVE REPLAY: OK`,
  13,180.653 s, 2026-08-17, `docs/run_reports/2026-08-18-t10-session.md:108`;
  `docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:189`). That exercises the
  **mint's** full-fixture equality proof over a downloaded custody-store corpus — it does **not**
  supply the verdict→margins→backup→extraction CLI chain over a retained real window corpus that
  ED-L10-1 names.
- **A2's own acceptance still names the missing rehearsal:** `state_kernel.json:3176` — "the L10
  sacrificial rehearsal passes at one head"; `TASK_QUEUE.md:537` — "Remaining before close: the
  production freeze (rides Phase 2) + the **same-head production-pack L10 replay**."

### (c) Candidate disposition for the seat
**ED-ROW — STILL-OPEN, AND THE IDENTIFIER HAS GONE MISSING.** The seat is adjudicating whether a
sitting can proceed with a stable (non-T0) ED-QUALIFICATION row unclosed, when that row's ID appears
nowhere in the tracking system and its content is carried only as informal prose in three ED-OWED
lists — and when four CLI-level lifecycle obligations, including the aggregate mint route gamma
depends on, still have no CLI transcript.

### (d) Skeptical probes
1. `grep -rn "ED-L10-1" . --exclude-dir=.git` — verify the assembler's claim that it exists only in
   the council directory. A gating seat's ED row that no queue tracks is exactly the "silently
   skipped" outcome the seat wrote the row to prevent.
2. Ask directly: **has the a9/a10 desk replay been executed?** If yes, demand the pasted commands
   and exit codes the row requires. If no, ask how the charter's "only T0 rows may remain open"
   clause is satisfied.
3. Ask whether ED-QUAL-L4-1 is being treated as a substitute. It is not one: different corpus
   (release download vs retained a9/a10 custody), different chain (mint fixtures vs
   verdict→margins→backup→extraction), different proof (exact-equality vs PASSED-basis).
4. Ask for the four CLI transcripts (§9 salvage dispatch, §10 supersession, v2 aggregate mint,
   waiver→flagged). The seat classified 14 refusal events; none of these four was among them.
5. `cef3306` is branch-only and rewrites mint policy resolution. Ask whether the v2 aggregate mint
   route's suite coverage was re-run on the branch, and whether merging it invalidates the
   already-thin coverage of the route gamma depends on.
6. Ask whether the L10 rehearsal itself will be re-run at the READY-candidate head. A sacrificial
   lifecycle seat whose rehearsal predates a 3226-line rewrite of the terminal edge has rehearsed a
   different instrument.

---

## ROW-LEVEL OPEN ITEMS
- **L10-B1's terminal edge still does not reach the frozen packs.** Code merged to main (#155,
  `d54db78`), but all three committed `analysis_manifest_v3.json` files — `_v1`, `_v2`, and the
  `_v3` family frozen in this transaction — produce **4 refusals** from the shipped
  `validate_prospective_analysis_manifest_v3`, and none carries the `families` block D-139 A2
  requires. No producer converts them.
- **Nothing schedules the conversion.** `docs/process/phase2-transaction-runsheet.md` has zero hits
  for `prospective` / `finaliz` / `analysis_manifest`; `docs/phase_2/window_runbook.md` has zero
  hits for `finalize_analysis_manifest` / `analyze-claims`. The finalizer has no operator step and
  no transaction step.
- **The A2 acceptance criterion "the L10 sacrificial rehearsal passes at one head" is unmet and
  untracked** — no rehearsal transcript found anywhere.
- **L10-SF-1 (runbook §11 extraction argparse): NO REPAIR.** Still `--evaluation-basis-sha256`
  without `--consumption-semantics-id` at `window_runbook.md:1766-1771` vs the co-requirement at
  `extract_detection_floors.py:100-106`. The 2026-08-18 magistrate runbook correction pass
  (`de6ccd7`, +6/-4) did not touch §11.
- **L10-SF-2 cured, then regenerated one generation later.** `$WINDOW_ID` is now plan-derived
  (`a61ac92`, main) — but every §4 value names the **`_v2`** family while the frozen packs are
  **`_v3`**; the runbook contains zero `_v3` references. The cure has no regression test, which is
  why it regenerated.
- **L10-SF-3 (L1 vs cross-session floors): NO REPAIR, NO RULING.** FLOOR-BIND-01 is still
  `READY [AGENT]` (`TASK_QUEUE.md:542`, `state_kernel.json:1237`); no decision-log entry rules on
  cross-session floor consumption. The #155 `floor_dependency` machinery is a lineage check, not a
  fence retirement.
- **L10-NIT-1 (backup_runs.sh): NO REPAIR.** File untouched since `5b12332`; the miscount is
  written into `$DEST/backup.log` and understated by the seat (`instrument_validation/` inflates it
  too).
- **ED-L10-1 is untracked and unclosed.** The identifier appears in no queue, kernel, packet, or run
  report; its content survives only as "a9/a10 desk replay" in three ED-OWED lists. It is a stable
  (non-T0) ED-QUALIFICATION row, which the charter says may not remain open at a sitting.
- **All four unexecuted CLI obligations remain unexecuted**, including the v2 multi-cell aggregate
  mint route gamma depends on — which has since been modified by branch-only work (`cef3306`).
- **Coverage denominator (15/18) is self-nominated, never attacked, and stale**: +4579 lines in
  L10-scope code, a wholly new consumption wire, a new finalizer CLI that was never a universe
  member, and two new pack families. The ordered adversarial re-enumeration (Phase 3) has not run
  and the baseline manifest has not been superseded.
- **Assembler could not verify:** any CLI-level `RECEIPT_STATUS=PASS` from the margins recorder, any
  L10 rehearsal at any post-#155 head, or the existence/absence of an a9/a10 desk-replay transcript
  in Ed-held off-repo custody.
