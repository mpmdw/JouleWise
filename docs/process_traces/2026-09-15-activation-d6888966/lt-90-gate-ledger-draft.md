# lt-90 — Twelve-row gate ledger DRAFT, INSTALL-WINDOWS-MULTI-01

Draft only. **The lieutenant did not open a PR and did not merge.** Rows the
lieutenant could not satisfy are marked OPEN with the reason; rows 6, 7, 11 and
12 are not the lieutenant's to fill by construction.

Final integration head at hand-back: **`df86cee6`** on
`int/2026-09-15-install-windows` (pushed). **This head is NOT merge-ready**: the
FIX-1 blocker is unclosed (record `lt-04` F1) and the lane is in a CONSULT
request (`lt-05`).

Evidence paths are repo-relative and all resolve on the bookkeeping branch
`bookkeeping/2026-09-15-activation-d6888966-lt`. Per the template, every row is
`RUN <repo-relative-path>` or `RUN <sha>`, plain text, no anchors.

| # | Gate item | Evidence | State |
| --- | --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-02-refuter-round-1.md | SATISFIED — two fresh Astra xhigh seats, neither an author; plus the fresh delta auditor in lt-04 |
| 2 | Paired distinct lenses: contract + execution | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-02-refuter-round-1.md | SATISFIED — contract lens (read-only, wt-ref-iw-contract) and execution lens (wt-ref-iw-execution), separate worktrees, blind to each other, both at 7a512827 |
| 3 | Lead-written FIX contract with dictated closure shapes; findings triaged and dispositioned | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-03-fix-round-1.md | SATISFIED — the disposition table carries all eleven items including the one NOT fixed; brief at /tmp/magistrate-d6888966/brief-04-fix-round-1.md |
| 4 | Delta re-audit of every fix round | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-04-delta-re-audit.md | SATISFIED — fresh auditor over both fix commits, with original-defect reproduction and isolated-reversion checks per item |
| 5 | Same-signature statement from every delta; a surviving class escalates to a consult, not round three | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-05-consult-request.md | SATISFIED AND FIRED — the delta answered YES on two classes; the lieutenant stopped and requested a consult instead of launching round 2 |
| 6 | Opus counter-review on the near-final head | NOT-RUN | OPEN — the lieutenant IS the Opus seat here and directed the fix rounds, so it cannot also be the independent Opus counter-review. Needs a fresh Opus seat on the post-consult head |
| 7 | Apex Fable code-reading diff gate answering design-level questions | NOT-RUN | OPEN — magistrate-owned, not delegable; must cover the acceptance clause (c) narrowing and the FIX-1 disposition |
| 8 | Overbuild / merge-ability prune | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-04-delta-re-audit.md | PARTIAL — the delta verified no ruled-out design shipped, no new ceiling constant, the v2 schema untouched, the whole design-§6 untouched list byte-identical, and only three pre-existing test lines changed. A deliberate prune pass over the new code was NOT run |
| 9 | Lead unpiped full-suite replay on the integration tree, exact tail recorded | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-91-replay-and-pr-body.md | see lt-91 — lieutenant-run `python3 scripts/shard_tests.py --workers 4 --split` in wt-integ-install-windows at df86cee6; tail pasted there |
| 10 | Final-head fresh-eyes review after every post-review commit | NOT-RUN | OPEN — the delta covered ffc3cafc and df86cee6, which are the only post-review commits so far; it must be re-run on whatever head the consult produces |
| 11 | CI green on final head + post-merge cross-unit integration review | NOT-RUN | OPEN — no PR was opened, so no CI has run |
| 12 | Magistrate terminal review, full session context, of the exact merge candidate | NOT-RUN | OPEN — not delegable; and the current head is not a merge candidate while the blocker is open |

## Why rows 6, 7, 11, 12 are OPEN rather than attempted

Row 6 would be self-review: the lieutenant wrote the FIX contract and the FIX-5
ruling. Row 7 and row 12 are reserved to the magistrate by the gate text. Row 11
requires a PR, which the lieutenant is directed not to open. Row 10 is satisfied
for today's commits but cannot be closed while further commits are expected from
the consult.

## Commit series on `int/2026-09-15-install-windows`

| Sha | What |
|---|---|
| `1cc8db30` | inherited integration head (seat A + main + seat D) |
| `5124de47` | merge of `origin/main` `e42949dc` (trace/bookkeeping only) — sets the refuters' diff base |
| `7a512827` | lt-01 docs↔code reconciliation |
| `ffc3cafc` | fix round 1 (FIX-1..4, 6..10) |
| `df86cee6` | FIX-5 under the lieutenant's ruling |
