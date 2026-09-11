# D-078 Reason Registry Amendment

This additive amendment extends the closed D-078 claim-refusal vocabulary.
Consumers preserve each spelling verbatim; none of these conditions may license
a claim.

| Reason code | Semantics |
| --- | --- |
| `capture_pipeline_superseded` | Capture-pipeline evidence is authentically stored and names a retired, non-claim-bearing capture method. |
| `capture_pipeline_absent` | No capture-pipeline evidence presentation is available for claim admission. |
| `instrument_calibration_capture_time_mismatch` | The declared calibration capture time disagrees with the immutable, hashed calibration-event chronology. |

## D-176 launch-family registration — 2026-09-08 (stage-1 R-8)

These codes belong to `LAUNCH_LINEAGE_REASON_CODES`, not the frozen readiness
row registry or `REASON_CODE_COVERAGE`. They are raised as `LaunchLineageError`
and rendered by the launcher's shared JSON refusal handler.

| Reason code | Semantics |
| --- | --- |
| `launch_go_receipt_missing` | The GO file is missing, or live replay presents a v2 or GO-less consumption record. |
| `launch_go_receipt_invalid` | Any other GO authentication, binding, class, purpose, condition or validity failure; detail identifies the field, or `class=<receipt_class>` for a rehearsal receipt. |

## D-102 epoch-continuation diagnostic — 2026-09-10

This diagnostic records a rejected continuation in
`acceptance.continuation_refusals` and the writer's preflight record. The
invalid entry grants no judged epoch. When no judged epoch matches the
machine, the outer bracket refusal remains
`calibration_acceptance_bound_stale`; the diagnostic does not replace it.

| Reason code | Semantics |
| --- | --- |
| `calibration_epoch_continuation_invalid` | A registered continuation failed authentication, acceptance binding, schema, verdict, arithmetic, or the available ledger-session cross-check; detail identifies the failed field. |
