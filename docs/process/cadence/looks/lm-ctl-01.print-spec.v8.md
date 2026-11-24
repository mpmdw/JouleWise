# lm-ctl-01 pre-reservation specification, revision 8

The lead's 23:45 engineering ruling follows the executing report on
`62d0a3c8d`. It verified three HIGHs and one LOW. The previous review
cycle remains closed under PIPELINE §3. This revision freezes the
compatible remediation and records the unresolved contract choices.
PR #957 remains draft. [Revision 7](lm-ctl-01.print-spec.v7.md)

## Compatible acceptance

1. Apply the native episode wire schema at the common blind gate.
   Every field emitted by the closed `Episode`, `Turn`, `ToolCall`,
   `MonitorVerdict`, and `RouterLog` serializers is present and has
   its declared JSON type. Reject unknown fields in those records.
   Before converting measurements, check whether numeric tokens can
   round to finite binary64. Opaque score, suspicion, and router
   observations have typed placeholders in the blind projection.
   Cover each field with missing, wrong-type, nonfinite, and
   oversized mutations in the shared preflight validator.
2. Decode a thermal `turn` as an index for H only. On G0 and G1
   the native integer, absent value, and opaque free text do not
   participate in tiling. Bind the original bytes. Check the exact
   synthetic G0 sentinel under the conversion guard at both blind
   gates, then exercise publication.
3. Both result records must agree with native work completion. A
   dispatched incomplete script cannot have complete terminal status
   or be admitted. A completed native script requires every reached
   step complete. The pinned writer can emit an interrupted trailing
   step for a non-admitted incomplete leg. Rebind the admitted 30 s
   CPU reproduction and independently mismatch each completion copy.
4. The worker reports a typed read, calculation, or publication
   failure in confined diagnostics and preserves the frozen observer
   notice `stage2_error` followed by the exception type. Its established
   marker determines spend. Inject a failure separately in each phase
   and verify the typed result and spent status.

Structural refusals use exit 2 and `REFUSE PREFLIGHT INPUT_CHANNELS`
at stage 1, preflight, and direct stage 2. Assert absent reservation,
marker, public output, and claim/read events. Keep the frozen and
governed per-leg outcomes. The LOW orphan-marker race is a follow-up.

## NEEDS_SPEC

- The pinned frozen bundle stores `0.0001` as a JSON clock bound.
  Binary64 rounds it to a finite value. The decimal is mathematically
  inexact in binary64. Exact representation for every number and
  retaining this accepted fixture require a ruling on the numeric
  policy. Native nanosecond integers also carry exact integer
  precision independent of floating-point conversion.
- The pinned writer omits fields on valid interrupted steps and emits
  task-defined diagnostic objects. The frozen G0 row omits `turn`.
  Define which fields are conditionally required and where a declared
  opaque object can carry producer-defined keys. This determines how
  far the complete closed-schema and per-field removal matrix can
  extend beyond the settled native records in this revision.

Independent Tier 2 executing review, the installed byte pass, and
bound-host blind preflight remain lead gates before reservation.
