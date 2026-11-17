# PR #799 round 9 desk repair

The user selected the four cold-review findings ahead of the ordinary [AGENT] queue. Mission M0 found no active stop card and a clean PR #799 worktree at `69931e529`. The governing desk conditions are RL-172(c) and the cadence desk format. The refusal came from `COLD-REVIEW.md` in the round 9 review directory.

F4 reproduced against a signed synthetic bundle and an existing signed verdict record. Git's history-prefix lookup and full enumeration now check exit status, diagnostics and ref output before replay. An incomplete listing or an enumeration that loses the ref seen by the prefix probe produces `DESK_UNAUTHENTICATED` and `desk_final=false`. The authenticated bundle retains its verified transport identity.

`SignedTransport.test_failed_history_listing_refuses_signed_desk_final` reproduced the stale behavior on `69931e529` and passes with the fix. The guarded cadence suite passed 247 tests. The user narrowed verification to the cadence suites and excluded all 12 cases in `test_launch_cadence_span.py` on each branch because those cases signal live fixture processes. The local runner rejects nonzero process signals. No phase exit-checklist item closed.

PR #800 inherits this commit through its existing linear stack. Fresh admission and live gates remain lead-owned.
