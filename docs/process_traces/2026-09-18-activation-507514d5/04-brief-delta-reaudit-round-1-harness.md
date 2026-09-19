SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Delta re-audit (read-only) — lane QUIET-PREDICATE-EVIDENCE-01 harness, fix round 1 vs `d066d271`

Cwd is a detached read-only worktree at the fix-round-1 head (`git log -1` shows it; its parent is `d066d271`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; write nothing but `/tmp` scratch. No `sudo`, no `powermetrics`, no live `collect` with power. A measurement night is armed for 00:00 PDT: every process you start must end inside 60 s; load experiments at most `--cores 0.1` for 5 s. Set `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp` and `-B`; use `python3 -B -m unittest tests.test_sample_quiet_predicate_evidence`. Never run the canonical discovery suite. Finish inside 10 minutes.

## What you are re-auditing

`git diff d066d271 HEAD` is fix round 1 answering the refuter findings in `/tmp/mag-507514d5/01-refuter-contract-astra.md` (F1, F2) and `/tmp/mag-507514d5/02-refuter-execution-astra.md` (R1 blocker, R2–R7); the fix brief is `/tmp/mag-507514d5/03-brief.md` and the fix seat's report is `/tmp/mag-507514d5/03-fix-round-1-astra.md`. Fix rounds introduce defects; that is why you exist.

## Answer with evidence (commands, outputs, file:line)

D1. For each of R1–R7, F1, F2: FIXED / NOT FIXED / REGRESSED, citing the test that now guards it. Run `/tmp/mag-507514d5/mutations.py` for `alignment`, `observer`, `cores` against the new head and paste the tails: each must report failures. A mutation that still survives is the same signature as before — name it.
D2. Was any existing assertion weakened, deleted, or made conditional? Diff the test file's assertions before and after (`git diff d066d271 HEAD -- tests/`), list any removed `assert*` line.
D3. Did the schema change meaning under the same schema name? Compare the emitted row keys before and after; a renamed or re-typed field under `joulewise.quiet_predicate_evidence.v1` is a finding.
D4. New behaviour: does the census_clean derivation treat "no census completed" as unknown (null), never as clean? Does `summarize` on a directory mixing clean and unknown rounds keep them apart? Construct a two-row fixture in `/tmp` and show the output.
D5. Does any new test depend on wall-clock timing loosely enough to flake on a loaded machine (state the tolerance and the window), or take more than 5 s? Time the module.
D6. Same-signature statement: "same-signature: none found" or the surviving signature by name.

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre review`; `verdict` = `{counts, findings}` only; JSON header under 8000 bytes; severity blocker / should_fix / nit; counterfactual input and call site for every finding.

D4b. Census exit-code semantics: `census_condition` treats exit 0 with stdout as a hit, exit 1 with empty stdout as absence, anything else as malformed. Verify against the production census contract in `joulewise/quiet_admission.py` and `scripts/run_night.py` (cite lines) that these are the real codes; a mismatch that could label a hit as unknown or clean is a blocker.
