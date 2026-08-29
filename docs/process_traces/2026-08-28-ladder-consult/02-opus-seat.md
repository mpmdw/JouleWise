# Opus seat — _v5 model-ladder design (Opus 5, read-only, blind). Verbatim.

All four investigations are in. Here is the answer.

---

# LADDER-CONSULT — design seat answer

## 1. DESIGN SPACE

`analysis_manifest_v3.py` is a **per-campaign frozen sibling module**, not a parameterised engine (docstring `:1-8`: "intentionally a sibling of the byte-frozen Slice-2M v1 schema… owns the one ratified Splitwise decode contrast"). Nothing k-way is expressible today. The prospective validator refuses, in order:

- `:2034-2045` — `condition_families` must be **exactly 4** bindings covering slots `{(decode,A),(decode,B),(prefill_p256,A),(prefill_p256,B)}` → `analysis_prospective_schema_invalid`, then `analysis_prospective_contrast_cover_mismatch` at `:2125`.
- `:2276`, `:2283-2285`, `:2596-2605` — `contrasts` must be **exactly 2**, arms exactly `{decode, prefill_p256}`.
- `:2377-2389` — each contrast's `condition_a_id`/`condition_b_id` must equal the slot map for its `measurement_arm`; **every contrast is a two-condition A/B pair**.
- `:2153` — `planned_n_blocks != 10`; `:2590-2594` blocks 1..10; `:2603-2608` exactly **80** members ordered 1..80.
- Frozen path adds `RUN_ID_RE` `:63`, two-entry `ARM_FREEZE` `:68-170`, `len(family_refs)!=2` `:778`, byte-equal `sampling_plan` `:731`.

What already works unchanged: `estimate_paired_blocks` (`estimators.py:450-513`) is generic in `(value_a, value_b)` and knows nothing about models; `holm_adjust` (`multiplicity.py:49-78`) is generic in `m`, requiring only `len(p_values)==m` (`:28-31`); `families` is a nonempty array with per-family `multiplicity.m` (`:2186-2271`).

So **(a) k−1 pairwise against a fixed reference, m=k−1** and **(b) adjacent pairs** are the same shape to the engine and both are blocked *solely* by manifest literals. **(c) monotone trend needs new code and is forbidden by doctrine**: C5-1.1 caps 4–6-model designs at "descriptive L2 pairwise contrasts", "no active+total+KV regression on 4-6 models" (`research_question_registry.md:64`, `:123-128`); the escape is a set larger than 6 with a *predeclared one-covariate* fit. T26 ruling item 9 narrows further: "never an active-parameter scaling law."

**Code cost:** don't generalise v3 — mint `analysis_manifest_v5.py` as the next frozen sibling. Surface: 4196-line module + 2327-line generator + 10 test modules + `run_campaign.py`, `finalize_analysis_manifest.py`, `arm_readiness_evidence.py`, `window_duration_margins.py`, `analysis_engine/artifact.py`. **6–10 Sol xhigh days with the C-028 gauntlet.**

## 2. FLOORS

Cell key = `detection_floor.py:1842-1849` plus stack identity hashed into `source_regime` (`:1519-1530`), whose eleven governed fields include `model_artifact_sha256` (`identity_pins.py:48-60`). `transport_refusal_reasons` (`:4295-4313`, `:4343-4348`) refuses cross-model as `stack_mismatch`. **Five sizes = five independent mint chains.**

Per size, the frozen v3 floor pack = **100 members, 3 mints** (decode, p128 rider, p256), 6 calibration floor cells, **1 bracket session** (pre+post) — ratified **6.28 h (1.5B) / 6.48 h (7B)**, 20% margin included (`decision_log.md:8941-8944`). Decode-only 50-member shape: **3.14/3.24 h** (`DESIGN-MEMO:315-329`). Contrast pack: 80 members, **310 min = 5.17 h**; decode-only 40-member arm **168 min**. Fixed per-night overhead **70 min core / 84 min margined** and it **never amortises** — the NEG-8 bound must be minted inside the window using it (`window_runbook.md:158-162`).

Nights, decode-only, reusing `_v4`'s 1.5B/7B floors and its 1.5–7 contrast:
- **4-size (+0.5B, 3B):** 2 floor packs = 2×104.4+84 = 293 min (4.9 h) → 1 night; 2 contrasts = 252 min (4.2 h) → 1 night. **2 nights** (3 if split).
- **5-size (+14B):** 3 floor packs = 397 min (6.6 h) → 1–2 nights; 3 contrasts = 336 min (5.6 h) → 1 night. **3–4 nights**, plus a mandatory 14B timing probe (`window_runbook.md:136-140` forbids size-based inference).

**fixed_n = 10** is pinned at `generate_configs.py:51`/`:2026`, `calibration_plan.json:6`, `N_BLOCKS` `:92-95`, validator `:2153`/`:731`. **D-062 does not authorise n=5** — it is the rule that outlawed start-at-5-and-grow, steers "nearer 10 than 5 for near-floor comparisons," and demotes top-ups to exploratory (`decision_log.md:3327-3336`). n=5 is legal only frozen in advance and costs `small_sample_guard_factor` = √(9/4) = **1.5 — a 50% wider floor** (`detection_floor.py:664-672`), plus t 2.776 vs 2.262. Wrong economy: saves half a night, widens every rung's floor.

## 3. WORKLOAD

**Do not change it.** Two regimes:

- **Prefill:** the ~1 J attribution term is duration-independent while the effect grows with prompt length, so lengthening buys clearance linearly (`decision_log.md:4763-4767`, `:7953-7959`). That is why p256 was chosen: 5.809930 J at p128 → 11.619860 J projected (`draft-v1.md:268-272`).
- **Decode:** the comparative cell floor scales *with the cell* — 13.998036715259254 J on a 192.386233 J member mean = **7.3%** (`decision_log.md:5392`). Adjacent-size Δ scales identically, so **Δ/floor is ≈invariant in decode length**. Lengthening decode does not improve the floor gate at all.

Assumption (stated): the two diagnostic anchors **50.257 J (1.5B) / 192.386 J (7B)** at 512 tokens (`prop-param-scaling-energy.md:5559` — permanently non-claim-bearing, sizing only) project **24/50/90/192/371 J**. Smallest step 0.5B→1.5B ≈ **26 J** ≈ 0.051 J/token: **5.2× the ~5 J bar, ~7× a projected 1.5B comparative floor** (0.073×50 ≈ 3.7 J). All other adjacent steps sit at 6–7×. Clearing 5 J alone needs ~98 output tokens. **The answer is 512 — the length already frozen** — and `draft-v1.md:302` forbids length-as-repair regardless.

The near-floor rungs live in **p128 prefill**: projected 0.6/1.6/3.3/7.6/15 J → steps of 1.0, 1.7, 4.3, 7.4 J against the ~5 J bar = refuse, refuse, marginal, clear. That mixed outcome is the ladder's only instrument-exercising content.

## 4. MODELS

Mirror `/Users/edr/jw_models/mlx-community/`: **0.5B (276 MB), 1.5B (839 MB), 7B (4.0 GB) on disk. 3B and 14B are absent and unpinned anywhere.** Only 1.5B (`8b403126…`) and 7B (`c26a38f6…`) are D-016-admitted; 0.5B is mirrored with its own provenance tree (`a5339a41…`) but appears in zero configs.

**Tokenizer:** `tokenizer.json`, `vocab.json`, `merges.txt` are **byte-identical across 0.5B/1.5B/7B**, and `tokenizer.json` equals the pinned `SHARED_TOKENIZER_JSON_SHA256 = a8506e71…` (contrast generator `:453-455`). The p256 prompt therefore tokenises identically on 0.5B — no new prompt. Caveats: the repo's token-id pin is prefix-only ("no full-hex token-ID pin exists in-tree", `d117_floor_qwen25_7b_v3/plan_tree.json:779`); `tokenizer_config.json` **differs** on 7B; `vocab_size` is 151936 (0.5B/1.5B) vs 152064 (7B), and `vocab_size` is in `determinism_gate.py:88` `_TOKENIZER_IDENTITY_KEYS`. For 3B/14B, tokenizer identity is conjecture (`model-search-12gib.md:136`).

**Memory:** 0.28/0.84/~1.74/4.28/~8.32 GB. 128 GB is a non-issue (a 65 GB Qwen3.5-122B mirror exists). The binding constraint is D-073's cross-target 12 GiB cap (Mpeak ≤ 10.2 GiB), which 14B strains — though D-073 leaves big models open Mac-only.

**Net: 0.5B is a one-desk-day admission; 3B and 14B each need a fresh mirror, revision SHA, licence/provenance receipts, and the D-074 gate battery.**

## 5. WHAT THE PAPER GAINS

Strongest honest sentence: *"On the named M3 Max / MLX / powermetrics configuration, 512-token decode energy for 4-bit Qwen2.5 at 0.5B, 1.5B and 7B — each gated by its own independently minted cell floor — was ordered by parameter count with every adjacent pairwise contrast resolved, while the same ladder's 128-token prefill contrasts refused at the two smallest steps."* RQs: **C5-1.1 in its permitted pairwise form only, never a scaling relation**; it retires RQ-TWO-MODEL-ACTIVE-NONCLAIM by making two points three. RQ-SHAPE-ENERGY is untouched (that is workload shape, not model size).

**The argument against is strong and already in-repo.** The ladder's decode rungs land at 6–10× the floor, and the project's own referee wrote: *"An effect at 20–56× the detection floor does not need this instrument… It needs a wall socket and a stopwatch."* The paper's thesis is attribution **dominance**; a ladder whose every rung clears trivially demonstrates that thesis least. §7 already names a deliberate micro-delta challenge at 0.5×/1×/1.5×/3× an issued floor (`draft-v1.md:316`) — the same "decision behaviour at varying distances from the floor," cheaper, with no new models and no new floors.

**Impressiveness per night:**

1. **Inserted-gap fiducial (TRANSFER-FIDUCIAL-01).** ~10 runs, well under one night. Closes §7 **Limitation 1** — the paper's stated #1 weakness and the one thing `_v4` structurally cannot test. Already ruled (T26 item 16), registered (`TASK_QUEUE.md:595`, blocked only on `_v4` close), diagnostic and non-claim-bearing → **no new manifest, no floor mint, no model admission, no Holm family.**
2. **Model ladder, 3-point 0.5/1.5/7 only.** 2 nights, ~1 desk-week of manifest work, one new floor mint, one new pairwise contrast, plus the mixed prefill refusal.
3. **Quantization axis.** Registered (C5-1.12), adopted as the P2 paper — but ADJUDICATION's own correction puts it at **four** nights, because the existing Q4 artifact cannot be byte-matched (it stores non-quantized parameters as F16 and carries no "mode" key), and it needs C-023-QUALITY-EQUIV-QUANT, a D-016 amendment, and Ed's still-owed posture ruling. Not a seven-day item.

## 6. CONCRETE PLAN

**Minimal changes, if funded:** (i) `analysis_manifest_v5.py`, sibling of v3, replacing four literal pins — `expected_condition_slots` `:2034-2040` → derived from declared arms; `len(conditions)!=4` `:2041` and `len(contrasts)!=2` `:2283` → per-manifest counts; `planned_n_blocks != 10` `:2153` → the frozen value; the 80/1..80 cover `:2603` → 4·n·|contrasts|. **Leave `holm_adjust` and `estimate_paired_blocks` untouched** — that is the point of the pairwise shape. (ii) `d117_ladder_*_v1` generator cloned from the contrast pack: decode-only, n=10, one Holm family with m = new-contrast count. (iii) `d117_floor_qwen25_0p5b_v1` cloned from the 1.5B floor pack, decode-only. (iv) D-016 pin for 0.5B (`a5339a41…`) + a tokenizer-hash regression against `a8506e71…` + a `vocab_size` note against `determinism_gate.py:88`.

**Desk-only sequence during `_v4`.** Every campaign night is QUIET-MAC: `AGENTS.md:91` / `CLAUDE.md:35` forbid any agent session touching them, and D-150a keeps the machine untouchable on window nights. So all of the below is daytime desk work: design consult + this packet → v5 module + regressions → generator + pack → 0.5B floor pack + D-016 pin → independent audit → distinct-lens refuters → fix rounds → delta re-audit → freeze. That is **6–10 Sol xhigh days of gauntleted work against a 7-day calendar already carrying `_v4` operation, round-7 paper fills and the advisor brief.**

**Earliest `_v5` night.** Campaign close ≈ Sun 09-06, and TRANSFER-FIDUCIAL-01 owns the first post-campaign diagnostic window by ruling. A `_v5` floor night is therefore **not before Tue 09-08**, contrast night ~09-09, results ~09-10 — i.e. after the moved advisor meeting week, not before it.

**Recommendation.** Run the fiducial first (highest paper value per night, and it is the only item that repairs a *stated* weakness rather than adding a capped new one). Freeze the 3-point 0.5/1.5/7 ladder at the desk as the funded contingency — 0.5B is already mirrored and tokenizer-identical, which is the whole reason the 4- and 5-size versions are disproportionately more expensive. Do not attempt 3B or 14B in this window.
