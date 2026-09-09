WRITE_SCOPE: ["docs/contracts/window_liveness.md"]

# WINDOW-LIVENESS-DOCS-01 — final fix round (gpt-6-astra, medium, genre implementation; docs only)
Head 5cf1660f. The pedagogy + fidelity delta at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99da-pedagogy-delta-liveness-docs-astra-report.md
passed reconstruction and the 50-row table; cure exactly its findings: B1 (C5 ~:157 — qualify "refuses any start
object without a usable token" with "when neither exit check accepts an exit", consistent with C10 and
measurement_liveness.py:189–198); B2 (Code map pins: P1 → window_status.sh:94 and :107–108; C2 → run_night.py:102–103;
C4 → run_night.py:116–125; C5 → run_night.py:382; T7 → window_status.sh:96–99 — VERIFY each by reading the code at
this head before writing); A1 (gloss at first use: "courier-delivery" ~:193 — the program that emails the night's
result; "collector" ~:696 — the launchd-run measurement collection program; "watchdog" ~:699 — the agent-monitoring
LaunchAgent that evaluates arming ticks). Change nothing else. Acceptance: tests.test_docs_freshness rc 0 to a log;
git diff --check; no commit; header < 8192 bytes; report each edit with before/after.
