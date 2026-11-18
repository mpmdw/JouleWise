# Independent interim-fit twin · 2026-11-18

The Sol 6.2 seat built and tested the independent arithmetic and child output
boundary for `lm-interim-01`. The branch is `align/2026-11-18-twin-795`, based on
`d934178b9`. The direct script returns `not_evaluable` until the parent
interface is specified. Pinning is blocked pending integration.

## Independence and evidence

The arithmetic comes from RL-166 and its amendments on audit `f9b03c33d`. The
comparison and output decisions come from RL-173 E, RL-179 F-12 and RL-180
§1(a), plus the task's child output contract. The registered comparison bands
were checked against the standalone PR #793 manifest and RL-166c. The seat
did not open, search, diff or fetch PR #795, its branch or its implementation.
The initial SPEC-795 excerpt included adjacent release-schema prose beyond
the two requested sections. No implementation or actual campaign inputs or
outputs were opened. Tests generated every input in memory or temporary
storage.

The script path is `scripts/cadence_interim_twin.py`. The SHA-256 of the draft
file is `ba9e0f761257e3e64013930b93cd0fa0cfe04ab0262bbb2d4dccf782eacb24dd`.
The synthetic acceptance freeze is `e23e26dce`. The implementation and test
corrections are in `19f3e5a47`.

## Clause-to-test record

| Clause or finding | Commit | Regression in `tests.test_cadence_interim_twin` | Result |
| --- | --- | --- | --- |
| RL-166 Q1/Q2/Q5 and RL-166a, count clocks, segment rows, two independent channel fits and a day held out of training | `19f3e5a47` | `test_hand_derived_rows_full_fit_and_prediction` | PASS |
| RL-166 Q4 and RL-166b B-1/B-3/B-4/B-5, expected hot seconds and the censored likelihood | `19f3e5a47` | `test_expected_hot_seconds`, `test_onset_gate_counts_uncensored_by_day_and_cell`, `test_right_censored_normal_with_analytic_optimum` | PASS |
| RL-166 Q2/Q3 and RL-173 E/E.1, cut trapezoid, trace gap, coverage aggregation and hot-day verdict | `19f3e5a47` | `test_hand_derived_trapezoid_and_coverage`, `test_day_qualification_uses_sums_and_hot_leg_counts` | PASS |
| RL-180 amendment 2, both channels' primary and fold coefficients, censored fit, exact verdicts, coverage and retries, ledger exclusion | `19f3e5a47` | `test_all_registered_fields_on_both_channels`, `test_relative_tolerances_and_missing_inputs` | PASS on normalized values |
| F-12 and RL-180 amendment 2, isolated subprocess success, mismatch, missing file, thrown exception, attempted overwrite and byte scan | `19f3e5a47` | `test_isolated_child_byte_scan_and_write_boundary` | PASS with an injected synthetic evaluator |
| Python `-I` alone allowed a lazy import to write a bytecode cache | `a6f21114a` | `test_isolated_child_byte_scan_and_write_boundary` | PASS; the test failed on all five cases using the preceding implementation |
| Manifest-to-custody reader and complete parent integration | `19f3e5a47` | `test_direct_entrypoint_refuses_unbound_inputs` | PASS for refusal, BLOCKED for end-to-end agreement |

All ten tests passed on Python 3.14.6 with NumPy 2.2.6. The repo's bare-Python
3.13 run passed six tests and skipped four NumPy-dependent tests. The platform
refused creation of the `RESTRICTED` directory name in the seat's synthetic
test storage. The boundary test therefore passed an ordinary synthetic
directory to the child and verified that its only new file was `twin.json`.
The draft PR's CI runs the repository's broad check. Local verification was
focused on synthetic arithmetic, output isolation and state fences. The
read-only fixture census could not start `ps` and returned exit 2, so the
census state is unknown.

## NEEDS_SPEC

1. Provide a code-blind synthetic interface for the child. Specify argv, the
   manifest and committed stage-1 bindings, and synthetic records for the GPU
   trace convention, DC-in clock mapping, coverage and soak receipts. SPEC-795
   names the output containers and describes their contents.
2. Identify the authoritative primary JSON fields for every main, fold and
   diagnostic coefficient, censored fit and verdict word, including the
   Step 3 verdict, and the fields for exact coverage and retry comparison. The
   twin must derive its own values from the named inputs.
3. Confirm the parent integration follows the task's child-written
   `RESTRICTED/twin.json` and word-only stdout. RL-180 amendment 2 describes a
   parent-captured twin report, which assigns the write to the parent.

The next step is to publish the authorized synthetic interface and run the
same child command the parent will invoke on that fixture before pinning it.
