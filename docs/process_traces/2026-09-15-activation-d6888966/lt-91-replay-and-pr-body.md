# lt-91 — Lead replay at the final head, and the PR body draft

## Replay (gate row 9) — lieutenant-run, not delegated

Run by the lieutenant itself in the INTEGRATION worktree
`/Users/edr/code/JouleWise-wt-integ-install-windows` (not a stale branch, not a
seat's sandbox) at head **`df86cee6`**, working tree clean. `scripts/shard_tests.py`
exists on this tree, so the sharded runner was used as directed.

```
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 scripts/shard_tests.py --workers 4 --split
```

Started 07:56:28 PDT, finished 08:50:55 PDT (clock reads; ~54 min wall, sharing
the machine with the delta auditor and with the magistrate's own PR #339
review). Exact tail:

```
MODULE PASS tests.test_workload_profile tests=7 failures=0 errors=0 skipped=0 seconds=0.002
SHARD SUMMARY index=4/4 modules=61 tests=1755 failures=0 errors=0 skipped=3 result=PASS
WORKERS SUMMARY shards=4 modules=233 tests=6094 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
EXIT=0
```

**233 modules, 6094 tests, 0 failures, 0 errors, 109 skipped, PASS, exit 0.**

This is the whole-suite evidence, and it is genuinely green. It does NOT make
the head merge-ready: the FIX-1 blocker is unclosed and has no failing test,
because the defect is reachable only through a fake-launchctl sequence in which
the clock advances DURING the bootstrap — the delta reproduced it with an
executed probe, not with a suite test. A green suite is necessary and not
sufficient, which is precisely the standing rule.

## PR body draft — NOT opened; the magistrate opens and merges

The lieutenant did not run `gh pr create`. The body below follows
`.github/pull_request_template.md`, with the twelve-row ledger from `lt-90`.
**Rows 6, 7, 10, 11 and 12 are NOT-RUN and row 3's lane is unfinished**, so this
body is a draft for a head that does not yet exist — whatever the consult
produces. It is recorded now so the magistrate is not reconstructing it later.

---

### Gate ledger (D-118 / D-121)

| # | Gate item | Evidence |
| --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-02-refuter-round-1.md |
| 2 | Paired distinct lenses: contract + execution (physics if measurement-adjacent) | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-02-refuter-round-1.md |
| 3 | Lead-written FIX contract with dictated closure shapes; findings triaged and dispositioned, never silently applied | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-03-fix-round-1.md |
| 4 | Delta re-audit of every fix round | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-04-delta-re-audit.md |
| 5 | Same-signature statement from every delta; a surviving class escalates to a consult, not round three | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-05-consult-request.md |
| 6 | Opus counter-review on the near-final head | NOT-RUN |
| 7 | Apex Fable code-reading diff gate answering design-level questions; never skipped or downgraded | NOT-RUN |
| 8 | Overbuild / merge-ability prune | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-04-delta-re-audit.md |
| 9 | Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-91-replay-and-pr-body.md |
| 10 | Final-head fresh-eyes review after every post-review commit | NOT-RUN |
| 11 | CI green on final head + post-merge cross-unit integration review | NOT-RUN |
| 12 | Magistrate terminal review, full session context, of the exact merge candidate (final head sha); not delegable | NOT-RUN |

### Summary

INSTALL-WINDOWS-MULTI-01 (kernel agent lane, rank 0; D-180 cl.1 and D-181 cl.1).
The night schedule can name several bounded install spans per day instead of the
single fixed 03:00-06:30 block; a plan's `t0` may sit at any clock time, with the
launchd calendar fields derived from the plan rather than a fixed belt; the
runtime dead-man is derived per plan in one home, `deadman_epoch(plan)` in
`scripts/run_night.py`; results and traces are keyed by `plan_id`, so a second
plan may be armed as soon as the previous harvest is done. The v2 plan schema is
unchanged: every new quantity is a pure function of existing keys.

Implementation: seat A (code) and seat D (docs) in parallel, then a docs-to-code
reconciliation, then two refuters with distinct lenses, one fix round of ten
dictated items, one ruling, and a delta re-audit. The shipped `INSTALL_SPANS`
default is the single whole-day span `(("00:00","24:00"),)`: this lane ships the
MECHANISM, and populating a narrower schedule is Ed's call, not this activation's.

**Open blocker (do not merge as-is):** `scripts/install_night_agent.sh:348` — the
final dead-man bootstrap can still complete after the selected install span has
closed, exit 0, both agents loaded. The fix round closed the earlier call sites;
the delta found this one. Two rounds with the same signature triggered the
standing escalation rule, so the lane is in a CONSULT rather than a third fix
round. Latent under the shipped whole-day default.

**Flagged for adjudication:** acceptance clause (c) "t0 may be any clock time"
now reads "any whole minute that occurs exactly once in local time"
(`plan_t0_not_minute_aligned`, `plan_t0_ambiguous_local_time`); and runbook §3's
FAIL-route distinct-calendar-days pre-registration constraint, left byte-identical
and judged design-bearing by two independent reviewers.

### Verification

Lead replay at `df86cee6` in the integration worktree:
`python3 scripts/shard_tests.py --workers 4 --split` →
`WORKERS SUMMARY shards=4 modules=233 tests=6094 failures=0 errors=0 skipped=109 failed_shards=none result=PASS`, exit 0.

Delta auditor, seven target modules separately: 411 tests, all OK, no ERROR,
WARNING or ResourceWarning. Mutation evidence: the 17 enumerated previously-
surviving mutants are all RED at this head; a 54-mutation sweep of the new code
left 22 survivors, enumerated with counterfactuals in `lt-04` (finding F4).

Runbook §3 byte-identical, SHA-256
`71337a836df21f1f3668bcb46e7ffe6e487a247f7ce51368b459b9516612072b`.

---

## Worktrees left behind for the magistrate

- `/Users/edr/code/JouleWise-wt-integ-install-windows` — branch `int/2026-09-15-install-windows` at `df86cee6`, clean, pushed.
- `/Users/edr/code/JouleWise-wt-ref-iw-contract` — detached at `df86cee6`; hosted the contract refuter and then the delta auditor.
- `/Users/edr/code/JouleWise-wt-ref-iw-execution` — detached at `7a512827`; hosted the execution refuter, which ended with `git status --porcelain` empty.

None were merged, none were pushed except the int branch, and nothing was
committed from the two refuter worktrees.
