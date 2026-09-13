# Counter-review — `prop-quantization-ladder.md`
## "Quantization Under the Floor: Which Precision Rungs Are Measurably Different on Apple Silicon?"

Reviewer: Opus 5 counter-reviewer (adversarial charge: try to kill it).
Ground truth: repo checkout at `scratchpad/desk` @ `89b929c`, main.

**VERDICT: VIABLE — but only as a shrunk 3-rung BF16/Q4/Q8 ladder without a
quality gate.** As written (Q4/Q5/Q6/Q8, quality-equivalence contributions, four
extension nights) it is a WEAK proposal that invents two unverified rungs,
deletes the largest-effect arm the repo already designed for, imports an accuracy
axis that D-041 fences off, and hides a multi-month desk build behind a
truthful-looking night count. Every one of those defects is fixable at the desk
with no external dependency — which is why it survives where the mechanism
directions do not.

| Axis | Score |
|---|---|
| Novelty | 4/10 |
| Feasibility | 5/10 |
| MVP leverage | 7/10 |
| Venue fit | 6/10 |
| Original-goals service | 4/10 |

---

## 1. Which rungs actually exist at pinned revisions — the answer is: one

Asked directly. The repo's local artifact inventory is **4-bit only**:

- `/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit` (839 MB),
  revision `8b403126…ea677`, mirrored per R-014, D-016 provisional pick
  (`docs/decision_log.md:876-879`); `"quantization": {"name":"int4","bits":4}`
  in `configs/examples/mac_mlx_local.json`.
- `Qwen2.5-7B-Instruct-4bit` (4.0 GB), revision `c26a38f6…d9fed`
  (`configs/campaigns/qwen25_7b_decode_floor_v1/calibration_plan.json`).
- **No BF16/fp16 mirror of Qwen2.5-1.5B-Instruct. No Q5. No Q6. No Q8. Nothing.**

The repo's own frozen-on-paper ladder is `docs/specs/axi/sd_model_pair_scorecard.md`
§8, ladder ID `c5-1.12-qwen2.5-1.5b-mlx-bf16-q8-q4-v1` — **three levels: BF16,
Q8_G64, Q4_G64** — and every row is marked `NEEDS-VERIFICATION`. The document is
labelled "PRE-REGISTERED PROPOSAL — no model pair is selected and D-016 is not
amended", authorizing "no model download, campaign, quiet-Mac use, or claim". It
even pre-specifies its own shrink: "A pre-freeze capability check may
prospectively reduce the design to the two-level BF16/Q4_G64 ladder."

So the proposal's **Q5 and Q6 rungs are its own invention**, absent from the
repo's design, unverified at pinned `mlx==0.31.2` / `mlx-lm==0.31.3`, and
unmirrored. The evidence the proposal offers for their existence is that
"current MLX conversion exposes integer bit width" with a link to `convert.py`.

**That is precisely the inference the repo's own AXI-SC verdict forbids.**
`docs/specs/axi/sc_spec_decode_verdict.md` classifies "the parameter exists in
the API" as *not* support evidence — "Configured `num_draft_tokens`, model-call
shapes … may not be substituted for direct evidence"; a surface must be
*exercised*. The proposal applies the loose standard to itself and the strict one
to nobody. Q5 in particular is the least likely to exist as an optimized affine
kernel at this pin. The proposal does flag "local support on the pinned
JouleWise versions remains a required smoke gate" and carries a shrink clause
("If Q5 fails capability before freeze, shrink honestly to Q4/Q6/Q8") — honest,
but it means the headline four-rung ladder is a *hope*, and the paper's title
question is answerable only after a smoke that has not been run.

**And there is an authorization gate the proposal never names.** Deriving four
new artifacts from a new BF16 source revision is a **D-016 model decision**,
explicitly reserved to Ed ("artifact acquisition and any D-016 model decision
remain lead/Ed-owned"). The proposal presents conversion as desk work. It is a
ruling.

## 2. FATAL as written: it deletes the largest-effect arm and keeps only the sub-floor ones

This is the design inversion that would sink it at review.

The repo's motivation for a ladder (`docs/strategy/2026-08-06-impressiveness-roadmap.md`
row 5) is a **"Quality-gated BF16/Q8/Q4 quantization ladder"** whose value is to
"adjudicate the reported q4-vs-q8 anomaly" — **1–2 nights**, 4–8 weeks desk.

The proposal instead:

- **Demotes BF16 to a quality reference only, with no energy arm.** BF16 vs Q4 is
  ~4× the weight bytes — on a batch-1, bandwidth-bound decode this is by an
  enormous margin the most resolvable contrast available, and the one contrast
  guaranteed to clear any floor. It is dropped.
- **Demotes Q4–Q8 to "secondary"** — the exact contrast the roadmap says the
  ladder exists to adjudicate.
- **Promotes the three adjacent rungs to primary** — Q4–Q5, Q5–Q6, Q6–Q8 — which
  the proposal itself concedes are the most likely to miss the bar ("Q5–Q6 the
  most likely miss").

Net: the plan **maximizes night count and minimizes effect size**, then spends
its multiplicity budget (Holm over three adjacent contrasts) on the three tests
most likely to fail. If you were designing to produce a null, this is how.

## 3. Effect sizes vs the ~5 J bar, and whether refusal is the finding

Sizing evidence in the repo: ~**0.098 J/decode token** for 1.5B Q4 (non-claim
diagnostic; note historical corpora are voided for claim use under D-078's
time-anchor defect) → ~**50 J** for a 512-token decode. The ~5 J bar is
`floor + claim-side bound` "for the measured phase-contrast regime"
(`docs/paper/draft-v1.md:115`, `CLAIMS_STATUS.md:55`). **So the bar is ~10% of
total decode energy for the 1.5B/512 workload.** That is a brutal ratio, and the
proposal states it nowhere — it quotes 4–10 J estimates without saying they are
8–20% of the whole measured quantity.

My own first-principles estimate, offered as a check rather than a prior:
batch-1 decode on this stack is weight-bandwidth bound, so energy roughly tracks
weight bytes moved. Q4→Q5 ≈ +25% weight bytes, Q5→Q6 ≈ +20%, Q6→Q8 ≈ +33%. If
energy tracked bytes 1:1 the adjacent contrasts would be ~10–15 J and would
clear comfortably. They probably won't track 1:1 — which exposes the real
problem:

**INTERNAL VALIDITY, unaddressed: this ladder measures MLX kernel maturity, not
the energy cost of precision.** 4-bit and 8-bit are the well-trodden paths in
MLX; 5- and 6-bit affine kernels are, at best, less optimized. A measured
Q5 > Q6 inversion, or a Q5–Q6 gap larger than Q6–Q8, would be an artifact of
which kernels Apple/`ml-explore` tuned — not a fact about precision. A competent
ICPE referee will say "you have measured a software engineering roadmap." The
finding is still legitimate and publishable, but **only if framed that way from
the title down**, and the proposal frames it as a "phase-energy ladder", which
implies a precision→energy relationship it cannot isolate. This is the single
biggest missing caveat in the document.

**The proposal's own sizing evidence is self-refuting.** Its only quantitative
anchor is "an official MLX benchmark on a different Qwen model and M4 Max
reports adjacent generation-throughput differences of roughly 10–17%; **at
comparable power**, that suggests approximately 4–10 J". Different model,
different chip, throughput not energy — and the conversion runs through exactly
the latency⇒energy assumption that JouleWise exists to falsify. The project's
thesis and the proposal's power-analysis are in direct contradiction. Delete it
or replace it with a local daytime timing smoke.

**Is the refusal the finding?** Yes, and this is the proposal's strongest idea —
the title question ("which rungs are measurably different") is genuinely well
posed, and contribution 1 (a rung-specific resolvability map) is the version of
this paper that cannot fail. But be clear-eyed about what a refusal costs and
buys: four extension nights to report "our calibrated instrument cannot separate
Q5 from Q6 at 512 tokens" is a *methods* result that the floor-methodology
direction already delivers more cheaply. The refusal is worth publishing; it is
not worth four nights **unless** it is bundled with at least one contrast that
resolves loudly — which is exactly the BF16/Q4 arm the proposal deleted. And the
proposal's own escape hatch (workload length as the "permitted redesign lever")
means a Q5–Q6 refusal at 512 tokens can be dissolved at 2048 tokens, which
weakens "not resolvable" into "not resolvable at a workload we chose".

**Prefill:** the proposal correctly predicts 128-token prefill rung differences
will miss the bar, correctly says what that refusal means, and this is
corroborated by `docs/process_traces/2026-08-07-prefill-feasibility/` and D-117's
finding that even the 128-token prefill *contrast* is marginal. Fine.

## 4. Cost arithmetic: the night count is roughly right; the desk cost is off by an order of magnitude

Credit where due — I checked the night arithmetic and it broadly survives.
Against DESIGN-MEMO's measured budget (W-alpha 3.14 h, W-beta 3.24 h,
W-gamma 2.80 h; 50 science members = 10 absolute + 40 ABBA for a floor window,
40 for a contrast; overhead of 12 NEG8 + 7 references + 2 live calibration
brackets + 10 min untouched idle, ×1.2 margin):

- Q5/Q6/Q8 floor windows at 10 abs + 40 null each → ≈3.1 h each ≈ **9.4 h**.
- 4-arm contrast, 48 members vs gamma's 40 → ≈**3.1 h**.
- Total ≈ **12.5 h over 4 nights**. The proposal claims "approximately 12–15
  additional quiet-machine hours". **Correct.** It also correctly copies D-117's
  10+40 member design rather than improvising it. Good discipline.

Two real gaps:

1. **Per-rung floors mean per-rung *cells*, and the mint tool is single-cell.**
   `docs/phase_2/floor_mint_contract.md:41` targets one cell,
   `phase_energy_j.decode @ window_class phase`; DESIGN-MEMO F2 (a **blocker**)
   says the tool is "one plan and one artifact cell; `phase_energy_j.decode`
   only; `["phase","decode"]` only; no aggregate artifact over independently
   collected plans." D-117's U3 work order extends it to a **four-cell**
   aggregate (decode+prefill × 1.5B/7B) with component + aggregate pinsets. This
   proposal needs an **eight-cell** aggregate (decode+prefill × four rungs), each
   with its own pre-frozen `pin_requirements.v2` component pinset, plus
   postcollection pins, plus a **four-arm Williams-block estimator with Holm
   control that does not exist**. The proposal's desk paragraph names all of this
   in one 40-word sentence.
2. **Desk cost dwarfs night cost, and desk time is the binding constraint.** The
   roadmap budgets 4–8 weeks for the *three-level* version. This is the four-level
   version plus prefill riders plus an unimplemented quality screen plus a
   multi-arm estimator plus conversion/mirror/dual-hash machinery for four new
   artifacts. Realistically 8–12 weeks. The proposal's funding line — "the three
   D-117 nights plus four extension nights … with no new apparatus" — is
   technically true and rhetorically misleading, because nothing here is
   apparatus-limited; it is desk-limited, against a capstone deadline where P1 is
   the MVP paper.
3. **Failure correlation.** Seven quiet nights total, and each rung floor window
   is a single point of failure: lose the Q6 window to admission and **both**
   Q5–Q6 and Q6–Q8 die. This repo's night history (Window A: 43/50 bundles lost
   to a Ventura screensaver; night-hardening audits still surfacing blockers as
   of today's HEAD) does not support a 7-night serial dependency without a
   re-run reserve. None is budgeted.

## 5. FATAL as written: the quality axis is fenced off, and the harness for it does not exist

Contribution 3 promises "quality-qualified energy conclusions" — a rung is
"called quality-equivalent" only if a 256-item BF16 comparison clears −2 pp
overall and −5 pp per stratum.

**D-041** (`docs/decision_log.md:2239-2287`) fences exactly this:

> cl.3 — joined accuracy+energy data "may never produce **JouleWise accuracy
> claims**, pass@k-per-joule, leaderboard standing, or intelligence-per-joule."
> cl.4 kill/defer list — "**accuracy scoring beyond quarantined annotation**,
> judges/retries/pass@k/benchmark-score normalization."

A JouleWise-run, JouleWise-scored 256-item stratified screen producing a
JouleWise-issued "quality-equivalent" verdict is a JouleWise accuracy
determination. Whether it is *forbidden* or merely *requires a D-041 amendment*
is a lead/Ed ruling — but the proposal makes it a numbered contribution without
noticing that a decision stands in the way. That is an existing-material
compliance miss.

**And the screen does not exist.** The "256-item, four-stratum quality screen"
appears only inside `docs/specs/axi/se_analysis_plans_draft.md` §3 (`AP-QUANT-DRAFT`,
lines 283–294), a file headed "**DRAFT — design only; no campaign authority**",
"PROVISIONAL pending P2-015", claim ceiling **L2 or lower**, and itself dependent
on the unfrozen `sd_model_pair_scorecard.md`. There is **no implementation** —
no scorer, no MMLU/benchmark harness, no per-stratum gate anywhere in
`joulewise/`. The proposal's phrase "**Run the existing** 256-item, four-stratum
quality screen" is factually wrong: nothing existing is being run. That single
word is the proposal's worst sentence, because it converts a multi-week build
into an assumed capability.

**Does the paper need a quality axis to mean anything?** Honest answer: **partly
yes, and that is the direction's core tension.** "Q4 uses less energy than Q8"
without a quality qualifier is a trivially uninteresting statement — of course
fewer bits move fewer bytes; nobody trades precision for joules blind. The repo
agrees: `C-023-QUALITY-EQUIV-QUANT` (`docs/research_question_registry.md:105`) —
"no quantization efficiency or quality-neutrality claim without AP-level
equivalence rule." So a pure-energy ladder is a *resolvability* paper (fine, and
that is the honest title) but not an *efficiency* paper. The resolution is not to
build an accuracy harness; it is to **cite published quality numbers for these
exact rungs as related work** and confine JouleWise's own claim to
resolvability + energy. That keeps D-041 intact and cuts weeks.

## 6. Novelty, venue fit, original goals

- **Novelty: low.** Quantization energy is thoroughly trodden ground. The only
  novel element is the floor-gated *resolvability* framing — and that framing
  belongs to the floor-methodology contribution, not to quantization. Strip the
  instrument and there is no paper here; which is compliant with the hard
  constraint but also tells you the instrument is doing all the work.
- **Venue fit: honest and correctly calibrated.** "Strong capstone/CSCSU chapter
  and a credible EuroMLSys, HotCarbon, or ICPE Emerging extension; for an ICPE
  full paper, combine with artifact release and preferably wall validation or
  second-unit replication." That is the right ladder and the right hedge. No
  WT310E dependency, correctly argued.
- **MVP leverage: the best of any direction I have seen in this portfolio.** It
  keeps the exact D-117 128/512 single-request profile, consumes the D-117 **Q4
  decode and prefill floors directly as the fourth rung**, and reuses the intro,
  related-work gap, calibration method, floor composition, fail-closed protocol,
  attribution-limited result, and the model-size demonstration. That is genuine
  data reuse, not just method-section reuse.
- **Original goals: overclaimed.** The proposal says it "directly serves the
  original **quantization** … axes". Ed's original-goals list is speculative
  decoding, MTP, MoE routing, KV/attention variants, split inference, modular
  harness, energy-honest reporting. **Quantization is not on it.** It is in
  `capstone_scope.md` ("the model set spans quantization and size axes") as a
  *stack dimension*, not a mechanism. The proposal is right that it does not
  advance MTP/MoE/KV/split and right that it exercises the modular harness — it
  should just delete the word "original" from the quantization claim.

## 7. Three strengthening moves

1. **Shrink to the ladder the repo already designed: BF16 / Q4 / Q8, three
   arms, two extension nights.** Q4's floor comes free from D-117. Mint two new
   floors (BF16, Q8), run one 3-arm contrast window. BF16–Q4 is a guaranteed
   loud result (~4× weight bytes) that anchors the paper; Q4–Q8 adjudicates the
   anomaly the roadmap actually cares about. Zero Q5/Q6 capability risk, ladder
   lineage matches `sd_model_pair_scorecard.md` §8 verbatim so the frozen design
   is reused rather than reinvented, and the night count halves. If Q5/Q6 smoke
   *does* pass at the pinned version, add them later as a second-order figure —
   as *exploratory* rungs, not primary contrasts.
2. **Delete the quality gate; cite it instead.** Replace contribution 3 with a
   related-work table of published task-quality deltas for these exact rung
   families, and restrict JouleWise's claim to "energy resolvability at named
   rungs, quality qualified by external evidence." This preserves D-041 intact,
   removes the largest unbuilt component from the desk list, removes a D-041
   amendment from the critical path, and honestly answers the "does it mean
   anything?" objection. If Ed *wants* a quality axis, it is its own decision
   and its own quarter — not a bullet inside a quantization proposal.
3. **Front-load a two-hour daytime capability-and-sizing smoke, and rewrite the
   sizing section around it.** Before any night is committed: (a) convert BF16 →
   Q8 (and Q5/Q6 if you must) at the pinned mlx, load each, verify token
   identity and memory; (b) run wall-clock tok/s and mean-power-free duration
   for each rung on the exact 128/512 workload. That replaces the M4-Max/
   different-model/"at comparable power" extrapolation — which contradicts the
   project's own thesis — with local evidence, and it directly evaluates the
   proposal's own kill criterion ("a daytime timing smoke predicts two adjacent
   effects remain below 5 J") *before* the D-016 amendment, not after four
   nights. Add to the plan: an explicit statement that adjacent-rung differences
   may reflect MLX kernel maturity rather than precision, and a pre-registered
   re-run reserve night, since seven serial nights with no slack against a
   capstone deadline is not a schedule.
