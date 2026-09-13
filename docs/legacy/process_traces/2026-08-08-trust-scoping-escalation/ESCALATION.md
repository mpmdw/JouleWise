# ESCALATION — trust-branch delta classes at count 2 (2026-08-08)

**Ruling: the standing trigger fires on `impl/d117-postcollection-trust`.
No fix round 4. Consult on the terminating shape of two classes.**

## The count

- **Regression-fidelity class:** round 3 — decisive regression
  pre-authenticated inputs in memory (count 1). Round 4 (`ad16fb2`) —
  the file-backed rework still substitutes the production
  authentication chain via `_fresh_original_core` (strict validator,
  whole-window consumer, allowance derivation, custody checks all
  replaced) AND the on-disk attack dropped required mutation legs
  (no inserted `floor_mint_postcollection`, no drift/allowance
  mutations), so first-independent-mismatch ordering is unestablished
  (count 2).
- **Strict-parse-scoping class:** round 3 — blanket rglob over-scan
  (count 1). Round 4 — the scoped traversal UNDER-scans
  (authentication-reached ledger custody artifacts under
  instrument_validation and attempt-ledger bundle metadata are read by
  authentication but absent from the strict map — probe-verified) while
  STILL over-scanning (`execution == "existing"` members that
  authentication never consumes falsely refuse) (count 2).

## Why structural

Both classes are the same disease: the strict-parse SET and the
regression's EXERCISED PATH are being approximated by parallel
enumeration that drifts from the real consumption code. Every round
moves the approximation; none derives it.

## Consult charge

Design the shapes that make both classes unconstructible:
1. **Registration-at-read:** the strict parser becomes the single
   byte-read used by the v2 authentication path itself (every document
   authentication reads is strict-parsed AT THE READ SITE and thereby
   registered), abolishing the parallel traversal — the set is then
   definitionally the authentication-reached set. Rule on feasibility
   against the actual read sites, TOCTOU re-read requirements, and the
   v1 byte-parity constraint.
2. **The decisive regression's contract:** what may be substituted
   (nothing? only the v1 core artifact loader for fixture minting?) for
   the regression to count as exercising the production path; and the
   EXACT mutation-leg inventory the coordinated attack must include
   (from the memo §8 list, verbatim).

The custody-authority class remains DEAD (unchallenged since the
round-3 tripwire). The mint bar stays up until this branch completes
its gate; the merge does not happen tonight.
