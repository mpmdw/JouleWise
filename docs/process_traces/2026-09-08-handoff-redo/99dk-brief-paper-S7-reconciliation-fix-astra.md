WRITE_SCOPE: ["docs/paper/protocol/prospective-comparison-protocol.md","docs/contracts/paper_comparison_placements.md","docs/contracts/paper_supply_custody.md","docs/paper/results-fill-registry.md","docs/paper/round7/successor-migration-inventory.md","docs/paper/round7/fill-checklist.md","docs/decision_log.md","tests/test_paper_comparison_placements.py","tests/test_paper_successor_migration.py"]

# Paper S7 reconciliation — fix round (gpt-6-astra, medium, genre implementation; docs + tests)
Head 1dcbf0b2 on feat/2026-09-08-paper-S7-reconciliation. Cure the Opus findings at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99dj-ref-paper-S7-reconciliation-opus-review.md exactly: (2+7) protocol ~:61–62 — replace "an issued floor (a
published resolution guard for assigned-energy differences)" with "a floor (the registered resolution guard for
assigned-energy differences, called the cell floor in P.3)" so the class matches :181 exactly and the gloss no longer
uses an unbuilt construction; (3) protocol ~:460 — lift the conditional into prose: "Where the successor reports phase
attribution, it is reported without an instrument phase-accounting characterization…" and delete the HTML-comment
conditional; (4) add a `D-177` token to the X5 Missing-evidence cell in ALL THREE tables (placements, custody
mirror, registry) so `test_all_three_tables_agree` guards the adjacency note, and add one assertion that the
adjacency prose block exists in the placements contract; (5) decision_log.md:222 status word → `adopted` (match
neighbours); (6) restore the concrete numbers in successor-migration-inventory.md ~:43 ("planned n=40 / n=16, fresh
null blocks and workload counts remain design requirements") alongside the P.2 reference; (9-nit) gloss the bare
STOP_FILL beside PROPOSED_STOP_FILL in fill-checklist.md. Do NOT touch the verbatim paragraph (finding 8 is recorded
debt). Acceptance (rc-gated to a log, env JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise):
tests.test_paper_comparison_placements tests.test_paper_successor_migration tests.test_d165_rationale_census
tests.test_gen_state tests.test_docs_freshness; git diff --check; no commit; header < 8192 bytes; report before/after per edit.
