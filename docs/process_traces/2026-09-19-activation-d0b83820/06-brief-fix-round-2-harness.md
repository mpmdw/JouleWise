SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/test_sample_quiet_predicate_evidence.py"]

# Fix round 2 — lane QUIET-PREDICATE-EVIDENCE-01 harness, defect D5-T1 (real-load regression asserts scheduler delivery)

Cwd is the linked worktree of branch `feat/2026-09-18-quiet-predicate-evidence-harness` at `3df43458` (rebased onto main `2f79e633`; `git log -1` shows it). Never touch `/Users/edr/code/JouleWise` (the canonical root) or any other worktree; scratch goes under `/tmp` only. No `sudo`, no `powermetrics`, no live `collect` with power. Nothing is armed tonight, so the real-load test (a 3 s, 0.1-core subprocess burn) MAY run at the bench. Do not commit; the lead commits by pathspec from your report. Do not end your turn before the report is complete: every step below is executed, or its non-execution is named.

## The ruling you implement (read these first; they are in this tree)

- `docs/process_traces/2026-09-18-activation-e82f29ac/01a-adjudication-d5-t1-ruling-synthesis.md` — §3 is the EXACT assertion block; §5 is the regression spec; §2 explains why ruling 10's `charged_s <= claimed_s + STARTUP_CPU_S` assertion is NOT adopted.
- `…/01-coldgate-packet-d5-t1-real-load-regression/11-opus-contract-refuter.md` — the two deterministic tests (lines ~43–61) and the `FakeClock.ratio` change, to be taken verbatim.
- `…/10-coldgate-fable-ruling.md` lines ~55–75 — the stricter pins to fold in.
- `docs/process_traces/2026-09-18-activation-8bd030d2/05a-adjudication-d5-t1-open-and-closeout.md` — the two surviving correct-code counterexamples your tests must encode.

## Step 1 — real-load assertion block

In `tests/test_sample_quiet_predicate_evidence.py`, `test_real_load_tracks_point_one_core_and_guards_worker_budget` (currently lines 601–638): add `import resource` at module top and a module constant `STARTUP_CPU_S = 0.5` (with a one-line comment: measured child start-up CPU ≈ 0.19 s on this host, record 12; the floor is sized to the instrument, not to delivery). Take `before = resource.getrusage(resource.RUSAGE_CHILDREN)` immediately before `harness.load(args)` and `after = …` immediately after it returns (inside the `with`). Replace everything from `periods = [...]` through the `else:` branch's `assertGreaterEqual` (lines 620–632) with record 01a §3's block VERBATIM (it drops the delivery minimum and the `late_s` branch; keeps the 0.14 ceiling; adds the per-period ceiling, the liveness floor, the `charged_s >= claimed_s - .01` kernel cross-check and the `charged_s <= .14 * duration + STARTUP_CPU_S` ceiling). Keep the cleanup assertions that follow. Update the test's leading comment so it states the contract in one sentence: the controller promises a measured CPU ceiling and no catch-up, never delivery.

## Step 2 — two deterministic regressions (fake clock, test-file only)

Add record 11's `test_late_initial_scheduling_never_catches_up` and `test_preempted_burn_exits_on_the_wall_deadline` verbatim, giving `FakeClock` a `ratio` attribute (default 1.0) that scales the wall advance in `burn`. Fold in ruling 10's pins where stricter: period ids `[4, 5]` for the late-start case; every `wake_late_s < 1e-3`; every row `work_budget_cpu_s <= .1 * elapsed_s + 1e-9` (no catch-up). If a pin from ruling 10 contradicts a number record 11 executed, keep record 11's number and REPORT the contradiction as a finding — do not average.

## Step 3 — bench acceptance (execute; paste tails)

Interpreter: `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use of the canonical venv is fine; no writes there).
1. `python -m unittest tests.test_sample_quiet_predicate_evidence -v` TWICE; expect 43 tests OK both times; paste the summary lines and the two runs' wall time.
2. Three unmodified runs of the real-load test alone; paste `charged_s`, `claimed_s` and `charged_s - claimed_s` for each (a `/tmp` copy of the test with a print, or a `-k` run with an env-guarded print you remove afterwards; the committed file must carry no print).
3. Mutation set, each applied to a `/tmp` COPY of the tree or via the substitution pattern of `docs/process_traces/2026-09-18-activation-507514d5/02a-refuter-execution-mutations.py` — the production script in THIS worktree must be byte-identical afterwards (`git status` clean apart from the scoped test file): `cores`, `alignment`, `observer` (the 02a scripts; if a substitution no longer matches the rebased text, apply the equivalent by hand and say so), `clock` (`Clock.cpu` → 0; expected to die on the liveness floor AND the kernel ceiling), `catchup-capped` (carry unmet budget forward with the total capped at share × duration; expected to die on the per-period ceiling and on test (i)'s 0.1 CPU-s pin), `burn-noop` (`burn_profile` returns a no-op; REPORT which assertion kills it — if none does, that is a finding, not a fix). Paste each mutation's failing assertion names and counts.
4. `git diff --stat` and confirm the only changed path is the scoped file.

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes; list every executed command with its outcome; findings with severity blocker / should_fix / nit, each with the counterfactual input and the call site (`file:line`). State the same-signature answer for BOTH signatures: "real-load assertion fails on correct code under scheduler starvation" and "assertion keyed to a quantity starvation destroys". If anything blocks you (a contradiction between the records, a pin that fails on correct code), finish the independent work and return NEEDS_RULING with the question, options and your recommendation.
