RECOVERY GAUNTLET DELTA RE-AUDIT (fresh adversarial reviewer; read-everything, write-nothing-in-repo; emit the report as your FINAL MESSAGE).

You are auditing the fix round FIX-1..13 on branch impl/d117-ledger-recovery at 468e0a6 (this worktree). The fix-round diff is `git diff 3df8777..468e0a6`. Fix rounds introduce defects — this is proven history in this repo; your job is to try to FAIL this round, not to confirm it.

READ IN FULL FIRST (all in this worktree or the referenced scratchpad):
- docs/process_traces/2026-08-08-recovery-exits-escalation/GAUNTLET-LENS-A-WITNESS-CORPUS.md
- docs/process_traces/2026-08-08-recovery-exits-escalation/GAUNTLET-LENS-B-CUMULATIVE-DELTA.md
- docs/process_traces/2026-08-08-recovery-exits-escalation/GAUNTLET-TRIAGE.md
- The fix-round contract: /private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/recovery4-prompt.md
- The fix-round report: /private/tmp/claude-501/-Users-edr-code-JouleWise/8f13f748-d7d8-43aa-a780-691dddf6a2f4/scratchpad/recovery4-out.md

DELIVERABLES (all five; severity-tiered P1 acceptance-blocking / P2 should-fix; every finding gets file:line + a concrete reproduced scenario):

1. PER-FIX CLOSURE TABLE (FIX-1..13). For each: does the landed change implement the dictated closure, and is its regression DISCRIMINATING — would it FAIL against the named broken implementation the lens admitted? Verify by reading and by running the named tests. Where discrimination is unclear, prove it with a mutation probe executed ONLY in a temporary copy of the repo under $TMPDIR (copy, mutate, run there) — NEVER mutate this worktree.

2. PROHIBITED-SHAPE SWEEP, same-signature grading, both classes currently at COUNT 1:
   (a) unexecuted-proof — any witness/test that asserts an outcome without executing the mapped exit/correction (string comparison, marker firing, monkeypatched shortcut);
   (b) inspect-as-permission — any diagnostic/audit route whose output can authorize (emit or feed ready_to_arm or equivalent).
   Sweep the ENTIRE post-fix tree (production + tests), not just the cited sites. Verdict per class: DEAD or ALIVE with the reproduced site. If ALIVE, label it explicitly "same-signature COUNT 2" and STOP THERE on that class — do not design a fix; the magistrate escalates to a consult by standing rule.

3. ORPHAN-REAPING FINDING (new, from the lead's checkpoint note, quoted): "Eight orphaned python test children (PPID 1, ~55% CPU each, ~8 min) from the recovery crash-matrix/witness harness (tempfile repo tmprk9virdc) were found spinning and lead-killed. SIGKILLed parents leak their spawned children — the harness must kill via process groups / addCleanup so witnesses reap everything they spawn." Verify:
   (a) whether the post-fix harness actually reaps: find the kill mechanism (process-group kill / setsid / addCleanup), then RUN the crash matrices and witness suites and check for leaked processes afterwards (capture `ps` evidence before/after; a leaked spinning child is a P1 test-hygiene defect);
   (b) whether the fix round's in-run "full suite 2770 OK" could have been TIMING-DISTORTED by spinning orphans — identify timeout/timing-sensitive tests in the touched suites and state the exposure concretely.

4. NEW-DEFECT HUNT over the fix-round diff itself, production code first: calibration_exits.py, calibration_ledger.py, calibration_bracketing.py, the three scripts. Specifically probe: FIX-2's identity-keyed lease (does realpath/inode keying break any legitimate concurrent-different-ledger flow, or refuse a valid re-acquire?); FIX-3's all-finalized-sessions custody verification (over-refusal on the legitimate morning path? performance blowup on large ledgers?); FIX-4's recovery-shaped-terminal-state gate (does any legitimate desk-only pin advancement now refuse?); FIX-9's kill-switch env/config crash points (are they inert in production — prove no production code path can trigger them).

5. FULL SUITE RUN, unpiped, exact tail (total count, failures, skips, wall time), run from a clean process; afterwards check for leaked processes again. Compare the count and wall time against the in-run claim (2770 OK) and flag any discrepancy.

VERDICT: ACCEPT or FAIL, plus the per-class DEAD/ALIVE verdicts, plus a one-line "checks performed" list.

WRITE_SCOPE: []

CONSTRAINTS: this worktree is READ-ONLY for you — the WRITE_SCOPE above is exhaustive (no repo edits at all) — all scratch work in $TMPDIR only; do NOT git commit anywhere; do not touch RUN_STATE.md, TASK_QUEUE.md, docs/decision_log.md, docs/council_log.md, or the three gauntlet/triage records. Never pipe a test run through anything that eats the exit status. If reports, tests, and decision-log entries conflict, named decisions win; flag any conflict in the final message. If this prompt's requested expectation contradicts the binding contracts, do not force it — report the contradiction.
