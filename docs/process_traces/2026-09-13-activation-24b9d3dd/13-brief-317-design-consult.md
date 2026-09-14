# Design consult brief — CI-TRIM-01 T2: can a docs-only push skip the matrix soundly? (blind seat; read-only; license to disagree)

SESSION_MODE: delegated
WRITE_SCOPE: []

You are a BLIND design seat. Work in the detached review worktree at HEAD `8819cb5f` (PR #317 after fix round 1). Read-only on tracked files; temp dirs allowed; never touch `/Users/edr/code/JouleWise` (read-only use of its `.venv/bin/python3` allowed), any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`. No network. Do not run the full suite; single modules and snippets only.

Read first: `.github/workflows/ci.yml` at HEAD; `scripts/shard_tests.py`; `scripts/test_timings.json`; and, read-only in `/Users/edr/code/JouleWise-wt-bk-24b9d3dd/docs/process_traces/2026-09-13-activation-24b9d3dd/`: the delta re-audit `07-delta-317-execution-astra-report.md` (its R1/R2 tables are the evidence) and the triage `12-lead-triage-317-delta-escalation.md` (the question and options A/B/C are stated there — answer THAT question).

You have explicit license to disagree with every option listed and to propose a better one. Ground every claim in a line of the repository or a command you ran (paste). For option B, prototype the trace: run ONE docs-asserting module (e.g. `tests.test_workload_sizing`) under a `sys.addaudithook` that records `open` events for paths under the repo root, and paste the recorded repository files; then run one module that reads docs through a subprocess or `git show` if you can find one, and say whether the hook sees it. State the arithmetic: full matrix ≈ 190 runner-minutes per push; docs-only baseline ≈ 1.5; the current docs-readers ≈ 23; how many docs-only pushes per week would make B pay for its build and maintenance (estimate the build in seat-hours from the design you write).

Report (claude-codex-report/v1, genre scout) as your FINAL MESSAGE: recommendation (A/B/C/other) with the deciding reason; the design for the recommended mechanism at the level a seat could implement from it (file, function, hook, map schema, CI step, failure modes and their handling); the staleness proof or counterexample; the cost arithmetic; and "what the lead should double-check". Under 8000 bytes.
