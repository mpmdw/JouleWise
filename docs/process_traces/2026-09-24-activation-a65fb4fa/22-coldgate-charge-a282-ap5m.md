# 22 — Cold-gate charge: A282 AP-5M draft v2 (rulings and dictated texts for v3)

Assembled 2026-09-24 by a charge-assembly seat (an Opus 5.5 subagent that did not write the draft under review) for
activation a65fb4fa. Read-only everywhere except this file.

## 1. Status

**This charge asks for rulings on a proposal. Nothing here is adopted claim policy.** Work item A282 has drafted
"AP-5M", a proposed new row of the project's analysis-plan contract (`docs/contracts/analysis_plans.md`), plus a
dated addendum to decision D-166 (the project's workload decision). AP-5M would govern one experiment: gross joules
per correct answer for two Qwen3 models (1.7B and 8B parameters) across the five difficulty levels of the MATH
benchmark. No measurement for this experiment has been taken, and nothing is armed (no capture is scheduled).

Ed, the project owner, alone decides whether AP-5M is adopted (his decision E2). He also decides E1 (whether the
problem text is published), E3 (the decoding rule and primary thinking mode) and E4 (whether the capture budget is
acceptable). This charge does not ask the judge to decide E1–E4.

**What the judge's rulings bind.** They bind the TEXT of the next draft (v3): a writer installs the judge's dictated
texts verbatim. They do not bind the project's claim policy; that happens only if Ed adopts AP-5M.

**Why a cold gate now.** The draft went from v1 to v2 through one fix round. Two re-reviews of v2 (a source-fidelity
review by the Sol model, record 17, and a teaching-quality review by Opus, record 18) found three BLOCKERs and several
defects that the fix round itself introduced. The project's escalation rule forbids a second self-directed fix round
on the same defect classes; the next step is a ruling. The judge rules each open question below and dictates the
exact replacement text.

**How quotes work in this charge.** Every blockquote is copied byte for byte from the file named under it, at the
stated lines, and was checked by a script. Short keys used below:

| Key | File (relative to the repository root) | What it is |
|---|---|---|
| V2 | `docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md` | The draft under review (1,208 lines). |
| V1 | `docs/process_traces/2026-09-24-activation-a65fb4fa/07-a282-ap5m-draft.md` | Version 1 (history only). |
| R11, R12 | `…/2026-09-24-activation-a65fb4fa/11-a282-fidelity-sol-lens.md`, `…/12-a282-pedagogy-opus-lens.md` | The two reviews of v1 (fidelity by Sol; teaching and replication by Opus). |
| B16 | `…/2026-09-24-activation-a65fb4fa/16-a282-v2-fidelity-delta-brief.md` | The brief for record 17; it summarises the magistrate's v2 revision rulings. |
| R17, R18 | `…/2026-09-24-activation-a65fb4fa/17-a282-v2-fidelity-delta.md`, `…/18-a282-v2-pedagogy-delta.md` | The two re-reviews of v2. |
| C | `docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md` | Packet C, the first design draft of AP-5M. |
| PB | `…/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md` | Packet B, the scored-night design. |
| H18 | `…/2026-09-23-activation-1d3796d5/18-headline-opus-integration.md` | The Opus integration consult (planning arithmetic). |
| S19 | `…/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md` | The integration synthesis: settled items M1–M13 and Ed's decisions E1–E4. |
| M40 | `…/2026-09-23-activation-1d3796d5/40-fable-ruling-math.md` | The cold ruling on the MATH importer and scorer. |
| R08 | `docs/process_traces/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md` | Round-1 rulings on the packer and estimator code. |
| R20 | `…/2026-09-23-activation-d8cc9c0a/20-a281-opus-consult.md` | The Opus consult that wrote the status vocabulary and procedure. |
| G21C, G21, G21R | `…/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/{00-charge, 10-coldgate-fable-ruling, 11-opus-contract-refuter}.md` | Cold gate 21: charge, ruling, paired refuter. |
| G45, G45A | `…/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/{10-coldgate-fable-ruling, 21-coldgate-fable-addendum-ruling}.md` | Cold gate 45: ruling and addendum ruling. |
| AP | `docs/contracts/analysis_plans.md` | The analysis-plan contract; the AP-5 row is lines 258–278. |
| DF | `docs/phase_2/detection_floor.md` | The detection-floor contract. |
| DL | `docs/decision_log.md` | The decision log (D-078, D-079, D-166). |
| SIR | `docs/phase_2/suite_implementation_research.md` | The AP-5 design note; §3 defines the smoke-gate checks. |
| RQB | `docs/research_question_bank.md` | The research-question bank. |
| AG | `docs/paper/artifact-guide.md` | The artifact guide (how energy is reduced from raw samples). |
| IMP | `joulewise/benchmark_import_math.py` | The merged MATH importer. |

Where sources conflict, V2 §1 (lines 39–40) says the later ruling prevails, in the order G45A §7, G45, G21 with G21R,
R08, then C and S19.

## 2. Terms in plain words

Each term below uses only terms defined above it.

**The machine and the models.**

- **Power capture.** The laptop (an Apple M3 Max) reports its own power draw through the macOS program
  `powermetrics`, read every 100 ms. Each reading gives the watts drawn by the chip package (CPU, GPU and neural
  engine) over that 100 ms. Energy in joules is watts times seconds: 30 W held for 10 s is 300 J. The energy of any
  time interval is obtained from the readings that overlap it.
- **Model, thinking mode (arm).** The two models are Qwen3 1.7B and Qwen3 8B, run as fixed 4-bit weights. A
  *thinking mode* (the draft says *arm*) is either *thinking on* (the model writes a long reasoning trace before its
  answer) or *thinking off*. Thinking on is the *primary* arm: only it may carry the headline claim.
- **Problem, level.** A MATH problem is one competition-mathematics question with one reference answer. Its *level*
  is the integer 1–5 that the dataset's authors attached when they published it; nothing in the experiment computes
  it. "Difficulty" in this charge means only this label.
- **Attempt, cap, capped, correct.** An *attempt* is one model's single generation for one problem. The *cap* is a
  fixed maximum number of generated tokens. An attempt that reaches the cap is *capped* and counts as incorrect. An
  attempt is *correct* when a fixed scoring program finds its final answer equal to the reference and it is not
  capped.
- **Cell.** One (model, thinking mode, level) combination, for example (8B, thinking on, Level 5).

**How energy is recorded.**

- **Envelope, envelope index.** An *envelope* is one continuous power recording of fixed length (the sources name
  600 s with a 480 s usable interior; the length is not yet registered) during which exactly one model is loaded.
  Envelopes run back to back on a fixed schedule; the *envelope index* 0, 1, 2, … is an envelope's position in it.
- **Night.** One unattended capture session: a sequence of envelopes. The sources call this a *window*; the draft
  calls it a *night*. Several can run per day.
- **Block, block window, gross energy.** A *block* is a fixed list of problems from one cell, run back to back
  inside one envelope. A timestamp marker is written when the first problem starts and when the last one ends; the
  *block window* is the time between them. The block's *gross energy* is all joules recorded inside the block window,
  with nothing subtracted for the power the machine draws when doing nothing. Energy is never read per problem.
- **Idle slot, idle reference.** An *idle slot* is an envelope recorded with a model loaded and doing nothing, used
  to keep the schedule evenly spaced. Its energy (the *idle reference*) is recorded but never divided into a result.
- **Parent block, single, retry stages.** A *parent block* is a block placed by the initial schedule. If an envelope
  runs out of time before its blocks finish (an *overrun*), the block that used up the time (the *culprit*) is re-run:
  first whole in a fresh envelope, then as one-problem blocks called *singles* (pieces of the parent), then once
  more as a single. A single that exceeds its registered worst-case duration twice is a *ceiling violation*: a
  terminal state, recorded and never counted. Blocks cut off only because a culprit used up the time are
  *innocent* and are rescheduled without advancing.
- **Voided and counted windows.** When a retry supersedes an attempt, that attempt's window is *voided*: kept on
  record, never summed. A *counted* window enters a cell's energy sum.
- **Recapture.** A registered re-measurement on a later night, allowed only where a rule names it.

**Why the schedule has constraints.**

- **Spread minima (M8).** Forcing problem: blocks in one envelope share its temperature and background load, so they
  are not independent measurements. Each cell must therefore hold at least five parent blocks in at least five
  distinct envelopes. A cell that loses this after capture (for example, a parent loses a problem to a ceiling
  violation) carries the flag `spread_exceeded`.
- **Drift, position, drift lever.** Forcing problem: the machine's power drifts slowly over a night (for example, as
  it warms). If one model's blocks sit systematically later, drift biases the comparison. A parent's *position* is
  the mean envelope index of its counted windows (weighted by problems). A level's *drift lever* is the absolute
  difference between the mean position of its 8B parents and that of its 1.7B parents. Example: 8B parents in
  envelopes 1, 5, 9, 13, 17 (mean 9) and 1.7B parents in 0, 4, 8, 12, 16 (mean 8) give a lever of 1 slot. The
  threshold `max_gap = budget_j / (δ_upper · blocks_per_cell)` uses a registered drift rate `δ_upper` (joules per
  block per slot) and a registered bias budget `budget_j` (joules). A level whose executed lever exceeds `max_gap`
  carries `drift_exceeded`.

**The quantity and its uncertainty.**

- **J per correct, R_L.** A cell's *J/correct* is its summed gross block energy divided by its number of correct
  attempts. Example: 23,552 J with 16 correct is 1,472 J/correct. *R_L* is J/correct(8B) ÷ J/correct(1.7B) at level L
  in one thinking mode; R_L < 1 means the 8B spent fewer joules per correct answer.
- **Bootstrap, replicate.** To measure how much R_L would change on another sample of problems, the analysis redraws,
  with replacement, the level's parent blocks and, inside each drawn parent, its problems, the same draw for both
  models, and recomputes the ratio. One redraw is a *replicate*; there are B = 20,000.
- **Instrument floor.** The smallest energy the instrument can tell apart from zero for a given kind of time
  interval (the *window class*: phase, request, level, block …). It is measured by repeating identical workloads.
  The contract names the gate value `max(floor_abs_j, floor_cmp_j)`: the larger of an absolute floor (scatter of
  repeated identical cells) and a comparative floor (scatter of same-condition contrasts). The draft writes
  `floor_j` for the per-window floor value used in the estimator.
- **Anchor bound.** The marker timestamps and the power sampler's clock can be offset by some milliseconds. Shifting
  a window edge by that offset moves energy across the edge. The *anchor bound* `anchor_j` (field
  `E_clock_anchor_shift_bound_j`) is the most energy that can be misassigned this way. Example from D-078: a ±31 ms
  shift where power swings about 33 W misassigns about 1 J. On this machine the anchor term is larger than the
  repeat scatter, so the published floor is labelled *attribution-limited*: its size comes from the anchor term.
- **Widening, low side, high side, interval.** In each replicate the ratio is computed twice: once with the 8B's
  energy lowered and the 1.7B's raised by their bounds (the *low side*, most favourable to the 8B), once the reverse
  (the *high side*). The *interval* runs from the 2.5th percentile of the 20,000 low sides to the 97.5th percentile
  of the high sides.
- **p_below, p_above, p_L.** `p_below` is (1 + the number of replicates whose high side is ≥ 1 or undefined) ÷
  (B + 1); it is small when nearly every replicate says the 8B is cheaper. `p_above` is the mirror. The level's
  two-sided p-value is `p_L = min(1, 2·min(p_below, p_above))`.
- **Holm correction, family.** Forcing problem: testing five levels gives five chances of a false finding. A
  *family* is one thinking mode's five hypotheses "R_L = 1". Holm's procedure sorts the p-values ascending and
  compares the smallest with 0.05/5 = 0.01, the next with 0.05/4 = 0.0125, then 0.0167, 0.025 and 0.05, stopping at
  the first failure. Example: p-values 0.004, 0.011, 0.03, 0.2, 0.5 reject the first two (0.004 ≤ 0.01 and
  0.011 ≤ 0.0125) and stop at the third (0.03 > 0.0167). m, the divisor count, is fixed at 5.
- **Denominator guard, sparse, merge, pooled group.** Forcing problem: J/correct divides by the correct count, so
  with 1 or 2 correct answers one problem changes the ratio by a factor of 2 or 3. A level is *sparse* when either
  model fails the guard ("at least 3 correct", in a reading that is Question 1). A sparse level is *merged* with a
  neighbour in a fixed order (4 and 5 join, 1 and 2 join, then into 3). A merged run such as "4–5" is a *pooled
  group*, tested as one hypothesis.
- **Group statuses.** Each group ends as *8B cheaper* (code E8, letter `8`), *1.7B cheaper* (E1, `1`), *not
  resolved* (NR, `n`: the data do not settle the direction; inconclusive, not a null), or *not estimable* (NE, `e`:
  no ratio can be computed, with a reason such as `sparse_after_merges` or `ceiling_violation`). A constituent of a
  pooled estimable group gets letter `p`. A group is E8 only when Holm rejects, p gives the direction, and the
  interval lies wholly below 1 (the *three-way test*); a Holm rejection whose interval contains 1 is NR with the flag
  `interval_disagrees`. **Name collision:** these status codes E8/E1 are unrelated to Ed's decisions E1–E4 and to
  the smoke-gate checks E1–E5 below.
- **Pattern, crossover level L\*, licensing and boundary groups, gap levels.** Reading resolved groups in level
  order gives a *pattern*, e.g. `11n88`. A *crossover* is 1.7B-cheaper groups followed by 8B-cheaper groups with one
  change. The *boundary group* is the first 8B-cheaper group, the *licensing group* the last 1.7B-cheaper group
  before it, and *L\** the boundary group's level. *Gap levels* are NR or NE levels.

**Process words.**

- **Registration.** The frozen, hashed record of every rule, constant and input fixed before any test problem runs.
- **Sizing pilot, shakedown night.** 16 problems per level, never reported, run on the bench without power capture
  to measure token counts, then one short measured night to check envelope timing.
- **Smoke gate.** A short trial capture that must *pass* before any scored campaign. AP-5's design note defines
  its pass checks E1–E4 (stop-reason, emitted-token mean, emitted-token distribution, prompt-token invariance across
  levels) plus an advisory E5 (early-stop bias: whether wrong answers are systematically shorter). E1–E4 each test
  that something does not change with level.
- **Selection-confounded sensitivity.** A re-analysis that removes retried problems for both models. It removes
  exactly the longest problems, so it is labelled confounded and never replaces the primary result.
- **Seat, record, lens, magistrate, cold gate.** A *seat* is one delegated agent session; a *record* is one
  numbered file of project history; a *lens* is a review from one angle; the *magistrate* runs the project loop and
  cannot adopt claim policy; a *cold gate* is a fresh judge with no loop context (this one).

## 3. Questions

Each question gives the exact question, the candidate readings, the draft's current text, each lens's position, and
the source texts. The charge takes no position.

### Q1 — The denominator guard: observed count or statistical lower bound? (BLOCKER, record 17 F1; open item O-2)

**Question.** In AP-5M, what exactly must hold for a model at a level (or merged group) to pass the "≥ 3 correct"
guard, and is AP-5's wording "binomial lower-bound" amended?

**Candidate readings.** (a) Adopt an observed count: at least 3 correct answers, expressly replacing AP-5's
wording for AP-5M. (b) Keep AP-5's words and define a statistical lower confidence bound on the correct count
(which bound, at which confidence), which must reach 3. (c) Require both.

**Why it matters.** The guard decides which levels merge, and the merge partition decides which hypotheses Holm
tests. With 64 problems, a group with 3 observed correct passes (a); a one-sided 95 % lower bound on 3 successes in
64 trials lies far below 3, so under (b) that group fails and merges further.

**Draft text (V2).**

> - **Sparse, merge, group, pooled.** A level is *sparse* in an arm when either model fails the denominator guard
>   there (K9). A sparse level is *merged* with a neighbour in a fixed order (§2.4), decided on correct counts only.
>   The result is a set of *groups*: single levels or merged runs such as "4–5". A merged group is tested as one
>   hypothesis; its constituent levels are *pooled* and each carries `pooled_in` (the group's levels).

*Source: V2, lines 202–205.*

> *Numbers (illustrative, n = 64 per level; guard read as an observed count ≥ 3, pending O-2).* Correct counts by
> level 1–5: 8B 30, 25, 14, 6, 2; 1.7B 20, 12, 5, 2, 1. Levels 4 (1.7B has 2) and 5 (8B 2, 1.7B 1) are sparse, so 4
> and 5 join: group "4–5" has 8B 8 and 1.7B 3, passing, so it stops. Levels 1–3 pass. Partition: 1 | 2 | 3 | 45.

*Source: V2, lines 309–311.*

> In
> AP-5M it applies per model per level: a level fails if either model fails. The words "binomial lower-bound" are not
> defined in AP-5;

*Source: V2, lines 573–575 (excerpt).*

> the `< 3` in `sparse` is the denominator guard read as an observed count (O-2)

*Source: V2, line 803 (excerpt).*

**Lens positions.**

> K9 identifies the conflict, but the procedure cannot produce a unique partition until O-2 specifies the bound and confidence convention or expressly adopts the observed-count change. Keep the example conditional rather than saying that group passes.

*Source: R17, line 57 (excerpt).*

> | G3 | Denominator guard: observed count vs statistical lower bound | O-2 | step 6 yes | Yes (changes the partition) |

*Source: R18, line 97 (excerpt).*

**Sources.** The operative AP-5 row, in three fields:

> energy-per-correct = level-window energy / correct count only after the binomial guard passes.

*Source: AP, line 269 (excerpt).*

> Exact scorer output plus emitted-token/stop-reason audit; binomial lower-bound must be >=3 correct per level, else merge adjacent levels or report `not estimable`.

*Source: AP, line 274 (excerpt).*

> lower-bound <3 correct with no valid merge

*Source: AP, line 277 (excerpt).*

The AP-5 design note (review item 9) and its energy-per-correct paragraph:

> the >= 3-correct binomial guard is a deterministic property of the item set, not a per-bundle stochastic event.

*Source: SIR, line 464 (excerpt).*

Packet C (its proposed text; C line 11 also lists "the ≥3-correct guard" among what AP-5M inherits):

> **Minimum correct and merge order.** Each cell needs ≥ 3 correct (AP-5 guard; an observed count, a deterministic
> property of the set). If either model fails at a level in an arm, that level merges for both models, in that arm only,
> in this fixed order: 5 into 4 ("4–5"), then into 3; 1 into 2 ("1–2"), then into 3. Merges depend only on correct
> counts, never on energy or R. If no valid merge remains, the result is `not estimable`.

*Source: C, lines 130–133.*

The adopted merge pseudocode (R20 Q2, adopted by G21 §Q1 "AMEND D2 (adopt, with rulings below)") and the ruled
constant list:

>   groups = {1},{2},{3},{4},{5}; sparse(g) = min(Σc8[g], Σc17[g]) < 3

*Source: R20, line 15.*

> | Constants: levels, merge_order, min_correct 3, holm_m 5,

*Source: G45, line 52 (excerpt).*

**Does a source settle it?** No source in the packet defines a confidence level or bound formula for "binomial
lower-bound", and no ruling expressly amends AP-5's wording. SIR line 464 and C read the guard as an observed count;
AP-5 lines 269, 274 and 277 use the lower-bound words.

### Q2 — What must the pre-campaign smoke gate check for MATH, and what makes it pass? (BLOCKER, record 17 F2; O-11)

**Question.** AP-5 requires an envelope-validation smoke gate that "must pass". Its defined checks all test that
something is the same at every level, and MATH answers lengthen with level by nature. Which predicates does AP-5M's
smoke gate evaluate, what are their pass thresholds, and what happens on failure?

**Candidate readings.** (a) Keep the gate as a pass/fail check with no level-invariance predicate: pass means the
shakedown night yields strict-valid bundles (plus any named timing checks), and token and stop-reason
distributions are reported only (the v2 proposal). (b) Keep some E-checks as pass conditions in a MATH form, for
example E1 restated so that every stop other than the end token must be a cap hit, or E4 (prompt tokens) dropped because MATH
prompts differ by design. (c) Replace the gate with named new predicates (for example envelope timing, marker
integrity, cap-hit rate below a threshold).

**Draft text (V2).**

> **K21 — pre-campaign smoke gate (PROPOSED, for the gate; O-11).** AP-5 requires that an "envelope-validation smoke
> gate must pass before any scored campaign" (`analysis_plans.md:270`, VERBATIM fragment). Its defined checks
> (`docs/phase_2/suite_implementation_research.md` §3, E1–E4) are all invariance tests across levels: stop reasons,
> mean and distribution of emitted tokens, and prompt tokens. Packet C replaces level-invariant length with the
> three-factor decomposition, because MATH answers lengthen with level by nature. Proposed: AP-5M keeps a pre-campaign
> smoke gate, run as the shakedown night, that must yield strict-valid bundles and record per-level token, stop-reason
> and cap-hit distributions as reported descriptors; none of E1–E4 is a pass condition, and E5 (early-stop bias,
> advisory) is reported. Record 11 M6 and the magistrate's ruling M6 ask that the gate be kept; since every defined
> check is a level-invariance test, what "kept" means is O-11.

*Source: V2, lines 745–753.*

**Lens positions.**

> Strict-valid bundles and recorded distributions alone do not define a passing envelope check. The cold judge should name the surviving predicates, including how stop-reason and prompt-token behavior are judged for MATH.

*Source: R17, line 59 (excerpt).*

The magistrate's v2 revision ruling, as summarised in the brief for record 17:

> the smoke gate is kept minus its length condition

*Source: B16, line 7 (excerpt).*

**Sources.** AP-5's inclusion and disqualifier fields:

> Strict-valid bundles; envelope-validation smoke gate must pass before any scored campaign; correctness remains quarantined annotation under C-004.

*Source: AP, line 270 (excerpt).*

> Failed envelope validation, below-floor level windows, lower-bound <3 correct with no valid merge, or EOS-bias contamination gives `not estimable`/L1.

*Source: AP, line 277 (excerpt).*

The defined checks (SIR §3):

> `envelope_validated` iff E1–E4 all pass, else `envelope_failed([reason_codes])`

*Source: SIR, line 565 (excerpt).*

> Thresholds are pinned here; changing them requires a decision-log entry.

*Source: SIR, line 565 (excerpt).*

> - **E1 stop-reason invariance:** per level ℓ, r_ℓ = fraction with `stop_reason != "eos"`. PASS iff `max_ℓ r_ℓ ≤ 0.05` AND `max_ℓ r_ℓ − min_ℓ r_ℓ ≤ 0.05`.
> - **E2 emitted-token mean invariance:** PASS iff `max_ℓ mean(emitted) − min_ℓ mean(emitted) ≤ 1.0 token`.
> - **E3 emitted-token distribution homogeneity:** chi-square statistic on the level × emitted-token-count contingency (counts binned {1,2,3,4,5+}), p-value by **permutation test** (10,000 label permutations, `random.Random` seeded by SHA-256 of `suite_seed || "envelope_gate"` — stdlib-only, avoids needing a chi-square CDF). PASS iff p ≥ 0.01.
> - **E4 prompt-token invariance:** PASS iff global `max − min` realized prompt tokens ≤ 4 AND level means within 2 tokens (tolerance covers the {n}-digit deviation plus BPE digit-merge jitter; tokenizer-specific, recheck per model).
> - **E5 early-EOS-bias check (C-004's named caveat; advisory, does not gate):** per level where both classes have ≥5 parsed items, `|mean emitted(incorrect) − mean emitted(correct)| ≤ 1.0 token`, else `not_evaluable` recorded. Uses quarantined correctness as a *validity* input only — within the C-004 quarantine.

*Source: SIR, lines 569–573.*

Packet C's diagnosis and replacement:

> | `analysis_plans.md:270` + `docs/research_question_bank.md:104-106` | "envelope-validation smoke gate must pass before any scored campaign"; the gate "must show level-invariant emitted-token and stop-reason distributions" | MATH answers lengthen with level by nature; the gate fails by design. |

*Source: C, line 24.*

> It replaces AP-5's level-invariant-length
>   gate with a mandatory three-factor decomposition: for MATH, length change is measured, not a contaminant.

*Source: C, lines 11–12 (excerpt).*

The shakedown night (synthesis M4):

> It runs as a **bench token pilot** between windows (token counts, cap hits, loop rate, scorer audit, rough s/token), followed by one short shakedown night for envelope timing.

*Source: S19, line 14 (excerpt).*

**Does a source settle it?** No. AP-5 requires a passing gate (AP line 270); SIR defines passing only through E1–E4,
all level-invariance tests; C replaces the length condition but names no surviving pass predicate; the magistrate's
ruling keeps the gate "minus its length condition" without saying whether E1 (stop reasons) and E4 (prompt tokens)
survive. SIR line 565 requires a decision-log entry to change thresholds.

### Q3 — The floor and the anchor bound: which goes into the interval widening, and what is the block-window floor? (BLOCKER, record 17 F3 and F6; O-12)

**Question.** (a) Must each bootstrap replicate widen by `k·(floor_j + anchor_j)·s` as gate 21 ruled (D5a), or by
`k·anchor_j·s` alone, with the floor applied only as a separate gate on each block window, as the project's
single-count discipline states? (b) Which calibration artifact supplies the floor for the block-window class, and
what is `floor_j` (is it `max(floor_abs_j, floor_cmp_j)` for that class)? (c) How may the draft state the "about 1 J"
figure, given that it comes from phase windows?

**Candidate readings for (a).** (i) Keep D5a: floor + anchor inside every replicate, expressly overriding the
interval rule of the single-count discipline for AP-5M. (ii) Anchor only in the widening; floor as a separate
per-window gate (the single-count discipline). (iii) Another composition the judge names.

**Size of the effect.** With `floor_j` = 1 J and `anchor_j` = 1 J (illustrative), five one-window parents per model
give a total bound of 10 J under (i) and 5 J under (ii), against a planning cell sum of 23,552 J (1.7B) and 60,000 J
(8B). The sampling spread is about ×/÷ 1.59. The choice changes a verdict only at the knife edge, but it is a
registered rule and step 2 of the procedure cannot run without (b).

**Draft text (V2).**

> On this stack the floor is attribution-limited: about
>   1 J, set by how precisely a window's edges can be placed in the sampler's record, not by noise (D-078 clause 11;
>   detection_floor.md, `floor_limit_class: "attribution_limited"`).

*Source: V2, lines 115–117 (excerpt).*

> In the estimator below, `floor_j` names the per-window floor value
>   and `anchor_j` the per-window anchor bound; no block-window floor artifact exists yet (O-12).

*Source: V2, lines 119–120 (excerpt).*

> 2. **Select counted windows.** Exclude voided windows. A terminal `ceiling_violation` attempt's window is recorded
>    but never enters a cell sum (K17). Refuse any block window at or below the floor (row, Floor gate). *Cannot run
>    until O-12 names the floor value for block windows.*

*Source: V2, lines 233–235.*

> point bounds with U = Σ k·(floor_j + anchor_j) per model (K11).

*Source: V2, line 246 (excerpt).*

> add bound u = k·(floor_j + anchor_j)·s;

*Source: V2, line 249 (excerpt).*

> | Floor gate | Every block window above `max(floor_abs_j, floor_cmp_j)` for the block-window class; the estimator refuses a block window at or below the floor. No block-window floor artifact exists yet (O-12). |

*Source: V2, line 460.*

**Lens positions.**

> Both sources explicitly require both roles, but they prescribe different interval widening. O-12 correctly exposes this; it cannot be silently resolved by citing D5a alone.

*Source: R17, line 61 (excerpt).*

> **Precise question:** For AP-5M, must each replicate widen by `k·(floor_j + anchor_j)·s` under D5a, expressly overriding the single-count interval rule, or must it widen by `k·anchor_j·s` while the issued block-window floor remains a separate gate? Name the block-window floor artifact and define `floor_j` either way. This can change whether an interval excludes 1.

*Source: R17, line 103.*

> Label 1 J as a historical phase-window planning figure, not the block-window floor.

*Source: R17, line 67 (excerpt).*

> | G1 | Value of `floor_j`; whether the floor belongs in the widening; the block-window floor gate | O-12 | step 2 yes, step 7 no | Yes, at the knife edge (the bound is ~0.1 % of sampling spread); step 2 cannot run at all |

*Source: R18, line 95.*

> | N9 | "spread" (statistical) in the floor definitions | 110–111 | FAILS (collision and unquantified) | MATERIAL |

*Source: R18, line 56 (excerpt).*

**Sources: gate 21 and its inputs.**

> **D5a bootstrap bound: AFFIRM Opus's share-scaled bound.** Code `:99-100` fixes `error8/error17` once and reuses them at `:123` for every replicate (Sol 14 B1 confirmed by reading). Cure: per replicate, per drawn block and model, `u = k·(floor_j + anchor_j)·s`, with `k` the block's measured windows for that model and `s` the drawn-token share used at `:60-65`; point bounds keep `s = 1`.

*Source: G21, line 68.*

> bound u = k·(floor + anchor)·s with k the number of measured windows composing the block for that model.

*Source: R20, line 69 (excerpt).*

> Bootstrap over paired problems **and** over capture blocks (block-aware), widened by the instrument's floor and anchor bounds.

*Source: S19, line 19 (excerpt).*

> (4) Instrument
> widening: w = Σ_b (operative floor + `E_clock_anchor_shift_bound_j`) ÷ cell energy, per model.

*Source: C, lines 108–109 (excerpt).*

> Instrument error is a deterministic widening: ≈ 1 J floor per window against hundreds of joules per block
> (`research_question_bank.md:1603-1604`), while binomial spread (±12 % at n = 64) dominates.

*Source: C, lines 119–120 (excerpt).*

**Sources: the single-count discipline.** D-078 clause 11 (Ed-ratified):

>    **Binding condition — SINGLE-COUNT DISCIPLINE (Ed: "the cost seems
>    sensible as long as it's noted").** The floor gate now contains the
>    anchor term, and each claim's decision interval separately consumes
>    the member's `E_clock_anchor_shift_bound_j`. These are different
>    objects (calibration false-effect bound vs claim-side measurement
>    uncertainty) and both are legitimate, but the consequence is that the
>    effective clearable effect is FLOOR + CLAIM-SIDE BOUND (~5 J for
>    phase contrasts), not the floor alone. Every artifact publishing an
>    attribution-limited floor must state this explicitly so that neither
>    term is later removed as an apparent double count. Science must be
>    sized to the ~5 J bar; Splitwise-class effects (tens of percent of
>    tens of joules) clear it with margin.

*Source: DL, lines 4802–4813.*

The detection-floor contract (the attribution-limited floor row, then the single-count paragraph that follows its v2 object):

> - When the registered condition
>   `admissible_set_uncertainty_dominates_point_floor` is the sole cell
>   condition, the row is claim-ready and additionally carries
>   `floor_limit_class: "attribution_limited"`,
>   `floor_source: "E_clock_anchor_shift_bound_j"`, a
>   `point_floor_diagnostic` labelled `repeatability_diagnostic` with
>   `published_claim_floor: false`, and the machine-readable
>   `single_count_discipline` object specified below. The published component
>   and `floor_gate_j` use the corner-widened value, never that point
>   diagnostic.

*Source: DF, lines 75–84.*

> This is the versioned D-078/D-083 single-count discipline. The anchor term
> legitimately appears once in the calibrated false-effect floor and separately
> in the claim decision interval as measurement uncertainty. The sum is only a
> prospective planning/sizing diagnostic. Acceptance uses two separate checks:
> strict `|estimate| > F` and zero-exclusion by both metrology and decision
> intervals, plus the registered multiplicity adjustment and evidence/eligibility
> requirements. For symmetric `estimate ± h` intervals with nonnegative widening
> `B`, their numerical conjunction is strict
> `|estimate| > max(F, h+B)`; asymmetric intervals use their actual endpoints.
> The two roles remain mandatory and neither may be optimized away as apparent
> double counting.

*Source: DF, lines 160–170.*

**Sources: floor values and window classes.**

> each member carries a
>    clock-anchor-shift envelope of ~0.7-1.0 J: a +/-31 ms window shift
>    across a phase boundary where power swings ~33 W mis-attributes ~1 J
>    between prefill and decode.

*Source: DL, lines 4761–4764 (excerpt).*

> PC-1 labelled attribution floor ≈1 J per
> phase, effective contrast bar ≈5 J

*Source: RQB, lines 1603–1604 (excerpt).*

> The
>    **canonical operative floors**, which additionally include the window's
>    0.652272 J drift allowance and are the numbers that may be published or
>    compared against effect sizes, are **3.823787 J prefill** and
>    **3.592138 J decode**.

*Source: DL, lines 5026–5030 (excerpt).*

> *(AMENDED by D-084, 2026-07-29: at mint the
>    operative decode pin was re-set to the composed cell gate 7.377086 J;

*Source: DL, lines 5034–5035 (excerpt).*

> The calibration manifest produces one row per
> `backend x metric x window_class x condition_family` with:
>
> - `floor_abs_j`: the absolute detection floor for a nominal zero-effect
>   repeated cell.
> - `floor_cmp_j`: the comparative floor from same-condition ABBA or matched
>   duplicate-label contrasts.
> - `floor_gate_j`: `max(floor_abs_j, floor_cmp_j)`, matching
>   `analysis_plans.md`.

*Source: DF, lines 66–74.*

> | Floor gate | pending-P2-015: `max(floor_abs_j, floor_cmp_j)` for level windows. |

*Source: AP, line 272 (excerpt).*

**Does a source settle it?** Partly. For (a), D5a (G21 line 68) is a ruling that puts floor + anchor in the widening;
D-078 clause 11 and DF lines 160–170 assign the floor to a separate gate and the anchor to the decision interval, and
call the sum a planning diagnostic that is not an acceptance gate. G21 does not mention the single-count discipline.
Note also DF lines 75–84: an attribution-limited floor is itself sourced from `E_clock_anchor_shift_bound_j`. For (b),
no source names a block-window floor artifact; AP-5's floor field is pending for level windows. For (c), the ≈1 J
figure is stated per phase (DL 4761–4764, RQB 1603–1604), and D-079 names canonical operative phase floors of about 3.8 J (prefill) and 3.6 J (decode), the decode gate later re-set to about 7.4 J by D-084.

### Q4 — Interval endpoints and the resampling scheme (O-4; record 17 F9)

**Question.** (a) Do the reported interval ends stay at the percentiles alone (packet C step 6, operative in v2), or
are they amended to `min(point_low, percentile_low)` and `max(point_high, percentile_high)`, where the point bounds
are the low and high sides computed on the observed data (s = 1)? (b) Is K10's two-stage draw (parents, then problems
within each drawn parent, the same draws for both models, energy scaled by each model's own drawn-token share s)
adopted as registration text? (c) Are Python's `random.Random(seed)` and linear interpolation between order
statistics adopted, or left to the registration packet?

**Draft text (V2).**

> 8. **Bootstrap, B = 20,000.** Per replicate: draw parents within each level of the group, then problems within each
>    drawn parent, both paired across models; scale each drawn parent's energy by the model's own drawn-token share s;
>    add bound u = k·(floor_j + anchor_j)·s; form the low-side and high-side ratios (K10, K11; worked in §2.5). *The
>    two-stage draw is proposed text pending O-4.*

*Source: V2, lines 247–250.*

> In each replicate, within each level of the group, draw as many parent blocks as the level has, with
> replacement, using the same draw for both models; within each drawn parent, draw as many problems as it holds, with
> replacement, using the same positions for both models.

*Source: V2, lines 589–591 (excerpt).*

> The draft estimator does this with Python's `random.Random(seed)` and linear interpolation between order statistics
> for percentiles (`d2f9a273:joulewise/energy_per_correct.py`, `ratio_interval`); these are proposed, not ruled.

*Source: V2, lines 594–595 (excerpt).*

> (magistrate ruling B2 for version 2):
>
> > (6) The reported interval runs
> > from the 2.5th percentile of the low-side values to the 97.5th percentile of the high-side values.
>
> *Source: C §3, step 6. VERBATIM.* Whether the point bounds also widen the ends is O-4.

*Source: V2, lines 612–617.*

**Lens positions.**

> Including point bounds can turn a percentile-only directional interval into NR. **Cold-judge question:** Are the endpoints percentiles alone, or `min(point_low, percentile_low)` and `max(point_high, percentile_high)`? The exact two-stage resampling in K10 also needs approval as proposed policy.

*Source: R11, line 57 (excerpt).*

> already supplies the operative percentile-only wording under the v2 revision ruling. Ask whether to **amend** it with point bounds.

*Source: R17, line 73 (excerpt).*

> | G5 | Whether point bounds widen the interval ends | O-4 | step 11 yes | Yes, at the knife edge |

*Source: R18, line 99.*

**Sources.**

> (3) Draw B = 20,000 resamples (seed pinned
> in the registration). Each draws n problem indices with replacement within the level and applies the same indices to
> both models, so the shared problems stay paired.

*Source: C, lines 106–108 (excerpt).*

> (6) The reported interval runs
> from the 2.5th percentile of the low-side values to the 97.5th percentile of the high-side values.

*Source: C, lines 112–113 (excerpt).*

> U_m = Σ u. Low bound R(E₈ − U₈, E₁.₇ + U₁.₇), high R(E₈ + U₈, E₁.₇ − U₁.₇); point bounds use s = 1.

*Source: R20, line 69 (excerpt).*

**Does a source settle it?** (a): C step 6 is the only endpoint rule; no source adds point bounds. (b): M9 requires
a block-aware draw but no source specifies the two-stage scheme; V2 marks it PROPOSED. (c): no source.

### Q5 — Does a level already forced NR by a flag stay in the Holm sort? (O-5)

**Question.** A level forced NR by `spread_exceeded` or `drift_exceeded` still has a computed p-value. Does that
p-value enter the Holm sort (m stays 5), or is the level removed from the sort like an NE group (m still 5)?

**Why it matters.** Holm compares the k-th smallest p-value with 0.05/(6 − k). A flag-forced level with a small p that
stays in the sort takes the strictest threshold 0.01, and the remaining levels are compared with 0.0125, 0.0167, …;
removing it moves each remaining level one step stricter. Example: p-values 0.002 (flag-forced), 0.012, 0.014. Kept:
0.012 ≤ 0.0125 and 0.014 ≤ 0.0167 both reject. Removed: 0.012 > 0.01 and Holm stops; neither rejects.

**Candidate readings.** (a) Keep it in the sort; the flag forces NR afterwards. (b) Remove it from the sort, m = 5.
(c) Remove it and reduce m.

**Draft text (V2).**

> 10. **Holm**, m = 5, over the tested groups; NE groups are not tested and m stays 5 (K9, S2). *Whether a level
>     already forced NR by `spread_exceeded` or `drift_exceeded` still contributes its p-value to the sort is not
>     settled by any source (O-5). It matters: with m fixed at 5, a flag-forced level with a small p-value that stays
>     in the sort takes the strictest threshold α/5 and lets the levels after it be compared against the looser α/4,
>     α/3, …; removing it makes each of those comparisons one step stricter, which can turn a rejection into NR.*

*Source: V2, lines 252–256.*

> - **O-5 (Holm membership).** *Question:* does a level already forced NR by `spread_exceeded` or `drift_exceeded`
>   contribute its p-value to the Holm sort, or is it removed like an NE group (with m still 5)?

*Source: V2, lines 1134–1135.*

**Lens positions.**

> fixes precedence, not Holm membership.

*Source: R17, line 113 (excerpt).*

> | G4 | Whether flag-forced NR levels stay in the Holm sort | O-5 | step 10 yes | Yes |

*Source: R18, line 98.*

**Sources.**

> Holm within each family, α = 0.05 two-sided, m = 5 fixed (one hypothesis R_L = 1 per level; a merged cell tests one hypothesis and m stays 5).

*Source: C, line 85 (excerpt).*

> holm(p over tested groups, m=5 fixed): sort ascending; reject while p ≤ α/(5−rank); stop at first failure
> status(g): NE if g∈NE; else if not rejected or p_below==p_above: NR
>            else E8 if p_below<p_above and hi<1; E1 if p_above<p_below and lo>1

*Source: R20, lines 19–21.*

> **(P) Precedence.** "When a level carries both NE(`ceiling_violation`) for a group and `spread_exceeded`, NE(`ceiling_violation`) takes precedence in the A281b total table and `spread_exceeded: true` is recorded alongside; a level with `spread_exceeded` and no NE is NR(`spread_exceeded`)."

*Source: G45A, line 60.*

> Cure: *"If the executed roster's gap exceeds max for a level, that level's status is NR(`drift_exceeded`) pending a balanced recapture."*

*Source: G21R, line 17 (excerpt).*

**Does a source settle it?** No. R20's `holm` runs "over tested groups" and `status` assigns NR afterwards, but no
source says whether a flag-forced level is a tested group.

### Q6 — `spread_exceeded` inside a merged group, and the recapture bound (O-6)

**Question.** (a) When one constituent level of a merged group carries `spread_exceeded`, is the whole group
NR(`spread_exceeded`), or only that level's status? (b) Does "until a registered recapture" in K15 and in text (W)
share S8's bound of at most one recapture, or is it a separate, unbounded recapture?

**Draft text (V2).**

> - **spread_exceeded, drift_exceeded.** Flags that a cell lost its minimum spread after capture, or that a level's
>   executed drift lever exceeded `max_gap`; each makes the level NR until a registered recapture.

*Source: V2, lines 223–224.*

> - **O-6 (spread in merged groups).** *Question:* when one constituent of a merged group is spread-exceeded, is the
>   whole group NR(`spread_exceeded`)? Does "until a registered recapture" in K15 and in (W) share S8's one-recapture
>   bound?

*Source: V2, lines 1136–1138.*

**Lens positions.**

> defines a cell flag, not its merged-group propagation or recapture limit.

*Source: R17, line 114 (excerpt).*

> | G6 | Spread-exceeded constituent of a merged group | O-6 | **no** (step 4) | Yes |

*Source: R18, line 100.*

**Sources.**

> *spread_exceeded.* "A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them, because a parent lost an item to a terminal ceiling_violation after capture. The cell carries `spread_exceeded: true`, its numbers are reported, and its level is not resolved (`spread_exceeded`) until a registered recapture. Before capture the same shortfall is a packing refusal."

*Source: G45, line 71.*

> **(X) spread_exceeded, cause-agnostic.** Replace "because a parent lost an item to a terminal ceiling_violation after capture" with "for any reason after capture (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place)".

*Source: G45A, line 58.*

*(G45A line 60, text (P), is quoted in Q5.)*

> If it holds none, every uncompleted or not-started block becomes the typed terminal state `unattributed_overrun` (a `terminal_refusals` entry; its cell is unresolved until a registered recapture); the call never raises for innocence.

*Source: G45A, line 44 (excerpt).*

> Cure: *"At most one recapture, on a later census-clean window, both models' copies adjacent as singles; the night's other blocks for that arm are checked against s_per_token_upper; a second violation makes `ceiling_violation_unresolved` terminal for the family under this registration."*

*Source: G21R, line 12 (excerpt).*

> Constituents of an estimable merged group get `pooled` + `pooled_in`. Constituents of an NE merged group get `not estimable` + `pooled_in` + the NE reason.

*Source: G21R, line 13 (excerpt).*

**Does a source settle it?** No. G45A (P) defines the level status; the S8 bound (G21R R6) is written for the
ceiling-violation recapture only.

### Q7 — The drift threshold: source of δ_upper, the budget, the unit of `blocks_per_cell`, and the rank of `drift_exceeded` (O-7)

**Question.** (a) Where does `δ_upper` come from: the shakedown night, a pinned earlier power corpus, or another
named source? (b) What derivation of `budget_j` is registered? (c) Is `blocks_per_cell` the number of parent blocks
per cell per model? (d) Where does NR(`drift_exceeded`) rank against NE(`ceiling_violation`) and
NR(`spread_exceeded`) in the precedence rule?

**Draft text (V2).**

> 5. **Drift check per level.** Compute positions and the lever (K12); compare with `max_gap`; excess ⇒
>    NR(`drift_exceeded`). *Cannot run until O-7 fixes δ_upper and budget_j.*

*Source: V2, lines 241–242.*

> 12. **Group status** by the three-way test (S2); then flags: NE(`ceiling_violation`) takes precedence over
>     `spread_exceeded` (K16); `drift_exceeded` ⇒ NR (its rank is O-7).

*Source: V2, lines 259–260.*

> *Drift from panel 1.* At pack time the Level-5 thinking-on parents sit in envelopes 1, 5, 9, 13, 17 for the 8B (mean 9)
> and 0, 4, 8, 12, 16 for the 1.7B (mean 8): lever 1.0 slot. After the retry P3's position is (21 × 2 + 22 × 2) ÷ 4 =
> 21.5; the 1.7B mean becomes (0 + 21.5 + 8 + 12 + 16) ÷ 5 = 11.5; the lever grows to 2.5 slots. *Threshold
> (illustrative values, O-7):* δ_upper = 2 J per block per slot, budget_j = 50 J, P = 5 parents per cell give max_gap =
> 50 ÷ (2 × 5) = 5 slots; 2.5 ≤ 5, so the roster is accepted. The bound on bias is 2 × 5 × 2.5 = 25 J against a 23,552 J
> cell (0.1 %).

*Source: V2, lines 394–399.*

**Lens positions.**

> supplies units and budget requirement, not values or precedence.

*Source: R17, line 115 (excerpt).*

> | G2 | δ_upper, budget_j; rank of `drift_exceeded` against NE | O-7 | steps 5, 12 yes | Yes |

*Source: R18, line 96.*

> `GUESS 5`: `blocks_per_cell`.

*Source: R12, line 169 (excerpt).*

**Sources.**

> **D5b drift refusal: AFFIRM**, amend units: register `δ_upper` in joules per block per slot and `budget_j` as the per-cell absolute bias budget with its derivation; `max_gap` follows. `requeue_overrun` recomputes `drift_lever_slots`.

*Source: G21, line 70.*

> the formula max_gap = budget_j / (δ_upper · blocks_per_cell) is registered now and δ_upper comes from the pilot; recompute after every requeue.

*Source: G21C, line 22 (excerpt).*

> Register the threshold now as a formula: `max_gap = budget_j / (δ_upper · blocks_per_cell)`, with δ_upper from the pilot.

*Source: R20, line 70 (excerpt).*

> **R11 D5b (MATERIAL): incomplete.** No source is named for δ_upper; M4's bench token pilot measures no energy, so name the shakedown night or a pinned corpus.

*Source: G21R, line 17 (excerpt).*

> The claim tolerance on it is registered in AP-5M after the sizing pilot measures drift, not fixed here.

*Source: R08, line 9 (excerpt).*

*(S19 line 14, the shakedown night, is quoted in Q2; G45A line 60, text (P), in Q5.)*

**Does a source settle it?** (c) is supported by G45 §Q4 (parents are the drift unit) but no source states the
reading of `blocks_per_cell`. (a), (b), (d): no source. G21C and R20 say "from the pilot"; G21R R11 notes the bench
pilot measures no energy.

### Q8 — What drift model does the bias bound assume? (record 17 F8; record 18 N11, MATERIAL introduced by the v1→v2 fix)

**Question.** V2 derives a bound on the between-model bias, δ_upper × P × lever (V2 lines 170–173), from a bound on
each block's shift per slot. Records 17 and 18 say that this holds only for a drift linear in envelope index with a
slope common to both models (record 18 gives a counterexample). Does AP-5M (a) state that
assumption as registered (drift linear in envelope index, common slope ≤ δ_upper), (b) present `max_gap` as a
registered tolerance without claiming a proved bound, or (c) register a different drift model?

**Draft text (V2).**

> - **Position, drift lever, drift threshold.** Forcing problem: the machine's power drifts slowly across a night. If
>   one model's blocks sit systematically later, drift biases the ratio between models. A parent's *position* is the
>   item-weighted mean envelope index of its counted windows. The *drift lever* of a level is the absolute difference
>   between the mean position of its 8B parents and that of its 1.7B parents, in envelope slots. If a block's energy
>   shifts by at most δ_upper joules per slot of position, a model's cell sum over P parents shifts by at most
>   δ_upper × P × (its mean position), so the between-model bias is at most δ_upper × P × lever. Holding that below a
>   registered budget `budget_j` gives the threshold `max_gap = budget_j / (δ_upper · P)`. The packer aims for lever
>   0; a roster is accepted if lever ≤ `max_gap`.

*Source: V2, lines 167–174.*

> > Drift cancels in a per-level ratio only when each model's measured blocks share the mean envelope index; `idle_slot` captured, never a numerator.

*Source: V2, line 542.*

**Lens positions.**

> Equal mean positions cancel a *shared linear* position effect; a bound on each block’s shift alone does not establish that cancellation for different slopes or nonlinear drift.

*Source: R17, line 71 (excerpt).*

> State the assumed drift model beside the derivation, or present the formula as the registered tolerance without claiming a proved general bound.

*Source: R17, line 71 (excerpt).*

> Counterexample: 8B parents at positions 0 and 10 (mean 5), 1.7B parents at 5 and 5 (mean 5), lever 0, drift f(x) = δ·\|x − 5\| (slope never above δ). The 8B sum shifts by 10δ and the 1.7B sum by 0, so the bias is 10δ against a stated bound of 0. Version 1 said "cancel a drift that is linear in time"; version 2 dropped the word.

*Source: R18, line 21 (excerpt).*

**Sources.**

>   in envelope slots. Equal mean positions cancel a drift that is linear in time.

*Source: V1, line 95.*

> Drift cancels in a per-level ratio only when each model's measured blocks share the mean envelope index; `idle_slot` captured, never a numerator.

*Source: G21, line 80 (excerpt).*

> Opus 07 S1 showed the reason: drift cancels in a per-level ratio only when each cell's MEASURED blocks sit at the same mean position in time for both models.

*Source: R08, line 8 (excerpt).*

**Does a source settle it?** No source states a drift model. The cancellation sentence (G21 line 80, R08 line 8) is
true for a shared linear drift; the bound in V2 lines 170–173 is the draft's own derivation.

### Q9 — May retry tails continue on another night, and how are positions compared across nights? (O-10)

**Question.** M12 says an overrunning block is re-queued "within the night"; text (N) places rescheduled singles
"into the first later envelope … else a fresh one" with no night boundary. (a) Must a fresh envelope extend the same
night, or may retry work continue on a later census-clean night? (b) If later, how are envelope indices and the drift
lever defined across nights (continuous index, per-night index, or excluded from the lever)?

**Draft text (V2).**

> - **Night (measurement window), census-clean.** A *night* is one scheduled, unattended capture session holding a
>   sequence of envelopes (the sources also call it a "window"; this file says "night").

*Source: V2, lines 102–103 (excerpt).*

**Lens positions.**

> leave that boundary unclear.

*Source: R17, line 118 (excerpt).*

> | G7 | Positions of retry tails that spill into another night | O-10 | **no** (step 5) | Yes (via the drift lever) |

*Source: R18, line 101.*

**Sources.**

> | M12 | Overruns | A block that overruns is re-queued once within the night. It is then re-queued as single-problem envelopes, never dropped. | B's "void after two overruns" would drop exactly the long items. |

*Source: S19, line 22.*

> Any other uncompleted or not-started single is rescheduled without advancing, into the first later envelope satisfying M8-by-parent and capacity, else a fresh one.

*Source: G45A, line 48 (excerpt).*

> An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's.

*Source: G45A, line 50 (excerpt).*

> Idle collector plus a separate model worker; one thinking arm per night;

*Source: S19, line 23 (excerpt).*

> M12's purpose was that a long item is never dropped and always fits alone.

*Source: R08, line 16 (excerpt).*

**Does a source settle it?** No.

### Q10 — For a retried problem, which attempt's answer and token count are used? (record 18 G9; flagged nowhere in V2)

**Question.** A problem can run more than once: for example, it completes inside a block that is then cut off (the
block is the culprit and is re-run whole), or its single is re-run. V2 voids the superseded *windows* (energy) but
never says whether the superseded *attempt's* correctness and generated tokens are also dropped. Which attempt
supplies each problem's correct flag and tokens?

**Candidate readings.** (a) The attempt whose window is counted (the last non-voided attempt); every superseded
attempt's answer and tokens are recorded and never used. (b) The first attempt that completed, even if its window is
voided. (c) Another rule.

**Why it matters.** Under seeded sampling (Ed's option E3 (b)), two attempts of one problem can differ; under greedy
decoding they should be identical. Tokens also set the share s in the bootstrap.

**Draft text (V2).**

> - **Voided and counted windows.** A *voided* window belongs to an attempt that a retry superseded; it stays on
>   record and is never counted. A *counted* window is one whose energy enters a cell sum.

*Source: V2, lines 152–153.*

> P3 windows         voided                        voided; envelope keeps        counted: 2 problems       counted: 2 problems

*Source: V2, line 377 (excerpt).*

**Lens positions.**

> | G9 | **Which attempt supplies correctness and tokens for a retried item.** The text voids superseded *windows* (152–153) but never says the superseded *attempt's* answer and tokens are dropped too. An item completed inside a cut-off block and then re-run as a single has two answers | **no** | **no** | Yes under seeded sampling (E3 option b), where the two attempts can differ; no under greedy decoding |

*Source: R18, line 103.*

**Sources.**

> A completed block keeps its window; if its elapsed exceeds its `predicted_s` it is marked `late: true` and is a culprit.

*Source: G45A, line 44 (excerpt).*

> item conservation (per model, every registered item is in exactly one block that is neither superseded nor terminal, and that block is in exactly one envelope, or is in exactly one terminal refusal and no envelope)

*Source: G45A, line 52 (excerpt).*

> MATERIAL: windows must be keyed by (block_id, attempt), because a whole-block retry keeps its block_id and the voided and retry windows collide; `reduce` takes the executed roster; every roster item appears exactly once as a row or a terminal refusal; voided windows are excluded by rule.

*Source: G21R, line 15 (excerpt).*

> (b) the card's sampling settings (temperature 0.6, top-p 0.95, top-k 20), one pinned seed per (problem, model), one attempt, the same attempt count as greedy;

*Source: S19, line 29 (excerpt).*

> Both integration seats recommend (b), with (a) as the registered fallback if a bench probe shows seeded MLX sampling does not reproduce the same tokens.

*Source: S19, line 29 (excerpt).*

**Does a source settle it?** No text says so directly. G45A (S) and G21R R9 require each item to appear exactly once
as a row or a terminal refusal, and exclude voided windows; neither names which attempt's row survives.

### Q11 — What does a failed check during the ceiling-violation recapture mean? (O-9)

**Question.** S8 allows one recapture of a ceiling-violating problem and checks "the night's other blocks for that
arm" against `s_per_token_upper` (the registered upper bound on seconds per generated token). If one of those other
blocks exceeds it, is that (a) a second violation (the withholding of L\* becomes terminal), (b) a separate refusal of
that night (the recapture does not count and may be repeated once), or (c) a recorded disclosure with no status
consequence?

**Draft text (V2).**

> One recapture is allowed: on a later
> census-clean night, P3.a is run once by each model as a single, in adjacent envelopes (this seat reads "adjacent" as
> consecutive indices); the night's other blocks for that arm are checked against `s_per_token_upper`; a second
> violation makes the withholding final for this registration (S8).

*Source: V2, lines 425–428 (excerpt).*

> The consequence of a failed check on the night's other
> blocks is O-9.

*Source: V2, lines 894–895 (excerpt).*

**Lens positions.**

> requires the check without its failure disposition.

*Source: R17, line 117 (excerpt).*

> | G8 | Consequence of a failed `s_per_token_upper` check on the recapture night | O-9 | **no** (step 13) | Yes (L\* withheld or not) |

*Source: R18, line 102.*

**Sources.**

> (ii) the violation falsifies a registered physical bound, a physics/evidence refusal. Also, the cure is unbounded.

*Source: G21R, line 12 (excerpt).*

> The output flags that the registered `s_per_token_upper` was false for that arm.

*Source: R20, line 71 (excerpt).*

**Does a source settle it?** No.

### Q12 — Adopt the 10 % retried-attempts trigger? (O-8)

**Question.** Round-1 ruling 08 F2(d) left this lane a proposed trigger: if retried attempts exceed 10 % of a headline
cell, the next night re-measures the other model's copies adjacently. V2 does not adopt it. Add it (with what
exact text), or confirm its omission?

**Draft text (V2).**

> > (d) The paired drop-retried sensitivity analysis is pre-registered, and it is labelled selection-confounded because it removes exactly the long items (Opus). If including versus pairwise excluding retried blocks changes any Holm direction or L\*, that claim is reported unresolved until a balanced recapture (Sol).
>
> *Source: 08 F2 (a)–(d), affirmed by 21/10 §Q4. VERBATIM.* The 10 %-retried trigger 08 F2(d) left to this lane is
> O-8.

*Source: V2, lines 683–686.*

> - **O-8 (retry trigger).** 08 F2(d) left this lane a trigger: retried attempts above 10 % of a headline cell ⇒ the
>   next night re-measures the other model's copies adjacently. This draft does not adopt it. *Question:* add it, or
>   confirm its omission?

*Source: V2, lines 1143–1145.*

**Lens positions.**

> leaves the 10% trigger for consideration.

*Source: R17, line 116 (excerpt).*

**Sources.**

> The paired-retry default is rejected: it doubles cost. The AP-5M drafting lane considers Opus's suggested trigger (retried attempts > 10 % of a headline cell ⇒ the next night re-measures the other model's copies adjacently); no code for it here.

*Source: R08, line 15 (excerpt).*

**Does a source settle it?** No; R08 expressly leaves it open.

### Q13 — Which reason does AP-5M record for withholding L\* after a ceiling violation? (O-1)

**Question.** Gate 21 and its refuter agree that a ceiling violation withholds L\* but give different reasons. Which
does AP-5M record: gate 21's ("a gap there is the selection M12 forbids"), the refuter's (i) and (ii), or both?

**Draft text (V2).**

> > When any item in the family carries a terminal `ceiling_violation`, its group is NE(`ceiling_violation`), every other group is classified and printed, and `crossover_level` is null with reason `ceiling_violation_unresolved` until a registered recapture resolves the item. Pairwise exclusion of the item appears only in the labelled selection-confounded sensitivity.
>
> *Source: 21/10 §Q1, Split 3 cure text. VERBATIM.* The ruling's stated reason is disputed by the refuter (O-1).

*Source: V2, lines 885–887.*

> *Question:* which reason does AP-5M record for withholding
>   L\*: the ruling's "a gap there is the selection M12 forbids", the refuter's (i) and (ii), or both?

*Source: V2, lines 1121–1122 (excerpt).*

**Lens positions.**

> Properly open:

*Source: R17, line 109 (excerpt).*

**Sources.**

> Reason: the violating item is by construction the longest; a gap there is the selection M12 forbids.

*Source: G21, line 23 (excerpt).*

> **R6 ceiling violation: AGREE with the outcome, DISAGREE with the reason (MATERIAL).** Group-level NE is not pairwise exclusion, and the table lets count-based NE gaps license L\* (`11e88`, `eee18`), so "a gap there is selection" contradicts it. The operative reasons: (i) the censored outcome leaves the count-only merge partition undetermined; (ii) the violation falsifies a registered physical bound, a physics/evidence refusal.

*Source: G21R, line 12 (excerpt).*

> Pairwise exclusion as primary is exactly the selection M12 forbids; imputing "incorrect" fails because energy and outcome are both censored.

*Source: R20, line 71 (excerpt).*

**Does a source settle it?** No; the gate-21 ruling and its paired refuter disagree on the reason.

### Q14 — The combined claim sentence (O-3)

**Question.** Adopt V2's proposed template in S6, which combines pooled licensing, bracket gaps and every other gap,
and calls NE gaps "not estimable" and NR gaps "not resolved"? If not, dictate the template.

**Draft text (V2).**

> **PROPOSED combined sentence (this seat's drafting, for the gate; O-3).** Template, with every part optional except
> the first:
>
> "On this frozen MATH set (arm, cap), the cheaper model per correct answer changed from 1.7B **[at Level a | on
> pooled Levels a–b]** to 8B **[at Level L\* | between Levels b and L\*]**; **[Level(s) … not resolved]**; **[Level(s)
> … not estimable]**."
>
> Rules: use "at Level L\*" when no bracket gap exists, else "between Levels b and L\*" with b the highest level of the
> licensing group; list every gap level (bracket and outside), NR levels under "not resolved" and NE levels under "not
> estimable"; a pooled boundary group gives no L\* (S3). Examples: `1nn8n` → "changed from 1.7B at Level 1 to 8B
> between Levels 1 and 4; Levels 2, 3 and 5 not resolved." `12|3|4|5` with `1n88` (levels `ppn88`) → "changed from 1.7B
> on pooled Levels 1–2 to 8B between Levels 2 and 4; Level 3 not resolved." `11e88` → "changed from 1.7B at Level 2 to
> 8B between Levels 2 and 4; Level 3 not estimable."

*Source: V2, lines 869–881.*

**Lens positions.**

> **Cold-judge question:** Supply one sentence template that names pooled licensing, bracket gaps, all other gaps, and NE gaps without describing NE as an NR status.

*Source: R11, line 59 (excerpt).*

> Properly open for adoption of the proposed sentence; all-gap disclosure is already answered by

*Source: R17, line 111 (excerpt).*

> | N27 | S6 proposed template and rules | 869–881 | BUILT-BEFORE | — | the three examples apply the rules consistently |

*Source: R18, line 74.*

**Sources.**

> (a) `gap_levels` must list every NR/NE level in the family, not only those strictly between licensing and boundary; the claim sentence names them.

*Source: G21, line 27 (excerpt).*

> Cure: *"If any level lies strictly between the licensing group and the boundary level, the sentence reads 'changed from 1.7B (Level a) to 8B between Levels a and L\*; Levels … not resolved'; L\* is reported as the first level with a resolved 8B-cheaper result."* NIT: keep `bracket_gap_levels` separate.

*Source: G21R, line 10 (excerpt).*

> | 1\|2\|3\|4\|5, L3 sparse `11e88` | `11e88` | crossover | **4**, licensing 2, gap 3 (NE) |

*Source: G21, line 49.*

> | 123\|4\|5 `e18` (Sol) | `eee18` | crossover | **5**, licensing 4, gaps 1–3 (NE) |

*Source: G21, line 56.*

> *"A merged group may license L\* only as a region statement. When the licensing group is pooled, the crossover sentence reads: 'The cheaper model per correct answer changed from 1.7B on pooled Levels 1–2 to 8B at Level 3 on this set.'

*Source: G21, line 19 (excerpt).*

**Does a source settle it?** Partly: G21 (a) requires every gap level to be named. The combined wording, and the
word used for an NE gap, are not fixed by any source.

### Q15 — The idle reference: report only, or a registered adjustment? (O-13)

**Question.** Several sources call the idle reference "a covariate" without a computation. Does AP-5M (a) record and
report it only, never entering any computation (V2's position), or (b) register an adjustment (which one)?

**Draft text (V2).**

> | Order/blocking/covariates | The packer aims for equal mean envelope position per cell across models (the objective); a roster is accepted if the drift lever ≤ `max_gap` (the registered tolerance), and an executed excess makes the level NR (K6, K12). The idle reference (idle-slot energy) is recorded and reported beside results; no registered computation adjusts R_L by it (O-13). |

*Source: V2, line 459.*

> > Gross energy between the outer item edges of each block. Net-of-idle is never a peer number; the idle reference is a covariate.
>
> *Source: 19 §1 M7. VERBATIM.* No source says how the covariate is used; this draft records and reports it only
> (O-13).

*Source: V2, lines 528–531.*

> - **O-13 (idle covariate).** M7 and 08 F1 call the idle reference a covariate without a computation. *Question:*
>   report-only (this draft's position), or a registered adjustment?

*Source: V2, lines 1163–1164.*

**Lens positions.**

> calls idle a covariate without an adjustment rule.

*Source: R17, line 121 (excerpt).*

> `GUESS 17`: is it used in any computation, or only reported?

*Source: R12, line 194 (excerpt).*

**Sources.**

> | M7 | Energy numerator | Gross energy between the outer item edges of each block. Net-of-idle is never a peer number; the idle reference is a covariate. | D-045.7 (`decision_log.md:2618-2619`): block and level energies are gross only. |

*Source: S19, line 17.*

> It never enters any numerator (M7). It may be used as a covariate.

*Source: R08, line 7 (excerpt).*

**Does a source settle it?** No; M7 and R08 F1 permit a covariate use but define none.

### Q16 — Registration numbers left open, and the unit of the capture budget (O-14; record 17 F4)

**Question.** (a) May AP-5M leave to the registration packet the envelope length (600 s in the gate-21 charge and
packet B; 480 s slots in record 18's arithmetic), the cap-ladder values, the budget value and the seed? (b) What
unit and word does AP-5M use for the capture budget in K2 and O-18: "windows" (the sources' word), "nights" (V2's
word, which V2 defines as the same thing), or both with a gloss? The mechanical n rule (128 if the pilot-projected
capture at 128 fits the registered budget, else 64) is carried verbatim from C and is not in question.

**Draft text (V2).**

> Its
>   length is a registration number not yet fixed (the gate-21 charge states 600 s; the planning arithmetic in record
>   18 uses 480 s slots; O-14).

*Source: V2, lines 89–91 (excerpt).*

> - **Night (measurement window), census-clean.** A *night* is one scheduled, unattended capture session holding a
>   sequence of envelopes (the sources also call it a "window"; this file says "night").

*Source: V2, lines 102–103 (excerpt).*

> *Source: C §3. VERBATIM.* ("16-problem" means 16 per level, 80 in all, per M4.) The "declared ladder" is a list of
> candidate cap values and the "registered window budget" a number of nights; neither is yet stated (O-14). Ed's E4
> decision is whether that budget is acceptable (O-18).

*Source: V2, lines 502–504.*

> - **O-18 (Ed, E4).** n per level is chosen mechanically by K2 (c): 128 if the pilot-projected capture fits the
>   registered window budget, else 64. Ed's decision is whether the budget is acceptable; planning figures (record 18)
>   are about 12 nights for n = 64 and about 23 for n = 128, at 4–5 nights a day.

*Source: V2, lines 1177–1179.*

**Lens positions.**

> Correct the unit wherever the mechanical n rule is explained.

*Source: R17, line 63 (excerpt).*

> Properly open for registration values, but correct its budget unit alongside F4:

*Source: R17, line 122 (excerpt).*

> | N29 | "4–5 nights a day" | 1179 | FAILS (jarring) | NIT | "night" is built as a capture session; say so here |

*Source: R18, line 76.*

**Sources.**

> An *envelope* is one fixed-length power capture (600 s).

*Source: G21C, line 7 (excerpt).*

> Each envelope is a fixed 600 s powermetrics capture taken by the idle collector's `PowerRecorder`. (An **envelope** is one continuous power capture. Its **interior** is the 480 s span that starts 60 s after capture start, the 60 s being the **offset**.)

*Source: PB, line 7 (excerpt).*

> - *Window cost.* At 12 × 480 s per window and 0.8 utilisation, n = 64 needs about 10 thinking-on windows plus 1–2 thinking-off windows. This assumes 8 h of 8B decode (synthesis) and my assumed 5 h for the 1.7B. n = 128 needs about 20 + 3.
> - *Days.* At 4–5 windows per day, that is about 3 days vs about 5–6 days. The deadline is end of November, so recommend 128 if the pilot confirms the rates.

*Source: H18, lines 119–120.*

> That is about 12 windows (≈ 3 days at 4–5 windows/day) against about 23 windows (≈ 5–6 days).

*Source: S19, line 30 (excerpt).*

> The registered rule decides mechanically from the pilot; Ed rules only on whether the budget ceiling is acceptable.

*Source: S19, line 30 (excerpt).*

**Does a source settle it?** (b): the sources consistently say "windows" (S19 line 30, H18 lines 119–120, C line 127).
(a): no source requires these values in the analysis plan.

### Q17 — Adopt K1's problem draw as AP-5M text? (O-15; record 18 N19)

**Question.** (a) Adopt K1's population and draw (the merged importer's keyed, subject-interleaved selection; the same
problem ids for both models and both thinking modes) as AP-5M text, or leave the draw to the importer by reference?
(b) The eligibility text in K1 lists "grouped integer" among qualifying forms and then excludes `1,000` as a
plain-comma reference; record 18 calls this self-contradictory. The importer accepts thousands grouped by the TeX
forms `{,}` or `,\!` and excludes any other comma. The judge may dictate the exact wording.

**Draft text (V2).**

> *Rational* means the reference, after removing TeX spacing,
> dollar signs, a trailing degree or percent sign, a unit word and a leading "x =", parses as an integer, decimal,
> grouped integer, a/b, or `\frac{a}{b}`: `5`, `-\frac{3}{4}`, `0.25` and `10\%` qualify; `\sqrt{2}`, `3\pi` and `(1,2)`
> do not. A *plain-comma* reference such as `1,000` is excluded because the comma could separate thousands or list two
> answers.

*Source: V2, lines 476–480 (excerpt).*

> *Draw.* Each eligible problem gets a key = sha256 of a fixed domain string and the problem's content hash. Within a
> level, problems are queued by subject (MATH's seven subject labels), each queue sorted by key; rounds take one
> problem from each subject in turn, each round ordered by key ("balanced by subject" means this round-robin). The
> pilot takes the first 16 per level under the pilot domain string; the test set takes the first n per level of the
> remaining problems under a different domain string. The same problem ids serve both models and both arms. Source:
> `joulewise/benchmark_import_math.py` (`eligible_records`, `select_pilot`, `select_items`) at `a53a6b97`, gated by the
> cold ruling of record 40, activation 1d3796d5. Publication of problem text is Ed's E1 decision (O-20).

*Source: V2, lines 483–489.*

**Lens positions.**

> Properly open for *adoption*, though the mechanics are answerable from the

*Source: R17, line 123 (excerpt).*

> New defect (MATERIAL): 478 lists "grouped integer" among forms that qualify, and 479 then excludes `1,000` as a "plain-comma" reference. `1,000` is the ordinary example of a grouped integer, so the predicate reads as self-contradictory.

*Source: R18, line 20 (excerpt).*

**Sources.**

> Rational-valued answers only. Balanced by subject.

*Source: S19, line 11 (excerpt).*

> MATH-500's Level-1 count is unverified; if it is below 64, it
>    cannot supply n = 64. Subject balancing is left to the importer packet.

*Source: C, lines 196–197 (excerpt).*

>     s = s.replace("{,}", ",")
>     match = _LHS.fullmatch(s)
>     if match:
>         s = match.group(1)
>     try:
>         if _INT.fullmatch(s) or _DEC.fullmatch(s):
>             return str(Fraction(s))
>         if _GROUPED.fullmatch(s):
>             return str(Fraction(s.replace(",", "")))

*Source: IMP, lines 127–135.*

> def plain_comma_ambiguous(answer: str) -> bool:
>     s = "".join(answer.split())
>     for token in (r"\,", r"\;", r"\:"):
>         s = s.replace(token, "")
>     return "," in s.replace(r",\!", "").replace("{,}", "")

*Source: IMP, lines 192–196.*

**Does a source settle it?** M1 settles "balanced by subject" and the population; C leaves the balancing mechanism
to the importer; no source says whether AP-5M must restate the mechanism.

### Q18 — Keep the five added row fields? (O-16, editorial)

**Question.** V2's row adds five fields that AP-5 does not have (Estimand, Capture unit, Sparse-level merge order,
Retry and overrun rules, Status vocabulary). Keep them, or fold their content into AP-5's standard fields?

**Draft text (V2).**

> Fields follow the AP-5 row in order; five fields marked *(added)* have no AP-5 slot (an editorial choice; record 11
> F6 finds no ban on extra fields). Clause references K-n point to §2.9.

*Source: V2, lines 443–444.*

**Lens positions.**

> supplies no prohibition on extra fields.

*Source: R17, line 124 (excerpt).*

**Does a source settle it?** No prohibition exists; the choice is editorial.

## 4. What the judge returns

1. For every question Q1–Q18, a ruling and the **exact replacement text** for each affected place in V2 (name the
   V2 section and line range the text replaces, or the place it is inserted). Where a ruling changes the procedure
   (V2 §2.2), the Terms (§2.1), a worked example (§2.3–§2.6), a clause (K1–K21), the row (§2.8), §3, §4 or an open
   item (§6), give the text for each.
2. Where a question is Ed's to decide (E1–E4), say so and give the text that frames it; do not decide it.
3. Close with one consolidated list headed **"Final texts (paste verbatim into v3)"**, one entry per replacement, each
   naming its target location. The writer of v3 installs these verbatim and makes no other policy change.
4. The appendix below lists the pure writing defects that need no policy choice. The judge may add items, strike
   items, or promote an item to a ruling. The writer fixes the remaining items in v3.

## Appendix A — writing defects for the v3 writer (no policy choice)

From record 18 (teaching quality), each fixable by a gloss, rename or pointer:

- **N12** (after Q1 is ruled): build the guard at V2 line 202 in words ("at least 3 correct per model per level",
  in the reading Q1 rules).
- **N9** (after Q3 is ruled): replace "spread" in the floor definitions (V2 110–111) with the contract's actual
  statistics (DF lines 101–107 give both estimators).
- **N23** (after Q2 is ruled): rename the smoke checks away from "E1–E4" (V2 747, 751, 1152); gloss "early-stop
  bias".
- Flag O-6 at procedure step 4, O-10 at step 5, O-9 at step 13 and O-12 at step 7 (record 18 §5 item 7).
- NITs N2, N4–N8, N13–N15, N18, N20–N22, N24, N29 (record 18 §2 table), the panel-2 note on why envelope 23 rather
  than 22 (record 18 F11 row), "outside carries" at V2 157, and O-4 flagged at V2 191–192.
- V2 §7 self-check: correct it to match record 18 §4 (it omits the 20 new findings and overclaims "window
  collisions").

From record 17 (source fidelity), factual corrections judged to need no policy choice (the judge may promote any):

- **F5**: V2 line 86 says interval energy is "the sum of the sampler's per-record energy counters falling in it".
  The artifact guide computes it from power times overlap duration:

> For interval-supported powermetrics samples it recomputes phase energy as the sum of `power_w` times the overlap duration between each sample interval and the phase interval; point traces instead use linear interpolation and trapezoidal integration.

*Source: AG, line 336 (excerpt).*

- **F7**: V2 lines 72–74 say the scorer compares answers "as an exact rational number". The MATH ruling strips a
  percent sign on both sides without rescaling, and discloses a hazardous accepted pair:

> **C2. Percent rule = packet A step 4, symmetric, no rescale.** Remove the `("%" in box) != ("%" in expected_answer)` clause entirely. `canonical_reference_v1` already strips one trailing `\%`/`%` on both sides.

*Source: M40, line 49 (excerpt).*

> Documented known accepted pair (dangerous direction, disclosed, same class as `5,120`): (`\frac12\%`, `\frac12`) is `correct`; it is caught by packet A's per-cell audit, not by the mechanical scorer.

*Source: M40, line 49 (excerpt).*

- **N6**: "working interior" and `guard_s` (V2 line 92) are unbuilt; PB line 7 (quoted in Q16) defines the interior
  and offset.

## Exhibits needed

The magistrate copies these into the packet (paths relative to the repository root):

- `docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md`
- `docs/process_traces/2026-09-24-activation-a65fb4fa/07-a282-ap5m-draft.md`
- `docs/process_traces/2026-09-24-activation-a65fb4fa/11-a282-fidelity-sol-lens.md`
- `docs/process_traces/2026-09-24-activation-a65fb4fa/12-a282-pedagogy-opus-lens.md`
- `docs/process_traces/2026-09-24-activation-a65fb4fa/16-a282-v2-fidelity-delta-brief.md`
- `docs/process_traces/2026-09-24-activation-a65fb4fa/17-a282-v2-fidelity-delta.md`
- `docs/process_traces/2026-09-24-activation-a65fb4fa/18-a282-v2-pedagogy-delta.md`
- `docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md`
- `docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md`
- `docs/process_traces/2026-09-23-activation-1d3796d5/18-headline-opus-integration.md`
- `docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md`
- `docs/process_traces/2026-09-23-activation-1d3796d5/40-fable-ruling-math.md`
- `docs/process_traces/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md`
- `docs/process_traces/2026-09-23-activation-d8cc9c0a/20-a281-opus-consult.md`
- `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/00-charge.md`
- `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md`
- `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/11-opus-contract-refuter.md`
- `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md`
- `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md`
- `docs/contracts/analysis_plans.md`
- `docs/phase_2/detection_floor.md`
- `docs/decision_log.md`
- `docs/phase_2/suite_implementation_research.md`
- `docs/research_question_bank.md`
- `docs/paper/artifact-guide.md`
- `joulewise/benchmark_import_math.py`
