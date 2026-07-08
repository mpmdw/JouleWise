# Stream ledger — suite-substrate (P2-010a, 2026-07-08)

Branch: `suite-substrate`. Scope: P2-010a substrate per report A as amended
by D-044..D-046. Unit 1 = foundation (suite.py, schemas, interfaces,
bundle, mock adapter); unit 2 = read/controller/reduce wiring; unit 3 =
MLX adapter + contracts docs.

### SUB-1 [lead+codex-lens] [contract] Sentinel-gated item_id duplicates

Decision: duplicate `item_id` manifest entries are a validation error
unless every duplicate carries the `sentinel` tag.
Alternatives: blanket uniqueness (rejected — breaks D-040 sentinel
repeats, which are repeated manifest entries); no check (rejected —
ambiguous pairing/prev_item).
Why: D-040 reserves within-bundle repeats for sentinels; FIFO pairing +
`item_index` disambiguation stays sound only when duplication is
intentional and tagged.
Evidence: bug-lens finding 2 (`a1-lens-bugs.md`), lead triage amendment;
`joulewise/suite.py` duplicate check + tests.
Confidence: high. Binds: manifest authors, generators (P2-012/P2-020
sentinels must tag).

### SUB-2 [codex-lens] [contract] Level contiguity is per-block

Decision: a level run closes at its block boundary in BOTH validation and
runtime marker emission; level marker indexing keys on
`(block_id, level_id)`.
Alternatives: global level contiguity (rejected — validation would pass
manifests the runtime splits into duplicate level windows).
Why: validation-accepted manifests must produce well-nested markers.
Evidence: bug-lens finding 3; FIX-3 diff.
Confidence: high. Binds: unit-2 `level_windows()` semantics (a level_id
recurring across blocks yields multiple windows — reader API is
`dict[str, list[Window]]`, already shaped for this).

### SUB-3 [codex-lens] [contract] Pinned manifest vocabularies

Decision: `schema_version` pinned exactly to `suite_manifest.v1`;
`output_policy` ∈ {fixed_budget_exact, natural_eos}; `status_policy` ∈
{none} (grows only by decision).
Alternatives: free strings (rejected — typo'd policies silently change
status semantics).
Evidence: bug-lens findings 4-5; FIX-4/FIX-5 diff + tests.
Confidence: high. Binds: P2-010b/P2-012 manifests.

### SUB-4 [codex-test-audit] [process] Omission whitelist is exact

Decision: the emitted-keys round-trip test whitelists exactly
{suite_manifest_ref, suite_manifest_sha256} as omission-serialized; any
other omitted optional fails the test.
Why: a section-wide whitelist would let future fields silently go
omission-serialized, eroding D-029.
Evidence: test-audit finding 4; `test_workload_to_dict_omits_suite_fields_only_when_none`.
Confidence: high. Binds: schema changes (a third omission field triggers
D-044's revisit clause).
