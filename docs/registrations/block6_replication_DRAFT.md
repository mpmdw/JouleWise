# Registration B6-REPL (draft): block 6, the replication of block 5's three packs

**Status: DRAFT, not cold-gated.** Written 2026-10-14 by Opus 5.5 (session e308c59a), before any block-6 data
exists and while block 5 is still blinded. The author opened no block-5 energy, power, floor, phase duration,
calibration value or outcome; the only numbers below are design figures, non-claim rehearsal figures and synthetic
worked examples, each labelled. This file is both the registration and the analysis plan of the three replication
packs. Every refusal line that the quiet-machine measurements will set is an **open slot**, written
`OPEN[S-n]`, which names the measurement or record that fills it; §14 lists them all. No number is entered in a
slot before its measurement exists.

**What happens to this draft.** The quiet-machine measurements (named M1 to M15 in section 8 of the design draft
cited below; M1 to M5 set the refusal lines, and §14 lists every one this file needs) run with no AI agent alive on
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
  14.531 ms). *Worked example (synthetic):* opening 40.0 ms, closing 30.0 ms, s_bracket 14.531 ms: b_op = 40.0 +
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
5. **The opening capture is not a screen.** A capture above the acceptance's alignment reference (block 5: 36.46 ms)
   is a flag, and its value is carried into b_op, so the session prints a larger floor instead of stopping. The one
   stop is the line of §8.6 on b_op. At the opening capture, whose value is written b_pre, the chain stops when
   b_pre + s_bracket is above the line, because b_op can then only be larger.
6. **Before t0** (process, not data): a pre-session check measures the physical hazards and computes, by the same
   function the harvest uses, whether the session would certainly be excluded; if so, it does not start. A short
   smoke session runs only when the session's fingerprint (code commit, OS build, model file hashes, boot, meter
   device, sampler version, pack) differs from the last passing smoke. Neither produces claim data.

### 3.3 Calibration acceptance and capture list

The **calibration acceptance** is the file that fixes three constants: the alignment reference (a flag level), the
bracket minimum s_bracket (an input to b_op) and the drift budget (a flag level). Block 6 uses a **fresh acceptance**
derived, by the derivation that produced block 5's (B5-REG §0.11), from quiet-machine captures taken after Ed's
restart and before round 1: `OPEN[S-4]`. Each block prints its own s_bracket beside its bounds. Captures are kept
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
   its cold gate and committed. No session arms while a slot marked "before round 1" in §14 is open.

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
| P3 | b_op above the stop line `OPEN[S-5]` | P | a sampler in a disturbed state (§8.6) | `calibration.operative_bound_above_stop` |
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
drift-screen codes, `roster.duplicate_run_id`, `whole_window.verdict_absent` and
`records.malformed_flag_exclusion_possible`); their conditions are carried by the measured or recomputed
conditions above. One block-5 session rule is dropped: on GAMMA, a lost midpoint reference no longer removes the
session (`neg8.midpoint_lost` is disclosed on every pack; design 13 item 7). Such a session's allowance uses the
start and end references only, which can understate an excursion that reverted before the end, and the contrast
prints B5-PLAN §8.1's fixed sentence for a lost midpoint.

### 8.3 Run and unit exclusions

A run removed by any of these is removed from every cell it feeds; a removed repeat removes that repeat; a removed
quad run removes its whole quad.

1. **Every run-excluding code of block 5's catalog keeps its effect** (37 of its 40), with three exceptions that
   become flags (`member.cooldown_evidence_unverified`, `instrument.binary_identity_unmeasured`,
   `records.malformed_flag_member_exclusion_possible`). The 37 are defined in B5-REG §6.3, §6.4 and §6.7. In words, a
   run is removed when: its status is not succeeded; it fails strict validation (every raw file re-checked and its
   summary recomputed from them), its recomputed summary differs from the stored one, or a required file is missing,
   unreadable or doubled; its clock fit is not `bounded` (B5-REG §0.14: six conditions, among them an effective clock
   bound of at most 5 ms, unchanged; §15 D8); its token counts differ from the registered ones; its target phase fails
   the **phase checks** (at least 3 records overlap the phase, the records are regular, the timing bound is small
   against the phase length, and the attribution bound is at most a quarter of the phase energy); the GPU was not
   idle in its baseline, its idle telemetry is missing, or its cooldown hit the 300 s cap; its configuration is not in
   the pack, or its bundle cannot be placed in the session's roster; its model identity cannot be derived; a display
   woke, the screensaver ran or Low Power Mode was on during it; or a physical hazard fell in its span: charging or
   AC lost (`battery.member_span`), a charging excursion of the battery's accumulator, battery state unmeasured, OS
   thermal level nonzero, thermal pressure in its own records, a clock step, too few or too slow records for its
   target phase, outside processor work (now sized by item 3), contention unmeasured, its span unknown. Battery
   discharge alone (`battery.assist`) is disclosed, as in block 5.
2. **New in block 6** (physics, measured):
   - the machine slept more than 1 ms during the run (`sleep.in_run`; a session with no sleep reads 2.5 µs, so the
     line is 400 times the quiet reading);
   - the run's unit overlapped an agent's presence (whole unit; `agent.presence`, `agent.presence_overlap`);
   - the run was skipped at the 1,500 s wait cap or by the exhausted wait budget (`idle.wait_cap_skip`,
     `idle.wait_budget_skip`).
3. **Contamination by outside power, at levels set by §8.5:**
   - outside processor work in the run's request (`contention.request_overlap`, its line moved from block 5's 0.05
     CPU-s/s per process): excluded at the level `OPEN[S-8]`;
   - outside graphics-processor or neural-engine power that processor time does not show (a new code, not yet
     built): excluded at the level `OPEN[S-9]`;
   - a run admitted after waiting (`idle.waited`): disclosed or excluded according to `OPEN[S-6]`.

### 8.4 Everything else is a flag

Every other code in the catalog is disclosed only. A code the catalog does not list is recorded as
`catalog.code_unclassified`, blocks nothing during collection, and is classified blind (from its definition and
emitter, reading no energy) before the release. The flags new in block 6 that the paper prints include: a capture
above the alignment reference (`calibration.alignment_above_reference`); capture-to-capture movement above the drift
budget (`calibration.drift_above_budget`); other sessions' captures (`calibration.other_session_*`); the idle
busy-fraction test (`idle.busy_fraction_exceeded`; 13 of 53 quiet rehearsal baselines fail it while their power is
only 0.17 to 0.42 W against the 1.0 W limit); lost references and a lost midpoint; the query-only time-server offset before and after
each session (`clock.time_server_offset`, recorded with no threshold until measurement M9 gives the query scatter);
a run whose phase duration lies more than three standard deviations from its cell's (`member.duration_outlier`,
threshold note §8.2 item 1: a slowed model adds its own power for the extra time; the code is classified, its
emitter not yet built); sleep between runs; a changed fingerprint; and the code-identity and model-identity records.

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
| Outside processor work | C, the outside processes' CPU-seconds (all processes except the measurement's own and `kernel_task`) in the 10 s monitor intervals that overlap the run's request | w × C, assuming the worst placement: all of it inside the phase | w, joules per outside CPU-second, the largest over M4's burst placements and priorities: `OPEN[S-8]`; the exclusion line is C* = F_min / (4w) |
| Outside GPU or ANE power | P_x, GPU plus ANE rail power in the run's idle baseline above the quiet level M5 measures | P_x × T_max(pack) | M5 (the rails in idle and in a CPU-only reference run) gives the quiet level and confirms the rail sees the contender: `OPEN[S-9]`; T_max(pack), the longest target phase of the pack in its non-claim smoke runs: `OPEN[S-11]`; the line is P* = F_min / (4 T_max) |
| Waiting before the run | Whether the run was admitted after a wait | the upper end of the 95% interval of the mean shift between runs after a 20-minute wait and after the ordinary 85 s (M2, 10 reference runs each, alternated) | `OPEN[S-6]`: if that upper end is below F_min / 4, `idle.waited` is disclosed only; otherwise every waited run is excluded |

Where the wall meter's idle-power step (M14) shows outside power that the processor-time or rail conversion misses,
the larger of the two conversions is used (`OPEN[S-12]`). Below its exclusion line, outside processor work is still
recorded as a flag when one process exceeds 0.05 CPU-s/s in an interval, block 5's old exclusion line.

*Worked example, with the real rehearsal sizes and a hypothetical conversion.* An agent at its lowest measured draw,
8 W, over a 0.62 s prefill adds 8 × 0.62 = 4.96 J, ten times 0.475 J: excluded, which is why §8.3 removes the whole
unit an agent overlaps. A 10 W graphics contender adds 6.2 J to the same prefill and 19.9 J to a 1.99 s decode:
excluded. For the 1.7B pack the longest target phase in the rehearsal is the 1.99 s decode, so its graphics line
would be P* = 0.475 / 1.99 = 0.24 W (the 0.62 s prefill alone would give 0.475 / 0.62 = 0.77 W). For outside
processor work, M4 has not run: the threshold note brackets w between under 2 J and 6 J per CPU-second (not
measured). At w = 2, C* = 0.475 / 2 = 0.24 CPU-s; at w = 6, 0.079 CPU-s.
Block 5's line was 0.05 CPU-s/s over a 10 s interval, 0.5 CPU-s per process. Under the worst-placement assumption the
block-6 line is therefore 2 to 6 times stricter than block 5's; the replay of §8.7 states how many runs of known-good
non-claim sessions it would remove before it is adopted, and §15 D10 marks the assumption for the cold gate.

### 8.6 Refusal and stop lines set by the quiet-machine measurements

| Slot | Line | What sets it | Rule for reading the measurement |
|---|---|---|---|
| `OPEN[S-5]` (M1) | The one stop on b_op (§8.2 P3; at the opening capture, b_pre + s_bracket above it stops the chain) | Captures on a quiet machine, under one busy core, and in the faulty launch context of September (records of 244 to 250 ms where 130.5 ms is normal); and how often an ordinary capture exceeds the alignment reference | The line lies above the largest b_op that pairs of quiet-machine captures give and below the smallest b_op of the faulty-context captures; busy-core captures that fall between them set no line (they are flags). If the two sets overlap, there is no stop on b_op and the bound is always carried. In no case is the line above 139 ms, where the attribution bound of a 26 J prefill (0.047 J per ms) would reach a quarter of the phase energy and every prefill run would fail its phase checks |
| `OPEN[S-6]` (M2) | Whether a waited run is excluded; the 1,500 s cap | §8.5, waiting row | As in §8.5. The cap stays 1,500 s either way: it is sized by the longest disturbance, not by the energy effect |
| `OPEN[S-7]` (M3) | The clock-rate line of the pre-check | T_stream_max, the longest sampler stream any run can have under waiting admission (read from the machine test; block 5's sizing value is 335 s, and waiting restarts the stream, so it is expected to hold); and r, the rate at which the wall clock (CLOCK_REALTIME) runs against a hardware counter nothing adjusts (CLOCK_MONOTONIC_RAW), in parts per million (ppm), over hours with automatic network time setting off | Block 5's formula, unchanged: 3.7 ms + (\|r\| + 0.25 ppm) × T_stream_max ≤ 5 ms, where 5 ms is the largest clock bound a run may have, 3.7 ms is block 3's largest fitted placement half-width (3.6 ms) plus 0.1 ms, and 0.25 ppm allows for a stream's rate differing from the one measured. So \|r\| ≤ 1.3 ms / T_stream_max − 0.25 ppm, 3.63 ppm at 335 s. If the measured rate is steadily outside the line, waiting cannot cure it (with network time off the rate does not change); the cure is block 5's desk redraw of the clock's frequency correction, done between sessions, recorded, and changing no energy |
| `OPEN[S-8]` (M4) | The outside-processor exclusion line | §8.5 | As in §8.5 |
| `OPEN[S-9]` (M5) | The graphics and neural-engine exclusion line | §8.5 | As in §8.5 |

The other physical lines are fixed now and are block 5's or the design's: before t0, AC attached with battery current
within 200 mA and the battery not charging, OS thermal level 0, 180 s with no outside process above 5% of one core,
an empty agent census, free disk at least the measured writes of the largest session plus 20 GiB (43 + 20 = 63 GiB)
plus the smoke's, the sampler's median interval at most 150 ms over 300 records, every capture the capture list names
present on local disk, and the model files' hashes equal to the pins. Each failed physical reading waits and is
measured again; disk and sampler get one automatic remedy and then wake the orchestrator. In a session: the stops of
§8.2 P4.

### 8.7 The five requirements every excluding rule meets

From threshold note §9, for every condition of §8.2 and §8.3 that is new or changed in block 6:

1. **Replayed before adopted.** Each is run over every known-good non-claim archive on disk (the 2026-10-09
   rehearsals, structure only) and, after block 5's release, over block 5's three usable sessions (structure only);
   the count of runs and sessions it removes is written beside it: `OPEN[S-16]`. A rule that removes runs from a
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
   variation the intervals do not cover.
7. **Block-5 codes carried**: for each block-6 session, the block-5 session-removing codes it carries, each now a
   flag, so a reader sees which block-6 sessions block 5's rules would have removed.

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
4. the independent recompute agrees with the analysis programs within the tolerance `OPEN[S-13]`, fixed from
   non-claim and full-size synthetic archives before any block-6 energy is read.

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
| S-4 | Fresh calibration acceptance: file, digest, alignment reference, s_bracket, drift budget | quiet-machine captures, block 5's derivation | round 1 |
| S-5 | Stop line on b_op | **M1** (threshold-note test 15 extended), rule of §8.6 | round 1 |
| S-6 | Whether a waited run is excluded | **M2** (threshold-note test 8: 10 reference runs after 85 s idle, 10 after 20 min, alternated) | round 1 |
| S-7 | T_stream_max and the measured clock rate; the clock-rate line | **M3** (machine-test stream lengths; hours of CLOCK_REALTIME minus CLOCK_MONOTONIC_RAW with network time off) | round 1 |
| S-8 | w, joules per outside CPU-second; line C* = F_min / (4w) | **M4** (threshold-note test 1 with burst placements) | round 1 |
| S-9 | Quiet GPU plus ANE level; line P* = F_min / (4 T_max) | **M5** (the rails in idle and in a CPU-only reference run) | round 1 |
| S-10 | F_min (proposed 1.9 J) | the cold gate, from non-claim data (§15 D9) | round 1 |
| S-11 | T_max per pack, the longest target phase in non-claim smoke runs | each pack's first smoke | that pack's first session |
| S-12 | Meter cross-check of the S-8 and S-9 conversions | **M14** (meter idle-power step with known GPU and CPU loads) | round 1 |
| S-13 | Recompute agreement tolerance for the release | non-claim and full-size synthetic archives | any block-6 energy is read |
| S-14 | Analysis commit | block 5's L9 release tag plus the block-6 additions, reviewed and cold-passed | the blind dry run |
| S-15 | Definition of whole-machine energy per phase | the commit that fixes it for block 5 | the blind dry run |
| S-16 | Replay counts beside each new or changed rule of §8 | replay on the 2026-10-09 rehearsal archives; on block 5's usable sessions after its release (structure only) | round 1 (rehearsals); the block-6 release (block 5) |
| S-17 | GAMMA pairing when no later counting floor session exists (§6.2 step 3) | the cold gate | round 1 |
| S-18 | Model and runtime pins for block 6 (expected: block 5's `identity_pins.json`) | S-1 | round 1 |

Measurements owed that set no line here: M9 (time-server query scatter, which will size the time-server flag), M10
(rails against the wall meter, for the comparability statement), M13 (meter edges against sampler edges, an
independent check of the alignment bound), M15 (drift transfer from the reference to the 8B workload, which bears on
the scaled-allowance line of §9.5 item 3).

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
  builds it; so condition (e) stays at 5 ms and the pre-check's clock line stays block 5's formula. The cost: a steady
  clock rate beyond 3.63 ppm would hold every start, which §8.6 cures by the desk redraw. **[cold gate]**
- **D9.** F_min is estimated from non-claim data as the decode attribution floor of the 2026-10-09 rehearsal sizes at
  block 3's operative bound, 1.9 J; the text says "the smallest floor the paper prints", which is a block-5 or block-6
  result and so cannot be used. The F5 investigation's non-claim figures agree with that size: the first-kind bounds
  stored for 22 rehearsal prefill runs ranged 0.98 to 1.72 J, so a prefill attribution floor of 1.72 J under the
  opening capture's bound and about 2 J under b_op. **[cold gate]**
- **D10.** Outside processor work is converted to added energy with the worst placement (all of the overlapping
  intervals' CPU time inside the phase), since the monitor's 10 s intervals cannot place it; this makes the line 2 to 6
  times stricter than block 5's if w lies where the threshold note brackets it. Block 5's 0.05 CPU-s/s per process
  stays as a flag level. **[cold gate]**
- **D11.** The formula of §8.5 covers energy from outside the run's workload, not the run's own duration or energy.
- **D12.** The rule for reading M1 into a stop line (§8.6). **[cold gate]**
- **D13.** M2 is read as a two-point test: below F_min / 4, waiting is a flag; otherwise every waited run is excluded.
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
- **D23.** The graphics-contender rule uses the idle-baseline rail reading and T_max from non-claim smoke runs, so the
  exclusion function reads no science phase duration. **[cold gate]**
- **D24.** Where the meter (M14) and the rail or processor-time conversion disagree, the larger conversion is used.

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

## 17. Change log

- 2026-10-14: draft written (Opus 5.5, session e308c59a). Not cold-gated.
