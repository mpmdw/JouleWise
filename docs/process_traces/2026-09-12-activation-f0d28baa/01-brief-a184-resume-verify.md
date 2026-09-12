# Seat brief — RECOVER-SESSION-REFUSAL-WINDOW-EXHAUSTED-01 resume + verify (kernel lane A184)

WRITE_SCOPE: ["scripts/recover_calibration_ledger.py","joulewise/calibration_exits.py","tests/test_calibration_exits.py","docs/phase_2/derivation_night_runbook.md","docs/contracts/calibration_ledger_append.md","docs/contracts/powermetrics_fiducial.md"]

You are a resume seat in the linked worktree you were started in (branch
`fix/2026-09-12-recover-window-exhausted`, from origin/main `ace4cc3c`). A
previous seat (activation b02193d2, brief in
`../JouleWise-wt-bk-b02193d2/docs/process_traces/2026-09-12-activation-b02193d2/01-brief-a184-recover-window-exhausted.md`
— read it in full first; it is the governing brief) drafted the change and
was killed before verifying it. The working tree is DIRTY with that draft
(`git status --short` shows five modified files, `git diff --stat` = 53
insertions). Do NOT revert, stash, or checkout those files. Never run git
commands that move HEAD, never push, never touch `/Users/edr/code/JouleWise`
or `/Users/edr/JouleWise-measurement-20260913-derivation` (a measurement
night is armed there; both are fenced).

## Your work

1. Read `git diff` and review the draft against the governing brief's
   steps 1–4 with a critical eye. Known questions the magistrate wants
   answered, fix in place if wrong:
   a. The new test asserts `refused.returncode ==
      REFUSAL_BY_CODE[RefusalCode.SAMPLER_NEVER_READY].process_exit`. It
      should reference the NEW code's own record
      (`REFUSAL_BY_CODE[RefusalCode.WINDOW_EXHAUSTED].process_exit`) unless
      the file's convention says otherwise; make the assertion self-describing.
   b. The `WITNESS_CASES` entry uses observer `"session-refusal"` and the
      generic witness loop gained a `case.observer == "session-refusal"`
      branch. Confirm every generic witness test that iterates
      `WITNESS_CASES` still passes for the new case (family/tier tables,
      human strings, witness column, process exit) and that the new branch
      does not weaken the existing cases' assertions.
   c. The registry table in `docs/contracts/calibration_ledger_append.md`
      sits inside a `GENERATED: calibration-refusal-registry` region
      ("generated from REFUSAL_INVENTORY"). Find the generator (grep for
      `calibration-refusal-registry`) and run its check mode; the
      hand-written row must be byte-identical to the generator's output.
      If the generator also writes a digest/count anywhere, run it so the
      ONE home is fresh, and say what it touched (it must stay inside
      WRITE_SCOPE; if not, NEEDS_SCOPE naming the path).
   d. `docs/contracts/powermetrics_fiducial.md` ~line 463 names one of the
      three codes; decide whether the new code belongs there too (mirror only
      if the prose enumerates the automatic-abort set; otherwise leave it).
2. Killed cut (governing brief step 3): run the new test with the
   `"window_exhausted"` entry removed from `_AUTOMATIC_ABORT_REFUSALS` (must
   FAIL with SESSION_NOT_OPEN), restore the bytes (sha256 before/after),
   run again (PASS). Paste both `Ran N` / result lines.
3. Whole file: `python -m pytest tests/test_calibration_exits.py -q`;
   `python scripts/gen_state.py --check` if applicable; `git diff --check`.
   Do NOT commit; leave the tree dirty. Report `git status --short` and
   `git diff --stat`.

## Report (final message, claude-codex-report/v1 envelope per --genre)

What you changed relative to the inherited draft and why; answers to 1a–1d
with line citations; killed-cut evidence (both runs); whole-file result line;
any NEEDS_SCOPE/NEEDS_RULING; anything unsure. Under 8000 bytes.
