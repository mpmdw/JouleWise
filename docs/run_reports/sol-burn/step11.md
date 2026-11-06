# Block 5 speed analysis — STEP 11 sensitivity

Date: 2026-11-06 UTC. Scope: synthetic fixtures only; no experiment, custody, archive, or restricted path was read.

## Decision

Keep the two **bound passes** ordered, and run the two **pack kernels** (`alpha`, `beta`) concurrently inside each pass.

The two driver calls are not independent in the required observable semantics. The first call is the primary-bound equality gate and the second is the wider result that may be published: `dry_run._sensitivity` invokes `BMax(0.0, ...)` first, discards that record, and only then invokes `s.b_max`; the write follows the second return (`joulewise/b5_analysis/dry_run.py:1725-1727`). Moving the wider call ahead of successful completion of the equality gate would perform work after the serial implementation's first refusal. In addition, each pass uses the same authenticated archive handles supplied as `gamma_archive` (`dry_run.py:1715-1726`), and successful pack work merges replay census rows into the caller's archive (`joulewise/b5_analysis/sensitivity.py:357-364`). Those are shared observable authentication/accounting objects, not independent pass-local state. Consequently this change does **not** speculate the wider pass across the equality gate.

The pack derivations within one pass are independent before ordered consumption. Each call receives one pack's window, kept units, fresh sensitivity context, deep-copied spec/projection/report, and returns rows/report plus a detached census (`joulewise/b5_analysis/sensitivity.py:240-275,347-356`). The parent consumes results in fixed `alpha`, `beta` order and only then merges each census (`joulewise/b5_analysis/sensitivity.py:357-364`). Contrast composition starts after both pack reports have been consumed (`joulewise/b5_analysis/sensitivity.py:365-382`). Thus neither pack consumes the other pack's result, census, floor, or contrast while computing.

## Implementation and equality proof

Production already schedules `derive_pack` through the bounded ordered `pack_map` path for default authenticated consumers, while caller-owned seams remain serial (`joulewise/b5_analysis/sensitivity.py:347-356`). This task adds direct synthetic evidence for both properties that STEP 11 requires:

1. `test_parallel_pack_results_are_byte_equal_at_both_step_11_bounds` runs the isolated pack derivations at representative equality (`0.03 s`) and wider (`0.05 s`) bounds with one worker and three workers. It serializes the complete ordered `(rows, report, census)` values using the issuer-compatible sorted compact JSON form and asserts exact byte equality (`tests/b5_analysis/test_sensitivity_parallel.py:94-114`). Both comparisons passed.
2. `test_alpha_and_beta_pack_kernels_really_overlap` installs a two-party filesystem barrier in the synthetic projection consumer. Neither worker can return until it observes the other worker's marker. Both worker outcomes completed successfully, proving actual overlap rather than merely proving that the process-pool branch was selected; ordered consumption still returned `alpha`, then `beta` (`tests/b5_analysis/test_sensitivity_parallel.py:116-130`).
3. The pre-existing refusal matrix compares one-worker and three-worker outcomes for successful work, project refusal, extract refusal, and a primary-bound equality failure, and asserts the same first refusal and consumed prefix (`tests/b5_analysis/test_sensitivity_parallel.py:69-92`).

Measured focused result: `python3 -m unittest tests.b5_analysis.test_sensitivity_parallel` ran **3 tests in 5.529 s**, all passing. No real-data timing claim is made.

## Outcome

STEP 11 preserves the primary-bound equality gate, exact output bytes, alpha-first refusal behavior, and bound-pass order. It overlaps only the proven-independent alpha/beta derivations within each bound pass. Disclosure and fill remain downstream of the completed wider sensitivity record (`joulewise/b5_analysis/dry_run.py:1732-1740`).
