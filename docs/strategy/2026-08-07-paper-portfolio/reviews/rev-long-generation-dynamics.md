# Counter-review — `prop-long-generation-dynamics.md`

**Reviewer:** Opus 5 counter-reviewer (independent). Ground truth: `desk` @ main.
**Proposal:** "Does Token 4,000 Cost More Than Token 400? Calibrated Decode-Energy Dynamics on Apple Silicon"

## Verdict: **WEAK**

Not because the physics is below the floor — the assigned worry is answered NO, the
effects are probably resolvable — but because the proposal picks the confounded
observational design when the repo already banks the interventional one, builds its
primary estimand on a floor construction that cannot exist, and misses the single
genuinely novel methodological point sitting in its own material. This needs a
redesign, not a tune-up. The redesigned sibling (below) would be VIABLE-to-STRONG.

| Axis | Score | One-line justification |
|---|---:|---|
| novelty | **4** | "Energy drifts within a request" restates the project's already-published never-zero drift allowance at finer granularity. The one novel idea in the material (interior-bounded estimands escape the attribution limit) is absent from the proposal. |
| feasibility | **6** | Exact-N generation and per-token timestamps genuinely exist. Per-*chunk* energy does not, and the extension lands on a D-117 desk stack (U1–U10) that is not yet built. |
| mvp_leverage | **3** | Reuses §§2–5 but costs 1–2 extra nights + a substantial schema/reducer/floor extension, and closes none of the MVP's open sections. |
| venue_fit | **5** | Capstone chapter, yes. ICPE only if the methodological point becomes the headline — as framed it is a descriptive table with a conceded confound. |
| original_goals | **6** | Really does serve the KV/attention axis (RQ-KV-GROWTH, C5-1.2, C5-2.12) and builds substrate for KDA / quantized-KV. Then explicitly declines the causal version the axis needs. |

---

## First, the assigned question: is anything here resolvable?

**Yes — marginally, and the proposal gets the reason wrong in both directions.**

**Sub-request resolution exists, partially.** Verified in the tree:

- Per-token timestamps are real: `joulewise/bundle_read.py:555` `token_timestamps()`,
  `_is_decode_token_event` (`bundle_read.py:1499`), provenance
  `runtime_per_token_callback` (`reduce.py:3062`, `axi_decode_config.py:520`), and a
  precheck that *refuses* to treat them as eligible on stream-chunk fallback
  (`reduce.py:3650`, `token_count_stream_chunk_fallback`).
- Exact-N EOS-masked generation is real: `adapters/mlx_runtime.py:206` `suppress_eos=True`,
  `:414` `output_policy == "fixed_budget_exact"`, with `eos_suppressed` and
  `original_eos_token_ids` recorded into metadata.
- **Per-chunk energy is NOT real.** `phase_energy_j` is keyed by phase *name*, and
  `bundle_read.py` states the contract explicitly: "Multiple valid intervals with the
  same phase name are integrated separately **and summed by the reducer**." Chunking
  therefore requires either distinct per-chunk phase identities or a new reducer path —
  plus new condition families, new bound corpora, new floor cells, pinset/extraction
  changes. The proposal calls this "decode-chunk schema and reducer support"; that is a
  fair label for a large piece of work stacked on U1–U10, which do not exist yet.

**Per-token is hopeless; per-chunk is fine.** The repo already did this arithmetic:
`docs/research_question_bank.md:51` — "token cadence (~4 ms) far outruns the power
sampler (~113 ms); no per-token joule claims." Confirmed independently:
`SAMPLING_INTERVAL_MS = 100` (`powermetrics_fiducial.py:63`), and the design memo's
timing probe gives 512-token generation at **2.05 s (1.5B)** and **6.40 s (7B)**
(`docs/phase_2/splitwise_decode_campaign.md` §4). So a 512-token chunk is ~18 samples
at 1.5B and ~57 at 7B. Chunked works; per-token is 25× below resolution.

**The magnitude.** The proposal's base numbers reconcile (51 J / 192 J per 512 tokens
matches the repo's measured 0.098 / 0.376 J/tok, `2026-07-30-sweep-mechanisms.md:66`).
Its *effect* sizing does not. Scaling the position effect proportionally to base energy
is the wrong model. The effect is extra KV traffic per token against weight traffic per
token. Using the repo's own `joulewise/kv_size.py` formula (2·L·H_kv·d·dtype):
Qwen2.5-1.5B ≈ **28.7 kB/token** (28 layers, 2 KV heads, d=128, fp16) against ~0.9–1.0 GB
of 4-bit weights; Qwen2.5-7B ≈ **57.3 kB/token** against ~4.2 GB. The *relative* effect
is roughly **2× larger for the 1.5B model**, not smaller. Back-solving ~90–100 pJ/byte
from the repo's own J/token figures, late-1024 minus early-1024 over a 4096-token
generation lands near **≈9 J (1.5B)** and **≈16 J (7B)** — flag: my estimate, ±50%,
depends on Qwen2.5 config values I did not read from disk.

Consequences: the effect is ~2–3× the ~5 J bar, not the 4–19× the proposal implies for
7B; and the arm the proposal offers to kill (1.5B) is the one with the strongest
*relative* signal. Its "kill that model's night if runtime-only sizing projects under
7.5 J" gate would likely kill the wrong arm.

---

## Fatal flaws

**F1 — The primary estimand has no comparative floor, and comparative is the binding term.**
The operative floor is `max(F_abs, F_cmp)` (draft §4), and comparative has historically
bound: mint #1 was absolute 3.592138 J vs comparative **7.377086 J**, operative 7.377086
(D-110). A comparative floor requires A/B/B/A blocks in which A and B are *aliases of the
exact same configuration* (draft §4: "A and B are aliases of the exact same configuration
and payload, so any nonzero block delta is a false comparative effect"). "Early chunk" and
"late chunk" are **positions, not swappable labels** — no alias null can be constructed for
them. The proposal's "the alias blocks supply comparative false-effect evidence" yields a
floor for the *member-level* metric; transporting it to a *within-member* chunk difference
is exactly the transport violation the D-117 design memo forbids ("never borrow a decode
floor for prefill"; "the 128-prompt prefill riders do not automatically transport"). The
same rule binds here. Contribution 2 has no gate it can pass.

**F2 — The estimand is not counterbalanceable, and the confound is never zero by the
project's own measurement.** ABBA cancels a linear time trend *between* members
(draft §5). Within a member, token position and elapsed time are the same variable and
cannot be reordered — no design fixes this. Draft §4: the drift allowance "remains
positive even in an exceptionally stable window." So late-minus-early ≡ KV growth + DVFS +
thermal + within-run drift, inseparably. The proposal is honest about this ("position-
associated drift, not KV growth causes energy") — but that honesty collapses Contribution 2
into *re-measuring the known drift limitation on a finer timescale*. That is a
re-parameterization, not a result.

**F3 — Duplicative of banked work whose discipline it doesn't cite, and it picks the weaker
of two designs that cost the same nights.** `docs/research_question_registry.md:48` banks
**RQ-KV-GROWTH** at "L1/L2 chunked", "no per-token joule claims", with the rider "bounded-
window KV marginal slope". **C5-2.12** (`research_question_bank.md:977`) already specifies
the *interventional* version: bounded evicting `RotatingKVCache` via `max_kv_size` vs
unbounded step-growing `KVCache` — available in the pinned mlx-lm, ABBA-counterbalanceable
at matched positions, with a real alias null and a real comparative floor. The proposal
defers this ("a causal KV-mechanism claim would still require a later bounded-versus-
unbounded cache intervention") while spending the same nights on the confounded version.
That is a design error, not a scoping choice.

## Should-fix

**S4 — The attribution model is inherited uncritically, and in the *pessimistic* direction —
which is why the best idea got missed.** Draft §4 derives ~1 J from "a roughly 30 ms timing
uncertainty meets a power change of roughly **33 W**" — that 33 W is the *prefill→decode
power step*. A decode-to-decode chunk boundary sits inside a homogeneous power regime where
the step is ≈0 W, so the existing corner scan would honestly return a near-zero interval
there. Two consequences: (i) the proposal's own floors are **not** attribution-dominated,
so the "attribution-limited" framing it leans on doesn't apply to its estimand; (ii) if you
drop the phase-adjacent chunks (compare chunk 2 vs chunk 7, both bounded by interior edges)
the estimand becomes the project's **first noise-limited (~0.3 J) rather than attribution-
limited quantity**. That is the most publishable thing available in this direction, and it
is nowhere in the proposal. As written, chunk 1's leading edge is the prefill boundary and
chunk 8's trailing edge is the decode-end step, so the proposal gratuitously imports ~2 J of
worst-case attribution into a ~9 J effect.

**S5 — Budget bookkeeping is understated (though the headline hours survive).** Per the
design memo the member is overwhelmingly fixed overhead (1.5B member 92.7 s of which only
2.05 s is generation; 7B ~97 s / 6.40 s). 4096 tokens adds ~14 s (1.5B) / ~45 s (7B) per
member, so ~2.6 h / ~3.4 h is about right *for a 40-member design* — but only because the
proposal silently leaves the 12-member NEG-8 bound corpus and the 3/1/3 references at the
**short** workload. Draft §4 defines a condition family by "workload profile", so a
512-token bound corpus cannot bound a 4096-token cell. Moving them adds ~10–14 min and puts
the 7B window at ~3.5 h with no headroom against the 4 h cap. Also unbudgeted: cooldown
cap-hits (historically one 305 s cap-hit against a 117 s recovery) under 40 × 51 s sustained
GPU bursts.

**S6 — 4096 tokens is 2× beyond the untested range.** Draft §6 ramps linearity 128→2048 and
every one of the six characterization rows is `[PENDING WINDOW C]`. The proposal asserts the
extrapolation and simultaneously makes the untested range its estimand.

**S7 — No minimum-samples-per-chunk rule.** The 8-chunk secondary trajectory at 1.5B is ~18
samples/chunk. The bank's own convention ("bundles with fewer than N samples report a flag,
not a bare joule value") applies and is never stated.

**S8 — The ABBA structure is decorative for the primary estimand.** All 40 members are the
same config; the position contrast is computed *within* each member. ABBA buys nothing for
the headline number — it only supports the member-level null. Say so, or drop the framing.

## Three strengthening moves

1. **Make it an intervention, not an observation.** Run C5-2.12's bounded (`max_kv_size`)
   vs unbounded `KVCache` contrast at matched token positions in real ABBA blocks. This
   converts an uncounterbalanceable within-request difference into the project's standard
   A/B estimand with a legitimate alias null and a legitimate comparative floor, and it
   answers "does KV growth cost energy" *causally*. Price: eviction changes generations, so
   pre-register a **work-matched, never output-matched** contrast per C5-2.12's own
   forbidden-upgrade wording and report divergence. Output-identity-preserving sibling:
   hold the measured chunk at a fixed position in the request and vary the *starting* KV
   size via prompt length (128 vs ~3200 prefill, then measure the first 512 decode tokens) —
   the repo's KV replay spike already demonstrates prefix-cache save/load with
   `tokens_identical: true` (`docs/stream_logs/2026-07-07-kv-spike-301/`).
2. **Make the interior-boundary result the headline.** Pre-register that chunk floors are
   minted for *interior-bounded chunks only* (drop chunks 1 and 8), demonstrate via the
   existing corner scan that their attribution intervals collapse, and publish: *the
   attribution limit is a phase-boundary property, not a global property of the instrument —
   interior-bounded estimands are repeatability-limited at ~0.3 J.* That extends the MVP's
   central finding instead of merely reusing it, and it costs desk work rather than nights.
3. **Fix the sizing before asking for a night.** Replace proportional-to-base sizing with a
   bandwidth model built from `kv_size.bytes_per_token` and the measured 0.098 / 0.376 J/tok;
   publish the implied pJ/byte; set the kill gate on the *interior-bounded* (chunk 2 vs 7)
   estimand, whose effect I estimate at ~6 J (1.5B) / ~11 J (7B), not the full-span one.
   Then declare the minimum-samples-per-chunk rule, re-spec the NEG-8 bound corpus and the
   3/1/3 references at the long workload, and re-run the 4 h envelope with those members in.

## Sequencing note

The proposal correctly refuses to disturb the three D-117 windows. But it adds 1–2 nights
plus a large desk extension (chunk reducer, new condition families, pinset/extraction
changes) on top of a U1–U10 stack that is not built, while closing neither §6 nor §7 of the
MVP. Under the paper-first stack this is not an MVP candidate. Post-redesign it is a
reasonable ICPE-version chapter.
