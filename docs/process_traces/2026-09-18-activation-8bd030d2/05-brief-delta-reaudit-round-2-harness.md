SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Delta re-audit (read-only) — lane QUIET-PREDICATE-EVIDENCE-01 harness, bench fix `498ad1d0` vs `05e90616`

Cwd is a detached read-only worktree at `498ad1d0` (`git log -1` shows it; its parent is `05e90616`, the fix-round-1 head your predecessor audited). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; write nothing but `/tmp` scratch. No `sudo`, no `powermetrics`, no live `collect` with power. A measurement night is armed for 00:00 PDT: every process you start must end inside 60 s; load experiments at most `--cores 0.1` for 5 s. Set `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp` and `-B`; use `python3 -B -m unittest tests.test_sample_quiet_predicate_evidence`. Never run the canonical discovery suite. Finish inside 8 minutes.

## What you are re-auditing

`git diff 05e90616 HEAD` is a single lead-authored bench fix (one test changed, 11 lines) answering finding D5-T1 of the previous delta re-audit, `/tmp/mag-8bd030d2/04-delta-reaudit-round-1-astra.md` (should_fix: the real-load regression `test_real_load_tracks_point_one_core_and_guards_worker_budget` confused scheduler starvation with incorrect core budgeting; counterfactual: correct budgeting with each sleep waking 1.05 s late yields 0.0333 cores and failed the old ±0.04 two-sided check). The lead's own account of the fix is `/tmp/mag-8bd030d2/04a-bench-fix-d5-t1-and-closeout.md`; it was never independently audited. Fix rounds introduce defects; that is why you exist.

## Answer with evidence (commands, outputs, file:line)

E1. Is D5-T1 FIXED, NOT FIXED, or REGRESSED? Re-run the D5-T1 counterfactual in reasoning or with a fake clock: correct `duty_periods` with 1.05 s late wakes → does the new assertion chain accept it? Show the arithmetic of `fraction >= .1 - .04 - .1 * late_s / duration_s` for that input and state whether the bound is derived from the production no-catch-up rule at `scripts/sample_quiet_predicate_evidence.py` (cite the line) or merely fitted.
E2. Did the fix weaken the guard it was protecting? Construct the counterfactual the test exists for: a budgeting defect that under-burns (e.g. a controller that burns half the requested budget every period, on time). Under the new branch structure, does it still fail? If a defect could hide by *also* producing late wakes (late_s > 0.12), say so and judge whether that is a real hole or an acceptable residual; state which assertion (if any) in the deterministic fake-clock tests already covers it.
E3. Run `/tmp/mag-8bd030d2/mutations.py cores` (and `alignment`, `observer`) against HEAD and paste the tails: each must still report failures. Note: the module carries `d066d271`-era source text for its substitutions; if a substitution no longer matches, apply the equivalent substitution by hand and say so.
E4. Does the new assertion's `wake_late_s` field exist on every period row the real-load path emits (cite the producer line), and can it be missing or None such that the sum raises? Is the message f-string safe for the values that reach it?
E5. Timing: time the module twice. Does the changed test still finish under 5 s, and does the branch that fires (tight vs starvation) differ between the two runs on this idle machine? Report `late_s` values you observed if you can print them (a `/tmp` copy of the test with a print is fine).
E6. Same-signature statement: "same-signature: none found" or the surviving signature by name (the signature of D5-T1 is "real-load assertion fails on correct code under scheduler starvation").

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre review`; `verdict` = `{counts, findings}` only; JSON header under 8000 bytes; severity blocker / should_fix / nit; counterfactual input and call site for every finding.
