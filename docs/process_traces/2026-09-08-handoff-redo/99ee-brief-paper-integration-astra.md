WRITE_SCOPE: ["configs/paper_supply/supply_map.json","docs/contracts/paper_comparison_placements.md","docs/contracts/paper_supply_custody.md","docs/paper/results-fill-registry.md","tests/test_paper_comparison_placements.py","docs/decision_log.md","tests/test_paper_custody.py","tests/test_gen_state.py"]

# Paper integration tree — resolve the S2 + S3 + S7 merge conflicts (gpt-6-astra, HIGH, genre implementation)
Branch int/2026-09-08-paper-s2-s3-s7 at af8956ea = main 99a42edb + feat/2026-09-08-paper-S2 (31f39466, merged clean
after a union resolve of docs/decision_log.md) + feat/2026-09-08-paper-S3 (6c34cfe6) + feat/2026-09-08-paper-S7-reconciliation
(1f7cb8e0), the last two committed as WIP with CONFLICT MARKERS left in five files: configs/paper_supply/supply_map.json,
docs/contracts/paper_comparison_placements.md, docs/contracts/paper_supply_custody.md, docs/paper/results-fill-registry.md,
tests/test_paper_comparison_placements.py. The three lanes are each fully reviewed and LAND-verdicted; your job is a
SEMANTIC merge that keeps every lane's ruling, not a textual pick: S2 (D-179) = reported-energy X5 census text ("five
fields defined in paper_reported_energy.md … RETIRED_FALLBACK under D-174; no placement restored") + both pending
production roles; S3 (D-178) = X6/X7 rows with the v2 verdict-resolution-join wording (PROPOSED_STOP_FILL kept) + the
claim_evidence census/gate; S7 (D-177) = X13–X16 "ruled omission (D-177)" rows, the D-177 token in every X5 Missing-
evidence cell, the adjacency prose block, the phase-attribution limitation. Each marker hunk: read BOTH sides against
the lane rulings (docs at /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99be-*/13-magistrate-synthesis.md, /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bb-*/13-magistrate-synthesis.md,
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bc-*/13-magistrate-synthesis.md) and produce the row that satisfies all applicable lanes; the three placement
tables (placements contract, custody mirror, registry) must end IDENTICAL row-for-row (the S1 agreement test enforces
it — update its pins to the merged text and say so). supply_map.json: take the UNION of role/pending-role changes from
S2 and S3 (no production digests), then ONE hash-only repin of every fixture receipt/inventory digest against the merged
source census. docs/decision_log.md was union-resolved mechanically: verify there is exactly ONE D-176, D-177, D-178 and
D-179 entry and one index row each, in numeric order, with no duplicated blocks or index rows (dedupe if the union
duplicated D-176); update tests/test_gen_state.py EXPECTED_IDS/count pins if they moved (say which). Then remove every
marker (`grep -rn '^<<<<<<<\|^=======$\|^>>>>>>>'` must be empty).
Acceptance (rc-gated to a log; named modules ONLY — NEVER unittest discover or shard_tests; the lead owns the full
replay): tests.test_paper_reported_energy tests.test_paper_custody tests.test_paper_rendering tests.test_claim_side_bound
tests.test_analysis_ratio tests.test_paper_comparison_placements tests.test_paper_comparison_contract
tests.test_paper_successor_migration tests.test_paper_round7_artifacts tests.test_d165_rationale_census
tests.test_d117_floor_qwen25_1p5b_plan tests.test_gen_state tests.test_docs_freshness (env: JOULEWISE_BACKUP_ROOTS=
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise); run_kills.py --s3; git diff --check; no commit; header < 8192 bytes; report
per conflict file: each hunk's resolution and which lane rulings it satisfies.
