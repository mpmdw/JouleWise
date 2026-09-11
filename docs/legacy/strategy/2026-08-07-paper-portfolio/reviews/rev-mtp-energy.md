# Counter-review — `prop-mtp-energy.md`
**"Does Multi-Token Prediction Save Joules? A Detection-Floor-Gated Study on Apple Silicon"**
Reviewer: Opus 5 (counter-reviewer, adversarial charge). Ground truth: `desk` @ `89b929c`.

## VERDICT: **WEAK**

More precisely: **KILL as a standalone funded direction; survives only as a ~zero-cost desk rider
on the speculative-decoding proposal.** It is not a dishonest proposal — it self-gates behind a
feasibility check and explicitly refuses to displace D-117, which is more discipline than most of
this portfolio will show. But it was given an instruction it did not follow: *"If your assigned
direction cannot honestly be built from existing material, SAY SO PLAINLY and shrink it to the
version that can."* It said so. It did not shrink. It kept the full three-window ambition behind a
gate whose prior of returning "no" is high, and it never noticed that its own evidence base
contains a strictly better version of the same paper.

## Scores

| Axis | Score | One-line |
|---|---:|---|
| Novelty | **5/10** | Real gap (on-device MTP energy is unexamined), but 2 of 4 contributions restate already-frozen repo contracts. |
| Feasibility | **2/10** | The runtime does not exist in supported form; the named artifact is wrong; the fix is "fork and self-instrument mlx-lm." |
| MVP leverage | **4/10** | Reuses method prose, cannot reuse a single number — and the floor machinery does no work at this effect size. |
| Venue fit | **5/10** | ICPE-credible *if* it lands; conditional on a gate it probably fails. |
| Original goals | **8/10** | MTP is a named original mechanism goal and this squarely serves it. Best axis by far. |

---

## (a) Does an MTP-capable model + runtime exist on the MLX stack today? — **No, and the proposal names the wrong artifact.**

This is the fatal axis, and the repo answers it unambiguously.

`docs/specs/axi/sc_spec_decode_verdict.md` closed native MTP as
`unsupported_for_joulewise(native_mtp_generation)` on 2026-07-17 with lead-run Metal evidence
(SHA-256 `f7ab8800…`). The mechanism is exact and cited to source: `mlx_lm/models/qwen3_5.py:307-314`
**detects MTP weights and then deletes every key containing `mtp.`**. The package exports no native-MTP
entry point; `stream_generate`'s only accelerated branch is an external `draft_model`.

Three specific failures follow.

**1. The proposal names a model that is neither on disk nor established to exist.** It nominates
"Qwen3.5-27B" as a "plausible candidate but uncertain and not frozen." The repo's actual on-disk
MTP-candidate artifact is **`mlx-community/Qwen3.5-122B-A10B-4bit`, ~65 GiB, vocab 248,320, config
advertising one MTP hidden layer** (same verdict doc, "Historical pre-live artifact snapshot").
A proposal that has read AXI-SC — and it cites AXI-SC — should be able to name the artifact AXI-SC
already probed. Getting this wrong is not cosmetic: 27B-dense and 122B-A10B-MoE differ in every
budget-bearing dimension in the plan.

**2. The reopening gate is violated by the proposed remedy.** AXI-SC's revisit condition is explicit:
*"Revisit native MTP only when a **newly pinned runtime** retains MTP weights, executes an identifiable
native path, **and supplies** the same AXI-SA counters and step boundaries."* The proposal offers an
unmerged community fork (upstream issue open, by its own admission) and then proposes to **add the
counters itself** ("add runtime-observed head provenance and per-round counters"). That is the
measurer writing the measurement into the artifact under test. The AXI-SC controller's entire design
premise is independence — *"The controller suppresses the child's verdict and re-derives the result"*;
*"Proposal/acceptance observability must be real runtime evidence and is never inferred."* Self-supplied
counters may still be admissible, but that is a **custody and contract question requiring a cold-gate
ruling and a successor verdict**, not an engineering line-item. The proposal budgets it as the latter.

**3. Undisclosed dependencies that are themselves open research.** Nowhere does the plan account for:
(i) whether **MTP heads survive 4-bit quantization** with usable acceptance — nobody has shown this, and
a 4-bit MTP head with 40% acceptance produces a different paper; (ii) that a **65 GiB MoE** is a new
model family, new architecture, new tokenizer, and — critically — a **new power envelope**. The
attribution-limited finding (~1 J per phase member) is derived from ~30 ms edge uncertainty × **~33 W
swings**, and the ~5 J practical bar descends from it. Move to a 122B MoE whose decode is dominated by
expert-weight streaming and that 33 W figure, the ~1 J bound, and the 5 J bar all require
re-characterization before a single floor can be minted. **The proposal treats the instrument's
acceptance basis as portable across a 16× change in resident working set. It is not.** This is the
single largest omission in the document.

Net: this is not "one desk gate." It is *new artifact acquisition + quantization validation + a runtime
fork + self-instrumentation + a new stack-identity contract + re-characterization of the attribution
bound + new pinsets/extraction specs + a pilot window*. That is a runtime-and-instrument program, which
is precisely what the hard constraint forbids.

## (b) Is "per accepted token" well-posed? — **Yes, and the proposal handles it correctly — but it is not a contribution.**

Contribution 3 is right on the merits: gross request energy primary, J/committed-output-token as
companion, J/accepted-MTP-token as a spec-on diagnostic only because it is undefined for MTP-off.
It is also **already ratified doctrine**, verbatim, in two places:

- `docs/contracts/token_normalization.md:50-56` — "Committed output tokens and accepted draft/MTP
  tokens are distinct denominators… gross joules per accepted draft token is a speculation-enabled
  [diagnostic]… D-037 claims-ladder rider."
- `docs/research_question_bank.md` C5-2.5c — "accepted-draft J/token stays a mechanism diagnostic,
  never the on/off efficiency denominator (token_normalization.md D-037 rider)."

Contribution 4 (`emitted = accepted + target-origin`, observed not configured) is likewise a restatement
of the frozen AXI-SA contract (`tokens_proposed` / `tokens_accepted` / `acceptance_rate` +
one request-scoped `decode_emission` per step). **Two of four falsifiable contributions are compliance,
not findings.** Halve the novelty score accordingly.

One thing the proposal *misses* on this axis: the 122B artifact's tokenizer (vocab 248,320) is not the
Qwen2.5 tokenizer (151,936). Under the token-normalization contract every per-token number here is
tokenizer-scoped to a stack that shares nothing with the MVP. Within-arm off/on comparison is clean;
**cross-reference to any MVP or D-117 number is forbidden**. The study is hermetically sealed from the
paper it claims to extend. The proposal says "do not transport the Qwen2.5 floors" but does not follow
that through to "therefore this chapter shares no numbers with the rest of the paper."

## (c) Effect sizes vs the ~5 J bar and the two gates — **the strongest section, but it contains a hard error and a self-defeating implication.**

Effect size is genuinely **not** the risk. At 1024-token decode on a model ≥ the 7B anchor, gross decode
energy is hundreds to thousands of joules and a 20–40% mechanism effect is 10–50× any floor. Correct
conclusion, sloppy arithmetic (the 192 J anchor is a **7B, 128-prompt/512-output** member mean from
`window_7bfloor_20260729`, D-110 RT-5-untainted; applying a fork's speedup ratio measured on other
hardware to a different model at 2× the decode length is theater, even for sizing).

**Hard error — the kill threshold is set below the instrument's own comparative floor.** The proposal
kills on *"a bench pilot projects |ΔE| < 10 J."* The measured 7B **comparative** floor from that same
window is **13.998036715259254 J** (absolute 6.294380135190098 J). A 10 J threshold would greenlight a
three-night campaign that structurally cannot clear gate 1. Referee-fatal as written; trivially fixable.

**Undisclosed design problem — duration asymmetry.** MTP-on and MTP-off differ in wall time **by the
effect itself** (~30–40%). Every existing floor design has near-equal arms: D-117's gamma arms are
90.5 s (1.5B ref) vs ~97 s (7B) — ~7% — and the comparative floors are built from *identical-label*
ABBA null blocks where drift loads both halves equally. A 30–40% asymmetric contrast means the two arms
sample different amounts of the **measured never-zero drift** trajectory and different thermal states.
Attribution error is duration-independent; drift is not. **The proposal's contrast imports an asymmetry
the floor machinery has never had to handle and does not say how the drift allowance is apportioned.**

**Self-defeating implication.** If the effect is 10–50× the floor, JouleWise's *entire published
contribution* — attribution-aware detection floors — does no work in this study. An ICPE referee will
ask why the apparatus is needed to see a 60 J effect. The MVP's method sections become ceremonial
reuse. The proposal's defence ("a refusal is still a result") only holds if refusal is plausible,
and its own sizing says it is not.

**Budget is asserted, not derived.** The D-117 memo derives windows from anchor member times
(7B decode member ≈ 97 s) → alpha 3.14 h, beta 3.24 h, gamma 2.80 h against a 2–4 h envelope, beta
already near the ceiling. The proposal doubles decode length (512 → 1024) and multiplies the resident
working set ~16× (≈4 GiB → 65 GiB), then asserts "2.8–4 h windows" **with no anchor member time in
existence**. Its own kill criterion ("cannot fit within four hours including 20% margin") is likely
triggered by its own design. The budget and the design contradict each other.

## (d) Novelty — **thin, and dominated within the portfolio.**

On-device native-MTP energy is genuinely unmeasured — credit where due. But MTP is *self-speculative
decoding*, a special case of a question the repo has already scoped, and `docs/run_reports/2026-07-30-sweep-mechanisms.md`
— which this proposal **does not cite** — already adjudicated it:

> `| — | MTP | — | — | **unreachable** (no runtime) |`
> `| MTP | MiMo-7B-Base (heads in checkpoint) | — | — | **Not reachable**: no MLX MTP support (vLLM only) |`

…while ranking **spec decode on/off (7B + 0.5B) at 6–16× floor clearance** as recommended first
campaign #1: *"cleanest single-mechanism ABBA in existence (identical target weights, flag-toggled),
verified runtime, open sign question."* The proposal's Contribution 1 — a floor-gated on/off energy
verdict at matched output — is **achievable today** for external-draft spec decode and **not at all**
for MTP. Same science, same estimand, on models already floor-characterized. That is domination, and
the proposal reached past it for an external arXiv cite (`2602.09113`, unverifiable here, absent from
the repo's own source list) to make a point the repo already banked with a native citation
(mlx-lm #250: the spec-decode step may be *slower*).

Citation hygiene: `1.41–1.52×` and `~80% acceptance` are load-bearing for a three-night spend and are
**un-custodied third-party claims from an open issue on other hardware**. Under this project's own
evidence discipline they should be labelled as such in the proposal body, not cited as sizing input.

## (e) True cost — **understated by a factor of several.**

Stated: 2–3 weeks desk + 3 windows (8.5–12 h). Realistic floor, assuming everything works:
artifact acquisition/conversion + 4-bit MTP-head validation; fork adoption; runtime instrumentation to
AXI-SA shape; 100-prompt exact-output validation; **cold-gate ruling on measurer-authored counters**;
new stack-identity contract; **re-characterization of the attribution bound and the 5 J bar at the new
power envelope** (itself a measurement campaign, uncounted); pinset v2 analogues; extraction specs;
an uncounted pilot night; then 3 windows that its own parameters suggest exceed the 4 h envelope.
Call it 4–8 weeks desk and 4–5 nights, with a high probability of terminating at "no" somewhere in the
first third. Under Ed's stated priority stack (P1 MVP paper, P2 ICPE, **P3 sacrificed if it costs
P1/P2**), this is textbook P3 spend on the critical path.

## (f) Original-goals service — **genuine, and the proposal's best claim.**

MTP is a named original mechanism axis, and this is a faithful, well-shaped attempt at it: energy as a
third axis beside output-equivalence and latency, single-request boundary preserved, modular harness
exercised. If Ed's question is *"does anything in the portfolio serve the original MTP goal?"*, the
honest answer is: **only via a dated negative result**, and AXI-SC already produced that. A
well-written "this mechanism is currently unreachable on this stack, here is the source-level
evidence" section is real, publishable, advisor-legible material — it just is not a paper.

---

## Fatal flaws (ranked)

1. **No supported runtime, and the remedy is a runtime project.** AXI-SC's reopening gate requires a
   *newly pinned runtime* that *supplies* the counters. The proposal offers an unmerged fork plus
   self-written counters — violating the gate and the existing-material constraint simultaneously.
2. **The instrument's acceptance basis is treated as portable and is not.** The ~1 J attribution bound
   and the ~5 J bar derive from ~33 W swings on the current stack; a 65 GiB MoE requires them re-derived
   before any floor mints. Not mentioned, not budgeted.
3. **Wrong artifact named.** "Qwen3.5-27B" (speculative) instead of the repo's probed
   `Qwen3.5-122B-A10B-4bit` — and every budget/scale/tokenizer consequence flows from that error.
4. **Kill threshold (10 J) sits below the measured 7B comparative floor (13.998 J).**
5. **Strictly dominated by external-draft spec decode**, which the repo's own 07-30 sweep ranks #1 and
   which is reachable on the current pin with already-characterized models. Not cited, not considered.
6. **Budget asserted without an anchor member time**, in contradiction with its own 4 h kill criterion.
7. **Unaddressed drift asymmetry** between arms whose durations differ by the effect under test.

## Three strengthening moves (if kept)

1. **Re-target to external-draft speculative decoding on Qwen2.5-7B + 0.5B; demote MTP to one dated
   paragraph.** AXI-SC established that this exact pair **executes live** (evidence SHA
   `559731f4…`), with distinct loaded paths, matching terminal token IDs, and **directly observed
   accepted tokens via `GenerationResponse.from_draft`**. The `event_observability` verdict blocks only
   `tokens_proposed`, aggregate acceptance rate, and per-step emission bursts — i.e. the *mechanism-yield*
   claims. It does **not** block the paper's actual estimand: gross request energy and
   J/committed-output-token, on/off, at matched output (greedy speculation is output-identical by
   construction — a *stronger* version of Contribution 2 than MTP can offer). Result: zero runtime
   engineering, target model already floor-characterized, floors already minted, tokenizer identical
   to the MVP so numbers *do* cross-reference, and the missing proposal counters become an honest
   declared limitation — which is itself on-brand for this project. Keep MTP as the dated
   unreachable-mechanism section; that costs one rerun of `scripts/axi_sc_spec_decode_spike.py`.
2. **Fix the sizing block and add the asymmetry analysis.** Replace the 10 J kill threshold with the
   measured comparative floor (13.998 J) plus stated margin. Re-derive effect estimates from the repo's
   own anchors (7B 0.376 J/tok, 1.5B 0.098 J/tok) at the actual pre-registered decode length rather
   than from a 512-token member mean on a different model. Add a pre-registered rule for apportioning
   the never-zero drift allowance when contrast arms differ in wall time by the effect itself — and
   state plainly that at 10–50× floor clearance the floor machinery is *method provenance*, not the
   detection mechanism, so the paper's claim to extend the MVP rests on protocol reuse rather than
   floor-limited inference.
3. **If MTP is kept at all, make the desk gate terminate in a written AXI-SC successor verdict, not a
   paper.** Name `Qwen3.5-122B-A10B-4bit` explicitly; add the three missing gate items the proposal
   omits — (a) do the MTP heads survive 4-bit conversion with usable acceptance at all, (b) a
   re-characterization of the attribution bound and the sizing bar at the 65 GiB MoE power envelope
   *before* any floor plan is frozen, (c) a cold-gate ruling on whether measurer-authored counters
   inside the runtime under test satisfy AXI-SA's "real runtime evidence, never inferred" rule. Any
   one of the three returning "no" closes the axis at desk cost, which is the only defensible way to
   spend anything here.
