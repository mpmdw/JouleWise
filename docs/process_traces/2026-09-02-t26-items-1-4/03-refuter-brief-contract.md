WRITE_SCOPE: []
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: review

# REFUTE (contract lens) — T26 items 1 + 4 install and the Q1/Q2 process-rule install

Worktree `/Users/edr/code/JouleWise-wt-t26-a` (branch `feat/2026-09-02-t26-install`,
five commits over main 6075389a; head 2d24ef70; everything committed).
Read-only: write NOTHING in the tree; `TMPDIR` preset under the scratchpad.
Named test modules only; never `discover`. No codex/claude launches.

Rulings (the AUTHORITY the landing must match):
- `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
  item 1 (`:45-110`: ruled text, Enforcement (i)/(ii), Where recorded) and
  item 4 (`:255-298`).
- `docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md`
  Q1 ruled text + S1/S2/S3 synthesis clauses and its "Installation" section.

S2 ORDERING (mandatory): BEFORE opening `git diff 6075389a..HEAD` or the
seats' reports, read the three rulings and write your OWN clause list — one
row per proposition a single edit could falsify. Expect at least: the
`open (installs via <TASK-ID>)` form in the log's How-To; the closed status
vocabulary {accepted, adopted, ratified, open, proposed, superseded,
recorded, executed, adjudicated} tested on every index Status cell's leading
token; the `open \(installs via ([A-Z0-9-]+)\)` regex with kernel-task
existence AND a `kind: decision` dependency targeting that D-id; the
`D-\d{3}[a-z]?` regex widening; the dependency object shape
{kind, target, strength: hard, scope: start, state: pending, evidence: null,
required}; "S9 SHORTLIST items marked gates the mint / gates windows are
registered" (which rows, on which tasks?); D-170 entry carrying all four
verdicts by pointer; M0 one-line pointer; NO change to orchestration.md or
the council skill for item 1; item 4's test over
`docs/process_traces/<date>/**/*MAGISTRATE-RULING*.md` with date ≥
2026-08-29, the three trigger headings, the `## Executed evidence` section
with a fenced `$ ` + `exit` line OR a `file:line` citation; D-160 R-5
amended by the new entry never edited in place; charter §4 DEFERRED (no
charter byte change — verify `shasum -a 256 docs/process/coldgate_charter.md`
= 099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81); the
consult-brief template "Executed:" block; Q1 home in bridge_protocol §1
after the ACCEPTANCE/VERIFICATION bullets + §10 inventory row + M0 pointer;
S1 mandatory `## Clause map` heading test over custodied `*-impl.md` dated ≥
2026-09-03; S2 text present; Q2 as D-160 amendment with JSON pointer + both
observed values + "or artifact-pair exhibit" words in the consult-brief
"Executed:" block; the T26 trace README and the process-rules custody
directory. Record the list FIRST under `## Independent clause list`.

Then, per clause: `file:line` of the landed text, CONFIRMED / DIVERGES /
MISSING, and whether a test binds it (name it) or only prose does. Specific
checks:
1. Does `test_decision_index_status_vocabulary_is_closed` actually read the
   LEADING token, and does `test_open_decisions_name_an_installing_kernel_task`
   check BOTH the kernel task's existence AND the `kind: decision` dependency
   targeting the row's D-id? Cite the assertion lines.
2. Item 1 says the S9 SHORTLIST "gates the mint / gates windows" items are
   registered under the rule in the ruling's implementation commit. Are
   they? List the `kind: decision` dependencies now in
   `docs/process/state_kernel.json` and compare with the S9 SHORTLIST file
   (`docs/process_traces/.../ruled-not-installed-sweep/`). Anything the
   ruling required that is absent is a finding.
3. Item 4's test: does it fire on `## Addendum` as well as `## Rulings` /
   `## RULED`? Does "at least one fenced block holding a `$ ` argv line plus
   an `exit` line, OR a `file:line` citation" match the code — or does the
   code accept a weaker or stronger shape? Is the date cut-off applied to
   the DIRECTORY date, not the filename?
4. Is any status cell in the decision index now outside the closed set —
   run the tests and also grep the index yourself.
5. Did the landing touch `docs/orchestration.md` or the council skill for
   item 1 (the ruling says no)?
6. Does D-170's body carry all four verdicts by pointer to the ruling file,
   plus the Q1/Q2 paragraph the process-rules ruling required?
7. `python3 -m unittest tests.test_docs_freshness tests.test_gen_state` and
   `python3 scripts/gen_state.py --check` — paste tails.

## Deliverable

FINAL message = `claude-codex-report/v1` review envelope with
`verdict.findings` (id, severity blocker/should_fix/nit, `file:line`,
`ruled_text`, `landed_text`, `why_they_differ`) and `verdict.clause_table`
(your independent list with CONFIRMED/DIVERGES/MISSING and the binding
test or "prose only"). No fixes; no writes.
