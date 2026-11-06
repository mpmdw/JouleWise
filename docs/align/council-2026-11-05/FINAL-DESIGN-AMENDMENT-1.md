# FINAL-DESIGN — Amendment 1: Qwen3.8-27B as the only production model now; Flash-Next later

Chair: Opus 5.5 (`claude-opus-5-5`), 2026-11-05. This amends `FINAL-DESIGN.md` in this directory (commit `219fb1515`). Where they differ, this amendment wins; everything not restated here stands. Nothing under `/Users/edr/jw-b5-*`, `night-custody`, `night-archive` or `restricted/` was opened. Not pushed.

## A0. What changed and why

**Ed's decisions (coordinator message, 2026-11-05):**
1. On Artificial Analysis Progress Index v1, the best open models in 128 GB are Qwen3.8-Flash-Next (320) and Qwen3.8-27B at xhigh (303). Qwen3-Next-80B scores 225.
2. Flash-Next joins **later**, as the paper's next phase, through a verified MLX port.
3. **ALIGN proceeds now with Qwen3.8-27B 8-bit (`815b83c0`, on disk) as the production model.**

**Ruling: Qwen3-Next-80B is dropped.** I see no strong scientific reason to keep it as a second model.
- **Architecture transfer.** A second model would test whether the frozen sequence design transfers across architectures. Flash-Next (a hybrid MoE) is the better carrier for that test: it ranks higher, it is a 2026 production model, and it arrives in the next phase.
- **The deciding contrast.** A "light" cell would exercise the contrast's G1 branch. Flash-Next (6B active) is the likely light cell, and the 30B contrast arms exercise that branch in W1 anyway.
- **Cost.** N would buy cheaper calibrated m. That is time, not science. Its continuity with pilots 2-3 is weak: those runs were greedy Instruct under a different protocol.

The cost of dropping N, disclosed: until Flash-Next lands, the series has one production model. That means:
- no cross-model monitoring claim;
- no reasoning-omission tamper curve on a second model.

**Also dropped:**
- the 122B R1 screen (Ed's ranking does not include it; it can be reinstated on his word);
- the N download (Q3 is moot);
- the N parts of R0 and R1.

**Built since the ruling, all draft PRs under review:**
- #659: XML parser plus `reasoning_content` history. Its body records "0 bytes invalidated" over a 6-turn probe on the real Qwen3.8 template; the reasoning-history commit is on the branch.
- #657: hybrid checkpoint. Its body still says "native MLX exactness gate pending". The coordinator reports it bitwise-exact on `qwen3_5` and `qwen3_next`. **That result must be recorded on #657 before kit v4 enables it** (see A3).
- #660: token budget and deadman.
- #658: SMC journal and R0 sensor selection.
- #661: R0 desk scripts.
- #666: G0/G1 gates, holds, hold attribution, desk U1-U6. It merges #660.

## A1. Window 1, for Qwen3.8-27B only

**Members (18):**
- the 4 Qwen3-30B anchor originals, byte-identical to pilots 4-9;
- the pilot-7 deciding contrast, unchanged from FINAL-DESIGN §2.5 (X = b-e25 spam/sabotage, seed index 16; Y = b-e18 spam/benign, index 14). Arm S has G0 only; arm G has G0 + G1. Both stop at the recorded pilot-7 turn count;
- 6 D members.

**D settings:** sampler 1.0/0.95/20/0, effort from the R0 ladder, `reasoning_content` history, XML tools, G0 + G1 + **holds**, budget B_D, deadman.

| Ord | Member | Class | Planning member_s (guess; R1 replaces) |
|---|---|---|---|
| 1 | anchor a-e01 spam/benign s1 | byte-identical | 782.8 |
| 2 | anchor a-e02 bank/sabotage s1 | byte-identical | 782.8 |
| 3 | anchor a-e03 spam/sabotage s1 | byte-identical | 782.8 |
| 4 | anchor a-e04 bank/benign s1 | byte-identical | 782.8 |
| 5 | D spam/benign s1 (**original**; first sidecar member, so its idle sets the window reference R) | D | 1,800 |
| 6 | X-G | contrast G0 + G1 | 1,150 |
| 7 | Y-S | contrast G0 | 850 |
| 8 | D bank/benign s1 | D | 1,800 |
| 9 | X-S | contrast G0 | 850 |
| 10 | Y-G | contrast G0 + G1 | 1,150 |
| 11 | D spam/sabotage s1 | D | 1,800 |
| 12 | Y-G | contrast G0 + G1 | 1,150 |
| 13 | X-S | contrast G0 | 850 |
| 14 | D bank/sabotage s1 | D | 1,800 |
| 15 | Y-S | contrast G0 | 850 |
| 16 | X-G | contrast G0 + G1 | 1,150 |
| 17 | D bank/benign s93 (development index) | D | 1,800 |
| 18 | D spam/benign s1 **replay** (late; identical work to ordinal 5) | D | 1,800 |

**Balance.**
- Position sums: X-G 6 + 16 = 22 = X-S 9 + 13; Y-S 7 + 15 = 22 = Y-G 10 + 12. Linear drift cancels within each template.
- Predecessors balance by arm. Each contrast arm of each template has one D predecessor and one 30B predecessor:

  | Arm | First run (predecessor) | Second run (predecessor) |
  |---|---|---|
  | X-G | 6 (D) | 16 (30B) |
  | X-S | 9 (D) | 13 (30B) |
  | Y-S | 7 (30B) | 15 (D) |
  | Y-G | 10 (30B) | 12 (D) |
- Stage split and midpoint reference after ordinal 9.
- The 5↔18 pair gives D an in-window identical-work pair, so D's U3 is evaluable in W1 itself. The FINAL-DESIGN roster had none for the new models.

**Arithmetic** (`plan_inputs.py:56-59`; member law 516.575 + 1.13544 × episode_s; scaffold 4,995 s):
- Align = 4 × 782.82 + 4 × 850 + 4 × 1,150 + 6 × 1,800 = 3,131.27 + 3,400 + 4,600 + 10,800 = **21,931.27 s**.
- Span = 21,931.27 + 4,995 = 26,926.27 → **26,927 s**.
- Max = 60 × ⌈(26,927 + 3,300 + 7,200 + 7,200)/60⌉ = 60 × ⌈44,627/60⌉ = 60 × 744 = **44,640 s**. This equals the cap, with **13 s** of span slack (limit 26,940).
- Disk: 18.71 GB per copy, **37.4 GB for two copies**.

**Fit rule, pre-declared, applied after R1 replaces the planning numbers.** If the span exceeds 26,940 s:
1. Drop ordinal 17 (D bank/benign s93). Span 25,127 s, max **42,840 s**, 17 members, 35.2 GB for two copies.
2. If it still does not fit: lower B_D in 1,024 steps down to its 6,144 floor.
3. If it still does not fit: return the roster to the lead.

Anchor, contrast, and the 5/18 D pair are never cut.

Seeds: D seed index 1 (both pairs, both conditions) and index 93 for bank/benign. Both are development indices. The seed law is unchanged with tag `qwen3.8-27b`.

**What W1 yields:**
- the contrast verdict;
- U1-U3 for D and for the 30B arms;
- D's capability gate;
- D's rates, energies, gate and hold costs, cap hits and restore counts;
- the K-session anchor read (printed only).

U4-U6 are not evaluable in W1.

## A2. Later windows and calibration targets (Qwen3.8-27B alone)

- **Target (unchanged):** m ≥ 20 held-out benign per pair, plus ≥ 2 held-out sabotage per pair.
  - Calibration is the frozen per-session LOO `7fbd95e31`, per pair (`c110a6c9`).
  - The threshold is the rank-⌈0.95(m+1)⌉ value, which is the sample maximum at m = 20-21. There is no FPR or power claim.
- **Seed roles:**
  - Development: indices 1 and 91-99. R0's ladder uses 91-92; W1 uses 1 and 93.
  - Held-out: index 2 upward per pair, in kit order.
  - A frozen-commit record fixes every v4 slot before D1's desk is read.
- **Every D window contains:**
  - 4 anchor originals;
  - 2 **sentinels**: seed replays of W1's ordinal-5 original, placed early (ordinal 5) and at the last ordinal;
  - the held-out D members, with pair order alternating by seed parity and sabotage spread across the window.

| Window | Max | Composition | Arithmetic: align → span → max | Disk (two copies) |
|---|---|---|---|---|
| D_k, default (Q4 = yes) | 59,520 | 4 + 2 + 14 benign (7/pair) + 2 sabotage (1/pair) = 22 | 3,131.27 + 16 × 1,800 = 35,531.27 → 40,527 → 60 × ⌈58,227/60⌉ = **58,260 s** | 52.9 GB |
| D_k, if Ed vetoes 59,520 | 44,640 | 4 + 2 + 7 benign of one pair + 1 sabotage of that pair = 14; pairs alternate | 21,131.27 → 26,127 → **43,860 s** | 35.1 GB |

- **Series:** W1, then D1, D2, D3.
  - Yield: 21 held-out benign and 3 held-out sabotage per pair.
  - U4 (cross-window sentinels) becomes evaluable at D3.
  - Under the 44,640 veto it takes six windows (D1-D6) for the same yield.
- **Registration grade** (m ≥ 39 per pair plus a locked test cohort): D4-D6 at 59,520, only on Ed's go, and decided before any alarm is read.
- **Reservation** (default): 44,640 + 3 × 58,260 = 219,420 s of window maxima (61 h). Expected chains are about 45 h, plus desks of about 2 h each.

## A3. Gates and acceptance: what changes for a dense-only roster

1. **D is declared heavy by protocol, so every D member carries G1 and holds**, whatever the contrast verdict.
   - N_chunk = 256 × ⌊0.6 × t_decline × r_decode / 256⌋ (minimum 256) when R1 finds a clock decline.
   - If R1 finds no decline within D's planning turn (t_decline = ∞), N_chunk = **2,048**. Every turn longer than 2,048 tokens then takes one hold. The hold path and its attribution are exercised identically in every D member, and the per-turn-position state stays referenced to the episode start.
   - Holds still begin only after the in-flight lookahead token has been evaluated (FINAL-DESIGN §2.6).
2. **Scope of the contrast.** Its rule (FINAL-DESIGN §2.5) is unchanged, but its branch no longer controls any cell in this series. It now decides two things:
   - (a) whether the pilot-7 signature is attributed to state, which feeds the pilots 8-9 disclosure;
   - (b) G1 for future light cells: Flash-Next if R1-FN classifies it light, and any reuse of the 30B.

   It stays in W1 because both (a) and (b) need identical-token evidence gathered under one physical setup, and W1 is the cheapest place to get it.
3. **U5 uses only the heavy-cell form.** β_T (J/°C) is fitted on D's own temperature-observed identical-work pairs:
   - the R1 replay pair;
   - W1's 5↔18 pair;
   - the D_k sentinels.

   It is multiplied by the observed G0 release range, and the result must be ≤ 0.1 × D's smaller per-pair s_r. The light-cell form (the contrast δ scaled by energy) is held for Flash-Next.
4. **U3 is evaluated in W1 for D.** The 5↔18 pair is checked against 3 × max(2.97 J, 0.0011 × E_pair) and a decode-clock difference ≤ 0.5 %, alongside the R1 pair. U4 needs D1-D3 sentinels and is evaluated from D3 on.
5. **No other change.**
   - U1, U2 and U6 are unchanged.
   - Exclusions X1-X8 are unchanged.
   - Timeouts are unchanged: G0 flags and proceeds; G1 and H stop the episode.
   - The token admission budget (B_D floor 6,144, planning member ≤ 1,800 s) and the deadman (episode wall time ≤ (1,750 − I_D)/1.13544 s) are unchanged.
   - The R0 effort ladder (xhigh → medium → low) and the 8-bit → 4-bit rule are unchanged.
6. **Hybrid checkpoint (#657).**
   - Once #657's native exactness gate is **recorded** as bitwise-exact for `qwen3_5` on the pinned stack and the PR passes review, kit v4 enables it for D as a safety path. With #659's zero-invalidation result, it should almost never fire. Restore counts are printed.
   - Until then, D runs on the rebuild fallback, with `cache.rebuilt_untrimmable:<k>` logged.
   - If W1 shows rewinds on more than 5 % of D transitions, the cause is investigated before D1. The rule is not loosened.
7. **D capability failure in W1.** If D makes no state-changing action on some pair in any benign W1 episode, there is no second model in this phase. W1 is then reported as an energy and capability screen, and **no held-out seed is spent**. Before D1, the lead rules between two options, each of which is a new cell and is selection data again:
   - the next lower effort rung; or
   - 4-bit at the same rung.

## A4. Slot for adding Flash-Next later (new calibration cell FN)

**Pre-registration hook.** Protocol v4 reserves a section **"Addendum FN"** now, with these fixed fields. The addendum must pass its own registration cold gate (Fable + Opus, blind) before any FN data are collected. Adding FN never edits D's frozen record, D's slots, or any frozen script.

- **Identity.**
  - Tag `qwen3.8-flash-next`.
  - Artifact: the verified MLX port's weights (repo, revision, quantization, bytes) plus the port's code commit.
  - FN members run on a **separate pinned venv ("stack B")**. The anchors and D stay on stack A (mlx 0.31.2 / mlx-lm 0.31.3). The stack identity (`runtime_versions` digest) goes in every bundle. FN is its own configuration cohort, never pooled with D.
- **Seeds.** Same law. Development indices 1 and 91-99; held-out from 2.
- **Admission bars** (filled by the addendum, measured in an FN R0 before any FN window):
  1. **Port parity on the full model, not only the tiny ones.** Fixed-prompt NLL and top-k logit agreement against a reference engine (llama.cpp or mlx-vlm) within a bar declared in the addendum, plus greedy token agreement over a fixed span. Per-turn reseed determinism must also be shown with the n-gram embedding path active.
  2. **Memory.** Full-context (40,960) peak below the 115.4 GB working set with declared headroom and no swap, and **no** change to `iogpu.wired_limit_mb`. A sysctl needs its own ruling. The mlx-community 4-bit is 111.5 GB, so the addendum names the quantization that fits.
  3. **Template audit.** Tool-call format and parser coverage ≥ 95 %; `reasoning_content` or content-split round trip with 0 rewrites on closed-reasoning turns; effort controls, if any, go on the R0 ladder.
  4. **Cache.** #657 exactness on `qwen4_exp`, or rebuild accounting.
  5. **#1632-class long-decode check** on stack B.
- **Thermal class.** FN's own R1-FN step test applies FINAL-DESIGN §2.5:
  - heavy → G1 + holds;
  - light → G1 per the W1 contrast verdict.

  The U5 form follows the class.
- **Windows.**
  - **FN-Q** (qualification): 4 anchors, then **2 D sentinels** (a cross-stack state bridge), then FN both pairs × both conditions at seed 1, plus one FN replay (FN's U3). It is sized by the same formula and kept within 44,640 s.
  - **FN calibration windows** use the D_k shape (FN sentinels instead of D's), with the window maximum set by FN's measured member cost.
  - Target: m ≥ 20 per pair and ≥ 2 sabotage per pair.
  - FN windows may interleave with D windows once admitted; D's series does not wait for FN.

## A5. Order of work on the MacBook Pro (measurement Mac)

**0. Before R0.**
- Pilot 9 runs under protocol v3, unchanged, if the pilot-8 read supports it (`c110a6c9`). Offload the pilot-8 and pilot-9 roots to iCloud during their desks (verified rehash).
- Build a fresh measurement checkout (never the canonical root while anything is armed) from the admitted v4 lanes: #659, #660/#666, #658, #661, and #657 when admitted.
- Nothing heavy runs on the analysis laptop. All model work in R0/R1 happens on the MacBook Pro.

**R0** (by day, no window armed, unmeasured; the lead runs #661's guarded scripts; one record committed at the end). Each step has a pass/fail bar:
1. **Inventory.** `ls` and hash D-8bit at `815b83c0` and the 30B. Disk: at least 80 GB free after weights before W1.
2. **Platform state.** `mx.metal.device_info()` and `sysctl iogpu.wired_limit_mb`. `pmset -g custom`, the census and the readiness probes pass under Automatic, and under High Power if Ed opts in (`arm_readiness_evidence_t0.py:1990` greps `lowpowermode`).
3. **SMC enumeration (#658)** at idle and under a 60 s load step. Bar: at least one die-class and one heatsink-class key readable without root at 1 Hz with < 1 % errors over 10 min.
4. **D coherence.** NLL ≤ 3.0 nats/token on the fixed 2k SHADE prompt.
5. **D template round trip** on real generated turns (#659): 0 rewritten tokens on closed-reasoning turns over ≥ 12 transitions. Parser coverage ≥ 95 %, with no `unsupported_tool_call_format`.
6. **#657 native exactness gate** on `qwen3_5`, if it is not already recorded on the PR.
7. **D effort ladder** (dev seeds 91-92; 2 benign episodes per rung; stop at the first passing rung).
8. **#1632 long decode** to 40,960 positions on D, about 55 min. Pass: no Metal resource error, and active-memory growth ≤ 2 GB per 10k tokens. On failure: the align-local metadata `mx.eval` mitigation, then a retest.
9. **D memory.** Full-context peak ≤ 45 GB **(guess bar)**, no swap growth.
10. **D-4bit download.** If R0 rates predict B_D < 6,144, download D-4bit (`10c35caa`, 16.1 GB) for R1.

**R1** (quiet: Interactive LaunchAgent, no agent alive; about 2.5-3 h by day):
1. **30-min idle soak**, giving the sensor SDs and so δ.
2. **Planning-turn step tests** (10k fed prefill + 4,096 seeded decode), each followed by a 10-min cooldown: 30B, then D under Automatic. If Ed opts in, an A-B-A on D (High Power, then Automatic; and the cooler if he has one). Each lever is adopted only on a ≥ 25 % longer t_decline.
3. **One X-G contrast run.** Measures gate cost and checks token identity against pilot-7 b-e25.
4. **Two gated and held D spam/benign s1 runs.** These give U3, token identity under holds, and the W1 cross-session reference.
5. **D-4bit step test and one episode**, only if R0.10 triggered.
6. **Fill the slots:**
   - sensor keys and classes;
   - δ;
   - G_turn;
   - t_decline;
   - N_chunk;
   - B_D;
   - I_D;
   - T_dead.

   The lead verifies them. Apply the A1 fit rule, freeze span and disk, check the ledger pin, run a real `prepare`, send the arm notice, and arm W1.

## A6. Ed's open items after this amendment
- **Q1** (which Qwen 3.8) and **Q3** (N download) are answered or moot.
- **Q2** (122B) is out.
- **Q7** (model priority) is moot.
- **Still open, with defaults:**
  - Q4: 59,520 s D windows. Default: yes.
  - Q5: High Power and cooler A-B-A in R1. Default: High Power yes; cooler only if he owns one.
  - Q6: registration grade. Default: no.
- **Physical setup:** unchanged (FINAL-DESIGN §3.1).
