# 02c — Ruling on the delta re-audit of fix round 4 (record 02b), magistrate b0ae8462, 2026-09-15 20:48 PDT

The auditor (Astra xhigh, read-only, worktree `wt-delta4-txn` detached at `0ba6ce54`) executed the three isolated
reversions and all three module suites (foreground and under inherited SIG_IGN; 183 tests, OK both ways), then answered
the same-signature question by executing 50 predicate cases and reported `class_1: YES`, `class_2: YES` **on a literal
reading**, flagging both for a lead ruling rather than classifying them as recurrences. Ruling:

**Class 1 — NO.** The brief's predicate is "installer exits 0 with a label loaded while a clock read taken after the
LAST LAUNCHD MUTATION is at or past min(selected_span_close, install_close_epoch)". The clock read the predicate names is
the engine's commit-gate read (adjudication 34 D5/D6: the commit predicate is evaluated once, on a clock read taken after
the last launchd mutation). The auditor's witness is its OWN observer clock read taken later still (`final observer
clock=1789498860 >= close`), while the engine's post-mutation read was `1789498800 < close` — and the auditor's own
`engine_postmutation_clock_violation: false` confirms it. A clock that keeps advancing after a correct commit will always
eventually pass the close; that is not the class-1 defect (a commit accepted on a stale pre-mutation read). Same verdict
as deltas 1–3 (lieutenant records lt-27/lt-30) and the Opus execution lens (lt-28).

**Class 2 — NO.** The two witness families are labels pre-loaded WITHOUT a plist BEFORE the run (an orphan planted in
the fake launchd): install refuses with exit 3 and leaves the orphan exactly as found; uninstall with the orphan loaded
exits 4 (RETAINED) and likewise leaves it. The predicate targets states the transaction PRODUCES ("any path ends with a
label loaded and its plist absent") or an exit 0 while a label it attempted to bootout is still loaded; neither case exits
0 and neither case was produced by the installer — refusing to touch a pre-existing orphan is D7's ruled behaviour
(`new_orphan_or_false_bootout_success: false` in the auditor's own summary). The predicate text will be tightened for the
delta on round 5: "…a label loaded and its plist absent **where the run mutated that label or its plist**".

**R2 (nit) — accepted.** The S1 mutant is the VERIFIED-guarded RETAINED-branch `4 → 1` (the shape in lt-28), not an
unconditional rewrite; the auditor showed the unconditional shape is already RED without the S1 cell, so the cell's
value is the guarded shape. Recorded; no change.

**Reversions:** (a) S2 oracle reverted → six cells FAIL under inherited SIG_IGN and pass in the foreground — the oracle
discriminates; (b) S1 cell reverted → the guarded mutant survives, with the cell it is RED (36 failures); (c) shell argv
guards reverted → dangling `--plan` exits 1 instead of 2. All three fix-round-4 changes are real.

**Census (bench, because the sandbox denied `ps`):** no process from the audit copy survives; `/private/tmp/iw-*` count
is 0 after the suites exited (the 263 dirs seen mid-run were live matrices, cleaned on normal exit; the leak-on-kill
mechanism is A207's).

Gate ledger row 4/5 for fix round 4: SATISFIED — same-signature answered by executed predicates, NO/NO under this ruling.
