# CO-DESIGN BRIEF R2 — Mint-lane fan-out shape (pack identity)

WRITE_SCOPE: []

You are an INDEPENDENT DESIGN SEAT in the JouleWise co-design protocol
(D-144-pending): two seats design independently, then a bounded debate, then a
Fable magistrate ruling. You have explicit license — and a standing record of
peer designs out-designing the lead's — to disagree with any framing in this
brief. This is a READ-ONLY consult: read anything in the tree, run read-only
commands and tests, write NOTHING inside the repo.

## Situation

Branch `integration/phase2-transaction` @ 9f7f091. Read
docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md (sections
from "Conditions executed (afab1a2)" to end) and
docs/process_traces/2026-08-18-anchor-v3-science-review/ first. The anchor-v3
priced-validation arc changed the acceptance corpus: D-079 r3 (n=17, screens
tightened) then science-neutral r4 are issued; the old max moved from 33.559.
The atomic family re-freeze cycle is PARKED at steps 3–6: the fan-out of
mint-lane constants/goldens, _v2 pack regeneration, evidence re-author,
freeze-0002 re-mints, canonical FULL GREEN.

Canonical at bb81323: 3,726 ran, 16F/22E — 33 mint-lane reds are the known
fan-out awaiting this design; zero cured, zero unexplained.

## The design question

How should the mint-lane constants/goldens fan-out be SHAPED?

Executed evidence already on record:
- A flat migration of the 0.010818 constant was TRIED and REFUTED: it breaks
  the n=19 estimator replay (this is an executed refutation, not a
  hypothesis).
- One analysis recommends generation-indexing via
  `_D102_GENERATION_DERIVATIONS` (see `joulewise/calibration_bracketing.py`
  and `joulewise/floor_mint_estimator.py`).
- A second analysis proposes minting a NEW `_v3` PACK FAMILY instead of
  regenerating the `_v2` packs — a pack-identity design question: is a pack
  regenerated-in-place under the same identity, or is a new generation a new
  family member with lineage?
- HARD CONSTRAINT: `_ACCEPTANCE_SELECTION` is an independent axis — your
  design must NOT move it.
- The D-079 reissue TOOL cannot check v3 generations (it compares stored
  scalars); bespoke derive/build scripts were the r3/r4 route — your design
  should say what tooling the chosen shape demands.
- Budget ruling (magistrate, amends D-143 basis): Option B — 165,000
  UNCHANGED, calibrated on the claim-bearing population.

## What your design must decide

1. The fan-out mechanism: generation-indexed derivations vs _v3 pack family
   vs another shape you argue is better. State the pack-identity semantics
   your choice implies (what is frozen, what supersedes, what carries
   lineage).
2. Replay integrity: the n=19 estimator replay must remain byte-exact for its
   era. Show how your shape preserves historical replay while the successor
   family carries v3-derived values.
3. Enumerated touch points (file:line — verify in the tree yourself):
   calibration_bracketing.py, floor_mint_estimator.py, the three _v2 pack
   generators (floor-mint / detection-floor / pack), evidence author, test
   pins/goldens behind the 33 reds.
4. Tooling: what derive/build/verify scripts the shape needs, given the
   reissue tool's scalar-comparison limitation.
5. Composition with the atomic re-freeze: re-mints happen at
   /Users/edr/JouleWise-measurement-20260818 (path-binding); freeze-0002
   receipts are r2-era and currently untouched.
6. Incidental defects queued (fold in if your shape touches them, else say
   they stay queued): stale DEFAULT_ACCEPTANCE_BOUND_SHA256 genesis digest
   (zero consumers, live trap); evidence-author acceptance copy-list omits
   r3/r4.

## Constraints

- Science soundness above all; where discretion exists, choose what makes the
  stronger paper.
- Kernel edits = kernel + regen + test pins in ONE transaction.
- Do not design R1 (production capture v3 flip) — a separate seat owns it;
  note interactions if your design creates any.

## Deliverable (single markdown document, your final message)

(a) the decision, stated as a ratifiable spec; (b) pack-identity semantics;
(c) enumerated touch points with file:line; (d) replay-integrity argument;
(e) tooling plan; (f) test fan-out plan to FULL GREEN; (g) rejected
alternatives with reasons — including an explicit verdict on the refuted flat
migration, the generation-indexing route, and the _v3-family route; (h)
explicit disagreements with this brief's framing, if any; (i) open questions
only Ed can rule on, if any.
