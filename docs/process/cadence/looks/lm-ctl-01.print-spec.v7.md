# lm-ctl-01 pre-reservation specification, revision 7

The lead's follow-up report on `1a9e96922` verified three HIGHs and
one LOW after revision 6. The prior review cycle remains closed under
PIPELINE §3. The commit introducing this revision and its synthetic
acceptance cases is the freeze for the requested remediation. PR #957
remains draft.

[Revision 6](lm-ctl-01.print-spec.v6.md) · [PIPELINE §3](../../PIPELINE.md#3-tier-2-only-spec-freeze-and-convergence)

## Blind input and reservation invariants

1. A native work record declared complete has every reached step
   flagged complete. Incomplete native work can retain a valid
   interrupted trailing step. The shared calculation still applies
   the ruled short-delivery and incomplete-recovery dispositions.
2. Clock resolution and effective uncertainty bounds are nonnegative.
   Bounded anchor limits must be finite and ordered. Derive the rail
   map using the frozen mapper, and refuse an invalid mapped uncertainty
   before any sample values are used.
3. Project only the fields that apply to a script row's kind. Token
   counts and first-token timing apply to calls. Requested duration
   applies to intervals. Skip irrelevant values while validating the
   enclosing JSON, independently of key order. Config observations used
   solely for a numeric shape or range check remain opaque. Check the
   native finiteness and sign predicates on the token and pass a
   placeholder to the typed constructor.
4. If claim setup raises after a valid read-start marker is bound to
   the reservation entry and verified stage-1 record, claim reports
   `SPENT` immediately. Every later invocation reports the same state.
   An unbound partial reservation retains the existing `HALF_MADE` rule.

## Synthetic acceptance

| Invariant | Acceptance |
| --- | --- |
| Contradictory completion | Leave the synthetic L003 script complete and flip the 30-second CPU row to incomplete. Repeat with a call and recovery row. Retain the native interrupted-tail positive. |
| Invalid clock bounds | Independently set L002's effective anchor bound to −0.25 s and paired wall resolutions to −250000000 ns. Also check a negative monotonic resolution that can be hidden by conversion padding and an inverted anchor bracket. |
| Opacity | On otherwise valid inputs, guard an L002 recovery `first_token_ns` containing `synthetic power_w=91827.375`, an irrelevant duration on a call, and a separately valid link-rate observation. Require successful stage 1 and preflight under the conversion and projection guard. Exercise an invalid negative and overflowing link rate without converting the value. |
| Claim sync result | Let production claim write and sync a synthetic bound marker, then inject a final directory sync error return. Claim, status, and retry each return `SPENT`. The synthetic reader and publication are never reached. |

Rebind malformed structural fixtures at synthetic close. Assert exit
2 and `REFUSE PREFLIGHT INPUT_CHANNELS` at stage 1, standalone
preflight and direct stage 2. Assert fresh status and absent
reservation, read-start marker, publication, and claim and read events.
Retain the ruled G0, stamp, and post-start digest outcomes, frozen
suite byte identity, the exact cumulative receipt, and v3.1 at
`846/846`. Independent Tier 2 executing review, the installed byte
pass and bound-host blind preflight remain lead gates before reservation.
