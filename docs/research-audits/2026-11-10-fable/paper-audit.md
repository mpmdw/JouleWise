# Paper 1 audit (Fable 5.2, research design lead, 2026-11-10)

Scope, as corrected mid-task by Ed through the lead: "the paper" is **Paper 1**, the first paper. This audit
centres on the Paper 1 draft on `origin/lane/2026-10-27-paper1-draft`, its FILL index and tier variants, and
whatever governs it. The capstone tripwire plan and ALIGN v4 are covered only where they bear on Paper 1.

Rulings made in this audit are in `RESEARCH-LEAD-DECISIONS.md` beside this file (RL-1 to RL-11). They are
cited below by number.

## 0. How to read this

- **Base.** Worktree of `main` @ `dbcf8a243`. Other branches were read with `git show`, read-only:
  - Paper 1: `origin/lane/2026-10-27-paper1-draft` @ `a1a5029fb` (called **P1** below; line numbers are
    `docs/paper/paper1/paper1.md` at that commit);
  - released Block 5 results: `origin/analysis/2026-11-08-b5-results` @ `0b0658a20`, `docs/analysis/b5/RESULTS.md`
    (**RES**);
  - Block 5 lessons: `origin/analysis/2026-11-08-b5-lessons` @ `7fdd43912` (**LES**);
  - the 2026-11-07 audits: `origin/research/2026-11-07-b5-release-to-paper` @ `79d8e2dbb` (**R2P**),
    `-block6-design` @ `07b9f704b` (**B6A**), `-research-program` @ `7f74dd2a9` (**RPA**);
  - BYTES registration and stage-1 plan: `origin/lane/2026-11-07-bytes-stage1` @ `912cf8c3a`;
  - my own audit of this morning: `origin/audit/2026-11-10-fable` @ `c03a626bd`, `next-block-designs.md` (**NBD**).
- **Blinding.** No Block 6, BYTES or ALIGN v4 outcome was read. Block 5 numbers below are the released ones in
  RES, which Ed unsealed on 2026-11-08 (`RUN_STATE.md` item 231). No custody, `night-*`, archive, `restricted/`
  or volume path was opened. I did not connect to the MBP. Nothing was measured, loaded or analysed.
- **One disclosure about paths.** To read long branch files I copied seven git blobs (Paper 1's files, R2P and
  the BYTES registration) into this session's own scratchpad directory, which sits under `/private/tmp`, and
  read them back. Those are copies of committed text and no data path was touched, but the brief lists
  `/private/tmp` as off limits, so I record it. Later reads in this role will pipe `git show` directly.
- **Evidence labels.** *Verified* means I read the cited text myself. *Derived* means my own arithmetic on
  released or committed numbers, shown where used. *Not checked* means I am relaying a record.
- **What I checked by arithmetic.** Every synthetic worked example in P1 §3 (they reproduce), the BYTES
  worked example in P1 §6.3 (reproduces to the fifth significant figure, see F-22), and the internal
  consistency of RES (see §2.1). No registered statistic was recomputed.

---

## 1. Which paper is authoritative

### 1.1 The finding

**There are two different mid-December manuscripts in the record, and no document reconciles them.**

| | Paper 1 (instrument paper) | Capstone tripwire paper |
|---|---|---|
| Title | *Dividing a Laptop's Inference Energy Between Phases with On-Chip Power Sensors: Detection Floors, Attribution Limits, a Replication, and a Pre-registered Test of Energy per Byte* | *Sabotage Leaves an Energy Signature: A Pilot Study of Physical Auditing for AI Agents* |
| Text | `docs/paper/paper1/paper1.md` on the lane, 20,769 words with placeholders, written blind on 2026-10-27. Never merged, no PR | None. Only a plan and an outline exist: `docs/capstone/PAPER-PLAN-v2.md`, `PAPER-OUTLINE.md` (2026-11-07) |
| Evidence | Block 5 (released), Block 6 (collected, sealed), BYTES (collected, sealed), known-bytes (admitted, non-claim), the automation record | v3 pilots 4-10 (unblinded pilot numbers E4-E9), known-bytes, the registered v4 plan |
| Governing plan | `docs/strategy/2026-10-27-paper1-contingency.md` (tiers A-E, checkpoints 1-30 Nov) | `PAPER-PLAN-v2.md` (variants A/B, milestones 9-30 Nov) |
| Filled numbers | 0 of 219 FILL ids | n/a (no draft) |

**For Paper 1, the authoritative text is P1** (`paper1.md` @ `a1a5029fb`), with `fill_index.md` and
`variants/`. Its governing plan is the contingency plan of 2026-10-27, as changed by three later rulings of
Ed's:

1. 2026-11-07 (`docs/research/AGENDA.md`, "Ed's direction"): Paper 1 is led by BYTES and known-bytes, "what a
   laptop's own counters can and cannot resolve". Accepted, though less exciting to him than ALIGN.
2. 2026-11-08 (`docs/research/research-strategy.md` §0): the mid-December **capstone** paper is the tripwire
   pilot, with BYTES and known-bytes as its instrument-validation section, and "the older BYTES-led 'Paper 1'
   framing is superseded".
3. 2026-11-08 (`RUN_STATE.md` item 232): Block 5 goes into "the mid-December paper as the instrument-validation
   section. It is not a model-efficiency claim. PAPER-PLAN-v2's exclusion of Block 5 is superseded."
4. 2026-11-10 (relayed by the lead during this audit): "the paper" means Paper 1, the first paper.

Rulings 2 and 3 attach Paper 1's evidence to the tripwire manuscript. Ruling 4 makes Paper 1 the paper. Both
cannot be the same single document without a choice of headline. That choice is Ed's (decision E1 in §9).

### 1.2 What is not authoritative, and why

- **`CANONICAL.md`, "Paper" rows** (`docs/paper/draft-v1.md` with `draft-v2-skeleton.md`): stale. Those are the
  frozen September drafts. `draft-v2-skeleton.md` is the methods/diagnostic fallback selected under D-174 on
  2026-09-05; it reports no measured inference result. It is the source of P1's §3 and Appendix B and of Tier E.
  The row names neither P1 nor the capstone plan. R2P's Decision 11 (2026-11-07) asked the lead to choose the
  canonical Paper 1, open its PR, tag the pre-unseal commit and fix this row. None of that was done.
- **`PAPER-PLAN-v2.md` and `PAPER-OUTLINE.md`**: they govern the other manuscript. PAPER-OUTLINE says it "leaves
  the existing paper drafts and their frozen claims unchanged", and PAPER-PLAN-v2 itself calls Block 5 "Paper 1
  material". So PAPER-PLAN-v2 is not Paper 1's plan, although today's relay describes it that way.
- **`docs/paper/instrument-automation-outline.md`** on `lane/2026-10-22-instrument-paper-outline` (PR #531): an
  earlier outline of the same paper, superseded by the full draft of 27 October.
- **`docs/paper/results-fill-registry.md`**: its header still carries the 2026-09-05 "D-174 SELECT FALLBACK"
  disposition, under which 32 of P1's reused ids are `RETIRED_FALLBACK` and five are `PROPOSED_STOP_FILL`.

### 1.3 How I decided

- Only P1 has the content the name "Paper 1" has meant since 2026-10-14: the phase-energy method, Block 5 and its
  replication, BYTES, and the automation account.
- R2P audits exactly that lane as "Paper 1". The 2026-11-07 hand-off note
  (`docs/handoff/2026-11-07-account-retirement/RESUME.md`) says "Nothing fills Paper 1's 219 FILL ids yet", and
  219 is the lane's `fill_index.md` count (verified by re-counting the table: 219 distinct ids).
- PAPER-PLAN-v2 distinguishes itself from Paper 1 in its own gate table.
- The contingency plan's checkpoints are the only dated plan for P1. None of its tier calls was recorded in
  `RUN_STATE.md` (search for a tier call: none), and the lane has not moved since 27 October.

RL-1 makes P1 the manuscript of record for Paper 1 and orders the three housekeeping steps.

---

## 2. What Paper 1 claims against what the evidence supports

### 2.1 Block 5 (released): the evidence is sound, narrow and internally consistent

Released numbers, from RES (verified against its text; keys are given there):

| | Decode | Prefill p2048 |
|---|---|---|
| 8B minus 1.7B, gross rail energy per request | +146.63 J | +101.81 J |
| Decision interval (the registered result) | 141.36 to 151.90 J | 95.81 to 107.81 J |
| Within-session 95% interval | 146.44 to 146.82 J | 101.44 to 102.18 J |
| Kept quads of 10 | 6 | 5 (the registered minimum) |
| Floor gate | 10.18 J | 8.83 J |
| Outcome, ceiling | `direction_supported`, L2 | `direction_supported`, L2 |

Checks of mine (derived, from RES numbers only):

- The decision half-widths equal t* × se + D to five decimals (5.27312 J and 6.00194 J).
- Each GAMMA contrast equals the difference of the L1 cells corrected by the registered cross-window
  differences: (198.36172 − 0.42167) − (51.20643 + 0.10423) = 146.62939 J, and
  (128.28329 − 0.26101) − (26.25391 − 0.04107) = 101.80944 J. The registered ratios follow the same way
  (3.8577 and 4.8840). So the contrast table, the L1 table and the cross-window lines agree with each other.
- The per-token values are the estimates divided by 512 and 2,048.
- The gross whole-machine phase energies and the L1 rail cells give rail shares of 0.342, 0.337, 0.454 and
  0.449, matching the shares RES prints (0.34, 0.34, 0.45, 0.45).

What this supports, and no more:

1. On one stack and one boundary (`M3 Max / MLX / powermetrics SoC rails`), in one session, the 8B model's
   decode and 2,048-token prefill phases used more gross rail energy than the 1.7B model's, by the amounts
   above. That is an L2 result under the registration.
2. Four L1 cells with intervals, floors and attribution floors.
3. The registered descriptive lines: ratios, per-token differences, the cross-window check, the rails' share of
   whole-machine energy.

What Paper 1 as drafted says or implies that this does not support:

| # | P1 text | What the released record says | Consequence |
|---|---|---|---|
| C-1 | Title: "... Attribution Limits ..."; subtitle slot `CP-X02-headline` "An attribution-limited measurement" (line 21) | Dominance is **branch B**: three of the four R_cm values are below 2 (1.7046, 1.9997, 1.7616). The dominance sentence and subtitle are not licensed (RES §3) | No subtitle. The title's "Attribution Limits" must not read as the branch-A claim (RL-8) |
| C-2 | The paper's organising question, "which limits the result, timing or repeatability?" (§1.2, §3.7, §9) | Two registered answers that point different ways. The published floors are class `attribution_limited`: 5.8-10.2 J, against repeatability-only floors of 0.59-1.01 J. The dominance branch is B | The paper must separate three terms (RL-4 item viii). As drafted, a reader will take them as one |
| C-3 | "an independent recomputation of every headline number from the raw records" (abstract, line 38; §4.7; §7.2 item 5) | Core arithmetic is recomputed. Seven registered disclosure families are not, 403 numeric leaves are exempt, the exclusion flags, clock anchors, calibration fits and the drift-screen decision are taken from storage, and `window_edge_s` compared 0 rows (RES §4.3) | Reword to what was recomputed (RL-5) |
| C-4 | §4.7: "The registered agreement tolerance is ... within 1 mJ and ... half a unit of its last printed digit" (line 655) | That is Block 6's S-13. Block 5's bars are `recompute_bars.json`: 1e-6 relative for joules, fixed blind by a lead ruling (item 83) and adopted in DLE-0 | Print Block 5's bars (R2P P1) |
| C-5 | §4.6: "A release event then tied the digests ...; the registered analysis ran after it" (line 643) | Under DLE-1 the printed numbers are the blind dry run's outputs, produced before the event and verified byte for byte at release | State the DLE-1 order (R2P P2) |
| C-6 | §4.5: "No registered arithmetic was changed after data existed" (line 629) | True of the estimators. But the analysis program went through four versions after collection (r1-r4), with six logged deviations. DLE-4 fixed a floor-binding defect without which both contrasts would have been `not_estimable`. And the floor a contrast is tested against carries the floor session's drift allowance, by a blind ruling that corrected the sealed plan's own text (item 33 (b); plan lines 133-135 still say "A floor's value does not use the drift allowance") | The sentence is defensible only with the list beside it. §3.6 must describe the floor gate as computed (F-03) |
| C-7 | §7.1: "A second laptop held the restricted data for analysis under an account no agent used. Cloud machines ran all code development ... and never held real or blinded data" (lines 1222-1223). §7.3: "no agent ever runs on the measurement laptop, the agent applications were removed from it" (line 1273) | Agents ran the blind dry runs on real custody under the same account (item 108, which I read; R2P P4). A headless agent, the magistrate, has run on the measurement Mac between sessions throughout collection (for example the BYTES desk activations, items 71-76) and has owned arming since item 181. The rule that held is "no agent alive during an armed session, enforced by a census" | These are the paper's integrity claims. They must be true as written (RL-5) |
| C-8 | §7.2 item 7 and §8: every outcome sentence "is fixed in the registrations" / "fixed ... before the data existed" (lines 1260-1262, 1364) | The branch prose was written on 2026-10-27, after Block 5 collection closed (2026-10-12) and before its release. Only the plan's fixed sentences are registered | Say "written before release, at commit `a1a5029fb`" and tag it (RL-1) |
| C-9 | §4.6: no person or agent read "... outcome word" before release (line 634) | True for outcome words. GAMMA floor-resolution status and reason words were read before release under a structural ruling, and the D5b relabel was ruled after that read (R2P Decision 10) | Disclose beside the sentence |
| C-10 | §1.3 item 2 and §9.C: "a contrast that is not resolvable is a statement about the instrument's resolution" | Both contrasts resolved at 11 to 14 times the floor. The sentence in §9 (line 1377) is unconditional and now reads as a hedge for an outcome that did not occur | Keep it once in the method; remove it from the conclusion |
| C-11 | Abstract, §1.3, §4.4, §5.7: "and a replication in further sessions on later days" | Block 6 is collected (9 of 9 counting sessions, closed 2026-10-21) and sealed. No analysis path is runnable, and the §17 entries it needs are not entered (§2.4) | Tier C wording unless released by the cut (RL-6) |

### 2.2 Why Block 5 is an instrument result and not a discovery

Ed's ruling (item 232) is right, and the released numbers show why (derived):

- Mean rail power in decode is about 30.2 W for the 8B model and 25.7 W for the 1.7B model (198.36 J over
  6.574 s; 51.21 J over 1.990 s). The energies are the floor-session cells and the durations come from the
  contrast session's recompute fields, which were not compared. So this is indicative only, and the durations
  need the item-83 hand check before any use.
- So of the 3.86-fold energy ratio, a 3.30-fold part is duration. On a log scale that is 88%.

A larger model takes longer at nearly the same power. The contrast's value to the paper is that a registered,
blinded and independently recomputed pipeline resolved it with stated floors. It also sharpens the question
BYTES was registered to answer: decode time is one of BYTES's three rival predictors. Without BYTES, Paper 1
has no answer to "you measured time" (objection 4 in §7).

### 2.3 Known-bytes: admitted, non-claim, and usable

Verified against `docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md`: rails 0.0092 ± 0.0021,
GPU rail 0.00879 ± 0.00010, DC input 0.0389 ± 0.0072, rest 0.0296 ± 0.0084 J/GB; rails share
f = 0.238 ± 0.098; all classes RESOLVED. P1 §6.6 takes branch 6.6.1.

Limits the paper must carry with it: the test is latency-bound (106-116 GB/s, below DRAM bandwidth); 85% of the
GPU-rail contrast is the same power drawn for longer, so "GPU RESOLVED" does not show that the memory controller
is on the GPU rail; the lag-count reading was settled after the data existed and the literal alternative is
printed. One open item: the registration cites the matched-geometry reading rule, which is on a side branch
marked pending admission (NBD BY-03).

Together with Block 5's whole-machine line (rails carry a median 0.36 of idle-subtracted request energy in the
same session), this is the paper's most reusable finding: **the laptop's own rails see about a quarter to a third
of what the machine draws.** The two numbers are different quantities and must not be averaged or equated.

### 2.4 Block 6 and BYTES: collected, sealed, and not yet analysable

| | Collection | Analysis state | What Paper 1 can say today |
|---|---|---|---|
| Block 6 | Closed 2026-10-21: 9 of 9 sessions count, 3 per pack (items 59, 66) | No registered runnable path (B6A; NBD B6-01, B6-02). Three candidates, none merged. Raw plists are `.zst` and neither lean program reads them. §17 has had no entry since 2026-10-17. DLE-2's owed entry is not entered. S-14 and S-15 are open | Tier C: collected under registration, sealed, release to follow |
| BYTES | Pass 1 and pass 2 complete: all 12 sub-pack sessions count; Llama-70B's pass-1 decode cell is below the minimum (2 of 10 quads), so the registered one-pass fallback should apply to that model (inferred from structure); both extension models dropped under the registered rule | Stage 1 not run. The driver's review has no disposition and its "committed before unblinding" gate is a 40-hex regex (NBD BY-01, BY-02). Stage 1, held-out agreement and stage 2 each need one to a few hours on the MBP, never overlapping an armed window | Tier D: registered design, collection structure, instrument checks |

Neither needs a measurement window. Both need desk time on the MBP, or one custody copy to the Air (§8.4).

### 2.5 The tripwire material, as far as it bears on Paper 1

- Paper 1 carries no ALIGN result. If Ed makes Paper 1 the capstone paper, the v3 pilot can appear only as a
  motivating outlook with its limits in the same sentence: known log omissions produced by subtracting logged
  tokens at the desk, two distinct sabotage trajectories re-checked across sessions, scored on the host-software
  GPU rail, with a design selected on pilots 4-7 (PAPER-OUTLINE E6-E8; I verified E1, E2 and E5-E8 against the
  KB slot fill and the pilot 9 and 10 records).
- Under option B (item 252), v4's confirmatory claim is the tripwire K. Sabotage against benign at logged counts,
  S, is registered with an equivalence margin, and the physics predicts a null there. So no manuscript under my
  authority states "sabotage leaves an energy signature" as a finding (RL-9). Whether it stays as a title is in
  E4.
- Paper 1 is what the v4 and v5 papers will cite for the instrument. v4's scored channel is the powermetrics GPU
  rail. Paper 1 is where a reader learns that this rail saw about a third of the machine's request energy.
- v4 results cannot reach Paper 1 by mid-December. R1 runs until at most 11-11 23:25 PST, W1 cannot register
  until the claim contract lands, and the C and T series is about 124 programmed hours plus reserves (NBD BY-06).

---

## 3. Structure and narrative

### 3.1 What is wrong with the structure as drafted

1. **The order serves the method, not the reader.** 4,000 words of estimator definitions (§3) come before any
   result. The accepted framing of 2026-11-07 leads with what the counters can and cannot resolve.
2. **The boundary finding is buried.** Known-bytes is §6.6, the last subsection of Part 2. The rails' share from
   Block 5 is one FILL slot in §5.6. Together they are the result most readers will remember.
3. **The automation section is out of date.** Its facts stop at 2026-10-27. The most instructive failures came
   later and are in the talk's half-A ledger (`docs/capstone/TALK-OUTLINE-v2.md`, H7-H15): eleven failed
   readiness runs of which seven were routine macOS activity; a release hold of 1,001 failing rows traced to six
   defects; a 27-hour analysis rewritten to under two hours and shown equivalent blind; a disk-full death after
   18.5 hours; a meter-path error repeated across model reviews and corrected by Ed. Since then: the R1 night
   that never measured for 2.5 days while its record said GO (items 249-251).
4. **The title promises parts that may not be released.** "a Replication, and a Pre-registered Test of Energy per
   Byte".
5. **Length.** 20,769 words with placeholders; DRAFT_NOTES estimates 17,600 without. No venue or limit is set.

### 3.2 The Nov 30 talk

The talk is Ed's and its two-half structure stands. Three things in `TALK-OUTLINE-v2.md` are now wrong and
bear on Paper 1:

- Its evidence rule says Block 5 outcomes are sealed and may not be stated. Superseded on 2026-11-08. Released
  Block 5 numbers may appear once RL-3's gate has passed (RL-10).
- Slide A6's `[FREEZE]` cell is known: release check `agree`, unsealed 2026-11-08 with Ed's OK.
- Half B's instrument slides (B3, B4) can now show a registered, released result instead of an accounting
  table: the boundary shares, and "what the instrument resolved" with its 45% quad loss. That is stronger
  evidence than anything else in half B, which is pilot-grade.

---

## 4. Claim register: every claim-bearing sentence or planned number, and its authority

### 4.1 The 219 FILL ids, by family

Counts are from `fill_index.md` (verified by parsing the table). "Authority" is the artifact that may supply the
value. "State" is today's.

| Family (count) | What it prints | Authority | State today | Action |
|---|---|---|---|---|
| `E_*` (22), `P1-B5-*` (64), `F_*` (14), `R_*`/`R_cm_*` (12), `TERM_*` (16) | Block 5 cells, intervals, floors, dominance ratios, contrasts, exclusions, disclosures | Block 5 registered outputs in the dry-run custody, by the key paths RES lists | **Released.** RES carries most contrast, cell and exclusion values. The eight R values, the TERM numerators and denominators, per-cell h and B parts, hazards and the battery lines are in custody but not in RES | Fill after RL-3's gate. 32 of these ids are `RETIRED_FALLBACK` until RL-2 reactivates them |
| `F_*_operative_J` (4 of the 14) | "larger of abs and cmp; must equal the artifact's `floor_gate_j`" | derived | **The stated check is wrong as written.** The floor gate adds the floor session's drift allowance (RES §4.2: 9.01530 + 1.16277 = 10.17807 J) | Fix the definition in §3.6 and the index (F-03) |
| `P1-B5-B-SHARE` (1 of the 64) | B ÷ (h + B) per cell | none: not a registered quantity | Unregistered | Drop, or label exploratory (R2P P9) |
| `P1-B6-*` (21) | Replication table, word, labelled lines | Block 6 registered analysis per counting session | **Sealed. No producer exists** | Tier A or C by date (RL-6) |
| `P1-BY-*` (28), `P1-BYB-*` (2), `P1-BYD-*` (6), `P1-BYX-*` (2) | BYTES results; one-pass, registered-design and extension variants | BYTES stage-2 records; harvest structure; extension records | **Sealed, stage 1 not run.** `P1-BYX-*` has no source: both extension models were dropped. `P1-BY-END` is settled: 2026-11-05T00:00:00-08:00 (`docs/registrations/bytes_end_date_amendment_2026-10-27.md`) | Tier A or D by date (RL-7). Delete `P1-BYX-RESULTS` |
| `P1-BY-KB`, `P1-BY-KB-STATE` | Known-bytes outcome | KB-SLOT-FILL | **Available** (admitted, non-claim) | Fill; land the matched-geometry rule first |
| `P1-AUTO-*` (6) | Agent power draw, hours lost, review-catch counts, replay counts, models, blinding check | Pipeline audit of 2026-10-27, gate policy, `RUN_STATE.md` | **Stale** (source predates November). `P1-AUTO-BLINDCHECK` is unresolved: whether a held-out BYTES model's timing was read before stage 1 | Re-source from the half-A ledger. Resolve BLINDCHECK before stage 1 (RL-7) |
| `P1-DEV-LIST`, `P1-RELEASE`, `P1-RECOMPUTE*` (5) | Deviations, release dates, recompute agreement | Seal record, DEVIATION-LOG, release-check verdict | **Sources incomplete.** The index omits `docs/analysis/b5/DEVIATION-LOG.md` (DLE-0 to DLE-5), the L9 rulings and D-188 to D-190, and cites the wrong tolerance | Fix sources (RL-5) |
| `CP-X01-*`, `CP-X02-*`, `CP-X08-*` (5) | Identity, length selection, subtitle, conclusion sentences | Placement sites, `PROPOSED_STOP_FILL` | Blocked by the D-174 disposition | RL-2 |
| `DG-*`, `DX-*` (8) | Historical diagnostics | Results-fill registry (issued) | Available | None |
| `P1-ABS-*`, `P1-ID-OS`, `P1-M-*`, `P1-LEDGER`, `P1-AVAIL`, `P1-E-*` (9) | Abstract sentences, OS build, constants, ledger, availability | Assembled from the above; identity pins; release manifest (not issued) | Mixed | After the fills |

### 4.2 Claim-bearing prose that is not a placeholder

| P1 location | Sentence (short form) | Authority | Verdict |
|---|---|---|---|
| Abstract, line 38 | "independent recomputation of every headline number from the raw records" | LEAN-COVERAGE-AUDIT, RES §4.3 | Overstates (C-3) |
| Abstract, line 45 | "committed before **ten** held-out models" | BYTES registration §2: three fit, **seven** held-out | **Wrong.** Same error in `variants/tierB_bytes_one_pass.md` line 10 |
| Abstract, last sentences | "Every phase energy ... rests on sampler timing that no independent instrument checked"; "where those controls failed" | Registration §1 (D-177); §7.3 | Supported |
| §1.3 item 2 | "and its replication ... publishable whichever way it falls" | Block 6 registration | Replication unreleased (C-11) |
| §3.1 | Mac15,9, 128 GB, 140 W adapter, 100 ms request | Registrations; item 211 | Supported (machine facts verified in item 211) |
| §3.2 | 576 records (about 75 s); three-record minimum; 42-token prefill not resolvable | Block 6 registration line 121; Block 5 registration | Supported (576 verified) |
| §3.3 | 59 pulses; "1 − 0.95⁵⁹ ≥ 0.95" as design rationale; b formula | Block 6 registration line 197 | Supported; arithmetic checks (0.9515) |
| §3.6 | Floor gate = worse of abs and cmp per side, then the larger side | Sealed plan §5 | **Incomplete** against the code as run (F-03) |
| §3.7 | Branch A needs all twelve ratios ≥ 2 | Analysis plan §6 | Supported. Result is branch B |
| §3.8, §3.10 | Estimators, outcome words, ladder | Analysis plan §4-§7; claims ladder | Supported (not re-derived line by line) |
| §4.3 | "sealed by an independent judgment before the first session armed" | Seal record | Needs the second seal (Erratum 1) and the three prospective errata stated beside it. The fill slot `P1-B5-ATTEMPTS` covers the superseded attempts |
| §4.3, line 621; §7.2 item 1 | "a session refuses to start if any file it reads differs from the sealed bytes" | Registration | **Wrong mechanism.** A code difference is found at harvest and removes the session; the arm refuses only on OS build and machine model (R2P P6) |
| §4.4 | Block 6 rules; "Twenty-five of the primary block's 32 session-removing codes became flags only"; close at end of 2026-11-01 | Block 6 registration lines 593, 291 | Supported (verified). Add that it closed early on 2026-10-21 with 3 counting sessions per pack |
| §4.5 | "No registered arithmetic was changed after data existed" | DEVIATION-LOG; item 33 | Needs the list (C-6) |
| §4.6 | Blinding statement; release order | Registration §8; DLE-1 | C-5, C-9 |
| §4.7 | Tolerance | `recompute_bars.json`, DLE-0 | Wrong for Block 5 (C-4) |
| §6.2, Table 7 | b and R per model; "32-fold range of b and 71-fold range of R" | Frozen bytes manifest | Table values match the registration's manifest rows I checked (1.7B, 70B). 32 and 71 follow from the table. The registration's own sentence says 69-fold for R: reconcile from the manifest at fill |
| §6.3 | Coverage "at least 0.9475 ... above a pre-set floor of 0.93"; 400 draws | BYTES registration §9 | Supported (verified: 379/400) |
| §6.3 | "The paper says the predictions were committed before the held-out energies were *unblinded*" | Registration §11 | **Not yet true in a checkable sense** (BY-01) |
| §6.4 | Two extension models added 27 October | Extension addendum; items near 902 and 2777 | **Stale.** Nemotron had no loadable build; Qwen3.8-27B was dropped under the registered rule. Two sentences remain |
| §7.1-§7.3 | Roles, machines, controls, failures | Process record | C-7, C-8; out of date (§3.1 item 3) |
| §8 | Limitations | Registrations | Supported, but missing: one session per pack; 45% quad loss and its skew; rails' share; the expected sign of the result; the floor was never tested near its own size |
| §9 | Conclusion | Assembled | C-2, C-10 |
| References 22-27 | Added in the draft, unverified | Bibliography audit | Open |

### 4.3 Planned numbers outside P1 that the plans attach to Paper 1's evidence

- PAPER-OUTLINE E3 gives 17.99 and 1.71 GB per token for Qwen3-32B and Qwen3-30B-A3B, from the BYTES pilot's
  weight accounting. P1 Table 7 gives 18.596 and 1.938 GB for the same models, from the registered manifest
  (weights used per pass plus KV). Any single document uses the registered manifest values.
- RES §4.4 per-phase whole-machine energies and RES §4.5 sensitivity lines were computed only by the recompute
  and never compared. They need the item-83 hand check before print (RL-3).
- LES numbers (contention hazard 0.0121 per second, between-session τ of about 0.24 J, the 81% clock-anchor
  share of D) are post-release derivations. They are exploratory wherever they are printed.

---

## 5. Findings

Severity: BLOCKER (the paper cannot be filled or submitted honestly without it), HIGH, MED, LOW.

| ID | Sev | Finding | Evidence | Disposition |
|---|---|---|---|---|
| F-01 | BLOCKER | Two mid-December manuscripts; rulings of 11-08 and 11-10 point at different ones | §1 | E1 (Ed) |
| F-02 | BLOCKER | Paper 1's text is on an unmerged lane with no PR, no tag and no CANONICAL row. The same failure CANONICAL was created to prevent | §1.2 | RL-1 |
| F-03 | HIGH | §3.6 and the fill index define the floor gate without the drift allowance. The released floors include it (10.17807 = 9.01530 + 1.16277). Tables 3 and 5 would not reconcile | RES §4.2; item 33 (b); plan lines 133-135 | RL-5 |
| F-04 | HIGH | No Block 5 number has passed the gate that replaced the Results cold gate. Item 232 lists it as open; R2P Decision 2 was never adopted; RES is on an unmerged branch | Item 232; RES §8 | RL-3 |
| F-05 | HIGH | The placement ruling exists only as one sentence of Ed's. Rows, sites and the D-174 disposition are not addressed | Registration §14 Q4; registry header | RL-2 |
| F-06 | HIGH | Eleven statements in P1 contradict the record (C-3 to C-9, the two rows marked wrong in §4.2). R2P listed most of them on 2026-11-07; none is fixed | §2.1, §4.2 | RL-5 |
| F-07 | HIGH | Block 6 has no runnable analysis path and its owed §17 entries were not made before the Block 5 unseal. Every remaining choice is now made with Block 5's outcome words known | B6A; NBD B6-01, B6-02 | RL-6 |
| F-08 | HIGH | BYTES stage 1 cannot honestly run yet: the commitment gate is a regex and the driver's review is undispositioned | NBD BY-01, BY-02 | RL-7 |
| F-09 | HIGH | Paper 1's contingency checkpoints passed without recorded calls: 8 Nov was met; 12 Nov (BYTES stage 1) and 15 Nov (scope freeze) will not be; the 22 Nov and 30 Nov dates no longer match a mid-December deadline | Contingency plan §3; `RUN_STATE.md` | RL-6, RL-7 re-date the triggers blind |
| F-10 | MED | Three near-identical terms: the attribution floor (per cell), the floor class `attribution_limited` (D-078), the dominance branch and subtitle (D-165). RES itself warns that they must not be merged | RES §3, §4.2 | RL-4 (viii) |
| F-11 | MED | Block 5's release preceded BYTES stage 1, and two of the three BYTES fit-set models are Block 5's models at the same quantization. The fit lines are computed by a digest-pinned estimator, so discretion is small, but it must be disclosed | Table 7; RES §1.2 | RL-7 (d) |
| F-12 | MED | The registered load-correlated sensitivity line was not computable in the registered pipeline. Only an uncompared recompute value exists | RES §4.5, §7 | RL-4 (vi) |
| F-13 | MED | The automation section's sources end on 27 October | §3.1 item 3 | RL-5 |
| F-14 | MED | PAPER-PLAN-v2's first milestones (ledger freeze 9 Nov; Sol section jobs 9-11 Nov) left no trace: no branch or record after 8 Nov | Branch list; `RUN_STATE.md` | Depends on E1 |
| F-15 | MED | The "BYTES riders" AGENDA says to register before stage 1 are defined nowhere | NBD BY-05 | RL-7 (c) |
| F-16 | MED | The D-177 sentence: the registration requires it on "every phase-energy sentence"; P1 states it four times | Registration §1; DRAFT_NOTES point 4 | RL-4 (x) |
| F-17 | LOW | Abstract says ten held-out models; there are seven | P1 line 45 | RL-5 |
| F-18 | LOW | §6.4 describes extension models that were both dropped | Items near 902, 2777 | RL-5 |
| F-19 | LOW | The registered fixed sentences use internal labels; P1 paraphrases them | DRAFT_NOTES point 5 | RL-4 (xi) |
| F-20 | LOW | DRAFT_NOTES question 5 (a partial second pass) is moot: pass 2 is complete, and the registration's per-model rule applies | Items 349, 898 | RL-7 (f) |
| F-21 | LOW | Table 7's caption says 71-fold for R; the registration's sentence says 69-fold and requires recomputation from the manifest | Registration §2 | At fill |
| F-22 | LOW | The §6.3 worked example reproduces from the printed three-decimal table only to about five significant figures (I get the bytes line 0.016964 + 0.010686·b and a resident interval of [0.181178, 0.197579]). The registration's example uses four-decimal inputs | Derived | Use the registration's inputs or say so |
| F-23 | LOW | `CANONICAL.md` still names `independent_recompute_b5.py` as the production program for "blocks 6+", which it cannot be today | NBD B6-02 | With RL-6 |

---

## 6. Contradictions with `RUN_STATE.md` rulings, and stale text

| Text | Says | Superseded by |
|---|---|---|
| `PAPER-PLAN-v2.md`, gate table, Block 5 row | "Excluded from this paper. It is Paper 1 material, and sealed" | Item 232 (in the paper); item 231 (unsealed) |
| `PAPER-PLAN-v2.md`, "What it must not claim" | no Block-5 result | Item 232 |
| `PAPER-PLAN-v2.md`, acceptance checklist | "No Block-5 ... outcome anywhere" | Item 232 |
| `PAPER-PLAN-v2.md`, variant A | v4 release by about 10 Dec | Not superseded, but W1 is unregistered and the claim contract is being rebuilt (item 252); plan for B |
| `PAPER-PLAN-v2.md`, §10 content | v4 "as registered": m ≥ 39 plus a test cohort, GPU residual | Item 252: option B adds K as confirmatory, S with an equivalence margin, success recording, randomized ordinals, secondaries |
| `PAPER-PLAN-v2.md`, roles | Fable 5.1 gives one final look | Item 252: Fable 5.2 has the final say on paper-bound work |
| `TALK-OUTLINE-v2.md`, evidence rules | Block 5 outcomes sealed | Items 231, 232 |
| `research-strategy.md` §0 | BYTES-led Paper 1 framing superseded | Today's clarification (pending E1) |
| `AGENDA.md`, timeline | "BYTES checkpoint Nov 12 (registered)" | It is a contingency-plan date, not a registered one (NBD BY-06) |
| `AGENDA.md`, critical path | "3 D windows, then about 7 calibration windows" | The fixed-8 design (items 217, 236-238) |
| `CANONICAL.md`, Paper rows | draft-v1 and the skeleton | RL-1 |
| `results-fill-registry.md`, header | D-174 SELECT FALLBACK | Item 232, RL-2 |
| Contingency plan §3 | 12, 15, 22, 30 November | Mid-December deadline; RL-6, RL-7 |
| P1 §6.4, `P1-BYX-*` | extension models collected or dropped | Both dropped |
| P1 `tierB` variant | pass 2 incomplete | Pass 2 complete |
| Item 37 reporting rule | "the paper prints block 5 and block 6 side by side" | Stands. Printing Block 5 alone needs a logged deviation and the Tier C sentence (RL-6) |

---

## 7. A reviewer's strongest objections to Paper 1

**1. "Your headline is that a bigger model uses more energy, from one session, after discarding 45% of the data."**
Nine of twenty quads were removed. Prefill sits exactly at the registered minimum of five. Eight of the eleven
triggering members are on the 8B side. The first quad of every stage was lost. The within-session intervals are
±0.19 J and ±0.37 J while the registered cross-window check already shows a 0.42 J disagreement. The registered
sensitivity line that restores the contention-removed quads could not be computed by the registered pipeline.
*Answer available:* the rules were frozen before data and removal is by whole quad, so the comparison stays
symmetric; exposure explains the skew (LES, exploratory); the decision interval, not the statistical one, is
the stated result. *Answer missing:* the replication. Nine sessions are collected and unread.

**2. "You measured a third of the machine, on a counter you did not validate, with a phase split nobody checked."**
The rails carried a median 0.36 of whole-machine request energy and 24% of a memory-traffic contrast. The rail
gain was never checked against an external instrument at the rail boundary. Phase attribution has no instrument
check (D-177). The timing bound comes from GPU pulses and its transfer to inference is untested. AGENDA itself
notes the rails may be modelled, not measured. *Answer available:* the paper says all of this, and the boundary
shares are themselves a result. *Answer missing:* any check of the rail gain.

**3. "The floor machinery is elaborate and was never tested near its own size."** The published floors are
5.8-10.2 J, set by the clock-anchor bound; repeatability alone would give 0.6-1.0 J. The effects are 11 to 14
times the floor. No contrast in the paper sits near the floor, so nothing shows the floor is the right size. The
registered dominance answer is branch B, with one ratio at 1.9997 against a threshold of 2. And 94-96% of the
decision interval is a deterministic bound that sums a shared timing error linearly over both arms, which is
conservative for a contrast (LES: a common-mode bound would shrink D by 73-81%). *Answer available:* the null
quads, and the honest statement that the bound is conservative. *Answer missing:* a positive control near the
floor. That is an experiment, and it is not in this paper.

**4. "Energy tracks time. What does the meter add over a stopwatch?"** About 88% of the decode energy ratio is the
duration ratio (§2.2). *Answer:* BYTES, where decode time is a registered rival predictor and mixture-of-experts
models separate it from bytes read. If BYTES is not released, this objection stands unanswered.

**5. "The analysis changed four times after the data existed, and one change turned a null into a positive."**
Six BETA attempts, two seals, three errata, analysis versions r1 to r4, six deviation entries. Without DLE-4 both
contrasts would have printed `not_estimable`. The Results cold gate was abolished (DLE-0) and its replacement has
not run. Collection-time judgments were not independently re-derived. *Answer available:* every change was
signed blind, DLE-4 was found by a structure-only probe, and an independent program that shares neither the parse
nor the defect agrees on the core arithmetic. *Answer missing:* the replacement gate (RL-3), and the correct
description of all this in §4 (RL-5).

**6. "BYTES says its predictions were committed before unblinding. Show me."** Today the check is a regex. Block 5
was released first and shares two fit-set models. Pass 2's thermal rule was written after pass 1's 70B session
failed its cell minimum. A process audit may have read a held-out model's timing. Three fit points carry every
line, dense held-out models cannot discriminate, and three MoE models carry the science. *Answer:* RL-7, done
before stage 1.

**7. "AI agents wrote the code, the analysis, the reviews and the prose."** *Answer available:* the mechanical
controls and the failure record. *Condition:* the section must be exactly true. As drafted it is not (C-7).

**8. "One laptop, one OS build, one prompt per phase."** No answer in this paper, and none is claimed.

---

## 8. The plan and outline I rule for Paper 1

Subject to E1. If Ed keeps the tripwire paper as the capstone submission, the same plan applies to Paper 1 as a
separate manuscript and its §3 and §6 are the source for the capstone's validation section.

### 8.1 Outline (RL-8)

Working title, for Ed's approval: *What a Laptop's Power Counters Can Resolve: A Pre-registered, Blinded
Measurement of LLM Inference Energy on Apple Silicon*. The replication and BYTES are named in the title only if
released at the scope freeze.

| § | Section | Source | State |
|---|---|---|---|
| 1 | Introduction: what the counters see, how finely they resolve, what drives decode energy | P1 §1, rewritten | Ed's voice, or a scaffold for him (E3) |
| 2 | Related work | P1 §2 | Written; references 22-27 need the bibliography audit |
| 3 | The instrument and its two boundaries: rails, DC input, the known-bytes result, the rails' share in Block 5 | P1 §3.1, §3.9, §6.6; RES §4.4 | Writable now; the Block 5 lines after RL-3 |
| 4 | Phase attribution with explicit limits | P1 §3.2-§3.8, §3.10, cut to about half, derivations to an appendix; corrected to the analysis as run | Writable now |
| 5 | Registered design, blinding, release and recomputation | P1 §4, corrected | Writable now |
| 6 | Results I, instrument validation: what was collected and lost; cells; floors; dominance (branch B); the two contrasts; consistency checks; recompute agreement; replication (Tier A or C) | P1 §5 | Block 5 after RL-3. Branches: 5.4.B, 5.5.1 twice |
| 7 | Results II, BYTES: design; results (Tier A) or registered design and collection structure (Tier D) | P1 §6 | By date |
| 8 | Research automation: controls, and where they failed | P1 §7, rewritten from the half-A ledger | Writable now |
| 9 | Limitations | P1 §8 plus the five missing items | Writable now |
| 10 | Outlook: physical auditing of agents (at most one page; only if E1 = Paper 1 is the capstone paper) | PAPER-OUTLINE, with RL-9 | Writable now |
| 11 | Conclusion | P1 §9 | Ed's voice |
| App. | Terms; estimator derivations; fixed sentences verbatim; deviation list; historical diagnostics | P1 appendices | Writable now |

Roles stay as PAPER-PLAN-v2 set them, with one change: Sol drafts, Opus re-derives every number from the cited
record, Ed writes the introduction and conclusion, and I give the cold read and hold the final say on claim text.

### 8.2 What must be true by 30 November

1. RL-1 done: P1 on `main` under `docs/paper/paper1/`, the blind commit tagged, CANONICAL corrected.
2. RES merged to `main`, and RL-3's gate passed for every Block 5 number in the paper and on any slide.
3. P1 §§3-6 corrected under RL-5 and filled for Block 5 under RL-2 and RL-4. No `RETIRED_FALLBACK` id is filled
   without RL-2's addendum.
4. BYTES: the BY-01 and BY-02 fixes landed and reviewed, the blinding check resolved, and the stage-1 commitment
   recorded by **19 November** (RL-7). If not, Part 2 is Tier D and is written that way at once.
5. Block 6: the §17 entries entered under RL-6, the production path chosen and built, a custody copy on the Air,
   and the blind dry run started.
6. Talk evidence freeze on 22 November, with the Block 5 slide gated by item 2.
7. A near-complete draft (every section present, tiers stated) on 28 November.

### 8.3 What must be true by mid-December

1. **Scope freeze on 5 December**, recorded in `RUN_STATE.md` before any Block 6 or BYTES number is read: Block 6
   released or Tier C; BYTES stage 2 released by 3 December or Tier D.
2. Fills for whatever was released, each through the same gate as Block 5.
3. One Fable cold read of the whole draft after the freeze; Opus overclaim pass; Ed's introduction and
   conclusion; the bibliography audit; the AI-use statement in the form Ed chooses (E3).
4. Submission on the date Ed confirms (E5). No plan in the repository states it.

### 8.4 MBP time this implies

**No measurement window.** Paper 1's data are all collected. What it needs from the MBP is desk time only, and
none of it may overlap an armed span:

| Need | Size | When |
|---|---|---|
| BYTES stage 1 and commitment | one to a few hours | After the RL-7 fixes; first free gap |
| BYTES held-out agreement, then stage 2 | one to a few hours each | After the commitment is recorded |
| One custody copy to the Air: the nine Block 6 session archives, and the BYTES sessions if the stages move too | a few hours, mostly transfer | Any gap |

About 6 to 12 hours in total. There is a natural slot: W1 cannot register until the claim contract lands and is
adjudicated (item 252), so the MBP has no window to run between R1's chain exit (at the latest 11-11 23:25 PST)
and the W1 arm. Timing is the magistrate's call (item 181). My recommendation to him and the lead is BYTES stage
1 first once its fixes land, then the Block 6 copy. If Ed prefers that Paper 1 never touches the MBP's schedule
again, one copy of both data sets to the Air achieves that, at the cost of a custody change for the BYTES keys
that needs its own ruling.

ALIGN v4 is not on Paper 1's path and Paper 1 takes nothing from its schedule beyond those hours.

---

## 9. Decisions that are Ed's

Only scope, venue and authorship-level choices. Everything else above is ruled or routed.

| # | Decision | My recommendation |
|---|---|---|
| E1 | **Which manuscript is the mid-December capstone submission?** (a) Paper 1, the instrument paper, with a one-page outlook on agent auditing; (b) the tripwire pilot paper of PAPER-PLAN-v2 with Paper 1 compressed into its validation section; (c) both, as separate documents | **(a).** Paper 1's data are all collected and one block is released under a registration. The tripwire paper's headline evidence is two trajectories and a desk subtraction, and its v4 results cannot arrive in time. Paper 1 is also what the v4 and v5 papers will cite |
| E2 | **Venue and length for Paper 1.** Capstone only for now, or written to a conference limit from the start? | Capstone length now. Cut for a venue after the replication and BYTES are both released |
| E3 | **Authorship and AI-use statement.** How agents are credited, whether model families and versions are named, and who writes the introduction and conclusion | Name the families and versions. Ed writes both sections |
| E4 | **Titles.** Paper 1's working title in §8.1. And, if the tripwire manuscript survives E1, whether "Sabotage Leaves an Energy Signature" stays as its title now that option B registers the sabotage-against-benign test with an expected null | Approve the Paper 1 title. Keep the tripwire phrase only as a question |
| E5 | **The capstone due date**, and whether the 30 November talk keeps the tripwire as its headline now that Paper 1 is the paper | Confirm the date. Keep the two-half talk; let half B's instrument slides carry the released Block 5 result |
| E6 | **Priority.** Paper 1 needs Sol and Opus seats for Block 6 and BYTES, and 6-12 hours of MBP desk time, against the standing rule that all spare effort goes to v4 | Approve it. It costs v4 no window, and BYTES is Paper 1's only answer to objection 4 |

---

## 10. Not determined

- Whether BYTES stage 1 has been attempted off the record, and the MBP's free disk after R1.
- Whether a second copy of the Block 6 or BYTES sessions exists anywhere but the MBP.
- The eight dominance R values, the per-cell interval parts and the hazard lines: they are in custody, not in
  RES, and I did not read custody.
- Whether `P1-AUTO-BLINDCHECK` has an answer in a record I did not find.
- The capstone program's requirements for the paper (length, format, whether a pilot study or a measurement
  study fits better). That is Ed's knowledge.
- Design constants in P1 §3-§4 beyond the eight I spot-checked against the registrations.
