# S-1 candidate — lead full-read ledger (rule-1 gate, sliced)

Object: main...impl/s1-candidate @ b5f97c3 (33 files, +8527/-211).
Method: structured slices, highest-stakes first, each slice's verdict
recorded here at read time; the gate closes only when every slice is
READ. Slicing is a read-order decision, not a rigor reduction — every
changed line is covered by exactly one slice.

| # | Slice | Lines | Status |
|---|---|---|---|
| 1 | joulewise/arm_readiness.py (cond-2 channel, chain-read, library gate, family-publication) | ~2298 diff | PENDING |
| 2 | joulewise/scheduler_gates.py (G7/v2) + joulewise/arm_readiness_evidence.py | ~330 | PENDING |
| 3 | scripts/: build/verify marker, pinset builder, verify_receipt_histsem, author CLI | ~large | PENDING |
| 4 | configs/arm_readiness/d117_row_registry_v2.json (112 literal, horizons, vocabulary) | full file | PENDING |
| 5 | docs/contracts/: d117_step6_confirmation_table.md + receipt_histsem_verifier.md delta | full | PENDING |
| 6 | tests/: family_marker + receipt_histsem + scheduler_gates + schemas deltas | ~2040 | PENDING |
| 7 | tests/: lifecycle + evidence_author + evidence_t0 + others + enumeration | ~rest | PENDING |
| 8 | MANIFEST.md final + cross-slice coherence pass | full | PENDING |
