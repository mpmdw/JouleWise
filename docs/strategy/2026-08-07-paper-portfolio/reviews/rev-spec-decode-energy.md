# Counter-review — `prop-spec-decode-energy.md`
## "When Does Speculative Decoding Save Energy on a Mac? Floor-Gated Break-Even Curves"

Reviewer: Opus 5 counter-reviewer (adversarial charge: try to kill it).
Ground truth: repo checkout at `scratchpad/desk` @ `89b929c`, main.

**VERDICT: WEAK.** High ceiling, correct axis, honest hedging — but the proposal
mis-specifies the floor class it needs, understates the build by roughly a
quarter, and the repo's own banked evidence predicts that its headline
deliverable (a localized break-even acceptance threshold) does not exist in the
observable region on this stack.

| Axis | Score |
|---|---|
| Novelty | 7/10 |
| Feasibility | 3/10 |
| MVP leverage | 4/10 |
| Venue fit | 7/10 |
| Original-goals service | 9/10 |

---

## 1. The existing-material constraint: what actually checks out

Credit where due — several things the assignment asked me to attack are **fine**:

- **The draft+target pair exists and is resident-feasible.** All three artifacts
  are mirrored locally: `Qwen2.5-0.5B-Instruct-4bit` (276 MB),
  `Qwen2.5-1.5B-Instruct-4bit` (839 MB), `Qwen2.5-7B-Instruct-4bit` (4.0 GB)
  under `/Users/edr/jw_models/mlx-community/`. Target + draft co-residency is
  ~4.3 GB on a 128 GB machine. There is no memory story here; the
  "M3 Max holds concurrently" constraint is trivially satisfied. Tokenizer
  compatibility holds (Qwen2 vocab 151,936 across the family, per
  `docs/specs/axi/sc_spec_decode_verdict.md`).
- **MLX serves external-draft speculative decoding today.** Pinned
  `mlx-lm==0.31.3` / `mlx==0.31.2` exposes `--draft-model`,
  `--num-draft-tokens`, `speculative_generate_step(...)` with separate
  target/draft caches, and `stream_generate(draft_model=...)` dispatch
  (`sc_spec_decode_verdict.md` §A with line cites into `mlx_lm/generate.py`).
  A **lead-run live Metal probe on 2026-07-17 executed the exact
  1.5B-target/0.5B-draft pair** to completion, evidence SHA-256
  `559731f4…0645f11`. So generation is not the blocker.
- **`gross_energy_per_accepted_draft_token_j` is already policy-correct.**
  `docs/contracts/analysis_plans.md:159` already defines it as a *spec-on-only
  diagnostic*, with `gross_energy_per_committed_output_token_j` as the companion
  efficiency denominator. The proposal restates this correctly and does not
  smuggle accepted-token-J in as an efficiency metric. Good.
- **AP-SPEC exists** as `AP-SPEC-DRAFT` in `docs/specs/axi/se_analysis_plans_draft.md:209`.

So the proposal is not unmoored. Its failures are elsewhere and they are sharper.

## 2. FATAL: the floor class it needs does not exist, and is not on any work order

The proposal's primary metric is **paired `spec_on − spec_off` gross joules per
request**, and its floor window collects "three `gross_request` cells". That
choice is metrologically sensible (see §4) but it walks straight off the end of
the repo's minting machinery:

- `docs/phase_2/floor_mint_contract.md:41` — the ratified mint contract targets
  `phase_energy_j.decode @ window_class phase`.
- `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md` F2 (blocker):
  the current mint tool is "one plan and one artifact cell;
  `phase_energy_j.decode` only; `["phase","decode"]` only". D-117's own U3 work
  order extends it to **four phase cells** — decode+prefill × 1.5B/7B. It does
  **not** add a gross window class.
- `docs/contracts/analysis_plans.md:164` is explicit that the gross gate is not
  live: floor gate for `gross_request` is "**pending-P2-015** … otherwise **a
  dedicated calibration cell is required**."

So this proposal needs a floor artifact class that (a) does not exist, (b) is not
in D-117's U3, and (c) the analysis-plan contract flags as requiring its own
dedicated calibration cell. The proposal's desk list says "floor selectors" in a
six-word clause. That is a contract-and-mint build comparable in size to U3
itself, invisible in the plan and invisible in the budget.

**Corollary that also guts the MVP-leverage story:** because it needs gross
floors and D-117 mints phase floors, this paper reuses **none of the three
D-117 windows' claim products**. Its "builds on the MVP" is method-section reuse
(§§3–5, instrument characterization, limitations) plus a demonstration figure.
Every claim-bearing number in the mechanism chapter comes from its own two new
windows under a floor class nobody has built. Contrast with the quantization
direction, which consumes the D-117 Q4 floor directly as a rung.

## 3. FATAL: the repo's own dated verdict closes the observability route the proposal reopens

`docs/specs/axi/sc_spec_decode_verdict.md` is a **closed, dated applicability
finding**: `unsupported_for_joulewise(event_observability)`. Its revisit clause
is narrow and explicit:

> "External draft is revisited only after a **pinned-runtime upgrade** exposes
> an **exercised callback** carrying per-round proposal counts, running
> aggregate acceptance, and exact decode-step emitted slices."
> …
> "configured caps or reconstructed groups **do not trigger revisit**."

The proposal's answer is "the current MLX path must be **wrapped or narrowly
forked** to emit actual `tokens_proposed`, `tokens_accepted`, acceptance rate,
and exact committed bursts." Two problems:

1. **It is not a pinned-runtime upgrade.** The proposal quietly proposes to
   satisfy a closed verdict by editing the thing the verdict is about, without
   naming the decision that reopens it. That is a lead/Ed ruling, not a desk
   task. The proposal never says "this requires reopening the AXI-SC verdict" —
   it should, in its first paragraph. (To be fair to it: a fork *can* emit real
   proposal counts, because they are genuine local variables inside
   `speculative_generate_step` at `mlx_lm/generate.py:607-627`. This is real
   evidence, not the forbidden inference. The objection is procedural and
   metrological, not epistemic.)
2. **A forked runtime is a different measured stack.** The floor-mint pin set
   binds "model/runtime/config hashes"; `sc_spec_decode_verdict.md` itself pins
   per-file SHA-256 of `mlx_lm/generate.py`. Changing `generate.py` changes the
   stack identity for *both* arms and severs any inheritance from D-117-era
   calibration. The proposal collects its own floors, so this is survivable —
   but it must be stated, and the spec-off arm must run the *forked* runtime too,
   which the proposal never says.

**Unaddressed and serious: in-window instrumentation load.** The plan emits one
`decode_emission` event per decode step across a 256-token generation, in the
middle of a quiet-machine measurement whose instrument is *attribution-limited
at ~1 J per phase member* and whose bar is ~5 J. Callback + serialization work
inside the measured window is exactly the contamination class this project has
already been burned by (Window A: 43/50 bundles lost to a screensaver). Worse,
the instrumentation load is **asymmetric across arms**: spec-on has fewer decode
steps but more per-step payload; spec-off has one event per token. So it does
not cancel in the pairing. Nothing in the proposal budgets, measures, or bounds
this. A referee at ICPE will ask, and there is no answer in the text.

## 4. Phase-boundary well-posedness: the proposal dodges correctly, then pays for it

Asked directly: is energy-per-ACCEPTED-token well-posed under this project's
phase boundary? **Under phase resolution, no. Under gross_request, yes but
weakly.**

- Under spec-on, the **draft model performs its own prompt prefill**. If the
  prefill/decode split is anchored on the target's first committed token, the
  draft's prompt pass lands inside "prefill" and the phase now contains two
  models' prompt processing — a different physical object than the spec-off
  prefill carrying the same label.
- Inside "decode", the target's verify pass is a *batched K+1-token forward* —
  prefill-shaped compute wearing a decode label. Comparing "decode energy"
  across arms compares different mechanism compositions under a shared name.
- The proposal **sidesteps this by making `gross_request` primary** and
  explicitly attempting "no per-round energy attribution". That is the right
  call and I credit it. But note the cost: **the mechanism chapter is the one
  chapter of the paper with no phase resolution** — it abandons the project's
  signature contribution precisely where it would be most interesting, and it
  is the reason §2's missing floor class bites.
- Energy per *accepted* token: numerator = whole-request gross J including draft
  work, verify work, *and* rejected-proposal waste; denominator counts only
  draft-originated committed tokens and excludes the target's bonus token. It is
  a well-defined ratio and a legitimate mechanism-yield diagnostic. It is not an
  efficiency metric, it is undefined for spec-off, and the D-037 rider in
  `analysis_plans.md` already says so. Compliant. But the paper's *title*
  gestures at exactly the quantity it is contractually barred from headlining.

## 5. FATAL: acceptance rate is not manipulated — the break-even curve is observational and under-identified

The assignment asked how the proposal honestly *sets* acceptance rate as an
independent variable. **It doesn't.** It uses "a frozen, equal-token-shape prompt
roster spanning chat, code, and structured reasoning to generate acceptance
variation" and regresses paired Δ-energy on runtime-observed acceptance. Three
consequences the proposal never confronts:

1. **Effective n is the number of prompts, not the number of members.**
   Acceptance is a per-prompt property; 80 members over a handful of prompts
   yields a handful of distinct x-values. Contribution 2's headline is a
   *break-even threshold with an interval* — the root of a fitted line — and no
   estimator is named (Fieller? delta method?). Rooted-ratio intervals from ~6–10
   prompt-level points will be enormous. This is the most likely quiet failure
   mode: not a refusal, but a "break-even is somewhere between 40% and 95%"
   non-result that still cost two nights.
2. **No multiplicity control is specified**, unlike the sibling quantization
   proposal which names Holm. There are at minimum: on/off at two draft sizes,
   the size contrast, and a fitted threshold.
3. **Acceptance is a post-treatment mediator observable only in the spec-on
   arm.** Regressing the paired difference on a spec-on-only covariate is a
   descriptive model at best; any threshold statement is an extrapolation the
   claims ladder would push below L2. (Note: `se_analysis_plans_draft.md` sets a
   **claim ceiling of L2 or lower** for every plan in the file, including
   AP-SPEC-DRAFT, and is PROVISIONAL pending P2-015 floors.)

**The obvious manipulable lever is fixed by fiat.** The proposal pins the
proposal cap at **K=3** and then hunts for variation in prompt content. K is a
genuine, settable, pre-registrable independent variable (K=1,2,3,…), and draft
size is a second. The design uses the two weak levers and freezes the strong one.

## 6. Effect sizes vs the ~5 J bar — and the self-refuting prior

Provenance check: the ~5 J bar is `floor + claim-side bound`, "**for the measured
phase-contrast regime**" (`docs/paper/draft-v1.md:115`, `CLAIMS_STATUS.md:55`,
D-078 cl.11). The proposal imports it wholesale into a **gross_request** design.
That is not obviously the right bar in either direction — a gross window has two
request edges rather than an internal phase split, so its attribution term may
well be *smaller*. The proposal never re-derives it. Since its own floors will
define the real bar, all the "5 J ≈ 5% of request energy" arithmetic is
decorative.

On magnitudes: the ~192 J historical 7B 512-token member halved to "~96 J at 256
tokens" is flagged as non-claim extrapolation — fine, but note the historical
corpora are voided for claim use (D-078 time-anchor defect), so this is a
diagnostic-of-a-diagnostic.

**The killer is the repo's own smoke.**
`docs/process_traces/2026-07-17-dspark-dflash-smoke/README.md` (lead-run, Metal):

| mode | tok/s | accept/round |
|---|---|---|
| dspark | 45.8 | 2.60 |
| dflash | 40.4 | 2.45 |
| **baseline greedy** | **113.0** | — |

Speculative modes ran at **0.36–0.41× baseline throughput** on this class of
stack. Two models drawing power for 2.5× longer is not a break-even candidate;
it is a rout. If the mlx-lm external-draft path behaves similarly (different
mechanism family, so not dispositive — but it is the only local evidence there
is), then Δ-energy is large, positive, and monotone across the entire observable
acceptance range, **the break-even root lies outside the data**, and the
proposal's own kill criterion "the break-even is unlocalized" fires *after* the
nights are spent rather than before. The honest expected deliverable is one
sentence: "on this stack, external-draft speculative decoding never repays its
energy." That is a real result. It is not two quiet windows plus a quarter of
runtime engineering worth of result.

The counter-evidence the proposal leans on (`mlx-dspark` reporting 1.7–2.3× on
an M4 Pro) is a *different mechanism, different model family, different chip*,
and the proposal itself notes the contradiction and widens its prior to
−40 J…+100 J. A prior that wide is an admission that the desk gate cannot size
the effect, which means the gate cannot do the job the proposal assigns it.

## 7. Cost accounting the proposal understates

- **Nights.** Floor window: 3 cells × (5 absolute + 5 ABBA null blocks = 25
  members) = 75 science members, plus D-117's fixed overhead (12 NEG8 = 22 min,
  7 references, 2 live calibration brackets = 16 min, 10 min untouched idle,
  ×1.2 margin). Mechanism window: 80 members. Both land near or over the 4 h
  envelope depending on whether spec-on members are ~2.5× slower (see §6) — and
  if they are, the mechanism window blows the envelope and splits into a third
  night, which the proposal concedes.
- **The repetition counts are cut in half without justification.** D-117 floor
  windows are **10 absolute + 40 ABBA null = 50 science members per cell**
  (DESIGN-MEMO §budget, 3.14 h / 3.24 h). This proposal uses **5 + 20 = 25 per
  cell**. The operative floor is `max(absolute_component, comparative_component)`
  — a **max of two noisy estimates biases upward**, so halving n does not merely
  loosen the floor, it systematically *raises the bar the effect must clear*.
  Self-defeating, and it is the one number in the plan that should have been
  copied verbatim from D-117 rather than improvised.
- **Calendar.** The proposal advertises "a two-to-three-week desk feasibility
  gate" then two nights.
  `docs/strategy/2026-08-06-impressiveness-roadmap.md` row 7 — the roadmap entry
  for exactly this direction — says **"2–3-week desk feasibility gate; if passed,
  another 6–12 weeks and roughly 2 nights."** The proposal reproduces the gate
  and silently drops the 6–12 weeks. For a capstone on a submission clock with
  P1 = MVP paper, a hidden quarter is the single most consequential omission in
  the document.
- **Exact-output-identity gate.** The proposal's own kill criterion, correctly
  identified, citing a live mlx-lm greedy-divergence report at K=4. My read: the
  probability this gate fires is high — spec decode's exactness guarantee is
  distributional, and batched verify vs sequential decode differ in float
  reduction order. If identity fails, the contrast is a workload change, not a
  mechanism contrast, and the paper ends. Honest of them to name it; it does not
  stop it being a coin-flip on which a quarter is staked.

## 8. Existing-material compliance, venue honesty, original goals

- **Existing material:** artifacts PASS (all mirrored, no downloads, no D-016
  amendment needed). Runtime FAILS-with-caveat (requires forking the pinned
  runtime and reopening a closed dated verdict). Floor machinery FAILS (needs an
  unbuilt window class). No wall-meter dependency — correctly argued, and the
  argument that WT310E cannot validate phase allocation is right.
- **Venue honesty: the best part of the document.** It explicitly disclaims
  "first speculative-decoding energy study", names EuroMLSys / ICPE emerging as
  the destination if the interval is broad, and positions the capstone version as
  an *optional* chapter on an independently complete metrology paper. That
  optionality is the proposal's real strength — a null here does not damage P1.
- **Original goals: bullseye.** Speculative decoding is the first-named axis on
  Ed's original list, and the roadmap explicitly recommends it as the *first*
  mechanism choice. It also genuinely exercises the modular-harness vision
  (swappable draft/target/policy). If any direction deserves the mechanism bet,
  it is this one — which is why the flaws above are worth fixing rather than
  walking away from.

## 9. Three strengthening moves

1. **Make K the manipulated variable and drop the break-even curve as the
   headline.** Pre-register a K ∈ {1, 2, 3, 4} sweep at a single draft size
   against a fixed prompt, with acceptance as a *measured mediator*, not the
   x-axis. K is settable, pre-registrable, and generates a monotone design with
   a real dose-response; the current design has no manipulated variable at all.
   Retitle to "Does speculative decoding ever repay its energy at batch 1?" —
   a question this instrument can actually answer, with a directional
   floor-gated answer either way. Keep acceptance-vs-Δenergy as a secondary
   descriptive figure with an honest prompt-level n.
2. **Move the go/no-go evidence to the front and make it cheap.** Before any
   runtime fork, run a *non-claim, daytime, wall-clock-only* spec-on/off timing
   pilot on the 7B/0.5B pair with the stock pinned runtime (generation already
   works — no instrumentation needed for tok/s). If spec-on is slower than
   baseline, as the DSpark/DFlash smoke predicts, the energy answer is settled
   at essentially zero cost and the whole fork/floor/AP build is never funded.
   This is a two-hour desk task that currently sits *after* two to three weeks
   of instrumentation work.
3. **Fix the floor story explicitly, or change the primary metric.** Either
   (a) name the `gross_request` floor-class build as a first-class work item,
   fold it into D-117's U3 pinset-v2 scope so one mint effort serves both, and
   restore the 10+40 member design; or (b) if that is too much, re-scope the
   primary metric to `phase_energy_j.decode` with an explicit, pre-registered
   statement of how the draft's prompt pass is attributed — and accept the
   phase-comparability caveat in the text rather than avoiding it by metric
   choice. Additionally: run the spec-off arm on the *same forked runtime*, and
   pre-register a measured bound on in-window instrumentation energy (an
   instrumented-vs-uninstrumented spec-off pair) before either arm is claimed.

**Bonus route worth a paragraph in any revision:** `mlx-dspark`/`mlx-dflash` are
already vendored and smoked locally, and the smoke README notes they surface
**per-round acceptance and target-forward counts — precisely the observability
surface pinned mlx-lm lacks**. That path needs no fork of the calibrated runtime.
It costs a different target model (Qwen3-4B), a D-016 touch, a non-mirrored
auto-fetched drafter, and a thinking-policy pin (D-074) — but the proposal does
not even mention it, and it may be the cheaper road to the same paper.
