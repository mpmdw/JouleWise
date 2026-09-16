# Best use of time and windows for the best papers, fastest — Apple hardware only

**Date:** 2026-09-16. **Author:** Fable writer seat under the magistrate's
dictated structure. **Inputs:** the Fable exploration seat (`RQ-NEXT-*`), the
Astra exploration (`RQ-D-A*`), the literature seat, the
[coverage map](../research_question_coverage-2026-09-04.md) and
[`CLAIMS_STATUS.md`](../../CLAIMS_STATUS.md). Question ids resolve in
[`research_question_bank.md`](../research_question_bank.md).

## Terms

A **window** is one uninterrupted quiet-machine collection session, armed by
the unattended chain. A **floor window** measures a cell's resolution bound —
the largest false energy difference the fixed measurement calculation can
produce for one model, phase and component. A **contrast window** compares two
fixed models. A **refusal** is the chain declining to capture because a gate
failed (load, census, clock); it spends the arm time and no capture time.
**NEEDS-WEB** marks a runtime-support fact no seat verified; it is a
prerequisite to arming, never an assumption. `_v5` is the governed campaign
generation for the pinned Qwen3 1.7B and 8B pair. **ABBA** is the
alternating-order block design (A then B, then B then A) that cancels drift.
**Greedy** decoding always emits the most likely token, so outputs are
identical across repeats. **AP-1** is the pre-registered held-out rule: the
shapes or models reserved for validation are named before any collection.
**PC-n** are the assumed Paper-C facts listed at the head of the bank's Fable
section (for example PC-5, the per-model KV-growth slope).

## Assumptions

- One M3 Max (128 GB), unattended; MLX is the execution leg.
- Cadence 4–5 windows/day, any hour the machine is quiet (D-181). Window
  ≈ 2.5 h: arm-to-t0 10 min, ≈15 min quiet-to-first-capture, so ≈2.25 h of
  capture. A refusal costs ≈20 min.
- Papers: **A** methods (merged); **B** phase-energy capstone (`_v5`); **C**
  mechanism, the Tier 1 bank; **D** post-C scaling and mechanism laws.
- The Fable seat sized its windows at ≈3.5 h of capture (≈80 members at ≤8B,
  ≈40 at the 100B class). Every seat window count below is multiplied by
  3.5/2.25 ≈ 1.6 and rounded up. Astra's convention is kept: every new
  model×phase cell needs its own floor window; 20% of each phase is refusal
  reserve; a sub-floor result prints `not resolvable`, never equivalence.

## Phase 0 (days 1–3): Paper B

The chain as the coverage map and `CLAIMS_STATUS.md` describe it: the stub
rehearsal → the equivalence night → the `_v5` transaction. The stub rehearsal
runs the unattended chain end to end with no capture (`REHEARSAL_ONLY`); it is
repeated here because the installer changed after the 09-12 pass (PR #341). The
equivalence night is twelve timing captures judged by the desk tool against the
calibration envelope in force (`d079_calibration_acceptance_v2_n17_r6`): PASS
continues that acceptance onto the current macOS build by a dated addendum;
FAIL starts the three pre-registered derivation nights with this one counting
first; fewer than six retained captures is INCONCLUSIVE and buys one more
night. Then G2-a (the probe evening that picks the prefill prompt length: the
shortest of 512/1024/2048/4096 at which every one of ≥5 small-model probe
members shows ≥5 overlapping power records), the desk day (rung pin, pack
generation, throwaway-clone re-proof), and G2-b/transaction: alpha (1.7B decode
floor, prefill cells riding), beta (8B decode floor, prefill riding), gamma
(the 1.7B-vs-8B decode contrast), and the D-168 close-out (eight ordinary
dominance ratios, four common-mode values, branch A/B).

**Two diagnostic arms ruled in on the desk day** (literature seat §3), run as
`DIAGNOSTIC_NO_PACK` windows so the frozen pack is untouched:

1. **IOReport "Energy Model" cross-check.** Read the cumulative IOReport
   counters (CPU/GPU/ANE/DRAM, 1 mJ resolution, readable at arbitrary instants
   without sudo — Zeus's Apple interface) at the runtime's own phase edges, in
   the same window as `powermetrics`, and compare each phase's counter delta
   with the `powermetrics` interval integral against that cell's floor. This
   tests whether the ≈1 J attribution scale survives an independent read path
   and time base. **Caveat to print:** both paths are Apple's model of energy,
   so agreement tests read-path and time-base independence, not physics.
   Prerequisite: an IOReport reader at the desk (day 2 morning).
2. **Generation-length-1 prefill isolation.** Requests capped at one output
   token, so the request is prefill plus one decode step; its gross energy is
   compared with the boundary-derived prefill allocation for the same prompt.
   A boundary-free falsifier (Ruf & Detyniecki's design). Prerequisite: none.

| window | question id(s) | held constant | claim it feeds | paper section | prerequisite / NEEDS-WEB |
|---|---|---|---|---|---|
| 0.1 (day 1) | stub rehearsal | chain, installer | none (licenses nothing) | — | PR #341 merged |
| 0.2 (day 1) | equivalence night (12 captures) | pulse workload, r6 envelope | calibration in force on this OS build | B: instrument | quiet census; INCONCLUSIVE → repeat |
| 0.3–0.4 (day 1) | G2-a probe evening | 1.7B/8B, thinking off, greedy | prefill rung pin | B: protocol | PASS addendum landed; PACK-ROOT-SUCCESSOR-V5-01 |
| desk (day 2) | rung pin, pack generation, clone re-proof | — | pre-registration object | B: protocol | — |
| 0.5 (day 2) | IOReport cross-check arm | same requests as G2-a, both readers | read-path independence of ≈1 J | B: limitations / instrument | IOReport reader built |
| 0.6 (day 2) | generation-length-1 arm | prompts at the pinned rung, d=1 | boundary-free prefill check | B: limitations | none |
| 0.7 (day 3) | alpha: 1.7B decode floor (+prefill cells) | pinned prompts, 512 tokens | 1.7B floor | B: results | frozen pack |
| 0.8 (day 3) | beta: 8B decode floor (+prefill cells) | as alpha | 8B floor | B: results | frozen pack |
| 0.9 (day 3) | gamma: 1.7B vs 8B contrast | ABBA blocks, n=10 | `C5-1.1` decision-rule demonstration; `RQ-ATTRIBUTION-DOMINANCE` | B: results | alpha, beta minted |
| desk (day 3) | D-168 close-out | — | dominance sentence licensed or refused | B: results | all cells authenticated |

**What a refusal costs here:** the equivalence night cannot be retried inside
its plan (D-078 no-retry); a refusal or INCONCLUSIVE costs one day. An alpha,
beta or gamma refusal voids that window's members; re-arm at the next quiet
slot (≈20 min + one window). Two refusals push Paper B's data-complete day
from 3 to 4.

**Output:** Paper B data-complete day 3.

## Phase 1 (days 4–10, 30 windows): Paper C

Ordered by what Paper C's predictive model needs first. **Panel:** the `_v5`
pair (floors minted in Phase 0) plus Qwen3-30B-A3B and Qwen3.5-122B-A10B as
the two sparse points Phase 2's laws need; each new model needs its own floor
window first. Per the literature seat: the 1.7B-vs-8B contrast is the
decision-rule demonstration with citations (ML.ENERGY, Watt Counts, Silicon
Showdown, GreenBench), not a headline; quantization non-monotonicity is cited
(Arya & Simmhan; ML.ENERGY FP8), not re-measured — one 8-bit 8B cell supplies
the per-quant coefficient row and nothing more. 24 collection windows + 6
reserve = 30.

| window | question id(s) | held constant | claim it feeds | paper section | prerequisite / NEEDS-WEB |
|---|---|---|---|---|---|
| 1–2 | floors: 30B-A3B, 122B-A10B (decode + prefill cells) | pinned prompts, 512 tokens | cell floors for the two sparse points | C: instrument | 122B smoke feasibility (68.9 GB peak) on record |
| 3–8 | `Q4`/`RQ-SHAPE-ENERGY` shape grid: p∈{512,1K,2K,4K} × d∈{128,512,2048}, 4 models | thinking off, greedy, cold cache | `E = fixed + a·p + b·d` per model | C: coefficient model | held-out shapes reserved before collection (AP-1) |
| 9–10 | `Q4` held-out validation | as grid | coefficient transport within model | C: coefficient model | frozen predictions |
| 11 | `C5-1.12` one 8-bit 8B cell | shape from the grid | per-quant coefficient row (cited, not a headline) | C: coefficient model | 8-bit artifact pinned |
| 12–14 | `RQ-KV-GROWTH` + `C5-1.2`: chunked decode at p 128→8192, 4 models | d fixed, chunk edges pinned | KV-growth slope, nonlinearity onset | C: context | unsupported cells recorded |
| 15–16 | `RQ-ENERGY-VARIANCE`: repeated stochastic sampling at one shape | shape, seeds logged | length vs residual decomposition | C: variance | none |
| 17–19 | `RQ-SESSION-SHAPE` + `RQ-CACHE-PREFIX` | shared prefix 2K/8K, suffix 512 | session overhead term; prefix crossover | C: sessions | prefix-cache identity pinned |
| 20–21 | `RQ-CONTENT-SENTINEL` + `C5-W.1` | fixed token shape, categories rotated | token-shape sufficiency | C: workloads | none |
| 22–24 | `C5-W.3` / `Q5` workload-category grid | natural stop under cap | category ranking by model | C: workloads | none |
| 25–30 | reserve | | | | |

**What a refusal costs here:** ≈20 min plus the slot; the six-window reserve
absorbs six refusals. Each refusal beyond six delays Paper C by one window
(≈0.2 day). The floors (windows 1–2) gate everything on 30B-A3B and 122B: a
refusal there is re-armed before any grid window on those models.

**Output:** Paper C data-complete day 10.

## Phase 2 (days 11–17, 30 windows): Paper D

The Fable seat's week ranking, merged with Astra where the dedupe table names
Astra's design stronger (A01 for residency; A03's identification for
routing×batch; A09 as the MTP record). Counts are seat counts × 1.6.

| window | question id(s) | held constant | claim it feeds | paper section | prerequisite / NEEDS-WEB |
|---|---|---|---|---|---|
| 1–5 | `RQ-NEXT-BYTES-LAW` (+`COEFF-LAW` rides): 8 models, p=256, d=2048, 14B held out | quant recipe, router stats logged | one-covariate bytes law; coefficient law | D: scaling law | floors for 4B/14B/32B/80B-A3B inside these windows; Qwen3-Next-80B-A3B support NEEDS-WEB |
| 6–7 | `RQ-NEXT-FRONTIER-235B` | 3-bit artifact | frontier point on/above the line | D: scaling law | 3-bit conversion NEEDS-WEB; A01 residency rider fits here |
| 8–11 | `RQ-NEXT-PHASE-CROSSOVER`: 4 models × p∈{512…8K} | prefill chunk pinned, d=512 | p\*/d as a roofline constant, held-out model | D: roofline | none |
| 12 | `RQ-NEXT-PREFILL-CHUNK`: chunk∈{256…8192}, 8B/32B | p=8K | chunk-size knob; confound guard for p\* | D: roofline | labelled prefill floor |
| 13–17 | `RQ-NEXT-MIXER-3B`: MLA/GQA/DeltaNet/KDA at ≈3B active, p∈{512,8K,32K} | d=512, byte-matched roster | mixer signature in decode slope | D: mechanism | MLX support for Kimi-Linear and DeepSeek-V2 NEEDS-WEB |
| 18–24 | `RQ-NEXT-MIXER-120B`: GLM-4.5-Air / gpt-oss-120b / Qwen3.5-122B, p∈{2K…128K} | d=512, n=8 | prefill scaling by mixer at the 128 GB class | D: mechanism | GLM-4.5-Air, gpt-oss-120b MLX support NEEDS-WEB; Qwen3.5 hybrid status verify |
| 25–30 | reserve | | | | |
| 31–35 | `RQ-NEXT-SPEC-SURFACE`: 8B/32B/70B targets, 0.6B/1.7B drafters | greedy, d=1024 | break-even acceptance predicted from coefficients | D: dynamic execution | counter-complete speculative path NEEDS-WEB (AXI-SC `unsupported` in July) |
| 36–39 | `RQ-NEXT-BATCH-KNEE`: B∈{1…16}, 8B/30B-A3B | p=d=512 | knee predicted from PC-5 | D: dynamic execution | AXI-SB supported |
| 40–43 | `RQ-D-A03` identification + `RQ-NEXT-ROUTING×BATCH` B=1 null | routing trace precomputed, 32B dense control | expert-union predictor | D: dynamic execution | MLX router hook (desk) |
| 44–48 | `RQ-NEXT-KVQ-SURFACE`: kv_bits∈{16,8,4}, 32B/122B, 2K/16K/64K | d=512 | saving = KV-byte saving × slope − dequant term | D: applied | quantized-cache support per class NEEDS-WEB |
| 49–53 | `RQ-NEXT-EPCA-LEVELS` (MATH levels 1–5; `EPCA-MECHANISM` shares rosters) | fixed shape, natural EOS under cap, 32 items/level | energy per correct answer vs published difficulty | D: applied | AP-5 policy ruling extended to MATH (`RQ-D-A10`); scored leg |

Windows 31–53 do not fit days 11–17; they are Phase 2b (days 18–23) in this
order. Nothing after window 24 is required for Paper D's core (scaling law +
roofline + mechanism).

**What a refusal costs here:** as Phase 1, ≈0.2 day each beyond the reserve.
The 100B-class windows (6–7, 18–24) are the expensive ones: a refusal there
loses a window that holds only ≈25 members.

**Output:** Paper D core data-complete day 17; full set day 23.

## Days to each paper

- Paper A: merged, day 0.
- Paper B: 9 windows + 2 desk blocks over days 1–3 at 4–5 windows/day → day 3.
- Paper C: 24 + 6 reserve = 30 windows ÷ 4.5/day ≈ 6.7 days → day 10.
- Paper D core: 24 + 6 reserve = 30 windows → day 17. Full set: +23 windows
  + 5 reserve = 28 ÷ 4.5 ≈ 6.2 days → day 23.

Writing runs in parallel on desk days; these are data-complete days.

## What would change the order

1. **The equivalence night FAILs.** Three pre-registered derivation nights
   follow (this night counts as the first); Phase 0 grows by two nights and
   everything slides ≥2 days. INCONCLUSIVE slides one day per repeat.
2. **A NEEDS-WEB check fails.** If Kimi-Linear, DeepSeek-V2, GLM-4.5-Air or
   gpt-oss-120b lack an exercised MLX path, the mixer windows shrink to the
   within-family GQA-vs-hybrid pair (Qwen3-30B-A3B vs Qwen3.5-122B) and
   Phase 2b's dynamic-execution group moves into days 11–17.
3. **The IOReport cross-check disagrees with `powermetrics` by more than the
   cell floor.** That is an instrument finding, not a Paper C input: Phase 1
   stops until the read-path question is resolved, and Paper B carries the
   disagreement as a stated limitation.
