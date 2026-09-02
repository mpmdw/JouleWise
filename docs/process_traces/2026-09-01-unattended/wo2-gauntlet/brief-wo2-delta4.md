ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
WRITE_SCOPE: []

# Delta re-audit — night driver fix round 4 (`2f9ad50a` over `66e496a5`)

Checkout: `/Users/edr/code/JouleWise-wt-night-driver` (branch
`feat/2026-09-01-night-driver`, head `7c80ba2d`; the code commit is
`2f9ad50a`, 3 files +254/-9; `7c80ba2d` is docs only). Write NOTHING in the
tree; `TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Run only `python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d
tests.test_night_gate` (worktree: expected `Ran 95 tests … OK`; TMPDIR
copies: `cp -R` the worktree, since installer tests need `.git`). NEVER
spawn a real chain, a real `claude`, `launchctl`, or `git push`. Avoid the
substring `t3` in anything you create.

Authority: `docs/process_traces/2026-09-01-unattended/coldgate-d1-RULING.md`
(cures C1/C2/C3 and the "Not in round 4" list are binding). Brief:
`.../wo2-gauntlet/brief-wo2-fix4.md`; seat report
`.../wo2-gauntlet/134-terra-wo2-fix4.md`. This is the FOURTH fix round; a
same-signature failure here is a structural signal, so be precise about
what you find and whether it is the marker-semantics signature again.

1. **Cure match, executed.** For C1/C2/C3: read the cure at the cited
   lines and run the seat's named tests in the worktree; re-create the
   pre-fix condition on a TMPDIR copy of `66e496a5` with the new test file
   copied over and paste the failing line. Verify specifically:
   - C1: the guard sits AFTER the `courier.sent` early return and BEFORE
     `_resolve_courier_bin`/`_courier_lock_is_live`; on stand-down the
     night dir's entry set is unchanged, `night.log` gains exactly one
     line, no `Popen`/`run`/`killpg`; `_completion_epoch_s` is the ONLY
     source of the completion arithmetic in the file (grep for
     `COURIER_DEADLINE_S` — any remaining inline `t0 + window_max_s +`
     sum is a finding); the run-path overrun predicate is behaviourally
     unchanged (existing boundary tests untouched: `git diff 66e496a5 --
     tests/test_run_night.py` must not modify them).
   - C1 boundary: clock == completion epoch → the absent-marker path
     runs (census, durable record, courier). Clock == completion − 1 →
     stand-down.
   - C2: `--hour == DEADMAN_HOUR` refused with exit 2 and the message,
     nothing rendered; `--uninstall` with that hour is NOT refused;
     `--render-only` with that hour IS refused (say what the code does).
   - C3: each of the seven record names alone triggers exit 3 (loop the
     test or reason from the loop — say which); `--uninstall` on a dirty
     dir still boots out both labels; a fresh custody root installs.
2. **New defects in the delta.** (a) Does the stand-down interact with
   the REHEARSAL_STUB run path or with `_malformed_plan_exit` (a plan with
   no `window_max_s`) — can `_completion_epoch_s` raise on a plan the
   dead-man accepted? (b) `night.log` on stand-down: is `_append_log`
   safe if `custody_root` does not exist yet (the dead-man `mkdir`s the
   night dir first — confirm order)? (c) A dead-man that stands down
   returns `EXIT_GO` — does anything (launchd plist, installer,
   NIGHT_HANDBACK.md) treat the dead-man's exit code as meaningful such
   that GO-before-the-night is misread? (d) The installer's stale-record
   loop uses zsh arrays — confirm it runs under `/bin/zsh` as invoked by
   the tests AND by the plist (`ProgramArguments`), and that `[[ -e ]]`
   on a dangling symlink behaves as intended. State FOUND/NOT FOUND with
   file:line.
3. **Mutants (TMPDIR copies of `2f9ad50a`):** (a) delete the guard;
   (b) `<`→`<=`; (c) guard on `plan.t0_epoch_s`; (d) `_completion_epoch_s`
   drops `COURIER_DEADLINE_S`; (e) remove C2; (f) C3 loop checks only
   `chain.started`; (g) C2 guard also fires under `--uninstall`. Failing
   test per mutant or SURVIVED.
4. **Signature check.** State explicitly whether any finding is about
   what an incomplete `chain.started` means to the dead-man (the D1/F3
   signature). If yes, that is a structural signal: say so in the verdict.

## Report

Envelope first (fenced ```json, `claude-codex-report/v1`, genre `review`).
Verdict MERGE-READY / FIX-ROUND. Cure table (item → executed pre-fix
failure line → post-fix), §2 findings with file:line, mutant table,
signature statement, exact commands. Under 100 lines after the envelope.
