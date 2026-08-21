# Scheduler-gates ruling — addendum: FREEZE-REPLAY-EXPIRY-01 landed (2026-08-20 evening)

The B-12 defect the ruling's R-1/G1 sections treat as OPEN is CURED:
PR #162 (main `d0d5e7b`) makes `_authenticate_generic_evidence_item`
enforce `valid_until_monotonic_ns` fail-closed (live monotonic time on
omission; explicit `enforce_expiry=False` the only bypass, unused in
production and census-pinned). Consequences for the gate design:

- G1's "recompute deadlines from the authenticated frozen evidence
  bytes and never treat an arm PASS as freshness proof" REMAINS the
  ruled design — it is now belt-and-braces over an enforcing
  authenticator rather than the only live expiry check.
- The stage-3 sequencing condition ("G1 sequenced with/after
  FREEZE-REPLAY-EXPIRY-01, delta re-audit against it") has its
  precondition satisfied; stage 3 may open when its other inputs
  (registry budget value — ED_RESERVED until the `_v4` install) exist.
- The R-1 RECORDED LESSON and the rest of the adjudicated text are
  unchanged; this addendum is the FRE row's acceptance-mandated cure
  record (S-4 closure refuter finding, 2026-08-20).
