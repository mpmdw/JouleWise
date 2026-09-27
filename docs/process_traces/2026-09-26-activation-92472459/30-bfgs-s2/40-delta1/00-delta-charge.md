# BFG-S S2 delta re-audit of fix round 1: `4ea4b26b..6c73caf4`

**Candidate.** `feat/2026-09-26-bfgs-s2-qpe-collector` @ `6c73caf4`. Read-only worktree `/Users/edr/code/JouleWise-wt-s2lens-92472459` (detached @ `6c73caf4`). Delta: `git diff 4ea4b26b 6c73caf4`. Full S2 diff: `git diff 1417c0c4 6c73caf4`.

**What the fix round was asked to do:** `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/30-bfgs-s2/30-fix1/10-fix-contract.txt` (items F1–F8, each with a dictated closure, and one NO CHANGE item). The seat's report: `30-fix1/11-seat-report.md`. The round-1 lens reports that motivated it: `30-bfgs-s2/20-lenses/11-sol-execution-lens.md` and `12-opus-contract-lens.md`. The ruled texts: listed in `30-bfgs-s2/10-seat-brief.txt`.

**Questions.**
1. Does each of F1–F8 close its finding exactly as dictated, no more and no less? Is the closure pinned by a test that dies under the named counterfactual (run the mutant)?
2. **Did the fix round introduce a defect?** Fix rounds have introduced defects before. Look especially at: F2's shared booking helper (did the authenticated path's order, reasons or covariates change for any envelope class?); F4's before/after byte comparison (can an honest night now raise, e.g. an envelope whose collector is still writing, or whose files the executor itself rewrites, such as `record_attestation`? does every summary read now come from the authenticated bytes?); F1's `execute` change (can a non-replay night now be refused?); F7's write order (does the refusal record still authenticate?).
3. **Same-signature statement:** is any finding of this delta the same defect class as a round-1 finding (custody converted to exclusion; an unpinned routing operand; a record field dropped under a battery status)? Say yes/no per class.

**Standing constraints:** as in the round-1 lens charge (`20-lenses/00-lens-charge.md`).

**Output.** Findings tiered BLOCKER / SHOULD-FIX / NIT with executed evidence (command + exact tail), the production call site, and a closure shape; the same-signature statement. Edit no repository file; scratch under `/tmp`.
