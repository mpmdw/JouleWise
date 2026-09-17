CUSTODY-PASS-MEMO-01 (kernel A223, P1: gates the next night arm) plus the fix-forward after PR #350 (post-merge review record 51).

**Fix-forward (hosted CI on main c9589525 was red on the Linux runner from two tests PR #350 introduced):** the interpreter-identity install test now changes the interpreter's bytes so the refusal rests on the content hash on every platform, with a unit test pinning the compared fields; the probe-timeout test waits for the stub's pid file. Also from the review: the bounded abort-session path now routes its typed refusals through the calibration refusal document (phase abort) so a custody timeout during window exhaustion is reported REFUSED / night_calibration_refused, not GO with a nonzero chain exit; two stale runbook sentences corrected (no separate pre-reserve readiness command on the chain; the driver hands the chain seven variables); installer usage strings list the probe flags.

**CUSTODY-PASS-MEMO-01:** the capture writer performed four whole-corpus custody verification passes per slot on one 120 s allowance while the arm-time probe measures one. An under-lease custody memo on the deadline — keyed on the physical ledger head digest and the (attempt, locator, artifact sha256) entry set, armed only after the writer lease is acquired, cleared on release and on every operation handoff, invalidated by a repair or another writer's append, never seeded by the pre-lease preflight — reduces a healthy slot to two passes (three when a repair moved the head). The install admission constant WRITER_CUSTODY_PASSES is set to 3, the honest worst case (repaired ledger or corrupt corpus), so a refusing slot reaches its typed calibration_ledger_custody_invalid rather than a timeout; with the 1.5 headroom factor the arm-time probe must show custody_elapsed_s at most 26.67 s. The writer's success receipt carries custody_passes. The contract states the accepted trade: the lease is an advisory lock on the ledger, not on governed bytes, so corruption arriving after the under-lease sweep is caught by the next slot's unmemoized preflight, not by that slot's readiness gate (D-161 threat model).

No measurement, instrument, gate, claim constant or census rule changes. Model note: the Codex quota was exhausted from 03:32 PDT, so every seat and refuter on this PR is Opus 5; cross-family diversity was not available and is stated here rather than implied.

## Gate ledger (D-118 / D-121)

| # | Gate item | Evidence |
| --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | RUN docs/process_traces/2026-09-16-activation-9853dd2b/55-custody-pass-memo-refuter-report.md |
| 2 | Paired distinct lenses: contract + execution (physics if measurement-adjacent) | RUN docs/process_traces/2026-09-16-activation-9853dd2b/55-custody-pass-memo-refuter-report.md |
| 3 | Lead-written FIX contract with dictated closure shapes; findings triaged and dispositioned, never silently applied | RUN docs/process_traces/2026-09-16-activation-9853dd2b/56-brief-memo-fix-round-1.md |
| 4 | Delta re-audit of every fix round | RUN docs/process_traces/2026-09-16-activation-9853dd2b/59-delta-reaudit-post-350-memo-report.md |
| 5 | Same-signature statement from every delta; a surviving class escalates to a consult, not round three | RUN docs/process_traces/2026-09-16-activation-9853dd2b/59-delta-reaudit-post-350-memo-report.md |
| 6 | Opus counter-review on the near-final head | RUN docs/process_traces/2026-09-16-activation-9853dd2b/59-delta-reaudit-post-350-memo-report.md |
| 7 | Apex Fable code-reading diff gate answering design-level questions; never skipped or downgraded | RUN docs/process_traces/2026-09-16-activation-9853dd2b/00-launch-record.md |
| 8 | Overbuild / merge-ability prune | RUN docs/process_traces/2026-09-16-activation-9853dd2b/57-memo-fix-round-1-opus-report.md |
| 9 | Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded | RUN docs/process_traces/2026-09-16-activation-9853dd2b/60-full-replay-int4.log.gz |
| 10 | Final-head fresh-eyes review after every post-review commit | RUN docs/process_traces/2026-09-16-activation-9853dd2b/59-delta-reaudit-post-350-memo-report.md |
| 11 | CI green on final head + post-merge cross-unit integration review | RUN docs/process_traces/2026-09-16-activation-9853dd2b/51-postmerge-cross-unit-review-report.md |
| 12 | Magistrate terminal review, full session context, of the exact merge candidate (final head sha); not delegable | RUN FINALSHA |

### Ledger notes
- Rows 1–2: the memo refuter (record 55) carried both lenses (contract reading plus execution with seven mutants, six killed, one survivor closed in fix round 1); the fix-forward's independent audit is the post-merge review (record 51) that dictated it, and the delta re-audit (record 59) re-applied every fix-forward defect.
- Row 4–6, 10: one Opus delta re-audit over the whole combined delta (fix-forward, memo, memo fix round) on the integration head; no other model family was available (Codex quota exhausted).
- Row 5: the memo fix round closed a new class (prose overclaim, an unenforced clearing clause, a sizing ruling); nothing survived two rounds.
- Row 7: record 00 addendum "09:45 PDT" — the magistrate's read of the memo cover/record/clear logic, the writer's arm and release sites, the abort refusal routing and the constants.
- Row 8: record 57 (fix round 1) removed the lease overclaims and the double-booked headroom rationale; no dead code added.
- Row 9: the replay ran on the integration head before the docs-only README guard fix (one sentence) was merged; the replay result and the docs test result are both recorded.
- Row 11: hosted CI does not run on pull requests here and is post-merge confirmation under Ed's 2026-09-16 ruling; the linked record is the post-merge cross-unit review of the previous merge that this PR closes (its blocker B1 and finding S7), and the local substitute (full replay + quick tier) ran on this head. The post-merge review of THIS merge is the successor's next item.
- Row 12: FINALSHA is the exact merge candidate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
