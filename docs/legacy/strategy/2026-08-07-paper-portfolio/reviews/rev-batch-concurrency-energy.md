# Counter-review — "Cohort Joules: Defining Honest Energy Boundaries for Batched LLM Inference on Consumer Silicon"

Reviewer: Opus 5 counter-reviewer (adversarial charge: kill it if it can be killed).
Target: `scratchpad/portfolio/prop-batch-concurrency-energy.md` (proposal = final block, lines 7137–7197; an identical duplicate sits at 7074–7136).
Ground truth: `scratchpad/desk` @ main (`89b929c`), verified by two independent repo audits.

## VERDICT: **WEAK** — and KILL as currently framed. Only the rewritten form survives.

The proposal is honest in tone, well-disciplined about D-117, and correctly defers continuous
batching. But three things are fatal as written: the **headline contribution cannot fail**, the
**effect sizing is drawn from the wrong physical regime and is wrong by ~3×**, and the **true cost
is roughly 2–3× the claimed cost** once you count what the repo actually has (which for batch
floors is: nothing, not even a window class that can be expressed). It also produces the one
result class in this project's entire option space where the instrument's distinguishing
capability is irrelevant. The proposal has its own strengths and weaknesses inverted — it hedges
on feasibility (easy) and overclaims on novelty and venue (the actual problems).

## Scores

| Axis | Score | One-line |
|---|---:|---|
| Novelty | **3/10** | Batch-size energy curves are a saturated literature; "no per-request joules under batching" is stated verbatim in ML.ENERGY (NeurIPS D&B spotlight), which then *solves* it. The genuinely uncovered slice (Apple/MLX) is thin and is not what the proposal leads with. |
| Feasibility | **4/10** | The runtime gate is genuinely passed and effects will clear any bar easily — but batch floors are **zero lines of implementation** on top of a floor module that hard-refuses the required window class, plus a mandatory 31-group alias-calibration campaign the budget omits. |
| MVP leverage | **4/10** | Reuses the method sections honestly, but §8 of the MVP draft is the project's *own written argument* for scoping overlapping requests out. And a 30 J effect on a ~47 J baseline needs no detection floor. |
| Venue fit | **3/10** | Workshop-plausible. "Plausible ICPE full-paper component" contradicts the repo's 2026-08-06 roadmap, which enumerates the qualifying deeper contributions (held-out Q4 prediction / second-unit replication / one mechanism study) and does not rank batching anywhere in its top nine. |
| Original goals | **5/10** | Real infrastructure dividend for spec-decode and MoE-by-batch — D-070 cl.3 designed the request-scoped schema for exactly this. But it touches no mechanism, and it consumes the nights the mechanism study needs. |

---

## FATAL FLAWS

### F1. The headline contribution is unfalsifiable by construction — the crux failure

Thesis and Contribution 1 are the **overlap-boundary rule**: report phase energy "only when
request events prove a globally separated prefill/decode boundary." The matching kill criterion
is "cohort phase unions overlap."

That criterion **cannot fire**, for four compounding reasons, all documented in the repo:

1. The design imposes a **prefill barrier** with **sixteen equal-shape requests**
   (`docs/specs/axi/se_analysis_plans_draft.md` §1 `selection_scope`), and the S-B probe
   "freezes a static cohort by inserting all B requests once before the first `next()` … and
   draining the cohort to completion" (`docs/specs/axi/sb_static_batch_verdict.md`). Overlap is
   engineered away before any measurement.
2. `mlx-lm` 0.31.3 prefills the whole cohort in **one batched 2-D forward**: "Prompt processing
   constructs a two-dimensional batch, including right padding … then calls the model with
   `tokens[:, :n_to_process]`. Decode likewise calls the model once with `inputs[:, None]`."
   Live evidence shows `input_shape [2,12]` → `[2,1]` and `[4,13]` → `[4,1]`. With equal-shape
   prompts there is no padding and there are no per-request prefill intervals at all.
3. Most damaging: the same verdict records that the harness "takes a monotonic timestamp when
   each `next()` result returns … and **records the shared return timestamp honestly for
   responses from the same scheduler step**." There are no independent per-request phase edges to
   compare. The "union of prefill intervals vs union of decode intervals" is a test over
   *group-level scheduler-step bookkeeping*, not over physical per-request intervals.
4. The MVP paper already makes this argument, as its own scoping rationale
   (`docs/paper/draft-v1.md:172`): "continuous batching makes an 'active phase' label difficult
   to interpret when requests overlap. JouleWise adopts phase-specific reporting but **restricts
   its primary scope to one sequential request**, where runtime-emitted phase boundaries are
   well posed and can be calibrated." Contribution 1 is the MVP paper's *limitation sentence*
   promoted to a finding.

So the flagship contribution validates the harness's own accounting against a case constructed to
satisfy it, and the interesting case — real overlap under continuous batching — is explicitly
deferred to "a later paper." A referee will call this a tautology dressed as a rule. **This alone
prevents any rating above WEAK.**

### F2. Effect sizing uses the wrong reference class, a voided number, and lands ~3× low

The proposal projects a "cautious 5–30% per-request reduction (~2.5–15 J)" and concludes "**B=2
may not clear 5 J**, B=4 is uncertain," sourcing this from "datacenter literature reports roughly
a 25% energy/token reduction over a much larger batch range."

Wrong regime. Datacenter batch curves are measured on GPUs already compute-saturated; the cited
25% is the *flat* part of their curve. An M3 Max running Qwen2.5-1.5B-4bit at B=1 is deeply
**memory-bandwidth-bound and grossly under-utilized** — decode reads ~0.8–1 GB of weights per
token per sequence, and batching amortizes that read across B sequences nearly for free.

Independent evidence: *Native LLM and MLLM Inference at Scale on Apple Silicon* (arXiv 2601.19139,
M4 Max 128 GB) measures **3.7–4.3× throughput at 16 concurrent requests**. If power rises ~1.3×
while throughput rises ~4×, per-request decode energy falls **~65–75%** — from ~47 J to ~13–17 J,
an effect of **~30–35 J**, i.e. **6–7× the ~5 J phase bar**. Even B=2 should show ~15–20 J.
*(Flagged: that throughput figure is a different model on a different chip and the power factor is
my inference. The sign and order are not in doubt, and the proposal's own "group-gross differences
should be much larger" concedes the mechanism.)*

Two consequences, the second worse than the first:

- The "cautious" posture and several kill criteria are mis-sized; "B=2 may not clear 5 J" is very
  likely a false-negative call that could kill the project's best cell for the wrong reason.
- **The paper does not need this instrument.** JouleWise's thesis is that detection floors and the
  attribution limit decide what may be claimed. A ~30 J effect on a ~47 J baseline is visible to a
  stopwatch and a wall plug. Scalpel, tree trunk.

Compounding compliance point: the ~47–50 J sizing input is **permanently VOIDED for claim use**
by D-078 (`PROJECT_STATUS.md:381`, `README.md:69`). The proposal calls it "the old … diagnostic"
but never says voided. Sizing an MDE off a voided corpus is exactly what D-078 forbade.

### F3. True cost is roughly 2–3× claimed, and the priority case is never made

The proposal budgets "**three additional quiet nights, possibly four**" beyond D-117's three, and
folds the batch floor *and* the 93-group three-block pilot into one window. Every load-bearing
piece of that is missing from the repo:

- **No batch adapter exists.** `joulewise/adapters/mlx_runtime.py` contains the string "batch"
  **zero times**. The only `static_batch` producer is the mock (`mock_spec_runtime.py:194`). Queue
  row `A4 / AXI-SB-ADAPTER` is `READY` — i.e. unstarted. *(The proposal does say "the required
  adapter is not yet implemented" — credit.)*
- **The floor module cannot express a batch window at all.** `joulewise/detection_floor.py:227–239`
  hard-raises on any `window_class` outside `("request","phase")`, and `batch_group_gross_energy_j`
  is absent from `FLOOR_METRIC_CATALOG`. Grep for `Sigma_F` / covariance machinery across
  `joulewise/`: **zero hits**; `detection_floor.py` is scalar-only.
- **A dedicated calibration campaign is mandatory, not optional.** AP-BATCH's floor gate: "accept a
  group calibration only if it covers **every B's** unioned window semantics, duration/cadence/drift
  range and supplies the joint `Sigma_F`; **a scalar single-request floor alone refuses** … If any
  required covariance, bound, B, or nonlinear denominator support is absent, **a dedicated 31-group
  same-design alias calibration is mandatory; otherwise this AP does not execute.**" And: "There is
  no fallback transport that always accepts."
- **The inherited hours exclude that calibration.** The ~3 h / ~5 h figures are not from AP-BATCH;
  they are from `docs/phase_2/splitwise_replication_roadmap.md` (2026-07-19), whose own row already
  warns "group-level floor/covariance path (**single-request floors do NOT transport**)". *(The
  proposal does flag these as uncertain historical estimates — credit — but then budgets from them
  anyway.)*

Realistic total: **four to six nights**, plus a from-scratch floor/covariance subsystem, plus an
adapter, under a fail-closed protocol where a refused window costs the whole night
(D-079 rationale: "it costs a whole quiet window per occurrence and window time is the project's
scarcest physical resource").

Now the priority arithmetic the proposal never does. The 2026-08-06 roadmap recommends **5–7
Ed-present sessions** total, 8–10 for an ICPE-full attempt, and concludes: "The strongest realistic
paper is … C1–C8 metrology + the already-collected 1.5B/7B demonstration + **one designed extension**
+ an independently usable artifact" — with the shortlist for that one slot being held-out Q4
prediction, quantization, or one mechanism study. D-117's three nights plus this proposal's four-to-six
consumes the entire ICPE-full budget on an axis that **appears at no rank in the roadmap's nine**.
(The only batch-adjacent phrase there is rank 7's "batch-**1**" speculative decode — that means the
*single-request* condition, not batching. Do not let it be read as support.) Rank 1's decision line
is explicit: "Reserve the core nights now and **prohibit breadth work from consuming them**." Under
Ed's paper-first stack (P1 MVP, P2 ICPE, **P3 sacrificed if it costs P1/P2**), this is P3 work
eating P1/P2 nights, and the proposal argues neither side of that trade.

### F4. Existing-material compliance gaps

- **"the existing AP-BATCH design"** — it is `AP-BATCH-**DRAFT**`, in a file headed "**DRAFT — design
  only; no campaign authority**", plan state "**PROVISIONAL pending P2-015 Window-A floors**", last
  edited 2026-07-15, owning queue row `A7 / AXI-SE` still `READY`, every number literal-marked
  `PROVISIONAL-UNTIL-P2-015-AND-PILOT-BATCH-V1`. P2-015 floors do not exist: `CLAIMS_STATUS.md` §1
  reads "**NONE at this checkpoint.**" The proposal's desk list does say "AP-BATCH finalization after
  the pilot," so this is overstatement rather than fabrication — but a reader budgeting nights off
  this text will think a frozen plan exists.
- **"authorized by D-070"** overstates it. D-070 cl.3 authorizes *scope and schema shape*; cl.2 holds
  that "every AP remains floor-gated on P2-015 floors … and no AXI stream consumes a [QUIET-MAC]
  window until Window A completes"; cl.5 caps everything at L2 with "no live claims from
  fixture-first code." No campaign authority was granted.
- **Contribution 4 is already repo doctrine.** AP-BATCH's metric row already states "**No overlapping
  group energy is divided among requests.**" Presenting the design constraint as an empirical finding
  is circular.
- **The claim-bearing phase work is unauthorized and unbudgeted.** AP-BATCH: "Gross phase-window
  energy is a **descriptive L1 audit** unless a later registry enumerates a phase family."
  Contributions 1–2 need a newly minted phase family, its own Holm denominator, and a phase-specific
  floor route. None appears in the desk list or the night budget.
- **C5-2.2 is never named.** The row this paper consumes carries the binding caveat "*no serving
  conclusion without latency-bound policy*." Its Mac leg *is* minted (2026-07-16, in
  `docs/research_question_bank.md`, per D-070 cl.4's mint-on-`supported` rule) — but the proposal
  cites neither the row, its caveat, nor D-070's requirement that these axes be framed as **stress
  tests of the single Q4 thesis, "not five new theses."** The proposal gives batching its own thesis.
- **Multiplicity is never mentioned.** AP-BATCH runs a seven-hypothesis Holm family for model
  selection, a separate denominator for normalized energy, and eight two-sided latency hypotheses —
  at draft `n_blocks=5`. That is where the statistical risk actually lives.
- **D-117 licenses no new axes.** Its only fenced extensions are the ≥256-token prefill arm (Ed's
  open option, "not adopted here," ~110 core min, "likely its own window") and Option 1 historical
  candidacy as a contingency requiring a rule-11 cold gate. Three severity-`blocker` desk items
  (F1/F2/F3 in the design memo) plus live night-stranding defects (L4, L5, R6) stand before the
  first D-117 arm runs.

*(One overreach I checked and did **not** find: the proposal does not claim the token-normalization
contract needs re-issuance, and correctly so — `docs/contracts/token_normalization.md:137` already
requires batch/concurrency policy disclosure as "Always applicable.")*

### F5. Contributions 3 and 4 contradict each other

C3 promises "gross joules/request" and "joules/output-token." C4 declares that "physical energy
remains identifiable only at cohort level" and that "no equal-share allocation is presented as
measurement." Both C3 metrics *are* cohort energy divided by a request or token count.

AP-BATCH resolves this and the proposal does not: dividing a **complete 16-request block partition**
by exactly 16 is legitimate *by symmetry of the design* (`BATCH-JREQ-B<value>-VS-B1`), whereas
allocating a single overlapping group window among its members is not. As stated, "an empirical
limit on per-request energy" is simply wrong — with sixteen identical equal-shape requests the
symmetric mean **is** the correct per-request estimator, and refusing it would be a metrology error
dressed as rigor.

### Minor

- The B=16 memory-fit kill criterion is near-empty. Measured marginal cost is **~33 MB per added
  sequence** (B=2 peak 968.7 MB → B=4 peak 1,034.4 MB); B=16 extrapolates to ~1.43 GB on a machine
  that has absorbed a 68.9 GB peak (Qwen3.5-122B-A10B-4bit run). D-070 cl.3's own rationale says "a
  single model instance with B KV caches is **memory-feasible on current hardware**." Fair as an
  untested-cell check; not a kill, and it must not be used to justify a smaller grid.
- "This intentionally extends the frozen single-request boundary, but does not alter or contaminate
  the D-117 campaigns" is the right sentence — and it is the only place the extension is priced. It
  prices *contamination* risk correctly (~zero) but never prices the *authorization* cost: the new
  phase family, the new floor window class, the AP freeze.

---

## What the proposal gets right (credit where due)

- Correctly defers continuous batching per D-070 cl.3, and names *why* (arrival traces, steady-state
  detection, scheduler policy, offered-load) rather than gesturing.
- Correctly refuses looped-singleton dispatch, matching AP-BATCH's inclusion rule and the S-B
  verdict's `unsupported_for_joulewise(native_batch_execution)` code.
- Correctly states that single-request floors do not license batch claims and that the ~5 J bar is
  only a planning proxy here. This is the sharpest sentence in the document, and it is consistent
  with D-078 cl.11 / D-083, which scope that bar to *phase contrasts on single-request windows* and
  provide no bar for any other estimand.
- Correctly rules the borrowed WT310E a non-dependency, for the right reason (validates totals, not
  allocation) — matching the roadmap's own C8 row and D-092.
- Correctly protects D-117 as non-negotiable, and reproduces its 3.14 / 3.24 / 2.80 h budgets and
  six-item desk list **faithfully** (independently re-verified against the design memo, including
  the arithmetic).
- Honest that the adapter does not exist and that the inherited hour estimates are stale.
- Kill criteria are mostly real, pre-committed, and desk-checkable — except the one that matters (F1).

---

## THREE STRENGTHENING MOVES (if kept)

**1. Re-center the thesis on the *shape* of E(B), not on the boundary rule.**
Make the primary claim AP-BATCH's *existing* primary family — the affine slope and the three
lack-of-fit curvature contrasts `d_1,d_2,d_3` — and ask what the datacenter literature structurally
cannot answer: **where is the amortization knee on a memory-bandwidth-bound consumer SoC, and is the
departure from affine resolvable above the floor?** Curvature contrasts are small differences of
large numbers; unlike the J/request curve, they *are* floor-sensitive, which makes the instrument
load-bearing again and turns the paper into the Q4 stress test D-070 actually asked for. Retitle
accordingly; demote the overlap rule to a two-paragraph methods subsection.

**2. Replace Contribution 1 with a negative control that can actually fire.**
Pre-register a deliberately **ragged cohort** — unequal prompt lengths (triggering `mlx-lm`'s right
padding) or staggered admission at B=4 — and show the validator *refusing* the phase split there
while *accepting* it under the equal-shape barrier. That is the only version of the boundary claim a
referee will accept; it is falsifiable; it costs desk time plus a slot inside the pilot rather than a
new claim night; and it yields the paper's one genuinely publishable refusal. If it cannot be built
on a shared-scheduler-step timestamp surface — and the S-B verdict suggests it cannot — **drop the
boundary claim entirely** and say so in print.

**3. Re-price honestly, and force the head-to-head before a single night is committed.**
(a) Build the A4 adapter and run the group ladder **off-window** on the unquiet machine to produce a
real occupancy number, replacing the 2026-07-19 inherited estimates. (b) Scope the batch-floor
subsystem explicitly as what it is — a new `detection_floor` window class, a `Sigma_F` covariance
implementation, and a 31-group alias-calibration campaign — and put *that* on the night ledger, not
just the pilot. (c) Write the ledger against roadmap ranks 1, 2 and 3 (remint / C8 wall meter /
artifact release) and state in writing which Ed accepts delaying; the roadmap's "one designed
extension" slot has a shortlist and batching is not on it, so that omission must be argued *with*,
not around. (d) If the lack-of-fit family cannot be powered at `n_blocks=5` under Holm-7, **shrink to
B ∈ {1,4,16}** — three well-floored cells beat five unresolvable ones, and the knee is still
locatable. Bind the limitations section to C5-2.2's existing "no serving conclusion without
latency-bound policy" wording, and re-derive the sizing input from D-117's fresh floors rather than
the D-078-voided ~47 J corpus.

---

## Novelty evidence (external)

| Work | Overlap | Why it hurts |
|---|---|---|
| ML.ENERGY Benchmark (arXiv 2505.06371; NeurIPS D&B spotlight) | Direct | States Contribution 4 verbatim: batching makes "the energy consumption of a single request dependent on all other requests being processed at the same time." It then *solves* it with a steady-state accounting method. The proposal's answer is to refuse — weaker than the state of the art, not stronger. |
| "Where Do the Joules Go?" (arXiv 2601.22076) | Direct | 1,858 configurations with batch-size sweeps, static-power accounting, causal knob→latent-factor→energy framework. Already in the repo's related work. |
| TokenPowerBench; SweetSpot (2602.05695); vLLM energy benchmarking (2509.08867); Bench360 | Direct | Batch-size energy curves are a crowded, actively published space. |
| *Silicon Showdown* (arXiv 2605.00519) | Partial | Apple M3 Ultra + RTX 5090, `powermetrics`, tokens/joule, prefill/decode separated — but **batch size 1 only**. Half the gap. |
| *Native LLM/MLLM Inference at Scale on Apple Silicon* (arXiv 2601.19139) | Partial | Continuous batching on MLX, 16 concurrent, M4 Max — but **no energy measured at all**; energy profiling listed as future work. The other half. |
| `ml-energy/zeus-apple-silicon` | Reviewer question | Sub-millisecond per-rail IOKit energy counters on Apple Silicon. A referee *will* ask why the attribution limit is accepted rather than instrumented away. The repo has the rebuttal (`docs/run_reports/2026-07-30-sweep-cv-paths.md`: 8 stars, README "explicitly disclaims accuracy… no calibration, no error bars, tests use mocked data") — **but the proposal does not carry it**, and this paper needs it far more than the MVP does. |

Net: the honest uncovered slice is "phase-resolved energy vs static batch size on Apple
Silicon/MLX, with floors." That is real and narrow — a workshop paper. The proposal instead leads
with the boundary rule, which is the *least* novel and *least* testable thing in it.

---

## Bottom line

Do not fund this as a paper. In its current form it spends four-to-six quiet nights — plus an
adapter and a floor/covariance subsystem that do not exist — to measure a large, well-known effect
with an instrument whose distinguishing capability the measurement does not need, and to prove a
boundary rule its own design cannot violate, on an axis the project's own strategy document does not
rank.

Fund it only in the rewritten form (a Q4 shape-of-E(B) stress test with a falsifiable ragged-cohort
refusal control, re-priced, with an explicit written trade against roadmap ranks 1–3) and only
**after** the MVP lands and the roadmap's single "designed extension" slot has been spent on
something from its own shortlist. Until then, the correct disposition is: build the A4 adapter as
desk work — it is cheap, it is already queued, and it is the infrastructure D-070 cl.3 wanted for
speculative decode — and spend no quiet nights on batching.
