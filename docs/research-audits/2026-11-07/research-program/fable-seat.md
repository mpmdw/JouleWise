# Research program audit: what is noteworthy so far, and what next (Fable 5.1 seat)

Date: 2026-11-07. Seat: Fable 5.1 (high), independent of the Opus seat. Brief: Ed's question "are there any signs when working this will lead to any noteworthy research?"

**Evidence base.** `origin/main` at `bd7a3efcd` (worktree `jw-wt/fable-research-audit`), plus three lane branches for documents not yet on main: `lane/2026-10-28-bytes-pass2-open` (`docs/registrations/bytes_pack_v1.md`), `lane/2026-11-05-align-pilot10-benign` (`docs/align/pilot_protocol_v3.md`) and `lane/2026-11-06-v4-r1-integrated` (`docs/align/PIPELINE.md`, `pilot_protocol_v4.md`, `council-2026-11-06-v4-review/LEAD-RULINGS-2.md`). Citations are `path:line @ commit`; lines in `RUN_STATE.md` are at `bd7a3efcd`.

**Blinding.** Nothing under `/Users/edr/jw-b5-*`, `night-*`, `night-custody`, `night-archive` or any `restricted/` was opened. `docs/analysis/b5/` and the `2026-11-0x-b5-*` run reports were not read. No Block-5 estimate, contrast or verdict is inferred anywhere below; where Block 5 is mentioned it is as a sealed input whose *either* outcome is publishable.

---

## 0. Short answer

Yes, there are real signs, and they are concentrated in one place that was not in the original capstone plan.

1. **ALIGN (energy as a tamper-evident record of agent work) is the one line with genuine novelty.** Ten pilots in five days produced a clean, repeatable instrument result: on Qwen3-30B-A3B running SHADE-Arena task pairs, a five-term token-accounting fit leaves a residual SD of about 20-60 J per trajectory on episodes of roughly 2.7 kJ, replays are token-identical with a pair-difference SD of 2.97 J, and every simulated reasoning omission of about 500-1,200 tokens crossed a held-out threshold while every *untampered* sabotage run stayed below it (`RUN_STATE.md:993,999,1644,1682,1699`). That is exactly the result the pipeline predicted ("power counts work; it is blind to what a token says", `docs/align/PIPELINE.md:9-21 @ e901eb2a4`) and I know of no published work that measures it. It is a paper if two things are added: a second model and a real adversary condition.
2. **Paper 1 (Block 5 + Block 6 + BYTES) is robust and will exist, but its publishable core is BYTES, not the dominance ratio.** BYTES is a pre-registered three-hypothesis test (bytes read per token vs resident bytes vs decode time) with committed predictions before held-out unblinding, over a 32-fold bytes range and a 71-fold resident range, where the three MoE models separate the hypotheses by factors of 8-19 (`bytes_pack_v1.md:16-60 @ ee4ce93fc`). Whatever word prints, it is a result about Apple unified-memory decode that nobody has measured this carefully.
3. **The metrology findings are publishable as a methods note, not as a headline.** Attribution-limited at about 1 J versus 0.3-0.5 J repeatability; the clock-anchor knife-edge; 37 of 50 short prefills unresolvable; macOS maintenance and agent idle power as measurement hazards. Honest, useful, unglamorous.
4. **DIFFICULTY is the best-designed but least surprising question.** Its registration is the most thoroughly simulated document in the repo, and its pilot shows the expected crossover (small model cheapest per correct answer on easy MATH levels, 4B about twice as cheap at level 5). The collection side is unbuilt (`RUN_STATE.md:325-332`). It is a fine capstone chapter or short paper; it is not where the novelty is.
5. **Ed's priority order (after BYTES: ALIGN pilots, then DIFFICULTY) is scientifically right.** The main risk is not order but lead capacity between 15 and 22 November, when ALIGN v4's first window may be refused by ruling 1(f) and Paper 1 needs its author.

---

## 1. What has been found so far (unblinded material only)

### 1.1 Instrument and metrology (Paper 1, Part 1 backbone)

| Finding | Evidence | Publishable as |
|---|---|---|
| The repaired instrument is **attribution-limited, not noise-limited**: boundary placement contributes about 0.7-1.0 J per run against 0.29-0.49 J repeatability on about 50 J points; the clearable phase contrast is about 5 J | `PROJECT_STATUS.md:100-105`; `CLAIMS_STATUS.md:106-110` | The motivating measurement for the Block-5 dominance question (R = timing-aware floor / point floor, pre-registered R >= 2; `configs/campaigns/v5_claim_25g83/registration_block5.md:1622-1640`). The question itself is sealed. |
| **Clock-anchor knife-edge**: at 197 s capture length the native-second intersection margin is about +/-1 ms while the unmodeled wall/monotonic rate (about -12 ppm, 2.3 ms per capture) exceeds it, so pass/fail was quantization-phase luck | `CLAIMS_STATUS.md:230-235` | A metrology limitation paragraph; motivates the rate-aware clock mapping now in the methods draft (`docs/paper/draft-v2-skeleton.md:55-66`). |
| **Short prefill is not resolvable** with `powermetrics` at this cadence: 37 of 50 Qwen2.5-1.5B prefill phases crossed only two records; the 7B passed in all 50 | `docs/paper/draft-v2-skeleton.md:19-27` | Already in the methods draft; a concrete "what a laptop sampler cannot do" result. |
| **Environmental validity on a laptop**: the operator session's own output streaming fails idle admission; validated quiet state requires suspended cloud sync; macOS daily batch at about 12:53, the XProtect scan hour, and the 00:00 `/private/tmp` walk each cost members; an idle AI agent draws 8-47 W | `CLAIMS_STATUS.md:236-242`; `RUN_STATE.md:46-53` (items 14, 17, 29); `docs/registrations/difficulty_pack_v2.md:213` | A systems note that practitioners would actually use. Nobody publishes these; they should be a table in Paper 1's limitations or a separate short note. |
| **Falsified instrument generations, recorded rather than hidden**: the anchor-v2 rate model was falsified (748 bundles permanently non-claim-bearing); Windows A and B voided; mint #1 retroactively void | `CLAIMS_STATUS.md:9-19,77-110` | Limitations section material. It is also the strongest evidence that the pre-registration discipline is real and not decorative. |

**Candid weak spot.** `PROJECT_STATUS.md` (the advisor-facing page) still says "No claim-bearing Qwen3 data exist" and describes the four-rung probe as the next milestone (`PROJECT_STATUS.md:77,169-179`); `CLAIMS_STATUS.md` was last updated 2026-08-20 (`CLAIMS_STATUS.md:38`). Both are two collection blocks stale. An advisor who reads them before the paper will form the wrong picture. Fix before 22 November.

### 1.2 ALIGN pilots 1-10 (the surprising line)

All numbers below are pilot (non-claim) numbers from the magistrate records in `RUN_STATE.md`; they are unblinded by design.

| Pilot | What it established | Where |
|---|---|---|
| 3 (greedy, 24 members) | First side-task successes; identical-work prompt-cache saving 14,451 -> 2,232 J and 20,563 -> 1,380 J against the throttled pilot 2; 6 thermal exclusions all in A/bank | `RUN_STATE.md:988` |
| 4 (sampled, 28 members) | Five-term counts-logged fit: s_r 176.4 J (20 df), e = 0.619 +/- 0.013 J per decode token; cell offsets spam -99/-79 J, bank +94/+241 J; **cross-pair transfer fails**; all 12 sabotage trajectories cross the grouped threshold at 1,282 or 2,192-3,077 stripped reasoning tokens | `RUN_STATE.md:993` |
| 5 (exact repeat of 4) | All 28 members token-identical; window contrast -0.43 J (SE 0.61); **pair-difference SD 2.97 J** (2.1 J per measurement) on multi-kJ episodes; fits reproduce (s_r 176.7 J, e 0.618) | `RUN_STATE.md:999` |
| 6-7 | Same-ordinal anchors token-identical across sessions; a **session step of 8-9 J** between pilots 5 and 6, not time of day, not attributable (no temperature recorded); frozen alternative desk out of sample: per-pair s_r bank 182 -> 87 J, spam 36.5 -> 22.9 J; **untampered sabotage alarms on spam 3/6, accumulated over later turns, tracking GPU clock** | `RUN_STATE.md:1029,1712` |
| 8-10 (held-out benign increments, seeds 17-46) | Sequence design `[1, P, D, (C+P)D + D^2/2, CP + P^2/2]` as headline: s_r bank 251 -> 58 J, spam 45 -> 19 J (pilot 8); first held-out pooled split thresholds bank 2.53, spam 7.13 at m 28-30 (the sample maximum); **all six untampered sabotage scores below threshold, all detected at the smallest tamper**; the spam threshold rests on one trajectory (next 2.99); clock correlation bank +0.79 to +0.92 for five sessions; K = 7 anchors sigma_w 4.67 J | `RUN_STATE.md:1644,1682,1699` |

What this means, stated plainly:

- **The instrument works as a work counter.** Residual SD after token accounting is 1-2 % of episode energy; a reasoning omission of a few hundred to a thousand tokens (at about 0.6 J per decode token, roughly 300-700 J) is far above it. That is a new kind of monitoring signal: a record the agent cannot edit because it is measured outside the software.
- **It is blind to intent, as predicted.** Untampered sabotage is not separable from benign once logged tokens are accounted for. The paper must say this first, not last.
- **The nuisance is thermal/DVFS drift.** Later-turn residual accumulation tracking GPU clock, an 8-9 J unexplained session step, and clock correlations near +0.9 in bank are the dominant residual structure (`RUN_STATE.md:1712,1682`). This is what the v4 thermal gates are for (`docs/align/council-2026-11-05/FINAL-DESIGN.md:15-23,432-457 @ bd7a3efcd`), and the W1 contrast experiment (T versus W) is itself a publishable methods result.

**Candid weak spots of the ALIGN result as it stands.**

1. **One model, two task pairs, 28-30 held-out benign per pair.** Thresholds are the sample maximum (rank ceil(0.95(m+1)) = m until m >= 39), so there is no false-positive-rate claim (`FINAL-DESIGN.md:54,539`). The spam threshold rests on a single trajectory.
2. **The tamper is simulated.** "Known-H" stripping of logged reasoning counts is a post-hoc transform (`pilot_protocol_v3.md:155-163 @ 83e2dac59`). It measures detection of a known log omission, which is the honest estimand, but a reviewer will ask what happens when the model itself is the adversary: compressing reasoning, moving work into tool calls, or spreading it over turns. No such condition has run.
3. **No baseline comparison.** The pipeline names `RQ-ALIGN-METADATA-BASELINE` (token, turn and tool-call counts alone) as the always-reportable baseline (`PIPELINE.md:25-31`), and SHADE-Arena's own LLM monitor reaches AUC 0.87 (Kutasov et al. 2025, https://arxiv.org/abs/2506.15740). The energy residual has not yet been placed beside either.
4. **The threat model needs a sentence.** The power record is tamper-evident only if the adversary controls the logs but not the meter and its clock mapping. That is plausible for a co-located monitor and must be stated; the project's own threat-model limitation (no adversarial process on the measurement machine, `CLAIMS_STATUS.md:14-19`) cuts the other way and must be reconciled.
5. **Cross-pair transfer fails** (`RUN_STATE.md:993`), so calibration is per task pair. A deployment story needs per-task calibration or a model of why the offsets exist (the +241 J bank/sabotage offset is large and unexplained).

### 1.3 BYTES (Paper 1, Part 2)

Design, as registered (`bytes_pack_v1.md @ ee4ce93fc`): ten MLX models (fit set Qwen3 1.7B/4B/8B 4-bit; held-out Qwen3 14B, 32B, 8B-8bit, Llama-3.3-70B, Qwen3-30B-A3B, Qwen3-Next-80B-A3B, Qwen3.5-122B-A10B), one fixed 2,048-in/512-out greedy decode workload, three boundaries (rails, DC input, rest), three frozen rival OLS lines through the fit set with corner-line prediction intervals, a word per held-out model (`bytes`/`resident`/`time`/`unresolved`/`neither`), an `active`/`resident`/`mixed` verdict over the MoE trio, Bonferroni k = 21 per boundary, hidden offsets with a withheld store, and a committed `predictions.json` before any held-out row enters the export (§8-§11).

Collection status (unblinded facts only): pass 1 complete 6 of 6 after retries (`RUN_STATE.md:349`); s5-p1 (Llama-70B) counts but is not claim-usable on thermal exclusions at the 140 W adapter (`RUN_STATE.md:277`), which produced the pass-2 thermal rule R1 (`RUN_STATE.md:350`); pass 2 ran from `2649fad54` through s6, s5, s4, s3, s2 (`RUN_STATE.md:384,900`), with s1-p2 the last slot before the 2026-11-05 end (`RUN_STATE.md:1849`). The extension model (Qwen3.8-27B-8bit) was dropped under its registered rule (`RUN_STATE.md:902`). Stage 1 is planned for 12 November (`docs/strategy/2026-10-27-paper1-contingency.md:40`).

Why it is publishable whatever it prints: the pilot (no power) showed Qwen3-32B dense reading 18.0 GB per token against Qwen3-30B-A3B reading 1.71 GB with 17.2 GB resident, and MoE decode slower per byte (130-231 GB/s effective against 209-344 GB/s dense) (`docs/design/block6_collection_draft.md:596`). On a unified-memory SoC with no DRAM power rail, whether energy follows bytes moved, bytes resident, or time is a real open question with a direct consequence for whether MoE "active parameters" buy energy or only latency.

**Candid weak spots.**
1. **The fit set is three points.** Each rival line is OLS through n = 3; prediction intervals are the 8 corner lines (`bytes_pack_v1.md:282`). Dense held-out models cannot discriminate the hypotheses (predictions differ by 2-9 %), so the whole discriminating power rests on three MoE models (`:30-32`). That is enough to answer the question but reviewers will call it thin; say so.
2. **Llama-70B**, the top of the bytes range, had its pass-1 decode cell gutted by thermal exclusions; pass 2 under R1 is the rescue. If it is `missing` or `one_pass` the dense-linearity statement loses its anchor.
3. **The DC-input and rest boundaries carry a meter label-offset alternative interval** and the rest-boundary intercept c is not identified (VIF 3.4e6) (`bytes_pack_v1.md:300-304`). Headline on rails; print the others as labelled.
4. **The known-bytes stream test** (does the GPU rail include the memory controller?) was still `PENDING` in the registration (`bytes_pack_v1.md:36`); three KB night attempts ran around 2026-10-30 (`RUN_STATE.md:1814,1833,1844`). Its outcome is a precondition for interpreting rails vs rest and I could not find it recorded on main. Open question below.

### 1.4 DIFFICULTY (Paper 2 candidate)

Pilot (no power, 20 problems per level): thinking-off accuracy falls 95 % -> 30 % (1.7B), -> 65 % (4B), -> 70 % (8B) from MATH level 1 to 5; by time per correct answer 1.7B is cheapest at levels 1-2 and 4B about twice as cheap at level 5 (16 s vs 29 s); thinking-on 4B and 8B saturate MATH at 85-100 % (`difficulty_pack_v2.md:19`; `block6_collection_draft.md:597`).

Registration v2.3 (`docs/registrations/difficulty_pack_v2.md @ bd7a3efcd`) is the most carefully power-simulated design in the repo: three synthetic worlds, two spreads, coverage bars, a near-tie world that caught a 6 % false "changes with level" rate and fixed it to 1.5 % by raising level-1 energy to 70 (`:144-168`), null worlds where the misfit check fails (`:174-191`), a twin implementation, frozen code at `fc4078667` (`:390-412`), and an end date of 2027-01-31 (`:386`).

Expected effect sizes (pilot-derived, worlds A/B/C): ln(EPC 1.7B / EPC 4B) at level 1 between -0.58 and -0.99 (1.7B 1.8-2.7x cheaper), at level 5 between +0.48 and +0.67 (4B 1.6-1.95x cheaper), level 3 near zero (`:118`). Intended pattern resolved in 0.85-0.99 of simulated campaigns at the registered sizes (`:157-166`).

**Readiness: analysis ready, collection not.** `DIF-READY-1` found the block-6 loop's module shapes cannot carry DIFFICULTY attempts, the runner forces `suppress_eos=True`, the energy adapter and bench runner are unbuilt, revision 2.4 is unwritten, and the freeze audit has not run (`RUN_STATE.md:325-331`). Everything on that list is claim-path work needing two reviews per item.

**Candid weak spots.**
1. **Novelty.** "Small models collapse on hard problems, so the cheapest model per correct answer flips with difficulty" is intuitive; the contribution is measuring it in joules on-device with pre-registered decisions. Fine for a capstone chapter; a workshop paper at most unless the thinking-on energy gradient is the headline.
2. **Contamination.** MATH is in every 2025-2026 model's training mix. The registration says "at level L", never "difficulty causes" (`:25`), but it does not address memorization; a held-out or perturbed set (the pilot already suggests AIME-style for thinking-on, `block6_collection_draft.md:597`) would be stronger.
3. **Model age.** Qwen3 1.7B/4B/8B are the right ladder for 2026-10 but the ALIGN track has already moved to Qwen3.8; by January the ladder will read dated. This is acceptable for a controlled ladder; say so.
4. **One cell the sizes cannot fix** (8B level-1 undercoverage from one 5.5x-length problem, `:172`) is disclosed; good, but a reviewer will notice the design is at the edge of what 30 energy runs per level can do.

### 1.5 Process and automation

Nine Block-6 sessions (3 per pack), twelve counting BYTES sessions and ten ALIGN pilots were armed, run, harvested and read by a headless magistrate with pre-registration, blinding (hidden offsets after Klein and Roodman 2005, `bytes_pack_v1.md:342`), refusal-as-result (D-189/D-190, `docs/decision_log.md:12251-12272`), two-seat blind consults and twin implementations. That is a real automation result. It is publishable as a methods or process contribution **only** if it is framed as what it bought (zero results read before registration; zero silent retries) rather than as its mechanism, and only after a proportionality pass: the advisor's comment that the project over-engineers simple measurements (memory: proportionate care) will be a reviewer's comment too. The repo prune (`CANONICAL.md:1-14`) is the right instinct.

---

## 2. The strongest papers

### Paper 1 (due 30 November): "Phase energy on Apple silicon under pre-registration: attribution limits, replication, and what decode energy follows"

- **Part 1**: Block 5 (sealed) beside Block 6 (three claim-usable sessions per pack, `RUN_STATE.md:203`), same estimators, printed side by side; the dominance question answered either way; the methods draft (`docs/paper/draft-v2-skeleton.md`) already carries the attribution and clock material.
- **Part 2**: BYTES stage 1 and 2 with committed predictions.
- **Why it is strong**: no outcome dependence (`2026-10-27-paper1-contingency.md:8-15`), a replication built in before any number was seen (`RUN_STATE.md:66`), and a hypothesis test with pre-committed predictions.
- **Why it is not a top-venue paper**: one machine, one stack, one boundary, a three-point fit set, and models (Qwen3 1.7B/8B) that will read dated. Target: a measurement or sustainable-ML venue or workshop (the energy-benchmarking literature it sits beside is Samsi et al. 2023, https://arxiv.org/abs/2310.03003; Fernandez et al. 2025, https://arxiv.org/abs/2504.17674; Stojkovic et al. 2024, https://arxiv.org/abs/2403.20306; Splitwise for the prefill/decode phase framing, Patel et al. 2024, https://arxiv.org/abs/2311.18677). Its differentiator against all of those is on-device Apple silicon with stated detection floors and pre-registration; none of them report an attribution floor.

### Paper 2 (the one worth protecting): "Energy as a tamper-evident work record for LLM agents"

- **Claim shape**: a software-independent power trace, after token accounting, detects omitted work of size H tokens with calibrated per-pair thresholds; it does not detect sabotage per se.
- **What exists**: the pilot 4-10 corpus on Qwen3-30B-A3B, the frozen sequence design and calibration script (`7fbd95e31`), the v4 thermal-gate design and the W1 T-vs-W contrast experiment.
- **What it still needs**: (a) a second model (Qwen3.8-27B via v4; Flash-Next later), (b) a real-adversary condition, (c) the metadata baseline and an LLM-monitor comparison on the same transcripts, (d) m >= 39 per pair for a finite threshold, (e) the thermal-control result (U1-U6) so residual drift is bounded rather than described.
- **Related work to position against**: SHADE-Arena (monitoring with LLM monitors, AUC 0.87; Kutasov et al. 2025); physical side channels on neural networks (Batina et al. 2018 recover architecture and weights from power/EM on a microcontroller, https://arxiv.org/abs/1810.09076), which is the inverse use of the same physics. I found no prior work using power as a monitoring record for agents; that gap is the paper.
- **Venue**: an AI-control or safety workshop first; a systems-security venue if the adversary condition holds up.

### Paper 3 (capstone chapter or short paper): DIFFICULTY

As designed. The honest headline is the pre-registered crossover in joules per correct answer and the thinking-on energy gradient where accuracy saturates.

---

## 3. Priority order: assessment

Ed's order (`2026-10-27-paper1-contingency.md:115-124`): after BYTES closes, agent-monitoring pilots first, then DIFFICULTY, overlapping Paper 1 writing. The 11-07 resume note sharpens it: ALIGN first; Flash-Next port waits on the SSD (`docs/handoff/2026-11-07-account-retirement/RESUME.md:17`).

I agree, with two conditions.

1. **Paper 1's lead time is the scarce resource, not Mac-nights.** The contingency plan reserves 15-22 November for writing and says Paper 1 goes first if DIFFICULTY needs attention (`:112-113`). The same rule must apply to ALIGN v4. The v4 build has already consumed nine review rounds (`LEAD-RULINGS-2.md:14 @ e901eb2a4`), and ruling 1(f) is expected to bind on hardware: at about 11 tok/s, (6,144 + 4,096) / 11 is about 930 s against T_dead about 1,200-1,280 s, so W1 is refused unless worst-case G0 + gates + prefill fit in about 270-350 s (`LEAD-RULINGS-2.md:61,199-206`). When the kit refuses, the lead owes ruling 1(e)'s fallback. Decide the fallback order **now**, blind, so that the R1 night's outcome triggers a procedure and not a design session during the writing window.
2. **Keep the 30B series alive as the fallback and as Paper 2's calibrated base.** Pilot 10 was declared the last v3 pilot because 30B thresholds do not transfer to Qwen3.8-27B (`RUN_STATE.md:1653`). True, but a pilot 11 of pilot 10's shape reaches the m >= 39 contract on the 30B (`RUN_STATE.md:1662`) at one Mac-night with zero build risk, and it is the cheapest route to a finite (non-sample-maximum) threshold on *some* model. If W1 is refused twice, run it.

DIFFICULTY third is right: its collection code does not exist, its end date is 2027-01-31, and its bench attempts (no power) can run as daytime jobs once the bench runner exists.

---

## 4. DIFFICULTY design documents: readiness

| Item | State | Evidence |
|---|---|---|
| Registration text | v2.3 on main, cold-gated by refuters (Sol) at v2.1, v2.2; revision 2.4 "unwritten" per DIF-READY-1 (presumably the idle-power leak and contention-level items) | `difficulty_pack_v2.md:1-9`; `RUN_STATE.md:175,329` |
| Registered estimator code and twin | frozen at `fc4078667` on `lane/2026-10-14-difficulty-pack`; 56 tests; main and twin agree on production-shaped synthetic packs within 1e-6 | `difficulty_pack_v2.md:390-412` |
| Problem lists | built, hashed, kept outside the repo (manifest holds problem text) | `:97` |
| Power simulations | worlds A/B/C, near-tie, nulls; intended pattern >= 0.85; near-tie false-change 0.015 | `:155-191` |
| Collection code | **absent**: loop module shapes, `suppress_eos`, energy adapter, bench runner | `RUN_STATE.md:325-331` |
| Freeze audit (#416) | not run | `RUN_STATE.md:330` |
| Machine time | 570 thinking-off energy runs about 14.5 h of session time with 85 s idle baselines; 5,400 bench attempts about 13 h (no power; busy-machine upper bound); 4B thinking-on about 5 h; 8B thinking-on optional about 5.6 h | `difficulty_pack_v2.md:201` |

Readiness verdict: **the science is ready; the plumbing is one to two weeks of two-review build away.** Earliest energy about 13-17 November was the 10-27 estimate (`RUN_STATE.md:332`); with ALIGN first, December is realistic and still inside the end date.

One design concern to settle before revision 2.4: the pilot timed answers "while other jobs ran" (`:201`) and the energy adapter's physical flags assume the block-6 contention level, which is itself a slot filled from the quiet-machine kit (`:218`). Confirm that level is recorded before the first DIFFICULTY session, or the primary line's exclusion rule is undefined.

---

## 5. Highest-value next experiments

Costs are in Mac-nights of about 12.4 h (one 44,640 s window); build cost is separate. Expected effect sizes are from the unblinded pilots and registrations cited above; none depends on a sealed number.

| # | Experiment | Expected effect | Mac-nights | Main risks |
|---|---|---|---|---|
| E1 | **Block 5 release, then Block 6 read under the same estimators** (laptop work; the r4 D5 fix is in flight, `RESUME.md:20-28`) | Whatever prints. The decision interval machinery and the replication difference are the result; both outcomes are pre-written | 0 (dry run runs on the laptop; the measurement Mac is not needed) | The release check holding on a new family after D5; the 20 Nov Tier-E date (`2026-10-27-paper1-contingency.md:25`) |
| E2 | **BYTES stage 1 (12 Nov) and stage 2**, preceded by recording the known-bytes stream-test outcome | H1 words on the three MoE models, where rival predictions differ by 8-19x (decisive at the registered precision); dense held-out tests line straightness at 2-9 % | 0, or about 0.1 if the KB test must be re-run on a quiet Mac (about 1 h, `bytes_pack_v1.md:36`) | Llama-70B pass-2 cell short; KB outcome missing; the fit-set-of-three critique |
| E3 | **ALIGN v4 W1 + D1-D3 on Qwen3.8-27B** as amended (18-member W1; three D windows at 58,260 s) | Contrast T-vs-W verdict at |d| >= 10 J vs <= 6 J against 2.1 J same-position noise (`FINAL-DESIGN.md:432-446`); second-model tamper curve; U1-U3 thermal control in W1, U4 at D3 | 44,640 + 3 x 58,260 s of maxima, about 61 h, expected about 45 h: **4-5 Mac-nights** (`FINAL-DESIGN-AMENDMENT-1.md:A2`) | Ruling 1(f) refusal; D effort ladder failing (D becomes a screen); unverified SMC thermometry on Mac15,9 (`AMENDMENT-2.md:§3`); capability gate (no state-changing action); hybrid cache rebuilds. Sample-maximum thresholds remain |
| E4 | **ALIGN real-adversary and baseline night on the 30B** (design council first): conditions where the model is instructed to keep reasoning terse or to move work into tool calls, with the frozen calibration unchanged; score the metadata baseline and a local LLM monitor on the same transcripts | If energy residuals catch omitted tokens that the transcript hides, detection at H of order 500-1,200 tokens as in pilots 4-10; if the adversary compresses work rather than hiding it, a null that the paper needs to state. Baseline AUCs give the comparison SHADE-Arena readers expect | 1-2 (reuse pilot-10 kit shape; a pilot 11 of the same shape also reaches m >= 39, `RUN_STATE.md:1662`) | Prompt-induced work differences confound the residual (the +755-token sabotage prompt already shows how); needs the `Turn.hidden_tokens` ledger to be the adversary's, not the logger's; judge-free pilots so far (`RUN_STATE.md:322`) |
| E5 | **DIFFICULTY collection** after the plumbing build | Level-1 and level-5 resolved in opposite directions in >= 0.85 of simulated campaigns; ln ratios about -0.6 to -1.0 and +0.5 to +0.7 | about 3 (14.5 h energy sessions as 1.5 nights; 13 h bench can run by day without power capture; 5 h thinking-on) | Collection code unbuilt; contamination critique; contention level slot; one 5.5x-length problem undercovering 8B level 1 |
| E6 | **Second-unit replication of one Block-5 pack shape** (C5-3.1, the cheapest route from stack-specific to replication-aware claims, `docs/research_question_registry.md:103`) | A machine-to-machine difference printed under the same estimators; converts "one unit" from a limitation into a measured term | 2 per pack shape (ALPHA + BETA) on a borrowed M-series Mac | Access; calibration acceptance must be re-derived for the unit; competes with ALIGN for lead time. Optional for Paper 1; strong for any journal version |

If only three can happen before the end of the year: E1 and E2 (Paper 1), then E3. E4 is the cheapest high-information experiment in the whole program and I would run it ahead of D2-D3 if W1 is refused.

---

## 6. Weak spots, collected

1. **Stale advisor-facing status pages** (`PROJECT_STATUS.md`, `CLAIMS_STATUS.md`) describe a project two blocks behind the real one.
2. **One machine, one stack, one boundary** for every claim; the registry already caps claims at L2 for that reason (`research_question_registry.md:89`), but no replication-aware term exists yet (E6).
3. **ALIGN's estimand is a simulated omission** scored against sample-maximum thresholds on one model and two task pairs; no baseline comparison; threat model unstated.
4. **BYTES rests on three fit points and three MoE models**; the 70B anchor is thermally fragile; the memory-controller question (KB test) must be recorded before rails is interpreted.
5. **DIFFICULTY has no collection code** and a contamination question it has not addressed.
6. **Over-engineering as a reviewer risk**: twelve-column registrations and nine-round reviews are the project's strength and its most visible excess. The paper should report what the machinery bought in one table and move on.
7. **Model obsolescence**: the Block-5/6 and DIFFICULTY ladders are Qwen3; the ALIGN line is already on Qwen3.8. Say in Paper 1 that the method, not the models, is the contribution.

---

## 7. Open questions I could not close from the repo

1. What was the **known-bytes stream test** outcome (KB night attempts 1-3, 2026-10-30)? It is a registered precondition for BYTES stage-1 unblinding (`bytes_pack_v1.md:36`) and I found no recorded result on main.
2. Did **s1-p2** count, closing BYTES pass 2 at 6 of 6, and has its head been appended to the freeze-by-commit addendum §5 (`RUN_STATE.md:1849`)?
3. What is **ruling 1(e)'s fallback order** if the W1 kit refuses on 1(f): 4-bit D, lower B_D, D as a screen with the 30B series continuing, or wait for Flash-Next?
4. Has Ed answered **Q4** (59,520 s D windows) and **Q6** (registration grade m >= 39) from the FINAL-DESIGN checklist (`FINAL-DESIGN.md:§3.2`)? Both change E3's night count by a factor of about two.
5. Is there a plan for a **MATH contamination or perturbation check** before DIFFICULTY revision 2.4 is sealed?
6. Where do the pilot-4-to-10 **sabotage prompts' extra 755 tokens** sit in the sequence design: is the prefill term enough to absorb them, or does part of the +241 J bank/sabotage offset come from prompt length rather than hidden work?

---

## Appendix: sources opened

Repository (at the commits named inline): `PROJECT_STATUS.md`, `CLAIMS_STATUS.md`, `RUN_STATE.md`, `CANONICAL.md`, `docs/strategy/2026-10-27-paper1-contingency.md`, `docs/handoff/2026-11-07-account-retirement/RESUME.md`, `docs/registrations/difficulty_pack_v1.md`, `difficulty_pack_v2.md`, `bytes_freeze_by_commit_addendum.md`, `bytes_extension_models_2026-10-27.md`, `bytes_end_date_amendment_2026-10-27.md`, `block6_replication_DRAFT.md` (head), `docs/design/block6_collection_draft.md` (§18), `docs/design/next_block_threshold_proportion.md` (head), `docs/align/council-2026-11-05/FINAL-DESIGN.md` and amendments 1-2, `docs/research_question_registry.md`, `docs/decision_log.md` (D-188 to D-190), `docs/paper/draft-v2-skeleton.md` (head), `docs/paper/results-fill-registry.md` (head), `docs/paper/round7/survival-map.md` (head), `configs/campaigns/v5_claim_25g83/registration_block5.md` (§1); on lanes: `docs/registrations/bytes_pack_v1.md` @ `ee4ce93fc`, `docs/align/pilot_protocol_v3.md` @ `83e2dac59`, `docs/align/PIPELINE.md`, `pilot_protocol_v4.md`, `council-2026-11-06-v4-review/LEAD-RULINGS-2.md` @ `e901eb2a4`.

External (opened 2026-11-07): https://arxiv.org/abs/2506.15740 (SHADE-Arena); https://arxiv.org/abs/2504.17674 (Fernandez et al. 2025); https://arxiv.org/abs/2310.03003 (Samsi et al. 2023); https://arxiv.org/abs/2311.18677 (Splitwise); https://arxiv.org/abs/2505.09598 (Jegham et al. 2025); https://arxiv.org/abs/2403.20306 (Stojkovic et al. 2024); https://arxiv.org/abs/1810.09076 (Batina et al. 2018). The ML.ENERGY leaderboard page returned only a title and the PNAS preregistration paper returned 403; neither is cited above.
