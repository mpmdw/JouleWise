SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Delta re-audit round 3 (read-only) — lane QUIET-PREDICATE-EVIDENCE-01 harness, fix rounds 2 + 3 (`3df43458..HEAD`) after cold gate packet 08

Cwd is a detached read-only worktree at the branch head named in `git log -1` (its ancestry: `3df43458` = the pre-round-2 head rebased onto main `2f79e633`; `37ca3c35` = fix round 2; HEAD = fix round 3). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; write nothing but `/tmp` scratch. No `sudo`, no `powermetrics`, no live `collect`. Nothing is armed; the real-load test may run. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use). Do not end your turn before every item has an answer or a named reason it has none.

## What you are re-auditing

`git diff 3df43458 HEAD -- tests/test_sample_quiet_predicate_evidence.py` — the full two-round change to the real-load regression and the new deterministic tests, ruled by: `docs/process_traces/2026-09-18-activation-e82f29ac/01a-adjudication-d5-t1-ruling-synthesis.md` (round 2) and `docs/process_traces/2026-09-19-activation-d0b83820/08a-adjudication-d5-t1-liveness-floor.md` with `08-coldgate-packet-d5-t1-liveness-floor/{10-coldgate-fable-ruling.md,11-opus-contract-refuter.md}` (round 3). Fix rounds introduce defects (proven twice on this repo): audit the FINAL text, not the intent.

## Answer with evidence (commands, outputs, file:line)

E1. Does the real-load test at HEAD contain ANY assertion that a correct worker can fail under scheduler starvation (late wakes, late first scheduling, in-burn preemption, zero service inside the window)? Enumerate every assertion in the test and classify each: upper bound on a starvation-lowered quantity / kernel lower bound relaxed by starvation / other. Execute the four fake-clock inputs from ruling 10's probe against the assertion set.
E2. Is the two-round change exactly what the rulings specified, no more? List every difference between the HEAD text and (a) 01a §3's block, (b) ruling 10's exact deletion, (c) refuter 11's two test texts as adopted in 08a. Any extra change is a finding.
E3. Mutation set against HEAD, each on a `/tmp` copy of the tree (the worktree must stay byte-identical; verify with `git status` before and after): `cores`, `alignment`, `observer` (`docs/process_traces/2026-09-18-activation-507514d5/02a-refuter-execution-mutations.py` patterns), `clock` (`Clock.cpu → 0`), `catchup-capped`, `burn-noop` (`burn_profile → lambda count: None`), `burn-constant` (`lambda count: 1`), `window-skip` (rendezvous `clock.sleep_until(start)` → `sleep_until(start + config["duration_s"])`). Paste failure counts and the failing test names. Any survivor is a finding.
E4. The new deterministic tests: do the patched names in `test_load_worker_runs_its_window_after_the_rendezvous` match the script's actual attributes and the worker's connection protocol at HEAD (cite lines)? Could the test pass against a worker that sends the rows but never burned (i.e. is the ≈ .3 CPU sum keyed to `FakeClock.burn`, and is `burn_profile` patched to the fake clock's burn)? Does `test_burn_profiles_advance_their_generator` assert against the script's real LCG constants?
E5. Timing and flake surface: module twice; wall time of the real-load test; does `charged_s <= .14 × 3 + 0.5` have margin on this host (paste `charged_s` from an instrumented `/tmp` copy, three runs)? Is `STARTUP_CPU_S = 0.5` still sized above the measured child start-up with margin?
E6. Same-signature statements, both: "real-load assertion fails on correct code under scheduler starvation" and "assertion keyed to a quantity starvation destroys" — "none found" or the surviving signature with its witness.
E7. Anything else a PR reviewer must know before the twelve-row gate (docstrings, comments that now lie, dead imports, `resource` on non-darwin).

## Report

`claude-codex-report/v1` envelope for `--genre review`; `verdict` = `{counts, findings}` only; JSON header under 8000 bytes; severity blocker / should_fix / nit; counterfactual input and call site for every finding.
