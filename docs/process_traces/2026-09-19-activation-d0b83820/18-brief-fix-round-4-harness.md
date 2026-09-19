SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["scripts/sample_quiet_predicate_evidence.py", "tests/test_sample_quiet_predicate_evidence.py"]

# Fix round 4 — lane QUIET-PREDICATE-EVIDENCE-01 harness: Opus counter-review 13 findings S1–S7, N1–N3 (lead triage 13a)

Cwd is the linked worktree of branch `feat/2026-09-18-quiet-predicate-evidence-harness` at `d74b1be5` (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; scratch under `/tmp` only; no `sudo`, no `powermetrics`, no live `collect` with power. Nothing is armed; the real-load test may run. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use). Do not commit. Do not end your turn before the report is complete.

Read first (absolute paths in another worktree; read them as files): `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/13a-triage-opus-counter-review-lane-232.md` (the exact fix shape per finding — implement each disposition as written, nothing more) and `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/13-opus-counter-review-lane-232.md` (the findings with file:line and the probes under `/tmp/magistrate-d0b83820/opus-counter-232/`, which you may reuse as regression seeds).

## Do

Implement S1, S2, S3 (bounded as ruled), S4, S5, S6, S7, N1, N2, N3 exactly per record 13a. For each production change add or adjust a defect-shaped regression in the test module (counterfactual input from record 13's probe, production call site named in the test's comment): S1 (slow-exit child → `report["error"]` names the escalation; exit code 1), S2 (a correct child needing 1 s to exit after delivering its result → no escalation, exit 0, `exitcode == 0`), S3 (all rounds error → `session["error"]` set and exit 1; one of three rounds error → `error_rounds == 1`, `session["error"]` None, exit 0), S4 (resolved sibling → reason key absent), S5 (two boots → two groups, each carrying its `boot_id`), S6 (QoS readback), N2 (foreign row → `ValueError`, not `KeyError`), N3 (`Process.start` raising → no unclosed pipe; assert via a fake Process whose `start` raises and check both connection ends are closed). Preserve every existing test except the two deleted with `stop_process`.

## Bench acceptance (execute; paste tails)

- Module twice under unittest: expect 44 tests OK, wall times.
- Mutations on `/tmp` copies (worktree byte-identical afterwards, `git status` before/after): `cores`, `alignment`, `observer`, `clock`, `catchup-capped`, `burn-noop`, `window-skip` (patterns as in records 10/11) plus new: `cleanup-silent` (revert S1: never set `report["error"]` from cleanup), `pool-across-boots` (revert S5: drop `boot_id` from the key), `qos-swap` (`0x09 ↔ 0x19`), `all-error-exit-0` (revert S3). Each ≥ 1 failure; paste failing test names.
- Both same-signature statements: "real-load assertion fails on correct code under scheduler starvation" and "assertion keyed to a quantity starvation destroys" — enumerate every assertion in the real-load test again and classify.
- `git diff --stat`: only the two scoped files.

## Report

`claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes; commands with outcomes; findings with counterfactual and call site; NEEDS_RULING if any disposition in 13a cannot be implemented as written (say why, propose the smallest alternative, finish the rest).
