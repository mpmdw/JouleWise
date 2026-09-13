# FIX contract — PR #329 DOCS-THIN-01, fix round 1 (Astra high, enforced scope)

SESSION_MODE: delegated
WRITE_SCOPE: ["RUN_STATE.md", "docs/paper/results-fill-registry.md", "docs/project_critique_review.html", "docs/specs/axi/sb_static_batch_verdict.md", "docs/legacy/README.md", "docs/process_traces/RESUME-2026-07-26.md", "docs/legacy/process_traces/RESUME-2026-07-26.md", "docs/process_traces/2026-09-10-side-threads/docs-thin-01-RESUME.md"]

You are in the linked worktree of branch `chore/2026-09-10-docs-thin` (HEAD
`ae5b09e7`, which contains main `a4bb8838`). Do NOT commit (the lead commits
by pathspec). Do not touch `/Users/edr/code/JouleWise`, any
`/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`.
No network. Precedence: this contract over the PR body over any other doc;
flag conflicts. The archive rule of this PR is `docs/X -> docs/legacy/X`
(pure `git mv`, content byte-identical), and historical records are never
rewritten — only LIVE reading surfaces get link repairs.

Findings being fixed (refuter records 06 Astra execution lens, 09 Opus
contract lens):

FIX-1 (should-fix, Opus §3). `RUN_STATE.md` lines 6–9 (the orientation
paragraph, OUTSIDE the generated marker-fenced region) name
`docs/process_traces/RESUME-2026-07-26.md`, `RESUME-2026-07-27.md` and
`RESUME-2026-07-28.md`; the last two were archived. Required: (a) archive the
sibling too — `git mv docs/process_traces/RESUME-2026-07-26.md
docs/legacy/process_traces/RESUME-2026-07-26.md` — so the dated set stays
together; (b) add its row to the move table in `docs/legacy/README.md` in the
same format as its siblings (and bump any count the README states, quoting the
old and new number); (c) repair the RUN_STATE sentence to the three
`docs/legacy/process_traces/RESUME-2026-07-2{6,7,8}.md` paths, changing no
other word. `python3 scripts/gen_state.py --check` must still exit 0 (the
paragraph is outside the fences; confirm by pasting the fence line numbers).

FIX-2 (should-fix, Astra F2 + Opus §5). Repair these live-surface pointers to
their `docs/legacy/...` targets, one path each, nothing else on the line:
- `docs/paper/results-fill-registry.md:132` — the `PLAN` source pointer to
  `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`. Before
  editing, run `python3 -m unittest tests.test_paper_first_use_ledger
  tests.test_paper_terms_lint tests.test_paper_comparison_placements
  tests.test_paper_reported_energy tests.test_paper_custody` and `grep -rn
  "results-fill-registry" tests/ scripts/` to learn whether any test or
  renderer pins that line's bytes or a digest of the file. If a pin exists,
  do NOT edit; report the pin (file:line) as a deviation instead.
- `docs/project_critique_review.html:880` — the link to
  `test_audit_2026-07-07.md` (the archived file is
  `docs/legacy/test_audit_2026-07-07.md`; use the correct relative form for an
  HTML file at `docs/`).
- `docs/specs/axi/sb_static_batch_verdict.md:200` — the evidence pointer to
  `docs/process_traces/2026-07-16-axi-sb-live-probes/axi-sb-b2.jsonl`.

FIX-3 (nit, Astra F4). `git diff --check a4bb8838..HEAD` reports six added
lines with trailing whitespace (the refuter's log is at
`/tmp/ref329-diff-check.log` if still present; otherwise re-run the command).
Remove the trailing whitespace ONLY on lines this branch ADDED and only in
files inside your WRITE_SCOPE; list any offending file outside your scope as a
deviation with file:line (do not touch it).

FIX-4 (bookkeeping). In
`docs/process_traces/2026-09-10-side-threads/docs-thin-01-RESUME.md` append
one dated line under its last section recording: sibling RESUME-2026-07-26
archived; three live pointers repaired (list them); base for review is
`a4bb8838`.

Verification to run and paste: `git diff -M --name-status a4bb8838..HEAD |
grep -v '^R100' ` (only M/A lines + the one new R100 you added should appear;
paste the whole output), `python3 scripts/gen_state.py --check` rc,
`python3 -m unittest tests.test_docs_freshness tests.test_gen_state` result
lines, the five paper test modules' result lines, `git diff --check
a4bb8838..HEAD` rc, and `git status --short` (must show only your scoped
paths as modified/renamed; do NOT commit).

Report (claude-codex-report/v1, genre implementation) as your FINAL MESSAGE:
what changed per FIX id with file:line, pasted evidence, deviations, and
"what the lead should double-check". Under 8000 bytes.
