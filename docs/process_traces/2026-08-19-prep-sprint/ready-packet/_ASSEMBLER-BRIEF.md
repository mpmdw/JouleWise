# ASSEMBLER BRIEF (internal — for the packet-building agents, not a packet file)

## What we are building
The READY-CANDIDATE council packet that reconvenes the 2026-08-15 instrument-readiness
council. Cold-gate doctrine: **the packet is MECHANICALLY ASSEMBLED. Assemblers do NOT
grade rows READY.** You attach evidence and name the candidate disposition a seat must
adjudicate; the seat judges.

## Read-only rules
- Repo worktree (READ ONLY, never write, never `git checkout/commit/stash`):
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS0`
  branch `impl/r2-s0-mint-resolver` @ `d10881b`.
- ALL writes go under
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/ready-packet/`
- No network. `git log`, `git show`, `git diff`, `grep`, `sed` reads are fine.

## Primary sources
- Original verdict: `docs/process_traces/2026-08-15-readiness-council/council-verdict.md`
- Sealed sitting packet (verbatim blockers §3, should-fix §4, ED-QUAL §5, unexecuted §6,
  refuter verdicts §9): `.../2026-08-15-readiness-council/sitting-packet-FINAL.md`
- Per-seat reports: `.../2026-08-15-readiness-council/seat-reports/L*-report.md`
- Refuter outputs: `.../2026-08-15-readiness-council/refuter-outputs/`
- Cold ruling + Opus refuter: `cold-fable-ruling.md`, `opus-contract-refuter-findings.md`
- Charter: `docs/process/instrument-readiness-audit-charter.md` (verdict form = amendments 11-12)
- Work-order closure evidence: `TASK_QUEUE.md` (Completed table ~lines 100-115; hand-authored
  WO notes ~lines 190-520; the GENERATED "Current Queue" region A-rows from
  `docs/process/state_kernel.json`)
- Decision log: `docs/decision_log.md` — D-138..D-149 index at ~lines 8791-8901, bodies later.
- Phase-2 transaction: `docs/process/phase2-transaction-runsheet.md`
- Ed/operator qualification: `docs/process/ed-batch-packet.md`,
  `docs/process/ed-morning-packet-2026-08-18.md`, `docs/process/rehearsal-operator-card.md`,
  `docs/process/ed-evening-checklist.md`, `docs/process/ed-s5-mint-decision-2026-08-19.md`
- Process traces since the council (all under `docs/process_traces/`):
  `2026-08-15-l2-reaudit`, `2026-08-15-*-consult`, `2026-08-15-m2-coldgate`,
  `2026-08-15-recorder-race-coldgate`, `2026-08-16-grant-identity-consult`,
  `2026-08-16-launch-f3-coldgate`, `2026-08-16-phase2-plan-consult`,
  `2026-08-17-freeze-numbering-consult`, `2026-08-18-anchor-v3-science-review`,
  `2026-08-18-freeze-semantics-coldgate`, `2026-08-18-shakedown-first-light`,
  `2026-08-18-t10-t11-working-notes`, `2026-08-19-r1-r2-codesign`,
  `2026-08-19-refreeze-execution`
- `RUN_STATE.md` (4862 lines — grep, don't read whole), `docs/council_log.md`

## Repo state facts already established (do not re-derive; DO verify anything you cite)
- HEAD `d10881b` on `impl/r2-s0-mint-resolver`; `origin/main` == `main` == `0099382`;
  49 commits on HEAD not on origin/main; merge-base `311d8016`.
  **Evidence living only on the branch and not on main is a material fact for a seat —
  always state WHERE evidence lives (merged to main / branch-only / uncommitted).**
- Merged council Phase-1 work orders (TASK_QUEUE Completed table):
  - WO-KERNEL-RECONCILE — PR #150 (`47d2645`): WINDOW-COUNCIL-GATE live; P2-006 retired.
  - WO-MARGIN-RECORDER-AUTHZ — PR #151 (`00ec3b7`).
  - WO-T0-PRODUCER — PR #152 (`a61ac92`) at head `9e8936a`: `scripts/capture_t0_step.py`,
    strict R2 plan resolver, D-127 privileged clock route, dwell/env hardening.
  - WO-L2-REAUDIT — delivered same day, custody `docs/process_traces/2026-08-15-l2-reaudit/` (`0f886d3`).
  - WO-ARM-EVIDENCE-AUTHOR-01 — PR #149 (`ac3fe1d`) (pre-council).
- STILL OPEN in the generated kernel queue (status text as of the current head):
  - A1 `WO-LAUNCH-BINDING` — READY [AGENT] (i.e. queued, NOT done). Hand-authored
    "WO-LAUNCH-BINDING stage checkpoint — 2026-08-15" in TASK_QUEUE says stage 1 + campaign
    half of stage 2 are on branch `impl/wo-launch-binding`; "does not close A1 or clear
    WINDOW-COUNCIL-GATE".
  - A2 `WO-CONSUMPTION-EDGE` — PARTIAL; READY [AGENT]
  - A4 `WO-CENSUS-SEMANTICS` — BLOCKED on ED-Q-L9-3
  - A5 `WO-DETECT-PULSES-BUDGET` — PARTIAL; READY [AGENT] (impl note in TASK_QUEUE ~line 317,
    branch `impl/wo-detect-pulses-budget`)
  - A62 `WO-PROOF-RUNNABILITY-REPAIR` — READY [AGENT]
  - `WO-RECORDER-GRANT-IDENTITY` — RETIRED WITHOUT IMPLEMENTATION by D-139 A1.
- Phase-2 transaction (T10 + this session): S0–S5, `freeze-0003` family for the `_v3` packs,
  r6 acceptance, capture-era system, claim barrier (D-146), D-147 mint-lane ruling.
  Freeze-0003 commits: `5e38f1e` (1p5b_v3), `eb7f6c6` (7b_v3), `94dc3b3` (contrast_v3),
  `8b2b021` (S5 confirmation table). U11 projections: `3d05982`, `6fd8bce`, `74632e3`.
  These are on the BRANCH, not on main — verify.
- D-148 (Ed's seven rulings 2026-08-19), D-149 (standing conditional T-0 GO / no-hands window
  automation, `0e96dbb`), D-139 (Ed batched rulings A1-A3), D-142/D-143, D-144 (co-design
  protocol), D-145, D-146 (R1 capture-pipeline v3), D-147 (R2 mint-lane).
- Shakedown first light: `docs/process_traces/2026-08-18-shakedown-first-light/`.

## OUTPUT FORMAT — follow exactly
One markdown file per assignment (filename given in your task). Structure:

```
# ROW <ID> — <seat name> (<gating|non-gating>)
Original verdict: NOT-READY (<n> blockers / <n> should-fix / <n> nits / coverage <x>/<y>)
[plus "UNVERIFIED on coverage" where it applies]

## <FINDING-ID> — <short title>
### (a) Original finding (VERBATIM)
> <exact text from sitting-packet-FINAL.md §3/§4, with its `at:` citation>
Citation: sitting-packet-FINAL.md §3 "<heading>"; seat report <path>; refuter verdict <path/section>
Post-verdict adjudication (if any): <e.g. "struck per council-verdict.md Disposition 4">

### (b) What changed since 2026-08-15
- <exact commit sha + subject, PR number, file path:line, custody trace path, receipt id>
- WHERE it lives: merged to main `<sha>` / branch-only `<branch>@<sha>` / uncommitted
- <what the change actually does, in one or two lines, verified by reading the code/doc>

### (c) Candidate disposition for the seat
One of: READY-EVIDENCE-ATTACHED / STILL-OPEN / ED-ROW / SUPERSEDED-BY-RULING /
STRUCK-AT-2026-08-15 / NO-REPAIR-FOUND. Then one sentence saying what the seat is
adjudicating. **Never write "READY" as a conclusion — write what evidence is attached
and what remains for the seat to weigh.**

### (d) Skeptical probes
- 3-6 concrete, checkable probes a hostile seat should run (command, file, or question),
  each aimed at a way the attached evidence could be false or incomplete.
```

End your file with:
```
## ROW-LEVEL OPEN ITEMS
- <anything in this row that NO repair addressed, or where you could not find evidence>
```

## Discipline
- Verbatim means verbatim. Copy the finding text exactly; do not paraphrase or shorten.
- Every pointer must be checkable: sha, path, path:line, PR number, or custody dir.
- If you cannot find repair evidence, write **NO-REPAIR-FOUND** and say what you searched.
  Honesty over completeness-theater. Do not invent closure.
- Do not grade. Do not write "this row is now READY".
- Keep each finding sub-row tight; the packet is for reading at a sitting.

## Return to the orchestrator
A short summary: file written, count of sub-rows by candidate disposition, and the full
row-level OPEN ITEMS list. Do not paste the whole file back.
