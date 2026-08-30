# 02 — Opus 5 seat (general-purpose subagent, model opus, read-only)

Verbatim. Round 1 answers the original brief; round 2 (sent after the addendum reached the seat mid-run) answers the addendum and restates the four questions in revised form.

## Round 1

# Opus 5 seat — workload consult verdict (2026-08-28)

**Recommendation in one paragraph.** Keep the fixed-shape, fixed-budget, greedy-decode workload — but fix the two things that are actually wrong with it, both of which are *content* and *length*, not *shape*. (1) Replace the synthetic filler prompt (`"The plan remains easy to audit."` × 35 + one variant, `generate_configs.py:449-451`) with one pinned, human-readable, license-clean task prompt rendered to an exact token count on the tokenizer-identical `_v5` pair. This costs nothing: the frozen condition-family schema pins `prompt_tokens`/`output_tokens`, **not** prompt text (`joulewise/floor_extraction.py:712-717`), so the prompt bytes are a free variable that the pack already pins separately (`prefill_prompt_candidate.json`, `prompt-text-sha256=` tag). (2) **The 256-token prefill arm is not admissible and must get longer.** I measured this, I did not infer it: in the historical 40-member contrast (`runs_window_contrast_20260730`), **all 20 of the 1.5B members are ineligible for `phase_energy_j.prefill`** — `insufficient_in_window_samples` (2 records against `MIN_PHASE_SAMPLES = 3`, `reduce.py:116`), `cadence_ratio_unrecorded`, and `anchor_energy_envelope_exceeds_quarter_metric` — while all 20 7B members are eligible. Those refusal reasons flow straight into the contrast's reason list (`analysis_engine/__init__.py:819-822`), so an A-arm that cannot clear the precheck yields a *refused* prefill contrast for an avoidable instrument-design reason, not a scientific one. D-122 sized 256 tokens against the ~5 J **energy** bar and never against the **resolvability/precheck** bar. My recommendation for `_v5` is therefore: decode arm unchanged (128-token pinned real prompt, 512-token cap); prefill arm moved from 256 to **2048 prompt tokens (4096 preferred, because 4096 is the only length with *measured* margin)**, with the same move applied to the dedicated prefill floor cells in both floor packs. The added window time is under two minutes on a ~5-hour budget. Options (b), (c) and (d) are all better science and all cost mint-path schema surgery this calendar cannot absorb; (d) has a shovel-ready vehicle (`jw_mixed_v1`) and should be the first post-campaign window, not `_v5`.

---

## Measured facts this verdict rests on

All from the tree; every number is either a file constant or computed by me from run bundles on disk.

| Fact | Value | Source |
|---|---|---|
| Phase-resolvability threshold | `MIN_PHASE_SAMPLES = 3` | `joulewise/reduce.py:116` |
| Overlap predicate | `min(w_end, r_end) > max(w_start, r_start)` | `reduce.py:196-206` |
| Two further phase-precheck gates | `cadence_ratio ≥ 2.0`; `clock_bound ≤ 0.25 × duration`; `anchor_energy_envelope ≤ 0.25 × metric` | `reduce.py:975-991`, member JSON |
| Realized sampler | requested 10 Hz, **observed 8.87 Hz**; median record support width **0.1208 s**; p95 in-window gap 0.113 s | `runs_recal_20260718/...-su-b01-a1`, `runs_window_contrast_20260730/*` |
| 1.5B prefill @128 tok | 0.1376 s → **2 records** (18/20 members), 1.713 J | contrast window, 20 members |
| 7B prefill @128 tok | 0.2794 s → **3–4 records**, 7.523 J, cadence ratio 2.28, envelope ratio 0.13 | same |
| Prefill precheck eligibility, historical contrast | **A arm 0/20 eligible, B arm 20/20 eligible** | computed from `window_evidence_precheck.phase.prefill` |
| 1.5B prefill @512 tok | 0.186–0.220 s → **2–3 records**; bundle prints `prefill: not_resolvable_sample_count` | `runs_recal_20260718` suite bundles |
| 1.5B prefill @4096 tok | **1.123 s → 10–11 records**, 51.07 J | `runs_window_a10_20260725` |
| Decode @512 tok | 1.5B 1.936 s / 18 records / **50.42 J** (SD 0.241); 7B 6.105 s / 54 records / **191.70 J** (SD 0.189); **Δ = 141.3 J** | contrast window, 40 members |
| Prefill Δ @128 tok | **5.810 J** (the D-122 sizing number) | consult trace + my recomputation |
| Member cadence (real) | **median 148.1 s**, 40 members spanned **106.7 min** | `runs_window_contrast_20260730/campaign_log.jsonl` |
| Generation is a rounding error | 1.93 s of 148 s = **1.3%** (small), 6.1 s = **4.1%** (large) | as above |
| Pack budget | decode 168 min + prefill_p256 130 min + refs 12 min = **310 min** | `generate_configs.py:1804-1830` |
| Design constants | `N_BLOCKS = 10`; `GUARD_MINIMUM_N = 5`; `MAX_EXACT_ADMISSIBLE_CORNER_N = 16` | `generate_configs.py:92`, `detection_floor.py:108-110` |
| Condition-family schema | exact keys `{name, prompt_tokens, output_tokens, repetitions, warmup_runs}`, each a **positive integer** | `floor_extraction.py:712-717, 798-810` |
| Floor metric catalog | no per-token metric exists (`gross_energy_j`, `energy_request_j`, `idle_subtracted_energy_j`, `phase_energy_j.*`) | `detection_floor.py:245-252` |
| Determinism gate | config equality **exact** after removing only `run_id`; suite bundles compare per-item `response_sha256` | `determinism_gate.py:1-9`, `REASON_DIFFERENT_CONFIGS` |
| Suite path already works | `jw_mixed_v1` = 48 items, 6 categories × 8, all `512/256 fixed_budget_exact`; suite ABBA already executed (20 bundles, `runs_recal_20260718`), 5-item suite = 65 s wall, prefill phase 25.19 J | `configs/suite_manifests/`, bundles |
| Benchmark import | **no importer exists**; P2-022/P2-023 both `BLOCKED — POST-2M-CORPUS` under D-041 | `TASK_QUEUE.md:613-614`, repo-wide grep |
| Floor-cell estate | each floor pack carries 6 floor cells incl. `...prefill-p256-...-absolute` and `...-abba` | `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json` |

Fit used below (labelled): 1.5B prefill duration ≈ `0.116 + 1.7e-4 · n_prompt` s in the 128–2048 region (from 0.137 s @128 and 0.202 s @512); prefill energy ≈ `0.055 + 0.01245 · n_prompt` J (from 128 and 4096). Guaranteeing 3 overlapping records needs duration > 2 × 0.1208 = **0.242 s**; 4 records needs **0.363 s**.

---

## 1. What each option does to the six axes

**(a) Fixed-length synthetic, as-is (128/512 decode; 256/512 prefill).**
Determinism: perfect — greedy, `fixed_budget_exact`, identical config bytes; the gate's `different_configs` refusal never fires. Pairing: intact, 10 ABBA blocks × 4 members × 2 arms = 80. Floor arithmetic: decode is luxurious (Δ 141.3 J against a ~1 J boundary scale and a ~5 J effective bar); prefill projects Δ ≈ 11.6 J. **Resolvability: FAILS.** At 256 tokens the small model's prefill is ≈ 0.16 s → 2 records; the measured 128- and 512-token points bracket it and both give 2–3. Night: 310 min budgeted, ~197 min of member time measured. Honest sentence: *"For token generation, 7B minus 1.5B was Δ J, above the cell's resolution bound; for prompt processing the contrast was refused for `insufficient_in_window_samples` on the A arm."* That is a refusal the reader will read as a design error, because it is one.

**(b) Pinned real benchmark items (GSM8K/MMLU/HumanEval/MT-Bench), cap on `max_new_tokens`.**
Determinism: fine *if* each cell runs one fixed item (config equality) or one fixed suite manifest (per-item hashes). Pairing: unchanged if item count is fixed. Floor: unchanged in magnitude; but if distinct items appear *within* a cell, real item-to-item variation enters the absolute component and **inflates the floor**, which is the one thing the design must not do. Resolvability: depends entirely on the prompt length the items happen to have — an MMLU stem is ~100 tokens and would fail exactly as p256 does. Night: unchanged. Blocking cost: **no importer, and both queue rows are D-041-blocked**; license/contamination/subset fields exist in `suite_manifest.v1` but nothing populates them. Sentence: strong (*"on a frozen 20-item GSM8K subset…"*) and unavailable before 09-01.

**(c) Same prompts, natural stopping.**
Determinism: *not* broken across repeats (greedy is deterministic, so the response hash still matches). What breaks is representability: `output_tokens` must be a positive integer in the frozen condition family, so a `natural_eos` cell **cannot be expressed at all** without a schema-version bump on the mint path. `natural_eos` exists only in the suite layer (`joulewise/suite.py:44`). Pairing survives; floor does not — differing lengths inject genuine variance into the absolute component. Length confound handling would require pre-registering length as part of the effect (see Q2). Verdict: closed by construction for `_v5`.

**(d) Small mixed profile (chat / long-form / code).**
The registered vehicle exists and is already shape-matched: `jw_mixed_v1`, 48 items, six categories, **all at 512/256** precisely so category is tested at fixed shape (AP-4's rule: category residual CI inside ±2% of request energy *and* the 2% margin exceeding `max(floor_abs_j, floor_cmp_j)`). Determinism: fine (one manifest per cell, per-item hashes). Pairing: fine. Floor: per-item prefill windows are individually checked, and 512 tokens gives 2–3 records — the existing suite bundles literally print `prefill: not_resolvable_sample_count`, so a mixed profile buys nothing for the prefill arm unless its items are lengthened too. Night: 5-item suite = 65 s wall on the small model; a 48-item suite ≈ 3 min small / ≈ 4 min large per member, pushing 80 members to ≈ 6.5 h and past the runbook's 2–4 h window envelope. Blocking cost: the condition-family schema cannot describe a suite cell (`prompt_tokens` is `None` in suite configs) — mint-path schema surgery. Sentence: the best of the five (*"category explained no energy beyond token shape"*), and the right **first post-campaign window**, not `_v5`.

**(e) One standard-length question, same to both models.**
This is (a) with honest content, and is what I recommend, extended to fix the length. Determinism, pairing, night: identical to (a). Floor: identical. Resolvability: fixed only if the length is chosen against the record cadence rather than against the energy bar. Sentence: *"Both models processed the same pinned 2048-token question and emitted the same 512-token budget; 7B minus 1.5B was Δ J for token generation and Δ' J for prompt processing, each above its cell's resolution bound."* A reader understands that in one pass.

---

## 2. The confound and the right pre-registered quantity

**Per-query energy at a declared cap is the only quantity the frozen machinery can gate, and it should stay the registered primary.** `FLOOR_METRIC_CATALOG` contains no per-token metric, so a per-token contrast has no floor, no precheck path and no estimator; the paper's Table 2 per-token columns are — correctly — *descriptive report columns* with a runtime-observed denominator, and Table 3's gated rows are per-member phase energy. Pre-register exactly that: primary = `phase_energy_j.decode` and `phase_energy_j.prefill` per member at the declared caps (128→512 decode; 2048-token prompt for prefill), Holm α = 0.05, m = 2, two-sided, per D-139 A2 / D-157 R-1.

Because `fixed_budget_exact` forces both models to emit exactly 512 tokens (`bundle_read.py:2202-2208` refuses a succeeded item whose emitted count differs), per-query and per-token are related by a **constant known before collection**, so the confound Ed names does not arise in the recommended design — that is the strongest argument for keeping the cap. Report both, and say why: per-query answers "what does one request of this shape cost", per-token answers "what does the marginal token cost", and at a fixed cap they are the same measurement divided by a constant. State the cap in the sentence, always.

If natural stopping is ever adopted (post-`_v5`), the honest pre-registration is *three* declared quantities, not two: energy per query with the stop policy named, energy per emitted token with the denominator runtime-observed, **and the emitted-length distribution itself published as a result** — because with natural stopping the length difference *is* part of the effect (that is C5-W.2, thinking-token inflation), and quietly dividing it out converts a finding into a nuisance parameter.

---

## 3. Concrete recommendation for `_v5`

**Workload to freeze.**

- **Decode arm** (unchanged shape): one pinned prompt at exactly **128 tokens**, `output_tokens = 512`, `fixed_budget_exact`, greedy, `repetitions = 1`, `warmup_runs = 1`. Prompt **text** replaced by a real, self-contained task (a short document + a question about it), padded/truncated to exactly 128 ids **on both tokenizers of the D-164 tokenizer-identical pair**, pinned by `prompt_text_utf8_sha256` and by prompt-token-ids SHA. Keeping 128/512 preserves floor transfer from the two floor packs, whose decode cells are `df_ph_decode` at 128/512.
- **Prefill arm**: same real prompt family, extended to **2048 prompt tokens** (4096 if Ed prefers measured margin over extrapolated), `output_tokens = 512` unchanged. Rename the family `prefill_p256` → `prefill_p2048` in the contrast pack **and** in both floor packs' dedicated prefill floor cells (`d117-df-ph-prefill-p256-*-absolute` and `-abba`, 2 cells + 1 reported cell per pack).
- **Number of distinct prompts per block: one.** Distinct prompts within a cell would inflate the absolute floor component with real content variance and break config-equality for the determinism gate. Content variation belongs to AP-6 / `RQ-CONTENT-SENTINEL`, in its own campaign.
- **Data source**: internally authored, license-clean, pinned in-repo (the `jw_mixed_v1` generator's provenance discipline is the model). Not GSM8K/HumanEval — that path is D-041-gated and unbuilt.

**Why 2048 (the arithmetic, shown).** Guaranteed 3 records needs > 0.242 s; 4 records needs > 0.363 s. From the fit, 256 tok → 0.160 s (**2 records, fails**); 1024 tok → 0.290 s (3, marginal); **2048 tok → 0.464 s (4–5, passes with margin)**; 4096 tok → 1.123 s **measured**, 10–11 records. Energy at 2048: small ≈ 25.6 J, large ≈ 112 J (using the measured 4.39× prefill ratio), **Δ ≈ 86 J** against the ~5 J effective bar — 17×, versus 2.3× at p256. The anchor-envelope quarter-rule also clears: it failed at p128 only because 0.600 J > 0.25 × 1.885 J; at 25.6 J the same ~0.6 J edge term is 2.3%.

**Night arithmetic.** Unchanged in structure: 2 arms × 10 blocks × 4 members = **80 members**, run as four sub-campaigns (2 decode halves, 2 prefill halves) with a reference between halves, at a **measured 148.1 s/member → ≈ 197 min** of member time plus ≈ 20 min of references and brackets, inside the pack's 310-min budgeted envelope and the runbook's 2–4 h per-window split with ≥20% margin. My change adds prefill time only: at 2048, +0.30 s × 20 (small) + ≈ +1.3 s × 20 (large) = **+32 s total**; at 4096, **+106 s total**. Under two minutes either way — because generation is 1.3–4.1% of member cadence and the night is bought by idle baselines (36 s), warmups (5 s) and cooldowns, not by tokens. `n = 10` blocks stays (D-062, D-163); note the ceiling if anyone proposes more: exact corner enumeration refuses above `n = 16`.

**Process cost.** Generator constants + prompt artifact + family ids + 6 cell ids across three packs — all regenerated for `_v5` anyway under D-164 — plus **one decision-log amendment to D-139 A2**, whose family is named "decode + `prefill_p256`" and which D-157 R-1 requires installed *verbatim*. That amendment is the only governance item; it is Ed's or the magistrate's, and it must be recorded before the mint, not after.

**The strongest counter-argument to my own recommendation.** By moving prefill to 2048–4096 tokens I make the prefill contrast trivially resolvable (17–35× the bar), and the paper thereby loses the one place where its two-gate decision rule was going to be genuinely *tested* rather than merely *exercised*. A metrology paper whose every gate passes by an order of magnitude has demonstrated its rule on easy cases only; §6's "Why 256 prompt tokens were selected" narrative and D-122's clearance arithmetic both get rewritten to a length chosen for admissibility rather than for a near-bar test, which a reviewer can read as the instrument being tuned until it agrees. My answer, and I hold it: the paper already owns its hard case as a *printed negative* — 37 of 50 short prompt-processing phases not resolvable, with a worked two-against-three record count — and D-160 R-5 rules that evidence-path claims are made only after a seat has executed the path. Executing it here says the p256 A-arm refuses on `insufficient_in_window_samples`. A refusal caused by a length the design could have chosen correctly is not a scientific result about the world; it is an instrument-design mistake that the reader will identify faster than we will.

---

## 4. Which registered RQs each option answers

- **(a) fixed synthetic / (e) standard-length same question — the recommended design.** `RQ-ATTRIBUTION-DOMINANCE` (the T26 capstone primary; falsifier = per-cell point-only vs timing-widened floor — needs *admitted* cells in both phases, which is exactly what my length change buys); `RQ-METHOD-FLOOR` (methodology artifact it consumes); `RQ-SHORT-PREFILL-RESOLVABILITY` (answered-L1, and the printed negative survives untouched); `C5-1.1` **pairwise L2 only** (two models never license a scaling claim — C-014, and `RQ-TWO-MODEL-ACTIVE-NONCLAIM` is the standing guard); `C5-1.3` (prefill/decode phase asymmetry, L2 structural — strengthened by a resolvable prefill arm); `RQ-MAC-BASELINES` (L1 per condition). Option (e) additionally makes the figure legible to a reader without changing a single gate.
- **(b) pinned benchmark items.** Adds `C5-I.1` (external benchmark energy signatures), `C5-I.2` (published-difficulty strata, L1 association), `C5-I.5` (prompt-template sensitivity), `C5-I.4` (harness overhead floor), `RQ-HUMANEVAL-IMPORT-SMOKE` (L0/L1 plumbing), and `C5-1.9` **only** under the C-004/C-014 correctness quarantine. Every one of these is gated behind `P2-022`/`P2-023`, both `BLOCKED — POST-2M-CORPUS` under D-041.
- **(c) natural stopping.** `C5-W.2` (thinking-token inflation, the operational-cost view under natural EOS) and `RQ-ENERGY-VARIANCE` (per-prompt energy-at-risk). Unrepresentable in the frozen condition-family schema; also the natural home for the D-164 exclusion of thinking-mode models.
- **(d) mixed profile.** `C5-W.1` (category beyond token counts — AP-4, the null-or-effect design `jw_mixed_v1` was built for), `C5-W.3` (category ranking stability, the workload-axis analogue of promoted Q5), `RQ-SHAPE-ENERGY` (AP-2), `C-023-COEFF-TRANSPORT`, `RQ-SESSION-SHAPE`, and — with a lengthened variant — `C5-1.2` (context-length scaling). This is a strong, cheap, already-half-built second paper-figure; route it to the post-`_v4` window queue beside D-163's fiducial and 3-point ladder, not into `_v5`.
- Unaffected by any option: `Q1`–`Q6` (hardware/split-gated), `C5-2.*`, `C5-3.*`.

---

## Assumptions I could not verify from the tree

1. **`docs/process_traces/2026-08-28-model-panel/` does not exist yet** — D-164's shortlist is unreadable, so every duration and energy number above is measured on Qwen2.5 1.5B/7B and *assumed* to transfer in shape (not in value) to the `_v5` pair. **The prefill-length choice must be re-measured on the actual pair before freeze** — a single un-instrumented timing run per model settles it in minutes, and it is the one desk check I would refuse to skip.
2. The 7B prefill duration at 2048/4096 tokens is extrapolated from a single measured point (0.279 s @128) via the 4.39× energy ratio; only the 1.5B curve has three measured lengths.
3. No issued floor artifact exists (`[RESULT PENDING ISSUED ARTIFACTS]` throughout §4/§6), so "~1 J" is the paper's diagnostic-era boundary scale and "~5 J" is the D-078/D-083 composed practical bar, not a current cell floor. The ratios 10.92 / 5.92 / 7.02 are explicitly retired-calculation diagnostics.
4. I did not trace whether the *floor-pack* p128 prefill cells for the small model would themselves be starved of admitted members by the same 2-record failure. Given the identical 128-token shape, I believe they would, and that would leave the prefill contrast with no floor at all — I flag it as the highest-value follow-up check and did not have time to execute it.
5. Whether the two arms could share one member set (one long prompt serving both the prefill and decode contrasts, halving the night or doubling `n`) is a real efficiency option I did not price; it changes the ABBA/family structure and correlates the two Holm contrasts, so I name it and do not recommend it before this campaign.

---

## Round 2 (addendum)

Read the addendum, the D-164 survey (commit `6b8927db`, not on `main`), the harness suite path, and the scoring/envelope machinery. The finding that reorganizes everything: **option (b) is already ~80% built in this repo, under a different name, with a ratified analysis plan — and it cannot be a `_v5` arm.** Full verdict below; the addendum is answered first because it is the leading path.

# Opus 5 seat — workload consult verdict (2026-08-28, revised for the addendum)

**Recommendation.** Ed's instinct is right and the repo already agrees with him: a pinned question set with deterministic scoring, natural EOS under a cap, and "did it finish in budget" as a co-outcome is **`affine_mod_ladder_v1` + AP-5 + `joulewise/envelope_gate.py`**, designed and merged in July 2026 for exactly this question (C5-1.9, "energy per correct answer rises as accuracy falls under a controlled per-attempt energy envelope"). The suite path already does natural EOS per item (`mlx_runtime.py:511` sets `suppress_eos = item.output_policy == "fixed_budget_exact"`), already emits `status: capped` + `stop_reason: length` when the budget truncates an answer (`mlx_runtime.py:527-536`, `suite.py:141`), already hashes every per-item response, and the envelope gate already runs E1–E4 invariance plus an **advisory E5 "early-EOS bias by correctness class"** — Ed's cap-truncation trap, pre-built. What is *not* built: the offline scorer join (no CLI writes `scoring.correct` into `suite_items.jsonl`), and any external-benchmark import — `benchmark_import`, `scoring.scorer_id`, `scoring.expected_answer_hash`, `scoring.correctness_quarantine` are **reserved-but-deferred fields that the schema actively refuses** (`suite.py:702-710`, `_reject_unknown(... deferred=...)` raises `SchemaError`), and P2-022/P2-023 (the HumanEval import rows) are both `BLOCKED — POST-2M-CORPUS` under D-041. **Structural ruling I would ask the magistrate to make loudly: option (b) is a second campaign and a second figure, not a `_v5` arm.** The frozen `_v5` machinery consumes `phase_energy_j.{decode,prefill}` from condition-family cells whose `workload_profile` is an exact-keyed `{name, prompt_tokens, output_tokens, repetitions, warmup_runs}` of **positive integers** (`floor_extraction.py:712-717, 798-810`); a suite cell sets `prompt_tokens: None` and cannot be expressed without a schema version bump on the mint path, which is the D-157/D-160 class of change that costs Sol-days and a fresh estate. So: **`_v5` keeps the single-prompt shape with two fixes (real pinned prompt content; prefill arm 256 → 2048 tokens, because I measured that 256 is inadmissible); the benchmark-scored campaign is prepared at the desk during `_v5` and owns a post-campaign window beside D-163's fiducial and ladder.**

---

## Part A — Option (b), developed

### (i) The defensible pre-registered quantity for "joules per solved problem"

It exists, ratified, in `docs/contracts/analysis_plans.md` **AP-5** (`FAM-C5-LADDER-SCORED-ENERGY`, `claim_role: secondary`). Pre-register exactly this and nothing stronger:

1. **Primary, gated:** *level-window energy* per model arm, compared against `max(floor_abs_j, floor_cmp_j)` for that level window (AP-5 "Floor gate"). This is the only quantity that meets a floor gate. Accuracy never gates anything.
2. **Secondary, conditional:** `energy_per_correct = level-window energy / correct count`, **computed only after the binomial guard passes** — AP-5 requires a binomial **lower bound ≥ 3 correct per level**, else adjacent levels merge, else the cell prints `not estimable`. This guard exists because the denominator explodes as correct → 0.
3. **Labelled co-outcomes, never gates:** accuracy by level; **malformed items counted as incorrect** in the accuracy denominator with malformed counts reported alongside (AP-5 amendment D-047.6); the per-model **capped rate** (`status: capped` / `stop_reason: length`) — this is Ed's "how close they get in their fixed budget", and it is a *result*, not a nuisance; and the emitted-token / stop-reason distributions.
4. **Multiplicity:** Holm within `FAM-C5-LADDER-SCORED-ENERGY` across the predeclared level-window-energy and energy-per-correct contrasts. This is a **different family** from the `_v5` D-139 A2 `m=2` family — do not merge them, or the `_v5` Holm denominator changes and D-157 R-4 (no post-hoc family selection) bites.

**Interaction with paired blocks — the load-bearing rule is D-047.3, quoted in AP-5:** *"under deterministic decoding, token, stop-reason, and correctness statistics are over distinct items; repeated bundles replicate energy only."* So an ABBA block of four bundles gives you **four energy replicates and zero extra correctness observations**. The correctness denominator is *distinct items*, and treating 10 blocks × 40 items as 400 scored trials is pseudo-replication that AP-5 forbids. Practically: pairing and the floor gate stay on energy exactly as today; accuracy is estimated once over the item set, per model, with its own binomial interval.

**Interaction with the floor gate:** benign, and that is itself worth knowing. A suite bundle's `analysis_contract` declares `primary_window_class: suite` with `allowed_aggregation_levels: [suite, block, level]` and `independent_unit: bundle`. Level windows are **seconds** long (measured: a 5-item, 256-token suite bundle spent 122.40 J / ~4.9 s in decode), i.e. tens to hundreds of power records — no resolvability problem at all. The flip side is the reason this cannot be the `_v5` headline: **a level window does not test phase-boundary attribution**, so option (b) contributes nothing to `RQ-ATTRIBUTION-DOMINANCE`, the capstone's primary falsifiable question, which lives on 0.14–6 s phase windows.

### (ii) Which benchmark

Ranked by what this repo can defend on 2026-09-01, not by name recognition.

| Candidate | Deterministic scoring | License / pinning | Fits a few-hundred-token cap | Small-vs-large spread | Verdict |
|---|---|---|---|---|---|
| **`affine_mod_ladder_v1`** (in-repo) | **Yes, built**: `score_response()` = `re.fullmatch(r"[+-]?[0-9]+")` on stripped text → `parse_status ∈ {parsed, malformed}`, `correct` bool; `expected_answer_sha256` domain-separated (`workloads.py:109-142`) | `license: synthetic-internal`, seed-derived, **contamination structurally impossible** | Yes — `natural_eos`, budget 16 tokens today; retunable | **Designed in**: difficulty = iteration count, levels 1/2/4/8/16/32/64, accuracy falls with `n_iter` while token budget is held ~constant | **Recommended.** Zero schema work, zero D-041 exposure |
| GSM8K | Exact-match on the final number — deterministic *if* the parse rule is pinned | MIT, but requires the **deferred** `benchmark_import` field + D-041 gate + P2-022/P2-023 (both BLOCKED) | Yes (~100–300 tokens with CoT) | Yes, large for 1.7B vs 8B | Post-`_v5` only |
| HumanEval | Requires code execution — a sandbox, not a checker | MIT; P2-023 is the row, blocked | Yes | Yes | No: execution-based scoring is a new trust surface |
| MMLU | Deterministic (letter) but prompts are ~100 tokens → **prefill unresolvable**, and a single-letter answer makes decode energy trivial | CC-BY, import blocked | Too short to be interesting | Modest | No |
| MT-Bench | LLM-as-judge — **non-deterministic scoring** | — | — | — | Disqualified outright |

The honest framing for the paper is that the *design property* Ed cares about — a controlled per-attempt energy envelope where difficulty moves accuracy without moving the token budget — is something a synthetic ladder **guarantees** and GSM8K only **approximates**. GSM8K's difficulty spread is confounded with CoT length, which is the exact confound of Q2. If Ed wants a recognizable name on the figure, the sequencing is: run the affine ladder now, and register GSM8K as the external-validity follow-up once `benchmark_import` is un-deferred.

### (iii) Distinct questions per block, and how repeats stay bit-exact

- **Distinct questions live as *items inside one manifest*, not as variation between members.** Every member of every cell runs the byte-identical suite manifest (pinned by `suite_manifest_sha256`); the A/B alternation is between **models**, never between questions.
- **Count:** the binomial guard needs ≥3 correct per level; the E5 EOS-bias audit needs `E5_MIN_DISTINCT_PARSED_PER_CLASS = 10` **correct and 10 incorrect** distinct items per level to be estimable (`envelope_gate.py:57, 588-625`). So a level sized at 8 items (the affine smoke default) can pass the binomial guard but can **never** run the audit that catches Ed's trap. **Recommend ≥24 items per level, at levels chosen to straddle ~50% accuracy, 3 levels → 72 items per bundle.**
- **Bit-exactness is preserved by construction, and I checked each link.** The sampler is pinned greedy at `temperature 0.0` and *hard-fails* if the mlx-lm sampler API is unavailable (`mlx_runtime.py:895-905`). Prompts are pinned as **integer token IDs** (`ItemSource.prompt_token_ids`, validated to equal `planned_prompt_tokens`; fed to the runtime verbatim with no `add_special_tokens`, `bos_present=False` — `mlx_runtime.py:886-888`). The determinism gate compares per-item `response_sha256` (`determinism_gate.py:311+`), requires config equality exact after removing only `run_id`, treats **`succeeded` and `capped` as equally eligible** statuses, and cross-checks the hash in `suite_items.jsonl` against the one in the `item_end` event. Natural EOS does **not** break bit-exactness — same model, same ids, greedy ⇒ same output and same length every repeat. What varies across *models* is length, which is the point.

### (iv) The honest paper sentence and the RQ

The bank already pins the template (`docs/research_question_bank.md:481`), and I would print it close to verbatim:

> On the controlled affine ladder, at the level band where level-window energy cleared its floor and the correctness denominator guard passed, Qwen3-8B-4bit consumed *E* J per correct answer against Qwen3-1.7B-4bit's *E′* J, with accuracy *a* versus *a′* over *k* distinct items per level and *c* / *c′* of them truncated at the 256-token budget before emitting an answer. Malformed responses are counted as incorrect and reported separately. No intelligence-per-joule claim is made, and the result does not state that difficulty causes energy.

**RQ:** `C5-1.9` — *"Energy-per-correct-answer vs difficulty; MoE-vs-dense controlled ladder"*, banked, ceiling **L2 after envelope and denominator guards**, AP owner **AP-5**, campaign owner *P2-010a + P2-010b + later scored campaign*, note *"Correctness remains quarantined annotation under the C-004/C-014 rules."* The killed row `RQ-INTELLIGENCE-PER-JOULE` is its forbidden upgrade — C5-1.9 is explicitly "the surviving minimal form". Also touched: `C5-W.2` (thinking-token inflation, if the capped rate differs by model), `C-023-OUTPUT-IDENTITY` (fixed output-token count is not fixed decoded work — the binding gate for any efficiency contrast), `C5-I.4` (harness overhead floor, if an external harness ever appears), and `RQ-ENERGY-VARIANCE`. **Gate to clear first:** TASK_QUEUE row `Q5 / P2-010` — *"P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail"* — status `GATED — WINDOW-COUNCIL-GATE [QUIET-MAC]`. C-014 makes this mandatory: *"before any scored campaign, an envelope-validation smoke gate must show level-invariant emitted-token and stop-reason distributions."* Five bundles on a window tail. Put it on the shakedown night.

### (v) Trap list

1. **Thinking-mode length blowup — the top risk with this pair.** Qwen3-1.7B/8B (April 2025) are *hybrid thinking* models. Today's forced-512 + `suppress_eos=True` makes the toggle unreachable, which is why the survey calls it moot for `_v5`; under **natural EOS it becomes load-bearing**, because a thinking model can emit hundreds of reasoning tokens, hit the cap, and never emit an answer. Cure: bake `enable_thinking=False` / `/no_think` into the **pinned token IDs**, and let `E1_stop_reason_invariance` (max non-EOS rate 0.05, max spread 0.05) prove it empirically rather than trusting the flag. Note the survey's finding that no `-2507` non-thinking build exists at 1.7B/8B, so this must be proven, not assumed.
2. **Cap-truncation bias against the large model.** If the 8B reasons longer, it caps more, scores incorrect more, *and* burns the full budget — energy-per-correct is penalized twice by one mechanism. `envelope_gate._advisory_e5` measures exactly this (mean emitted tokens, incorrect minus correct, per level), and AP-5 lists **"EOS-bias contamination"** among the disqualifiers that force `not estimable`. Pre-register the capped rate per model as a reported co-outcome so it can never be silently absorbed into accuracy.
3. **Answer-format parsing.** `score_response` is strict: anything but a bare integer is `malformed`, and malformed counts as **incorrect**. An instruct model behind a chat template will preface with prose and mass-malform. Cure: pin the answer-format instruction into the frozen prompt, pre-register the parse rule, report malformed counts. `lenient_correct()` exists and is documented *"diagnostic-only; never part of the primary score"* — keep it that way; promoting it after seeing the data is outcome-dependent retuning.
4. **Contamination.** Eliminated by construction for the affine ladder (`contamination_note: "seed-derived synthetic arithmetic item"`). For any real benchmark it is unmanageable at this scale — a small-vs-large accuracy gap on GSM8K may be a memorization gap, and this project has no way to rule that out.
5. **Chat template as code.** Do **not** add `apply_chat_template` to the runtime — there is currently no such call anywhere in `joulewise/` (verified). Render the template at *manifest build* time and pin the result as token IDs. The template then has a SHA, the harness stays byte-dumb, and the D-074 repeat-equality battery covers it. A runtime template call would put an mlx-lm/tokenizer version dependency inside the measured window.
6. **Turning `suppress_eos` off in the non-suite path.** Don't. `mlx_runtime.py:303` is hard-coded `True` and every `_v5` floor/contrast cell depends on exactly 512 emitted tokens (`fixed_budget_underrun` → `MALFORMED`). Natural EOS belongs to the suite path only, where it is already per-item.
7. **The missing scorer join.** No CLI writes `scoring.{parse_status, correct}` into `suite_items.jsonl`; `envelope_gate` reads those fields and degrades E5 to not-estimable without them. This is the one genuinely new artifact option (b) needs — a small offline join of `outputs/suite_items.jsonl` × the `*_annotations.json` sidecar through `score_response()`. **It must be written and frozen before collection**, or the scoring is post-hoc. Note the sidecar pattern is the right one and already in place: expected answers live *outside* the manifest the model sees.
8. **Family mixing.** Keep `FAM-C5-LADDER-SCORED-ENERGY` strictly separate from the `_v5` D-139 A2 `m=2` family.

**Night arithmetic for the scored campaign** (measured basis: 5-item/256-token suite bundle = 65 s wall on the 1.5B; decode rates 265 tok/s small, 84 tok/s large; member cadence median 148.1 s in the real 40-member contrast). 72 items, 256-token cap, mean ~120 emitted: added generation ≈ +33 s (small) / +103 s (large) per member → cadence ≈ 180 s / 250 s. Ten ABBA blocks × 4 members = 40 members ≈ **145 min**, inside the runbook's 2–4 h envelope with margin, plus the 5-bundle P2-010b smoke gate (~10 min) on a window tail. **One night.**

---

## Part B — the original four questions

### 1. What each option does to the six axes

**(a) Current fixed synthetic (128/512 decode; 256/512 prefill).** Determinism perfect; pairing intact (10 blocks × 4 × 2 arms = 80 members); decode floor arithmetic luxurious (Δ = **141.3 J** measured, against a ~1 J boundary scale and a ~5 J effective bar). **Resolvability FAILS, and this is the seat's central finding.** `MIN_PHASE_SAMPLES = 3` (`reduce.py:116`), record supports tile at median **0.1208 s** (observed sampler 8.87 Hz, not the requested 10). In `runs_window_contrast_20260730` I computed `window_evidence_precheck.phase.prefill` over all 40 members: **1.5B 0/20 eligible** (0.1376 s → 2 records; reasons `insufficient_in_window_samples`, `cadence_ratio_unrecorded`, `anchor_energy_envelope_exceeds_quarter_metric`), **7B 20/20 eligible** (0.2794 s → 3–4 records, cadence ratio 2.28, envelope ratio 0.13). Those reasons flow straight into the contrast's refusal list (`analysis_engine/__init__.py:819-822`). D-122 sized 256 tokens against the **energy** bar (5.810 J → projected 11.62 J) and never against the **precheck**. Night: 310 min budgeted, ~197 min of member time measured.

**(b) Pinned benchmark questions.** See Part A. Determinism fine; pairing fine; floors move to level windows (easy); night one window; **but** it needs the deferred `benchmark_import` field for real data, and it does not touch the attribution-dominance thesis.

**(c) Natural stopping in the `_v5` arms.** Not representable: `output_tokens` must be a positive integer in the frozen condition family. `natural_eos` exists **only** in the suite layer (`suite.py:44`). Closed by construction.

**(d) Mixed profile.** `jw_mixed_v1` exists — 48 items, 6 categories × 8, **all at 512/256** so category is tested at fixed shape (AP-4: category residual CI inside ±2% of request energy *and* the 2% margin exceeding `max(floor_abs_j, floor_cmp_j)`). Suite ABBA already exercised (20 bundles, `runs_recal_20260718`). Same schema blocker as (b); a 48-item suite pushes 80 members past the 2–4 h envelope.

**(e) Standard-length same question to both models.** This is (a) with honest content and an admissible length — my `_v5` recommendation.

### 2. The confound and the right pre-registered quantity

`FLOOR_METRIC_CATALOG` (`detection_floor.py:245-252`) contains **no per-token metric**, so a per-token contrast has no floor, no precheck and no estimator. **Per-query phase energy at a declared cap stays the gated primary**; per-token is a descriptive column with a runtime-observed denominator (the paper's Table 2 already has it). Under `fixed_budget_exact` both models emit exactly 512 tokens (`bundle_read.py:2202-2208` refuses a succeeded item whose count differs), so the two differ by a constant known before collection and **the confound does not arise** — the strongest argument for keeping the cap in `_v5`. Where lengths *do* vary (option b), the honest pre-registration is three declared quantities: energy per query with the stop policy named, energy per emitted token, **and the emitted-length and capped-rate distributions published as results** — because there the length difference *is* part of the effect (C5-W.2), and dividing it out silently converts a finding into a nuisance parameter.

### 3. Concrete recommendation for `_v5`, and the counter-argument

- **Decode arm unchanged in shape:** one pinned prompt at exactly 128 tokens, `output_tokens = 512`, `fixed_budget_exact`, greedy, `repetitions = 1`, `warmup_runs = 1` — preserving floor transfer from the two floor packs (`df_ph_decode` at 128/512). **Prompt text replaced** by a real, self-contained task, padded/truncated to exactly 128 ids on the Qwen3 tokenizer (`aeb13307…`, byte-identical across 1.7B/8B). This is free: the condition family pins token *counts*, not text.
- **Prefill arm 256 → 2048 prompt tokens** (4096 if Ed prefers measured over extrapolated margin), with the same move applied to the dedicated prefill floor cells in **both** floor packs (`d117-df-ph-prefill-p256-*-absolute` / `-abba` + the reported cell, per pack). Arithmetic: 3 records need duration > 0.242 s, 4 need > 0.363 s. Measured 1.5B points — 128 tok → 0.1376 s (2 records), 512 tok → 0.186–0.220 s (2–3; the bundle literally prints `prefill: not_resolvable_sample_count`), 4096 tok → **1.123 s, 10–11 records**. Fit ⇒ 256 tok ≈ 0.16 s (**2, fails**); 1024 ≈ 0.29 s (3, marginal); **2048 ≈ 0.46 s (4–5, passes)**. Effect at 2048: Δ ≈ 86 J versus 11.6 J at p256; the anchor-envelope quarter-rule clears with room (the ~0.6 J edge term is 2.3% of 25.6 J, versus 32% of 1.885 J today).
- **One distinct prompt per block.** Distinct prompts within a cell inflate the absolute floor component with real content variance and break config equality for the determinism gate.
- **Night cost of my change: +32 s total at 2048, +106 s at 4096**, on a 310-min budget — because generation is 1.3–4.1% of the 148.1 s member cadence.
- **Governance:** one decision-log amendment to **D-139 A2**, whose family is named "decode + `prefill_p256`" and which D-157 R-1 requires installed *verbatim*. Record it before the mint. Also: the survey's fact 2 — the prompt is frozen as **text**, so the Qwen3 tokenizer re-derives the count anyway; do that re-derivation once, at the new length.

**Strongest counter-argument to my own recommendation.** Moving prefill to 2048 makes that contrast resolvable by 17×, so the paper's two-gate decision rule is demonstrated only on easy cases, and a reviewer can read a length chosen for admissibility as an instrument tuned until it agreed. My answer: the paper already owns its hard case as a **printed negative** (37 of 50 short prompt-processing phases not resolvable, with the worked 2-against-3 record count), and D-160 R-5 says evidence-path rulings are made only after a seat has executed the path. I executed it: the p256 A-arm refuses on `insufficient_in_window_samples`. A refusal caused by a length we could have chosen correctly is not a result about the world.

### 4. RQ coverage by option

- **(a)/(e) — recommended `_v5`:** `RQ-ATTRIBUTION-DOMINANCE` (capstone primary; needs *admitted* cells in both phases, which the length fix buys), `RQ-METHOD-FLOOR`, `RQ-SHORT-PREFILL-RESOLVABILITY`, `C5-1.1` **pairwise L2 only** (C-014; `RQ-TWO-MODEL-ACTIVE-NONCLAIM` is the guard), `C5-1.3`, `RQ-MAC-BASELINES`.
- **(b):** `C5-1.9` (primary), `C-023-OUTPUT-IDENTITY`, `C5-W.2`, `RQ-ENERGY-VARIANCE`; with a real import, `C5-I.1`, `C5-I.2`, `C5-I.5`, `C5-I.4`, `RQ-HUMANEVAL-IMPORT-SMOKE`. Forbidden upgrade throughout: `RQ-INTELLIGENCE-PER-JOULE` (killed).
- **(c):** `C5-W.2`, `RQ-ENERGY-VARIANCE`. Unrepresentable in `_v5`.
- **(d):** `C5-W.1` (AP-4), `C5-W.3`, `RQ-SHAPE-ENERGY` (AP-2), `C-023-COEFF-TRANSPORT`, `RQ-SESSION-SHAPE`, and with lengthened items `C5-1.2`.

---

## Assumptions I could not verify from the tree

1. `docs/process_traces/2026-08-28-model-panel/00-SURVEY.md` is **not on `main`** — I read it from commit `6b8927db`. All durations/energies above are measured on Qwen2.5 1.5B/7B and assumed to transfer in *shape*, not value, to Qwen3-1.7B/8B (neither is mirrored locally yet). **The prefill length must be re-measured on the actual pair before freeze** — one uninstrumented timing run per model; it is the one desk check I would refuse to skip.
2. 7B prefill at 2048/4096 tokens is extrapolated from one measured point (0.279 s @128) via the measured 4.39× energy ratio.
3. No issued floor artifact exists (`[RESULT PENDING ISSUED ARTIFACTS]`); "~1 J" is the paper's diagnostic-era boundary scale and "~5 J" the D-078/D-083 composed bar.
4. **Not executed, and high value:** whether the floor packs' *p128 prefill* cells are themselves starved by the same 2-record failure on the small model. At the identical 128-token shape I believe they are — which would leave the prefill contrast with no floor at all. Highest-priority follow-up.
5. The scored-campaign night arithmetic assumes mean ~120 emitted tokens under natural EOS at a 256-token cap; unmeasured for Qwen3 and the first thing the P2-010b smoke tail would settle.
6. I did not price sharing one member set across both `_v5` arms (one long prompt yielding both phases — halves the night or doubles `n`); it changes the ABBA/family structure and correlates the two Holm contrasts. Named, not recommended before this campaign.
