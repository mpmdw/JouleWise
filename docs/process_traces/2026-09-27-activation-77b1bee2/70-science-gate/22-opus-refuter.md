# SCI-25G83-CANDIDATE-01 — paired contract-lens refuter (Opus 5.5)

Seat: Opus 5.5, one foreground session, 2026-09-27 ≈16:36–17:05 PDT. Worked from `/Users/edr/code/JouleWise-wt-sci-judge-77b1bee2` (origin/main `e7c8bcc6`). Scratch: `/tmp/opus-sci-77b1bee2/` (`frames.py`, `rederive.py`, `stats.py`).

## 0. Contamination disclosure

- The harness injected the owner's global instruction file, the project CLAUDE files and the memory index before my first action. I opened none of RUN_STATE, TASK_QUEUE, CLAUDE*, AGENTS, memory or skill files. The memory index carries status lines, not B values.
- Section A was written from my own executed evidence **before** the judge's ruling existed (it appeared at 16:52; my re-derivations ran 16:40–16:47).
- Values I read: the 12 member B values, and 8 diagnostic B values that I computed myself for the captures the cell cap excluded (§A1.3). No file in any repository or custody root was modified: `sys.dont_write_bytecode` and `PYTHONDONTWRITEBYTECODE=1` were set on every Python run.

Terms used below. A **capture** is one ≈197 s powermetrics recording of 59 commanded GPU pulses. **B** (`b_fiducial_s`) is the capture's timing bound in seconds: its worst pulse-edge residual plus its clock-alignment bound. A **member** is a capture that is ledger-`valid` and whose stored clock alignment (the **anchor**) resolved. The **cell cap** is `DETECTION_PROJECTION_CELL_BUDGET = 165_000` (`joulewise/powermetrics_fiducial.py:88`): the maximum number of rectangles of candidate edge timings the estimator may evaluate across all 59 pulses before it gives up and records `detection_nonconvergent`. **S**, **C**, **level screen**, **Q99** are as defined in Revision 5 (quoted in A3).

---

# Section A — independent answers (written before the ruling)

## A1. Membership and exclusions

### A1.1 Membership is exact
Executed. The candidate's 12 `member_id`s (W1 d04 d05 d06 d07 d10 d12; W2 d01 d03 d04 d05 d09 d10) equal the set of custody `instrument_evidence.json` files with `status: valid`. Candidate sha256 `dbad7cc7…b5b2` verified. `excluded_members: []`, `battery_confounded_sessions: []`.

I re-ran the pinned estimator (`rederive_detection_from_artifacts`, run checkout `e7c8bcc6`) from raw bytes on all 12 members. All 12 B values reproduce to the last digit, e.g. w2-d10 `0.03807857930294817`, w1-d04 `0.03610911339816257`.

### A1.2 The 12 non-member captures: true causes

The packet's two top-level labels hide three distinct causes. From each capture's `clock_anchor.detail` and `detection_projection.diagnostics`:

| Cause | n | Captures | Mechanism |
|---|---:|---|---|
| Cell cap exhausted (`detection_nonconvergent`, trigger `evaluated_cell_budget`, 165,000 cells) | 8 | W1 d02 d03 d09; W2 d02 d06 d08 d11 d12 | estimator work limit |
| Wall clock moved against monotonic clock > 5 ms during capture (`wall_minus_monotonic_span_exceeded`) | 3 | W1 d08 (51.98 ms), W1 d11 (5.83 ms), W2 d07 (35.90 ms) | anchor precondition |
| No feasible affine clock fit (`affine_clock_fit_empty`) | 1 | W1 d01 | the registered r6 class |

For the 4 anchor failures detection was skipped (`trigger: invalid_anchor_bypass`, 0 cells). Their "0 of 59 pulses" is therefore a consequence of the anchor failure, not a detection result.

### A1.3 Is the cell cap selecting on outcome? (executed; the germane-to-verity check nobody had run)

The cap's own comment and D-143 say it was sized on 2026-08-18 from the 25F84 corpus at ≈120 ms frames: "n=34 full 59-pulse convergences, min 112,205, median 122,044, p95 135,513, max 137,189 evaluated cells … 165,000 clears the observed maximum by 27,811 cells (20.3%)". I measured this epoch:

- Members needed **144,037–163,849** cells, every one above the 25F84 maximum. Three used more than 98.7 % of the cap: w1-d06 163,849; w2-d10 163,405; w2-d03 162,911.
- I re-ran the 8 capped captures with the cap raised to 600,000. **All 8 fit 59 of 59 pulses with no spurious plateau**, needing 165,311–170,965 cells (0.2–3.6 % over). Their diagnostic B values are w1-d02 0.027679, w1-d03 0.024069, w1-d09 0.036909, w2-d02 0.029164, w2-d06 0.026508, w2-d08 0.023351, w2-d11 0.029430, w2-d12 0.027362 s.
- Median native frame length, parsed from every raw plist: members 127.6–130.2 ms, capped captures 127.9–129.8 ms. Across the 20 anchor-resolved captures: cells vs frame length **r = +0.82**; cells vs B **r = −0.055** (Spearman −0.23); frame length vs B r = +0.10.

**Answer.** The cap selects on cadence, not on B. The exclusion is procedurally outcome-blind: a work count fixed by pinned code at capture time, reproducible (`reproducible: true`). It is also empirically outcome-independent on all 20 computable captures. The 4 anchor exclusions read five clock stamps and no power sample, so they cannot depend on B.

Diagnostic only, never operative: with all 20 captures the maximum is unchanged (0.038079 s), range 0.014727 s (candidate S 0.013701), Q99 0.017118 s (candidate C 0.019021), and 3 exceed r7's screen instead of 2. The candidate's S is about 1.0 ms stricter and its C about 1.9 ms looser than the 20-capture figures. These are sampling differences of the expected size.

### A1.4 Registered mechanism, correctly applied? (contract)

Revision 1, lines 165–171, verbatim: "An observation is excluded only if (a) its stored anchor-v3 record shows the estimator's clock-anchor feasibility model admitted no feasible affine fit (affine_clock_fit_empty, the r6 exclusion class, and the ONLY exclusion mechanism registered at this step: an unresolved anchor carrying any other reason refuses issuance instead of quietly excluding the member); (b) a protocol gate fails (plateau, SNR, 59-pulse detection, spurious plateau, edge coverage), which the writer records as ordinary-invalid; or (c) a recorded operator or system event interrupted the window."

- **Cap (8): registered.** The D-078 registry amendment of 2026-08-15 ("bounded pulse-detection projection") registers `detection_nonconvergent` as a condition that "always makes the evidence `invalid`" and fixes it as "a completed `ordinary-invalid` observation". The cap value was frozen by D-143 on 2026-08-18. Revision 1 pins estimator code ("an estimator-code rotation mid-campaign" voids the registration). The four estimator files are byte-identical in the W1 root, the W2 root and main, and equal the candidate's `estimator_code_sha256` and r7's (`386e8254…`, `b583f35a…`, `70f47086…`, `7b9c0d28…`). Correctly applied, but it is a work-limit exclusion wearing the "59-pulse detection" label of route (b).
- **Fit-empty (1):** the registered class. Correctly applied.
- **Clock step (3): needs a reading.** The strict text of (a) says an unresolved anchor with "any other reason refuses issuance". I hold that (a) does not reach these captures, for four reasons. (i) (a) is scoped to "this step", the issuer's read-back of ledger-valid rows (the companion Membership sentence: "Valid registered observations whose stored outcome does not resolve…"). (ii) The ratified refusal-branch statement, item 4(iii), confines the terminal refusal to "a **valid** capture's stored clock alignment". (iii) The D-078 2026-08-15 amendment makes `clock_anchor_unresolved` an invalidating writer condition. (iv) A wall-clock step is "a recorded … system event" under (c), and Revision 5 names "anchor feasibility" among "the physical barriers". It is outcome-blind. However, "quietly" is binding: these three were named in neither the candidate, the packet nor the re-derivation report, so they must be disclosed.

## A2. Arithmetic and proofs

Executed in 80-digit Decimal from the 12 member lexemes: mean 0.029591582579198539, SD 0.004330477884879059, range 0.013701485381050852 → quantized 0.013701 (half-even), S = max(0.013701, 0.010818) = 0.013701. Level screen = 0.038078579302948. Q95 = `0.013479318561660503` and Q99 = `0.01902064410651988` in binary64, both exact to the candidate. C = max(0.010164834757777545, 0.01902064410651988, 0.013701) = 0.01902064410651988. C − S = 0.00531964410651988.

The quantiles t(0.975, 11) and t(0.995, 11) were checked by my own Simpson integration of the t density: CDF = 0.9750000000000001 and 0.9950000000000001. The 80-digit proof itself is NOT EXECUTED by me. The recorded residuals (4e-81, 2e-81) and 57-digit agreement meet the registered bounds (≤ 1e-30; ≥ 30 digits). The Astra re-derivation (MATCH, 0 findings) agrees on every stored value. It re-read the stored evidence and did not re-run detection, which is why it did not see A1.2–A1.3.

## A3. The screen challenge: does sealed Revision 5 remove the veto? Yes.

Registration sha256 `81b65f08…ddf1` verified. Three sealed passages:

> "…and drops Revision 1's “Screen challenge.” as an issuance veto for this epoch." (Revision 5, Authority paragraph)

> "The predecessor screen challenge is recorded as a diagnostic, not an issuance veto for this epoch: on an identical instrument it would falsely refuse 16.3 % of the time." (Issuance arithmetic and barriers)

> "Calendar-day spacing, n ≥ 19, the predecessor screen challenge, and strict S < C are not physical barriers for this epoch."

Decision log, D-126 addendum (2026-09-25): "The old n ≥ 19 floor, calendar-day spacing, screen challenge as issuance veto, and strict S < C are superseded for this registration only. The comparison against the predecessor screen stays diagnostic." Issuer lines 1929–1933 (`if not revision_five and len(challenged) >= …`) implement exactly this. The count of 2 is recorded (`screen_challenge_member_count: 2`). The second diagnostic is false (0.038079 < 0.042622).

## A4. Physics and sanity

- **Epoch higher than r7.** The frames are about 128–130 ms against about 120 ms. Revision 5 states in advance that "B grows with frame length", and the new maximum is not a single outlier. Not an artifact.
- **W2 above W1.** Member means are 0.02788 and 0.03130 s against an SD of 0.0043 with n = 6 each. Not significant, and it shrinks once the capped diagnostics are included.
- **Yield 50 % against ≈79 %.** Fully explained by A1.2: 8 from the cap, 3 clock steps, 1 fit-empty. Without the cap, 20 of 24 (83 %).
- **Display.** All 24 captures sit in one cadence regime: no frame above 183.3 ms, longest 141.6 ms. The slow display regime has medians of 243–248 ms. The actual panel state is not recorded: NOT ESTABLISHABLE.
- **Battery.** All 48 per-slot observations authenticate against their digests and pass the predicate on my parse. The W1 d11 +9 mAh and W2 +12 mAh steps move `AppleRawCurrentCapacity` and `AppleRawMaxCapacity` together, with InstantAmperage 0. That is a gauge re-estimate. The W1 step was already disclosed (activation 3ba66eeb, S4).
- **Registered marks.** Retained B > 0.075 s: 0, so no `excursion_limited`. B > 0.25 s: 0, so no `PLATEAU_INSET_S` refusal. C > S, so `positive_headroom`, not `zero_headroom`. n = 12 is exactly the floor ("Retained n ≥ 12 is the issuance floor"). W3 was not permitted ("W3 is permitted only if the count-only dry run after W2 shows fewer than 12 valid"; the cumulative count is 12).

## A5. My verdict and what D-138 requires next

**PROCEED TO ISSUANCE**, with these contract conditions on the D-138 transaction (the one atomic re-freeze that issues the acceptance):
1. It issues with `estimator_code_sha256` byte-equal to the candidate's. Three unmerged origin branches touch pinned estimator files: `feat/2026-09-04-instrument-path-pin`, `feat/2026-09-04-raw-capture-digest`, `feat/2026-09-24-acc-25g83-v4-rev4`. D-138's inheritance corollary routes estimator changes *into* the atomic re-freeze. Any of them, or a cap re-size, folded into this transaction would pin code that did not derive the members, which Revision 1 treats as voiding.
2. It carries the disclosures: yield causes, cap mis-sizing, the three clock-step exclusions, and the existence of the diagnostic B values.
3. It discharges the custody-repair and predecessor-path ruling conditions. I did not audit them (NOT EXECUTED).

---

# Section B — refutation of the judge's ruling (`21-science-gate-ruling.md`, 16:52)

**Overall.** The judge and I reached the same verdict independently, and the same two unreported findings (F1 cap, F2 clock steps). My A1.3 numbers are an independent second-seat replication of the judge's §2.3, which the judge lists as NOT EXECUTED. Every one of the 20 cell counts and all 8 diagnostic B values match to the digits the judge prints. The clock-step spans also match (51.98 / 5.83 / 35.90 ms). The judge's reading of clause (a) is the same as mine, and I verified the D-078 2026-08-15 registration text it cites. No BLOCKER.

### SHOULD-FIX

**SF-1. Classify F1 against refusal-branch statement item 7 explicitly.**
- Item 7(b) makes a later rejection "for a defect found in the code that derives them" terminal (item 4(a)–(d): Revision 5 ends and all 24 captures become diagnostics). The ruling calls the cap "mis-sized" (D2) and "a sign of an artifact … in the estimator's work cap", but never says whether F1 is a 7(b) defect.
- Without that sentence, the D-138 gate or a later reader can take "mis-sized" as a derivation-code defect and trigger the terminal branch after the fact.
- The ruling should state that F1 is not a 7(b) defect, and why: (i) the cap is a registered (D-078, 2026-08-15), frozen (D-143) and registration-pinned parameter, behaving exactly as registered; (ii) the cap cannot change a converged capture's B. Both seats reproduced all 12 member B values bit-exact, and raising the cap only adds captures; it moves no member value; (iii) it did not select on B.

**SF-2. Bind the D-138 transaction to the candidate's estimator pins.**
- Judge §8 says re-sizing the cap "forces a re-issue" and that the council should rule first. It does not forbid folding the re-size, or any other merge-staged estimator branch, into *this* issuing transaction. D-138's inheritance corollary ("Follow-on work that must touch the same pinned files RIDES THE SAME BRANCH") points the other way.
- The three unmerged estimator-touching branches listed in A5.1 exist on origin today.
- The verdict should say that this issuance pins `386e8254…/b583f35a…/70f47086…/7b9c0d28…` unchanged, and that a cap re-size is a separate, later re-freeze, sequenced after the council ruling the judge recommends.

**SF-3. Name F1 as a downstream verity risk, not only a throughput cost.**
- Judge §8 frames the cap as bracket yield ("one bracket in four"). Under the D-078 2026-08-15 amendment, an invalid pre slot aborts the bracket. The cap now filters production brackets on cadence (r = +0.82), which is a machine-state variable.
- If cadence co-varies with thermal or system state that also moves the measured energy, claim windows are selected on that state.
- The owner's directive makes anything germane to verity mandatory. This should be recorded as a lane that must be resolved or measured before claim-bearing windows run at 25G83. It is not a condition on this issuance.

### NIT

- **N-1.** §2.4 could also cite Revision 1 route (c) ("a recorded operator or system event") and Revision 5's named physical barrier "anchor feasibility". Both support the structural reading of the three clock-step exclusions independently.
- **N-2.** §5 says the W1 d11 +9 mAh step is newly found beyond the charge. It was already disclosed in activation 3ba66eeb item S4. Only the 12 mAh gap between windows is new.
- **N-3.** §8's "one bracket in four" assumes independent per-capture failures at the 50 % rate. The anchor failures (4 of 24) are not cap-related and have no reason to be independent of each other; the figure is illustrative only.
- **N-4.** D6 should say that the diagnostic B values were computed twice, independently (judge and refuter), so that a successor registration's disclosed-design-inputs list names both seats.

### Tier disagreements with the judge
None on the verdict, membership, arithmetic, screen challenge or marks. Three SHOULD-FIX items tighten the ruling's text so that the D-138 gate cannot misread it.

REFUTER: CONCUR
