# Cold-gate ruling on D-165 (provisional) — 2026-08-28

## 0. Seat and contamination
Cold Fable 5 instance, fresh session, no loop context. Disclosed contamination: this
session auto-loads `CLAUDE.local.md` and the project memory index (doctrine rules,
D-128/D-161/D-164 summaries, "seven-day paper mandate"); none of it addresses the
falsifier, the ratio, or the titles. Packet read in the prescribed order; every
load-bearing claim below re-read at file:line on `main` (`joulewise/detection_floor.py`,
`joulewise/analysis_manifest_v3.py`, `joulewise/floor_extraction.py`,
`joulewise/floor_mint_estimator.py`, the PR #209 generator). One Opus 5 contract-lens
refuter, custodied verbatim as `05-cold-gate-refuter.md`.

## 1. Verdicts

**R-1 — ADOPT.** Reversal of item 34 is warranted: the coded boolean is monotone in every
width (`detection_floor.py:822-835`), returns `False` at zero widths by construction
(`:816-817`), and in the `max|r| ≥ P` regime is true for any positive width; at the
diagnostic cells it cleared by ≈30×. Item 34's real content — no invented aggregate, per
component as coded — survives intact, because R is per component per cell. The numerator
`_corner_maximized_unguarded_floor` (`:856-908`) re-evaluates the FULL floor
(`max(max|r|, t·s·√(1+1/n))`) at every box corner, so R − 1 is "the whole-floor inflation
the admitted timing envelope causes, scatter re-evaluated at the corner included," not a
pure TERM-B widening. That is still the plain meaning of "dominates" — the widened floor
exceeds the point floor by at least the point floor — and it is the number the paper
already prints (10.92/5.92/7.02), so one dominance number appears, not two. `R ≥ 2` is
defended from the sentence at `draft-v1.md:298`, not from the retired ratios; the ruling
must say so in the paper, and must disclose the pilot ratios as pilot evidence.
Refuter (Q2) confirms R ≥ 1 identically and R > 1 for any positive width, so `> 1` would
be F-1's tautology and `≥ 2` is a bar that can fail; R is a ratio of two already-emitted
fields (`floor_extraction.py:1328-1336`), which makes the ≈1 Sol-day credible.
Implementation clause to be read into R-1 (a specification the ruling omits, flagged by
both the refuter and the seats): R is computed per registered component (absolute,
comparative — the claim-bearing contrasts consume the COMPARATIVE path,
`floor_extraction.py:629-632`; a9/a10 were absolute) per claim-bearing cell,
unguarded/unguarded, `≥ 2.0` with the exact-equality and zero-denominator cases stated;
the headline passes only if EVERY registered component passes; mixed outcomes are
reported per component and take the null framing.

**R-2 — AMEND.** Gating on the independent-corner R is correct (it is the built,
replayable estimator; `R_ind ≥ R_cm` always, so it is the permissive gate and R_cm the
honest one). Two defects in the null consequence:
(a) **`R_cm ≤ 1` is an unreachable trigger of the same shape the ruling is reversing**
(refuter Q3: FAILS; my reading agrees). The corner floor is a max over box corners of a
function whose corner values dominate the centre value, so `R_cm ≥ 1` identically and
`> 1` strictly for any positive width; `local_width = fsum(residuals)/2` plus the
never-zero allowance guarantee positivity. The band `1 < R_cm < 2` is the entire
reachable domain below 2, not a corner case. AMENDED: the withdrawal fires at **`R_cm < 2`** — the
same standard as the gate. In the band the ruling left open (`1 < R_cm < 2`) the sentence
does not stand; it is reported as "independent-corner dominance only, not established
under the shared-fiducial treatment," with the C3 caveat printed.
(b) **Enforceability.** `_common_mode_block_half_width` (`floor_extraction.py:447-494`)
composes `shared_width` (`:481-484`) + `local_width` (`:485`) as locals and returns ONE
scalar; the emitted floor row carries only the composed `admissible_half_widths_j`
(`:1331-1332`). The split is destroyed before emission, so R_cm is NOT derivable from what
`_v5` will mint as ruled; D-140 forbids adding it after. AMENDED: before the `_v5` mint,
S15 either (i) emits the shared/local split per block (an artifact-emission change on the
floor path, to be costed against the 09-01/02 window and, if it moves the mint path,
absorbed by estate 12), or (ii) registers a replay rule computing R_cm from the custodied
block inputs (onset/offset/zero-point/residuals) under the replay fence, or (iii) registers
"R_cm not derivable — C3 caveat printed verbatim." One of the three is chosen and written
into the registration pre-mint; "mandatory disclosure" with no chosen route is the
ruled-not-installed shape. Scope note (refuter Q3): the deviations-from-mean cancellation is an ABSOLUTE-kind
argument; on the comparative path a common shift moves `|mean Δ|` and does not cancel.
R-5's bench check is scoped to that distinction.

**R-3 — AMEND.** The hash claim holds: `floor_estimator_registration` is a contrast key
(`analysis_manifest_v3.py:1049`, finalized `:1162`), passed through opaquely (`:1605-1607`),
hashed inside `contrasts` by `_prospective_semantics` (`:1531-1542`), asserted against
`frozen_semantics_sha256` at `:2704` and at finalization `:4051`. No `_exact_keys` call
touches its interior. But "no validator change" is only true of `analysis_manifest_v3.py`.
The registration dict IS a validated contract elsewhere: `validate_common_mode_estimator_registration`
(`detection_floor.py:530-536`) is **whole-dict equality** against
`two_shared_edge_common_mode_registration()`, enforced on the floor-plan path
(`floor_extraction.py:1125-1154`, `:2577`) and the mint estimator
(`floor_mint_estimator.py:88-95, :271-278`). If `dominance_criterion` is added INSIDE the
producer's return dict (`detection_floor.py:483-527`), every artifact carrying the old
bytes fails equality — the six issued extraction specs
(`configs/floor_mint/d117_qwen25_{1p5b,7b}{,_v2,_v3}_extraction_spec.json`, three
registrations each), the v1/v2/v3 `calibration_plan.json` / `analysis_manifest_v3.json`
goldens, and `tests/test_d117_decode_contrast_plan.py:2276-2286`, which asserts the
committed `_v1` pack equals live producer output — and the D-124 estimator's registration
changes semantics under an unchanged `COMMON_MODE_ESTIMATOR_VERSION = "v1"` (`:115`).
The ruling does not say which placement it means; the refuter (Q1: HOLDS WITH CAVEAT)
and I converge that it must. AMENDED placement: the generator emits the
contrast's `floor_estimator_registration` as
`{**two_shared_edge_common_mode_registration(), "dominance_criterion": {...}}` at its three
sites (PR #209 generator `:1021, :1040, :1623`); the producer function, the floor plans,
and `COMMON_MODE_PARAMETER_SHA256` are untouched. This keeps the digest binding, the
D-157/D-140 compliance, and the ≈1 Sol-day cost, and adds no mint-path change beyond the
regeneration D-164 already bought. Second amendment: an interior no validator reads is
exactly the contract-required-input-with-no-check shape D-157 R-2 closed the class on. The
frozen `detection_floor.py` function that computes R must READ its threshold and
definition from the manifest's `dominance_criterion` (or a golden test must assert the
manifest's sub-object equals the frozen constants); a falsifier registered as inert bytes
is declared, not enforced.

**R-4 — ADOPT.** One outcome-invariant, protocol-first title fixed pre-mint; the
attribution-limited phrasing survives only as a subtitle contingent on the R ≥ 2 gate
(all registered components). The dissenting Fable seat's condition — branch rule
disclosed in the paper's methods in one sentence — is adopted with it, since a subtitle
that appears with the result is still an outcome-contingent surface. Item 28's `_v4`
condition is struck (D-164: never collected) and replaced by the registered gate.

**R-5 — ADOPT.** F-2 is a floor-estimator semantics question, not a falsifier question;
Sol xhigh bench check before `_v5` freeze, NEEDS-RULING on confirmation, estate consequence
stated. Add: the bench check also decides whether the absolute component's R_cm is even
defined, which R-2(b) depends on.

**R-6 — ADOPT.** The clone-proof artifact is the only evidence that "minted into the pack"
is true; the addendum waits for it. The ruled-not-installed pattern (T26) makes this
clause load-bearing, not ceremonial.

## 2. Refuter disposition
`05-cold-gate-refuter.md` (verbatim). Q1 HOLDS WITH CAVEAT → R-3 AMEND (placement bound
to the generator's contrast dict; six specs + `_v1` equality assertion are the evidence).
Q2 HOLDS WITH CAVEAT → R-1 ADOPT with the quantifier/kind clause; the refuter's point that
R − 1 bundles corner-recomputed scatter and (comparative) mean shift is accepted as a
description the paper must print, not a reason to switch to TERM B/TERM A, which is
unpublished. Q3 FAILS → R-2 AMEND on both counts. No refuter point rejected.

## 3. Standing
D-165 binds as amended above (R-2 threshold and derivation rule; R-3 placement and
read-back). The magistrate may overrule only with written dissent Ed sees (rule 11).
