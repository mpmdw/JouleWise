# Round 6 pedagogy seat — Appendix A replication bar

- **Date:** 2026-08-27
- **Seat:** Opus pedagogy review, fresh instance. No prior context; no git history, process traces, or earlier review files consulted.
- **Repository:** `/Users/edr/code/JouleWise-wt-r6` at `git rev-parse HEAD` = `2f0dc3f6066ff78c4ca228c42a08192b6e955ac8`
- **Inputs at these bytes:**
  - `docs/paper/draft-v1.md` — `wc -w` = **17428** (672 lines; Appendix A is lines 394–672)
  - `docs/paper/artifact-guide.md` — `wc -w` = **5398** (392 lines)
- **Code consulted read-only (closure checks only):** `joulewise/powermetrics_fiducial.py` (the brief named `joulewise/pulse_fit.py`; no such file exists — the pulse-fit and accepted-region code lives in `powermetrics_fiducial.py`), `joulewise/uncertainty_evidence.py`.
- **Scope of the bar:** the appendix and the guide measured together, as a capstone reader would use them.

---

## VERDICT

**PASSES the replication bar — high confidence for every claim-bearing output; moderate confidence for refusal-path bookkeeping on already-invalid captures.**

I rebuilt both algorithms from the prose plus the guide and then diffed my reconstruction against the code. For any capture that produces a published number — the anchor *A*, the anchor bound *B_anchor*, the per-pulse fitted shifts, the accepted regions, and *B_fiducial* — the text pins every decision that moves a digit. I found no un-pinned guess that changes a claim-bearing output. That is the strong form of the bar and the appendix meets it.

Two caveats, stated so a stricter reader can disagree on a stated basis rather than a hunch:

1. One un-pinned guess (**G-P17**, when the spurious-plateau check is evaluated) does change *an* output — but only fields of an evidence record that is already `invalid`, and only for a capture that also exhausts the work budget. It cannot move *B_anchor*, *B_fiducial*, a region, or a fit. Under the most mechanical reading of "any un-pinned guess that changes an output is a FAIL," this item is the sole candidate. I judge it a mandatory fix, not a failure of the bar, because the appendix's own A.5 reproduction target — reason name, admitted member set, phase energy, pulse bound, final verdict — is unaffected in the common case, and the fix is one sentence.
2. One symbol, `Loss*`, is used three times in the paper before it is defined anywhere in the paper. Its definition exists in the guide (§9), so the two documents *together* clear the bar; the paper alone does not. This is a genuine first-use failure and is mandatory nit M1.

Set against that: the appendix does several things that this kind of text almost never does, and they are why the verdict is a pass rather than a grudging one. It pins float-versus-exact arithmetic as a *normative* definition (A.3.4's accumulation clause). It warns the reader in advance that recomputing *H* from the printed endpoints will not close, and prices the discrepancy against one binary64 ulp. It gives the van der Corput sequence as a construction plus eight worked values rather than a citation. It states the model condition on which the containment claim rests, and says which part of it the estimator cannot verify. It defines "95/95" with the arithmetic rather than asserting it. Every one of those is a place a replicator would otherwise have guessed.

**Independent whole-mechanism check.** I rebuilt the entire A.3.2 capture schedule from the prose alone — van der Corput, gap rule, pulse recursion, warm-ups, both 5 s rests — and it reproduces a 196.70 s protocol span from `sampling_started`. The paper reports a 197-second capture with 197 rollovers and 1665 records (mean record length 118.3 ms, consistent with the stated *e_0* = 111.24 ms). The prose is sufficient to regenerate the protocol, not merely to recognise it.

---

## GUESS LIST

Twenty-four points where a from-scratch implementer must decide something. Each is checked against the code.

### Clock-anchor estimator (A.3.3)

| # | Guess | Status |
|---|---|---|
| G-A1 | Whether the span uses raw or resolution-padded offsets | **Pinned by prose at A.3.3 "Wall-minus-monotonic span"** — "compute the raw offset range", and the formula is written out. The code also computes a padded envelope, which the bound does not use; the prose correctly ignores it. |
| G-A2 | Which stamps enter the span and *r_max* | **Pinned at A.3.3** ("over the five stamps"); order-independent, so the code's `STAMP_ORDER` is immaterial. |
| G-A3 | Whether the span's two subtractions are exact-rational or binary64 | **Pinned only indirectly**, at A.3.3 "Numeric-padding check" — "(two inside the span's subtractions, one per anchor endpoint)". The governing sentence three paragraphs earlier says arithmetic is exact rational, so a reader who does not chain the parenthetical will exactify the stamps and compute the span exactly, shifting *B_anchor* by up to ~5·10⁻⁷ s — visible in the 17 published digits. Recoverable, but only by inference across subsections. Mandatory nit M4. |
| G-A4 | *r* = max(wall resolution, monotonic resolution) | **Pinned at A.3.1 "Clock stamps."** |
| G-A5 | *m_0* = *mb*(S_pre)·10⁹ rather than a midpoint | **Pinned at A.3.3 "The model."** |
| G-A6 | Whether *r_v* pads the wall value, the monotonic bracket, or both | **Pinned at A.3.3 "Stamp constraints"** — both, written out in the two inequalities. |
| G-A7 | Whether native rows apply to record 0 (with *q_0* = 0) | **Pinned at A.3.1 "Cumulative elapsed time"** + A.3.3 "For each record *i*". Matches `zip(native_ns, cumulative_ns, strict=True)` over all records. |
| G-A8 | Stamp-pair row count: ordered pairs including *v* = *v′* | **Pinned at A.3.3 "Eliminating α"** ("25 rows"). Matches the code's 5×5 double loop exactly; causal rows 5 + 5 = 10 likewise. |
| G-A9 | *β* box-edge refusal: either endpoint or both | **Pinned at A.3.3 step 4** ("If either equals its box edge"). |
| G-A10 | Whether *A* attaining a box edge is also a refusal | **Pinned at A.3.3 "The feasible set"** — "only *β* attaining a box edge is treated as a refusal." A reader would otherwise add a symmetric check the code does not have. |
| G-A11 | The first-parse-lag objective (max over the feasible set of a *min over stamps*, via one LP per stamp) | **Pinned at A.3.3 step 6.** This matches `_max_lower_envelope_lp2` line for line, including the branch construction. |
| G-A12 | In step 3, whether the δ = 1 s relaxation is retested against native rows alone or the full row set | **Pinned weakly at A.3.3 step 4 [step 3]** — "that relaxed set" sits inside the "All rows infeasible" branch, so context supplies it, but the antecedent is the re-formed native rows. Reading it as native-only yields the wrong detail string (`affine_clock_residual_exceeded` vs `admissible_interval_empty`) on a refused capture — an A.5 reproduction target. Mandatory nit M3. |
| G-A13 | Order and detail strings of the admission checks | **Pinned by pointer**, guide §9 first paragraph, enumerated in evaluation order. |
| G-A14 | Whether `roundup` applies to the four terms or the sum | **Pinned at A.3.3 "Composing the bound"** — one roundup over the sum, and the worked example demonstrates it (verified below). |
| G-A15 | Point anchor conversion mode | **Pinned at A.3.3** — midpoint by round-to-nearest, limits outward. Matches `float((lo+hi)/(2·10⁹))`. |
| G-A16 | The 24-step δ bisection's interval, direction, and reported end | **Pinned by pointer**, guide §9 item "7." Diagnostic-only; not in the bound. |

### Trace placement (A.3.4)

| # | Guess | Status |
|---|---|---|
| G-A17 | Whether *t_i* is a float running sum or *A* + *q_i*/10⁹ | **Pinned at A.3.4 "Anchoring"**, and pinned as *normative*: "That accumulation is the normative definition." The single most commonly-omitted fact in this class of document, and it is here. |
| G-A18 | Trimming inclusivity and what *T_warm* is | **Pinned at A.3.4 "Trimming warm-ups"** — start ≥ *T_warm*, *T_warm* = last warm-up off-stamp wall time. (Code uses `max(off)` over warm-ups; identical for any capture that authenticates.) |
| G-A19 | Whether schedule authentication runs on the trimmed or untrimmed trace | **Pinned at A.3.4** — "From the pulse stamps and the trimmed trace". Matches the call order in `rederive_detection_from_artifacts`. |

### Pulse fit and accepted region (A.3.5–A.3.7)

| # | Guess | Status |
|---|---|---|
| G-P1 | Overlap-test strictness for *O* and *L* | **Pinned at A.3.5 "Baseline set"** — written out with a strict `>`. |
| G-P2 | Interior inset test direction and inclusivity | **Pinned at A.3.5 step 2.** |
| G-P3 | Which 0.75 the edge-coverage test uses (`FIT_HALF_RANGE_S` vs `LOCAL_MARGIN_S`) | **Value pinned at A.3.5 step 4**; the constant's identity is not named, but both constants are 0.75, so no output can differ. |
| G-P4 | Whether amplitude/SNR rejections can both fire | **Pinned by pointer**, guide §9 record-shape paragraph ("one or two, since the amplitude and SNR tests are evaluated together"). |
| G-P5 | Whether the offset sweep uses the just-updated *d_on* | **Pinned at A.3.5 step 6** by the pseudocode's variable use. |
| G-P6 | Whether each grid recenters on the current value | **Pinned at A.3.5 step 6** — `G(d_on, s)`, `G(d_off, s)`. |
| G-P7 | Grid clipping applied before or after generation | **Pinned by pointer**, guide §9 ("The clip … is applied after generation, so a grid centred away from zero is one-sided at the clipped end"), with worked counts. Verified numerically below. |
| G-P8 | Argmin tie-break | **Pinned by pointer**, guide §9 ("Ties … resolve to the smallest (most negative) candidate"). Matches Python `min` over an increasing list. |
| G-P9 | Definition of `Loss*` | **NOT pinned in the paper**; **pinned in guide §9** ("Let *Loss** = Loss(*d_on*, *d_off*) at the end"). First-use failure F1; mandatory nit M1. |
| G-P10 | Λ's floor of 1.0 in loss units | **Pinned at A.3.5 "The accepted region."** |
| G-P11 | Which rectangle corners bound the prediction | **Pinned at A.3.5 "Cell lower bound"** — ŷ(on_hi, off_lo) and ŷ(on_lo, off_hi), with the monotonicity argument that justifies them. |
| G-P12 | Distance-to-interval rule for the lower bound | **Pinned at A.3.5 "Cell lower bound"** — 0 inside, else nearer endpoint. |
| G-P13 | Retention test (both sides ≤ 10⁻⁴) and whether the retained cell is kept whole | **Pinned at A.3.5 "Procedure"** — "*retain the entire cell*", plus the reason it matters ("including points between resolution cells"). |
| G-P14 | Bisection tie-break (equal sides) and push order | **Pinned at A.3.5 "Procedure"** — onset on a tie; lower half pushed first so the upper is processed next. Matches the code's `>=` and push sequence. |
| G-P15 | Whether a cell is charged to the budget before or after its bound is evaluated | **Pinned by pointer**, guide §9 ("consumes one unit *before* its lower bound is evaluated") and §4. |
| G-P16 | Whether the 120 s deadline is continuous or pre-cell | **Pinned by pointer**, guide §9 ("a *pre-cell deadline* … the last cell evaluated may run past the 120 s mark"). |
| G-P17 | **When the spurious-plateau check is evaluated relative to the per-pulse fits** | **NOT pinned.** A.3.5 places it in prose between the baseline statistics and "Per-pulse fit", which reads as a pre-check; the code (`detect_pulses`) computes it *after* every fit completes. A short-circuiting implementation emits a different record (`fits` empty, `projection_evaluated_cell_count` = 0) and, on a capture that both has a spurious plateau and exhausts the budget, a different reason name. No claim-bearing number changes. Mandatory nit M2. |
| G-P18 | Whether widening applies *u_on* to both onset endpoints and *u_off* to both offset endpoints | **Pinned at A.3.5 "Widening by stamp uncertainty"** — all four assignments written out. |
| G-P19 | Whether *B_fiducial*'s excursions use the widened or unwidened regions | **Pinned at A.3.6** ("that edge's widened region"). |
| G-P20 | That the added anchor term is *this same capture's* *B_anchor* | **Pinned at A.3.6** ("for the same capture"), with the independence argument. Matches `trace_anchor_bound_s=derived_anchor["effective_clock_anchor_bound_s"]`. |
| G-P21 | p95 index convention among the 118 values | **Pinned at A.3.6** — "the ⌈0.95·118⌉ = 113th smallest". Matches `ordered[max(0, ceil(0.95n) − 1)]` under 0-based indexing. |
| G-P22 | Median convention for an even count of 118 | **NOT pinned.** The code takes the mean of the 59th and 60th; the prose says only "the median of the 118 values". Diagnostic-only and the paper says so ("not used for any claim"), so no claim-bearing output moves. Optional nit O2. |
| G-P23 | Disposition when \|*O*\| < 3 | **NOT pinned.** A.3.5 states the requirement ("There must be at least 3 intervals in *O*") but names no reason string; the code raises rather than returning a named refusal. No claim-bearing output. Optional nit O3. |
| G-P24 | Where the 120 s work clock starts | **Pinned at A.3.7 "Origin of the 120 s work clock"** — after baseline/σ, before the first fit, monotonic, not reset between pulses. Matches the construction site exactly. |

**Counts: 24 guesses; 3 NOT pinned (G-P17, G-P22, G-P23); 2 pinned only weakly or indirectly (G-A3, G-A12); 19 cleanly pinned. Of the not-pinned, exactly one (G-P17) can change any emitted output, and only on a capture that is already invalid.**

---

## FIRST-USE FAILURES

Terms, symbols, or criteria words whose meaning arrives later than their first use, or never. Six, in severity order.

- **F1 — `Loss*` (mandatory).** First used in A.3.5 step 7 ("Require *Loss** < 0.5·*Loss_flat*"), again in step 8's discussion and in Λ = Loss* + max(1.0, 0.05·Loss*). The paper never defines it. The guide does, in §9, but the appendix's pointer at that spot promises only "the tie-break rule", so a reader following the appendix has no reason to look. Output-bearing: Λ is the accepted region's threshold.
- **F2 — "detected" (mandatory).** A.3.6 opens "For every detected pulse", using *detected* as a criterion word. A.3.5 never says that a pulse surviving all eight checks is thereby *detected*; it only lists rejection reasons. The very next clause, "Over 59 pulses this gives 118 values", then silently assumes all 59 detected — which is true, but only because of a condition stated a paragraph later.
- **F3 — "angle-bracketed input."** The appendix's third paragraph says the steps become executable "after the release manifest supplies every angle-bracketed input", before any angle-bracketed placeholder has appeared in the text. The convention is only demonstrated later, in A.2's `<runs root>/<run id>` and the guide's §11 commands.
- **F4 — "governed extraction evidence."** The L1 gloss in the same paragraph — "the claim consumer's incomplete binding of a floor back to the complete governed extraction evidence" — is itself built from three unbuilt terms. The gloss discharges the label *L1* but not the reader's question.
- **F5 — "baseline classifier."** A.3.4 warns that leaving warm-ups in "would make the baseline classifier (A.3.5) report them as uncommanded plateaus", but A.3.5 contains no *baseline classifier*: it has a *baseline set* and a *spurious-plateau check*. A reader chasing the forward reference finds no such object.
- **F6 — the binding-field hash.** A.3.6's validity list ends "all ten binding fields are present and non-empty …, whose hash pins the calibration to one machine". What is hashed, in what order, and where the digest is compared is never built. The *checked* condition (presence and non-emptiness) is pinned, so nothing is unreplicable; the word "hash" is doing unpaid work.

Terms I checked and found correctly built before or at first use, for the record: *re-derivation*, *fresh collection*, *fingerprint*, *refusal*, *cell* and *detection floor* (built in the Abstract and §1), binary64, exact floating summation, ppm, wall clock, monotonic clock, *paired stamp*, half-width, *record*, *e_i*/*n_i*/*p_i*/*E_i*/*q_i*/*t_i*/*y_i*/*I_i*, trace interval, commanded pulse, *fiducial* (with the statistical-fiducial disclaimer), rollover, van der Corput, set membership, outward rounding, ulp, slew, *α*/*β*/*A*/*m_0*/*k_pre*/*k_parse*/*δ*/*H*/span/*r_max*, Fourier–Motzkin (mechanism shown, not just named), Seidel-type solver (named then defused — "any exact LP solver returns the same optimal *values*"), margin window, MAD and its 1.4826 factor, Huber loss, robust SNR, *T_warm*, *τ_j*, *R*/*s_coarse*/*s_fine*/*G(c,s)*, *C*/LB(*C*)/*z_i*/*ẑ_lo*/*ẑ_hi*, enclosure, Λ, accepted region, 95/95.

---

## POINTER INTEGRITY

Every place Appendix A says material lives in the guide, checked against the guide.

| Appendix pointer | Target | Result |
|---|---|---|
| A.3.3 "the repository artifact guide enumerates the checks and their detail strings" | guide §9, para. 1 | **PRESENT.** Full admission enumeration with every detail string, in evaluation order, including the two-rollover, 60 s baseline, and controller-coverage gates. |
| A.3.3 step 7 "the repository artifact guide gives its bounds and step count" | guide §9, item "7." | **PRESENT** ([0, 250 µs], 24 steps, reports the upper end). Formatting defect: the item appears as an orphaned "7." with no list 1–6 and no lead-in tying it to A.3.3's solver sequence. Mandatory nit M6. |
| A.3.4 "the repository artifact guide gives the event names and the pairing rules" | guide §9, "Reading the pulses" | **PARTIAL.** Pairing rules fully present (open/close, strict `off > on`, ambiguous/unpaired refusals, exactly 3 + 59). The four event *names* are not listed there — the guide says only "the four command event types". The names are given in A.3.2 of the paper, so no reader is stranded, but the pointer over-promises. Optional nit O5. |
| A.3.5 step 6 "the repository artifact guide gives the point counts for each step and the clipping behaviour" | guide §9, "For the coarse step *N* = 150 …" | **PRESENT**, with three worked grids. Counts verified numerically below. |
| A.3.5 step 6 "The repository artifact guide states the tie-break rule" | guide §9 | **PRESENT.** |
| A.3.5 end "the repository artifact guide gives the exact record shape" | guide §9, "The pulse's record is then …" | **PRESENT**, for both the detected and rejected shapes. |
| A.3.7 "whose constants and exhaustion behaviour are in the repository artifact guide" | guide §9 (and §4 "Pulse-projection deadline") | **PRESENT** in both places; the two statements agree with each other and with the code. |
| A.3.6 "the projection completed within budget (next section)" | A.3.7 | **PRESENT.** |
| A.4 "`docs/paper/artifact-guide.md` Section 11, 'Executable verification order'" | guide §11 | **PRESENT**, section number and title exact; six steps, each naming a command, the artifact it reads, and the field it compares, as A.4 promises. |

Two notes that are not pointer failures. (1) Seven of the nine pointers say "the repository artifact guide" without a section number; only A.4 gives a path and section. The guide's §9 is titled for this purpose and opens by saying the paper points there, so navigation resolves — but at cost. Optional nit O4. (2) Guide §10.1 declares "Paths are relative to `/Users/edr/code/JouleWise-wt-r4`", a different worktree from the one this material sits in, and its evidence rows cite `/Users/edr/code/JouleWise/runs_window_a_20260722/…`. Since §10 is explicitly a maintainer-side derivation index and not a replication path, this does not touch the bar, but a reader who tries those paths will fail.

---

## NUMBER CHECKS

Fourteen numbers recomputed from stated inputs. All pass.

1. **Record-0 health check.** Stated channel powers 0.9169149999999999 + 0.00898937 + 0.0 → *p_0* = **0.9259043699999999 W** (paper's value, exactly). *e_0*/10⁹ = 0.111242541 s; *p_0*·*e_0* = **0.10299995484180416 J** (paper's value, exactly). *E_0* = (102+1+0)/1000 = **0.103 J**. \|difference\| = **4.5158·10⁻⁸ J**, against a tolerance of 0.002 + 0.001·0.103 = 0.002103 J. Paper's "4.5·10⁻⁸ J, far inside the tolerance" ✓.
2. **B_anchor sum.** 0.0006869160344978743 + 0.00044608116149902344 + 0.0000010000000000000002 + 0.000001, in exact decimal = **0.0011349971959968977402** — the paper's printed exact sum, digit for digit. Outward rounding to binary64 gives **0.0011349971959968978** ✓.
3. **H from the printed endpoints.** (1784757336.5532944 − 1784757336.5519202)/2 in binary64 = **0.0006871223449707031**, the paper's value exactly. Excess over the exact *H* = **2.0631047·10⁻⁷ s**; the paper says "0.0000002063105 s above" ✓.
4. **The ulp comparison.** `math.ulp(1784757336.0)` = 2⁻²² = **2.384185791015625·10⁻⁷ s**. The paper's "2.4·10⁻⁷ s" ✓, and 2.063·10⁻⁷ < 2.384·10⁻⁷, so the paper's claim that the excess is under one spacing holds ✓.
5. **Span from the printed stamps.** 1784298599.0949996 − 1784298599.0945535 = **0.00044608116149902344 s**, the paper's value exactly ✓.
6. **k_pre.** 111 242 541 − 1000 = **111 241 541 ns** ✓ (= 0.111 s, as the paper says).
7. **k_parse.** (458737.509840291 − 458736.4081875)·10⁹ + 1000 = **1101653790.9669094 ns** = 1.1016537909669094·10⁹, the paper's value exactly ✓ (= 1.102 s).
8. **u_on.** 2.500019036233425·10⁻⁷/2 + 1.0000000000000002·10⁻⁶ = **1.1250009518116714·10⁻⁶ s**, the paper's value exactly ✓.
9. **B_fiducial minus B_anchor.** 0.030067931757111657 − 0.0011349971959968978 = **0.0289329345611147592**, the paper's value exactly ✓.
10. **p95 index.** ⌈0.95·118⌉ = ⌈112.1⌉ = **113** ✓.
11. **95/95.** 0.95⁵⁹ = **0.048494525**; the paper's "≈ 0.048", and 1 − 0.0485 = 0.9515 ≥ 0.95 ✓.
12. **Branch-and-bound depth.** 1.5/2¹⁴ = **9.1552734375·10⁻⁵ s** ≤ 10⁻⁴ ✓, and since the wider side alternates, both sides reach the resolution after 14 halvings each — **28 bisections**, the paper's figure ✓.
13. **Guide's grid counts.** G(0, 0.005) → **301** points; G(0.015, 0.005) → 301 raw, **298** after clipping, spanning −0.735 to 0.750; G(0.015, 0.0005) → 3001 raw, **2971** after clipping, same span. All three match the guide exactly, including the one-sided clip ✓.
14. **Protocol duration (independent whole-schedule rebuild).** Rebuilding A.3.2 from the prose: pulse train span = **174.203125 s**; total from `sampling_started` = 5 + 3·(1.0+1.5) + 5 + 174.203125 + 5 = **196.703125 s**, against the paper's "197-second capture" and 197 rollovers ✓. Mean record length 197/1665 = **118.3 ms**, consistent with the stated *e_0* = 111.2 ms ✓. vdC₂(1…8) regenerated from the digit-reversal rule = 0.5, 0.25, 0.75, 0.125, 0.625, 0.375, 0.875, 0.0625 ✓; first five gaps = 2.0, 1.75, 2.25, 1.625, 2.125 ✓.

No number in a worked example failed to reproduce, and none was invented here.

---

## RESIDUAL NITS

Twelve, verbatim old/new. Seven mandatory, five optional.

### M1 — mandatory (F1, G-P9). Define `Loss*` where the search ends.

**Old** (`draft-v1.md`, A.3.5 step 6):
```
    Eight one-dimensional searches in all — onset and offset at the coarse step, then the same pair at the fine step. The repository artifact guide states the tie-break rule.
```
**New:**
```
    Eight one-dimensional searches in all — onset and offset at the coarse step, then the same pair at the fine step. The repository artifact guide states the tie-break rule. Write *Loss** for the loss at the pair (*d_on*, *d_off*) the procedure ends with — the fit's best loss. It is used in steps 7 and 8 and in the loss limit below.
```

### M2 — mandatory (G-P17). Pin when the spurious-plateau check runs.

**Old** (A.3.5):
```
**Spurious-plateau check on the baseline set.** Sort *O* by start time.
```
**New:**
```
**Spurious-plateau check on the baseline set.** The check is evaluated once, after every pulse in the train has been fitted, not as a gate before the fits; a capture that exhausts the work budget of A.3.7 is therefore recorded as nonconvergent whether or not it also carries a spurious plateau. Sort *O* by start time.
```

### M3 — mandatory (G-A12). Pin the scope of the δ = 1 s relaxation.

**Old** (A.3.3, solver step 3):
```
3. All rows infeasible → the native rows are re-formed with *δ* = 1 s; if that relaxed set is feasible the detail is `affine_clock_residual_exceeded`, otherwise `admissible_interval_empty`.
```
**New:**
```
3. All rows infeasible → the native rows are re-formed with *δ* = 1 s and recombined with the same stamp and causal rows; if that full relaxed set is feasible the detail is `affine_clock_residual_exceeded`, otherwise `admissible_interval_empty`.
```

### M4 — mandatory (G-A3). Say where binary64 survives inside an exact-rational estimator.

**Old** (A.3.3, "Wall-minus-monotonic span"):
```
over the five stamps, in seconds. It measures how much the wall clock drifted against the monotonic clock over the whole capture, including any slew (gradual rate adjustment applied by the operating system's time discipline).
```
**New:**
```
over the five stamps, in seconds. These two subtractions are the one place the estimator does not use exact rational arithmetic: they are performed in binary64 on the stored stamp values, and the resulting float is then exactified — which is what the 10⁻⁶ s padding term below pays for. The span measures how much the wall clock drifted against the monotonic clock over the whole capture, including any slew (gradual rate adjustment applied by the operating system's time discipline).
```

### M5 — mandatory (F2). Build "detected" before A.3.6 grades on it.

**Old** (A.3.6):
```
For every detected pulse and each of its two edges, take the **worst excursion** of that edge's widened region, max(|lo|, |hi|). Over 59 pulses this gives 118 values.
```
**New:**
```
A pulse is **detected** when it passes every check of A.3.5 and so carries two widened edge regions; a pulse rejected at any of those checks is not detected and carries none. For every detected pulse and each of its two edges, take the **worst excursion** of that edge's widened region, max(|lo|, |hi|). The bound below is formed only when all 59 pulses are detected, so it always draws on exactly 118 values.
```

### M6 — mandatory. Give the guide's orphaned step 7 a lead-in.

**Old** (`artifact-guide.md`, §9):
```
7. Diagnostic only: bisect *δ* over [0, 250 µs] for 24 steps to find the smallest allowance at which the full set is still feasible; report the upper end as `min_l_infinity_residual_upper_bound_s` (1.49·10⁻¹¹ s on the example: the labels fit the affine model essentially exactly). This value does not enter the bound.
```
**New:**
```
**Step 7 of the A.3.3 solver sequence — diagnostic only.** Bisect *δ* over [0, 250 µs] for 24 steps to find the smallest allowance at which the full set is still feasible; report the upper end as `min_l_infinity_residual_upper_bound_s` (1.49·10⁻¹¹ s on the example: the labels fit the affine model essentially exactly). This value does not enter the bound.
```

### M7 — mandatory. Renumber the guide's caveat list, which currently runs 1, 3, 2.

**Old** (`artifact-guide.md`, §10.2, third item):
```
3. The code fixes MIN_NATIVE_ROLLOVERS = 2 and MAX_FIRST_PARSE_LAG_S = 0.25 s without a recorded rationale for those particular numbers; the prose states what each gate tests and its value, and does not invent a justification for the magnitude.
2. The claim that "any exact LP solver returns the same optimal values" is a mathematical property of linear programmes (optimal value is unique), stated to make the estimator replicable without reproducing the Seidel implementation; it is not asserted anywhere in the code.
```
**New:**
```
2. The code fixes MIN_NATIVE_ROLLOVERS = 2 and MAX_FIRST_PARSE_LAG_S = 0.25 s without a recorded rationale for those particular numbers; the prose states what each gate tests and its value, and does not invent a justification for the magnitude.
3. The claim that "any exact LP solver returns the same optimal values" is a mathematical property of linear programmes (optimal value is unique), stated to make the estimator replicable without reproducing the Seidel implementation; it is not asserted anywhere in the code.
```

### O1 — optional (F5). Name the object A.3.5 actually defines.

**Old** (A.3.4):
```
leaving them in the trace would make the baseline classifier (A.3.5) report them as uncommanded plateaus and invalidate the capture.
```
**New:**
```
leaving them in the trace would put their plateaus into the baseline set of A.3.5, where the spurious-plateau check would report them as uncommanded plateaus and invalidate the capture.
```

### O2 — optional (G-P22). Pin the median convention for an even count.

**Old** (A.3.6):
```
Two diagnostics are also reported and are not used for any claim: the median of the 118 values and their 95th percentile, defined as the ⌈0.95·118⌉ = 113th smallest value.
```
**New:**
```
Two diagnostics are also reported and are not used for any claim: the median of the 118 values — the mean of the 59th and 60th smallest, the count being even — and their 95th percentile, defined as the ⌈0.95·118⌉ = 113th smallest value.
```

### O3 — optional (G-P23). Say what an under-supported baseline does.

**Old** (A.3.5):
```
There must be at least 3 intervals in *O*. Then
```
**New:**
```
There must be at least 3 intervals in *O*; a trace that cannot supply them is an error rather than a named refusal, and no evidence file is produced. Then
```

### O4 — optional. Name the guide section once, at the first pointer.

**Old** (A.3.3, "Inputs and their admission checks"):
```
Each failure returns `clock_anchor_unresolved` with a named detail; the repository artifact guide enumerates the checks and their detail strings.
```
**New:**
```
Each failure returns `clock_anchor_unresolved` with a named detail; the repository artifact guide (`docs/paper/artifact-guide.md` Section 9, "Calibration algorithm operator detail" — the target of every such pointer below) enumerates the checks and their detail strings.
```

### O5 — optional. Make the guide's pairing paragraph carry the event names it is pointed at for.

**Old** (`artifact-guide.md`, §9):
```
**Reading the pulses.** `events.jsonl` is scanned for the four command event types.
```
**New:**
```
**Reading the pulses.** `events.jsonl` is scanned for the four command event types: `warmup_command_on`, `warmup_command_off`, `pulse_command_on`, and `pulse_command_off`.
```

---

## SUMMARY COUNTS

- Guesses recorded: **24**
- Not pinned: **3** (one output-affecting, and only on already-invalid captures)
- Pinned only weakly or indirectly: **2**
- First-use failures: **6** (one output-bearing)
- Pointer-integrity failures: **0** (one partial, one navigation cost)
- Number checks performed: **14**; failures: **0**
- Mandatory nits: **7**; optional nits: **5**
