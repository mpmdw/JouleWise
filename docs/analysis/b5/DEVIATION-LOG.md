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
