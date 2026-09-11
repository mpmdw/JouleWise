# Counter-review — "Windowed Attention Under an Attribution-Limited Energy Instrument"

Reviewer: Opus 5 counter-reviewer (portfolio referee, adversarial charge).
Target: `scratchpad/portfolio/prop-attention-variant-energy.md` (final block, L5158–5212).
Ground truth: `scratchpad/desk` @ main. Every repo claim below is cited by path.

## VERDICT: **WEAK** — kill as written; a different, cheaper study survives underneath it.

Scores (1–10): **novelty 5 · feasibility 3 · mvp_leverage 5 · venue_fit 5 · original_goals 6**

The proposal deserves credit for one thing and should be read as honest about it:
it *self-demotes* the assigned KDA/GQA four-way to a same-checkpoint ablation and
says so plainly. That is exactly the behaviour the brief asked for. Unfortunately
the surviving ablation is itself infeasible on this stack, logically
self-contradictory at the only cell that carries an effect, and duplicates a
question the repo already banked in a form that needs **no runtime work at all**.

---

## F1 (FATAL). No admitted checkpoint on this stack has a sliding-window path in the pinned runtime.

The proposal's entire experiment rests on "one MLX-supported, 4–7B-class
checkpoint whose native sliding-window mask can be changed to full attention
without changing weights." Checked directly:

- Locally mirrored artifacts (`/Users/edr/jw_models/mlx-community/`) are exactly
  five: `Qwen2.5-0.5B/1.5B/7B-Instruct-4bit`, `Qwen3-4B-4bit`,
  `Qwen3.5-122B-A10B-4bit`.
- In pinned `mlx-lm` (`/Users/edr/code/JouleWise/.venv/.../mlx_lm/models/`), the
  files that reference `sliding_window` are: `olmo3`, `gemma3_text`, `gemma3n`,
  `mimo_v2_flash`, `llama`, `exaone_moe`, `step3p5`, `cohere2`, `gemma4_text`,
  `afmoe`, `gpt_oss`, `baichuan_m1`, `ministral3`, `exaone4`. **`qwen2.py` and
  `qwen3.py` are not among them.**

So the intersection of {admitted, hash-pinned, D-117-relevant models} and
{models with an SWA path} is **empty**. The experiment requires acquiring,
converting, quality-gating, hash-pinning and admitting a *new model family*
(Gemma-3 / Ministral-3 / Cohere2 class). The proposal budgets zero desk work for
this and never names a candidate. Under D-074-class precedent a conditional
primary repin is its own multi-week gated exercise
(`docs/decision_log.md` D-073/D-074).

Worse for the proposal's numbers: its sizing anchor is "the diagnostic Qwen2.5-7B
decode level is about 192 J for 512 outputs" — a number transplanted from a model
that **categorically cannot run this experiment**. The actual subject would be a
3–4B-class SWA model at roughly half the weight-byte traffic. My own estimate
(mine, not the repo's; ±large): Gemma-3-4B-4bit at 4× a 1024-token window moves
KV-read bytes ~13% (weights ≈2.5 GB vs KV 0.22→0.57 GB per step), i.e. ≈**12–18 J
on a ≈110 J decode** — above the ~5 J bar but *below* the proposal's own 10 J
desk gate at the low end. The proposal's headline "10–80 J" range is anchored on
the wrong model and is optimistic by roughly a factor of two.

## F2 (FATAL). The output-identity gate is logically impossible at the only cell with an effect.

The proposal makes exact output-token identity a hard admission gate ("merely
similar prose is insufficient"), and simultaneously predicts a resolvable effect
only *above* the window. But above the window, forcing full attention **is** a
change to the attention mask on ~5/6 of layers; the attention outputs differ, the
logits differ, and greedy decoding diverges. Identity holds only below the
window — precisely the cell the proposal itself expects to be `<5 J` and
unresolved.

The repo saw this coming: the 2026-07-17 axis evaluation lists as a named risk
"Output divergence at long context can fail C-023-OUTPUT-IDENTITY gates
mid-campaign" (`docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json`,
attention axis, `risks`). The proposal quotes the discipline and then writes a
protocol that guarantees the gate fires. As written, the campaign is
pre-destined to a refusal that teaches nothing about attention.

Second-order: forcing *global* attention on layers **trained** local is
off-distribution. Quality is therefore not matched either — so even if one waived
identity, the contrast confounds "KV traffic" with "degraded model." The D-070
quality-equivalence control is unsatisfiable in this design.

## F3 (MAJOR). The repo already adjudicated this axis and scored it low; the proposal contradicts that record without engaging it.

`docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json`, attention
axis, `summary`: *"The attention-mechanism half is currently weak: no MLA/GQA or
SWA/full pair survives single-axis scrutiny … llama.cpp's `--swa-full` is a
cache-allocation toggle not an attention toggle … **no MLA weight-absorption or
SWA-mask-disable flag was established**"*; enrichment verdict *"low-medium
marginal for attention mechanisms today since C5-1.2/RQ-KV-GROWTH already carry
the context/KV-scaling question."*

And one day before this proposal, `docs/strategy/2026-08-06-impressiveness-roadmap.md`
L146: *"KDA/hybrid comparisons currently involve cross-model confounding and
**unverified long-context execution**"*; L148: *"No tracked repository document
uses 'KDA' as a governed project axis."* The roadmap's rank-7 mechanism slot
costs *"2–3-week desk feasibility gate; if passed, another 6–12 weeks and roughly
2 nights"* and its **recommended first choice is external-draft speculative
decode, explicitly because KDA is confounded.**

A proposal that re-opens a ranked-and-deprioritised axis owes the reader a reason
the prior adjudication was wrong. This one does not cite it at all. Note the
sharpest irony: the *only* readily-available MLX lever, `--max-kv-size →
RotatingKVCache` (`mlx_lm/models/cache.py:410`), is a cache-eviction policy — and
the proposal's own kill criterion says "Never reinterpret a cache-allocation flag
as an attention mechanism." The proposal forbids itself the one thing that works
out of the box.

## F4 (MAJOR). Forking the runtime breaks the pin the custody chain is built on.

There is no SWA-disable flag; the toggle must be a **source patch to
`mlx-lm`**. The proposal's manifest field "runtime commit" acknowledges this in
passing and then treats it as free. It is not: the D-117 acceptance regime, the
issued ledger, admission gates and hash-bound custody all key off the pinned
runtime identity. A patched fork is arguably a different instrument stack
requiring its own calibration acceptance — and a patched attention path is
exactly the "runtime fallback kernels can silently make a subject execute a
different path than its architecture label" failure the axis evaluation names as
a risk. The proposal lists "MLX silently falls back to another cache/kernel" as a
kill criterion but proposes no mechanism to *detect* it beyond a config digest,
which cannot see kernel dispatch.

## F5 (MAJOR). Night budget doubles the paper's cost for a P3 axis.

D-117 funds three windows (3.14 + 3.24 + 2.80 h). This proposal adds **three
more** ("Native-window floor", "Forced-full floor", "Science contrast", each
2.5–4 h) — a 100% increase in Ed's quiet-night spend, plus a new-model admission
program, plus a runtime fork. Under the ratified paper-first priority stack
(P1 MVP, P2 ICPE, **P3 modularity sacrificed if it costs P1/P2**), this is P3
work bought with P1 currency. History says the nights are not cheap: the project
has run windows A and B since 2026-06-09 and **both verdicts FAILED**
(`WINDOW_STATUS.md`), with `CLAIMS_STATUS.md` §1 reading *"VALID — minted,
mainline, citable: **NONE at this checkpoint.**"*

## F6 (MODERATE). Unverifiable citation.

`[H200 attention-energy study](https://arxiv.org/abs/2605.11999)` carries the
load-bearing "up to roughly half of request energy" sizing prior. I could not
verify this identifier; it should be treated as unconfirmed until checked. The
Kimi Linear / Moonshot claims (75% KV reduction, ~6× throughput) are consistent
with the public model card and are correctly labelled as *not* energy
measurements — that part is well handled.

## What is actually good here

- The demotion of the KDA four-way to a matched ablation, with the confound
  named (MoE + MLA + tokenizer + training all move together in Kimi Linear), is
  exactly right and is the single best paragraph in the proposal.
- Contribution 4 ("architecture labels alone do not license attribution") is a
  genuine, publishable methodological point that costs **zero nights**.
- The below-window null as a causal sanity check is a good instinct, correctly
  motivated.
- Venue honesty is broadly consistent with `impressiveness-roadmap.md`'s ladder,
  though "ICPE full-track becomes credible" omits that the roadmap's own ICPE
  full-track row also requires C1–C8, cross-day stability and an artifact-ready
  release — none of which this proposal funds.

## Three strengthening moves if kept

1. **Replace the mask hack with the already-banked context-slope row.** Run
   `RQ-AXI-ATTN-CONTEXT-SLOPE` (registry: fixed-decoded-output decode energy vs
   initial context length, within one named artifact) on the *already admitted*
   Qwen2.5-7B-4bit. This measures the same physical quantity — decode energy as a
   function of KV bytes read — with **no new model, no runtime fork, no
   output-identity contradiction** (outputs are trivially identical across a
   within-artifact sweep of one variable if you hold the prompt prefix and force
   fixed-length greedy decode), and it reuses D-117's admitted model and floors.
   Length is the free lever the brief already identifies. This is the honest
   paper hiding inside the dishonest one.
2. **If the SWA ablation is retained, replace output identity with a declared
   quality-equivalence band and pre-register the divergence.** State up front
   that above-window outputs *must* diverge, measure the divergence (token
   agreement rate, perplexity delta on a held-out set) as a reported covariate,
   and bind the claim to "windowed vs full KV access at matched decode length,
   with quality difference reported" — not to a mechanism claim. Otherwise the
   gate kills the campaign at the desk and the nights are wasted.
3. **Front-load a zero-night desk gate with a hard kill date**, per
   `impressiveness-roadmap.md` rank 7: (a) name one SWA checkpoint and prove it
   loads, converts to 4-bit, and passes the harness admission battery; (b) prove
   the mask toggle changes *dispatched kernels*, not just a config field, with a
   traced execution receipt; (c) time a pilot at both contexts and project the
   effect. If any of (a)–(c) fails, publish the feasibility refusal as
   contribution 4 and spend the nights on D-117. The proposal already gestures at
   this; it should be the *primary* deliverable, not a precondition.

## Bottom line

The submitted design cannot be executed on the admitted stack, and its central
admission gate contradicts its central hypothesis. The good news is that the
scientifically identical measurement — decode energy vs KV traffic — is already
banked, costs no runtime work, and rides D-117's own model. Kill the mask
ablation; fund the context slope.
