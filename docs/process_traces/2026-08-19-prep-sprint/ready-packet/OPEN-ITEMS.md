# OPEN ITEMS — what no repair addressed, and what could not be located

Honesty over completeness-theater. This list exists so no seat has to discover an absence by
accident. "EVIDENCE NOT LOCATED" means the assembler searched the named places and found nothing —
it is a reported fact about the repository at **4597ad4**, not a confession of a weak search. A
seat that locates the missing artifact should say so and strike the item.

Assembled read-only at `impl/r2-s0-mint-resolver` HEAD **4597ad4**; council audit baseline
**8937dec**; 214 commits between them.

---

## A. PROGRAM-LEVEL OPEN ITEMS (source: `rows/ROW-P-PROGRAM.md`)

### A-1. Ten of eleven evidence universes have never been independently re-enumerated
The verdict made independent re-enumeration of **every** universe plus a standing adversarial
coverage attack a condition of the READY-candidate re-audit (`council-verdict.md:18-22`). Only L2's
universe was re-enumerated (`docs/process_traces/2026-08-15-l2-reaudit/`, `0f886d3`). **No artifact
located** for the other ten, or for any coverage attack against this sitting. Coverage error was
conservative under NOT-READY; under READY it is fail-open.

**And the one re-enumeration that exists is already arithmetically stale.** The L2 assembler
verified three ways that the re-audit ran at `fac87d1` — **187 commits behind `4597ad4`** — and
reproduced its method: counting `def test_` across the exact eight modules it enumerated gives
**251 at `fac87d1`** (matching exactly) and **289 at the current head** (+38, +15.1%;
`test_powermetrics_fiducial` 46→75, `test_calibration_bracketing` 42→48, crash matrix 13→15). The
denominator that felled L2's READY has moved again, and nothing re-runs it. See `rows/ROW-L2.md`.

### A-2. The audit-baseline manifest has not been superseded — it pins a dead head and a two-generation-stale pack family
`docs/process/audit-baseline-manifest.json` has exactly one commit in its history (`694442c`). It
still pins `head_commit`/`origin_main` = `ac3fe1d…` and the three **_v1** pack digests, while the
live family is **_v3** under freeze-0003. **None** of the three ruled supersession fields
(`pack_digest_algorithm`, the chain-template coverage note, paths for all bindings) is present.
Charter amendment 12's final-head invalidation is therefore live against every 2026-08-15 lens
result.

### A-2b. The frozen `_v1` packs' committed bytes CHANGED after the freeze — the manifest's digest binding is broken (assembler-verified)
The L1 assembler found the three `_v1` `pack_digests` no longer reproduce at the current head. The
packet assembler verified the cause directly:

```
git diff --stat ac3fe1d..HEAD -- configs/campaigns/d117_floor_qwen25_1p5b_v1/
  .../d117_floor_qwen25_1p5b_v1/generate_configs.py | 648 +++++++++++++++---
  1 file changed, 576 insertions(+), 72 deletions(-)

git diff --stat ac3fe1d..HEAD -- .../d117_floor_qwen25_1p5b_v1/plan_tree.json
  (empty — plan_tree.json is unchanged)
```

All three `_v1` packs show the same single-file change, from commits `0cb9bf2`, `5292cf7`,
`07c12f3`, `3e780a1`, `54f990d`. **The nuance matters and the seat must rule on it:** `plan_tree.json`
— the receipt's `pack_identity` transitive closure under D-140/M-2 — is byte-unchanged, so the
D-134 freeze receipts may still authenticate. But `generate_configs.py` **is inside the committed
pack tree** that `joulewise.arm_readiness.committed_pack_tree_sha256` hashes, which is the digest the
audit-baseline manifest pins. So the audit baseline's integrity binding is broken even though the
freeze receipts' binding may be intact. Verdict Disposition 1 established byte-identical recompute
**at 8937dec**; that is no longer the state.

### A-3. The Phase-3 focused re-audit of L1, L5, L7 was never performed
Ordered at `council-verdict.md:102-104`. **EVIDENCE NOT LOCATED** — searched all 37
`docs/process_traces/` directories, the T9/T10/T12-T13 run reports, `TASK_QUEUE.md`, and
`docs/council_log.md`. The project's own queue rows (Q2–Q4) state the Phase-3 re-audit as a
precondition to this sitting.

### A-4. The charter file was never amended
The ENUMERATING vs READY-CANDIDATE sitting distinction (Opus S12) and the manifest-supersession
conditions (Opus S11) live only in `council-verdict.md`, `docs/council_log.md`, and the kernel/queue
clearance strings. `docs/process/instrument-readiness-audit-charter.md` is unchanged since
`6a7849c` and contains neither "READY-CANDIDATE" nor "ENUMERATING". The clearance line in
`state_kernel.json:9` cites the charter for language the charter does not contain.

### A-5. All three same-signature consequences are unhomed
(a) **No drafting-mechanic checklist document exists** — `grep -rln "drafting-mechanic"` over
`docs/` and `.claude/` hits only `docs/council_log.md` and the 2026-08-15 council directory; the
mechanical rule-11 trigger enumeration over the decision log therefore has no home, and the council
called it "the one consequence that would have caught this cycle's failure prospectively"
(`docs/council_log.md:3748`). (b) No output-keyed refuter-liveness protocol located. (c) No
standing record of the stop-signal timing rule outside the verdict. **A seat should ask whether
this packet itself was finalized without the trigger enumeration the council ordered.**

### A-6. The 23-finding consistency sweep remains formally UNVERIFIED as a body
Only sweep-B4 was adjudicated (REFUTED). Individual fixes landed (`76f6861`, `47d2645`, queue
closures) but **no per-finding verification ledger was located**. Under charter:66-68 an unverified
item is UNVERIFIED, and amendment 11 makes UNVERIFIED independently disqualifying. B7 — the paper's
floor-regime contradiction — is claim-bearing and P1.

### A-7. Four Phase-1 work orders are not closed on the state kernel, the declared sole work-selection authority
At `docs/process/state_kernel.json` (`updated: 2026-08-19`): **WO-CENSUS-SEMANTICS = blocked**
(hard dependency `ED-Q-L9-3`, `state: pending`); **WO-CONSUMPTION-EDGE = partial** (remaining: "the
production freeze (rides Phase 2) + the same-head production-pack L10 replay");
**WO-DETECT-PULSES-BUDGET = partial**; **WO-LAUNCH-BINDING = queued** (remaining: "stage 4
successor flag inside the transaction", note ends "**Launch stays NO-GO**").

### A-8. The kernel's own merge-state narrative is stale
The staged payload at `e22e658` **is** an ancestor of HEAD and is contained in `main`, yet the
kernel still describes it as "MERGE-STAGED for the atomic re-freeze". A stale record in the
declared sole work-selection authority is itself a finding.

### A-9. Phase-2's "ONCE, atomically, LAST among pack-byte changes" is not evidently satisfied
The freeze history since the council shows a `_v2` family frozen, **reverted, re-minted, reverted
again, and re-minted a third time**, followed by a whole `_v3` family and freeze-0003. Opus W2's
warning was that any earlier pack-byte change forces an extra baseline supersession and re-audit
round. Whether the current state satisfies the ordering is unadjudicated.

### A-10. No end-to-end T-0 pass at the exact reviewed head, and no successor arm packet
Opus W8 conditioned the successor arm packet on the T-0 repair passing end-to-end at the exact
reviewed head. **No such pass receipt and no successor arm packet located.**

### A-11. M-2 residues
Composed-verdict item 2d left an explicit **RULING-REQUIRED** row (the contrast pack's
PROPOSED-PENDING-LEAD-RATIFICATION / TODO(lead) / "EMPTY pending U11" markers, "likely
Ed-adjacent"). No ruling located. Also unconfirmed: whether freeze-0003 retired M-2 per its
per-pack retirement mechanism.

### A-12. This sitting's own form preconditions are unmet
No sealed packet custody under `docs/process_traces/<date>-readiness-council/` for the new sitting;
the mechanical extraction script is not yet committed beside the packet (required by the M-2 gate's
non-author-assembly protocol, since the reviewed party is the magistrate); **no fresh rule-11 cold
pairing convened**; `scripts/validate_gate_packet.py` remains unbuilt, so the cold judge's trust
anchor is manual.

### A-13. Queue rows name two pack generations in the same row
`TASK_QUEUE.md` Q2/Q3/Q4 name `_v1` pack ids in the task text and `_v3` ids in the acceptance
evidence. The arm path binds on exact pack identity; both cannot be right.

### A-14. D-149 removed the human margin the 2026-08-15 seats assumed
Under D-149 a standing READY-candidate verdict is **condition (1) of an automatic, unattended T-0
GO**; the other four conditions are machine-evaluated, and the per-window "separate perishable T-0
GO from Ed" fence is **explicitly superseded for no-hands windows**. The charter's separation
survives in letter; the human at the arm does not. No seat has audited the automation itself.

### A-14b. ED-QUALIFICATION ROLL-UP: 20 of 23 rows are not in a state the clearance rule accepts
The consolidated ED file (`30-ED-QUALIFICATION-rows.md`, produced by the sibling assembly — see the
note at the head of `00-INDEX.md`) walks all 23 rows against primary evidence and tallies:

> **Tally: 3 CLOSED (candidate) · 12 PARTIAL · 8 OPEN · 0 SUPERSEDED.**
> Under charter amendment 11 ("all ED-QUALIFICATION rows closed with evidence"), 20 of 23 rows are
> not in a state the clearance rule accepts on this record. Two of the three CLOSED rows rest wholly
> or partly on an off-repo custody root; the third (ED-QUAL-L1-2) is branch-only.

The eight OPEN rows: ED-QUAL-L6-1, EDQ-L2-2, ED-L3-2, ED-L7-1, ED-L7-2, ED-L10-1, ED-Q-L8-2,
ED-Q-L8-4. Independently confirmed by this assembler for the most consequential one:
`~/JouleWise-window-custody/ed-qual-20260817/` contains sudoers vectors, clock states, backlight,
rail-probe note, quiet-census and the decisive-replay log — and **no `rehearsal` directory**.
**ED-Q-L8-2, the full E-4→E-9 dress rehearsal the verdict called "the program's most valuable Ed
hour", has not been performed.**

Recurring qualifiers across the PARTIAL rows, each of which a seat must weigh separately:
- **executed but not quiet** — ED-Q-L8-3 and the rail probe (ED-L3-3 / ED-Q-L9-2) ran during a
  3h40m decisive replay, on a machine that was by definition not quiet;
- **executed but not committed** — ED-Q-L9-3's quiet-census exists off-repo and was captured *by
  the lead agent*, and the regression fixture its own kernel acceptance requires was never
  committed (`WO-CENSUS-SEMANTICS` still `blocked`);
- **executed at the wrong head** — EDQ-L2-1 (crash matrix, 15 tests not 16, no head pin),
  ED-QUAL-L4-1 (decisive replay at a 2026-08-17 pre-r5/r6 head);
- **closure evidence lives off-repo and unhashed** — most rows; nothing in any committed manifest
  binds `~/JouleWise-window-custody/…`.

### A-15. Findings retired by risk acceptance rather than repair
D-139 A1 + D-148.6 accept the in-process-adversary family (recorder check-to-grant race, T-0
capture provenance, hostile same-UID injection, forged launch-context) as registered limitations;
WO-RECORDER-GRANT-IDENTITY was **retired without implementation**. This is legitimate risk-appetite
authority, not evidence that the instrument fails closed. The sitting should state explicitly
whether acceptance discharges these rows or merely relabels them.

---

## B. PER-SEAT OPEN ITEMS

Harvested verbatim from each row file's §6. See the row file for context and citations.

### Seat L1 — harvested verbatim from `rows/ROW-L1.md` §6

- **The audit-baseline manifest has not been superseded, and its three `_v1` pack digests no
  longer reproduce at `b92b43d`** (cause: a committed `generate_configs.py` change inside each
  frozen `_v1` pack between `ac3fe1d` and HEAD). The ruled supersession fields
  (`pack_digest_algorithm`; per-binding paths; chain-template coverage note) are absent.
- **Phase 3's focused re-audit of L1 does not exist.** No artifact under `docs/process_traces/`
  matches; the only post-verdict re-audit is `2026-08-15-l2-reaudit` (Phase-1 WO-L2-REAUDIT).
- **The B1 repair reproduces B1's mechanism:** `_v3` freeze evidence is the legacy
  `joulewise.arm_readiness_evidence_receipt.v1` schema with the unchanged 24 h
  `_EVIDENCE_VALIDITY_NS`, ≈14.9 h of headroom measured at probe time, death stated at
  ~2026-08-20T16:51Z or on any reboot.
- **The R1-ruled content-bound lifecycle is not in force for the frozen family:** no successor row
  registry is installed (`configs/arm_readiness/` holds only `d117_row_registry_v1.json`), the
  five Ed-reserved registry values are still at council (D-148.5), and the checked-in placeholder
  refuses issuance/consumption by design.
- **`WO-L1-1` … `WO-L1-5` were never enrolled as tracked rows** in TASK_QUEUE or the kernel; there
  is no per-work-order closure record for this seat.
- **WO-L1-4 (D-118 gate-ledger lint) is unexecuted and unscheduled** — neither built nor was D-118
  amended; L1-S1 was omitted from the verdict's Phase-1 should-fix batch.
- **WO-L1-5 (FREEZE-FCM01 dated supersession banner) is unexecuted** — the prohibition banner is
  byte-unchanged.
- **B3's demotion limb is unexecuted and the class regressed:** three post-verdict hand-written WO
  sections outside the generated region carry no kernel row
  (`WO-SAMPLER-SUPERVISOR`, `WO-CRASHMATRIX-RELIABILITY`, `WO-DETERMINISM-LOAD-ISOLATION`), and the
  three original sections were never demoted to pointers nor enrolled as kernel rows.
- **No automated staleness detector for `kernel.updated`** was built (L1's own unexecuted
  obligation); freshness is hand-maintained.
- **`gen_state.py:372` D-041 substring lint unchanged**; its sibling limb at `:371` still requires
  a `P2-006` task dependency after P2-006's retirement.
- **`draft_status: "unfrozen_draft"` is permanent in the `_v1` bytes** (`plan_tree.json:793`); the
  M-2 override therefore remains the operative instrument for `_v1` for its lifetime
  (`cold-fable-ruling.md:55` ruled the M-2 remedy "incomplete as recorded").
- **ED-QUAL-L1-1 has no located closure evidence** for the `verify`-subcommand production replay,
  and may be in tension with R1 cl.5's no-grandfathering prohibition — needs a ruling, not a
  silent close.
- **ED-QUAL-L1-2's Ed-side exact-byte confirmation is still owed**
  (`docs/process/ed-s5-mint-decision-2026-08-19.md:94-95`; `RUN_STATE.md:82-84`).
- **No independent audit of the S4/S5 mint execution was located**; the D-144 pre-merge seat pass
  over the implemented S0–S5 artifact is a ruled requirement that has not run, and both merge-gate
  inputs are recorded UNSATISFIED (`RUN_STATE.md:133-135, 146-149`).
- **Nothing in this repair program has merged to main** — `impl/r2-s0-mint-resolver` @ `b92b43d`;
  `RUN_STATE.md:138`: "NO MERGE HAS OCCURRED."
- **Provenance discrepancy:** the assembler brief states HEAD `4597ad4`; the tree is `b92b43d`.

---

## 7. ADDENDUM — the read-only tree MOVED during assembly (recorded, not graded)

All verifications in §§1–6 were executed at **`b92b43d`**. At the close of assembly
(`git -C wtS0 log --oneline -1`) the shared worktree had advanced to **`48f337b`**, three commits
later — a concurrent writer landed while this row was being assembled:

| Commit | Subject (verbatim) |
|---|---|
| `7305e0d` | Prep sprint: paper staging landed — registry audit (0/34 clean locators; 8-slot coverage hole; era-codes renderer gap F1), refreshed-registry DRAFT (anchors only), 5 STOP_FILL figure skeletons + drift-proof generator |
| `45e0229` | Fresh-pass gate CLEAN through b92b43d (report custodied); fix its B1/B2 + S1-S10 bookkeeping findings (kernel status_note, gate-record pinning, stale hazards/banners, gate-count unification, D-149 ONE-home, GO-evaluator queue row) |
| `48f337b` | README: restore the RUN_STATE freshness-owner pointer the banner rewrite dropped (cures the docs-freshness red pushed in 45e0229) |

**What this changes for L1 (verified by `git diff b92b43d..HEAD`):**
- **Unchanged:** `docs/process/audit-baseline-manifest.json` (still the single `694442c` version),
  `FREEZE-FCM01.md`, every `configs/campaigns/**` pack byte, `scripts/gen_state.py`,
  `.github/**`. Every §2 finding-level conclusion therefore still holds at `48f337b`.
- **Changed:** `docs/process/state_kernel.json` (7 lines). The `WINDOW-COUNCIL-GATE` record itself
  is **byte-unchanged**; what moved is the three window rows: `goal` now names the `_v3` packs
  (was `_v1`), and each `status_note` was shortened to "Successor family frozen (freeze-0003,
  2026-08-19); awaits READY-candidate council + D-149 GO conditions" — **dropping the previous
  explicit mention of the Phase-2 successor re-freeze and the Phase-3 re-audit fences.** A
  skeptical seat may wish to probe whether that shortening removes a truthful fence from the
  authority plane (L1's own subject matter) at exactly the sitting that would clear the gate.
- **Also changed:** `RUN_STATE.md`, `TASK_QUEUE.md`, `WINDOW_STATUS.md`, `README.md`,
  `docs/decision_log.md` (1 line), `tests/test_gen_state.py` (1 line), and a new custody file
  **`docs/process_traces/2026-08-19-prep-sprint/merge-freshpass.md`** (350 lines).
- **Directly affects ROW-L1 §5 probe 6:** the fresh-pass merge-gate input that `RUN_STATE.md:133-135`
  recorded as UNSATISFIED is now claimed **CLEAN through `b92b43d`** with a custodied report at
  `docs/process_traces/2026-08-19-prep-sprint/merge-freshpass.md`. The seat should read that report
  directly and check (i) whether it covers the L1-bearing commits, (ii) whether it is
  self-reported by the same session that authored the work, and (iii) that it does **not** cover
  `45e0229`/`48f337b`, which landed after its own coverage cutoff.

---

### Seat L2 — harvested verbatim from `rows/ROW-L2.md` §6

- **The packet does not agree with itself about the current head.** Task brief says
  `4597ad4`; `_ASSEMBLER-BRIEF.md:12` says `d10881b`; the actual `wtS0` tip is `b92b43d`
  (parent `4597ad4`). Under amendment 12 the seat cannot adjudicate without a ruled head.
- **The branch gained two commits (`b92b43d`, `7305e0d`) while this packet was being
  assembled.** The head is live. An amendment-12 sitting requires a frozen, named head.
- **The mandatory coverage re-audit ran at `fac87d1`, 187–188 commits behind the current
  head.** Amendment 12's final-head invalidation is engaged and nothing in the packet
  addresses it.
- **The 251 denominator no longer holds.** The same eight modules carry 289 test methods at
  the current head (+38). No re-enumeration at the current head exists.
- **The re-audit's enumeration procedure has not been re-applied** to modules added in
  `fac87d1..HEAD`; a new L2-surface module would enlarge the universe beyond even 289.
- **L2-2: no repair located.** `calibration_ledger.py:2885` and
  `recover_calibration_ledger.py:484` are unchanged; no WO-L2-2 queue row exists; the
  re-audit re-found it as L2R-2 and folded it back into the same unimplemented batch.
  Searched: those two files, `TASK_QUEUE.md`, the Completed Queue table.
- **L2-3: no repair located.** The runbook bullet is byte-identical to baseline `8937dec`.
  It was RAISED to should_fix by the refuter, so it is not disposable as a nit. Searched:
  all `needs_pin_commit` hits in the runbook, `TASK_QUEUE.md`.
- **EDQ-L2-1 is closed against the wrong head and a differently-sized module** (15 methods
  vs 13 at baseline), with no head pin in the log.
- **The canonical-suite log from the same quiet slot as the crash-matrix log has never been
  located** — anomaly A-3 named two missing logs and only one was re-custodied.
- **EDQ-L2-2 has no closure evidence at all**; the dress rehearsal that would produce it is
  recorded **OPEN**, gated on the frozen `_v2` alpha pack.
- **L2-EDQ-1 remains "qualification open"** by the council's own addendum wording, and
  **WO-CRASHMATRIX-RELIABILITY has no completion entry** in the Completed Queue table.
- **TASK_QUEUE A5 (`WO-DETECT-PULSES-BUDGET`) is still `PARTIAL; READY [AGENT]`** even though
  its cure is on `origin/main`; the hand-authored evidence note explicitly declines to retire
  it, and that note still describes the superseded **100,000**-cell budget rather than
  D-143's 165,000.
- **The detection budget value has already been falsified once by live data** (100k → 165k,
  D-143). The seat should decide whether a single n=34 sweep is an adequate basis for the
  replacement.
- **Runtime probes were NOT executed by this assembler** (read-only mandate): P2, P4, and P7
  are static-analysis claims awaiting execution. The 289 figure is a `def test_` count that
  reproduces the loader total exactly at `fac87d1` — but it is not itself a
  `countTestCases()` run at the current head.

---

### Seat L3 — harvested verbatim from `rows/ROW-L3.md` §6

- **F1 (should_fix) — no repair, and not even queued.** `joulewise/adapters/powermetrics.py:1664-1671`
  is byte-unchanged; the adapter contains no census of any kind; `WO-L3-1` exists only in the
  council packet. Searched `TASK_QUEUE.md`, `RUN_STATE.md`, `docs/process/state_kernel.json`, and
  tree-wide for `WO-L3-1`.
- **WO-SAMPLER-SUPERVISOR remains unimplemented and unregistered in the kernel** —
  `TASK_QUEUE.md:293-316`, "Not on any critical path" — so detect-and-report is the architectural
  ceiling for any F1 remedy, on a path that today has no detection at all.
- **F2 (should_fix) — no repair, and the failure scenario ACTUALLY OCCURRED.**
  `docs/phase_2/ed-qualification-session.md` has zero commits since 2026-08-15, the sampler-module
  docstring still carries no checklist items, and the batched Ed session nonetheless ran and closed
  the sampler row on 2026-08-17.
- **F3 (should_fix) — WO-L3-3 not done**, and the live 100 ms data that now exists shows
  **realized ≈113 ms at configured 100 ms (~13 % long)** across all ten 2026-08-18 bundles. No
  seat, ruling, or document has assessed what a 13 % cadence overshoot does to the rollover gate,
  the drain budgets, or window sample-count planning. **This is a NEW open item, not a repair.**
- **F4 and F5 nits — no repair.** `docs/paper/related_work_draft.md:19` and
  `joulewise/adapters/powermetrics.py:1183-1187` are verbatim unchanged.
- **ED-L3-1 was closed against the very checklist the row forbids closing against.** The row says
  "Close only after WO-L3-2/WO-L3-3"; neither is done. The seat must decide whether a good live run
  against a defective checklist closes a gating row.
- **ED-L3-2 has NO LABELLED CLOSURE.** The string `ED-L3-2` appears nowhere outside the 2026-08-15
  council packet; the ten live SIGTERM relays that would satisfy it were an **agent-run** by-product
  of the shakedown, on the fiducial path, and **their post-teardown orphan censuses were never
  durably recorded** — `~/JouleWise-window-custody/shakedown-20260818/fences/` has no
  `census-orphan-post.txt` and no `census-monitor-post.txt`, and no
  `powermetrics_post_teardown_census` event exists in any live `events.jsonl`. The SIGKILL branch —
  the row's actual hazard — has still only ever been observed in an **unprivileged simulation**
  (falsifier F-B).
- **ED-L3-3's differential is uninformative and was taken on a contaminated machine** — a
  concurrent decisive-replay unit test plus a mid-sequence charge-to-full, both recorded in
  `rail-probe-load-note.txt`, which is itself lead-dictated after the operator's own note was
  overwritten.
- **ED-L3-4 has never been asserted closed anywhere**, and its REOPEN-on-OS-update trigger is live
  and unchecked since 2026-08-18. The row's silent-failure mode (a unit change that keeps mW fields
  parseable) is not excluded by any attached evidence.
- **ALL ED-row closure evidence for this seat is OUT-OF-REPO and UNCOMMITTED**
  (`/Users/edr/JouleWise-window-custody/ed-qual-20260817/` and `.../shakedown-20260818/`), bound to
  no manifest and hashed by nothing. A future re-audit cannot re-derive this seat's closure from the
  repository.
- **`WO-L3-1..4` were never registered as work items anywhere outside the council packet** — unlike
  the L9 work orders, which at least reached the kernel as WO-CENSUS-SEMANTICS. Nothing in the
  queue would ever surface them for selection.
- **D-149's no-hands window automation is unaudited by any seat and is branch-only**
  (`0e96dbb`, `79a4cd0`, `b92b43d`, none on `origin/main`). It removes the human presence that the
  F1 orphan scenario tacitly relies on, on a path that has no software census.
- **The queue's WO-DETECT-PULSES-BUDGET status string (`PARTIAL; READY`) disagrees with the commit
  graph** (`ceda7a6` is on `origin/main` and its governed abort was observed firing live). Not L3's
  finding, but it is a fact about the evidence base this seat is being asked to trust.

---

### Seat L4 — harvested verbatim from `rows/ROW-L4.md` §6

- **The packet does not agree with itself about the current head.** Task brief `4597ad4`;
  `_ASSEMBLER-BRIEF.md:12` `d10881b`; actual `wtS0` tip `b92b43d`. Under amendment 12 the
  seat cannot adjudicate without a ruled head.
- **The branch gained two commits (`b92b43d`, `7305e0d`) while this packet was being
  assembled.** The head is live. An amendment-12 sitting requires a frozen, named head.
- **L4's amendment-12 exemption no longer holds.** The seat's own report claimed exemption
  because "no file in L4 scope changed after the manifest"; 214 commits later, most of L4's
  scope has changed — including `reduce.py`, `uncertainty_evidence.py`, `whole_window.py`,
  `analysis_engine/claims.py`, `floor_extraction.py`, and every frozen spec and pack.
- **Only ONE of the four L4 work orders was ever registered as a queue row.**
  `grep -n "WO-L4-" TASK_QUEUE.md` returns nothing; the only trace is
  WO-MARGIN-RECORDER-AUTHZ at line 105. **WO-L4-2, WO-L4-3, and WO-L4-4 have no queue
  existence at all** — they cannot be tracked to closure by the queue.
- **L4-2: no repair located.** Zero production references to `d117c15v7`;
  `analysis_manifest_v3.py` splitwise pin and `swdec-contrast` grammar unchanged. Searched:
  `joulewise/`, `scripts/`, `TASK_QUEUE.md`, the Completed Queue table.
- **L4-3: no repair located.** No `plan_tree.sha256` close-out comparison anywhere in
  `window_runbook.md`; the D-133 item (1) row still says "record its path and SHA-256 at
  close-out" only. Searched: the whole runbook, `three_night_freeze_manifest.md`,
  `TASK_QUEUE.md`.
- **L4-4: no repair located** (record-only). Searched: `TASK_QUEUE.md`, Completed Queue.
- **The D-133 item (1) freeze-manifest checklist row that WO-L4-1 ordered re-executed against
  frozen bytes is still an unchecked `- [ ]`** at `three_night_freeze_manifest.md:170`.
- **The L4-1 committed regression binds the `_v1`-generation spec and packs**
  (`tests/test_window_duration_margins.py` `_floor_spec_path`, and pack constants
  `d117_floor_qwen25_{1p5b,7b}_v1`) while the live family is `_v3`/r6 — the
  synthetic-fixture/real-vocabulary seam the cure was built to close may have reopened one
  generation downstream. **Not executed by this assembler; probe P1/P2 required.**
- **The D-146 claim barrier is post-council, branch-only, lands in five L4-scope modules,
  and no seat has audited it.** D-148 cl.(7) leans on it to make 748 stored bundles
  "mechanically" non-claim-bearing.
- **The r5→r6 supersession was forced by a fix round editing two of the four D-079-pinned
  estimator sources**, and the packet's named head (`4597ad4`) is already one commit behind
  the actual tip — i.e. the head has advanced past the delta re-audit boundary that
  re-verified the pin state.
- **ED-QUAL-L4-1's primary evidence (`decisive-replay.log`) lives outside the repo and was
  NOT read by this assembler.** The PASS is attested only by the T10 run-report table row.
  The run was at a later head, took three attempts, and two of its aborts were cured by
  patching the decisive test (`724ea28`) and the replay script (`1500265`) mid-session.
- **The two skipped decisive tests the row was meant to close were not shown running
  un-skipped at the current head.**
- **The check-to-grant registered limitation is absent from `docs/risk_register.md`** (newest
  rows R-019/R-020), and D-139 A1's requirement that "the paper states the assumption once,
  plainly" has no located paper-side artefact.
- **L4's 24/27 coverage denominator was never adversarially tested** and no re-enumeration at
  the current head exists — the standing obligation at `council-verdict.md:20-22` is
  unaddressed for this seat.
- **No runtime probes were executed by this assembler** (read-only mandate). Every "NO-REPAIR-
  FOUND" above is a static-analysis finding from grep/sed over the tree at the `wtS0` tip.

---

### Seat L5 — harvested verbatim from `rows/ROW-L5.md` §6

- **Phase 3's mandated focused re-audit of L5 does not exist** (`council-verdict.md:102-104`
  names L1/L5/L7 minimum); the only post-verdict re-audit artifact in `docs/process_traces/` is
  `2026-08-15-l2-reaudit`.
- **WO-L5-1's CI-truth limb is unmet: EVIDENCE NOT LOCATED.** Searched
  `grep -rn "test_d117_floor_qwen25_1p5b_plan\|test_d117_floor_qwen25_7b_plan" docs/ --include=*.md`;
  `grep -rn "floor.*plan test\|plan-test shard\|CI log" docs/run_reports/2026-08-16-t9-session.md
  docs/council_log.md`; the C-058/C-059 council-log entries. No CI-log determination and no
  recorded process defect.
- **WO-L5-1's runbook pack-pollution cleanup note: EVIDENCE NOT LOCATED.**
- **WO-L5-2 (echo hole / plan_tree binding at freeze) is unexecuted:** freeze-0003 contains zero
  `plan_tree` references; the U11 projection receipts contain zero; no repo trace of the work order
  exists.
- **The `_v3` generators' `CURRENT_FROZEN_RECEIPT_SHA256` still names the `_v2` freeze-0002 sha
  (`1277103b…`) while the `_v3` attachment binds freeze-0003 (`0abfddb1…`)** — the preserve/status
  predicate keys off a predecessor family's receipt; current behaviour unverified by execution.
- **WO-L5-3 is unexecuted as specified:** no registered "advance checkout → re-execute §5C dry-run
  at the final head → then E-steps" sequence located in `RUN_STATE.md` or
  `docs/phase_2/window_runbook.md`; **no freeze-log X-8 staleness annotation located.**
- **No §5C dry-run exists for the `_v3` family at any head**; the only external dry-run receipt is
  `~/JouleWise-window-custody/d117_floor_qwen25_1p5b_v1/arm_readiness.dry_run.receipts/dry-run-0001.json`,
  bound to `49dcc49` and to a retired pack. **No arm or consumption receipt exists anywhere in
  custody.**
- **The advanced measurement checkout `/Users/edr/JouleWise-measurement-20260818` (`94dc3b34`) is
  10 commits behind the branch head**, so the "advance to the final reviewed head" step is still
  owed at arm time; the old checkout `…-20260813` is still at `49dcc49`.
- **F4 recurs on the successor family with executed evidence:**
  `docs/process_traces/2026-08-19-refreeze-execution/s4/check-preauthor-1p5b_v3.log` prints
  "verified d117_floor_qwen25_1p5b_v3 **unfrozen draft**".
- **Post-S4, the `_v3` generator `--check` fails on inventory** ("generation failed: pack inventory
  differs: extras=arm_readiness.evidence/…, arm_readiness.sources/…",
  `s4/check-d117_floor_qwen25_1p5b_v3.log`) — the `--check` catch layer's behaviour on the family
  to be armed is materially different from what L5 audited and has not been re-audited.
- **F5 / M-2 is ruled but not retired:** the dated decision-log entry is deferred "to be minted at
  the merge gate" (freeze-semantics composed verdict, holding 2) and no merge has occurred.
- **Both of L5's uncovered universe classes remain uncovered:** U17 (CI behaviour of the
  pack-integrity plan tests) and U18 (live arm-night chain incl. U11 `verify_frozen_projection`
  with real model bytes).
- **The seat's other unexecuted obligations are unchanged:** `identity_pins.py` internals not
  line-read; the arm-packet document under `~/JouleWise-window-custody/t4-session-20260810/`
  located but not content-audited.
- **ED-QUAL-L5-1 is open:** real `systemsetup` captures exist in
  `~/JouleWise-window-custody/ed-qual-20260817/` (including the `### Error:-99` stderr prefix), but
  **no `arm_readiness.t0.inputs` namespace and no validation against
  `arm_readiness_evidence_t0.py:838-861` were located** (searched the runbook, the T10 report, the
  Ed packets, and `find ~/JouleWise-window-custody -name "*t0*"` → no results). The row is absent
  from the T10 qualification table, and the subsuming dress rehearsal is recorded **OPEN**
  (`docs/run_reports/2026-08-18-t10-session.md:110`).
- **`WO-L5-1` … `WO-L5-3` were never enrolled** as TASK_QUEUE or kernel rows; there is no
  per-work-order closure record for this seat.
- **No independent audit of the S4/S5 execution was located**, and the ruled D-144 pre-merge seat
  pass over the implemented S0–S5 artifact has not run; both merge-gate inputs are recorded
  UNSATISFIED (`RUN_STATE.md:133-135, 146-149`).
- **Nothing has merged to main** (`RUN_STATE.md:138`), so every repair above lives only on
  `impl/r2-s0-mint-resolver`.
- **Provenance discrepancy:** the assembler brief states HEAD `4597ad4`; the tree is `b92b43d`.

---

## 7. ADDENDUM — the read-only tree MOVED during assembly (recorded, not graded)

All verifications in §§1–6 were executed at **`b92b43d`**. At the close of assembly the shared
worktree had advanced to **`48f337b`** (three commits later; a concurrent writer landed during
assembly): `7305e0d` (prep-sprint paper staging), `45e0229` ("Fresh-pass gate CLEAN through
b92b43d (report custodied); fix its B1/B2 + S1-S10 bookkeeping findings…"), `48f337b` (README
freshness-owner pointer restore).

**What this changes for L5 (verified by `git diff b92b43d..HEAD`):**
- **Unchanged:** every `configs/campaigns/**` byte (all three `_v3` packs, their freeze-0003
  receipts, U11 projections, and 33 evidence receipts), `docs/process/audit-baseline-manifest.json`,
  `tests/test_d117_floor_qwen25_{1p5b,7b}_plan.py`, `tests/test_d117_v3_family.py`,
  `docs/phase_2/window_runbook.md`, and all custody roots under `~/JouleWise-window-custody/`.
  Every §2 finding-level conclusion therefore still holds at `48f337b`.
- **Changed and L5-adjacent:** `docs/process/state_kernel.json` — the three window rows' `goal`
  fields now name the `_v3` packs (was `_v1`) and their `status_note` was shortened to "Successor
  family frozen (freeze-0003, 2026-08-19); awaits READY-candidate council + D-149 GO conditions",
  **dropping the prior explicit Phase-2 re-freeze / Phase-3 re-audit fence language**. Also
  changed: `RUN_STATE.md`, `TASK_QUEUE.md`, `WINDOW_STATUS.md`, `README.md`, one line of
  `docs/decision_log.md`, one line of `tests/test_gen_state.py`.
- **New custody file relevant to ROW-L5 §5 probe 3:**
  `docs/process_traces/2026-08-19-prep-sprint/merge-freshpass.md` (350 lines) claims the fresh-pass
  merge-gate input is **CLEAN through `b92b43d`** — the input `RUN_STATE.md:133-135` recorded as
  UNSATISFIED. The seat should read it directly and establish (i) whether it examined the S4/S5
  pack/custody artifacts at all, (ii) whether it is independent of the implementing session, and
  (iii) that its coverage necessarily stops at `b92b43d`, excluding `45e0229` and `48f337b`.
- **Still true after the move:** no `_v3` custody root, no dry-run at any head containing the t0
  author, no arm or consumption receipt anywhere, and no Phase-3 focused re-audit of L5.

---

### Seat L6 — harvested verbatim from `rows/ROW-L6.md` §6

- **F3 / S2 — stage-1 `floor_mint_pin_requirements.v2`: NO REPAIR OF ANY KIND.** No committed
  instance, no subsumption ruling, no mint-side or close-out existence check. WO-L6-4 unexecuted in
  both of its permitted forms. Searched: `git ls-files | grep -i pin_requirement`,
  `git grep -n pin_requirements`, TASK_QUEUE completed + current queue, the should-fix batch commits.
- **F4 / S3 — hashed postcollection backup receipts: NO REPAIR.** `scripts/backup_runs.sh` has zero
  commits in the 215-commit span and contains no `sha256`. §12's two-root hashed-receipt obligation
  remains unperformable as written; WO-L6-5's primary half unexecuted.
- **F5 / S4 — the FINAL arm packet has not been regenerated**, and
  `docs/process/audit-baseline-manifest.json:3` still cites it. The successor packet is correctly
  sequenced behind an end-to-end T-0 pass that has not occurred; the nearest new document
  (`rehearsal-operator-card.md`) is self-declared non-claim evidence and is already one pack family
  stale (`_v2` vs live `_v3`).
- **F6 / N1 — the duration-margins receipt still has no machine consumer.** PR #151 authorized the
  recorder's read of the governed spec; it gave the receipt no consumer, and §11 ordering is still
  unenforced.
- **F7 / N2 — PRIVILEGE_INSTALLATION still has no producer anywhere in the repo**, and the only
  reason it is harmless is that `capture_t0_step.py:438` hardcodes `clock_route: MANUAL`. D-127
  landed a network-time **toggle** sudoers fragment, not the CLOCK_HELPER route — the finding's
  "any future arm context using the clock-helper route" hazard is untouched.
- **F8 / N3 — the arm-time horizon skip is unchanged in code.** `_freeze_evidence_for_arm`
  (`arm_readiness.py:5360`) still passes no `now_monotonic_ns`; the min-fold and verify/consume are
  still the sole defense. Only the fact pattern improved, and only for ~14.9 h from probe time.
- **The R1 freeze-evidence lifecycle exists in code but is DORMANT on production packs.** The
  committed registry is `joulewise.arm_readiness_row_registry.v1` with no `freeze_evidence_lifecycle`
  block, so `lifecycle_registry` and `expected_head_commit` are `None` at arm. D-148 cl.5 defers the
  R1 registry's reserved values to a council that has not sat.
- **Charter amendment-12 exposure is unresolved.** The re-freezes that cured B2's lapse are exactly
  the pack-byte changes that void the audit baseline, and the **Phase-3 superseding manifest with the
  ruled fields (`pack_digest_algorithm`, chain-template coverage note, paths for all bindings) has
  not been issued** (`council-verdict.md:68-70,102-104`).
- **The entire Phase-2 transaction — `_v3` packs, freeze-0003 ×3, U11 projections, D-146/D-147/D-148/D-149
  — is BRANCH-ONLY on `impl/r2-s0-mint-resolver` and absent from `origin/main` (`0099382`).** Every
  freeze-lane claim in this row depends on unmerged state.
- **The `_v3` evidence `head_commit` `1d3873b` is 28 commits behind HEAD and not on `origin/main`.**
- **`window_runbook.md:813` — the ordered terminal-review step still names the retired measurement
  checkout `/Users/edr/JouleWise-measurement-20260813`**, while the live checkout is
  `/Users/edr/JouleWise-measurement-20260818`. Run verbatim, the ordered step attests the wrong tree.
- **ED-QUAL-L6-1's terminal condition is not met:** the dress rehearsal (live E-steps → author → 15
  receipts → same-boot arm) is recorded **OPEN** at the latest record, and the committed rehearsal
  card targets `_v2`, not the live `_v3` family. No later execution record located.
- **ED-QUAL-L6-2's specific deliverable — a measured wall-clock for the freeze-refresh lane, and the
  WO2 runbook amendment it was to ground — IS NOT LOCATED**, despite the lane having been executed
  twice for real.
- **Neither ED row ID appears anywhere in the repository outside the 2026-08-15 council trace.**
  `git grep -n "ED-QUAL-L6-1\|ED-QUAL-L6-2"` over `docs/` returns zero hits elsewhere — there is no
  mechanical tracker binding these rows to closure evidence.
- **This seat's 34/40 coverage denominator was never adversarially tested**, and at least 29 new
  schema IDs have entered the chain since it was enumerated. Under `council-verdict.md:18-22` the
  denominator must be independently re-enumerated before any READY finding.
- **Five of L6's six unexecuted obligations remain unexecuted by this seat**, including the end-to-end
  CLI freeze/dry-run/arm/consume run and the open question handed to L2 (whether the
  `t0.ledger_reservation` predicate's `expected_plan_sha256` and the reservation's `FROZEN_PLAN` sha
  are the same identity). The R2 FROZEN_PLAN identity ruling (D-147, custody
  `docs/process_traces/2026-08-15-r2-frozen-plan-consult/` and
  `2026-08-19-r1-r2-codesign/14-r2-ruling.md`) may have answered it; **this assembler did not verify
  that it does**, and the seat should not assume it.
- **Packet-metadata discrepancies to correct on the record:** the assembler brief names HEAD
  `4597ad4`/`d10881b` and "214 commits", while the tree is at `b92b43d` with **215** commits from
  `8937dec`.

---

### Seat L7 — harvested verbatim from `rows/ROW-L7.md` §6

- **F1 — the horizon asymmetry is UNCHANGED IN CODE.** `_freeze_evidence_for_arm`
  (`joulewise/arm_readiness.py:5360`) still authenticates PACK evidence by bytes + boot session and
  **still passes no `now_monotonic_ns`**; the min-fold (`:6231-6252`) plus verify (`:6499`) and
  consume (`:7126,7219,7910`) remain the sole defense. **Neither branch of WO-L7-1 was taken** — no
  arm-path enforcement, and no authoritative statement of PACK-namespace `valid_until` as
  freeze-time-only semantics located in runbook §5C or the receipt schema notes.
- **No explicit recorded disposition for the original lapsed 08-13/14 receipts was located** — the
  WO's other half. The `_v1`/`_v2` packs still sit in the tree beside `_v3`; whether their lapsed
  evidence is retired, grandfathered, or merely superseded is not stated in any document this
  assembler found.
- **The R1 freeze-evidence lifecycle exists in code but is DORMANT.** The only committed registry is
  `joulewise.arm_readiness_row_registry.v1` with no `freeze_evidence_lifecycle` block, so
  `lifecycle_registry` and `expected_head_commit` are `None` at arm and the `V1_GRANDFATHERING`
  refusal never fires. D-148 cl.5 defers the registry's reserved values to a council that has not sat.
- **The `_v3` evidence's `head_commit` `1d3873b` is 28 commits behind HEAD `b92b43d` and is not on
  `origin/main`** — invisible to the machine while the lifecycle registry is dormant.
- **The horizon will lapse again.** Live probe: ~53,597 s ≈ 14.9 h of headroom at assembly, on boot
  `da90818c-…`, with `RUN_STATE.md:211` naming the instant (~2026-08-20T16:51Z). The 24 h re-run
  obligation is standing and is not scheduled as a window-day step in runbook §4/§5C.
- **F2 — no executed fresh §5C dry-run PASS at the final reviewed head on the `_v3` family was
  located.** The obligation is now correctly documented (`window_runbook.md:340-364,840-862`); the
  execution is not evidenced.
- **`docs/phase_2/window_runbook.md:813` still names the RETIRED measurement checkout
  `/Users/edr/JouleWise-measurement-20260813`** in the ordered terminal-review step, while the live
  checkout is `/Users/edr/JouleWise-measurement-20260818`. Two operative documents disagree on the
  path; run verbatim, §5C attests the wrong tree.
- **The committed rehearsal choreography (`docs/process/rehearsal-operator-card.md`) targets the
  `_v2` pack family while the live family is `_v3`**, and self-declares "qualification choreography
  evidence, never claim evidence" (`:3`).
- **RUN_STATE's corrected reboot text coexists with two uncorrected copies.** The WO-L7-2 correction
  landed at `RUN_STATE.md:625-627`, but "NO REBOOT of the Mac preserves the frozen evidence" survives
  verbatim at `:694` and a variant at `:709` inside superseded checkpoint sections.
- **F3 — `joulewise reduce` still defaults its re-reduction artifact into the invoker's CWD.**
  `joulewise/cli.py:1885-1915`; neither proposed remedy implemented; four cli.py commits in the span
  touched other things. Newly consequential: `b9c7d0a` put launch-lineage on the reduce path and
  `capture_t0_step.py:290-296` refuses on a dirty checkout, so the pollution path is now arm-blocking.
- **ED-L7-1 — NO CLOSURE EVIDENCE LOCATED**, and the bar rose: `prewindow_check.sh:37` now requires
  600 s of *continuous* clean dwell with reset-on-dirty (`:174-199`). Its own text confines the
  demonstration to an Ed/quiet block, which collides with the standing five-day `/loop` fan-out
  posture (`RUN_STATE.md:60-80`) and with D-149's automation preconditions. **Unresolved: whether
  D-148 cl.4 lead-delegation may close it, or whether `quiet_mac_prep.sh`'s display mutation reserves
  it to Ed's hands.** The census this row depends on carries its own unlanded L9 should-fix
  (`sitting-packet-FINAL.md:155`, WO-CENSUS-SEMANTICS recorded BLOCKED).
- **ED-L7-2 — NO CLOSURE EVIDENCE LOCATED.** The only staged dry-run is `_v2`, into rehearsal scratch,
  inside a rehearsal recorded **OPEN**; and it would already be head-stale by `window_runbook.md:361-362`.
- **ED-L7-3 — closure evidence located but never recorded against the row**, and it carries three
  caveats: taken under D-142's night license as a **nonclaim diagnostic** with a preserved
  counter-reading on the WINDOW-COUNCIL-GATE (`docs/decision_log.md:165`); it predates the D-146
  capture-pipeline-v3 flip and the `_v3` family; and it appears in no ED-row closure table.
- **None of the three ED row IDs appears anywhere in the repository outside the 2026-08-15 council
  trace.** `git grep -n "ED-L7-1\|ED-L7-2\|ED-L7-3"` over `docs/` returns zero hits elsewhere — there
  is no mechanical tracker binding these rows to closure evidence, and the charter's READY-CANDIDATE
  form requires "all ED-QUALIFICATION rows closed" (`RUN_STATE.md:4054`; `council-verdict.md:54-57`).
- **This seat's 21/25 coverage denominator was never adversarially tested**, and at least 29 schema
  IDs — including the entire WO-LAUNCH-BINDING receipt family — entered the chain after it was
  enumerated. Under `council-verdict.md:18-22` it must be independently re-enumerated before any
  READY finding, and **L7 is named in the Phase-3 focused re-audit minimum set** (`:102-104`), which
  has not occurred.
- **Two work orders touching this seat's graph are OPEN with launch explicitly NO-GO:**
  WO-LAUNCH-BINDING (A1 — "remaining: stage 4 successor flag inside the transaction. **Launch stays
  NO-GO**", `TASK_QUEUE.md:536,630`) and WO-CONSUMPTION-EDGE (A2, PARTIAL — "Remaining before close:
  the production freeze (rides Phase 2) + the same-head production-pack L10 replay", `:537,631`).
- **Five of L7's seven unexecuted obligations remain unexecuted**, including two CI-exclusive modules
  whose "last known green" is the **#149** CI — eight PRs and 215 commits stale.
- **The entire Phase-2 transaction this row depends on is BRANCH-ONLY** on
  `impl/r2-s0-mint-resolver`; `origin/main == main == 0099382` contains none of the `_v3` packs,
  freeze-0003 receipts, or D-146/D-147/D-148/D-149.
- **Packet-metadata discrepancies to correct on the record:** the brief names HEAD `4597ad4` /
  `d10881b` and "214 commits"; the tree is at `b92b43d` with **215** commits from `8937dec`.

---

### Seat L8 — harvested verbatim from `rows/ROW-L8.md` §6

- **F5 (blocker) — no successor/recut arm packet exists anywhere.** The FINAL packet at
  `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md` is unmodified;
  no repair artifact of that class was located (`grep -rln "arm-packet" docs/`). Everything WO-L8-5
  bundled into the packet — the paste-ready E-9a/b/c literals, the horizon, the fuse, the re-author
  rule, the E-14 `date(1)` literal, the F12 ABORT row — has no home.
- **F7 (blocker) — WO-LAUNCH-BINDING is still queue row A1, READY [AGENT]**, stage 4 outstanding,
  calibration-slot writer enforcement unimplemented; the runbook itself declares E-10 "not current
  authority to launch" and the queue note says "Launch stays NO-GO."
- **F8 — `--arm-context` still refuses a custody path**; the `$(cat …)` literal exists only in the
  rehearsal card.
- **F9 — NO-REPAIR-FOUND.** The 5-minute arm-receipt fuse (`arm_readiness.py:6101`) is still
  documented nowhere operator-visible, and the licensed re-arm recovery is undocumented.
- **F10 — NO-REPAIR-FOUND.** No governed `reauthor-clean`; the raw `rm -r` now spans three namespaces.
- **F11 — no machine catch** for restore-before-close-out; documentation-only improvement.
- **F12 — no re-probe** of process state at arm/verify/consume; the prohibition is prose only, and
  D-149 may have removed the human who honoured it.
- **F13 — `prewindow_check.sh` agent pattern still omits `claude`/`t3`** (`:148-150`).
- **F14 — NO-REPAIR-FOUND.** No `date(1)` literal for the do-not-return-before time.
- **F15 — ED-session census still substring-based**, and its repair WO (A4 `WO-CENSUS-SEMANTICS`)
  remains marked **BLOCKED — ED-Q-L9-3** (TASK_QUEUE `:538`, `:632`) even though that fixture was
  captured 2026-08-17 — a stale kernel row, or an unstated stricter precondition.
- **ED-Q-L8-2 — OPEN, and the verdict's "most valuable Ed hour" is unspent.** Builder and card
  exist on main (`ad14ac4`); **no execution**, no scratch custody root, no receipts. The card is
  stale (`_v2`/freeze-0002/`…-20260818` vs live `_v3`/freeze-0003), and E-9a→E-10 is structurally
  unreachable without a lead-approved committed scratch-ledger route that does not exist.
- **ED-Q-L8-4 — OPEN.** No live `quiet_mac_prep.sh` run located at any date after 2026-07-17
  (`bash -n` only). It is now E-7a inside the un-executed rehearsal, so it inherits ED-Q-L8-2's blockage.
- **ED-Q-L8-1 read-path caveat.** The row asked for a proven read path or a ratified `sudo -v`
  warm-up; neither was delivered. The defect was dissolved by re-shaping the contract (write-vector
  probe + interactive prior-state read). Adjudicable, not automatic.
- **The L8 error-injection matrix has NOT been re-run** against the rewritten §5C, the E-9b/E-9c/E-10
  sequence, the FD-198 handoff, the capture-era system, or the D-146 claim barrier. Searched
  `docs/run_reports/2026-08-1[6-9]*.md` and `docs/process_traces/2026-08-1[6-9]*/` for
  "error-injection" — no matches. This is the seat's own instrument, and it is stale.
- **D-149's automation has been audited by nobody.** The GO-receipt evaluator is explicitly deferred
  to a future gauntlet (`d149-go-receipt-template.md:63-66`); until then "mechanical evaluation" is a
  markdown checklist filled by the issuing agent. D-149 (`0e96dbb`), the template (`79a4cd0`) and the
  shakedown run card (`b92b43d`) are **all branch-only** (`git merge-base --is-ancestor … main` = NO).
- **Unresolved authority conflict:** runbook `:1051-1056` and TASK_QUEUE `:536` both reserve the
  physical launch to Ed; D-149 authorises no-hands windows. No ruling naming the invoker of
  `launch_window.py` in a no-hands window was located.
- **F1's residual is an ACCEPTED LIMITATION, not a closed defect** (D-148 ruling 6 + the
  TRUSTED-OPERATOR registration). Whether an accepted limitation satisfies a READY-CANDIDATE seat is
  the seat's call, not the assembler's.
- **Family staleness runs through the operator surface**: runbook `window.env` example binds `_v2` /
  `…-20260813`; rehearsal card binds `_v2` / freeze-0002 / `…-20260818`; the live family is `_v3` /
  freeze-0003 and lives **only on the branch**.
- **ED-QUALIFICATION rows are not tracked by ID** anywhere in the repo (`grep -rn "ED-Q-L8"` outside
  the council directory → zero hits), while D-149 C1 conditions auto-GO on "ED-QUAL rows closed".
  There is no mechanical list for that condition to read.
- **Three of the seat's six unexecuted obligations remain unexecuted** (`quiet_mac_prep.sh` live;
  E-9 reservation double-reserve/live-writer against a ledger copy; runbook §10 refusal-row
  completeness for the 2am operator — and §10 has since grown four new `launch_*` rows).

---

### Seat L9 — harvested verbatim from `rows/ROW-L9.md` §6

- **F1 (blocker) — no repair.** `t0.background_quiet` MAINTENANCE_CENSUS is byte-unchanged at
  `joulewise/arm_readiness_evidence_t0.py:981-1006`; arm still refuses on every attempt on a
  genuinely quiet machine.
- **F2 (blocker) — no repair.** `t0.no_stray_keepawake` browser/monitor patterns byte-unchanged at
  `:1389-1390`.
- **WO-CENSUS-SEMANTICS has zero implementation** and is still `BLOCKED — ED-Q-L9-3` in the
  generated queue at the current head (`TASK_QUEUE.md:538`, duplicated `:632`).
- **ED-Q-L9-3 is NOT closed as the row defines it.** A live capture exists
  (`~/JouleWise-window-custody/ed-qual-20260817/quiet-census/`, 2026-08-17T23:51:29-0700) but was
  taken **by the lead agent with agent processes live** (contaminating the keepawake and agent
  censuses) and was **never committed** as the regression fixture the kernel acceptance requires.
  **NO COMMITTED FIXTURE LOCATED** — searched `find . -type d -name "quiet-census*"`,
  `find . -name "*quiet*census*"`, `ls tests/fixtures/`,
  `grep -rln "watchdogd\|mds_stores" tests/ configs/`, and `git log --since=2026-08-15` on
  `tests/test_arm_readiness_evidence_t0.py`.
- **Disposition 5's SINGLE-SOURCE label is not cleanly discharged.** The only re-observation is
  same-machine, same-organisation, and self-partitioned by its own capture note; its counts differ
  from the seat's (7 vs 9 Safari agents; 20 vs "~20" maintenance daemons).
- **WO-L9-3 — no repair.** `scripts/prewindow_check.sh:150` still uses
  `codex exec|codex-run|run_campaign|window-chain`; E-7b can still print OK with agents live.
- **WO-L9-4 — no repair, nothing authored.** No hazard register exists anywhere in the tree; the
  consult-mandated rows (radios, notifications, peripherals, remote sessions, third-party
  LaunchAgents, ambient temperature, charge state, lid state, mid-workload residual) are all still
  absent.
- **F5's paper limitation text does not exist** — `grep -rn "mid-workload|mid-member"` over
  `docs/paper docs/report_src docs/contracts` returns nothing.
- **F6/F7/F8 nits all unrepaired**, verified line by line at 4597ad4.
- **The two hazards L9 flagged as uncontrolled actually fired inside this seat's own qualification
  probe**: ED-Q-L9-2's rail probe ran under `concurrent_load=decisive_replay_unittest` (F5) while
  the battery reached full charge mid-sequence (F7). No seat has assessed what that does to the
  probe's admissibility.
- **All ED-row closure evidence for this seat lives OUTSIDE the repository**
  (`~/JouleWise-window-custody/ed-qual-20260817/`), uncommitted and unhashed by any manifest. F6 is
  the registered version of exactly this gap.
- **The dress rehearsal — the operator ceremony that would exercise the arm sequence end to end —
  is OPEN**, per `docs/process/ed-morning-packet-2026-08-18.md:126` ("OPEN: the dress rehearsal
  (item 4) only.") and `docs/run_reports/2026-08-18-t10-session.md:110`.
- **D-149's no-hands window automation is unaudited by any seat** and is **branch-only**
  (`0e96dbb`, `79a4cd0`, `b92b43d`, none on `origin/main`). It removes the operator presence that
  F5's and F8's "operator discipline" dispositions silently assume.
- **D-149 DELETED the kernel clause "Ed remains the physical launch authority"** from all three
  window tasks while `docs/phase_2/window_runbook.md` still asserts Ed's §5A tap, E-10 physical
  launch, and handback attestation verbatim at HEAD. **The kernel and the runbook now contradict
  each other on who launches**, and no cold gate or seat has reconciled them.
- **D-149's C1 ("ED-QUALIFICATION rows closed") makes its auto-GO depend on the very rows this
  sitting is adjudicating** — a circularity recorded nowhere in D-149's own text.
- **D-149's "evaluated mechanically at T-0" is not implemented.** The receipt template defers the
  evaluator (`d149-go-receipt-template.md:63-66`) and a queue block `## WO-D149-GO-EVALUATOR`
  appeared at `TASK_QUEUE.md:373` *during this assembly*.
- **`WINDOW_STATUS.md` was never reconciled with D-149** — no mention of it, still dated
  2026-08-17.
- **A file in this seat's evidence universe changed after the audit and was re-audited by nobody:**
  `joulewise/environment_admission.py` (universe item 10) via **`b7e5730`** (branch-only), with a
  "missed census site" repair in `d279bd2`.
- **The branch HEAD moved twice during this assembly** (`4597ad4` → `b92b43d` → `7305e0d`),
  shifting `TASK_QUEUE.md` line numbers by +7 and adding a new queue block. A packet assembled
  against a moving tree is itself a finding for the sitting.
- **`docs/phase_2/ed-qualification-session.md` has not been touched since the council**
  (zero commits since 2026-08-15), so ED-Q-L9-1 and ED-Q-L9-2's documented homes (steps 4 and 3)
  are byte-identical to what the seat audited.

---

### Seat L10 — harvested verbatim from `rows/ROW-L10.md` §6

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

---

### Seat L11 — harvested verbatim from `rows/ROW-L11.md` §6

- **SF3's primary remedy was not executed.** No excursion re-derivation artifact was committed
  beside the custody close-out: `~/JouleWise-window-custody/window_a10_20260725/` still holds only
  `CLOSE_OUT.md` (mtime 2026-07-25 06:54), `detection-floor-extraction.json`, `operator_logs/`,
  `quarantine/`; the a9 custody directory holds only `operator_logs/` and `quarantine/`. The
  a9/a10 PASSED context is now **prose-backed re-derivation** in one paper paragraph
  (`docs/paper/draft-v1.md:137`) rather than artifact-backed.
- **Uncaveated PASSED prose survives in two consuming documents** that WO-3's third option would
  have covered: `docs/decision_log.md` D-054 clause 11 ("windows a9, a10; both whole-window
  verdicts PASSED") and `README.md:103` ("That protocol ran five times and passed five times —
  windows C, D, a10, …").
- **N1 unrepaired.** `runs_window_a9_20260724/MANIFEST.sha256:202` still lists `./backup.log`;
  `PRUNED.md` still does not mention it; both files unmodified since 2026-07-28 05:29.
- **N2 unrepaired.** `docs/decision_log.md` D-054 clause 11 still carries "a settled reference pair
  three hours apart agreed to 0.007 J" and "fiducial 24.9 ms (80-87%)"; zero commits since the
  audit baseline touched either string.
- **A new stale assertion has appeared in the paper since the corrections landed:**
  `docs/paper/draft-v1.md:189` states "NOTE: freeze-0003 itself is not yet minted", contradicted by
  the S5 mints (`5e38f1e`, `eb7f6c6`, `94dc3b3`) and the filled confirmation table (`8b2b021`), all
  BRANCH-ONLY on `impl/r2-s0-mint-resolver`. The 2026-08-19 consistency sweep (`76f6861`) that
  recorded the r5→r6 supersession did not catch it.
- **All six of L11's unexecuted obligations remain without located closure evidence**, including
  the `joulewise/whole_window.py` deep audit (the machinery behind the missing SF3 artifact), the
  reducer envelope-v3 code audit, and the 29 outstanding exact trace re-integrations — the last two
  now underwriting ranges the paper publishes as its stated basis.
- **Corpus-era question unresolved by any located document:** the a9/a10 basis is pre-anchor-v3 and
  mechanically barred from claims by D-146/D-148.7, while the paper's floor-regime numbers
  (8.611855 J, 1.869502 J) are still sourced to "the retained token-generation contrast cell" at
  seven sites. No located ruling distinguishes prospective-sizing use from claim use for that cell.
- **Neutrality-replay scope unresolved:** the r6 science-neutrality proof is a 19-member replay
  over the D-079 calibration corpus; the assembler could not establish whether the a10 30-member
  phase corpus — whose envelopes the paper now publishes — was inside it, despite `reduce.py` being
  edited in the same transaction (`3038eeb`).
- **Where the evidence lives is split.** L11's three corrections and the B7 row are **ON-MAIN**
  (`36c9d78`). Every subsequent paper/guide rewrite that carried them (`53e480e`, `3efea49`,
  `2952226`) and the whole r5→r6 / freeze-0003 transaction are **BRANCH-ONLY**.
- **Read-tree discrepancy:** the task named `4597ad4`; the worktree is at its child `b92b43d`.

