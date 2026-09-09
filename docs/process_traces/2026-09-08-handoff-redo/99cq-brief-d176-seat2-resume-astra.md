WRITE_SCOPE: ["joulewise/night_plan_writer.py","joulewise/night_gate.py","scripts/install_night_agent.sh","scripts/run_night.py","joulewise/arm_readiness.py","joulewise/t0_rehearsal.py","scripts/rehearse_t0_unattended.py","configs/production_custody_inventory.json","tests/test_night_gate.py","tests/test_install_night_agent.py","tests/test_run_night.py","tests/test_t0_rehearsal.py","tests/test_night_plan_writer.py","tests/test_rehearse_t0_unattended.py","tests/test_arm_readiness_schemas.py","docs/contracts/pack_night_go_receipt.md"]

# D-176 seat 2 — RESUME with the roots/locators ruling (gpt-6-astra, HIGH, genre implementation)
Your partial landing is committed at 8eae7492 (v3 plan, serialization, installer, watchdog compatibility; 179 tests
OK). F1/F2 are now RULED by a three-seat gate; the synthesis at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99cm-coldgate-packet-d176-roots-locators/13-magistrate-synthesis.md GOVERNS (10/11/12 beside it are evidence). Install its items 1–2, 4–8 and the shared
item 9 exactly, plus the "§10.3 seat-2 rulings (2026-09-08)" block in the contract propagated to §§2–6, key tables
and YOUR §9 rows only (seat 3 runs in parallel and owns the consumer-side of item 3 and the launch_window flags —
call them as item 8 lists; pin the argv in a test that tolerates seat 3's landing). Baseline anchors
(BASELINE_MANIFEST/DIGEST) are SUPERSEDED for this runner-owned lane — do not block on them. Touch
joulewise/arm_readiness.py ONLY at the constants area (the census constant + resolver) and test_arm_readiness_schemas.py
only for the resolver's tests. Preserve WINDOW-STATUS-GUARD-CENSUS-01 in run_night.py (complete chain.started marker
before any probe; start token by atomic replace). Every clause → regression with the §9 counterfactual (stale census
false-PASS, nested rehearsal custody, equal-to-parent, symlinked root, env override shrinking the census, selected
instead of self-written ARM, second manifest candidate, pack_root digest mismatch at each of the three points, GO on a
refused night, launcher argv missing any of the eight flags).
Acceptance (rc-gated to a log): tests.test_night_gate tests.test_install_night_agent tests.test_run_night
tests.test_t0_rehearsal tests.test_night_plan_writer tests.test_rehearse_t0_unattended tests.test_arm_readiness_schemas
tests.test_docs_freshness (drop nonexistent modules and say so); git diff --check; no commit; header < 8192 bytes;
report = per-clause map (synthesis item → file:line → test → counterfactual) + NEEDS_RULING for any residual gap.
