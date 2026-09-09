WRITE_SCOPE: ["docs/contracts/pack_night_go_receipt.md","joulewise/arm_readiness.py","joulewise/night_gate.py","tests/test_arm_readiness.py","tests/test_night_gate.py","tests/test_launch_window.py"]

# D-176 integrated head — contract-map and pin fixes (gpt-6-astra, medium, genre implementation)
Branch int/2026-09-08-d176-seats-2-3 at 4d72e524. The Opus review at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ew-ref-d176-integrated-opus-contract-review.md ruled LAND-WITH-FIXES; finding 1 (census makes T0_REHEARSAL
unreachable) goes to a cold gate — DO NOT touch the predicate. Cure findings 2–6 only:
2. §9 rows for landed seats still carrying NOT PINNED (:769, :770, §8.1 receipt_id, §8.3 encodings, §10.1 F1/F2/F7,
   §7 opening): replace each with the biting test that exists (read the assertion) or, where none exists, add the
   smallest defect-shaped assertion and pin it.
3. Stale pins: launch_window.py:129 (§9.1 "pack-only entry boundary" and the four transport flags), run_night.py:1236
   and :1369 (§9), tests/test_arm_readiness.py:2112 — re-read each symbol and rewrite; then sweep every §9/§9.1 pin
   into the touched files and verify each lands on its symbol.
4. §7.1's integration record: it must state that 4d72e524 IS the integration commit editing this contract.
5. One home for the rehearsal prefix: arm_readiness.py ~:9849 imports t0_rehearsal.REHEARSAL_WINDOW_PREFIX (or the
   constant moves to a shared module both import); regression that the two sites cannot diverge.
6. Gate/consumer symmetry: a MISSING pack_root refuses launch_go_receipt_missing in BOTH night_gate (_pack_digest ~:681)
   and the consumer (~:9919); gate refusal `detail` values match §6's bare form (no appended field) OR §6's table is
   amended to the field-suffixed form consistently — pick one, apply to both, regression asserting equality of the
   detail strings across gate and consumer.
Acceptance (rc-gated; named modules ONLY, never discover/shard): tests.test_night_gate tests.test_arm_readiness
tests.test_launch_window tests.test_arm_readiness_schemas tests.test_docs_freshness; git diff --check; no commit;
header < 8192 bytes; report per finding.
