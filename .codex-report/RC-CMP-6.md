# RC-CMP-6: producer-derived input gate for the block-5 recompute comparator

**Status: IN PROGRESS (milestone 1 of 3).** Seat RC-CMP-6, cloud, synthetic only. Brief:
`docs/process_traces/2026-10-28-recompute-meter-fit/FIX-BRIEF-3.md` (main `03ea4a6ef`). Base: lane tip `7fede8c76`.

## Milestone 1

- G1 (strict canonical load), G2 (owner-only identity), G3 (registered-id routing) and G5 (enumerated exemptions,
  named-exemption census in the restricted output) are in `scripts/compare_b5_recompute.py`.
- The base fixture (`tests/independent_recompute/test_comparator.py`) is producer-shaped (G4): 24-key fill rows from
  an adapter mirror, full fill top level, `_item` disclosure lines, the disclosure record's nine sections, registered
  ids, canonical bytes.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`:
  `Ran 235 tests ... OK (skipped=18)`.

Next: the round-3 witness and consult-probe regression tests with counterfactuals (G6), the AST guard extension,
then the full report.
