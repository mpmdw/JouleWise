# Reviewer-panel synthesis — three blind seats on the frozen draft (round 6)

Paper under review: `docs/paper/draft-v1.md` at `f6544b08` (frozen after PR
#219; #226 fidelity fixes). Three seats, one brief (`00-REVIEWER-BRIEF.md`),
blind to each other and to the process traces:

| seat | file | words | score now | if `_v4` reproduces | if it does not | (b) pick |
|---|---|---|---|---|---|---|
| Sol (gpt-5.6-sol, xhigh, read-only) | `01-sol-reviewer.md` | 3,138 | 3 | 3 | 2 | inserted-gap fiducial |
| Opus 5 | `02-opus-reviewer.md` | 5,996 | 3 | 4 (cond. on desk fixes) | 2 (3 with the fiducial) | inserted-gap fiducial |
| Fable 5 (fresh) | `03-fable-reviewer.md` | 4,117 | 3 | 4 (cond. on W1–W3) | 3 (2 without desk fixes) | inserted-gap fiducial |

All three: 3/5 borderline, none docked for the `[PENDING]` results, all three
rank the `_v5` model ladder LAST for the measurement week. The director
spot-checked the two code-level claims that two seats made independently
(below); both are true as stated.

## 1. Convergent findings (two or three seats, without contact)

C1. **Pulse-to-inference transfer is untested and every number rests on it**
(Sol W1, Opus W1, Fable strength+W2). All three name §7 "Nothing in the frozen
`_v4` campaign tests that transfer" as the #1 or #2 score-limiter, and all three
say the paper's own Future Work #1 is the cure. Opus: placing it *after* the
campaign "is the single largest score-lowering decision in the paper"; "a PC
will not accept 'the pack is frozen' as a scientific reason."

C2. **The registered dominance predicate is weak, and vacuous in the outlier
regime** (Opus W2, Fable W1 — both read `detection_floor.py:806`; Sol W2 reaches
the adjacent conclusion from the envelope model). Director check: the code
compares `max_i(|r_i| + h_i(n−1)/n + (Σh − h_i)/n)` with
`g(n)·max(max|r_i|, t·s_r·√(1+1/n))`. Whenever `max|r_i|` is the larger point
term the predicate is true for ANY `h > 0`; otherwise at n=10 it is
`max|r| + 1.8h > 2.372 s_r`, i.e. roughly `h ≳ 0.26 s_r`. Both seats: the
substantive content is the RATIO (10.92 / 5.92 / 7.02), not the boolean; the
"prospective null" apparatus in §1/§10 is "largely decorative" (Fable),
"'dominates' is doing unpaid work" (Opus). Opus also: the §3 zero-width sanity
check ("forcing widths to zero flipped the predicate") is vacuous for a predicate
monotone in `h`.
   → This CONTRADICTS ruling item 34 ("the paper's falsifier IS the code's
   dominance predicate, verbatim"). It is NEEDS-RULING, not a round-7 edit.

C3. **The corner enumeration re-independises the shared fiducial term** (Sol W2,
Opus W3). Within a block the code composes shared+local
(`floor_extraction.py::_common_mode_block_half_width`), but across the ten
blocks `comparative_false_effect_floor` varies the scalar widths independently.
Conservative for Gate 1, but self-serving for the finding: it inflates exactly
the timing side of the dominance comparison. Both ask for the ratio under a
common-mode treatment as well as the unconstrained one.

C4. **The calibration bound is dominated by a repeatable, opposite-sign edge
bias that the paper never names** (Fable W2, Opus W9/req. 9 and (a)). Pulse 0
onset ~+16 ms late, offset ~−11 ms early; the worked example onset lag in
[25.4, 28.9] ms with a 2–3 ms accepted-region width. If the sign pattern holds
across the 59 pulses, ~30 ms is mostly a stable bias plus a few ms of scatter —
a *characterisation* the paper should print, and the concrete mechanism by which
transfer can fail (GPU dispatch/ramp latency of a 4096² matmul ≠ runtime-event-to-
power latency at a prefill→decode transition). Both seats independently choose
"publish the 118-excursion distribution" as the (a) desk move.

C5. **The "95/95" label on `B_fiducial` assumes 59 i.i.d. draws the paper
denies elsewhere** (Sol W3, Opus W8). Either show no trend vs pulse index / no
onset–offset correlation, or relabel as "sample maximum over 59 commanded
pulses of one capture".

C6. **Undisclosed constants** (Sol W3, Opus W7, Fable W4/req. 8–9):
`g(n)=max(1,√(9/(n−1)))` has no derivation; 9.724 ms and 10.164835 ms appear
two sentences apart at seven significant figures with no derivation and no
statement of how they relate. Director check: `calibration_bracketing.py:199-214`
binds 0.009724 (95 % two-draw pin, n=17), 0.010164834757777545 (99 % pin,
"maximum budgetable drift"), 0.010818 (n=19 screen). Opus: the value in force is
the SMALLER candidate and enters `a_t = max(observed, 0.009724)` in every `h_i`,
so the open reconciliation is permissive in direction — "stating that no current
claim depends on the superseded value is not the same as showing the difference
is immaterial." (Ruling item 32 chose to print one value with a note; two seats
say the note is not enough.)

C7. **Two diagnostic-era `[PENDING]` values in the §6 resolvability example are
fillable today** (Sol W6, Opus req. 5, Fable W3/req. 6): record width
111.8–112.5 ms and median spacing 120.922 ms are in the registry (DG-071,
DG-075) held only for a declared statistic. "The paper's single fully worked
negative-result example currently has two of its three numbers missing."

C8. **Unfrozen suppliers are a design defect, not a placeholder** (Sol W4, Opus
W5b, Fable req. 5/Q8): D-123 reported-mean schema `STOP_FILL/SUPPLIER_UNKNOWN`,
DS-29 claim-side bound unbuilt, some Table 3 verdict bindings unbound. Sol: "no
numerical `_v4` outcome can repair an undefined estimand retrospectively" —
freeze before collection or remove the columns.

C9. **Not independently re-reducible (FLOOR-BIND-01 / L1)** (Sol W8, Opus W4,
Fable W7). Candid, but "from outside, indistinguishable from 'trust us'"
(Opus). All three ask the paper to say what closing it requires and whether it
closes before camera-ready.

C10. **Internal identifiers and process language leak into the frozen text**
(Fable W3, Opus W9): D-152, P06, DS-29, C5-1.3, FLOOR-BIND-01,
`calibration_acceptance_d079_v2_n17_r3`, the `[[NEEDS-VALUE …]]` editorial note
in §6, artifact field names inline. Round 6 glossed the field names once; two
seats say that is still too much for a PC reader — collapse to one
term→field table, cited once.

C11. **Bibliography** (Sol W9, Opus W9): ten uncited entries; [19] and [23]
unverified. (Ruling item 62 already schedules removal+renumber for round 7.)

C12. **Length/repetition** (Fable W6, Opus W9): the "largest false difference"
gloss verbatim in abstract, §1, §6, §7; the transfer-assumption sentence seven
times; a prose walk of each figure repeated in the caption.

## 2. Divergent findings (one seat only — verbatim)

D1. Opus W5(a), the p256 resolvability cliff: "If a 128-token 1.5B prefill runs
~0.121 s and yields two records, a 256-token prefill plausibly yields three —
i.e. the demonstration's prefill arm is designed to land *on* the resolvability
threshold, where a few-millisecond alignment accident decides admissibility per
member. The paper never states the projected overlap count for either model at
256 tokens, and never states the contingency if the 1.5B arm is not resolvable.
Half the demonstration could be a printed refusal for a reason known in advance."

D2. Opus W6, the motivating ratios were computed under the retired anchor: "The
ratios that motivate the entire paper were computed with the estimator whose
error the paper's first contribution fixes … report, over the retained
diagnostic captures, the distribution of `B_fiducial` change under
re-derivation with the corrected model. That both defends the diagnostic ratios
and honestly sizes contribution #1, which as written implies a correction whose
numerical effect on the published bound may be under 4 % and whose real effect
was on *admissibility*."

D3. Opus req. 11, an internal contradiction: Table 1 workload-response row
"Evaluate each slope at every joint corner … n=40" vs §4 "Exact enumeration
refuses above n=16". "2⁴⁰ corners are not enumerated; the OLS slope is linear in
the energies so its corner extremum is analytic. Say so in one sentence."

D4. Opus W9 / req. 13: "No plotted measured data anywhere. Figures 1, 2, and 3
are all schematics … Add: one real pulse from a retained capture with the fitted
rectangle and the accepted-region band overlaid; and the overlapping-record-count
histogram behind '37 of 50'."

D5. Opus W10, missing lineage: Marzullo interval-intersection, Kopetz, Cristian,
Wilks (1941) tolerance limits, Milanese & Vicino set-membership — all [VERIFY].
Fable req. 15 adds Burtscher/Zecena/Zong 2014 (K20 built-in sensor lag) and
Raffin & Trystram — [VERIFY].

D6. Sol W5, the inferential unit: "Ten blocks from one long window can share
calibration error, thermal trajectory, background conditions, and serially
correlated sampler behavior. A deterministic drift allowance can widen an
interval but does not automatically make Student-t sampling units independent."
Asks for the total-standard-error formula, degrees of freedom, covariance
assumptions, missing-block behaviour.

D7. Sol W7, no gain check: "the paper supports a counter-internal
phase-attribution result more strongly than it supports energy differences in
physical joules."

D8. Fable W5, only the GPU channel is calibrated: "If the three channels are
sampled and averaged on a common window there is no problem, but the paper does
not say so … 'probably small' is a claim the paper should make and bound, not
leave implicit."

D9. Fable Q4, possible double counting: "Why is the whole-window drift allowance
A_k added as a joule term to the *floor* rather than treated as an interval on
the contrast, given that the A/B/B/A order already cancels linear drift? Isn't
this double-counting for the comparative component?"

D10. Fable req. 16 vs ruling item 28: "choose one title before submission; the
two-title device signals the outcome will steer the framing, which sits uneasily
beside 'fixed before collection.'"

D11. Fable W4: the identical-condition null test "will contain five fresh draws
almost by construction; passing carries little evidential weight" — state its
power in terms of floor/scatter.

D12. Score divergence: Sol holds 3 even if dominance reproduces ("the transfer,
dependence, and coverage issues still prevent an accept"); Opus and Fable go to
4 conditional on the desk fixes in C2–C4.

D13. (a) desk pick divergence: Sol wants an "uncertainty-and-dependence ledger"
(per term: unit, deterministic/statistical, coverage, shared-by session/block/
member, gate it enters, validated under pulses/inference) plus a sensitivity
table; Opus and Fable want the 118-excursion bias/scatter decomposition (C4).
These are complementary, not competing.

## 3. Ranked round-7 improvement list

Round 7 = results fills + one fidelity pass (ruling item 59). Items marked
NEEDS-RULING touch a ruled item or the registered RQ and are for the magistrate,
not the fill director. Ranking is by score impact × seat convergence.

### Desk-only (no measurement)

1. **NEEDS-RULING — the falsifier.** Register a ratio with a pre-specified
   threshold (`R = corner-widened / guarded point-only`, ≥2 or ≥3, defended) as
   the headline; keep the coded predicate as the *label* predicate, named as
   such; report R per cell as a column in Tables 2 and 3; delete the zero-width
   sanity sentence. `_v4` has NOT collected (V4-TRANSACTION-01 READY), so this
   can still be a pre-collection registration; it changes the RQ row (item 8)
   and item 34. (C2; Opus req. 1–2, Fable req. 1–2, Sol Q3.)
2. **NEEDS-RULING — common-mode dominance ratio.** Report the ratio under both
   the independent-corner and a shared-fiducial-across-blocks treatment; state
   which is used for gating and why. (C3; Opus req. 3, Sol req. 2.) Derivable at
   the desk from the retained artifacts under the replay fence.
3. **Bias/scatter decomposition of the 118 edge excursions** on the worked
   capture (median, IQR, min, max, sign, vs pulse index): one table + one
   paragraph naming the dispatch/ramp mechanism and stating that `B_fiducial`
   includes a repeatable bias by design. Also discharges C5 (independence
   evidence) and D4 (a first measured-data figure). (C4; Fable req. 3, Opus
   req. 8–9.) Deterministic re-derivation from retained bytes; no
   registration change.
4. **Fill the two diagnostic-era `[PENDING]`s in §6** by declaring the statistic
   (DG-071/DG-075). (C7.)
5. **Derive the three bracket constants in the text** (95 % / 99 % two-draw pins
   over n=17; n=19 binds 0.010818) and bound the effect on floors of the larger
   value — extends ruling item 32's note into a disclosure. `g(n)`: derivation or
   citation, and why it vanishes at n=10. (C6.)
6. **95/95 label:** add the independence check or relabel. (C5.)
7. **Identifier sweep:** every D-/DS-/P06/C5-1.3/FLOOR-BIND-01 token becomes the
   ruled value + one-clause rationale or a pointer to the artifact guide; the
   `[[NEEDS-VALUE …]]` §6 note is filled (F, B, margin) or replaced by "the
   decision used C ≈ 5 J as a planning figure without decomposition"; artifact
   field names collapse to one term→field table. (C10; C8 partly.)
8. **Suppliers frozen or columns removed** before collection: D-123 means,
   Table 3 bindings; `B_decode_claim_J` stays STOP_FILL per item 33 but the
   sizing paragraph says so in plain words. (C8.)
9. **p256 projection + contingency:** projected overlap count for 1.5B and 7B
   at 256 tokens from retained durations and realised spacing; what happens to
   the Holm family if the 1.5B prefill arm returns `not_resolvable_sample_count`;
   prompt length behind "37 of 50". (D1; Opus req. 6, Q3–4.)
10. **Table 1 n=40 vs n=16 enumeration cap:** one sentence (analytic corner
    extremum of a linear slope). (D3.)
11. **Quantify the anchor correction:** distribution of `B_fiducial` change on
    re-derivation of retained captures under the corrected model; does it
    preserve the 10.92/5.92/7.02 ratios. (D2.)
12. **FLOOR-BIND-01 sentence:** what closing it requires and whether it closes
    before camera-ready. (C9.)
13. **De-duplication:** "largest false difference" once; transfer sentence in
    abstract/§7/§10 only; figure prose walks to two sentences. (C12.)
14. **Bibliography:** remove the ten orphans and renumber (already item 62);
    verify [19], [23]; fix [13]; consider the D5 lineage citations, each
    [VERIFY] before insertion.
15. **Inferential unit paragraph:** define the block as the sampling unit, the
    total-standard-error formula, degrees of freedom, missing-block rule. (D6.)
16. **One sentence each:** CPU/ANE channels share the GPU averaging window (or a
    bound) (D8); why the absolute component enters a paired-contrast gate and
    why `A_k` is not double-counted against A/B/B/A (D9); null-test power (D11);
    the joule-vs-counter framing (D7).
17. **NEEDS-RULING — title device** (D10 vs item 28).

### Needs measurement

M1. **Inserted-gap fiducial** (~10 real-workload runs, one night, existing
    estimator) — all three seats' (b) pick, "by a wide margin" (Opus). Design
    notes from the seats: fit both the fall and the rise (a 500 ms sleep is a
    dip, not the prefill→decode step — Fable); pre-register one- vs two-sided
    residual comparison; run on members otherwise identical to admitted ones
    (Opus). Ruled Future Work #1 / TRANSFER-FIDUCIAL-01 (item 16). The seats'
    unanimous view is that it should be IN the paper, not after it.
M2. **Two-point prompt-length check** (128 vs 256 on both models, ~1 night) —
    retires D1 before the demonstration is committed. (Opus rank 2.)
M3. **Cross-session floor stability** (≥3 sessions, 2–3 nights) — Fable rank 2;
    ruled to Future Work by item 12.
M4. **Micro-delta challenge** (0.5/1/1.5/3× floor) — Sol rank 2, Fable rank 3.
M5. **External-meter request-total gain check** — Sol rank 3.
M6. **`_v5` model ladder** — LAST for all three: "multiplies conditional results
    rather than removing the condition" (Opus); "spend the night on the
    assumption, not the demonstration" (Fable); "amplifies the reach of the
    instrument without first strengthening its validity" (Sol).

## 4. The "impressiveness" moves, ranked by value per night

1. **Inserted-gap fiducial — one night.** The only move valuable under BOTH
   `_v4` outcomes: with dominance it makes the headline defensible rather than
   conditional; without it, it makes the null interpretable (edge placement is
   genuinely not limiting vs the pulse bound does not describe inference —
   opposite conclusions a bare null cannot separate). Opus: "'Insert a commanded
   fiducial into the real workload and check your calibration against it' …
   would be the most quotable methodological sentence in the paper — arguably a
   stronger contribution than the dominance finding itself." Moves Opus's
   null-outcome score 2→3.
2. **The 118-excursion bias/scatter characterisation — zero nights.** Turns "we
   bound the edge error at ~30 ms" into "the sampler reports onsets ~X ms late
   and offsets ~Y ms early, repeatably, with Z ms of scatter" — the difference
   between describing an instrument and showing one; gives the paper its first
   plotted measured data; supplies the independence evidence the 95/95 label
   lacks; sizes how much of the ~1 J is correctable in principle. Two seats
   picked it independently; the third's ledger (D13) is its natural table.
3. **Ratio-as-headline with a common-mode variant — zero nights, but a ruling.**
   A soundness repair that reads as an upgrade: if the 5–11× ratios survive the
   shared-term treatment and a registered ≥2/≥3 threshold, the finding is much
   stronger than the boolean currently makes it look; if they do not, the paper
   learns it before `_v4` rather than from a reviewer.

## 5. Director notes for the magistrate

- Two desk items (list 1, 2, 17) contradict ruled items 34, 28 and touch the
  candidate RQ row; they are reported, not applied. The pack is frozen and
  untouched by any of them — they are analysis-plan / registration text.
- Director bench checks: the predicate at `detection_floor.py:806-843` and the
  three constants at `calibration_bracketing.py:199-214` are as the seats
  describe; V4-TRANSACTION-01 is still READY (no real collection), so a
  pre-collection threshold registration is still possible.
- All seat texts are custodied verbatim; the Sol file carries its thread id and
  final envelope. No edit was made to `docs/paper/**`.
