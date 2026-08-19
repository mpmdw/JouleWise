# CO-DESIGN BRIEF R1 — Production capture-pipeline v3 adoption

WRITE_SCOPE: []

You are an INDEPENDENT DESIGN SEAT in the JouleWise co-design protocol
(D-144-pending): two seats design independently, then a bounded debate, then a
Fable magistrate ruling. You have explicit license — and a standing record of
peer designs out-designing the lead's — to disagree with any framing in this
brief. This is a READ-ONLY consult: read anything in the tree, run read-only
commands and tests, write NOTHING inside the repo.

## Situation

Branch `integration/phase2-transaction` @ 9f7f091. The anchor-v3 arc is
ratified science (read docs/process_traces/2026-08-18-anchor-v3-science-review/
and docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md — the
sections from "Conditions executed (afab1a2)" to end are the authoritative
recent state). Capture activation for v3 landed at bb81323 for 3 of 4 sites,
and the science-neutral D-079 r4 acceptance artifact is issued (dcb3d3ed…,
one pin moved, neutrality proven by direct 19-member estimator replay).

The atomic family re-freeze cycle is PARKED at steps 3–6 pending this ruling.

## The design question

The PRODUCTION capture pipeline still hardcodes the v2 capture-pipeline
identity at 4 sites in `joulewise/adapters/powermetrics.py` and emits the
`p2-038.2` limitation label. Flipping production to v3 touches:

- `joulewise/cli.py` strict verify (see ~:1272 and the :1541–:1564 docstrings —
  the D-078 precedent is there: stored p2-038.1 bundles keep legacy
  reconstruction and are NOT re-judged; p2-038.2 bundles must byte-match a
  re-derivation)
- the campaign gate (cli.py ~:1644 region)
- contracts (docs/contracts/) that name the capture-pipeline identity
- `joulewise/controller.py`, `joulewise/uncertainty_evidence.py`,
  `joulewise/analysis_engine/inputs.py` all reference capture-pipeline identity
- 54 historical bundles on disk carry the v2 label → THE ADMISSION-GATE
  QUESTION: what does strict verify / the campaign gate / analysis admission do
  with stored v2-label bundles after production flips to v3?
- One currently-failing canonical test —
  `test_whole_window_selection…embeds_allowance_once` — fails from exactly this
  root, fail-closed. It is evidence for this ruling, not a defect to patch
  around.

## What your design must decide

1. Label semantics: does production v3 mint a new limitation label
   (p2-038.3?), retire p2-038.2, or keep the label and version the pipeline
   identity elsewhere? Justify against how p2-038.1→.2 was handled.
2. Admission policy for the 54 stored v2-label bundles, per consumer class
   (strict verify, campaign gate, analysis admission, claim consumption).
   Follow or distinguish the D-078 precedent explicitly. Fail-closed is the
   default posture; any admission of v2 bundles must state what re-derivation
   or evidence it demands.
3. Flip scope: the exact site list (enumerate file:line yourself — verify the
   4 powermetrics.py sites, don't trust this brief), what flips atomically
   inside the parked re-freeze transaction vs what may not be part of it.
4. Test/goldens fan-out: what the flip breaks, how canonical returns to FULL
   GREEN, and which new tests the design itself demands (attack-shaped, not
   confirmation-shaped).
5. Interaction with the frozen family: freeze-0002 receipts at the
   measurement checkout are r2-era and UNTOUCHED; your design must state
   precisely how the flip composes with the atomic re-freeze (re-mints happen
   at /Users/edr/JouleWise-measurement-20260818, path-binding).

## Constraints

- Science soundness above all; where discretion exists, choose what makes the
  stronger paper.
- The D-078 no-retry discipline and all freeze semantics bind.
- Do not design R2 (mint-lane fan-out shape) — a separate seat owns it; note
  interactions if your design creates any.

## Deliverable (single markdown document, your final message)

(a) the decision, stated as a ratifiable spec; (b) enumerated touch points
with file:line; (c) per-consumer admission policy table for historical
bundles; (d) migration + test fan-out plan to FULL GREEN; (e) rejected
alternatives with reasons; (f) explicit disagreements with this brief's
framing, if any; (g) open questions only Ed can rule on, if any.
