# ALIGN next-window design, round 2 (cross-critique), Fable 5.1 seat

Read in full: `r1-opus.md`, `r1-sol.md`, my `r1-fable.md`. Every claim below that I call verified was checked today against the checkout (`e328f0e72`), `origin/main` (`92026c184`), the named lanes, the data-repo review branch, or the web (HF raw files and API, GitHub PR pages). Nothing under block-5, night-custody, night-archive or restricted/ was opened. No file of another seat was edited.

New fact that changes all three designs: record `c110a6c9` (branch `origin/docs/2026-11-05-magistrate-c110a6c9`) ruled the calibration review's B1 **rejected: pooling stays per pair** ("benign LOO score spreads differ by pair"), froze the calibration script at `7fbd95e31`, and admitted the pilot-9 kit `c9a0a3943`. Sol's "pooling-authority issue" is therefore settled, and Opus's and my "run pilot 9 first" stands.

---

## 1. Errors in the other two designs

### 1.1 Opus (`r1-opus.md`)

| # | Where | Claim | Finding |
|---|---|---|---|
| O1 | §1.3 "Why these are the top", §1.3 fallbacks | "The Thinking variant [of Qwen3-Next] is the one that acts." | **Unsupported.** No record has run Next-Thinking. Pilot 2 (greedy): Next-Instruct acted in 3 of 4 episodes (RS:981); pilot 3 (greedy): 0-2 state changes (`af17111e:36`). Instruct under sampling is untested; Thinking is untested at all. The choice may be right, but it is a bet, not a record. |
| O2 | §4 item 4 ("hybrid checkpoint") and R3 | "The Qwen3.5/3.8 and Next thinking templates re-render reasoning and tool calls ... That would mean a full re-prefill every turn." Checkpoint build called "the critical build item" for F and D. | **Half wrong, and the half that is right is caused by Opus's own N choice.** The Qwen3.8-27B template keeps earlier reasoning by default: `{%- if preserve_thinking is undefined or preserve_thinking is true or loop.index0 > ns.last_query_index %}` (HF `Qwen/Qwen3.8-27B/raw/main/chat_template.jinja`), so D's prefix is append-only unless the XML tool-call round trip rewrites tokens (Opus's own R0 check decides that). The **Next-Thinking** template does strip earlier reasoning (`{%- if loop.index0 > ns.last_query_index %}`, mlx-community Thinking-4bit `chat_template.jinja`), so with Opus's N every turn rewinds into the generated region and `prompt_cache.py:62-74` rebuilds the whole non-trimmable cache. Next-**Instruct** is append-only (`e1308804:57`: "C is append-only"). So the checkpoint is mandatory only if Next-Thinking is chosen; with Instruct it is optional. |
| O3 | §3.2 W1 roster, §0 | W1 keeps anchors at ordinals 1-4 only and says they sit "at the same ordinals as in pilots 4-9". | The K-session link in pilots 4-9 is **8** same-ordinal anchors (1-4 and the replays 9, 14, 19, 28; record `cf1baad2` "Pilot-8 kit build"). Dropping the four replays removes the within-window identical-work channel for the 30B (I4′ replay identity, same-position noise 2.1 J) and halves the anchor set behind "session effect within ±6 J". U2 then rests on two contrast pairs. |
| O4 | §1.1 "Models already on disk ... standing rule `RS:1190`" | RS:1190 as a do-not-delete rule. | RS:1190 is the record of the 10-25 deletion and the re-download order; the re-download itself is RS:349 (revision `815b83c0`, 28 GB, 2026-10-28). The conclusion (D is on disk) is right; the citation is not the rule. Minor. |
| O5 | §1.1 Memory | `SUMMARY.md:29` on main | `docs/design/bytes_pilot/SUMMARY.md` is not in `origin/main` (git refuses the path); it is in the lane checkout. Content verified there: wired limit 0, recommended working set 115.4 GB, largest MLX peak 71.5 GB. Minor. |
| O6 | §2.3 interleaving | "Models alternate member by member." | Not an error but a cost Opus does not price: with N-4bit (44.8), D (29.5) and the 30B (17.2) the page cache holds all three (91 GB) only while no process is resident; each switch is a cold re-map of up to 45 GB in `prepare`. Since `prepare` precedes `idle_baseline` (`controller.py:31-32`), the heat lands inside the gate window, which is fine, but the 300 s idle plus gate must then cover the load; add it to the member law. |
| O7 | §1.5 | "#1632 is a risk on 0.31.3." | **Verified and important.** PR #1632 ("Fix unbounded ArraysCache metadata graph during decode", merged 2026-08-22) is after 0.31.3 (2026-04-22); the failure is `[metal::malloc] Resource limit (499000) exceeded` in long decodes. Pilot 3's Next decodes were 31-54 s episodes (`af17111e:14`), far from 4,096-token turns. Opus's R1 check (12 × 4,096 decodes per hybrid model) is necessary; I adopt it. |
| O8 | §2.1 item 3 | "In pilot 3 the clock declined about 20 s before the first positive reading (`P3:128-129`), in the 170-180 s bin (`c9ac22ae` l.38)." | Verified (`pilot_protocol_v3.md:128-129`; `c9ac22ae:38`, which also gives the capped prefill clock 1,176-1,313 MHz). |
| O9 | §5 R11 | `arm_readiness_evidence_t0.py:1990` greps `lowpowermode 0` while macOS 26 reports `powermode`. | Verified (`:1990`; `environment.py:607-611`). Since pilots arm under `powermode 0`, this probe is evidently not on the arming path or is satisfied another way; Opus is right that High Power must be rehearsed against the probes. |

Arithmetic checked and right: window maximum 60·⌈(26,492 + 17,700)/60⌉ = 44,220 s; disk 36.8 GB for two copies; D planning member 1,774 s at B_D = 6,144.

### 1.2 Sol (`r1-sol.md`)

| # | Where | Claim | Finding |
|---|---|---|---|
| S1 | §4 "Duration and disk budget", table | WQ envelope 42,355 s and production windows 43,835 s, "headroom to 44,640 s" 2,285 s and 805 s; "hard stop remains 44,640 s". | **Conflates the programmed span with the window maximum.** `window_max_s = 60·⌈(span + 3,300 + 7,200 + 7,200)/60⌉` (`joulewise/b6/plan_inputs.py:56-59`; `b5/plan.py:59,66,67`). Pilot 8's 44,640 s came from a 26,914 s span (`cf1baad2` ARM). Sol's 42,355 s span gives a 60,060 s maximum and the 32-member windows 61,560 s (17.1 h). Either the 44,640 s ceiling is honoured and Sol's rosters shrink by about 40 % (to roughly 16-18 members plus anchors), or the maxima are 60k s. The five-window "60.47 h of collection reservation" is also understated for the same reason. |
| S2 | §2 primary roster, D fallback | Fallback `mlx-community/Qwen3.5-27B-4bit`, "exact revision unverified". | Verified on disk (RS:253: Qwen3.5 2B/4B/9B/27B-4bit downloaded, run on 0.31.3). Not an error, but `Qwen3.8-27B-4bit` (same `qwen3_5` architecture, the newer weights, 16.1 GB) is the fallback that keeps the model; Qwen3.5-27B is a different model and a different cell. |
| S3 | §2 "D ... Treat neither number as measured peak memory" and §4 memory arithmetic | R = 28,579,478,528 B; download 29,531,521,322 B; KV 2,684,354,560 B. | Verified (`origin/desk/2026-10-29-byext-slots`: `.codex-report/BY-EXT-2.md` "R: 28,579,478,528"; `slots.json` `size_bytes 29531521322`, revision `815b83c0df8f…`). Correct. |
| S4 | §3 "The current lifecycle is idle baseline → warmup → measured run, and ALIGN warmup currently renders a condition-specific task prompt." | | **Verified and important** (`workload.py:264-269`: `prompt_text=self.task.system_prompt(self.spec.condition) + "\n" + self.task.user_prompt()`). The warmup is a 6,347-7,102-token prefill of the condition's own prompt immediately before the episode, so (i) my r1 gate in `idle_baseline` sat in the wrong place, and (ii) warmup heat differs by condition by 755 tokens. Both other seats put the gate after warmup; I adopt that. |
| S5 | §4 "pooling-authority issue ... The chair must settle" | | Settled since: `c110a6c9` rejected B1 (per pair stays). Not an error at writing time. |
| S6 | §2 feasibility, Next peak budget "80 GiB provisional" | | Over-conservative but harmless: the BYTES pilot measured the Instruct-4bit MLX peak at 47.0 GB at 2.5k (SUMMARY.md row), so about 49 GB at the cap. Sol had no network and says so. |
| S7 | §4 WQ roster "proposed seed indices 101-102 in a new versioned namespace" | | Unnecessary: the seed law already hashes `model_id` (`pilot_protocol_v3.md`, seed-law paragraph; kit `:125`), so indices 1-2 under a new model id are already disjoint from every 30B seed. A new namespace adds a second law to review for no gain. Minor. |
| S8 | §2 "Capability gate" | | Not an error; adopted (below). |

Sol's claims that needed the web (its list in §2): the two upstream repos exist (`Qwen/Qwen3-Next-80B-A3B-Instruct`, `Qwen/Qwen3.8-27B`); Qwen3.8-27B is `qwen3_5` top-level / `qwen3_5_text` text config, 64 layers, 16 full-attention, 4 KV heads, head_dim 256, 262,144 context, thinking default on with `reasoning_effort` default `xhigh` rendered as a system-prompt line; the Thinking Next MLX repo exists (`9a2b4634…`, 2025-09-13); mlx-lm latest is 0.32.2; `qwen3_next` landed in 0.28.0 (release 17 Sep, "Adding Qwen3 Next"), `qwen3_5`/`qwen3_5_moe` in 0.30.7; Flash-Next needs `qwen4_exp`, mlx-lm PR #1788 is open since 2026-08-26 ("await verification"); Nemotron: not re-checked.

### 1.3 My own round-1 errors (corrected in §4)

- F1: I wrote that Qwen3.8-27B-8bit was deleted and the re-download owed. It was re-downloaded 2026-10-28 (RS:349, `815b83c0`, 28 GB, `/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit`). Disk and R1 change accordingly.
- F2: I missed that Qwen3.8 emits **XML tool calls** (`<tool_call>\n<function=name>\n<parameter=key>…`), which `endpoint.py` flags as `unsupported_tool_call_format` (`:155-158`; the parser is JSON-only, `:60,129,143`). Without Opus's parser D cannot act. Next-Instruct and Next-Thinking use JSON (both templates verified).
- F3: Gate placement (S4 above).
- F4: I did not price the `#1632` risk (O7).

---

## 2. Best ideas adopted from the others

From Opus:
1. **The deciding experiment** (§2.2): pilot-7 b-e25 and b-e18 replayed token-identically, gated (A) and ungated (B), in ABBA order, with the rule fixed now (both |ΔE| ≥ 10 J and a per-turn trend → state confirmed; both ≤ 6 J and no trend → gates dropped from the next window; else keep and add two pairs). It is the only cheap way to put identical tokens at two thermal states. I add: keep B byte-identical to pilot 7 so it is also a 5th/6th K-session anchor for spam.
2. **Token budget instead of the wall guard** for new cells (`max_episode_decode_tokens`): trajectories cannot depend on machine speed; replays stay exact. Anchors keep the 120 s guard byte-identically.
3. **S_fast / S_slow sensor derivation and θ = reference + max(1.0 °C, 3 × idle SD)** (§2.4): a rule for choosing the gate sensor from the R0 step response instead of my guessed "GPU die sensor".
4. **XML tool-call parser** and the **template round-trip count of rewritten tokens** in R0.
5. **R1 long-decode check for #1632** and the fallback of a second pinned venv only for production members.
6. **High Power mode** as an R1-tested option (verified: a System Settings toggle on 14- and 16-inch M3 Max; Apple's text says it lets the fans run faster for sustained work). It is the one legitimate fan control; it must be on for the whole series or not at all, and rehearsed against the census and readiness probes (O9).
7. **U2 scale rule** 3 × max(2.97 J, 0.11 % of E) so the identical-work bar scales to 8-36 kJ episodes.

From Sol:
8. **Gate after warmup, immediately before the episode start stamp**, plus a **neutral warmup** for new cells (the same fixed-token prefill for both conditions) so warmup heat does not carry the condition label.
9. **Capability gate** before any calibration spend: a state-changing action on each pair in at least one benign episode and one main-task score improved from its initial state; otherwise the model is reported as an energy/capability screen.
10. **Fixed-work sentinels** (three templates: decode-heavy, prefill-heavy, cache-rewrite tool sequence; frozen token IDs and tool I/O) as the production-series identical-work channel, with the cross-window equivalence test (≥ 6 pairs over ≥ 2 windows; |mean| ≤ 0.25 %, SD ≤ 0.25 %, 90 % t-interval inside ±0.5 %).
11. **Separate training/calibration split with an immutable coefficient artefact** written by a deterministic fitter after the training members and before the first calibration member (no refitting per window).
12. **Hard operational stop** on any continuous episode (540 s) and the duty ceiling as a scheduling rule, both disclosed as incompleteness, never as a low-energy episode.
13. **Telemetry coverage bars** (≥ 99 % interval coverage; no die-telemetry gap > 2 s; missing is unavailable, never zero).

From both: the pilot-8/9 30B population stays closed under protocol v3; no frozen script is edited; new code imports the frozen alternative desk and calibration script.

---

## 3. Contested decisions

**(a) Model set and quantizations.**
- **Next: Instruct 4-bit first, not Thinking, not 8-bit.** Reasons: Instruct-4bit is on disk at the pilot-3 revision, append-only under the prompt cache (`e1308804:57`), JSON tool calls the parser already handles, measured MLX peak 47.0 GB; Thinking strips earlier reasoning every turn (verified), which on a non-trimmable cache means Opus's checkpoint build before any window, plus an untested capability claim (O1). 8-bit (84.7 GB download against 82 GB free at the last record, `c110a6c9`; peak about 89 GB, never run here) is a second cell later if Ed wants precision. If Ed's question *needs* hidden reasoning tokens on Next (the tamper grid), Thinking-4bit is the model and the checkpoint build moves to the critical path; that is a question for Ed (§3f), not for the council.
- **Qwen3.8-27B 8-bit in**, with the XML parser; `reasoning_effort` fixed at `low` for the first cell (the template renders it as a system-prompt line, verified), re-decided after WQ by the pre-fixed cap-hit rule (Opus: > 50 % of turns at the cap → one step). 4-bit is the thermal fallback by the R1 rule.
- **122B: out of the first two cells, in as the reserve and the third cell** if Ed wants three models. It is on disk, measured peak 71.5 GB, decode 42.6 tok/s (SUMMARY.md), and it is the largest MoE that fits; but the 10-27 registration ranks Qwen3.8-27B above it, and a third cell costs two more windows. Not in WQ.
- **Flash-Next: truly infeasible now.** `qwen4_exp` is not in any mlx-lm release (0.32.2); PR #1788 open since 2026-08-26; the mlx-community 4-bit is 111.5 GB, 97 % of the 115.4 GB working set. All three seats agree; Ed is told.

**(b) Window plan.** Qualification-and-deciding window first, then one model per window. WQ = 28 members in the pilot-8 shape: the **8** 30B anchors at ordinals 1-4, 9, 14, 19, 28 (not Opus's 4); the **4** pilot-7 contrast members (ABBA); **8 N** (seeds 1-2 × 2 pairs × 2 conditions) and **6 D** (seed 1 × 2 pairs × 2 conditions + seed 2 benign × 2 pairs). Budget: 8 × 783 + 4 × 900 + 8 × 800 + 6 × 1,100 = 22,864 s align + 4,995 s scaffold = **27,859 s**, window maximum **45,600 s** (16 min over 44,640; if the ceiling is literal, D drops to 4 and the span is 25,659 s, maximum 43,380 s). WQ is selection data for both models. Then the series **N1, D1, D2, N2**, each 8 anchors + 20 new-model members (16 held-out benign, 8 per pair, + 4 sabotage, 2 per pair) in the pilot-8 ordinals; the first window of each model also carries the 6 training benign from WQ in the frozen-fit artefact. **Calibration target: m = 16 held-out benign per pair after two windows plus WQ's 2 = still below 19**, so a fifth and sixth window (10 benign per pair, pilot-8 shape) per model are the registration-grade extension if Ed wants a finite split threshold (k = 20 at m = 20 is the sample maximum; k = 38 at m = 39 is the first non-maximum rank). I say so plainly rather than promise thresholds from four windows. Pilot 9 runs first under protocol v3, unchanged.

**(c) Gate variable and form.** Variable: the S_slow sensor from R0 (heatsink-level, τ ≤ 300 s) with S_fast as a secondary condition, window-local reference taken after the scaffold; fallback thermometer the idle package power. Form, by member class: (1) **start-state gate after neutral warmup, before the episode stamp**, for every new-model member (cap 600 s, then flag; Sol's refusal variant only in production windows); (2) **per-turn gate to the episode's own start state** plus **chunked decode with holds** only for D and for the contrast A-arm in WQ; whether per-turn gates continue is decided by the WQ contrast under Opus's rule. Token budget for all new cells; the 120 s wall guard stays only on the byte-identical anchors and contrast-B members; 540 s operational stop on every new-cell episode.

**(d) Merged acceptance set ("under control"), per model per window, printed in PILOT.json, never a hypothesis test:**
- U1 state: OS level 0 and powermetrics Nominal at every in-episode sample in ≥ 27/28 members; gate timeouts ≤ 2 members (start gate) and ≤ 1 per 50 turns (per-turn gate); start-sensor range across the window ≤ 3.0 °C; telemetry coverage ≥ 99 %, no sensor gap > 2 s.
- U2 identical work: every within-window replay or sentinel pair |ΔE_GPU| ≤ 3 × max(2.97 J, 0.0011 × E); the 30B anchors' session effect within ±6 J of the pilot 6-9 mean; moment σ_w over all sessions ≤ 6 J.
- U3 no drift with turn index: 90 % CI of the pooled benign per-turn residual slope within ±1 J/turn × (model mean turn energy ÷ 30B mean turn energy).
- U4 no state dependence: for cells with m ≥ 6, corr(residual, start-sensor) 90 % bootstrap CI includes 0 and |r| ≤ 0.4; corr(residual, mean clock) printed beside it; |β_T| × start-sensor range ≤ 0.1 × the pair's s_r.
- U5 cross-window (production series only): ≥ 6 matched sentinel pairs over ≥ 2 windows with |mean| ≤ 0.25 %, SD ≤ 0.25 %, 90 % t-interval inside ±0.5 %.
- U6 calibration flag (separate verdict): fitted early-to-late residual change on fresh benign > 10 J per 2.7 kJ-equivalent trajectory → "calibration unresolved" even if U1-U5 pass.
A failing cell is printed "state not controlled" and enters no calibration pool; a failing window is still a complete non-claim pilot.

**(e) Must-build list, in order** (new lane from the pilot-9 lane; `joulewise/align/*` is unpinned; no calibration-pinned file touched; a new align-only campaign policy file instead of editing `quiet_mac_p2_b5.json`):
1. `scripts/align_smc_enumerate.py` and the R0 run (gate sensor identity is a hard prerequisite).
2. XML tool-call parser in `endpoint.py` + template round-trip test (D cannot act without it).
3. `joulewise/align/apple/thermal_gate.py`: 1 Hz SMC sidecar, start gate after warmup, neutral warmup, token budget (`max_episode_decode_tokens`), operational stop; `EpisodeSpec` fields unset for anchors so pilot 4-9 configs stay byte-identical.
4. Kit v4 (`configs/campaigns/align_pilot_v4/`): blocks per model, WQ roster incl. contrast members (B byte-identical to pilot 7), identity pins for the three models, sizing from R1.
5. Desk: per-turn thermal table, U1-U6, contrast table, `--compare-session` against pilot 7; frozen alternative desk and calibration script imported unchanged, run per model id.
6. Per-turn gate, chunked holds and hold-segment attribution (D only; can slip to D1 if R1 shows D-4bit passes without holds).
7. Fixed-fit split calibration driver and sentinel runner (needed from N1, not WQ).
8. Hybrid cache checkpoint: only if Next-Thinking is chosen or R0's round trip rewrites tokens for D.
Rehearsal: R0 by day (enumeration, `mtp` key scan, NLL ≤ 3.0 nats bar, round trip, greedy exactness, `pmset` under each mode), R1 under an Interactive LaunchAgent (idle soak, step tests per model, 12 × 4,096 decodes per hybrid model, one gated episode per model, replays), production-shaped synthetic desk on the WQ roster. Gates: Sol build, Opus executing review, cold Fable on gate/attribution/parser/checkpoint, registration cold gate on protocol v4, then arm.

**(f) Ed, physically and by answer.** Once, before R1, then untouched for the series: hard stand with clearance, lid open, fixed HVAC setpoint with an ambient logger at the intake, battery 100 % with Optimized Battery Charging off, the 140 W MagSafe; no third-party fan utility. Decide: (1) which "Qwen 3.8": 27B (runnable) or Flash-Next (not runnable on the pinned stack); (2) whether the Next question needs hidden reasoning (then Thinking-4bit and the checkpoint build) or production tool use suffices (Instruct-4bit, no new cache code); (3) High Power mode on for the whole series, yes or no (R1 shows whether it buys headroom); (4) 8-bit Next later as a precision cell, and the 85 GB download it needs; (5) 122B as a third model, yes or no; (6) accept a 45,600 s maximum for WQ or cut D to 4 members; (7) approve the offloads that free the disk.

---

## 4. Revised recommended design (one page)

**Models.** N = `mlx-community/Qwen3-Next-80B-A3B-Instruct-4bit` @ `d8a069bf` (44.8 GB, peak ≈ 49 GB, on disk, 0.31.3, JSON tools, append-only cache). D = `mlx-community/Qwen3.8-27B-8bit` @ `815b83c0` (29.5 GB, peak ≈ 34 GB, on disk, 0.31.3, XML tools, `reasoning_effort: low`, thinking sampler 1.0/0.95/20/0). Anchors: `Qwen3-30B-A3B-4bit` @ `d388dead`, byte-identical. Reserve: `Qwen3.5-122B-A10B-4bit` (on disk, peak 71.5 GB). Later cells by Ed's answers: Next-Thinking-4bit (needs the checkpoint), Next-Instruct-8bit (needs 85 GB). Flash-Next recorded as infeasible (PR #1788 open; 111.5 GB). No pin bump; a second pinned 0.32.2 venv only if R1 trips #1632, and only for production members.

**Thermal and clock protocol.** Telemetry: existing powermetrics 10 Hz with DVFM residency and pressure, OS level every 5 s, SMC power at 1 s, plus a 1 Hz SMC die/heatsink/fan sidecar inside every member and an ambient logger. Controls: neutral warmup; start-state gate after warmup (S_slow ≤ θ_slow and S_fast ≤ θ_fast for ≥ 2 s; θ = window reference + max(1.0 °C, 3 × idle SD); cap 600 s then flag); per-turn gate and chunked holds for D and the contrast A-arm; token budget instead of the wall guard for new cells; 540 s operational stop; 8 anchors at the pilot ordinals; ABBA on pairs/conditions inside blocks, N and D in alternating 4-member blocks within WQ, one model per production window in the order N, D, D, N. Physical: stand, lid open, fixed room, 100 % battery, optional High Power mode for the whole series. Exclusions fixed now: existing OS-level and pressure rules; `thermal.gate_timeout` and `thermal.start_state_out_of_band` remove a trajectory from calibration fits and keep it printed; `thermal.state_unobserved` keeps it in fits but out of U3/U4. Analysis: frozen sequence design per model × pair × session, counts logged, no clock or temperature term; print-only start sensor, per-turn clock, PSTR-minus-rails energy; β_T and per-turn clock-versus-temperature slopes on identical work only. Acceptance U1-U6 as in §3d.

**WQ (next window after pilot 9).** 28 members, span 27,859 s, maximum 45,600 s: 8 anchors; the pilot-7 b-e25/b-e18 contrast in ABBA (A gated with token budget, B byte-identical); 8 N and 6 D new-cell members at seeds 1-2 under their own model ids. Outputs: the state-versus-work decision under the pre-fixed rule; capability gate per model; per-model rates, energies, cache rebuild counts, cap hits; U1-U4; the K-session anchor read with the new protocol. Everything in WQ is selection data.

**Series.** N1, D1, D2, N2 (8 anchors + 16 held-out benign + 4 sabotage each; sentinels interleaved; frozen-fit artefact written after the training members), then N3/D3 benign increments if Ed wants a finite per-pair split threshold (m ≥ 20, sample-maximum rank; m ≥ 39 for the first non-maximum rank). Each window's maximum stays at or just above 44,640 s because the spans stay near 27,000 s; no 17-hour windows.

**Build order and gates.** §3e; cold Fable on the gate, hold attribution, parser and any cache code; protocol v4 cold gate before WQ arms; frozen commits recorded before any window is read.

**Status against pilot 8.** New calibration cells under protocol v4; pilots 4-9 and the 30B population are untouched and closed; per-pair pooling as ruled in `c110a6c9`; no frozen script edited.
