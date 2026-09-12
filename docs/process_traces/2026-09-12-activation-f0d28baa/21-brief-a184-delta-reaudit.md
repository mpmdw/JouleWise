# Delta re-audit brief — A184 fix round 1 (contract refuter 14 B1), contract + pedagogy lens

SESSION_MODE: delegated
WRITE_SCOPE: []

Read-only re-audit of ONE fix commit: `git diff 7014dd0e..HEAD` in this
detached worktree (HEAD `ca7346e4`, branch `fix/2026-09-12-recover-window-exhausted`).
You may run tests (temp dirs allowed) but must not edit tracked files. Your
own prior report is `../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/14-refuter-a184-contract-astra-report.md`
(finding B1 and its proposed wording). Never touch `/Users/edr/code/JouleWise`
or `/Users/edr/JouleWise-measurement-20260913-derivation` (fenced).

The fix replaced one runbook sentence in
`docs/phase_2/derivation_night_runbook.md` §"The other early end:
`window_exhausted`" (~line 1665) with a seven-line paragraph written by the
magistrate, not by a seat. Judge it on:
1. B1 closure: is the harvest operator, running the desk tool from the
   frozen clone at H f90cb8c0, now told the truth (prints
   `calibration_session_not_open`; read the reason from the chain-log line)?
   Quote the clone's actual behaviour from the git objects of this worktree
   (`git show f90cb8c0:scripts/recover_calibration_ledger.py | grep -n
   _AUTOMATIC_ABORT_REFUSALS -A6`) to confirm the paragraph's claim.
2. First-use test (writing standard): every term of art in the paragraph
   (`session-refusal`, "refusal code", "frozen clone", "H", "chain log line
   above") is either defined at first use in the paragraph or defined
   earlier in the SAME section/runbook. Cite where each is first defined; a
   term defined only later in the document is a should-fix with the exact
   replacement wording.
3. Factual claims: "main after 2026-09-12" (this change is not yet merged;
   is the phrasing safe if it merges 09-12 or later?), "Harvest always uses
   the night's frozen clone, never main" (is that what runbook §2 says?
   quote the §2 line). Any contradiction with §2 is a blocker.
4. Same-signature statement: does this fix introduce the SAME class of
   defect as B1 (a statement true for one checkout and false for the one
   the operator actually uses)? Answer explicitly.
5. Run `python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests -q` once and `python3 scripts/gen_state.py --check`; paste result lines.

Report (claude-codex-report/v1, genre review): findings tiered
blocker / should-fix / nit with exact replacement wording for any prose
finding; explicit "no blocker found" if none; the same-signature statement
as its own line. Under 8000 bytes.
