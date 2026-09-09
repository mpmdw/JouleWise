# PR #309 acceptance under cold gate 44 Q2 (A1–A6) — magistrate record, activation 2145630c

Integration tree: `fix/2026-09-09-night-gate-stub-chain` @ `dd135364fc607dbb628a30da1df708a6425f6535` = 5db38b58 + merge of origin/main
`d7f5d5d9` (PR #308 merge) + `0d9881ef` (README blurb); `git merge-base --is-ancestor origin/main HEAD` true at replay start.

- A2 (pathspec + import independence): PR files = {docs/contracts/pack_night_go_receipt.md, joulewise/night_gate.py,
  scripts/run_night.py, tests/test_night_gate.py, tests/test_run_night.py} (`git diff --name-only 83ab38ed..5db38b58`); failing path =
  {tests/test_run_campaign.py, joulewise/adapters/powermetrics.py, joulewise/uncertainty_evidence.py, joulewise/controller.py,
  joulewise/cli.py, scripts/run_campaign.py, tests/fixtures/fake_powermetrics_process.py}; intersection ∅. Import check at the
  integration head: `grep -ln "night_gate\|run_night" joulewise/run_campaign.py joulewise/controller.py joulewise/cli.py
  joulewise/adapters/powermetrics.py joulewise/uncertainty_evidence.py scripts/run_campaign.py` → no match (none of the failing-path
  modules imports night_gate or run_night).
- A3 (same four on the merge base, same session): class alone at 5db38b58 (= main 83ab38ed + this PR's four files, run_campaign path
  untouched) `Ran 71 tests / FAILED (failures=4)` (39-idle-admission-alone-5db38b58.log); at main 83ab38ed the single-test diagnostic
  failed identically (42-bench-diagnostic-idle-admission.out) and the cold judge re-ran it (44 §Probes). Three later class re-runs on
  5d13d0e6 (docs-only over main) stayed red 4/4/3 (39b logs).
- A1 (replay alone on the integration tree): REPLAY_RESULT
- A4 (covering tests on the integration tree, not the branch): A4_RESULT
- A5 (CI green on the final head): A5_RESULT
- A6 (addendum obligation + file 31 addendum): 31's addendum is committed (PR #308 merge); the class re-run after powermode 0 or the
  FIXTURE-TIMEOUT-WALLCLOCK-01 cure is owed as a dated addendum to this PR's ledger row 9 as well.
- Refuter 45's stricter position (rc 0 with bounded retries) is recorded as dissent; the magistrate applies the judge's A1 door.
