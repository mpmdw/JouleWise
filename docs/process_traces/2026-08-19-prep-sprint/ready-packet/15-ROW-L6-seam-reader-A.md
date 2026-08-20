# ROW L6-SEAM-READER-A — Seam Reader A / contract-derived producer→consumer graph (GATING)
Original verdict: NOT-READY (2 blockers / 3 should-fix / 3 nits / coverage 34/40)
**UNVERIFIED on coverage** — the denominator (40 artifact-class nodes) was self-nominated by the
seat; council-verdict.md lines 18-22 rule every seat's universe self-nominated and order
independent re-enumeration + the adversarial coverage attack as a standing packet element.

Assembly base: read-only worktree `…/scratchpad/wtS0`, branch `impl/r2-s0-mint-resolver` @ `79a4cd0`
(three commits past the `d10881b` named in the assembler brief — `f8a8fef`, `d10881b`, `79a4cd0`
are the branch tip; verified `git log --oneline -3`). `main` == `origin/main` == `0099382`;
merge-base with the branch = `311d8016`. Ancestry of every sha below verified with
`git merge-base --is-ancestor <sha> main`.

**Standing branch fact for the seat:** `git diff --stat 311d8016..main` = 4 files, all prose
(`RUN_STATE.md`, `docs/guides/instrument-guide.md`, `docs/paper/draft-v1.md`,
`docs/process_traces/2026-08-18-benchmark-profiler-design.md`). **Zero code has landed on main
since the merge-base.** Every code repair cited below therefore either predates the fork (and is
on main) or is branch-only. Nothing is "on main but not on the branch."

---

## L6-B1 — The T-0 evidence author's own inputs have no producer

### (a) Original finding (VERBATIM)
> ### L6-SEAM-READER-A B1: B1 — The T-0 evidence author's own inputs have no producer: no tool, no runbook step, no packet step
> at: joulewise/arm_readiness_evidence_t0.py:42,132-139,506,556,601; docs/phase_2/window_runbook.md:812-827
> scenario: The funded night reaches §5C's post-E-9 authoring step; author_arm_evidence_t0.py refuses evidence_author_t0_clock_attestation_missing (demonstrated live in probe P3) because nothing has created CUSTODY/PACK_ID/arm_readiness.t0.inputs/ — the author requires clock-attestation.json, arm-context.json, launch-manifest.json and six command captures (clock-prior-state, clock-disable, quiet-mac-prep, prewindow-check, ledger-readiness, ledger-reservation) as canonical JSON with boot-bound monotonic-ns fields no human can hand-produce; no repo tool writes joulewise.arm_readiness_t0_command_capture.v1 (grep: only the author itself references the schema), the runbook never names arm_readiness.t0.inputs, and the FINAL arm packet predates the author entirely. Night ends NO-GO — or worse, the operator hand-crafts nine JSON files at 2 a.m., the exact anti-pattern the readiness machinery exists to prevent.
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: `docs/process_traces/2026-08-15-readiness-council/sitting-packet-FINAL.md:39-42`;
seat report `docs/process_traces/2026-08-15-readiness-council/seat-reports/L6-SEAM-READER-A-report.md`;
refuter verdicts `…/refuter-outputs/refuter-verdicts.md` §"B-contract" (F1+F2 CONFIRMED, "MERGE into
ONE work order: shipped T-0 acquisition/capture tool") and §"B-execution" (F1/F2 CONFIRMED; NEW
DISCOVERY: terminal-review commit-trailer producer gap).

Post-verdict adjudication: **not struck.** Verdict Phase 1 ratifies the integrated WO-T0-PRODUCER
(`council-verdict.md:81-83`). Verdict Disposition 4 strikes only "F4's timing premise", not F1/F2.
The verdict ADDENDUM (`council-verdict.md:121-131`) clears the SINGLE-LENS label on the
terminal-review-trailer gap and folds its remedy into WO-T0-PRODUCER + the Phase-3 supersession.

### (b) What changed since 2026-08-15
- **`a61ac92` — "WO-T0-PRODUCER: T-0 acquisition capture tool + R2 resolver + D-127 clock route +
  dwell/env hardening (#152)"**. WHERE it lives: **merged to main** (`--is-ancestor a61ac92 main` →
  true; also an ancestor of the merge-base, i.e. in shared history). 11 files, +2160/−125; new file
  `scripts/capture_t0_step.py` (1006 lines at that commit).
- **The nine inputs are produced — verified by reading the tool, not by trusting the report.**
  - Six command captures: `scripts/capture_t0_step.py:59-66` `STEP_FILENAMES` = exactly
    `clock-prior-state.json`, `clock-disable.json`, `quiet-mac-prep.json`, `prewindow-check.json`,
    `ledger-readiness.json`, `ledger-reservation.json`; written at `:952-955`
    (`_write_no_clobber(capture_path, …, accept_identical=False)`), schema
    `joulewise.arm_readiness_t0_command_capture.v1` declared at `:38` — so a repo tool now writes
    the schema the finding said only the author referenced.
  - `arm-context.json` and `launch-manifest.json`: `_prepare_derived_inputs`, `:516-533`, written on
    **every** invocation into `context.input_root`.
  - `clock-attestation.json`: `_clock_attestation`, path at `:597`, invoked at `:898-902` on the
    `clock-prior-state` step.
  - Target directory: `INPUT_DIRECTORY = "arm_readiness.t0.inputs"` at `:41`, rooted at
    `custody / pack.name / INPUT_DIRECTORY` (`:500`) — the namespace the finding said nothing created.
  - Sequencing + refusals: `_require_sequence` (`:897`), boot-probe refusals before and after the
    command (`:906-911`, `:917-922`), the **600-second continuous dwell** enforcement for
    `prewindow-check` at `:942-950` (refuse `evidence_author_t0_capture_result_invalid`).
  - The author-side paths the finding cited still expect exactly these three derived files:
    `joulewise/arm_readiness_evidence_t0.py:513` (`clock-attestation.json`), `:563`
    (`arm-context.json`), `:608` (`launch-manifest.json`).
- **Runbook now names the steps.** `docs/phase_2/window_runbook.md:913,922,931,942,952,963` carry the
  six literal `python3 scripts/capture_t0_step.py <step>` invocations (E-4…E-9a); `:869` "Ed executes
  the frozen E-step sequence with no reordering"; `:994-1005` E-9b authoring + the 20-minute volatile
  horizon; `:1010-1027` the reboot/HEAD-change re-author rule and E-9c. WHERE: the runbook edits came
  in with `a61ac92` (+220/−61) — **main**.
- **D-127 privileged clock route landed as bytes:** `scripts/joulewise-network-time.sudoers` (4 lines,
  `systemsetup -setusingnetworktime on|off` for `edr`), added by `a61ac92` — **main**. It is shipped,
  **not installed**; installation + exercise remains the Ed row (verdict `:90-91`).
- **The "F4 honest-contract deltas ride the follow-up t0-producer lane" caveat
  (`TASK_QUEUE.md:106`) — what it means, read at source:** `docs/decision_log.md:9598-9647`, "T-0
  CAPTURE PROVENANCE (F4) — honest-contract fix now + trusted-operator scope call DEFERRED to
  Ed/advisor (magistrate, 2026-08-15)". The finding: the author authenticates capture bytes/keys/
  monotonic values/boot identity/order but **not which process produced them**; the council's
  "boot-bound monotonic-ns fields NO HUMAN CAN HAND-PRODUCE" property is **NOT enforced**, so the
  contract overclaimed. The mandatory fix landed as **`65cc0f3`** — "T-0 F4 honest contract: D-134
  cl.6 overclaim superseded (production-interface/ceremony rule, no operator-fabrication-resistance
  claim), TRUSTED-OPERATOR limitation v1 registered, public execute/monotonic_ns/utc_now injection
  seam removed from capture_t0_step (module-private test hook), runbook + docstrings corrected"
  — **merged to main**. The surviving docstring at `scripts/capture_t0_step.py:1-11` now says
  verbatim: "The production CLI is a trusted-operator ceremony interface, not independent producer
  attestation. … v1 does not defend against deliberate operator fabrication."
  **Still open inside the caveat:** the decision entry (`docs/decision_log.md:9640-9647`) records a
  **RULING-REQUIRED for Ed + advisor (Rivoire), PAPER-SCOPE, non-blocking** — whether the MVP
  integrity claim rests on trusted-operator T-0 evidence (publish the limitation labelled) or needs
  the consult's option (a) signed-capture/App-Attest route. No ruling found in `docs/decision_log.md`.
- **Terminal-review commit-trailer producer (the refuter's NEW DISCOVERY, folded into this WO):**
  no producer found. `grep -rn "JouleWise-Terminal-Review"` outside `docs/process_traces/` returns
  nothing that authors a trailer; the R1 ruling (`docs/decision_log.md:9218-9219`) says
  "TERMINAL_REVIEW binds head_tree_oid unconditionally" but the remedy the addendum names — "a
  lead-owned terminal-review attestation step whose commit the superseding manifest pins" — is
  bound to the **Phase-3 supersession, which has not happened** (see L6-S4 below).

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED (producer half) / STILL-OPEN (attestation + live-exercise halves).**
The seat is adjudicating whether a shipped, main-merged nine-input producer with dwell enforcement
and a *downgraded, honestly-stated* contract discharges a blocker whose scenario premise ("no human
can hand-produce") the project has since ruled unachievable in v1 — and whether the two undischarged
riders (Ed's paper-scope trusted-operator ruling; the terminal-review-trailer producer, still tied to
an unexecuted Phase 3) plus the never-executed live path (ED-QUAL-L6-1) leave the blocker standing.

### (d) Skeptical probes
1. `python3 scripts/capture_t0_step.py --help` and then read `_require_sequence`
   (`scripts/capture_t0_step.py:897`, body ~`:700-760`): does the sequence guard actually force
   E-4→E-9a order, or can a step be captured out of order and still author?
2. Has the tool **ever been run for real**? `find /Users/edr -name "arm_readiness.t0.inputs" -type d`
   — if the directory exists nowhere, B1's PASS side is still unproven (ED-QUAL-L6-1 open) and the
   only evidence is `tests/test_capture_t0_step.py` (575 lines, added by `a61ac92`).
3. The 600 s dwell at `:942-950` refuses when `finished - started < 600e9`. Confirm the clock is
   the module-private monotonic hook after `65cc0f3` removed the public injection seam — i.e. that
   the *public* CLI has no monotonic override. `git show 65cc0f3 -- scripts/capture_t0_step.py`.
4. `sudo -l` / `ls /etc/sudoers.d/` on the measurement Mac: is `scripts/joulewise-network-time.sudoers`
   **installed**? If not, E-5 refuses at T-0 regardless of the tool existing.
5. Nine inputs vs the author's demand set: diff the author's required filenames
   (`joulewise/arm_readiness_evidence_t0.py:513,563,608` + its six capture names) against
   `STEP_FILENAMES` — is there a tenth input the author requires that no step writes?
6. Ask for the Ed/advisor ruling on `docs/decision_log.md:9640-9647`. If it is unanswered, the T-0
   integrity claim is still an open paper-scope commitment, not a closed engineering row.

---

## L6-B2 — Committed freeze evidence past its 24 h monotonic horizon; undocumented full freeze-refresh lane

### (a) Original finding (VERBATIM)
> ### L6-SEAM-READER-A B2: B2 — Committed freeze evidence is already past its 24 h monotonic horizon; every future window requires an undocumented full freeze-refresh lane
> at: joulewise/arm_readiness.py:2943-2975,3712-3719; docs/phase_2/window_runbook.md:726-742,812-830
> scenario: Live reading on the freeze boot session: now-monotonic 1,996,764 s > valid_until 1,986,799 s — all 11 generic PACK evidence receipts frozen 2026-08-13 are expired. generate_arm_receipt folds evidence expirations into the arm receipt's valid_until (min(...)), so any arm receipt issued now is expired at birth; verify/consume then refuse readiness_record_expired (arm_readiness.py:3952-3955). Cure = re-author 11 receipts + new freeze receipt + plan-tree re-pin + commit + review + fresh dry-run, same boot session as ARM and ≤24 h before it — a cycle no operative document names: §4 presents freeze as 'before quiet time' desk work, §5C's re-author rm covers only the two T-0 namespaces, and the reboot-fence paragraph says only 'generate new receipts'. Fails closed at every probe point, so no consumption unsoundness — but a required output (a valid GO arm receipt) currently has no producible path under the frozen packs + current runbook alone, and the refresh commits void the audit baseline per charter amendment 12.
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: `sitting-packet-FINAL.md:44-47`; refuter verdicts `…/refuter-outputs/refuter-verdicts.md`
§"A-contract" ("L6-B2 refresh lane: CONFIRMED w/ qualification (partial prose exists; freeze CLI
cannot reissue — freeze-0001 hardcoded, mutated:false short-circuit; no successor-pack command
anywhere)") and §"A-execution" F2 ("CONFIRMED: producer exists, operative refresh lifecycle for a
frozen pack does not").

Post-verdict adjudication: routed to **Phase 0 R1** (`council-verdict.md:74-75`) and **Phase 2**
("re-freeze via the R1-ruled route ONCE, atomically, LAST among pack-byte changes … irreversible ⇒
magistrate+Ed", `:97-99`).

### (b) What changed since 2026-08-15
**(i) The ruling.** R1 freeze-evidence lifecycle ran as a rule-2 Sol consult + rule-11 cold gate.
Custody: `docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/` (`consult.md`,
`coldgate-adjudicator-ruling.md`, `coldgate-opus-refuter-findings.md`, `consult-prompt.md`) — cold
verdict **ADOPT-WITH-AMENDMENTS** (7 amendments; ruling §F). Magistrate synthesis entered at
`docs/decision_log.md:9196-9243` ("R1 RULED … content-bound design ADOPTED WITH THE COMPOSED
AMENDMENT SET"), with cl.5 **NO GRANDFATHERING**: "the 33 expired v1 receipts are never revalidated;
migration is fresh re-authoring within the Phase-2 successor family, one atomic family transaction."
Cold amendment 7 (adopted in full, cl.4): "The horizon may not be removed in any commit that does
not also land the fresh dependency-comparison validator and its cl.10 test obligations."
WHERE: the trace dir and the decision-log entries are **on main** (the council trace and decision log
predate the merge-base). *Note for the seat: the `2026-08-19-r1-r2-codesign/` trace and D-146 are a
DIFFERENT R1 — the capture-pipeline-v3 ruling — and say nothing about the PACK horizon (grep of
`13-r1-ruling.md` for `horizon|valid_until|monotonic` returns zero hits).*

**(ii) The tooling that made reissue possible.** The refuter's "freeze CLI cannot reissue —
freeze-0001 hardcoded" is cured:
- `66a433d` "WO-FREEZE-NUMBERING: freeze-receipt v2 with chain-monotonic freeze-0002 and an
  authenticated predecessor" — **main**
- `b6553fd` "delta-8: replay reauthenticates the successor; v2 freeze sequences carry the
  predecessor" — **main** (also made `--predecessor-pack-root` mandatory for successor packs)
- `9574fda` "delta-10: a validly minted REFUSE freeze receipt replays as its recorded REFUSE" — **main**
- `docs/process/phase2-transaction-runsheet.md:29-33` records why: "Step 4's 'NO code edits
  (delta-proven installable)' claim is REMOVED — it was **false** … the freeze number was hardwired
  to 1, which is precisely why WO-FREEZE-NUMBERING exists".

**(iii) The lane was actually EXECUTED, twice over, and is now written down.**
- `docs/process/phase2-transaction-runsheet.md` (117 lines) is the ordered transaction document
  (steps 1-8; step 5 = "Freeze the family: fresh receipts … one atomic family transaction, NO
  grandfathering … `--predecessor-pack-root` … exactly one `freeze-0002` per pack (singleton)").
  WHERE: on main as of `de6ccd7` (merge-gate docs batch) with later edits.
- `_v2` family froze at `freeze-0002` (predecessor shas recorded); then the `_v3` family:
  - `3a75a77` "D-147 S4: author D-134 freeze evidence for the three `_v3` packs at the measurement
    checkout (all PASS)" (2026-08-19 09:57 −0700) — **BRANCH-ONLY**
  - `5e38f1e` / `eb7f6c6` / `94dc3b3` — "D-147 S5: freeze-0003 minted for
    d117_floor_qwen25_1p5b_v3 / _7b_v3 / contrast…_v3 (PASS; predecessor `_v2`/freeze-0002 …)"
    (2026-08-19 17:28-17:29 −0700) — all three **BRANCH-ONLY**
  - `8b2b021` "S5 COMPLETE: confirmation table filled (three freeze-0003 receipts + committed tree
    digests)" — **BRANCH-ONLY**
- The lane is now operator-documented end-to-end with literal commands and a duration figure in
  `docs/process/ed-s5-mint-decision-2026-08-19.md` (95 lines, branch-only): the six-command S5
  sequence at `:56-70`, "~5 minutes" at `:41`, and the landing rule "Landing is a pull FROM the
  measurement checkout (never a push from it)" at `:72`.
- **Horizon state now (probed read-only in this worktree at `time.monotonic_ns()` ≈
  2,415,087,816,993,791):** the three `_v3` packs carry **33** PACK evidence receipts
  (`configs/campaigns/d117_*_v3/arm_readiness.evidence/*.json`, 11 each) and **all 33 are LIVE** —
  `valid_until_monotonic_ns` 2,468,742,407,178,458 / 2,468,774,933,440,083 / 2,468,792,444,508,708,
  i.e. ~15 hours remaining, lapsing ≈ 2026-08-20 17:28 PST. The 66 `_v1`/`_v2` receipts remain lapsed.

**(iv) What did NOT change — the mechanism.**
- The 24 h stamp is untouched: `joulewise/arm_readiness_evidence.py:42`
  `_EVIDENCE_VALIDITY_NS = 86_400 * 1_000_000_000`, applied at `:2421`
  (`valid_until = evaluated_at_monotonic_ns + _EVIDENCE_VALIDITY_NS`).
- The `_v3` receipts are the **OLD schema**: all 33 parse as
  `joulewise.arm_readiness_evidence_receipt.v1` and carry both `valid_until_monotonic_ns` and
  `boot_session_id` (verified by direct JSON read). The R1 content-bound schemas ruled at
  `docs/decision_log.md:9264-9270` (`joulewise.arm_readiness_content_evidence_receipt.v1`,
  `joulewise.arm_readiness_execution_evidence_receipt.v1`) are **not what the frozen family uses** —
  `grep -rn "content_receipt\|arm_readiness_evidence_content\|dependency_divergent" joulewise/*.py`
  returns nothing. The R1 registry install is **step 4 of the runsheet and still Ed-reserved**:
  `docs/process/phase2-transaction-runsheet.md:11-15` "step 4 (R1 registry install) NEEDS_RULING on
  Ed-reserved values (five items)"; `docs/process/ed-s5-mint-decision-2026-08-19.md:90-92` "R1
  row-registry reserved values — three of five are now supplied".
- The same-boot + 24 h coupling B2 named is therefore **still live and now stated in operator prose**:
  `docs/process/ed-s5-mint-decision-2026-08-19.md:41-46` — "the S4 evidence EXPIRES
  ~2026-08-20T16:51:33Z and dies on ANY REBOOT (boot session
  `da90818c-9c31-45d0-8813-deae65fba143`). After either event: `git rm -r` of the six governed
  evidence dirs and a full S4 re-author before S5 can run. **DO NOT REBOOT the Mac before ruling.**"
- **The runbook still does not name the refresh lane.** `grep -n "re-freeze\|refresh lane\|
  freeze-refresh\|re-author" docs/phase_2/window_runbook.md` returns exactly one hit — `:1012`, the
  T-0 namespace re-authoring paragraph. §4/§5C are unchanged on this point. The lane lives only in
  the transaction runsheet and the branch-only S5 packet, neither of which is the night document.
- **ED-QUAL-L6-2** asked for one *timed* freeze-refresh rehearsal grounding the window-day schedule
  in an observed duration. The S5 packet's "~5 minutes" covers the six mint commands only; no timing
  of the full lane (re-author → freeze → commit → review → fresh dry-run) was found.

### (c) Candidate disposition for the seat
**STILL-OPEN, with substantial partial repair (branch-only).** The seat is adjudicating whether an
executed, ruled, once-through re-freeze that produced 33 currently-live receipts — but left the 24 h
+ same-boot mechanism intact, left the ruled content-bound schema uninstalled behind an Ed-reserved
registry ruling, left the lane out of the operative runbook, and lives entirely on
`impl/r2-s0-mint-resolver` — discharges a blocker whose complaint was that no *operative document*
names a producible path to a valid GO arm receipt.

### (d) Skeptical probes
1. **Time-bomb probe.** Recompute the `_v3` horizons at sitting time:
   `python3 -c "import json,glob,time; print(time.monotonic_ns()); [print(f, json.load(open(f))['valid_until_monotonic_ns']) for f in glob.glob('configs/campaigns/d117_*_v3/arm_readiness.evidence/*.json')]"`.
   If the sitting is after ≈2026-08-20 17:28 PST, **all 33 are lapsed again** and B2 is empirically
   un-repaired — the cure was data, not machinery.
2. Has the Mac rebooted? `sysctl kern.bootsessionuuid` vs `da90818c-9c31-45d0-8813-deae65fba143`
   (recorded in every receipt). A reboot voids all 33 regardless of the horizon.
3. `grep -rn "freeze-0003\|_v3\|20260818" docs/phase_2/window_runbook.md` → if zero hits, the night
   document still points at the retired family and the retired checkout, and the "operative document"
   half of B2 is untouched.
4. Ask what happens on the **next** window after these lapse. Is the answer still "run the runsheet"?
   The runsheet is a one-time Phase-2 transaction document ("Phase-2 atomic re-freeze — execution
   runsheet", `:1`), not a repeatable window-day lane.
5. Cold amendment 7 ordering check: the horizon was NOT removed, so amendment 7 is satisfied
   vacuously — but confirm the fresh dependency-comparison validator genuinely does not exist
   (`grep -rn "dependency_divergent\|dependency manifest" joulewise/`), because R1's whole staleness
   guarantee rests on it and cl.2 of the ruling records "TODAY neither head comparison nor manifest
   replay executes on the evidence path".
6. Charter amendment 12: `5e38f1e`/`eb7f6c6`/`94dc3b3` rotated the pack digests. Does
   `docs/process/audit-baseline-manifest.json` still bind the old digests? (See L6-S4 (b) — it does,
   and it has never been touched: single commit `694442c`.)

---

## L6-S2 — D-117 two-stage mint freeze: stage-1 desk pin artifact has no committed instance

### (a) Original finding (VERBATIM)
> - [should_fix] [L6] S2 — D-117 two-stage mint freeze: the stage-1 desk pin artifact (floor_mint_pin_requirements.v2) has no committed instance and nothing fails closed on its absence

Citation: `sitting-packet-FINAL.md:120`; seat report
`…/seat-reports/L6-SEAM-READER-A-report.md:52,:75`. No post-verdict adjudication found.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** The schema id lives in exactly two places at HEAD:
  `scripts/mint_floor_artifact_generalized.py:64`
  (`PIN_REQUIREMENTS_SCHEMA_VERSION_V2 = "joulewise.floor_mint_pin_requirements.v2"`) and
  `scripts/floor_mint_pinsets/schema_v2.json:976`.
- No committed instance: `git ls-files scripts/floor_mint_pinsets/` = `mint1.json` + `schema_v2.json`
  only; `mint1.json:2` is `joulewise.floor_mint_pinset.v1` (a pinset, not pin-requirements), from
  `4e94e70` (pre-council).
- Nothing fails closed on absence: the only consumer is a **presence**-rejecting guard,
  `scripts/mint_floor_artifact_generalized.py:1416-1417` — `if schema_version ==
  PIN_REQUIREMENTS_SCHEMA_VERSION_V2: raise MintError("desk-stage pin requirements are non-mintable")`.
  Absence is silent, exactly as filed.
- Branch-only commits touching the mint script since the merge-base — `cef3306`, `8018a4b`, `3038eeb`
  (D-147 S0/S1 mint-policy resolver work) — leave the constant as unchanged context and add no
  instance. WHERE: all three **branch-only**.
- No ruling either way: `docs/process/ed-s5-mint-decision-2026-08-19.md` has zero `stage` hits;
  `docs/process/phase2-transaction-runsheet.md` has zero hits for `two-stage`/`stage-1`/
  `pin_requirements`/`desk pin`; D-147 (`docs/decision_log.md:170`) governs the generation-indexed
  mint-policy resolver and says "no new tracked tooling". The `two-stage` hits in the decision log
  (`:159,505,8605,8778,8937`) are D-134's arm-readiness two-stage, a different mechanism.

Searched: `floor_mint_pin_requirements`, `PIN_REQUIREMENTS_SCHEMA_VERSION_V2`, `pin_requirements`,
`desk-stage`, `desk pin`, `two-stage`, `stage-1`, `mint_floor_artifact` across the repo, the decision
log, the runsheet, the S5 decision packet, and `2026-08-19-r1-r2-codesign/14-r2-ruling.md`.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating a should-fix that has neither been fixed nor ruled
out of scope — and whether "stage-1 desk pin" is still an operative D-117 concept at all, or dead
vocabulary surviving only in the mint script and its schema.

### (d) Skeptical probes
1. `git log --oneline --all -S"floor_mint_pin_requirements"` — has anyone ever authored an instance
   on any branch?
2. Is the two-stage mint freeze still the design? Put the question to whoever owns D-117: if the
   answer is "superseded by D-147's resolver", this row should be STRUCK, not carried.
3. Construct the failure: run the generalized mint with **no** pin-requirements artifact present.
   Does it mint? If yes, "nothing fails closed on its absence" is executed, not asserted.
4. `grep -rn "schema_v2.json" scripts/ tests/` — is the v2 pinset schema itself exercised by any
   test, or is the whole v2 lane unreachable?

---

## L6-S3 — §12 postcollection backup receipts have no producer

### (a) Original finding (VERBATIM)
> - [should_fix] [L6] S3 — §12's postcollection backup receipts have no producer: backup_runs.sh emits no receipt and no hash

Citation: `sitting-packet-FINAL.md:121`. No post-verdict adjudication found.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** `scripts/backup_runs.sh` (74 lines) has one real commit in its whole history:
  `5b12332` "P0-002: measurement-corpus backup script (R-016, playbook M2)", **2026-07-06**,
  **on main**. Nothing since 2026-08-15; nothing on the branch.
- `grep -n "sha256\|receipt\|shasum" scripts/backup_runs.sh` → **no matches**. Its only durable output
  is the append at `:38-43`/`:61`:
  `printf "%s source=%s rsync_status=%s bundle_count=%s\n" … >> "$DEST/backup.log"`.
- What §12 still demands: `docs/phase_2/window_runbook.md:1807` "the backup-preflight receipt path
  and SHA-256"; `:1808-1810` "each successful postcollection backup receipt path and SHA-256,
  recorded separately from backup preflight and separately for the claim and bound roots"; `:1825`
  "backup destination and exit status" (the only clause the script can satisfy). The §11 call site
  (`:1758-1762`) asks only for exit 0.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating an unrepaired producer gap on the post-collection
plane, where the runbook's own close-out list demands two receipt-path-plus-SHA-256 records that no
tool emits.

### (d) Skeptical probes
1. Read `scripts/backup_runs.sh` end to end at the sitting — 74 lines; confirm no receipt path.
2. `ls ~/JouleWise-window-custody/**/backup*` — does any *hand-written* backup receipt exist from a9
   or a10, i.e. is the operator already improvising this at close-out?
3. Ask which seat owns the remedy. L10's nit ("backup_runs.sh counts campaign_manifests/ as a
   bundle", `sitting-packet-FINAL.md:157`) touches the same script — one work order or two?
4. Does §12 have a checklist that mechanically blocks close-out on a missing backup receipt, or is it
   prose only? `sed -n '1795,1830p' docs/phase_2/window_runbook.md`.

---

## L6-S4 — The FINAL arm packet is stale against the baseline runbook

### (a) Original finding (VERBATIM)
> - [should_fix] [L6] S4 — The FINAL arm packet (the operator's night document, cited by the audit-baseline manifest) is stale against the baseline runbook

Citation: `sitting-packet-FINAL.md:122`; seat report `…/seat-reports/L6-SEAM-READER-A-report.md:59`
(census row 38: "FINAL arm packet … ✖ STALE (S4): no T-0 E-step; 'expect a refusal unless §0.6' —
§0.6 is closed at this baseline") and `:77`. Same defect filed independently by L8 as **B5**
(`…/seat-reports/L8-OPERATOR-RECOVERY-HUMAN-FACTORS-report.md:104`).
Post-verdict adjudication: remedy ratified as refuter B-contract **F5** ("issue reviewed SUCCESSOR
packet; preserve old as custody"), sequenced by `council-verdict.md:99-100` (Phase 2, "the successor
arm packet ONLY after the T-0 repair passes end-to-end at the exact reviewed head (Opus W8)") and
`opus-contract-refuter-findings.md:71` ("Record as a hard dependency or L8-B5 recurs verbatim").

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND — and the row is aggravated.** No successor arm packet exists in the repo, in
  custody, as a draft, or as a queued work order.
  - Off-repo custody: `/Users/edr/JouleWise-window-custody/t4-session-20260810/` still holds
    `arm-packet-alpha-FINAL-20260813.md` (mtime **2026-08-13 20:21**, 67,081 B) as the newest packet.
    `find ~/JouleWise-window-custody -type f -newermt 2026-08-13` returns only shakedown /
    profiler-pilot / ed-qual / dry-run-receipt material — no packet.
  - `find . -iname "*arm-packet*"` in the repo → zero (the packet has never been in-repo).
  - `TASK_QUEUE.md` carries **no** work-order row for a successor packet.
  - `docs/process/phase2-transaction-runsheet.md:103-112` (step 8) still speaks prescriptively:
    "The successor packet carries exactly one informational note…".
  - `RUN_STATE.md:723` still names `arm-packet-alpha-FINAL-20260813.md` "The operative packet (111
    cells filled, 34 AT-T0)"; `RUN_STATE.md:603` still lists "Phase 2 re-freeze ONCE atomically LAST
    + successor packet → Phase 3 manifest SUPERSESSION" as future work.
- **The manifest still cites the stale packet, and its own baseline has drifted.**
  `docs/process/audit-baseline-manifest.json:3` — `"arm_packet": "~/JouleWise-window-custody/
  t4-session-20260810/arm-packet-alpha-FINAL-20260813.md (off-repo custody)"`. The file has exactly
  one commit ever, `694442c` (**main**), and is untouched in `311d8016..HEAD`. Its
  `runbook_sha256` = `25a4e809…` reproduces from `git show ac3fe1d:docs/phase_2/window_runbook.md`
  (1,588 lines); the current worktree runbook hashes `8e1b76e2…` at **1,875 lines**. Council
  **Phase 3 supersession has not happened**.
- **The runbook moved ~+422/−124 lines across 10 commits since `8937dec`**, nine on main and one
  branch-only — every one of them a premise the packet was written against:
  `a61ac92` (**main**, +220/−61, T-0 producer + `window.env` frozen-literal contract),
  `345bfbb` (**main**, launch-binding), `65cc0f3` (**main**, F4 honest contract),
  `e7fa8fd` (**main**, `consume` now refuses `readiness_usage_invalid` and points at
  `scripts/launch_window.py`), `72cd698` (**main**), `9d3ba21` (**main**, E-9a/E-9b/E-9c renumbering),
  `b6553fd` (**main**, `--predecessor-pack-root` mandatory), `de6ccd7` (**main**, `freeze-000N`),
  `844453a` (**main**, `window.env` flipped to the `_v2` family), `f4d5ea7` (**branch-only**, D-079 r3).
- D-149 (`docs/decision_log.md:8866-8872`, standing conditional T-0 GO / auto-issued GO receipts)
  rewrote the T-0 GO regime after the packet was written, further invalidating its night choreography.
  `docs/process/d149-go-receipt-template.md` is **branch-only** at HEAD `79a4cd0`.

Searched: `arm packet|arm-packet|successor packet|successor arm|packet reissue|WO-PACKET|L8-B5|L6-S4`
repo-wide; `git log --all --grep` for the same; `find` over `~/JouleWise-window-custody`;
`docs/process/` operator documents; `docs/decision_log.md` D-138…D-149; the 08-18/08-19 trace dirs.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND (aggravated).** The seat is adjudicating a should-fix whose gate condition
(Phase 2: T-0 repair passing end-to-end at the exact reviewed head) has not been reached, while the
document's staleness grew by ~422 runbook lines, a family rotation (`_v1`→`_v3`), and a wholesale
T-0 GO-regime rewrite (D-149) — and whether L6-S4/L8-B5 should be re-severitised upward given that
the audit-baseline manifest still points at it as authoritative.

### (d) Skeptical probes
1. `shasum -a 256 <(git show ac3fe1d:docs/phase_2/window_runbook.md)` vs the manifest's
   `runbook_sha256`, then against the current file — confirm the manifest's `invalidation_rule`
   ("any repo change after this manifest voids affected lens results") is live-triggered.
2. Open `arm-packet-alpha-FINAL-20260813.md` and grep it for `capture_t0_step`, `E-9a`, `E-9c`,
   `launch_window.py`, `_v3`, `freeze-0003`. Zero hits on any of these = the operator's night
   document cannot be followed at the current head.
3. Ask for the work-order row. If no row exists in `TASK_QUEUE.md` or the state kernel, the remedy
   has no owner and no trigger — an unregistered obligation, which is the same class of defect L1-B3
   raised about work-selection authority.
4. Check the ordering claim: has the T-0 repair "passed end-to-end at the exact reviewed head"?
   (See L6-B1 probe 2 — no `arm_readiness.t0.inputs` directory exists anywhere.) If not, Phase 2's
   precondition is unmet and this row cannot close by design — which the seat should record as a
   dependency, not a defect.

---

## L6-N1 — window_duration_margins_receipt.v1 has no machine consumer

### (a) Original finding (VERBATIM)
> - [nit] [L6] N1 — window_duration_margins_receipt.v1 has no machine consumer; §11 ordering is unenforced

Citation: `sitting-packet-FINAL.md:123`.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** Producer: `scripts/record_window_duration_margins.py` over
  `joulewise/window_duration_margins.py` (`RECEIPT_SCHEMA_VERSION` `:43`,
  `render_window_duration_margins_receipt` `:169`, `validate_window_duration_margins_receipt` `:1032`).
  Consumers outside the module and its tests: **none** — `grep -rn "window_duration_margins"` over
  `.py` hits only `joulewise/window_duration_margins.py` (`:156`, `:1009`) and
  `tests/test_window_duration_margins.py`.
- **WO-MARGIN-RECORDER-AUTHZ `00ec3b7` (#151) is authorization, not consumption** — WHERE: **main**
  (also an ancestor of the merge-base). Its two files are
  `joulewise/window_duration_margins.py` and `tests/test_window_duration_margins.py` (+477 test
  lines); the hunks add `authoritative_input_invalid` refusal normalisation, an
  exactly-one-registry-source check (`registered_cell_inventory_invalid`), a symlink
  resolution-invariance guard before `allow_governed_extraction_spec`, and `pack_pin_invalid` sha
  checks. All harden the writer's read grant. No reader of the emitted receipt was added.
- Zero commits touch either file in `311d8016..HEAD`. §11 ordering remains prose at
  `docs/phase_2/window_runbook.md:1730`.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating whether an unconsumed receipt on the post-collection
ordering seam stays a nit now that #151 has hardened the producer's authority without giving the
artifact a reader.

### (d) Skeptical probes
1. `grep -rn "duration_margin" scripts/ joulewise/ --include=*.py | grep -v window_duration_margins.py`
   → confirm zero.
2. Does `docs/process/d149-go-receipt-template.md` (the new GO-receipt evaluator) consume it? If the
   D-149 checklist could cheaply become the machine consumer, the remedy is nearly free.
3. If §11 ordering is unenforced, construct the violation: record margins **after** extraction and see
   whether anything refuses.

---

## L6-N2 — PRIVILEGE_INSTALLATION evidence kind has no producer

### (a) Original finding (VERBATIM)
> - [nit] [L6] N2 — PRIVILEGE_INSTALLATION evidence kind has no producer anywhere in the repo

Citation: `sitting-packet-FINAL.md:124`.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** Consumer side fully wired in `joulewise/arm_readiness.py`: predicate specs
  `:811,:815,:819,:822`; kind map `:916-919` (`privilege.activation_fence.v1`,
  `privilege.fresh_authorization.v1`, `privilege.installed_bytes.v1`,
  `privilege.isolated_interpreter.v1`); allowed-probe set `:661`; class `EXECUTION_BOUND` `:698`.
  Registry rows `configs/arm_readiness/d117_row_registry_v1.json:25-28,66-69,107-110,303-334`.
- Producer side: nothing. Those four ids appear only in `arm_readiness.py` and the registry JSON.
  `scripts/author_arm_readiness_evidence.py` has no `privilege` hit;
  `joulewise/arm_readiness_evidence.py` has no `privilege.*` id.
- `a61ac92` (#152, **main**) did **not** add one: `scripts/capture_t0_step.py` declares exactly three
  schemas (`:38-40`), and its only `privilege` string is a docstring at `:765`. The D-127 route it
  shipped, `scripts/joulewise-network-time.sudoers`, produces no evidence receipt.
- `docs/decision_log.md:9331` still lists `PRIVILEGE_INSTALLATION` among the `EXECUTION_BOUND` kinds
  with no producer named.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating whether the nit's own caveat ("N/A only while
`clock_route` stays MANUAL") still holds now that D-127's sudoers file has shipped as bytes —
because installing it is precisely the event this evidence kind would attest.

### (d) Skeptical probes
1. If Ed installs `scripts/joulewise-network-time.sudoers`, does `clock_route` leave MANUAL? If yes,
   this nit becomes load-bearing at exactly the moment the D-127 Ed row closes. Check
   `grep -rn "clock_route" joulewise/ configs/`.
2. `grep -n "PRIVILEGE_INSTALLATION" configs/arm_readiness/d117_row_registry_v1.json` — is the row
   gated OFF for the funded packs, or would arm evaluate it and refuse for absent evidence?
3. Ask whether the four `privilege.*` predicate specs are dead code that should be removed rather
   than given a producer.

---

## L6-N3 — Arm-time freeze-evidence replay skips the monotonic-horizon check

### (a) Original finding (VERBATIM)
> - [nit] [L6] N3 — The arm-time freeze-evidence replay skips the monotonic-horizon check; defense is one hop downstream

Citation: `sitting-packet-FINAL.md:125`. **Same defect as L7's first should-fix**
(`sitting-packet-FINAL.md:145`) — two seats, two severities; the seat should note the split.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** In `joulewise/arm_readiness.py` at HEAD: the horizon check lives in
  `_authenticate_generic_evidence_item` (def `:4163`) behind an **optional** parameter
  `now_monotonic_ns: int | None = None` (`:4171`); the refusal is `:4271-4278`. Both freeze-replay
  call sites omit it — `_load_freeze_reference` (def `:5151`, call `:5253-5262`) and
  `_freeze_evidence_for_arm` (def `:5360`, call `:5385-5392`) pass only
  `expected_boot_session_id` / `expected_head_commit` / `lifecycle_registry`.
- The real horizon enforcement, `validate_r1_class_lifecycle` (def `:3344`, horizon branch
  `:3378-3387`), has exactly two call sites — `:4585` in `_discover_evidence` and `:6543` in
  `_verify_arm_receipt` — neither on the freeze-replay path. That is literally "one hop downstream".
- `git diff 311d8016..HEAD -- joulewise/arm_readiness.py` is a **single 16-line hunk** inside
  `_issued_d079` (~`:4134`) adding `d079_calibration_acceptance_v2_n17_r3/r4/r5/r6` ids; grepping
  that diff for `monotonic` returns nothing. The horizon plumbing visible in `ac3fe1d..HEAD` came
  from `8fd29f7` "R1 freeze-evidence lifecycle (Phase-2 prep)" and `9e71279` (both **main**), both of
  which the seat was already reading — count of `now_monotonic_ns` occurrences went 9 → 16 → 19 and
  has stayed 19 through every branch commit.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** The seat is adjudicating an unchanged code seam that a sibling gating seat (L7)
filed at higher severity, on a branch where the frozen family's receipts are once again within their
horizon — i.e. the downstream defense is currently untested by live conditions.

### (d) Skeptical probes
1. Re-run the count: `grep -c now_monotonic_ns joulewise/arm_readiness.py` (expect 19) and confirm
   `:5253-5262` and `:5385-5392` still omit the kwarg.
2. Reconcile the severity split with L7 before ruling: one defect cannot be both a nit and a
   should-fix in the same packet.
3. Ask whether the R1 ruling *intends* this: cl.1 splits the taxonomy so `RE_DERIVABLE` kinds carry
   no validity at all. If the frozen family migrates to
   `joulewise.arm_readiness_content_evidence_receipt.v1`, the replay-time horizon check becomes
   meaningless — so the correct remedy may be the registry install, not a kwarg.

---

## L6-COVERAGE — 34/40, self-nominated denominator

### (a) Original finding (VERBATIM)
Seat table row: `sitting-packet-FINAL.md:24` — `| L6-SEAM-READER-A | GATING | NOT_READY | 34/40 | 2 | 3 | 3 | 5 | 6 | 2 |`
Seat's own denominator statement, `…/seat-reports/L6-SEAM-READER-A-report.md:10`:
> 40 artifact-class nodes across five planes of the chain (pack → arm → collection → post → governance). Node list = column 1 of the graph table in §3; the schema-ID census over `joulewise/`+`scripts/` (~120 IDs) was used as the enumeration cross-check, with off-chain families (AXI spikes, load-transition, wo003/wo005, publication capsule) excluded as out of this council's window-chain scope.

and `:14`:
> **34 / 40 nodes examined** = producer and consumer located and at least spot-verified in code against the contract; 6 partial (frozen-plan instance off-repo/by-design absent; salvage artifacts lead-authored-by-design; claims-index deep trace; deep internals of ledger/capture/verdict owned by seats L2–L4; duplicate node; conditional privilege path).

Council ruling on all coverage numbers — `council-verdict.md:18-22`:
> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every seat's evidence universe was self-nominated, and the one denominator adversarially tested fell. Closing all listed work orders does not entitle READY; the READY-candidate re-audit must re-enumerate every universe independently and run the adversarial coverage attack as a standing packet element.

Reinforced at `docs/council_log.md:3760`: "the fleet's aggregate coverage (219/253 …) is arithmetic
over self-nominated denominators and is NOT an audit-coverage figure … the honest statement is that
coverage is unquantified pending the Phase-3 re-enumeration."

### (b) What changed since 2026-08-15
- **Yes, L6's universe was self-nominated** — the seat says so in its own words above (it chose the
  40 nodes and chose the exclusions).
- **The ordered re-enumeration has not run for L6.** The only re-audit executed is **WO-L2-REAUDIT**
  (`docs/process_traces/2026-08-15-l2-reaudit/`, custody `0f886d3`, **main**), which is scoped to L2 —
  its `reaudit-prompt.md:10` carries the adversarial coverage attack for calibration acquisition only.
  Council **Phase 3** ("focused re-audit of pack/custody-bearing seats (L1, L5, L7 minimum) +
  adversarial coverage re-enumeration of all universes", `council-verdict.md:102-104`) is unexecuted:
  the baseline-manifest supersession that opens Phase 3 has not happened (single manifest commit
  `694442c`, untouched).
- Note L6 is **not** in Phase 3's named minimum set (L1, L5, L7) even though it is a gating seat with
  a self-nominated 40-node denominator.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating whether L6 may carry 34/40 into a READY-candidate sitting
when the council ruled the denominator itself untrustworthy, ordered independent re-enumeration as a
standing packet element, and that re-enumeration has been performed for exactly one seat (L2) — not
this one.

### (d) Skeptical probes
1. Attack the exclusions directly: "AXI spikes, load-transition, wo003/wo005, publication capsule"
   were declared out of window-chain scope by the seat. Is any of them reachable from a funded-window
   artifact? If yes, the denominator is understated.
2. Re-run the enumeration cross-check independently: census schema IDs over `joulewise/` + `scripts/`
   at HEAD and compare the count against the seat's "~120 IDs". `_v3`, `freeze-0003`, the D-149 GO
   receipt, and `capture_t0_step`'s three schemas are all post-baseline additions the seat never saw.
2b. Specifically: `capture_t0_step.py:38-40` adds three schema IDs; `d149-go-receipt-template.md`
   adds a GO-receipt artifact class. Both are new nodes in L6's own graph, unexamined.
3. Ask whether the six "partial" nodes have moved. The frozen-plan instance was "off-repo/by-design
   absent; none exists yet for the next window" (`sitting-packet-FINAL.md:206`) — does one exist now?
4. Demand the Phase-3 artifact. If no independent re-enumeration document exists for L6, the coverage
   line is UNVERIFIED by the council's own standing rule, regardless of how the six findings resolve.

---

## ROW-LEVEL OPEN ITEMS
- **L6-S2** (stage-1 mint pin): NO-REPAIR-FOUND. No instance, no producer, no absence-check, and no
  ruling on whether the two-stage mint freeze is still the operative design.
- **L6-S3** (backup receipts): NO-REPAIR-FOUND. `scripts/backup_runs.sh` unchanged since 2026-07-06
  (`5b12332`); runbook §12 still demands two receipt-path+SHA-256 records nothing emits.
- **L6-S4** (successor arm packet): NO-REPAIR-FOUND and aggravated. No packet, no draft, no queue
  row; the audit-baseline manifest (`694442c`, never touched) still cites the 2026-08-13 FINAL packet
  while the runbook has moved ~+422/−124 lines and D-149 rewrote the T-0 GO regime.
- **L6-N1** (margins receipt consumer): NO-REPAIR-FOUND; #151 added authorization only.
- **L6-N2** (PRIVILEGE_INSTALLATION producer): NO-REPAIR-FOUND; consumer-side only, and the D-127
  sudoers file that would make it live has shipped as bytes.
- **L6-N3** (replay-time horizon check): NO-REPAIR-FOUND; `joulewise/arm_readiness.py` diff since the
  merge-base is one 16-line D-079 id-set hunk. Unreconciled severity split with L7's should-fix.
- **L6-B1 riders:** (i) the Ed/advisor paper-scope ruling at `docs/decision_log.md:9640-9647`
  (trusted-operator T-0 evidence vs the signed-capture option) is unanswered; (ii) the
  terminal-review commit-trailer producer has no implementation and is bound to the unexecuted
  Phase-3 supersession; (iii) ED-QUAL-L6-1's live PASS side has never been exercised — no
  `arm_readiness.t0.inputs` directory exists anywhere on the machine.
- **L6-B2 riders:** (i) the R1 content-bound schemas are ruled but **not installed** — the `_v3`
  receipts are still `joulewise.arm_readiness_evidence_receipt.v1` with the 24 h
  `_EVIDENCE_VALIDITY_NS` stamp; the R1 registry install is runsheet step 4, NEEDS_RULING, 3 of 5
  Ed-reserved values supplied; (ii) the entire freeze-0003 re-freeze is **branch-only**
  (`3a75a77`, `5e38f1e`, `eb7f6c6`, `94dc3b3`, `8b2b021`); (iii) the refresh lane is documented in the
  Phase-2 **transaction** runsheet and a branch-only Ed decision packet, **not** in the operative
  runbook (one hit, `docs/phase_2/window_runbook.md:1012`); (iv) ED-QUAL-L6-2's timed full-lane
  rehearsal is undischarged — only "~5 minutes" for the six mint commands is recorded;
  (v) the 33 live receipts lapse ≈2026-08-20 17:28 PST and die on any reboot.
- **Coverage:** L6's 40-node denominator is self-nominated (seat's own words); no independent
  re-enumeration or adversarial coverage attack has been run for L6 — the only executed re-audit is
  WO-L2-REAUDIT, and L6 is not even in Phase 3's named minimum set (L1, L5, L7).
- **Assembler note on the brief:** the brief pins the worktree at `d10881b`; the actual branch tip in
  the read-only worktree is `79a4cd0` (`d10881b` is its parent's parent). Nothing in this row depends
  on the difference, but the seat should know the packet was assembled two commits later.
