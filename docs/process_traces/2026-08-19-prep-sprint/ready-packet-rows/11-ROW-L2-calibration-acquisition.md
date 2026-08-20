# ROW L2-CALIBRATION-ACQUISITION — calibration acquisition (GATING)

Original verdict: **NOT-READY (3 blockers / 3 should-fix / 1 struck nit)** — *after* the
falsely-clean refuter attack. **PLUS UNVERIFIED on coverage** (15/16 refuted).

This row is the sitting's only dual verdict. The seat self-reported **READY, coverage 15/16,
0 blockers / 2 should-fix / 2 nits** (sitting-packet-FINAL.md §2 line 27; seat report §7
"READY"). The falsely-clean attack (refuter-outputs/refuter-L2-out.md) flipped it: three NEW
blockers raised, one nit raised to should-fix, one nit killed as a phantom.
council-verdict.md:13-16 records the split explicitly:

> **L2 additionally carries UNVERIFIED on coverage** (its denominator was refuted; charter
> amendment 11 treats the verdicts as distinct — the NOT-READY carries the work orders, the
> UNVERIFIED carries the mandatory re-audit).

Baseline: audit-baseline manifest head `ac3fe1d`; effective audit baseline `8937dec`.
Seat report sha256-16 `54b6e67c24f752e5` — **VERIFIED** by `shasum -a 256` against
sitting-packet-FINAL.md:12.

Charter note for the seat: `docs/process/instrument-readiness-audit-charter.md` was last
committed `6a7849c` (2026-08-13) and has **not been amended since**. It contains the verdict
form (charter:78-90: READY / NOT-READY(+work orders) / UNVERIFIED; "Council READY requires: no
NOT-READY, no UNVERIFIED, all ED-QUALIFICATION rows closed with evidence") and the ED-QUAL/T0
split (charter:70-76). It contains **no** text for "mandatory re-audit" and **no** text for the
ENUMERATING-vs-READY-CANDIDATE sitting distinction — both live only in council-verdict.md
(lines 15-16 and 54-57). The seat is adjudicating against a charter that was never edited to
carry the amendments this sitting is convened under.

---

## L2-1 — detect_pulses region projection has no work budget (NEW BLOCKER, raised from L2's own should-fix)

### (a) Original finding (VERBATIM)

Sitting-packet §4 title:

> - [should_fix] [L2] detect_pulses region projection has no work budget — non-termination on degenerate traces while holding the writer lease

Seat-report §4 full text:

> **L2-1 (should-fix)** — `joulewise/powermetrics_fiducial.py:554` (`_accepted_region_projection`; constants :70/:73). No work budget in the interval branch-and-bound: 1.5 s × 1.5 s bisected to 0.1 ms cells is ~2.25e8 cells/pulse × 59 pulses when the loss surface doesn't prune (degenerate unanchored traces). *Failure scenario:* pre-calibration hits `clock_anchor_unresolved` (recorded real condition, §10/§13.1) with a flat loss surface; the writer computes for hours **holding the writer lease**, the chain has no watchdog, the operator may not touch the Mac (§5C) — the funded window and its one-launch consumed arm capability burn with no governed exit. Consumption soundness unaffected (evidence forced invalid; SIGKILL leaves fail-closed pending state — witness-proven). Also prevents the crash-matrix suite from completing on this host. → **WO-L2-1**: rigorous cell/wall budget → fail-closed `detection_nonconvergent`; and/or skip full-resolution projection when the anchor is unresolved.

Raised to blocker, sitting-packet §9 "L2-falseclean" (VERBATIM):

> - NEW BLOCKER L2-1 (raised from L2's own should-fix): detect_pulses region projection has NO finite
>   work budget; frozen chain calls it synchronously UNDER THE WRITER LEASE (validate_powermetrics_fiducial.py:846
>   acquire, :1509 call, :1037 release; runbook:1017 no watchdog; powermetrics_fiducial.py:555 unbounded loop).
>   Remedy: bounded evaluation/wall budget -> registered invalid-evidence + governed abort.

Citation: sitting-packet-FINAL.md §4 line 136 (title) and §9 lines 382-385; seat report
`docs/process_traces/2026-08-15-readiness-council/seat-reports/L2-CALIBRATION-ACQUISITION-report.md:49`;
refuter verdict `refuter-outputs/refuter-L2-out.md` §"L2-1 — CONFIRMED; severity raised from
should-fix to blocker".

Post-verdict adjudication: labelled **SINGLE-LENS** (council-verdict.md Disposition 5) with a
second distinct-lens refuter ORDERED before implementation. That order was discharged the same
day — council-verdict.md:121-131 ADDENDUM:

> The ordered second-lens refuter (refuter-outputs/sol-refuter-singlelens.md, Sol xhigh,
> execution lens) confirmed all four single-lens claims: L2-1 (refined: the unbudgeted
> projection tree is finite but intractably large — the operational lease-held blocker stands
> verbatim) …

The refinement in the refuter's own words (`sol-refuter-singlelens.md` §F1): 14 subdivisions per
dimension ⇒ up to 2^28 = 268,435,456 leaves, ~537 M node visits per pulse × 59 pulses —
"operationally an unbounded hang even though the tree is mathematically finite". Severity
**remains blocker**.

### (b) What changed since 2026-08-15

The remedy **landed and is MERGED TO MAIN**, contrary to what the queue and kernel still say.

- `ceda7a6` (2026-08-15 22:33 PDT) — "WO-DETECT-PULSES-BUDGET: deterministic projection budget +
  anchor-unresolved bypass + governed nonconvergent abort".
- `ac98695` — "Fix round 1 (lens F1/F2/F3 + S1/S2/N1): deterministic receipt fields uniform
  across triggers …, fail-closed serializer invariant (nonconvergent can never carry
  fits/bound/valid — refuses, with discriminating regression), bypass-with-resolved-anchor
  refusal, full-artifact byte-stability hash, wall-path regression".
- `891af00` — calibration-side stage 2 (launch-lineage), on the same branch.
- `e22e658` — merge of origin/main into `impl/wo-detect-pulses-budget` (the branch head named by
  the kernel note).
- `54f990d` (2026-08-18 06:25 PDT) — "**D-138** detection-budget ruling: DETECTION_PROJECTION_CELL_BUDGET
  100k -> 165k, D-079 r2 re-issued in place, dual-generation pins and the _v2 family regenerated".
- **WHERE it lives: MERGED TO MAIN.** All of the above are ancestors of `origin/main`
  (`0099382`), arriving via **PR #159** — `04e34ee` "Merge pull request #159 from
  mpmdw/integration/phase2-transaction" (2026-08-18 10:28 PDT). Verified:
  `git merge-base --is-ancestor ceda7a6 origin/main` → true;
  `git log --oneline impl/wo-detect-pulses-budget ^origin/main` → **empty** (the branch is fully
  contained in main).

Verified in the code at the current head:

- `joulewise/powermetrics_fiducial.py:87` `DETECTION_PROJECTION_CELL_BUDGET = 165_000`
  (corpus-basis comment at :80-86 records median 122,044 / p95 135,513 / max 137,189 and states
  "Budget exhaustion remains fail-closed: it yields registered invalid evidence, never a partial fit").
- `:91` `DETECTION_PROJECTION_WALL_BUDGET_S = 120.0`, described in-code as a *supplementary*
  host-safety deadline, the cell budget being "the primary reproducible mechanism".
- `:92` `DETECTION_NONCONVERGENT = "detection_nonconvergent"`; registered in the reason tuple at
  `:164`; raised as a typed exception at `:517`; emitted as `reasons=(DETECTION_NONCONVERGENT,)`
  and `projection_disposition=DETECTION_NONCONVERGENT` at `:1004,:1008`.
- `:953` guards the `clock_anchor_unresolved` bypass ("clock_anchor_unresolved bypass requires …").
- Discriminating regressions exist in the crash matrix:
  `tests/test_calibration_writer_crash_matrix.py:1244`
  `test_detection_budget_refuses_with_terminal_custody_and_released_lease` and `:1340`
  `test_post_detection_budget_has_terminal_custody_and_released_lease` — i.e. the lease-release
  half of the blocker has a named test.
- D-143 is the authority for 165,000: `docs/decision_log.md:166` (index) and the `## D-143`
  body at `docs/decision_log.md:8821-8827`; basis custody
  `docs/process_traces/2026-08-18-shakedown-first-light/03-budget-calibration-sweep.md`
  (34 full 59-pulse convergences over the retained v3 corpus; min 112,205 / median 122,044 /
  max 137,189; 165,000 = max + 20.3%).

**Reconciliation the assignment asked for, stated plainly:**

| Source | What it says | Truth at `origin/main` `0099382` |
|---|---|---|
| `TASK_QUEUE.md:317-334` (hand-authored note) | "Implementation on `impl/wo-detect-pulses-budget` adds the frozen **100,000-cell** whole-detection budget … On-host the formerly blocked crash matrix completed all **14 tests in 98.964 seconds**" | **STALE on both counts.** The budget on main is **165,000** (D-143, `54f990d`); the module now defines **15** test methods (`grep -c "    def test_"` = 15). The 14/98.964 s figure belongs to `ceda7a6` on the branch, pre-D-143 and pre-stage-2. |
| Kernel `docs/process/state_kernel.json` `/tasks/WO-DETECT-PULSES-BUDGET` | `"status": "partial"`, note: "COMPLETE Phase-2 payload on impl/wo-detect-pulses-budget @ e22e658 (main-synced) … **MERGE-STAGED** for the atomic re-freeze (D-138)" | **STALE.** The merge happened (PR #159). The generated A-row renders as "A5 … PARTIAL; READY [AGENT]" at `TASK_QUEUE.md:539` and `:633`, i.e. the queue still advertises this as *queued work*. |
| Commit subject `54f990d` | "**D-138** detection-budget ruling" | Mislabelled: D-138 is the *merge-staging* rule (`decision_log.md:163`); the budget ruling is **D-143** (`decision_log.md:166`). |

So: **the WO landed on MAIN**, at the D-143 value, and the two work-selection surfaces that are
supposed to be authoritative both still say otherwise. The remaining, genuinely-open half of the
A5 row per the hand-authored note is "kernel/checklist closure and the later D-079 acceptance/pin
re-freeze remain lead-owned" — the D-079 r2 re-issue is itself inside `54f990d`, which is on main.

### (c) Candidate disposition for the seat

**READY-EVIDENCE-ATTACHED (code) / STILL-OPEN (bookkeeping).** The seat is adjudicating whether a
merged, delta-audited, regression-bearing budget cure closes a launch-blocking defect while the
project's declared sole work-selection authority (the kernel) still renders the same work order
as PARTIAL/READY-[AGENT] with a branch-only, wrong-numbered note — and whether a re-parameterised
budget (100k→165k) fitted to the retained corpus needs its own coverage argument.

### (d) Skeptical probes

1. `git merge-base --is-ancestor ceda7a6 origin/main; git log --oneline impl/wo-detect-pulses-budget ^origin/main`
   — confirm the branch is fully in main and nothing was left behind.
2. Run `python3 -m unittest tests.test_calibration_writer_crash_matrix` at `origin/main` on a
   quiet bench, unpiped to a file. Does the module complete? How many tests, what wall time? The
   only completion evidence in the record is branch-era (14/98.964 s) or unlocatable (see
   L2-EDQ-1 probe 2).
3. D-143 fitted 165,000 to **34 retained v3 traces, all at the same 100 ms configured interval**
   (`03-budget-calibration-sweep.md:58`, flag F1: "not an unobserved future trace class").
   Ask: what happens on the FIRST successor-pack capture whose cell count exceeds 165,000 —
   registered invalid evidence, i.e. a burnt funded window that now fails *by budget* rather than
   by hang. Is that trade ruled anywhere?
4. `grep -n "clock_anchor_unresolved" scripts/validate_powermetrics_fiducial.py` — does the writer
   actually take the zero-cell bypass on the recorded real degenerate condition, or only inside
   `powermetrics_fiducial.py`? The original blocker was about the writer's synchronous call under
   the lease.
5. Inspect the two named lease regressions (`:1244`, `:1340`) and confirm they assert **lease
   released** and **terminal custody written**, not merely that the refusal code appears.
6. The wall deadline is 120 s while the observed corpus needs up to 137,189 cells — on a loaded
   host, which fires first? The singlelens refuter explicitly warned the wall "should not be the
   sole reproducibility mechanism"; check that a wall-trigger produces the same registered
   evidence bytes as a cell-trigger (`ac98695` claims it demoted wall-trigger fields to
   "labeled non-reproducible diagnostics" — verify).

---

## L2-COV-1 — the UNVERIFIED: coverage 15/16 refuted as a self-selected universe

### (a) Original finding (VERBATIM)

Sitting-packet §9 "L2-falseclean":

> - NEW BLOCKER L2-COV-1: coverage 15/16 REFUTED — self-selected universe; omitted contracts, bootstrap/
>   backfill scripts, 23-test three-window lifecycle module; crash matrix is 13 tests not 16; real direct
>   test universe 251.

Refuter machine verdict (`refuter-L2-out.md`, verdict.coverage):

> "reported": "15/16", "verdict": "REFUTED", "reason": "The universe is self-selected and
> inconsistently atomized; E4 is explicitly partial, E15 includes two skips, E16 contains 13
> rather than 16 tests, and directly scoped artifacts/tests were omitted.",
> "direct_test_universe": 251, "omitted_live_three_window_tests": 23

Council record: sitting-packet §9 ADJUDICATION TALLY line 492 lists "L2 coverage denominator
false" among the NEW DEFECTS FOUND BY REFUTERS; council-verdict.md:18-22 generalises it:

> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every
> seat's evidence universe was self-nominated, and the one denominator adversarially tested fell.
> Closing all listed work orders does not entitle READY; the READY-candidate re-audit must
> re-enumerate every universe independently and run the adversarial coverage attack as a standing
> packet element.

Citation: sitting-packet-FINAL.md §9 lines 386-388; refuter-outputs/refuter-L2-out.md
§"L2-COV-1 — CONFIRMED blocker: 15/16 is not the real universe"; second lens
`refuter-outputs/sol-refuter-singlelens.md` §F2 ("Total: exactly 251 tests"), cleared of the
SINGLE-LENS label by council-verdict.md:126 ("L2-COV-1 (251-test universe re-enumerated exactly)").

### (b) What changed since 2026-08-15

**WO-L2-REAUDIT was delivered the same day.**

- Custody: `docs/process_traces/2026-08-15-l2-reaudit/` — `README.md`, `reaudit-prompt.md`,
  `reaudit-report.md`. Custody commit `0f886d3` (2026-08-15 23:29:24 PDT, "Custody dir local-date
  correction (08-16 → 08-15; audit completed 23:29 PDT 08-15)").
- **WHERE it lives: MERGED TO MAIN** (`git merge-base --is-ancestor 0f886d3 origin/main` → true).
- Queue closure: `TASK_QUEUE.md:103` Completed row, "DELIVERED same-day".
- The audit ran at main head `fac87d1` (report workspace block; V9 confirms
  `HEAD == origin/main == fac87d1`, clean tree) — **not** at the sitting baseline `8937dec`.

**What the trace actually verified** (read from `reaudit-report.md`, not from the queue summary):

- **Universe/accounting coverage: 251/251 test IDs enumerated and dispositioned** (report
  §"Coverage accounting"; verdict `"coverage": "VERIFIED"`).
- **Current-head execution: 247/251** = **242 passing test bodies + 5 declared skips**;
  **4 crash-matrix IDs unexecuted**, named individually:
  `test_every_exact_stage_pre_and_post_sigkill_reaches_fresh_governed_exit`,
  `test_torn_and_fsynced_append_boundaries_resume_from_fresh_processes`,
  `test_two_presenters_racing_one_capability_authorize_exactly_one`,
  `test_two_process_lease_contention_then_fresh_resume` — **attributed to
  WO-DETECT-PULSES-BUDGET** (+ WO-CRASHMATRIX-RELIABILITY + the test-harness clause of
  WO-SAMPLER-SUPERVISOR).
- Per-module table: authentication_io 18 · bracketing 42 (1 skip) · custody_store 7 ·
  calibration_exits 30 (316.710 s) · calibration_ledger 72 (1 skip) · live_three_window 23
  (3 skips) · powermetrics_fiducial 46 · crash_matrix 13 (9 pass, 4 unexecuted) = **251**.
- The 5 skips are itemised: 2 needing lead-reviewed D-079 import inputs, 3 marked "U2 successor
  engine pending".
- **Procedure sensitivity probes ×3** (P1/P2/P3): each renamed one `test_*` in a `$TMPDIR` copy
  and showed the total move 251→250 — i.e. the procedure responds to membership, it is not
  reciting a memorised number.
- **Non-test universe independently traced: 26 paths/classes; 25 present in checkout; 1 absent**
  (the untracked production ledger `runs/calibration_observation_ledger.jsonl`), explicitly "not
  silently treated as examined".
- **Adversarial coverage attack executed** (9 failure classes incl. 2 novel of the auditor's own):
  two EXPLICIT GAPS recorded — non-termination/work budget, and the missing-ledger-parent
  diagnostic route — both dispositioned to existing registered work orders, no new WO minted.
- New finding **L2R-2** (missing-parent FileNotFoundError, V7 reproduced) folded into the L2-2
  batch, explicitly "not a new work order".
- Explicit non-claims (report §Verdict): "It does not claim 251/251 current-head execution, does
  not certify the remediation branch, and does not alter the council's separate NOT-READY machine
  verdict." Flag F3: "The 14-OK/99s evidence belongs to ceda7a6 on impl/wo-detect-pulses-budget,
  not fac87d1; remediation was not graded."

**The two questions the assignment posed, answered from the primary evidence:**

**(i) Does a same-day re-audit satisfy the charter's MANDATORY re-audit for an UNVERIFIED?**
The charter as committed (`6a7849c`) contains **no re-audit clause at all** — the obligation
exists only in council-verdict.md:15-16, and it names no independence conditions (fresh session,
different model, elapsed time, cold packet). Facts for the seat to weigh: the re-audit ran the
same calendar day (verdict recorded 2026-08-15; audit completed 23:29 PDT the same date), by the
**same model class as the attacker** (Sol xhigh — the falsely-clean refuter was also Sol xhigh),
commissioned and prompted by the same magistrate, at a *different* head (`fac87d1`) than the
sealed baseline (`8937dec`). Rule 11's cold-gate shape (fresh instance + cross-model refuter) was
**not** applied to it; no second lens reviewed the re-audit.

**(ii) Was its universe independently enumerated — the whole point?**
Procedurally, yes and it is replayable: `reaudit-prompt.md` obligation 1 forbids inheriting any
prior denominator, the report states a six-step derivation procedure (charter nouns → entry
points → whole modules, "Do not select favorable individual methods" → explicit exclusion list
→ loader with zero errors), and three negative probes demonstrate sensitivity. **But** the
outcome is numerically **identical to the refuter's**: the same eight modules, the same per-module
counts, the same 251 — and `reaudit-prompt.md` itself pre-loaded the answer's neighbourhood by
directing the auditor to read council-verdict.md, telling it the crash matrix cannot complete
locally, naming the remediation branch, and pointing at a specific worktree path for the
"14-OK/99s completion evidence". Convergence on 251 is therefore consistent with independent
derivation **and** with anchoring; the sensitivity probes discriminate against *memorisation of a
total*, not against *inheriting a module list*. Note also the re-audit changed the **unit of
counting** (test IDs + a separate 26-item non-test list) rather than re-deriving the seat's own
16-item artifact universe, so "15/16" was never re-scored on its own terms — it was replaced.

**Scope note:** council-verdict.md Phase 3 orders "adversarial coverage re-enumeration of **all**
universes". Only L2's has been done. No other seat's denominator has been re-enumerated.

### (c) Candidate disposition for the seat

**READY-EVIDENCE-ATTACHED, with the independence question live.** The seat is adjudicating
whether a same-day, same-model-class, magistrate-prompted re-audit — replayable, sensitivity-
probed, and honest about its four unexecuted IDs — discharges a MANDATORY re-audit whose only
written home is the verdict itself, and whether coverage can be VERIFIED for L2 while the Phase-3
order to re-enumerate every other seat's universe is untouched.

### (d) Skeptical probes

1. Re-run the enumeration cold: from the charter nouns alone, without reading
   `reaudit-report.md`, does an independent party reach the same eight modules? Specifically ask
   why `tests/test_d078_reason_registry` (13 tests, run as "corroborating") is *outside* the
   denominator while `test_authentication_io` is inside.
2. `diff` the prompt against the result: `reaudit-prompt.md` names the branch, the caveat, and a
   worktree path. Would the auditor have found the four unexecuted IDs and their attribution
   without being told the budget cure exists?
3. Ask for the raw run logs behind V2-V6. The report pastes tails only; the T10 session report's
   anomaly A-3 shows this project has already lost one claimed suite log.
4. Re-run the enumeration at **current** `origin/main` (`0099382`). The crash matrix now has **15**
   methods, not 13 — so the 251 denominator is already stale by 2. Does the coverage verdict
   survive re-derivation at the head the READY-candidate sitting is actually judging?
5. The non-test universe (26) was never reconciled with the seat's 16-item universe. Ask which of
   the seat's original E1-E16 rows map where, and whether "15/16" is being retired or silently
   superseded.
6. Check whether any *other* seat's denominator has been re-enumerated (Phase 3). If not, the
   council's own generalisation — every universe was self-nominated — remains untested for 10 seats.

---

## L2-EDQ-1 — charter forbids deferred ED-QUALIFICATION at READY; live writer/sudo + crash-matrix qualification open

### (a) Original finding (VERBATIM)

Sitting-packet §9 "L2-falseclean":

> - NEW BLOCKER L2-EDQ-1: charter forbids deferred ED-QUAL at READY; live writer/sudo + crash-matrix
>   qualification open.

Refuter body (`refuter-L2-out.md` §L2-EDQ-1):

> The charter says stable capabilities such as sudo powermetrics behavior must be qualified before the sitting and "cannot be deferred" ([instrument-readiness-audit-charter.md](…:70)); council READY requires all ED-QUALIFICATION rows closed at lines 81–84. L2 nevertheless leaves real-scale writer/sudo behavior and its own crash-matrix qualification open. Thus even absent L2-1, this report could be UNVERIFIED, not READY.

The two rows themselves, sitting-packet §5 (VERBATIM):

> - [L2] EDQ-L2-1 (stable capability): execute tests.test_calibration_writer_crash_matrix to completion on the quiet bench at the audit-baseline head and record pass + wall time. On the audited host it cannot complete (finding L2-1); CI exclusive-job green at the baseline head corroborates but a bench execution closes the row with local evidence.
> - [L2] EDQ-L2-2 (stable capability; runbook-mandated non-delegable): the SS5C lead live verification on the exact reviewed measurement checkout — frozen plan's literal readiness-validator command plus the complete under-lease synthetic rehearsal (real reservation CLI --execute + production writer lifecycle through BOTH slots against a synthetic root), requiring the D-134 dry-run receipt PASS/NOT_APPLICABLE with the reviewed HEAD + committed-pack digest. This audit replayed the equivalent in scratch; the runbook requires it on the production checkout with the frozen plan, which no sandboxed seat can perform.

Second lens (`sol-refuter-singlelens.md` §F3, CONFIRMED): "Three 600-second loaded-host failures
are durably recorded, WO-CRASHMATRIX-RELIABILITY remains open, and live writer/sudo
ED-QUALIFICATION remains explicitly ED-OWED." Cleared of SINGLE-LENS by council-verdict.md:126-127.

Citation: sitting-packet-FINAL.md §9 lines 389-390, §5 lines 181-182; refuter-outputs/refuter-L2-out.md;
refuter-outputs/sol-refuter-singlelens.md §F3.

### (b) What changed since 2026-08-15

**EDQ-L2-1 (crash matrix to completion, bench, recorded wall time) — partial, and the evidence is
not locatable.**

- The nearest thing to a closure is a RUN_STATE line at commit `62c6a06`:
  `git show 62c6a06:RUN_STATE.md` lines 30-31 — "canonical baseline + crash-matrix **(15/15 OK
  quiet)** logged". **WHERE it lives:** that text is *not* in RUN_STATE at the current head
  (`grep "15/15" RUN_STATE.md` → no match); it survives only in git history.
- The T10 session report contradicts its own corroboration —
  `docs/run_reports/2026-08-18-t10-session.md:576-586`, anomaly **A-3** (VERBATIM):

  > **A-3 — the quiet-slot canonical suite and crash-matrix logs are not locatable, and the "13" in the load run does not reconcile.** The quiet-slot rule required **full unpiped output to a file** for both the canonical suite and the crash-matrix rerun; no such file exists in the session scratchpad or any worktree scratch searched by mtime and size. The **15/15 OK quiet** result is corroborated only by the magistrate's RUN_STATE line at `62c6a06`. … The load run's recorded "**errors=3 of 13**" cannot be reconciled with that count … Treated here as: quiet rerun 15/15, load run failed with masked detail.

- Note the row's own wording: "at the **audit-baseline head**". `62c6a06` is a Phase-2 transaction
  head, not `8937dec`/`ac3fe1d`, and the module has since gained two methods.
- **WO-CRASHMATRIX-RELIABILITY: STILL OPEN.** It exists only as a hand-authored TASK_QUEUE section
  (`TASK_QUEUE.md:336-360`) — **not** in `docs/process/state_kernel.json`
  (`grep CRASHMATRIX docs/process/state_kernel.json` → no match) and **not** in the Completed
  table. Its closure condition is unmet on its own terms: "the module completes under 15 minutes
  on a hosted runner with no internal per-case timeout, and the exclusive-job ceiling tightens
  accordingly." The three 600-s loaded-host failures the second lens cited are recorded verbatim
  in that same section. RUN_STATE:686-689 still lists it as open debt ("bench canonical suites
  carry the known 3-test load-pathology trio — disposition recorded each time").

**EDQ-L2-2 (§5C non-delegable lead live verification) — NO-REPAIR-FOUND.**

- Searched: `grep -rn "EDQ-L2-1\|EDQ-L2-2"` across `docs/`, `TASK_QUEUE.md`, `RUN_STATE.md` —
  **zero hits outside the 2026-08-15 council trace**. Neither row ID is tracked anywhere.
- The closest live instrument is `docs/process/rehearsal-operator-card.md` (the E-4→E-9 +
  author→ARM→verify→consume dress rehearsal against scratch custody, with a `generate_arm_readiness.py
  dry-run` step at :38, targeting measurement checkout `/Users/edr/JouleWise-measurement-20260818`
  and scratch root `~/JouleWise-window-custody/ed-qual-20260817/rehearsal`). Its status is
  **OPEN**: `docs/process/ed-morning-packet-2026-08-18.md:126` — "OPEN: the dress rehearsal (item
  4) only"; the T10 report's qualification table (`docs/run_reports/2026-08-18-t10-session.md:110`)
  records "**Dress rehearsal | OPEN** — gated on the frozen `_v2` alpha pack".
- RUN_STATE:540-546 and :620-624 still carry "dress rehearsal E-4→E-9 + author→arm→verify→consume
  vs scratch custody" under **ED-OWED**.
- Note the rehearsal as carded is against the `_v2` alpha pack; the Phase-2 transaction has since
  produced a `_v3` family (`freeze-0003`), so even the carded rehearsal may be head-stale.

**Cross-reference (belongs to the ED row file, recorded here as pointers only):** the 2026-08-17
Ed qualification evening (custody `~/JouleWise-window-custody/ed-qual-20260817/`, off-repo;
summarised at `docs/run_reports/2026-08-18-t10-session.md:98-112` and
`docs/process/ed-morning-packet-2026-08-18.md:110-127`) closed D-127 sudoers, sampler lifecycle,
rail probe, backlight rows, ED-QUAL-L4-1 decisive replay, and ED-Q-L9-3. **Neither EDQ-L2-1 nor
EDQ-L2-2 appears in that ledger.**

### (c) Candidate disposition for the seat

**STILL-OPEN.** The seat is adjudicating whether L2's two ED-QUALIFICATION rows can be treated as
closed when (i) the only crash-matrix completion claim is a one-line RUN_STATE assertion whose log
the project's own session report could not find, recorded at the wrong head against a module that
has since changed shape, and (ii) the §5C non-delegable live verification has no tracking row, no
evidence, and its nearest carded instrument is still OPEN against a now-superseded pack family —
against a charter that says stable evidence "cannot be deferred" and that READY requires all
ED-QUALIFICATION rows closed with evidence.

### (d) Skeptical probes

1. Ask for the crash-matrix log file. `docs/run_reports/2026-08-18-t10-session.md:576` says it does
   not exist. If it still does not, the row has an assertion, not evidence.
2. Re-run the module at `origin/main` on a quiet bench with `> log 2>&1` (unpiped, per the
   quiet-slot rule) and record 15/15 + wall time. Compare against the branch-era 98.964 s.
3. `grep -rn "EDQ-L2-2" .` — confirm for yourself that the non-delegable §5C row is tracked
   nowhere. Then ask which artifact would record its closure if it happened.
4. Does the `_v2`-targeted `rehearsal-operator-card.md` still execute against the `_v3`
   freeze-0003 family? If not, EDQ-L2-2's instrument needs rebuilding before it can be run.
5. WO-CRASHMATRIX-RELIABILITY is registered *outside* the generated kernel region — exactly the
   bifurcated-authority defect L1-B3 named. Ask whether a work order invisible to
   `gen_state --check` can be said to be "open" in any binding sense.
6. The charter text the refuter cited (charter:70 "stable evidence cannot be deferred") is
   unchanged. Ask directly: does the council intend to enforce it at this sitting, or amend it?

---

## L2-2 — readiness/session-status crash with an unregistered raw traceback when the ledger parent directory is missing

### (a) Original finding (VERBATIM)

Sitting-packet §4 title:

> - [should_fix] [L2] readiness/session-status crash with an unregistered raw traceback when the ledger parent directory is missing

Seat-report §4:

> **L2-2 (should-fix)** — `joulewise/calibration_ledger.py:2885` via `writer_lease_is_live`, uncaught at `scripts/recover_calibration_ledger.py:412/:321`. Missing ledger **parent directory** → raw traceback (exit 1) on the diagnostic readiness/session-status surfaces instead of a registered refusal — an unmapped failure ends the night per §5C rule 4 where a governed `physical_ledger_unreadable`-family refusal (with its §10 row) should. *Bounded:* the frozen plan pins `CALIBRATION_LEDGER` to `/Users/edr/code/JouleWise/runs/...` which exists (verified live), so the documented night path is unaffected; trigger requires a mis-pointed path. → **WO-L2-2**.

Refuter: CONFIRMED should-fix (sitting-packet §9 line 391: "L2-2 missing-parent raw traceback
CONFIRMED should-fix (typed refusal remedy)."). Remedy shape endorsed in `refuter-L2-out.md`
§L2-2: "translate this path into an existing registered unreadable/unsafe-ledger refusal without
creating directories during diagnostic readiness."

Citation: sitting-packet-FINAL.md §4 line 137, §9 line 391; seat report :51;
refuter-outputs/refuter-L2-out.md §"L2-2 — CONFIRMED should-fix" + V6.

### (b) What changed since 2026-08-15

**NO-REPAIR-FOUND.** The defect is intact at the current head.

- `joulewise/calibration_ledger.py:2885` — `canonical_parent = canonical_path.parent.resolve(strict=True)`
  still outside the typed-error conversion (unchanged; the seat cited :2885, the refuter :2881 —
  same construct).
- `scripts/recover_calibration_ledger.py:484` — still the **only** `except CalibrationLedgerError`
  in the file; `grep -n "FileNotFoundError\|physical_ledger_unreadable" scripts/recover_calibration_ledger.py`
  → no match.
- Independently re-reproduced **after** the verdict by the re-audit at `fac87d1`:
  `docs/process_traces/2026-08-15-l2-reaudit/reaudit-report.md` V7 (exit 1, `FileNotFoundError`)
  and finding **L2R-2** — "The exact missing-parent route is uncovered and still fails outside the
  refusal registry … No enumerated test constructs this exact absent-parent diagnostic route. The
  generic `calibration_physical_ledger_unreadable` public witness does not cover it." Disposition:
  folded into the council's L2-2 batch, "not a new work order".
- No work order exists: `grep -rn "WO-L2-2" TASK_QUEUE.md docs/process/state_kernel.json` → no
  match. The council's "should-fix batch" (council-verdict.md:85-87) names sweep items and L11
  paper corrections; L2-2 is not enumerated there.
- Searched: TASK_QUEUE Completed table, kernel tasks, `git log --oneline -S"parent.resolve"` on the
  two files. Nothing.

**WHERE it lives: nowhere — no branch, no commit, no queue row.**

### (c) Candidate disposition for the seat

**NO-REPAIR-FOUND.** The seat is adjudicating a confirmed should-fix that has been reproduced
twice (refuter V6, re-audit V7), carries an agreed remedy shape, and has no work order, no owner,
and no code change — plus the second-order question of whether "folded into the L2-2 batch"
means anything when the batch does not exist as a tracked row.

### (d) Skeptical probes

1. Reproduce: `python3 scripts/recover_calibration_ledger.py --ledger <tmp>/absent/ledger.jsonl
   --head-pin configs/calibration/calibration_ledger_head.json readiness --phase terminal` at
   `origin/main`. Expect exit 1 + raw `FileNotFoundError`.
2. `grep -rn "WO-L2-2\|L2-2 batch" TASK_QUEUE.md docs/process/state_kernel.json` — is there a
   tracked home for the "batch" the re-audit folded L2R-2 into?
3. The seat called this bounded because the frozen plan pins an existing path. Check whether the
   `_v3` successor packs' `calibration_plan.json` still pin `CALIBRATION_LEDGER` to an existing
   path, and whether the rehearsal/scratch-root routes (which *do* invent paths) can hit it.
4. §5C rule 4 turns an unmapped failure into an ended night. Confirm the runbook still says that,
   and that `calibration_physical_ledger_unreadable` has a §10 row this path could be mapped onto.

---

## L2-3 — Runbook needs_pin_commit bullet is unscoped vs the by-design PHYSICAL_AHEAD pre-slot relation (RAISED nit → should-fix)

### (a) Original finding (VERBATIM)

Sitting-packet §4 title:

> - [nit] [L2] Runbook needs_pin_commit bullet is unscoped vs the by-design PHYSICAL_AHEAD pre-slot relation

Seat-report §4:

> **L2-3 (nit)** — runbook :421–423 vs `calibration_ledger.py:4949`: "needs_pin_commit: true ends a 2 a.m. attempt" is unscoped, but pre-slot readiness reports `needs_pin_commit: true` whenever ready (PHYSICAL_AHEAD is the required mid-bracket relation). Mechanical reading aborts every legitimate resume. → **WO-L2-3** (scope the bullet).

Post-verdict adjudication — RAISED, sitting-packet §9 line 392-393:

> - L2-3 needs_pin_commit contradiction CONFIRMED, RAISED nit->should-fix (can mechanically abort every
>   correct pre-slot session).

Refuter body (`refuter-L2-out.md` §L2-3): "The ambiguity can mechanically abort every correct
session, making it launch-relevant. Remedy should align semantics, preferably making
`needs_pin_commit` terminal-phase-specific; merely adding prose is weaker but acceptable if it
explicitly exempts an authenticated open-session pre-slot extension."

Citation: sitting-packet-FINAL.md §4 line 138, §9 lines 392-393; seat report :53;
refuter-outputs/refuter-L2-out.md §"L2-3 — CONFIRMED, but severity is should-fix rather than nit".

### (b) What changed since 2026-08-15

**NO-REPAIR-FOUND.** Both halves of the contradiction are byte-unchanged from the audit baseline.

- Runbook prose, current head `docs/phase_2/window_runbook.md:453-454`:
  "- [ ] Treat `needs_pin_commit: true` as desk work that ends a 2 a.m. attempt. / It never
  licenses an uncommitted-pin override." — **identical** to the baseline text at
  `git show ac3fe1d:docs/phase_2/window_runbook.md` line 421 (line number moved 421→453; the
  sentence did not change). The other two sites are likewise unchanged: :991 ("`needs_pin_commit:
  true` is desk work and ends the attempt; no override exists at night") and the §10 refusal row
  at :1573.
- Code, current head `joulewise/calibration_ledger.py:4949`:
  `needs_pin_commit=relation is PinRelation.PHYSICAL_AHEAD` — unchanged. The field is set from the
  bare pin relation with no phase discrimination; the other emitters (`:5202` `candidate is not
  None`, `:5247` `status["pin_relation"] == "physical_ahead"`, `:5271` hardcoded `True`) are also
  unchanged.
- No work order: `grep -rn "WO-L2-3" TASK_QUEUE.md docs/process/state_kernel.json` → no match.
- Searched additionally: `git log --oneline origin/main -- docs/phase_2/window_runbook.md` for any
  post-council prose fix touching this bullet; none.

**WHERE it lives: nowhere.**

### (c) Candidate disposition for the seat

**NO-REPAIR-FOUND.** The seat is adjudicating a should-fix (raised from nit precisely because it
is launch-relevant — a mechanical reading of the runbook aborts every legitimate pre-slot session
at 2 a.m.) that has no code change, no prose change, and no work order, on a runbook the operator
is instructed to follow literally.

### (d) Skeptical probes

1. Read `window_runbook.md:453` and `:991` aloud as a tired operator at 2 a.m., then run the
   pre-slot readiness command and observe `needs_pin_commit: true` on the healthy path. Does the
   runbook, as written, tell them to stop?
2. `git show ac3fe1d:docs/phase_2/window_runbook.md | sed -n '421p'` vs current `:453` — confirm
   byte-identity, i.e. nothing was quietly fixed.
3. Ask whether the T-0 producer work (`scripts/capture_t0_step.py`, PR #152) or the launch-binding
   stages changed which surface the operator actually reads at E-8/E-9 — if the reservation CLI is
   now wrapped, does the bullet still apply to anything the operator sees?
4. Does the D-134 dry-run receipt path emit `needs_pin_commit` too (`:5202`, `:5247`)? If so, the
   rehearsal will hit the same ambiguity.

---

## L2-4 — Idempotent re-reservation returns status:reserved without re-printing calibration_pre_reserve_authorized

### (a) Original finding (VERBATIM)

Sitting-packet §4 title:

> - [nit] [L2] Idempotent re-reservation returns status:reserved without re-printing calibration_pre_reserve_authorized

Seat-report §4:

> **L2-4 (nit)** — `reserve_calibration_window_bracket.py:172–201`: idempotent resume returns `status: reserved` without re-printing `calibration_pre_reserve_authorized`; §5C requires both markers. Harmless (byte-identical ledger, executed), but document the resume shape. → **WO-L2-4**.

Refuted, sitting-packet §9 line 394:

> - L2-4 idempotent-marker WO REFUTED as phantom (runbook forbids re-reserving; reprint would mislead) — drop WO-L2-4.

**Post-verdict adjudication: STRUCK.** council-verdict.md:44-45, ADJUDICATED DISPOSITIONS item 4:

> 4. **Struck findings:** L8-B4 (both lenses: wrong-path artifact; correct fail-closed refusal),
>    WO-L2-4 (phantom), F4's timing premise (privilege gap survives inside WO-T0-PRODUCER).

Also recorded in the §9 ADJUDICATION TALLY line 487: "DEAD: … WO-L2-4 (phantom)".

Citation: sitting-packet-FINAL.md §4 line 139, §9 lines 394 and 487; seat report :55;
refuter-outputs/refuter-L2-out.md §"L2-4 — REFUTED as a defect"; **council-verdict.md Disposition 4**.

### (b) What changed since 2026-08-15

Nothing was implemented, correctly: the work order was dropped at the sitting. The refuter's
residual suggestion — "at most document that idempotent API replay is non-authorizing" — has **no
corresponding change**: `grep -rn "non-authorizing\|idempotent" docs/phase_2/window_runbook.md`
finds no such note, and the runbook's forbidding text (`window_runbook.md:952` per the refuter's
citation, "On restart, do not reserve again … run `session-status`") is what makes the absence
correct.

**WHERE it lives: n/a — struck, not implemented.**

### (c) Candidate disposition for the seat

**STRUCK-AT-2026-08-15 (council Disposition 4).** Recorded here so the row's arithmetic is
auditable: the seat's original 2 nits are now 1 raised to should-fix (L2-3) and 1 struck (L2-4).
Nothing for the seat to adjudicate unless it wishes to revisit a struck finding.

### (d) Skeptical probes

1. Confirm the strike is real: `grep -n "WO-L2-4" docs/process_traces/2026-08-15-readiness-council/council-verdict.md`.
2. Confirm no zombie implementation exists: `grep -rn "calibration_pre_reserve_authorized" scripts/reserve_calibration_window_bracket.py`
   — the marker should still print only on the fresh-authorization path.
3. Sanity-check the strike's premise against the current runbook: does §5C still forbid
   re-reserving on restart? If the T-0/launch-binding work changed the restart path, the phantom
   ruling's basis may have moved.

---

## ROW-LEVEL OPEN ITEMS

- **L2-2 (missing-parent typed refusal): NO REPAIR, NO WORK ORDER.** Confirmed by two independent
  runs (refuter V6 at `8937dec`, re-audit V7 at `fac87d1`); code unchanged at
  `calibration_ledger.py:2885` / `recover_calibration_ledger.py:484`. The re-audit "folded" it into
  a "council L2-2 should-fix batch" that does not exist as a tracked row in TASK_QUEUE or the kernel.
- **L2-3 (needs_pin_commit contradiction): NO REPAIR, NO WORK ORDER.** Runbook :453 byte-identical
  to baseline; code :4949 unchanged. This is a *raised* should-fix (launch-relevant: aborts every
  correct pre-slot session on a mechanical reading) sitting untouched.
- **EDQ-L2-2 (§5C non-delegable lead live verification): NO EVIDENCE, NO TRACKING ROW ANYWHERE.**
  `grep -rn "EDQ-L2-2"` returns hits only inside the 2026-08-15 council trace. Its nearest
  instrument (`rehearsal-operator-card.md`) is recorded OPEN and targets the superseded `_v2`
  pack family.
- **EDQ-L2-1 (crash matrix to completion at the audit-baseline head): evidence not locatable.**
  The 15/15 claim survives only as a RUN_STATE line at `62c6a06` (absent from the current
  RUN_STATE); the project's own T10 report anomaly A-3 states the required unpiped log file
  cannot be found and that the companion load run's "errors=3 of 13" does not reconcile. The row
  also specifies the *audit-baseline* head, which `62c6a06` is not, on a module that has since
  grown from 13 to 15 methods.
- **WO-CRASHMATRIX-RELIABILITY: still open and structurally invisible.** Registered only as
  hand-authored prose at `TASK_QUEUE.md:336-360`, outside the generated region and absent from
  `state_kernel.json`. Closure condition (module under 15 min hosted, no internal per-case
  timeout) unmet on the record.
- **Work-selection surfaces contradict the merged code for WO-DETECT-PULSES-BUDGET.** The cure is
  on `origin/main` (PR #159 / `04e34ee`) at the D-143 value 165,000, but the kernel row reads
  `"status": "partial"` / "MERGE-STAGED", the generated A5 row renders "PARTIAL; READY [AGENT]"
  (`TASK_QUEUE.md:539`, `:633`), and the hand-authored note (`TASK_QUEUE.md:317-334`) still states
  the superseded 100,000-cell budget and a branch-era 14-test/98.964 s result. Commit `54f990d`
  additionally mislabels the ruling as D-138 when it is D-143.
- **The coverage denominator is already stale.** The re-audit's 251 was measured when the crash
  matrix had 13 methods; it now has 15. No re-enumeration exists at the head this sitting judges.
- **Phase 3's "adversarial coverage re-enumeration of all universes" is undone for 10 of 11 seats.**
  Only L2's universe has been re-enumerated; council-verdict.md:18-22 makes the self-nomination
  problem general, not L2-specific.
- **The charter file carries neither of the two rules this row turns on.** No "mandatory re-audit"
  clause and no ENUMERATING/READY-CANDIDATE sitting distinction exist in
  `docs/process/instrument-readiness-audit-charter.md` (last touched `6a7849c`, 2026-08-13); both
  live only in council-verdict.md. The independence conditions for a re-audit are therefore
  unwritten, which is why question (i) under L2-COV-1 has no mechanical answer.
