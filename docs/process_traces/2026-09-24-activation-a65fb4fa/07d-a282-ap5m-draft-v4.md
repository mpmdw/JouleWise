# 07d — A282 AP-5M draft, version 4: the proposed MATH energy-per-correct analysis plan and D-166 addendum (PROPOSAL, gate-ruled text installed)

## For Ed, in plain words

This proposes the rules for one experiment, written before any data exist: on the five published difficulty levels of the MATH problem set, does the small model (Qwen3 1.7B) or the larger one (Qwen3 8B) use fewer joules of energy per correct answer?
If adopted, the project may claim, for this exact problem set, laptop and settings only: at each level, which model used less energy per correct answer, with an uncertainty range, and whether there is a difficulty level where the cheaper model switches from the small one to the large one.
It forbids: "harder problems cause more energy", "intelligence per joule", any claim about model ability or ranking, advice on which model to use, and anything beyond these five levels, two models, one machine and the answer-length limits.
Problems that run long are re-run, never dropped; if one breaks its registered time limit twice, the switch level is withheld until a single re-measurement settles it.
An independent reviewer has ruled on the text twice; nothing binds until you decide. Your decisions:

- E1: Should the MATH problem text itself be committed to the repository? (Recommended: no; commit only problem ids and fingerprints.)
- E2: Do you adopt these rules, including the new rules the reviewer wrote (listed in section 7)? (Yes or no.)
- E3: Should the models pick words by seeded random sampling, as the model makers recommend, instead of always taking the most likely word? (Recommended: yes.)
- E4: How many capture sessions (each a fixed stretch of measurement; 4–5 fit in a day) do you accept: about 14 (64 problems per level, about 3 days) or about 25 (128 per level, about 5–6 days)? (A number; the rules choose 128 only if it fits.)
- O-21: Should a claimed difference also have to exceed the smallest energy difference the instrument can detect, on top of the statistical test? (Yes or no.)

Written 2026-09-24 by an Opus 5.5 drafting subagent (a "seat": one delegated agent session with a bounded task)
for work item A282 of the project task queue, in the project-loop session identified as activation a65fb4fa. It
replaces version 3 (record 07c in this folder) completely. It carries the cold-gate ruling on version 2 (record
30/10, below) as amended by that gate's addendum ruling on its paired refuter's objections (record 30/21), and the
writing fixes of version 3. Read-only everywhere else.

## 1. Status, sources and how to read this file

**This is a proposal, not adopted claim policy.** AP-5M is a proposed row of the project's analysis-plan contract
(`docs/contracts/analysis_plans.md`): a filled table of rules that any published claim about MATH energy per correct
answer would have to cite and obey, written before any data exist. The accompanying D-166 addendum is a dated
amendment to decision-log entry D-166 (the project's workload decision), which today licenses scored benchmarks
only for the GSM8K leg (a separate scored workload of grade-school arithmetic word problems). The magistrate (the
agent that runs the project loop day to day) cannot adopt claim policy. A cold gate (a fresh Claude Fable instance
with no loop context) has ruled on version 2 (record 30/10), a paired refuter objected (record 30/11), and a
second cold instance ruled on the objections (record 30/21); the final texts of both rulings are installed here. Ed (the project owner) alone decides adoption, through his answer to question E2
of the decision brief emailed on 2026-09-23 (Gmail `1a0d069e15a52ba9`); that answer is still pending. Until Ed
answers, no sentence here binds any measurement, estimator or claim.

**Ed's questions.** The brief asks Ed four questions: E1 (publish the problem text?), E2 (adopt AP-5M and the D-166
addendum?), E3 (decoding rule, and which thinking mode is primary), E4 (problems per level, i.e. the capture budget). In this file "E1"
to "E4" mean these questions, with one exception: inside carried decision rules, the status code "E1" means "1.7B
cheaper" and always appears beside its partner code "E8" ("8B cheaper").

**Where the text comes from.** Project history is kept as numbered files ("records") in one folder per
supervisory session ("activation"), `docs/process_traces/<date>-activation-<id>/`. This file cites them by short
keys:

| Key | File | What it is |
|---|---|---|
| **C** | `docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md` | Packet C: the first design draft of AP-5M. |
| **19** | `…/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md` | The integration synthesis: the magistrate's record merging three design packets; its settled items are numbered M1–M13. |
| **18i** | `…/2026-09-23-activation-1d3796d5/18-headline-opus-integration.md` | The Opus integration consult behind record 19 (contains the planning arithmetic). |
| **08** | `…/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md` | The magistrate's rulings after the first review round of the draft analysis code ("round-1 rulings"). |
| **20** | `…/2026-09-23-activation-d8cc9c0a/20-a281-opus-consult.md` | An Opus consult that wrote the decision vocabulary and procedure. |
| **21/00, 21/10, 21/11** | `…/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/{00-charge, 10-coldgate-fable-ruling, 11-opus-contract-refuter}.md` | Cold gate 21: its charge, its ruling, and its paired refuter. |
| **45/10, 45/21** | `…/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/{10-coldgate-fable-ruling, 21-coldgate-fable-addendum-ruling}.md` | Cold gate 45: its ruling on the draft scheduling code and its addendum ruling. |
| **30/10** | `docs/process_traces/2026-09-24-activation-a65fb4fa/30-coldgate-packet-a282-ap5m/10-coldgate-fable-ruling.md` | Cold gate 30: the ruling on version 2 of this draft; questions Q1–Q18, final texts T-1 to T-23. |
| **30/11, 30/21** | `…/30-coldgate-packet-a282-ap5m/{11-opus-contract-refuter, 21-coldgate-fable-addendum-ruling}.md` | The paired refuter's objections R1–R17, and the addendum ruling on them (A1–A18), which supersedes or amends some T-n and adds T-24 to T-28. |
| **11, 12, 17, 18** | `docs/process_traces/2026-09-24-activation-a65fb4fa/{11,12,17,18}-*.md` | Reviews of versions 1 and 2 (source fidelity: 11, 17; teaching quality: 12, 18). |

Precedence, as ruled in 30/10 §0: decisions ratified by Ed and the contracts outrank cold-gate rulings on code work
items, which outrank consults, which outrank design packets. Among cold gates the later ruling prevails: 30/21, 30/10,
then 45/21 §7, 45/10, 21/10 with 21/11. Blockquoted text is copied byte for byte from the source named under it
(marked VERBATIM). Texts marked **T-n** are the gate's final texts, pasted byte for byte from 30/21 §3 where that ruling
supersedes, amends or adds them and from 30/10 §3 otherwise; §5 maps each
to its place. Anything else is this seat's drafting and has no authority beyond the proposal. Codes like D-062 or
C-004 are entries of the decision log or of the council log (the record of the project's multi-model review
meetings); each is glossed in one clause where first cited.

## 2. The proposed AP-5M row

### 2.1 Terms (read before anything below; each term uses only terms defined above it)

**Setup and problems.**

- **Registration.** The frozen, hashed record of every rule, constant and input fixed before any test problem runs
  (problem ids, caps, timing, bounds, seeds and the other settings named below), assembled as the *registration
  packet*. "Pinned" means fixed in the registration by version and content hash. Nothing registered changes once
  data exist; adding problems after seeing results (a "top-up") is forbidden (D-062: n is frozen before execution,
  and an outcome-dependent top-up demotes a result to exploratory, i.e. not claim-bearing).
- **Problem, level, reference answer.** A MATH problem is one competition-mathematics question with one reference
  answer, from the MATH dataset (Hendrycks et al., 2021), as redistributed in the PRM800K repository. Its *level*
  is the integer 1–5 the dataset's authors attached when they published it. It is fixed before any model sees the
  problem and is never computed from a model's success rate or answer length. In this plan "difficulty" means only
  this label.
- **Model, arm, decoding.** The two models are Qwen3 1.7B and Qwen3 8B, run as pinned 4-bit weights under MLX
  (Apple's machine-learning framework for Apple-silicon chips) on one M3 Max laptop. An *arm* is a thinking mode:
  *thinking on* (the model writes a reasoning trace before its answer) or *thinking off*. Both arms use the same
  problems. The decoding rule is Ed's decision E3: *greedy* (always the most likely next token, so a rerun repeats
  the same answer) or *seeded sampling* (random choice of next token from a fixed random seed, so a rerun under a
  different seed may differ).
- **Attempt, cap, capped, stop_reason.** An *attempt* is one generation by one model for one problem. The *cap* is
  the fixed maximum number of tokens an attempt may generate in an arm. An attempt that reaches the cap is
  *capped*; packet C calls the same thing *truncated*, and this file treats the two words as one. `stop_reason`
  records why generation stopped: the model's end token, or the cap ("length").
- **Cell.** One (model, arm, level) combination.
- **Scorer, correct, malformed.** The prompt asks the model to put its final answer in `\boxed{…}` (a "boxed
  answer"). The *scorer* is a pinned program that reads the last boxed answer and canonicalises both the boxed answer and the reference (removing TeX spacing, dollar signs, one trailing percent or degree sign without rescaling, a unit word and a leading "x =") and compares the results as exact rational numbers; so `44\%` matches `44`, and the disclosed accepted pair (`\frac12\%`, `\frac12`) is caught only by the per-cell audit, not by the scorer. An attempt is *correct* only when the scorer finds a match and the attempt is not
  capped. A *malformed* attempt has no extractable answer and counts as incorrect (D-047.6: malformed items count
  as incorrect in the accuracy denominator).

**The instrument.**

- **Power boundary and sampler.** Power is read by macOS `powermetrics`, the operating system's power sampler, at a
  100 ms sampling interval; each 100 ms reading is a *sample*. Its boundary is the Apple system-on-chip package:
  CPU + GPU + neural-engine power, summed over the rails (separately reported power domains) named in the rail
  manifest of the project's powermetrics reader (its "adapter"); display, storage, memory at the wall and
  power-supply losses are excluded (`docs/contracts/measurement_methodology.md` boundary table;
  `docs/paper/artifact-guide.md` §10.1). The *energy rail* identity in M13 means this rail manifest and boundary.
  Energy in a time interval is the sum, over sampler records, of each record's power times the duration of its overlap with the interval.
- **Envelope, envelope index, interior, capacity.** An *envelope* is one continuous, fixed-length power recording
  during which exactly one model is loaded. Envelopes follow one another on a fixed schedule: the *pitch* is the
  start-to-start spacing, and the *envelope index* 0, 1, 2, … is an envelope's position in the schedule of its night (one unattended capture session, built below).
  The planning design (packet B, record 09 of activation 1d3796d5, line 7) is a 600 s capture whose *interior*, the
  span in which problems run, is the 480 s starting 60 s after capture start (the 60 s is the *offset*); the values
  are registration numbers. *Capacity* is the number of seconds available for running problems: `interior_s −
  guard_s`, where `guard_s` is a registered safety margin left unused at the end of the interior (draft scheduling code
  `scored_registration.py:129` at `c0998fdb`; record 02b of this folder).
- **Idle slot.** An envelope recorded with its model loaded and doing nothing, labelled `kind: "idle_slot"`. It
  keeps the schedule grid evenly spaced. Its joules are never divided by anything to form a result.
- **Block, item, block window, gross block energy.** A *block* is a fixed list of problems from one cell, run back
  to back inside one envelope; each problem so scheduled is an *item*. A marker is written when its first item starts and when its last item ends (the block's
  *outer item edges*). The *block window* is the interval between those markers. *Gross block energy* is the joules
  the sampler records inside the block window, with nothing subtracted for idle power (D-045.7: per-item, block and
  level energies are gross only). In this file "window" alone means a block window, except in the phrase "capture
  window" (a night, below). Energy is read only per block window; per-problem energy inside a multi-problem block
  is never read.
- **Bundle, strict-valid, replacement rule.** A *bundle* is the directory of raw artifacts one capture produces
  (`docs/contracts/run_bundle_layout.md`). *Strict-valid* means the bundle passes that contract's strict reduction
  checks. A technically invalid bundle is re-run under the pre-declared *replacement rule*; a replacement is not a
  top-up (D-062).
- **Night (capture window), census-clean.** A *night* is one scheduled, unattended capture session holding a
  sequence of envelopes; the sources and the gate texts also call it a "window" or "capture window". *Arming* a night
  means installing its schedule for unattended start. *Census-clean* is a reference, not a definition written here:
  it means the night passed the project's coded agent census, which refuses a night while any process of the
  project's AI agents (command lines matching `codex|claude|t3`) is running, checked when the night is armed and at
  its start (`docs/phase_2/derivation_night_runbook.md` §0.6, "Census clean, and the night is agent-free");
  machine-activity admission is a separate contract (`docs/contracts/night_quiet_admission.md`). How retries extend
  a night is fixed in the "Nights and retries" term below (K23).
- **Instrument floor and anchor bound.** Two different error terms come from the instrument. (i) The *floor*: the smallest energy difference the instrument can distinguish from zero for a given window class, published as `floor_gate_j = max(floor_abs_j, floor_cmp_j)` by the calibration manifest (`docs/phase_2/detection_floor.md`, "Floor Artifact Semantics"): `floor_abs_j` is the larger of the largest absolute residual and the prediction bound `t_0.975 · s_r · √(1 + 1/n)` over repeated identical cells; `floor_cmp_j` is `max(max_i |δ_i|, |mean δ| + t_0.975 · s_δ · √(1 + 1/n))` over same-condition A-B-B-A contrast deltas δ_i (`detection_floor.md`, "Estimator rule"). Floors are calibrated per *window class* (request, phase, level, block …). AP-5M's window class is the block window; its floor row does not yet exist and is a registration prerequisite (row, Floor gate). The published per-phase figures are historical planning context only: an anchor envelope of about 0.7–1.0 J per phase boundary (D-078 clause 11) and operative phase floors of 3.823787 J prefill and 7.377086 J decode gate (D-079 as amended by D-084). No block-window value may be inferred from them. (ii) The *anchor bound* `anchor_j` (`E_clock_anchor_shift_bound_j`): the most energy that can be assigned to the wrong window because the marker clock and the sampler's clock may be offset; it is the only instrument term inside the interval. Under D-078 clause 11 the floor and the anchor bound play separate roles and neither may be dropped as a double count: the floor gates each block window; the anchor bound widens the interval.
  In the floor formulas, n is the number of strict-valid bundles (defined above) in the calibration cell, s_r the
  sample standard deviation of the residuals, δ_i the contrast delta of one A-B-B-A pair and s_δ the sample standard
  deviation of those deltas, and t_0.975 the 97.5 %
  quantile of Student's t distribution with n − 1 degrees of freedom. D-079 and D-084 are the decisions that fixed
  the published phase floors; D-078 clause 11 is the decision that set the instrument's attribution limit and the
  separate roles of floor and anchor bound. The anchor bound is recorded per window: anchor_{j,w} denotes
  window w's value (K11). The contract's *single-count discipline* is its rule that the floor and the anchor bound
  each keep their own role and neither is dropped as a double count. A *residual* is one measurement minus its cell mean; the *prediction bound*
  is the formula's second term; A-B-B-A contrasts are same-condition measurement pairs run in the alternating order A,
  B, B, A; the *calibration manifest* is the P2-015 artifact (P2-015 being the work item that issues it) that
  publishes one floor row per backend, metric, window class and condition family. "The interval" is the uncertainty
  interval on the between-model energy ratio, built under Estimation below; prefill and decode are the two phases of a generation (reading the
  prompt, then producing tokens).

- **J/correct, R_L, factors.** A cell's *J/correct* is its summed gross block energy divided by its number of
  correct attempts. It factors exactly as J/correct = J/token × tokens/attempt ÷ accuracy (J/token = cell energy ÷
  cell generated tokens; tokens/attempt = generated tokens ÷ n, with n the problems per cell; accuracy = correct ÷
  n). *R_L* = J/correct(8B) ÷ J/correct(1.7B) at level L in one arm. R_L < 1 means the 8B spent fewer joules per
  correct answer on that level's problems. R(E₈, E₁.₇) below means this ratio computed from the two models' energies
  E₈ and E₁.₇ with the correct counts held fixed; these E symbols are energies, not the status codes E8/E1 defined
  later.

**Scheduling and retries.**

- **Sizing pilot.** Before the test, 16 problems per level (disjoint from test problems) are run on the bench
  without power capture ("bench token pilot") to measure tokens per item, cap hits and rough seconds per token, then
  one short measured "shakedown" night checks envelope timing (M4 of record 19). Its outputs set only the
  quantities K2 lists, as extended for this plan by T-24; it is never reported as a result.
- **Packer, roster, parent block, piece.** The *packer* is the program that assigns blocks to envelopes before the
  night; its output list is the *roster*. A *parent block* is a block placed by this initial packing. A retry can
  cut a parent into one-problem blocks; each is a *single*, also called a *piece* of its parent.
- **Predicted, worst-case and reserved seconds.** `predicted_s` is the packer's forecast of a block's duration from
  the sizing pilot. The *derived worst case* of one problem is `cap_tokens × s_per_token_upper + prefill_s`: the cap
  times a registered upper bound on seconds per generated token, plus the time to read the prompt. This is a
  registered **assumption**, not a physical law: the plan assumes no attempt takes longer, and an attempt that does
  has a defined status consequence (it advances a retry stage, and a second excess ends the problem's retries;
  K13 (N)). `reserved_s` is the time the packer sets aside for a block. `ceiling_s` is the per-attempt kill timeout
  the night runner (the program that executes a night) enforces, registered so that worst case ≤ `ceiling_s` ≤
  capacity.
- **Overrun, observation, culprit, innocent.** An *overrun* is an envelope ending, or an attempt being killed,
  before all its blocks finish. Each block in that envelope then receives an *observation*: `completed`, `cut_off`
  (started, not finished) or `not_started`, with its elapsed seconds where it ran. A *culprit* is a block whose
  elapsed time exceeded its `predicted_s` (at the single stages, its derived worst case): the block that used up
  the time. An *innocent* block was cut off or never started because a culprit used up the time.
- **Retry stages, terminal states.** Forcing problem: the envelopes have fixed length, and the longest attempts are
  the most expensive, so dropping attempts that overrun would remove exactly the costliest hard problems and bias
  the hard levels' energy per correct answer downward. So nothing is dropped. A culprit moves through fixed stages: `initial` →
  `whole_block` (the whole block re-run alone in a fresh envelope) → `single_problem` (each problem as its own
  single) → `single_retry` (one more attempt of a single that exceeded its worst case) → `ceiling_violation`. A
  *ceiling violation* is a single that exceeds its derived worst case twice; it shows the registered assumption false
  for that arm, so it is terminal, not a retry path. `unattributed_overrun` is the terminal state for blocks left
  unfinished in an envelope that holds no culprit; under correct instrumentation it cannot occur, so it signals a
  fault. Terminal states are listed in `terminal_refusals`.
- **Recapture.** A registered re-measurement on a later census-clean night, allowed only where a rule names it.
- **Voided and counted windows.** A *voided* window belongs to an attempt that a retry superseded; it stays on
  record and is never counted. A *counted* window is one whose energy enters a cell sum.
- **Counted attempt (K24).** For every problem and model at most one attempt is *counted*: the one whose window is counted. Its correct flag and generated tokens are the problem's values in every computation. Every superseded attempt's answer and tokens are recorded and never used. When a superseded and a counted attempt of one problem disagree in correctness, `attempt_divergence` is recorded for disclosure (expected never under greedy decoding, possible under seeded sampling). A problem with no counted attempt for either model (terminal `ceiling_violation`, `unattributed_overrun`, `night_exhausted`, or a `below_floor` refusal) contributes to neither model's energy nor correct count nor n for that cell; its level carries that reason and is NR under step 12 (NE if `ceiling_violation`) until the K22 or S8 recapture; the cell's printed numbers state how many problems were dropped and why.
  (Reading note for K24: NR, "not resolved", and NE, "not estimable", are the group statuses built under
  Estimation below; step 12 is the status step of §2.2; S8 is the ceiling-violation recapture of §3; K22 is the flag
  recapture of §2.9.)
- **Claims ladder, rung.** The project's claims ladder (`docs/contracts/claims_ladder.md`) ranks claim strength in
  *rungs*: rung L0 capability, rung L1 instrument result, rung L2 comparative result, rung L3 model fit, rung L4
  generalized finding. Rung L2 requires "n ≥ 5 per condition", strict-valid bundles (below), confidence intervals,
  and an effect clearing the detection floor. Outside carried text this file writes "rung L2" to avoid confusion
  with MATH Level 2; the carried row text "Ceiling L2" means rung L2.
- **Spread, M8.** A cell's *spread* is the number of its parent blocks and the number of distinct envelopes holding
  their counted windows (this file uses "spread" in no other sense). Forcing problem: blocks inside one envelope
  share its temperature and background load, so they are not independent energy measurements; independent
  repeated measurements need separate envelopes. M8 (record 19) meets rung L2's "n ≥ 5" by requiring at least five parents in
  at least five distinct envelopes per cell.
- **Position, drift lever, drift model, drift threshold.** Forcing problem: the machine's power drifts slowly across
  a night. If one model's blocks sit systematically later, drift biases the ratio between models. A parent's
  *position* is the item-weighted mean envelope index of its counted windows. The *drift lever* of a level is the
  absolute difference between the mean position of its 8B parents and that of its 1.7B parents, in envelope slots.
  The registered drift model is: within a night, gross block energy drifts linearly in envelope index with one slope, of magnitude at most δ_upper joules per block per slot, shared by both models; each night has its own intercept, and balance within every night is what cancels it. Under that model a level's between-model bias within a night is at most δ_upper × P × lever, and lever 0 cancels the drift exactly. For any other drift shape this rule bounds nothing; it is the registered tolerance, not a proof. `max_gap` is defined in K12; the packer aims for lever 0 and a roster is accepted if lever ≤ `max_gap`.
  The *drift threshold* is `max_gap = budget_j / (δ_upper · P)`, registered per (arm, level), with P the number of parent blocks per cell per model (the registered n ÷ problems per block). `δ_upper` (joules per block per slot) is registered per arm from that arm's shakedown night: each model runs one fixed block of pilot problems twice, in its first and last envelopes of that night; for each model compute `(|E_last − E_first| + floor_gate_j) ÷ (slot separation)` with the block-window `floor_gate_j` of T-6, and δ_upper is the larger of the two models' values; a shakedown lacking either pair refuses registration. `budget_j` for (arm, level) is 0.01 × the smaller of the two models' projected energies for that cell at the registered n, where a model's projection is its mean pilot generated tokens per problem at that level × n × its shakedown seconds per token × its mean shakedown power; so the admitted bias moves that level's R_L by at most about one percent. δ_upper, every `budget_j` and every `max_gap` are hashed in the registration packet before any test problem runs.
- **Nights and retries (K23).** Retries and reschedules extend the same night: a "fresh envelope" is appended to that night's schedule up to the registered `max_envelopes_per_night`. Any block unfinished when the night ends is the terminal refusal `night_exhausted` (a `terminal_refusals` entry); its cell is unresolved until the K22 recapture. Envelope indices start at 0 in every night, including a recapture night. A level's drift lever is computed within each night over that night's counted windows of both models, and the level's lever is the largest of its nights' levers; a night holding counted windows of only one model for a level has no lever and is a K22 defect (`recapture_unpaired`).

**Estimation.**

- **Bootstrap, replicate, low and high side, interval.** The *bootstrap* estimates sampling uncertainty by
  redrawing, with replacement, from the observed parent blocks and problems many times (B = 20,000); each redraw is
  a *replicate*. Each replicate yields a *low-side* ratio (energies moved by the anchor bound in the direction that
  makes the 8B look cheapest) and a *high-side* ratio (moved the other way). A replicate whose 8B draw has zero
  correct answers has ratio +∞; one whose 1.7B draw has zero has ratio 0; zero for both is *undefined*.
  The *interval* runs from the 2.5th percentile of the replicate low-side ratios to the 97.5th percentile of the replicate high-side ratios (K11); its ends are `lo` and `hi`. The point bounds (s = 1) are reported beside it as `point_low` and `point_high` and do not alter `lo` or `hi`.
- **p_below, p_above, p_L.** `p_below` = (1 + the number of replicates whose high-side ratio is ≥ 1 or undefined) ÷
  (B + 1): small when nearly every replicate says the 8B is cheaper. `p_above` = (1 + the number of replicates whose
  low-side ratio is ≤ 1 or undefined) ÷ (B + 1). `p_L = min(1, 2·min(p_below, p_above))` is the two-sided p-value
  for level L.
- **Holm, family, primary, secondary.** Forcing problem: testing five levels gives five chances of a false finding.
  A *family* is the fixed set of hypotheses tested together: one family per arm, five hypotheses "R_L = 1". *Holm's
  procedure* keeps the chance of any false rejection in a family at or below α (0.05). With m = 5: sort the
  family's p-values ascending as p(1) ≤ … ≤ p(m); reject the k-th while p(k) ≤ α/(m − k + 1); stop at the first
  failure. The thinking-on family is *primary* (it alone can carry the headline); thinking-off is *secondary*.
- **Denominator guard, sparse, merge, group, pooled.** The *denominator guard* is an observed count: a model passes at a level (or merged group) when at least 3 of its attempts there are correct. A level is *sparse* in an arm when either model fails the guard there (K9). A sparse level is *merged* with a neighbour in a fixed order (§2.4), decided on correct counts only. The result is a set of *groups*: single levels or merged runs such as "4–5". A merged group is tested as one hypothesis; its constituent levels are *pooled* and each carries `pooled_in` (the group's levels). AP-5M expressly replaces AP-5's phrase "binomial lower-bound must be >=3 correct per level" with this observed count for this plan; the substitution is part of what Ed adopts under E2.
- **Group status, three-way test.** Each tested group gets one of four statuses: *8B cheaper* (code E8, letter
  `8`), *1.7B cheaper* (E1, letter `1`), *not resolved* (NR, letter `n`: the evidence does not settle the direction;
  inconclusive, not a null), or *not estimable* (NE, letter `e`: no ratio can be computed, with a reason such as
  `sparse_after_merges` or `ceiling_violation`). A pooled constituent of an estimable group carries letter `p`. The
  *three-way test* (S2) gives a direction only when Holm rejects, p gives the direction, and the interval lies
  wholly on that side of 1. The floor contract calls this interval test *zero-exclusion*: the interval must
  exclude the no-difference value, which for a ratio is 1. `interval_disagrees` flags a group whose Holm test rejected but whose interval still
  contains 1; such a group is NR.
- **Pattern, licensing group, boundary group, L\*, region statement, supported switch.** Reading the resolved
  groups (E8 or E1) in level order gives a *pattern* (named in §3 S0). The *boundary group* is the first 8B-cheaper
  group; the *licensing group* is the last 1.7B-cheaper group before it. A *supported switch* is such a
  1.7B-then-8B change licensed by §3. The *crossover level L\** is the boundary group's level, reported only when
  the boundary group is a single level. When the licensing group is pooled, the claim may only be a *region
  statement*: it names the pooled range, never a constituent level.
- **Gap levels, bracket gap levels.** *Gap levels* are every NR or NE level in the family. *Bracket gap levels* are
  the gap levels lying strictly between the licensing group and the boundary level.
- **Cap-bound.** A cell with more than 20 % capped attempts.
- **Selection-confounded sensitivity.** A secondary re-analysis that removes some attempts for both models (for
  example the retried ones). Because it removes exactly the longest problems, it is labelled as confounded by that
  selection and never replaces the primary estimate. A *balanced recapture* re-measures both models' affected
  problems at matched positions.
- **spread_exceeded, drift_exceeded.** Flags that a cell lost its minimum spread after capture, or that a level's executed drift lever exceeded `max_gap`. Either flag on any constituent makes the whole group NR with that reason and `flagged_levels` listing the constituents; the group's numbers are still printed.

### 2.2 Analysis procedure, from raw rows to a per-level verdict

Run once per arm. Each step names the clause that governs it.

1. **Label attempts.** capped := generated tokens ≥ the arm's cap; the row's `stop_reason` must agree (end token vs
   "length") or the reducer (the program that turns rows into cell sums) refuses the row. correct := scorer match
   and not capped; malformed := incorrect (K3).
2. **Select counted windows.** Exclude voided windows. A terminal `ceiling_violation` attempt's window is recorded
   but never enters a cell sum (K17). Refuse any block window at or below `floor_gate_j` for the block-window class (row, Floor gate); the refusal is `below_floor`, the window is not counted, and its problems follow the counted-attempt rule (K24).
3. **Form each parent's energy per model.** g = the sum of the parent's counted windows for that model; k = the
   number of those windows (1 for an unsplit parent; the number of counted singles for a split parent). Pairing is on
   the parent (K13 (a)). Each problem's correctness and tokens come from its counted attempt (§2.1, K24); a problem with none is dropped
   from both models as K24 says.
4. **Spread check per cell.** At least five parents with every item counted, in at least five distinct envelopes;
   else `spread_exceeded` (K15), which makes the whole group NR (§2.1); the one cure is the K22 recapture. Before
   capture the same shortfall is a packing refusal.
5. **Drift check per level.** Compute positions and the lever within each night and take the largest (K23, K12);
   compare with the registered `max_gap`; excess ⇒ NR(`drift_exceeded`), cured only by the K22 recapture.
6. **Denominator guard and merge.** Apply the guard (§2.1, K9) per model per level; merge sparse levels in the fixed
   order (§2.4, S2 `merge`); a group still failing is NE(`sparse_after_merges`).
7. **Point estimate per tested group.** R = (Σ E_8B ÷ Σ correct_8B) ÷ (Σ E_1.7B ÷ Σ correct_1.7B) over the
   group's levels; point bounds with U = Σ over the group's parents of Σ_w anchor_{j,w} per model (K11).
8. **Bootstrap, B = 20,000.** Per replicate: draw parents within each level of the group, then problems within each
   drawn parent, both paired across models; scale each drawn parent's energy by the model's own drawn-token share s;
   add bound u = s · Σ_w anchor_{j,w}; form the low-side and high-side ratios (K10, K11; worked in §2.5).
9. **p-values** p_below, p_above, p_L (§2.1).
10. **Holm**, m = 5 fixed, over the tested groups. A group is *tested* when it is estimable and no constituent level carries `ceiling_violation`, `spread_exceeded`, `drift_exceeded`, `unattributed_overrun`, `night_exhausted` or `below_floor`; all of these are determined before this step. Untested groups have their p-values computed and reported but excluded from the sort, and m stays 5. (A flag-forced level cannot change status whatever its p-value; leaving it in the sort could only loosen the thresholds for the others.)
11. **Interval** per group: The *interval* runs from the 2.5th percentile of the replicate low-side ratios to the 97.5th percentile of the replicate high-side ratios (K11); its ends are `lo` and `hi`. The point bounds (s = 1) are reported beside it as `point_low` and `point_high` and do not alter `lo` or `hi`.
12. **Group status** by the three-way test (S2); then flags, in this precedence: NE(`ceiling_violation`) first; otherwise NR listing every applicable reason in the order `spread_exceeded`, `drift_exceeded`, `unattributed_overrun`, `night_exhausted`, `below_floor`; every applicable flag is recorded true whatever the printed status.
13. **Level statuses** (S9), **pattern and L\*** (S2 `classify`, checked against the S11 table). A ceiling violation
    anywhere in the family withholds L\* (S7) until one recapture (S8); a failed check during that recapture makes
    the withholding terminal (S8, final paragraph).
14. **Sensitivity pass.** Repeat 7–13 with retried items removed for both models; if any Holm direction or L\*
    changes, that claim is reported unresolved until a balanced recapture (K13 (d)).
15. **Labels and sentences.** Cap-bound label per cell (K3); claim sentence from S3, S6 and S10; three factors and
    gross energy displayed beside every J/correct (§4 ruling (3)).

### 2.3 Worked example: one level (planning figures, unmeasured)

Packet C's planning stand-ins come from `docs/research_question_bank.md:1615-1616`: about 47 J (1.5B) and 192 J (7B)
per 512 decoded tokens, i.e. 47 ÷ 512 ≈ 0.092 J/token and 192 ÷ 512 = 0.375 J/token. They are not measurements.

*One level.* Thinking on, Level 5, n = 64. The 1.7B spends 0.092 J/token × 4,000 tokens/attempt = 368 J per attempt,
64 × 368 = 23,552 J per cell, and gets 16 correct (25 %): 1,472 J/correct. The 8B spends 0.375 × 2,500 = 937.5 J
per attempt, 60,000 J per cell, and gets 40 correct (62.5 %): 1,500 J/correct. R_5 = 1,500 ÷ 1,472 = 1.019. The 8B
needed an accuracy ratio of (0.375 ÷ 0.092) × (2,500 ÷ 4,000) = 2.55 to break even and achieved 0.625 ÷ 0.25 = 2.50.

*Spread.* Five parents of 13, 13, 13, 13 and 12 problems, the same membership for both models, each in its own
envelope: M8 holds.

*Anchor bound.* With Σ_w anchor_{j,w} = 2 J (illustrative; one window per parent), each model's point bound is U = 5
parents × 2 J = 10 J, giving `point_low` 1.0184 and `point_high` 1.0196 around 1.0190. (Each block window must also
clear the block-window floor gate, a separate check; no value exists yet.)

*Sampling width.* Record 18i gives the planning interval as "×/÷ 1.59" at n = 64: the interval runs from the point
value ÷ 1.59 to the point value × 1.59, here [0.64, 1.62]. It comes from the binomial variability of the two
accuracies on a log scale: SE² ≈ (1 − 0.25)/(64 × 0.25) + (1 − 0.625)/(64 × 0.625) = 0.0469 + 0.0094 = 0.0563, SE =
0.237, and e^(1.96 × 0.237) = 1.59; at n = 128, SE = 0.168 and the factor is 1.39. Token variance widens both
further. The sampling width exceeds the anchor bound by more than two orders of magnitude; this level would be NR.

### 2.4 Worked example: denominator guard and merge order

Why a guard: J/correct divides by the correct count, so with 1 or 2 correct answers a single problem changes the
ratio by a factor of 2 or 3. Why merge toward Level 3: a sparse level joins its neighbour on the side nearer the
middle of the scale, so extremes are pooled with their nearest levels and never with each other.

```
Level line:     [1] <-> [2] ---> [3] <--- [4] <-> [5]
first moves:    1 and 2 join as "1-2"    4 and 5 join as "4-5"
                (when either is sparse)  (when either is sparse)
second moves:   "1-2" joins 3            "4-5" joins 3
                (if still sparse)        (if still sparse)
Level 3 alone:  never moves; if sparse by itself it is not estimable
```

Every element: each bracket is a level; `<->` is a first-stage merge between the two outer pairs; `--->` and
`<---` are second-stage merges into Level 3. This is the S2 `merge` rule: a sparse Level 4 alone joins 5, and a
sparse Level 2 alone joins 1 (record 20 Q2, adopted by 21/10 §Q1).

*Numbers (illustrative, n = 64 per level).* Correct counts by level 1–5: 8B 30, 25, 14, 6, 2; 1.7B 20, 12, 5, 2, 1.
Levels 4 (1.7B has 2) and 5 (8B 2, 1.7B 1) are sparse, so 4 and 5 join: group "4–5" has 8B 8 and 1.7B 3, passing,
so it stops. Levels 1–3 pass. Partition: 1 | 2 | 3 | 45.

### 2.5 Worked example: one bootstrap replicate (illustrative numbers)

Why two tiers: energy is measured per parent block, correctness per problem, so the resampling must redraw parents
(the energy replicates) and, inside each, problems (the correctness replicates), pairing both across models. Why the
share s: a replicate that redraws a parent's problems carries that parent's energy in proportion to the tokens the
drawn problems generated for that model; the anchor bound is scaled the same way.

A toy level with three parents (A, B, C) of three problems each. Σ_w anchor_{j,w} = 2 J (illustrative; one window per parent).

| Parent | 8B tokens per problem | 8B correct | 8B g (J) | 1.7B tokens per problem | 1.7B correct | 1.7B g (J) |
|---|---|---|---|---|---|---|
| A | 2000, 2600, 3000 | 1, 1, 0 | 2,850 | 4000, 3600, 4400 | 0, 1, 0 | 1,104 |
| B | 2400, 2200, 2800 | 1, 0, 1 | 2,775 | 3800, 4200, 4000 | 1, 0, 0 | 1,104 |
| C | 2500, 2700, 2300 | 1, 1, 1 | 2,810 | 4100, 3900, 4000 | 0, 1, 1 | 1,100 |

Point estimate: 8B 8,435 J / 7 correct = 1,205 J/correct; 1.7B 3,308 J / 4 = 827 J/correct; R = 1.457, with
`point_low` 1.4534 and `point_high` 1.4608 (U = 6 J per model), reported beside the interval.

```
tier 1: draw 3 parents with replacement (same draw for both models)
        observed parents:   A    B    C
        draws:              draw #1 = B    draw #2 = C    draw #3 = B
tier 2: inside each draw, draw 3 problem positions with replacement (same positions for both models)
        draw #1 (B): positions 1, 1, 3     draw #2 (C): positions 2, 3, 3     draw #3 (B): positions 2, 3, 1
per model, per draw:  s = drawn tokens / parent tokens;  e = g * s;  u = s * Σ_w anchor_{j,w};
                      correct = sum of drawn problems' flags
sum over draws:       E, U, correct  ->  R*, low side, high side
```

Every element: "observed parents" are the level's parent blocks; "draws" are the three draws of tier 1; "positions"
are the problem draws of tier 2 inside the parent chosen by that draw; s, e, u and correct are computed separately
for each model from its own tokens, energy and flags.

| Draw | 8B tokens | s | e (J) | u (J) | correct | 1.7B tokens | s | e (J) | u (J) | correct |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 B (1,1,3) | 7,600 | 1.02703 | 2,850.00 | 2.0541 | 3 | 11,600 | 0.96667 | 1,067.20 | 1.9333 | 2 |
| #2 C (2,3,3) | 7,300 | 0.97333 | 2,735.07 | 1.9467 | 3 | 11,900 | 0.99167 | 1,090.83 | 1.9833 | 3 |
| #3 B (2,3,1) | 7,400 | 1.00000 | 2,775.00 | 2.0000 | 2 | 12,000 | 1.00000 | 1,104.00 | 2.0000 | 1 |
| Sum | | | 8,360.07 | 6.0007 | 8 | | | 3,262.03 | 5.9167 | 6 |

R\* = (8,360.07 ÷ 8) ÷ (3,262.03 ÷ 6) = 1.9221. Low side = ((8,360.07 − 6.0007) ÷ 8) ÷ ((3,262.03 + 5.9167) ÷ 6) =
1.9173. High side = ((8,360.07 + 6.0007) ÷ 8) ÷ ((3,262.03 − 5.9167) ÷ 6) = 1.9270. This replicate adds one to the
`p_below` count (high side ≥ 1) and nothing to the `p_above` count (low side > 1). After 20,000 replicates `lo` is the
2.5th percentile of the low sides and `hi` the 97.5th percentile of the high sides.

### 2.6 Worked example: retries, drift and a ceiling violation (illustrative timings, not measured)

Assumed for the drawings: capacity 540 s; derived worst case ≈ 200 s per problem (8,192-token cap × 0.02 s/token
upper bound + 36 s prefill); `ceiling_s` = 360 s; parent P3 holds four Level-5 problems P3.a–P3.d with `predicted_s`
250 s. All envelopes shown belong to one night.

*Panel 1: the ordinary path.*

```
envelope index ->  4                        ...  20                          21                        22
model loaded       1.7B                          1.7B                        1.7B                      1.7B
                 +------------------------+    +---------------------------+ +-----------------------+ +-----------------------+
stage            | initial                |    | whole_block (P3 alone)    | | single_problem        | | single_problem        |
blocks           | P7 (L2): completed,    |    | P3 retry, 4 problems      | | P3.a   P3.b           | | P3.c   P3.d           |
                 |   180 s <= 200 s pred. |    |   reserved_s = 540 s      | |   200 s reserved each | |   200 s reserved each |
                 | P3 (L5): cut_off,      |    |   = min(4 x 200, 540)     | |   both completed      | |   both completed      |
                 |   360 s > 250 s pred.  |    |   not completed -> split  | |                       | |                       |
                 |   => culprit           |    |                           | |                       | |                       |
                 +------------------------+    +---------------------------+ +-----------------------+ +-----------------------+
P3 windows         voided                        voided; envelope keeps        counted: 2 problems       counted: 2 problems
                                                 voided_block_ids = [P3]
time ------------------------------------------------------------------------------------------------------------------>
```

Every element: the top row is the **envelope index**; "…" stands for envelopes 5–19 of the initial roster. **Model
loaded** is the one model in that envelope. Each box is one **envelope**. **Stage** is the retry stage of the P3 work
in it. **Blocks** lists what ran: P7, an unrelated Level-2 parent, completed inside its `predicted_s`, keeps its
window and is not a culprit; P3 is cut off after 360 s against a 250 s prediction, so it is the culprit and advances
to `whole_block`. Envelope 20 holds the whole-block retry alone, reserved at the smaller of the **sum** of its four
problems' worst cases (4 × 200 = 800 s) and capacity (540 s); it does not complete, so it splits. **voided_block_ids**
is the envelope's list of blocks whose attempts there were superseded; it makes envelope 20 a legal envelope with no
active block. Envelopes 21 and 22 hold the four **singles**, reserved at 200 s each, two per envelope because three
would need 600 s. Pieces of one parent may share an envelope; two parents of one cell may not. **P3 windows** says
which recordings count. **Time** runs left to right; every retry sits at a higher index than the envelope where its
overrun was observed, and all of these envelopes extend the same night (K23).

*Drift from panel 1.* At pack time the Level-5 thinking-on parents sit in envelopes 1, 5, 9, 13, 17 for the 8B (mean 9)
and 0, 4, 8, 12, 16 for the 1.7B (mean 8): lever 1.0 slot. After the retry P3's position is (21 × 2 + 22 × 2) ÷ 4 =
21.5; the 1.7B mean becomes (0 + 21.5 + 8 + 12 + 16) ÷ 5 = 11.5; the lever grows to 2.5 slots. *Threshold
(illustrative values; the registered values come from the arm's shakedown night as in K12):* δ_upper = 2 J per block
per slot; budget_j = 0.01 × 23,552 J = 235.5 J (K12's rule applied to the planning cell of §2.3, the smaller of the
two models' cells); P = 5 parents per cell; max_gap = 235.5 ÷ (2 × 5) = 23.55 slots; 2.5 ≤ 23.55, so the roster is
accepted. Under the registered drift model (linear in envelope index within a night, one slope shared by both models)
the bias is at most 2 × 5 × 2.5 = 25 J against a 23,552 J cell (0.1 %).

*Panel 2: an alternative history for envelopes 21 and 23 (a ceiling violation and an innocent reschedule).*

```
envelope index ->  21                                        23
model loaded       1.7B                                      1.7B
                 +---------------------------------------+ +---------------------------------------+
blocks, in       | P3.a single_problem, reserved 200 s   | | P3.b single_problem (rescheduled),    |
run order        |   killed at ceiling_s after 360 s     | |   completed in 170 s                  |
                 |   360 > 200 worst case => culprit,    | | P3.a single_retry, reserved 200 s     |
                 |   advances to single_retry            | |   killed at 360 s > 200 s             |
                 | P3.b single_problem, reserved 200 s   | |   => ceiling_violation (terminal)     |
                 |   starts at 360 s, cut_off by the     | |                                       |
                 |   envelope end after 180 s <= 200 s   | |                                       |
                 |   => innocent, rescheduled at the     | |                                       |
                 |   same stage without advancing        | |                                       |
                 +---------------------------------------+ +---------------------------------------+
counted windows    none                                      P3.b (P3.a's window recorded on its
                                                             terminal refusal, never counted)
```

Every element: as in panel 1; "killed at ceiling_s" is the runner's per-attempt timeout; "rescheduled at the same
stage" is the innocent path of K13 (N); "terminal refusal" is the `terminal_refusals` entry. Envelope 22 still holds
P3.c and P3.d as in panel 1 (400 s reserved), so a further 200 s single does not fit its 540 s capacity; the first
later envelope with room is 23. *Consequences:* parent P3 now has an item with no counted window, so the cell (1.7B,
thinking on, Level 5) has four complete parents and carries `spread_exceeded` (K15); the group containing Level 5 is
NE(`ceiling_violation`), which takes precedence (K16); L\* is withheld with reason `ceiling_violation_unresolved`
(S7). The violation also sets `s_per_token_upper_falsified: true` for the arm (S8). One recapture is allowed: on a later census-clean night, P3.a is run once by each model as a single, in
adjacent envelopes (this seat reads "adjacent" as consecutive indices; §8 Residual); the night's other blocks for that
arm are checked against `s_per_token_upper`; a second violation, or a failed check, makes the withholding final for
this registration (S8).

### 2.7 Placement

A new subsection `### AP-5M: MATH author-level energy per correct answer, two model sizes` inserted after AP-5 in
`docs/contracts/analysis_plans.md`. AP-5 is the existing row governing a synthetic scored workload,
`affine_mod_ladder_v1`: generated answer-only modular-arithmetic problems whose difficulty is set by construction
while answer length is held fixed. AP-5 gains one line: "Amendment (D-166 addendum, proposed 2026-09-24): MATH
author-level strata are AP-5M, which inherits this row's forbidden upgrade and quarantine." (A *forbidden upgrade* is
the stronger claim a row explicitly bans; the *quarantine* (C-004) records correctness as an annotation used only as
a denominator, never as a capability claim.) The registry paragraph listing separate families adds "MATH level
energy per correct answer" (packet C §2b).

### 2.8 The row

Fields follow the AP-5 row in order; five fields marked *(added)* have no AP-5 slot (kept, 30/10 Q18). Clause
references K-n point to §2.9.

| Field | Value |
|---|---|
| Plan ID / RQ consumer | AP-5M / research question RQ-NEXT-EPCA-LEVELS (energy per correct answer vs published difficulty), headline: MATH author-level energy per correct answer, Qwen3 1.7B vs 8B (D-166 dated addendum, §4, proposed). |
| family_id | FAM-MATHLVL-EPC-THINKON (primary); FAM-MATHLVL-EPC-THINKOFF (secondary). The registration field `arm_to_family` derives the family from the arm. |
| claim_role | Thinking-on R_L: primary. Thinking-off R_L: secondary; it cannot carry the crossover headline. |
| Estimand *(added)* | For each arm and level L, R_L on the frozen problem set (K1), this machine (M3 Max), pinned weights, prompt template, scorer and extractor, the arm's cap, and the decoding rule Ed fixes under E3. The headline quantity is the thinking-on crossover level L\*, which exists only where §3 licenses it. |
| selection_scope | Problem set K1; Qwen3 1.7B and 8B; two arms; levels 1–5; the same problems for both models and both arms; pinned template, scorer, extractor and caps (K3). Nothing else is searched. |
| multiplicity_rule | Holm within each family, α = 0.05 two-sided, m = 5 fixed (one hypothesis R_L = 1 per level; a merged cell tests one hypothesis and m stays 5). Holm: sort p ascending; reject the k-th while p(k) ≤ α/(m−k+1); stop at the first failure. NE groups and flag-forced NR groups are not tested; m stays 5 (§2.2 step 10). |
| Metric + exact window class | Gross block energy (K4) summed per cell; J/correct; the three factors, descriptive only (K5); capped and malformed counts; the cap-bound label (K3). Window class: block window, gross. |
| Capture unit *(added)* | The envelope, one model loaded, one thinking arm per night; the block window inside it; the parent block as the energy replicate (the unit treated as an independent energy measurement); idle slots captured, never divided into a result (K6). |
| Unit of analysis + dependence structure | Problem for correctness and tokens (distinct problems, D-047.3: token and correctness statistics are over distinct items; repeated captures replicate energy only), each problem's values taken from its counted attempt; parent block for energy. Spread K7; retry tails K8. |
| Estimator/formula | R_L with the paired, block-aware bootstrap and share-scaled anchor bound (K10, K11); status by the three-way test (§3 S2). |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only; a bundle contaminated by outside machine activity is re-run under the replacement rule, not waived. The pre-campaign smoke gate K21. Capped = incorrect (K3); malformed = incorrect (D-047.6). Terminal-attempt windows K17. Pilot rosters K18. |
| Order/blocking/covariates | The packer aims for equal mean envelope position per cell across models (the objective); a roster is accepted if the drift lever ≤ `max_gap` (the registered tolerance), and an executed excess makes the level NR (K6, K12, K23). The idle reference (idle-slot energy per envelope, per model) is recorded and reported beside results per window; no computation in this plan adjusts any energy or R_L by it, and any exploratory use is labelled exploratory. |
| Floor gate | Every counted block window must exceed `floor_gate_j = max(floor_abs_j, floor_cmp_j)` from the P2-015 calibration manifest row for this backend, gross energy, the block-window class and the scored-campaign condition family, issued and hashed before registration seals; a block window at or below it is refused (`below_floor`) and never counted. The floor never enters the interval; the anchor bound never gates a window. At block scale (thousands of joules per window against a floor of order 10 J) this gate is expected never to bind; it is a refusal check, not a claim margin. Whether AP-5M must also register an estimate-level floor check (`detection_floor.md` single-count discipline, `|estimate| > F`) on the J/correct difference is open item O-21 for Ed (E2); until adopted, claim acceptance is Holm plus zero-exclusion by the anchor-widened interval (S2). |
| MDE/n sizing + predeclared top-up rule | n per level ∈ {64, 128}, equal across levels, models and arms, chosen mechanically by K2 (c) and frozen before any test problem runs (D-062). No top-up. Planning intervals ×/÷ 1.59 at n = 64 and ×/÷ 1.39 at n = 128 (§2.3). |
| Denominator provenance requirement | Exact scorer output plus emitted-token and stop-reason audit. Observed count of correct attempts ≥ 3 per model per level; a level where either model has fewer than 3 merges in the fixed order of §2.4, else the group is `not estimable (sparse_after_merges)`. This is an observed count (a fixed property of the frozen problem set), not a confidence bound; for AP-5M it replaces AP-5's "binomial lower-bound" wording. |
| Sparse-level merge order *(added)* | K9 and §2.4. |
| Holdout cells (ladder rung L3 only) | not applicable. |
| Retry and overrun rules *(added)* | K13 (M12 as amended), K14–K16, K8, K22–K25. |
| Status vocabulary *(added)* | §3 in full. Ruled constants K19. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 on this frozen set, stack and caps. Forbidden: intelligence-per-joule; "difficulty causes energy"; any capability, ranking or routing claim; extrapolation beyond levels 1–5, these two models, or these caps. K20. |
| Disqualifiers + not-resolvable conditions | Below-floor blocks (refused, `below_floor`); a packing shortfall of the five-parent or five-envelope minimum (refused); `not estimable` after all merges; any interval containing 1, any `interval_disagrees`, `spread_exceeded` or `drift_exceeded` prints `not resolved`; a ceiling violation withholds L\* (S7, S8); an unattributed overrun or `night_exhausted` leaves its cell unresolved until the K22 recapture; a non-claim-ready roster is refused (K18); a failed smoke gate starts no campaign for that arm (K21); a problem with no counted attempt for either model is dropped from both and its level is NR (K24). |
| Linked manifests/bundle hashes | pending post-execution. |

### 2.9 Clauses referenced by the row

**K1 — problem set (ADAPTED from 19 §1 M1 and its addendum and from the merged importer; adopted as AP-5M text by
30/10 Q17).**
*Population.* `test.jsonl` plus the `test/`-tagged rows of `train.jsonl` at `openai/prm800k` commit `7ecc7947`:
5,001 rows. Excluded: both rows of the one duplicated id (2); references that are not a single rational number
(954); and references containing a plain comma (5). *Rational* means the reference, after removing TeX spacing,
dollar signs, a trailing degree or percent sign, a unit word and a leading "x =", parses as an integer, a decimal, a grouped integer (thousands separated by `{,}` or `,\!`, or by whitespace or a TeX space `\,`, `\;`, `\:`, `\ ` or `~`, all of which the importer removes or normalises before parsing), a/b, or `\frac{a}{b}`: `5`, `-\frac{3}{4}`, `0.25`, `10\%` and `1{,}000` qualify; `\sqrt{2}`, `3\pi` and `(1,2)` do not. A reference containing a bare comma, such as `1,000`, is a *plain-comma* reference and is excluded, because a bare comma could separate thousands or list two answers. Eligible: 5,001 − 2 − 954 − 5 = 4,040, by level 381/437, 733/894, 924/1130, 967/1214, 1035/1324 of the
non-duplicate rows (retention 0.872 at Level 1 falling to 0.782 at Level 5). Every eligible reference must equal the
parsed last boxed answer of its own worked solution, or the import refuses.
*Draw.* Each eligible problem gets a key = sha256 of a fixed domain string and the problem's content hash. Within a
level, problems are queued by subject (MATH's seven subject labels), each queue sorted by key; rounds take one
problem from each subject in turn, each round ordered by key ("balanced by subject" means this round-robin). The
pilot takes the first 16 per level under the pilot domain string; the test set takes the first n per level of the
remaining problems under a different domain string. The same problem ids serve both models and both arms. Source:
`joulewise/benchmark_import_math.py` (`eligible_records`, `select_pilot`, `select_items`; domain strings
`PILOT_DOMAIN` and `SELECTION_DOMAIN`) at `a53a6b97`, gated by the cold ruling of record 40, activation 1d3796d5.
Publication of problem text is Ed's decision E1 (O-20).

**K2 — sizing pilot: what it may set, and how n is chosen.** In the carries below, "problems per bundle" means the
block size.

> Caps, block size, envelope pitch, n per level (64 or 128, by a registered rule), and scorer additions (additions only, with a scorer-id bump). **Never** which levels are reported (D-062).

*Source: 19 §1 M5. VERBATIM.* The registered rule for n:

> **Fixed n and pilot.** A 16-problem sizing pilot, disjoint from test problems, never reported as a result, may set only
> (a) problems per bundle, (b) each arm's cap from a declared ladder, (c) n = 128 if the pilot-projected capture for
> the arm at 128 fits the registered window budget, else 64. It never sets which levels, models, arms, families or
> estimands are reported (D-062). All five levels are always reported.

*Source: C §3. VERBATIM.* ("16-problem" means 16 per level, 80 in all, per M4.) The "declared ladder" is a list of
candidate cap values, fixed in the registration packet. The "registered window budget" is a number of nights (the sources call a night a "capture window"; in this file "window" alone still means a block window); the value is fixed in the registration packet (O-14). O-14's list also carries `max_envelopes_per_night` and the per-(arm, level) `budget_j` and `max_gap`. Ed's decision E4 is whether that budget is
acceptable (O-18).

Extension of that list for this plan (30/21 A8, T-24; Ed adopts under E2):

For AP-5M the sizing pilot and shakedown also set `s_per_token_upper` and `prefill_s` (per model and arm), `ceiling_s`, δ_upper, every `budget_j` and every `max_gap` (K12, K21); none of them decides which levels, models, arms, families or estimands are reported (D-062). This extends C §3's list (a)–(c) for this plan and is part of what Ed adopts.

**K3 — caps, capped attempts, cap-bound.**

> Every attempt that hits the cap counts as incorrect, even when a boxed answer parses. The parsed text is kept for a sensitivity analysis.

*Source: 19 §1 M2. VERBATIM.* In the next carry, "disagreement refuses" means that a row whose `stop_reason`
disagrees with the token-count test is refused by the reducer.

> capped := generated_tokens ≥ Registration.cap_tokens[arm]; stop_reason required on every row; disagreement refuses.

*Source: 21/11 R9. VERBATIM.*

> A cell with more than 20 % capped attempts is labelled cap-bound. The cap per arm is the smaller of two values: the cap-ladder rung that covers the pilot's Level-5 1.7B 95th-percentile length, and B's physical ceiling (cap × s/token + prefill ≤ 450 s).

*Source: 19 §1 M3. VERBATIM.* ("B" is packet B, the scored-night design.)

> **Cap-bound label.** A cell with > 20 % truncated attempts is *cap-bound*. The label prints beside every number
> from that cell. If L\* rests on a cap-bound cell, the crossover sentence must state the cap ("at an N-token cap").

*Source: C §3. VERBATIM.*

**K4 — energy numerator.** "Peer number" below means a result reported as an equal alternative.

> Gross energy between the outer item edges of each block. Net-of-idle is never a peer number; the idle reference is a covariate.

*Source: 19 §1 M7. VERBATIM.* The idle reference (idle-slot energy per envelope, per model) is recorded and reported beside results per window; no computation in this plan adjusts any energy or R_L by it, and any exploratory use is labelled exploratory. (30/10 Q15.)

**K5 — J/token.** Descriptive only (19 §1 M10, VERBATIM "Descriptive only."). J/token and tokens/attempt are reported
beside J/correct and never carry a claim-bearing contrast (D-045.7: no token-normalized claim metrics).

**K6 — capture unit, idle slots, ordering.**

> An empty slot is captured as a full-length envelope with its model worker loaded and idle, and is labelled `kind: "idle_slot"` in the roster. It never enters any numerator (M7). It may be used as a covariate.

*Source: 08 F1. VERBATIM.*

> Drift cancels in a per-level ratio only when each model's measured blocks share the mean envelope index; `idle_slot` captured, never a numerator.

*Source: 21/10 §Q4 F1. VERBATIM.* Round-1 ruling 08 F1 made "equal mean envelope index per cell across the two
models" the packer's ordering invariant; gate 21 D5b (K12) later registered a tolerance. In plain words: equality is
what the packer aims for, and `lever ≤ max_gap` is what a roster must satisfy. 08 F1 also dropped packet C's rotated
level order and A-B-B-A model order as requirements ("The palindrome is kept only if the balance search wants it";
the *balance search* is the packer's search for an ordering that equalises positions).

> Idle collector plus a separate model worker; one thinking arm per night; the energy rail and floor identity must match Paper B's pins or the floors are re-measured.

*Source: 19 §1 M13. VERBATIM.* (The idle collector is the process recording power; the model worker is a separate
process running the model. Paper B is the project's earlier measurement paper; its pins are the powermetrics
boundary and rail manifest of §2.1 and its floors.)

**K7 — spread (M8).**

> Each cell is spread over at least 5 blocks in at least 5 distinct envelopes. The packer carries a no-two-blocks-of-a-cell-in-one-envelope constraint. Block membership is identical across the two models, and block size is set per arm, not per model.

*Source: 19 §1 M8. VERBATIM.* K8 fixes what "block" means once retries exist.

**K8 — M8 on retry tails.**

> M8 applies to parent blocks. A parent block is a block scheduled by the initial packing; single-problem blocks made from it under M12 are pieces of that parent, not new replicates. No two parent blocks of one cell share an envelope at any stage, initial or retry. Pieces of one parent may share an envelope with each other and with blocks of other cells of the same model, within capacity. The five-block and five-envelope minima count parent blocks and the distinct envelopes holding their executed windows; a split never adds to either count.

*Source: 45/10 §Q4. VERBATIM.*

**K9 — denominator guard, merge order, multiplicity.** The guard is T-1's observed count (at least 3 correct per model per level or group); AP-5M replaces AP-5's 'binomial lower-bound' wording (`analysis_plans.md:274`), subject to Ed's adoption under E2. The row's "Denominator
provenance requirement" (T-2) states the same rule. The AP-5 wording it replaces for this plan:

> Exact scorer output plus emitted-token/stop-reason audit; binomial lower-bound must be >=3 correct per level, else merge adjacent levels or report `not estimable`.

*Source: `docs/contracts/analysis_plans.md:274`, AP-5 "Denominator provenance requirement" field. VERBATIM; replaced
for AP-5M only.* The project's AP-5 design note already reads the guard as an observed count ("the >= 3-correct
binomial guard is a deterministic property of the item set", `docs/phase_2/suite_implementation_research.md:464`).
Packet C's text, now consistent with the ruled guard:

> **Minimum correct and merge order.** Each cell needs ≥ 3 correct (AP-5 guard; an observed count, a deterministic
> property of the set). If either model fails at a level in an arm, that level merges for both models, in that arm only,
> in this fixed order: 5 into 4 ("4–5"), then into 3; 1 into 2 ("1–2"), then into 3. Merges depend only on correct
> counts, never on energy or R. If no valid merge remains, the result is `not estimable`.

*Source: C §3. VERBATIM.* The merge order itself is S2's `merge` (§2.4).

**K10 — bootstrap draw (ADAPTED; adopted as registration text by 30/10 Q4).** B = 20,000 replicates, seed fixed in
the registration packet (packet C §3). In each replicate, within each level of the group, draw as many parent blocks
as the level has, with replacement, using the same draw for both models; within each drawn parent, draw as many
problems as it holds, with replacement, using the same positions for both models. A drawn problem contributes its
model's correct flag and tokens; a drawn parent contributes its gross energy g times the model's own drawn-token
share s (the drawn problems' generated tokens ÷ the parent's generated tokens for that model; equal shares if the
parent generated zero tokens). In the next sentences, `randrange` is Python's uniform whole-number draw, and
Hyndman–Fan type 7 is a named percentile rule (the one numpy uses by default). Replicates use Python's `random.Random(seed)` with the seed fixed in the registration packet; each draw is `randrange`, in the order parent then problem. Percentiles are Hyndman–Fan type 7 (h = (B − 1)·p on the 0-based sorted values; numpy's default). An undefined replicate (both models' draws zero correct) is never dropped: it sorts below every finite value on the low side and above every finite value on the high side; an end that interpolates with an infinite value is that infinity. All of this is registered so the interval can be rebuilt exactly.

> Bootstrap over paired problems **and** over capture blocks (block-aware), widened by the instrument's floor and anchor bounds. Holm is applied in two families of m = 5 (thinking-on primary; thinking-off secondary and unable to carry the headline). The crossover level L\* is defined only on Holm-significant directions.

*Source: 19 §1 M9. VERBATIM.* (As to "widened by the instrument's floor and anchor bounds": superseded by T-4/T-5; the floor gates windows, only the anchor bound widens.)

**K11 — anchor bound and interval.** Gate 21's text, whose bracket 30/10 Q3 replaces (`:60-65` names the share
computation in the draft estimator, which K10 gives in words):

> per replicate, per drawn block and model, `u = k·(floor_j + anchor_j)·s`, with `k` the block's measured windows for that model and `s` the drawn-token share used at `:60-65`; point bounds keep `s = 1`.

*Source: 21/10 §Q2 D5a. VERBATIM; bracket superseded.* The operative text (T-5 as superseded by 30/21 A10):

u = s · Σ_w anchor_{j,w}, summed over the parent's counted windows w for that model, where anchor_{j,w} is window w's reducer field `energy_bound_terms_j.E_clock_anchor_shift_bound_j`; a counted window without a bounded value is refused (`anchor_energy_envelope_unrecorded`). Point bounds use s = 1. This departs from gate 21 D5a's bracket `k·(floor_j + anchor_j)` because D-078 clause 11 and `detection_floor.md` assign the floor to a separate gate and record the anchor bound per window; D5a's per-replicate share-scaled structure is kept.

In the next carry, E₈ and E₁.₇ are each model's replicate energy and U₈, U₁.₇ its summed bound (now the sum, over
drawn parents, of s · Σ_w anchor_{j,w}).

> U_m = Σ u. Low bound R(E₈ − U₈, E₁.₇ + U₁.₇), high R(E₈ + U₈, E₁.₇ − U₁.₇); point bounds use s = 1.

*Source: 20 §Q5(a), adopted by 21/10 D5a. VERBATIM.* The interval rule:

> (6) The reported interval runs
> from the 2.5th percentile of the low-side values to the 97.5th percentile of the high-side values.

*Source: C §3, step 6. VERBATIM.* Point bounds are reported beside the interval and do not alter it (30/10 Q4, T-7).

**K12 — drift lever and threshold.**

> The drift lever of a level is the absolute difference, in envelope slots, between the mean position of its 8B parents and the mean position of its 1.7B parents. A parent's position is the item-weighted mean of the envelope indices of its executed windows: each item contributes the index of the envelope in which its counted attempt was captured. Voided attempts and idle slots contribute nothing. At pack time every item of a parent sits in one envelope, so its position is that envelope's index.

*Source: 45/10 §Q4. VERBATIM.* In the next carry, `requeue_overrun` is the packer function that applies K13 after an
overrun.

> register `δ_upper` in joules per block per slot and `budget_j` as the per-cell absolute bias budget with its derivation; `max_gap` follows. `requeue_overrun` recomputes `drift_lever_slots`.

*Source: 21/10 §Q2 D5b. VERBATIM.* The registered derivation (30/10 Q7, as superseded by 30/21 A2, A3, A9; T-10):

The *drift threshold* is `max_gap = budget_j / (δ_upper · P)`, registered per (arm, level), with P the number of parent blocks per cell per model (the registered n ÷ problems per block). `δ_upper` (joules per block per slot) is registered per arm from that arm's shakedown night: each model runs one fixed block of pilot problems twice, in its first and last envelopes of that night; for each model compute `(|E_last − E_first| + floor_gate_j) ÷ (slot separation)` with the block-window `floor_gate_j` of T-6, and δ_upper is the larger of the two models' values; a shakedown lacking either pair refuses registration. `budget_j` for (arm, level) is 0.01 × the smaller of the two models' projected energies for that cell at the registered n, where a model's projection is its mean pilot generated tokens per problem at that level × n × its shakedown seconds per token × its mean shakedown power; so the admitted bias moves that level's R_L by at most about one percent. δ_upper, every `budget_j` and every `max_gap` are hashed in the registration packet before any test problem runs.

> If the executed roster's gap exceeds max for a level, that level's status is NR(`drift_exceeded`) pending a balanced recapture.

*Source: 21/11 R11. VERBATIM.* The "balanced recapture" is the K22 recapture. The drift model behind the threshold
is T-12 (§2.1).

**K13 — overruns and retries (M12 as amended).** Lead-in glossary for the carries: a *pure module* is a program
component that only computes outputs from inputs; `_seal` is the packer's single validating exit; the *runner lane*
is the work item building the night runner; "Opus B2/S5/S6" and "(Sol)" are finding identifiers from the round-1
reviews.

> A block that overruns is re-queued once within the night. It is then re-queued as single-problem envelopes, never dropped.

*Source: 19 §1 M12. VERBATIM; amended by 08, 21/10 §Q4, 45/21 §7 below and K23 ("within the night" is kept: fresh
envelopes extend the same night).*

> After a second overrun, the items become single-problem BLOCKS, packed several per envelope, each with its own item edges. They are packed by the item's cap-bounded worst case (cap tokens × upper s/token + prefill; the pure module takes that worst-case seconds as an input), never by the prediction that already failed.

*Source: 08, "M12 amendment". VERBATIM.*

> the worst-case seconds input is derived in Registration (`cap × s_per_token_upper + prefill`) and asserted ≥ the failed prediction, and the AP-5M text carries the amended M12 wording so registration and code do not diverge.

*Source: 21/10 §Q4, M12 amendment condition. VERBATIM.*

> "`requeue_overrun` at the initial and whole-block stages takes, for every block in the reporting envelope, an observation: `completed` with elapsed seconds, `cut_off` with elapsed seconds, or `not_started`; the envelope records every observation. A completed block keeps its window; if its elapsed exceeds its `predicted_s` it is marked `late: true` and is a culprit. An uncompleted block whose elapsed exceeds its `predicted_s` is a culprit and advances one stage. An uncompleted or not-started non-culprit is rescheduled at its current stage without advancing, provided the envelope holds a culprit. If it holds none, every uncompleted or not-started block becomes the typed terminal state `unattributed_overrun` (a `terminal_refusals` entry; its cell is unresolved until a registered recapture); the call never raises for innocence. The whole-block retry is scheduled alone in a fresh envelope with `reserved_s = min(Σ item derived worst cases, capacity)`; `predicted_s` is unchanged."

*Source: 45/21 §7 (W). VERBATIM.*

> "A whole-block retry advances to the split stage when its attempt did not complete within its envelope; its observed elapsed is recorded. Each single is packed at `reserved_s = predicted_s = the item's derived worst case`."

*Source: 45/21 §7 (T). VERBATIM.*

> "At the single stages the observation per single is `completed`, `cut_off` or `not_started`, with elapsed where applicable. A single whose elapsed exceeds its derived worst case advances (`single_problem` → `single_retry` → `ceiling_violation`). Any other uncompleted or not-started single is rescheduled without advancing, into the first later envelope satisfying M8-by-parent and capacity, else a fresh one. Each innocent reschedule is caused by one culprit event in its envelope and each item has at most two culprit events, so the total is at most 2 × (number of singles); the seal refuses a roster exceeding it."

*Source: 45/21 §7 (N). VERBATIM.*

> "An envelope with no active block is legal iff its `kind` is `idle_slot` or its `voided_block_ids` is non-empty; `_seal` refuses any other empty envelope. An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's. The split stage never reuses the whole-block retry's envelope."

*Source: 45/21 §7 (E). VERBATIM.*

> `unattributed_overrun` is unreachable under correct instrumentation (Σ elapsed ≤ Σ predicted ≤ capacity); it is a fault signal the runner lane must surface, not a retry path.

*Source: 45/21 §8 NIT N1. VERBATIM.*

> runner lane, as the per-attempt kill timeout; registration keeps the inequality derived worst case ≤ `ceiling_s` ≤ capacity

*Source: 45/10 §Q2, CARRIED row for `ceiling_s`. VERBATIM.*

Round-1 conditions that still stand ("pairwise excluding" below removes a retried item for both models):

> (a) Pairing survives a split: singles carry `parent_block_id`, and the estimator pairs on the parent (Opus B2).
> (b) `retry_stage` is on every item row and flows into cells (Opus S6).
> (c) The single-problem stage is terminal: one single-problem retry, then the item is flagged `ceiling_violation`, a typed refusal for that item, recorded and never silently dropped (Opus S5).
> (d) The paired drop-retried sensitivity analysis is pre-registered, and it is labelled selection-confounded because it removes exactly the long items (Opus). If including versus pairwise excluding retried blocks changes any Holm direction or L\*, that claim is reported unresolved until a balanced recapture (Sol).

*Source: 08 F2 (a)–(d), affirmed by 21/10 §Q4. VERBATIM.* The 10 %-retried trigger 08 F2(d) left to this plan is not
adopted (30/10 Q12, §6 O-8).

**K14 — ceiling violation.** Carried in §3 as S7 (status) and S8 (recapture bound and failed check); worked in §2.6
panel 2.

**K15 — spread_exceeded (ADAPTED by ruled substitution).**

> A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them, for any reason after capture (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place). The cell carries `spread_exceeded: true`, its numbers are reported, and its level is not resolved (`spread_exceeded`) until a registered recapture. Before capture the same shortfall is a packing refusal.

*Source: 45/10 §Q4 "spread_exceeded", with its clause replaced as 45/21 §7 (X) orders. Each part VERBATIM; §6 A3.*
In a merged group the flag makes the whole group NR (§2.1, T-9).

**K16 — precedence.** (A281b is the estimator work item, now A293.)

> "When a level carries both NE(`ceiling_violation`) for a group and `spread_exceeded`, NE(`ceiling_violation`) takes precedence in the A281b total table and `spread_exceeded: true` is recorded alongside; a level with `spread_exceeded` and no NE is NR(`spread_exceeded`)."

*Source: 45/21 §7 (P). VERBATIM.* The full precedence (30/10 Q7 (d) as superseded by 30/21 A5; T-11):

12. **Group status** by the three-way test (S2); then flags, in this precedence: NE(`ceiling_violation`) first; otherwise NR listing every applicable reason in the order `spread_exceeded`, `drift_exceeded`, `unattributed_overrun`, `night_exhausted`, `below_floor`; every applicable flag is recorded true whatever the printed status.

Flagged constituents of a merged group (30/21, T-28): A constituent of an estimable merged group that carries a flag keeps level status `p` + `pooled_in`; the flag is recorded true on that level and the group is NR with `flagged_levels` (T-9).

**K17 — terminal-attempt windows.**

> A window for a terminal ceiling_violation attempt is accepted, recorded on the terminal refusal as `gross_j`, and never enters a cell sum.

*Source: 45/10 §Q5 F3. VERBATIM.*

**K18 — pilot rosters.** `mode = pilot` marks a registration used only for the sizing pilot; a consumer is any
program reading the roster (reducer, estimator or night runner).

> `mode = pilot` objects may emit only rosters flagged `claim_ready: false`; every consumer refuses a non-claim-ready roster outside pilot mode.

*Source: 21/10 §Q2 D4. VERBATIM.*

**K19 — ruled constants.** Levels [1, 2, 3, 4, 5]; merge order per S2 `merge`; denominator guard ≥ 3 correct per model per level or group (T-1, observed count); Holm m = 5 per family; α = 0.05 two-sided; minimum parent blocks per cell
5; minimum envelopes per cell 5; cap-bound fraction 0.20; retry stages `initial`, `whole_block`, `single_problem`,
`single_retry`, `ceiling_violation`; B = 20,000; budget fraction 0.01 (K12). `schema` is the registration's version
identifier.

> Module constants pinned by `schema`; one test asserts equality to the AP-5M text.

*Source: 45/10 §Q3, constants row. VERBATIM.* This clause is the text such a test compares against.

**K20 — forbidden upgrades, exclusions and claim language.** The AP-5 prohibitions carry over through §4 ruling (2);
rung L2 of the claims ladder forbids "extrapolated crossover" in any case. In the list below, the "residual fit" E =
fixed + a·p + b·d models energy E from p prompt tokens and d decoded tokens; "affine-ladder rules" are AP-5's rules
for its synthetic workload.

> Capability or leaderboard claims; rankings beyond this pair and set; routing policies; other caps, quantizations,
> devices or benchmarks; per-problem energy; confirmatory J/token or tokens/attempt contrasts; mechanism claims from the
> residual fit E = fixed + a·p + b·d (exploratory unless registered); thinking-off results as headline; pilot outcomes;
> any change to AP-5's affine-ladder rules.

*Source: C §5. VERBATIM.* Example sentences:

| Allowed | Banned |
|---|---|
| Per-level R_L with interval, cap and set named. *"On our frozen MATH Level 5 problems (thinking on, 8,192-token cap), Qwen3-8B used 0.6× [0.4, 0.9] the joules per correct answer of Qwen3-1.7B."* | Causal difficulty. *"Harder problems make the model draw more energy."* |
| Decomposition. *"Of the Level-5 gap, the token ratio contributes X and the accuracy ratio Y."* | Intelligence per joule or capability. *"The 8B delivers more intelligence per joule"*; *"the 8B solves 62 % of Level-5 MATH."* |
| Crossover within tested levels. *"The cheaper model per correct answer changed from 1.7B to 8B at MATH Level 4 on this set."* | Routing or general advice. *"Route hard prompts to bigger models to save energy."* |
| Null. *"No crossover within levels 1–5."* | Extrapolated crossover. *"Beyond Level 5 the 8B wins by more."* |

*Source: C §4. VERBATIM.* These are shapes only; the exact sentence for any pattern is fixed by §3, which prevails.

**K21.** In the text below (T-3), "AP-5's E5" names the fifth check of AP-5's smoke design (early-stop bias), not
one of Ed's questions; AP-5's defined checks are listed in the corrected gate inputs of
`docs/phase_2/suite_implementation_research.md` §3 (the D-047 correction). Ruled by 30/10 Q2.

**K21 — pre-campaign smoke gate.** AP-5 requires an envelope-validation smoke gate that passes before any scored campaign (`analysis_plans.md:270`). AP-5's defined checks were written for a ladder whose prompts differ by one digit; for MATH, emitted-token mean and distribution and prompt-token count change with level by design, so those checks are not pass conditions here. The AP-5M smoke gate is one shakedown night per arm (M4, M13); each arm's scored campaign waits for its own pass. An arm's gate PASSES only when all of the following hold on every envelope of its shakedown night: (G1) every bundle is strict-valid; (G2) every attempt's `stop_reason` is `eos` (end-of-sequence token) or `length` (cap), `capped := generated_tokens ≥ cap_tokens[arm]` agrees with `stop_reason` on every row, and no attempt ends by runtime error, by kill at `ceiling_s`, or with a missing or unrecognised `stop_reason`; a malformed answer is an outcome (K3), counted incorrect, and does not fail the gate; (G3) every completed block's markers lie inside its envelope's usable interior, and no block's elapsed seconds exceed the sum, over its problems, of `cap_tokens[arm] × s_per_token_upper + prefill_s`. Reported per (model, level) with no pass threshold: emitted-token mean and distribution, prompt-token count, cap-hit fraction beside the registered `cap_bound_fraction` (0.20), and the early-stop-bias descriptor (mean emitted tokens of incorrect minus correct attempts; AP-5's E5). A failed gate records `smoke_failed([reasons])`; no scored campaign starts for that arm; the cause is cured and recorded and that arm's shakedown repeated; no registered value beyond those K2 as extended (T-24) lets the pilot and shakedown set changes on its account. A G3 failure falsifies `s_per_token_upper` for that arm; it is re-derived before any repeat.

**K22 to K25.** K22 is the flag recapture bound (T-9, second part; ruled 30/10 Q6, superseded by 30/21 A4). A
recapture night runs under a new roster linked to the old one by `recapture_of`:

**K22 — flag recapture bound.** For each (arm, level) at most one registered recapture may cure `spread_exceeded`, `drift_exceeded`, `unattributed_overrun` or `night_exhausted`, all causes together. It runs on a later census-clean night as a new roster linked by `recapture_of`: for every *affected* parent, both models' copies are re-run with the same problems, packed to lever 0 within that night; the recaptured copies supersede both models' earlier windows of that parent. A parent is affected when it is missing a counted window for either model, or (for `drift_exceeded`) when it holds a retried or rescheduled window. If the level still carries any of these flags afterwards, it is NR terminal under this registration. This bound is separate from S8's one recapture of a ceiling-violating problem.

K23 is the rule for retries across the night (T-13; ruled 30/10 Q9, superseded by 30/21 A4), also given in §2.1
"Nights and retries"; `recapture_unpaired` is the defect name for a night holding one model's windows only:

Retries and reschedules extend the same night: a "fresh envelope" is appended to that night's schedule up to the registered `max_envelopes_per_night`. Any block unfinished when the night ends is the terminal refusal `night_exhausted` (a `terminal_refusals` entry); its cell is unresolved until the K22 recapture. Envelope indices start at 0 in every night, including a recapture night. A level's drift lever is computed within each night over that night's counted windows of both models, and the level's lever is the largest of its nights' levers; a night holding counted windows of only one model for a level has no lever and is a K22 defect (`recapture_unpaired`).

**K24** is the counted-attempt rule (T-14, 30/21 A6), given in §2.1 "Counted attempt (K24)".

**K25** records an amendment the code needs (T-26, 30/21 A13). Lead-in glossary: 45/21 §7 is the packer ruling's list
of final texts; its part (G) is the closed list of allowed retry-stage transitions ("edges"), part (E) the rule placing
every retry at a higher envelope index, and part (S) the checks `_seal` (the packer's single validating exit) runs,
including *item conservation* (every problem sits in exactly one live block).

**K25 — required amendment to 45/21 §7 for the code lane.** (G)'s closed edge list adds: any non-terminal stage → `night_exhausted` (terminal); and, for a parent affected under K22 or an item under S8, terminal-or-flagged → `recapture`. A recapture is a new roster sealed under the same registration, linked by `recapture_of` (the superseded roster's `sha256`), with envelope indices from 0; (E)'s "index above the reporting envelope's" applies within a night; (S)'s item conservation treats a recaptured item as superseding its earlier block and windows. `max_envelopes_per_night` is a registration field, hashed with the others. Until the code lane's gate ratifies this text, `_seal` refuses these paths and no K22 or S8 recapture roster can be produced.

### 2.10 Change log

**Version 4 vs version 3 (installing 30/21):**

- **Superseded texts replaced byte for byte:** T-3 (one shakedown night per arm; G2 names `eos` and `length` and
  treats a malformed answer as an outcome; G3 sums worst cases over a block's problems), T-5 (anchor bound recorded
  per window, Σ_w anchor_{j,w}, and `k` removed; the §2.3 and §2.5 examples relabelled to Σ_w anchor_{j,w} = 2 J with
  version 2's numbers restored, as T-5 directs), T-7 (draw order, Hyndman–Fan type 7 percentiles, undefined
  replicates), T-8 and T-11 (all six flags leave the Holm sort; the precedence lists five NR reasons), T-9 (K22 as a
  linked recapture roster of affected parents), T-10 (δ_upper per arm with a floor allowance and the larger of the two
  models' values; `budget_j` and `max_gap` per arm and level), T-12 (one intercept per night), T-13
  (`max_envelopes_per_night`, `recapture_unpaired`), T-14 (at most one counted attempt; dropped pairs), T-15 (the
  falsified-bound flag set at the first violation), T-20 (budget counted in nights, plus one shakedown night per
  arm), T-21 (every grouping form the importer accepts).
- **Amended:** T-4 (the `floor_cmp_j` formula) and T-6 (the floor gate is expected never to bind; new O-21).
- **New:** T-24 (K2 extension), T-25 (guard lead-ins), T-26 (clause K25), T-27 (note on M9's "floor and anchor"),
  T-28 (flagged pooled constituents).
- **T-25's change-log instruction, installed:** C's observed count guard is operative (K9, T-1). Version 3 already
  contained neither of the two phrases T-25 deletes (from K9, step 6 and the version-2 change list); nothing else to
  remove.
- **Other:** a plain-language summary for Ed at the top; O-21 added to Ed's items; §5 map rebuilt over T-1 to T-28;
  §6–§9 updated; the §2.6 drift example recomputed with K12's per-level budget (235.5 J); the refuter-pending note
  removed from §8.

**Version 3 vs version 2 (carried from version 3):**


- **Installed from 30/10 (T-1 to T-23):** observed-count guard replacing AP-5's wording for this plan (T-1, T-2);
  smoke gate with pass predicates G1–G3 (T-3); floor as a separate per-window gate and anchor bound alone in the
  interval, `floor_j` removed (T-4, T-5, T-6); percentile-only interval with point bounds reported beside, RNG and
  quantile rule registered (T-7); flag-forced NR levels out of the Holm sort (T-8); whole-group NR for flags and one
  flag recapture per (arm, level) (T-9); drift threshold with registered δ_upper and budget_j (T-10); flag precedence
  (T-11); explicit linear drift model (T-12); retries extend the same night, `night_exhausted`, per-night levers (T-13);
  counted attempt (T-14); failed recapture check terminal (T-15); 10 % trigger omitted (T-16); operative reasons for
  withholding L\* (T-17); ruled claim sentence with NE reason codes (T-18); idle reference report-only (T-19);
  capture-window budget unit (T-20); grouped-integer forms (T-21); scorer canonicalisation (T-22); interval energy by
  power × overlap (T-23).
- **Closed:** open items O-1 to O-16 (§7), each citing its ruling question.
- **Writing fixes (charge Appendix A, record 18):** guard built in Terms (N12); floor statistics named instead of
  "spread" (N9); "spread" now has one meaning; smoke checks no longer called E1–E4, and "E1–E4" given one meaning
  (§1); interior, offset and guard margin built (N6); "arm time", `codex|claude|t3`, adapter, reducer, balanced
  recapture, three-way test, council log, "problems per bundle" and "balance search" glossed at first use (N2, N4,
  N7, N8, N13–N15, N20, N21); replicate "slots" renamed "draws" (N18); references to review-finding codes B1/B2/M6
  removed (N22, N24); "rung L2 outside carried text" (record 18 F6 NIT); panel-2 note on why envelope 23 (record 18
  F11); the grouped-integer contradiction removed (N19); drift linearity stated (N11); decoding (greedy vs seeded
  sampling) built before T-14 uses it.
- **Removed as superseded:** v2's "binomial lower-bound operative" position; v2's K21 proposal; the `floor_j + anchor_j`
  bracket; v2's O-items texts; v2's "PROPOSED" label on the claim template.

## 3. Decision-pattern table and status rules

This section decides, for each arm, which groups are 8B cheaper, 1.7B cheaper, not resolved or not estimable,
which pattern the family shows, and whether L\* may be claimed. The adopted vocabulary and procedure are record
20's (21/10 §Q1: "AMEND D2 (adopt, with rulings below)"; D2 was the gate-21 charge's name for this adoption),
amended by the gate-21 cures, the gate-21 refuter's wording and 30/10. Every rule is carried; this seat adds the
ordering and reading notes.

**S0 — pattern names, in words (from S2 `classify`).** Read the statuses of resolved groups (E8, E1) in level order,
ignoring NR and NE. `crossover`: one or more 1.7B-cheaper groups, then one or more 8B-cheaper groups, one change.
`reverse_order`: 8B-cheaper groups then 1.7B-cheaper groups, one change. `non_monotone`: two or more changes.
`all_1.7B` / `all_8B`: every group resolved and all the same direction. `one_signed_1.7B` / `one_signed_8B`: all
resolved groups the same direction, but some groups unresolved or not estimable. `none_resolved`: no resolved group
and not all NE. `none_estimable`: every group NE. The L\* absent reasons name why no L\* is reported.

**S1 — vocabulary.**

> Group status: `8B cheaper` (E8), `1.7B cheaper` (E1), `not resolved` (NR), `not estimable` (NE, reason `sparse_after_merges` or `ceiling_violation`). Level status: the group status if alone, else `pooled` with `pooled_in`. Pattern: `crossover`, `reverse_order`, `non_monotone`, `all_1.7B`, `all_8B`, `one_signed_1.7B`, `one_signed_8B`, `none_resolved`, `none_estimable`. L\* absent reasons: `boundary_group_pooled`, `reverse_order_not_registered`, `non_monotone`, `no_8B_cheaper_group`, `no_1.7B_cheaper_group`, `none_resolved`, `none_estimable`.

*Source: 20 §Q2, adopted by 21/10 §Q1. VERBATIM.* S9 amends "else `pooled`" for constituents of a not-estimable
group; S7 adds `ceiling_violation_unresolved`; K12, K15, K22, K23, K24 and T-6 add `drift_exceeded`, `spread_exceeded`,
`night_exhausted`, `unattributed_overrun` and `below_floor` as NR reasons and terminal states.

**S2 — the three-way direction test.**

> The status rule is: Holm rejects, the direction by p, and the interval lies wholly on that side; otherwise NR with an `interval_disagrees` flag.

*Source: 21/00, lead disposition D2. VERBATIM; affirmed by the next quote.*

> Packet C's terms paragraph ("interval wholly below 1") and §3 ("Holm rejects and p_below < p_above") plus M9 ("only on Holm-significant directions") are satisfied together only by the conjunction; a Holm rejection whose widened interval straddles 1 is NR with `interval_disagrees`.

*Source: 21/10 §Q1, "Status rule (three-way conjunction): AFFIRM". VERBATIM.*

Operational form (record 20 §Q2 pseudocode, adopted with D2; VERBATIM). Reading notes: `c8`, `c17` are per-level
correct counts; `join` merges groups; in `holm`, `rank` counts from 0, so the first comparison is against α/5, and
"tested groups" excludes NE and flag-forced NR groups (§2.2 step 10); `lo`, `hi` are the interval's ends; the `< 3` in
`sparse` is the observed-count guard of §2.1; the `gap_levels` line is amended by S6.

```
merge(c8, c17):                        # correct counts per level; nothing else
  groups = {1},{2},{3},{4},{5}; sparse(g) = min(Σc8[g], Σc17[g]) < 3
  if sparse{4} or sparse{5}: join(5,4); if sparse(group(5)): join(group(5),3)
  if sparse{1} or sparse{2}: join(1,2); if sparse(group(1)): join(group(1), group(3))
  NE = {g : sparse(g)}                 # e.g. {3} alone, 345, 123, 12345
holm(p over tested groups, m=5 fixed): sort ascending; reject while p ≤ α/(5−rank); stop at first failure
status(g): NE if g∈NE; else if not rejected or p_below==p_above: NR
           else E8 if p_below<p_above and hi<1; E1 if p_above<p_below and lo>1
           else NR + flag interval_disagrees
classify(groups in level order):
  seq = statuses of E8/E1 groups in level order; changes = #adjacent differences
  seq empty          → none_estimable if all NE else none_resolved
  changes == 0       → all_X if every group resolved else one_signed_X
  changes ≥ 2        → non_monotone
  seq[0] == E8       → reverse_order
  else (E1…E1 E8…E8) → crossover: boundary = first E8 group, licensing = last E1 group,
                       gap_levels = levels strictly between (NR/NE)
                       L* = boundary's level if single, else None, reason boundary_group_pooled
                       (crossover_group still reported)
```

**S3 — pooled licensing, boundary rule.**

> A merged group may license L\* only as a region statement. When the licensing group is pooled, the crossover sentence reads: 'The cheaper model per correct answer changed from 1.7B on pooled Levels 1–2 to 8B at Level 3 on this set.' The output carries `licensing_group` (list of levels) and `licensing_pooled: true|false`. The boundary group must always be a single level.

*Source: 21/10 §Q1, Split 1 cure text. VERBATIM.*

**S4 — reverse order and non-monotone patterns.** In the pattern `8+1+` below, `8+` means one or more 8s and `1+`
one or more 1s, with `n` and `e` letters ignored.

> Pattern `reverse_order`, reason `reverse_order_not_registered`, no L\*, per-level results printed.

*Source: 21/10 §Q1, Split 2. VERBATIM.*

> (b) `reverse_order` is any resolved sequence matching `8+1+` with zero further changes; `88111` qualifies, `8n111` too.

*Source: 21/10 §Q1, amendment (b). VERBATIM.*

> NIT: non_monotone rows need the reason code `non_monotone`.

*Source: 21/11 R5. VERBATIM.*

**S5 — sparse Level 3.**

> **Isolated sparse Level 3: AFFIRM** NE(`sparse_after_merges`); registration text for A282.

*Source: 21/10 §Q1. VERBATIM.* An isolated sparse Level 3 has no merge target and stays not estimable.

**S6 — gap levels and the claim sentence.**

> (a) `gap_levels` must list every NR/NE level in the family, not only those strictly between licensing and boundary; the claim sentence names them.

*Source: 21/10 §Q1, amendment (a). VERBATIM.*

> If any level lies strictly between the licensing group and the boundary level, the sentence reads 'changed from 1.7B (Level a) to 8B between Levels a and L\*; Levels … not resolved'; L\* is reported as the first level with a resolved 8B-cheaper result.

*Source: 21/11 R4 cure. VERBATIM.*

> NIT: keep `bracket_gap_levels` separate.

*Source: 21/11 R4. VERBATIM.*

**Combined sentence (ruled, 30/10 Q14 and T-18).** Template, with every part optional except the first:

"On this frozen MATH set (arm, cap), the cheaper model per correct answer changed from 1.7B **[at Level a | on
pooled Levels a–b]** to 8B **[at Level L\* | between Levels b and L\*]**; **[Level(s) … not resolved]**; **[Level(s)
… not estimable (reason)]**."

Rules: use "at Level L\*" when no bracket gap exists, else "between Levels b and L\*" with b the highest level of the
licensing group; list every gap level (bracket and outside), NR levels under "not resolved" and NE levels under "not estimable" followed by the reason code in parentheses, e.g. "Level 3 not estimable (sparse_after_merges)". A pooled boundary group gives no L\* (S3). Examples: `1nn8n` → "changed from 1.7B at Level 1 to 8B
between Levels 1 and 4; Levels 2, 3 and 5 not resolved." `12|3|4|5` with `1n88` (levels `ppn88`) → "changed from 1.7B
on pooled Levels 1–2 to 8B between Levels 2 and 4; Level 3 not resolved." `11e88` → "changed from 1.7B at Level 2 to
8B between Levels 2 and 4; Level 3 not estimable (sparse_after_merges)."

**S7 — ceiling-violation null.**

> When any item in the family carries a terminal `ceiling_violation`, its group is NE(`ceiling_violation`), every other group is classified and printed, and `crossover_level` is null with reason `ceiling_violation_unresolved` until a registered recapture resolves the item. Pairwise exclusion of the item appears only in the labelled selection-confounded sensitivity.

*Source: 21/10 §Q1, Split 3 cure text. VERBATIM.* AP-5M records two reasons for withholding L\*: (i) the censored outcome leaves the count-only merge partition undetermined; (ii) the violation falsifies the registered bound `s_per_token_upper`, a physics/evidence refusal (21/11 R6). The gate-21 sentence "a gap there is the selection M12 forbids" is preserved as the historical statement; it is not the operative reason, because the ruled table lets count-based NE gaps license L\*.

**S8 — ceiling-violation recapture bound and failed check.** In the carry, "census-clean window" means a
census-clean night, and "copies" are the same problem run by each model.

> At most one recapture, on a later census-clean window, both models' copies adjacent as singles; the night's other blocks for that arm are checked against s_per_token_upper; a second violation makes `ceiling_violation_unresolved` terminal for the family under this registration.

*Source: 21/11 R6 cure. VERBATIM.* Worked in §2.6 panel 2. The falsified-bound rule (30/10 Q11, superseded by 30/21 A7):

The first ceiling violation sets `s_per_token_upper_falsified: true` for the arm. S8's single recapture is the only run allowed under it. If, during that recapture, the recaptured single or any other block of the night for that arm exceeds `s_per_token_upper`, `crossover_level` stays null with reason `ceiling_violation_unresolved`, terminal under this registration; the arm's results still print with the flag; a further recapture requires a new registration.

**S9 — constituents of merged groups.**

> Constituents of an estimable merged group get `pooled` + `pooled_in`. Constituents of an NE merged group get `not estimable` + `pooled_in` + the NE reason.

*Source: 21/11 R7. VERBATIM.* Flagged constituents (30/21, T-28): A constituent of an estimable merged group that carries a flag keeps level status `p` + `pooled_in`; the flag is recorded true on that level and the group is NR with `flagged_levels` (T-9).

**S10 — null sentences.**

> **Null wording.** All levels above 1: "On this frozen MATH subset and stack, Qwen3-1.7B spent fewer joules per correct
> answer than Qwen3-8B at every level 1–5; no crossover within the tested levels." All below 1: the mirror. Non-monotone:
> per-level results, no crossover claimed.

*Source: C §3. VERBATIM.*

> When any group is pooled, the null sentence reads 'at every level or pooled level group (Levels 4–5 pooled)'; the mirror for 8B.

*Source: 21/11 R3 cure. VERBATIM.*

**S11 — authoritative worked-pattern table.** How to read it: in the first column, `|` separates groups and digits
written together form one merged group (`45` = Levels 4 and 5 merged); the letters after the partition are group
statuses in level order; the second column gives level statuses 1→5. A row with no partition written is the
all-singleton partition 1|2|3|4|5. "(Sol …)" gives the same row in the Sol consult's notation (`level:status`,
brackets for a merged range); "code" notes record what the ungated draft estimator did and are not rules.

Statuses per level 1→5: `8` 8B cheaper, `1` 1.7B cheaper, `n` not resolved, `e` not estimable, `p` pooled (with `pooled_in`). Brackets = merged group. "code" = probe at d2f9a273 where it differs.

| Partition / group statuses | Level statuses | Pattern | L\* or reason |
|---|---|---|---|
| 1\|2\|3\|4\|5 `1n888` | `1n888` | crossover | **3**, gap 2 |
| `88111` | `88111` | reverse_order | none, `reverse_order_not_registered` |
| `81888` | `81888` | non_monotone | none (code: 3) |
| `18188` | `18188` | non_monotone | none (code: 2) |
| `1n8n1` | `1n8n1` | non_monotone | none (code: 3) |
| `1nn8n` | `1nn8n` | crossover | **4**, gaps 2,3,5 |
| `n1n8n` | `n1n8n` | crossover | **4**, licensing 2, gaps 1,3,5 |
| `11188` | `11188` | crossover | **4** |
| `11n88` | `11n88` | crossover | **4**, gap 3 |
| `11111` | `11111` | all_1.7B | none, `no_8B_cheaper_group` |
| `88888` | `88888` | all_8B | none, `no_1.7B_cheaper_group` |
| `111n1` | `111n1` | one_signed_1.7B | none, `no_8B_cheaper_group` |
| `n8888` | `n8888` | one_signed_8B | none, `no_1.7B_cheaper_group` |
| `nnnnn` | `nnnnn` | none_resolved | none, `none_resolved` |
| 1\|2\|3\|4\|5, L3 sparse `11e88` | `11e88` | crossover | **4**, licensing 2, gap 3 (NE) |
| 1\|2\|3\|45 `1118` | `111pp` | crossover | none, `boundary_group_pooled`; crossover_group 4–5 |
| 1\|2\|3\|45 `1111` | `111pp` | all_1.7B | none, `no_8B_cheaper_group` (code: false `boundary_in_merged_group`) |
| 1\|2\|3\|45 `n1n8` | `n1npp` | crossover | none, `boundary_group_pooled` |
| 12\|3\|4\|5 `1888` | `pp888` | crossover | **3**, licensing 1–2 pooled (code: none; 08: undefined) |
| 12\|3\|45 `1n8` | `ppnpp` | crossover | none, `boundary_group_pooled` |
| 1\|2\|345 `11e` | `11eee` | one_signed_1.7B | none, `no_8B_cheaper_group` (code: false `boundary_in_merged_group`) |
| 123\|4\|5 `e18` (Sol) | `eee18` | crossover | **5**, licensing 4, gaps 1–3 (NE) |
| 1\|2\|345 `1n8` (Sol `1:1\|2:n\|[3–5]8`) | `1nppp` | crossover | none, `boundary_group_pooled` |
| 1\|2\|3\|45 `1n88` (Sol `1:1\|2:n\|3:8\|[4–5]8`) | `1n8pp` | crossover | **3**, gap 2 |
| 12345 `e` | `eeeee` | none_estimable | none, `none_estimable` |
| any partition, one group NE(`ceiling_violation`) | as above | as classified | none, `ceiling_violation_unresolved` |

*Source: 21/10 §Q1, "Authoritative worked-pattern table", legend and all 26 table rows (25 worked patterns plus the
generic ceiling-violation row). VERBATIM.*

## 4. D-166 dated addendum (draft)

Index row pointer, appended to the D-166 row at `docs/decision_log.md:212`: "(MATH levels: see dated addendum,
proposed 2026-09-24; adoption by Ed under E2)." In the addendum, "the MATH importer" is the program that builds the
frozen problem set (K1), and "the GSM8K constants and manifest" are the existing scored workload's fixed settings.
Ruling (9) carries K21 as the decision-log entry changing AP-5's smoke thresholds for this plan, as 30/10 T-3
directs.

> ## D-166 dated addendum (PROPOSED 2026-09-24, not adopted; Ed decides under E2): MATH author levels as a stratum for energy per correct answer
>
> **Forcing problem.** The headline question is how the energy spent per correct answer changes with problem
> difficulty and model size. AP-5 was written for a synthetic ladder built to keep answer length fixed, so it cannot
> host a benchmark whose answers lengthen on harder problems.
>
> **Terms.** As built in AP-5M §Terms (analysis_plans.md): level (the MATH authors' published label 1–5, never
> computed from model behaviour), attempt, cap, correct (a capped or malformed attempt is incorrect), cell, envelope,
> block, parent block, gross block energy, J/correct, R_L = J/correct(8B) ÷ J/correct(1.7B), and a supported switch
> (a change from 1.7B-cheaper to 8B-cheaper groups that AP-5M's decision table licenses).
>
> **Worked example (planning figures, unmeasured).** Level 5, thinking on, n = 64: the 1.7B spends 0.092 J/token ×
> 4,000 tokens and gets 16 correct, 1,472 J/correct; the 8B spends 0.375 J/token × 2,500 tokens and gets 40 correct,
> 1,500 J/correct; R_5 = 1.02. The 8B needed an accuracy ratio of 2.55 to break even and achieved 2.50.
>
> **Ruling.** (1) MATH levels may stratify energy-per-correct comparisons under analysis plan AP-5M. (2) Every AP-5
> prohibition carries over unchanged: no intelligence-per-joule claim, no "difficulty causes energy" claim; accuracy is a
> property of the pinned frozen problem set, never a capability claim, because Qwen3's pre-training contamination by
> MATH is unmitigable; correctness remains a quarantined annotation (C-004) used only as the J/correct denominator.
> (3) The three factors are always reported beside J/correct and gross block energy is co-displayed
> (`token_normalization.md`). (4) J/token and tokens/attempt are descriptive factors, never claim-bearing contrasts
> (D-045.7 unchanged). (5) The GSM8K constants and manifest keep their text; the MATH importer carries its own.
> (6) The energy numerator is gross energy between the outer item edges of each block; net-of-idle is never a peer
> number. (7) A crossover is claimed only where the AP-5M decision table licenses it: a crossover is the first
> supported switch in which model uses less gross energy per correct answer, and a pooled difficulty group can
> license only a region statement. (8) No problem is dropped for running long: overruns are retried under AP-5M's
> retry rules, and a problem that exceeds its registered worst case twice withholds the crossover until one bounded
> recapture resolves it. (9) For AP-5M, AP-5's envelope-validation smoke gate is replaced by the following clause:
>
> **K21 — pre-campaign smoke gate.** AP-5 requires an envelope-validation smoke gate that passes before any scored campaign (`analysis_plans.md:270`). AP-5's defined checks were written for a ladder whose prompts differ by one digit; for MATH, emitted-token mean and distribution and prompt-token count change with level by design, so those checks are not pass conditions here. The AP-5M smoke gate is one shakedown night per arm (M4, M13); each arm's scored campaign waits for its own pass. An arm's gate PASSES only when all of the following hold on every envelope of its shakedown night: (G1) every bundle is strict-valid; (G2) every attempt's `stop_reason` is `eos` (end-of-sequence token) or `length` (cap), `capped := generated_tokens ≥ cap_tokens[arm]` agrees with `stop_reason` on every row, and no attempt ends by runtime error, by kill at `ceiling_s`, or with a missing or unrecognised `stop_reason`; a malformed answer is an outcome (K3), counted incorrect, and does not fail the gate; (G3) every completed block's markers lie inside its envelope's usable interior, and no block's elapsed seconds exceed the sum, over its problems, of `cap_tokens[arm] × s_per_token_upper + prefill_s`. Reported per (model, level) with no pass threshold: emitted-token mean and distribution, prompt-token count, cap-hit fraction beside the registered `cap_bound_fraction` (0.20), and the early-stop-bias descriptor (mean emitted tokens of incorrect minus correct attempts; AP-5's E5). A failed gate records `smoke_failed([reasons])`; no scored campaign starts for that arm; the cause is cured and recorded and that arm's shakedown repeated; no registered value beyond those K2 as extended (T-24) lets the pilot and shakedown set changes on its account. A G3 failure falsifies `s_per_token_upper` for that arm; it is re-derived before any repeat.
>
> **Status.** Proposed. A cold gate has ruled on this text's draft (record 30/10); Ed adopts or rejects it under E2
> (Gmail `1a0d069e15a52ba9`). Until then it binds nothing.
>
> Gate records:
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md`;
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/11-opus-contract-refuter.md`;
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md`;
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md`;
> `docs/process_traces/2026-09-24-activation-a65fb4fa/30-coldgate-packet-a282-ap5m/10-coldgate-fable-ruling.md`;
> draft `docs/process_traces/2026-09-24-activation-a65fb4fa/07c-a282-ap5m-draft-v3.md`.

Forcing problem and ruling (1)–(5): C §2a VERBATIM. Terms and worked example: C §2a ADAPTED. Ruling (6): 19 M7
ADAPTED. Ruling (7): the A282 queue row ADAPTED. Ruling (8): this seat's summary of K13 and S7–S8. Ruling (9): lead-in
by this seat; the clause is T-3 VERBATIM. Matching edits elsewhere follow packet C §6, except that its
`claims_ladder.md:63` entry reads "five parent blocks in five envelopes (M8)" and its
`research_question_bank.md:1728-1738` entry uses n ∈ {64, 128} from K2.

## 5. Gate texts T-1 to T-28: where each is installed

Final texts come from two rulings: 30/10 §3 (T-1, T-2, T-16 to T-19, T-22 and T-23 stand as written there) and 30/21
§3 (supersedes T-3, T-5, T-7 to T-15, T-20 and T-21; amends T-4 and T-6; adds T-24 to T-28). Every text is pasted
byte for byte; for T-5, T-7, T-20 and T-25 the quoted fragments the ruling dictates. Coverage is total: every 30/10
text not superseded and every 30/21 text has a location.

| T-n | Operative text from | Ruling target | Installed at in v4 |
|---|---|---|---|
| T-1 | 30/10 | §2.1 sparse/merge term | §2.1 "Denominator guard, sparse, merge, group, pooled" |
| T-2 | 30/10 | row "Denominator provenance requirement" | §2.8 row |
| T-3 | 30/21 (supersedes) | K21; row points to K21; D-166 carries it | §2.9 K21; §2.8 row "Inclusion/exclusion"; §4 ruling (9) |
| T-4 | 30/10, amended by 30/21 | §2.1 floor term; `floor_cmp_j` sentence | §2.1 "Instrument floor and anchor bound" (30/21's `floor_cmp_j` sentence in place of 30/10's) |
| T-5 | 30/21 (supersedes) | steps 2, 7, 8; K11; worked examples | §2.2 steps 2, 7, 8; §2.9 K11; §2.3 "Anchor bound" and §2.5 relabelled (T-5's "§2.6 instrument-bound lines" are this file's §2.3; §2.6 has no anchor expression) |
| T-6 | 30/21 (supersedes) | row "Floor gate" | §2.8 row |
| T-7 | 30/21 (supersedes) | interval term; step 11; K10 | §2.1 bootstrap term and §2.2 step 11 (first fragment, unchanged from 30/10); §2.9 K10 (second fragment) |
| T-8 | 30/21 (supersedes) | step 10 | §2.2 step 10 |
| T-9 | 30/21 (supersedes) | flag term; K22 | §2.1 last Estimation term; §2.9 K22; flagged at step 4 |
| T-10 | 30/21 (supersedes) | drift threshold term; O-7; K12 | §2.1 drift term; §2.9 K12; O-7 closed (§7) |
| T-11 | 30/21 (supersedes) | step 12; K16 | §2.2 step 12; §2.9 K16 |
| T-12 | 30/21 (supersedes) | drift term | §2.1 drift term |
| T-13 | 30/21 (supersedes) | after the Night term; K23 | §2.1 "Nights and retries (K23)", after the drift term so its terms are built first, with a pointer from the Night term; §2.9 K23; flagged at step 5 |
| T-14 | 30/21 (supersedes) | after the voided/counted windows term, as K24 | §2.1 "Counted attempt (K24)"; K24 pointer in §2.9 |
| T-15 | 30/21 (supersedes) | S8 | §3 S8 |
| T-16 | 30/10 | O-8 | §7 O-8 |
| T-17 | 30/10 | S7 | §3 S7 |
| T-18 | 30/10 | S6 template rules | §3 S6 "Combined sentence" |
| T-19 | 30/10 | row "Order/blocking/covariates"; K4 | §2.8 row; §2.9 K4 |
| T-20 | 30/21 (supersedes) | K2 budget sentence; O-18; O-14's list | §2.9 K2; §7 O-18; §7 O-14 and the registration list |
| T-21 | 30/21 (supersedes) | K1 predicate | §2.9 K1 |
| T-22 | 30/10 | scorer term | §2.1 "Scorer, correct, malformed" |
| T-23 | 30/10 | power term, last sentence | §2.1 "Power boundary and sampler" |
| T-24 | 30/21 (new) | after K2's C §3 carry | §2.9 K2 |
| T-25 | 30/21 (new) | K9 lead-in; step 6; K19; change log | §2.9 K9 and K19; step 6 and change-log deletions had no target in v3; §2.10 carries the replacement sentence |
| T-26 | 30/21 (new) | clause K25 | §2.9 K25 |
| T-27 | 30/21 (new) | K10, after the M9 carry | §2.9 K10 |
| T-28 | 30/21 (new) | S9 and K16, append | §3 S9; §2.9 K16 |

## 6. Provenance

Keys as in §1. "VERBATIM" means byte-identical to the source after removing the leading `> ` of each quoted line.

| # | Carried text (opening words) | Where | Source | Carry |
|---|---|---|---|---|
| 1 | "Caps, block size, envelope pitch, n per level…" | K2 | 19 §1 M5 | VERBATIM |
| 2 | "**Fixed n and pilot.** A 16-problem sizing pilot…" | K2 | C §3 | VERBATIM |
| 3 | "Every attempt that hits the cap counts as incorrect…" | K3 | 19 §1 M2 | VERBATIM |
| 4 | "capped := generated_tokens ≥ Registration.cap_tokens[arm]…" | K3 | 21/11 R9 | VERBATIM |
| 5 | "A cell with more than 20 % capped attempts…" | K3 | 19 §1 M3 | VERBATIM |
| 6 | "**Cap-bound label.** A cell with > 20 % truncated attempts…" | K3 | C §3 | VERBATIM |
| 7 | "Gross energy between the outer item edges of each block…" | K4 | 19 §1 M7 | VERBATIM |
| 8 | "Descriptive only." | K5 | 19 §1 M10 | VERBATIM |
| 9 | "An empty slot is captured as a full-length envelope…" | K6 | 08 F1 | VERBATIM |
| 10 | "Drift cancels in a per-level ratio only when…" | K6 | 21/10 §Q4 F1 | VERBATIM |
| 11 | "Idle collector plus a separate model worker…" | K6 | 19 §1 M13 | VERBATIM |
| 12 | "Each cell is spread over at least 5 blocks…" | K7 | 19 §1 M8 | VERBATIM |
| 13 | "M8 applies to parent blocks…" | K8 | 45/10 §Q4 | VERBATIM |
| 14 | "Exact scorer output plus emitted-token/stop-reason audit; binomial lower-bound…" (replaced wording) | K9 | analysis_plans.md:274 | VERBATIM |
| 15 | "**Minimum correct and merge order.**…" | K9 | C §3 | VERBATIM |
| 16 | "Bootstrap over paired problems **and** over capture blocks…" | K10 | 19 §1 M9 | VERBATIM |
| 17 | "per replicate, per drawn block and model, `u = k·(floor_j + anchor_j)·s`…" (bracket superseded) | K11 | 21/10 §Q2 D5a | VERBATIM |
| 18 | "U_m = Σ u. Low bound R(E₈ − U₈, …)…" | K11 | 20 §Q5(a) | VERBATIM |
| 19 | "(6) The reported interval runs from the 2.5th percentile…" | K11 | C §3 step 6 | VERBATIM |
| 20 | "The drift lever of a level is the absolute difference…" | K12 | 45/10 §Q4 | VERBATIM |
| 21 | "register `δ_upper` in joules per block per slot…" | K12 | 21/10 §Q2 D5b | VERBATIM |
| 22 | "If the executed roster's gap exceeds max for a level…" | K12 | 21/11 R11 | VERBATIM |
| 23 | "A block that overruns is re-queued once within the night…" | K13 | 19 §1 M12 | VERBATIM |
| 24 | "After a second overrun, the items become single-problem BLOCKS…" | K13 | 08 M12 amendment | VERBATIM |
| 25 | "the worst-case seconds input is derived in Registration…" | K13 | 21/10 §Q4 | VERBATIM |
| 26 | (W) "`requeue_overrun` at the initial and whole-block stages…" | K13 | 45/21 §7 (W) | VERBATIM |
| 27 | (T) "A whole-block retry advances to the split stage…" | K13 | 45/21 §7 (T) | VERBATIM |
| 28 | (N) "At the single stages the observation per single…" | K13 | 45/21 §7 (N) | VERBATIM |
| 29 | (E) "An envelope with no active block is legal iff…" | K13 | 45/21 §7 (E) | VERBATIM |
| 30 | "`unattributed_overrun` is unreachable under correct instrumentation…" | K13 | 45/21 §8 N1 | VERBATIM |
| 31 | "runner lane, as the per-attempt kill timeout…" | K13 | 45/10 §Q2 | VERBATIM |
| 32 | F2 (a)–(d) "Pairing survives a split…" | K13 | 08 F2 | VERBATIM |
| 33 | spread_exceeded with (X) substituted | K15 | 45/10 §Q4 + 45/21 §7 (X) | ADAPTED (A3) |
| 34 | (P) "When a level carries both NE(`ceiling_violation`)…" | K16 | 45/21 §7 (P) | VERBATIM |
| 35 | "A window for a terminal ceiling_violation attempt is accepted…" | K17 | 45/10 §Q5 F3 | VERBATIM |
| 36 | "`mode = pilot` objects may emit only rosters…" | K18 | 21/10 §Q2 D4 | VERBATIM |
| 37 | "Module constants pinned by `schema`…" | K19 | 45/10 §Q3 | VERBATIM |
| 38 | "Capability or leaderboard claims; rankings beyond this pair and set…" | K20 | C §5 | VERBATIM |
| 39 | Claim-language table (4 rows) | K20 | C §4 | VERBATIM |
| 40 | "Group status: `8B cheaper` (E8)…" | S1 | 20 §Q2 | VERBATIM |
| 41 | "The status rule is: Holm rejects, the direction by p…" | S2 | 21/00 D2 | VERBATIM |
| 42 | "Packet C's terms paragraph… widened interval straddles 1…" | S2 | 21/10 §Q1 | VERBATIM |
| 43 | merge/holm/status/classify pseudocode | S2 | 20 §Q2 | VERBATIM |
| 44 | "A merged group may license L\* only as a region statement…" | S3 | 21/10 §Q1 Split 1 | VERBATIM |
| 45 | "Pattern `reverse_order`, reason `reverse_order_not_registered`…" | S4 | 21/10 §Q1 Split 2 | VERBATIM |
| 46 | "(b) `reverse_order` is any resolved sequence matching `8+1+`…" | S4 | 21/10 §Q1 (b) | VERBATIM |
| 47 | "NIT: non_monotone rows need the reason code `non_monotone`." | S4 | 21/11 R5 | VERBATIM |
| 48 | "**Isolated sparse Level 3: AFFIRM**…" | S5 | 21/10 §Q1 | VERBATIM |
| 49 | "(a) `gap_levels` must list every NR/NE level…" | S6 | 21/10 §Q1 (a) | VERBATIM |
| 50 | "If any level lies strictly between the licensing group…" | S6 | 21/11 R4 | VERBATIM |
| 51 | "NIT: keep `bracket_gap_levels` separate." | S6 | 21/11 R4 | VERBATIM |
| 52 | "When any item in the family carries a terminal `ceiling_violation`…" | S7 | 21/10 §Q1 Split 3 | VERBATIM |
| 53 | "At most one recapture, on a later census-clean window…" | S8 | 21/11 R6 | VERBATIM |
| 54 | "Constituents of an estimable merged group get `pooled`…" | S9 | 21/11 R7 | VERBATIM |
| 55 | "**Null wording.** All levels above 1…" | S10 | C §3 | VERBATIM |
| 56 | "When any group is pooled, the null sentence reads…" | S10 | 21/11 R3 | VERBATIM |
| 57 | Table legend + 26 table rows | S11 | 21/10 §Q1 | VERBATIM |
| 58 | "Thinking-on R_L: primary. Thinking-off R_L: secondary…" | row claim_role | C §2b | VERBATIM |
| 59 | "Holm within each family, α = 0.05 two-sided, m = 5 fixed…" | row multiplicity | C §2b | VERBATIM (first two sentences) |
| 60 | "Ceiling L2 on this frozen set, stack and caps. Forbidden: …" | row ceiling | C §2b | VERBATIM |
| 61 | D-166 forcing problem and ruling (1)–(5) | §4 | C §2a | VERBATIM |
| 62 | T-1 to T-28 | §5 map | 30/10 §3 and 30/21 §3 | VERBATIM |
| 63 | D-166 terms and worked example | §4 | C §2a | ADAPTED (A4) |
| 64 | D-166 ruling (6) | §4 | 19 §1 M7 | ADAPTED (A5) |
| 65 | D-166 ruling (7) | §4 | TASK_QUEUE A282 row | ADAPTED (A6) |
| 66 | K1 population and draw | K1 | 19 §1 M1 + §Addendum; `joulewise/benchmark_import_math.py` | ADAPTED (A1) |
| 67 | K10 two-stage draw | K10 | C §3 step 3; `d2f9a273:joulewise/energy_per_correct.py` | ADAPTED (A2) |

Counts: 61 VERBATIM source carries (rows 1–32, 34–61; row 59 covers two sentences, the 26-row table and the
pseudocode count once each), 28 gate texts (row 62), 6 ADAPTED (rows 33, 63–67). Version 2's faithful excerpt of the
R6 dissent is gone: the dissent's reasons are now operative through T-17.

**Adaptations, with originals.**

- **A1 (K1).** Original, 19 §1 M1: "The full MATH test split, 5,000 rows = `test.jsonl` plus the `test/`-tagged rows of
  `train.jsonl` at `openai/prm800k` `7ecc7947`. Those rows hold 5,001 lines and 4,999 unique ids. **Both** rows of the
  duplicated id are excluded. Rational-valued answers only. Balanced by subject." Corrected by 19 §Addendum: "5,001
  rows, 5,000 distinct ids before exclusion (one id appears twice), 4,999 singleton ids. Exclusions are both rows of
  the duplicated id (2), 954 non-rational references and 5 plain-comma references. That leaves **5,001 − 2 − 954 − 5 =
  4,040 eligible**". The eligibility predicates, per-level counts and draw are read from the merged importer
  (`canonical_reference_v1`, `plain_comma_ambiguous`, `ELIGIBILITY_NOTE`, `select_pilot`, `select_items`); the
  grouped-integer forms are T-21.
- **A2 (K10).** Original, C §3 step 3: "Draw B = 20,000 resamples (seed pinned in the registration). Each draws n
  problem indices with replacement within the level and applies the same indices to both models". M9 requires the
  block level too; K10 describes the draft estimator's two-stage scheme (docstring: "Bootstrap common blocks, then
  paired problems within each drawn block"), adopted by 30/10 Q4.
- **A3 (K15).** Original, 45/10 §Q4: "…or fewer than five distinct envelopes holding them, because a parent lost an item
  to a terminal ceiling_violation after capture. The cell carries…". Substitution, 45/21 §7 (X): "Replace 'because a
  parent lost an item to a terminal ceiling_violation after capture' with 'for any reason after capture (terminal
  `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place)'."
- **A4 (§4 terms and example).** C §2a's terms paragraph and its worked example ("Level 5, n = 64: the 1.7B spends
  0.092 J/token × 4,000 tokens/attempt and gets 16 correct (25%): 0.092 × 4,000 ÷ 0.25 = 1,472 J/correct. The 8B
  spends 0.375 J/token × 2,500 tokens and gets 40 correct (62.5%): 1,500 J/correct. R_5 = 1.02. …") are shortened;
  numbers unchanged; "supported switch" added to the terms.
- **A5 (§4 ruling 6).** Original, 19 §1 M7: "Gross energy between the outer item edges of each block. Net-of-idle is
  never a peer number; the idle reference is a covariate." Rephrased as a ruling clause.
- **A6 (§4 ruling 7).** Original, TASK_QUEUE A282: "a crossover is the first supported switch in which model uses less
  gross energy per correct answer, and a pooled difficulty group can license only a region statement." Carried word
  for word inside a new lead-in.

## 7. Open items

**Closed by rulings 30/10 and 30/21** (each with the question that closed it):

- **O-1 (reason for withholding L\*): closed by 30/10 Q13**, T-17 (S7).
- **O-2 (denominator guard): closed by 30/10 Q1**, T-1 and T-2, with 30/21 A11's T-25 lead-ins: observed count ≥ 3,
  replacing AP-5's wording for AP-5M (part of Ed's E2 adoption).
- **O-3 (claim sentence): closed by 30/10 Q14**, T-18 (S6).
- **O-4 (interval and draw): closed by 30/10 Q4 and 30/21 A15**, T-7: percentile-only ends, point bounds reported
  beside; K10's draw, the random-number generator, Hyndman–Fan type 7 percentiles and the placement of undefined
  replicates adopted as registration text.
- **O-5 (Holm membership): closed by 30/10 Q5 and 30/21 A5**, T-8 (step 10).
- **O-6 (flags in merged groups; recapture count): closed by 30/10 Q6 and 30/21 A4**, T-9 (§2.1 and K22) and T-28.
- **O-7 (drift threshold): closed by 30/10 Q7–Q8 and 30/21 A2, A3, A5, A9, A18**, T-10 (K12), T-11 (step 12, K16) and
  T-12 (drift model).
- **O-8 (retry trigger): closed.** The 10 %-retried trigger is not adopted. Its hazard, position imbalance after retries, is covered by K12: the executed roster's lever is recomputed after every requeue and an excess is NR(`drift_exceeded`) pending the K22 recapture.
- **O-9 (failed recapture check): closed by 30/10 Q11 and 30/21 A7**, T-15 (S8).
- **O-10 (tails across nights): closed by 30/10 Q9 and 30/21 A4**, T-13 (K23).
- **O-11 (smoke gate): closed by 30/10 Q2 and 30/21 A1, A9, A12**, T-3 (K21 and §4 ruling (9)).
- **O-12 (floor and anchor): closed by 30/10 Q3 and 30/21 A10, A17**, T-4 to T-6. The block-window floor row is a
  registration prerequisite; the estimate-level floor check is reserved to Ed as O-21.
- **O-13 (idle covariate): closed by 30/10 Q15**, T-19.
- **O-14 (registration numbers): closed by 30/10 Q16 and 30/21 A18**: envelope length, cap ladder, capture budget
  (in nights) and seed are left to the registration packet, which must be hashed before any test problem runs; T-20
  adds `max_envelopes_per_night` and the per-(arm, level) `budget_j` and `max_gap` to the list.
- **O-15 (problem draw): closed by 30/10 Q17 and 30/21 A16**, K1 adopted with T-21.
- **O-16 (added row fields): closed by 30/10 Q18**, kept.
- Not previously open items, ruled by the gate: which attempt counts, and dropped pairs (30/10 Q10, 30/21 A6; T-14);
  what the pilot and shakedown may set (30/21 A8; T-24); the code amendment for night-bounded retries and recaptures
  (30/21 A13; T-26, which binds the code only once that code's own gate ratifies it).

**Left to the registration packet (not claim policy):** envelope length, interior, offset and guard margin;
`max_envelopes_per_night`; the cap ladder values; the capture budget in nights; the seed; the block-window
`floor_gate_j` row; per model and arm `s_per_token_upper` and `prefill_s`, and `ceiling_s` (set from the pilot and
shakedown, T-24); δ_upper per arm and `budget_j` and `max_gap` per (arm, level), computed as K12 prescribes from each
arm's shakedown night.

**Open for Ed:**

- **O-17 (Ed, E2).** Adopt AP-5M and the §4 addendum, amend, or reject. Every NEW RULE of the two rulings is text for
  that adoption, not policy: K22's one recapture per (arm, level), K12's 1 % per-level budget and its derivation, the
  observed-count guard's replacement of AP-5's wording (T-1, T-2, T-25), K21's smoke predicates, K2's extension
  (T-24), and the code amendment K25 (T-26). Packet C's proposed choices, narrowed since: (1) a sibling row, not a
  rewrite of AP-5; (2) two Holm families of m = 5, not one of m = 10; (3) rung L2's "n ≥ 5" met by five parents in
  five envelopes, not by amending the ladder; (4) J/token descriptive only; (5) capped = incorrect even when an answer
  parses; (6) the 20 % cap-bound threshold and the per-arm cap rule; (8) the residual fit exploratory; (9) claims say
  "MATH level", and "difficulty" appears only where defined.
- **O-18 (Ed, E4).** n per level is chosen mechanically by K2 (c): 128 if the pilot-projected capture fits the
  registered window budget, else 64. Ed's decision is whether the budget is acceptable; planning figures (record 18) are about 12 nights for n = 64 and about 23 for n = 128, plus one shakedown night per arm, at 4–5 nights a day. ("Record 18" in that sentence is record 18i.)
- **O-19 (Ed, E3).** Decoding: (a) greedy, labelled "under greedy decoding"; (b) the model card's seeded sampling
  (temperature 0.6, top-p 0.95, top-k 20, one pinned seed per problem and model); or (c) thinking-off as primary.
  Recommendation (record 19): (b), with (a) as fallback if seeded sampling does not reproduce the same tokens. The
  estimand is incomplete until this is decided; under (b), T-14's `attempt_divergence` can occur.
- **O-20 (Ed, E1).** Whether the problem text is published. Options: commit only ids and hashes, with the text in an
  untracked "custody path" (a storage location outside the repository whose files are bound by sha256 digests
  recorded in it); or publish the text. Recommendation (record 19): hashes and ids only, because PRM800K's licence
  covers OpenAI's data and probably not the Art of Problem Solving problem text.
- **O-21 (Ed, E2; reserved by 30/21 A17).** Must AP-5M also register an estimate-level floor check from the project's
  floor contract (`detection_floor.md`, single-count discipline): a claimed J/correct difference is accepted only if
  its size exceeds the floor F (`|estimate| > F`), in addition to Holm and the anchor-widened interval excluding the
  no-difference value (1 for a ratio)? Until adopted, claim acceptance is Holm plus that interval test (T-6). Yes or no.

## 8. Residual

Findings the rulings flag without dictating text, and points this installation could not settle:

- **"Adjacent" in S8.** The recapture puts "both models' copies adjacent as singles"; this seat reads "adjacent" as
  consecutive envelope indices (record 18 G11). No ruling fixes it; it affects scheduling only.
- **Shakedown design.** T-3 and T-10 require one shakedown night per arm, in which each model runs one fixed block of
  pilot problems twice, in its first and last envelopes. Packet B's shakedown plan (record 09 of activation 1d3796d5)
  does not yet include those runs; the runner and registration work items must add them, or registration refuses.
- **δ_upper needs the block-window floor.** T-10 adds `floor_gate_j` of the block-window class to each model's
  observed difference; until that floor row exists (a registration prerequisite, T-6), δ_upper cannot be computed.
- **K25 is not yet in force for the code.** Until the packer's own gate ratifies T-26, `_seal` refuses
  `night_exhausted` transitions and recapture rosters, so neither the K22 nor the S8 recapture can be produced.
- **T-13 placement.** Installed as its own Terms entry after the drift term instead of directly after the Night term,
  so that the terms it uses are built first; the Night term points to it. Wording unchanged.
- **T-5's section reference.** T-5 names "§2.5 and §2.6" worked examples; in this file the anchor lines sit in §2.3
  and §2.5 (the version-2 numbering), and both are relabelled.
- **Naming inside T-3.** T-3 says "AP-5's E5"; this cannot be edited, so K21's lead-in glosses it.
- **Hygiene NITs H1, H2 of 30/10.** H1 is followed (K21 cites the D-047 correction, not the superseded passage); H2
  concerns the charge only.

## 9. First-use self-check

Method: a script listed each term, symbol and code in this file with the line of its first occurrence and the line
where it is built or glossed, and flagged any term used before it is built; the result was then checked by hand
against record 18's table (its 31 rows) and record 12's table. Results:

- **Built or glossed before use:** every row of record 18's table marked FAILS (N2, N4–N9, N12–N15, N18–N24, N29, N31)
  and the two fix-introduced defects (N11, N19), as listed in §2.10; the terms new in this version (counted attempt,
  decoding, interior, offset, `guard_s`, `floor_gate_j`, n, s_r and t_0.975 in the floor formulas, `below_floor`,
  `point_low`/`point_high`, `night_exhausted`, capture window, arming, `attempt_divergence`, `flagged_levels`,
  `s_per_token_upper_falsified`, smoke predicates G1–G3).
- **Terms new in version 4, built or glossed at first use:** Σ_w anchor_{j,w} and per-window anchor values (floor
  term and K11), s_δ and δ_i (floor term), single-count discipline and zero-exclusion (floor and group-status terms,
  before T-6 and O-21 use them), `eos` and `length` (step 1 and T-3), `randrange` and Hyndman–Fan type 7 (K10 lead-in),
  `recapture_of` and `recapture_unpaired` (K22–K23 lead-ins), `max_envelopes_per_night` (self-describing registration
  field in T-13, listed in §7), (G), (E), (S) and item conservation (K25 lead-in), capture session (Ed summary).
- **Glossed at first use rather than built before it** (the gloss sits in the same sentence or the next): the
  night in the Envelope term; "the interval", prefill and decode inside the floor term (the carried T-4 uses them
  before the Estimation terms); the K22 recapture referred to by T-13 and T-9 (the term "recapture" is built first,
  the clause K22 is a pointer); `max_gap` in T-12, defined by T-10 in the same term.
- **Built only by pointer or by reference, not in full:** census-clean (a reference to the runbook's coded census);
  strict validation's list of checks (by reference to `run_bundle_layout.md`); the registration numbers left to the
  registration packet (§7); "problems per bundle" and "declared ladder" inside the K2 carries (glossed as block size
  and as the cap values' list).
- **Plain-English uses not treated as terms:** "work item" (§1), "time interval" (T-23), "packet", "seat".
- **Left as identifiers without explanation:** work-item ids (A281b/A293, A282, A291, A294) and the activation ids in
  paths; the model names Fable, Sol and Opus (reviewer identities only); `RQ-NEXT-EPCA-LEVELS` beyond its one-line
  gloss. Every decision code cited (C-004, D-045.7, D-047.3, D-047.6, D-062, D-078, D-079, D-084, D-166) is glossed
  at or before first use.
- **Known residual inside verbatim text:** "AP-5's E5" in T-3 (glossed in K21's lead-in) and "record 18" in T-20
  (glossed where used as record 18i).
