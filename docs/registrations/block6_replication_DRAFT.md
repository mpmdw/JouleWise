# Registration B6-REPL (draft): block 6, the replication of block 5's three packs

**Status: DRAFT, not cold-gated.** Written 2026-10-14 by Opus 5.5 (session e308c59a), before any block-6 data
exists and while block 5 is still blinded. The author opened no block-5 energy, power, floor, phase duration,
calibration value or outcome; the only numbers below are design figures, non-claim rehearsal figures and synthetic
worked examples, each labelled. This file is both the registration and the analysis plan of the three replication
packs. Every refusal line that the quiet-machine measurements will set is an **open slot**, written
`OPEN[S-n]`, which names the measurement or record that fills it; §14 lists them all. No number is entered in a
slot before its measurement exists.

**What happens to this draft.** The quiet-machine measurements (named M1 to M15 in section 8 of the design draft
cited below; M2, M3 and M4 supply the measured values that three of the refusal and exclusion rules consume, and §14
lists every one this file needs) run with no AI agent alive on
the machine and fill the slots; the 40-minute machine test (a short session on the final code that exercises the
agent pause, an idle disturbance up to the wait cap and an unplugged meter) runs on the code to be pinned; the pinned
commit is named (§7); then one **cold gate** (an independent judgment by a model with no prior involvement in this
work, checked by a second model whose task is to show it wrong) reads this file against the measurements; then the
file is committed with a date. That commit precedes the start of round 1's first session (its t0, §1.6). A change
after that commit is a dated entry in §17 with its reason (§12.4 says what such a change may and may not touch).

**Governing texts, in order of authority.** `RUN_STATE.md` item 37 (the blind decisions (a) to (f) of 2026-10-14
with their amendments of 03:26, the close at 2026-11-01, whole-machine energy per phase, the labelled sensitivity
lines and the definitions fixed at 07:53) and item 39 (block 6 on its own track); `docs/design/block6_collection_draft.md`
sections 5, 6, 13, 13.1, 16 and 17, where 13 and 13.1 override the earlier sections; the threshold note
`docs/design/next_block_threshold_proportion.md` sections 8 and 9; the pruning list
`docs/process/pruning_list_2026-10-14.md` section 7a; and, for every estimator block 6 reuses unchanged, block 5's
registration and analysis plan (`configs/campaigns/v5_claim_25g83/registration_block5.md`, written "B5-REG" below,
and `analysis_plan_block5.md`, written "B5-PLAN"). Where this draft fills a gap those texts leave, §15 lists the
choice as a decision made by the author, with the text it rests on; those that change which data count or a
printed number are marked for the cold gate.

**Revision of 2026-10-15.** The lines that refuse or exclude were sized against the instrument by the
orchestrator's ruling `/Users/edr/night-archive/silly-numbers-2026-10-15/council/RULING.md` (two blind seats, Sol 6.1
and Opus 5.5, replayed every rule over the 77 unblinded rehearsal runs of 2026-10-06 and 2026-10-09; Ed, 2026-10-15:
"make sure there are no such silly numbers please"). Each changed clause now states its line and one sentence of
derivation with its replay count and its size in joules. Changed: the alignment screen is a flag on every path (§3.2
item 5); the b_op stop line is the 25% attribution point of the pack's smallest target phase, 139 ms for the 1.7B
packs (S-5); a cooldown that reaches its cap no longer excludes (§8.3 item 1); the outside-processor line charges only
CPU time above the quiet machine's own (S-8); the graphics line uses each phase's own length (S-9, S-11); waited runs
are excluded only on M2's point estimate (S-6); the pre-check clock-rate hold moves to 5 ms / T_stream_max − 0.25 ppm
(S-7); the wall meter is a cross-check and excludes nothing (S-12); one slow sampler interval and recent keyboard or
mouse input are flags at the pre-check (§8.6); the recompute tolerance is fixed (S-13); the NEG-8 bracket decision is
disclosure only (§9.5 item 7); the rehearsal replay counts are written (S-16). The 5 ms run clock bound, the 0.25 ppm
margin and the cross-session test are kept, now with their counts.

**Revision of 2026-10-17: the quiet-machine values.** The quiet-machine kit ran with no agent alive from 2026-10-16
16:24 to 2026-10-17 06:42 PDT (kit commit `1c1bc3204`, results under `/Users/edr/night-archive/threshold-validation/`,
every test complete). Its numbers fill S-4, S-6, S-7 (r), S-8 and c_q, and give S-12's printed cross-check. Every value
below carries its source, its arithmetic and its replay count; the full arithmetic, line by line, is in
`/Users/edr/night-archive/b6-acceptance/DERIVATION.md`. In short:

- **S-4, fresh acceptance** (`configs/b6/registration/acceptance.json`): alignment reference 37.054941476587 ms,
  s_bracket 10.818 ms (the D-125 floor binds over the measured range of 9.675 ms), drift budget 15.50217418713139 ms,
  from the 13 quiet captures of the kit; 0 of the 4 rehearsal sessions stopped.
- **S-6, waiting:** d = +0.180 J on the reference prefill (+0.009 J on its decode), below 0.475 J, so `idle.waited` is
  disclosed only; no waited run exists in any replay.
- **S-7, clock:** r = −4.67 × 10⁻⁷ ppm over 14.3 hours with network time off; T_stream_max stays block 5's 335 s
  (the machine test that was to measure run spans produced no runs); hold 14.675 ppm; 0 sessions held.
- **S-8, outside processor work:** w = 5.432 J per outside CPU-second (the largest of M4's 20 bursts), c_q = 0.54
  CPU-s per 10 s interval (§8.5). As registered, the exclusion would remove 12 to 14 of the 53 quiet rehearsal runs of
  2026-10-09, which §8.7 item 1 does not allow, so for round 1 `contention.request_overlap` stays a recorded flag and
  the registered rule's result is printed beside each cell as a labelled alternative.
- S-5, S-9 and S-11 stay open: the kit ran no pack smoke and no 2,048-token prefill. S-10 (F_min) stays with the cold
  gate; every line below is written as F_min / 4 = 0.475 J at the proposed 1.9 J.

**Cold gate of 2026-10-17 on the quiet-machine values.** Two blind cold judges, Fable 5.1 and Opus 5.5, each
re-derived the fill from the kit's raw files: `docs/process_traces/2026-10-17-magistrate-1a1261a5/b6-accept-ruling-fable.md`
and `docs/process_traces/2026-10-17-magistrate-1a1261a5/b6-accept-ruling-opus.md` (written "the Fable ruling" and "the
Opus ruling" below). Both reproduced S-4, d, r, the 20 burst values and the replay counts. The lead's decisions,
which govern where the judges differ (§15 D31 to D38):

- S-4 registered as filled (§3.3).
- S-6 registered: d = +0.180 J, `idle.waited` disclosed only; the text now describes M2's two arms as measured
  (ordinary baselines of about 75 s, not 85 s; 8 of 10 long waits ended at the kit's 2,700 s cap) and says why d
  still qualifies (§8.5).
- S-7 registered: r = −4.67 × 10⁻⁷ ppm; T_stream_max = 335 s, carried from block 5, replaced by the machine test's
  longest run-level stamp span if that is longer.
- S-8: w = 5.432 J per CPU-s registered as measured; the exclusion is not adopted for round 1 (above; §8.3 item 3,
  §8.5).
- c_q = 0.54 CPU-s per interval governs (every quiet-machine interval, Spotify and an orphaned test process removed);
  0.72 with them is printed beside it; 2026-10-09's 0.52 is the check.
- Before round 1: Spotify not running and the orphaned hazard monitor stopped (§7 item 6), a recorded condition and a
  pre-check flag, not a refusal.
- S-5, S-9, S-11 held until each pack's smoke; S-12 registered (printed cross-check, excludes nothing).

## 0. Why block 6 exists

Block 5 produced one usable session per pack (ALPHA attempt 1, BETA attempt 6, GAMMA attempt 1). Every interval
it prints is built from the scatter of runs inside that one session, so it says how much the number moves from run
to run on one afternoon and nothing about whether it holds on another day, after another reboot, at another time
of day. Block 6 collects at least two, and aims for three, further sessions of each pack with the same session
shape and block 5's arithmetic, so that every printed quantity has three or four independent sessions behind it.
With four sessions a spread across sessions rests on 3 degrees of freedom instead of 2; an interval for a mean over
sessions, were one computed (§10 computes none), would shrink from 4.303 / √3 = 2.48 standard deviations (three
sessions) to 3.182 / √4 = 1.59 (four), 36% narrower.

Every choice in this file that could depend on what block 5 shows was made before any block-5 number was seen
(item 37), so block 6 is collected whatever block 5 shows.

## 1. Terms, built in the order they are used

### 1.1 The machine and the power sampler

- **The machine.** One Apple M3 Max laptop (model identifier Mac15,9), on its 140 W mains adapter, dedicated to
  this work by its owner, Ed. Its OS build is recorded with every session (§3.2 item 6).
- **Processor rails.** The chip reports the electrical power of three on-chip parts: the CPU cores, the graphics
  processor (GPU) and the neural engine (ANE). Their sum is the quantity every claim in this file measures.
- **Sampler and power record.** The macOS tool `powermetrics` is asked for one reading every 100 ms and in fact
  delivers one about every 130.5 ms. Each reading, a **power record**, is the *average* rail power over its own
  time span. A record's span is never subdivided: inside it, the power is known only as that average.

### 1.2 A run, step by step

A **run** (the code says *member*) is one inference request in its own process:

```
 idle baseline (75 s) | idle admission | warm-up | measured request | cleanup  ... cooldown before the next run
 |<----------------------- one sampler stream ------------------------->|
```

- **Idle baseline.** 576 consecutive power records (about 75 s) of the machine doing nothing.
- **Idle admission.** The test, applied to the baseline, that the machine was quiet: the 95th percentile (the value
  95% of the records lie under, written **p95**) of rail power is at most 1.0 W, plus environment checks (on AC
  power, displays asleep, thermal state nominal). Block 5 also required the p95 of the CPU busy fraction to be at
  most 0.5; in block 6 that test is recorded as a flag only (§8.4). In block 6 a failed baseline makes the run
  **wait** (§3.2).
- **Warm-up.** One untimed generation of the same request, so the measured one does not pay first-call costs.
- **Measured request.** The request whose energy is reported.
- **Sampler stream.** One continuous `powermetrics` process from the baseline's start to the request's end.
- **Cooldown.** Between runs of a stage, short power readings (about 7.5 s each) until one reads at most twice the
  previous run's baseline power with the thermal state nominal, or 300 s pass, so that heat and activity from one run
  do not leak into the next.
- **Stage.** One ordered list of runs the campaign runner executes together (for example the ten decode repeats).

### 1.3 Phases and phase energy

- **Phase.** A timestamped part of the measured request. **Prefill**: the model reads the whole prompt and computes
  the first output token. **Decode**: the model produces the remaining output tokens.
- **Phase energy.** Each power record contributes its power times the length of time it overlaps the phase. Nothing
  is subtracted for idle power: the energy is **gross**. *Worked example (synthetic; B5-REG §0.4).* A phase runs from
  10.00 s to 10.25 s. Record 1 covers 9.90–10.03 s at 20 W: overlap 0.03 s, 0.60 J. Record 2 covers 10.03–10.16 s at
  30 W: 0.13 s, 3.90 J. Record 3 covers 10.16–10.29 s at 30 W: 0.09 s, 2.70 J. Phase energy = 7.20 J.

### 1.4 Workloads and models

- **Models.** Qwen3-1.7B and Qwen3-8B, both 4-bit, run with MLX (Apple's machine-learning framework) on the
  machine's GPU; the files are pinned by hash (§8.2, row W1).
- **Decode workload.** One fixed 42-token prompt (prompt 0 of `real_prompts_v1`, Qwen3 chat template, thinking off);
  output forced to exactly 512 tokens (greedy, end-of-sequence suppressed). Its decode phase is reported. Its
  42-token prefill, shorter than one power record, is registered as unresolvable and never printed ("p42").
- **Prefill workload.** One fixed prompt of exactly 2,048 tokens (block 5's token-ID hash
  `202e4913340b2bae39bf9a9d3a314f62bb5ff783fae483ad6a98507d071e1479`), 512 output tokens. Its prefill phase is
  reported ("prefill-p2048").
- **Reference workload.** A third model, Qwen2.5-1.5B, with a 1,024-token prompt and 256 output tokens, about 37 J per
  request. It is not a science measurement: it is run at fixed places in every session to see whether the instrument
  drifts (§1.8).

### 1.5 Repeats, quads, contrasts, units, strata and cells

- **Repeat.** One run of a workload on its own. Ten in a row form the repeat stratum of a phase.
- **Quad.** Four consecutive runs in the order A, B, B, A. *Why:* if every run reads δ joules more than the one before
  it (a slow linear drift), positions 0, 1, 2, 3 carry 0, δ, 2δ, 3δ; side A (positions 0 and 3) averages 1.5δ and side
  B (positions 1 and 2) averages 1.5δ, so A minus B gains nothing from the drift. A curved drift does not cancel.
- **Null quad.** A quad whose two sides run the identical model and workload. Any A-versus-B difference can then
  only come from the instrument and the machine.
- **Contrast quad.** In GAMMA, side A is Qwen3-1.7B and side B is Qwen3-8B on the same workload, always in the order
  1.7B, 8B, 8B, 1.7B. Its difference is d = (B1 + B2)/2 − (A1 + A2)/2.
- **Unit.** What the statistics treat as one independent draw: one repeat, or one quad. A **stratum** is all units of
  one kind for one phase (for example the decode quads). Ten units are planned per stratum; the estimators are
  defined from five.
- **Reported cell.** One registered energy per model and phase, from that model's 10 repeats and 10 null quads (50
  runs). The **target cells** are decode and prefill-p2048 for each model.
- **Kept unit.** A unit none of whose runs was excluded (§8). Removing one run of a quad removes the whole quad, so
  its drift cancellation is never broken.

### 1.6 Packs, sessions, attempts, rounds

- **Pack.** One frozen measurement plan. **ALPHA** measures Qwen3-1.7B's reported cells and detection floors (the
  smallest energy differences the method can tell apart from noise, §9.2)
  (`configs/campaigns/d117_floor_qwen3-1p7b_v5`), **BETA** the same for Qwen3-8B (`d117_floor_qwen3-8b_v5`),
  **GAMMA** the two 1.7B-versus-8B contrasts (`d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`).
- **Session** (block-5 code: *window*). One unattended collection of a whole pack, about 6 hours. **t0**: the moment
  its driver starts. **Attempt**: one try at a session; an attempt counts as made when its chain (the script that
  runs the session's stages in order) starts its first stage. **Round**: one attempt of each pack that has not yet
  reached its target (§6).
- **Session loop.** Plain programs started by launchd (the macOS job scheduler) that run, for each session in turn,
  the pre-session check, the smoke when needed (both built in §3.2 item 6), the session and its desk steps, with no
  AI agent alive (an agent draws 8 to 47 W at "idle"). When it needs a decision it **wakes the orchestrator**, the
  lead model session that runs this project, which may run only while no session is in progress.

### 1.7 Timing: captures, the operative bound, the first-kind bound, the attribution floor

*Forcing problem.* Power records are stamped by the sampler; phase edges are stamped by the program running the
model. To give a phase its records, the two time bases must be laid on one timeline, and the energy assigned to a
phase depends on how well that is done.

- **Calibration capture.** A short run in which the GPU is driven through 59 commanded on/off pulses. For each pulse
  the estimator fits the power records with a rectangle whose edges may be late, and returns the delays consistent
  with the records. The capture's **fiducial bound** is the largest such delay over all pulses, in milliseconds: the
  largest timing error between commanded and observed edges. Each session has an **opening capture** before its
  first run and a **closing capture** after its last.
- **Operative timing bound** (b_op). The timing bound used for the whole session:
  b_op = max(opening, closing) + max(|closing − opening|, s_bracket), where s_bracket is a fixed minimum allowance
  for the alignment moving between the two captures, taken from the calibration acceptance (§3.3; block 5's value is
  14.531 ms, block 6's 10.818 ms). *Worked example (synthetic):* opening 40.0 ms, closing 30.0 ms, s_bracket 14.531 ms: b_op = 40.0 +
  max(10.0, 14.531) = 54.531 ms. With opening 28.0 and closing 48.0 ms: 48.0 + 20.0 = 68.0 ms.
- **First-kind timing bound of a run** (the first of the three kinds of recorded bound that §9.1 adds up). The
  largest change in the run's phase energy when each phase edge is moved, on its own, by up to g = b_op + s (s is
  the change in wall-clock-minus-monotonic-clock time over the run's sampler stream), while the whole power trace is
  also shifted by up to ± m (the run's effective clock bound, fitted from its own records, B5-REG §0.14). *Worked example
  (synthetic; B5-PLAN §4 step 4):* b_op = 45.6 ms, s = 0.4 ms, so g = 46 ms; m = 2 ms; the record holding the start
  edge averages 40 W and the one holding the end edge 10 W. Moving the start edge 46 ms early and the end edge 46 ms
  late adds 0.046 × (40 + 10) = 2.30 J; shifting both a further 2 ms early adds 0.002 × (40 − 10) = 0.06 J. The bound
  is 2.36 J.
- **Attribution floor of a cell.** The largest first-kind bound over the cell's kept runs. It is printed beside the
  cell because every run of a session is laid on the timeline by the same method, so this part of the uncertainty
  does not shrink when runs are averaged.

### 1.8 Reference runs and the drift screen

- **Reference runs.** Runs of the reference workload at fixed places: 18 at the start (the **corpus**), then a
  **start triplet** (3), one **midpoint reference** between the decode and prefill halves of the session, and an
  **end triplet** (3). GAMMA also runs two diagnostic references, one in the middle of each half, which enter neither
  the screen nor the allowance.
- **Clean corpus.** The first 12 corpus runs, in the committed order, that succeeded and carry no excluding run flag
  (§8.3). At least 6 are needed (block 5 needed 10; the threshold council of 2026-10-12, row N2, set 6).
- **Drift bound.** From the clean corpus energies (n values, sample standard deviation s), for n_s surviving start
  references and n_e surviving end references, with U_j the mean of the corpus's j largest values and L_j the mean of
  its j smallest: bound(n_s, n_e) = max( max(U_ns − L_ne, U_ne − L_ns), t × s × √(1/n_s + 1/n_e) ), with t the
  0.975 Student-t quantile at n − 1 degrees of freedom rounded to three places (`whole_window.neg8_count_adjusted_bound`).
  The first term is the widest gap two means of those sizes could show if drawn from the corpus itself; the second is
  the 95% repeatability bound for a difference of two means when nothing drifts.
- **Drift screen** (the code calls it NEG-8). The session passes when |mean of surviving end references − mean of
  surviving start references| ≤ bound(n_s, n_e), on the gross energies and again on the idle-subtracted energies
  (the same energies with each run's idle-baseline power over its request removed; the bound is computed for each).
  A reference **survives** when it ran and carries no excluding run flag. Fewer than 2 survivors at the start or at
  the end, or fewer than 6 clean corpus runs, leave the screen **undefined**.
- **Drift allowance.** max(spread, bound(n_s, n_e)), where the spread is the largest minus the smallest of three
  values: the start mean, the midpoint energy and the end mean (|end mean − start mean| if the midpoint is lost).
  Each run carries half of it into its cell's bound B (§9.1), so a contrast carries it once.
- *Worked example (synthetic, gross energies only).* Clean corpus of 12: 36.42, 36.95, 36.61, 37.18, 36.80, 36.55,
  37.02, 36.71, 36.88, 36.39, 37.10, 36.67 J (s = 0.2592 J, t = 2.201). U_3 = 37.10, L_3 = 36.4533, so the envelope is
  0.6467 J; the repeatability term is 2.201 × 0.2592 × √(2/3) = 0.4659 J; bound(3, 3) = 0.6467 J. Start triplet 36.70,
  36.92, 36.58 (mean 36.7333), midpoint 37.05, end triplet 37.01, 36.84, 37.12 (mean 36.99): |36.99 − 36.7333| =
  0.2567 J ≤ 0.6467 J, the screen passes; spread = 37.05 − 36.7333 = 0.3167 J; allowance = 0.6467 J, half of it,
  0.3233 J, on each run. If the end reference at 37.12 J is lost, the screen uses (3, 2): bound = 0.6950 J, end mean
  36.925, difference 0.1917 J, passes, allowance 0.6950 J. A lost reference widens the allowance; it does not
  remove the session.

### 1.9 Hazards, flags, exclusions, counting

- **Physical hazard.** A state of the machine that would make a measured energy wrong if collection ran through it:
  the clock stepping or drifting beyond budget; running on battery or charging; thermal pressure; an outside process
  drawing power; too little free disk; the sampler not sampling; and an agent process (an AI coding assistant, which
  draws 8 to 47 W at "idle") alive on the machine.
- **Refusal.** A check that stops collection or removes data. In block 6 only a directly measured physical hazard
  refuses (doctrine of 2026-10-05).
- **Flag.** A recorded fact written beside the data (a code such as `sleep.in_run`, the run or session it concerns,
  the observed value and the evidence). A flag removes nothing by itself. The **flag catalog** gives each code one
  effect: exclude the run, exclude the session, or disclose only. §8 is the normative statement of which flags
  exclude; the catalog implements it.
- **Counting session.** A session that no physical hazard stopped and that carries no session-excluding flag (§4).
  Only counting sessions enter the registered numbers.
- **Flagged-inclusive line.** A second, labelled result printed beside each registered one, with the non-counting
  sessions that can be computed added back (§11.4). It shows what the session-level rules cost.

### 1.10 Blinding, release and the code that runs

- **Blinding.** From round 1's first t0 until the release, no person or agent reads a block-6 energy, power, phase
  duration, floor, contrast or outcome word; automation computes them into restricted files (§12).
- **Release.** The recorded moment after which the block-6 numbers may be read (§12.3).
- **Blind dry run.** The analysis programs run end to end over the real block-6 archives before the release, with
  only structure (exit codes, schema checks, refusal codes) written out.
- **Independent recompute.** The headline numbers computed again from the raw power records by code that shares
  nothing with the analysis programs (branch `lane/2026-10-14-independent-recompute`).
- **Integration branch and pinned commit.** The block-6 build lanes (branches, each building one part of the
  collection and desk code) are merged, not into the project's main
  branch, but into `integration/2026-10-14-b6-stage1`. One commit of that branch is **pinned** (§7): its hash is
  recorded, and every session runs from a **measurement checkout**, a separate clone of the repository checked out
  at that commit and used for nothing else.
- **Harvest.** The desk program that, after a session ends, reads its raw records, re-derives every check from the
  preserved bytes, writes every flag, applies the catalog and decides counting. It never decides an effect itself.

## 2. The registered design at a glance

| What | Registered | Where |
|---|---|---|
| Session shape | Block 5's, unchanged inside every run: 125 runs for ALPHA and BETA, 107 for GAMMA, 10 planned units per stratum, corpus 18 | §3 |
| What counts | No physical stop and no session-excluding flag; a structural failure of the collection code excludes, judged from structure alone | §4 |
| How many | Target 3 counting sessions per pack, minimum 2; a pack that has made 5 attempts without its target pauses and wakes the orchestrator | §5 |
| Close | 3 counting sessions in every pack, or the end of 2026-11-01 (PDT), whichever comes first | §5.3 |
| Order | Interleaved rotating rounds (A B G, B G A, G A B); GAMMA of round k takes its floors from ALPHA and BETA of round k, else the next counting session of that pack | §6 |
| Collection | From a measurement checkout at a pinned commit of `integration/2026-10-14-b6-stage1`, independent of the block-5 release | §7 |
| Exclusions | Physics refuses; a record condition is a flag; four further grounds exclude: the number is undefined, the data are not of the registered experiment, the registered drift screen, a structural failure | §8 |
| Exclusion levels | Set by one formula on non-claim data: a contamination flag excludes when its added energy reaches one quarter of F_min, the smallest floor the paper prints as estimated from non-claim data | §8.5 |
| Estimators | Block 5's four, unchanged, per counting session | §9 |
| New estimator | Between-session summary: per quantity, each counting session's value, their mean and standard deviation; no ratio, no pooled interval | §10 |
| Reporting | Block 5 and block 6 side by side under the same estimators, with their difference; "replicated" for a GAMMA contrast needs the same outcome word and the same sign of the estimate in every counting block-6 session | §11 |
| Blinding | Block-6 energies stay blinded until block 6 closes and block 5 has been released | §12 |

## 3. Session shape (decision (a))

### 3.1 The stages

Block 5's packs and plan trees (B5-REG §0.7, §5.1), with only the spare-reference retries removed (§3.2 item 4) and
nothing changed inside a run: same models, workloads, prompts, token counts, idle baseline length, cooldown rule,
settles and stage order.

```
 t0 ─ reservation ─ settle ─ OPENING CAPTURE ─ CORPUS (18 ref) ─ bound ─ START TRIPLET (3 ref) ─┐
 ┌──────────────────────────────────────────────────────────────────────────────────────────────┘
 └─ DECODE HALF ─ MIDPOINT (1 ref) ─ PREFILL HALF ─ END TRIPLET (3 ref) ─ CLOSING CAPTURE ─ exit ─► harvest
    ALPHA, BETA: each half = 10 repeats, then 10 null quads (50 runs)
    GAMMA:       each half = 5 contrast quads, 1 diagnostic ref, 5 contrast quads (41 runs)
```

Named elements: *t0* is the driver's start; *reservation* opens the session's entry in the capture list; *settle* is
a 60 s idle wait (every collection stage also begins with one); *OPENING* and *CLOSING CAPTURE* are the calibration
captures of §1.7; *CORPUS*, *START TRIPLET*, *MIDPOINT* and *END TRIPLET* are the reference runs of §1.8; *bound* is
the in-session drift-bound derivation, which decides nothing (the harvest recomputes the deciding bound); *DECODE
HALF* runs the decode workload, *PREFILL HALF* the prefill workload; *exit* is the chain's end; *harvest* runs at
the desk afterwards.

Counts: ALPHA and BETA 18 + 3 + 1 + 3 + 50 + 50 = 125 runs; GAMMA 18 + 3 + 1 + 3 + 2 + 40 + 40 = 107. Block 5
measured chains of 350 min (ALPHA), 355 min (BETA) and 291 min (GAMMA), and harvests of 45, 49 and 42 min.
*Why not shorter sessions:* two half sessions cost 46% more machine time for the same science (the fixed part,
captures, corpus and references, is paid twice), widen every interval by 2.776 / 2.262 × √(10 / 5) = 1.74 and put
every stratum on its minimum, so that one lost unit makes it undefined (design §4.2).

### 3.2 What changes around the runs (none of it inside a run)

1. **Waiting admission.** A run whose idle baseline fails admission does not abort: its sampler stream is ended,
   and a fresh baseline in a fresh stream is tried, until one passes or 1,500 s have passed since the first try
   (the cap: the longest disturbance seen in block 5, a 20-minute scan, plus one baseline, rounded up). At the cap
   the run is skipped and flagged. A session spends at most 7,200 s waiting in total; after that, a failed admission
   skips the run. Because each try starts a fresh stream, the stream of the run that is measured has block 5's
   shape (`lane/2026-10-14-b6-driver`).
2. **Pause on an agent.** When the census (a scan for agent processes every 30 s) sees one, the chain lets the run in
   flight end, pauses before the next run, and resumes 10 minutes after the last sighting with a fresh idle
   admission. The whole unit that overlapped the agent is excluded (§8.3). A pause longer than 7,200 s
   stops the session (a physical stop, §4).
3. **No sleep.** The driver holds its own no-sleep assertion (the keep-awake job stays as a second layer) and reads,
   at every run's start and end, the difference between a clock that counts sleep and one that does not.
4. **No spare references.** Block 5's spare runs for lost references are removed (they left no record in 2 of 2 live
   uses); a lost reference is a flag and the screen runs on the survivors (§1.8).
5. **The opening capture is not a screen.** A capture above the acceptance's alignment reference (block 5: 36.46 ms;
   block 6: 37.05 ms, §3.3) is a flag, and its value is carried into b_op, so the session prints a larger floor instead of stopping. The one
   stop is the line of §8.6 on b_op. At the opening capture, whose value is written b_pre, the chain stops when
   b_pre + s_bracket is above the line, because b_op can then only be larger. The alignment reference never sets a
   capture's disposition, on any path: when the session's plan record cannot be read, the comparison is recorded as a
   flag beside a records flag saying so, and the capture stays valid. *Derivation:* the reference is the largest of
   the captures it was derived from (24 for block 5, 13 for block 6), so an unchanged instrument exceeds it in 1
   capture in 25 (block 5) or 1 in 14 (block 6) by construction, and 2 of the 7 rehearsal captures exceed either
   (48.01 and 40.14 ms); each ms above it is carried into b_op at 0.047 J per ms on a prefill (0.18% of
   its 26.1 J).
6. **Before t0** (process, not data): a pre-session check measures the physical hazards and computes, by the same
   function the harvest uses, whether the session would certainly be excluded; if so, it does not start. A short
   smoke session runs only when the session's fingerprint (code commit, OS build, model file hashes, boot, meter
   device, sampler version, pack) differs from the last passing smoke. Neither produces claim data.

### 3.3 Calibration acceptance and capture list

The **calibration acceptance** is the file that fixes three constants: the alignment reference (a flag level), the
bracket minimum s_bracket (an input to b_op) and the drift budget (a flag level). Block 6 uses a **fresh acceptance**
derived, by the derivation that produced block 5's (B5-REG §0.11), from quiet-machine captures taken after Ed's
restart and before round 1 (S-4):

- **File:** `configs/b6/registration/acceptance.json` (schema `joulewise.b6_acceptance_registration.v1`, SHA-256
  `ea130c87ece4e8b557a6357f1f75df045b5a0a738db18fe5ee990a7b539ce2a8`, branch `reg/2026-10-17-b6-acceptance`; one file
  serves all three packs).
- **Corpus:** the 13 quiet-condition captures of the quiet-machine kit, each its own stored fiducial bound: M1's 10
  quiet captures (27.38 to 37.05 ms) and M13's 3 (29.83 to 33.54 ms). Each was refit from its raw records by the
  block-6 reader (`joulewise.b6.calibration.read_own_capture`: valid, refit equal to the stored value), each has a
  bounded clock anchor and 59 of 59 pulses, and battery current stayed between −21 and 0 mA. 13 meets the corpus
  minimum of 12 of block 5's derivation (revision six); M1's 10 alone would not. Left out: M1's 4 captures under one
  busy core and its 4 in the throttled launch context (2 of which failed pulse detection), which are deliberate
  disturbances, not the quiet machine.
- **Alignment reference** = the largest corpus value, quantized to 10⁻¹⁵ s: **37.054941476587 ms** (M1 capture-011;
  block 5: 36.462861644980 ms).
- **s_bracket** = the larger of the corpus range quantized to 1 µs and the D-125 floor 10.818 ms: range 37.0549 −
  27.3802 = 9.6748 ms → 9.675 ms, so **s_bracket = 10.818 ms** (the floor binds; block 5: 14.531 ms, its range).
- **Drift budget** = the larger of the predecessor's budget (block 5's 15.50217418713139 ms), the corpus's two-draw
  99% prediction t(0.995, 12) × s × √2 = 3.0545 × 2.8083 ms × 1.4142 = 12.131 ms, s_bracket, and the within-test
  prediction t(0.995, 11) × s_within × √2 = 12.816 ms: **15.50217418713139 ms** (the predecessor binds).
- *Size and replay.* s_bracket is the only one of the three that enters a number (b_op, §1.7); it is 3.713 ms below
  block 5's, which lowers b_op by up to 3.713 ms, 0.175 J of floor at 0.047 J per ms on a 1.7B prefill, whenever the
  two captures differ by less than 10.818 ms. Over the 4 non-claim rehearsal sessions it gives b_op 41.3, 41.4 and
  51.0 ms (was 45.0, 45.1 and 54.7) and, for the session stopped at its opening capture, b_pre + s_bracket = 58.8 ms
  (was 62.5) against the 139 ms line: 0 of 4 stopped. The reference and the budget only flag: 2 of 7 rehearsal
  captures exceed the reference, 0 of 3 rehearsal brackets exceed the budget.
- *Cold gate, 2026-10-17: registered as filled* (§15 D31). Both judges recomputed every value above through block 5's
  issuer functions and the file's SHA-256 from `5ffbe15c4`, to the last digit. On the corpus (13 captures from one
  kit job): the one constant that enters a number, s_bracket, is set by the D-125 floor, not by the corpus. A
  24-capture corpus of the same spread (standard deviation 2.808 ms) would have an expected range of 3.895 × 2.808 =
  10.94 ms, 0.12 ms above the floor, 0.006 J at 0.047 J per ms; if the spread across days grew to block 5's 3.80 ms, a
  13-capture range would be about 3.336 × 3.80 = 12.7 ms, 1.9 ms above the floor, 0.09 J (Opus ruling e). Both are far
  inside the 1 J attribution limit. The reference and the budget only flag. The corpus coming from one job is
  disclosed. The reference is the corpus maximum quantized half-even to 10⁻¹⁵ s, so its own source capture (M1
  capture-011) sits 2.8 × 10⁻¹⁶ s above it and would flag itself; block 5's reference is built the same way, and it is a
  flag (Fable ruling e).

Each block prints its own s_bracket beside its bounds. Captures are kept
in a plain **capture list**; a session's b_op uses only its own two captures. Other sessions' captures are read
only for flags: `calibration.other_session_systematic` (another session's capture was judged systematically off by
the capture estimator) and `calibration.corpus_doubling_reached` (the captures taken since the acceptance have
reached twice the number it was derived from, block 5's trigger for deriving it again). The capture list
holds only quiet-machine and block-6 captures: no block-5 capture enters anything of block 6 before block 5's
release, because block 5's calibration values are restricted under its blinding (B5-REG §8 item 2).

## 4. What counts (decision (c), with the structural rule of design 13.1)

A session **counts** toward its pack's target when both hold:

1. no physical hazard stopped it (§8.2 row P4), and
2. it carries none of the session-excluding conditions of §8.2.

Every other session is kept: its bytes are harvested, its flags recorded, its attempt listed in the attempt
history, and, where its cells can be computed, it is printed in the flagged-inclusive line (§11.4). It does not count.

**Structural failure.** A session in which the collection code failed structurally (the chain crashed; a stage with
planned runs left none of their records while later stages ran; no capture record; no roster of runs) is excluded,
judged from structure alone before any energy is seen. Each pack's first block-6 session is examined for structure
(counts, flags, verdict words; no energy) as soon as it ends and before the next pack arms; a structural defect is
fixed before the next session of any pack. This replaces a full-length rehearsal per pack (design 13.1): the code's
count-dependent paths are exercised at the desk on full-size synthetic archives, and the first real session of each
pack carries the risk that only six hours of new code on the real machine can show.

**Harvest problems are not session losses.** A harvest that fails on bytes that are present (`HARVEST_FAULT`), or
whose source bytes changed while it read them (`records.source_changed_during_harvest`), is fixed and re-run on the
identical bytes; the session's counting is decided by the re-run.

## 5. How many sessions, attempts and the close (decision (b))

### 5.1 Target and minimum

**Target 3 counting sessions per pack; minimum 2.** With block 5's one session, 2 gives three sessions per quantity
and 3 gives four. The third round costs about 23 hours. The condition item 37 set (target 2 if disk was not solved
before this registration) does not apply: disk is solved by compressing raw sampler files about 70 times at the desk
after the harvest and the independent recompute, never during a session and never touching a capture the capture
list names.

### 5.2 Attempts

- A pack stops at 3 counting sessions; the loop skips it in later rounds.
- The same cause removing two consecutive attempts of one pack sends that pack's next spend to a two-seat consult
  (two models asked the question blind to each other, then a recorded decision) before its next attempt; the other
  packs continue. The **cause** of a non-counting attempt is the family of its session-excluding codes, or the kind
  of physical stop.
- After 5 attempts of one pack without its target, the loop pauses that pack and wakes the orchestrator. This never
  cancels the commitment of 2: the orchestrator resumes the pack once the cause is understood.

### 5.3 The close

Block 6 **closes** when every pack has 3 counting sessions, or at the end of 2026-11-01, Pacific time, whichever
comes first. No session arms with a t0 after 2026-11-01 23:59:59 PDT; a session already running then completes and
is judged like any other. A pack that closes with fewer than 3 counting sessions is printed with its count and the
word **short**; one with fewer than 2 also says that it falls below the commitment of 2. No precision-based stopping
applies to the replication packs (design 16 item 5 is for later packs).

## 6. Order of sessions and GAMMA's floors (decision (d))

### 6.1 Rounds

Sessions run in interleaved rounds, one attempt per pack per round, with the order rotating:

```
 round 1:   ALPHA_1   BETA_1    GAMMA_1        order A B G
 round 2:   BETA_2    GAMMA_2   ALPHA_2        order B G A
 round 3:   GAMMA_3   ALPHA_3   BETA_3         order G A B
 round 4+:  the same rotation continued, skipping every pack that has its target
```

Named elements: *ALPHA_k*, *BETA_k*, *GAMMA_k* are that pack's attempt in round k; the order line is the rotation.
*Why:* a slow change of the machine over days then spreads over all three packs instead of hiding in one; a round
takes about 23.3 hours, so each pack's t0 falls at a different time of day from round to round; and GAMMA's
contrasts are judged against floors measured on the same days.

### 6.2 GAMMA's floor pairing

A GAMMA contrast is judged against a **floor gate**, the larger of the two models' detection floors (§9.2, §9.4),
so each GAMMA session needs one ALPHA session and one BETA session. For a GAMMA session of round k and each floor
pack P (ALPHA, BETA), the paired P session is:

1. P's counting session of round k, if it exists;
2. otherwise P's first counting session of a later round;
3. otherwise (no later counting session of P exists at the close) P's last counting session of an earlier round,
   and failing that, block 5's analysed session of P, labelled "floor from block 5" (`OPEN[S-17]`: this third step
   is not in the governing texts; it is proposed here and marked for the cold gate).

One floor session may serve more than one GAMMA session; each pairing is printed. Pairing depends only on which
sessions count, never on an energy. A GAMMA session's counting does not depend on its pairing.

*Worked example.* Round 1: ALPHA_1 counts, BETA_1 is stopped by a disk hazard (does not count), GAMMA_1 counts.
Round 2: BETA_2, GAMMA_2, ALPHA_2 all count. Round 3: GAMMA_3, ALPHA_3, BETA_3 all count. BETA has 2 counting
sessions, so round 4 runs BETA alone and BETA_4 counts. Pairings: GAMMA_1 with ALPHA_1 and BETA_2 (rule 2);
GAMMA_2 with ALPHA_2 and BETA_2; GAMMA_3 with ALPHA_3 and BETA_3. BETA_4 serves no GAMMA session; its own cells
and floors are printed.

## 7. Collection: a measurement checkout at a pinned commit, independent of the block-5 release

*Forcing problem.* Block 5's analysis code (lane L9, the code line that implements B5-PLAN) is still being finished
on the main branch's side, and block 5's numbers stay blinded until its release. Every block-6 science decision was
made blind (item 37), so the only thing that tied block 6 to that release was the order in which code merges into
main (item 39). Block 6 therefore runs from its own code line:

1. **Build.** The stage-1 lanes that design §17 names (harvest, driver, pre-check and smoke, desk), with the session
   loop that runs them, are merged into `integration/2026-10-14-b6-stage1` one at a time, each with an independent
   **executing review** (a reviewer that runs the code on production-shaped inputs, not only reads it), the whole test
   suite on the merged tree, and, on the code that touches measurement or the counting decision, two blind executing
   cold passes, one by Fable 5.1 and one by Opus 5.5 (two Claude models). Nothing of block 6 merges into main before
   block 5's release.
2. **Pin.** One commit of that branch is pinned: `OPEN[S-1]` (hash, date, and the record of the 40-minute machine
   test that ran on it: agent pause, an idle disturbance up to the 1,500 s cap, the meter unplugged). The pin also
   fixes the block-6 flag catalog file (`configs/b6/flag_catalog_b6.json`, digest `OPEN[S-3]`), the model and runtime
   pins (`OPEN[S-18]`) and the session deadline (block 5's, plus the 7,200 s pause limit and the 7,200 s wait budget,
   so the driver cannot kill a session that uses either; the driver lane's report names this change as blocking its
   merge, and no lane has built it yet).
3. **Measurement checkout.** Every session runs from a clone checked out at the pinned commit, with its own runs,
   custody and archive roots: `OPEN[S-2]`. None of them lies under a block-5 restricted path, and no block-6 program
   reads a block-5 restricted path before block 5's release.
4. **Code identity.** The harvest records each session's executed commit and the paths that differ from the pinned
   one. A difference in a number-bearing file (the model-runtime adapter, the sampler adapter, the reducer, the
   fiducial estimator, the controller that runs each run, the clock modules, idle admission, the bundle writer, the
   prompt-suite module, the campaign runner, the driver and the chain; the list is in the harvest lane's
   `joulewise/b6/code_check.py`) that no executing review
   covered excludes the session (`code.number_bearing_unreviewed`). A reviewed change is pinned again by a dated
   addendum; sessions after it are named as such in every printed line. Any other difference is a flag.
5. **The four estimator files are block 5's.** `joulewise/reduce.py`, `joulewise/uncertainty_evidence.py`,
   `joulewise/powermetrics_fiducial.py` and `joulewise/adapters/powermetrics.py` at the pinned commit are
   byte-identical to block 5's frozen head `a434e363d`. This is what "block 5's arithmetic unchanged" means for the
   runs themselves; the harvest refuses no session for it, but a pin that breaks it is not a block-6 pin.
6. **Before round 1** (each a precondition, recorded with its date): the quiet-machine measurements of §14 have run
   with no agent alive (the Apple media daemons came back after the restart, item 39, so each result carries their
   processor time beside it); the fresh acceptance (§3.3); the pin and the machine test; this registration through
   its cold gate and committed; and Spotify (with its helpers) not running and the orphaned test `hazard_monitor.py`
   (pid 43816, §8.5) stopped, so that the machine in the windows is the machine c_q was measured on (§15 D36). The
   last condition is recorded with its date, and the pre-session check records a flag when either program is present;
   it is not a refusal (physics refuses, everything else is a flag; their outside processor time is what
   `contention.request_overlap` already records). No session arms while a slot marked "before round 1" in §14 is open.

## 8. Which flags exclude a run or a session: the clause that protects the science

### 8.1 The rule

Only a directly measured physical hazard stops collection or removes data. Every other condition is written as a
flag and printed. Four further grounds remove data, because without them a number would be undefined or would not
be a measurement of the registered experiment:

- **N, the number is undefined:** an estimator input is missing or below the count at which the estimator exists;
- **W, wrong data:** the bytes are not of the registered model, runtime or code;
- **D, the registered drift screen:** the instrument read differently at the end of the session than at its start;
- **S, structural failure** of the collection code (§4).

Below, each excluding condition carries its ground (P for physics, or N, W, D, S) and the code that implements it
at the lane heads (`lane/2026-10-14-b6-harvest` at `83163e6a4`, `lane/2026-10-14-b6-driver` at `a1b2b59c3`). The
catalog at the pinned commit must implement exactly this section: every code it marks excluding is one listed here,
and every condition listed here has a code. A spelling that differs between lanes (for example the agent overlap,
`agent.presence` in the driver lane and `agent.unit_overlap` in the harvest lane) is reconciled at the merge; the
condition, not the spelling, is registered.

### 8.2 Session exclusions

| # | Condition | Ground | Why it protects a number | Code |
|---|---|---|---|---|
| P1 | Charging, loss of AC, or missing battery evidence during a calibration capture | P | the timing bound is measured under a different power path | `calibration.capture_battery_span`, `calibration.capture_battery_pair_failed`, `calibration.capture_battery_unmeasured` |
| P2 | A clock step inside a calibration capture | P | the capture's timing bound is then not a bound | `clock.step_overlap_calibration` |
| P3 | b_op above the stop line (S-5: 139 ms for ALPHA and GAMMA at the rehearsal sizes) | P | above it every run of the pack's smallest target phase fails its phase check, so the session cannot count (§8.6) | `calibration.operative_bound_above_stop` |
| P4 | A physical stop: sampler down more than 10 min, disk exhausted, sustained thermal emergency, the session deadline, an agent pause longer than 7,200 s | P | the session's remaining runs were not measured under the registered conditions | the chain's stop record (`chain.stop` with its reason); kept and harvested, not counting |
| N1 | A calibration capture missing, or its pulse refit failing | N | b_op, and with it every bound B, is undefined | `calibration.bracket_incomplete` |
| N2 | Fewer than 6 clean corpus runs, or fewer than 2 surviving start or end references | N | no drift allowance, so no B and no floor | `neg8.survivor_screen_undefined` |
| N3 | Fewer than 5 kept units in any stratum of a target cell | N | the floor's guard factor and the cell's estimator are undefined below 5 | `cell.below_minimum` |
| N4 | No science runs at all | N | nothing to compute | `roster.no_science_bundles` |
| W1 | A run's model files differ from the registered files, measured directly by hash | W | another experiment was run | `model.files_differ_from_registered`; the pre-check refuses before t0 on the same hash |
| W2 | The executed runtime stack (runtime, kernel library, MLX packages, tokenizer, quantization) differs from the registered one | W | the computation measured is not the registered one | `model.stack_differs_from_registered` |
| W3 | A number-bearing file changed without an executing review | W | §7 item 4 | `code.number_bearing_unreviewed` |
| D1 | The drift screen fails on either family | D | the instrument's reading moved by more than its own repeatability allows | `neg8.survivor_screen_failed` |
| S1 | Structural failure (§4) | S | the session is not the registered procedure | `structure.chain_crashed`, `structure.missing_stage_bundles`, `structure.no_capture_records`, `structure.no_roster` |

One more code stays session-excluding in the catalog without being a session loss:
`records.source_changed_during_harvest` (bytes changed while the harvest read them) is read as "harvest again on the
same bytes" (§4).

Of block 5's 32 session-removing codes, 25 become flags in block 6 (among them the calibration acceptance and ledger
codes, the bracket screen, `clock.systematic`, the pack, code, lineage and model-identity record codes, the old
drift-screen codes (the NEG-8 bracket decision among them, §9.5 item 7), `roster.duplicate_run_id`, `whole_window.verdict_absent` and
`records.malformed_flag_exclusion_possible`); their conditions are carried by the measured or recomputed
conditions above. One block-5 session rule is dropped: on GAMMA, a lost midpoint reference no longer removes the
session (`neg8.midpoint_lost` is disclosed on every pack; design 13 item 7). Such a session's allowance uses the
start and end references only, which can understate an excursion that reverted before the end, and the contrast
prints B5-PLAN §8.1's fixed sentence for a lost midpoint.

### 8.3 Run and unit exclusions

A run removed by any of these is removed from every cell it feeds; a removed repeat removes that repeat; a removed
quad run removes its whole quad.

1. **Every run-excluding code of block 5's catalog keeps its effect** (35 of its 40), with five exceptions that
   become flags (`member.cooldown_evidence_unverified`, `instrument.binary_identity_unmeasured`,
   `records.malformed_flag_member_exclusion_possible`, `member.cooldown_cap_hit`, below, and, for round 1,
   `contention.request_overlap`, item 3). The 35 are defined in
   B5-REG §6.3, §6.4 and §6.7. In words, a
   run is removed when: its status is not succeeded; it fails strict validation (every raw file re-checked and its
   summary recomputed from them), its recomputed summary differs from the stored one, or a required file is missing,
   unreadable or doubled; its clock fit is not `bounded` (B5-REG §0.14: six conditions, among them an effective clock
   bound of at most 5 ms, unchanged; §15 D8); its token counts differ from the registered ones; its target phase fails
   the **phase checks** (at least 3 records overlap the phase, the records are regular, the timing bound is small
   against the phase length, and the attribution bound is at most a quarter of the phase energy); the GPU was not
   idle in its baseline, or its idle telemetry is missing; its configuration is not in
   the pack, or its bundle cannot be placed in the session's roster; its model identity cannot be derived; a display
   woke, the screensaver ran or Low Power Mode was on during it; or a physical hazard fell in its span: charging or
   AC lost (`battery.member_span`), a charging excursion of the battery's accumulator, battery state unmeasured, OS
   thermal level nonzero, thermal pressure in its own records, a clock step, too few or too slow records for its
   target phase, contention unmeasured (part of the request covered by no processor-time interval), its span
   unknown. Battery
   discharge alone (`battery.assist`) is disclosed, as in block 5.

   The 5 ms clock bound is kept (§15 D8). *Derivation:* it removes 1 of the 53 quiet rehearsal runs of 2026-10-09
   (m = 5.64 ms, 5.39 ms of it placement, in a fit that is unresolved and so not bounded in any case), 0 of the 24
   runs of 2026-10-06 and 2 of block 5's 520, and 5 ms is 0.21 J at one edge of a 42 W prefill (0.8%), so keeping it
   costs almost nothing and keeps block 6 like for like with block 5.

   A cooldown that reaches its 300 s cap (`member.cooldown_cap_hit`) is disclosed only. The 300 s stays as a time cap
   on the wait, the cooldown's release at twice the previous run's baseline now sets only how long the machine waits,
   and the next run's own waiting admission (§3.2 item 1, p95 at most 1.0 W) decides whether that run is measured.
   *Derivation:* the cap was hit in 0 of 43 cooldowns on 2026-10-09 and 1 of 49 across the rehearsals (an agent was
   alive in that one), and the release level, twice a baseline of about 0.07 W, is a 0.07 W excess worth about
   0.15 J over a 1.99 s decode, a third of the 0.475 J exclusion size of §8.5, while the admission measures the same
   hazard directly.
2. **New in block 6** (physics, measured):
   - the machine slept more than 1 ms during the run (`sleep.in_run`; a session with no sleep reads 2.5 µs, so the
     line is 400 times the quiet reading);
   - the run's unit overlapped an agent's presence (whole unit; `agent.presence`, `agent.presence_overlap`);
   - the run was skipped at the 1,500 s wait cap or by the exhausted wait budget (`idle.wait_cap_skip`,
     `idle.wait_budget_skip`).
3. **Contamination by outside power, at levels set by §8.5:**
   - outside processor work in the run's request (`contention.request_overlap`): **a recorded flag for round 1, not
     an exclusion** (cold gate of 2026-10-17, §15 D34). M4 measured w = 5.432 J per CPU-s and c_q is 0.54 CPU-s per
     interval (S-8), so the registered rule would exclude a run when its excess C − k × 0.54 reaches 0.475 / 5.432 =
     0.0874 CPU-s. That line is about a fifth of the bottom decile of the quiet machine's own outside time per 10 s
     interval (10th to 90th percentile 0.41 to 1.60 CPU-s), and on replay it removes 14 of the 53 known-good quiet
     runs of 2026-10-09 (12 at c_q = 0.72), which §8.7 item 1 forbids. Each cell prints the registered rule's result
     beside it as a labelled alternative, with the flagged runs' C, k, C − k × c_q and E_add (§8.5). The catalog
     already has the code as DISCLOSE; the code that computes E_add is owed before the analysis release (S-14), not
     before round 1;
   - outside graphics-processor or neural-engine power that processor time does not show (a new code, not yet
     built): excluded at the §8.5 level P*, set per pack and phase (S-9);
   - a run admitted after waiting (`idle.waited`): excluded only when M2's measured shift reaches the §8.5 level,
     otherwise disclosed; the cells are printed with and without waited runs either way (§9.5 item 8). M2 measured
     d = +0.180 J (S-6), 38% of 0.475 J, so `idle.waited` is disclosed only (registered by the cold gate of
     2026-10-17, §15 D32; why M2's capped long arm qualifies is in §8.5).

### 8.4 Everything else is a flag

Every other code in the catalog is disclosed only. A code the catalog does not list is recorded as
`catalog.code_unclassified`, blocks nothing during collection, and is classified blind (from its definition and
emitter, reading no energy) before the release. The flags new in block 6 that the paper prints include: a capture
above the alignment reference (`calibration.alignment_above_reference`); capture-to-capture movement above the drift
budget (`calibration.drift_above_budget`); other sessions' captures (`calibration.other_session_*`); the idle
busy-fraction test (`idle.busy_fraction_exceeded`; 13 of 53 quiet rehearsal baselines fail it while their power is
only 0.17 to 0.42 W against the 1.0 W limit); lost references and a lost midpoint; the query-only time-server offset before and after
each session (`clock.time_server_offset`, recorded with no threshold; M9 measured one query's scatter, after a
linear trend is removed, as 0.669 ms for time.apple.com, 95% interval 0.452 to 1.282 ms, and 0.313 ms for
time.cloudflare.com, 0.212 to 0.600 ms; this file sets no threshold from it);
a run whose phase duration lies more than three standard deviations from its cell's (`member.duration_outlier`,
threshold note §8.2 item 1: a slowed model adds its own power for the extra time; the code is classified, its
emitter not yet built); a cooldown that hit its 300 s cap (`member.cooldown_cap_hit`, §8.3 item 1); a pre-check
clock rate between block 5's line and the hold (`clock.rate_above_budget`, §8.6); a wall-meter idle step the
conversions do not explain (`meter.unexplained_idle_step`, §8.5); sleep between runs; a changed fingerprint; and the
code-identity and model-identity records.

### 8.5 The formula that sets flag-to-exclusion levels, on non-claim data

*Forcing problem.* A contamination flag (another process, a graphics contender, a long wait before the run) adds
energy to a run that the run's workload did not spend. Block 5 drew such lines from a fixed proxy (5% of one CPU core
per process) with no stated size in joules. Block 6 sizes every such line by what it does to the smallest number the
paper prints, and draws it from measurements on non-claim data only, never from block 5's results (design 13 item 2).

**The rule.** For a contamination flag of kind k on a run, let E_add be the largest energy the contamination can
have added to the run's target phase, computed from the flag's own measured quantity and a conversion measured on the
quiet machine. The run is **excluded** when

    E_add ≥ F_min / 4,

where F_min is the smallest floor the paper prints, estimated from non-claim data: `OPEN[S-10]`, proposed 1.9 J,
the decode attribution floor of Qwen3-1.7B at block 3's operative bound of 45.7 ms (45.7 ms × 0.041 J per ms;
threshold note §1, from the 53-run quiet-machine rehearsal of 2026-10-09, a non-claim session). F_min is fixed once,
before round 1, and never revised after a block-6 session's t0. With the proposed value, F_min / 4 = 0.475 J.

The rule applies to energy added from outside the run's own workload. It does not apply to the run's own duration or
energy, whose variation is the scatter the estimators measure; a duration outlier stays a flag (§8.4).

| Kind | Measured quantity | E_add | Conversion, and the slot that fills it |
|---|---|---|---|
| Outside processor work | C, the outside processes' CPU-seconds in the k 10 s monitor intervals that overlap the run's request: the monitor's `outside_total`, summed from its per-process (ps) listing over every process except the measurement's own and `kernel_task` (not the host's total CPU-tick count, which reads about 2.7 times larger) | w × max(0, C − k × c_q), where c_q is the median outside CPU-seconds per interval on the quiet machine, assuming the worst placement for the excess: all of it inside the phase | w, joules per outside CPU-second, the largest over M4's burst placements and priorities: **w = 5.432 J per CPU-s** (S-8); c_q was 0.52 CPU-s on the 2026-10-09 rehearsal (its agent processes left out, §8.7 item 1) and is replaced by the median over the quiet-machine measurement sessions, with Spotify and the orphaned test process removed: **c_q = 0.54 CPU-s** (derivation below). The registered line, C − k × c_q ≥ F_min / (4w) = 0.475 / 5.432 = 0.0874 CPU-s, **is not adopted for round 1**: it removes 14 of 53 known-good quiet runs (derivation below), so `contention.request_overlap` stays a recorded flag and the line's result is printed beside each cell as a labelled alternative |
| Outside GPU or ANE power | P_x, GPU plus ANE rail power in the run's idle baseline | P_x × T_phase, where T_phase is the length of the run's own target phase for its pack in the pack's non-claim smoke runs (the longest, if they differ) | T_phase per pack and phase: `OPEN[S-11]`, from each pack's first smoke; the line is P* = F_min / (4 T_phase) (S-9); M5 confirms the rail sees the contender: a graphics contender adds 1.25 to 7.58 W on the GPU rail, a CPU-only one adds 5.10 to 5.38 W on the CPU rail and at most 0.14 mW on the GPU rail, and the idle GPU rail reads 0.19 mW (standard deviation 1.59 mW) |
| Waiting before the run | Whether the run was admitted after a wait | d, M2's point estimate of the shift: the mean of 10 reference runs after a long, disturbed wait minus the mean of 10 after an ordinary idle baseline, alternated (the arms as M2 ran them are described below) | S-6: when \|d\| ≥ F_min / 4 every waited run is excluded; otherwise `idle.waited` is disclosed only; either way the cells are printed with and without waited runs (§9.5 item 8). **Measured: d = +0.180 J** on the reference workload's prefill and +0.009 J on its decode (+0.193 J summed over all phases of the request; the bundles' recorded request energy, `energy_request_j`, gives +0.195 J), each below 0.475 J: `idle.waited` is disclosed only |

*Derivation of each row* (replays on the non-claim rehearsals of 2026-10-06 and 2026-10-09, §8.7 item 1):

- *Outside processor work:* the drafted form w × C charged the quiet machine's own background (median 0.52 CPU-s per
  interval) 1.04 J at w = 2 and excluded 46 of the 53 quiet 2026-10-09 runs (77 of 77 rehearsal runs in the second
  seat's replay), while outside processor time measurably added at most 0.03 J per CPU-second to 25 identical
  reference runs (the 2026-10-17 fits, with their uncertainties, are under "Why the exclusion is not adopted"
  below; two of which overlapped about 20 CPU-s each and stayed within one standard deviation of the
  others), so only the excess over the quiet level is charged, which excludes 12 of the 53 at w = 2 and 3 at
  w = 0.17 and is exactly 0.475 J at the line.
- *Outside GPU or ANE power:* contender power adds energy only during the run's own phase, and the rails' quiet GPU
  plus ANE power (0.2 mW median, 1.3 mW at most over the 53 baselines) is about a fiftieth of the lowest line, so the
  quiet level M5 was to subtract is dropped; 0 of 77 rehearsal runs are excluded, and P* × T_phase = 0.475 J by
  construction.
- *Waiting:* in 20,000 simulated M2 trials with no true shift and 0.40 J scatter, the drafted rule (exclude unless
  the upper end of the 95% interval of the shift lies below 0.475 J) excluded every waited run in 28.8% of trials and
  the point rule in 0.8%, while the point rule catches a true 0.475 J shift in 50% of trials and a 0.7 J shift in
  90%; no waited run exists in any replay yet, the rehearsals having run on the old abort rule.

*The measured values (quiet-machine kit, 2026-10-16/17; arithmetic in DERIVATION.md):*

- **w (S-8) = 5.432 J per outside CPU-second.** M4 ran 20 bursts of one busy core at full duty and interactive
  priority, 0.62 s and 2.0 s long, each at five placements inside a 10 s accounting interval, twice. For each burst,
  w_i = the energy it added (rail energy above the bracketing idle level, from 0.5 s before the burst to 1.0 s after)
  ÷ its true CPU-seconds. The 20 values lie between 4.213 and 5.432; the largest is the first 0.62 s burst of the
  second set (3.578 J ÷ 0.6587 CPU-s). The priority arms of M4 (steady loads at 5, 20 and 100% of one core) give
  0.086 ± 0.011 J per CPU-s at background priority and 4.969 ± 0.015 at interactive priority at full duty; the
  low-duty arms are either unresolved (background 5% and 20%: 1.29 ± 2.30 and 2.02 ± 1.47) or flagged because
  `mediaanalysisd` or `photoanalysisd` ran during them (interactive 5% and 20%: 19.33 ± 3.66 and 1.50 ± 0.29; in the
  5% arm the outside processes' CPU rose by 0.154 CPU-s/s, 30 times the load's own 0.0052), so neither sets w. The
  line on the excess is 0.475 / 5.432 = 0.0874 CPU-s, and E_add is exactly 0.475 J at it. *Cold gate, 2026-10-17:*
  w = 5.432 registered as the measured value (both rulings). The interactive 5% arm's 19.33 is not a candidate: it is
  a steady arm, not a burst, and its power step belongs to the outside daemons, not to the load; M14's one-core loads
  read 5.21 and 5.42 W on the rails for a full core, the scale of 5.432, not of 19.33.
- **c_q = 0.54 CPU-s per 10 s interval, governing** (cold gate, 2026-10-17; §15 D35). The registered definition is
  the median of the ps-listed outside total over the quiet-machine measurement sessions' accounting intervals of 9 to
  11 s. The pool is every such interval the kit recorded, 2,965 (M2's long waits 2,391, M4 122, M5 98, M10 228, M14
  126), rebuilt from the raw ps snapshot pairs and M2's interval records (Opus ruling, "c_q"). The kit's outside total
  excludes the kit's own processes as the monitor excludes the measurement's own, and `ps` does not list
  `kernel_task`, so it is the quantity C is. Counting every listed process, the median is **0.72 CPU-s, printed beside
  0.54 as the as-measured value**. It includes two programs that will not be in a window: Spotify (its GPU helper
  alone drew 0.128 CPU-s in every interval) and an orphaned test `hazard_monitor.py` (pid 43816, started 2026-10-15
  09:41 from a scratch directory of the `JouleWise-wt-b6-s3cold-fix` worktree, parent 1, still alive on 2026-10-17;
  0.056 CPU-s per interval). c_q is the quiet machine's own background, a user program in a window is outside work the
  flag exists to show, and both programs are stopped before round 1 (§7 item 6); removing Spotify, Spotify Helper and
  pid 43816 from every interval gives **0.54**. *Check:* the 2026-10-09 rehearsal's journals list Spotify in 0 of 852
  intervals and give 0.52, 0.02 CPU-s (0.11 J at w = 5.432) from 0.54. *Size:* 0.72 − 0.54 = 0.18 CPU-s per
  interval, 0.98 J at w = 5.432 on a flag-only quantity; it removes no run under the governing flag and moves the
  labelled alternative's count from 36 to 38 of 77. The draft's earlier 0.73 pooled only the 2,477 intervals stored
  in M2's and M4's result files; the Fable ruling's 0.55 removed the same programs from that narrower pool; 0.55
  against 0.54 is 0.01 CPU-s, 0.05 J at w = 5.432.
- **Replay of the registered outside-processor rule** (same 77 rehearsal runs and monitor journals as above, agent
  processes left out of C; both rulings reproduced every count; the two 2026-10-06 sessions had an agent and a busy
  `fseventsd`, median 4.2 and 5.9 outside CPU-s per interval):

  | w (J per CPU-s) | c_q (CPU-s) | 2026-10-09, 53 quiet | 2026-10-06 alpha-1, 13 | 2026-10-06 gamma-2, 11 | all 77 |
  |---|---|---|---|---|---|
  | 5.432 | 0.72 | 12 | 13 | 11 | 36 |
  | 5.432 | 0.54 | 14 | 13 | 11 | 38 |
  | 0.0862 | 0.72 or 0.54 | 2 | 4 | 8 | 14 |
  | flag only (governs for round 1) | — | 0 | 0 | 0 | 0 |

- **Why the exclusion is not adopted for round 1** (cold gate, 2026-10-17, both rulings, ruling a; §15 D34). (1) The
  line, 0.0874 CPU-s of excess, is about a fifth of the 10th percentile of the quiet machine's own outside time per
  interval (10th to 90th percentile 0.41 to 1.60 CPU-s over the 2,965 kit intervals, Opus ruling; 0.44 to 1.82 over
  2,496, Fable ruling §4.4), so it fires on the interval-to-interval scatter of C, not on contamination. (2) The
  known-good data show no dependence of energy on outside CPU: on the 33 reference runs of 2026-10-09, phase energy
  regressed on C gives −0.09 ± 0.09 J per CPU-s at prefill and −0.29 ± 0.31 at decode (Fable ruling §4.5; on the session's
  25 reference-corpus runs, −0.0006 ± 0.014 and +0.0057 ± 0.0083, Opus ruling). The two runs with about 20 outside CPU-s (refcorpus r01,
  k = 2, and r03, k = 1) read 11.11 and 11.44 J at prefill and 25.70 and 25.58 J at decode against their 23 siblings'
  11.26 ± 0.38 and 25.50 ± 0.22 J, where w = 5.432 predicts 104 and 107 J added (5.432 × (C − k × 0.54)). w = 5.432 is
  the cost of a performance core at full clock and interactive priority; the quiet machine's daemons run on efficiency
  cores at background priority (M4's in-situ daemon fit, 0.17 ± 0.06 J per CPU-s). (3) The rule would remove 12 to 14
  of 53 known-good quiet runs, which §8.7 item 1 forbids.
- **Background-priority w rejected as the governing value.** M4's one resolved background arm, w = 0.0862 ± 0.0106 J
  per CPU-s (line 0.475 / 0.0862 = 5.51 CPU-s of excess), is not an upper bound for interactive outside work, which
  costs 5.432 / 0.0862 = 63 times more, and it still removes 2 of the 53 known-good quiet runs (r01 and r03, where it
  predicts 1.65 and 1.69 J added and the runs show none). It may be printed beside the registered alternative as a
  second labelled line (Fable ruling a).
- **What is printed.** Beside every cell, a labelled line "registered outside-processor rule (w = 5.432 J per CPU-s,
  c_q = 0.54 CPU-s)" with that rule's exclusions applied and its exclusion count, and for each flagged run C, k,
  C − k × c_q and E_add = 5.432 × max(0, C − k × 0.54). The monitor's contention journals are collected in every
  session whatever the disposition, so the code that computes E_add is owed before the analysis release (S-14), not
  before round 1. What would qualify an exclusion later (both rulings): a conversion measured for outside work as it
  occurs on the quiet machine (for example an in-situ fit on quiet reference runs) whose replay removes 0 of the 53
  known-good quiet runs; such a change follows §12.4.
- **d (S-6) = +0.180 J, registered** (cold gate, 2026-10-17; §15 D32). *What M2 measured.* Five quads of the
  reference workload in the order ordinary, long, long, ordinary, every run through the same code path. Ordinary arm:
  the run's usual idle baseline, delivered as 74.9 to 75.2 s (the bundles' `idle_baseline_delivered_s`), not the 85 s
  the plan named. Long arm: the kit waited for 20 continuous quiet minutes, restarting the count whenever an outside
  process exceeded 0.05 CPU-s/s, up to a 2,700 s cap, then took a 75 s baseline and ran; in 8 of the 10 long runs the
  cap came first (7 to 24 restarts, longest quiet stretch 149 to 993 s), so those runs waited 2,700 s through
  intermittent outside work, and the other 2 reached 20 quiet minutes. All 20 bundles' clock anchors read `unknown`
  (`clock_fit_span_insufficient`), so both arms were placed on the same fallback timeline. d = mean of the 10 long
  runs − mean of the 10 ordinary runs: prefill 7.8460 − 7.6657 = +0.1803 J (95% interval −0.008 to +0.368 J,
  t(0.975, 4) = 2.776 on the five quad differences, standard error 0.068 J), decode 15.9661 − 15.9572 = +0.0089 J
  (−0.156 to +0.174), +0.193 J summed over all phases of the request (the bundles' recorded `energy_request_j`
  gives +0.195 J). Each |d| is below 0.475 J (prefill is 38% of it, and the upper end of its interval, 0.368 J, is
  78%), so waited runs are disclosed only. No waited run exists in any replay, so 0 runs are removed either way.
  *Why d qualifies* (both rulings, ruling c). A block-6 waited run is a run admitted after up to 1,500 s of
  intermittent disturbance and one passing baseline (§3.2 item 1). A capped, interrupted wait followed by a passing
  baseline is the closest measured analogue of that run; an arm with 20 continuous quiet minutes would have measured a
  cleaner machine than block 6 will deliver. The fallback timeline and the caps act on both arms of every quad alike,
  and the paired differences carry the placement scatter they add. The proportional carry of D26 (+2.35% of the 1.7B
  prefill-p2048's 26.1 J = 0.61 J) is not the rule's reading: the rule reads d in joules on the reference workload,
  the transfer is unmeasured (a constant power offset, 0.180 J over the reference prefill's 0.30 s = 0.6 W, gives
  0.6 W × 0.62 s = 0.37 J on the 1.7B prefill; a fixed cost gives 0.18 J), and the carry's own interval,
  26.1 J × (−0.10% to +4.81%) = −0.03 to +1.25 J, includes zero. The cells with and without waited runs (§9.5 item 8)
  are printed either way.

The wall meter excludes nothing. The printed number is the sum of the rails, so power the rails do not see cannot
bias it, and power they do see is judged by the two rows above; where the meter's idle-power step (M14) shows outside
power that the conversions miss, the run carries `meter.unexplained_idle_step` and the cross-check is printed
(S-12). *Derivation:* the whole machine's idle power (its own system-power reading, SMC key PSTR) varies by 0.27 W
(one standard deviation) across the 53 baselines of 2026-10-09, more than the 0.24 W graphics line a larger-of rule
would have governed, so that rule would exclude on meter noise, and a 0.1 W unexplained step is 0.062 J over a
0.62 s prefill. *M14, the printed cross-check (S-12):* steps of a known load, each bracketed by idle, seen at the
meter (DC input) and on the rails, two repeats each: graphics load at 5% duty, meter 4.20 and 3.96 W, rails 1.48 and
1.40 W (rails / meter 0.353 and 0.353); graphics at 20%, meter 20.15 and 19.08 W, rails 7.65 and 7.33 W (0.380,
0.384); one core at 100%, meter 9.41 and 8.87 W, rails 5.42 and 5.21 W (0.576, 0.587); one core at 20%, meter 0.070
and 0.041 W (standard error 0.022), rails 0.030 and 0.007 W (0.015), unresolved. The meter's idle sample scatter is
0.97 to 1.31 W (one standard deviation) over its 10 idle segments. M10 over steady levels: meter = 2.650 × rails +
1.632 W (95% interval of the slope 2.596 to 2.704). So a load the rails see as 1 W shows as about 1.7 to 2.8 W at the
meter, and the meter sees every tested load the rails see. Below its exclusion line, outside processor work is still
recorded as a flag when one process exceeds 0.05 CPU-s/s in an interval, block 5's old exclusion line; the
pre-session contention hazard (no outside process above 5% of one core for 180 s, §8.6) is unchanged.

*Worked example, with the real rehearsal sizes.* An agent at its lowest measured draw, 8 W, over a 0.62 s prefill
adds 8 × 0.62 = 4.96 J, ten times 0.475 J: excluded, which is why §8.3 removes the whole unit an agent overlaps. A
10 W graphics contender adds 6.2 J to the same prefill and 19.9 J to a 1.99 s decode: excluded. For the 1.7B pack
the graphics lines are P* = 0.475 / 0.62 = 0.77 W for prefill runs and 0.475 / 1.99 = 0.24 W for decode runs. A run
whose request overlaps two monitor intervals holding C = 1.54 outside CPU-s has an excess of 1.54 − 2 × 0.54 =
0.46 CPU-s: at the registered w = 5.432 J per CPU-second, E_add = 2.50 J, above 0.475 J, so the labelled alternative
removes it; under the governing flag (round 1) it is kept, flagged, and printed with C = 1.54, k = 2, excess 0.46
and E_add 2.50 J (0.040 J at w = 0.0862).

### 8.6 Refusal and stop lines set by the quiet-machine measurements

| Slot | Line | What sets it | Rule for reading the measurement |
|---|---|---|---|
| `S-5`, decided 2026-10-15 | The one stop on b_op (§8.2 P3; at the opening capture, b_pre + s_bracket above it stops the chain) | The pack's smallest target-phase energy and the energy per ms of timing bound at its edges, from the pack's non-claim smoke sizes (filled with S-11) | The line is the b_op at which the attribution bound of the pack's smallest target phase reaches a quarter of its energy, the phase check of §8.3 item 1: for ALPHA and GAMMA, whose smallest target phase is the Qwen3-1.7B prefill, 0.25 × 26.1 J = 6.5 J at 0.047 J per ms, 139 ms at the rehearsal sizes. Captures in the faulty launch context of September (records of 244 to 250 ms where 130.5 ms is normal) do not set it: the pre-check's sampler-median line (at most 150 ms, below) refuses that context directly. This replaces the threshold note's 60 ms capture line (about 92 ms on b_op, its §8). *Derivation:* every ms of b_op below the line is carried into the floor at 0.047 J per ms, and above it every run of that phase fails its phase check, so the session could not count (§8.2 N3) and the stop only saves its hours; 0 of the 4 rehearsal sessions are stopped (b_op 45.0 to 62.5 ms with block 5's s_bracket, 41.3 to 58.8 ms with block 6's, §3.3) |
| `S-6` (M2), measured 2026-10-17 | Whether a waited run is excluded; the 1,500 s cap | §8.5, waiting row: M2's point estimate d | Every waited run is excluded when \|d\| ≥ F_min / 4 = 0.475 J, otherwise `idle.waited` is disclosed only; the cells are printed with and without waited runs either way (§9.5 item 8). **Measured and registered (cold gate 2026-10-17, §15 D32): d = +0.180 J** (reference prefill, 38% of 0.475 J; decode +0.009 J; +0.193 J summed over the request's phases), so `idle.waited` is disclosed only, as the block-6 catalog already has it; replay: no waited run exists, 0 removed. M2's ordinary arm delivered baselines of about 75 s (74.9 to 75.2 s), not 85 s, and 8 of its 10 long waits reached the kit's 2,700 s cap before 20 continuous quiet minutes; such a capped, interrupted wait is the closest measured analogue of a block-6 waited run, and the proportional carry (0.61 J) is not the rule's reading and its interval includes zero (derivation in §8.5). The cap stays 1,500 s either way: it is sized by the longest disturbance, not by the energy effect |
| `S-7` (M3), measured 2026-10-17 | The clock-rate hold of the pre-check and of the arm | T_stream_max, the longest **run-level stamp span** any run can have under waiting admission: the time between the first and last paired readings of the wall clock against the hardware counter (both named below) that one run's own clock fit uses, over which a rate error accumulates into its effective clock bound m (§1.7). M3 reports it from the machine test; block 5's sizing value is 335 s, and the rehearsal runs had spans of 88.6 s median and 103 s at most. And r, the rate at which the wall clock (CLOCK_REALTIME) runs against a hardware counter nothing adjusts (CLOCK_MONOTONIC_RAW), in parts per million (ppm), over hours with automatic network time setting off | The start is held only when \|r\| > 5 ms / T_stream_max − 0.25 ppm, 14.7 ppm at 335 s: at that rate a run of the longest span exceeds the unchanged 5 ms run clock bound (§8.3 item 1) with no placement error at all, so the session would certainly be excluded (§8.7 item 3). Between block 5's line, \|r\| ≤ 1.3 ms / T_stream_max − 0.25 ppm (3.63 ppm at 335 s), and the hold, the session starts and the pre-check records `clock.rate_above_budget`; each run's own fit then decides. Block 5's 3.7 ms placement term (block 3's largest fitted placement half-width, 3.6 ms, plus 0.1 ms; a largest-value line that 2 of the 77 rehearsal runs exceed) is no longer part of the hold. The 0.25 ppm allows for a stream's rate differing from the one measured. At the hold there is one remedy, block 5's desk redraw of the clock's frequency correction (recorded, changing no energy), and then the loop wakes the orchestrator; it does not wait and retry, because with network time off the rate does not change by waiting. **Measured:** r = −4.67 × 10⁻⁷ ppm (standard error 5.19 × 10⁻⁷ ppm), the slope of CLOCK_REALTIME − CLOCK_MONOTONIC_RAW over 5,147 readings 10 s apart across 51,514 s (14.3 h) in one boot with network time off (M3; largest residual 0.028 ms): the two clocks run at the same rate. Registered by the cold gate of 2026-10-17 (§15 D33). **T_stream_max = 335 s**, carried from block 5, where it is the longest stream any `_v5` member is programmed to have (`sizing_b5.json`), which block 6 replicates unchanged; it is labelled carried, not measured: the machine test of 2026-10-16 that was to report run-level spans under waiting produced no runs (every member crashed on a smoke defect), the kit's longest sampler stream (2,292.6 s) is a kit stream and not one run's, and each waiting try starts a fresh stream (§3.2 item 1); the machine test on the pin reports the spans, and a longest span above 335 s replaces it. Hold: 5 ms / 335 s − 0.25 ppm = **14.675 ppm**; block 5's line 3.631 ppm; |r| is below both by more than 3.6 ppm, and stays below the hold for any T_stream_max under 5 ms / 0.25 ppm = 20,000 s, so the value of T_stream_max changes no decision. Over 335 s the measured rate moves a run's clock by 1.6 × 10⁻¹⁰ s, no energy. Replay: 0 of the 4 rehearsal sessions held; at 0 ppm, 1 of the 77 rehearsal runs exceeds the 5 ms run bound, by its placement alone (unchanged rule). *Derivation:* with each rehearsal run's own span, 1 of the 77 runs exceeds 5 ms at 0 ppm and at 3.17 ppm (by its 5.39 ms placement alone) and 2 do at 10 and at 20 ppm, while the machine sits at −3.17 ppm (2026-10-06) or +2.72 ppm (2026-10-09) and 0 of the 4 rehearsal sessions are held under either line; 0.1 ms over block 5's line was worth 0.004 J, and the hold's 5 ms is 0.21 J at one edge of a 42 W prefill. *Derivation of the 0.25 ppm, kept:* 306 real 60 s fits on the monitor's clock journals over 4 sessions scatter by 0.004 to 0.011 ppm, and even a worst-case ±125 µs read skew on every reading (a 6.15 ppm fit error, so 3.17 + 6.15 = 9.3 ppm) stays below the 14.7 ppm hold; 0.25 ppm × 335 s is 0.08 ms, 0.004 J |
| `S-8` (M4), measured 2026-10-17 | w, for the outside-processor exclusion line | §8.5 | The registered rule: excluded when w × max(0, C − k × c_q) ≥ F_min / 4 (§8.5). **Measured and registered (cold gate 2026-10-17, §15 D34): w = 5.432 J per CPU-s** (the largest of M4's 20 bursts), with **c_q = 0.54 CPU-s** per 10 s interval (every quiet-machine interval, Spotify and the orphaned test process removed; 0.72 with them, printed beside; §15 D35): line C − k × 0.54 ≥ 0.0874 CPU-s. **The exclusion is not adopted for round 1**: `contention.request_overlap` stays a recorded flag (0 of 77 removed), and each cell prints the registered rule's result as a labelled alternative (14 of 53 quiet 2026-10-09 runs, 38 of 77 rehearsal runs removed), with C, k, C − k × c_q and E_add per flagged run. *Reason:* the line is about a fifth of the quiet machine's own 10th-percentile outside time per interval (0.41 CPU-s); on the 2026-10-09 reference runs energy shows no dependence on outside CPU (−0.09 ± 0.09 J per CPU-s at prefill); and removing 12 to 14 of 53 known-good runs is what §8.7 item 1 forbids. Background-priority w = 0.0862 is rejected as the governing value (not an upper bound for interactive work; still removes 2 of 53) and may be printed beside. Derivation in §8.5 |
| `S-9`, decided 2026-10-15 | The graphics and neural-engine exclusion line | §8.5 | P* = F_min / (4 T_phase), per pack and phase, with T_phase from S-11: for Qwen3-1.7B at the rehearsal sizes, 0.77 W at prefill and 0.24 W at decode; the quiet-level clause is dropped (derivation in §8.5) |

The other physical lines are fixed now and are block 5's or the design's: before t0, AC attached with battery current
within 200 mA and the battery not charging, OS thermal level 0, 180 s with no outside process above 5% of one core,
an empty agent census, free disk at least the measured writes of the largest session plus 20 GiB (43 + 20 = 63 GiB)
plus the smoke's, the sampler's median interval at most 150 ms over 300 records, every capture the capture list names
present on local disk, and the model files' hashes equal to the pins. Each failed physical reading waits and is
measured again (the clock rate excepted, S-7); disk and sampler get one automatic remedy and then wake the
orchestrator. In a session: the stops of §8.2 P4.

Two pre-check readings are flags, not refusals. A single sampler interval above 200 ms among the 300 records:
*derivation:* 0 of 101 non-overlapping 300-record windows of quiet idle baselines contain one (the largest single
interval seen is 166.8 ms), the median line already refuses the faulty launch context, and a pre-check capture is
not data, so it carries no joules. Recent keyboard or mouse input (HID idle time, the time since the last such input,
below 600 s): *derivation:* it has no joule size and no replay, and every run's idle admission measures the hazard it
stands for directly.

### 8.7 The five requirements every excluding rule meets

From threshold note §9, for every condition of §8.2 and §8.3 that is new or changed in block 6:

1. **Replayed before adopted.** Each is run over every known-good non-claim archive on disk (the 2026-10-09
   rehearsals, structure only) and, after block 5's release, over block 5's three usable sessions (structure only);
   the count of runs and sessions it removes is written beside it (S-16). The rehearsal counts were taken for the
   ruling of 2026-10-15 over the 77 unblinded rehearsal runs of 2026-10-06 and 2026-10-09 and stand beside each rule
   above. The 2026-10-09 session, the source of the sizes used here for F_min, the 1.7B phase lengths, c_q and these
   counts, had a Claude Code process alive throughout, drawing 0.02 to 0.03 CPU-s/s (the 2026-10-06 sessions had
   agents alive too); its sizes stand as non-claim sizing at that load, because the measured conversion shows no
   effect on reference-run energy even at 20 outside CPU-s, and the quiet-machine measurement sessions replace them
   when they run. Block 5's counts stay open until its release (`OPEN[S-16]`). A rule that removes runs from a
   known-good session is resized or becomes a flag before round 1.
2. **Sized in joules** (§8.5, §8.6).
3. **Known before the session.** The pre-session check computes every condition that can be known before t0 by the
   same function the harvest uses, and does not start a session that would certainly be excluded.
4. **Collect, flag, decide in the analysis**: §4 and §11.4.
5. **Rehearsed on full-size data**: desk runs on full-size synthetic archives through harvest, analysis and the
   independent recompute, and the structural rule of §4 on each pack's first session.

## 9. Estimators: block 5's, unchanged, applied to each counting session

"Unchanged" means: the arithmetic of B5-PLAN sections 4 to 7 and their programs, at the analysis commit of §13
(`OPEN[S-14]`), applied to one counting session at a time (for GAMMA, with the floors of its paired sessions, §6.2).
No run, unit or cell is pooled across sessions. The worked examples below are B5-PLAN's own synthetic data,
re-executed for this draft with the repository functions at main `3bb305d7a` (`joulewise.detection_floor`), so a
reader can check both files against one set of numbers.

### 9.1 Estimator 1: reported phase energy per model and phase (B5-PLAN §4)

For a cell with n_r kept repeats (energies r) and n_b kept quads (quad means b, each the mean of its four runs):

1. Mean: m = 0.2 × mean(r) + 0.8 × mean(b). The weights are fixed by design (10 of the 50 runs are repeats, 40 are
   quad runs), not by what was kept.
2. Variance of m: V = 0.04 × s_r² / n_r + 0.64 × s_b² / n_b (sample standard deviations, divisor n − 1).
3. Half-width: h = t(0.975, min(n_r, n_b) − 1) × √V, with the exact quantile (t(0.975, 9) = 2.262157162798205,
   t(0.975, 8) = 2.306004135204166, t(0.975, 7) = 2.364624251592785).
4. Timing bounds: B = the sum of three stratified averages (0.2 × mean over kept repeats + 0.8 × mean over the runs of
   kept quads) of each run's recorded bounds: its first-kind bound (§1.7), its interpolation bound (zero for these
   traces) and half the session's drift allowance (§1.8).
5. Interval: [m − h − B, m + h + B]. Per-token value: m ÷ 512 output tokens for decode, m ÷ 2,048 prompt tokens for
   prefill. Attribution floor: the largest first-kind bound over the kept runs (§1.7), printed beside, not added.

*Worked example (synthetic).* Repeats 10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0, 9.6 J; quad means 10.4,
10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3, 10.1, 9.9 J. Repeat 6 and quads 5 and 9 were removed: n_r = 9, n_b = 8.
mean(r) = 9.96667, mean(b) = 10.175, m = 0.2 × 9.96667 + 0.8 × 10.175 = 10.13333 J (a plain mean over the 41 kept
runs would give 10.12927 J, which is why the weights are fixed). s_r = 0.18028, s_b = 0.16690, V = 0.0023730,
√V = 0.048714; 7 degrees of freedom; h = 2.364624 × 0.048714 = 0.11519 J. With B = 0.060 J the interval is
[9.9581, 10.3085] J; decode per token 10.13333 / 512 = 0.019792 J.

### 9.2 Estimator 2: detection floors (B5-PLAN §5)

*What a floor is.* In a null quad both sides run the same thing, so any difference is made by the instrument and the
machine. The floor is the largest such false difference the estimator allows: the smallest real difference it can
resolve. Six floor cells per model: decode, prefill-p42 (expected not extractable) and prefill-p2048, each in an
**absolute** form (over the kept repeats) and a **comparative** form (over the kept null-quad differences
d = (B1 + B2 − A1 − A2)/2).

- Deviations: absolute, each repeat minus the repeats' mean; comparative, the d themselves (not re-centred).
- Prediction: t × s × √(1 + 1/n), plus |mean(d)| in the comparative form, with s the sample standard deviation of the
  deviations and t from the code's table rounded to three places (2.262, 2.306, 2.365, 2.447, 2.571, 2.776 for 9 to
  4 degrees of freedom).
- Point floor: max(largest |deviation|, prediction).
- Corner widening: each value may lie anywhere within ± its timing half-width w_i; the corner-widened floor is the
  largest point floor over every corner of that box (2ⁿ corners, exact, n ≤ 16). The **operative** floor is the
  larger of the two. (For the absolute form, w_i is the largest distance of the run's phase energy from its
  unshifted value over the timing shifts of §1.7, read from its anchor-shift envelope, plus its interpolation bound,
  zero here; for the comparative form it is the shared-edge treatment of B5-PLAN §5,
  "Comparative form", in which each phase edge is shared by the quad's four runs and moves by one common amount
  within b_op.)
- Guard: × g(n), with g(n) = 1 for n ≥ 10 and √(9 / (n − 1)) for 5 ≤ n < 10 (g(9) = 1.0607, g(8) = 1.1339, g(5) =
  1.5); undefined below 5, which is why a stratum needs 5 kept units.

*Worked example (synthetic, the repeats of §9.1 with repeat 6 removed, w_i = 0.05 J on every run).* n = 9, mean
9.96667, s = 0.18028, largest |deviation| 0.36667; prediction 2.306 × 0.18028 × √(10/9) = 0.4382 J; operative
unguarded floor 0.5435 J; guarded 1.0607 × 0.5435 = 0.5765 J.

### 9.3 Estimator 3: dominance ratios (B5-PLAN §6)

For each model, phase (decode, prefill-p2048) and form, R = corner-widened unguarded floor ÷ point unguarded floor.
R ≥ 2 says that letting each value move within its timing box at least doubles the floor, so timing attribution
limits the measurement. An (ALPHA, BETA) pair has eight R and four R_cm (the comparative floors recomputed with one
shift of a common sign added to every quad, B5-PLAN §6). **Branch A** (every one of the twelve at least 2) licenses
the paper's sentence that timing attribution dominates the floor; **branch B** reports each ratio that failed. Each R
is printed with its numerator, denominator and n, labelled "point diagnostic; no interval".
In block 6 each floor session's four R per model are printed, and the branch sentence once per GAMMA pairing.
*Worked example (synthetic, all ten repeats of §9.1 with w_i = 0.05 J; and the ten null-quad differences 0.10,
−0.05, 0.20, 0.00, −0.10, 0.05, 0.15, −0.05, 0.10, 0.00 J with w_k = 0.30 J).* Absolute: point floor 0.4745 J,
corner-widened 0.5730 J, R = 1.21 (fails). Comparative: point floor 0.2692 J, corner-widened 1.0349 J, R = 3.84
(passes).

### 9.4 Estimator 4: the two GAMMA contrasts (B5-PLAN §7)

Contrasts: decode and prefill-p2048, Qwen3-1.7B (side A) against Qwen3-8B (side B), registered direction positive (8B
uses more), both primary, their two p-values corrected together by Holm's method (item 4) at α = 0.05. Over the n
kept quads of one counting GAMMA session:

1. d_k = (B1 + B2)/2 − (A1 + A2)/2; **dbar** = mean(d_k); s_d their sample standard deviation; se = s_d / √n.
2. t* = t(0.975, n − 1) rounded to three places; **metrology interval** dbar ± t* × se (no extra error term for phase
   energies).
3. D, the deterministic bound total: per quad, the A-side mean of its two runs' recorded bounds plus the B-side mean,
   averaged over kept quads and summed over the bound kinds. **Decision interval**: the metrology interval widened by
   D on both sides.
4. Test: t = dbar / se, two-sided, n − 1 degrees of freedom. Holm for two p-values p(1) ≤ p(2): adjusted
   min(1, 2 p(1)) and min(1, max(2 p(1), p(2))); rejected when the adjusted value is at most 0.05.
5. **Floor gate**: for each side, the worse of its model's absolute and comparative operative floors for that phase,
   from the paired floor session; the gate is the larger of the two sides.
6. **Outcome word**, in this precedence: `not_estimable` (a required input is missing or invalid); `not_resolvable`
   (no floor, |dbar| at most the floor gate, or the decision interval contains 0 while the metrology interval does
   not); `unresolved` (the metrology interval contains 0, or Holm does not reject); otherwise `direction_supported`,
   whose direction is the sign of dbar.
7. Leave-one-quad-out: a quad whose removal changes the sign, the floor status, the Holm decision or the outcome
   blocks the strongest claim level, **L2** (a sentence stating the contrast's direction; **L1** is an instrument
   result printed with its interval and no comparison); one that moves dbar by more than a quarter of the floor gate
   is reported. L2 also needs the outcome `direction_supported` in the registered direction (B5-PLAN §7.2).
8. Descriptive estimates beside each contrast (B5-PLAN §7.3): the 8B-to-1.7B energy ratio exp(mean of ln(B side /
   A side)) with its t interval, and dbar per token (÷ 512 or ÷ 2,048).

*Worked example (synthetic).* d_k = 3.1, 2.9, 3.3, 3.0, 2.8, 3.2, 3.1, 2.9, 3.0, 2.7 J with quad 4 removed: n = 9,
dbar = 3.0 J, s_d = 0.19365, se = 0.06455, t* = 2.306; metrology interval [2.8511, 3.1489] J; with D = 0.05 J the
decision interval is [2.8011, 3.1989] J; t = 46.5. With a floor gate of 1.2 J, |dbar| exceeds it, neither interval
contains 0, Holm rejects, dbar > 0 is the registered direction, and leaving out any one quad moves dbar by at most
0.0375 J (below 0.25 × 1.2): outcome `direction_supported`, ceiling L2.

### 9.5 Disclosures and labelled lines, per counting session

Each counting session prints B5-PLAN §8.1's disclosures (kept units and the positions of removed units; the attempt
history of the pack, now block 5's and block 6's attempts; battery, thermal, contention and clock counts; reference
drift with realised reference counts; monitor cost; the fixed sentences), with "session" for "window", and these
labelled lines, none of which changes a registered number:

1. **Load-correlated physics sensitivity line** (B5-PLAN §8.1): each estimate recomputed with the units restored that
   only thermal or contention codes removed.
2. **Battery-assist line** (B5-PLAN §8.1): each estimate also over the units with no battery-assisted run.
3. **Scaled drift allowance** (item 37, definitions of 07:53): the allowance term recomputed with the factor
   max(1, E/E_ref, T/T_ref), where E and T are the cell's estimator-1 mean and mean phase length and E_ref, T_ref the
   means over the surviving references that set the allowance; for a contrast, max(1, E_a/E_ref, E_b/E_ref, T_a/T_ref,
   T_b/T_ref) on the allowance term of D. It exists because the drift measured on a 37 J reference is added
   unscaled to larger phases, and that transfer is unmeasured (measurement M15 tests it). *Worked example
   (synthetic):* allowance term 0.49 J (half of the rehearsal's 0.98 J drift bound), E_ref = 37.0 J, T_ref = 4.0 s,
   a cell of 300 J over 9.0 s: factor
   max(1, 8.108, 2.25) = 8.108, scaled term 3.97 J.
4. **Single-step reconstruction diagnostic** (item 37): where a record straddles a phase edge, the power inside it is
   taken to step once between the neighbouring plateau levels, at the time that reproduces the record's average,
   instead of sharing the record by time; printed as m ± h with no B term, computed by the independent recompute.
   On the 2026-10-09 rehearsal (non-claim) it raised the prefill mean by 0.60 J and cut the run-to-run standard
   deviation from 0.379 J to 0.083 J.
5. **Whole-machine energy per phase** (item 37, as amended at 03:26): the wall meter's DC-input energy (50 samples a
   second) over each phase, gross, the same basis as the rail cells, summarised per model and phase with estimator
   1's arithmetic, with the rails' share of it per phase. The battery term (energy the battery supplied, read only
   once a second and absent in 38% of prefill phases) stays at request level, and a phase whose request shows the
   battery assisting the adapter is flagged. Not given for GAMMA (no repeat stratum). Boundary printed every time:
   "DC input at the USB-C port; the adapter's AC-to-DC loss is not included." Its exact definition, including how the
   meter's clock-fit residual and the alignment bound enter its uncertainty, is the one committed for block 5:
   `OPEN[S-15]`.
6. **Cross-session consistency** (B5-PLAN §8.1's cross-window check): for each counting GAMMA session and each model
   and phase, G is the mean over the GAMMA session's kept quads of that model's side mean and h_G its half-width
   (t × s / √n), F is that model's reported mean in the paired floor session and h_F its half-width h (without B);
   the line says "agree" when |G − F| ≤ √(h_G² + h_F²) and otherwise prints the difference as between-session
   variation the intervals do not cover. The line names the uncertainty it tests: "agree within the statistical
   half-widths; timing bounds B not included". *Derivation (kept):* it removes nothing (0 runs and 0 sessions on any
   replay), and adding the two timing bounds (about 4 J against a statistical 0.38 J) would make it say "agree"
   almost always and hide a real machine shift of 1 to 3 J.
7. **Block-5 codes carried**: for each block-6 session, the block-5 session-removing codes it carries, each now a
   flag, so a reader sees which block-6 sessions block 5's rules would have removed. The stored NEG-8 bracket
   decision and its `neg8_bracket_*` conditions (block 5's fixed 0.05 J bar on the largest difference between the end
   and start reference energies when each may lie anywhere in its range widened by its timing bounds) are disclosed
   only and never listed here as a carried failure; the policy file keeps the bar's bytes so that block 5's plan
   digests stay identical, packs registered after these three drop the bar, and drift is decided by the D1 screen's
   own bound (§1.8). *Derivation:* that widened difference is at least the mean width of the two ranges, so the bar
   fails every session by construction, 1 of 1 quiet session on replay (2026-10-09: 1.64 J against 0.05 J, with a
   point difference of 0.014 J and a D1 bound of 1.13 to 1.35 J).
8. **Waited runs** (§8.5, waiting row): each registered cell also computed without its waited runs, labelled, whether
   or not M2's shift excludes them.

## 10. The between-session summary (decision (f), as amended): the one new estimator

*Forcing problem.* Side by side, a reader sees four values of a quantity and needs one statement of how much they
vary from session to session, without the false precision of pooling runs from different days into one interval.

**Definition.** For each printed quantity Q (each reported mean and per-token value, attribution floor, operative
floor, dominance ratio, dbar and energy ratio, and each whole-machine per-phase value) and each pack:

- each counting session's value of Q, computed by §9 within that session; the sessions are block 5's analysed
  session and every counting block-6 session, so n = 1 + (counting block-6 sessions);
- their mean, Q̄ = (1/n) Σ Q_j;
- their sample standard deviation, s_Q = √( Σ (Q_j − Q̄)² / (n − 1) ).

Nothing else: no ratio of s_Q to any half-width, no pooled interval, no test, and no claim rests on it. It is printed
as "between-session summary (n sessions): mean, standard deviation".

*Worked example (synthetic).* ALPHA's prefill-p2048 reported mean in block 5's session: 26.10 J; in three counting
block-6 sessions: 26.31, 25.97 and 26.22 J. n = 4, mean 26.15 J, standard deviation 0.148 J. If a fourth block-6
session that did not count (say, removed by its drift screen) read 26.48 J, the flagged-inclusive summary (§11.4)
would read n = 5, mean 26.216 J, standard deviation 0.195 J, labelled as such.

## 11. Reporting

### 11.1 Side by side

The paper prints, for every quantity of §9 and each pack, block 5's value and each counting block-6 session's value,
under the same estimators, with each session's interval, kept units and flags. Beside them: the difference between
the blocks, Δ = (mean over counting block-6 sessions) − (block 5's value), and each block-6 session's own difference
from block 5; then the between-session summary of §10. *Same worked example:* the block-6 mean is 26.1667 J, so
Δ = +0.0667 J; the sessions' own differences are +0.21, −0.13 and +0.12 J.

The rules for which runs and sessions enter differ between the blocks (§8: block 6 makes record conditions flags),
and each block's own calibration acceptance sets its b_op; both facts are printed with the table, and §9.5 item 7
shows for each block-6 session the block-5 codes it carries.

### 11.2 The replication word for GAMMA (decision (e), as amended)

For each of the two contrasts: **"replicated"** means that every counting block-6 GAMMA session gives the same outcome
word as block 5's analysed GAMMA session **and** the same sign of dbar. Otherwise the contrast is **"not replicated"**,
and each session's word and sign are printed. If block 5's contrast is `not_estimable` (it has no dbar), the word
"replicated" is not used and the sessions' words are printed. If GAMMA closes short (§5.3), the sentence says
"short: k counting block-6 sessions of the 3 targeted". The flagged-inclusive sessions' words are printed beside,
and do not enter the word.

*Worked example (synthetic).* Block 5's decode contrast: `direction_supported`, dbar = +3.0 J. Block 6: +2.8 J and
+3.3 J, both `direction_supported`: **replicated**. Had a third counting session given `unresolved` with dbar = +0.9 J,
the contrast would read **not replicated** (sessions: supported +2.8, supported +3.3, unresolved +0.9), although every
sign agrees.

### 11.3 What may be said

The claim ceilings are block 5's: a reported cell is an instrument result (L1) and its interval is printed, not
tested; a contrast may reach L2 only per §9.4 in its own session. "Replicated" describes agreement of outcome words and
signs across sessions; it is not a new test and carries no new interval. Between-session statements use the summary of
§10 and say how many sessions it rests on.

### 11.4 The flagged-inclusive line

Beside every registered result, one labelled line repeats it with the non-counting sessions added back that (i) ran
the registered experiment (no W1, W2, W3 or S1 condition) and (ii) can be computed (at least 5 kept units per stratum,
a defined b_op and a defined drift screen). Session-level excluding flags (P1 to P4, D1) are ignored for it; run
exclusions still apply. Each added session is listed with its flags. It is printed as "including sessions that did not
count (n = …)" and never replaces the registered value.

## 12. Blinding until close

### 12.1 What is restricted

From round 1's first t0 until the release (§12.3), everything B5-REG §8 item 2 restricts is restricted for block 6:
energies, powers, phase durations, floors, means, ratios, dbar, outcome words, signs, calibration values, any
pass/fail derived from a science energy or phase duration (including `member.duration_outlier` and the phase check
on the attribution bound), and the three derived files that name each excluded run's codes. Released during the
block, as **structure**: the harvest verdict, counting or not, flag counts by code and family (a restricted code shown
only as "removed (restricted code)"), kept-unit counts, the drift screen's verdict word (it reads reference energies,
never a science energy), hazard measurements, and stage and run timing that is not a phase duration. The per-session
line in the next arm notice (the mail sent to Ed before each session, to which he can answer NO), the structure check
of §4 and every mail carry structure only. B5-REG §8's custody map (the list of path patterns that only automation
may read until the release) applies to block 6's roots (`OPEN[S-2]`). The hidden-offset factors of design §16 item 3
(secret multipliers applied to each pack's energies at export) are not part of the replication packs' protection; if
the exporter at the pinned commit (the program that writes each session's per-run table) applies them, they are
divided out exactly before any number is printed and change none.

### 12.2 What may happen blind

The analysis programs may be built and run blind on the real block-6 archives as sessions arrive (the blind dry run),
with only structure written out; their code is written and reviewed by models and people that have read no block-6
or block-5 energy.

### 12.3 Release

Block-6 numbers are released when all of these hold:

1. block 6 has closed (§5.3);
2. block 5's release event has happened. *Why:* block-6 values estimate the same quantities as block 5's blinded
   ones, so reading them first would unblind the block-5 analysis in all but name;
3. the blind dry run has completed over every block-6 session with no tooling refusal;
4. the independent recompute agrees with the analysis programs within the tolerance of S-13: each run's phase
   energy within 1 mJ, and every printed quantity, compared unrounded, within half a unit of its last printed digit.
   The observed agreement is printed beside the tolerance and is never used as it. The same tolerance governs the
   design draft's two other uses of "the recompute agrees" (`docs/design/block6_collection_draft.md` §14 on
   `integration/2026-10-14-b6-stage1`, lines 547 and 549: a new version of the analysis library becoming usable, and
   release per pack); where that text is silent or differs, this one governs. *Derivation:* an independent overlap sum
   over the rehearsals' raw records reproduced 154 of 154 phase energies within 7 × 10⁻¹⁵ J, so 1 mJ sits far above
   rounding (a 1 ns edge rounding at 42 W is 4.2 × 10⁻⁸ J) and far below the defects it must catch (a 1 ms edge shift
   is 0.047 J, 47 times it; a dropped record 3.4 to 5.5 J).

The release is a dated record tying the digests of this file, the catalog and every block-6 harvest record. There is
no separate cold gate (pruning list 7a decision 2, applied to block 6 as to block 5); the code that computes the
numbers has had its two executing cold passes at merge (§13).

### 12.4 Changes after round 1 starts

No change to registered arithmetic after any block-6 data exists. A rule of §8 found wrong may be changed while
block 6 is blinded, by a dated entry in §17 checked by one executing refuter; it then applies to every session, and
the result under the original rule is printed beside it. If a registered line proves too strict, the registered result
is printed with a labelled alternative beside it.

## 13. Analysis order and code

For each counting session, B5-PLAN §3.1 steps 1 to 11: strict validation and re-reduction of every kept run; the
kept units from the session's exclusions; floor extraction for each ALPHA and BETA session; per GAMMA pairing, the
aggregate floor record that combines its ALPHA and BETA floors and the dominance close-out (§9.3); per GAMMA session,
finalization (tying its inputs to the contrast manifest frozen before any collection) and the claim gate (the program
that computes each contrast and decides its outcome word, §9.4), given the paired floor sessions; the reported
energy per cell (§9.1); descriptive estimates and disclosures. Then §9.5, §10 and §11. The programs are block 5's
analysis programs (lane L9, the code line that implements B5-PLAN) at their release tag, plus the block-6 additions
(pairing, between-session summary, side-by-side table, replication word, flagged-inclusive line), written blind,
tested on synthetic fixtures and on full-size production-shaped synthetic archives through the real stage chain,
independently reviewed by executing them, and given one blind executing cold pass by Fable and one by Opus. The analysis commit is pinned before the blind dry run: `OPEN[S-14]`. Every output is
content-addressed; after the release the analysis re-runs from identical bytes and every output digest must equal the
dry run's.

## 14. Open slots

| Slot | What | Filled by | Before |
|---|---|---|---|
| S-1 | Pinned commit of `integration/2026-10-14-b6-stage1`, its date, the machine-test record | the stage-1 merges, whole suite on the merged tree, cold passes, the 40-minute machine test | round 1 |
| S-2 | Measurement checkout path; block-6 runs, custody and archive roots; capture list path; the custody map applied to them | the session loop's layout at S-1 | round 1 |
| S-3 | Digest of `configs/b6/flag_catalog_b6.json` at S-1, checked against §8 | `scripts/build_b6_flag_catalog.py --check` at S-1 | round 1 |
| S-4 | Fresh calibration acceptance: file, digest, alignment reference, s_bracket, drift budget. **Filled 2026-10-17 (§3.3):** `configs/b6/registration/acceptance.json`, SHA-256 `ea130c87…539ce2a8`; alignment reference 37.054941476587 ms; s_bracket 10.818 ms; drift budget 15.50217418713139 ms; 13 quiet captures; 0 of 4 rehearsal sessions stopped. **Registered by the cold gate of 2026-10-17** (§15 D31) | quiet-machine captures, block 5's derivation | round 1 |
| S-5 | Stop line on b_op. Decided 2026-10-15 (§8.6): the b_op at which the pack's smallest target phase reaches 25% attribution, 139 ms for ALPHA and GAMMA at the rehearsal sizes. Still open per pack: the kit ran no pack smoke and no 2,048-token prefill; BETA has no line yet (the code holds none for it). Held by the cold gate of 2026-10-17 until each pack's smoke (§15 D37) | each pack's value from its non-claim smoke sizes, with S-11 | that pack's first session |
| S-6 | M2's measured shift d; the rule is fixed (every waited run excluded when \|d\| ≥ F_min / 4, cells printed with and without waited runs). **Filled 2026-10-17 and registered by the cold gate** (§15 D32): d = +0.180 J (prefill, 38% of 0.475 J; decode +0.009 J): `idle.waited` disclosed only; 0 runs removed on replay. The proportional carry (0.61 J) is not the rule's reading (§8.5) | **M2** (threshold-note test 8, as run: 10 reference runs after the ordinary baseline, delivered as about 75 s, and 10 after a wait aimed at 20 continuous quiet minutes, 8 of which reached the kit's 2,700 s cap first; alternated in five quads) | round 1 |
| S-7 | T_stream_max (the longest run-level stamp span) and the measured clock rate; the hold rule is fixed (\|r\| > 5 ms / T_stream_max − 0.25 ppm). **Filled 2026-10-17 and registered by the cold gate** (§15 D33): r = −4.67 × 10⁻⁷ ppm over 14.3 h; T_stream_max 335 s carried from block 5 (the programmed longest stream), replaced by the machine test's longest run-level stamp span if that is longer; hold 14.675 ppm; 0 sessions held; no decision depends on T_stream_max below 20,000 s at the measured r | **M3** (machine-test run-level stamp spans; hours of CLOCK_REALTIME minus CLOCK_MONOTONIC_RAW with network time off) | round 1 |
| S-8 | w, joules per outside CPU-second; the rule is fixed (excluded when w × max(0, C − k × c_q) ≥ F_min / 4; C a flag only until w exists). **Filled 2026-10-17; cold gate:** w = 5.432 J per CPU-s registered as measured; c_q = 0.54 CPU-s (0.72 as measured with Spotify and the orphaned test process, printed beside; 2026-10-09's 0.52 the check). The exclusion is not adopted for round 1: `contention.request_overlap` stays a recorded flag, and each cell prints the registered rule's result (14 of 53 quiet rehearsal runs, 38 of 77 removed) as a labelled alternative with C, k, C − k × c_q and E_add per flagged run; the code that computes E_add is owed before the analysis release (S-14) (§8.5, §15 D34, D35) | **M4** (threshold-note test 1 with burst placements) | round 1 |
| S-9 | Line P* = F_min / (4 T_phase), per pack and phase. Decided 2026-10-15 (§8.6); the M5 quiet level is dropped. M5 (2026-10-17) confirms the GPU rail sees a graphics contender. Held by the cold gate of 2026-10-17 until each pack's smoke (§15 D37) | the values follow from S-11 (1.7B at the rehearsal sizes: 0.77 W prefill, 0.24 W decode) | that pack's first session |
| S-10 | F_min (proposed 1.9 J) | the cold gate, from non-claim data (§15 D9) | round 1 |
| S-11 | T_phase per pack and target phase, the phase's length in non-claim smoke runs (the longest, if they differ). Still open: no pack smoke has run. Not the registered source, for comparison only: M15 ran the packs' decode configurations, longest decode 1.9935 s for Qwen3-1.7B (30 runs) and 6.6009 s for Qwen3-8B (29 runs), which would give P* = 0.238 W and 0.0720 W; it ran no 2,048-token prefill. Held by the cold gate of 2026-10-17 until each pack's smoke (§15 D37) | each pack's first smoke | that pack's first session |
| S-12 | Meter cross-check of the S-8 and S-9 conversions. Decided 2026-10-15 (§8.5): the meter excludes nothing; `meter.unexplained_idle_step` is recorded and the cross-check printed. **M14 values (2026-10-17, §8.5):** rails / meter step 0.353 (graphics 5%), 0.380 to 0.384 (graphics 20%), 0.576 to 0.587 (one core); meter idle scatter 0.97 to 1.31 W. Registered by the cold gate of 2026-10-17 as a printed cross-check that excludes nothing (§15 D38) | closed; **M14** (meter idle-power step with known GPU and CPU loads) supplies the printed cross-check | — |
| S-13 | Recompute agreement tolerance for the release, the analysis-library version and per-pack release. Decided 2026-10-15 (§12.3 item 4): 1 mJ per run phase energy, and half a unit of its last printed digit for every printed quantity | closed | — |
| S-14 | Analysis commit | block 5's L9 release tag plus the block-6 additions, reviewed and cold-passed | the blind dry run |
| S-15 | Definition of whole-machine energy per phase | the commit that fixes it for block 5 | the blind dry run |
| S-16 | Replay counts beside each new or changed rule of §8 | rehearsals: done for the ruling of 2026-10-15 (2026-10-06 and 2026-10-09 archives, an agent process alive in each; §8.7 item 1); block 5's usable sessions after its release (structure only) | the block-6 release (block 5) |
| S-17 | GAMMA pairing when no later counting floor session exists (§6.2 step 3) | the cold gate | round 1 |
| S-18 | Model and runtime pins for block 6 (expected: block 5's `identity_pins.json`) | S-1 | round 1 |

Measurements that set no line here, all run 2026-10-16/17 (values for the record; none changes a rule):
M1 (10 quiet captures, median 29.48 ms, largest 37.05 ms; 4 under one busy core, 28.17 to 35.04 ms, no separation
from quiet; 4 in the throttled launch context, records about 250 ms apart, 2 of them failing pulse detection and 2
bounded at 31.05 and 44.00 ms; since 2026-10-15 they no longer set the b_op line, §8.6), M5 (the rails see a graphics
contender, §8.5), M9 (time-server query scatter 0.669 ms and 0.313 ms, §8.4), M10 (meter = 2.650 × rails + 1.632 W,
for the comparability statement), M13 (the meter's edges lag the commanded edges by 31.2 ms on average and the
sampler's by 25.2 ms, standard deviation 4.7 ms over 354 edges; the sampler's own edge lag 6.0 ms, standard deviation
11.4 ms, inside the 30 ms typical capture bound: an independent check of the alignment bound), M15 (over a 90-minute
soak the 8B decode moved by −1.26 J, standard error 0.30 J, against −0.12 J, standard error 0.36 J, for the
reference's decode and −0.01 J for the 1.7B decode; it bears on the scaled-allowance line of §9.5 item 3), and M2b (a
50 s idle baseline instead of 57.6 s shifts the reference decode by −0.139 J and prefill by −0.083 J, both intervals
containing 0).

## 15. Decisions made by the author

Marked **[cold gate]** where the choice changes which data count or a printed number.

- **D1.** One file is the registration and analysis plan of all three replication packs, because GAMMA's pairing
  ties them (design §14 asks for a registration per pack; the three are one pack family here).
- **D2.** The between-session summary includes block 5's analysed session (design §5: "with block 6 at 2 the paper has
  three independent sessions per quantity; at 3 it has four"; 13 item 4 speaks of four sessions). **[cold gate]**
- **D3.** "The difference between them" (item 37) is the block-6 mean minus block 5's value, with each session's own
  difference listed. **[cold gate]**
- **D4.** The replication word is not used when block 5's contrast has no dbar; a short GAMMA is labelled.
- **D5.** The close is read as the last t0 at 2026-11-01 23:59:59 PDT, with a running session completed. **[cold gate]**
- **D6.** Block 6 is released no earlier than block 5's release event, under the same release condition as block 5
  (7a decision 2): the reason is in §12.3 item 2.
- **D7.** No block-5 calibration capture enters block 6 before block 5's release; block 6's capture list holds only
  quiet-machine and block-6 captures (B5-REG §8 restricts calibration values).
- **D8.** The four estimator files stay byte-identical to block 5's. The council's 15 ms form of the run clock bound
  (threshold note §8.1, row T3) needs a change to `uncertainty_evidence.py`, which is one of them, and no stage-1 lane
  builds it; so condition (e) stays at 5 ms, which also keeps block 6 like for like with block 5 (it removes 1 of 53
  quiet rehearsal runs and removed 2 of block 5's 520, §8.3 item 1). The pre-check holds a start only where that 5 ms
  rule certainly bites, |r| > 5 ms / T_stream_max − 0.25 ppm (14.7 ppm at 335 s); between block 5's 3.63 ppm line
  and the hold the session starts with `clock.rate_above_budget` recorded, and at the hold the desk redraw is the one
  remedy before the orchestrator is woken (§8.6 S-7; ruling of 2026-10-15). **[cold gate]**
- **D9.** F_min is estimated from non-claim data as the decode attribution floor of the 2026-10-09 rehearsal sizes at
  block 3's operative bound, 1.9 J; the text says "the smallest floor the paper prints", which is a block-5 or block-6
  result and so cannot be used. The F5 investigation's non-claim figures agree with that size: the first-kind bounds
  stored for 22 rehearsal prefill runs ranged 0.98 to 1.72 J, so a prefill attribution floor of 1.72 J under the
  opening capture's bound and about 2 J under b_op. **[cold gate]**
- **D10.** Outside processor work is converted to added energy as w × max(0, C − k × c_q), with the worst placement
  for the excess (all of it inside the phase), since the monitor's 10 s intervals cannot place it; the quiet
  machine's own background, present in every run including those that set the floors, is not charged, and C is the
  monitor's ps-listed `outside_total` (§8.5; ruling of 2026-10-15). Until M4 measures w, C is a flag only. Block 5's
  0.05 CPU-s/s per process stays as a flag level. **[cold gate]**
- **D11.** The formula of §8.5 covers energy from outside the run's workload, not the run's own duration or energy.
- **D12.** The b_op stop line is the 25% attribution point of the pack's smallest target phase, computed per pack
  from non-claim smoke sizes, not a line read from M1's captures (§8.6 S-5; ruling of 2026-10-15). **[cold gate]**
- **D13.** M2 is read by its point estimate: every waited run is excluded when |d| ≥ F_min / 4; otherwise waiting
  is a flag; the cells are printed with and without waited runs either way (§8.5; ruling of 2026-10-15).
  **[cold gate]**
- **D14.** GAMMA pairing step 3, and one floor session serving several GAMMA sessions (§6.2). **[cold gate]**
- **D15.** The flagged-inclusive line's composition (§11.4). **[cold gate]**
- **D16.** Block 6 prints every labelled line block 5 prints (§9.5), so the side-by-side table compares like with
  like.
- **D17.** Each block-6 session lists the block-5 session-removing codes it carries (§9.5 item 7).
- **D18.** An attempt counts as made when its chain starts its first stage; a pre-check that does not start and an arm
  that refuses before any run are not attempts.
- **D19.** A rule change after round 1 starts applies to every session with the original-rule result printed beside it
  (pruning list §5, "Prospective-only removed").
- **D20.** Hidden-offset factors are not part of the replication packs' blinding (design §17 puts them in stage 2, for
  the new packs).
- **D21.** Flags derived from a science energy or a phase duration are restricted, including `member.duration_outlier`.
- **D22.** The "same cause twice" consult keys on the family of the session-excluding code or the kind of physical
  stop.
- **D23.** The graphics-contender rule uses the idle-baseline rail reading and T_phase, per pack and phase, from
  non-claim smoke runs, so the exclusion function reads no science phase duration; no quiet rail level is subtracted
  (§8.5; ruling of 2026-10-15). **[cold gate]**
- **D24.** The meter (M14) excludes nothing: where it and the rail or processor-time conversion disagree,
  `meter.unexplained_idle_step` is recorded and the cross-check printed, because power the rails do not see is not in
  the printed number (§8.5; ruling of 2026-10-15).

Added 2026-10-17 with the quiet-machine values (registration seat, Opus 5.5):

- **D25.** The fresh acceptance's corpus is every quiet-condition capture of the kit: M1's 10 and M13's 3 (13, which
  meets block 5's revision-six minimum of 12; M1's 10 alone would not). M1's captures under one busy core and in the
  throttled launch context are left out as deliberate disturbances. The within-test prediction treats M1 and M13 as
  two sessions (K = 2). The drift budget keeps block 5's lineage rule, with block 5's acceptance as the predecessor,
  so the predecessor's 15.502 ms binds; the corpus's own value, 12.816 ms, is the labelled alternative. Every corpus
  choice tried (13 with K = 2, 13 with K = 1, M1's 10) gives the same alignment reference and the same s_bracket.
  **[cold gate]** (s_bracket enters b_op).
- **D26.** M2's d is read per phase of the reference workload, in joules, unscaled, and the rule is applied to the
  larger magnitude (prefill, +0.180 J); the whole request (+0.193 J) gives the same result. The long arm is accepted
  although 8 of its 10 waits reached the kit's 2,700 s cap before 20 continuous quiet minutes. **[cold gate]**: in
  proportion the prefill shift is +2.35% (95% interval −0.10% to +4.81%); carried in proportion to the 1.7B
  prefill-p2048 phase (26.1 J at rehearsal sizes) it would be 0.61 J, above 0.475 J, which would exclude waited 1.7B
  prefill runs. The registered rule reads d in joules; the labelled cells without waited runs (§9.5 item 8) are
  printed either way. *Ruled 2026-10-17: registered with the reading of D32; the proportional carry is not adopted.*
- **D27.** w is the largest of M4's 20 burst values, 5.432 J per CPU-s; the bursts were all run at interactive
  priority, and the priority arms are reported beside it but set nothing (the low-duty arms are unresolved or flagged).
  c_q is the median over every 9 to 11 s accounting interval the kit recorded, 0.73 CPU-s, including the user programs
  that were running (without them, 0.55). The rule then excludes 12 of 53 quiet rehearsal runs (36 of 77), which
  §8.7 item 1 forbids for known-good data; the registered result is written, with the labelled alternative of w at
  background priority (0.0862 J per CPU-s: 2 of 53, 14 of 77) and the option of keeping the code a flag (0 of 77).
  The choice is the cold gate's. **[cold gate]** *Superseded 2026-10-17 by D34 (w, the flag) and D35 (c_q = 0.54).*
- **D28.** T_stream_max stays block 5's 335 s until the machine test on the pin reports run-level spans; with the
  measured r no decision depends on it below 20,000 s.
- **D29.** S-5, S-9 and S-11 stay open: their registered source is each pack's non-claim smoke, and the kit ran
  neither a smoke nor a 2,048-token prefill. M15's decode lengths are printed beside S-11 for comparison only.
- **D30.** One `acceptance.json` serves the three packs (the readers pass each session's own pack and pack root): its
  `pack_id` is the family name `b6-replication`, its `operative_bound_stop_s` is null because the packs' stop lines
  live in `joulewise.b6.capture_screen.REGISTERED_T10_STOP_S`, and its `registered_commit` is main's `3bb305d7a`, the
  base of `configs/b6/executing_reviews.json`; moving it to the pinned commit is a choice at S-1.

Added 2026-10-17 from the cold gate on the quiet-machine values. Two blind cold judges ruled:
`docs/process_traces/2026-10-17-magistrate-1a1261a5/b6-accept-ruling-fable.md` (Fable 5.1) and
`docs/process_traces/2026-10-17-magistrate-1a1261a5/b6-accept-ruling-opus.md` (Opus 5.5). Where they differ, the lead
(orchestrator, Opus 5.5) decided as follows; both judges registered D25, D28, D29 and D30 as written.

- **D31. S-4 registered as filled** (both rulings). `configs/b6/registration/acceptance.json` at `5ffbe15c4`, no
  change; the corpus of 13 captures from one job is adequate because s_bracket, the only constant that enters a
  number, is set by the D-125 floor, and the sizing of a larger or more spread corpus is 0.006 to 0.09 J (§3.3).
- **D32. S-6 registered with a change of text** (both rulings, ruling c). d = +0.180 J (prefill), 38% of 0.475 J;
  `idle.waited` disclosed only. The text now describes M2's arms as measured: the ordinary arm's baselines were about
  75 s (74.9 to 75.2 s), not 85 s, and 8 of the 10 long waits reached the kit's 2,700 s cap before 20 continuous quiet
  minutes. d still qualifies: a capped, interrupted wait followed by a passing baseline is the closest measured
  analogue of a block-6 waited run (up to 1,500 s of intermittent disturbance, §3.2 item 1), and both arms share the
  fallback timeline. The proportional carry (+2.35% × 26.1 J = 0.61 J) is not the rule's reading, and its interval
  (−0.03 to +1.25 J) includes zero (§8.5). **[cold gate, ruled]**
- **D33. S-7 registered** (both rulings, ruling d). r = −4.67 × 10⁻⁷ ppm (standard error 5.19 × 10⁻⁷). T_stream_max
  = 335 s, labelled as carried from block 5 (the longest programmed `_v5` stream), replaced by the machine test's
  longest run-level stamp span if that is longer; hold 14.675 ppm. At the measured r no decision depends on
  T_stream_max below 5 ms / 0.25 ppm = 20,000 s.
- **D34. S-8: w registered, exclusion not adopted for round 1** (both rulings, ruling a). w = 5.432 J per CPU-s is
  registered as measured. `contention.request_overlap` stays a recorded flag (DISCLOSE, as the catalog at
  `5ffbe15c4` has it). Each cell prints, as a labelled alternative, the registered rule's result (w = 5.432,
  c_q = 0.54) with its exclusions, and per flagged run C, k, C − k × c_q and E_add. Reason: the line, 0.087 CPU-s of
  excess, is a fraction of the quiet machine's own 10 s interval scatter (10th percentile 0.41 CPU-s); on the 33
  reference runs of 2026-10-09 energy shows no dependence on outside CPU (Fable's fit −0.09 ± 0.09 J per CPU-s at
  prefill); the rule would remove 12 to 14 of 53 known-good quiet runs, which §8.7 item 1 forbids. The
  background-priority w = 0.0862 is rejected as the governing value (not an upper bound for interactive work, which
  costs 63 times more; still removes 2 of 53) and may be printed beside, as the Fable ruling suggests. The code that
  computes E_add is owed before the analysis release, not before round 1. **[cold gate, ruled]**
- **D35. c_q = 0.54 CPU-s per interval governs.** It is the registered definition applied to the full pool: the
  median over every quiet-machine measurement session's 9 to 11 s intervals (2,965, the Opus ruling's raw pooling),
  with Spotify, Spotify Helper and the orphaned test hazard monitor (pid 43816) removed. 0.72 (with them) is printed
  beside it as measured; 2026-10-09's 0.52 (Spotify absent there) is the check. The Fable ruling's 0.55 came from a
  narrower pooling (the result-file intervals of M2 and M4); the 0.01 CPU-s difference is 0.05 J at w = 5.432 on a
  flag-only quantity. The draft's 0.73 is withdrawn. **[cold gate, ruled]**
- **D36. Before round 1, Spotify is not running and the orphaned hazard monitor (pid 43816) is stopped** (both
  rulings), so the windows match the c_q baseline. A recorded condition (§7 item 6) and a pre-check flag, not a new
  refusal: physics refuses, everything else is a flag.
- **D37. S-5, S-9 and S-11 held** until each pack's smoke run (both rulings).
- **D38. S-12 registered**: M14's values are a printed cross-check and exclude nothing (both rulings).

## 16. What the author read and did not read

Read: `RUN_STATE.md` items 36 to 39 on main (`3bb305d7a`); `docs/design/block6_collection_draft.md` in full;
`docs/design/next_block_threshold_proportion.md` sections 0 to 4, 8 and 9; `docs/process/pruning_list_2026-10-14.md`
sections 4, 5, 6 and 7a; B5-REG sections 0.1 to 0.17, 5.1, 6.1 to 6.7, 7 and 8; B5-PLAN in full; block 5's sealed flag
catalog (SHA-256 `5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d`) and the block-6 catalog at the
harvest lane's head; `/Users/edr/night-archive/b6-build/RESULTS.md` and the harvest, driver and precheck lane specs;
the loop lane's pack registration files; the F5 investigation's non-claim tables
(`/Users/edr/night-archive/b5-consults/threshold-council/F5-investigation.md`); `joulewise/detection_floor.py` and
`whole_window.neg8_count_adjusted_bound`, which were run on the synthetic examples. Not opened: anything under
`/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`, `/Users/edr/night-g2a/`,
`/Users/edr/night-archive/harvest-v5-b5-*` or a runs root under `/Users/edr/night-custody/measurement/`, and no pull
request body.

For the revision of 2026-10-17 the registration seat read, besides this file: every `result.json`, `summary.md` and
capture `instrument_evidence.json` under `/Users/edr/night-archive/threshold-validation/` (non-claim, no agent alive);
the kit's code at `1c1bc3204` (`joulewise/quiet_kit/analysis.py`, its guide and README); block 5's issued acceptance
file `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` and the issuer script that derived it
(both from before block 5's first window; no block-5 session capture); the block-6 readers of `acceptance.json` on
`lane/2026-10-16-b6-round2`; the non-claim rehearsal archives under `/Users/edr/night-archive/gate-prune/rehearsal-real/`
(capture bounds, run request times, monitor contention journals) and the 2026-10-15 council's replay tables. It opened
nothing under the block-5 restricted paths listed above.

## 17. Change log

- 2026-10-14: draft written (Opus 5.5, session e308c59a). Not cold-gated.
- 2026-10-15: refusal and exclusion lines sized against the instrument by the orchestrator's ruling
  (`/Users/edr/night-archive/silly-numbers-2026-10-15/council/RULING.md`); S-5, S-9, S-12 and S-13 decided; S-6,
  S-7 and S-8 keep only their measured values open (Opus 5.5). Not cold-gated.
- 2026-10-17: the quiet-machine values entered: S-4 (fresh acceptance), S-6 (d), S-7 (r; T_stream_max carried),
  S-8 (w) with c_q, M14's cross-check for S-12, and the other measurements' values; S-8's exclusion and the reading
  of d marked for the cold gate (D25 to D30). Derivation: `/Users/edr/night-archive/b6-acceptance/DERIVATION.md`
  (Opus 5.5, registration seat). Not cold-gated.
- 2026-10-17: cold gate on the quiet-machine values applied (two blind judges, Fable 5.1 and Opus 5.5; rulings copied
  to `docs/process_traces/2026-10-17-magistrate-1a1261a5/b6-accept-ruling-fable.md` and `b6-accept-ruling-opus.md`;
  the lead's decisions D31 to D38). S-4, S-7, S-12 registered; S-6 registered with M2's arms described as measured;
  S-8's w registered and its exclusion not adopted for round 1 (`contention.request_overlap` a flag, the registered
  rule printed as a labelled alternative); c_q 0.54 (was 0.73); Spotify and the orphaned hazard monitor stopped before
  round 1; S-5, S-9, S-11 held until each pack's smoke. S-10, S-17 and the rest of this file are not yet cold-gated.
