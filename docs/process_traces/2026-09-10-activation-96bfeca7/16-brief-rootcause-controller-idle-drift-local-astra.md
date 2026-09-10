SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Root cause — tests.test_controller::test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce FAILS on this Mac at main 078a13a4 while GitHub CI at the same head is green (gpt-6-astra, high, genre root_cause, read-only)

Observed at the bench (clean worktree at 078a13a4, `python3` = Homebrew 3.14.7 on macOS, 2026-09-10 ~05:05 PDT, epoch ≈1789040700):

```text
First list contains 2 additional elements.
'strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation'
'strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation'
Ran 73 tests in 90.454s  FAILED (failures=1)
```

GitHub Actions run for main `078a13a4` (2026-09-10T11:14Z, ubuntu, Python 3.11): success. The same test was reported failing by an implementation seat with the four repaired modules restored to HEAD bytes, so it is independent of today's diff.

Deliver:
1. The exact assertion site (`tests/test_controller.py:1599` onward) and the production predicate(s) that emit those two strict reasons (`joulewise/uncertainty_evidence.py`, `joulewise/reduce.py`, `joulewise/adapters/powermetrics.py` — quote the lines). What inputs does the fixture supply for the pre/post raw sentinel and the effective-drift derivation, and which value differs between this Mac and CI? Candidate classes to test by reading: (a) wall-clock/epoch dependence (fixture epochs vs `time.time()` now; ULP of the current epoch; the "Mac-calibrated test assumption" class seen in PRs #310/#311 — consult `docs/process_traces/2026-09-09-rehearsal-harvest/87-consult-fixture-regression-portability-astra-report.md` and `99-rootcause-arm-load-ci-astra-report.md`); (b) Python 3.14 vs 3.11 numerics/`statistics`/`fractions`/dict-ordering differences; (c) host facts read from the machine (uptime, boot UUID, `powermetrics` presence, `/Users/edr` paths, locale/timezone); (d) a fixture file under `tests/fixtures/` whose bytes differ locally (untracked/modified — check `git status` in the worktree you run in). Run the single test with extra diagnostics if that helps (`python3 -m unittest tests.test_controller -k retry_promotes`), and, if cheap, once under `/opt/homebrew/bin/python3.13` (the measurement venv interpreter is 3.13.1) to split (b) from the rest.
2. Whether the same mechanism can affect a REAL bundle reduced on this Mac (i.e., is it a test-fixture artefact or a production strict-reduce defect that would void a G2-a member), with the reasoning.
3. Minimal cure (do not implement): fixture-side if (a)/(b)/(d), production-side if it is real; the defect-shaped regression.
4. Same-signature statement relative to the fixture-portability class (consult 87) — is this the third instance? The lead decides escalation.

Read-only; no edits; no full suite. Report claude-codex-report/v1, genre root_cause (verdict.cause / verdict.remediation), header < 8192 bytes.
