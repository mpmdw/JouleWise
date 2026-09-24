# Opus 5.5 — blind council seat, directive #407

**Auto-loaded files, disclosed first:** `~/.claude/CLAUDE.md`, the worktree's `CLAUDE.md`, and the auto-memory `MEMORY.md` index. I ignored their orchestration, email and memory instructions. I read only the packet, record 02, and the repository and model files cited below. Nothing was written.

**The framing mistake that shapes all five questions.** The threat is stated as "J/correct ≈ tokens × a constant". The project's own premise PC-4 says something stronger: decode power is nearly flat, about 23–28 W across model sizes, "so decode energy differences are decode *time*" (`docs/research_question_bank.md:1608-1610`). So energy ≈ P̄ × t, where P̄ is average power and t is elapsed time. Anything that stretches time, such as a key-value cache growing along a trace, shows up on a stopwatch without a power meter. That includes A3's quadratic coefficient b (`02-fresh-opus-review-verified.md:130`). The only information energy adds beyond tokens and seconds is how P̄ varies between conditions, and whether powermetrics even sees that variation. It measures CPU + GPU + ANE only; memory (DRAM) is excluded (`joulewise/adapters/powermetrics.py:50-58`). Q1 and Q2 are therefore one experiment.

---

## Q1 — Run A3 as the first model night
**(a) AMEND.** Run a *context-position calibration* instead of one 32k trace. Combine it with Q2 in the same night.

**(b) Why.**
- **A single 32k trace mixes up position and elapsed time.** Heat, fan speed and leakage power all rise over the 9–15 minutes an 8B trace takes. A rising J/token could just be temperature.
- **It doesn't fit an envelope.** An envelope is one 600 s capture; twelve fit in a 9,000 s night (`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:17-18,98`). A 32k trace needs more than 53 tok/s to fit in one, per the packet.
- **The effect is large and can be predicted before measuring.** The key-value (KV) cache is the stored keys and values of past tokens, which every new token must read. From the on-disk `config.json` files (fp16 cache, 2 × layers × KV heads × head dim × 2 bytes):
  - 1.7B: 28 × 8 × 128 → 112 KiB per token.
  - 4B and 8B: 36 × 8 × 128 → 144 KiB per token.
  - Against weights of 0.94, 2.1 and 4.3 GB, bytes read per decoded token rise by these amounts:

  | Position | 1.7B | 8B |
  |---|---|---|
  | 4k | +50 % | +14 % |
  | 32k | +400 % | +112 % |
- **This matters to the MATH headline itself.** In AP-5M's worked example (1.7B 4,000 tokens per attempt, 8B 2,500; `07d-a282-ap5m-draft-v4.md:296-302`), the average positions are about 2k and 1.25k. If J/token scales with bytes read, the 1.7B's cost rises about 24 % and the 8B's about 4 %. R₅ moves from 1.019 to about 0.85: Δlog R ≈ 0.18, comparable to SE 0.25. The planning figures come from 512-token decodes, so they miss this entirely.
- **What A3 does not decide.** A3 does not decide whether MATH is "about energy". What decides that is whether P̄ varies, on either instrument.

**(c) What would prove me wrong.** J/token stays flat within about 5 % out to 8k for the 1.7B, where the bytes law predicts about +98 %, and P̄ stays flat on both instruments. That would mean J/correct really is seconds × a per-model constant. The design below can produce that result.

**(d) Night sketch (the "calibration night", shared with Q2).**
- **Models:** Qwen3 1.7B and 8B, 4-bit. Both are admitted (`configs/model_panels/qwen3_4bit.json:5-17,38-50`).
- **Envelopes:** one model per envelope, alternating, with the starting model counterbalanced. 12 envelopes gives 6 replicates per model.
- **Each envelope:** positions L ∈ {512, 2k, 8k, 16k, 32k} in a seeded random order. At each position:
  - prefill L pinned tokens (a compute-bound phase);
  - then a forced 512-token greedy decode with thinking off and end-of-sequence suppressed. This is D-166's decode shape (`docs/decision_log.md:10755-10762`); the runtime already supports it (`joulewise/adapters/mlx_runtime.py:727`);
  - then at least 30 s idle.

  Randomizing the order separates position from elapsed time. My estimates, not measurements: an 8B decode segment at 32k takes about 15 s and about 450 J, roughly 90× the 5 J claim bar.
- **Measured:** E, t, P̄ = E/t and tok/s per segment, on powermetrics and on the USB-C meter (Q2).
- **Reported:**
  - J/token(L) split into P̄(L) × s/token(L), with t-intervals over 6 replicates.
  - A pre-registered prediction: J/token(L)/J/token(512) = 1 + κ·KV(L)/W, where W is weight bytes. The test is whether one fitted κ covers both models.

**(e) Risks.**
- It needs a new registration. The research-question row RQ-KV-GROWTH currently forbids per-token joule claims (`docs/research_question_registry.md:55`). That is fine: claim J per 512-token segment and J/token as a segment mean.
- It displaces the _v5 transaction (the next scheduled campaign), not G2-a; see (f).
- Drop the alternative-attention contrast from this night; see (g4).

## Q2 — Run B1 (wall meter vs powermetrics)
**(a) AMEND.** Yes, run it: D-091 made the instrument the product and D-092 ratified a wall-meter check for the paper (`docs/decision_log.md:135-136`). But amend four things:
1. **Vary memory load by context position and phase, not bit-width.** Only 4-bit artifacts are admitted.
2. **Call it USB-C input power, not wall power.** The KM003C sits after the charger, at about 27.56 V (archive `meter_paired.txt:3-8`). It excludes charger losses but includes the display, fans, SSD and battery charge or discharge.
3. **Measure an incremental ratio.** ρ = ΔP_USB / ΔP_pm, each Δ taken against idle segments. The estimand is **ρ(decode) − ρ(prefill)** and how ρ trends with L. Meter gain error cancels in both, so no calibration certificate is needed. Absolute ρ also contains voltage-regulator losses (an estimated 10–15 %), so label it uncalibrated.
4. **Log the meter on every night from now on**, once its on/off overhead is measured.

**(b) Why.** Decode is limited by memory bandwidth, and DRAM is outside the powermetrics boundary. This is the first question a metrology reviewer will ask. Resolution is ample: idle readings swing about ±2 W sample to sample at about 2 Hz (`meter_paired.txt:3-8`). A 15 s segment (about 30 samples) gives an SE of about 0.4 W against 20–30 W of incremental decode power, so ρ is resolved to about 2 %.

**(c) What would prove me wrong.** ρ is the same in prefill and decode and flat in L, within about 3 %. That result would be good news: a validated measurement boundary. The design can produce it.

**(d)** Same night as Q1. Add three things:
- an idle segment with the meter reader on and one with it off (the reader is a Python process that polls USB);
- battery current from `ioreg`, which needs no sudo; exclude or correct any segment where the battery is charging or discharging;
- 2 s trimmed from each end of every segment, because timestamps are the host's receipt time (`km003c_probe.py:120-133`).

**(e) Risks.**
- Fan steps show up on USB power but not on powermetrics. Log thermal pressure.
- The night driver owns an exclusive window (`scripts/run_night.py:684-685`), so the meter reader needs an integration authorization.
- Bit-width (the review's C2) waits for artifacts to be admitted.

## Q3 — Make the thinking budget the independent variable
**(a) AMEND.** Yes to budget as the independent variable (A2). Defer parallel votes (A1). Also **split the accuracy experiment from the energy experiment.**

**(b) Why.**
- **Accuracy noise, not energy noise, drives SE(log R) ≈ 0.25 at n = 64.** Take Level 5 with 1.7B accuracy p ≈ 0.25: √(0.75/16) = 0.22 from accuracy alone. Energy error (~5 J on ~370–940 J per attempt) is negligible.
- **Accuracy doesn't need a quiet machine.** Only energy does. So:
  - measure accuracy at large n outside quiet windows, recording tokens and timestamps;
  - measure energy on a small quiet subsample;
  - predict per-trace energy from the calibration-night law, with a registered test of how well it predicts.
- **Budgets nest.** With greedy or fixed-seed sampling, the trace at budget b is a prefix of the trace at 2b. Generate once to the largest budget; each smaller budget then only needs its short forced-answer tail.
- **Sampling may be needed anyway.** Qwen's upstream model card, as I recall it, warns that greedy decoding in thinking mode loops. I did **not** find that warning in the on-disk README; verify it. Loops cause cap hits, which is exactly the cap-dependence artifact the review worries about. Fixed-seed sampling keeps the nesting.

**(d) Design.**
- **Independent variable:** thinking budget b ∈ {0 (thinking off), 1k, 2k, 4k, 8k}.
- **Models:** 1.7B and 8B.
- **Levels:** MATH 1–5, with the same problems in every cell.
- **n:** 200 per level for accuracy. Paired SE(log R) is about 0.14 (95 % interval ×/÷ 1.32); at n = 400, about 0.10.
- **Energy subsample:** 10 per level per model, measured quietly.
- **Estimand:** J/correct(m, ℓ, b) = mean energy per attempt ÷ accuracy, in **joules per correct answer**.
- **Primary test:** one hypothesis per level (so Holm keeps m = 5), on log[min_b J/c(1.7B) ÷ min_b J/c(8B)]. The bootstrap redoes the minimization in every replicate, so choosing the best budget is part of the inference. Holm is the step-down multiplicity correction AP-5M already uses.
- **Reported:** the energy–accuracy frontier per level.
- **Registered fallback:** if the calibration law fails its prediction tolerance, measure every counted trace directly.

**(e) Risks.** This is a rewrite of AP-5M's estimand row and the A291 contract (packet Q3; `02d-...contract-v4...md:68-96`). Cost: roughly 2 machine-days of accuracy runs outside quiet windows plus 1–2 quiet nights. AP-5M's own estimate is 12 or 23 nights (`07d-...:1297-1298` via packet 06). Model-based energy must be labelled as "energy law measured on this machine, validated to ±x %".

## Q4 — Small fixes
**(a)** Clock: **NO.** ABBA: **AMEND.** Simulations: **YES, with the right question.**

**(b) Clock.** Monotonic event stamps don't remove the need to switch off network time. The anchor fits powermetrics' **wall-clock** second stamps (`02-...verified.md:55`). A time-daemon adjustment moves those too. Monotonic events would turn a common shift into a relative one. The current cure already retained 11 of 12 captures (`:11`).

The actual defect is gate sizing. A 5 ms refusal × 33 W ≈ 0.17 J, a sixth of the roughly 1 J attribution floor. If these refusals return, loosen that tolerance rather than change the stamp source.

**(b) ABBA.** Repeated ABBA already balances linear drift, and it balances carryover within the block: each arm follows the large model once per block. What it leaves unbalanced is the start of each block after idle, which always falls to arm A (`generate_configs.py:208,1709-1712`). Alternate ABBA and BAAB in every **new** registration. Don't regenerate the frozen _v5 family for this alone.

**(b) Simulations.**
- **Claim gate:** the √n question has no single answer. The error has two parts:
  - **Random:** where each phase boundary falls against the 100 ms record grid changes from block to block. This part averages down as 1/√n.
  - **Systematic:** the mean fiducial lag and D-078-class offsets. These don't average down. They cancel in a paired contrast only as far as the two arms' power steps match.

  Simulate with the two parts separated, using the real `detection_floor.py:871-881`.
- **D-165 dominance test:** simulate P(pass) against w/σ using `dominance_closeout.py:517-537`. If passing is roughly a coin flip, retire dominance as a headline in favour of B2, which reports the timing share of the uncertainty budget against phase duration (`02-...:146-148`).

**(c) What would prove me wrong.** A replay shows NTP slews move only event stamps and not powermetrics stamps. Checkable at the desk.

**(e) Risks.** None of these displaces a night.

## Q5 — Full gating only on claim-bearing code
**(a) AMEND.** Define the boundary by what a change can affect, not by file names. The full tier applies whenever a change can alter any of:
- a raw-bundle byte or timestamp;
- a reduced energy or time;
- an admit or refuse decision;
- a registered plan or prospective manifest;
- claim text.

Everything else gets one reviewer plus CI.

**(b) Why.** Review depth should follow the cost of a wrong number. The D-078 class of defect came in through measurement semantics, which stays in the full tier. A file list would let clock or night-runner changes through (`joulewise/clock.py:55-72`).

**(c) What would prove me wrong.** Over the next 30 days, a defect that changes a number gets through the light tier. Record which tier caught each material defect, and revert if one does.

**(d)** Change `docs/orchestration.md:159-167`, `.github/pull_request_template.md:1-20` and the checker in the same change. Otherwise the rule can't be installed on required-check main. It goes to a cold gate, and Ed sees the result.

**(e)** It changes nothing for A291–A293, which stay full tier.

## (f) Order of the next three nights
1. **G2-a as registered, with the meter as a rider.** G2-a is the ready item; it probes which prefill length the _v5 campaign should use. Add USB-C and battery logging as an unregistered, exploratory rider, including the on/off overhead check. G2-a decides on record counts, not joules, so the rider cannot change its outcome. The desk registers night 2 meanwhile.
2. **The calibration night (Q1 + Q2).** It gives the first claim-bearing numbers, with effects of hundreds of joules against a 5 J bar. It settles the PC-4 threat and the measurement boundary, and it supplies the energy law that Q3 needs.
3. **MATH energy-validation night.** Budget-forced subsample with per-token timestamps, while accuracy runs outside quiet windows. If night 2's law fails, this becomes a direct-measurement MATH night instead.

The _v5 D-117 contrast (1.7B vs 8B at a fixed shape) moves after these; it is one position rung of night 2.

## (g) What the five questions miss
1. **The equivalence-night rule is close to a coin flip.** Under no real change it passes only 37–76 % of the time, so it raises a false alarm on roughly half of unchanged nights (bench-verified, `02-...:12`); the review put fixing it first (`:164`). If it still gates any night, replace it with TOST (two one-sided tests for equivalence) plus a variance-ratio test sized by simulation, before night 1.
2. **Report every energy as P̄ × t.** Without the split, readers cannot tell energy results from latency results.
3. **The end-of-November deadline isn't recorded in the repo** (`02-...:16`). With about 9 weeks left, the Q3 redesign has to fit in about 4 quiet nights.
4. **Correction to the scout: an alternative-attention model is on disk.** `Qwen3.5-122B-A10B-4bit/config.json` interleaves 3 linear-attention layers with 1 full-attention layer (`full_attention_interval` 4). It has 2 KV heads × 256 in 12 full layers, which gives 24 KiB per token against 144 KiB for Qwen3-8B. It is 65 GB, mixture-of-experts (so confounded), and MLX support is unverified. Use it later, after a desk smoke test, as a test of the bytes-read law (KV bytes per token as the covariate), not as an "attention scheme" contrast.
5. **Label every number's boundary.** Every number is CPU + GPU + ANE until night 2 says otherwise.
