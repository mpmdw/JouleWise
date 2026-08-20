# ROW ED-QUALIFICATION — all seats (GATING: the clearance rule turns on this file)
Original verdict: NOT-READY (0 READY / 11 NOT-READY; L2 additionally UNVERIFIED on coverage).
23 ED-QUALIFICATION rows emitted across seats L1, L2, L3, L4, L5, L6, L7, L8, L9, L10.

**Assembler note (read before the table).** This file attaches evidence and names a
CANDIDATE disposition per row. It does not grade. Three states are kept sharply apart,
per the assignment's honesty requirement:
(i) **the mechanism to perform the row now exists** (a script, a card, a plan, a ruling
authorizing a session) — this is NOT closure;
(ii) **the row was actually performed and its output custodied** — this is closure evidence;
(iii) **a ruling retired the row** — this is supersession.
Where only (i) was found, the disposition is ED-ROW-OPEN or ED-ROW-PARTIAL.

**Repo state for every pointer below.** Worktree
`.../scratchpad/wtS0`, branch `impl/r2-s0-mint-resolver`. NOTE FOR THE SEAT: HEAD is
`b92b43d` at assembly time, **not** the `d10881b` named in the assembler brief — three
docs/prep commits landed after the brief was written (`79a4cd0`, `4597ad4`, `b92b43d`);
none touch pack bytes or evidence. `main == origin/main == 0099382`.
All 2026-08-17/18 qualification-era documents cited here are **merged to main**.
All S4/S5 `_v3` freeze material is **branch-only**.

---

## PREAMBLE — the charter rule that governs all 23 rows

### (a) Original text (VERBATIM)

Charter §"Ed rows (amendment 10)" — `docs/process/instrument-readiness-audit-charter.md:70-77`:

> ## Ed rows (amendment 10)
>
> Hardware/privilege rows split into: ED-QUALIFICATION (stable
> capabilities — sudo powermetrics behavior, sampler child supervision
> live, the JW-MET-3 rail probe — performed BEFORE the sitting, in any tap
> block; stable evidence cannot be deferred) and T0 (genuinely perishable
> same-night observations — live census at arm, clock stabilization).
> Only T0 rows may remain open at the sitting.

Charter §"Verdict form (amendments 11-12)" — same file, `:81-83`:

> READY-WITH-CONDITIONS is DELETED. Per component: READY / NOT-READY(+work
> orders) / UNVERIFIED. Council READY requires: no NOT-READY, no
> UNVERIFIED, all ED-QUALIFICATION rows closed with evidence. T-0 GO is a
> SEPARATE, later closure bound to the arm-night's perishable rows — the
> council's READY never implies it.

Council's ordered Ed-required batched-session list — `council-verdict.md:89-96` (VERBATIM):

> **Ed-required (ONE batched session when Phase 1 nears close; ~expanded qualification script):**
> D-127 sudoers install + exercise (explicit ratification — amends D-004 posture) · full dress
> rehearsal E-4→E-9 + author→arm→verify→consume vs scratch custody (the program's most valuable
> Ed hour) · sampler checklist, SIGTERM relay, rail probe · keyboard-backlight rows · ED-Q-L9-3
> quiet-state baseline EARLY (gates census WO) · production-machine freeze-chain replays ·
> EDQ-L2-2 §5C live verification · a9/a10 desk replay (Ed-held corpus) · ED-QUAL-L4-1 decisive
> replay (network, independent scheduling).

**Mapping of that list onto the rows it was meant to close** (assembler-derived; each item
verified against the row text in `sitting-packet-FINAL.md §5`):

| Council list item (in order) | Rows it was meant to close |
|---|---|
| D-127 sudoers install + exercise (explicit ratification) | **ED-Q-L8-1** (primary); enables ED-QUAL-L5-1's capture vectors |
| Full dress rehearsal E-4→E-9 + author→arm→verify→consume vs scratch custody | **ED-Q-L8-2** (primary), **ED-QUAL-L6-1**, **ED-QUAL-L5-1**, **ED-L7-1** (its E-7a/E-7b legs) |
| Sampler checklist | **ED-L3-1**, **ED-Q-L8-3** (half), **ED-L3-4** (co-closed) |
| SIGTERM relay | **ED-L3-2** |
| Rail probe | **ED-L3-3**, **ED-Q-L9-2**, **ED-Q-L8-3** (half) |
| Keyboard-backlight rows | **ED-Q-L9-1** |
| ED-Q-L9-3 quiet-state baseline EARLY (gates census WO) | **ED-Q-L9-3** |
| Production-machine freeze-chain replays | **ED-QUAL-L1-1**, **ED-QUAL-L1-2**, **ED-QUAL-L6-2** |
| EDQ-L2-2 §5C live verification | **EDQ-L2-2**, **ED-L7-2** (same dry-run receipt) |
| a9/a10 desk replay (Ed-held corpus) | **ED-L10-1** |
| ED-QUAL-L4-1 decisive replay (network) | **ED-QUAL-L4-1** |
| *(not on the council's list)* | **EDQ-L2-1** (crash matrix), **ED-L7-3** (fiducial seam), **ED-Q-L8-4** (quiet_mac_prep literals) — these three ED rows were never carried into the batched-session script and are the list's own coverage gap |

### (b) What changed since 2026-08-15
- The batched session was assembled (`docs/process/ed-batch-packet.md`, `b352cff`-era, on main)
  and its hardware half executed on the evening of **2026-08-17, ~17:40–22:05 PT**, ordered by
  `docs/process/ed-evening-checklist.md` (on main).
- Results ledger: `docs/run_reports/2026-08-18-t10-session.md:104-116` (table "Ed's qualification
  evening — every stable row CLOSED") and `docs/process/ed-morning-packet-2026-08-18.md:110-126`
  ("Qualification ledger"). Both are on main.
- **Custody root for that evening is OFF-REPO: `~/JouleWise-window-custody/ed-qual-20260817/`.**
  No file under it is in the repo. Every "CLOSED" claim below that rests on it is a
  *second-hand report of a primary artifact this assembler could not read*. Repo-side
  corroboration exists only where the run produced a commit (see ED-L3-1, ED-QUAL-L4-1).
- D-139 (Ed's A1–A3), D-142 (identity B-keep + standing night license), D-148 (seven rulings),
  D-149 (standing conditional T-0 GO) were all adopted after the council.
  **NONE of them retires any ED-QUALIFICATION row.** D-149 clause (1) re-asserts the clearance
  rule verbatim (`docs/decision_log.md:173`: "a READY-candidate council verdict stands (charter
  form: no NOT-READY, no UNVERIFIED, ED-QUALIFICATION rows closed)"). D-148.4 delegates *quiet
  windows* to the lead but expressly reserves "hardware/sudo/physical items" to Ed.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL (aggregate).** Of 23 rows the assembler finds 3 with candidate closure
evidence, 12 partial, 8 with nothing found. Under amendment 10 ("stable evidence cannot be
deferred"; "Only T0 rows may remain open at the sitting") and amendment 11 ("all
ED-QUALIFICATION rows closed with evidence"), the seat is adjudicating whether the clearance
rule can be satisfied at all on the present record, and — separately — whether an off-repo
custody root the packet cannot read counts as "closed with evidence".

### (d) Skeptical probes
- `ls -R ~/JouleWise-window-custody/ed-qual-20260817/` on the real machine: does every file the
  T10 table names actually exist, with the timestamps claimed?
- `git log --all --oneline --since=2026-08-15 -- docs/process/instrument-readiness-audit-charter.md`
  — was amendment 10/11 quietly relaxed after the verdict? (Assembler found no such commit.)
- Grep the whole decision log for any entry retiring an ED row: `grep -n "ED-QUAL\|ED-Q-L\|ED-L" docs/decision_log.md`
  returns only D-149's restatement of the clearance rule and the WO-CENSUS-SEMANTICS gate.
- Three rows (EDQ-L2-1, ED-L7-3, ED-Q-L8-4) never appear in any Ed-facing checklist. Ask why the
  batched-session script's authorship dropped them, and whether other rows were dropped too.

---

## ED-QUAL-L6-1 — live T-0 authoring path on the measurement Mac

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:176`
> - [L6] ED-QUAL-L6-1 (stable capability, any tap block): execute the T-0 authoring path live on the measurement Mac — once the B1 capture helper exists, run the six E-step captures + clock attestation + launch manifest into arm_readiness.t0.inputs/ and author_arm_evidence_t0.py end-to-end under real passwordless-sudo powermetrics (POWERMETRICS_PROBE) and real systemsetup state (CLOCK_PROBE), confirming all 15 receipts author and a same-boot `generate_arm_readiness.py arm` reaches row evaluation. This lens could only prove the refusal side (P3) from the sandbox; the PASS side of the arm-plane producer seam needs Ed's machine and sudo.

### (b) What changed since 2026-08-15
- **(i) MECHANISM ONLY.** The B1 capture helper landed: `scripts/capture_t0_step.py` via
  WO-T0-PRODUCER, PR #152, merged `a61ac92` (on main). Operator card `docs/process/rehearsal-operator-card.md`
  committed `ad14ac4` (on main), which walks E-4→E-9 + author→ARM→verify→consume.
- **(ii) NOT PERFORMED.** No T-0 authoring run exists. `docs/run_reports/2026-08-18-t10-session.md:110`
  records "Dress rehearsal | **OPEN**"; `ed-morning-packet-2026-08-18.md:126` records
  "OPEN: the dress rehearsal (item 4) only."
- No later trace records an execution: `docs/process_traces/2026-08-18-shakedown-first-light/`
  ran a *calibration* driver, not the T-0 author; `2026-08-19-refreeze-execution/` is
  freeze-lane work, not arm-plane.

### (c) Candidate disposition for the seat
**ED-ROW-OPEN.** The seat is adjudicating a row whose mechanism exists and whose execution does
not — with the additional fact that the operator card targets the now-superseded `_v2` pack.

### (d) Skeptical probes
- `find ~/JouleWise-window-custody -name "arm_readiness.t0.inputs" -o -name "*t0*"` — is there an
  unlisted inputs namespace from an unrecorded attempt?
- `grep -rn "author_arm_evidence_t0\|arm_readiness.t0.inputs" docs/run_reports/ docs/process_traces/2026-08-1[89]*/`
  — any execution log at all?
- The row demands "all 15 receipts author". Does the current T-0 author still emit 15 rows after
  the D-146/D-147 transaction, or has the count moved? (`_CAPTURE_ORDER` / `_RUNBOOK_ARTIFACT_REASON_CODES`
  in `joulewise/arm_readiness_evidence_t0.py:120-165`.)
- The row requires "a same-boot `generate_arm_readiness.py arm` reaches row evaluation" — the
  current boot session `da90818c…` dates to before 2026-08-15. Does the arm path still reach row
  evaluation against a `_v3` pack, or does the pack-family change refuse first?

---

## ED-QUAL-L6-2 — timed freeze-refresh rehearsal

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:177`
> - [L6] ED-QUAL-L6-2 (stable capability, desk, no sudo but Ed's checkout): one full freeze-refresh rehearsal timed against the 24 h/same-boot coupling of B2 — re-author pack evidence, re-freeze, commit, dry-run, and measure the wall-clock of the lane so the window-day schedule in the WO2 runbook amendment is grounded in an observed duration, not an estimate.

### (b) What changed since 2026-08-15
- **(ii) PERFORMED FOR REAL, TWICE — but not as the row specifies.** The freeze-refresh lane
  executed in production, not rehearsal: (1) T10, `_v2` family re-authored + `freeze-0002` ×3
  re-minted at `/Users/edr/JouleWise-measurement-20260818` (D-143 cycle, heads `54f990d..75f22a0`,
  on main); (2) T12/T13, `_v3` S4 evidence ×3 + U11 projections `3d05982`/`6fd8bce`/`74632e3` +
  `freeze-0003` ×3 `5e38f1e`/`eb7f6c6`/`94dc3b3`, all **branch-only** on `impl/r2-s0-mint-resolver`.
- WHERE it lives: `_v2` round merged to main; `_v3` round branch-only.
- **GAPS:** the row's **dry-run** leg was never run (no receipt after `dry-run-0001`, 2026-08-13
  @ `49dcc49`); and no **observed wall-clock for the lane** was written into a runbook amendment —
  `grep -n -i "24 h\|same-boot\|freeze-refresh" docs/phase_2/window_runbook.md` returns only
  `:881` and `:1461`, neither a duration. The only timing recoverable is commit spacing
  (`3d05982` 17:26:52 → `8b2b021` 17:29:36 PT = ~2m44s for the *mint* step alone, not the lane).

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** The seat is adjudicating whether two real executions of the lane discharge a
row whose deliverable was an *observed duration folded into the window-day schedule* plus a
dry-run leg — neither of which exists.

### (d) Skeptical probes
- `grep -rn "WO2 runbook amendment" docs/` — does the amendment the row names even exist?
- Reconstruct the `_v3` lane duration from `git log --format="%ci %s"` over `3a75a77..8b2b021`;
  is it inside a 24 h same-boot horizon with margin, or does it consume most of it?
- The `_v3` freeze consumed S4 evidence with a hard expiry (`~2026-08-20T16:51Z`, `RUN_STATE.md:211`).
  On a window day, would the lane fit *inside* the horizon, or did it only fit because S4 had been
  authored a day earlier?
- Ask why a *production* re-freeze was accepted in place of the *rehearsal* the row ordered.

---

## ED-QUAL-L1-1 — same-boot production replay of the freeze chain

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:178`
> - [L1] ED-QUAL-L1-1 (stable capability, before the sitting): same-boot production replay of the freeze chain — run scripts/generate_arm_readiness.py verify against each pack's freeze receipt and scripts/project_identity_pins.py verify with the real model bytes on the production Mac (boot session da90818c-9c31-45d0-8813-deae65fba143). The sandbox cannot discharge this: model bytes are absent, so U11 refuses readiness_identity_artifact_unreadable (observed, fail-closed).

### (b) What changed since 2026-08-15
- **Boot session is unchanged.** `da90818c-9c31-45d0-8813-deae65fba143` is still the live boot
  (`RUN_STATE.md:211`, `WINDOW_STATUS.md:4`, `ed-s5-mint-decision-2026-08-19.md:42`); L6's own
  F2-live check at council time recorded it as current (`seat-reports/L6-SEAM-READER-A-report.md:67`).
- **(ii) PARTLY PERFORMED, with the wrong verbs.** On the production Mac at
  `/Users/edr/JouleWise-measurement-20260818`: `project_identity_pins.py **freeze**` ×3 ran with
  real model bytes (two tool refusals first — "missing MLX runtime under the system interpreter;
  build residue dirtying the git anchor — both diagnosed read-only, causes removed, then clean",
  `docs/run_reports/2026-08-19-t12-t13-session.md:55-60`), commits `3d05982`, `6fd8bce`, `74632e3`;
  and `generate_arm_readiness.py **freeze**` ×3 PASS, commits `5e38f1e`, `eb7f6c6`, `94dc3b3`.
  Branch-only.
- **GAP:** the row asks for `verify` against each pack's *existing* freeze receipt, and
  `project_identity_pins.py verify`. Assembler found no record of either `verify` subcommand being
  run on the production Mac. The T10 trace records `_load_freeze_reference VERIFIED authenticating
  there end-to-end` (`2026-08-18-t10-t11-working-notes/trace-notes.md:~318`) for the `_v2` round —
  that is the closest thing, and it is a library-level check reported in a note, not a CLI receipt.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** The seat is adjudicating whether mint-time authentication on the production
Mac substitutes for the standalone `verify` replay the row names, and whether the `_v2`-era
`_load_freeze_reference` note is admissible for a `_v3` pack family.

### (d) Skeptical probes
- Run it now, on the machine: `python3 scripts/generate_arm_readiness.py verify --pack-root <each _v3>`
  and `python3 scripts/project_identity_pins.py verify <each _v3>` — do all three PASS same-boot?
- `git log --all --format=%s | grep -i "verify"` — is there a verify receipt anywhere?
- Does `freeze` actually exercise the same authentication code path as `verify`, or a shorter one?
  Read `scripts/generate_arm_readiness.py` and say which checks `verify` runs that `freeze` does not.
- The row names the *sandbox* refusal `readiness_identity_artifact_unreadable` as the negative
  control. Was the positive side ever observed, or only the absence of a refusal?

---

## ED-QUAL-L1-2 — re-author pack-side freeze evidence on the production machine

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:179`
> - [L1] ED-QUAL-L1-2 (stable capability, after the B1 disposition is ruled): re-author the pack-side freeze evidence (scripts/author_arm_readiness_evidence.py), reissue freeze receipts, update plan-tree pins, and recommit on the production machine — must run there because evidence receipts derive kern.bootsessionuuid and monotonic time from the arming host; any reboot decision is Ed's.

### (b) What changed since 2026-08-15
- **(ii) PERFORMED, TWICE, ON THE PRODUCTION MACHINE.**
  - `_v2` round (T10, 2026-08-18): three `freeze-0002` receipts PASS minted at
    `/Users/edr/JouleWise-measurement-20260818` after the path-binding catch reverted the
    scratchpad-bound mints (`98265d4`); digests in `ed-morning-packet-2026-08-18.md:93-97`. On main.
  - `_v3` round (T12/T13, 2026-08-19): S4 D-134 evidence authored ×3 at the measurement checkout,
    **33 receipts, all PASS**, `3a75a77`; U11 plan-tree pins `3d05982`/`6fd8bce`/`74632e3`;
    `freeze-0003` ×3 PASS `5e38f1e`/`eb7f6c6`/`94dc3b3`; confirmation table complete at `8b2b021`
    (`docs/process/ed-s5-mint-decision-2026-08-19.md:71-85`). **Branch-only.**
  - Receipts are committed and readable in-tree, e.g.
    `configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`
    (+ `.sha256`). All `_v3` evidence receipts carry `boot_session_id: da90818c-…`.
- Landing discipline honoured: "landed by pull-from-measurement-checkout"
  (`docs/run_reports/2026-08-19-t12-t13-session.md:60`).

### (c) Candidate disposition for the seat
**ED-ROW-CLOSED — evidence: `freeze-0003.json` ×3 + U11 projections, minted at
`/Users/edr/JouleWise-measurement-20260818`, commits `3d05982`, `6fd8bce`, `74632e3`, `5e38f1e`,
`eb7f6c6`, `94dc3b3`, table `8b2b021`, all BRANCH-ONLY on `impl/r2-s0-mint-resolver`.**
The seat is adjudicating (1) whether branch-only evidence satisfies a clearance rule, and (2) that
the row's precondition "after the B1 disposition is ruled" was in fact satisfied before execution.

### (d) Skeptical probes
- Verify each receipt in-tree binds the absolute `pack_root` `/Users/edr/JouleWise-measurement-20260818/…`
  — the T10 path-binding defect was exactly this, and it voided a whole freeze wave once.
- `git merge-base --is-ancestor 5e38f1e main` → **NO**. Does the council accept evidence that
  disappears if the branch is not merged?
- Cross-check the three predecessor triples in `freeze-0003.json` against the `freeze-0002` shas
  in `ed-morning-packet-2026-08-18.md:93-97` byte-for-byte.
- The row names `scripts/author_arm_readiness_evidence.py`; S4 used the T0/D-134 author path.
  Same tool, or a different one with a different provenance surface?

---

## ED-QUAL-L5-1 — non-window rehearsal of the t0 clock-attestation input handshake

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:180`
> - [L5] ED-QUAL-L5-1 (stable capability, any tap block): one non-window rehearsal of the t0 clock-attestation input handshake — Ed captures real `sudo systemsetup -getusingnetworktime` / `-setusingnetworktime off` outputs per runbook E-4/E-5 into a scratch arm_readiness.t0.inputs namespace and the lead validates them against the t0 author's capture validators (joulewise/arm_readiness_evidence_t0.py:838-861 _systemsetup_argv / _derive_clock_attestation). The authored tests use synthetic captures only; the first real sudo-output shape mismatch must not surface at T-0.

### (b) What changed since 2026-08-15
- **(ii) REAL OUTPUTS CAPTURED — but outside the namespace and without the validation step.**
  Ed's evening captured both clock vectors with ground-truth state flips:
  `sudoers-vector-{on,off}.txt`, `vector-{on,off}-confirmed.txt`, `clock-{prior,post}-state.txt`
  (`docs/run_reports/2026-08-18-t10-session.md:106`) — **off-repo**, `~/JouleWise-window-custody/ed-qual-20260817/`.
  The shakedown driver then ran `sudo -n /usr/sbin/systemsetup -setusingnetworktime off|on` live
  (`docs/process_traces/2026-08-18-t10-t11-working-notes/shakedown-driver.sh:20-21,32-34,70-72`).
- **GAP 1:** nothing was captured into an `arm_readiness.t0.inputs` namespace via
  `scripts/capture_t0_step.py`; the shapes were never run through the real capture writer.
- **GAP 2:** no record of the lead validating those outputs against `_systemsetup_argv` /
  `_derive_clock_attestation` (now at `joulewise/arm_readiness_evidence_t0.py:845-888`, shifted
  from the cited :838-861). The very shape-mismatch risk the row exists to retire is untested.
- **GAP 3 (material):** the shakedown driver *worked around* the `-getusingnetworktime` read
  entirely — `"prior_state=On (operator qualification record ed-qual-20260817/clock-post-state.txt)"`
  (`shakedown-driver.sh:32`) with the comment "the get vector is deliberately not NOPASSWD". The
  real read shape was therefore never fed to the validator. See ED-Q-L8-1.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** The seat is adjudicating whether raw captured sudo outputs sitting in off-repo
custody, never passed through `capture_t0_step.py` and never checked against the author's
validators, discharge a row whose whole purpose is to surface a shape mismatch before T-0.

### (d) Skeptical probes
- Take `~/JouleWise-window-custody/ed-qual-20260817/clock-prior-state.txt` and run it through
  `_derive_clock_attestation`'s regex `r"Network Time:\s*(On|Off)\s*$"` — does it match?
- `_derive_clock_attestation` refuses unless `prior["argv"] == _INTERACTIVE_PRIOR_STATE_ARGV`
  (`:862-863`, the literal `["operator-interactive","network-time-prior-state"]` at `:143`).
  Ed's captures used real sudo argv. Would they be *rejected* by the author?
- The row cites `:838-861`; the functions now live at `:845-888`. What else moved in that file
  since the council, and was any validator semantics changed?
- Ask for the artifact that records the lead performing the validation. If none exists, the row's
  second half was never done by anyone.

---

## EDQ-L2-1 — crash matrix to completion on the quiet bench

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:181`
> - [L2] EDQ-L2-1 (stable capability): execute tests.test_calibration_writer_crash_matrix to completion on the quiet bench at the audit-baseline head and record pass + wall time. On the audited host it cannot complete (finding L2-1); CI exclusive-job green at the baseline head corroborates but a bench execution closes the row with local evidence.

### (b) What changed since 2026-08-15
- **(ii) EXECUTED TO COMPLETION ON THE QUIET BENCH, and the log is IN THE REPO.**
  `docs/process_traces/2026-08-18-freeze-semantics-coldgate/verification-logs/crash-matrix-quiet-20260818-0110PT.log`
  (commit `3f9d759`, **on main**). Tail: `Ran 15 tests in 535.763s` / `OK`. Pass + wall time recorded.
- WO-DETECT-PULSES-BUDGET's `test_detection_budget_refuses_with_terminal_custody_and_released_lease`
  is present in the run, so the module is the post-council version.
- **GAP 1:** the row says **at the audit-baseline head** (`8937dec`/manifest `ac3fe1d`). This ran at
  the 2026-08-18 freeze-semantics-coldgate head on the transaction branch — a different head, and
  many pack/estimator commits later.
- **GAP 2:** the row and `sitting-packet-FINAL.md §6` both say **16 tests**; the log shows **15**.
  Nothing in the record explains the missing test.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL — evidence: `.../verification-logs/crash-matrix-quiet-20260818-0110PT.log` (`3f9d759`, on main),
15 tests / 535.763 s / OK.** The seat is adjudicating whether a completed quiet-bench run at a
*later* head with a *smaller* test count closes a row scoped to the audit-baseline head's 16-test module.

### (d) Skeptical probes
- `git show 8937dec:tests/test_calibration_writer_crash_matrix.py | grep -c "def test_"` vs the
  current file — which test disappeared, and was it the degenerate-cost case that caused L2-1?
- If the degenerate case was *removed* rather than fixed, the row's underlying finding (L2-1) is
  masked, not cured. Check `git log -p --follow tests/test_calibration_writer_crash_matrix.py` since 2026-08-15.
- 535.763 s here vs the §6 note of 5,317 s for the CI-exclusive module. A 10× gap needs explaining —
  different machine, or different work?
- Was the bench genuinely quiet at 01:10 PT on 2026-08-18? The T10 session had fleets running
  through the night (`t10-session.md`, "the loop ran unattended from ~18:45").

---

## EDQ-L2-2 — SS5C lead live verification on the production checkout

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:182`
> - [L2] EDQ-L2-2 (stable capability; runbook-mandated non-delegable): the SS5C lead live verification on the exact reviewed measurement checkout — frozen plan's literal readiness-validator command plus the complete under-lease synthetic rehearsal (real reservation CLI --execute + production writer lifecycle through BOTH slots against a synthetic root), requiring the D-134 dry-run receipt PASS/NOT_APPLICABLE with the reviewed HEAD + committed-pack digest. This audit replayed the equivalent in scratch; the runbook requires it on the production checkout with the frozen plan, which no sandboxed seat can perform.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND / not performed.** The only D-134 dry-run receipt in existence remains
  `dry-run-0001`, generated **2026-08-13 at `49dcc49`**
  (`docs/process_traces/2026-08-13-freeze-execution/dryrun-alpha.json`, on main; receipt itself at
  `~/JouleWise-window-custody/d117_floor_qwen25_1p5b_v1/arm_readiness.dry_run.receipts/dry-run-0001.json`).
- The repo's own status doc says so: `docs/phase_2/alpha_arm_readiness.md:125` —
  "`desk.under_lease_rehearsal` | **PRIOR PASS ONLY.** `dry-run-0001` passed at `49dcc49`; the
  council-ordered full dress rehearsal against the successor pack remains pending and cannot itself
  authorize arming."
- Head-staleness is now severe: `49dcc49` predates PR #152, the `_v2` family, D-143's re-supersession,
  and the entire D-146/D-147 `_v3`/`freeze-0003` transaction. The receipt binds a `_v1` pack.
- Searched: `find . -iname "*dry-run*" -o -iname "*dryrun*"` → one hit, the 2026-08-13 file.

### (c) Candidate disposition for the seat
**ED-ROW-OPEN.** Explicitly "runbook-mandated non-delegable". The seat is adjudicating a row with
zero post-council evidence, whose only prior artifact binds a pack family that has been superseded twice.

### (d) Skeptical probes
- `grep -rn "under_lease_rehearsal" docs/phase_2/*_arm_readiness.md` — all three packs still say
  PRIOR PASS / pending. Does any of them claim otherwise?
- Does `reserve_calibration_window_bracket.py --execute` even run against the `_v3` FROZEN_PLAN
  identity after the D-147 S0 resolver rewrite? (R2 identity was itself a Phase-0 ruling.)
- The row requires "BOTH slots". Confirm the production writer lifecycle has two slots in the
  current code, and that a rehearsal would exercise both.
- Ask who is on the hook: the row says non-delegable *lead* verification, not Ed. Was it dropped
  because it fell between the Ed batch and the lead's queue?

---

## ED-L3-1 — live sudo/powermetrics sampler checklist

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:183`
> - [L3] ED-L3-1 (stable): Live sudo/powermetrics checklist — run scripts/ed_session/sampler-checklist.sh (sudo -n grant, empty pre-census, supervised 5-sample capture under _sampler_lifetime, empty post-teardown census, cadence record, parse by the pinned parser). This is the long-owed row gating reliance on #127's production sampler commit (RUN_STATE 'ED-OWED' item 3). Close only after WO-L3-2/WO-L3-3 fix the checklist's documented home and add the 100 ms leg.

### (b) What changed since 2026-08-15
- **(ii) EXECUTED.** `docs/run_reports/2026-08-18-t10-session.md:107`: "Sampler lifecycle
  (ED-QUAL step 2) | PASS — cadence mean **1.0128 s**, zero orphans |
  `ed-session-evidence/sampler-checklist-*.log` (3 runs + plist)". Off-repo custody.
- **Repo-side corroboration that the run really happened:** it flushed two real script defects,
  fixed on main the same evening — `d873f77` "guard empty-args re-exec against macOS bash 3.2
  set -u" (18:06) and `e5dc38a` "probe command-scoped sudo authorization, not blanket sudo -n true"
  (18:18). Both verified present on main.
- **THE ROW'S OWN CLOSURE PRECONDITION IS UNMET.** "Close only after WO-L3-2/WO-L3-3…":
  - `grep -rn "WO-L3-2\|WO-L3-3" .` returns hits **only** inside
    `docs/process_traces/2026-08-15-readiness-council/triage.json:284-285` and the L3 seat report.
    Neither WO ever entered `TASK_QUEUE.md` or `docs/process/state_kernel.json`.
  - **100 ms leg absent:** `scripts/ed_session/sampler-checklist.sh:59` still runs
    `powermetrics -b 0 -i 1000 -n 5` — 1 Hz. Production binds 100 ms.
  - **Documented home still wrong:** `docs/phase_2/ed-qualification-session.md` Step 2 still says
    the items "live in the sampler module docstring" and points at `/tmp/ed-session/sampler-checklist.sh`.
  - `git log -- scripts/ed_session/` since the council shows only `d873f77`, `e5dc38a`, `ad14ac4` —
    no WO-L3-2/-3 work.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** The seat is adjudicating a row that was *executed* but whose text forbids
closure until two work orders land — and those two work orders were never even registered in the
queue, so the cadence evidence stands at 1 Hz against a 100 ms production binding.

### (d) Skeptical probes
- `sed -n '55,65p' scripts/ed_session/sampler-checklist.sh` — confirm `-i 1000` is still there.
- `grep -n "WO-L3-2" TASK_QUEUE.md docs/process/state_kernel.json` → no hits. Ask how two council
  work orders vanished between `triage.json` and the queue, and whether others did too.
- Cadence mean 1.0128 s at 1 Hz says nothing about realized interval at 100 ms, where scheduler
  jitter is 10× more consequential. Is there any 100 ms cadence observation anywhere?
- The row requires "empty pre-census" and "empty post-teardown census". Does
  `ed-session-evidence/sampler-checklist-*.log` actually show both empty, or only the orphan count?

---

## ED-L3-2 — live SIGTERM-relay termination

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:184`
> - [L3] ED-L3-2 (stable): Live SIGTERM-relay termination — confirm on the current OS build that `sudo -n powermetrics` exits within the 10 s grace on SIGTERM to sudo (normal path) ; the executed falsifier F-B shows that if it ever does not, the SIGKILL escalation strands a root orphan no software census on the measured-run path detects. One observation, any tap block.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** Searched: `grep -rn -i "SIGTERM" docs/process/ docs/run_reports/ RUN_STATE.md`
  — every hit is from July sessions (`2026-07-10`, `2026-07-11`, `2026-07-12`, `2026-08-09`); none
  from the 2026-08-17/18 qualification evening or the shakedown.
- The council's Ed-required list **named** "SIGTERM relay"
  (`council-verdict.md:92`), but `docs/process/ed-evening-checklist.md` — the ordered list Ed
  actually worked — **does not contain it**: its item 4 is "Sampler checklist + rail probe +
  keyboard-backlight rows". The row was dropped between the verdict and the operator checklist.
- The T10 qualification table (`t10-session.md:104-116`) has no SIGTERM row.

### (c) Candidate disposition for the seat
**ED-ROW-OPEN.** One observation, ~1 minute of machine time, never taken. The seat is also
adjudicating a *checklist-authorship* failure: a council-named item silently absent from the
operator's ordered list.

### (d) Skeptical probes
- Run it now: `sudo -n powermetrics … & ; kill -TERM <sudo pid>` and time the child's exit against
  the 10 s grace. Any tap block; no window needed.
- The sampler-checklist run reported "zero orphans" — does that path go through SIGTERM-to-sudo, or
  does the supervisor kill the child directly? Read `_sampler_lifetime` teardown and say which.
- If the checklist *does* exercise the relay, why did the L3 seat emit ED-L3-2 as a separate row
  from ED-L3-1?
- Diff `council-verdict.md:89-96` against `docs/process/ed-evening-checklist.md` item by item —
  what else was dropped? (Assembler finds SIGTERM relay and the production-machine freeze-chain
  replays both missing from the evening list.)

---

## ED-L3-3 — JW-MET-3 rail probe

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:185`
> - [L3] ED-L3-3 (stable): JW-MET-3 rail probe — scripts/ed_session/rail-probe.sh ABBA keyboard-backlight arms with --samplers battery,cpu_power,gpu_power,ane_power,thermal; documentation-grade rail-inclusion differential (the LED-outside-boundary verdict already stands on code evidence).

### (b) What changed since 2026-08-15
- **(ii) EXECUTED.** `docs/run_reports/2026-08-18-t10-session.md:108`: "ABBA executed; **ANE delta
  exactly 0.000000000 J**; cpu delta **−5.7 J** attributed to concurrent replay load +
  charge-termination step. **Documentation-grade**; the boundary verdict (LED outside cpu+gpu+ane)
  stands on code evidence | `rail-probe-load-note.txt` (lead-restored after the operator's own
  paste overwrote it)". Off-repo custody.
- **CONTAMINATION, ON THE RECORD:** the ABBA arms ran **under concurrent decisive-replay load and
  a charge-to-full transition** — the differential is negative on cpu, i.e. the measurement is
  confounded, and the report itself says the boundary verdict rests on *code* evidence, not on this probe.
- **CUSTODY ANOMALY, ON THE RECORD:** the evidence file was "lead-restored after the operator's own
  paste overwrote it" — the primary artifact was destroyed and reconstructed.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** The seat is adjudicating whether a documentation-grade probe executed under
acknowledged contamination, whose evidence file was overwritten and reconstructed by the lead,
counts as "closed with evidence".

### (d) Skeptical probes
- Read `rail-probe-load-note.txt` and establish what is *original operator output* vs *lead
  reconstruction*. A reconstructed artifact is lead testimony, not operator evidence.
- A negative cpu delta across an ABBA whose only intended variable is the LED means the design's
  A/B isolation failed. Should the probe simply be re-run on a genuinely quiet machine (~7 min)?
- `scripts/ed_session/rail-probe.sh` was read "for role, not line-audited" by L3 (§6). Has anyone
  line-audited it since? `git log -- scripts/ed_session/rail-probe.sh` shows no post-council edits
  beyond `d873f77`/`e5dc38a`.
- ANE delta "exactly 0.000000000 J" across both arms — is that a real null or an unpopulated field?

---

## ED-L3-4 — channel-census currency on the arm build

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:186`
> - [L3] ED-L3-4 (stable, largely co-closed by ED-L3-1): Channel-census currency on the arm build — one live capture parsed by the pinned parser with hw_model/kern_osversion recorded and matched against the runbook's Mac15,9 / macOS 25F84 bindings; REOPENS on any OS update before the window (the parser is pinned to the Slice-2H fixture format; a format/unit change fails closed on rails but silently on units only if Apple kept mW fields parseable — currency is an empirical row, not a test-provable one).

### (b) What changed since 2026-08-15
- **Live captures exist** (both off-repo): the sampler-checklist plist (2026-08-17) and the
  shakedown's 600×1 s idle plist plus a 97 MB corpus-grade calibration bundle (2026-08-18,
  `~/JouleWise-window-custody/shakedown-20260818/`), the latter parsed successfully by the
  production pipeline and re-derived in-band (`b_fiducial=0.030878 s`).
- **GAP — the row's actual deliverable is missing.** `grep -rn "25F84\|Mac15,9\|kern_osversion\|hw_model"`
  across `docs/run_reports/2026-08-18-t10-session.md`, `docs/process_traces/2026-08-18-shakedown-first-light/`,
  `docs/process_traces/2026-08-18-t10-t11-working-notes/` returns **nothing**. The only hit in the
  whole repo is `docs/phase_2/window_runbook.md:703` ("valid only for Mac15,9 / macOS 25F84 /").
  No recorded match of a live capture's `hw_model`/`kern_osversion` against those bindings exists.
- The row also **REOPENS on any OS update before the window** — no OS-version watch is recorded anywhere.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** The seat is adjudicating whether successful parsing of a live capture implies
currency, when the row's deliverable is an explicit recorded binding of `hw_model`/`kern_osversion`
against `Mac15,9 / macOS 25F84` — which does not exist — and whether any mechanism reopens the row
on an OS update.

### (d) Skeptical probes
- `plutil -p ~/JouleWise-window-custody/shakedown-20260818/quiet-state-baseline/powermetrics_idle_baseline.plist | head`
  — do `hw_model`/`kern_osversion` appear, and do they equal `Mac15,9` / `25F84`?
- `sw_vers` and `sysctl hw.model` on the machine right now — has the OS moved since 2026-08-18?
- The row warns the parser fails closed on rails but **silently on units**. Is there any unit
  assertion (mW vs W) in the pinned parser, or only field presence?
- What mechanically reopens this row on an OS update — a test, a preflight check, or nothing?

---

## ED-L7-1 — prewindow_check.sh --wait to READY + quiet_mac_prep.sh

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:187`
> - [L7] ED-L7-1: prewindow_check.sh --wait to READY plus quiet_mac_prep.sh on the freed quiet machine (stable capability; my execution proves the gate correctly BLOCKS while any agent fleet runs, so READY can only be demonstrated in an Ed/quiet block)

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND / (i) mechanism only.** `capture_t0_step.py prewindow-check` appears in the
  rehearsal card (`docs/process/rehearsal-operator-card.md:69-74`, section "7. E-7b prewindow-check
  — ED-FIRST") and in the builder brief (`rehearsal-builder-brief.md:93`) — both are *cards*, and
  the rehearsal never ran.
- No execution log: `grep -rn "prewindow_check\|prewindow-check" docs/run_reports/ docs/process/ RUN_STATE.md`
  returns only the card, the brief, a 2026-08-13 note, and a trace line about a v1 runs-prefix.
- `quiet_mac_prep.sh` was likewise never run — see ED-Q-L8-4.
- Note the shakedown deliberately bypassed both: `shakedown-driver.sh:44` uses a bare
  `pmset displaysleepnow`, not `quiet_mac_prep.sh`.

### (c) Candidate disposition for the seat
**ED-ROW-OPEN.** The row exists precisely because READY can only be shown in a quiet block; no
quiet block has demonstrated it.

### (d) Skeptical probes
- Run `scripts/prewindow_check.sh --wait` in a quiet block and capture the READY transition —
  minutes of work, no sudo beyond what is installed.
- L8-B2 (`sitting-packet-FINAL.md:89`) says "The frozen E-7b command cannot prove the ≥10-minute
  idle the author enforces". Was that blocker repaired? If not, ED-L7-1 may be unpassable as written.
- Does D-148.4/D-149's no-hands delegation make this a *lead* row now? If so, why has the lead not
  run it — it needs no hands.
- Check for stale `caffeinate`/agent processes that would keep the gate BLOCKED and make a READY
  observation impossible without a real fleet stand-down.

---

## ED-L7-2 — fresh §5C lead dry-run PASS at the final reviewed head

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:188`
> - [L7] ED-L7-2: fresh §5C lead dry-run PASS at the final reviewed head on the measurement checkout — executes the real reservation CLI --execute and the production ledger-writer lifecycle through both slots under lease (the recorded dry-run-0001 is head-stale after any checkout advance; a new PASS receipt binding the final head/digest is required desk evidence before arm)

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** Identical evidence position to EDQ-L2-2: the only receipt is `dry-run-0001`
  @ `49dcc49` (2026-08-13). The head has advanced by the whole Phase-1 merge wave (#150/#151/#152),
  the `_v2` family, D-143's re-supersession, and the entire `_v3`/`freeze-0003` transaction.
- `docs/phase_2/alpha_arm_readiness.md:102` — "`desk.arming_procedure` | **PRIOR PASS; successor
  recheck required.** The old receipt and dry run passed, but #152 changed the runbook/T-0 route and
  the new exact-head rehearsal is pending."
- The row's own trigger condition ("head-stale after any checkout advance") has fired many times over.

### (c) Candidate disposition for the seat
**ED-ROW-OPEN.** The seat is adjudicating required desk evidence that does not exist for any head
in the last six days, on a row whose text calls it "required desk evidence before arm".

### (d) Skeptical probes
- Note the ordering trap: this receipt must bind the **final reviewed head**. If the merge wave
  (`impl/r2-s0-mint-resolver` → `integration/phase2-transaction` → `main`) runs after the dry-run,
  the receipt is stale again. Ask the council to fix the sequencing explicitly.
- `git log --oneline 49dcc49..HEAD | wc -l` — how stale is `dry-run-0001` in commits?
- The receipt must also bind the **committed-pack digest**. `_v1` digests are three generations old.
- Does the dry-run generator even accept a `_v3` pack after the D-147 S0 resolver rewrite? If it
  refuses, this row is blocked on code, not on scheduling.

---

## ED-L7-3 — live sudo powermetrics fiducial calibration seam

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:189`
> - [L7] ED-L7-3: live sudo powermetrics fiducial calibration seam (validate_powermetrics_fiducial --allow-live producing instrument_evidence.json consumed by the chain's §5B jq screen) — unexercisable without sudo + quiet machine; covered by the charter's sampler checklist but named here because it is the one producer->consumer edge in the §6 chain I could not execute or observe in any test

### (b) What changed since 2026-08-15
- **(ii) THE PRODUCER HALF RAN LIVE.** The D-139 shakedown executed exactly this CLI on the real
  machine under Ed's D-142 standing night license:
  `"$CLONE/.venv/bin/python" "$CLONE/scripts/validate_powermetrics_fiducial.py" --allow-live
  --power-policy ac_high_power --output-root "$CUST/runs/instrument_validation"`
  (`docs/process_traces/2026-08-18-t10-t11-working-notes/shakedown-driver.sh:60-72`).
  Custody: `~/JouleWise-window-custody/shakedown-20260818/` (off-repo). Trace:
  `trace-notes.md:330-345`; decisions D-142, D-143.
- Outcome, honestly: **run 1** bundle refused `calibration_reservation_head_mismatch`; **run 2**
  bundle 1 CAPTURED corpus-grade (97 MB, SNR ~43k, no gaps) but **evaluated invalid —
  `detection_nonconvergent`, cell budget 100,000 exhausted**. The in-band result
  (`b_fiducial=0.030878 s ∈ [0.022741, 0.033559]`, 59/59) came from an **offline re-derivation**
  under the corrected 165k budget (D-143), not from a passing live run.
- **GAP 1:** run against an **isolated clone ledger** (`shakedown-driver.sh:9-11`, "the canonical
  calibration ledger is never touched"), not the production ledger the seam consumes.
- **GAP 2:** the row's actual subject is the **producer→consumer edge** — `instrument_evidence.json`
  consumed by the chain's §5B jq screen. No record anywhere of the §5B screen consuming a live
  `instrument_evidence.json`. The edge remains unobserved.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** The seat is adjudicating whether a live producer run — against a clone ledger,
whose first evaluation failed closed and whose in-band number came from an offline re-derivation —
discharges a row explicitly scoped to the unobserved producer→consumer edge.

### (d) Skeptical probes
- `ls ~/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/` — does an
  `instrument_evidence.json` actually exist, and was it ever fed to the §5B jq screen?
- Locate the §5B jq screen in `docs/phase_2/window_runbook.md` and run it against that file. Does
  it pass, or does it need fields the live producer did not emit?
- The bundle was captured under the **100k** budget and re-derived under **165k**. Would a fresh
  live run under 165k reproduce in-band, or was the re-derivation fit to the answer? (D-143 claims
  the budget came from a complete n=34 corpus sweep, not from tuning — verify that claim's log.)
- Clone-ledger isolation means the reservation/finalization path against the *production* ledger
  was never exercised live. Is that path part of this seam?

---

## ED-L10-1 — desk replay of the post-collection chain against a9/a10

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:190`
> - [L10] ED-L10-1 (stable capability, any tap block, no live measurement): one desk replay of the complete post-collection chain against a RETAINED real window corpus (a9/a10 custody, Ed-held off-repo) — whole-window verdict (expect passed), duration-margins recorder, backup, governed extraction with the matching spec and basis sha — pasting every command and exit code. This supplies the CLI-level PASSED-basis positive proof that no sandboxed desk rehearsal can produce, because a passing basis requires real calibration-bracket, NEG-8 corpus, and reference-triplet evidence that only a live sudo/powermetrics window can mint.

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** `grep -rn "a9/a10" docs/ RUN_STATE.md TASK_QUEUE.md` (excluding the council
  directory) returns only historical references: `council_log.md:79` (C-046, July), the July iCloud
  prune report, plan-factory drafts, and the *forward-looking* mentions in
  `docs/run_reports/2026-08-15-t8-session.md:338`, `2026-08-16-t9-session.md:497`,
  `docs/process/ed-batch-packet.md:57`, `docs/process/ed-evening-checklist.md:24` — all of which
  list the replay as OWED, none as done.
- The T10 qualification table has no a9/a10 row. The morning packet's §5 ledger does not list it.
  It appears on the evening checklist as item 5 ("desk items, can run while other captures settle")
  and simply never produced an artifact.
- This is the **only** source of CLI-level PASSED-basis positive proof named anywhere in the packet.

### (c) Candidate disposition for the seat
**ED-ROW-OPEN.** The seat is adjudicating the absence of the one piece of evidence the L10 seat
identified as impossible to obtain any other way — and it needs no sudo and no window, only Ed's
retained corpus.

### (d) Skeptical probes
- Does the a9/a10 corpus still exist and verify? (`docs/run_reports/2026-07-28-icloud-archive-prune.md`
  documents parity checks; §6 L11 notes iCloud mirror parity was "layout and existence checked only".)
- Would a9/a10 even pass the **D-146 claim barrier**? D-148.7 registered the 748-bundle anchor-v2
  population as permanently non-claim-bearing, mechanically enforced by `capture_pipeline_superseded`.
  If a9/a10 are anchor-v2-era, this replay may now be *impossible to pass* — which would change the
  row from "not done" to "cannot be done", a materially different verdict.
- If the row is unpassable, what replaces the CLI-level PASSED-basis proof before a claim window?
- `grep -rn "PASSED-basis\|passed basis" docs/` — has anyone else supplied it?

---

## ED-QUAL-L4-1 — decisive replay (network)

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:191`
> - [L4] ED-QUAL-L4-1 (network capability, not hardware/sudo — emitted so it is not silently skipped): execute scripts/replay_d117_decisive.sh at the audited head in any tap block with network — anonymous release download, digest gate, governed hydration, census byte-compare, then the single decisive no-skip mint test (~3h35m on the M3 Max). Stable evidence; closes the two skipped decisive tests and the full-fixture leg of the mint's exact-equality proof.

### (b) What changed since 2026-08-15
- **(ii) EXECUTED AND PASSED.** `docs/run_reports/2026-08-18-t10-session.md:109`: "**`DECISIVE
  REPLAY: OK`** — full chain (download, digest, hydration, census byte-compare, decisive no-skip
  mint), 23 proof selections, **13,180.653 s** total | `decisive-replay.log`". Off-repo custody;
  three attempts, third clean (`trace-notes.md:189` "ED-QUAL-L4-1 CLOSED (2026-08-17 ~22:05 PT)").
- **Strong repo-side corroboration** — the run flushed two defects and produced a guard test, all
  merged to main and verified present:
  - `724ea28` (18:10) "decisive-test repair: import STACK_IDENTITY_DOMAIN from its post-#131 home" —
    a drift the CI-excluded decisive leg could not see;
  - `1500265` (18:21) "qualification-catch hardening: replay script requires an explicit external
    work dir; fast CI guard resolves decisive-test module references", which added
    `tests/test_decisive_reference_resolution.py`.
  These commits are unforgeable evidence that the replay really ran and really failed twice first.
- **CAVEAT:** run at the `1500265`-era head (2026-08-17). Since then: D-143's estimator budget
  ruling, D-079 r4→r5→r6 reissues, S2 goldens re-derived against r6, and the entire `_v3` family.
  The row says "at the audited head"; that head is now two acceptance generations behind.

### (c) Candidate disposition for the seat
**ED-ROW-CLOSED — evidence: `DECISIVE REPLAY: OK`, 13,180.653 s, `~/JouleWise-window-custody/ed-qual-20260817/decisive-replay.log`,
corroborated in-repo by `724ea28`, `1500265`, `tests/test_decisive_reference_resolution.py` (all on main).**
The seat is adjudicating whether a PASS at the 2026-08-17 head survives the r5/r6 acceptance
reissues and the `_v3` family, or must be re-run at the final reviewed head.

### (d) Skeptical probes
- Re-run cost is ~3h40m and needs only network. Is a re-run at the final reviewed head cheaper than
  arguing the PASS still holds?
- Did the r6 goldens re-derivation (`S2`) touch anything the decisive test compares byte-for-byte?
  `docs/process_traces/2026-08-19-refreeze-execution/reports/S2-goldens-report.md`.
- The decisive leg is **CI-excluded** — so nothing has re-tested it since 2026-08-17. Confirm:
  `grep -n "decisive" .github/workflows/ci.yml`.
- Read `decisive-replay.log`'s final lines directly; "OK" in a run report is lead testimony.

---

## ED-Q-L9-1 — JW-MET-2 System Settings keyboard-backlight census

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:192`
> - [L9] ED-Q-L9-1 (staged): JW-MET-2 System Settings keyboard-backlight census — level 0, auto-adjust off, inactivity Never, verification=operator_visual (ed-qualification-session.md step 4; no CLI exists for the level, operator visual is the only probe)

### (b) What changed since 2026-08-15
- **(ii) PERFORMED.** `docs/run_reports/2026-08-18-t10-session.md:108` (row "Backlight rows"):
  "level 0 / auto-adjust off / inactivity never, `operator_visual` | `keyboard-backlight.txt`
  (18:00:42)". Confirmed in `ed-morning-packet-2026-08-18.md:118`. Off-repo custody
  `~/JouleWise-window-custody/ed-qual-20260817/keyboard-backlight.txt`.
- All three required states recorded, with the required `verification=operator_visual` marker and a
  timestamp. This is the cleanest match between a row's text and its evidence in the whole set.
- **CAVEAT:** it is a mutable OS setting captured on 2026-08-17. Nothing re-verifies it at T-0, and
  the row's own note says no CLI probe exists for the level.

### (c) Candidate disposition for the seat
**ED-ROW-CLOSED — evidence: `~/JouleWise-window-custody/ed-qual-20260817/keyboard-backlight.txt`,
2026-08-17 18:00:42, level 0 / auto-adjust off / inactivity Never, `verification=operator_visual`.**
The seat is adjudicating whether an off-repo operator-visual attestation of mutable OS settings,
with no T-0 re-verification path, is durable evidence.

### (d) Skeptical probes
- Read `keyboard-backlight.txt` and confirm all three literals plus the operator_visual marker are
  present in the file, not only in the run report's paraphrase.
- Since no CLI exists for the level, what stops the setting drifting between 2026-08-17 and a window
  weeks later? Is there a T-0 checklist item, or is this a one-shot attestation?
- Was the machine's keyboard backlight physically at level 0 during the *rail probe*, whose ABBA
  arms deliberately drive it max/off? The probe ran the same evening — check ordering
  (`keyboard-backlight.txt` 18:00:42 vs the rail-probe arms).
- Does any window-day census assert backlight state, or only this one-time record?

---

## ED-Q-L9-2 — JW-MET-3 keyboard-backlight rail-inclusion differential probe

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:193`
> - [L9] ED-Q-L9-2 (staged): JW-MET-3 keyboard-backlight rail-inclusion differential probe — sudo powermetrics ABBA max/off arms (ed-qualification-session.md step 3; documentation-grade, boundary verdict already stands on code evidence)

### (b) What changed since 2026-08-15
- **Co-extensive with ED-L3-3** — the same single execution discharges both rows; L3 and L9 emitted
  it independently. Same evidence, same caveats: ABBA executed 2026-08-17; ANE delta exactly
  0.000000000 J; cpu delta −5.7 J under concurrent decisive-replay load and charge-termination;
  `rail-probe-load-note.txt` lead-restored after the operator's paste overwrote it
  (`docs/run_reports/2026-08-18-t10-session.md:108`). Off-repo.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** Same adjudication as ED-L3-3: contaminated arms, reconstructed artifact. The
seat should additionally note that two independent seats scored this probe important enough to emit
separately, which argues against writing off the contamination as "documentation-grade anyway".

### (d) Skeptical probes
- All ED-L3-3 probes apply. Additionally: does L9's framing require anything L3's did not —
  e.g. a specific census interaction — that the single run did not cover?
- If the boundary verdict "already stands on code evidence", what does a contaminated probe add?
  Ask what would change if it were struck rather than counted PARTIAL.
- ~7 minutes of quiet-machine time re-runs it clean. Why has it not been re-run in the two days since?

---

## ED-Q-L9-3 — quiet-state resident-process baseline (HARD-GATES WO-CENSUS-SEMANTICS)

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:194`
> - [L9] ED-Q-L9-3 (new, stable capability, no sudo): quiet-state resident-process baseline — with all fleets/agents closed on the real machine, capture the four PROCESS_CENSUS and one MAINTENANCE_CENSUS pgrep outputs and commit them as the regression fixture that the WO-L9-1/2 pattern fixes must pass against; this is the only way to prove the fixed censuses PASS in the state they will actually run in

### (b) What changed since 2026-08-15
- **(ii) CAPTURE HALF DONE.** `docs/run_reports/2026-08-18-t10-session.md:110`: "**Captured 23:51**
  by the lead with all agent runs quiesced; 7 resident Safari agents, `watchdogd`+`watchlistd`,
  19 maintenance daemons — the L8/L9 **over-match findings confirmed as fixture ground truth**;
  lead-session lines labeled | `quiet-census/` (6 files + `CAPTURE-NOTE.txt`)". Off-repo custody
  `~/JouleWise-window-custody/ed-qual-20260817/quiet-census/`.
  Also `trace-notes.md:276`. Note it was captured by the **lead**, not Ed.
- **(ii) COMMIT HALF NOT DONE — and this is load-bearing.** The row requires "commit them as the
  regression fixture". Repo-wide search finds no such fixture:
  `find . -iname "*quiet*"` → only quiet_guard/quiet_mac_prep code and one crash-matrix log;
  `find . -iname "*census*"` → only three `docs/process_traces/` directories, none a fixture.
- **The live queue still says the same thing.** `TASK_QUEUE.md:538` and `:632`:
  "A4 | WO-CENSUS-SEMANTICS | P1 Phase Gate | **BLOCKED — ED-Q-L9-3** (real quiet-state
  resident-process baseline fixture is captured with all fleets and agents closed)", with acceptance
  "**ED-Q-L9-3 real quiet-state fixture is committed before implementation**" and the fence
  "Do not weaken either census from synthetic or self-nominated evidence; ED-Q-L9-3 is a hard
  precondition". `docs/process/state_kernel.json:3125,3148,3158,3168` carry the same gate.
  `RUN_STATE.md:426`: "WO-CENSUS-SEMANTICS stays HARD-gated on ED-Q-L9-3."
- So: A4 remains BLOCKED, WO-L9-1/L9-2 pattern fixes remain unimplemented, and the two census
  blockers (L9-B2, L8's `t0.no_stray_keepawake` unpassability) remain live.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL — capture exists off-repo (`~/JouleWise-window-custody/ed-qual-20260817/quiet-census/`,
6 files + CAPTURE-NOTE.txt, 2026-08-17 23:51); the committed regression fixture the row demands
does not exist anywhere in the tree.** The seat is adjudicating the sharpest cascade in this file:
the row is unclosed, so A4 WO-CENSUS-SEMANTICS is still BLOCKED, so the census blockers that made
L9 and L8 NOT-READY are still open.

### (d) Skeptical probes
- `git log --all --diff-filter=A --name-only --since=2026-08-17 | grep -i census` — was a fixture
  ever added on any branch? (Assembler: no.)
- Copy the six custody files into `tests/fixtures/` right now and run the current census patterns
  against them. Do they PASS, or does the over-match still fire? Until that is executed, the row's
  stated purpose ("prove the fixed censuses PASS in the state they will actually run in") is unmet
  even in principle — there are no fixed censuses yet.
- The capture was taken by the **lead** with "lead-session lines labeled". Labeling is an editorial
  act on the ground truth. Who verified the labels?
- 23:51 on a night when the loop "ran unattended from ~18:45" (`t10-session.md`, Session shape).
  Was the machine genuinely quiescent, or only the *named* fleets?
- Ask whether the council can clear WINDOW-COUNCIL-GATE while A4 is BLOCKED on this row — D-149's
  auto-GO condition (1) requires exactly the clearance this row denies.

---

## ED-Q-L8-1 — privileged read path for the T-0 CLOCK_PROBE

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:195`
> - [L8] ED-Q-L8-1 (sudo): decide and prove the privileged read path for the T-0 CLOCK_PROBE — either a scoped read-only sudoers entry for `/usr/sbin/systemsetup -getusingnetworktime` or a ratified `sudo -v` warm-up literal immediately before the T-0 author — and exercise it once in a tap block; D-004's powermetrics-only NOPASSWD plus a >10-min-cold sudo timestamp otherwise guarantees an authoring refusal at night

### (b) What changed since 2026-08-15
- **(ii) THE SUDOERS FILE WAS INSTALLED AND EXERCISED — but it does not cover the read.**
  `docs/run_reports/2026-08-18-t10-session.md:106`: "Installed root:wheel 0440; digest
  **`7dfe980b…`** verified; **both** vectors passwordless with ground-truth state flips (Network
  Time Off→On)".
  The installed file is `scripts/joulewise-network-time.sudoers` (sha256 verified in this worktree
  as `7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d`, matching), whose entire
  grant is:
  `Cmnd_Alias JOULEWISE_NETWORK_TIME = /usr/sbin/systemsetup -setusingnetworktime off, /usr/sbin/systemsetup -setusingnetworktime on`
  — **`-getusingnetworktime` is NOT in it.** "both vectors" means off and on, not read and write.
- **The shakedown driver confirms the read was never granted**, and worked around it:
  `shakedown-driver.sh:31-32` — `"clock: D-127 disable (hygiene, custodied; prior state = On per
  Ed's qualification clock-post-state.txt; **the get vector is deliberately not NOPASSWD**)"`.
- **(iii)-adjacent: the code decided the question by implementation, not by ratification.** The T-0
  author takes the prior-state read as an **operator-interactive paste**, not a privileged probe:
  `_INTERACTIVE_PRIOR_STATE_ARGV = ["operator-interactive", "network-time-prior-state"]`
  (`joulewise/arm_readiness_evidence_t0.py:143`), enforced at `:862-863` ("prior clock-state capture
  was not Ed's interactive action"); `scripts/capture_t0_step.py:46,50,762-777,912-913` prompts for
  and exact-matches Ed's pasted output. The actual `CLOCK_PROBE` deriver
  (`arm_readiness_evidence_t0.py:891-905`) uses the **write** vector
  `sudo -n systemsetup -setusingnetworktime off`, which the installed sudoers does cover.
- **CROSS-CUTTING COLLISION the seat should see:** that design makes E-4 a **hands-required** step
  at T-0, which contradicts D-149's standing conditional T-0 GO ("full no-hands window automation",
  `docs/decision_log.md:173`) for any window that reaches the T-0 author.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** The seat is adjudicating three things at once: (1) the sudoers install/exercise
is real but discharges the *write* vectors, not the read path the row names; (2) the read path was
resolved by code as an operator-interactive paste and was **never ratified against this row** nor
exercised once through `capture_t0_step.py`; (3) that resolution is in direct tension with D-149.

### (d) Skeptical probes
- On the machine: `sudo -n /usr/sbin/systemsetup -getusingnetworktime` — does it prompt? If yes, the
  read path is not privileged-noninteractive, exactly as the row feared.
- `sudo -l -U edr` — enumerate the real installed grant and compare to the repo file byte-for-byte.
- Run `scripts/capture_t0_step.py clock-prior-state` once and confirm the operator-interactive paste
  path works end-to-end with a real systemsetup output. It has never been exercised.
- Reconcile with D-149: if E-4 requires Ed's hands, which windows can actually be no-hands? Ask
  whether D-149's auto-GO was written in awareness of `_INTERACTIVE_PRIOR_STATE_ARGV`.
- The row also warns about a ">10-min-cold sudo timestamp". Does the NOPASSWD grant make the
  timestamp irrelevant for the write vector, and is the read the only warm-sudo dependency left?

---

## ED-Q-L8-2 — full arm-sequence dress rehearsal (the program's most valuable Ed hour)

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:196`
> - [L8] ED-Q-L8-2 (sudo + Ed): full arm-sequence dress rehearsal on the recut packet — E-4→E-9 under the capture wrapper, T-0 authoring, arm→verify→consume against scratch custody/synthetic roots, with a real ≥10-minute prewindow wait — timed against the 20-minute volatile horizon and 5-minute arm-receipt fuse

### (b) What changed since 2026-08-15
- **(i) MECHANISM BUILT — and it was hard-won.** Five builder rounds (Sol xhigh/high r1–r2, terra
  xhigh/high r3–r5) produced `scripts/ed_session/build_rehearsal_env.sh` (183 lines) and
  `docs/process/rehearsal-operator-card.md` (123 lines), committed `ad14ac4` (**on main**).
  Rounds r1/r2 returned correct NEEDS_RULING with executed proofs; r4's F1 generalised into the
  absolute-`pack_root` authentication property that **voided the magistrate's own freeze wave before
  publication** (`docs/run_reports/2026-08-18-t10-session.md:1047`); r5 proved the E-8 scratch-ledger
  stop `calibration_ledger_head_uncommitted` rather than working around it.
- **(ii) NOT PERFORMED.** Stated OPEN in three places on main:
  `t10-session.md:110` ("Dress rehearsal | **OPEN**"), `t10-session.md:1213`, and
  `ed-morning-packet-2026-08-18.md:126` ("OPEN: the dress rehearsal (item 4) only.").
  No later trace records it; it does not appear in the T11/T12/T13 blocks of `RUN_STATE.md` at all —
  it dropped out of the tracked Ed-owed list after T10 (current list: `RUN_STATE.md:198,252,328,373`
  — family marker, A4 markers, env-fingerprint semantics, registry values, exact-byte confirmation).
- **THE MECHANISM IS NOW STALE.** The card runs against the `_v2` alpha pack —
  `rehearsal-operator-card.md:74` pins `--pack-root /Users/edr/JouleWise-measurement-20260818/configs/campaigns/d117_floor_qwen25_1p5b_v2`
  and `--custody-root .../ed-qual-20260817/rehearsal/...`. The D-147 transaction superseded `_v2`
  with the `_v3` family at `freeze-0003`. The card must be regenerated before it can run.
- `rehearsal-operator-card.md:35` also records that the builder's own smoke "reached the sandbox
  boot-ID boundary before this command could run" — even the smoke test of the card is incomplete.

### (c) Candidate disposition for the seat
**ED-ROW-OPEN.** The council called this "the program's most valuable Ed hour". Nine months of
mechanism exists; the hour was never spent; and the mechanism has since gone stale against `_v3`.
The seat is adjudicating an unexecuted row that also silently fell off the tracked owed-list.

### (d) Skeptical probes
- Read `rehearsal-operator-card.md` end to end and count how many commands still name `_v2`. Estimate
  the regeneration cost before the hour can even be scheduled.
- `grep -n "rehearsal" RUN_STATE.md` — confirm no mention after line 623 (a T8-era block). How does a
  row the council called most valuable disappear from the live pointer?
- The row demands timing "against the 20-minute volatile horizon and 5-minute arm-receipt fuse".
  Do those numbers still hold after #152 and D-146/D-147, or have the horizons moved?
- The builder proved E-8 stops on `calibration_ledger_head_uncommitted` against scratch. Can the
  rehearsal actually reach E-9 at all, or does it structurally stop at E-8? If it stops, the row is
  unpassable as written and needs an amendment, not a scheduling slot.
- Ask directly: is there any path to a claim window that does *not* require this row, given
  amendment 10's "stable evidence cannot be deferred"?

---

## ED-Q-L8-3 — live sampler-checklist and rail-probe executions on a quiet machine

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:197`
> - [L8] ED-Q-L8-3 (sudo, already chartered as steps 2-3): live sampler-checklist and keyboard-backlight rail-probe executions on a quiet machine (dry-run staging verified in this audit; the live arms and teardown censuses still need sudo)

### (b) What changed since 2026-08-15
- **Co-extensive with ED-L3-1 + ED-L3-3.** Both executed on 2026-08-17; evidence and gaps as recorded
  in those two rows. Sampler: PASS, cadence 1.0128 s, zero orphans, off-repo logs, repo-corroborated
  by `d873f77`/`e5dc38a`. Rail probe: ABBA executed, contaminated by concurrent load, artifact
  lead-restored.
- **This row adds one requirement the others state less sharply: "on a quiet machine".** The record
  is explicit that the machine was **not** quiet — the rail-probe deltas are attributed to
  "concurrent replay load + charge-termination step" (`t10-session.md:108`), i.e. the ~3h40m decisive
  replay was running during the qualification evening (started ~18:2x, `DECISIVE REPLAY: OK` at
  ~22:05 per `trace-notes.md:189`).
- The row also names "teardown censuses" — reported as "zero orphans" in the run report; the census
  outputs themselves are off-repo and unread by this assembler.

### (c) Candidate disposition for the seat
**ED-ROW-PARTIAL.** The seat is adjudicating whether executions performed while a 3h40m CPU-bound
replay was running satisfy a row whose text says "on a quiet machine".

### (d) Skeptical probes
- Timeline check: `decisive-replay.log` start/end timestamps vs `keyboard-backlight.txt` (18:00:42),
  the sampler-checklist log times, and the rail-probe arms. How much of the qualification evening
  overlapped the replay?
- If the sampler checklist ran under the same load, is "cadence mean 1.0128 s" a quiet-machine number?
- Read the pre- and post-teardown census files directly; "zero orphans" is a summary, and the row
  requires *empty* censuses on both sides.
- Both halves re-run in ~12 minutes on a genuinely quiet machine. Ask why that has not been scheduled.

---

## ED-Q-L8-4 — live quiet_mac_prep.sh confirming its three OK literals

### (a) Original finding (VERBATIM) — `sitting-packet-FINAL.md:198`
> - [L8] ED-Q-L8-4 (sudo): live quiet_mac_prep.sh run to confirm its three OK literals (passwordless powermetrics, displays asleep, screensaver disengaged) match what the T-0 author's _quiet_capture requires verbatim

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** No execution of `scripts/quiet_mac_prep.sh` since the council. Post-council
  hits are static reads only: `docs/process_traces/2026-08-18-shakedown-first-light/01-protocol-scout.md:172-173`
  cites `quiet_mac_prep.sh:12-15` and `:85-126` as *code references* in the scout's protocol survey.
  The two `RUN_STATE.md` execution mentions (`:3634`, `:3778`) are from far older blocks and record
  the known "Graphics capability FAIL is a false negative" note.
- **The shakedown deliberately did not use it:** `shakedown-driver.sh:44` runs a bare
  `/usr/bin/pmset displaysleepnow || true` instead. So even the one live quiet-machine event of the
  post-council period bypassed the script this row is about.
- The rehearsal card's E-7a quiet-mac-prep step (`rehearsal-builder-brief.md:93`) never ran — the
  rehearsal is open.
- **The row's substance — literal string matching between the script's OK lines and the T-0 author's
  `_quiet_capture` — was never checked by anyone**, live or on paper. `sitting-packet-FINAL.md §6`
  L8 confirms the seat could only do "static review only".

### (c) Candidate disposition for the seat
**ED-ROW-OPEN.** The seat is adjudicating a row where a single live run would either confirm or
break the T-0 author's `_quiet_capture` parse — and where the only post-council quiet-machine event
routed around the script entirely.

### (d) Skeptical probes
- Cheapest possible check, no sudo needed for the paper half: diff the literal OK strings emitted by
  `scripts/quiet_mac_prep.sh` against what `_quiet_capture` in `joulewise/arm_readiness_evidence_t0.py`
  parses. A mismatch is findable at the desk in minutes — do it before scheduling machine time.
- Run the script live in a quiet block and capture all three OK literals verbatim.
- The known "Graphics capability FAIL is a false negative" — does `_quiet_capture` treat that FAIL as
  fatal? If so, the T-0 author refuses on a benign condition.
- Why did `shakedown-driver.sh` substitute `pmset displaysleepnow`? If the author of that driver
  judged `quiet_mac_prep.sh` unsafe or unsuitable, that judgement belongs in front of the seat.

---

## SUMMARY TABLE — 23 ED-QUALIFICATION rows

Legend: **CLOSED** = ED-ROW-CLOSED (candidate) · **PARTIAL** = ED-ROW-PARTIAL · **OPEN** = ED-ROW-OPEN.
No row is ED-ROW-SUPERSEDED: no post-council ruling retires any ED-QUALIFICATION row.
"off-repo" = `~/JouleWise-window-custody/…`, unreadable by this assembler.

| # | Row | One-line requirement | Disposition | Evidence pointer |
|---|---|---|---|---|
| 1 | ED-QUAL-L6-1 | Live T-0 authoring path on the measurement Mac; 15 receipts author; same-boot `arm` reaches row evaluation | **OPEN** | none found (mechanism only: `scripts/capture_t0_step.py` #152 `a61ac92`; card `ad14ac4`) |
| 2 | ED-QUAL-L6-2 | Timed freeze-refresh rehearsal incl. dry-run; observed wall-clock into the runbook schedule | **PARTIAL** | lane executed for real ×2 (`54f990d..75f22a0` main; `3a75a77`→`8b2b021` branch-only); **no dry-run leg, no recorded duration** |
| 3 | ED-QUAL-L1-1 | Same-boot production replay: `generate_arm_readiness.py verify` + `project_identity_pins.py verify`, real model bytes | **PARTIAL** | boot `da90818c…` still live; `freeze`/U11-`freeze` ran on the production Mac (`3d05982`,`6fd8bce`,`74632e3`,`5e38f1e`,`eb7f6c6`,`94dc3b3`, branch-only); **no `verify` run found** |
| 4 | ED-QUAL-L1-2 | Re-author pack freeze evidence, reissue receipts, update pins, recommit on the production machine | **CLOSED** | `freeze-0003.json` ×3 in-tree; S4 33 receipts PASS `3a75a77`; table `8b2b021` — **branch-only** |
| 5 | ED-QUAL-L5-1 | Real systemsetup captures into `arm_readiness.t0.inputs`, validated against the t0 capture validators | **PARTIAL** | raw vectors captured off-repo (`clock-{prior,post}-state.txt`); **not in the t0 namespace, never validated** |
| 6 | EDQ-L2-1 | Crash matrix to completion on the quiet bench at the audit-baseline head; pass + wall time | **PARTIAL** | `…/2026-08-18-freeze-semantics-coldgate/verification-logs/crash-matrix-quiet-20260818-0110PT.log` (`3f9d759`, main): 15 tests / 535.763 s / OK — **wrong head, 15 vs 16 tests** |
| 7 | EDQ-L2-2 | §5C lead live verification on the production checkout w/ D-134 dry-run receipt at reviewed HEAD | **OPEN** | none found; only `dry-run-0001` @ `49dcc49` (2026-08-13, `_v1` pack) |
| 8 | ED-L3-1 | Live sampler checklist; close only after WO-L3-2/WO-L3-3 (checklist home + 100 ms leg) | **PARTIAL** | executed (off-repo logs; repo-corroborated `d873f77`,`e5dc38a`); **WO-L3-2/-3 never queued; `sampler-checklist.sh:59` still `-i 1000`** |
| 9 | ED-L3-2 | One live observation that `sudo -n powermetrics` exits within the 10 s SIGTERM grace | **OPEN** | none found; dropped from `ed-evening-checklist.md` despite `council-verdict.md:92` |
| 10 | ED-L3-3 | JW-MET-3 ABBA rail probe, documentation-grade | **PARTIAL** | executed 2026-08-17 (`t10-session.md:108`); **contaminated by concurrent load; artifact lead-restored after overwrite** |
| 11 | ED-L3-4 | Live capture with `hw_model`/`kern_osversion` recorded and matched to Mac15,9 / macOS 25F84 | **PARTIAL** | live captures exist off-repo; **no recorded binding anywhere** (`grep 25F84` → only `window_runbook.md:703`) |
| 12 | ED-L7-1 | `prewindow_check.sh --wait` to READY + `quiet_mac_prep.sh` on the freed quiet machine | **OPEN** | none found (card text only: `rehearsal-operator-card.md:69-74`) |
| 13 | ED-L7-2 | Fresh §5C dry-run PASS receipt binding the final reviewed head + committed-pack digest | **OPEN** | none found; `alpha_arm_readiness.md:102` "successor recheck required" |
| 14 | ED-L7-3 | `validate_powermetrics_fiducial --allow-live` → `instrument_evidence.json` consumed by the §5B jq screen | **PARTIAL** | producer ran live (`shakedown-driver.sh:60-72`, D-142/D-143); **clone ledger, first eval failed closed, consumer edge unobserved** |
| 15 | ED-L10-1 | Desk replay of the full post-collection chain against retained a9/a10; every command + exit code | **OPEN** | none found; listed as owed in `ed-evening-checklist.md:24`, never produced |
| 16 | ED-QUAL-L4-1 | `replay_d117_decisive.sh` full chain at the audited head | **CLOSED** | `DECISIVE REPLAY: OK`, 13,180.653 s, off-repo `decisive-replay.log`; repo-corroborated `724ea28`,`1500265`, `tests/test_decisive_reference_resolution.py` (main) — **2026-08-17 head, pre-r5/r6** |
| 17 | ED-Q-L9-1 | Keyboard-backlight census: level 0 / auto-adjust off / inactivity Never, `operator_visual` | **CLOSED** | off-repo `keyboard-backlight.txt` 2026-08-17 18:00:42 (`t10-session.md:108`) — mutable setting, no T-0 re-check |
| 18 | ED-Q-L9-2 | JW-MET-3 ABBA differential (L9's emission of the same probe) | **PARTIAL** | same single run as row 10; same contamination + restored-artifact caveats |
| 19 | ED-Q-L9-3 | Capture 4× PROCESS_CENSUS + 1× MAINTENANCE_CENSUS quiet **and commit them as the regression fixture** | **PARTIAL** | captured off-repo `quiet-census/` (6 files + CAPTURE-NOTE.txt, 23:51, **by the lead**); **NO fixture committed — `TASK_QUEUE.md:538` A4 still BLOCKED** |
| 20 | ED-Q-L8-1 | Decide + prove the privileged READ path for CLOCK_PROBE and exercise it once | **PARTIAL** | sudoers installed/exercised (digest `7dfe980b…`) but grants **only** `-setusingnetworktime off/on`; read resolved as an operator-interactive paste (`arm_readiness_evidence_t0.py:143,862`), never ratified or exercised; **collides with D-149** |
| 21 | ED-Q-L8-2 | Full dress rehearsal E-4→E-9 + author→arm→verify→consume vs scratch, real ≥10-min wait, timed | **OPEN** | none found; OPEN per `t10-session.md:110` and `ed-morning-packet:126`; mechanism `ad14ac4` is **stale (`_v2`-bound)** |
| 22 | ED-Q-L8-3 | Live sampler-checklist + rail-probe **on a quiet machine**, incl. teardown censuses | **PARTIAL** | both executed 2026-08-17 but **during the 3h40m decisive replay** — not a quiet machine |
| 23 | ED-Q-L8-4 | Live `quiet_mac_prep.sh` confirming its three OK literals match `_quiet_capture` verbatim | **OPEN** | none found; shakedown bypassed it (`shakedown-driver.sh:44` bare `pmset displaysleepnow`) |

**Tally: 3 CLOSED (candidate) · 12 PARTIAL · 8 OPEN · 0 SUPERSEDED.**
Under charter amendment 11 ("all ED-QUALIFICATION rows closed with evidence"), 20 of 23 rows are
not in a state the clearance rule accepts on this record. Two of the three CLOSED rows rest wholly
or partly on an off-repo custody root; the third (ED-QUAL-L1-2) is branch-only.

---

## ROW-LEVEL OPEN ITEMS

- **ED-Q-L9-3's committed fixture does not exist.** The capture is real and off-repo; the row's
  second clause ("commit them as the regression fixture") has no artifact anywhere in the tree.
  `TASK_QUEUE.md:538`/`:632` and `state_kernel.json:3125,3148,3158,3168` still carry A4
  WO-CENSUS-SEMANTICS as BLOCKED on it, so the L9-B2 / L8 `t0.no_stray_keepawake` census blockers
  remain live. This is the single largest unclosed dependency in the file.
- **ED-Q-L8-2 (the full dress rehearsal) was never run** and fell out of `RUN_STATE.md`'s tracked
  Ed-owed list after T10. Its mechanism (`ad14ac4`) is now `_v2`-bound and stale against the `_v3`
  family; even the builder's smoke never reached the dry-run command.
- **D-127's sudoers grants only the WRITE vectors.** `scripts/joulewise-network-time.sudoers` covers
  `-setusingnetworktime off|on` and not `-getusingnetworktime`. ED-Q-L8-1's read path was settled
  by code as an operator-interactive paste (`_INTERACTIVE_PRIOR_STATE_ARGV`), never ratified against
  the row, never exercised through `capture_t0_step.py`. **This collides with D-149's no-hands
  auto-GO** and no one has reconciled the two.
- **WO-L3-2 and WO-L3-3 were never registered.** They exist only in
  `2026-08-15-readiness-council/triage.json:284-285` and the L3 seat report — never in `TASK_QUEUE.md`
  or `state_kernel.json`. ED-L3-1's text forbids closure until they land; `sampler-checklist.sh:59`
  still samples at 1 Hz against a 100 ms production binding, and `ed-qualification-session.md`
  Step 2 still points at the wrong home. **The seat should ask what else was lost between triage
  and the queue.**
- **ED-L3-2 (SIGTERM relay) was named by the council verdict and is absent from the operator
  checklist Ed actually worked.** So is the "production-machine freeze-chain replays" item's
  `verify` half (ED-QUAL-L1-1). The batched-session script under-covered the verdict's own list.
- **Three ED rows never reached any Ed-facing checklist at all:** EDQ-L2-1, ED-L7-3, ED-Q-L8-4.
- **ED-L10-1 may be structurally unpassable now, not merely undone.** D-148.7 registered the
  anchor-v2 population as permanently non-claim-bearing, mechanically enforced by D-146's
  `capture_pipeline_superseded` barrier. If a9/a10 are anchor-v2-era, the desk replay cannot produce
  the PASSED basis the row demands, and the council needs a substitute source of CLI-level
  PASSED-basis positive proof. Nobody has adjudicated this.
- **EDQ-L2-2 / ED-L7-2 have a sequencing trap the council must resolve:** the dry-run receipt must
  bind the *final reviewed head*, but a merge wave is queued. Any dry-run run before the wave is
  stale after it.
- **Custody unreadability is a packet-level defect, not a row-level one.** Ten rows' only primary
  evidence lives under `~/JouleWise-window-custody/ed-qual-20260817/` and
  `~/JouleWise-window-custody/shakedown-20260818/`. This assembler could read none of it. Every
  "CLOSED"/"PARTIAL" resting on it is a lead's report of an artifact, not the artifact. The seat
  should decide whether the clearance rule's "with evidence" tolerates that, and whether the custody
  roots should be inventoried (hashes + listing) into the repo before the sitting.
- **EDQ-L2-1's test count moved from 16 to 15** with no explanation in the record. If the missing
  test is the degenerate-cost case behind finding L2-1, the finding is masked rather than cured.
- **ED-L3-3 / ED-Q-L9-2's primary artifact was overwritten by the operator and reconstructed by the
  lead.** A reconstructed evidence file is testimony; the seat should decide whether it is admissible
  or whether the ~7-minute probe is simply re-run clean.
- **The qualification evening was not a quiet block.** The 3h40m decisive replay ran concurrently
  with the sampler checklist, rail probe, and backlight rows. ED-Q-L8-3 says "on a quiet machine"
  explicitly; ED-L3-3's own numbers show the contamination.
