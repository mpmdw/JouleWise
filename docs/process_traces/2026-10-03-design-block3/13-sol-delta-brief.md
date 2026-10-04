# Delta check: PR #465 at 68bf2301 (after your review of ccca0b3c returned FAIL on F1)

Worktree: `/Users/edr/code/JouleWise-wt-db3-review`, detached at `68bf2301`. Read-only; same prohibitions as your review brief (no powermetrics/sudo/launchctl/model; no summary/counts/selection files under the night roots; no PR bodies of #461-#464). Interpreter `/Users/edr/code/JouleWise/.venv/bin/python -B` from the worktree root; scratch `/tmp/db3-delta/`.

Read `git diff ccca0b3c..68bf2301`. It answers your F1 and two findings of a parallel cold Fable final pass:
1. Sizing: `RetryBackoffClockAnchorTests` now budgets the worst-case retried stream for the longest member (2 x 104 s idle attempts, as observed in block 2's completed members; 300 s wait; 45 s guards; 2 x 10 s 4096-token prefills; 516 tokens at 5 tok/s; 6 s) = 683 s, and uses block 2's observed drift (about 3.2 ppm, all twelve completed members) and widest observed anchor half-width (2.31 ms), adding the half-width difference to the synthetic anchor. Bound about 4.5 ms < 5 ms; 600 s exceeds. The 7.24-7.60 ppm in the `uncertainty_evidence.py` comment are older captures; the Fable pass read block 2's member metadata for the 3.2 ppm and 2.31 ms figures.
2. Harvest: the inventory-bound policy must be production profile, bracket required, admission enabled and aborting; otherwise REFUSED `campaign_policy_not_claim_grade`.
3. A test label fix.

Check: (a) is the new budget honest and conservative for both longest-rung members (re-derive each term from code; flag any term still missing, e.g. model load inside the sampler window, thermal probes, teardown); (b) at 683 s, at what drift does the widest-half-width bound reach 5 ms; (c) does the harvest guard refuse exactly the non-claim-grade policies and still pass both block policies (run `tests.test_harvest_g2a_window`; one mutation: delete the guard and show a test fails); (d) run `tests.test_controller_retry_backoff tests.test_gen_g2a_window tests.test_harvest_g2a_window tests.test_schemas`.

Output: first line `DELTA: PASS` or `DELTA: FAIL`, findings each {severity, file:line, claim, evidence}. ≤ 600 words.

## Write scope (exhaustive)

WRITE_SCOPE: []
