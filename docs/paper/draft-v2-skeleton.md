<!--
SUCCESSOR SKELETON, NOT A RESULTS DRAFT.

Build notes replace every result-sensitive section. Stable text is carried
where survival-map.md says KEEP VERBATIM; text classified KEEP WITH NAMED EDITS
is also carried, with only the ledger's named replacements applied. Neither
disposition licenses mechanical generation of result prose.

Fill notation: [FILL:<registry-row-id>] names one row in
docs/paper/results-fill-registry.md. Conventional row identifiers include
DS-25 and V5-ID-001. Where the exact-token table gives a row no conventional
identifier, its exact token without the outer square brackets identifies it;
for example, R_1p7B_decode_abs. STOP_FILL means print the registered omission
or refusal, never a guessed value.
-->

# JouleWise — Measuring Phase Energy in Large-Language-Model (LLM) Inference on Apple Silicon

<!-- BUILD NOTE — optional subtitle: add “Attribution-limited” only under
Outcome A below. A missing, refused, zero-denominator, or below-two required
ratio forbids the subtitle. -->

## Abstract

<!-- BUILD AFTER DATA, IN THIS ORDER:
1. Build the physical problem: uncertain placement of the boundary between
   prompt processing and token generation can move energy between phases
   without changing request energy.
2. State the in-window pulse calibration and its untested transfer to sustained
   inference.
3. Define in words the point-only and boundary-moved component bounds; then
   name R and R_cm.
4. Insert exactly one canonical outcome sentence from “Outcome sentence
   forms” in Section 4.
5. Report the fixed Qwen3-8B-versus-Qwen3-1.7B demonstration as an application
   of the rule, never as scaling. Fill only authenticated rows. The stopped
   placements read:
   [FILL:DS-28] — “The decode sizing sum and signed clearance
   are omitted: the claim-side bound and one-cell/two-quantity rendering are
   unresolved (registry row DS-28).”
   [FILL:DS-29] — “The decode claim-side bound
   is omitted: no producing artifact field is registered, and
   `deterministic_bounds.total` is not a substitute (registry row DS-29).”
   [FILL:DS-30] — “The decode floor-gate outcome is omitted: no exact
   conservative rendering token is registered (registry row DS-30).”
   [FILL:DS-31] — “The decode direction-gate outcome is omitted: no exact
   conservative rendering token is registered (registry row DS-31).”
   [FILL:DS-32] — “The decode verdict is omitted: no professor-facing
   conservative rendering token is registered (registry row DS-32).”
   [FILL:DS-33] — “The selected `_v5` prefill claim floor is omitted:
   `[PREFILL_LENGTH]` is unresolved until G2-a and no professor-facing prefill
   token is registered (registry row DS-33).”
   [FILL:PG-01] — “The selected
   `_v5` prefill contrast estimate is omitted: `[PREFILL_LENGTH]` is unresolved
   until G2-a and no authenticated estimate token is registered (registry row
   PG-01).”
   [FILL:PG-02] — “The selected `_v5` prefill interval is omitted:
   `[PREFILL_LENGTH]` is unresolved until G2-a and no authenticated lower or
   upper endpoint tokens are registered (registry row PG-02).”
   [FILL:PG-04] —
   “The selected `_v5` prefill sizing sum and signed clearance are omitted: the
   claim-bound token family and rendering contract are not registered (registry
   row PG-04).”
   [FILL:PG-05] — “The selected `_v5` prefill claim-side bound is
   omitted: no named producing field or rendering token is registered (registry
   row PG-05).”
   [FILL:PG-06] — “The selected `_v5` prefill floor-gate outcome
   is omitted: no conservative rendering token is registered (registry row
   PG-06).”
   [FILL:PG-07] — “The selected `_v5` prefill direction-gate outcome
   is omitted: no conservative rendering token is registered (registry row
   PG-07).”
   [FILL:PG-08] — “The selected `_v5` prefill verdict is omitted: no
   authenticated professor-facing verdict token is registered (registry row
   PG-08).”
6. State the retained negative: [FILL:DG-067] of [FILL:DG-068] short-prompt
   phases failed the three-overlap rule; [FILL:DG-069] passed.
7. End with the named-machine, named-software, named-counter boundary and the
   transfer-fiducial condition. Do not draft this prose before those outcomes
   issue. -->

## 1. Introduction

<!-- BUILD AFTER DATA, IN THIS ORDER:
1. Power is averaged over records with start and end times; moving a software
   phase edge across a record moves integrated energy between phases.
2. Prompt processing reads the prompt through the first output token; token
   generation emits later output tokens. Introduce these plain phrases before
   the shorthand “prefill” and “decode”.
3. Explain why repeats reduce ordinary run-to-run spread but cannot remove a
   boundary displacement shared by the runs.
4. Introduce the corrected rate-aware clock mapping and in-window pulse
   calibration.
5. Define a cell as runs sharing phase, workload, model, hardware, software,
   and counter boundary; define its resolution bound as the largest false
   difference admitted by the registered calculation.
6. Ask RQ-ATTRIBUTION-DOMINANCE only after Section 4's inputs have been
   summarized in plain words: did allowed edge movement at least double every
   component's point-only bound, both with independently moved edges and with
   the timing error shared inside each four-run comparison?
7. Introduce the fixed identities [FILL:V5-ID-001] and [FILL:V5-ID-002] and the
   workload pins [FILL:V5-WL-001]–[FILL:V5-WL-004]. The stopped final pin reads
   [FILL:V5-WL-005] — “The selected prefill prompt pin is omitted: its
   G2-a-bound `joulewise.prefill_prompt_pin.v2` record has not issued (registry
   row V5-WL-005).” Call the pair a demonstration of the decision rule, not a
   scaling experiment.
8. State the short-prefill question and scope. Do not insert result prose here
   until Sections 3 and 6 are filled. -->

## 2. In-window calibration method

Prompt processing (*prefill*) reads the prompt through the first output token; token generation (*decode*) emits later output tokens. A phase boundary is the runtime-recorded time separating those phases. macOS's built-in power sampler, *powermetrics*, emits one record containing the CPU, GPU, and neural-engine average power over one shared start-to-end interval; JouleWise assigns that sampling record to a phase using the boundary and multiplies each channel's average power by the part of the interval in that phase. A phase boundary is therefore a separate measurement problem from repeatability. If a boundary is placed a few tens of milliseconds late while power falls by tens of watts, power multiplied by misplaced time assigns about a joule to the wrong phase. The request total does not change: energy removed from one phase is added to the other. Repetition can reduce random scatter, but it cannot remove this systematic reassignment.

Figure 1 shows interval-average power around the recorded boundary between prompt processing and token generation, with the allowed boundary positions marked as a band. The hatched area is the energy reassigned between phases when the boundary moves across that band; the request total does not change.

![Figure 1. Boundary-attribution mechanism.](figures/fig1_boundary_attribution.svg)

*Figure 1. Boundary-attribution schematic. Every value is illustrative, including both axes, the sampler interval, timing band, power step, and approximately one-joule product. The power-versus-time axes and pale grid frame gray interval-average rectangles and a dashed idealized-power trace; lower bars name prefill and decode. A black vertical line marks the runtime-recorded boundary, a blue band its calibrated timing bound, and a hatched sliver the energy reassigned by a boundary shift. Horizontal and vertical double-headed arrows name the sampler interval and power step; a blue callout arrow points to the sliver. The notes and legend explain the high- and low-power regimes, the blended boundary sample, the unchanged request total, and every mark.*

### Bracketed pulse-train algorithm

Immediately before and after each science window—one uninterrupted measurement session—JouleWise records a calibration under the same declared machine state. Its recorded SHA-256 values, which identify exact file bytes, must match the fixed record; its timestamps must place it before the first or after the last science run and no more than 24 hours from the window's far end. After three warm-up pulses, which are discarded, it commands 59 one-second GPU matrix-multiplication pulses on preallocated \(4096\times4096\) 16-bit floating-point matrices. A fixed base-two varied-gap schedule—gaps stepping through powers of two—prevents the pulse edges from repeatedly lining up with the requested 100-ms sampler cadence. Five seconds of quiet trace (no commanded pulse) are requested on both sides of the train, of which at least 4.5 s must be present.

For each commanded pulse, the detector estimates resting GPU power from samples outside the fixed time margin around every pulse and pulse height from samples wholly inside its flat high-power portion, called the plateau. It predicts each reported interval average from the fraction of that interval covered by a shifted rectangular pulse, then scores the difference between predicted and observed power with a rule that limits the influence of one large discrepancy while moving the onset and offset separately. After finding the best pair, it encloses every pair close enough to that fit: a rectangle is rejected only when a mathematical lower bound proves that none of it can pass, and every surviving rectangle is split to a fixed resolution. The four outer edge values are widened for uncertainty in the two command timestamps. A capture is refused unless all 59 pulses pass the signal, fit, range, trace-coverage, and completeness checks; no uncommanded plateau appears; and the shared search-work limits remain unexhausted. The accepted capture bound is the largest allowed edge displacement among all pulses plus the trace's clock-anchor bound, the uncertainty in placing the trace on wall-clock time, built next.

The clock anchor uses five wall-clock readings, each bracketed by readings from a monotonic clock—a counter that advances but is never corrected to civil time—together with every whole-second label embedded in the native power records. It retains the complete set of straight-line clock mappings whose rate, offset, first-record endpoint, stamp brackets, native labels, and launch-to-first-parse ordering agree. The method permits the two clocks to run at slightly different fixed rates and charges the full allowed departure of a native label from that line. It refuses missing or malformed inputs, an empty or unbounded set, inadequate capture span, implausible clock rate, active automatic network-time correction, or a bound outside the accepted range. Otherwise it finds the earliest and latest allowed first-record endpoint and adds four separately named allowances. This corrected rate-aware model replaced the false equal-rate assumption, which could move every fitted edge in the same direction.

Finally, the pre-window and post-window capture bounds form a bracket. The calibration policy derives two constants from its retained 17-capture corpus. Student-\(t\) is a small-sample bell curve whose 99% quantile—the two-sided 99% point, written \(t_{0.995,16}\) because it leaves 0.5% in each tail with 16 degrees of freedom, and larger than the normal curve's because the spread is estimated from only 17 captures—sets the maximum permitted pre/post difference. For \(n=17\) per-capture bounds, the sample standard deviation (the \(n-1\) formula of Section 4) is \(s_b = 2.460856\) ms (unrounded, \(2.460856207694636\) ms) and \(t_{0.995,16}=2.92078162242509999197\); the two-draw rule—two fresh capture bounds are drawn, and the spread of their difference is \(\sqrt{2}\) times one capture's spread—so \(t_{0.995,16}\times s_b\times\sqrt{2}\) records \(10.164834757777545\) ms, printed as the \(10.164835\)-ms maximum permitted pre/post difference. The separately retained **minimum allowance** starts from the corpus range, \(9.723589288793850\) ms, rounded to the nearest microsecond, with an exact tie going to the even digit (`ROUND_HALF_EVEN`), giving \(9.724\) ms; Appendix A.3.8 prints the 17 bounds from the retained calibration acceptance file `configs/calibration/calibration_acceptance_d079_v2_n17_r3.json` (registry source S17). The minimum prevents two numerically matching captures from erasing the finite change allowance fixed from that corpus. A larger difference refuses the window. Appendix A.3.6 calls one capture's pulse-plus-anchor bound \(B_{\mathrm{fiducial}}\). The window's distinct **operative timing bound** \(b\) is the larger capture bound plus \(\max(|B_{\mathrm{post}}-B_{\mathrm{pre}}|,9.724\ \mathrm{ms})\), added once. For example, a 25-ms pre-window bound and a 29-ms post-window bound differ by 4 ms, pass the 10.164835-ms limit, and give \(b=29+\max(4,9.724)=38.724\) ms. If the post-window calibration widens a bound already used, the affected phase energies are recomputed with the wider bound or refused. Appendix A.3 formally defines the complete sets of pulse-edge positions and clock mappings that satisfy every fixed constraint, along with objectives, ranges, and refusal conditions.

Commanded GPU pulses calibrate edge placement, but applying that bound to sustained mixed inference is an assumption. The before-and-after bracket tests for change across the measurement window; it does not test whether the pulse-derived bound applies to inference.

Figure 2 orders the before-and-after pulse calibrations, entry check, reference runs, and science blocks within one measurement window. A **stage** is one declared group of runs measured back-to-back inside that window. Each science block uses A/B/B/A order—condition A, condition B, condition B, condition A—and names its four **members**, meaning its four individual runs, \(A_1,B_1,B_2,A_2\) in that order. Its block difference is \((B_1+B_2-A_1-A_2)/2\); a positive value means condition B used more energy than condition A. Matching the average run time of the two A members to that of the two B members cancels steady linear drift. Curvature remains covered by a separately measured **whole-window allowance**: one joule amount for each **energy family**, a group reduced under one energy definition such as gross energy or idle-subtracted energy, later added once to its component bound, equal to the larger of the **reference-trajectory excursion**—the spread among the mean energies of the opening, midpoint, and closing reference runs (largest minus smallest)—and that family's **issued repeatability bound**—a repeatability bound on reference-run energy issued from an earlier retained window, not re-estimated in this one.

![Figure 2. One measurement window and the drift-cancelling A/B/B/A order.](figures/fig2_window_timeline.svg)

*Figure 2. Schematic structure of one measurement window. The upper session-time arrow orders the pre-calibration, admission gate, three opening references, two groups of A/B/B/A science stages around one midpoint reference, three closing references, and post-calibration. The blue spanning bracket joins the two pulse trains; the lower inset's axes, dashed drift line, four A/B/B/A circles, common-time line, and averaging brackets show why steady drift cancels while curvature still requires the measured whole-window allowance defined above. Stage widths are not to scale, and no measured value is shown.*

### One diagnostic reconstruction

The following table and arithmetic reconstruct one retained diagnostic capture from raw clock readings through its maximal pulse. Wall stamps use seconds since 1970; monotonic stamps use the machine's never-adjusted counter. The protocol offsets use the commanded pulse schedule's own origin at its first protocol pulse. Three warm-up pulses occur before that origin, and sampling began earlier still, so those offsets are neither times since sampling began nor observed edge times. Each onset or offset lag uses its matching commanded edge as zero and is observed edge minus commanded edge; bounds are elapsed durations rather than positions on either clock.

| Stamp \(s\) | \(W_s\) (s) | \(M_s^-\) (s) | \(M_s^+\) (s) | \(R_s\) (s) |
|---|---|---|---|---|
| `pre_spawn` | 1784757335.502742 | 458736.4081875 | 458736.408188666 | 0.0000010000000000000002 |
| `first_parse` | 1784757336.604396 | 458737.509839458 | 458737.509840291 | 0.0000010000000000000002 |
| `sampling_started` | 1784757337.0900722 | 458737.995513416 | 458737.995514666 | 0.0000010000000000000002 |
| `sampling_stopped` | 1784757533.877846 | 458934.782846541 | 458934.782848041 | 0.0000010000000000000002 |
| `post_parse` | 1784757533.8891652 | 458934.794166 | 458934.7941665 | 0.0000010000000000000002 |

*The rows above are the five paired clock readings of one retained diagnostic capture. Wall values are seconds since 1970; monotonic values are seconds on the machine's never-adjusted counter. \(R_s\) is the larger of the two resolutions recorded with the stamp — the wall clock's \(1.0000000000000002\times10^{-6}\) s against the monotonic clock's \(4.166666666666666\times10^{-8}\) s — so the wall figure governs every row here. The two monotonic readings bracket each wall reading, which is what makes the pair usable: the wall value is known to have been taken somewhere inside that bracket.*
<!-- evidence: runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/instrument_evidence.json -> clock_anchor.clock_stamps; row order is joulewise/uncertainty_evidence.py STAMP_ORDER; R_s composition is max(wall_resolution_s, monotonic_resolution_s) per the same module -->
<!-- replay fence: scripts/check_paper_replay_fence.py is the mechanical re-derivation check for this table — it reads the five stamp rows back out of the retained evidence file in solver order and requires each printed value to be the same double, failing closed if a row is dropped or the caption is reworded. -->

**Worked current-capture arithmetic.** One retained current-estimator derivation reports all \(59\) pulses detected, \(122{,}859\) evaluated rectangles, a local clock-anchor bound of \(0.0011349971959968978\) s, and a final capture bound of \(0.030067931757111657\) s. Therefore the largest pulse residual before the anchor term is \(0.030067931757111657-0.0011349971959968978=0.0289329345611147592\) s. Re-running the detector over that capture's retained raw power trace and event log, under the current anchor method, reproduces both the capture bound and the evaluated-rectangle count exactly, and identifies the pulse attaining the maximum: the tenth commanded pulse of the capture, scheduled to switch on \(26.625\) s and off \(27.625\) s measured from the origin of the commanded pulse schedule, which is where the schedule places its first protocol pulse rather than an observed onset. Its two commands were stamped at \(1784757381.2856488\) s and \(1784757382.293089\) s of wall time, expressed as seconds since 1970. The fit leaves its onset lag anywhere in \([0.02544938965763524,\,0.02893293456111476]\) s and its offset lag anywhere in \([-0.008607394549133255,\,-0.005308621075866744]\) s, about a best-fit pair of \(+0.027\) s and \(-0.007\) s. The retained residual bound for the pulse is the largest absolute value those four endpoints allow — \(0.02893293456111476\) s, the upper end of the onset interval — and adding the local clock-anchor bound to it returns the capture bound quoted above. Every value in this worked example is diagnostic instrument evidence; none of it supports a claim.
<!-- evidence: runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/{events.jsonl,instrument_evidence.json}; commanded edges from events.jsonl pulse_command_on/off #10 metadata.clock_stamp.epoch_s (planned offsets 26.625 s / 27.625 s). The v3-anchored fit rows are re-derived deterministically by joulewise.powermetrics_fiducial.rederive_detection_from_artifacts over the retained raw plist + events.jsonl, reproducing b_fiducial_s = 0.030067931757111657 and projection_evaluated_cell_count = 122859 exactly; the byte-retained pulses[] in this 2026-07-22 file are v2-anchor-era, while fresh _v5 captures byte-retain v3. -->
<!-- evidence: docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json -->
<!-- replay fence: scripts/check_paper_replay_fence.py is the mechanical re-derivation check for this paragraph — it re-runs the anchor and the 59 pulse fits from the capture's primary bytes and requires every literal above to be the same double it re-derives (stored rows and the stored bound are never inputs). -->

## 3. Instrument characterization

<!-- BUILD FRESH:
1. State each characterization question in physical words.
2. For each row, state the calculation, fixed threshold, independent unit,
   minimum count, and exact refusal consequence.
3. Explain the 40-point slope limit analytically: because an ordinary
   least-squares slope is a fixed weighted sum of energies, choose each lower
   or upper endpoint by the sign of its weight; this requires two endpoint
   vectors, not 2^40 enumeration. Contrast that linear calculation with the
   nonlinear mean-and-standard-deviation corner calculation, which refuses
   above 16 observations.
4. State that five identical-condition blocks test only whether those five
   intervals fit inside an earlier comparator; they do not establish a
   population-coverage percentage.
5. Fill the surviving characterization rows only from an issued authenticated
   report. Until then, [FILL:DS-02] — “The phase-consistency characterization
   result is omitted: its named supplier is an unissued authenticated report
   (registry row DS-02).” [FILL:DS-03] — “The workload-response characterization
   result is omitted: its named supplier is an unissued authenticated report
   (registry row DS-03).” [FILL:DS-05] — “The phase-accounting characterization
   result is omitted: its named supplier is an unissued authenticated report
   (registry row DS-05).” [FILL:DS-06] — “The drift-and-recovery
   characterization result is omitted: its named supplier is an unissued
   authenticated report (registry row DS-06).” DS-04 and DS-07 are retired
   future-work rows; DS-01 is the separate phase-cell hold. -->

### Pilot observations under the retired calculation

<!-- BUILD FRESH, IN THIS ORDER:
1. Label every number here “pilot evidence under the retired calculation, not
   a current instrument property or campaign result.”
2. Point-only component bounds: [FILL:DG-044] [FILL:DG-045] [FILL:DG-046].
3. Full corner-re-evaluated component bounds: [FILL:DG-047]
   [FILL:DG-048] [FILL:DG-049].
4. Their independent-edge ratios: [FILL:DG-050] [FILL:DG-051]
   [FILL:DG-052].
5. Timing range and basis: [FILL:DG-053]–[FILL:DG-056].
6. Corrected-anchor sensitivity, if issued: [FILL:DG-059]–[FILL:DG-066].
7. If the older code-generated “attribution-limited” label is mentioned, say
   that positive interval width could trigger it and that it does not select
   this paper's result. -->

## 4. How the method bounds a false phase-energy difference

<!-- BUILD FRESH AROUND THE METHODS PASSAGE BELOW. Before it, define a cell and
show one record-clipping example in joules. After it, build the guarded
published component floors, cell maximum, Holm correction, and two directional
claim gates. Do not move g(n) or a whole-window allowance into either ratio. -->

To clip a record is to keep only the part of its time interval inside the
phase, then multiply that duration by the record's average power. For example,
a 30-W record from 1.000 to 1.100 s cut at a phase boundary of 1.040 s gives
prompt processing \(30\times0.040=1.20\) J and token generation
\(30\times0.060=1.80\) J. Moving the permitted boundary to 1.050 s would
instead give 1.50 J to each phase. This 0.30-J movement is the physical reason
to calculate a bound on a false phase-energy difference rather than treating
the recorded split as exact.

### Comparing the boundary-moved and point-only bounds

The forcing problem is that any positive boundary interval can make a
boundary-moved bound exceed a point-only bound, so mere exceedance cannot show
that boundary placement is the limiting uncertainty. The comparison therefore
asks for a fixed twofold increase in the complete bound, not just a positive
increase in one timing term.

A cell groups runs that use the same phase, workload, model, hardware,
software, and processor-power definition. It has two false-difference
components. The **absolute component** measures spread among repeated runs of
one model. The **comparative component** measures differences from four-run
blocks executed in A, B, B, A order. If the four phase energies in one block
are \(A_1,B_1,B_2,A_2\), the block difference is

\[
\delta=(B_1+B_2-A_1-A_2)/2.
\]

A positive difference means condition B used more phase energy than condition
A. The order gives the two A runs and the two B runs the same average position
in time, which cancels steady linear drift; curved change remains covered by a
separate whole-window allowance.

For either component, first calculate a **point-only unguarded bound**. An
**admitted energy** is an energy from a run that passed the Section 5 entry
checks and may therefore bear a claim. “Point only” means using each admitted
energy at its recorded value. “Unguarded” means before the later small-sample
multiplier and before the whole-window allowance. Here \(n\), the number of
**independent units**, counts one repeated run for the absolute component and
one four-run A/B/B/A block for the comparative component.
For repeated energies \(E_i\), calculate their mean \(\bar E\), residuals
\(r_i=E_i-\bar E\), and residual mean \(\bar r\). Calculate the sample
standard deviation as

\[
s_r=\sqrt{\frac{\sum_i(r_i-\bar r)^2}{n-1}}.
\]

Let \(t_{.975,n-1}\) be the value below which 97.5% of a Student-\(t\)
distribution with \(n-1\) degrees of freedom lies; this distribution widens
the prediction when only a few independent units exist. Then take

\[
U_{\mathrm{abs,point}}=
\max\!\left(\max_i|r_i|,
t_{.975,n-1}s_r\sqrt{1+1/n}\right).
\]

The first term preserves the largest displacement already observed. The second
is the two-sided 95% prediction amount for one further observation. For block
differences \(\delta_i\), calculate their mean \(\bar\delta\) and sample standard
deviation

\[
s_\delta=\sqrt{\frac{\sum_i(\delta_i-\bar\delta)^2}{n-1}},
\]

then take

\[
U_{\mathrm{cmp,point}}=
\max\!\left(\max_i|\delta_i|,
|\bar\delta|+t_{.975,n-1}s_\delta\sqrt{1+1/n}\right).
\]

For a worked point-only example, take five repeated energies 8, 9, 10, 11,
and 12 J. Their mean is 10 J, their residuals are −2, −1, 0, 1, and 2 J,
and their sample standard deviation is \(\sqrt{10/4}=1.581139\) J. With
\(t_{.975,4}=2.776445\), the prediction amount is
\(2.776445\times1.581139\times\sqrt{1.2}=4.808944\) J, larger than the
2 J observed residual, so \(U_{\mathrm{abs,point}}=4.808944\) J. If five
block differences are 0, 1, 2, 3, and 4 J, their mean is 2 J and their sample
standard deviation is again 1.581139 J; therefore
\(U_{\mathrm{cmp,point}}=\max(4,2+4.808944)=6.808944\) J. These values
demonstrate the formulas and are not campaign evidence.

Each admitted energy also has a lower and upper value obtained by moving its
phase edges through every position allowed by the session calibration. To
calculate the **independent-edge corner bound**, choose either the lower or
upper value for every admitted energy, enumerate every joint choice, and at
each choice recalculate the complete applicable formula above—including its
mean, largest magnitude, and sample standard deviation. Retain the largest
result. Call it \(U_{\mathrm{abs,corner}}\) or
\(U_{\mathrm{cmp,corner}}\). Exact enumeration refuses above 16 independent
units; it never substitutes an approximation.

The independent-edge ratio is

\[
R=\frac{U_{\mathrm{corner}}}{U_{\mathrm{point}}}.
\]

The numerator and denominator are therefore the same complete unguarded
formula, once after allowed edge movement and once at the recorded points.
Neither is a timing term alone or a value after the multiplier or
whole-window allowance is added. In this paper, allowed boundary movement
**dominates** a component only when \(R\ge2\): it adds at least one entire
point-only bound. Exact equality at \(R=2\) passes. A threshold merely above 1
would let any positive interval width do the decisive work. If
\(U_{\mathrm{point}}=0\), the program refuses with the fixed reason name
`dominance_ratio_zero_denominator`; it does not print infinity.

Here, **authenticated** means that the evidence, plan, and close-out records
carry the expected SHA-256 fingerprints and their named inputs agree. A
missing fingerprint, a mismatch, or a required input that cannot be checked is
unauthenticated and cannot select a ratio outcome.

The retained pilot arithmetic illustrates the quotient without supplying a
campaign result. Under the retired guarded calculation, the same multiplier
was applied to each corner value and its matching point value, so it cancels
from their quotient. The three corner/point pairs are
\(3.153/0.2888=10.92\), \(2.922/0.4934=5.92\), and
\(2.184/0.3113=7.02\) after rounding fixed before collection in a plan whose
SHA-256 fingerprint identifies its exact bytes (the plan's **registered
rounding**)
([FILL:DG-044]–[FILL:DG-052]). They show the numerical effect of recalculating
the complete formula at the worst joint endpoint choice, but they are pilot
evidence and cannot fill a current campaign ratio.

Independent movement is deliberately conservative, but some timing error is
shared by all four members of one A/B/B/A block. Rebuild that physical split
before combining the two movements into one width. For a block \(j\), start
with its admitted point difference \(\delta_j\). Reintegrate the four retained
power traces after moving all four phase starts by the same shift while holding
their ends fixed. The shift candidates are \(-b,0,+b\), where \(b\) is the
window's authenticated operative timing bound from Section 2, plus every shift
within \([-b,b]\) that makes a retained power record's start or end coincide
with one of the four phase starts. The resulting block differences form the
onset set \(O_j\). Repeat for the four phase ends, using the analogous
record-edge coincidences and holding starts fixed, to form the offset set
\(P_j\). Both sets include the zero-shift value \(z_j\).

Define the shared lower and upper excursions

\[
d_j^-=(\min O_j-z_j)+(\min P_j-z_j),\qquad
d_j^+=(\max O_j-z_j)+(\max P_j-z_j),
\]

and let

\[
q_j=\max(|d_j^-|,|d_j^+|)+|z_j-\delta_j|.
\]

Thus \(q_j\) is the farther common start-plus-end movement, plus any difference
between recomputing energy at zero shift and the admitted block value. The
implementation prevents a printed interval from rounding inward. In
**binary64**, the usual 64-bit floating-point format, `ulp(1.0)` is the gap
between 1 and the next larger representable number. The **member-envelope
integral sum** is
\(\sum_{m\in\{A_1,B_1,B_2,A_2\}}|c_m|\int_{\mathrm{start}_m-b}^{\mathrm{end}_m+b}P_m(t)\,dt\),
where \(c_m=(-1/2,+1/2,+1/2,-1/2)\) and \(P_m(t)\) is member \(m\)'s
interval-average-power trace, held at each record's reported average across
that record's time interval. This nonnegative joule sum supplies a scale
large enough to cover all four member integrals before their signed contrast
is formed. It sets
\(M=\max(1,|\delta_j|,|z_j|,\max_{o\in O_j}|o|,\max_{p\in P_j}|p|,\text{member-envelope integral sum})\), takes
\(p=64\,[\operatorname{ulp}(1.0)/2]M\), subtracts \(p\) from the lower
extreme and adds \(p\) to the upper extreme, and then moves each resulting
endpoint four representable binary64 values outward. The factor 64 pays for
the finite set of floating-point operations before the enclosure is printed.
For the first two-block fixture below, (M=103.06152807459057) J gives

\[
p=64(2^{-53})(103.06152807459057)=7.322962010973595\times10^{-13}\ \mathrm{J},
\]

before the four outward binary64 steps. The amount is small, but its direction
is fixed: the printed enclosure cannot become narrower through rounding.

Next set the shared calibration-pulse timing movement to zero and, for each of
the four block members, recompute phase energy from the same power trace while
moving only that member's remaining local clock and edge uncertainty. Let the
largest absolute energy change for member \(m\) be
\(r_{jm}\). The local half-width of the block difference is

\[
\ell_j=(r_{j1}+r_{j2}+r_{j3}+r_{j4})/2.
\]

Enumerate one shared sign \(s\in\{-1,+1\}\) for the entire set of blocks and
one independent local sign \(e_j\in\{-1,+1\}\) for each block. At every one of
the \(2\times2^n\) choices, replace each point difference with

\[
\delta'_j=\delta_j+s q_j+e_j\ell_j,
\]

recalculate the complete comparative unguarded formula, and retain the largest
value \(U_{\mathrm{cmp,shared}}\). Divide that complete shared/local replay
bound by the point-only comparative bound. This quotient is the comparative
**shared-error ratio** \(R_{cm}\):

\[
R_{cm}=\frac{U_{\mathrm{cmp,shared}}}
             {U_{\mathrm{cmp,point}}}.
\]

The same zero-denominator refusal applies. A comparative \(R_{cm}<2\)
withdraws the boundary-doubling sentence even when \(R\ge2\). An absolute
\(R_{cm}\) is `not_applicable`, not missing: the absolute formula first
subtracts the cell mean, so a uniform shared shift cancels from every residual.

A retained two-block fixture makes the replay checkable without becoming
campaign evidence. The Student-\(t\) critical used by the two-block interval is
\(t_{0.975,1}=12.706\), the fixed-table value `_T_CRITICAL_95[1] = 12.706` in
`joulewise/aggregate.py:41–42`, returned by `student_t_critical_95` and used by
`joulewise/detection_floor.py:696`; the artifact records
`t_critical_source: joulewise.aggregate.student_t_critical_95.v1`.
Block 1 has
\(\delta_1=z_1=0.2146256513\) J, onset values from 0.1098764207 to
0.2243993676 J, and offset values from 0.0576055478 to 0.3349382543 J. Hence
\(d_1^-=-0.2617693342\) J, \(d_1^+=0.1300863192\) J, and
\(q_1=0.2617693342\) J. Its four local residual half-widths are
0.0015589205, 0.0337198644, 0.0491358083, and 0.0127439131 J, so
\(\ell_1=0.0485792531\) J. Block 2 has
\(\delta_2=0.4072547482\) J and \(z_2=0.4072547482\) J. Its
\(q_2=0.6153099135\) J and \(\ell_2=0.1356776459\) J are authenticated fixture
inputs from `tests/fixtures/fcm_r4_real_blocks/measured_pair.json`. Enumerating both
shared signs and all four local-sign pairs yields
\(U_{\mathrm{cmp,point}}=2.4305766103\) J and
\(U_{\mathrm{cmp,shared}}=8.8304376431\) J, so
\(R_{cm}=3.6330628732\), which passes 2. A replay from the printed
10-decimal operands agrees to nine significant figures. The fixture demonstrates
the arithmetic only.

### Adding publication safeguards after the ratio

The ratio is calculated before the safeguards used to publish the final
**resolution bound**, the largest false phase-energy difference this cell
admits. The final resolution bound is called the **cell floor** in the
artifacts. For \(n\ge5\) independent units, first apply the fixed
small-sample multiplier

\[
g(n)=\max\!\left(1,\sqrt{9/(n-1)}\right).
\]

The 9 is \(10-1\): the multiplier compares the residual degrees of freedom
at the 10-unit design point with the \(n-1\) residual degrees of freedom
actually observed. It is an operational widening rule, not a population-
coverage or confidence guarantee. For example, five units give \(g(5)=1.5\),
while ten give \(g(10)=1\). Below five units the calculation deliberately
returns no multiplier and no publishable component; its unguarded value is
diagnostic only.

Next add that component's whole-window allowance \(A_k\) once. For a named
energy family \(k\), take the means of its opening, midpoint when present, and
closing reference runs. The **reference-trajectory excursion** is the largest
of those means minus the smallest. The **issued repeatability bound** is the
positive endpoint bound for that family from an earlier retained calculation,
not a number re-estimated from this window. Its artifact field is
`replicated_endpoint_bound_j` when the reference protocol has a midpoint and
`single_member_endpoint_bound_j` otherwise. The forcing problem is a rise and
fall: A/B/B/A order cancels a steady straight-line change but not a path that
turns between references. Then \(A_k\) is the larger of that independent bound
and the observed excursion. Thus reference means 10.0, 10.6, and 10.2 J have
an excursion of \(10.6-10.0=0.6\) J; with an issued 0.4-J repeatability bound,
\(A_k=\max(0.6,0.4)=0.6\) J. It is a joule quantity and is distinct from the
timing allowance already embedded in each energy interval. The published
components and cell floor are

\[
F_{\mathrm{abs}}=g(n)U_{\mathrm{abs,corner}}+A_{\mathrm{abs}},\qquad
F_{\mathrm{cmp}}=g(n)U_{\mathrm{cmp,corner}}+A_{\mathrm{cmp}},
\]

\[
F_{\mathrm{cell}}=\max(F_{\mathrm{abs}},F_{\mathrm{cmp}}).
\]

The maximum is used because either component can manufacture the apparent
difference the claim must clear; summing them would charge both competing
worst cases at once. In a synthetic regression example, five units give
unguarded corner values 1.6656 J absolute and 1.7656 J comparative. With
\(g(5)=1.5\) and a 0.4 J allowance for each component, the published values
are \(1.5(1.6656)+0.4=2.8984\) J and
\(1.5(1.7656)+0.4=3.0484\) J. Their maximum, 3.0484 J, is the cell floor.
The example's point-only bounds are zero, so it demonstrates floor composition
but correctly refuses \(R\); it supplies no boundary-doubling result.

Two directional comparisons—token generation and prompt processing, each with its
expected direction fixed before collection—share one
two-sided Holm step-down correction, which keeps the chance of any false
direction claim across the pair at 0.05. For each block \(i\), first form its
paired difference \(d_i=B_i-A_i\), condition B's mean energy in that A/B/B/A
block minus condition A's mean energy. Ordinary repeat-to-repeat scatter gives
the repeat standard error \(se_{\mathrm{repeat}}=s/\sqrt{n}\), where \(s\) is
the sample standard deviation of the ten \(d_i\). For every recorded energy term
that carries its own measurement variance—the instrument's uncertainty in that
term, separate from repeat-to-repeat scatter—the gross repetition term is left out
because its scatter is already counted in \(se_{\mathrm{repeat}}\)—the metrology
standard error carries the paired measurement variance that remains once the
shared A/B covariance—the part of the two conditions' measurement error that
moves together and therefore drops out when B is differenced against A—is
subtracted:

\[
se_{\mathrm{metrology}}^2=
\frac{\sum_{\text{energy terms}}\sum_{i=1}^{n}
\left(\operatorname{var}_{A,i}+\operatorname{var}_{B,i}
-2\operatorname{cov}_{AB,i}\right)}{n^2}.
\]

Combine the two independent sources on the variance scale and then take the
square root, \(se_{\mathrm{total}}=\sqrt{se_{\mathrm{repeat}}^2+
se_{\mathrm{metrology}}^2}\). Divide the mean \(\bar d\) by
\(se_{\mathrm{total}}\); with \(n=10\), the Student-\(t\) reference has
\(n-1=9\) degrees of freedom. The null hypothesis is zero mean difference;
“two-sided” counts equally extreme positive and negative statistics. The
resulting tail area is that comparison's **raw probability** \(p\).

An illustrative, not campaign data, fixture uses ten block differences in
joules: \([5.0,7.6,5.5,4.2,4.7,6.8,5.5,3.6,3.9,3.2]\). Their mean is
\(5.0\) J, their squared deviations sum to
\(\sum_i(d_i-5.0)^2=17.64\ \mathrm{J}^2\), and therefore
\(s=\sqrt{17.64/9}=1.4\) J and
\(se_{\mathrm{repeat}}=1.4/\sqrt{10}=0.442719\) J. Take
\(se_{\mathrm{metrology}}=0.2\) J as a stipulated input: each block contributes
\(0.4\ \mathrm{J}^2\) of paired metrology variance, so summing the ten inputs
and dividing by \(n^2=100\) gives \(0.04\ \mathrm{J}^2\). Thus
\(se_{\mathrm{total}}=\sqrt{0.442719^2+0.2^2}=0.485798\) J and
\(t=5.0/0.485798=10.2923\) on 9 degrees of freedom, with two-sided
\(p=2.8\times10^{-6}\). The separate dependence-sensitivity sheet,
`docs/paper/round7/dependence-sensitivity.md`, works the same ten differences
on its separate branch under a stipulated halving of the effective sample
size—the number of independent blocks that would give the same repeat
scatter—to five blocks, so its degrees of freedom \(\nu\) fall to \(5 - 1 = 4\)—a
named pessimistic scenario, not an estimate—obtaining \(t=7.607258\) and
\(p=0.0016\); its separately estimated AR(1) model, which treats adjacent block
errors as serially correlated, leaves \(n_{\mathrm{eff}}=5.76\) and gives
\(t=8.111070\), \(p=0.0013\). The documents differ in that dependence
assumption, not in their data.

Order the two raw probabilities \(p_{(1)}\le p_{(2)}\). Compare the first with
0.025; only if it passes, compare the second with 0.05. Pairing the fixture's
\(2.8\times10^{-6}\) with a second illustrative raw probability of \(0.041\) for
the other comparison orders them as \(2.8\times10^{-6}<0.041\): the smaller
passes 0.025, then 0.041 passes 0.05, so both directional comparisons pass
Holm. If one contrast is missing, its slot remains: a sole value 0.041 is
compared with 0.025 and fails, while the missing contrast cannot pass. Holm is
one step; the decision-interval sign check (the direction gate) in the next
paragraph is the other, and the sheet's \(\nu=9\) row fails that direction gate
on these same deltas while both comparisons pass Holm.

A directional result then faces two different checks. The magnitude check
requires the absolute point estimate to exceed \(F_{\mathrm{cell}}\); failure
means **not resolvable**—the estimate does not clear the cell floor—not zero.
The direction check requires two named complete uncertainty intervals: the
measurement interval, formed from the total standard error, and the decision
interval, formed by extending both ends of that measurement interval by the
sum of the recorded deterministic bounds. A deterministic bound is a
non-random maximum displacement carried in the authenticated block record.
For each named kind, use its recorded contrast bound when present, otherwise
add its A-side and B-side bounds; average that kind across the ten blocks, then
sum those kind averages. Both intervals must lie wholly on the direction fixed
before collection and the Holm-adjusted test must pass. In the synthetic
example, a 10.0-J point estimate exceeds the 3.0484-J floor. Its measurement
interval is [9.5, 10.5] J. If the authenticated deterministic-bound list for
that example contains 0.10 J and 0.15 J, its sum is 0.25 J and the decision
interval is [\(9.5-0.25\), \(10.5+0.25\)] = [9.25, 10.75] J. Both intervals
remain positive and the adjusted test passes, so the example supports the
positive direction.

The results table's **signed clearance or shortfall** is the absolute point
estimate minus the cell floor. A positive value is the amount by which the
magnitude check clears; zero or a negative value is the shortfall and cannot
pass. The synthetic example prints \(10.0-3.0484=6.9516\) J. This difference
summarizes the magnitude check; it does not replace either uncertainty
interval used by the direction check.

### Outcome sentence forms

Select exactly one only after the authenticated close-out artifact has checked
all eight independent-edge ratios and all four comparative shared-error ratios.
Do not soften, combine, or mechanically retensor these sentences.

**A — every required ratio passes:**

> Every required independent-edge ratio \(R\) was at least 2 and every required comparative shared-error ratio \(R_{cm}\) was at least 2, so allowed boundary movement at least doubled every component's point-only bound on the named M3 Max hardware, MLX, Apple's on-device inference framework, and *powermetrics* power-recording configuration. This result supports the headline that boundary placement dominates point-only variation only if the post-campaign **inserted-gap check**—a test that inserts an approximately 500-ms no-work gap and compares its independently known edges with the power record—supports applying the pulse-derived timing bound to inference.

**B — an authenticated, evaluable ratio is below 2:**

> Every required ratio was authenticated and evaluable, but at least one independent-edge ratio \(R\) or comparative shared-error ratio \(R_{cm}\) was below 2. We therefore withdraw the boundary-doubling sentence and report each failed component without claiming that boundary placement dominated point-only variation.

**Refusal — a required ratio is missing, unauthenticated, or has a zero denominator:**

> A required ratio was missing, unauthenticated, or had a zero denominator and therefore could not be evaluated under the fixed pre-collection rule. This selects neither outcome A nor outcome B, stops all branch-dependent filling, and reports the recorded refusal reason without a boundary-doubling claim.

**Figure 3 is required here.** It must show three separate paths from the
same authenticated evidence: an exclusion path that stops before either gate;
a magnitude path that compares the absolute estimate with
\(F_{\mathrm{cell}}\); and a direction path that takes the measurement interval,
decision interval, Student-\(t\) raw probability, and Holm result to a fixed
positive or negative direction. It must also show the four A/B/B/A members,
one shared sign spanning their blocks, their independent local signs, and the
corner endpoint choices that feed the two ratios. The figure must label every
input, every stop, the two intervals, the two thresholds 0.025 and 0.05, and
the three outcomes above; it must show no campaign number until a fillable
artifact exists.

<!-- CAMPAIGN FILL LEDGER:
1. Report all eight independent-edge ratios:
   [FILL:R_1p7B_prefill_p[PREFILL_LENGTH]_abs]
   [FILL:R_1p7B_prefill_p[PREFILL_LENGTH]_cmp]
   [FILL:R_1p7B_decode_abs] [FILL:R_1p7B_decode_cmp]
   [FILL:R_8B_prefill_p[PREFILL_LENGTH]_abs]
   [FILL:R_8B_prefill_p[PREFILL_LENGTH]_cmp]
   [FILL:R_8B_decode_abs] [FILL:R_8B_decode_cmp].
2. Report the four required comparative shared-error ratios:
   [FILL:R_cm_1p7B_prefill_p[PREFILL_LENGTH]_cmp]
   [FILL:R_cm_1p7B_decode_cmp]
   [FILL:R_cm_8B_prefill_p[PREFILL_LENGTH]_cmp]
   [FILL:R_cm_8B_decode_cmp].
3. Render each absolute R_cm key as not_applicable with its cancellation
   reason, not as a blank:
   [FILL:R_cm_1p7B_prefill_p[PREFILL_LENGTH]_abs]
   [FILL:R_cm_1p7B_decode_abs]
   [FILL:R_cm_8B_prefill_p[PREFILL_LENGTH]_abs]
   [FILL:R_cm_8B_decode_abs].
4. Apply Holm's two-comparison correction for token generation and
   [FILL:V5-G2A-001] — “The selected prefill length is omitted: the hash-bound
   G2-a selection record has not issued (registry row V5-G2A-001).” prompt
   processing. A missing contrast retains its place in m=2 and cannot reject.
5. Build Figure 3 from three distinct paths: evidence exclusion before either
   gate; magnitude against the final cell floor; direction from the complete
   intervals and adjusted test. -->

## 5. Collection stops when required evidence fails

If a required measurement is missing, malformed, outside its fixed limit, or inconsistent with another record, collection stops and records why; the program never substitutes a favorable value or silently skips the member. This behavior is *fail-closed*. The unit governed this way is a two-to-four-hour measurement window, including its calibrations, declared runs, cooldowns, and final verdict.

### Measured admission rules

To admit a stage—that is, to allow its first measured member—the program evaluates these recorded fields and limits immediately before measurement:

- After any operator or stage intervention, it waits \(180\) s with no experiment activity. The environment record must show `power_source = "AC Power"`, `power.external_connected = true`, `low_power_mode = false`, `display_power_state = "all_asleep"`, `screensaver_engaged = false`, and `thermal_pressure = "nominal"`. `power.adapter_watts` must be numeric and must match every other admission observation in the window; adapter description and power-source labels must also remain unchanged. Any mismatch or missing required field refuses admission.
- The pre-run idle baseline samples for \(30\) s at a requested \(10\) Hz and must yield at least \(30\) complete processor-state and power records. For each record, CPU busy ratio is the largest across cores of \(1-\text{idle ratio}-\text{powered-down ratio}\), clipped to \([0,1]\). The reported `cpu_busy_ratio_p95` and `processor_combined_power_w_p95` use nearest-rank p95: sort \(n\) values and select item \(\lceil0.95n\rceil\). Admission requires the former to be at most \(0.5\) and the latter at most \(1.0\) W.
- In those same idle records, fewer than \(40\%\) of raw `gpu.idle_ratio` values may fall below \(0.80\), and `gpu_freq_mhz_mean` must be at most \(800\) MHz. Missing or malformed CPU, GPU, or power telemetry refuses admission. One completely recorded idle-baseline retry is allowed; failure of the retry aborts that stage attempt.
- Between members, the cooldown rule must pass before \(300\) s. A cap hit refuses recovery. Runtime and power-source identities, clock-anchor status, power-record spacing, calibration age, and the post-run environment are also checked. An operator override is recorded but makes the member diagnostic only, never claim-bearing.

A stage attempt stops at its first member failure. If the same cause fails a window stage for the third time, the **window closes**; this rule does not merely close or restart the stage. All collected material remains preserved as diagnostic evidence.

### Counterbalanced order

Each comparison uses A, B, B, A order fixed before collection, with an admitted cooldown between members. Heating or other approximately linear drift over the hour can otherwise favor whichever condition runs later. If run midpoints are \(t_{A1},t_{B1},t_{B2},t_{A2}\), exact first-order balance is \(t_{A1}+t_{A2}=t_{B1}+t_{B2}\); the measured contrast is \((B_1+B_2-A_1-A_2)/2\). Unequal runtimes and cooldowns can break exact balance, while curvature and the separate whole-window drift allowance remain, so the retained midpoint times are part of the evidence rather than an assumed symmetry.

### Every input and every refusal remains visible

Every file the analysis reads is fingerprinted. Failed or interrupted attempts are never deleted or overwritten: an occupied retry slot moves to retained quarantine, the retry uses a new slot, and an append-only replacement record identifies both occurrences. Two present bundles claiming one occurrence cause a refusal. The final verdict binds the declared member set, preserved attempts, replacements, calibration bracket, policy, and drift evidence, preventing later selection of a favorable subset.

The refusal log is part of the result. It preserves contaminated members, calibration outside the allowed condition family, stale drift evidence, unresolved clock anchors, duplicate recorded occurrences, and below-floor effects. In one end-of-night case, re-evaluation refused a window because one member's internal clock alignment could not be resolved; independent adjudication upheld that refusal, and the window remained non-claim-bearing.

The repository is tamper-evident for the operator's own benefit—a way to catch mistakes—not tamper-proof against another program or person. It assumes a single trusted operator, so its gates defend against error and post-hoc choice rather than an adversary; they provide internal consistency, not third-party provenance.

The repository artifact guide holds the maintainer-facing path conventions,
**freeze receipts**—records that fix the plan bytes and the time those bytes
were frozen—generated-state checks, and reissue workflow; Appendix A retains
the scientific route from raw bytes to the reported verdict.

## 6. Demonstration results

<!-- BUILD AFTER CAMPAIGN DATA. This section is never generated by replacing
future tense in the frozen draft. -->

### Results

<!-- WRITE IN THIS ORDER:
1. Print the identical-condition null or its exclusion first.
2. Print the component ratio table below from authenticated suppliers.
3. Insert exactly one canonical outcome sentence from Section 4.
4. Print the fixed Qwen3 pair's magnitude gate, direction gate, and result.
5. Keep the pairwise result separate from scaling language. -->

The selected prompt length remains held. **G2-a** is the fixed-before-
collection shakedown that tests the allowed prompt lengths before any energy
claim. A **hash-bound** selection record carries the SHA-256 digest of the
G2-a record that selected that length, so a later length cannot silently replace
it. A **prompt pin** is the retained record of the selected prompt text and
token IDs together with its tokenizer and generation rules.

| Phase | Model | Cell floor | \(R\), absolute | \(R\), comparative | \(R_{cm}\), absolute | \(R_{cm}\), comparative | Registry status |
|---|---|---:|---:|---:|---|---:|---|
| prompt processing; [FILL:V5-G2A-001] — “The selected prefill length is omitted: the hash-bound G2-a selection record has not issued (registry row V5-G2A-001).” | Qwen3-1.7B | [FILL:DS-11] | [FILL:R_1p7B_prefill_p[PREFILL_LENGTH]_abs] | [FILL:R_1p7B_prefill_p[PREFILL_LENGTH]_cmp] | [FILL:R_cm_1p7B_prefill_p[PREFILL_LENGTH]_abs] | [FILL:R_cm_1p7B_prefill_p[PREFILL_LENGTH]_cmp] | [FILL:DS-09] — “The Qwen3-1.7B prefill-p[PREFILL_LENGTH] gross phase-energy estimate and interval are omitted: the D-123 reported-mean supplier is not built (registry row DS-09).” [FILL:DS-10] — “The Qwen3-1.7B prefill-p[PREFILL_LENGTH] per-token value is omitted: no authenticated D-123 numerator and denominator fields are registered (registry row DS-10).” [FILL:DS-12] — “The Qwen3-1.7B prefill-p[PREFILL_LENGTH] bundle count is omitted: the D-123 admitted independent-bundle basis is undefined (registry row DS-12).” |
| prompt processing; [FILL:V5-G2A-001] — “The selected prefill length is omitted: the hash-bound G2-a selection record has not issued (registry row V5-G2A-001).” | Qwen3-8B | [FILL:DS-15] | [FILL:R_8B_prefill_p[PREFILL_LENGTH]_abs] | [FILL:R_8B_prefill_p[PREFILL_LENGTH]_cmp] | [FILL:R_cm_8B_prefill_p[PREFILL_LENGTH]_abs] | [FILL:R_cm_8B_prefill_p[PREFILL_LENGTH]_cmp] | [FILL:DS-13] — “The Qwen3-8B prefill-p[PREFILL_LENGTH] gross phase-energy estimate and interval are omitted: the D-123 reported-mean supplier is not built (registry row DS-13).” [FILL:DS-14] — “The Qwen3-8B prefill-p[PREFILL_LENGTH] per-token value is omitted: no authenticated D-123 numerator and denominator fields are registered (registry row DS-14).” [FILL:DS-16] — “The Qwen3-8B prefill-p[PREFILL_LENGTH] bundle count is omitted: the D-123 admitted independent-bundle basis is undefined (registry row DS-16).” |
| token generation | Qwen3-1.7B | [FILL:DS-19] | [FILL:R_1p7B_decode_abs] | [FILL:R_1p7B_decode_cmp] | [FILL:R_cm_1p7B_decode_abs] | [FILL:R_cm_1p7B_decode_cmp] | [FILL:DS-17] — “The Qwen3-1.7B `real_prompts_v1` decode gross phase-energy estimate and interval are omitted: the D-123 reported-mean supplier is not built (registry row DS-17).” [FILL:DS-18] — “The Qwen3-1.7B `real_prompts_v1` decode per-token value is omitted: no authenticated D-123 numerator and denominator fields are registered (registry row DS-18).” [FILL:DS-20] — “The Qwen3-1.7B `real_prompts_v1` decode bundle count is omitted: the D-123 admitted independent-bundle basis is undefined (registry row DS-20).” |
| token generation | Qwen3-8B | [FILL:DS-23] | [FILL:R_8B_decode_abs] | [FILL:R_8B_decode_cmp] | [FILL:R_cm_8B_decode_abs] | [FILL:R_cm_8B_decode_cmp] | [FILL:DS-21] — “The Qwen3-8B `real_prompts_v1` decode gross phase-energy estimate and interval are omitted: the D-123 reported-mean supplier is not built (registry row DS-21).” [FILL:DS-22] — “The Qwen3-8B `real_prompts_v1` decode per-token value is omitted: no authenticated D-123 numerator and denominator fields are registered (registry row DS-22).” [FILL:DS-24] — “The Qwen3-8B `real_prompts_v1` decode bundle count is omitted: the D-123 admitted independent-bundle basis is undefined (registry row DS-24).” |

| Contrast | Point estimate | Complete interval | Cell floor | Signed clearance or shortfall | Magnitude outcome | Direction outcome | Verdict |
|---|---:|---:|---:|---:|---|---|---|
| token generation, Qwen3-8B − Qwen3-1.7B | [FILL:DS-25] | [FILL:DS-26] | [FILL:DS-27] | [FILL:DS-28] — “The decode sizing sum and signed clearance are omitted: the claim-side bound and one-cell/two-quantity rendering are unresolved (registry row DS-28).” | [FILL:DS-30] — “The decode floor-gate outcome is omitted: no exact conservative rendering token is registered (registry row DS-30).” | [FILL:DS-31] — “The decode direction-gate outcome is omitted: no exact conservative rendering token is registered (registry row DS-31).” | [FILL:DS-32] — “The decode verdict is omitted: no professor-facing conservative rendering token is registered (registry row DS-32).” |
| prompt processing, Qwen3-8B − Qwen3-1.7B | [FILL:PG-01] — “The selected `_v5` prefill contrast estimate is omitted: `[PREFILL_LENGTH]` is unresolved until G2-a and no authenticated estimate token is registered (registry row PG-01).” | [FILL:PG-02] — “The selected `_v5` prefill interval is omitted: `[PREFILL_LENGTH]` is unresolved until G2-a and no authenticated lower or upper endpoint tokens are registered (registry row PG-02).” | [FILL:DS-33] — “The selected `_v5` prefill claim floor is omitted: `[PREFILL_LENGTH]` is unresolved until G2-a and no professor-facing prefill token is registered (registry row DS-33).” | [FILL:PG-04] — “The selected `_v5` prefill sizing sum and signed clearance are omitted: the claim-bound token family and rendering contract are not registered (registry row PG-04).” | [FILL:PG-06] — “The selected `_v5` prefill floor-gate outcome is omitted: no conservative rendering token is registered (registry row PG-06).” | [FILL:PG-07] — “The selected `_v5` prefill direction-gate outcome is omitted: no conservative rendering token is registered (registry row PG-07).” | [FILL:PG-08] — “The selected `_v5` prefill verdict is omitted: no authenticated professor-facing verdict token is registered (registry row PG-08).” |

<!-- “The decode claim-side bound is omitted: no producing
artifact field is registered, and `deterministic_bounds.total` is not a
substitute (registry row DS-29).” “The selected `_v5` prefill
claim-side bound is omitted: no named producing field or rendering token is
registered (registry row PG-05).” Do not make either undefined quantity a
reader-facing column. -->

### Printed negative result: short prompt processing has too few overlapping records

<!-- BUILD FRESH:
1. A sampling-record support is its start-to-end time interval. Clip each
   support to the prompt-processing interval and count supports with positive
   overlap. Fewer than three refuses the phase.
   **Diagram required:** draw the record supports and the prefill interval on
   one time axis, then mark the two-overlap and three-overlap counts so the
   refusal threshold is visible.
2. State [FILL:DG-067] of [FILL:DG-068] had two overlaps and
   [FILL:DG-069] had three. This is the fixed negative answer, not evidence of
   zero prompt-processing energy and not a model comparison.
3. An interquartile range (**IQR**) is the difference between the upper and
   lower edges of the middle half of sorted values. Work the retained bundle:
   duration [FILL:DG-070], record-width statistic
   [FILL:DG-071] — “The sampling-record width is omitted: its median-with-IQR
   statistic is ratified but not issued (registry row DG-071).”, overlap count
   [FILL:DG-072], threshold [FILL:DG-073], and start-spacing statistic
   [FILL:DG-075] — “The record spacing is omitted: its median-with-IQR statistic
   is ratified but not issued (registry row DG-075).” State that records tile without a
   meaningful pause; width and start spacing describe the same record-period
   distribution apart from endpoint convention. Never resurrect the false
   pause mechanism.
4. Close with population counts [FILL:DG-076] and [FILL:DG-077]. -->

### Demonstration fixed before collection

<!-- BUILD FRESH:
Condition A is [FILL:V5-ID-001]; condition B is [FILL:V5-ID-002]. Build the
A/B/B/A order and sign before the result. The token-generation arm uses
[FILL:V5-WL-001], shared tokenizer [FILL:V5-WL-002], shared conversation
template and reasoning-off pin [FILL:V5-WL-003], and greedy forced-512 output
[FILL:V5-WL-004]. The prompt-processing arm uses [FILL:V5-G2A-001] — “The
selected prefill length is omitted: the hash-bound G2-a selection record has
not issued (registry row V5-G2A-001).” and the post-selection prompt pin
[FILL:V5-WL-005] — “The selected prefill prompt pin is omitted: its
G2-a-bound `joulewise.prefill_prompt_pin.v2` record has not issued (registry
row V5-WL-005).” State ten blocks and Holm m=2.
Call the fixed pair a demonstration of the decision rule, never scaling. -->

### Why the selected prompt length is not yet stated

[FILL:V5-G2A-001] — “The selected prefill length is omitted: the hash-bound
G2-a selection record has not issued (registry row V5-G2A-001).”

The forcing problem is alignment: a prompt-processing phase close to the
three-record minimum can gain or lose an overlapping record when its boundary
moves slightly relative to the sampler. A pre-collection ladder therefore
required two extra overlaps rather than selecting a length from an energy
result.

Before collection, a prompt-length shakedown called G2-a tested 512, 1024, 2048, and 4096 prompt
tokens in that order with at least five Qwen3-1.7B probe runs at every length.
A length passed only when every small-model probe contained at least five power
records whose time interval overlapped prompt processing. Five is a chosen
two-record safety margin above the three overlaps needed to calculate a phase.
For example, counts 5, 6, 7, 5, and 8 pass, while 5, 6, 4, 7, and 8 do not. The
shortest passing length became [FILL:V5-G2A-001] — “The selected prefill length
is omitted: the hash-bound G2-a selection record has not issued (registry row
V5-G2A-001).” Qwen3-8B probes were recorded to discover whether the larger
model made the phase even easier or harder to resolve, but the fixed selection
rule used only the small-model probes.

If no length passed, collection still used 4096; that fallback alone was not a
refusal. A final count below 3 printed `not_resolvable_sample_count`. A count
of 3 or 4 remained calculable but printed “below the fixed-before-collection
count floor of 5” beside the calculated result. This keeps a **reducer**
failure—the program that turns a retained run bundle into phase energies—from
the stricter design floor and leaves the two-comparison Holm family unchanged.

## 7. Discussion and limitations

<!-- BUILD AFTER CAMPAIGN AND TRANSFER FIDUCIAL:
1. Insert the selected exact outcome sentence.
2. Explain what the fixed pair demonstrates and why it is not scaling.
3. State whether the post-campaign inserted-gap fiducial supports transfer of
   the pulse timing bound to inference; the headline remains conditional on it.
4. Do not copy the superseded Discussion prose. -->

### What the finding changes

<!-- BUILD FRESH. Only under Outcome A may the text say that further repeats
attack the smaller point-only component while leaving the larger boundary
contribution. Keep pilot values [FILL:DG-050]–[FILL:DG-052] separate from all
campaign ratio keys. Report every failed or excluded component under Outcome
B. -->

### Further limitations

<!-- BUILD IN THIS ORDER: pulse-to-inference transfer; one physical machine and
software/counter boundary; internal CPU/GPU/neural-engine counter joules with
no external gain check; dependence among ten blocks in one window; incomplete
independent floor re-reduction; trusted-operator rather than adversarial
provenance. State what evidence would close each limit. -->

### Future work

<!-- BUILD FRESH. First: an approximately 500-ms inserted gap in about ten real
inference runs, with both edges fitted by the existing estimator and residual
compared with the pulse-derived bound. Then external-meter gain validation and
another-machine replication. Keep all other research-bank questions outside
this paper's answer set. Use the registered campaign generation throughout. -->

## 8. Related work

### From counter gain to counter time

Running Average Power Limit (RAPL) is a processor-exposed energy counter. Khan et al.'s *RAPL in Action* and Jay et al. own the gain axis: how accurately a software counter reports the magnitude of energy use [5] [6]. For phase-resolved `powermetrics` inference on Apple Silicon, JouleWise opens the complementary time axis: where in time a counter places the energy it reports. Khan et al. align lag, model the relationship between RAPL and wall power, account for temporal correlation, and inspect update granularity, sampler overhead, jitter, overflow, and timestamps [5]. Jay et al. show through controlled regression against wall power that disagreement changes with load, and they decline component claims that their reference meter cannot test [6]. Those studies establish how to validate counter gain; an external wall meter still cannot determine how a software trace should divide a correct total between prompt processing and token generation.

Hähnel et al. are the closest ancestor to this boundary problem. RAPL's update interval limits how short a code path can receive a defensible energy attribution, and they respond by aligning the start and end of the measured path to the counter's own update boundaries — spinning on the register until it advances before entering the code path, and again on leaving it — then enumerating the errors that remain when entry and exit fall inside a single update interval [29]. That is edge placement as an explicit technique, on a different interface and at a different scale. Dauner et al. provide the strongest corroboration. Across RAPL and the NVIDIA Management Library (NVML) software power counter, they show that counter-update behavior and requested sampling frequency can materially change an energy reading; on one evaluated GPU, very frequent polling severely underestimated integrated power, with agreement recovering only at a much longer interval [23]. JouleWise's distinct contribution is to calibrate runtime phase edges in the same measurement window, propagate their permitted positions through the energy integral, and make the resulting cell-specific resolution bound a claim gate (Sections 2, 3, and 5).

### LLM energy measurement

*The Illusion of Power Capping in LLM Decode* is the closest methodological rival. It is phase-aware, repeats configurations, and independently checks sufficiently long sampled-power integrals against a hardware energy counter [20]. JouleWise lacks that independent cross-check. Its narrower advance is different: the power-capping study reports counter agreement, repetition, and timing regimes as separate diagnostics, whereas JouleWise carries uncertain phase-edge placement into the bound that decides whether a phase contrast may be reported.

TokenPowerBench reports prefill and decode energy and groups measurements by context length [7]. Its disclosed method does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation needed to reconstruct a phase-attribution error budget. Ruf and Detyniecki isolate prefill by generating one token and infer decode by subtraction, from one run per context length without error bars [19]. Broader efforts such as ML.ENERGY, Intelligence per Watt, and Apple-focused inference characterizations map energy across useful deployed configurations [8] [22], and Benazir and Lin characterize inference throughput on Apple silicon without energy measurement [13]. They answer system-selection questions; JouleWise instead asks whether one named software-counter boundary can support a phase claim at all.

### Benchmark and metrology lineage

JouleSort established that an energy-efficiency benchmark needs a fixed workload, a comparison metric, and explicit rules for executing the workload and measuring energy [3]. Its boundary is specific: wall power includes conversion losses and every participating component, including idle components; any net change in stored battery energy must be shown no greater than zero with 95% confidence or included in the total. JouleSort also identified synchronization between meter readings and the actual run, alongside the meter's ±1.5% specification, as a reason not to use a fixed-energy-budget metric. JouleWise inherits that boundary discipline rather than replacing it: JouleSort names the synchronization problem at whole-run scale; JouleWise measures its consequence at phase scale.

SPECpower fixes a graduated-load server workload and accepted-analyzer reporting discipline [15]. MLPerf Power extends public energy benchmarking across machine-learning systems, while its associated SPEC methodology requires load-specific analyzer uncertainty, fixed ranges, minimum measurement intervals, invalid-sample accounting, clock synchronization, and controlled battery behavior [1] [2]. JouleWise translates their run-level refusal discipline to a consumer software counter: missing timing evidence invalidates the phase claim rather than disappearing into an average.

Rigorous performance metrology supplies the experimental lineage. Georges, Buytaert, and Eeckhout make repetition, warmup, independence, and uncertainty part of performance evaluation [30]. Mytkowicz et al. show that apparently harmless experimental choices can create systematic measurement bias [31]. JouleWise operationalizes those warnings through paired order, bracketed calibration, fixed-before-collection rules, and explicit refusals, while evidence from one host and configuration cannot establish generality.

Paired minimum-detectable-effect methods use paired variation to estimate the smallest effect a planned study has adequate power to detect. They can allow observed variability to raise, but not lower, a threshold fixed by pre-registration—before results are seen [26]. That work concerns quantization-accuracy benchmarking, not energy. JouleWise borrows its prospective discipline, but treats worst-case phase-edge placement as bounded systematic uncertainty and does not combine it statistically as though it were independent random noise; doing so would take credit for cancellation that the instrument has not demonstrated.

Split and disaggregated inference remain a demanding application rather than this capstone's contribution. Prior work reports whole-run or GPU-only energy for disaggregation and phase-aware placement [27] [12] [10], while SplitZip makes no energy claim [28]. A future JouleWise study would need named boundaries at both endpoints, cross-device clock alignment, and a resolution bound established before collection.

## 9. Evidence and code availability

<!-- BUILD AFTER RELEASE:
1. [FILL:DS-34] — “Repository and archive locators are omitted: the release
   checklist has not issued the registered locator set (registry row DS-34).”
   supplies the repository revision, evidence archive, and fingerprint-manifest
   locators only after it is fillable. No nearby path may substitute.
2. Explain independent re-reduction: rebuild every admitted member and allowed
   timing width from primary bytes and the fixed manifest, compare the complete
   set with the floor artifact, and refuse before analysis on any mismatch.
3. If that consumer remains absent, state the limitation and the lead-custody
   requirement in plain words. -->

## 10. Conclusion

<!-- WRITE LAST, IN THIS ORDER:
1. Insert the selected exact outcome sentence from Section 4.
2. Give the fixed Qwen3 pair decision from fillable DS/PG rows and say it is not
   scaling.
3. Give [FILL:DG-067] of [FILL:DG-068] as the retained negative.
4. State the transfer-fiducial condition and one-machine/counter boundary.
Do not copy or retensor the frozen conclusion. -->

## 11. References

<!-- BUILD AFTER PROSE. Keep only cited entries, verify every locator, add only
sources actually used, and renumber once. -->

## Appendix A. Reproducing this work

This appendix separates two tasks. *Re-derivation* recomputes reported values from preserved bytes; it needs the released code and evidence, not Apple hardware or administrator privilege. *Fresh collection* creates new evidence and requires the named machine and measurement conditions. A *fingerprint* below is a SHA-256 digest of exact file bytes. A *refusal* is a recorded decision that the supplied evidence does not authorize a requested result, together with a reason name.

The code repository is available to the project, but the claim-bearing evidence archive and its public locators are not yet released. Moreover, the registered L1 floor-binding limitation—the claim consumer's incomplete binding of a floor back to the complete governed extraction evidence—remains open. The demonstration evidence chain therefore is **not presently open to independent re-reduction**. The steps below state what becomes executable only after the release manifest supplies every angle-bracketed input.

### A.1 What a reader needs

Re-derivation requires a full-history checkout at the released revision, Python 3.11 or later, and a copy of the evidence archive. JouleWise's core declares no third-party dependencies in `pyproject.toml`; `env/analysis-lock.txt` records the environment used for retained reductions. Optional plotting and Mac inference dependencies are not part of the numeric replay.

Fresh collection additionally requires the configured Apple-silicon instrument, the exact model files named by the plan, the measurement environment recorded in `env/mac-measurement-lock.txt`, non-interactive permission to run `/usr/bin/powermetrics`, and the measured admission predicates in Section 5. The retained configuration used one Apple M3 Max. This work does not establish that another Mac, operating-system build, model revision, or quantization shares its measured limits; that machine must characterize its own cells.

### A.2 Scientific artifacts and their bindings

The repository contains programs and plans, but measured run directories are excluded from Git. The separate archive must provide these connected objects:

1. A run bundle at `<runs root>/<run id>/`. `config.json` identifies the condition; `events.jsonl` supplies phase boundaries; `raw/powermetrics.plist` is the native power capture; `power_trace.csv` is its parsed trace; and `summary_metrics.json` contains the reduction. `metadata.config_sha256` binds the stored result to the exact configuration bytes. Strict validation independently rebuilds the trace and summary rather than trusting either derived file.
2. The bundle's `instrument_calibration/` subtree. Its `raw/powermetrics.plist` and `events.jsonl` hold the calibration trace and commanded pulse times; `instrument_evidence.json` names the clock-anchor method and published pulse-edge bound. Removing any member breaks the scientific binding. Section A.3 gives the complete estimators that turn those inputs into the bound.
3. The fixed campaign plan, its freeze receipt, calibration-acceptance file, policy, drift-bound artifact, extraction specification, and analysis manifest. The receipt issue time and fingerprints establish which membership, limits, estimator, and contrasts were fixed before the evidence they judge.
4. The append-only whole-window verdict, which binds admitted members, preserved failures and replacements, the calibration bracket, policy, and drift evidence. The floor extraction then binds each reported floor to its admitted cell. The claim verdict binds the contrast estimate, composed uncertainty, cell floor, and two decision gates to those authenticated inputs.

A fingerprint proves equality to disclosed bytes, not who created the original capture. Presence in the archive also does not mean a bundle was analyzed: the whole-window verdict, not directory membership, decides that.

### A.3 Formal calibration algorithms

This appendix specifies the two calculations behind the calibration numbers in Section 2 precisely enough that a reader can rebuild them from this text alone: the **clock-anchor estimator**, which places the instrument's power trace on the controller's wall clock and prices how far that placement can be wrong, and the **pulse-fit (accepted-region) algorithm**, which measures how far the instrument's reported edge timing departs from commanded edges and turns the worst departure into the calibration bound. Everything below is stated as the code executes it. Constants are quoted with their values; a reader who wants the source line for any equation, constant, or rule will find it in the evidence list that follows the prose.

Two conventions hold throughout. All times are in seconds unless marked "ns" (nanoseconds). "Wall clock" means the controller's Unix-epoch UTC clock (`time.time()`), and "monotonic clock" means the controller's monotonic counter (`time.monotonic()`), which cannot jump backward or be adjusted but has an arbitrary origin. "binary64" means the IEEE-754 double-precision floating-point format that Python floats use. "Exact floating summation" means a compensated, correctly rounded sum (Python's `math.fsum`): the result is the true sum of the inputs rounded once to binary64, so summation order cannot change it. "ppm" is parts per million.

#### A.3.1 The objects the algorithms operate on

**The instrument and its records.** The instrument is macOS `powermetrics`, run with the samplers `cpu_power,gpu_power,ane_power,thermal` at a commanded sampling interval of 100 ms. It emits a stream of property-list documents. Each document is one *record*; record *i* (counting from 0) carries:

- `elapsed_ns`, written *e_i*: the length in nanoseconds of the averaging window the record summarises.
- a `timestamp` date, written *n_i* once converted to Unix-epoch nanoseconds. The instrument writes this date at whole-second granularity, and the estimator refuses any record whose *n_i* is not a whole number of seconds. *n_i* labels the **end** of the record's averaging window, quantised down to the second.
- three processor power fields, `cpu_power`, `gpu_power`, `ane_power`, each in milliwatts; and three processor energy counters, `cpu_energy`, `gpu_energy`, `ane_energy`, each an integer in millijoules.
- an `is_delta` flag, which must be `true` (the record is an interval aggregate, not a cumulative counter).

From those fields the parser derives, for every record *i*:

- the per-channel powers in watts, `rail_power_w[ch] = field_ch / 1000` for each channel *ch* in {`cpu_power`, `gpu_power`, `ane_power`};
- the **combined power** *p_i* = Σ_ch `rail_power_w[ch]`, i.e. cpu + gpu + ane, in watts, formed by converting each channel to watts first and then summing the three;
- the **record energy** *E_i* = (`cpu_energy` + `gpu_energy` + `ane_energy`) / 1000, in joules, formed by summing the three integer millijoule counters (with exact floating summation) and then dividing by 1000.

*p_i* and *E_i* are used for only one thing: a health check that the record's power and energy agree, |*p_i* · (*e_i*/10⁹) − *E_i*| ≤ 0.002 J + 0.001·|*E_i*|. Worked example (capture `20260722T145535-e941c821`, record 0): *e_0* = 111 242 541 ns; the parsed channel powers are 0.9169149999999999 W + 0.00898937 W + 0.0 W, giving *p_0* = 0.9259043699999999 W; counters 102 + 1 + 0 mJ give *E_0* = 0.103 J; and *p_0* · 0.111242541 s = 0.10299995484180416 J, which differs from *E_0* by 4.5·10⁻⁸ J, far inside the tolerance. The pulse fit itself never uses *p_i*; it reads only the `gpu_power` channel (Section A.3.5).

**Cumulative elapsed time.** Define *q_0* = 0 and *q_i* = *e_1* + *e_2* + … + *e_i* (nanoseconds) for *i* ≥ 1. *q_i* is the instrument's own count of time from the end of record 0 to the end of record *i*. Note that *e_0* is deliberately excluded: record 0's end is the reference point, so its own length does not enter *q*.

**Clock stamps.** The controller reads time with a *paired stamp*: it reads the monotonic clock, then the wall clock, then the monotonic clock again, and records all three values together with the operating system's stated resolution of each clock. A stamp *S* therefore has five fields: *w* (wall epoch seconds), *mb* (monotonic before), *ma* (monotonic after), and the two resolutions, from which we define *r* = max(wall resolution, monotonic resolution). The wall read happened somewhere between the two monotonic reads. The stamp's **half-width** is

    u(S) = (ma − mb)/2 + r,

the largest amount by which the wall value can be wrong as a label for the midpoint of the monotonic bracket. On the capture used below every stamp reports a wall resolution of 0.0000010000000000000002 s (the closest binary64 value to 1 µs) and a monotonic resolution of 4.166666666666666e-8 s, so *r* = 0.0000010000000000000002 s for every stamp.

**Trace intervals.** After the trace is anchored (A.3.4), each record becomes a *trace interval* *I_i* = [*t_i* − *e_i*/10⁹, *t_i*) carrying one power value *y_i* = `gpu_power` in watts, where *t_i* is the wall-clock time of the record's end. |*I_i*| denotes its length in seconds.

**Commanded pulses.** A commanded pulse *P* is a pair of stamps, one taken immediately before the controller starts driving the GPU and one immediately after it stops. It is stored as four numbers: *on* = wall time of the on-stamp, *off* = wall time of the off-stamp, *u_on* = half-width of the on-stamp, *u_off* = half-width of the off-stamp. Pulses are numbered *j* = 0 … 58.

#### A.3.2 The capture procedure

The forcing problem: the instrument labels its records only to the whole second, and the operating system tells us nothing about when the first record's window began. Without a deliberate protocol there is no way to know where the trace sits on the wall clock, let alone how sharply it reports an edge. The protocol below manufactures both kinds of evidence.

The capture is protocol `powermetrics_pulse_fiducial_v3`. (*Fiducial* here means a commanded reference edge whose wall-clock time is known independently of the instrument; it is not fiducial inference in the statistical sense.) In order, the controller:

1. Takes stamp **S_pre** (named `pre_spawn`), then spawns `powermetrics`.
2. Polls the output file until the first record parses, then takes stamp **S_parse** (named `first_parse`). Because the poll succeeded, record 0 had been completely written before S_parse.
3. Waits until the whole-second `timestamp` label of a record advances at least once (a *rollover*), so that the anchor interval is bounded on both sides before any work happens. (The estimator in A.3.3 later requires at least *two* such label increases across the whole capture; the capture-time wait guarantees only the first, and a 197-second capture supplies the rest.)
4. Takes stamp **S_start** (`sampling_started`), then rests 5 s (the pre-train quiet baseline, `BASELINE_S`).
5. Drives 3 **warm-up pulses**, each 1 s of GPU work followed by a 1.5 s rest. Each warm-up on/off edge is stamped and logged as `warmup_command_on` / `warmup_command_off`, but warm-ups are not protocol pulses (see A.3.4 for what happens to them).
6. Rests 5 s.
7. Drives the **59 measured pulses**. Pulse *j* (0-based) is commanded on at planned schedule offset *τ_j* and off at *τ_j* + 1.0 s, where *τ_0* = 0 and *τ_{j+1}* = *τ_j* + 1.0 + gap(*j*+1), with gap(*k*) = 1.5 + vdC₂(*k*). vdC₂ is the base-2 van der Corput sequence: write *k* in binary, reverse its digits, and read the result as a binary fraction after the point. Equivalently, if *k* = Σ_m d_m·2^m with binary digits d_m, then vdC₂(*k*) = Σ_m d_m·2^(−m−1). So vdC₂(1) = 0.1₂ = 0.5, vdC₂(2) = 0.01₂ = 0.25, vdC₂(3) = 0.11₂ = 0.75, vdC₂(4) = 0.001₂ = 0.125, and vdC₂(1…8) = 0.5, 0.25, 0.75, 0.125, 0.625, 0.375, 0.875, 0.0625. The first five gaps are therefore 2.0, 1.75, 2.25, 1.625, 2.125 s. The purpose of the irregular gaps is to stop pulse edges from landing at the same phase of the ~10 Hz sampling cadence pulse after pulse. Offsets are measured from a monotonic reading taken immediately before the loop starts (after step 6), not from S_start. Each on/off edge is stamped and logged as `pulse_command_on` / `pulse_command_off` with the full stamp. The GPU work is repeated 4096×4096 float16 matrix multiplications with a fence after each (`mx.eval`), on buffers allocated before the capture, so that the commanded off-edge is honest: no queued work spills past the off-stamp.
8. Rests 5 s, takes stamp **S_stop** (`sampling_stopped`), terminates `powermetrics`, and takes stamp **S_post** (`post_parse`).

The five stamps S_pre, S_parse, S_start, S_stop, S_post are recorded in that order; the pulses are recorded in `events.jsonl`; the raw record stream is retained byte-for-byte and hashed. Every quantity below is re-derived from those primary bytes; stored summary values are never inputs.

#### A.3.3 The clock-anchor estimator

The estimator's identity is `powermetrics_native_second_rate_aware_set_membership_v1`. Its output is the wall-clock time of the **end of record 0**, called the **anchor** and written *A*, together with a bound on how wrong *A* can be. The design principle is *set membership*: rather than estimating *A* and attaching a statistical error, the estimator writes down every constraint the evidence imposes and computes the exact set of (*A*, rate) values consistent with all of them. The reported interval is that set's extent in *A*; the point value is its midpoint. Arithmetic is exact rational (Python `Fraction`); only the final outputs are converted to binary64. Every *limit* and *bound* is rounded *outward* (a lower limit toward −∞, an upper limit or a bound toward +∞) to the nearest binary64 in that direction; the point anchor (the midpoint) is converted with ordinary round-to-nearest.

**The model.** Two unknowns:

- *β*, the rate of the wall clock relative to the monotonic clock (dimensionless; 1 means the two clocks tick at the same speed);
- *α*, the wall time (ns) at the monotonic instant *m_0* = *mb*(S_pre) · 10⁹, i.e. at the first monotonic read of the pre-spawn stamp.

The wall clock is assumed affine in monotonic time over the capture: wall(*m*) = *α* + *β*·(*m* − *m_0*) for any monotonic reading *m* (ns). The third unknown, *A*, is expressed through this relation as described under "causal constraints."

**Model condition (stated because the containment claim depends on it).** The estimator's interval contains the true anchor *provided that* (i) the wall clock has a single rate across the capture with no step adjustment, and (ii) each whole-second label departs from the affine relation by at most 250 µs (`MAX_AFFINE_CLOCK_RESIDUAL_S`), an allowance charged in full and never shrunk to the observed residual. A wall-clock excursion of less than 250 µs occurring between stamps is invisible to the arithmetic; it is excluded by the requirement that any capture whose numbers support a published claim runs with network time synchronisation off, which is a recorded admission condition, not something the estimator can verify.

**Inputs and their admission checks.** All five stamps must be present and well formed, the trace must be non-empty, and every record's elapsed value must be finite and non-negative. Each failure returns `clock_anchor_unresolved` with a named detail; the repository artifact guide (`docs/paper/artifact-guide.md` Section 9, "Calibration algorithm operator detail" — the target of every such pointer below) enumerates the checks and their detail strings.

**Wall-minus-monotonic span.** Index the five stamps by *v* (reserving *j* for pulses). For each stamp *v* compute the raw offset range [*w_v* − *ma_v*, *w_v* − *mb_v*]. The **span** is

    span = max_v (w_v − mb_v) − min_v (w_v − ma_v)

over the five stamps, in seconds. These two subtractions are the one place the estimator does not use exact rational arithmetic: they are performed in binary64 on the stored stamp values, and the resulting float is then exactified — which is what the 10⁻⁶ s padding term below pays for. The span measures how much the wall clock drifted against the monotonic clock over the whole capture, including any slew (gradual rate adjustment applied by the operating system's time discipline). If span > 0.005 s the capture is refused (`wall_minus_monotonic_span_exceeded`). Worked example (same capture; wall origin is the Unix epoch, monotonic origin is the machine's boot): the largest raw upper offset *w* − *mb* is 1784298599.0949996 s (at S_stop) and the smallest raw lower offset *w* − *ma* is 1784298599.0945535 s (at S_pre); the difference is span = 0.00044608116149902344 s (446 µs), the second of the four terms in the final bound.

**Numeric-padding check.** Let *w_max* = the largest |*w_v*| over the five stamps. The estimator requires 4·ulp(*w_max*) ≤ 10⁻⁶ s, where ulp is the spacing of binary64 numbers at that magnitude, and refuses otherwise (`numeric_padding_insufficient`). For epochs in 2004–2038 the ulp is 2⁻²² s ≈ 238 ns, so the term is ≈ 954 ns and the check passes. Why four: at most four epoch-scale floating-point roundings can lean inward in the emitted bound (two inside the span's subtractions, one per anchor endpoint).

**Stamp constraints.** For each stamp *v* (all quantities converted to ns by multiplying by 10⁹; *r_v* is the stamp's resolution in ns):

    α ≤ h_v(β) := (w_v + r_v) − β·(mb_v − r_v − m_0)
    α ≥ g_v(β) := (w_v − r_v) − β·(ma_v + r_v − m_0)

These say: the wall value *w_v*, padded by ±*r_v*, must lie between the affine wall times of the monotonic bracket ends, each end padded outward by *r_v*.

**Native-label constraints.** For each record *i*, with *δ* = 250 µs = 250 000 ns:

    n_i − δ ≤ A + β·q_i ≤ n_i + 10⁹ + δ

*A* + *β*·*q_i* is the model's wall time for the end of record *i* (record 0's end, advanced by the instrument-counted elapsed time *q_i* scaled by the rate). The label *n_i* is that time rounded down to the second, so the true value lies in [*n_i*, *n_i* + 1 s), widened by the 250 µs allowance on each side.

**Causal constraints, and the two symbols k_pre and k_parse.** Two facts tie *A* to *α*. First, record 0's averaging window cannot have started before `powermetrics` was spawned, which happened after S_pre; so the window's end is at least *e_0* after the earliest possible time of S_pre's monotonic bracket. Second, record 0 had been fully written by S_parse; so its end is no later than the latest possible time of S_parse's monotonic bracket. In monotonic nanoseconds relative to *m_0*:

    k_pre   := (mb(S_pre)·10⁹ − r_pre − m_0) + e_0  =  e_0 − r_pre        (all in ns)
    k_parse := ma(S_parse)·10⁹ + r_parse − m_0                          (all in ns)

and the constraints are

    α + β·k_pre ≤ A ≤ α + β·k_parse.

Because *m_0* is *by definition* *mb*(S_pre) · 10⁹, the first bracket collapses and **k_pre equals e_0 minus one resolution unit r_pre**. This is by design, not error: *k_pre* is the earliest monotonic instant (relative to *m_0*) at which record 0 can end, and the pre-spawn stamp's own monotonic read is uncertain by *r_pre*, so the earliest instant is pushed *earlier* by exactly that amount. Worked example: *e_0* = 111 242 541 ns and *r_pre* = 0.0000010000000000000002 s ≈ 1000 ns, so *k_pre* = 111 241 541 ns; and *k_parse* = (458737.509840291 − 458736.4081875)·10⁹ + 1000 ns = 1.1016537909669094·10⁹ ns, i.e. record 0 ended between 0.111 s and 1.102 s after *m_0*. If *k_pre* > *k_parse* the stamps are inconsistent and the capture is refused (`clock_stamp_invalid`).

**Eliminating α.** *α* appears with coefficient 1 in every stamp and causal constraint, so it is removed exactly by Fourier–Motzkin elimination, leaving linear constraints in (*β*, *A*) only:

- for every ordered pair of stamps (*v*, *v′*), including *v* = *v′*: *g_v′*(β) ≤ *h_v*(β) (25 rows; these say some *α* exists);
- for every stamp *v*: *A* ≤ *h_v*(β) + *β*·*k_parse* (5 rows);
- for every stamp *v*: *A* ≥ *g_v*(β) + *β*·*k_pre* (5 rows).

**The feasible set and the solver.** The variables are boxed: *β* ∈ [1 − 10⁻³, 1 + 10⁻³] and *A* ∈ [min_i *n_i* − 2·10⁹, max_i *n_i* + 2·10⁹] ns, a bracket deliberately far wider than any feasible extent; only *β* attaining a box edge is treated as a refusal (step 4 below). The feasible set is the polygon cut from that box by all native, stamp, and causal rows (two native rows per record; 1665 records give 3330 rows on the example capture). Every optimum below is an exact two-variable linear programme over that polygon; the code uses an incremental (Seidel-type) exact rational solver with a fixed-seed row order, but any exact LP solver returns the same optimal *values*, which is all that is used.

The solver is applied in this order, each step refusing on infeasibility:

1. Native rows alone infeasible → `rate_aware_native_set_empty`.
2. Native + stamp rows infeasible → `affine_clock_fit_empty`.
3. All rows infeasible → the native rows are re-formed with *δ* = 1 s and recombined with the same stamp and causal rows; if that full relaxed set is feasible the detail is `affine_clock_residual_exceeded`, otherwise `admissible_interval_empty`.
4. *β_lo* = min *β*, *β_hi* = max *β* over the full set. If either equals its box edge → `clock_fit_unbounded`. If *β_lo* < 1 − 50·10⁻⁶ or *β_hi* > 1 + 50·10⁻⁶ (50 ppm, `MAX_CLOCK_RATE_DEVIATION_PPM`) → `clock_rate_limit_exceeded`. The rate is refused, never clipped.
5. *A_lo* = min *A*, *A_hi* = max *A* over the full set.
6. First-parse lag: the largest value over the feasible set of min_v (*h_v*(β) + *β*·*k_parse* − *A*), computed by solving one LP per stamp with the other stamps' forms constrained to be no smaller and taking the best. This is the longest time, consistent with all evidence, between record 0's end and the latest instant the first-parse stamp allows for it — how loosely the causal upper constraint holds. A negative value means the causal constraint is inconsistent with the rest; a value above 0.25 s (`MAX_FIRST_PARSE_LAG_S`) means the controller noticed record 0 too long after it was written for the upper causal constraint to be trusted as a tight physical bound; either → `first_parse_lag_exceeded`. On the example capture it is 0.05247795879145338 s.
7. A diagnostic-only relaxation search is also run; the repository artifact guide gives its bounds and step count.

**Composing the bound.** With *A_lo*, *A_hi* in ns:

    H       = (A_hi − A_lo) / 2 / 10⁹                       (seconds)
    r_max   = max over the five stamps of r_v               (seconds)
    B_anchor = roundup( H + span + r_max + 10⁻⁶ )

where roundup is outward rounding to binary64 and 10⁻⁶ s is `NUMERIC_PADDING_S`. The point anchor is *A* = (*A_lo* + *A_hi*)/2 converted to seconds. If *B_anchor* > 0.005 s the capture is refused (`effective_clock_anchor_bound_exceeded`).

The four terms price four different errors and none subsumes another:

1. **H** prices *where record 0's end sits on the wall clock* — the half-width of the exact admissible interval for *A*.
2. **span** prices *within-capture wall-versus-elapsed drift*. It is needed because the trace anchoring of A.3.4 advances the trace from the single point *A* at rate exactly 1 using the instrument's elapsed counts, while the pulse edges the fit of A.3.5 compares it against carry wall-clock stamps; if the wall clock ran fast or slow relative to elapsed time during the capture, every later trace interval is displaced by up to the span, and *H* knows nothing about it.
3. **r_max** prices the *reported resolution of the clocks* that produced the stamps.
4. **10⁻⁶ s** prices *binary64 representation error* of the epoch-scale inputs that were exactified into rationals (see the numeric-padding check above).

Worked example (capture `20260722T145535-e941c821`, wall origin the Unix epoch): *A_lo* = 1784757336.5519202 s and *A_hi* = 1784757336.5532944 s after outward rounding, point anchor *A* = 1784757336.5526073 s, and the four terms are

    H      = 0.0006869160344978743
    span   = 0.00044608116149902344
    r_max  = 0.0000010000000000000002
    pad    = 0.000001
    sum    = 0.0011349971959968977402  →  roundup  →  0.0011349971959968978 s

so *B_anchor* = 0.0011349971959968978 s (1.135 ms). The sum is exact in decimal; the published value is that sum rounded outward to the nearest binary64, which is the one shown. *H* is computed from the exact rational endpoints, before they were rounded to the printed *A_lo* and *A_hi*: recomputing (*A_hi* − *A_lo*)/2 from the printed endpoints gives 0.0006871223449707031 s, 0.0000002063105 s above the exact *H* — less than one binary64 spacing at the epoch magnitude 1.78·10⁹ s, which is 2.4·10⁻⁷ s — because each endpoint was rounded outward before printing. A reader who does that subtraction should not expect the headline sum to close from the printed endpoints. Fitted rate window: [1.0000022202281935, 1.0000022646196323], i.e. the wall clock ran about 2.2 ppm fast against the monotonic clock over the 197-second capture; 197 rollovers and 1665 records were checked.

#### A.3.4 Placing the trace on the wall clock, trimming warm-ups, and authenticating the schedule

**Anchoring.** With the point anchor *A* (seconds), record *i*'s end time *t_i* is produced by floating-point accumulation as the records are read: *t_0* = *A* exactly, and each later record adds its own *e_i*/10⁹ to a running binary64 sum. That accumulation is the normative definition; *t_i* = *A* + *q_i*/10⁹ is its exact-arithmetic equivalent. Its trace interval is *I_i* = [*t_i* − *e_i*/10⁹, *t_i*) with *y_i* = the record's `gpu_power` in watts. The whole trace therefore moves rigidly with *A*, at rate 1 — the reason the span term exists.

**Reading the pulses.** The command event log is scanned for on/off events and paired into pulses, warm-up and measured; the repository artifact guide gives the event names and the pairing rules.

**Trimming warm-ups.** Let *T_warm* = the wall time of the last warm-up's off-stamp. Every trace interval whose start is earlier than *T_warm* is discarded; only intervals with start ≥ *T_warm* survive. Consequently **warm-up pulses do not participate in the baseline set and are never fitted**: their plateaus are removed from the trace altogether, along with the pre-train quiet baseline and everything else before *T_warm*. The 1.5 s rest plus 5 s rest that follow the last warm-up remain in the trace and supply quiet support before the first measured pulse. Warm-ups exist to bring the GPU to its operating state before the measured train; leaving them in the trace would make the baseline classifier (A.3.5) report them as uncommanded plateaus and invalidate the capture.

**Authenticating the executed schedule.** From the pulse stamps and the trimmed trace, all of the following must hold, else the capture is refused: every measured pulse's *off* − *on* lies in [0.8 s, 1.2 s]; for every consecutive pair (*j*, *j*+1), counting *k* = *j*+1 from 1, the executed gap *on_{j+1}* − *off_j* is within 0.25 s (`MAX_AUTHENTICATED_GAP_ERROR_S`) of 1.5 + vdC₂(*k*); the trimmed trace begins at least 4.5 s before pulse 0's *on*; and it ends at least 4.5 s after pulse 58's *off*. No planned-offset metadata is trusted; only stamps and trace extent.

#### A.3.5 The pulse-fit algorithm

The forcing problem: a 1 s rectangular GPU pulse, sampled by an instrument averaging over ~100 ms windows, appears in the trace as a plateau with two smeared edges. We want to know how far the instrument's reported edge positions sit from the commanded ones, and we want the *whole set* of edge positions the data cannot rule out, not merely the best-fitting one — because it is the extent of that set, not the best fit, that bounds what a later measurement window can trust.

**Baseline set and robust scale.** Define the *margin window* of pulse *j* as [*on_j* − 0.75 s, *off_j* + 0.75 s] (`LOCAL_MARGIN_S` = 0.75). The **baseline set** *O* is every trace interval (after trimming) that overlaps no measured pulse's margin window, where "overlaps" means min(interval end, *off_j* + 0.75) > max(interval start, *on_j* − 0.75). Only the 59 measured pulses define margin windows; as established in A.3.4, warm-up intervals are already gone. There must be at least 3 intervals in *O*. Then

    b = median{ y_i : I_i ∈ O }                                    (baseline power, W)
    σ = max( 1.4826 · median{ |y_i − b| : I_i ∈ O },  0.001 W )    (robust scale)

The median absolute deviation (MAD) is the median of the absolute distances from the median; 1.4826 converts it to a standard-deviation equivalent for Gaussian noise; the 1 mW floor prevents a perfectly flat baseline from producing σ = 0. Worked example: on the example capture the idle GPU channel reads 0.0 W throughout the baseline set, so *b* = 0.0 W, the MAD is 0, and the floor engages: σ = 0.001 W.

**Spurious-plateau check on the baseline set.** The check is evaluated once, after every pulse in the train has been fitted, not as a gate before the fits; a capture that exhausts the work budget of A.3.7 is therefore recorded as nonconvergent whether or not it also carries a spurious plateau. Sort *O* by start time. With threshold *b* + max(5.0 W, 5σ), count each run of at least 2 consecutive baseline intervals above the threshold as one spurious plateau (a run of any length ≥ 2 counts once). Any spurious plateau invalidates the capture — it means the GPU did work when nothing was commanded, and a fit could not distinguish that from instrument timing.

**Per-pulse fit.** For pulse *j* with commanded (*on*, *off*, *u_on*, *u_off*):

1. **Local set** *L*: all trace intervals overlapping the margin window [*on* − 0.75, *off* + 0.75], by the same overlap test as above. Everything below sums over *L* only.
2. **Interior set**: intervals in *L* with start ≥ *on* + 0.25 and end ≤ *off* − 0.25 (`PLATEAU_INSET_S` = 0.25) — the part of the plateau that no plausible edge smear reaches. If empty → reject `no_plateau_interior_intervals`.
3. **Amplitude** *a* = median{ *y_i* : interior } − *b*, and **robust SNR** = *a*/σ. Reject if *a* < 10 W (`plateau_below_minimum`) or SNR < 10 (`robust_snr_below_minimum`). The amplitude is fixed at this value for the rest of the fit; it is not a free parameter. Example (pulse 0 of the capture): *a* = 40.6667 W, SNR = 40 666.7. All pulse-0 fit values quoted in this section were computed when the capture was first processed, under an earlier anchor point 1784757336.5528765 s, about 0.27 ms later than the current point quoted in A.3.3; a refit under the current anchor would move them slightly. They are quoted to show magnitudes, not as claim values.
4. **Edge coverage**: the earliest start in *L* must be ≤ *on* − 0.75 and the latest end in *L* ≥ *off* + 0.75; otherwise → `edge_coverage_missing`. A trace truncated near either edge cannot certify that edge.
5. **The model and the objective.** For candidate edge shifts (*d_on*, *d_off*) in seconds, the model predicts interval *i*'s power as

       ŷ_i(d_on, d_off) = b + a · | I_i ∩ [on + d_on, off + d_off] | / |I_i|

   i.e. baseline plus amplitude times the fraction of the averaging window that the shifted pulse covers. The overlap length is max(0, min(end_i, off + d_off) − max(start_i, on + d_on)). The objective is the Huber loss of the standardised residuals,

       Loss(d_on, d_off) = Σ_{I_i ∈ L} ρ( (y_i − ŷ_i) / σ ),
       ρ(x) = x²/2            if |x| ≤ 1.345,
       ρ(x) = 1.345·(|x| − 0.6725)   otherwise,

   summed with exact floating summation. Huber's loss is quadratic for small residuals and linear for large ones, so a single wild sample cannot dominate.

6. **The search (constrained coordinate descent).** The two shifts are searched one at a time on explicit grids, starting from *d_on* = *d_off* = 0, with the half-range *R* = 0.75 s (`FIT_HALF_RANGE_S`), a coarse step *s_coarse* = 0.005 s and a fine step *s_fine* = 0.0005 s. Define the candidate grid centred on a value *c* with step *s* as the explicit set

       G(c, s) = { c + s·k : k ∈ ℤ, −N ≤ k ≤ N,  N = ⌈R / s⌉ } ∩ { d : |d| ≤ R }.

    The grid is finite and explicit, so the search is reproducible; the repository artifact guide gives the point counts for each step and the clipping behaviour.

   The procedure is exactly:

       for s in (s_coarse, s_fine):
           repeat 2 times:
               d_on  ← argmin over d ∈ G(d_on,  s) of Loss(d, d_off)
               d_off ← argmin over d ∈ G(d_off, s) of Loss(d_on, d)

    Eight one-dimensional searches in all — onset and offset at the coarse step, then the same pair at the fine step. The repository artifact guide states the tie-break rule. Write *Loss\** for the loss at the pair (*d_on*, *d_off*) the procedure ends with — the fit's best loss. It is used in steps 7 and 8 and in the loss limit below.

7. **Significance.** Let *Loss_flat* = Σ_{I_i ∈ L} ρ((*y_i* − *b*)/σ), the loss of a model with no pulse at all. Require *Loss\** < 0.5·*Loss_flat*; otherwise → `model_fit_not_significant`.
8. **Shift limit.** Require |*d_on*| < 0.5 s and |*d_off*| < 0.5 s (`MAX_VALIDATED_EDGE_SHIFT_S`); a fitted shift of 0.5 s or more → `fitted_shift_exceeds_validation_limit`. The search range (±0.75 s) is deliberately wider than the acceptance range (±0.5 s) so that a true shift near the acceptance edge is found rather than pinned.

**The set of acceptable edge pairs.** The fitted point is not the output. Define the **loss limit**

    Λ = Loss* + max(1.0, 0.05 · Loss*).

The **accepted region** is the set of all (*d_on*, *d_off*) in the square [−0.75, 0.75]² whose loss is at most Λ — every edge placement the data cannot distinguish from the best one by more than the tolerance. The algorithm computes a guaranteed *enclosure* of that region, not a sample of it, by interval branch-and-bound:

- **Cell lower bound.** For a rectangle *C* = [on_lo, on_hi] × [off_lo, off_hi] of shifts, the covered fraction of any interval is monotone: it decreases as the onset moves later and increases as the offset moves later. So over *C* the model prediction for interval *i* lies between ŷ_i(on_hi, off_lo) and ŷ_i(on_lo, off_hi). Writing *z_i* = (*y_i* − *b*)/σ and the two normalised predictions *ẑ_lo* ≤ *ẑ_hi* (amplitude times fraction, over σ), the distance from *z_i* to the nearest point of [*ẑ_lo*, *ẑ_hi*] is 0 if *z_i* lies inside, else min(|*z_i* − *ẑ_lo*|, |*z_i* − *ẑ_hi*|). LB(*C*) = Σ_i ρ(distance_i). No point of *C* can have loss below LB(*C*), because each term is the smallest Huber value its interval can attain anywhere in *C*.
- **Procedure.** Start with the single cell [−0.75, 0.75]² on a last-in-first-out stack. Repeatedly pop the most recently pushed cell: if LB(*C*) > Λ, discard it (no accepted point can lie inside). Otherwise, if both of its side lengths are ≤ 10⁻⁴ s (`REGION_COVERAGE_RESOLUTION_S`), *retain the entire cell*. Otherwise bisect it at the midpoint of its wider side (the onset side when the two are equal) and push the lower half first, then the upper half, so the upper half is processed next (depth-first). Because a cell is discarded only on a rigorous lower bound and retained cells are kept whole, every accepted point is inside some retained cell — including points between resolution cells. Starting from a side of 1.5 s, 14 halvings bring a side to 1.5/2¹⁴ ≈ 9.16·10⁻⁵ s ≤ 10⁻⁴ s, so a full-depth cell is 28 bisections deep.
- **Projection.** The region's enclosure is the bounding box of the retained cells:

      [on_lo, on_hi]   = [min over retained cells of on_lo,  max of on_hi]
      [off_lo, off_hi] = [min over retained cells of off_lo, max of off_hi]

  If no cell is retained the run raises an error (the best-fit point always satisfies Loss ≤ Λ, so this cannot happen for a fit that reached this step).

**Widening by stamp uncertainty.** The commanded edges themselves are known only to the stamp half-widths, so

    on_lo ← on_lo − u_on,   on_hi ← on_hi + u_on,
    off_lo ← off_lo − u_off,  off_hi ← off_hi + u_off.

Example: pulse 0's on-stamp has *ma* − *mb* = 2.500019036233425e-7 s as executed in binary64 and *r* = 0.0000010000000000000002 s, so *u_on* = 1.1250009518116714e-6 s. Its reported onset region (under the earlier anchor noted above) is [0.014921970702173189, 0.017213039063451813] s and its offset region is [−0.012269482911167666, −0.009886278807582334] s: the instrument reported this pulse starting about 16 ms late and ending about 11 ms early, and the data rule out any onset outside a 2.3 ms-wide band around that.

The pulse's record retains the fitted shifts, the widened edge intervals, and, for a rejected pulse, its reasons; the repository artifact guide gives the exact record shape.

#### A.3.6 The calibration bound B_fiducial and validity

A pulse is **detected** when it passes every check of A.3.5 and so carries two widened edge regions; a pulse rejected at any of those checks is not detected and carries none. For every detected pulse and each of its two edges, take the **worst excursion** of that edge's widened region, max(|lo|, |hi|). The bound below is formed only when all 59 pulses are detected, so it always draws on exactly 118 values. Then

    B_fiducial = max over the 118 edge excursions  +  B_anchor

where *B_anchor* is the clock-anchor bound of A.3.3 for the same capture. The anchor term is added because the whole trace was placed on the wall clock from a single point whose error is independent of, and additive to, the per-edge fit error. Two diagnostics are also reported and are not used for any claim: the median of the 118 values — the mean of the 59th and 60th smallest, the count being even — and their 95th percentile, defined as the ⌈0.95·118⌉ = 113th smallest value.

Worked example (capture `20260722T145535-e941c821`, re-derived under the anchor estimator of A.3.3): *B_fiducial* = 0.030067931757111657 s, of which *B_anchor* = 0.0011349971959968978 s and the difference between the two printed bounds is 0.0289329345611147592 s (28.9 ms). That difference is what the two published numbers give when subtracted; it is not itself the value the code retains for the worst edge excursion, which is computed and stored separately.

The evidence file is marked `valid` only if all of the following hold: every one of the 59 pulses is detected; the spurious-plateau count is 0; every region limit is finite; the pulse count equals the protocol's 59; the raw record stream and `events.jsonl` both carry 64-hex-character SHA-256 digests; a capture wall time is recorded; the projection completed within budget (next section); and all ten binding fields are present and non-empty (`hardware_model`, `os_build`, `powermetrics_sha256`, `sampling_interval_ms`, `anchor_method_version`, `mlx_version`, `pulse_protocol_id`, `power_policy`, `estimator_revision`, `protocol_sha256`), whose hash pins the calibration to one machine, operating system build, instrument binary, and protocol. Otherwise the status is `invalid` and the reasons are listed from a closed vocabulary; a numerical bound may still be printed in an invalid file (for example when the detection succeeded but a binding field is missing), and it then has no standing. The pulse portion of the calibration bound is the largest of 118 observed onset and offset excursions from 59 commanded pulses in one capture; the clock-anchor allowance is then added. Because those pulses share one capture and independence across pulse order and between onset and offset errors has not been shown, this value is an observed sample maximum, not a “95/95” population-coverage bound. It is not a deterministic out-of-sample guarantee.

#### A.3.7 The work budget and the 120 s work clock

The branch-and-bound of A.3.5 must terminate on a flat loss surface. Two shared limits bound it — a cell budget and a wall-clock budget — whose constants and exhaustion behaviour are in the repository artifact guide.

**Origin of the 120 s work clock.** The clock starts at the moment the budget object is created, which is inside the detection routine immediately after the baseline set, *b*, and σ have been computed and immediately before the first pulse's fit begins. It is a monotonic-clock reading, not a wall-clock one, and it is not reset between pulses. It excludes the anchor estimation, trace anchoring, trimming, and schedule authentication of A.3.3–A.3.4, all of which finish before the budget exists.

#### A.3.8 Retained calibration corpus (2026-07-22 to 2026-07-25 instrument-validation captures), diagnostic, not campaign data

These are the 17 per-capture \(b_{\mathrm{fiducial}}\) bounds used by the n17
acceptance generation, not pre/post differences. Values reproduce the retained
decimal strings in the retained calibration acceptance file
`configs/calibration/calibration_acceptance_d079_v2_n17_r3.json` (registry
source S17).

| Capture member | \(b_{\mathrm{fiducial}}\) (s) |
|---|---:|
| `20260722T145535-e941c821` | 0.030067931757111657 |
| `20260722T194118-9dc0749d` | 0.027365018417518542 |
| `20260722T214220-1acdbbc0` | 0.03289849371536248 |
| `20260722T215127-eeef661a` | 0.02317490442656863 |
| `20260722T232509-82642517` | 0.028744604461883507 |
| `20260723T023058-8732d1c9` | 0.025549688302808828 |
| `20260723T052051-d9358c8a` | 0.026112736870656926 |
| `20260723T194632-d04e038e` | 0.025120423355537637 |
| `20260723T195730-bc4ba14a` | 0.025462798878078775 |
| `20260723T221449-e9ae755e` | 0.027201280356104838 |
| `20260723T223406-314f6d9e` | 0.025993442258292716 |
| `20260724T014109-57844352` | 0.02562670977988252 |
| `20260725T005132-a64711b7` | 0.02366861961761718 |
| `20260725T011533-0b5ec77c` | 0.029273357215668885 |
| `20260725T022712-0a9534f5` | 0.028733193582380412 |
| `20260725T030533-d3f076e5` | 0.026415695490612106 |
| `20260725T060617-97c5cba6` | 0.02501695592329986 |

### A.4 Executable verification order

The step-by-step verification order (release manifest, code and plan bytes, custody, calibration replay, characterization issuance, contrast verdict) is operator procedure, not mechanism, and now lives in the artifact guide, `docs/paper/artifact-guide.md` Section 11, "Executable verification order". Each step there names the command, the artifact it reads, and the field it compares.

### A.5 Interpreting a refusal

A matching refusal is a reproduced result, not a failed replication. Given identical bytes and a fixed plan, the program should emit the same reason name. A different reason, a different admitted member set, a changed phase energy or pulse bound, or a changed final verdict is the discrepancy to report.

A refused contrast does not show equality. It says the named instrument and evidence cannot adjudicate that difference: the effect may be absent or may lie below what the cell resolves. Failed and interrupted occurrences remain in the archive, while replacements are named separately; therefore extra directories are expected and must never be treated as admitted merely because they exist.

### A.6 Release locators

<!-- BUILD AFTER RELEASE. [FILL:DS-34] — “Repository and archive locators are
omitted: the release checklist has not issued the registered locator set
(registry row DS-34).” Only after that row is fillable may it supply the
repository revision, evidence-archive locator, and fingerprint-manifest
locator. Until then, state that the evidence-dependent commands cannot support
independent re-reduction. Release does not remove the pulse-to-inference
transfer assumption. -->

## First-use audit ledger

The first-use test was rerun over the final successor text. For each term below,
the first reader-facing use either builds it from physical inputs, glosses it in
plain words, or occurs only inside a build note that orders the definition
first. The audit excludes literal field names and reason names inside quoted
omission sentences: they identify a registry row and do not assert a mechanism.

| Term checked | First reader-facing home | Definition or disposition |
|---|---|---|
| large-language model / LLM | Title | Full phrase precedes the abbreviation. |
| prompt processing / prefill | Section 2 | Prompt work through the first output token; shorthand follows the phrase. |
| token generation / decode | Section 2 | Later output-token emission; shorthand follows the phrase. |
| sampling record | Section 2 | One average-power record covers one stated start-to-end interval. |
| phase boundary | Section 2 | Runtime-recorded time separating prompt processing and token generation. |
| `powermetrics` | Section 2 | macOS built-in sampler emitting CPU, GPU, and neural-engine interval averages. |
| SHA-256 fingerprint | Section 2 | Digest identifying exact file bytes. |
| pulse plateau | Section 2 | Flat high-power portion of a commanded pulse. |
| monotonic clock | Section 2 | Counter that advances but is never corrected to civil time. |
| \(B_{\mathrm{fiducial}}\), \(b\), and minimum allowance | Section 2 bracket | One-capture pulse-plus-anchor bound, distinct window operative bound, and 9.724-ms lower allowance; formula and 25/29-ms example are printed together. |
| stage / block member | Figure 2 text | Back-to-back declared run group / one of the four individual runs in an A/B/B/A block. |
| energy family / whole-window allowance | Figure 2 text | One energy definition and the once-added maximum of named reference excursion and repeatability bound. |
| record clipping | Section 4 opening | Keep the record time inside a phase and multiply by its average power; the 30-W, 100-ms example is worked. |
| cell | Section 4 | Runs sharing phase, workload, model, hardware, software, and power definition. |
| absolute / comparative component | Section 4 | Same-model repeated-run spread / A/B/B/A block-difference spread. |
| admitted energy / independent unit | Section 4 | Energy passing Section 5 entry checks / one run for absolute or one block for comparative. |
| point-only unguarded bound | Section 4 | Complete component formula at recorded points before multiplier and allowance. |
| sample standard deviation / Student-\(t\) prediction amount | Section 4 | Printed \(n-1\) formula and 97.5% small-sample prediction term. |
| corner | Section 4 | One joint lower-or-upper endpoint choice for every admitted interval. |
| independent-edge ratio \(R\) / dominates | Section 4 | Complete corner bound divided by matching point bound; “dominates” means \(R\ge2\). |
| authenticated / unauthenticated | Section 4 | SHA-256 fingerprints and named input agreement are present / a required fingerprint, match, or check is absent. |
| registered rounding | Section 4 pilot arithmetic | Rounding fixed before collection in plan bytes identified by a SHA-256 fingerprint. |
| shared / local edge movement and \(R_{cm}\) | Section 4 replay | One common shift for all four block members versus remaining member-specific movement; replay quotient and two-block fixture are printed. |
| member-envelope integral sum / binary64 padding | Section 4 replay | Coefficient-weighted four-trace integral / 64-bit float format, `ulp(1.0)`, scale \(M\), pad formula, 103.0615-J worked value, and four outward steps. |
| `not_applicable` absolute \(R_{cm}\) | Section 4 replay | Uniform shared shift cancels when the absolute formula subtracts its cell mean. |
| resolution bound / cell floor | Section 4 safeguards | Largest false difference the cell permits / maximum of its guarded components. |
| small-sample multiplier \(g(n)\) | Section 4 safeguards | \(\max(1,\sqrt{9/(n-1)})\), derived from 10-unit versus observed residual degrees of freedom; unavailable below five. |
| reference-trajectory excursion / issued repeatability bound / \(A_k\) | Section 4 safeguards | Largest-minus-smallest opening/midpoint/closing reference means / retained `replicated_endpoint_bound_j` or `single_member_endpoint_bound_j` / their maximum, with a 10.0/10.6/10.2-J example. |
| raw probability / Holm correction | Section 4 gates | Two-sided Student-\(t\) tail probability from ten block differences; ordered 0.025 then 0.05 procedure. |
| measurement interval / decision interval / deterministic bound | Section 4 gates | Total-standard-error interval / that interval extended by authenticated non-random maximum displacements, whose per-kind calculation and 0.25-J example are printed. |
| not resolvable | Section 4 gates | Estimate does not clear the cell floor; it is not zero. |
| signed clearance or shortfall | Section 4 gates | Absolute estimate minus cell floor, with a 10.0 − 3.0484-J example. |
| outcome A, outcome B, and refusal | Section 4 close-out | All ratios pass / every ratio evaluable with one below 2 / missing, unauthenticated, or zero-denominator ratio selects neither and stops filling. |
| inserted-gap check | Section 4 close-out | Approximately 500-ms no-work gap with independently known edges compared against the power record. |
| fail-closed | Section 5 | Missing or inconsistent evidence stops and records why. |
| freeze receipt | Section 5 | Record fixing plan bytes and the time those bytes were frozen. |
| G2-a / hash-bound / prompt pin | Section 6 results lead | Fixed prompt-length shakedown / SHA-256-bound selection record / retained prompt text, token IDs, tokenizer, and generation rules. |
| record support / IQR / resolvability | Section 6 negative build | Record start-to-end interval / middle-half spread of sorted values / at least three supports must overlap the phase. |
| reducer | Section 6 selection passage | Program turning a retained run bundle into phase energies. |
| Running Average Power Limit / RAPL | Related work | Processor-exposed energy counter; full phrase precedes the abbreviation. |
| NVIDIA Management Library / NVML | Related work | Software power counter; full phrase precedes the abbreviation. |
| fiducial | Appendix A.3.2 | Commanded reference edge timed independently of the instrument. |
| set membership | Appendix A.3.3 | Complete set of clock mappings consistent with every constraint. |
| accepted region | Appendix A.3.5 | All pulse-edge pairs whose loss remains within the fixed limit. |
| observed sample maximum | Appendix A.3.6 | Largest of the 118 observed edge excursions; no population-coverage label. |

The audit also searched the successor text for the retired campaign tag,
retired model family, retired fixed-prompt labels, the false between-record
pause mechanism, and the retired any-exceedance falsifier. Any occurrence is
a failure. Terms the final first-use audit could not build: none.
