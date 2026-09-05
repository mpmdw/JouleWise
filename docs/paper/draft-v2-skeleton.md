<!-- METHODS/DIAGNOSTIC SUBMISSION DRAFT — selected 2026-09-05 under D-174.
Authority: docs/process_traces/2026-09-05-readiness/02-magistrate-ruling-fallback.md.
Source rows and retired placements remain in results-fill-registry.md.
No empirical outcome selection or prospective result fill remains.
-->

# JouleWise: Timing Sensitivity of Phase-Energy Assignments on Apple Silicon

## Abstract

Software can report one average power value over a span crossing the change
from reading input to generating output tokens. JouleWise assigns energy to
each part as average power times overlap duration; moving the dividing time
reallocates energy without changing the request total. The method specifies
clock placement, calibration using commanded graphics-processor pulses (work
with time-stamped start and stop commands), and sensitivity calculations over
the registered timing domain—the edge movements fixed before collection.
The allocation holds each record at its reported average; it does not bound
physical phase energy under arbitrary within-record allocations. A GPU is a
graphics processor; fitted onsets and offsets are the switch-on and switch-off
times selected by matching predicted interval-average power to the recorded
trace. In a current-method re-analysis of one historical GPU pulse capture, all 59 fitted onsets occur after their commands and 49 of 59 fitted offsets occur before them; transfer of its timing allowance to inference remains untested.
Earlier short requests had 37 of 50 measured parts crossed by two power
readings and 13 by three; only the latter met the three-record minimum.
Labelled synthetic examples expose the distinction between timing sensitivity
and physical allocation ambiguity and make the arithmetic reproducible.
The empirical evidence is historical and confined to one Apple computer,
software configuration, and macOS processor-power records. It supplies no
new model-energy comparison or phase-energy dominance result.
<!-- Headline: DX-001/003/012/013; record support: DG-067/068/069/072/073. -->

## 1. Introduction

This methods/diagnostic paper asks how a software power record can support
an allocation to separate parts of an inference request. macOS `powermetrics` is the power sampler used here. A sampling record
is one sampler output that averages processor power from its recorded
start time to its recorded end time. An inference request first reads its
input through production of the first output token; this paper calls that
prompt processing, or *prefill*. It then emits later output tokens; this is
token generation, or *decode*. The runtime-recorded time between those parts
is the **phase boundary**.

One sampling record can begin during prefill and end during decode. It then
reports one average power for a span that contains both parts, rather than one
value for each. The measurand is energy assigned to each phase by
**interval-overlap allocation**: each sampling record's energy is divided
between the two phases in proportion to the share of its interval falling on
each side of the phase boundary. The record's integrated energy is the time integral \(\int P(t)\,dt\) over its full
span. The **timing envelope** is the range of assigned energies over the
registered timing domain—the edge movements fixed before collection—conditional on the **held-average reconstruction**,
which holds each record at its reported average. It bounds neither physical
phase energy under arbitrary within-record allocations nor inference transfer nor future-error coverage. Moving the edge
within the same record reassigns a slice of recorded energy from one phase to
the other, but the request total does not change. Repeating the request can
narrow ordinary run-to-run scatter; it does not remove this allocation
sensitivity.

In a **synthetic enclosure diagnostic**, a 0.9-s window crossing ten 100-ms
records that each report 10 W is assigned 9 J. Its \(\pm10\)-ms two-edge timing
envelope is [8.8, 9.2] J, while allowing each record's energy to sit anywhere
inside its own interval gives the nonnegative partial-record enclosure
[8, 10] J: the eight records lying wholly inside contribute 8 J, and the two
records the window only partly covers contribute between 0 and 1 J each.
The latter is a diagnostic of allocation ambiguity at the registered window; it is reported, never composed into any bound.
Appendix Figure A1 shows the records, window, and three energy results for this synthetic example.

The historical evidence is deliberately narrow. It measures one Apple M3 Max with
128 GB of unified memory and one configuration of `powermetrics`. MLX is
Apple's on-device inference framework used to run the models. The resulting
allocation sensitivities do not transfer to another machine,
software stack, workload, or power sampler.

Edge placement also depends on clock placement. A rate-aware clock mapping
does not assume that the computer's wall clock and its monotonic clock—a counter
that advances but is never corrected to civil time—advance at exactly the same
rate. Instead, it places each wall-clock reading between the monotonic-clock
readings taken immediately before and after it. Those are the bracketed
readings; the method retains every fixed-rate, offset mapping that they and the
power-record labels permit. The pulse calibration and clock mapping together
specify the allowed edge movements for recalculating assigned energy; using
those movements for inference requires the untested transfer assumption.

To measure the edge problem rather than assume its size, JouleWise records
command timestamps for GPU pulses whose onset is fitted from the
power record. **Commanded graphics-processor pulses** are fixed-duration GPU
work with time-stamped start and stop commands, recorded inside a measurement
window—one uninterrupted measurement session.
The largest displacement between the commanded times and every edge position
allowed by the pulse records, plus the **clock-anchor bound**—the uncertainty in
placing the power record on wall-clock time—is the **pulse-derived limit**.
Applying that limit to inference assumes that the power record locates pulse edges and
model-work edges with the same error. Because pulses are not inference, an
**inserted-gap check**—commanding about 500 ms of no work between prefill and
decode and comparing the gap's independently time-stamped edges with the power
record—is registered as future diagnostic work; this paper did not run it.

A **configuration cell**, shortened below to **cell**, is the set of runs with
one phase, workload, model, hardware, software, and power-measurement boundary,
meaning which power is counted: here the processor power macOS reports, not power
at the wall outlet.
The registered comparison method has three distinct estimands, meaning
quantities the calculation is intended to estimate. It is specified here,
but no new comparison result is reported:

An A/B/B/A block is four runs in the order A, B, B, A.

| Source | Estimand |
|---|---|
| Same-model repeats | Absolute floor |
| Same-model null A/B/B/A blocks, with A = B | Comparative floor |
| Two-model A/B/B/A blocks | Science contrast |

Within a cell, repeated measurements of one model's assigned phase energy
produce a spread after their mean is subtracted. A same-model null A/B/B/A
block produces a false-difference diagnostic, whereas a two-model A/B/B/A
block produces the science contrast. JouleWise bounds each floor source
separately; each separately bounded source is a component. The cell's
**resolution bound**—the **detection floor** in the advisor's terminology—is a
registered operational resolution guard for assigned-energy differences in
that cell before the safeguards in Section 4; the artifacts call the final
gate value after those safeguards the **cell floor**.

The registered sensitivity question is whether permitted edge movement—every lower-or-upper
edge position allowed by that calibration and mapping—at least doubles each
component's source of false difference. Let \(U_{\mathrm{point}}\) be a component bound calculated
at the recorded edges; this is the **point-only value**. Let
\(U_{\mathrm{corner}}\) be its counterpart after every allowed
lower-or-upper edge choice for that component is evaluated jointly and the
largest result retained. This **moved-edge limit** is called the
**independent-edge corner bound** in the artifacts. Their quotient,
\(U_{\mathrm{corner}}/U_{\mathrm{point}}\), is the **independent-edge ratio** because each
run's edge may move separately. In the same-model null blocks, A and B are
condition-slot labels set equal to each other; the science contrast assigns the
two models to different conditions.
The comparative replay also retains an **energy-allowance sign**, which says
which direction a nonnegative block-level allowance moves assigned energy. A
shared sign is one choice applied across all blocks, while a local sign is
chosen separately for each block. This replay uses a different numerator:
let \(U_{\mathrm{cmp,point}}\) be the four-run comparison's point-only value, and
let \(U_{\mathrm{cmp,shared}}\) be its largest limit after one energy-allowance sign
is replayed across all blocks and one local sign is chosen per block. Their
quotient is \(R_{cm}=U_{\mathrm{cmp,shared}}/U_{\mathrm{cmp,point}}\). This
\(R_{cm}\) quantity is a **shared-energy-sign/local-corner sensitivity
diagnostic**: it retains one shared sign for block-level energy allowances and
one local sign per block. It does not globally replay one physical common-time
shift and has no proven conservatism for common-time motion. Both ratios
measure enlargement under specified perturbation sets; they do not estimate
how often or how strongly those errors occur.

Before either ratio is compared with 2, **authentication** matches every input
to its named source-file contents. **Evaluation** then requires a nonzero
point-only value, making the ratio evaluable. In the prospective design,
the twelve required ratios are
one independent-edge ratio for each of the eight floor components (two models,
two phases, and for each of those the same-model repeat and same-model null
A/B/B/A sources) and one comparative \(R_{cm}\) diagnostic for each of the four
same-model null components. Any of the twelve below 2 falsifies the claim;
equality passes. A ratio of at least 2 means that moving
the edge adds at least one entire point-only value to the bound—the
**twofold boundary contribution** defined by the method. This submission
reports the method and its worked arithmetic; it does not evaluate that
twelve-ratio empirical hypothesis.

That ratio result does not by itself choose between models. The
**decision rule**, fixed before collection, reports a direction only when the
measured difference clears its cell floor and the full lowest-to-highest range
after known errors stays on the direction fixed before collection.

The prospective demonstration—the comparison fixed before collection—is
outside this submission's empirical scope. It
compares the small model `qwen3-1p7b`, revision
`3b1b1768f8f8cf8351c712464f906e86c2b8269e`, with the large model `qwen3-8b`,
revision `545dc4251c05440727734bcd94334791f6ab0192`. <!-- V5-ID-001; V5-ID-002 -->
Its token-generation contrast uses prompt 0 of the ordered eight-prompt
`real_prompts_v1` set for every block in both model arms. The prompt-set SHA-256
fingerprint—an identifier of exact file bytes—is
`20debdb41eb4983339a160176dcf4e475153b5d6f16b1ef3ada39447e99f3474`. <!-- V5-WL-001 -->
Both conditions use the same `tokenizer.json` SHA-256
`aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` and the
same applied chat-template—the formatter that turns a prompt into model input—
whose SHA-256 is
`87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5`, with
reasoning disabled (Qwen3's optional chain-of-thought output is switched off).
<!-- V5-WL-002; V5-WL-003 --> Greedy generation—choosing
the highest-probability next token at every step—forces 512 output tokens for
one rendered prompt in each run. <!-- V5-WL-004 --> The prefill length-selection procedure remains prospective. No selected
length supplies this submission.
This fixed pair would demonstrate the decision rule; it is not a scaling experiment.
The comparison supports this fixed prompt and makes no prompt-population
generality claim. No result for that pair is reported here.

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

Immediately before and after each science window—one uninterrupted measurement session—JouleWise records a calibration under the same declared machine state, meaning the hardware and operating conditions recorded before collection. Each capture carries an instrument-validation manifest, a list of its calibration artifacts and their SHA-256 fingerprints. Under the current mint—the analysis run that issues the paper's fixed results—JouleWise hashes that manifest's bytes and compares the result with `validation_manifest_sha256` recorded in the capture, then hashes every listed artifact and compares the result with the manifest's entry; either mismatch refuses the capture as `instrument_calibration_invalid` in `joulewise/reduce.py`. Separately, it hashes the bytes of the frozen reservation plan, the file that names the reserved collection slots, and checks both that digest and the plan identifier against pins in the calibration ledger's session record; either mismatch is `PLAN_HASH_MISMATCH` in `joulewise/calibration_ledger.py`. The calibration-acceptance file, which contains the fixed rule used to judge a bracket, gets its expected digest from the in-code `ISSUED_ACCEPTANCE_REGISTRY`, or from `GENESIS_FIXTURE_ACCEPTANCE_SHA256` for the retained genesis test fixture, before its bytes are accepted by `joulewise/calibration_bracketing.py`. **Frozen** means fixed and fingerprinted before collection. The capture's timestamps must place it before the first or after the last science run and no more than 24 hours from the window's far end. After three warm-up pulses, which are discarded, it commands 59 one-second GPU matrix-multiplication pulses on preallocated \(4096\times4096\) 16-bit floating-point matrices. A fixed base-two varied-gap schedule—gaps generated by reversing binary digits as specified in Appendix A.3.2—prevents the pulse edges from repeatedly lining up with the requested 100-ms sampler cadence. Five seconds of quiet trace (no commanded pulse) are requested on both sides of the train, of which at least 4.5 s must be present.

For each commanded pulse, the detector estimates resting GPU power from samples outside the fixed time margin around every pulse and pulse height from samples wholly inside its flat high-power portion, called the plateau. It predicts each reported interval average from the fraction of that interval covered by a shifted rectangular pulse, then scores the difference between predicted and observed power with a rule that limits the influence of one large discrepancy while moving the onset and offset separately. After finding the best pair, it encloses every pair close enough to that fit: a rectangle is rejected only when a mathematical lower bound proves that none of it can pass, and every surviving rectangle is split to a fixed resolution. The four outer edge values are widened for uncertainty in the two command timestamps. A capture is refused unless all 59 pulses pass five kinds of check: the signal rises far enough above resting power; the fitted pulse explains the trace better than a no-pulse model; the fitted onset and offset stay inside the accepted shift range; trace coverage extends through the fixed margin on both sides of the pulse; and the required pulses, file fingerprints, and machine-and-protocol fields are complete. Appendix A.3.5 gives the signal, fit, range, and trace-coverage calculations, and Appendix A.3.6 gives the completeness test. No uncommanded plateau may appear. The shared search-work limits cap both the number of search rectangles evaluated and the elapsed search time for the whole capture; exhausting either limit refuses the capture (Appendix A.3.7). The accepted capture bound is the largest allowed edge displacement among all pulses plus the trace's clock-anchor bound, the uncertainty in placing the trace on wall-clock time, built next.

The clock anchor uses five wall-clock readings, each bracketed by readings from a monotonic clock—a counter that advances but is never corrected to civil time—together with every whole-second label embedded in the native power records. The **first-record endpoint** is the wall-clock time assigned to the end of the first native power record. The method retains every straight-line mapping whose rate and offset satisfy four evidence constraints: each wall reading lies inside its monotonic stamp bracket; each native whole-second label contains its modeled record end; the first record starts after sampler launch; and that record is parsed only after it is written. Appendix A.3.3 gives the inequalities. The method permits the two clocks to run at slightly different fixed rates and charges the full allowed departure of a native label from that line. It refuses missing or malformed inputs, an empty set or an unbounded one (the allowed rate reaches the edge of its search box), inadequate capture span, implausible clock rate, active automatic network-time correction, or a bound outside the accepted range. Otherwise it finds the earliest and latest allowed first-record endpoint and adds four allowances: half the endpoint range, the observed wall-versus-monotonic span, the largest reported clock resolution, and a fixed numeric-rounding pad. This corrected rate-aware model replaced the false equal-rate assumption, which could move every fitted edge in the same direction.

Finally, the pre-window and post-window capture bounds form a bracket. The frozen **calibration-acceptance rule** is the pre-collection rule that decides whether those two captures may bracket one window; it derives two constants from its retained 17-capture corpus. Student-\(t\) is a small-sample bell curve whose 99% quantile—the two-sided 99% point, written \(t_{0.995,16}\) because it leaves 0.5% in each tail with 16 degrees of freedom, and larger than the normal curve's because the spread is estimated from only 17 captures—sets the maximum permitted pre/post difference. For \(n=17\) per-capture bounds, the sample standard deviation (the \(n-1\) formula of Section 4) is \(s_b = 2.460856\) ms (unrounded, \(2.460856207694636\) ms) and \(t_{0.995,16}=2.92078162242509999197\); the two-draw rule—two fresh capture bounds are drawn, and the spread of their difference is \(\sqrt{2}\) times one capture's spread—so \(t_{0.995,16}\times s_b\times\sqrt{2}\) records \(10.164834757777545\) ms, printed as the \(10.164835\)-ms maximum permitted pre/post difference. The separately retained **minimum allowance** starts from the corpus range, \(9.723589288793850\) ms, rounded to the nearest microsecond, with an exact tie going to the even digit (`ROUND_HALF_EVEN`), giving \(9.724\) ms; Appendix A.3.8 prints the 17 bounds from the retained calibration acceptance file `configs/calibration/calibration_acceptance_d079_v2_n17_r3.json` (registry source S17). The minimum prevents two numerically matching captures from erasing the finite change allowance fixed from that corpus. A larger difference refuses the window. Appendix A.3.6 calls one capture's pulse-derived limit \(B_{\mathrm{fiducial}}\). The window's distinct **operative timing bound** \(b\) is the larger capture bound plus \(\max(|B_{\mathrm{post}}-B_{\mathrm{pre}}|,9.724\ \mathrm{ms})\), added once. For example, a 25-ms pre-window bound and a 29-ms post-window bound differ by 4 ms, pass the 10.164835-ms limit, and give \(b=29+\max(4,9.724)=38.724\) ms. If the post-window calibration widens a bound already used, the affected phase energies are recomputed with the wider bound or refused. Appendix A.3 formally defines the complete sets of pulse-edge positions and clock mappings that satisfy every fixed constraint, along with objectives, ranges, and refusal conditions.

Commanded GPU pulses calibrate edge placement, but applying that bound to sustained mixed inference is an assumption. The before-and-after bracket tests for change across the measurement window; it does not test whether the pulse-derived limit applies to inference.

Appendix Figure A2 orders the before-and-after pulse calibrations, the **entry check**, the pass/fail checks on recorded machine state that a stage must satisfy before its first run is measured (Section 5), fixed reference workloads repeated at the
window's opening, midpoint when present, and close to track drift, and science blocks within
one measurement window. Those repeated workloads are the **reference runs**.
A stage that passes is **admitted**, meaning allowed to begin its measured runs.
A **stage** is one declared group of runs measured back-to-back inside that
window. Each science block uses A/B/B/A order—condition A, condition B,
condition B, condition A—and names its four **members**, meaning its four
individual runs, \(A_1,B_1,B_2,A_2\) in that order. Its block difference is
\((B_1+B_2-A_1-A_2)/2\); a positive value means condition B used more energy
than condition A. The order balances conditions and suppresses a linear trend
only when the sums of the A and B run midpoints match; unequal runtimes or
cooldowns can break that symmetry. **Gross energy** is the
processor energy recorded during a run. **Idle-subtracted energy** removes the
mean idle power multiplied by run duration from that gross amount. Curvature
remains covered by a separately measured **whole-window allowance**: one joule
amount for each **energy family**, a group reduced under one of those energy
definitions, later added once to its component bound, equal to the larger of
the **reference-trajectory excursion**—the spread among the mean energies of
the opening, midpoint, and closing reference runs (largest minus smallest)—and
that family's **issued repeatability bound**—a repeatability bound on
reference-run energy issued from an earlier retained window, not re-estimated
in this one.

### One diagnostic reconstruction

The following table and arithmetic reconstruct one retained diagnostic capture from raw clock readings through its maximal pulse. Wall stamps use seconds since 1970; monotonic stamps use the machine's never-adjusted counter. The protocol offsets use the commanded pulse schedule's own origin at its first protocol pulse. Three warm-up pulses occur before that origin, and sampling began earlier still, so those offsets are neither times since sampling began nor observed edge times. A **best-fit lag** is fitted edge time minus its matching command time. Each onset lag or offset lag uses that commanded edge as zero; bounds are elapsed durations rather than positions on either clock.

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

*Worked historical-capture arithmetic.* One retained current-estimator derivation reports all \(59\) pulses detected, \(122{,}859\) evaluated rectangles, a local clock-anchor bound of \(0.0011349971959968978\) s, and a final capture bound of \(0.030067931757111657\) s. Therefore the largest pulse residual before the anchor term is \(0.030067931757111657-0.0011349971959968978=0.0289329345611147592\) s. Re-running the detector over that capture's retained raw power trace and event log, under the current anchor method, reproduces both the capture bound and the evaluated-rectangle count exactly, and identifies the pulse attaining the maximum: the tenth commanded pulse of the capture, scheduled to switch on \(26.625\) s and off \(27.625\) s measured from the origin of the commanded pulse schedule, which is where the schedule places its first protocol pulse rather than an observed onset. Its two commands were stamped at \(1784757381.2856488\) s and \(1784757382.293089\) s of wall time, expressed as seconds since 1970. The fit leaves its onset lag anywhere in \([0.02544938965763524,\,0.02893293456111476]\) s and its offset lag anywhere in \([-0.008607394549133255,\,-0.005308621075866744]\) s, about a best-fit pair of \(+0.027\) s and \(-0.007\) s. The retained residual bound for the pulse is the largest absolute value those four endpoints allow — \(0.02893293456111476\) s, the upper end of the onset interval — and adding the local clock-anchor bound to it returns the capture bound quoted above. These values support only the diagnostic reconstruction of this retained calibration capture; they do not supply the prospective Qwen3 comparison.
<!-- evidence: runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/{events.jsonl,instrument_evidence.json}; commanded edges from events.jsonl pulse_command_on/off #10 metadata.clock_stamp.epoch_s (planned offsets 26.625 s / 27.625 s). The v3-anchored fit rows are re-derived deterministically by joulewise.powermetrics_fiducial.rederive_detection_from_artifacts over the retained raw plist + events.jsonl, reproducing b_fiducial_s = 0.030067931757111657 and projection_evaluated_cell_count = 122859 exactly; the byte-retained pulses[] in this 2026-07-22 file are v2-anchor-era, while fresh _v5 captures byte-retain v3. -->
<!-- evidence: docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json -->
<!-- replay fence: scripts/check_paper_replay_fence.py is the mechanical re-derivation check for this paragraph — it re-runs the anchor and the 59 pulse fits from the capture's primary bytes and requires every literal above to be the same double it re-derives (stored rows and the stored bound are never inputs). -->

### Historical current-method edge result

The following are diagnostic-era instrument statistics — a desk
re-derivation over retained captures whose energy values the repository decision D-078
voids for energy-claim use; they characterise the timing calibration of the instrument and are not
evidence for any new model-energy result. Here diagnostic-era means collected
in the historical July 2026 period. The source is the single capture
`20260722T145535-e941c821`, re-derived under the current rate-aware anchor
`powermetrics_native_second_rate_aware_set_membership_v1`. Its historical
stored pulse fits used an earlier anchor; this analysis recalculates them
from the retained raw power bytes and command events. Re-deriving a historical
capture under the current method does not make it a supplier for a prospective
energy claim.

A best-fit lag is fitted edge time minus its command time: positive means late,
negative means early. Onsets switch work on; offsets switch it off. The 59
onset lags are all positive; 49 of 59 offset lags are negative, eight positive,
and two zero. Their medians—the middle sorted values—are +13.0 ms and
−5.5 ms. These are 59 onset and 59 offset values (118 edges) from one capture,
not independent calibration draws; these sample statistics make no coverage
or independence claim.

![Figure 2. Historical capture re-derived with the current clock method.](figures/fig4_edge_excursions.svg)

*Figure 2. Historical current-method re-derivation, one GPU pulse capture.
The horizontal axis is pulse index 0–58 in command order; the vertical axis
is signed fitted lag in milliseconds, with pale horizontal grid lines and
labelled ticks. Blue circles are the 59 fitted onset lags; orange squares are
the 59 fitted offset lags. The solid black zero line is each edge's commanded
time. Blue and orange dashed horizontal lines mark the respective medians,
+13.0 ms and −5.5 ms; they describe this sample, not a repeatable error or
future coverage. The title, explanatory subtitle, right-hand line labels,
bottom shape legend and notes name those marks and the late/early counts.
The leader at pulse index 9 marks its +27-ms best-fit onset. An **allowed region** contains every edge
pair surviving the fit's discrepancy limit. The allowance
is a different quantity: the largest excursion of an allowed-region endpoint,
28.93293456111476 ms on that onset, plus the 1.1349971959968978-ms clock-anchor
allowance, gives 30.067931757111657 ms. The endpoint excursions and anchor
allowance are described in the notes but are not plotted. The 0.5-ms fitted
lag grid reflects the search step; allowed edge positions range continuously.
The edges share a capture and are dependent. These historical timing
statistics establish neither phase-energy dominance nor transfer to inference
nor future-error coverage.*

A source map links each displayed value or figure mark to its supplying
artifact and field. Source map: registry DX-001 binds `round7/excursion-decomposition.json`;
DX-003 binds this SVG; DX-010/011 bind the two medians; DX-012/013 bind the
59/59 and 49/59 counts. The same JSON's `per_pulse` array supplies each mark;
its `summary.offset_best_fit_lag` supplies the eight positive and two zero
counts. DG-024–042 bind the capture and pulse-9 arithmetic above. Reproduction
from a directory containing the retained `runs_window_a_20260722` tree is:

```bash
python3 -B scripts/paper_excursion_decomposition.py --corpus-root /path/to/corpus --out /tmp/excursion.json --svg /tmp/excursion.svg
```

The producer checks primary-file fingerprints and recalculates the anchor and
pulse fits. Compare its numerical payload and SVG with the registered parents;
the JSON replay-command locator records the supplied corpus path. Section 9
states why public raw-byte replay is currently limited.

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

The following are registered characterization methods, not issued empirical
results. A later campaign must collect their designated inputs and apply the
fixed calculations before claiming characterization. **Floor packs** are the
campaign plans that collect calibration data used to build a comparator floor;
a **contrast pack** is a plan collecting model-comparison data. Their planned
same-condition A/B/B/A blocks build floors and cannot also count as disjoint
characterization evidence. No such report is supplied in this submission.

For workload response, an independent unit is one separately admitted bundle,
not one sampler record within it. A workload-response slope is the fitted
change in energy per output token. A fitted residual is one observed energy
minus the straight-line value predicted for its output length. The residual
must fit both the bundle's allowed timing half-width and a floor issued earlier
for that same cell.

For one A/B/B/A block, let
\(\delta=(B_1+B_2-A_1-A_2)/2\). Each of the four member energies has its
recorded value at its phase boundaries and an edge-moved allowance
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
The mean interval over the five identical-condition null-test blocks—blocks in
which both conditions are the same—is
\(I_{\mathrm{mean}}=[\sum_i\delta_i^-/5,\sum_i\delta_i^+/5]\). Let
\(C=[-m,+m]\) be the earlier comparator, where \(m\) is its positive joule
endpoint, and define the largest absolute allowed block difference as
\[
M=\max_i\max(|\delta_i^-|,|\delta_i^+|).
\]
No issued null-ladder member endpoints are available, so this construction is
symbolic rather than measured. The forcing problem is that a point value can
hide an allowed nonzero difference, while a mean can hide blocks moving in
opposite directions. The containment test therefore requires every \(I_i\) to
contain zero, then requires \(I_{\mathrm{mean}}\subseteq C\) and \(M\le m\).

Here is a numeric illustration, not measured evidence: its comparator is
\([-3\ \mathrm{J},+3\ \mathrm{J}]\), and its five block intervals, all in
joules, are \([-2,+2]\), \([-1,+1]\), \([-0.5,+0.5]\),
\([-1.5,+1.5]\), and \([-1,+1]\). For this numeric illustration, the
lower endpoints sum to \(-6\) J and the upper endpoints to \(+6\) J, so
\(I_{\mathrm{mean}}=[-1.2\ \mathrm{J},+1.2\ \mathrm{J}]\) and \(M=2\) J.
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
\(D=E_{\mathrm{prefill}}+E_{\mathrm{decode}}-E_{\mathrm{request}}\) is the signed energy left
after subtracting the enclosing request from the two phase energies. A positive
value is double-counted energy. A negative value may be energy in the unphased gap,
the recorded interval between the end of prefill and the start of decode;
its duration times its largest recorded **package power**—the summed CPU, GPU,
and neural-engine power—bounds what may be missing. A resolution band is the
symmetric allowed slope range made from one
admitted prefill half-width across the observed output span. A floor band is
the analogous range made from an independently issued prefill floor. The
shared session timing term is the one bracket-capture timing bound common to
all session members; member-local timing is each run's own local and edge-span
contribution. Timing flags mark a member whose clock bound exceeds a quarter
of its window. Sampling flags mark too few in-window sampler records or a
window whose sampling cadence cannot be recorded or does not stay above a
fixed multiple of the phase rate. The required multiples are the design
constants `SHORT_WINDOW_CADENCE_RATIO_MIN = 2.0` for a short phase window and
`REQUEST_WINDOW_CADENCE_RATIO_MIN = 4.0` for a request window. A missing ratio
records `cadence_ratio_unrecorded`; a ratio below its required multiple records
`cadence_ratio_below_threshold` in `joulewise/reduce.py`.

For drift and recovery, reference roles identify the allowance-building runs
at the window opening, midpoint, and close and distinguish the held-out probes
that cannot enter that allowance. A passing cooldown exit is the first gate
evaluation after a sustained workload whose complete thirty-second rolling
window has at least eighty-percent duration coverage, duration-weighted mean
power no greater than one-and-one-tenth times the clean reference, and nominal
thermal pressure; elapsed recovery time starts when the sustained workload
ends and stops at that first pass.

The registered minimum basis is forty admitted bundles over five output
lengths for workload response; five disjoint A/B/B/A test blocks at each
null-test magnitude; twenty-four admitted bundles and two bracket captures for
phase accounting; and six designated reference members, three held-out probes,
and three sustained-work/cooldown pairs for drift and recovery. A **workload level** is one output-token count fixed before collection, and a **workload magnitude** is one target size in the null test. Failure withdraws the relevant
**per-token conversion**, the fitted joules per output token, floor, or
phase-specific claim. These are design requirements, not counts collected
for this paper.

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
This shortcut does not apply to the separate moved-edge-limit calculation: it
recalculates a mean and sample standard deviation at every joint endpoint
choice. Changing one endpoint changes both quantities and the largest
residual, so this nonlinear calculation refuses exact enumeration above sixteen
observations.

If issued, an identical-condition result would have a deliberately narrow
meaning: five contained measured blocks would establish only the containment
drawn above. It would neither estimate a percentage of a wider population nor
supply an independent coverage guarantee. <!-- reviewer C5: containment caveat -->

## 4. How the method quantifies assigned-energy sensitivity

To clip a record is to keep only the part of its time interval inside the
phase, then multiply that duration by the record's average power. For example,
a 30-W record from 1.000 to 1.100 s cut at a phase boundary of 1.040 s gives
prompt processing \(30\times0.040=1.20\) J and token generation
\(30\times0.060=1.80\) J. Moving the permitted boundary to 1.050 s would
instead give 1.50 J to each phase. This 0.30-J movement is the allocation
sensitivity calculated under the held-average reconstruction; it is not a
physical enclosure for arbitrary within-record power allocations.

### Comparing the moved-edge limit and point-only value

The forcing problem is that any positive boundary interval can make a
moved-edge limit exceed a point-only value, so mere exceedance cannot show
that boundary placement is the limiting uncertainty. The comparison therefore
asks for a fixed twofold increase in the complete bound, not just a positive
increase in one timing term.

A cell groups runs that use the same phase, workload, model, hardware,
software, and power-measurement boundary. It has two false-difference
components. The **absolute component** measures spread among repeated runs of
one model. The **comparative component** measures differences from four-run
blocks executed in A, B, B, A order. If the four phase energies in one block
are \(A_1,B_1,B_2,A_2\), the block difference is

\[
\delta=(B_1+B_2-A_1-A_2)/2.
\]

A positive difference means condition B used more assigned phase energy than
A. A/B/B/A balances order and suppresses a linear trend only under the
specified timing symmetry: the A and B run-midpoint sums must match. Unequal
runtimes or cooldowns break that balance; curved change is addressed only by a
separate empirical whole-window allowance.

A later factor that widens a result to allow for limited repetition is applied
before the whole-window allowance; neither enters the first calculation. For
either component, first calculate its **point-only unguarded value**;
“unguarded” means that neither has yet been applied. An
**admitted energy** is an energy from a run that passed the Section 5 entry
checks and may therefore bear a claim. “Point only” means using each admitted
energy at its recorded value. The later factor is the **small-sample
multiplier**. Here \(n\), the number of
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

The first term preserves the largest displacement already observed. Under the
independent-normal model, the second is a two-sided 95% prediction amount for
one further observation; it is not a deterministic future-error bound. For block
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

For a worked example of that bound, take five repeated energies 8, 9, 10, 11,
and 12 J. Their mean is 10 J, their residuals are −2, −1, 0, 1, and 2 J,
and their sample standard deviation is \(\sqrt{10/4}=1.581139\) J. Using the
code's fixed three-decimal lookup-table convention, \(t_{.975,4}=2.776\), and
the prediction amount is \(2.776\times1.581139\times\sqrt{1.2}=4.808173\) J,
larger than the 2 J observed residual, so
\(U_{\mathrm{abs,point}}=4.808173\) J. If five
block differences are 0, 1, 2, 3, and 4 J, their mean is 2 J and their sample
standard deviation is again 1.581139 J; therefore
\(U_{\mathrm{cmp,point}}=\max(4,2+4.808173)=6.808173\) J. These values
demonstrate the formulas and are not campaign evidence.

Each admitted energy also has a lower and upper value obtained by moving its
phase boundaries through every position allowed by the session calibration. To
calculate the **moved-edge limit**, choose either the lower or
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

The moved-edge limit and point-only value therefore use the same complete
unguarded formula, once after allowed edge movement and once at the recorded points.
Neither is a timing term alone or a value after the multiplier or
whole-window allowance is added. In this paper, allowed boundary movement
**dominates** a component only when \(R\ge2\): it adds at least one entire
point-only value. Exact equality at \(R=2\) passes. A threshold merely above 1
would let any positive interval width do the decisive work. If
\(U_{\mathrm{point}}=0\), the program refuses with the fixed reason name
`dominance_ratio_zero_denominator`; it does not print infinity.

Here, **authenticated** means that the evidence, plan, and post-campaign
**close-out artifact**, which checks every required ratio, carry the expected
SHA-256 fingerprints and their named inputs agree. A
missing fingerprint, a mismatch, or a required input that cannot be checked is
unauthenticated and cannot select a ratio outcome.

The comparative \(R_{cm}\) diagnostic first derives a block-level energy
allowance from shared start and end movements within each A/B/B/A block. This
within-block construction is not a global common-time replay across blocks.
For a block \(j\), start
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

Thus \(q_j\) is the nonnegative block-level energy allowance from the farther
shared start-plus-end movement, plus any difference between recomputing energy
at zero shift and the admitted block value. The
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
bound by the comparative point-only value. Retaining the same sign for the
scalar \(q_j\) allowances does not preserve or replay one physical time shift;
their extrema can arise at different timing coordinates. This quotient is the
comparative **shared-energy-sign/local-corner ratio** \(R_{cm}\):

\[
R_{cm}=\frac{U_{\mathrm{cmp,shared}}}
             {U_{\mathrm{cmp,point}}}.
\]

The same zero-denominator refusal applies. A comparative \(R_{cm}<2\)
withdraws the boundary-doubling sentence even when \(R\ge2\). Absolute
\(R_{cm}\) remains `not_applicable` because the registered replay is
comparative-only, not because absolute timing uncertainty vanishes.

A retained two-block fixture makes the replay checkable. SYNTHETIC ARITHMETIC
ONLY: it is a test fixture, not a new hardware result or campaign evidence. The Student-\(t\) critical used by the two-block interval is
\(t_{0.975,1}=12.706\), the fixed-table value `_T_CRITICAL_95[1] = 12.706` in
`joulewise/aggregate.py`, returned by `student_t_critical_95` and used by
`joulewise/detection_floor.py`; the artifact records
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
the arithmetic only. Source map: `tests/fixtures/fcm_r4_real_blocks/measured_pair.json`
contains `blocks` with each point difference, onset/offset extrema and local
member residual; `joulewise/detection_floor.py` implements the shared/local
enumeration. The filename is a historical fixture label and confers no
empirical authority. The full fixture and its SHA-256 are recorded in registry
SYN-01; the printed operands above reproduce the quotient to the stated
precision without a raw capture.

### Adding publication safeguards after the ratio

The ratio is calculated before the safeguards used to publish the final
resolution bound, the registered operational guard for assigned-energy
differences in this cell. The final resolution bound is called the cell floor
in the artifacts. A **same-cell floor** is that artifact for exactly the phase,
workload, model, hardware, software, and power-measurement boundary being tested. For
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
fall: A/B/B/A suppresses a steady straight-line change only when the A and B
run-midpoint sums match, and it does not remove a path that turns between
references. Then \(A_k\) is the larger of that independent bound
and the observed excursion. Thus reference means 10.0, 10.6, and 10.2 J have
an excursion of \(10.6-10.0=0.6\) J; with an issued 0.4-J repeatability bound,
\(A_k=\max(0.6,0.4)=0.6\) J. This empirical allowance samples the registered
reference epochs; it is not a deterministic bound on arbitrary unobserved
excursions between them. It is a joule quantity and is distinct from the
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
unguarded moved-edge limits of 1.6656 J absolute and 1.7656 J comparative. With
\(g(5)=1.5\) and a 0.4 J allowance for each component, the published values
are \(1.5(1.6656)+0.4=2.8984\) J and
\(1.5(1.7656)+0.4=3.0484\) J. Their maximum, 3.0484 J, is the cell floor.
The example's point-only values are zero, so it demonstrates floor composition
but correctly refuses \(R\); it supplies no boundary-doubling result.

Two directional comparisons—token generation and prompt processing, each with
its expected direction fixed before collection—share one two-sided Holm
step-down correction. We apply Holm at nominal family-wise level 0.05 to two
model-based tests; error control depends on their distributional and dependence
assumptions. For each block \(i\), first form its paired difference
\(d_i=B_i-A_i\), condition B's mean energy in that A/B/B/A block minus
condition A's mean energy. For the gross phase-energy contrasts used here, the
current builder supplies no additional stochastic metrology variance, so the
**repeat standard error** is the standard error of the block differences,
\(se_{\mathrm{repeat}}=s/\sqrt{n}\), where \(s\) is their sample standard
deviation. Timing and other deterministic allowances are propagated
separately. Divide the mean \(\bar d\) by \(se_{\mathrm{repeat}}\); with
\(n=10\), the Student-\(t\) reference has \(n-1=9\) degrees of freedom. The null
hypothesis is zero mean difference; “two-sided” counts equally extreme positive
and negative statistics. The resulting tail area is that comparison's **raw
probability** \(p\).

An illustrative, not campaign data, fixture uses ten block differences in
joules: \([5.0,7.6,5.5,4.2,4.7,6.8,5.5,3.6,3.9,3.2]\). Their mean is
\(5.0\) J, their squared deviations sum to
\(\sum_i(d_i-5.0)^2=17.64\ \mathrm{J}^2\), and therefore
\(s=\sqrt{17.64/9}=1.4\) J and
\(se_{\mathrm{repeat}}=1.4/\sqrt{10}=0.442719\) J. With no additional
stochastic metrology term on this phase path, \(t=5.0/0.442719=11.2938\) on 9
degrees of freedom, with two-sided \(p=1.29\times10^{-6}\). The separate
dependence-sensitivity sheet,
`docs/paper/round7/dependence-sensitivity.md`, works the same ten differences
under a stipulated effective-sample-size halving and an estimated AR(1) model,
which treats adjacent block errors as serially correlated. Those alternatives
are sensitivity scenarios, not estimates of independence for the campaign.

Order the two raw probabilities \(p_{(1)}\le p_{(2)}\). Compare the first with
0.025; only if it passes, compare the second with 0.05. Pairing that
\(1.29\times10^{-6}\) with a second illustrative raw probability of \(0.041\) for
the other comparison orders them as \(1.29\times10^{-6}<0.041\): the smaller
passes 0.025, then 0.041 passes 0.05, so both directional comparisons pass
Holm. If one contrast is missing, its slot remains: a sole value 0.041 is
compared with 0.025 and fails, while the missing contrast cannot pass. Holm is
one step; the decision-interval sign check (the direction gate) in the next
paragraph is the other. The sheet's \(\nu=9\) row adds a stipulated
0.2-J stochastic metrology standard error to these same deltas; its different
raw probability also passes Holm, but its decision interval fails the
direction gate. That composition example is not a campaign input.

A directional result then faces two different checks. The magnitude check
requires the absolute point estimate to exceed \(F_{\mathrm{cell}}\); failure
means **not resolvable**—the estimate does not clear the cell floor—not zero.
The direction check requires the measurement interval, formed from the repeat
standard error already defined for this gross phase-energy path, and the
decision interval, formed by extending both ends by the sum of the recorded
deterministic bounds. A deterministic bound is a
non-random maximum displacement carried in the authenticated block record.
A **reducer** is the program that turns a retained run bundle into phase energies.
For native interval-average records, the reducer integrates constant reported power
over the overlap duration; its interpolation-bound term is zero. Timing
uncertainty enters through separately recomputed boundary envelopes. An
**interpolation edge** is the point-sample fallback's phase-window start or end
between neighboring point samples. The named **deterministic-bound kinds** are
that fallback's joint interpolation-edge movement, idle-power drift for
idle-subtracted request energy, clock-anchor movement, and
the whole-window drift allowance. For each kind, use its recorded contrast bound when present, otherwise
add its A-side and B-side bounds; average that kind across the ten blocks, then
sum those kind averages. Both intervals must lie wholly on the direction fixed
before collection and the Holm-adjusted test must pass. In the synthetic
example, a 10.0-J point estimate exceeds the 3.0484-J floor. Its measurement
interval is [9.5, 10.5] J. If the authenticated deterministic-bound list for
that example contains 0.10 J and 0.15 J, its sum is 0.25 J and the decision
interval is [\(9.5-0.25\), \(10.5+0.25\)] = [9.25, 10.75] J. Both intervals
remain positive and the adjusted test passes, so the example supports the
positive direction.

The floor and decision interval remain separate mandatory gates. For a
symmetric measurement interval with half-width \(h\) and symmetric nonnegative
deterministic widening \(B\), their numerical conjunction is
\(|\mathrm{estimate}|>\max(F,h+B)\); asymmetric intervals use their actual
endpoints. \(F+B\) is only a non-gating planning diagnostic, neither necessary
nor sufficient for acceptance, and neither mandatory gate may be removed as
double counting.

The method's **signed clearance or shortfall** is the absolute point
estimate minus the cell floor. A positive value is the amount by which the
magnitude check clears; zero or a negative value is the shortfall and cannot
pass. The synthetic example prints \(10.0-3.0484=6.9516\) J. This difference
summarizes the magnitude check; it does not replace either uncertainty
interval used by the direction check.

### Evidence refusal and claim gates

The schematic describes the method's possible decisions; this paper reports
no new model-comparison verdict.

Figure 3 separates evidence refusal from the two claim gates. An admission
failure means the stage did not pass the entry check. **Custody** means that
each named input's fingerprint still matches its recorded bytes; a custody
failure means at least one does not. Missing, stale,
contaminated, duplicated, inconsistent, or unauthenticated evidence enters a
side path and is refused before either gate. Usable evidence carries a point
estimate and its complete uncertainty interval to the magnitude gate; a value
that clears the cell floor then reaches the direction gate. The four
possible outcomes are refusal, not resolvable, direction unresolved, and a
directional claim.

![Figure 3. Evidence refusal and two sequential claim gates.](figures/fig3_decision_gates.svg)

*Figure 3. Decision-gate schematic; no measured data or numeric threshold is encoded by its layout. On the white background, the title and subtitle identify two gates and four outcomes. In the upper lane, a dashed box lists an admission or custody failure and the six evidence defects that can cause it; a right-pointing arrow labelled as a side entry that reaches no gate leads to the bordered “refused” box, which says that the evidence produces no result. A pale horizontal rule separates that refusal lane from the lower decision lane. The lower lane starts with a gray measured-contrast box containing the point estimate and composed uncertainty interval. A right-pointing arrow leads to the first white rounded box, Gate 1, which asks whether the estimate's magnitude exceeds the cell floor. Its “yes” arrow leads to the second white rounded box, Gate 2, which asks whether the whole uncertainty interval points one way; the next “yes” arrow leads to the blue directional-claim box, which states that both gates passed in the direction registered before collection. Gate 1's downward “no” arrow leads to the “not resolvable” box, which says the effect is smaller than this instrument can resolve and does not mean zero, equality, or no difference. Gate 2's downward “no” arrow leads to the “direction unresolved” box, which says the floor cleared but the interval did not settle direction, so no claim is made. The bottom notes define the cell floor as the registered operational resolution guard for assigned-energy differences, retain the separate floor and interval gates, and identify F+B—floor plus deterministic widening—as a non-gating planning diagnostic, neither necessary nor sufficient for acceptance.*

## 5. Collection stops when required evidence fails

If a required measurement is missing, malformed, outside its fixed limit, or inconsistent with another record, collection stops and records why; the program never substitutes a favorable value or silently skips the member. This behavior is *fail-closed*. The unit governed this way is a measurement window, including its calibrations, declared runs, cooldowns, and final verdict.

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

The refusal log is part of the result. It preserves contaminated members, calibration outside the allowed condition family, stale drift evidence, unresolved clock anchors, duplicate recorded occurrences, and below-floor effects. These are specified refusal behaviors; no missing campaign result is treated as an observed empirical refusal.

The repository is tamper-evident for the operator's own benefit—a way to catch mistakes—not tamper-proof against another program or person. It assumes a single trusted operator, so its gates defend against error and post-hoc choice rather than an adversary; they provide internal consistency, not third-party provenance (evidence that would convince someone who does not trust the operator).

The repository artifact guide holds the maintainer-facing path conventions,
**freeze receipts**—records that fix the plan bytes and the time those bytes
were frozen—generated-state checks, and reissue workflow; Appendix A retains
the scientific route from raw bytes to the reported verdict.

## 6. Historical record-support result

### Printed negative result: short prompt processing has too few overlapping records

Section 1 introduced a sampling record as one sampler output that averages
processor power from its recorded start time to its recorded end time. That
start-to-end span is the sampling record's interval; its duration is the
**record width**. For a prompt-processing phase with start and end times
\(p_s\) and \(p_e\), and a sampling record with start and end times \(r_s\) and
\(r_e\), the sampling record has **positive overlap** with the phase exactly when
\[
\min(p_e,r_e)>\max(p_s,r_s).
\]
The **overlap count**, also called **record support**, is the number of sampling
records with positive overlap. A sampling record that crosses a phase boundary
counts because the shared part has positive duration; one that only touches an
edge does not. The overlap count, record support, and the three-record minimum
are the same test: count the sampling records with positive overlap, and
calculate phase energy only when the count reaches the minimum. For this use,
**resolvability** asks only whether record support reaches that minimum. With
fewer than three overlapping sampling records, the phase prints **not
resolvable** because its record support is too small, using the label
`not_resolvable_sample_count`; Section 4 uses the same verdict words for a
different reason, an estimate that does not clear the cell floor.

Figure 4, the phase–record overlap diagram, names the phase boundaries, adjacent
sampling-record intervals, shared portions, overlap count, and three-record
minimum for both sides of the decision.

![Figure 4. Phase–record overlap diagram.](figures/fig5_phase_record_overlap.svg)

*Figure 4. Phase–record overlap diagram. Both prompt-processing intervals have
the same illustrative width. In the upper row, sampling records about as wide
as the phase are misaligned with it: the phase straddles one record boundary and
overlaps two records. In the lower row, a shorter middle sampling record lies
entirely between the phase boundaries, producing three positive overlaps. Every
drawn data mark is labelled: each sampling record, prompt-processing interval,
phase boundary, positive-overlap segment, count box, decision, and axis. Widths and
positions are not to scale; the count labels explain the three-record minimum
rather than population frequencies, and the diagram contains no measured timing
value.*

The forcing problem appears in one run whose power trace was retained, meaning
kept on disk as preserved evidence and never overwritten. Its prompt-processing phase
lasted 0.121034145 s, rendered as 0.121 s for the comparison below. Over that
run's retained power trace, the 406 sampling records had a record-width median
of 120.9186 ms. An
interquartile range (IQR) is the upper edge minus the lower edge of the middle
half of sorted values; the width IQR was 5.9508 ms. Across the 405 differences
between consecutive unique recorded timestamps, record spacing had median
120.9224 ms and IQR 5.8949 ms. The program that issued these statistics refuses
the trace unless each sampling record's interval-end label is identical to its
timestamp label. It also checks that each sampling record begins within
0.000001 s of the previous record's end. The [issued statistics
artifact](round7/dg071-dg075-statistics.md) reports that 100 of 405 boundaries
have a nonzero gap and that the largest is 0.0000004 s. The enforced endpoint
equality makes a spacing statistic over consecutive timestamps a statistic over
consecutive end times.

The 0.121-s phase is only barely longer than the median-width sampling record,
and dividing phase duration by either issued median cannot reproduce the
decision because division discards the phase's position relative to record
boundaries. Three overlaps require one whole middle sampling record to lie
between the phase boundaries: the phase must start before that record and end after
it. When the phase and middle record have about the same width, only a very
narrow range of relative positions satisfies both conditions. A middle record
at the short end of the issued middle-half width spread leaves more room for
both phase boundaries to fall outside it, making that full fit easier rather than
first making it possible. Alignment, not width alone, therefore denies the
third overlap in most phases. In this run, exactly two sampling records shared
positive time with the phase. Two is less than the required three, so the phase
was not resolvable.

The population consists of short prompt-processing phases from the earlier
1.5-billion-parameter diagnostic configuration during the July 2026 window.
Across this retained population, 37 of 50 phases overlapped two sampling
records and the remaining 13 of 50 overlapped three. Accordingly, 37 failed
the three-record minimum and 13 passed it. This describes the retained
population; it does not estimate the failure rate on future requests, show
zero prompt-processing energy, or supply a model comparison.

Source map: registry DG-067/068/069 binds the 37/50/13 counts to
`docs/process_traces/2026-08-09-prefill-phase-proof/results.json`,
`stack_summaries[stack="1.5B"].bundle_count` and `.resolvability`.
DG-072/073/076/077 bind the two/three overlaps and minimum to the same
artifact's per-bundle records and `prefill_overlap_sample_count` histogram.
DG-070/074 bind the example's duration to its phase-start/end events;
DG-071/075 bind its record widths and spacings to the issued statistics JSON
and Markdown. Each of the 50 bundles occurs once in the population. The source
report's raw-to-CSV checks matched the native power records; its source-code
provenance and per-bundle configuration fingerprints are retained. This is
historical descriptive evidence, not a prospective inference-energy result.

A future prefill selection should count actual overlaps for every probe,
rather than divide duration by mean or median record width. The registered
length ladder tests 512, 1024, 2048, and 4096 prompt tokens, at least five
small-model probes at each length, and selects the shortest rung whose every
probe has at least five overlaps. Five provides two extra overlaps beyond the
three needed for a phase calculation. If none passes, its collection length
is 4096; that design choice alone is not an empirical refusal. This procedure
was not performed for this paper, and no selected length is reported.

## 7. Discussion and limitations

The historical calibration shows asymmetric fitted edge placement in one
capture. The record-support result shows a separate limitation: a short phase
can cross too few records even when the records tile continuously. Neither
result establishes a prospective energy difference between models. The
synthetic examples explain how recorded averages support an allocation and
how permitted timing changes alter it; they do not validate the physical
power distribution within a record.

Transfer of the pulse-derived timing allowance to inference was not tested.
The shared-energy-sign/local-corner ratio is a sensitivity calculation with
no proven conservatism for physical common-time motion. The published-floor
and decision-interval roles remain mandatory in the method; their sum is
planning information, not an acceptance guarantee.

### Further limitations

<!-- Source: docs/paper/round7/survival-map.md; reviewer items C9, D6, D7, D8, D9, D11; ranked items 12, 15, 16. -->

First, the pulse-to-inference transfer was not tested. The calibration commands
long, square GPU work and measures how its reported edges differ from the
commanded edges, whereas inference has a different sequence of GPU work at the
transition from prompt processing to token generation. A difference in those
two physical edge responses could make the pulse-derived limit either
too narrow or unnecessarily wide; its effect on the reported phase energies is
unquantified. The retained diagnostic capture's pulse-derived limit was
\(0.030067931757111657\) s. <!-- DG-027; MEASURED / DIAGNOSTIC_ERA / REPLAY_FENCED. --> This is a calibration value, not a bound on real inference. The paper therefore does not apply it as an inference-error bound or make a later inserted-gap result a submission predicate.

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
power share the same start-to-end averaging window, so the same phase boundaries
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

Fourth, the prospective design's ten blocks in one measurement window would not automatically be ten
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
\(d_i=(B_{i1}+B_{i2}-A_{i1}-A_{i2})/2\). For this path, the **total standard error** equals the modeled repeat
standard error, with no additional stochastic metrology variance. The
sensitivity calculation is

\[
\begin{aligned}
s&=\text{sample standard deviation of the complete block differences},\\
n&=\text{number of complete blocks},\\
V&=\text{variance multiplier supplied by the selected dependence model},\\
n_{\mathrm{eff}}&=n/V=\text{number of independent blocks with the same repeat standard error},\\
\nu&=\text{Student-}t\text{ degrees of freedom supplied by that model},\\
\mathrm{SE}_{\mathrm{repeat,model}}&=s\sqrt{V}/\sqrt{n}=s/\sqrt{n_{\mathrm{eff}}},\\
\mathrm{SE}_{\mathrm{total}}&=\mathrm{SE}_{\mathrm{repeat,model}}
\quad\text{for the gross phase-energy path used here}.
\end{aligned}
\]

The registered independent-block model supplies \(V=1\),
\(n_{\mathrm{eff}}=n\), and \(\nu=n-1\). The AR(1) estimated-adjacency model,
which relates each block to the immediately preceding block, supplies \(V\)
from its finite sum over the estimated correlation between successive block
differences and uses
\(\nu=\min(n-1,\lfloor n_{\mathrm{eff}}\rfloor-1)\). The named fixed effective-
sample-size halving case supplies \(V=2\), \(n_{\mathrm{eff}}=5\), and \(\nu=4\).
For these gross phase-energy contrasts the current builder supplies no
additional stochastic metrology variance, so \(SE_{\mathrm{metrology}}=0\) on
this path and each model's total stochastic standard error reduces to its
modeled repeat standard error. The dependence-sensitivity sheet's worked
example stipulates a nonzero \(se_{\mathrm{metrology}}\) and is an arithmetic
check of the composition, not a campaign input. Timing and other deterministic
allowances remain separate. <!-- Pre-registered design/model
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
The identical-condition null illustration covers only its five synthetic
intervals. Even a later measured pass would establish neither population
coverage nor equality. <!-- DS-03; KEY_FROZEN /
VALUE_UNISSUED. Five-block design: docs/contracts/analysis_plans.md:380-381;
reviewer D11; ranked item 16. -->
The exact closing check is to retain all blocks in collection order, rerun the
registered independent-block calculation and every pre-registered dependence
sensitivity model, and compare their total standard errors, degrees of freedom,
intervals, and direction gates without changing the member set.

Fifth, the generic floor consumer does not independently rederive every
uncertainty width from primary inputs. It binds configurations, membership,
identities and point metrics; its floor validator recomposes the result from
widths supplied by the floor artifact. The mint performs a stronger
source-based width comparison. Thus a coherently produced wrong-width artifact
is not independently caught at every consumption boundary. Byte seals catch
later substitution but do not close that production-error gap. This submission
publishes no new floor; the gap is a limit of the reusable method, not a
claim that an unissued floor was reproduced. Section 9 describes the separate
paper-input custody requirement and public reproduction limits.

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

The inserted-gap study remains possible future diagnostic work; it is not a
predicate for this submission and this paper has not run it. Its gap, run count,
estimator, and residual comparison are fixed before collection. It is a proposed
design, not yet a runnable protocol: its sleep
actuation, command-stamp method, and fitted-edge selection remain to be fixed.
Hold model identity, prompt, tokenizer, and
generation rules fixed at the values registered for the campaign. In each of
about ten otherwise identical real-workload runs, insert an approximately
500-ms commanded sleep during which the inference workload submits no GPU work.
Place it after the runtime stamps prefill completion and before it stamps decode
start. Retain both command stamps, the surrounding power records, the before-
and-after calibration bracket, and every refusal record. <!-- TRANSFER-FIDUCIAL-01 at
docs/process/state_kernel.json:/tasks/TRANSFER-FIDUCIAL-01; runtime events:
joulewise/adapters/mlx_runtime.py:795-809 emits phase_end/prefill, "mlx prefill
completed", and phase_start/decode, "mlx decode started". -->

Apply the detector that Section 2 defines for commanded pulse edges, without
modification, to the falling edge when the sleep begins and the rising edge
when decode resumes. For each edge
\(e\), define
\(r_e=t_{\mathrm{fit},e}-t_{\mathrm{command},e}\), where
\(t_{\mathrm{fit},e}\) is the detector's fitted edge time and
\(t_{\mathrm{command},e}\) is that edge's independently stamped command time.
Report every signed \(r_e\) and record its comparison with
\(B_{\mathrm{fiducial}}\), where
\(B_{\mathrm{fiducial}}=0.030067931757111657\) s is the retained diagnostic
capture's pulse-derived limit. <!-- DG-027; MEASURED / DIAGNOSTIC_ERA /
REPLAY_FENCED. --> The registered row does not prescribe an acceptance
threshold for that comparison, so this paper does not label a result a pass or
transfer failure. A reader can recompute both residuals from the retained
command stamps and power trace.

The external-meter study is a proposed design, not yet a runnable protocol: its
tested load settings—its workload levels—meter synchronization, and allowable range for \(g\) remain to
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

Running Average Power Limit (RAPL) is a processor-exposed energy counter. Khan et al.'s *RAPL in Action* and Jay et al. own the gain axis: how accurately a software counter reports the magnitude of energy use [4] [5]. For phase-resolved `powermetrics` inference on Apple Silicon, JouleWise opens the complementary time axis: where in time a counter places the energy it reports. Khan et al. align lag, model the relationship between RAPL and wall power, account for temporal correlation, and inspect update granularity, sampler overhead, jitter, overflow, and timestamps [4]. Jay et al. show through controlled regression against wall power that disagreement changes with load, and they decline component claims that their reference meter cannot test [5]. Those studies establish how to validate counter gain; an external wall meter still cannot determine how a software trace should divide a correct total between prompt processing and token generation.

Hähnel et al. are the closest ancestor to this boundary problem. RAPL's update interval limits how short a code path can receive a defensible energy attribution, and they respond by aligning the start and end of the measured path to the counter's own update boundaries — spinning on the register until it advances before entering the code path, and again on leaving it — then enumerating the errors that remain when entry and exit fall inside a single update interval [19]. That is edge placement as an explicit technique, on a different interface and at a different scale. Dauner et al. provide the strongest corroboration. Across RAPL and the NVIDIA Management Library (NVML) software power counter, they show that counter-update behavior and requested sampling frequency can materially change an energy reading; on one evaluated GPU, very frequent polling severely underestimated integrated power, with agreement recovering only at a much longer interval [15]. JouleWise's distinct contribution is to calibrate runtime phase boundaries in the same measurement window, propagate their permitted positions through the energy integral, and make the resulting cell-specific resolution bound a claim gate (Sections 2, 3, and 5).

### Large-language-model energy measurement

A large-language model (LLM) generates text by predicting successive tokens,
its units for representing text.

*The Illusion of Power Capping in LLM Decode* is the closest methodological rival. It is phase-aware, repeats configurations, and independently checks sufficiently long sampled-power integrals against a hardware energy counter [13]. JouleWise lacks that independent cross-check. Its narrower advance is different: the power-capping study reports counter agreement, repetition, and timing regimes as separate diagnostics, whereas JouleWise carries registered phase-edge perturbations into the allocation-sensitivity calculation that decides whether a phase contrast may be reported.

TokenPowerBench reports prefill and decode energy and groups measurements by context length [6]. Its disclosed method does not specify the boundary events, alignment rule, repetition and variance protocol, idle baseline, or external validation needed to reconstruct a phase-attribution error budget. Ruf and Detyniecki isolate prefill by generating one token and infer decode by subtraction, from one run per context length without error bars [12]. Broader efforts such as ML.ENERGY, Intelligence per Watt, and Apple-focused inference characterizations map energy across useful deployed configurations [7] [14], and Benazir and Lin characterize inference throughput on Apple silicon without energy measurement [10]. They answer system-selection questions; JouleWise instead asks whether one named software-counter boundary can support a phase claim at all.

### Benchmark and metrology lineage

JouleSort established that an energy-efficiency benchmark needs a fixed workload, a comparison metric, and explicit rules for executing the workload and measuring energy [3]. Its boundary is specific: wall power includes conversion losses and every participating component, including idle components; any net change in stored battery energy must be shown no greater than zero with 95% confidence or included in the total. JouleSort also identified synchronization between meter readings and the actual run, alongside the meter's ±1.5% specification, as a reason not to use a fixed-energy-budget metric. JouleWise inherits that boundary discipline rather than replacing it: JouleSort names the synchronization problem at whole-run scale; JouleWise measures its consequence at phase scale.

SPECpower fixes a graduated-load server workload and accepted-analyzer reporting discipline [11]. MLPerf Power extends public energy benchmarking across machine-learning systems, while its associated SPEC methodology requires load-specific analyzer uncertainty, fixed ranges, minimum measurement intervals, invalid-sample accounting, clock synchronization, and controlled battery behavior [1] [2]. JouleWise translates their run-level refusal discipline to a consumer software counter: missing timing evidence invalidates the phase claim rather than disappearing into an average.

Rigorous performance metrology supplies the experimental lineage. Georges, Buytaert, and Eeckhout make repetition, warmup, independence, and uncertainty part of performance evaluation [20]. Mytkowicz et al. show that apparently harmless experimental choices can create systematic measurement bias [21]. JouleWise operationalizes those warnings through paired order, bracketed calibration, fixed-before-collection rules, and explicit refusals, while evidence from one host and configuration cannot establish generality.

Paired minimum-detectable-effect methods use paired variation to estimate the smallest effect a planned study has adequate power to detect. They can allow observed variability to raise, but not lower, a threshold fixed by pre-registration—before results are seen [16]. That work concerns quantization-accuracy benchmarking, not energy. JouleWise borrows its prospective discipline, but treats movement over the registered phase-edge domain as deterministic allocation sensitivity and does not combine it statistically as though it were independent random noise; doing so would take credit for cancellation that the instrument has not demonstrated.

Split and disaggregated inference remain a demanding application rather than this capstone's contribution. Prior work reports whole-run or GPU-only energy for disaggregation and phase-aware placement [17] [9] [8], while SplitZip makes no energy claim [18]. A future JouleWise study would need named boundaries at both endpoints, cross-device clock alignment, and a resolution bound established before collection.

## 9. Evidence and code availability

The project checkout contains the source code, registered plans, tests,
synthetic fixtures, figure SVGs and small issued diagnostic JSON/Markdown
artifacts named in the source maps. Those files allow inspection of the
algorithms and reproduction of the synthetic arithmetic. No public submission
release, evidence-archive locator, release revision, or complete public
fingerprint manifest has issued (registry DS-34). We therefore provide
repository-relative source locations, not a claimed archival release.

The historical native `raw/powermetrics.plist` captures, `events.jsonl`
command/phase logs, `instrument_evidence.json` clock records, and run bundles
are retained under project custody outside Git. The calibration source is
`runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/`;
the record-support sources are the named members of `runs_window_a10_20260725/`.
The registry and issued diagnostic artifacts retain their source fingerprints.
These raw bytes have not been released as a complete public reproduction
archive. Derived JSON and a source hash permit consistency checks but cannot
replace unavailable primary bytes; an outside reader cannot presently repeat
the complete historical raw-byte analysis from the repository alone.

Under D-173, the adopted paper-custody rule, a claim-bearing supplier must
obtain inputs through the typed custody-read interface `open_paper_input(ref)`:
a role name and runs root resolve through a clean-Git supply map to fixed
paths and expected digests, followed by fresh validator replay from disk.
The rule is an input requirement, not evidence that this draft has a released
production supply chain. It does not close the generic floor consumer's
uncertainty-width gap described in Section 7. Any later floor publication
requires a source-member and width census, bracket and basis identifiers,
estimator identity, and an independently reconstructed-versus-published floor
comparison. Correct points with coherently wrong widths cannot count as
source reproduction. No such prospective floor or model verdict is published
here. Hashes provide trusted-operator consistency, not third-party provenance.

## 10. Conclusion

In a current-method re-analysis of one historical GPU pulse capture, all 59 fitted onsets occur after their commands and 49 of 59 fitted offsets occur before them; transfer of its timing allowance to inference remains untested.

JouleWise specifies interval-overlap-assigned phase energy—average power times
overlap duration—and its sensitivity to the registered timing domain,
conditional on the held-average reconstruction, which holds each record at
its reported average. It does not enclose physical phase energy under arbitrary
within-record allocations. The historical record-support population had 37 of
50 phases below the three-record minimum and 13 meeting it. The synthetic P1
enclosure and two-block fixture make the distinct calculations explicit and
reproducible. The result is a methods/diagnostic contribution on one machine
and one software-counter configuration; it supports no new model-energy
comparison, empirical phase-energy dominance, or future-error coverage.
<!-- Headline: DX-001/003/012/013; record support: DG-067/068/069. -->

## 11. References

1. A. Tschand et al. “MLPerf Power: Benchmarking the Energy Efficiency of Machine Learning Systems from μWatts to MWatts for Sustainable AI.” *IEEE International Symposium on High-Performance Computer Architecture (HPCA)*, 2025, pp. 1201–1216. DOI:10.1109/HPCA61900.2025.00092; arXiv:2410.12032.
2. Standard Performance Evaluation Corporation. *Power and Performance Benchmark Methodology*, V2.3. SPECpower Committee. https://www.spec.org/power/docs/SPEC-Power_and_Performance_Methodology.pdf.
3. S. Rivoire, M. A. Shah, P. Ranganathan, and C. Kozyrakis. “JouleSort: A Balanced Energy-Efficiency Benchmark.” *Proceedings of the 2007 ACM SIGMOD International Conference on Management of Data*, 2007, pp. 365–376. DOI:10.1145/1247480.1247522.
4. K. N. Khan, M. Hirki, T. Niemi, J. K. Nurminen, and Z. Ou. “RAPL in Action: Experiences in Using RAPL for Power Measurements.” *ACM Transactions on Modeling and Performance Evaluation of Computing Systems* 3(2), 2018, Article 9. DOI:10.1145/3177754.
5. M. Jay, V. Ostapenco, L. Lefèvre, D. Trystram, A.-C. Orgerie, and B. Fichel. “An Experimental Comparison of Software-Based Power Meters: Focus on CPU and GPU.” *23rd IEEE/ACM International Symposium on Cluster, Cloud and Internet Computing (CCGrid)*, 2023, pp. 106–118. DOI:10.1109/CCGrid57682.2023.00020; HAL:hal-04030223.
6. C. Niu, W. Zhang, J. Li, Y. Zhao, T. Wang, X. Wang, and Y. Chen. “TokenPowerBench: Benchmarking the Power Consumption of LLM Inference.” *Proceedings of the Fortieth AAAI Conference on Artificial Intelligence* 40(38), 2026, pp. 32582–32590. arXiv:2512.03024.
7. J.-W. Chung et al. “The ML.ENERGY Benchmark: Toward Automated Inference Energy Measurement and Optimization.” *Advances in Neural Information Processing Systems, Datasets and Benchmarks Track*, Spotlight, 2025. arXiv:2505.06371.
8. Z. Li et al. “Prima.cpp: Fast 30-70B LLM Inference on Heterogeneous and Low-Resource Home Clusters.” *The Fourteenth International Conference on Learning Representations (ICLR)*, 2026. arXiv:2504.08791.
9. O. Basit, Y. Liu, Z. J. Kong, and Y. C. Hu. “DualScale: Energy-Efficient Disaggregated LLM Serving via Phase-Aware Placement and DVFS.” arXiv preprint, 2026. arXiv:2602.18755.
10. A. Benazir and F. X. Lin. “Benchmarking and Characterization of Large Language Model Inference on Apple Silicon.” *Proceedings of the ACM on Measurement and Analysis of Computing Systems (POMACS)* 9(3), December 2025, pp. 1–26. DOI:10.1145/3771563.
11. K.-D. Lange. “Identifying Shades of Green: The SPECpower Benchmarks.” *IEEE Computer* 42(3), 2009, pp. 95–97. DOI:10.1109/MC.2009.84.
12. B. Ruf and M. Detyniecki. “The Cost of Context: Profiling the Energy Footprint of Input Tokens in Large Language Models.” *HotCarbon '26*, 2026. https://hotcarbon.org/assets/2026/paper-17.pdf.
13. B. Ma, A. Afzal, J. Eitzinger, and G. Wellein. “The Illusion of Power Capping in LLM Decode: A Phase-Aware Energy Characterisation Across Attention Architectures.” arXiv preprint, 2026. arXiv:2605.11999.
14. J. Saad-Falcon, A. Narayan, et al. “Intelligence per Watt: Measuring Intelligence Efficiency of Local AI.” arXiv preprint, 2025. arXiv:2511.07885.
15. M. Dauner, M. Steinberg, A. Brunnert, B. Schicker, and B. Zönnchen. “Evaluating the Influence of Measurement Frequency on Energy Readings Using Intel RAPL and NVIDIA NVML.” *HotCarbon '26*, 2026. https://hotcarbon.org/assets/2026/paper-46.pdf.
16. Z. Zhuang, Y. Li, and Z. Fan. “Pre-Registering the Detectable Effect: A Paired-MDE Budget for 4-bit Quantization Benchmarks, with a Pilot Audit.” arXiv preprint, 2026. arXiv:2605.28873.
17. J. Li, Y. Zhu, B. Chen, E. K. Lee, and K. Nahrstedt. “Revisiting Disaggregated Large Language Model Serving for Performance and Energy Implications.” *Proceedings of the 2026 European Workshop on Machine Learning and Systems (EuroMLSys '26)*, 2026, pp. 397–406. DOI:10.1145/3805621.3807662; arXiv:2601.08833.
18. Y. Guo and S. Joshi. “SplitZip: Ultra Fast Lossless KV Compression for Disaggregated LLM Serving.” arXiv preprint, 2026. arXiv:2605.01708.
19. M. Hähnel, B. Döbel, M. Völp, and H. Härtig. “Measuring energy consumption for short code paths using RAPL.” *ACM SIGMETRICS Performance Evaluation Review* 40(3), 2012, pp. 13–17. DOI:10.1145/2425248.2425252.
20. A. Georges, D. Buytaert, and L. Eeckhout. “Statistically Rigorous Java Performance Evaluation.” *Proceedings of the 22nd Annual ACM SIGPLAN Conference on Object-Oriented Programming Systems, Languages and Applications (OOPSLA '07)*, 2007, pp. 57–76. DOI:10.1145/1297027.1297033.
21. T. Mytkowicz, A. Diwan, M. Hauswirth, and P. F. Sweeney. “Producing Wrong Data Without Doing Anything Obviously Wrong!” *Proceedings of the 14th International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS XIV)*, 2009, pp. 265–276. DOI:10.1145/1508244.1508275.

<!-- Source: draft-v1.md Section 11; bibliography-audit-2026-08-27.md;
round7/bibliography-verification.md (HotCarbon locators); contiguous mapping
per round7/bibliography-renumber-plan.md. Unresolved citations: none.
No new references added. -->

## Appendix A. Reproducing this work

This appendix separates two tasks. *Re-derivation* recomputes reported values from preserved bytes; it needs the released code and evidence, not Apple hardware or administrator privilege. *Fresh collection* creates new evidence and requires the named machine and measurement conditions. A *fingerprint* below is a SHA-256 digest of exact file bytes. A *refusal* is a recorded decision that the supplied evidence does not authorize a requested result, together with a reason name.

The code repository is available to the project; Section 9 states which small
artifacts are included and which raw evidence remains unreleased. Complete
historical replay is **not presently open to independent re-reduction** from
Git alone. A release manifest—the file naming every archived input and its
SHA-256 fingerprint—must supply the missing raw evidence. Synthetic arithmetic
needs only the repository; prospective floor and contrast chains below are
method specifications, not reported results.

### A.1 What a reader needs

Re-derivation requires a full-history checkout at the released revision, Python 3.11 or later, and a copy of the evidence archive. JouleWise's core declares no third-party dependencies in `pyproject.toml`; `env/analysis-lock.txt` records the environment used for retained reductions. Optional plotting and Mac inference dependencies are not part of the numeric replay.

Fresh collection additionally requires the configured Apple-silicon instrument, the exact model files named by the plan, the measurement environment recorded in `env/mac-measurement-lock.txt`, non-interactive permission to run `/usr/bin/powermetrics`, and the measured admission predicates in Section 5 (the pass/fail checks a machine's own calibration must satisfy before its runs are admitted). The retained configuration used the machine named in Section 1. This work does not establish that another Mac, operating-system build, model revision, or quantization shares its measured limits; that machine must characterize its own cells.

### A.2 Scientific artifacts and their bindings

The repository contains programs and plans, but measured run directories are excluded from Git. A complete replay archive would need these connected objects; items 3 and 4
describe the prospective comparison method rather than a result of this paper:

1. A run bundle at `<runs root>/<run id>/`. `config.json` identifies the condition; `events.jsonl` supplies phase boundaries; `raw/powermetrics.plist` is the native power capture; `power_trace.csv` is its parsed trace; and `summary_metrics.json` contains the reduction. `metadata.config_sha256` binds the stored result to the exact configuration bytes. Strict validation independently rebuilds the trace and summary rather than trusting either derived file.
2. The bundle's `instrument_calibration/` subtree. Its `raw/powermetrics.plist` and `events.jsonl` hold the calibration trace and commanded pulse times; `instrument_evidence.json` names the clock-anchor method and published pulse-edge bound. Removing any member breaks the scientific binding. Section A.3 gives the complete estimators that turn those inputs into the bound.
3. The fixed campaign plan, its freeze receipt, calibration-acceptance file, policy, drift-bound artifact, extraction specification, and analysis manifest. The receipt issue time and fingerprints establish which membership, limits, estimator, and contrasts were fixed before the evidence they judge.
4. The append-only whole-window verdict, which binds admitted members, preserved failures and replacements, the calibration bracket, policy, and drift evidence. The floor extraction then binds each reported floor to its admitted cell. The claim verdict binds the contrast estimate, composed uncertainty, cell floor, and two decision gates to those authenticated inputs.

A fingerprint proves equality to disclosed bytes, not who created the original capture. Presence in the archive also does not mean a bundle was analyzed: the whole-window verdict, not directory membership, decides that.

### A.3 Formal calibration algorithms

This appendix specifies the two calculations behind the calibration numbers in Section 2 precisely enough that a reader can rebuild them from this text alone: the **clock-anchor estimator**, which places the instrument's power trace on the controller's wall clock and prices how far that placement can be wrong, and the **pulse-fit (accepted-region) algorithm**, which measures how far the instrument's reported edge timing departs from commanded edges and turns the worst departure into the calibration bound. Everything below is stated as the code executes it. Constants are quoted with their values; a reader who wants the source line for any equation, constant, or rule will find it in `docs/paper/artifact-guide.md` Section 10, the code-location index for this appendix.

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

**Inputs and their admission checks.** All five stamps must be present and
finite, with monotonic-before no greater than monotonic-after, nonnegative
resolutions, and nondecreasing monotonic-before readings in the stated stamp
order. Records must exist, have positive integer elapsed nanoseconds and
integer whole-second timestamp labels, carry `is_delta=true`, finite energy,
and pass the power/energy agreement test in A.3.1. Labels must be nondecreasing;
a jump exceeding the later record's elapsed duration plus 1 s is refused.
At least two label increases are required. The final cumulative elapsed value
must cover at least 60 s, and the controller span from monotonic-before at
`pre_spawn` to monotonic-after at `post_parse` must cover at least that duration.
Failure returns `clock_anchor_unresolved`; the artifact guide Section 9 maps
each failed condition to its diagnostic detail string.

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
7. For a diagnostic that does not enter the bound, bisect the native-label allowance δ over [0, 250 µs] for 24 steps: at each midpoint, move the upper endpoint down to it if the full set is feasible, otherwise move the lower endpoint up to it. Report the final upper endpoint as `min_l_infinity_residual_upper_bound_s`.

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

**Reading the pulses.** Scan `events.jsonl` for `warmup_command_on`,
`warmup_command_off`, `pulse_command_on`, and `pulse_command_off`. An on-event
opens a pending pulse of that kind and the next off-event of the same kind
closes it at a strictly later wall time. Store the two command times and their
stamp half-widths as defined in A.3.1. Unpaired, ambiguous, or missing stamps
are refused; exactly three warm-up and 59 measured pairs are required.

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

    The coarse grid has 301 candidates before clipping and the fine grid 3001. Generate the candidates in increasing order, then remove those outside ±0.75 s; a grid centred away from zero can therefore have fewer candidates.

   The procedure is exactly:

       for s in (s_coarse, s_fine):
           repeat 2 times:
               d_on  ← argmin over d ∈ G(d_on,  s) of Loss(d, d_off)
               d_off ← argmin over d ∈ G(d_off, s) of Loss(d_on, d)

    Eight one-dimensional searches in all — onset and offset at the coarse step, then the same pair at the fine step. Ties resolve to the smallest (most negative) candidate: candidates are visited in increasing order and the first minimum is retained. Write *Loss\** for the loss at the pair (*d_on*, *d_off*) the procedure ends with — the fit's best loss. It is used in steps 7 and 8 and in the loss limit below.

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

The evidence file is marked `valid` only if all of the following hold: every one of the 59 pulses is detected; the spurious-plateau count is 0; every region limit is finite; the pulse count equals the protocol's 59; the raw record stream and `events.jsonl` both carry 64-hex-character SHA-256 digests; a capture wall time is recorded; the projection completed within budget (next section); and all ten binding fields are present and non-empty (`hardware_model`, `os_build`, `powermetrics_sha256`, `sampling_interval_ms`, `anchor_method_version`, `mlx_version`, `pulse_protocol_id`, `power_policy`, `estimator_revision`, `protocol_sha256`), whose hash pins the calibration to one machine, operating system build, instrument binary, and protocol. Otherwise the status is `invalid` and the reasons are listed from a closed vocabulary; a numerical bound may still be printed in an invalid file (for example when the detection succeeded but a binding field is missing), and it then has no standing. The pulse portion of the calibration bound is the largest of 118 observed onset and offset excursions from 59 commanded pulses in one capture; the clock-anchor allowance is then added. Because those pulses share one capture and independence across pulse order and between onset and offset errors has not been shown, this value is an observed sample maximum, not a bound covering 95% of future edge errors with 95% confidence. It is not a deterministic out-of-sample guarantee.

#### A.3.7 The work budget and the 120 s work clock

The branch-and-bound of A.3.5 shares one limit of 165,000 evaluated cells and
one supplementary 120.0-s monotonic-clock deadline across all 59 pulses.
Before each cell's lower-bound evaluation, test the cell count first, then
the deadline, and consume one cell unit. The deadline is checked only before
a cell, so the last evaluation can finish after 120 s. Exhausting either
limit discards every partial fit and yields `detection_nonconvergent`, no
fitted pulse list, and no capture bound; an incomplete region is never a
calibration result. The cell-count stop is reproducible for the stated
traversal; a deadline stop depends on the host. These constants and behavior
are fixed in `joulewise/powermetrics_fiducial.py`.

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

### A.6 Release status

No public archive, release revision or fingerprint-manifest locator has issued.
Section 9 and registry DS-34 give the current availability statement; local
project custody paths are not public release locators. A complete public
historical replay remains unavailable, while Figure A1 can be regenerated
from the repository alone.

### A.7 Synthetic partial-record enclosure

<!-- [FILL:PE-01] SYNTHETIC appendix placement; no measured value is issued. -->
![Figure A1: synthetic records, fixed window, point, timing envelope, and nonnegative enclosure.](figures/figA_partial_record_enclosure.svg)

Figure A1. SYNTHETIC P1; no hardware observation. Panel A's ten numbered
rectangles R1–R10 are adjacent records from 0.5 to 1.5 s: record Ri covers
\([0.5+0.1(i-1),\,0.5+0.1i]\) s and reports an interval average of 10 W,
so each contains \(10\times0.1=1\) J. The horizontal purple segment marks
the fixed window [0.55, 1.45] s; its dashed vertical lines mark the window's
edges. The time axis and ticks are in seconds. The eight blue rectangles
R2–R9 lie wholly inside and contribute 8 J. The two orange rectangles R1
and R10 straddle the edges: each may place anywhere from 0 to its full 1 J
inside the window when power is nonnegative and no within-record shape is
assumed. Adding gives \([8+0+0,\,8+1+1]=[8,10]\) J. Holding each record
at its reported average instead assigns half of each boundary record:
\(8+0.5+0.5=9.0\) J. Independently moving each window edge by up to 10 ms
under that held-average reconstruction gives the shortest window
[0.56, 1.44] s and longest [0.54, 1.46] s, hence the timing envelope
\([10(1.44-0.56),\,10(1.46-0.54)]=[8.8,9.2]\) J. In panel B, the orange
capped segment shows the nonnegative enclosure at the original fixed
window, the blue capped segment shows the timing envelope, and the black
dot shows the 9.0 J point; caps mark endpoints, and the shared energy axis
and ticks are in joules. These are distinct calculations, not confidence
intervals; the enclosure is never composed into any bound.

The adjacent `figA_partial_record_enclosure.json` records every input,
the four timing corners, unrounded computed outputs, and SHA-256 fingerprints
of the generating script and SVG. From the repository root, regenerate both
files with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -c 'from pathlib import Path; from scripts.paper.partial_record_enclosure import write_synthetic_p1_figure; p = Path("docs/paper/figures/figA_partial_record_enclosure"); write_synthetic_p1_figure(p.with_suffix(".svg"), p.with_suffix(".json"))'
```

### A.8 Measurement-window schematic

![Figure A2. One measurement window and the time-balanced A/B/B/A order.](figures/fig2_window_timeline.svg)

*Figure A2. Schematic structure of one measurement window. The upper session-time arrow orders the pre-calibration, admission gate, three opening references, two groups of A/B/B/A science stages around one midpoint reference, three closing references, and post-calibration. The blue spanning bracket joins the two pulse trains; the lower inset's axes, dashed drift line, four A/B/B/A circles, common-time line, and averaging brackets show the equal-midpoint timing symmetry under which linear drift cancels. Unequal runtimes or cooldowns break that balance, and curvature (drift that bends rather than runs straight) still requires the measured whole-window allowance defined above. Stage widths are not to scale, and no measured value is shown.*

## First-use audit ledger

`built-before` means the body constructs the referent from physical inputs before its first named use.
`glossed-at-first-use` means the first named use supplies a plain-word definition or an equivalent calculation in the same sentence or paragraph.
`audience-vocabulary` means a textbook-statistics or plain-English expression the intended metrology/CS professor uses without definition; that class here is exactly: repeatability, repetition, random scatter, complete, completeness, sampler cadence, refused, refuses, missing, malformed, corpus range, degrees of freedom, threshold, exact equality, null hypothesis, tail area, quarantine, append-only, run bundle, full-history checkout, third-party dependencies, cumulative counter, linear programme, infeasible, argmin, and detected.
`forward-pointer-next-paragraph` means the first use carries an explicit cross-reference to a definition in the immediately following paragraph.
`FAILS` means the term is neither built before nor glossed at first use and therefore requires a prose cure or deletion.
The inventory excludes literal field names and reason names inside quoted omission sentences, and all text inside `<!-- -->` build notes.
The reading order tested here is the single methods/diagnostic draft: title,
Abstract, Sections 1 through 11, and appendices. The ledger excludes itself.
A later explanation cannot cure an undefined Abstract term. Removed terms
have no ledger rows; surviving terms are re-homed to their first occurrence.
The frozen round-7 lexicon remains historical context; this ledger owns the
current single-draft reading order.

| Term | First reader-facing home | Status | Definition or disposition |
|---|---|---|---|
| commanded graphics-processor pulses | Abstract | glossed-at-first-use | The Abstract defines work with time-stamped start and stop commands; the Introduction supplies the fixed duration and measurement session. |
| pulse-derived limit | 1. Introduction | glossed-at-first-use | Largest displacement between the commanded times and every edge position allowed by the pulse records, plus the clock-anchor bound. |
| interval-overlap allocation / interval-overlap-assigned phase energy | 1. Introduction | glossed-at-first-use | Split each record's energy in proportion to the interval on each side of the phase boundary; the Abstract and Conclusion states average power times overlap duration. |
| held-average reconstruction | 1. Introduction | glossed-at-first-use | Hold each record at its reported average; the Abstract states the mechanism and the Conclusion glosses the label. |
| timing envelope | 1. Introduction | glossed-at-first-use | Range of assigned energies over the registered timing domain, conditional on the stated reconstruction. |
| synthetic enclosure diagnostic | 1. Introduction | glossed-at-first-use | A labelled 0.9-s, ten-record example comparing the timing envelope with a nonnegative partial-record enclosure; it is never composed into a bound. |
| component | 1. Introduction | glossed-at-first-use | One separate same-model repeat or same-model null A/B/B/A floor calculation. |
| permitted edge movement | 1. Introduction | glossed-at-first-use | Every lower-or-upper edge position allowed by the pulse calibration and clock mapping. |
| independent-edge ratio / four-run comparison | 1. Introduction | glossed-at-first-use | Moved-edge limit divided by the point-only value with separate movement per run; a four-run comparison can be a same-model null or a two-model science contrast. |
| moved-edge limit / independent-edge corner bound / point-only value | 1. Introduction | glossed-at-first-use | The first is \(U_{\mathrm{corner}}\) after every allowed edge choice; the second is its single artifact alias, declared at first use; the point-only value is \(U_{\mathrm{point}}\) at the stored boundary times. |
| decision rule | 1. Introduction | glossed-at-first-use | A direction prints only when the measured difference clears its cell floor and the lowest-to-highest range after known measurement errors stays on the direction fixed before collection. |
| twofold boundary contribution | 1. Introduction | glossed-at-first-use | The moved-edge limit is at least twice the point-only value. |
| prompt processing / prefill | 1. Introduction | glossed-at-first-use | Prompt work through the first output token; the shorthand follows the physical phrase. |
| token generation / decode | 1. Introduction | glossed-at-first-use | Later output-token emission; the shorthand follows the physical phrase. |
| phase boundary | 1. Introduction | glossed-at-first-use | The runtime-recorded time between prompt processing and token generation. |
| powermetrics | 1. Introduction | glossed-at-first-use | The macOS power sampler and its start-to-end interval-average record are stated at first use. |
| Apple M3 Max / 128 GB unified memory | 1. Introduction | glossed-at-first-use | The single measured machine and its memory capacity. |
| sampling record | 1. Introduction | glossed-at-first-use | One sampler output averaging processor power from its recorded start to its recorded end. |
| integrated energy | 1. Introduction | glossed-at-first-use | The time integral of power over a sampling record. |
| detection floor | 1. Introduction | glossed-at-first-use | The advisor's term for the resolution bound before the safeguards; the artifacts call the final gate value after those safeguards the cell floor. |
| power-measurement boundary | 1. Introduction | glossed-at-first-use | Which power is counted: the processor power macOS reports, not power at the wall outlet. |
| \(U_{\mathrm{point}}\) / \(U_{\mathrm{corner}}\) | 1. Introduction | glossed-at-first-use | An independent component bound at recorded edges versus that component after all allowed lower-or-upper choices are evaluated jointly and the largest result is retained; shared movement uses the separately defined \(U_{\mathrm{cmp,shared}}/U_{\mathrm{cmp,point}}\). |
| A/B/B/A block | 1. Introduction | glossed-at-first-use | Four runs in the order A, B, B, A. |
| energy-allowance sign | 1. Introduction | glossed-at-first-use | Says which direction a nonnegative block-level allowance moves assigned energy. |
| twelve required ratios | 1. Introduction | glossed-at-first-use | Eight independent-edge ratios over same-model repeat and null floor components and four comparative \(R_{cm}\) diagnostics over same-model null components. |
| reasoning disabled | 1. Introduction | glossed-at-first-use | Qwen3's optional chain-of-thought output is switched off. |
| bracketed readings | 1. Introduction | glossed-at-first-use | One wall-clock reading placed between the monotonic-clock readings taken immediately before and after it. |
| repeatability / repetition / random scatter | 2. In-window calibration method | audience-vocabulary | Ordinary metrology words for between-repeat spread and repeated observation. |
| systematic reassignment | 2. In-window calibration method | built-before | The joule reassigned between phases under the held-average allocation is built before this label. |
| science window / measurement window | 1. Introduction | glossed-at-first-use | One uninterrupted measurement session; Appendix Figure A2 later diagrams the same window. |
| SHA-256 / SHA-256 fingerprint | 1. Introduction | glossed-at-first-use | A fingerprint that identifies exact file bytes. |
| applied chat-template | 1. Introduction | glossed-at-first-use | The formatter that turns a prompt into model input. |
| greedy generation | 1. Introduction | glossed-at-first-use | Chooses the highest-probability next token at every step. |
| phase reduction | 1. Introduction | glossed-at-first-use | Computes separate phase energies from overlapping sampler records. |
| measurement refusal | 1. Introduction | glossed-at-first-use | A no-result stop when the fixed support requirement fails. |
| declared machine state / instrument-validation manifest / reservation plan / calibration ledger / calibration-acceptance file | Bracketed pulse-train algorithm | glossed-at-first-use | Recorded hardware and operating conditions; the capture's artifact-and-fingerprint list; the reserved-slot file; its pinned session record; and the file containing the fixed bracket rule. |
| mint | Bracketed pulse-train algorithm | glossed-at-first-use | The analysis run that issues the paper's fixed results. |
| frozen | Bracketed pulse-train algorithm | glossed-at-first-use | Fixed and fingerprinted before collection. |
| signal, fit, range, trace-coverage, and completeness checks / shared search-work limits | Bracketed pulse-train algorithm | glossed-at-first-use | Signal rises above rest; the pulse fit beats a no-pulse model; shifts stay in range; the trace covers both margins; required pulses, fingerprints, and binding fields exist; rectangle count and elapsed search time remain within their caps. |
| first-record endpoint | Bracketed pulse-train algorithm | glossed-at-first-use | Wall-clock time assigned to the end of the first native power record. |
| calibration-acceptance rule | Bracketed pulse-train algorithm | glossed-at-first-use | Pre-collection rule deciding whether two capture bounds may bracket one window. |
| entry check | Bracketed pulse-train algorithm | glossed-at-first-use | The pass/fail checks on recorded machine state that a stage must satisfy before its first run is measured. |
| reference runs | Bracketed pulse-train algorithm | glossed-at-first-use | Fixed reference workloads repeated at opening, midpoint when present, and close to track drift. |
| gross energy / idle-subtracted energy | Bracketed pulse-train algorithm | glossed-at-first-use | Recorded processor energy versus that amount after mean idle power times duration is removed. |
| warm-up pulses | Bracketed pulse-train algorithm | glossed-at-first-use | The first use says the three pulses are discarded. |
| base-two varied-gap schedule | Bracketed pulse-train algorithm | glossed-at-first-use | Its gaps step through powers of two to keep pulse edges from repeatedly aligning with samples. |
| sampler cadence | Bracketed pulse-train algorithm | audience-vocabulary | Requested 100-ms sampling cadence is textbook/plain-English measurement vocabulary. |
| quiet trace | Bracketed pulse-train algorithm | glossed-at-first-use | The parenthesis defines quiet as no commanded pulse. |
| resting GPU power / pulse height / plateau / pulse plateau | Bracketed pulse-train algorithm | glossed-at-first-use | Resting level, pulse height, and the flat high-power portion are built in physical words. |
| trace-coverage | Bracketed pulse-train algorithm | glossed-at-first-use | The captured trace extends through the fixed margin on both sides of every pulse. |
| accepted capture bound / capture bound | Bracketed pulse-train algorithm | built-before | The pulse search, surviving rectangles, stamp widening, and refusal checks precede the largest-displacement label. |
| clock-anchor bound | 1. Introduction | glossed-at-first-use | The appositive gives the uncertainty in placing the power record on wall-clock time; Section 2 and Appendix A.3.3 construct it. |
| complete / completeness | Bracketed pulse-train algorithm | audience-vocabulary | Plain-English criteria words; the surrounding lists state what must be present. |
| refused / refuses | Bracketed pulse-train algorithm | audience-vocabulary | Plain-English rejection verbs used consistently for a calculation that cannot authorize evidence. |
| wall clock / monotonic clock | 1. Introduction | glossed-at-first-use | The wall clock keeps civil time; the monotonic clock is a counter that advances but is never corrected to civil time, and their rates need not match. |
| straight-line clock mappings / rate-aware model | Bracketed pulse-train algorithm | glossed-at-first-use | The retained linear rate-and-offset mappings and the unequal fixed-rate correction are stated in the same paragraph. |
| missing / malformed | Bracketed pulse-train algorithm | audience-vocabulary | Plain-English absent or structurally invalid inputs. |
| unbounded | Bracketed pulse-train algorithm | glossed-at-first-use | The allowed rate reaches the edge of its search box. |
| Student-\(t\) | Bracketed pulse-train algorithm | glossed-at-first-use | A small-sample bell curve, wider because spread is estimated from 17 captures. |
| 99% quantile / \(t_{0.995,16}\) | Bracketed pulse-train algorithm | glossed-at-first-use | Two-sided 99% is tied to the 0.995 one-sided point with 16 degrees of freedom. |
| degrees of freedom | Bracketed pulse-train algorithm | audience-vocabulary | Textbook statistics vocabulary; 17 captures leave 16 degrees of freedom. |
| sample standard deviation / prediction amount | Bracketed pulse-train algorithm | glossed-at-first-use | The pointer clause identifies the \(n-1\) formula of Section 4; the same paragraph supplies the value and prediction construction. |
| two-draw rule | Bracketed pulse-train algorithm | glossed-at-first-use | Two fresh bounds make the difference spread \(\sqrt{2}\) times one capture's spread. |
| corpus range | Bracketed pulse-train algorithm | audience-vocabulary | Textbook largest-minus-smallest range of the retained corpus. |
| ROUND_HALF_EVEN / nearest microsecond | Bracketed pulse-train algorithm | glossed-at-first-use | Nearest-microsecond rounding with an exact tie going to the even digit. |
| minimum allowance / operative timing bound / \(B_{\mathrm{fiducial}}\) / \(b\) | Bracketed pulse-train algorithm | glossed-at-first-use | The corpus lower allowance, one-capture pulse-derived limit, and distinct window bound are separated and numerically worked. |
| stage / block member | Bracketed pulse-train algorithm | glossed-at-first-use | A back-to-back declared run group and one of its four individual A/B/B/A runs. |
| members | Bracketed pulse-train algorithm | glossed-at-first-use | The four individual runs in an A/B/B/A science block. |
| A/B/B/A order / block difference | Bracketed pulse-train algorithm | glossed-at-first-use | The four-member order and \((B_1+B_2-A_1-A_2)/2\) contrast are printed together. |
| curvature | Bracketed pulse-train algorithm | glossed-at-first-use | Drift that bends rather than runs straight. |
| whole-window allowance / energy family | Bracketed pulse-train algorithm | glossed-at-first-use | A once-added joule allowance for a group reduced under one energy definition. |
| reference-trajectory excursion / issued repeatability bound | Bracketed pulse-train algorithm | glossed-at-first-use | Largest-minus-smallest reference means versus a retained earlier-window repeatability bound. |
| onset lag / offset lag / pulse residual | One diagnostic reconstruction | glossed-at-first-use | Observed edge minus its matching commanded edge; the residual is the largest endpoint magnitude before the anchor term. |
| record clipping / clip a record | 4. How the method quantifies assigned-energy sensitivity | glossed-at-first-use | Keep only record time inside the phase and multiply duration by average power; the joule example is worked. |
| configuration cell / cell | 1. Introduction | glossed-at-first-use | A configuration cell groups runs sharing work, model, machine, software, and power definition; the shorter name follows in the defining sentence. |
| false-difference components / false-difference | 1. Introduction | glossed-at-first-use | The same-model null A/B/B/A block produces this diagnostic, distinct from the two-model science contrast. |
| admitted | Bracketed pulse-train algorithm | glossed-at-first-use | A stage that passes the entry check is allowed to begin its measured runs. |
| leaking dependence across the phase boundary | 3. Instrument characterization | glossed-at-first-use | Prompt-processing energy changes with work performed only after prompt processing ended. |
| floor packs / contrast pack | 3. Instrument characterization | glossed-at-first-use | The first use defines floor packs as campaign plans that collect calibration data used to build a comparator floor; the contrast pack is the separate two-model science comparison. |
| Workload response | 3. Instrument characterization | glossed-at-first-use | Whether request and token-generation energy increase with realized output length in the registered way. |
| Identical-condition null | 3. Instrument characterization | glossed-at-first-use | Whether an A/B/B/A comparison manufactures a difference when both conditions are the same. |
| independent unit | 3. Instrument characterization | glossed-at-first-use | One separately admitted bundle, not one sampler record within it. |
| workload-response slope | 3. Instrument characterization | glossed-at-first-use | Fitted change in energy per output token. |
| workload level | 3. Instrument characterization | glossed-at-first-use | One output-token count fixed before collection. |
| workload magnitude | 3. Instrument characterization | glossed-at-first-use | One target size fixed in the identical-condition ladder. |
| per-token conversion | 3. Instrument characterization | glossed-at-first-use | Fitted joules per output token. |
| fitted residual | 3. Instrument characterization | glossed-at-first-use | One observed energy minus the straight-line value predicted for its output length. |
| null-test blocks | 3. Instrument characterization | glossed-at-first-use | Identical-condition blocks whose allowed difference should contain zero. |
| interval of allowed differences | 3. Instrument characterization | glossed-at-first-use | Minimum and maximum A/B/B/A difference over the fixed member-energy endpoint combinations. |
| mean interval | 3. Instrument characterization | glossed-at-first-use | Mean of the five block lower endpoints through mean of their five upper endpoints. |
| resolution band | 3. Instrument characterization | glossed-at-first-use | Symmetric allowed slope range made from one admitted prefill half-width across the output span. |
| floor band | 3. Instrument characterization | glossed-at-first-use | Analogous symmetric slope range made from an independently issued prefill floor. |
| unphased gap | 3. Instrument characterization | glossed-at-first-use | Recorded interval between the end of prefill and the start of decode. |
| shared session timing term | 3. Instrument characterization | glossed-at-first-use | One bracket-capture timing bound common to all session members. |
| member-local timing | 3. Instrument characterization | glossed-at-first-use | Each run's own local and edge-span timing contribution. |
| timing flags | 3. Instrument characterization | glossed-at-first-use | Mark a member whose clock bound exceeds a quarter of its window. |
| sampling flags / cadence ratio | 3. Instrument characterization | glossed-at-first-use | Mark too few in-window records, an unrecorded cadence ratio, or cadence below the fixed phase-rate multiple. |
| package power | 3. Instrument characterization | glossed-at-first-use | Summed CPU, GPU, and neural-engine power. |
| reference roles | 3. Instrument characterization | glossed-at-first-use | Separate opening, midpoint, and closing allowance builders from held-out probes. |
| passing cooldown exit | 3. Instrument characterization | glossed-at-first-use | First post-hold gate evaluation meeting the frozen rolling-power, coverage, and thermal checks. |
| absolute component / comparative component | Comparing the moved-edge limit and point-only value | glossed-at-first-use | Same-model repeat spread versus A/B/B/A block-difference spread. |
| admitted energy | Comparing the moved-edge limit and point-only value | glossed-at-first-use | Energy from a run that passed Section 5 entry checks and may bear a claim. |
| independent units | 3. Instrument characterization | glossed-at-first-use | Singular first use defines one separately admitted bundle; later the component-specific units are stated. |
| point-only unguarded value / unguarded | Comparing the moved-edge limit and point-only value | glossed-at-first-use | The first calculation uses admitted energies at their recorded values before the later small-sample multiplier and whole-window allowance. |
| independent-edge ratio \(R\) / dominates | Comparing the moved-edge limit and point-only value | glossed-at-first-use | Moved-edge limit divided by the matching point-only value; dominates means \(R\ge2\). |
| threshold / exact equality | 3. Instrument characterization | glossed-at-first-use | A threshold is the numerical cutoff that the positive slope must exceed. |
| authentication / evaluation | 1. Introduction | glossed-at-first-use | Authentication matches inputs to named source-file contents; evaluation requires a nonzero second value. |
| registered rounding / registered | Abstract | glossed-at-first-use | Each Abstract branch defines the registered timing domain as the set of edge movements fixed before collection; the later registered-rounding use names a rule fixed in fingerprinted plan bytes. |
| reintegrate | Comparing the moved-edge limit and point-only value | glossed-at-first-use | Reintegrate the four retained power traces after moving all four phase starts while holding their ends fixed. |
| onset set / offset set / zero-shift value | Comparing the moved-edge limit and point-only value | glossed-at-first-use | Reintegrated common-start values, analogous common-end values, and their included zero-shift value. |
| shared lower and upper excursions | Comparing the moved-edge limit and point-only value | glossed-at-first-use | The displayed equations define the lower and upper common start-plus-end movements. |
| binary64 / member-envelope integral sum | Comparing the moved-edge limit and point-only value | glossed-at-first-use | The usual 64-bit float format and a nonnegative four-member joule scale that covers the integrals before contrast. |
| ulp | Comparing the moved-edge limit and point-only value | glossed-at-first-use | The gap between 1 and the next larger representable number. |
| local sign | 1. Introduction | glossed-at-first-use | The comparative replay chooses one separately for each block. |
| local half-width / shared sign | 1. Introduction | glossed-at-first-use | One sign for energy allowances across all blocks; Section 4 constructs the local half-width from four member residuals. |
| half-width | 3. Instrument characterization | glossed-at-first-use | A timing half-width is half an allowed timing range. |
| \(R_{cm}\) | 1. Introduction | glossed-at-first-use | Shared-energy-sign/local-corner sensitivity diagnostic with one shared sign for block-level energy allowances and one local sign per block; it is not a physical common-time replay. |
| shared-energy-sign/local-corner sensitivity diagnostic / shared-energy-sign/local-corner ratio | 1. Introduction | glossed-at-first-use | Registered comparative diagnostic that retains scalar energy-allowance signs without claiming common-time conservatism. |
| two-block fixture / Student-\(t\) critical | Comparing the moved-edge limit and point-only value | glossed-at-first-use | A retained arithmetic-only example and its fixed-table critical value. |
| resolution bound | 1. Introduction | glossed-at-first-use | Registered operational resolution guard for assigned-energy differences in one cell. |
| cell floor | 1. Introduction | glossed-at-first-use | Artifact name for the final resolution bound, bridged in Section 1 to the detection-floor name. |
| same-cell floor | Adding publication safeguards after the ratio | glossed-at-first-use | That floor for exactly the phase, workload, model, hardware, software, and power-measurement boundary being tested. |
| small-sample multiplier / \(g(n)\) | Comparing the moved-edge limit and point-only value | glossed-at-first-use | A factor that widens a result to allow for limited repetition; its formula follows under publication safeguards. |
| directional comparison / directional comparisons | Adding publication safeguards after the ratio | glossed-at-first-use | The expected direction is fixed before collection. |
| Holm step-down correction / raw probability | Adding publication safeguards after the ratio | glossed-at-first-use | Applied at nominal family-wise level 0.05 to two model-based tests, conditional on distributional and dependence assumptions; the later worked ordering supplies mechanics. |
| repeat standard error | Adding publication safeguards after the ratio | glossed-at-first-use | Repeat-to-repeat scatter divided by \(\sqrt n\). |
| total standard error | Further limitations | glossed-at-first-use | For the gross phase-energy path, this is the standard error of the block differences because the builder supplies no additional stochastic metrology variance. |
| null hypothesis / tail area | Adding publication safeguards after the ratio | audience-vocabulary | Textbook statistics vocabulary for zero mean difference and the resulting two-sided probability. |
| effective sample size / n_{\mathrm{eff}} | Adding publication safeguards after the ratio | glossed-at-first-use | Number of independent blocks giving the same repeat scatter. |
| AR(1) model | Adding publication safeguards after the ratio | glossed-at-first-use | Adjacent block errors are treated as serially correlated. |
| serially correlated | Adding publication safeguards after the ratio | glossed-at-first-use | Adjacent block errors are treated as serially correlated. |
| decision-interval sign check / direction gate | Adding publication safeguards after the ratio | forward-pointer-next-paragraph | The first use explicitly says the direction gate is in the next paragraph, which defines both intervals and the fixed direction. |
| magnitude check / direction check | Adding publication safeguards after the ratio | glossed-at-first-use | Absolute estimate must clear the cell floor; both complete intervals must remain on the fixed direction. |
| not resolvable | Adding publication safeguards after the ratio | glossed-at-first-use | The estimate does not clear the cell floor; it is not zero. |
| measurement interval / decision interval / deterministic bound | Adding publication safeguards after the ratio | glossed-at-first-use | Repeat-standard-error interval for this gross phase-energy path; that interval extended by authenticated non-random maximum displacements. |
| deterministic-bound kinds / interpolation edge | Adding publication safeguards after the ratio | glossed-at-first-use | Native interval-average records integrate constant reported power and have zero interpolation-bound term; the named interpolation edge belongs to the point-sample fallback, while timing uses separate boundary envelopes. |
| close-out artifact | Comparing the moved-edge limit and point-only value | glossed-at-first-use | Post-campaign artifact that checks every required ratio. |
| signed clearance or shortfall | Adding publication safeguards after the ratio | glossed-at-first-use | Absolute point estimate minus cell floor, with positive clearance and nonpositive shortfall. |
| request total | Abstract | glossed-at-first-use | Energy assigned over the whole request; moving the dividing time reallocates energy between its parts without changing that total. |
| MLX | 1. Introduction | glossed-at-first-use | Apple's on-device inference framework. |
| inserted-gap check | 1. Introduction | glossed-at-first-use | An approximately 500-ms no-work gap between the request parts whose time-stamped edges are compared with the power record. |
| Figure 3 | Evidence refusal and claim gates | glossed-at-first-use | The prose and caption enumerate the refusal lane, measured-contrast input, magnitude and direction gates, yes/no arrows, and four outcomes. |
| fail-closed | 5. Collection stops when required evidence fails | built-before | Missing, malformed, out-of-limit, or inconsistent evidence stops collection and records why. |
| measured admission rules / admit a stage | Measured admission rules | glossed-at-first-use | Recorded fields and limits evaluated immediately before the stage's first measured member. |
| idle baseline / nearest-rank p95 | Measured admission rules | glossed-at-first-use | Thirty-second no-run sample; sort \(n\) values and select item \(\lceil0.95n\rceil\). |
| cooldown rule | Measured admission rules | glossed-at-first-use | Inter-member recovery must pass before 300 s; an override makes the member diagnostic only and prevents claim bearing. |
| window closes | Measured admission rules | glossed-at-first-use | The third same-cause stage failure closes the full window, not merely the stage. |
| measured contrast | Evidence refusal and claim gates | glossed-at-first-use | The figure's input box carries a point estimate and composed uncertainty interval. |
| first-order balance | Counterbalanced order | glossed-at-first-use | Equal sums of A and B run midpoints. |
| quarantine / append-only | Every input and every refusal remains visible | audience-vocabulary | Plain-English custody words for retained failed slots and non-overwriting replacement records. |
| tamper-evident / tamper-proof / trusted operator | Every input and every refusal remains visible | glossed-at-first-use | Mistake detection and post-hoc-choice defense, not protection against another actor. |
| third-party provenance / provenance | Every input and every refusal remains visible | glossed-at-first-use | Evidence that would convince someone who does not trust the operator. |
| freeze receipt / freeze receipts | Every input and every refusal remains visible | glossed-at-first-use | Records fixing plan bytes and the time those bytes were frozen. |
| record support / positive overlap / overlap count | Printed negative result: short prompt processing has too few overlapping records | glossed-at-first-use | Positive overlap is defined by the positive-time inequality; overlap count and record support both name the number of sampling records that pass it. |
| interquartile range / IQR | Printed negative result: short prompt processing has too few overlapping records | glossed-at-first-use | Upper edge minus lower edge of the middle half of sorted values. |
| resolvability / not_resolvable_sample_count | Printed negative result: short prompt processing has too few overlapping records | glossed-at-first-use | Here the not-resolvable verdict names record support below the three-record minimum and the printed label identifies that reason; Section 4 uses the same verdict words for failure to clear a cell floor. |
| record width | Printed negative result: short prompt processing has too few overlapping records | glossed-at-first-use | Record width is the duration of one sampling record's interval. |
| prospective demonstration | 1. Introduction | glossed-at-first-use | Comparison fixed before collection; outside this submission's empirical scope. |
| diagnostic-era | Historical current-method edge result | glossed-at-first-use | Collected in the historical July 2026 period. |
| three-record minimum | Abstract | glossed-at-first-use | A phase must overlap at least three sampler records to be reduced at all. |
| reducer | Adding publication safeguards after the ratio | glossed-at-first-use | Program that integrates native interval-average records over their overlap durations and later turns retained bundles into assigned phase energies. |
| variance multiplier | Further limitations | glossed-at-first-use | The displayed definition says how much the selected dependence model multiplies repeat variance. |
| within-arm variation | Further limitations | glossed-at-first-use | Variation among runs of the same A or B condition. |
| fitted edge time / command time | One diagnostic reconstruction | glossed-at-first-use | A fitted edge time is compared with its matching command timestamp; their signed difference is the best-fit lag. |
| external-meter study | Future work | glossed-at-first-use | A proposed, unrun whole-request comparison against a meter on the wall side of the power supply. |
| Running Average Power Limit / RAPL | From counter gain to counter time | glossed-at-first-use | Processor-exposed energy counter; full phrase precedes the abbreviation. |
| NVIDIA Management Library / NVML | From counter gain to counter time | glossed-at-first-use | Software power counter; full phrase precedes the abbreviation. |
| large-language model / LLM | Large-language-model energy measurement | glossed-at-first-use | A model predicting successive text units (tokens); the abbreviation follows the full name. |
| minimum-detectable-effect / pre-registration | Benchmark and metrology lineage | glossed-at-first-use | Paired variation estimates a prospectively detectable effect; the threshold is fixed before results. |
| disaggregated inference / disaggregation | Benchmark and metrology lineage | glossed-at-first-use | Split inference across endpoints is named as a future application requiring two boundaries and clock alignment. |
| re-derivation / fresh collection | Historical current-method edge result | glossed-at-first-use | Recompute from preserved bytes versus create new evidence under the named machine conditions. |
| not presently open to independent re-reduction | Appendix A. Reproducing this work | built-before | Git lacks the complete historical primary-byte archive; synthetic arithmetic is reproducible from the repository. |
| release manifest | Appendix A. Reproducing this work | glossed-at-first-use | The file that names every archived input and its SHA-256 fingerprint. |
| full-history checkout / third-party dependencies | A.1 What a reader needs | audience-vocabulary | Plain software-reproduction vocabulary for repository history and externally supplied packages. |
| admission predicates | A.1 What a reader needs | glossed-at-first-use | The pass/fail checks a machine's own calibration must satisfy before its runs are admitted. |
| run bundle | Adding publication safeguards after the ratio | audience-vocabulary | Plain-English software packaging vocabulary; Appendix A.2 later enumerates its files. |
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
| Commanded pulses | Bracketed pulse-train algorithm | glossed-at-first-use | The first use states their count, duration, matrix workload, and warm-up exclusion. |
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
| bisect | A.3 Formal calibration algorithms | glossed-at-first-use | Split an interval at its midpoint; the later rectangular pulse search splits its wider side. |
| depth-first | A.3 Formal calibration algorithms | glossed-at-first-use | The upper half is processed next. |
| Projection | A.3 Formal calibration algorithms | glossed-at-first-use | The region's enclosure is the bounding box of the retained cells. |
| Widening by stamp uncertainty | A.3 Formal calibration algorithms | glossed-at-first-use | Subtract or add each command stamp's half-width from its projected edge limits. |
| detected | One diagnostic reconstruction | audience-vocabulary | Plain-English observation that all 59 pulses passed detection. |
| worst excursion | A.3 Formal calibration algorithms | glossed-at-first-use | An edge's largest widened-region endpoint magnitude. |
| observed sample maximum | A.3 Formal calibration algorithms | glossed-at-first-use | Largest of 118 observed edge excursions, without a population-coverage guarantee. |
| percentile | A.3 Formal calibration algorithms | glossed-at-first-use | The \(\lceil0.95\cdot118\rceil=113\)th smallest value. |
| Origin of the 120 s work clock | A.3 Formal calibration algorithms | glossed-at-first-use | The budget clock starts after baseline computation and before the first pulse fit. |
| custody | Evidence refusal and claim gates | glossed-at-first-use | Each named input's fingerprint still matches its recorded bytes. |
| matching refusal / reproduced result | A.5 Interpreting a refusal | glossed-at-first-use | Identical bytes and plan should reproduce the same reason name; that refusal is a result. |
| GPU / fitted onsets and offsets | Abstract | glossed-at-first-use | A graphics processor; switch-on and switch-off times selected by matching predicted interval-average power to the recorded trace. |
| best-fit lag | One diagnostic reconstruction | glossed-at-first-use | Fitted edge time minus its matching command time; positive means later, negative earlier. |
| allowed region | Historical current-method edge result | glossed-at-first-use | Every edge pair surviving the fit's discrepancy limit; its endpoints differ from a best-fit lag. |
| medians | Historical current-method edge result | glossed-at-first-use | Middle sorted values; for the 59-value series each is its 30th sorted lag. |
| source map | Historical current-method edge result | glossed-at-first-use | Registry rows associate each printed diagnostic value or mark with its exact artifact and field. |
| typed custody-read interface / supply map | 9. Evidence and code availability | glossed-at-first-use | A role name and runs root resolve through a clean-Git table to fixed paths and expected digests before disk replay. |

The audit also searched the reader-facing draft for empirical outcome branches,
prospective result-fill markers, the false between-record pause mechanism,
and the retired any-exceedance falsifier. Historical calibration and record
support retain their explicit era labels; fixtures retain their arithmetic-only
labels. Any uncured first use is a failure. Terms inventoried: 260; FAILS: 0.
