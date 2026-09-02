ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: ["scripts/check_gate_ledger.py", "tests/test_check_gate_ledger.py", ".github/workflows/gate-ledger.yml", ".github/pull_request_template.md"]
GENRE: implementation
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FIX round 3 — gate-ledger checker (branch feat/2026-09-02-t26-gateledger @ ec6f97ea)

DETACHED WORKTREE `/Users/edr/code/JouleWise-wt-t26-c2` @ ec6f97ea. Do NOT
commit/rebase/checkout; never canonical `unittest discover`; the magistrate
commits. Run tests as `python3 -m unittest tests.test_check_gate_ledger
tests.test_docs_freshness`.

AUTHORITY (read both first, in this order):
1. `docs/process_traces/2026-09-02-t26-item2/16-MAGISTRATE-RULING-gateledger-splitter.md`
   — the cold-gate ruling L1/L2/L3. Its §L2 and §L3 are DICTATED code shapes;
   apply them verbatim (the seat text in `14-seat-cold-fable-222.md` §L2 has
   the reference splitter — use it).
2. `docs/process_traces/2026-09-02-t26-item2/13b-opus-207b-counter-review.md`
   — Opus 5 counter-review; items S1–S5, N1–N9 below are dictated from it,
   with the magistrate's rulings where Opus asked a question.
Current code: `scripts/check_gate_ledger.py` (171 lines), tests (191 lines,
15 tests), workflow, template. Do NOT touch `docs/orchestration.md` or
`docs/decision_log.md` (B1 — the D-170 entry lands on a sibling branch that
merges first; not your problem).

## Dictated closures

F-1 (ruling L2/L3 — the splitter). Replace `_split_table_row` with the
GFM-exact backslash-parity splitter (consume the escaping backslash of `\|`;
`\\|` splits; `\\\|` does not; drop leading/trailing empty cells; strip);
docstring states "no inline syntax is modelled, on purpose". Delete all
code-span state and the escaped-backtick guard. Add the table-driven spec
test from ruling §L3 (all ten rows, exact expected lists).

F-2 (ruling L2 — arity). `_ledger_rows` returns `(rows, malformed)`; a row
whose first cell is a ledger key (1..12) with cell count ≠ 3 is recorded in
`malformed` with the defect line
`gate-ledger: item {key}: row has {n} cells, expected 3 (an unescaped | splits a cell even inside backticks; write \|)`;
`check()` skips missing/duplicate/evidence logic for malformed keys. Tests:
invert `test_pipe_inside_backticked_gate_item_does_not_lose_row` (raw pipe
→ rc 1, stdout exactly that one line, renamed to say what it now pins);
companion escaped form `| 4 | gate \`a \| b\` | RUN evidence.txt |` → rc 0
`12/12 RUN`; `| 4 | gate 4 | RUN evidence.txt | extra |` → `row has 4 cells`;
`| 4 | gate 4 |` → `row has 2 cells`; keep the escaped-tick test at `:130`
UNCHANGED (valid GFM that must pass under any splitter).

F-3 (Opus S1, RULED: refuse, don't model). The Evidence cell is plain text.
A cell containing a backtick → defect
`gate-ledger: item {key}: evidence cell must be plain text (no backticks)`.
Test: `` RUN `evidence.txt` `` and a backticked item-12 sha → that message,
rc 1. Template line 3 says "plain text, no backticks".

F-4 (Opus N1, RULED). Evidence is a committed artifact (repo-relative path
at the PR head) or a commit sha — no `:N`, no `#anchor`, no URL. State it in
the template in one clause. A `:N` suffix → the existing "neither a commit
nor a path" message is fine; no new branch.

F-5 (Opus N2 + ruling §L3 flag — table context, refuse don't model). Rows
are taken only from the FIRST contiguous block of pipe-lines after the
ledger heading (contiguous = no blank line, no non-pipe line). A pipe-line
starting with a ledger key that appears anywhere else in the section →
defect `gate-ledger: item {key}: ledger row outside the ledger table`.
Fences are NOT modelled; a ledger quoted inside a fence BEFORE the real
section will be read as the section (fail-closed: twelve NOT-RUN lines) —
say exactly that in one comment. Tests: a numbered row after a blank line
→ the "outside" line; the quoted-fence body from Opus P12 → rc 1 (whatever
the lines, assert rc 1 and no `12/12`).

F-6 (Opus N3). A pipe-line inside the ledger block whose first cell is not
a digit-string in 1..12 and is not the header/delimiter row → defect
`gate-ledger: unrecognised ledger row: {first cell!r}` (bold `**1**` is the
probe). Test it.

F-7 (Opus N4). `if not rows and not malformed` and the heading was never
seen → exactly one line
`gate-ledger: no '## Gate ledger (D-118 / D-121)' section in the PR body`
(no twelve `missing` lines). Test: heading drift `## Gate ledger (D-118/D-121)`.

F-8 (Opus N5). Lowercase/mixed-case `run x` → defect
`gate-ledger: item {key}: evidence must start with RUN (uppercase)`. Test it.

F-9 (Opus N6). Section termination and heading detection both use the
stripped line. Test: indented `  ## Summary` terminates the section.

F-10 (Opus N7). Add `reopened` to `types:`.

F-11 (Opus N8). Add `test_valid_path_matches_gen_state_check_pointer`: load
`scripts/gen_state.py` via `importlib` (it is not a package) and assert
`_valid_path` and `gen_state._check_pointer` agree on a fixed list of ≥ 10
pointers (absolute, `~`, `..`, `://`, plain file, missing file, dir, `:N`
suffix, empty, backslash). If `_check_pointer`'s signature makes that
awkward, say so in the report and assert on the shared rejection set only.

F-12 (Opus S3). `permissions:\n  contents: read` above `jobs:` in the
workflow.

F-13 (Opus S4). `test_workflow_text_pins_round1_fixes` in
`tests/test_check_gate_ledger.py` (NOT test_docs_freshness — scope): reads
`.github/workflows/gate-ledger.yml` and asserts (a) `ref: ${{
github.event.pull_request.head.sha }}` present, (b) `edited` and `reopened`
in `types:`, (c) `continue-on-error` absent, (d) `permissions:` with
`contents: read` present, (e) `fetch-depth: 0` present.

F-14 (Opus S5). Template line 3 clause: "…or `NOT-RUN`, which the advisory
`gate-ledger` check reports as a defect until the row is filled." plus the
F-3/F-4 clauses. Test `test_shipped_template_is_refused_until_filled`: run
the checker on the template itself → rc 1 and exactly twelve `NOT-RUN` lines
(this pins template↔KEYS parity: twelve labels, numbered 1..12, once each).

F-15 (Opus N9). One sentence in the workflow header comment: every fresh PR
is red by construction (the template seeds twelve NOT-RUN) — deliberate.

## Mutation check (report each: KILLED by <test> / SURVIVED)

M1 restore code-span tracking in the splitter → KILLED by the spec table.
M2 `len(cells) != 3` back to a silent `continue` → KILLED by the arity tests.
M3 delete `ref: … head.sha` from the workflow → KILLED by F-13.
M4 delete `permissions:` → KILLED by F-13.
M5 revert to `line.split("|")` → KILLED by the `f\|oo` row.

## ACCEPTANCE

- `python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness` tail (expect ≥ 27 tests OK).
- `python3 scripts/check_gate_ledger.py --root . --body .github/pull_request_template.md; echo EXIT=$?` → twelve NOT-RUN lines, EXIT=1.
- `git status --porcelain` shows only in-scope files; `git diff --stat`.
- Same-signature statement: classify every closure against the ruling's
  class definition ("hand-rolled cell model ≠ GFM's one rule") — which
  closures remove modelling, which add refusals; state what remains
  modelled (must be: nothing but the pipe rule).
- `## Clause map`: one row per closure F-1…F-15 — production `file:line`,
  biting test `file:line`, counterfactual.
