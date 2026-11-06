# Triage of sol/burn-r0rev (lead-side verification, 2026-11-06)

Verified on the Air (synthetic tests only).

- Finding (sum overflow -> Infinity -> report_serialization_error): REAL on the merged
  kit (84848dc68 has the same tree as c712318e5). Reproduced: with the fix reverted, the
  new runner regression gets a load row without nll_verdict, and the adversarial probe
  gets mean inf.
- Severity: LOW, not URGENT. It cannot produce a false pass (the run still fails), and the
  real MLX path cannot reach it: losses come from float32 logits, so each finite loss is
  below about 6.8e38 and 2048 of them sum to about 1.4e42, far under the float64 maximum.
  The R0 re-run does not need this fix.
- Fix: correct, and the happy path stays byte-identical (test added). It can ride with the
  next R0 kit PR (for example after #687). It need not block anything.
- Tests: tests.align.test_r0_load_reference + _adversarial: 50 OK with the fix; the 2 new
  tests fail/error without it.
