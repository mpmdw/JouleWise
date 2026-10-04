# Executing review: PR #465, lane G2A-B3-RETRY-BACKOFF-01 (delayed idle-admission retry for measurement block 3)

Worktree: `/Users/edr/code/JouleWise-wt-db3-review`, detached at `ccca0b3c` (branch `feat/2026-10-03-g2a-b3-retry-backoff`; parent main `871a43f6`). Read-only review: do not edit tracked files and do not commit. Interpreter: `/Users/edr/code/JouleWise/.venv/bin/python -B`, run from the worktree root (so its code is imported). Scratch: `/tmp/db3-review/` only. Never run powermetrics, sudo, launchctl or a model; never read `summary*.json`, `counts*.json` or `selection*.json` under `/Users/edr/night-g2a`, `/Users/edr/night-custody` or `/Users/edr/night-archive`; do not read GitHub PR bodies of #461-#464.

## What the change is for

Block 2 of the G2-a prefill probe lost its recovery window when one member's idle admission was rejected twice inside a ~6-minute macOS maintenance burst; attempt 2 starts ~0.5 s after attempt 1 (`joulewise/controller.py` idle-baseline stage). Block 3 adds a wait before the one retry. Requirements:
1. `IdleAdmissionPolicy.retry_backoff_s`: optional, finite, 0..1800, not bool/str/None; absent = 0. Production policy bytes unchanged; `CampaignPolicy.to_dict()` and any digest identical to before at 0.
2. Controller: wait only after a rejected attempt 1 whose post-capture guard passed; then the unchanged `before_attempt_2` guard, attempt 2, `after_attempt_2` guard, abort on a second rejection with the unchanged reason; promotion of attempt 2 unchanged; the wait recorded under `environment_admission.retry_backoff`, never in `attempts` or `guard_observations`.
3. Block-3 policy file = production + backoff 300 + its own `policy_id`; nothing else differs.
4. The emitted G2-a chain exports that policy exactly once; the span adds 4 x (backoff + idle + 30) s; `--check` passes.
5. Harvest and `check_harvest_inputs` use the policy the window's inventory binds (inside `configs/campaign_policies/`, sha checked); block-2-style archives still harvest.
6. The 300 s value: the adapter keeps ONE sampler from before attempt 1 through the measured window, and the v3 clock anchor fits every record of that stream; at the 7.24-7.60 ppm network-time-OFF drift on record (`joulewise/uncertainty_evidence.py` comments) a retried member's stream must stay inside the 5 ms cap.

## Execute (an executing lens: run code, do not only read it)

- `git diff 871a43f6..ccca0b3c`; run every touched test module plus `tests.test_custody_mode_inventory`, `tests.test_controller`, `tests.test_environment_admission` (if present), `tests.test_whole_window` (if present).
- Mutation probes in a scratch copy (`cp -R` the worktree to `/tmp/db3-review/mut-N`, never edit the review worktree): (a) remove the sleep; (b) sleep before the `after_attempt_1` guard instead of after; (c) apply the wait when attempt 1 is admitted; (d) drop the `to_dict` zero-omission; (e) make the harvest use the production path again; (f) set the block-3 backoff to 600. For each, say whether some test fails. A surviving mutation is a finding.
- Independently check claim 6: estimate a retried member's real stream (attempt 1 idle 75 s + backoff + attempt 2 idle 75 s + guards + warmup + measured window + post dwell; read the producer configs and the controller for each term) for small and large members at the longest rung, and run the v3 anchor (`derive_powermetrics_anchor_v3`) on synthetic records at 7.24, 7.60 and 9.0 ppm for those lengths. Is the 60 s allowance in `RetryBackoffClockAnchorTests.retried_stream_s` honest?
- Look for anything that reads the whole member stream and could refuse a long one (strict validator in `joulewise/cli.py`, `joulewise/whole_window.py`, `joulewise/environment_admission.py` freshness limits, salvage) and confirm each by test or line.

## Output

A `claude-codex-report/v1` review with first line `REVIEW: PASS` or `REVIEW: FAIL`, findings each {severity BLOCKER|MAJOR|MINOR|NIT, file:line, claim, evidence (command and result)}, the mutation table, and the stream-length table. ≤ 1200 words.

## Write scope (exhaustive)

WRITE_SCOPE: []
