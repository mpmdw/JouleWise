SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Refuter — FIXTURE-TIMEOUT-WALLCLOCK-01 (PR #310), EXECUTION lens (gpt-6-astra, high, genre review, read-only)

Worktree: this one, detached at 112e86e4 (branch head). Diff under review: `git diff 21e31107..112e86e4` (tests/fixtures/fake_powermetrics_process.py, tests/test_run_campaign.py, tests/test_idle_admission.py). Seat report: /Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/74-seat-fixture-timeout-wallclock-astra-report.md; brief 73; lane authority cold gate 44 C5 / refuter 45 (same directory); bench record 42 (+addendum).
Refute, by execution (this sandbox is read-only: no writes outside /dev/null; drive the fixture module in-process with patched argv/env as the seat's test does):
1. Counterfactual pair: show the four affected scenarios' outcome under FAKE_POWERMETRICS_SLEEP_SCALE=3.5 with the SLEEPING fixture (bypass --no-sleep in-memory by patching the helper's `_command` to not append it) vs with --no-sleep; the sleeping run must produce post_idle_unavailable via a real TimeoutExpired at 17.5 s. Run `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= FAKE_POWERMETRICS_SLEEP_SCALE=3.5 python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_member_survives_fixture_sleep_slack` and the four named tests at scale 3.5 and at scale 1; paste tails.
2. Production untouched: `git diff 21e31107..112e86e4 --stat -- joulewise scripts` must be empty; confirm `_capture_timeout_s` unchanged and that no production module reads FAKE_POWERMETRICS_SLEEP_SCALE or --no-sleep (grep joulewise scripts).
3. Synthetic timestamps: prove no derived value that the paper or the strict validator consumes changes between paced and --no-sleep sentinels beyond what the seat's identity assertion covers — inspect measure_post_run_idle and derive_idle_drift_evidence inputs; name any field that DOES differ (e.g. wall-clock timestamps in the raw plist) and whether any consumer reads it.
4. D-078 causal constraint: the fixture docstring says record 0's window end must follow the spawn by elapsed_ns; with --no-sleep the first record's synthetic timestamp is native_start + interval — find the validator that enforces the constraint (grep joulewise for D-078 / causal / spawn) and say whether bounded sentinels are subject to it and whether --no-sleep could trip or bypass it.
5. Mutation: invert the --no-sleep predicate in an in-memory copy of the fixture (always sleep) and confirm the new regression FAILS; then restore.
6. Same-signature statement and anything the seat report over-states.
Read-only; no edits. Report claude-codex-report/v1, genre review, header < 8192 bytes (verdict = {counts, findings} only); body = disposition per item with command tails.
