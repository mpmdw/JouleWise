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

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

---

## Not adopted for now: DLE-3, DLE-4 and DLE-5 (lead, 2026-11-06)

These are CARE §4's drafts:
- **DLE-3**: step-1 strict validation by hash binding.
- **DLE-4**: memoizing or hash-binding the 3b candidate refits.
- **DLE-5**: dropping the 120 s analysis-path wall deadline.

Under DLE-2 the heavy pipeline is off the critical path. So it keeps its full strict re-derivation, as the audit.
The PLAN rules these drafts would have changed stand as written. Engineering-only speedups, which change no
registered number, decision or refusal position, continue on `lane/2026-11-06-b5-under-90`.
