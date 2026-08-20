# ROW L10 — SACRIFICIAL FULL LIFECYCLE (charter tier: xhigh, launch-gating; state **GATING**)

> **Assembler note on the read tree.** The task named the read-only worktree at
> `impl/r2-s0-mint-resolver` @ `4597ad4`. The tree as found is at **`b92b43d`**
> ("Shakedown-v3 first-light run card (prep item 6b) …"), which is the direct child of
> `4597ad4` (`git merge-base --is-ancestor 4597ad4 HEAD` → yes). All findings below were read
> at `b92b43d`. `main` == `origin/main` == `0099382`. Every pointer is labelled
> **ON-MAIN** or **BRANCH-ONLY**.
>
> **This row assembles evidence. It does not grade the seat.**

---

## 0. Seat identity and 2026-08-15 result

- **Seat:** `L10-SACRIFICIAL-FULL-LIFECYCLE` — charter §The fleet item 10, "SACRIFICIAL FULL
  LIFECYCLE (xhigh): a disposable end-to-end …"
  (`docs/process/instrument-readiness-audit-charter.md:51`).
- **Seat question (seat report §Seat question):** "drive a synthetic-but-shape-true window
  through reduce → verdict → floors → mint → claim consumption at the frozen configuration;
  prove the AFTER-window path exists and fail-closes BEFORE a window is spent; classify every
  refusal (correct vs gap); where synthetic data cannot legally pass, name the real-data
  property demanded."
- **Recorded verdict:** **NOT_READY**, GATING.
  Sitting-packet seat table row, verbatim
  (`docs/process_traces/2026-08-15-readiness-council/sitting-packet-FINAL.md:30`; header at `:21`
  = `lens | gating | verdict | coverage | blockers | should-fix | nits | falsifiers | unexec | ed-qual`):

  ```
  | L10-SACRIFICIAL-FULL-LIFECYCLE | GATING | NOT_READY | 15/18 | 1 | 3 | 1 | 13 | 5 | 1 |
  ```

- **Coverage:** 15/18 examined-and-executed (`evidence_universe_count = 18`). Unexecuted
  obligations, per the seat: #7 salvage dispatch, #8 supersession recording, #13 v2 aggregate CLI
  mint, #18 waiver path, plus the CLI-level PASSED-basis chain (→ ED-L10-1).
- **Component verdict, verbatim (seat report line 7):** "**NOT-READY** — the machinery from
  collection through mint exists, runs, and fail-closes with enumerated, honest refusals at every
  gate (excellent), but the LAST edge — claim consumption of the frozen D-117 packs — is unbuilt
  (blocker F1), and two frozen §11 runbook commands refuse as written (F2, F3)."
- **Refutation status of the blocker:** ECF-contract refuter (Sol xhigh) — "All four CONFIRMED
  (**L10-B1 consumption edge**, L4-B1 margin recorder, L9-B1 maintenance census, L9-B2
  browser/monitor regexes). Qualifications: L1 custody discipline does not categorically bar
  post-collection implementation (but heightened proof burden -> blocker stands) … Remedies ruled
  sound: governed prospective validator + finalizer + queue row"
  (`docs/process_traces/2026-08-15-readiness-council/refuter-outputs/refuter-verdicts.md:92-100`).
  Refuter lens outputs: `refuter-outputs/sol-refuter-ECF-contract.md`,
  `refuter-outputs/sol-refuter-ECF-execution.md`.
- **Seat-report digest recorded in the sealed packet:** `c8f2e0530da08faa`
  (`sitting-packet-FINAL.md:10`).
- **Bearing on a READY-candidate aggregation:** L10 is one of the ten GATING seats. Under charter
  amendment 11/12 and the verdict's own aggregation line
  (`sitting-packet-FINAL.md:36`: "READY requires no NOT-READY + no UNVERIFIED + all ED-QUAL rows
  closed"), this row's blocker and its one ED-QUALIFICATION row both bind the launch GO. The
  council-verdict's standing caution applies in full: "**The work-order program is NOT CERTIFIED
  COMPLETE** … Closing all listed work orders does not entitle READY"
  (`council-verdict.md:18-22`).

---

## 1. FINDINGS — original text verbatim, with citation

Source of the verbatim text below: `raw/L10-triage.md` (extracted from
`docs/process_traces/2026-08-15-readiness-council/triage.json`, seat entry
`L10-SACRIFICIAL-FULL-LIFECYCLE`). Cross-cited to the sealed sitting packet and the seat report.

### F1 — [blocker]

**Title (verbatim):** Frozen packs' claim-consumption edge is unbuilt: analyze-claims refuses the
packs' v3.prospective manifests, the U7-designed prospective builder/validator do not exist, and
the final-v3 wire is hard-pinned to splitwise

**file_line (verbatim):**
`joulewise/analysis_engine/inputs.py:556-568; joulewise/analysis_manifest_v3.py:613,630-663; configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json:2`

**failure_scenario (verbatim):**
> The funded gamma window collects clean, the verdict passes, alpha/beta floors mint into the
> aggregate — and the contrast claim cannot be consumed: analyze-claims refuses 'unsupported
> analysis manifest schema_version: joulewise.analysis_manifest.v3.prospective' (executed);
> validate_analysis_manifest_v3 hard-requires design_id splitwise_decode_cross_model_abba_v1, the
> splitwise generator path/plan sha, exactly two stages and n=10, so no hand-authored final D-117
> manifest can validate either; grep finds zero implementations of the U7-specified
> build_prospective_analysis_manifest_v3 / validate_prospective_analysis_manifest_v3 and no
> postcollection-attachment finalizer; no TASK_QUEUE row tracks this edge. The window is spent and
> its REQUIRED OUTPUT cannot trace through a claim consumer without landing new code post-hoc,
> colliding with L1 same-session custody discipline.

**Citations:** `sitting-packet-FINAL.md:64` ("### L10-SACRIFICIAL-FULL-LIFECYCLE B1: Frozen packs'
claim-consumption edge is unbuilt …"); seat report
`docs/process_traces/2026-08-15-readiness-council/seat-reports/L10-SACRIFICIAL-FULL-LIFECYCLE-report.md:65`;
refuter verdict `refuter-outputs/refuter-verdicts.md:93` (CONFIRMED).
**Post-verdict adjudication:** none — not among the struck findings (council-verdict Disposition 4
struck L8-B4, WO-L2-4, and F4's timing premise only; none is this F1).

**Work order (verbatim, WO-1, closes blocker F1):**
> implement and land the D-117 analysis-manifest consumption edge before any window is spent —
> build_prospective_analysis_manifest_v3 / validate_prospective_analysis_manifest_v3 per the U7
> spec (docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md §'Prospective analysis-manifest
> repair'), plus the postcollection-attachment finalizer (passed verdict sha, evaluation-basis
> sha, bracket-binding sha, terminal ledger head, aggregate floor-artifact sha) producing a
> manifest analyze-claims accepts, generalizing the final-v3 wire beyond its splitwise pins
> without changing splitwise bytes; add refusal regressions for missing/stale attachments

### F2 — [should_fix]

**Title (verbatim):** Runbook §11 extraction command as frozen refuses at argparse:
--evaluation-basis-sha256 without the co-required --consumption-semantics-id

**file_line (verbatim):**
`docs/phase_2/window_runbook.md:1485-1491 vs scripts/extract_detection_floors.py:100-106`

**failure_scenario (verbatim):**
> At close-out the operator pastes the literal §11 command; it exits 2 with
> '--evaluation-basis-sha256 and --consumption-semantics-id are required together' (executed). A
> tired operator must improvise the exact semantics id (d078_minted_envelopes_v1) at 4 a.m. —
> precisely the hand-improvisation the runbook forbids elsewhere — or close-out stalls.

**Citations:** `sitting-packet-FINAL.md:148`; seat report line 66.

### F3 — [should_fix]

**Title (verbatim):** Runbook §11 margins-recorder identity mismatch: --pack-identity
"$WINDOW_ID" (window_a9_YYYYMMDD convention per §4) can never satisfy the recorder's plan-derived
window_id requirement

**file_line (verbatim):**
`docs/phase_2/window_runbook.md:1456-1461 (with §4 window.env WINDOW_ID convention at line 186) vs joulewise/window_duration_margins.py:374-379`

**failure_scenario (verbatim):**
> First §11 command on the night: the recorder REFUSEs {reason: pack_identity_invalid} for any
> identity other than the pack plan-tree's window_id (executed with both the runbook-style id and
> the pack dirname; only plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1 advances). REFUSE stops
> close-out by §11's own rule; the operator must reverse-engineer identity semantics mid-night.

**Citations:** `sitting-packet-FINAL.md:149`; seat report line 67.

**Work order (verbatim, WO-2, closes F2+F3):**
> repair runbook §11 — add --consumption-semantics-id d078_minted_envelopes_v1 to the extraction
> command, and replace --pack-identity "$WINDOW_ID" with the pack's plan-derived window_id literal
> (plan-d117-…-v1) per pack, or define WINDOW_ID as that literal for D-134 nights in §4

### F4 — [should_fix]

**Title (verbatim):** L1 same-custody-session limitation structurally conflicts with the
three-window design's cross-session floor consumption; FLOOR-BIND-01 is READY but unclosed

**file_line (verbatim):** `TASK_QUEUE.md:477 (L1 fence); docs/phase_2/window_runbook.md:61-66`

**failure_scenario (verbatim):**
> Even with the manifest edge built, the gamma analysis must consume alpha/beta floor artifacts
> extracted and minted in EARLIER custody sessions; L1 ('claim-bearing analysis may consume floor
> artifacts only from same-custody-session governed extraction') renders that consumption
> non-claim-bearing until FLOOR-BIND-01 lands or a prospective ruling licenses an L1-compatible
> cross-window procedure. No such ruling or closure is scheduled before the windows.

**Citations:** `sitting-packet-FINAL.md:150`; seat report line 68.
**Post-verdict adjudication:** council-verdict Disposition 4 struck "**F4's timing premise**
(privilege gap survives inside WO-T0-PRODUCER)" — but that strike names **L3/T-0 F4**, not this
seat's F4; L10's F4 appears unstruck in the sitting packet's should-fix list at `:150`. **The seat
should confirm this reading; the assembler flags it as an ambiguity, not a fact.**

**Work order (verbatim, WO-3, closes F4):**
> close FLOOR-BIND-01 before gamma claim consumption, or obtain a prospective magistrate ruling
> licensing an L1-compatible cross-window floor-consumption procedure (recorded before the plan
> freeze, not improvised after collection)

### F5 — [nit]

**Title (verbatim):** backup_runs.sh counts campaign_manifests/ as a bundle in operator-facing
output (reported 5 bundles for a 4-member window)

**file_line (verbatim):** `scripts/backup_runs.sh:25-36`

**failure_scenario (verbatim):**
> §12 requires member counts by distinct bundle ID; an operator cross-checking the backup line (5)
> against the member count (4) sees a discrepancy and burns close-out time chasing a phantom
> bundle. Cosmetic; the copy itself was complete and correct (executed).

**Citations:** `sitting-packet-FINAL.md:151`; seat report line 69.

**Work order (verbatim, WO-4, nit F5):**
> make backup_runs.sh exclude campaign_manifests/ from its bundle count or reword the
> operator-facing line

### Unexecuted obligations (verbatim, all five)

> - §9 D-100 salvage-dangler verdict dispatch (--consumption-semantics-id
>   salvage_dangler_exclusion_v1 with membership binding + salvage closure) — not exercised at the
>   CLI (no synthetic salvage closure); covered only by suite evidence
> - §10 --record-supersession quarantine/supersession flow — not exercised at the CLI
> - v2 multi-cell aggregate mint route (--v2-input-manifest + schema_v2 pinset), the route the
>   gamma consumption depends on — not exercised at the CLI; covered by
>   tests/test_mint_floor_artifact_generalized.py (passed)
> - Waiver path: --waivers producing a 'flagged' verdict and extraction refusing the flagged basis
>   — not exercised
> - CLI-level PASSED-basis end-to-end (verdict passed → margins PASS → extraction admitted → mint
>   minted) — impossible from the desk without a real window corpus; see ED-QUALIFICATION row

Citation: `sitting-packet-FINAL.md:235-239`.

---

## 2. WHAT CHANGED SINCE 2026-08-15

### F1 — the claim-consumption edge

**A. The work order exists and its code merged.**

- **Queue row now exists** (F1's "no TASK_QUEUE row tracks this edge" is cured):
  `TASK_QUEUE.md:537` (generated Current Queue) and `TASK_QUEUE.md:631`; kernel source
  `docs/process/state_kernel.json:3176` (acceptance) and `:3207` (status note). Row **A2
  `WO-CONSUMPTION-EDGE`**, status **`PARTIAL; READY [AGENT]`** — i.e. **queued, not closed**.
  Status note verbatim from `TASK_QUEUE.md:537` / `state_kernel.json:3207`:
  > Code MERGED #155 (d54db78). D-139 rules delivered: Holm m=2 family (decode+prefill,
  > alpha=0.05, two-sided) adopted; p256 floor = dedicated artifact (cells already frozen, #138).
  > **Remaining before close: the production freeze (rides Phase 2) + the same-head production-pack
  > L10 replay**
- **PR #155**, merge commit **`d54db78`** (2026-08-16), "Merge pull request #155 from
  mpmdw/impl/wo-consumption-edge" — **ON-MAIN**.
- Implementation commits, all **ON-MAIN**:
  - `0cba93d` — "WO-CONSUMPTION-EDGE checkpoint (scoped build complete, NEEDS_SCOPE pause):
    prospective validator + outcome-blind finalizer + finalized-v3 consumer wire + synthetic
    end-to-end; open scientific rulings flagged NOT invented (contract cl.5); artifact.py
    family-semantics validation awaits scope grant"
  - `189feab` — "WO-CONSUMPTION-EDGE continuation: manifest-bound family-semantics validation in
    artifact.py (replaces the historical Holm m=1 hard-pin; historical v3 byte/behavior
    compatibility proven), frozen cross-arm LOO block-strata mechanism with registered refusal
    when a multi-contrast family lacks strata"
  - `eabe853` (fix round 1), `d1e5dfc` (fix round 2, delta residuals), `fa87666` (fix round 3) —
    three C-028 fix rounds against two lens sets.

**B. What the code actually is now (read at `b92b43d`).**

- New CLI **`scripts/finalize_analysis_manifest.py`** (added at `0cba93d`), docstring:
  `"""Outcome-blind prospective-to-finalized analysis-manifest transition."""`; required args
  `--prospective-manifest --plan-tree --custody-root --runs-root --whole-window-verdict
  --bracket-binding --calibration-ledger --aggregate-floor-artifact --output-dir`.
- `joulewise/analysis_manifest_v3.py:3722` `def finalize_prospective_analysis_manifest_v3(`;
  `:4062` `def validate_finalized_analysis_manifest_v3(`.
- `joulewise/analysis_engine/inputs.py` `load_manifest` now dispatches on
  `ANALYSIS_MANIFEST_FINALIZED_V3_SCHEMA` via `validate_finalized_analysis_manifest_v3`, and the
  bare-prospective path is a **registered** refusal rather than the generic one L10 executed:
  ```python
  elif schema_version == "joulewise.analysis_manifest.v3.prospective":
      raise AnalysisInputError(
          "analysis_manifest_prospective_not_consumable: frozen prospective "
          "manifests must pass the outcome-blind finalizer"
      )
  ```
- Regressions: `tests/test_analysis_finalizer.py` (948 lines, new),
  `tests/test_analysis_manifest_v3.py` (780 lines).
- **Naming delta the seat should note:** the U7 symbols F1/WO-1 named —
  `build_prospective_analysis_manifest_v3` / `validate_prospective_analysis_manifest_v3` — **still
  return zero repo-wide grep hits.** The adopted remedy is a different shape: a two-artifact
  contract (frozen prospective is never mutated and never consumed; an outcome-blind finalizer
  derives an immutable `joulewise.analysis_manifest.v3.finalized`). Authority:
  `docs/decision_log.md:9100-9130` (WO-CONSUMPTION-EDGE adopted contract, clauses 1–6), with the
  refusal registry at `docs/decision_log.md:9143+` ("D-078 amendment — 2026-08-15:
  analysis-manifest consumption-edge refusal registry").
- The `_v3` packs still ship `joulewise.analysis_manifest.v3.prospective`
  (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/analysis_manifest_v3.json`) — consistent
  with clause 1, not a residual of the defect.

**C. The production freeze that A2 names as "remaining" — DONE, BRANCH-ONLY.**

All of the following are **BRANCH-ONLY** on `impl/r2-s0-mint-resolver` (none is an ancestor of
`main` @ `0099382`):

| SHA | Subject (verbatim `git log -1 --format=%s`) |
|---|---|
| `cef3306` | S0 kernel: generation-resolved mint policy (D-147 S2/S4); genesis digest rename; schema generation conditionals |
| `6771924` | S0 regressions: no-copied-scalar guard, genesis-fixture authentication test, resolver call-shape updates |
| `8018a4b` | S0 fix round 1: fixture declaring-id threading (B1), immutable resolver operatives (B2), shim removal, malformed-container refusal, schema id-set $defs, N4/N5 guards |
| `b7e5730` | S1: anchor-v3 production flip + D-079 r5 (science-neutral, 19-member replay proven) + claim barrier (D-146) |
| `1ec5dc4` | S1 fix round: v3 production fixtures, whole-window v3 conversion + retained v2 negatives, era fixture repairs, r5 rebinds, test_052 era adjudication + v3 stale pin, A9 kill tests |
| `3038eeb` | S1 fix round 2: two-lens findings — per-lane barrier pins + capture_pipeline_absent (positive presentation), F1 attack rebuilt on v3, campaign-positive fixture, allowlist era pre-filter, diagnostics outside governed artifact, r5 schema row, D-079 r6 (pins: reduce.py + uncertainty_evidence.py; 19-member neutrality proven) |
| `d8f1202` | S2: r6 golden re-derivation via independent fixture oracle; n19 literals generation-derived; six-artifact copy-list |
| `1d3873b` | S3: d117 _v3 pack family emitted via unedited _v2 generators, bound to r6 at birth; family tests (successor emission, replay integrity, byte preservation) |
| `3a75a77` | D-147 S4: author D-134 freeze evidence for the three _v3 packs at the measurement checkout (all PASS) |
| `5e38f1e` | D-147 S5: freeze-0003 minted for d117_floor_qwen25_1p5b_v3 (PASS; predecessor _v2/freeze-0002 1277103b…; receipt 0abfddb1…) |
| `eb7f6c6` | D-147 S5: freeze-0003 minted for d117_floor_qwen25_7b_v3 (PASS; predecessor _v2/freeze-0002 decd8cdc…) |
| `94dc3b3` | D-147 S5: freeze-0003 minted for d117_contrast_qwen25_1p5b_vs_7b_v3 (PASS; predecessor _v2/freeze-0002 18855647…) |
| `8b2b021` | S5 COMPLETE: confirmation table filled (three freeze-0003 receipts + committed tree digests) |

Custody for the transaction: `docs/process_traces/2026-08-19-refreeze-execution/` — subdirs
`r5-issuance/` (49 files incl. `build_r5.py`, `r5-neutrality-proof.json`, 19 per-member
transcripts), `r6-issuance/` (43 files incl. `build_r6.py`, `r6-neutrality-proof.json`),
`reports/` (S0/S1 impl + two-lens + fix-round + delta reports, `S2-goldens-report.md`,
`S3-emission-report.md`, `consistency-sweep.md`, `docs-fidelity-opus.md`), `s2-goldens/`,
`s4/` (per-pack `author-*.json`, `check-*_v2.log` / `check-*_v3.log`, `authored-files.sha256`,
15 arm-readiness/plan suite logs), `suite-logs/`.
r6 acceptance: `docs/process_traces/2026-08-19-r1-r2-codesign/15-amendment-r6.md` — "the `_v3`
family binds **r6** at birth (executed: `configs/campaigns/d117_*_v3/generate_configs.py`
SUCCESSOR_ACCEPTANCE_ID = `d079_calibration_acceptance_v2_n17_r6`)". Rulings: `13-r1-ruling.md`
(D-146), `14-r2-ruling.md` (D-147); index rows `docs/decision_log.md:8844`, `:8850`.

**D. The other half of "remaining before close" — the same-head production-pack L10 replay.**

**EVIDENCE NOT LOCATED.** No artifact, transcript, receipt, report, or custody directory
recording an L10 sacrificial-lifecycle replay at any head after the `_v3` emission/freeze exists
in this tree.
Searched: repo-wide grep over `docs/`, `TASK_QUEUE.md`, `RUN_STATE.md` for
`L10 replay|L10-replay|sacrificial rehearsal|sacrificial replay|SACRIFICIAL` — every hit is
forward-looking or historical narrative (`docs/decision_log.md:9117`, `:9137`;
`docs/process/ed-batch-packet.md:32`; `docs/process/state_kernel.json:3176`, `:3207`;
`TASK_QUEUE.md:537`, `:631`; `RUN_STATE.md:465`;
`docs/process_traces/2026-08-15-consumption-edge-consult/consult.md:34,269,290`;
`docs/council_log.md:3568,3570,3626,3642,3710`;
`docs/process/instrument-readiness-audit-charter.md:51`); full file listing of
`docs/process_traces/2026-08-19-refreeze-execution/**` (no lifecycle-replay artifact);
grep for `L10|replay` in `docs/run_reports/2026-08-19-t12-t13-session.md` (single hit, the r6
19-member neutrality replay — unrelated); grep for `L10|backup_runs|pack-identity|consumption-semantics`
across the T8/T9/T10 session reports (zero hits).
The requirement itself is doubly recorded: `docs/decision_log.md:9117` — "the L10 sacrificial
rehearsal re-runs the full edge at the same head before any window is spent"; and
`docs/decision_log.md:9137` — the Ed RULING-REQUIRED item "(d) authorization of the production
successor freeze followed by the **same-HEAD, production-pack L10 sacrificial replay**".
Ed's 2026-08-19 rulings (D-148, `docs/decision_log.md:171` index row, 8856 body) cover the S5 mint
route, merge authority, confirmation table, quiet-window delegation, R1 registry values → council,
the risk-appetite limitation family, and the anchor-v2 registered limitation — **the index row
contains no ruling authorizing or recording the L10 replay.**

**E. Not changed, and relevant to F1's operator surface.**

`docs/phase_2/window_runbook.md` runs `## 11. Record duration margins, back up, then extract in
the same custody session` (`:1730`) directly into `## 12. Close-out record` (`:1790`). Grep for
`finalize_analysis_manifest` and `analyze-claims` in the runbook returns **zero** hits (the only
`finalized` hits, `:460` and `:1732`, are about calibration slots). **The frozen operator
procedure does not route through the new finalizer or through any claim consumer.**

### F2 — runbook §11 extraction command

**NO REPAIR FOUND.** Current text at `docs/phase_2/window_runbook.md:1765-1772` (the finding cited
`:1485-1491`; the section moved, the defect did not):

```sh
.venv/bin/python scripts/extract_detection_floors.py \
  --runs-root "$RUNS_ROOT" \
  --spec "$WINDOW_PLAN_ROOT/extraction_spec.json" \
  --out "$WINDOW_CUSTODY_ROOT/detection-floor-extraction.json" \
  --evaluation-basis-sha256 "$WHOLE_WINDOW_BASIS_SHA256" \
  --hash-bundles
```

`--consumption-semantics-id` appears exactly once in the whole runbook — at `:1537`, inside the §9
salvage-dangler dispatch, not here. The co-requirement is still enforced verbatim at
`scripts/extract_detection_floors.py:101-106`:

```python
    if (args.evaluation_basis_sha256 is None) != (
        args.consumption_semantics_id is None
    ):
        parser.error(
            "--evaluation-basis-sha256 and --consumption-semantics-id are required together"
        )
```

No queue row tracks WO-2 (grep of `TASK_QUEUE.md` for `backup_runs|RUNBOOK|runbook §11|WO-RUNBOOK`
returns only the unrelated `P0-002` row at `:173`).

### F3 — margins-recorder `--pack-identity`

**PARTIAL, INCIDENTAL REPAIR — via WO-2's *alternative* remedy, not its primary one.**

- The §11 command is **unchanged**: `docs/phase_2/window_runbook.md:1742` still reads
  `  --pack-identity "$WINDOW_ID"`.
- What changed is §4's definition of `WINDOW_ID`. Commit **`844453a`** (**ON-MAIN**) —
  "Bookkeeping follow-ups: D-138/D-139 index rows (pre-existing gap); **window.env example flipped
  whole to the _v2 family with real generated identities**; refusal paragraph updated to the
  v2-family reading". Current `docs/phase_2/window_runbook.md:190`:
  ```
  WINDOW_ID=plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v2
  ```
  This is the plan-derived literal form WO-2 offered as its second option ("or define WINDOW_ID as
  that literal for D-134 nights in §4"). The `window_a9_YYYYMMDD` convention the finding cited is
  gone from the example.
- **New staleness the fix introduces:** the frozen §4 literal is pinned to the `_v2` family, but
  the packs frozen at S5 are the `_v3` family. `configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json:3717`
  → `"window_id": "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3"`, against
  `configs/campaigns/d117_floor_qwen25_1p5b_v2/plan_tree.json:3717` → `…-v2`. Pasting the frozen
  §4 literal against a `_v3` pack reproduces exactly F3's `{"reason": "pack_identity_invalid",
  "status": "REFUSE"}`. **The §4 window.env example was not re-flipped to `_v3` in the S0–S5
  transaction** (`git log 8937dec..HEAD -- docs/phase_2/window_runbook.md` shows the last
  runbook commit as `f4d5ea7`, "D-079 r3 live-pin migration", BRANCH-ONLY, unrelated).

### F4 — L1 fence / FLOOR-BIND-01

**NOTHING CHANGED.** `FLOOR-BIND-01` is still row **A10**, status **`READY [AGENT]`**, unclosed
(`TASK_QUEUE.md:542`, `:636`; kernel `docs/process/state_kernel.json:1237-1268`). Its fence text
is verbatim what the finding quoted:
> Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from
> same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078
> clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1
> workflow rule mitigates until closed.

**No prospective ruling licensing an L1-compatible cross-window floor-consumption procedure was
located.** Searched: `docs/decision_log.md` for `cross-window|cross-session floor|L1-compatible|aggregate floor`
(hits: the D-082 index row at `:107`, the D-082 body at `:5173`, and the WO-CONSUMPTION-EDGE
clause 1 mention of "exact aggregate floor artifact" at `:9107` — none is a ruling on L1's
same-session fence); D-145 through D-149 index rows (`docs/decision_log.md:8838-8871`) — none
addresses it. The adjacent change is that the finalizer now authenticates "aggregate floor
lineage" as one of its attachments (`docs/decision_log.md:9106-9108`), which is a mechanism, not a
licence. Runbook §11's heading still binds close-out to one session: "Record duration margins,
back up, then extract **in the same custody session**" (`:1730`).

### F5 — `backup_runs.sh` bundle count

**NO REPAIR FOUND.** `git log 8937dec..HEAD -- scripts/backup_runs.sh` is **empty** — zero commits
since the audit baseline. The counter at `scripts/backup_runs.sh:25-36` is byte-unchanged:

```sh
count_bundles() {
  ...
  while IFS= read -r _bundle_path; do
    bundle_count=$((bundle_count + 1))
  done < <(find "$RUNS_DIR" -mindepth 1 -maxdepth 1 -type d ! -name experiments -print)
  echo "$bundle_count"
}
```

`campaign_manifests/` is still counted (only `experiments` is excluded).

### Unexecuted obligations

**NO CLOSURE EVIDENCE LOCATED** for any of the five. No CLI transcript for the §9 salvage dispatch,
the §10 `--record-supersession` flow, the v2 aggregate mint route, the waiver path, or a PASSED-basis
end-to-end run exists in `docs/process_traces/2026-08-19-refreeze-execution/**` (whose `s4/` and
`suite-logs/` cover pack authoring, arm-readiness suites and plan tests only) or in any post-council
process trace. Searched the same greps as §2.D plus the full refreeze-execution file listing.

---

## 3. ED-QUALIFICATION ROWS

### ED-L10-1 (verbatim, `sitting-packet-FINAL.md:190`; `raw/L10-triage.md` §ED-QUALIFICATION ROWS)

> ED-L10-1 (stable capability, any tap block, no live measurement): one desk replay of the
> complete post-collection chain against a RETAINED real window corpus (a9/a10 custody, Ed-held
> off-repo) — whole-window verdict (expect passed), duration-margins recorder, backup, governed
> extraction with the matching spec and basis sha — pasting every command and exit code. This
> supplies the CLI-level PASSED-basis positive proof that no sandboxed desk rehearsal can produce,
> because a passing basis requires real calibration-bracket, NEG-8 corpus, and reference-triplet
> evidence that only a live sudo/powermetrics window can mint.

**NO CLOSURE EVIDENCE LOCATED — searched:**

1. Repo-wide grep for `a9/a10 desk replay|a9-a10 desk replay|desk replay` over `docs/`,
   `RUN_STATE.md`, `TASK_QUEUE.md`. Every JouleWise-current hit is a **still-owed** item, not a
   record of execution:
   - `RUN_STATE.md:459` — "… ED-Q-L9-3 quiet-state baseline EARLY, **a9/a10 desk replay**,
     ED-QUAL-L4-1) PLUS the three risk-appetite calls …"
   - `RUN_STATE.md:546` — "**ED-OWED (ONE batched session when Phase 1 nears close; NOTHING now):**
     … ED-Q-L9-3 quiet-state baseline — EARLY if any tap happens, it gates the census WO;
     **a9/a10 desk replay**; ED-QUAL-L4-1 decisive replay) …"
   - `docs/process/ed-batch-packet.md:57` — under "## B. Hands-on qualification (the hardware batch
     — unchanged from T8's list)": "… **a9/a10 desk replay**; ED-QUAL-L4-1 decisive replay. ONE
     home: RUN_STATE §Ed-owed + `docs/phase_2/window_runbook.md`."
   - `docs/process/ed-evening-checklist.md:24` — item 5: "**a9/a10 desk replay + ED-QUAL-L4-1
     decisive replay** — desk items, can run while other captures settle."
   - `docs/run_reports/2026-08-16-t9-session.md:497`; `docs/council_log.md:3687` — narrative
     restatements of the owed item.
2. Directory listing of `~/JouleWise-window-custody/` (22 entries). The one Ed-qualification
   session present, **`ed-qual-20260817/`**, contains: `clock-post-state.txt`,
   `clock-prior-state.txt`, `decisive-replay-work/`, `decisive-replay-work2/`,
   `decisive-replay.log`, `ed-session-evidence/`, `keyboard-backlight.txt`, `quiet-census/`,
   `rail-probe-load-note.txt`, `sudoers-digest.txt`, `sudoers-vector-{off,on}.txt`,
   `vector-{off,on}-confirmed.txt`. The `decisive-replay*` artifacts are **ED-QUAL-L4-1** (their
   payload is `d117_v2_production_custody_store.tar.zst` + a content-addressed `store/`), not the
   a9/a10 chain. `ed-session-evidence/` holds rail-probe and sampler-checklist output only.
   **No a9/a10 post-collection replay transcript.**
3. `~/JouleWise-window-custody/window_a10_20260725/` — contains only `CLOSE_OUT.md` (mtime
   2026-07-25 06:54), `detection-floor-extraction.json` (2026-07-25 06:37), `operator_logs/`,
   `quarantine/`. `~/JouleWise-window-custody/window_a9_20260724/` — only `operator_logs/` and
   `quarantine/`. **Both untouched since the original July windows; no replay output was written
   into custody.**
4. Full file listing of `docs/process_traces/2026-08-19-refreeze-execution/**` — no a9/a10
   artifact.
5. Grep for `L10` across `docs/run_reports/2026-08-15-t8-session.md`,
   `2026-08-16-t9-session.md`, `2026-08-18-t10-session.md`, `2026-08-19-t12-t13-session.md` — zero
   execution records.

**Related, and not the same thing:** the two-artifact contract requires a *separate* replay — the
"same-head production-pack L10 replay" of §2.D above, which is against the **frozen `_v3` packs**,
not against the retained a9/a10 corpus. **Neither replay has located evidence.** ED-L10-1 supplies
the PASSED-basis positive proof; the A2 replay proves the current packs' edge. A seat should not
let one stand in for the other.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

**Candidate dispositions are assembled, not adjudicated; the seat rules.**

| Item | Sev. | Candidate disposition | What the seat is adjudicating |
|---|---|---|---|
| **F1** consumption edge unbuilt | blocker | **REPAIR-EVIDENCE-ATTACHED, WORK ORDER NOT CLOSED** | The designed mechanism landed and merged (PR #155 / `d54db78`, ON-MAIN: finalizer CLI, finalized-v3 validator, registered prospective refusal, ~1.7k lines of regressions), and the production freeze it waited on executed (BRANCH-ONLY, `1d3873b`→`8b2b021`). But the row's own closure condition — the **same-head production-pack L10 replay** — has no located evidence, the shape differs from the U7 symbols WO-1 named, and the operator runbook still contains no finalize or analyze-claims step. Does mechanism-plus-suite discharge a blocker whose original charge was "the after-window path cannot be traced end-to-end"? |
| **F2** §11 extraction argparse | should-fix | **STILL-OPEN / NO-REPAIR-FOUND** | Text unchanged (`window_runbook.md:1765-1772`), enforcement unchanged (`extract_detection_floors.py:101-106`), no queue row. The 4 a.m. failure the finding described is reproducible today. |
| **F3** `--pack-identity` mismatch | should-fix | **PARTIALLY REPAIRED — AND NEWLY STALE** | `844453a` (ON-MAIN) adopted WO-2's alternative by redefining `WINDOW_ID` as the plan literal at `:190` — but pinned to `_v2`, while the frozen packs are now `_v3` (`plan_tree.json:3717`, `…-v3`). The seat weighs whether an incidental bookkeeping commit closes a council should-fix, and whether the fix has already decayed. |
| **F4** L1 fence vs cross-window floors | should-fix | **STILL-OPEN / NO-REPAIR-FOUND** | `FLOOR-BIND-01` unchanged at `READY [AGENT]`; no cross-window ruling located; runbook §11 still binds close-out to one custody session. Seat must also settle whether council-verdict Disposition 4's strike of "F4's timing premise" touches this seat's F4 at all (assembler reads it as the T-0 F4; flagged, not decided). |
| **F5** `backup_runs.sh` miscount | nit | **STILL-OPEN / NO-REPAIR-FOUND** | Zero commits to the file since baseline; `campaign_manifests/` still counted. |
| **5 unexecuted obligations** | — | **NO CLOSURE EVIDENCE LOCATED** | None of the five CLI gaps has a located transcript; the v2 aggregate mint route (the one gamma consumption depends on) remains suite-covered only. |
| **ED-L10-1** desk replay | ED row | **NO CLOSURE EVIDENCE LOCATED — still Ed-owed** | Named as outstanding in four live surfaces (`RUN_STATE.md:459,:546`, `ed-batch-packet.md:57`, `ed-evening-checklist.md:24`); the one executed Ed-qual session (`ed-qual-20260817`) covered other rows; the a9/a10 custody dirs are untouched since July. Under charter aggregation ("all ED-QUAL rows closed"), this row on its own is dispositive for the seat. |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

1. **[MANDATORY — the lifecycle proof against the *current* packs.]** Was the sacrificial
   lifecycle re-run end-to-end **after** the S0–S5 pack/mint rewrite? The 2026-08-15 rehearsal was
   executed at `8937dec` against the `_v1` packs; the packs since became `_v2` and then `_v3` with
   `freeze-0003` receipts (`5e38f1e`, `eb7f6c6`, `94dc3b3`) and a new capture-era claim barrier
   (`b7e5730`, D-146) and generation-resolved mint policy (`cef3306`, D-147). **A lifecycle proof
   against superseded packs proves nothing about the current ones.**
   *Probe:* `ls docs/process_traces/*/ | grep -i lifecycle`; `git log --all --oneline --since=2026-08-16 | grep -i 'L10\|lifecycle\|sacrificial'`; ask for the transcript by path.
   *Falsifier:* production of a dated transcript naming the `_v3` pack roots and a commit SHA at or
   after `1d3873b`, showing reduce → verdict → margins → backup → extraction → mint →
   finalize → analyze-claims with exit codes. **Absent that artifact, A2's own closure text
   ("Remaining before close: … the same-head production-pack L10 replay") is unmet on its face.**
2. **Does the finalizer actually work on a real frozen `_v3` pack, or only on fixtures?** The three
   fix rounds (`eabe853`, `d1e5dfc`, `fa87666`) describe fixture, fuzz, and injected-bug batteries.
   *Probe:* run `scripts/finalize_analysis_manifest.py` against
   `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/analysis_manifest_v3.json` with the real
   `plan_tree.json` and deliberately absent attachments; then with a `_v2` prospective manifest and
   `_v3` plan tree.
   *Falsifier:* it produces a finalized artifact for a mismatched generation pair, or it refuses
   with an unregistered code (D-078 amendment registry, `docs/decision_log.md:9143+`, requires a
   registered top-level code).
3. **Rule-11 fix-round hazard: did the fix rounds break what round zero proved?** `fa87666` and
   `d1e5dfc` are the second and third fix rounds on the same boundary; the r6 amendment itself
   records the general rule that "fix rounds can invalidate design-time verifications"
   (`15-amendment-r6.md`).
   *Probe:* was a C-028 **delta re-audit** run after `fa87666`? Look for a delta report naming it
   in `docs/process_traces/2026-08-19-refreeze-execution/reports/` (which holds `S0-delta.md` and
   `S1-delta.md` — for S0/S1, not for the consumption-edge rounds).
   *Falsifier:* a delta-re-audit artifact covering `eabe853..fa87666`.
4. **Is the operator surface wired to the new edge at all?** Grep the runbook: `grep -n
   'finalize_analysis_manifest\|analyze-claims' docs/phase_2/window_runbook.md` → **zero hits**;
   §11 (`:1730`) runs straight into §12 (`:1790`).
   *Falsifier:* a runbook section, operator card, or `docs/process/` checklist that invokes the
   finalizer with the eight required paths. If none exists, the machinery is unreachable from the
   frozen night procedure, and F1's failure scenario ("landing new code post-hoc") is replaced by
   "improvising an eight-argument command post-hoc."
5. **Re-run F2 and F3 verbatim at this head.** Paste `window_runbook.md:1765-1772` unmodified;
   paste `:1739-1744` with `WINDOW_ID` from `:190` against a **`_v3`** pack root.
   *Falsifier:* exit 0 on either. Expected on the assembled evidence: exit 2
   (`required together`) for F2 and `{"reason": "pack_identity_invalid", "status": "REFUSE"}` for
   F3-against-`_v3`.
6. **Does anything license gamma's cross-session floor consumption?** `FLOOR-BIND-01` is still
   `READY` and its fence is verbatim intact.
   *Probe:* `grep -n 'FLOOR-BIND-01' TASK_QUEUE.md docs/process/state_kernel.json`; search D-138…D-149
   bodies for a cross-window licence.
   *Falsifier:* a decision-log clause, recorded **before** the freeze, licensing an L1-compatible
   cross-window procedure. Note the timing constraint in WO-3's own words: "recorded before the plan
   freeze, not improvised after collection" — and the freeze already happened at S5.
7. **Whose evidence lives where?** The entire Phase-2 transaction (`cef3306` … `8b2b021`, plus the
   refreeze custody tree) is **BRANCH-ONLY**; `main` is `0099382`. The F1 code is ON-MAIN; the
   freeze that F1's closure depends on is not.
   *Probe:* `git merge-base --is-ancestor <sha> main` for each cited SHA.
   *Falsifier:* a merged PR bringing the transaction to main. A seat weighing "the freeze is done"
   must decide whether branch-resident freeze receipts satisfy a launch gate.
8. **Do the five unexecuted obligations still bind?** In particular the v2 multi-cell aggregate
   mint route, which L10 named as "the route the gamma consumption depends on … not exercised at
   the CLI".
   *Falsifier:* a CLI transcript of `--v2-input-manifest` with the `schema_v2` pinset against real
   pack bytes. Suite coverage (`tests/test_mint_floor_artifact_generalized.py`) was already the
   seat's stated reason for calling it unexecuted, so a green suite is **not** a falsifier here.

---

## 6. OPEN ITEMS FROM THIS ROW

- **ED-L10-1 (a9/a10 desk replay against the RETAINED real corpus) has NO located closure
  evidence.** It is still listed as owed in four live surfaces (`RUN_STATE.md:459`, `:546`,
  `docs/process/ed-batch-packet.md:57`, `docs/process/ed-evening-checklist.md:24`); the executed
  Ed-qualification session `~/JouleWise-window-custody/ed-qual-20260817/` covered sudoers, clock,
  backlight, quiet census, rail probe and the ED-QUAL-L4-1 decisive replay, but not this; the a9
  and a10 custody directories are unmodified since 2026-07-25.
- **The same-head production-pack L10 sacrificial replay — A2's own stated closure condition — has
  NO located closure evidence**, although the production freeze it was sequenced after has
  executed (BRANCH-ONLY). `TASK_QUEUE.md:537` still reads "Remaining before close: the production
  freeze (rides Phase 2) + the same-head production-pack L10 replay". The sacrificial lifecycle has
  therefore never been driven end-to-end against `_v2` or `_v3` packs, only against the `_v1` packs
  of the audit baseline.
- **F2 is untouched.** The frozen §11 extraction command at `docs/phase_2/window_runbook.md:1765-1772`
  still omits `--consumption-semantics-id`, and `scripts/extract_detection_floors.py:101-106` still
  refuses. No queue row tracks WO-2.
- **F3's repair has already gone stale.** `WINDOW_ID` at `docs/phase_2/window_runbook.md:190` is
  pinned to the `_v2` plan literal, while the frozen packs are `_v3`
  (`configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json:3717`). The S0–S5 transaction did
  not re-flip the window.env example.
- **F4 is untouched and its deadline has passed.** `FLOOR-BIND-01` remains `READY [AGENT]`
  (`TASK_QUEUE.md:542`), no cross-window floor-consumption ruling was located, and WO-3 required
  any such ruling to be "recorded before the plan freeze" — the S5 freeze has already occurred.
- **F5 is untouched.** Zero commits to `scripts/backup_runs.sh` since the audit baseline.
- **All five of L10's unexecuted obligations remain without located CLI evidence**, including the
  v2 multi-cell aggregate mint route that the seat identified as the route gamma consumption
  depends on.
- **The claim-consumption edge is absent from the operator-facing runbook.** No
  `finalize_analysis_manifest` or `analyze-claims` step exists anywhere in
  `docs/phase_2/window_runbook.md`; §11 runs directly into §12.
- **Naming/shape divergence between WO-1 and the delivered remedy is unreconciled in writing.** The
  U7 symbols WO-1 named (`build_prospective_analysis_manifest_v3` /
  `validate_prospective_analysis_manifest_v3`) do not exist; the adopted two-artifact contract
  (`docs/decision_log.md:9100-9130`) is a different design. No document located records that the
  council's WO-1 text was superseded by that contract.
- **Disposition-4 ambiguity:** council-verdict Disposition 4 strikes "F4's timing premise
  (privilege gap survives inside WO-T0-PRODUCER)". The assembler reads that as the T-0/L3 F4, not
  L10's F4 (which is about the L1 custody fence and has no timing premise), and L10's F4 is still
  listed live in the sitting packet's should-fix list at `:150`. **Unresolved by the assembler; a
  seat must rule.**
- **Read-tree discrepancy:** the task named `4597ad4`; the worktree is at its child `b92b43d`. One
  additional commit ("Shakedown-v3 first-light run card (prep item 6b)") is inside every finding
  above.
