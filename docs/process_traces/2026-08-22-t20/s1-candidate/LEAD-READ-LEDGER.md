# S-1 candidate — lead full-read ledger (rule-1 gate, sliced)

Object: main...impl/s1-candidate @ b5f97c3 (33 files, +8527/-211).
Method: structured slices, highest-stakes first, each slice's verdict
recorded here at read time; the gate closes only when every slice is
READ. Slicing is a read-order decision, not a rigor reduction — every
changed line is covered by exactly one slice.

| # | Slice | Lines | Status |
|---|---|---|---|
| 1 | joulewise/arm_readiness.py (cond-2 channel, chain-read, library gate, family-publication) | ~2298 diff | READ ✓ SOUND (2026-08-23: cond-2 subtraction order correct; chain closed-enumeration + duplicate refusal; digest-first table auth, no pre-match parsing; strict 4-way + head_unpublished rollback split; registry-roster engagement; candidate lane non-tautological via reviewed manifest; laundering defense present; executed-checks-only receipts; all four G2 cures and all six delta conditions verified in place) |
| 2 | joulewise/scheduler_gates.py (G7/v2) + joulewise/arm_readiness_evidence.py | ~574 diff | READ ✓ SOUND (2026-08-23: B-2 tokens ruled-exact; role-resolved census w/ authority comment; fence assertion as adjudicated; v2 seven-gate G5-first; G7 disjoint scheduler vocabulary typed CUSTODY + single mirrored R1 refusal shape; PASS/REFUSE binding discipline incl. nulls-on-refusal; GO requires family PASS; laundering defense pre-recording) |
| 3 | scripts/ (5 tools + sidecars + CLI threading) | 729 diff | READ ✓ SOUND + 1 nit (2026-08-23: K5/K12/K7 replay exact per rh-8; create-only O_EXCL/NOFOLLOW/fsync; phase-explicit thin CLIs, governed refusal envelopes w/ lane fields; digest threading complete incl. launch_window; NIT: pinset builder merge-base is-None wrapper is dead code — enforcement real via _git nonzero-raise, fix one line at merge tidy) |
| 4 | configs/arm_readiness/d117_row_registry_v2.json | full file | READ ✓ SOUND (2026-08-23: 112 = 3x37+pinset sorted-unique, zero authenticator paths; threshold 4; ruled roster; horizons exact per D-150/tiers 10x168h + 4x24h + 2x6h EB + T-0 tiers + 2 RE_DERIVABLE; 8-role vocabulary with r4-5 POLICY/LIFECYCLE/CUSTODY/GIT typing, FAMILY_PUBLICATION=CUSTODY, SUCCESSOR_CHAIN=GIT) |
| 5 | docs/contracts/: step6 table + histsem delta | 278 diff | READ ✓ SOUND (2026-08-23: acyclic C->M/C->S graph normative; sidecar = transport-only made contract text; 8-condition C->S enforcement w/ worked consequence; fixed-point embedded; chain semantics exact to code, zero drift; ONE-home discipline held) |
| 6 | tests/: family_marker + receipt_histsem + scheduler_gates + schemas deltas | ~2040 | PENDING |
| 7 | tests/: lifecycle + evidence_author + evidence_t0 + others + enumeration | ~rest | PENDING |
| 8 | MANIFEST.md final + cross-slice coherence pass | full | PENDING |
