# Refuter for cold erratum E-NT1 (Opus 5.5)

You are the independent refuter for the cold erratum gate whose charge is
`docs/process_traces/2026-10-02-interactive/40-erratum-nt1-charge.md` in this worktree. Read
that charge in full; its read limits, prohibitions and checks bind you exactly as they bind the
judge (no RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files; no sudo,
systemsetup, launchctl, powermetrics; no git fetch/pull/checkout/commit; foreground only, no
background task, no subagent). Scratch `/tmp/cg-ent1-refuter-d138/`. Budget 60 minutes.
Ending your turn before your output file exists is a protocol failure.

**Phase 1 (do this FIRST, before reading any judge output).** Answer the charge's two
questions yourself, executing its checks. Write your contamination disclosure and your
independent findings to `docs/process_traces/2026-10-02-interactive/41r-erratum-nt1-refuter.md`
in this worktree under the heading `## Phase 1: independent findings`, with your own
provisional answers in the same two-line form the charge prescribes for the judge.

**Phase 2.** Only after Phase 1 is written, wait for the judge's ruling at
`JUDGE_RULING_PATH` (polling in the foreground with `sleep 60` steps; each Bash call at most
9 minutes; give up after 50 minutes of waiting and record `NO RULING` as your verdict). Read
it, try to break it (wrong facts, a check it skipped, adopted text that does not describe what
the code admits, a consequence it missed), and append `## Phase 2: on the ruling`. Then
prepend, as the file's **first line**, exactly one of:

- `REFUTER E-NT1: AGREE`
- `REFUTER E-NT1: DISAGREE — <one line: the defect>`

AGREE means no defect in the ruling would change a number, the admission of either counting
window, or what the registration says is admitted. Wording nits are findings, not
disagreement. End with a 3-line plain summary.
