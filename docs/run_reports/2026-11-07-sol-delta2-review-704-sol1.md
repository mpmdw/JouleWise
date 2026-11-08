# PR #704 delta-2 review — Sol seat sol1

Branch: `b5rel/2026-11-08-sol-delta2-704-sol1`.
Reviewed head: `1313698017e8277e4791b368eb8fde0d94748b1e`, base `bea480f29`.
User-authorized work: independent synthetic review, new witnesses, reports and
local commits only; no push. The existing branch already had the requested name
and the starting worktree was clean.

Verdict: **ADMIT_WITH_FIXES**. The [review](../analysis/b5/reviews/sol-delta2-review-704-sol1.md)
owns the findings, evidence, test commands/results and limitations. It finds a
remaining false-agreement path from assuming an unprinted bound's identity and
a remaining metadata false-disagreement path for legitimate transport refusal.
Original witnesses pass; new witnesses retain three explicit expected failures.

Process: Mission M0 and the review/orchestration instructions were read. No
active stop card was present. The user's sealed-data, no-network, targeted-test
and coordination-state exclusions superseded the ordinary state-update/full-suite
checklist. No `RUN_STATE.md`, `TASK_QUEUE.md`, state kernel or generator test was
edited. No additional agent or cross-model consultation was used. The lead owns
finding dispositions, final verification, both-seat adjudication and all live
release/unseal authority. No peer advice or unreviewed fix was landed.

Changed files: the linked review, this run report, and
`tests/independent_recompute/test_sol_delta2_review_704_sol1.py`. Production code,
raw evidence and run bundles are unchanged. Commits are local on the named
branch; the handoff message gives their object ids.

Verification: 256 existing targeted tests passed. The new module has five
passing tests and three expected failures, checked at their final assertions.
`nice` could not change priority. A short witness-inspection process briefly
overlapped the targeted census test; the review records that deviation.
Python 3.11 is unavailable; the lead/CI must check it. No new native MLX check
is necessary. No full suite or real analysis pipeline ran.

Final checks: `JW_B5_SYNTHETIC_ONLY=1 nice -n 10 python3.13 -B -m compileall -q
joulewise tests scripts/compare_b5_recompute.py scripts/independent_recompute_b5.py
scripts/release_b5.py` passed. The final witness module rerun passed five tests
with the same three expected failures (8 tests, 2.733 s); the final absolute-bound
witness was rechecked to fail at its last assertion. Diff whitespace and the
staged three-file scope were checked before commit. The recompute hash still
matches the brief. Python 3.11 was probed and is not installed.

Next: lead disposition of R704-DELTA2-S1/S2, exit-code clarification, production
fixes and fresh independent delta review. Ed's unseal OK is still required.
