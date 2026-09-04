ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: ["tests/test_docs_freshness.py","tests/test_gen_state.py","docs/contracts/bridge_protocol.md","docs/decision_log.md","docs/agent_playbook.md","docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md"]
GENRE: implementation
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FIX ROUND (Opus counter-review) — T26 items 1+4 lane, worktree `/Users/edr/code/JouleWise-wt-t26-a` @ 10845c14

Branch `feat/2026-09-02-t26-install`. You are the fixing seat for the
findings of the Opus counter-review (read-only copy on this checkout:
`docs/process_traces/2026-09-02-t26-items-1-4/14-opus-counter-review.md`,
untracked — do NOT touch it). Do NOT commit (linked worktree; the magistrate
commits). Do NOT run canonical `unittest discover`; run
`python3 -m unittest tests.test_docs_freshness tests.test_gen_state` and
`python3 scripts/gen_state.py --check`. Do NOT edit
`docs/process/state_kernel.json` or `TASK_QUEUE.md` (bench-only; the S9 rows
named below are being registered by the magistrate in parallel — your D-170
sentence names them by ID; do not wait for them). Never `git checkout`,
`stash`, `rebase`.

Each item below carries its dictated closure shape. If a shape is wrong
against the code you read, return NEEDS_RULING naming the item — do not
improvise a different shape.

## SF2 — census pin will break on the next dated ruling
`tests/test_docs_freshness.py:628-637`
`test_dated_magistrate_rulings_carry_executed_evidence` pins the selected
census to an exact two-path list. The sibling branch
`feat/2026-09-02-t26-gateledger` adds
`docs/process_traces/2026-09-02-t26-item2/16-MAGISTRATE-RULING-gateledger-splitter.md`
(it carries `## Executed evidence`), so the pin fails at integration.
CLOSURE: keep `self.assertTrue(selected)`; replace the `assertEqual` on the
full list with `assertIn` of each of the two known paths in the
relative-path list, and keep the per-path shape loop. Update the comment so
it no longer claims "exactly the two". Add nothing else.

## SF3 — clause-map cell count vs contract
`tests/test_docs_freshness.py:459-477` `_assert_clause_map` demands exactly
three cells, while `docs/contracts/bridge_protocol.md:61-63` reads "three
cells per row: production site …, biting assertion …, and counterfactual …"
AND the same §1 paragraph (`:55-61`) says each row quotes "the phrase with
ruling `file:line`", which a reader can take as a fourth column.
CLOSURE (test side, contract unchanged in meaning): locate the three
required columns by header index (case-insensitive match on `production
site`, `biting assertion`, `counterfactual`); require each body row to have
the SAME number of cells as the header, and the three required cells to be
non-empty; `NOT PINNED:` rows are recognised by the production-site cell
(not blindly cells[0]). Then in `bridge_protocol.md:61-63` replace "three
cells per row" with "at least these three cells per row (a quote column is
permitted)". Add a positive control in the existing shape test for a
four-column map (header with a leading `Ruling quote` column) and a
negative control for a row with a cell count different from the header.

## SF4 — comment arithmetic
`tests/test_gen_state.py:603-608`: comment ends "116 + 3 = 119" but the
assertion is 120. Four rows were added on this lane: T26-RULING-INSTALL-01,
ED-BRANCH-PROTECTION-E1-01, ED-GATE-LEDGER-E2-01 (verify the exact IDs
against `EXPECTED_IDS` in the same file), and D110-MINT-DEP-RECONCILE-01.
CLOSURE: correct the comment to name all four and read "116 + 4 = 120".

## SF5 — stale citation to a superseded paragraph
`docs/decision_log.md:10529` (the D-170 body) cites
`COLD-GATE-RULING.md:270-282`; that span is the ORIGINAL enforcement
paragraph, superseded by the dated addendum at
`docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md:317-331`
(read both spans on this checkout and confirm the line numbers before
citing — if they differ, cite what you measured). CLOSURE: the quote keeps
its source span `:269-279` (or the measured span of the quoted text) and
the sentence gains "; the enforcement paragraph at `:270-282` is superseded
by the dated addendum at `:317-331`" with measured numbers.

## SF1 (doc half only) — D-170 records the S9 registration
Ruling §B4 (`docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md:245-247`)
says the S9 rows register at the bench with the hard/start/pending D-170
dependency. The kernel rows are the magistrate's; the D-170 body must carry
the affirmative clause. CLOSURE: in the D-170 body, in the paragraph that
describes where the `kind: decision` dependency sits (near `:10561`), add
one sentence: "Per the 2026-09-02 cold-gate ruling §B4, the seven S9
sweep rows S9-01B-REFUSAL-PRODUCER-CHECK-01, S9-02-W10-SCOPE-P256-M1-01,
S9-03-GAMMA-PREFILL-PROMPT-OWNER-01, S9-04-GAMMA-ROSTER-CHECK-01,
S9-05-CAL-SCREEN-FLOOR-RULING-01, S9-06-WINDOW-T0-GO-RECEIPT-GATE-01 and
S9-12-L10-REHEARSAL-SCHEDULE-01 register in the kernel carrying the same
hard-start pending dependency on D-170, so limb 3 of the status rule is
satisfiable by more than one task." (Cite the ruling by path + measured
line.)

## NIT1 — name the ruling path for S1/S2
`docs/contracts/bridge_protocol.md` §1 clause-map paragraph (`:55-73`) cites
"(S1, shape test)" and "(S2)" with no path; the ONE-home table row at
`:823` says "the T26 process-rules ruling is the record" with no path;
`docs/agent_playbook.md:60` says "(process-rules ruling 2026-09-02)".
CLOSURE: at all three sites add the path
`docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md`
(confirm it exists on this checkout; if it exists only on main at
`/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-process-rules/`,
still cite the repo-relative path).

## NIT2 — gloss two terms at first use (Ed's writing standard)
`bridge_protocol.md:64` "biting assertion" and `:72` "dated ≥ 2026-09-03".
CLOSURE: after "biting assertion (test method `file:line`)" add ", i.e. the
assertion that FAILS under the row's counterfactual"; after "dated ≥
2026-09-03" add " (the date in the report's filename or first heading, on
or after the rule's ratification day — earlier reports are not re-graded)".

## NIT3 — `NOT PINNED:` scope
`bridge_protocol.md:66`. CLOSURE: after "— or `NOT PINNED: <reason>`" add "
in the production-site cell, in which case the whole row is skipped by the
shape test and handed to the refuters as a finding". Keep the sentence
about refuters that follows consistent (do not duplicate it).

## NIT4 — duplicate T-0 amendment paragraph
`docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:85`
carries a mid-file "**Horizon — AMENDED by cold gate 2026-08-28 (T26 item
3):**" paragraph added on this branch. The sibling branch
`feat/2026-09-02-t26-liveness` records the same amendment in custody form
(inline `[STRUCK 2026-09-02 …]` marker at the struck sentence plus an EOF
`## Addendum 2026-09-02 — item 3 liveness bound (T26 cold gate)`), and that
lane merges after this one. CLOSURE: DELETE the mid-file paragraph on this
branch (restore `:85` to what main has: `git diff main -- <file>` must be
EMPTY afterwards). Nothing else in that file.

## NIT5 — evidence-pointer constraint undocumented
`scripts/gen_state.py` `_check_pointer` accepts, for a satisfied
`kind: decision` dependency, only an evidence pointer of the form
`tests/<file>.py::<TestClass>::<test_method>` (read the function and quote
the accepted grammar precisely). `docs/decision_log.md:22-30` (How-To) says
"an evidence pointer to the regression" without the grammar. CLOSURE: add
one sentence to that How-To bullet stating the accepted pointer grammar with
`scripts/gen_state.py` `file:line` cited.

## NIT9 — restore the `accepted` gloss
`docs/decision_log.md:14`: main read "`accepted` (binding until revisited)";
this branch reads "`accepted` (binding design choice)". CLOSURE: "`accepted`
(binding design choice, binding until revisited)".

## Clause map
Return under `## Clause map` a table with header `| Ruling quote | Production site | Biting assertion | Counterfactual |`
— one row per SF2/SF3 change (the test edits) with the counterfactual you
EXECUTED (mutant → named assertion fails → restored). Doc-only items list
`NOT PINNED: doc-only` in the production-site cell.

## Report
Final message: claude-codex-report/v1 envelope, then `## Clause map`, then
`## Executed evidence` with the two-module suite tail, `gen_state --check`
exit, the SF2/SF3 counterfactual runs, `git diff --stat`, and `git diff
main -- docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`
(must print nothing). Do not end the turn before all items are done or
returned as NEEDS_RULING.
