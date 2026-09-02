# Cold-gate packet — gate-ledger cell splitter, 2026-09-02 (session 540125d5)

Mandatory trigger (rule 11 / charter §3): a THIRD round on the same
component and a REVERSAL of a fix-round decision. Branch
`feat/2026-09-02-t26-gateledger` @ `2983cdd4`, checked out detached at
`/Users/edr/code/JouleWise-wt-t26-c2` (read-only for you; write nothing there;
scratch under a subdirectory you create in
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`).
Python `/Users/edr/code/JouleWise/.venv/bin/python`; tests need `TMPDIR`
exported to your scratch dir; never `unittest discover`; do not launch codex
or claude.

Charter: `docs/process/coldgate_charter.md`, expected sha256
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. Read §3–§5,
§8. Read set: ONLY this packet, the files in this directory, and the primary
evidence cited here. No README/RUN_STATE/TASK_QUEUE/orchestration/
agent_playbook, no CLAUDE*.md, no memory files. Disclose contamination.

## History (mechanical)

- Round 0 (landing): `_split_table_row` was a naive `line.split("|")`.
- Round 1 (refuters luna 199 / sol 200 → Sol 205, commit `1529b09a`): replaced
  with a stateful scanner that (a) treats a backslash-escaped `\|` as literal
  and (b) does NOT split on a `|` inside a backtick code span; pinned by
  `tests/test_check_gate_ledger.py:121` `test_pipe_inside_backticked_gate_item_does_not_lose_row`
  (input `| 4 | gate \`escaped \| and raw |\` |` expected to keep the row).
- Round 2 (terra 208 delta I1 → bench, commit `2983cdd4`): an escaped
  backtick outside a span opened scanner state; guard added at
  `scripts/check_gate_ledger.py:28-34`, test at `:130`. luna 215 delta: CLEAN,
  classified NEW.
- Opus counter-review (`207b-opus-counter-review.md`, S2 + prune section):
  claims (b) contradicts the GFM Tables extension — cell splitting is a
  pre-pass before inline parsing, a RAW `|` inside backticks DOES split, and
  the spec's own example escapes the pipe INSIDE the code span
  (`| b \`\|\` az |`). Consequence: for `| 1 | gate \`a | b\` | RUN evidence.txt |`
  GitHub renders four cells truncated to three (Evidence column shows
  `` b` ``), while the checker reads `RUN evidence.txt` and passes —
  permissive divergence. Proposed cure: delete the code-span machinery,
  13-line backslash-only splitter; `_ledger_rows:76` `len(cells) != 3` →
  `len(cells) < 3` taking `cells[2]` (mirror GitHub's truncation); invert
  the `:121` test; keep a companion asserting the escaped form
  `| 4 | gate \`a \| b\` | RUN evidence.txt |` passes. Mutation M1 (run,
  reverted): with that splitter 14/15 pass and only `:121` fails.

## Primary evidence

- `scripts/check_gate_ledger.py` (`:19-60` splitter; `:63-81` `_ledger_rows`).
- `tests/test_check_gate_ledger.py:121-139`.
- GFM spec, Tables (extension) §6.7 — you may consult the spec text from
  memory or fetch it; state which. The dispositive sentence is the one about
  escaping a pipe "including inside other inline spans" and the example
  whose cell content is a code span containing an escaped pipe.
- Empirical: you cannot render on GitHub from here. If you can state a
  reproducible way the magistrate can verify GitHub's actual rendering
  (e.g. the exact PR-body row to paste and what the rendered table must
  show), include it — the magistrate will run that live before adopting.

## Questions

**L1.** Is Opus's reading of GFM correct — does GitHub split a table cell on
an unescaped `|` inside a backtick code span? ADOPT / REJECT with the spec
citation.

**L2.** If L1 ADOPT: rule the cure. (a) as proposed (delete code-span state;
backslash-only split; `< 3` truncation taking `cells[2]`; inverted test +
escaped-form companion); (b) keep the scanner and only add the truncation;
(c) other. State the biting counterfactual and what it does NOT decide.
Also rule whether truncating a >3-cell row (mirroring GitHub) or REFUSING it
("row has 4 cells") is the fail-closed choice — the checker's job is to
refuse mistakes, and a row GitHub silently truncates is itself a mistake.

**L3.** Same-signature classification: are rounds 0, 1, 2 and this one the
same class ("the checker's cell model ≠ GitHub's")? If yes, say what the
STRUCTURAL cure is such that no round 4 exists (e.g. the checker must
implement exactly GFM's two rules — escaped pipe literal, everything else
splits — and nothing else, with a table-driven test over the spec's own
examples).

Deliverable: `## Disclosure` (charter sha256; contamination), then L1, L2, L3
each with verdict, operative text/code shape, counterfactual, not-decided.
