# Opus 5 reviewer seat — blind, 2026-08-28

## 1. Summary of contribution

The paper argues that phase-resolved energy measurement of LLM inference has a
timing problem that repetition cannot fix: prefill and decode are separated by a
boundary that must be placed on a power trace, the power step across that
boundary is large, and a boundary placed tens of milliseconds wrong moves on the
order of a joule from one phase into the other while leaving the request total
untouched. To price that error the authors run a commanded GPU pulse train
immediately before and after every measurement session, fit each pulse's onset
and offset against the instrument's reported trace, and keep not the best fit but
a guaranteed enclosure of every edge placement the data cannot rule out; a
set-membership clock-anchor estimator (rate-aware, replacing an earlier and
incorrect equal-rate model) places the trace on the controller's wall clock and
prices that placement. The worst per-edge excursion plus the anchor bound becomes
a per-session timing bound, which is propagated through the energy integral so
that every run's phase energy becomes an interval. Those intervals are then
corner-maximised into a per-cell "resolution bound" — the largest false
difference the system can manufacture — which acts as a magnitude gate, paired
with a separate direction gate over a composed uncertainty interval, with printed
refusals when either fails. The registered primary question is whether the
boundary-attribution term exceeds the run-to-run repeatability term for prefill
and decode on one M3 Max / MLX / *powermetrics* configuration. Results are
[PENDING] by design; the paper ships the design, the corrected calibration
mathematics (Appendix A is a genuine build-it-from-the-text specification), a
real negative result (37 of 50 diagnostic-era prefill phases were not resolvable
under a three-record overlap rule), and a fixed-before-collection 7B-vs-1.5B
demonstration whose job is to exercise the decision behaviour rather than to
report a scaling law.

## 2. Strengths

- **The problem is correctly identified and correctly located.** Framing phase
  attribution as a *time*-axis problem complementary to the RAPL *gain*-axis
  literature (§8, "an external wall meter still cannot determine how a software
  trace should divide a correct total between prompt processing and token
  generation") is the right insight, and it is defended rather than asserted. The
  Hähnel [29] and Dauner [23] positioning is accurate and generous to prior work.
- **Appendix A.3 is the best part of the paper and is unusually good.** The
  clock-anchor estimator is specified to the level of the Fourier–Motzkin
  elimination, the box, the refusal codes, and the four bound terms with an
  explicit statement of why none subsumes another; the branch-and-bound enclosure
  is specified with its monotonicity argument, its cell lower bound, its
  resolution, and its retain-whole-cell rule. I could reimplement both from the
  text. That is a rare thing to be able to write in a review.
- **The set-membership choice is the right one and is used honestly.** Reporting
  the extent of the admissible edge set rather than a fitted point, and refusing
  rather than clipping when the rate window or the anchor bound leaves its
  allowed range, is the correct instinct for a bounded-systematic error.
- **The worked example discipline.** §2's reconstruction from five raw clock
  stamps through to the maximal pulse, and A.3.3's four-term bound with the
  explicit warning that recomputing *H* from the printed (outward-rounded)
  endpoints will not close, is exactly the level of care a metrology venue wants.
- **The negative result is real and is not buried.** "37 of 50 failed the
  resolvability rule" is a genuine, publishable finding about what a 100 ms-class
  software counter can and cannot support at prefill scale, and the paragraph
  that distinguishes record width, record spacing, and the overlap *count* is a
  well-built piece of teaching.
- **Scope discipline throughout.** The paper repeatedly refuses to claim
  transfer: "The numerical bound does not transfer. Nor does this capstone
  establish a property of software counters as a class." §7 and §9 volunteer
  limitations (L1 floor-binding, 748 barred bundles, no independent gain check)
  that many submissions would have hidden.
- **Refusals as first-class output.** The A/B/B/A counterbalancing with retained
  midpoints, the fail-closed window rule, the quarantine-and-replace record, and
  the "a `REFUSED` comparison is a scientific result" argument together form a
  coherent anti-selective-reporting design rather than a slogan.

## 3. Weaknesses, ranked

### W1. The pulse-to-inference transfer is untested, and the whole quantitative claim rests on it — while the test costs one night

*Where:* §7, "Nothing in the frozen `_v4` campaign tests that transfer." Abstract:
"This scale comes from commanded calibration pulses and is assumed to apply to
sustained mixed inference load; the prospective collection will not test the
transfer."

*Why it matters:* every number the paper will publish — every *h_i*, every cell
floor, every gate outcome, and the headline dominance verdict itself — is a
function of a bound measured on 1 s square GPU pulses at ~40 W amplitude over a
0 W baseline under light CPU load, then applied to sustained mixed CPU+GPU+ANE
inference. The two regimes differ in exactly the ways that plausibly change edge
reporting: baseline offset (0 W vs tens of watts), step height, step *shape* (a
commanded matmul fence versus a runtime phase transition that is not
instantaneous in the hardware), thermal state, and the number of active samplers
contributing to the record. A reviewer's first question is whether the ~29 ms
worst excursion is a property of the instrument or a property of the pulse. The
paper answers, correctly, that it does not know. The authors themselves name the
experiment that answers it (Future Work #1, the inserted-gap fiducial, ~10 runs)
and then place it *after* the campaign. That ordering is the single largest
score-lowering decision in the paper: it leaves the central quantity unvalidated
in the submitted version when validating it is cheaper than one science stage.

*Fixable:* needs measurement — but only one night, with code that already exists.

### W2. The registered "dominance" finding is decided by a predicate that is weak, and on some cells vacuous

*Where:* §1, "The finding is falsified for a phase if the timing-widened bound
does not exceed the point-only repeatability bound." §4, "the exact linear corner
maximum used by the code's predicate strictly exceeds the guarded point-only
value."

I checked the implementation (`joulewise/detection_floor.py`,
`admissible_set_uncertainty_dominates_point_floor`). The comparison is

    uncertainty_max > g(n) · max( max_i|r_i| ,  t_{.975,n-1} s_r √(1+1/n) )

with, for the absolute kind,
`uncertainty_max = max_i( |r_i| + h_i(n−1)/n + (Σh − h_i)/n )`. For uniform
half-width *h* this is `max_i|r_i| + 2h(n−1)/n`. Two consequences:

1. **Whenever `max_i|r_i|` is the larger of the two point terms, the predicate is
   true for any positive *h* whatsoever** — it reduces to *h* > 0. One outlying
   run in a cell is enough to put a cell in that regime, and then the paper's
   primary research question cannot fail for that cell.
2. **Otherwise the effective bar is astonishingly low.** The `_v4` design has
   n = 10, so g(10) = √(9/9) = 1, t = 2.262, and the predicate becomes
   `max_i|r_i| + 1.8h > 2.372 s_r`. For roughly Gaussian residuals with n = 10,
   `max_i|r_i| ≈ 1.5–1.9 s_r`, so the finding is declared whenever the timing
   half-width exceeds roughly a *quarter* of the run-to-run standard deviation.

"Dominates" is doing unpaid work. A term contributing ~26 % of a standard
deviation is not dominance in any ordinary sense, and a term contributing
anything at all is not dominance in the outlier regime. The paper's own sanity
check makes the point against itself: "Forcing all timing-envelope widths to zero
flipped the registered dominance predicate from true to false, showing that
phase-edge placement, rather than the predicate itself, produced the widening."
Setting *h* = 0 flips a predicate that is monotone in *h* by construction; that
demonstrates nothing.

The *substantive* content is in §3's ratios — 10.92, 5.92, 7.02 — which are
genuinely large and genuinely interesting. Those are the finding. The registered
falsifier is not.

*Fixable at the desk:* yes, and it must be, before collection — register the
ratio with a pre-specified threshold (≥ 2, ≥ 3, whatever the authors defend) and
report the ratio, not the boolean, in Tables 2 and 3.

### W3. The corner enumeration re-independises a term the paper elsewhere insists is shared, which inflates exactly the side of the comparison the finding needs

*Where:* §4 step 3, "each independent energy or block difference enters as
[x_i−h_i, x_i+h_i]. Enumerate all 2^n joint corners." Against §3, "Those are not
30 independent timing draws: every member in the session contains the same shared
fiducial term plus a member-local term."

Every member and every block inside one window shares one `b_fiducial_s`. A joint
corner that sets block 1 to +h and block 2 to −h asserts that the shared edge
bound was in two places at once. The code does handle this *within* a block —
`joulewise/floor_extraction.py::_common_mode_block_half_width` sweeps a common
onset/offset and composes `shared_width + local_width` — but the resulting scalar
block widths are then handed to `comparative_false_effect_floor`, whose corner
enumeration varies them independently *across* the ten blocks. A genuinely
common-mode shift moves every δ_i together: it inflates |δ̄| but not s_δ, and it
largely cancels in an A/B/B/A contrast. Independent enumeration inflates both.

The direction of the error is the problem. Over-conservatism is safe for Gate 1
(fewer claims pass), but it is *self-serving for the finding*: it enlarges the
timing side of the very comparison that decides attribution dominance. The
diagnostic ratios of 10.92 / 5.92 / 7.02 are therefore upper bounds on the real
ratio by an unquantified factor.

*Fixable at the desk:* yes — decompose h_i into shared and local across blocks,
enumerate corners over the local part only, add the shared part common-mode, and
report the dominance ratio both ways. If the ratio survives, the finding is much
stronger than it currently is.

### W4. The claim-authorising chain is not independently re-reducible, at a venue that cares

*Where:* §9, "The registered L1 floor-binding limitation prevents describing the
present chain as independently re-reducible… Standalone or externally supplied
floor artifacts remain non-claim-bearing." Appendix A, "**not presently open to
independent re-reduction**." §9, "**[REPOSITORY AND ARCHIVE LOCATORS PENDING
RELEASE CHECKLIST]**."

A paper whose entire thesis is that measurement claims must be gated on
authenticated evidence, and which then cannot let a third party rebuild the
authorising link, is in an awkward position. The honesty is admirable and the
distinction drawn ("a third-party-verifiability limit, not an instrument-physics
defect") is fair. But an ICPE-shaped PC evaluates artifacts, and "a floor may
support a claim only when governed extraction and the consuming analysis run in
the same lead-controlled custody session" is, from outside, indistinguishable
from "trust us." At minimum the paper needs to say what closing FLOOR-BIND-01
requires and whether it will be closed before camera-ready.

*Fixable:* desk/engineering, not measurement.

### W5. The p256 prefill arm is designed on an untested extrapolation and sits near the resolvability cliff the paper itself discovered

*Where:* §6, "It is an **extrapolation**: none of the forty retained contrast
configurations uses more than 128 prompt tokens." And §6's own negative result:
"**37 of 50 failed the resolvability rule**", with the worked case at a
0.121034145 s prefill yielding two overlapping records against a threshold of
three.

Two distinct problems.

(a) **Feasibility.** If a 128-token 1.5B prefill runs ~0.121 s and yields two
records, a 256-token prefill plausibly yields three — i.e. the demonstration's
prefill arm is designed to land *on* the resolvability threshold, where a
few-millisecond alignment accident decides admissibility per member. The paper
never states the projected overlap count for either model at 256 tokens, and
never states the contingency if the 1.5B arm is not resolvable. Half the
demonstration could be a printed refusal for a reason known in advance.

(b) **The sizing decision cannot be reconstructed.** "The decision record gives
only approximately 5 J for C, not its exact components: [[NEEDS-VALUE: exact
cell-floor F, claim-side bound B …]]". The arithmetic that selected 256 tokens
(1.16× C vs 2.32× C) is printed, but its denominator is a number the paper cannot
recover, built from a quantity whose "supplier is not yet built" and which the
registry (`docs/paper/results-fill-registry.md`, row DS-29) records as
unresolved. A pre-registration whose sizing input is unreconstructable is weaker
than it looks.

*Fixable at the desk:* (a) yes — project the counts from retained phase durations
and record spacings and register a contingency. (b) yes — either recover F, B and
the margin, or say plainly that the 256 choice was made against an approximate
disclosure and that the pre-registration's force does not depend on it.

### W6. The paper's motivating magnitude comes from a corpus it has declared unfit for claims, computed under the anchor model it is correcting

*Where:* Abstract, "Diagnostic-era evidence identifies the scale: boundary
uncertainty during a steep power change can move about 1 J into the wrong phase."
§3's ratios. Against §7, "The 748 bundles made with the retired clock-anchor
calculation remain auditable under that calculation but are permanently barred
from claims", and §2, "This corrected rate-aware model replaced the false
equal-rate assumption, which could move every fitted edge in the same direction."

The ratios that motivate the entire paper were computed with the estimator whose
error the paper's first contribution fixes — an error described as capable of
moving *every* fitted edge coherently, which is precisely the way to inflate
per-member envelopes. The paper labels them correctly ("evidence of the
phenomenon under the retired 25 July calculation") but still leans on them in the
abstract and in §7's "what the finding changes".

The fix is in hand and the paper nearly states it: §2 already reports that
re-deriving capture `20260722T145535-e941c821` under the current anchor
"reproduces both the capture bound and the evaluated-rectangle count exactly",
and B_anchor is 1.135 ms of a 30.07 ms bound — 3.8 %. Say this generally: report,
over the retained diagnostic captures, the distribution of `B_fiducial` change
under re-derivation with the corrected model. That both defends the diagnostic
ratios and honestly sizes contribution #1, which as written implies a correction
whose numerical effect on the published bound may be under 4 % and whose real
effect was on *admissibility*.

*Fixable at the desk:* yes; the re-derivation path is deterministic and already
demonstrated.

### W7. Two load-bearing constants are undisclosed, and one of them is knowingly unreconciled in the anti-conservative direction

*Where:* §2, "A difference greater than 10.164835 ms refuses the window." §4 step
5, "The paper uses one value for this screen throughout: 9.724 ms… A superseded
ruling records a larger figure, derived when the calibration corpus held nineteen
members rather than seventeen; that discrepancy is registered… its reconciliation
is pending."

Both numbers are printed to seven significant figures with no derivation. They
are not arbitrary — `joulewise/calibration_bracketing.py` shows 0.009724 s and
0.010164834757777545 s as the 95 % and 99 % two-draw prediction pins of a
17-member calibration corpus, and the n=19 derivation binds 0.010818 s instead —
but a reader cannot learn any of that from the paper. Worse, the value in force
(9.724 ms) is the *smaller* of the two candidates, it enters
`a_t = max(observed drift, 0.009724 s)` which is embedded in every *h_i*, and a
smaller *a_t* means smaller floors and an easier Gate 1. A metrology paper should
not carry an open discrepancy in an uncertainty screen whose unresolved direction
is permissive. Stating that no current claim depends on the superseded value is
not the same as showing that the difference is immaterial.

*Fixable at the desk:* yes — disclose the derivation (corpus size, statistic,
which acceptance generation binds which value) and either reconcile or bound the
effect of choosing 10.818 ms instead.

### W8. The "95/95" label on B_fiducial assumes independence the paper denies elsewhere

*Where:* A.3.6, "it is a '95/95' bound: with at least 95 % confidence it exceeds
at least 95 % of that distribution (the probability that all 59 draws fall below
the 95th percentile is 0.95⁵⁹ ≈ 0.048)."

The arithmetic is right; the premise is not established. The Wilks-style
maximum-of-n tolerance argument requires 59 i.i.d. draws. The 59 pulses come from
one 197 s capture, share one estimated baseline *b* and one robust scale σ, one
thermal trajectory, one anchor, and one instrument state. §3 makes exactly this
objection about a different quantity — "Those are not 30 independent timing
draws" — and then A.3.6 does not make it about the 118 edge excursions. Either
justify independence (e.g. show no trend of excursion against pulse index or
elapsed time, and no onset/offset correlation within a pulse) or drop the 95/95
label to "sample maximum over 59 commanded pulses" and let it stand on that.
Note also that even granting independence, the covered distribution is explicitly
"the distribution of edge excursions the instrument produces *under this
protocol*" — the label never reaches inference, so it cannot help with W1.

*Fixable at the desk:* yes; the 118 values are retained.

### W9. Presentation: three schematics and no measured data; a padded reference list; and prose density that will lose the PC

- **No plotted measured data anywhere.** Figures 1, 2, and 3 are all schematics,
  and all three captions insist on it ("Every value is illustrative"; "no
  measured data"; "No measured data or numeric threshold is encoded by the
  layout"). For a paper whose contribution is an instrument, the absence of a
  single plotted real trace is striking, and it is not caused by the pending
  campaign — the diagnostic captures are retained and re-derive deterministically.
- **Ten of thirty-one references are never cited** in the body: [4], [9], [11],
  [14], [16], [17], [18], [21], [24], [25]. (Confirmed against
  `docs/paper/bibliography-audit-2026-08-27.md`, which records the same finding
  and the decision to leave them in place.) A PC will read that as padding.
- **Density.** §4's three-way disambiguation paragraph ("the attribution-dominance
  sentence—the falsifier—tests that exact per-component linear corner maximum
  against the guarded point-only value; the null-containment sentence tests the
  published corner-widened guarded floor…") is, I believe, correct, and I could
  not follow it without the source. Table 1 is a wall. The artifact field names
  (`corner_widened_guarded_floor_j`, `floor_gate_j`,
  `admissible_set_uncertainty_dominates_point_floor`) inlined into body prose
  serve traceability at heavy cost to readability; they belong in a table
  mapping paper term → artifact field, cited once.
- The title is still a placeholder ("# PLACEHOLDER pending `_v4`").

*Fixable at the desk:* yes, all of it.

### W10. Missing methodological lineage

The clock-anchor estimator is interval-intersection clock synchronisation, and
the B_fiducial argument is a nonparametric tolerance bound. Neither literature is
cited. Candidates, all marked for verification since I am citing from memory and
must not fabricate: Marzullo's interval-intersection agreement algorithm
[VERIFY]; Kopetz's interval-based clock synchronisation [VERIFY]; Cristian's
probabilistic clock reading [VERIFY]; Wilks (1941) on nonparametric tolerance
limits, for the 95/95 claim [VERIFY]; and the bounded-error / set-membership
identification literature (Milanese & Vicino) [VERIFY] for the "keep the whole
consistent set" framing. Locating the estimator in an existing tradition would
*strengthen* the paper — it shows the authors did not invent an idiosyncratic
scheme — and would give A.3.3 a name to hang on.

## 4. Specific requested changes

1. **§1 / §4 — replace the boolean falsifier with a registered ratio and
   threshold.** Quote: "The finding is falsified for a phase if the timing-widened
   bound does not exceed the point-only repeatability bound." Change: register
   `R = (corner-widened component) / (guarded point-only component)` with a
   pre-specified threshold, state the threshold and its justification, and report
   R per cell in Tables 2 and 3. Additionally state, in §4, the algebraic
   condition under which the current predicate is automatically true (when
   `max_i|r_i|` exceeds the Student-t prediction term), so readers can see what
   the boolean does and does not certify.
2. **§3 — delete or replace the zero-width sanity check.** Quote: "Forcing all
   timing-envelope widths to zero flipped the registered dominance predicate from
   true to false, showing that phase-edge placement, rather than the predicate
   itself, produced the widening." A predicate monotone in *h* must flip when
   *h* = 0; this shows nothing. Replace with the ratio (W2) or with a
   permutation/shuffle check that could have failed.
3. **§4 step 3 — handle the shared fiducial term as shared across blocks.**
   Quote: "each independent energy or block difference enters as [x_i−h_i,
   x_i+h_i]. Enumerate all 2^n joint corners." Change: state the shared/local
   decomposition explicitly (your `_common_mode_block_half_width` already does it
   within a block), apply it between blocks, and report the dominance ratio under
   both treatments. If you keep the independent enumeration for gating because it
   is conservative, say so in one sentence and give the finding under the
   common-mode treatment.
4. **§7 / Future Work — move the inserted-gap fiducial into the paper, or state
   why one night of measurement was not spent on it.** Quote: "Nothing in the
   frozen `_v4` campaign tests that transfer." A PC will not accept "the pack is
   frozen" as a scientific reason. Either run the ~10 runs and report the
   residual against the pulse-derived bound, or add an explicit paragraph
   defending the ordering.
5. **§6 — fill the two [PENDING] diagnostic-era numbers in the resolvability
   example.** Quotes: "for this bundle it is [PENDING] (DIAGNOSTIC-ERA VALUE:
   sampling-record interval width…)" and "…median record spacing…". These require
   no measurement; per `docs/paper/results-fill-registry.md` rows DG-071 and
   DG-075 they are already measured (111.8–112.5 ms width; 120.922 ms median
   spacing) and are held only pending a declared statistic. Declare the statistic.
   The paper's single fully worked negative-result example currently has two of
   its three numbers missing.
6. **§6 — state the projected record-overlap count for the p256 prefill arm and
   register a contingency.** Quote: "Prompt processing will use the fixed
   synthetic 256-token prompt with identical token identifiers across model
   tokenizers." Add: projected prefill duration and overlapping-record count for
   both 1.5B and 7B at 256 tokens, derived from retained durations and the
   realised record spacing, and what happens to the Holm family if the 1.5B arm
   returns `not_resolvable_sample_count`.
7. **§2 / §4 — derive the two bracket constants in the text.** Quotes: "A
   difference greater than 10.164835 ms refuses the window" and "9.724 ms". State
   that these are the 99 % and 95 % two-draw prediction pins over a 17-member
   calibration corpus, name the acceptance generations that bind each, and give
   the effect on published floors of using the n = 19 value (0.010818 s) instead.
   Seven significant figures without a derivation is exactly what this paper
   criticises elsewhere.
8. **A.3.6 — justify or retire the 95/95 label.** Quote: "it is a '95/95'
   bound". Add an independence check over the 118 retained excursions (excursion
   vs pulse index; onset vs offset within pulse) or replace the label with
   "sample maximum over the 59 commanded pulses of one capture".
9. **A.3.6 / §2 — publish the distribution of the 118 edge excursions, not only
   their maximum.** Quote: "Two diagnostics are also reported and are not used for
   any claim: the median of the 118 values… and their 95th percentile." Print
   them for the worked capture. Pulse 0's reported onset is ~+16 ms and offset
   ~−11 ms (A.3.5), i.e. the instrument reports the pulse *shorter* than
   commanded in both directions — if that sign pattern holds across the train it
   is a systematic offset, not noise, and the paper should say whether it is
   correctable rather than only bounded.
10. **§2 / §7 — quantify the anchor correction.** Quote: "This corrected
    rate-aware model replaced the false equal-rate assumption, which could move
    every fitted edge in the same direction." Report the change in `B_fiducial`
    from re-deriving retained diagnostic captures under the corrected model
    (§2 already shows one capture reproducing exactly, and B_anchor is 3.8 % of
    B_fiducial there). This both sizes contribution #1 honestly and defends §3's
    diagnostic ratios against the objection that they are artifacts of the
    retired estimator.
11. **§3, Table 1, workload-response row — reconcile with §4's enumeration
    cap.** Quotes: "Evaluate each slope at every joint corner of the authenticated
    energy intervals" with "\(n=40\)", against §4's "Exact enumeration refuses
    above \(n=16\)". 2⁴⁰ corners are not enumerated; the OLS slope is linear in
    the energies so its corner extremum is analytic. Say so in one sentence — as
    written the two passages contradict each other.
12. **§11 — resolve the ten uncited references** ([4], [9], [11], [14], [16],
    [17], [18], [21], [24], [25]): cite them in the body or remove them and
    renumber.
13. **Figures — add at least one panel of measured data.** All three current
    figures are schematics. Add: one real pulse from a retained capture with the
    fitted rectangle and the accepted-region band overlaid; and the
    overlapping-record-count histogram behind "37 of 50". Both come from bytes you
    already hold.
14. **§8 — add the clock-synchronisation and tolerance-bound lineage** (see W10),
    each verified before insertion.
15. **Terminology — collapse the artifact-field names out of body prose** into a
    single term→field table, cited once. Retain traceability, recover readability.

## 5. Questions for the authors

1. In the `_v4` design (n = 10 blocks, g(10) = 1), under what realisable
   combination of residual spread and timing half-width does the registered
   dominance predicate return *false*? Please give the numeric condition. If a
   single outlying run makes it unconditionally true for that cell, is the
   finding falsifiable as registered?
2. Across the ten blocks of one window, is the shared `b_fiducial_s` contribution
   to each block's half-width varied independently in the 2¹⁰ corner enumeration?
   If so, what is the dominance ratio when the shared part is instead moved
   common-mode?
3. What is the projected number of *powermetrics* records overlapping a
   256-token prefill phase for 1.5B and for 7B, and what fraction of members do
   you expect to clear the three-record rule? What is the registered contingency
   if the 1.5B prefill arm is not resolvable?
4. Were the 50 prompt-processing phases behind "37 of 50" all at one prompt
   length, and which? Without that the negative result cannot be positioned
   against the p256 design.
5. Do the 118 edge excursions of a capture show a systematic sign (onset late,
   offset early)? If yes, why is a systematic offset bounded rather than
   corrected?
6. Are the 59 pulses of one capture independent in the sense the 95/95 argument
   requires? What evidence supports that, given they share *b*, σ, anchor, and
   thermal trajectory?
7. What is the numerical effect on published floors of the unreconciled bracket
   screen (9.724 ms in force vs 0.010818 s from the 19-member derivation)? Is the
   direction permissive, as it appears?
8. Over the retained diagnostic captures, how much does `B_fiducial` change when
   re-derived under the corrected rate-aware anchor rather than the retired
   equal-rate model? Does the change preserve the 10.92 / 5.92 / 7.02 ratios?
9. What must happen for FLOOR-BIND-01 to close, and will it close before
   camera-ready? Can any part of the extraction→analysis link be made
   independently checkable before then?
10. §4's `C = F + B` sizing disclosure uses a `B` whose "supplier is not built".
    If `B` is unconstructible before the campaign, on what basis was "approximately
    5 J" used to select 256 tokens, and would the selection change under a
    plausible range of `B`?
11. §7 notes that a "known interval between checking a floor-specification path
    and authorizing it" is exploitable. Is this a TOCTOU window in the claim
    authorisation path, and is it closed?
12. The estimator refuses any record whose whole-second label is not exact, and
    charges a 250 µs affine residual allowance. What happens on a capture that
    spans a leap second or an OS time-discipline slew step, given that NTP is
    required off by admission but is not verifiable by the estimator?

## 6. Score

**Score: 3 (borderline).**

This is a serious, honest, technically careful piece of metrology, and Appendix A
is better than most artifact appendices I read. If the question were "did these
authors do rigorous work," the answer is plainly yes. But three things hold it at
borderline. First, the central quantity — the timing bound that produces every
number in the paper — is transported from a commanded-pulse regime to an
inference regime without a test, and the test the authors themselves specify
costs about ten runs. A metrology paper that declines to validate its own
transport assumption when validation is one night away is asking reviewers to
accept on trust the exact thing it exists to establish. Second, the registered
finding is decided by a predicate that, on inspection of the code, is weak
(≈ 0.26 s_r) and on some cells vacuous, while the timing side of that comparison
is inflated by treating a shared systematic as n independent perturbations — so
the headline result is simultaneously easy to obtain and biased toward being
obtained. Third, the claim-authorising evidence chain is admittedly not
independently re-reducible. None of these is fatal; all three are addressable,
two of them at the desk. But as submitted, the paper's strongest defensible
outputs are the corrected clock model (whose numerical effect appears to be a few
percent of the published bound), the specification itself, and the 37/50
resolvability negative result — which is a real contribution but a modest one for
a full paper.

I want to be clear that the [PENDING] results are *not* what is holding this at
3. The design would be readable and reviewable either way, and the paper is
structured to be honest under both outcomes. What holds it at 3 is that under
*either* outcome, W1–W3 leave the primary finding under-defended.

- **If `_v4` reproduces dominance: 4 (accept)** — conditional on the desk fixes,
  chiefly the ratio-based falsifier (W2), the common-mode treatment (W3), and
  quantifying the anchor correction (W6). Large ratios in the 5–11 range,
  reproduced prospectively under a corrected estimator with printed refusals,
  would be a genuine and useful result for this venue even with the transfer
  assumption standing — provided the paper stops calling a ≈0.26 s_r bar
  "dominance" and starts reporting the number.
- **If `_v4` does not reproduce dominance: 2 (weak reject)** as currently
  structured, rising to 3 with the inserted-gap fiducial added. A prospective
  null on the primary question leaves the corrected clock model, the refusal
  machinery, and the resolvability result — honest, but thin for a full paper,
  and the null itself would be hard to interpret without knowing whether the
  pulse-derived bound transfers at all. If the transfer experiment were in hand,
  a null would become interesting rather than merely disappointing: it would say
  that on this configuration, phase-edge placement is *not* the limiting term,
  which is a genuine, quotable, prospectively-registered negative finding.

## 7. What would make this paper impressive rather than merely sound

### (a) Desk work only: publish the empirical distribution of the 118 per-edge excursions, decomposed into systematic and scatter components

Right now the calibration output is one number — the sample maximum, ~30 ms —
carried through the entire paper as an opaque worst case, and the paper contains
no plotted measured data at all. Everything needed to change that is retained and
re-derives deterministically (§2 demonstrates `rederive_detection_from_artifacts`
reproducing `b_fiducial_s` and the rectangle count exactly).

Do this: for each retained diagnostic capture, plot all 118 widened edge
excursions — onsets and offsets separately — against pulse index and against
commanded gap length; report median, 95th percentile, and maximum; test for a
systematic component. The one data point the paper already prints is suggestive:
pulse 0's onset region sits ~+16 ms and its offset region ~−11 ms, i.e. the
instrument reports the pulse as *shorter than commanded at both ends*. If that
sign structure holds across the train, then a large part of the 30 ms bound is a
correctable calibration offset rather than irreducible edge uncertainty, and
subtracting it could shrink every *h_i* substantially — which would improve every
floor in the paper and change what the demonstration can resolve. If it does not
hold, the worst-case bound is empirically vindicated instead of merely asserted,
and the 95/95 argument (W8) gets the independence evidence it currently lacks.

Either outcome is a win, and the same figure fixes W9's "no measured data"
problem, gives the paper its missing money shot (a real pulse, its fit, and the
accepted-region band drawn to scale), and turns "we bound the edge error" into
"we characterised this instrument's edge response, and here is what it looks
like." That is the difference between a paper that describes an instrument and a
paper that *shows* one. It costs zero measurement nights.

(Second-best desk addition, if a second is possible: the W2/W3 pair — report the
dominance ratio with a registered threshold, under a common-mode treatment of the
shared term. That is a soundness repair rather than an impressiveness upgrade,
which is why it sits in §4 above rather than here, but it is more important than
either.)

### (b) One more measurement week: the inserted-gap fiducial, ranked first by a wide margin

**Rank 1 — inserted-gap fiducial (the authors' own Future Work #1).** ~10 runs,
one night, existing estimator, no new code path. Command a ~500 ms sleep between
prefill end and decode start, fit both edges of the gap with the same pulse
estimator, and compare the residual against the pulse-derived bound.

Why it dominates everything else on the table:

- It converts the paper's *single largest* stated limitation into a measured
  result. Nothing else on the list touches W1.
- It is valuable under **both** `_v4` outcomes, which is rare. If dominance
  reproduces, the transfer test is what makes the headline defensible instead of
  conditional. If dominance does not reproduce, the gap fiducial is what makes
  the null interpretable — it distinguishes "edge placement genuinely is not the
  limiting term here" from "our pulse-derived bound simply does not describe
  inference," which are opposite scientific conclusions that a bare null cannot
  separate.
- It is the cheapest experiment on the list per unit of claim it protects: ten
  runs against a two-to-four-hour window, versus a full ladder campaign.
- It generalises. "Insert a commanded fiducial into the real workload and check
  your calibration against it" is a transferable technique for anyone doing
  phase-resolved counter measurement, on any counter. It would be the most
  quotable methodological sentence in the paper — arguably a stronger
  contribution than the dominance finding itself.
- It has a real chance of *failing*, which is what makes it worth doing. If the
  gap residual exceeds the pulse-derived bound, the paper has found something
  important about software counters that nobody has reported, and the honest
  reporting machinery is already built to say so.

One design note if you run it: the inserted gap changes the thermal and
memory-residency state across the boundary, so command the gap on a subset of
runs that are otherwise identical to admitted members, and pre-register whether
the comparison is one-sided (residual ≤ bound) or two-sided.

**Rank 2 — a targeted two-point prompt-length check (128 vs 256 prefill on both
models), not a full `_v5` ladder.** ~1 night. This directly tests the
extrapolation that W5 flags — "none of the forty retained contrast configurations
uses more than 128 prompt tokens" — and simultaneously measures the realised
record-overlap count at 256 tokens, retiring the resolvability risk to the
demonstration. It is cheap insurance on a design decision the paper currently
cannot reconstruct.

**Rank 3 — the `_v5` model ladder.** More model sizes on the same protocol adds
breadth, and breadth is what a scaling-flavoured reader wants. But every point on
the ladder inherits the untested transfer assumption, so it multiplies
conditional results rather than removing the condition; and the paper explicitly
disclaims a scaling law ("The fixed 7B-versus-1.5B comparison demonstrates the
resulting decision behaviour; it is not a model-size scaling law"), so the ladder
does not serve the stated contribution. Per measurement night it is the weakest
of the three.

**Rank 4 — an external wall meter cross-check.** Valuable eventually, and §8
concedes the closest rival [20] has one while "JouleWise lacks that independent
cross-check." But the paper's own argument is that an external meter cannot
adjudicate *phase attribution* — it validates gain, not time. It fixes a
different weakness than the one that is limiting this paper, and it costs
hardware setup rather than a night.
