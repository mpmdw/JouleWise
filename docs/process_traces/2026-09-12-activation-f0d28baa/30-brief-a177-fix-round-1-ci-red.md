# Fix-round brief — FIXTURE-SENTINEL-CONTROLLER-01 round 1: the stressed regression is RED on hosted CI (both interpreters), green at the bench

WRITE_SCOPE: ["tests/test_controller.py","tests/test_run_campaign.py","tests/test_idle_admission.py","tests/fixtures/fake_powermetrics_process.py","tests/fixtures/**"]

Root-cause-then-cure seat in the linked worktree you were started in (branch
`fix/2026-09-12-fixture-sentinel-controller`, HEAD `c85a171d`, one commit over
origin/main `ace4cc3c`; PR #324). TEST AND FIXTURE FILES ONLY (kernel fence);
production code is out of scope — if production must change, stop with
NEEDS_RULING. Never move HEAD, never push, never touch
`/Users/edr/code/JouleWise` or `/Users/edr/JouleWise-measurement-20260913-derivation`
(a measurement night is armed there; both fenced). `python3 -m unittest` only
(no pytest on this host); the repo venv interpreter is
`/Users/edr/code/JouleWise/.venv/bin/python3` (3.13) — read-only use of that
binary is allowed; the system `python3` is 3.14.

## The defect (new signature: CI-red, bench-green)

Hosted CI (GitHub `ci.yml`, run 34690082410) fails
`tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
IDENTICALLY on Python 3.11 and 3.14 (shard 3, Linux runners):

```
File "tests/test_controller.py", line 1646, in test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce
    self.assertEqual(summary.status, RunStatus.SUCCEEDED)
AssertionError: <RunStatus.FAILED: 'failed'> != <RunStatus.SUCCEEDED: 'succeeded'>
Ran 74 tests in 47.567s
```

At the bench the same module is green (magistrate, venv 3.13: Ran 74 in
80.669s OK; seat 04: 74 OK; Opus 25: 74 OK). The module took 47 s in CI, so
the runner is not slower overall. Before c85a171d the test was CI-green and
locally flaky (root-cause record
`docs/process_traces/2026-09-10-activation-96bfeca7/19-rootcause-controller-idle-drift-local-astra-report.md`).
The c85a171d change (read `git show c85a171d`) added: the adapter `_command`
override appending `--no-sleep` for bounded captures, and — in the test — a
`patch.dict(os.environ, {"FAKE_POWERMETRICS_SLEEP_SCALE": "3.5"})` around the
WHOLE production run, so the continuous (paced) captures also sleep 3.5×
longer per sample on the host.

## Work

1. Make the failure self-describing FIRST: the assertion at ~:1646 must carry
   `summary`'s failure reason / status reason and the relevant metadata
   (whatever `RunSummary` exposes — find it) so the next CI run explains
   itself. This edit stays regardless of the cure.
2. Reproduce locally. Hypotheses to test, in order, each with a command and
   its result line pasted:
   a. The 3.5× scale on CONTINUOUS captures starves admission or the measured
      window (fewer samples per admission slice on Linux `time.sleep`
      granularity / CI CPU quota): run the test with
      `FAKE_POWERMETRICS_SLEEP_SCALE` at 3.5, 6, 10 and record status +
      reason at each; find the smallest scale that fails at the bench and
      the reason it reports. If the reason is an admission/idle-baseline
      refusal (not the post-idle capture), the stress is applied to the
      wrong capture.
   b. Consult 87's campaign regression (`tests/test_run_campaign.py`,
      `test_retry_member_survives_fixture_sleep_slack` or its successor)
      passes in CI under the same ≥3.5× floor — diff how IT applies the
      stress vs how the controller test does (scope of the env patch, which
      captures are bounded, the post-count expectation).
   c. Linux vs macOS fixture behaviour in `tests/fixtures/fake_powermetrics_process.py`
      (anything platform-dependent: `os.sched_*`, signal handling, `-b`
      baseline, `--no-sleep` parsing).
3. Cure in the TEST/FIXTURE layer only: the regression must stay
   defect-shaped for report 19's defect (post-idle capture timeout →
   unknown drift → strict validation mismatch) — i.e. removing the bounded
   `--no-sleep` policy must still make it FAIL — while the stress must not
   make the continuous path fail on a hosted runner. Likely shape: apply the
   sleep stress only to the bounded sentinel path (a fixture flag or a
   scoped env var the adapter override sets for `count is not None`), or
   lower the continuous stress to what consult 87 actually uses. Say which
   and why; cite consult 87 lines.
4. Killed cut after the cure: revert the `--no-sleep` policy in memory or by
   a temporary edit (restore by hash) → regression FAILS with the report-19
   signature; restore → PASS. Paste both result lines.
5. Verify: `python3 -B -m unittest tests.test_controller -q` with BOTH
   interpreters (venv 3.13 and system 3.14), and `tests.test_run_campaign
   tests.test_idle_admission` once with the venv; paste result lines.
   `git diff --check`. Do NOT commit; report `git status --short` and
   `git diff --stat`.

## Report (claude-codex-report/v1 envelope per --genre)
Root cause with the reproducing scale and reason string; the cure and why it
keeps the defect shape; killed-cut evidence; per-interpreter results; any
NEEDS_SCOPE/NEEDS_RULING; anything unsure. Under 8000 bytes.
