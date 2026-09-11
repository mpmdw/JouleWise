# Counter-review: "Same Silicon, Different Stack: Floor-Gated MLX–llama.cpp Inference Energy on an M3 Max"

Reviewer: Opus 5, counter-review lens (charge: kill it). Ground truth: `scratchpad/desk` @ main.

## VERDICT: **WEAK** — do not fund as a paper.

Scores (1–10):

| Axis | Score |
|---|---:|
| novelty | **3** |
| feasibility | **3** |
| mvp_leverage | **5** |
| venue_fit | **4** |
| original_goals | **3** |

Recommendation: demote to a 0-night desk note, or fold the artifact-parity
machinery into the already-ranked quantization-ladder axis (roadmap rank 5),
which needs the same conversion-provenance work and already carries a quality
gate. Do not spend the two (really three) nights.

The proposal is honestly written and self-aware — it flags its own confound and
its own ICPE ceiling. It is not incoherent. It is *dominated*: every night it
spends buys a result the project's own registry has pre-capped at L2
stack-vs-stack, at a moment when P1 is an unwritten MVP paper.

---

## FATAL FLAWS

### F1. The effect-size arithmetic is calibrated against the wrong floor — off by ~3×.

This is the flaw that kills the experiment plan as written.

The proposal sizes everything against "the ~5 J bar": 3 % = 5.77 J, 5 % =
9.62 J, "difficult only when the stacks are within roughly 2.6 %", and a
pre-night kill criterion at **7.5 J**.

But the ~5 J number is the project's *generic* statement of attribution-limited
sizing (`CLAIMS_STATUS.md` §1: "floor + claim-side bound ≈ 5 J"), and the
proposal's own primary cell is **7B decode**, whose measured diagnostic floors
are (`CLAIMS_STATUS.md` §2, `window_7bfloor_20260729`):

- absolute **6.294380135190098 J**
- comparative **13.998036715259254 J**

`docs/paper/draft-v1.md` §"detection floor": the cell's operative floor is the
**maximum** of the two → **≈ 14.0 J**, not 5 J. `DESIGN-MEMO.md` line 450
confirms the contrast gate resolves "both decode arm floors … and appl[ies] the
armwise maximum" — and one of this proposal's two arms is a 7B decode cell.

So the real bar is:

| Bar | J | as % of the 192.39 J 7B decode cell mean |
|---|---:|---:|
| proposal's assumed bar | ~5 | 2.6 % |
| proposal's pre-night kill threshold | 7.5 | 3.9 % |
| **actual applicable armwise floor (diagnostic)** | **~14.0** | **7.3 %** |
| floor + claim-side interval margin (cf. prefill synthesis half-width ~1.81 J) | **~16–18** | **8–9 %** |

Every number in §"Experiment plan" is therefore wrong in the direction that
matters. A 3 % stack difference does **not** clear. A 5 % difference does
**not** clear. The proposal's own gate ("kill if the pilot's conservative lower
estimate is below 7.5 J") would *pass* a study that is then guaranteed to be
refused at the floor gate after burning two quiet nights. That is precisely the
failure mode this project exists to prevent, committed inside a proposal whose
thesis is floor discipline.

Fixing this is not cosmetic: it forces the honest question "do MLX and
llama.cpp-Metal differ by ≥8 % in batch-1 decode energy at 7B/4-bit?" — and the
answer to that is F2.

### F2. The only effect size large enough to clear the floor is the size the artifact mismatch alone can manufacture.

The charge asked whether "same model artifact class" is well-posed. It is not,
and the failure is quantitative, not philosophical.

Batch-1 decode on unified memory is bandwidth-bound: energy tracks bytes moved
per token. The two arms do not move the same bytes.

- MLX 4-bit (default group_size 64, fp16 scale+bias): ≈ **4.5 bits/weight**.
- GGUF **Q4_K_M**: ≈ **4.8–4.85 bits/weight** average (Q6_K promotion on
  attention-output / FFN-down and higher-precision embed/output tensors).
- Realized 7B file sizes: MLX-4bit ≈ 4.2–4.3 GB vs Q4_K_M ≈ 4.6–4.7 GB.
  *(Flagged: from public artifact listings, not measured here — but the
  direction and rough magnitude are robust.)*

That is a **~7–9 % difference in weight bytes**, sitting exactly on top of the
~8 % effect the floor requires. A cleared result is therefore
**unidentifiable**: "llama.cpp uses 9 % more decode energy" and "Q4_K_M carries
9 % more weight bytes than MLX-4bit" are the same sentence. The paper's headline
number would be a quantization-format result wearing a runtime costume.

The escape routes both fail:

- Match bits-per-weight with **Q4_0** (4.5 bpw): now the arms differ in
  quantization *algorithm* and quality, and Q4_0 is a strictly worse quantizer —
  you have swapped a byte confound for a quality confound.
- Match quality with Q4_K_M: byte confound restored.

There is no GGUF quantization that is simultaneously byte-matched and
quality-matched to MLX 4-bit. The contrast is **structurally confounded at
exactly the effect scale it needs**. Contribution 4 ("keep the wording
'MLX-stack versus llama.cpp-stack'") is a *labelling* fix for an
*identifiability* problem. It renames the confound; it does not remove it.

And the project already knows this. `docs/research_question_bank.md` C5-1.8:
"where formats force different artifacts (MLX vs GGUF), the comparison is
stack-vs-stack, stated as such." `docs/research_question_registry.md` line 68 and
lines 128–131 set the ceiling at **L2 stack-vs-stack** and *forbid* "belongs to
the runtime" language. So contribution 4 is not a contribution — it is the
pre-existing guardrail on a pre-existing registry row, restated.

### F3. No quality gate — the project's own standard for cross-artifact energy comparison.

`docs/strategy/2026-08-06-impressiveness-roadmap.md` rank 5 (quantization
ladder) requires "one frozen source revision, reproducible conversions, **256-item
quality gate**, 32-item energy subset, stack-specific floors" — for comparisons
*within* one runtime across BF16/Q8/Q4. This proposal compares across two
runtimes *and* two quantization schemes with **zero** quality evaluation; its
only nod is "quantify output-token divergence," i.e. counting how much the
strings differ, which is not a quality measurement.

Worse, `docs/paper/related_work_draft.md` criticises Silicon Showdown for
exactly this: "unmatched runtimes and precision stacks and **no comparison of
model-output accuracy**." As written, this paper reproduces the flaw it
indicts, with a floor bolted on. A referee who has read the project's own
related-work section will make that observation in one sentence.

`C-023-OUTPUT-IDENTITY` (registry line 103) is explicit: "no quant/**runtime**
efficiency claim without equivalence or divergence report," and "fixed
output-token count is not fixed decoded work." The proposal fixes the output cap
at 512 and calls that parity. It isn't.

### F4. No llama.cpp adapter exists, and the desk estimate is off by roughly 2×.

`joulewise/adapters/` contains `mlx_runtime.py`, `vllm_runtime.py`,
`mock_runtime.py`, `mock_spec_runtime.py`, telemetry and transport modules —
**no llama.cpp anything**. `RuntimeBackend.LLAMA_CPP` exists in
`joulewise/schemas.py:211` as an enum value only; `adapters/__init__.py
resolve_runtime()` falls through to
`RUNTIME_UNAVAILABLE: "runtime backend 'llama_cpp' has no registered adapter"`.
The enum is a placeholder, not a capability. The proposal says "new harness work
is substantial but bounded" — the word doing the work there is "bounded," and it
is unsupported.

Scale reference: `mlx_runtime.py` is **1246 lines**, and the phase boundary it
emits is `phase_boundary_method: "first_token"` — a marker planted *inside* the
Python generation loop, monotonic-clock-stamped, aligned to the powermetrics
anchor, with prefill/decode `phase_start`/`phase_end` `RuntimeEvent`s and
item-level control/failure semantics. A llama.cpp arm must reproduce all of it
against a C API (or `llama-cpp-python`), plus Metal build provenance, plus
`docs/contracts/adapter_contracts.md` conformance, plus tests.

Then the *campaign* machinery. `DESIGN-MEMO.md` §units enumerates **U1–U10** of
desk work — successor bracketing engine, pinset schema v2, multi-cell mint,
three campaign packs, extraction specs, post-collection pin closure — for
D-117, which adds **only prefill riders to existing MLX plans on an existing
adapter**. This proposal needs all of that *again* for a second stack identity,
plus the adapter itself, plus conversion manifests, plus "multi-runtime
floor/contrast consumers." "2–4 weeks of desk engineering" is not credible; 6–10
weeks is the honest range, and it is 6–10 weeks of the same desk capacity P1
needs.

### F5. The night budget is wrong: it is three new nights, not two — by the proposal's own protocol.

The proposal's own artifact-parity protocol (contribution 2: "both arms must
share the upstream checkpoint revision") requires deriving the MLX artifact from
the same source revision as the GGUF. But the D-117 windows pin a **prebuilt
mlx-community artifact** with its own revision hash (see
`configs/examples/mac_mlx_local.json`: source
`.../mlx-community/Qwen2.5-7B-Instruct-4bit`, `revision` pinned;
`DESIGN-MEMO.md` line 208 pins "Exact Qwen2.5-7B stack identity"). A locally
re-converted MLX artifact is a **different stack identity** → a different cell →
the D-117 7B floor does not transport → you must mint a fresh MLX floor too.

That is the proposal's own listed kill criterion ("D-117's MLX floor cannot
legally transport to the exact contrast cell") — and its own plan *guarantees*
the trigger. Either:

- keep the prebuilt MLX artifact (D-117 floor transports, but "same source
  revision" parity is nominal — mlx-community's conversion settings are not
  recorded, so contribution 2 is unenforceable), **or**
- re-convert (parity real, but **3 new nights**: MLX floor + llama.cpp floor +
  contrast).

Either branch breaks a headline claim. The stated "five quiet nights total" is
the optimistic branch of a dilemma the proposal doesn't notice it has.

### F6. Silent on the residency/warm-cache asymmetry that makes the floors non-transportable.

The two floor windows are single-runtime-resident. The ABBA contrast window
alternates MLX and llama.cpp members. Two options, both bad, neither addressed:

- **Both resident**: ~9 GB of weights held simultaneously plus two process
  memory footprints. That is a different environment — different idle baseline,
  different memory pressure, different thermal state — from the single-resident
  floor windows that minted the floors being transported in. Floors are cell-
  scoped on "telemetry backend, metric, window type, workload profile, and
  **stack identity**" (`draft-v1.md` §detection floor). A dual-resident window is
  not the cell the floor was minted for.
- **Tear down and reload between members**: injects model-load energy and
  thermal transients inside the claim window and violates the frozen "warm
  model" boundary the proposal explicitly promises to preserve.

D-117's gamma window does swap models within one MLX process, so there is
precedent for *model* swapping — but not for *process/runtime* swapping, which
is strictly harder and adds a variance source that neither arm's within-stack
null block measures. Which brings the last point: the "maximum of the two decode
floors, never their sum" rule is (a) **not a contribution** — it is verbatim
existing doctrine (`DESIGN-MEMO.md` line 481: "Ensure gamma takes the maximum of
the two decode arm floors, never their sum"; line 450: "apply the armwise
maximum"), and (b) **anti-conservative here**, because a comparative floor is
measured from a null in which "labels are deliberately made identical"
(`draft-v1.md` §detection floor), and no such null can exist for a cross-stack
pair. Both within-stack nulls are blind to runtime-switch variance. The proposal
imports a rule validated for two cells of one runtime into a setting where its
validating construction is unavailable.

---

## SECONDARY OBJECTIONS

**Novelty (d).** MLX-vs-llama.cpp on Apple silicon is a heavily trodden
comparison in the grey literature and is Silicon-Showdown-adjacent in kind. The
one differentiator is the floor gate — which is the **MVP paper's** contribution,
not this paper's. Strip the floor and nothing here is new; keep the floor and the
new content reduces to "we applied C1–C7 to one more pair of conditions." The
registry ceiling (L2, descriptive, stack-conditioned, no causal attribution) means
the best possible outcome is: *"stack X used ~9 % more decode energy than stack Y
for one model, one workload shape, one machine, and we cannot attribute it, and we
did not measure whether the outputs were equally good."* That is a table row, not
a paper.

Coverage is also thin against the bank's own framing of C5-1.8, which asks for
"MLX vs llama.cpp-Metal vs ollama … over a **shared shape grid**, n≥5." The
proposal delivers one model, one shape, two runtimes. It is the minimum viable
instance of an already-banked question.

**Venue (d/e).** The proposal's own assessment is right and should be taken at
face value: not an ICPE full-paper centerpiece. But it undersells the downside —
a workshop referee at EuroMLSys will ask "why is this not a quantization result?"
(F2) and "where is quality?" (F3), and the paper has no answer. Meanwhile
`impressiveness-roadmap.md` does not rank a cross-runtime axis **at all** among
its nine expansions; the nearest neighbour is rank 9 ("additional model families,
generic workloads" — "add only a model or device that changes the claim, not
merely the size of a results table"), and rank 1 carries the standing
instruction to "**prohibit breadth work from consuming**" the core nights. This
proposal is breadth work asking for core nights.

**Original goals (f).** It serves **none** of Ed's named mechanism axes —
speculative decoding, MTP, MoE routing, KV/attention, split inference — and the
proposal concedes this. Its claimed service is "exercises the intended
swappable-runtime harness," i.e. **modularity**, which is **P3** in the ratified
priority stack and is *explicitly sacrificeable if it costs P1/P2*. This costs
P1/P2 (6–10 weeks of desk capacity and 2–3 nights). Under the stack's own rule,
that is a decline. The claim that it "establishes the substrate those later
mechanisms require" is also weak: the mechanism studies (roadmap rank 7) name
speculative decode on a *forked or instrumented* runtime with proposal/acceptance
events — a llama.cpp *adapter* is not that substrate, and the roadmap recommends
external-draft spec-decode as the first mechanism precisely because it gives a
same-target on/off contrast with **no artifact mismatch at all** — the exact
property this proposal cannot have.

**One thing done right.** Section §Risks is genuinely good — the kill list is
specific, pre-night, and mostly correct in kind. It is wrong in *threshold* (F1)
and it omits the two triggers its own plan guarantees (F5, F6). That is a
proposal that reviewed its execution risk and not its design risk.

---

## THREE STRENGTHENING MOVES (if Ed keeps it anyway)

1. **Re-derive the entire sizing against the ~14 J armwise 7B floor, then let
   the arithmetic decide.** Set the pre-night gate at **lower interval edge >
   18 J (≈ 9.4 %)**, not 7.5 J. Run the daytime pilot *first, this week, at zero
   night cost*: build nothing but a throwaway `llama-cli`/`mlx_lm.generate`
   timing-and-power comparison at 7B/128-in/512-out, and compute
   `(E_llama − E_mlx)` from the diagnostic corpus scale. If the pilot gap is
   under ~10 %, **the paper is dead before any adapter is written** — that single
   afternoon is the highest-value action in this whole proposal, and it should be
   the gate on funding the desk work, not a step inside it. Publish the refusal
   in the MVP's limitations if it fails; that costs nothing and is on-thesis.

2. **Convert the confound into the contribution: make it a bits-per-weight
   study, not a runtime study.** Pre-register the *measured* weight-byte totals
   and realized bits-per-weight of both artifacts, and predict decode energy from
   bytes-per-token under the bandwidth-bound model. Then the paper's claim
   becomes falsifiable and identifiable: *"cross-stack decode energy is predicted
   within X J by weight bytes alone; the residual bounds the runtime-attributable
   term at < Y J, which is below/above our floor."* That converts F2 from a fatal
   confound into a covariate, upgrades the result past a bare L2 pairwise
   contrast, and — critically — a residual that is *below floor* is a publishable
   refusal ("no runtime-attributable term resolvable above bytes"), so the study
   has a positive outcome in both branches. This also merges cleanly with roadmap
   rank 5, which needs the same conversion-provenance apparatus.

3. **Add the quality gate and fix the two unbudgeted triggers.** (a) Adopt rank
   5's 256-item quality screen on both artifacts — it runs *outside* quiet
   windows at zero night cost and is the difference between this paper and the
   Silicon Showdown critique the project already published. (b) Decide the
   artifact-provenance dilemma explicitly and budget **three** new nights, not
   two, if re-conversion is chosen — or drop contribution 2's "same upstream
   revision" language and state honestly that MLX conversion settings are
   unrecorded. (c) Pre-register the residency policy for the contrast window
   (both-resident vs reload) and mint the floors **under that same residency
   condition**, or the floors do not transport and the window is refused after
   collection.

---

## Summary for the funder

Wrong bar (5 J assumed, ~14 J actual), a confound the same size as the only
clearable effect, no quality gate the project's own roadmap demands, an adapter
that does not exist behind an enum that suggests it does, and a night budget
that is 2 when the plan implies 3. The proposal is well-written and honest about
its ceiling; the ceiling is just too low for what it costs. **Spend the
afternoon on move 1. Do not spend the nights.**
