# BFG-D final-pass charge: gate-ledger row 7, cold Fable; row 6, Opus counter-review

**Exact merge candidate:** `b2c31e5b` on `feat/2026-09-25-bfg-d`. It was merged with main at `a9c40d4c`, so `git diff origin/main b2c31e5b` is the PR diff.

**What BFG-D is.** BFG-D implements Ed's binding directive #421 for derivation windows: the battery must be floating (not charging, near-zero current, fresh gauge) at arm, at publication and at t0. Every slot is bracketed by `ioreg` reads outside the clock anchor. Each window's verdict is committed at harvest, before any B is read, and every consumer authenticates that verdict through one seam. W1, the next measurement window, cannot arm until this merges.

**Governing rulings.** Read the source copies in this directory:
- BATTERY-FLOAT-01 and its addendum: `00-…` §5.
- HARVEST-VERDICT-FINAL-01 and its addendum: `06-…` §4, with §4.5 reissued in `29-…`.
- BFG-D-PARSER-ESC-01: `15-…` §4 and §6; the refuter's additions are in `18-…` R2-8..R2-11.
- CONSUMER-DRIFT-ESC-01 and its addendum: `23-…` §3.

**Review history.** `11-review/` holds three lenses, three delta rounds and the final deltas. The triage files are `12-…`, `18-…`, `20-…`, `24-…`, `26-…` and `30-final-delta-triage.md`.

**Lead decisions that no cold gate has ruled. Rule each one: AFFIRM or REVERSE.**
1. FX-2. `battery-verdict` authenticates the working-tree head pin against the ledger head, instead of requiring an already-committed pin. Consumers add check 5: the verdict was committed together with its pin. The reason: the ruled harvest order could not otherwise complete (Astra B2).
2. The t0 R1 liveness bound is 610 s (11 × 45 + 10 + 105) rather than the literal 645 s. Every lens affirmed 610.
3. The lead adopted refuter MATERIALs R2-8..R2-11 without convening an addendum.
4. The AST guard does not catch a computed module name via `importlib`. This is recorded as a limitation under D-161.
5. The pin proof is taken against main `cab01506`, not `c6814dd8`.
6. C-2(b) was reverted; the paper tool is pinned in the results registry and is dispositioned as reading pinned historical corpora.
7. The kernel evidence label and the test comment follow the renamed liveness test. Decision-log line 11131 is left as history.

**Answer each question with executed evidence:**
- **Q1.** Does the diff implement every governing obligation, with nothing weakened?
- **Q2.** Is there any route by which a charging, stale, missing or custody-failed window could count as evidence? Is there any route by which a clean window could be dropped after B is seen?
- **Q3.** Can any battery observation perturb a measured number or a pinned byte?
- **Q4.** Is it fit to merge? Say MERGE or FIX-FIRST, and give dictated closure texts for any FIX-FIRST item.

**Constraints:**
- Read-only, except `/tmp` scratch space, which you remove afterwards.
- Focused unit tests only; no discovery.
- Never run sudo, launchctl, powermetrics, the installer or model inference.
- Work in one foreground session, with no subagents.
- Write only the file named in your prompt.
- Begin with a contamination disclosure.
- Do not read RUN_STATE.md, TASK_QUEUE.md, memory or council logs.
