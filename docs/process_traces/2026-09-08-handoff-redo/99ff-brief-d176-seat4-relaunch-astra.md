WRITE_SCOPE: ["scripts/run_night.py","joulewise/t0_rehearsal.py","tests/test_run_night.py","tests/test_t0_rehearsal.py","tests/test_launch_window.py","docs/contracts/pack_night_go_receipt.md"]

# D-176 seat 4 — RELAUNCH with the G7 ruling (gpt-6-astra, HIGH, genre implementation)
Worktree feat/2026-09-08-d176-seat4-rehearsal at 4d72e524 with your intake run's UNCOMMITTED B4 regression in the tree
(report 99fd; keep it). The G7 ruling is at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99fe-magistrate-ruling-g7-control.md — install it as
"§10.5 G7 control (2026-09-08)" in the contract and implement items 1–5 exactly. Everything else in the original seat-4
brief (/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99fb-brief-d176-seat4-astra.md) stands: the purpose=T0_REHEARSAL GO production path with the 2×2 table; G5
evaluating joulewise.pack_night_go_receipt.v1 recomputing C1–C5 (D-149 schema refused); the G7 producer + acceptance per
the ruling; the four-case purpose/root regressions through the seat-3 consumer; §9 rows B4/S1/S4/N1 pinned; §7.1 row.
Do NOT edit joulewise/arm_readiness.py or joulewise/night_gate.py (the census-cure seat owns them; call the predicate
as the contract names it). Baseline anchors are superseded for this lane.
Acceptance (rc-gated to a log; named modules ONLY, NEVER discover/shard; end your turn after the named acceptance):
tests.test_run_night tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_docs_freshness;
git diff --check; no commit; header < 8192 bytes; report = per-clause map + the G7 artifact's exact JSON shape.
