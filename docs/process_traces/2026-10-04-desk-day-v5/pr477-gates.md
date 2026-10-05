# PR #477 gates (`_v5` pin bundle + three generated packs), desk-day v5 seats 1-2

- Executing reviews (Sol 6.1, non-author): [45-sol-packs-review.md](45-sol-packs-review.md) (seat 1), delta [62-sol-packs-delta.md](62-sol-packs-delta.md) PASS at ca5f3f11; delta of the seat-2 fix [71-sol-packs-delta2.md](71-sol-packs-delta2.md) PASS at 4e51d28c (fresh regeneration byte-identical; only status tags, covering hashes and README text change; floors byte-identical; the ten allowlisted lines are exactly the registered sentence).
- Seat-2 fix [66-sol-packs-census-n1-report.md](66-sol-packs-census-n1-report.md) (brief 66): (1) whole-suite finding at ca5f3f11, `test_d165_rationale_census`: the ten hits are the REGISTERED corrected absolute rationale ("no absolute common-time replay is implemented ...") copied verbatim from `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`, which denies the retired rationale and is allowlisted at its source; disposition: exact allowlist entries, generators unchanged (changing the string would change registered text). (2) Fable N1: contrast prompt status `PROPOSED-PENDING-LEAD-RATIFICATION` -> `ISSUED-BY-G2A-PROMPT-PIN`, pack regenerated; FIXED.
- Cold Fable final pass at ca5f3f11: [61-fable-packs.md](61-fable-packs.md), PASS. The seat-2 delta (a status label and test allowlist entries) touches no number-bearing code; no delta Fable pass (doctrine: delta re-audits only for fixes to number-bearing code). N2-N5 informational.
- Whole suite at 4e51d28c (main 85d67b12 merged), CI shard method:
  - SHARD SUMMARY index=1/6 modules=1 tests=73 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=55 tests=1345 failures=0 errors=0 skipped=5 result=PASS
  - SHARD SUMMARY index=3/6 modules=56 tests=1707 failures=8 errors=0 skipped=19 result=FAIL
  - SHARD SUMMARY index=4/6 modules=56 tests=1732 failures=3 errors=0 skipped=7 result=FAIL
  - SHARD SUMMARY index=5/6 modules=57 tests=1144 failures=4 errors=0 skipped=8 result=FAIL
  - SHARD SUMMARY index=6/6 modules=56 tests=1569 failures=44 errors=0 skipped=3 result=FAIL
  - exclusive: test_calibration_exits FAILED (errors=1: `test_logical_producer_delay_preserves_exact_evidence_bytes`, passes serially = load flake); test_calibration_writer_crash_matrix OK.
  The census test passes. Remaining failures are base 8fa002f7's local-environment set plus `test_installer_refuses_outside_a_listed_install_span` (live battery probe: UpdateTime stale on this machine; not code).
