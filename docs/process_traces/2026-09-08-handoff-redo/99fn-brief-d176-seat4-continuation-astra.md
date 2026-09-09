WRITE_SCOPE: ["scripts/run_night.py","joulewise/t0_rehearsal.py","scripts/launch_window.py","joulewise/arm_readiness.py","scripts/rehearse_t0_unattended.py","tests/test_run_night.py","tests/test_t0_rehearsal.py","tests/test_launch_window.py","tests/test_rehearse_t0_unattended.py","tests/test_arm_readiness.py","docs/contracts/pack_night_go_receipt.md"]

# D-176 seat 4 — CONTINUATION with the G7 addendum rulings (gpt-6-astra, HIGH, genre implementation)
Worktree feat/2026-09-08-d176-seat4-rehearsal, now = your partial work (99fh) + the census cure merged (int head 07681e95;
§10.4 precedes §10.5 in the contract). The addendum to the G7 ruling at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99fe-magistrate-ruling-g7-control.md items 6–9 answers your F1/F2: (6) PRE-ARM ADMISSION in the consumer
(joulewise/arm_readiness.py — you now own the admission step only; preserve every census-cure edit byte-for-byte
elsewhere in that file): read plan bytes + presented GO bytes → GO digest + exact 26-key shape → class/purpose admission
against the plan (T0_REHEARSAL purpose or rehearsal-prefixed id on an unprefixed production plan → launch_go_receipt_invalid
detail rehearsal_purpose_on_production_id; a six-key rehearsal receipt presented as a GO → launch_go_receipt_invalid
detail receipt_class) → THEN ARM verify → remaining ordered checks; scripts/launch_window.py parses all eight flags but
the consumer performs admission before touching the ARM path; regression: absent ARM + rehearsal GO on a production plan
→ the class refusal, not launch_consumption_missing. (7) the G7 artifact schema joulewise.pack_night_g7_control.v1 with
the exact keys listed there; (8) the bundle record-name set gains g7_control {path, sha256}; the loader authenticates the
bytes; G7 acceptance re-validates schema + PASS conditions from those bytes. Then finish the rest of the seat-4 brief
(/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ff-brief-d176-seat4-relaunch-astra.md): the T0_REHEARSAL GO production path with the 2×2 table; G5 evaluating
joulewise.pack_night_go_receipt.v1 recomputing C1–C5 (D-149 refused); the four-case purpose/root regressions through the
consumer; §9 rows B4/S1/S4/N1 pinned; §7.1 row; §10.5 amended with items 6–8. NEEDS_RULING only for a genuine gap.
Acceptance (rc-gated to a log; named modules ONLY, NEVER discover/shard; end your turn after the named acceptance):
tests.test_run_night tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_arm_readiness
tests.test_rehearse_t0_unattended tests.test_docs_freshness; git diff --check; no commit; header < 8192 bytes; report
= per-clause map + the G7 artifact's exact JSON produced by the regression.
