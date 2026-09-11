# COLD-GATE PACKET — D-100 repair residual: b-ii cross-capture binding (2026-08-02)

The repairs disposition note's binding commitment fired: the decisive
re-audit of head 05d99b6 (impl/met-dangler-disposition) left ONE
blocker. Everything else on the branch is CLOSED and verified: B1, B4,
B5, S1 (delta re-audit), b-i content-general sweep + all five
red-on-base regressions (decisive re-audit). Lead gates green at every
head (suite 2396 OK unmasked; mapping pins hash-identical).

## The residual (decisive-reaudit.md, this dir)
The b-ii inspector validates allowlisted files' rows for
admission-phase schema and bounds timestamps by failure+0.250 s — but
does not bind telemetry/nested content to THIS capture: a schema-valid
rich_telemetry.jsonl from an EARLIER measured run (older timestamps,
no phase/occurrence identity in rows) planted under the allowlisted
name licenses. The attack requires write access to custody quarantine
contents (rider-(ii)-class actor) or an operator error of a very
specific shape.

## Material context for the ruling
1. Window B's two r08 bundles — the ONLY b-ii subjects the license
   currently needs — were verified by the LEAD directly on 2026-08-01
   (recorded: event sequences, admitted flags, zero measurand fields,
   teardown flush 136-171 ms) and re-verified by the cold instance and
   the round-4 audit chain. The automated inspector is belt for an
   already-recorded manual verification FOR THIS WINDOW.
2. The inspector's residual hole requires foreign-capture telemetry
   inside custody — the same coordinated-custody-write class D-097
   rider (ii) ratified as out of this layer's threat model.
3. A consistency-binding fix is specifiable (bind telemetry rows to
   the capture: timestamps within [bundle start, failure+0.250];
   row-cadence consistency with the admission duration; cross-check
   against events.jsonl's phase timeline) but would be the THIRD
   formulation of b-ii — the commitment forbids another round without
   this gate.

## Options
A — REGISTER the residual as a fenced blocker (C3 F1/F2 precedent
    shape, itself a new-ruling precedent): merge; closure through a
    named follow-up row (D100-BII-BINDING-01) with the
    consistency-binding fix + its own audit; fences: the b-ii AUTOMATED
    license is valid ONLY for bundles ALSO carrying a recorded lead
    manual verification until the row closes (for window B: already on
    record); accepted set may only shrink.
B — one more surgical round under gate license (the gate may license
    what the magistrate's commitment cannot): the consistency-binding
    fix, ~30-60 lines + regressions, then a final focused re-audit.
C — hold the branch to next session (boundary in ~3 h; the merge and
    the window-B re-evaluation move post-pause).

## Required ruling
1. A, B, or C (or variant), with fences verbatim if A, and the exact
   binding specification if B.
2. Whether window B's re-evaluation may proceed under A given the
   recorded manual verification (the license conditions' own text
   required the recorded verification anyway).
3. Anything the packet lacks.
Magistrate lean (recorded, non-binding, and per the S3 process finding
this packet contains NO runway/cost framing): A.
