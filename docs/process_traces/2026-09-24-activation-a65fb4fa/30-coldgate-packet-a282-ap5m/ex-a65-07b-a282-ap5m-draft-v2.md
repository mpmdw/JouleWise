# 07b — A282 AP-5M draft, version 2: the proposed MATH energy-per-correct analysis plan and D-166 addendum (PROPOSAL)

Written 2026-09-24 by an Opus 5.5 drafting subagent (a "seat": one delegated agent session with a bounded task)
for work item A282 of the project task queue, in the project-loop session identified as activation a65fb4fa. It
replaces version 1 (record 07 in this folder) completely, and installs the findings of two reviews of version 1:
record 11 (source fidelity, by the Sol model) and record 12 (teaching quality and replicability, by Opus), under
the magistrate's rulings for version 2. Read-only everywhere else.

## 1. Status, sources and how to read this file

**This is a proposal, not adopted claim policy.** AP-5M is a proposed row of the project's analysis-plan contract
(`docs/contracts/analysis_plans.md`): a filled table of rules that any published claim about MATH energy per correct
answer would have to cite and obey, written before any data exist. The accompanying D-166 addendum is a dated
amendment to decision-log entry D-166 (the project's workload decision), which today licenses scored benchmarks
only for the GSM8K leg (a separate scored workload of grade-school arithmetic word problems). The magistrate (the
agent that runs the project loop day to day) cannot adopt claim policy. An independent cold gate (a fresh Claude
Fable instance with no loop context, paired with an Opus refuter who checks the text against the project's
contracts) reviews this draft. Ed (the project owner) alone decides adoption, through his answer to question E2
("adopt AP-5M and the D-166 addendum?") of the decision brief emailed on 2026-09-23 (Gmail `1a0d069e15a52ba9`);
that answer is still pending. The same brief's other questions are E1 (publishing the problem text), E3 (decoding
rule and primary arm) and E4 (problems per level, i.e. budget). Until Ed answers, no sentence here binds any
measurement, estimator or claim.

**Where the text comes from.** Project history is kept as numbered files ("records") in one folder per
supervisory session ("activation"), `docs/process_traces/<date>-activation-<id>/`. This file cites them by short
keys:

| Key | File | What it is |
|---|---|---|
| **C** | `docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md` | Packet C: the first design draft of AP-5M. |
| **19** | `…/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md` | The integration synthesis: the magistrate's record merging three design packets; its settled items are numbered M1–M13 and its questions for Ed E1–E4. |
| **18** | `…/2026-09-23-activation-1d3796d5/18-headline-opus-integration.md` | The Opus integration consult behind record 19 (contains the planning arithmetic). |
| **08** | `…/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md` | The magistrate's rulings after the first review round of the draft estimator and packer code ("round-1 rulings"). |
| **20** | `…/2026-09-23-activation-d8cc9c0a/20-a281-opus-consult.md` | An Opus consult that wrote the decision vocabulary and procedure. |
| **21/00, 21/10, 21/11** | `…/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/{00-charge, 10-coldgate-fable-ruling, 11-opus-contract-refuter}.md` | Cold gate 21: its charge, its ruling, and its paired refuter. |
| **45/10, 45/21** | `…/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/{10-coldgate-fable-ruling, 21-coldgate-fable-addendum-ruling}.md` | Cold gate 45: its ruling on the packer and its addendum ruling. |
| **11, 12** | `docs/process_traces/2026-09-24-activation-a65fb4fa/{11-a282-fidelity-sol-lens, 12-a282-pedagogy-opus-lens}.md` | The two reviews of version 1. |

When sources conflict, the later ruling prevails, in this order: 45/21 §7, 45/10, 21/10 with 21/11, 08, then C
and 19. Blockquoted text is copied byte for byte from the source named under it (marked VERBATIM); anything
else is this seat's drafting and has no authority beyond the proposal. Codes like D-062 or C-004 are decision-log
and council entries; each is glossed in one clause where first cited.

**What version 2 replaces.** It replaces packet C as the AP-5M candidate: C's draft decision-log addendum (its
§2a), its draft row (§2b) and its decision rule (§3) are replaced by §2–§4 below; C's statement of the problem,
prohibitions, claim-language table, sizing condition and list of files needing matching edits (§6) are carried.
§2.9 itemises every change from C and from version 1, after the terms it needs.

## 2. The proposed AP-5M row

### 2.1 Terms (read before anything below; each term uses only terms defined above it)

**Setup and problems.**

- **Registration.** The frozen, hashed record of every rule, constant and input fixed before any test problem runs
  (problem ids, caps, timing, bounds, seeds and the other settings named below). "Pinned" means fixed in the registration by version and
  content hash. Nothing registered changes once data exist; adding problems after seeing results (a "top-up") is
  forbidden (D-062: n is frozen before execution, and an outcome-dependent top-up demotes a result to
  exploratory, i.e. not claim-bearing).
- **Problem, level, reference answer.** A MATH problem is one competition-mathematics question with one reference
  answer, from the MATH dataset (Hendrycks et al., 2021), as redistributed in the PRM800K repository. Its *level*
  is the integer 1–5 the dataset's authors attached when they published it. It is fixed before any model sees the
  problem and is never computed from a model's success rate or answer length. In this plan "difficulty" means only
  this label. An *item* is one problem as scheduled inside a block (below).
- **Model, arm.** The two models are Qwen3 1.7B and Qwen3 8B, run as pinned 4-bit weights under MLX (Apple's
  machine-learning framework for Apple-silicon chips) on one M3 Max laptop. An *arm* is a thinking mode: *thinking
  on* (the model writes a reasoning trace before its answer) or *thinking off*. Both arms use the same problems.
- **Attempt, cap, capped, stop_reason.** An *attempt* is one generation by one model for one problem. The *cap* is
  the fixed maximum number of tokens an attempt may generate in an arm. An attempt that reaches the cap is
  *capped*; packet C calls the same thing *truncated*, and this file treats the two words as one. `stop_reason`
  records why generation stopped: the model's end token, or the cap ("length").
- **Scorer, correct, malformed.** The prompt asks the model to put its final answer in `\boxed{…}` (a "boxed
  answer"). The *scorer* is a pinned program that reads the last boxed answer and compares it with the reference as
  an exact rational number. An attempt is *correct* only when the scorer finds a match and the attempt is not
  capped. A *malformed* attempt has no extractable answer and counts as incorrect (D-047.6: malformed items count
  as incorrect in the accuracy denominator).
- **Cell.** One (model, arm, level) combination.

**The instrument.**

- **Power boundary and sampler.** Power is read by macOS `powermetrics`, the operating system's power sampler, at a
  100 ms sampling interval. Its boundary is the Apple system-on-chip package: CPU + GPU + neural-engine power,
  summed over the rails (separately reported power domains) named in the adapter's rail manifest; display,
  storage, memory at the wall and power-supply losses are excluded (`docs/contracts/measurement_methodology.md`
  boundary table; `docs/paper/artifact-guide.md` §10.1). The *energy rail* identity in M13 means this rail manifest
  and boundary. Energy in a time interval is the sum of the sampler's per-record energy counters falling in it.
- **Envelope, envelope index, pitch, capacity.** An *envelope* is one continuous, fixed-length power recording
  during which exactly one model is loaded. Envelopes follow one another on a fixed schedule: the *pitch* is the
  start-to-start spacing, and the *envelope index* 0, 1, 2, … is an envelope's position in that schedule. Its
  length is a registration number not yet fixed (the gate-21 charge states 600 s; the planning arithmetic in record
  18 uses 480 s slots; O-14). *Capacity* is the number of seconds inside an envelope available for running
  problems; the draft packer defines it as `interior_s − guard_s` (the envelope's working interior minus a safety
  margin; `scored_registration.py:129` at draft `c0998fdb`, recorded in record 02b of this folder).
- **Idle slot.** An envelope recorded with its model loaded and doing nothing, labelled `kind: "idle_slot"`. It
  keeps the schedule grid evenly spaced. Its joules are never divided by anything to form a result.
- **Block, block window, gross block energy.** A *block* is a fixed list of items from one cell, run back to back
  inside one envelope. A marker is written when its first item starts and when its last item ends (the block's
  *outer item edges*). The *block window* is the interval between those markers. *Gross block energy* is the joules
  the sampler records inside the block window, with nothing subtracted for idle power (D-045.7: per-item, block and
  level energies are gross only). In this file "window" alone always means a block window. Energy is read only per
  block window; per-problem energy inside a multi-problem block is never read.
- **Night (measurement window), census-clean.** A *night* is one scheduled, unattended capture session holding a
  sequence of envelopes (the sources also call it a "window"; this file says "night"). *Census-clean* is a
  reference, not a definition written here: it means the night passed the project's coded agent census, which
  refuses a night while any process matching `codex|claude|t3` is running, run at arm time and at the night's start
  (`docs/phase_2/derivation_night_runbook.md` §0.6, "Census clean, and the night is agent-free"); machine-activity
  admission is a separate contract (`docs/contracts/night_quiet_admission.md`).
- **Instrument floor and anchor bound.** Two different error terms come from the instrument. (i) The *floor*: the
  smallest energy difference the instrument can distinguish from zero for a given kind of window. The contract
  names it `max(floor_abs_j, floor_cmp_j)`: `floor_abs_j` is the spread of repeated measurements of an identical
  workload, `floor_cmp_j` the spread of same-condition contrasts measured in A-B-B-A order (alternating repeats of
  two identical conditions), and the larger is the claim gate
  (`docs/phase_2/detection_floor.md` "Floor Artifact Semantics"; "P2-015" is the work item that issues this
  calibration artifact). A *window class* is the kind of interval an energy figure integrates over (request, phase,
  item, level, block …); floors are calibrated per class. On this stack the floor is attribution-limited: about
  1 J, set by how precisely a window's edges can be placed in the sampler's record, not by noise (D-078 clause 11;
  detection_floor.md, `floor_limit_class: "attribution_limited"`). (ii) The *anchor bound* `anchor_j`
  (`E_clock_anchor_shift_bound_j`): the most energy that can be assigned to the wrong window because the marker
  clock and the sampler's clock may be offset. In the estimator below, `floor_j` names the per-window floor value
  and `anchor_j` the per-window anchor bound; no block-window floor artifact exists yet (O-12).

**Scheduling and retries.**

- **Sizing pilot.** Before the test, 16 problems per level (disjoint from test problems) are run on the bench
  without power capture ("bench token pilot") to measure tokens per item, cap hits and rough seconds per token, then
  one short measured "shakedown" night checks envelope timing (M4 of record 19). Its outputs set only the
  quantities K2 lists; it is never reported as a result.
- **Packer, roster, parent block, piece.** The *packer* is the program that assigns blocks to envelopes before the
  night; its output list is the *roster*. A *parent block* is a block placed by this initial packing. A retry can
  cut a parent into one-problem blocks; each is a *single*, also called a *piece* of its parent.
- **Predicted, worst-case and reserved seconds.** `predicted_s` is the packer's forecast of a block's duration from
  the sizing pilot. The *derived worst case* of one problem is `cap_tokens × s_per_token_upper + prefill_s`: the cap
  times a registered upper bound on seconds per generated token, plus the time to read the prompt. This is a
  registered **assumption**, not a physical law: the plan assumes no attempt takes longer, and an attempt that does
  has a defined status consequence (it advances a retry stage, and a second excess is a terminal ceiling violation;
  K13 (N)). `reserved_s` is the time the packer sets aside for a block. `ceiling_s` is the per-attempt kill timeout
  the night runner enforces, registered so that worst case ≤ `ceiling_s` ≤ capacity.
- **Overrun, observation, culprit, innocent.** An *overrun* is an envelope ending, or an attempt being killed,
  before all its blocks finish. Each block in that envelope then receives an *observation*: `completed`, `cut_off`
  (started, not finished) or `not_started`, with its elapsed seconds where it ran. A *culprit* is a block whose
  elapsed time exceeded its `predicted_s` (at the single stages, its derived worst case): the block that used up
  the time. An *innocent* block was cut off or never started because a culprit used up the time.
- **Retry stages, terminal states.** Forcing problem: the envelopes have fixed length, and the longest attempts are
  the most expensive, so dropping attempts that overrun would remove exactly the costliest hard problems and bias
  hard-level J/correct downward. So nothing is dropped. A culprit moves through fixed stages: `initial` →
  `whole_block` (the whole block re-run alone in a fresh envelope) → `single_problem` (each problem as its own
  single) → `single_retry` (one more attempt of a single that exceeded its worst case) → `ceiling_violation`. A
  *ceiling violation* is a single that exceeds its derived worst case twice; it shows the registered assumption false
  for that arm, so it is terminal, not a retry path. `unattributed_overrun` is the terminal state for blocks left
  unfinished in an envelope that holds no culprit; under correct instrumentation it cannot occur, so it signals a
  fault. Terminal states are listed in `terminal_refusals`.
- **Voided and counted windows.** A *voided* window belongs to an attempt that a retry superseded; it stays on
  record and is never counted. A *counted* window is one whose energy enters a cell sum.
- **Claims ladder, rung.** The project's claims ladder (`docs/contracts/claims_ladder.md`) ranks claim strength in
  *rungs*: rung L0 capability, rung L1 instrument result, rung L2 comparative result, rung L3 model fit, rung L4
  generalized finding. Rung L2 requires "n ≥ 5 per condition", strict-valid bundles (below), confidence intervals,
  and an effect clearing the detection floor. This file always writes "rung L2" to avoid confusion with MATH
  Level 2.
- **Bundle, strict-valid, replacement rule.** A *bundle* is the directory of raw artifacts one capture produces
  (`docs/contracts/run_bundle_layout.md`). *Strict-valid* means the bundle passes that contract's strict reduction
  checks. A technically invalid bundle is re-run under the pre-declared *replacement rule*; a replacement is not a
  top-up (D-062).
- **Spread, M8.** A cell's *spread* is the number of its parent blocks and the number of distinct envelopes holding
  their counted windows. Forcing problem: blocks inside one envelope share its temperature and background load, so
  they are not independent energy measurements; independent replicates need separate envelopes. M8 (record 19)
  meets rung L2's "n ≥ 5" by requiring at least five parents in at least five distinct envelopes per cell.
- **Position, drift lever, drift threshold.** Forcing problem: the machine's power drifts slowly across a night. If
  one model's blocks sit systematically later, drift biases the ratio between models. A parent's *position* is the
  item-weighted mean envelope index of its counted windows. The *drift lever* of a level is the absolute difference
  between the mean position of its 8B parents and that of its 1.7B parents, in envelope slots. If a block's energy
  shifts by at most δ_upper joules per slot of position, a model's cell sum over P parents shifts by at most
  δ_upper × P × (its mean position), so the between-model bias is at most δ_upper × P × lever. Holding that below a
  registered budget `budget_j` gives the threshold `max_gap = budget_j / (δ_upper · P)`. The packer aims for lever
  0; a roster is accepted if lever ≤ `max_gap`.
- **Recapture.** A registered re-measurement on a later census-clean night, allowed only where a rule names it.

**Estimation.**

- **J/correct, R_L, factors.** A cell's *J/correct* is its summed gross block energy divided by its number of
  correct attempts. It factors exactly as J/correct = J/token × tokens/attempt ÷ accuracy (J/token = cell energy ÷
  cell generated tokens; tokens/attempt = generated tokens ÷ n, with n the problems per cell; accuracy = correct ÷
  n). *R_L* = J/correct(8B) ÷ J/correct(1.7B) at level L in one arm. R_L < 1 means the 8B spent fewer joules per
  correct answer on that level's problems. R(E₈, E₁.₇) below means this ratio computed from the two models' energies
  E₈ and E₁.₇ with the correct counts held fixed; these E symbols are energies, not the status codes E8/E1 defined
  later.
- **Bootstrap, replicate, low and high side, interval.** The *bootstrap* estimates sampling uncertainty by
  redrawing, with replacement, from the observed parent blocks and problems many times (B = 20,000); each redraw is
  a *replicate*. Each replicate yields a *low-side* ratio (energies moved by the instrument bound in the direction
  that makes the 8B look cheapest) and a *high-side* ratio (moved the other way). A replicate whose 8B draw has zero
  correct answers has ratio +∞; one whose 1.7B draw has zero has ratio 0; zero for both is *undefined*. The
  *interval* runs from the 2.5th percentile of the low-side ratios to the 97.5th percentile of the high-side ratios
  (K11). Its ends are written `lo` and `hi`.
- **p_below, p_above, p_L.** `p_below` = (1 + the number of replicates whose high-side ratio is ≥ 1 or undefined) ÷
  (B + 1): small when nearly every replicate says the 8B is cheaper. `p_above` = (1 + the number of replicates whose
  low-side ratio is ≤ 1 or undefined) ÷ (B + 1). `p_L = min(1, 2·min(p_below, p_above))` is the two-sided p-value
  for level L.
- **Holm, family, primary, secondary.** Forcing problem: testing five levels gives five chances of a false finding.
  A *family* is the fixed set of hypotheses tested together: one family per arm, five hypotheses "R_L = 1". *Holm's
  procedure* keeps the chance of any false rejection in a family at or below α (0.05). With m = 5: sort the
  family's p-values ascending as p(1) ≤ … ≤ p(m); reject the k-th while p(k) ≤ α/(m − k + 1); stop at the first
  failure. The thinking-on family is *primary* (it alone can carry the headline); thinking-off is *secondary*.
- **Sparse, merge, group, pooled.** A level is *sparse* in an arm when either model fails the denominator guard
  there (K9). A sparse level is *merged* with a neighbour in a fixed order (§2.4), decided on correct counts only.
  The result is a set of *groups*: single levels or merged runs such as "4–5". A merged group is tested as one
  hypothesis; its constituent levels are *pooled* and each carries `pooled_in` (the group's levels).
- **Group status.** Each tested group gets one of four statuses: *8B cheaper* (code E8, letter `8`), *1.7B cheaper*
  (E1, letter `1`), *not resolved* (NR, letter `n`: the evidence does not settle the direction; inconclusive, not a
  null), or *not estimable* (NE, letter `e`: no ratio can be computed, with a reason such as `sparse_after_merges`
  or `ceiling_violation`). A pooled constituent of an estimable group carries letter `p`. `interval_disagrees` flags
  a group whose Holm test rejected but whose interval still contains 1; such a group is NR.
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
  selection and never replaces the primary estimate.
- **spread_exceeded, drift_exceeded.** Flags that a cell lost its minimum spread after capture, or that a level's
  executed drift lever exceeded `max_gap`; each makes the level NR until a registered recapture.

### 2.2 Analysis procedure, from raw rows to a per-level verdict

Run once per arm. Each step names the clause that governs it; a step that cannot run until an open item is ruled
says so.

1. **Label attempts.** capped := generated tokens ≥ the arm's cap; the row's `stop_reason` must agree (end token vs
   "length") or the reducer refuses the row. correct := scorer match and not capped; malformed := incorrect (K3).
2. **Select counted windows.** Exclude voided windows. A terminal `ceiling_violation` attempt's window is recorded
   but never enters a cell sum (K17). Refuse any block window at or below the floor (row, Floor gate). *Cannot run
   until O-12 names the floor value for block windows.*
3. **Form each parent's energy per model.** g = the sum of the parent's counted windows for that model; k = the
   number of those windows (1 for an unsplit parent; the number of counted singles for a split parent). Pairing is on
   the parent (K13 (a)).
4. **Spread check per cell.** At least five parents with every item counted, in at least five distinct envelopes;
   else `spread_exceeded` (K15). Before capture the same shortfall is a packing refusal.
5. **Drift check per level.** Compute positions and the lever (K12); compare with `max_gap`; excess ⇒
   NR(`drift_exceeded`). *Cannot run until O-7 fixes δ_upper and budget_j.*
6. **Denominator guard and merge.** Apply the guard (K9) per model per level; merge sparse levels in the fixed order
   (§2.4, S2 `merge`); a group still failing is NE(`sparse_after_merges`). *The guard's exact reading is O-2.*
7. **Point estimate per tested group.** R = (Σ E_8B ÷ Σ correct_8B) ÷ (Σ E_1.7B ÷ Σ correct_1.7B) over the
   group's levels; point bounds with U = Σ k·(floor_j + anchor_j) per model (K11).
8. **Bootstrap, B = 20,000.** Per replicate: draw parents within each level of the group, then problems within each
   drawn parent, both paired across models; scale each drawn parent's energy by the model's own drawn-token share s;
   add bound u = k·(floor_j + anchor_j)·s; form the low-side and high-side ratios (K10, K11; worked in §2.5). *The
   two-stage draw is proposed text pending O-4.*
9. **p-values** p_below, p_above, p_L (§2.1).
10. **Holm**, m = 5, over the tested groups; NE groups are not tested and m stays 5 (K9, S2). *Whether a level
    already forced NR by `spread_exceeded` or `drift_exceeded` still contributes its p-value to the sort is not
    settled by any source (O-5). It matters: with m fixed at 5, a flag-forced level with a small p-value that stays
    in the sort takes the strictest threshold α/5 and lets the levels after it be compared against the looser α/4,
    α/3, …; removing it makes each of those comparisons one step stricter, which can turn a rejection into NR.*
11. **Interval** per group: 2.5th percentile of replicate low-side ratios to 97.5th percentile of high-side ratios
    (K11). *Whether point bounds widen the ends is O-4.*
12. **Group status** by the three-way test (S2); then flags: NE(`ceiling_violation`) takes precedence over
    `spread_exceeded` (K16); `drift_exceeded` ⇒ NR (its rank is O-7).
13. **Level statuses** (S9), **pattern and L\*** (S2 `classify`, checked against the S11 table). A ceiling violation
    anywhere in the family withholds L\* (S7) until one recapture (S8).
14. **Sensitivity pass.** Repeat 7–13 with retried items removed for both models; if any Holm direction or L\*
    changes, that claim is reported unresolved until a balanced recapture (K13 (d)).
15. **Labels and sentences.** Cap-bound label per cell (K3); claim sentence from S3, S6, S10 and the proposed
    template in S6 (O-3); three factors and gross energy displayed beside every J/correct (§4 ruling (3)).

### 2.3 Worked example: one level (planning figures, unmeasured)

Packet C's planning stand-ins come from `docs/research_question_bank.md:1615-1616`: about 47 J (1.5B) and 192 J (7B)
per 512 decoded tokens, i.e. 47 ÷ 512 ≈ 0.092 J/token and 192 ÷ 512 = 0.375 J/token. They are not measurements.

*One level.* Thinking on, Level 5, n = 64. The 1.7B spends 0.092 J/token × 4,000 tokens/attempt = 368 J per attempt,
64 × 368 = 23,552 J per cell, and gets 16 correct (25 %): 1,472 J/correct. The 8B spends 0.375 × 2,500 = 937.5 J
per attempt, 60,000 J per cell, and gets 40 correct (62.5 %): 1,500 J/correct. R_5 = 1,500 ÷ 1,472 = 1.019. The 8B
needed an accuracy ratio of (0.375 ÷ 0.092) × (2,500 ÷ 4,000) = 2.55 to break even and achieved 0.625 ÷ 0.25 = 2.50.

*Spread.* Five parents of 13, 13, 13, 13 and 12 problems, the same membership for both models, each in its own
envelope: M8 holds.

*Instrument bound.* With `floor_j` = 1 J and, for illustration only, `anchor_j` = 1 J, each model's point bound is
U = 5 parents × 1 window × 2 J = 10 J, giving point bounds 1.0184 and 1.0196 around 1.0190.

*Sampling spread.* Record 18 gives the planning interval as "×/÷ 1.59" at n = 64: the interval runs from the point
value ÷ 1.59 to the point value × 1.59, here [0.64, 1.62]. It comes from the binomial spread of the two accuracies
on a log scale: SE² ≈ (1 − 0.25)/(64 × 0.25) + (1 − 0.625)/(64 × 0.625) = 0.0469 + 0.0094 = 0.0563, SE = 0.237,
and e^(1.96 × 0.237) = 1.59; at n = 128, SE = 0.168 and the factor is 1.39. Token variance widens both further. The
sampling spread exceeds the instrument bound by more than two orders of magnitude; this level would be NR.

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
sparse Level 2 alone joins 1 (record 20 Q2, adopted by 21/10 §Q1; record 11 M3).

*Numbers (illustrative, n = 64 per level; guard read as an observed count ≥ 3, pending O-2).* Correct counts by
level 1–5: 8B 30, 25, 14, 6, 2; 1.7B 20, 12, 5, 2, 1. Levels 4 (1.7B has 2) and 5 (8B 2, 1.7B 1) are sparse, so 4
and 5 join: group "4–5" has 8B 8 and 1.7B 3, passing, so it stops. Levels 1–3 pass. Partition: 1 | 2 | 3 | 45.

### 2.5 Worked example: one bootstrap replicate (illustrative numbers)

Why two tiers: energy is measured per parent block, correctness per problem, so the resampling must redraw parents
(the energy replicates) and, inside each, problems (the correctness replicates), pairing both across models. Why the
share s: a replicate that redraws a parent's problems carries that parent's energy in proportion to the tokens the
drawn problems generated for that model; the instrument bound is scaled the same way.

A toy level with three parents (A, B, C) of three problems each. `floor_j + anchor_j` = 2 J; each parent is one
window (k = 1).

| Parent | 8B tokens per problem | 8B correct | 8B g (J) | 1.7B tokens per problem | 1.7B correct | 1.7B g (J) |
|---|---|---|---|---|---|---|
| A | 2000, 2600, 3000 | 1, 1, 0 | 2,850 | 4000, 3600, 4400 | 0, 1, 0 | 1,104 |
| B | 2400, 2200, 2800 | 1, 0, 1 | 2,775 | 3800, 4200, 4000 | 1, 0, 0 | 1,104 |
| C | 2500, 2700, 2300 | 1, 1, 1 | 2,810 | 4100, 3900, 4000 | 0, 1, 1 | 1,100 |

Point estimate: 8B 8,435 J / 7 correct = 1,205 J/correct; 1.7B 3,308 J / 4 = 827 J/correct; R = 1.457.

```
tier 1: draw 3 parents with replacement (same draw for both models)
        observed parents:   A    B    C
        drawn slots:        #1 = B    #2 = C    #3 = B
tier 2: inside each drawn slot, draw 3 problem positions with replacement (same positions for both models)
        #1 (B): positions 1, 1, 3     #2 (C): positions 2, 3, 3     #3 (B): positions 2, 3, 1
per model, per slot:  s = drawn tokens / parent tokens;  e = g * s;  u = k * (floor_j + anchor_j) * s;
                      correct = sum of drawn problems' flags
sum over slots:       E, U, correct  ->  R*, low side, high side
```

Every element: "observed parents" are the level's parent blocks; "drawn slots" are the three draws of tier 1;
"positions" are the problem draws of tier 2 inside the parent drawn for that slot; s, e, u and correct are computed
separately for each model from its own tokens, energy and flags.

| Slot | 8B tokens | s | e (J) | u (J) | correct | 1.7B tokens | s | e (J) | u (J) | correct |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 B (1,1,3) | 7,600 | 1.02703 | 2,850.00 | 2.0541 | 3 | 11,600 | 0.96667 | 1,067.20 | 1.9333 | 2 |
| #2 C (2,3,3) | 7,300 | 0.97333 | 2,735.07 | 1.9467 | 3 | 11,900 | 0.99167 | 1,090.83 | 1.9833 | 3 |
| #3 B (2,3,1) | 7,400 | 1.00000 | 2,775.00 | 2.0000 | 2 | 12,000 | 1.00000 | 1,104.00 | 2.0000 | 1 |
| Sum | | | 8,360.07 | 6.0007 | 8 | | | 3,262.03 | 5.9167 | 6 |

R\* = (8,360.07 ÷ 8) ÷ (3,262.03 ÷ 6) = 1.9221. Low side = ((8,360.07 − 6.0007) ÷ 8) ÷ ((3,262.03 + 5.9167) ÷ 6) =
1.9173. High side = ((8,360.07 + 6.0007) ÷ 8) ÷ ((3,262.03 − 5.9167) ÷ 6) = 1.9270. This replicate adds one to the
`p_below` count (high side ≥ 1) and nothing to the `p_above` count (low side > 1). After 20,000 replicates the
interval's ends are the 2.5th percentile of the low sides and the 97.5th percentile of the high sides.

### 2.6 Worked example: retries, drift and a ceiling violation (illustrative timings, not measured)

Assumed for the drawings: capacity 540 s; derived worst case ≈ 200 s per problem (8,192-token cap × 0.02 s/token
upper bound + 36 s prefill); `ceiling_s` = 360 s; parent P3 holds four Level-5 problems P3.a–P3.d with `predicted_s`
250 s.

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
overrun was observed.

*Drift from panel 1.* At pack time the Level-5 thinking-on parents sit in envelopes 1, 5, 9, 13, 17 for the 8B (mean 9)
and 0, 4, 8, 12, 16 for the 1.7B (mean 8): lever 1.0 slot. After the retry P3's position is (21 × 2 + 22 × 2) ÷ 4 =
21.5; the 1.7B mean becomes (0 + 21.5 + 8 + 12 + 16) ÷ 5 = 11.5; the lever grows to 2.5 slots. *Threshold
(illustrative values, O-7):* δ_upper = 2 J per block per slot, budget_j = 50 J, P = 5 parents per cell give max_gap =
50 ÷ (2 × 5) = 5 slots; 2.5 ≤ 5, so the roster is accepted. The bound on bias is 2 × 5 × 2.5 = 25 J against a 23,552 J
cell (0.1 %).

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
stage" is the innocent path of K13 (N); "terminal refusal" is the `terminal_refusals` entry. *Consequences:* parent
P3 now has an item with no counted window, so the cell (1.7B, thinking on, Level 5) has four complete parents and
carries `spread_exceeded` (K15); the group containing Level 5 is NE(`ceiling_violation`), which takes precedence
(K16); L\* is withheld with reason `ceiling_violation_unresolved` (S7). One recapture is allowed: on a later
census-clean night, P3.a is run once by each model as a single, in adjacent envelopes (this seat reads "adjacent" as
consecutive indices); the night's other blocks for that arm are checked against `s_per_token_upper`; a second
violation makes the withholding final for this registration (S8).

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

Fields follow the AP-5 row in order; five fields marked *(added)* have no AP-5 slot (an editorial choice; record 11
F6 finds no ban on extra fields). Clause references K-n point to §2.9.

| Field | Value |
|---|---|
| Plan ID / RQ consumer | AP-5M / research question RQ-NEXT-EPCA-LEVELS (energy per correct answer vs published difficulty), headline: MATH author-level energy per correct answer, Qwen3 1.7B vs 8B (D-166 dated addendum, §4, proposed). |
| family_id | FAM-MATHLVL-EPC-THINKON (primary); FAM-MATHLVL-EPC-THINKOFF (secondary). The registration field `arm_to_family` derives the family from the arm. |
| claim_role | Thinking-on R_L: primary. Thinking-off R_L: secondary; it cannot carry the crossover headline. |
| Estimand *(added)* | For each arm and level L, R_L on the frozen problem set (K1), this machine (M3 Max), pinned weights, prompt template, scorer and extractor, the arm's cap, and the decoding rule Ed fixes under E3 (O-19). The headline quantity is the thinking-on crossover level L\*, which exists only where §3 licenses it. |
| selection_scope | Problem set K1; Qwen3 1.7B and 8B; two arms; levels 1–5; the same problems for both models and both arms; pinned template, scorer, extractor and caps (K3). Nothing else is searched. |
| multiplicity_rule | Holm within each family, α = 0.05 two-sided, m = 5 fixed (one hypothesis R_L = 1 per level; a merged cell tests one hypothesis and m stays 5). Holm: sort p ascending; reject the k-th while p(k) ≤ α/(m−k+1); stop at the first failure. A not-estimable group is not tested and m stays 5; flag-forced NR levels: O-5. |
| Metric + exact window class | Gross block energy (K4) summed per cell; J/correct; the three factors, descriptive only (K5); capped and malformed counts; the cap-bound label (K3). Window class: block window, gross. |
| Capture unit *(added)* | The envelope, one model loaded, one thinking arm per night; the block window inside it; the parent block as the energy replicate (the unit treated as an independent energy measurement); idle slots captured, never divided into a result (K6). |
| Unit of analysis + dependence structure | Problem for correctness and tokens (distinct problems, D-047.3: token and correctness statistics are over distinct items; repeated captures replicate energy only); parent block for energy. Spread K7; retry tails K8. |
| Estimator/formula | R_L with the paired, block-aware bootstrap and share-scaled instrument bound (K10, K11); status by the three-way test (§3 S2). |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only; a bundle contaminated by outside machine activity is re-run under the replacement rule, not waived. The pre-campaign smoke gate K21 (proposed, O-11). Capped = incorrect (K3); malformed = incorrect (D-047.6). Terminal-attempt windows K17. Pilot rosters K18. |
| Order/blocking/covariates | The packer aims for equal mean envelope position per cell across models (the objective); a roster is accepted if the drift lever ≤ `max_gap` (the registered tolerance), and an executed excess makes the level NR (K6, K12). The idle reference (idle-slot energy) is recorded and reported beside results; no registered computation adjusts R_L by it (O-13). |
| Floor gate | Every block window above `max(floor_abs_j, floor_cmp_j)` for the block-window class; the estimator refuses a block window at or below the floor. No block-window floor artifact exists yet (O-12). |
| MDE/n sizing + predeclared top-up rule | n per level ∈ {64, 128}, equal across levels, models and arms, chosen mechanically by K2 (c) and frozen before any test problem runs (D-062). No top-up. Planning intervals ×/÷ 1.59 at n = 64 and ×/÷ 1.39 at n = 128 (§2.3). |
| Denominator provenance requirement | Runtime-observed generated tokens including thinking tokens; exact scorer output with `scorer_id` on every row; `stop_reason` on every row (K3); the AP-5 denominator guard per model per level (K9), else the merge order, else `not estimable`. |
| Sparse-level merge order *(added)* | K9 and §2.4. |
| Holdout cells (ladder rung L3 only) | not applicable. |
| Retry and overrun rules *(added)* | K13 (M12 as amended), K14–K16, K8. |
| Status vocabulary *(added)* | §3 in full. Ruled constants K19. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 on this frozen set, stack and caps. Forbidden: intelligence-per-joule; "difficulty causes energy"; any capability, ranking or routing claim; extrapolation beyond levels 1–5, these two models, or these caps. K20. |
| Disqualifiers + not-resolvable conditions | Below-floor blocks (refused); a packing shortfall of the five-parent or five-envelope minimum (refused); `not estimable` after all merges; any interval containing 1, any `interval_disagrees`, `spread_exceeded` or `drift_exceeded` prints `not resolved`; a ceiling violation withholds L\* (S7, S8); an unattributed overrun leaves its cell unresolved until a registered recapture (K13); a non-claim-ready roster is refused (K18). |
| Linked manifests/bundle hashes | pending post-execution. |

### 2.9 Clauses referenced by the row

**K1 — problem set (ADAPTED from 19 §1 M1 and its addendum; the draw is the merged importer's, O-15).**
*Population.* `test.jsonl` plus the `test/`-tagged rows of `train.jsonl` at `openai/prm800k` commit `7ecc7947`:
5,001 rows. Excluded: both rows of the one duplicated id (2); references that are not a single rational number
(954); and references containing a plain comma (5). *Rational* means the reference, after removing TeX spacing,
dollar signs, a trailing degree or percent sign, a unit word and a leading "x =", parses as an integer, decimal,
grouped integer, a/b, or `\frac{a}{b}`: `5`, `-\frac{3}{4}`, `0.25` and `10\%` qualify; `\sqrt{2}`, `3\pi` and `(1,2)`
do not. A *plain-comma* reference such as `1,000` is excluded because the comma could separate thousands or list two
answers. Eligible: 5,001 − 2 − 954 − 5 = 4,040, by level 381/437, 733/894, 924/1130, 967/1214, 1035/1324 of the
non-duplicate rows (retention 0.872 at Level 1 falling to 0.782 at Level 5). Every eligible reference must equal the
parsed last boxed answer of its own worked solution, or the import refuses.
*Draw.* Each eligible problem gets a key = sha256 of a fixed domain string and the problem's content hash. Within a
level, problems are queued by subject (MATH's seven subject labels), each queue sorted by key; rounds take one
problem from each subject in turn, each round ordered by key ("balanced by subject" means this round-robin). The
pilot takes the first 16 per level under the pilot domain string; the test set takes the first n per level of the
remaining problems under a different domain string. The same problem ids serve both models and both arms. Source:
`joulewise/benchmark_import_math.py` (`eligible_records`, `select_pilot`, `select_items`) at `a53a6b97`, gated by the
cold ruling of record 40, activation 1d3796d5. Publication of problem text is Ed's E1 decision (O-20).

**K2 — sizing pilot: what it may set, and how n is chosen.**

> Caps, block size, envelope pitch, n per level (64 or 128, by a registered rule), and scorer additions (additions only, with a scorer-id bump). **Never** which levels are reported (D-062).

*Source: 19 §1 M5. VERBATIM.* The registered rule for n:

> **Fixed n and pilot.** A 16-problem sizing pilot, disjoint from test problems, never reported as a result, may set only
> (a) problems per bundle, (b) each arm's cap from a declared ladder, (c) n = 128 if the pilot-projected capture for
> the arm at 128 fits the registered window budget, else 64. It never sets which levels, models, arms, families or
> estimands are reported (D-062). All five levels are always reported.

*Source: C §3. VERBATIM.* ("16-problem" means 16 per level, 80 in all, per M4.) The "declared ladder" is a list of
candidate cap values and the "registered window budget" a number of nights; neither is yet stated (O-14). Ed's E4
decision is whether that budget is acceptable (O-18).

**K3 — caps, capped attempts, cap-bound.**

> Every attempt that hits the cap counts as incorrect, even when a boxed answer parses. The parsed text is kept for a sensitivity analysis.

*Source: 19 §1 M2. VERBATIM.* In the next carry, "disagreement refuses" means that a row whose `stop_reason`
disagrees with the token-count test is refused by the reducer (the program that turns rows into cell sums).

> capped := generated_tokens ≥ Registration.cap_tokens[arm]; stop_reason required on every row; disagreement refuses.

*Source: 21/11 R9. VERBATIM.*

> A cell with more than 20 % capped attempts is labelled cap-bound. The cap per arm is the smaller of two values: the cap-ladder rung that covers the pilot's Level-5 1.7B 95th-percentile length, and B's physical ceiling (cap × s/token + prefill ≤ 450 s).

*Source: 19 §1 M3. VERBATIM.* ("B" is packet B, the scored-night design, record 09 of activation 1d3796d5.)

> **Cap-bound label.** A cell with > 20 % truncated attempts is *cap-bound*. The label prints beside every number
> from that cell. If L\* rests on a cap-bound cell, the crossover sentence must state the cap ("at an N-token cap").

*Source: C §3. VERBATIM.*

**K4 — energy numerator.** "Peer number" below means a result reported as an equal alternative.

> Gross energy between the outer item edges of each block. Net-of-idle is never a peer number; the idle reference is a covariate.

*Source: 19 §1 M7. VERBATIM.* No source says how the covariate is used; this draft records and reports it only
(O-13).

**K5 — J/token.** Descriptive only (19 §1 M10, VERBATIM "Descriptive only."). J/token and tokens/attempt are reported
beside J/correct and never carry a claim-bearing contrast (D-045.7: no token-normalized claim metrics).

**K6 — capture unit, idle slots, ordering.**

> An empty slot is captured as a full-length envelope with its model worker loaded and idle, and is labelled `kind: "idle_slot"` in the roster. It never enters any numerator (M7). It may be used as a covariate.

*Source: 08 F1. VERBATIM.*

> Drift cancels in a per-level ratio only when each model's measured blocks share the mean envelope index; `idle_slot` captured, never a numerator.

*Source: 21/10 §Q4 F1. VERBATIM.* Round-1 ruling 08 F1 made "equal mean envelope index per cell across the two
models" the packer's ordering invariant; gate 21 D5b (K12) later registered a tolerance. In plain words: equality is
what the packer aims for, and `lever ≤ max_gap` is what a roster must satisfy (record 11 M4). 08 F1 also dropped packet
C's rotated level order and A-B-B-A model order as requirements ("The palindrome is kept only if the balance search
wants it").

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

**K9 — denominator guard, merge order, multiplicity.** The operative guard is AP-5's, carried unchanged (magistrate
ruling B1 for version 2):

> Exact scorer output plus emitted-token/stop-reason audit; binomial lower-bound must be >=3 correct per level, else merge adjacent levels or report `not estimable`.

*Source: `docs/contracts/analysis_plans.md:274`, AP-5 "Denominator provenance requirement" field. VERBATIM.* In
AP-5M it applies per model per level: a level fails if either model fails. The words "binomial lower-bound" are not
defined in AP-5; the project's AP-5 design note reads the guard as an observed count ("the >= 3-correct binomial
guard is a deterministic property of the item set", `docs/phase_2/suite_implementation_research.md:464`), and packet
C and the gate-21-adopted `merge` rule (S2) use the observed count ≥ 3. Whether AP-5M adopts that reading, or means a
statistical lower confidence bound, is O-2. Packet C's proposed text, carried for the gate as a proposed change, not
as operative text:

> **Minimum correct and merge order.** Each cell needs ≥ 3 correct (AP-5 guard; an observed count, a deterministic
> property of the set). If either model fails at a level in an arm, that level merges for both models, in that arm only,
> in this fixed order: 5 into 4 ("4–5"), then into 3; 1 into 2 ("1–2"), then into 3. Merges depend only on correct
> counts, never on energy or R. If no valid merge remains, the result is `not estimable`.

*Source: C §3. VERBATIM.* The merge order itself is S2's `merge` (settled; §2.4).

**K10 — bootstrap draw (PROPOSED text, ADAPTED; O-4).** B = 20,000 replicates, seed pinned in the registration
(packet C §3). In each replicate, within each level of the group, draw as many parent blocks as the level has, with
replacement, using the same draw for both models; within each drawn parent, draw as many problems as it holds, with
replacement, using the same positions for both models. A drawn problem contributes its model's correct flag and
tokens; a drawn parent contributes its gross energy g times the model's own drawn-token share s (the drawn problems'
generated tokens ÷ the parent's generated tokens for that model; equal shares if the parent generated zero tokens).
The draft estimator does this with Python's `random.Random(seed)` and linear interpolation between order statistics
for percentiles (`d2f9a273:joulewise/energy_per_correct.py`, `ratio_interval`); these are proposed, not ruled.

> Bootstrap over paired problems **and** over capture blocks (block-aware), widened by the instrument's floor and anchor bounds. Holm is applied in two families of m = 5 (thinking-on primary; thinking-off secondary and unable to carry the headline). The crossover level L\* is defined only on Holm-significant directions.

*Source: 19 §1 M9. VERBATIM.*

**K11 — instrument bound and interval.** In the carry, `:60-65` names the share computation in the draft
estimator (K10 gives it in words), and k is the number of counted windows composing the parent for that model.

> per replicate, per drawn block and model, `u = k·(floor_j + anchor_j)·s`, with `k` the block's measured windows for that model and `s` the drawn-token share used at `:60-65`; point bounds keep `s = 1`.

*Source: 21/10 §Q2 D5a. VERBATIM.* In the next carry, E₈ and E₁.₇ are each model's replicate energy and U₈, U₁.₇ its
summed bound.

> U_m = Σ u. Low bound R(E₈ − U₈, E₁.₇ + U₁.₇), high R(E₈ + U₈, E₁.₇ − U₁.₇); point bounds use s = 1.

*Source: 20 §Q5(a), adopted by 21/10 D5a ("AFFIRM Opus's share-scaled bound"). VERBATIM.* The operative interval
(magistrate ruling B2 for version 2):

> (6) The reported interval runs
> from the 2.5th percentile of the low-side values to the 97.5th percentile of the high-side values.

*Source: C §3, step 6. VERBATIM.* Whether the point bounds also widen the ends is O-4.

**K12 — drift lever and threshold.**

> The drift lever of a level is the absolute difference, in envelope slots, between the mean position of its 8B parents and the mean position of its 1.7B parents. A parent's position is the item-weighted mean of the envelope indices of its executed windows: each item contributes the index of the envelope in which its counted attempt was captured. Voided attempts and idle slots contribute nothing. At pack time every item of a parent sits in one envelope, so its position is that envelope's index.

*Source: 45/10 §Q4. VERBATIM.* In the next carry, δ_upper and budget_j are as in §2.1, and `requeue_overrun` is the
packer function that applies K13 after an overrun.

> register `δ_upper` in joules per block per slot and `budget_j` as the per-cell absolute bias budget with its derivation; `max_gap` follows. `requeue_overrun` recomputes `drift_lever_slots`.

*Source: 21/10 §Q2 D5b. VERBATIM.* The formula is `max_gap = budget_j / (δ_upper · blocks_per_cell)` (21/00 D5(b));
this draft reads `blocks_per_cell` as parent blocks per cell per model, matching the parent unit of 45/10 §Q4 (O-7).
The derivation is in §2.1 and a worked threshold in §2.6. "Balanced recapture" below means re-measuring both
models' affected problems at matched positions.

> If the executed roster's gap exceeds max for a level, that level's status is NR(`drift_exceeded`) pending a balanced recapture.

*Source: 21/11 R11. VERBATIM.*

**K13 — overruns and retries (M12 as amended).** Lead-in glossary for the carries: a *pure module* is a program
component that only computes outputs from inputs; `_seal` is the packer's single validating exit; the *runner lane*
is the work item building the night runner (the program that executes a night); "Opus B2/S5/S6" and "(Sol)" are
finding identifiers from the round-1 reviews.

> A block that overruns is re-queued once within the night. It is then re-queued as single-problem envelopes, never dropped.

*Source: 19 §1 M12. VERBATIM; amended by 08, 21/10 §Q4 and 45/21 §7 below.*

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

*Source: 08 F2 (a)–(d), affirmed by 21/10 §Q4. VERBATIM.* The 10 %-retried trigger 08 F2(d) left to this lane is
O-8.

**K14 — ceiling violation.** Carried in §3 as S7 (status) and S8 (recapture bound); worked in §2.6 panel 2.

**K15 — spread_exceeded (ADAPTED by ruled substitution).**

> A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them, for any reason after capture (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place). The cell carries `spread_exceeded: true`, its numbers are reported, and its level is not resolved (`spread_exceeded`) until a registered recapture. Before capture the same shortfall is a packing refusal.

*Source: 45/10 §Q4 "spread_exceeded", with its clause replaced as 45/21 §7 (X) orders. Each part VERBATIM; §5 A3.*

**K16 — precedence.** (A281b is the estimator work item, now A293.)

> "When a level carries both NE(`ceiling_violation`) for a group and `spread_exceeded`, NE(`ceiling_violation`) takes precedence in the A281b total table and `spread_exceeded: true` is recorded alongside; a level with `spread_exceeded` and no NE is NR(`spread_exceeded`)."

*Source: 45/21 §7 (P). VERBATIM.*

**K17 — terminal-attempt windows.**

> A window for a terminal ceiling_violation attempt is accepted, recorded on the terminal refusal as `gross_j`, and never enters a cell sum.

*Source: 45/10 §Q5 F3. VERBATIM.*

**K18 — pilot rosters.** `mode = pilot` marks a registration used only for the sizing pilot; a consumer is any
program reading the roster (reducer, estimator or night runner).

> `mode = pilot` objects may emit only rosters flagged `claim_ready: false`; every consumer refuses a non-claim-ready roster outside pilot mode.

*Source: 21/10 §Q2 D4. VERBATIM.*

**K19 — ruled constants.** Levels [1, 2, 3, 4, 5]; merge order per S2 `merge`; denominator guard ≥ 3 per model per
level (reading O-2); Holm m = 5 per family; α = 0.05 two-sided; minimum parent blocks per cell 5; minimum envelopes
per cell 5; cap-bound fraction 0.20; retry stages `initial`, `whole_block`, `single_problem`, `single_retry`,
`ceiling_violation`; B = 20,000. `schema` is the registration's version identifier.

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

**K21 — pre-campaign smoke gate (PROPOSED, for the gate; O-11).** AP-5 requires that an "envelope-validation smoke
gate must pass before any scored campaign" (`analysis_plans.md:270`, VERBATIM fragment). Its defined checks
(`docs/phase_2/suite_implementation_research.md` §3, E1–E4) are all invariance tests across levels: stop reasons,
mean and distribution of emitted tokens, and prompt tokens. Packet C replaces level-invariant length with the
three-factor decomposition, because MATH answers lengthen with level by nature. Proposed: AP-5M keeps a pre-campaign
smoke gate, run as the shakedown night, that must yield strict-valid bundles and record per-level token, stop-reason
and cap-hit distributions as reported descriptors; none of E1–E4 is a pass condition, and E5 (early-stop bias,
advisory) is reported. Record 11 M6 and the magistrate's ruling M6 ask that the gate be kept; since every defined
check is a level-invariance test, what "kept" means is O-11.

### 2.10 Changes from packet C and from version 1

- From C: the problem-only bootstrap gives way to the block-aware draw (K10, proposed) inside C's own interval rule
  (K11); "≥ 5 bundles per cell" gives way to five parents in five envelopes (K7, K8); rotated level order and A-B-B-A
  model order are dropped (08 F1; K6); the crossover definition gives way to the gate-21 table (§3); population, cap
  and pilot text give way to M1–M5 (K1–K3); the overrun rule gives way to the gate-45 texts (K13–K16); C's observed
  count guard is carried as a proposed change (K9, O-2).
- From version 1: the AP-5 guard is restored as operative (K9); the interval is C's percentile rule, with point-bound
  widening moved to O-4 (K11); the sizing condition is installed (K2); O-2 and O-10 of version 1 are closed as
  settled; the ordering rule is stated as objective plus tolerance (K6, K12); the worst case is an assumption and
  census-clean a reference (§2.1); the smoke gate is added (K21); a procedure (§2.2), a merge example (§2.4), a
  worked replicate (§2.5), a drift threshold and a ceiling-violation panel (§2.6), instrument and floor
  identification (§2.1) and the problem draw (K1) are added.

## 3. Decision-pattern table and status rules

This section decides, for each arm, which groups are 8B cheaper, 1.7B cheaper, not resolved or not estimable,
which pattern the family shows, and whether L\* may be claimed. The adopted vocabulary and procedure are record
20's (21/10 §Q1: "AMEND D2 (adopt, with rulings below)"; D2 was the gate-21 charge's name for this adoption),
amended by the gate-21 cures and the refuter's wording. Every rule is carried; this seat adds the ordering, reading
notes and one proposed sentence (S6).

**S0 — pattern names, in words (from S2 `classify`).** Read the statuses of resolved groups (E8, E1) in level order,
ignoring NR and NE. `crossover`: one or more 1.7B-cheaper groups, then one or more 8B-cheaper groups, one change.
`reverse_order`: 8B-cheaper groups then 1.7B-cheaper groups, one change. `non_monotone`: two or more changes.
`all_1.7B` / `all_8B`: every group resolved and all the same direction. `one_signed_1.7B` / `one_signed_8B`: all
resolved groups the same direction, but some groups unresolved or not estimable. `none_resolved`: no resolved group
and not all NE. `none_estimable`: every group NE. The L\* absent reasons name why no L\* is reported.

**S1 — vocabulary.**

> Group status: `8B cheaper` (E8), `1.7B cheaper` (E1), `not resolved` (NR), `not estimable` (NE, reason `sparse_after_merges` or `ceiling_violation`). Level status: the group status if alone, else `pooled` with `pooled_in`. Pattern: `crossover`, `reverse_order`, `non_monotone`, `all_1.7B`, `all_8B`, `one_signed_1.7B`, `one_signed_8B`, `none_resolved`, `none_estimable`. L\* absent reasons: `boundary_group_pooled`, `reverse_order_not_registered`, `non_monotone`, `no_8B_cheaper_group`, `no_1.7B_cheaper_group`, `none_resolved`, `none_estimable`.

*Source: 20 §Q2, adopted by 21/10 §Q1. VERBATIM.* S9 amends "else `pooled`" for constituents of a not-estimable
group; S7 adds `ceiling_violation_unresolved`; K12 and K15 add `drift_exceeded` and `spread_exceeded` as NR reasons.

**S2 — the three-way direction test.**

> The status rule is: Holm rejects, the direction by p, and the interval lies wholly on that side; otherwise NR with an `interval_disagrees` flag.

*Source: 21/00, lead disposition D2. VERBATIM; affirmed by the next quote.*

> Packet C's terms paragraph ("interval wholly below 1") and §3 ("Holm rejects and p_below < p_above") plus M9 ("only on Holm-significant directions") are satisfied together only by the conjunction; a Holm rejection whose widened interval straddles 1 is NR with `interval_disagrees`.

*Source: 21/10 §Q1, "Status rule (three-way conjunction): AFFIRM". VERBATIM.*

Operational form (record 20 §Q2 pseudocode, adopted with D2; VERBATIM). Reading notes: `c8`, `c17` are per-level
correct counts; `join` merges groups; in `holm`, `rank` counts from 0, so the first comparison is against α/5; `lo`,
`hi` are the interval's ends; the `< 3` in `sparse` is the denominator guard read as an observed count (O-2); the
`gap_levels` line is amended by S6.

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

**PROPOSED combined sentence (this seat's drafting, for the gate; O-3).** Template, with every part optional except
the first:

"On this frozen MATH set (arm, cap), the cheaper model per correct answer changed from 1.7B **[at Level a | on
pooled Levels a–b]** to 8B **[at Level L\* | between Levels b and L\*]**; **[Level(s) … not resolved]**; **[Level(s)
… not estimable]**."

Rules: use "at Level L\*" when no bracket gap exists, else "between Levels b and L\*" with b the highest level of the
licensing group; list every gap level (bracket and outside), NR levels under "not resolved" and NE levels under "not
estimable"; a pooled boundary group gives no L\* (S3). Examples: `1nn8n` → "changed from 1.7B at Level 1 to 8B
between Levels 1 and 4; Levels 2, 3 and 5 not resolved." `12|3|4|5` with `1n88` (levels `ppn88`) → "changed from 1.7B
on pooled Levels 1–2 to 8B between Levels 2 and 4; Level 3 not resolved." `11e88` → "changed from 1.7B at Level 2 to
8B between Levels 2 and 4; Level 3 not estimable."

**S7 — ceiling-violation null.**

> When any item in the family carries a terminal `ceiling_violation`, its group is NE(`ceiling_violation`), every other group is classified and printed, and `crossover_level` is null with reason `ceiling_violation_unresolved` until a registered recapture resolves the item. Pairwise exclusion of the item appears only in the labelled selection-confounded sensitivity.

*Source: 21/10 §Q1, Split 3 cure text. VERBATIM.* The ruling's stated reason is disputed by the refuter (O-1).

**S8 — ceiling-violation recapture bound.** In the carry, "census-clean window" means a census-clean night, and
"copies" are the same problem run by each model.

> At most one recapture, on a later census-clean window, both models' copies adjacent as singles; the night's other blocks for that arm are checked against s_per_token_upper; a second violation makes `ceiling_violation_unresolved` terminal for the family under this registration.

*Source: 21/11 R6 cure. VERBATIM.* Worked in §2.6 panel 2. The consequence of a failed check on the night's other
blocks is O-9.

**S9 — constituents of merged groups.**

> Constituents of an estimable merged group get `pooled` + `pooled_in`. Constituents of an NE merged group get `not estimable` + `pooled_in` + the NE reason.

*Source: 21/11 R7. VERBATIM.*

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
> recapture resolves it.
>
> **Status.** Proposed. A cold gate reviews this text; Ed adopts or rejects it under E2 (Gmail
> `1a0d069e15a52ba9`). Until then it binds nothing.
>
> Gate records:
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md`;
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/11-opus-contract-refuter.md`;
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md`;
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md`;
> draft `docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md`; the AP-5M cold-gate ruling
> (pending).

Forcing problem and ruling (1)–(5): C §2a VERBATIM. Terms and worked example: C §2a ADAPTED. Ruling (6): 19 M7
ADAPTED. Ruling (7): the A282 queue row ADAPTED. Ruling (8): this seat's summary of K13 and S7–S8. Matching edits
elsewhere follow packet C §6, except that its `claims_ladder.md:63` entry reads "five parent blocks in five envelopes
(M8)" and its `research_question_bank.md:1728-1738` entry uses n ∈ {64, 128} from K2.

## 5. Provenance

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
| 14 | "Exact scorer output plus emitted-token/stop-reason audit; binomial lower-bound…" | K9 | analysis_plans.md:274 | VERBATIM |
| 15 | "**Minimum correct and merge order.**…" (proposed change) | K9 | C §3 | VERBATIM |
| 16 | "Bootstrap over paired problems **and** over capture blocks…" | K10 | 19 §1 M9 | VERBATIM |
| 17 | "per replicate, per drawn block and model, `u = k·(floor_j + anchor_j)·s`…" | K11 | 21/10 §Q2 D5a | VERBATIM |
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
| 40 | "envelope-validation smoke gate must pass before any scored campaign" | K21 | analysis_plans.md:270 | VERBATIM fragment |
| 41 | "Group status: `8B cheaper` (E8)…" | S1 | 20 §Q2 | VERBATIM |
| 42 | "The status rule is: Holm rejects, the direction by p…" | S2 | 21/00 D2 | VERBATIM |
| 43 | "Packet C's terms paragraph… widened interval straddles 1…" | S2 | 21/10 §Q1 | VERBATIM |
| 44 | merge/holm/status/classify pseudocode | S2 | 20 §Q2 | VERBATIM |
| 45 | "A merged group may license L\* only as a region statement…" | S3 | 21/10 §Q1 Split 1 | VERBATIM |
| 46 | "Pattern `reverse_order`, reason `reverse_order_not_registered`…" | S4 | 21/10 §Q1 Split 2 | VERBATIM |
| 47 | "(b) `reverse_order` is any resolved sequence matching `8+1+`…" | S4 | 21/10 §Q1 (b) | VERBATIM |
| 48 | "NIT: non_monotone rows need the reason code `non_monotone`." | S4 | 21/11 R5 | VERBATIM |
| 49 | "**Isolated sparse Level 3: AFFIRM**…" | S5 | 21/10 §Q1 | VERBATIM |
| 50 | "(a) `gap_levels` must list every NR/NE level…" | S6 | 21/10 §Q1 (a) | VERBATIM |
| 51 | "If any level lies strictly between the licensing group…" | S6 | 21/11 R4 | VERBATIM |
| 52 | "NIT: keep `bracket_gap_levels` separate." | S6 | 21/11 R4 | VERBATIM |
| 53 | "When any item in the family carries a terminal `ceiling_violation`…" | S7 | 21/10 §Q1 Split 3 | VERBATIM |
| 54 | "At most one recapture, on a later census-clean window…" | S8 | 21/11 R6 | VERBATIM |
| 55 | "Constituents of an estimable merged group get `pooled`…" | S9 | 21/11 R7 | VERBATIM |
| 56 | "**Null wording.** All levels above 1…" | S10 | C §3 | VERBATIM |
| 57 | "When any group is pooled, the null sentence reads…" | S10 | 21/11 R3 | VERBATIM |
| 58 | Table legend + 26 table rows | S11 | 21/10 §Q1 | VERBATIM |
| 59 | "Thinking-on R_L: primary. Thinking-off R_L: secondary…" | row claim_role | C §2b | VERBATIM |
| 60 | "Holm within each family, α = 0.05 two-sided, m = 5 fixed…" | row multiplicity | C §2b | VERBATIM (first two sentences) |
| 61 | "Ceiling L2 on this frozen set, stack and caps. Forbidden: …" | row ceiling | C §2b | VERBATIM |
| 62 | D-166 forcing problem and ruling (1)–(5) | §4 | C §2a | VERBATIM |
| 63 | R6 dissent "Group-level NE is not pairwise exclusion…" | O-1 | 21/11 R6 | faithful excerpt (line breaks differ) |
| 64 | D-166 terms and worked example | §4 | C §2a | ADAPTED (A4) |
| 65 | D-166 ruling (6) | §4 | 19 §1 M7 | ADAPTED (A5) |
| 66 | D-166 ruling (7) | §4 | TASK_QUEUE A282 row | ADAPTED (A6) |
| 67 | K1 population and draw | K1 | 19 §1 M1 + §Addendum; `joulewise/benchmark_import_math.py` | ADAPTED (A1) |
| 68 | K10 two-stage draw | K10 | C §3 step 3; `d2f9a273:joulewise/energy_per_correct.py` | ADAPTED (A2) |

Counts: 61 VERBATIM (rows 1–32, 34–62; row 40 is a fragment, row 60 covers two sentences, the 26-row table and the
pseudocode count once each), 1 faithful excerpt (row 63), 6 ADAPTED (rows 33, 64–68).

**Adaptations, with originals.**

- **A1 (K1).** Original, 19 §1 M1: "The full MATH test split, 5,000 rows = `test.jsonl` plus the `test/`-tagged rows of
  `train.jsonl` at `openai/prm800k` `7ecc7947`. Those rows hold 5,001 lines and 4,999 unique ids. **Both** rows of the
  duplicated id are excluded. Rational-valued answers only. Balanced by subject." Corrected by 19 §Addendum: "5,001
  rows, 5,000 distinct ids before exclusion (one id appears twice), 4,999 singleton ids. Exclusions are both rows of
  the duplicated id (2), 954 non-rational references and 5 plain-comma references. That leaves **5,001 − 2 − 954 − 5 =
  4,040 eligible**". The eligibility predicates, per-level counts and draw are read from the merged importer
  (`canonical_reference_v1`, `plain_comma_ambiguous`, `ELIGIBILITY_NOTE`, `select_pilot`, `select_items`).
- **A2 (K10).** Original, C §3 step 3: "Draw B = 20,000 resamples (seed pinned in the registration). Each draws n
  problem indices with replacement within the level and applies the same indices to both models". M9 requires the
  block level too; K10 describes the draft estimator's two-stage scheme (docstring: "Bootstrap common blocks, then
  paired problems within each drawn block") as proposed text.
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

## 6. Open items

For the cold gate unless marked **Ed**. Each states the question that would close it. Closed since version 1: the
merge of a sparse Level 4 or Level 2 alone (settled by record 20 Q2 as adopted by 21/10 §Q1: 4 joins 5, 2 joins 1),
and the drop of packet C's level and model order (settled by 08 F1).

- **O-1 (refuter dissent, not resolved here).** 21/11 R6 agrees with S7's outcome but disputes its reason. Faithful
  excerpt of R6 (the source's line breaks differ): "Group-level NE is not pairwise exclusion, and the table lets
  count-based NE gaps license L\* (`11e88`, `eee18`), so "a gap there is selection" contradicts it. The operative
  reasons: (i) the censored outcome leaves the count-only merge partition undetermined; (ii) the violation falsifies a
  registered physical bound, a physics/evidence refusal." *Question:* which reason does AP-5M record for withholding
  L\*: the ruling's "a gap there is the selection M12 forbids", the refuter's (i) and (ii), or both?
- **O-2 (denominator guard).** *Question (record 11 B1):* does AP-5M expressly replace AP-5's "binomial lower-bound
  must be >=3 correct" with an observed count ≥ 3 (as packet C, the AP-5 design note at
  `suite_implementation_research.md:464` and the adopted `merge` rule read it), or must a statistical lower bound also
  pass, and if so which bound at which confidence?
- **O-3 (claim sentence).** Settled already: every gap level must be named (21/10 §Q1 (a)). *Question:* adopt the
  proposed template in S6, which names pooled licensing, bracket gaps and all other gaps, and calls an NE gap "not
  estimable" and an NR gap "not resolved"?
- **O-4 (interval).** Settled already: B = 20,000 (C §3) and share-scaled bounds inside each replicate (21/10 D5a).
  *Question (record 11 B2):* are the endpoints the percentiles alone, or `min(point_low, percentile_low)` and
  `max(point_high, percentile_high)`? And is K10's two-stage draw (parents, then problems within each drawn parent),
  with `random.Random(seed)` and linear-interpolation percentiles, adopted as registration text?
- **O-5 (Holm membership).** *Question:* does a level already forced NR by `spread_exceeded` or `drift_exceeded`
  contribute its p-value to the Holm sort, or is it removed like an NE group (with m still 5)?
- **O-6 (spread in merged groups).** *Question:* when one constituent of a merged group is spread-exceeded, is the
  whole group NR(`spread_exceeded`)? Does "until a registered recapture" in K15 and in (W) share S8's one-recapture
  bound?
- **O-7 (drift threshold).** 21/11 R11: no source is named for δ_upper, and the bench token pilot measures no energy.
  *Question:* is δ_upper taken from the shakedown night or from a pinned earlier corpus; what budget_j derivation is
  registered; is `blocks_per_cell` the parent count per cell per model; and where does NR(`drift_exceeded`) rank in
  K16's precedence?
- **O-8 (retry trigger).** 08 F2(d) left this lane a trigger: retried attempts above 10 % of a headline cell ⇒ the
  next night re-measures the other model's copies adjacently. This draft does not adopt it. *Question:* add it, or
  confirm its omission?
- **O-9 (recapture check).** *Question:* if, during the S8 recapture, one of the night's other blocks exceeds
  `s_per_token_upper`, is that a second violation (terminal) or a separate refusal?
- **O-10 (tails across nights).** M12 says "within the night"; (N) places rescheduled singles "into the first later
  envelope … else a fresh one" without a night boundary. *Question:* must a fresh envelope extend the same night, or
  may work continue on another census-clean night, and if so how are envelope indices and the drift lever compared
  across nights?
- **O-11 (smoke gate).** *Question:* AP-5's smoke-gate checks E1–E4 are all level-invariance tests, which MATH fails
  by design; is K21's proposal (a shakedown night yielding strict-valid bundles and reporting per-level token,
  stop-reason and cap-hit distributions, with no invariance pass condition) what AP-5M keeps, or does some named
  check remain a pass condition?
- **O-12 (block-window floor).** Record 18: floors exist only as pending for level windows (`analysis_plans.md:272`);
  none is issued for block windows. *Question:* which floor artifact supplies `max(floor_abs_j, floor_cmp_j)` for the
  block-window class, and does `floor_j` in D5a equal that gate value? Also: the project's single-count rule
  (`detection_floor.md`, "single-count discipline") uses the floor as a gate and the anchor bound as interval
  widening, and calls their sum "only a prospective planning/sizing diagnostic"; D5a puts `floor_j + anchor_j` into
  the widening. Is that intended, or should the widening carry the anchor bound alone with the floor as a separate
  gate?
- **O-13 (idle covariate).** M7 and 08 F1 call the idle reference a covariate without a computation. *Question:*
  report-only (this draft's position), or a registered adjustment?
- **O-14 (registration numbers not yet stated).** Envelope length (600 s in the gate-21 charge vs 480 s slots in
  record 18), the cap-ladder values, the window budget in nights, and the seed. *Question:* these belong to the
  registration packet, not claim policy; confirm AP-5M may leave them to it.
- **O-15 (problem draw).** *Question:* adopt K1's draw (the merged importer's keyed, subject-interleaved selection;
  the same ids for both arms) as AP-5M text?
- **O-16 (editorial).** Keep the five added row fields, or fold them into the standard fields?
- **O-17 (Ed, E2).** Adopt AP-5M and the §4 addendum (after the gate's amendments), amend, or reject. Packet C's
  proposed choices, narrowed since: (1) a sibling row, not a rewrite of AP-5; (2) two Holm families of m = 5, not one
  of m = 10; (3) rung L2's "n ≥ 5" met by five parents in five envelopes, not by amending the ladder; (4) J/token
  descriptive only; (5) capped = incorrect even when an answer parses; (6) the 20 % cap-bound threshold and the
  per-arm cap rule; (8) the residual fit exploratory; (9) claims say "MATH level", and "difficulty" appears only where
  defined.
- **O-18 (Ed, E4).** n per level is chosen mechanically by K2 (c): 128 if the pilot-projected capture fits the
  registered window budget, else 64. Ed's decision is whether the budget is acceptable; planning figures (record 18)
  are about 12 nights for n = 64 and about 23 for n = 128, at 4–5 nights a day.
- **O-19 (Ed, E3).** Decoding: (a) greedy, labelled "under greedy decoding"; (b) the model card's seeded sampling
  (temperature 0.6, top-p 0.95, top-k 20, one pinned seed per problem and model); or (c) thinking-off as primary.
  Recommendation (record 19): (b), with (a) as fallback if seeded sampling does not reproduce the same tokens. The
  estimand is incomplete until this is decided.
- **O-20 (Ed, E1).** Whether the problem text is published. Options: commit only ids and hashes, with the text in an
  untracked "custody path" (a storage location outside the repository whose files are bound by sha256 digests
  recorded in it); or publish the text. Recommendation (record 19): hashes and ids only, because PRM800K's licence
  covers OpenAI's data and probably not the Art of Problem Solving problem text.

## 7. First-use self-check

Method: every term, symbol and code in §1–§6 was listed with its first occurrence and checked against where it is
built or glossed, starting from record 12's 111-row table. Results:

- **Built or glossed before use:** all of record 12's BLOCKER rows (power meter, energy rail, floors, window class,
  P2-015, eligibility predicates, subject balancing, `blocks_per_cell`, interval endpoints) and its MATERIAL rows
  (records and activations, synthesis, item, registration ordering, sizing pilot, claims ladder and rungs, window
  collisions, undefined ratio, `p_above`, "×/÷", `voided_block_ids`, AP-5, forbidden upgrade, quarantine, the cited
  decision codes, energy replicate, problem window, bundle, strict-valid, replacement rule, truncated, envelope
  pitch, disagreement refuses, residual-fit symbols, affine-ladder rules, pattern names, copies, custody path,
  supported switch, idle covariate), and the NIT rows except those listed below.
- **Built only by pointer or by reference, not in full:** census-clean (a reference to the runbook's coded census,
  as ruled); capacity (the draft code's definition `interior_s − guard_s`, whose parts are not further explained);
  cap-ladder rung (its values do not exist yet, O-14); "binomial lower-bound" (undefined in its source, O-2);
  strict validation's list of checks (by reference to `run_bundle_layout.md`).
- **Left as identifiers without explanation:** work-item ids (A281b/A293, A282, A291) and the activation ids in paths;
  the model names Fable, Sol and Opus (used as reviewer identities only); `RQ-NEXT-EPCA-LEVELS` beyond its one-line
  gloss. Every cited decision code (C-004, D-045.7, D-047.3, D-047.6, D-062, D-078, D-166) is glossed at or
  before first use.
