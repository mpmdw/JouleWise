# REFUTE (execution lens) — T26 items 1 + 4 + Q1/Q2 install: do the new tests bite?

You are an Opus 5 execution-lens refuter for the JouleWise magistrate.
Worktree `/Users/edr/code/JouleWise-wt-t26-a2` (DETACHED at 2d24ef70 = head of
`feat/2026-09-02-t26-install`; five commits over main 6075389a). You MAY
edit files there ONLY as counterfactual mutations, and MUST revert each one
with `git checkout -- <file>` immediately after its test run; the tree must
be byte-clean (`git status --short` empty) at exit — verify and state it.
Never commit. Never run `python3 -m unittest discover`; name modules. Set
`TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp-opus-a2`
(mkdir it). Do not launch codex or claude. Do not read
`/Users/edr/code/JouleWise-wt-t26-a` (another seat is there).

Authority: `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
items 1 (`:45-110`) and 4 (`:255-298`);
`docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md`
Q1 + S1/S2. Landed: `git diff 6075389a..HEAD`. The four new tests are in
`tests/test_docs_freshness.py` (`test_decision_index_status_vocabulary_is_closed`,
`test_open_decisions_name_an_installing_kernel_task`,
`test_dated_magistrate_rulings_carry_executed_evidence`,
`test_custodied_impl_reports_carry_clause_map`,
`test_bridge_protocol_clause_map_pins_s1_and_s2`) plus `tests/test_gen_state.py`.

Suite for each mutation:
`python3 -m unittest tests.test_docs_freshness tests.test_gen_state` — record
KILLED by <test> / SURVIVED.

Named counterfactuals (execute all, then add your own):
M1  in `docs/decision_log.md` index, change one row's status to `decided` → vocabulary test must kill.
M2  change one row's status to `Accepted` (capitalised) → report which way the test goes and whether that is the ruled behaviour.
M3  change a row to `open (installs via NO-SUCH-TASK-01)` → must kill (task absent).
M4  change a row to `open (installs via <an EXISTING task id that has NO kind:decision dependency on that D-id>)` → must kill on the dependency check, not the existence check (state which assertion fired).
M5  add an index row `D-150c` with a bad status → must be seen by the widened `D-\d{3}[a-z]?` regex (report whether the test iterates it).
M6  in `docs/process/state_kernel.json`, flip the T26-RULING-INSTALL-01 decision dependency `state` to `satisfied` with `evidence: null` → `python3 scripts/gen_state.py --check` must refuse (paste the line).
M7  in `docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md`, delete the `## Executed evidence` heading → item-4 test must kill.
M8  same file: keep the heading but empty the fenced block of its `exit` line and remove every `file:line`-shaped citation → must kill (check the regex; is `:162-260` treated as a file:line citation? should it be?).
M9  create a NEW file under TMPDIR? No — instead: copy a pre-2026-08-29 ruling (e.g. any `docs/process_traces/2026-08-2[0-8]-*/**/*MAGISTRATE-RULING*.md`) into a directory named `docs/process_traces/2026-09-09-probe/` in the worktree with its evidence section stripped → must kill (prospective date applied to the DIRECTORY date); then `rm -rf` that directory and confirm clean.
M10 create `docs/process_traces/2026-09-09-probe/foo-impl.md` WITHOUT `## Clause map` → S1 test must kill; with a dated dir `2026-09-01-probe/` it must NOT (prospective ≥ 2026-09-03). Remove afterwards.
M11 in `docs/contracts/bridge_protocol.md`, delete the S2 sentence ("enumerates the ruling's clauses independently") → `test_bridge_protocol_clause_map_pins_s1_and_s2` must kill.
M12 in `tests/test_gen_state.py` EXPECTED_IDS remove `ED-D118-NA-TIER-E2-01` → must kill (sanity that the census binds).

Also: run `python3 scripts/gen_state.py --check` on the clean tree and paste
its last line; confirm `shasum -a 256 docs/process/coldgate_charter.md` =
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81.

Deliverable (your final message, no file writes outside TMPDIR): a report
with a `## Mutations` table (id, mutation, KILLED/SURVIVED, killed_by
test:line), `## Findings` (each: severity, file:line, counterfactual input,
observed outcome — a SURVIVED mutation the ruling wanted killed is a
should_fix at least), `## Tests` tails, `## Tree clean at exit` with the
`git status --short` output. Same-signature statement: first round — say so.
No fixes.
