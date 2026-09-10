# Lead note — execution refuter 18 triage, fix round 1, bench delta re-audit (2026-09-10 ~05:10 PDT)

Refuter 18 (Astra xhigh, read-only, worktree at 8da99190): one **should_fix** (R1): widening ONLY the two capture-endpoint
comparisons in `environment_admission.py` from 1e-6 s to 1e-3 s left all 12 new tests green, so the endpoint allowance was
not bound from above. Mutation table otherwise clean: reverting R1/R3/R4 each failed its ADMIT tests; widening the shared R1
allowance, both R3 allowances, or R4's identity tolerance ×1000 each failed a REFUSE test. Same-signature sweep: no remaining
sub-ULP epoch comparison in the three modules; `reduce.py` byte-identical to main; D-138 pin test passes. Contract sentences
reconstructible; no document-byte pin. idle 75: all 24 producer configs valid at 75 s / 10 Hz; the "no committed 30 s pins"
sentence in the brief is false for 24 HISTORICAL fixture configs under `tests/fixtures/g2a/pin/config-root/` (frozen
pin-consumer fixtures, not producer outputs — no change). Blocking flag F1 is a sandbox limitation (no writable temp dir in
the read-only runner), not a finding; the lead-side full replay covers it.

Fix round 1 (`558f9368`, test file only): `test_r1_refuses_capture_outside_attempt_by_ten_microseconds` (±1e-5 s at either
capture edge must refuse `environment_admission_missing`); removed the orphan `AnchorCoverageRoundingTests` helper class and
the `reduce`/`bundle_read` imports left behind when R2 was staged (record 15).

Bench delta re-audit (lead, pasted verbatim from the run):

```text
--- DELTA RE-AUDIT (bench): widen ONLY the two endpoint comparisons 1e-6 -> 1e-3
mutant applied
FAIL: test_r1_refuses_capture_outside_attempt_by_ten_microseconds (...) (shift_s=-1e-05)
FAIL: test_r1_refuses_capture_outside_attempt_by_ten_microseconds (...) (shift_s=1e-05)
Ran 13 tests in 0.008s
FAILED (failures=2)
mutant reverted
OK
 tests/test_gate_sensibility_rounding.py | 27 +++++++++------------------
```

Production bytes at 558f9368 equal those at 8da99190 (`git diff 8da99190..558f9368 --stat` = the test file only). Pending:
Opus contract/physics refuter; full replay at the final head (row 9).
