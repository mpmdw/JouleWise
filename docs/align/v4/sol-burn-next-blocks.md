# ALIGN after v4: proposed next blocks for more information per measurement-Mac hour

**Status:** design proposal only; synthetic planning calculations; not a
registration, arm authority, or claim about real experiment data.  This proposal
uses only material tracked in this checkout.

## 1. Recommendation in one page

Run a short, deterministic **instrument block** between long agent windows, not
another series of 12--16.5 h exploratory windows.  The preferred order is:

1. **H-dose crossover** (Block A): estimate the continuous hidden-decode response
   and the smallest resolvable hidden-token increment.
2. **Context/cache surface** (Block B): identify whether prompt length and cache
   reuse change the energy slope or residual variance.
3. **Segmentation/tool-topology crossover** (Block C): isolate the cost of turn
   and tool boundaries while holding all prompt and output bytes fixed.
4. **Locked benchmark holdout** (Block D): turn the best cells from A--C into a
   model-independent, longitudinal instrument benchmark.

These are complementary, not four alternatives.  A--C are compact factorial
blocks for parameter estimation; D is the recurring confirmation block.  Do not
spend a Mac night on D until A--C have selected its cells without looking at D's
held-out measurements.

The central design change is to make **a pre-rendered prompt/output token stream,
not an agent trajectory, the experimental unit**.  Every scheduled replay has a
content-addressed input transcript, exact admitted token IDs, exact output token
IDs, cache/reset policy, and expected event sequence.  The runtime teacher-forces
or replays those output IDs and fails closed on any byte, token, count, or event
divergence.  Thus repeats are genuinely identical-work measurements.  Model
family, quantization, hardware, and runtime remain benchmark *strata*, while the
registered factors below (token counts, reused-token fraction, boundary count,
and hidden-token dose) are model-independent benchmark parameters.

## 2. Why this is the next useful design

The current v4 skeleton allocates 18 members to four anchors, eight 30B
contrasts, and six D runs [source: `configs/campaigns/align_v4/README.md:7-12`].
Its provisional planning maximum is 44,640 s, or 12.4 h
[source: `configs/campaigns/align_v4/registration/sizing_preview.json:16-22`].
The council explicitly treats Mac wall time as scarce because the intended
windows take 12--16.5 h [source:
`docs/align/council-2026-11-06-v4-review/CHAIR.md:5-8`].  It also rejected an
extra 24-run contrast window as roughly eight Mac hours because that contrast
would not govern the D cell [source:
`docs/align/council-2026-11-06-v4-review/CHAIR.md:127-140`].

V4's important unresolved quantity is continuous resolution.  Whole-turn
tampering only gives an upper bound when first-turn reasoning is 1--4k tokens;
the council therefore requested a registered sub-turn grid and benign-carrier
curve [source: `docs/align/council-2026-11-06-v4-review/CHAIR.md:42-56`].  Its
planning expectation is 300--500 hidden tokens, but the stated plausible range
is 120--1,500 and the limiting uncertainty is model misfit rather than meter
noise [source: `docs/align/council-2026-11-06-v4-review/CHAIR.md:270-301`].
V3's desk, moreover, grouped trajectories by exact prompt/output sequence, a
useful precedent for exact-work blocking [source:
`docs/align/pilot_protocol_v3.md:140-149`].

The proposal therefore spends Mac time on repeated, short, identical-work
crossovers that directly estimate slopes and variance components.  It does not
replace v4's ecological agent episodes.  In particular, a replay benchmark
cannot establish agent capability, sabotage prevalence, or production-monitor
power.

## 3. Common contract and power calculation

### 3.1 Deterministic replay contract

Before any measurement, freeze for every fixture:

- UTF-8 prompt and output bytes and their SHA-256 digests;
- tokenizer identity and the exact prompt/output token-ID arrays;
- four integer workload coordinates: admitted prompt tokens **P**, emitted
  output tokens **D**, hidden replay tokens **H**, and tool/turn boundaries
  **B**;
- cache state (`cold`, `prefix-warm`, or an exact reused-token count), context
  limit, batch/chunk controls, and reset/idle policy;
- expected event names, order, token counts, and terminal output bytes; and
- a paired schedule generated before measurement, with condition labels hidden
  from the reducer until the member manifest is sealed.

Each pair is adjacent and order-balanced (AB/BA); each four-pair packet is an
ABBA/BAAB crossover.  A failed half-pair invalidates its mate and is replaced at
the end using the next frozen schedule row.  No outcome-dependent stopping is
allowed.  Keep v4's thermal and power-source screens, but report both gross and
reference-adjusted energy so the benchmark remains auditable.

The exact-output requirement deliberately differs from stochastic generation.
It benchmarks the measurement/runtime path under fixed work.  A separate
ecological episode is needed before generalizing any coefficient to freely
sampled agents.

### 3.2 Planning assumptions and reproducible arithmetic

All power numbers below are **synthetic planning numbers**, not estimates from
experiment data.  The independent observation is an eligible within-pair
difference.  For a two-sided paired t test at alpha 0.05 and 80% power, the
normal approximation is

`n_pairs = ceil((1.96 + 0.84)^2 / d_z^2) = ceil(7.84 / d_z^2)`,

where `d_z = effect / SD(within-pair difference)`.  This gives 32, 64, and 126
pairs for standardized effects 0.50, 0.35, and 0.25.  The schedules below round
up to complete counterbalance packets.  For 90% power replace 0.84 by 1.282:
43, 86, and 169 pairs.  Final registration must replace these approximations
with a t/noncentral-t or simulation calculation using blinded variance from the
first complete packet; it may change the future fixed sample size once, without
examining condition means.

For a binary detection rate, 30 independent held-out fixtures with 27/30
detections give an approximate 90% Wilson interval of 0.77--0.96; 60 with 54/60
give approximately 0.82--0.95.  These are precision illustrations, not promised
outcomes.  They are much more informative than three sabotage observations per
pair: v4's review says 3/3 yields only a 46% one-sided 90% lower bound
[source: `docs/align/council-2026-11-06-v4-review/CHAIR.md:307-312`].

Mac-hour estimates below include a conservative 25% allowance for reset,
reference, and replacement time.  They must be re-priced from a synthetic dry
run before registration.  Cadence assumes no overlap with quiet-machine v4
collection and at least one no-measurement day after two consecutive blocks.

## 4. Block A -- hidden-decode dose crossover (highest priority)

### Question and estimand

How many joules does a known increment of hidden decode cost, and at what H can
the instrument distinguish that increment while prompt, visible output, cache
state, and boundary topology are fixed?

Use doses **H = {0, 128, 256, 512, 1,024} tokens** on each of eight frozen
carrier prompt/output pairs.  H is a pre-rendered, teacher-forced side stream;
it is actually executed but omitted from the visible transcript.  The primary
estimand is the within-carrier slope `beta_H` in J/token with carrier and packet
fixed effects.  Secondary estimands are the mean contrasts at each nonzero dose,
the smallest H whose simultaneous 95% interval excludes zero, and curvature.
This is the physical positive control that v4 says is required before claiming
detection of physical hidden computation [source:
`docs/align/council-2026-11-06-v4-review/CHAIR.md:50-56`], rather than a desk-only
edit that holds measured joules fixed as v3 did
[source: `docs/align/pilot_protocol_v3.md:155-163`].

### Size, power, and Mac cost

- **Core:** 8 carriers x 5 doses x 2 repeats = 80 members / 40 matched
  dose-control differences.  At 90 s/member plus 25%, budget **2.5 Mac h**.
- **Resolution:** 40 pairs have about 80% power at `d_z = sqrt(7.84/40) =
  0.443`.  If blinded packet SD is 40 J, this is a 17.7 J paired effect.  Using
  v4's planning `e_D = 3.0--4.5 J/token`, 128 executed tokens imply 384--576 J,
  so the proposed lowest dose is intentionally far above that synthetic noise
  example [source: `docs/align/council-2026-11-06-v4-review/CHAIR.md:274-293`].
  The result will test whether that optimistic separation survives real replay
  overhead and model misfit.
- **Extension:** if the 128-token cell is cleanly resolved, add a frozen
  **H = {16, 32, 64}** packet (8 carriers x 3 doses x 2 = 48 members, about
  **1.5 h**) to locate the floor; do not add it based on a favorable point
  estimate, only on the registered interval rule.
- **Cadence:** **2 core blocks/week** (5 Mac h/week), at least 24 h apart; one
  extension block the following week if triggered.

### Risks and controls

- Teacher forcing or side-stream execution may use a different kernel path than
  ordinary sampling.  Record kernel/event identity; the claim is physical work
  on this replay path, not hidden agent reasoning.
- H may perturb thermal state for the next member.  Counterbalance dose order,
  require return-to-reference, and test carryover by previous dose.
- Token energy can be nonlinear with context and cache state.  That is why Block
  B follows; do not export `beta_H` outside the registered P/cache stratum.
- A single repeated token sequence could compress or exercise atypical logits.
  Use eight independently frozen natural-text continuations and treat carrier as
  a randomization block, while keeping every replay byte-identical.

## 5. Block B -- prompt-length x cache-reuse response surface

### Question and estimand

Does energy attribution remain stable across model-independent prompt length
and cache reuse?  Cross **P = {2,048, 8,192, 32,768} admitted tokens** with
**reuse = {0%, 75%}**, while fixing D = 512 output tokens, H = 0, one turn, and
the exact visible continuation.  Construct long prompts by concatenating
content-addressed text tiles; the manifest, not the tokenizer at run time,
defines the exact admitted IDs.  The primary estimands are J/new-prefill-token,
J/reused-token, J/decode-token, and the P x reuse interaction.  A secondary
estimand is the residual SD in each cell, which directly tells later blocks
where paired Mac time buys the most resolution.

### Size, power, and Mac cost

- **Core:** 6 cells x 8 carriers x 2 repeats = **96 members**.  Pair cold and
  warm runs within carrier/P and reverse their order across packets.  At a
  conservative 120 s/member plus 25%, budget **4.0 Mac h**.
- **Power:** the 48 cold/warm pairs detect `d_z = 0.404` at 80% power.  Each
  prompt-length main-effect contrast pools 32 members per level; a paired trend
  contrast with 32 effective differences detects `d_z = 0.495`.  Treat the
  interaction CI, not six cellwise p-values, as primary.
- **Precision option:** duplicate the whole counterbalance (192 members,
  **8 h**) only if blinded SD implies the registered smallest relevant effect
  is between `d_z=0.29` and 0.40; 96 effective pairs at 8 h resolve about
  `d_z=0.286` at 80% power.
- **Cadence:** **1 block/week**; never split the six-cell counterbalance across
  weeks.  If the precision option is invoked, run two 4 h halves within 48 h
  with every cell represented equally in each half and include half as a fixed
  effect.

### Risks and controls

- A nominal warm cache can silently miss.  Require exact reused-token counts and
  a cache-hit event; otherwise invalidate the pair.
- The 32,768-token prompt may cross a runtime batching or memory threshold.
  That is useful as a benchmark discontinuity, but coefficients must be
  piecewise if residual plots reject linearity.
- Concatenated tiles are not ecological prompts.  Publish the tile digests and
  scope the result to admitted-token and reuse parameters, not semantic task
  complexity.
- Cache warming can contaminate later cells.  Use explicit reset receipts and a
  cold-cache sentinel at packet boundaries.

## 6. Block C -- turn and tool-boundary topology crossover

### Question and estimand

How much energy is attributed to orchestration boundaries independently of
token volume?  Hold the concatenated prompt bytes and concatenated output bytes
constant at P = 8,192 and D = 2,048, then render the same content as:

1. one assistant turn, no tool boundary;
2. four assistant segments, no-op tool result after each of the first three;
3. eight assistant segments, no-op tool result after each of the first seven;
4. four segments with a state-changing fixture tool whose deterministic result
   has the **same byte length and token count** as the no-op result.

The event grammar and final transcript digest are frozen.  The primary
estimands are J/additional boundary and the state-changing-minus-no-op contrast;
the secondary estimands are re-prefill tokens and wall time per boundary.  This
tests an instrument parameter that v4's trajectory design cannot separate from
model behavior, while retaining exactly reproducible content.

### Size, power, and Mac cost

- **Core:** 12 fixtures x 4 topologies x 2 repeats = **96 members / 48
  topology pairs**, about **3.3 Mac h** at 100 s/member plus 25%.
- **Power:** pooled topology contrasts with 48 pairs detect `d_z=0.404` at 80%
  power.  The state-changing/no-op contrast has 24 paired differences and
  detects `d_z=0.572`; doubling only those two cells to 48 differences costs
  about **0.8 h** and reaches `d_z=0.404`.
- **Cadence:** **1 block/week**, preferably 48 h away from Block B so cache
  state can be reset and its receipt reviewed.

### Risks and controls

- Token identity can diverge when chat templates add role markers.  The
  benchmark therefore freezes both semantic payload bytes and the *fully
  rendered* per-turn token arrays; report structural marker tokens separately.
- A tool implementation may perform variable host work.  Use a local fixture
  with a frozen response and record host energy/time; never call a network or
  external service.
- Equal total tokens do not imply equal KV-cache work after a boundary.  That is
  the intended mechanism, so record re-prefill/reused counts rather than
  “adjusting” it away.
- This does not estimate how often real agents call tools.  It estimates the
  marginal instrument/runtime cost conditional on a topology.

## 7. Block D -- locked longitudinal benchmark and holdout

### Question and estimand

Can the instrument reproduce known prompt/output pairs and recover registered
effects over time, hardware, runtime, and model strata?  Before opening any D
measurement, select 12 fixtures from A--C using only their engineering validity,
not effect magnitude: four H-dose pairs, four cache pairs, and four topology
pairs.  Freeze six additional fixtures as a never-tuned holdout.  Each benchmark
block runs the 12 calibration pairs plus six holdout pairs, with condition order
balanced and labels blinded until reduction.

Primary outputs are (i) paired-effect estimates with 95% intervals, (ii)
standardized residuals against the A--C frozen reference, (iii) exact-output and
event-sequence pass rates, and (iv) a variance-components decomposition for day,
runtime version, model stratum, and pair.  Parameters are the registered H, P,
reuse, and B coordinates; therefore a new model need not reproduce another
model's natural-language behavior to enter the benchmark.

### Size, power, and Mac cost

- **Per block:** 18 pairs = **36 members**, about **1.25 Mac h** at 100
  s/member plus 25%.
- **Accumulation:** four weekly blocks give 72 paired differences.  A pooled
  fixed-effect check has 80% power at `d_z=0.330`; eight blocks/144 differences
  reach `d_z=0.233`.  Inference must cluster by fixture and day; these figures
  are optimistic upper bounds until the variance decomposition is available.
- **Detection-rate precision:** accumulate at least 30 holdout fixture-block
  observations before quoting a rate.  Report Wilson intervals and raw counts;
  do not call 3/3 or 6/6 a power estimate.
- **Cadence:** **1 block/week for eight weeks** (1.25 Mac h/week).  Also run one
  block immediately before and after an intended runtime/model/hardware change.
  Do not exceed two blocks/week, because dense same-day repeats estimate repeat
  noise rather than longitudinal drift.

### Risks and controls

- Repeated inspection can overfit the instrument to the benchmark.  Keep the
  six holdout fixtures inaccessible to tuning, version the calibration set, and
  require a prospective reason before replacement.
- Hardware and model changes can alter absolute joules.  Compare standardized
  paired effects and fit explicit strata; never claim absolute cross-model
  equivalence.
- A stable replay path can coexist with unstable ecological episodes.  D is an
  instrument control, not evidence that v4's agent trajectories are
  exchangeable or thermally controlled.
- Weekly cadence is vulnerable to scheduled OS work.  Randomize the start-time
  band within the approved quiet window and retain OS/power-source receipts.

## 8. Decision rules and information-per-hour comparison

| Block | Core pairs | Budget | Primary information per core block | Cadence |
|---|---:|---:|---|---:|
| A: H-dose | 40 | 2.5 h | continuous J/hidden-token slope; dose floor | 2/week |
| B: context/cache | 48 | 4.0 h | three token-cost coefficients + interaction + cell SDs | 1/week |
| C: topology | 48 | 3.3 h | boundary cost and tool-state contrast | 1/week |
| D: locked benchmark | 18 | 1.25 h | drift and reproducibility; cumulative holdout precision | 1/week |

For comparison only, v4's provisional W1 maximum is 12.4 h and its current
member costs are planning guesses, not arm-compatible sizing
[source: `configs/campaigns/align_v4/README.md:30-36`; source:
`configs/campaigns/align_v4/registration/sizing_preview.json:8-22`].  The proposed
core A--C program costs about **9.8 Mac h** and returns three response surfaces
from 224 deterministic members.  That arithmetic is a budget proposal, not a
claim that short members are interchangeable with v4 episodes.

Pre-register these decisions:

1. **Proceed A -> B -> C** if exact-output compliance is at least 95% and at
   least 90% of scheduled pairs remain complete.  Otherwise stop and repair the
   replay instrument; do not compensate by collecting more.
2. **Freeze D cells** from engineering-valid A--C fixtures without ranking their
   observed effect sizes.  If a minimum effect is needed for an instrument
   check, define it prospectively in physical units from the H/P/B coordinates,
   not from the largest observed contrast.
3. **Variance re-estimation** may alter the next not-yet-run block once, using
   condition-blinded pair differences and a frozen smallest relevant effect.
4. **Multiplicity:** one primary regression/contrast per block; simultaneous
   intervals for dose/cell follow-ups; all other slices explicitly exploratory.
5. **No transfer claim:** a coefficient is valid only for its frozen model,
   runtime, quantization, cache, and thermal stratum until Block D includes and
   passes a prospectively registered bridge.

## 9. What this program can and cannot buy

If successful, these blocks give finer effect-size resolution, direct physical
positive controls, interpretable token/cache/boundary coefficients, and a cheap
longitudinal control whose prompt/output pairs are deterministic.  They also
separate instrument variance from trajectory variance before another long Mac
campaign.

They do **not** repair v4's small ecological test cohort, prove a 5% false-positive
rate, establish sabotage-detection power, or show that replayed hidden tokens are
equivalent to naturally generated hidden reasoning.  V4 itself is explicit that
the sample-maximum threshold supports neither a realized 5% FPR nor detection
power and that a physical positive control is needed for a physical-computation
claim [source: `docs/align/council-2026-11-06-v4-review/CHAIR.md:307-313`].
Those limitations should remain in every registration and paper draft.
