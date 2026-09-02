ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
WRITE_SCOPE: []

# Delta re-audit — night driver fix round 3 (`f07c85d5` over `224b2295`)

Checkout: `/Users/edr/code/JouleWise-wt-night-driver` (branch
`feat/2026-09-01-night-driver`, head `f07c85d5`). The fix is ONE commit:
`git show f07c85d5 --stat` (4 files, +241/-41). Write NOTHING in the tree;
`TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Run only `python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d
tests.test_night_gate` (in the worktree and against TMPDIR copies — note the
installer tests need `.git`; `git worktree`-style copies: `cp -R` the
worktree rather than `git archive`, or replicate what report 131 did). NEVER
spawn a real chain, a real `claude`, `launchctl`, or `git push`. Avoid the
substring `t3` in anything you create.

Authority: `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
(R-7, §8 d.3). The round's brief is `.../scratchpad/run-wo2-fix3.md`; the
seat's report `.../scratchpad/out/131-sol-wo2-fix3.md`; the terra audit that
ordered the round `.../scratchpad/out/130-terra-wo2-delta2.md`. Fix rounds
introduce defects — audit the DELTA only.

1. **Cure match, executed.** For F3 / F1 / F4 (brief text is authoritative):
   read the cure at the seat's cited lines and run the seat's named test in
   the worktree; then re-create each pre-fix condition on a TMPDIR copy of
   `224b2295` (the seat claims it did; you re-execute) and paste the failing
   line. Specifically verify:
   - F3: `Popen` `OSError` → `chain.started` completed with null pid/pgid +
     `launch_error`, `chain.exited.launch_failed == True`, refusal reason
     `night_chain_launch_failed` validates under `validate_refusal`, courier
     attempted, push attempted, rc == `EXIT_REFUSED`; dead-man over EMPTY and
     over null-pgid `chain.started` couriers and never calls `killpg`. ALSO
     the case the brief did not spell out: `chain.started` present, VALID
     pgid, `chain.exited` present with `launch_failed: true` — dead-man must
     courier, not `killpg`. State FOUND/NOT FOUND.
   - F1: equality test computes the dead-man epoch via `_next_deadman_epoch`
     (not a hard-coded number) and the `window_max_s - 1` twin proceeds past
     the predicate. Mutants `>=`→`>` and, on any inverse form, `<`→`<=`: both
     must die.
   - F4: the wait loop's sleep is `max(0, min(1, deadline_rem, stop_rem))`
     and both bounds are re-checked before sleeping; with a fake clock at
     `stop_epoch_s - 0.3` no sleep exceeds 0.3. Also: with `stop_epoch_s is
     None` the behaviour is unchanged from round 2 (state how you checked).
2. **New defects in the delta.** Read every hunk of `git show f07c85d5 --
   scripts/run_night.py`. Check in particular: (a) `_complete_chain_launch_failure`
   closes the claim descriptor exactly once on every path (no double close,
   no leak when `_write_all` raises); (b) the refusal path after a launch
   failure still writes `result.json`, `courier.json`, and the durable
   record in the SAME order as the other refusal paths; (c) the changed
   verdict/exit-code selection (`refused = abort_reason == chain_launch_failed
   or not termination_proven`) does not turn a census ABORT into a REFUSED
   or vice versa — enumerate the (abort_reason, termination_proven) table
   and the resulting (verdict, rc); (d) the dead-man's new null-pgid branch
   cannot be reached while a real chain is alive (what if `chain.started`
   is being written at that instant — the O_EXCL claim opens the file empty
   before the pid lands; is there a window where the dead-man reads an empty
   marker of a chain that is actually starting? state the timing argument
   and whether R-3/R-7 tolerate it; the dead-man fires at 07:00, the chain
   starts at t0 — say what protects the case where t0 ≥ 07:00).
3. **Mutants (TMPDIR copies of `f07c85d5`):** (a) remove the `except OSError`
   (let it raise); (b) `launch_failed=False` in the dead-man null branch;
   (c) `sleep_s = 1.0` unconditionally; (d) `refused = not termination_proven`
   (drop the launch-failed clause); (e) re-run round 2's five mutants from
   report 130 (O_EXCL on result.json; termination returns True; predicate
   `<`→`<=` / `>=`→`>`; second push dropped; deadline 600). Failing test
   name per mutant or SURVIVED.
4. Suite: expected `Ran 88 tests … OK` in the worktree; `git status` clean.

## Report

Envelope first (fenced ```json, `claude-codex-report/v1`, genre `review`).
Verdict MERGE-READY / FIX-ROUND. Then the cure table (item → executed
pre-fix failure line → post-fix), §2 findings with file:line, the
(abort_reason, termination_proven) table, the mutant table, exact commands.
Under 100 lines after the envelope.
