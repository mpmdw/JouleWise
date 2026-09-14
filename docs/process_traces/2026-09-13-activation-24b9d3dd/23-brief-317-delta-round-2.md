# Delta re-audit brief — PR #317 CI-TRIM-01 fix round 2 (option A), EXECUTION lens (Astra high; workspace-write for temp dirs, WRITE_SCOPE [])

SESSION_MODE: delegated
WRITE_SCOPE: []

You are in the detached review worktree at HEAD `8a733f5c` (PR #317 after fix round 2; PR base `a4bb8838`; round-2 delta = `git diff 8819cb5f..8a733f5c`). Read-only on tracked files; temp dirs allowed; never touch `/Users/edr/code/JouleWise` (its `.venv/bin/python3` may be used read-only for PyYAML), any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`. No network; no GitHub API (say where you would have used one).

Authority for the round (read-only): cold-gate ruling `/Users/edr/code/JouleWise-wt-bk-24b9d3dd/docs/process_traces/2026-09-13-activation-24b9d3dd/17-coldgate-packet-ci-trim-t2/10-coldgate-fable-ruling.md` Q1 (exact deletions) and Q2(c); the fix contract `…/21-brief-317-fix-round-2-option-A.md`; the seat report `…/22-fix-317-round-2-astra-report.md`.

Try to BREAK the round:
1. Ruling fidelity: apply the ruling's Q1 edits mechanically to `git show 8819cb5f:.github/workflows/ci.yml` in a temp dir and `diff` the result against `git show 8a733f5c:.github/workflows/ci.yml`; paste any difference (a difference is should-fix unless it is the ruled comment line, which must match the ruling's sentence exactly).
2. Net PR shape: `git diff a4bb8838..8a733f5c -- .github/workflows/ci.yml` — confirm the ONLY changes against the base are: the concurrency block + its comment (FIX-1), the `fences` job added and its five steps removed from the matrix job (T1: diff each step's command old vs new, byte-equal), the zsh guard (T4), the `pr-fast` job deleted (T3). Any other change is a finding. Confirm no `changes`, `docs-readers`, `needs.changes`, `cancelled()` token exists at HEAD.
3. Suite completeness at HEAD: the matrix (`test`) still runs four shards × Python 3.11 and 3.14 and both exclusive jobs on every push and PR with NO `if:`; `installed-wheel` needs `build` only. Table job → needs → if.
4. `scripts/test_timings.json`: the only change since `a4bb8838` is the removal of the `pr_fast_tier` key; parse it; run `python3 -m unittest tests.test_check_gate_ledger` and any test that imports `scripts/shard_tests.py` or reads `test_timings.json` (find them with `rg -l "test_timings|shard_tests" tests/`); paste tails. `rg -n pr_fast_tier` over the tree excluding `docs/process_traces/` must be empty.
5. `bash -n` on every `run:` block; YAML parse; `git diff --check a4bb8838..8a733f5c`; `git status --short` empty.
6. Same-signature line: is any docs-asserting test skipped on any push or PR at HEAD? (Expected NO, because nothing is gated.) State it with the evidence line.

Report (claude-codex-report/v1, genre review) severity-tiered with file:line, pasted evidence, the same-signature line, and "what the lead should double-check". Under 8000 bytes.
