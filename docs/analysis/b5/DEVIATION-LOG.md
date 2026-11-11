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
log's own DLE-3, DLE-4 and DLE-5 (2026-11-07, below) are different entries.
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

---

## Signing statement for DLE-5

DLE-5 carries the following statement verbatim, made by the signer at signing:

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

Signer: the block-5 lead (Opus), 2026-11-07. The gap was found blind, at the r4 release check: the lead read only
the comparator's public line (per-family pass and fail counts, `step11_unmapped` count) and the unmapped leaf paths,
with `*` for each list item and each floor cell id as printed. No energy value, interval, outcome word of a real
contrast or other outcome-bearing content was seen by the lead or by the fixing seat, which read code and the
registration and worked on synthetic fixtures only.

---

## DLE-5. Release tooling: the comparator maps the GAMMA attribution-floor leaves of the fill

- **Status.** ADOPTED, 2026-11-07, on `lane/2026-11-07-b5-cmp-floor-leaves`. A tooling coverage fix in the
  comparator (`scripts/compare_b5_recompute.py`, DLE-1 stage (c)). It changes no L9 output and no recompute output:
  the analysis commit stays `b5/analysis-r4` (`ab1e0098d`) and `scripts/independent_recompute_b5.py` is unchanged
  (its program digest too). The release script runs the committed comparator at HEAD, so the fix takes effect when
  the release check re-runs after merge; no analysis pin is rebound.
- **Source.** The r4 release check. The r4 dry run exits 0; every result family of the comparison is AGREE with no
  failing row; the comparator refuses `step11_unmapped_fill` with 84 unmapped leaves, all of the attribution-floor
  metadata, printed now that DLE-4 lets the GAMMA floors resolve. Before r4 those floors were refused, so no fill
  carried these leaves and no rule had met them.

### The gap

- **Original rule.** DLE-1 stage (c) and the comparator's step-11 coverage (RC-CMP-3 X1, RC-CMP-5 S1, RC-CMP-6 G5):
  every leaf of the fill and of the disclosure record is either a copy of an agreeing compared row or named by an
  exemption; a leaf no rule matches refuses the run. That rule is right and is kept.
- **What the producers print.** When a GAMMA contrast's floor resolves and one of its source cells is
  attribution-limited (D-078: the admissible-set uncertainty of a form dominates its guarded point floor;
  `joulewise/detection_floor.py` `_add_attribution_limit_metadata`), the claim verdict, and so the fill that copies
  it, carries:
  1. on the floor (`analysis_engine/__init__.py`): `floor_source`, `floor_limit_class`, `single_count_discipline`,
     and `point_floor_diagnostics` keyed by source cell then form;
  2. on each limited resolution (`analysis_engine/inputs.py`): the same words and discipline, and the diagnostics
     keyed by form for an `exact` resolution, by source cell then form for a `transported` one;
  3. in `claim_evaluation.floor_limit` (`analysis_engine/claims.py` `evaluate_claim`): `floor_limit_class`,
     `floor_source`, `published_floor_j`, `point_floor_diagnostics` (the floor's, keyed by source cell then form) and
     `single_count_discipline`.

  Each diagnostic is `detection_floor._point_floor_diagnostic`: `label` (`repeatability_diagnostic`),
  `published_claim_floor` (false), `unguarded_floor_j`, `guard_factor`, `guarded_floor_j`.
- **Defect: the comparator is the wrong side.** No rule matched (3). The rules for (1) and (2) named a diagnostic
  directly under `point_floor_diagnostics` (`(unguarded_floor_j|guard_factor|guarded_floor_j)` as the named
  exemption `FLOOR_DIAGNOSTICS`, the label and flag as uncovered words), a shape no producer writes, so the
  producers' nested leaves were unmapped too. The synthetic comparator fixtures carried no attribution-limited
  floor, and the one test of these rules used the flat shape.
- **The count.** The leaf shapes the lead read name (3)'s class, source and diagnostics. With
  `published_floor_j` and the 11 words of the discipline object that (3) also prints, and the floor and resolution
  copies of (1) and (2), the count is 14 + 10C + 5R (C the cell-and-form pairs carrying a diagnostic, R the
  resolution diagnostic paths), which can reach 84; (3)'s class, source and diagnostics alone are 2 + 5C, which
  cannot. So the fix maps every shape the producers can print, not only the three shapes listed.

### The mapping chosen, by leaf

Decided from the code and the registration (structure only). No bar is widened and no number is exempted.

| Leaf | Mapping | Why |
|---|---|---|
| `point_floor_diagnostics/<cell>/<form>/unguarded_floor_j` (floor, claim evaluation, transported resolution); `point_floor_diagnostics/<form>/unguarded_floor_j` (exact resolution) | Compared, `floor_j` bar, against the recompute's `point_unguarded_floor_j` of floor key `<model>/<phase>/<form>`, the cell routed through its registered entry and only as one of the contrast's registered floor cells (G3) | PLAN §5, "The D-054 point floor": point floor = max(max \|deviation\|, prediction). The recompute already computes it (`point_floor`), and its two terms and its use as the dominance denominator are already compared |
| `.../guard_factor` | Compared, `floor_j` bar, against the recompute's `guard` | PLAN §5 guard g(n); the floor cells' `guard_factor` is already compared under `floor_j` (`FLOOR_FIELDS`) |
| `.../guarded_floor_j` | Compared, `floor_j` bar, against the recompute's guard × point floor (composed from its own terms, as `corner_widened_guarded_floor_j` already is) | PLAN §5: guarded floor = g × unguarded floor. So a printed guarded floor that is not guard × unguarded disagrees |
| `.../label`, `.../published_claim_floor` | Exact (`outcome_word`) against the engine's words, `repeatability_diagnostic` and false | Fixed by `_point_floor_diagnostic`; the flag asserts the number is not a claim floor, so a true flag disagrees |
| `claim_evaluation/floor_limit/floor_limit_class`, `.../floor_source` | Exact (`outcome_word`) against `attribution_limited` and `E_clock_anchor_shift_bound_j`, where the re-derived D-078 rule (below) says some source cell is limited; absent otherwise | The engine's words (`ATTRIBUTION_LIMIT_CLASS`; `ATTRIBUTION_FLOOR_SOURCE`, the first-kind bound of PLAN §4 step 7). The comparator copies them as literals; `tests/independent_recompute/test_floor_limit.py` pins them to `detection_floor.py` on origin/main |
| `claim_evaluation/floor_limit/published_floor_j` | Compared, `floor_gate_j` bar, against the recompute's contrast floor gate | `evaluate_claim` prints the active floor it gated on (`artifact.py` requires it to equal `floor.active_floor_j`, itself compared under the same row family) |
| `claim_evaluation/floor_limit/single_count_discipline/*` | Uncovered words (strings and booleans only; a number there still refuses), by the same rule as the floor's and resolutions' copies | A fixed registered object (rule id, roles, flags, note) with `gating` false: no number, no claim |

- **Unchanged.** The floor's and the resolutions' `floor_source` and `floor_limit_class` words, and the discipline
  object's leaves, stay exempt from independent derivation under their existing rule (NEEDS_RULING RC-CMP-8 2); only
  the equality of their copies is new (below, R704-D1).
- **Re-derived (cold-pass M1).** Whether each floor is attribution-limited, the D-078 rule, is re-derived from the
  recompute's own terms and compared, not pinned (`limited_forms`; stdlib only, no `joulewise` import, so hash
  independence holds). A form of a registered floor cell is limited when the cell has a nonzero admissible half-width
  (`widths_j`) and the recompute's `linear_deviation_bound_j` exceeds its guarded point floor, `guard` ×
  `point_unguarded_floor_j` (`detection_floor.admissible_set_uncertainty_dominates_point_floor`, pinned as text by
  `test_floor_limit.py`; PLAN §5). Then, against that derivation: each cell and form that carries a diagnostic, on the
  floor, on the claim evaluation and on each resolution (the resolution's own registered cell only, L1), is a
  `routing_id` row, so a diagnostic printed for a form the rule does not limit, or dropped for one it does, is DISAGREE;
  the presence of `claim_evaluation/floor_limit` is an `outcome_word` row; and its class and source words are compared
  against the engine's words only where the rule says limited (missing otherwise: DISAGREE). Inside the
  `floor_j` bar of its guarded point floor (R704-D3, the lead's ruling after Sol's delta review, as narrowed after the
  delta-2 reviews S1-1) the form is always undetermined: L9 never prints the engine's linear bound and the engine computes
  it with a different floating-point expression than the recompute (the absolute form's other-width sum), so no decision
  operand set can be shown bit-identical and the RC-CMP-11 F1 exception is not used for limit decisions. Through
  `Comparison.atom` and `Comparison.word` a `within_bar_undetermined` row (the `limit_decision` rows, one per cell and
  form at the floor, the claim evaluation and each resolution) records both labels, AGREE only if the printed numbers
  agree within their bar. Outside the bar the strict `>` decides. The hold is automatic: the comparison lists the keys
  of every such row (`limit_undetermined`) and exits 1, and `scripts/release_b5.py` reports their count and keys
  (structure only, no value) and exits 1 with reason `within_bar_undetermined` (comparator stage status `undetermined_hold` when every family agrees), whatever the rows' numeric agreement;
  exit 0 requires zero such rows. Precedence is refused (exit 2) > hold (exit 1) > agree (exit 0) in both: a
  comparator that exits 2 (for example, a disagreeing fill copy is unmapped) is a release refusal and is never
  reported as `within_bar_undetermined` or as a disagreement hold; its family counts are still reported. Neither label
  is ever accepted silently.
  **Disclosed consequence, and its prespecified disposition (lead ruling, made blind before any release run).** A
  value genuinely inside the bar is held: a correct non-limited form at or just under the threshold prints no
  diagnostic and is undetermined even when every number agrees, and rerunning the same immutable inputs cannot clear it
  (an equality can also be structural, for example a maximum with zero width and other members with positive widths).
  That is the intended behaviour, not a defect, and there is no liveness guarantee. The disposition is fixed now and
  involves no discretion: the affected cell and form is published with the label "attribution limit not independently
  determined". No bar, threshold, outcome or label is changed, and there is no other discretion. The release exit
  stays 1 mechanically; this rule says only how the hold is reported. Ed's unseal decision is unaffected.
  A form that is not `computed` (below minimum, or `not_computed` after `make_floors` retained its
  terms because the drift allowance is unrecorded) has no limit, and a `computed` record without its four terms
  (`widths_j`, `linear_deviation_bound_j`, `guard`, `point_unguarded_floor_j`) refuses
  `recompute_floor_terms_missing` instead of meaning "no limit". The label stays a label beside the floor (no outcome reads it), but a wrong one no longer
  passes. The floor's and the resolutions' own `floor_source` and `floor_limit_class` words stay uncovered (RC-CMP-8 2).
  Every number a printed diagnostic carries is compared. A cell that is not one of the contrast's registered floor
  cells, or a form other than absolute or comparative, is DISAGREE, and so is every number under it.
- **Leaf count is structure, not an outcome (Fable LOW-6).** The 14 + 10C + 5R leaf count above is floor-metrology
  structure (how many registered cell and form pairs carry an attribution diagnostic), not a Block 5 outcome. No bar or
  threshold was chosen after seeing it: the bars are byte-pinned by `RELEASE_BARS_SHA256` in `scripts/release_b5.py`.
- **Notes from the cold final pass (Fable LOW-1, -2, -4, -5).** (1) The release script's row-key alphabet takes the same
  cell-id characters as the comparator's `DIAG_CELL`, a dot included, so a hold on such a cell still names its keys
  (all four registered floor cells are dot-free). (2) The release precedence trusts the comparator's exit code, not its
  summary: with comparator exit 1 and a summary that shows both a family failure and unmapped leaves (possible only if
  the comparator's own precedence broke) the release reports `comparator_disagreement` (exit 1) rather than a refusal;
  it can never come out as agree. (3) The tests that pin the engine's words read `detection_floor.py` from
  `origin/main` and skip if the ref is absent, not from the DLE-1 analysis commit; the engine files are blob-identical
  at `ab1e0098d`, `origin/main` and this head, so the pin is harmless today. (4) The discipline object's flags
  (`gating`, `not_an_acceptance_gate`) are checked for equality between verdict and fill but not pinned as literals;
  the engine's object is a frozen literal, so it cannot print `gating: true`, and the exemption is disclosed above.
- **Fill copies, both directions (Sol R704-2).** Comparison rows come from the verdict and coverage walks the fill's
  leaves, so a fill that omitted a verdict leaf was silently uncovered. The fill's copies of the attribution-floor
  metadata (the floor's, each resolution's and the claim evaluation's point diagnostics, and the claim evaluation's
  class word, source word and published floor) are now in `COPIED_LISTS`: every leaf of the verdict's group must be
  present in the fill (else `copy_shortened`), with type-preserving equality (`value_differs`), and a fill leaf the
  verdict does not carry has no row (unmapped). The presence row and the cell and form routing rows are not leaves of
  either document and are excluded.
- **Exempt words and flags: equal copies, both directions (Sol R704-D1).** The words and flags exempt from independent
  derivation (the floor's and each resolution's `floor_source`, `floor_limit_class` and `single_count_discipline`, and
  the claim evaluation's discipline) had no comparison row, so the fill could omit, alter or add them independently of
  the verdict. `floor_limit_copy_defects` compares the complete metadata (every leaf of those keys, of the floor's and
  resolutions' point diagnostics, and of the whole `claim_evaluation.floor_limit`) between the verdict and the fill,
  leaf by leaf, type and presence included, in both directions: a verdict leaf the fill lacks is `copy_shortened`, a
  fill leaf the verdict lacks `copy_extra`, a differing value `value_differs`; each makes the leaf unmapped (exit 2,
  `step11_unmapped_fill`). The exemption from derivation is unchanged.
- **Conditional publication (Sol R704-D2).** The aggregate attribution metadata (the floor's, the claim evaluation's)
  is expected only when every resolution is usable, as the producer publishes it (`analysis_engine/__init__.py`
  `_floor_row`: `all_usable and limited`); a usable limited resolution keeps its own diagnostic when its partner
  refuses. Usability is read from the independent recompute (a finite floor gate for the arm's registered cell in
  `floor_cells`), not from a printed status, so a printed refusal does not suppress a check the recompute says is due.
  **Inherited limit (delta-2 S1-2, S2-1).** The independent recompute has no transport model and its output exposes
  no transported or exact status for a registered cell, so usability cannot be derived from it beyond this proxy
  (the source cell's floor arithmetic is available). A consumer the engine refuses for transport (for example,
  consumer power outside the calibrated envelope) while its source has a finite gate is therefore still expected to
  carry the metadata the engine correctly withholds; the rows disagree, so the proxy fails closed (a hold, never an
  agreement), and the numeric floor rows (a null against a finite floor) already hold such a refusal. The registered
  Block-5 route is `exact_stack_only`, which the general transport-stress test does not apply to; the proxy is not
  claimed equivalent to the engine's usability. A printed refusal is not trusted to suppress a check. Extending the
  recompute is out of scope (it stays byte-identical).
- **Pruned.** The flat-shape rules and the `FLOOR_DIAGNOSTICS` exemption are deleted: a diagnostic printed directly
  under `point_floor_diagnostics` now refuses (`test_input_gate.py`
  `test_numbers_under_floor_diagnostics_refuse_sol` updated to say so).
- **Census.** `tests/test_single_count_discipline_census.py`'s reviewed manifest follows the extended discipline rule
  and lists the test fixture's discipline object.

### Tests

`tests/independent_recompute/test_floor_limit.py`, 15 tests when first written (now 37 after the review rounds). At
the r4 comparator 13 of the 15 fail (one of them the pin test, an error); the other 2 pin refusals that must survive
the fix. All 15 passed after the first fix. The fixtures are synthetic
and shaped as the producers write them: exact and transported resolutions, one form
per cell, the prefill contrast's own cells. Each of these disagrees and the run does not exit 0: a point floor, a
guard factor or a guarded floor off the recompute's; an exact resolution's diagnostic off; a class or source word other
than the engine's; a label or flag other than the engine's; the published floor off the floor gate; a cell of
another contrast. An unregistered form or an extra number in a diagnostic refuses `step11_unmapped_fill`, and a fill
copy that differs from the verdict is not coverage.

`tests/independent_recompute/test_sol_delta_review_704.py` (Sol's delta witnesses, now ordinary tests, with the added
cases for R704-D1, D2 and D3), the within-bar tests of `test_floor_limit.py` and the hold tests of
`test_release_b5.py` (one undetermined row exits 1 with the reason and the row keys; none leaves exit 0) cover the
three dispositions. The delta-2 witnesses (`test_sol_delta2_review_704_sol1.py`, `_sol2.py`) are ordinary tests: the unprinted
bound and the refusal precedence are fixed, and the transport-usability witnesses pin the disclosed proxy limit as fail-closed.

### Release condition

- The r4 release check re-runs at the merged comparator against the same r4 dry-run custody. The new rows are
  ordinary comparison rows under the existing bars and are not waivable. If any disagrees, that is a new hold,
  traced structure only.
- The r4 dry run is not released by this entry.

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

---

## Signing statement for DLE-6 to DLE-10

These entries were written after the Block 5 release event (Ed's unseal, 2026-11-08, `RUN_STATE.md` item 231). The
statement the earlier entries carry ("The release event has not happened") cannot be made for them, and they do not
carry it.

Each records a ruling of the research design lead (Fable 5.2) of 2026-11-10 18:44 PST, in
`docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` on `origin/audit/2026-11-10-fable` @ `5de56400f`
(called **RL** below; `RL:42` is its line 42 at that commit). Later rulings (RL-25 to RL-27, 2026-11-10 20:07 PST)
are quoted from `9f536d876` on the same branch, whose lines 1-640 are byte-identical to `5de56400f`.
The lead's authority, RL:3-6:

> **Authority.** Ed, 2026-11-10 about 18:25 PST, recorded in `RUN_STATE.md` item 252: "def fable 5.2 should be the
> final say for anything paper bound". That covers claim contracts, registrations, designs, analysis rulings, and
> release and claim text. Opus 5.5 (the lead) orchestrates and has the final say on non-paper engineering.
> Scope, venue and authorship choices stay with Ed.

Each entry quotes its ruling, reason and blind-status line verbatim, copied from those bytes line for line. The
rulings are **Block-5-aware**: the research lead read the released Block 5 results before ruling, and each blind-status
line says so. The recorder (an Opus 5.5 seat, RL-24 seat 8) read the rulings, the registrations, the sources cited and
`RUN_STATE.md` items 231 and 232, and opened no Block 6, BYTES held-out or restricted path. RL-24 routes these entries
to the research lead for review before merge.

---

## DLE-6. The gate a Block 5 number passes before it is rendered (RL-3)

- **Status.** ADOPTED, 2026-11-10, by research-lead ruling RL-3 (RL:56-76). It is logged as DLE-6 because RL-3 says
  "The lead logs it as DLE-6".
- **Original rule.** The 2026-10-20 renderer obligation, declared deviation Q-RENDERER, appended to the Block 5 seal
  record (`docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md:631-638`;
  `docs/process_traces/2026-10-20-magistrate-6cff3515/L9-RULING-ADDENDUM.md:92-99`). Its obligation, from the line on which it starts (SEAL_RECORD.md:635-638):

> changes. Obligation fixed now, before release: any block-5 Results renderer written after release prints every row of
> the validated fill input's contrast census with its issued status (unsupported and refused included), selects none, and
> its validator checks row-for-row correspondence with the fill input. It passes the Results cold gate before any number
> it prints is used.

  `RUN_STATE.md` item 232 lists that gate as open: "the Results cold gate required by the 2026-10-20 renderer
  obligation". DLE-0 replaced PLAN step 12, the results cold gate, by the recompute agreement; the obligation still
  named it.
- **Ruling (verbatim, RL:58-71).**

> **Ruling.** No Block 5 number enters Paper 1, a slide, the site or any public page until all three hold:
>
> 1. `docs/analysis/b5/RESULTS.md` is on `main`.
> 2. One fresh executing reader from the other model family than its author (it was written by an Opus seat, so
>    a Sol seat) re-derives every number to be printed from the frozen custody by the key paths the file gives,
>    and checks the paper's sentences against the ten licence constraints listed in the release-to-paper audit.
>    That reader is not a repair seat.
> 3. Every printed value that comes from one of the seven families the recompute does not cover, from the 403
>    exempt leaves, or from a recompute-only line (the whole-machine per-phase energies, the load-correlated and
>    scaled-allowance lines, the durations, the attempt history, the monitor cost) has the item-83 ruling-3 hand
>    check, with its source named.
>
> This is the replacement for the "Results cold gate" that the 2026-10-20 renderer obligation still names and
> DLE-0 abolished. The lead logs it as DLE-6. Internal documents may quote `RESULTS.md` meanwhile, naming it.

- **Reason (verbatim, RL:73-74).**

> **Reason.** Item 232 lists this gate as open. Without it, every paper number is a hand copy of one seat's
> reading.

- **Blind status (verbatim, RL:76).**

> **Blind status.** Not blind to Block 5. Procedural.

- **Effect on estimands.** None. No estimand, estimator, decision rule or threshold changes. It governs when a
  released Block 5 number may be rendered.
- **Scope (research-lead ruling RL-27 (1) and (2), 2026-11-10 20:07 PST, RL:751-758 @ `9f536d876`, verbatim; RL-25
  directs that they be appended here).** RL-27 (1) replaces RL-3's word "internal" with "working records".

> 1. **RL-3 is a quality gate, not a secrecy gate.** The repository is public, and `RESULTS.md` and `RUN_STATE.md`
>    item 232 have carried the Block 5 numbers since 2026-11-08. "Any public page" in RL-3 means a presentation
>    of Block 5 numbers as results to a reader: the paper, slides, the site, and the status pages (`README.md`,
>    `PROJECT_STATUS.md`, `CLAIMS_STATUS.md`, the advisor status site). It does not mean the repository's working
>    records: `RUN_STATE.md`, `RESULTS.md`, audits, the deviation and decision logs, review records. Those may
>    carry the numbers, naming their source. RL-3's word "internal" is replaced by "working records".
> 2. **Site builds are held** until RL-3's gate passes: no `build_site.py`, capsule or report build is published,
>    and Pages is not enabled. The hold goes in `CANONICAL.md` beside the site row.

- **Reason and blind status of RL-27 (verbatim, RL:769-772).**

> **Reason.** A gate that pretends a public repository is private would be false on its face. What it can and
> should control is what we present as a result.
>
> **Blind status.** Not blind to Block 5. Procedural.

---

## DLE-7. Adoption ruling for Block 5 placement, registration §14 Q4 (RL-2)

- **Status.** ADOPTED, 2026-11-10, by research-lead ruling RL-2 (RL:40-54). RL-2 directs that it be recorded here
  and as a dated addendum at the head of `docs/paper/results-fill-registry.md`; that addendum is entered in the same
  commit as this entry.
- **Original rule.**
  - Block 5 registration §1 (`configs/campaigns/v5_claim_25g83/registration_block5.md:1652-1653`):

> What the paper prints, and from which artifact, is fixed in analysis plan §9; printing anything needs the placement
> ruling of §14 Q4.

  - Block 5 registration §14 Q4 (`registration_block5.md:5968-5969`):

> - **Q4. Paper placement (cold gate, ideally before seal).** D-174's fallback places no `_v5` result; printing needs an
>   adoption ruling.

  - The registry's standing disposition, `docs/paper/results-fill-registry.md:5-15` at `60d3225ee`, before the RL-2 addendum was put above it:

> D-174 SELECT FALLBACK selects the single methods/diagnostic draft in
> `draft-v2-skeleton.md`, under
> `docs/process_traces/2026-09-05-readiness/02-magistrate-ruling-fallback.md`.
> `RETIRED_FALLBACK` means no placement in this submission and no rendering
> permission. Dated retirement entries preserve each former supplier, token,
> value and status for history; they do not delete rows or authorize a later
> campaign. This disposition overrides the historical A/B/Refusal instructions,
> contingent subtitle, floor tables and fill census below. Those describe the
> frozen draft-v1/template, not active slots in the methods/diagnostic paper.
> The selector filename is retained as a single-outcome validator/copier accepting
> only METHODS_DIAGNOSTIC; A, B and REFUSAL selections are rejected.

- **Ruling (verbatim, RL:42-48).**

> **Ruling.** Every row the Block 5 analysis plan §9 registers for print is placed in Paper 1 at the sites
> `fill_index.md` names for it (§5.1 to §5.6 and §5.8, the abstract and conclusion sentences assembled from
> them), beside its registered fixed sentence. Both contrasts print with their issued status; nothing is selected
> or omitted. Dominance prints as branch B, with every ratio, numerator, denominator and n, and no subtitle. This
> supersedes the 2026-09-05 "D-174 SELECT FALLBACK" disposition for these rows, on Ed's written instruction of
> 2026-11-08 (item 232), which is one of the two events at which D-174 says it expires. The lead records it as a
> dated addendum at the head of `docs/paper/results-fill-registry.md` and in the Block 5 deviation log.

- **Reason (verbatim, RL:50-51).**

> **Reason.** Item 232 settles that Block 5 is in the paper. It does not say which rows, where, or what happens to
> the registry's standing disposition, and the registration requires an adoption ruling before anything prints.

- **Blind status (verbatim, RL:53-54).**

> **Blind status.** Not blind: Block 5 is released and I have read it. The ruling places every registered row and
> selects none, so knowing the outcomes cannot shape it.

- **Effect on estimands.** None. No estimand, estimator, decision rule or threshold changes. It places registered rows
  and selects none.

---

## DLE-8. The D-177 limitation on phase-energy sentences (RL-4 (x)): reporting interpretation

- **Kind.** A reporting interpretation, not a change of rule. RL-4 (x): "Logged as a reporting interpretation."
- **Status.** ADOPTED, 2026-11-10, by research-lead ruling RL-4 (x) (RL:104-106).
- **Original rule.** Block 5 registration §1 (`configs/campaigns/v5_claim_25g83/registration_block5.md:1641-1642`):
  "Every phase-energy sentence carries the D-177 limitation (phase attribution was not characterized by a measured
  instrument check)."

- **Ruling (verbatim, RL:80 and RL:104-106).**

> **Ruling.** These bind every sentence about Block 5 in Paper 1, the capstone manuscript and the talk:

> - (x) Registration §1's "every phase-energy sentence carries the D-177 limitation" is met by stating it in the
>   abstract, in every table caption and in every paragraph that states a phase energy, and in the limitations.
>   Logged as a reporting interpretation.

- **Reason (verbatim, RL:111).**

> **Reason.** These are the points at which the released record is narrower than the natural way to write it up.

- **Blind status (verbatim, RL:113).**

> **Blind status.** Not blind to Block 5; the ruling is about wording released results.

- **Effect on estimands.** None. It fixes where a registered limitation sentence is stated.

---

## DLE-9. The registered fixed sentences (RL-4 (xi)): reporting interpretation

- **Kind.** A reporting interpretation, not a change of rule. RL-4 (xi): "Logged as a reporting interpretation."
- **Status.** ADOPTED, 2026-11-10, by research-lead ruling RL-4 (xi) (RL:107-109).
- **Original rule.** PLAN's fixed sentences, for example the attribution-floor sentence of §5 (PLAN line 257) and the
  disclosure sentences of §8.1. They use internal labels, which Paper 1's draft paraphrases (finding F-19 of
  `docs/research-audits/2026-11-10-fable/paper-audit.md` on `origin/audit/2026-11-10-fable`), and they say "window"
  (for example PLAN line 506: "These numbers are conditional on a window ...").
- **Ruling (verbatim, RL:80 and RL:107-109).**

> **Ruling.** These bind every sentence about Block 5 in Paper 1, the capstone manuscript and the talk:

> - (xi) The registered fixed sentences print verbatim in an appendix, with internal labels glossed in brackets.
>   The body may paraphrase one only where it cites that sentence by label. "Session" may replace "window" with
>   one note saying so. Logged as a reporting interpretation.

- **Reason (verbatim, RL:111).**

> **Reason.** These are the points at which the released record is narrower than the natural way to write it up.

- **Blind status (verbatim, RL:113).**

> **Blind status.** Not blind to Block 5; the ruling is about wording released results.

- **Effect on estimands.** None. Every fixed sentence prints verbatim; the ruling governs where it prints and how the
  body may refer to it.

---

## DLE-10. Printing Block 5 without Block 6 beside it (RL-6 (e))

- **Status.** ADOPTED, 2026-11-10, by research-lead ruling RL-6 (e) (RL:159-162). A standing deviation: it covers every
  draft, talk or Tier C submission that prints Block 5 without Block 6 beside it.
- **Original rule.**
  - `RUN_STATE.md` item 37 (line 66), decided blind on 2026-10-14: "Reporting rule fixed now: the paper prints block 5
    and block 6 side by side, each under the same estimators, and the difference between them per printed quantity;
    a GAMMA contrast is called replicated only if block 6 gives the same outcome word."
  - Block 6 registration §11.1 (`docs/registrations/block6_replication_DRAFT.md:1083-1084`): "The paper prints, for
    every quantity of §9 and each pack, block 5's value and each counting block-6 session's value, under the same
    estimators, with each session's interval, kept units and flags."

- **Ruling (verbatim, RL:159-162).**

> - (e) Printing Block 5 without Block 6 beside it, in a draft, the talk or a Tier C submission, departs from
>   item 37's reporting rule. It is logged as a deviation and carries the sentence that a registered replication
>   is collected and its results are not yet released. I will not sign off a submission of Paper 1 to an
>   external venue without the replication released.

- **Context in the same ruling (verbatim, RL:145 and RL:156-158).**

> - (a) Block 6 stays in Paper 1's design. It is not ruled out of scope.

> - (d) Paper 1 prints the replication if Block 6 is released under its registration by **5 December 2026**.
>   Otherwise it prints the Tier C text. The call is recorded in `RUN_STATE.md` by date, before any Block 6
>   number is read. This replaces the contingency plan's 22 November trigger.

- **Reason (verbatim, RL:164-166).**

> **Reason.** Nine counting sessions are collected and no path can analyse them. The amendments that should have
> preceded the Block 5 unseal did not. Adopting the pre-unseal text verbatim is the only way left to keep those
> choices from depending on Block 5's outcome words.

- **Blind status (verbatim, RL:168-169).**

> **Blind status.** Blind to Block 6: nothing of it has been read. **Not blind to Block 5**, whose outcome words
> the replication word compares against. The date in (d) was chosen from engineering state only.

- **The required sentence (research-lead ruling RL-25, flag 4, RL:712-714 @ `9f536d876`, verbatim).** It carries the
  "decided after Block 5 outcomes were known" label of RL-25 (RL:648).

> 4. *The DLE-10 sentence.* "A replication of this experiment in nine further sessions on later days (Block 6)
>    was registered before any Block 5 number was seen and has been collected. Its results are sealed and are not
>    yet released." On a slide: "Replication collected (nine sessions, registered blind); not yet released."

- **Effect on estimands.** None. No Block 5 or Block 6 number changes. It changes what a draft, the talk or a Tier C
  submission prints beside Block 5.
