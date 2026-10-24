# BYTES pack registration, version 1 (draft)

**Status.** This is the draft of a pre-registration: the question, the models, the runs, the exclusions and every piece of arithmetic are fixed in writing before any BYTES energy exists. No BYTES energy has been measured, and nothing below depends on one. A **pack** is one question with its own registration, collection and release (`docs/design/block6_collection_draft.md` §14, "the block-6 design"). This file replaces the BYTES design ruling (`docs/design/bytes_pack_design.md` at `298a292a7`, "the ruling": sections R1 to R8 and Addenda 1 to 8) as the pack's specification; where the two differ, the ruling's later addendum is what this text writes down, and §20 maps every ruling item to the paragraph that carries it. It is not yet the registration. It becomes the registration when every marked slot below is filled and its cold gate passes (R8 item 8); the commit that does that is the registration time, and it must precede the first BYTES session's start (block-6 design §16 item 2).

**Marked slots.** A value that does not exist yet is written as a slot and is never guessed:
- `⟦MAC: …⟧`: a value measured or read on the measurement laptop (R8 items 5 to 7);
- `⟦B2: …⟧`: a value from the analysis and twin build in the cloud (coverage numbers, the estimator digest);
- `⟦B4: …⟧`: a name fixed by the build of the shared blinding group and withheld store (R8 item 7, C6 and C7);
- `⟦NEEDS_RULING: …⟧`: a question this text cannot settle from the governing texts.
§18 lists every slot.

**Authority.** In order: the BAT-2 ruling (2026-10-21; `docs/process_traces/2026-10-22-forward/BAT-RULING.md`) on the battery term, its edge term v and the decode-assisted marker (§6, §7, §9), where it amends Addendum 1 item 2, Addendum 4 item 11 and Addendum 9's C_j; then the ruling's Addendum 9 (2026-10-21, NR1; `docs/process_traces/2026-10-21-magistrate-a017b694/B2-NR1-RULING.md`), then Addendum 8, then 7, 6, 5, 4, 3, 2, 1, then R1 to R8; the block-6 replication registration (`docs/registrations/block6_replication_DRAFT.md` on `main`, "the block-6 registration") for anything that would change how the replication packs ALPHA, BETA and GAMMA behave (they must behave byte-identically); the block-6 design §14 to §17, whose §14 fixes the form of a pack registration; and block 5's registered arithmetic (`configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`, "the block-5 plan", with its library), which wins on arithmetic (Addendum 1 item 1, Addendum 7 D8). The lead's ruling on BYTES blinding of 2026-10-20 (§11) is part of this text.

## 1. The question

A language model writes text one **token** at a time (a token is a short piece of text: a word, part of a word, a digit). Writing each token needs one **forward pass** through the network, and during that pass the processor reads the model's weights, and the stored keys and values of earlier tokens (the **KV cache**), from memory. On the machine used here, an Apple M3 Max laptop with 128 GB of memory running Apple's MLX library, energy per token might follow how many bytes are read per token, how large the model is in memory, or simply how long each token takes.

**Question.** Does decode energy per token follow the format-derived bytes the model reads per token (weights used per token plus KV), the resident model size, or decode time? (R1.)

- **Decode** is the part of a request after the first output token, in which the model writes the rest of its answer (§3).
- **Format-derived bytes** b (also "bytes read per token"): bytes computed from the stored sizes of the tensors the model uses for one token, read from the model files (§4), never from a memory-controller counter (R1).
- **Resident size** R: the bytes of all weights the model holds in memory (§4).
- **Decode time** τ: seconds per decode forward pass (§7).

**Mixture-of-experts** (MoE) models use only k of their E "expert" weight blocks for each token, so they read far fewer bytes per token than they hold. That is what separates the hypotheses: on the three MoE models (30B-A3B, Next-80B, Qwen3.5-122B) the resident hypothesis's prediction is 8.42, 19.43 and 12.20 times the bytes hypothesis's, and the time hypothesis's 1.68, 2.22 and 1.39 times (the ruling's preamble, "MoE splits resident/bytes" and "time/bytes": the lead's re-execution of the design seats' `calc/design.py` on the pilot column, JouleWise-data branch `claude/bytes-design-opus`). On dense models the hypotheses' predictions differ by only 2 to 9% (R5), so dense held-out models test whether a line stays straight over the bytes range, not which hypothesis is right; this is said wherever their results are printed.

**Boundaries.** Each energy is measured at three **boundaries** (what the meter sees; R1):
- **rails**: the processor chip's CPU, GPU and neural-engine energy as reported by macOS `powermetrics`;
- **DC input**: the energy entering the whole machine. It is the power on its USB-C charging cable after the power
  adapter, from a KM003C USB-C meter, plus the power the battery supplies when the machine draws more than the
  adapter delivers (§7, "Battery term"). It is never called "wall" or "AC".
- **rest**: DC input minus rails, which includes memory chips, power conversion losses, the SSD and fans.

The recorded `powermetrics` samples carry no memory (DRAM) key, so the energy of reading memory is split: the chip's share appears in rails, the memory chips' share only in rest (block-6 design §15, "BYTES measures in two boundaries"). Whether the GPU rail includes the memory controller is measured by the known-bytes stream test (R8 item 6): `⟦MAC: known-bytes stream test outcome⟧`.

## 2. The models

All ten models are MLX checkpoints of the `mlx-community` organisation on Hugging Face, at the revisions in `configs/campaigns/bytes_v1/roster.json` (R1, R4). The **fit set** is the three models the rival lines are drawn through; the **held-out** models are predicted from those lines.

| Role | Model | Revision (`roster.json`) | MoE (k of E experts per token; pilot table) | In the Qwen3 4-bit tier (§9) |
|---|---|---|---|---|
| fit | Qwen3-1.7B-4bit | `3b1b1768f8f8cf8351c712464f906e86c2b8269e` | dense | yes |
| fit | Qwen3-4B-4bit | `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25` | dense | yes |
| fit | Qwen3-8B-4bit | `545dc4251c05440727734bcd94334791f6ab0192` | dense | yes |
| held out, dense | Qwen3-14B-4bit | `a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4` | dense | yes |
| held out, dense | Qwen3-32B-4bit | `bcaaf7f538adf166c1080a2befdb4f6019f66639` | dense | yes |
| held out, dense | Llama-3.3-70B-Instruct-4bit | `de2dfaf56839b7d0e834157d2401dee02726874d` | dense | no |
| held out, dense | Qwen3-8B-8bit | `⟦MAC: revision (R8 item 5)⟧` | dense | no |
| held out, MoE | Qwen3-30B-A3B-4bit | `d388dead1515f5e085ef7a0431dd8fadf0886c57` | 8 of 128 | yes |
| held out, MoE | Qwen3-Next-80B-A3B-Instruct-4bit | `d8a069bfa8ae87d3d468412e1034acae19b5892b` | 10 of 512, plus shared experts | no |
| held out, MoE | Qwen3.5-122B-A10B-4bit | `e9c67b08899964be5fdd069bb1b4bc8907fe68f5` | 8 of 256, plus shared experts | no |

The k-of-E column is the BYTES pilot's (`docs/design/bytes_pilot/SUMMARY.md`, a run of every model without power capture on 2026-10-14). "4-bit" means each weight is stored in 4 bits with a scale and offset per group of 64 weights (`4b/64g/affine` for every 4-bit model in the pilot's header census; Qwen3-Next-80B also stores 50,429,952 bytes of weights at 8 bits).

**Qwen3-8B-8bit** has the same architecture as the fit-set 8B and about twice its bytes per token; without it no quantization statement stands (R1). It is kept only if it passes the resolvability check of R8 item 6 (a 3 to 5 run check that its decode phase is resolvable: block-6 design §14): `⟦MAC: 8B-8bit kept or dropped⟧`. If it is dropped, it is removed before registration, the quantization sentence is deleted, the H1 family becomes 18 checks (§10) and H2 has three non-tier models (§9). Its group size of 64 is assumed and recorded unverified until the checkpoint is downloaded (Addendum 5 item 5).

**Printed ranges.** R1 prints "a 32-fold range of bytes read per token (weights plus KV), 69-fold range of resident size". Both are recomputed from the frozen manifest (§4) before they are printed: the bytes range is max b / min b over the registered roster and the resident range is max R / min R, each rounded to a whole number: `⟦MAC: b range from the manifest⟧`-fold and `⟦MAC: R range from the manifest⟧`-fold. *Derivation of the ruling's numbers from the pilot table:* b = measured weight bytes + 0.9 × end-of-run KV bytes gives 39.8523 GB (Llama-70B) / 1.2322 GB (Qwen3-1.7B) = 32.3; resident 68.6907 GB (Qwen3.5-122B) / 0.9680 GB (Qwen3-1.7B) = 71.0 unrounded, while the table's rounded columns give 68.7 / 1.0 = 68.7, which is where "69" came from. The manifest's value replaces both. The phrase "two orders of magnitude" is not used (R1).

## 3. The workload

Every science run is the same request (R2, as amended by Addendum 5 item 4):
- a prompt of exactly 2,048 token ids built by `_synthetic_prompt_tokens` (`joulewise/adapters/mlx_runtime.py`), which is exact for every tokenizer;
- exactly 512 output tokens chosen greedily (temperature 0: the most probable token each time), with the end-of-sequence token suppressed so every run writes 512;
- one 4-token warm-up on the same prompt and the inherited 5 s settle before the request;
- the model is loaded in the run's preparation, outside the measured request.

**Phases.** **Prefill** reads the prompt and ends at the first output token (`phase_boundary_method: first_token`). **Decode** is the rest of the request. The pinned runtime (mlx 0.31.2, mlx-lm 0.31.3, mlx-metal 0.31.2; the ruling's preamble) calls `stream_generate(max_tokens=512)`, which dispatches **512 decode forward passes** inside the measured request, one of which computes a token that is never returned (Addendum 5 item 4, confirmed by the pilot's caches ending at 2,560 = 2,048 + 512 positions on all six attention-only models). All per-pass arithmetic therefore divides by 512, and the printed per-token value carries the label "512 decode forward passes, one of which yields no returned token". R2's and R3's "511" is replaced; the change is a uniform 0.2% on e (512/511 − 1 = 0.00196) and moves no word (Addendum 5 item 4). Prefill energies are recorded and not analysed. No runtime code is changed for BYTES.

## 4. The bytes manifest

`scripts/bytes_manifest.py` writes `configs/bytes/bytes_manifest.json`, frozen before the first BYTES session (R4). Per model it records the revision, tokenizer, k and E, shared experts and whether the embeddings are tied, and three byte counts, all integers (bytes are counted, not estimated; the 2026-10-20 status audit (JouleWise-data branch `claude/bytes-status-c634`, `reports/bytes-status-c634/BYTES-STATUS.md`, "the audit") §5 P5):
- **W**, bytes of weights used per decode pass: the stored sizes, including quantization scales and offsets, of every dense weight used per token, one row of the input embedding, the whole output layer, and k/E of the routed expert weights plus the shared experts;
- **R**, resident bytes: the sum of all loaded weight storage;
- **KV**, KV-cache bytes per decode pass: (cache bytes after prefill + cache bytes after the 512th decode pass) / 2, that is at 2,048 and 2,560 positions (R4 with Addendum 5 item 4), from one MLX generation per model on the laptop without power capture. Occupied length and allocated capacity are recorded separately, as is the cache class of each layer; the recurrent-state layers of Qwen3-Next and Qwen3.5 have constant size. `joulewise/kv_size.py`, which assumes every layer is full attention, is not used.

Then b = W + KV and R are converted to GB with 1 GB = 10⁹ bytes (`docs/contracts/bytes_tables.md`).

Tensors that mlx-lm's loader discards (names beginning `vision_tower.` or `model.visual.`, or containing an `mtp.` segment) get category `not_loaded`; their bytes are recorded and kept out of W and R. Any other unknown tensor name makes the script refuse (Addendum 5 item 3; Qwen3.5-122B holds 333 such vision tensors, 0.9026 GB, beside 68.6907 GB of language-model tensors, which equals the pilot's loaded bytes). The manifest prints its differences from the pilot column.

Manifest values: `⟦MAC: manifest SHA-256⟧`; per model W, KV (occupied and allocated) and R in bytes: `⟦MAC: manifest table⟧`.

## 5. Collection

**Floor module.** Each model is measured in one **floor module** per pass: 10 **absolute repeats** (single runs) and 10 **null quads** (four runs in A, B, B, A positions where A and B are the same configuration, so the contrast is null), 50 runs in all (R6; `configs/campaigns/bytes_v1/generate_configs.py`). A **unit** is a repeat or a whole quad; the repeats and the quads are the two **strata**. A **cell** is one model, pass and boundary.

**Sub-packs and sessions.** A **session** is one unattended stretch of measurement on the laptop with nothing else running. The ten models are grouped into six **sub-packs**, one session each per pass (R6): s1 1.7B + 4B; s2 8B + 30B-A3B (the cleanest dense and MoE pair shares a session); s3 14B + Next-80B; s4 32B + 8B-8bit; s5 Llama-70B; s6 Qwen3.5-122B. Modules run whole and in sequence. Each session also runs the shared **reference workload** (Qwen2.5-1.5B, 1,024-token prompt, 256 output tokens, about 37 J; block-6 design §14): a **corpus** of 18 planned reference runs stopped after 12 valid ones, a **start triplet** of 3, one **midpoint reference** and an **end triplet** of 3 (`joulewise/b6/registration.py` defaults; pack registration `corpus`). The midpoint falls at the module boundary in two-model sub-packs; in single-model sub-packs s5 and s6 it falls between the quad halves after 30 runs, and the analysis does not assume it splits models (Addendum 5 item 5).

**Passes, packs, counts and stopping** (block-6 design §14's target, minimum and stopping rule). A **pass** is one session of every sub-pack. The target is 2 passes and the minimum 1 (R6); there is no precision stopping. Each sub-pack and pass is its own fixed pack, `bytes-sN-p1` and `bytes-sN-p2` (N = 1 to 6), each with its own plan tree `configs/campaigns/bytes-sN-pP/plan_tree.json` (Addendum 5 items 1 and 2). Every one of the twelve packs registers target 1 session and minimum 1 (Addendum 6: block 6's validator requires a minimum of at least 1, and `minimum_sessions` is read only by precision stopping, which BYTES does not use; "minimum one pass" is a rule of the analysis, §7). Stopping: a pack stops after its one counting session, or when no t0 can start before **2026-11-02T00:00:00-08:00** (R6; the packs' `stopping.end_t0_before`). Pass 2 reverses the module order within each sub-pack and the sub-pack order: the loop's base order (`configs/b6/loop.json`) is s1-p1 … s6-p1, then s6-p2 … s1-p2. Per model the paper prints each pass's value, their mean and their difference (R6).

**Interleaving.** BYTES starts after replication round 1; after each later replication round, the next BYTES sub-packs run. Replication order and GAMMA's pairing never move; a lost BYTES attempt retries in the next BYTES slot (R6).

**Machine time (planning only).** Module minutes in the drafts are (largest pilot request seconds + 57.6 s inherited idle baseline + 5.0 s settle) × 50 runs × 1.2 margin / 60, and 150 min for 8B-8bit (R1's planning estimate; `scripts/bytes_plan_trees.py`). They are not measured session footprints and are replaced by C5's sizing (R8 item 7), whose margin is the largest measured run-to-run spread of request seconds in the R8 item 6 session (max/min − 1 over its 5 runs, 12 for the soaks; the audit §5 P6): `⟦MAC: C5 sizing per sub-pack⟧`. Fixed packs bypass block 6's 265-minute science cap; s4 is planned at 103.617 + 150.0 = 253.617 min, 11.383 min under the cap on planning numbers only (Addendum 5 item 5).

**Gates set from the laptop measurements** (R6, R8 items 6 and 7):
- **Contention level.** Block 6's quarter-floor rule gives a power limit P_limit = F_min / (4 · T_max) for a background process, where F_min is the smallest detection floor (J) and T_max the longest phase (s) of the regime; it is derived in R6 and gives milliwatts for minute-long phases. It is computed per regime from measured floors before registration: `⟦MAC: P_limit per regime⟧`. If it is below what the contention census can measure, contention is recorded as a flag only, and this text says so: `⟦MAC: contention measurable or flag only⟧`.
- **Clock gate.** Re-derived from measured stream lengths. If the 70B's limit is below the live frequency word, s5 arms only when the measured word clears its own gate (a physical check, waited out): `⟦MAC: clock-gate values⟧`.
- **Disk.** Before arming, free space is checked against the measured per-session footprint plus a 150 GiB reserve. The reserve is operational (block-6 design §15: keep free disk above 150 GiB when downloading large models), not a derived quantity: `⟦MAC: per-session disk footprint⟧`.
- **Identity pins (C4).** Each model's files are pinned by hash. The model sources are Hugging Face cache snapshot directories, whose files are symbolic links, so the pins hash through the links (Addendum 5 item 5): `⟦MAC: C4 pins⟧`.

## 6. What counts

**Flags and exclusions.** A **flag** is a recorded code on a run or session. Block 6's flag catalog (`configs/b6/flag_catalog_b6.json`, 263 codes) is used with four BYTES disclose-only codes added by the B6 and BAT-2 rulings (`bytes.withheld_missing`, Q1; `bytes.module_changed_after_commitment` and `bytes.commitment_not_rebuilt`, Q2; `bytes.decode_battery_assist`, BAT-2) and otherwise unchanged, including its non-thermal exclusions (Addendum 2). Each code has one effect: 41 exclude the run (`EXCLUDE_MEMBER`), 19 exclude the session (`EXCLUDE_WINDOW`) and 203 are disclosed only (`DISCLOSE`); Appendix A lists the 60 excluding codes. Thermal pressure above 0 excludes the run (`thermal.os_level_nonzero`, `thermal.powermetrics_pressure_elevated`; R6). New catalog codes take their catalog effect (Addendum 2). Each pack registration carries the full code-to-effect map as `flag_effects`.

**Units, not runs** (Addendum 4 item 1). A run that the harvest excluded, or one without a usable record (missing bundle, output count not 512, non-finite or missing decode energy, re-reduction not succeeded, no decode timing envelope), removes its whole unit: the repeat, or all four runs of its quad. This never stops a stage. A stratum with fewer than **5 kept units** makes that cell unavailable (printed with its reason). *Source of 5:* block 6's detection-floor guard factor g(n) = √(9 / (n − 1)) is defined only for n ≥ 5 (block-6 registration §9.2 and its threshold row N3, code `cell.below_minimum`); BYTES inherits the minimum unchanged (`cell_unit_minimum: 5`, `joulewise/b6/registration.py`). A run whose DC-input value is unavailable removes its unit from the DC-input and rest cells only; rails selection never changes for missing meter data.

**Flagged-inclusive line** (Addendum 1 item 3, Addendum 2, Addendum 3 item 8, Addendum 4 item 6, Addendum 7 D5). Beside every primary line a second line restores every unit excluded by a catalog code, whatever its class (thermal, contention, battery, clock, the NUMBER class and the rest), provided each of its runs has a valid energy record. It never restores a run without one: harvest status not succeeded, a missing or unreadable bundle, a strict-validity failure or a token-count mismatch. It is labelled and decides nothing.

**Draft revision 2026-10-22 (F15).** `member.anchor_not_bounded` is an invalid energy record: a fallback or unresolved clock anchor cannot bound placement of the decode phase, so neither selection restores it.

**Battery assist.** When the laptop draws more than its 140 W adapter delivers, the battery supplies the difference
while the adapter stays connected. The meter on the adapter's cable does not see that energy, so DC input adds it
back (§7, "Battery term"). Assist is disclosed, not excluded (R3; the battery-assist ruling of 2026-10-06), because
removing assisted runs would select runs by load.

The laptop reports its battery current up to a delay τ late (§7). So a run is **decode-assisted**
(`bytes.decode_battery_assist`, disclose only) when a meter poll received between τ after its decode start and τ
after its decode end reports a battery current below 0 mA. The rule is "τ after": a reading in the first τ of
decode can describe the prefill, and a reading up to τ after decode can describe the decode.

For every cell that holds a decode-assisted run, block 5's registered without-assisted line is printed beside it:
the same estimator over the units with no decode-assisted run, labelled as description (Addendum 7 D10). Printed
with it, per stratum, are the count of decode-assisted runs and the count of runs carrying the harvest's
request-level `battery.assist`. Below 5 units the line prints its counts and "below the registered minimum of 5
units".

The marker is read from the meter stream, so only the stages that read that stream evaluate it. A stage that
reads no meter stream (the blinded stage, §11) prints the count of decode-assisted runs and this line's numbers as
null, labelled "not evaluated at the blinded stage", never as 0. The count of runs carrying `battery.assist`,
which comes from the harvest's flags, is printed at every stage.

*Expected, from the non-claim check session H (2026-10-21):*
- Llama-3.3-70B: 1 decode-assisted run of 18 (0.40 J, a run the harvest excluded for an agent's presence).
- Qwen3.5-122B: no decode-assisted run, but 0.56 to 1.15 J of battery energy in every full-length run, all of it
  from meter polls received in the first 1.93 s of decode, and within its edge term v.
- Every model at or below 32B: 0 J.

## 7. Quantities per model and boundary

**The cell estimate** (R3; the block-5 plan §4, unchanged, through Addendum 1 item 1's equivalence test against the block-5 library on every input it accepts, integers kept exact as the library keeps them, Addendum 4 item 12). For one model, pass and boundary, over the kept units:
1. **Mean.** m = 0.2 × (mean of the kept repeats' decode energies) + 0.8 × (mean of the kept quads' four-run means). With all 20 units kept this equals the plain mean of the 50 runs, because 10 of the 50 runs are repeats and 40 are quad members.
2. **Variance.** V = 0.04 × s_r² / n_r + 0.64 × s_b² / n_b, with s_r and s_b the sample standard deviations (divisor n − 1) of the kept repeats and of the kept quad means, and n_r, n_b their counts.
3. **Statistical half-width.** h = t × √V, where t is the Student-t quantile at 1 − 0.05 / (2 × 21) with min(n_r, n_b) − 1 degrees of freedom (the Bonferroni widening of §10; it widens h only). At 9 degrees of freedom t = 4.1786 (computed with `joulewise.analysis_engine.distributions.student_t_quantile`), against block 5's 2.2622 at 0.975.
4. **Bound B**, the sum (`math.fsum`) of three stratified averages, each 0.2 × (mean over kept repeats) + 0.8 × (mean over kept quad members), of per-run timing and drift terms. By boundary:

   | Term | rails | DC input | rest |
   |---|---|---|---|
   | phase-edge timing | the run's rails anchor-shift bound (block-5 plan §4 step 4, its first kind, re-derived under the session's operative timing bound from `joulewise/b6/calibration.py`; Addendum 1 item 4) | u + v, the meter and battery edge terms below (Addendum 1 item 2; BAT-2 ruling) | rails anchor-shift bound + u + v |
   | interpolation | the run's rails joint-edge interpolation bound (identically 0 for interval-support traces, and required to be 0) | 0 | as rails |
   | drift | ½ × A_rails × scale | ½ × A_DC × scale (Addendum 7 D2) | ½ × A_rest × scale (Addendum 7 D3) |

5. **Interval.** m − h − B to m + h + B, in that order, not clamped at zero (block-5 plan §4 step 5).

**Meter edge term u** (Addendum 1 item 2, Addendum 4 item 10, Addendum 7 D4). The meter's energy over the decode span is its power integrated over that span after mapping the meter's clock to the laptop's monotonic clock (`joulewise/external/km003c_parse.clock_fit` and `integrate`, computed in the analysis, not the harvest; R3). Per run, u = (P_start + P_end) × (r_max + Δt), where P_start and P_end are, at each phase edge, the larger power of the two meter samples adjacent to the edge, r_max is the largest absolute recorded excess latency of the clock fit (an edge can move either way; Addendum 7 item 12) and Δt is the meter's sample interval read from the stream header (`km003c_parse.STEP_MS`; 100 ms at the 10 Hz rate). The stratified mean of u + v enters B as shown; the largest u + v over the kept runs is printed as the cell's **meter attribution floor** and not added again. Phase edges map to integer nanoseconds by rounding to nearest (Addendum 7 item 11; Addendum 8 item 2 withdrew it as a ruling item: either rounding is acceptable, and round-to-nearest stays because it is done). A stream without a clock fit gives no DC-input value for that run, flagged `bytes.meter_decode_unavailable`; there is no fallback to the hazard journal (Addendum 3 item 10). **Rest** for each run is its DC-input energy minus its rails energy, formed per run before any averaging.

**Battery term and its edge term v** (BAT-2 ruling).

*The term.* Each meter poll, five a second, also carries the laptop's latest published battery current B0AC (mA,
negative while the battery discharges) and battery voltage B0AV (mV). At a poll, the battery's power into the
machine is P_b = −B0AC × B0AV / 10⁶ W. It is positive while the battery discharges and negative while it charges
(`km003c_parse.Stream.battery_watts`). Over a span [start, end) of length T that holds n polls, the battery energy
is E_b = (T / n) × Σ P_b over those polls. This is the mean-times-length rule that `km003c_parse.integrate`
applies to the meter, and that blocks 5 and 6 apply to these polls (`delta_machine_energy`).

DC-input energy over a span is the meter's energy plus E_b over the same span. The idle-subtracted basis subtracts
the idle span's mean P_b × T, as it subtracts the meter's idle power. The NEG-8 reference runs' DC-input and rest
energies, which set the drift allowance, include E_b over their request spans in the same way.

*Why it needs an edge term.* The laptop's system controller publishes B0AC and B0AV once a second (T_SMC = 1.0 s;
on H the median interval between changes of the published pair was 1.002 s). Each reading averages the second
before its publication, and it stays current until the next publication. A poll then sees it up to one poll
interval later. So battery energy is reported up to τ = 2 × T_SMC + Δt_p late, and never early. Δt_p is the
stream's largest interval between polls (H: 0.302 s, so τ = 2.302 s). On H, after the prefill-to-decode power step
of every Qwen3.5-122B run, discharge readings continued for 1.20 to 2.13 s.

*The edge term.* Per run, v = v_start + v_end, where v_edge = (T / n) × Σ |P_b| over the polls received in
[edge, edge + τ). At the start edge, v_start is all the battery energy the term counted that may be the prefill's.
At the end edge, v_end is all the decode energy that may have been reported after the span.

*Where it enters.* v is added to u in B (table above). The largest u + v over the kept runs is the cell's meter
attribution floor. Beside DC input and rest are printed the battery term's stratified mean and largest value, the
count of runs with a nonzero term, and the largest v.

*Missing readings.* A run whose decode or idle span holds no poll with both readings has no DC-input value
(`bytes.meter_decode_unavailable`, reason "battery reading missing").

*Per-phase definitions registered elsewhere* (third dispatch). This amends the last sentence of Addendum 1 item 2.
Block 5 or block 6 may later register a per-phase whole-machine energy (block-6 slot S-15). If one is registered
before this registration, BYTES adopts its treatment of the meter's phase edges and clock, as that sentence says.
BYTES' DC input and rest keep the battery term as defined here, whatever that definition says about the battery.

**Drift allowance** (Addendum 3 items 1 and 2, Addendum 4 item 7). A_β is the session's **NEG-8 drift allowance** on boundary β, computed from that session's reference runs exactly as the block-6 registration §1.8 defines it: from the clean corpus (the first 12 valid corpus runs; at least 6 required) the count-adjusted bound bound(n_s, n_e) = max(envelope, t × s × √(1/n_s + 1/n_e)) (`joulewise.whole_window.neg8_count_adjusted_bound`, with block 5's three-decimal t table `aggregate.student_t_critical_95`, Addendum 7 D8), and A = max(bound, largest minus smallest of the start-triplet mean, midpoint energy and end-triplet mean). At least 2 surviving start and 2 surviving end references are required. Each run carries ½ × A, as in blocks 5 and 6 (block-5 plan §4 step 4; block-6 registration §1.8: "Each run carries half of it into its cell's bound B (§9.1), so a contrast carries it once"). Rails reference energies come from the export; DC-input and rest reference energies come from the references' released meter spans over the whole request. Each boundary and each basis (gross, idle-subtracted) has its own allowance.

**Scale** (R3; block-6 design §14; Addendum 3 item 2). The drift allowance was measured on 37 J reference requests; BYTES decode phases are larger. Until **test 7** (the drift-transfer test: the largest planned workload alternated with the reference at the start and end of a session, about 16 minutes per regime; block-6 design §14) passes for a regime, the allowance is scaled by scale = max(1, E / E_ref, T / T_ref), where E is the cell's gross decode m on that boundary, E_ref the mean gross energy over the whole request of the session's kept start, midpoint and end references on that boundary, T the cell's stratified mean decode duration and T_ref those references' mean whole-request duration. The idle-subtracted basis uses its own allowance with the gross scale. Once test 7 passes for the regime, scale = 1. Test 7 outcomes: `⟦MAC: test 7 per long regime⟧`.

**Idle-subtracted secondary basis** (R3, Addendum 4 item 7, Addendum 7 D6). Primary energies are **gross** (the machine's idle power is not subtracted). A labelled secondary basis subtracts from each run's decode energy that run's own idle-baseline mean power on the same boundary times its decode duration. It uses the idle-subtracted family's own allowance. Negative values are kept.

**Per model, combining passes** (Addendum 3 item 5, Addendum 4 item 4, Addendum 7 D9 and item 12). With two computed passes, a model's point is E = the mean of the passes' m, with half-width the mean of the passes' (h + B); h is not pooled, because B dominates and does not shrink with passes. Each pass's value, their mean and their difference are printed, and per-pass words are printed as description. **One-pass fallback** (Addendum 7 D9, decided before any data so that it is not a choice made after seeing them): (a) if one pass of a model refuses, or its withheld file is missing (§11 item 4), and the other computes, the model's point is the surviving pass, with its own (h + B), labelled `one_pass` wherever it appears, and H1 and H2 use it; (b) if both refuse, the model has no point and no H1 word, the refusal is printed, and H2 is fitted on the models that have points and labelled with their number n; (c) wherever (a) or (b) applies, H2 is also printed over the models with two passes as a labelled sensitivity line.

**Derived quantities** (R3, Addendum 5 item 4, Addendum 7 item 12). With T the model's stratified mean decode duration (mean over passes):
- e = E / 512, per decode forward pass, with interval (E − h − B) / 512 to (E + h + B) / 512;
- τ = T / 512;
- b and R in GB from the manifest;
- P̄ = E / T, mean decode power, with half-width (h + B) / T (for two passes: mean E / mean T, and (mean h + mean B) / mean T);
- BW = b / τ = b × 512 / T, effective bandwidth in GB/s.

## 8. H1: frozen rival lines

For each hypothesis x in {b, R, τ}, an **OLS line** (ordinary least squares: the straight line minimising the sum of squared vertical distances) e = a + s · x is drawn through the three fit-set points (x_i, e_i) (R5). Its **prediction interval** at a held-out model's x_j is the range of the predictions at x_j of the 2³ = 8 lines drawn through every combination of the fit points' interval endpoints (each fit point at its lower or its upper end). Hypothesis x is **consistent** for held-out model j when j's measured interval and x's prediction interval overlap.

**Word per held-out model and boundary:** `bytes`, `resident` or `time` when exactly one hypothesis is consistent; `unresolved` when two or more are; `neither` when none is. For every model and hypothesis, whatever the word, ln(e_measured / e_predicted) is printed (null, with status `undefined_nonpositive`, when either value is not positive).

**Active or resident.** Over the three MoE models: `active` if `resident` is inconsistent on all three with its prediction interval above the measured interval each time; `resident` if `bytes` is inconsistent on all three with its prediction interval below the measured interval each time; otherwise `mixed`, with each model's misses printed (R5).

*Worked example (synthetic numbers, not measurements).* Fit points use the pilot's b, R and decode time (b = 1.2322, 2.6027, 4.5974 GB; R = 0.9680, 2.2629, 4.6077 GB; τ = 2.37/512, 4.48/512, 7.70/512 s) with invented e = 0.030, 0.045, 0.066 J ± 0.001 J. The bytes line is e = 0.016966 + 0.010685 · b. A held-out model with the 30B-A3B's pilot regressors (b = 1.9378 GB, R = 17.1746 GB, τ = 0.010840 s) and an invented measured e = 0.038 ± 0.001 J gets prediction intervals bytes [0.036672, 0.038672], resident [0.181187, 0.197589] and time [0.050714, 0.052714] J; only bytes overlaps [0.037, 0.039], so the word is `bytes`, and ln(0.038 / 0.037672) = 0.0087. (Computed with `joulewise.bytes_analysis.freeze_lines` and `h1_point`.)

## 9. H2: power against bandwidth

All fits are OLS over models, on each boundary and basis (R5, Addendum 3 item 6, Addendum 4 items 2 and 5):
- **Simple:** P̄_i = P₀ + ε · BW_i over all models; ε in J/GB, P₀ in W.
- **Resident-extended** (its ε is primary): P̄_i = P₀ + ε · BW_i + ρ · (R_i / τ_i). "Resident adds nothing" when ρ's interval contains 0 or ρ ≤ 0.
- **Tier fit:** the same two-term fit over the six Qwen3-family 4-bit models only (1.7B, 4B, 8B, 14B, 32B, 30B-A3B). Each non-tier model (Llama-70B, Next-80B, Qwen3.5-122B, 8B-8bit) is printed as a signed **deviation** from that tier line, in W, with its interval.
- **Rest boundary** adds: P̄_rest,i = c + ε_rest · BW_i + λ · P̄_rails,i. The **variance inflation factor** VIF = 1 / (1 − r²), with r the correlation of BW and P̄_rails over the fitted models, is printed beside λ and ε_rest (Addendum 3 item 9, Addendum 4 item 9). No word is drawn from λ or from c: with VIF 3.4 × 10⁶ in the synthetic worlds, input noise of 3 × 10⁻¹⁰ moved c by 6%, so c is not identified (Addendum 8 item 6).

**Standard errors** (Addendum 4 item 5, Addendum 7 D1). Errors in P̄ scale with P̄ (2 to 29 W across models), so equal-variance OLS errors understate the spread (plain-95% coverage was 0.80 in the resident world). Primary intervals use **HC3** errors (a heteroscedasticity-robust "sandwich" covariance in which each squared residual is divided by (1 − leverage)²) with Student t at n − p degrees of freedom, n models and p coefficients, at the Bonferroni level of §10. The OLS standard error is printed beside each, labelled. Each fit prints n, p and df; a fit with n − p < 2 is printed as refused, with no primary interval (Addendum 7 D9 (b)).

**Deviation interval** (Addendum 3 item 7, Addendum 4 item 3, Addendum 7 D1). For a non-tier model at regressors x = (1, BW, R/τ): t × √(MSE + xᵀ Σ x) + (h + B) / T, where MSE is the tier fit's residual mean square, Σ its HC3 covariance and (h + B) / T the model's own measured half-width of P̄; both parts are printed. A deviation compares two uncertain quantities, so both uncertainties enter.

**Meter label-offset alternative** (Addendum 9). The meter's clock is mapped to the laptop's by the earliest-arrival envelope, which labels a sample no earlier than it was digitised, so any constant meter-to-host label offset δ ≥ 0 shifts every decode window by δ in the same direction. Each model's DC-input energy then changes by about δ × (prefill-tail power − decode-tail power), coherently across models, which the per-run term u (§7) budgets inside each cell but the H2 coefficient intervals do not carry. Beside every H2 coefficient at DC input and rest a labelled alternative interval is printed: β_j ± (t × SE_HC3,j + C_j), where, with A = (XᵀX)⁻¹Xᵀ the matrix that maps the model points to the coefficients (β = A·y), C_j = Σ_i |A_ji| × [max(P_start,i, P_end,i) × (r_max,i + Δt) + max(v_start,i, v_end,i)] / T_i, using §7's edge powers, r_max and Δt and the model's decode time T_i, each pass's term averaged over the available passes as B is (no shrinkage, no t). That is, the per-run term max(P_start,i, P_end,i) × (r_max,i + Δt) + max(v_start,i, v_end,i) is in joules, averaged over passes, and divided by the point's mean decode time, the same ratio of means as the point's power. The time factor (r_max + Δt) is u's own, so no constant is new. The battery reading's delay is one-signed, like δ, so it also moves every model's DC-input energy the same way; the edge with the larger v enters, as the edge with the larger meter power does. Zero and sign statements at DC input and rest, including "resident adds nothing", print the decision under both intervals. Rails has no C term, and the other parts of B (drift allowance, rails anchor, h) are not propagated, because no coherence across models is established for them. The registered interval above is printed first and is the one the family of §10 counts. *Disclosure printed with the H2 DC-input and rest table:* δ has not been measured (block-6 M13); its structural bound is one sample period plus the poll round trip, 22 to 25 ms on the recorded 50 SPS streams; and the sensitivity dβ_j/dδ = Σ_i A_ji × (P_before-start,i − P_before-end,i) / T_i is printed in J/GB per ms, so a later measurement of δ applies without a new rule. *Why:* on synthetic campaigns with a generic sample phase and a 10 ms offset, the registered resident-extended DC and rest intervals covered the true zero in 0.65 of campaigns at plain 95% (0.30 at 20 ms), and the alternative covered in all 240 (B2 NR1 cold judge, section 2.6).

**Coverage check** (Addendum 4 item 5). The coverage harness draws 400 synthetic campaigns per world (`docs/contracts/bytes_tables.md`, round-2 record); the threshold for HC3's plain-95% coverage is 0.93, the binomial two-standard-error floor 0.95 − 2 × √(0.95 × 0.05 / 400) = 0.928, rounded (the audit §5 P4, supplying Addendum 4 item 5's missing derivation). Results per world, HC3 and OLS, plain-95% and at the ruled k: `⟦B2: coverage table (count of 400 and fraction)⟧`. If HC3's plain-95% coverage is below 0.93 in any world, the method is not changed here; the lead rules (Addendum 4 item 5).

Leave-one-out predictions of the simple fit (each model predicted from the others) are printed as description (R5).

## 10. Multiplicity

The pack's family of inferences is the H1 consistency checks plus the H2 intervals printed as primary, protected **familywise** (the chance of any false statement in the family at most 0.05) by **Bonferroni** (each of the k statements at level 0.05 / k) within the pack, as DIFFICULTY does (R5). The systematic term B is never widened.

- **H1:** k = 21 per boundary: 7 held-out models × 3 hypotheses (R5). Each fit-set and held-out h uses t at 1 − 0.05 / (2 × 21) = 1 − 0.0011905. If 8B-8bit is dropped, k = 6 × 3 = 18 (§2; decided by R5's definition of the family, not by data). At the expected sizes h is about 0.1% of the energy and B dominates, so the widening costs almost nothing (R5).
- **H2:** per boundary, the primary intervals are simple ε; extended ε and ρ; tier ε and ρ; one deviation per non-tier model present (up to 4); and on rest, ε_rest and λ. With all ten models k = 9 for rails, 9 for DC input and 11 for rest (Addendum 3 item 6, Addendum 4 item 2); with 8B-8bit dropped, 8, 8 and 10. P₀ and c are printed and not counted. H2's intervals use t at 1 − 0.05 / (2k) with the fit's n − p degrees of freedom. When D9 applies, k is counted from what is printed as primary (Addendum 7 D9); a refused tier fit refuses its deviations; the two-pass sensitivity line reuses the primary k and adds nothing to it.

At full roster, for reference: H2 rails simple fit (k = 9, df = 8) t = 3.7586; extended (df = 7) t = 3.9467; tier (n = 6, p = 3, df = 3) t = 7.1849; rest fit (k = 11, df = 7) t = 4.1048 (same quantile function as §7).

## 11. Blinding and two-stage unblinding

**Hidden offsets** (block-6 design §16 item 3; Klein and Roodman, Annu. Rev. Nucl. Part. Sci. 55, 2005). At harvest, every science energy and power column of a pack is multiplied by a secret **pack factor** drawn once, uniform on [0.8, 1.25], and each configuration's by a secret **configuration factor** near one, uniform on [0.97, 1.03] (`joulewise/b6/blinding.py`). The factors are stored once (file mode 0600, created exclusively) and divided out at release. All twelve BYTES packs share one **blinding group** `bytes`, so one pack factor (R5; R8 item 7, C6): `⟦B4: group key location⟧`.

**Why held-out rows are withheld** (lead's ruling of 2026-10-20, two blind seats agreeing). Every H1 word is unchanged when all energies are multiplied by one common factor, because the lines, their prediction intervals and the measured intervals scale together; so only the configuration factor hides the words. Configuration ratios stay visible to about ±6% (two independent factors on [0.97, 1.03] can differ by a ratio of up to 1.03 / 0.97 = 1.062), while the MoE hypotheses differ by factors of 8 to 19 (§1). The active-or-resident answer would therefore be readable from a blinded export before the predictions are committed. The ruling, which this text states and does not re-rule:

1. A held-out configuration's rows never enter the analysis export before the stage-1 hash is recorded. They are written, already blinded, to a **withheld store** under the pack group's records root (`⟦B4: withheld store path⟧`); the export's sidecar records only the counts and key digests of withheld rows.
2. **Timing closure.** Rows visible before the stage-1 commit carry no `run_start_utc` or any other clock, because gaps between reference runs would reveal a withheld module's duration. Any ordering the analysis or the twin needs uses the registered pass identity (pass id, position in the registered plan tree), not clocks.
3. Before the stage-1 commit, the blinded agreement between the analysis and the twin (§12) covers the fit set, the references and NEG-8 on real data; the held-out code paths are exercised on production-shaped synthetic campaigns. After the stage-1 commit and before held-out keys are released, both implementations run on the real held-out blinded rows. No sealed pass/fail agreement script is built.
4. A missing withheld file is never a refusal (project doctrine: only a physical hazard refuses; everything else is a recorded flag). A withheld file covers one session, so its absence removes every held-out run of that session as a run without a usable record (§6, Addendum 4 item 1): each unit is removed, the pass's cell is unavailable, flagged `⟦B4: flag code⟧`, and prints `missing` with the sidecar's withheld row count. The model then follows §7's one-pass fallback: when its other pass computes, the model's point is that pass, labelled `one_pass` and carrying the flag, and H1 and H2 use it (Addendum 7 D9 (a)); when both passes are missing the model prints `missing`, has no point and no H1 word, and H2 follows D9 (b) and (c). No stage refuses for a missing file, including the blinded post-commit agreement run. (Lead ruling, activation af419b16, `docs/process_traces/2026-10-20-magistrate-af419b16/B6-RULING.md` Q1.)
5. Wider blinding factors are rejected.
6. This section's agreement statement (§12) replaces Addendum 7's "including the blinded one" for held-out models.

**Known limitation, queued separately for every block-6 pack.** The exported idle power `idle_power_w` is scaled by the configuration factor, so its ratio to the reference rows' idle power estimates that factor. This round does not change idle-power handling (lead's ruling, "out of scope"). Under item 1 it can be read only from rows already visible, that is the fit set's and the references'.

**Stages** (R5, Addendum 3 items 1 and 4, Addendum 4 item 8; the command is `scripts/bytes_analyze.py`; releasing a configuration means placing the group's pack key and that configuration's key in the release directory the analysis reads; the analysis never reads the exporter's private key directory and never draws a key):

| Stage | Command | Keys released before it | What it computes |
|---|---|---|---|
| blinded | `--stage blinded --export DIR` | none | Rails only, from the blinded export's columns (no archive, key or meter reads): fit set, references and NEG-8 inputs. No DC-input or rest number: the raw meter stream carries no hidden offset (Addendum 3 item 4). This is the input to the blinded agreement. |
| 1 (fit) | `--stage fit` | the fit set's three configurations and `neg8_reference` (Addendum 3 item 1) | Fit points on all three boundaries, the rival lines and their corner lines, and the tier inputs of the fit models only (Addendum 4 item 8(e): the six-model tier fit is completed after held-out release). Only meter samples inside fit-model and reference spans are parsed; a held-out configuration's raw meter samples are not loaded (Addendum 4 item 8(c)). The meter join refuses a configuration whose key has not been released; release is read only from the key directory, never from the manifest's `synthetic` field or an export's `non_claim` column (Addendum 4 item 8(b), Addendum 7 D7). |
| commitment | — | — | `predictions.json` holds the schema `joulewise.bytes_predictions.v1`, the manifest's SHA-256, the SHA-256 of `joulewise/bytes_analysis.py` (Addendum 4 item 8(d)), the NEG-8 inputs, the fit points, the rival lines, the fit-model tier inputs, the H1 and H2 family sizes and the dense-linearity note; `predictions.sha256` holds the hash of that exact file. Both are committed in git, and the hash recorded, before any held-out row enters the export (ruling item 1). Only the analysis's commitment is the registered one (Addendum 7 item 14). The commitment is its content; the module digest it carries is provenance (§13). |
| held-out agreement | both implementations, blinded | none further | Ruling item 3: the analysis and the twin run on the real held-out blinded rows, now moved from the withheld store into the export. A difference above §12's bar is attributed, as in Addendum 7, before any held-out key is released. If the attributed difference is a defect in `joulewise/bytes_analysis.py` (its arithmetic differs from this text, R5, the Addenda, or the block-5 equivalence of Addendum 1 item 1), the fix restores the registered arithmetic and does not change it. The fix is complete when its diff is limited to the attributed difference and both implementations agree again at §12's bar on the same blinded held-out rows and on the synthetic campaigns. The stage-1 commitment is not withdrawn, re-signed or edited: it is the registered commitment, and stage 2 evaluates its committed content (fit points, rival lines, NEG-8 inputs, tier inputs, family sizes, manifest digest) as committed, by the fixed module; the module digest it carries is provenance (§13), not a condition of evaluation, and the committed module is not run for the record. Before the stage-2 release, the fixed module writes a second commitment by `--stage fit` from the same stage-1 inputs into a fresh directory. It is committed in git as a descendant of the fix commit, labelled `post-agreement fix`, with the first commitment's SHA-256, both module digests, the attributed difference, and the statement that it was written after both implementations had run on blinded held-out rows. The stage-2 release record names that commit (`⟦B4: --stage1-commit⟧`). The record prints one table: for each commitment its predictions SHA-256, module SHA-256, git commit and label, and the fields in which the two files differ (exact equality; the module digest always differs). Stage 2 runs on each commitment into its own directory. The run on the first commitment is the registered result; its record carries `bytes.module_changed_after_commitment` with the committed and evaluating digests, and `bytes.commitment_not_rebuilt` with the field names when the committed lines or tier inputs no longer rebuild from the committed fit points under the fixed module. Both flags are disclose-only. The run on the second commitment is the labelled alternative. When the two files differ in the module digest only, the two runs are identical and the record says so in one sentence. When they differ in content, every word, interval and answer of the alternative is printed beside the registered one, and a word that differs is reported, not chosen. Where the first commitment's content cannot be evaluated (a committed line group is null), the registered result prints unavailable with its reason, beside the alternative. The twin's comparer compares the record's flags, digests and field list exactly (Addendum 8 item 5). (Cold judge Fable 5.1, adopted by the lead, activation af419b16: `docs/process_traces/2026-10-20-magistrate-af419b16/B6-RULING.md` Q2.) |
| 2 (held-out) | `--stage heldout --predictions FILE` | every held-out configuration | Checks the prediction file's hash, manifest and frozen inputs before opening any held-out record; then H1 words, the active-or-resident answer, every H2 fit and the per-pass description. |

The stage names are the CLI's (`blinded`, `fit`, `heldout`); `all` runs fit and held-out in one process and is refused on non-synthetic inputs. The paper says "predictions were committed before the held-out energies were unblinded", not "before they were measured" (R5).

## 12. Agreement between the two implementations

The analysis (`joulewise/bytes_analysis.py` with `scripts/bytes_analyze.py`) and an independent **twin** (`scripts/bytes_twin.py`, written from the ruling alone and sharing no code with the analysis; R8 item 4) compute the same tables from the same inputs. They **agree** (Addendum 8 item 1) when every word, k, df, n, refusal, label and exit code matches exactly, and every number matches within 1% of its cell's half-width:
- energies within 1% of the cell's (h + B);
- P̄ within 1% of its half-width (h + B) / T;
- H2 coefficients within 1% of their HC3 half-width;
- durations within 1 ms; VIF to 2 significant figures;
- any other quantity without a half-width, at its printed precision (§14).

A difference under the bar is printed as one count per campaign and not classified. A difference above it is attributed and ruled before release, as Addendum 7 did. *Why this bar:* the instrument's attribution limit is about 1 J per run and the smallest printed half-width is 0.013 J (1.7B rails), so 1% of it (1.3 × 10⁻⁴ J) still lies above 10⁶ times float noise on the largest decode energies (10⁶ × 2.2 × 10⁻¹⁶ × 10⁴ J = 2.2 × 10⁻⁶ J, with 10⁴ J ≈ 64 s × 100 W for the 70B), while Addendum 7's 1 × 10⁻⁹ relative bar would fail on a harmless change of summation order (Addendum 8 items 1 and 3; the scales are the audit's §5). Method differences must not hide under the bar: the synthetic campaigns give the references' DC-minus-rails drift its own scale, at least 10% of each rest cell's B, so a rest-allowance method difference (D3) shows at about ten times the bar or more wherever B dominates h, as R5 expects; they keep unequal pass durations and signed clock latency on (Addendum 7 item 12); and the twin's unit test pins D8's t values (Addendum 8 item 4).

**What the agreement covers, by stage** (replacing Addendum 7's "including the blinded one" for held-out models; §11 item 6). Before the stage-1 commit: on real data, the blinded rails tables for the fit set, the references and NEG-8; on production-shaped synthetic campaigns (full-size modules, 50 runs per model per pass, start, midpoint and end references, a 10 Hz meter stream, run through the real harvest export and every CLI stage), every stage and boundary, including the held-out paths. After the stage-1 commit and before held-out keys are released: on real data, the held-out blinded rails tables. After each release: DC input and rest on the released configurations. The agreement test runs in the suite at this bar (Addendum 8 item 3); agreement on real data is recorded by the comparer, not by a sealed pass/fail script.

## 13. Estimators

One library (block-6 design §14): `joulewise.bytes_analysis`, entered through three functions, each named in every pack registration's `estimators`: `reduce_models` (the cells of §7), `frozen_predictions` (the stage-1 commitment of §11) and `evaluate` (H1, active or resident, and H2). Their version is the SHA-256 of `joulewise/bytes_analysis.py` at the commit where the twin agrees with it at §12's bar on the synthetic campaigns: `⟦B2: SHA-256 of joulewise/bytes_analysis.py at the agreeing pin⟧`. Until then each entry's `version` is null, which block 6's validator allows only in a draft. If `joulewise/bytes_analysis.py` changes after the stage-1 commitment (§11, held-out agreement), this version is not re-registered: every stage-2 record prints the evaluating digest beside the committed one under the flag `bytes.module_changed_after_commitment`.

## 14. Printed precision

Every printed number has a fixed number of decimals, set before data. Where §12 says "at printed precision", these are the decimals meant. **Rule:** one unit in the last printed digit is at most one tenth of the smallest half-width the column can carry, so rounding (at most half a unit) moves a value by at most 5% of any half-width. The smallest half-width is Addendum 8's 0.013 J (1.7B rails), and the 1.7B decode phase lasts about 2.37 s (pilot table, 512-token decode).

| Quantity | Unit | Printed | Derivation |
|---|---|---|---|
| E, m, interval endpoints, h, B, pass values and differences, attribution floors | J | 3 decimals (1 mJ) | 0.001 J ≤ 0.0013 J, a tenth of 0.013 J; matches block 6's 1 mJ per-run recompute tolerance (block-6 registration §12.3) |
| e and its interval, H1 predictions and prediction intervals, H1 line intercepts | J per decode pass | 6 decimals (1 µJ) | 0.013 J / 512 = 2.5 × 10⁻⁵ J; a tenth is 2.5 × 10⁻⁶ J ≥ 10⁻⁶ J |
| H1 line slopes | J/GB (b, R), J/s (τ) | 6 decimals | combine with x into e at the precision of e |
| T, decode durations | s | 3 decimals (1 ms) | Addendum 8 item 5 compares durations to 1 ms |
| τ | s per decode pass | 6 decimals (1 µs) | 1 ms / 512 = 1.95 µs; rounding τ (≤ 0.5 µs) stays below the duration's own rounding carried through the division (≤ 0.98 µs) |
| P̄ and its half-width | W | 4 decimals | 0.013 J / 2.37 s = 0.0055 W; a tenth is 5.5 × 10⁻⁴ W ≥ 10⁻⁴ W |
| BW, R/τ | GB/s | 3 decimals | rounding T to 1 ms (at most 0.5 ms) moves BW = b × 512 / T by at most BW × 0.5 ms / T, largest on the pilot numbers for 1.7B: 266 GB/s × 0.5 ms / 2.37 s = 0.056 GB/s; 0.001 GB/s is below a tenth of it |
| b, R in result tables | GB | 3 decimals | display only; arithmetic uses the manifest's integer bytes, printed in full in the manifest table |
| W, KV (occupied, allocated), R in the manifest table | bytes | integers, exact | counts of stored bytes (R4; the audit §5 P5); KV may end in .5 from the two-snapshot average and is printed so |
| ln(e_measured / e_predicted) | — | 4 decimals | a unit of 10⁻⁴ is a tenth of R5's "h about 0.1% of the energy" |
| H2 coefficients (ε, ρ, P₀, c, ε_rest, λ) and every H2 interval, HC3 and OLS errors | their units | the half-width to 2 significant figures, and the estimate, endpoints and errors to the same decimal place | a 2-significant-figure half-width is at least 10 units of its last digit, so the rule above holds per row |
| VIF | — | 2 significant figures | Addendum 8 item 5 |
| correlation r of BW and P̄_rails | — | 9 decimals | resolves VIF = 1 / (1 − r²) to 2 significant figures up to VIF ≈ 10⁷ (1 − r ≈ 5 × 10⁻⁸) |
| drift scale | — | 6 decimals | rounding (at most 5 × 10⁻⁷) moves the drift term ½ × A × scale by at most 2.5 × 10⁻⁷ × A, below a tenth of the 1 mJ energy digit for any allowance A under 400 J; the reference requests the allowance is measured on are about 37 J on rails (block-6 design §14) |
| coverage | — | count of 400, and the fraction to 4 decimals | the fraction is an exact multiple of 1/400 = 0.0025 |
| t quantiles | — | 4 decimals | display; the arithmetic uses the full value |
| k, n, p, df, unit and run counts, words, labels, hashes | — | exact | integers and labels; bit identity is the property |

JSON outputs keep full precision; these decimals apply to every printed table.

## 15. What is printed, in every outcome

Per model and boundary, on both bases and both selections (primary and flagged-inclusive): each pass's cell (m, h, B, interval, counts, removed units and their reasons, flags, drift scale and family, attribution floors, the battery term (stratified mean, largest, count of runs with a nonzero term) and the largest v beside DC input and rest), the pass mean and difference, e, τ, P̄, BW, b and R, and the pass status (`two_pass`, `one_pass`, `no_pass`). Cells that cannot be computed are printed as unavailable with their reason; they never stop the stage. Per held-out model: the H1 word, the three prediction intervals, the measured interval, consistency and the log ratios, then per-pass words as description; a pass whose withheld file is missing prints `missing`; a model prints `missing` only when both of its passes do (§11 item 4). Every stage-2 record prints the commitment it evaluated: its SHA-256, the committed and evaluating module digests, the commitment flags and the fields that did not rebuild (§11); when a second commitment exists, both stage-2 results are printed, the first as registered and the second labelled `post-agreement fix`. The active-or-resident answer with each MoE model's misses. Every H2 fit with n, p, df, status, k and the point labels; primary intervals with HC3 and OLS errors; tier deviations with both parts of their intervals; the rest fit with VIF and r; leave-one-out description; the two-pass sensitivity line when D9 applies; and, for cells with an assisted run, the without-assisted line. The sentence for dense held-out models: "Dense held-out models test linearity over the format-derived bytes range; their small rival splits do not identify the hypothesis." Per-token values carry the label "512 decode forward passes, one of which yields no returned token".

## 16. Dependencies

- **Other packs:** none of BYTES's numbers depend on another pack's results (`dependencies: []` in every pack registration). BYTES shares the reference workload with every block-6 pack (block-6 design §14) and is scheduled after replication round 1 (§5).
- **Harvest dependencies the analysis relies on, stated as Addendum 4 requires:** for battery assistance in decode, the meter stream's own battery readings, the same readings that make the battery term (§6, §7); the harvest's request-level `battery.assist` is counted only (BAT-2 ruling, which replaces Addendum 4 item 11's dependency); and the stage-1 tier inputs are the fit models' only, the six-model tier fit being completed after held-out release (item 8(e)). The analysis also reads the harvest's operative timing bound (`calibration.operative_bound_s` in `derived/b6-acceptance.json`, evaluated by `joulewise/b6/calibration.py`; Addendum 1 item 4) and never recomputes a calibration bracket.

## 17. Dissent recorded (R7)

- Sol: a two-coefficient H_B / H_R fit on the fit set only, without intercept. Not adopted as primary: on the fit set bytes and time are collinear (VIF 37,560, the ruling's preamble), so a two-coefficient fit there is unidentified; H2 over all models is where the MoE models give leverage, and the same conditioning is why H1 is three one-variable lines.
- Sol: runtime accounting added to `mlx_runtime.py`. Not adopted: the manifest gives the same regressors without touching measured code.
- Sol: three passes and separate calibration and validation registrations. Not adopted: they do not fit the date beside the replications, buy precision BYTES does not need (its limit is systematic), and would put held-out collection behind a release (R5, R6).
- Opus: a 0.95 interval per model. Not adopted: it would leave the family unprotected for no gain (R5).

## 18. Marked slots

| Slot | Where | Comes from |
|---|---|---|
| `⟦MAC: manifest SHA-256⟧`, `⟦MAC: manifest table⟧` (W, KV occupied and allocated, R per model) | §4 | R8 item 5 (KV generation on the laptop) and `scripts/bytes_manifest.py` |
| `⟦MAC: revision (R8 item 5)⟧` for 8B-8bit | §2 | R8 item 5 download |
| `⟦MAC: 8B-8bit kept or dropped⟧` | §2, §10 | R8 item 6 resolvability check |
| `⟦MAC: b range from the manifest⟧`, `⟦MAC: R range from the manifest⟧` | §2 | the frozen manifest (F15) |
| `⟦MAC: C4 pins⟧` | §5 | R8 item 7, C4 |
| `⟦MAC: P_limit per regime⟧`, `⟦MAC: contention measurable or flag only⟧` | §5 | R8 items 6 and 7, C5 |
| `⟦MAC: clock-gate values⟧`, `⟦MAC: per-session disk footprint⟧`, `⟦MAC: C5 sizing per sub-pack⟧` | §5 | R8 items 6 and 7, C5 |
| `⟦MAC: test 7 per long regime⟧` | §7 | R8 item 6 |
| `⟦MAC: known-bytes stream test outcome⟧` | §1 | R8 item 6 |
| `⟦B2: coverage table (count of 400 and fraction)⟧` | §9 | coverage harness re-run (Addendum 4 item 5) |
| `⟦B2: SHA-256 of joulewise/bytes_analysis.py at the agreeing pin⟧` | §13, and `version` in every pack registration's `estimators` | the analysis at the commit the twin agrees with (R8 items 3 and 4) |
| `⟦B4: catalog SHA-256 at the B4 merge⟧` — FILLED | Appendix A | SHA-256 recorded in Appendix A for `configs/b6/flag_catalog_b6.json` at the B4 merge |
| `⟦B4: group key location⟧`, `⟦B4: withheld store path⟧`, `⟦B4: flag code⟧`, `⟦B4: --stage1-commit⟧` | §11 | the blinding-group and withheld-store build (R8 item 7, C6 and C7) |

## 19. Before the first BYTES session

In order: every slot of §18 filled; the whole test suite run on the laptop before any BYTES lane merges into the release line, and not while measuring (Addendum 2); this registration's cold gate (R8 item 8); its commit before the first t0; then, for each sub-pack's first session, the smoke by fingerprint (block-6 design §13.1; R8 item 8).

## 20. Map from the ruling to this text

| Ruling item | Where |
|---|---|
| Preamble (pilot re-execution, MoE splits, VIF, stack check) | §1, §3, §17 |
| R1 question, roster, 8B-8bit, printed ranges, fixed words | §1, §2 |
| R2 workload | §3 |
| R3 quantities: E_dec, T_dec, e, τ, b, R, P̄, BW, DC input, idle secondary, battery | §6, §7 |
| R4 manifest | §4 |
| R5 H1, active or resident, dense note | §8, §15 |
| R5 H2 | §9 |
| R5 multiplicity | §10 |
| R5 two-stage unblinding, one blinding group | §11 |
| R6 modules, passes, sub-packs, interleaving, exclusions, flagged-inclusive, contention, clock gate, disk | §5, §6 |
| R7 dissent | §17 |
| R8 items 1-8 (build and measure list) | §4 (1, 5), §5 (2, 7), §12 (3, 4), §2 and §5 (6), §11 (7), §19 (8); slots §18 |
| Add. 1 item 1 (library equivalence) | §7 |
| Add. 1 item 2 (u) | §7 |
| Add. 1 item 3 (flagged-inclusive) | §6 |
| Add. 1 item 4 (operative bound) | §7, §16 |
| Add. 1 note (lanes carry main's docs commits) | merge record only; no registration content |
| Add. 2 (catalog unchanged; suite on the laptop before merge; launcher defect) | §6; §19; the launcher defect is tooling, no registration content |
| Add. 3 items 1-10 | §7 (1, 2, 3, 5, 10), §11 (1, 4), §9 (6, 7, 9), §10 (6), §6 (8) |
| Add. 4 item 1 (W1) | §6 |
| Add. 4 items 2, 3, 5 (S2, S3, N5) | §9, §10 |
| Add. 4 item 4 (S4) | §7 |
| Add. 4 item 6 (S6) | §6 |
| Add. 4 item 7 (S7) | §7 |
| Add. 4 item 8 (a)-(e) (S8) | §11, §16 |
| Add. 4 item 9 (S9) | §9 |
| Add. 4 item 10 (F10) | §7 |
| Add. 4 item 11 (N11 battery) | §6, §16 |
| Add. 4 item 12 (N12) | §7 |
| Add. 5 items 1, 2 | §5 |
| Add. 5 item 3 | §4 |
| Add. 5 item 4 (512 passes) | §3, §4, §7 |
| Add. 5 item 5 notes (snapshot symlinks, 8B-8bit group size, s5/s6 midpoint, 265-min cap) | §5 (symlinks, midpoint, cap), §2 (group size) |
| Add. 6 (1/1) | §5 |
| Add. 7 D1 | §9 |
| Add. 7 D2, D3 | §7 |
| Add. 7 D4, D5, D6 | §7, §6, §7 |
| Add. 7 D7 | §11 |
| Add. 7 D8 | §7, §12 |
| Add. 7 D9 | §7, §9, §10 |
| Add. 7 D10 | §6 |
| Add. 7 items 11 (N1), 12, 13, 14; "agree to 1e-9 … including the blinded one" | §7 (11, 12), §3 and §7 (13), §11 (14); §12 (superseded) |
| Add. 8 items 1-6 | §12 (1, 3, 4, 5), §7 (2), §9 (6) |
| Lead's blinding ruling of 2026-10-20, items 1-6 and the idle-power note | §11, §12 |
| Add. 9 (NR1, meter label offset; lead a017b694 adopting the cold judge) | §9 |
| BAT-2 ruling | Authority, §1, §6, §7, §9, §15, §16 |

## Appendix A. Excluding codes of block 6's flag catalog

From `configs/b6/flag_catalog_b6.json` (SHA-256 `33e1c6110d98474465109062cfcdff480679ba8b2c9854fc754fa26fa07bccb6`; it was `b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b` at the integration head `d924e7acf`, before the three disclose-only BYTES codes; the excluding codes below are unchanged), as copied into each pack registration's `flag_effects`. Every other code (203) is disclosed only.

**Exclude the session (`EXCLUDE_WINDOW`, 19):** `calibration.bracket_incomplete`, `calibration.capture_battery_pair_failed`, `calibration.capture_battery_span`, `calibration.capture_battery_unmeasured`, `calibration.operative_bound_above_stop`, `cell.below_minimum`, `clock.step_overlap_calibration`, `code.number_bearing_unreviewed`, `model.files_differ_from_registered`, `model.stack_differs_from_registered`, `neg8.survivor_screen_failed`, `neg8.survivor_screen_undefined`, `precheck.certain_exclusion`, `records.source_changed_during_harvest`, `roster.no_science_bundles`, `structure.chain_crashed`, `structure.missing_stage_bundles`, `structure.no_capture_records`, `structure.no_roster`.

**Exclude the run (`EXCLUDE_MEMBER`, 41):** `agent.presence`, `agent.presence_overlap`, `agent.unit_overlap`, `battery.accumulator_excursion`, `battery.capture_pair_failed`, `battery.member_span`, `battery.unmeasured`, `clock.step_overlap`, `contention.unmeasured`, `env.member_quiet_state_violated`, `idle.wait_budget_skip`, `idle.wait_cap_skip`, `instrument.cadence_ratio_below_threshold`, `instrument.insufficient_in_window_samples`, `member.admission_aborted`, `member.anchor_energy_envelope_exceeded`, `member.anchor_not_bounded`, `member.anchor_recompute_mismatch`, `member.bytes_ambiguous`, `member.bytes_missing`, `member.config_not_in_inventory`, `member.idle_admission_telemetry_missing`, `member.idle_window_suspect`, `member.reduction_mismatch`, `member.span_unknown`, `member.status_not_succeeded`, `member.strict_validation_failed`, `member.target_phase_precheck_failed`, `member.timeout`, `member.token_count_mismatch`, `member.unreadable`, `member.whole_window_member_failure`, `model.identity_underivable`, `roster.before_chain_started`, `roster.creation_unplaced`, `roster.foreign_attempt`, `roster.not_in_plan`, `roster.run_id_mismatch`, `sleep.in_run`, `thermal.os_level_nonzero`, `thermal.powermetrics_pressure_elevated`.
