# Block-5 analysis plan: deviation log

This log records deviations from the sealed block-5 analysis plan,
`configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` (called **PLAN** below). Its SHA-256 is pinned in
`configs/analysis/b5/seal_pins.json`, `sealed.analysis_plan_sha256`.

Before this file, the plan's deviations were recorded in three places:
- the registration's §10 list of registered deviations (sealed);
- the decision log (`docs/decision_log.md`, for example D-188 to D-190);
- `RUN_STATE.md`.

No single document gathered them. This file is that place from 2026-11-06 on.

**Why the plan does not link here.** The plan is sealed. One changed byte changes its SHA-256. The frozen-file test
(`tests/b5_analysis/test_frozen_files.py`) would then fail, and so would the dry run's seal check
(`joulewise/b5_analysis/dry_run.py`, `SEAL_KEYS`). Instead this log is linked from:
- the care audit, `docs/run_reports/2026-11-06-b5-care-audit.md` §4;
- the lean release runbook, `docs/analysis/b5/RELEASE-RUNBOOK-lean.md`.

**Other abbreviations.**
- **RS**: `RUN_STATE.md`.
- **DL**: `docs/decision_log.md`.
- **CARE**: the care audit, `docs/run_reports/2026-11-06-b5-care-audit.md`.
- **Entry numbers** (DLE-0, DLE-1, ...) are the care audit's numbers for its drafts.

## Signing statement for DLE-0, DLE-1 and DLE-2

Each of these entries carries the following statement verbatim, made by the signer at signing:

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

Signer: the block-5 lead (Opus), 2026-11-06. The rulings were made blind and are recorded verbatim in the build brief
of branch `lane/2026-11-06-b5-lean-release`.

---

## DLE-0. PLAN step 12, the results cold gate

- **Status.** ADOPTED, 2026-11-06. This entry records a decision made earlier.
- **Original rule.** PLAN line 172, §3.1, step 12: "Results cold gate: re-derive every printed number from the
  artifacts of steps 3–11 | judge + refuter | gate record".
- **Change.** Step 12 is replaced by the independent recompute agreeing with L9 within the blind-fixed bars. The
  recompute is `scripts/independent_recompute_b5.py`. The comparator is `scripts/compare_b5_recompute.py`. The bars
  are in `configs/analysis/b5/recompute_bars.json`.
  - This was decided blind on 2026-10-14, before any block-5 number existed. RS line 64, item 37 (ii): "the release
    condition is the blind dry run passing plus the independent recompute agreeing with L9 within a tolerance fixed
    before release, with no separate cold gate".
  - The bars were bound to block 5's release blind (RS line 340, item 83, ruling 1).
  - Until now the change had not been entered against the plan. This entry does that.
- **Rationale.**
  - The cold gate re-derives the printed numbers by hand, with a judge and a refuter.
  - The recompute re-derives them from the raw power records in separate code (standard library only, sharing no code
    with L9). It is compared leaf by leaf against L9's outputs, with bars fixed before any value was seen.
  - That is a stronger and reproducible check of the same thing.
- **Effect on estimands.** None. No estimand, estimator, decision rule, threshold or reported quantity changes. Only
  the way the printed numbers are checked changes.
- **Coverage limit, recorded so that it is not forgotten.** The recompute does not re-derive every quantity the plan
  prints. The gaps are in `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md` §2, mostly §8 disclosure lines: monitor cost, arm
  and host summaries, battery phase and temperature lines, the full reference and attempt history, and G10.
  - RS item 83, ruling 3, already requires the post-release reader to check by hand, against the recompute's
    restricted output, any uncovered leaf the paper prints.
  - For a quantity the recompute does not compute, that hand check needs another source, which that audit names.
  - DLE-0 does not widen what the release condition checks. It only names what step 12 is replaced by.

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

---

## DLE-1. The release run

- **Status.** ADOPTED, 2026-11-06.
- **Original rule.** PLAN lines 194-195, §3.2, item 2: "**After the release**, the analysis re-runs steps 1–11 from
  identical bytes at the pinned commit; every output digest must equal the dry run's. A mismatch stops the analysis
  and goes to R3 as a determinism defect." The implementation is the `release` mode of `dry_run.py` (lines 2006-2027
  and 2076-2087).
- **Change.** The release no longer re-runs steps 1-11. It is the following three stages, implemented as
  `scripts/release_b5.py`.
  1. **(a) Digest re-verification.** Re-verify every output digest held in the dry-run record
     (`dry-run/B5-BLIND-DRY-RUN-RECORD.json`) against the dry-run custody and the pinned commit.
     - The record must be a completed blind dry run at the pinned commit.
     - Its sealed digests must equal `seal_pins.json` at that commit.
     - Its window-index digest must equal the index given.
     - Every step output must hash to its recorded digest. It is read under `dry-run/restricted/` without following a
       symbolic link.
     - Every input-census row must hash to its recorded digest at the indexed roots, using L9's own mapping
       (`_released_input_difference`).
     - Any mismatch refuses with `release_digest_differs_from_dry_run`.
  2. **(b) Independent recompute.** Run `scripts/independent_recompute_b5.py` on the indexed roots, with
     `--member-detail --workers N`.
  3. **(c) Comparator.** Run `scripts/compare_b5_recompute.py` against the dry-run custody, with the release bar set.
     That set is `configs/analysis/b5/recompute_bars.json`, the set RS item 83, ruling 1 bound blind. It is pinned by
     SHA-256 in `release_b5.py`; other bars refuse.

  The release condition is all of: (a) verified, the recompute exiting 0 with `comparison_stopped` false, and the
  comparator exiting 0 (every family passes, nothing unmapped, no absent or non-finite step-11 output). There is no
  second heavy run. A full heavy re-run may still be done as audit work; it gates nothing.
- **Rationale.**
  - The re-run checks two things: that deterministic code is deterministic, and that the dry-run outputs were not
    altered.
  - Determinism is already shown. D-188 calls the code deterministic (DL:12244). Candidate 1 (dry-h) compared
    EQUIVALENT to attempt E across inputs, decisions, and the registered and intermediate tiers.
  - Custody integrity is what the digest re-verification checks, directly and in seconds.
  - Agreement of an independent program is a stronger check than the program replaying itself.
  - The saving is one full heavy run per block (136-152 min on r2 dry-j; CARE row 1). It also saves a rerun for every
    tooling refusal on the release path.
- **Effect on estimands.** None. No estimand, estimator, decision rule, threshold or reported quantity changes. The
  numbers that print are the dry run's L9 outputs, which (a) verifies byte for byte. Only how they are verified at
  the release changes.
- **Coverage gap, accepted for block 5 only.** Seven registered families are not independently recomputed, so
  stage (c) does not check them. They are `LEAN-COVERAGE-AUDIT.md` §2 items 1-7:
  1. monitor cost;
  2. arm hazards (arm/host and anchor summaries);
  3. battery (phase and subject summaries, discharged energies);
  4. battery temperature (the stage thermistor disclosure);
  5. reference, corpus and NEG-8 history;
  6. attempt history (all attempts, yield, G10);
  7. selection (and full eligibility adjudication).

  For block 5 these lines are covered by two things, and only by them:
  - stage (a)'s byte verification of the L9 dry-run outputs that print them. This proves the bytes are the ones
    the dry run produced (integrity); it does not prove the arithmetic (correctness);
  - RS item 83, ruling 3: the post-release reader checks each such leaf the paper prints by hand, against the
    source the audit names, before it enters the paper.

  A comparator `agree` therefore says nothing about these seven families. Adding them to the lean program is
  required before the lean path becomes production for block 6 (DLE-2, "Coverage before block-6 production").
- **What is not changed.**
  - PLAN §3.2 item 3 (repairs after the release) stands.
  - The R3 loop for tooling refusals stands.
  - Unsealing is a separate step, after (a)-(c) agree, and needs Ed's OK. `release_b5.py` prints only a blinded
    verdict: agree or hold per family with counts, and structure codes. It unseals nothing.

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

---

## DLE-2. The production program for blocks 6 onward

- **Status.** ADOPTED, 2026-11-06.
- **Original rule.**
  - PLAN lines 159-172 (§3.1, the steps table) and §11 (lines 736-757): lane L9's programs produce the registered
    numbers.
  - Block 6 is analysed "with block 5's registered arithmetic unchanged" (RS line 64, item 37).
  - Block 6's registration changes only by a dated §17 entry checked by one executing refuter
    (`docs/registrations/block6_replication_DRAFT.md` lines 19 and 1171).
- **Change.**
  1. For blocks 6 onward, the lean recompute (`scripts/independent_recompute_b5.py`, with its member pool) is the
     production path.
  2. The collection-time input judgments are bound by content hash to the harvest record (the step-0 census), not
     re-derived. They are: the clock anchors (m, s), the calibration fits (b_pre, b_post), the exclusions and the
     NEG-8 record. This is D-188 item 2 (DL:12245) applied to them, and ED-RULING item 6, option (b).
  3. The heavy L9 pipeline runs once per block as an audit, off the critical path, with fewer workers. It never gates
     a release unless it disagrees.
  4. **Disagreement rule, as drafted in CARE §2.5 item 3.** Any family outside its bar holds the release. A blind seat
     traces it, structure only. Which side prints is decided by the defect found, never by the value.
- **Rationale.**
  - The arithmetic is the same, wall time is 20-30 times less, and the code is separate.
  - Re-deriving deterministic collection-time judgments on every run protects against nothing that hash binding does
    not. D-161 (DL:207) says the threat model is "tamper-EVIDENT … not tamper-PROOF".
  - The heavy pipeline's full strict re-derivation is kept, as the audit.
- **Effect on estimands.** None. No estimand, estimator, decision rule or threshold changes. Block 5's registered
  arithmetic is unchanged for block 6. Only the program that produces the numbers changes.
- **Conditions and follow-ups.**
  - **Block-6 registration.** Block 6's registration file must carry this change as a dated §17 entry, checked by
    one executing refuter, by its own rule. That entry is owed. This log does not edit the block-6 draft.
  - **Coverage before block-6 production.** As a production path, the recompute must print every quantity the
    block-6 analysis plan registers.
    - The quantities it does not compute today are in `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md` §2: monitor cost,
      arm and host summaries, battery phase, subject and temperature lines, and the full reference, attempt and G10
      history.
    - Each must either be added to the lean program or be named in the block-6 plan as supplied by the heavy audit
      run.
    - Until then, those lines come from the audit run.
  - **Agreement gate.** Before the lean path is production for block 6, CARE §2.5 item 1 must hold. That is exit 0
    on the block-5 dry-run custody (DLE-1 stage (c)), with every family agreeing and 0 unmapped, and again on the
    first counting block-6 session.
  - **Ties at thresholds.** The comparator's half of the tie rule is the FS3 rule (RS lines 589-602). The paper's half
    is the lead's FS3 note.
- Block-6 sessions must also be blinded at signing.
- **Open review points for the lead, before block-6 activation (not rulings; recorded 2026-11-06 from a skeptical
  methods critique, cloud Sol `sol/burn-dle`, checked by the lean-release lane).**
  - The rationale above says re-deriving collection-time judgments "protects against nothing that hash binding does
    not". That holds for re-running the same deterministic code. It does not hold for the first derivation: a wrong
    anchor, fit or verdict on unchanged bytes is caught only by a re-derivation, which under this entry is the heavy
    audit run. The audit run is therefore the only check of those judgments for block 6.
  - Because the audit is off the critical path, the entry should say what happens if it has not finished when the
    block-6 numbers would be released: hold, or release labelled provisional pending the audit. Its disagreement
    surface should include the strict refusal set, not only the comparator families.
  - Neither point applies to block 5: the block-5 dry run is the full heavy pipeline, strict step 1 included, and
    DLE-1 verifies its outputs byte for byte.

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

---

## Not adopted for now: CARE drafts DLE-3, DLE-4 and DLE-5 (lead, 2026-11-06)

These are CARE §4's drafts. Their numbers are the care audit's draft numbers, not this log's entry numbers; the
log's own DLE-3 (2026-11-07, below) is a different entry.
- **DLE-3**: step-1 strict validation by hash binding.
- **DLE-4**: memoizing or hash-binding the 3b candidate refits.
- **DLE-5**: dropping the 120 s analysis-path wall deadline.

Under DLE-2 the heavy pipeline is off the critical path. So it keeps its full strict re-derivation, as the audit.
The PLAN rules these drafts would have changed stand as written. Engineering-only speedups, which change no
registered number, decision or refusal position, continue on `lane/2026-11-06-b5-under-90`.

---

## Signing statement for DLE-3

DLE-3 carries the following statement verbatim, made by the signer at signing:

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

Signer: the block-5 lead (Opus), 2026-11-07. The rulings were made blind and are recorded in the assembly brief of
branch `lane/2026-11-07-b5-analysis-r3`. Every finding below comes from a structure-only trace: type pairs, counts,
leaf paths, status and reason words, and code reading. No energy value, interval, outcome word of a real contrast or
other outcome-bearing content was seen by the tracer, the assembler or the lead.

---

## DLE-3. Analysis version r3: release-hold fixes (D1-D4, D6), floor binding refusal label (D5b), and the D-188 engineering

- **Status.** ADOPTED, 2026-11-07, on `lane/2026-11-07-b5-analysis-r3`. Supersedes the analysis commit
  `b5/analysis-r2` (`929fc65c9`) for the block-5 dry run and release; the new commit is tagged `b5/analysis-r3`
  after merge (the cited rebind of the analysis pin: `scripts/release_b5.py` takes the pinned commit as an
  argument, so the rebind is the tag and the re-run, not a hash in the tree).
- **Source.** The release-hold blind trace, `docs/run_reports/2026-11-07-b5-release-hold-trace.md` (rounds 1 and 2,
  branch `lane/2026-11-07-b5-release-trace`). Its probes print only counts and status or reason words; the lead
  ruled floor-resolution status and reason words structural.

### Changes that change L9 output (not result-equal to r2)

1. **D1, the L9 key bug (plan §8.2).**
   - **Original rule.** PLAN §8.2 (lines 658-659): "The row also says whether the battery term was available."
   - **Defect.** `joulewise/b5_analysis/disclosures.py` `machine_member` read `machine.battery_available`. The meter
     record names the field `battery_term_available` (`joulewise/external/km003c_parse.py`
     `delta_machine_energy`). Every `machine_member` line printed null for the flag. The L9 test fixture used the same
     wrong key, which hid it.
   - **Rows affected.** 346 `battery_term` comparator rows on the r2 dry run (trace §2, class null/bool), plus 2
     shared with D3. The record itself was right; only the printed line was wrong.
   - **Change.** Read `battery_term_available`; correct the fixture. Commit `9c51ce2d0`, failing-first test
     `tests/b5_analysis/test_disclosures.py` `test_T8_T20_B8_meter_all_members`.
   - **Effect on estimands.** None. The line now prints what the plan registers. No number, decision or refusal
     position changes.
2. **D5b, the floor binding refusal label (plan §7.2 step 1).**
   - **Original rule.** PLAN §7.2 step 1 (lines 419-422) registers `floor_artifact_invalid` as `not_estimable`.
     PLAN §7.2 step 2 makes `floor_transport_inapplicable` `not_resolvable`, a registered scientific outcome.
   - **Defect.** `_floor_engine_reasons` (`joulewise/analysis_engine/__init__.py`) mapped every floor-resolution
     code it did not list to `floor_transport_inapplicable`. That included `artifact_schema_invalid`, the engine
     wrapper's refusal when the claim-side floor-evidence binding has problems (trace round 2, "D5: what
     `artifact_schema_invalid` means here"), and the selected-cell and transport-group refusals in
     `analysis_engine/inputs.py` that use the same word for a cell or group outside the externally verified
     artifact contract. A binding failure is neither an inapplicable transport nor an outcome.
   - **Change (lead ruling).** Map `artifact_schema_invalid` to `floor_artifact_invalid`. Every other mapping is
     unchanged, including the binding codes that ride beside the bare word. Failing-first test
     `tests/test_analysis_integration.py`
     `test_floor_binding_refusal_maps_to_floor_artifact_invalid` (resolution reasons, and the claim outcome
     `not_estimable`).
   - **Consumer check.** `analyze_claims` is called by `joulewise/cli.py` (`analyze-claims`), the block-5 claim
     replay in `joulewise/paper_custody.py`, and `joulewise/b5_analysis/phase_timing.py` (timing only).
     `joulewise/dominance_closeout.py` imports only `AnalysisInputError` and input helpers; `joulewise/twins/engine_twin.py`
     keeps its own outcome sets and maps no floor resolution. No tracked claim-verdicts record, rehearsal fixture,
     report table or site page carries `floor_transport_inapplicable` or a refused `artifact_schema_invalid`
     resolution (the two `docs/paper/fill-rehearsal/*-claim-verdicts.json` records resolve every floor; the
     `analysis/rpt001-*` records are void placeholders not produced by the engine). No published or frozen result
     changes. The one real-data output it changes is the unreleased r2 dry run's GAMMA claim verdicts (the 4
     refused resolutions of trace round 2), which the r3 dry run replaces.
   - **What D5b does not decide.** Which binding check refused (trace D5, `probe_d5_binding.py`) is still open. If
     the binder is wrong for registered inputs, that is a further L9 fix; if a floor member genuinely fails
     registered authentication, it is R3 (PLAN §3.1, "Refusals"). D5b only stops a tooling-class refusal from
     printing as a scientific `not_resolvable`.
   - **Step 9b.** Unchanged: its non-issuance follows the refused resolution status, not the reason word.

### Changes that do not change L9 output (result-equal to r2)

3. **Speed, robust and step-3b prefetch engineering under D-188** (DL:12239; merged from
   `lane/2026-11-07-b5-r3-speed-fix` at `03bc58477`).
   - **Content.** Parallel pack brackets, issuer staging, sensitivity packs and producer preparation; the ordered
     bulk source census; L4 bracket-fill storability; the candidate-refit memo and prefetch; Student-t quantile memo;
     reserved-key location formatting; step checkpoints, `--resume`, serial step retries and closed refusals on a
     malformed checkpoint; the step-4 speculative-file cleanup, L3 expiry, bracket snapshot normalization and G9
     sidecar predicate; registered step-11 tooling refusal codes; and fix `70d32a878`, the step-3b prefetch refitting
     only the rows discovery authenticates (it had refitted 141 rows too many).
   - **Equivalence evidence.** On real data, the blinded D-188 comparator (`tools/b5_equivalence/compare_b5_results.py`,
     #643) found the r2 rewrite EQUIVALENT to the r1 reference (RS item 165; the final dry-j against dry-i comparison
     per the lead). On the full synthetic chain (steps 0-11), the speed-fix head is EQUAL to r2: the same record
     sha256 `dfd1f5b9...49b7f8` and 1,540 of 1,543 custody files identical, the other three being timing logs
     (`docs/run_reports/2026-11-07-b5-robust-fullchain.md`).
   - **Effect on estimands.** None, by D-188's result-equivalence rule.
4. **Release-tooling fixes, D2, D3, D4 and D6** (merged from `lane/2026-11-07-b5-release-trace` at `36e79f13a`).
   These change the independent recompute and the comparator (DLE-0, DLE-1 stages (b) and (c)), never L9.
   - **D2.** `scripts/independent_recompute_b5.py` subtracted idle attempt 1's power where the controller had kept a
     re-measured baseline; it now reads the kept attempt and flags a missing file (33 members, confirmed 33 of 33 by
     the probe).
   - **D3.** The recompute left out two succeeded members whose clock anchor did not resolve; it now re-derives
     their descriptive row from the controller stamps and the bundle trace (`descriptive_unanchored`).
   - **D4.** The recompute listed nine members aborted at idle admission as null members; they now go to
     `no_measured_request`.
   - **D6.** `scripts/compare_b5_recompute.py` compared BETA's two NEG-8 survivor terms unconditionally; it now
     compares them only when the record's protocol carries them (condition `neg8_survivor_terms`).
   - **Effect on estimands.** None. The bars (`configs/analysis/b5/recompute_bars.json`) are unchanged.

- **Cited rebinds under this entry.**
  - `joulewise/calibration_bracketing.py` (frozen, seal pin4): edited in place by the under-90 round 2 memo
    (`13af1baa8`). `tests/b5_analysis/test_frozen_files.py` keeps the freeze on the accepted analysis commit's bytes
    (`EVOLVED_ON_MAIN`, with the citation), and now also pins the working-tree bytes of the rebound file
    (`REBOUND_WORKING_TREE`, sha256 `40fd34bb...a1f2`). A further edit therefore fails until it carries its own
    cited rebind. `tests/test_whole_window_inverted_corner_clamp.py`
    `FROZEN_FILES_TEST_SHA256` is rebound to the edited `test_frozen_files.py`, and
    `tests/b5_analysis/test_vdl_sol_w2.py` lists `CANDIDATE_PHYSICS_MEMO` as a reviewed memo. Both cite DLE-3.
  - `configs/gates/hazard_refusals.json` lists `calibration_ledger.custody_probe_code`'s raise (`ae558a914`) as
    INTERNAL: its only caller catches it, and the effect is that an L4 fill is not stored.
  - `joulewise/b5_analysis/disclosures.py` and `joulewise/analysis_engine/__init__.py` carry no hash pin in the
    tree. Their pin is the analysis commit (the tag above). Two integration tests that pinned the old D5b label
    now expect `not_estimable` and `floor_artifact_invalid`.
- **What follows.** The block-5 dry run re-runs at `b5/analysis-r3` (D1 changes the step-11 disclosure, D5b the
  step-9 claim verdicts). The r2 dry run is not released.
- **r3 is not releasable until D5 is answered (release condition, binding).**
  - DLE-1's release stages do not run against an r3 dry run until two things have happened:
    - the D5 binder cause has been answered, by `probe_d5_binding.py` or an equivalent structure-only probe;
    - its fix has landed: an L9 fix with a cited rebind if a binder check is wrong for registered inputs, or an
      R3 producer cure if a floor member genuinely fails registered authentication (PLAN §3.1, §3.2 item 1).
  - The comparator's D5 rows (`floor_gate_j`, the floor and outcome leaves of the GAMMA contrasts) are not
    waivable under DLE-1. A hold on them is a hold.
  - **D5b changes only the label.** A binding refusal now prints `floor_artifact_invalid` (`not_estimable`)
    instead of `floor_transport_inapplicable` (`not_resolvable`). It does not reclassify the refusal as tooling.
  - **What the dry run does today with a GAMMA floor-binding refusal** (checked in
    `joulewise/b5_analysis/dry_run.py`):
    - step 9 (`analyze-claims`) exits 0 and is `ok`;
    - step 9b finds the refused resolution (`_first_condition_is_outcome`: status outside `exact`/`transported`)
      and exits `CLAIM_SIDE_BOUND_NOT_ISSUABLE_EXIT` = 3. That is the D-189 non-stopping `outcome_class` row;
    - `completed_without_tooling_refusal` stays true, and `_record_exit` returns **3**, the outcome-class exit,
      not 0;
    - the same holds before and after D5b.
  - **Reviewer disagreement, settled.** One review of PR #693 said the driver exits 0; the other said 3. The code
    gives 3: `_record_exit` returns 3 whenever any step row is `outcome_class`, and step 9b's row is.
  - **Today's only stop is the release comparator.** Nothing in the dry run marks the refusal as tooling, so the
    stop is the comparator: the D5 floor rows DISAGREE (L9 null against the recompute's number), and any family
    disagreement is `comparator_disagreement` in `scripts/release_b5.py`. That stop and this release condition
    together hold r3. An exit 3 must not be read as §3.2 completion while D5 is open.

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

---

## Signing statement for DLE-4

DLE-4 carries the following statement verbatim, made by the signer at signing:

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

Signer: the block-5 lead (Opus), 2026-11-07. The cause was found blind. The lead ran structure-only probes of the r3
dry run's floor binding: key names of campaign-log rows, row and id counts, and status and reason enum words. No
energy value, interval, outcome word of a real contrast or other outcome-bearing content was seen by the lead or by
the fixing seat, which worked on synthetic data only.

---

## DLE-4. Analysis version r4: the D5 cause, an L9 campaign-log member parse

- **Status.** ADOPTED, 2026-11-07, on `lane/2026-11-07-b5-analysis-r4`. Supersedes the analysis commit
  `b5/analysis-r3` (`68e47e1f2`) for the block-5 dry run and release. The new commit is tagged `b5/analysis-r4`
  after merge. As under DLE-3, the cited rebind of the analysis pin is the tag and the re-run, not a hash in the tree.
- **Source.** The lead's structure-only probes of the r3 dry run, which follow up the D5 section of the release-hold
  trace (`docs/run_reports/2026-11-07-b5-release-hold-trace.md`). What they found:
  - **The four cells.** All four GAMMA floor cells, `d117-qwen3-{1p7b,8b}-{decode,prefill-p2048}-floor-v5`, are left
    out of `bound_cell_ids`.
  - **The problems.** Eight global binding problems do it, one per cell and component:
    `component_evidence_root_disagreement: cells[i].provenance.{absolute,comparative}.campaign_log does not bind
    every calibration bundle exactly once`.
  - **What passes.** The order-manifest checks (member order and the A/B/B/A blocks) and the sha256 pins all pass.
  - **The log.** Each campaign log has 261 rows. Grouped by key set:
    - 9 campaign verdict rows;
    - 144 provenance attestation rows;
    - 104-105 executed-member rows (`status` ok);
    - 2-3 refused-member rows (`status` failed, with run ids outside the cells);
    - one campaign-level whole-window evaluation row, whose `bundle_ids` lists the campaign's bundles.
  - **The count.** The binder's parse finds 107 distinct ids and 211-212 in total. Every cell member has count 2:
    one executed-member row and the evaluation row.

### Changes that change L9 output (not result-equal to r3)

1. **D5, the campaign-log member parse (plan §3.1 step 9, §7.2 step 1).**
   - **Original rule.** PLAN §3.1 step 9: the claim gate runs "one `--evidence-root` per floor pack". The step that
     reads an output authenticates it (§3.1, lines 155-156). PLAN §7.2 step 1 makes a floor that fails that
     authentication `floor_artifact_invalid` (`not_estimable`). PLAN §3.1 "Refusals": a tooling refusal goes to R3.
   - **Defect: L9 is the wrong side.** The floor binder reads the executed member order of each component's
     `campaign_log.jsonl` with `_order_member_ids` (`joulewise/analysis_engine/inputs.py`). For every row, that
     function counted the `bundle_ids` list, or else `bundle_id` or `run_id`. It did not tell the runner's
     per-member rows from campaign-level records.
     - The runner (`scripts/run_campaign.py`) writes per-member rows with `log_row`, which never sets `record_type`.
     - It writes its in-runner whole-window evaluation with `record_type`
       `idle_admission_whole_window_verdict` and `bundle_ids` = the campaign's members.
     - So that row named every calibration bundle a second time, and the "exactly once" check refused every cell
       of the artifact.
     - The registered input is not at fault. The mint's component authentication reads the same log bytes
       (`scripts/mint_floor_artifact.py` `_authenticate_component`, called by the generalized mint) and requires the
       log to hold exactly one evaluation basis, which is the one this row carries. The mint therefore accepted what
       the binder refused: two readers in the analysis chain (the step-5 mint and the step-9 binder) disagreed on
       the same registered bytes. The floor members did not fail
       registered authentication, so this is an L9 fix, not an R3 producer cure.
   - **Why the tests missed it.** The synthetic S10 chain's logs have the other shape. Its windows' members are
     cloned, not run by the runner, so its claim-window logs hold no per-member row at all: only provenance
     attestations and the whole-window evaluation. There the evaluation's `bundle_ids` is the only row naming the
     members, each once, so the old parse bound them. The binder's unit fixtures hold only member rows. No test had
     both kinds of row in one log, as the runner writes it.
   - **Change.** In the campaign-log branch, `_order_member_ids` now reads the executed order from the log's
     executed-member rows whenever the log has any: rows with no `record_type` that name an id (`bundle_ids`, or else
     `bundle_id` or `run_id`, extracted as before). Every row with a `record_type` is then ignored.
     - **A log with no member row keeps the previous parse of every row, unchanged.** That is the synthetic S10
       shape. The first version of this fix (`cf42f2a98`) skipped `record_type` rows unconditionally. The full
       synthetic chain then refused all four synthetic GAMMA floor resolutions (`artifact_schema_invalid`; step 9b
       `outcome_class`, exit 3), so the fallback was added in `7e6ba73b2`.
     - **Why `record_type` and not a structural rule.** In the writer's schema, every campaign-level record carries
       a `record_type`: the evaluation row, `campaign_verdict`, `campaign_stop`, `shakedown_gate`, the provenance
       attestation and `campaign_occurrence_supersession`. No member row carries one. So the field decides it
       exactly.
       - A structural rule (rows with `run_id`, `run_index` and `executed_order`) would also drop member rows the
         runner writes without an order entry (`config_error` rows, `block_order_warning` rows).
     - **What is unchanged.**
       - Failed, refused, timed-out, blocked and drained member rows still count as executed attempts. They are
         `log_row` rows.
       - The "exactly once", order and contiguous A/B/B/A checks are as strict as before, in both modes.
       - The order-manifest branch is unchanged.
     - **Commits and tests.** Commits `cf42f2a98` and `7e6ba73b2`, with failing-first tests in commit `cb2498c2a`:
       - `tests/test_analysis_engine_campaign_log_members.py`, on a synthetic log of the probed shape. It binds after
         the fix. Before the fix it refused with the probed problem words, one per component.
         - A duplicate executed-member row still refuses.
         - A failed attempt on a cell member still counts.
         - An attestations-plus-evaluation log (the S10 shape) binds both before and after the fix. A second
           evaluation row in it still refuses.
       - The CLI binding fixture in `tests/test_analysis_integration.py`, whose evidence-root logs gain the
         campaign-level rows. With production identity, every cell binds after the fix; before it, none did.
   - **Effect on estimands.** None. No estimand, estimator, decision rule or threshold changes.
     - The binder now reads the registered campaign evidence as the runner wrote it.
     - On the block-5 dry run, the GAMMA floor cells can bind. A GAMMA contrast's floor then resolves through the
       registered §7.2 path, instead of refusing with `floor_artifact_invalid` (after DLE-3's D5b label;
       `floor_transport_inapplicable` before it).
     - Which outcome follows is not known to the lead and is not part of this ruling.
   - **Consumer check.** `_order_member_ids` has one caller, `_campaign_order_binding_problems`, inside
     `bind_floor_artifact_evidence`. Every floor binding goes through it: the claim gate (`analyze-claims`), the
     block-5 claim replay in `joulewise/paper_custody.py` and the dry run's step 9. The mint's own
     `bind_floor_artifact_evidence` (`scripts/mint_floor_artifact.py`) is a separate function: it checks the log's
     sha256 and reads no member order from it.
     - Two kinds of log parse exactly as before: a log with no executed-member row, and a log whose
       campaign-level rows name no id (no `bundle_ids`, `bundle_id` or `run_id`).
     - A log in the probed shape used to refuse every floor cell and now binds. No tracked claim-verdicts record
       carries a refused floor resolution (DLE-3's consumer check), so no published or frozen result changes.
     - The one real-data output it changes is the unreleased r3 dry run's GAMMA claim verdicts, which the r4 dry
       run replaces.
   - **Independence of the recompute.** `scripts/independent_recompute_b5.py` (stdlib only, no `joulewise` import)
     reads no campaign log and no order manifest. It takes the armwise maximum of the per-model floor cells directly,
     with no binding admission. So it shares neither this parse nor its defect.

### Observability note (no change)

`component_evidence_root_disagreement` is not one of the ten surfaced floor binding codes
(`_FLOOR_BINDING_REASON_CODES`, `joulewise/analysis_engine/inputs.py`). So the engine wrapper's refusal for D5 was
the bare `artifact_schema_invalid` with no binding code beside it, and the cause had to be found by a probe that
replays the binder. The vocabulary is left unchanged here: adding a code changes the claim artifact's public reason
set, which is a separate ruling. This note records the gap.

### Rebind and release condition

- **Cited rebinds under this entry.** `joulewise/analysis_engine/inputs.py` has no hash pin in the tree. The hazard
  refusal census lists it as `not_scanned`, class `analysis` (`configs/gates/hazard_refusals.json`); that is
  unchanged. Its pin is the
  analysis commit (the tag above). No frozen file is touched.
- **The D5 release condition of DLE-3 is satisfied.**
  - **The cause is answered** by the lead's structure-only probe, above.
  - **Its fix has landed** as an L9 fix with a cited rebind (this entry), once merged and tagged.
  - **What r4 still needs before DLE-1's stages run against it.** The block-5 dry run re-runs at `b5/analysis-r4`.
    The comparator's D5 rows (`floor_gate_j`, and the floor and outcome leaves of the GAMMA contrasts) stay not
    waivable. If they still disagree on the r4 dry run, that is a new hold, traced structure only.
  - **Checks first reached on real data.** On the r3 dry run the "exactly once" check broke out of the campaign-log
    loop first, so the log's own member-order and contiguous A/B/B/A checks have never run on these logs. They run
    at r4. The member rows carry their order-manifest `run_index`, and the order manifest passes the same checks, so
    they are expected to pass, but this is not yet shown. A refusal there would be a new D5 finding, not covered by
    this entry.
  - The r3 dry run is not released.

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

## Signing statement for DLE-5

DLE-5 carries the following statement verbatim, made by the signer at signing:

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

Signer: the block-5 lead (Opus), <date>. Found by code reading and synthetic tests only (PR #701 and its
executing review); no block-5 data was read.

---

## DLE-5. BYTES lineage landing: cited in-place rebind of five frozen collection files and two extractor modules

(This is this log's own DLE-5, not the CARE draft of the same number listed above as not adopted.)

- **Status.** ADOPTED, <date>, with the merge of PR #701 (`lane/2026-11-07-bytes-stage1` into `main`). It changes
  no L9 output (result-equal to r4) on block-5 windows. The analysis pin is unchanged: `b5/analysis-r4` is tagged
  on a commit before this merge. Any later analysis tag that includes this merge is re-run through the D-188
  comparator before release (DLE-1 stages (b) and (c)).
- **Source.** The block-6 and BYTES collection lane (`lane/2026-10-28-bytes-pass2-open` @ `ee4ce93fc`,
  BY-THERM-LINES `4e29114ea`) edited these files in place for block 6. They land on `main` with this merge.
- **Frozen files rebound** (`tests/b5_analysis/test_frozen_files.py`: `EVOLVED_ON_MAIN`, `REBOUND_WORKING_TREE`,
  `FROZEN_FILES_TEST_SHA256`):
  1. `joulewise/flags/catalog.py`: 17 block-6 DRAFT codes and the DISCLOSE code
     `records.claim_usable_counting_disagreement`. The sealed block-5 catalog is unchanged, and no block-5 writer
     emits any of them.
  2. `joulewise/flags/core.py`: 11 block-6 core codes (`agent.pause_marker_stale`, `sleep.*`, `idle.*`) and
     `calibration.acceptance_preflight_unverified`. Their only writers are block-6 lane code; none exists at any
     block-5 window's pinned commit.
  3. `joulewise/flags/exclusions.py`: `compute(..., *, pack_scoped=True)`, which keeps the default behaviour.
     `cell.below_minimum` is now added only when the catalog in force maps it to `EXCLUDE_WINDOW`; the sealed
     block-5 catalog does, so block-5 behaviour is identical.
  4. `scripts/run_campaign.py`: block-6 HAZARD collection hooks (pause marker, run clock and sleep flags, idle-wait
     member cap, `StorageStop` exit 2). On the analysis path:
     - `_final_idle_admission_attempt` accepts consecutive `[1..k]`; the block-5 controller wrote at most `[1, 2]`.
     - The busy-fraction admission exception is gated on `busy_fraction_admitted`. Its only writer is
       `joulewise/controller.py` `_wait_hazard_idle`, added on the lane in `a1b2b59c3` (2026-10-14) and absent from
       `main`, so no block-5 bundle carries it.
     - `core_passed` in the whole-window verdict is rewritten through `_idle_admission_claim_barrier_reasons`; it is
       equivalent on every input that lacks `final_admission_attempt`.
  5. `scripts/harvest_b5_window.py`: `StorageStop` exits with code 3. It is reachable only from a compressed-archive
     restore; block-5 archives are plain.
- **Step-4 extractor modules (not frozen, census-pinned).**
  6. `joulewise/environment_admission.py`: adds `busy_fraction_admission_admitted`, which waives
     `environment_admission_failed` and the core CPU failure for an explicit controller busy-fraction admission.
     It is unreachable on block-5 data for the reason in item 4. The step-4 reason census gains `busy_fraction_admitted`
     and `compression_records` in `tooling` (`configs/analysis/b5/step4_reason_classes.json` regenerated). No mask
     or R3 code changes and the step-4 rule is unchanged.
  7. `joulewise/whole_window.py`: the lane's compressed-archive restore wraps main's `_prepare` body
     (`readable_run` yields a plain directory unchanged). The whole-window verdict now reads a non-admitted member's
     `metadata.json` before deciding; the decision is unchanged on block-5 data.
- **Scope of "inert".** Inert for the analysis of collected block-5 windows. Block-5 collection is closed. A new
  collection from block-5 configs on `main` would differ: `block_id` is logged in `executed_order`, the HAZARD
  idle wait replaces the one retry, and run-clock records are written.
- **Release condition.** None beyond DLE-1, provided `b5/analysis-r4` is tagged before this merge. Otherwise the
  D-188 comparator is re-run at the tag that includes it, and any disagreement is a hold.

- **Review caveats and the census change (executing review of PR #701).**
  1. `block_id` is logged by new collections, so "inert" holds for the analysis of collected windows, not for
     re-collecting a block-5 config on post-merge `main`.
  2. `whole_window`'s merged verdict reads the bundle's `metadata.json` for every non-admitted member before
     deciding; the decision is the same and only the reads are added.
  3. Merge order: tag `b5/analysis-r4` before this merge, or re-run the D-188 comparator at a tag that includes the
     lineage.
  4. The CI-fallout respelling of `busy_fraction_admitted` and `compression_records` (`373471bbf`) was removed:
     the plain literals are restored and `configs/analysis/b5/step4_reason_classes.json` is regenerated with
     `tests/b5_analysis/step4_reasons/make_table.py` (plus `RULING`). The only diff is the two literals, both in
     `tooling`; the mask list, the R3 codes and the step-4 rule are unchanged. The respelling had hidden an
     admission-relaxing path (`busy_fraction_admission_admitted`) from the census.
