# lm-ctl-01 pre-reservation specification, revision 9

The lead resolved revision 8's numeric and schema-boundary questions.
The commit introducing this specification and the failing synthetic
cases is the revision 9 freeze. PR #957 remains draft.
[Revision 8](lm-ctl-01.print-spec.v8.md) · [PIPELINE §3](../../PIPELINE.md#3-tier-2-only-spec-freeze-and-convergence)

## Native wire schema

- Apply one role and record-variant inventory in stage 1, standalone
  preflight, and direct stage 2. Reject duplicate keys, undeclared
  fields, wrong types, and missing required fields, including required
  nullable fields. Retain the five closed episode record types.
- Binary64 fields round once, nearest with ties to even, and must
  yield a finite value within existing range checks. Keep observation
  tokens opaque during validation and bind their bytes by digest.
  Integer tokens retain exact integer precision. Reject fractional
  and exponent forms for these fields. Enforce signed 64-bit bounds
  on timestamps and offset-adjusted timestamps passed to `>q`.
- Thermal G0/G1 require kind and both bounds. An optional turn can be
  null, an integer or opaque text. H also requires a nonnegative
  integer turn. Free text is never inspected for embedded values.
- Reached steps require kind, boolean completion and an issued
  request. Returned calls require integer clock and token fields,
  including cached prompt tokens and a nullable first-token stamp.
  An interruption before a call returns has null actual tokens,
  optionally a start, and an end only with a start. Finished
  intervals require both epoch and monotonic stamp pairs. Finished
  CPU intervals also require thread CPU time. Only the final
  interrupted row in incomplete, non-admitted work can omit its
  unwritten fields. Retain cross-record completion and admission.
- The native diagnostic envelope has the pinned five keys.
  Evaluation outputs and each tool schema are opaque objects with
  task-defined keys, checked for strict syntax, unique keys,
  nesting and numeric form. The same key in an undeclared sibling
  refuses. Close hardware, thermal, config, metadata and result
  envelopes. Use each producer's defined vocabulary for keyed maps,
  including the meter's SMC sensor keys.

## Acceptance

Mutate required field presence and type, optional field absence and
invalid presence, and the applicable numeric boundaries. Include
the binary64 overflow midpoint and predecessor, subnormals and
signed zero, the accepted frozen `0.0001`, exact adjacent integer
nanoseconds above `2**53`, float-form integers and packed timestamp
overflow. Pair the approved opaque sentinel with the refused sibling.

Rebind malformed synthetic fixtures before registration. Require
exit 2, empty stdout, and `REFUSE PREFLIGHT INPUT_CHANNELS` from all
three entry points with fresh status and no reservation, marker,
publication, claim or read. Preserve the frozen per-leg and
post-start spent outcomes, frozen tree bytes, exact receipt, and
v3.1 at `846/846`. Independent Tier 2 executing review, installed
byte pass, and bound-host blind preflight remain lead gates.
