# Cold gate CUSTODY-REPAIR-FINAL-01: the final diff of the issuer custody repair (gate row 7 + statement REV5-REFUSAL-BRANCH-01 item 6(c))

You are a COLD judge: a fresh session with no loop context. You did not design or write this repair. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**Outcome-blind, binding.** Open no epoch 25G83 W1/W2 measured value: no B / `b_fiducial_s`, no ledger value fields, no `manifest.json` or `instrument_evidence.json` content under `/Users/edr/night-custody`. Only path strings, ids and file existence.

**Candidate:** `/Users/edr/code/JouleWise-wt-corpus-fp-77b1bee2`, detached at **`f783a3fd`** (branch `fix/2026-09-27-issuer-corpus-root`). Its base is main `b69c39eb`. The diff is `git diff b69c39eb f783a3fd`: the issuer, the fixture builder and `tests/test_issuer_corpus_root.py`.

**Governing texts.** All are under `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/`:
- The statement: `60-prepare-record/00-refusal-branch-final-statement.md`, especially item 6 and constraints R1–R9 in 6(d). The addendum that set this gate's role is `40-refusal-branch/30-addendum/21-addendum-ruling.md` §6.
- The design: `50-custody-outside-repo/30-lead-synthesis.md` (design C and rulings 1–5), taken from Fable consult `14-fable-consult.md` §5.
- The evidence (verify; do not trust):
  - `41-impl-seat-report.md`, `42-lead-verify-tail.txt` (263 OK);
  - `51-sol-execution-lens.md` (FAIL: F1 nested path) and `52-opus-contract-lens.md` (PASS, S1 + nits);
  - `60-fix1-brief.txt` (the lead's F1 ruling: the exact four-part shape) and `61-fix1-seat-report.md`;
  - `63-fix1-lead-verify-tail.txt` (270 OK) and `64-astra-delta-report.md` (DELTA PASS).

**Rule on:**
1. **Item 6(c).** Is this change a *tool repair* in the statement's sense (a fault in the tool, not a change in which captures count or in any limit), satisfying R1–R9? Check each constraint against the diff.
2. **Correctness.** Re-run the issuer suites and the new tests yourself with `/opt/homebrew/bin/python3`: `tests.test_issuer_corpus_root`, `tests.test_issue_calibration_acceptance_generation`, `tests.test_reissue_calibration_acceptance` and `tests.test_calibration_bracketing`. Re-run the R8 value-blind probe on the 24 real locators, projecting only `custody_locator`, `attempt_id` and `session_id` from `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl`. Try to break the naming function or `verify-members` with at least five adversarial synthetic inputs of your own.
3. **The lead's ruling on Sol's F1** (the exact four-part shape). Is it within design C? Could it refuse a legitimate future layout in a way that matters? For example, a relocated archive keeps the `<plan_id>/runs/instrument_validation/<id>` layout.
4. **Anything that blocks merging `f783a3fd` to main**, or that `prepare-candidate` with `--corpus-root /Users/edr/night-custody` could still refuse value-blind. List what the prepare step must still check.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`.
- Modify NO file in any repository or custody root. Scratch goes under `/tmp/cg-custody-final-77b1bee2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/50-custody-outside-repo/71-coldgate-final-diff-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 35 minutes. Mark anything not run as NOT EXECUTED.
- The first line is `VERDICT: MERGE` or `VERDICT: DO-NOT-MERGE`, and the second line is `ITEM 6(c): TOOL REPAIR` or `ITEM 6(c): NOT A TOOL REPAIR`. End with a 3-line plain summary.
