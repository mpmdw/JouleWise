# Post-merge cross-unit integration review — main a03a1b8a after PRs #326, #325, #327, #324 (ledger row 11)

SESSION_MODE: delegated
WRITE_SCOPE: []

Read-only review in the detached worktree you were started in (main
`a03a1b8a`). You may run tests (temp dirs allowed) but must not edit tracked
files; never touch `/Users/edr/code/JouleWise` (read-only use of its
`.venv/bin/python3` allowed), `/Users/edr/JouleWise-measurement-20260913-derivation`,
or `/Users/edr/night-custody`. `python3 -m unittest` only.

Four merges landed on main this morning over ace4cc3c: `git log --oneline
ace4cc3c..a03a1b8a`; the union diff is `git diff ace4cc3c..a03a1b8a`
(11 files). Lanes: #326 GIT-FIXTURE-MAINTENANCE-SWEEP-01 (git-init census +
identity_pins routing), #325 RECOVER-SESSION-REFUSAL-WINDOW-EXHAUSTED-01
(new RefusalCode + registry row + runbook paragraph), #327
ARM-READINESS-FIXTURE-CLOCK-ORIGIN-01 (fixture clock origin), #324
FIXTURE-SENTINEL-CONTROLLER-01 (controller regression stress scoping).
Each was gated alone (records under
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`,
replay 4 record 58 on the pre-merge integration tree 318b17f6).

Cross-unit questions (answer with file:line and executed evidence):
1. Is the merged main byte-identical in the 11 files to the integration
   tree 318b17f6 the replay ran on? `git diff 318b17f6..a03a1b8a --stat`
   must be empty for tracked code/docs; paste.
2. Cross-PR seams: run #326's census over the merged `tests/` (import
   `_git_init_violations` from `tests.test_git_fixture_maintenance`) → must
   be `{}`; run `tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene`
   once; paste.
3. #325 × everything: does any consumer enumerate `RefusalCode` by count or
   position such that the new member shifts it (goldens, JSON fixtures,
   `analysis_engine`)? grep + run `tests.test_calibration_exits.RefusalInventoryTests`
   once; paste.
4. #324 × #327 host-state family: both cure host-state fixture classes
   (timing; uptime). Is there a shared helper that should now own both
   policies, or are they correctly separate? One paragraph; no edits.
5. Docs: `python3 scripts/gen_state.py --check` and any docs-freshness test
   that parses the runbook or contracts (`tests.test_docs_freshness` if it
   exists) once; paste result lines.
6. Verdict: CLEAN / FOLLOW-UP NEEDED (name the follow-up rows) / BLOCKER
   (name the defect; the magistrate would revert).

Report (claude-codex-report/v1, genre review): findings tiered
blocker / should-fix / nit; the verdict line; under 6000 bytes.
