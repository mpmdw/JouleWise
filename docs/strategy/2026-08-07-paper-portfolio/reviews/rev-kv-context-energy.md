# Counter-review: "The Cost of Remembering: Floor-Gated Context Scaling of Decode Energy on Apple Silicon"

Reviewer: Opus 5 counter-reviewer (adversarial charge: try to kill it).
Ground truth: desk checkout at `89f28bf`; D-117 (end of `docs/decision_log.md`);
`docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`;
`docs/paper/draft-v1.md`; `CLAIMS_STATUS.md`; `docs/research_question_registry.md`
(rows `RQ-KV-GROWTH`, `C5-1.2`, `C5-2.11`).

**VERDICT: WEAK** (borderline KILL as designed; rebuildable to VIABLE).

This is the more careful of the two proposals — its window arithmetic is honest, its
single-request compliance is clean, and it is the only one in the pair that serves an
original Ed axis. It nevertheless fails on two independent grounds, either of which is
sufficient: (a) an untreated confound that is perfectly aligned with the hypothesised
direction, and (b) an effect that is a ~12–25% perturbation on a large baseline,
measured against floors that the project's own minted diagnostics suggest scale with
that baseline. It also spends two nights collecting data that is unclaimable unless a
transport rule it does not yet have is ratified.

---

## 1. Fatal flaw A — prefill thermal carryover is confounded *in the hypothesised direction*

The proposal names three things it must separate ("position vs cache-size vs
attention cost") only implicitly, and treats none of them. Let me do the arithmetic,
because it reorders the whole problem.

**Position (RoPE) is negligible.** No meaningful energy.

**Attention FLOPs are negligible.** For 7B at 8192 context, per decode step:
attention ≈ 2 × 8192 × 512 (KV dim) × 2 (K and V) × 28 layers ≈ 4.7e8 FLOPs, against
weight FLOPs ≈ 2 × 7e9 = 1.4e10. That is **~3%**. Attention *compute* is not a
candidate cause.

**Memory traffic is the only real hypothesis.** The proposal's KV arithmetic checks
out: 1.5B = 28 layers × 2 KV heads × 128 dim × 2 (K,V) × 2 B = 28 KiB/token; 7B = 4 KV
heads → 56 KiB/token; at 8192 tokens, 224 MiB and 448 MiB resident. Per decode step
this adds ~25% (1.5B: 0.224 GiB vs ~0.9 GB weights) and ~11.5% (7B: 0.448 GiB vs
~3.9 GB weights) to streamed bytes.

**But the rival cause is untreated and is the size of the effect.** In the B arm, the
decode phase is preceded *within the same request* by an 8192-token prefill. For 7B
that is ~1.15e14 FLOPs — on the order of 15–30 s of sustained high-power GPU work
(my estimate, flag as uncertain) at a materially higher package power than decode.
In the A arm, the 128-token prefill is sub-second. **Decode in the B arm therefore
begins on a hotter die, at a different DVFS/residency operating point, every single
time.** Hotter silicon leaks more; the direction is *the same* as the hypothesised KV
effect.

This confound is immune to every control the proposal lists:

- **ABBA counterbalancing** cancels linear *time trends across members*. This is a
  deterministic *within-member* carryover, locked to condition, not to order. ABBA
  cannot touch it.
- **NEG8 bound corpus, start/mid/end references, drift allowance** all characterise
  *whole-window* drift. This is a per-member state difference.
- **Fresh pre/post calibration** bounds edge placement, not thermal state.

Contribution 4 — "a quantitative link between analytical resident-KV size and
observed decode energy" — is exactly the claim this guts, because *prefill thermal
load is also monotone in prompt length*. A good fit to KV bytes is, in this design,
an equally good fit to prefill thermal work. The two candidate causes are perfectly
collinear across every cell. The paper cannot distinguish "remembering costs energy"
from "the machine that just did a big prefill decodes hotter."

The proposal does honourably refuse module attribution ("it must not be renamed an
'attention energy fraction'"), which is the registry's stated forbidden upgrade for
`RQ-KV-GROWTH`. But this is not module attribution — it is a rival cause for the
*entire* whole-phase effect.

**A second, lesser rival cause:** decode at 8192 context is *slower per token*, so the
decode phase is longer. A model with constant mean decode power and longer duration
predicts the same energy slope with no KV-specific energy at all. The proposal lists
mean decode power as a secondary metric but never states the discriminating
prediction, so the result will be uninterpretable either way.

## 2. Fatal flaw B — the base windows carry no floor for the family they measure

Each proposed window is: 10 ABBA blocks of 128-vs-8192 (40 members) + 5 absolute
members each at 1024 and 4096 (10 members). That is **zero A=A null blocks and zero
absolute members in the 8192-context condition family** — no comparative floor
component, no absolute floor component, for the family in which the entire claim
lives.

The plan is to transport D-117's comparative null floor from the 128-prompt decode
family to "the otherwise identical long-context decode family." It is not otherwise
identical. Draft §4 defines a condition family as "the same telemetry backend,
metric, window type, **workload profile**, and stack identity"; the DESIGN-MEMO's
claim-eligibility list binds "exact **workload parameters**, model/tokenizer
revision, seeds, quantization, runtime, sampling, and telemetry mode." Prompt length
is a workload parameter. And the memo already ruled the exactly analogous case:

> "The floor riders here use the prefill phase of the 128-prompt decode workload.
> They **do not automatically transport to a prospectively defined 256-token
> contrast.** The fourth plan needs either exact matching prefill floor cells or a
> separately predeclared and justified transport rule."

If 128 → 256 does not transport automatically, 128 → 8192 does not.

The proposal *does* list this as a pre-quiet-time kill criterion, which I credit —
that is more honest than its sibling. But it then budgets the remedy as "a sixth
night… contingency," and the arithmetic is wrong: a long-context decode floor family
is 10 absolute + 40 null = **50 members ≈ one full window, per model**. The
contingency is nights **six and seven**, not six. Realistic headline cost is 7, not 5.

Worse, the ordering is inverted relative to risk. The two base windows are worthless
without a rule the project has not written. The ratification is *desk work and free*;
the nights are the scarce resource. Nothing should be armed until the transport rule
exists in ratified form — or, better, until the windows no longer need one (§ moves).

## 3. Effect sizes vs the bar — the interior points are dead and both endpoints are coin flips

The proposal's expectation table is asserted, not derived. Deriving it from the
project's own anchors changes the conclusion, including the *ordering*.

Anchors: historical diagnostics imply ~51 J for 1.5B decode and ~192 J for 7B decode
at the D-117 shape (memo/proposal, both non-claim). If decode energy tracks streamed
bytes plus duration, the 8192−128 effect is roughly the traffic ratio:

| Stack | KV/weights at 8192 | Decode anchor | Traffic-ratio Δ estimate |
|---|---:|---:|---:|
| 1.5B | ~25% | ~51 J | **~13 J** |
| 7B | ~11.5% | ~192 J | **~22 J** |

(Both uncertain; an independent LPDDR5-class pJ/byte estimate gives ~1–5 J and
~2–10 J respectively, i.e. 2–3× lower, so treat 13/22 J as an upper band.)

Now the floors. The project's minted diagnostics are 1.5B absolute/comparative
3.823787 / 3.592138 J at a ~51 J decode (~7%) and 7B 6.294380 / 13.998036 J at a
~192 J decode (~3–7%). **Two stacks, 4× apart in magnitude, land in the same ratio
band — the floors look roughly proportional to phase magnitude, not fixed at ~5 J.**
The proposal itself flags this ("the nominal 5 J planning bar may not govern that
stack"), then does not follow it through.

Following it through:

| Contrast | Δ estimate | Plausible operative floor | Effect/floor |
|---|---:|---:|---:|
| 1.5B 8192−128 | ~13 J | ~4–5 J | **~2.9×** |
| 7B 8192−128 | ~22 J | ~14 J | **~1.6×** |
| either 4096−128 | ~6–11 J | ~4–14 J | **~0.8–1.5×** |
| either 1024−128 | ~1–3 J | ~4–14 J | **< 1** |

Three consequences, all bad for the proposal as written:

1. **The interior points (1024, 4096) are near-certain refusals.** The proposal
   concedes 1024 ("probably unresolved") but still spends 10 members per window on
   1024 and 4096 absolutes. Those 10 members buy nothing claim-bearing.
2. **Contributions 2 and 4 collapse in the modal outcome.** If only 128 and 8192
   resolve, you have a **two-point "curve."** You cannot fit "a pre-registered
   monotonic or piecewise context model" (Contribution 2) or establish "a
   quantitative link between analytical resident-KV size and observed decode energy"
   (Contribution 4) to two points. The modal paper is one resolved contrast plus
   three refusals.
3. **The proposal's stack ordering is inverted for funding purposes.** Its table
   shows 7B effects ~2× the 1.5B effects and implies 7B is the better bet. In
   *absolute* joules that is right, but under proportional floors what matters is the
   ratio — and 1.5B wins (2.9× vs 1.6×) because GQA gives it proportionally more KV
   per weight byte. **The 1.5B window is the one to fund first, not both.**

## 4. Does varying resident context stay inside the frozen single-request boundary?

**Yes.** I tried to break this and could not. Each member is one sequential request,
batch/concurrency one, no continuous batching, no cross-request cache reuse, no cache
eviction or quantization, no server. Prompt length is a workload-axis parameter, and
the harness is explicitly modular by axis. The new harness work (record initial KV
tokens, predicted/observed KV bytes, cache class and precision, MLX memory counters)
is metadata capture only — no measured-path change. The 512-token fixed output with a
fixed EOS policy is already the D-117 shape and the repo already distinguishes
requested vs runtime-observed emitted tokens.

Memory is a non-issue: 448 MiB KV + ~3.9 GB weights on a 128 GB machine. No swap, no
wired-memory pressure, no allocation confound.

This is the proposal's cleanest section, and it is a real advantage over
batching/serving directions in the same portfolio.

## 5. Per-length window cost arithmetic — the one piece that checks out

Reconstructing from the DESIGN-MEMO's alpha/beta columns: fixed operational overhead
is 8 (pre-cal) + 22 (12 NEG8) + 1 (bound eval) + 8 (start refs) + 5 (midpoint) + 8
(end refs) + 8 (post-cal) + 10 (untouched idle) = **70 min/window** before science.
Science runs ~1.7–2.0 min/member. The 4 h ceiling with the mandatory 20% margin caps
base occupancy at 200 min → ~130 min of science → **≈ 65–75 members per window**.

The proposal's 50 science members therefore fit, and its 3.4–3.8 h estimate is about
right: 20 of the 40 ABBA members carry an 8192-token prefill (+~25 s each for 7B, my
estimate) ≈ +8–10 min raw, so beta's 3.24 h → ~3.45 h; 1.5B lower. This is the only
budget in the pair I did not have to correct, and it leaves ~15–25 member-slots of
genuine headroom per window — which is exactly the resource that should be spent
fixing §2 (see moves).

**Lengths can share a window.** Nothing in the manifest contract forbids multiple
condition families in one window — D-117 alpha itself mints four cells from 50
bundles. The binding constraints are (i) the ~70-member occupancy ceiling and (ii)
the fact that different lengths mean different *members* (unlike alpha's four cells,
which ride the same 50 bundles at zero marginal runtime). So each new length costs
members linearly, and each new *window* costs 70 min of pure overhead. That
arithmetic argues for packing lengths — but only lengths that will actually resolve.

## 6. Novelty

Weak, and the proposal supplies the refutation itself: it cites Fernandez et al.
(ACL 2025) as showing "decode energy begins scaling with input length at sufficiently
large contexts" on an A6000. The headline finding is already published; what is new
is the hardware and the floor/refusal discipline. `draft-v1.md` §8 also notes
TokenPowerBench already "groups results by context length."

There is a genuinely novel angle here, but the proposal does not lead with it: a
*calibrated refusal boundary* for context effects — "on this stack, context effects
below ~X tokens of growth are not resolvable, and here is the instrument-grounded
reason" — is rare and is what Rivoire's bar rewards. Reframing around the refusal
rather than the curve would raise novelty and would also survive the modal outcome of
§3.

## 7. Existing-material and registry compliance

- **Registry rows exist and cap this work.** `RQ-KV-GROWTH` (banked, "L1/L2 chunked",
  forbidden: "no per-token joule claims; no attention-vs-FFN fraction from context
  slopes") and `C5-1.2` "Context-length energy scaling" (candidate, "L2/L3 if
  modeled", forbidden: "no short-prompt phase point claims"). The proposal respects
  the attention-fraction prohibition explicitly — credit.
- **Compliance gap 1:** `RQ-KV-GROWTH`'s registry note says the candidate riders
  "**stay attached rather than becoming independent rows**." This proposal promotes a
  banked rider into a standalone two-window campaign and a standalone paper. That is a
  registry promotion and needs one; the proposal never mentions it.
- **Compliance gap 2:** Contribution 2's "decode J/output-token" brushes
  `RQ-KV-GROWTH`'s "no per-token joule claims." The proposal's guard ("phase
  aggregates — not energy assigned to individual tokens") plus draft §1's
  tokenizer-scoped-companion-metric framing probably clears it, but it should be
  stated in the registry's own words, not paraphrased.
- **Compliance gap 3 — Contribution 1 is not this paper's.** "A claim-bearing
  calibration and floor characterization for two Qwen2.5 model sizes" is D-117's
  alpha/beta output, already funded and already the MVP's C-v material. Double-counted.
- **Cost omission shared with the sibling proposal.** "Five planned quiet nights"
  assumes the MVP closes in three. It does not: `draft-v1.md` §6 has **all six C-iv
  characterization rows marked `[PENDING WINDOW C]`**, and D-117 cl.4 schedules
  MET-WINDOW-C-01 *after* the three windows. The MVP is 3 nights **plus Window C**.
- **Correctly compliant otherwise:** owned hardware only; wall meter correctly
  declared a non-dependency with the right reason (a wall meter validates totals, not
  the prefill/decode split — draft §8); §§3–5 reuse is accurately scoped.

## 8. The lever the proposal leaves on the table

The project brief states the design principle explicitly: "workload LENGTH is the
free lever since attribution error is ~duration-independent." The proposal applies
this to *context* length and fixes decode at 512 tokens to match D-117.

That is the wrong lever. The KV effect scales with **decode steps × resident KV**.
Raising decode length multiplies the effect *and* the baseline, but it is far cheaper
in window time than raising context: 1.5B decode of 512 tokens is only ~5–10 s of a
~92.7 s member (most of a member is idle, warmup, teardown, cooldown). Going to 2048
decode tokens roughly quadruples the KV-read effect — 1.5B ~13 J → ~50 J — for
roughly +20 s/member (my estimate; ~+25 min across 40 members for 1.5B, ~+40 min for
7B, which is why it needs rehearsal). Against a floor that grows with magnitude this
does not buy a 4× ratio improvement, but it moves both endpoints out of the coin-flip
band, and it is the cheapest joules-per-minute available anywhere in this design.

This is the single largest missed opportunity in the proposal, and it is the
project's own stated doctrine.

---

## Scores

| Axis | Score | One-line justification |
|---|---:|---|
| Novelty | **3** | Finding already published (proposal cites Fernandez et al. ACL 2025); novelty is hardware + refusal discipline; registry says this should be a rider, not a row. |
| Feasibility | **3** | Effect is a 12–25% perturbation on a large baseline against apparently magnitude-proportional floors; interior points near-certain refusals; base windows carry no floor for their own condition family; untreated thermal confound. |
| MVP leverage | **5** | §§3–5 reuse is accurate and clean, but Contribution 1 is D-117's, and the 5-night total ignores Window C. |
| Venue fit | **5** | Honest ladder (capstone / EuroMLSys / HotCarbon / ICPE-ERT), correctly excludes ICPE-full without wall or second-unit; but modal outcome is a one-result-plus-three-refusals paper. |
| Original goals | **7** | Best in the pair. Directly serves the KV/attention axis and builds the unmodified full-KV baseline that quantized-KV (C5-2.11) and KDA work require. |

## Three strengthening moves

1. **Make each window self-flooring, and pay for it by deleting the interior points.**
   Replace the 10 absolute members at 1024/4096 (which the proposal already expects to
   be unresolved) with **5 A=A null blocks at 8192 context (20 members)**. New window:
   40 contrast + 20 null = 60 science members, inside the ~65–75 ceiling, ~3.6–3.9 h —
   rehearse before freezing. This gives the long-context family its own *comparative*
   floor, which is the binding component (7B historically 14.0 comparative vs 6.29
   absolute), and transports only the non-binding absolute component. It removes the
   entire transport dependency, deletes the contingency nights six and seven, and
   turns two unclaimable-by-default nights into two claim-bearing ones. Cost: you lose
   the "curve," which §3 says you were going to lose anyway.
2. **Add a thermal-matched control arm, or the causal claim is not defensible.** Run
   ABBA blocks of *128-context decode preceded by an out-of-window GPU preload*
   matched in duration and energy to the 8192 prefill, versus ordinary cold-start
   128-context decode. The preload sits *outside* the measured request, so the
   single-request boundary and the phase markers are untouched. If that hot-vs-cold
   128-context contrast is itself resolvable, the KV claim as framed is dead and you
   have found something more interesting (a measurable prefill→decode thermal
   carryover, which is a real metrology contribution and directly relevant to every
   phase-resolved energy paper). If it is below floor, the confound is bounded and
   Contribution 4 becomes defensible. Either way, pre-register die temperature /
   thermal pressure at decode onset as a recorded covariate, and pre-register mean
   decode power as the discriminator between "KV bytes cost energy" and "decode just
   ran longer."
3. **Fund the 1.5B window first, alone, and raise decode length.** Under
   magnitude-proportional floors the 1.5B arm has the better effect/floor ratio
   (~2.9× vs ~1.6×) despite the smaller absolute effect, because GQA gives it ~25%
   KV-to-weight traffic versus 7B's ~11.5%. Combine with move 2's lever: raise the
   decode target from 512 to 2048 tokens so the effect scales with decode steps. Then
   gate the 7B window on the 1.5B result. Before any of this, spend zero nights and
   do the desk arithmetic the proposal skipped: derive the expected Δ from the
   *freshly minted* D-117 decode floors and the traffic ratio, and check whether the
   fresh 7B comparative floor lands near the old ~14 J. If it does, the 7B arm should
   never be armed.
