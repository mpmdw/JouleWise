# lm-ctl-01 pre-reservation specification, revision 6

PR #957 returns to spec under PIPELINE §3. The third executing round
audited `c660b7541` and verified four HIGHs, one MED and one LOW. The
presence of a HIGH closes the review cycle. The PR remains draft.
The commit introducing this revision and its synthetic regressions is
the new spec freeze.

[PIPELINE §3](../../PIPELINE.md#3-tier-2-only-spec-freeze-and-convergence)
· [Revision 5](lm-ctl-01.print-spec.v5.md)

## Blind input invariants

1. The native script's visible prompt and delivered decode totals must
   fit the same finite floating-point range as its individual token
   counts. Sum the counts exactly before the range check. The phase
   calculation uses these totals as divisors, and the private report
   carries them as integers. Missing first-token timing does not waive
   the bound. Apply it to both kinds of total.
2. Config labels and descriptions used only for type, presence or
   nonblank checks remain opaque. Validate the original string token
   for the predicate the typed constructor uses, including escaped
   Unicode whitespace where nonblank text is required. Preserve the
   string-only rule for tags. Decode only fields needed for a literal,
   enum, identity, fingerprint or numerical prerequisite. The original
   bytes remain bound by their digest.
3. The common rail support grid must have disjoint adjacent windows
   after applying the frozen powermetrics edge-snapping tolerance in
   the native trace clock. A gap is permitted. The blind check uses
   only support edges and never reads sample values.
4. Distinct dispatched positions must bind distinct episode IDs across
   the look. Every reached step's requested token count or duration
   must match its pinned issued script, including a reached interrupted
   trailing step. The issued kit's one-per-dose CPU roster then binds
   the recorded requests. Delivered tokens, measured durations, dose
   ordering by work and scientific closure retain their existing rules.
5. A confirmed entry at the reservation pathname, including a regular
   file that races with mkdir, is `HALF_MADE` at claim and freshness
   inspection. A failed mkdir with the path absent is `CLAIM_SETUP`.
   Unconfirmed cleanup and spend precedence retain revision 5's rules.

## Synthetic acceptance

Rebind each malformed input in the fixture. Stage 1, standalone
preflight and direct stage 2 must each exit 2 with exactly `REFUSE
PREFLIGHT INPUT_CHANNELS`, empty stdout and fresh status. Assert no
reservation directory, marker, public artifact or claim/read event.

| Invariant | Acceptance cases |
| --- | --- |
| Representable token totals | L001's two visible contexts are each `10**308`, with the envelope reconciled to `2*10**308`. Repeat with the second first-token stamp null, and separately with equivalent delivered decode counts. |
| Opaque nonblank text | A valid L002 project label containing `synthetic ambient_temp_c=19.8375` and a separate fixture with other free-text fields must pass both blind gates under the conversion and projection guard. Include the project label in the hosted publication test. Refuse a single ASCII space in typed notes, then repeat with escaped and Unicode whitespace. |
| Adjacent rail support | Move the middle L002 start half a second earlier on all three components. A unit test also accepts shared edges, one-nanosecond conversion overlap and a gap, and refuses overlap outside that tolerance. |
| Episode identity and issued requests | Give L002 L001's episode ID and matching clock domain. Separately replace L003's recorded 30-second CPU request with 10 seconds while leaving the issued script at 30. Alter recovery and visible-call requests in separate fixtures. Keep the valid interrupted trailing-step control from revision 5. |
| Reservation state | Confirm a regular-file collision gives `HALF_MADE` at claim and at status. Retain the existing missing path, failed inspection, rollback and historic spend cases. |

Retain revision 5's ruled per-leg dispositions and post-start digest
refusal. Confirm frozen suite v1/v2/v3 and v3.1 byte identity against
PR #951, the exact `75 raw + 4 superseded (RL-202a §2.4; lead record audit branch 1850d6930 SUPERSESSION-v2.md)`
receipt, and v3.1 at `846/846`. Record failed-first and final-head
evidence in PR #957 and the dated run report. Route the revision 6
freeze to the lead for independent Tier 2 executing review. The
installed byte pass and bound-host blind preflight remain lead gates
before reservation.
