# Lead note — R2 (reduce.py coverage endpoint ULP) staged for the D-138 re-freeze, not landed (2026-09-10 ~05:05 PDT)

Seat 08 implemented R1–R4 as specified. Its blocking flag F1: R2 edits `joulewise/reduce.py`, one of the four
D-079-pinned estimator inputs (D-138: `powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`,
`reduce.py`); `tests/test_reduce.py::test_d138_reduce_source_bytes_remain_at_issued_pin` pins its bytes to the issued
acceptance `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`. D-138 lands such changes only inside the
one atomic successor-family re-freeze with the D-079 acceptance reissue.

Ruling (magistrate, within D-138, no rule amended): R2 is REMOVED from the GATE-SENSIBILITY-SWEEP-01 PR and STAGED.
`15-r2-coverage-ulp-staged-for-d138.patch` is the exact diff (reduce.py `_anchor_coverage_ok` + the run_bundle_layout.md
sentence) and `15-r2-tests-staged-for-d138.py.txt` holds its four regressions verbatim, both extracted from the seat's
worktree before reverting. R2 needs a tail within one ULP of the required endpoint, so its omission is a rare false
refusal, not a G2-a blocker; it rides the transaction branch per D-138's inheritance corollary. R1, R3, R4 land now
(`environment_admission.py`, `controller.py`, `load_transition_alignment.py` are not governed inputs).

Seat flag F2 (a controller test failing at baseline) is triaged separately in this directory.
