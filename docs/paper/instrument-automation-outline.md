# Outline: the instrumentation and automation paper

**Status.** Section-by-section outline, written 2026-10-21 (PDT) by Opus 5.5 (an AI model session) for Ed, the
project's owner. It is not a draft of the paper's prose and has not been sent to anyone; whether any of it goes to
the advisor (the academic supervising the work, to whom the paper would go) is Ed's decision.

**Why it exists.** Ed, 2026-10-20: "seems we're close to an instrument paper, whatever the first paper is i forget"
(his mail, transcribed in `docs/process_traces/2026-10-20-magistrate-c634f6f3/RECORD.md:21-22`). The plan of
2026-10-14 names the first paper: *Paper A by mid-November: method plus replication*
(`docs/design/block6_collection_draft.md:576` on `integration/2026-10-14-b6-stage1`). This outline is that paper,
built around what the instrument and its automation have already shown. The numbers of the replication (block 6, the
re-run of the three measurement plans on later days; §0 item 16) are blinded (read by no person or AI tool) until
their release (a dated, written entry after which they may be read), so every section below says whether it can be
written now or waits for the release.

**What this outline never contains.** No energy, power, phase duration, floor, contrast or outcome word (each built
in §0) from the two data collections whose numbers the paper's results rest on (the *claim collections*): 8-12
October (block 5) and 17-21 October (block 6). Every joule and watt printed here comes from a non-claim session (a
session whose numbers never enter the paper's results): the quiet-machine measurements of 16-17 October, the
rehearsals of 6 and 9 October, or the check session of 21 October (the three kinds are built in §0 item 18). Each is
labelled where it appears. This outline sets no threshold (no level at which a check passes or fails); every such
cut-off it quotes carries its derivation at the cited place.

**How to read a section.** Each paper section below has the same parts: the *forcing problem* (why the mechanism must
exist), the *claim* the section makes, the *evidence* (file and line; repository paths are at `origin/main`
`ef520743c` unless another commit or branch is named, and paths under `/Users/edr/` are local files on the
measurement Mac, outside the repository), the *status* (writable now, or waits for the release), a *worked example*
with real numbers, and the *figures*, with every visual element named.

---

## 0. Words used, in the order they are needed

Each term is built here before any section uses it. A term used in only one section is built in that section, before
its first use.

1. **The machine.** One Apple MacBook Pro with an M3 Max chip (model identifier Mac15,9), dedicated to this work. Its
   140 W power adapter connects to it through a USB-C cable.
2. **Rails.** The chip's own power sensors report the electrical power of three on-chip parts: the general-purpose
   processor cores (CPU), the graphics processor (GPU) and the neural engine (ANE, a block for neural-network
   arithmetic). Their sum, *rail power*, is the quantity every result of the paper measures.
3. **Power record.** macOS's built-in sampling tool, `powermetrics` (the *sampler*), is asked for one reading every
   100 ms and in fact delivers one about every 130.5 ms. Each reading, a *power record*, is the *average* rail power
   over its own time span; inside that span the power is known only as that average.
4. **Request, prefill, decode, phase, edge, workload.** One *request* asks a language model to continue a prompt. The
   model first reads the whole prompt and computes the first output token (*prefill*), then produces the remaining
   output tokens one at a time (*decode*). Prefill and decode are the request's two *phases*; the program running the
   model writes a timestamp at the start and end of each, the phase's two *edges*. A *workload* is the fixed prompt
   and output length a request uses. A request's energy is its prefill energy plus its decode energy.
5. **Registration.** The document, written and reviewed before any data exists, that fixes the measurement plan, the
   arithmetic and the rules for which data are removed; *registered* means fixed there. It is
   `docs/registrations/block6_replication_DRAFT.md`, cited below as "registration" with its line numbers.
6. **Phase energy.** Each power record contributes its average power times the time it overlaps the phase. *Example
   (synthetic, registration §1.3):* a phase runs from 10.00 s to 10.25 s; a record over 9.90-10.03 s at 20 W overlaps
   it for 0.03 s and gives 0.60 J; a record over 10.03-10.16 s at 30 W gives 3.90 J; a record over 10.16-10.29 s at
   30 W overlaps 0.09 s and gives 2.70 J; phase energy 7.20 J.
7. **Run, stage.** A *run* is one request measured in its own process: about 75 s of *idle baseline* (the machine
   doing nothing, recorded to check that it is quiet), one unmeasured warm-up request, then the measured request. Two
   workloads are measured: a *decode workload* (a 42-token prompt and 512 output tokens), whose decode phase is
   reported, and a *prefill workload* (a 2,048-token prompt), whose prefill phase is reported; each session has a
   decode half and a prefill half. A *stage* is one ordered list of runs executed together, for example ten runs of
   the decode workload in a row.
8. **Repeat, quad, unit, cell.** A *repeat* is one run on its own. A *quad* is four consecutive runs in the order A,
   B, B, A, where A and B are the quad's two *sides*: when two models are compared, the two models; otherwise the
   same model and workload on both sides (a *null quad*, whose A-minus-B difference can only come from the instrument
   and the machine). If each run reads a little more than the one before (a slow, steady drift), the two A runs and
   the two B runs carry the same total drift, so A minus B is free of it. A *unit* is one repeat or one quad, the
   draw the statistics treat as independent; removing one run of a quad removes the whole quad. A *cell* is one
   reported energy per model and phase.
9. **Pack, session, t0, chain, attempt, round.** A *pack* is one measurement plan, fixed before collection: ALPHA
   measures the model Qwen3-1.7B, BETA the model Qwen3-8B, GAMMA compares the two. A *session* is one unattended
   collection of a whole pack, 125 runs for ALPHA and BETA and 107 for GAMMA, about five hours. *t0* is the moment
   the session's *driver* starts: the session's top-level program, which checks the physical state of the machine,
   starts the monitoring programs and then runs the *chain*, the script that runs the session's stages in order. An
   *attempt* is one try at a session; a *round* is one attempt of each pack. Block-6 sessions are named
   round-then-pack: *r1-alpha* is round 1's ALPHA session.
10. **Reference runs, drift screen.** *Reference runs* use a fixed third model (Qwen2.5-1.5B, 1,024-token prompt, 256
    output tokens) at fixed places in every session: 18 at the start, a group of 3 right after them, 1 at the
    midpoint (between the decode half and the prefill half) and 3 at the end. Their energies are never reported as
    results; they exist only to check the instrument. The *drift screen* passes when the end references read the same
    as the start references within the references' own run-to-run scatter, so the instrument did not drift during the
    session.
11. **Calibration capture.** A short run at a session's start and another at its end in which the GPU is switched on
    and off on command, so that the timing between the sampler's records and the model program's stamps can be
    measured (§3 builds it).
12. **Wall meter and DC input.** A USB-C power meter (ChargerLab POWER-Z KM003C) sits between the adapter's cable and
    the laptop and reads voltage and current 50 times a second. Their product is the *DC input*: the power the
    machine takes from the adapter. The adapter's own loss in turning mains AC into DC happens before the meter and
    is in no number.
13. **Battery current.** The laptop's System Management Controller (SMC, the chip that runs the charger and the power
    sensors) reports the battery's current once a second; a negative value means the battery is discharging into the
    machine.
14. **Battery assist.** A moment when the battery discharges while the adapter is attached, because the machine needs
    more power than the adapter delivers.
15. **Agent, census.** An *agent* is an AI coding assistant process (Claude Code or Codex) running on the machine. It
    draws 8 to 47 W while "idle" (registration line 188), so none may be alive while anything is measured. The
    *census* is a scan for agent processes every 30 s.
16. **Block, usable.** A *block* is a set of sessions collected under one plan fixed in advance. Block 5 (8-12
    October 2026) gave one *usable* session per pack (one whose data entered block 5's results; block 6's word for
    the same status is *counting*, item 23). Block 6 (17-21 October) repeated the three packs to test whether block
    5's numbers hold on other days: the *replication*.
17. **Ed.** The project's owner, who runs the machine and can stop any session.
18. **Non-claim sessions used here.** A *non-claim* session is one whose numbers never enter the paper's results. The
    *quiet-machine kit*: 11 measurements, each carrying an M-number from M1 to M15 (the numbering has gaps; only the
    numbers used below are cited), taken 16-17 October with no agent alive, over 51,524 s of wall time, to measure
    the quantities the levels at which the rules' checks pass or fail (their *cut-offs*) are drawn from
    (`docs/process_traces/2026-10-17-magistrate-1a1261a5/RECORD.md:6`). The *rehearsals*: four non-claim sessions of
    6 and 9 October, run with the collection code but outside any result; their 77 runs (53 of them on 9 October) are
    the replay set of §5. *Session H*: a check session of 21 October that ran models up to 122 billion parameters on
    the same instrument, in a *check* stage (five requests per model) and a *soak* stage (the same
    70-billion-parameter request repeated back to back), stopped by Ed at 17:19 PDT (`RUN_STATE.md:233-234`).
19. **Physical hazard.** A state of the machine that would make a measured energy wrong if collection ran through it:
    running on battery or charging; the clock stepping or drifting; thermal pressure; another process using the
    processor (*contention*; such processes, other than the measurement's own, are *outside processes*); too little
    free disk; the sampler slow or not sampling; the machine sleeping; an agent alive.
20. **Refusal, flag, exclusion.** A *refusal* stops collection or removes data. A *flag* is a recorded fact written
    beside the data (a code such as `sleep.in_run`, the run or session it concerns, the observed value and the
    evidence); it removes nothing by itself. An *exclusion* is what the registration says a given flag does: remove
    the run, remove the session, or only disclose. The *flag catalog* is the file listing every flag code and its
    effect.
21. **Labelled alternative, known-good, replay.** Where a rule could reasonably have been drawn another way, the
    paper prints the registered result and, beside it, a *labelled alternative* computed under the other rule.
    *Known-good* data are non-claim sessions whose correctness nobody disputes (the rehearsals and the quiet-machine
    kit of item 18). A proposed rule is *replayed* on them (applied to their stored records to count how many runs it
    would remove), and a rule that removes known-good data is suspect.
22. **Harvest, desk.** After a session ends, the *harvest* program reads its raw files, re-derives every check from
    the preserved bytes, writes every flag, applies the registration and writes the *verdicts* (its written decisions
    on whether each run and session counts). The *desk* step is the harvest plus compressing the raw files; it runs
    with no measurement in progress.
23. **Counting session, line.** A *counting session* is one that no physical hazard stopped and that carries no
    session-excluding flag; only counting sessions enter the registered numbers. A *line*, in this outline, is one
    printed row of results: the *flagged-inclusive line* is a labelled alternative printed beside each registered
    result, with the non-counting sessions added back where they can be computed. (A level at which a check passes or
    fails is called a *cut-off*.)
24. **Pinned commit.** The one version of the collection code, named by its git commit hash, that every block-6
    session runs from, in a separate copy of the repository used for nothing else.
25. **Pre-session check, smoke, machine test.** The *pre-session check* measures the physical hazards directly (no
    model runs) before a session may start. A *smoke* is a short real collection (4 to 6 runs) of the same pack by
    the same code, started the same way the session will be (its *launch route*: by the same macOS job-scheduler
    (`launchd`) job, with the same declared job type, not by hand), and judged by the desk programs before the
    session. A *machine test* is a 40-minute live test of the pinned commit that injects faults (an agent appearing,
    a disturbed idle baseline, the meter unplugged) and checks that each leaves its expected record.
26. **Loop, orchestrator, arming, hold.** The *loop* is a set of plain programs that macOS's job scheduler
    (`launchd`) starts every few minutes; it runs pre-check, smoke, session and desk, session after session, with no
    agent alive. The *orchestrator* (also *the lead*) is the AI model session that leads the project; it runs only
    between sessions, when the loop wakes it or a person starts it. *Arming* a session is committing to start it: the
    loop sends Ed a notice and waits for his NO. A *hold* stops the loop from arming a pack (or any pack) until the
    orchestrator has looked.
27. **Floor, contrast, outcome word.** A *detection floor* is the smallest energy difference the method can tell
    apart from noise. A *contrast* is GAMMA's 1.7B-versus-8B energy difference on the same workload; it is judged
    against the larger of the two models' floors (the *floor gate*), each model's floor coming from its own pack's
    session. An *outcome word* is the registered verdict on a contrast (whether it clears the floor gate).
28. **Blinding, release.** Until the *release*, no person or agent reads a block-5 or block-6 energy, power, phase
    duration, floor, contrast or outcome word; programs compute them into restricted files. *Structure* (verdicts,
    counts of flags and runs, hazard readings, stage timing that is not a phase duration) is not restricted
    (registration §12.1, lines 1124-1138). The release is a dated, written entry in the project's records after which
    the numbers may be read.

---

## Front matter (writable now)

**Working titles.** (a) *An unattended, physics-gated energy instrument for language-model inference on one laptop*;
(b) *Measuring the energy of language-model inference on Apple Silicon without anyone watching: an instrument, its
rules, and a blinded replication*.

**Abstract (structure only until the release).** One paragraph: the problem (a software power sampler on a personal
laptop, many processes and clocks that can corrupt a phase energy, and a single session that cannot show whether a
number holds on another day); the instrument (rails, a wall meter and the battery current, with in-session timing
calibration); the rule set (only a directly measured physical hazard refuses; every other condition is a recorded
flag; every excluding rule's cut-off set in joules and replayed on known-good data before adoption); the automation
(a loop with no person or agent on the machine collected 9 of 9 counting replication sessions, 1,071 of 1,071 planned
runs, in 78 hours); the blinded replication, with an independent recompute (a second program, sharing no code with
the analysis, that recomputes the numbers from the raw records; results at release). The sentence with the
replication's numbers is a placeholder until the release.

**Contributions** (each is a section below): an instrument with three independent views of power (§2) and timing
calibration inside every session (§3); direct measurement of every physical hazard (§4); a rule set that refuses only
on physics and sets every exclusion's cut-off in joules (§5); a measured answer to battery assist (§6); an unattended
loop and its record (§7); live tests that found defects before data was lost (§8); blinding with an independent
recompute (§9); a record of how the software was built and checked (§10); the replication (§11).

---

## 1. Introduction

- **Forcing problem.** Energy per phase of a language-model request is a small number measured on a machine that is
  never fully idle: system daemons wake on their own, the clock can be corrected under the program, the machine can
  sleep, and the people and AI tools that build the software run on the same machine. In block 5, rules about
  bookkeeping files (a missing list, a stale file) rather than about the machine's physical state cost most of the
  machine time: BETA spent 42.5 h of wall time for one usable 5.9 h session, 21.4 h of it in five lost attempts and
  15.1 h in the gaps between them; three of the five losses were rule losses, two of them certain before t0 from
  files already on disk.
- **Claim.** A single laptop can measure phase energy unattended, session after session, if (i) power is read three
  independent ways, (ii) the two clocks (the sampler's and the model program's) are calibrated inside every session,
  (iii) only a directly measured physical hazard stops collection, and everything else is written down and decided by
  a rule fixed in advance, and (iv) no agent is alive and nobody uses the machine while it measures. Block 6 is the
  test of that claim.
- **Evidence.** `docs/design/block6_collection_draft.md:42-44` and `:66-78` (block 5's losses, table by attempt;
  integration branch); `RUN_STATE.md:203` (block 6 tally); `/Users/edr/night-b6/loop/attempts.jsonl` lines 1-9 (one
  structure line per block-6 session).
- **Status.** Writable now, except the last paragraph, which states the replication's result at release.
- **Worked example (structure, real).** Block 5's BETA: attempts a1 to a6, chain run-times of 6.05, 2.53, 0.13, 6.95,
  5.77 and 5.92 h; only a6 usable; lost chain time 6.05 + 2.53 + 0.13 + 6.95 + 5.77 = 21.4 h; wall time from a1's t0
  to a6's end 42.5 h. Block 6: 9 sessions, 9 counting, first t0 17 October 20:51 PDT, the loop reached its final
  state, DONE (every pack at its target of three counting sessions; §7), 21 October 02:54 PDT (78.1 h), 46.4 h of it
  collecting.
- **Figures.** *Figure 1: one usable session against nine.* Two horizontal time bars on a shared axis in hours. Upper
  bar, "block 5, BETA pack": six segments, one per attempt (a1 to a6), each as long as its chain, coloured "lost:
  bookkeeping rule" (a1, a4, a5), "lost: physics" (a2, an agent opened at the keyboard), "lost: the start-of-session
  calibration capture measured a delay above a fixed limit (§3)" (a3) or "usable" (a6), with the gaps between them in
  grey and labelled "reviews and rule changes between attempts". Lower bar, "block 6, all packs": nine segments
  coloured by pack (ALPHA, BETA, GAMMA), each labelled with its session name (r1-alpha ... r4-alpha, round then
  pack), with the desk step after each in a lighter shade of the same colour. A legend names every colour. No energy
  appears.

## 2. The machine and three views of its power

- **Forcing problem.** The rails see only the chip. A reader, especially one who builds whole-system energy
  benchmarks, asks what the whole machine pays, and whether the rails miss power the workload causes elsewhere
  (memory, storage, fans, voltage regulators). One sensor cannot answer either question.
- **Claim.** The instrument reads power at three places on one power path, each with its own clock and rate: the
  rails (`powermetrics`, one average about every 130.5 ms), the DC input (the wall meter, 50 samples a second) and
  the battery current (the SMC, once a second). The rails are the quantity every result rests on; the DC input plus
  the battery term is a printed whole-machine line that never enters a result; their ratio is measured, not assumed,
  and depends on the workload.
- **Evidence.** Registration `docs/registrations/block6_replication_DRAFT.md:104-110` (machine and sampler),
  `:824-837` (the meter excludes nothing; cross-checks M14 and M10), `:1030-1037` (whole-machine energy per phase,
  its boundary sentence); `joulewise/hazards/smc.py:17-27` (SMC keys: `B0AC` battery current, `B0AV` battery voltage,
  `PDTR` DC-in power, `PSTR` system total power); `joulewise/external/km003c_parse.py:79` (the 28 V band of the USB-C
  power contract, §6), `:368` (`integrate`), `:397` (`delta_machine_energy`). Session H raw files (local):
  `/Users/edr/night-bytes/h-20261021T185555Z/custody/hazards/meter/stream-001.jsonl`,
  `.../runs-parent/runs_bytes_mac_check/*/summary_metrics.json` and `events.jsonl`.
- **Status.** Writable now from non-claim data. The whole-machine line per phase for blocks 5 and 6 waits for the
  release.
- **Worked example 1 (quiet-machine kit M14, real).** A known load is switched on between idle stretches and seen at
  both places. GPU load at 20% duty: meter 20.15 W, rails 7.65 W, so the rails see 0.380 of the step. One CPU core at
  100%: meter 9.41 W, rails 5.42 W, 0.576. Over steady levels (M10) the fit is meter = 2.650 × rails + 1.632 W. So a
  load the rails see as 1 W shows as about 1.7 to 2.8 W at the meter, and the meter sees every tested load the rails
  see (registration lines 830-837).
- **Worked example 2 (session H, real; computed for this outline).** Request window: from the program's prefill start
  stamp to its decode end stamp. The program stamps on the wall clock; the meter's samples are placed on the Mac's
  hardware counter that nothing adjusts (`CLOCK_MONOTONIC_RAW`); the meter stream records the offset between those
  two Mac clocks at its start, so a wall-clock stamp becomes a counter time by subtracting that offset (§3 measures
  the two clocks' relative rate as −4.67 × 10⁻⁷ ppm, so the offset stays constant). Meter energy: `integrate`, the
  mean of the 50 Hz samples inside the window times its length; rail energy: the run's recorded request energy
  (prefill plus decode phase energy).
  - Qwen3.5-122B-A10B (4-bit), 2,048-token prompt and 512 output tokens, run r01: 15.732 s; rails 507.0 J, a mean of
    32.23 W; meter 1,340.0 J, 85.18 W. M10 predicts 2.650 × 32.23 + 1.632 = 87.03 W, 2.2% above the measured 85.18 W.
  - Llama-3.3-70B-Instruct (4-bit), same workload, soak-stage run r01: 82.570 s; rails 3,117.1 J, 37.75 W; meter
    9,016.8 J, 109.20 W. M10 predicts 101.67 W, 6.9% below the measured value; over the 11 soak runs the shortfall is
    5.3% to 11.0%.
  - Reading: the rails' share of the machine is workload-dependent (0.377 to 0.378 for the five 122B requests, 0.330
    to 0.351 for the eleven 70B soak requests), so the paper prints the measured DC-input line and never converts
    rails into machine power with M10.
- **Figures.** *Figure 2: the power path and the three taps.* A left-to-right block diagram. Boxes, in order: "mains
  socket"; "140 W adapter (AC to DC; its loss is upstream of every printed number)"; "USB-C cable"; "KM003C meter,
  tap M: DC input voltage × current, 50 samples a second"; "laptop power input"; a branch to "battery, tap B: SMC
  battery current × voltage, once a second, negative = discharging"; then "system-on-chip, tap R: CPU, GPU and ANE
  rails, one average every ~130.5 ms" and "rest of the machine: memory, storage, fans, regulators, display circuitry
  (seen only at M)". Solid arrows are power flow, labelled "adapter power" and "battery power"; dashed arrows from
  each tap to a box "recorded streams", each dashed arrow labelled with its clock (meter device clock fitted to the
  Mac's raw clock; SMC reads stamped on the Mac's clocks; power records stamped by the sampler). *Figure 3: rails
  against DC input.* Scatter with rail power (W) on x and meter power (W) on y; filled circles are the M14 load steps
  (labelled "GPU 5%", "GPU 20%", "one core"), the solid line is the M10 fit with its equation printed on it, open
  squares are session H's request means (labelled with model and run). A note under the plot says every point is
  non-claim.

## 3. Placing power records on the request's clock

- **Forcing problem.** Power records are stamped by the sampler; phase edges are stamped by the program running the
  model. Before a record can be shared between phases, the two time bases must sit on one timeline, and any error in
  that placement moves energy across the phase edge. Repetition cannot remove it: every run of a session is placed by
  the same method.
- **Claim.** Each session measures its own timing error twice, with a *calibration capture* at its start and another
  at its end. A capture drives the GPU through 59 commanded one-second on/off pulses; for each pulse the capture's
  fitting program (the *estimator*) fits the power records with a rectangle whose edges may be late and returns every
  delay consistent with the records: a pair of delays (onset, offset) is *consistent* when the rectangle shifted by
  them predicts the records' averages with a fit loss (a robust sum of the prediction errors, each divided by the
  quiet trace's noise level) at most the best pair's loss plus the larger of 1.0 and 5% of it; the set of such pairs
  is the *accepted region*. The capture's *fiducial bound* is the largest such delay over its pulses. The session's
  *operative timing bound* is b_op = max(opening, closing) + max(|closing − opening|, s_bracket), where *opening* and
  *closing* are the fiducial bounds of the start and end captures and s_bracket is a minimum allowance for the
  placement of records on the program's timeline (the *alignment*) moving between the two captures. Every phase edge
  is then moved by up to that bound and the largest change in phase energy is carried into the run's uncertainty.
- **Evidence.** Registration `:191-217` (captures, b_op, and how the bound enters each run's uncertainty), `:361-401`
  (the calibration acceptance file, built in the worked example below, and its constants), `:1214-1221` (M1 and M13
  values); `docs/paper/draft-v2-skeleton.md:125-173` (the full capture algorithm, already written: pulse schedule,
  fit, accepted region, the clock anchor that ties the sampler's records to wall time, and the *bracket*, the pair of
  captures between which every run of the session sits); draft-v2 `:1194-1196` (the loss cut-off and the accepted
  region); registration `:856` (the clock-rate measurement M3).
- **Status.** Mechanism writable now (reuse draft-v2 §2 and Appendix A.3). Block 6's own capture values and b_op are
  restricted until the release.
- **Worked example (real, non-claim).**
  - *The acceptance constants for block 6.* The *calibration acceptance* is the file that fixes, before any session,
    the constants used to judge captures. For block 6, 13 quiet captures (M1's 10 and M13's 3) had fiducial bounds
    from 27.38 to 37.05 ms; their range is 9.675 ms, below the 10.818 ms minimum fixed earlier (a minimum allowance,
    not a detection floor), so s_bracket = 10.818 ms. The largest value, 37.05 ms, became the alignment reference: a
    capture above it is flagged, never refused.
  - *b_op on real sessions.* Over the non-claim rehearsals, the block-6 rule gives b_op of 41.3, 41.4 and 51.0 ms.
  - *A check that shares nothing with the capture.* M13 timed the same commanded edges at the wall meter: the meter's
    edges lag the commands by 31.2 ms on average and lag the sampler's edges by 25.2 ms (standard deviation 4.7 ms
    over 354 edges), so the sampler's own edges lag the commands by about 6.0 ms (standard deviation 11.4 ms), inside
    the 30 ms typical capture bound.
  - *The clocks themselves.* M3 read wall time (`CLOCK_REALTIME`) against a hardware counter nothing adjusts
    (`CLOCK_MONOTONIC_RAW`) 5,147 times, 10 s apart, over 51,514 s with automatic network time off: the slope is
    −4.67 × 10⁻⁷ ppm (standard error 5.19 × 10⁻⁷ ppm). Over the longest run stream (335 s) that moves a run's clock
    by 1.6 × 10⁻¹⁰ s.
- **Figures.** *Figure 4: one calibration pulse.* x axis time (ms), y axis GPU power (W). Elements: the commanded
  pulse as a dashed rectangle between "command on" and "command off" (two vertical dashed lines); the power records
  as horizontal solid bars, each spanning its record's interval at its average power (labelled "one power record,
  ~130.5 ms"); the fitted late rectangle as a solid outline; two horizontal arrows "onset delay" and "offset delay"
  between commanded and fitted edges; a shaded band "accepted delays" around each fitted edge. *Figure 5: the
  bracket.* A session timeline (left to right) with two short blocks "opening capture" and "closing capture" at its
  ends, each labelled with its fiducial bound as a vertical bar height; a brace joining them labelled "b_op = larger
  bound + max(difference, s_bracket)"; a phase-edge inset showing an edge moved by ±b_op and the hatched energy that
  moves across it. Values in the figure are the registration's synthetic example recomputed with block 6's s_bracket
  (opening 40.0 ms, closing 30.0 ms: b_op = 40.0 + max(10.0, 10.818) = 50.818 ms), labelled synthetic.

## 4. Measuring the machine's state directly

- **Forcing problem.** Every hazard of §0 item 19 has a cheap proxy (a settings string, a receipt file, a job's
  declared priority), and proxies can say "fine" while the physics is not. Block 5 lost sessions to proxies and its
  rehearsals overrode the census on every call, so they never exercised the path that later stopped a session.
- **Claim.** Every hazard is measured as the physical quantity itself, by a monitor that runs beside every session at
  fixed cadences (clock every 1 s, battery current every 1 s, thermal level every 5 s, processor time of outside
  processes every 10 s, free disk every 60 s) and by the pre-session check before t0. The pre-session check's
  cut-offs: adapter attached with battery current within 200 mA and not charging; OS thermal level 0; 180 s with no
  outside process above 5% of one core; no agent alive; free disk at least the largest session's measured writes plus
  20 GiB (43 + 20 = 63 GiB); the sampler's median interval at most 150 ms over 300 records; model files equal to
  their pinned hashes. A failed reading waits and is measured again; it never becomes a guess.
- **Evidence.** `joulewise/hazards/monitor.py:17-41` (cadence table); registration `:860-873` (pre-t0 lines; the two
  readings that are flags, with derivations), `:338-345` (agent pause, no sleep); `RUN_STATE.md:133-134` and
  `docs/process_traces/2026-10-17-magistrate-6789ef94/RECORD.md:5-19` (the media daemon); `RUN_STATE.md:138-139` and
  `docs/process_traces/2026-10-17-magistrate-f4db0072/RECORD.md:9-26` (the launch context);
  `docs/design/block6_collection_draft.md:90-94` (block 5's rehearsals overrode the census).
- **Status.** Writable now. Hazard readings are structure, not restricted.
- **Worked example 1: a daemon that would have contaminated every run (17 October, pre-checks of the first block-6
  session, real).** The pre-check refused twice on contention (another process using the processor): "no 180 s run of
  clean 30 s intervals within 600 s; last dirty interval: mediaanalysisd at 1.856 CPU-s/s" and 1.907 on the second
  try (CPU-seconds used per second of wall time: about 1.9 cores kept busy), against a limit of 0.05
  (`mediaanalysisd` is Apple's photo and video analysis daemon, which works when the machine is idle on AC power,
  exactly the loop's own condition). The polite stop signal (SIGTERM) was ignored for 30 s; the forced kill (SIGKILL)
  made `launchd` restart it within 5 s at 178-199% CPU; the pause signal (SIGSTOP) held it at 0.0% CPU, after which
  the busiest process was the loop itself at 1.4%.
- **Worked example 2: a launch context that slowed the sampler (17 October, real).** The sampler check refused on all
  five pre-checks, including the three after the media daemon was stopped: 237, 178, 197, 183 and 180 records of the
  300 required within 55 s, median intervals 218, 298, 259, 290 and 299 ms against the 150 ms cut-off. The same probe
  gave 300 records at a 131 ms median in both machine tests that day. The cause: the loop's `launchd` job was
  declared `ProcessType Background`, which throttles its children, `powermetrics` included. Declared `Interactive`,
  the next pre-check captured 300 of 300 records over 39 s, mean 130 ms. Nothing had been collected, so no number was
  affected.
- **Worked example 3: why one slow interval is only a flag (real, non-claim).** In 101 non-overlapping 300-record
  windows of quiet idle baselines, none holds an interval above 200 ms (the largest is 166.8 ms); the 150 ms median
  cut-off already refuses the slow launch context, and the pre-check's sampler probe (its 300 records) carries no
  joules.
- **Figures.** *Figure 6: the sampler under two launch contexts.* Strip plot, x axis "pre-check" (000001 to 000007,
  with their clock times), y axis "median interval between power records (ms)"; filled circles for the five
  Background checks, an open circle for the first Interactive check; a horizontal dashed line "refusal cut-off 150
  ms" and a dotted line "nominal 130.5 ms"; each circle labelled with its record count out of 300. *Figure 7: the
  monitor's cadences.* A timeline of one minute with one row per hazard log file (*journal*: clock, battery, thermal,
  contention, disk), each tick a reading, labelled with its interval.

## 5. Physics refuses; everything else is a flag

- **Forcing problem.** A rule that removes data can bias a result as surely as a contaminated run can, and a rule
  whose cut-off is drawn without a size in joules can remove known-good data for nothing. Block 5 removed sessions
  for bookkeeping conditions (a missing source list, a stale acceptance file) that no measurement showed had changed
  a number.
- **Claim.** Only a directly measured physical hazard stops collection or removes data. Four further grounds remove
  data because without them the number would be undefined or not a measurement of the registered experiment: the
  number is undefined (N), the data are not of the registered model, runtime or code (W), the registered drift screen
  fails (D), the collection code failed structurally: the chain crashed, a stage with planned runs left none of their
  records while later stages ran, or the capture records or the list of runs are missing (S). Everything else is a
  flag, printed. Each excluding rule must meet five requirements before adoption: it is replayed over every
  known-good non-claim archive and its removal count written beside it; its cut-off is set by the energy it can add,
  in joules, against the smallest printed quantity; anything it can know before t0 is computed before t0 by the same
  function; the session is collected and the flag decided in the analysis; and it is rehearsed on full-size data. Of
  block 5's 32 session-removing codes, 25 are flags in block 6.
- **Evidence.** Registration `:553-567` (the rule and its four grounds), `:569-600` (session exclusions table),
  `:593` (25 of 32), `:684-704` (the sizing formula and F_min), `:711`, `:735-747` and `:769-799` (the
  outside-processor rule, its measurement and its replay), `:841-848` (worked example with rehearsal sizes),
  `:875-897` (the five requirements); `docs/process/pruning_list_2026-10-14.md` (the inventory of checks it was
  applied to).
- **Status.** Writable now.
- **Worked example (real, non-claim).** (A *contamination flag* records energy that something other than the run's
  own workload may have added: another process, another program on the GPU, a long disturbed wait before the run.)
  - *The size every exclusion is drawn at.* F_min, the smallest floor the paper prints, estimated from the non-claim
    rehearsal of 9 October, is 1.9 J; a contamination flag excludes a run when the energy it can have added reaches
    F_min / 4 = 0.475 J. The registration states this quarter but records no derivation for the factor; for scale, a
    5-unit mean's statistical half-width (half the width of its 95% interval) on the same rehearsal is 0.47 J
    (threshold note `docs/design/next_block_threshold_proportion.md:292-304`). The paper needs one sentence of
    derivation (open decision 5).
  - *A rule that passes.* An agent at its lowest measured draw, 8 W, over a 0.62 s prefill (rehearsal size) adds 8 ×
    0.62 = 4.96 J, ten times 0.475 J: excluded, so the whole unit an agent overlaps is removed.
  - *A rule that fails its replay and stays a flag.* Outside processor work: M4 measured w = 5.432 J per CPU-second
    (the largest of 20 one-core bursts at interactive priority), and the quiet machine's own background is c_q = 0.54
    CPU-s per 10 s interval. The rule "exclude when 5.432 × (C − k × 0.54) ≥ 0.475 J" (C the outside CPU-seconds in
    the k intervals the request overlaps) draws its cut-off at 0.0874 CPU-s of excess, about a fifth of the quiet
    machine's own 10th-percentile interval (0.41 CPU-s). Replayed on the 53 known-good quiet rehearsal runs of 9
    October, it removes 14. On the same session's reference runs, phase energy regressed on outside CPU gives −0.09 ±
    0.09 J per CPU-second at prefill; two reference runs with about 20 outside CPU-seconds read 11.11 and 11.44 J at
    prefill against their 23 siblings' 11.26 ± 0.38 J, where the rule predicts 104 and 107 J added. So the rule is a
    recorded flag, and each cell prints the rule's result beside it as a labelled alternative.
- **Figures.** *Figure 8: the decision path of one condition.* A flow chart. Diamond "measured physical hazard?";
  "yes" leads to a box "refuse: wait and re-measure before t0, or stop the session"; "no" leads to a box "write a
  flag (code, run, observed value, evidence)", then a diamond "named as excluding in the registration?" with "yes" to
  "exclude run or session, and print the flagged-inclusive line" and "no" to "disclose only". A side panel lists the
  five requirements as five ticked boxes beside the "named as excluding" diamond. *Figure 9: a replay table as a
  figure.* For each candidate rule (rows: agent overlap, outside processor at w = 5.432, outside processor at
  background-priority w, another program on the GPU, a run's own clock fit, the placement of its records on wall
  time, with a bound above 5 ms), bars of "known-good runs removed" out of 53 (the quiet 9 October rehearsal) and 77
  (all rehearsal runs), and a column "size in J at the cut-off"; rows that fail are marked "kept as flag".

## 6. The battery and the adapter's ceiling

- **Forcing problem.** The wall meter sits on the DC input. If the machine needs more than the adapter can deliver,
  the battery supplies the rest, and a whole-machine number read from the meter alone is too small. Was this a real
  effect on this machine, and if so, how large?
- **Claim.** Yes, on the heaviest workload. With Llama-3.3-70B the DC input reached a hard ceiling of about 136.5 W,
  consistent with a 5 A current limit at the 28 V supply voltage the adapter and laptop negotiate over USB-C (their
  *power contract*), and the battery covered the excess for a few seconds per request. The battery's share of each
  request's energy was 0.10% to 0.29%. The rails, the quantity every result rests on, are not affected: they are the
  chip's own sensors and report on-chip power whatever its source (a physical argument, not a measurement). The
  opposite failure, losing the adapter, is a physical hazard: in block 5 the charger lost voltage for 26 s during
  BETA's attempt 4 and the Mac then slept for 3,507 s, costing 4 runs, which is why the pre-session check and every
  run read the battery current directly. The whole-machine line adds the battery term back (DC input energy + battery
  energy), and a phase whose request shows battery assist is flagged.
- **Evidence.** `RUN_STATE.md:36` and `docs/design/block6_collection_draft.md:72` (the block-5 charger drop);
  `joulewise/external/km003c_parse.py:312` (`battery_watts`: −B0AC × B0AV / 10⁶ W at each poll), `:397-425`
  (`delta_machine_energy`: the machine term is the meter term plus the battery term); `joulewise/hazards/smc.py:1-12`
  (why the SMC key is read: the battery registry values refresh only every 60 s and missed discharge bursts
  entirely), `:21` (`B0AC`); registration `:620-625` (charging or loss of AC excludes a run; battery discharge alone,
  `battery.assist`, is disclosed), `:860-861` (pre-t0: battery current within 200 mA, not charging), `:1016` (the
  battery-assist labelled line: each estimate also over the units with no battery-assisted run), `:1030-1037`
  (whole-machine line; boundary sentence "DC input at the USB-C port; the adapter's AC-to-DC loss is not included").
  Session H raw files (local): `.../custody/hazards/meter/stream-001.jsonl` (93,535 lines),
  `.../custody/hazards/monitor/battery.jsonl` (19,023 lines), and the run folders
  `bytes-mac-check-soak-llama-70b-r01` to `-r11`, `bytes-mac-check-check-qwen35-122b-r01` to `-r05`. Computation done
  for this outline with the two functions above; a tracked script for the paper is still to be written.
- **Status.** Writable now from session H (non-claim). Block 6's count of battery-assisted runs is structure and is
  printed at release with the battery-assist line.
- **Worked example (session H, 21 October, real).**
  - The meter's 935,345 samples over the session never exceed 136.79 W; the largest current is 4.991 A at a bus
    voltage of 27.38 to 27.63 V. In all 16 check and soak requests of the 70B model, the largest 50 Hz sample is
    136.3 to 136.4 W.
  - Soak run r01 (2,048-token prompt, 512 output tokens, 82.570 s): DC input 9,016.8 J; battery 9.08 J; machine
    9,016.8 + 9.08 = 9,025.9 J; rails 3,117.1 J (0.345 of the machine). In 3 of its 84 once-a-second SMC reads the
    battery was discharging; the deepest read was −395 mA at 12.758 V, 0.395 × 12.758 = 5.04 W from the battery,
    while the SMC's own DC-in reading was 129.6 W and its system total 134.2 W.
  - Over the 11 soak requests (81.6 to 84.3 s each): battery 9.08 to 26.90 J per request, 0.101% to 0.292% of 8,876.3
    to 9,361.0 J. Over five Qwen3.5-122B requests (15.7 s each): 1.07 to 1.49 J, 0.080% to 0.110%. In the Qwen3-1.7B
    check requests of the same session the battery never discharged.
  - So the meter alone would have under-read the 70B requests by at most 0.29%; adding the battery term removes that.
    The term's own resolution is one SMC reading per second, which the paper states as a limit.
- **Figures.** *Figure 10: one 70B request at the ceiling.* x axis time within the request (s), with a vertical
  dashed line "prefill ends" at 26.6 s. Upper panel, y axis power (W): a thin line "DC input (meter, 50 Hz)", a
  horizontal dotted line "adapter ceiling ≈ 136.5 W", and a stepped line "rails (one value per power record)". Lower
  panel, y axis battery power (W): bars, one per SMC second, "battery → machine" above zero and "charging" below,
  with the three discharging seconds labelled with their current in mA. A caption box gives the four energies of the
  request (DC input, battery, machine, rails).

## 7. The unattended loop

- **Forcing problem.** Any agent alive on the machine adds 8 to 47 W, and a person at the keyboard is a disturbance
  too, yet a replication needs many six-hour sessions back to back. The work between sessions (pre-checks, smokes,
  harvests, decisions) must happen without anyone on the machine while it measures.
- **Claim.** A loop of plain programs under `launchd` runs the whole cycle: pre-check, a notice to Ed that a session
  is about to start (arming it, §0 item 26) with a 30-minute window to answer NO (the smoke runs inside that window),
  smoke and its desk check, the session, its desk step, then the next pack in a rotating order. A physical hazard
  makes it wait and re-measure every 240 s; a failed smoke holds only that pack, any other non-physical problem holds
  the loop, and both wake the orchestrator. Block 6 ran 9 sessions with 9 counting and no physical stop.
- **Evidence.** `joulewise/b6/loop.py` at the pinned commit `f31aca19f`: `:285` (`_precheck`), `:308` (the 1,800 s
  notice window), `:314-316` (wait and re-measure every 240 s), `:423` (`_smoke_desk`), `:471` (`_arm_wait`),
  `:195-199` (`DONE`); `configs/b6/loop.json` at `f31aca19f` (base order ALPHA, BETA, GAMMA); registration `:186-189`
  and `:465-481` (rounds); `/Users/edr/night-b6/loop/attempts.jsonl` lines 1-9 and
  `/Users/edr/night-b6/loop/state.json` (`since` = the DONE time);
  `docs/process_traces/2026-10-20-magistrate-c634f6f3/RECORD.md:31-41`; `RUN_STATE.md:202-203`.
- **Status.** Writable now (all structure).
- **Worked example (structure, real).** Block 6, from the loop's ledger (its own record of every attempt):

  | Session | Round | t0 (PDT) | Chain run-time (min) | Harvest (min) | Desk (min) | Runs present and succeeded | Counting |
  |---|---|---|---|---|---|---|---|
  | r1-alpha | 1 | 10-17 20:51 | 313.1 | 87.8 | 94.8 | 125 of 125 | yes |
  | r1-beta | 1 | 10-18 05:28 | 332.5 | 86.1 | 93.3 | 125 of 125 | yes |
  | r1-gamma | 1 | 10-18 14:29 | 278.5 | 86.2 | 92.9 | 107 of 107 | yes |
  | r2-beta | 2 | 10-18 22:23 | 333.9 | 79.6 | 87.0 | 125 of 125 | yes |
  | r2-gamma | 2 | 10-19 07:22 | 282.7 | 93.0 | 100.0 | 107 of 107 | yes |
  | r3-gamma | 3 | 10-19 17:01 | 279.3 | 88.8 | 95.8 | 107 of 107 | yes |
  | r3-alpha | 3 | 10-20 01:07 | 313.6 | 92.2 | 99.6 | 125 of 125 | yes |
  | r3-beta | 3 | 10-20 09:48 | 335.3 | 89.3 | 96.9 | 125 of 125 | yes |
  | r4-alpha | 4 | 10-20 19:14 | 315.8 | 92.8 | 100.5 | 125 of 125 | yes |

  Chain run-times 278.5 to 335.3 min (4.64 to 5.59 h); desk 87.0 to 100.5 min, of which the harvest is 79.6 to 93.0
  min; start to start 7.89 to 9.65 h (mean 8.8 h); 46.4 h of collecting in 78.1 h of wall time; 1,071 of 1,071
  planned runs present and succeeded (the harvest's run exclusions by flag are structure counts printed at release).
  Before each start a smoke ran: its collection took 21.4 to 26.4 min, and its start preceded the session's t0 by
  47.5 to 76.1 min (file times of the smoke folders). ALPHA's round-2 session never ran: its smoke held the pack
  (§8), so ALPHA's third session moved to round 4.
- **Figures.** *Figure 11: the loop's states.* A state diagram. Nodes: NEXT (choose the next pack), PRECHECK,
  WAIT_PHYSICS (a hazard: re-measure every 240 s), SMOKE_RUN, SMOKE_DESK, ARM_WAIT (the 30-minute NO window),
  SESSION_RUN, SESSION_DESK, ROTATE, DONE (every pack at its target of three counting sessions), HOLD_LOOP (a
  non-physical problem, Ed's NO, or a stop file, a marker whose presence holds the loop: wake the orchestrator).
  Edges labelled with their conditions ("hazard measured", "hazard clear", "smoke pass", "smoke non-physical failure:
  hold this pack", "no NO after 30 min", "chain exit", "harvest written", "target reached"). The two collecting
  states are drawn with a heavy border and the note "no agent alive". *Figure 12: the block-6 timeline* (the lower
  bar of Figure 1 expanded): one row per session, segments for smoke, NO window, chain and desk, on a clock-time axis
  from 17 October 20:00 to 21 October 03:00.

## 8. Tests that found defects before data was lost

- **Forcing problem.** Six hours of new code on the real machine can fail in ways no unit test sees: a file rewritten
  without updating the stored hash that names its bytes, a schema mismatch only the live path builds, a launch
  context. A failure found in a real session costs the session.
- **Claim.** Three kinds of live test, each with a written expected result and no override of any check, found the
  defects below before any run of the claim collections was collected on the faulty code: the machine test (three
  runs on 16-17 October: two failed, each for defects since fixed, then one passed), the smoke before each session,
  and the pre-check itself (§4). The one smoke hold of block 6 was judged wrong and the rule behind it was named for
  repair, under §5's principle.
- **Evidence.** `RUN_STATE.md:93` (first machine test failed: root cause), `:114-115` (second: three desk defects),
  `:122` (third passed); `docs/process_traces/2026-10-17-magistrate-d34bf254/RECORD.md:17-38` (the three desk defects
  and their effect), `docs/process_traces/2026-10-17-magistrate-52d50d1f/RECORD.md:10-18` (the passing test's
  injected faults and their records); `RUN_STATE.md:159-163` (the smoke hold);
  `docs/process_traces/2026-10-17-magistrate-57e84ae6/RECORD.md:7-14` (a smoke false alarm); registration `:425-431`
  (each pack's first session examined for structure before the next arms).
- **Status.** Writable now.
- **Worked example (real, structure).**
  - *Machine test 1 (16 October).* All 4 runs died about 0.5 s after starting: the smoke's preparation rewrote the
    plan file but left the file holding its SHA-256 digest naming the old bytes, so the integrity check refused. The
    loop's own smoke used the same code, so round 1 could never have armed. The same test found that the driver built
    the agent-presence flag without one required clock field, so the flag was rejected and only logged; a run that
    overlapped an agent and lacked its own clock rows could then have counted.
  - *Machine test 2 (17 October).* The shared *admission check* (the test each run's idle baseline must pass before
    its measured request may start) still applied block 5's busy-fraction veto (it refused an idle baseline whose CPU
    was often busy even when its power was low), which block 6's rules had made a flag. Two runs that had succeeded
    were excluded. In round 1 this would have silently dropped every such run and reference run, changing which
    references survive and so the allowed difference the drift screen judges against.
  - *Machine test 3 (17 October, passed).* An injected agent process (alive 15:40:39 to 15:41:25) paused the chain
    for 630 s and the overlapping run was excluded by the agent flag; an injected busy load pushed one run's idle
    wait to the cap (the longest a run may wait for a quiet idle baseline, 1,500 s), and it was skipped after 1,360 s
    and 18 admission attempts, as registered.
  - *The smoke hold (19 October).* ALPHA's round-2 smoke had one run that exited cleanly but whose clock fit (the
    placement of its records on wall time, from its own clock readings) gave no bounded result, so the run had to be
    repeated, which full sessions already handle (the same event appeared in r1-alpha in 2 stages, r1-beta in 1 and
    r2-beta in 3, and each of those sessions finished with every run succeeded and counted). The smoke rule read the
    stage's exit code 1 as a failure and held the pack (stopped arming it until the orchestrator looked). The
    orchestrator, woken by the loop, judged the hold wrong and resumed the pack within its 11-minute wake; the loop
    had already moved to the next pack.
- **Figures.** *Figure 13: what each test catches.* A matrix: rows are defect classes found in October (stale plan
  digest, flag schema, busy-fraction veto, a run skipped at the wait cap read as a missing stage, smoke exit code,
  launch context, media daemon), columns are "unit tests", "machine test", "smoke", "pre-check", "full session"; a
  filled cell means "this test caught it", an open cell "it would have", a dash "it cannot". A legend names the three
  cell marks.

## 9. Blinding, the blind dry run and the independent recompute

- **Forcing problem.** Block 6 estimates the same quantities as block 5. If either block's numbers were read before
  every rule and program was fixed, any later choice could lean toward a preferred result, and a reader could not
  tell. And one analysis program can carry one defect into every number.
- **Claim.** Every block-6 decision that could change a printed number was made while block 5 was still blinded, and
  block 6 stays blinded until its collection has ended, block 5 has been released, the analysis programs have run end
  to end over every real block-6 archive writing structure only (the *blind dry run*) without any program refusing to
  run, and a second program sharing no code with them (the *independent recompute*) agrees with them within a
  registered tolerance: each run's phase energy within 1 mJ, and every printed quantity within half a unit of its
  last printed digit.
- **Evidence.** Registration `:267-282` (terms), `:1122-1166` (what is restricted, what may happen blind, the release
  conditions, the tolerance and its derivation); `RUN_STATE.md:64` (the blind decisions of 14 October).
- **Status.** Mechanism writable now. The observed agreement and the release record wait for the release.
- **Worked example (real, non-claim).** An independent overlap sum over the rehearsals' raw power records reproduced
  154 of 154 phase energies within 7 × 10⁻¹⁵ J. The 1 mJ tolerance therefore sits far above rounding (a 1 ns edge
  rounding at 42 W is 4.2 × 10⁻⁸ J) and far below the defects it must catch: moving one phase edge by 1 ms changes a
  rehearsal prefill by 0.047 J, 47 times the tolerance, and dropping one power record changes it by 3.4 to 5.5 J.
- **Figures.** *Figure 14: the path from raw bytes to a printed number.* Two parallel columns from one box "raw power
  records and stamps (the session's preserved raw files)": left column "harvest → analysis programs → restricted
  results", right column "independent recompute (no shared code) → restricted results"; a diamond "agree within 1 mJ
  per phase and half a printed digit?" joins them, then "release entry (digests of registration, flag catalog,
  harvests)" and "printed number". A dashed box around everything above the release labelled "blinded: structure only
  leaves this box".

## 10. How the software was built and checked

- **Forcing problem.** The collection and analysis code was written mostly by AI coding agents. A builder's own green
  tests do not show that a number is right: in the block-6 build, the defects that changed which data count were
  found by live tests and by reviewers running the code, not by the builder's tests (records below).
- **Claim.** A review procedure in which a second model, not the author, runs the code on production-shaped inputs
  (an *executing review*), and, for code that touches measurement or the counting decision, two further reviewers of
  different model families do the same without seeing each other's report (*blind cold passes*), caught defects that
  each single reviewer missed. The paper reports this as engineering evidence with its catch record, not as a claim
  about AI.
- **Evidence.** `docs/process_traces/2026-10-17-magistrate-d34bf254/RECORD.md:72-75` (the machine test caught three
  number-touching desk defects; each blind cold pass caught one major defect the other missed);
  `docs/process_traces/2026-10-17-magistrate-1a1261a5/RECORD.md:14-17` (reviews of the first machine-test fixes: no
  wrong number or lost run found, both original defects confirmed fixed on the real paths);
  `docs/process_traces/2026-10-21-magistrate-283e9802/RECORD.md:21-24` (both cold passes found the same formula error
  in a written fix instruction drafted by the orchestrator); `docs/orchestration.md:76-137` (when reviews and cold
  gates run, and what each protects); `docs/process_prune_2026-09-29.md` (the six conditions a merge must meet).
- **Status.** Writable now. Open question for Ed: whether this belongs in the paper or in a separate report.
- **Worked example (real).** The second machine-test fix: one blind pass (by the AI model Fable 5.1) found that the
  verdict writer still vetoed busy-only runs; the other (by the AI model Opus 5.5) found a defect in how a run
  skipped by the exhausted wait budget was treated. Both defects change which data count; neither reviewer found
  both.
- **Figures.** *Figure 15: the merge path of one change to code that computes or selects a number.* A left-to-right
  flow: "builder (one model session given the job) writes code and its tests" → "executing review by a non-author
  (runs the code on production-shaped data)" → two parallel boxes "blind cold pass, model A" and "blind cold pass,
  model B" → "each finding fixed, deferred to a named later piece of work, or rejected with a reason" → "whole test
  suite on the merged tree and CI green" → "merge, then record the new pinned commit". Each arrow labelled with what
  is handed over (code, report, findings).

## 11. Results: the replication (waits for the release)

- **Forcing problem.** Block 5's intervals hold variation inside one afternoon only; they say nothing about another
  day, another reboot or another time of day.
- **Claim (to be filled at release).** Block 5 and block 6 printed side by side under block 5's unchanged arithmetic,
  with their difference per printed quantity; a between-session summary per quantity (each counting session's value,
  their mean and standard deviation, no pooled interval); a GAMMA contrast called *replicated* only if every counting
  block-6 session gives the same outcome word and the same sign of the estimate; the flagged-inclusive line (the
  sessions that do not count, added back where computable); the whole-machine line per phase with its boundary
  sentence; the battery-assist line; and the independent recompute's observed agreement.
- **Evidence.** Registration `:1058-1120` (§§10-11: summary, side-by-side reporting, the replication word, what may
  be said, the flagged-inclusive line), `:1007-1056` (§9.5: disclosures and labelled lines), `:1146-1166` (release).
- **Status.** Waits for the release. Available now, as structure: 9 of 9 sessions counting; 3 per pack; all runs
  present and succeeded (§7).
- **Worked example (real; structure and registered arithmetic, no energy).**
  - *What a fourth session buys.* With block 5's one session and block 6's three, every printed quantity has four
    sessions behind it, so a spread across sessions rests on 3 degrees of freedom instead of 2. An interval for a
    mean over sessions, were one computed (none is), would shrink from 4.303 / √3 = 2.48 standard deviations with
    three sessions to 3.182 / √4 = 1.59 with four (4.303 and 3.182 are the two-sided 95% Student-t multipliers for 2
    and 3 degrees of freedom), 36% narrower (registration `:93-95`).
  - *Which ALPHA and BETA sessions supply the floors that judge each GAMMA session.* The rule (registration
    `:483-498`): GAMMA's session of round k is judged against ALPHA's and BETA's counting sessions of round k, or
    else the first counting session of a later round. It depends only on which sessions count, never on an energy.
    Applied to the ledger of §7: r1-gamma pairs with r1-alpha and r1-beta; r2-gamma with r2-beta and, because ALPHA's
    round-2 session never ran, r3-alpha; r3-gamma with r3-alpha and r3-beta; r4-alpha judges no GAMMA session and is
    printed on its own. (Derived here from the registered rule; the analysis programs compute it.)
  - The numbers themselves wait for the release; the registration's synthetic examples (block 5's analysis plan's
    own, re-executed with the repository functions; registration `:899-1006`) show each statistical estimator's
    arithmetic.
- **Figures.** *Figure 16: one printed quantity across sessions.* For each target cell (model × phase), a dot plot: x
  axis "session" (block 5's session, then block 6's three in collection order), y axis the cell's energy (J), each
  dot with its registered interval as a vertical bar and its timing bound as a lighter outer bar; a horizontal line
  at the block-6 mean. *Figure 17: GAMMA's replication.* Per contrast, the estimate and interval for each session,
  coloured by outcome word, with the floor gate drawn as a shaded band around zero. Both figures are drawn blank
  (axes and legends only) until the release.

## 12. Limitations

- **Forcing problem.** A reader who builds energy benchmarks will look first for what the instrument cannot see.
- **Claim.** Each limit below is stated with its size where it has one; none is hidden in a footnote.
- **Status.** Writable now.
- **Worked example (real, non-claim).** The rails-to-machine limit in numbers: on session H the rails were 0.377 to
  0.378 of the whole machine for a 122B model and 0.330 to 0.351 for a 70B model (§2), so no single factor turns a
  rail number into a machine number.
- **Figures.** None.
- **Evidence and the limits, one paragraph each in the paper:**

- One machine, one OS build, one week of sessions (17-21 October): the replication is across days, not months or
  machines (registration `:86-95`).
- The rails are three on-chip sensors; power elsewhere is seen only at the meter, and the rails-to-machine ratio is
  workload-dependent (§2, worked example 2).
- The meter's boundary is DC input at the USB-C port; the adapter's AC-to-DC loss is outside every number
  (registration `:1035`).
- The battery term is read once a second (§6).
- The capture's pulse-derived timing bound is measured on GPU pulses; applying it to sustained mixed inference is an
  assumption that M13 checks only at the edges it timed (`docs/paper/draft-v2-skeleton.md:159`).
- The rules' cut-offs come partly from rehearsals during which an agent process was alive, drawing 0.02 to 0.03
  CPU-s/s; the quiet-machine kit replaced them where it ran (registration `:886-890`).
- The media daemon was held with SIGSTOP by hand; a reboot clears the hold (`RUN_STATE.md:134`).
- The conversion w = 5.432 J per CPU-second is the cost of a performance core at interactive priority; the quiet
  machine's daemons run at background priority on efficiency cores (registration `:784-786`).

## 13. Availability and replication

- **Forcing problem.** A reader who wants to repeat the measurement needs every fixed thing named: which code, which
  models and runtime, which rules, which raw bytes. Without that list nobody else can rebuild the paper's numbers.
- **Claim.** A reader can rebuild the measurement from the repository: the registration, the pinned commit, the flag
  catalog, the model and runtime pins, and the loop's configuration, plus the raw archives on request.
- **Evidence.** Registration `:506-547` (the pinned commit, the measurement checkout, code identity, the estimator
  files byte-identical to block 5's); `docs/paper/draft-v2-skeleton.md:952-1525` (Appendix A, already written for the
  calibration method).
- **Status.** Writable now; release locators added at the release.
- **Worked example.** Storage, which decides whether raw archives can be shared: a session's bytes are mostly sampler
  text that compresses about 70 times (83.0 MB to 1.2 MB at zstd level 3, round trip byte-identical, on a non-claim
  rehearsal file; `RUN_STATE.md:64`); a collected session keeps about 43 GiB before compression (runs root plus
  harvest archive; `RUN_STATE.md:38`).
- **Figures.** None.

---

## Relation to the existing drafts

`docs/paper/draft-v2-skeleton.md` is a methods paper on the calibration and the timing sensitivity of phase-energy
assignment, demonstrated on synthetic and historical data. This outline reuses its §2 and Appendix A.3 for §3 above
and adds the instrument chain, the hazard measurements, the rule set, the automation and the replication.
`docs/paper/draft-v1.md` is the earlier draft; draft-v2 is the one selected on 2026-09-05 (its header, line 1).

## Open decisions for Ed

1. Title (front matter).
2. Whether §10 (how the software was built and checked) belongs in this paper or in a separate report.
3. Whether the paper prints session H's 70B and 122B examples (non-claim) or only the quiet-machine kit's.
4. The venue; its deadline sets whether the replication's release must happen before the first full draft.
5. The derivation of the factor one quarter in F_min / 4 (§5): the registration states the cut-off but records no
   reason for the factor, and the paper must give one.

## Check run before delivery

- Every J and W value in this file was compared against its source: the quiet-machine kit of 16-17 October (M4's
  5.432 J per CPU-second, M10's fit, M14's load steps); the rehearsals of 6 and 9 October (F_min 1.9 J and its
  quarter 0.475 J, the 0.62 s prefill and the 4.96 J agent example, the −0.09 ± 0.09 J per CPU-second regression, the
  11.11, 11.44 and 11.26 ± 0.38 J reference runs and the rule's predicted 104 and 107 J, the 0.47 J half-width, 0.047
  J per ms, 3.4 to 5.5 J per dropped record, 42 W, 7 × 10⁻¹⁵ J); session H of 21 October (every value in §2 worked
  example 2 and in §6); the agent draw (8 to 47 W); the adapter (140 W); or a synthetic registration example (7.20 J
  and its parts). None comes from a block-5 or block-6 session. Block-6 values that appear are structure only:
  verdicts, run counts, stage and session timing, and hazard readings taken before t0.
