# Falsifier consult — three blind seats (2026-08-28)

Convened by the consult director on the reviewer panel's NEEDS-RULING #2
(`docs/process_traces/2026-08-28-reviewer-panel/04-SYNTHESIS.md` §3 items 1,
2, 17; convergent finding C2, C3; divergent D10). Three seats — Sol
(gpt-5.6-sol, xhigh, read-only), Opus 5, a fresh Fable 5 — receive THIS
brief verbatim, have no contact with each other, and write a recommendation
plus the strongest counter to it. The MAGISTRATE rules; no seat writes a
ruling. Nothing in this consult edits code, the paper, the pack, or any
process doc.

## Standing facts (director-verified; seats re-verify at file:line)

Repo: `/Users/edr/code/JouleWise` (main at `340f8bfc`). The reviewer-panel
files are on branch `docs/paper-reviewer-panel` (PR #230), checked out at
`/Users/edr/code/JouleWise-wt-panel/docs/process_traces/2026-08-28-reviewer-panel/`
(`01-sol-reviewer.md`, `02-opus-reviewer.md`, `03-fable-reviewer.md`,
`04-SYNTHESIS.md`). The D-157/W-10 families block lives on branch
`fix/d139-a2-gamma-families` (PR #209, OPEN), checked out at
`/Users/edr/code/JouleWise-wt-s8-d139-families/` — see
`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py`
~1681–1730 there (`design`, `replacement_policy`, `families`, `contrasts`,
`finalization_contract`, `frozen_semantics_sha256`). The prospective
manifest's exact top-key set is `joulewise/analysis_manifest.py:37-47`
(`TOP_KEYS`) with `DESIGN_KEYS` at :48-55 — keys are validated as an EXACT
set, so a new key is a contract change, not a free addition.

**Ruling items** (`docs/process_traces/2026-08-27-t26/paper-goal-consult/03-MAGISTRATE-RULING.md`):

- Item 28 (line 231): two titles drafted and held in the results-fill
  registry — primary around attribution-limited resolution (used if `_v4`
  reproduces dominance), S8's protocol-first title as the null-outcome
  title; neither typeset before results issue.
- Item 34 (line 265): "the paper's falsifier IS the code's dominance
  predicate, verbatim — per-component comparison as coded (`A_guarded =
  guard_factor × max(max_abs_residual_j | max_abs_delta_j,
  prediction_component_j)`; no invented aggregate), and TERM B is the exact
  corner maximum the predicate compares (derived at the desk under the
  replay fence)." Registry rows are written to that
  (`docs/paper/results-fill-registry.md:197-261`, sixteen TERM_A/TERM_B
  rows, all `VALUE_UNISSUED`).

**The predicate** — `joulewise/detection_floor.py:806-843`
`admissible_set_uncertainty_dominates_point_floor`. Point gate
`_point_floor_diagnostic` (:788-803): `g(n) · max(max|r_i|, P)` with
`P = t_{0.95,n−1} · s_r · √(1+1/n)` (`_floor_estimate` :689-719;
`prediction_extra = 0` for absolute, `|mean Δ|` for comparative);
`g(n) = max(1, √(9/(n−1)))` (:664-673, `GUARD_REFERENCE_N = 10`, so
g(10) = 1). Absolute TERM B (:822-831):
`max_i(|r_i| + h_i(n−1)/n + (Σh − h_i)/n)`; comparative TERM B (:832-835):
`max_i(|d_i| + w_i)`. Predicate: `TERM B > point gate`.

**Director's algebra (verify or refute):** with equal widths h and n = 10,
absolute TERM B = `max|r| + 2h(n−1)/n = max|r| + 1.8h`; t(9) = 2.262,
`P = 2.372 s_r`.
- Regime 1, `max|r| ≥ 2.372 s_r`: the predicate is `max|r| + 1.8h > max|r|`,
  TRUE for every h > 0. Widths are never zero in production:
  `calibration_bracketing.py:199-214` binds `a_t = max(observed, 0.009724 s)`
  into every `h_i`.
- Regime 2, `max|r| < 2.372 s_r`: true iff `h > (2.372 s_r − max|r|)/1.8`.
  Since `max|r| ≥ s_r·√((n−1)/n) = 0.949 s_r` for any sample, the threshold
  ranges over (0, 0.79 s_r]; the synthesis's "h ≳ 0.26 s_r" corresponds to
  `max|r| ≈ 1.9 s_r`. State the general form and the range, not one point.
- Comparative: same shape with `|mean Δ| + 2.372 s_Δ` as the P term.
- The §3 zero-width sanity sentence (`docs/paper/draft-v1.md:103`,
  "forcing all timing-envelope widths to zero flipped the registered
  dominance predicate from true to false") is vacuous for a predicate that
  is monotone in h and returns False by construction at `not any(widths)`
  (:816-817).

**Diagnostic values** (July-25 a9/a10 cells, retired anchor, diagnostic-era
label; `draft-v1.md:103, 298`): point floors 0.2888 / 0.4934 / 0.3113 J;
corner-widened 3.153 / 2.922 / 2.184 J; ratios 10.92 / 5.92 / 7.02. Note
the ratio is unguarded/unguarded (the g(n) cancels) and its numerator is
the full corner-maximized floor (`_corner_maximized_unguarded_floor`
:856ff), not TERM B. `_v4` has NO collected data; do not peek at or reason
from any `_v4` artifact.

**Common-mode issue (C3):** within a block `floor_extraction.py::
_common_mode_block_half_width` composes shared + local; across the ten
blocks `comparative_false_effect_floor` varies the scalar widths
independently — conservative for the gate, but inflates the timing side of
the dominance comparison.

**Campaign state — READ THIS, it moved today.** D-164 (Ed, 2026-08-28,
`docs/decision_log.md` index row, commit `340f8bfc`): the production
campaign runs on a NEWER model pair (from
`docs/process_traces/2026-08-28-model-panel/`); "the swapped pack is
generation `_v5` of the same frozen design (D-139 A2 families, 2 contrasts,
n=10, 80 members), minted by the same path after its own estate clone
proof; `_v4` is never collected. Cost accepted by Ed: ≈2 Sol desk-days
(D-016/D-074 admission of the pair, generator re-pin, estate 12) →
transaction night ≈ 2026-09-01/02 … Estate 11 still runs tonight as the
mint-path rehearsal." Governing constraints still in force: D-140 (bytes
inside the freeze receipt's `pack_identity` closure never change
post-mint; no post-mint repair), D-153 (any non-config cure ⇒ new family
generation), D-157 (`families` is byte-bound into the semantics digest and
plan tree; the freeze path now REFUSES a manifest the prospective validator
rejects; a mint-path change ⇒ S-0 re-runs as a new estate). So: a
pre-registered falsifier that is minted INTO the pack must be in the
generator/manifest before the `_v5` mint; the question is whether it rides
the `_v5` re-generation Ed already paid for, or costs more Sol-days and/or
another estate.

## Questions (answer all four; number your answers)

1. **Vacuity.** Is the registered predicate near-vacuous as stated? Verify
   the director's algebra at file:line — confirm, correct, or refute it
   with your own derivation. State exactly what the boolean CAN and CANNOT
   falsify.
2. **The sound pre-collection registration.** If (1) holds, what
   registration makes the headline falsifiable before collection?
   Candidates: a pre-registered dominance RATIO with a threshold (which
   ratio — corner-widened/point-only as in the diagnostic values, or
   TERM B/TERM A? which threshold — ≥2, ≥3, other — and how do you defend
   it from 10.92/5.92/7.02 without peeking at `_v4`/`_v5`?); a
   common-mode-fiducial variant (which one gates, which one is reported);
   both. WHERE does it live — the analysis manifest `design` block, a new
   top-level key, a new registered predicate in `detection_floor.py` with a
   registry row, or the results-fill registry + RQ row only? Which of those
   count as "pre-registered" (minted into the pack) vs "declared in a
   document"? Cost in Sol-days, and whether it fits inside the `_v5`
   re-generation already scheduled (before estate 12) or forces a further
   estate.
3. **Steelman the status quo.** The strongest argument for leaving item 34
   as ruled — the coded boolean as THE falsifier — and reporting the ratio
   descriptively (per-cell column, no threshold).
4. **Item 17 / D10.** The two-title device (item 28) vs the Fable
   reviewer's objection that it "signals the outcome will steer the
   framing." Keep, drop, or replace with what?

## Output contract

Write to YOUR seat file (path given in your launch message), Markdown,
≤ 2,000 words: a header naming your seat and model, then
`## 1`…`## 4` each ending with **Recommendation:** and **Strongest
counter:** lines, then `## Arithmetic` with every number you relied on and
its file:line, then `## Confidence` (one line). Read-only: touch nothing
else. Do not read the other seat files under
`2026-08-28-falsifier-consult/`; if one exists, ignore it. Do not write a
ruling.
