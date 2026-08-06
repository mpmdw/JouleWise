# D-110 re-mint fork — magistrate synthesis (2026-08-06, pending Ed's ruling)

Inputs: `DIAGNOSIS.md` (live reproduction of the structural block at main
`c537386`), `CONSULT-PROMPT.md` / `CONSULT-RESPONSE.md` (Sol xhigh
pre-decision design consult, run `20260806T165843Z-10884`, read-only,
Fast Mode).

## The finding

No historical window (a10 2026-07-25, window-C 2026-07-26, old window-D
2026-07-26, 7B-floor 2026-07-29, contrast 2026-07-30) can pass
authenticated max-bracket consumption at merged main: the issued ledger
contains only import-marked receipts, candidate discovery excludes imports
by design (originating in the CAL-BRACKET/ledger arc, commit `63f43a68`;
retained and test-enshrined through the issuance reconciliation), and
future live receipts cannot causally bracket past windows. The bootstrap
and bracketing contracts are individually sound and jointly exclude the
D-110 re-mint as desk work.

## Magistrate position (concurring with the consult recommendation)

**Adopt Option 2 — supersede the historical re-mint with prospective
collection.** Three compact claim-coherent windows (fresh 1.5B decode
floor; fresh 7B decode floor; fresh 1.5B-vs-7B contrast), each with fresh
§5A, live pre/post calibration receipts appended to the issued ledger,
own verdict + head-pin + custody. Claims chain:

historical corpus → issued D-079 acceptance rule → prospective live
brackets → prospective floors → prospective contrast.

Grounds: it removes the one provenance weakness imports cannot repair
(reservation-first contemporaneous completeness; retrospective
authorization after outcomes are known), matches the paper's stated
method, avoids amending just-issued semantics, and is the strongest
defensible chain for a metrology-expert advisor. Option 1 (historical
candidacy) is PHYSICALLY plausible — the consult verified complete
matching bracket pairs for all five historical windows, drifts
0.000167–0.003680 s, all under the 0.010818 s screen — and is preserved
ONLY as a separately versioned finite-allowlist contingency requiring a
rule-11 cold gate (semantics sketch in the consult response §3).

## Corrections adopted from the consult

- Fresh collection does NOT remove imports from the chain: the acceptance
  RULE derives from the historical n=19 corpus and 38-member prior set.
  Honest claim: historical data establish the rule; live receipts bracket
  all claim-bearing science.
- `window_contrast_20260730` is also pre-genesis: closing historical
  consumption invalidates the banked contrast evidence too, not just
  a10/window-C/7B.
- "Window D" naming is unavailable (collides with `runs_window_d_20260726`
  and D-113's reserved C/D terminology); the three fresh windows get new
  immutable plan/root identifiers.
- The mint's D-084 hard literal remains an independent refusal under ANY
  option; closure is per-plan pin supply via the generalized mint path.

## What this needs from Ed (apex authority; his ruling moots a cold gate)

1. Ratify superseding D-110's re-mint order with prospective replacement
   (decision-log entry on his word), including the D-113 dependency
   rewire the consult flags.
2. Confirm the MVP claim scope (decode contrast only, or more phase
   cells) — sets the fresh-window count.
3. Schedule appetite: three quiet-mac nights (est. ~3.0 h + ~2.6 h + a
   comparable 1.5B window, each incl. margin), his presence for §5A.

## Desk work unblocked NOW regardless of the ruling (consult §4)

Freeze the three window plans + runtime budgets; build the 1.5B
decode-only floor plan from the proven 10-absolute/40-null design;
verify/finish generalized mint pinsets for both fresh floors (per-plan
six-decimal literals); freeze extraction specs, order manifests,
evidence-root ids, contrast manifest; add a synthetic three-window
live-ledger integration regression; prepare the D-102 successor-artifact
packet so a range-expanding live observation cannot strand the campaign;
results/methods prose with placeholders.

Until Ed rules, no decision-log entry is written and the historical
corpora remain exactly as they are (non-claim-bearing per D-110 cl.1,
untouched on disk, logs sha-verified).
