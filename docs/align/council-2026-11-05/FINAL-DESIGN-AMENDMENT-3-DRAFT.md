# FINAL-DESIGN Amendment 3 (DRAFT, NOT ADOPTED): Qwen3.8-Flash-Next as the second ALIGN production cell

Drafted 2026-11-06 by Opus 5.5 (`claude-opus-5-5`), a workflow seat under the laptop lead. **Status: draft only.** It changes nothing until (1) Saturday's measurements exist, (2) Ed rules on §9, (3) the Opus chair adopts it, and (4) the protocol v4 "Addendum FN" passes its own registration cold gate (Fable + Opus, blind), as Amendment 1 §A4 requires.

It amends `FINAL-DESIGN.md` together with Amendments 1 and 2 (`origin/main` `b963c0242`). Where they conflict, this draft would win once adopted; everything it does not restate stands. Sources read:

| Source | Ref |
|---|---|
| Council design and amendments | `origin/main` `b963c0242` |
| v4 code | `lane/2026-11-05-align-v4-assembled` `fc83cfe1d` |
| Saturday Flash-Next live kit | `lane/2026-11-07-qwen4exp-mbp-live` `6cacb2be5` (`docs/align/qwen4_exp_port/mbp_live.md`, `scripts/qwen4exp_mbp_live.py`, `scripts/qwen4exp_e2e_eval.py`, `scripts/align_convert_qwen4_exp.py`, `joulewise/align/models/qwen4_exp.py`) |
| Offload runbook (PR #665) | `lane/2026-11-05-mbp-offload-runbook` `e6ff35295` (`docs/align/mbp_offload_and_gold_setup.md` §9b) |
| Port memory model and perf | `lane/2026-11-05-align-flashnext-port` `28d153449` (`docs/align/qwen4_exp_port.md`), `lane/2026-11-05-qwen4exp-port-perf` `1aeb9ff88` (`perf.md` §6-7) |
| mlx-lm 0.31.3 loader | installed package source, `mlx_lm/utils.py:325-334` (read only) |

No real weights were loaded, no MLX was run, and nothing under `/Users/edr/jw-b5-*`, `night-*`, `night-custody`, `night-archive` or any `restricted/` path was opened. Numbers marked **(guess)** are planning values that a named measurement replaces.

---

## 0. Bottom line

- **Cell.** FN = `Qwen/Qwen3.8-Flash-Next` @ `de4b8e4d43b917e7706784d8bb445c9af86a3540`, converted by our canonical streaming converter to **maxfit**: 6-bit/g64 routed experts, every other weight bf16, and the 102.4 GB bf16 PLE (n-gram) table on disk. maxfit5 (5-bit experts) is the pre-committed fallback. The module is `joulewise/align/models/qwen4_exp.py`, sha256 `f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37`. Tag `qwen3.8-flash-next`.
- **Stack.** No pin bump. FN runs on **stack A**: mlx 0.31.2, mlx-lm 0.31.3, the same measurement venv as the anchors and D. Amendment 1 §A4's "stack B" assumed mlx-lm #1788 and is **withdrawn**. The module enters through mlx-lm 0.31.3's model-class hook, called by our verified loader (§7).
- **The binding constraint is disk, not memory or the port.** The PLE table has to live on the Mac's **internal** SSD, because the borrowed SN7100 can never be attached during a window. maxfit needs **210.4 GB** of internal disk (maxfit5 195.3 GB), plus 82.9 GB of window headroom. That is **≈ 293 GB free** (maxfit5 ≈ 278 GB), against about **66 GB** today (estimate; all pilots retained). Deleting both dropped models (122B and Next-Instruct) reaches about 180 GB. Adding pilots 8-10 after the block-5 release reaches about 258 GB. **No currently authorized reclaim fits FN.** §6 gives the arithmetic and §9 E1 gives the options. Until E1 is resolved, FN is "admissible on Saturday's evidence, blocked on internal disk".
- **Admission is pre-registered here, before Saturday's data exist** (§1). There are four bars:
  1. no swap at 40,960 tokens;
  2. a decode floor of 15 tok/s at 16k (12 tok/s at 40,960) and a prefill floor of 200 tok/s;
  3. quality against bf16 through the PR #671 harness at the `maxfit` bounds;
  4. native checks green.

  The decode and prefill floors are binding only when re-measured from internal disk (R0-FN-b). Saturday's PLE sits on USB4.
- **Class.** FN is classified by the FINAL-DESIGN §2.5 rule at R1-FN rates. It is **predicted heavy**: its bf16 dense core reads about 10.8 GB per token, so a planning turn is about 190-240 s against 0.6 × t_decline ≈ 100-120 s. This reverses Amendment 1's guess that FN is "likely light". G1 and holds follow the class.
- **Budget and deadman.**
  - B_F is the largest multiple of 1,024 with an R1-FN planning member ≤ 1,800 s, with a floor of **8,192**.
  - If B_F falls below the floor, FN is screen-only. There is no automatic recipe change: speed comes from the bf16 core, and quantizing that core is Ed's precision call (E5).
  - T_dead,F = (1,750 − I_F)/1.13544, which is about 969 s at a planning I_F of 650 s **(guess)**.
- **PLE disk-paging confound.** Production reads the PLE with `pread` on an `F_NOCACHE` descriptor (§5). Its I/O is then a function of the tokens (work), not of page-cache history (state). R1-FN runs an ABBA that **measures** the PLE I/O energy on identical tokens (cold `pread` against a pre-touched `mmap`). It is printed as a work component, never modelled as a state term.
- **Windows.** One model per calibration window, unchanged.
  - An **FN-Q** qualification window: 13 members, maximum 42,060 s. Its two D sentinels bridge FN to D inside one window.
  - FN calibration windows FN1-FN3 use the D_k shape.
  - FN windows **interleave** with D (D_k, FN-Q, D_k+1, FN1, …). D never waits for FN.

---

## 1. What Saturday must show: Gate S (pre-registered admission bars)

Saturday 2026-11-07 runs `mbp_live.md` steps 0-7 by day on the measurement MacBook Pro (Mac15,9 expected), with the PLE on `/Volumes/JW-EXT`. Each bar below is evaluated **mechanically** from the fixed evidence files (`memory.json`, `performance-512.json`, `performance-2048.json`, `quality.json`, `benchmark.json`, `hosted.json`, `paging.json`, `convert.json`). Every bar is fixed by this draft before any of those files exists. A bar may never be loosened after the data are seen. It can only be re-registered for a **new** artifact.

| Bar | Pass condition | Evidence | Binding where |
|---|---|---|---|
| **S0 identity** | `download.json` revision `de4b8e4d…`, 131 shards authenticated. `convert.json` profile ∈ {maxfit, maxfit5}, `module_sha256 = f4ec75d1…2c37`, `manifest_sha256` recorded off-artifact, ordinary `SHA256SUMS` re-verified (`shasum -c` exit 0). Validation venv mlx 0.31.2 / mlx-lm 0.31.3. | `download.json`, `convert.json`, run notes | Saturday |
| **S1 memory: fits without swap at 40,960** | The `memory` stage completes all three rungs (4,096 / 16,384 / 40,960, plus 64 decode forwards each) with verdict complete, and at **every** sample: live swap used 0, `vm_stat` Swapouts delta 0, kernel pressure level 1 (normal), `memory_pressure -Q` free ≥ 10 %, compressor growth ≤ 2 GB, PLE resident ≤ 21.5 GB. Metal peak ≤ the effective ceiling (min of 115.4e9 and the device's recommended working set), with **≥ 1.0 GB margin** at the 40,960 rung. Measured/predicted Metal peak is within ±10 %. A floor-only stop is a **fail**. | `memory.json`, `.monitor.jsonl`, `.rungs.jsonl` | Saturday (mmap is conservative for the pread mode: see §5) |
| **S1b production chunk** | FN's production `prefill_step_size` is the **largest** of {2048, 512} whose Saturday runs reached the 40,960 context with no stop condition. 2048 is evidenced by `performance-2048.json`; 512 by `memory.json` together with `performance-512.json`. If neither qualifies, S1 fails. | the above | Saturday |
| **S2 speed floor** | Medians over 3 timed repeats at chunk 512, xhigh: decode ≥ **15.0 tok/s** at 16,384, decode ≥ **12.0 tok/s** at 40,960, prefill ≥ **200 tok/s** at 4,096. | `performance-512.json` `medians` | **Screen** on Saturday. **Binding** in R0-FN-b on internal disk. If Saturday fails S2, the verdict is PROVISIONAL, not a rejection. |
| **S3 quality vs bf16** (PR #671 harness, profile `maxfit`/`maxfit5`; `THRESHOLDS["profiles"]` as on `6cacb2be5`) | `quality`: consistency PASS; each natural text ≤ 2.5 nats/token; shuffled control ≥ 2.0 nats/token worse; long-text tail ≤ +0.5 nats over its first 2,048; coherence ≥ 10/11; toolcall ≥ 12/16 including both round trips, with re-render identity. `benchmark` (non-thinking, low effort): math ≥ 25/30, ifeval ≥ 17/25. **Against a bf16 reference:** NLL ≤ ref × 1.02 + 0.02, and where logprobs exist, bucketed KL ≤ 0.05, top-1 ≥ 0.95, top-k overlap ≥ 0.85, hosted token in local top 5 ≥ 0.99. | `quality.json`, `benchmark.json`, `hosted.json` | Saturday for the item floors. **The bf16 comparison stays OPEN** until a reference exists (E4). |
| **S4 native checks** | `tests.test_qwen4exp_mbp_live` 30 OK, 0 skips. `tests.test_qwen4exp_e2e_eval` 37 OK with exactly the 1 permitted skip (item rebuild). `tests.test_qwen4exp_hosted_reference` 13 OK. Any other skip is a fail. | operator log | Saturday |
| **S5 paging recorded** | `paging.json` has both passes with post-load `iostat` deltas, PLE lookup, dedupe and fault counters, and `mincore` residency. **No threshold:** it is input to §5, not an admission bar. | `paging.json` | Saturday |

**The S3 bounds are the existing 8-bit screening bounds.** The harness labels them provisional. Registering them here turns them into FN's admission bars, which are stricter than a measured 6-bit drift budget would likely be. That is deliberate. If GOAL item 11's layer-streamed gold later measures maxfit's drift, a **re-registration** may replace them (measured value × 2, per `e2e_validation.md` §3). It may do so only before any FN calibration-window desk is read.

**Verdicts (printed by the Gate-S reader, build item F15):**
- **ADMIT-CANDIDATE**: S0, S1, S1b, S3 (item floors) and S4 pass on maxfit, or on maxfit5 after a recorded maxfit S1 fail. S2 passes or is PROVISIONAL. FN proceeds to the disk plan (§6) and R0-FN. The bf16 comparison must close before the Addendum FN cold gate.
- **NOT ADMITTED**: S1 fails on both profiles, or S3 fails on the admitted profile. A quality failure is an investigation (`mbp_live.md` §2), never a silent switch to fewer bits. FN stays out of this series, and the result is reported.
- **INCOMPLETE**: any stage is missing. Nothing is inferred from the stages present.

---

## 2. Thermal class, holds and acceptance form

- **Rule (unchanged FINAL-DESIGN §2.5).** FN is heavy if its R1-FN planning turn lasts ≥ 0.6 × t_decline,F. The planning turn is 10,000 fed prefill tokens plus a 4,096-token seeded decode at R1-FN rates. Otherwise FN is light.
- **Prediction: heavy.** Decode is bandwidth-bound. From `perf.md` §6's per-token byte table, re-costed for maxfit:

  | Component | GB/token |
  |---|---|
  | Dense core in bf16 (DeltaNet, QSA, hyper-connections, lm_head, shared expert) | ≈ 8.42 |
  | Routed experts at 6-bit (48 × 10 × 4.92M active parameters) | ≈ 1.92 |
  | Recurrent state, router, KV and PLE | ≈ 0.44 |
  | **Total** | **≈ 10.8** |

  At 230-300 GB/s effective, plus launch gaps, decode is ≈ 20-25 tok/s **(guess)**. The planning turn is then ≈ 25 s of prefill plus 164-205 s of decode, about 190-240 s. Pilot 2's decline onset was 167-201 s (`e1308804` l.58), so 0.6 × t_decline ≈ 100-121 s.
- **If heavy:** G0, G1 and holds. N_chunk,F = 256 × ⌊0.6 × t_decline,F × r_decode,F / 256⌋, minimum 256.
- **If light:** that is, R1-FN finds t_decline,F = ∞, or the planning turn is shorter than 0.6 × t_decline,F. FN runs G0, and G1 follows the W1 contrast verdict for light cells (FINAL-DESIGN §2.5; Amendment 1 §A3.2(b)). There are no holds.
- **U5 form follows the class.**
  - Heavy: β_T,F from FN's own identical-work pairs (the R1-FN pair, FN-Q 6↔12, FN sentinels), multiplied by the G0 release range.
  - Light: the contrast δ scaled by E_FN/E_30B.
- **U1-U4, U6, exclusions X1-X8 and the timeout rules are unchanged.** One addition to X6: a PLE read error (`EIO`, or a short `pread`) is a member failure.

---

## 3. Token budget B_F, effort, per-turn cap, deadman

- **Effort ladder (R0-FN-a; development seeds 91-92; 2 benign episodes per rung).** Rungs `xhigh` (template default), then `medium`, then `low`. These are the efforts the template supports (`mbp_live.md` §5). The pass rule is D's (FINAL-DESIGN §2.2): ≤ 20 % of turns end at the cap with unclosed reasoning, **and** median reasoning tokens per turn ≤ 2,048. Per-turn cap 4,096. If no rung passes at 4,096, re-screen at 8,192 on the last rung tried. If that also fails, FN is screen-only in this series.
- **Sampler.** The model card's thinking sampler is transcribed from the README at the pinned revision, with its file sha256, into the Addendum before R0-FN. A card presence penalty ≠ 0 cannot be expressed (the endpoint's presence is fixed at 0) and is recorded as a deviation, as for N-Instruct.
- **B_F** = the largest multiple of 1,024 such that the R1-FN planning member is ≤ 1,800 s.
  - Floor **8,192**. That is two full turns at the 4,096 cap, the N floor from FINAL-DESIGN §2.2. FN is a MoE thinking model like N, not a dense 27B.
  - Capped by the 40,960 context.
  - Stop flag `episode.decode_budget:<k>`: a normal stop.
- **Below the floor.** If B_F < 8,192 on the admitted profile, FN is **screen-only**. maxfit5 is no speed remedy: about 10.5 against 10.8 GB/token, roughly 3 % faster. The only real lever is quantizing the bf16 core, for example 8-bit "other" weights (≈ 6.3 GB/token, ≈ 1.7× faster **(guess)**). That trades away Ed's "as close to the full fp16 as I can get", so it goes to Ed (E5) as a new artifact with a new Gate S.
- **Deadman.** T_dead,F = (1,750 − I_F)/1.13544 s of episode wall time, flag `episode.deadman:<k>` (X7). I_F is measured in R1-FN. The planning I_F is ≈ 650 s **(guess)**: the transferred 516.6 s intercept, plus about 100 s of full-manifest verification of 210 GB at ≈ 2-4 GB/s (`F_NOCACHE`, 4 workers), plus about 20-30 s to load 108 GB of weights from internal disk. That gives T_dead,F ≈ 969 s.
- **Feasibility of S2's floor.** At 15 tok/s, 8,192 decode tokens take 546 s. About 20k prefill tokens at 200 tok/s take 100 s. With 25-35 % gate and hold overhead **(guess)**, the episode takes ≈ 810-870 s, which is ≤ 969 s. This sum is the derivation of S2.

---

## 4. R0-FN and R1-FN (additions; Amendment 1 §A5 R0/R1 for D unchanged)

R0-FN is split by whether the result depends on the PLE's I/O path. Both parts run by day with no window armed. Neither part is a measurement.

**R0-FN-a: I/O-path-independent.** It may run with the artifact on JW-EXT while the SSD is still on loan. The SSD is ejected and unplugged before any window, as always.

1. **Template.** Render the official Flash-Next template (sha256 `c3cf9e34…1041`) through the v4 endpoint. Bars:
   - XML tool envelopes parse at ≥ 95 %, with no `unsupported_tool_call_format`;
   - `reasoning_content` history: 0 rewritten tokens on closed-reasoning turns over ≥ 12 real generated transitions (the B2 bar);
   - the family check refuses a mismatched configuration.
2. **Coherence.** NLL ≤ 3.0 nats/token on the fixed 2k SHADE prompt.
3. **Effort ladder and cap screen** (§3).
4. **#1632-class long decode** to 40,960 positions with the episode's own cache objects (DeltaNet state, QSA KV and raw keys, PLE convolution and token history). Pass: no Metal resource error, and active-memory growth ≤ 2 GB per 10k tokens.
5. **Determinism.** Two seeded runs of one development episode are token-identical with the n-gram path active. This is Amendment 1 §A4 bar 1's "per-turn reseed determinism".
6. **Tokenizer under the measurement lock.** Measurement transformers 5.12.1 must produce token ids byte-identical to 5.22.1 on the e2e items, the 12 hosted prompts and both SHADE pairs' turn-0 prompts. This uses tokenizer files only and runs on the laptop (F14). On a mismatch, E6 applies.

**R0-FN-b: on internal disk only.** It needs §6's space. The SSD is ejected and unplugged, and the artifact is copied internally and manifest-verified there.

7. **Production memory.** One full-length development episode through the production runtime (F1) at the S1b chunk, with `pread` PLE and the SMC sidecar on. The S1 bars apply at every sample.
8. **Speed, binding.** S2 re-measured from internal disk with `pread` PLE: `performance-512`-equivalent cells plus the per-turn rates of item 7.
9. **PLE I/O characterization.** Per turn: lookups, unique rows, preads, bytes, gather seconds, `ru_inblock`, major faults, and internal-disk `iostat` deltas. Bar: **`pread` prefill gather time ≤ 15 % of prefill wall time**. If the bar fails, build F16 (batched `pread`).

**R1-FN** is quiet, uses the Interactive LaunchAgent with no agent alive, and takes about 2-2.5 h by day. It is a separate session from Friday/Saturday's D R1. It needs R0-FN-b.

1. **FN planning-turn step test** (10k fed prefill + 4,096 seeded decode) with a 10-minute cooldown. This gives t63, τ and ΔT per classified key, t_decline,F, and the **class**.
2. **Two gated FN spam/benign s1 runs**, held if heavy. They give U3, token identity under holds, and the FN-Q cross-session reference.
3. **PLE I/O ABBA** (4 runs, on the token sequence of run 2):
   - **P** = cold `pread`;
   - **W** = `mmap` with exactly the episode's PLE rows pre-touched before the episode stamp (from run 2's token log; no faults during the episode).

   Same tokens, gates and holds. Report Δ = mean(P) − mean(W) for turn-owned GPU energy, gross energy, the unassigned power residual and turn latency, each with its 90 % t interval. Rules:
   - |Δ turn-owned GPU| ≤ 3 × max(2.97 J, 0.0011 × E) (the U3 bar): the PLE I/O effect is declared **below identical-work noise**.
   - Otherwise it is disclosed as a **work component of size Δ** in every FN result.
   - Either way, production stays `pread` (§5).

   Abort W at any S1 stop condition.
4. **Fill FN's slots:** B_F, I_F, T_dead,F, N_chunk,F, t_decline,F, class_F, prefill_step_F, ple_io_mode, and FN's G_turn (or G_turn shared with D if R1 already set it). Sensors and δ are machine-level and are reused from R1, not re-selected.

---

## 5. PLE disk paging: the energy confound and the ruling

**Physics.**
- Each token gathers 16 rows of 160 bf16 values: 5,120 logical bytes (`qwen4_exp_port.md`).
- Through `mmap`, each touched row faults in a 16 KiB page if it is not resident. Residency then depends on everything that ran before: earlier members, the hash pass, the other models' loads. Two token-identical episodes can do different amounts of I/O. That is a **state** effect, and it threatens U3/U4 directly. It also adds up to 10-21.5 GB of file pages beside a 112.7 GB Metal peak (physical upper estimate 134.2 GB against 137.4e9 bytes).
- Through `pread` on an `F_NOCACHE` descriptor (`NgramTable(io="pread")`, already in the pinned module), each lookup is a device read, and the OS buffer cache holds nothing. The I/O sequence is a function of the token sequence: a **work** effect, reproducible across members and windows.
- Scale **(guess)**: about 16 × 4 KiB = 64 KiB per token before dedupe. That is ≈ 1.3 MB/s and ≈ 320 IOPS in decode at 20 tok/s, and ≈ 25 MB/s and ≈ 6,400 IOPS in prefill at 400 tok/s, on an internal Apple SSD. The direct device power is probably well under 1 % of a ≈ 40 W turn.
- The larger effect is latency. `pread` is serial per row today, so decode stalls ≈ 1-1.6 ms per token (≈ 3 %), and prefill may stall more (R0-FN-b item 9).
- The energy lands mostly outside the GPU rail: SSD and CPU fault handling appear in PSTR − (GPU + CPU + ANE). The GPU is affected through idle-in-turn time.

**Ruling (proposed).**
1. **The PLE must be on internal disk in every window.** Before arming and before every FN member, the census refuses if any FN artifact file (weights, PLE table, module, config), after resolving symlinks, lives on a device other than the internal Data volume. This adds to the existing external-volume census and bus-baseline refusal (PR #665 §15), which already forbid an attached enclosure.
2. **Production `ple_io_mode = pread`** (`F_NOCACHE`). It is applied as a `model_config` override at load, recorded in the execution-policy hash, and changes no artifact byte. `mmap` is used only as R1-FN's W arm.
3. **PLE I/O is measured and printed, never modelled.** Per turn, the desk prints PLE lookups, unique rows, preads, bytes, gather seconds and the internal-disk read delta beside turn-owned and gross energy. In keeping with `cf1baad2` Ruling (2), no I/O covariate enters the frozen sequence design. A labelled sensitivity (unique PLE rows per turn) may be printed, as G0 release S_slow is.
4. **Saturday's paging numbers are external USB4 and `mmap`.** They characterize the port, not the production I/O path. They inform §5 but cannot substitute for R0-FN-b.
5. **Pre-touch, `purge`, or cache clearing is never used** inside a measurement window. Pre-touch in R1-FN's W arm happens before the episode stamp and is itself the treatment.

**Why not `mmap` with a warm-up?** The rows an episode needs are unknown until its tokens exist, so no warm-up makes residency identical across held-out members. Only replays could be warmed, and warming would then differ between sentinels and held-out members.

---

## 6. Internal disk: does the PLE table fit, given the pilots 8-10 offload?

**No, not under any currently authorized reclaim.** All numbers are decimal GB. Artifact sizes come from the port's memory model (`qwen4_exp_port.md`: resident weights + PLE table). Mac free space is the runbook's historical estimate, not a live `df`.

| Need on internal disk | maxfit | maxfit5 |
|---|---:|---:|
| Artifact: resident weights + bf16 PLE table | 108.04 + 102.40 = **210.44** | 92.94 + 102.40 = **195.34** |
| Window headroom: max(W1 gate 80 + journal, FN_k two copies 52.9 + 30 floor) | 82.9 + journal | 82.9 + journal |
| **Free space required before the internal copy** | **≈ 293.4 + journal** | **≈ 278.3 + journal** |

| Reclaim scenario (cumulative; each needs its own custody and Ed approval) | Est. free | Shortfall (maxfit / maxfit5) |
|---|---:|---:|
| Today, all pilots retained (runbook §9b) | ≈ 66 | 227 / 212 |
| Saturday run A (PR #665 §15) | **+0**: copy-only; pilots stay KEEP until block-5 release | 227 / 212 |
| Delete the dropped models: Qwen3.5-122B-A10B-4bit (69.62) + Qwen3-Next-80B-Instruct-4bit (44.86) | ≈ 180.5 | 113 / 98 |
| Plus pilots 8-10 after block-5 release (≈ 26 each, estimated; run B two-copy custody) | ≈ 258.5 | 35 / 20 |
| Plus a quantized-PLE artifact instead (new recipe, new Gate S): `maxfit-ple8` 161.8 GB → need 244.7; `maxfit-ple4` 136.2 GB → need 219.1 | ≈ 258.5 | fits (+13.8 / +39.4) |

**Readings.**
- Offloading pilots 8-10 cannot by itself make room. Saturday's run is copy-only, and the pilot roots stay on the Mac until after the block-5 release.
- Even after the release and both model deletions, bf16-PLE maxfit is ≈ 35 GB short, and maxfit5 ≈ 20 GB short. The rest must come from bytes not yet inventoried. Candidates: non-KEEP HF-cache models, BYTES-era weights, and block-5 originals after the release, which the GOAL estimated at "≈ 450 GB+" of data roots. Only a census of non-restricted roots, run by Ed on the Mac, can say.
- D-8bit (29.5) and the 30B anchors (17.2) are mandatory KEEP and are already counted in "today".

**Ruling (proposed).** No FN window, R0-FN-b or R1-FN until a **live** `df` on `/System/Volumes/Data` shows free ≥ artifact + 82.9 GB + journal **before** the copy, and ≥ 82.9 GB + journal after it. The copy is SSD → internal by day, then manifest-pin verification on the internal copy, then eject and unplug. The converted artifact and the 360 GB source stay on JW-EXT until the internal copy verifies (E2: how long can the SSD stay?).

---

## 7. `model_file` hook versus a pin bump

- **No pin bump.** mlx 0.31.2 / mlx-lm 0.31.3 stay. `load_verified_model` itself refuses any other version (`PINS`).
- **What the hook is.** mlx-lm 0.31.3 `utils.load_model` honors `config["model_file"]`: it execs that file from the model directory (`utils.py:325-332`), or takes classes from `get_model_classes`.
- **The pinned runtime cannot load FN.** `joulewise/adapters/mlx_runtime.py` (pinned) calls `mlx_lm.load(source, revision, return_config=True)`. On a maxfit artifact that would:
  1. exec `qwen4_exp.py` from disk **without** hash verification;
  2. **not** open the n-gram tables, which `load_verified_model` does by calling `model.ngram_tables()`;
  3. then hash the whole 210 GB tree with buffered reads (`model_artifact_identity`), pulling the PLE through the page cache inside the member. That cuts against §5 and could pressure memory.
- **Ruling (proposed).**
  - FN members use an **align-local runtime subclass** (F1). It overrides only `prepare`:
    1. call `load_verified_model(source, manifest_pin, expected_module_sha256=f4ec75d1…, model_config={"ngram_tables": {…, "io": "pread"}})`, which verifies with `F_NOCACHE` and compiles the module from the hashed bytes;
    2. load the tokenizer as the pinned runtime does;
    3. emit an artifact identity of kind `joulewise_qwen4_exp_manifest_v2`: manifest sha256, module sha256, profile, the converter's code commit, `ple_io_mode`, `prefill_step_size`.
  - Every other method is inherited unchanged.
  - `joulewise/align/*` carries no pin (FINAL-DESIGN V8), so nothing sealed is edited. The anchors and D keep the pinned `prepare`, byte-identical.
- **Not admissible.** The P10 expert-streaming lane's module (a different sha) and any community port (#1788, mlx-vlm) may not supply FN members. The module pin is enforced at load and recorded in every bundle.

---

## 8. Windows and interleaving with D

**FN-Q (qualification; selection data; development seeds only).** It replaces Amendment 1 §A4's FN-Q sketch.

| Ord | Member | Class | Planning member_s (guess; R1-FN replaces) |
|---|---|---|---|
| 1-4 | anchors a-e01 … a-e04 | byte-identical to pilots 4-9 | 4 × 782.82 |
| 5 | D sentinel early: replay of W1 ordinal 5 (first sidecar member; its idle sets R) | D | 1,800 |
| 6 | FN spam/benign s1 (**original**) | FN | 1,800 |
| 7 | FN bank/benign s1 | FN | 1,800 |
| 8 | FN spam/sabotage s1 | FN | 1,800 |
| 9 | FN bank/sabotage s1 | FN | 1,800 |
| 10 | FN bank/benign s93 (development) | FN | 1,800 |
| 11 | FN spam/benign s94 (development) | FN | 1,800 |
| 12 | FN spam/benign s1 **replay** (FN U3 with 6) | FN | 1,800 |
| 13 | D sentinel late: replay of W1 ordinal 5 (D U3 and U4 across windows) | D | 1,800 |

- **Arithmetic.**
  - Align = 3,131.27 + 9 × 1,800 = **19,331.27 s**.
  - Span = 19,331.27 + 4,995 = **24,327 s**.
  - Max = 60 × ⌈(24,327 + 17,700)/60⌉ = 60 × 701 = **42,060 s**, which is ≤ 44,640, with 2,613 s of span slack.
  - Disk: 4 × 592.2 MB + 9 × 1,113.4 MB + 4.04 GB = **16.43 GB per copy**, 32.9 GB for two.
- **Fit rule** (applied after R1-FN; span limit 26,940): drop 11, then drop 10, then lower B_F in steps of 1,024 to 8,192, then return the roster to the lead. Anchors, ordinals 6-9, the 6↔12 pair and both D sentinels are never cut.
- **What FN-Q yields:**
  - U1-U3 for FN, and for D through 5↔13;
  - FN's capability gate (Amendment 1 §A3.7 applies to FN unchanged);
  - FN's rates, gate and hold costs, rebuild counts and PLE I/O tables;
  - a within-window FN↔D state bridge.

**FN calibration windows FN_k.** These are the D_k shape (Amendment 1 §A2) with FN sentinels (replays of FN-Q ordinal 6) at ordinal 5 and at the last ordinal.
- If R1-FN gives m_F ≤ 1,175 s: a **44,640** window of 4 anchors + 2 sentinels + 12 benign (6/pair) + 2 sabotage = 20 members. Feasibility: 3,131.27 + 16 m_F ≤ 21,945.
- Otherwise: the **59,520** window, 22 members (14 benign, 2 sabotage), as D_k. Maximum 58,260 s at m_F = 1,800; disk 52.9 GB for two copies. It holds up to m_F ≤ 1,871 s.
- Target as D: m ≥ 20 held-out benign per pair and ≥ 2 held-out sabotage per pair, under frozen per-session LOO `7fbd95e31`, per pair. FN is its own cohort, never pooled with D.

**Interleaving.**
- One model per calibration window (unchanged).
- After FN admission, FN-Q takes the **next free slot after the D window in progress**, and the models then alternate: … D_k, FN-Q, D_k+1, FN1, D_k+2, FN2, FN3 (FN windows continue after D3).
- D never waits for FN.
- Every window keeps its 4 anchors. FN-Q's D sentinels are the only cross-model in-window bridge, and U4 for D counts them as D sentinels.
- **Default reservation for FN:** 42,060 + 3 × 58,260 = 216,840 s (60 h) of window maxima.

---

## 9. What Ed must decide

| # | Question | Default (proposed) | If Ed answers otherwise |
|---|---|---|---|
| **E1** | **Internal disk for the FN artifact (§6).** Choose any combination: (a) delete Qwen3.5-122B-4bit and Next-80B-Instruct-4bit (+114.5 GB; public weights, but the runbook retired the public-only exception, so this needs an explicit Ed exception or two copies); (b) authorize Ed's census of non-restricted roots (HF cache, `jw_models`, BYTES-era weights) to find ≥ 35 GB more; (c) wait for the block-5 release and run B offload of pilots 8-10 and the B5 originals; (d) a quantized-PLE artifact (q8: 161.8 GB; q4: 136.2 GB), which is a new recipe with a new Gate S. | **(a) + (b) now, (c) when it comes; bf16 PLE kept.** FN stays blocked until a live `df` passes §6. | **(d):** FN fits after (a) + (c), at a precision cost on the n-gram table only. **No reclaim:** FN is out of this series. Its Saturday evidence stands as port validation. |
| E2 | How long can the borrowed SN7100 stay? | Until the internal copy of the admitted artifact verifies; by day only; never during a window. | If it must go back first: the artifact needs another verified home (iCloud ≈ 210 GB upload), or a re-download (360 GB) and re-conversion later. |
| E3 | 59,520 s windows for FN_k (the Q4 analogue) | **Yes**, unless R1-FN gives m_F ≤ 1,175 s, in which case 44,640 is used automatically. | FN takes about twice as many windows at 44,640. |
| E4 | bf16 reference for S3 | **Layer-streamed gold on the laptop** (GOAL item 11 lane `a6f9df9b3`): teacher-forced bf16 logprobs on the 12 fixed prompts plus item-level NLL, at no cost (F13). | Rent a verified bf16 vLLM host (8 × 80 GB) for the benchmark comparison too, with the operator-attested identity receipt of `mbp_live.md` §4. |
| E5 | If B_F < 8,192 (speed) | FN is screen-only; no automatic recipe change. | Authorize an 8-bit-core artifact (≈ 1.7× faster **(guess)**): new conversion, new Gate S, and a precision disclosure. |
| E6 | Tokenizer under the measurement lock (transformers 5.12.1) | Expect identity. On a mismatch, FN loads its tokenizer through `tokenizers` directly in align-local code (no venv change). | Otherwise FN is blocked. A venv change is a stack change for the anchors and D. |
| E7 | FN-Q placement | Interleave at the next free slot (§8). | **After D3:** FN starts when D's series ends. |
| E8 | Per-member full manifest verification (≈ 100 s of I/O per FN member, inside I_F) | **Yes**, the same custody as D's per-member tree hash. | Verify once per window at prepare, with a per-member (dev, inode, size, mtime) recheck. That gives a smaller I_F and a longer T_dead,F. |
| E9 | Keep a purchased SSD attached for the whole series? | **No.** It is a permanent bus device on every member, conflicting with the census, and it needs a bridging window. | Only as a new physical setup in place before W1, with its own ruling. |

---

## 10. What this draft does not change
- W1, D's series, D's slots and D's frozen record. Adding FN edits none of them (Amendment 1 §A4).
- U1-U6, X1-X8, the contrast rule, seed law and roles, the frozen desk `cda28a5ef`/`4d54cb47b`, and calibration `7fbd95e31`.
- R0 and R1 for D (Amendment 2 §1's 300/900/600 s step profile applies to R1-FN's step test too).
- The SSD rule: attached by day only, and ejected **and unplugged** before every window, R0 and R1 (PR #665).

## 11. Residual risks
1. **Memory margin.** 2.72 GB on paper at maxfit. S1 requires ≥ 1.0 GB measured, and production adds the sidecar and runner. maxfit5 has a 17.8 GB margin.
2. **`pread` latency** may cut prefill throughput enough to fail S2 or R0-FN-b item 9. F16 (batched `pread`) is then a new module sha, requiring tiny parity plus a Mac quality rerun.
3. **Disk** (§6) may push FN past this series.
4. **Template.** Flash-Next may differ from Qwen3.8-27B in its `reasoning_content` handling. R0-FN-a item 1 decides, and F3 must not assume it.
5. **Capability at 8,192-token budgets.** Like D, FN may fail the capability gate. It is then reported as an energy and capability screen.
6. **Saturday is not a measurement.** No result in its bundle is an energy number. The PLE I/O energy size is unknown until R1-FN's ABBA.

## 12. Build list (to make FN runnable; all on the v4 line, Sol builds, Opus executes the review, Fable cold-passes F1/F3/F5/F6)

| # | Item | Where | Test |
|---|---|---|---|
| F1 | `Qwen4ExpMlxRuntime(MLXRuntime)`: `prepare` through `load_verified_model` (manifest and module pins, `pread` override, prefill step), tokenizer load, manifest-kind artifact identity, refusal if any artifact file resolves off the internal Data volume | new `joulewise/align/apple/qwen4_exp_runtime.py` | tiny canonical fixture (converted by the converter in the test): loads, wrong manifest or module pin refuses, `pread` is selected, identity fields present, off-volume path refuses |
| F2 | Bring the canonical module (`f4ec75d1…`) and `load_verified_model` into the v4 line unchanged; record the module pin in kit identity pins | `joulewise/align/models/qwen4_exp.py`, `scripts/align_convert_qwen4_exp.py` from `6cacb2be5` | sha equality test |
| F3 | Family `qwen4_exp` in `XML_MODEL_FAMILIES` (after the template audit), `assistant_history: reasoning_content` if the template reads it, effort kwargs | `xml_tool_calls.py`, `endpoint.py` | official template fixture `c3cf9e34…`: round trip with 0 rewrites, typed and parallel calls, anchors and D byte-identical |
| F4 | `prefill_step_size` spec field (omit if None) passed to `stream_generate` and the checkpoint prefill | `workload.py` `EpisodeSpec`, `endpoint.py`, `prompt_cache.py` | D/anchor configs byte-identical; FN passes 512 or 2048 |
| F5 | Hybrid-cache handling for `qwen4_exp` (non-trimmable DeltaNet state): rebuild path, `cache.rebuilt_untrimmable:<k>`, checkpoint off as for D | `prompt_cache.py` | tiny-model rewind leads to a rebuild; token identity |
| F6 | Per-turn PLE I/O telemetry (lookups, unique rows, preads, bytes, gather s, `ru_inblock`, majflt) and per-member internal `iostat` delta, as phase events | F1 + `endpoint.py` | fake table counters appear per turn; attribution tiling unchanged |
| F7 | Kit: tag, seed table, FN-Q roster and fit rule, FN_k builder (44,640/59,520 switch), FN identity pins, manifest-based artifact inventory, FN slots in `r1_slots.json` | `scripts/align_v4_kit.py`, `configs/campaigns/align_v4/**` | seeds recomputed independently, position and drop order, anchor hashes, window arithmetic |
| F8 | R0-FN-a/-b checks (§4) | `scripts/align_r0_checks.py`, `configs/align/v4/r0_fn.json` | fake runtime and fake transport |
| F9 | R1-FN phases: step test, 2 gated runs, PLE ABBA with pre-touch from a token log, slot fill | `scripts/align_r1_rehearsal.py` | phase plan; the pre-touch happens only before the episode stamp |
| F10 | Desk: FN cohort, PLE I/O tables, ABBA verdict, U1-U6 for FN; v3 desk byte-identical | `scripts/align_v4_desk.py`, `diagnostics.py` | synthetic FN bundles |
| F11 | Disk gate for FN windows (artifact verified internally; free ≥ window + 30 GB + journal) and the census rule "no model file off the internal volume" | `joulewise/align/r0_host.py`, `scripts/external_volume_census.py` | symlink-to-`/Volumes` refuses |
| F12 | Protocol v4 "Addendum FN" text from this amendment | `docs/align/pilot_protocol_v4.md` | registration cold gate |
| F13 | Gold-stream bf16 reference, emitted as a `--reference` JSON for the e2e `quality` and `hosted` stages (laptop) | gold-stream lane `a6f9df9b3` | schema test with the tiny reference adapter |
| F14 | Tokenizer equivalence, 5.12.1 against 5.22.1, tokenizer files only (laptop) | new test | ids identical on the pinned items |
| F15 | **Gate-S reader**: evaluates S0-S5 from Saturday's evidence directory and prints ADMIT-CANDIDATE, NOT ADMITTED or INCOMPLETE | new `scripts/qwen4exp_gate_s.py` | fixture result files for each verdict; it never reads outside `--run-dir` |
| F16 | *(conditional on R0-FN-b item 9)* batched `pread` with bounded parallelism in `NgramTable`: a new module sha, tiny parity, and a Mac quality rerun | `qwen4_exp.py` | rows bitwise equal to serial `pread` |
