# Independent interim-fit twin raw bundle · 2026-11-18

Draft PR #816 implements the raw readers from TWIN-INTERFACE-2, with RL-183a
on audit `286062767` governing the decoder boundary, ties and Step 3 cell
status. The script path is `scripts/cadence_interim_twin.py`. The SHA-256 of
this draft is `c37a27420a09e3fa27db2a203c4ab6edc7db113829616888da99977ebd1fc9b6`.

The real child command ran on a hand-derived raw synthetic bundle under
`python -I -B`. Both channel fits, full and held-out fits, the marked-span
fit, Step 3, the receipt summary and the parent-derived agreement were
checked without constructing the fixture's primary coefficients with the
twin. Each manifest named and committed to both dependency files. The
positive run used a test decoder with a sample already anchored at each
poll. It verified the twin's arithmetic and readers above that boundary.

The exact decoder at the registered `6b2e4f57776f03ba39ea644e395d4649d4e7a4ded27dd1e008eda77601fa6e0e`
hash imports `joulewise.aggregate.student_t_critical_95` and
`joulewise.desk_compress.read_bytes`. It loads neither under the enforced
stdlib-only boundary. Swapping the exact decoder and initializer into the
same fixture and pinning both reproduced `ImportError` before sample reads.
The child emitted the closed two-line failure and empty stdout. The draft
digest is pending the exact-decoder acceptance run before manifest pinning.

## Clause-to-test record

All names below are in `tests.test_cadence_interim_twin`. Nineteen tests
passed locally with NumPy. The focused fixtures generated all loaded input
records. No production data or primary look code was read. The seat consulted
the explicitly authorized dependency blobs and the generic runner's receipt
roster field declaration.

| Clause or finding | Commit | Regression | Result |
| --- | --- | --- | --- |
| RL-183a §1, both dependency hashes and the isolated import boundary | `834d7bbe2` | `test_meter_decoder_import_boundary`, `test_actual_child_argv_on_fully_bound_raw_bundle` | PASS. One-byte pin changes refuse. The exact registered decoder fails its permitted imports. |
| TWIN-INTERFACE-2 §2, complete operational bytes, counter and native row projections, GPU time binding | `834d7bbe2` | `test_gpu_rows_and_raw_meter_time_identities`, `test_native_digest_preserves_spelling_and_paired_prefix`, `test_actual_child_argv_on_fully_bound_raw_bundle` | PASS |
| RL-183a §2, tied samples, clipped integration, gap, and largest span-wide nominal period | `834d7bbe2` | `test_meter_ties_and_span_wide_period` | PASS against hand values |
| TWIN-INTERFACE-2 §3 and RL-183a §3, temperature, guarded cut, slope, full-cell spread, subset fits, and empty cells | `834d7bbe2` | `test_step3_temperature_at_unsnapped_cut_and_block_mean`, `test_step3_spread_rounding_sensitivity_and_empty_cells`, `test_actual_child_argv_on_fully_bound_raw_bundle` | PASS |
| RL-180 and RL-181, hand-derived fit, perturbation, missing input, private output, and outer byte scan | `834d7bbe2` | `test_actual_child_argv_on_fully_bound_raw_bundle`, `test_isolated_child_private_capture_and_closed_failure` | PASS with the fixture decoder |

## NEEDS_SPEC

RL-183a forbids the other JouleWise imports and assumes the exact decoder can
load with stdlib only. Before the next acceptance run, the lead must either
provide a standalone decoder pin or approve a narrow import shim for the
unchanged registered bytes. The requested shim would permit plain-file reads
and fail if the diagnostic-only t helper is called. Compressed input already
refuses under RL-174 A.4. Run the same bound synthetic bundle with the
authorized decoder setup after that decision.
