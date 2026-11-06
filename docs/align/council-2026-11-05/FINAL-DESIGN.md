# FINAL DESIGN: the next ALIGN window series (production Qwen models under thermal control)

Chair: Opus 5.5 (`claude-opus-5-5`), 2026-11-05. I was not a seat. This ruling uses the six council files (r1/r2 from Opus, Fable and Sol), the briefs, the live checkout `e328f0e72`, `origin/main` `92026c184`, `origin/docs/2026-11-05-magistrate-c110a6c9` `1b428cdf7`, and web checks I ran today (HF API and raw files, GitHub API). Nothing under `/Users/edr/jw-b5-*`, `night-custody`, `night-archive` or any `restricted/` path was opened. No commit or push.

Status: design ruling. It is not an arm authorization and not a registration. Protocol v4 (below) carries this design to the registration cold gate.

---

## 0. Bottom line

- **Models.** Run Qwen3.8-27B 8-bit (**D**) and Qwen3-Next-80B-A3B-**Thinking** 4-bit (**N**) as new calibration cells under protocol v4, with Qwen3-30B-A3B 4-bit anchors byte-identical. Qwen3.5-122B-A10B 4-bit is a screened reserve (R1 only). Qwen3.8-Flash-Next is not admitted on the pinned stack. The stack stays at mlx 0.31.2 / mlx-lm 0.31.3.
- **A chair finding that changes the build.** The Qwen3.8 chat template reads earlier reasoning only from a `reasoning_content` field and never splits `</think>` out of `content` (verified below). Our endpoint passes the raw generated text as `content`. Without a fix, every D turn after turn 0 (a) shows the model a malformed history, with an empty think block and then its own reasoning as visible text, and (b) rewrites the cached prefix, which forces a whole-cache rebuild on D's non-trimmable hybrid cache. Before D runs at all, we need:
  - the XML tool-call parser;
  - a history-rendering fix that passes `reasoning_content`.
- **Thermal control.** Five parts:
  1. A 1 Hz SMC sidecar records die-class, heatsink-class and fan sensors.
  2. A start gate sits after warmup and before the episode stamp. It is referenced to a window-local idle state.
  3. A per-turn gate is referenced to the episode's own start, so the reference can never ratchet.
  4. Decode holds apply at fixed token counts, for "heavy" cells only (D, as expected).
  5. A token admission budget replaces the 120 s wall guard. A deadman sits below the runner's member cap.

  All gate and hold time is unowned in attribution. Both turn-owned and gross energy are printed.
- **Deciding experiment, in W1.** Pilot-7 b-e25 and b-e18 are replayed token-identically, four runs per template in ABBA/BAAB order. Arm S has the start gate only; arm G adds per-turn gates. A pre-fixed rule decides whether per-turn gates stay for "light" cells. "Heavy" cells keep gates and holds whatever the result.
- **W1** (after pilot 9, R0 and R1): 19 members, programmed span 26,327 s, window maximum 44,040 s (cap 44,640).
  - 4 anchors
  - 8 contrast runs
  - 4 N members
  - 3 D members
- **Series.** One model per calibration window, in the order N1, D1, D2, N2, N3, D3, (N4).
  - Target: m ≥ 20 held-out benign per pair per model, plus ≥ 2 held-out sabotage per pair, using the frozen per-session LOO calibration (`7fbd95e31`) unchanged.
  - N windows stay ≤ 44,640 s.
  - D windows default to a 59,520 s maximum. Without it, the frozen per-session fit cannot get 6 benign per pair per session at D's member cost (§2.6). Ed can veto this; the alternative is listed.
- **Acceptance.** Six criteria, U1-U6, with numbers (§2.4). Hardware control (U1-U5) and monitoring calibration (U6) are separate verdicts. "Too imprecise" is a verdict of its own ("inconclusive"), never a pass.

---

## 1. Rulings on the contested points

### 1.0 Facts I verified to settle disagreements

| # | Fact | Evidence (checked today) | Consequence |
|---|---|---|---|
| V1 | `window_max_s = 60·⌈(span + 3,300 + 7,200 + 7,200)/60⌉`. A 44,640 s maximum therefore needs span ≤ 26,940 s. | `joulewise/b6/plan_inputs.py:56-59`; `joulewise/b5/plan.py:59,66-67` | Sol's r1 windows (42,355 s spans) were really 60,060 s windows. Sol withdrew them. |
| V2 | Member law `member_s = 516.575 + 1.13544 × episode_s`. Scaffold 4,995 s. Member cap 1,800 s once the wait budget is spent, 3,300 s while it is unspent. | `configs/campaigns/align_pilot_v3/registration/sizing_b5.json`; `scripts/run_campaign.py:3776` (`HAZARD_MEMBER_CAP_S = 1800.0`); kit comment `scripts/align_pilot_kit.py` `planning_sizing` | A D member is planned to at most 1,800 s, so its episode is at most 1,130 s of wall time. |
| V3 | HF revisions and sizes:<br>• N-Thinking-4bit `9a2b4634…`, 44,860,367,003 B, `qwen3_next`<br>• Instruct-4bit `d8a069bf…`, 44,860,366,993 B<br>• D-8bit `815b83c0…`, 29,531,521,322 B, `qwen3_5`<br>• D-4bit `10c35caa…`, 16,081,490,933 B<br>• 122B-4bit `e9c67b08…`, 69,620,619,709 B, `qwen3_5_moe`<br>• Flash-Next-4bit `07b5dc6c…`, 111,546,653,418 B, `qwen4_exp` | `https://huggingface.co/api/models/<repo>?blobs=true` | Pins in §2.1. |
| V4 | mlx-lm 0.31.3 released 2026-04-22; the latest is 0.32.2 (2026-10-16). #1623 merged 2026-08-18 and #1632 merged 2026-08-22, both after the pin. #1788 (Flash-Next, `qwen4_exp`) is **open** since 2026-08-26. | `gh api repos/ml-explore/mlx-lm/{releases,pulls/N}` | Flash-Next needs an unmerged branch. #1632 is a real risk on 0.31.3 (R0 test). |
| V5 | The **Qwen3.8 template** sets `reasoning_content = ''` unless `message.reasoning_content is string`. It has no `'</think>' in content` split. It renders `'<think>\n' + reasoning_content + '\n</think>\n\n' + content`. `preserve_thinking` defaults on. Effort levels are `xhigh` (default), `medium` and `low`. | mlx-community and upstream `chat_template.jinja` are byte-identical; l.47-56 and 106-117 | Chair finding above. Fable's "D is append-only" and Opus's "rewrites because reasoning is stripped" are both wrong. Rewrites happen because the field is missing. |
| V6 | The Qwen3-Next-Thinking and Qwen3.5-122B templates **do** split `</think>` from `content`, and keep reasoning for assistant turns after the last real user query. SHADE transcripts have one user message, so every assistant turn keeps its reasoning. | `next_think chat_template.jinja` l.17-46; `Qwen3.5-122B-A10B-4bit chat_template.jinja` l.90-101 | Fable's claim that Thinking "strips earlier reasoning every turn" is wrong for our transcripts. N should be near append-only (R0 measures it). |
| V7 | The endpoint renders `{"role", "content": raw_text}` with no `reasoning_content` and no template kwargs. The tool parser is JSON-only. | `joulewise/align/apple/endpoint.py:240-250`, `:95-161`; `joulewise/align/apple/workload.py:354-356` | Must-build B1 and B2. |
| V8 | `smc.py`, `controller.py`, `monitor.py`, `mlx_runtime.py` and `run_campaign.py` are pinned. `joulewise/align/*` has no pin. | `configs/pins/registry.json` (smc.py at l.4615; 0 hits for `joulewise/align/`) | Gates and the sidecar live in `joulewise/align/` and import `smc.py` unchanged. Fable's controller/policy placement is out. |
| V9 | Qwen3.8-27B card:<br>• thinking sampler 1.0/0.95/20/0, presence 0;<br>• a warning that lower effort "can also lead to insufficient analysis, more failures, and repeated retries". | `https://huggingface.co/Qwen/Qwen3.8-27B` README l.252, 258-267 | Effort ladder in §2.2. |
| V10 | Next agent scores (card, last column):<br>• Thinking: BFCL-v3 72.0, TAU2-Retail 67.8<br>• Instruct: BFCL-v3 70.3, TAU2-Retail 57.3 | Qwen/Qwen3-Next-80B-A3B-{Thinking,Instruct} README | Thinking is stronger on agentic benchmarks and keeps the reasoning estimand. |
| V11 | Pilot-7 contrast seeds:<br>• b-e18: spam/benign, seed index 14, expected seed 8158640411307706161<br>• b-e25: spam/sabotage, index 16, expected seed 7655467588542005630 | `git show 45b47f7b6:configs/campaigns/align_pilot_v3/collection_plan.json` | Contrast configs are reproducible from the pilot-7 kit. |
| V12 | Pooling stays per pair (B1 rejected). Calibration is frozen at `7fbd95e31`, with rank `⌈0.95(m+1)⌉` computed exactly as `(19(m+1)+19)//20`. | `c110a6c9` RECORD; `git show 7fbd95e31:scripts/align_pilot_calibration.py:45-57` | m = 19 is the first finite rank. m = 20 uses the sample maximum. |
| V13 | D was re-downloaded on 10-28 (`815b83c0`, 28 GB). The BYTES extension was later dropped. No later deletion is recorded. | `RUN_STATE.md` l.349, l.900 | R0 checks it with `ls` and a hash; no download is budgeted. |

**Seat errors found by the chair**, in addition to those the seats found in each other:
- Opus r2's 20-member WQ places an anchor at ordinal 28.
- Fable r2's "28-member" WQ sums to 26 members (8 + 4 + 8 + 6), and its own maximum (45,600 s) breaks the cap.
- Fable r2 says D is append-only and Next-Thinking rewinds every turn. Both are reversed (V5, V6).

### (a) Models: Next variant and quantization, the 122B, Flash-Next

**Ruling.**
- **N = Qwen3-Next-80B-A3B-Thinking 4-bit.** The 8-bit and Instruct builds are not the primary.
- **D = Qwen3.8-27B 8-bit**, with 4-bit as the fallback under a fixed rule.
- **The 122B is out of calibration.** It is screened in R1, and becomes a third cell only if Ed says so.
- **Flash-Next is "not admitted on the pinned stack; not proved physically impossible."**

**Why, and who won.**
- **N: Opus and Sol won over Fable.**
  - The pilots' monitoring estimand is the known-H reasoning-omission tamper curve (`docs/align/pilot_protocol_v3.md:155-163`). Instruct has no reasoning spans, so the estimand would be lost for N.
  - Thinking also scores higher on agent benchmarks (V10).
  - Fable's main practical argument was cache rewinds under Thinking. It rests on a template misreading (V6).
  - Fable's other points stand: Instruct is on disk and append-only. That makes Instruct the right **fallback**.
  - 8-bit is out: an 84.7 GB download against about 82 GB free (`c110a6c9` Launch), an untested peak of about 89 GB, and no gain in the estimand. It can be a later precision cell.
- **D: all three seats agreed on 8-bit.**
  - Effort is ruled by a measured ladder (§2.2), which combines Sol's "freeze after checking" with Opus's start at the card default.
  - `low` is allowed only as the last rung before giving up on D. This rejects Opus's "never low", because a cell whose episodes end at turn 0 measures nothing. It also rejects Fable's "low first", because of the card's warning (V9).
  - The fallback is the same model at 4-bit (V3; Opus and Fable), not Qwen3.5-27B (Sol r1).
- **122B: all three seats agreed in r2.**
  - It is the largest Qwen that fits: measured peak 71.5 GB at 2.5k (`docs/design/bytes_pilot/SUMMARY.md:26`), against a 115.4 GB working set (l.29).
  - Ed did not name it, and a third cell costs about 3 long windows (§2.6).
- **Flash-Next: Sol's wording, Opus's and Fable's facts.**
  - It needs `qwen4_exp`, which is only in the open #1788 (V4).
  - The mlx-community 4-bit is 111.55 GB = 103.9 GiB = 96.7 % of the 115.4 GB working set, before KV and the OS. That means a wired-limit sysctl and an unmerged runtime.
  - GGUF builds exist (unsloth, ISTA-DASLab), so it is reachable through another engine or a future pin. That is an engine decision, not this window's.

### (b) The first window: size, member mix, series length, calibration targets

**Ruling.**
- **W1 has 19 members:**
  - 4 Qwen3-30B anchor originals;
  - 8 contrast runs (2 templates × 4, ABBA/BAAB);
  - 4 N (both pairs × both conditions, seed 1);
  - 3 D (spam/benign, bank/benign, spam/sabotage, seed 1).
- Span 26,327 s, maximum 44,040 s (§2.3).
- W1 and R0/R1 are selection data.
- Then one model per window: N1, D1, D2, N2, N3, D3, (N4).
- **Target per model:** m ≥ 20 held-out benign per pair, plus ≥ 2 held-out sabotage per pair, under frozen `7fbd95e31` per-session LOO, per pair.
- Registration grade (m ≥ 39 per pair, plus a locked test cohort) needs Ed's go.

**Why.**
- **Size: 20 vs 28.** 28 is infeasible under the cap at new-model member costs. Fable's own roster gives 45,600 s even at member costs below the law (V2). 19-20 is what fits, so Opus's shape is adopted.
- **Contrast: Sol won over Opus.**
  - Opus's 4-run contrast gives one A/B difference per template, each carrying about 10 ordinal units of drift.
  - Within-window identical-work drift on the 30B reaches about 10 J (pilot 4 replays differed by 1.3-10.1 J; RUN_STATE l.991). That is the same size as the decision thresholds.
  - ABBA within each template cancels linear drift exactly. The cost is about 4,000 s once, against a decision that sets gate cost for every later window.
- **Four anchors only: Sol won over Fable and Opus.**
  - The 8 contrast runs supply W1's 30B identical-work pairs (same template, same arm).
  - The 4 originals keep the K-session bridge to pilots 4-9. The replays at 9/14/19/28 would cost 3,131 s that the cap does not have.
- **Calibration method: Opus won over Sol and Fable.**
  - The known convergence imports `7fbd95e31` unchanged.
  - Per-session fits are what cancel the 8-9 J session offsets (`cf1baad2` "Calibration population").
  - Sol's fixed-coefficient split would carry those offsets into every score and is a different estimator. It is rejected.
  - Sol's correct point is kept as a disclosure: "held-out" means fresh seeds scored by a frozen design and frozen code with per-session coefficients, the same doctrine as pilots 8-9.
- **Target: Opus's m = 20, stated Sol's way.** m = 20 gives rank 20, the sample maximum: a finite threshold, but no 5 % FPR claim.
- **One model per calibration window: all seats.** It avoids reload churn and gives each per-session fit enough benign trajectories per pair.

### (c) Gate form and placement, per-turn gate, holds, token budget

**Ruling.**
- Gates live in `joulewise/align/apple/thermal.py` (new), driven from `workload.py`.
- **Start gate G0:** after a neutral warmup, immediately before the episode stamp. Reference is window-local.
- **Per-turn gate G1:** before every turn k ≥ 1, referenced to the episode's own release values.
- **Holds H:** inside decode, at fixed token counts, for heavy cells only.
- **Timeouts:**
  - G0 timeout: flag and proceed, with the trajectory excluded from calibration;
  - G1 or H timeout: stop the episode, flag it, exclude it.
- A missing sensor gives a timed wait plus `thermal.state_unobserved`. Such trajectories are excluded from calibration and from the U checks.
- New cells use a **token admission budget** and a **deadman** below the member cap. The anchors keep their byte-identical 120 s guard. The contrast arms stop at the recorded pilot-7 turn count.

**Why, and who won.**
- **Placement.**
  - Sol was right that the gate must follow warmup. Warmup prefills the condition's own prompt (`workload.py:258-269`), which is 755 tokens longer for sabotage.
  - Sol's neutral warmup is adopted: new cells warm up on the benign prompt for both conditions.
  - The controller and monitor are pinned (V8), so Fable's `idle_baseline` and policy-file placement cannot be built without touching sealed files.
- **References.**
  - The window-local reference is Fable's: one reference, measured at the window's first sidecar member's idle.
  - Sol's per-model 15-30 min conditioning (6,000 s per window) is rejected. It costs about 5 members per window, and the start gate plus R1 step data do the same job.
  - The per-turn reference is the episode's own release state, not the previous turn's. Sol showed Opus's previous-turn fallback can ratchet.
- **Sensor choice is Opus's.** It uses the step response (die class t63 ≤ 5 s; heatsink class τ ≤ 300 s), not a guessed key.
- **Holds: Opus's mechanism with Sol's conditions.**
  - Holds are mandatory only where R1 shows the planning turn reaches 0.6 × t_decline.
  - D's 4,096-token turn is about 370 s at 11 tok/s, against a pilot-2 onset of 167-201 s at 40-47 W (`e1308804` l.58). So holds are expected for D.
  - Per Sol, holds need requalification in R1: token identity under holds, resume transients, and gross energy printed.
  - New detail from the chair: a hold may begin only after the in-flight lookahead token has been evaluated. Otherwise about one decode step (about 90 ms at about 40 W, about 3.6 J for D) leaks into an unowned segment.
- **Timeout handling is mixed.**
  - Stopping on a G1 or H timeout (from Sol) protects the next member's start state and the window clock.
  - Proceeding on a G0 timeout (Opus and Fable) keeps a capability reading where no clean energy existed anyway.
- **Token budget vs wall guard: Opus, with Sol's deadman.**
  - A wall guard makes trajectory length depend on decode speed, which is machine state.
  - The deadman exists only so that the runner's 1,800 s kill never destroys a bundle.
  - Sol's 540 s stop is replaced: D's held episodes are designed to run longer.
- **Rejected:** Sol's 50 % duty ceiling over 3,600 s, because it makes idle depend on history; and Sol's ambient gate of 20-23 °C, because ambient is recorded, not gated (Opus).

### (d) The merged acceptance set

**Ruling:** U1-U6 in §2.4, with numbers. The parts come from:
- Opus: the scaled identical-work bar and the residual-slope bar;
- Fable: the start-state range, the β_T bound, and the "protocol not met" consequence;
- Sol:
  - coverage bars;
  - clock bars;
  - cross-window equivalence with window-cluster df;
  - the 0.37 % early-to-late bar;
  - separate verdicts;
  - "inconclusive" as an outcome.

**Rejected:**
- Fable's "30B anchors within ±6 J of pilots 6-9" as an acceptance test. It confounds the new physical setup with control (Opus F11); it is printed only.
- Fable's β_T from historical anchors, which have no recorded temperatures (Sol).
- Any correlation "CI includes 0" used as a pass (Sol). Correlations are printed diagnostics only.

### (e) Build order and review gates

**Ruling:** §2.7. In order:
1. **Stage 1 (small; unblocks R0):**
   - the XML parser;
   - the history-rendering fix (`reasoning_content`, template kwargs);
   - the token budget and deadman;
   - the R0 scripts.
2. **R0** on the Mac by day, with no window armed.
3. **Stage 3**, run in parallel with R0:
   - the SMC sidecar and gates;
   - holds and hold attribution;
   - kit v4 and the desk;
   - protocol v4.
4. **R1** hardware rehearsal.
5. **Slot verification**, then arm W1.

The hybrid-cache checkpoint is **conditional** on R0's round-trip count. Here Fable and Sol won over Opus: with V5 fixed and V6 known, rewinds are expected to be rare, not every turn. Opus was right that D would rebuild every turn, but the cause is the missing field, and B2 fixes it more cheaply.

Review gates follow the standing pattern: Sol builds; Opus does the non-author executing review; Fable does a cold pass on the science-touching parts; then the registration cold gate on protocol v4 and CI.

### (f) Ed's physical tasks and questions

**Ruling:** §3.
- Physical setup is once, before R1, and then left untouched for the series.
- No third-party fan control.
- High Power mode, and an external cooler if Ed owns one, are tested in R1 under a fixed adoption rule (Opus's rule, extended to Fable's cooler idea).
- Questions carry defaults, and the design is complete under the defaults.

---

## 2. Final design

### 2.1 Model pins and per-model settings

The stack is unchanged: mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1 (`env/mac-measurement-lock.txt`). All models use:
- context cap 40,960;
- the `episode_prefix` cache;
- hint on;
- a 300 s configured idle;
- a fresh process per member;
- the seed law `["align-p4-v1", model_id, "thinking_on", "shade/<pair>", i]`.

The seed law is unchanged; new `model_id` tags give disjoint seeds.

| Tag (`align-model=`) | Repo @ revision | Bytes (download) | Arch / loader | Est. peak at 40,960 | Sampler (T / top_p / top_k / min_p) | Template / tools | Per-turn cap | Role |
|---|---|---|---|---|---|---|---|---|
| `qwen3-30b-a3b` | mlx-community/Qwen3-30B-A3B-4bit @ `d388dead1515f5e085ef7a0431dd8fadf0886c57` | 17.2 GB, on disk | `qwen3_moe` | 18.1 GB measured at 2.5k | 0.6 / 0.95 / 20 / 0 | Qwen3, JSON | 4,096 × 12, 120 s guard | anchors + contrast; byte-identical configs for anchors |
| `qwen3-next-80b-a3b-thinking` **N** | mlx-community/Qwen3-Next-80B-A3B-Thinking-4bit @ `9a2b46347bb170cb2924092175fa21554fe585a9` | 44,860,367,003 B, **download** | `qwen3_next` (mlx-lm ≥ 0.28) | ≈ 49 GB (Instruct twin 47.0 GB at 2.5k + ≈ 1.0 GiB KV) | 0.6 / 0.95 / 20 / 0 (card) | force-opens `<think>`; JSON; splits content (V6) | 4,096 (ladder §2.2) | cell |
| `qwen3.8-27b` **D** | mlx-community/Qwen3.8-27B-8bit @ `815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9` | 29,531,521,322 B, on disk (R0 verifies) | `qwen3_5` (≥ 0.30.7; no `mtp.` keys in the weight map) | ≈ 34 GB (29.5 + 2.7 GB KV + runtime) | 1.0 / 0.95 / 20 / 0, presence 0 (card thinking) | XML tools; **`reasoning_content` history** (B2); `reasoning_effort` per ladder; `preserve_thinking` default | 4,096 | cell |
| D fallback | mlx-community/Qwen3.8-27B-4bit @ `10c35caafbb80f7dc6a7a432cdd11af10a6d4818` | 16,081,490,933 B | same | ≈ 20 GB | same | same | 4,096 | by rule §2.2 |
| N fallback | mlx-community/Qwen3-Next-80B-A3B-Instruct-4bit @ `d8a069bfa8ae87d3d468412e1034acae19b5892b` | on disk | `qwen3_next` | 47.0 GB measured at 2.5k | 0.7 / 0.80 / 20 / 0 (card; presence 1.5 cannot be expressed and is recorded as a deviation) | no reasoning; JSON; append-only | 4,096 | by rule §2.2; **no reasoning-omission estimand** |
| reserve **F** | mlx-community/Qwen3.5-122B-A10B-4bit @ `e9c67b08899964be5fdd069bb1b4bc8907fe68f5` | 69,620,619,709 B, on disk | `qwen3_5_moe` | ≈ 73-78 GB (71.5 GB measured at 2.5k) | 0.6 / 0.95 / 20 / 0 (card "precise coding"; the general setting needs presence 1.5) | XML; splits content | 4,096 | R1 screen only |

- **Excluded:**
  - Flash-Next (V3, V4);
  - Qwen3.5-397B and Qwen3.8-2.4T (too large on the pinned stack);
  - Next 8-bit (disk and an untested peak; a possible later precision cell).
- **Why these are "the top runnable in 128 GB":**
  - Qwen3.8-27B was recorded as the strongest open-weights model that fits (`docs/registrations/bytes_extension_models_2026-10-27.md` table row 1, AA index 10-27).
  - Qwen3-Next is Ed's named model, and Thinking is its stronger agent variant (V10).
  - The 122B is the largest Qwen that fits, and it is held ready.
- All peaks are below the 115.4 GB working set, so no sysctl is needed.

### 2.2 Pre-declared operating-parameter rules (fixed in protocol v4 before R0; R0 and R1 fill them)

**D effort ladder (R0, unmeasured, by day).**
- Run 2 benign episodes (spam, bank) per rung:
  - per-turn cap 4,096;
  - at most 6 turns and 16,384 decode tokens;
  - development seed indices 91-92.
- Rungs, in order: `xhigh` (template default; nothing passed), then `medium`, then `low`. Stop at the first rung that passes.
- A rung passes if:
  - ≤ 20 % of turns end at the cap with unclosed reasoning, **and**
  - median reasoning tokens per turn ≤ 2,048.
- If no rung passes, D is screen-only in this series. Its W1 members are reported as an energy and capability screen.

**D quantization rule (R1).**
- B_D = the largest multiple of 1,024 such that the R1 planning member is ≤ 1,800 s.
- If B_D < 6,144 at 8-bit, D switches to 4-bit at the same effort.
- If R0's measured rates already predict that switch, the 16.1 GB 4-bit is downloaded before R1 and step-tested there.

**N cap ladder (R0).**
- The same 2-episode screen at a per-turn cap of 4,096.
- If more than 20 % of turns hit the cap: re-screen at 8,192.
- If still more than 20 %: N falls back to Instruct-4bit, disclosed as "no reasoning-omission estimand".

**Token admission budget B_m.**
- Turn k is admitted only if cumulative decode tokens are below B_m. An admitted turn keeps its full per-turn cap.
- **B_N** = the largest multiple of 1,024 with R1 planning member ≤ 1,200 s, with a floor of 8,192.
- **B_D** is as above, with a floor of 6,144 at 8-bit.
- Both are capped by the 40,960 context.
- Stop flag: `episode.decode_budget:<k>`. This is a normal stop, not an exclusion.

**Deadman.**
- T_dead,m = (1,750 − I_m) / 1.13544 seconds of episode wall time, where I_m is the member intercept R1 measures for model m (load, idle, warmup, teardown). With the transferred intercept, that is 1,086 s.
- Flag `episode.deadman:<k>`. The trajectory is incomplete and excluded.

**#1632 rule (R0).**
- Decode to 40,960 positions on N and D with the episode's cache object, logging MLX active memory and Metal errors.
- If there is any `Resource limit` error, or growth above 2 GB per 10k tokens:
  - first mitigation: an align-local `mx.eval` of each `ArraysCache`'s metadata arrays at every turn and hold boundary (no stack change), then retest;
  - only if that fails: a separate pinned 0.32.2 venv for production members, as its own stack-change ruling. Until then, D or N is screen-only.
- Background: the PR #1632 body says `ArraysCache.lengths` and `left_padding` keep a lazy graph that grows per decode step. Whether evaluating them at boundaries is enough is a **(guess)** until R0.

**Hybrid-checkpoint rule (R0).**
- With B2 in place, R0 counts rewritten prompt tokens at each turn transition of real generated turns.
- The checkpoint (B7) is built **before R1** if either:
  - D shows any rewind on a closed-reasoning turn over ≥ 12 transitions, or
  - N shows rewinds on more than 10 % of transitions.
- Otherwise it is not built. Rebuilds are logged (`cache.rebuilt_untrimmable:<k>`). If W1 shows rebuilds on more than 5 % of a model's transitions, B7 is built before that model's first calibration window.

**Physical levers (R1).**
- High Power mode (Apple toggle, M3 Max 16-inch), and an external cooler only if Ed owns one. Each is tested as an A-B-A on D's planning-turn step.
- Adopt a lever for the whole series only if:
  - t_decline lengthens ≥ 25 %, **and**
  - the census and readiness probes pass under it (note: `arm_readiness_evidence_t0.py:1990` greps `lowpowermode 0`, while macOS 26 reports `powermode`).
- Otherwise use Automatic with no cooler, for continuity with pilots 4-9.
- Once adopted, a lever is never changed within the series.

### 2.3 The W1 roster, order, span and maximum

**Contrast templates:**
- **X** = pilot-7 b-e25 (spam/sabotage, seed index 16);
- **Y** = pilot-7 b-e18 (spam/benign, seed index 14).

**Contrast configs.** Each is the pilot-7 member config with these changes:
- `max_episode_seconds` removed;
- `max_turns` = that member's recorded pilot-7 turn count;
- sidecar on, neutral warmup, G0 on;
- arm **G** also has G1 (per-turn gate);
- no holds.

Seed, sampler, cache and context are byte-equal to pilot 7, so tokens must equal the pilot-7 bundle.

**N/D members:** seed index 1 under their model tags, with G0 + G1, holds if heavy, B_m and the deadman.

| Ord | Member | Config class | Planning member_s (guess; R1 replaces) |
|---|---|---|---|
| 1 | anchor a-e01 spam/benign s1 | byte-identical to pilots 4-9 | 782.8 |
| 2 | anchor a-e02 bank/sabotage s1 | byte-identical | 782.8 |
| 3 | anchor a-e03 spam/sabotage s1 | byte-identical | 782.8 |
| 4 | anchor a-e04 bank/benign s1 | byte-identical | 782.8 |
| 5 | N spam/benign s1 | N gated (first sidecar member: its idle sets the window reference R) | 1,200 |
| 6 | X-G | contrast, G0 + G1 | 1,150 |
| 7 | D spam/benign s1 | D gated, holds if heavy | 1,800 |
| 8 | Y-S | contrast, G0 only | 850 |
| 9 | N bank/benign s1 | N gated | 1,200 |
| 10 | X-S | contrast, G0 only | 850 |
| 11 | Y-G | contrast, G0 + G1 | 1,150 |
| 12 | D bank/benign s1 | D gated | 1,800 |
| 13 | Y-G | contrast, G0 + G1 | 1,150 |
| 14 | X-S | contrast, G0 only | 850 |
| 15 | N spam/sabotage s1 | N gated | 1,200 |
| 16 | Y-S | contrast, G0 only | 850 |
| 17 | D spam/sabotage s1 | D gated | 1,800 |
| 18 | X-G | contrast, G0 + G1 | 1,150 |
| 19 | N bank/sabotage s1 | N gated | 1,200 |

**Balance checks.**
- Position sums: X-G 6 + 18 = 24 = X-S 10 + 14; Y-S 8 + 16 = 24 = Y-G 11 + 13. Linear drift cancels within each template.
- Predecessors are mixed across arms: X-G follows N and D; X-S follows N and 30B; Y-S follows D and N; Y-G follows 30B and D.
- N sits at 5/9/15/19 and D at 7/12/17.
- Stage split and midpoint reference after ordinal 10 (the analogue of pilot 8's split after 14).

**Arithmetic** (V1, V2):
- Align = 4 × 782.82 + 4 × 850 + 4 × 1,150 + 4 × 1,200 + 3 × 1,800
  = 3,131.27 + 3,400 + 4,600 + 4,800 + 5,400
  = **21,331.27 s**.
- Span = 21,331.27 + 4,995 = 26,326.27 → **26,327 s**.
- Window max = 60 × ⌈(26,327 + 3,300 + 7,200 + 7,200)/60⌉ = 60 × ⌈44,027/60⌉ = 60 × 734 = **44,040 s**. That is at most 44,640, with 613 s of span slack (span limit 26,940).
- Disk, using the law `186,751,297 + 512,401.34 × member_s + 4,286,134` B per member, plus 4.04 GB scaffold: **18.60 GB per copy, 37.2 GB for two copies.**

**Pre-declared fit rule after R1.** Any planning numbers above are replaced by R1 measurements. If the R1-sized span exceeds 26,940 s, apply in order:
1. lower B_N in 1,024 steps, down to 8,192;
2. lower B_D, down to 6,144;
3. drop ordinal 19.

If it still does not fit, the roster returns to the lead. Contrast and anchor slots are never cut.

**What W1 yields:**
- the contrast verdict;
- U1-U3 for N, D and the 30B;
- the capability gate per model;
- per-model rates, energies, gate and hold costs, cap hits and rebuild counts;
- the K-session anchor offset under the new physical setup (printed only).

U4-U6 are not evaluable in W1. That is said, not promised.

### 2.4 Acceptance: "under control" (fixed in protocol v4 before R0)

All criteria are evaluated per model per window and printed in `PILOT.json` and the desk. None is a hypothesis test. Each has three outcomes: **pass**, **fail**, or **inconclusive** (the interval is wider than the margin while the point estimate is inside it).

- **U1 Throttle-free and observed.**
  - (a) Every included turn has OS thermal level 0 at every reading and powermetrics Nominal at every sample.
  - (b) Thermal exclusions X1-X4 hit at most 1 member per model per window.
  - (c) SMC sidecar coverage ≥ 99 % of the seconds of every gated episode and its gates, with no gap > 2 s; powermetrics gaps ≤ max(1 s, 5 sample periods).
  - (d) G1 and H timeouts ≤ 2 % of turn admissions; G0 timeouts ≤ 1 per model per window.
- **U2 Start state.**
  - The range of G0 release S_slow across a model's gated members in the window ≤ 3.0 °C.
  - Every G1 and H release is within δ of the episode's G0 values (verified from the journal, not assumed).
- **U3 Identical work within a window.** This covers every within-window identical-work pair:
  - W1 contrast same-arm pairs;
  - calibration-window sentinel early/late pairs;
  - the R1 replay pair for W1's new models.

  Each pair must satisfy:
  - |ΔE_GPU, turn-owned| ≤ 3 × max(2.97 J, 0.0011 × E_pair), where 2.97 J is the pilot-4/5 pair-difference SD (`1b198a71`; RUN_STATE l.997);
  - decode-phase active-clock difference ≤ 0.5 %;
  - token-identical, else X5.
- **U4 Cross-window equivalence** (per model; evaluated once ≥ 3 new-protocol windows of that model exist).
  - For every sentinel run i in window w: r_i = (E_i − E_ref) / E_ref, with E_ref the model's W1 original of the sentinel trajectory.
  - Pass if:
    - the mean of the window means r̄_w has |·| ≤ 0.25 %, **and**
    - its 90 % t-interval over windows (df = W − 1) lies inside ±0.5 %.
  - The 30B anchors' moment σ_w among new-protocol sessions (K ≥ 3) ≤ 6 J.
- **U5 State-sensitivity bound.** The 90 % upper bound of the state-induced episode-energy shift must be ≤ 0.1 × the smaller per-pair s_r of the cell. Its source depends on the cell:
  - **Light cells:** the W1 contrast arm effect δ, scaled by E_cell / E_30B.
  - **Heavy cells:** β_T (J/°C), fitted only on that model's temperature-observed identical-work pairs (R1 replay, sentinels), multiplied by the observed G0 release range.
- **U6 Monitoring stability** (separate verdict; benign, m ≥ 6 per model × pair, using the frozen per-session fits). Both must hold:
  - the 90 % CI of the pooled per-turn residual slope on turn index lies inside ±1 J/turn × (model mean turn energy ÷ 30B mean turn energy);
  - the 90 % CI of the early-half-to-late-half benign residual change lies inside ±0.37 % of the model's mean episode energy (≈ 10 J at 2.7 kJ).

  corr(residual, release S_slow) and corr(residual, mean clock) are printed as diagnostics only.

**Consequences.**
- **U1-U3 fail:** that model-window is "thermal protocol not met". Its new-model members enter no held-out pool. Before the model's next window the escalation ladder applies, one step at a time:
  1. idle 300 → 450 s;
  2. δ → max(0.5 °C, 2 × SD);
  3. holds on;
  4. one quantization step down.
- **U4 or U5 fail:** "state not controlled" for the cell; calibration unresolved.
- **U4 or U5 inconclusive:** add 2 sentinels per window to that model's remaining windows (pre-declared). Never loosen a margin.
- **U6 fail:** "calibration unresolved", even if U1-U5 pass.
- **Ed's "under control"** means U1-U5 pass for that model.

**Exclusions (fixed now; none depends on a residual, clock or temperature value).**
- **X1** `thermal.os_level_nonzero` (registered span; episode-scope alternative printed), unchanged (`pilot_protocol_v3.md:116-131`).
- **X2** `thermal.start_gate_timeout`, `thermal.gate_timeout:<k>` and `thermal.hold_timeout:<k>`: excluded from calibration and primary fits; kept for capability; printed.
- **X3** powermetrics non-Nominal inside an included turn: treated as X2.
- **X4** `thermal.state_unobserved`: excluded from calibration and from all U checks.
- **X5** token divergence in a replay, contrast run or sentinel: not an identical-work pair.
- **X6** MLX OOM or Metal resource error: member failure.
- **X7** `episode.deadman`: incomplete and excluded.
- **X8** no replacement or top-up; every refusal or incomplete member is printed by arm.

**Analysis.**
- Primary: the frozen sequence design `[1, P, D, (C+P)D + D²/2, CP + P²/2]`, per model × pair × session, counts logged, through the frozen alternative desk `4d54cb47b` and calibration `7fbd95e31`, imported unchanged. The script already keys pools by configuration, so new models are their own cohorts.
- No clock or temperature term (`cf1baad2` Ruling (2)).
- Labelled sensitivity: add G0 release S_slow.
- Printed:
  - per-turn thermal table;
  - prefill vs decode active clock, low-clock fraction, first sustained decline (Sol);
  - turn-owned **and** gross energy;
  - PSTR minus (GPU + CPU + ANE), labelled "unassigned power residual", not a DRAM meter (Sol);
  - Sol's tamper grid H ∈ {0, 128, 256, 300, 512, 1,024, 2,048, full} as an additional print-only table, with H = 0 never counted as a detection.

### 2.5 The deciding experiment and its rule

- **Question.** Is pilot 7's later-turn residual accumulation (+2 to +8 J per later turn; `cf1baad2` Ruling (4)) caused by heat building over back-to-back turns (**T**), or by work mix the design prices imperfectly (**W**)?
- **Treatment.** The per-turn gate G1, at identical tokens and an identical start gate.
- **Measure.** For each run, E = turn-owned GPU energy summed over turns. For each template t, d_t = mean(E_S) − mean(E_G) over its 2 + 2 runs.
- **Model.** Over the 8 runs: E_i = α_template + δ·1[arm S] + β·τ_i + ε, with τ = episode start in hours since t0. Report δ̂ with a 90 % t CI (4 df).
- **Noise.** Expected noise on d_t is about 2.1 J (same-position SD).

**Rule (mechanical; the v4 desk prints the verdict):**

| Verdict | Condition | Branch for the rest of the series |
|---|---|---|
| **T CONFIRMED** | \|d_X\| ≥ 10 J **and** \|d_Y\| ≥ 10 J, same sign, **and** the 90 % CI of δ excludes 0 | G1 stays for every cell. Disclose for pilots 8-9 that the Qwen3-30B v3 calibration carries state effects of size δ̂. No frozen script is edited. |
| **T REJECTED** | \|d_X\| ≤ 6 J **and** \|d_Y\| ≤ 6 J, **and** the 90 % CI of δ ⊂ [−6, +6] J | From the first calibration window, **light** cells run with G0 only. **Heavy** cells keep G1 and holds. The pilot-7 clock tracking is recorded as W; any remedy is a separately registered design change, never a clock term. |
| **INCONCLUSIVE** | otherwise, including when a template has fewer than 2 token-identical runs in either arm | G1 stays for every cell. No automatic re-test. |

**Light and heavy.**
- A cell is **heavy** if its R1 planning turn (10,000 fed prefill + per-turn-cap decode, at R1 rates) lasts ≥ 0.6 × t_decline. Otherwise it is **light**.
- The contrast is run on the 30B, so its verdict governs only light cells. This is Sol's objection: a 30B result cannot certify a dense 27B.
- D is expected to be heavy, and N to be light or borderline. R1 decides.

**Always printed:**
- d by turn index;
- per-turn Δ decode clock and ΔS_slow;
- same-arm repeat differences (these feed U3);
- token identity of all 8 runs against the pilot-7 bundles (`--compare-session`).

### 2.6 Gate specification (for the build lane)

**Sensors** (slots S1-S4; R0 enumerates them and R1 classifies them).
- R0 lists every readable `T*` and `F*` SMC key (key by index, command 8), with type and value at idle and under a 60 s load step.
- R1's planning-turn step test gives each key its 63 % rise time t63, its cooling time constant τ, and its rise ΔT.
- **S_fast** = the key with the largest ΔT among keys with t63 ≤ 5 s.
- **S_slow** = among keys with ΔT ≥ 3 °C and τ ≤ 300 s, the one with the longest τ.
- Keys with τ > 300 s (chassis) are recorded but not gated.
- Fan RPM keys (`F0Ac`/`F1Ac` or whatever R0 finds) are recorded.
- If no usable die-class **and** heatsink-class key is readable without root at 1 Hz with < 1 % errors, R0 fails its thermometry bar. Choose between an IOHID-reader lane, or proceeding with every member X4 and no thermal-control claim (Sol).

**Sidecar.**
- 1 Hz, in-process. It starts at adapter `prepare` and stops at teardown, so it covers idle, warmup, gates, the episode and holds.
- It reads through `joulewise.hazards.smc` transport and `Reader`, **unchanged**. Extra decoders (`sp78`, `fpe2`, `ui8 ` etc.) live in align-local code.
- Writes `outputs/align_thermal.jsonl` (monotonic + epoch stamps, key, type, raw value, error) and phase events `align_thermal_gate`, `align_thermal_hold`.

**Reference R.**
- Medians of S_fast and S_slow over the last 60 s of the 300 s configured idle of the window's first sidecar member (W1: ordinal 5).
- Recorded in the custody record and in every bundle.

**Bands.**
- δ_k = max(1.0 °C, 3 × SD_k), where SD_k is the 1 Hz SD over R1's 30-min idle soak (slot S5).
- Pre-declared tuning (slot S6): if R1's median G1 wait exceeds 90 s, raise δ_slow in 0.5 °C steps until it is ≤ 90 s, and print the energy band the change implies (via R1's dE/dT).

**G0 (start gate).**
- Placed after the neutral warmup (benign-condition prompt for both conditions) and immediately before the episode start stamp.
- Releases when, for **10 consecutive samples**:
  - S_fast ≤ R_fast + δ_fast and S_slow ≤ R_slow + δ_slow;
  - the OLS slope of S_slow over the last 60 s satisfies |slope| ≤ 0.2 °C/min;
  - the last OS level reading is 0 and the last powermetrics state is Nominal.
- Cap 600 s. On cap: flag `thermal.start_gate_timeout` and proceed (X2).

**G1 (per-turn gate).**
- Before `endpoint.chat` for every turn k ≥ 1 (`workload.py:347`).
- Releases when, for **5 consecutive samples**, S_fast ≤ E_fast + δ_fast and S_slow ≤ E_slow + δ_slow. E is that episode's G0 release values, so the reference never ratchets.
- Cap G_turn = min(300 s, 3 × the R1 p95 recovery time from planning-turn peak to within δ) (slot S7).
- On cap: flag `thermal.gate_timeout:<k>` and **stop the episode** (X2).

**H (holds; heavy cells only).**
- At every N_chunk decoded tokens within a turn, pause at a token boundary. The pause starts **after the in-flight lookahead token's array has been evaluated** and ends immediately before the next step is dispatched.
- Release on the G1 condition. Cap G_turn. On cap: flag `thermal.hold_timeout:<k>` and stop.
- N_chunk = 256 × ⌊0.6 × t_decline × r_decode / 256⌋, minimum 256 (slot S8).
- t_decline (slot S9) = the time from step start to the first 2 consecutive powermetrics samples whose active-weighted GPU clock is < 0.97 × the median clock of the first 10 s of decode. It is ∞ if no decline occurs.

**Unobserved.**
- If more than 10 % of sidecar reads fail inside a gate's evaluation window, that gate becomes a timed wait (G_turn, or 300 s for G0), and the member is flagged `thermal.state_unobserved` (X4).

**Attribution.**
- Gate time lies in existing unowned gaps (`joulewise/align/attribution.py` `_segments`, l.555-600).
- Holds split the decode segment into unowned `hold` parts. I3 tiling must hold.
- Turn energy excludes gates and holds (`energy_residual.py:145-163`).
- Gross episode energy and latency are printed beside it.

### 2.7 Later windows and calibration targets

**Seed roles.**
- Development: index 1 (R1, W1, and the sentinels' originals) and 91-99 (R0 screens).
- Held-out: index 2 upward, assigned in kit order per model and pair.
- Sabotage is paired with a benign seed (common random numbers, as in the existing law).
- Before the first calibration window's desk is read, a **frozen-commit record** fixes every v4 slot: effort, B_m, δ, N_chunk, the heavy/light classes, the G1 branch from the contrast, and the kit and desk commits.
- Pilots 8-9 remain the closed Qwen3-30B v3 held-out set. Anchors, contrast runs and sentinels never enter any pool. Pooling is per pair (`c110a6c9`).

**Shape of every calibration window:**
- the 4 anchor originals at ordinals 1-4 (byte-identical);
- 2 sentinels of that window's model: exact seed replays of its W1 spam/benign s1 original, at ordinal 5 (early) and at the last ordinal (late);
- then the model's held-out members, alternating pair order by seed parity as in pilots 4-9, with sabotage members spread across the window.

| Window | Max | Composition | Arithmetic: align → span → max |
|---|---|---|---|
| N_k, G1 on (T confirmed or inconclusive) | 44,640 | 4 anchors + 2 sentinels + 12 benign (6/pair) + 1 sabotage (pair alternates by window) = 19 | 3,131.27 + 15 × 1,200 = 21,131.27 → 26,127 → **43,860 s** |
| N_k, G1 off (T rejected, N light) | 44,640 | 4 + 2 + 16 benign (8/pair) + 2 sabotage = 24 | 3,131.27 + 20 × 900 = 21,131.27 → 26,127 → **43,860 s** |
| D_k (default) | **59,520** | 4 + 2 + 14 benign (7/pair) + 2 sabotage = 22 | 3,131.27 + 16 × 1,800 = 35,531.27 → 40,527 → 60 × ⌈58,227/60⌉ = **58,260 s**; disk 26.4 GB/copy, 52.9 GB for two |
| D_k (if Ed vetoes 59,520) | 44,640 | 4 + 2 + 7 benign of one pair + 1 sabotage of that pair = 14 | 3,131.27 + 10 × 1,800 = 21,131.27 → **43,860 s** |

- **Why 59,520 for D.** The frozen per-session fit has only been run out of sample with 6 benign per pair per session (pilot 7). At 1,800 s per D member, a 44,640 s window holds 8 D members: one pair per window, which doubles the D series. Pilot 3 ran at 59,520 s (RUN_STATE l.1094). The binding constraint is member count, not thermal state, which is the justification Opus named.
- **Series order:** W1, N1, D1, D2, N2, N3, D3, then N4 only if G1 stays on. This is ABBA-like across days.
- **Yield at series end:**
  - N gated: 4 windows, 24 benign per pair (m ≥ 20 ✓), 2 sabotage per pair.
  - N ungated: 3 windows, 24 per pair, 3 sabotage per pair.
  - D: 3 windows at 59,520, 21 per pair (✓), 3 sabotage per pair.
  - Thresholds are at rank 20 or 21, the sample maximum (V12). There is no FPR or power claim.
- **Registration grade** (m ≥ 39 per pair, then a separately locked test cohort): only on Ed's go. It roughly doubles the series.
- **Total reservation** (defaults, gated N): 44,040 + 4 × 43,860 + 3 × 58,260 ≈ 393,300 s (109 h) of window maxima. Expected chain time is about 78 h, plus desks of about 2 h each.

### 2.8 Build list, file pointers and gates

Lanes are cut from the pilot-9 lane (`lane/2026-11-05-align-pilot9-benign` @ `c9a0a3943`). Build seat: Sol 6.1 (local or Codex Cloud). Never during a window on the measurement Mac.

**Stage 1, lane `lane/2026-11-05-align-v4-s1` (unblocks R0):**

| # | Item | Where | Test |
|---|---|---|---|
| B1 | XML tool-call parser: `<tool_call><function=NAME><parameter=KEY>VALUE</parameter>…</function></tool_call>`, multiple calls per turn, values coerced by the tool's JSON-schema type (string raw; integer, number, boolean, array and object through `json.loads`), malformed input flagged | `joulewise/align/apple/endpoint.py` `parse_completion` (l.95-161) | `tests/align/test_endpoint_xml_toolcalls.py`: typed, nested, multi-line string, malformed, truncated, and a round trip through `task.call_tool` |
| B2 | History rendering: an optional spec field `assistant_history: "reasoning_content"` makes `_render_prompt` pass `reasoning_content = hidden` and `content = visible`, both split by `_split_reasoning` (l.63). An optional `chat_template_kwargs` (e.g. `reasoning_effort`) is passed through and hashed into the execution policy. The `prior_hidden_prefill_tokens` scrub uses the same path. | `endpoint.py:240-250, 280-375`; `workload.py` `EpisodeSpec` (l.38-110; add the fields to the omit-if-None list) | `tests/align/test_history_rendering.py`, three cases:<br>• **Qwen3.8 template:** turn k's generated ids are a prefix of the rendered turn-k+1 prompt (0 rewritten tokens on closed-reasoning turns).<br>• **Anchors and the pilot 4-9 configs:** render byte-identically to today.<br>• **Spec text:** unchanged when the fields are unset. |
| B3 | Token admission budget `max_episode_decode_tokens` and `deadman_s`; flags `episode.decode_budget:<k>` and `episode.deadman:<k>` | `workload.py` loop (l.313-318) | `tests/align/test_decode_budget.py` |
| B4 | R0 tools:<br>• `scripts/align_smc_enumerate.py` (read-only; key by index; extra decoders in align-local code);<br>• `scripts/align_r0_checks.py`: NLL on a fixed 2k SHADE prompt, round-trip rewrite counter, effort/cap screen, #1632 long decode, peak memory, `pmset` and census capture. | new files | unit tests with a fake transport and a fake runtime |

**Stage 3, lane `lane/2026-11-05-align-v4-s3` (in parallel with R0; sensor names are config slots):**

| # | Item | Where |
|---|---|---|
| B5 | Sidecar, G0, G1, holds, timeouts, unobserved fallback, journal, events, neutral warmup (`warmup_condition`) | new `joulewise/align/apple/thermal.py`; `workload.py` warmup (l.257-275) and before `endpoint.chat` (l.347); hold hook in the endpoint stream loop (`_StreamObservation`, l.164 on) |
| B6 | Hold attribution: decode split at hold events into unowned `hold` segments; turn-owned and gross energy | `joulewise/align/attribution.py` `_segments`; `energy_residual.py` reads only owned segments (unchanged) |
| B7 | *(conditional, §2.2)* Hybrid checkpoint: per-turn snapshots of the recurrent (`ArraysCache`) state at prompt end. On a rewind: restore, trim the attention layers to the offset, re-feed. Metadata `cache_checkpoint_restored`, `cache_refed_tokens`. | `joulewise/align/apple/prompt_cache.py` `prepare` (l.42-94) |
| B8 | Kit v4. It imports helpers from `scripts/align_pilot_kit.py`, which stays untouched. Contents:<br>• W1 roster (§2.3) and its manifest;<br>• seed table per model tag;<br>• contrast configs derived from the pilot-7 kit (`45b47f7b6`) as specified;<br>• anchors hash-identical to pilots 4-9;<br>• base configs for N and D through `configs/campaigns/bytes_v1/generate_configs.py` with revision pins;<br>• identity pins and `model_artifact_inventory.json` from the Mac;<br>• sizing from the R1 slots file `registration/r1_slots.json`, with `fits_spent_cap`;<br>• the §2.3 fit rule. | new `scripts/align_v4_kit.py`; `configs/campaigns/align_v4/**` |
| B9 | v4 desk, which:<br>• runs the frozen alternative desk and calibration through `sys.path` to the frozen commits;<br>• prints the thermal and phase tables, U1-U6 with pass/fail/inconclusive, the contrast verdict, `--compare-session` identity against pilot 7 and R1, and the K-session anchor read (ported into repo code). | new `scripts/align_v4_desk.py`; additive functions in `joulewise/align/apple/diagnostics.py`; the v3 desk output must stay byte-identical |
| B10 | Protocol v4: models, §2.2 rules, slots S1-S9, gates, X1-X8, U1-U6, contrast rule and branches, seed roles, frozen-commit procedure, series plan | `docs/align/pilot_protocol_v4.md` |
| B11 | R1 driver and slot filler: step tests, soak, A-B-A lever tests, replays; writes `r1_slots.json` | new `scripts/align_r1_rehearsal.py` |
| T | Tests:<br>• `tests/align/test_thermal_gate.py` (fake SMC and clock: release, slope, timeouts, stop-on-G1-timeout, unobserved, no ratchet, tokens unchanged under gates and holds with a mock runtime);<br>• `test_attribution_holds.py` (tiling; pilot-8 bundles re-attributed with no holds give byte-identical turn energies);<br>• `test_v4_kit.py` (seeds recomputed independently, ABBA position sums, anchor hashes, contrast seeds equal to V11, drop order);<br>• `test_prompt_cache_checkpoint.py` if B7 is built. | `tests/align/` |

**Gates, in order:**
1. **Stage-1 review.**
   - Opus 5.5 non-author executing review: run the new tests and render real Qwen3.8 and Next-Thinking templates from the HF tokenizer files.
   - Fable 5.1 cold pass on B1 and B2, which decide what the model sees and what counts as an action.
   - CI, then merge into the v4 line.
2. **R0** (Mac by day, no window armed; the lead runs it; not a measurement). Steps:
   - offload the pilot-8 and pilot-9 roots during their desks;
   - `ls` and hash D (re-download at `815b83c0` only if it is missing);
   - download N at `9a2b4634` and hash it;
   - SMC enumeration;
   - NLL ≤ 3.0 nats/token per model;
   - round-trip counts (§2.2 checkpoint rule);
   - ≥ 95 % of D tool envelopes parse and no `unsupported_tool_call_format` flags appear;
   - D effort ladder and N cap ladder;
   - #1632 long decodes;
   - full-context peak memory: N ≤ 60 GB, D ≤ 45 GB **(guess bars)**, no swap growth;
   - `device_info` / wired limit;
   - `pmset`, census and readiness probes under Automatic (and High Power if testing).

   Each bar is pass/fail, and the record is committed.
3. **Stage-3 review.**
   - Opus executing review on a production-shaped synthetic dry run of the 19 W1 bundles. Required results:
     - `instrument_ok`;
     - a one-bit flip in each class (anchor, X-G, Y-S, N, D) fails exactly that member;
     - the drop rule works;
     - the v3 desk output on pilot-8-shaped bundles is unchanged.
   - Fable cold pass on B5, B6 and B7.
   - **Registration cold gate** (Fable + Opus, blind) on protocol v4.
   - CI.
4. **R1** (quiet; Interactive LaunchAgent; no agent alive; about 4-4.5 h by day):
   - 30 min idle soak;
   - planning-turn step tests with 10 min cooldowns for the 30B, N, D and F;
   - D A-B-A lever tests, if Ed opts in;
   - 2 gated N spam/benign s1 runs (these are U3 and the W1 cross-session reference);
   - 2 gated D spam/benign s1 runs, with holds if heavy (token identity under holds, U3);
   - 1 X-G contrast run (gate cost; token identity against pilot 7);
   - 1 gated F episode (screen: parser on `qwen3_5_moe`, peak, rates);
   - fill S1-S9, B_m, I_m and the heavy/light classes.
5. **Lead verifies the slots.** Then:
   - freeze span and disk;
   - check the ledger pin;
   - real `prepare`;
   - arm notice;
   - install.

**Critical path.** Pilot 9 (≈ 6.5 h) runs alongside the stage-1 build and review. Then R0 (≈ 5-6 h, mostly D's ladder and long decode) runs alongside the stage-3 build and review. Then R1 (≈ 4.5 h), then arm W1. That is about 2-3 days to W1. Nothing on the analysis laptop waits on the Mac, or the reverse.

---

## 3. Ed's checklist

### 3.1 Physical tasks (once, before R1; then untouched for the whole series)
1. A hard, flat stand with ≥ 5 cm clearance under and around the intake and exhaust. Lid open, out of the sun, away from heaters.
2. Room thermostat at a fixed setpoint, and write it down.
3. If you have one, a standalone ambient logger at 1/min, 30 cm from the intake. Otherwise, read a thermometer at arm and at the desk. Ambient is recorded, never gated.
4. Battery ≥ 95 % at arm, **Optimized Battery Charging off**, and the 140 W MagSafe connected directly.
5. Optional: if you own a laptop cooler, put it in place but leave it off. R1 decides by the ≥ 25 % rule whether it is used for the whole series. No third-party fan-control software.
6. As always, before R1 and every window: close the agent apps and sessions on the measurement Mac.

### 3.2 Questions only Ed can answer (I ruled defaults; the design runs under them)

| # | Question | **Default (ruled)** | If Ed answers otherwise |
|---|---|---|---|
| Q1 | Which "Qwen 3.8"? | **Qwen3.8-27B** (dense; D, 8-bit). | **Flash-Next:** it cannot run on the pinned MLX stack:<br>• `qwen4_exp` support is only in mlx-lm PR #1788, still open;<br>• the 4-bit build is 111.5 GB, about 97 % of the GPU working set.<br>W1 still runs D as the Qwen3.8 representative. A separate engine council weighs two routes:<br>(i) a second pinned venv once #1788 merges, plus a wired-limit sysctl;<br>(ii) a llama.cpp/GGUF engine.<br>If Ed wants a large production MoE in the first series anyway: W1's 3 D members become 3 × 122B (F, on disk; XML parser path; no history fix needed), and D moves to D1. |
| Q2 | Is the 122B in? | **Reserve:** an R1 screen only. | **In:** the R1 screen counts as its qualification. It becomes a third cell with 3 calibration windows at 59,520 s (its members are ≈ 1,500 s, so it needs the same long-window shape as D). W1 is unchanged. Series +3 windows. |
| Q3 | Approve the ≈ 45 GB N download and the pilot-8/9 root offloads? | **Yes.** Same verified-offload practice as pilots 4-7: every file re-hashed in iCloud before local deletion. | **No:** N = Next-Instruct-4bit (on disk, `d8a069bf`). No reasoning-omission estimand for N; its tamper grid is not computed. The R0 N ladder and round trip are skipped (append-only, `e1308804`). Sampler 0.7/0.8/20/0. The W1 shape is unchanged. |
| Q4 | Allow 59,520 s maxima for D calibration windows? | **Yes** (§2.7). | **No:** D windows hold one pair each at 44,640 s, so D takes 6 windows instead of 3. |
| Q5 | Test High Power mode (fan noise) in R1? | **Yes.** It is adopted only under the R1 rule. | **No:** stay on Automatic throughout. |
| Q6 | Registration grade (m ≥ 39 per pair plus a test cohort)? | **No:** a pilot series to m ≥ 20. | **Yes:** about double the calibration windows per model, decided before any alarm is read. |
| Q7 | If Mac time is short, which model first? | **Interleave:** N1, D1, D2, N2, … | **N first:** it is cheaper. D stops after D1 until Ed resumes it. |

---

## 4. Residual risks

1. **D may not be controllable within the member cap.** If holds plus a 6,144-token budget leave fewer than about 3 turns per episode, D goes to 4-bit. If even 4-bit fails, D is a screen. The capability read will then reflect time, not ability, and protocol v4 must say so.
2. **Capability.** The bars:
   - N-Thinking: the card recommends 32,768 output tokens, against our 4,096-8,192 per-turn cap;
   - D at reduced effort: the card warns about this.

   Either model may fail the capability gate: no state-changing action per pair in any benign W1 episode. A model that fails is reported as an energy and capability screen, not as a monitored production agent.
3. **New endpoint code (B1, B2).** It changes what D sees. A defect here corrupts D's behavior silently. R0's round-trip bar (0 rewrites on closed-reasoning turns) and Fable's cold pass are the guards.
4. **#1632 on 0.31.3.** The mitigation is a guess until R0. The fallback (a second venv) is a stack change with its own ruling, and it delays N or D.
5. **SMC thermometry on M3 Max is unverified.** Without a die-class and a heatsink-class key, there is no thermal-control claim (U4/U5 not evaluable). The only fallback is an IOHID lane, about a day.
6. **The contrast may be inconclusive.** Gates then stay for all cells, at about 25-35 % extra member time **(guess)**, which is about one extra N window.
7. **Calibration is thin by construction.**
   - Per-session fits use 6-8 benign per pair per session.
   - m = 20 is the sample maximum, and there are only 2-3 held-out sabotage per pair.
   - Window dependence limits exchangeability.
   - No FPR or power claim can be made (Sol).
8. **Realism.** Gated and held energy is energy at a reference state. Production agents do not pause, and the paper must say so. The gross-energy print and the contrast measure the gap.
9. **The anchor bridge moves.** The new stand and physical setup change the 30B's state, and the K-session offset at the W1 boundary cannot separate setup from session. It is printed, not used for acceptance.
10. **Lookahead leakage at holds.** If the hold starts before the in-flight step completes, about one decode step of energy goes unowned. B5's specification and test, and R1's held D replay, guard this.
11. **Disk and time.**
    - W1 needs 37.2 GB for two copies, plus N's 44.9 GB. Arm only with ≥ 80 GB free after weights.
    - D windows need 52.9 GB for two copies.
    - The full series is about 4-5 days of Mac time, competing with DIFFICULTY and the Paper-1 checkpoints (RUN_STATE l.1191).
12. **The pilot-9 dependency.** Pilot 9 runs only if the pilot-8 read supports it (`c110a6c9`). If it does not run, the v4 path does not change; only the R0 start moves earlier.
13. **Page-cache churn.** Three models (17 + 45 + 29.5 GB) alternate member by member in W1. Load heat falls inside the idle and G0, but R1 must measure I_m per model. A cold load longer than about 60 s **(guess)** pushes the span toward the fit rule.
