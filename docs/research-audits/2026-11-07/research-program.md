# Research program audit, synthesis: what is noteworthy so far, and what next

Date 2026-11-07. Synthesis by Opus 5.5 (xhigh) of two independent seat reports on Ed's question, "are there any signs when working this will lead to any noteworthy research?":
- **Seat 1:** Fable 5.1 (high). Its own durable copy is `docs/research-audits/2026-11-07/research-program/fable-seat.md` on `research/2026-11-07-research-program-fable` @ `d3c9d5894`.
- **Seat 2:** Opus 5.5 (xhigh). It committed nothing, so Appendix B is its only durable copy.

This is model-written triage input. Do not adopt it wholesale (`docs/handoff/2026-11-07-account-retirement/RESUME.md:50`).

**Evidence base.** Citations are `path:line @ commit`. Bare `RUN_STATE.md:N` and `RECORD …:N` lines are at `origin/main` = `bd7a3efcd`. "Records" means `docs/process_traces/<date>-magistrate-<id>/RECORD.md`. The commits are:
- the BYTES lane `lane/2026-10-28-bytes-pass2-open` @ `ee4ce93fc`;
- the ALIGN measurement lane `lane/2026-11-05-align-pilot10-benign` @ `5f817856b` (with `83e2dac59` for `pilot_protocol_v3.md`);
- the v4 R1 lane @ `e901eb2a4`;
- the DIFFICULTY readiness lane @ `cef8388c7`;
- the ALIGN desk alternative @ `cda28a5ef` and the frozen calibration @ `7fbd95e31`.

**Blinding.** I did not read, list or open `/Users/edr/jw-b5-*`, `/Users/edr/night-*`, night-custody, night-archive, any `restricted/` path or any `night-results/*` branch, and I did not follow repo pointers into them. I read no Block-5 or Block-6 outcome and inferred none. BYTES science energies are still blinded and were not read. Every number below is one of:
- an already-unblinded instrument check;
- a non-claim pilot read recorded in `RUN_STATE.md` or a magistrate record;
- a design document;
- my own estimate, labelled **[estimate]**.

---

## Executive summary

1. **Yes. The one genuinely novel line is ALIGN: energy as a record of an agent's work that the agent cannot edit.** On Qwen3-30B-A3B in SHADE-Arena:
   - A frozen token-count energy model with attention-length terms leaves a per-pair leave-one-out residual SD of 19-58 J on episodes of 2-4 kJ.
   - Token-identical replays repeat to about 2 J.
   - In every held-out test, simulated omission of one turn's logged reasoning (539 or 1,193 tokens) crossed the frozen thresholds.

   Neither seat found published work that uses power as a monitoring record for agents, and neither did I. **But the held-out sabotage evidence is two distinct trajectories, scored in three sessions.** The thresholds are sample maxima, and the tamper is a post-hoc edit of the log, not real hidden work. Today it is workshop-grade. One or two Mac-nights on the 30B plus desk work would make it a strong paper (E1, E2).
2. **Paper 1's strongest material is BYTES plus the known-bytes (KB) result.** About three quarters of marginal memory-traffic energy falls outside the `powermetrics` CPU+GPU+ANE rails: f = 0.238 ± 0.098, from one latency-bound session. Seat 1 said the KB outcome was missing. It is on main.
3. **The largest risk to Paper 1 is operational, not scientific.** BYTES stage 1 is due 12 Nov and needs no measurement window. It has no owner and no pointer:
   - the retirement `RESUME.md` mentions neither BYTES nor Paper 1;
   - `CANONICAL.md` has no BYTES row;
   - the registration and the analysis code sit on a lane last committed 10-28.
4. **ALIGN v4's W1 will probably be refused under ruling 1(f).** Rule the 1(e) fallback order now, blind. A 30B confirm-and-inject night (E2) is the best fallback, and arguably belongs before the D series in any case. It needs Ed's OK, because he ruled that pilot 10 is the last v3 pilot.
5. **DIFFICULTY is ready on the analysis side, but its collection code is unbuilt, and its novelty is modest.** Jin, Wei and Brooks (2025) already report a difficulty-dependent small-vs-large accuracy-per-energy trade-off on MATH500. Keep it third and lean, and treat it as a section of Paper 2.

---

## Decisions needed from the lead

1. **Give BYTES stage 1 an owner and a date now: stage 1 → prediction commit → held-out agreement → stage 2.** The checkpoint is 12 Nov, with Tier D for Part 2 if it misses 15 Nov (`docs/strategy/2026-10-27-paper1-contingency.md:40`). Put it in the next RUN_STATE item and in `RESUME.md`, and add a BYTES row to `CANONICAL.md`. The concrete steps:
   1. Land the BYTES lineage (`lane/2026-10-28-bytes-pass2-open`), copying the KB slot fill into `bytes_pack_v1.md` §1. It still reads PENDING at `ee4ce93fc:36`; the fill is `docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md:3`.
   2. Build the stage-1 export.
   3. Re-run the thermal lines with `--export` into a new directory (`RUN_STATE.md:1806`).

   The thermal-line outputs live under night-archive on the MBP (`RUN_STATE.md:929`). So stage 1 is either a by-day MBP job for the magistrate or needs a transfer. It needs no quiet window.
2. **Rule ruling 1(e)'s fallback order before R1's numbers exist.** The kit refuses W1 and names the largest fitting B_D when 1(f) does not fit (`docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md:58-61,199-207 @ e901eb2a4`). Candidates: the largest fitting B_D, 4-bit D, D as a screen while the 30B series continues, or waiting for Flash-Next. **Recommendation:** on a refusal, run E2 (if decision 3 allows it), then retry W1 at the kit's largest fitting B_D. Do not open a design session inside the 15-22 Nov writing window.
3. **Put the ALIGN paper question to Ed.** The options are "energy as an independent record of logged compute" and "does sabotage leave an energy signature".
   - The first needs no deceptive, capable agent, so the 30B is enough. The second needs v4.
   - I recommend the first as Paper A's claim, with v4 and Flash-Next as the extension.
   - Running E2 conflicts with Ed's direct ruling (`RUN_STATE.md:1653`, item 174), so it needs his OK. Frame it as a confirmatory positive control, not more calibration.
4. **Get Ed's answers to Q4 and Q6, or rule on them.** Q4 asks whether D calibration windows may run to a 59,520 s maximum. Q6 asks whether the series should reach registration grade (m ≥ 39 per pair plus a test cohort). Both are listed in `docs/align/council-2026-11-05/FINAL-DESIGN.md:635-637`, and I found no answer in `RUN_STATE.md`. A "no" to Q4 doubles the D windows (3 → 6), and a "yes" to Q6 roughly doubles the calibration windows (`FINAL-DESIGN-AMENDMENT-1.md:123-124`).
5. **Decide whether to run a bandwidth-bound KB repeat (E3, about 1.3 h) before Paper 1's 15 Nov scope freeze.** It would be labelled exploratory. The alternative is to report the KB result only with its regime limit (`KB-SLOT-FILL.md:77`).
6. **DIFFICULTY: pick the lean path or defer.** The lean path has two parts, each logged in the public deviation log under the lead's prereg authority:
   - collect energy through the unpinned ALIGN Apple runner instead of block-6 sessions (`FINAL-DESIGN.md:50`, V8);
   - run the bench off the quiet Mac, after an output-identity check.

   The alternative is to defer DIFFICULTY to December. Its end date is 2027-01-31.
7. **Refresh the advisor-facing status pages before the 22 Nov draft.** `PROJECT_STATUS.md:77` still says "No claim-bearing Qwen3 data exist" and names the four-rung probe as the next milestone (`:169-179`). `CLAIMS_STATUS.md:38` was last updated 2026-08-20.
8. **Paper 1 framing.** The current title is "Timing Sensitivity of Phase-Energy Assignments on Apple Silicon" (`docs/paper/draft-v2-skeleton.md:7`). Both seats recommend leading instead with what a laptop's own power counters can and cannot resolve for LLM inference: BYTES, KB coverage, the attribution floor, then the replication.

---

## Where the seats disagreed, and how I resolved it

| # | Topic | Seat 1 (Fable) | Seat 2 (Opus) | What I checked | Ruling |
|---|---|---|---|---|---|
| R1 | Known-bytes (KB) outcome | "outcome not found on main" | f = 0.238 ± 0.098, from `KB-SLOT-FILL.md` | The file is on main at `bd7a3efcd`: classes at `:14`, contrasts at `:20-23`, f at `:60`, regime at `:77`. The lead admitted the reading rule (`RUN_STATE.md:903`), and "KB test done" is at `:1810`. | **Seat 2 is right.** Still owed: the copy into `bytes_pack_v1.md` §1. |
| R2 | Did BYTES pass 2 close? | open question | — | `RUN_STATE.md:896-901`: s1-p2 counts, all 12 sub-packs count, and addendum §5 is appended. | **Closed.** |
| R3 | Untampered sabotage below threshold | "every untampered sabotage stayed below" | "2 distinct trajectories" | Pilots 8-10 were "8 anchors + 20 fresh benign" (`RUN_STATE.md:1662,1700,1713`). The six held-out scores are each pair's seed-1 sabotage, scored in three sessions (RECORD 3efb8793:21-23). On pilots 4-9, as a labelled diagnostic, the sequence design puts 2 of 26 untampered bank sabotage above 3.46 at m 35 (pilot 6 seeds 1 and 11) and 0 of 26 spam (RECORD f775edaf:25). On pilot 7 out of sample, 3 of 6 spam were above at m = 6 (`RUN_STATE.md:1712`). | **Seat 2 is right.** Seat 1's wording holds only for the two held-out trajectories. |
| R4 | BYTES "(1c)" thermal transform | — | still owed (`RUN_STATE.md:359`) | Superseded. BY-THERM-LINES ran on all 12 counting sessions on 10-31, every run rc 0 and `view verified` (`RUN_STATE.md:928-932`), and "Thermal lines are DONE for the BYTES pass-2 analysis" (`:1806`). Only the `--export` re-run is left. | **Seat 2's item is stale.** |
| R5 | D decode rate for 1(f) | about 11 tok/s (`LEAD-RULINGS-2.md:61`) | about 20 tok/s (`RESUME.md:41`) | Both figures are in the repo, and R1 measures the rate. Both seats conclude that 1(f) probably binds. | No ruling needed. The conclusion stands. |
| R6 | ALIGN v4 cost | 4-5 nights (W1 + D1-D3) | 6-8 Mac-days nominal, 9-12 with refusals (R1 included) | W1 + 3 D windows reserve 219,420 s (61 h) of maxima, with about 45 h of expected chains plus about 2 h of desk each (`FINAL-DESIGN-AMENDMENT-1.md:125`). A D window is 58,260 s (16.2 h), longer than a 12.4 h night (`:117`). R1's worst case is 56,207-61,607 s (`RESUME.md:39`). Under the Q4 veto it takes 6 D windows (`:123`). | **R1 + W1 + D1-D3 ≈ 5 calendar Mac-days nominal** (about 77 h of maxima with R1). **8 days under the Q4 veto.** Seat 2's 1.5-2× refusal factor is a judgment from history, not a repo number. |
| R7 | DIFFICULTY contamination | "unaddressed" | (not raised) | The registration acknowledges it as an accuracy caveat (`difficulty_pack_v2.md:379`). It has no perturbation or contamination check. | **Acknowledged, not tested.** It bears on accuracy claims more than on a same-family EPC crossover. |
| R8 | ALIGN detection limit | — | **[estimate]** 170-470 hidden tokens, assuming score = residual / s_r | The score is (measured − predicted) / √(sd_pred² + half_width²), with sd_pred² = sᵀΣs + n_turns·σ²_turn (`joulewise/align/energy_residual.py:513-588 @ cda28a5ef`). It is not residual / s_r. | **Dropped.** The data bound is H ≤ 539 (spam) and H ≤ 1,193 (bank) at the smallest tamper. A finer grid is already planned (`RUN_STATE.md:1723`; `FINAL-DESIGN.md:430`). |
| R9 | Prior-art ratio | — | decode/prefill cost falls "from about 335× to about 3.3× under batching" | Opened https://neurips.cc/virtual/2026/170701. 335× is prefix-cached batch 1. The fall to 3.3× is from 115× at uncached batch 1. | **Corrected.** The point stands: per-request attribution weakens under batching. |
| R10 | Jin, Wei, Brooks 2025 | — | "MATH500 with Qwen2.5" | Opened https://arxiv.org/html/2505.14733. It uses DeepSeek-R1-distilled Qwen2.5 at 1.5B-32B on MATH500 and LiveCodeBench by difficulty. "Smaller models with RT can match the performance of larger models for easier tasks." | **Confirmed.** DIFFICULTY's novelty is in measured joules and preregistration, not in the crossover. |
| R11 | Where DIFFICULTY goes | Paper 3, a chapter or short paper | a section of Paper 2 | Both seats call the novelty modest. | **A section of Paper 2, or a chapter.** Weight the "energy price of thinking" output (4B on vs off), which is registered as descriptive (`difficulty_pack_v2.md:197`). |
| R12 | Next ALIGN experiment on the 30B | E4: real adversary plus metadata and LLM-monitor baselines | E2: fresh sabotage seeds plus real injected unlogged compute | The estimand is omitted work (`docs/align/PIPELINE.md:9-20 @ e901eb2a4`). The 30B rarely achieves the side task: only spam/sabotage seed 1 succeeded in pilot 4 (RECORD c9ac22ae:21). Prompt-induced work confounds the residual (RECORD 7e06863b:38-39). | **Merged.** Injected compute at blinded doses is the primary arm. An adversary-instructed arm and the baselines are secondary (E2 below). |

---

## Findings (agreed or verified), by severity

### High

**H1. BYTES stage 1 has no owner or pointer, but it is Paper 1's best result and needs no quiet window.**

Evidence:
- `RESUME.md` (the new lead's entry point) has no line mentioning BYTES, Paper 1 or stage 1. A search of the file returns nothing.
- `CANONICAL.md` has sections for project state, ALIGN windows, Block-5 analysis, Flash-Next, CI and the paper, and none for BYTES or DIFFICULTY.
- `joulewise/bytes_analysis.py` and `docs/registrations/bytes_pack_v1.md` are not on main. They are on `lane/2026-10-28-bytes-pass2-open`, last committed 2026-10-28.
- The KB slot fill is waiting to join that lineage (`KB-SLOT-FILL.md:3`).
- `RUN_STATE.md:1846` says only "BYTES stage 1 is planned for 12 Nov (contingency plan), after the KB outcome". The KB outcome has existed since 10-31.

Why it matters:
- The design separates the hypotheses well on the three MoE models. The resident-size prediction is 8.42, 19.43 and 12.20 times the bytes prediction, and the time prediction is 1.68, 2.22 and 1.39 times it (`bytes_pack_v1.md:27 @ ee4ce93fc`).
- Collection is complete: 12 of 12 sub-packs count (`RUN_STATE.md:896-901`).
- The `test_bytes_analysis` CI shard takes 8,973 s (`RUN_STATE.md:926`). Budget for that.

**H2. The ALIGN headline is real but thin.** Both seats agree on the core numbers, and I re-checked each one.
- **Residual SD.** Per-pair s_r under the frozen sequence design `[1, P, D, (C+P)D + D²/2, CP + P²/2]`:

  | Pilot | Bank (J) | Spam (J) | Source |
  |---|---|---|---|
  | 8 | 250.8 → 58.3 | 45.4 → 19.0 | `RUN_STATE.md:1699` |
  | 9 | 274.0 → 45.1 | 118.8 → 32.7 | RECORD f775edaf:17-18 |
  | 10 | 232.9 → 45.5 | 47.5 → 24.2 | RECORD 3efb8793:22 |

  The marginal decode cost e is 0.667 J/token (bank) and 0.495 J/token (spam).
- **Repeatability.** Pilot 5 repeated pilot 4 exactly: pair-difference SD 2.97 J, 2.1 J per measurement, window contrast −0.43 J (SE 0.61) (`RUN_STATE.md:999`). Across K = 7 sessions: residual SD 1.93 J, σ_w 4.67 J (RECORD 3efb8793:21).
- **Held out (frozen `7fbd95e31`, pilots 8-10, seeds 17-46).** m = 28 per pair, rank k = m, so each threshold is the sample maximum.
  - The thresholds are bank 2.53 and spam 7.13. The spam threshold rests on one trajectory; the next spam score is 2.99.
  - The six untampered sabotage scores are all below. They come from two distinct trajectories.
  - Every sabotage trajectory was detected at k = 1 (H 1,193 bank, 539 spam) (RECORD 3efb8793:23).
- **Not claimable.** There is no FPR or power claim (`FINAL-DESIGN-AMENDMENT-1.md:105`). The tamper "describes detection of a known log omission, not a causal effect of sabotage" (`docs/align/pilot_protocol_v3.md:155-163 @ 83e2dac59`). Cross-pair transfer fails: the grouped threshold is a transfer statistic (RECORD 7e06863b:24,38).

**H3. W1 is likely to be refused under ruling 1(f), and the fallback is unruled.**
- The builder reports: "(6,144 + 4,096)/11 ≈ 930 s against T_dead ≈ 1,200-1,280 s … When it does not fit, the kit refuses W1" (`LEAD-RULINGS-2.md:61`).
- R6-3 fixes the slowest observed rate and the full turn cap, with no code fallback: "the lead rules on ruling 1(e)'s fallback after the R1 night" (`:199-207`).
- `RESUME.md:41` calls this the "open lead call after the R1 night".

Ruling it after the R1 night puts a design decision into the Paper-1 writing window. Rule it now, blind (decision 2).

### Medium

**M1. KB: `powermetrics` rails miss about three quarters of marginal memory-traffic energy.** This is the most surprising unblinded physical number. Seat 2 found it; seat 1 missed it.
- Rotate-minus-repeat contrasts, in J/GB: rails 0.0092 ± 0.0021, GPU rail 0.00879 ± 0.00010, DC input 0.0389 ± 0.0072, rest 0.0296 ± 0.0084 (`KB-SLOT-FILL.md:20-23`).
- f = 0.238 ± 0.098 (`:60`). Both gate seats' independent programs agree to within 6e-10 J/GB (`:25`).
- 85% of the GPU-rail contrast is stall time. "Three quarters of the DC contrast is in rest" (`:72-76`).

Limits:
- one session;
- a latency-bound 32 MiB geometry at 106-116 GB/s, against decode's 209-344 GB/s (`:77`; `docs/design/bytes_pilot/SUMMARY.md:39 @ ee4ce93fc`);
- "rest" mixes memory chips, power conversion and fans (`:55`).

Relevance: current Apple-silicon LLM energy work relies on `powermetrics` alone. GreenBench (Aug 2026) uses "macOS powermetrics for direct power measurement" on an M4 Pro (https://arxiv.org/abs/2608.28667, opened). If the result holds in the bandwidth-bound regime, it is a correction others will cite.

**M2. The naive-design trap is a cautionary methods result.**
- The registered design `[1, P, D, C·D, C·P]` charged no attention over the freshly prefilled turn-0 prompt.
- The spam sabotage prompt is 755 tokens longer (7,102 vs 6,347), so untampered spam sabotage false-alarmed 5 of 6 times in pilot 6. The attention-length design removed most of that (RECORD 7e06863b:27,38-40).

Any count- or energy-based agent monitor faces the same trap. This also partly answers seat 1's open question 6:
- The +241 J figure was pilot 4's bank/sabotage cell offset under the registered design (RECORD c9ac22ae:23).
- The 755-token difference belongs to the spam pair.
- Under the sequence design, the held-out bank sabotage scored below threshold.
- No decomposition of the old offset is in the repo.

**M3. Thermal and DVFS state is the dominant nuisance.**
- Benign residuals correlate with mean GPU clock in bank: +0.92, +0.87 and +0.79 in pilots 8-10, positive for five sessions in a row (`RUN_STATE.md:1699,1682,1644`).
- An 8-9 J step between pilots 5 and 6 sits in the decode segments (−0.41%). No temperature was recorded, so it is not attributable (RECORD 7e06863b:38).
- v4 adds the SMC journal, the gates and the W1 T-vs-W contrast (`FINAL-DESIGN.md:15-23,432-446`).

No one has analysed an adversary who shapes DVFS state or hides work in low-clock periods.

**M4. ALIGN framing and prior art (external sources opened 2026-11-07).**
- **SHADE-Arena.** "Success on the side task relies heavily on having access to a hidden scratchpad"; the top monitor has AUC 0.87 (https://arxiv.org/abs/2506.15740). Energy could bound the size of hidden reasoning without seeing its content.
- **CoIn.** It audits invisible reasoning-token counts and detects inflation "with a success rate reaching up to 94.7%", deployed "as a trusted third-party auditor" (https://arxiv.org/abs/2505.13778). Power needs physical access instead of provider cooperation.
- **Hardware-enabled mechanisms.** The abstract names compute amount, cluster configuration or location, and policy enforcement. It does not mention power or energy (https://arxiv.org/abs/2505.03742).
- **"Prefill, Decode, and Context: A Measured Energy Law for Agentic LLM Serving"** (NeurIPS 2026 workshop poster). A three-term per-call model reaches R² = 0.961 (https://neurips.cc/virtual/2026/170701). The fit form is therefore not ALIGN's novelty. The forensic use and the precision are.
- **The inverse use of the same physics:** side-channel recovery of network architecture and weights from power (Batina et al., https://arxiv.org/abs/1810.09076).

Two things are still owed:
- **A stated threat model.** The candidates are an operator-controlled meter on-prem or at the edge against agent-editable logs, or a metered audit. Either must be reconciled with the project's "no adversarial process on the machine" limitation (`CLAIMS_STATUS.md:14-19`) and with batch 1 only.
- **A counts-only baseline.** It is already a bank row, `RQ-ALIGN-METADATA-BASELINE` (`docs/align/PIPELINE.md:26 @ e901eb2a4`), and has never been run.

**M5. DIFFICULTY: the science is ready, the plumbing is not.**
- **Registration.** v2.3, refuted and fixed twice, including the near-tie fix that brought a 6% false "changes with level" rate to the level-1 energy subset of 70 (`difficulty_pack_v2.md:5-9`).
- **Code.** Registered at `fc4078667` (`:390`).
- **Simulated effects.** ln(EPC 1.7B / EPC 4B) is −0.58 to −0.99 at level 1 and +0.48 to +0.67 at level 5 (`:118`).
- **Collection side: absent.** The loop's module shapes cannot carry attempts, the runner forces `suppress_eos=True`, and the energy adapter and bench runner are unbuilt. Revision 2.4 is unwritten, and the #416 freeze audit has not run (`RUN_STATE.md:325-331`, DIF-READY-1 @ `cef8388c7`).
- **Machine time** (`:201`):
  - about 14.5 h of thinking-off energy session time;
  - about 1.2 h of 4B thinking-on energy attempts;
  - about 13.0 h of thinking-off bench and 3.8 h of 4B thinking-on bench, with 5.6 h more for the optional 8B thinking-on bench.

  The bench needs no power capture.
- **Contention level.** It must be recorded before the first energy session (`:218`).

**M6. The advisor-facing status pages are two collection blocks stale.** See decision 7. Both seats found this.

### Low

**L1. Throughput and proportionality.** Much of the cost is self-imposed.
- About 3 s of each Block-5 run's roughly 237 s is measured, and about 230 s are waits (`docs/design/next_block_threshold_proportion.md:30-31,316`).
- The ALIGN member law is 516.575 s + 1.13544 × episode_s (`FINAL-DESIGN.md:44`, V2).
- R0, a desk check, is on re-run 8 after refusals by scheduled macOS jobs (`RESUME.md:34`; `RUN_STATE.md` items 188-195).

The advisor's over-engineering remark will also be a reviewer's. Report what the machinery bought in one table.

**L2. Without prefix caching, agentic energy is dominated by prefill.**
- Pilot 2 used 147k-645k prefill tokens per episode against at most 7.7k decoded (`RUN_STATE.md:983`).
- With the episode-prefix cache, identical work fell from 14,451 to 2,232 J and from 20,563 to 1,380 J (RECORD af17111e:17). This is confounded: pilot 2 was throttled.

This is practitioner-note material, not a headline.

**L3. Laptop thermal and battery limits.**
- OS thermal onset came 178-209 s into A-bank episodes (RECORD af17111e:13).
- The Llama-70B BYTES decode cell kept 2 of 10 quads in s5-p1 (`RUN_STATE.md:277`). The s5-p2 hull line adds `thermal.os_level_nonzero` to 23 Llama-70B members (13 units) (`:930`).
- macOS topped the battery up mid-session at about 95% (RECORD 3efb8793:18).

This threatens BYTES' top dense point. Whether 70B still has a usable point can be answered structurally, without unblinding.

**L4. Stale TASK_QUEUE rows.** A282, A285 and A293 are the "HEADLINE" 1.7B-vs-8B AP-5M rows. They predate DIFFICULTY v2 and should be pruned (`TASK_QUEUE.md:891,894,901`).

**L5. A curiosity from R0.** Qwen3.8-27B scores 11.04-11.06 nats/token on its own system and tool block, reproduced in HF fp32 on the upstream weights. The Qwen3.5-0.8B sibling scores 0.467 (`docs/align/v4/R0-LOAD-REFERENCE-NOTE.md:22-34 @ 5f817856b`). The cause is unverified. This is not a paper line.

---

## The strongest papers (reconciled)

1. **Paper 1 (due 30 Nov).** Method, replication and BYTES, led by what a laptop's own counters can and cannot resolve:
   - BYTES H1 words on the MoE trio and the H2 slope at DC input and at rest;
   - the KB rails-coverage result;
   - the attribution floor (about 1 J against 0.29-0.49 J repeatability; clearable phase contrast about 5 J; `PROJECT_STATUS.md:100-105`);
   - the clock-anchor knife-edge (`CLAIMS_STATUS.md:230-235`);
   - Block 5 beside Block 6.

   Its value does not depend on any outcome (`2026-10-27-paper1-contingency.md:8-15`). Its limits: one machine, one stack, single unit (registry level L2, `docs/research_question_registry.md:89`); a three-point fit set; dated models.
2. **Paper A (ALIGN): "Power as an independent record of agent work".** Present the v3 corpus (pilots 4-10, the frozen design and frozen calibration) as a frozen-analysis pilot, not a registered confirmatory study. With E1 and E2 it becomes a strong paper. v4 and Flash-Next are the journal extension: until Flash-Next lands there is "no cross-model monitoring claim" (`FINAL-DESIGN-AMENDMENT-1.md:17-19`).
3. **A practitioner note, or a section of Paper 1: measuring LLM energy on a Mac.** It covers rails coverage, the scheduled-contention catalogue, battery top-ups, thermal onset and identical-work repeatability. The evidence already exists.
4. **DIFFICULTY**, as a section of Paper 2 or a chapter.
5. **Optional, after 30 Nov: the AI-agent-operated lab as a case study.** Only after a proportionality pass.

---

## Priority order

Ed's order is right on value: BYTES, then the agent-monitoring pilots, then DIFFICULTY, with collection overlapping Paper-1 writing (`2026-10-27-paper1-contingency.md:115-120`; `RESUME.md:17`). Four adjustments:

1. **Lead attention goes to BYTES stage 1 first** (H1). It uses no window and is the checkpoint most likely to slip silently.
2. **ALIGN:** R0 re-run 8, then R1 as planned. If W1 is refused, run E2, subject to Ed's OK (decision 3). Consider E2 before D1 even if W1 passes, because it upgrades the estimand from simulated to physical.
3. **DIFFICULTY third.** Build it lean, and only with capacity Paper 1 does not need. The plan already says Paper 1 goes first during 15-22 Nov (`:112-113`).
4. **Do not resume v3 calibration** (`RUN_STATE.md:1653`). E2 is a positive control, not calibration.

---

## Next experiments

Mac-night ≈ 12.4 h window. Effect sizes marked **[estimate]** are back-of-envelope figures from repo numbers, not repo results.

| # | Experiment | Expected effect | Cost | Main risks | Seats |
|---|---|---|---|---|---|
| **E0** | **BYTES stage 1 → commit → held-out agreement → stage 2** | Resident vs bytes differ 8.4-19.4× and time vs bytes 1.4-2.2× on the three MoE models, so the MoE words are likely resolvable. Dense held-out models are unresolved by design (2-9%; `bytes_pack_v1.md:27`). The H2 J/GB slopes at DC input and rest can be cross-checked against KB. | **0 windows.** About 1-3 analysis days plus reviews. | Lineage not landed; data on the MBP; 70B usability (L3); drift scale retained because test 7 established no pass (`bytes_pack_v1.md:441`), so intervals may be wide. | both |
| **E1** | **ALIGN desk work on existing v3 data:** (a) a measured detection curve on the planned tamper grid H ∈ {128, 256, 300, 512, 1,024, …} (`FINAL-DESIGN.md:430`); (b) the counts-only metadata baseline (`PIPELINE.md:26`); (c) rescore pilot-7 sabotage seeds 12-16 against the pilots 8-10 thresholds, labelled post hoc because pilots 4-7 were selection data (RECORD f775edaf:25); (d) an idle-truncation refit, prospective only. | (a) replaces the unmeasured detection limit (R8); (b) separates "energy verifies logs" from "counts flag sabotage", and the AUC is likely high because of the +755-token prompt; (c) raises the untampered-sabotage count from 2 distinct trajectories toward 12; (d) tests whether the 516.6 s fixed member cost can roughly halve. | **0 windows.** The pilot 4-7 roots are offloaded to iCloud (`RUN_STATE.md:1699,1712`); the pilot 8-10 roots are on the MBP. | (c) is post hoc and must be disclosed; (d) changes a protocol constant. | S2 (S1: baseline) |
| **E2** | **30B confirm-and-inject night** (v3 shape): anchor originals as the bridge; about 12 fresh sabotage seeds scored against the frozen thresholds; about 12 benign seeds with **real unlogged compute** at desk-blinded doses of 0, 256, 512 and 1,024 tokens. Secondary arm: adversary-instructed prompts, plus a local LLM monitor on the same transcripts. | **[estimate]** At e = 0.49-0.67 J/token for in-context hidden decode, the doses add about 125-170, 250-340 and 500-690 J, against per-pair s_r of 19-58 J. So 512 tokens or more should be detected and 256 is marginal. Fresh-context side generation costs nearer the bare decode coefficient (about 0.18 J/token; RECORD 7e06863b:39), so it needs about 3× the tokens. A run of this shape also reaches m ≥ 39 (`RUN_STATE.md:1662`). | **1-2 Mac-nights.** The pilot-10 shape was a 6.5 h chain (`RUN_STATE.md:1682`) plus about 100 min of desk. Needs a small change to the unpinned runner. | Ed's v3 ruling; injection changes thermal and clock state; the injection site must match the stated threat model; the 30B is a weak saboteur. | both, merged |
| **E3** | **KB in a bandwidth-bound geometry**, plus one decode-matched check | If DC J/GB stays near 0.039 while rails J/GB falls, f drops below 0.24 and "rails undercount memory energy" transfers to decode. If not, the result is regime-specific, which is also worth knowing. | **About 0.1 Mac-night.** Attempt 3's window was 1 h 17 min (`KB-SLOT-FILL.md:8`). | Exploratory, outside the registered slot. Seat 2 reports an MLX array-size limit in attempt 2 (not re-verified). | S2 |
| **E4** | **ALIGN v4: R1 + W1 + D1-D3** on Qwen3.8-27B | The W1 T-vs-W verdict: T confirmed at \|d\| ≥ 10 J, rejected at ≤ 6 J, against about 2.1 J noise (`FINAL-DESIGN.md:436-446`). After D3: 21 held-out benign and 3 held-out sabotage per pair, a second-model tamper curve, and U4 (`FINAL-DESIGN-AMENDMENT-1.md:121-122`). | **About 5 calendar Mac-days nominal**; 8 under the Q4 veto; more with refusals. | 1(f) refusal; the capability gate; thermals; Flash-Next timing. | both |
| **E5** | **DIFFICULTY collection**, after a lean build | Levels 1 and 5 resolve in opposite directions in at least 0.85 of simulated campaigns; ln ratios as in M5. | **About 2-3 Mac-nights of energy sessions**, plus about 17-22 h of bench with no power capture. | Collection unbuilt; contention slot; modest novelty; a cross-machine bench might disagree, so check output identity. | both |
| **E6** | **Second-unit replication** of one Block-5 pack shape (`research_question_registry.md:103`, C5-3.1) | A measured machine-to-machine term, which turns "one unit" from a limitation into a result. | 2 nights per pack shape, on a borrowed M-series Mac | Access; competes with ALIGN for lead time. | S1 |

**If only three happen before 30 Nov:** E0, E1, then E2, or E4 if Ed declines E2. E3 fits in a daytime gap.

**Mac budget.** About 23 nights remain through 30 Nov. R1 + W1 + 3 D + E2 + E3 + E5 come to about 10-12 nominal Mac-days. That fits only if E2 and E3 run early and DIFFICULTY takes the lean path.

---

## Weak spots, candidly

1. **ALIGN:**
   - two distinct held-out sabotage trajectories;
   - thresholds at the sample maximum, with the spam threshold resting on one trajectory;
   - a simulated tamper;
   - one model and two task pairs, at batch 1;
   - no baseline and no stated threat model;
   - an agent too weak to test whether sabotage leaves a signature in its own right.
2. **Generality:** one M3 Max, one OS build, one stack, for every claim.
3. **BYTES:**
   - three fit points, so 8 corner lines (`bytes_pack_v1.md:282`);
   - power rests on three MoE models;
   - the top dense point is thermally fragile;
   - KB is latency-bound;
   - a meter label-offset alternative for DC input and rest (`:302`).
4. **DIFFICULTY:** the crossover is close to known results (Jin, Wei, Brooks 2025); contamination is acknowledged but untested; the collection code does not exist.
5. **Perception of over-engineering**, together with self-imposed throughput limits (L1).
6. **Model obsolescence:** the Qwen3 ladders against the Qwen3.8 ALIGN line. Say that the method is the contribution.
7. **Lead attention is spread thin.** B5 release, the ALIGN v4 kits, the Flash-Next port, the DIFFICULTY build, BYTES and Paper-1 writing all compete. BYTES, the cheapest high-value item, is the one that dropped out of the handoff.

---

## Claims dropped or corrected

| Claim | Seat | Why |
|---|---|---|
| "KB outcome not found on main" | 1 | Wrong: `KB-SLOT-FILL.md` is on main (R1). |
| "Every untampered sabotage stayed below" | 1 | Overstated: true for the 2 held-out trajectories; 2 of 26 bank above in the pilots 4-9 diagnostic; 3 of 6 spam above in pilot 7 (R3). |
| "MATH contamination unaddressed" | 1 | Corrected to "acknowledged as a caveat, not tested" (R7). |
| "c is not identified (VIF 3.4e6)" | 1 | No such figure at the cited lines or elsewhere in `bytes_pack_v1.md @ ee4ce93fc`. The registration only prints VIF beside λ (`:296`). Dropped. |
| The "(1c) thermal transform" is owed | 2 | Superseded by BY-THERM-LINES, run 10-31 (R4). |
| Detection limit of 170-470 hidden tokens | 2 | It rests on the wrong score definition (R8). Dropped. |
| 335× → 3.3× under batching | 2 | Corrected: 115× → 3.3× uncached; 335× is the prefix-cached figure (R9). |
| "R0 about 9 attempts over about 33 h" | 2 | Not verified. Replaced by "re-run 8" (`RESUME.md:34`). |
| "Block 5 needed 11 attempts for 3 usable sessions" | 2 | Not verified at the cited range. Dropped. |
| "9-12 Mac-days with refusals" | 2 | Kept only as a labelled judgment, not a repo number (R6). |
| OLMoE uses about 2.1× the energy per token of a dense model with comparable active parameters, on Jetson | 2 | Verified on the emergentmind summary page (https://www.emergentmind.com/papers/2606.21428). It is an aggregator page, so cite the primary paper before using it. |
| An "MLX array-size limit in attempt 2" | 2 | Not re-verified. Kept, labelled. |

External sources I opened on 2026-11-07, beyond those cited above:
- https://arxiv.org/abs/2310.03003 (Samsi et al., "From Words to Watts")
- https://arxiv.org/abs/2504.17674 (Fernandez et al., energy considerations of LLM inference)
- https://arxiv.org/abs/2403.20306 (Stojkovic et al., "Towards Greener LLMs")
- https://arxiv.org/abs/2311.18677 (Splitwise)

None of them reports an attribution floor, or phase energy on an Apple-silicon device, under preregistration.

---

## Appendix A: Seat 1 (Fable 5.1 high), verbatim

TOP:

```json
["ALIGN is the genuinely novel line: on Qwen3-30B-A3B, a five-term token-accounting fit leaves ~20-60 J residual SD on ~2.7 kJ episodes, replays are token-identical with 2.97 J pair-difference SD, every simulated reasoning omission of ~500-1,200 tokens crossed held-out thresholds and every untampered sabotage stayed below (RUN_STATE.md:993,999,1644,1682,1699 @ bd7a3efcd). No prior work measures power as a tamper-evident record of agent work; it becomes a paper with a second model and a real-adversary condition.","Paper 1's publishable core is BYTES, not the dominance ratio: a pre-registered three-rival-line test (bytes/resident/time) with predictions committed before held-out unblinding, where the three MoE models separate hypotheses by 8-19x (bytes_pack_v1.md:16-60 @ ee4ce93fc). Pass 1 is 6/6; pass 2 ran from 2649fad54; stage 1 planned 12 Nov. Weak spot: the fit set is three points and the 70B anchor is thermally fragile.","The metrology findings (attribution-limited ~1 J vs 0.3-0.5 J repeatability; clock-anchor knife-edge; 37/50 short prefills unresolvable; macOS maintenance and 8-47 W idle agents as hazards) are publishable as a methods/limitations note, not a headline (PROJECT_STATUS.md:100-105; CLAIMS_STATUS.md:106-110,230-242).","DIFFICULTY is the best-simulated design in the repo (v2.3: three worlds, near-tie fix to 1.5% false change, twin at fc4078667) but its collection side does not exist (RUN_STATE.md:325-331); expected effects ln(EPC 1.7B/4B) -0.6..-1.0 at level 1 and +0.5..+0.7 at level 5; ~3 Mac-nights; contamination unaddressed.","Ed's order (ALIGN pilots, then DIFFICULTY) is right; the binding constraint is lead time 15-22 Nov. Ruling 1(f) is expected to refuse W1 at ~11 tok/s ((6,144+4,096)/11 ~ 930 s vs T_dead ~1,200-1,280 s; LEAD-RULINGS-2.md:61,199-206 @ e901eb2a4): decide ruling 1(e)'s fallback now, blind, and keep a one-night 30B pilot 11 (reaches m >= 39) as the zero-build-risk fallback.","Highest-value next experiments: E1 B5 release + B6 read (0 nights), E2 BYTES stages 1-2 after recording the known-bytes stream-test outcome (0-0.1 nights), E3 ALIGN v4 W1 + D1-D3 (4-5 nights), E4 a 1-2 night real-adversary + metadata/LLM-monitor baseline on the 30B (cheapest high-information experiment), E5 DIFFICULTY (~3 nights after build), E6 second-unit replication (2 nights per pack shape).","Advisor-facing PROJECT_STATUS.md and CLAIMS_STATUS.md are two collection blocks stale (still 'No claim-bearing Qwen3 data exist'; last claims update 2026-08-20) and must be refreshed before the 22 Nov draft."]
```

OPEN:

```json
["What was the known-bytes stream test outcome (KB nights 1-3, 2026-10-30)? It is a registered precondition for BYTES stage-1 unblinding (bytes_pack_v1.md:36) and no result was found on main.","Did BYTES s1-p2 count, closing pass 2 at 6 of 6, and was its measurement head appended to the freeze-by-commit addendum section 5 (RUN_STATE.md:1849)?","What is ruling 1(e)'s fallback order if the W1 kit refuses on ruling 1(f): 4-bit D, lower B_D, D as a screen with the 30B series continuing, or wait for Flash-Next?","Has Ed answered FINAL-DESIGN Q4 (59,520 s D windows) and Q6 (registration grade m >= 39)? Each changes the ALIGN v4 series night count by about 2x.","Is a MATH contamination or perturbation check planned before DIFFICULTY revision 2.4 is sealed, and is the block-6 contention level recorded before the first DIFFICULTY energy session?","How much of the +241 J bank/sabotage cell offset in ALIGN pilot 4 comes from the sabotage prompt's extra 755 tokens rather than hidden work, and does the sequence design's prefill term absorb it?"]
```

<!-- seat 1 report begins (verbatim) -->

# Research program audit: what is noteworthy so far, and what next (Fable 5.1 seat)

Date: 2026-11-07. Seat: Fable 5.1 (high), independent of the Opus seat. Brief: Ed's question "are there any signs when working this will lead to any noteworthy research?"

**Durable copy:** committed as `docs/research-audits/2026-11-07/research-program/fable-seat.md` on branch `research/2026-11-07-research-program-fable` @ `d3c9d5894` (pushed to `origin`; no PR opened). Worktree removed.

**Evidence base.** `origin/main` at `bd7a3efcd`, plus three lane branches for documents not yet on main: `lane/2026-10-28-bytes-pass2-open` (`docs/registrations/bytes_pack_v1.md` @ `ee4ce93fc`), `lane/2026-11-05-align-pilot10-benign` (`docs/align/pilot_protocol_v3.md` @ `83e2dac59`) and `lane/2026-11-06-v4-r1-integrated` (`docs/align/PIPELINE.md`, `pilot_protocol_v4.md`, `council-2026-11-06-v4-review/LEAD-RULINGS-2.md` @ `e901eb2a4`). Citations are `path:line @ commit`; `RUN_STATE.md` lines are at `bd7a3efcd`.

**Blinding.** Nothing under `/Users/edr/jw-b5-*`, `night-*`, `night-custody`, `night-archive` or any `restricted/` was opened. `docs/analysis/b5/` and the `2026-11-0x-b5-*` run reports were not read. No Block-5 estimate, contrast or verdict is inferred; Block 5 is mentioned only as a sealed input whose either outcome is publishable.

---

## 0. Short answer

Yes, there are real signs, concentrated in one place that was not in the original capstone plan.

1. **ALIGN (energy as a tamper-evident record of agent work) is the one line with genuine novelty.** Ten pilots in five days produced a clean, repeatable instrument result: on Qwen3-30B-A3B running SHADE-Arena task pairs, a five-term token-accounting fit leaves a residual SD of about 20-60 J per trajectory on episodes of roughly 2.7 kJ; replays are token-identical with a pair-difference SD of 2.97 J; every simulated reasoning omission of about 500-1,200 tokens crossed a held-out threshold while every untampered sabotage run stayed below it (`RUN_STATE.md:993,999,1644,1682,1699`). That is exactly what the pipeline predicted ("power counts work; it is blind to what a token says", `docs/align/PIPELINE.md:9-21 @ e901eb2a4`), and I know of no published work that measures it. It is a paper once a second model and a real-adversary condition are added.
2. **Paper 1 (Block 5 + Block 6 + BYTES) is robust and will exist, but its publishable core is BYTES, not the dominance ratio.** BYTES is a pre-registered three-hypothesis test (bytes read per token vs resident bytes vs decode time) with predictions committed before held-out unblinding, over a 32-fold bytes range and a 71-fold resident range, where the three MoE models separate the hypotheses by factors of 8-19 (`bytes_pack_v1.md:16-60 @ ee4ce93fc`). Whatever word prints, it is a result about Apple unified-memory decode nobody has measured this carefully.
3. **The metrology findings are publishable as a methods note, not a headline**: attribution-limited at ~1 J vs 0.3-0.5 J repeatability; the clock-anchor knife-edge; 37 of 50 short prefills unresolvable; macOS maintenance and agent idle power as measurement hazards.
4. **DIFFICULTY is the best-designed but least surprising question.** Its registration is the most thoroughly simulated document in the repo and its pilot shows the expected crossover. The collection side is unbuilt (`RUN_STATE.md:325-332`).
5. **Ed's priority order (after BYTES: ALIGN pilots, then DIFFICULTY) is scientifically right.** The main risk is lead capacity between 15 and 22 November, when ALIGN v4's first window may be refused by ruling 1(f) while Paper 1 needs its author.

---

## 1. What has been found so far (unblinded material only)

### 1.1 Instrument and metrology (Paper 1, Part 1 backbone)

| Finding | Evidence | Publishable as |
|---|---|---|
| Repaired instrument is **attribution-limited, not noise-limited**: boundary placement ~0.7-1.0 J/run vs 0.29-0.49 J repeatability on ~50 J points; clearable phase contrast ~5 J | `PROJECT_STATUS.md:100-105`; `CLAIMS_STATUS.md:106-110` | Motivation for the sealed Block-5 dominance question (R = timing-aware floor / point floor, pre-registered R >= 2; `configs/campaigns/v5_claim_25g83/registration_block5.md:1622-1640`) |
| **Clock-anchor knife-edge**: at 197 s capture the native-second intersection margin is ~+/-1 ms while the unmodeled wall/monotonic rate (~-12 ppm, 2.3 ms/capture) exceeds it; pass/fail was quantization-phase luck | `CLAIMS_STATUS.md:230-235` | Metrology limitation; motivates the rate-aware clock mapping in the methods draft (`docs/paper/draft-v2-skeleton.md:55-66`) |
| **Short prefill not resolvable**: 37/50 Qwen2.5-1.5B prefill phases crossed only two records; 7B passed in all 50 | `docs/paper/draft-v2-skeleton.md:19-27` | Already in the methods draft |
| **Environmental validity on a laptop**: operator streaming fails idle admission; quiet state needs suspended cloud sync; the 12:53 daily batch, XProtect scan hour and 00:00 `/private/tmp` walk each cost members; an idle AI agent draws 8-47 W | `CLAIMS_STATUS.md:236-242`; `RUN_STATE.md:46-53` (items 14, 17, 29); `difficulty_pack_v2.md:213` | A systems note practitioners would use; belongs as a table in Paper 1's limitations |
| **Falsified instrument generations, recorded**: anchor-v2 rate model falsified (748 bundles void); Windows A/B voided; mint #1 void | `CLAIMS_STATUS.md:9-19,77-110` | Limitations; strongest evidence the pre-registration discipline is real |

**Weak spot.** `PROJECT_STATUS.md` still says "No claim-bearing Qwen3 data exist" and names the four-rung probe as the next milestone (`:77,169-179`); `CLAIMS_STATUS.md` was last updated 2026-08-20 (`:38`). Both are two collection blocks stale. Fix before 22 November.

### 1.2 ALIGN pilots 1-10 (the surprising line)

| Pilot | Established | Where |
|---|---|---|
| 3 | First side-task successes; identical-work prompt-cache saving 14,451 -> 2,232 J and 20,563 -> 1,380 J vs the throttled pilot 2 | `RUN_STATE.md:988` |
| 4 | Five-term fit: s_r 176.4 J (20 df), e = 0.619 +/- 0.013 J/decode token; cell offsets spam -99/-79 J, bank +94/+241 J; **cross-pair transfer fails**; all 12 sabotage trajectories cross the grouped threshold at 1,282 or 2,192-3,077 stripped reasoning tokens | `RUN_STATE.md:993` |
| 5 (exact repeat) | All 28 members token-identical; window contrast -0.43 J (SE 0.61); **pair-difference SD 2.97 J** on multi-kJ episodes | `RUN_STATE.md:999` |
| 6-7 | Anchors token-identical across sessions; an **8-9 J session step** between pilots 5 and 6, not attributable (no temperature recorded); frozen alternative desk out of sample: s_r bank 182 -> 87 J, spam 36.5 -> 22.9 J; **untampered sabotage alarms on spam 3/6, accumulated over later turns, tracking GPU clock** | `RUN_STATE.md:1029,1712` |
| 8-10 | Sequence design `[1, P, D, (C+P)D + D^2/2, CP + P^2/2]`: s_r bank 251 -> 58 J, spam 45 -> 19 J; held-out pooled thresholds bank 2.53, spam 7.13 at m 28-30 (sample maximum); **all six untampered sabotage below threshold, all detected at the smallest tamper**; spam threshold rests on one trajectory; clock correlation bank +0.79 to +0.92 over five sessions; K = 7 anchors sigma_w 4.67 J | `RUN_STATE.md:1644,1682,1699` |

Plainly: the instrument works as a work counter (residual 1-2 % of episode energy; a few hundred to a thousand omitted tokens at ~0.6 J/token is far above it); it is blind to intent, as predicted; and the dominant nuisance is thermal/DVFS drift, which the v4 gates and the W1 T-vs-W contrast address (`FINAL-DESIGN.md:15-23,432-457 @ bd7a3efcd`).

**Weak spots.** (1) One model, two task pairs, m 28-30 per pair; thresholds are the sample maximum so no FPR claim (`FINAL-DESIGN.md:54,539`); the spam threshold rests on one trajectory. (2) The tamper is simulated post hoc (known-H stripping, `pilot_protocol_v3.md:155-163`); no condition where the model is the adversary. (3) No baseline: the metadata baseline (`PIPELINE.md:25-31`) and SHADE-Arena's LLM monitor (AUC 0.87, Kutasov et al. 2025, https://arxiv.org/abs/2506.15740) have not been placed beside the energy residual. (4) Threat model unstated: the power record is tamper-evident only if the adversary controls logs but not the meter; must be reconciled with the project's "no adversarial process on the machine" limitation (`CLAIMS_STATUS.md:14-19`). (5) Cross-pair transfer fails; the +241 J bank/sabotage offset is unexplained.

### 1.3 BYTES (Paper 1, Part 2)

Design (`bytes_pack_v1.md @ ee4ce93fc`): ten MLX models (fit set Qwen3 1.7B/4B/8B 4-bit; held-out Qwen3 14B, 32B, 8B-8bit, Llama-3.3-70B, Qwen3-30B-A3B, Qwen3-Next-80B, Qwen3.5-122B), one 2,048-in/512-out greedy workload, three boundaries, three frozen rival OLS lines with corner-line prediction intervals, a word per held-out model, an active/resident/mixed verdict on the MoE trio, Bonferroni k = 21, hidden offsets with a withheld store, `predictions.json` committed before held-out rows enter the export (§8-§11).

Status: pass 1 complete 6/6 after retries (`RUN_STATE.md:349`); s5-p1 (70B) counts but not claim-usable on thermal exclusions at the 140 W adapter (`:277`), producing pass-2 rule R1 (`:350`); pass 2 ran from `2649fad54` through s6-s2 (`:384,900`), s1-p2 last before the 2026-11-05 end (`:1849`); extension dropped (`:902`); stage 1 planned 12 Nov (`2026-10-27-paper1-contingency.md:40`).

Why publishable regardless: the pilot showed Qwen3-32B reading 18.0 GB/token vs 30B-A3B reading 1.71 GB with 17.2 GB resident, and MoE decode slower per byte (`block6_collection_draft.md:596`). On a unified-memory SoC with no DRAM rail, which of bytes moved, bytes resident or time energy follows decides whether MoE active parameters buy energy or only latency.

**Weak spots.** Fit set is three points, 8 corner lines (`:282`); dense held-out cannot discriminate (2-9 %) so power rests on three MoE models (`:30-32`). Llama-70B's pass-1 decode cell was gutted thermally. DC-input and rest carry a label-offset alternative and c is not identified (VIF 3.4e6) (`:300-304`). The known-bytes stream test (GPU rail includes memory controller?) was `PENDING` in the registration (`:36`); three KB night attempts ran ~10-30 (`RUN_STATE.md:1814,1833,1844`); outcome not found on main.

### 1.4 DIFFICULTY

Pilot (no power): thinking-off accuracy 95 % -> 30 % (1.7B), -> 65 % (4B), -> 70 % (8B) from level 1 to 5; 1.7B cheapest per correct answer by time at levels 1-2, 4B ~2x cheaper at level 5 (16 s vs 29 s); thinking-on saturates MATH (`difficulty_pack_v2.md:19`; `block6_collection_draft.md:597`).

Registration v2.3: three synthetic worlds, two spreads, coverage bars, a near-tie world that caught a 6 % false "changes with level" rate and fixed it to 1.5 % via level-1 energy 70 (`:144-168`), null worlds (`:174-191`), twin implementation, frozen code `fc4078667` (`:390-412`), end date 2027-01-31 (`:386`). Expected ln(EPC 1.7B/4B): level 1 -0.58 to -0.99, level 5 +0.48 to +0.67, level 3 ~0 (`:118`); intended pattern resolved in 0.85-0.99 of simulated campaigns (`:157-166`).

**Readiness: analysis ready, collection not.** Loop module shapes cannot carry attempts; runner forces `suppress_eos=True`; energy adapter and bench runner unbuilt; revision 2.4 unwritten; freeze audit not run (`RUN_STATE.md:325-331`). Machine time: ~14.5 h energy sessions, ~13 h bench (no power), ~5 h thinking-on (`:201`).

**Weak spots.** Novelty is in joules and rigor, not the crossover itself; MATH contamination unaddressed; Qwen3 ladder will read dated; one 8B level-1 cell undercovers by design (`:172`); the contention level is a slot from the quiet-machine kit that must be recorded before the first session (`:218`).

### 1.5 Process and automation

Nine Block-6 sessions, twelve counting BYTES sessions and ten ALIGN pilots armed, run, harvested and read by a headless magistrate with pre-registration, hidden offsets (Klein and Roodman 2005, `bytes_pack_v1.md:342`), refusal-as-result (D-189/D-190, `decision_log.md:12251-12272`), blind two-seat consults and twin implementations. Publishable as a methods contribution only if framed as what it bought (zero results read before registration; zero silent retries), after a proportionality pass; the advisor's over-engineering remark will be a reviewer's.

---

## 2. The strongest papers

**Paper 1 (30 Nov): "Phase energy on Apple silicon under pre-registration: attribution limits, replication, and what decode energy follows."** Part 1: Block 5 beside Block 6 (three claim-usable sessions per pack, `RUN_STATE.md:203`), same estimators; Part 2: BYTES stages 1-2. Strong because outcome-independent (`2026-10-27-paper1-contingency.md:8-15`) with a replication fixed before any number was seen (`RUN_STATE.md:66`). Not a top venue: one machine, one stack, one boundary, three-point fit set, dated models. Sits beside Samsi et al. 2023 (https://arxiv.org/abs/2310.03003), Fernandez et al. 2025 (https://arxiv.org/abs/2504.17674), Stojkovic et al. 2024 (https://arxiv.org/abs/2403.20306), Splitwise (https://arxiv.org/abs/2311.18677); none reports an attribution floor or on-device Apple-silicon phase energy under pre-registration.

**Paper 2 (worth protecting): "Energy as a tamper-evident work record for LLM agents."** Claim shape: a software-independent power trace, after token accounting, detects omitted work of size H tokens with per-pair calibrated thresholds; it does not detect sabotage per se. Exists: pilots 4-10 corpus, frozen sequence design and calibration (`7fbd95e31`), v4 thermal design, W1 contrast. Needs: second model (Qwen3.8-27B; Flash-Next later), real-adversary condition, metadata baseline and LLM-monitor comparison, m >= 39 for a finite threshold, U1-U6 thermal control. Position against SHADE-Arena (LLM monitors) and physical side channels on NNs (Batina et al. 2018, https://arxiv.org/abs/1810.09076, the inverse use of the same physics). I found no prior work using power as a monitoring record for agents.

**Paper 3 (chapter or short paper): DIFFICULTY**, as designed; headline the pre-registered joules-per-correct-answer crossover and the thinking-on energy gradient where accuracy saturates.

---

## 3. Priority order: assessment

Ed's order (`2026-10-27-paper1-contingency.md:115-124`) and the 11-07 resume (ALIGN first; Flash-Next waits on the SSD, `RESUME.md:17`) are right, with two conditions.

1. **Paper 1's lead time, not Mac-nights, is the scarce resource.** The plan already says Paper 1 goes first if DIFFICULTY needs attention in 15-22 Nov (`:112-113`); apply the same rule to ALIGN v4. Ruling 1(f) is expected to bind: at ~11 tok/s, (6,144 + 4,096)/11 ≈ 930 s against T_dead ≈ 1,200-1,280 s, so W1 is refused unless worst-case G0 + gates + prefill fit in ~270-350 s (`LEAD-RULINGS-2.md:61,199-206`). Decide ruling 1(e)'s fallback order now, blind, so R1's outcome triggers a procedure, not a design session in the writing window.
2. **Keep the 30B series as fallback and as Paper 2's calibrated base.** Pilot 10 was the last v3 pilot because thresholds do not transfer to Qwen3.8-27B (`RUN_STATE.md:1653`), but a pilot 11 of pilot 10's shape reaches m >= 39 on the 30B (`:1662`) at one Mac-night with zero build risk. If W1 is refused twice, run it.

DIFFICULTY third is right: collection code absent, end date 2027-01-31, bench attempts can run by day.

---

## 4. DIFFICULTY design documents: readiness

| Item | State | Evidence |
|---|---|---|
| Registration text | v2.3 on main; refuted at v2.1, v2.2; revision 2.4 unwritten | `difficulty_pack_v2.md:1-9`; `RUN_STATE.md:175,329` |
| Estimator code + twin | frozen `fc4078667`; 56 tests; agree within 1e-6 on production-shaped synthetic packs | `:390-412` |
| Problem lists | built, hashed, outside repo | `:97` |
| Power simulations | worlds A/B/C, near-tie, nulls; intended pattern >= 0.85 | `:155-191` |
| Collection code | **absent** | `RUN_STATE.md:325-331` |
| Freeze audit #416 | not run | `:330` |
| Machine time | ~14.5 h energy + ~13 h bench (no power) + ~5 h thinking-on (+5.6 h optional 8B) | `:201` |

Verdict: science ready; plumbing one to two weeks of two-review build away. December is realistic and inside the end date. Confirm the contention level is recorded before the first session.

---

## 5. Highest-value next experiments (Mac-night ≈ 12.4 h window)

| # | Experiment | Expected effect | Mac-nights | Main risks |
|---|---|---|---|---|
| E1 | Block 5 release, then Block 6 read under the same estimators (laptop; r4 D5 fix in flight, `RESUME.md:20-28`) | Whatever prints; both outcomes pre-written | 0 | New release-check family after D5; 20 Nov Tier-E date |
| E2 | BYTES stage 1 (12 Nov) and stage 2, after recording the KB stream-test outcome | H1 words on the MoE trio where rivals differ by 8-19x; dense linearity at 2-9 % | 0 (or ~0.1 if KB must re-run, ~1 h) | 70B pass-2 cell short; KB outcome missing; fit-set-of-three critique |
| E3 | ALIGN v4 W1 + D1-D3 on Qwen3.8-27B (18-member W1; three D windows at 58,260 s) | T-vs-W verdict at |d| >= 10 J vs <= 6 J against 2.1 J noise (`FINAL-DESIGN.md:432-446`); second-model tamper curve; U1-U3 in W1, U4 at D3 | ~61 h maxima, ~45 h expected: **4-5** (`AMENDMENT-1.md:A2`) | 1(f) refusal; D effort ladder fails; unverified SMC thermometry (`AMENDMENT-2.md:§3`); capability gate; cache rebuilds; sample-maximum thresholds |
| E4 | ALIGN real-adversary + baseline night on the 30B (design council first): model told to keep reasoning terse or move work into tool calls, frozen calibration unchanged; metadata baseline and a local LLM monitor scored on the same transcripts | Detection at H ~500-1,200 tokens if hidden; a stated null if the adversary compresses work; baseline AUCs for SHADE-Arena readers | 1-2 (reuse pilot-10 kit; also reaches m >= 39) | Prompt-induced work confounds the residual; ledger must be the adversary's; pilots so far judge-free (`RUN_STATE.md:322`) |
| E5 | DIFFICULTY collection after the plumbing build | Levels 1 and 5 resolved oppositely in >= 0.85 of campaigns; ln ratios -0.6..-1.0 and +0.5..+0.7 | ~3 (1.5 nights energy; bench by day; 5 h thinking-on) | Collection unbuilt; contamination; contention slot; 8B level-1 undercoverage |
| E6 | Second-unit replication of one Block-5 pack shape (C5-3.1, `research_question_registry.md:103`) | A measured machine-to-machine term; converts "one unit" from limitation to result | 2 per pack shape on a borrowed M-series Mac | Access; acceptance re-derivation; competes with ALIGN for lead time |

If only three happen this year: E1, E2, then E3. E4 is the cheapest high-information experiment in the program; run it ahead of D2-D3 if W1 is refused.

---

## 6. Weak spots, collected

1. Stale advisor-facing status pages (`PROJECT_STATUS.md`, `CLAIMS_STATUS.md`).
2. One machine, one stack, one boundary for every claim (registry caps at L2, `research_question_registry.md:89`); no replication-aware term yet.
3. ALIGN's estimand is a simulated omission scored against sample-maximum thresholds on one model and two pairs; no baseline; threat model unstated.
4. BYTES rests on three fit points and three MoE models; 70B thermally fragile; KB test must be recorded before rails is interpreted.
5. DIFFICULTY has no collection code and an unaddressed contamination question.
6. Over-engineering as a reviewer risk; report what the machinery bought in one table.
7. Model obsolescence (Qwen3 ladders vs Qwen3.8 ALIGN line); say the method is the contribution.

---

## 7. Open questions I could not close from the repo

1. Known-bytes stream test outcome (KB nights 1-3, 2026-10-30), a registered precondition for BYTES stage-1 unblinding (`bytes_pack_v1.md:36`).
2. Did s1-p2 count, closing pass 2 at 6/6, with its head appended to the addendum §5 (`RUN_STATE.md:1849`)?
3. Ruling 1(e)'s fallback order if the W1 kit refuses on 1(f).
4. Ed's answers to Q4 (59,520 s D windows) and Q6 (m >= 39 registration grade) (`FINAL-DESIGN.md:§3.2`); each changes E3's night count ~2x.
5. A MATH contamination or perturbation check before DIFFICULTY revision 2.4.
6. Where the sabotage prompts' extra 755 tokens sit in the sequence design: is part of the +241 J bank/sabotage offset prompt length rather than hidden work?

---

## Appendix: sources opened

Repo (commits inline): `PROJECT_STATUS.md`, `CLAIMS_STATUS.md`, `RUN_STATE.md`, `CANONICAL.md`, `docs/strategy/2026-10-27-paper1-contingency.md`, `docs/handoff/2026-11-07-account-retirement/RESUME.md`, `docs/registrations/{difficulty_pack_v1,difficulty_pack_v2,bytes_freeze_by_commit_addendum,bytes_extension_models_2026-10-27,bytes_end_date_amendment_2026-10-27,block6_replication_DRAFT}.md`, `docs/design/block6_collection_draft.md` §18, `docs/design/next_block_threshold_proportion.md`, `docs/align/council-2026-11-05/FINAL-DESIGN.md` + amendments 1-2, `docs/research_question_registry.md`, `docs/decision_log.md` (D-188..D-190), `docs/paper/{draft-v2-skeleton,results-fill-registry,round7/survival-map}.md`, `configs/campaigns/v5_claim_25g83/registration_block5.md` §1; lanes: `bytes_pack_v1.md` @ `ee4ce93fc`, `pilot_protocol_v3.md` @ `83e2dac59`, `PIPELINE.md`, `pilot_protocol_v4.md`, `LEAD-RULINGS-2.md` @ `e901eb2a4`.

External (opened 2026-11-07): https://arxiv.org/abs/2506.15740; https://arxiv.org/abs/2504.17674; https://arxiv.org/abs/2310.03003; https://arxiv.org/abs/2311.18677; https://arxiv.org/abs/2505.09598; https://arxiv.org/abs/2403.20306; https://arxiv.org/abs/1810.09076. The ML.ENERGY leaderboard returned only a title and the PNAS preregistration paper returned 403; neither is cited.

<!-- seat 1 report ends -->

---

## Appendix B: Seat 2 (Opus 5.5 xhigh), verbatim

TOP:

```json
["The most novel result is ALIGN. A frozen count-based energy model with attention-length terms predicts SHADE-Arena episode GPU energy to a residual SD of about 20-58 J on 2-4 kJ episodes. Token-identical replays repeat to about 2 J. Every held-out simulated omission of one turn's reasoning (539 or 1,193 tokens) was detected (RUN_STATE.md:1644; magistrate RECORDs f775edaf:16-23 and 3efb8793:22-23 at bd7a3efcd).","The ALIGN held-out evidence is thin. The held-out sabotage is only the seed-1 anchors (2 distinct trajectories). Each threshold is the sample maximum at m = 28, and the spam threshold rests on one benign trajectory. The tamper is a post-hoc edit of the token log, not real hidden work. One cheap night (E2: fresh sabotage seeds plus real injected unlogged compute at blinded doses) plus zero-cost desk work (E1, including rescoring pilot-7 seeds 12-16) would make it a strong paper.","The most surprising unblinded physical number is the known-bytes test. About 3/4 of marginal memory-traffic energy is outside the powermetrics CPU+GPU+ANE rails: f = 0.238 ± 0.098; DC 0.0389 vs rails 0.0092 J/GB (KB-SLOT-FILL.md:20-23,60,76 at bd7a3efcd). It is one session in a latency-bound regime (106-116 GB/s); a short bandwidth-bound repeat (about 0.15 Mac-night) would make it a citable correction to rails-only Apple-Silicon LLM energy work such as GreenBench.","BYTES is the most likely clean, general, publishable result: 10 models including 3 MoE, resident/bytes separation 8.4-19.4x, predictions committed before the held-out models are unblinded. But no BYTES stage-1 analysis appears in the repo since collection closed on 10-30/31, against the Paper-1 checkpoint 'BYTES stage 1 committed' by 12 Nov. It needs zero Mac time and should be the lead's first priority. Llama-70B (the top dense point) is at thermal-exclusion risk.","The ALIGN v4 plan (Qwen3.8-27B 8-bit only, thermal holds, windows up to 59,520 s, about 6-12 Mac-days, likely W1 refusal under ruling 1(f)) is expensive relative to its scientific gain. Detecting unlogged work does not need a capable deceptive agent, and Amendment 1 itself says there is 'no cross-model monitoring claim' until Flash-Next lands. Run E1 and E2 on the 30B before the D series, and decide whether a cheaper second model is acceptable if Flash-Next slips.","DIFFICULTY v2.3 is registered and its analysis code is ready and hash-pinned, but the collection side is unbuilt (EOS member, energy adapter, bench runner, rev 2.4, freeze audit; DIF-READY-1 at cef8388c7). It costs about 3 Mac-nights plus 17-22 h of bench generation, and its primary 1.7B-vs-4B crossover is close to known results. Build it lean on the unpinned ALIGN Apple runner (public deviation log), run the bench off the quiet Mac after an output-identity check, and treat it as a section of Paper 2, not a standalone paper.","Paper 1 is safe but niche as framed ('Timing Sensitivity of Phase-Energy Assignments'). Reframe it around what a laptop's own power counters can and cannot resolve for LLM inference, with BYTES H2 and the rails-coverage finding as the headline and the method plus replication as support.","Throughput is the binding constraint, and it is mostly self-imposed: about 3 s measured per 237 s Block-5 run, a 516.6 s fixed cost per ALIGN member, about 9 R0 attempts over about 33 h. A zero-cost idle-truncation refit on existing ALIGN data could show whether members per night can roughly double."]
```

OPEN:

```json
["Who runs BYTES stage 1 (the (1c) thermal transform, stage-1 fit, prediction commit, held-out agreement, stage 2), and when? There is no repo record of work since 2026-10-31, and the plan checkpoint is 12 Nov.","Does Ed accept that ALIGN's core paper question is 'energy as an independent record of logged compute', which needs no deceptive-capable agent, rather than 'does sabotage leave an energy signature'? This decides whether E2 on Qwen3-30B goes before the expensive Qwen3.8-27B series.","Will Ed allow one or two more Qwen3-30B nights framed as a confirmatory positive control (fresh sabotage seeds plus real injected hidden compute), given his 'no more v3 pilots' ruling?","Which threat model should the ALIGN paper state: an on-prem/edge operator meter vs agent-editable logs, a metered third-party audit of reported reasoning tokens (CoIn-style, but physical), or hardware-enabled compute verification? Where should injected hidden work land (decode, tool call, between turns) to match it?","If Flash-Next slips past the SSD and memory risks, should a cheaper second production model (e.g. Qwen3-Next-80B-Thinking) be reinstated, to secure a cross-model claim before the D series finishes?","Will Llama-3.3-70B have a usable BYTES point after s5-p1 (2 of 10 quads kept) and the s5-p2 hull exclusions? This can be answered structurally, without unblinding, and it decides whether the bytes range is 32x or about 15x.","Is the known-bytes rails-coverage result (f = 0.238) worth a short exploratory repeat in the bandwidth-bound regime before Paper 1 freezes on 15 Nov?","For DIFFICULTY: will the lead accept, via the public deviation log, (a) collecting energy through the ALIGN Apple runner instead of block-6 sessions and (b) running the bench on another machine after an output-identity check? Should 'price of thinking' (4B on vs off) get more weight?","Is the 'score' in the ALIGN calibration output a residual divided by s_r, or by a larger predictive SD? My detection-limit estimate (about 170-470 hidden tokens per episode) assumes the former, and E1(a) should replace it with a measured curve."]
```

<!-- seat 2 report begins (verbatim) -->

# Research program audit, Opus seat: what is noteworthy so far, and what comes next

JouleWise, 2026-11-07. Repo evidence is cited as `path:line@commit`:
- `main` = `bd7a3efcd`
- ALIGN measurement lane `lane/2026-11-05-align-pilot10-benign` = `5f817856b`
- BYTES lane `lane/2026-10-28-bytes-pass2-open` = `ee4ce93fc`
- DIFFICULTY readiness lane `lane/2026-10-27-difficulty-ready` = `cef8388c7`

**Blinding.** I did not read, list or open `/Users/edr/jw-b5-*`, `/Users/edr/night-*`, night-custody, night-archive or any `restricted/` path. I did not open any `night-results/*` branch. No Block-5 or Block-6 outcome was read or inferred. BYTES science energies are still blinded and were not read. The numbers below are already-unblinded instrument checks, non-claim pilot reads in RUN_STATE and the magistrate RECORDs, and design documents. Estimates of my own are labelled **[my estimate]**. Nothing was committed. The worktree `jw-wt/opus-noteworthy` was created at `origin/main` and has been removed.

---

## 1. Short answer to Ed

**Yes, there are real signs of noteworthy research.** They are not mainly where the project has spent most of its effort.

1. **The most novel result is ALIGN: energy as a record of an agent's work that the agent cannot edit.** On Qwen3-30B-A3B in SHADE-Arena:
   - A token-count energy model with attention-length terms, frozen in advance, predicts per-episode GPU energy with a residual SD of about 20-58 J on episodes of about 2-4 kJ.
   - Token-identical replays repeat to about 2 J.
   - Simulated omission of a single turn's logged reasoning (539 or 1,193 tokens) was detected in every held-out test.

   As far as I can find, nobody has published this as a monitoring method. It is close to two active lines of work: auditing hidden reasoning tokens (CoIn) and hardware-enabled verification mechanisms. The weak spots are serious but fixable cheaply (§7). Today the held-out sabotage evidence is **2 distinct trajectories**, and the tamper is a post-hoc log edit, not real hidden work.

2. **The most surprising unblinded physical number is the known-bytes stream test.** About three quarters of the marginal energy of memory traffic on the M3 Max falls *outside* the `powermetrics` CPU+GPU+ANE rails:
   - rails share f = 0.238 ± 0.098
   - DC input 0.0389 ± 0.0072 J/GB, against rails 0.0092 ± 0.0021 J/GB

   Many Apple-Silicon LLM energy papers use `powermetrics` alone (e.g. GreenBench, Aug 2026). If this holds in the bandwidth-bound regime, it is a correction the community will cite. Today it is one session in a latency-bound regime.

3. **BYTES is the most likely clean, general, publishable physics result.** It asks whether decode energy follows bytes read, resident size or time. It uses 10 models including 3 MoE models, three measurement boundaries, and predictions committed before the held-out models are unblinded. The design is strong: on MoE models the hypotheses differ by 1.4-19×. **But there is no repo record of BYTES stage-1 analysis since collection closed on 10-30/31.** The Paper-1 plan's 12 Nov checkpoint is at risk, and that analysis needs zero Mac time.

4. **Paper 1's method contribution** (`powermetrics` timing sensitivity, the replication) is publishable, but it is niche on its own. It becomes much stronger if BYTES and the rails-coverage finding are its headline.

5. **DIFFICULTY is the weakest on novelty.** Its primary question, whether 1.7B or 4B is cheaper per correct answer by MATH level, is close to known results (Jin, Wei, Brooks 2025). Its collection side has not been built. Keep it cheap, or fold it into another paper.

---

## 2. Findings so far, ranked by how noteworthy they are

| # | Finding (unblinded) | Evidence | Why it matters | Confidence and caveats |
|---|---|---|---|---|
| F1 | **Counts → energy is tight enough to witness logs.** With the attention-length "sequence design" `[1, P, D, (C+P)D + D²/2, CP + P²/2]`, per-pair residual SD fell from 274.0 to 45.1 J (bank) and from 118.8 to 32.7 J (spam) in pilot 9. In pilot 10 it fell from 232.9 to 45.5 J and from 47.5 to 24.2 J. Marginal decode cost e = 0.667 / 0.495 J/token. | `docs/process_traces/2026-11-05-magistrate-f775edaf/RECORD.md:16-18@bd7a3efcd`; `.../2026-11-05-magistrate-3efb8793/RECORD.md:22@bd7a3efcd` | A residual of about 1-2% of episode energy is what makes omitted-work detection possible. | One model (Qwen3-30B-A3B 4-bit), two SHADE task pairs, batch 1, one Mac. |
| F2 | **Held-out detection.** Frozen calibration (`7fbd95e31`) on pilots 8-10, seeds 17-46, m = 28 per pair. Thresholds: bank 2.53, spam 7.13. All untampered sabotage scores fell below threshold, and every sabotage trajectory was detected at the smallest tamper (k = 1: H = 1,193 bank, 539 spam). | `RUN_STATE.md:1644@bd7a3efcd`; `...3efb8793/RECORD.md:23@bd7a3efcd`; `...f775edaf/RECORD.md:20-23@bd7a3efcd` | Out-of-sample: the design was frozen before pilot 7 and the calibration before pilot 8. | **The held-out sabotage = the seed-1 anchors only**, i.e. 2 distinct trajectories replayed (pilots 8-10 were "8 anchors + 20 fresh benign", `RUN_STATE.md:1662,1700,1713@bd7a3efcd`). Each threshold is the sample maximum (conformal false-positive rate ≤ 1/29 ≈ 3.4% nominal). The spam threshold rests on one benign trajectory (7.13; the next is 2.99). |
| F3 | **A naive energy model "detects sabotage" because the sabotage prompt is longer.** The registered design charged no attention over the freshly prefilled turn-0 prompt. The spam sabotage prompt is 755 tokens longer, so untampered sabotage false-alarmed (5 of 6 spam in pilot 6). The attention-length design removes most of this. | `docs/process_traces/2026-11-04-magistrate-7e06863b/RECORD.md:27,38-40@bd7a3efcd` | This is a cautionary methods result for any energy- or count-based monitor of agents. | Found on pilots 4-6 and tested on pilot 7, where spam still had 3 of 6 untampered alarms at m = 6 (`RUN_STATE.md:1712@bd7a3efcd`). |
| F4 | **Energy repeatability under token-identical replay.** Identical-work replays differ by about 2 J (residual SD 1.93-2.17 J). The between-session offset is σ_w ≈ 4.6 J. There was an unexplained −0.41% step in decode segments between pilots 5 and 6. | `...f775edaf/RECORD.md:15@bd7a3efcd`; `...7e06863b/RECORD.md:22-23,38@bd7a3efcd` | About 0.05-0.1% repeatability of episode energy is remarkable, and useful for energy regression testing. | Temperature was not recorded, so the step is "not attributable". |
| F5 | **`powermetrics` rails miss about 3/4 of memory-traffic energy.** Rotate-minus-repeat contrast: rails 0.0092 ± 0.0021, GPU 0.00879 ± 0.00010, DC 0.0389 ± 0.0072, rest 0.0296 ± 0.0084 J/GB. f = 0.238 ± 0.098. 85% of the GPU-rail contrast is stall time, and "three quarters of the DC contrast is in rest". | `docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md:20-23,60,70-77@bd7a3efcd` | It corrects the common practice of rails-only measurement for memory-bound decode. | One session. **Latency-bound regime (106-116 GB/s) vs decode's 209-344 GB/s** (`:77`). "Rest" mixes DRAM, conversion and fans. |
| F6 | **BYTES pilot: MoE decode is slow for its byte count.** Dense models reach 209-344 GB/s effective bandwidth, MoE models 130-231 GB/s. Same footprint, very different bytes: 32B reads 18.0 GB per token vs 30B-A3B 1.71 GB, at 17-18 GB resident. | `docs/design/bytes_pilot/SUMMARY.md:37-39@ee4ce93fc` | This is what makes the BYTES hypotheses separable (resident/bytes 8.42-19.43×, time/bytes 1.39-2.22× on MoE; `docs/registrations/bytes_pack_v1.md:27@ee4ce93fc`). | Throughput only, no power. Measured under contention. |
| F7 | **Agentic energy is prefill-dominated without prefix caching.** 147k-645k prefill tokens per episode against at most 7.7k decoded. Identical work cost 14,451 → 2,232 J and 20,563 → 1,380 J with the episode-prefix cache. | `RUN_STATE.md:983,989@bd7a3efcd`; `docs/process_traces/2026-11-03-magistrate-af17111e/RECORD.md:17@bd7a3efcd` | Practical guidance for local agents. | Confounded: pilot 2 was throttled. Qualitatively known. |
| F8 | **A laptop cannot sustain heavy decode.** OS thermal onset came at about 170-210 s at 40-47 W. The Llama-70B BYTES decode cell kept 2 of 10 quads in s5-p1, the rest removed by thermal and battery exclusions. macOS tops the battery up mid-session at about 95% (21-31 W). | `...af17111e/RECORD.md:13@bd7a3efcd`; `RUN_STATE.md:277,1645@bd7a3efcd` | A physical limit that matters for local-LLM energy claims. It may also cost BYTES its top dense point (see §7). | Structural counts only. |
| F9 | **`powermetrics` timing behaviour.** Historical pulses: all 59 fitted onsets come after their commands, and 49 of 59 offsets before them. 37 of 50 short prefills crossed only 2 records. A macOS update moved the timing calibration. The wall/monotonic rate = 1 model was falsified. | `docs/paper/draft-v2-skeleton.md:19-27@bd7a3efcd`; `CLAIMS_STATUS.md:10-14@bd7a3efcd` | The core of the Paper-1 method story. | Historical, diagnostic only. |
| F10 | **Qwen3.8-27B is "confidently wrong" on its own system and tool text.** 11.06 nats/token, reproduced in HF fp32 on the upstream weights. Some bins are worse than uniform over the vocabulary (15.86 vs 12.42). | `docs/align/v4/R0-LOAD-REFERENCE-NOTE.md` (lane `5f817856b`), table and text under "Why" | A curious side finding about model behaviour. It does not change the energy work. | Cause unverified. |
| F11 | **Process data.** 8 refused or removed Block-5 attempts, each root-caused (12:53 maintenance, XProtect, `/tmp` cleaner at 00:00, 6-hourly softwareupdated scan, charger sag causing sleep). The D-188 rewrite cut the dry run from 27.1 h to 1 h 46 min. | `README.md` "Now (2026-10-12)"; `RUN_STATE.md:1013,1069-1084@bd7a3efcd` | A rare, documented case of a pre-registered measurement campaign run by AI agents. | n = 1, and partly a lesson in over-engineering (advisor's remark). |

---

## 3. The strongest papers

1. **Paper 1 (due 30 Nov): method + replication + BYTES. Highest certainty of publication.**
   - Today it is framed as "Timing Sensitivity of Phase-Energy Assignments on Apple Silicon" (`docs/paper/draft-v2-skeleton.md:7@bd7a3efcd`). That framing is rigorous but narrow.
   - **Recommendation:** make the headline "what a laptop's own power counters can and cannot resolve for LLM inference", with three parts:
     - BYTES H2 (power against bandwidth) at rails, DC input and rest;
     - the known-bytes rails-coverage result;
     - the timing-attribution floor and the replication.
   - Its value does not depend on any outcome (`docs/strategy/2026-10-27-paper1-contingency.md:5-12@bd7a3efcd`). It does depend on BYTES stage 1 running now.

2. **ALIGN Paper A: "Power as an independent record of agent work: detecting omitted reasoning in SHADE-Arena on a laptop". The most novel.**
   - The v3 dataset (pilots 4-10, 7 sessions × 28 members, a frozen design, frozen calibration code) is already workshop-grade. Label it a frozen-analysis pilot, not a registered confirmatory study.
   - With one or two cheap nights (E2 below) it becomes a strong paper.
   - Framing: SHADE-Arena found that sabotage success "relies heavily on having access to a hidden scratchpad" (arXiv 2506.15740). Energy can bound the *size* of hidden reasoning without seeing its content. CoIn audits hidden token counts cryptographically but needs the provider's cooperation; power needs physical access instead. HEM proposals (arXiv 2505.03742) do not name power or energy as a verification signal, which is a gap this fills.
   - The v4 series (Qwen3.8-27B) and Flash-Next become the journal extension. Until then, Amendment 1 itself says there is "no cross-model monitoring claim" (`docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md:12-18@bd7a3efcd`).

3. **A short practitioner note (or a Paper-1 section): measuring LLM energy on a Mac.** It would cover rails coverage, the scheduled-contention catalogue, battery top-ups, thermal onset and the identical-work repeatability. Cheap, because the evidence already exists.

4. **Optional: the AI-agent-operated lab as a case study.** Preregistration, blinding, cross-family blind review, and an honest account of the cost of refusals and over-engineering. Noteworthy in 2026, but not a priority before 30 Nov.

**DIFFICULTY** belongs as a section of a Paper 2, not as a standalone paper (§5).

---

## 4. Research priority order: assessment

Ed's order (BYTES → agent-monitoring pilots → DIFFICULTY, with collection overlapping Paper-1 writing; `docs/strategy/2026-10-27-paper1-contingency.md:100-128@bd7a3efcd`) is right on value. Four adjustments:

1. **Lead attention: BYTES stage 1 → commit → stage 2 goes first.** It uses no Mac time, it is Paper 1's best result, and the plan's own checkpoint is "12 Nov: BYTES stage 1 committed" (`:40`). I found no repo trace of BYTES analysis work after 2026-10-31 (newest BYTES-related branches are dated 10-30). The owed item "(1c)", the thermal member-hull exclusion transform, is still listed (`RUN_STATE.md:359@bd7a3efcd`).
2. **ALIGN: run the cheap validations before committing 5-10 Mac-days to the Qwen3.8-27B series.**
   - The core estimand, detecting unlogged work, does **not** need a capable deceptive agent. It needs a calibrated counts-to-energy model, a real positive control, and more held-out sabotage trajectories.
   - Agent capability matters only for the question "does sabotage itself leave an energy signature beyond logged counts". Power is unlikely to answer that, because sabotage prompts are longer and the logged work differs (F3).
   - The planned D model is also the most expensive and riskiest choice: about 11-20 tok/s, needs thermal holds, windows up to 59,520 s, and the handoff expects ruling 1(f) to "likely refuse W1 at about 20 tok/s" (`docs/handoff/2026-11-07-account-retirement/RESUME.md` at `ca2d1ee97`; `FINAL-DESIGN.md:24,29,32@bd7a3efcd`).
   - So: R0 re-run 8 → R1 as planned. Then insert E2 (one 30B night, no thermal holds needed) before W1 and the D series.
3. **DIFFICULTY: start a lean collection build now as a hedge.** If W1 is refused under 1(f), the Mac then has useful work instead of sitting idle.
4. **Do not resume v3 calibration.** I agree with Ed (`RUN_STATE.md:1653@bd7a3efcd`). E2 is a different thing: a confirmatory night with a positive control, not more calibration.

---

## 5. DIFFICULTY: design documents and readiness

**Documents I found:**
- `docs/registrations/difficulty_pack_v1.md`: withdrawn 2026-10-14 before any data. Its refuter found that it resolved the crossover only about 4% of the time (`:3`).
- `docs/registrations/difficulty_pack_v2.md` (rev 2.3): the live registration.
  - Primary question: `qwen3-1.7b/off` vs `qwen3-4b/off` energy per correct answer (EPC) at each MATH level, decided at 0.99 (`:21`, `:335-346`).
  - Sizes come from three simulated worlds (`:108-193`).
  - Blinding by hidden factors (`:384`).
  - Registered code `fc4078667` on `lane/2026-10-14-difficulty-pack` (`:388`).
- The stale TASK_QUEUE "HEADLINE" rows A282 / A285 / A293 (1.7B vs 8B, AP-5M) are predecessors and should be pruned (`TASK_QUEUE.md:891,894,901@bd7a3efcd`).

**Readiness: NOT READY.** As of the DIF-READY-1 report (`.codex-report/DIF-READY-1.md@cef8388c7`, summarised at `RUN_STATE.md:325-332@bd7a3efcd`), and nothing has moved since:
- **Ready:** the analysis code. It is hash-pinned, and 56 tests plus a twin implementation pass.
- **Missing:**
  - a block-6 loop module kind for per-problem attempts;
  - EOS-terminated generation (the runner forces `suppress_eos=True`);
  - the energy adapter;
  - the bench runner;
  - registration rev 2.4 (battery term in the wall boundary, the idle-power leak);
  - the freeze audit.
- Earliest energy session in that report: about 13-17 Nov.

**Cost** (`difficulty_pack_v2.md:199-201`):
- about 14.5 h of thinking-off energy session time;
- about 1.2 h of 4B thinking-on generation plus idle baselines;
- about 16.8 h of bench generation with no power capture, or 22.4 h with the optional 8B thinking-on.

**[My estimate]** That is about 3 Mac-nights of energy sessions, plus bench time that needs no quiet machine.

**Recommendations:**
- **Lean runner.** Build the energy path on the ALIGN Apple runner, which already does EOS-terminated turns, per-turn attribution, battery and thermal flags, and is not pinned (`FINAL-DESIGN.md` V8, `:43-44@bd7a3efcd`). A MATH attempt is a one-turn episode. Log the departure from "block-6 sessions" in the public deviation log, under the lead's preregistration authority. This avoids redesigning `pack_registration` / `compose` / `queue`.
- **Bench off the quiet Mac**, either on the Air or on the MBP by day, once one check passes: the energy-subset problems produce token-identical outputs on both machines. Pilot 3 showed bf16 ties can break differently across code paths (`...af17111e/RECORD.md:34@bd7a3efcd`), so this must be checked, not assumed.
- **Science framing.**
  - The expected crossover, in which 1.7B is cheaper at levels 1-2 and 4B at level 5, is what wall time already shows (the pilot: 16 s against 29 s per correct answer at level 5; `difficulty_pack_v2.md:19`).
  - It is close to known results: Jin, Wei and Brooks found a difficulty-dependent accuracy-per-energy frontier on MATH500 with Qwen2.5.
  - The more topical angle is the "energy price of thinking" (4B on vs off by level). It is registered only as descriptive (20 energy problems and 64 bench problems per level).
  - Keep DIFFICULTY cheap. Do not let it take review capacity from Paper 1.

---

## 6. The highest-value next experiments

Ranked by value per unit cost. Effect sizes marked **[my estimate]** assume a threshold in joules ≈ score × per-pair s_r, and hidden-token cost ≈ e. They are back-of-envelope figures from repo numbers, not repo results.

| # | Experiment | Expected effect | Cost | Main risks |
|---|---|---|---|---|
| **E0** (precondition, not an experiment) | **BYTES stage 1 → commit predictions → held-out agreement → stage 2.** Build the (1c) thermal transform first. | Resident vs bytes predictions differ 8.4-19.4× on the 3 MoE models, so a clean "active" or "resident" answer is likely. Bytes vs time differ 1.39-2.22× on MoE, so those words are probably resolvable. Dense held-out models stay unresolved by design (2-9% separation; `bytes_pack_v1.md:27`). The H2 slope ε (J/GB) at DC and rest is the citable number, and it can be cross-checked against F5. **[design-based expectation, no data read]** | **0 Mac-nights.** About 1-3 analysis-machine days plus reviews. | Analysis tests are heavy (`test_bytes_analysis` 8,973 s, `RUN_STATE.md:926`). Llama-70B may be one-pass or missing after thermal exclusions (s5-p1 kept 2 of 10 quads; s5-p2 hull line excluded 23 members / 13 units; `RUN_STATE.md:277,931-932`). That would shrink the bytes range from 32× to about 15×. The data and withheld store sit on the MBP. |
| **E1** | **ALIGN desk analyses on existing v3 data**, four parts: (a) a fine tamper grid (strip fractions of turn-1 reasoning) to find the detection-limit H at the frozen thresholds; (b) rescore pilot-7 sabotage seeds 12-16 (design frozen before them, not calibration data) against the pilots 8-10 thresholds; this adds 10 distinct held-out sabotage trajectories at zero cost; (c) a counts-only metadata baseline (AUC), to separate "energy verifies logs" from "counts flag sabotage"; (d) truncate idle baselines from about 390 s to 60 s and refit, to test whether members per night can roughly double. | (a) **[my estimate]** detection limit ≈ 170-470 hidden tokens per episode (bank: 2.53 × 45.1 J / 0.667 ≈ 170; spam: 7.13 × 32.7 J / 0.495 ≈ 470, or about 200 without the single outlier), i.e. about 100-250 J, about 3-8% of a 2-4 kJ episode, at about 3.4% nominal false-positive rate. (b) a held-out untampered-sabotage false-alarm rate on 12 distinct trajectories instead of 2. (c) AUC likely high because of the +755-token prompt, which makes the framing point. (d) If s_r changes by less than 10%, the 516.6 s fixed member cost (`pilot_protocol_v3.md`, sizing) falls by about half. | **0 Mac-nights.** Pilot roots are on the MBP or in iCloud. | (b) is post hoc: pilot-7 scores were already seen at m = 6. Disclose it. (d) changes a protocol constant; adopt it only prospectively. |
| **E2** | **ALIGN confirm-and-inject night on Qwen3-30B** (28 members, v3 shape): 4 anchor originals as the session bridge; about 12 fresh sabotage seeds scored against the frozen pilots 8-10 thresholds; about 12 benign seeds with **real unlogged compute** injected at randomized, desk-blinded doses (0 / 256 / 512 / 1,024 tokens). Two injection modes: in-context hidden continuation, and fresh-context side generation. | **[my estimate]** In-context hidden decode costs about 0.5-0.67 J/token: about 130-170 J at 256 tokens (near threshold), 250-340 J at 512, 500-680 J at 1,024 (well above). 50% detection around 200-500 tokens. Fresh-context hidden generation costs about 0.18 J/token (pilot-6 decode coefficient, `...7e06863b/RECORD.md:39`), so it needs about 3× more tokens to detect. **This turns a simulated estimand into a physical one.** It is the single most important validity upgrade for the paper. | **1 Mac-night** (chain about 6.5 h plus about 100 min desk), or 2 nights for 24+ fresh sabotage trajectories. Small unpinned runner change on the ALIGN lane. | Injection changes thermal and clock state. That is realistic, but must be logged. Ed said "no more v3"; this is a positive control, not calibration. Where the hidden work lands (turn, tool call, between turns) has to match the stated threat model. |
| **E3** | **Known-bytes test, bandwidth-bound geometry** (larger matched dispatches at 300+ GB/s), plus one decode-matched check. | If DC J/GB stays near 0.039 while rails J/GB falls (less stall time), f drops below 0.24 and the "rails undercount memory energy" claim transfers to decode. If not, F5 is regime-specific, which is also worth knowing. | **About 0.15 Mac-night** (attempt 3's window was 1 h 17 min). Could run in a daytime gap. | Exploratory (beyond the registered BYTES slot); label it so. A geometry or residency rule may need a fresh ruling (attempt 2 hit an MLX array-size limit). |
| **E4** | **DIFFICULTY v2 energy collection via the lean runner**, bench off-night. | From the registration's simulations: ln(EPC1.7 / EPC4) at L1 is about −0.58 to −0.99 (1.7B 1.8-2.7× cheaper), at L5 about +0.48 to +0.67 (4B 1.6-2.0× cheaper). Intended-pattern power 0.86-0.99 at rev 2.1 sizes (`difficulty_pack_v2.md:166-178` tables). | **About 3 Mac-nights** plus 17-22 h of bench. Build: energy adapter, EOS member, bench runner, rev 2.4, two reviews each. | Modest novelty. Lead attention competes with Paper 1. Level is confounded with subject. Answers that hit the cap loop until cut off. Cross-machine bench may disagree with the Mac. |
| **E5** | **ALIGN cross-model generality.** Either (a) the D (Qwen3.8-27B) series as designed, or (b) a cheaper second production model for the cross-architecture claim if Flash-Next slips. | (a) gives a capable-agent model but needs at least 3-4 D windows at about 6 benign per pair each to reach m ≥ 20 (`FINAL-DESIGN.md:29-32`). (b) N decodes at 64 tok/s in the pilot (`bytes_pilot/SUMMARY.md` table), likely needs no thermal holds, and could reach m ≈ 20 in 2-3 nights. | (a) **R1 (15.6-17 h) + W1 (about 12 h) + 3-4 windows of up to 16.5 h, about 6-8 Mac-days nominal**, more like 9-12 with this project's refusal rate. (b) about 2-3 nights. | (a) feasibility refusal under 1(f); thermal holds; Flash-Next needs the SSD and runs at a peak of 112.7 of 115.4 GB. (b) Ed explicitly dropped N for capability reasons (Amendment 1 A0). Reinstating it is his call. |

**Mac budget.** About 23 nights remain through 30 Nov. Nominal demand: R1 + E2 + W1 + 3-4 D windows + E3 + E4 ≈ 10-13 nights. History points to 1.5-2× that, from refusals and redos: Block 5 needed 11 attempts for 3 usable sessions, and R0 is on its 8th re-run (`RUN_STATE.md:1154-1600@bd7a3efcd`). It fits only if E2 and E3 go early and DIFFICULTY uses the lean path.

---

## 7. Weak spots

1. **ALIGN's held-out evidence is thin.**
   - 2 distinct held-out sabotage trajectories (F2).
   - Thresholds are sample maxima at m = 28. The spam threshold rests on one benign trajectory.
   - The tamper is a post-hoc edit of the token log with measured joules held fixed (`pilot_protocol_v3.md:155-163@5f817856b`). It is not physical hidden work.
   - The protocol itself says it cannot estimate "a causal hidden-work effect, or claim-grade power" (`:193`).
2. **The agents are too weak for any sabotage question.**
   - Qwen3-30B succeeded at the side task once in 12 sabotage seeds in pilot 4 (`...c9ac22ae/RECORD.md:21@bd7a3efcd`).
   - So "does real sabotage leave an energy signature" cannot be tested on v3. Even on stronger models, the signal would be mostly logged work and a longer prompt, not something power uniquely sees (F3).
3. **Machine state contaminates the residual.**
   - The residual correlates with mean GPU clock: +0.79 to +0.92 in bank sessions, five sessions in a row (`...3efb8793/RECORD.md:24@bd7a3efcd`).
   - There is an unattributed step between sessions (F4).
   - An adversary who can shape DVFS state, or hide work in low-clock periods, is not analysed.
4. **Generalisation.**
   - One M3 Max, one OS build, batch 1.
   - Under production batching, per-request attribution collapses. The measured-energy-law paper reports the decode-to-prefill cost ratio falling from about 335× to about 3.3× under batching. ALIGN's threat model has to be stated as on-prem or edge with an operator-controlled meter, or as a metered audit.
5. **Prior-art proximity.**
   - "Prefill, Decode, and Context: A Measured Energy Law for Agentic LLM Serving" (NeurIPS 2026 workshop) fits per-call energy from prefill, decode and context, R² = 0.961. ALIGN's novelty is the forensic use and its precision, not the fit form.
   - Jin et al. 2025 covers DIFFICULTY's core.
   - GreenBench shows rails-only `powermetrics` practice is current, which supports F5's relevance.
6. **BYTES design limits.**
   - Dense held-out models cannot discriminate between hypotheses (stated in the registration).
   - The drift allowance is scaled by E/E_ref for large decode cells, because test 7 did not pass in any regime (`bytes_pack_v1.md` §7). Intervals may be wide, so some H1 words may be "unresolved".
   - The top dense point (Llama-70B) is at thermal risk.
   - The known-bytes test was latency-bound.
7. **Throughput is the binding constraint, and it is mostly self-imposed.**
   - Block 5: about 3 s measured out of each run's 237 s (`docs/design/next_block_threshold_proportion.md:31,316@bd7a3efcd`).
   - ALIGN: a 516.6 s fixed cost per member, with the configured 300 s idle running 389-393 s.
   - R0, a desk check, has taken about 9 attempts over about 33 h.
   - Several R0 failures did find real defects: the NLL bar, a prompt defect, a 100 ms coverage tolerance with no derivation. But the pattern matches the advisor's "unseen level of care for such simple measurements".
8. **Lead attention is spread thin.** B5 release, ALIGN v4 kits, the Flash-Next port, DIFFICULTY build, BYTES analysis and Paper-1 writing all compete. BYTES analysis, the cheapest high-value item, appears to be the one that dropped.
9. **Paper 1's Block-5/6 core is a method-internal question** (whether timing attribution dominates repeatability). It interests measurement specialists. Without BYTES it will read as niche.

---

## 8. Literature I opened

- SHADE-Arena (Kutasov et al., 2025): hidden scratchpads drive sabotage success; best monitor AUC 0.87. https://arxiv.org/abs/2506.15740
- CoIn: auditing invisible reasoning-token counts; up to 94.7% detection of inflation; needs a trusted third-party auditor. https://arxiv.org/abs/2505.13778
- Hardware-enabled mechanisms for verifying responsible AI development: covers compute quantity and location, and does not mention power or energy as a signal. https://arxiv.org/abs/2505.03742
- The Energy Cost of Reasoning (Jin, Wei, Brooks): test-time compute vs model scaling in accuracy per energy; matching compute to query complexity. https://arxiv.org/abs/2505.14733
- Prefill, Decode, and Context: a measured energy law for agentic LLM serving (NeurIPS 2026 workshop poster). https://neurips.cc/virtual/2026/170701
- GreenBench (Aug 2026): Apple M4 Pro, energy via `powermetrics`. https://arxiv.org/abs/2608.28667
- MoE on consumer and edge hardware: OLMoE about 2.1× the energy per token of a dense model with similar active parameters on Jetson, attributed to resident experts and bandwidth. https://www.emergentmind.com/papers/2606.21428

---

## 9. Answers to the brief, compressed

- **Publishable or surprising so far:** F5 (rails miss most memory-traffic energy), F1-F4 (energy as a witness of agent logs, with replay repeatability), F3 (the naive-model false-alarm trap), and F6 plus the BYTES design.
- **Strongest papers:** Paper 1 led by BYTES and F5. ALIGN Paper A on v3 data plus E1 and E2.
- **Priority order:** keep ALIGN before DIFFICULTY. Make BYTES analysis the top lead-attention item now. Put E1/E2 before the D series. Build DIFFICULTY lean as a hedge.
- **DIFFICULTY:** registered (v2.3) and analysis-ready; collection is unbuilt; about 3 Mac-nights; modest novelty.
- **Next experiments:** E0 BYTES analysis (0 nights), E1 ALIGN desk (0 nights), E2 confirm and inject (1-2 nights), E3 bandwidth-bound known-bytes test (about 0.15 night), E4 DIFFICULTY (about 3 nights), E5 cross-model (2-8+ nights).

<!-- seat 2 report ends -->
