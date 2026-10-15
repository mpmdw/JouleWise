# BYTES pack: design ruling (orchestrator, Opus 5.5, 2026-10-15 12:20 PDT, session e308c59a)

Two blind seats, both in the cloud: Sol 6.1 xhigh (Codex Cloud thread 01a140df-119c-717f-a8f2-bc472f8bc00e, model and effort
read back before the turn: `SEAT-sol.md`) and Opus 5.5 (Claude cloud session_01FtdX5KVC5CfJKSVeWrLjt4, `SEAT-opus.md`,
arithmetic in JouleWise-data branch `claude/bytes-design-opus` `design/bytes/calc/`). Brief: `brief-core.md`. No BYTES
energy exists; no block-5 number was opened by either seat or by me.

Lead re-execution (12:15): `calc/pilot.py`, `design.py`, `leverage.py` re-run locally, output identical to the seat's
tables: fit-set corr(bytes, time) 1.0000, VIF 37,560; MoE splits resident/bytes 8.42, 19.43, 12.20 and time/bytes 1.68,
2.22, 1.39; BW_eff sd 74.6 GB/s over nine models against 31.4 dense; prediction half-widths 5 to 9% at 5% fit-point
intervals. Stack check (Opus N4) resolved: the pilot ran in `/Users/edr/code/JouleWise/.venv` at mlx 0.31.2, mlx-lm
0.31.3, mlx-metal 0.31.2, which are exactly the pinned `runtime_versions`, and Qwen3-Next-80B and Qwen3.5-122B loaded and
ran there.

This ruling is the build spec until the registration (`docs/registrations/bytes_pack_v1.md`) replaces it; the
registration goes through its cold gate before the first BYTES t0.

## R1. Question and roster

Does decode energy per token follow the format-derived bytes the model reads per token (weights used per token plus
KV), the resident model size, or decode time? Roster, all MLX, pinned revisions recorded in the manifest (R4):

| Role | Models |
|---|---|
| Fit set | Qwen3-1.7B-4bit, Qwen3-4B-4bit, Qwen3-8B-4bit |
| Held out, dense | Qwen3-14B-4bit, Qwen3-32B-4bit, Llama-3.3-70B-Instruct-4bit, **Qwen3-8B-8bit** |
| Held out, MoE | Qwen3-30B-A3B-4bit, Qwen3-Next-80B-A3B-Instruct-4bit, Qwen3.5-122B-A10B-4bit |

Qwen3-8B-8bit is added (Opus N1, Sol's note that without it no quantization claim stands): same architecture and
kernels family as the fit-set 8B, about twice the bytes per token; the design's original BYTES question named it. Cost
about 150 min per pass and about 9 GB of download. If it fails the resolvability check (R8 item 5) it is dropped before
registration and the quantization sentence is deleted.

Printed range: "a 32-fold range of bytes read per token (weights plus KV), 69-fold range of resident size". The phrase
"two orders of magnitude" is not used (Opus N2, Sol 1.5); no 0.6B is added (its 1.5 s decode phase is where the timing
term is largest).

Words fixed for every printed line: **format-derived bytes** (from stored tensor sizes, never a memory-controller
count); boundaries **rails** (powermetrics CPU+GPU+ANE), **DC input** (KM003C, USB-C, after the adapter; never "wall"
or "AC"), **rest** (DC input minus rails, which includes DRAM, conversion losses, SSD, fans).

## R2. Workload

Each run: prompt of exactly 2,048 token ids built by `_synthetic_prompt_tokens` (`joulewise/adapters/mlx_runtime.py`,
exact for every tokenizer), then exactly 512 greedy tokens, temperature 0, EOS suppressed, one 4-token warm-up on the
same prompt and the existing settle. No runtime code change (Opus). Load is in `prepare`, outside the request; prefill
ends at the first token (`phase_boundary_method: first_token`); the decode phase holds 511 forward passes. Prefill
energies are recorded and not analysed.

## R3. Quantities (per model i, boundary β)

- E_dec,i,β: gross decode-phase energy, the registered per-phase estimate over the model's floor module,
  m = 0.2·mean(repeats) + 0.8·mean(null quads), interval m ± (h + B) with block 5's analysis-plan arithmetic
  (`configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`), the library function unchanged. The drift allowance is
  scaled by max(1, E/E_ref, T/T_ref) until test 7 passes for that regime (design section 14).
- T_dec,i: decode-phase duration (mean over the same units, same weights).
- e_i = E_dec,i / 511 and τ_i = T_dec,i / 511 (printed per output token as E/512 with the label "512 output tokens,
  511 generated in the decode phase"; arithmetic uses 511 consistently with bytes per decode step).
- b_i = W_i + KV_i from the frozen manifest (R4), GB per decode step. R_i: resident GB from the manifest.
- P̄_i = E_dec,i / T_dec,i; BW_i = b_i / τ_i.
- DC-input decode energy: meter energy over the decode span, mapped to CLOCK_MONOTONIC_RAW with
  `joulewise/external/km003c_parse.clock_fit` and integrated with `km003c_parse.integrate`, computed analysis-side
  (the harvest today integrates the meter over the request span only); its clock-fit uncertainty is carried separately
  from the powermetrics bounds. A run whose request shows battery assist is flagged, not removed.
- Idle: primary gross. Labelled secondary: gross minus each run's own idle-baseline mean power on that boundary times
  T_dec. Negative diagnostic values are kept.

## R4. The bytes manifest (frozen before the first BYTES session)

`scripts/bytes_manifest.py` writes `configs/bytes/bytes_manifest.json` per model: revision, tokenizer, k/E, shared
experts, tied embeddings; W = stored sizes including quantization scales of every dense weight used per token, one
embedding row, the whole output layer, k/E of routed expert weights plus shared experts; R = sum of loaded weight
storage. The safetensors-header part runs anywhere. KV comes from one MLX generation per model on the Mac without power
capture: KV = (cache bytes after prefill + cache bytes after the last token) / 2, recording occupied length and
allocated capacity separately and the cache class per layer (recurrent-state layers in Qwen3-Next and Qwen3.5 are
constant). `joulewise/kv_size.py` (all-full-attention assumption) is not used. The manifest prints its differences from
the pilot column.

## R5. Analysis (both primary; every line for rails, DC input and rest)

**H1, frozen rival lines.** For x in {b, R, τ}: OLS line e = a + s·x through the three fit-set points (e_i, x_i).
Prediction interval for held-out j: the range of the line's prediction at x_j over the 2³ lines through the corner
combinations of the fit points' interval endpoints. Hypothesis x is **consistent** for j when j's measured interval
meets x's prediction interval. Word per held-out model: `bytes`, `resident` or `time` when exactly one is consistent;
`unresolved` when two or more; `neither` when none. ln(e_measured / e_predicted) is printed for every model and
hypothesis whatever the word. "Active or resident" answer: `active` if `resident` is inconsistent on all three MoE
models with its prediction above the measured interval each time; `resident` if `bytes` is inconsistent on all three
with its prediction below; otherwise `mixed`, misses printed. Dense held-out models test the line's linearity over the
bytes range, not which hypothesis is right (their splits are 2 to 9%), and this is said in the text.

**H2, power against bandwidth.** OLS over all ten models: P̄_i = P₀ + ε·BW_i; ε in J/GB with its 95% interval (t, n-2
df) and P₀ in W. Resident-extended: P̄_i = P₀ + ε·BW_i + ρ·(R_i/τ_i); "resident adds nothing" when ρ's interval
contains 0 or ρ ≤ 0. Tier split: the same two-term fit over the Qwen3 family 4-bit models only (1.7B, 4B, 8B, 14B, 32B,
30B-A3B); Llama-70B, Next-80B, Qwen3.5-122B and 8B-8bit are each printed as a signed deviation from that frozen tier
line, with its interval. Rest boundary adds λ·P̄_rails: P̄_rest = c + ε_rest·BW + λ·P̄_rails. Leave-one-out predictions
are description.

**Multiplicity.** BYTES's family is the H1 words (7 held-out models × 3 hypotheses = 21 consistency checks per
boundary) plus the H2 intervals named above. Familywise 0.05 by Bonferroni within the pack, as DIFFICULTY does: the
statistical half-width h of each fit-set and held-out interval uses t at 1 − 0.05/(2·21) for H1, and H2's intervals use
1 − 0.05/(2·k) with k the number of H2 intervals printed as primary. The systematic term B is unchanged. At the expected
sizes h is about 0.1% of the energy and B dominates, so this costs almost nothing (Opus's 0.95-per-model recommendation
is not adopted; it would leave the family unprotected for no gain).

**Two-stage unblinding** (Opus decision 12, adopted over Sol's separate calibration-then-validation registrations,
which would push held-out collection behind a release and cost the 2026-11-01 date). All BYTES sub-packs share one
blinding group `bytes` (one pack factor). After collection closes and the analysis code and twin agree on the blinded
export, the fit-set configurations are unblinded, H1's lines and prediction intervals and H2's tier-1 fit inputs are
computed and committed (hash in the record), and only then are the held-out configurations unblinded. The paper says
"predictions were committed before the held-out energies were unblinded", not "before they were measured".

## R6. Collection

- One floor module (10 absolute repeats + 10 null ABBA quads, 50 runs) per model per pass; at least 5 kept units per
  stratum. A pass is the six sub-packs below plus 8B-8bit placed with 32B. **Target 2 passes, minimum 1**; no
  precision stopping; t0 before 2026-11-02T00:00:00-08:00. Sol's three passes do not fit the date with the
  replications and buy precision BYTES does not need (its limit is systematics).
- Sub-packs (fixed session shape, plan trees from `joulewise/b6/compose.layout`, since the modular driver is stage 2):
  s1 1.7B + 4B; s2 8B + 30B-A3B (the cleanest dense/MoE pair shares a session); s3 14B + Next-80B; s4 32B + 8B-8bit;
  s5 70B; s6 122B. Modules whole and in sequence, midpoint reference at the module boundary. Pass 2 reverses the module
  order within each sub-pack and the sub-pack order. Per model the paper prints each pass's value, their mean and
  difference.
- Interleaving: BYTES starts after replication round 1; then after each replication round, the next BYTES sub-packs.
  Replication order and GAMMA pairing never move; a lost BYTES attempt retries in the next BYTES slot.
- Exclusions: block 6's flag catalog unchanged (thermal pressure above 0 excludes the run; the rest are flags);
  the flagged-inclusive line is printed.
- Contention level for long phases (Sol 2): the quarter-floor rule P_limit = F_min / (4·T_max) gives milliwatts for
  minute-long phases; the level used for BYTES is computed per regime from measured floors before registration, and
  if it is below what the census can measure, the registration says so and records contention as a flag only.
- Clock gate (Opus 1.3): re-derived from measured stream lengths; if the 70B's limit is under the live frequency word,
  s5 arms only when the measured word clears its own gate (a physical check, waited out).
- Disk: pre-arm free space is checked against the measured per-session footprint plus the 150 GiB reserve.

## R7. Dissent recorded

- Sol: two-coefficient H_B / H_R on the fit set only, no intercept. Not adopted as primary: on the fit set bytes and time
  are collinear (VIF 37,560), so a two-coefficient fit there is unidentified; H2 over all models is where MoE gives the
  leverage. Sol's conditioning numbers are the reason H1 is three one-variable lines.
- Sol: runtime accounting added to `mlx_runtime.py`. Not adopted: the manifest at the desk gives the same regressors
  without touching measured code.
- Sol: three passes, separate calibration/validation registrations. Not adopted (R5, R6).
- Opus: 0.95 per model. Not adopted (R5).

## R8. Build and measure list (route in brackets)

1. Bytes manifest script, header part, with tests on synthetic headers [cloud, Sol high].
2. C1 configs (`configs/campaigns/bytes_v1/generate_configs.py`; never a config named `df_rq_mid`), C2
   `scripts/bytes_plan_trees.py`, C3 sub-pack registration drafts, with the compose round-trip and validator tests
   [cloud, Sol high].
3. `joulewise/bytes_analysis.py` (H1, H2, words, DC-input decode join, Bonferroni, two-stage unblind inputs) with
   full-size production-shaped synthetic archives [cloud, Sol xhigh].
4. `scripts/bytes_twin.py`, independent recompute from this ruling only, sharing no code with item 3 [cloud, Claude
   Fable]; agreement test on the same synthetic archives.
5. Mac, no power capture, between quiet measurements: KV generation for the manifest (about 20 min), Qwen3-8B-8bit
   download (about 9 GB).
6. Mac, quiet: one non-claim resolvability, thermal and timing session (5 runs each, 12-run soaks for 70B and 122B;
   about 4 h), reading structure only; known-bytes stream test (1 h); test 7 for the long regimes (1 h).
7. C4 identity pins, C5 sizing and the clock-gate derivation; C6 one blinding group and C7 subset unblind once stage 2's
   hidden offsets are merged.
8. Registration prose and its cold gate; smoke by fingerprint for each new sub-pack's first session.

## Addendum 1 (12:58 PDT): rulings on the analysis builder's stop (Codex Cloud thread of 12:17, branch lane/2026-10-15-bytes-analysis f9c24dce6)

1. `joulewise/paper_reported_energy.py` is not edited (block 5's arithmetic, L9's file). BYTES implements the per-phase
   estimate generally in `joulewise/bytes_analysis.py` with an equivalence test against the block-5 library on every
   input the library accepts; that test is what "registered arithmetic unchanged" means for BYTES.
2. DC-input phase-edge term per member u = (P_start + P_end)(r_max + Δt_meter); stratified mean of u in B for DC input;
   largest u printed as the meter attribution floor; rest carries both terms; no clock fit means no DC-input value
   (flag). If the block-5 whole-machine-per-phase definition is registered differently before the BYTES registration,
   BYTES adopts that one.
3. Flagged-inclusive restores every physically excluded unit, thermal included, labelled.
4. The operative bound comes from the block-6 harvest's existing code path (`joulewise/b6/calibration.py`).
Note: the BYTES lanes branch from integration 220166913 and merge lane/2026-10-15-bytes-build, which is on main; they
therefore carry main's docs commits since integration's base (DIFFICULTY registrations, RUN_STATE). Docs only; recorded
so the eventual integration merge is not surprised.

## Addendum 2 (13:05 PDT): config builder (lane/2026-10-15-bytes-config ba0072e69)

- NEEDS_RULING answered: block 6's flag catalog is used unchanged, including its non-thermal exclusions; R6's "the rest
  are flags" describes the catalog, it does not change it. The flagged-inclusive line restores them (Addendum 1 item 3).
- Its block-6 suite run in the cloud had 19 failures and 4 errors from the environment (no Homebrew Python, temp disk);
  the whole suite is run on the Mac before any BYTES lane merges.
- Launcher defect found and fixed (~/.local/bin/codex-cloud-run.mjs, backup .bak-20261015): the account's websocket
  carries every thread's events; the launcher acted on another thread's turn/completed and agent text, so the config
  run's first report was cut short and the analysis continuation's launcher exited after 20 s (both tasks ran on in the
  cloud). Events are now filtered by threadId; --attach sets it.

## Addendum 3 (14:46 PDT): the twin's open choices (Fable twin, JouleWise-data claude/bytes-twin-tptjkk @ 07e032d), and the analysis lane's state

The analysis lane (lane/2026-10-15-bytes-analysis 82c014c55) finished with NEEDS_RULING none:
- 28 tests and 1,224 exact equivalence comparisons with the block-5 library.
- 60 synthetic campaigns with no wrong word.
- H2 coverage 1.00 in every world. That suggests the intervals are wide (B dominates); the executing review checks it.

The twin was written from the ruling text before Addenda 1 and 2. These rulings bind both implementations. The agreement test judges each side against them.

1. **Drift allowance:** computed from the export's NEG-8 reference rows (twin CHOICES 11), not read from `withheld/`. Stage 1 unblinds the `neg8_reference` key with the fit set.
2. **Allowance scale:** max(1, E/E_ref, T/T_ref) per cell. E is the cell's decode-phase m; E_ref is the mean gross energy of the session's kept start, midpoint and end references over the whole request. T and T_ref are the same with durations. The allowance was measured on whole requests, so the comparison is with the whole request (twin CHOICES 12, adopted).
3. **DC-input edge term:** Addendum 1 item 2 governs. Per member, u = (P_start + P_end)(r_max + Δt_meter). The twin's 2·p95·P̄ (CHOICES 18) is replaced.
4. **No DC-input or rest number at the blinded stage.** The raw meter stream carries no hidden offset. DC input and rest are computed only for configurations already unblinded (stage 1 fit set, stage 2 all). The blinded agreement therefore covers rails. DC input and rest agree on synthetic stage-1/2 inputs. Both implementations must refuse the meter join for a configuration that is still blinded (twin CHOICES 20).
5. **Two passes:** H1 and H2 use the mean of the passes' e, with half-width equal to the mean of the passes' (h + B). B does not shrink with passes, and h is about 0.1%. Per-pass words are printed as description (twin CHOICES 26).
6. **H2 multiplicity:** the primary intervals per boundary are: the simple ε; the extended ε and ρ; the tier ε and ρ; one deviation per non-tier model present (up to 4); and, for rest, ε_rest and λ. That gives k = 9 for rails and DC input and k = 11 for rest with all ten models (twin CHOICES 27). P₀ and c are printed, not counted.
7. **Tier deviation interval:** t·se_pred(new observation) plus the model's own measured half-width of P̄, (h + B)/T, added (twin CHOICES 28). The deviation is a comparison of two uncertain quantities.
8. **Flagged-inclusive line** (clarifies Addendum 1 item 3 and Addendum 2):
   - It restores every unit excluded by a flag-catalog code whose run has a valid energy record: thermal, contention, battery, clock and the rest.
   - It never restores a run without a valid energy record (status not succeeded, bundle or validity failure).
   - The twin's narrower restore (CHOICES 14) is replaced.
9. **Rest fit near-collinearity** (twin note 5): print the VIF of BW and P̄_rails beside λ and ε_rest. Their intervals stay in H2's k. No word is drawn from λ.
10. **Twin limits accepted:** no hazard-journal fallback for the meter offset (a stream without pairs gives no DC-input number, flagged), and the manifest reader is narrowed once `scripts/bytes_manifest.py` fixes the schema.

## Addendum 4 (15:07 PDT): the executing review of the analysis (Opus cloud, JouleWise-data claude/bytes-analysis-review-opus @ 6039fff)

Every finding is accepted. Fix round: Sol 6.1 xhigh on lane/2026-10-15-bytes-analysis.

1. **W1, wrong.** A member the harvest excluded, or one without a usable record (missing bundle, token count not 512, non-finite or missing decode energy, re-reduction not succeeded, no decode envelope), removes its unit.
   - It never stops the stage. Only a stratum below 5 kept units refuses that cell.
   - Applies at every stage and in non-synthetic mode.
2. **S2.** H2 follows item 6 exactly:
   - k per boundary is 9, 9 and 11.
   - The extended ε is primary.
   - The tier fit is the two-term fit (BW and R/τ), and the deviations are measured from it.
3. **S3.** The deviation interval adds (h + B)/T (item 7).
4. **S4.** The two-pass half-width is the mean over passes of (h + B), not a pooled h (item 5). Per-pass words are printed as description in h1.json, with a pass dimension.
5. **N5: H2 standard errors.** Errors in P̄ scale with P̄ (2 to 29 W across models), so homoscedastic OLS understates the spread; plain-95% coverage was 0.80 in the resident world.
   - Primary H2 intervals use HC3 heteroscedasticity-robust standard errors with t at n − p df and the Bonferroni k. The OLS SE is printed beside them, labelled.
   - The builder re-runs the reviewer's coverage harness (p03) in all three worlds and reports plain-95% and ruled-k coverage for HC3 and OLS.
   - If HC3's plain-95% coverage is below 0.93 in any world, report NEEDS_RULING with the table. Do not pick another method.
6. **S6.** Flagged-inclusive restores every catalog exclusion of a run with a valid energy record, NUMBER class included (item 8). Only status, bundle and validity failures stay out.
7. **S7: drift allowance.**
   - Computed from the session's NEG-8 reference rows (items 1 and 2), not from the manifest.
   - E_ref and T_ref are the means of the kept start, midpoint and end references over the whole request.
   - The idle-subtracted secondary uses the block-5 plan's idle-subtracted family allowance, as block 5 does.
   - The synthetic campaign gains start, midpoint and end references, so this is tested.
8. **S8: blinding.**
   - (a) A `--stage blinded` path computes rails from the blinded export, so the twin agreement can run.
   - (b) The meter join refuses a configuration whose key has not been released. Release is read from the key directory, never from the manifest's `synthetic` field.
   - (c) At stage 1 only samples inside fit-model spans are parsed. A held-out configuration's raw meter samples are not loaded before stage 2.
   - (d) The stage-1 commit adds the NEG-8 inputs and the SHA-256 of bytes_analysis.py.
   - (e) The tier inputs committed at stage 1 are the fit models' only. The registration says so.
9. **S9.** Print the VIF of BW and P̄_rails beside the rest fit.
10. **F10.** Each phase edge uses the larger power of the two samples adjacent to the edge.
11. **N11 battery.** The analysis relies on the harvest's `battery.assist` flag. The registration states that dependency.
12. **N12.** Keep integers exact as the library does, and add ints, constant cells and zeros to the equivalence test. Alternatively, narrow the claim to floats and say so. The builder chooses and records it.
