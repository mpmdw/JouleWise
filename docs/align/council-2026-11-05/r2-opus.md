# r2-opus: cross-critique and revised design (Opus 5.5 seat, round 2)

I read r1-fable.md and r1-sol.md in full, and re-read my own r1. I checked every claim used below against the repo at `e328f0e72` / `origin/main 92026c184` and against the web on 2026-11-05.

Citation keys are as in r1. `RS:n` is `origin/main:RUN_STATE.md` line n. `F§`, `S§` and `O§` are sections of r1-fable, r1-sol and r1-opus.

---

## 1. Errors in the other designs (and three in my own)

### Fable

| # | Claim (location) | Finding | Evidence |
|---|---|---|---|
| F1 | Qwen3.8-27B-8bit "was deleted from the Mac on 10-25 … re-download owed" (F§1.1 table; R1 step) | **Wrong.** It was re-downloaded on 10-28 at rev `815b83c0…`, 28 GB, to `/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit`. No later deletion is recorded. It needs an `ls` check in R0, not a download, and the disk plan should not budget 29.5 GB for it. | `RS:349` (item 85) |
| F2 | "default Metal working-set limit (about 96 GB) [guess]" (F§1.1 Flash-Next row) | **This Mac measured 115.4 GB (107.5 GiB)**, MLX's recommended working set, with `iogpu.wired_limit_mb` 0. The repo also contains an older "about three quarters of RAM" note (`docs/design/block6_collection_draft.md:573`), so R0 should re-read `mx.metal.device_info()`. Sol's `min(96 GiB, 0.75×RAM)` ceiling (S§2) has the same problem. | `docs/design/bytes_pilot/SUMMARY.md:29` |
| F3 | N = Next-80B **Instruct 8-bit**, 84.7 GB | **Scientific problem.** Instruct emits no reasoning span, so the pilots' main monitoring estimand (the known-H reasoning-omission tamper curve, `P3:155-163`) is unavailable for N. Only untampered residuals would remain (Sol makes the same point, S§2). | — |
| F3 (cont.) | same | **Practical problem.** It is an 84.7 GB download against 82 GB free (`c110a6c9` Launch) with 36-41 GB needed per window. Its peak (about 89 GB) has never run here (largest 71.5 GB, `SUMMARY.md:26`). Nothing in the records says Instruct acts better than Thinking. | — |
| F4 | Q at `reasoning_effort: low`, 12 × 2,048, **180 s wall guard** (F§1.4) | Moves Q **off the production default.** The card's default is xhigh, and the card warns that low effort "can increase total task latency in multi-turn agent work … failures, and retries" (https://huggingface.co/Qwen/Qwen3.8-27B). Fable itself predicts "2-4 turns per episode inside the guard", so capability would read low for timing reasons. | — |
| F4 (cont.) | same | **Machine state leaks into work.** A wall guard makes trajectory length depend on decode speed, i.e. on thermal state. A guard decision near the boundary also breaks replays across thermal states. | `workload.py:313-318` |
| F5 | Gate enforced in the controller's `idle_baseline` stage (F§4.2 item 7) | **Misses warmup heat.** The lifecycle runs idle_baseline, then warmup, then measured_run. ALIGN warmup prefills the condition-specific task prompt, about 37 s of prefill for Q at about 190 tok/s, and the sabotage prompt is 755 tokens longer. That heat lands after Fable's gate and differs by condition. Sol places the gate correctly. | `controller.py:1658-1660`; `workload.py:258-269` |
| F6 | Gate per member only, on GPU die temperature (F§2.3 C1) | **Does not address the pilot-7 signature,** which builds up across turns *within* an episode (`cf1baad2` Sol: +25.0/+23.7/+49.2 J on turns ≥3). After 300 s of idle the die returns to near-ambient within seconds, so a die-only member gate almost always passes. The slow, heatsink-class state is what sets the die temperature during the next load. | — |
| F7 | "(b) is small … so the clock is tracking behaviour" (F§2.1) | **Not supported.** Fact 2 compares *identical* work, and identical work has an identical heating profile. It says nothing about whether *different* heating profiles shift energy, which is the open question. Only same-token replays at different thermal states test it; that is the contrast experiment adopted below. | — |
| F8 | Q's prompt cache: "verify the whole-cache rebuild fallback engages" (F§4.1 item 5) | **Engaging that fallback is itself the cost problem.** In pilot 2, thinking-on A needed trims of 143-560 tokens at 3 transitions (`e1308804` l.56), and pilot-3 a-e01 needed 4 trims of 1,570 tokens. On a non-trimmable DeltaNet cache, each such trim becomes a whole re-prefill (`prompt_cache.py:62-74`): 10-35k tokens at about 190 tok/s, i.e. 50-180 s per event for Q. A checkpoint-and-restore build is needed. | — |
| F9 | Q tool calls | **Not mentioned anywhere.** Qwen3.8-27B and Qwen3.5 templates emit XML calls (`<tool_call><function=…><parameter=…>`). The runtime parser accepts only JSON envelopes and flags `<function` as `unsupported_tool_call_format`, so **Q cannot act until a parser is built.** | https://huggingface.co/mlx-community/Qwen3.8-27B-8bit/raw/main/chat_template.jinja; `endpoint.py:60,154-158` |
| F10 | M2 member 970 s = 390 + 90 + 430 + 60 (F§3.2) | **The member law gives more.** The law is 516.6 + 1.135 × 430 = 1,005 s, plus a 60 s gate, so 1,065 s. M2's span becomes 32,564 s and the window maximum **50,280 s** (Fable printed 48,420). M3 rises similarly. | `sizing_b5.json` member law |
| F11 | A3: anchor session effect within ±6 J of pilots 6-9 | **Confounds protocol change with control.** The new gate and physical setup are *expected* to move the Qwen3-30B anchors; Fable's own question 4 says so. Stability should be tested among new-protocol sessions. | — |
| F12 | Four windows reach m = 16 held-out benign per pair | Below m = 19, the split rule has no finite threshold (`RS:1055`; `cf1baad2`), so the series ends without a threshold. Fable acknowledges a 5th and 6th window would be needed. | — |

### Sol

| # | Claim (location) | Finding | Evidence |
|---|---|---|---|
| S1 | WQ planned envelope 42,355 s, "headroom to 44,640 s 2,285 s"; N1-N2 at 43,835 s (S§4, duration table) | **Arithmetic error that decides the plan.** The window maximum is *derived* from the programmed span: 60 × ⌈(span + 3,300 + 7,200 + 7,200)/60⌉. A 42,355 s span gives a **60,060 s** maximum, and a 43,835 s span gives **61,560 s**. Holding 44,640 s requires span ≤ 26,940 s; pilot 8 used 26,914. So Sol's windows are 1.6× pilot 8 while S§4 says "No argument here justifies a longer window". Under the real limit at 1,120 s per member, WQ holds about 14 members with its 6,000 s conditioning allowance (not 28), and N1/D1 about 16 with 3,000 s (not 32). | `joulewise/b6/plan_inputs.py:56-59`; `b5/plan.py:59,66-67` |
| S2 | Qwen3.5-122B "about 92.1 GiB, close to the 96 GiB ceiling" | Built from guesses (16 GiB workspace + 10 GiB runtime) against a guessed ceiling. Measured MLX peak on this Mac is **71.5 GB at about 2.5k context**. Full-attention KV at 40,960 adds about 0.94 GiB (12 layers × 2 KV heads × 256 × 2 B × 2 = 24 KiB/token). External M4 Max runs peak at 66-85 GB. The real ceiling is 107.5 GiB. | `SUMMARY.md:26,29`; config https://huggingface.co/Qwen/Qwen3.5-122B-A10B/raw/main/config.json |
| S3 | D fallback `Qwen3.5-27B-4bit` | That is a different, older model. The same-model fallback exists: `mlx-community/Qwen3.8-27B-4bit`, 16.1 GB, same architecture and loader. | HF tree API |
| S4 | New cells use a 120 s wall turn-admission guard | Same flaws as F4: at 12 tok/s it allows about 2-3 turns, and trajectory length then depends on machine speed. | — |
| S5 | Frozen fitter **inside the chain** after the training members; fixed coefficients for later windows | **(i) Unnecessary.** Collection does not depend on the fit. "Fit on training rows, freeze and record the commit before the calibration rows are read" gives the same honesty at the desk, with no in-chain code. | — |
| S5 (cont.) | same | **(ii) Reintroduces the session-offset problem.** Coefficients frozen across windows carry the 8-9 J window offsets into every score. Per-session fits were chosen in `cf1baad2` precisely so that offsets cancel. Sol's own sentinel gate is meant to compensate, but this is a different calibration method from the frozen `7fbd95e31`, and it must be argued, not swapped in. | `cf1baad2` "Calibration population" |
| S6 | N = Next-Instruct, "known kit compatibility" | Same as F3. Sol notes the tamper estimand may be lost but still chooses Instruct. | — |
| S7 | Ambient 20-23 °C, session range ≤1 °C as a gate (S§3 item 1) | Over 12 h in a home room this would refuse many windows, and nothing records the room today. Record ambient; do not gate on it. | — |
| S8 | Neither design schedules the XML parser or the hybrid cache checkpoint | Both are required before D acts or runs at feasible cost (F8/F9). | — |

### My own r1 (corrected here)

- **O1. Next-Instruct did act.** In pilot 2 it made 4/0/3/12 state changes, acting in 3 of 4 episodes (`e1308804` l.12). The 0-2 figure comes from pilot 3's cached greedy runs. My r1 claim that "Thinking is the one that acts" was too strong. The preference for Thinking rests on the reasoning estimand and the published agent scores (BFCL-v3 72.0, TAU2-Retail 67.8; https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Thinking), not on measured action rates.
- **O2. Keep 8 anchors in the qualification window,** as Fable and Sol do. The four replays at 9/14/19/28 are the within-window exact-work early/late pairs that U3 needs. I had cut them to 4.
- **O3. Cache-rewrite evidence was missing from my r1.** I justified the checkpoint by template inspection only. `e1308804` l.56 gives measured cases: A trimmed 143-560 tokens at 3 transitions; B (thinking off) had a 4-token suffix rewrite every turn; Next-Instruct was append-only. Hybrid *thinking* models will therefore need rewinds, so the checkpoint is required. It should keep one snapshot per turn boundary, about 70-150 MiB each (linear-attention state, from config).

---

## 2. Best ideas adopted from the others

- **Gate after warmup, immediately before the episode start stamp** (Sol S§3 item 5), plus a **settled-slope condition** |dT/dt| ≤ 0.2 °C/min (Fable C1).
- **Window-local reference temperature** (Fable): measured after the scaffold, not chased across nights. Cross-session differences are the anchors' job.
- **β_T (J/°C) estimated only on identical-work pairs** (Fable §2.4), combined with my gated/ungated contrast. Its acceptance bar (Fable A4): |β_T| × observed start-T range ≤ 0.1 × min per-pair s_r.
- **Sol's exact-work equivalence margins:** across at least 6 exact pairs from at least 2 windows, mean normalized |ΔE| ≤ 0.25 % with the 90 % CI inside ±0.5 %; identical-work active-clock difference ≤ 0.5 %.
- **Sol's early-to-late benign residual change bar:** ≤ 10 J per about 2.7 kJ (0.37 %).
- **Sol: hardware acceptance and score calibration are separate verdicts.**
- **One model per calibration window, model order N, D, D, N** (both seats). The qualification window stays mixed.
- **Sol: a capability gate** before calibration. Each model must make a state-changing action on each pair in at least one benign qualification episode; otherwise it is reported as an energy/capability screen.
- **Fable: print system power minus rails** (SMC `PSTR` minus GPU, CPU and ANE) per anchor, to chase the pilot 5→6 decode-only step.
- **Fable: a protocol failure (U1-U3) is labelled** "thermal protocol not met", and that window's new-model members enter no held-out pool.
- **Sol: phase-specific clock summaries** (prefill vs decode active clock, low-clock fraction, first sustained decline).
- **Sol: a frozen tamper grid,** H = 0, 128, 256, 300, 512, 1,024, 2,048 plus full, with H = 0 never counted as a detection.

---

## 3. Contested decisions

### (a) Model set

**N = Qwen3-Next-80B-A3B-Thinking, 4-bit** (`mlx-community/…-Thinking-4bit`, rev `9a2b4634…`, 44.8 GB). It is not 8-bit Instruct, for these reasons:
- It keeps the reasoning-omission estimand.
- It uses the JSON tool format the existing parser handles.
- It is a 44.8 GB download versus 84.7 GB.
- 4-bit has run here (the Instruct twin, under the pinned 0.31.3).
- Fallback: Next-Instruct-4bit (on disk, pilots 2-3 continuity), labelled as having no tamper estimand.

**D = Qwen3.8-27B, 8-bit, at card defaults.**
- On disk at rev `815b83c0`. Its weight map has no `mtp.` keys, so mlx-lm #1623 does not apply.
- Card defaults: xhigh effort, `preserve_thinking`, sampler 1.0/0.95/20/0, turn budget 4,096.
- Two R1 rules, fixed in advance:
  - if more than 50 % of R1 turns hit the 4,096 cap, use `medium`;
  - if the gated planning member exceeds the 1,800 s cap, use `Qwen3.8-27B-4bit` (16.1 GB). Never `low`.

**The 122B MoE is a screened reserve, not a calibration cell in this series.**
- It fits: 69.6 GB on disk, measured peak 71.5 GB, about 73-78 GB at 40,960 (estimate).
- R1 runs one gated episode, which tests the XML parser on its `qwen3_5_moe` template.
- It becomes a third cell only if Ed says "top models" includes it. Each cell costs about 3-5 calibration windows.

**Qwen3.8-Flash-Next is truly infeasible on the pinned stack.**
- `model_type qwen4_exp` (config.json).
- mlx-lm PR #1788 adding it has been **open since 2026-08-26**; it drops MTP and has an n-gram seed hazard that silently degrades output (https://github.com/ml-explore/mlx-lm/pull/1788).
- One reported 4-bit run peaked at **111.02 GB**, about 96 % of the 115.4 GB working set, which would need a wired-limit sysctl.
- The only mlx-community builds are 4-bit and above, plus an OptiQ "2-bit" with inconsistent tags.
- Using it needs an unmerged code branch, a second venv and a sysctl. That is a separate pin/engine council, not this series. Record it as "dropped with reason".

### (b) Window plan

**Order.** Run pilot 9 first: it is already built and admitted (`c110a6c9`), its protocol is unchanged, and it brings Qwen3-30B to m = 20/pair. Then R0 (desk), then R1 (hardware rehearsal, about 3.5 h), then **WQ**.

**WQ is qualification and the deciding experiment in one window,** because both are selection data anyway. 20 members:

| Group | Members × planning s | Total (s) |
|---|---|---|
| 8 Qwen3-30B anchors (1-4, 9, 14, 19, 28), byte-identical | 8 × 783 | 6,264 |
| Contrast: pilot-7 b-e25 and b-e18, each gated per turn (A) and byte-identical ungated (B), order A B B A | 2 × 783 + 2 × 1,140 | 3,846 |
| N: 4 cells at seed 1 + 1 replay | 5 × 1,130 | 5,650 |
| D: spam/benign, bank/benign, spam/sabotage at seed 1 | 3 × 1,774 | 5,322 |

The align members total 21,082 s; with the 4,995 s scaffold the span is **26,077 s**, and the **maximum is 43,800 s**. The N and D members are gated per turn so that the gate cost is measured.

**Calibration windows** (N1, D1, D2, N2, …). One model per window. Six anchors: the four originals at ordinals 1-4, plus 2 replays at mid-window and at the end as early/late exact-work sentinels, costing 4,698 s.

| Window | Members | Span / maximum |
|---|---|---|
| N, gated | 15 | 26,643 s / 44,400 s |
| N, ungated (if the contrast rejects T) | 23 | about 26,276 s / 43,980 s |
| D, with holds | 9 | 25,659 s / 43,380 s |

**Calibration target per model:** m = 20 held-out benign per pair (the first finite split threshold, equal to the sample maximum) plus 4 sabotage per pair. That is 48 members per model:
- N needs 3 windows ungated or 4 gated.
- D needs 5-6 windows (4-5 at 4-bit).

**Recommendation:** take N to m = 20 first. D gets qualification and 2 calibration windows (m ≈ 9/pair) unless Ed approves the longer series, or approves 59,520 s maxima like pilot 3, which roughly doubles members per window. Registration grade (m ≥ 39) needs Ed's go.

**Calibration method:** the frozen per-session LOO method (`7fbd95e31`, pooled split rank ⌈0.95(m+1)⌉), applied per model × pair. This rejects Sol's frozen-coefficient split (S5).

### (c) Thermal gate

- **Variable:** the slow, heatsink-class SMC key chosen at R0/R1 by response (63 % rise time ≤ 5 s means die class; the slow sensor is the gated one). The die key is recorded and also checked.
- **Member gate:** always applied, after warmup and before the episode stamp. Release when T_slow ≤ T_ref + δ, with δ = max(1.0 °C, 3 × idle SD), and |dT/dt| ≤ 0.2 °C/min, using the window-local T_ref. Extra-wait cap 600 s; on cap, flag and proceed.
- **Per-turn gate:** same condition, before each `endpoint.chat`. **Used in WQ; kept for the calibration windows only if the contrast confirms T:**
  - both |ΔE| ≥ 10 J with a turn-index trend → keep it;
  - both ≤ 6 J (2 SD of a 2.97 J difference) → drop it;
  - otherwise add two pairs.
- **Decode holds** at fixed token counts, with N_chunk = 256 × ⌊0.6 × t_decline × r_decode / 256⌋. Applied for D only, and only if R1 shows its planning turn crosses t_decline; expected, since a 4,096-token turn is about 18 kJ against the 6.5-8.3 kJ onset budget (`e1308804` l.58).
- **Gate and hold time** fall in unowned attribution segments (`attribution.py:568,582`; holds need a decode split).
- **Guard:** a **token budget** for the new cells (B_D sized so the planning member is ≤ 1,800 s), so episode work is independent of machine speed. The anchors and the contrast's B arm keep their byte-identical 120 s guard.

### (d) Merged "under control" criteria

These are checked per model, per window, and printed in `PILOT.json`.

- **U1 (throttle and coverage):** in-episode OS level 0 and powermetrics Nominal for all but at most 1 member; SMC coverage ≥ 99 % with no gap > 2 s; gate timeouts ≤ 2 per window.
- **U2 (start state):** every release meets T_slow ≤ T_ref + δ and |dT/dt| ≤ 0.2 °C/min; the range of release T_slow across a model's members is ≤ 3.0 °C.
- **U3 (identical work):**
  - every within-window exact pair has |ΔE| ≤ max(6 J, 0.15 % of E) and Δ active clock ≤ 0.5 %;
  - from at least 6 pairs over at least 2 new-protocol windows: mean normalized |ΔE| ≤ 0.25 %, with the 90 % CI inside ±0.5 %;
  - anchor σ_w among new-protocol sessions (K ≥ 3) ≤ 6 J.
- **U4 (state sensitivity):** |β_T| × release-T range ≤ 0.1 × min per-pair s_r, with β_T taken from the contrast and anchor pairs.
- **U5 (residual independence; benign, m ≥ 6 per model × pair):**
  - |corr(residual, release T)| ≤ 0.4, with the 90 % CI including 0;
  - the 90 % CI of the per-turn residual slope on turn index lies within ±1 J/turn × (mean turn energy / Qwen3-30B mean turn energy);
  - early-to-late change ≤ 0.37 % of mean episode energy.

**Consequences:**
- Failing U1-U3 labels the window "thermal protocol not met", and its new-model members enter no held-out pool.
- Failing U4-U5 marks the cell's calibration unresolved.
- The clock correlation is printed, never adjusted for (`cf1baad2` Ruling (2)).

### (e) Must-build list, in order

1. **R0 instruments and checks** (by day, no window armed): an SMC key enumeration script and run; `device_info` and wired limit; NLL coherence per model (bar ≤ 3.0 nats/token); the template round-trip rewrite count per model; an `ls` of D at `815b83c0`; offloads, then the N download; `pmset` and census under the chosen energy mode.
2. **XML tool-call parser** with schema-typed values (`endpoint.py`). D and F cannot act without it.
3. **SMC thermal sidecar** at 1 Hz in the episode, using `smc.Reader` unchanged.
4. **Hybrid-cache checkpoint** with per-turn snapshots (`prompt_cache.py`), plus an exactness test against a fresh prefill.
5. **Gate** (member and per-turn), holds, the token budget (new `EpisodeSpec` fields omitted when unset, so the pilot configs stay byte-identical), and **attribution of hold segments**.
6. **Kit v4 and protocol v4:** seeds by `model_id`, roster, identity pins, per-model sizing; frozen before R1 except for the R1-filled slots.
7. **Desk:** the thermal and phase tables, U1-U5, the contrast table, β_T, and a wrapper that runs the frozen alternative desk (`4d54cb47b`) and calibration script (`7fbd95e31`) per model, unedited.
8. **Synthetic dry run** of WQ; Opus executing review; Fable cold pass on items 2, 4 and 5; CI.
9. **R1 hardware rehearsal,** then the lead verifies the slots, then arm WQ.

### (f) Ed

**Physical, once before R1, then left alone for the series:**
- hard stand with ≥ 5 cm clearance, lid open;
- room thermostat fixed and the setpoint written down;
- a standalone ambient logger at the intake;
- battery at 100 % with Optimized Battery Charging off, on the 140 W adapter directly.
- High Power mode and/or an external fan (Fable C5) **only** if an R1 A/B on D's planning turn lengthens t_decline by ≥ 25 %, and only then. No fan-pinning utility.

**Questions only Ed can answer:**
1. Which "Qwen 3.8": the 27B (runnable) or Flash-Next (not runnable on the pinned stack)?
2. Next Thinking (recommended) or Instruct?
3. Is the 122B a third cell or a reserve?
4. Approve the 44.8 GB N download and the root offloads.
5. Accept the series length (WQ plus about 3-4 N windows plus about 5 D windows), or limit D to a screen, or allow 59,520 s maxima?
6. Is registration grade (m ≥ 39) wanted?

---

## 4. Revised design (one page)

**Models.**
- N: Qwen3-Next-80B-A3B-Thinking-4bit (44.8 GB; sampler 0.6/0.95/20/0; JSON tool calls).
- D: Qwen3.8-27B-8bit (on disk, `815b83c0`; 1.0/0.95/20/0; xhigh; XML tool calls).
- Anchors: Qwen3-30B-A3B-4bit, byte-identical.
- Reserve: Qwen3.5-122B-A10B-4bit, R1 screen only.
- Flash-Next: dropped with reason.
- Stack: pinned mlx 0.31.2 / mlx-lm 0.31.3. All episodes: context cap 40,960, 12 turns × 4,096, `episode_prefix` cache with per-turn hybrid checkpoints, token budget per model.

**Thermal and clock.**
- The SMC sidecar (die, heatsink, fan) runs at 1 Hz.
- Member gate after warmup on T_slow ≤ T_ref + δ, settled to ≤ 0.2 °C/min, with a window-local T_ref.
- Per-turn gate and D's token-count holds as in (c).
- Physical setup fixed for the series.
- No clock or temperature term in the score. Release temperature is a labelled sensitivity covariate. Phase clocks, β_T and PSTR minus rails are printed.

**Deciding experiment (in WQ).** Pilot-7 b-e25 and b-e18 replayed token-identically, gated (A) and ungated (B), in A B B A order, against a 2.97 J difference SD. The pre-declared rule in (c) keeps or drops the per-turn gate for every later window.

**Acceptance.** U1-U5 as in (d), with fixed numbers. Hardware and calibration are separate verdicts.

**Windows** (each maximum ≤ 44,640 s; `window_max_s`):
- pilot 9 (built);
- R0 and R1 by day;
- **WQ:** 20 members, span 26,077 s, maximum 43,800 s: 8 anchors + 4 contrast + 5 N + 3 D;
- then N1, D1, D2, N2, … one model per window with 6 anchors (N: 15 members gated or 23 ungated; D: 9).
- Target 20 held-out benign plus 4 sabotage per pair per model. N first (3-4 windows); D to calibration only on Ed's go (about 5 windows).

**Pre-registration.**
- Protocol v4 is fresh, with new calibration cells per model × pair.
- It imports the frozen sequence design (`4d54cb47b`) and the per-session LOO calibration (`7fbd95e31`) unchanged.
- WQ and R1 are selection data. Held-out data start at the first calibration window, after the v4 freeze commit is recorded before that desk is read.
- Pilots 8-9 stay the closed Qwen3-30B set under protocol v3. Anchors and contrast replays never enter any pool.

**Build order:** R0, then parser, sidecar, cache checkpoint, gates/holds/budget/attribution, kit and protocol v4, desk, dry run and reviews, R1, arm.
