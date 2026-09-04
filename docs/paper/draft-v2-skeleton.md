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

<!-- BUILD NOW — source: results-fill-registry V5-ID-001/002 and V5-WL-001–005; reviewer C4; magistrate R-B2. Physical mechanism, research question, and frozen pins are written now; only measurement-dependent values retain registered omissions. -->

This capstone asks a measurement question before it asks a model-comparison
question. macOS `powermetrics` is the power sampler used here. A sampling record
is one sampler output that averages processor power from its recorded
start time to its recorded end time. A phase edge is the runtime time that
divides one part of an inference request from the next. The record's integrated energy,
the time integral \(\int P(t)\,dt\) of power over that record, moves from one
phase to the other when the edge moves within the record even though the
request total stays unchanged.

Prompt processing reads the prompt through production of the first output
token; this paper calls it *prefill*. Token generation emits the later output
tokens; this paper calls it *decode*. Repeating the same request can narrow
ordinary run-to-run scatter, but it cannot remove a shared boundary
displacement: if every repeat assigns the same slice of one record to the
wrong phase, averaging repeats preserves that reassignment.

JouleWise therefore calibrates edge placement inside each measurement window,
one uninterrupted measurement session, with commanded GPU pulses. It also uses
a rate-aware clock mapping: rather than assuming the computer's wall clock and
its never-adjusted monotonic clock advance at exactly the same rate, it places
each wall-clock reading between the monotonic-clock readings taken immediately
before and after it. Those are the bracketed readings; the method retains every
fixed-rate, offset mapping that they and the power-record labels permit. The
calibration and mapping bound how far an edge may move before phase energy is
recomputed.

A cell is the set of runs with one phase, workload, model, hardware, software,
and power-counter boundary. Its resolution bound is the largest false
phase-energy difference allowed by the fixed calculation for that cell. The
research question is whether permitted edge movement at least doubles each
source of false difference. Let \(U_{\rm point}\) be a bound calculated at the
recorded edges and \(U_{\rm edge}\) its counterpart after allowed movement.
Any required \(U_{\rm edge}/U_{\rm point}<2\) falsifies the claim, under either
independent or shared movement; equality passes. Ordinary \(R\) moves every
member's edges independently. Comparative \(R_{cm}\) instead replays one shared
timing-error sign across every A/B/B/A block plus one local sign chosen
separately for each block. In plain terms, the question is whether uncertainty
about where the phase starts or ends is at least as large as the ordinary
variation already present in the repeated measurements.

The fixed demonstration compares the small model `qwen3-1p7b`, revision
`3b1b1768f8f8cf8351c712464f906e86c2b8269e`, with the large model `qwen3-8b`,
revision `545dc4251c05440727734bcd94334791f6ab0192`. <!-- V5-ID-001; V5-ID-002 -->
Its token-generation workload is the ordered eight-prompt `real_prompts_v1`
set, whose prompt-set SHA-256 fingerprint—an identifier of exact file bytes—is
`20debdb41eb4983339a160176dcf4e475153b5d6f16b1ef3ada39447e99f3474`. <!-- V5-WL-001 -->
Both conditions use the same `tokenizer.json` SHA-256
`aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` and the
same applied chat-template—the formatter that turns a prompt into model input—
whose SHA-256 is
`87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5`, with
reasoning disabled. <!-- V5-WL-002; V5-WL-003 --> Greedy generation—choosing
the highest-probability next token at every step—forces 512 output tokens for
one rendered prompt in each run. <!-- V5-WL-004 --> G2-a is the fixed
candidate-length selection step, and a prefill prompt pin is its record fixing
the selected prompt and generation inputs. The selected prefill prompt pin is omitted: its G2-a-bound `joulewise.prefill_prompt_pin.v2` record has not issued. <!-- [FILL:V5-WL-005] — The selected prefill prompt pin is omitted: its G2-a-bound `joulewise.prefill_prompt_pin.v2` record has not issued (registry row V5-WL-005). -->
This fixed pair demonstrates the decision rule; it is not a scaling experiment.

The short-prefill question is narrower: when prompt processing is brief, do
enough sampling-record intervals overlap it to support a phase reduction—that
is, computing separate phase energies from the overlapping sampler records? A
failure of the fixed three-record minimum is a measurement refusal, a no-result
stop rather than evidence of zero prompt-processing energy or a model
comparison.

## 2. In-window calibration method

Prompt processing (*prefill*) reads the prompt through the first output token; token generation (*decode*) emits later output tokens. A phase boundary is the runtime-recorded time separating those phases. macOS's built-in power sampler, *powermetrics*, emits one record containing the CPU, GPU, and neural-engine average power over one shared start-to-end interval; JouleWise assigns that sampling record to a phase using the boundary and multiplies each channel's average power by the part of the interval in that phase. A phase boundary is therefore a separate measurement problem from repeatability. If a boundary is placed a few tens of milliseconds late while power falls by tens of watts, power multiplied by misplaced time assigns about a joule to the wrong phase. The request total does not change: energy removed from one phase is added to the other. Repetition can reduce random scatter, but it cannot remove this systematic reassignment.

Figure 1 shows interval-average power around the recorded boundary between prompt processing and token generation, with the allowed boundary positions marked as a band. The hatched area is the energy reassigned between phases when the boundary moves across that band; the request total does not change.

![Figure 1. Boundary-attribution mechanism.](figures/fig1_boundary_attribution.svg)

*Figure 1. Boundary-attribution schematic. Every value is illustrative, including both axes, the sampler interval, timing band, power step, and approximately one-joule product. The power-versus-time axes and pale grid frame gray interval-average rectangles and a dashed idealized-power trace; lower bars name prefill and decode. A black vertical line marks the runtime-recorded boundary, a blue band its calibrated timing bound, and a hatched sliver the energy reassigned by a boundary shift. Horizontal and vertical double-headed arrows name the sampler interval and power step; a blue callout arrow points to the sliver. The notes and legend explain the high- and low-power regimes, the blended boundary sample, the unchanged request total, and every mark.*

### Bracketed pulse-train algorithm

Immediately before and after each science window—one uninterrupted measurement session—JouleWise records a calibration under the same declared machine state. Its recorded SHA-256 values, which identify exact file bytes, must match the fixed record; its timestamps must place it before the first or after the last science run and no more than 24 hours from the window's far end. After three warm-up pulses, which are discarded, it commands 59 one-second GPU matrix-multiplication pulses on preallocated \(4096\times4096\) 16-bit floating-point matrices. A fixed base-two varied-gap schedule—gaps stepping through powers of two—prevents the pulse edges from repeatedly lining up with the requested 100-ms sampler cadence. Five seconds of quiet trace (no commanded pulse) are requested on both sides of the train, of which at least 4.5 s must be present.

For each commanded pulse, the detector estimates resting GPU power from samples outside the fixed time margin around every pulse and pulse height from samples wholly inside its flat high-power portion, called the plateau. It predicts each reported interval average from the fraction of that interval covered by a shifted rectangular pulse, then scores the difference between predicted and observed power with a rule that limits the influence of one large discrepancy while moving the onset and offset separately. After finding the best pair, it encloses every pair close enough to that fit: a rectangle is rejected only when a mathematical lower bound proves that none of it can pass, and every surviving rectangle is split to a fixed resolution. The four outer edge values are widened for uncertainty in the two command timestamps. A capture is refused unless all 59 pulses pass the signal, fit, range, trace-coverage (the captured trace extends through the fixed margin on both sides of every pulse), and completeness checks; no uncommanded plateau appears; and the shared search-work limits remain unexhausted. The accepted capture bound is the largest allowed edge displacement among all pulses plus the trace's clock-anchor bound, the uncertainty in placing the trace on wall-clock time, built next.

The clock anchor uses five wall-clock readings, each bracketed by readings from a monotonic clock—a counter that advances but is never corrected to civil time—together with every whole-second label embedded in the native power records. It retains the complete set of straight-line clock mappings whose rate, offset, first-record endpoint, stamp brackets, native labels, and launch-to-first-parse ordering agree. The method permits the two clocks to run at slightly different fixed rates and charges the full allowed departure of a native label from that line. It refuses missing or malformed inputs, an empty set or an unbounded one (the allowed rate reaches the edge of its search box), inadequate capture span, implausible clock rate, active automatic network-time correction, or a bound outside the accepted range. Otherwise it finds the earliest and latest allowed first-record endpoint and adds four separately named allowances. This corrected rate-aware model replaced the false equal-rate assumption, which could move every fitted edge in the same direction.

Finally, the pre-window and post-window capture bounds form a bracket. The calibration policy derives two constants from its retained 17-capture corpus. Student-\(t\) is a small-sample bell curve whose 99% quantile—the two-sided 99% point, written \(t_{0.995,16}\) because it leaves 0.5% in each tail with 16 degrees of freedom, and larger than the normal curve's because the spread is estimated from only 17 captures—sets the maximum permitted pre/post difference. For \(n=17\) per-capture bounds, the sample standard deviation (the \(n-1\) formula of Section 4) is \(s_b = 2.460856\) ms (unrounded, \(2.460856207694636\) ms) and \(t_{0.995,16}=2.92078162242509999197\); the two-draw rule—two fresh capture bounds are drawn, and the spread of their difference is \(\sqrt{2}\) times one capture's spread—so \(t_{0.995,16}\times s_b\times\sqrt{2}\) records \(10.164834757777545\) ms, printed as the \(10.164835\)-ms maximum permitted pre/post difference. The separately retained **minimum allowance** starts from the corpus range, \(9.723589288793850\) ms, rounded to the nearest microsecond, with an exact tie going to the even digit (`ROUND_HALF_EVEN`), giving \(9.724\) ms; Appendix A.3.8 prints the 17 bounds from the retained calibration acceptance file `configs/calibration/calibration_acceptance_d079_v2_n17_r3.json` (registry source S17). The minimum prevents two numerically matching captures from erasing the finite change allowance fixed from that corpus. A larger difference refuses the window. Appendix A.3.6 calls one capture's pulse-plus-anchor bound \(B_{\mathrm{fiducial}}\). The window's distinct **operative timing bound** \(b\) is the larger capture bound plus \(\max(|B_{\mathrm{post}}-B_{\mathrm{pre}}|,9.724\ \mathrm{ms})\), added once. For example, a 25-ms pre-window bound and a 29-ms post-window bound differ by 4 ms, pass the 10.164835-ms limit, and give \(b=29+\max(4,9.724)=38.724\) ms. If the post-window calibration widens a bound already used, the affected phase energies are recomputed with the wider bound or refused. Appendix A.3 formally defines the complete sets of pulse-edge positions and clock mappings that satisfy every fixed constraint, along with objectives, ranges, and refusal conditions.

Commanded GPU pulses calibrate edge placement, but applying that bound to sustained mixed inference is an assumption. The before-and-after bracket tests for change across the measurement window; it does not test whether the pulse-derived bound applies to inference.

Figure 2 orders the before-and-after pulse calibrations, entry check, reference runs, and science blocks within one measurement window. A **stage** is one declared group of runs measured back-to-back inside that window. Each science block uses A/B/B/A order—condition A, condition B, condition B, condition A—and names its four **members**, meaning its four individual runs, \(A_1,B_1,B_2,A_2\) in that order. Its block difference is \((B_1+B_2-A_1-A_2)/2\); a positive value means condition B used more energy than condition A. Matching the average run time of the two A members to that of the two B members cancels steady linear drift. Curvature remains covered by a separately measured **whole-window allowance**: one joule amount for each **energy family**, a group reduced under one energy definition such as gross energy or idle-subtracted energy, later added once to its component bound, equal to the larger of the **reference-trajectory excursion**—the spread among the mean energies of the opening, midpoint, and closing reference runs (largest minus smallest)—and that family's **issued repeatability bound**—a repeatability bound on reference-run energy issued from an earlier retained window, not re-estimated in this one.

![Figure 2. One measurement window and the drift-cancelling A/B/B/A order.](figures/fig2_window_timeline.svg)

*Figure 2. Schematic structure of one measurement window. The upper session-time arrow orders the pre-calibration, admission gate, three opening references, two groups of A/B/B/A science stages around one midpoint reference, three closing references, and post-calibration. The blue spanning bracket joins the two pulse trains; the lower inset's axes, dashed drift line, four A/B/B/A circles, common-time line, and averaging brackets show why steady drift cancels while curvature (drift that bends rather than runs straight) still requires the measured whole-window allowance defined above. Stage widths are not to scale, and no measured value is shown.*

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

<!-- Source: characterization_result_schema_v1; reviewer D3 and C5. -->

Instrument characterization asks four physical questions before any campaign
result may rely on the instrument. Does energy change with the amount of work
in the planned way? Under identical conditions, do repeated paired blocks stay
inside a comparator—an upper limit fixed from earlier, disjoint evidence? Do
the two phase energies account for their enclosing request without leaking dependence across the phase boundary, meaning without prompt-processing energy
changing with work performed after prompt processing ended? And do held-out
reference probes, kept out of the allowance calculation, remain inside the
drift allowance—the maximum within-window change assigned from its designated
references—while the machine recovers within the declared settling convention,
its fixed maximum recovery time? An admitted bundle is a run allowed into the
calculation because it passed its frozen entry and evidence checks.

For workload response, an independent unit is one separately admitted bundle,
not one sampler record within it. A workload-response slope is the fitted
change in energy per output token. A fitted residual is one observed energy
minus the straight-line value predicted for its output length. The residual
must fit both the bundle's allowed timing half-width and a floor issued earlier
for that same cell.

For one A/B/B/A block, let
\(\delta=(B_1+B_2-A_1-A_2)/2\). Each of the four member energies has a
point-only value at its recorded edge and an edge-moved allowance
\([A_1^L,A_1^U]\), \([B_1^L,B_1^U]\), \([B_2^L,B_2^U]\), or
\([A_2^L,A_2^U]\). Evaluate \(\delta\) over the fixed set of allowed endpoint
combinations and retain the interval of allowed differences
\[
I_i=[\delta_i^-,\delta_i^+]
=\left[
\frac{B_1^L+B_2^L-A_1^U-A_2^U}{2},
\frac{B_1^U+B_2^U-A_1^L-A_2^L}{2}
\right].
\]
The mean interval over the five null-test blocks is
\(I_{\rm mean}=[\sum_i\delta_i^-/5,\sum_i\delta_i^+/5]\). Let
\(C=[-m,+m]\) be the earlier comparator, where \(m\) is its positive joule
endpoint, and define the largest absolute allowed block difference as
\[
M=\max_i\max(|\delta_i^-|,|\delta_i^+|).
\]
No issued null-ladder member endpoints are available, so this construction is
symbolic rather than measured. The forcing problem is that a point value can
hide an allowed nonzero difference, while a mean can hide blocks moving in
opposite directions. The containment test therefore requires every \(I_i\) to
contain zero, then requires \(I_{\rm mean}\subseteq C\) and \(M\le m\).

Here is a numeric illustration, not measured evidence: its comparator is
\([-3\ \mathrm{J},+3\ \mathrm{J}]\), and its five block intervals, all in
joules, are \([-2,+2]\), \([-1,+1]\), \([-0.5,+0.5]\),
\([-1.5,+1.5]\), and \([-1,+1]\). For this numeric illustration, the
lower endpoints sum to \(-6\) J and the upper endpoints to \(+6\) J, so
\(I_{\rm mean}=[-1.2\ \mathrm{J},+1.2\ \mathrm{J}]\) and \(M=2\) J.
Every displayed check passes. If, still only as an illustration, the fifth
interval were \([+0.5\ \mathrm{J},+2.5\ \mathrm{J}]\), it would remain
inside the comparator but exclude zero, so that block would fail the first
containment check even though its mean interval would be inside the comparator.

```text
comparator C       [-3 J==========================+3 J]
first block I_1    |    [-2 J----------------+2 J]    |
second block I_2   |      [-1 J------------+1 J]      |
third block I_3    |       [-0.5 J--------+0.5 J]      |
fourth block I_4   |     [-1.5 J----------+1.5 J]     |
fifth block I_5    |      [-1 J------------+1 J]      |
mean interval Ibar |     [-1.2 J----------+1.2 J]     |
```

Diagram legend: `C` is the earlier comparator band; `I_1` through `I_5` are the
five illustrative allowed-difference intervals; `Ibar` is their mean interval;
`|` marks the comparator band's left and right boundaries on each block row;
`=` spans the comparator; `-` is a schematic connector for a block or mean
interval and is not drawn to a numerical scale; and square brackets mark
included endpoints. The endpoint labels carry the numeric values. Five
measured blocks leave every unmeasured block and the population distribution
unknown, so a pass establishes only
measured-block containment, never population coverage.

For phase accounting, the residual
\(D=E_{\rm prefill}+E_{\rm decode}-E_{\rm request}\) is the signed energy left
after subtracting the enclosing request from the two phase energies. A positive
value is double-counted energy. A negative value may be energy in the unphased gap,
the recorded interval between the end of prefill and the start of decode;
its duration times its largest recorded package power bounds what may be
missing. A resolution band is the symmetric allowed slope range made from one
admitted prefill half-width across the observed output span. A floor band is
the analogous range made from an independently issued prefill floor. The
shared session timing term is the one bracket-capture timing bound common to
all session members; member-local timing is each run's own local and edge-span
contribution. Timing flags mark a member whose clock bound exceeds a quarter
of its window, while sampling flags mark cadence below its fixed ratio or too
few in-window sampler records.

For drift and recovery, reference roles identify the allowance-building runs
at the window opening, midpoint, and close and distinguish the held-out probes
that cannot enter that allowance. A passing cooldown exit is the first gate
evaluation after a sustained workload whose complete thirty-second rolling
window has at least eighty-percent duration coverage, duration-weighted mean
power no greater than one-and-one-tenth times the clean reference, and nominal
thermal pressure; elapsed recovery time starts when the sustained workload
ends and stops at that first pass.

| Question | Calculation and fixed comparison | Independent unit, minimum basis, and refusal consequence |
|---|---|---|
| Workload response | Complete every registered (fixed-before-collection) workload level; fit whole-request and token-generation energy against output length; require the lowest allowed slope to be positive and the largest departure from the fitted line to fit both one admitted bundle's timing half-width—half its allowed timing range—and an independently issued floor for that same cell. | The unit is an admitted bundle. The slope and residual checks require forty admitted bundles, and the level-completeness check requires all five levels. Failure withdraws the affected per-token conversion; a response may then be reported only at its individual workload levels. |
| Identical-condition response | At every registered workload magnitude, form each A/B/B/A block's interval of allowed differences. Every interval must contain zero; the mean interval and largest absolute block difference must also fit inside the earlier comparator. | The unit is an A/B/B/A block. The frozen ladder requires all three magnitudes. At each magnitude it requires five `null_test` blocks when an issued comparator floor for that cell exists and its evidence is disjoint; otherwise it requires ten blocks: five `floor_train` blocks to build the comparator and five disjoint `null_test` blocks. A failed block or comparator check withdraws that cell's floor from claim use, so every contrast using it becomes not resolvable—that is, too small to clear its false-difference bound—until the floor is re-derived. |
| Phase accounting | Compare the sum of the two phase energies with the enclosing request, allowing no positive double count beyond numerical rounding and no negative residual larger than the retained unphased gap can contain. Test whether prompt-processing energy stays inside both a resolution band and an earlier floor band as later output changes; keep the shared session timing term separate from member-local timing; require both bracket captures to lie in their registered band and no claim-bearing admitted member to carry the timing or sampling flags. | The main checks use admitted bundles and require at least twenty-four; the bracket check requires two captures, and the floor-label check requires every floor cell. Failure withdraws or narrows phase-specific claims: affected members become diagnostic, and an accounting failure narrows the result to request-total energy. |
| Drift and recovery | Construct the drift allowance from its designated references, then test it only with held-out reference probes; require each probe's deviation to fit within that allowance. Separately measure time from a sustained workload to the first passing cooldown exit and compare it with the fixed settling convention. | Reference roles must be fixed for at least six reference members; containment needs at least three held-out probes, and recovery needs at least three sustained-hold/cooldown pairs. A containment failure re-derives every floor carrying that allowance; a recovery failure raises the settling interval in a successor policy and re-examines windows collected under the old one. |

The workload-response slope has a special exact calculation because choosing a
lower or upper endpoint independently for forty energies appears to require
\(2^{40}\) joint combinations. Ordinary least-squares fitting chooses the
straight line whose squared vertical departures from the observed energies are
smallest. With fixed output levels, its slope is a fixed weighted sum,
\(\hat\beta=\sum_i w_iE_i\), of the forty energies. Each energy has an allowed
lower endpoint \(L_i\) and upper endpoint \(U_i\). To obtain the smallest
allowed slope, use \(L_i\) wherever \(w_i>0\) and \(U_i\) wherever \(w_i<0\);
to obtain the largest, reverse those choices. A zero weight changes neither
result. Thus the positive-slope screen at its fixed zero threshold—the
numerical cutoff the slope must exceed—needs two endpoint vectors, not all
\(2^{40}\) combinations. <!-- C1.2/C1.3: fixed forty-bundle design and zero threshold; reviewer D3 -->

An illustrative three-term excerpt, not measured data, uses weights
\((-2,0,+2)\ \mathrm{token}^{-1}\) and allowed energy intervals
\([0,2]\), \([2,16]\), and \([16,24]\) J. The minimum chooses \(2\)
for the negative-weight term, either endpoint for the zero-weight term, and
\(16\) for the positive-weight term. For this numeric illustration, the
minimum is \(-2(2)+2(16)=28\) J per output token and the maximum, after
reversing those endpoint choices, is \(-2(0)+2(24)=48\) J per output
token. The forty-member calculation applies that same sign rule to every real
weight.

```text
allowed endpoint pair [L_i, U_i]
              | w_i < 0  --> minimum U_i; maximum L_i
weight w_i ---| w_i = 0  --> either endpoint; contribution unchanged
              | w_i > 0  --> minimum L_i; maximum U_i
```

Diagram legend: `[L_i, U_i]` is one energy's allowed endpoint pair; `w_i` is
its fixed least-squares weight; the three branches are negative, zero, and
positive weight signs; `-->` maps a sign to its endpoint choice; and “minimum”
and “maximum” name the two slope vectors being constructed.
This shortcut does not apply to the separate corner calculation: it
recalculates a mean and sample standard deviation at every joint endpoint
choice. Changing one endpoint changes both quantities and the largest
residual, so this nonlinear calculation refuses exact enumeration above sixteen
observations.

The identical-condition result therefore has a deliberately narrow meaning:
five contained measured blocks establish only the containment drawn above. It
neither estimates a percentage of a wider population nor supplies an
independent coverage guarantee. <!-- reviewer C5: containment caveat -->

An authenticated report is one whose expected evidence fingerprints and named
inputs agree. The workload-response characterization result is omitted: its
named supplier is an unissued authenticated report. <!-- [FILL:DS-02] — “The workload-response characterization result is omitted: its named supplier is an unissued authenticated report (registry row DS-02).” -->
The identical-condition null characterization result is omitted: its named
supplier is an unissued authenticated report. <!-- [FILL:DS-03] — “The identical-condition null characterization result is omitted: its named supplier is an unissued authenticated report (registry row DS-03).” -->
The phase-accounting characterization result is omitted: its named supplier is
an unissued authenticated report. <!-- [FILL:DS-05] — “The phase-accounting characterization result is omitted: its named supplier is an unissued authenticated report (registry row DS-05).” -->
The drift-and-recovery characterization result is omitted: its named supplier
is an unissued authenticated report. <!-- [FILL:DS-06] — “The drift-and-recovery characterization result is omitted: its named supplier is an unissued authenticated report (registry row DS-06).” -->

### Pilot observations under the retired calculation

<!-- Source: results-fill-registry DG-044–DG-066; reviewer D2; magistrate R-B1. -->

These values are pilot evidence under the retired calculation, not a current
instrument property or campaign result. Point-only component bounds are the
components' false-difference limits with every phase edge left at its recorded
time. For prompt processing, token generation, and short prompt processing
respectively, they were 0.2888 J, 0.4934 J, and 0.3113 J.
<!-- DG-044; DG-045; DG-046 -->
Re-evaluating the complete component calculation at its jointly worst allowed
edge endpoints gave 3.153 J, 2.922 J, and 2.184 J. <!-- DG-047; DG-048; DG-049 -->
The corresponding independently moved-edge ratios—each worst-endpoint bound
divided by its point-only bound while every member edge may move separately—
were 10.92, 5.92, and 7.02. <!-- DG-050; DG-051; DG-052 -->

Across the thirty recorded timing members, the retained timing bound ranged
from 25.6 ms to 31.1 ms. <!-- DG-053; DG-054; DG-055 --> Those members are not
thirty independent timing draws, because repeated members can share timing
sources. <!-- DG-056 -->

The current named bracket screen—the minimum pre/post allowance retained from
the calibration corpus—is 9.724 ms. <!-- DG-059 --> The same screen is rendered
elsewhere as 0.009724 s, as a 9.724-ms reference, and again as 9.724 ms; these
are unit or prose renderings of that one screen, not separate sensitivity
results. <!-- DG-060; DG-061; DG-062 --> The superseded calibration corpus
contained nineteen captures; the current corpus contains seventeen.
<!-- DG-064; DG-065 --> Separately, the historical short-prefill diagnostic
population contained 50 bundles. <!-- DG-066 -->
<!-- ANCHOR-CORRECTION: awaiting registry decision -->

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
artifacts. A **same-cell floor** is that artifact for exactly the phase,
workload, model, hardware, software, and counter cell being tested. For
\(n\ge5\) independent units, first apply the fixed
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

The repository is tamper-evident for the operator's own benefit—a way to catch mistakes—not tamper-proof against another program or person. It assumes a single trusted operator, so its gates defend against error and post-hoc choice rather than an adversary; they provide internal consistency, not third-party provenance (evidence that would convince someone who does not trust the operator).

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
three-record minimum (a phase must overlap at least three sampler records
to be reduced at all) can gain or lose an overlapping record when its boundary
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
count floor of 5”—the registered minimum record count for a full-strength
result—beside the calculated result. This keeps a **reducer**
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

<!-- Source: docs/paper/round7/survival-map.md; reviewer items C9, D6, D7, D8, D9, D11; ranked items 12, 15, 16. -->

First, the pulse-to-inference transfer is untested. The calibration commands
long, square GPU work and measures how its reported edges differ from the
commanded edges, whereas inference has a different sequence of GPU work at the
transition from prompt processing to token generation. A difference in those
two physical edge responses could make the pulse-derived timing bound either
too narrow or unnecessarily wide; its effect on the reported phase energies is
unquantified. The retained diagnostic capture's pulse-derived bound was
\(0.030067931757111657\) s. <!-- DG-027; MEASURED / DIAGNOSTIC_ERA / REPLAY_FENCED. --> This is a calibration value, not a bound on real inference. The concrete closing check is the inserted-gap
experiment in the next subsection: command a no-work interval inside real
inference, fit both of its independently stamped edges, and compare the
largest absolute residual with the pulse-derived bound; an exceedance would
withdraw transfer rather than inflate the bound after seeing the result.

Second, the evidence covers one physical machine and one software/counter
boundary. The machine, operating-system build, inference framework, sampler,
and power channels are a single configuration, so a different chip, firmware,
software build, or sampler implementation could change the edge response, the
power scale, or both; the direction and size of that change are unquantified.
An independent reader could close this limit by repeating the complete
calibration, admission, workload, and analysis protocol on another Apple
Silicon machine and comparing the resulting transfer check, cell floors, and
contrast decisions under the same pre-registered workload.

Third, the reported joules come from internal CPU, GPU, and neural-engine
counter channels, with no external gain check. CPU, GPU, and neural-engine
power share the same start-to-end averaging window, so the same phase edges
clip all three channels before their energies are summed; no separate timing
bound for the CPU or neural-engine channel is issued. <!-- Reviewer D8; the channel-window answer is fixed by the Section 2 record definition. -->
An external power meter—a separate instrument measuring the machine's physical
input on the wall side of its power supply—could test whether the counter's
whole-request totals track physical energy over controlled loads. Without that
comparison, a gain error, meaning a mismatch between reported and physical
energy, could move the absolute and comparative joule values upward or downward
by an unquantified amount. Such a comparison would address this limit at
whole-request scale, but would not by itself validate a phase split. We report
joules rather than counter-internal units because watts integrated over seconds
give an interpretable energy quantity, while the
unmeasured gain means that quantity is validated only on the counter's reported
scale. <!-- Reviewer D7; ranked item 16. -->

Fourth, the ten blocks in one measurement window are not automatically ten
independent physical draws. Consecutive member runs inside a block share the same
local machine state, and blocks can share the calibration bracket, thermal
trajectory, background activity, neighbouring sampler behavior, and serial
change across the window; a deterministic allowance can widen an interval but
does not make those observations independent. Positive dependence would make
an independence-based repeat standard error and tail probability too small,
while its direction and size here are unquantified.

<!-- Source: docs/paper/round7/dependence-sensitivity.md; reviewer item D6; ranked item 15. -->
The sampling unit—the smallest observation treated as a separate draw—is one
complete A/B/B/A block, never one of its four member runs. For block \(i\),
\(d_i=(B_{i1}+B_{i2}-A_{i1}-A_{i2})/2\). The sensitivity calculation is

\[
\begin{aligned}
s&=\text{sample standard deviation of the complete block differences},\\
n&=\text{number of complete blocks},\\
V&=\text{variance multiplier supplied by the selected dependence model},\\
n_{\mathrm{eff}}&=n/V=\text{number of independent blocks with the same repeat standard error},\\
\nu&=\text{Student-}t\text{ degrees of freedom supplied by that model},\\
\mathrm{SE}_{\mathrm{repeat,model}}&=s\sqrt{V}/\sqrt{n}=s/\sqrt{n_{\mathrm{eff}}},\\
\mathrm{SE}_{\mathrm{total}}&=\sqrt{\mathrm{SE}_{\mathrm{repeat,model}}^2+
\mathrm{SE}_{\mathrm{metrology}}^2},\\
\mathrm{SE}_{\mathrm{metrology}}&=\text{the issued measurement standard error}.
\end{aligned}
\]

The registered independent-block model supplies \(V=1\),
\(n_{\mathrm{eff}}=n\), and \(\nu=n-1\). The AR(1) estimated-adjacency model,
which relates each block to the immediately preceding block, supplies \(V\)
from its finite sum over the estimated correlation between successive block
differences and uses
\(\nu=\min(n-1,\lfloor n_{\mathrm{eff}}\rfloor-1)\). The named fixed effective-
sample-size halving case supplies \(V=2\), \(n_{\mathrm{eff}}=5\), and \(\nu=4\).
Every model retains the issued \(SE_{\mathrm{metrology}}\) unchanged. The current
builder treats the A and B members as independent runs, so the covariance of
their stochastic measurement terms is zero. <!-- Pre-registered design/model
constants: docs/paper/round7/dependence-sensitivity.md:28-52; builder treatment:
joulewise/analysis_engine/__init__.py:588-603 and
joulewise/analysis_engine/estimators.py:350-371; not measured values. -->
If any member is absent, invalid, or not admitted, its contrast cannot enter
the registered claim procedure: the analysis uses no shortened set, outcome-
driven replacement, or top-up, and it does not calculate the registered result
unless all ten complete blocks are present. The A/B/B/A order counterbalances
straight-line drift and cancels it exactly only when the A and B time-midpoint
sums match; unequal runtimes or cooldowns break that balance. <!-- Source:
docs/paper/round7/dependence-sensitivity.md:6; reviewer D9; ranked item 16. -->
\(A_k\) is one family-level allowance for remaining across-window curvature
and repeatability added once to the component floor, so it is not an additional
member or block charge. Within-arm variation—variation among runs of the same A
or B condition—can manufacture an apparent paired difference; ordering does not
remove it. <!-- Reviewer D9; ranked item 16. -->
The identical-condition null passage covers only its five observed blocks. It
establishes neither population coverage nor equality, and that structural limit
would remain after an authenticated result issued. <!-- DS-03; KEY_FROZEN /
VALUE_UNISSUED. Five-block design: docs/contracts/analysis_plans.md:380-381;
reviewer D11; ranked item 16. -->
The exact closing check is to retain all blocks in collection order, rerun the
registered independent-block calculation and every pre-registered dependence
sensitivity model, and compare their total standard errors, degrees of freedom,
intervals, and direction gates without changing the member set.

Fifth, the final cell floor is not yet independently re-reducible. An outside
reader cannot presently rebuild every admitted member and every allowed timing
width from the primary bytes, verify that the same members and widths reached
the floor artifact, and then replay the claim gates; an omitted member,
substituted width, or stale derived file could therefore change the reported
floor in an unquantified direction. The concrete closing evidence is a released
archive and its file-fingerprint list plus a re-reduction that reconstructs
those members and widths from primary bytes, byte-compares the complete set
with the floor artifact, and refuses before analysis on any mismatch; this
limit remains open until that check is available. <!-- DS-34; SUPPLIER_UNKNOWN; no release locator issued. -->

Sixth, the provenance is trusted-operator rather than adversarial. The hashes
and refusal records can expose an accidental edit or inconsistent derived file,
but an operator who controls acquisition, hashing, and analysis could replace
the primary files and recompute the records consistently; the possible effect
on any reported value is therefore unquantified and could favor a claimed
contrast. A reader could close this limit only with independently held
acquisition evidence—for example, a separate operator or laboratory retaining
append-only, signed raw records and comparing them with the analysis archive—so
that the person producing the claim cannot rewrite the evidence and its
fingerprints alone.

### Future work

<!-- Source: docs/paper/round7/survival-map.md; reviewer items C1 and M1; ranked item 16 / TRANSFER-FIDUCIAL-01. -->

<!-- BEGIN TRANSFER-FIDUCIAL-RUNNABLE -->
The inserted-gap study is a registered and runnable diagnostic protocol—a
study that tests the timing method but supplies no scientific result, detection
threshold, or claim—that this paper has not run. Its
generator imports the small-model identity—the exact model name, revision,
tokenizer fingerprint, and formatting-template fingerprint—from the campaign generator, binds
the exact prompt selected for that campaign, and emits the registered set of
ten otherwise identical configurations with a 0.5-s commanded sleep. <!-- Run
count and gap: T26 paper-goal ruling item 16 and
docs/process/state_kernel.json:/tasks/TRANSFER-FIDUCIAL-01; campaign binding:
configs/campaigns/d117_transfer_fiducial_v5/generate_configs.py. -->

The sleep-actuation problem is that the runtime's first output yield—the moment
the generator returns its first output item—can arrive while a decode step is
already queued on the graphics processor. The executable
choice is to take the gap-start command stamp—a paired wall-clock and
monotonic-clock reading from the runtime's injected clock, the clock object
also used for event times—first, stop submitting work, call the
runtime's synchronization function, which waits for queued work to finish,
sleep through that clock, and then take the gap-end command stamp before
generation continues.
For example, if queued work remains at the first yield, the start stamp stays
before the drain, so drain and redispatch delay remain visible in the measured
time difference instead of being removed. The result is a transport-edge test—covering
drain, sleep, and restart—not a computation-exact natural phase boundary.
<!-- Runtime order and boundary semantics:
joulewise/adapters/mlx_runtime.py; held PR #239 branch commit cb9371aa. -->

The command-stamp problem is that separate clock calls for two labels on the
same edge could create an artificial interval.
The executable choice therefore reuses the gap-start stamp for both prefill end
and gap start, and reuses the gap-end stamp for both gap end and decode start.
For example, the retained event record has one recorded time for the prefill-end
and gap-start pair and another recorded time for the gap-end and decode-start pair, so each
commanded edge is one measurement rather than two nearly coincident ones.
<!-- Stamp pairing: joulewise/adapters/mlx_runtime.py; authenticated parsing:
joulewise/transfer_fiducial.py. -->

The fitted-edge problem is that the existing detector fits positive power
pulses, whereas the inserted sleep appears as a negative valley between active
periods. The executable choice constructs one positive pulse from prefill start
to gap start and a second positive pulse from gap end to decode end, then keeps
the first pulse's fitted falling edge, called its offset, and the second pulse's
fitted rising edge, called its onset. For each selected edge \(e\), the detector
returns an allowed signed residual interval \([l_e,u_e]\); the protocol defines
its edge radius as
\(R_e=\max(|l_e|,|u_e|)+h\), where \(h\) is that run's clock-anchor bound.
The pre-registered transfer residual is the largest \(R_e\) across every edge
from every planned run. It is labelled *supported* only when that residual is
no larger than the pulse-derived bound \(B_{\mathrm{fiducial}}\), labelled
*exceeds bound* when it is larger, and labelled *inconclusive* when any planned
run, stamp, trace-coverage check, fit, or binding is missing or invalid. Failed
runs are retained; neither dropping a run nor widening the pulse-derived bound
after seeing the result is allowed.

A worked arithmetic example uses falling-edge interval
\([-0.010,0.020]\) s, rising-edge interval \([-0.015,0.012]\) s, and
\(h=0.002\) s. Their radii are 0.022 s and 0.017 s, so the transfer residual is
0.022 s; because it is no larger than the retained pulse-derived bound
\(B_{\mathrm{fiducial}}=0.030067931757111657\) s, the example is labelled
*supported*. These values illustrate the registered arithmetic and are not
measurement results. <!-- Numeric source:
docs/process_traces/2026-09-04-fanout/transfer-fiducial/worked-example.json;
bound registry row DG-027. Executable rule: joulewise/transfer_fiducial.py. -->
<!-- END TRANSFER-FIDUCIAL-RUNNABLE -->

The external-meter study is a proposed design, not yet a runnable protocol: its
workload levels, meter synchronization, and allowable range for \(g\) remain to
be fixed. This paper has not pre-registered it. Place the meter on the wall side of the
machine's power supply. At each workload level already registered for the
campaign, integrate the meter's power over the same request start and end stamps
that the counter uses, obtaining \(E_{\mathrm{meter}}\), and retain the counter's
whole-request energy \(E_{\mathrm{counter}}\) over that window. For each load,
calculate \(g=E_{\mathrm{counter}}/E_{\mathrm{meter}}\). Fix an allowable range
for \(g\) before collection, report every ratio, and pass a load only when its
ratio is inside that range. This tests whole-request gain, not the phase split.
A separate Apple Silicon machine can repeat the complete protocol; other
questions remain outside this capstone's scope.

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

The code repository is available to the project, but the claim-bearing evidence archive and its public locators are not yet released. Moreover, the registered L1 floor-binding limitation—the claim consumer's incomplete binding of a floor back to the complete governed extraction evidence—remains open. The demonstration evidence chain therefore is **not presently open to independent re-reduction**. The steps below state what becomes executable only after the release manifest—the file that names every archived input and its SHA-256 fingerprint—supplies every angle-bracketed input.

### A.1 What a reader needs

Re-derivation requires a full-history checkout at the released revision, Python 3.11 or later, and a copy of the evidence archive. JouleWise's core declares no third-party dependencies in `pyproject.toml`; `env/analysis-lock.txt` records the environment used for retained reductions. Optional plotting and Mac inference dependencies are not part of the numeric replay.

Fresh collection additionally requires the configured Apple-silicon instrument, the exact model files named by the plan, the measurement environment recorded in `env/mac-measurement-lock.txt`, non-interactive permission to run `/usr/bin/powermetrics`, and the measured admission predicates in Section 5 (the pass/fail checks a machine's own calibration must satisfy before its runs are admitted). The retained configuration used one Apple M3 Max. This work does not establish that another Mac, operating-system build, model revision, or quantization shares its measured limits; that machine must characterize its own cells.

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

**The instrument and its records.** The instrument is macOS `powermetrics`, run with the samplers `cpu_power,gpu_power,ane_power,thermal` at a commanded sampling interval of 100 ms. It emits a stream of property-list documents (Apple's `plist` XML format). Each document is one *record*; record *i* (counting from 0) carries:

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

**The feasible set and the solver.** The variables are boxed: *β* ∈ [1 − 10⁻³, 1 + 10⁻³] and *A* ∈ [min_i *n_i* − 2·10⁹, max_i *n_i* + 2·10⁹] ns, a bracket deliberately far wider than any feasible extent; only *β* attaining a box edge is treated as a refusal (step 4 below). The feasible set is the polygon cut from that box by all native, stamp, and causal rows (two native rows per record; 1665 records give 3330 rows on the example capture). Every optimum below is an exact two-variable linear programme over that polygon; the code uses an incremental (Seidel-type: rows are added one at a time and the optimum repaired after each) exact rational solver with a fixed-seed row order, but any exact LP solver returns the same optimal *values*, which is all that is used.

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

**Spurious-plateau check on the baseline set.** The check is evaluated once, after every pulse in the train has been fitted, not as a gate before the fits; a capture that exhausts the work budget of A.3.7 is therefore recorded as nonconvergent (the search ended by budget, not by a found fit) whether or not it also carries a spurious plateau. Sort *O* by start time. With threshold *b* + max(5.0 W, 5σ), count each run of at least 2 consecutive baseline intervals above the threshold as one spurious plateau (a run of any length ≥ 2 counts once). Any spurious plateau invalidates the capture — it means the GPU did work when nothing was commanded, and a fit could not distinguish that from instrument timing.

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

The step-by-step verification order (release manifest, code and plan bytes, custody—each archived file's recorded fingerprint matching its bytes—calibration replay, characterization issuance, contrast verdict) is operator procedure, not mechanism, and now lives in the artifact guide, `docs/paper/artifact-guide.md` Section 11, "Executable verification order". Each step there names the command, the artifact it reads, and the field it compares.

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

`built-before` means the body constructs the referent from physical inputs before its first named use.
`glossed-at-first-use` means the first named use supplies a plain-word definition or an equivalent calculation in the same sentence or paragraph.
`audience-vocabulary` means a textbook-statistics or plain-English expression the intended metrology/CS professor uses without definition; that class here is exactly: repeatability, repetition, random scatter, complete, completeness, sampler cadence, refused, refuses, missing, malformed, corpus range, degrees of freedom, threshold, exact equality, null hypothesis, tail area, quarantine, append-only, run bundle, full-history checkout, third-party dependencies, cumulative counter, linear programme, infeasible, argmin, and detected.
`forward-pointer-next-paragraph` means the first use carries an explicit cross-reference to a definition in the immediately following paragraph.
`FAILS` means the term is neither built before nor glossed at first use and therefore requires a prose cure or deletion.
The inventory excludes literal field names and reason names inside quoted omission sentences, and all text inside `<!-- -->` build notes.

| Term | First reader-facing home | Status | Definition or disposition |
|---|---|---|---|
| prompt processing / prefill | 1. Introduction | glossed-at-first-use | Prompt work through the first output token; the shorthand follows the physical phrase. |
| token generation / decode | 1. Introduction | glossed-at-first-use | Later output-token emission; the shorthand follows the physical phrase. |
| phase boundary | 2. In-window calibration method | glossed-at-first-use | Runtime-recorded time separating prompt processing and token generation. |
| powermetrics | 1. Introduction | glossed-at-first-use | The macOS power sampler and its start-to-end interval-average record are stated at first use. |
| sampling record | 1. Introduction | glossed-at-first-use | One sampler output averaging processor power from its recorded start through its recorded end. |
| integrated energy | 1. Introduction | glossed-at-first-use | The time integral of power over a sampling record. |
| bracketed readings | 1. Introduction | glossed-at-first-use | One wall-clock reading placed between the monotonic-clock readings taken immediately before and after it. |
| repeatability / repetition / random scatter | 2. In-window calibration method | audience-vocabulary | Ordinary metrology words for between-repeat spread and repeated observation. |
| systematic reassignment | 2. In-window calibration method | built-before | The joule moved from one phase to the other is worked physically before this label. |
| science window / measurement window | 1. Introduction | glossed-at-first-use | One uninterrupted measurement session; Figure 2 later diagrams the same window. |
| SHA-256 / SHA-256 fingerprint | 1. Introduction | glossed-at-first-use | A fingerprint that identifies exact file bytes. |
| applied chat-template | 1. Introduction | glossed-at-first-use | The formatter that turns a prompt into model input. |
| greedy generation | 1. Introduction | glossed-at-first-use | Chooses the highest-probability next token at every step. |
| G2-a | 1. Introduction | glossed-at-first-use | The fixed candidate-length selection step. |
| prompt pin | 1. Introduction | glossed-at-first-use | The record fixing the selected prompt and generation inputs. |
| phase reduction | 1. Introduction | glossed-at-first-use | Computes separate phase energies from overlapping sampler records. |
| measurement refusal | 1. Introduction | glossed-at-first-use | A no-result stop when the fixed support requirement fails. |
| warm-up pulses | Bracketed pulse-train algorithm | glossed-at-first-use | The first use says the three pulses are discarded. |
| base-two varied-gap schedule | Bracketed pulse-train algorithm | glossed-at-first-use | Its gaps step through powers of two to keep pulse edges from repeatedly aligning with samples. |
| sampler cadence | Bracketed pulse-train algorithm | audience-vocabulary | Requested 100-ms sampling cadence is textbook/plain-English measurement vocabulary. |
| quiet trace | Bracketed pulse-train algorithm | glossed-at-first-use | The parenthesis defines quiet as no commanded pulse. |
| resting GPU power / pulse height / plateau / pulse plateau | Bracketed pulse-train algorithm | glossed-at-first-use | Resting level, pulse height, and the flat high-power portion are built in physical words. |
| trace-coverage | Bracketed pulse-train algorithm | glossed-at-first-use | The captured trace extends through the fixed margin on both sides of every pulse. |
| accepted capture bound / capture bound | Bracketed pulse-train algorithm | built-before | The pulse search, surviving rectangles, stamp widening, and refusal checks precede the largest-displacement label. |
| clock-anchor bound | Bracketed pulse-train algorithm | glossed-at-first-use | The appositive gives the uncertainty in placing the trace on wall-clock time and points to the construction next. |
| complete / completeness | Bracketed pulse-train algorithm | audience-vocabulary | Plain-English criteria words; the surrounding lists state what must be present. |
| refused / refuses | Bracketed pulse-train algorithm | audience-vocabulary | Plain-English rejection verbs used consistently for a calculation that cannot authorize evidence. |
| monotonic clock | 1. Introduction | glossed-at-first-use | A counter that advances but is never corrected to civil time. |
| straight-line clock mappings / rate-aware model | Bracketed pulse-train algorithm | glossed-at-first-use | The retained linear rate-and-offset mappings and the unequal fixed-rate correction are stated in the same paragraph. |
| missing / malformed | Bracketed pulse-train algorithm | audience-vocabulary | Plain-English input rejection conditions. |
| unbounded | Bracketed pulse-train algorithm | glossed-at-first-use | The allowed rate reaches the edge of its search box. |
| Student-\(t\) | Bracketed pulse-train algorithm | glossed-at-first-use | A small-sample bell curve, wider because spread is estimated from 17 captures. |
| 99% quantile / \(t_{0.995,16}\) | Bracketed pulse-train algorithm | glossed-at-first-use | Two-sided 99% is tied to the 0.995 one-sided point with 16 degrees of freedom. |
| degrees of freedom | Bracketed pulse-train algorithm | audience-vocabulary | Textbook statistics vocabulary; 17 captures leave 16 degrees of freedom. |
| sample standard deviation / prediction amount | Bracketed pulse-train algorithm | glossed-at-first-use | The pointer clause identifies the \(n-1\) formula of Section 4; the same paragraph supplies the value and prediction construction. |
| two-draw rule | Bracketed pulse-train algorithm | glossed-at-first-use | Two fresh bounds make the difference spread \(\sqrt{2}\) times one capture's spread. |
| corpus range | Bracketed pulse-train algorithm | audience-vocabulary | Textbook largest-minus-smallest range of the retained corpus. |
| ROUND_HALF_EVEN / nearest microsecond | Bracketed pulse-train algorithm | glossed-at-first-use | Nearest-microsecond rounding with an exact tie going to the even digit. |
| minimum allowance / operative timing bound / \(B_{\mathrm{fiducial}}\) / \(b\) | Bracketed pulse-train algorithm | glossed-at-first-use | The corpus lower allowance, one-capture pulse-plus-anchor bound, and distinct window bound are separated and numerically worked. |
| stage / block member | Bracketed pulse-train algorithm | glossed-at-first-use | A back-to-back declared run group and one of its four individual A/B/B/A runs. |
| members | Bracketed pulse-train algorithm | glossed-at-first-use | Its four individual runs, \(A_1,B_1,B_2,A_2\) in that order. |
| A/B/B/A order / block difference | Bracketed pulse-train algorithm | glossed-at-first-use | The four-member order and \((B_1+B_2-A_1-A_2)/2\) contrast are printed together. |
| curvature | Bracketed pulse-train algorithm | glossed-at-first-use | Drift that bends rather than runs straight. |
| whole-window allowance / energy family | Bracketed pulse-train algorithm | glossed-at-first-use | A once-added joule allowance for a group reduced under one energy definition. |
| reference-trajectory excursion / issued repeatability bound | Bracketed pulse-train algorithm | glossed-at-first-use | Largest-minus-smallest reference means versus a retained earlier-window repeatability bound. |
| Worked current-capture arithmetic | One diagnostic reconstruction | glossed-at-first-use | The bold label introduces a raw-stamp-to-maximal-pulse diagnostic calculation. |
| onset lag / offset lag / pulse residual | One diagnostic reconstruction | glossed-at-first-use | Observed edge minus its matching commanded edge; the residual is the largest endpoint magnitude before the anchor term. |
| record clipping / clip a record | 4. How the method bounds a false phase-energy difference | glossed-at-first-use | Keep only record time inside the phase and multiply duration by average power; the joule example is worked. |
| cell | 1. Introduction | glossed-at-first-use | Runs sharing phase, workload, model, hardware, software, and power-counter boundary. |
| false-difference components / false-difference | 3. Instrument characterization | glossed-at-first-use | The table names the false-difference bound that a contrast must clear before it is resolvable. |
| admitted | 3. Instrument characterization | glossed-at-first-use | Allowed into a calculation after frozen entry and evidence checks pass. |
| leaking dependence across the phase boundary | 3. Instrument characterization | glossed-at-first-use | Prompt-processing energy changes with work performed only after prompt processing ended. |
| independent unit | 3. Instrument characterization | glossed-at-first-use | One separately admitted bundle, not one sampler record within it. |
| workload-response slope | 3. Instrument characterization | glossed-at-first-use | Fitted change in energy per output token. |
| fitted residual | 3. Instrument characterization | glossed-at-first-use | One observed energy minus the straight-line value predicted for its output length. |
| interval of allowed differences | 3. Instrument characterization | glossed-at-first-use | Minimum and maximum A/B/B/A difference over the fixed member-energy endpoint combinations. |
| mean interval | 3. Instrument characterization | glossed-at-first-use | Mean of the five block lower endpoints through mean of their five upper endpoints. |
| resolution band | 3. Instrument characterization | glossed-at-first-use | Symmetric allowed slope range made from one admitted prefill half-width across the output span. |
| floor band | 3. Instrument characterization | glossed-at-first-use | Analogous symmetric slope range made from an independently issued prefill floor. |
| unphased gap | 3. Instrument characterization | glossed-at-first-use | Recorded interval between the end of prefill and the start of decode. |
| shared session timing term | 3. Instrument characterization | glossed-at-first-use | One bracket-capture timing bound common to all session members. |
| member-local timing | 3. Instrument characterization | glossed-at-first-use | Each run's own local and edge-span timing contribution. |
| timing flags | 3. Instrument characterization | glossed-at-first-use | Mark a member whose clock bound exceeds a quarter of its window. |
| sampling flags | 3. Instrument characterization | glossed-at-first-use | Mark cadence below its fixed ratio or too few in-window sampler records. |
| reference roles | 3. Instrument characterization | glossed-at-first-use | Separate opening, midpoint, and closing allowance builders from held-out probes. |
| passing cooldown exit | 3. Instrument characterization | glossed-at-first-use | First post-hold gate evaluation meeting the frozen rolling-power, coverage, and thermal checks. |
| point-only component bounds | Pilot observations under the retired calculation | glossed-at-first-use | Component false-difference limits with every phase edge left at its recorded time. |
| independently moved-edge ratios | Pilot observations under the retired calculation | glossed-at-first-use | Worst-endpoint bound divided by its point-only bound while every member edge moves separately. |
| bracket screen | Pilot observations under the retired calculation | glossed-at-first-use | Minimum pre/post allowance retained from the calibration corpus. |
| absolute component / comparative component | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | Same-model repeat spread versus A/B/B/A block-difference spread. |
| point-only unguarded bound | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | The complete component formula at recorded energies before the multiplier and allowance. |
| admitted energy | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | Energy from a run that passed Section 5 entry checks and may bear a claim. |
| independent units | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | One run for the absolute component or one four-run block for the comparative component. |
| independent-edge corner bound / corner | 3. Instrument characterization | glossed-at-first-use | The corner calculation is the recalculation at every joint endpoint choice. |
| independent-edge ratio \(R\) / dominates | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | Complete corner bound divided by the matching point bound; dominates means \(R\ge2\). |
| threshold / exact equality | 3. Instrument characterization | glossed-at-first-use | A threshold is the numerical cutoff that the positive slope must exceed. |
| authenticated / unauthenticated | 3. Instrument characterization | glossed-at-first-use | Expected evidence fingerprints and named inputs agree, or they do not. |
| registered rounding / registered | 3. Instrument characterization | glossed-at-first-use | Registered means fixed before collection; the later rounding rule remains fixed in fingerprinted plan bytes. |
| reintegrate | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | Reintegrate the four retained power traces after moving all four phase starts while holding their ends fixed. |
| onset set / offset set / zero-shift value | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | Reintegrated common-start values, analogous common-end values, and their included zero-shift value. |
| shared lower and upper excursions | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | The displayed equations define the lower and upper common start-plus-end movements. |
| binary64 / member-envelope integral sum | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | The usual 64-bit float format and a nonnegative four-member joule scale that covers the integrals before contrast. |
| ulp | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | The gap between 1 and the next larger representable number. |
| local sign | 1. Introduction | glossed-at-first-use | The comparative replay chooses one separately for each block. |
| local half-width / shared sign | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | The member-local changes form one block half-width; enumeration uses one common sign across blocks. |
| half-width | 3. Instrument characterization | glossed-at-first-use | A timing half-width is half an allowed timing range. |
| \(R_{cm}\) | 1. Introduction | glossed-at-first-use | Comparative edge-moved ratio with one shared timing-error sign across all blocks and one local sign per block. |
| shared-error ratio | Comparing the boundary-moved and point-only bounds | built-before | The complete shared/local replay quotient is constructed immediately before it is named. |
| not_applicable / absolute \(R_{cm}\) | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | A uniform shared shift cancels when the absolute formula subtracts its cell mean. |
| two-block fixture / Student-\(t\) critical | Comparing the boundary-moved and point-only bounds | glossed-at-first-use | A retained arithmetic-only example and its fixed-table critical value. |
| resolution bound | 1. Introduction | glossed-at-first-use | Largest false phase-energy difference allowed by the fixed cell calculation. |
| cell floor | Adding publication safeguards after the ratio | glossed-at-first-use | Artifact name for the final guarded resolution bound. |
| same-cell floor | Adding publication safeguards after the ratio | glossed-at-first-use | That floor for exactly the phase, workload, model, hardware, software, and counter cell being tested. |
| small-sample multiplier / \(g(n)\) | Adding publication safeguards after the ratio | glossed-at-first-use | The adjacent displayed formula widens five-to-nine-unit results and returns no publishable component below five. |
| directional comparison / directional comparisons | Adding publication safeguards after the ratio | glossed-at-first-use | The expected direction is fixed before collection. |
| Holm step-down correction / raw probability | Adding publication safeguards after the ratio | glossed-at-first-use | One two-comparison correction controls any false direction claim at 0.05; the later worked ordering supplies mechanics. |
| repeat standard error | Adding publication safeguards after the ratio | glossed-at-first-use | Repeat-to-repeat scatter divided by \(\sqrt n\). |
| measurement variance | Adding publication safeguards after the ratio | glossed-at-first-use | Instrument uncertainty in a recorded energy term, explicitly separate from repeat scatter. |
| metrology standard error / paired measurement variance | Adding publication safeguards after the ratio | glossed-at-first-use | The paired measurement variance remaining after shared A/B covariance is removed. |
| covariance | Adding publication safeguards after the ratio | glossed-at-first-use | The two conditions' measurement error that moves together and drops out on differencing. |
| total standard error | Adding publication safeguards after the ratio | glossed-at-first-use | Independent repeat and metrology sources combine on the variance scale before the square root. |
| null hypothesis / tail area | Adding publication safeguards after the ratio | audience-vocabulary | Textbook statistics vocabulary for zero mean difference and the resulting two-sided probability. |
| effective sample size / n_{\mathrm{eff}} | Adding publication safeguards after the ratio | glossed-at-first-use | Number of independent blocks giving the same repeat scatter. |
| AR(1) model | Adding publication safeguards after the ratio | glossed-at-first-use | Adjacent block errors are treated as serially correlated. |
| serially correlated | Adding publication safeguards after the ratio | glossed-at-first-use | Adjacent block errors are treated as serially correlated. |
| decision-interval sign check / direction gate | Adding publication safeguards after the ratio | forward-pointer-next-paragraph | The first use explicitly says the direction gate is in the next paragraph, which defines both intervals and the fixed direction. |
| magnitude check / direction check | Adding publication safeguards after the ratio | glossed-at-first-use | Absolute estimate must clear the cell floor; both complete intervals must remain on the fixed direction. |
| not resolvable | 3. Instrument characterization | glossed-at-first-use | The contrast is too small to clear its false-difference bound; it is not zero. |
| measurement interval / decision interval / deterministic bound | Adding publication safeguards after the ratio | glossed-at-first-use | Total-standard-error interval; that interval extended by authenticated non-random maximum displacements. |
| signed clearance or shortfall | Adding publication safeguards after the ratio | glossed-at-first-use | Absolute point estimate minus cell floor, with positive clearance and nonpositive shortfall. |
| A — every required ratio passes / B — an authenticated, evaluable ratio is below 2 / Refusal — a required ratio is missing, unauthenticated, or has a zero denominator / outcome A / outcome B | Outcome sentence forms | glossed-at-first-use | The three bold forms state all-pass, evaluable-below-two, and cannot-evaluate dispositions. |
| MLX | Outcome sentence forms | glossed-at-first-use | Apple's on-device inference framework. |
| inserted-gap check | Outcome sentence forms | glossed-at-first-use | An approximately 500-ms no-work gap whose independently known edges are compared with the power record. |
| Figure 3 is required here | Outcome sentence forms | glossed-at-first-use | The following sentence enumerates the exclusion, magnitude, and direction paths the required figure must show. |
| fail-closed | 5. Collection stops when required evidence fails | built-before | Missing, malformed, out-of-limit, or inconsistent evidence stops collection and records why. |
| measured admission rules / admit a stage | Measured admission rules | glossed-at-first-use | Recorded fields and limits evaluated immediately before the stage's first measured member. |
| idle baseline / nearest-rank p95 | Measured admission rules | glossed-at-first-use | Thirty-second no-run sample; sort \(n\) values and select item \(\lceil0.95n\rceil\). |
| cooldown rule | Measured admission rules | glossed-at-first-use | Inter-member recovery must pass before 300 s; an override makes the member diagnostic only and prevents claim bearing. |
| window closes | Measured admission rules | glossed-at-first-use | The third same-cause stage failure closes the full window, not merely the stage. |
| first-order balance / measured contrast | Counterbalanced order | glossed-at-first-use | Equal sums of A and B run midpoints; the A/B/B/A difference is printed. |
| quarantine / append-only | Every input and every refusal remains visible | audience-vocabulary | Plain-English custody words for retained failed slots and non-overwriting replacement records. |
| tamper-evident / tamper-proof / trusted operator | Every input and every refusal remains visible | glossed-at-first-use | Mistake detection and post-hoc-choice defense, not protection against another actor. |
| third-party provenance / provenance | Every input and every refusal remains visible | glossed-at-first-use | Evidence that would convince someone who does not trust the operator. |
| freeze receipt / freeze receipts | Every input and every refusal remains visible | glossed-at-first-use | Records fixing plan bytes and the time those bytes were frozen. |
| hash-bound | Results | glossed-at-first-use | A selection record carrying the digest of the fixed candidate-length selection record. |
| overlapping record / record support / IQR / resolvability | Why the selected prompt length is not yet stated | built-before | The body builds boundary-to-sampler overlap; the other legacy alternatives occur only in excluded build notes. |
| three-record minimum | 1. Introduction | glossed-at-first-use | A phase must overlap at least three sampler records to be reduced at all. |
| two-record safety margin / design floor | Why the selected prompt length is not yet stated | glossed-at-first-use | Five overlaps are two above the three-overlap phase minimum; the design floor is stricter than reducer calculability. |
| count floor | Why the selected prompt length is not yet stated | glossed-at-first-use | The registered minimum record count for a full-strength result. |
| reducer | Why the selected prompt length is not yet stated | glossed-at-first-use | Program that turns a retained run bundle into phase energies. |
| variance multiplier | Further limitations | glossed-at-first-use | The displayed definition says how much the selected dependence model multiplies repeat variance. |
| within-arm variation | Further limitations | glossed-at-first-use | Variation among runs of the same A or B condition. |
| fitted edge time / command time | Future work | glossed-at-first-use | Detector-fitted time and independently stamped command time are defined beside the residual equation. |
| external-meter study | Future work | glossed-at-first-use | A proposed, unrun whole-request comparison against a meter on the wall side of the power supply. |
| Running Average Power Limit / RAPL | From counter gain to counter time | glossed-at-first-use | Processor-exposed energy counter; full phrase precedes the abbreviation. |
| NVIDIA Management Library / NVML | From counter gain to counter time | glossed-at-first-use | Software power counter; full phrase precedes the abbreviation. |
| large-language model / LLM | LLM energy measurement | built-before | The document title expands the abbreviation before its first body use. |
| minimum-detectable-effect / pre-registration | Benchmark and metrology lineage | glossed-at-first-use | Paired variation estimates a prospectively detectable effect; the threshold is fixed before results. |
| disaggregated inference / disaggregation | Benchmark and metrology lineage | glossed-at-first-use | Split inference across endpoints is named as a future application requiring two boundaries and clock alignment. |
| re-derivation / fresh collection | Appendix A. Reproducing this work | glossed-at-first-use | Recompute from preserved bytes versus create new evidence under the named machine conditions. |
| not presently open to independent re-reduction | Appendix A. Reproducing this work | built-before | The unreleased archive and open floor-binding limitation support the bold disposition. |
| claim-bearing evidence archive / floor-binding limitation | Appendix A. Reproducing this work | glossed-at-first-use | Evidence that may support a claim and the consumer's incomplete binding back to governed extraction evidence. |
| release manifest / manifest | Appendix A. Reproducing this work | glossed-at-first-use | The file that names every archived input and its SHA-256 fingerprint. |
| full-history checkout / third-party dependencies | A.1 What a reader needs | audience-vocabulary | Plain software-reproduction vocabulary for repository history and externally supplied packages. |
| admission predicates | A.1 What a reader needs | glossed-at-first-use | The pass/fail checks a machine's own calibration must satisfy before its runs are admitted. |
| run bundle | Why the selected prompt length is not yet stated | audience-vocabulary | Plain-English software packaging vocabulary; Appendix A.2 later enumerates its files. |
| strict validation | A.2 Scientific artifacts and their bindings | glossed-at-first-use | Independently rebuilds the trace and summary rather than trusting derived files. |
| scientific binding | A.2 Scientific artifacts and their bindings | glossed-at-first-use | Removing a calibration input breaks the connection from primary bytes to the bound. |
| whole-window verdict / floor extraction / claim verdict | A.2 Scientific artifacts and their bindings | glossed-at-first-use | Successive artifacts bind admitted membership, each cell floor, and the final contrast decision. |
| clock-anchor estimator / pulse-fit (accepted-region) algorithm | A.3 Formal calibration algorithms | glossed-at-first-use | One places the trace on wall time; the other encloses edge timing consistent with a commanded pulse. |
| exact floating summation | A.3 Formal calibration algorithms | glossed-at-first-use | Correctly rounded compensated sum whose order cannot change the binary64 result. |
| ppm | A.3 Formal calibration algorithms | glossed-at-first-use | Parts per million. |
| The instrument and its records | A.3 Formal calibration algorithms | glossed-at-first-use | Expository label for the powermetrics record definition that follows. |
| property-list | A.3 Formal calibration algorithms | glossed-at-first-use | Apple's `plist` XML format. |
| interval aggregate | A.3 Formal calibration algorithms | built-before | The record is an interval aggregate, not a cumulative counter. |
| cumulative counter | A.3 Formal calibration algorithms | audience-vocabulary | The record is an interval aggregate, not a cumulative counter. |
| combined power | A.3 Formal calibration algorithms | glossed-at-first-use | CPU, GPU, and neural-engine channel watts summed after conversion. |
| record energy | A.3 Formal calibration algorithms | glossed-at-first-use | Three integer millijoule counters summed and divided by 1000. |
| Cumulative elapsed time | A.3 Formal calibration algorithms | glossed-at-first-use | Instrument-counted time from the end of record 0 to a later record end. |
| Clock stamps / paired stamp | A.3 Formal calibration algorithms | glossed-at-first-use | Monotonic-wall-monotonic readings; their half-width covers bracket timing plus reported clock resolution. |
| Trace intervals | A.3 Formal calibration algorithms | glossed-at-first-use | Anchored record start-to-end intervals carrying one GPU-power value. |
| Commanded pulses | A.3 Formal calibration algorithms | glossed-at-first-use | Stamped on/off pairs numbered 0 through 58. |
| fiducial | Bracketed pulse-train algorithm | built-before | The pulse-plus-anchor capture construction is built before its \(B_{\mathrm{fiducial}}\) label; Appendix A.3 later gives the general reference-edge gloss. |
| rollover | A.3 Formal calibration algorithms | built-before | The whole-second `timestamp` label of a record advances at least once. |
| van der Corput sequence | A.3 Formal calibration algorithms | glossed-at-first-use | Write \(k\) in binary, reverse its digits, and read the result as a binary fraction after the point. |
| 59 measured pulses | A.3 Formal calibration algorithms | glossed-at-first-use | Protocol pulses after warm-up; their schedule and one-second duration are built in the same step. |
| end of record 0 | A.3 Formal calibration algorithms | glossed-at-first-use | Wall-clock time of record 0's end, called the anchor in the same sentence. |
| set membership | A.3 Formal calibration algorithms | glossed-at-first-use | Exact set of anchor-rate pairs consistent with every evidence constraint. |
| The model | A.3 Formal calibration algorithms | glossed-at-first-use | Expository label for the affine wall-versus-monotonic relation immediately below. |
| affine | A.3 Formal calibration algorithms | glossed-at-first-use | The wall clock is assumed affine in monotonic time over the capture. |
| Model condition (stated because the containment claim depends on it) | A.3 Formal calibration algorithms | glossed-at-first-use | The same sentence states the fixed-rate and 250-µs-residual conditions for containment. |
| Inputs and their admission checks | A.3 Formal calibration algorithms | glossed-at-first-use | The following sentence lists stamp, trace, and elapsed-value requirements. |
| Wall-minus-monotonic span | A.3 Formal calibration algorithms | glossed-at-first-use | Largest raw upper clock offset minus smallest raw lower clock offset across five stamps. |
| Numeric-padding check | A.3 Formal calibration algorithms | glossed-at-first-use | Four ulps at the epoch magnitude must fit inside the one-microsecond pad. |
| Stamp constraints | A.3 Formal calibration algorithms | glossed-at-first-use | Inequalities force each wall reading inside its padded monotonic bracket. |
| Native-label constraints | A.3 Formal calibration algorithms | glossed-at-first-use | Whole-second record labels bound the modeled end time with a 250-µs allowance. |
| Causal constraints, and the two symbols k_pre and k_parse | A.3 Formal calibration algorithms | glossed-at-first-use | Spawn-before-window and parsed-after-write facts give lower and upper anchor constraints. |
| k_pre equals e_0 minus one resolution unit r_pre | A.3 Formal calibration algorithms | glossed-at-first-use | The identity follows from choosing the first pre-spawn monotonic read as the origin. |
| Eliminating α | A.3 Formal calibration algorithms | glossed-at-first-use | Fourier–Motzkin removes the coefficient-one offset and leaves constraints in rate and anchor. |
| Fourier–Motzkin elimination | A.3 Formal calibration algorithms | glossed-at-first-use | \(α\) is removed exactly, leaving linear constraints in \((β,A)\) only. |
| The feasible set and the solver | A.3 Formal calibration algorithms | glossed-at-first-use | Boxed rate-anchor polygon optimized by an exact two-variable solver. |
| Seidel-type | A.3 Formal calibration algorithms | glossed-at-first-use | Rows are added one at a time and the optimum repaired after each. |
| linear programme / infeasible | A.3 Formal calibration algorithms | audience-vocabulary | Textbook optimization vocabulary for an exact constrained optimum or an empty constraint set. |
| first-parse lag | A.3 Formal calibration algorithms | glossed-at-first-use | The longest time between record 0's end and the latest instant the first-parse stamp allows for it. |
| Composing the bound | A.3 Formal calibration algorithms | glossed-at-first-use | The displayed sum combines anchor half-width, span, clock resolution, and numeric padding. |
| admissible | A.3 Formal calibration algorithms | built-before | The exact admissible interval for \(A\). |
| Anchoring | A.3 Formal calibration algorithms | built-before | The earlier estimator has built the point anchor before this trace-placement label. |
| Reading the pulses | A.3 Formal calibration algorithms | glossed-at-first-use | Scan and pair command on/off events for warm-up and measured pulses. |
| Trimming warm-ups | A.3 Formal calibration algorithms | glossed-at-first-use | Discard every interval starting before the last warm-up off-stamp. |
| warm-up pulses do not participate in the baseline set and are never fitted | A.3 Formal calibration algorithms | built-before | The immediately preceding trimming rule entails the emphasized disposition. |
| Authenticating the executed schedule | A.3 Formal calibration algorithms | glossed-at-first-use | Duration, varied-gap, and quiet-support checks consume stamps and trace extent rather than planned metadata. |
| Baseline set and robust scale / baseline set | A.3 Formal calibration algorithms | glossed-at-first-use | Intervals outside all pulse margins; median power and floored MAD scale are then defined. |
| median absolute deviation / robust scale | A.3 Formal calibration algorithms | glossed-at-first-use | Median distance from the median, scaled to a Gaussian standard-deviation equivalent with a 1-mW floor. |
| MAD | A.3 Formal calibration algorithms | glossed-at-first-use | The median of the absolute distances from the median. |
| Spurious-plateau check on the baseline set / spurious plateau | A.3 Formal calibration algorithms | glossed-at-first-use | Two or more consecutive quiet intervals above the fixed threshold indicate uncommanded work. |
| nonconvergent | A.3 Formal calibration algorithms | glossed-at-first-use | The search ended by budget, not by a found fit. |
| Per-pulse fit | A.3 Formal calibration algorithms | glossed-at-first-use | The numbered procedure defines the local data, plateau, model, search, and acceptance checks. |
| Local set | A.3 Formal calibration algorithms | glossed-at-first-use | Trace intervals overlapping one pulse's margin window. |
| Interior set | A.3 Formal calibration algorithms | glossed-at-first-use | Local intervals wholly inside the plateau inset. |
| Amplitude | A.3 Formal calibration algorithms | glossed-at-first-use | Amplitude \(a\) = median{ \(y_i\) : interior } − \(b\), fixed at this value for the rest of the fit. |
| robust SNR | A.3 Formal calibration algorithms | glossed-at-first-use | Fitted plateau amplitude divided by robust baseline scale. |
| Edge coverage | A.3 Formal calibration algorithms | glossed-at-first-use | Local trace must extend through both fixed pulse-edge margins. |
| The model and the objective | A.3 Formal calibration algorithms | glossed-at-first-use | Shifted rectangular-pulse interval average scored by standardized Huber residual loss. |
| Huber loss | A.3 Formal calibration algorithms | glossed-at-first-use | Quadratic for small residuals and linear for large ones so one wild sample cannot dominate. |
| The search (constrained coordinate descent) | A.3 Formal calibration algorithms | glossed-at-first-use | Alternate explicit onset and offset grid minimizations at coarse then fine steps. |
| argmin | A.3 Formal calibration algorithms | audience-vocabulary | Standard mathematical operator for minimizing `Loss` over the displayed candidate grid. |
| Significance | A.3 Formal calibration algorithms | glossed-at-first-use | Require \(Loss^* < 0.5\,Loss_{flat}\), the loss of a model with no pulse at all. |
| Shift limit | A.3 Formal calibration algorithms | glossed-at-first-use | Both fitted shifts must remain strictly below 0.5 s in magnitude. |
| The set of acceptable edge pairs / loss limit | A.3 Formal calibration algorithms | glossed-at-first-use | Edge pairs with loss no more than best loss plus the fixed tolerance. |
| accepted region | A.3 Formal calibration algorithms | glossed-at-first-use | All pulse-edge pairs whose loss is within that limit. |
| Cell lower bound | A.3 Formal calibration algorithms | glossed-at-first-use | Sum of least attainable per-interval Huber values over one shift rectangle. |
| monotone | A.3 Formal calibration algorithms | glossed-at-first-use | Covered fraction decreases as onset moves later and increases as offset moves later. |
| interval branch-and-bound / region's enclosure | A.3 Formal calibration algorithms | glossed-at-first-use | Reject a rectangle only by a rigorous lower bound and retain passing resolution cells whole. |
| bisect | A.3 Formal calibration algorithms | glossed-at-first-use | Split at the midpoint of the wider side. |
| depth-first | A.3 Formal calibration algorithms | glossed-at-first-use | The upper half is processed next. |
| Projection | A.3 Formal calibration algorithms | glossed-at-first-use | The region's enclosure is the bounding box of the retained cells. |
| Widening by stamp uncertainty | A.3 Formal calibration algorithms | glossed-at-first-use | Subtract or add each command stamp's half-width from its projected edge limits. |
| detected | One diagnostic reconstruction | audience-vocabulary | Plain-English observation that all 59 pulses passed detection. |
| worst excursion | A.3 Formal calibration algorithms | glossed-at-first-use | An edge's largest widened-region endpoint magnitude. |
| observed sample maximum | A.3 Formal calibration algorithms | glossed-at-first-use | Largest of 118 observed edge excursions, without a population-coverage guarantee. |
| percentile | A.3 Formal calibration algorithms | glossed-at-first-use | The \(\lceil0.95\cdot118\rceil=113\)th smallest value. |
| Origin of the 120 s work clock | A.3 Formal calibration algorithms | glossed-at-first-use | The budget clock starts after baseline computation and before the first pulse fit. |
| custody | A.4 Executable verification order | glossed-at-first-use | Each archived file's recorded fingerprint matching its bytes. |
| matching refusal / reproduced result | A.5 Interpreting a refusal | glossed-at-first-use | Identical bytes and plan should reproduce the same reason name; that refusal is a result. |

The audit also searched the successor text for the retired campaign tag,
retired model family, retired fixed-prompt labels, the false between-record
pause mechanism, and the retired any-exceedance falsifier. Any occurrence is
a failure. Terms inventoried: 224; FAILS: 0.
