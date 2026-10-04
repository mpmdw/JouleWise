# Refuter for cold registration gate G2A-25G83-B3 (Opus 5.5)

You are the independent refuter for the cold registration gate whose charge is
`docs/process_traces/2026-10-03-design-block3/50-seal-charge.md` in this worktree. Read that
charge in full; its read limits, blindness rule, prohibitions and checks bind you exactly as they
bind the judge (no RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files; no
pull-request bodies or comments; no sudo, systemsetup, launchctl, powermetrics; no model loading or
capture; no git fetch/pull/checkout/commit; foreground only, no background task, no subagent).
Scratch `/tmp/cg-g2a-b3-refuter/`. Budget 75 minutes. Ending your turn before your output file
exists is a protocol failure.

**Phase 1 (do this FIRST, before reading any judge output).** Answer the charge's nine questions
yourself, executing its checks. Write your contamination disclosure and your independent findings
to `docs/process_traces/2026-10-03-design-block3/51r-seal-refuter.md` in this worktree under the
heading `## Phase 1: independent findings`, with your own provisional first line in the form the
charge prescribes for the judge.

**Phase 2.** Only after Phase 1 is written, wait for the judge's ruling at
`docs/process_traces/2026-10-03-design-block3/51-seal-ruling.md` in this worktree (poll in the
foreground with `sleep 60` steps; each Bash call at most 9 minutes; give up after 60 minutes of
waiting and record `NO RULING` as your verdict). Read it, try to break it (wrong facts, a check it
skipped, a required change that would itself make a rule ambiguous or a selection wrong, a
consequence it missed), and append `## Phase 2: on the ruling`. Then prepend, as the file's
**first line**, exactly one of:

- `REFUTER G2A-25G83-B3: AGREE`
- `REFUTER G2A-25G83-B3: DISAGREE — <one line: the defect>`

AGREE means no defect in the ruling would let the block select a wrong rung, waste a window by
rule, contradict D-166 outside the end-state clause, or make the end state unsound. Wording nits
are findings, not disagreement. End with a 3-line plain summary.
