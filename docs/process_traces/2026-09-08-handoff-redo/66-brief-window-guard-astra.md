WRITE_SCOPE: ["scripts/window_status.sh","tests/test_window_status_guard.py"]

# Seat brief — WINDOW-STATUS-GUARD-CENSUS-01 (gpt-6-astra, medium)
`scripts/window_status.sh:42` refuses with "REFUSING: a measurement process is running" when `ps aux | grep -E
"run_campaign|window-chain"` matches ANY process; during a 4-worker parallel test replay a sibling shard's
`run_campaign` dry-run test process matched, so `tests/test_window_status_guard.py::test_present_sentinel_writes_status_without_git_publication`
failed (trace docs/process_traces/2026-09-08-handoff-redo/43-full-replay-f55febc9-pr297.md item 3). Cure: the guard
must recognise a REAL measurement chain — read how a night chain / campaign actually runs (scripts/run_night.py,
scripts/run_campaign.py, the chain's process shape: e.g. `scripts/run_campaign.py` invoked from a night custody
root, or a `window-chain` marker file / pid file if one exists) and match on that (pid-file or argv pattern that
excludes `python -m unittest`, `--dry-run`, and test fixtures), OR have the test isolate the process view by
injecting the census command (an env override for the ps command used by the guard, defaulting to the real one).
Prefer the first if a reliable discriminator exists; do both if cheap. Regressions: (a) a sibling process whose
argv contains `run_campaign` under `unittest`/`--dry-run` must NOT trigger the refusal; (b) a real chain shape
MUST; (c) the existing sentinel tests keep passing. Acceptance = tests.test_window_status_guard to a log with rc;
`bash -n scripts/window_status.sh`. Never the repository-wide suite; no `git commit`; header < 8192 bytes; genre
implementation verdict keys; body = the discriminator chosen and why, counterfactuals, tails, rc.
