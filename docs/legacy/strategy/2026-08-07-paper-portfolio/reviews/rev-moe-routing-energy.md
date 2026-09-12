# Counter-review — `prop-moe-routing-energy.md`

**Reviewer:** Opus 5, adversarial counter-review. Ground truth: desk checkout at `89f28bf`
(main), D-117 + design memo, `CLAIMS_STATUS.md`, `docs/research_question_registry.md`,
`docs/run_reports/2026-07-30-sweep-mechanisms.md`,
`docs/run_reports/2026-07-07-flagship-qwen35-122b.md`,
`docs/run_reports/2026-07-29-modularity-survey.md`, and **direct inspection of the installed
runtime** at `/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/` plus the
local artifact config at `/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit/`.

**VERDICT: VIABLE** (with two blockers that must be closed before any night is committed)

| axis | score |
|---|---|
| novelty | 6 / 10 |
| feasibility | 4 / 10 |
| mvp_leverage | 5 / 10 |
| venue_fit | 6 / 10 |
| original_goals | 8 / 10 |

This is the better of the two proposals I was assigned, and it survives a serious attempt to
kill it. It does not survive intact.

---

## The existing-material question, answered from the runtime source

The charge asked whether a Qwen MoE variant exists on MLX at a servable size with per-token
expert-activation observability. I checked the installed code rather than the model card.

**Artifact: EXISTS, pinned, already exercised.** `Qwen3.5-122B-A10B-4bit` is present at
`/Users/edr/jw_models/mlx-community/`, and `docs/run_reports/2026-07-07-flagship-qwen35-122b.md`
records 3/3 reps `validate-bundle --strict` green, rev `e9c67b0`, 65 GB on disk, 68.9 GB peak,
46 tok/s decode, 12.8 s warm load, gross CV **0.3 %** across reps (the tightest in the corpus).
The ~304 J / 512-token diagnostic the proposal cites is real (303.5 / 303.5 / 305.1 J) and is
correctly labelled as planning-only. The claim is not invented.

**Architecture: the proposal's numbers are exactly right.** From the local `config.json`
(`text_config`): `num_hidden_layers=48`, `num_experts=256`, `num_experts_per_tok=8`,
`hidden_size=3072`, `moe_intermediate_size=1024`, `shared_expert_intermediate_size=1024`,
`decoder_sparse_step=1`. So all 48 layers are MoE, giving 48 × 8 = **384** routed
expert-layer activations and 48 shared activations per token — as stated. Per routed expert:
3 × 3072 × 1024 = 9.44 M params; × 8 × 48 = **3.624 B** routed-active. Halving k removes
**1.812 B**. The proposal's "about 1.81B, roughly 18 % of the advertised 10B active" is
arithmetically exact. Credit.

**Runtime: the knob is real and the observability gap is real.** `qwen3_5_moe.py` subclasses
`qwen3_5.py`, which imports `Qwen3NextSparseMoeBlock as SparseMoeBlock` from `qwen3_next.py`
— so the proposal's citation of `qwen3_next.py` is **correct**, not the mismatch it looks
like. I had that queued as a hit and withdrew it. The block reads:

```python
gates = mx.softmax(self.gate(x), axis=-1, precise=True)
k = self.top_k                                    # = args.num_experts_per_tok
inds = mx.argpartition(gates, kth=-k, axis=-1)[..., -k:]
scores = mx.take_along_axis(gates, inds, axis=-1)
if self.norm_topk_prob:
    scores = scores / scores.sum(axis=-1, keepdims=True)
y = self.switch_mlp(x, inds)
```

Three consequences, two favourable:

1. **`routing_top_k_override` is a one-line config change** (`num_experts_per_tok`). No source
   patch needed for the *intervention*. Feasible as claimed.
2. **`norm_topk_prob` defaults to `True`** (`qwen3_5.py:51`, and the artifact does not
   override it). So forcing k=4 **renormalizes the gate mass** and preserves output scale.
   This is important and the proposal does not know it: the obvious "k=4 produces scaled-down
   garbage" failure mode is structurally excluded. The quality risk is real but it is
   distribution shift, not numerical collapse.
3. **`inds` is a live intermediate, never returned.** Per-token expert IDs require a source
   patch to `Qwen3NextSparseMoeBlock`. The proposal's "current MLX code calculates those
   indices internally but does not expose them as evidence" is exactly right.

So the existing-material constraint is **satisfied** — better than for most of this portfolio.
The problems are elsewhere.

---

## BLOCKER 1 — The contrast has no floor for arm B

The proposal budgets "one exact-stack floor window" using "the proven 10-absolute plus 40
A=A null design". That produces **one** floor cell, for the native k=8 configuration.

But the k=4 arm is a *different config hash* → a different condition family → a different
stack identity under this repo's own rules. D-117 gamma's floor rule is
`cross_stack_armwise_max.v1`: "independently resolve the 1.5B and 7B decode cells and take
their maximum, never their sum." Both arms need independently resolved floors. The design
memo is emphatic about the general principle — *"never borrow a decode floor for prefill"*,
and prefill riders "do not automatically transport" to a differently-parameterised workload
without "either exact matching prefill floor cells or a separately predeclared and justified
transport rule."

A k=8 floor is precisely a borrowed floor for the k=4 arm. As designed, the contrast cannot
be governed. The fix is cheap if made now and expensive if discovered at the arm gate: split
the null half into 20 members at k=8 and 20 at k=4 (or run 10-absolute + 20 + 20 in one
window), or pre-register an explicit transport ruling with justification. Either way the
proposal's window count and member schedule change, and its "5 nights, 14–16 h" figure is
understated.

## BLOCKER 2 — The effect/floor ratio is asserted against the wrong denominator, and the kill gate is set below the largest measured floor

> "use **40–120 J/request** as the uncertain planning range. Even its low end is about 8× the
> 5 J bar."
>
> Kill if "a pessimistic desk timing proxy … projects under **15 J**".

Two problems.

**(a) The "5 J bar" is a document-level prose constant; the measured floors are 2–3× larger.**
`CLAIMS_STATUS.md` line 55 gives "floor + claim-side bound ≈ 5 J", but eight lines below it
records the only actually-minted comparative floor: **13.998036715259254 J** for the 7B decode
cell, on an absolute-cell member mean of **192.386233 J** — i.e. the comparative floor is
**7.3 % of member energy**, and the absolute component (6.294380 J) is 3.3 %. On this
instrument, floors have empirically scaled with member energy, not sat at an absolute ~1 J.
(The ~1 J attribution limit is one *component*; at 7B it is not the binding one.)

A 122B member at 1024 output tokens is **~597 J** (583 mJ/output-token measured × 1024 —
note this, not "roughly 110 J at 1,024 tokens", is the request energy; see the prose defect
below). Scaling the one measured precedent forward, a projected comparative floor of
**~44 J** is the honest central estimate, with a plausible range of ~25–90 J.

Against that, the proposal's own 110 J central effect is **~2.5×** the floor, not 8×; its
40 J low end is **below** it. The proposal is not obviously wrong — the flagship report's
0.3 % gross CV suggests this stack may be unusually repeatable, and an attribution-dominated
floor of ~5–10 J is genuinely possible — but it asserts the optimistic branch without
engaging the one measured precedent that contradicts it. The honest statement is:
*effect/floor is somewhere between ~1.2× and ~20× and the floor window is the experiment that
decides it.*

**(b) The 15 J desk kill gate is below the largest already-measured floor (13.998 J).** A gate
set at 1.07× the biggest floor this project has ever minted cannot fail for any reason that
matters. It must be expressed as a multiple of the *projected floor for this cell* — I would
demand ≥3× — not as a fixed joule literal inherited from a different model's regime.

**(c) The physics may cut against the proposal.** Decode here is bandwidth-bound. Per-token
weight traffic ≈ routed 3.62 B + shared 0.45 B + LM head 0.76 B (`tie_word_embeddings: false`,
vocab **248320** × 3072) + attention ≈ 6.3 B params at ~4.25 effective bits (group_size 64,
affine) ≈ **3.35 GB/token**. At the measured 46 tok/s that is **~154 GB/s** — roughly 40 % of
the M3 Max's ~400 GB/s, whereas dense Qwen2.5-7B (0.376 J/tok at ~28–36 W → ~93 tok/s ×
4.2 GB) runs at **~390 GB/s**, essentially at peak.

That gap is the real story: **batch-1 MoE on unified memory achieves ~40 % of the bandwidth
efficiency of dense inference**, because gathering 8 of 256 experts per layer is
dispatch-bound, not traffic-bound. Which means the k=8→k=4 saving will be **sublinear** in
removed parameters: the gather/dispatch cost per layer is roughly fixed, so halving k halves
the bytes but not the overhead. The proposal's proportional 18 % assumption is an upper
bound on the mechanism it is measuring. (Conversely, counting only per-token *read* traffic
rather than the advertised 10 B active gives 1.81/6.3 = 29 %, an upper-upper bound. The
truth is bracketed by dispatch overhead and nobody knows where.) This is simultaneously the
proposal's biggest risk and its most interesting potential finding — and it is unstated.

---

## FLAW 3 — The confound between expert budget and sequence content is treated as a quality question when it is an estimand question

The proposal correctly rejects cross-model MoE comparisons as confounded and correctly picks
a same-checkpoint intervention. But it then declares:

> "Native k=8 and forced k=4 differ **only** in routed-expert budget on one
> artifact/runtime/boundary."

That is false past token 1. Forcing k=4 changes the logits, which changes the greedy argmax,
which changes the emitted token, which changes the next hidden state, which changes **which
experts route** and **what the KV cache contains**. By token ~50 the two arms are generating
different text. With `max_tokens` pinned at exactly 1024 the *count* matches, but the two arms
are no longer "the same work minus four experts" — they are **1024 tokens of text X versus
1024 tokens of text Y**, and if arm B degenerates into a repetition loop (a classic
reduced-top-k failure) then Y has systematically different routing entropy, expert-reuse
locality, and cache behaviour. Repetition loops concentrate routing on few experts, which
*improves* gather locality and would **inflate** the measured energy saving beyond the
mechanism.

The repo already owns this gate: `C-023-OUTPUT-IDENTITY` — *"Fixed output-token count is not
fixed decoded work"* — is a registry row, and it is `status: candidate (C-023)` with
`AP owner: none-yet`. The machinery is **not built**. The proposal's response (an
"exact-output divergence report", and a quality gate that "kills 'quality-equivalent' wording
but may retain a trade-off paper") mis-frames it: divergence is not a caveat on the *wording*,
it is a bias on the *estimand*. The minimum honest addition is a **routing-locality
companion** — unique experts touched per layer, expert-reuse rate, and routing entropy per
arm — so that a divergence-driven locality shift can be distinguished from the budget effect
it is being credited to. The proposal already plans "expert-load/unique-expert summaries";
it just does not connect them to this confound.

The teacher-forced variant (replay arm A's exact token IDs through arm B's k=4 routing) would
eliminate the confound entirely at the cost of measuring a counterfactual rather than a
deployment. Worth at least a paragraph of adjudication; the proposal gives none.

---

## FLAW 4 — Instrumentation overhead is the most likely killer, and MLX's execution model makes it worse than budgeted

The proposal's ≤2 % decode-time overhead gate is right in spirit but underestimates the
mechanism. MLX is lazy and asynchronous. Exporting `inds` per layer per token requires
keeping 48 live arrays alive across the decode step, which prevents buffer donation and
kernel fusion around the MoE block, and any host readback forces a graph sync **48 × 1024
times per member**. The proposal's mitigation ("buffered routing evidence must be flushed
outside the measured decode interval") is the correct instinct and probably necessary, but
on-device buffering still materialises 48 × 1024 × 8 index arrays per member and still adds a
graph node per layer.

This is a desk-testable question and the proposal treats it as one — good. But note what a
failure means: an instrumentation-on run is a **different stack identity** from an
instrumentation-off run, so a patched `mlx_lm` cannot silently inherit D-117's runtime
identity. The instrumentation-on/off ABBA equivalence test the proposal names is exactly
`C-023-TELEMETRY-PERTURBATION` from the registry (`status: candidate (C-023)`, `AP owner:
none-yet`) — another unbuilt dependency it inherits without acknowledging.

## FLAW 5 — Undeclared properties of the chosen artifact

The proposal describes the target as "the already exercised, pinned `Qwen3.5-122B-A10B-4bit`
MLX artifact" and cites the *text* model card. The local artifact is not quite that:

- **It is a vision-language checkpoint.** Root config carries `vision_config`,
  `image_token_id: 248056`, `video_token_id`, `vision_start/end_token_id`, and
  `qwen3_5_moe.py`'s `sanitize()` explicitly **discards** every `vision_tower` / `model.visual`
  weight at load. So part of the 65 GB on disk is read and thrown away, which is why peak
  memory hit 68.9 GB. Model identity, artifact SHA, and the discarded-weight behaviour all
  need to be in the stack-identity table; citing the text model card's parameter counts for a
  VLM artifact is an identity mismatch a referee will catch.
- **It is a hybrid, not a transformer.** `full_attention_interval: 4` and
  `from .gated_delta import gated_delta_update` — 36 of 48 layers are GatedDeltaNet linear
  attention, 12 are full attention. The paper would place a hybrid-linear-attention MoE
  alongside D-117's dense Qwen2.5 transformers without saying so.
- **It is a reasoning model with a different tokenizer.** `vocab_size` **248320** vs Qwen2.5's
  151936/152064. Within the two MoE arms this is fine (same tokenizer, so the mJ/output-token
  companion is well-scoped). But the paper juxtaposes MoE results with D-117's Qwen2.5
  results, and `docs/contracts/token_normalization.md` forbids cross-tokenizer/cross-family
  per-token comparison without a J/char or J/byte companion or purely descriptive language.
  Unaddressed.
- **The quality screen the proposal promises has no harness support.**
  `docs/run_reports/2026-07-29-modularity-survey.md` records that model family is "MODULAR by
  omission" — qwen3.5-122b ran the identical path — but also that **"no chat-template/
  thinking-mode/multimodal seam exists at all … a chat/thinking model needs a new
  prompt-rendering seam."** Contribution 4 (a "frozen quality screen" with an overall pass
  rate and per-stratum breakdown) requires chat templating and task scoring on a *reasoning*
  model, and neither exists. This is a substantially larger build than the routing sidecar and
  the proposal budgets it as an afterthought.

---

## Novelty, honestly

The proposal oversells its position relative to the repo's own prior art.

`docs/run_reports/2026-07-30-sweep-mechanisms.md` already contains this idea, ranked and
costed. Its pairs table lists **"MoE top-k knob | Qwen3-30B-A3B, `num_experts_per_tok=8` |
same checkpoint, k=4 (config edit) | same weights | *Unverified but mechanically plausible* —
single-mechanism, same-weights knob"**, and its claims ranking puts "MoE top-k slope (same
weights)" at **rank 6 of 6** with "expert-FFN energy ~∝ k; maybe 20–40 % of J/tok". The
top-3 recommended first campaigns are spec decode, the quant ladder, and **MoE-vs-dense
matched-active** — not the top-k knob. So the proposal re-derives a repo-registered idea,
picks a *worse* artifact than the one already vetted for it, and does not engage the
adjudication that ranked it last.

The literature position is also weaker than claimed. arXiv 2606.21428 (the one Apple-silicon
MoE paper) already reports that **"routing itself is <9 % of MoE-block compute — the penalty
is total-parameter footprint, dispatch, KV pressure."** A paper titled *"What Does a Routed
Expert Cost?"* whose intervention is expert *budget* (not routing overhead) will be read as
answering the question 2606.21428 already answered, unless the framing shifts to what is
genuinely open: **the dispatch-bound sublinearity above**, and the matched-active-vs-matched-total
sign flip between arXiv 2504.17674 (+54 % vs dense, A100) and arXiv 2601.22076 (3.56× *less*,
H100/B200 batched) — which the sweep calls "a point of genuine confusion the literature hasn't
resolved cleanly." That is the paper. The k-knob is the *instrument* for it, not the thesis.

Governance, unmentioned: there is **no registry row for MoE routing energy**. The nearest is
`C5-1.9` ("MoE-vs-dense controlled ladder", `status: banked`, L2 after envelope and
denominator guards). Promotion requires a named RQ slot in `PROJECT_STATUS.md` and a data
plan that does not displace higher queue ranks. Also note `TASK_QUEUE.md` A7 (AXI-SE) already
fences this: **"routing-mechanism claims allowed only when auditable expert evidence exists"**
and requires AP-MOE-BATCH / the AP-5 MoE rider to be finalized *against P2-015 floors* — both
still `READY`, i.e. unbuilt.

## Prose defect worth fixing before anyone reads it twice

> "A permanently voided … diagnostic observed approximately 304 J for a 512-output-token
> request … Crude proportional scaling therefore suggests roughly **110 J at 1,024 tokens**;
> use 40–120 J/request as the uncertain planning range."

304 J at 512 tokens scales to **~608 J** at 1024 tokens (and the measured 583 mJ/output-token
gives ~597 J). The 110 J is 18 % of 608 — i.e. the **effect**, not the request energy — and
"40–120 J/**request**" mislabels the effect range as a request quantity. The arithmetic
underneath is right; the sentence says something false. In a metrology paper that is not a
typo, it is a credibility event.

---

## Three strengthening moves

1. **Swap the artifact to `Qwen3-30B-A3B-4bit` (~17 GB) and drop the 122B.** The repo's own
   sweep already verified this checkpoint exists and named it the MoE arm; it is a pure text
   MoE with no vision tower to load-and-discard, no 65 GB residency squeezing the page cache
   during a quiet window, no reasoning/thinking-mode seam gap, and a member energy small
   enough that the projected floor is a smaller fraction of a smaller number. Critically, it
   makes the **matched-active dense comparison possible in the same paper** — `Qwen3-4B-4bit`
   is *already present locally* — so one artifact swap converts a rank-6 knob study into the
   rank-3 campaign the sweep actually recommended, with the k-knob as the causal
   within-checkpoint leg that no prior work has. Keep the 122B as a single scale-context
   diagnostic, not as the claim vehicle.

2. **Fix the floor design and re-anchor every sizing number to a projected floor.** Produce
   **two** floor cells in the floor window (10 absolute + 20 null at k=8 + 20 null at k=4, or
   a second window), so `cross_stack_armwise_max.v1` has both arms. Replace the 15 J desk kill
   gate with **≥3× the projected floor for this cell**, where the projection is scaled from
   the one measured precedent (7B comparative floor = 7.3 % of member mean) and stated as a
   range. Publish the projection and its precedent in the paper — "we predicted our own floor
   from a prior cell and here is how the live mint compared" is a genuine methodological
   contribution that costs nothing.

3. **Promote routing locality from a summary statistic to a co-primary endpoint, and add a
   teacher-forced arm to the desk gate.** Report unique experts per layer, expert-reuse rate,
   and routing entropy per arm alongside joules; this is what separates "removing 4 experts
   costs N joules" from "the divergent text arm B generated happened to route more locally."
   Then reframe the thesis around the finding the physics actually predicts and nobody has
   measured: **batch-1 MoE decode on unified memory realises only ~40 % of the bandwidth
   efficiency of dense inference, so expert-budget savings are sublinear in removed
   parameters.** That claim is floor-gated, mechanism-level, contradicts the naive
   active-parameter model, speaks directly to the matched-active-vs-matched-total sign flip
   the literature has not resolved, and is exactly the kind of result that lifts this from a
   capstone chapter to an ICPE Emerging or EuroMLSys submission.

---

## Bottom line

The feasibility spine is sound and I verified it in source: the artifact exists and is pinned,
the k-knob is a config field, `norm_topk_prob=True` protects output scale, the effect is
plausibly large, the single-request boundary holds, and no borrowed apparatus is needed. This
serves Ed's highest-priority original axis (MoE mechanism) better than anything else in this
portfolio slice, and it reuses §§3–5 of the MVP draft essentially intact.

But the contrast currently has no floor for one of its two arms; the effect/floor ratio is
quoted against a prose constant rather than the one measured precedent, which cuts it from 8×
to plausibly ~2.5×; the kill gate is set below the largest floor ever minted here; the
output-divergence confound is filed as a wording risk when it is an estimand bias; and the
chosen artifact is a 65 GB vision-language hybrid reasoning checkpoint when a 17 GB text MoE
with a matched-active dense partner is sitting one download away and was already vetted by
the repo's own sweep. Fix the artifact, fix the floor, re-anchor the sizing — then it is worth
two nights.
