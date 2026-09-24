ROLE: INDEPENDENT CHECKER seat, fix round 1, for JouleWise lane A291. You maintain the oracle that the packer implementation is stress-tested against; you are not the implementer, and you must not read or copy any packer implementation (none exists on your branch). Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: ["tests/scored_roster_checker.py", "tests/test_scored_roster_checker.py"]

0. CONTEXT. Linked worktree /Users/edr/code/wt-a65fb4fa-a291chk, branch fix/2026-09-24-a291-checker-r1 at b8962fd0 (the committed checker). Do not commit. Fences: never launchctl, sudo, networksetup; never touch /Users/edr/night-custody or /Users/edr/JouleWise-measurement-*; never import or execute from /Users/edr/code/JouleWise; never read /Users/edr/code/wt-a65fb4fa-a291 (the implementer's tree).
Authority is unchanged: docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md plus 31-a291-v4-residual-rulings.md, and the ruled texts they quote in 15-coldgate-packet-a291-contract/. The review to act on is 37-a291-checker-opus-lens.md in that directory (an independent Opus lens that executed each finding in a /tmp copy). Read it in full; your original report is 32-a291-checker-seat-report.md.

1. CLAUSES.
   C1 (lens B1, INV-27/38) The planned drift lever follows 02d / RD-4 as installed: a split parent whose singles are partly terminal still has a planned position from its live, non-terminal placements. Fix `_derived` and the test fixture's `refresh_derived`, which copies the same misreading. Regression: the lens's R2 roster, whose planned lever is the value 02d gives (the lens computes 6.2); show the arithmetic in the test.
   C2 (lens B2, INV-26/45) `check_executed` uses each block's LIVE placement (the latest non-voided placement per 02d), never a voided earlier one. Regressions: executed values after a reschedule, and after a single advance.
   C3 (lens M1, INV-45) The executed lever counts partly counted parents exactly as 45/10 §Q4 and 31 X-5 define (a position from the counted items' windows). A parent is excluded only when it has no counted window. Regression with a partly counted parent.
   C4 Kill every one of the lens's surviving mutations, listed in record 37. For each: the test that now kills it, and proof by re-running that mutation in a /tmp copy.
   C5 Contract gaps 4 and 5 from report 32 are CONFIRMED by the magistrate as chosen; keep them. Update the CONTRACT GAPS list only if C1–C3 change a gap.
   C6 Re-verify every row: ROWS | NOT_CHECKABLE still equals the INV ids parsed from 02d.

2. ACCEPTANCE: `python3 -B -m unittest tests.test_scored_roster_checker` passes. NEVER `unittest discover`. `git status --porcelain` shows only WRITE_SCOPE paths. End your turn only after acceptance has run.

3. EVIDENCE DEMANDED (markdown body): C1–C6 mapped to file:line and test names; the mutation table (each mutation, killing test, re-run result); the test command and its result tail; "what the magistrate should double-check". Implementation-genre verdict keys only; JSON header under 8 KB.
