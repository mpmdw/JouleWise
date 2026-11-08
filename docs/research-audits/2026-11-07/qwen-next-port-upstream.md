# Qwen-Next (qwen4_exp, Qwen3.8-Flash-Next) MLX port: what is achievable, and the upstream path

Research track, 2026-11-07 (Saturday evening PST).

- **Asked by Ed:** "dont just review the research set it against our methodology and see if theres anything new/interesting that arises for use of that machine - also research what could be achievable re porting qwen next and possibly upstreamed".
- **Method:** two independent seats (Fable 5.1 and Opus 5.5) researched the question separately. The lead synthesized their reports and checked every disagreement against the repo, the live GitHub and Hugging Face APIs, and the L3 gold work folder on the Air.
- **What was not done:** nobody ran MLX, loaded real weights, ran community code, posted upstream, touched the MBP or opened a blinded path.
- **Layout:** executive summary → decisions for Ed → synthesized report (with research ideas) → appendix with both seat reports verbatim.
- **Scripts:** the noise-floor scripts behind §2 of the report are committed next to this file in `qwen-next-port-upstream-scripts/` (`noise_floor.py`, `noise_floor_fp32ref.py`). They read only the L3 head logits in `/private/tmp/jwgold-run-l3/work/parity/head` and the committed `reference-top64.npz`.

---

## Executive summary

1. **The port is correct everywhere the laptop could test it, but the 128 GB Mac has measured nothing yet.**
   - Laptop results: canonical module `f4ec75d1…`; tiny-config gold parity (fp32 ≤ 9.8e-6, bf16 ≤ 1.07× noise); real-weight layer parity 13/13; a 48-layer bf16/fp32 reference chain on 12 real prompts.
   - Still open: full 48-layer MLX parity (GOAL 5/11) and any real-weight test of sparse attention (L3 prompts are ≤ 507 tokens; sparse attention starts at 2,052).
2. **The new finding: the quant-quality POLICY cannot be passed as written.**
   - Scored by the POLICY's own formula, the exact fp32 model reads `reject` against the bf16 reference: mean projected KL 0.0208 vs a bar of 0.020, p99 0.380 vs 0.10/0.25.
   - Sunday's score would therefore fail whatever the artifact's quality.
   - The lead re-registers the POLICY and Gate S S3's bf16 bars against the measured precision floor, blind, before any variant is scored (decision 10, FYI).
3. **Disk is the binding constraint, then I/O, then memory.**
   - maxfit needs ≈293 GB of internal disk against ≈66 GB free.
   - Prefill n-gram I/O is serial and likely takes 30-50 % of prefill until module v2 adds batched `pread` and an async prefetcher.
   - maxfit's predicted margin is 2.7 GB, so maxfit5 is the likely production profile.
4. **Expected speed: decode ≈16-25 tok/s (centre ≈20).** The cause is a per-token host sync in the module. Gate S's 15 tok/s screen probably passes; the 30 tok/s P5 target will not.
5. **Proposed logistics:**
   - plug the SSD (Sunday at the earliest) into the **M4 Air** and run download and conversion there overnight;
   - MBP time drops to about 4-8 daytime probe hours, and the SSD never touches the MBP during R1.
6. **Upstream:**
   - Best value per Ed-hour: the mlx-vlm D1 fix. The bug is still on main and unreported, and the kit is ready.
   - Next: a coordination comment on the stalled mlx-lm #1788, not a competing PR.
   - mlx-lm and llama.cpp ban AI-written posts, and llama.cpp bans agent-run pushes and PRs. So Ed writes every word and does every push upstream.
7. **New research angles for the 128 GB Mac:**
   - a fidelity-energy frontier scored against the precision floor, on agentic text;
   - measured energy of SSD-resident parameters;
   - joules of pure software overhead from bitwise-identical variants;
   - J per byte of weight traffic;
   - flat decode energy with context under sparse attention;
   - energy per accepted token with MTP.

---

## Decisions for Ed

1. **SSD on the Air first.** Approve plugging the borrowed SSD into the M4 Air first (Sunday, about 30 min of you):
   - inspect it read-only, then create an APFS volume `JW-EXT` (erase only with the lender's consent);
   - turn Spotlight off, run `caffeinate`, start the download.

   The Air then downloads and converts maxfit (plus maxfit5 if ≥ 800 GB is free) overnight, unattended. The kit has no host check, and the Air already has the S0 pins. The MBP then needs only 4-8 daytime hours of probes. The SSD never touches the MBP before the offload baseline or during R1.
2. **MBP slot ranking.** Tell the magistrate how to rank the MBP daytime slots (they can never overlap R0/R1/W1): Flash-Next probes (4-8 h) vs the 6.8 h always-attached SSD qualification. **Recommendation:** the FN probes take the first free day after R1, and the qualification goes after.
3. **Precision call on a quantized n-gram table.** May the SSD day also score a quantized table candidate?
   - **Candidates:** maxfit4 + q4 table held in RAM (about 106-110 GB on disk, 110.7-114.5 GB physical), or maxfit-ple8 paged (161.8 GB).
   - **For:** it is the only build with zero disk I/O inside windows, and the cheapest disk fix.
   - **Against:** it puts the n-gram table at 4/8-bit, against "as close to full fp16", and needs a new module mode and a new Gate S.
   - It is scored, never adopted, unless you accept the measured cost.
4. **E1 internal disk.** Authorize:
   - (a) deleting the two dropped models, Qwen3.5-122B-4bit and Next-80B-Instruct-4bit (+114.5 GB, public weights);
   - (b) a census of non-restricted roots for at least 35 GB more.

   Without a reclaim, Flash-Next energy data either waits for the block-5 release offload or leaves this series, and Sunday's results stand as port validation only.
5. **Keep E5 deferred.** E5 is an 8-bit dense core. Corrected figures: it saves only about 4.6 GB of memory and no disk, and cuts decode bytes about 40 %. Revisit only if the Mac shows decode below 15 tok/s at 16K and the bytes regression shows decode is bandwidth-bound rather than host-sync-bound.
6. **mlx-vlm D1.** The bug is still unfixed on main and unreported.
   - Read `fix.diff`.
   - Re-run `repro_minimal.py` yourself on current main in a fresh venv.
   - Write the issue, and a day later the PR, in your own words with a one-line AI disclosure.

   About 2-4 h, with no dependency on the SSD.
7. **Confirm the upstream rule.** In mlx-lm, llama.cpp and mlx-vlm, you personally write every post, PR description, commit message and reply, and you do every push and PR creation. Agents never do.
   - llama.cpp's AGENTS.md bans agent-run pushes and PRs (penalty: a ban).
   - mlx-lm bans AI-written posts.

   This overrides our "drive PRs end to end" practice for external repos.
8. **mlx-lm #1788.** Write a coordination comment offering our verification assets once you have read the test file and the parity report. No competing PR until all of these hold:
   - there is a response, or about 2 weeks pass;
   - your `/code-review ultra 675` is done;
   - an mlx-lm-main venv (mlx ≥ 0.32.3) is approved.
9. **Reviews.** Launch `/code-review ultra 675` on the canonical module (you can launch it; I cannot). Later, run it on module v2 before v2 is frozen.
10. **FYI, no action unless you object.** This is a lead ruling under your 11-06 delegation, made blind tonight before any artifact exists.
    - The quant-quality POLICY and Gate S S3's bf16 bars will be re-registered relative to the measured precision floor: score against the fp32 chain, with bars set as a ratio to the official bf16 chain's own distance (the bound-(f) style).
    - Reason: as written, they classify even the exact fp32 model as `reject` (mean projected KL 0.0208, p99 0.380), so Sunday's score would fail regardless of quality.
    - The L3 logits will also be moved out of `/private/tmp`.

---

## Synthesized report

### Qwen3.8-Flash-Next (qwen4_exp) MLX port: what we can get done, what it means for our methods, and what can go upstream

This report synthesizes two independent seat reports (Fable 5.1 and Opus 5.5), dated 2026-11-07 evening PST.

- I checked every disagreement against the repo, the live GitHub and Hugging Face APIs, and the L3 gold work folder on the Air.
- Anything I could not check is listed in §8 and was not used for any conclusion.
- I ran no MLX, loaded no model weights, ran no community code, posted nothing, opened no restricted path, and committed nothing during the research.

#### 0. Bottom line

1. **The port is correct everywhere the laptop could test it. The 128 GB Mac has measured nothing yet.** Both seats agree and I confirmed it.
   - The canonical module is `f4ec75d1…`. I re-hashed it from `lane/2026-11-06-qwen4exp-quality-ref`.
   - Gold parity on tiny configs: fp32 ≤ 9.8e-6, bf16 ≤ 1.07× the reference's own noise.
   - Real-weight parity on layers 2/3, embed/head and a PLE shard: 13/13 pass.
   - A 48-layer bf16 reference exists (L3, 12 prompts).
   - **Not established:** a full 48-layer MLX-vs-reference parity run (GOAL 5/11), and any real-weight test of sparse attention.
2. **New finding (I measured it; neither seat had it): the quant-quality POLICY cannot be passed, even by a perfect port.** I ran the L3 fp32 reference chain through the POLICY's own formula as if it were the variant. The fp32 "truth" scores:
   - mean projected KL **0.0208** (bar 0.020);
   - p99 **0.380** (acceptable bar 0.10, marginal bar 0.25);
   - top-5 overlap 0.920 (bar 0.90).

   So the POLICY labels fp32 itself **`reject`**. Full-vocabulary KL(bf16‖fp32) averages 0.0217. That matches an independent community figure: nace-ai reports a bf16 noise floor of KL 0.024.

   As written, Sunday's maxfit score is certain to read `reject` whatever the artifact's quality, and both seats made "POLICY acceptable" a GO condition. The lead must re-register the POLICY **before** any variant is scored, so the ruling stays blind (§2).
3. **Disk is the binding constraint, then I/O. Memory is a close third.** Two corrections:
   - **The "all-resident maxfit4 + q4 n-gram table" build is not the free lunch seat 1 described.**
     - At 4-bit the n-gram table is 28.2 GB (group 80) or 32.0 GB (group 32), not 25.6 GB. mlx-vlm #2045 confirms "about 30 GB at Q4".
     - It would sit in host RAM, not Metal. Total physical use is 110.7-114.5 GB, the same memory-pressure class as maxfit.
     - It needs a **module** change: `ple_storage_for` refuses non-bf16 tables for maxfit profiles, and `NgramTable` has no resident mode.
     - It is still the only build with zero disk I/O inside windows.
   - **Seat 1's 8-bit-core (E5) memory figures are wrong.** It needs ≈103 GB resident and ≈108 GB peak, not ≈60 GB. An 8-bit core saves only ≈4.6 GB of memory, but cuts decode bytes ≈40 %.
4. **Decode speed: about 16-25 tok/s, centred near 20.** The module forces a host sync on every token (`qwen4_exp.py` line 1834: "Host sync: the n-gram rows depend on the token ids just fed"). That defeats MLX's overlap of encoding token t+1 while token t runs.
   - The bandwidth floor alone gives ≈28 tok/s.
   - mlx-vlm measured 19.0 tok/s for Q4 on an M2 Ultra.
   - Gate S's 15 tok/s screen at 16K probably passes. The 30 tok/s P5 target will not.
5. **The prefill n-gram I/O risk is real (seat 2 is right).**
   - There is one table with 16 heads, so a 512-token chunk does up to 8,192 lookups.
   - The `mmap` path skips its prefetch above 4,096 unique rows. The `pread` path reads one row at a time.
   - mlx-vlm measured ≈148 µs per cold miss. At that rate one chunk costs ≈1.2 s of I/O, so gather time is 30-50 % of prefill.
   - The R0-FN-b "≤ 15 % of prefill" bar fails without F16 (batched `pread`) plus an async prefetcher. Prefill token ids are known in advance, so this is straightforward.
6. **The SSD arrives Sunday at the earliest** (RUN_STATE 199). R1 may hold the MBP's nights, and the SSD must stay unplugged during R1 (item 202). Seat 2's plan is therefore the right one, and I verified it in code:
   - plug the SSD into the **M4 Air** and run download → maxfit (and maxfit5) conversion there, unattended overnight;
   - the kit never checks the host model;
   - the converter writes bounded slices through `mx.quantize`;
   - the Air already has the S0 pins (mlx 0.31.2, mlx-lm 0.31.3, transformers 5.22.1).

   MBP time drops to about 4-8 daytime hours of probes.
7. **Upstream:**
   - **mlx-vlm D1** (ragged-batch sparse attention drops the selection) is still on main and nobody has reported it. `language.py` blob `9a9bee24` is identical to the audited `5cdc659b`, and mlx-vlm has no AI-use rule. It is the best value per Ed-hour.
   - **mlx-lm #1788** is still open and labelled `await verification`; nothing has happened since 2026-10-04. The right move is a coordination comment, not a competing PR.
   - **llama.cpp:** its AGENTS.md forbids AI-written commit messages and any agent-run `git push` or `gh pr create`. So for upstream repos Ed pushes, writes and replies himself. That overrides our "drive PRs end to end" default.
   - Seat 2's #2 item (publish our reference because "no community quant publishes KL") is false. nace-ai, ddalcu, sh0wie and others publish KL against bf16. I downgraded it.

#### 1. Where the seats disagreed, and what I found

| # | Claim | Seat 1 (Fable) | Seat 2 (Opus) | Verdict | Evidence |
|---|---|---|---|---|---|
| 1 | SSD timing | in hand Saturday | Sunday at the earliest | **Seat 2** | RUN_STATE 199 (12:15 PST): enclosure slipped to Sun 11-08. Item 200: Ed puts ALIGN first; port Sun-Tue. Item 202: SSD unplugged during R1. |
| 2 | Decode speed, maxfit | 21-28 tok/s (bandwidth-bound) | 15-22 (overhead-bound) | **Reconciled: 16-25, centre ~20** | Host sync verified (line 1834). perf.md §6 assumed CPU encode overlaps ("MLX encodes token t+1 while the GPU runs token t"), which the sync breaks. mlx-vlm #2045: 19.04 tok/s, Q4, M2 Ultra, 21.6K. |
| 3 | Prefill n-gram I/O | ≈1-1.6 ms/token, ≈3 % | major prefill risk | **Seat 2** | `PREFETCH_MAX_ROWS = 4096`; `pread` loop is serial per row. Real config: `ple_layer_ids [2]`, `ngram_size 3`, `heads_per_ngram 8` → 16 rows/token, one table. #2045: 65,545 cold misses = 9.68 s in a 4K prefill at 217.8 tok/s. |
| 4 | All-resident maxfit4 + q4 table | ≈103 GB disk, ≈108 GB peak, 7.3 GB headroom, converter-only | ≈106 GB | **Both partly wrong** | q4 row = 80 B codes + 4 B per group (fp16 scale + bias): group 80 → 28.2 GB, group 32 → 32.0 GB. The table goes to host RAM: Metal 82.5 + 28.2/32.0 = 110.7/114.5 GB physical. Needs a new module profile and I/O mode (`ple_storage_for` raises "maxfit profiles require the bf16 n-gram table"). |
| 5 | E5 8-bit core | ≈60 GB resident, ≈65 peak, ≈162 GB artifact | ≈103 GB, ≈108 peak, ≈205 artifact | **Seat 2** | 120.8 B experts × 0.8125 = 98.15 GB, plus 4.91 B core × 1.0625 = 5.22 GB. |
| 6 | Community MLX quants | none matches our recipe | "~60, none publishes KL" | **Seat 2 wrong** | HF API: 287 MLX-tagged Flash-Next repos. Of the 40 most downloaded, 9 cards report KL or perplexity (nace-ai exact full-vocab KL vs bf16; ddalcu top-1024 KLD; sh0wie; sanasol2008; neopolita wikitext ppl). I found no MLX build of our recipe; a bf16 disk-backed n-gram table exists on other engines (gostar77 Radiance/AMD, 178.3 GB). |
| 7 | Air-first plan | — | proposed | **Verified** | `qwen4exp_mbp_live.py` checks only JW-EXT/APFS, launchd measurement agents and free space (no `hw.model`). Converter: bounded row slices + `mx.quantize`. Air venv at `/private/tmp/jwsol/venv-mlx` = mlx 0.31.2 / mlx-lm 0.31.3 / transformers 5.22.1. |
| 8 | Kit fragmentation, F15 | F15 not on sat-kit | F15 on no branch; one merge conflict | **Seat 2** | Scanned every remote branch for the reader: none. `git merge-tree` sat-kit `bb921a127` × quality-ref `92042869a`: CONFLICT in `scripts/qwen4exp_mbp_report.py`. The operator card still names `97d780d59`, which has no `--resume` for convert. |
| 9 | HF template change 812d96e1 | card touched | `{% generation %}` tags + `response_template` with implicit closes | **Seat 2** | I diffed both revisions. Rendered text is unchanged. `reasoning_content.close_pattern = "</think>|(?=<tool_call>)"`; parameters can close implicitly too. `chat_template` moved out of `tokenizer_config.json`. |
| 10 | transformers fixes | #49840 in 5.22.1; #49923 only on main | — | **Seat 1** | compare: #49840 merge commit is an ancestor of v5.22.1. #49923 diverged; v5.22.2 = 3 commits, none Qwen4. |
| 11 | mlx-lm main | — | `normalize_qk` (#1896) = our eps adapter; #2027 fused DSA prefill merged 11-05 | **Verified** | `gated_delta.py:33-44` scales eps by `inv_scale**2`. #2027 merged 2026-11-05T20:48Z. |
| 12 | llama.cpp converter | — | `ratio if layer_types[i] == "full_attention" else 0` | **Verified in code; runtime effect unverified** | `conversion/qwen4exp.py:89`. transformers 5.22.1 remaps to `indexed_attention` on load (`configuration_qwen4_exp.py:179-182`), so re-saved checkpoints would get ratio 0. No issue found. |
| 13 | Open llama.cpp qwen4exp items | — | "about 30" | **≈57** | search `qwen4exp is:open` = 57 issues + PRs |
| 14 | GOAL 5/11 full-depth parity | not established | not established; a2 gone | **Agree, plus** | `/private/tmp/jwgold-run-a2` is gone. Also, per `quant_quality.md`, a2 ran "17 positions of arbitrary token ids", so even a PASS would not have covered real text or sparse attention. The longest L3 prompt is 507 tokens, under the 2,052-token sparse threshold. |

#### 2. New: the quality gate sits below the bf16 precision floor

**Method.**
- Script: `qwen-next-port-upstream-scripts/noise_floor.py`, committed next to this document (originally in the lead's session scratchpad).
- It re-implements `qwen4_quant_quality.score` from `92042869a` verbatim.
- It scores the fp32 head outputs of the L3 gold work folder (`/private/tmp/jwgold-run-l3/work/parity/head/*-fp32-real`) against the committed bf16 top-64 reference (`reference-top64.npz`, sha `6c9dcb7c…`).
- Coverage: 12 prompts, 2,521 positions.

**Result** (as if a perfectly exact model were the variant):

| Metric | Reference's own floor (fp32 vs bf16 ref) | POLICY `acceptable` | POLICY `marginal` |
|---|---:|---:|---:|
| mean projected KL | **0.0208** | ≤ 0.020 | ≤ 0.050 |
| p99 projected KL | **0.380** | ≤ 0.100 | ≤ 0.250 |
| top-1 agreement | 0.979 | ≥ 0.90 | ≥ 0.80 |
| top-5 overlap | **0.920** | ≥ 0.90 | ≥ 0.80 |
| mean ΔNLL | −0.025 | ≤ 0.05 | ≤ 0.15 |
| full-vocab KL(bf16‖fp32), mean / p99 | 0.0217 / 0.393 | — | — |

The classification is **`reject`**. Script 2 (`qwen-next-port-upstream-scripts/noise_floor_fp32ref.py`) takes fp32 as the reference instead and gives the same picture: mean 0.0199, median 0.0005, p99 0.370, top-1 0.979.

**The noise runs both ways.**
- fp32 has *higher* NLL than bf16 on 8 of 12 prompts.
- Overall fp32 is better (1.884 vs 1.909) only because of `long_context_qsa` (−0.159) and `derivative` (−0.043).
- So neither chain is "the truth" for quality: the floor is irreducible precision noise.

**An MLX bf16 build adds its own, independent bf16 noise.** Canonical bound (f) puts MLX bf16 at 1.0-1.07× the reference's distance from fp32. So even with zero quantization error, expect KL(bf16 ref ‖ MLX maxfit) ≈ 2× the floor, about 0.04 mean.

**Agentic text is where precision bites.**
- `tool_weather` (tool schema + tool-call format, 438 positions) has mean projected KL 0.079. Prose prompts sit at about 0.004-0.008.
- `tool_weather` holds 22 of the 53 top-1 disagreements.
- The worst positions are inside the JSON schema and the tool-call format. At position 62 (`{"city": {"` → `type`), bf16 gives `type` 0.986 and fp32 gives `description` 1.000.

This is one prompt, so treat it as a hint, not a result. But ALIGN's workload is tool-call text, so quantization quality should be judged on agent content.

**What to do (lead ruling, blind, before any variant is scored):**
- Re-register the POLICY relative to the floor, the way bound (f) is already defined:
  - score each variant against the **fp32** chain;
  - admit when the mean and p99 projected KL are each ≤ r × the official bf16 chain's own value against fp32, with r around 2 (MLX bf16 noise ≈ 1×, quantization ≤ 1×);
  - top-1 ≥ the floor minus a small margin;
  - ΔNLL against fp32 ≤ the bf16 reference's ΔNLL + 0.05;
  - report prose and agentic prompts separately.
- This needs an fp32 top-64 capture. `load_gold` reads only `bf16:` keys, so it is a small code change or a separate capture.
- **Preserve the L3 work folder now.** It is 4.7 GB, it lives in `/private/tmp`, and it is the only copy of the full-vocabulary fp32 and bf16 logits (a2's folder has already vanished). Copy it to `jw-wt/` or the SSD.
- The same arithmetic weakens Gate S S3's bf16-comparison bars (top-1 ≥ 0.95, top-k overlap ≥ 0.85 against a bf16 reference). Re-register them in the same ruling.

#### 3. Done and validated, versus not

**Done (laptop):**
- two blind ports and their differential;
- the canonical module `f4ec75d1…`: 31 tests, fp32 ≤ 9.8e-6 over 11 scenarios, greedy 32/32, bf16 1.00-1.07× noise, maxfit/maxfit5 under bound (f);
- real-weight L2/L3/embed/head/PLE-shard parity, 13/13;
- the L3 bf16+fp32 48-layer reference chain on 12 real prompts (records `ade3bf7f5`);
- the mlx-vlm audit (D1 HIGH, F1, P5);
- the D1 upstream kit (`port/qwen4-exp-mlx:docs/align/upstream_mlxvlm_d1/`);
- port r2 (compiled decode, bitwise-equal to eager over 64 steps; maxfit4), with no speed measured yet.

**Not done:**
- download and conversion of the real checkpoint;
- S1 memory at 40,960;
- real decode and prefill speed;
- quality on the real model;
- paging telemetry;
- 48-layer MLX parity (GOAL 5/11);
- any real-weight test of sparse attention;
- F15 Gate-S reader (does not exist);
- frozen Gate S bars (Amendment 3 is still a draft);
- Ed's `/code-review ultra 675`;
- every upstream post.

The GOAL.md status log stops at 2026-11-05 17:00Z; everything from 11-06 lives only in lane documents.

#### 4. Against our methodology: what is new for the 128 GB Mac

##### 4.1 Memory, disk and speed (corrected)

Assumptions:
- Affine group-64 storage costs bits/8 + 1/16 bytes per parameter.
- Routed experts are 120.8 B parameters; everything else is 4.91 B.
- The n-gram table is 320 M rows × 160.
- Non-weight peak at 40,960 tokens is 4.7 GB (112.7 − 108.0).
- Physical memory is 137.4e9 bytes; the 10 % free floor leaves 123.7 GB for everything, macOS included.
- The Metal working set is ≈115.4 GB.

| Build | Metal resident / peak | Table | Physical total | Artifact | Internal disk need (+82.9) | Decode GB/token | Decode est. |
|---|---:|---|---:|---:|---:|---:|---:|
| 8-bit experts | 138.2 / 142.9 | — | — | — | — | — | does not fit |
| **maxfit** (6-bit) | 108.0 / **112.7** | bf16 on disk, cache ≤ 21.5 | 112.7 + cache | 210.4 | 293.3 | 10.74 | 16-24 |
| maxfit5 | 92.9 / 97.6 | bf16 on disk | 97.6 + cache | 195.3 | 278.2 | 10.43 | 16-25 |
| maxfit4 | 77.8 / 82.5 | bf16 on disk | 82.5 + cache | 180.2 | 263.1 | 10.13 | 17-25 |
| maxfit-ple8 (draft) | 108.0 / 112.7 | q8 g80 on disk | 112.7 + cache | 161.8 | 244.7 | ≈10.7 | 16-24 |
| **maxfit4 + q4 table in RAM** (new module mode) | 77.8 / 82.5 | q4 g80 / g32 in host RAM | **110.7 / 114.5** | 106.0 / 109.8 | 188.8 / 192.7 | ≈10.1 | 17-25 |
| E5: 8-bit core + 6-bit experts | ≈103.4 / ≈108.1 | bf16 on disk | ≈108 + cache | ≈205.8 | ≈288.7 | ≈6.3-6.8 | 25-33 (guess) |

What follows from the table:
- **Expert bits move memory a lot and speed hardly at all.** The bf16 core sets both the speed and the heavy thermal class.
- **E5 does not help disk or memory.** It only helps speed, and only if decode turns out bandwidth-bound.
- **maxfit5 is the honest production profile** if maxfit fails the ≥ 1.0 GB S1 margin. It is ≈3 % slower.
- **The in-RAM q4 build** is the only recipe with zero window I/O, and the only one that fits internal disk after deleting the dropped models plus a modest census. But:
  - its physical footprint is maxfit-class;
  - it needs a new module sha: tiny parity, a new profile and a new Gate S;
  - it puts the table at 4-bit, against Ed's "as close to full fp16".

  Measure it against the re-registered POLICY before arguing about it.
- **Speed basis.**
  - Bandwidth floor: 10.74 GB ÷ 300 GB/s = 35.8 ms.
  - Plus GPU launch gaps of 4-8 ms (perf.md).
  - Plus host work that no longer overlaps, about 5-15 ms: Python graph build for about 4,100 dispatches, the numpy hash, and a 16-row gather.
  - Community runtimes at equal bits differ 2-3× (llama.cpp #30074 cites mlx-serve at 53.9 tok/s at 252K on an M5 Max), so overhead matters.
  - Prefill is compute-bound at about 300-450 tok/s before n-gram I/O (guess), and about 180-270 with today's serial I/O.
  - Gate S's 200 tok/s prefill screen is a coin flip on USB4. It is only a screen there; it binds in R0-FN-b.

##### 4.2 Does paging make energy unreliable?

Both seats agree, and I agree:
- **`mmap` paging is a state effect** and must never be used in windows. Residency depends on everything that ran before.
- **`pread` with `F_NOCACHE` from the internal disk is a work effect.** The I/O is a function of the token sequence. It is acceptable if:
  - the module and I/O mode are frozen across all FN members;
  - the table sits on the internal Data volume, with Spotlight and Time Machine excluded;
  - the R1-FN ABBA measures its size (cold `pread` vs pre-touched `mmap`), printed per turn as a work component.
- **Add seat 2's two arms:**
  - P1 vs P4, to catch SSD-controller DRAM or APFS-metadata caching hiding beneath `F_NOCACHE`;
  - a parallel-`pread` arm.
- **Scale.**
  - Decode: about 16 random 4 KiB reads per token, a few ms of latency, under 1 % device power.
  - Prefill: up to 8,192 reads per 512-token chunk. This is where F16 plus async prefetch is needed.
- The latency cost lands in GPU idle-in-turn time. It is real, constant across replays, and must be reported.
- The USB4 SN7100 is DRAM-less with no HMB over USB4, so Sunday's paging numbers characterize the port only, not production.
- The PLE ABBA is a publishable methods contribution. I found no published energy measurement of disk-paged parameters for on-device LLM inference (not an exhaustive search).

##### 4.3 Other method-level items

- **One module rebind before any FN energy data.** Module v2 should hold:
  - port r2 (compiled decode, maxfit4);
  - F16 batched `pread` plus an async prefill prefetcher;
  - a batched `madvise` replacing the 4,096-row cutoff;
  - optionally the in-RAM q4 table mode.

  Any rebind after FN-Q breaks comparability.
- **Template implicit closes (HF 812d96e1).**
  - Our pin `de4b8e4d` is still valid. But the official parse spec says reasoning can close implicitly at `<tool_call>`.
  - If ALIGN re-renders history through the template, it inserts a `</think>` the model never produced. The DeltaNet state cannot be trimmed, so the whole context must be re-prefilled, with full-context n-gram reads.
  - So either F3 (parser) and B2 (round-trip bar) accept implicit closes, or the runtime appends the generated tokens verbatim.
- **bf16 router ties and determinism.** Ties are real (8 of 54 rows at L2 in the official model). U3 replays must keep the same chunking and dispatch thresholds. R0-FN-a should also test determinism across a process restart.
- **Weight-load file cache.** `mx.load` without `F_NOCACHE` may leave file pages that trip the 10 % floor at maxfit. This is plausible but unverified; check `vm_stat` after load.

#### 5. What we can get done

**Constraints:**
- the SSD arrives Sunday 11-08 at the earliest, possibly Tuesday;
- ALIGN comes first;
- R1 arms after R0 re-run 8 passes, with a window up to 56,207 s, and the SSD stays unplugged throughout;
- FN probes and the 6.8 h SSD qualification cannot share a day;
- the magistrate owns MBP timing.

##### Plan A (SSD Sunday)

| When | Who | Step | MBP h |
|---|---|---|---:|
| Sat night | lead (Air) | 1) Integration lane = sat-kit `bb921a127` + quality-ref `92042869a`; resolve `qwen4exp_mbp_report.py`; open a PR for CI. 2) Freeze the Gate S bars in a dated note and evaluate them by hand (F15 is missing; building it is not proportionate). 3) **Re-register the POLICY and S3's bf16 bars against the floor (§2), blind.** 4) Capture an fp32 top-64 reference; move the L3 work folder out of `/private/tmp`. 5) F14 tokenizer check (5.12.1 vs 5.22.1); implicit-close check for F3/B2. | 0 |
| Sun, about 30 min | Ed (Air) | Plug the SSD into the **Air**. Inspect it read-only. Add or rename an APFS volume `JW-EXT` (erase only with the lender's consent). Turn Spotlight off and run `caffeinate`. Start `download`. | 0 |
| Sun → Mon, unattended | Air | download (about 3 h at 33 MB/s) → `convert --profile maxfit` (1-4 h, resumable on `bb921a127`) → `shasum -c` → `convert --profile maxfit5` if ≥ 800 GB was free at the start. Record each PIN off-artifact. Optionally score each artifact's tiny/live checks natively on the Air. | 0 |
| Mon or Tue, by day, magistrate's slot | Ed + MBP | Offload baseline first if run A is still wanted (SSD never on the MBP before it) → plug in → step-0 checks → `memory` maxfit (then maxfit5 if needed) → `quality` → quant-quality `score` under the re-registered rule → `performance` at 512 (and 2048 if memory allows) → `paging` → optionally clone the artifact with the r2 module and re-run `performance` at 512 → evidence copy, eject, census, unplug. | ≈ 4-8 |
| Tue 11-10 | lead | Gate S by hand. GOAL 6/7/8 entries. Live `df` for E1. Choose the profile (expect maxfit5) and the scope of module v2. | 0 |

**Plan B (SSD Tuesday):** by Tue 11-10 only the download and conversion are done; the probes run Wednesday.

##### Within a week (to about 11-14)

- **Module v2 (§4.3).** Sol builds, Opus reviews, Fable cold-passes; tiny parity runs natively on the Air; existing artifacts get a manifest-rewrite clone.
- **L4 reference on the laptop.** One or two prompts of 4-6K tokens, fp32 and bf16, ALIGN-style tool transcripts. This is the first real-weight check of sparse attention above 2,052 tokens, and a long-context fidelity reference.
- **E1 disk.** Then the internal copy, then R0-FN-b by day, then R1-FN including the ABBA. FN-Q is probably beyond this week.
- **Upstream:** D1 issue + PR (Ed); the #1788 comment (Ed).
- **48-layer MLX parity.**
  - It needs a Mac day of its own, or the Air with the SSD-held snapshot.
  - The stream driver has no local-checkpoint flag, and whether it can reuse the HF cache is unverified (a 15-minute code check).
  - It does not gate FN-Q, but it is the strongest answer to `await verification`.

##### Not achievable this week

- a rented bf16 host (no longer needed);
- P10 expert-streaming reference runs;
- any upstream merge.

#### 6. Upstream

##### Ranking (value × chance of landing ÷ Ed-hours)

1. **mlx-vlm D1 fix.** The kit is complete. The bug has been reachable since #2056 (2026-08-27), affecting every release v0.7.0rc0-v0.7.12. Issue first, PR within a day. About 2-4 Ed-hours.
2. **mlx-lm #1788 coordination comment** offering our verification assets: a torch-free tiny official-layout test pinned to transformers 5.22.1, the real-weight per-layer parity method and numbers, and the design notes. About 3 Ed-hours plus reading the module.
3. **llama.cpp converter `indexed_attention`.** Issue first, with a reproducible case and a test that fails before the fix. Confirm what ratio 0 does at runtime before claiming dense attention.
4. **mlx-vlm bf16/q8 n-gram store + `F_NOCACHE` parallel `pread` + an experts-only quant predicate** (the max-fidelity recipe). Only after the Mac data; `ple_storage.py` today accepts only `(4,32,affine)` and `(4,16,nvfp4)`.
5. **A full mlx-lm qwen4_exp PR.** A 2-4 week job:
   - port to mlx-lm main (mlx ≥ 0.32.3);
   - reuse `normalize_qk` and #2027;
   - add BatchGenerator support, which our module deliberately refuses;
   - Ed reads all of it line by line.

   Only after the #1788 outcome.
6. **Publishing our reference:** downgraded. The community already publishes KL, and our bf16 reference sits 0.02 KL from fp32. If we publish anything, publish the fp32 chain plus the noise-floor method.
7. **transformers:** nothing to file; #49923 covered our finding.

##### AI-use policies (verified today)

| Repo | AI code | AI-written text | Other binding rules |
|---|---|---|---|
| mlx-lm | allowed, disclosed, 100 % responsible | **prohibited** (bug reports, PR descriptions, discussions, replies) | new-model PR template is mandatory |
| llama.cpp | allowed, disclosed; be ready to explain every line | **prohibited**, including commit messages | undisclosed AI → permanent ban; no automated commits or PRs; agents must not push or open PRs; bug-fix PRs need an issue plus a test that fails before the fix; verbose AI-sounding replies are badly received |
| mlx-vlm | no rule in CONTRIBUTING | no rule | norm is a one-line disclosure, an "AI Slop" label exists, issue first |

Ed writes every word, every commit message, and does every push himself, in all three repos.

##### Fact sheet A: mlx-vlm D1 (facts for Ed to write from, not text to paste)

- **Where.** `Neywa-Labs/mlx-vlm` (formerly Blaizzy), `mlx_vlm/models/qwen4_exp/language.py`. Blob `9a9bee24`, unchanged since 2026-10-13; identical in `5cdc659b` and PyPI 0.7.12.
- **Trigger.** A batch cache where any row is left-padded and the visible context is ≥ 2,052 tokens (budget 2048 + ratio 4).
- **Path A.** `Qwen4ExpAttention.__call__` returns `super().__call__` for the string mask `"left_padded_decode"`, which drops `selection`.
- **Path B.** The batch-invariant `_qsa_attention` merges the QSA mask only into `None`, `"causal"` or array masks, and routes padded calls of length > 1 to the dense helper. Ragged verify of exactly 2 tokens was already correct.
- **Why unpadded rows break too.** The string mode is chosen per batch, not per row.
- **Impact.** Tiny fp32 logits off by 0.06-0.19. Through BatchGenerator, 5/7 and 6/7 greedy agreement. Exposed in `mlx_vlm.server` continuous batching and in `batch_generate` with mixed lengths.
- **Fix.** One file, 3 hunks, +11/−16: treat `"left_padded_decode"` like `"causal"` (`indexer.build_mask(selection)`, masked SDPA); send padded calls down the masked path.
- **After the fix.** fp32 ≤ 7.7e-7, 7/7 tokens. Single requests and equal-length batches are bitwise unchanged. A mutation test shows each hunk guards its own path.
- **Environment.** M4, macOS 15.7.9, Python 3.13.18, mlx 0.32.4.
- **History to cite.** #2032 documented dense decode as intentional. #2056 made the indexer padding-aware, which removed the stated reason, but kept the dense path. #2126 carried it forward.
- **Separate second issue (F1).** `config.py` rejects `indexed_attention`, which transformers ≥ #48974 writes on save.
- **Ed must** re-run `repro_minimal.py` on current main in a fresh venv and be able to explain `build_mask`'s offsets.
- **Disclosure facts.** The audit, patch and test were produced with AI assistance (Opus 5.5, plus an independent AI reviewer); Ed reproduced and reviewed them.

##### Fact sheet B: mlx-lm #1788 comment (talking points)

- **State.** Open; head `2097324`; +1390 lines across 2 files; 23 comments, 0 inline review comments; label `await verification`; last activity 2026-10-04 (mukhanov's oMLX layouts).
- **What we can offer.**
  - a tiny official-layout test pinned to transformers 5.22.1 (every layer type, sparse selection active, no near-ties);
  - real-weight per-layer parity: fp32 rel ≤ 5.8e-6; bf16 1.00-1.06× the official error; expert sets identical modulo exact bf16 router ties;
  - the regeneration script.
- **Design questions** (questions, not demands):
  - standard caches only (`ArraysCache`, `CacheList(KVCache, KVCache)`), so `load_prompt_cache` and `--kv-bits` stay safe;
  - the raw-`conv1d` fold discriminator (#1623);
  - the group-size trap: g64 silently leaves the 160-wide table in bf16;
  - `indexed_attention` remap for re-saved checkpoints;
  - parity tests must compare modulo ties.
- **Constraints to state.** We do not run community branch code, so we offer tests, not results on their branch. No performance numbers without scripts.

#### 7. Risks and go/no-go

##### Risks, ranked

1. **The quality gate fails for reasons unrelated to quantization (§2).** Mitigation: blind re-registration tonight.
2. **Internal disk (E1)** blocks any FN energy data.
3. **maxfit's 2.7 GB predicted margin** fails S1 → maxfit5.
4. **Serial prefill n-gram I/O** fails the 15 % bar → module v2.
5. **Decode is overhead-bound** at about 16-24 tok/s; heavy class; P5 missed.
6. **No real-weight sparse-attention coverage**; GOAL 5/11 open.
7. **Kit fragmentation and the missing F15.**
8. **Template implicit closes** in ALIGN parsing and cache reuse.
9. **Upstream policy breaches** (llama.cpp bans; mlx-lm social enforcement).
10. **Borrowed-SSD logistics.** Its 2 TB is shared with the offload copy; it must keep the source and artifact until an internal copy verifies.
11. **Volatile `/private/tmp`** holds the L3 logits and the Air's port venvs.

##### GO to R0-FN-b only if all hold

- S0 identity;
- S1 on the chosen profile (zero swap, normal pressure, ≥ 1.0 GB margin at 40,960, prediction within ±10 %);
- the **re-registered** fidelity rule passes;
- the quality item floors pass, including XML round trips with implicit closes;
- decode ≥ 15 tok/s at 16K (screen);
- native tests green;
- a live `df` path for artifact + 82.9 GB.

##### NO-GO or defer if any holds

- maxfit5 also fails S1;
- the fidelity rule fails on the admitted profile;
- there is no internal-disk path (then Sunday's evidence stands as port validation only);
- prefill gather stays > 15 % even with v2;
- determinism fails.

##### Upstream GO

- **D1:** as soon as Ed has reproduced it and can explain each hunk; no dependency on the Mac.
- **#1788 comment:** after Ed has read the test file and the parity report.
- **Full mlx-lm PR:** only after the coordination outcome, `/code-review ultra 675`, an approved mlx-lm-main venv, and ideally the 48-layer gold.

#### 8. Dropped or unverified

- **Seat 1's figures:** the q4 table size, all-resident peak and "converter-only" claim (corrected); E5 memory (corrected); the Saturday SSD timeline (superseded).
- **Seat 2's figures:** "~60 quants, none publishes KL" (corrected); "~30 open llama.cpp items" (≈57).
- **Community decode figures for M4/M5 Max and M3 Ultra** from search snippets: not opened, not used. I used only mlx-vlm #2045 and the llama.cpp #30074 title.
- **Seat claims I could not check:**
  - "maintainers asked for batching on #819" (#819 is "Add LongCat Flash Lite", closed; the comment itself is unread);
  - mlx-vlm `--expert-cache-gb`;
  - #2027 being reusable for QSA;
  - the yomie4343 bf16 SSD build (not re-opened).
- **Open questions:**
  - the runtime effect of llama.cpp ratio 0;
  - whether the gold-stream driver can reuse a local snapshot;
  - whether `mx.quantize` output is bitwise-identical across M4 and M3 Max. This does not matter for S0, because the pin is recorded from whatever artifact is produced.
- **Single-prompt evidence:** the agentic-sensitivity observation in §2 rests on one prompt.

#### 9. Sources

**GitHub API (GET only):**
- mlx-lm: #1788 and its comments, CONTRIBUTING, #2027, #1896 (files + `gated_delta.py`), #1845, releases, `models/` listing.
- Neywa-Labs/mlx-vlm: `qwen4_exp/` contents and blob shas, commits on that path, `language.py@5cdc659b` sha, `ple_storage.py`, `config.py`, #2045, CONTRIBUTING, issue searches, releases.
- llama.cpp: #27742, `conversion/qwen4exp.py`, CONTRIBUTING, AGENTS.md, #29932, #30074, searches.
- transformers: #49923, #49840, #48974, tag comparisons, `configuration_qwen4_exp.py@v5.22.1`.

**Hugging Face API:**
- `Qwen/Qwen3.8-Flash-Next`: commits; `chat_template.jinja` and `tokenizer_config.json` at `de4b8e4d` and `812d96e1`; `tokenizer.json@de4b8e4d`.
- The MLX model search (287 repos); top-40 card scan.
- nace-ai/Qwen3.8-Flash-Next-MLX-4bit card (WebFetch); the gostar77 Radiance card.

**Repo:**
- `port/qwen4-exp-mlx` (GOAL.md, D1 kit);
- `lane/2026-11-06-qwen4exp-quality-ref` (module, `quant_quality.md`, `mbp_live.md`, `canonical.md`, `gold_parity.md`, provenance, scorer);
- `lane/2026-11-06-sat-kit-integrated` (kit, converter);
- `lane/2026-11-07-qwen4exp-mbp-live` `97d780d59`;
- `lane/2026-11-06-qwen4exp-port-r2` (module, MISSING-11 report);
- `lane/2026-11-05-qwen4exp-port-perf` (`perf.md`);
- `lane/2026-11-06-align-flashnext-cell-draft` (Amendment 3);
- `lane/2026-11-06-handoff-v4-port-state` (operator card);
- `records/2026-11-07-qwen4-l3-reference-top64`;
- main RUN_STATE 197-202.

**Local, read-only:**
- `/private/tmp/jwgold-run-l3/work/parity/head` (fp32 and bf16 head logits);
- `/private/tmp/jwsol/venv-*` package versions.

### Research ideas for the 128 GB Mac (from the synthesis)

No novelty checks were run on these ideas beyond what each seat and the synthesis state in the text above.

#### Idea 1. Fidelity-energy frontier scored against the precision floor, on agentic text

- **Claim.**
  - Score each recipe (maxfit, maxfit5, maxfit4, maxfit-ple8, maxfit4 + q4 table in RAM) against the fp32 chain, as a ratio to the official bf16 chain's own distance from fp32. This is the bound-(f) idea applied to quality.
  - Pair each recipe with J/token. That gives the first noise-floor-honest fidelity-vs-energy frontier for an agentic MoE on unified memory.
  - On tool-call text, precision effects look about 10× larger than on prose (one-prompt hint). So prose-only community KL numbers understate the cost for agent workloads.
- **Design sketch.**
  1. Capture an fp32 top-64 reference from `/private/tmp/jwgold-run-l3/work`, and persist that folder.
  2. Add an L4 set on the laptop: 2-4 ALIGN-style tool transcripts of 4-6K tokens, fp32 + bf16. This also covers sparse attention.
  3. Score every variant (converted on the Air) on the MBP by day, reporting prose and agentic prompts separately.
  4. Take energy from R0-FN-b for the admitted variant, and from the bytes regression (idea 4) for the others.
- **Why our rig.** We hold fp32 and bf16 48-layer reference chains on real text for a 360 GB model, built by streaming on a 24 GB laptop. We also have a recipe-exact converter and calibrated energy on the same 128 GB Mac. No community card reports fidelity against a measured precision floor, or energy at all.
- **Cost.** 0 Mac nights. Laptop hours for the captures and L4; about 1 MBP daytime slot to score 2-3 variants.

#### Idea 2. Measured energy of SSD-resident parameters (n-gram ABBA plus device-cache and parallel arms)

- **Claim.**
  - With `pread` and `F_NOCACHE`, n-gram table I/O is a function of the tokens, not of cache history. A cold-`pread` vs pre-touched-`mmap` ABBA on identical tokens sizes its energy as a work component.
  - A P1-vs-P4 contrast tests whether SSD-controller or APFS-metadata caching hides state beneath `F_NOCACHE`.
  - This would be the first published energy measurement of disk-paged weights for on-device LLM inference that I could find.
- **Design sketch.**
  - Amendment 3 R1-FN item 3: P = cold `pread`; W = `mmap` with the episode's rows pre-touched before the stamp.
  - Add an arm P' (parallel `pread` from module v2) and an explicit P1-vs-P4 contrast.
  - Per-turn counters: lookups, unique rows, preads, bytes, gather seconds, `ru_inblock`, internal-disk iostat.
  - Report the delta in GPU, gross and residual energy and in latency, with 90 % t intervals against the U3 bar.
  - Production stays `pread`.
- **Why our rig.** Rails plus the meter resolve the residual, where SSD and CPU energy land. Identical-token replay, the internal-disk census rules and per-turn telemetry already exist in the draft protocol.
- **Cost.** 0 Mac nights. It fits inside the 2-2.5 h R1-FN daytime session, plus about 1 h.

#### Idea 3. Joules of pure software overhead from bitwise-identical variants

- **Claim.**
  - Port r2's compiled decode is bitwise-equal to eager over 64 steps, and serial vs parallel `pread` changes only I/O timing. So ABBA pairs isolate the energy of dispatch, host sync and I/O latency, with token-identical outputs.
  - Our module syncs to the host every token, so this share is probably large. It also bears on what J/token measures in any runtime comparison.
- **Design sketch.**
  - Replay one FN development-episode token log on internal disk in two ABBAs: eager vs compiled decode, and serial vs parallel `pread`.
  - Both come from one module-v2 artifact via config switches (`compile_decode`, `pread` mode).
  - Same seeds, gates and holds. Assert token identity per arm.
  - Report the delta in turn-owned GPU, gross and residual energy and latency against the U3 bar.
- **Why our rig.** The whole-machine meter plus rail sampler, the identical-work pair method, module/manifest pins, and variants already verified bitwise-equal on the tiny fixture.
- **Cost.** 0 Mac nights. About 1 h added to R1-FN, or about 3 quiet daytime hours.

#### Idea 4. J per byte of weight traffic from synthetic full-depth Flash-Next, to decide E5 before converting

- **Claim.**
  - Decode bytes per token are known exactly per recipe: 10.74 / 10.43 / 10.13 GB for maxfit / maxfit5 / maxfit4, about 6.5 GB with an 8-bit core, about 4 GB at uniform 4-bit.
  - Regressing measured J/token on GB/token separates the per-byte DRAM energy from a fixed per-token overhead.
  - That tells us whether an 8-bit core (E5) would buy speed and energy, or mostly hit the host-sync floor.
- **Design sketch.**
  - `qwen4_exp_kernel_bench --suite model` with real per-layer dims and in-memory synthetic weights.
  - Grid: other-bits {16, 8, 6, 4} × expert-bits {6, 5, 4}; contexts 1K and 8K; 64-token decode; 3 repeats; powermetrics plus the meter.
  - Fit E = a + b × GB. Check the slope against one real maxfit point.
  - Caveat: random weights toggle bits differently from real ones.
- **Why our rig.** An exact byte model, the synthetic full-depth bench (MISSING-1), and calibrated whole-machine plus rail energy. It needs no SSD and no download.
- **Cost.** 0 Mac nights. About 0.5 quiet MBP day.

#### Idea 5. Sparse attention keeps decode energy flat as context grows

- **Claim.**
  - Each sparse-attention layer attends to at most about 2,051 keys, and DeltaNet state is constant-size.
  - So Flash-Next decode J/token should be nearly flat from 8K to 40K tokens, while the D cell's full-attention layers grow with context.
  - That would be a clean architectural energy result for the ALIGN paper.
- **Design sketch.**
  - Fixed prompts filled to 1K, 4K, 8K, 16K, 32K and 40,960 tokens; 256-token seeded decode.
  - 3 repeats per cell, for FN (admitted profile) and for D.
  - Report J/token and tok/s per context with the rail split, using the existing performance-probe plumbing plus energy capture.
  - Record the sparse-attention dispatch thresholds as fixed config.
- **Why our rig.** Both models run on one instrumented machine and desk. FN can run from internal disk only after E1; until then any SSD run is a screen.
- **Cost.** 0 Mac nights. About 0.5 daytime per model.

#### Idea 6. Energy per accepted token with the native MTP head (later)

- **Claim.** Flash-Next ships one MTP layer. Speculative decoding changes the work per emitted token, so J per accepted token with MTP on vs off, on identical prompts and weights, is a clean new cell. The community reports only tok/s.
- **Design sketch.**
  - After FN is admitted: extract the MTP head with our converter (new module path and pin) and add a verify forward.
  - Run identical-work pairs per effort. Report J per accepted token and acceptance rate.
  - MTP stays off for every ALIGN comparison.
- **Why our rig.** Same weights, same machine, batch 1, and measured energy instead of tok/s.
- **Cost.** 1 window plus a daytime R0 for the drafter path, after this series.

---

## Appendix: seat reports, verbatim

Both seat reports are reproduced as written. Only their heading levels were shifted down so they nest under this appendix. Where they disagree with the synthesized report, the synthesis (§1 and §8) records the verdict.

### Appendix A. Seat 1 (Fable 5.1)

### Qwen-Next (qwen4_exp / Qwen3.8-Flash-Next) MLX port: what is achievable, what it does to our methodology, and the upstream path

Fable 5.1 seat, 2026-11-07 (Saturday). Independent of the other seat. Everything below was read from the repo lanes named in the brief and from live GitHub/Hugging Face APIs today; nothing was executed, no weights were loaded, no community code was run, nothing was posted, no restricted path was opened. Items I could not open are marked UNVERIFIED.

#### 0. Bottom line

1. **The port itself is essentially done and well validated at every level short of the full checkpoint.** Canonical module `f4ec75d1…` (PR #675): fp32 gold parity ≤ 9.8e-6 on 11 scenarios, greedy 32/32, bf16 within 0.7–1.07× the reference's own noise, real-weight layer parity L2/L3/embed/head/PLE-shard ADMIT 13/13, 31 regression tests, two independent implementations converged, Sol-vs-twin differential at float noise. mlx-vlm was audited numerically against it (single-request path faithful; one real HIGH defect found in mlx-vlm, not in ours).
2. **What is NOT done is everything that needs the Mac + SSD:** download/convert of the real checkpoint, the no-swap memory gate at 40,960 tokens, real decode/prefill speed, the quality score of the 6-bit build against the bf16 reference, and the full 48-layer streamed gold. GOAL.md's status log stops at 2026-11-05 17:00Z; the 11-06 work (L3 ruling, quant-quality harness, port r2, Saturday kit integration, bf16 top-64 reference) lives only in lane docs.
3. **Set against our methodology, the single most important fact is not memory but disk and the paging confound.** The maxfit recipe needs ≈293 GB of *internal* disk (210 GB artifact + 83 GB window headroom) against ≈66 GB free; no currently authorized reclaim reaches it (Amendment 3 §6). And the bf16 PLE paged by `mmap` is a *state* effect that threatens U3/U4; the draft ruling (`pread`+`F_NOCACHE`, ABBA measured, printed as a work component) is sound. A new option falls out of the numbers: **a fully resident `maxfit4 + q4-PLE` build (≈108 GB peak, ≈103 GB on disk) removes the I/O confound entirely and fits the internal disk after the two dropped models are deleted**, at a precision cost Ed has not been asked about. Measure both on the SSD day.
4. **By Tuesday 11-10** (Ed at the Mac Sat/Sun by day): converted maxfit artifact with pinned manifest, memory gate verdict, quality screens, benchmark, performance medians, paging telemetry, and the bf16 comparison closed *without renting a host* by scoring against the L3 top-64 reference captured on 11-06 (records branch). **Within a week:** Gate S verdict, E1 disk ruling, internal copy, R0-FN-a/b, R1-FN (the PLE ABBA), and an Addendum FN draft ready for its cold gate. The 48-layer gold on the Mac is possible in the same week only if it is given a Mac day of its own.
5. **Upstream:** the highest-value, lowest-friction contribution is the **mlx-vlm ragged-QSA fix (D1)**: a complete kit exists (repro, 3-hunk diff, test, evidence), mlx-vlm has no AI-text rule, and the bug is still unfixed on main today (no `qwen4_exp` commit since 2026-10-13). For **mlx-lm**, the right move is a coordination comment on the stalled #1788 (last activity 2026-10-04, label `await verification`) offering our verification assets, not a competing PR; mlx-lm and llama.cpp both forbid AI-written posts and require full line-by-line understanding, so Ed writes every word. Fact sheets for both are in §6.

---

#### 1. External state today (2026-11-07), all opened unless marked

| Item | State today | Source |
|---|---|---|
| **mlx-lm PR #1788** (eauchs, text-only port) | Still **open, unmerged**, head `2097324` (2026-09-26), 9 commits, 2 files (+1201 model, +189 tests), 23 comments, last activity **2026-10-04** (mukhanov's oMLX-layout report). Verification output in the PR body was generated with the `Vontra` 4-bit quant on an M3 Ultra; 8-bit g64 "~600k tokens at 17–21 tok/s". Unresolved threads: R12 prefill-vs-stepwise 1.07e-3 on one setup (author and one tester cannot reproduce), oMLX layouts, `--kv-bits` dropping the indexer. No newer qwen4_exp PR in mlx-lm. | gh api pulls/1788, issue comments, search |
| mlx-lm policy | CONTRIBUTING (live today): "AI-generated code is allowed… must explicitly disclose… **strictly prohibited to use AI to write your posts** (bug reports, feature requests, PR descriptions, discussions, responding to humans)". New-model PR template mandatory. Latest release v0.32.2 (2026-10-16); main needs mlx ≥ 0.32.3 (per upstream.md, 11-05). | gh api contents/CONTRIBUTING.md, releases |
| mlx-lm issue #1845 (updated **today** 17:50Z) | `ArraysCache.advance()` still leaks one Metal buffer per SSM layer per token through `BatchGenerator` after #1632. Our canonical round-1 finding S2 is the same class and is fixed in our module (host-derived `left_padding`). | gh api issues/1845 |
| **mlx-vlm** (now `Neywa-Labs/mlx-vlm`) | `models/qwen4_exp/` with `language.py`, `qsa_kernel.py`, **`ple_storage.py`** ("row-addressable storage for PLE weights… maps safetensors byte ranges and materializes only the rows selected for the current token", Q4 g32 affine and nvfp4 layouts only, LRU, lookup stats). Latest release v0.7.12 (2026-11-04). **No commit on the qwen4_exp path since 2026-10-13**, so the D1 ragged-QSA defect our 11-05 audit confirmed on `5cdc659b` is still on main. README documents text/image/video, MTP speculative decoding via `split_mtp`, 3-bit g32 conversion recipe. Open qwen4_exp issues: #2581 (DFlash drafter defects), PR #2630. | gh api contents, commits, search |
| mlx-vlm policy | CONTRIBUTING has **no AI clause**; no PR template, no issue template, no `AGENTS.md` (404 today). Norm from merged PRs: one-line "AI assistance:" disclosure; maintainers use an "AI Slop" label and prefer issue-first (fact sheet §11, 11-05). | gh api contents; FACT_SHEET.md |
| **llama.cpp** | PR #27742 (danielhanchen) **merged 2026-08-27**, 28 files, +2881. Active follow-ups: #29932 the 51.2B `per_layer_token_embd` is **CPU-pinned and needs ≈50.7 GiB host RAM at Q8**; #30032 QSA indexer O(n_kv × ubatch) OOM; #30074 Metal decode depth-decay on M5 Max (free-form 26.9 t/s at 175K; the same issue quotes mlx-serve 5-bit at 53.9 t/s at 252K on that M5 Max); #30368, #29811 MTP bugs. | gh api pulls/27742, search, issues |
| llama.cpp policy | CONTRIBUTING + AGENTS.md: AI code allowed; **undisclosed AI use may result in a permanent ban**; must disclose manner of use; comment on an existing PR instead of duplicating; "a proper code review usually takes one hour per 200–400 LOC and you should spend at least that much"; "verbose, AI-sounding responses will not be well-received"; AI-written posts prohibited. | gh api contents |
| **transformers** | v5.22.2 released 2026-11-06 (3 commits over 5.22.1, none Qwen4). **#49840 "Fix Qwen4-Exp indexer position cache lifecycle" (merged 10-22) IS in 5.22.1** (our pin). **#49923 "Fix Qwen4-Exp eager attention NaNs with left padding" (merged 11-03) is NOT in 5.22.1 or 5.22.2**, only on main. That is exactly our upstream.md open issue 3 (two reference copies differ in eager float-mask handling; `finfo.min` double-add gives NaN on padded rows and leaks into DeltaNet). Our parity used sdpa and no padding, so our pins are unaffected; the bug is now confirmed upstream. | gh api compare, pulls |
| **Hugging Face, official** | `Qwen/Qwen3.8-Flash-Next` repo sha `812d96e1…` (card touched 2026-11-07 04:42Z; our pinned weights revision `de4b8e4d…` is immutable). 3.6M downloads. `Qwen/Qwen3.8-Flash-Next-FP8` exists. | HF API |
| HF community MLX quants (opened: API list + 3 cards) | `mlx-community/Qwen3.8-Flash-Next-4bit` (2026-09-02, mlx-vlm post-#2032, g32 "required so the PLE dimensions can be quantized"), `-4bit-mtp`; TensorFold 2/3/4/6/8-bit MTP packs; Jundot oQ2.5–oQ6e; pipenetwork mixed 4/8 and 4-bit (2026-08-26); `yomie4343/…-mixed-3-4-8bit-BF16-SSDNgram`: a **bf16 102.4 GB `ngram_table.bin` read from SSD** with a patched Sushi engine on an M3 Ultra 96 GB, i.e. the "bf16 table on SSD" idea has community precedent, but on a non-mlx-lm engine. **No published build matches our recipe (6-bit experts, bf16 everything else, bf16 table).** | HF API, model cards |
| Community M3 Max 128 GB decode numbers | None found. Search snippets (UNVERIFIED, not opened): M4 Max ≈60 tok/s 4-bit, 78 with MTP; M5 Max ≈30 tok/s without MTP, 44–60 with; M3 Ultra 25.7 tok/s at ≈103 GB active for a heavier pack. | WebSearch only |

---

#### 2. Done and validated vs not (as of 2026-11-07 morning)

| GOAL item | Status | Evidence |
|---|---|---|
| 1 Two independent ports | **Done.** Sol (PR #664) and Opus twin (PR #673), blind. | GOAL log 11-05 |
| 2 Gold parity on tiny configs | **Done** on canonical: fp32 ≤ 9.8e-6, bf16 ≤ 1.07× noise, prefill = stepwise = chunked, padded = batch-1, snapshot/trim bitwise, maxfit/maxfit5/maxfit4 under bound (f). | canonical.md, PR #675 |
| 3 Differential | **Done**, float noise in fp32; D0–D10 resolved against the reference. | differential docs |
| 4 Canonical module via `model_file`, pinned sha | **Done**: `f4ec75d1…` (Saturday pin). Port r2 (`c3d4a0bf…`, compiled decode + maxfit4) exists and is explicitly **not** adopted until Saturday's results are recorded. | port_r2_adoption.md |
| 5 Real-weight layer parity | **Partial**: L2, L3, embed/head, PLE shard ADMIT 13/13 on the laptop (PR #669, 11-05). Full 48-layer streamed parity (PR #680, native tests 51/51, run "pid 3097" on the M4 Air): **no result document found in any lane**; I treat it as not established. | gold_parity.md, PR #680 |
| 6 Memory fit, no swap | **Not run.** Model-predicted only: 112.7 GB peak at 40,960 (maxfit), 97.6 (maxfit5). | mbp_live.md |
| 7 Real-model validation | **Not run.** Harness ready (PR #671, kit PR #683 CI-only). bf16 reference host: none; **replaced by the L3 top-64 reference** (records branch, 12 prompts, 48-layer reference chain fp32+bf16, finished 11-06 23:4x PST, `reference-top64.npz` sha `6c9dcb7c…`). | records README, quant_quality.md |
| 8 Performance | **Not run on the Mac.** M4-extrapolated targets 30 tok/s decode, 400/550 prefill were for an 8-bit-core recipe; Amendment 3 re-costs maxfit at ≈10.8 GB/token → 20–25 tok/s (guess). | perf.md §6-7, amend3 §2 |
| 9 Review | Adversarial rounds + Fable cold pass done (18 findings fixed); **Ed's `/code-review ultra 675` not yet run** (freebie to name). | GOAL log |
| 10 Upstream package | mlx-lm-style tests (18), readiness checklist, fact sheet exist (PR #672); mlx-vlm D1 kit complete (port branch). **Nothing posted.** | upstream.md, FACT_SHEET.md |
| 11 Gold on the MBP | **Not started**; depends on today's SSD. | SAT card |
| P10 expert streaming | Implemented, off by default, refused for energy windows. | expert_streaming.md |
| Saturday kit software | MISSING-1 synthetic artifact, -3 triage, -5 resumable convert, feasibility: merged into `lane/2026-11-06-sat-kit-integrated` (`bb921a127`). **F15 Gate-S reader (`qwen4exp_gate_s.py`) not found on that branch**: the Gate S verdict will be manual against Amendment 3 §1 unless it landed elsewhere. | branch listing |

---

#### 3. Set against our methodology: what is new or interesting for use of the 128 GB Mac

**3.1 Disk, not memory, is the binding constraint, and there is a recipe that dissolves it.** Amendment 3 §6: maxfit needs ≈293 GB free internal (artifact 210.4 + headroom 82.9), maxfit5 ≈278; today ≈66 GB; deleting the two dropped models → ≈180; plus pilots 8–10 after the block-5 release → ≈258; still 35/20 GB short. The draft offers `maxfit-ple4` (136 GB artifact, needs 219) as option (d). Going one step further than the draft: **`maxfit4 + q4-PLE`** (4-bit g64 experts, bf16 core, 4-bit g32 table) is ≈77.8 GB resident weights + ≈25.6 GB table ≈ **103 GB on disk** and, if the table is loaded resident, ≈**108 GB peak at 40,960** (82.5 + 25.6; 7 GB under the 115.4 GB ceiling). Internal-disk need ≈186 GB: fits after deleting the dropped models (+pilots 8–10 for margin). It is the only configuration that is *all-resident*: **no disk I/O inside a window at all**, so §5's confound vanishes and U3/U4 are untouched. Costs: experts at 4-bit (our tiny-fixture bound ratio 1.28 stepwise before the MISSING-12 gate change; community standard) and the 51B table at 4-bit (community standard via mlx-vlm g32; quality impact **unmeasured**). This is a precision-vs-measurement-purity decision for Ed (it cuts against "as close to full fp16 as I can get"), but it should be *measured*, not argued: the L3 top-64 reference and `run_qwen4_quant_quality.py score` exist precisely to put a KL/NLL number on each variant. Note that the module already supports q4 `NgramTable` records; a converter profile (not a module change) would be needed, and the table would have to be loaded resident rather than mmap'd to realize the zero-I/O property (a `model_config` choice, to verify).

**3.2 The PLE I/O ABBA is a genuine methodological contribution.** Measuring the energy of a disk-paged embedding as a work component (cold `pread` vs pre-touched `mmap` on identical tokens, Δ with 90 % t-interval against the U3 bar) is, as far as I can find, not something any lab has published for on-device LLMs. It generalizes to every paged-weight scheme (mlx-vlm's `ple_storage.py`, llama.cpp's CPU-pinned table, expert offload). Worth a paragraph in the ALIGN paper regardless of FN's admission.

**3.3 The class flips to heavy because the core is bf16.** Decode bytes/token ≈ 8.42 GB dense core + 1.92 experts(6-bit) + 0.44 other = 10.8 GB; expert bits barely matter (5-bit 10.5, 4-bit 10.2). Only quantizing the *core* moves speed (8-bit core ≈ 6.3–6.8 GB/token, ≈1.6×). So the S2 floors (15/12 tok/s) and B_F ≥ 8,192 hinge on the bf16-core choice, and the thermal class (planning turn 190–240 s vs 0.6·t_decline ≈ 100–120 s) follows. If Saturday decode lands at ≤ 15 tok/s, the honest options are screen-only or an 8-bit-core artifact with a new Gate S (E5), not a maxfit5 swap.

**3.4 The reference moved under us, in our favour.** transformers main fixed the left-padding eager NaN (#49923) we had documented as "two reference copies differ"; 5.22.1 already carries the indexer position-cache fix (#49840). Record in GOAL that our gold authority (5.22.1, sdpa, no padding) is unaffected and that any future left-padded parity must use ≥ the #49923 commit.

**3.5 "PLE paging upstream" is less novel than the GOAL assumed.** mlx-vlm already pages the quantized table from safetensors byte ranges with an LRU and lookup stats; llama.cpp keeps the table in host memory. Our delta is bf16 rows, `pread`/`F_NOCACHE` determinism, per-turn I/O telemetry, and the measured energy cost. That reframes the upstream value (see §6).

**3.6 The Saturday SSD is not the production I/O path.** SN7100 is DRAM-less; a USB4 bridge gives it no HMB, so random-read latency is worse than internal. Saturday's paging numbers characterize the port, not production (Amendment 3 §5.4). Do not let a slow cold pass on JW-EXT drive a recipe change.

**3.7 MTP is an energy-research angle, not a measurement option.** The checkpoint ships one MTP layer; mlx-vlm and community packs use it for speculative decoding (claims +30–78 % tok/s, UNVERIFIED). For ALIGN comparability it must stay off (it changes work per token). But "energy per accepted token with/without MTP on the same weights" is a clean later cell on this machine.

**3.8 The batch-decode leak class is live upstream today** (#1845). Our module already derives `left_padding` on the host and ties QSA cache writes with `mx.depends`; R0-FN-a item 4 (40,960-token decode, ≤ 2 GB growth per 10k tokens) is the right guard and should be kept.

---

#### 4. What is achievable, and the plan

Today is Saturday 11-07; the SSD is borrowed, by day only, never attached in a window. Ed's presence is the critical resource; the lead/Air cannot run MLX at scale.

##### By Tuesday 2026-11-10 (realistic, all daytime, Mac + SSD)

| When | Who | Step | Output |
|---|---|---|---|
| Sat S1–S9 | Ed | Operator card as written: quiet Mac, bus baseline **before** plugging the SSD, APFS `JW-EXT`, Spotlight/TM exclusions, kit checkout `97d780d59`, venv pins, dry runs, 3 native test modules (32/37+1 skip/13). | green native checks |
| Sat S10 | Ed | `download --validation-only` (360 GB; 3–5 h at 33 MB/s; Ethernet if < 15 MB/s). While it runs: kernel bench at real dims and `memory --synthetic`/`performance --synthetic` (MISSING-1) for provisional fit/speed. | `download.json` |
| Sat S12–S13 (only if ≥ 5 h remain) | Ed | `convert --profile maxfit` (1–4 h, 211 GB; cannot resume; MISSING-9 resumable convert is on the integrated kit branch, not on `97d780d59`), `shasum -c`, record PIN off-artifact; `memory` 4k→16k→40,960. | PIN, memory verdict |
| Sun | Ed | `quality`, `benchmark` (no `--reference`), `performance --prefill-step 512` then `2048`, `paging` two passes; **then `run_qwen4_quant_quality.py score --reference reference-top64.npz`** from the records branch against the maxfit manifest: this closes B12/MISSING-6 under the L3 POLICY (projected KL ≤ 0.020, p99 ≤ 0.10, top-1 ≥ 0.90, top-5 ≥ 0.90, ΔNLL ≤ 0.05). If memory failed on maxfit: maxfit5 convert + rerun (needs ≥ 225 GB free on JW-EXT). Optional if time: a second small artifact for the q4-PLE question (§3.1) and score it too. | `quality.json`, `performance-*.json`, `paging.json`, quant-quality JSON |
| Sun evening | Ed | §7 evidence copy to internal, `EVIDENCE.SHA256SUMS`, eject, ejected census must REFUSE, unplug, unplugged census PASS. | evidence bundle |
| Mon | Lead (Air) | H1 evidence review (GOAL 6/7/8), Gate S S0–S5 verdict (manual if F15 absent), GOAL log entries, Deviation log, name `/code-review ultra 675` for Ed. Laptop F14 tokenizer equivalence 5.12.1 vs 5.22.1. | ADMIT-CANDIDATE / NOT ADMITTED / INCOMPLETE |
| Tue | Ed + lead | E1 disk ruling with a live `df`; E5/E6 if triggered; decide whether to add the all-resident recipe to the Gate S re-registration. R0-FN-a (template, coherence, effort ladder, determinism) can run from JW-EXT by day. | rulings; R0-FN-a |

##### Within a week (to ~11-14)

- Internal copy of the admitted artifact (after E1), manifest-verified; SSD ejected; **R0-FN-b** (production memory with `pread`, binding S2, PLE gather ≤ 15 % of prefill or build F16 batched `pread`).
- **R1-FN** (2–2.5 h quiet daytime, interactive agent, no window): step test → class; two gated runs; **PLE ABBA**; fill B_F, I_F, T_dead, N_chunk.
- F1–F11 build list (runtime subclass through `load_verified_model`, XML family, `prefill_step_size`, hybrid-cache rebuild, telemetry, kit/desk/R0/R1 scripts, census refusal of off-volume files): Sol builds, Opus reviews, Fable cold-passes F1/F3/F5/F6. This is the long pole; ≈ 30 h of Sol time in the draft's estimates.
- Addendum FN text (F12) ready for its registration cold gate; FN-Q window no earlier than the week after.
- **48-layer gold on the Mac (GOAL 11):** feasible only if given its own Mac day with the source still on JW-EXT (`--shared-shards retain` is affordable there; the reference is CPU torch per layer at real dims, serial, hours). It does not gate FN-Q under the L3 ruling, but it is what makes the upstream "human-expert verification" claim complete. Schedule it, do not let it slip silently.

Not achievable this week: a rented bf16 vLLM host comparison (not needed under L3), P10 expert-streaming reference runs, upstream merges of anything.

---

#### 5. Memory fit, speed, and whether paging makes energy unreliable

All decimal GB; 40,960-token context, batch 1, full-precision KV, from the port's memory model (prediction accuracy is itself a Saturday gate at ±10 %).

| Build (experts / everything else / PLE) | Artifact on disk | Resident weights | Predicted Metal peak | Headroom to 115.4 | Decode GB/token | Decode est. @230–300 GB/s eff. | Fits? |
|---|---:|---:|---:|---:|---:|---:|---|
| 8-bit / bf16 / bf16 paged | — | — | 142.9 | − | — | — | **No** |
| **6-bit (maxfit)** / bf16 / bf16 paged | 210.4 | 108.0 | **112.7** | 2.7 | 10.8 | **21–28 tok/s** | Yes, thin margin; page cache ≤ 21.5 GB rides beside it |
| 5-bit (maxfit5) / bf16 / bf16 paged | 195.3 | 92.9 | 97.6 | 17.8 | 10.5 | 22–29 | Yes |
| 4-bit (maxfit4) / bf16 / bf16 paged | ≈180.2 | ≈77.8 | ≈82.5 | ≈32.9 | 10.2 | 23–29 | Yes |
| 4-bit / bf16 / **q4 g32 resident** | ≈103.4 | ≈103.4 | ≈108.1 | ≈7.3 | ≈10.2 | 23–29 | Yes, **no paging** |
| 6-bit / **8-bit core** / bf16 paged (E5 option) | ≈ 162 (guess) | ≈ 60 (guess) | ≈ 65 (guess) | large | ≈ 6.5 | 35–48 | Yes |

Reading: expert bits move memory a lot and speed almost not at all; the bf16 core sets both the speed (bandwidth-bound) and the heavy class. Prefill is compute-bound (MoE `gather_qmm` ≈ 59 % of a chunk at M4 scale); the 400/550 tok/s targets came from an 8-bit-core recipe and Gate S only asks 200 at 4,096. My expectation for maxfit on an unloaded M3 Max is 300–450 tok/s at chunk 512 (guess; bf16 GEMMs are not slower than 8-bit qmm at M = 512). Record misses, do not tune the recipe to win.

Does paging make energy measurement unreliable? **Not inherently, under four conditions, all already in the draft ruling:** (1) the table on the *internal* volume (census refuses otherwise); (2) `pread` on `F_NOCACHE`, so I/O is a deterministic function of the token sequence (work), not of page-cache history (state); (3) the I/O cost *measured* by the R1-FN ABBA and printed per turn (lookups, unique rows, preads, bytes, gather seconds, `iostat` delta), never modelled into the frozen design; (4) `mmap`, `purge`, pre-touch never inside a window. Scale: ≈ 64 KiB/token before dedupe, ≈ 1.3 MB/s and ≈ 320 IOPS at 20 tok/s in decode; device power well under 1 % of a ≈ 40 W turn; the larger effect is latency (serial `pread`, ≈ 1–1.6 ms/token ≈ 3 %, more in prefill, hence the ≤ 15 % bar and F16). The energy lands outside the GPU rail (SSD + CPU fault handling in the residual) and reaches the GPU only through idle-in-turn time. What *would* make it unreliable: `mmap` in production (state), the table on an external bus (census-forbidden anyway), or an irreproducible Δ in the ABBA. If Δ is reproducible but large, it is disclosed as a work component, not fatal. The all-resident `maxfit4 + q4-PLE` build is the way to make the question moot if Ed accepts its precision.

---

#### 6. Upstream: the most valuable contribution, where, under which rules, and the fact sheet

##### 6.1 Ranking (value × probability of landing × Ed-hours)

1. **mlx-vlm: ragged-batch QSA selection discarded (D1).** HIGH for batched serving (every row in a batch with any left-padded row, including the unpadded row, attends densely past 2,052 visible tokens; silent; divergence compounds), none for single requests. Kit on `port/qwen4-exp-mlx` under `docs/align/upstream_mlxvlm_d1/`: `repro_minimal.py` (exit 1 = bug), `fix.diff` (one file, 3 hunks, +11/−16, applies to `5cdc659b` = PyPI 0.7.12), `test_qwen4_exp_ragged_qsa.py`, independent second-reviewer mutation check, bitwise non-regression on single/equal-length batches. **Still unfixed on main today.** No AI-text rule in mlx-vlm; issue-first then PR within a day; signed commit; one-line disclosure. Ed-hours ≈ 2–3. Probability of merge: good (outside fixes merged by lucasnewman in 1–12 days).
2. **mlx-lm: a coordination comment on #1788 offering verification assets** (the torch-free pinned-reference test on a tiny official-layout checkpoint with every layer type and QSA active; the real-weight parity method and numbers; the `CacheList(KVCache, KVCache)` design that keeps `load_prompt_cache` and `--kv-bits` safe; the #1623-style raw-`conv1d` fold discriminator). This addresses the `await verification` label, which is what has stalled the PR for ten weeks. One open PR per first-time contributor; main needs mlx ≥ 0.32.3 (a third venv Ed must approve). Ed-hours ≈ 3 plus reading our module. If no response in ~2 weeks, a separate PR with Ed's go and the real-weight evidence attached (then Ed must be able to defend ≈ 2,000 lines unaided).
3. **transformers:** nothing to file now; #49923 covered our finding. Possible later note on `topk` zero-score tie non-determinism in the QSA indexer (affects any reference comparison), low priority.
4. **ml-explore/mlx:** the 0.31.2 `mx.fast.rope` bug (B > 1, T = 1, scalar offset → rows ≥ 1 get position 0) if it still reproduces on 0.32.x (UNVERIFIED), a small Ed-written issue with a 10-line repro.
5. **Max-fidelity recipe as an HF upload** (6-bit experts, bf16 core, bf16 table): license permits with notice (Qwen Community 1.0; no MaaS); but our artifact format v2 loads only through our module, so it is useful to others only after the mlx-lm module lands. Defer.
6. **PLE paging to mlx-vlm:** they already have `ple_storage.py`; our bf16/`pread` variant is a niche extension. Defer unless the ABBA shows something maintainers would care about.

##### 6.2 AI-policy constraints (verified today)

- **mlx-lm**: AI code allowed with disclosure; **no AI-written posts of any kind**; "100 % responsible for every line"; new-model template mandatory (starts with the "I understand it is strictly prohibited…" checkbox). Enforced socially; a contributor reports a shadow-ban after AI contributions (#1821 thread, 11-05).
- **llama.cpp**: same prohibition; undisclosed AI → possible permanent ban; ≥ 1 h review per 200–400 LOC expected; comment on an existing PR instead of duplicating; terse, human replies.
- **mlx-vlm**: no written rule; visible norm is a one-line disclosure; "AI Slop" label exists; issue-first.
- Consequence for us: §6.3 are **facts for Ed to write from**, never text to paste; Ed must have read the diff/module he submits; the disclosure must say what agents did (two blind ports, review loops, tests) and what Ed did (ran, reviewed, decided).

##### 6.3 Fact sheets

**A. mlx-vlm issue + PR (D1)**
- Target: `Neywa-Labs/mlx-vlm` main; files `mlx_vlm/models/qwen4_exp/language.py` (+ test in `mlx_vlm/tests/test_cache.py`, already in a CI group).
- Symptom: with any left-padded row in a batch, `Qwen4ExpAttention.__call__` returns `super().__call__` for the string mask `"left_padded_decode"` (path A), and `Qwen4ExpBatchInvariantForward._qsa_attention` routes padded calls to `_attention`, which sets `mask=None` and runs the dense ragged helper (path B); the computed `selection`/`qsa_mask` is discarded. Affects one-token ragged decode (A and B) and ragged verify of ≥ 3 tokens (B); 2-token verify already correct.
- Reference: transformers 5.22.1 `modeling_qwen4_exp.py` `:711-754`, `:847-852`: selection mask always combined with the causal/padding mask; per-row block boundaries.
- Fix: treat `"left_padded_decode"` like `None`/`"causal"` (`mask = indexer.build_mask(selection)`, `dispatch_qsa_attention(causal=False)` → masked SDPA); route only unpadded ≥ 3-token calls to `_attention`; replace the string by the QSA mask in the lower path. 3 hunks, +11/−16.
- Evidence (kit `evidence/`): reproducer before exit 1 / after exit 0; ragged rows match single requests to ≤ 5e-7 after the fix (verify blocks 2, 3, 4; one-row padded cache); bitwise non-regression on single/equal-length; mutation test shows each hunk guards its path; fp32 ≤ 1.0e-6 vs transformers on tie-free tiny configs; env Apple M4, macOS 15.7.9, Python 3.13.18, mlx 0.32.4, mlx-vlm 0.7.12.
- History: dense ragged decode was once documented as intentional (#2032); #2126 text reads as "ragged stays dense"; a test removed in #2276 had shown padded-row mask = single-row mask.
- Also found, mention or not: F1 (checkpoints re-saved by transformers 5.22.1 refuse to load: `indexed_attention` layer type), P5 (left-padded batch scored without a cache ignores padding).
- Disclosure line facts: analysis, diff and test produced with AI assistance under Ed's direction; Ed ran the reproducer/tests himself [Ed confirms].

**B. mlx-lm #1788 coordination comment**
- Who to thank, by contribution: the author (eauchs), Sofille65 (official checkpoint fixes), beatakouchnir/sje397 (seed 1234 + constant check), Teejer (quant layout), xunlinkx (repro run), mukhanov (oMLX layouts).
- One-line context: a 128 GB M3 Max research rig needs Flash-Next in mlx-lm on a pinned stack.
- What we can hand over toward `await verification`: (1) a torch-free unittest pinning logits from transformers 5.22.1 `Qwen4ExpForCausalLM` on a tiny checkpoint in the official layout (fused experts, `shard_N`, hash buffers, `mtp`/`visual` extras), every layer type, QSA selection active, no near-ties in routing or block scores (pins: transformers 5.22.1, torch 2.15.0, sdpa; reference stepwise = prefill to 1.8e-6); (2) per-layer parity on real bf16 weights (L2 DeltaNet+MoE, L3 QSA+MoE, embed/head, PLE rows: fp32 rel ≤ 5.8e-6, bf16 at 1.00–1.06× the reference's own bf16 error, expert sets identical modulo exact bf16 router ties, which occur on 8/54 rows at L2 in the official model itself); (3) the pin script to regenerate (1).
- Design questions to raise, not demands: standard caches only (`ArraysCache`, `CacheList(KVCache, KVCache)`) so `load_prompt_cache`, `merge` and `--kv-bits` behave; the raw-`conv1d`-layout fold discriminator (#1623) instead of a prefix heuristic (R9); the `quantize_model` group-size trap (default g64 silently leaves the 160-wide table in bf16; either document `--q-group-size 32` or merge predicate dicts before the divisibility check); `qwen4_exp_text` remap for `save_pretrained` text-only checkpoints; QSA relu-zero `topk` ties are implementation-defined in torch, so parity tests must compare modulo ties.
- Constraints to state: we have not run #1788; results on that branch must come from whoever runs it; we will not quote performance without scripts.
- Licensing: our code MIT (Ed), reference Apache-2.0 re-implemented without copied text, no Qwen weights/configs/templates vendored, test checkpoint synthetic.

---

#### 7. Risks and go/no-go

**Saturday/Sunday (Gate S, pre-registered in Amendment 3 §1; do not loosen after seeing data):**
- GO to ADMIT-CANDIDATE: S0 identity; S1 all three rungs with zero new swap, pressure level 1, free ≥ 10 %, compressor ≤ +2 GB, PLE resident ≤ 21.5 GB, Metal peak within ±10 % of prediction with ≥ 1 GB margin; S1b chunk chosen; S3 item floors; S4 native checks; S5 paging recorded; **plus** (my addition under L3) quant-quality POLICY `acceptable` against `reference-top64.npz`. S2 is a screen on USB4; binding only in R0-FN-b.
- NOT ADMITTED: S1 fails on maxfit and maxfit5; or POLICY `reject`/`marginal` on the admitted profile (investigate, never drop bits silently).
- STOP conditions: a floor-only stop is a headroom **fail** (go to maxfit5); PLE-cap stop → stop for the day (pread variant later); shard digest mismatch → stop (no repair path on `97d780d59`); any conversion started within 5 h of a cutoff.

**Risks, ranked**
1. **Disk on the internal volume** (293 GB vs 66) pushes FN past this series; mitigations: E1 (a)+(b)+(c), or the all-resident q4-PLE recipe (§3.1) with a new Gate S.
2. **Memory margin 2.7 GB at maxfit** plus page cache; sidecar and runner add more in production. maxfit5 is the honest fallback; the prediction-accuracy check is what tells us whether the model is trusted.
3. **Speed below S2 on internal disk** (bf16 core): outcome is screen-only or an 8-bit-core artifact with precision disclosure (E5); maxfit5 is not a remedy.
4. **Serial `pread` latency in prefill** > 15 % → F16 batched `pread` = new module sha = tiny parity + Mac quality rerun.
5. **Template/tokenizer surprises** (`reasoning_content` handling; 5.12.1 vs 5.22.1 ids): F14 on the laptop now; E6 path (load tokenizer via `tokenizers` in align code).
6. **Operational**: conversion not resumable on the Saturday pin; SSD format/name unknown until plugged; R1 Saturday-night cutoff; borrowed SSD must leave with the source and artifact still on it until an internal copy verifies (E2).
7. **Upstream**: policy violations are reputational and permanent (llama.cpp bans; mlx-lm social enforcement); a competing mlx-lm PR as a first contribution reads badly; one-open-PR limit; main-branch venv not yet approved.
8. **Reference drift**: future transformers releases include #49923; any new parity with padding must pin ≥ that commit and re-record the authority sha.

**Go/no-go for upstream posts:** GO for the mlx-vlm issue+PR as soon as Ed has read `fix.diff` and run `repro_minimal.py` himself (no dependency on Saturday). GO for the #1788 comment once Ed has read the test file and the real-weight parity report and can answer questions on them; the full-module PR only after (a) coordination outcome, (b) Ed's `/code-review ultra 675`, (c) an approved mlx-lm-main venv, (d) ideally the 48-layer gold, which is the strongest answer to `await verification`.

---

#### 8. Sources opened today
- GitHub API (read-only): ml-explore/mlx-lm PR #1788 and its comments/files, issues #1845, CONTRIBUTING.md, releases; Neywa-Labs/mlx-vlm `models/qwen4_exp/` contents, `README.md`, `ple_storage.py`, commits, CONTRIBUTING.md, releases, issues #2041 and search; ggml-org/llama.cpp PR #27742, issues #30074, #29932, CONTRIBUTING.md, AGENTS.md, search; huggingface/transformers PRs #49840, #49923, #50138, tags v5.22.0/1/2 and compare/containment.
- Hugging Face API: model search (all and `filter=mlx`), `Qwen/Qwen3.8-Flash-Next`, cards of `mlx-community/Qwen3.8-Flash-Next-4bit`, `TensorFold/…-6bit-MTP`, `yomie4343/…-BF16-SSDNgram`.
- Repo (mpmdw/JouleWise, fetched): `docs/align/qwen4_exp_port/{GOAL,mbp_live,canonical,quant_quality,gold_parity,perf,expert_streaming,upstream,port_r2_adoption,audit_mlx_vlm_numerical}.md`, `docs/align/upstream_mlxvlm_d1/FACT_SHEET.md`, `docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-3-DRAFT.md`, `docs/handoff/2026-11-06-v4-and-port/SATURDAY-OPERATOR-CARD.md`, run reports 2026-11-05 gold-parity / gold-stream / mbp-live-preparation, 2026-11-06 quant-quality and synthetic-artifact, `records/qwen4/2026-11-07-l3-reference-top64/`, PRs #664–#683 metadata, RUN_STATE.md items 170–187, CANONICAL.md.
- UNVERIFIED (search snippets only): community decode figures for M4 Max / M5 Max / M3 Ultra (ddalcu/mlx-serve releases, besthub article, llmcheck estimates, rapid-mlx card).

### Appendix B. Seat 2 (Opus 5.5)

### Qwen3.8-Flash-Next (qwen4_exp) MLX port: what can be done on the 128 GB Mac, and what can go upstream

Opus seat, research track. Written 2026-11-07, evening PST.

**How I worked**
- Branches read with `git show` and one temporary worktree under `jw-wt/`, which has been removed.
- External state was read with `gh api` (GET requests only), the Hugging Face API, and WebFetch/WebSearch. Every external source cited below was opened unless it is marked UNVERIFIED.
- I did not touch the MBP, ran no MLX, loaded no weights and executed no community code.
- No blinded path was read: no `/Users/edr/jw-b5-*`, `night-*` or `restricted/`.
- Nothing was committed or posted.

---

#### 0. Summary

1. **The port is correct on everything the laptop could reach. The 128 GB Mac has measured nothing yet.** These are done and validated:
   - two independent ports, and a differential between them;
   - the canonical module (`f4ec75d1…`), with tiny-config gold parity: fp32 ≤ 9.8e-6, bf16 ≤ 1.07× the reference's own noise;
   - real-weight parity on layers 2 and 3, embed/head and a PLE shard (13/13 pass);
   - a 48-layer bf16 **quality reference** (L3, top-64, 12 prompts).

   Memory fit, end-to-end quality, speed and paging on the M3 Max are all predictions. I found **no recorded result** of the full 48-layer MLX-versus-reference parity pass (GOAL 5/11). Its work directory is gone, and no branch carries a summary for it.
2. **Decode will probably be limited by software overhead, not by memory bandwidth.**
   - Python-MLX builds of this model in the community decode at about 19-27 tok/s even on Ultra-class chips, at 3-6 bits.
   - mlx-serve, a Zig implementation, reports about 60 tok/s on an M4 Max at 4-bit.
   - Our module adds a host sync on every token: the n-gram rows need the token ids on the CPU. That sync defeats MLX's overlap between consecutive tokens.
   - My estimate for maxfit on the M3 Max is **15-22 tok/s**. Gate S's decode floors (15 tok/s at 16k, 12 at 40,960) probably pass. The P5 target of 30 tok/s probably does not.
3. **Prefill PLE I/O is the larger risk.**
   - mlx-vlm PR #2045 measured 9.68 s of cold PLE lookups inside a 4K prefill that ran at 217.8 tok/s. That is about half the prefill time.
   - Our pread path reads rows one at a time. Our mmap path skips its `MADV_WILLNEED` prefetch above 4,096 unique rows, which every 512-token chunk exceeds.
   - So the Gate S prefill floor (200 tok/s at 4,096) is roughly a coin flip on the USB4 SSD. R0-FN-b's "gather ≤ 15 % of prefill" bar will likely fail without F16.
   - In prefill every token id is known in advance, so a background prefetcher with parallel preads can hide almost all of it.
4. **Memory: maxfit is marginal and maxfit5 is the likely production profile.**
   - Predicted Metal peak is 112.7 GB against the 115.4 GB working set, a 2.7 GB margin. Gate S S1 requires ≥ 1.0 GB measured.
   - maxfit5 predicts 97.6 GB (17.8 GB margin) and is only about 3 % slower, because the bf16 core, not the expert bits, sets decode bytes.
5. **Paging only keeps energy data trustworthy in one form.** `mmap` paging makes the I/O depend on page-cache history (state) and must not be used in windows. `pread` with `F_NOCACHE` from the **internal** disk makes the I/O a function of the tokens (work), which the planned R1-FN ABBA can size. Two open questions remain: SSD-controller caching beneath `F_NOCACHE`, and latency stalls charged to GPU idle time. Internal disk (E1) is the binding constraint for any Flash-Next energy data.
6. **The plan can be cut from 7-20 MBP hours to about 4-8.** Plug the SSD into the **M4 Air** first and run download + verify + convert there, overnight and unattended. Nothing in the kit's download or convert path checks the host model, and the converter streams in 32 MiB slices. The MBP then needs only the memory, quality, quant-quality, performance and paging probes, by day.
7. **Upstream, ranked by value per Ed-hour:**
   1. **mlx-vlm D1** (ragged-batch QSA drops the sparse selection). Re-verified today: still on main, file blob `9a9bee24` unchanged, unreported. The kit is ready, and mlx-vlm has no AI-posting ban.
   2. **Publish the L3 bf16 reference + scorer.** About 60 community MLX quants exist and none publishes KL or perplexity. This also answers mlx-lm #1788's `await verification` blocker without CUDA.
   3. **mlx-vlm bf16/q8 external PLE store + parallel pread + an experts-only quant predicate** (the max-fidelity recipe). Today the store accepts 4-bit only, verified.
   4. **llama.cpp converter `indexed_attention` one-liner.** Still present and unreported.
   5. **An mlx-lm qwen4_exp PR,** a 2-4 week job. It needs a port to mlx-lm main and BatchGenerator support, which our module deliberately refuses. Coordinate on #1788 first.

   mlx-lm and llama.cpp both forbid AI-written posts. Ed writes every word.
8. **New today:** the official HF repo changed at 2026-11-07 04:42 UTC (commit `812d96e1`).
   - The chat template now wraps assistant turns in `{% generation %}` tags. Rendered text is unchanged.
   - `tokenizer_config.json` gained a `response_template` parse spec. It says reasoning may be closed **implicitly** by `<tool_call>`, and parameters and tool calls may also close implicitly.
   - Weights, config and `tokenizer.json` are unchanged.
   - Our pin `de4b8e4d` (template sha `c3cf9e34…`) stays valid. The ALIGN XML parser (F3), the "unclosed reasoning" metric and the template round-trip bar (B2) must accept these forms. Otherwise a re-rendered history adds a `</think>` the model never produced, the DeltaNet cache must be rebuilt, and the whole context is re-prefilled with full-context PLE reads.

---

#### 1. Done and validated, versus not

##### Done and validated (laptop: tiny configs or real shards)

| Item | Evidence | Where |
|---|---|---|
| Two independent ports (Sol 6.1, Opus twin), built blind to each other | Sol native gold: fp32 6.0e-8; differential agreed to fp32 noise | `lane/2026-11-05-align-flashnext-port` 28d153449, `-twin` ad56248a5, `differential_sol_vs_twin*.md` |
| Canonical module, mlx-lm house style, `model_file` hook, pinned stack | fp32 ≤ 9.8e-6 over 11 scenarios (padded, chunked, 320- and 4,101-token sparse-kernel prefill); greedy 32/32; bf16 ≤ 1.07× noise; snapshot/restore and prompt-cache round trip bitwise; 31 tests natively; validation round 1 found 18 findings, all fixed with regressions | `canonical.md`, module sha `f4ec75d1…` |
| Real-weight parity, laptop shards | Layers 2/3, embed/head, PLE shard: 13/13 PASS; bf16 1.00-1.06× the official error | GOAL log, PR #669 / #675 |
| Quantized profiles within bound (f) | maxfit 0.49-0.79, maxfit5 0.80-1.06 (bound 1.25); maxfit4 under the per-bit bound | `canonical.md` (f); port r2 |
| bf16 quality reference L3 | 48 layers, fp32+bf16, real inputs, no failures; 12 prompts ≤ 512 tokens; `reference-top64.npz` sha `6c9dcb7c…` | `records/2026-11-07-qwen4-l3-reference-top64` ade3bf7f5 |
| mlx-vlm audit | D1 confirmed (HIGH for batched serving), F1, P5; single-request path faithful (≤ 1e-6 fp32) | `audit_mlx_vlm_{static,numerical}.md`, `upstream_mlxvlm_d1/` |
| Saturday software | Kit + MISSING-1/2/3/4/5a/8/9/10 (`lane/2026-11-06-sat-kit-integrated` bb921a127, module still `f4ec75d1`); quant-quality harness (`lane/2026-11-06-qwen4exp-quality-ref` 92042869a); port r2 = compiled decode + maxfit4 (`c3d4a0bf…`, bitwise-equal to eager on the fixture) | lanes as named |

##### Not done, or not validated

- **GOAL 5/11, the full 48-layer real-weight MLX parity:**
  - no recorded PASS was found;
  - `/private/tmp/jwgold-run-a2` no longer exists, and no branch or RUN_STATE item reports its summary;
  - the only full-depth artifact is reference-chain-only (`full_48_layer_gold: false` in the L3 `gold-summary.json`);
  - the sparse QSA regime (≥ 2,052 visible tokens) has **never** been exercised on real weights.

  The lead should locate the a2 result or treat GOAL 5 as open.
- **GOAL 6, memory fit on the M3 Max:** prediction only (112.7 / 97.6 GB).
- **GOAL 7, end-to-end checks on the real model** (coherence, NLL, XML round trip, quant-quality against L3): not run.
- **GOAL 8, performance:** extrapolated from a loaded M4 Air only.
- **GOAL 9:** Ed's `/code-review ultra` on #675 is not evidenced.
- **GOAL 10:** prep documents only; nothing posted.
- **ALIGN cell (Amendment 3):** still a draft, not adopted.
  - The F1-F16 build list is mostly unbuilt. **The F15 Gate-S reader does not exist on any branch.**
  - I found no record that the Gate S bars were frozen.
- **Kit fragmentation.** The next SSD day needs three lanes that diverged from `97d780d59`:
  - sat-kit-integrated (bb921a127);
  - quality-ref (92042869a), which merges with sat-kit with **one conflict**, in `scripts/qwen4exp_mbp_report.py`;
  - port r2 (c3d4a0bf), used only for a post-test artifact clone.

  The operator card still names `97d780d59`, so the "Saturday commit" is ambiguous.
- **L3 covers short contexts only.** Its prompts are ≤ 512 tokens, so the primary quantization gate never sees sparse attention, the regime every ALIGN turn will run in.

---

#### 2. What is achievable by Tue 11-10, and within a week

**Constraints that bind**
- The SSD arrives Sun 11-08, possibly Tue (RUN_STATE 199/200).
- Ed set ALIGN as the priority.
- MBP nights belong to R0/R1/windows. Flash-Next work on the MBP is daytime only, never overlaps R0, R1, a window or the SSD qualification, and its timing is the magistrate's call (RUN_STATE 197).
- The same SSD is also wanted by offload run A and by the 6.8 h always-attached qualification.

##### Key change: do the download and conversion on the M4 Air

Checked in code:
- `qwen4exp_mbp_live.py download/convert` checks only:
  - `/Volumes/JW-EXT` is APFS and mounted;
  - no `com.joulewise.night*/b6loop/b6wake` agents are loaded (the Air has none; `launchctl list` checked);
  - free space.
- It never checks `hw.model`.
- The converter writes 32 MiB row slices, which suits 24 GB.
- The Air is not a measurement machine, so it can run unattended overnight.
- Plugging the SSD into the Air does not disturb the MBP's offload bus baseline, which only requires that the SSD never touched the MBP before the baseline.

##### Plan A (SSD on Sunday)

| When | Who / where | What | MBP hours |
|---|---|---|---|
| Sat night → Sun AM | lead, Air | (1) Integration lane = sat-kit-integrated + quality-ref (resolve `qwen4exp_mbp_report.py`); open a PR for CI; run the native tiny modules one at a time on the Air (mbp_live 32/0, e2e 37/1, hosted 13/0, canonical, quant_quality, synthetic and pread natives). (2) Freeze the Gate S bars as a short dated note, with S3's bf16 comparison replaced by the L3 POLICY per lead ruling L3. Skip building F15 and evaluate the six bars by hand: proportionate. (3) Write the RUN_STATE kit item for the magistrate. | 0 |
| Sun, ~30 min of Ed | Ed, Air | Plug the SSD into the **Air**. Inspect it read-only; add an APFS volume named JW-EXT (or rename; erase only with the lender's consent); turn off Spotlight; start `download`. | 0 |
| Sun → Mon AM, unattended | Air | `download` (about 3 h at 33 MB/s) → `convert --profile maxfit` (1-4 h) → `shasum -c`. Then `convert --profile maxfit5` as well, if the SSD has ≥ 800 GB free at the start. That takes the fallback conversion off the Mac. Record each PIN off-artifact. | 0 |
| Mon or Tue, by day | Ed + MBP | Offload A1 baseline (SSD unplugged), if run A is still wanted → plug in → step-0 checks → `memory` on maxfit (15-90 min), then maxfit5 if needed (already converted) → `quality` (20-90) → quant-quality `score` against L3 (~30-60) → `performance` at 512 (+2048 if the memory gate allows) (1-4 h) → `paging` (15-45) → optional: clone the artifact with the port r2 module (manifest rewrite only, minutes) and re-run `performance` at 512 to measure the compiled-decode gain on real weights (~1 h) → evidence copy, eject, census, unplug. | ≈ 4-8 |
| Tue 11-10 | lead, Air | Review the evidence: GOAL 6/7/8 entries, Gate S by hand, live `df` for E1. Choose the production profile (expect maxfit5) and the scope of module v2. | 0 |

**Plan B (SSD on Tuesday):** Tuesday → Air overnight; MBP probes Wednesday by day. By Tue 11-10, only the download and conversion are done.

**SSD-day conflict:** Flash-Next probes and the 6.8 h SSD qualification cannot share a day. Neither is on W1's critical path; the ordering is the magistrate's call.

##### Within a week (by about 11-14)

1. **Module v2, one rebind, before any Flash-Next energy data.** Sol builds, Opus reviews, tiny parity runs natively on the Air. It contains:
   - port r2 (compiled decode + maxfit4);
   - F16: parallel/batched `pread`, plus an **asynchronous prefill PLE prefetcher** (prefill ids are known in advance);
   - a batched `madvise` in place of the 4,096-row prefetch cutoff;
   - optionally a `maxfit-ple8` profile (6-bit experts, bf16 core, q8 n-gram, 161.8 GB).

   Module-only changes reach existing artifacts through a manifest-rewrite clone. Any rebind after FN-Q would break comparability.
2. **L4 sparse-regime gold on the laptop.** One or two prompts of about 4-6K tokens:
   - first real-weight check of QSA selection above 2,052 tokens;
   - a long-context quality reference for the quant gate.

   If the SSD sits on the Air holding the 360 GB source, point the harness at that local snapshot instead of restaging about 460 GB over Wi-Fi. The older parity harness takes `--checkpoint <dir>`; whether the stream driver can do the same is UNVERIFIED.
3. **E1, internal disk.** Apply Ed's 11-06 retention ruling (delete pilots 8-10 once the SSD and iCloud copies verify), plus the dropped-model deletion (needs Ed's exception), plus a census. Targets:
   - maxfit5 needs about 278 GB free;
   - maxfit-ple8 about 245 GB;
   - a resident maxfit4 + q4-PLE recipe (≈ 106 GB) about 189 GB.

   Then copy internally, verify, and run R0-FN-b by day.
4. **Upstream:** Ed files mlx-vlm D1 (issue + PR, about 4-6 h of his time); publish the L3 reference + scorer; Ed writes the #1788 coordination comment.
5. **R1-FN** (2-2.5 h by day) only after R0-FN-b and the v2 freeze. FN-Q is likely beyond this week.

---

#### 3. Memory fit and expected speed on 128 GB (bf16 core, n-gram table paged)

Parameter counts come from the real config:
- routed experts 120.8 B (2.52 B per layer);
- everything else 4.91 B (GDN 2.09 B, QSA 0.62 B, hyper-connections 0.64 B, lm_head 0.64 B, embed 0.64 B, shared expert 0.24 B, router 0.06 B);
- n-gram table 51.2 B (102.4 GB bf16).

Each token reads 16 n-gram rows of 320 bytes. Affine group-64 storage costs bits/8 + 1/16 bytes per parameter.

| | maxfit (6-bit) | maxfit5 | maxfit4 (r2) | 8-bit core + 6-bit experts (E5) |
|---|---:|---:|---:|---:|
| Resident weights | 108.0 GB | 92.9 GB | ≈ 77.8 GB | ≈ 103 GB |
| Predicted Metal peak at 40,960 tokens | 112.7 GB | 97.6 GB | ≈ 82.5 (derived) | ≈ 108 |
| Margin to the 115.4 GB working set | **2.7 GB** | 17.8 GB | ≈ 33 GB | ≈ 7 |
| Artifact with bf16 PLE | 210.4 GB | 195.3 GB | ≈ 180 GB | ≈ 205 |
| Decode bytes/token | 10.74 GB | 10.43 | 10.13 | ≈ 6.3-6.8 |
| Bandwidth floor at 300 GB/s effective | 36 ms (28 tok/s) | 35 ms | 34 ms | ≈ 22 ms (45 tok/s) |
| **Expected decode (my estimate)** | **15-22 tok/s** | 15-23 | 16-23 | 25-35 |
| Expected prefill, chunk 512, current serial PLE, USB4 SSD | 200-300 tok/s | ≈ same | ≈ same | ≈ same |
| Same, with parallel/async PLE (v2) | 330-450 tok/s | | | |

**Basis for the speed estimates**
- `perf.md`'s byte table, re-costed for a bf16 core.
- Community measurements (opened):

  | Build | Machine / runtime | Decode |
  |---|---|---|
  | oQ6 (TensorFold) | M3 Studio (by inference M3 Ultra; the card says only "M3 Studio"), oMLX / MLX-VLM | 19.5-23.1 tok/s |
  | oQ3 (Vontra) | same | 26.5 tok/s |
  | Q4 + external PLE | M2 Ultra, mlx-vlm #2045 | 19.0 tok/s at 21.6K; prefill 217.8 tok/s |
  | 4-bit | M4 Max, mlx-serve (Zig) | ≈ 60 tok/s |

  Equal bits giving a 2-3× spread across runtimes means decode is overhead-bound.
- Our per-token host sync (`qwen4_exp.py` `__call__`: "Host sync: the n-gram rows depend on the token ids just fed") stops MLX encoding token t+1 while token t runs.
- Expert bits barely move speed. The bf16 core sets it.

**Memory cautions**
- mlx-vlm's Q4 run peaked 6.8 GB above its resident weights at 21.6K. That is probably its dense-masked fallback, but it shows how fast transients appear next to a 2.7 GB margin.
- Loading 108 GB of weights through `mx.load` (without `F_NOCACHE`) leaves clean file-cache pages. They could trip the kit's `memory_pressure` 10 % floor at maxfit. Check `vm_stat` file-backed pages after load.
- A fully resident alternative exists: maxfit4 + q4 PLE ≈ 106 GB plus about 5 GB of transients. It has no paging at all, removes the disk confound and largely solves E1, at a precision cost. That is Ed's call, and it can be measured against L3.

**Does paging make energy measurement unreliable?**
- **mmap: yes.** I/O depends on residency left by earlier members, the hash pass and other models. That is a state effect hitting U3/U4. It also adds up to 21.5 GB of file pages beside the Metal peak. Never use it in windows.
- **pread + `F_NOCACHE` from the internal disk: acceptable as a work component**, provided that:
  - the module and I/O mode are frozen across all FN members;
  - the table sits on the internal Data volume, with Spotlight and Time Machine excluded;
  - the R1-FN ABBA measures the size.

  **Add two checks to the ABBA:**
  - P1 against P4: whether the SSD controller or filesystem metadata caching beneath `F_NOCACHE` makes replays cheaper;
  - a parallel-pread arm.
- **What remains:** latency stalls land in GPU idle-in-turn time (a real cost, constant across replays), and cache-rewind rebuilds re-read PLE rows for the whole context. Use the module's exact snapshot/restore, or count rebuilds.
- **The USB4 SN7100 paging numbers from the SSD day characterize the port only.** It is DRAM-less, with no HMB over USB4, and runs mmap. They cannot stand in for R0-FN-b.

---

#### 4. Upstream: the most valuable contributions, the AI-policy constraints, fact sheets

##### External state, 2026-11-07 (all opened)

- **mlx-lm #1788:**
  - open and `blocked`, labelled `await verification` since 2026-08-29;
  - head `2097324`; last activity 2026-10-04;
  - 23 comments, 0 inline review comments.
- **mlx-lm main:**
  - v0.32.2 (2026-10-16); no `qwen4_exp.py` in `mlx_lm/models`;
  - `normalize_qk` (fixed in #1896, 2026-09-17) now implements exactly our eps adapter, so the q/k-norm eps fix is already upstream;
  - a fused DSA sparse-prefill kernel was merged 11-05 (#2027) and is reusable for QSA;
  - #1798 (readout scale) was closed as fixed by `normalize_qk`.
- **mlx-vlm** (Neywa-Labs, formerly Blaizzy):
  - v0.7.12 (11-04); main pushed 11-07;
  - `qwen4_exp/language.py` blob `9a9bee24`, unchanged since 10-13, so **D1 is still present**;
  - `config.py` still rejects `indexed_attention` (F1);
  - the external PLE store (#2045) supports only `(4,32,affine)` and `(4,16,nvfp4)`;
  - there is an `--expert-cache-gb` expert offload;
  - no issue about D1 or F1 exists;
  - CONTRIBUTING has **no AI policy**, and the repo ships `.claude-plugin`/`.codex-plugin`.
- **llama.cpp:**
  - #27742 merged 2026-08-27; its AI-use note says "Used Claude and local models";
  - about 30 open qwen4exp issues and PRs, including Metal decode depth-decay #30074 (M5 Max: 26.9 tok/s free-form at 175K; mlx-serve 53.9 tok/s at 252K), indexer-cache PRs #28699 / #30815, and expert streaming #31469;
  - the converter still writes `ratio if layer_types[i] == "full_attention" else 0` (`conversion/qwen4exp.py:89`), unreported.
- **Hugging Face:** about 60 MLX builds, from 2-bit to 8-bit, REAP-pruned, abliterated, oQ/DWQ and mlx-serve packs, for example:
  - mlx-community 4bit, 111.5 GB;
  - pipenetwork 6bit, 148 GB; 8bit, 192 GB;
  - an SSD-stream pack carrying a 51.2 GB `ngram_table.bin`.

  None of the cards I opened publishes KL or perplexity.
- **Model license:** Qwen Community License 1.0. Permissive, with notice; conditions apply only to very large commercial services and MaaS businesses. Publishing a derived logits reference with the notice looks fine. This is my reading, not legal advice.

##### AI policies

| Repo | AI-written code | AI-written posts | Other binding rules |
|---|---|---|---|
| **mlx-lm** | allowed if disclosed and understood | **prohibited** | the new-model PR template has an "I understand" checkbox and an AI-disclosure line; per `upstream.md` (11-05, not re-opened today) a PR limit of about 1 open PR for Ed |
| **llama.cpp** | allowed, ≥ 1 h of manual review per 200-400 LOC | **prohibited** | undisclosed AI use can mean a permanent ban; check for an existing PR and join it; features start with an issue; bug fixes need a reproducible issue + a regression test that fails before; new contributors 1 open PR, no trivial fixes |
| **mlx-vlm** | no policy | no policy | — |

Ed should still write all mlx-vlm text himself, to be consistent and to build reputation.

##### Ranking

1. **mlx-vlm D1 fix.** Kit ready. About 4-6 h of Ed's time: re-run, understand, write.
2. **A public Flash-Next bf16 reference + scorer** (the L3 top-64 NPZ + `run_qwen4_quant_quality.py score` + an adapter for mlx-vlm).
   - The community quant ecosystem has no fidelity numbers.
   - It gives #1788, mlx-vlm, oMLX, mlx-serve and llama.cpp a CUDA-free verification oracle.
   - It needs no PR slot.
   - Add an L4 long-context set before calling it complete.
3. **mlx-vlm max-fidelity recipe**, after the Mac data:
   - bf16 and q8 record formats in `ple_storage`;
   - an `F_NOCACHE` pread mode with parallel gather;
   - a documented experts-only `quant_predicate`;
   - evidence: our memory, speed and L3 scores.
4. **llama.cpp converter fix:** issue first, then a one-line PR + converter test. Confirm what ratio 0 does at runtime before claiming silent dense attention.
5. **mlx-lm qwen4_exp model PR:**
   - port to main (mlx ≥ 0.32);
   - `normalize_qk`, standard caches, **BatchGenerator support**;
   - tests in `tests/models/test_qwen4_exp.py`;
   - Ed's line-by-line review of about 2,000 LOC.

   About 2-4 weeks. Coordinate on #1788 before competing. Our module refuses BatchGenerator, and maintainers asked for batching on #819.

##### Fact sheet for Ed: mlx-vlm D1 (for him to learn from and write his own issue and PR)

**Where the bug is**
- Repo `Neywa-Labs/mlx-vlm`, file `mlx_vlm/models/qwen4_exp/language.py`, blob `9a9bee24`. Identical on main 2026-11-07 and in PyPI 0.7.12.
- Introduced by #2126 (merged 2026-09-04, d68a25e71). Its parity tests used only equal-length batches.

**Trigger:** a batch cache in which any row is left-padded, and any row's visible context is ≥ 2,052 tokens. That is `indexer_budget + compress_ratio`: 512 complete blocks of 4.

**Mechanism, two paths**
- **Path A**, `Qwen4ExpAttention.__call__`: for any string mask other than `"causal"`, it returns `super().__call__`. That discards `selection`. Qwen3.5's `_qwen3_5_left_padded_attention` never reads its `mask`.
- **Path B**, the batch-invariant `_qsa_attention`: it merges the QSA mask only into `None`, `"causal"` or array masks; `"left_padded_decode"` survives. It also routes `length > 1` padded calls to the same helper. Ragged verify of exactly 2 tokens was already correct.
- **Why the unpadded row is affected too:** the string mode is chosen per batch, not per row.

**Impact**
- Every row diverges from its single-request output.
- Tiny config, fp32: logits off by 0.06-0.19.
- Through `BatchGenerator`: 5/7 and 6/7 greedy tokens agree; max |Δlogprob| 0.061-0.077.
- Exposed: `mlx_vlm.server` continuous batching and `batch_generate` with mixed lengths at long context.

**The fix:** one file, 3 hunks, +11/-16.
1. Path A treats `"left_padded_decode"` like `"causal"`, using `mask = self.indexer.build_mask(selection)` and masked SDPA.
2. Path B sends every padded call to the lower masked path.
3. Path B merges `"left_padded_decode"` like `"causal"`.

`build_mask` already offsets blocks by each row's left padding and excludes pad columns.

**After the fix:** fp32 ≤ 7.7e-7, 7/7 tokens, logprob ≤ 4.1e-7. Single requests and equal-length batches are bitwise unchanged. Cost: one boolean mask per padded step, which path B already built and threw away.

**Test:** proposed home `mlx_vlm/tests/test_cache.py`. A mutation check shows each parametrization guards its own path.

**Verification environment:** M4, macOS 15.7.9, Python 3.13.18, mlx 0.32.4.

**Ed must be able to explain:** the QSA block and tail rule, the `build_mask` offsets, and why a per-batch string mode breaks unpadded rows. He should re-run `repro_minimal.py` himself on current main in a fresh venv.

**Disclosure line, his words:** the audit and the patch were produced with AI assistance (Opus 5.5, plus an independent AI reviewer); he reproduced and reviewed them himself.

**Second PR, separately:** F1. Transformers ≥ #48974 saves `indexed_attention`, which mlx-vlm rejects, and `output_gate_type=None` is rejected after that. The patch is in `scripts/audit_mlxvlm/`.

##### Talking points for a #1788 comment (Ed writes it)

- We have a transformers-5.22.1-pinned tiny-checkpoint test in the official layout, real-weight layer parity, and a 48-layer teacher-forced bf16 top-64 reference. The author or a maintainer can run these to clear `await verification` without CUDA.
- We do not run community branch code (our rule), so we offer tests, not results on their branch.
- Point to R12 (prefill versus stepwise not reproducible across machines), R16 (KV quantization drops indexer state) and R18 (private cache classes) as the design questions.

---

#### 5. Risks and go/no-go

##### Risks, roughly in order

1. maxfit's memory margin (2.7 GB predicted) fails S1 → maxfit5.
2. Serial PLE I/O in prefill puts the Gate S prefill floor and the R0-FN-b 15 % bar at risk → F16 / async prefetch in v2.
3. Decode is overhead-bound at 15-22 tok/s: the P5 target is missed, and the planning turn is heavy.
4. GOAL 5 (48-layer MLX parity) is unrecorded, and the sparse regime is untested on real weights.
5. Three-lane kit integration; the F15 reader is missing; the Gate S freeze is unevidenced.
6. Upstream template and parse spec changed 11-07. Stay pinned, and harden F3 and B2 for implicit closes.
7. Internal disk (E1) blocks any FN energy data.
8. The borrowed SSD's loan length (E2) and the delivery slip.
9. L3 is blind to long-context and sparse-attention quantization effects.
10. A module rebind after FN-Q invalidates comparability, so freeze v2 first.
11. bf16 routing ties on 11-15 % of rows at the released scale. Replays must keep identical chunking and dispatch thresholds, or U3 pairs diverge. R0-FN-a item 5 should also test determinism across a process restart.
12. Weight-load file cache may trip the free-memory floor.
13. AI-policy breaches upstream: account bans in llama.cpp; social shadowbans reported for mlx-lm.

##### GO to R0-FN-b (Flash-Next proceeds as an ALIGN cell candidate) only if

- S0 identity holds.
- S1 holds on the chosen profile: zero swap, normal pressure, ≥ 1.0 GB Metal margin at 40,960.
- The L3 POLICY reads `acceptable`: mean projected KL ≤ 0.020, p99 ≤ 0.100, top-1 ≥ 0.90, top-5 ≥ 0.90, ΔNLL ≤ 0.05.
- The quality screens pass, including XML round trips with the implicit-close forms.
- Decode is ≥ 15 tok/s at 16k (screen).
- The native tests are green.
- E1 has a live `df` path to the artifact + 82.9 GB + journal.

##### NO-GO or defer

- maxfit5 also fails S1 (maxfit4 needs Ed's E10).
- The POLICY reads `marginal` or `reject` on the admitted profile.
- There is no internal-disk path. The SSD-day evidence then stands as port validation only.
- PLE prefill gather stays above 15 % even with v2.
- R0-FN-a determinism fails.

##### Upstream GO

- D1: Ed reproduces it on current main and can explain each hunk.
- mlx-lm PR: only after the #1788 coordination and Ed's full read of the code.
- Never agent-written text.

---

#### Sources (opened unless marked)

**GitHub (read-only `gh api`)**
- mlx-lm: #1788 and its comments; CONTRIBUTING; the new-model PR template; `models/` listing and releases; `gated_delta.py` `normalize_qk` and its commit #1896; issue #1798; PRs #2027, #1997 and #2013.
- mlx-vlm: repo metadata and releases; `qwen4_exp/language.py` sha and history; `config.py`; `ple_storage.py`; CONTRIBUTING and repo contents; PRs #2045 and #2085; issue and PR searches.
- llama.cpp: #27742 body; issue #30074; qwen4exp issue and PR search; CONTRIBUTING; `conversion/qwen4exp.py`.
- mlx-serve (ddalcu): repo metadata and recent releases.

**Hugging Face**
- `Qwen/Qwen3.8-Flash-Next`: model API, commits, file trees at `de4b8e4d` and `812d96e1`, `chat_template.jinja` and `tokenizer_config.json` at both revisions, LICENSE.
- HF model search API, and sizes for six builds.

**Web**
- mlx-serve v26.8.11 release page (WebFetch).
- TensorFold oQ6 and Vontra oQ3 model cards (WebFetch).

**UNVERIFIED (not opened):** llama.cpp `AGENTS.md`; the mlx-serve pre-release figure of about 75 GB; the unsloth docs page; the mlx-lm PR-limit rule (taken from our 11-05 `upstream.md`); typical Apple-SSD random-read latency figures.

**Repo**
- `port/qwen4-exp-mlx` GOAL.md, audits, D1 kit.
- `lane/2026-11-06-qwen4exp-quality-ref`: `canonical.md`, `mbp_live.md`, `quant_quality.md`, `gold_parity.md`, run reports, the module source.
- `lane/2026-11-06-sat-kit-integrated`: kit code and reports.
- `lane/2026-11-06-qwen4exp-port-r2`: adoption and MISSING-11 report.
- `lane/2026-11-05-qwen4exp-port-perf`: `perf.md`.
- `lane/2026-11-05-qwen4exp-port-upstream`: `upstream.md`.
- `lane/2026-11-06-align-flashnext-cell-draft`: Amendment 3 draft.
- `lane/2026-11-06-handoff-v4-port-state`: Saturday operator card.
- `records/2026-11-07-qwen4-l3-reference-top64`.
- main RUN_STATE 197-200, handoff RESUME, CANONICAL.md.
