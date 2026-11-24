# lm-ctl-01 pre-reservation specification, revision 12

This revision freezes the lead's replacement of the blind scientific
projection and the admission predicate for draft PR #957.
[Revision 11](lm-ctl-01.print-spec.v11.md)

## Blind object

Construct the object explicitly from the following closed fields.

| Field group | Admitted types and purpose |
| --- | --- |
| Kit | Registered digest and issued roster order bind the projection to the chosen kit. |
| Leg | Integer roster index, closed script kind, and dispatch, runner admission and completion flags identify eligible work. |
| Script | Issued integer call counts and interval doses. Each completed row carries its kind, monotonic stamps, token counts and completion. These reproduce the view and its denominators. |
| Episode | Monotonic endpoints, ordered turn counts and timestamps, logged flags and tool presence. Gate and hold variants carry their enum, interval and applicable turn index. These reproduce the joined views and partition. |
| Trace support | Integer timestamps on the episode clock, window endpoints, cadence and clock half-width. The shared rail grid and optional DC grid define which quantities can be computed. |

The source binder authenticates the original bytes and verifies the producer
records. The projection contains no source locators, lengths, listings,
producer-defined keys, diagnostic text, or observation values. Binding and
reservation artifacts retain their registered formats and digests. Rebinding
or renaming auxiliary content leaves the blind object unchanged when its
allowed fields and kit digest agree. Wire-level refusals remain in force.

## Admission

Run the real per-leg calculation on fixed positive synthetic samples on the
same support as the bound traces. This computation reads only the blind
object and invokes the same per-channel estimates and phase table as release.
Commit the resulting dispositions and channel availability to the private
certificates before the marker. Missing required per-token estimates caused
by a phase denominator make the leg `not_evaluable` with reason
`phase_denominator`. Keep ruled per-leg reasons, channel gaps and quorum
refusals. Use the committed plan during release. The two closed
value-dependent reasons from revision 11 remain in force.

## Acceptance

Replay the two narrow-check findings and the audit 7 and audit 8 cases.
Compare admission on synthetic and real-value fixture runs across the
issued script kinds and the A3 mutation matrix. Verify fresh refusals and
the previously ruled post-marker integrity failure. Compare serialized
projections from stage 1 and standalone preflight after varying source
names, paths, sizes and undeclared content. Verify frozen byte identity
and the exact cumulative result, including v3.1 at 846/846.
